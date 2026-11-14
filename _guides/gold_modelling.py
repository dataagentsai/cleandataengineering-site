"""Gold data modelling: dimensional modelling done right. One page at /learn/gold-data-modelling/.

    python3 _guides/gold_modelling.py      (then python3 _site/nav.py and python3 _site/seo.py)

Lesson first (plain words and pictures), then the parts in order: grain, keys, dimensions, facts and how to design
one, the bus matrix, what else lives in gold (aggregates, materialized views, metric views, pre-aggregation level),
physical layout, mistakes, a worked tyre example, decisions with verdicts, FAQ. The silver-to-gold harness has its
own page (_guides/silver_to_gold.py). Databricks facts marked "checked 13 Nov 2026" were run on Free Edition.
"""
import json
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "_paths"))
import components as C  # noqa: E402
from bi_choice import ar, bx, svg, t, vtable  # noqa: E402
from gold_harness_spec import CSS, fig  # noqa: E402
import gold_keys_learn as KL  # noqa: E402

wb = C.wb
SITE = wb.SITE
URL_PATH = "/learn/gold-data-modelling/"
DATE = "2026-11-13"
TITLE = "Gold data modelling: grain, keys, facts and dimensions done right"
DESC = ("How to model the gold layer: declare the grain first, business keys vs primary keys vs surrogate keys, "
        "conformed dimensions and SCD types, every kind of fact table and how to design one, the bus matrix, "
        "aggregate tables, materialized views, metric views and the right level to pre-aggregate, with a worked example.")


# ------------------------------------------------------------------ drawings
def d_star():
    i = bx(390, 110, 220, 110, ["fact: order line", "qty ordered, qty delivered,", "on time in full (0 or 1)"], "y", 15)
    dims = [(60, 20, ["date", "(order, promised,", "delivered)"]), (720, 20, ["dealer", "name, region,", "segment"]),
            (60, 250, ["material", "tyre class, size,", "brand"]), (720, 250, ["plant", "country, time", "zone"])]
    for x, y, lines in dims:
        i += bx(x, y, 220, 80, lines, "g", 15)
    i += ar(390, 140, 282, 75) + ar(610, 140, 718, 75) + ar(390, 200, 282, 275) + ar(610, 200, 718, 275)
    i += t(500, 355, "the fact in the middle holds numbers; each arm points to one dimension by its surrogate key", 13, "middle")
    return svg(1000, 368, "A star: the fact table 'order line' in the middle with quantities and an on-time flag, joined by "
                          "surrogate keys to four dimensions around it: date (used three times: order, promised, delivered), "
                          "dealer, material and plant.", i)


def d_keys():
    i = bx(10, 40, 200, 70, ["source row", "dealer_code D-0042"], "w", 15) + ar(210, 75, 258, 75)
    i += bx(260, 40, 210, 70, ["key map", "D-0042 -> durable 42"], "l", 15) + ar(470, 75, 518, 75)
    i += bx(520, 10, 230, 56, ["version 1: Pune", "sk 701, 2024 to Mar 2026"], "g", 14)
    i += bx(520, 84, 230, 56, ["version 2: Delhi", "sk 702, Mar 2026 to now"], "g", 14)
    i += ar(470, 70, 518, 38) + ar(470, 80, 518, 112)
    i += bx(790, 40, 200, 70, ["fact row stores", "sk 701 or 702 (as of)", "and/or 42 (today)"], "y", 14)
    i += ar(750, 38, 788, 66) + ar(750, 112, 788, 84)
    i += t(500, 150, "business key comes from the source; durable key never changes; version (surrogate) key changes with history", 13, "middle")
    return svg(1000, 162, "Keys: the source's business key D-0042 goes through a key map to durable key 42, which never "
                          "changes. Each SCD2 version gets its own surrogate key: 701 for Pune, 702 for Delhi. A fact row "
                          "stores the version key (values as of its date), the durable key (today's values), or both.", i)


def d_fact_kinds():
    i = ""
    for k, (name, f) in enumerate([("transaction", "y"), ("periodic snapshot", "b"), ("accumulating snapshot", "g")]):
        y = 20 + k * 90
        i += bx(10, y, 190, 60, [name], f, 15)
        i += f'<path d="M230,{y + 30} L980,{y + 30}" stroke="#111" stroke-width="1.2" stroke-dasharray="4 5"/>'
    for x in (260, 330, 345, 470, 520, 640, 700, 715, 860, 930):
        i += f'<circle cx="{x}" cy="50" r="7" fill="#fff6dc" stroke="#111" stroke-width="1.4"/>'
    i += t(600, 92, "one row per event, never changed", 13, "middle")
    for x in (400, 650, 900):
        i += bx(x - 45, 118, 90, 44, ["month end"], "b", 13)
    i += t(600, 180, "one row per thing per period, same shape every period", 13, "middle")
    for k, (x, lbl) in enumerate([(300, "ordered"), (500, "promised"), (700, "shipped"), (900, "delivered")]):
        i += bx(x - 55, 208, 110, 44, [lbl], "g", 13)
        if k:
            i += ar(x - 145, 230, x - 57, 230)
    i += t(600, 274, "one row per thing, updated as it reaches each milestone", 13, "middle")
    return svg(1000, 286, "Three kinds of fact on a timeline. Transaction: one row per event, never changed. Periodic snapshot: "
                          "one row per thing per period, taken at each month end. Accumulating snapshot: one row per thing "
                          "(an order line) updated as it moves from ordered to promised to shipped to delivered.", i)


def d_ladder():
    steps = [("order line", "atomic grain", "y"), ("dealer x material x day", "first aggregate", "b"),
             ("dealer x month", "dashboard tiles", "b"), ("region x month", "executive view", "b")]
    i = ""
    for k, (a, b, f) in enumerate(steps):
        x = 10 + k * 245
        i += bx(x, 30, 220, 70, [a, b], f, 15)
        if k:
            i += ar(x - 24, 65, x - 2, 65, label="add up", lx=x - 13, ly=50)
    i += bx(160, 130, 680, 56, ["ratios (OTIF %, scrap rate) never add up: store the numerator and denominator,",
                                "add those, divide at the end"], "r", 14)
    return svg(1000, 200, "The grain ladder: order line (atomic) adds up to dealer by material by day, then dealer by month, "
                          "then region by month. Ratios such as OTIF % and scrap rate never add up: keep the numerator and "
                          "denominator, add those, and divide at the end.", i)


def d_gold_objects():
    i = bx(10, 70, 200, 100, ["silver", "clean, one row per", "source record"], "w", 15) + ar(210, 120, 248, 120)
    i += bx(250, 20, 230, 200, [""], "y", 14) + t(365, 44, "gold tables", 16, "middle")
    i += bx(268, 62, 194, 44, ["atomic facts"], "w", 14) + bx(268, 116, 194, 44, ["conformed dimensions"], "w", 14)
    i += bx(268, 170, 194, 40, ["aggregate tables"], "w", 13)
    i += ar(480, 120, 518, 120)
    i += bx(520, 20, 220, 92, ["metric views", "one definition per", "measure (semantic)"], "g", 15)
    i += bx(520, 128, 220, 92, ["materialized views", "pre-aggregated,", "refreshed on a schedule"], "b", 15)
    i += ar(740, 66, 778, 66) + ar(740, 174, 778, 174)
    i += bx(780, 20, 210, 200, ["dashboards", "Genie / AI answers", "Power BI", "notebooks, ML", "data sharing"], "l", 15)
    return svg(1000, 232, "What lives in gold: atomic facts, conformed dimensions and aggregate tables are built from silver. "
                          "Above them sit metric views (one definition per measure) and materialized views "
                          "(pre-aggregated, refreshed on a schedule). Dashboards, AI answers, Power BI, notebooks and "
                          "data sharing read from those.", i)


def d_fanout():
    i = bx(10, 40, 230, 70, ["fact: 1 order line", "qty 10, dealer D-0042"], "y", 15)
    i += bx(380, 10, 260, 40, ["D-0042 version 1 (Pune)"], "g", 14)
    i += bx(380, 58, 260, 40, ["D-0042 version 2 (Delhi)"], "g", 14)
    i += bx(380, 106, 260, 40, ["D-0042 version 3 (Goa)"], "g", 14)
    i += ar(240, 75, 378, 30) + ar(240, 75, 378, 78) + ar(240, 75, 378, 126)
    i += t(310, 60, "join on", 13, "middle") + t(310, 76, "dealer_code", 13, "middle")
    i += bx(700, 40, 290, 70, ["3 rows, qty 30", "the total is three times too big"], "r", 15) + ar(640, 78, 698, 75)
    i += t(500, 178, "join on the surrogate key instead: exactly one dimension row per fact row, by construction", 13, "middle")
    return svg(1000, 190, "Fan-out: one order line with quantity 10 joined to the dealer dimension on the business key "
                          "D-0042 matches all three history versions of that dealer, so the result has three rows and a "
                          "quantity of 30. Joining on the surrogate key matches exactly one row.", i)


# ------------------------------------------------------------------ content
KIMBALL = [
    ("Shaping data for questions people ask", "Business processes, grain, facts and dimensions map straight to how people ask", "Pursue: this is Kimball's home ground"),
    ("Many facts that must agree", "Conformed dimensions and the bus matrix make sales, deliveries and returns comparable", "Pursue"),
    ("History of descriptions", "SCD types give a named, tested choice per attribute", "Pursue"),
    ("BI tools, semantic layers and AI answers", "Stars are what metric views, Power BI and text-to-SQL tools read best: few joins, clear names, one grain per table", "Pursue"),
    ("Integrating many messy sources", "Kimball assumes clean, conformed input; matching, deduplicating and keeping source history is silver's job (or a data vault)", "Pursue with care: not the tool for this layer"),
    ("Sub-second or streaming answers", "A star is batch or micro-batch; a live lane needs a store built for it", "Drop for the live lane"),
    ("Machine learning features", "Models want one wide row per entity per time; build it from the star", "Pursue with care: derive, don't replace"),
    ("Exploring unknown data", "Modelling first slows people who don't know the questions yet", "Drop for exploration: let them read silver"),
]

FACT_HISTORY = [
    ("Show values as they were on the fact's date", "Sales by the dealer's region at the time of sale", "Fact stores the dimension's version key (as-of lookup)", "Often called a 'Type 2 fact', but the history lives in the dimension"),
    ("Show today's values for all history", "All past sales under today's regions after a reorganisation", "Fact stores the durable key; join to the current version", "Often called a 'Type 1 fact'"),
    ("Both views", "Finance wants as-it-was, sales wants as-it-is", "Store both keys on the fact; the metric view exposes both", "Cheap: two integer columns"),
    ("The fact's own numbers get corrected, latest is enough", "A delivery quantity fixed next day", "Upsert by grain key: the row is overwritten", "The fact behaves like Type 1"),
    ("The fact's corrections must be auditable", "Prove what the report showed last month", "Versioned fact: new row per change with valid_from and valid_to on the grain key", "The fact behaves like Type 2; expensive, use only when required"),
    ("Corrections must never change a posted row", "Ledgers, invoices", "Reversal rows: a minus row and a plus row", "Totals stay additive; history is the rows themselves"),
    ("Show what the report said on a past day", "Audit of a published month", "Time travel or snapshots of the gold table, or a versioned fact", "Time travel retention is short; keep a snapshot if the period matters"),
]

PATTERNS = [
    ("Count and sum events", "How many tyres did we sell per region per month?", "Transaction fact at event grain; additive measures", "Incremental by event-date window"),
    ("Level at a point in time", "Stock on hand at month end", "Periodic snapshot; semi-additive measure (last value over time)", "Rebuild the open period; freeze closed ones"),
    ("Durations and lags of a process", "Days from order to delivery; how many are late", "Accumulating snapshot with one date per milestone and lag measures", "Upsert by grain key as milestones arrive"),
    ("Things that did not happen", "Dealers with no orders this month; products not sold on promotion", "Factless coverage fact, compared with the event fact", "Rebuild per period"),
    ("Plan against actual", "Sales target vs actual per dealer per month", "Two facts at different grains, drilled across conformed dimensions at the common grain (dealer x month)", "Each fact loads alone; compare in the metric view"),
    ("History as it was", "Revenue by the region a dealer had at the time", "Version key on the fact (as-of lookup); SCD Type 2 dimension", "As-of lookup on event date"),
    ("Restate by today's structure", "Last year's revenue under this year's regions", "Durable key on the fact; current view of the dimension", "No fact change when regions change"),
    ("Late data that changes closed numbers", "A dealer's file arrives five days late", "Window rebuild with a completeness flag; restatement logged", "Lookback window per fact"),
    ("Many-to-many", "An order line credited to two sales reps", "Bridge table with weights that add to 1", "Rebuild the bridge with the dimension"),
    ("Ratios and percentages", "OTIF %, scrap rate", "Store numerator and denominator; define the ratio once in the metric view", "Same as the fact"),
]

JOIN = [
    ("Fact to dimension", "Surrogate key", "Exactly one dimension row per fact row, by construction", "Pursue"),
    ("Fact to dimension on the business key", "Business key", "With SCD2, one fact row matches every version: totals multiply (fan-out)", "Drop"),
    ("Business key plus is_current", "Business key", "Gives today's view, but silently drops facts whose member is no longer current or not yet loaded", "Pursue with care: prefer the durable key"),
    ("Fact to fact (drill across)", "Neither: never join two facts row to row", "Different grains multiply rows (chasm trap)", "Drop: add each up to the common grain on conformed dimensions, then join the results"),
    ("Silver to gold, while building", "Business key, as of the event date", "This is the lookup that turns business keys into surrogate keys", "Pursue: business keys belong to the build, surrogate keys to the readers"),
    ("Gold to an outside system", "Business key", "Other systems do not know your surrogate keys", "Pursue: always keep the business key as a column on the dimension"),
]

JOIN_PROBLEMS = [
    ("Fan-out", "Totals too big after a join", "One fact row matched several dimension rows (business-key join on SCD2, or a dimension that is not unique on its key)", "Join on the surrogate key; check every dimension is unique on it every run"),
    ("Chasm trap", "Orders and deliveries both joined to dealer: totals multiply", "Two facts joined through a shared dimension in one query", "Aggregate each fact to the shared grain first, then join (drill across)"),
    ("Fan trap", "Header amount repeated on every line, summed", "A measure at a coarser grain carried onto a finer grain", "Keep header measures on a header fact, or allocate them to lines"),
    ("Rows silently missing", "Totals too small after a join", "Inner join to a dimension where the member is missing or late", "Unknown member -1 in every dimension; facts never have null keys; use the key, not an inner join on the business key"),
    ("Many-to-many double count", "Commission paid twice", "Order line credited to two reps with no weights", "Bridge table with weighting factors"),
    ("Mixed grain", "Day and month rows in one table; totals double", "Two grains in one fact", "One grain per fact; aggregates in their own tables"),
    ("Grain mismatch across facts", "Plan (monthly) vs actual (daily) compared day by day", "Facts at different grains joined at the finer one", "Compare at the coarser grain only"),
    ("Semi-additive summed over time", "Stock 'total' for the month is thirty times too big", "Daily stock added across days", "Use last value or average over time; the metric view encodes it"),
    ("Ratio averaged", "Average of dealers' OTIF % differs from company OTIF %", "Averaging ratios with different denominators", "Add up numerator and denominator, then divide"),
    ("Time-zone day boundary", "Day totals differ between report and source", "Grain day cut in UTC instead of the business time zone", "Cut business days in the business zone, declared in the contract"),
]

DASH = [
    ("Atomic grain of each fact", "No", "Set by the business process and the source; dashboards come and go"),
    ("Conformed dimensions and keys", "No", "Shared by every fact and every tool"),
    ("SCD type per attribute", "Partly", "Set by what the business must report over time, not by one chart; ask the owner, not the dashboard"),
    ("Measures and their definitions", "No", "Defined once in the metric view; dashboards read them"),
    ("Data quality rules, freshness targets, contracts", "No", "Promises of the data product"),
    ("Aggregate tables and materialized views", "Yes", "Exist only to make named dashboard or AI questions fast or cheap"),
    ("Pre-aggregation grain", "Yes", "Chosen from the grains the top dashboards actually read"),
    ("Refresh cadence of aggregates", "Yes", "Matches how fresh the dashboard must be, never fresher than its inputs"),
    ("Wide flattened tables for a tool", "Yes", "Only for a tool that cannot join"),
    ("Which dimensions a metric view exposes", "Partly", "Business vocabulary first; dashboards may add filters"),
]

MATERIALIZE = [
    ("The same aggregate is read many times a day, and the query is slow or costly", "Materialize (materialized view or aggregate table)"),
    ("Few reads, or reads spread over many different slices", "Do not: let the metric view compute it at query time"),
    ("The atomic fact is small (tens of millions of rows) and clustered well", "Do not: a warehouse answers in seconds anyway"),
    ("Freshness must be minutes, and the base changes all the time", "Do not, or use incremental refresh only: a full refresh each time costs more than the reads save"),
    ("The aggregate needs completeness flags and the same checks as the fact", "Aggregate table in the harness, not a materialized view"),
    ("Plain SQL over gold, refresh on a schedule is fine", "Materialized view (the platform refreshes it)"),
    ("A metric view is slow at the grain dashboards ask most", "Metric-view materialization at that grain"),
    ("Nobody can say which question it speeds up", "Do not"),
]

PREAGG_GRAIN = [
    ("Dashboards show monthly trends by region", "dealer x material x month, or region x month if the region never changes", "Daily stays on the atomic fact for drill-down"),
    ("Daily operational tiles", "plant x material x day", "Hourly drill-down reads the atomic fact"),
    ("Executive summary", "region x month, a handful of rows", "Usually a materialized view is enough"),
    ("AI answers over many slices", "Usually none: the metric view over a well-clustered fact", "Pre-aggregate only the slices query history shows are slow"),
]

FACT_COLUMNS = [
    ("Surrogate keys to each dimension", "dealer_sk, material_sk, order_date_key, promised_date_key", "Yes: the links, small integers, never null (-1, -2)"),
    ("Durable keys, where today's view is needed", "dealer_dk", "When reports need both as-it-was and as-it-is"),
    ("Degenerate dimensions", "order_id, line_no, invoice_no", "Yes: business keys with no table of their own; also the grain"),
    ("Measures", "qty_ordered, qty_delivered, net_value_inr, on_time_in_full (0/1)", "Yes: the reason the fact exists"),
    ("Event timestamps at their natural precision", "order_ts, delivered_ts", "Yes, when lags or hours are asked; the date key covers day-level slicing"),
    ("Lag and duration measures (accumulating snapshots)", "days_order_to_delivery", "Yes: computed once in the build, not in every report"),
    ("Small flags", "is_rush, is_cancelled", "A few are fine; many go into a junk dimension"),
    ("Audit columns", "_run_id, _is_complete, _source_batch", "Yes: lineage, completeness, reruns"),
    ("Descriptive text", "dealer_name, material_description, region", "No: lives in dimensions; copied text means rewriting facts on every rename"),
    ("Business keys of dimensions", "dealer_code", "No as a link; at most kept for traceability on very large facts, never joined on"),
]

SCD2_JOIN = [
    ("Where the as-of join happens", "Once, in the build (silver to gold): business key plus event time finds the version, the fact stores its surrogate key. Readers then join on that key with a plain equality join."),
    ("The rule", "valid_from <= event_time < valid_to: start included, end excluded. The current row has valid_to = 9999-12-31 (or null treated as open), never a gap between versions."),
    ("Which time", "The business event time in the business time zone (order time), not the load time. A late fact must land on the version valid when it happened."),
    ("Event before the member's first version", "Pick a rule and write it down: the first version (most common) or the unknown member. Never drop the row."),
    ("Member not loaded yet", "Unknown member now, re-keyed when it arrives, or an inferred member with a real key filled in later. Both are on the harness page."),
    ("Backdated dimension change", "A version inserted in the past changes which facts belong to it: re-key only the facts of that member in that date range."),
    ("Checks every run", "One current row per member, no overlapping ranges, no gaps, every fact key exists in the dimension. Broken ranges cause fan-out or lost rows."),
    ("Performance", "Look up only the members in the batch; broadcast small dimensions; use a range-join hint or bin by date for large ones; cluster the dimension by business key."),
]

VOLUME = [
    ("Keep the star; integer keys", "Columnar engines and Power BI's engine compress integer keys and low-cardinality columns very well; wide text on facts kills compression.", "Gold"),
    ("Cluster facts by date and the most filtered key", "Queries skip most files; liquid clustering on Delta, sort order on Iceberg; compact regularly.", "Gold"),
    ("Aggregates at the grains people read", "Most dashboard tiles read a few coarse grains; serve them from aggregates or materialized views, keep the atomic fact for drill-down.", "Gold"),
    ("Metric views for definitions", "Every tool asks the same definitions; the warehouse pushes filters and grouping down to clustered tables.", "Semantic"),
    ("Power BI: Import for small and medium models", "Import the dimensions and aggregated facts into the Power BI model; fastest visuals; schedule incremental refresh by date partitions (RangeStart and RangeEnd).", "BI"),
    ("Power BI: DirectQuery for very large or very fresh facts", "Queries go to the warehouse each time; keep visuals few and filtered; never on unclustered, unaggregated tables.", "BI"),
    ("Power BI: composite model with aggregations", "Aggregated table imported, atomic fact in DirectQuery; Power BI answers from the aggregate when it can and goes to the detail only on drill-down.", "BI"),
    ("Power BI model hygiene", "One-to-many relationships from dimension to fact, single direction; a marked date table; remove unused columns; no calculated columns on big facts.", "BI"),
    ("Warehouse settings", "Serverless SQL warehouse with Photon, result cache on, sized for concurrency (scale-out clusters) not for single-query size.", "Platform"),
    ("Row security in one place", "Row filters in the catalog or in the BI model, not both, so caches stay useful.", "Platform"),
    ("Measure before and after", "Query history: slowest and most frequent queries, bytes read; fix the top ten first.", "Operate"),
]

WORDS = [
    ("Gold","The layer people and tools read answers from. Shaped for questions, not for the source system."),
    ("Dimensional model", "Tables arranged as facts (what happened, with numbers) and dimensions (who, what, where, when). Also called a star schema, because one fact with its dimensions looks like a star."),
    ("Business process", "One thing the business does that makes events: taking an order, delivering, curing a tyre. One fact table per process."),
    ("Grain", "What exactly one row of a fact means, in one sentence: \"one row per order line\". The most important decision in gold."),
    ("Measure", "A number on a fact row that people add up or average: quantity, value, minutes late."),
    ("Business key", "The key the source uses for a thing: dealer code D-0042, material code M-1188. Meaningful to people, can be reused or changed by the source."),
    ("Primary key", "Whatever makes a row unique in its table. In a dimension it is the surrogate key; in a fact it is usually the grain columns."),
    ("Surrogate key (sk)", "A meaningless number the warehouse gives each dimension row. Facts point to dimensions with it, never with the business key."),
    ("Durable key", "One number per real-world member (dealer 42) that stays the same across all its history versions."),
    ("Conformed dimension", "A dimension shared, unchanged, by several facts, so their numbers can be compared side by side."),
    ("SCD", "Slowly changing dimension: the rule for what happens when a dimension value changes (overwrite it, keep history, ...)."),
    ("Degenerate dimension", "A business key kept on the fact with no table of its own, such as an order number."),
]

KEYS = [
    ("Business key (natural key)", "Comes from the source; identifies the thing in the source's world", "dealer_code D-0042", "Keep it as a column on the dimension, never as the link from facts"),
    ("Durable key", "One per real-world member, assigned once by a key map, never changes", "dealer 42", "Store on facts that need today's values (current view)"),
    ("Surrogate (version) key", "One per dimension row; with SCD2, one per version", "sk 701 (Pune), sk 702 (Delhi)", "Store on facts that need the values true on the fact's date (as-of view)"),
    ("Dimension primary key", "The surrogate key", "dealer_sk", "Unique, not null, never reused"),
    ("Fact primary key", "The grain columns (often business keys plus dates), or a hash of them", "order_id + line_no", "Declare it and check it every run; a surrogate row id adds nothing"),
    ("Reserved keys", "-1 unknown (the fact had no value), -2 not applicable (the dimension does not apply)", "dealer_sk = -1", "One row each in every dimension, so joins never drop facts"),
]

SK_HOW = [
    ("Key map table (business key -> durable key, assigned once)", "Stable across rebuilds, supports late members, small integers", "Pursue"),
    ("Hash of the business key (SHA-256 or 64-bit)", "No lookup table, same key on every engine and every rerun", "Pursue with care: check for collisions every run at large member counts"),
    ("Identity column (auto-increment)", "Simple", "Drop for history dimensions: a rebuild renumbers everything and breaks facts"),
    ("Source key as the link from facts", "No work", "Drop: breaks with history, with two sources, and when the source reuses keys"),
]

SCD = [
    ("Type 0: keep the original", "The value never changes after first load", "Date of birth, first order date", "Pursue where true"),
    ("Type 1: overwrite", "Only today's value; history lost", "Corrected spellings, contact email", "Pursue for attributes nobody reports on over time"),
    ("Type 2: new row per change", "Full history with valid_from, valid_to, is_current", "Dealer region, material class, price band", "Pursue for attributes reports slice history by"),
    ("Type 3: previous value column", "Current plus one previous value", "Old and new sales territory during a reorganisation", "Pursue with care: one step of history only"),
    ("Type 4 / mini-dimension", "Fast-changing attributes split into their own small dimension", "Customer credit band changing monthly", "Pursue when Type 2 would explode the row count"),
    ("Type 6: 1 + 2 + 3", "Version rows plus a current-value column on every version", "Report history by the region of the day and also by today's region", "Pursue when both views are asked for often"),
    ("Type 2 on every column", "History for everything", "-", "Drop: rows multiply, nobody asks for most of it"),
]

DIMS = [
    ("Date dimension", "One row per day with calendar and fiscal attributes (week, month, quarter, holiday, working day). Used many times on one fact under different names (order date, promised date, delivered date): a role-playing dimension.", "Pursue: every model needs it"),
    ("Conformed dimensions", "Dealer, material, plant built once and used by every fact that mentions them.", "Pursue: it is what makes facts comparable"),
    ("Degenerate dimension", "Order number kept on the fact; no table.", "Pursue for document numbers"),
    ("Junk dimension", "Small flags and codes (rush order, channel, payment type) combined into one tiny dimension instead of many.", "Pursue when a fact has many low-cardinality flags"),
    ("Bridge table", "Many-to-many between a fact and a dimension (one order line, several sales reps with shares).", "Pursue with care: needs weighting factors"),
    ("Outrigger (dimension pointing at a dimension)", "Snowflaking: material -> brand table -> company table.", "Drop mostly: flatten into the dimension unless the sub-dimension is huge and shared"),
    ("Unknown and not-applicable members", "Rows -1 and -2 in every dimension.", "Pursue: no fact is ever dropped by a join"),
]

FACTS = [
    ("Transaction fact", "One event", "One row per order line, payment, sensor reading", "Appended; corrected only by a declared correction rule", "Most common; start here"),
    ("Periodic snapshot", "The state of a thing at the end of each period", "Stock per material per day; account balance per month", "Rebuilt for the open period; closed periods frozen", "For levels and balances"),
    ("Accumulating snapshot", "One thing's whole life, with a date per milestone", "One row per order line with ordered, promised, shipped, delivered dates and lags", "Updated in place as milestones arrive", "For processes with a start and an end"),
    ("Factless fact", "An event or coverage with no number", "Dealer attended a training; product on promotion in a store on a day", "Appended", "For 'what did not happen' questions"),
    ("Aggregate fact", "A coarser grain of another fact", "Dealer x material x day sales", "Rebuilt for changed days only", "Only when the atomic fact is too slow for a named question"),
    ("Consolidated fact", "Two processes at the same grain side by side", "Plan vs actual per dealer per month", "Rebuilt per period", "Only on conformed dimensions"),
]

MEASURES = [
    ("Additive", "Adds up across every dimension", "Quantity, net value, scrap kilograms", "Store as is"),
    ("Semi-additive", "Adds up across some dimensions but not time", "Stock on hand, account balance (add across materials, not across days)", "Store; use last value or average over time"),
    ("Non-additive", "Never adds up", "OTIF %, scrap rate, unit price, averages", "Do not store the ratio as the measure: store numerator and denominator; the metric view divides"),
]

FACT_STEPS = [
    "Name the business process and its owner (taking orders, sales team).",
    "Write the grain in one sentence, at the lowest level the source gives (one row per order line). Atomic grain first; aggregates come later.",
    "List the dimensions that are true at that grain (date, dealer, material, plant). A dimension that is not true for one row means the grain is wrong.",
    "List the measures that are true at that grain, and mark each additive, semi-additive or non-additive.",
    "Pick the fact kind (transaction, periodic snapshot, accumulating snapshot) from how rows change over time.",
    "Decide per dimension: as-of (version key) or current (durable key), or both.",
    "Declare the primary key (the grain columns) and check it is unique on every run.",
    "Declare how late data and corrections arrive: lookback window, correction rule, what happens when a dimension member is missing.",
    "Declare the window column (order date, promised date, cure hour) the harness rebuilds by, and when a window is complete.",
    "Write the contract: columns, types, owner, quality rules, freshness target. Only then write the build.",
]

BUS = [
    ("Order lines (OTIF)", "✓ order, promised, delivered", "✓", "✓", "-", "Transaction (better: accumulating snapshot)"),
    ("Sales (sell-in and sell-out)", "✓ month", "✓", "✓", "-", "Periodic snapshot (monthly)"),
    ("Scrap", "✓ cure hour", "-", "✓", "✓ (via press)", "Periodic snapshot (hourly)"),
    ("Deliveries (proposed)", "✓ shipped, delivered", "✓", "✓", "✓", "Transaction"),
]

OBJECTS = [
    ("Atomic fact and dimension tables", "The star itself", "Every model", "The harness, incremental by window", "Pursue: the source of truth for every number"),
    ("Aggregate table (a gold table at a coarser grain)", "Rows already added up, kept by the harness", "A named question is slow or costly on the atomic fact, and the aggregate is reused", "The harness, changed windows only", "Pursue with care: one more table to keep in step"),
    ("Materialized view", "A query whose result is stored and refreshed by the platform", "The same aggregate is read many times; the logic is a plain SQL query over gold", "The platform, on a schedule or on change (a managed pipeline)", "Pursue for read-heavy aggregates"),
    ("Metric view (semantic layer)", "One definition per measure and dimension; tools ask it questions", "Always, for any number shown to people or AI", "Nothing: it is a definition, computed at query time", "Pursue: one number everywhere"),
    ("Metric view with materialization", "The metric view keeps pre-aggregated results it uses when a query fits them", "A metric view is slow at the grain dashboards ask most", "The platform (a managed pipeline per view)", "Pursue with care: refresh uses compute even when nobody reads"),
    ("Plain view", "A saved query, nothing stored", "Renames, filters, row security", "Nothing", "Pursue for thin layers only"),
    ("Wide 'one big table' for a tool", "Fact joined to all dimensions, flattened", "A tool that cannot join, or a ML feature table", "The harness", "Pursue with care: build it from the star, never instead of it"),
]

PREAGG = [
    ("Look at what is asked", "Take the top dashboards and AI questions; write down the grain each one reads (dealer x month, region x week). Query history tells you."),
    ("Keep the atomic fact", "Never replace it: drill-down, reconciliation and new questions need it."),
    ("Aggregate one step up first", "dealer x material x day usually serves most tiles and cuts rows 10 to 100 times. Go coarser only for a named slow question."),
    ("Only additive measures", "Pre-aggregate sums and counts. For ratios, pre-aggregate the numerator and denominator; divide in the metric view."),
    ("Same dimensions, same keys", "An aggregate uses the conformed dimensions (or their rolled-up versions, such as month instead of date), so it joins like the atomic fact."),
    ("Refresh by changed window", "Recompute only the days or months the atomic fact changed; never the whole table."),
    ("Prove it pays", "Compare query time and compute cost before and after. An aggregate nobody reads is pure cost: drop it."),
]

LAYOUT = [
    ("Conformed dimensions (date, dealer, material, plant)", "<env>_gold.shared", "Owned by the team that masters the data (master data, or the platform team for date); every domain reads, nobody else writes", "Pursue"),
    ("Facts of one business area", "<env>_gold.<domain>: sales, manufacturing, finance", "Owned by the domain team; their metric views and aggregates sit beside them", "Pursue"),
    ("Dimensions only one domain uses", "With that domain's facts", "Move to shared the day a second domain needs them", "Pursue"),
    ("Metric views", "Next to the facts they read, in the domain schema", "Certified views read by dashboards and AI; previews marked", "Pursue"),
    ("Aggregate tables and materialized views", "Domain schema, named agg_<process>_<grain>", "Owned with the fact they come from", "Pursue"),
    ("Cross-domain facts (plan vs actual across finance and sales)", "The domain that owns the decision", "Reads the other domain's facts only through conformed dimensions", "Pursue with care"),
    ("Copies of a shared dimension inside each domain", "-", "Drift: two dealer lists that disagree", "Drop"),
    ("One schema for all of gold", "-", "No ownership, no access boundaries", "Drop beyond a small start"),
]

CLUSTER = [
    ("Transaction fact", "The window column first (order or promised date), then the key most filtered on (dealer_sk)", "Window replaces touch few files; date-range dashboards skip most files"),
    ("Periodic snapshot", "The period (month) and the main key", "Same reason; snapshots are read by period"),
    ("Accumulating snapshot", "The grain key's date (order date) and the main key", "Upserts by grain find their rows fast"),
    ("SCD2 dimension", "Business key (and is_current)", "The build looks up by business key and event time"),
    ("Small dimension (under a few million rows)", "Nothing", "It is broadcast; clustering adds upkeep for no gain"),
    ("Aggregate table", "Its date and its first dimension", "Same as the fact it came from"),
    ("What not to cluster on", "A unique id (order_id) unless people look rows up by it; more than about four columns; columns nobody filters", "High-cardinality ids spread every query; too many keys dilute all of them"),
    ("Let the platform choose", "Automatic clustering where available (Unity Catalog managed tables can pick keys from query history)", "Pursue once query patterns are stable; check what it chose"),
    ("Iceberg note", "On Unity Catalog managed Iceberg we found clustering needs deletion vectors and row tracking turned off when the table is created (checked 13 Nov 2026)", "Set at create; changing later needs a rebuild"),
]

ONTOLOGY = [
    ("Business concepts (Dealer, Material, Plant, Order line, Delivery)", "Dimensions for things, facts for events", "Gold names come from the business, not from source tables"),
    ("Identity of a concept (what makes a dealer one dealer)", "Business keys and the key map", "Two sources that say 'customer' resolve to one member, or are told apart on purpose"),
    ("Relationships (a dealer places order lines; a press cures tyres)", "Fact-to-dimension links and the grain", "Which dimensions are true at a fact's grain is read off the ontology"),
    ("Concepts shared across departments", "Conformed dimensions and the bus matrix", "Sales and manufacturing mean the same 'material'"),
    ("Definitions and synonyms (OTIF, on-time delivery, delivery performance)", "Metric views: descriptions, synonyms, certified measures", "People and AI tools ask in their words and get one definition"),
    ("Rules and constraints (an order line belongs to one order; a delivery cannot precede its order)", "Grain checks, quality rules, as-of rules", "Checks come from business facts, not from guesses"),
    ("Change over time (a dealer can change region)", "SCD type per attribute", "History is kept where the business says the concept changes"),
]

PHYSICAL = [
    ("Clustering", "Cluster facts by the window column and the most filtered key (promised_date, dealer_sk); dimensions by business key and is_current.", "Pursue: liquid clustering on Delta; sort order on Iceberg"),
    ("Partitioning", "Partition only very large facts, and only by a coarse date (month). Small partitions make small files.", "Pursue with care"),
    ("File sizes", "Aim for files of hundreds of megabytes; compact after many small window replaces.", "Pursue: scheduled upkeep"),
    ("Naming", "fact_<process>, dim_<thing>, agg_<process>_<grain>, columns in plain words with units (qty_ordered, value_inr).", "Pursue"),
    ("Comments and contract", "Every table and column described; the grain sentence in the table comment.", "Pursue: AI tools read these"),
    ("Nulls", "No null foreign keys (use -1 or -2); nulls in measures only when truly unknown.", "Pursue"),
    ("Data types", "Exact decimals for money; dates as dates; flags as booleans or plain-word codes.", "Pursue"),
]

MISTAKES = [
    ("Mixed grain in one fact", "Order headers and order lines in one table; totals double count.", "One fact per grain; header values allocated to lines or kept as a separate fact"),
    ("Ratios stored as measures", "Someone averages OTIF % across dealers and gets a wrong number.", "Store numerator and denominator"),
    ("Business key as the fact's link", "History breaks when the dealer moves region; two sources clash.", "Surrogate keys from a key map"),
    ("Type 2 on everything", "Dimension rows explode; nobody reports on most of the history.", "Type 2 only on attributes reports slice by"),
    ("Snowflaked dimensions", "Five joins to get a brand name; slow and confusing for tools and AI.", "Flatten into one dimension"),
    ("No date dimension", "Every report re-derives weeks, fiscal months and holidays differently.", "One shared date dimension, used in roles"),
    ("One big table instead of a star", "Every change to a dimension rewrites billions of fact rows.", "Keep the star; build wide tables from it when a tool needs them"),
    ("Aggregates first", "The atomic detail is never stored; a new question cannot be answered.", "Atomic fact first, aggregates only for named questions"),
    ("Facts reading facts in chains", "Backfills need a careful order; one error spreads.", "Build from silver or from one atomic fact, never three deep"),
    ("Descriptive text on facts", "Dealer names copied onto every fact row; renames need a fact rewrite.", "Text lives in dimensions"),
]

DECISIONS = [
    ("Modelling style for gold", "Dimensional (star) with conformed dimensions", "Pursue"),
    ("Grain", "Atomic first, declared in one sentence, checked every run", "Pursue"),
    ("Keys", "Surrogate keys from a key map; facts store version and/or durable keys; -1 and -2 reserved", "Pursue"),
    ("History", "SCD Type 2 only on attributes reports slice history by; Type 1 elsewhere", "Pursue"),
    ("Date dimension", "One, role-playing", "Pursue"),
    ("Ratios", "Numerator and denominator stored, divided in the metric view", "Pursue"),
    ("Semantic layer", "Metric views over the star, certified measures only for dashboards and AI", "Pursue"),
    ("Pre-aggregation", "Only for named slow questions, one step up first, refreshed by changed window", "Pursue with care"),
    ("Data vault in gold", "Hubs, links and satellites as the reporting layer", "Drop: a fine integration layer, a poor reading layer"),
    ("One big table instead of the star", "-", "Drop"),
]

TYRE = [
    ("fact_otif", "One row per order line", "Transaction, rebuilt by promised-date window (35-day lookback)", "Dealer and material as of the order time; unknown member while a new dealer is missing", "Better as an accumulating snapshot with order, promised, shipped and delivered dates"),
    ("fact_sales", "One row per dealer, material and month (sell-in and sell-out)", "Periodic snapshot, monthly; a month is complete when every dealer that owes a file has sent it", "Dealer and material as of the month", "Late files restate the month; re-sent files change nothing"),
    ("fact_scrap", "One row per press, material and cure hour", "Periodic snapshot, hourly (48-hour lookback)", "Press and material as of the cure hour", "Plant needs its own dimension (time zone)"),
    ("dim_dealer, dim_material, dim_press", "One row per version (SCD Type 2)", "Built through one shared pipeline, no code per dimension", "-", "A date dimension and a plant dimension are missing"),
]

QA = [
    ("What is the right way to model the gold layer?", "Model gold dimensionally: one fact table per business process at a declared atomic grain, conformed dimensions with surrogate keys shared by every fact, SCD Type 2 only where reports need history, ratios stored as numerator and denominator, and a semantic layer (metric views) on top so every tool reads one definition per measure."),
    ("What is the difference between a business key, a primary key and a surrogate key?", "A business key comes from the source (dealer code D-0042). A primary key is whatever makes a row unique in its table. A surrogate key is a meaningless number the warehouse assigns to each dimension row; it is the dimension's primary key, and facts link to dimensions with it, never with the business key."),
    ("What are the kinds of fact table?", "Transaction facts (one row per event), periodic snapshots (one row per thing per period), accumulating snapshots (one row per thing updated at each milestone), factless facts (events with no number), aggregate facts (a coarser grain of another fact) and consolidated facts (two processes at the same grain)."),
    ("How do I define the grain of a fact table?", "Write one sentence that says what one row means, at the lowest level the source provides, such as one row per order line. Every dimension and measure must be true at that grain, and the grain columns become the fact's primary key, checked for uniqueness on every run."),
    ("At what level should I pre-aggregate?", "Keep the atomic fact, then pre-aggregate one step up (for example dealer by material by day) only for named slow questions, using additive measures only (numerator and denominator for ratios), refreshed by changed window, and drop any aggregate nobody reads."),
    ("Should I use materialized views or aggregate tables in gold?", "Use a materialized view when the aggregate is a plain SQL query over gold that is read many times and can be refreshed by the platform; use an aggregate table built by your own harness when it needs the same windows, completeness flags and checks as the atomic fact."),
]


def page():
    url = f"{SITE}{URL_PATH}"
    toc = "".join(f'<li><a href="#{a}">{E(b)}</a></li>' for a, b in [
        ("plain", "In plain words"), ("kimball", "Where Kimball helps, and where not"), ("ontology", "How a business ontology helps"), ("grain", "1. Start with the grain"),
        ("keys-zero", "2a. Keys from zero: one dealer, one story"), ("keys", "2. Keys: business, primary, surrogate"), ("join", "3. Join on surrogate key or business key"),
        ("scd2join", "4. SCD Type 2 joins"), ("dims", "5. Dimensions"), ("dim-kinds", "5a. Kinds of dimension, with examples"), ("bridge", "5b. Bridge tables: why and when"), ("facts", "6. Facts: the kinds"),
        ("factcols", "7. What goes in a fact (only IDs?)"), ("facthist", "8. A 'Type 1 fact' or a 'Type 2 fact'?"),
        ("design", "9. How to design a fact properly"), ("patterns", "10. Requirement patterns and their designs"),
        ("bus", "11. The bus matrix"), ("more", "12. What else lives in gold"), ("dash", "13. What depends on dashboards"),
        ("materialize", "14. Materialize or not"), ("preagg", "15. Pre-aggregate or not, and at what grain"),
        ("volume", "16. Volume: fast Power BI and dashboards"), ("problems", "17. Joining and grain problems"),
        ("schemas", "18. Shared dimensions, domain facts: schemas"),
        ("cluster", "19. Liquid clustering on what"), ("physical", "20. Physical layout"), ("mistakes", "21. Mistakes"),
        ("tyre", "22. Worked example"), ("decide", "23. Decisions"), ("faq", "FAQ")])
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/data-engineering/">Data engineering</a> › Gold data modelling</p>
<p class="eyebrow" style="margin-top:22px">Data engineering · guide</p>
<h1>{E(TITLE)}</h1>
<p class="lede">Gold is where people, dashboards and AI read their answers. If gold is shaped well, every number agrees everywhere and new questions are easy. If it is shaped badly, totals double count, history breaks and every tool invents its own definition. This page teaches the shape from zero, then gives the rules and the decisions. How gold gets built from silver is the next page: <a href="/learn/silver-to-gold/">Silver to gold</a>.</p>
<div class="gh">
<div class="box"><b>In one paragraph.</b> One fact table per business process, at a grain you can say in one sentence. Dimensions around it describe who, what, where and when, and are shared by every fact (conformed). Facts link to dimensions with surrogate keys, never with the source's own keys. History is kept (SCD Type 2) only where reports need it. Ratios are stored as their two parts. A semantic layer (metric views) on top defines each measure once. Aggregates and materialized views are added later, only for questions that are slow, at one step above the atomic grain.</div>
<ul class="toc">{toc}</ul>

<section id="plain"><p class="eyebrow">Lesson first</p><h2>In plain words</h2>
<p>Think of a shop's receipt. The receipt line (2 tyres, ₹9,000) is a <b>fact</b>: it happened, and it has numbers. The shop, the tyre type, the day and the customer are <b>dimensions</b>: they describe the fact, and you slice the numbers by them ("sales by region by month"). Put the fact in the middle and the dimensions around it, and you get a star.</p>
{fig(d_star(), "A star schema. The fact holds numbers; each dimension holds descriptions. The date dimension appears three times, once for each date on the order line.")}
<p>Why this shape? Because almost every business question is "a number, sliced by some descriptions, over time". A star answers that with one join per description, it is easy for people and AI tools to read, and the same dimension can serve many facts, so sales and deliveries can be compared on the same dealer list.</p>
{C.table(["Word", "What it means here"], WORDS)}</section>

<section id="kimball"><p class="eyebrow">Method</p><h2>Where Kimball helps, and where not</h2>
<p>Ralph Kimball's dimensional modelling is the method this page follows: start from business processes, declare the grain, build conformed dimensions, plan with a bus matrix. On a lakehouse it still fits gold, because storage got cheaper but people, BI tools and AI still need clear, small, joinable tables. It is not the tool for every layer.</p>
{vtable(["Need", "Why", "Verdict"], KIMBALL)}</section>

<section id="grain"><p class="eyebrow">1. The first decision</p><h2>Start with the grain</h2>
<p>The grain is what one row of a fact means. Say it in one sentence before anything else: <i>one row per order line</i>, <i>one row per press per hour</i>, <i>one row per dealer per material per month</i>. Most broken gold models broke here: two grains mixed in one table, so totals double count.</p>
<ul><li><b>Atomic first.</b> Choose the lowest level the source gives. You can always add up later; you can never split a total back into its lines.</li>
<li><b>Every dimension must be true at the grain.</b> If "delivery driver" is not known for an order line, it does not belong on the order-line fact.</li>
<li><b>The grain is the primary key.</b> order_id plus line_no; checked for uniqueness on every run, not just in tests.</li>
<li><b>One grain per table.</b> Order headers and order lines are two facts, or header values are shared out onto lines.</li></ul>
{fig(d_ladder(), "Coarser grains are built by adding up the atomic one. Ratios are the exception: add up their parts, then divide.")}</section>

{KL.part_keys()}
<section id="keys"><p class="eyebrow">2. Keys</p><h2>Business key, primary key, surrogate key</h2>
<p>Three kinds of key are easy to mix up. The <b>business key</b> is the source's name for a thing (dealer D-0042). The <b>primary key</b> is whatever makes a row unique in its own table. The <b>surrogate key</b> is a meaningless number the warehouse gives each dimension row, and it is the only thing a fact uses to point at a dimension.</p>
{fig(d_keys(), "The source's code is kept as a column, but facts link through warehouse keys, so history and source changes never break them.")}
{C.table(["Key", "What it is", "Example", "Rule"], KEYS)}
<h3>How to make surrogate keys</h3>{vtable(["Method", "Why", "Verdict"], SK_HOW)}
<p>The details (key maps, version keys, inferred members for late dimensions) are on the <a href="/learn/gold-harness-spec/#keys">gold harness spec</a>.</p></section>

<section id="join"><p class="eyebrow">3. Joining</p><h2>Join on the surrogate key or the business key?</h2>
<p>Short answer: <b>business keys are for building gold, surrogate keys are for reading it.</b> The build looks up each fact's business key (as of its event time) and stores the surrogate key. Every reader then joins fact to dimension on the surrogate key with a plain equality join.</p>
{fig(d_fanout(), "The most common gold bug: a business-key join against a history dimension multiplies every total.")}
{vtable(["Join", "On", "What happens", "Verdict"], JOIN)}</section>

<section id="scd2join"><p class="eyebrow">4. History joins</p><h2>SCD Type 2 joins, done right</h2>
{C.table(["Topic", "Rule"], SCD2_JOIN)}</section>

<section id="ontology"><p class="eyebrow">Meaning first</p><h2>How a business ontology helps</h2>
<p>An ontology is a written map of the business: its concepts (dealer, material, order line), what identifies each one, how they relate, what words mean, and what can change. A good gold model is that map made into tables. Write the ontology (even a light one: a glossary with keys and relationships) and much of the model follows from it; skip it, and each team's gold invents its own meaning of "customer".</p>
{C.table(["In the ontology", "Becomes in gold", "What it buys"], ONTOLOGY)}
<p><b>Verdict.</b> Pursue a light ontology (a glossary of concepts, keys, relationships and definitions kept in Git, feeding the catalog's glossary and the metric views' descriptions). Pursue with care a full ontology platform: worth it when many domains and AI agents must agree on meaning; not as the first step.</p></section>

<section id="dims"><p class="eyebrow">5. Dimensions</p><h2>Dimensions, and how they change</h2>
<p>A dimension is a list of things with their descriptions: one row per dealer, with name, region and segment. When a description changes (a dealer moves region), you must choose what the warehouse remembers. That choice is the SCD type.</p>
{vtable(["Type", "What it keeps", "Example", "Verdict"], SCD)}
<h3>Kinds of dimension</h3>{vtable(["Kind", "What it is", "Verdict"], DIMS)}
<div class="warn"><b>As of then, or as of today?</b> With Type 2, a fact can show the dealer's region on the order date (store the version key) or today's region (store the durable key). Ask which the reports need; many need both, and storing both keys costs little. See <a href="/learn/scd2-auto-cdc-vs-pyspark/">SCD Type 2: AUTO CDC or own PySpark</a> and <a href="/learn/time-travel-vs-scd2/">time travel as SCD2</a>.</div></section>

{KL.part_dims()}
{KL.part_bridge()}
<section id="facts"><p class="eyebrow">6. Facts</p><h2>The kinds of fact table</h2>
<p>Facts differ by how their rows behave over time. Pick the kind from the business process, not from the source table.</p>
{fig(d_fact_kinds(), "Transaction facts collect events, periodic snapshots take a picture every period, accumulating snapshots follow one thing through its milestones.")}
{C.table(["Kind", "One row is", "Example", "How rows change", "When"], FACTS)}
<h3>Measures: what adds up</h3>{C.table(["Kind", "Meaning", "Examples", "Rule"], MEASURES)}</section>

<section id="factcols"><p class="eyebrow">7. Inside a fact</p><h2>What goes in a fact: only IDs?</h2>
<p>Mostly keys and numbers, but not only IDs. A fact holds the keys that place a row (who, what, when), the business keys that name the event itself, the numbers, and a few columns that let the platform prove where the row came from. Descriptions never.</p>
{C.table(["Column kind", "Example", "In the fact?"], FACT_COLUMNS)}</section>

<section id="facthist"><p class="eyebrow">8. A common confusion</p><h2>Is a fact "Type 1" or "Type 2"?</h2>
<p>SCD types belong to dimensions, not facts. When people say "a Type 2 fact" they usually mean one of two different things: <b>which dimension key the fact stores</b> (the version true at the time, or today's), or <b>how the fact's own rows change</b> when the source corrects them (overwritten, versioned, or reversed). Separate the two questions, and each requirement maps to a clear design:</p>
{C.table(["Requirement", "Example ask", "Design", "Note"], FACT_HISTORY)}</section>

<section id="design"><p class="eyebrow">9. Designing a fact</p><h2>How to design a fact properly: ten steps</h2>
<ol class="steps">{''.join(f'<li>{E(s)}</li>' for s in FACT_STEPS)}</ol>
<div class="box"><b>The test of a good fact:</b> you can say its grain in one sentence, every column is either a key, a measure or a degenerate dimension, every measure says whether it adds up, and the harness can rebuild any day of it without touching the others.</div></section>

<section id="patterns"><p class="eyebrow">10. Requirements to design</p><h2>Requirement patterns, and the design for each</h2>
<p>Most gold asks fall into a few patterns. Recognise the pattern in the requirement, and the fact kind, keys and load follow.</p>
{C.table(["Pattern", "The ask", "Design", "Load"], PATTERNS)}</section>

<section id="bus"><p class="eyebrow">11. Planning many facts</p><h2>The bus matrix</h2>
<p>The bus matrix is one table that lists the business processes (rows) against the conformed dimensions (columns). It is the plan for the whole gold layer: it shows which dimensions must be shared, so they are built once. Here it is for a tyre maker.</p>
{C.table(["Process (fact)", "Date", "Dealer", "Material", "Plant", "Fact kind"], BUS)}
<p>A column with many ticks is a dimension to build first and build well. A fact with a tick under a dimension that does not exist yet (plant, date in the example above) is a gap.</p></section>

<section id="more"><p class="eyebrow">12. Beyond facts and dimensions</p><h2>What else lives in gold</h2>
{fig(d_gold_objects(), "Gold tables hold the truth; metric views define the numbers; materialized views keep popular answers ready.")}
{vtable(["Object", "What it is", "Use it when", "Who refreshes it", "Verdict"], OBJECTS)}
<p>On Databricks we checked on Free Edition (13 Nov 2026) that both <code>CREATE MATERIALIZED VIEW</code> and metric-view materialization work; each creates a managed pipeline that refreshes on its schedule and uses compute even when nobody reads. Metric views in full, including materialization: <a href="/learn/metric-views/">Metric views, taught from zero</a>. Power BI's own aggregations and storage modes: <a href="/learn/power-bi-vs-databricks-ai-bi/">Power BI vs Databricks AI/BI</a>.</p></section>

<section id="dash"><p class="eyebrow">13. Requirements that come and go</p><h2>What depends on dashboard requirements, and what does not</h2>
<p>The core of gold follows the business, not the screens. Dashboards change every quarter; if the core changed with them, every number would move. Only the speed layer (aggregates, materialized views, wide tables) is shaped by dashboards.</p>
{C.table(["Part of gold", "Shaped by dashboards?", "Why"], DASH)}</section>

<section id="materialize"><p class="eyebrow">14. Storing answers</p><h2>When to materialize, and when not</h2>
{C.table(["Situation", "Decision"], MATERIALIZE)}</section>

<section id="preagg"><p class="eyebrow">15. Pre-aggregation</p><h2>Pre-aggregate or not, and at what grain</h2>
<p>Pre-aggregation trades storage and refresh compute for faster, cheaper reads. It pays only when the same coarse answer is read many times. When not: the atomic fact is small or well clustered, reads are spread over many slices, or nobody can name the question it speeds up. The rules:</p>
{C.table(["Rule", "What it means"], PREAGG)}
<h3>Which grain</h3>{C.table(["What is asked", "Pre-aggregate at", "Leave on the atomic fact"], PREAGG_GRAIN)}</section>

<section id="volume"><p class="eyebrow">16. Volume</p><h2>Handling volume so Power BI and dashboards stay fast</h2>
<p>Speed comes from layers working together: a clustered star, aggregates at the grains people read, one semantic layer, and a BI model that asks the warehouse for little. No single trick fixes a slow dashboard built on a wide, unclustered table.</p>
{C.table(["Practice", "What to do", "Where"], VOLUME)}
<p>Power BI storage modes, Direct Lake and row security in depth: <a href="/learn/power-bi-vs-databricks-ai-bi/power-bi/">Power BI and Fabric, in depth</a>.</p></section>

<section id="problems"><p class="eyebrow">17. When numbers are wrong</p><h2>Joining and grain problems</h2>
<p>Almost every "the dashboard number is wrong" ticket is one of these. Each has a symptom you can see and a cause you can design away.</p>
{C.table(["Problem", "Symptom", "Cause", "Fix"], JOIN_PROBLEMS)}</section>

<section id="schemas"><p class="eyebrow">18. Where things live</p><h2>Shared dimensions, domain facts: the schema layout</h2>
<p>Organise gold by business area, with one shared home for the conformed dimensions. Ownership follows the schema: whoever owns a schema writes to it, everyone else reads. In our tyre example: <code>dev_gold.shared</code> for date, dealer, material and plant (once they move there; today dealer sits with sales and material with manufacturing), <code>dev_gold.sales</code> for order lines and sales, <code>dev_gold.manufacturing</code> for scrap.</p>
{vtable(["What", "Lives in", "Owner and rule", "Verdict"], LAYOUT)}</section>

<section id="cluster"><p class="eyebrow">19. Clustering</p><h2>Liquid clustering on what?</h2>
<p>Cluster on the columns queries and the harness filter by, in order of how often. For gold that is almost always the window column first, then the most used key.</p>
{C.table(["Table", "Cluster on", "Why"], CLUSTER)}</section>

<section id="physical"><p class="eyebrow">20. Physical layout</p><h2>Layout, names and types</h2>{vtable(["Topic", "Rule", "Verdict"], PHYSICAL)}
<p>Table chores (compaction, clean-up of old files) are on <a href="/learn/table-maintenance/">who maintains your tables</a>.</p></section>

<section id="mistakes"><p class="eyebrow">21. Mistakes</p><h2>Mistakes we see, and the fix</h2>{C.table(["Mistake", "What goes wrong", "Fix"], MISTAKES)}</section>

<section id="tyre"><p class="eyebrow">22. Worked example</p><h2>A tyre maker's gold, as we built it</h2>
<p>Our reference platform builds this gold every day from a simulated tyre company (orders, deliveries, dealer files, presses, lab results) and checks every number against the simulated world's own truth. On Databricks Free Edition on 13 Nov 2026, a 3-day run with eleven planted problems (late files, re-sent files, deleted orders, a dealer that appears late, a backdated correction) gave gold equal to the truth on every day. The last column is what we would change, following this page.</p>
{C.table(["Table", "Grain", "Kind and refresh", "Dimension lookups", "What we would change"], TYRE)}</section>

<section id="decide"><p class="eyebrow">23. Decisions</p><h2>Decisions with verdicts</h2>{vtable(["Decision", "Choice", "Verdict"], DECISIONS)}</section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(QA + KL.QA_EXTRA)}</section>
<section id="next"><p class="eyebrow">Next</p><h2>Where it connects</h2>
<p><b><a href="/learn/silver-to-gold/">Next: Silver to gold, the harness that builds this →</a></b></p>
<p><a href="/learn/gold-harness-spec/">Gold harness spec</a> · <a href="/learn/metric-views/">Metric views</a> · <a href="/learn/scd2-auto-cdc-vs-pyspark/">SCD Type 2 on Databricks</a> · <a href="/learn/medallion-architecture/">Medallion architecture</a> · <a href="/learn/data-platform-architecture/gold/">Hop 3: silver to gold</a> · <a href="/data-engineering/">All data engineering</a></p></section>
</div>"""
    crumbs = [("Data engineering", f"{SITE}/data-engineering/"), ("Gold data modelling", url)]
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": TITLE, "description": DESC, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in QA + KL.QA_EXTRA]}]
    head = CSS + KL.EXTRA_CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(TITLE, DESC, url, body, head)


def main():
    out = ROOT / "learn" / "gold-data-modelling"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("gold data modelling ->", out / "index.html")


if __name__ == "__main__":
    main()
