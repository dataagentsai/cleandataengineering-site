"""Record the Spark internals scenes for DataTwin Studio from REAL runs.

    env -u SPARK_HOME ~/CostIntelligence1/.venv/bin/python _sim/record_spark.py

Seven scenarios on local Spark (2 cores), each step tagged with its own job group so the event log
can be split per step: tasks and waves, lazy evaluation, narrow vs wide, the query plan, joins,
skew and AQE, caching. For every step it records the code, the result, the plan, and every stage
with its tasks (duration, launch offset, shuffle read and write, spill).
Output: _sim/data/spark.json
"""
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
from pyspark.sql import SparkSession, functions as F  # noqa: E402

OUT = Path(__file__).resolve().parent / "data" / "spark.json"


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse(evdir):
    f = next(Path(evdir).iterdir())
    jobs, stages, tasks, execs = {}, {}, {}, []
    for line in f.read_text().splitlines():
        e = json.loads(line)
        ev = e["Event"]
        if ev == "SparkListenerJobStart":
            jobs[e["Job ID"]] = {"group": e.get("Properties", {}).get("spark.jobGroup.id"), "stages": e["Stage IDs"], "start": e["Submission Time"],
                                 "desc": (e.get("Properties", {}).get("spark.job.description") or "")[:80]}
        elif ev == "SparkListenerJobEnd":
            jobs[e["Job ID"]]["end"] = e["Completion Time"]
        elif ev == "SparkListenerStageCompleted":
            si = e["Stage Info"]
            stages[si["Stage ID"]] = {"name": si["Stage Name"][:70], "tasks": si["Number of Tasks"], "submitted": si.get("Submission Time", 0),
                                      "ms": si.get("Completion Time", 0) - si.get("Submission Time", 0), "parents": si.get("Parent IDs", [])}
        elif ev == "SparkListenerTaskEnd":
            ti, m = e["Task Info"], e.get("Task Metrics") or {}
            sw, sr = m.get("Shuffle Write Metrics") or {}, m.get("Shuffle Read Metrics") or {}
            tasks.setdefault(e["Stage ID"], []).append({
                "i": ti["Index"], "launch": ti["Launch Time"], "ms": ti["Finish Time"] - ti["Launch Time"],
                "sw": sw.get("Shuffle Bytes Written", 0), "sr": sr.get("Remote Bytes Read", 0) + sr.get("Local Bytes Read", 0),
                "spill": m.get("Disk Bytes Spilled", 0), "rows_in": (m.get("Input Metrics") or {}).get("Records Read", 0)})
        elif ev == "SparkListenerExecutorAdded":
            execs.append({"id": e["Executor ID"], "host": e["Executor Info"]["Host"], "cores": e["Executor Info"]["Total Cores"]})
    groups = {}
    for jid, j in sorted(jobs.items()):
        g = j["group"] or "other"
        st = []
        for sid in j["stages"]:
            if sid not in stages:
                continue  # skipped stage (already computed, e.g. reused shuffle)
            ts = sorted(tasks.get(sid, []), key=lambda t: t["i"])
            t0 = min((t["launch"] for t in ts), default=0)
            st.append({"id": sid, **stages[sid], "task_list": [{**t, "offset": t["launch"] - t0} for t in ts],
                       "sw": sum(t["sw"] for t in ts), "sr": sum(t["sr"] for t in ts), "spill": sum(t["spill"] for t in ts)})
        groups.setdefault(g, []).append({"job": jid, "desc": j["desc"], "ms": j.get("end", j["start"]) - j["start"], "stages": st})
    return groups, execs


class Rec:
    def __init__(self, spark):
        self.spark, self.steps, self.logs, self.n, self._lp = spark, [], [], 0, 0

    def log(self, level, msg):
        self.logs.append([now()[11:19], level, msg])

    def plan(self, df, mode="formatted"):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            if mode == "extended":
                df.explain(extended=True)
            else:
                df.explain(mode)
        txt = buf.getvalue().strip()
        return txt if mode == "extended" else txt.split("\n\n(1)")[0].strip()

    def stage_tasks(self, gid):
        st = self.spark.sparkContext.statusTracker()
        out = []
        for jid in sorted(st.getJobIdsForGroup(gid)):
            ji = st.getJobInfo(jid)
            for sid in (ji.stageIds if ji else []):
                si = st.getStageInfo(sid)
                if si:
                    out.append(si.numTasks)
        return out

    def result(self, rows, cols):
        return {"result": {"cols": cols, "rows": [[str(x) for x in r] for r in rows], "count": len(rows)}}

    def step(self, scenario, title, plain, code, group=None, panels=None, focus=None):
        self.n += 1
        self.steps.append({"n": self.n, "scenario": scenario, "title": title, "plain": plain, "code": code, "group": group,
                           "focus": focus or ["inputs", "stages", "engine"], "panels": {"inputs": {"user": "", "file": "", "text": code}, **(panels or {})},
                           "logs": self.logs[self._lp:], "run_log": []})
        self._lp = len(self.logs)


def timed(fn):
    t = time.time()
    r = fn()
    return r, int((time.time() - t) * 1000)


def run():
    evdir, tmp = tempfile.mkdtemp(prefix="dts-sev-"), tempfile.mkdtemp(prefix="dts-sdata-")
    spark = (SparkSession.builder.master("local[2]").appName("DataTwin Studio: Spark internals")
             .config("spark.eventLog.enabled", "true").config("spark.eventLog.dir", evdir)
             .config("spark.ui.enabled", "false").config("spark.sql.session.timeZone", "UTC")
             .config("spark.driver.memory", "1g").getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    sc = spark.sparkContext
    R = Rec(spark)

    def g(gid, desc):
        sc.setJobGroup(gid, desc)
        return gid

    # shared data: orders (2M rows) written as Parquet, a small customers table
    g("setup", "setup")
    spark.conf.set("spark.sql.adaptive.enabled", "false")
    orders_path, cust_path = f"{tmp}/orders", f"{tmp}/customers"
    (spark.range(0, 2_000_000).selectExpr("id AS order_id", "id % 5000 AS customer_id", "cast(rand(7) * 1000 AS double) AS amount",
                                           "date_add(date'2026-01-01', cast(id % 300 AS int)) AS order_date", "CASE WHEN id % 10 = 0 THEN 'refund' ELSE 'sale' END AS kind")
     .repartition(8).write.mode("overwrite").parquet(orders_path))
    spark.range(0, 5000).selectExpr("id AS customer_id", "concat('C-', id) AS name", "CASE WHEN id % 4 = 0 THEN 'AU' ELSE 'IN' END AS country").coalesce(1).write.mode("overwrite").parquet(cust_path)
    orders = spark.read.parquet(orders_path)
    customers = spark.read.parquet(cust_path)
    R.log("INFO", "setup: 2,000,000 orders in 8 Parquet files; 5,000 customers in 1 file")

    # ------------------------------------------------------------- 1. tasks and waves
    code = 'orders = spark.read.parquet("orders/")      # 8 files\norders.count()'
    gid = g("tasks-1", "count with 8 files")
    n, ms = timed(lambda: orders.count())
    R.log("INFO", f"count = {n:,} in {ms} ms")
    tk = R.stage_tasks(gid)
    R.step("tasks", "An action becomes a job, a job becomes tasks", f"count() is an action, so Spark starts a job, split into stages, split into tasks: one task per partition, run by the 2 cores of this machine. Surprise: 8 Parquet files became only {tk[0] if tk else '?'} read tasks. Spark packs small files together (up to spark.sql.files.maxPartitionBytes, 128 MB) and aims for about one split per core, so 8 small files are read by {tk[0] if tk else '?'} tasks. Then a tiny final stage adds up the partial counts. Result: {n:,} rows in {ms} ms.",
           code, gid, {"layers": R.result([[n]], ["count"])})
    code = 'orders.repartition(40).count()'
    gid = g("tasks-2", "count after repartition 40")
    n, ms = timed(lambda: orders.repartition(40).count())
    R.log("INFO", f"repartition(40).count() in {ms} ms")
    R.step("tasks", "More partitions, more tasks, more waves", f"repartition(40) asks for 40 partitions. The job now has a shuffle (a stage that writes 8 pieces, a stage that reads 40), and the second stage has 40 tasks running two at a time: about 20 waves. More partitions than cores only helps when each task has real work; here it added overhead ({ms} ms).",
           code, gid, {"layers": R.result([[n]], ["count"])})

    # ------------------------------------------------------------- 2. lazy evaluation
    gid = g("lazy-1", "transformations only")
    before = len(sc.statusTracker().getJobIdsForGroup("lazy-1"))
    q = orders.filter("kind = 'sale'").withColumn("amount_with_tax", F.col("amount") * 1.18).select("order_id", "customer_id", "amount_with_tax")
    after = len(sc.statusTracker().getJobIdsForGroup("lazy-1"))
    R.log("INFO", f"three transformations defined: {after - before} jobs started")
    R.step("lazy", "Transformations run nothing", "filter, withColumn and select only describe what you want. Spark builds a plan and returns immediately: zero jobs, zero tasks, no data read. This is lazy evaluation.",
           'q = (orders.filter("kind = \'sale\'")\n       .withColumn("amount_with_tax", F.col("amount") * 1.18)\n       .select("order_id", "customer_id", "amount_with_tax"))\n# no action yet',
           gid, {"engine": {"plan": R.plan(q)}}, ["inputs", "engine", "stages"])
    gid = g("lazy-2", "action")
    rows, ms = timed(lambda: q.limit(5).collect())
    R.log("INFO", f"q.limit(5).collect(): {len(sc.statusTracker().getJobIdsForGroup('lazy-2'))} job(s), {ms} ms")
    R.step("lazy", "The action runs the whole plan", f"collect() is an action. Now Spark optimises the plan, reads only the columns it needs, and runs. Because we asked for 5 rows, it stops early: the first task found 5 rows and the job ended ({ms} ms).",
           "q.limit(5).collect()", gid, {"layers": R.result([[r.order_id, r.customer_id, round(r.amount_with_tax, 2)] for r in rows], ["order_id", "customer_id", "amount_with_tax"]), "engine": {"plan": R.plan(q.limit(5))}})

    # ------------------------------------------------------------- 3. narrow vs wide
    gid = g("wide-1", "narrow")
    q = orders.filter("amount > 900").select("order_id", "amount")
    n, ms = timed(lambda: q.count())
    R.log("INFO", f"narrow: filter + select + count, {ms} ms")
    R.step("wide", "Narrow: each task works alone", f"filter and select are narrow: each output partition comes from one input partition, so every task works on its own file with no data moving between them. One stage (plus a tiny final count). {n:,} rows matched in {ms} ms.",
           'orders.filter("amount > 900").select("order_id", "amount").count()', gid, {"layers": R.result([[n]], ["count"]), "engine": {"plan": R.plan(q)}})
    gid = g("wide-2", "wide")
    spark.conf.set("spark.sql.shuffle.partitions", "8")
    q = orders.groupBy("customer_id").agg(F.sum("amount").alias("total"), F.count("*").alias("orders"))
    rows, ms = timed(lambda: q.orderBy(F.desc("total")).limit(5).collect())
    R.log("INFO", f"wide: groupBy customer_id, {ms} ms")
    R.step("wide", "Wide: groupBy needs a shuffle", f"groupBy(customer_id) is wide: all orders of one customer must end up in the same task, wherever they started. Stage 1 reads, pre-aggregates and writes shuffle files by customer_id; stage 2 reads its share of every file and finishes the sum. Look at shuffle write and read in the stages panel, and the Exchange in the plan. {ms} ms.",
           'spark.conf.set("spark.sql.shuffle.partitions", "8")\n(orders.groupBy("customer_id")\n       .agg(F.sum("amount"), F.count("*"))\n       .orderBy(F.desc("total")).limit(5).collect())',
           gid, {"layers": R.result([[r.customer_id, round(r.total, 2), r.orders] for r in rows], ["customer_id", "total", "orders"]), "engine": {"plan": R.plan(q.orderBy(F.desc("total")).limit(5))}})

    # ------------------------------------------------------------- 4. the query plan
    q = (orders.join(customers, "customer_id").filter("country = 'AU' AND order_date >= date'2026-06-01'")
         .groupBy("name").agg(F.sum(F.col("amount") * 2 / 2).alias("total")))
    R.log("INFO", "plan captured with explain(extended=True)")
    R.step("plan", "Four plans for one query", "Spark turns your code into four plans. Parsed: what you wrote. Analysed: names and types resolved. Optimised (Catalyst): rules rewrite it, e.g. 'amount * 2 / 2' is simplified, filters are pushed below the join and down into the Parquet scan, and only the needed columns are read. Physical: how it will actually run (scans, exchanges, join strategy).",
           'q = (orders.join(customers, "customer_id")\n        .filter("country = \'AU\' AND order_date >= date\'2026-06-01\'")\n        .groupBy("name").agg(F.sum(F.col("amount") * 2 / 2)))\nq.explain(extended=True)',
           None, {"engine": {"plan": R.plan(q, "extended")}}, ["inputs", "engine"])
    gid = g("plan-2", "run the plan")
    rows, ms = timed(lambda: q.orderBy(F.desc("total")).limit(3).collect())
    R.log("INFO", f"query ran in {ms} ms")
    R.step("plan", "Pushdown in action", f"Look at the physical plan's FileScan nodes: PushedFilters lists the filters handed to the Parquet reader, and ReadSchema lists only the columns needed. Parquet files keep min and max per row group, so whole chunks are skipped without being read. Ran in {ms} ms.",
           "q.orderBy(F.desc('total')).limit(3).collect()", gid, {"layers": R.result([[r.name, round(r.total, 2)] for r in rows], ["name", "total"]), "engine": {"plan": R.plan(q)}})

    # ------------------------------------------------------------- 5. joins
    spark.conf.set("spark.sql.shuffle.partitions", "8")
    q = orders.join(customers, "customer_id").groupBy("country").agg(F.sum("amount").alias("total"))
    gid = g("join-1", "broadcast")
    rows, ms_b = timed(lambda: q.collect())
    pb = R.plan(q)
    R.log("INFO", f"broadcast hash join: {ms_b} ms")
    R.step("join", "Broadcast hash join: ship the small table", f"customers is small (5,000 rows), so Spark copies it to every task (a broadcast) and builds a hash table there. The 2 million orders never move. Plan: BroadcastHashJoin. {ms_b} ms.",
           'orders.join(customers, "customer_id").groupBy("country").agg(F.sum("amount")).collect()', gid,
           {"layers": R.result([[r.country, round(r.total, 2)] for r in rows], ["country", "total"]), "engine": {"plan": pb}})
    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
    gid = g("join-2", "sort merge")
    q = orders.join(customers, "customer_id").groupBy("country").agg(F.sum("amount").alias("total"))
    rows, ms_s = timed(lambda: q.collect())
    ps = R.plan(q)
    R.log("INFO", f"sort-merge join (broadcast switched off): {ms_s} ms vs {ms_b} ms")
    R.step("join", "Sort-merge join: shuffle both sides", f"With broadcasting switched off, Spark must shuffle both tables by customer_id, sort each partition, then merge them. Compare the stages: the orders side now writes shuffle data. Plan: SortMergeJoin. {ms_s} ms vs {ms_b} ms for the broadcast.",
           'spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")   # never broadcast\norders.join(customers, "customer_id").groupBy("country").agg(F.sum("amount")).collect()', gid,
           {"layers": R.result([[r.country, round(r.total, 2)] for r in rows], ["country", "total"]), "engine": {"plan": ps}})
    spark.conf.unset("spark.sql.autoBroadcastJoinThreshold")

    # ------------------------------------------------------------- 6. skew and AQE
    skew_path = f"{tmp}/skewed"
    g("setup", "setup")
    (spark.range(0, 2_000_000).selectExpr("id AS order_id", "CASE WHEN id % 10 < 4 THEN 0 ELSE id % 20000 END AS customer_id", "rand(3) * 100 AS amount")
     .repartition(8).write.mode("overwrite").parquet(skew_path))
    cust2 = spark.range(0, 20000).selectExpr("id AS customer_id", "concat('C-', id) AS name")
    skewed = spark.read.parquet(skew_path)
    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
    spark.conf.set("spark.sql.shuffle.partitions", "16")
    spark.conf.set("spark.sql.adaptive.enabled", "false")
    spark.conf.set("spark.sql.files.maxPartitionBytes", "1MB")   # more map tasks, so AQE has pieces to split along
    q = skewed.join(cust2, "customer_id").groupBy("name").agg(F.sum("amount").alias("total"))
    gid = g("skew-1", "skew without aqe")
    _, ms1 = timed(lambda: q.write.format("noop").mode("overwrite").save())
    R.log("INFO", f"skewed join without AQE: {ms1} ms")
    R.step("skew", "One hot key: one slow task", f"40% of these orders belong to customer 0 (think 'guest checkout'). In a sort-merge join, every row of customer 0 goes to the same task. In the join stage, one bar is much longer than the rest: everyone waits for it. {ms1} ms.",
           "# 40% of rows have customer_id = 0\nskewed.join(customers, 'customer_id').groupBy('name').agg(F.sum('amount'))\n# AQE off, broadcast off, 16 shuffle partitions, 1 MB file splits", gid, {"engine": {"plan": R.plan(q)}})
    spark.conf.set("spark.sql.adaptive.enabled", "true")
    spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
    spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "1MB")
    spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "2")
    spark.conf.set("spark.sql.adaptive.advisoryPartitionSizeInBytes", "1MB")
    spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "false")
    gid = g("skew-2", "skew with aqe")
    q = skewed.join(cust2, "customer_id").groupBy("name").agg(F.sum("amount").alias("total"))
    _, ms2 = timed(lambda: q.write.format("noop").mode("overwrite").save())
    R.log("INFO", f"skewed join with AQE skew handling: {ms2} ms (was {ms1} ms)")
    tk1, tk2 = R.stage_tasks("skew-1"), R.stage_tasks(gid)
    R.step("skew", "AQE splits the hot partition", f"With adaptive query execution on, Spark looks at the real shuffle sizes after the first stage, sees one partition far bigger than the others, and splits it into several tasks, each joined with a copy of the matching rows from the other side. Join-stage tasks: {max(tk1) if tk1 else '?'} without AQE, {max(tk2) if tk2 else '?'} with it; compare the slowest bar. {ms2} ms vs {ms1} ms. One limit worth knowing: AQE can only split along the map side's outputs, so a skewed partition can never be cut into more pieces than the first stage had tasks. Thresholds were lowered for laptop scale (skewedPartitionThresholdInBytes 1 MB instead of 256 MB).",
           'spark.conf.set("spark.sql.adaptive.enabled", "true")\nspark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")\n# laptop scale: skewedPartitionThresholdInBytes = 1MB, factor = 2',
           gid, {"engine": {"plan": R.plan(q)}})
    spark.conf.unset("spark.sql.autoBroadcastJoinThreshold")
    spark.conf.unset("spark.sql.files.maxPartitionBytes")

    # ------------------------------------------------------------- 7. caching
    spark.conf.set("spark.sql.adaptive.enabled", "true")
    spark.conf.set("spark.sql.shuffle.partitions", "8")
    base = orders.filter("kind = 'sale'").groupBy("order_date").agg(F.sum("amount").alias("total"))
    gid = g("cache-1", "cold")
    _, c1 = timed(lambda: base.count())
    gid2 = g("cache-2", "cold again")
    _, c2 = timed(lambda: base.count())
    R.log("INFO", f"no cache: {c1} ms, then {c2} ms (reads the files again)")
    R.step("cache", "Without cache: every action starts from the files", f"Running the same query twice reads all 8 Parquet files twice and repeats the aggregation. {c1} ms, then {c2} ms.",
           "base = orders.filter(\"kind = 'sale'\").groupBy('order_date').agg(F.sum('amount'))\nbase.count()\nbase.count()   # again", gid2, {"engine": {"plan": R.plan(base)}})
    base.cache()
    gid = g("cache-3", "fill cache")
    _, c3 = timed(lambda: base.count())
    gid = g("cache-4", "from cache")
    _, c4 = timed(lambda: base.count())
    R.log("INFO", f"cache(): first count {c3} ms (fills the cache), second {c4} ms (from memory)")
    R.step("cache", "With cache: the second action reads memory", f"cache() marks the result to be kept in memory. The first action still computes it ({c3} ms) and stores it; the next reads the stored result: {c4} ms. The plan now starts from InMemoryTableScan. Cache only what you reuse, and unpersist it after: memory is shared with everything else.",
           "base.cache()\nbase.count()   # computes and fills the cache\nbase.count()   # reads from memory", "cache-4", {"engine": {"plan": R.plan(base)}})
    base.unpersist()

    groups, execs = parse(evdir)

    def join_stage(gid):  # the stage that read the most shuffle data = the join
        st = [x for j in groups.get(gid, []) for x in j["stages"]]
        x = max(st, key=lambda x: x["sr"])
        ms_ = sorted(t["ms"] for t in x["task_list"])
        return len(ms_), ms_[-1], ms_[len(ms_) // 2]
    (n1, mx1, md1), (n2, mx2, md2) = join_stage("skew-1"), join_stage("skew-2")
    for stp in R.steps:
        if stp["group"] == "skew-1":
            stp["plain"] += f" Recorded: the join stage has {n1} tasks; the slowest took {mx1} ms while the median took {md1} ms."
        if stp["group"] == "skew-2":
            stp["plain"] = stp["plain"].split(" Join-stage tasks:")[0] + (
                f" Recorded: the join stage went from {n1} tasks to {n2}, and its slowest task from {mx1} ms to {mx2} ms (median {md1} → {md2} ms). Whole query: {ms2} ms vs {ms1} ms."
                " One limit worth knowing: AQE can only split along the first stage's outputs, so a skewed partition can never be cut into more pieces than that stage had tasks."
                " Thresholds were lowered for laptop scale (skewedPartitionThresholdInBytes 1 MB instead of 256 MB).")
    env = {"spark": spark.version, "master": "local[2]", "executors": execs, "recorded_at": now()}
    spark.stop()
    shutil.rmtree(evdir, ignore_errors=True)
    shutil.rmtree(tmp, ignore_errors=True)
    return {"env": {**env, "delta": "n/a"}, "jobs": groups, "steps": R.steps}


if __name__ == "__main__":
    t = time.time()
    data = run()
    OUT.write_text(json.dumps(data, indent=1, default=str))
    print(f"{len(data['steps'])} steps -> {OUT} in {time.time() - t:.0f}s")
