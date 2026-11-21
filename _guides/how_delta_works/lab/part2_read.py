import os, json, glob, shutil
from lab import *
spark = session("read", cores=2)
T, T2, S = f"{DATA}/T", f"{DATA}/T2", f"{DATA}/S"
res = {}
def tbl(p): return spark.read.format("delta").load(p)
def plan(df):
    mode = spark._jvm.org.apache.spark.sql.execution.ExplainMode.fromString("formatted")
    return df._jdf.queryExecution().explainString(mode)
def scan_lines(txt):
    keep = [l.strip() for l in txt.splitlines() if any(k in l for k in ("Scan parquet", "PushedFilters", "ReadSchema", "PartitionFilters", "DataFilters", "Location", "Batched"))]
    return keep
d = tbl(T)
Q = {
 "q1_select_star": d,
 "q2_two_columns": d.select("event_id", "amount"),
 "q3_event_date": d.filter(F.col("event_date") == "2026-01-10"),
 "q4_user_id": d.filter(F.col("user_id") == 12345),
 "q5_late_code_default_stats": d.filter(F.col("late_code") == 7),
 "q5b_late_code_stats_on_all": tbl(T2).filter(F.col("late_code") == 7),
}
run(spark, "warmup", tbl(T).limit(10), reps=1)
spark.conf.set("spark.databricks.delta.clusteredTable.enableClusteringTablePreview", "true")
res["queries"] = {}
for k, df in Q.items():
    r = run(spark, k, df)
    r["plan"] = scan_lines(plan(df))
    res["queries"][k] = r; print(k, {x: r[x] for x in ("seconds", "files", "file_bytes", "rows", "tasks", "input_bytes")})
# ---- layout: z-order and liquid clustering on a copy
spark.conf.set("spark.databricks.delta.optimize.maxFileSize", "400000")
spark.conf.set("spark.databricks.delta.optimize.minFileSize", "400000")
TZ = f"{DATA}/TZ"; shutil.copytree(T, TZ)
spark.sql(f"OPTIMIZE delta.`{TZ}` ZORDER BY (user_id)")
dz = tbl(TZ)
res["zorder"] = {"files": spark.sql(f"DESCRIBE DETAIL delta.`{TZ}`").collect()[0]["numFiles"]}
res["queries"]["q4z_user_id_zorder"] = run(spark, "q4z", dz.filter(F.col("user_id") == 12345)); print("zorder", res["queries"]["q4z_user_id_zorder"]["files"], "of", res["zorder"]["files"])
try:
    spark.sql(f"CREATE TABLE tc USING delta CLUSTER BY (user_id) AS SELECT * FROM delta.`{T}`")
    spark.sql("OPTIMIZE tc")
    dd = spark.sql("DESCRIBE DETAIL tc").collect()[0]
    res["liquid"] = {"files": dd["numFiles"], "clusteringColumns": list(dd["clusteringColumns"])}
    res["queries"]["q4c_user_id_liquid"] = run(spark, "q4c", spark.table("tc").filter(F.col("user_id") == 12345))
    print("liquid", res["liquid"], res["queries"]["q4c_user_id_liquid"]["files"])
except Exception as e:
    res["liquid"] = {"error": str(e)[:600]}; print("liquid failed", str(e)[:600])
spark.conf.unset("spark.databricks.delta.optimize.maxFileSize"); spark.conf.unset("spark.databricks.delta.optimize.minFileSize")
# ---- small files: same filter on 400 files vs 20 files
ds = tbl(S)
res["small_files"] = {"s_all": run(spark, "S select all", ds), "t_all": res["queries"]["q1_select_star"],
                      "s_date": run(spark, "S date", ds.filter(F.col("event_date") == "2026-01-10")), "t_date": res["queries"]["q3_event_date"]}
for k, v in res["small_files"].items(): print("small", k, v["seconds"], v["files"], v["tasks"])
# ---- the log of T
log = sorted(glob.glob(f"{T}/_delta_log/*"))
res["log_listing"] = [os.path.basename(p) for p in log]
lines = open(f"{T}/_delta_log/00000000000000000000.json").read().splitlines()
res["log_kinds"] = [list(json.loads(l).keys())[0] for l in lines]
res["log_commitInfo"] = json.loads(lines[res["log_kinds"].index("commitInfo")])["commitInfo"]
res["log_protocol"] = json.loads(lines[res["log_kinds"].index("protocol")])["protocol"]
md = json.loads(lines[res["log_kinds"].index("metaData")])["metaData"]; md["schemaString"] = md["schemaString"][:120] + "..."; res["log_metaData"] = md
adds = [json.loads(l)["add"] for l in lines if '"add"' in l]
a0 = adds[0]; a0["stats_parsed"] = json.loads(a0["stats"]); st = a0["stats_parsed"]
res["log_adds"] = len(adds)
res["log_add_first"] = {k: a0[k] for k in ("path", "partitionValues", "size", "modificationTime", "dataChange")}
res["log_add_first_stats"] = {"numRecords": st["numRecords"], "minValues": {k: st["minValues"][k] for k in ("event_id", "user_id", "event_date", "country", "amount", "f26")},
    "maxValues": {k: st["maxValues"][k] for k in ("event_id", "user_id", "event_date", "country", "amount", "f26")}, "nullCount": {k: st["nullCount"][k] for k in ("event_id", "user_id")},
    "stat_columns": len(st["minValues"]), "has_late_code_stat": "late_code" in st["minValues"], "has_f27_stat": "f27" in st["minValues"]}
res["log_stats_cols_T2"] = len(json.loads(json.loads([l for l in open(sorted(glob.glob(f"{T2}/_delta_log/*.json"))[-1]).read().splitlines() if '"add"' in l][0])["add"]["stats"])["minValues"])
res["ranges"] = []
for i, a in enumerate(adds):
    sp = json.loads(a["stats"])
    res["ranges"].append({"file": i, "event_date_min": sp["minValues"]["event_date"], "event_date_max": sp["maxValues"]["event_date"], "user_id_min": sp["minValues"]["user_id"], "user_id_max": sp["maxValues"]["user_id"]})
# ---- checkpoint demo on a tiny table
L = f"{DATA}/L"
spark.range(10).write.format("delta").save(L)
spark.sql(f"ALTER TABLE delta.`{L}` SET TBLPROPERTIES ('delta.checkpointInterval'='5')")
for i in range(8): spark.range(10 * (i + 1), 10 * (i + 2)).write.format("delta").mode("append").save(L)
res["checkpoint_listing"] = sorted(os.path.basename(p) for p in glob.glob(f"{L}/_delta_log/*"))
res["last_checkpoint"] = open(f"{L}/_delta_log/_last_checkpoint").read().strip()
# ---- parquet footer of one T file through the JVM
f0 = sorted(glob.glob(f"{T}/*.parquet"))[0]
jv = spark._jvm
inp = jv.org.apache.parquet.hadoop.util.HadoopInputFile.fromPath(jv.org.apache.hadoop.fs.Path("file://" + f0), spark._jsc.hadoopConfiguration())
rd = jv.org.apache.parquet.hadoop.ParquetFileReader.open(inp); ft = rd.getFooter(); blocks = ft.getBlocks()
foot = {"file_bytes": os.path.getsize(f0), "row_groups": blocks.size(), "created_by": ft.getFileMetaData().getCreatedBy(), "columns_total": len(base_cols := [c.getPath().toDotString() for c in blocks.get(0).getColumns()])}
bl = blocks.get(0); foot["rows"] = bl.getRowCount(); foot["uncompressed_bytes"] = bl.getTotalByteSize(); foot["chunks"] = []
for c in bl.getColumns():
    n = c.getPath().toDotString()
    if n in ("event_id", "user_id", "country", "f01", "amount", "payload", "late_code"):
        s = c.getStatistics()
        foot["chunks"].append({"column": n, "codec": str(c.getCodec()), "encodings": sorted(str(e) for e in c.getEncodings()), "compressed": c.getTotalSize(), "uncompressed": c.getTotalUncompressedSize(),
                               "min": str(s.genericGetMin()), "max": str(s.genericGetMax())})
res["footer"] = foot; rd.close()
print(json.dumps(foot)[:600])
save("part2_read", res); spark.stop()
