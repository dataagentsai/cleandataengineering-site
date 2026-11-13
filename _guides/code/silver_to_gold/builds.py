"""PROCESSOR: the pure builds, one per fact. Shown on /learn/silver-to-gold/.

Each build takes DataFrames (and plain settings) and returns a DataFrame.
It never reads a table, never writes, never asks the clock. That is what makes it testable with tiny tables.
"""
from pyspark.sql import DataFrame, functions as F


# 1. Transaction fact: one row per order line, with on-time and in-full flags (OTIF).
def build_otif(lines: DataFrame, deliveries: DataFrame, params: dict) -> DataFrame:
    per_line = (deliveries.groupBy("line_id")                                       # one row per line FIRST,
                .agg(F.sum("qty").alias("qty_delivered"),                           # so the join below can
                     F.max("delivered_date").alias("last_delivered")))              # never multiply lines
    j = lines.join(per_line, "line_id", "left")
    qty_del = F.coalesce("qty_delivered", F.lit(0))
    on_time = F.coalesce(F.col("last_delivered") <= F.col("promised_date"), F.lit(False)).cast("int")
    in_full = (qty_del >= F.col("qty_ordered")).cast("int")
    return j.select("line_id", "dealer_id", "promised_date", "qty_ordered",
                    qty_del.alias("qty_delivered"), on_time.alias("on_time"), in_full.alias("in_full"),
                    (on_time * in_full).alias("otif"))


# 2. Periodic snapshot: stock on hand per warehouse and product at the end of EVERY day, even quiet days.
def build_daily_stock(movements: DataFrame, days: DataFrame, params: dict) -> DataFrame:
    pairs = movements.select("warehouse", "product").distinct()
    grid = pairs.crossJoin(days.select(F.col("day").alias("snapshot_date")))       # a row per pair per day
    m = movements.select("warehouse", "product", "move_date", "qty")
    j = grid.join(m, ["warehouse", "product"], "left")
    upto = F.when(F.col("move_date") <= F.col("snapshot_date"), F.col("qty")).otherwise(0)   # count, never drop, the day
    return (j.groupBy("warehouse", "product", "snapshot_date")
             .agg(F.sum(upto).cast("int").alias("stock_on_hand")))


# 3. Accumulating snapshot: one row per order line, a column per milestone, filled in as milestones happen.
MILESTONES = ["ordered", "shipped", "delivered", "invoiced"]


def build_line_lifecycle(events: DataFrame, params: dict) -> DataFrame:
    p = events.groupBy("line_id").pivot("milestone", MILESTONES).agg(F.min("at"))
    for m in MILESTONES:
        p = p.withColumnRenamed(m, f"{m}_at")
    return p.withColumn("days_to_deliver", F.datediff("delivered_at", "ordered_at"))


# 4. Factless fact: sales-rep visits to dealers. No measures; the row itself is the fact.
def build_visits(visits: DataFrame, params: dict) -> DataFrame:
    return visits.select("rep_id", "dealer_id", "visit_date").dropDuplicates()   # a re-sent visit counts once


# 5. Aggregate fact: OTIF per region per day, built from the atomic gold fact (not from silver).
def build_otif_by_region(fact_otif: DataFrame, dim_dealer: DataFrame, params: dict) -> DataFrame:
    d = dim_dealer.select("dealer_key", "region")
    return (fact_otif.join(d, "dealer_key", "left")
            .groupBy("promised_date", "region")
            .agg(F.count("*").alias("lines"), F.sum("otif").alias("otif_lines"))
            .withColumn("otif_pct", F.round(100 * F.col("otif_lines") / F.col("lines"), 1)))


# 6. Consolidated fact: plan vs actual per dealer per month (two sources brought to one grain).
def build_plan_vs_actual(plan: DataFrame, lines: DataFrame, params: dict) -> DataFrame:
    actual = (lines.withColumn("month", F.date_format("promised_date", "yyyy-MM"))
              .groupBy("dealer_id", "month").agg(F.sum("qty_ordered").cast("int").alias("actual_qty")))
    j = plan.join(actual, ["dealer_id", "month"], "full_outer")
    return (j.select("dealer_id", "month",
                     F.coalesce("plan_qty", F.lit(0)).alias("plan_qty"),
                     F.coalesce("actual_qty", F.lit(0)).alias("actual_qty"))
             .withColumn("gap", F.col("actual_qty") - F.col("plan_qty")))


# 1b. The same transaction fact as SQL. The harness hands the frames over as views; the SQL file is the rule.
def build_otif_sql(lines: DataFrame, deliveries: DataFrame, params: dict) -> DataFrame:
    from pathlib import Path
    lines.createOrReplaceTempView("order_lines")
    deliveries.createOrReplaceTempView("deliveries")
    return lines.sparkSession.sql((Path(__file__).parent / "fact_otif.sql").read_text())


# 7. Versioned fact (writer mode): keep every version of a fact row, like SCD Type 2 but on the fact's grain.
def plan_fact_versions(current: DataFrame, new: DataFrame, keys: list, measures: list, recorded_at) -> tuple:
    """current = open versions in gold; new = rows just built. Returns (keys to close, rows to insert)."""
    cur = current.select(*keys, *[F.col(m).alias(f"_old_{m}") for m in measures])
    j = new.join(cur, keys, "left")
    changed = j.where(" OR ".join(f"NOT (`{m}` <=> `_old_{m}`)" for m in measures))
    to_close = changed.where(F.col(f"_old_{measures[0]}").isNotNull()).select(*keys)
    to_insert = (changed.drop(*[f"_old_{m}" for m in measures])
                 .withColumn("recorded_from", F.lit(recorded_at)).withColumn("recorded_to", F.lit(None).cast("timestamp")))
    return to_close, to_insert


# 8. Adjustment rows (accounting style): never change a row; add the difference as a new row.
def plan_adjustments(published_totals: DataFrame, new: DataFrame, keys: list, measures: list, run_id: str) -> DataFrame:
    old = published_totals.select(*keys, *[F.col(m).alias(f"_old_{m}") for m in measures])
    j = new.join(old, keys, "left")
    diffs = [(F.col(m) - F.coalesce(F.col(f"_old_{m}"), F.lit(0))).alias(m) for m in measures]
    out = j.select(*keys, *diffs).withColumn("_run_id", F.lit(run_id))
    return out.where(" OR ".join(f"{m} != 0" for m in measures))
