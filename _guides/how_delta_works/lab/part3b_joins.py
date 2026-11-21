import os, json
from lab import *
from pyspark.sql.window import Window
spark = session("joins", cores=2)
def tbl(p): return spark.read.format("delta").load(p)
f, dc, du, tb, tp = tbl(f"{DATA}/T"), tbl(f"{DATA}/dim_country"), tbl(f"{DATA}/dim_user"), tbl(f"{DATA}/T_b"), tbl(f"{DATA}/TP")
KEYS = ["Join", "Exchange", "BroadcastExchange", "dynamicpruning", "PartitionFilters", "isFinalPlan", "AQEShuffleRead", "Scan parquet", "FileScan"]
def final_plan(df):
    qe = df._jdf.queryExecution(); qe.toRdd().count()       # run this exact query so AQE finalises its plan
    return qe.executedPlan().toString()
def lines(txt, keys=KEYS):
    out = []
    for l in txt.splitlines():
        if any(k in l for k in keys):
            s = l.strip(" +-:*()0123456789").strip()
            out.append(s[:150])
    return out
res = {"joins": {}, "shuffles": {}}
def jr(key, df, conf=None):
    old = {}
    for k, v in (conf or {}).items(): old[k] = spark.conf.get(k, None); spark.conf.set(k, v)
    r = run(spark, key, df); txt = final_plan(df); r["plan"] = lines(txt)
    r["join_kind"] = next((k for k in ("BroadcastHashJoin", "SortMergeJoin", "ShuffledHashJoin", "BroadcastNestedLoopJoin", "CartesianProduct") if k in txt), "none")
    r["has_dynamic_pruning"] = "dynamicpruning" in txt.lower() or "dynamicpruningexpression" in txt.lower()
    for k, v in old.items(): spark.conf.unset(k) if v is None else spark.conf.set(k, v)
    res["joins"][key] = r; print(key, r["join_kind"], r["has_dynamic_pruning"], {x: r[x] for x in ("seconds", "tasks", "shuffle_write_bytes", "files", "rows")})
run(spark, "warm", f.limit(5), reps=1)
jr("j1_big_small_broadcast", f.join(dc, "country"), {"spark.sql.adaptive.enabled": "false"})
jr("j2_big_small_forced_sortmerge", f.join(dc, "country"), {"spark.sql.autoBroadcastJoinThreshold": "-1", "spark.sql.adaptive.enabled": "false"})
jr("j3_big_medium_broadcast", f.join(du, "user_id"), {"spark.sql.adaptive.enabled": "false"})
jr("j4_big_big_sortmerge", f.join(tb, "event_id"), {"spark.sql.autoBroadcastJoinThreshold": "1048576", "spark.sql.adaptive.enabled": "false"})
jr("j4b_big_big_aqe_on", f.join(tb, "event_id"), {"spark.sql.autoBroadcastJoinThreshold": "1048576", "spark.sql.adaptive.enabled": "true", "spark.sql.adaptive.autoBroadcastJoinThreshold": "10485760"})
jr("j5_partitioned_dpp_off", tp.join(dc.filter("region = 'AMER'"), "country"), {"spark.sql.optimizer.dynamicPartitionPruning.enabled": "false", "spark.sql.adaptive.enabled": "false"})
jr("j5b_partitioned_dpp_on", tp.join(dc.filter("region = 'AMER'"), "country"), {"spark.sql.optimizer.dynamicPartitionPruning.enabled": "true", "spark.sql.adaptive.enabled": "false"})
spark.conf.set("spark.sql.adaptive.enabled", "false")
W = {"narrow_filter_select": f.filter("amount > 800").select("event_id", "amount"),
     "wide_groupby": f.groupBy("country").agg(F.sum("amount").alias("s")),
     "wide_orderby": f.orderBy("amount"),
     "wide_repartition": f.repartition(8),
     "wide_global_count": f.groupBy().count(),
     "wide_window": f.withColumn("rn", F.row_number().over(Window.partitionBy("country").orderBy("amount"))),
     "wide_distinct": f.select("country").distinct()}
for k, df in W.items():
    r = run(spark, k, df); txt = final_plan(df)
    r["exchanges"] = [l for l in lines(txt, ["Exchange"])]; r["n_exchanges"] = sum(1 for l in txt.splitlines() if "Exchange" in l and "BroadcastExchange" not in l)
    res["shuffles"][k] = r; print(k, r["n_exchanges"], r["tasks"], r["shuffle_write_bytes"], r["input_bytes"], r["exchanges"][:2])
save("part3b_joins", res); spark.stop()
