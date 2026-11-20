"""Run every table-maintenance command on a real local Delta table and record what happened.

    unset SPARK_HOME; /Users/ishaan/CostIntelligence1/.venv/bin/python run.py <scratch_dir>

Spark 3.5.1 + Delta 3.2.0 (open source). Databricks adds Photon, Predictive Optimization and a few
defaults, so file sizes and thresholds differ there; the behaviour shown is the same idea.
Writes results.json next to this file. Each step is wrapped so a failure is recorded, not hidden.
"""
import json
import os
import shutil
import sys
from pathlib import Path

os.environ.pop("SPARK_HOME", None)
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
from delta import configure_spark_with_delta_pip  # noqa: E402
from pyspark.sql import SparkSession  # noqa: E402

SCRATCH = Path(sys.argv[1])
shutil.rmtree(SCRATCH, ignore_errors=True)
SCRATCH.mkdir(parents=True)
OUT = Path(__file__).parent / "results.json"
R = {"engine": "Apache Spark 3.5.1 + Delta Lake 3.2.0 (open source), local[4]"}

b = (SparkSession.builder.master("local[4]").appName("tm")
     .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
     .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
     .config("spark.ui.enabled", "false").config("spark.sql.warehouse.dir", str(SCRATCH / "wh")).config("spark.sql.shuffle.partitions", "4")
     .config("spark.sql.adaptive.enabled", "false").config("spark.databricks.delta.snapshotPartitions", "2"))
spark = configure_spark_with_delta_pip(b).getOrCreate()
spark.sparkContext.setLogLevel("ERROR")


def disk_files(path):
    return sum(1 for p in Path(path).glob("*.parquet"))


def detail(path):
    d = spark.sql(f"DESCRIBE DETAIL delta.`{path}`").collect()[0]
    return {"files_in_table": int(d["numFiles"]), "size_kb": round(d["sizeInBytes"] / 1024), "files_on_disk": disk_files(path)}


def hist(path, n=1):
    rows = spark.sql(f"DESCRIBE HISTORY delta.`{path}`").select("version", "operation", "operationMetrics").limit(n).collect()
    return [{"version": r["version"], "operation": r["operation"], "metrics": dict(r["operationMetrics"])} for r in rows]


def batch(i, n=1500):
    return (spark.range(i * n, (i + 1) * n).selectExpr(
        "id as order_id", "pmod(hash(id), 1000) as customer_id",
        "element_at(array('IN','US','UK','DE','FR','AU','SG','AE','JP','BR'), cast(pmod(hash(id,1), 10) + 1 as int)) as country",
        "round(pmod(hash(id,2), 50000) / 100.0, 2) as amount",
        "date_add(date'2026-01-01', cast(pmod(hash(id,3), 30) as int)) as order_date").coalesce(1))


def files_read(df):
    """Run the query, then read the scan node's 'number of files read' metric."""
    df.collect()
    plan = df._jdf.queryExecution().executedPlan()
    leaves = plan.collectLeaves()
    for i in range(leaves.size()):
        m = leaves.apply(i).metrics()
        if m.contains("numFiles"):
            return int(m.apply("numFiles").value())
    return None


def why(e):
    """Pick the useful line out of a py4j error (the first line is often just 'An error occurred while calling')."""
    txt = str(e)
    for line in txt.splitlines():
        if any(k in line for k in ("FileNotFound", "No such file", "does not exist", "DELTA_", "AnalysisException", "ParseException", "Exception:")) and "An error occurred" not in line:
            return line.strip()[:260]
    j = getattr(e, "java_exception", None)
    return (str(j.getMessage()).splitlines()[0] if j is not None and j.getMessage() else txt.splitlines()[0])[:260]


def step(name, fn):
    try:
        R[name] = fn()
        R[name]["status"] = "ok"
    except Exception as e:  # noqa: BLE001 - recorded, shown on the page as not run
        R[name] = {"status": "failed", "error": why(e)}
        print("FAILED", name, e)


T = str(SCRATCH / "orders")
N_APPENDS = 200


def s_small_files():
    for i in range(N_APPENDS):
        batch(i).write.format("delta").mode("append").save(T)
    d = detail(T)
    d["appends"] = N_APPENDS
    d["rows"] = spark.read.format("delta").load(T).count()
    d["avg_file_kb"] = round(d["size_kb"] / d["files_in_table"], 1)
    d["version"] = int(spark.sql(f"DESCRIBE HISTORY delta.`{T}`").agg({"version": "max"}).collect()[0][0])
    q = spark.read.format("delta").load(T).filter("customer_id = 42")
    d["files_read_customer_42"] = files_read(q)
    return d


def s_optimize():
    spark.conf.set("spark.databricks.delta.optimize.maxFileSize", str(250 * 1024))
    spark.conf.set("spark.databricks.delta.optimize.minFileSize", str(250 * 1024))
    before = detail(T)
    r = spark.sql(f"OPTIMIZE delta.`{T}`").collect()[0]["metrics"]
    after = detail(T)
    q = spark.read.format("delta").load(T).filter("customer_id = 42")
    return {"before": before, "after": after, "metrics": {"added": int(r["numFilesAdded"]), "removed": int(r["numFilesRemoved"])},
            "files_read_customer_42": files_read(q), "max_file_size_set_kb": 250,
            "note": "maxFileSize was lowered to 250 KB so the tiny demo table yields several files; the default target is about 1 GB."}


def s_zorder():
    r = spark.sql(f"OPTIMIZE delta.`{T}` ZORDER BY (customer_id)").collect()[0]["metrics"]
    q = spark.read.format("delta").load(T).filter("customer_id = 42")
    return {"after": detail(T), "metrics": {"added": int(r["numFilesAdded"]), "removed": int(r["numFilesRemoved"])},
            "files_read_customer_42": files_read(q)}


def s_vacuum():
    dry = spark.sql(f"VACUUM delta.`{T}` DRY RUN").collect()
    v_old = 100
    spark.conf.set("spark.databricks.delta.optimizeMetadataQuery.enabled", "false")  # count(*) must read files, not stats
    spark.sql(f"SELECT sum(amount) c FROM delta.`{T}` VERSION AS OF {v_old}").collect()
    out = {"before": detail(T), "dry_run_default_7d_files": len(dry), "time_travel_before_vacuum": "ok"}
    spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "false")
    spark.sql(f"VACUUM delta.`{T}` RETAIN 0 HOURS").collect()
    out["after"] = detail(T)
    try:
        spark.sql(f"SELECT sum(amount) c FROM delta.`{T}` VERSION AS OF {v_old}").collect()
        out["time_travel_after_vacuum"] = "still works"
    except Exception as e:  # noqa: BLE001
        out["time_travel_after_vacuum"] = "failed: " + why(e)
    out["current_rows"] = spark.read.format("delta").load(T).count()
    spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "true")
    return out


DV = str(SCRATCH / "orders_dv")


def s_deletion_vectors():
    (spark.range(0, 60000).selectExpr("id as order_id", "pmod(hash(id), 1000) as customer_id", "round(pmod(hash(id,2), 50000)/100.0,2) as amount")
        .repartition(4).write.format("delta").option("delta.enableDeletionVectors", "true").save(DV))
    spark.sql(f"ALTER TABLE delta.`{DV}` SET TBLPROPERTIES ('delta.enableDeletionVectors' = 'true')")
    b0 = detail(DV)
    rows0 = spark.read.format("delta").load(DV).count()
    spark.sql(f"DELETE FROM delta.`{DV}` WHERE customer_id < 50")
    h = hist(DV)[0]
    b1 = detail(DV)
    rows1 = spark.read.format("delta").load(DV).count()
    spark.sql(f"REORG TABLE delta.`{DV}` APPLY (PURGE)").collect()
    h2 = hist(DV)[0]
    b2 = detail(DV)
    spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "false")
    spark.sql(f"VACUUM delta.`{DV}` RETAIN 0 HOURS").collect()
    spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "true")
    return {"start": b0, "rows_start": rows0, "after_delete": b1, "rows_after_delete": rows1, "delete_metrics": h["metrics"],
            "after_purge": b2, "purge_metrics": h2["metrics"], "after_vacuum": detail(DV)}


def s_restore_clone():
    R_ = str(SCRATCH / "restore_demo")
    spark.range(0, 10000).selectExpr("id", "pmod(hash(id), 100) as k").repartition(2).write.format("delta").save(R_)       # version 0
    spark.sql(f"DELETE FROM delta.`{R_}` WHERE k < 50")                                                                        # version 1 (bad delete)
    rows_bad = spark.read.format("delta").load(R_).count()
    spark.sql(f"RESTORE TABLE delta.`{R_}` TO VERSION AS OF 0").collect()                                                      # version 2
    rows_restored = spark.read.format("delta").load(R_).count()
    out = {"rows_after_bad_delete": rows_bad, "rows_after_restore": rows_restored}
    C = str(SCRATCH / "restore_clone")
    spark.sql(f"CREATE TABLE delta.`{C}` SHALLOW CLONE delta.`{R_}`").collect()
    out["shallow_clone"] = {"files_in_table": detail(C)["files_in_table"], "parquet_files_in_clone_folder": disk_files(C), "parquet_files_in_source_folder": disk_files(R_)}
    spark.sql(f"DELETE FROM delta.`{R_}` WHERE k < 50")                                                                        # version 3
    spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "false")
    spark.sql(f"VACUUM delta.`{R_}` RETAIN 0 HOURS").collect()
    spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "true")
    try:
        spark.sql(f"RESTORE TABLE delta.`{R_}` TO VERSION AS OF 0").collect()
        out["restore_after_vacuum"] = "worked"
    except Exception as e:  # noqa: BLE001
        out["restore_after_vacuum"] = "failed: " + str(e).splitlines()[0][:160]
    try:
        spark.read.format("delta").load(C).selectExpr("sum(k)").collect()
        out["shallow_clone_after_source_vacuum"] = "still readable"
    except Exception as e:  # noqa: BLE001
        out["shallow_clone_after_source_vacuum"] = "failed: " + why(e)
    return out


def s_optimized_write():
    P = str(SCRATCH / "ow_off")
    Q = str(SCRATCH / "ow_on")
    df = spark.range(0, 60000).selectExpr("id", "pmod(hash(id), 1000) as customer_id").repartition(40)
    df.write.format("delta").save(P)
    spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")
    df.write.format("delta").save(Q)
    spark.conf.unset("spark.databricks.delta.optimizeWrite.enabled")
    return {"files_without": detail(P)["files_in_table"], "files_with_optimized_writes": detail(Q)["files_in_table"]}


def s_auto_compact():
    P = str(SCRATCH / "ac_off")
    Q = str(SCRATCH / "ac_on")
    for i in range(60):
        batch(i, 200).write.format("delta").mode("append").save(P)
    spark.conf.set("spark.databricks.delta.autoCompact.enabled", "true")
    spark.conf.set("spark.databricks.delta.autoCompact.minNumFiles", "10")
    for i in range(60):
        batch(i, 200).write.format("delta").mode("append").save(Q)
    spark.conf.unset("spark.databricks.delta.autoCompact.enabled")
    return {"appends": 60, "files_without": detail(P)["files_in_table"], "files_with_auto_compaction": detail(Q)["files_in_table"], "min_files_set": 10}


def s_liquid():
    """CREATE ... CLUSTER BY and inserts work in open-source Delta 3.2.0; OPTIMIZE on the clustered table failed here
    (SparkException 'Boxed Error', cause not isolated). Recorded as-is: liquid clustering is NOT measured on the site."""
    spark.sql("DROP TABLE IF EXISTS liquid_orders")
    spark.sql("CREATE TABLE liquid_orders (order_id BIGINT, customer_id INT, country STRING, amount DOUBLE, order_date DATE) USING DELTA CLUSTER BY (customer_id)")
    out = {"create_with_cluster_by": "ok", "clustering_columns": list(spark.sql("DESCRIBE DETAIL liquid_orders").collect()[0]["clusteringColumns"])}
    try:
        spark.sql("OPTIMIZE liquid_orders").collect()
        out["optimize"] = "ok"
    except Exception as e:  # noqa: BLE001
        out["optimize"] = "failed in this local open-source setup: " + why(e)
    return out


def s_write_speed():
    """The same 300,000 rows written four ways; wall-clock seconds and files produced."""
    import time
    base = spark.range(0, 300000).selectExpr("id as order_id", "pmod(hash(id), 1000) as customer_id", "pmod(hash(id,1), 10) as country_id", "round(pmod(hash(id,2), 50000)/100.0, 2) as amount").cache()
    base.count()
    out = {"rows": 300000, "partitions_of_customer_id": 1000}
    cases = [
        ("a_partition_by_high_cardinality", lambda df, p: df.repartition(8).write.format("delta").partitionBy("customer_id").save(p)),
        ("b_repartition_by_key_then_partition", lambda df, p: df.repartition("customer_id").write.format("delta").partitionBy("customer_id").save(p)),
        ("c_partition_by_low_cardinality", lambda df, p: df.repartition(8).write.format("delta").partitionBy("country_id").save(p)),
        ("d_no_partition_right_sized", lambda df, p: df.repartition(2).write.format("delta").save(p)),
    ]
    for name, fn in cases:
        P = str(SCRATCH / f"w_{name}")
        t0 = time.time()
        fn(base, P)
        secs = round(time.time() - t0, 1)
        d = detail(P)
        out[name] = {"seconds": secs, "files": d["files_in_table"], "size_kb": d["size_kb"], "avg_file_kb": round(d["size_kb"] / max(d["files_in_table"], 1), 1)}
        # the cost lands later: how long does a simple read of the result take?
        t1 = time.time()
        spark.read.format("delta").load(P).filter("amount > 400").count()
        out[name]["read_seconds"] = round(time.time() - t1, 1)
    base.unpersist()
    return out


def s_history():
    rows = spark.sql(f"DESCRIBE HISTORY delta.`{T}`").select("version", "operation").orderBy("version").collect()
    ops = {}
    for r in rows:
        ops[r["operation"]] = ops.get(r["operation"], 0) + 1
    return {"operations": ops, "last_five": [(r["version"], r["operation"]) for r in rows[-5:]]}


for nm, fn in [("small_files", s_small_files), ("optimize", s_optimize), ("zorder", s_zorder), ("vacuum", s_vacuum),
               ("deletion_vectors", s_deletion_vectors), ("restore_clone", s_restore_clone), ("optimized_write", s_optimized_write),
               ("auto_compact", s_auto_compact), ("liquid", s_liquid), ("write_speed", s_write_speed), ("history", s_history)]:
    step(nm, fn)
    print(nm, R[nm].get("status"))
OUT.write_text(json.dumps(R, indent=2, default=str))
print("wrote", OUT)
