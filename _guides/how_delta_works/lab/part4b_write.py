import os, json, glob
from lab import *
spark = session("write2", cores=2)
res = {"ops": []}
N = 100_000
def mk(n0, n1, status="new", country=None):
    c = F.lit(country) if country else F.element_at(F.array(*[F.lit(x) for x in ["IN","US","UK","DE","FR"]]), (F.col("id") % 5 + 1).cast("int"))
    return spark.range(n0, n1).select(F.col("id").alias("event_id"), (F.rand(3) * 50000).cast("long").alias("user_id"), F.round(F.rand(5) * 900 + 5, 2).alias("amount"), c.alias("country"), F.lit(status).alias("status"))
def fresh(name, dv=False):
    p = f"{DATA}/w_{name}"
    mk(0, N).coalesce(1).sortWithinPartitions("event_id").write.format("delta").option("maxRecordsPerFile", 10000).mode("overwrite").save(p)
    if dv: spark.sql(f"ALTER TABLE delta.`{p}` SET TBLPROPERTIES ('delta.enableDeletionVectors' = 'true')")
    return p
def commit(p, v): return [json.loads(l) for l in open(f"{p}/_delta_log/{v:020d}.json").read().splitlines()]
def op(label, sql_text, p, fn):
    before = spark.sql(f"DESCRIBE DETAIL delta.`{p}`").collect()[0]
    t = time.perf_counter(); fn(); secs = time.perf_counter() - t
    after = spark.sql(f"DESCRIBE DETAIL delta.`{p}`").collect()[0]
    h = spark.sql(f"DESCRIBE HISTORY delta.`{p}`").collect()[0]
    v = h["version"]; acts = commit(p, v); kinds = {}
    for a in acts: k = list(a.keys())[0]; kinds[k] = kinds.get(k, 0) + 1
    ci = [a["commitInfo"] for a in acts if "commitInfo" in a][0]
    adds = [a["add"] for a in acts if "add" in a]; rems = [a["remove"] for a in acts if "remove" in a]
    dv = [a for a in adds if a.get("deletionVector")]
    r = {"label": label, "sql": sql_text, "version": v, "seconds": round(secs, 3), "files_before": before["numFiles"], "files_after": after["numFiles"],
         "actions": kinds, "operation": h["operation"], "operationParameters": dict(h["operationParameters"]), "operationMetrics": dict(h["operationMetrics"]),
         "isBlindAppend": ci.get("isBlindAppend"), "readVersion": ci.get("readVersion"), "isolationLevel": ci.get("isolationLevel"), "dv_adds": len(dv),
         "sample_dv": (dv[0]["deletionVector"] if dv else None),
         "sample_remove": ({k: rems[0][k] for k in rems[0] if k in ("path", "dataChange", "size", "deletionTimestamp")} if rems else None),
         "sample_add": ({k: adds[0][k] for k in adds[0] if k in ("path", "size", "dataChange")} if adds else None)}
    res["ops"].append(r); m = r["operationMetrics"]
    print(label, "v", v, kinds, "files", r["files_before"], "->", r["files_after"], {k: m[k] for k in m if k.startswith(("numRemovedFiles", "numAddedFiles", "numTargetFiles", "numUpdatedRows", "numCopiedRows", "numDeletedRows", "numTargetRows", "numDeletionVectors", "numOutputRows"))}, secs)
# 1. create is the first commit
p = f"{DATA}/w_create"; t = time.perf_counter()
mk(0, N).coalesce(1).sortWithinPartitions("event_id").write.format("delta").option("maxRecordsPerFile", 10000).mode("overwrite").save(p)
h = spark.sql(f"DESCRIBE HISTORY delta.`{p}`").collect()[0]; acts = commit(p, 0)
res["create"] = {"seconds": round(time.perf_counter() - t, 3), "actions": {k: sum(1 for a in acts if k in a) for k in ("commitInfo", "metaData", "protocol", "add")}, "operation": h["operation"]}
print("create", res["create"])
# 2. append (blind append) on a fresh table
pa = fresh("append"); mk(N, N + 5000).createOrReplaceTempView("new5k")
op("insert_append", "INSERT INTO t SELECT ... 5,000 new rows", pa, lambda: spark.sql(f"INSERT INTO delta.`{pa}` SELECT * FROM new5k"))
# 3. update touching rows in one file, and in every file
pu1 = fresh("upd_one"); op("update_one_file", "UPDATE t SET status='checked' WHERE event_id BETWEEN 20 AND 30", pu1, lambda: spark.sql(f"UPDATE delta.`{pu1}` SET status = 'checked' WHERE event_id BETWEEN 20 AND 30"))
pu2 = fresh("upd_all"); op("update_every_file", "UPDATE t SET amount = amount + 1 WHERE user_id % 100 = 0", pu2, lambda: spark.sql(f"UPDATE delta.`{pu2}` SET amount = amount + 1 WHERE user_id % 100 = 0"))
# 4. delete: rewrite vs deletion vectors
pd1 = fresh("del_rewrite"); op("delete_rewrite", "DELETE FROM t WHERE event_id < 50", pd1, lambda: spark.sql(f"DELETE FROM delta.`{pd1}` WHERE event_id < 50"))
pd2 = fresh("del_dv", dv=True); op("delete_with_deletion_vector", "DELETE FROM t WHERE event_id < 50   (delta.enableDeletionVectors = true)", pd2, lambda: spark.sql(f"DELETE FROM delta.`{pd2}` WHERE event_id < 50"))
res["dv_rows_after"] = spark.read.format("delta").load(pd2).count()
# 5. merge: keys in one file vs spread across every file
srcA = mk(60000, 61000, "merged").unionByName(mk(500000, 501000, "fresh")); srcA.createOrReplaceTempView("src_clustered")
srcB = mk(0, 100000, "spread").filter("event_id % 1000 = 0"); srcB.createOrReplaceTempView("src_spread")
M = "MERGE INTO delta.`{p}` t USING {s} s ON t.event_id = s.event_id WHEN MATCHED THEN UPDATE SET t.status = s.status, t.amount = s.amount WHEN NOT MATCHED THEN INSERT *"
pm1 = fresh("merge_a"); op("merge_keys_in_one_file", "MERGE ... 1,000 matching keys (one file) + 1,000 new keys", pm1, lambda: spark.sql(M.format(p=pm1, s="src_clustered")))
pm2 = fresh("merge_b"); op("merge_keys_in_every_file", "MERGE ... 100 matching keys, one in each of 10 files", pm2, lambda: spark.sql(M.format(p=pm2, s="src_spread")))
# 6. small appends then OPTIMIZE
po = fresh("opt"); 
for i in range(5): mk(N + i * 100, N + i * 100 + 100).write.format("delta").mode("append").save(po)
op("optimize_after_small_appends", "OPTIMIZE t   (after five tiny appends)", po, lambda: spark.sql(f"OPTIMIZE delta.`{po}`"))
# 7. overwrite then time travel
pw = fresh("overwrite")
op("overwrite", "write.mode('overwrite') of 20,000 rows", pw, lambda: mk(0, 20000, "over").write.format("delta").mode("overwrite").save(pw))
res["time_travel"] = {"rows_now": spark.read.format("delta").load(pw).count(), "rows_version0": spark.read.format("delta").option("versionAsOf", 0).load(pw).count(),
                      "parquet_files_on_disk": n_parquet(pw), "files_in_current_version": spark.sql(f"DESCRIBE DETAIL delta.`{pw}`").collect()[0]["numFiles"],
                      "log": sorted(os.path.basename(x) for x in glob.glob(f"{pw}/_delta_log/*.json"))}
print(res["time_travel"])
save("part4b_write", res); spark.stop()
