"""Silver to gold: the harness that builds the gold star. One page at /learn/silver-to-gold/.

    python3 _guides/silver_to_gold.py      (then python3 _site/nav.py and python3 _site/seo.py)

Follows /learn/gold-data-modelling/ (what to build). This page is how: the harness as built and run in our reference
platform (data-platform-framework, branch w1-core-engine), incremental loading and watermarks, windows and grain,
completeness and restatements, late data, pure functions and local tests on a synthetic world, how the harness
answers each problem, reliability and cost practices. Requirements in full stay on /learn/gold-harness-spec/.
Measured numbers are from runs on 13 Nov 2026 (Databricks Free Edition and a laptop), labelled as such.
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

wb = C.wb
SITE = wb.SITE
URL_PATH = "/learn/silver-to-gold/"
DATE = "2026-11-13"
TITLE = "Silver to gold: the harness that builds facts and dimensions"
DESC = ("How gold is built from silver by one harness: incremental loading with watermarks, rebuilding changed windows at "
        "a declared grain, completeness and restatements, late facts and late dimensions, pure functions tested locally "
        "on a synthetic world, how the harness answers each gold problem, and reliability and cost practices.")


# ------------------------------------------------------------------ drawings
def d_hop():
    i = bx(10, 60, 170, 100, ["silver", "clean rows,", "history kept"], "w", 15) + ar(180, 110, 218, 110)
    i += bx(220, 10, 560, 200, [""], "y", 14) + t(500, 34, "the gold harness: same steps for every table", 16, "middle")
    steps = [["what", "changed?"], ["which", "windows?"], ["build", "(pure)"], ["keys as", "of event"], ["check"], ["replace", "windows"]]
    for k, lines in enumerate(steps):
        x = 232 + k * 91
        i += bx(x, 70, 82, 76, lines, "g" if k == 2 else "w", 14)
        if k:
            i += ar(x - 8, 108, x - 1, 108)
    i += t(500, 186, "metadata says what to build; one small build per fact says how to compute it", 13, "middle")
    i += ar(780, 110, 818, 110) + bx(820, 60, 170, 100, ["gold star", "facts and", "dimensions"], "b", 15)
    return svg(1000, 222, "Silver flows into the gold harness, which runs the same six steps for every table: find what "
                          "changed, work out which windows it touches, run the pure build, look up keys as of the event, "
                          "check, and replace those windows in gold. Metadata says what to build; a small build per fact "
                          "says how.", i)


def d_incr():
    i = '<path d="M40,70 L960,70" stroke="#111" stroke-width="1.5" marker-end="url(#bia)"/>' + t(960, 94, "change sequence", 13, "end")
    for x in range(80, 900, 55):
        f = "#eaf6ef" if 420 < x < 760 else "#fff"
        i += f'<circle cx="{x}" cy="70" r="7" fill="{f}" stroke="#111" stroke-width="1.3"/>'
    i += '<path d="M410,30 L410,110" stroke="#111" stroke-width="2"/>' + t(410, 24, "watermark (last run)", 13, "middle")
    i += '<path d="M770,30 L770,110" stroke="#111" stroke-width="2" stroke-dasharray="5 4"/>' + t(770, 24, "high mark (fixed at start)", 13, "middle")
    i += t(590, 128, "this run reads only these changes", 13, "middle")
    i += bx(120, 150, 300, 60, ["changed rows touch", "promised dates 10, 11 and 14 Nov"], "w", 14) + ar(420, 180, 478, 180)
    i += bx(480, 150, 230, 60, ["+ lookback", "windows 10 to 14 Nov"], "y", 14) + ar(710, 180, 768, 180)
    i += bx(770, 150, 220, 60, ["rebuild only those", "windows from silver"], "g", 14)
    return svg(1000, 222, "Incremental loading. Changes are ordered by a change sequence. The watermark marks the last change "
                          "the previous run used; the high mark is fixed when this run starts. Only the changes between "
                          "them are read. They touch promised dates 10, 11 and 14 November; with the lookback that becomes "
                          "windows 10 to 14 November, and only those windows are rebuilt from silver.", i)


def d_complete():
    i = bx(10, 30, 200, 70, ["October window", "600 dealers owe a file"], "b", 15)
    for k, (lbl, f) in enumerate([("day 1: 599 files", "w"), ("day 2: dealer 42 late", "y"), ("day 3: re-sent copy", "w")]):
        x = 260 + k * 245
        i += bx(x, 30, 220, 70, [lbl], f, 14)
        i += ar(x - 30, 65, x - 2, 65)
    i += t(370, 130, "published, flagged incomplete", 13, "middle") + t(615, 130, "complete; restatement logged", 13, "middle")
    i += t(860, 130, "duplicate skipped; nothing changes", 13, "middle")
    return svg(1000, 145, "Completeness. October is owed a file by 600 dealers. Day 1: 599 files arrive, so October is "
                          "published but flagged incomplete. Day 2: dealer 42's late file arrives, October becomes complete "
                          "and the change is logged as a restatement. Day 3: a re-sent copy is skipped and nothing changes.", i)


def d_pure():
    i = bx(10, 40, 200, 80, ["adapter reads", "silver frames"], "w", 15) + ar(210, 80, 278, 80)
    i += bx(280, 20, 300, 120, ["build(inputs, params)", "-> rows", "no reads, no writes,", "no clock, no random"], "g", 15)
    i += ar(580, 80, 648, 80) + bx(650, 40, 200, 80, ["adapter writes", "gold windows"], "w", 15)
    i += bx(280, 170, 300, 60, ["tests: small tables in,", "expected rows out"], "y", 14) + ar(430, 168, 430, 142)
    i += bx(650, 170, 340, 60, ["same tests on Spark and DuckDB,", "a laptop, in seconds"], "y", 14)
    return svg(1000, 242, "Pure functions. An adapter reads silver frames and hands them to build(inputs, params), which only "
                          "returns rows: no reads, no writes, no clock, no random numbers. Another adapter writes the gold "
                          "windows. Tests feed small tables in and compare the rows out, and the same tests run on Spark and "
                          "DuckDB on a laptop in seconds.", i)


# ------------------------------------------------------------------ content
STEPS = [
    "Read each input's watermark from the metadata store and fix a high mark for this run. Changes that arrive during the run wait for the next one.",
    "Read only the silver changes between the watermark and the high mark (change sequence, file list, or commit version, per input).",
    "Turn changed rows into changed windows: the window column of each changed row (promised date, sale month, cure hour), widened by the lookback the fact declares.",
    "Overlay any correction plan due today (records from a corrections table, never edits in the source).",
    "Run the fact's build for those windows: a small SQL file or PySpark function, pure, reading only the frames it is given.",
    "Look up surrogate keys as of each row's event time; a missing member gets the unknown key (-1) and is counted.",
    "Mark each window complete or not: every input has loaded past the window's end, and every feed that owes data has sent it.",
    "Check before writing: grain unique, rows in equal rows out, totals reconcile with silver, unknown-key rate under its limit. A failure stops here; nothing is written.",
    "Replace only the windows whose numbers changed. A window published before and now different is logged as a restatement.",
    "Write the run log and move each watermark to its high mark. Last, and only on success.",
]

INCR = [
    ("Facts", "Rebuild changed windows from silver", "A window is small (a day, a month, an hour), rebuilt whole, so the write is idempotent and needs no row-by-row MERGE"),
    ("Dimensions (SCD Type 2)", "Through one shared dimension pipeline; replace the dimension when it changed", "Dimensions are small; history comes from silver's SCD2 rows, keys from the key map stay stable"),
    ("Very large dimensions", "MERGE only changed members", "Worth it above tens of millions of members"),
    ("Aggregate tables", "Rebuild the windows the atomic fact changed", "Same windows, same checks"),
    ("Full rebuild", "Only on a declared backfill, with its own run id and the same checks", "Never as the daily default: cost grows with history, not with change"),
]

WATERMARK = [
    ("What it is", "A bookmark per gold table and per input: the last change this table has already used. Stored in the metadata store's run log, never in a notebook or a file."),
    ("What it is measured in", "A value that only goes up and never ties: a change sequence from the source, a table commit version, an ordered file list, an API cursor. Timestamps tie and go backwards with clock skew; use them only when nothing better exists, with an overlap and a dedupe."),
    ("Fixed high mark", "Fixed at the start of the run, so the run reads a closed range and a rerun reads the same range."),
    ("Moves last", "Only after the write and the checks succeed. A crash before that repeats work; it never leaves a gap."),
    ("Never past unsaved data", "If a window was held back (incomplete, failed check), the watermark does not pass it."),
    ("Second job: completeness", "An input's watermark says how far its data is loaded. A window is complete when every input's watermark is past the window's end."),
    ("Reset is an event", "Moving a watermark back (to reload) is a logged action with a reason, never a silent edit."),
]

WINDOWS = [
    ("Window column", "The date that decides where a row belongs in gold: promised date for OTIF, sale month for sales, cure hour for scrap."),
    ("Window size", "The grain of time the fact is rebuilt in: day, month or hour. Usually the time part of the fact's grain."),
    ("Lookback", "How far back a late or changed row may still land (35 days for OTIF, 3 months for sales, 48 hours for scrap). Changes older than that go through a correction plan."),
    ("Replace, not merge", "The whole window is recomputed and replaced. Running it twice gives the same table; a deleted source row disappears without a delete rule."),
    ("On incomplete", "Publish the window flagged incomplete (readers see it is not final), or hold it until complete. Declared per fact."),
    ("Restatement", "A window that was published and later changes is recorded with its old and new numbers, the reason (late data or a correction plan) and the run."),
]

LATE = [
    ("Late fact inside the lookback", "Its window is rebuilt; the change is a restatement if the window was already published", "Late sensor readings, a delivery recorded a day late"),
    ("Late fact outside the lookback", "Goes through a correction plan with the windows it may touch, approved and dated", "A promised date corrected after the month closed"),
    ("Late feed (a file per dealer)", "The window stays incomplete until every feed that owes data has sent it, then completes and restates", "One dealer's October file arrives late"),
    ("Re-sent file", "Refused at landing as a duplicate; gold does not change and nothing is restated", "The same file sent twice under a new name"),
    ("Dimension member arrives after its facts", "Facts get the unknown key (-1) and are counted as orphans; re-keyed in the run where the member appears", "Orders for a new dealer before the dealer list has it"),
    ("Source deletes", "Silver marks the row deleted; the window rebuild leaves it out of gold", "Cancelled order lines hard-deleted at source"),
]

PURE = [
    ("The build is a function", "build(inputs, params) takes the input frames and returns the fact's rows. It reads nothing, writes nothing, never asks the clock or a random source."),
    ("I/O lives in adapters", "Reading silver and writing gold windows sit behind ports (reader, table writer, metadata store). Swapping Delta for Iceberg or Spark for DuckDB is a new adapter, not new logic."),
    ("Same code, several engines", "The same stage and build tests run on Spark and on DuckDB (through SQLFrame): DuckDB on every push in about two minutes with no Java, Spark nightly and on Databricks."),
    ("Table-driven tests", "Each case is a few input rows and the expected output rows: new member, late fact, deleted line, duplicate, window straddling a month."),
    ("A synthetic world", "A seeded generator plays a whole company (orders, deliveries, dealer files, presses, lab results) and keeps its own truth (the oracle): what gold must hold on each day."),
    ("Planted incidents", "The world plants problems on a calendar: late files, re-sent files, deletes, a dealer that appears late, an out-of-order change, a backdated correction. Each names the check that must catch it."),
    ("Compressed calendar", "For the daily loop, every incident is moved into three days, so a short run meets all of them."),
    ("Compare layer by layer", "After each simulated day, bronze, silver and gold are compared with the oracle; a difference fails the run and names the layer."),
]

SOLVES = [
    ("Double counting from joins", "Keys are looked up once in the build; facts carry surrogate keys; grain uniqueness checked every run", "Grain check"),
    ("Duplicates and replays", "Duplicates dropped in silver; gold windows are replaced whole, so a rerun is a no-op", "Stream replay incident (DUP-04)"),
    ("Re-sent files", "Refused at landing; gold unchanged, nothing restated", "Re-sent file incident (DUP-01)"),
    ("Late data", "Changed windows with a lookback; completeness flags; restatements logged", "Late file incident (LATE-01)"),
    ("Late dimension members", "Unknown member (-1), counted, re-keyed when the member appears", "Late dealer incident (LATE-02)"),
    ("Source deletes", "Soft delete in silver, window rebuild in gold", "Deleted lines incident (DEL-01)"),
    ("Out-of-order history", "Silver orders SCD2 by the source's change sequence; gold looks up as of the event", "Out-of-order change incident (SCD-02)"),
    ("Corrections to closed periods", "A correction plan touches only its declared windows", "Backdated correction incident (HIST-05)"),
    ("A crash halfway", "Watermark moves last; window replace is idempotent", "Rerun tests"),
    ("Silent loss", "Rows in equal rows out; totals reconcile with silver; unknown-key rate limited", "Reconciliation checks"),
    ("Cost creep", "Only changed windows are rebuilt; work grows with change, not history", "Run log timings"),
    ("Every table done differently", "One harness, metadata per table, one small build per fact", "Code review: the build is the only per-fact code"),
]

RELIABILITY = [
    ("Idempotent writes", "Replace whole windows; never append to gold", "A retry or rerun never doubles a number"),
    ("Watermark moves last", "After write and checks, in the metadata store", "A crash repeats work, never skips it"),
    ("Pinned inputs", "Fix the high mark per input at run start", "A run reads a closed range; reruns match"),
    ("Check before publish", "Grain, balance, reconciliation, thresholds before the write", "Bad windows never reach readers"),
    ("Completeness on every row", "_is_complete per window, visible to readers and metric views", "Nobody mistakes a partial month for a final one"),
    ("Run log per run", "Inputs and ranges read, windows rebuilt, counts, checks, restatements, time", "Every number has evidence"),
    ("One writer per table", "A lock or a single job per gold table", "No two runs fight over a window"),
    ("Dependency order", "Dimensions before facts; facts before aggregates", "Lookups always see finished dimensions"),
    ("Backfill is a run", "A date range with its own run id, same plan, same checks", "No special scripts that skip the rules"),
    ("Tested on a world, not only units", "Daily runs on the synthetic world with planted incidents", "The whole hop is proven, not just functions"),
]

COST = [
    ("Rebuild changed windows only", "Work follows the number of changes, not the size of history"),
    ("Right-size the lookback", "Each extra day of lookback is rebuilt every run; set it from how late data really arrives"),
    ("Cluster by the window column", "A window replace touches a few files, not the whole table"),
    ("Broadcast small dimensions", "Key lookups without shuffling the fact"),
    ("Trigger on change, with a minimum interval", "No run when silver did not change; no run every minute for a chatty source"),
    ("Regular upkeep", "Window replaces leave small files and old snapshots; compact and expire on a schedule (we run it every seven days)"),
    ("Serverless for spiky loads", "No idle cluster between runs; classic clusters only for steady heavy loads"),
    ("Tag every run", "Domain, table and run id on the job, so the cost of each table is visible"),
    ("Aggregates only where read", "A materialized view or aggregate nobody queries is refresh cost with no benefit"),
]

ONE_HARNESS = [
    ("Transaction fact", "Replace changed windows of the event date", "Built (order lines, scrap)"),
    ("Periodic snapshot", "Rebuild the open period; closed periods frozen; completeness per period", "Built (monthly sales)"),
    ("Accumulating snapshot", "Upsert by grain key as milestones arrive (the one mode that MERGEs rows)", "Owed: a declared fact mode"),
    ("Factless fact", "Same as transaction, with no measures", "Same code path"),
    ("Aggregate fact", "Rebuild the windows its source fact changed", "Same code path, input is a gold fact"),
    ("Consolidated fact (plan vs actual)", "Each input added up to the common grain in the build", "Same code path"),
    ("Dimensions", "One shared dimension pipeline, no code per dimension", "Built"),
    ("Bridge tables with weights", "Built with their dimension; weights checked to add to 1", "Owed"),
]

SQL_VS_DF = [
    ("Readable by analysts and reviewers", "Yes: the logic reads like the question", "Harder: chained calls, Python around it", "SQL"),
    ("Run a piece of it by hand", "Paste a CTE into a SQL editor and look", "Needs a notebook and the input frames", "SQL"),
    ("Complex logic (sessions, allocations, loops over rules, reuse)", "Gets long and repetitive", "Functions, parameters, reuse, unit tests per function", "PySpark"),
    ("Unit tests with small tables", "Possible: register small tables as views, run the SQL", "Natural: pass DataFrames in", "Both"),
    ("Same code on Spark and DuckDB", "Mostly (a common SQL subset)", "Yes through SQLFrame, with known gaps", "Both, tested on both"),
    ("Static checks before running", "SQL linters and parsers", "Ruff, mypy and pure-function checks", "Both"),
    ("Performance", "Same engine underneath; the optimizer sees all of it", "Same; watch for Python UDFs and collect()", "Even"),
]

INSPECT = [
    ("Each SQL build is a file of named steps (CTEs)", "Run any step alone in a SQL editor against the same inputs", "Built: fact_otif.sql, fact_sales.sql"),
    ("The harness logs the exact SQL it ran, with the window values filled in", "Copy, paste, run", "Proposed"),
    ("Inspect mode for one run and a few windows", "Every step's output saved to a scratch schema keyed by run id: changed rows, windows, build output before and after key lookup, rows rejected, check results", "Proposed: off by default, sampled, auto-dropped after a few days"),
    ("Replay one window locally", "The run log holds the input ranges; a command rebuilds that window on a laptop from a copy of those inputs", "Proposed"),
    ("Row counts per step in the run log", "See where rows were added or lost without rerunning", "Built for silver stages and gold totals; per-join counts proposed"),
    ("Checks name their rows", "A failed check lists sample keys, not just a count", "Partly built"),
]

LEDGER = [
    ("Rows read per input", "Rows in the changed range of each input", "Reading"),
    ("Filtered", "Rows removed by a declared filter (cancelled, test dealers), counted per filter name", "Build"),
    ("After each join", "Rows out against rows in, per join; a lookup join must never add rows and never lose rows", "Build"),
    ("Unknown keys", "Rows given -1 because the member is missing, per dimension", "Key lookup"),
    ("Rejected", "Rows that broke a rule, with the reason, in a rejects table", "Checks"),
    ("Written", "Rows in the replaced windows", "Write"),
    ("The balance", "Rows read = filtered + rejected + written (or the aggregate's declared rule); totals of each measure equal silver's for the same windows", "Before publish"),
]

M2M = [
    ("Before the join", "Check the dimension side is unique on the join key (one row per surrogate key, or per business key and version range)", "Stops the run and names the duplicate keys"),
    ("At the join", "Count rows out against rows in; for a lookup join they must be equal", "Fails the build step that grew"),
    ("SCD2 ranges", "No overlapping valid_from / valid_to for a member, checked every run", "An overlap would match two versions"),
    ("Real many-to-many", "Model it with a bridge table and weights that add to 1", "Totals stay right when an order line has two sales reps"),
    ("Grain after the build", "The fact is unique on its grain columns", "Catches anything that slipped through"),
]

GENERIC = [
    ("Reading changes, watermarks, high marks", "Generic", "Same for every table"),
    ("Windows, lookback, window replace", "Generic, configured", "Window column and lookback are metadata"),
    ("Surrogate keys, as-of lookups, unknown and inferred members", "Generic, configured", "Which dimensions and how: metadata"),
    ("Completeness, restatements, correction plans", "Generic, configured", "Which inputs owe data per window: metadata"),
    ("Checks, row ledger, run log, upkeep", "Generic, configured", "Thresholds per table: metadata"),
    ("Dimensions", "Generic", "One shared pipeline; a new dimension is metadata only"),
    ("Grain, measures, fact kind", "Per fact, declared", "Metadata, not code"),
    ("The business rule itself (what counts as on time, how a discount is shared out, which orders are open)", "Per fact, code", "A small SQL file or PySpark function; the only hand-written part"),
]

REGRESSION = [
    ("Unit tests on each build", "Table-driven cases: small tables in, expected rows out, on Spark and DuckDB", "Every commit", "Built"),
    ("Generated files unchanged unless meant", "Metric views, dashboards, bundle files are generated and compared with the committed copies; any drift fails", "Every commit", "Built"),
    ("Known answers", "Fixed questions (OTIF for one region and month) asked of the metric views; the answer must equal the expected number", "Every run", "Built"),
    ("The synthetic world, every incident", "Three compressed days with eleven planted incidents; every layer must equal the world's truth", "Every change to the harness or a build; daily on the platform", "Built"),
    ("Side-by-side data diff", "Run the new version on the same inputs into a scratch schema; compare with today's gold per window: row counts, keys, measure totals; any difference must be explained before release", "Before every release that touches a build or metadata", "Proposed"),
    ("Speed and cost", "Step times and rows per step from the run log, compared with the last runs; a step twice as slow is flagged", "Every run", "Partly built (timings logged; comparison proposed)"),
    ("Release gate", "A change ships only when all of the above pass; a planted bad change must be blocked", "Every release", "Built for the observability gate; extend to gold builds"),
]

HISTORY = [
    ("Load silver's history first", "Years of source history land in bronze and silver once (snapshots, history tables or a full extract); SCD2 dimensions are built from it with their real valid_from dates", "Facts can only look up versions that exist"),
    ("Build gold with the same harness, period by period", "A backfill run per month (or quarter), oldest first, with its own run id, the same build and the same checks", "No special one-off scripts that skip the rules"),
    ("Dimensions before facts", "Every dimension holds its full history before any fact is looked up against it", "As-of lookups land on the right version"),
    ("Size compute for the load, then shrink", "A bigger cluster or more parallel periods only for the history load", "History is a one-time cost; do not keep paying it"),
    ("Reconcile with the old system", "Per period: counts and totals against the legacy warehouse or finance close", "Proves the history before anyone reports on it"),
    ("Quiet the alarms", "Restatement and freshness alerts off for backfill runs (still logged)", "A history load is not an incident"),
    ("Freeze closed periods", "Mark periods already closed by finance as frozen once reconciled", "Later loads cannot move them by accident"),
    ("Hand over to incremental", "Set each input's watermark to the point the history load read up to, in the same logged step, then start the daily runs", "No gap and no overlap between history and daily loads (our harness owes a written rule for this step)"),
]

RELOAD = [
    ("Gold build was wrong (a rule or a bug)", "Fix the build; backfill the affected windows from silver", "Silver"),
    ("Silver was wrong (a stage or a setting)", "Rebuild silver from bronze for the affected batches, then rebuild the gold windows they touch", "Bronze"),
    ("A file was landed wrong", "Re-land it from the landing archive, then silver and gold", "Landing archive"),
    ("The source sent wrong data", "Ask the source to resend (or re-extract); the new delivery flows through normally", "Source"),
    ("Rules for every reload", "A logged backfill run with a reason; watermarks moved back only as a logged event; restatements logged; a data diff against current gold before the swap", "-"),
]

BAD_BATCH = [
    ("Stop it before readers see it", "Checks run before publish: a failing batch writes nothing and the watermark stays", "Best: built"),
    ("Void the batch", "Mark the batch void in the metadata store; every row carries its batch key, so silver is rebuilt from bronze without it", "Built in silver (void plus rebuild)"),
    ("Rebuild the gold windows it touched", "Lineage from batch to windows says which; the harness rebuilds just those and logs the restatement", "Owed: the gold rerun after a silver rebuild"),
    ("Hide it at once, while the rebuild runs", "Views and metric views filter out rows of void batches, or the windows are flagged 'under review' so readers see the number is not final", "Proposed"),
    ("Roll the table back (time travel restore)", "Fast, but it also undoes every good batch after the bad one", "Pursue with care: emergencies only"),
    ("Delete the rows by hand", "No record of why; the next run may bring them back", "Drop"),
]

ISOLATE = [
    ("The build sees only frames and parameters", "build(inputs, params) gets the input DataFrames (or SQL views) and settings; it cannot read a table, write, or ask the clock. Everything else is the harness's job."),
    ("The harness never knows the business", "No dealer, OTIF or tyre word in the harness code; a test fails the build if one appears."),
    ("Shape is metadata, not code", "Grain, window, lookback, inputs, lookups, checks: one file per gold table, validated when loaded."),
    ("Separate folders, separate owners", "Harness in the platform package (platform team); builds in models/<domain>/gold/ (domain team). A change to the harness needs the platform's review; a change to a build needs the domain owner's."),
    ("Separate tests", "Harness tests use made-up tables of any shape; build tests use the domain's small tables and expected rows; the synthetic world tests both together."),
    ("A contract between them", "The build declares the columns it returns; the harness checks them against the gold contract before keys are looked up."),
]

READS = [
    ("Transactional tables with a change feed (order lines, deliveries, production)", "Incremental: rows changed since the watermark, by change sequence", "Then the whole changed windows are recomputed from silver's current rows"),
    ("Event streams (sensor readings)", "Incremental: by arrival or commit, mapped to event-time windows with a lookback", "Late events inside the lookback rebuild their window"),
    ("File-per-period feeds (a dealer's monthly file)", "Incremental per feed: each feed's newest file is a mark; a window waits until every owed feed has delivered", "Re-sent copies are refused before silver"),
    ("Small dimensions' sources (dealers, materials, presses)", "Full read of silver's current and history rows: small, so a full read is cheaper than tracking changes", "Switch to incremental above tens of millions of members"),
    ("Dimension slices during a fact build", "Only the members whose keys appear in the changed rows, as of their event times", "Broadcast when small"),
    ("Full daily copies from the source (a materials copy)", "Silver turns the copy into changes; gold reads silver like any other table", "A short copy is held in bronze, never passed on (mass-delete guard)"),
    ("Gold facts read by aggregates", "Incremental: the windows the atomic fact changed in this run", "Never the whole fact"),
    ("Backfill, history load, rule change", "Full for a declared date range, through the same harness", "Logged, checked, compared before release"),
]

STATUS = [
    ("The harness: windows, keys as of event, completeness, checks, restatements, run log", "Built", "Gold equal to the simulated truth every day: 14 days on a laptop (1/10 data size); 3 days on Databricks Free Edition with eleven planted incidents (13 Nov 2026, gold step about 200 seconds)"),
    ("Incremental reads with watermarks per input", "Built", "Change sequence for database feeds, file lists for drops, cursor for the API"),
    ("Pure builds tested on two engines", "Built", "Same stage and build tests on Spark and DuckDB; a 3-day local run on DuckDB takes about 2 minutes"),
    ("Iceberg and Delta through one table port", "Built", "Unity Catalog managed Iceberg on Databricks"),
    ("Gold rerun after a silver rebuild", "Owed", "When a bad batch is voided and silver rebuilt, the affected gold windows must be redone"),
    ("Full data size on Databricks", "Owed", "Runs so far use 1/10 of the data"),
    ("A written rule for what counts as a restatement", "Owed", "The harness decides today; the spec must say it"),
    ("Date and plant dimensions", "Owed", "See the gold modelling page"),
]

DECISIONS = [
    ("How gold tables are built", "One harness with metadata; one small build per fact", "Pursue"),
    ("Fact refresh", "Replace changed windows with a lookback", "Pursue"),
    ("Row-level MERGE into large facts", "Only for accumulating snapshots that update by grain key", "Pursue with care"),
    ("Watermark unit", "Change sequence or commit version, never a wall-clock timestamp alone", "Pursue"),
    ("Incomplete windows", "Publish flagged by default; hold only where readers cannot handle a flag", "Pursue"),
    ("Corrections", "Correction plans with declared windows, never edits in the source", "Pursue"),
    ("Testing", "Pure builds, table-driven tests on two engines, a synthetic world with planted incidents every day", "Pursue"),
    ("Notebook per gold table", "-", "Drop"),
    ("Full rebuild every night", "-", "Drop except for small tables and declared backfills"),
]

QA = [
    ("How does incremental loading from silver to gold work?", "Each gold table keeps a watermark per input. A run fixes a high mark, reads only the changes between the two, turns the changed rows into the windows they touch (plus a lookback), rebuilds only those windows from silver, checks them, replaces them in gold, and moves the watermark last."),
    ("What is a watermark in data engineering?", "A bookmark of the last change a table has already processed, stored per table and per input in a metadata store. It should be a value that only goes up and never ties, such as a change sequence or a commit version, and it moves only after a run has written and checked its output."),
    ("Why rebuild whole windows instead of merging rows?", "A window (a day, a month, an hour) recomputed and replaced whole is idempotent, removes deleted rows without delete rules, and is cheap because only changed windows are touched. Row-level MERGE is kept for accumulating snapshots that update by key."),
    ("How do I test a silver-to-gold pipeline locally?", "Keep each fact's build a pure function of its input frames, put reading and writing in adapters, and test the build with small tables in and expected rows out. Then run the whole hop on a synthetic world with planted incidents, comparing gold with the world's own truth after every day, on a laptop with DuckDB or local Spark."),
    ("How does gold handle late-arriving data?", "Late facts inside the lookback rebuild their window and are logged as restatements; older ones go through a correction plan. A window owed data by several feeds stays flagged incomplete until all have arrived. Facts whose dimension member is missing get the unknown key and are re-keyed when it appears."),
]


def page():
    url = f"{SITE}{URL_PATH}"
    toc = "".join(f'<li><a href="#{a}">{E(b)}</a></li>' for a, b in [
        ("plain", "In plain words"), ("harness", "1. The harness, step by step"), ("one", "1b. One harness for every fact; SQL or PySpark"),
        ("debug", "1c. Troubleshooting, record drops, many-to-many"), ("incr", "2. How incremental loading works"),
        ("watermark", "3. Watermarks"), ("windows", "4. Grain and windows"), ("complete", "5. Completeness and restatements"),
        ("late", "6. Late facts and late dimensions"), ("history", "6b. History load, reloads, bad batches"), ("pure", "7. Pure functions, local tests, regression"),
        ("solves", "8. How the harness answers each problem"), ("reliable", "9. Reliability practices"),
        ("cost", "10. Cost practices"), ("status", "11. What is built"), ("decide", "12. Decisions"), ("faq", "FAQ")])
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/data-engineering/">Data engineering</a> › <a href="/learn/gold-data-modelling/">Gold data modelling</a> › Silver to gold</p>
<p class="eyebrow" style="margin-top:22px">Data engineering · guide</p>
<h1>{E(TITLE)}</h1>
<p class="lede"><a href="/learn/gold-data-modelling/">Gold data modelling</a> said what to build: facts at a declared grain, conformed dimensions, surrogate keys. This page is how to build it from silver, every day, without losing, doubling or silently changing a number, and without the cost growing with history. It describes the harness as we built and run it, and links to the <a href="/learn/gold-harness-spec/">gold harness spec</a> for the full requirements.</p>
<div class="gh">
<div class="box"><b>In one paragraph.</b> One harness builds every gold table the same way. It reads only what changed in silver since its watermark, works out which windows of the fact (days, months, hours) those changes touch, rebuilds just those windows with a small pure build per fact, looks up keys as of each event, checks everything before writing, replaces the windows, logs any number that changed after it was published, and moves the watermark last. Because the build is pure, it is tested on a laptop with small tables and with a whole synthetic company that plants problems on purpose.</div>
<ul class="toc">{toc}</ul>

<section id="plain"><p class="eyebrow">Lesson first</p><h2>In plain words</h2>
<p>Silver is clean, but shaped like the sources: an orders table, a deliveries table, a dealers table with history. Gold is shaped for questions: a fact of order lines with on-time flags, a monthly sales fact, dimensions with keys. The silver-to-gold hop is the factory between them. A good factory does the same steps for every product, checks every product before it leaves, and only remakes what changed.</p>
{fig(d_hop(), "Same steps for every gold table; only the build in the middle is written per fact.")}</section>

<section id="harness"><p class="eyebrow">1. The harness</p><h2>The harness, step by step</h2>
<p>Metadata (one file per gold table) declares the kind (fact or dimension), the grain, the inputs and how each is bookmarked, the window column and lookback, the dimensions and how to look them up, and the checks. The harness reads it and runs these steps:</p>
<ol class="steps">{''.join(f'<li>{E(s)}</li>' for s in STEPS)}</ol></section>

<section id="one"><p class="eyebrow">1b. One harness for every fact?</p><h2>Can one harness build every kind of fact?</h2>
<p>Yes, for the mechanics: reading changes, windows, keys, completeness, checks, writing, logging. Each fact kind is a declared mode the harness knows. What one harness cannot do is decide business logic: how OTIF is defined, how a header discount is shared out over lines. That stays in a small build per fact, and it should.</p>
{C.table(["Fact kind", "How the harness builds it", "In our build"], ONE_HARNESS)}
<h3>Is gold too business-specific to generalise?</h3>
<p>Partly, and that is the point of the split. Gold is the first layer where business logic cannot be avoided: silver is almost entirely generic (13 standard stages driven by metadata), while gold must know what "on time" means. But the business part is small. In our build the three facts' business logic is 116 lines in total (about 35 to 45 each), the shared harness is about 1,400 lines written once, and the six gold tables' metadata is 140 lines of YAML. So: <b>generalise the mechanics, declare the shape, hand-write only the business rule</b>. Never per-dataset code for the mechanics; that is where every notebook-per-table platform goes wrong.</p>
{C.table(["Part", "Generic or per fact", "Where it lives"], GENERIC)}
<h3>How to keep the common and the specific apart</h3>{C.table(["Rule", "What it means"], ISOLATE)}
<h3>The build: SQL or PySpark DataFrames?</h3>
<p>Both, chosen per fact, behind the same build interface. Default to SQL; use PySpark when the logic is genuinely complex. In our build the two sales facts are SQL and the scrap fact (hours, shifts, plant time zones) is PySpark.</p>
{vtable(["Need", "SQL", "PySpark DataFrames", "Better"], SQL_VS_DF)}</section>

<section id="debug"><p class="eyebrow">1c. Developer friendly</p><h2>Troubleshooting: seeing the intermediate results</h2>
<p>People can fix only what they can see. A harness that hides its steps is worse than a notebook. So every step must be visible: what was read, what each step produced, and where rows came and went.</p>
{C.table(["Feature", "What the developer gets", "State"], INSPECT)}
<h3>Where exactly records drop: the row ledger</h3>
<p>Every run keeps a ledger of rows per step. When totals are wrong, the ledger shows the step where they changed, without rerunning anything.</p>
{C.table(["Ledger line", "What is counted", "Step"], LEDGER)}
<h3>Catching many-to-many joins</h3>
<p>A join that silently matches several rows multiplies totals. The harness checks for it at four points:</p>
{C.table(["Where", "Check", "What it catches"], M2M)}</section>

<section id="incr"><p class="eyebrow">2. Incremental loading</p><h2>How incremental loading works</h2>
<p>Incremental means a run does work in proportion to what changed, not to how much history there is. In gold that takes two moves: find the changed rows, then turn them into the windows they touch.</p>
{fig(d_incr(), "Read a closed range of changes, map them to windows, rebuild only those windows.")}
{C.table(["Table kind", "Incremental pattern", "Why"], INCR)}
<h3>What gold reads from silver incrementally, and what in full</h3>{C.table(["Silver input", "How gold reads it", "Note"], READS)}</section>

<section id="watermark"><p class="eyebrow">3. Watermarks</p><h2>Watermarks</h2>{C.table(["Topic", "Rule"], WATERMARK)}</section>

<section id="windows"><p class="eyebrow">4. Grain and windows</p><h2>Grain and windows</h2>
<p>The fact's grain (one row per order line) says what a row is. The window says how the fact is rebuilt: by the time part of that grain. Declaring both is what lets the harness rebuild a day without touching the rest.</p>
{C.table(["Topic", "Rule"], WINDOWS)}</section>

<section id="complete"><p class="eyebrow">5. Completeness</p><h2>Completeness and restatements</h2>
<p>A number shown before all its data arrived is a promise that will change. The harness says so on the row (<code>_is_complete</code>) and records the change when it comes.</p>
{fig(d_complete(), "A month owed files by many dealers is complete only when the last owed file is in.")}
<div class="warn"><b>A real lesson from our tests:</b> our test oracle once expected October to complete on the day the late dealer's file arrived. The harness kept October open, because other dealers' files were still owed that day, and it was right. Completeness is "every owed feed has delivered", not "the late one arrived".</div></section>

<section id="late"><p class="eyebrow">6. Late data</p><h2>Late facts and late dimensions</h2>{C.table(["Case", "What the harness does", "Example"], LATE)}
<p>Inferred members (a placeholder dimension row with a real key, filled in later) are the alternative to the unknown key; both are compared on the <a href="/learn/gold-harness-spec/#late">gold harness spec</a>.</p></section>

<section id="history"><p class="eyebrow">6b. Loads that are not daily</p><h2>History load, reloads and hiding a bad batch</h2>
<h3>The history load</h3>
<p>The first load of years of history is just a long backfill: the same harness, period by period, oldest first, with the same checks. What is special is the order, the size and the handover to daily runs.</p>
{C.table(["Step", "How", "Why"], HISTORY)}
<h3>Reloads: reload from the nearest correct copy</h3>
<p>Pick the reload by where the fault entered, and start from the nearest copy that is still right. Most reloads are small: a few windows rebuilt from silver.</p>
{C.table(["Where the fault entered", "Reload", "Reload from"], RELOAD)}
<h3>Hiding a bad batch</h3>
<p>A bad batch that reached readers must disappear from their numbers quickly, and leave a record of why.</p>
{C.table(["Option", "How", "State or verdict"], BAD_BATCH)}</section>

<section id="pure"><p class="eyebrow">7. Testing</p><h2>Pure functions, and testing locally with synthetic data</h2>
{fig(d_pure(), "Keep every decision in a pure build; keep reading and writing in adapters; then the build can be tested anywhere.")}
{C.table(["Practice", "What it means"], PURE)}
<p>More on testing data code without a cluster: <a href="/learn/shift-left/">Shift left</a>. The synthetic world idea: <a href="/learn/datatwin/">DataTwin</a>.</p>

<h3>Regression: proving a change broke nothing</h3>
<p>A change to one build, one setting or the harness itself can move numbers far away. Regression testing is layered, from seconds to a full simulated run, and the slowest layer is the one that catches the surprises.</p>
{C.table(["Layer", "What it compares", "When", "State"], REGRESSION)}</section>

<section id="solves"><p class="eyebrow">8. Why a harness</p><h2>How the harness answers each problem</h2>
<p>Each problem on the <a href="/learn/gold-data-modelling/#problems">gold modelling page</a> needs a rule. Written once in the harness, the rule holds for every table, and a planted incident proves it every day.</p>
{C.table(["Problem", "How the harness handles it", "Proven by"], SOLVES)}</section>

<section id="reliable"><p class="eyebrow">9. Reliability</p><h2>Reliability practices</h2>{C.table(["Practice", "How", "What it prevents"], RELIABILITY)}</section>
<section id="cost"><p class="eyebrow">10. Cost</p><h2>Cost practices</h2>{C.table(["Practice", "Why it saves"], COST)}</section>

<section id="status"><p class="eyebrow">11. Status</p><h2>What is built, and what is owed</h2>{C.table(["Part", "State", "Evidence"], STATUS)}</section>
<section id="decide"><p class="eyebrow">12. Decisions</p><h2>Decisions with verdicts</h2>{vtable(["Decision", "Choice", "Verdict"], DECISIONS)}</section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(QA)}</section>
<section id="next"><p class="eyebrow">Related</p><h2>Where it connects</h2>
<p><a href="/learn/gold-data-modelling/">← Gold data modelling</a> · <a href="/learn/gold-harness-spec/">Gold harness spec</a> · <a href="/learn/scd2-auto-cdc-vs-pyspark/">SCD Type 2 on Databricks</a> · <a href="/learn/metric-views/">Metric views</a> · <a href="/learn/table-maintenance/">Table maintenance</a> · <a href="/learn/data-platform-architecture/gold/">Hop 3: silver to gold</a> · <a href="/data-engineering/">All data engineering</a></p></section>
</div>"""
    crumbs = [("Data engineering", f"{SITE}/data-engineering/"), ("Gold data modelling", f"{SITE}/learn/gold-data-modelling/"), ("Silver to gold", url)]
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": TITLE, "description": DESC, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in QA]}]
    head = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(TITLE, DESC, url, body, head)


def main():
    out = ROOT / "learn" / "silver-to-gold"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("silver to gold ->", out / "index.html")


if __name__ == "__main__":
    main()
