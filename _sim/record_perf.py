"""Record the Performance stories for DataTwin Studio from REAL runs (laptop scale).

    env -u SPARK_HOME ~/CostIntelligence1/.venv/bin/python _sim/record_perf.py

Each story: Before (the slow job and the clues that give it away) and After (the fix, measured).
Story 0 combines four problems and removes them one fix at a time (a waterfall).
All times are measured on local[2] (2 cores, 1 GB driver); the scale is stated on every story.
The one exception, the weekend bill, is arithmetic and is labelled illustrative.
Output: _sim/data/perf.json
"""
import json
import os
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

os.environ["TZ"] = "UTC"
time.tzset()
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
from delta import configure_spark_with_delta_pip  # noqa: E402
from pyspark.sql import SparkSession, functions as F, types as T  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from record_spark import Rec, now, parse  # noqa: E402
from record_problems import short_err  # noqa: E402

OUT = Path(__file__).resolve().parent / "data" / "perf.json"


def clue(name, value, ok):
    return [name, str(value), bool(ok)]


def secs(ms):
    return f"{ms / 1000:.1f} s" if ms >= 1000 else f"{ms} ms"


def run():
    evdir, wh = tempfile.mkdtemp(prefix="dts-pev-"), tempfile.mkdtemp(prefix="dts-pwh-")
    b = (SparkSession.builder.master("local[2]").appName("DataTwin Studio: Performance stories")
         .config("spark.eventLog.enabled", "true").config("spark.eventLog.dir", evdir)
         .config("spark.ui.enabled", "false").config("spark.sql.session.timeZone", "UTC")
         .config("spark.driver.memory", "1g").config("spark.driver.maxResultSize", "16m")
         .config("spark.sql.warehouse.dir", wh)
         .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
         .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
         .config("spark.databricks.delta.snapshotPartitions", "2")
         .config("spark.databricks.delta.properties.defaults.enableDeletionVectors", "false")
         .config("spark.sql.shuffle.partitions", "8"))
    spark = configure_spark_with_delta_pip(b).getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    sc = spark.sparkContext
    R = Rec(spark)
    sql = spark.sql
    late = []           # (step index, function(groups) -> extra clues / text), resolved after the event log is parsed

    def g(gid):
        sc.setJobGroup(gid, gid)
        return gid

    def setup():
        sc.setJobGroup("setup", "setup")

    def timed(fn):
        a = time.perf_counter()
        r = fn()
        ms = int((time.perf_counter() - a) * 1000)
        setup()                     # anything after the measured action is not counted in its job group
        return r, ms

    def step(story, title, plain, code, gid, clues, dash, panels=None, focus=None, after=None):
        p = {"checks": {"items": clues}, "dashboard": dash, **(panels or {})}
        R.step(story, title, plain, code, gid, p, focus or ["inputs", "dashboard", "checks", "stages"])
        if after:
            late.append((len(R.steps) - 1, after))
        setup()

    def before_tiles(ms, *extra):
        return {"tiles": [["Time on the laptop", secs(ms)], *extra]}

    def after_tiles(b_ms, a_ms, scale):
        return {"tiles": [["Before", secs(b_ms)], ["After", secs(a_ms)], ["Faster", f"{b_ms / max(a_ms, 1):.0f}×" if b_ms >= 2 * a_ms else f"{b_ms / max(a_ms, 1):.1f}×"], ["Scale", scale]]}

    for d in ("t0", "t1", "t2", "t3", "t5", "t6", "t11"):
        sql(f"CREATE DATABASE {d}")
    setup()

    # =================================================================== 0. the "3-hour" job: four problems at once
    cust = spark.range(0, 20000).selectExpr("id AS customer_id", "CASE WHEN id % 5 = 0 THEN 'Gold' ELSE 'Standard' END AS tier")
    cust.write.format("delta").saveAsTable("t0.customers")
    (spark.range(0, 2_000_000).selectExpr("id AS order_id", "CASE WHEN id % 10 < 4 THEN 0 ELSE id % 20000 END AS customer_id",
                                          "date_add(date'2026-07-01', cast(id % 90 AS int)) AS order_date", "cast(id % 997 AS double) AS amount")
     .repartition(3000).write.format("delta").saveAsTable("t0.orders"))
    files0 = spark.sql("DESCRIBE DETAIL t0.orders").first()["numFiles"]

    @F.udf(T.StringType())
    def segment_udf(amount):
        return "big" if amount >= 500 else "small"

    def job(builtin, day=None):
        o = spark.table("t0.orders")
        if day:
            o = o.where(F.col("order_date") == day)
        o = o.withColumn("segment", F.when(F.col("amount") >= 500, "big").otherwise("small") if builtin else segment_udf("amount"))
        return o.join(spark.table("t0.customers"), "customer_id").groupBy("order_date", "segment", "tier").agg(F.sum("amount").alias("revenue"), F.count("*").alias("orders"))

    spark.conf.set("spark.sql.adaptive.enabled", "false")
    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
    spark.conf.set("spark.sql.files.maxPartitionBytes", "1MB")
    wf = []
    _, ms = timed(lambda: (g("case-0"), job(False).write.format("delta").mode("overwrite").saveAsTable("t0.gold"))[1])
    wf.append(["The job as it was", ms])
    gold_ref = sorted(tuple(r) for r in spark.table("t0.gold").collect())
    R.log("WARN", f"nightly gold build: {secs(ms)} (2M orders, {files0} files, Python UDF, skewed join, full rebuild)")
    step("case", "Before: the nightly job everyone is afraid of",
         f"Every night this job rebuilds the gold revenue table from all 2 million orders (90 days). It takes {secs(ms)} on this laptop; the same shape of job on a real lake is the one that takes three hours. Four problems hide in it at once: the orders sit in {files0:,} tiny files, a Python function labels every row, 40% of orders belong to one customer (guest checkout), and it rebuilds all 90 days to add one. Each step from here removes one problem and measures what it was worth.",
         "orders = spark.table('orders')                      # 3,000 tiny files\norders = orders.withColumn('segment', segment_udf('amount'))   # Python UDF\ngold = (orders.join(customers, 'customer_id')        # 40% of rows: customer 0\n          .groupBy('order_date', 'segment', 'tier').agg(sum('amount'), count('*')))\ngold.write.mode('overwrite').saveAsTable('gold')     # all 90 days, every night",
         "case-0", [clue("files", f"{files0:,} files, average {2_000_000 // files0} rows", False), clue("Python UDF in the plan", "BatchEvalPython", False)],
         {"tiles": [["Time on the laptop", secs(ms)], ["Files", f"{files0:,}"], ["Days rebuilt", "90"], ["Fixes applied", "0 of 4"]], "waterfall": list(wf)},
         {"engine": {"plan": R.plan(job(False))}}, after=None)

    _, ms = timed(lambda: (g("case-1"), job(True).write.format("delta").mode("overwrite").saveAsTable("t0.gold"))[1])
    wf.append(["Built-in function instead of the Python UDF", ms])
    same = sorted(tuple(r) for r in spark.table("t0.gold").collect()) == gold_ref
    R.log("INFO", f"fix 1, built-in when(): {secs(ms)}")
    step("case", "Fix 1: replace the Python UDF with a built-in function",
         f"The UDF sends every row from the JVM to a Python process and back, one batch at a time, just to compare a number with 500. The built-in when() does the same inside Spark's own engine. {secs(wf[-2][1])} → {secs(ms)}. Same result: {'identical' if same else 'DIFFERENT'}.",
         "orders.withColumn('segment', when(col('amount') >= 500, 'big').otherwise('small'))",
         "case-1", [clue("Python UDF in the plan", "gone", True), clue("same result", "identical" if same else "different", same)],
         {"tiles": [["Time on the laptop", secs(ms)], ["Was", secs(wf[-2][1])], ["Fixes applied", "1 of 4"], ["Same result", "✓" if same else "✗"]], "waterfall": list(wf)},
         {"engine": {"plan": R.plan(job(True))}})

    g("case-opt")
    sql("OPTIMIZE t0.orders ZORDER BY (order_date)")
    files1 = spark.sql("DESCRIBE DETAIL t0.orders").first()["numFiles"]
    _, ms = timed(lambda: (g("case-2"), job(True).write.format("delta").mode("overwrite").saveAsTable("t0.gold"))[1])
    wf.append(["Compact the tiny files (OPTIMIZE)", ms])
    R.log("INFO", f"fix 2, OPTIMIZE ZORDER BY order_date: {files0:,} → {files1} files; job {secs(ms)}")
    step("case", "Fix 2: compact the tiny files",
         f"OPTIMIZE rewrote {files0:,} tiny files into {files1}, sorted by order_date (ZORDER), so each file now covers a narrow range of days. Fewer files means fewer tasks to schedule and fewer files to open. {secs(wf[-2][1])} → {secs(ms)}. The sort by date also pays off in fix 4.",
         "OPTIMIZE orders ZORDER BY (order_date)", "case-2",
         [clue("files", f"{files0:,} → {files1}", files1 < 50)],
         {"tiles": [["Time on the laptop", secs(ms)], ["Was", secs(wf[-2][1])], ["Fixes applied", "2 of 4"], ["Files", f"{files1}"]], "waterfall": list(wf)})

    for k, v in (("spark.sql.adaptive.enabled", "true"), ("spark.sql.adaptive.skewJoin.enabled", "true"),
                 ("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "1MB"), ("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "2"),
                 ("spark.sql.adaptive.advisoryPartitionSizeInBytes", "1MB"), ("spark.sql.adaptive.coalescePartitions.enabled", "false")):
        spark.conf.set(k, v)
    _, ms = timed(lambda: (g("case-3"), job(True).write.format("delta").mode("overwrite").saveAsTable("t0.gold"))[1])
    wf.append(["Let AQE split the skewed join", ms])
    R.log("INFO", f"fix 3, AQE skew join: {secs(ms)}")
    step("case", "Fix 3: let adaptive execution split the hot customer",
         f"With adaptive query execution (AQE) on, Spark measures the shuffle after the first stage, sees one partition (customer 0) far bigger than the rest and splits it across several tasks. {secs(wf[-2][1])} → {secs(ms)}{': on two cores, splitting adds tasks without adding cores to run them, so here it did not help' if ms >= wf[-2][1] else ', a small gain, because two cores run tasks two at a time anyway'}. On a cluster, where the slowest task sets the finish time, this is the fix that matters most (story 4 measures the critical path). Compare the slowest bars in the stages panel.",
         "spark.conf.set('spark.sql.adaptive.enabled', 'true')\nspark.conf.set('spark.sql.adaptive.skewJoin.enabled', 'true')\n# laptop scale: skewedPartitionThresholdInBytes = 1MB", "case-3",
         [], {"tiles": [["Time on the laptop", secs(ms)], ["Was", secs(wf[-2][1])], ["Fixes applied", "3 of 4"], ["Skew", "split"]], "waterfall": list(wf)})

    day = "2026-09-28"
    spark.range(0, 20000).selectExpr("2000000 + id AS order_id", "CASE WHEN id % 10 < 4 THEN 0 ELSE id % 20000 END AS customer_id",
                                     f"date'{day}' AS order_date", "cast(id % 997 AS double) AS amount").write.format("delta").mode("append").saveAsTable("t0.orders")

    def incr():
        g("case-4")
        job(True, day).write.format("delta").mode("overwrite").option("replaceWhere", f"order_date = '{day}'").saveAsTable("t0.gold")
    _, ms = timed(incr)
    wf.append(["Build only the new day (incremental)", ms])
    total = wf[0][1]
    R.log("INFO", f"fix 4, incremental: only {day}: {secs(ms)}; overall {secs(total)} → {secs(ms)}")
    step("case", "Fix 4: build only the day that changed",
         f"Tonight only {day} has new orders, so the job reads that day (Delta skips the files whose date range cannot match, thanks to the ZORDER in fix 2) and replaces only that day in gold. {secs(wf[-2][1])} → {secs(ms)}. Overall: {secs(total)} → {secs(ms)}, about {total // max(ms, 1)}× faster, with the same answer. On a real lake this is the 3 hours to 5 minutes story. Here it is measured at laptop scale, and the waterfall shows what each fix was worth.",
         f"(job(day='{day}')                                # read one day\n   .write.mode('overwrite')\n   .option('replaceWhere', \"order_date = '{day}'\")    # replace one day\n   .saveAsTable('gold'))", "case-4",
         [clue("days rebuilt per night", "1 of 91", True)],
         {"tiles": [["Before", secs(total)], ["After", secs(ms)], ["Faster", f"{total // max(ms, 1)}×"], ["Scale", "2M orders"]], "waterfall": list(wf),
          "note": "Each bar is the job's measured time after that fix (and all fixes above it)."})
    for k in ("spark.sql.autoBroadcastJoinThreshold", "spark.sql.files.maxPartitionBytes"):
        spark.conf.unset(k)
    spark.conf.set("spark.sql.adaptive.enabled", "true")
    spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")

    # =================================================================== T1. full reload vs incremental
    N1, NEW1 = 15_000_000, 15_000
    (spark.range(0, N1).selectExpr("id AS order_id", "date_add(date'2024-01-01', cast(id % 1000 AS int)) AS order_date", "cast(id % 997 AS double) AS amount")
     .withColumn("month", F.date_format("order_date", "yyyy-MM")).write.format("delta").partitionBy("month").saveAsTable("t1.silver"))
    full = "SELECT order_date, sum(amount) AS revenue, count(*) AS orders FROM t1.silver GROUP BY order_date"
    _, b_ms = timed(lambda: (g("t1-before"), spark.sql(full).write.format("delta").mode("overwrite").saveAsTable("t1.gold"))[1])
    nd = "2026-09-27"
    spark.range(0, NEW1).selectExpr(f"{N1} + id AS order_id", f"date'{nd}' AS order_date", "cast(id % 997 AS double) AS amount", "'2026-09' AS month").write.format("delta").mode("append").saveAsTable("t1.silver")
    R.log("WARN", f"nightly full rebuild of gold: {secs(b_ms)} for {N1:,} rows to add one day")
    step("t1", "Before: the nightly job rebuilds everything",
         f"Gold daily revenue is rebuilt from scratch every night: all 1,000 days of silver, {N1 // 1_000_000} million rows, to add one new day of {NEW1:,} orders. {secs(b_ms)} here. It grows every day, so a job that took minutes in its first month takes hours by year three.",
         full.replace("t1.", "") + "   -- overwrite gold, every night", "t1-before",
         [], before_tiles(b_ms, ["Rows in silver", f"{N1:,}"], ["New rows tonight", f"{NEW1:,}"], ["Days rebuilt", "1,000"]), {"engine": {"plan": R.plan(spark.sql(full))}})
    late.append((len(R.steps) - 1, f"rows:t1-before:{N1}"))
    incr_q = f"SELECT order_date, sum(amount) AS revenue, count(*) AS orders FROM t1.silver WHERE month = '2026-09' AND order_date = '{nd}' GROUP BY order_date"
    _, a_ms = timed(lambda: (g("t1-after"), spark.sql(incr_q).write.format("delta").mode("overwrite").option("replaceWhere", f"order_date = '{nd}'").saveAsTable("t1.gold"))[1])
    R.log("INFO", f"incremental: {secs(a_ms)}")
    step("t1", "After: process only what changed",
         f"The job takes the dates the new batch touched ({nd}), reads only that month's partition, and replaces only that day in gold (replaceWhere). {secs(b_ms)} → {secs(a_ms)}. Its cost now depends on tonight's data, not on all history. On Delta, the change data feed can tell you exactly which rows changed since the last run.",
         incr_q.replace("t1.", "") + f"\n-- write with replaceWhere \"order_date = '{nd}'\"", "t1-after",
         [], after_tiles(b_ms, a_ms, f"{N1 // 1_000_000}M rows"), {"engine": {"plan": R.plan(spark.sql(incr_q))}})
    late.append((len(R.steps) - 1, f"rows:t1-after:{N1 + NEW1}"))

    # =================================================================== T2. reading the whole lake
    jpath = f"{wh}/orders_json"
    src = spark.range(0, 1_000_000).selectExpr("id AS order_id", "date_add(date'2024-01-01', cast(id % 1000 AS int)) AS order_date", "cast(id % 997 AS double) AS amount",
                                               "id % 5000 AS customer_id", "repeat('x', 60) AS notes", "CASE WHEN id % 7 = 0 THEN 'refund' ELSE 'sale' END AS status")
    src.write.mode("overwrite").json(jpath)
    src.withColumn("month", F.date_format("order_date", "yyyy-MM")).write.format("delta").partitionBy("month").saveAsTable("t2_orders")
    wk = ("2026-09-20", "2026-09-26")

    def json_q():
        df = spark.read.json(jpath)                       # infers the schema: one extra pass over everything
        return df.select("*").where(F.col("order_date").between(*wk)).agg(F.sum("amount")).first()[0]
    rb, b_ms = timed(lambda: (g("t2-before"), json_q())[1])
    dq = spark.table("t2_orders").where((F.col("month") == "2026-09") & F.col("order_date").between(*wk)).select("amount")
    ra, a_ms = timed(lambda: (g("t2-after"), dq.agg(F.sum("amount")).first()[0])[1])
    R.log("WARN", f"weekly report on JSON: {secs(b_ms)}")
    step("t2", "Before: a weekly report reads the whole lake",
         f"The report needs one week of revenue. It reads raw JSON (1 million orders, every column, all 1,000 days), lets Spark infer the schema (one more full pass), and only then filters to the week. {secs(b_ms)}. The query plan shows a JSON scan with no partition filter: everything is read, parsed and thrown away.",
         "spark.read.json('lake/orders/')         # every file, every column\n     .select('*')\n     .where(col('order_date').between('2026-09-20', '2026-09-26'))\n     .agg(sum('amount'))", "t2-before",
         [clue("partition filter in the plan", "none", False), clue("columns read", "all 6", False)],
         before_tiles(b_ms, ["Rows scanned", "1,000,000"], ["Format", "JSON"], ["Week revenue", f"₹{rb:,.0f}"]),
         {"engine": {"plan": R.plan(spark.read.json(jpath).select("*").where(F.col("order_date").between(*wk)))}})
    late.append((len(R.steps) - 1, "rows:t2-before:1000000"))
    step("t2", "After: a columnar table, a partition filter, one column",
         f"The same data as a Delta table, partitioned by month. The query names the month (so Spark skips the other 32 partitions), reads only the amount column (Parquet is columnar), and its file statistics skip files outside the week. {secs(b_ms)} → {secs(a_ms)}, same answer: {'✓' if round(ra or 0, 2) == round(rb or 0, 2) else '✗'} (₹{ra:,.0f}).",
         "spark.table('orders')\n     .where((col('month') == '2026-09') & col('order_date').between('2026-09-20', '2026-09-26'))\n     .select('amount').agg(sum('amount'))", "t2-after",
         [clue("partition filter in the plan", "month = 2026-09", True), clue("columns read", "1 of 7", True)],
         after_tiles(b_ms, a_ms, "1M rows"), {"engine": {"plan": R.plan(dq)}})
    late.append((len(R.steps) - 1, "rows:t2-after:1000000"))

    # =================================================================== T3. tiny files
    spark.range(0, 2_000_000).selectExpr("id AS order_id", "concat('S-', id % 50) AS store", "cast(id % 997 AS double) AS amount").repartition(3000) \
        .write.format("delta").saveAsTable("t3.orders")
    q3 = "SELECT store, sum(amount) AS revenue FROM t3.orders GROUP BY store"

    def med(gid, n=3):
        spark.sql(q3).write.format("noop").mode("overwrite").save()
        ts = []
        for i in range(n):
            g(gid if i == n - 1 else "warm")
            _, m = timed(lambda: spark.sql(q3).write.format("noop").mode("overwrite").save())
            ts.append(m)
        setup()
        return sorted(ts)[n // 2]
    d3 = spark.sql("DESCRIBE DETAIL t3.orders").first()
    f_b, size_b = d3["numFiles"], d3["sizeInBytes"]
    b_ms = med("t3-before")
    step("t3", "Before: 3,000 tiny files",
         f"A stream wrote 2 million orders as {f_b:,} files of about {size_b // f_b // 1024} KB each. Listing, opening and reading the footer of each file costs more than reading its data. The store revenue query takes {secs(b_ms)} (median of 3). The CostIntelligence1 small-files rule flags any table whose average file is under 32 MB.",
         q3.replace("t3.", ""), "t3-before",
         [clue("average file size (rule: at least 32 MB)", f"{size_b // f_b // 1024} KB", False), clue("files", f"{f_b:,}", False)],
         before_tiles(b_ms, ["Files", f"{f_b:,}"], ["Average file", f"{size_b // f_b // 1024} KB"], ["Rows", "2,000,000"]))
    g("t3-opt")
    _, opt_ms = timed(lambda: sql("OPTIMIZE t3.orders"))
    d3 = spark.sql("DESCRIBE DETAIL t3.orders").first()
    f_a, size_a = d3["numFiles"], d3["sizeInBytes"]
    a_ms = med("t3-after")
    R.log("INFO", f"OPTIMIZE: {f_b:,} → {f_a} files in {secs(opt_ms)}; query {secs(b_ms)} → {secs(a_ms)}")
    step("t3", "After: compact them (OPTIMIZE)",
         f"OPTIMIZE rewrote {f_b:,} files into {f_a} ({size_a // max(f_a, 1) // 1024 // 1024} MB average) in {secs(opt_ms)}, in one atomic commit. The query: {secs(b_ms)} → {secs(a_ms)}. Prevent it next time: write bigger batches, and use auto-compaction or optimized writes where your platform has them.",
         "OPTIMIZE orders\n" + q3.replace("t3.", ""), "t3-after",
         [clue("files", f"{f_b:,} → {f_a}", True)], after_tiles(b_ms, a_ms, "2M rows"))

    # =================================================================== T4. one task for an hour (skew)
    skew_path = f"{wh}/skewed"
    (spark.range(0, 2_000_000).selectExpr("id AS order_id", "CASE WHEN id % 10 < 4 THEN 0 ELSE id % 20000 END AS customer_id", "cast(id % 997 AS double) AS amount")
     .repartition(8).write.mode("overwrite").parquet(skew_path))
    cust2 = spark.range(0, 20000).selectExpr("id AS customer_id", "concat('C-', id) AS name")
    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
    spark.conf.set("spark.sql.shuffle.partitions", "16")
    spark.conf.set("spark.sql.adaptive.enabled", "false")
    spark.conf.set("spark.sql.files.maxPartitionBytes", "1MB")

    def q4():
        return spark.read.parquet(skew_path).join(cust2, "customer_id").groupBy("name").agg(F.sum("amount").alias("total"))
    _, b_ms = timed(lambda: (g("t4-before"), q4().write.format("noop").mode("overwrite").save())[1])
    step("t4", "Before: one task runs while the others wait",
         f"40% of orders belong to customer 0 (guest checkout). In a sort-merge join every row of a key goes to one task, so one task in the join stage gets 40% of the work. {secs(b_ms)} on this laptop. Look at the stages panel: one long bar.",
         "orders.join(customers, 'customer_id').groupBy('name').agg(sum('amount'))\n# AQE off, broadcast off, 16 shuffle partitions", "t4-before",
         [], before_tiles(b_ms, ["Hot key", "customer 0"], ["Its share", "40%"], ["Rows", "2,000,000"]), {"engine": {"plan": R.plan(q4())}})
    late.append((len(R.steps) - 1, "skewclue:t4-before"))
    late.append((len(R.steps) - 1, "critical:t4-before"))
    for k, v in (("spark.sql.adaptive.enabled", "true"), ("spark.sql.adaptive.skewJoin.enabled", "true"),
                 ("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "1MB"), ("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "2"),
                 ("spark.sql.adaptive.advisoryPartitionSizeInBytes", "1MB"), ("spark.sql.adaptive.coalescePartitions.enabled", "false")):
        spark.conf.set(k, v)
    _, a_ms = timed(lambda: (g("t4-after"), q4().write.format("noop").mode("overwrite").save())[1])
    R.log("INFO", f"AQE skew join: {secs(b_ms)} → {secs(a_ms)}")
    step("t4", "After: AQE splits the hot partition",
         f"Adaptive query execution measures the real shuffle sizes, sees the hot partition and splits it into several tasks. Laptop time: {secs(b_ms)} → {secs(a_ms)}; with only two cores the wall time hides most of the gain. The better measure is the critical path: the sum, over stages, of each stage's slowest task, which is how long the job takes when there is a core for every task.",
         "spark.conf.set('spark.sql.adaptive.enabled', 'true')\nspark.conf.set('spark.sql.adaptive.skewJoin.enabled', 'true')\n# laptop scale: skewedPartitionThresholdInBytes = 1MB, factor 2", "t4-after",
         [], after_tiles(b_ms, a_ms, "2M rows"), {"engine": {"plan": R.plan(q4())}})
    late.append((len(R.steps) - 1, "skewclue:t4-after"))
    late.append((len(R.steps) - 1, "critical:t4-after:t4-before"))
    for k in ("spark.sql.autoBroadcastJoinThreshold", "spark.sql.files.maxPartitionBytes", "spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes",
              "spark.sql.adaptive.skewJoin.skewedPartitionFactor", "spark.sql.adaptive.advisoryPartitionSizeInBytes"):
        spark.conf.unset(k)
    spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
    spark.conf.set("spark.sql.shuffle.partitions", "8")

    # =================================================================== T5. the join that exploded
    spark.range(0, 500_000).selectExpr("id AS order_id", "id % 2000 AS product_id", "cast(id % 997 AS double) AS amount").write.format("delta").saveAsTable("t5.orders")
    spark.range(0, 2000 * 20).selectExpr("cast(id / 20 AS BIGINT) AS product_id", "id % 20 AS version", "id % 20 = 19 AS is_current",
                                         "CASE WHEN cast(id / 20 AS BIGINT) % 2 = 0 THEN 'Shirts' ELSE 'Shoes' END AS category").write.format("delta").saveAsTable("t5.dim_product")
    qb = "SELECT p.category, count(*) AS order_lines, sum(o.amount) AS revenue FROM t5.orders o JOIN t5.dim_product p ON o.product_id = p.product_id GROUP BY p.category"
    rb, b_ms = timed(lambda: (g("t5-before"), spark.sql(qb).collect())[1])
    lines_b = sum(r.order_lines for r in rb)
    step("t5", "Before: a join that multiplies rows",
         f"500,000 orders joined to the product dimension. The dimension keeps history (SCD Type 2): 20 versions of every product. Joining on product_id alone matches every version, so each order becomes 20 rows: {lines_b:,} rows came out of the join, and revenue is 20 times too high. {secs(b_ms)}. In production this is the job that never finishes, or finishes with a number nobody believes.",
         qb.replace("t5.", ""), "t5-before",
         [clue("rows out of the join vs orders in", f"{lines_b:,} vs 500,000 ({lines_b // 500_000}×)", lines_b == 500_000), clue("product_id unique in the dimension", "no: 20 rows each", False)],
         before_tiles(b_ms, ["Rows after join", f"{lines_b:,}"], ["Orders", "500,000"], ["Revenue", "20× too high"]), {"engine": {"plan": R.plan(spark.sql(qb))}})
    qa = qb.replace("ON o.product_id = p.product_id", "ON o.product_id = p.product_id AND p.is_current")
    ra, a_ms = timed(lambda: (g("t5-after"), spark.sql(qa).collect())[1])
    lines_a = sum(r.order_lines for r in ra)
    R.log("INFO", f"join on the current version only: {lines_a:,} rows; {secs(b_ms)} → {secs(a_ms)}")
    step("t5", "After: join to exactly one row per key",
         f"Join to the current version only (is_current), or to the version valid at the order's time. One order, one row: {lines_a:,} rows, correct revenue. {secs(b_ms)} → {secs(a_ms)}. Prevent it: a check in silver that the dimension's key is unique among current rows, and a row-count check before and after every join.",
         qa.replace("t5.", ""), "t5-after",
         [clue("rows out of the join vs orders in", f"{lines_a:,} vs 500,000", lines_a == 500_000), clue("product_id unique among current rows", "yes", True)],
         after_tiles(b_ms, a_ms, "500k orders"), {"engine": {"plan": R.plan(spark.sql(qa))}})

    # =================================================================== T6. the MERGE that rewrote everything
    base6 = spark.range(0, 2_000_000).selectExpr("id AS order_id", "date_add(date'2024-01-01', cast(id % 1000 AS int)) AS order_date", "cast(id % 997 AS double) AS amount") \
        .withColumn("month", F.date_format("order_date", "yyyy-MM"))
    base6.orderBy(F.rand(1)).repartition(16).write.format("delta").saveAsTable("t6.orders")
    base6.write.format("delta").partitionBy("month").saveAsTable("t6.orders_p")
    changes = spark.table("t6.orders").where("order_date >= '2026-09-20' AND order_id % 7 = 0").limit(2000).selectExpr("order_id", "order_date", "amount + 1 AS amount", "month")
    changes.write.format("delta").saveAsTable("t6.changes")

    def merge_metrics(t, cond):
        sql(f"MERGE INTO {t} t USING t6.changes s ON {cond} WHEN MATCHED THEN UPDATE SET amount = s.amount")
        m = spark.sql(f"DESCRIBE HISTORY {t}").orderBy(F.desc("version")).first()["operationMetrics"]
        return int(m.get("numTargetFilesRemoved", 0)), int(m.get("numTargetRowsCopied", 0)), int(m.get("numTargetRowsUpdated", 0))
    n_files_b = spark.sql("DESCRIBE DETAIL t6.orders").first()["numFiles"]
    (fr_b, cp_b, up_b), b_ms = timed(lambda: (g("t6-before"), merge_metrics("t6.orders", "t.order_id = s.order_id"))[1])
    step("t6", "Before: a small MERGE rewrites the whole table",
         f"Every day about 2,000 recent orders change. The MERGE matches them by order_id only. The table is not organised by date, so the changed rows are spread across all {n_files_b} files, and Delta rewrites every file that holds a matched row: {fr_b} of {n_files_b} files rewritten, copying {cp_b:,} unchanged rows to update {up_b:,}. {secs(b_ms)}.",
         "MERGE INTO orders t USING changes s\nON t.order_id = s.order_id\nWHEN MATCHED THEN UPDATE SET amount = s.amount", "t6-before",
         [clue("files rewritten", f"{fr_b} of {n_files_b}", fr_b <= 2), clue("unchanged rows copied", f"{cp_b:,} to update {up_b:,}", cp_b < 100 * max(up_b, 1))],
         before_tiles(b_ms, ["Files rewritten", f"{fr_b} of {n_files_b}"], ["Rows copied", f"{cp_b:,}"], ["Rows changed", f"{up_b:,}"]))
    n_files_a = spark.sql("DESCRIBE DETAIL t6.orders_p").first()["numFiles"]
    (fr_a, cp_a, up_a), a_ms = timed(lambda: (g("t6-after"), merge_metrics("t6.orders_p", "t.order_id = s.order_id AND t.month = '2026-09'"))[1])
    R.log("INFO", f"MERGE with a partition predicate: {fr_a} files rewritten (was {fr_b}); {secs(b_ms)} → {secs(a_ms)}")
    step("t6", "After: organise by date, and say so in the MERGE",
         f"The same table partitioned by month, and the MERGE condition names the month (all changes are recent). Delta now only looks at, and rewrites, files in that partition: {fr_a} of {n_files_a} files, copying {cp_a:,} rows to update {up_a:,}. {secs(b_ms)} → {secs(a_ms)}. Liquid clustering or ZORDER by date does the same for unpartitioned tables, and deletion vectors avoid rewriting files at all.",
         "MERGE INTO orders t USING changes s\nON t.order_id = s.order_id AND t.month = '2026-09'   -- lets Delta skip every other month\nWHEN MATCHED THEN UPDATE SET amount = s.amount", "t6-after",
         [clue("files rewritten", f"{fr_a} of {n_files_a}", fr_a <= 4), clue("unchanged rows copied", f"{cp_a:,} to update {up_a:,}", cp_a < 100 * max(up_a, 1))],
         after_tiles(b_ms, a_ms, "2M rows"))

    # =================================================================== T7. spill
    wide = spark.range(0, 2_500_000).selectExpr("id", "sha2(cast(id AS STRING), 256) AS h", "repeat(sha2(cast(id AS STRING), 256), 2) AS payload")
    spark.conf.set("spark.sql.adaptive.enabled", "false")
    spark.conf.set("spark.sql.shuffle.partitions", "1")
    _, b_ms = timed(lambda: (g("t7-before"), wide.orderBy("h").write.format("noop").mode("overwrite").save())[1])
    step("t7", "Before: one partition, and it does not fit in memory",
         f"Sorting 2.5 million wide rows (about 200 bytes each) with shuffle partitions set to 1, the way a config copied from a tiny test job might leave it. One task must sort everything; its data does not fit in the memory Spark gives it (this laptop's executor has 1 GB), so it writes sorted runs to disk and merges them back: spill. {secs(b_ms)}.",
         "spark.conf.set('spark.sql.shuffle.partitions', 1)     # AQE off\nwide.orderBy('h').write.format('noop').save()", "t7-before",
         [], before_tiles(b_ms, ["Shuffle partitions", "1"], ["Rows", "2,500,000"], ["Row width", "~200 bytes"]))
    late.append((len(R.steps) - 1, "spill:t7-before"))
    spark.conf.set("spark.sql.shuffle.partitions", "32")
    _, a_ms = timed(lambda: (g("t7-after"), wide.orderBy("h").write.format("noop").mode("overwrite").save())[1])
    R.log("INFO", f"32 partitions + AQE: {secs(b_ms)} → {secs(a_ms)}")
    step("t7", "After: enough partitions that each slice fits in memory",
         f"With 32 shuffle partitions each task sorts about 15 MB, which fits in memory: no spill. {secs(b_ms)} → {secs(a_ms)}. This laptop's fast SSD makes spilling cheap, so the time gain here is modest; on cluster disks, with gigabytes per task, spill is often the difference between minutes and hours. A trap we hit while recording: with adaptive execution's partition coalescing on, Spark merged the 32 small partitions back into a few large ones (it aims for 64 MB each by default) and the spill came back. Set the shuffle partitions and AQE's target size together.",
         "spark.conf.set('spark.sql.shuffle.partitions', 32)\nwide.orderBy('h').write.format('noop').save()", "t7-after",
         [], after_tiles(b_ms, a_ms, "2.5M rows"))
    late.append((len(R.steps) - 1, "spill:t7-after"))
    spark.conf.set("spark.sql.shuffle.partitions", "8")

    # =================================================================== T8. the Python UDF tax
    df8 = spark.range(0, 2_000_000).selectExpr("id", "cast(id % 997 AS double) AS amount", "CASE WHEN id % 3 = 0 THEN ' in ' ELSE 'au' END AS country")

    @F.udf(T.DoubleType())
    def with_tax(amount, country):
        return amount * (1.18 if country.strip().upper() == "IN" else 1.10)
    qb8 = df8.withColumn("gross", with_tax("amount", "country")).agg(F.sum("gross"))
    rb, b_ms = timed(lambda: (g("t8-before"), qb8.first()[0])[1])
    step("t8", "Before: a Python function on every row",
         f"A Python UDF adds tax to 2 million rows. Each row is serialised, sent to a Python worker, computed, and sent back. The CPU is busy, but mostly moving data between the JVM and Python. {secs(b_ms)}. The query plan gives it away: BatchEvalPython.",
         "@udf(DoubleType())\ndef with_tax(amount, country):\n    return amount * (1.18 if country.strip().upper() == 'IN' else 1.10)\n\ndf.withColumn('gross', with_tax('amount', 'country')).agg(sum('gross'))", "t8-before",
         [clue("Python UDF in the plan", "BatchEvalPython", False)], before_tiles(b_ms, ["Rows", "2,000,000"], ["Runs in", "Python"], ["Plan", "BatchEvalPython"]),
         {"engine": {"plan": R.plan(qb8)}})
    qa8 = df8.withColumn("gross", F.col("amount") * F.when(F.upper(F.trim("country")) == "IN", 1.18).otherwise(1.10)).agg(F.sum("gross"))
    ra, a_ms = timed(lambda: (g("t8-after"), qa8.first()[0])[1])
    R.log("INFO", f"built-in functions: {secs(b_ms)} → {secs(a_ms)}")
    step("t8", "After: the same logic with built-in functions",
         f"when(), upper() and trim() run inside Spark's engine, with no Python round-trip, and the optimiser can see what they do. {secs(b_ms)} → {secs(a_ms)}, same total ({'✓' if round(rb, 2) == round(ra, 2) else '✗'}). When Python is unavoidable, a vectorised (pandas) UDF moves data in batches with Arrow and is much faster than a row-at-a-time UDF (not measured here: this laptop's environment has no Arrow).",
         "df.withColumn('gross', col('amount') * when(upper(trim('country')) == 'IN', 1.18).otherwise(1.10))", "t8-after",
         [clue("Python UDF in the plan", "gone", True), clue("same total", "identical" if round(rb, 2) == round(ra, 2) else "different", round(rb, 2) == round(ra, 2))],
         after_tiles(b_ms, a_ms, "2M rows"), {"engine": {"plan": R.plan(qa8)}})

    # =================================================================== T9. broadcast or not
    o9 = spark.range(0, 3_000_000).selectExpr("id AS order_id", "id % 5000 AS store_id", "cast(id % 997 AS double) AS amount")
    s9 = spark.range(0, 5000).selectExpr("id AS store_id", "concat('Region-', id % 9) AS region")
    spark.conf.set("spark.sql.adaptive.enabled", "false")
    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
    q9 = o9.join(s9, "store_id").groupBy("region").agg(F.sum("amount"))
    _, b_ms = timed(lambda: (g("t9-before"), q9.write.format("noop").mode("overwrite").save())[1])
    step("t9", "Before: a tiny lookup joined by shuffling both sides",
         f"3 million orders joined to 5,000 stores. With broadcast joins switched off (someone set the threshold to -1 after a driver crash), Spark shuffles and sorts both sides: all 3 million orders cross the network to be matched with a table that would fit in a few hundred kilobytes. {secs(b_ms)}. The plan shows SortMergeJoin with an Exchange on both sides.",
         "spark.conf.set('spark.sql.autoBroadcastJoinThreshold', -1)\norders.join(stores, 'store_id').groupBy('region').agg(sum('amount'))", "t9-before",
         [clue("join strategy", "SortMergeJoin, both sides shuffled", False)], before_tiles(b_ms, ["Orders", "3,000,000"], ["Stores", "5,000"], ["Join", "sort-merge"]),
         {"engine": {"plan": R.plan(q9)}})
    late.append((len(R.steps) - 1, "shuffle:t9-before"))
    q9b = o9.join(F.broadcast(s9), "store_id").groupBy("region").agg(F.sum("amount"))
    _, a_ms = timed(lambda: (g("t9-after"), q9b.write.format("noop").mode("overwrite").save())[1])
    R.log("INFO", f"broadcast the small side: {secs(b_ms)} → {secs(a_ms)}")
    step("t9", "After: broadcast the small side",
         f"Send the 5,000 stores to every task once and join in place: no shuffle of the orders. {secs(b_ms)} → {secs(a_ms)}. Keep the default threshold (or let AQE switch to a broadcast at run time) and use a hint for tables you know are small. Never broadcast the big side: the driver collects the broadcast table first, which is exactly the crash that made someone turn broadcasts off.",
         "orders.join(broadcast(stores), 'store_id').groupBy('region').agg(sum('amount'))", "t9-after",
         [clue("join strategy", "BroadcastHashJoin, orders not shuffled", True)], after_tiles(b_ms, a_ms, "3M rows"), {"engine": {"plan": R.plan(q9b)}})
    late.append((len(R.steps) - 1, "shuffle:t9-after"))
    spark.conf.unset("spark.sql.autoBroadcastJoinThreshold")
    spark.conf.set("spark.sql.adaptive.enabled", "true")

    # =================================================================== T10. collect() killed the driver
    df10 = spark.range(0, 3_000_000).selectExpr("id AS order_id", "id % 5000 AS store_id", "cast(id % 997 AS double) AS amount", "repeat('x', 20) AS note")
    err = ""

    def bad():
        nonlocal err
        try:
            rows = df10.collect()
            return len(rows)
        except Exception as e:  # noqa: BLE001
            m = re.search(r"Total size of serialized results.*?maxResultSize \([^)]*\)", str(e))
            err = m.group(0) if m else short_err(e, ["maxResultSize", "bigger than", "OutOfMemory"])
    _, b_ms = timed(lambda: (g("t10-before"), bad())[1])
    assert err, "collect() was expected to fail under the driver's result limit"
    R.log("ERROR", f"driver: {err}")
    step("t10", "Before: collect() pulls everything into the driver",
         f"To build a report, someone calls collect() on 3 million rows, bringing every row into the driver's memory. Here the driver's result limit (spark.driver.maxResultSize, set to 16 MB on this laptop) stopped it after {secs(b_ms)}: {err}. Without that limit, the driver runs out of memory and the whole application dies, often hours into a job.",
         "rows = orders.collect()          # 3,000,000 rows into one machine\nreport = summarise_in_python(rows)", "t10-before",
         [clue("rows pulled to the driver", "3,000,000", False), clue("job finished", "no: " + err[:60], False)],
         {"tiles": [["Time to failure", secs(b_ms)], ["Rows requested", "3,000,000"], ["Driver limit", "16 MB"], ["Finished", "✗ no"]]})
    q10 = df10.groupBy("store_id").agg(F.sum("amount").alias("revenue"), F.count("*").alias("orders"))
    top, a_ms = timed(lambda: (g("t10-after"), q10.orderBy(F.desc("revenue")).limit(10).collect())[1])
    R.log("INFO", f"aggregated in Spark, 10 rows to the driver: {secs(a_ms)}")
    step("t10", "After: keep the work distributed; bring back only the answer",
         f"Do the summarising in Spark (groupBy, agg), write big results to a table, and bring back only what a person will look at: here the top 10 stores, 10 rows. {secs(a_ms)}. For a quick look at raw data, use limit() or sample(), never collect() or toPandas() on a whole table.",
         "(orders.groupBy('store_id').agg(sum('amount').alias('revenue'), count('*'))\n       .orderBy(desc('revenue')).limit(10).collect())   # 10 rows", "t10-after",
         [clue("rows pulled to the driver", "10", True), clue("job finished", "yes", True)],
         {"tiles": [["Before", "failed"], ["After", secs(a_ms)], ["Rows to driver", "10"], ["Scale", "3M rows"]]},
         {"layers": {"result": {"cols": ["store_id", "revenue", "orders"], "rows": [[str(r.store_id), f"{r.revenue:,.0f}", str(r.orders)] for r in top], "count": len(top)}}})

    # =================================================================== T11. too many partitions
    o11 = spark.range(0, 400_000).selectExpr("id AS order_id", "id % 2000 AS customer_id", "date_add(date'2026-01-01', cast(id % 270 AS int)) AS order_date", "cast(id % 997 AS double) AS amount")
    _, b_ms = timed(lambda: (g("t11-before"), o11.write.format("delta").partitionBy("customer_id").saveAsTable("t11.by_customer"))[1])
    f11b = spark.sql("DESCRIBE DETAIL t11.by_customer").first()["numFiles"]
    q11 = "SELECT sum(amount) FROM {t} WHERE order_date BETWEEN '2026-09-01' AND '2026-09-27'"
    _, qb_ms = timed(lambda: (g("t11-before-q"), spark.sql(q11.format(t="t11.by_customer")).first())[1])
    setup()
    step("t11", "Before: partitioned by customer",
         f"'Queries filter by customer, so partition by customer.' 400,000 orders across 2,000 customers became {f11b:,} files in 2,000 folders of about {400_000 // f11b} rows each. Writing took {secs(b_ms)}, and the monthly report, which filters by date, must open every one of them: {secs(qb_ms)}.",
         "orders.write.partitionBy('customer_id').saveAsTable('orders')   # 2,000 folders\n\n" + q11.format(t="orders"), "t11-before",
         [clue("files", f"{f11b:,}, about {400_000 // f11b} rows each", False)],
         {"tiles": [["Write", secs(b_ms)], ["Monthly report", secs(qb_ms)], ["Files", f"{f11b:,}"], ["Folders", "2,000"]]})

    def good():
        o11.withColumn("month", F.date_format("order_date", "yyyy-MM")).write.format("delta").partitionBy("month").saveAsTable("t11.by_month")
        sql("OPTIMIZE t11.by_month ZORDER BY (customer_id)")
    _, a_ms = timed(lambda: (g("t11-after"), good())[1])
    f11a = spark.sql("DESCRIBE DETAIL t11.by_month").first()["numFiles"]
    _, qa_ms = timed(lambda: (g("t11-after-q"), spark.sql(q11.format(t="t11.by_month") + " AND month = '2026-09'").first())[1])
    _, qc_ms = timed(lambda: (g("t11-after-c"), spark.sql("SELECT sum(amount) FROM t11.by_month WHERE customer_id = 42").first())[1])
    R.log("INFO", f"by month + ZORDER by customer: {f11a} files; write {secs(b_ms)} → {secs(a_ms)}; report {secs(qb_ms)} → {secs(qa_ms)}")
    step("t11", "After: partition by date (coarse), cluster by customer",
         f"Partition by month (9 folders), then OPTIMIZE ZORDER BY customer_id so each file holds a narrow range of customers. {f11a} files. Write plus OPTIMIZE: {secs(a_ms)} (was {secs(b_ms)}). The monthly report: {secs(qb_ms)} → {secs(qa_ms)}. A one-customer query still skips most files using the per-file statistics ({secs(qc_ms)}). Rule of thumb: partition only by a low-cardinality column you filter on, with partitions of about 1 GB or more; cluster by the rest.",
         "orders.write.partitionBy('month').saveAsTable('orders')\nOPTIMIZE orders ZORDER BY (customer_id)", "t11-after",
         [clue("files", f"{f11a}", True)],
         {"tiles": [["Write", f"{secs(b_ms)} → {secs(a_ms)}"], ["Monthly report", f"{secs(qb_ms)} → {secs(qa_ms)}"], ["Files", f"{f11b:,} → {f11a}"], ["One customer", secs(qc_ms)]]})

    # =================================================================== T12. the weekend bill (illustrative arithmetic)
    RATE, DBU_PER_NODE = 0.55, 1.0         # example: $ per DBU for all-purpose compute, DBUs per node-hour; check your own price list
    nodes, weekend_h = 4, 63
    b_dbu = nodes * DBU_PER_NODE * weekend_h
    job_h = 2 * 3                            # the jobs that actually ran: 2 hours a night, 3 nights
    JOBS_RATE = 0.20                         # example: $ per DBU for jobs compute
    a_dbu = nodes * DBU_PER_NODE * (job_h + 3 * 0.25)
    b_cost, a_cost = b_dbu * RATE, a_dbu * JOBS_RATE
    step("t12", "Before: the cluster that ran all weekend (illustrative)",
         f"Illustrative arithmetic, not a recording. An all-purpose cluster with {nodes} nodes was started on Friday at 18:00 to debug a job and never stopped. Its autoscaling minimum was {nodes}, so it never shrank. Monday 09:00 is {weekend_h} hours later: {nodes} nodes × {weekend_h} h × {DBU_PER_NODE} DBU = {b_dbu:.0f} DBU, at an example ${RATE}/DBU = ${b_cost:,.0f}, for a weekend with no new data. Rates here are examples; use your own price list.",
         f"cost = nodes × hours × DBU per node-hour × $ per DBU\n     = {nodes} × {weekend_h} × {DBU_PER_NODE} × {RATE} = ${b_cost:,.0f}", None,
         [clue("auto-termination", "off", False), clue("cluster type for scheduled jobs", "all-purpose (interactive)", False)],
         {"tiles": [["Weekend cost", f"${b_cost:,.0f}"], ["Hours running", str(weekend_h)], ["Useful hours", str(job_h)], ["Kind", "illustrative"]]}, focus=["inputs", "dashboard", "checks"])
    step("t12", "After: job clusters, auto-termination, a budget alert (illustrative)",
         f"Scheduled work runs on job clusters (or serverless) that start for the job and stop after it, billed at the lower jobs rate (example ${JOBS_RATE}/DBU). Interactive clusters get auto-termination after 15 minutes idle. A budget alert fires when spend passes a threshold. Same three nights of work: {nodes} × ({job_h} h + 3 × 15 min) × {DBU_PER_NODE} DBU × ${JOBS_RATE} = ${a_cost:,.0f} instead of ${b_cost:,.0f}. Illustrative: the shape of the saving is typical; your numbers depend on your rates and cluster sizes.",
         f"cost = {nodes} × ({job_h} + 0.75) × {DBU_PER_NODE} × {JOBS_RATE} = ${a_cost:,.0f}", None,
         [clue("auto-termination", "15 minutes", True), clue("cluster type for scheduled jobs", "job cluster / serverless", True), clue("budget alert", "on", True)],
         {"tiles": [["Before", f"${b_cost:,.0f}"], ["After", f"${a_cost:,.0f}"], ["Cheaper", f"{b_cost / a_cost:.0f}×"], ["Kind", "illustrative"]]}, focus=["inputs", "dashboard", "checks"])

    # ------------------------------------------------------------- resolve clues that need the event log
    groups, execs = parse(evdir)

    def stages(gid):
        return [s for j in groups.get(gid, []) for s in j["stages"]]

    def skew_of(gid):
        st = [s for s in stages(gid) if len(s["task_list"]) >= 4]
        if not st:
            return None
        s = max(st, key=lambda s: max(t["ms"] for t in s["task_list"]))
        ms_ = sorted(t["ms"] for t in s["task_list"])
        return ms_[-1], ms_[len(ms_) // 2], len(ms_)

    def critical(gid):
        return sum(max((t["ms"] for t in s["task_list"]), default=0) for s in stages(gid))

    for i, spec in late:
        st = R.steps[i]
        items = st["panels"]["checks"]["items"]
        kind, *args = spec.split(":")
        gid = args[0]
        if kind == "skewclue":
            k = skew_of(gid)
            if k:
                mx, md, n = k
                ratio = mx / max(md, 1)
                items.append(clue("slowest task vs median (rule: under 3×)", f"{mx} ms vs {md} ms ({ratio:.1f}×, {n} tasks)", ratio < 3))
        elif kind == "critical":
            c = critical(gid)
            if len(args) > 1:
                c0 = critical(args[1])
                st["plain"] += f" Recorded critical path: {secs(c0)} → {secs(c)}."
                items.append(clue("critical path (a core for every task)", f"{secs(c0)} → {secs(c)}", c < c0))
            else:
                items.append(clue("critical path (a core for every task)", secs(c), False))
        elif kind == "spill":
            sp = sum(s["spill"] for s in stages(gid))
            items.append(clue("spilled to disk", f"{sp / 1048576:.0f} MB" if sp else "0", sp == 0))
            if "before" in gid:
                st["plain"] += f" Recorded spill: {sp / 1048576:.0f} MB written to disk."
        elif kind == "shuffle":
            sw = sum(s["sw"] for s in stages(gid))
            items.append(clue("bytes shuffled", f"{sw / 1048576:.1f} MB", "after" in gid))
        elif kind == "rows":
            rin = sum(t["rows_in"] for s in stages(gid) for t in s["task_list"])
            total = int(args[1])
            ok = rin < total / 2
            items.append(clue("rows read from storage", f"{rin:,} (the table has {total:,})", ok))
    env = {"spark": spark.version, "delta": "3.2.0", "master": "local[2]", "executors": execs, "recorded_at": now()}
    spark.stop()
    shutil.rmtree(evdir, ignore_errors=True)
    shutil.rmtree(wh, ignore_errors=True)
    return {"env": env, "jobs": groups, "steps": R.steps}


if __name__ == "__main__":
    t = time.time()
    data = run()
    OUT.write_text(json.dumps(data, indent=1, default=str))
    print(f"{len(data['steps'])} steps -> {OUT} in {time.time() - t:.0f}s")
