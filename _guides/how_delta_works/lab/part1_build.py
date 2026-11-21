import os, shutil, json
from lab import *
shutil.rmtree(DATA, ignore_errors=True); os.makedirs(DATA)
spark = session("build")
N = 200_000; PER = 10_000
fillers = [F.expr(f"cast(id % {7 + i} as int)").alias(f"f{i:02d}") for i in range(1, 34)]
base = (spark.range(N).select(F.col("id").alias("event_id"),
        (F.rand(7) * 50000).cast("long").alias("user_id"),
        F.date_add(F.lit("2026-01-01").cast("date"), (F.col("id") * 20 / N).cast("int")).alias("event_date"),
        F.element_at(F.array(*[F.lit(c) for c in ["IN","US","UK","DE","FR","AU","AE","SG","JP","BR"]]), (F.col("id") % 10 + 1).cast("int")).alias("country"),
        F.round(F.rand(11) * 900 + 5, 2).alias("amount"), F.sha1(F.col("id").cast("string")).alias("payload"), *fillers,
        (F.col("id") * 20 / N).cast("int").alias("late_code")))
print("columns", len(base.columns), "late_code at position", base.columns.index("late_code") + 1)
res = {"rows": N, "rows_per_file": PER, "columns": len(base.columns), "late_code_position": base.columns.index("late_code") + 1}
# T: default stats (first 32 columns), written sorted by id in 20 files
def write(path, df, props=None, per=PER):
    w = df.coalesce(1).sortWithinPartitions("event_id").write.format("delta").option("maxRecordsPerFile", per).mode("overwrite")
    w.save(path)
    if props:
        for k, v in props.items(): spark.sql(f"ALTER TABLE delta.`{path}` SET TBLPROPERTIES ('{k}' = '{v}')")
write(f"{DATA}/T", base)
# T2: stats on all 40 columns (property must exist before the write)
spark.sql(f"CREATE TABLE delta.`{DATA}/T2` USING delta TBLPROPERTIES ('delta.dataSkippingNumIndexedCols'='40') AS SELECT * FROM delta.`{DATA}/T` WHERE 1=0")
base.coalesce(1).sortWithinPartitions("event_id").write.format("delta").option("maxRecordsPerFile", PER).mode("append").save(f"{DATA}/T2")
# S: same rows in 400 small files
write(f"{DATA}/S", base, per=500)
for n in ["T", "T2", "S"]:
    d = spark.sql(f"DESCRIBE DETAIL delta.`{DATA}/{n}`").collect()[0]
    res[n] = {"files": d["numFiles"], "bytes": d["sizeInBytes"]}
print(res)
save("part1_build", res)
spark.stop()
