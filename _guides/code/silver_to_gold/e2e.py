"""The whole story on the page, run for real: three nightly runs, a crash and rerun, a bad join stopped,
and the other fact kinds. Writes results.json, which the page generator reads, so the page shows these numbers.

    unset SPARK_HOME; python e2e.py
"""
import json
import shutil
import tempfile
from datetime import date as D
from pathlib import Path

from pyspark.sql import functions as F

import builds as B
import data as X
import harness as H
from conftest import make_spark

HERE = Path(__file__).parent
spark = make_spark("silver-to-gold-e2e")
tmp = Path(tempfile.mkdtemp())
GOLD = str(tmp / "fact_otif")
store = H.Meta(tmp / "meta.json")
keymap = spark.createDataFrame([], "dealer_id string, valid_from date, dealer_key int")
res = {"runs": [], "fact": {}, "dim": {}}


def df(rows, schema):
    return spark.createDataFrame(rows, schema)


def dim_from(history):
    """The shared dimension pipeline: keys from the key map, versions from silver's SCD2 history."""
    global keymap
    keymap = H.assign_keys(history, keymap, "dealer_id", "dealer_key").localCheckpoint()
    return history.join(keymap, ["dealer_id", "valid_from"]).select("dealer_key", "dealer_id", "name", "region", "valid_from", "valid_to")


def tables(lines, dels, dealers):
    return {"order_lines": df(lines, X.LINES_S), "deliveries": df(dels, X.DELS_S), "dim_dealer": dim_from(df(dealers, X.DEALERS_S))}


def snap(label):
    g = spark.read.format("delta").load(GOLD).orderBy("line_id")
    res["fact"][label] = [{k: str(v) if isinstance(v, D) else v for k, v in r.asDict().items()} for r in g.collect()]


def run(rid, day, lines, dels, dealers, files, build=B.build_otif):
    t = tables(lines, dels, dealers)
    out = H.run_fact(spark, H.FACT_OTIF, store, t, GOLD, build, rid, day, df(files, X.FILES_S))
    res["runs"].append(out)
    return t


run("r0", D(2026, 11, 5), X.LINES_R0, X.DELS_R0, X.DEALERS_R1, X.FILES_R0)
snap("after r0")
t1 = run("r1", D(2026, 11, 13), X.LINES_R1, X.DELS_R1, X.DEALERS_R1, X.FILES_R1)
snap("after r1")
res["dim"]["after r1"] = [{k: str(v) for k, v in r.asDict().items()} for r in t1["dim_dealer"].orderBy("dealer_key").collect()]

# wrong way, for the page: join to the CURRENT dealer row instead of the row true on the event date
cur = t1["dim_dealer"].where("valid_to = '9999-12-31'").select("dealer_id", F.col("region").alias("current_region"))
asof = spark.read.format("delta").load(GOLD).join(t1["dim_dealer"].select("dealer_key", "region"), "dealer_key", "left")
cmp = asof.join(cur, "dealer_id", "left").where("line_id IN ('L1','L2','L3','L4')").orderBy("line_id")
res["asof_vs_current"] = [{"line_id": r.line_id, "promised_date": str(r.promised_date), "as_of_region": r.region,
                           "current_region": r.current_region, "otif": r.otif} for r in cmp.collect()]

# r2 crashes after writing but before moving the watermark ...
real_commit = store.commit
store.commit = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("machine lost"))
try:
    run("r2-crashed", D(2026, 11, 15), X.LINES_R2, X.DELS_R2, X.DEALERS_R2, X.FILES_R2)
except RuntimeError as e:
    res["crash"] = str(e)
store.commit = real_commit
snap("after crash")
# ... the rerun reads the same range again and gives the same table
store = H.Meta(tmp / "meta.json")
t2 = run("r2", D(2026, 11, 15), X.LINES_R2, X.DELS_R2, X.DEALERS_R2, X.FILES_R2)
snap("after r2")
res["dim"]["after r2"] = [{k: str(v) for k, v in r.asDict().items()} for r in t2["dim_dealer"].orderBy("dealer_key").collect()]
strip = lambda rows: [{k: v for k, v in r.items() if k != "_run_id"} for r in rows]  # noqa: E731
res["rerun_same_as_crash"] = strip(res["fact"]["after crash"]) == strip(res["fact"]["after r2"])
res["watermarks"] = store.data["watermarks"]
res["restatements"] = store.data["restatements"]

# a careless build that joins every delivery row: the ledger stops it before anything is written
def careless(lines, dels, params):
    j = lines.join(dels.select("line_id", F.col("qty").alias("qty_delivered"), "delivered_date"), "line_id", "left")
    return j.select("line_id", "dealer_id", "promised_date", "qty_ordered", "qty_delivered",
                    F.lit(0).alias("on_time"), F.lit(0).alias("in_full"), F.lit(0).alias("otif"))


st2 = H.Meta(tmp / "meta2.json")
try:
    H.run_fact(spark, H.FACT_OTIF, st2, t2, str(tmp / "careless"), careless, "r-careless", D(2026, 11, 15), df(X.FILES_R2, X.FILES_S))
    res["careless"] = "NOT STOPPED"
except RuntimeError as e:
    res["careless"] = str(e)
res["careless_wrote_nothing"] = not (tmp / "careless").exists()

# aggregate fact: OTIF per region per day, from gold
agg = B.build_otif_by_region(spark.read.format("delta").load(GOLD), t2["dim_dealer"], {}).orderBy("promised_date", "region")
res["aggregate"] = [{k: str(v) if isinstance(v, D) else v for k, v in r.asDict().items()} for r in agg.collect()]

# periodic snapshot: daily stock, 10 to 13 Nov
days = df([(D(2026, 11, d),) for d in range(10, 14)], "day date")
st = B.build_daily_stock(df(X.MOVES, X.MOVES_S), days, {}).orderBy("snapshot_date")
res["stock"] = [{"day": str(r.snapshot_date), "stock": r.stock_on_hand} for r in st.collect()]

# accumulating snapshot: one row for line L3, updated by MERGE on three days
life_path = str(tmp / "fact_line_lifecycle")
res["lifecycle"] = []
for label, ev in [("day 1", X.EVENTS_DAY1), ("day 2", X.EVENTS_DAY2), ("day 3", X.EVENTS_DAY3)]:
    built = B.build_line_lifecycle(df(ev, X.EVENTS_S), {})
    for m in B.MILESTONES:                      # a milestone not in today's changes comes back empty
        if f"{m}_at" not in built.columns:
            built = built.withColumn(f"{m}_at", F.lit(None).cast("date"))
    built = built.select("line_id", *[f"{m}_at" for m in B.MILESTONES])
    H.merge_by_key(spark, built, life_path, "line_id", [f"{m}_at" for m in B.MILESTONES])
    r = (spark.read.format("delta").load(life_path)
         .withColumn("days_to_deliver", F.datediff("delivered_at", "ordered_at")).first())
    res["lifecycle"].append({"after": label, **{k: (str(v) if v is not None else None) for k, v in r.asDict().items()}})
res["lifecycle_rows"] = spark.read.format("delta").load(life_path).count()

# factless: visits, and which dealers were NOT visited (coverage)
vis = B.build_visits(df(X.VISITS, X.VISITS_S), {})
res["visits"] = vis.count()
res["not_visited"] = [r.dealer_id for r in t2["dim_dealer"].select("dealer_id").distinct().join(vis, "dealer_id", "left_anti").collect()]

# consolidated: plan vs actual for November
pva = B.build_plan_vs_actual(df(X.PLAN, X.PLAN_S), df(X.LINES_R2, X.LINES_S).where("dealer_id != 'TEST01'"), {}).orderBy("dealer_id")
res["plan_vs_actual"] = [r.asDict() for r in pva.collect()]

(HERE / "results.json").write_text(json.dumps(res, indent=1, default=str))
print(json.dumps(res, indent=1, default=str))
spark.stop()
shutil.rmtree(tmp)
