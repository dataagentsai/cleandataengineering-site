"""How many partitions does a DataFrame have? Runs on the tables run.py left in its scratch directory.

    unset SPARK_HOME; python partition_counts.py <scratch_dir_used_by_run.py>

Writes partitions.json next to this file. Spark 3.5.1 + Delta 3.2.0, local[4].
"""
import json
import os
import sys
from pathlib import Path

os.environ.pop("SPARK_HOME", None)
os.environ["PYSPARK_PYTHON"] = sys.executable
from delta import configure_spark_with_delta_pip  # noqa: E402
from pyspark.sql import SparkSession, functions as F  # noqa: E402

S = Path(sys.argv[1])
b = (SparkSession.builder.master("local[4]").appName("pc").config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
     .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog").config("spark.ui.enabled", "false"))
spark = configure_spark_with_delta_pip(b).getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
R = {"defaults": {"maxPartitionBytes_mb": int(spark.conf.get("spark.sql.files.maxPartitionBytes").rstrip("b")) // 1048576 if spark.conf.get("spark.sql.files.maxPartitionBytes").endswith("b") else spark.conf.get("spark.sql.files.maxPartitionBytes"),
                  "shuffle_partitions": spark.conf.get("spark.sql.shuffle.partitions")}}


def spread(df):
    rows = [r["count"] for r in df.groupBy(F.spark_partition_id().alias("p")).count().collect()]
    return {"partitions_with_rows": len(rows), "min_rows": min(rows), "max_rows": max(rows)}


def read(name):
    return spark.read.format("delta").load(str(S / name))


for key, name in [("many_tiny_files", "w_a_partition_by_high_cardinality"), ("two_files", "w_d_no_partition_right_sized"), ("compacted_orders", "orders")]:
    df = read(name)
    R[key] = {"table": name, "source_files": len(df.inputFiles()), "partitions_after_read": df.rdd.getNumPartitions()}
    R[key]["partitions_after_filter"] = df.filter("amount > 400").rdd.getNumPartitions()

big = read("w_a_partition_by_high_cardinality")
R["after_shuffle"] = {}
for aqe in ("false", "true"):
    spark.conf.set("spark.sql.adaptive.enabled", aqe)
    g = big.groupBy("customer_id").count()
    R["after_shuffle"][f"aqe_{aqe}_planned_partitions"] = g.rdd.getNumPartitions()
spark.conf.set("spark.sql.adaptive.enabled", "false")

df = read("w_d_no_partition_right_sized")
R["repartition_8"] = {"partitions": df.repartition(8).rdd.getNumPartitions(), **spread(df.repartition(8))}
R["coalesce_1"] = {"partitions": df.coalesce(1).rdd.getNumPartitions()}
R["skew_by_key"] = {**spread(df.withColumn("k", F.when(F.col("customer_id") < 100, F.lit(0)).otherwise(F.col("customer_id"))).repartition("k"))}
R["skew_by_key"]["note"] = "10 percent of rows share key 0; repartition by key puts them all in one partition"

# files written = tasks in the write stage (x distinct values with partitionBy)
out = {}
for name, fn in [("repartition_8_no_partitionBy", lambda d, p: d.repartition(8).write.format("delta").save(p)),
                 ("repartition_8_partitionBy_customer", lambda d, p: d.repartition(8).write.format("delta").partitionBy("customer_id").save(p)),
                 ("repartition_by_customer_partitionBy_customer", lambda d, p: d.repartition("customer_id").write.format("delta").partitionBy("customer_id").save(p))]:
    p = str(S / f"pc_{name}")
    fn(df, p)
    out[name] = len(list(Path(p).rglob("*.parquet")))
R["files_written"] = out
(Path(__file__).parent / "partitions.json").write_text(json.dumps(R, indent=2))
print(json.dumps(R, indent=1))
