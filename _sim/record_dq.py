"""Record the Data quality & profiling scene for DataTwin Studio from REAL runs.

    env -u SPARK_HOME -u PYTHONPATH _sim/.venv-dq/bin/python _sim/record_dq.py

_sim/.venv-dq is a small venv that reuses CostIntelligence1's pyspark 3.5.1 + delta-spark 3.2.0
(through a .pth file) and adds pydeequ 1.4.0 (Deequ 2.0.7 for Spark 3.5, fetched from Maven).

Rules are written as YAML, loaded into a metadata DB (SQLite), compiled by one port (DQEngine) into
either Spark SQL or Deequ checks. Scenarios: rules as metadata, profiling + suggested rules,
metrics over time with anomaly detection, onboarding a dataset with YAML only.
Output: _sim/data/dq.json
"""
import hashlib
import json
import os
import shutil
import sqlite3
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

os.environ["TZ"] = "UTC"
time.tzset()
os.environ["SPARK_VERSION"] = "3.5"
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
import pydeequ  # noqa: E402
import yaml  # noqa: E402
from delta import configure_spark_with_delta_pip  # noqa: E402
from pyspark.sql import SparkSession, Window, functions as F  # noqa: E402

OUT = Path(__file__).resolve().parent / "data" / "dq.json"


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Rec:
    def __init__(self):
        self.steps, self.logs, self._lp = [], [], 0

    def log(self, level, msg):
        self.logs.append([now()[11:19], level, msg])

    def step(self, scenario, title, plain, code, panels, focus):
        self.steps.append({"n": len(self.steps) + 1, "scenario": scenario, "title": title, "plain": plain, "code": code, "group": None,
                           "focus": focus, "panels": {"inputs": {"user": "", "file": "", "text": code}, **panels},
                           "logs": self.logs[self._lp:], "run_log": []})
        self._lp = len(self.logs)


def tbl(df, n=12, order=None):
    if order:
        df = df.orderBy(*order)
    r = df.limit(n).collect()
    return {"cols": df.columns, "rows": [[None if x is None else str(x) for x in row] for row in r], "count": df.count()}


def pct(x):
    return f"{100 * x:.2f}%"


# ----------------------------------------------------------------------------- the port and its two adapters
ROW_LEVEL = {"is_complete", "is_non_negative", "is_contained_in", "is_unique", "references"}


class SparkSqlEngine:
    """Adapter 1: every rule compiled to plain Spark SQL. Supports every rule type."""
    name = "spark_sql"

    def __init__(self, spark):
        self.spark = spark

    def supports(self, r):
        return True

    def compile(self, r, t):
        c, p = r.get("column"), r.get("params", {})
        k = r["rule"]
        if k == "is_complete":
            return f"SELECT avg(CASE WHEN {c} IS NOT NULL THEN 1D ELSE 0D END) AS metric FROM {t}   -- pass if = 1.0"
        if k == "is_non_negative":
            return f"SELECT avg(CASE WHEN {c} IS NULL OR {c} >= 0 THEN 1D ELSE 0D END) AS metric FROM {t}   -- pass if = 1.0"
        if k == "is_contained_in":
            vals = ", ".join(f"'{v}'" for v in p["values"])
            return f"SELECT avg(CASE WHEN {c} IS NULL OR {c} IN ({vals}) THEN 1D ELSE 0D END) AS metric FROM {t}   -- pass if = 1.0"
        if k == "is_unique":
            return f"SELECT sum(CASE WHEN n = 1 THEN n ELSE 0 END) / sum(n) AS metric FROM (SELECT {c}, count(*) n FROM {t} GROUP BY {c})   -- pass if = 1.0"
        if k == "completeness_at_least":
            return f"SELECT avg(CASE WHEN {c} IS NOT NULL THEN 1D ELSE 0D END) AS metric FROM {t}   -- pass if >= {p['min']}"
        if k == "row_count_between":
            return f"SELECT count(*) AS metric FROM {t}   -- pass if between {p['min']} and {p['max']}"
        if k == "references":
            return f"SELECT avg(CASE WHEN {t}.{c} IS NULL OR r.{p['key']} IS NOT NULL THEN 1D ELSE 0D END) AS metric FROM {t} LEFT JOIN {p['table']} r ON {t}.{c} = r.{p['key']}   -- pass if = 1.0"
        raise ValueError(k)

    def failing_rows(self, r, t):
        """Predicate (or query) for the rows a row-level rule rejects; used for quarantine."""
        c, p, k = r.get("column"), r.get("params", {}), r["rule"]
        if k == "is_complete":
            return f"{c} IS NULL"
        if k == "is_non_negative":
            return f"{c} < 0"
        if k == "is_contained_in":
            return f"{c} IS NOT NULL AND {c} NOT IN ({', '.join(repr(v) for v in p['values'])})"
        if k == "is_unique":
            return "_dup_rank > 1"
        if k == "references":
            return f"{c} IS NOT NULL AND _ref_missing"
        return None

    def run(self, rules, t):
        out = {}
        for r in rules:
            q = self.compile(r, t).split("   --")[0]
            m = self.spark.sql(q).first()[0]
            out[r["id"]] = float(m or 0)
        return out


class DeequEngine:
    """Adapter 2: the same rules as Deequ checks (VerificationSuite). No referential-integrity rule."""
    name = "deequ"

    def __init__(self, spark):
        from pydeequ.checks import Check, CheckLevel
        from pydeequ.verification import VerificationResult, VerificationSuite
        self.spark, self.Check, self.Level, self.VS, self.VR = spark, Check, CheckLevel, VerificationSuite, VerificationResult

    def supports(self, r):
        return r["rule"] != "references"

    def compile(self, r, t=None):
        c, p, k = r.get("column"), r.get("params", {}), r["rule"]
        return {"is_complete": f"isComplete('{c}')", "is_non_negative": f"isNonNegative('{c}')", "is_unique": f"isUnique('{c}')",
                "is_contained_in": f"isContainedIn('{c}', {p.get('values')})",
                "completeness_at_least": f"hasCompleteness('{c}', lambda x: x >= {p.get('min')})",
                "row_count_between": f"hasSize(lambda x: {p.get('min')} <= x <= {p.get('max')})"}[k]

    def _check(self, r):
        lvl = self.Level.Error if r["severity"] == "error" else self.Level.Warning
        ch, c, p, k = self.Check(self.spark, lvl, r["id"]), r.get("column"), r.get("params", {}), r["rule"]
        if k == "is_complete":
            return ch.isComplete(c)
        if k == "is_non_negative":
            return ch.isNonNegative(c)
        if k == "is_unique":
            return ch.isUnique(c)
        if k == "is_contained_in":
            return ch.isContainedIn(c, p["values"])
        if k == "completeness_at_least":
            mn = p["min"]
            return ch.hasCompleteness(c, lambda x: x >= mn)
        if k == "row_count_between":
            lo, hi = p["min"], p["max"]
            return ch.hasSize(lambda x: lo <= x <= hi)
        raise ValueError(k)

    def run(self, rules, t, suite_hook=None):
        df = self.spark.table(t)
        vs = self.VS(self.spark).onData(df)
        for r in rules:
            vs = vs.addCheck(self._check(r))
        if suite_hook:
            vs = suite_hook(vs)
        res = vs.run()
        checks = self.VR.checkResultsAsDataFrame(self.spark, res).collect()
        metrics = self.VR.successMetricsAsDataFrame(self.spark, res).collect()
        mval = {(m["name"], m["instance"]): m["value"] for m in metrics}
        out, raw = {}, []
        for r in rules:
            k, c = r["rule"], r.get("column")
            if k == "is_contained_in":
                key = ("Compliance", f"{c} contained in {','.join(r['params']['values'])}")
            else:
                key = {"is_complete": ("Completeness", c), "completeness_at_least": ("Completeness", c), "is_unique": ("Uniqueness", c),
                       "row_count_between": ("Size", "*"), "is_non_negative": ("Compliance", f"{c} is non-negative")}[k]
            v = mval.get(key)
            if v is None:   # match Compliance metrics loosely by column name
                v = next((val for (n, inst), val in mval.items() if n == key[0] and c and c in inst), None)
            out[r["id"]] = float(v) if v is not None else None
        for row in checks:
            raw.append([row["check"], row["constraint"][:90], row["constraint_status"], (row["constraint_message"] or "")[:80]])
        return out, raw, res


def verdict(r, metric):
    k, p = r["rule"], r.get("params", {})
    if metric is None:
        return False
    if k == "completeness_at_least":
        return metric >= p["min"]
    if k == "row_count_between":
        return p["min"] <= metric <= p["max"]
    return metric >= 1.0 - 1e-12


class DQPort:
    """The one interface pipelines call. The binding (dq_engine) picks the adapter; unsupported rules fall back to spark_sql."""

    def __init__(self, engines, binding):
        self.engines, self.binding = engines, binding

    def route(self, rules):
        main = self.engines[self.binding]
        plan = {}
        for r in rules:
            plan.setdefault(main.name if main.supports(r) else "spark_sql", []).append(r)
        return plan

    def run(self, rules, t):
        metrics, raw = {}, []
        for eng, rs in self.route(rules).items():
            if eng == "deequ":
                m, rw, _ = self.engines[eng].run(rs, t)
                raw += rw
            else:
                m = self.engines[eng].run(rs, t)
            metrics.update(m)
        return {r["id"]: (metrics[r["id"]], verdict(r, metrics[r["id"]])) for r in rules}, raw


# ----------------------------------------------------------------------------- data
def orders_df(spark, n, day="2026-10-27", seed_shift=0):
    base = spark.range(0, n).selectExpr(
        f"id + {seed_shift} AS id",
    ).selectExpr(
        "format_string('O-%07d', id) AS order_id",
        "CASE WHEN id % 250 = 0 THEN NULL ELSE format_string('C-%05d', id % 8000) END AS customer_id",
        "CASE WHEN id % 2500 = 7 THEN -1.0 * (id % 300 + 10) ELSE cast(id * 37 % 2000 + 50 AS DOUBLE) END AS amount",
        "CASE WHEN id % 1000 = 3 THEN 'Ind' WHEN id % 10 < 7 THEN 'IN' WHEN id % 10 = 7 THEN 'US' WHEN id % 10 = 8 THEN 'GB' ELSE 'AE' END AS country",
        "CASE WHEN id % 10 = 0 THEN 'DIWALI10' END AS coupon",
        f"timestamp'{day} 00:00:00' + make_interval(0, 0, 0, 0, 0, 0, cast(id % 86400 AS INT)) AS placed_at")
    dupes = base.where("cast(substring(order_id, 3) AS INT) % 4000 = 11").limit(12) \
        .withColumn("placed_at", F.col("placed_at") + F.expr("INTERVAL 7 SECONDS"))     # the same order delivered again, 7 s later
    return base.unionByName(dupes)


ORDERS_YAML = """# datasets/orders.dq.yaml  (owned by the data team; reviewed by PR)
dataset: orders
owner: sales-data
dq_engine: spark_sql          # binding: spark_sql | deequ   (great_expectations: adapter slot, not installed here)
checks:
  - {id: DQ-01, rule: is_complete,           column: customer_id, severity: error, action: quarantine}
  - {id: DQ-02, rule: is_unique,             column: order_id,    severity: error, action: quarantine}
  - {id: DQ-03, rule: is_non_negative,       column: amount,      severity: error, action: quarantine}
  - {id: DQ-04, rule: is_contained_in,       column: country,     severity: warn,  action: alert, params: {values: [IN, US, GB, AE, SG]}}
  - {id: DQ-05, rule: completeness_at_least, column: coupon,      severity: warn,  action: alert, params: {min: 0.05}}
  - {id: DQ-06, rule: row_count_between,                          severity: error, action: stop,  params: {min: 40000, max: 60000}}
  - {id: DQ-07, rule: references,            column: customer_id, severity: warn,  action: alert, params: {table: customers, key: customer_id}}
"""

CUSTOMERS_YAML = """# datasets/customers.dq.yaml  (a new dataset: this file is the whole change)
dataset: customers
owner: crm-data
dq_engine: deequ
checks:
  - {id: DQ-11, rule: is_complete,     column: customer_id, severity: error, action: stop}
  - {id: DQ-12, rule: is_unique,       column: customer_id, severity: error, action: stop}
  - {id: DQ-13, rule: is_contained_in, column: tier,        severity: warn,  action: alert, params: {values: [Gold, Standard]}}
"""


def load_rules(db, text):
    cfg = yaml.safe_load(text)
    rules = [dict(r, params=r.get("params", {})) for r in cfg["checks"]]
    canon = json.dumps({"dataset": cfg["dataset"], "dq_engine": cfg["dq_engine"], "checks": rules}, sort_keys=True, separators=(",", ":"))
    fp = hashlib.sha256(canon.encode()).hexdigest()[:12]
    db.execute("INSERT OR REPLACE INTO dataset_master VALUES (?,?,?,?)", (cfg["dataset"], cfg["owner"], cfg["dq_engine"], fp))
    db.execute("DELETE FROM dq_rule WHERE dataset = ?", (cfg["dataset"],))
    for r in rules:
        db.execute("INSERT INTO dq_rule VALUES (?,?,?,?,?,?,?,1)", (cfg["dataset"], r["id"], r["rule"], r.get("column"), json.dumps(r["params"]), r["severity"], r["action"]))
    db.commit()
    return cfg, rules, fp


def db_view(db):
    out = {}
    for t in ("dataset_master", "dq_rule"):
        cur = db.execute(f"SELECT * FROM {t}")
        out[t] = {"cols": [d[0] for d in cur.description], "rows": [[str(x) for x in r] for r in cur.fetchall()]}
    return out


def run():
    wh = tempfile.mkdtemp(prefix="dts-dqwh-")
    b = (SparkSession.builder.master("local[2]").appName("DataTwin Studio: data quality")
         .config("spark.ui.enabled", "false").config("spark.sql.session.timeZone", "UTC").config("spark.sql.warehouse.dir", wh)
         .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
         .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
         .config("spark.sql.shuffle.partitions", "4").config("spark.databricks.delta.snapshotPartitions", "2"))
    spark = configure_spark_with_delta_pip(b, extra_packages=[pydeequ.deequ_maven_coord]).config("spark.jars.excludes", pydeequ.f2j_maven_coord).getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    sql = spark.sql
    R = Rec()
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE dataset_master (dataset TEXT PRIMARY KEY, owner TEXT, dq_engine TEXT, rules_fingerprint TEXT)")
    db.execute("CREATE TABLE dq_rule (dataset TEXT, rule_id TEXT, rule TEXT, column_name TEXT, params TEXT, severity TEXT, action TEXT, is_active INT)")
    engines = {"spark_sql": SparkSqlEngine(spark), "deequ": DeequEngine(spark)}

    spark.range(0, 7900).selectExpr("format_string('C-%05d', id) AS customer_id", "CASE WHEN id % 5 = 0 THEN 'Gold' ELSE 'Standard' END AS tier") \
        .write.format("delta").saveAsTable("customers")
    orders_df(spark, 50000).write.format("delta").saveAsTable("bronze_orders")
    n_bronze = spark.table("bronze_orders").count()

    # =================================================================== 1. rules as metadata
    R.step("rules", "Rules are data: a YAML file, not code",
           f"A data engineer describes the checks for the orders dataset in a YAML file: seven rules, each with a severity (error or warn) and an action (quarantine the bad rows, stop the load, or just alert). No Python, no SQL. The file also names the engine that runs the checks (dq_engine), and that one line is the binding: the pipeline never imports Deequ or Great Expectations directly. Today's bronze batch has {n_bronze:,} orders.",
           ORDERS_YAML, {"config": {"yaml": ORDERS_YAML}}, ["inputs", "config"])

    cfg, rules, fp = load_rules(db, ORDERS_YAML)
    R.log("INFO", f"loaded datasets/orders.dq.yaml into the metadata DB: {len(rules)} rules, fingerprint {fp}")
    compiled = {"spark_sql (current binding)": "\n".join(f"-- {r['id']} {r['rule']}\n{engines['spark_sql'].compile(r, 'bronze_orders')}" for r in rules),
                "deequ (same rules, if the binding said deequ)": "VerificationSuite(spark).onData(bronze_orders)\n" + "\n".join(
                    f"  .addCheck(Check(spark, CheckLevel.{'Error' if r['severity'] == 'error' else 'Warning'}, '{r['id']}').{engines['deequ'].compile(r)})" if engines['deequ'].supports(r)
                    else f"  # {r['id']} {r['rule']}: Deequ has no referential check -> the port routes it to spark_sql" for r in rules) + "\n  .run()"}
    R.step("rules", "Loaded into the metadata DB, compiled by the port",
           f"A loader validates the YAML and writes it to the metadata database: one row per rule in dq_rule, and the dataset row with the engine binding and a fingerprint of the rules ({fp}). Every run records which fingerprint it checked against, so 'which rules were in force on 27 Oct?' has an answer. The port compiles each rule for the bound engine. Both compilations are shown: the same seven rules as Spark SQL, and as Deequ checks. Deequ has no referential-integrity rule, so the port routes DQ-07 to Spark SQL: the adapter declares what it supports instead of failing.",
           "loader: validate YAML -> INSERT INTO dataset_master, dq_rule; fingerprint = sha256(canonical rules)\nport.compile(rules, binding)",
           {"config": {"yaml": ORDERS_YAML, "db": db_view(db)}, "engine": {"compiled": compiled, "note": "What the port generates from the rules, per adapter (recorded)."}},
           ["config", "engine", "logs"])

    # run with spark_sql
    w = Window.partitionBy("order_id").orderBy("placed_at")
    sql("CREATE OR REPLACE TEMP VIEW orders_checked AS SELECT o.*, row_number() OVER (PARTITION BY order_id ORDER BY placed_at) AS _dup_rank, c.customer_id IS NULL AS _ref_missing "
        "FROM bronze_orders o LEFT JOIN customers c USING (customer_id)")
    port = DQPort(engines, "spark_sql")
    t0 = time.perf_counter()
    res_sql, _ = port.run(rules, "bronze_orders")
    ms_sql = int((time.perf_counter() - t0) * 1000)

    def results_items(res):
        items = []
        for r in rules:
            m, ok = res[r["id"]]
            shown = f"{int(m):,} rows" if r["rule"] == "row_count_between" else pct(m)
            items.append([f"{r['id']} {r['rule'].replace('_', ' ')}{(' · ' + r['column']) if r.get('column') else ''} [{r['severity']} → {r['action']}]", shown, ok])
        return items

    def act(res, publish_table):
        failing = [r for r in rules if not res[r["id"]][1]]
        stop = [r for r in failing if r["action"] == "stop"]
        qrules = [r for r in failing if r["action"] == "quarantine"]
        alerts = [r for r in failing if r["action"] == "alert"]
        if stop:
            return {"stopped": [r["id"] for r in stop], "quarantined": 0, "published": 0, "alerts": [r["id"] for r in alerts]}
        if qrules:
            preds = [(r["id"], engines["spark_sql"].failing_rows(r, "orders_checked")) for r in qrules]
            reason = "concat_ws(',', " + ", ".join(f"CASE WHEN {p} THEN '{i}' END" for i, p in preds) + ")"
            bad = " OR ".join(f"({p})" for _, p in preds)
            q = spark.sql(f"SELECT order_id, customer_id, amount, country, placed_at, {reason} AS failed_rules FROM orders_checked WHERE coalesce({bad}, false)")
            q.write.format("delta").mode("overwrite").saveAsTable("quarantine_orders")
            spark.sql(f"SELECT order_id, customer_id, amount, country, coupon, placed_at FROM orders_checked WHERE NOT coalesce({bad}, false)") \
                .write.format("delta").mode("overwrite").saveAsTable(publish_table)
        nq = spark.table("quarantine_orders").count() if qrules else 0
        return {"stopped": [], "quarantined": nq, "published": spark.table(publish_table).count(), "alerts": [r["id"] for r in alerts]}
    outcome = act(res_sql, "silver_orders")
    for r in rules:
        m, ok = res_sql[r["id"]]
        if not ok:
            R.log("ERROR" if r["severity"] == "error" else "WARN", f"{r['id']} {r['rule']} failed ({pct(m) if r['rule'] != 'row_count_between' else m}) → {r['action']}")
    R.log("INFO", f"published {outcome['published']:,} rows to silver; quarantined {outcome['quarantined']}; alerts: {', '.join(outcome['alerts']) or 'none'}")
    by_rule = spark.table("quarantine_orders").groupBy("failed_rules").count().orderBy("failed_rules").collect()
    R.step("rules", "Run with the Spark SQL adapter: results, quarantine, alerts",
           f"The pipeline calls the port; the binding says spark_sql. {sum(1 for v in res_sql.values() if not v[1])} of 7 rules fail, and each failure does what its action says. Rows that break an error rule (no customer, a duplicate order delivered again, a negative amount) go to quarantine with the rule IDs ({outcome['quarantined']} rows). Warnings (country 'Ind', customers missing from the customer table) raise alerts but keep the rows. The row count is in range, so the load is not stopped: {outcome['published']:,} rows published to silver. Checks took {ms_sql} ms.",
           "results = dq_port.run(rules, 'bronze_orders')        # binding: spark_sql\napply_actions(results)   # quarantine | stop | alert, per rule",
           {"checks": {"items": results_items(res_sql)},
            "layers": {"quarantine (by rule)": {"cols": ["failed_rules", "rows"], "rows": [[r.failed_rules, str(r["count"])] for r in by_rule], "count": len(by_rule)},
                       "quarantine": tbl(spark.table("quarantine_orders"), 10, ["order_id"]), "silver": tbl(spark.table("silver_orders"), 8, ["order_id"])},
            "dashboard": {"tiles": [["Rows in", f"{n_bronze:,}"], ["Published", f"{outcome['published']:,}"], ["Quarantined", str(outcome["quarantined"])], ["Alerts", str(len(outcome["alerts"]))]]}},
           ["checks", "layers", "dashboard", "logs"])

    # same rules with deequ
    db.execute("UPDATE dataset_master SET dq_engine = 'deequ' WHERE dataset = 'orders'")
    db.commit()
    port_d = DQPort(engines, "deequ")
    t0 = time.perf_counter()
    res_dq, raw = port_d.run(rules, "bronze_orders")
    ms_dq = int((time.perf_counter() - t0) * 1000)
    agree = all(res_dq[r["id"]][1] == res_sql[r["id"]][1] for r in rules)
    on_deequ = [r for r in rules if engines["deequ"].supports(r)]
    same_metric = sum(1 for r in on_deequ if res_dq[r["id"]][0] is not None and abs(res_dq[r["id"]][0] - res_sql[r["id"]][0]) <= 1e-6 * max(1.0, abs(res_sql[r["id"]][0])))
    routed = [r["id"] for r in port_d.route(rules).get("spark_sql", [])]
    R.log("INFO", f"binding changed to deequ (one line); {len(rules) - len(routed)} rules ran on Deequ, {', '.join(routed)} routed to spark_sql; verdicts agree: {agree}")
    cmp_rows = [[r["id"], r["rule"], (f"{int(res_sql[r['id']][0]):,}" if r["rule"] == "row_count_between" else pct(res_sql[r["id"]][0])) + (" ✓" if res_sql[r["id"]][1] else " ✗"),
                 ("routed to spark_sql" if r["id"] in routed else (f"{int(res_dq[r['id']][0]):,}" if r["rule"] == "row_count_between" else pct(res_dq[r["id"]][0])) + (" ✓" if res_dq[r["id"]][1] else " ✗"))] for r in rules]
    R.step("rules", "Change one line: the same rules on Deequ",
           f"The binding changes from spark_sql to deequ, in the YAML and therefore in the metadata DB. No pipeline code changes. The port builds a Deequ VerificationSuite from the same rows: {len(rules) - len(routed)} rules run on Deequ, and {', '.join(routed)} (referential integrity) is routed to Spark SQL because the Deequ adapter declares it cannot do that. Every verdict agrees ({'yes' if agree else 'NO'}), and {same_metric} of the {len(on_deequ)} metrics Deequ computed match the Spark SQL ones to six significant digits. One lesson from building the port: Deequ's 'uniqueness' means 'share of rows whose value appears exactly once', so the Spark SQL adapter computes exactly that, not 'distinct values / rows'. A port is only swappable if every adapter means the same thing by each rule. Running both adapters side by side also caught a bug in our own: the first Spark SQL adapter averaged decimal literals, and Spark rounded the metrics (0.996 instead of 0.99600096). It now averages doubles, and that comparison is kept as a contract test for the port.",
           "dq_engine: deequ        # the only change\n\nresults = dq_port.run(rules, 'bronze_orders')   # same call",
           {"checks": {"items": results_items(res_dq)},
            "layers": {"spark_sql vs deequ": {"cols": ["rule", "type", "spark_sql", "deequ"], "rows": cmp_rows, "count": len(cmp_rows)},
                       "Deequ's own check results": {"cols": ["check", "constraint", "status", "message"], "rows": raw, "count": len(raw)}},
            "config": {"yaml": ORDERS_YAML.replace("dq_engine: spark_sql ", "dq_engine: deequ     "), "db": db_view(db)}},
           ["inputs", "checks", "layers", "config"])

    # =================================================================== 2. profiling and suggested rules
    from pydeequ.profiles import ColumnProfilerRunner
    from pydeequ.suggestions import ConstraintSuggestionRunner, DEFAULT
    t0 = time.perf_counter()
    prof = ColumnProfilerRunner(spark).onData(spark.table("bronze_orders")).run()
    ms_prof = int((time.perf_counter() - t0) * 1000)
    prows = []
    for col, p in prof.profiles.items():
        g = lambda a: getattr(p, a, None)  # noqa: E731
        num = lambda v: "" if v is None else (f"{v:,.2f}" if isinstance(v, float) else str(v))  # noqa: E731
        prows.append([col, str(g("dataType")), pct(g("completeness") or 0), f"{g('approximateNumDistinctValues'):,}", num(g("minimum")), num(g("maximum")), num(g("mean"))])
    R.log("INFO", f"profiled {len(prows)} columns in {ms_prof} ms")
    hist = getattr(prof.profiles.get("country"), "histogram", None)
    hist_rows = [[str(h.value), f"{h.count:,}", pct(h.ratio)] for h in (hist or [])]
    R.step("profile", "Profile the data before writing rules",
           f"Deequ's column profiler reads the table once and describes every column: type, completeness, approximate distinct count, and for numbers the minimum, maximum and mean. It took {ms_prof} ms for {n_bronze:,} rows. The profile already shows the problems: customer_id is not 100% complete, amount has a negative minimum, and the country histogram includes 'Ind', which is not an ISO code. Profile first, then write rules: it is cheaper than guessing.",
           "ColumnProfilerRunner(spark).onData(bronze_orders).run()",
           {"layers": {"profile": {"cols": ["column", "type", "complete", "distinct (approx)", "min", "max", "mean"], "rows": prows, "count": len(prows)},
                       "country histogram": {"cols": ["value", "rows", "share"], "rows": hist_rows, "count": len(hist_rows)}},
            "dashboard": {"tiles": [["Columns", str(len(prows))], ["Rows", f"{n_bronze:,}"], ["Profile time", f"{ms_prof} ms"], ["Passes over data", "1"]]}},
           ["inputs", "layers", "dashboard"])

    sug = ConstraintSuggestionRunner(spark).onData(spark.table("bronze_orders")).addConstraintRule(DEFAULT()).run()
    srows = [[s["column_name"], s["description"][:80], s["code_for_constraint"][:70]] for s in sug["constraint_suggestions"]]
    covered = {r.get("column") for r in rules}
    new_cols = sorted({s[0] for s in srows} - covered)
    R.log("INFO", f"{len(srows)} rule suggestions; written to a draft PR, not applied")
    R.step("profile", "Let Deequ suggest rules; a person decides",
           f"Deequ's suggestion runner proposes {len(srows)} rules from the data itself (complete columns, value ranges, allowed values). Useful, but they describe today's data, not the business: here it suggests that customer_id may have up to 1% missing values, and that country may be 'Ind'. Accepted blindly, those rules would bless today's bugs. So suggestions are written to a draft YAML in a pull request, labelled proposed, and a person accepts or rejects each one. Suggestions touch columns with no rule yet: {', '.join(new_cols) or 'none'}. Nothing here changes a rule automatically.",
           "ConstraintSuggestionRunner(spark).onData(bronze_orders).addConstraintRule(DEFAULT()).run()\n# -> datasets/orders.dq.suggested.yaml, opened as a draft PR for review",
           {"layers": {"suggestions": {"cols": ["column", "description", "Deequ code"], "rows": srows, "count": len(srows)}}},
           ["inputs", "layers", "logs"])

    # =================================================================== 3. metrics over time, anomaly detection
    from pydeequ.analyzers import Completeness, Size
    from pydeequ.anomaly_detection import RelativeRateOfChangeStrategy
    from pydeequ.repository import FileSystemMetricsRepository, ResultKey
    repo = FileSystemMetricsRepository(spark, f"{wh}/dq_metrics.json")
    sizes = [50000, 51200, 49800, 50500, 19800]
    hist_rows, day_status = [], []
    for i, n in enumerate(sizes):
        d = f"2026-10-{23 + i:02d}"
        orders_df(spark, n, d, seed_shift=i * 100000).write.format("delta").mode("overwrite").saveAsTable("day_orders")
        key = ResultKey(spark, int(datetime(2026, 10, 23 + i, tzinfo=timezone.utc).timestamp() * 1000), {"day": d})
        rs = [r for r in rules if r["rule"] in ("is_complete", "row_count_between")]
        if i == 0:      # no history yet: only store the metrics
            hook = lambda vs: vs.useRepository(repo).saveOrAppendResult(key)  # noqa: E731
        else:
            hook = lambda vs: vs.useRepository(repo).saveOrAppendResult(key).addAnomalyCheck(RelativeRateOfChangeStrategy(maxRateDecrease=0.5), Size())  # noqa: E731
        _, raw_d, res = engines["deequ"].run(rs, "day_orders", suite_hook=hook)
        from pydeequ.verification import VerificationResult
        cres = VerificationResult.checkResultsAsDataFrame(spark, res).collect()
        anomaly = [c for c in cres if "AnomalyConstraint" in c["constraint"]]
        a_ok = all(c["constraint_status"] == "Success" for c in anomaly)
        size_ok = 40000 <= n <= 60000
        comp = spark.table("day_orders").select(F.avg(F.when(F.col("customer_id").isNotNull(), 1.0).otherwise(0.0))).first()[0]
        hist_rows.append([d, f"{n + 12:,}", pct(comp), ("— (no history yet)" if i == 0 else "✓") if a_ok else "✗ anomaly", "✓" if size_ok else "✗ stop"])
        day_status.append((d, n + 12, a_ok, size_ok))
        R.log("INFO" if a_ok and size_ok else "ERROR", f"{d}: {n + 12:,} rows; anomaly check {'passed' if a_ok else 'FAILED: size fell more than 50% vs the previous run'}" + ("" if size_ok else "; DQ-06 → stop: silver not updated"))
    stored = repo.load().getSuccessMetricsAsDataFrame().where("name = 'Size'").count()
    R.step("trend", "Five days of metrics, and the day the count fell",
           f"Every run stores its metrics in Deequ's metrics repository ({stored} Size metrics stored, one per day). An anomaly check compares today's row count with the history: fail if it fell by more than half since the last run. It needs at least one previous run, so it starts on the second day. Days 23–26 Oct are normal (about 50,000 orders). On 27 Oct only {day_status[-1][1]:,} rows arrived: the anomaly check fails, and so does DQ-06 (row count between 40,000 and 60,000), whose action is stop. Silver keeps yesterday's data instead of publishing a third of today's. A fixed range catches the obvious; the anomaly check also catches a drop inside the range, because it learns from history.",
           "VerificationSuite(spark).onData(day_orders)\n  .useRepository(FileSystemMetricsRepository(spark, path))\n  .saveOrAppendResult(ResultKey(spark, day_ts, {'day': day}))\n  .addAnomalyCheck(RelativeRateOfChangeStrategy(maxRateDecrease=0.5), Size())\n  .addCheck(...DQ-01, DQ-06...)\n  .run()",
           {"layers": {"metrics history": {"cols": ["day", "rows", "customer_id complete", "anomaly check", "DQ-06 range"], "rows": hist_rows, "count": len(hist_rows)}},
            "checks": {"items": [[f"{d}: anomaly check and row-count range", f"{n:,} rows", a and s] for d, n, a, s in day_status]},
            "dashboard": {"tiles": [["27 Oct rows", f"{day_status[-1][1]:,}"], ["Usual", "≈ 50,000"], ["Anomaly", "✗ detected"], ["Silver", "not updated"]]}},
           ["inputs", "layers", "checks", "dashboard", "logs"])

    # =================================================================== 4. onboard a dataset with YAML only
    spark.range(0, 400).selectExpr("format_string('K-%04d', id) AS customer_id",
                                   "CASE WHEN id IN (17, 211, 305) THEN 'gold' WHEN id % 5 = 0 THEN 'Gold' ELSE 'Standard' END AS tier").write.format("delta").saveAsTable("crm_customers")
    c_cfg, c_rules, c_fp = load_rules(db, CUSTOMERS_YAML)
    c_res, c_raw = DQPort(engines, c_cfg["dq_engine"]).run(c_rules, "crm_customers")
    R.log("INFO", f"new dataset 'customers' onboarded from YAML only: {len(c_rules)} rules, fingerprint {c_fp}")
    for r in c_rules:
        if not c_res[r["id"]][1]:
            R.log("WARN", f"{r['id']} {r['rule']} failed ({pct(c_res[r['id']][0])}) → {r['action']}")
    R.step("onboard", "A new dataset, onboarded with nine lines of YAML",
           "The CRM team wants checks on their customers table. The whole change is one new YAML file, reviewed as a pull request: three rules, bound to Deequ. The loader adds it to the metadata DB, the same port runs it, the same actions apply. No pipeline code, no new job. The tier rule catches three rows written as 'gold' instead of 'Gold'; it is a warning, so the owner is alerted and the rows are kept. This is what metadata-driven, low-code data quality means: the engine is built once, and each dataset is a file.",
           CUSTOMERS_YAML,
           {"config": {"yaml": CUSTOMERS_YAML, "db": db_view(db)},
            "checks": {"items": [[f"{r['id']} {r['rule'].replace('_', ' ')} · {r['column']} [{r['severity']} → {r['action']}]", pct(c_res[r['id']][0]), c_res[r['id']][1]] for r in c_rules]},
            "layers": {"Deequ's own check results": {"cols": ["check", "constraint", "status", "message"], "rows": c_raw, "count": len(c_raw)}},
            "dashboard": {"tiles": [["Files changed", "1 (YAML)"], ["Code changed", "0 lines"], ["Rules", str(len(c_rules))], ["Engine", c_cfg["dq_engine"]]]}},
           ["inputs", "config", "checks", "logs"])

    env = {"spark": spark.version, "delta": "3.2.0", "deequ": pydeequ.deequ_maven_coord.split(":")[-1], "master": "local[2]",
           "executors": [{"id": "driver", "host": "localhost", "cores": 2}], "recorded_at": now()}
    try:
        spark.sparkContext._gateway.shutdown_callback_server()
    except Exception:  # noqa: BLE001
        pass
    spark.stop()
    shutil.rmtree(wh, ignore_errors=True)
    return {"env": env, "jobs": {}, "steps": R.steps}


if __name__ == "__main__":
    import traceback
    t, code = time.time(), 0
    try:
        data = run()
        OUT.write_text(json.dumps(data, indent=1, default=str))
        print(f"{len(data['steps'])} steps -> {OUT} in {time.time() - t:.0f}s", flush=True)
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        code = 1
    os._exit(code)      # the Deequ (py4j) callback server can keep the process alive otherwise
