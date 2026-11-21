import os, json, re, pickle
from lab import *
from lab import _get
from pyspark.sql.types import DoubleType, LongType
spark = session("spark", cores=2)
T = f"{DATA}/T"
res = {}
def tbl(p): return spark.read.format("delta").load(p)
def plan_text(df, mode="formatted"):
    return df._jdf.queryExecution().explainString(spark._jvm.org.apache.spark.sql.execution.ExplainMode.fromString(mode))
def final_plan(df):
    """plan after the query ran (AQE has finalised it)"""
    return df._jdf.queryExecution().executedPlan().toString()
def interesting(txt, keys):
    return [l.strip(" +-:*()") .strip() for l in txt.splitlines() if any(k in l for k in keys)]
f = tbl(T)
# ---- helper tables
spark.createDataFrame([(c, r) for c, r in zip(["IN","US","UK","DE","FR","AU","AE","SG","JP","BR"], ["APAC","AMER","EMEA","EMEA","EMEA","APAC","EMEA","APAC","APAC","AMER"])], "country string, region string").write.format("delta").mode("overwrite").save(f"{DATA}/dim_country")
spark.range(50000).select(F.col("id").alias("user_id"), F.expr("concat('seg', id % 5)").alias("segment")).write.format("delta").mode("overwrite").save(f"{DATA}/dim_user")
f.select("event_id", "user_id", F.col("amount").alias("amount2")).write.format("delta").mode("overwrite").save(f"{DATA}/T_b")
f.write.format("delta").partitionBy("country").mode("overwrite").save(f"{DATA}/TP")
dc, du, tb, tp = tbl(f"{DATA}/dim_country"), tbl(f"{DATA}/dim_user"), tbl(f"{DATA}/T_b"), tbl(f"{DATA}/TP")
sizes = {n: sum(os.path.getsize(os.path.join(d, x)) for d, _, fs in os.walk(f"{DATA}/{n}") for x in fs if x.endswith(".parquet")) for n in ["T", "dim_country", "dim_user", "T_b", "TP"]}
res["table_bytes"] = sizes; print(sizes)
run(spark, "warm", f.limit(5), reps=1)
J = ["Join", "Exchange", "BroadcastExchange", "Sort ", "HashAggregate", "dynamicpruning", "PartitionFilters", "Scan parquet", "AdaptiveSparkPlan", "isFinalPlan"]
def joinrun(key, df, conf=None):
    old = {}
    for k, v in (conf or {}).items():
        old[k] = spark.conf.get(k, None); spark.conf.set(k, v)
    r = run(spark, key, df); r["plan"] = interesting(final_plan(df), J)[:14]
    for k, v in old.items():
        if v is None: spark.conf.unset(k)
        else: spark.conf.set(k, v)
    res.setdefault("joins", {})[key] = r
    print(key, {x: r[x] for x in ("seconds", "tasks", "stages", "shuffle_write_bytes", "files")}); return r
joinrun("j1_big_small_broadcast", f.join(dc, "country"))
joinrun("j2_big_small_forced_sortmerge", f.join(dc, "country"), {"spark.sql.autoBroadcastJoinThreshold": "-1", "spark.sql.adaptive.enabled": "false"})
joinrun("j3_big_medium_broadcast", f.join(du, "user_id"))
joinrun("j4_big_big_sortmerge", f.join(tb, "event_id"), {"spark.sql.autoBroadcastJoinThreshold": "1048576", "spark.sql.adaptive.enabled": "false"})
joinrun("j4b_big_big_aqe", f.join(tb, "event_id"), {"spark.sql.autoBroadcastJoinThreshold": "1048576", "spark.sql.adaptive.enabled": "true", "spark.sql.adaptive.autoBroadcastJoinThreshold": "10485760"})
joinrun("j5_partitioned_dpp_off", tp.join(dc.filter("region = 'APAC'"), "country"), {"spark.sql.optimizer.dynamicPartitionPruning.enabled": "false", "spark.sql.autoBroadcastJoinThreshold": "-1", "spark.sql.adaptive.enabled": "false"})
joinrun("j5b_partitioned_dpp_on", tp.join(dc.filter("region = 'APAC'"), "country"), {"spark.sql.optimizer.dynamicPartitionPruning.enabled": "true", "spark.sql.autoBroadcastJoinThreshold": "-1", "spark.sql.adaptive.enabled": "false"})
# ---- narrow vs wide and the kinds of exchange
spark.conf.set("spark.sql.adaptive.enabled", "false")
W = {
 "narrow_filter_select": f.filter("amount > 800").select("event_id", "amount"),
 "wide_groupby": f.groupBy("country").agg(F.sum("amount").alias("s")),
 "wide_orderby": f.orderBy("amount"),
 "wide_repartition": f.repartition(8),
 "wide_global_count": f.groupBy().count(),
 "wide_window": f.withColumn("rn", F.row_number().over(__import__("pyspark.sql.window", fromlist=["Window"]).Window.partitionBy("country").orderBy("amount"))),
 "wide_distinct": f.select("country").distinct(),
}
res["shuffles"] = {}
for k, df in W.items():
    r = run(spark, k, df); r["exchanges"] = interesting(final_plan(df), ["Exchange"]); res["shuffles"][k] = r
    print(k, r["stages"], r["tasks"], r["shuffle_write_bytes"], r["exchanges"][:2])
spark.conf.set("spark.sql.adaptive.enabled", "true")
# ---- what travels to the driver
def stage_result_bytes(s0):
    tot = 0
    for s in _get(spark, f"/applications/{app_id(spark)}/stages?status=complete"):
        if s["stageId"] > s0:
            d = _get(spark, f"/applications/{app_id(spark)}/stages/{s['stageId']}/{s['attemptId']}?details=true")
            tot += sum(t.get("taskMetrics", {}).get("resultSize", 0) for t in d.get("tasks", {}).values())
    return tot
def drv(key, fn):
    s0 = last_stage(spark); t = time.perf_counter(); out = fn(); secs = time.perf_counter() - t
    time.sleep(0.6); r = {"seconds": round(secs, 3), "result_bytes": stage_result_bytes(s0), "tasks": stage_totals(spark, s0)["tasks"]}
    res.setdefault("driver", {})[key] = r; print("driver", key, r); return out
drv("count", lambda: f.count())
drv("take5", lambda: f.take(5))
drv("show20", lambda: f.select("event_id", "amount").show(20, False))
drv("collect_2_cols", lambda: f.select("event_id", "amount").collect())
drv("collect_all_cols", lambda: f.collect())
drv("write_noop", lambda: f.write.format("noop").mode("overwrite").save())
drv("agg_then_collect", lambda: f.groupBy("country").agg(F.sum("amount")).collect())
try:
    import pandas; drv("toPandas_2_cols", lambda: f.select("event_id", "amount").toPandas())
except Exception as e: res.setdefault("driver", {})["toPandas_2_cols"] = {"error": str(e)[:80]}
# ---- cache in the select path
q = lambda: tbl(T).filter("amount > 100").groupBy("country").agg(F.sum("amount").alias("s"), F.count("*").alias("n"))
res["cache"] = {"before": run(spark, "uncached", q())}
c = tbl(T).filter("amount > 100").cache(); c.count()
res["cache"]["materialise_seconds"] = None
res["cache"]["after"] = run(spark, "cached", c.groupBy("country").agg(F.sum("amount").alias("s"), F.count("*").alias("n")))
res["cache"]["plan_after"] = interesting(final_plan(c.groupBy("country").agg(F.sum("amount"))), ["InMemory", "Scan"])
si = spark.sparkContext._jsc.sc().getRDDStorageInfo()
res["cache"]["storage"] = [{"memSize": int(x.memSize()), "diskSize": int(x.diskSize()), "partitions": int(x.numPartitions()), "cached": int(x.numCachedPartitions())} for x in si]
print("cache", res["cache"]["before"]["seconds"], res["cache"]["after"]["seconds"], res["cache"]["after"]["files"], res["cache"]["storage"])
c.unpersist()
# ---- Python and the JVM
res["pyjvm"] = {"driver_python_pid": os.getpid(), "jvm_pid": int(spark._jvm.java.lang.ProcessHandle.current().pid()), "jvm_java_version": str(spark._jvm.java.lang.System.getProperty("java.version")),
                "df_python_type": type(f).__name__, "df_jvm_type": str(f._jdf.getClass().getName()), "plan_is_built_in": "JVM"}
udf_x = F.udf(lambda x: x * 1.1, DoubleType())
base = tbl(T).select("event_id", "amount")
B = {"builtin_expr": base.select("event_id", (F.col("amount") * 1.1).alias("a2")),
     "python_udf": base.select("event_id", udf_x("amount").alias("a2"))}
res["pyjvm"]["runs"] = {}
for k, df in B.items():
    r = run(spark, k, df, reps=3); r["plan"] = interesting(final_plan(df), ["BatchEvalPython", "ArrowEvalPython", "WholeStageCodegen", "Project"])[:6]; res["pyjvm"]["runs"][k] = r; print(k, r["seconds"], r["plan"][:3])
pid_udf = F.udf(lambda x: os.getpid(), LongType())
pids = sorted({r[0] for r in tbl(T).select(pid_udf("event_id")).distinct().collect()})
res["pyjvm"]["worker_pids"] = pids; print("worker pids", pids, "driver", os.getpid())
t0 = time.perf_counter(); tbl(T).select("amount").rdd.map(lambda r: r[0] * 1.1).sum(); res["pyjvm"]["rdd_lambda_seconds"] = round(time.perf_counter() - t0, 3)
save("part3_spark", res); spark.stop()
