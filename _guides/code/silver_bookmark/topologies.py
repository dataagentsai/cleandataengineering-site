"""Silver written seven ways; gold reading changes three ways. Shown on /learn/silver-to-gold/#bookmark.

Silver row columns:
  _src_seq        the source's change number, carried through (updated when the source sends a change)
  _src_seq_first  the same number, but set on insert and never updated (a common mistake)
  _batch          a silver batch number stamped on every row a write touches (a writer contract)
The third reader uses no column at all: the table's own change log (Delta change data feed, _commit_version).
"""
from delta.tables import DeltaTable
from pyspark.sql import functions as F

SCHEMA = ("dealer_id string, region string, name string, is_current boolean, valid_to string, is_deleted boolean, "
          "_src_seq long, _src_seq_first long, _batch long")


def create(spark, path, rows, batch):
    df = spark.createDataFrame([(d, r, n, True, "open", False, s, s, batch) for d, r, n, s in rows], SCHEMA)
    df.write.format("delta").option("delta.enableChangeDataFeed", "true").save(path)


def insert(spark, path, rows, batch):
    spark.createDataFrame([(d, r, n, True, "open", False, s, s, batch) for d, r, n, s in rows], SCHEMA) \
        .write.format("delta").mode("append").save(path)


def upsert_type1(spark, path, dealer, col, value, src_seq, batch):
    """Overwrite a value in place. _src_seq follows the source; _src_seq_first is left alone; _batch is stamped."""
    DeltaTable.forPath(spark, path).update(f"dealer_id = '{dealer}' AND is_current",
                                           {col: F.lit(value), "_src_seq": F.lit(src_seq), "_batch": F.lit(batch)})


def scd2_change(spark, path, dealer, region, src_seq, batch):
    """Close the current version, insert a new one."""
    t = DeltaTable.forPath(spark, path)
    cur = t.toDF().where(f"dealer_id = '{dealer}' AND is_current").first()
    t.update(f"dealer_id = '{dealer}' AND is_current",
             {"is_current": F.lit(False), "valid_to": F.lit("12 Nov"), "_src_seq": F.lit(src_seq), "_batch": F.lit(batch)})
    insert(spark, path, [(dealer, region, cur.name, src_seq)], batch)


def hard_delete(spark, path, dealer):
    DeltaTable.forPath(spark, path).delete(f"dealer_id = '{dealer}'")


def full_overwrite(spark, path, rows, batch):
    """Replace the whole table with a full copy from the source. A full copy usually brings no change numbers,
    so each row keeps the number it had (or 0 if new); the batch stamp goes on every row."""
    old = {r.dealer_id: r for r in spark.read.format("delta").load(path).where("is_current").collect()}
    out = [(d, reg, n, True, "open", False, old[d]._src_seq if d in old else 0, old[d]._src_seq_first if d in old else 0, batch)
           for d, reg, n in rows]
    spark.createDataFrame(out, SCHEMA).write.format("delta").mode("overwrite").save(path)


# ------------------------------------------------------------------ the gold readers
def read_by_column(spark, path, col, watermark):
    df = spark.read.format("delta").load(path)
    seen = sorted({r.dealer_id for r in df.where(F.col(col) > watermark).select("dealer_id").collect()})
    high = df.agg(F.max(col)).first()[0] or 0
    return seen, max(high, watermark)


def latest_version(spark, path):
    return DeltaTable.forPath(spark, path).history(1).first()["version"]


def read_change_feed(spark, path, watermark):
    latest = latest_version(spark, path)
    if latest <= watermark:
        return [], watermark
    ch = (spark.read.format("delta").option("readChangeFeed", "true").option("startingVersion", watermark + 1)
          .option("endingVersion", latest).load(path).where("_change_type != 'update_preimage'"))
    return sorted({r.dealer_id for r in ch.select("dealer_id").collect()}), latest
