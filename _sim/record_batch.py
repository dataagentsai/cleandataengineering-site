"""Record the "one batch, end to end" scene for DataTwin Studio from a REAL run.

    env -u SPARK_HOME ~/CostIntelligence1/.venv/bin/python _sim/record_batch.py

Runs a tiny medallion pipeline on local Spark + Delta (the same three shop orders as the medallion
guide: order 1001 sent twice, order 1002 with no customer and a negative amount) and records, for
every step, what each studio panel shows: inputs, config and metadata (a real SQLite metadata store
using the platform's design), cluster (from Spark's event log), layers (rows), storage (the real
_delta_log commits), engine (query plans, jobs, stages, tasks), logs and the dashboard.

Three scenarios: "normal" (first run), "replay" (the same file again, through our pipeline) and
"naive" (the same file again, through a naive pipeline that appends and INSERTs).
Output: _sim/data/batch.json (read by _sim/build.py).
"""
import contextlib
import hashlib
import io
import json
import os
import shutil
import sqlite3
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

HERE = Path(__file__).resolve().parent
OUT = HERE / "data" / "batch.json"

LANDING_ROWS = [
    {"order_id": "1001", "customer": "C-77", "amount": "1,250.00", "currency": "inr", "placed": "27/10/2026 08:58", "status": "PAID "},
    {"order_id": "1002", "customer": None, "amount": "-40", "currency": "INR", "placed": "27/10/2026 08:59", "status": "paid"},
    {"order_id": "1001", "customer": "C-77", "amount": "1,250.00", "currency": "inr", "placed": "27/10/2026 08:58", "status": "PAID "},
]
YAML = """# manifests/shop_db.yaml  (merged by pull request)
source: shop_db
type: postgres
config:
  ingestion.mode: incremental
datasets:
  - name: orders
    schema: public
    table: orders
    config:
      landing.format: json
      silver.key: order_id
      silver.history: scd1
      quality.on_bad_row: quarantine
      quality.rules: customer_key not null; amount_inr >= 0
      gold.table: fact_sales
      cost.owner: sales-analytics"""

CODE = {
    "load": """loader.load("manifests/shop_db.yaml")   # validate keys, then upsert in one transaction
# INSERT INTO source_master / source_config / dataset_master / dataset_config ...""",
    "read_config": """row = db.execute("SELECT * FROM dataset_view WHERE dataset_name = 'orders'").fetchone()
config = {**platform, **source, **dataset}      # platform < source < dataset
fp = sha256(json.dumps(config, sort_keys=True))[:16]""",
    "land": """# the mover copied rows changed since the watermark into
landing/shop_db/orders/batch=b-0912/orders_2026-10-27_0900.json""",
    "bronze": """if run_log.has_succeeded("orders", "bronze", "b-0912"):
    return 0                                   # seen this batch: add nothing
df = (spark.read.json(files)
        .withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_source",   F.lit("shop_db"))
        .withColumn("_batch_id", F.lit("b-0912"))
        .withColumn("_file",     F.col("_metadata.file_path")))
df.write.format("delta").mode("append").saveAsTable("bronze.orders")""",
    "silver_clean": """typed = (bronze.filter("_batch_id = 'b-0912'")
  .select(F.col("order_id"),
          F.col("customer").alias("customer_key"),
          F.regexp_replace("amount", ",", "").cast("decimal(12,2)").alias("amount_inr"),
          F.to_utc_timestamp(F.to_timestamp("placed", "dd/MM/yyyy HH:mm"), "Asia/Kolkata").alias("placed_at_utc"),
          F.lower(F.trim("status")).alias("status"), "_batch_id"))
bad  = typed.filter("customer_key IS NULL OR amount_inr < 0")      # -> quarantine, with the rule
good = typed.subtract(bad)""",
    "silver_merge": """w = Window.partitionBy("order_id").orderBy(F.col("placed_at_utc").desc())
latest = good.withColumn("_rn", F.row_number().over(w)).filter("_rn = 1").drop("_rn")
MERGE INTO silver.orders t USING latest s ON t.order_id = s.order_id
WHEN MATCHED AND t.row_hash <> s.row_hash THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *""",
    "gold": """INSERT OVERWRITE gold.fact_sales PARTITION (order_date = '2026-10-27')
SELECT customer_key, order_id, amount_inr FROM silver.orders
WHERE to_date(placed_at_utc) = '2026-10-27'""",
    "recon": """source distinct orders = 2  ->  silver 1 + quarantine 1   (must match)
silver amount = gold amount                                (must match)""",
    "naive_bronze": """df = spark.read.json(files).withColumn(...audit columns...)
df.write.format("delta").mode("append").saveAsTable("bronze.orders")   # no batch check""",
    "naive_silver": """INSERT INTO silver.orders SELECT ... FROM bronze.orders WHERE _batch_id = 'b-0912'   # INSERT, not MERGE""",
    "naive_gold": """INSERT INTO gold.fact_sales SELECT ... FROM silver.orders   # append, not overwrite""",
}


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Recorder:
    def __init__(self, spark, wh, evdir):
        self.spark, self.wh, self.evdir = spark, wh, evdir
        self.steps, self.logs, self.run_log = [], [], []
        self.n = 0
        self._lp = self._rp = 0

    def log(self, level, msg):
        self.logs.append([now()[11:19], level, msg])

    def group(self, sid, desc):
        self.spark.sparkContext.setJobGroup(sid, desc)

    def table_rows(self, name, cols=None, order=None, limit=20):
        self.group("inspect", "reading tables for the studio (not part of the pipeline)")
        df = self.spark.table(name)
        if cols:
            df = df.select(*cols)
        if order:
            df = df.orderBy(*order)
        rows = df.limit(limit).collect()
        c = df.columns
        return {"cols": c, "rows": [[None if r[k] is None else str(r[k]) for k in c] for r in rows], "count": self.spark.table(name).count()}

    def delta_log(self, name):
        self.group("inspect", "reading tables for the studio (not part of the pipeline)")
        loc = self.spark.sql(f"DESCRIBE DETAIL {name}").first()["location"].replace("file:", "")
        files = sorted(Path(loc, "_delta_log").glob("*.json"))
        commits = []
        for f in files:
            acts = [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
            summ = []
            for a in acts:
                k = next(iter(a))
                v = a[k]
                if k == "commitInfo":
                    summ.append({"commitInfo": {"operation": v.get("operation"), "operationMetrics": v.get("operationMetrics", {}), "timestamp": v.get("timestamp")}})
                elif k in ("add", "remove"):
                    stats = json.loads(v["stats"]) if v.get("stats") else {}
                    summ.append({k: {"path": v["path"][-48:], "size": v.get("size"), "numRecords": stats.get("numRecords"), "dataChange": v.get("dataChange")}})
                elif k == "metaData":
                    summ.append({"metaData": {"partitionColumns": v.get("partitionColumns"), "schema (fields)": [x["name"] for x in json.loads(v["schemaString"])["fields"]]}})
                else:
                    summ.append({k: v})
            commits.append({"file": f.name, "actions": summ})
        data = sorted(p.name for p in Path(loc).rglob("*.parquet"))
        return {"table": name, "data_files": len(data), "commits": commits}

    def explain(self, df):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            df.explain("formatted")
        txt = buf.getvalue()
        return txt.split("\n\n(1)")[0].strip()  # the plan tree, without the per-node details

    def step(self, scenario, title, plain, focus, code, panels):
        self.n += 1
        self.steps.append({"n": self.n, "scenario": scenario, "title": title, "plain": plain, "focus": focus, "code": code,
                           "panels": panels, "logs": self.logs[self._lp:], "run_log": [list(r) for r in self.run_log[self._rp:]]})
        self._lp, self._rp = len(self.logs), len(self.run_log)


def metadata_db():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript("""
    CREATE TABLE platform_config (config_key TEXT PRIMARY KEY, config_value TEXT NOT NULL, description TEXT, updated_at TEXT);
    CREATE TABLE source_master (source_id TEXT PRIMARY KEY, source_name TEXT UNIQUE NOT NULL, source_type TEXT NOT NULL, is_active INTEGER NOT NULL DEFAULT 1);
    CREATE TABLE source_config (config_id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES source_master, config_key TEXT NOT NULL, config_value TEXT NOT NULL, config_group TEXT NOT NULL, is_active INTEGER NOT NULL DEFAULT 1, UNIQUE (source_id, config_key));
    CREATE TABLE dataset_master (dataset_id TEXT PRIMARY KEY, dataset_name TEXT NOT NULL, source_id TEXT NOT NULL REFERENCES source_master, schema_name TEXT, table_name TEXT, is_active INTEGER NOT NULL DEFAULT 1);
    CREATE TABLE dataset_config (config_id TEXT PRIMARY KEY, dataset_id TEXT NOT NULL REFERENCES dataset_master, config_key TEXT NOT NULL, config_value TEXT NOT NULL, config_group TEXT NOT NULL, is_active INTEGER NOT NULL DEFAULT 1, UNIQUE (dataset_id, config_key));
    CREATE VIEW dataset_view AS
    SELECT dm.dataset_id, dm.dataset_name, sm.source_name,
      COALESCE((SELECT json_group_object(config_key, config_value) FROM source_config sc WHERE sc.source_id = sm.source_id AND sc.is_active), '{}') AS source_config_json,
      COALESCE((SELECT json_group_object(config_key, config_value) FROM dataset_config dc WHERE dc.dataset_id = dm.dataset_id AND dc.is_active), '{}') AS dataset_config_json,
      COALESCE((SELECT json_group_object(config_key, config_value) FROM platform_config), '{}') AS platform_config_json
    FROM dataset_master dm JOIN source_master sm ON sm.source_id = dm.source_id
    WHERE dm.is_active AND sm.is_active;
    """)
    return db


def load_manifest(db):
    import uuid
    u = lambda: str(uuid.uuid4())[:8]  # noqa: E731  short ids for display
    db.executemany("INSERT INTO platform_config VALUES (?,?,?,?)", [("timezone", "UTC", "platform default", now()), ("retry.max", "3", "", now()), ("quality.on_bad_row", "fail", "safe default", now())])
    sid = u()
    db.execute("INSERT INTO source_master VALUES (?,?,?,1)", (sid, "shop_db", "postgres"))
    db.execute("INSERT INTO source_config VALUES (?,?,?,?,?,1)", (u(), sid, "ingestion.mode", "incremental", "ingestion"))
    did = u()
    db.execute("INSERT INTO dataset_master VALUES (?,?,?,?,?,1)", (did, "orders", sid, "public", "orders"))
    for k, v, g in [("landing.format", "json", "ingestion"), ("silver.key", "order_id", "silver"), ("silver.history", "scd1", "silver"),
                    ("quality.on_bad_row", "quarantine", "quality"), ("quality.rules", "customer_key not null; amount_inr >= 0", "quality"),
                    ("gold.table", "fact_sales", "gold"), ("cost.owner", "sales-analytics", "cost")]:
        db.execute("INSERT INTO dataset_config VALUES (?,?,?,?,?,1)", (u(), did, k, v, g))
    db.commit()


def db_tables(db):
    out = {}
    for t in ["platform_config", "source_master", "source_config", "dataset_master", "dataset_config"]:
        cur = db.execute(f"SELECT * FROM {t}")
        cols = [d[0] for d in cur.description]
        out[t] = {"cols": cols, "rows": [[str(x) for x in r] for r in cur.fetchall()]}
    return out


def parse_eventlog(evdir):
    f = next(Path(evdir).iterdir())
    jobs, stages, tasks, execs = {}, {}, [], []
    for line in f.read_text().splitlines():
        e = json.loads(line)
        ev = e["Event"]
        if ev == "SparkListenerJobStart":
            jobs[e["Job ID"]] = {"group": e.get("Properties", {}).get("spark.jobGroup.id"), "desc": e.get("Properties", {}).get("spark.job.description"),
                                 "stages": e["Stage IDs"], "start": e["Submission Time"]}
        elif ev == "SparkListenerJobEnd":
            jobs[e["Job ID"]]["end"] = e["Completion Time"]
        elif ev == "SparkListenerStageCompleted":
            si = e["Stage Info"]
            stages[si["Stage ID"]] = {"name": si["Stage Name"][:60], "tasks": si["Number of Tasks"], "ms": (si.get("Completion Time", 0) - si.get("Submission Time", 0))}
        elif ev == "SparkListenerTaskEnd":
            ti, m = e["Task Info"], e.get("Task Metrics") or {}
            tasks.append({"stage": e["Stage ID"], "ms": ti["Finish Time"] - ti["Launch Time"], "exec": ti["Executor ID"],
                          "shuffle_write": (m.get("Shuffle Write Metrics") or {}).get("Shuffle Bytes Written", 0),
                          "shuffle_read": sum((m.get("Shuffle Read Metrics") or {}).get(k, 0) for k in ("Remote Bytes Read", "Local Bytes Read"))})
        elif ev == "SparkListenerExecutorAdded":
            execs.append({"id": e["Executor ID"], "host": e["Executor Info"]["Host"], "cores": e["Executor Info"]["Total Cores"]})
        elif ev == "SparkListenerEnvironmentUpdate":
            pass
    by_group = {}
    for jid, j in sorted(jobs.items()):
        g = j["group"] or "other"
        st = [{"id": s, **stages.get(s, {"name": "skipped", "tasks": 0, "ms": 0}), "task_ms": [t["ms"] for t in tasks if t["stage"] == s],
               "shuffle_write": sum(t["shuffle_write"] for t in tasks if t["stage"] == s), "shuffle_read": sum(t["shuffle_read"] for t in tasks if t["stage"] == s)}
              for s in j["stages"] if s in stages]
        by_group.setdefault(g, []).append({"job": jid, "desc": (j["desc"] or "")[:70], "ms": j.get("end", j["start"]) - j["start"], "stages": st})
    return by_group, execs


def run(scenario_steps="all"):
    wh = tempfile.mkdtemp(prefix="dts-wh-")
    evdir = tempfile.mkdtemp(prefix="dts-ev-")
    landing = Path(tempfile.mkdtemp(prefix="dts-landing-")) / "landing/shop_db/orders/batch=b-0912"
    landing.mkdir(parents=True)
    lf = landing / "orders_2026-10-27_0900.json"
    lf.write_text("\n".join(json.dumps(r) for r in LANDING_ROWS) + "\n")
    b = (SparkSession.builder.master("local[2]").appName("DataTwin Studio recording")
         .config("spark.sql.warehouse.dir", wh).config("spark.eventLog.enabled", "true").config("spark.eventLog.dir", evdir)
         .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
         .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
         .config("spark.sql.shuffle.partitions", "2").config("spark.ui.enabled", "false")
         .config("spark.sql.session.timeZone", "UTC"))
    spark = configure_spark_with_delta_pip(b).getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    R = Recorder(spark, wh, evdir)
    sql = spark.sql
    for db_ in ("bronze", "silver", "gold", "naive_bronze", "naive_silver", "naive_gold"):
        sql(f"CREATE DATABASE {db_}")
    sql("CREATE TABLE silver.orders (order_id string, customer_key string, amount_inr decimal(12,2), placed_at_utc timestamp, status string, row_hash string, _batch_id string) USING delta")
    sql("CREATE TABLE silver.quarantine (order_id string, rule_failed string, _batch_id string, quarantined_at timestamp) USING delta")
    sql("CREATE TABLE gold.fact_sales (customer_key string, order_id string, amount_inr decimal(12,2), order_date date) USING delta PARTITIONED BY (order_date)")
    for t in ("silver.orders", "gold.fact_sales"):
        sql(f"CREATE TABLE naive_{t} LIKE {t}") if False else None
    sql("CREATE TABLE naive_silver.orders (order_id string, customer_key string, amount_inr decimal(12,2), placed_at_utc timestamp, status string, _batch_id string) USING delta")
    sql("CREATE TABLE naive_gold.fact_sales (customer_key string, order_id string, amount_inr decimal(12,2), order_date date) USING delta PARTITIONED BY (order_date)")

    db = metadata_db()
    inputs = {"file": "landing/shop_db/orders/batch=b-0912/orders_2026-10-27_0900.json", "text": lf.read_text(), "user": "Asha (data engineer) merges a pull request that onboards the orders table."}
    empty_dash = {"tiles": [["Revenue, 27 Oct", "—"], ["Orders", "—"], ["Quarantined", "—"], ["Reconciled", "—"]]}

    # 1. onboard
    R.log("INFO", "manifest shop_db.yaml merged to main (PR #42)")
    R.step("normal", "Onboard the orders table", "A data engineer describes the orders table in YAML and merges a pull request. No pipeline code is written.",
           ["inputs", "config"], "", {"inputs": {**inputs, "text": "(no data yet)"}, "config": {"yaml": YAML}, "dashboard": empty_dash})
    # 2. loader
    load_manifest(db)
    R.log("INFO", "loader: 9 keys validated against the key registry; 1 source, 1 dataset, 7 dataset settings written")
    R.step("normal", "The loader writes the metadata DB", "The loader checks every key against the key registry, then writes the five tables in one transaction.",
           ["config"], CODE["load"], {"config": {"yaml": YAML, "db": db_tables(db)}})
    # 3. read config
    row = db.execute("SELECT * FROM dataset_view WHERE dataset_name='orders'").fetchone()
    plat, src, ds = (json.loads(row[k]) for k in ("platform_config_json", "source_config_json", "dataset_config_json"))
    cfg = {**plat, **src, **ds}
    fp = hashlib.sha256(json.dumps(cfg, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
    R.log("INFO", f"orders: config read from dataset_view, fingerprint {fp}")
    R.step("normal", "The pipeline reads its settings", "The pipeline reads one row from dataset_view and merges the settings: platform, then source, then dataset. Note quality.on_bad_row: the platform says 'fail', the dataset overrides it with 'quarantine'.",
           ["config"], CODE["read_config"], {"config": {"yaml": YAML, "db": db_tables(db), "view": {"platform": plat, "source": src, "dataset": ds}, "merged": cfg, "fingerprint": fp}})
    # 4. landing
    R.log("INFO", "mover: 3 rows written to landing batch b-0912")
    R.step("normal", "The mover drops a file in landing", "The mover copies changed rows from the shop's database into a landing file, untouched. Order 1001 came twice; order 1002 has no customer and a negative amount.",
           ["inputs", "layers", "storage"], CODE["land"],
           {"inputs": inputs, "layers": {"landing": {"cols": list(LANDING_ROWS[0].keys()), "rows": [[str(v) if v is not None else None for v in r.values()] for r in LANDING_ROWS], "count": 3}},
            "storage": {"landing": [inputs["file"]]}})

    def bronze_step(scenario, naive=False):
        tgt = "naive_bronze.orders" if naive else "bronze.orders"
        sid = f"{scenario}-bronze"
        R.group(sid, "landing -> bronze")
        seen = any(r[1] == "bronze" and r[2] == "b-0912" and r[3] == "succeeded" and r[0] == ("naive" if naive else "ours") for r in R.run_log)
        if seen and not naive:
            R.log("INFO", "bronze: batch b-0912 already succeeded -> skipped, 0 rows added")
            R.run_log.append(["ours", "bronze", "b-0912", "skipped", fp, 0])
            return 0
        df = (spark.read.json(str(lf)).withColumn("_ingested_at", F.current_timestamp()).withColumn("_source", F.lit("shop_db"))
              .withColumn("_batch_id", F.lit("b-0912")).withColumn("_file", F.lit(lf.name)))
        plan = R.explain(df)
        df.write.format("delta").mode("append").saveAsTable(tgt)
        n = df.count()
        R.run_log.append(["naive" if naive else "ours", "bronze", "b-0912", "succeeded", fp, n])
        R.log("INFO", f"bronze: {n} rows appended to {tgt} (batch b-0912)")
        return plan

    def silver_step(scenario):
        R.group(f"{scenario}-silver", "bronze -> silver")
        bronze = spark.table("bronze.orders").filter("_batch_id = 'b-0912'").dropDuplicates(["order_id", "_ingested_at", "customer", "amount"])
        typed = bronze.select(F.col("order_id"), F.col("customer").alias("customer_key"),
                              F.regexp_replace("amount", ",", "").cast("decimal(12,2)").alias("amount_inr"),
                              F.to_utc_timestamp(F.to_timestamp("placed", "dd/MM/yyyy HH:mm"), "Asia/Kolkata").alias("placed_at_utc"),
                              F.lower(F.trim("status")).alias("status"), "_batch_id")
        bad = typed.filter("customer_key IS NULL OR amount_inr < 0")
        good = typed.subtract(bad)
        w = Window.partitionBy("order_id").orderBy(F.col("placed_at_utc").desc())
        latest = (good.withColumn("_rn", F.row_number().over(w)).filter("_rn = 1").drop("_rn")
                  .withColumn("row_hash", F.sha2(F.concat_ws("|", "customer_key", "amount_inr", "placed_at_utc", "status"), 256).substr(1, 12)))
        plan = R.explain(latest)
        latest.createOrReplaceTempView("latest")
        (bad.select("order_id", F.lit("customer_key is required; amount must be >= 0").alias("rule_failed"), "_batch_id", F.current_timestamp().alias("quarantined_at"))
            .createOrReplaceTempView("bad"))
        sql("MERGE INTO silver.quarantine t USING bad s ON t.order_id = s.order_id AND t._batch_id = s._batch_id WHEN NOT MATCHED THEN INSERT *")
        sql("""MERGE INTO silver.orders t USING latest s ON t.order_id = s.order_id
               WHEN MATCHED AND t.row_hash <> s.row_hash THEN UPDATE SET *
               WHEN NOT MATCHED THEN INSERT *""")
        nb, nq = bronze.count(), bad.count()
        R.run_log.append(["ours", "silver", "b-0912", "succeeded", fp, spark.table("silver.orders").count()])
        R.log("INFO", f"silver: {nb} bronze rows -> {latest.count()} after dedupe; {nq} quarantined (customer_key is required; amount must be >= 0)")
        return plan, typed

    def gold_step(scenario):
        R.group(f"{scenario}-gold", "silver -> gold")
        q = sql("SELECT customer_key, order_id, amount_inr FROM silver.orders WHERE to_date(placed_at_utc) = '2026-10-27'")
        plan = R.explain(q)
        sql("""INSERT OVERWRITE gold.fact_sales PARTITION (order_date = '2026-10-27')
               SELECT customer_key, order_id, amount_inr FROM silver.orders WHERE to_date(placed_at_utc) = '2026-10-27'""")
        s_amt = sql("SELECT coalesce(sum(amount_inr),0) a, count(*) c FROM silver.orders").first()
        g_amt = sql("SELECT coalesce(sum(amount_inr),0) a, count(*) c FROM gold.fact_sales").first()
        q_n = spark.table("silver.quarantine").count()
        src_distinct = len({r["order_id"] for r in LANDING_ROWS})
        ok = (src_distinct == s_amt.c + q_n) and (s_amt.a == g_amt.a)
        R.run_log.append(["ours", "gold", "b-0912", "succeeded", fp, g_amt.c])
        R.log("INFO" if ok else "ERROR", f"reconcile: source {src_distinct} distinct = silver {s_amt.c} + quarantine {q_n}; silver ₹{s_amt.a} = gold ₹{g_amt.a} -> {'OK' if ok else 'MISMATCH'}")
        return plan, ok, g_amt, q_n

    def layers_now(prefix=""):
        out = {"landing": {"cols": list(LANDING_ROWS[0].keys()), "rows": [[str(v) if v is not None else None for v in r.values()] for r in LANDING_ROWS], "count": 3}}
        bt, st, gt = (f"{prefix}bronze.orders", f"{prefix}silver.orders", f"{prefix}gold.fact_sales")
        if spark.catalog.tableExists(bt):
            out["bronze"] = R.table_rows(bt, ["order_id", "customer", "amount", "currency", "placed", "status", "_ingested_at", "_batch_id"], ["_ingested_at", "order_id"])
        out["silver"] = R.table_rows(st, [c for c in spark.table(st).columns if c != "row_hash"], ["order_id"])
        if not prefix:
            out["quarantine"] = R.table_rows("silver.quarantine", ["order_id", "rule_failed", "_batch_id"])
        out["gold"] = R.table_rows(gt, None, ["order_id"])
        return out

    def storage_now(prefix=""):
        out = {"landing": [inputs["file"]]}
        for t in (f"{prefix}bronze.orders", f"{prefix}silver.orders", f"{prefix}gold.fact_sales"):
            if spark.catalog.tableExists(t):
                out[t] = R.delta_log(t)
        return out

    def dash(g, q_n, ok, prefix=""):
        return {"tiles": [["Revenue, 27 Oct", f"₹{float(g.a):,.0f}"], ["Orders", str(g.c)], ["Quarantined", str(q_n)], ["Reconciled", "✓ yes" if ok else "✗ no"]],
                "note": "Read from gold through the semantic layer's net_revenue."}

    # 5. bronze
    plan_b = bronze_step("normal")
    R.step("normal", "Landing → bronze", "The lander checks the run log (batch b-0912 not seen yet), reads the file, adds four audit columns and appends to bronze in one Delta commit. Bronze keeps everything: strings, the duplicate, the bad row.",
           ["layers", "storage", "engine", "cluster", "logs"], CODE["bronze"],
           {"layers": layers_now(), "storage": storage_now(), "engine": {"plan": plan_b, "group": "normal-bronze"}})
    # 6. silver clean
    plan_s, typed = silver_step("normal")
    R.step("normal", "Bronze → silver: clean, quarantine, dedupe, MERGE", "Types are cast, codes standardised, India time turned into UTC. Order 1002 breaks the contract and goes to quarantine with its reason. The duplicate 1001 collapses to one row. A MERGE on order_id writes silver.",
           ["layers", "storage", "engine", "cluster", "logs"], CODE["silver_clean"] + "\n\n" + CODE["silver_merge"],
           {"layers": layers_now(), "storage": storage_now(), "engine": {"plan": plan_s, "group": "normal-silver"}})
    # 7. gold
    plan_g, ok, g, q_n = gold_step("normal")
    R.step("normal", "Silver → gold, then reconcile", "Gold rebuilds the day's partition from silver. Then reconciliation checks: 2 distinct orders in the source = 1 in silver + 1 in quarantine, and silver's amount equals gold's.",
           ["layers", "storage", "engine", "cluster", "logs"], CODE["gold"] + "\n\n# reconcile\n" + CODE["recon"],
           {"layers": layers_now(), "storage": storage_now(), "engine": {"plan": plan_g, "group": "normal-gold"}})
    # 8. dashboard
    R.step("normal", "The dashboard updates", "The revenue tile reads net_revenue from the semantic layer: ₹1,250 for 27 October, one order, one quarantined, reconciled.",
           ["dashboard", "logs"], "", {"dashboard": dash(g, q_n, ok)})

    # ---------- replay through our pipeline
    R.log("WARN", "mover: batch b-0912 re-sent (retry after a network timeout)")
    R.step("replay", "The same file arrives again", "A network timeout made the mover send batch b-0912 a second time. This happens in real life all the time.",
           ["inputs", "logs"], "", {"inputs": {**inputs, "user": "Nobody did anything: the mover retried after a timeout and re-sent batch b-0912."}})
    bronze_step("replay")
    R.step("replay", "Landing → bronze: batch check", "The lander looks in the run log first: batch b-0912 already succeeded, so it adds nothing. No Spark job runs at all.",
           ["layers", "storage", "logs"], CODE["bronze"].split("\n")[0:2] and "\n".join(CODE["bronze"].split("\n")[0:2]),
           {"layers": layers_now(), "storage": storage_now()})
    plan_s2, _ = silver_step("replay")
    R.step("replay", "Bronze → silver: MERGE changes nothing", "Even if silver runs again, MERGE on order_id finds the same row with the same hash: 0 rows inserted, 0 updated, so the data is safe. But look at the new commit in silver's _delta_log: Delta still removed one file and wrote a new one, copying the unchanged row. Safe for the data, not free. Filtering unchanged rows out before the MERGE (compare row_hash first) avoids the rewrite.",
           ["layers", "storage", "engine", "logs"], CODE["silver_merge"], {"layers": layers_now(), "storage": storage_now(), "engine": {"plan": plan_s2, "group": "replay-silver"}})
    plan_g2, ok2, g2, q2 = gold_step("replay")
    R.step("replay", "Gold and the dashboard: unchanged", "Gold overwrites the same partition with the same rows. Reconciliation passes. The dashboard still says ₹1,250.",
           ["layers", "dashboard", "logs"], CODE["gold"], {"layers": layers_now(), "storage": storage_now(), "dashboard": dash(g2, q2, ok2)})

    # ---------- naive pipeline: same first run, then the re-send
    def naive_run(tag):
        R.group(f"naive-{tag}", "naive pipeline")
        df = (spark.read.json(str(lf)).withColumn("_ingested_at", F.current_timestamp()).withColumn("_source", F.lit("shop_db"))
              .withColumn("_batch_id", F.lit("b-0912")).withColumn("_file", F.lit(lf.name)))
        df.write.format("delta").mode("append").saveAsTable("naive_bronze.orders")
        R.run_log.append(["naive", "bronze", "b-0912", "succeeded", fp, 3])
        sql("""INSERT INTO naive_silver.orders
               SELECT order_id, customer, CAST(regexp_replace(amount, ',', '') AS decimal(12,2)),
                      to_utc_timestamp(to_timestamp(placed, 'dd/MM/yyyy HH:mm'), 'Asia/Kolkata'), lower(trim(status)), _batch_id
               FROM (SELECT DISTINCT order_id, customer, amount, placed, status, _batch_id FROM naive_bronze.orders WHERE _batch_id = 'b-0912' AND _ingested_at = (SELECT max(_ingested_at) FROM naive_bronze.orders))
               WHERE customer IS NOT NULL AND CAST(regexp_replace(amount, ',', '') AS decimal(12,2)) >= 0""")
        sql("""INSERT OVERWRITE naive_gold.fact_sales PARTITION (order_date = '2026-10-27')
               SELECT customer_key, order_id, amount_inr FROM naive_silver.orders""")

    R.log("INFO", "naive pipeline: first run of batch b-0912")
    naive_run("first")
    g_first = sql("SELECT coalesce(sum(amount_inr),0) a, count(*) c FROM naive_gold.fact_sales").first()
    R.step("naive", "A naive pipeline, first run", "Same file, but a naive pipeline: no batch check in bronze, INSERT instead of MERGE in silver, and bad rows filtered out with a WHERE clause instead of quarantined. The first run looks fine: ₹1,250.",
           ["layers", "dashboard", "logs"], CODE["naive_bronze"] + "\n" + CODE["naive_silver"],
           {"layers": layers_now("naive_"), "storage": storage_now("naive_"), "dashboard": {"tiles": [["Revenue, 27 Oct", f"₹{float(g_first.a):,.0f}"], ["Orders", str(g_first.c)], ["Quarantined", "0 ⚠"], ["Reconciled", "not checked"]], "note": "⚠ Looks fine. But order 1002 has already vanished: the naive pipeline filtered it out instead of quarantining it."}})
    R.log("WARN", "mover: batch b-0912 re-sent (retry after a network timeout)")
    R.log("INFO", "naive pipeline: batch b-0912 processed again")
    naive_run("again")
    g_n = sql("SELECT coalesce(sum(amount_inr),0) a, count(*) c FROM naive_gold.fact_sales").first()
    gd = sql("SELECT count(DISTINCT order_id) FROM naive_gold.fact_sales").first()[0]
    ok_n = False
    R.log("INFO", f"row-count check: source {len(LANDING_ROWS) - 1} unique rows, gold {g_n.c} rows -> passes by coincidence (a duplicate hides a dropped row)")
    R.log("ERROR", f"reconcile by key: source 2 distinct orders = gold {gd} distinct + quarantine 0 -> MISMATCH; gold has {g_n.c} rows for {gd} order(s) -> duplicate key; revenue ₹{float(g_n.a):,.0f}")
    R.step("naive", "The same file again: revenue doubles", "Bronze appends the batch again (6 rows). Silver INSERTs order 1001 a second time. Gold now has two rows for one order and the dashboard says ₹2,500. Only reconciliation against the source notices.",
           ["layers", "storage", "dashboard", "logs"], CODE["naive_bronze"] + "\n" + CODE["naive_silver"],
           {"layers": layers_now("naive_"), "storage": storage_now("naive_"),
            "dashboard": {"tiles": [["Revenue, 27 Oct", f"₹{float(g_n.a):,.0f}"], ["Orders", str(g_n.c)], ["Quarantined", "0 ⚠"], ["Reconciled", "✗ no"]],
                          "note": "⚠ 0 quarantined because order 1002 was dropped silently. Two bugs. Order 1001 is counted twice (no batch check, INSERT not MERGE), and order 1002 was dropped by a WHERE clause instead of quarantined. A simple row count passes by coincidence; only reconciling by key catches both. Compare with 'Same file again, our pipeline'."}})

    groups, execs = parse_eventlog(evdir)
    env = {"spark": spark.version, "delta": "3.2.0", "master": "local[2]", "executors": execs,
           "shuffle_partitions": spark.conf.get("spark.sql.shuffle.partitions"), "recorded_at": now()}
    spark.stop()
    for d in (wh, evdir, str(landing.parents[3])):
        shutil.rmtree(d, ignore_errors=True)
    return {"env": env, "jobs": groups, "steps": R.steps}


if __name__ == "__main__":
    t = time.time()
    data = run()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1, default=str))
    print(f"{len(data['steps'])} steps, {sum(len(v) for v in data['jobs'].values())} jobs -> {OUT} in {time.time() - t:.0f}s")
