"""Shared helpers for the local Delta/Spark lab: capped-memory session, stage and scan metrics from the Spark UI REST API."""
import json, os, sys, time, urllib.request, shutil
os.environ.pop("SPARK_HOME", None)
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
from pyspark.sql import SparkSession, functions as F
from delta import configure_spark_with_delta_pip

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, os.environ.get("LABDIR", "data"))

def session(name="lab", cores=2, mem="1g", aqe=True, shuffle=4):
    b = (SparkSession.builder.appName(name).master(f"local[{cores}]")
         .config("spark.driver.memory", mem).config("spark.ui.enabled", "true").config("spark.ui.port", "4050")
         .config("spark.sql.shuffle.partitions", str(shuffle)).config("spark.sql.adaptive.enabled", str(aqe).lower())
         .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
         .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
         .config("spark.databricks.delta.snapshotPartitions", "2").config("spark.ui.showConsoleProgress", "false")
         .config("spark.sql.warehouse.dir", os.path.join(DATA, "wh")))
    s = configure_spark_with_delta_pip(b).getOrCreate()
    s.sparkContext.setLogLevel("ERROR")
    return s

def _get(spark, path):
    port = spark.sparkContext.uiWebUrl.rsplit(":", 1)[1]
    return json.load(urllib.request.urlopen(f"http://localhost:{port}/api/v1{path}", timeout=10))

def app_id(spark): return spark.sparkContext.applicationId

def stage_totals(spark, since):
    time.sleep(0.8)
    st = [s for s in _get(spark, f"/applications/{app_id(spark)}/stages?status=complete") if s["stageId"] > since]
    return {"stages": len(st), "tasks": sum(s["numCompleteTasks"] for s in st), "input_bytes": sum(s["inputBytes"] for s in st),
            "shuffle_write_bytes": sum(s["shuffleWriteBytes"] for s in st), "shuffle_read_bytes": sum(s["shuffleReadBytes"] for s in st)}

def last_stage(spark):
    st = _get(spark, f"/applications/{app_id(spark)}/stages?status=complete")
    return max([s["stageId"] for s in st], default=-1)

def scan_metrics(spark, since_exec):
    """metrics of the Parquet scan nodes in SQL executions after since_exec"""
    time.sleep(0.8)
    ex = _get(spark, f"/applications/{app_id(spark)}/sql?details=true&planDescription=false&length=200")
    out = {"files": 0, "file_bytes": 0, "rows": 0, "metadata_ms": 0}
    for e in ex:
        if e["id"] <= since_exec: continue
        for n in e["nodes"]:
            if "Scan" in n["nodeName"] and "parquet" in n["nodeName"].lower():
                for m in n["metrics"]:
                    if m["name"] == "number of files read": out["files"] += int(_first(m["value"])[0])
                    elif m["name"] == "size of files read": out["file_bytes"] += _bytes(m["value"])
                    elif m["name"] == "number of output rows": out["rows"] += int(_first(m["value"])[0])
                    elif m["name"] == "metadata time": out["metadata_ms"] += _ms(m["value"])
    return out

import re
def _first(v):
    """first number and unit of a Spark UI metric value, e.g. '155.3 KiB' or '2.2 s' or '10,000'"""
    t = str(v).strip().splitlines()[-1] if "\n" in str(v) else str(v).strip()
    m = re.match(r"([\d,]+(?:\.\d+)?)\s*(KiB|MiB|GiB|B|ms|s|min)?", t)
    if not m: return 0.0, ""
    return float(m.group(1).replace(",", "")), (m.group(2) or "")

def _bytes(v):
    n, u = _first(v); return int(n * {"": 1, "B": 1, "KiB": 1024, "MiB": 1024**2, "GiB": 1024**3}.get(u, 1))

def _ms(v):
    n, u = _first(v); return n * {"ms": 1, "s": 1000, "min": 60000, "": 1}.get(u, 1)

def last_exec(spark):
    ex = _get(spark, f"/applications/{app_id(spark)}/sql?length=1000")
    return max([e["id"] for e in ex], default=-1)

def run(spark, label, df, sink=True, reps=3):
    """execute a DataFrame to a no-op sink `reps` times; seconds = median, metrics come from the last run only"""
    secs = []
    for i in range(reps):
        s0, e0 = last_stage(spark), last_exec(spark)
        t = time.perf_counter()
        if sink: df.write.format("noop").mode("overwrite").save()
        secs.append(time.perf_counter() - t)
    r = {"label": label, "seconds": round(sorted(secs)[len(secs) // 2], 3), "first_seconds": round(secs[0], 3)}
    r.update(scan_metrics(spark, e0)); r.update(stage_totals(spark, s0))
    return r

def dir_size(path):
    return sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(path) for f in fs if f.endswith(".parquet"))

def n_parquet(path):
    return sum(1 for d, _, fs in os.walk(path) for f in fs if f.endswith(".parquet"))

def save(name, obj):
    os.makedirs(os.path.join(BASE, "results"), exist_ok=True)
    with open(os.path.join(BASE, "results", name + ".json"), "w") as f: json.dump(obj, f, indent=1, default=str)
