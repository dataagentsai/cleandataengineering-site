"""Keys for a dimension, shown on /learn/gold-data-modelling/#keys-zero. Tested on Spark 3.5.1.

business key  the source's own code for a dealer (D7, or DLR-0007 in a new system)
durable key   one number per real dealer, given once by the key map, never changes (dealer_dk)
version key   the surrogate key: one number per dimension row, i.e. per version (dealer_sk)
"""
from pyspark.sql import DataFrame, Window, functions as F

KEYMAP_S = "source string, business_key string, dealer_dk int"
SKMAP_S = "dealer_dk int, valid_from date, dealer_sk int"


def assign_durable_keys(keymap: DataFrame, incoming: DataFrame) -> DataFrame:
    """Key map: (source, business key) -> durable key. Known codes keep their number; new ones get the next.
    incoming may carry 'same_as' = an already known business key (a new code for a known dealer)."""
    known = incoming.join(keymap, ["source", "business_key"], "left_anti")
    if "same_as" in incoming.columns:      # a renamed or second-system code that points at a known dealer
        alias = (known.where(F.col("same_as").isNotNull())
                 .join(keymap.select(F.col("business_key").alias("same_as"), "dealer_dk").dropDuplicates(["same_as"]), "same_as")
                 .select("source", "business_key", "dealer_dk"))
        known = known.where(F.col("same_as").isNull())
    else:
        alias = keymap.limit(0)
    start = keymap.agg(F.coalesce(F.max("dealer_dk"), F.lit(0))).first()[0]
    rows = sorted((r.source, r.business_key) for r in known.select("source", "business_key").distinct().collect())
    new = keymap.sparkSession.createDataFrame([(s, b, start + i + 1) for i, (s, b) in enumerate(rows)], KEYMAP_S)
    return keymap.unionByName(alias).unionByName(new)


def assign_version_keys(skmap: DataFrame, versions: DataFrame, first: int = 101) -> DataFrame:
    """Version (surrogate) keys: (durable key, valid_from) -> dealer_sk, assigned once, never renumbered."""
    todo = versions.select("dealer_dk", "valid_from").distinct().join(skmap, ["dealer_dk", "valid_from"], "left_anti")
    start = skmap.agg(F.coalesce(F.max("dealer_sk"), F.lit(first - 1))).first()[0]
    rows = sorted((r.dealer_dk, r.valid_from) for r in todo.collect())
    new = skmap.sparkSession.createDataFrame([(d, v, start + i + 1) for i, (d, v) in enumerate(rows)], SKMAP_S)
    return skmap.unionByName(new)


def hash_key(df: DataFrame, cols: list) -> DataFrame:
    """The other way: a key computed from the business key and version date. No table, same on every rerun,
    but it changes if the business key changes."""
    return df.withColumn("hash_sk", F.xxhash64(*cols))


def identity_key(df: DataFrame, first: int = 101) -> DataFrame:
    """The bad way: number the rows at build time. A rebuild renumbers everything."""
    w = Window.orderBy("business_key", "valid_from")
    return df.withColumn("dealer_sk", F.row_number().over(w) + first - 1)


def lookup_as_of(fact: DataFrame, dim: DataFrame, date_col: str) -> DataFrame:
    """Version key true on the fact's date, plus the durable key. Missing dealer -> -1."""
    d = dim.select(F.col("business_key").alias("_bk"), "dealer_sk", "dealer_dk", "valid_from", "valid_to")
    on = (F.col("dealer_id") == F.col("_bk")) & (F.col(date_col) >= F.col("valid_from")) & (F.col(date_col) < F.col("valid_to"))
    out = fact.join(d, on, "left").drop("_bk", "valid_from", "valid_to")
    return out.fillna({"dealer_sk": -1, "dealer_dk": -1})


def lookup_via_keymap(fact: DataFrame, keymap: DataFrame, dim: DataFrame, date_col: str) -> DataFrame:
    """For facts from any source: business key -> durable key (key map), then the version true on the date."""
    f = fact.join(keymap.withColumnRenamed("business_key", "dealer_id"), ["source", "dealer_id"], "left")
    d = dim.select(F.col("dealer_dk").alias("_dk"), "dealer_sk", "valid_from", "valid_to")
    on = (F.col("dealer_dk") == F.col("_dk")) & (F.col(date_col) >= F.col("valid_from")) & (F.col(date_col) < F.col("valid_to"))
    return f.join(d, on, "left").drop("_dk", "valid_from", "valid_to").fillna({"dealer_sk": -1, "dealer_dk": -1})
