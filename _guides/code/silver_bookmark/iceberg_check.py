"""Does Iceberg's changelog view see every way of writing silver? Iceberg 1.9.2 on Spark 3.5.1, local catalog.

    unset SPARK_HOME; python iceberg_check.py      (writes iceberg_results.json)
"""
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
os.environ.pop("SPARK_HOME", None)
from pyspark.sql import SparkSession  # noqa: E402

JAR = str(Path.home() / ".dataplatform/jars/iceberg-spark-runtime-3.5_2.12-1.9.2.jar")
wh = tempfile.mkdtemp()
spark = (SparkSession.builder.master("local[2]").appName("iceberg-changelog")
         .config("spark.jars", JAR).config("spark.ui.enabled", "false").config("spark.sql.shuffle.partitions", "2")
         .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
         .config("spark.sql.catalog.lake", "org.apache.iceberg.spark.SparkCatalog")
         .config("spark.sql.catalog.lake.type", "hadoop").config("spark.sql.catalog.lake.warehouse", wh).getOrCreate())
q = spark.sql
q("CREATE TABLE lake.s.dealers (dealer_id string, region string, name string) USING iceberg")
ops = [("1. first load (insert)", "INSERT INTO lake.s.dealers VALUES ('D1','North','Sharma Tyres'), ('D7','North','Patel Motor')", ["D1", "D7"]),
       ("2. new row (append)", "INSERT INTO lake.s.dealers VALUES ('D9','South','Kumar Wheels')", ["D9"]),
       ("3. Type 1 update (MERGE)", "MERGE INTO lake.s.dealers t USING (SELECT 'D7' id, 'Patel Motors' nm) s ON t.dealer_id = s.id WHEN MATCHED THEN UPDATE SET name = s.nm", ["D7"]),
       ("5. hard delete", "DELETE FROM lake.s.dealers WHERE dealer_id = 'D9'", ["D9"]),
       ("6. full overwrite (D1 changed)", "INSERT OVERWRITE lake.s.dealers VALUES ('D1','East','Sharma Tyres'), ('D7','North','Patel Motors')", ["D1"])]
out = []
for name, sql, changed in ops:
    before = [r.snapshot_id for r in q("SELECT snapshot_id FROM lake.s.dealers.snapshots ORDER BY committed_at").collect()]
    q(sql)
    after = [r.snapshot_id for r in q("SELECT snapshot_id FROM lake.s.dealers.snapshots ORDER BY committed_at").collect()]
    opts = f"map('end-snapshot-id', '{after[-1]}'" + (f", 'start-snapshot-id', '{before[-1]}')" if before else ")")
    q(f"CALL lake.system.create_changelog_view(table => 's.dealers', options => {opts}, changelog_view => 'cl', net_changes => false)")
    rows = q("SELECT dealer_id, _change_type FROM cl").collect()
    seen = sorted({r.dealer_id for r in rows})
    types = {}
    for r in rows:
        types[r._change_type] = types.get(r._change_type, 0) + 1
    out.append({"op": name, "changed": changed, "seen": seen, "change_types": types,
                "verdict": "MISSED" if not set(changed) <= set(seen) else ("caught+" if set(seen) - set(changed) else "caught")})
    print(out[-1])
Path(__file__).with_name("iceberg_results.json").write_text(json.dumps(out, indent=1))
spark.stop()
shutil.rmtree(wh)
