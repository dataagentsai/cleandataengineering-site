"""The keys story on /learn/gold-data-modelling/#keys-zero, run for real. Writes results.json.

    unset SPARK_HOME; python e2e.py
"""
import json
from datetime import date as D
from pathlib import Path

from pyspark.sql import functions as F

import keys as K
from conftest import make_spark

spark = make_spark("gold-keys")
OPEN, INFERRED_FROM = D(9999, 12, 31), D(1900, 1, 1)
DIM_S = "business_key string, name string, region string, valid_from date, valid_to date"
FACT_S = "line_id string, source string, dealer_id string, promised_date date, qty int"
res = {}


def rows(df, cols=None):
    return [{k: (str(v) if isinstance(v, D) else v) for k, v in r.asDict().items() if cols is None or k in cols} for r in df.collect()]


def build_dim(keymap, skmap, versions):
    """versions: business_key, name, region, valid_from, valid_to (+ inferred). Keys come from the two maps."""
    erp = keymap.where("source = 'ERP'")
    v = versions.join(erp.select("business_key", "dealer_dk"), "business_key")
    v = v.join(skmap, ["dealer_dk", "valid_from"])
    return v.withColumn("is_current", F.col("valid_to") == F.lit(OPEN)).select(
        "dealer_sk", "dealer_dk", "business_key", "name", "region", "valid_from", "valid_to", "is_current", "inferred")


def fact_view(fact, dim):
    d = dim.select("dealer_sk", F.col("name").alias("dealer_name"), F.col("region").alias("region_as_was"))
    return fact.join(d, "dealer_sk", "left").orderBy("line_id")


# ---------- step 1: first load (10-11 Nov)
km = K.assign_durable_keys(spark.createDataFrame([], K.KEYMAP_S),
                           spark.createDataFrame([("ERP", "D1"), ("ERP", "D7")], "source string, business_key string"))
ver = spark.createDataFrame([("D1", "Sharma Tyres", "North", D(2024, 1, 1), OPEN), ("D7", "Patel Motor", "North", D(2024, 3, 1), OPEN)], DIM_S).withColumn("inferred", F.lit(False))
sm = K.assign_version_keys(spark.createDataFrame([], K.SKMAP_S), ver.join(km.where("source='ERP'"), "business_key"))
dim1 = build_dim(km, sm, ver)
facts1 = spark.createDataFrame([("L1", "ERP", "D1", D(2026, 11, 10), 10), ("L3", "ERP", "D7", D(2026, 11, 11), 8)], FACT_S)
f1 = K.lookup_via_keymap(facts1, km, dim1, "promised_date").localCheckpoint()
res["step1"] = {"keymap": rows(km.orderBy("dealer_dk")), "dim": rows(dim1.orderBy("dealer_sk")),
                "fact": rows(f1.orderBy("line_id"), ["line_id", "dealer_id", "promised_date", "qty", "dealer_sk", "dealer_dk"])}

# ---------- step 2 (12-13 Nov): name typo fixed (Type 1), D7 moves West (Type 2), unknown dealer D9 arrives on a fact
ver2 = spark.createDataFrame([("D1", "Sharma Tyres", "North", D(2024, 1, 1), OPEN),
                              ("D7", "Patel Motors", "North", D(2024, 3, 1), D(2026, 11, 12)),     # Type 1 fix on every version
                              ("D7", "Patel Motors", "West", D(2026, 11, 12), OPEN)], DIM_S).withColumn("inferred", F.lit(False))
new_facts = spark.createDataFrame([("L4", "ERP", "D7", D(2026, 11, 13), 4), ("L5", "ERP", "D9", D(2026, 11, 13), 6)], FACT_S)
# inferred member: D9 is on a fact but not in the dealer list -> a placeholder row with real keys, filled in later
unknown = new_facts.join(km.withColumnRenamed("business_key", "dealer_id"), ["source", "dealer_id"], "left_anti").select("source", F.col("dealer_id").alias("business_key")).distinct()
km = K.assign_durable_keys(km, unknown)
inferred = spark.createDataFrame([(r.business_key, f"(inferred) {r.business_key}", "unknown", INFERRED_FROM, OPEN) for r in unknown.collect()], DIM_S).withColumn("inferred", F.lit(True))
ver2 = ver2.unionByName(inferred)
sm = K.assign_version_keys(sm, ver2.join(km.where("source='ERP'"), "business_key"))
dim2 = build_dim(km, sm, ver2)
f2_new = K.lookup_via_keymap(new_facts, km, dim2, "promised_date")
fact2 = f1.unionByName(f2_new).localCheckpoint()          # old fact rows are NOT touched: only new rows added
res["step2"] = {"dim": rows(dim2.orderBy("dealer_sk")),
                "fact": rows(fact_view(fact2, dim2), ["line_id", "dealer_id", "promised_date", "dealer_sk", "dealer_dk", "dealer_name", "region_as_was"]),
                "old_fact_rows_unchanged": rows(fact2.where("line_id IN ('L1','L3')").orderBy("line_id")) == rows(f1.orderBy("line_id"))}

# ---------- step 3 (15 Nov): D9's real details arrive -> the inferred row is filled in, same keys
ver3 = ver2.where("business_key != 'D9'").unionByName(
    spark.createDataFrame([("D9", "Kumar Wheels", "South", INFERRED_FROM, OPEN)], DIM_S).withColumn("inferred", F.lit(False)))
dim3 = build_dim(km, sm, ver3)
res["step3"] = {"d9_before": rows(dim2.where("business_key='D9'")), "d9_after": rows(dim3.where("business_key='D9'")),
                "fact": rows(fact_view(fact2, dim3), ["line_id", "dealer_sk", "dealer_name", "region_as_was"]),
                "fact_rows_rewritten": 0}
# the -1 alternative: L5 would have stored -1 and must be rewritten (re-keyed) now
res["step3"]["unknown_member_alternative"] = {"L5_key_on_13_nov": -1, "L5_key_after_rekey": rows(dim3.where("business_key='D9'"))[0]["dealer_sk"], "fact_rows_rewritten": 1}

# ---------- step 4: a new ERP calls D7 'DLR-0007'
km4 = K.assign_durable_keys(km, spark.createDataFrame([("ERP2", "DLR-0007", "D7")], "source string, business_key string, same_as string"))
f4 = spark.createDataFrame([("L7", "ERP2", "DLR-0007", D(2026, 11, 14), 5)], FACT_S)
l7 = K.lookup_via_keymap(f4, km4, dim3, "promised_date").first()
h = K.hash_key(spark.createDataFrame([("D7", D(2026, 11, 12)), ("DLR-0007", D(2026, 11, 12))], "business_key string, valid_from date"),
               ["business_key", "valid_from"]).collect()
res["step4"] = {"keymap": rows(km4.orderBy("dealer_dk", "source")), "L7": {"dealer_sk": l7.dealer_sk, "dealer_dk": l7.dealer_dk},
                "hash_old_code": h[0].hash_sk, "hash_new_code": h[1].hash_sk, "hash_match": h[0].hash_sk == h[1].hash_sk}

# ---------- step 5: the bad way. Rebuild the dimension with row numbers after dealer D5 is added
ver5 = ver3.unionByName(spark.createDataFrame([("D5", "Gupta Tyres", "East", D(2025, 1, 1), OPEN)], DIM_S).withColumn("inferred", F.lit(False)))
renum = K.identity_key(ver5).select("dealer_sk", "business_key", "name", "region", "valid_from")
res["step5"] = {"renumbered": rows(renum.orderBy("dealer_sk")),
                "fact_now_reads": rows(fact2.select("line_id", "dealer_id", "dealer_sk").join(renum.select("dealer_sk", F.col("business_key").alias("now_points_to"), F.col("name").alias("now_name")), "dealer_sk", "left").orderBy("line_id"))}

# ---------- step 6: as-was (version key) vs as-is (durable key -> current row)
cur = dim3.where("is_current").select("dealer_dk", F.col("region").alias("region_as_is"))
both = fact_view(fact2, dim3).join(cur, "dealer_dk", "left").orderBy("line_id")
res["step6"] = rows(both, ["line_id", "dealer_id", "promised_date", "region_as_was", "region_as_is"])

# ---------- bridge: order line L3 (8 tyres, 40,000) sold by two reps
import bridge as BR  # noqa: E402
fact_b = spark.createDataFrame([("L1", "G1", 50000.0), ("L3", "G2", 40000.0)], "line_id string, rep_group string, revenue double")
credits = spark.createDataFrame([("L1", "Asha"), ("L3", "Asha"), ("L3", "Vik")], "line_id string, rep string")
br = spark.createDataFrame([("G1", "Asha", 1.0), ("G2", "Asha", 0.6), ("G2", "Vik", 0.4)], "rep_group string, rep string, weight double")
naive = BR.naive_join(fact_b, credits)
alloc = BR.allocate(fact_b, br, "rep_group", "revenue")
res["bridge"] = {
    "naive_rows": naive.count(), "naive_total": naive.agg(F.sum("revenue")).first()[0], "true_total": fact_b.agg(F.sum("revenue")).first()[0],
    "naive_by_rep": rows(naive.groupBy("rep").agg(F.sum("revenue").alias("revenue")).orderBy("rep")),
    "allocated": rows(alloc.select("line_id", "rep", "weight", "revenue", "revenue_allocated").orderBy("line_id", "rep")),
    "allocated_by_rep": rows(alloc.groupBy("rep").agg(F.sum("revenue_allocated").alias("revenue")).orderBy("rep")),
    "allocated_total": alloc.agg(F.sum("revenue_allocated")).first()[0],
    "lines_touched_by_rep": rows(alloc.groupBy("rep").agg(F.countDistinct("line_id").alias("lines")).orderBy("rep")),
}
# hierarchy bridge: Head of Sales > North manager > Asha ; Head > West manager > Vik
hb = spark.createDataFrame([(a, d, n) for a, d, n in [
    ("Head", "Head", 0), ("Head", "North mgr", 1), ("Head", "West mgr", 1), ("Head", "Asha", 2), ("Head", "Vik", 2),
    ("North mgr", "North mgr", 0), ("North mgr", "Asha", 1), ("West mgr", "West mgr", 0), ("West mgr", "Vik", 1),
    ("Asha", "Asha", 0), ("Vik", "Vik", 0)]], "ancestor string, descendant string, depth int")
by_rep = alloc.groupBy("rep").agg(F.sum("revenue_allocated").alias("revenue"))
res["hierarchy"] = {"bridge": rows(hb.orderBy("ancestor", "depth", "descendant")),
                    "rollup": rows(BR.rollup_hierarchy(by_rep, hb, "rep", "revenue").orderBy(F.desc("revenue_under"), "ancestor"))}

Path(__file__).with_name("results.json").write_text(json.dumps(res, indent=1, default=str))
print(json.dumps(res, indent=1, default=str))
spark.stop()
