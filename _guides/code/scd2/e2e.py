import os, sys, shutil, tempfile
os.environ["PYSPARK_PYTHON"] = sys.executable; os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
os.environ.pop("SPARK_HOME", None)
from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession
from adapters import run_cdc, run_snapshot, change_feed_events
from scd2 import plan_scd2, apply_scd2
from delta.tables import DeltaTable

wh = tempfile.mkdtemp()
spark = configure_spark_with_delta_pip(SparkSession.builder.master("local[2]")
    .config("spark.sql.shuffle.partitions", "2").config("spark.ui.enabled", "false")
    .config("spark.sql.warehouse.dir", wh)
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")).getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

DDL = "CREATE TABLE {} (customer_id INT, city STRING, segment STRING, row_hash STRING, valid_from {t}, valid_to {t}, is_current BOOLEAN) USING delta"
show = lambda n: spark.sql(f"SELECT customer_id, city, segment, valid_from, valid_to, is_current FROM {n} ORDER BY customer_id, valid_from").show(truncate=False)

# --- 1. CDC path: streaming foreachBatch, two batches, out-of-order and replay ---
spark.sql("CREATE TABLE cdc (customer_id INT, op STRING, commit_ts TIMESTAMP, city STRING, segment STRING) USING delta")
spark.sql(DDL.format("dim_customer", t="TIMESTAMP"))
spark.sql("""INSERT INTO cdc VALUES
 (42,'I',TIMESTAMP'2026-01-04 00:00','Pune','retail'),
 (42,'U',TIMESTAMP'2026-05-19 00:00','Mumbai','retail'),
 (7,'I',TIMESTAMP'2026-02-01 00:00','Chennai','sme'),
 (7,'U',TIMESTAMP'2026-02-01 00:00','Chennai','sme'),
 (9,'I',TIMESTAMP'2026-03-01 00:00','Goa','retail')""")
ck = os.path.join(wh, "_ck")
run_cdc(spark, "cdc", "dim_customer", "customer_id", "commit_ts", ["city", "segment"], ck)
print("after CDC batch 1"); show("dim_customer")
spark.sql("""INSERT INTO cdc VALUES
 (42,'U',TIMESTAMP'2026-09-02 00:00','Delhi','retail'),
 (42,'D',TIMESTAMP'2026-11-01 00:00',NULL,NULL),
 (7,'U',TIMESTAMP'2026-01-15 00:00','Madurai','sme'),
 (9,'U',TIMESTAMP'2026-06-01 00:00','Goa','retail')""")
run_cdc(spark, "cdc", "dim_customer", "customer_id", "commit_ts", ["city", "segment"], ck)
print("after CDC batch 2 (42 moves then deleted; 7 late event skipped; 9 no-op)"); show("dim_customer")

# Replay: rerun the whole source as one batch, table must not change
before = spark.table("dim_customer").count()
t = DeltaTable.forName(spark, "dim_customer")
apply_scd2(t, plan_scd2(spark.table("cdc"), t.toDF(), "customer_id", "commit_ts", ["city", "segment"]), "customer_id", ["city", "segment"])
print("replay full source -> rows before", before, "after", spark.table("dim_customer").count())

# --- 2. Snapshot path: three daily snapshots, then re-run day 3 ---
spark.sql(DDL.format("dim_snap", t="DATE"))
spark.sql("CREATE TABLE snap (customer_id INT, city STRING, segment STRING) USING delta")
days = [("2026-11-01", "(1,'Pune','retail'),(2,'Goa','sme')"),
        ("2026-11-02", "(1,'Pune','retail'),(2,'Goa','corp'),(3,'Delhi','retail')"),
        ("2026-11-03", "(2,'Goa','corp'),(3,'Delhi','retail')")]
from datetime import date
for d, rows in days:
    spark.sql(f"INSERT OVERWRITE snap VALUES {rows}")
    run_snapshot(spark, "snap", "dim_snap", "customer_id", ["city", "segment"], date.fromisoformat(d))
print("after 3 snapshots (2 changes segment on day 2, 3 new on day 2, 1 deleted on day 3)"); show("dim_snap")
n = spark.table("dim_snap").count()
run_snapshot(spark, "snap", "dim_snap", "customer_id", ["city", "segment"], date.fromisoformat("2026-11-03"))
print("re-run day 3 -> rows before", n, "after", spark.table("dim_snap").count())

# --- 3. Change data feed adapter: a Delta silver table becomes CDC ---
spark.sql("CREATE TABLE silver (customer_id INT, city STRING, segment STRING) USING delta TBLPROPERTIES (delta.enableChangeDataFeed = true)")
spark.sql(DDL.format("dim_cdf", t="BIGINT"))
spark.sql("INSERT INTO silver VALUES (5,'Pune','retail')")      # v1
spark.sql("UPDATE silver SET city='Delhi' WHERE customer_id=5")  # v2
spark.sql("DELETE FROM silver WHERE customer_id=5")              # v3
tc = DeltaTable.forName(spark, "dim_cdf")
def each(batch, _):
    apply_scd2(tc, plan_scd2(batch, tc.toDF(), "customer_id", "seq", ["city", "segment"]), "customer_id", ["city", "segment"])
(change_feed_events(spark, "silver", 1).writeStream.foreachBatch(each)
   .option("checkpointLocation", os.path.join(wh, "_ck2")).trigger(availableNow=True).start().awaitTermination())
print("change feed: insert v1, update v2, delete v3"); show("dim_cdf")
spark.stop(); shutil.rmtree(wh, ignore_errors=True)
