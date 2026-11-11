"""Gold harness spec: building facts and dimensions from silver as robustly as AUTO CDC. One page at
/learn/gold-harness-spec/.

    python3 _guides/gold_harness_spec.py      (then python3 _site/nav.py and python3 _site/seo.py)

A specification only, no code (the user asked for spec first): plain-words lesson, requirements,
design, low-level design, testing and record-drop checks, decisions with verdicts, open questions.
It builds on the tested SCD2 writer at /learn/scd2-auto-cdc-vs-pyspark/.
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

wb = C.wb
SITE = wb.SITE
URL_PATH = "/learn/gold-harness-spec/"
DATE = "2026-11-11"
VERSION = "0.1 (draft for review)"
TITLE = "Gold harness spec: facts and SCD2 dimensions from silver"
DESC = ("A specification for one harness that builds every gold fact and dimension from silver as robustly as Databricks AUTO CDC: "
        "watermarks, triggers, full or incremental loads, surrogate keys, late dimensions and late facts, pure functions, SCD2 tests and record-drop checks.")

CSS = C.CSS + """<style>
  .gh .fig { border:var(--line); border-radius:var(--wob); padding:12px 14px; margin:16px 0; background:#fff; overflow-x:auto; }
  .gh .fig svg { width:100%; min-width:700px; height:auto; display:block; } .gh .fig text { font-family:var(--hand); fill:#111; }
  .gh .fig p { font-size:13.5px; color:var(--muted); margin:6px 0 0; }
  .gh .box { border:var(--line); border-radius:var(--wob); padding:10px 16px; margin:14px 0; background:var(--butter-wash); }
  .gh .warn { border:var(--line); border-radius:var(--wob); padding:10px 16px; margin:14px 0; background:var(--rose-wash); }
  .gh table.t td { font-size:14px; } .gh td.v { font-weight:700; }
  .gh .toc { columns:2; } @media (max-width:700px){ .gh .toc { columns:1; } }
  .gh ol.steps li { margin-bottom:6px; }
</style>"""


def fig(d, cap):
    return f'<div class="fig">{d}<p>{E(cap)}</p></div>'


# ------------------------------------------------------------------ drawings
def d_overview():
    i = bx(10, 70, 170, 90, ["silver tables", "clean, conformed,", "change feed on"], "w", 14)
    i += bx(230, 20, 420, 190, [""], "y", 14)
    i += t(440, 44, "the gold harness (one code base)", 16, "middle")
    for k, lines in enumerate([["read", "changes since", "watermark"], ["plan", "pure", "functions"], ["check", "nothing", "lost"], ["write", "one", "MERGE"]]):
        x = 245 + k * 100
        i += bx(x, 66, 92, 80, lines, "w", 14)
        if k:
            i += ar(x - 8, 105, x - 1, 105)
    i += t(440, 170, "metadata says what to build; the code says how, once", 13, "middle")
    i += ar(180, 115, 228, 115)
    i += bx(700, 20, 290, 56, ["dimensions", "SCD Type 1 or Type 2"], "g", 14)
    i += bx(700, 92, 290, 56, ["facts", "current view or as-of view"], "b", 14)
    i += bx(700, 164, 290, 46, ["run log · watermarks · rejects"], "l", 13)
    i += ar(650, 60, 698, 48) + ar(650, 115, 698, 120) + ar(650, 170, 698, 187)
    return svg(1000, 222, "Silver tables with change feed on flow into the gold harness, one code base with four steps: read changes since the watermark, plan with pure functions, check nothing was lost, write with one MERGE. It produces dimensions (SCD Type 1 or 2), facts (current or as-of view) and a run log with watermarks and rejects.", i)


def d_asof():
    i = '<path d="M60,120 L960,120" stroke="#111" stroke-width="1.5" marker-end="url(#bia)"/>'
    for x, lbl in [(120, "1 Jan"), (420, "10 Mar"), (760, "1 Sep")]:
        i += f'<path d="M{x},114 L{x},126" stroke="#111" stroke-width="1.5"/>' + t(x, 144, lbl, 13, "middle")
    i += bx(120, 40, 298, 40, ["customer 7 · version 1 · Pune · sk 701"], "w", 13)
    i += bx(420, 40, 338, 40, ["version 2 · Delhi · sk 702"], "g", 13)
    i += bx(760, 40, 200, 40, ["version 3 · Goa · sk 703"], "w", 13)
    i += bx(230, 170, 190, 44, ["order A, 20 Feb"], "y", 13) + ar(325, 168, 280, 82)
    i += bx(500, 170, 220, 44, ["order B, 12 Mar (late)"], "y", 13) + ar(610, 168, 560, 82)
    i += t(500, 244, "as-of view: each order keeps the version valid on its own date. Current view: both show Goa through the durable key.", 13, "middle")
    return svg(1000, 256, "Customer 7 has three SCD2 versions: Pune from 1 January (key 701), Delhi from 10 March (key 702), Goa from 1 September (key 703). Order A on 20 February points to 701; order B on 12 March, even arriving late, points to 702. The current view shows Goa for both through the durable key.", i)


def d_late_dim():
    i = bx(10, 30, 210, 60, ["day 1: order for", "customer 99 arrives"], "y", 14) + ar(220, 60, 268, 60)
    i += bx(270, 30, 230, 60, ["no customer 99 yet:", "add inferred member"], "r", 14) + ar(500, 60, 548, 60)
    i += bx(550, 30, 200, 60, ["order gets sk 990", "now, not later"], "g", 14)
    i += bx(10, 130, 210, 60, ["day 3: customer 99", "lands in silver"], "y", 14) + ar(220, 160, 268, 160)
    i += bx(270, 130, 230, 60, ["fill the inferred row", "in place, keep sk 990"], "g", 14) + ar(500, 160, 548, 160)
    i += bx(550, 130, 200, 60, ["facts need no rework"], "g", 14)
    i += bx(790, 70, 200, 80, ["inferred for more", "than N days?", "raise an alert"], "l", 13)
    return svg(1000, 205, "Late-arriving dimension: on day 1 an order for customer 99 arrives before the customer; the harness adds an inferred member and the order gets key 990 straight away. On day 3 the customer lands; the harness fills the inferred row in place and keeps key 990, so facts need no rework. Members still inferred after N days raise an alert.", i)


def d_run():
    steps = ["lock the table", "fix high mark", "read changes", "plan (pure)", "check balance", "write MERGE", "log + move mark"]
    i = ""
    for k, s in enumerate(steps):
        x = 10 + k * 141
        i += bx(x, 30, 128, 56, s.split(" ", 1) if len(s) > 12 else [s], "y" if k in (3, 4) else "w", 13)
        if k:
            i += ar(x - 12, 58, x - 2, 58)
    i += t(500, 120, "a crash anywhere before the last step: the rerun reads the same range and the write is a no-op or completes", 13, "middle")
    return svg(1000, 134, "One run in seven steps: lock the table, fix the high watermark, read changes, plan with pure functions, check the counts balance, write with one MERGE, then log the run and move the watermark. A crash before the last step is safe: the rerun reads the same range and the write is either a no-op or completes.", i)


# ------------------------------------------------------------------ content
WORDS = [
    ("Fact table", "Things that happened, with numbers: an order line, a sensor reading, a payment. Many rows, mostly added, rarely changed."),
    ("Dimension", "The who, what, where of a fact: customer, product, plant. Few rows, and they change slowly."),
    ("SCD Type 1", "A dimension that overwrites: only the current value is kept."),
    ("SCD Type 2", "A dimension that keeps history: a changed value closes the old row and opens a new one, with valid_from and valid_to."),
    ("Surrogate key (sk)", "A number made by the warehouse to identify a dimension row. Facts store it instead of the source's own key."),
    ("Durable key", "One number per real-world member (customer 7) that never changes across SCD2 versions. Lets a fact show today's values."),
    ("Version key", "One number per SCD2 row (customer 7 as of March). Lets a fact show the values true on its own date."),
    ("As-of lookup", "Find the dimension version whose valid_from and valid_to surround the fact's event date."),
    ("Watermark", "A bookmark per source table: the last change already processed, so the next run reads only newer changes."),
    ("Inferred member", "A placeholder dimension row created when a fact arrives before its dimension; filled in when the real row arrives."),
    ("Harness", "Here: one code base plus metadata that builds every gold table the same way, so robustness is written once, not per table."),
    ("Pure function", "A function whose output depends only on its inputs: no reading tables, no clock, no random numbers inside. Easy to test with small tables."),
]

AUTO = [
    ("Ordering", "SEQUENCE BY orders changes per key", "FR-05: order column per source; ties broken by commit version"),
    ("Duplicates", "Same key and order value applied once", "FR-05: dedupe on key plus order value in the plan"),
    ("Out-of-order events", "Older events are placed correctly in history", "FR-09, FR-10: as-of lookup on event time; backdated dimension changes re-key affected facts"),
    ("Deletes", "APPLY AS DELETE WHEN", "FR-11: delete rule per source (close, soft delete, or reversal for facts)"),
    ("Replays and retries", "Checkpoint makes a batch apply once", "FR-03, FR-12: watermark moves only after a balanced, committed write; reruns are no-ops"),
    ("Incremental reads", "Streams read only new data", "FR-03: change data feed by commit version"),
    ("History protection", "pipelines.reset.allowed = false", "FR-14: full rebuild of an SCD2 target needs an explicit, logged approval"),
    ("What AUTO CDC does not do", "Surrogate keys, fact lookups, inferred members, reconciliation", "FR-06 to FR-10, FR-13: the reason this harness exists"),
]

FR = [
    ("FR-01 Declare, don't code", "Every gold table is described in metadata: kind, grain, keys, sources, lookups, load mode, trigger, checks. Adding a table needs no new code."),
    ("FR-02 Dimensions", "Build dimensions as SCD Type 1 or Type 2 from one or more silver sources, with tracked and untracked columns (untracked change in place, no new version)."),
    ("FR-03 Read only what changed", "Read each silver source incrementally from its watermark using the change data feed, up to a high mark fixed at run start; full read only where FR-04 says so."),
    ("FR-04 Full or incremental", "Each table declares its load mode; the harness applies the rules in the load-mode table, and can force a bounded backfill for a date range."),
    ("FR-05 Order and dedupe", "Each source declares an order column; changes for one key are applied in that order, duplicates once, ties broken by commit version."),
    ("FR-06 Surrogate keys", "Every dimension member gets a durable key and every SCD2 version a version key; both are stable across reruns and rebuilds."),
    ("FR-07 Two fact views", "Each fact lookup declares a mode: current (store the durable key) or as-of (store the version key valid on the fact's event date). A fact may store both."),
    ("FR-08 Fact change modes", "Each fact declares how it changes: append-only events, upsert of current state (accumulating snapshot), versioned (SCD2 on the fact grain), or reversal (correction as minus and plus rows)."),
    ("FR-09 Late-arriving dimension", "A fact whose dimension member does not exist yet gets an inferred member and a key at once; the member is filled in place when it arrives; old inferred members raise alerts."),
    ("FR-10 Late-arriving facts and backdated changes", "Late facts use as-of lookups on their own event date. A backdated SCD2 change re-keys only the affected facts (by key and date range)."),
    ("FR-11 Deletes and corrections", "Each source declares a delete rule: close the dimension row, soft-delete the fact, or post a reversal. Hard deletes for privacy follow FR-15."),
    ("FR-12 Safe to rerun", "Running the same range twice gives the same table. A crash at any step leaves nothing half applied that a rerun cannot finish."),
    ("FR-13 Nothing lost silently", "Each run proves rows in equal rows written, unchanged, rejected and filtered; checks run before the watermark moves; a failed balance stops the run."),
    ("FR-14 Protect history", "A full rebuild of an SCD2 dimension or versioned fact needs an explicit flag, is logged, and keeps key maps so keys do not change."),
    ("FR-15 Privacy deletes", "Remove or mask one person across dimension versions and facts without rebuilding history for everyone."),
    ("FR-16 Fact from another fact", "A fact may read another gold fact only under the rules in the design (published, watermarked, no cycles, same or coarser grain)."),
    ("FR-17 Triggers", "Each table declares its trigger: table update, file arrival, schedule or continuous, following the trigger table."),
    ("FR-18 Run record", "Every run writes one run-log row: source versions read, dimension versions used, counts, checks, duration, cost tags."),
]

NFR = [
    ("Correct before fast", "Invariants (one current row per key, no overlaps, balanced counts) are checked every run, not just in tests."),
    ("Testable without a cluster", "All decisions live in pure functions over small tables; reading and writing are thin adapters. Unit tests run on a laptop in seconds."),
    ("Deterministic", "No current time, random numbers or monotonically_increasing_id inside the plan; the run passes in its run id and run time."),
    ("Portable", "Ports for reader, writer, key service, watermark store and clock. Delta on Databricks first; Iceberg and plain Spark as other adapters."),
    ("Cost bounded", "A run's work grows with the number of changes, not the size of the table; full reads only where declared."),
    ("Observable", "Run log, metrics and lineage per run; failures say which check failed with counts."),
    ("Governed", "Runs as a service principal; Unity Catalog grants; personal data columns tagged in metadata."),
]

TRIGGERS = [
    ("Table update trigger (Lakeflow Jobs)", "The table depends on a few silver tables that update at irregular times; you want gold minutes after silver.", "Pursue for most facts and dimensions"),
    ("File arrival trigger", "The source is files in a volume or S3 path, before silver. Belongs to the silver job, not gold.", "Pursue, upstream of gold"),
    ("Schedule", "Business wants a fixed time (06:00 after close), or many sources must be complete first (period-end facts).", "Pursue for periodic snapshots and finance"),
    ("Continuous or streaming", "Seconds matter and the table is append-only with current-view lookups only.", "Pursue with care: as-of lookups and inferred members are costly per micro-batch"),
    ("Trigger every table on every silver change", "Chatty sources fire runs every minute; cost with little value.", "Drop: add a minimum interval or debounce in the trigger settings"),
]

LOADS = [
    ("Dimension, SCD1 or SCD2", "Incremental from the change data feed", "Full compare only when the source has no change feed (snapshot adapter)"),
    ("Small reference dimension (under about a million rows, no history needed)", "Full overwrite is fine and simplest", "Must still keep its key map so keys do not change"),
    ("Append-only fact (events, readings, transactions)", "Incremental by commit version", "Bounded backfill for a date range when a rule changes"),
    ("Accumulating snapshot fact (order lifecycle)", "Incremental upsert by grain key", "Full rebuild only with FR-14 approval"),
    ("Periodic snapshot fact (month-end balances)", "Full for the period being built, never touching closed periods", "Closed periods are frozen and tagged"),
    ("Aggregate fact built from another fact", "Incremental by affected grain (recompute only changed days or keys)", "Full when the aggregation rule changes"),
    ("Source with no change feed and no reliable timestamp", "Full snapshot compare by hash", "Ask the owner to turn on the change feed: FR-03"),
]

SK = [
    ("Identity column on the dimension", "Simple; numbers are compact", "A rebuild renumbers everything and breaks facts; parallel writers contend", "Drop for SCD2 dimensions"),
    ("Hash of the natural key (64-bit)", "Same key every time, no lookup table, parallel-safe", "Collisions become likely at billions of members (birthday problem); SCD2 version needs key plus valid_from", "Pursue with care: only with a collision check in every run"),
    ("Key map table per dimension (natural key to durable key, assigned once)", "Stable across rebuilds; supports inferred members; compact integers for BI", "One more table and a lookup join", "Pursue: durable keys come from here"),
    ("Version key = hash of durable key and valid_from, or a sequence from the key map", "Stable for the same version on rerun", "Must not change when an inferred row is filled in place", "Pursue"),
    ("Source system's own key as the fact foreign key", "No work", "Breaks with SCD2, mixed sources and key reuse", "Drop"),
]

FACT_FACT = [
    ("Aggregate a fact to a coarser grain (daily sales from order lines)", "Allowed", "Pursue: read the published gold fact incrementally by affected grain"),
    ("Consolidate two facts at the same grain (planned vs actual)", "Allowed, joined on conformed dimension keys and the grain", "Pursue"),
    ("Look up an attribute of another fact row by its business key (order header for order lines)", "Allowed only as a degenerate dimension or through a shared key, never on surrogate row ids", "Pursue with care"),
    ("Chain facts three or more deep", "Hard to backfill and debug", "Drop: build from silver or add a conformed dimension"),
    ("Two facts reading each other", "A cycle", "Drop: the dependency graph must have no cycles"),
    ("Read a fact that has no published watermark or is mid-run", "Reads half a load", "Drop: read only the version recorded as complete in the run log"),
]

LATE = [
    ("Fact arrives before its dimension member", "Inferred member, key now, filled later in place", "Park the fact in a suspense table and retry (delays numbers, needs retry logic)", "Pursue inferred member"),
    ("Fact arrives days late", "As-of lookup on its event date finds the right version", "Lookup on load date (wrong version)", "Pursue as-of"),
    ("Dimension change backdated before facts already loaded", "Re-key queue: affected keys and date range; rework only those facts", "Rebuild the whole fact", "Pursue re-key queue"),
    ("Dimension member deleted at source", "Close the version; facts keep their keys", "Delete the row (orphans facts)", "Pursue close"),
    ("Fact corrected at source", "By fact change mode: upsert, new version, or reversal rows", "Overwrite silently", "Pursue declared mode"),
    ("Event far older than the open period (after month-end close)", "Route to a correction period or a review table per finance rule", "Change a closed period", "Pursue routing"),
]

META = [
    ("table", "Gold table name and owner", "gold.fact_order_line, owner sales-data"),
    ("kind", "dimension or fact", "fact"),
    ("grain", "Columns that make one row unique", "order_id, line_no"),
    ("scd_type / fact_mode", "Dimension: 1 or 2. Fact: append, upsert, versioned or reversal", "upsert"),
    ("sources", "Silver tables, read mode (change feed, snapshot, full), order column, delete rule", "silver.order_line, change feed, order by updated_at, soft delete"),
    ("tracked / untracked", "For SCD2: columns that make a new version, and columns that change in place", "tracked: city, segment"),
    ("lookups", "Per dimension: natural key columns, mode (current, as-of, both), event date column, on missing (inferred, unknown, park)", "customer by customer_id, both, order_date, inferred"),
    ("measures", "Numeric columns and how they add up (additive, semi-additive, non-additive)", "amount additive, stock semi-additive"),
    ("load_mode", "incremental, full, period", "incremental"),
    ("depends_on", "Gold tables that must finish first (dimensions, or facts per the rules)", "dim_customer, dim_product"),
    ("trigger", "table update, schedule, file arrival, continuous; minimum interval", "table update, at most every 15 minutes"),
    ("checks", "Thresholds: unknown key rate, reject rate, count drift, control totals", "unknown key under 0.1 percent"),
    ("layout", "Clustering keys, retention, privacy tags", "cluster by order_date, customer_sk"),
]

STATE = [
    ("watermark", "table, source, last version read, run id, time", "Where each source was read up to. Moved only by a successful run."),
    ("run_log", "run id, table, from and to versions per source, dimension versions used, counts in, inserted, updated, unchanged, rejected, filtered, check results, status, duration", "One row per run; the evidence for every number in gold."),
    ("key_map", "dimension, natural key (as text and hash), durable key, created by run, inferred flag, filled by run", "Durable keys, assigned once."),
    ("rejects", "run id, table, reason, the row as JSON", "Rows that could not be loaded, with why. Counted in the balance."),
    ("rekey_queue", "dimension, durable key, from date, to date, created by run, done by run", "Facts to re-point after a backdated dimension change."),
]

STEPS = [
    "Take a lock for the table (one run at a time per table) and create a run id.",
    "For each source, read the watermark and fix the high mark as the source's current version. The run reads the range after the watermark up to the high mark, and nothing newer, so a rerun reads the same range.",
    "Pin the version of each dimension the run will look up, and record it in the run log. A fact run never sees a dimension half written.",
    "Read the changes from each source for that range (change data feed, or the snapshot adapter). This is the only step that reads tables.",
    "Plan with pure functions: dedupe and order changes, drop no-op changes, build SCD2 versions or fact rows, look up keys (as-of and current), create inferred members, apply delete rules, route rejects. Output: rows to write, key-map additions, re-key requests, rejects, counts.",
    "Check before writing: the counts balance (rows in equal inserted plus updated plus unchanged plus rejected plus filtered), the grain is unique, thresholds hold. Any failure stops the run here, and nothing is written.",
    "Write: key-map additions first, then one MERGE into the target, then rejects and re-key requests. Each write carries the run id, so a retried write is detected and skipped.",
    "Check after writing: SCD2 invariants on the touched keys, control totals against silver for the touched dates.",
    "Write the run-log row and move every watermark to its high mark. Release the lock.",
    "If anything fails before step 9, the watermark has not moved. The rerun reads the same range: the planner's order check and the run-id check make already applied rows a no-op.",
]

PURE = [
    ("plan_dimension", "changes, the target rows for the changed keys, key map rows, the table spec, run id", "rows to write, key-map additions, counts", "No reads, no clock: the run passes run id and run time in"),
    ("plan_fact", "changes, pinned dimension slices for the keys in the batch, key map rows, the table spec, run id", "fact rows, inferred members, rejects, counts", "As-of and current lookups happen here"),
    ("plan_rekey", "re-key requests, affected fact rows, dimension versions", "fact rows with corrected keys", "Same lookup logic as plan_fact, reused"),
    ("balance", "the counts from a plan", "pass or fail with the numbers", "The record-drop proof, as a function"),
    ("invariants", "rows of an SCD2 table for some keys", "a list of broken rules", "Also used by the tests"),
]

TESTS = [
    ("Unit, table-driven", "Every pure function, one row per case: new key, no-op, change, two changes in one batch, delete, delete then re-insert, late event, replay, replay after delete", "Every commit, on a laptop"),
    ("SCD2 invariants", "Exactly one current row per key, no overlapping or gapped ranges, valid_from before valid_to, keys stable across reruns", "Every unit test and every production run"),
    ("Idempotence", "Run the same input twice; the second run changes nothing", "Every commit"),
    ("Order independence", "Split the same changes into batches in different ways; the result is the same", "Every commit (randomized batch splits with a fixed seed)"),
    ("Late data", "Fact before dimension, late fact, backdated dimension change, event after period close", "Every commit"),
    ("Contract tests per port", "Each reader and writer adapter honors the same behavior (Delta, Iceberg)", "On adapter change"),
    ("Integration", "A small Delta lakehouse: silver to gold end to end, including a crash between write and watermark", "Nightly"),
    ("Simulation", "A simulated business with planted incidents (duplicates, late files, deletes), checked against the known truth", "Before release; see DataTwin"),
]

DROPS = [
    ("Count balance", "Rows in equal inserted plus updated plus unchanged plus rejected plus filtered (duplicates, late, no-op), per source, per run", "Fail the run"),
    ("Grain uniqueness", "No two rows share the grain key after the write", "Fail the run"),
    ("Control totals", "Sum of each additive measure per event date, silver against gold, for the touched dates", "Fail above tolerance"),
    ("Unknown and inferred keys", "Share of facts pointing at unknown or inferred members; inferred members older than N days", "Warn, then fail above threshold"),
    ("Orphans", "Fact keys with no dimension row at all", "Fail the run"),
    ("Silver to gold coverage", "Every silver key changed in the range appears in gold or in rejects", "Fail the run"),
    ("Count drift", "Rows per day compared with the same weekday over recent weeks", "Warn"),
    ("Freshness", "Time since the last successful run against the table's agreed delay", "Alert"),
    ("Reject rate", "Rejected rows as a share of rows read", "Warn, then fail above threshold"),
    ("SCD2 invariants after write", "On the keys this run touched", "Fail the run"),
]

DECISIONS = [
    ("Where the robustness lives", "One harness with metadata, not a notebook per table", "Pursue"),
    ("Dimensions with CDC input on Databricks", "AUTO CDC for the SCD2 history, the harness for keys and checks around it", "Pursue with care: two systems; pick one per platform"),
    ("Surrogate keys", "Key map for durable keys, stable version keys", "Pursue"),
    ("Facts store", "Both the version key (as-of) and the durable key (current) where reports need both", "Pursue"),
    ("Late dimension", "Inferred member filled in place", "Pursue"),
    ("Watermark store", "Run-log and watermark tables in the metadata store, moved only after checks pass", "Pursue"),
    ("Trigger default", "Table update trigger with a minimum interval", "Pursue"),
    ("Streaming gold facts with as-of lookups", "Micro-batches with pinned dimension versions", "Pursue with care"),
    ("Fact-to-fact chains three deep", "Not allowed", "Drop"),
]

OPEN = [
    ("Q1 Metadata home", "YAML in Git, or tables in the metadata store (Lakebase or Postgres)? Git gives review; tables give runtime edits. Suggestion: Git is the source, deployed to tables."),
    ("Q2 One engine for SCD2", "Use AUTO CDC for dimension history and the harness only for keys and facts, or the harness for both? Depends on whether the team runs Lakeflow pipelines."),
    ("Q3 Inferred-member age", "How many days before an inferred member fails the run rather than warns?"),
    ("Q4 Closed periods", "Finance rule for events after close: post to the next open period, or a correction period?"),
    ("Q5 Privacy deletes", "Mask in place or delete rows? Affects version keys and control totals."),
    ("Q6 Iceberg", "Is an Iceberg writer needed in year one, or only Delta?"),
]

QA = [
    ("How do I build fact tables from silver robustly, like AUTO CDC?", "Read only changes since a watermark fixed per run, plan in pure functions that order, dedupe and look up keys, prove the counts balance, write with one MERGE carrying the run id, and move the watermark only after the checks pass. A rerun then reads the same range and changes nothing twice."),
    ("Should a fact table store the SCD2 version key or the durable key?", "Store the version key when reports need the dimension values true on the fact's date, the durable key when they need today's values, and both when both are asked for. The durable key comes from a key map and never changes."),
    ("How do I handle a fact that arrives before its dimension?", "Create an inferred member in the dimension with a real surrogate key, load the fact with it, and fill the member in place when the dimension row arrives, keeping the same key. Alert on members still inferred after a set number of days."),
    ("Can a fact table read from another fact table?", "Yes, for aggregates to a coarser grain and consolidations at the same grain, if the source fact is published with a watermark and the dependency graph has no cycles. Avoid deep chains and joins on surrogate row ids."),
    ("When should a gold table use a table update trigger?", "When it depends on a few silver tables that change at irregular times and should follow them within minutes. Use a schedule for period-end facts and add a minimum interval for chatty sources."),
    ("How do I prove no records were dropped?", "Every run checks that rows read equal rows inserted, updated, unchanged, rejected and filtered, that the grain is unique, and that control totals match silver for the touched dates, before the watermark moves."),
]


def page():
    url = f"{SITE}{URL_PATH}"
    toc = "".join(f'<li><a href="#{a}">{E(b)}</a></li>' for a, b in [
        ("plain", "In plain words"), ("why", "Why a harness, and the bar it must meet"), ("req", "1. Requirements"),
        ("design", "2. Design"), ("trig", "2.1 Triggers"), ("load", "2.2 Full or incremental"), ("keys", "2.3 Surrogate keys"),
        ("lookup", "2.4 Current and as-of facts"), ("late", "2.5 Late dimensions and late facts"), ("ff", "2.6 A fact from another fact"),
        ("pure", "2.7 Pure functions"), ("lld", "3. Low-level design"), ("test", "4. Testing"), ("drops", "5. Record-drop checks"),
        ("decide", "6. Decisions"), ("open", "7. Open questions")])
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/data-engineering/">Data engineering</a> › Gold harness spec</p>
<p class="eyebrow" style="margin-top:22px">Data engineering · open specification · version {E(VERSION)}</p>
<h1>{E(TITLE)}</h1>
<p class="lede">One harness that builds every gold dimension and fact from silver, as robustly as Databricks AUTO CDC builds SCD2 tables, and also does what AUTO CDC does not: surrogate keys, fact lookups, late dimensions, late facts and proof that no record was lost. This page is the specification: requirements, design and low-level design. No code yet; code follows once the spec is agreed.</p>
<div class="gh">
<div class="box"><b>In one paragraph.</b> Metadata says what each gold table is. A run reads only the silver changes since its watermark, up to a mark fixed at the start. Pure functions decide everything: order, duplicates, SCD2 versions, key lookups (as-of the fact's date and current), inferred members for late dimensions, rejects. Before writing, the run proves its counts balance. It writes with one MERGE tagged with the run id, then moves the watermark. A crash anywhere is fixed by running again.</div>
<ul class="toc">{toc}</ul>

<section id="plain"><p class="eyebrow">Lesson first</p><h2>In plain words</h2>
<p>Gold is the layer people report from. It has two kinds of table. <b>Dimensions</b> describe things (customers, products, plants). <b>Facts</b> record what happened (order lines, readings, payments) and point at dimensions by key. Building gold means turning clean silver tables into these, every hour or every day, without losing or doubling anything.</p>
{fig(d_overview(), "Silver in, gold out. The harness is the one place where reading, deciding, checking and writing are done right.")}
<p>Two questions decide most of the design. First, does a dimension keep history (SCD Type 2) or only the current value (Type 1)? Second, when a fact points at a dimension that keeps history, should it show the values <i>true on the fact's date</i> or <i>true today</i>? This harness supports both, side by side.</p>
{fig(d_asof(), "The same two orders, two views. As-of: each order sees the city on its own date. Current: both see today's city.")}
{C.table(["Word", "What it means here"], WORDS)}</section>

<section id="why"><p class="eyebrow">The bar</p><h2>Why a harness, and the bar it must meet</h2>
<p>Hand-writing each gold table repeats the same hard problems (ordering, replays, late data, keys) table after table, and each copy fixes them a little differently. AUTO CDC shows what robust looks like for SCD2. This harness must meet that bar for every gold table, and add the parts AUTO CDC does not cover. The SCD2 writer it builds on is tested on <a href="/learn/scd2-auto-cdc-vs-pyspark/">the AUTO CDC or own PySpark page</a>.</p>
{C.table(["Robustness", "What AUTO CDC does", "Where this spec covers it"], AUTO)}</section>

<section id="req"><p class="eyebrow">1. Requirements</p><h2>What it must do</h2>
<h3>Functional requirements</h3>{C.table(["Requirement", "What it means"], FR)}
<h3>Quality requirements</h3>{C.table(["Quality", "What it means"], NFR)}
<h3>Out of scope for version 1</h3>
<ul><li>Building silver from bronze (that is the job of the silver hop).</li><li>Semantic models, metric views and BI (the next hop).</li><li>Sub-second serving (the fast lane on the <a href="/learn/streaming/">streaming page</a>).</li></ul></section>

<section id="design"><p class="eyebrow">2. Design</p><h2>How it is put together</h2>
<p>Three layers. <b>Metadata</b> describes each gold table. A <b>pure core</b> takes small tables in and gives tables out, and makes every decision. <b>Adapters</b> do the reading and writing behind fixed interfaces (ports): a source reader (change feed, snapshot, full), a table writer (Delta MERGE first, Iceberg later), a key service (key map), a watermark store, a clock and a check sink. Swapping Delta for Iceberg means a new adapter, not new logic.</p>
{fig(d_run(), "Every run follows the same seven steps for every table. Only the planning step differs, and it is chosen by metadata.")}
<p>Tables run in dependency order: dimensions before the facts that look them up, and source facts before facts built from them. The orchestrator (Lakeflow Jobs) reads the order from <code>depends_on</code>.</p>

<h3 id="trig">2.1 When to use a table trigger</h3>{vtable(["Trigger", "Use it when", "Verdict"], TRIGGERS)}
<h3 id="load">2.2 Which tables load full and which incremental</h3>{C.table(["Table type", "Default", "Exception"], LOADS)}
<p>The watermark is per gold table and per source, stored as the source's commit version, not a timestamp: versions never tie and never go backwards. The high mark is fixed at run start, so data arriving during the run waits for the next run instead of half joining this one.</p>
<h3 id="keys">2.3 How to create surrogate keys</h3>{vtable(["Option", "Strength", "Weakness", "Verdict"], SK)}
<p>Reserved keys: <b>-1 unknown</b> (the fact had no key value at all) and <b>-2 not applicable</b> (the dimension does not apply to this fact). Inferred members get ordinary keys, flagged in the key map.</p>
<h3 id="lookup">2.4 Facts with current lookups and facts with as-of (SCD2) lookups</h3>
<p>A <b>non-historical fact</b> looks up dimensions by durable key (or a Type 1 dimension's key): reports always show today's values, and a dimension change never touches the fact. A <b>historical fact</b> looks up the SCD2 version valid on the fact's event date and stores its version key: reports show values as they were. Many facts need both, so the spec lets a lookup be <i>current</i>, <i>as-of</i> or <i>both</i>. The as-of lookup is a range join on event date between valid_from and valid_to, run only for the keys in the batch against the pinned dimension version.</p>
<p>The fact itself can also change over time. Four declared modes: <b>append</b> (events never change), <b>upsert</b> (one row per grain holds the latest state, as in an accumulating snapshot of an order's life), <b>versioned</b> (SCD2 on the fact grain, when auditors need every state of the row) and <b>reversal</b> (a correction posts a minus row and a plus row, as finance ledgers require).</p>
<h3 id="late">2.5 Late-arriving dimensions and late-arriving facts</h3>
{fig(d_late_dim(), "The key is given once and never changes; only the placeholder values are filled in later.")}
{vtable(["Case", "Harness behavior", "Rejected alternative", "Verdict"], LATE)}
<h3 id="ff">2.6 Can a fact refer to another fact?</h3>{vtable(["Pattern", "Rule", "Verdict"], FACT_FACT)}
<h3 id="pure">2.7 Pure functions, so it can be unit tested</h3>
<p>Rule: <b>no function that decides anything reads a table, the clock or a random source</b>. The adapters read the data and pass it in; the run passes its id and time in; the functions return rows and counts. Then each hard case is a few rows of input and expected output, tested on a laptop.</p>
{C.table(["Function", "Takes", "Returns", "Note"], PURE)}
<p>Banned inside the core: reading or writing tables, current time functions, random numbers, row ids that depend on partitioning (such as monotonically_increasing_id), and collecting data to the driver.</p></section>

<section id="lld"><p class="eyebrow">3. Low-level design</p><h2>The details</h2>
<h3>Metadata per gold table</h3>{C.table(["Field", "What it holds", "Example"], META)}
<h3>State tables (in the metadata store)</h3>{C.table(["Table", "Columns", "Purpose"], STATE)}
<h3>One run, step by step</h3><ol class="steps">{''.join(f'<li>{E(s)}</li>' for s in STEPS)}</ol>
<div class="warn"><b>Why the watermark moves last:</b> Delta cannot commit two tables in one transaction. So the target write is made safe to repeat (the run id is recorded with the write, and the planner skips changes not newer than what is applied), and the watermark moves only after it. The worst case of a crash is a repeat of work, never a gap.</div>
<h3>SCD2 dimension rules</h3>
<ul><li>Changes per key are ordered by the order column, then commit version; duplicates on key and order value collapse to one.</li>
<li>A change that alters no tracked column makes no version; untracked columns update the current row in place.</li>
<li>Events not newer than the latest applied point for a key, counting closed rows, are skipped and counted as filtered (so a replay after a delete does not bring the member back).</li>
<li>A backdated change (valid_from earlier than the current version) splits the right version and adds a re-key request for facts of that key from that date.</li>
<li>Filling an inferred member is an in-place update of the placeholder row, never a new version.</li></ul>
<h3>Fact rules</h3>
<ul><li>Grain is unique after the write; a second change to the same grain in one batch keeps the latest by order column (upsert mode) or both (versioned mode).</li>
<li>Lookups run against the dimension version pinned at step 3, only for the keys in the batch.</li>
<li>Missing member: inferred, unknown or park, as declared; each counted separately in the run log.</li>
<li>Deletes follow the declared rule; reversal mode never updates a posted row.</li></ul>
<h3>Error handling</h3>
<ul><li>Row-level problems (bad value, missing mandatory key) go to rejects with a reason and count in the balance.</li>
<li>Table-level problems (balance fails, grain broken, threshold crossed) stop the run before any write, and the watermark stays.</li>
<li>Schema change in silver: new nullable columns are added to gold automatically if declared; anything else stops the run and asks for a metadata change.</li></ul>
<h3>Backfill and rebuild</h3>
<ul><li>Backfill is a run with an explicit date range and its own run id; it uses the same plan and checks.</li>
<li>Rebuilding an SCD2 dimension or versioned fact needs the protect-history flag, keeps the key map, and is compared to the old table before swap.</li></ul>
<h3>Performance</h3>
<ul><li>Cluster dimensions by natural key and is_current, facts by event date and the most used key.</li>
<li>Broadcast small dimension slices; use a range-join hint for as-of lookups on large ones.</li>
<li>Each run reads only touched keys and dates from the target.</li></ul></section>

<section id="test"><p class="eyebrow">4. Testing</p><h2>How it is tested, SCD2 first</h2>{C.table(["Test", "What it proves", "When it runs"], TESTS)}
<p>The SCD2 cases already have a working, table-driven example with 11 rows on <a href="/learn/scd2-auto-cdc-vs-pyspark/#tests">the AUTO CDC page</a>; the harness keeps that shape for every pure function. See also <a href="/learn/shift-left/">Shift left</a> for testing without a cluster.</p></section>

<section id="drops"><p class="eyebrow">5. Record-drop and other checks</p><h2>Proving nothing was lost</h2>{C.table(["Check", "Rule", "On failure"], DROPS)}</section>

<section id="decide"><p class="eyebrow">6. Decisions</p><h2>Decisions with verdicts</h2>{vtable(["Decision", "Choice", "Verdict"], DECISIONS)}</section>
<section id="open"><p class="eyebrow">7. Open questions</p><h2>To agree before code</h2>{C.table(["Question", "Options and suggestion"], OPEN)}</section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(QA)}</section>
<section id="next"><p class="eyebrow">Related</p><h2>Where it connects</h2>
<p><a href="/learn/scd2-auto-cdc-vs-pyspark/">SCD2: AUTO CDC or own PySpark</a> · <a href="/learn/data-platform-architecture/gold/">Hop 3: silver to gold</a> · <a href="/learn/data-platform-architecture/metadata-store/">The metadata store</a> · <a href="/learn/time-travel-vs-scd2/">Time travel as SCD Type 2?</a> · <a href="/concepts/scd/">Slowly changing dimensions</a> · <a href="/learn/datatwin/">DataTwin</a> · <a href="/data-engineering/">All data engineering</a></p></section>
</div>"""
    crumbs = [("Data engineering", f"{SITE}/data-engineering/"), ("Gold harness spec", url)]
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": TITLE, "description": DESC, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in QA]}]
    head = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(TITLE, DESC, url, body, head)


def main():
    out = ROOT / "learn" / "gold-harness-spec"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("gold harness spec ->", out / "index.html")


if __name__ == "__main__":
    main()
