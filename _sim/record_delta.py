"""Record the Delta Lake internals scenes for DataTwin Studio from REAL runs.

    env -u SPARK_HOME ~/CostIntelligence1/.venv/bin/python _sim/record_delta.py

Six scenarios on a small orders table, local Spark + Delta Lake:
  files    a table is Parquet files plus a log (create, append, append, UPDATE, DELETE)
  versions reading an old version, checkpoints, RESTORE
  writers  two writers at the same time (appends both win; conflicting updates: one fails)
  dv       the same UPDATE with deletion vectors on
  small    300 tiny files, then OPTIMIZE
  vacuum   VACUUM, and why time travel stops working
After every step it records: the command, the table's rows, every Parquet file on disk (live or
only kept for time travel), the _delta_log commits, DESCRIBE HISTORY, and the Spark jobs.
Output: _sim/data/delta.json
"""
import json
import os
import re
import shutil
import sys
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
from delta import configure_spark_with_delta_pip  # noqa: E402
from pyspark.sql import SparkSession  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from record_batch import parse_eventlog  # noqa: E402

OUT = Path(__file__).resolve().parent / "data" / "delta.json"


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Rec:
    def __init__(self, spark):
        self.spark, self.steps, self.logs, self.n, self._lp = spark, [], [], 0, 0

    def sql(self, q):
        return self.spark.sql(q)

    def loc(self, t):
        return Path(self.spark.sql(f"DESCRIBE DETAIL {t}").first()["location"].replace("file:", ""))

    def log(self, level, msg):
        self.logs.append([now()[11:19], level, msg])

    def files(self, t):
        """Replay the log: every Parquet file on disk, when it was added and removed, and whether it is live."""
        self.spark.sparkContext.setJobGroup("inspect", "studio")
        loc = self.loc(t)
        info = {}
        for f in sorted((loc / "_delta_log").glob("*.json")):
            v = int(f.stem)
            acts = [json.loads(l) for l in f.read_text().splitlines()]
            acts.sort(key=lambda a: 0 if "remove" in a else 1)   # a commit may remove and re-add the same path (deletion vectors)
            for a in acts:
                if "add" in a:
                    x = a["add"]
                    st = json.loads(x["stats"]) if x.get("stats") else {}
                    key = x["path"]
                    dv = x.get("deletionVector")
                    info.setdefault(key, {"added": v, "removed": None, "size": x.get("size"), "rows": st.get("numRecords")})
                    info[key]["removed"] = None
                    info[key]["dv"] = f"{dv.get('cardinality')} row(s) marked deleted" if dv else ""
                if "remove" in a:
                    key = a["remove"]["path"]
                    if key in info and info[key]["removed"] is None:
                        info[key]["removed"] = v
        on_disk = {str(p.relative_to(loc)) for p in loc.rglob("*.parquet") if "_delta_log" not in str(p)}
        rows = []
        for path in sorted(set(info) | on_disk, key=lambda p: (info.get(p, {}).get("added", 99), p)):
            i = info.get(path, {})
            live = path in info and i.get("removed") is None
            if path not in info:
                state = "orphan: never committed"
            else:
                state = "live" if live else ("removed (kept for time travel)" if path in on_disk else "deleted by VACUUM")
            rows.append([path.split("/")[-1][:16] + "…", str(i.get("size", "")), str(i.get("rows", "")), str(i.get("added", "")),
                         "" if i.get("removed") is None else str(i.get("removed")), state + (f" · {i['dv']}" if i.get("dv") else "")])
        live_n = sum(1 for r in rows if r[5].startswith("live"))
        return {"cols": ["file", "bytes", "rows", "added in v", "removed in v", "state"], "rows": rows,
                "summary": f"{len(on_disk)} Parquet file(s) on disk · {live_n} live in the current version"}

    def deltalog(self, t):
        loc = self.loc(t)
        commits = []
        for f in sorted((loc / "_delta_log").glob("*.json")):
            acts = []
            for line in f.read_text().splitlines():
                a = json.loads(line)
                k = next(iter(a))
                v = a[k]
                if k == "commitInfo":
                    acts.append({"commitInfo": {"operation": v.get("operation"), "operationParameters": v.get("operationParameters"),
                                                "operationMetrics": v.get("operationMetrics", {}), "readVersion": v.get("readVersion"), "isBlindAppend": v.get("isBlindAppend")}})
                elif k in ("add", "remove"):
                    st = json.loads(v["stats"]) if v.get("stats") else None
                    d = {"path": "…" + v["path"][-30:], "size": v.get("size"), "dataChange": v.get("dataChange")}
                    if st:
                        d["stats"] = st
                    if v.get("deletionVector"):
                        d["deletionVector"] = {kk: v["deletionVector"].get(kk) for kk in ("storageType", "cardinality", "sizeInBytes")}
                    acts.append({k: d})
                elif k == "metaData":
                    acts.append({"metaData": {"schema": [x["name"] + ":" + str(x["type"]) for x in json.loads(v["schemaString"])["fields"]],
                                              "partitionColumns": v.get("partitionColumns"), "configuration": v.get("configuration")}})
                else:
                    acts.append({k: v})
            commits.append({"file": f.name, "actions": acts})
        extra = sorted(p.name for p in (loc / "_delta_log").iterdir() if not p.name.endswith(".json") and not p.name.startswith("."))
        last = (loc / "_delta_log" / "_last_checkpoint")
        return {"table": t, "data_files": None, "commits": commits, "other_files": extra,
                "last_checkpoint": json.loads(last.read_text()) if last.exists() else None}

    def last(self, t):
        """Adds, removes and rows touched by the latest commit, read from the log itself."""
        loc = self.loc(t)
        f = sorted((loc / "_delta_log").glob("*.json"))[-1]
        acts = [json.loads(l) for l in f.read_text().splitlines()]
        adds = [a["add"] for a in acts if "add" in a]
        rems = [a["remove"] for a in acts if "remove" in a]
        same_paths = {a["path"] for a in adds} & {r["path"] for r in rems}
        rows_added = sum(json.loads(a["stats"])["numRecords"] for a in adds if a.get("stats") and a["path"] not in same_paths)
        same = len(same_paths)
        return {"version": int(f.stem), "adds": len(adds), "removes": len(rems), "rows_written": rows_added, "same_path": same,
                "bytes_written": sum(a.get("size", 0) for a in adds)}

    def history(self, t):
        h = self.sql(f"DESCRIBE HISTORY {t}").select("version", "operation", "operationMetrics").orderBy("version").collect()
        keep = ("numOutputRows", "numFiles", "numAddedFiles", "numRemovedFiles", "numUpdatedRows", "numDeletedRows", "numCopiedRows",
                "numDeletionVectorsAdded", "numFilesAdded", "numFilesRemoved", "numRestoredFiles", "numRemovedBytes", "numAddedBytes")
        return {"cols": ["version", "operation", "metrics"], "rows": [[str(r.version), r.operation, ", ".join(f"{k}={v}" for k, v in (r.operationMetrics or {}).items() if k in keep)] for r in h]}

    def rows(self, t, version=None):
        self.spark.sparkContext.setJobGroup("inspect", "studio")
        df = self.sql(f"SELECT * FROM {t}" + (f" VERSION AS OF {version}" if version is not None else ""))
        df = df.orderBy(df.columns[0])
        r = df.limit(15).collect()
        return {"cols": df.columns, "rows": [[None if x is None else str(x) for x in row] for row in r], "count": df.count()}

    def snap(self, t, extra_layers=None, history=True):
        layers = {"current version": self.rows(t)}
        layers.update(extra_layers or {})
        out = {"layers": layers, "files": self.files(t), "storage": {t: self.deltalog(t)}}
        if history:
            out["engine"] = {"history": self.history(t)}
        return out

    def step(self, scenario, title, plain, command, panels, group=None, focus=None):
        self.n += 1
        self.steps.append({"n": self.n, "scenario": scenario, "title": title, "plain": plain, "focus": focus or ["inputs", "files", "storage"],
                           "code": "", "group": group, "panels": {"inputs": {"user": "", "file": "", "text": command}, **panels},
                           "logs": self.logs[self._lp:], "run_log": []})
        self._lp = len(self.logs)


def run():
    wh, evdir = tempfile.mkdtemp(prefix="dts-dwh-"), tempfile.mkdtemp(prefix="dts-dev-")
    b = (SparkSession.builder.master("local[2]").appName("DataTwin Studio: Delta internals")
         .config("spark.sql.warehouse.dir", wh).config("spark.eventLog.enabled", "true").config("spark.eventLog.dir", evdir)
         .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
         .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
         .config("spark.sql.shuffle.partitions", "2").config("spark.ui.enabled", "false").config("spark.sql.session.timeZone", "UTC")
         .config("spark.databricks.delta.properties.defaults.enableDeletionVectors", "false"))
    spark = configure_spark_with_delta_pip(b).getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    R = Rec(spark)
    sc = spark.sparkContext
    T = "shop.orders"
    R.sql("CREATE DATABASE shop")

    def g(sid, desc):
        sc.setJobGroup(sid, desc)
        return sid

    # ------------------------------------------------------------- files: a table is files plus a log
    q = "CREATE TABLE shop.orders (order_id INT, customer STRING, status STRING, amount_inr DECIMAL(10,2)) USING delta"
    gid = g("files-1", "create")
    R.sql(q)
    R.log("INFO", "table created: version 0")
    R.step("files", "CREATE TABLE: a folder and a log, no data", "Creating a Delta table writes no data at all. It writes the first commit, _delta_log/00000000000000000000.json, holding the protocol version and the metaData (schema, partition columns, settings). The table is empty because no 'add' action has named any file yet.",
           q, R.snap(T), gid)
    q = "INSERT INTO shop.orders VALUES (1001,'C-77','paid',1250.00), (1002,'C-80','paid',400.00), (1003,'C-81','placed',990.00)"
    gid = g("files-2", "insert 1")
    R.sql(q)
    R.log("INFO", "insert: version 1, 3 rows")
    L = R.last(T)
    R.step("files", "INSERT: Parquet files first, then one commit", f"The rows are written into Parquet files first: {L['adds']} of them, because this Spark ran {L['adds']} tasks and each task writes its own file. Then commit {L['version']} is written with one 'add' per file, carrying its size and statistics (row count, min and max of every column). Until that commit file exists, nobody can see the rows: the commit is the moment the data appears.",
           q, R.snap(T), gid)
    q = "INSERT INTO shop.orders VALUES (1004,'C-90','placed',150.00), (1005,'C-77','paid',2200.00)"
    gid = g("files-3", "insert 2")
    R.sql(q)
    R.log("INFO", "insert: version 2, 2 rows")
    L = R.last(T)
    R.step("files", "Another INSERT: the table is the sum of live files", f"Commit {L['version']} adds {L['adds']} more file(s). The table you query is simply every file that has been added and not yet removed. Count the live files in the files panel; together they hold five rows.",
           q, R.snap(T), gid)
    q = "UPDATE shop.orders SET status = 'paid' WHERE order_id = 1003"
    gid = g("files-4", "update")
    R.sql(q)
    R.log("INFO", "update: version 3")
    L = R.last(T)
    R.step("files", "UPDATE one row: the whole file is rewritten", f"Parquet files are never edited. To change one row, Delta reads the file that holds it and writes a new file with every row of the old one, one of them changed. Commit {L['version']}: {L['removes']} remove, {L['adds']} add, {L['rows_written']} row(s) written to change 1. The old file stays on disk for time travel. That is copy-on-write.",
           q, R.snap(T), gid)
    q = "DELETE FROM shop.orders WHERE order_id = 1004"
    gid = g("files-5", "delete")
    R.sql(q)
    R.log("INFO", "delete: version 4")
    L = R.last(T)
    fs = R.files(T)["summary"]
    how = (f"the file holding order 1004 held only that row, so commit {L['version']} just removes it: {L['removes']} remove, no add, nothing rewritten"
           if L["adds"] == 0 else f"commit {L['version']} removes the file holding it and adds a new one with the other {L['rows_written']} row(s)")
    R.step("files", "DELETE one row", f"Deleting also works on whole files: {how}. Files panel: {fs}. The files that are no longer live stay on disk so old versions can still be read.",
           q, R.snap(T), gid)

    # ------------------------------------------------------------- versions: time travel, checkpoints, restore
    q = "SELECT * FROM shop.orders VERSION AS OF 1"
    v1 = R.rows(T, 1)
    R.log("INFO", "time travel: read version 1 by replaying commits 0 and 1")
    R.step("versions", "Read an old version", "To read version 1, Delta replays commits 0 and 1 only: the files they added and did not remove. Those files are still on disk, so yesterday's table comes back exactly, with order 1004 and the old status of 1003.",
           q, {"layers": {"current version": R.rows(T), "version 1": v1}, "files": R.files(T)}, None, ["inputs", "layers", "files"])
    gid = g("versions-2", "many small commits")
    for i in range(6):
        R.sql(f"INSERT INTO shop.orders VALUES ({2000 + i},'C-{100 + i}','placed',{100 + i}.00)")
    R.log("INFO", "6 more inserts: versions 5 to 10; checkpoint written at version 10")
    R.step("versions", "Ten commits later: a checkpoint", "Replaying hundreds of JSON files would get slow, so every 10 commits Delta writes a checkpoint: one Parquet file holding the whole table state at that version, plus _last_checkpoint pointing at it. A reader now starts from the checkpoint and replays only the JSON commits after it.",
           "INSERT INTO shop.orders VALUES (...)   -- six times, versions 5 to 10", R.snap(T), gid, ["inputs", "storage", "files"])
    q = "RESTORE TABLE shop.orders TO VERSION AS OF 2"
    gid = g("versions-3", "restore")
    R.sql(q)
    R.log("INFO", "restore: version 11 = the files of version 2")
    R.step("versions", "RESTORE: going back is a new commit", "RESTORE does not delete history. It writes a new commit (version 11) that removes the files that are live now and re-adds the files that were live in version 2. The table looks like version 2, and you could still restore to version 10.",
           q, R.snap(T), gid)

    # ------------------------------------------------------------- writers: optimistic concurrency
    R.sql("CREATE TABLE shop.w (order_id INT, status STRING) USING delta")
    R.sql("INSERT INTO shop.w VALUES (1,'placed'),(2,'placed'),(3,'placed')")
    results = {}

    def appender(name, rows):
        sc.setJobGroup(f"writers-{name}", name)
        try:
            spark.sql(f"INSERT INTO shop.w VALUES {rows}")
            results[name] = "committed"
        except Exception as e:  # noqa: BLE001
            results[name] = type(e).__name__ + ": " + str(e).split("\n")[0][:200]

    ts = [threading.Thread(target=appender, args=("writer A", "(4,'placed')")), threading.Thread(target=appender, args=("writer B", "(5,'placed')"))]
    [t.start() for t in ts]
    [t.join() for t in ts]
    R.log("INFO", f"two appends at once: A {results['writer A']}, B {results['writer B']}")
    R.step("writers", "Two writers append at the same time: both win", "Both writers read the same version, write their own Parquet file, then race to create the next commit file. Creating a commit file is all-or-nothing: one gets version 2, the other finds it taken, checks that the winner only appended (nothing it read changed), and simply commits as version 3. No locks, no lost rows.",
           "-- at the same moment, in two sessions:\nINSERT INTO shop.w VALUES (4,'placed')   -- writer A\nINSERT INTO shop.w VALUES (5,'placed')   -- writer B",
           R.snap("shop.w"), None, ["inputs", "storage", "logs"])
    conflict = None
    for attempt in range(25):
        res = {}
        bar = threading.Barrier(2)

        def updater(name, status):
            sc.setJobGroup(f"writers-conflict-{name}", name)
            bar.wait()
            try:
                spark.sql(f"UPDATE shop.w SET status = '{status}' WHERE order_id = 1")
                res[name] = "committed"
            except Exception as e:  # noqa: BLE001
                res[name] = type(e).__name__ + ": " + str(e).split("\n")[0][:240]
        ts = [threading.Thread(target=updater, args=("writer A", "paid")), threading.Thread(target=updater, args=("writer B", "cancelled"))]
        [t.start() for t in ts]
        [t.join() for t in ts]
        if any(v != "committed" for v in res.values()):
            conflict = (attempt + 1, res)
            break
    if conflict:
        att, res = conflict
        R.log("INFO", f"conflicting updates (attempt {att}): A {res['writer A'][:80]}")
        R.log("ERROR" if res["writer B"] != "committed" or res["writer A"] != "committed" else "INFO", f"B {res['writer B'][:160]}")
        loser = "writer A" if res["writer A"] != "committed" else "writer B"
        R.step("writers", "Two writers change the same row: one fails", f"This time both writers UPDATE order 1. Each reads the table to find the row (on an unpartitioned table, that read covers every file). The first to commit wins. The other then sees that the winner added a file its own read would have had to include, so its result might be wrong: it fails with ConcurrentAppendException instead of silently overwriting. Recorded: {loser} failed on attempt {att}. Look at the files panel: the loser had already written its Parquet file, which no commit names. It is an orphan: no version will ever read it, and VACUUM deletes it later. The fix is to retry (re-read and re-apply), partition or cluster so writers touch different files, or give each table one writer.",
               "-- at the same moment:\nUPDATE shop.w SET status = 'paid'      WHERE order_id = 1   -- writer A\nUPDATE shop.w SET status = 'cancelled' WHERE order_id = 1   -- writer B",
               {**R.snap("shop.w"), "engine": {"error": f"writer A: {res['writer A']}\nwriter B: {res['writer B']}", "history": R.history("shop.w")}}, None, ["inputs", "engine", "logs", "storage"])
    else:
        R.log("WARN", "no conflict observed in 25 attempts; the two updates happened one after the other")

    # ------------------------------------------------------------- dv: deletion vectors
    R.sql("CREATE TABLE shop.orders_dv (order_id INT, customer STRING, status STRING, amount_inr DECIMAL(10,2)) USING delta TBLPROPERTIES ('delta.enableDeletionVectors' = 'true')")
    R.sql("INSERT INTO shop.orders_dv SELECT id + 5000, concat('C-', id), 'placed', 100.00 FROM range(0, 2000)")
    R.log("INFO", "orders_dv: 2,000 rows in one file, deletion vectors on")
    R.step("dv", "A bigger file, deletion vectors on", "A copy of the table with 2,000 rows in one file, created with delta.enableDeletionVectors = true. Look at the metaData configuration in commit 0.",
           "CREATE TABLE shop.orders_dv (...) TBLPROPERTIES ('delta.enableDeletionVectors' = 'true');\nINSERT INTO shop.orders_dv SELECT ... FROM range(0, 2000)", R.snap("shop.orders_dv"), None, ["inputs", "storage", "files"])
    q = "DELETE FROM shop.orders_dv WHERE order_id = 5007"
    gid = g("dv-2", "delete with dv")
    t0 = time.time()
    R.sql(q)
    ms = int((time.time() - t0) * 1000)
    R.log("INFO", f"delete with deletion vectors: {ms} ms")
    L = R.last("shop.orders_dv")
    R.step("dv", "DELETE one row: nothing rewritten", f"With deletion vectors, Delta does not rewrite the file holding order 5007 (about a thousand rows). It writes a tiny deletion vector saying 'this row of this file is deleted', and commits a remove and re-add of the same file with the vector attached ({L['same_path']} file re-added with a vector attached, {L['rows_written']} rows of new data written). Readers skip the marked row. Took {ms} ms here. Compare with the copy-on-write UPDATE in the first scenario.",
           q, R.snap("shop.orders_dv"), gid)
    q = "UPDATE shop.orders_dv SET status = 'paid' WHERE order_id = 5010"
    gid = g("dv-3", "update with dv")
    R.sql(q)
    R.log("INFO", "update with deletion vectors: old row marked deleted, new row in a small new file")
    R.step("dv", "UPDATE one row: mark the old, write the new", "An UPDATE becomes 'mark the old row deleted' plus 'write the new row into a small new file'. Fast writes; the cost moves to reads, which must apply the vectors, until OPTIMIZE (or a purge) rewrites the file cleanly.",
           q, R.snap("shop.orders_dv"), gid)

    # ------------------------------------------------------------- small: small files and OPTIMIZE
    R.sql("CREATE TABLE shop.events (event_id BIGINT, customer STRING, amount DOUBLE) USING delta")
    gid = g("small-1", "write 300 small files")
    spark.range(0, 300000).selectExpr("id AS event_id", "concat('C-', id % 1000) AS customer", "rand() * 1000 AS amount").repartition(300).write.format("delta").mode("append").saveAsTable("shop.events")
    for _ in range(2):
        spark.sql("SELECT count(*), sum(amount) FROM shop.events WHERE customer = 'C-7'").collect()  # warm up
    t0 = time.time()
    spark.sparkContext.setJobGroup("small-query-before", "query before")
    before = spark.sql("SELECT count(*) AS n, round(sum(amount), 2) AS total FROM shop.events WHERE customer = 'C-7'").first()
    q_before = int((time.time() - t0) * 1000)
    R.log("INFO", f"300 files: query took {q_before} ms")
    snap = R.snap("shop.events", history=True)
    R.step("small", "300 tiny files", f"300,000 events written as 300 small files (about a thousand rows each), the way streaming or many small batches leave a table. A query for one customer has to list, open and read every file: it took {q_before} ms on this laptop.",
           "spark.range(0, 300000)...repartition(300).write.format('delta').saveAsTable('shop.events')\nSELECT count(*), sum(amount) FROM shop.events WHERE customer = 'C-7'",
           {**snap, "layers": {"query result": {"cols": ["n", "total"], "rows": [[str(before.n), str(before.total)]], "count": 1}}}, "small-query-before", ["inputs", "files", "cluster"])
    q = "OPTIMIZE shop.events"
    gid = g("small-2", "optimize")
    t0 = time.time()
    opt = R.sql(q).first()
    opt_ms = int((time.time() - t0) * 1000)
    R.log("INFO", f"optimize: {opt_ms} ms")
    for _ in range(2):
        spark.sql("SELECT count(*), sum(amount) FROM shop.events WHERE customer = 'C-7'").collect()
    t0 = time.time()
    spark.sparkContext.setJobGroup("small-query-after", "query after")
    after = spark.sql("SELECT count(*) AS n, round(sum(amount), 2) AS total FROM shop.events WHERE customer = 'C-7'").first()
    q_after = int((time.time() - t0) * 1000)
    R.log("INFO", f"after OPTIMIZE: query took {q_after} ms (was {q_before} ms)")
    snap = R.snap("shop.events")
    R.step("small", "OPTIMIZE: compact into a few big files", f"OPTIMIZE reads the small files and writes a few large ones, then commits one 'remove' for each small file and an 'add' for each new one. Same rows, same answer. The same query now took {q_after} ms instead of {q_before} ms. The 300 old files stay on disk until VACUUM.",
           q, {**snap, "layers": {"query result": {"cols": ["n", "total"], "rows": [[str(after.n), str(after.total)]], "count": 1}},
               "engine": {"history": R.history("shop.events"), "metrics": {"before_ms": q_before, "after_ms": q_after, "optimize_ms": opt_ms}}}, "small-query-after", ["inputs", "files", "storage", "engine"])

    # ------------------------------------------------------------- vacuum
    R.sql("SET spark.databricks.delta.retentionDurationCheck.enabled = false")
    q = "VACUUM shop.orders RETAIN 0 HOURS"   # version 4's files are not live any more (RESTORE re-used version 2's)
    on_disk_before = R.files(T)["summary"]
    gid = g("vacuum-1", "vacuum")
    R.sql(q)
    R.log("WARN", "vacuum with 0 hours retention (the safety check had to be switched off first)")
    R.step("vacuum", "VACUUM: delete files no version needs now", f"VACUUM deletes Parquet files that are no longer live and are older than the retention period (7 days by default). Here the retention was set to 0 hours, which Delta refuses unless a safety check is switched off. Before: {on_disk_before}. Now only live files remain on disk.",
           "SET spark.databricks.delta.retentionDurationCheck.enabled = false;   -- never do this in production\n" + q, R.snap(T), gid)
    try:
        R.sql("SELECT * FROM shop.orders VERSION AS OF 4").collect()
        err = "time travel still worked"
    except Exception as e:  # noqa: BLE001
        full = str(e)
        hits = [l.strip() for l in full.splitlines() if "FileNotFound" in l or "DELTA_" in l or "does not exist" in l]
        err = (hits[0] if hits else full.splitlines()[0])[:400]
        m = re.search(r"SparkFileNotFoundException: File \S+?/orders/((part-\S+?)\.parquet)", full)
        if m:
            err = "SparkFileNotFoundException: File …/shop.db/orders/" + m.group(2)[:44] + "… does not exist (VACUUM deleted it)"
    R.log("ERROR", "time travel to version 4 failed: " + err[:160])
    R.step("vacuum", "Time travel after VACUUM: the files are gone", "The log still lists version 4, but the files it needs were deleted. Reading it fails. (Version 1 would still work: RESTORE made its files live again, so VACUUM kept them.) That is why the default retention is 7 days and the safety check exists: VACUUM sets how far back you can travel, and long-running readers or streams may still need older files.",
           "SELECT * FROM shop.orders VERSION AS OF 4", {"files": R.files(T), "engine": {"error": err}}, None, ["inputs", "engine", "files", "logs"])

    groups, execs = parse_eventlog(evdir)
    env = {"spark": spark.version, "delta": "3.2.0", "master": "local[2]", "executors": execs, "recorded_at": now()}
    spark.stop()
    shutil.rmtree(wh, ignore_errors=True)
    shutil.rmtree(evdir, ignore_errors=True)
    return {"env": env, "jobs": groups, "steps": R.steps}


if __name__ == "__main__":
    t = time.time()
    data = run()
    OUT.write_text(json.dumps(data, indent=1, default=str))
    print(f"{len(data['steps'])} steps -> {OUT} in {time.time() - t:.0f}s")
