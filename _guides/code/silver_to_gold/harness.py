"""The harness: READER, KEY LOOKUP, CHECKS, WRITER and the run that ties them together.

Nothing here knows about tyres, dealers or OTIF. The fact's settings (FACT_OTIF below) say what to do;
the processor (builds.py) says how to compute the business rule.
"""
import json
from pathlib import Path

from delta.tables import DeltaTable
from pyspark.sql import DataFrame, functions as F

# --------------------------------------------------------------- metadata for one fact (normally a YAML file)
FACT_OTIF = {
    "name": "fact_otif",
    "grain": ["line_id"],
    "window_col": "promised_date",
    "lookback_days": 35,
    "driver": "order_lines",                                         # the input that carries the window column
    "inputs": {"order_lines": {"bookmark": "_seq"},                  # each input and its bookmark column;
               "deliveries": {"bookmark": "_seq", "window_via": "line_id"}},   # a delivery's window is its line's
    "filters": {"test dealers": "dealer_id NOT IN ('TEST01')"},     # declared filters, counted by name
    "measures": ["qty_ordered", "qty_delivered", "otif"],
    "dimension": {"table": "dim_dealer", "business_key": "dealer_id", "key": "dealer_key", "as_of": "promised_date"},
    "owed_feeds": ["WH-A", "WH-B"],                                  # who must send a file for each day
    "max_unknown_rate": 0.25,
    "params": {},
}


# --------------------------------------------------------------- metadata store (a JSON file here; a database in production)
class Meta:
    def __init__(self, path: Path):
        self.path = path
        self.data = json.loads(path.read_text()) if path.exists() else {"watermarks": {}, "runs": [], "restatements": []}

    def watermark(self, fact, inp):
        return self.data["watermarks"].get(f"{fact}.{inp}", 0)

    def commit(self, fact, high_marks, run):
        """Called LAST, only after the write and the checks succeeded."""
        for inp, hm in high_marks.items():
            self.data["watermarks"][f"{fact}.{inp}"] = hm
        self.data.setdefault("versions", {})[fact] = run["gold_version"]   # the last version readers may trust
        self.data["runs"].append(run)
        self.data["restatements"] += run["restatements"]
        self.path.write_text(json.dumps(self.data, indent=1, default=str))


# --------------------------------------------------------------- READER
def high_mark(df: DataFrame, col: str) -> int:
    """Fixed once at the start of the run: changes arriving later wait for the next run."""
    return df.agg(F.max(col)).first()[0] or 0


def read_changes(df: DataFrame, col: str, low: int, high: int) -> DataFrame:
    """Only the rows changed after the watermark, up to the high mark: a closed range."""
    return df.where((F.col(col) > low) & (F.col(col) <= high))


# --------------------------------------------------------------- KEYS (generic: which dimension is metadata)
def assign_keys(history: DataFrame, keymap: DataFrame, bk: str, key: str) -> DataFrame:
    """Stable surrogate keys: existing versions keep their key; new versions get the next numbers."""
    known = history.join(keymap, [bk, "valid_from"], "left")
    start = keymap.agg(F.coalesce(F.max(key), F.lit(0))).first()[0]
    rows = sorted(known.where(F.col(key).isNull()).select(bk, "valid_from").collect())
    add = [(r[0], r[1], start + i + 1) for i, r in enumerate(rows)]
    added = history.sparkSession.createDataFrame(add, f"{bk} string, valid_from date, {key} int")
    return keymap.unionByName(added)


def lookup_keys(fact: DataFrame, dim: DataFrame, bk: str, key: str, as_of: str) -> DataFrame:
    """Find the dimension version that was true ON THE EVENT DATE. Missing member -> -1 (unknown)."""
    d = dim.select(F.col(bk).alias("_bk"), key, "valid_from", "valid_to")
    on = (F.col(bk) == F.col("_bk")) & (F.col(as_of) >= F.col("valid_from")) & (F.col(as_of) < F.col("valid_to"))
    out = fact.join(F.broadcast(d), on, "left").drop("_bk", "valid_from", "valid_to")
    return out.withColumn(key, F.coalesce(F.col(key), F.lit(-1)))


# --------------------------------------------------------------- CHECKS (before anything is written)
def window_summary(df: DataFrame, meta: dict) -> dict:
    """Per window: row count, total of each measure, unknown keys. Used for restatements."""
    key, cols = meta["dimension"]["key"], ["rows"] + meta["measures"] + ["unknown_keys"]
    aggs = [F.count("*").alias("rows")] + [F.sum(m).alias(m) for m in meta["measures"]]
    aggs.append(F.sum((F.col(key) == -1).cast("int")).alias("unknown_keys"))
    s = df.groupBy(meta["window_col"]).agg(*aggs)
    return {str(r[0]): {c: r[c] for c in cols} for r in s.collect()}


def check(out: DataFrame, ledger: dict, meta: dict) -> list:
    problems = []
    dupes = out.groupBy(*meta["grain"]).count().where("count > 1").count()
    if dupes:
        problems.append(f"grain not unique: {dupes} keys appear more than once")
    if ledger["read"] != ledger["filtered"] + ledger["rejected"] + ledger["written"]:
        problems.append(f"ledger does not balance: {ledger}")
    if ledger["after_join"] != ledger["read"] - ledger["filtered"]:
        problems.append(f"a lookup join changed the row count: {ledger['read'] - ledger['filtered']} in, {ledger['after_join']} out")
    if ledger["written"] and ledger["unknown_keys"] / ledger["written"] > meta["max_unknown_rate"]:
        problems.append("too many unknown dealers")
    return problems


# --------------------------------------------------------------- WRITERS
def replace_windows(spark, df: DataFrame, path: str, window_col: str, windows: list):
    """Replace whole windows. Running it twice gives the same table; rows deleted at source simply vanish."""
    if not DeltaTable.isDeltaTable(spark, path):
        df.write.format("delta").save(path)
        return
    cond = f"{window_col} IN ({', '.join(repr(str(w)) for w in windows)})"
    df.write.format("delta").mode("overwrite").option("replaceWhere", cond).save(path)


def merge_by_key(spark, df: DataFrame, path: str, key: str, cols: list):
    """Only for accumulating snapshots: update the row for a key, never blank out a milestone already known."""
    if not DeltaTable.isDeltaTable(spark, path):
        df.write.format("delta").save(path)
        return
    t = DeltaTable.forPath(spark, path)
    sets = {c: F.coalesce(F.col(f"s.{c}"), F.col(f"t.{c}")) for c in cols}
    (t.alias("t").merge(df.alias("s"), f"t.{key} = s.{key}")
      .whenMatchedUpdate(set=sets).whenNotMatchedInsertAll().execute())


# --------------------------------------------------------------- THE RUN (the same steps for every fact)
def run_fact(spark, meta: dict, store: Meta, silver: dict, gold_path: str, build, run_id: str, run_date, files: DataFrame):
    name, wcol, dm = meta["name"], meta["window_col"], meta["dimension"]
    driver = silver[meta["driver"]]

    # 1-2 READER: watermarks, fixed high marks, changed rows only
    marks = {i: store.watermark(name, i) for i in meta["inputs"]}
    highs = {i: high_mark(silver[i], c["bookmark"]) for i, c in meta["inputs"].items()}
    changed = {i: read_changes(silver[i], c["bookmark"], marks[i], highs[i]) for i, c in meta["inputs"].items()}

    # 3 changed rows -> windows (a child row, like a delivery, belongs to the window of its driver row)
    w = changed[meta["driver"]].select(wcol)
    for i, c in meta["inputs"].items():
        if "window_via" in c:
            w = w.union(changed[i].join(driver, c["window_via"]).select(wcol))
    v = store.data.get("versions", {}).get(name)          # plan from the last COMMITTED version, never from a
    if v is not None:                                       # crashed run's half-done write
        g = spark.read.format("delta").option("versionAsOf", v).load(gold_path)
        # also: windows holding unknown members who have now arrived, and windows not yet complete
        w = w.union(g.where(f"{dm['key']} = -1").join(silver[dm["table"]], dm["business_key"], "left_semi").select(wcol))
        w = w.union(g.where("NOT _is_complete").select(wcol))
    windows = sorted({r[0] for r in w.distinct().collect()})
    too_old = [d for d in windows if (run_date - d).days > meta["lookback_days"]]
    windows = [d for d in windows if d not in too_old]          # older changes need a correction plan
    if not windows:
        return {"run": run_id, "windows": [], "note": "nothing changed"}

    # 4 read ALL current silver rows for those windows (not just the changed ones), then the declared filters
    inputs = {meta["driver"]: driver.where(F.col(wcol).isin(windows))}
    for i, c in meta["inputs"].items():
        if "window_via" in c:
            inputs[i] = silver[i].join(inputs[meta["driver"]].select(c["window_via"]), c["window_via"], "left_semi")
    n_read = inputs[meta["driver"]].count()
    for rule in meta["filters"].values():
        inputs[meta["driver"]] = inputs[meta["driver"]].where(rule)
    n_kept = inputs[meta["driver"]].count()

    # 5 PROCESSOR: the pure build
    built = build(*inputs.values(), meta["params"])

    # 6 keys as of the event
    out = lookup_keys(built, silver[dm["table"]], dm["business_key"], dm["key"], dm["as_of"])

    # 7 completeness: every owed feed has sent its file for the window's day
    got = files.groupBy("file_date").agg(F.collect_set("warehouse").alias("got"))
    owed = F.array(*[F.lit(x) for x in meta["owed_feeds"]])
    out = (out.join(got, out[wcol] == got["file_date"], "left")
              .withColumn("_is_complete", F.coalesce(F.size(F.array_except(owed, F.col("got"))) == 0, F.lit(False)))
              .drop("file_date", "got").withColumn("_run_id", F.lit(run_id)))

    # 8 CHECKS with the row ledger
    ledger = {"read": n_read, "filtered": n_read - n_kept, "after_join": built.count(), "rejected": 0,
              "unknown_keys": out.where(f"{dm['key']} = -1").count(), "written": out.count()}
    problems = check(out, ledger, meta)
    if problems:
        raise RuntimeError(f"{run_id} stopped before writing: {problems}")   # nothing written, watermark unchanged

    # 9 restatements: compare with the last COMMITTED version (a crashed run's half-done write does not count)
    new_s = window_summary(out, meta)
    old_s = window_summary(g.where(F.col(wcol).isin(windows)), meta) if v is not None else {}
    rest = [{"run": run_id, "window": k, "old": old_s[k], "new": v} for k, v in new_s.items() if k in old_s and old_s[k] != v]

    # 10 WRITER: replace only those windows
    replace_windows(spark, out, gold_path, wcol, windows)
    version = DeltaTable.forPath(spark, gold_path).history(1).first()["version"]

    # 11 run log, then move the watermarks LAST
    run = {"run": run_id, "read_from": marks, "read_to": highs, "windows": [str(d) for d in windows],
           "refused_too_old": [str(d) for d in too_old], "ledger": ledger, "restatements": rest, "gold_version": version}
    store.commit(name, highs, run)
    return run
