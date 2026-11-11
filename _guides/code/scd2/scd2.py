"""One SCD Type 2 writer. Input is always change events: key, seq, op ('I','U','D'), tracked columns.
Target columns: key, tracked..., row_hash, valid_from, valid_to, is_current."""
from delta.tables import DeltaTable
from pyspark.sql import DataFrame, Window, functions as F


def row_hash(cols: list[str]):
    return F.sha2(F.concat_ws("|", *[F.coalesce(F.col(c).cast("string"), F.lit("<null>")) for c in cols]), 256)


def plan_scd2(events: DataFrame, target: DataFrame, key: str, seq: str, tracked: list[str]) -> DataFrame:
    """Pure planning step. target = all rows of the SCD2 table (open and closed).
    Returns staged rows for one MERGE:
    merge_key set  = close that key's open row at close_at
    merge_key null = insert this row as a new version"""
    by_key = Window.partitionBy(key).orderBy(seq)
    cur = target.where("is_current").select(key, F.col("row_hash").alias("cur_hash"))
    # Latest point already applied per key, open or closed (a deleted key has no open row).
    seen = target.groupBy(key).agg(
        F.max(F.greatest("valid_from", F.coalesce("valid_to", "valid_from"))).alias("last_seq"))

    ev = (
        events.dropDuplicates([key, seq])
        .withColumn("row_hash", row_hash(tracked))
        .join(cur, key, "left")
        .join(seen, key, "left")
        # 1. Late or replayed events (not newer than what is applied) are skipped.
        #    This makes re-running a failed batch safe, even for deleted keys.
        .where(F.col("last_seq").isNull() | (F.col(seq) > F.col("last_seq")))
        .withColumn("prev_hash", F.coalesce(F.lag("row_hash").over(by_key), F.col("cur_hash")))
        .withColumn("prev_op", F.lag("op").over(by_key))
        # 2. Drop events that change nothing we track.
        .where((F.col("op") == "D") | (F.col("prev_op") == "D")
               | ~F.col("row_hash").eqNullSafe(F.col("prev_hash")))
        # 3. Each version ends where the next event for the same key starts.
        .withColumn("valid_to", F.lead(seq).over(by_key))
    )

    closes = (
        ev.groupBy(key).agg(F.min(seq).alias("close_at"))
        .join(cur.select(key), key)                       # only keys that have an open row
        .withColumn("merge_key", F.col(key))
    )
    inserts = (
        ev.where(F.col("op") != "D")
        .select(key, *tracked, "row_hash", F.col(seq).alias("valid_from"), "valid_to",
                F.col("valid_to").isNull().alias("is_current"))
        .withColumn("merge_key", F.lit(None).cast(events.schema[key].dataType))
    )
    return closes.unionByName(inserts, allowMissingColumns=True)


def apply_scd2(target: DeltaTable, staged: DataFrame, key: str, tracked: list[str]) -> None:
    """One atomic MERGE: close old versions and insert new ones together."""
    cols = [key, *tracked, "row_hash", "valid_from", "valid_to", "is_current"]
    (
        target.alias("t")
        .merge(staged.alias("s"), f"t.{key} = s.merge_key AND t.is_current")
        .whenMatchedUpdate(set={"valid_to": "s.close_at", "is_current": "false"})
        .whenNotMatchedInsert(condition="s.merge_key IS NULL", values={c: f"s.{c}" for c in cols})
        .execute()
    )
