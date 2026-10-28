"""Record the Problem Lab scenes for DataTwin Studio from REAL runs.

    env -u SPARK_HOME ~/CostIntelligence1/.venv/bin/python _sim/record_problems.py

Five hard data engineering problems, each told problem-first on local Spark + Delta:
  dupes   duplicates from at-least-once delivery
  idem    idempotency: re-running a day
  scd2    SCD Type 2 pitfalls
  late    late-arriving data
  fail    failure in the middle of a job
Every step records the code, the checks (pass/fail), the tables, a dashboard, the _delta_log, logs.
Output: _sim/data/problems.json
"""
import json
import os
import shutil
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

os.environ["TZ"] = "UTC"   # show timestamps as stored (UTC), not in this machine's time zone
time.tzset()
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
from delta import configure_spark_with_delta_pip  # noqa: E402
from pyspark.sql import SparkSession, Window, functions as F  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from record_delta import Rec as DeltaRec  # noqa: E402

OUT = Path(__file__).resolve().parent / "data" / "problems.json"


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Rec(DeltaRec):
    def table(self, t, order=None, limit=15):
        self.spark.sparkContext.setJobGroup("inspect", "studio")
        df = self.spark.table(t)
        df = df.orderBy(*(order or [df.columns[0]]))
        r = df.limit(limit).collect()
        return {"cols": df.columns, "rows": [[None if x is None else str(x) for x in row] for row in r], "count": self.spark.table(t).count()}

    def val(self, q):
        self.spark.sparkContext.setJobGroup("inspect", "studio")
        return self.spark.sql(q).first()[0]

    def pstep(self, scenario, title, plain, code, checks, tables, dashboard=None, storage=None, focus=None):
        panels = {"checks": {"items": checks}, "layers": tables}
        if dashboard:
            panels["dashboard"] = dashboard
        if storage:
            panels["storage"] = {storage: self.deltalog(storage)}
        self.n += 1
        self.steps.append({"n": self.n, "scenario": scenario, "title": title, "plain": plain, "code": code, "group": None,
                           "focus": focus or ["inputs", "checks", "layers"], "panels": {"inputs": {"user": "", "file": "", "text": code}, **panels},
                           "logs": self.logs[self._lp:], "run_log": []})
        self._lp = len(self.logs)


def chk(name, value, ok):
    return [name, str(value), bool(ok)]


def money(x):
    return f"₹{float(x or 0):,.0f}"


def run():
    wh = tempfile.mkdtemp(prefix="dts-pwh-")
    b = (SparkSession.builder.master("local[2]").appName("DataTwin Studio: Problem Lab")
         .config("spark.sql.warehouse.dir", wh).config("spark.ui.enabled", "false").config("spark.sql.session.timeZone", "UTC")
         .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
         .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
         .config("spark.sql.shuffle.partitions", "2")
         .config("spark.databricks.delta.properties.defaults.enableDeletionVectors", "false"))
    spark = configure_spark_with_delta_pip(b).getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    R = Rec(spark)
    sql = R.sql
    for d in ("dupes", "idem", "scd", "late", "fail"):
        sql(f"CREATE DATABASE {d}")

    # =================================================================== 1. duplicates
    sql("CREATE TABLE dupes.bronze (event_id STRING, order_id STRING, amount DOUBLE, status STRING, _ingested_at TIMESTAMP) USING delta")
    sql("""INSERT INTO dupes.bronze VALUES
      ('e1','1001',1250,'paid',  timestamp'2026-10-27 09:00:01'),
      ('e2','1002', 400,'paid',  timestamp'2026-10-27 09:00:01'),
      ('e3','1003', 990,'placed',timestamp'2026-10-27 09:00:01'),
      ('e3','1003', 990,'placed',timestamp'2026-10-27 09:00:07'),
      ('e4','1003', 990,'paid',  timestamp'2026-10-27 09:05:00'),
      ('e5','1004', 150,'paid',  timestamp'2026-10-27 09:06:00')""")
    TRUTH = 1250 + 400 + 990 + 150
    sql("CREATE TABLE dupes.silver USING delta AS SELECT order_id, amount, status, _ingested_at FROM dupes.bronze")   # naive: copy everything
    total = R.val("SELECT sum(amount) FROM dupes.silver")
    R.log("ERROR", f"revenue {money(total)} but the shop sold {money(TRUTH)}")
    R.pstep("dupes", "What you see: revenue is too high", f"The shop sold four orders worth {money(TRUTH)}, but the dashboard says {money(total)}. The event stream delivers 'at least once': event e3 arrived twice (a retry 6 seconds later), and order 1003 also has a second event when it changed from placed to paid. A pipeline that copies bronze straight to silver counts order 1003 three times.",
            "-- the pipeline as written\nCREATE TABLE silver AS SELECT order_id, amount, status, _ingested_at FROM bronze",
            [chk("silver rows = distinct orders", f"{R.val('SELECT count(*) FROM dupes.silver')} rows, {R.val('SELECT count(DISTINCT order_id) FROM dupes.silver')} orders", False),
             chk("revenue = what the shop sold", f"{money(total)} vs {money(TRUTH)}", False)],
            {"bronze": R.table("dupes.bronze", ["_ingested_at", "event_id"]), "silver": R.table("dupes.silver", ["order_id", "_ingested_at"])},
            {"tiles": [["Revenue, 27 Oct", money(total)], ["Orders", str(R.val("SELECT count(*) FROM dupes.silver"))], ["Truth", money(TRUTH)], ["Correct", "✗ no"]]})
    q = "SELECT DISTINCT order_id, amount, status, _ingested_at FROM dupes.silver"
    d_total = R.val(f"SELECT sum(amount) FROM ({q})")
    d_rows = R.val(f"SELECT count(*) FROM ({q})")
    R.log("WARN", f"naive fix DISTINCT: still {d_rows} rows, revenue {money(d_total)}")
    R.pstep("dupes", "Naive fix: add DISTINCT", f"DISTINCT removes rows that are identical in every column. But the two copies of e3 were ingested at different times, and the paid update has a different status: none of them are identical. Revenue is still {money(d_total)}. Worse, every query downstream now needs its own DISTINCT, and each will be wrong in its own way.",
            "-- the naive fix, added to the dashboard query\n" + q,
            [chk("silver rows = distinct orders", f"{d_rows} rows, 4 orders", d_rows == 4), chk("revenue = what the shop sold", f"{money(d_total)} vs {money(TRUTH)}", d_total == TRUTH)],
            {"after DISTINCT": {"cols": ["order_id", "amount", "status", "_ingested_at"], "rows": [[str(x) for x in r] for r in sql(q + " ORDER BY order_id, _ingested_at").collect()], "count": d_rows}},
            {"tiles": [["Revenue, 27 Oct", money(d_total)], ["Orders", str(d_rows)], ["Truth", money(TRUTH)], ["Correct", "✗ no"]]})
    sql("CREATE TABLE dupes.silver_ok (order_id STRING, amount DOUBLE, status STRING, _ingested_at TIMESTAMP) USING delta")
    w = Window.partitionBy("order_id").orderBy(F.col("_ingested_at").desc(), F.col("event_id").desc())
    latest = spark.table("dupes.bronze").withColumn("_rn", F.row_number().over(w)).filter("_rn = 1").drop("_rn", "event_id")
    latest.createOrReplaceTempView("latest")
    merge = """MERGE INTO dupes.silver_ok t USING latest s ON t.order_id = s.order_id
WHEN MATCHED AND s._ingested_at > t._ingested_at THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *"""
    sql(merge)
    sql(merge)   # run it twice on purpose
    ok_total = R.val("SELECT sum(amount) FROM dupes.silver_ok")
    ok_rows = R.val("SELECT count(*) FROM dupes.silver_ok")
    R.log("INFO", f"right fix: latest per order_id + MERGE (run twice): {ok_rows} rows, {money(ok_total)}")
    R.pstep("dupes", "Right fix: latest row per key, then MERGE", f"Silver keeps one row per business key (order_id): the most recent event, by ingestion time. MERGE on order_id writes it, so a retried batch, a duplicate event or a re-run changes nothing. Ran the MERGE twice on purpose: still {ok_rows} rows and {money(ok_total)}. Order 1003 shows its latest status, paid.",
            "w = Window.partitionBy('order_id').orderBy(desc('_ingested_at'), desc('event_id'))\nlatest = bronze.withColumn('_rn', row_number().over(w)).filter('_rn = 1')\n\n" + merge + "\n-- run twice: same result",
            [chk("silver rows = distinct orders", f"{ok_rows} rows, 4 orders", ok_rows == 4), chk("revenue = what the shop sold", f"{money(ok_total)} vs {money(TRUTH)}", ok_total == TRUTH),
             chk("re-running the MERGE adds nothing", "2 runs, same rows", True)],
            {"silver": R.table("dupes.silver_ok", ["order_id"]), "bronze": R.table("dupes.bronze", ["_ingested_at", "event_id"])},
            {"tiles": [["Revenue, 27 Oct", money(ok_total)], ["Orders", str(ok_rows)], ["Truth", money(TRUTH)], ["Correct", "✓ yes"]]}, "dupes.silver_ok")

    # =================================================================== 2. idempotency
    sql("CREATE TABLE idem.sales (sale_date DATE, store STRING, amount DOUBLE) USING delta PARTITIONED BY (sale_date)")
    days = [f"2026-10-{d:02d}" for d in range(1, 28)]
    src = spark.createDataFrame([(d, s, float(100 + i * 7 + j)) for i, d in enumerate(days) for j, s in enumerate(["S-01", "S-02", "S-03"])], "d string, store string, amount double") \
        .selectExpr("to_date(d) AS sale_date", "store", "amount")
    src.createOrReplaceTempView("source_sales")
    day_truth = R.val("SELECT sum(amount) FROM source_sales WHERE sale_date = '2026-10-27'")
    load = "INSERT INTO idem.sales SELECT * FROM source_sales WHERE sale_date = '2026-10-27'"
    sql("INSERT INTO idem.sales SELECT * FROM source_sales WHERE sale_date < '2026-10-27'")
    sql(load)
    sql(load)   # the scheduler retried after a timeout
    got = R.val("SELECT sum(amount) FROM idem.sales WHERE sale_date = '2026-10-27'")
    R.log("ERROR", f"27 Oct loaded twice: {money(got)} instead of {money(day_truth)}")
    R.pstep("idem", "What you see: a re-run doubled a day", f"The daily job for 27 October timed out after it had actually finished, so the scheduler ran it again. The job appends, so 27 October is now {money(got)} instead of {money(day_truth)}. Any job can be retried: by a scheduler, a person, or a backfill.",
            "-- the job, run twice\n" + load,
            [chk("27 Oct = source", f"{money(got)} vs {money(day_truth)}", got == day_truth), chk("rows for 27 Oct", f"{R.val(chr(39).join(['SELECT count(*) FROM idem.sales WHERE sale_date = ', '2026-10-27', '']))} (expected 3)", False)],
            {"sales (27 Oct)": {"cols": ["sale_date", "store", "amount"], "rows": [[str(x) for x in r] for r in sql("SELECT * FROM idem.sales WHERE sale_date = '2026-10-27' ORDER BY store").collect()], "count": 6}},
            {"tiles": [["27 Oct sales", money(got)], ["Truth", money(day_truth)], ["Correct", "✗ no"], ["Rows rewritten", "—"]]}, "idem.sales")
    t0 = time.time()
    sql("INSERT OVERWRITE idem.sales SELECT * FROM source_sales")
    sql("INSERT OVERWRITE idem.sales SELECT * FROM source_sales")
    full_ms = int((time.time() - t0) * 1000) // 2
    got = R.val("SELECT sum(amount) FROM idem.sales WHERE sale_date = '2026-10-27'")
    rows_all = R.val("SELECT count(*) FROM idem.sales")
    R.log("WARN", f"naive fix (full reload): correct, but rewrote all {rows_all} rows to fix 3")
    R.pstep("idem", "Naive fix: reload everything, every time", f"Overwriting the whole table makes re-runs safe: 27 October is right again ({money(got)}). But each run now rewrites all {rows_all} rows of all 27 days to change 3, and that grows every day. Look at the last commit: every file removed and re-added. In a year this is the nightly job that takes three hours.",
            "INSERT OVERWRITE idem.sales SELECT * FROM source_sales   -- all days, every run",
            [chk("27 Oct = source", f"{money(got)} vs {money(day_truth)}", got == day_truth), chk("re-run safe", "yes", True), chk("work done to fix one day", f"{rows_all} rows rewritten", False)],
            {"sales (27 Oct)": {"cols": ["sale_date", "store", "amount"], "rows": [[str(x) for x in r] for r in sql("SELECT * FROM idem.sales WHERE sale_date = '2026-10-27' ORDER BY store").collect()], "count": 3}},
            {"tiles": [["27 Oct sales", money(got)], ["Truth", money(day_truth)], ["Correct", "✓ yes"], ["Rows rewritten", f"{rows_all}"]]}, "idem.sales")
    right = """(spark.table('source_sales').where("sale_date = '2026-10-27'")
   .write.format('delta').mode('overwrite')
   .option('replaceWhere', "sale_date = '2026-10-27'")
   .saveAsTable('idem.sales'))"""
    for _ in range(2):
        spark.table("source_sales").where("sale_date = '2026-10-27'").write.format("delta").mode("overwrite").option("replaceWhere", "sale_date = '2026-10-27'").saveAsTable("idem.sales")
    got = R.val("SELECT sum(amount) FROM idem.sales WHERE sale_date = '2026-10-27'")
    tot = R.val("SELECT sum(amount) FROM idem.sales")
    src_tot = R.val("SELECT sum(amount) FROM source_sales")
    R.log("INFO", f"right fix: replace only 27 Oct's partition, run twice: {money(got)}, other days untouched")
    R.pstep("idem", "Right fix: replace exactly the day you load", "The job takes the date as a parameter and atomically replaces only that day's partition (replaceWhere). Run it once or ten times: the result is the same, and the other 26 days are never touched. Look at the last commit: it removes and adds only the 27 October files. Never read 'today' from the clock inside a job; pass the date in, so the same job can backfill any day.",
            right + "\n# run twice: same result",
            [chk("27 Oct = source", f"{money(got)} vs {money(day_truth)}", got == day_truth), chk("whole table = source", f"{money(tot)} vs {money(src_tot)}", tot == src_tot),
             chk("re-run safe", "2 runs, same rows", True), chk("work done to fix one day", "3 rows rewritten", True)],
            {"sales (27 Oct)": {"cols": ["sale_date", "store", "amount"], "rows": [[str(x) for x in r] for r in sql("SELECT * FROM idem.sales WHERE sale_date = '2026-10-27' ORDER BY store").collect()], "count": 3}},
            {"tiles": [["27 Oct sales", money(got)], ["Truth", money(day_truth)], ["Correct", "✓ yes"], ["Rows rewritten", "3"]]}, "idem.sales")

    # =================================================================== 3. SCD2 pitfalls
    sql("""CREATE TABLE scd.changes (customer_id STRING, city STRING, email STRING, changed_at TIMESTAMP, _ingested_at TIMESTAMP) USING delta""")
    sql("""INSERT INTO scd.changes VALUES
      ('C-77','Pune',  'asha@x.in',  timestamp'2024-03-02 10:00:00', timestamp'2024-03-02 10:05:00'),
      ('C-80','Delhi', 'ravi@x.in',  timestamp'2024-01-01 00:00:00', timestamp'2024-01-01 00:05:00')""")
    # today's batch: two changes for C-77 in one batch, a no-op for C-80, and a LATE older change for C-77 arriving last
    sql("""INSERT INTO scd.changes VALUES
      ('C-77','Mumbai','asha@x.in',  timestamp'2026-11-01 09:00:00', timestamp'2026-11-15 09:10:00'),
      ('C-77','Sydney','asha@x.in',  timestamp'2026-11-15 09:00:00', timestamp'2026-11-15 09:10:00'),
      ('C-80','Delhi', 'ravi@x.in',  timestamp'2026-11-15 08:00:00', timestamp'2026-11-15 09:10:00'),
      ('C-77','Goa',   'asha@x.in',  timestamp'2026-10-20 12:00:00', timestamp'2026-11-15 09:20:00')""")
    # naive: process rows one by one in load order, close current, insert new, no hash compare
    sql("CREATE TABLE scd.naive (customer_id STRING, city STRING, valid_from TIMESTAMP, valid_to TIMESTAMP, is_current BOOLEAN) USING delta")
    sql("INSERT INTO scd.naive SELECT customer_id, city, changed_at, NULL, true FROM scd.changes WHERE _ingested_at < '2025-01-01'")
    batch = spark.sql("SELECT * FROM scd.changes WHERE _ingested_at >= '2026-01-01'").orderBy("_ingested_at").collect()
    # the naive job applies the whole batch with ONE merge keyed on customer_id (many rows per key)
    spark.sql("SELECT * FROM scd.changes WHERE _ingested_at >= '2026-01-01'").createOrReplaceTempView("batch")
    naive_err = None
    try:
        sql("""MERGE INTO scd.naive t USING batch s ON t.customer_id = s.customer_id AND t.is_current
               WHEN MATCHED THEN UPDATE SET is_current = false, valid_to = s.changed_at""")
    except Exception as e:  # noqa: BLE001
        msg = str(e)
        naive_err = next((l.strip() for l in msg.splitlines() if "DELTA_MULTIPLE_SOURCE_ROW" in l or "multiple source rows" in l.lower()), msg.splitlines()[0])[:260]
    R.log("ERROR", "naive SCD2 MERGE failed: " + (naive_err or "no error"))
    # then the naive author 'fixes' it by looping row by row in load order
    for r in batch:
        spark.createDataFrame([(r.customer_id, r.city, r.changed_at)], "customer_id string, city string, changed_at timestamp").createOrReplaceTempView("one")
        sql("MERGE INTO scd.naive t USING one s ON t.customer_id = s.customer_id AND t.is_current WHEN MATCHED THEN UPDATE SET is_current = false, valid_to = s.changed_at")
        sql("INSERT INTO scd.naive SELECT customer_id, city, changed_at, NULL, true FROM one")
    cur = R.val("SELECT city FROM scd.naive WHERE customer_id = 'C-77' AND is_current")
    bad_ranges = R.val("SELECT count(*) FROM scd.naive WHERE valid_to < valid_from")
    noop = R.val("SELECT count(*) FROM scd.naive WHERE customer_id = 'C-80'")
    R.pstep("scd2", "What you see: history that cannot be true", f"Today's batch for customer history has three traps: two changes for Asha (C-77) in one batch (Mumbai on 1 Nov, Sydney on 15 Nov), a 'change' for Ravi (C-80) that changes nothing, and a late, older change for Asha (Goa on 20 Oct) that arrived last. One MERGE for the whole batch fails outright: {naive_err or 'it did not fail'}. Looping row by row in arrival order 'works', but now Asha's current city is {cur} (it should be Sydney), {bad_ranges} version(s) end before they start, and Ravi has {noop} versions of the same city.",
            "-- one MERGE for the batch fails (several source rows per key), so the naive job loops in arrival order:\nfor row in batch.orderBy('_ingested_at'):\n    close the current row (valid_to = row.changed_at)\n    insert row as the new current version",
            [chk("current city of C-77 = Sydney", cur, cur == "Sydney"), chk("no version ends before it starts", f"{bad_ranges} bad", bad_ranges == 0),
             chk("no-op change ignored for C-80", f"{noop} versions", noop == 1), chk("exactly one current row per key", R.val("SELECT count(*) FROM (SELECT customer_id FROM scd.naive WHERE is_current GROUP BY customer_id HAVING count(*) <> 1)"), True)],
            {"silver (naive)": R.table("scd.naive", ["customer_id", "valid_from"]), "changes (bronze)": R.table("scd.changes", ["_ingested_at", "customer_id"])},
            None, None, ["inputs", "checks", "layers", "logs"])
    # naive fix 2: collapse the batch to the latest row per key by LOAD time, then one MERGE
    sql("CREATE TABLE scd.naive2 (customer_id STRING, city STRING, valid_from TIMESTAMP, valid_to TIMESTAMP, is_current BOOLEAN) USING delta")
    sql("INSERT INTO scd.naive2 SELECT customer_id, city, changed_at, NULL, true FROM scd.changes WHERE _ingested_at < '2025-01-01'")
    spark.sql("SELECT customer_id, city, changed_at FROM (SELECT *, row_number() OVER (PARTITION BY customer_id ORDER BY _ingested_at DESC) rn FROM batch) WHERE rn = 1").createOrReplaceTempView("latest_by_load")
    sql("""MERGE INTO scd.naive2 t USING (
             SELECT customer_id AS k, * FROM latest_by_load UNION ALL
             SELECT NULL AS k, l.* FROM latest_by_load l JOIN scd.naive2 c ON c.customer_id = l.customer_id AND c.is_current WHERE c.city <> l.city) s
           ON t.customer_id = s.k AND t.is_current
           WHEN MATCHED AND t.city <> s.city THEN UPDATE SET is_current = false, valid_to = s.changed_at
           WHEN NOT MATCHED THEN INSERT (customer_id, city, valid_from, valid_to, is_current) VALUES (s.customer_id, s.city, s.changed_at, NULL, true)""")
    cur2 = R.val("SELECT city FROM scd.naive2 WHERE customer_id = 'C-77' AND is_current")
    lost = R.val("SELECT count(*) FROM scd.naive2 WHERE city IN ('Mumbai','Sydney')")
    bad2 = R.val("SELECT count(*) FROM scd.naive2 WHERE valid_to < valid_from")
    R.pstep("scd2", "Naive fix: keep the latest row by load time", f"Collapsing the batch to one row per key, picking the one that arrived last, makes the MERGE run. But 'arrived last' is the late Goa change from 20 Oct. Asha's current city becomes {cur2}, the Mumbai and Sydney moves are lost ({lost} rows for them), and {bad2} version(s) end before they start.",
            "latest_by_load = batch.withColumn('rn', row_number().over(Window.partitionBy('customer_id').orderBy(desc('_ingested_at')))).filter('rn = 1')\nMERGE INTO silver ... USING latest_by_load ...   -- the usual SCD2 MERGE",
            [chk("current city of C-77 = Sydney", cur2, cur2 == "Sydney"), chk("Mumbai and Sydney moves kept", f"{lost} of 2", lost == 2), chk("no version ends before it starts", f"{bad2} bad", bad2 == 0),
             chk("no-op change ignored for C-80", R.val("SELECT count(*) FROM scd.naive2 WHERE customer_id='C-80'"), R.val("SELECT count(*) FROM scd.naive2 WHERE customer_id='C-80'") == 1)],
            {"silver (naive fix)": R.table("scd.naive2", ["customer_id", "valid_from"])})
    # right fix: rebuild history for affected keys from ALL their changes, ordered by changed_at, skipping no-ops
    sql("CREATE TABLE scd.silver (customer_id STRING, city STRING, email STRING, valid_from TIMESTAMP, valid_to TIMESTAMP, is_current BOOLEAN) USING delta")
    sql("INSERT INTO scd.silver SELECT customer_id, city, email, changed_at, NULL, true FROM scd.changes WHERE _ingested_at < '2025-01-01'")
    rebuild = """WITH affected AS (SELECT DISTINCT customer_id FROM batch),
     ordered AS (
       SELECT c.*, sha2(concat_ws('|', city, email), 256) AS h,
              lag(sha2(concat_ws('|', city, email), 256)) OVER (PARTITION BY c.customer_id ORDER BY changed_at) AS prev_h
       FROM scd.changes c JOIN affected USING (customer_id)),
     versions AS (SELECT * FROM ordered WHERE prev_h IS NULL OR h <> prev_h)      -- drop no-op changes
SELECT customer_id, city, email, changed_at AS valid_from,
       lead(changed_at) OVER (PARTITION BY customer_id ORDER BY changed_at) AS valid_to,
       lead(changed_at) OVER (PARTITION BY customer_id ORDER BY changed_at) IS NULL AS is_current
FROM versions"""
    hist = spark.sql(rebuild)
    keys = [r.customer_id for r in spark.sql("SELECT DISTINCT customer_id FROM batch").collect()]
    cond = "customer_id IN (" + ",".join(f"'{k}'" for k in sorted(keys)) + ")"
    for _ in range(2):
        hist.write.format("delta").mode("overwrite").option("replaceWhere", cond).saveAsTable("scd.silver")
    cur3 = R.val("SELECT city FROM scd.silver WHERE customer_id = 'C-77' AND is_current")
    multi = R.val("SELECT count(*) FROM (SELECT customer_id FROM scd.silver WHERE is_current GROUP BY customer_id HAVING count(*) <> 1)")
    overl = R.val("SELECT count(*) FROM scd.silver a JOIN scd.silver b ON a.customer_id = b.customer_id AND a.valid_from < b.valid_from AND (a.valid_to IS NULL OR a.valid_to > b.valid_from)")
    noop3 = R.val("SELECT count(*) FROM scd.silver WHERE customer_id = 'C-80'")
    city_at = R.val("SELECT city FROM scd.silver WHERE customer_id = 'C-77' AND timestamp'2026-10-25 00:00:00' >= valid_from AND (valid_to IS NULL OR timestamp'2026-10-25 00:00:00' < valid_to)")
    R.log("INFO", f"right fix: history rebuilt for {len(keys)} key(s) from all their changes in changed_at order; run twice")
    R.pstep("scd2", "Right fix: rebuild the history of affected keys, in source order", f"For every customer touched by the batch, take all of their changes ever (old and new), order them by when they happened in the source (changed_at, never load time), drop changes that change nothing (hash equals the previous one), and derive valid_to from the next version. Then replace just those customers' rows in one atomic write (replaceWhere). Ran twice. Asha: Pune → Goa (20 Oct) → Mumbai → Sydney, current = {cur3}; on 25 Oct she lived in {city_at}. Ravi: still one version.",
            rebuild + "\n\n# replace only the affected customers, atomically\nhist.write.format('delta').mode('overwrite').option('replaceWhere', \"" + cond + "\").saveAsTable('scd.silver')",
            [chk("current city of C-77 = Sydney", cur3, cur3 == "Sydney"), chk("exactly one current row per key", f"{multi} keys wrong", multi == 0), chk("no overlapping valid ranges", f"{overl} overlaps", overl == 0),
             chk("no-op change ignored for C-80", f"{noop3} version", noop3 == 1), chk("late Goa change slotted into the past", f"25 Oct → {city_at}", city_at == "Goa")],
            {"silver": R.table("scd.silver", ["customer_id", "valid_from"])}, None, "scd.silver")

    # =================================================================== 4. late data
    sql("CREATE TABLE late.events (order_id STRING, event_date DATE, amount DOUBLE, _batch STRING) USING delta")
    sql("CREATE TABLE late.daily (event_date DATE, orders BIGINT, revenue DOUBLE) USING delta PARTITIONED BY (event_date)")
    sql("""INSERT INTO late.events VALUES ('2001', date'2026-10-26', 300, 'b-26'), ('2002', date'2026-10-26', 450, 'b-26')""")
    daily_sql = "SELECT event_date, count(*) AS orders, sum(amount) AS revenue FROM late.events WHERE event_date = '{d}' GROUP BY event_date"
    spark.sql(daily_sql.format(d="2026-10-26")).write.format("delta").mode("overwrite").option("replaceWhere", "event_date = '2026-10-26'").saveAsTable("late.daily")
    # 27 Oct's batch contains one 26 Oct order that the phone app held back offline
    sql("""INSERT INTO late.events VALUES ('2003', date'2026-10-27', 800, 'b-27'), ('2004', date'2026-10-27', 120, 'b-27'), ('2005', date'2026-10-26', 999, 'b-27')""")
    truth = {r.event_date.isoformat(): r.revenue for r in sql("SELECT event_date, sum(amount) revenue FROM late.events GROUP BY event_date").collect()}

    def daily_tbl():
        return R.table("late.daily", ["event_date"])

    def day(d):
        return R.val(f"SELECT revenue FROM late.daily WHERE event_date = '{d}'")
    # naive: build only today's partition
    spark.sql(daily_sql.format(d="2026-10-27")).write.format("delta").mode("overwrite").option("replaceWhere", "event_date = '2026-10-27'").saveAsTable("late.daily")
    R.log("ERROR", f"26 Oct shows {money(day('2026-10-26'))}; the source now says {money(truth['2026-10-26'])}")
    R.pstep("late", "What you see: yesterday is wrong, and stays wrong", f"Order 2005 was placed on 26 Oct, but the phone app was offline and sent it with 27 Oct's batch. The nightly job only builds 'today'. So 27 Oct is right ({money(day('2026-10-27'))}), but 26 Oct still says {money(day('2026-10-26'))} when the source now says {money(truth['2026-10-26'])}, and nothing will ever fix it.",
            "# the job builds only the partition for the run date\nbuild_daily(run_date='2026-10-27')",
            [chk("26 Oct = source", f"{money(day('2026-10-26'))} vs {money(truth['2026-10-26'])}", day("2026-10-26") == truth["2026-10-26"]),
             chk("27 Oct = source", f"{money(day('2026-10-27'))} vs {money(truth['2026-10-27'])}", day("2026-10-27") == truth["2026-10-27"])],
            {"daily": daily_tbl(), "events": R.table("late.events", ["_batch", "order_id"])},
            {"tiles": [["26 Oct", money(day("2026-10-26"))], ["27 Oct", money(day("2026-10-27"))], ["26 Oct truth", money(truth["2026-10-26"])], ["Correct", "✗ no"]]})
    # naive fix: group by load batch date (puts the order on the wrong day) -> show by building 27 from batch b-27
    wrong = sql("SELECT sum(amount) FROM late.events WHERE _batch = 'b-27'").first()[0]
    R.log("WARN", f"naive fix (count by arrival day): 27 Oct would show {money(wrong)}, 26 Oct still {money(day('2026-10-26'))}")
    R.pstep("late", "Naive fix: count by the day the data arrived", f"Grouping by the batch (arrival day) instead of the event date makes the totals add up overall, but it puts order 2005 on 27 Oct. 27 Oct would show {money(wrong)}, 26 Oct still {money(day('2026-10-26'))}. Both days are wrong now, and they disagree with the source system's own reports.",
            "SELECT batch_date, sum(amount) FROM events GROUP BY batch_date   -- arrival day, not event day",
            [chk("26 Oct = source", f"{money(day('2026-10-26'))} vs {money(truth['2026-10-26'])}", False), chk("27 Oct = source", f"{money(wrong)} vs {money(truth['2026-10-27'])}", wrong == truth["2026-10-27"])],
            {"by arrival day": {"cols": ["arrival day", "revenue"], "rows": [["2026-10-26", str(day("2026-10-26"))], ["2026-10-27", str(wrong)]], "count": 2}},
            {"tiles": [["26 Oct", money(day("2026-10-26"))], ["27 Oct", money(wrong)], ["26 Oct truth", money(truth["2026-10-26"])], ["Correct", "✗ no"]]})
    touched = sorted(r.event_date.isoformat() for r in sql("SELECT DISTINCT event_date FROM late.events WHERE _batch = 'b-27'").collect())
    cond = "event_date IN (" + ",".join(f"'{d}'" for d in touched) + ")"
    spark.sql(f"SELECT event_date, count(*) AS orders, sum(amount) AS revenue FROM late.events WHERE {cond} GROUP BY event_date") \
        .write.format("delta").mode("overwrite").option("replaceWhere", cond).saveAsTable("late.daily")
    R.log("INFO", f"right fix: rebuilt exactly the days this batch touched: {', '.join(touched)}")
    R.pstep("late", "Right fix: rebuild exactly the days the batch touched", f"Ask the batch which event dates it contains ({', '.join(touched)}), and rebuild exactly those days' partitions, by event date. Late data lands on the day it happened, and only the touched days are rewritten (see the last commit). For streams, the same idea is a watermark: how late data may be and still count.",
            "touched = batch.select('event_date').distinct()      # " + ", ".join(touched) + "\n(events.where(event_date IN touched).groupBy('event_date').agg(...)\n   .write.format('delta').mode('overwrite')\n   .option('replaceWhere', \"" + cond + "\").saveAsTable('late.daily'))",
            [chk("26 Oct = source", f"{money(day('2026-10-26'))} vs {money(truth['2026-10-26'])}", day("2026-10-26") == truth["2026-10-26"]),
             chk("27 Oct = source", f"{money(day('2026-10-27'))} vs {money(truth['2026-10-27'])}", day("2026-10-27") == truth["2026-10-27"]),
             chk("only touched days rewritten", ", ".join(touched), True)],
            {"daily": daily_tbl()}, {"tiles": [["26 Oct", money(day("2026-10-26"))], ["27 Oct", money(day("2026-10-27"))], ["26 Oct truth", money(truth["2026-10-26"])], ["Correct", "✓ yes"]]}, "late.daily")

    # =================================================================== 5. failure in the middle
    sql("CREATE TABLE fail.silver (order_id STRING, amount DOUBLE, _batch STRING) USING delta")
    sql("CREATE TABLE fail.gold (day STRING, revenue DOUBLE) USING delta")
    spark.createDataFrame([("3001", 500.0, "b-1"), ("3002", 700.0, "b-1")], "order_id string, amount double, _batch string").createOrReplaceTempView("b1")
    TRUE_REV = 1200.0

    def naive_job(crash):
        sql("INSERT INTO fail.silver SELECT * FROM b1")
        if crash:
            raise RuntimeError("cluster lost between silver and gold")
        sql("INSERT INTO fail.gold SELECT '2026-10-27', sum(amount) FROM fail.silver WHERE _batch = 'b-1'")
    try:
        naive_job(True)
    except RuntimeError as e:
        R.log("ERROR", f"job failed: {e}")
    s_rows = R.val("SELECT count(*) FROM fail.silver")
    g_rows = R.val("SELECT count(*) FROM fail.gold")
    R.pstep("fail", "What you see: silver moved on, gold did not", f"The job loads silver, then gold. The cluster was lost in between. Silver has the batch ({s_rows} rows); gold has nothing ({g_rows} rows). The dashboard is stale and silver and gold disagree.",
            "def job():\n    INSERT INTO silver SELECT * FROM batch     # ✓ committed\n    # 💥 cluster lost here\n    INSERT INTO gold  SELECT day, sum(amount) FROM silver WHERE _batch = 'b-1'",
            [chk("silver and gold agree", f"silver {s_rows} rows, gold {g_rows} rows", False)],
            {"silver": R.table("fail.silver"), "gold": R.table("fail.gold")}, {"tiles": [["Revenue", "—"], ["Truth", money(TRUE_REV)], ["Silver rows", str(s_rows)], ["Correct", "✗ stale"]]})
    naive_job(False)
    rev = R.val("SELECT sum(revenue) FROM fail.gold")
    s_rows = R.val("SELECT count(*) FROM fail.silver")
    R.log("ERROR", f"naive re-run: silver {s_rows} rows, revenue {money(rev)}")
    R.pstep("fail", "Naive fix: just run the whole job again", f"Re-running from the top inserts the batch into silver a second time ({s_rows} rows now), and gold sums it: revenue {money(rev)} instead of {money(TRUE_REV)}. A failure turned into a duplicate.",
            "job()   # again, from the top",
            [chk("silver rows = batch rows", f"{s_rows} vs 2", s_rows == 2), chk("revenue = truth", f"{money(rev)} vs {money(TRUE_REV)}", rev == TRUE_REV)],
            {"silver": R.table("fail.silver"), "gold": R.table("fail.gold")}, {"tiles": [["Revenue", money(rev)], ["Truth", money(TRUE_REV)], ["Silver rows", str(s_rows)], ["Correct", "✗ no"]]})
    # right fix: idempotent steps + a run log; re-run resumes
    sql("CREATE TABLE fail.silver2 (order_id STRING, amount DOUBLE, _batch STRING) USING delta")
    sql("CREATE TABLE fail.gold2 (day STRING, revenue DOUBLE) USING delta")
    run_log = []

    def good_job(crash):
        if ("silver", "b-1") not in run_log:
            sql("MERGE INTO fail.silver2 t USING b1 s ON t.order_id = s.order_id WHEN NOT MATCHED THEN INSERT *")
            run_log.append(("silver", "b-1"))
        if crash:
            raise RuntimeError("cluster lost between silver and gold")
        spark.sql("SELECT '2026-10-27' AS day, sum(amount) AS revenue FROM fail.silver2").write.format("delta").mode("overwrite").option("replaceWhere", "day = '2026-10-27'").saveAsTable("fail.gold2")
        run_log.append(("gold", "b-1"))
    try:
        good_job(True)
    except RuntimeError:
        pass
    good_job(False)
    good_job(False)
    rev2 = R.val("SELECT sum(revenue) FROM fail.gold2")
    s2 = R.val("SELECT count(*) FROM fail.silver2")
    # and a crash INSIDE a Delta write: readers never see half of it
    v_before = spark.sql("DESCRIBE HISTORY fail.silver2").agg(F.max("version")).first()[0]
    boom = F.udf(lambda x: (_ for _ in ()).throw(ValueError("bad row")) if x == "3999" else x)
    err = ""
    try:
        spark.createDataFrame([(str(3100 + i), 10.0, "b-2") for i in range(50)] + [("3999", 1.0, "b-2")], "order_id string, amount double, _batch string") \
            .repartition(2).withColumn("order_id", boom("order_id")).write.format("delta").mode("append").saveAsTable("fail.silver2")
    except Exception as e:  # noqa: BLE001
        err = next((l.strip() for l in str(e).splitlines() if "bad row" in l), "write failed")[:160]
    v_after = spark.sql("DESCRIBE HISTORY fail.silver2").agg(F.max("version")).first()[0]
    s2b = R.val("SELECT count(*) FROM fail.silver2")
    R.log("INFO", f"right fix: crash, then two re-runs: silver {s2} rows, revenue {money(rev2)}")
    R.log("INFO", f"crash inside a Delta write: version {v_before} -> {v_after}, readers see {s2b} rows")
    R.pstep("fail", "Right fix: every step safe to repeat, plus a run log", f"Each step is idempotent (MERGE into silver, replace the day in gold) and records itself in a run log. After the crash, the re-run skips silver (already done) and builds gold. Ran it twice more: silver {s2} rows, revenue {money(rev2)}. And a crash inside a single Delta write is harmless: a write failed on a bad row mid-way, the table stayed at version {v_after} (was {v_before}), and readers still see {s2b} rows. Half a write is never visible; at worst it leaves orphan files that VACUUM removes.",
            "def job(batch):\n    if not run_log.done('silver', batch):\n        MERGE INTO silver USING batch ON order_id ... WHEN NOT MATCHED THEN INSERT *\n        run_log.mark('silver', batch)\n    replace_day(gold, '2026-10-27')            # overwrite one partition\n    run_log.mark('gold', batch)\n\njob('b-1')  # 💥 after silver\njob('b-1')  # resumes: skips silver, builds gold\njob('b-1')  # again: changes nothing",
            [chk("silver rows = batch rows", f"{s2} vs 2", s2 == 2), chk("revenue = truth", f"{money(rev2)} vs {money(TRUE_REV)}", rev2 == TRUE_REV),
             chk("crash inside a write left the table unchanged", f"version {v_before} → {v_after}, {s2b} rows", v_before == v_after and s2b == s2)],
            {"silver": R.table("fail.silver2"), "gold": R.table("fail.gold2"), "run log": {"cols": ["step", "batch"], "rows": [list(x) for x in run_log], "count": len(run_log)}},
            {"tiles": [["Revenue", money(rev2)], ["Truth", money(TRUE_REV)], ["Silver rows", str(s2)], ["Correct", "✓ yes"]]}, "fail.silver2")

    env = {"spark": spark.version, "delta": "3.2.0", "master": "local[2]", "executors": [{"id": "driver", "host": "localhost", "cores": 2}], "recorded_at": now()}
    spark.stop()
    shutil.rmtree(wh, ignore_errors=True)
    return {"env": env, "jobs": {}, "steps": R.steps}


if __name__ == "__main__":
    t = time.time()
    data = run()
    OUT.write_text(json.dumps(data, indent=1, default=str))
    print(f"{len(data['steps'])} steps -> {OUT} in {time.time() - t:.0f}s")
