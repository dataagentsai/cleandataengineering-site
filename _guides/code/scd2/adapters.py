from delta.tables import DeltaTable
from pyspark.sql import DataFrame, functions as F
from scd2 import apply_scd2, plan_scd2, row_hash


def run_cdc(spark, source: str, target_name: str, key: str, seq: str, tracked: list[str], checkpoint: str):
    target = DeltaTable.forName(spark, target_name)

    def each_batch(batch: DataFrame, _batch_id: int):
        apply_scd2(target, plan_scd2(batch, target.toDF(), key, seq, tracked), key, tracked)

    (spark.readStream.table(source)
        .writeStream.foreachBatch(each_batch)
        .option("checkpointLocation", checkpoint)
        .trigger(availableNow=True)
        .start().awaitTermination())


def change_feed_events(spark, table: str, starting_version: int) -> DataFrame:
    return (spark.readStream.option("readChangeFeed", "true")
            .option("startingVersion", starting_version).table(table)
            .where("_change_type != 'update_preimage'")
            .withColumn("op", F.expr("CASE _change_type WHEN 'delete' THEN 'D' ELSE 'U' END"))
            .withColumnRenamed("_commit_version", "seq"))


def snapshot_to_events(snapshot: DataFrame, current: DataFrame, key: str, tracked: list[str], snap_ts) -> DataFrame:
    s = snapshot.select(key, *tracked).withColumn("new_hash", row_hash(tracked))
    c = current.select(key, F.col("row_hash").alias("cur_hash"))
    op = (F.when(F.col("cur_hash").isNull(), "I")
           .when(F.col("new_hash").isNull(), "D")
           .when(F.col("new_hash") != F.col("cur_hash"), "U"))
    return (s.join(c, key, "full_outer")
              .withColumn("op", op).where(F.col("op").isNotNull())
              .withColumn("seq", F.lit(snap_ts))
              .drop("new_hash", "cur_hash"))


def run_snapshot(spark, snapshot_table: str, target_name: str, key: str, tracked: list[str], snap_ts):
    target = DeltaTable.forName(spark, target_name)
    rows = target.toDF()
    events = snapshot_to_events(spark.read.table(snapshot_table), rows.where("is_current"), key, tracked, snap_ts)
    apply_scd2(target, plan_scd2(events, rows, key, "seq", tracked), key, tracked)
    # Running the same snapshot twice is a no-op: seq is not newer than what is applied.
