"""Seven ways of writing silver; after each, three gold readers try to catch the change.
The expected results are a table (EXPECT); the run fails if any reader behaves differently. Writes results.json.

    unset SPARK_HOME; python e2e.py
"""
import json
import shutil
import tempfile
from pathlib import Path

import topologies as T
from conftest import make_spark

spark = make_spark("silver-bookmark")
tmp = Path(tempfile.mkdtemp())
P = str(tmp / "silver_dealers")
READERS = ["_src_seq_first", "_src_seq", "_batch", "change_feed"]
marks = {r: 0 for r in READERS}
marks["change_feed"] = -1
results = []


def gold_reads(op, changed):
    row = {"op": op, "changed": changed}
    for r in READERS:
        if r == "change_feed":
            seen, marks[r] = T.read_change_feed(spark, P, marks[r])
        else:
            seen, marks[r] = T.read_by_column(spark, P, r, marks[r])
        row[r] = seen
    results.append(row)


# 1. first load
T.create(spark, P, [("D1", "North", "Sharma Tyres", 501), ("D7", "North", "Patel Motor", 502)], batch=1)
gold_reads("1. first load (insert)", ["D1", "D7"])
# 2. a new dealer arrives (append)
T.insert(spark, P, [("D9", "South", "Kumar Wheels", 504)], batch=2)
gold_reads("2. new row (append)", ["D9"])
# 3. typo fixed: Type 1 update in place
T.upsert_type1(spark, P, "D7", "name", "Patel Motors", src_seq=505, batch=3)
gold_reads("3. Type 1 update (MERGE)", ["D7"])
# 4. D7 moves region: Type 2 (close old version, add new)
T.scd2_change(spark, P, "D7", "West", src_seq=506, batch=4)
gold_reads("4. Type 2 change (close + insert)", ["D7"])
# 5. D9 hard-deleted
T.hard_delete(spark, P, "D9")
gold_reads("5. hard delete", ["D9"])
# 6. full overwrite from a full copy: D1 moved to East, D7 unchanged
T.full_overwrite(spark, P, [("D1", "East", "Sharma Tyres"), ("D7", "West", "Patel Motors")], batch=6)
overwrite_version = T.latest_version(spark, P)
gold_reads("6. full overwrite (D1 changed)", ["D1"])
# 7. two writers: batch 8 starts first, batch 9 commits first, gold runs in between, then batch 8 commits
T.upsert_type1(spark, P, "D1", "name", "Sharma Tyres Ltd", src_seq=521, batch=9)
gold_reads("7a. batch 9 commits first", ["D1"])
T.upsert_type1(spark, P, "D7", "name", "Patel Motors Pvt", src_seq=520, batch=8)
gold_reads("7b. batch 8 commits later", ["D7"])

# what each reader must do (a table; the run fails on any difference)
EXPECT = {
    "1. first load (insert)":            ("caught", "caught", "caught", "caught"),
    "2. new row (append)":               ("caught", "caught", "caught", "caught"),
    "3. Type 1 update (MERGE)":          ("MISSED", "caught", "caught", "caught"),
    "4. Type 2 change (close + insert)": ("caught", "caught", "caught", "caught"),
    "5. hard delete":                    ("MISSED", "MISSED", "MISSED", "caught"),
    "6. full overwrite (D1 changed)":    ("MISSED", "MISSED", "caught+", "caught+"),
    "7a. batch 9 commits first":         ("MISSED", "caught", "caught", "caught"),
    "7b. batch 8 commits later":         ("MISSED", "MISSED", "MISSED", "caught"),
}


def verdict(changed, seen):
    if not set(changed) <= set(seen):
        return "MISSED"
    return "caught+" if set(seen) - set(changed) else "caught"


table = []
for row in results:
    got = tuple(verdict(row["changed"], row[r]) for r in READERS)
    table.append({**row, "verdicts": got})
    assert got == EXPECT[row["op"]], (row["op"], got, EXPECT[row["op"]], row)

cdf_overwrite = (spark.read.format("delta").option("readChangeFeed", "true").option("startingVersion", overwrite_version).option("endingVersion", overwrite_version)
                 .load(P).groupBy("_change_type").count().collect())
out = {"overwrite_version": overwrite_version, "readers": READERS, "table": table, "overwrite_change_feed": {r[0]: r[1] for r in cdf_overwrite},
       "versions": [h.asDict()["operation"] for h in T.DeltaTable.forPath(spark, P).history().orderBy("version").collect()]}
Path(__file__).with_name("results.json").write_text(json.dumps(out, indent=1, default=str))
print(json.dumps(out, indent=1, default=str))
spark.stop()
shutil.rmtree(tmp)
