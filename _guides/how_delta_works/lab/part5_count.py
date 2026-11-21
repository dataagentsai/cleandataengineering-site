from lab import *
spark = session("count")
f = spark.read.format("delta").load(f"{DATA}/T")
spark.conf.set("spark.sql.adaptive.enabled", "false")
res = {}
Q = {"count_star": f.groupBy().count(), "count_filtered": f.filter("event_date='2026-01-10'").groupBy().count(),
     "min_max": f.agg(F.min("event_id"), F.max("event_id")), "sum_amount": f.agg(F.sum("amount")), "distinct_count": f.agg(F.countDistinct("country"))}
for k, df in Q.items():
    s0, e0 = last_stage(spark), last_exec(spark)
    qe = df._jdf.queryExecution(); t0 = time.perf_counter(); qe.toRdd().count(); secs = time.perf_counter() - t0
    plan = qe.executedPlan().toString().splitlines()
    sm = scan_metrics(spark, e0)
    res[k] = {"first_plan_line": plan[0].strip()[:120], "reads_parquet": any("FileScan parquet" in l for l in plan), "scan_files": sm["files"], "seconds": round(secs, 3),
              "plan": [l.strip(" +-:*()0123456789")[:130] for l in plan if any(x in l for x in ("LocalTableScan", "FileScan", "HashAggregate", "Exchange"))][:6], "full_plan": [l.rstrip()[:170] for l in plan][:12]}
    print(k, res[k]["first_plan_line"], res[k]["reads_parquet"], res[k]["scan_files"])
save("count", res); spark.stop()
