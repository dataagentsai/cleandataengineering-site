"""The ETL end to end on AWS + Databricks: /learn/data-platform-architecture/aws-databricks/etl/.

    python3 _guides/etl_aws.py

The runtime design of the core: which parts run, what starts them, how one run moves through
every hop, the ids and log rows that tie it together, failures, re-runs, streaming, and the
observability parts. The concept pages (ingestion, bronze to silver, gold, metadata store) say
WHAT each hop does; this page says HOW it runs. Names follow the framework (master run, run,
step, segment, watermark). Facts we are unsure of are marked "check current status".
"""
import json
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
import components as C  # noqa: E402
import dp_aws_databricks as D  # noqa: E402  (drawing helpers, table, CSS)

wb = C.wb
SITE = wb.SITE
URL = f"{SITE}/learn/data-platform-architecture/aws-databricks/etl/"
BASE = "/learn/data-platform-architecture/"
AWS = BASE + "aws-databricks/"
CHECK = D.CHECK
INK = D.INK
rect, tx, arr, svg, table = D.rect, D.tx, D.arr, D.svg, D.table


def rules(rows):
    return '<div class="rules">' + "".join(
        f'<div class="rule"><b class="n">{i + 1}</b><div><b>{E(t)}</b> {E(d)}</div></div>' for i, (t, d) in enumerate(rows)) + "</div>"


# ------------------------------------------------------------------ the principles
PRINCIPLES = [
    ("Movers never write to bronze; the lander never talks to a source.", "AWS services bring data to S3 landing; our one lander takes it from there. So every source, whatever its type, enters the platform the same way, and a source outage never touches Databricks."),
    ("Everything is a run, and every run leaves the same rows.", "A file load, a pipeline update and a 15-minute slice of a stream all get a run id and the same log rows, so one dashboard and one set of alerts cover all of them."),
    ("Every step can run twice.", "Re-running a step after a crash gives the same tables as running it once. That is what makes retries, re-runs and backfills safe without a person checking."),
    ("Jobs are generated, never hand-built.", "The run controller's jobs and pipelines are generated from the metadata and deployed with Asset Bundles. Adding a dataset changes YAML, not a job."),
    ("One orchestrator per path.", "Lakeflow Jobs owns everything from landing onwards. AWS only starts movers. Two schedulers for one pipeline is how runs overlap or never start."),
    ("Log before you work, close after you commit.", "A run that cannot write its start row does not start. A run is marked succeeded, and its bookmark moved, only after its data is committed."),
]

# ------------------------------------------------------------------ the working parts
PARTS = [
    ("1 Mover", "Brings data from a source to S3 landing", "source_config (which mover, schedule)", "Files in landing, plus a manifest per batch (file list, row count, source position)", "AWS DMS, AppFlow, Transfer Family, SiteWise and Kinesis", "Files are named by batch id; a re-sent batch overwrites itself"),
    ("2 Run controller", "Starts the work, in the right order, at the right time", "dataset_view (what is due), schedules and triggers", "master_run_log; the job run", "Lakeflow Jobs, generated from metadata", "A job that starts twice sees no new files and no due datasets; it ends as skipped"),
    ("3 Lander", "Landing to bronze: reads new files, adds ingest columns, tokenises personal data, appends", "dataset_view, the suppression list", "Bronze tables; run_log and step_log rows", "Our PySpark job using Auto Loader, one task per dataset", "Auto Loader's checkpoint remembers every file read; rows carry the run id"),
    ("4 Silver builder", "Bronze to silver: contract check, the eleven steps, quality rules, history", "Bronze, dq_rule, dataset_config", "Silver tables, quarantine tables, the pipeline event log", "A Declarative Pipeline per business domain, generated", "AUTO CDC orders changes by a sequence column, so reprocessing gives the same result"),
    ("5 Integrator", "Joins sources into one picture: MES production with SAP orders, materials mapped", "Silver tables, key mappings", "silver.integrated tables", "Materialized views in the same pipeline", "A materialized view is a result, not an append; refreshing it twice is harmless"),
    ("6 Gold builder", "Silver to gold: star schemas, multi-input facts, incomplete rows", "Silver, integrated silver", "Gold facts and dimensions", "Materialized views for simple facts; our window-recompute job for multi-input facts", "Each window is replaced whole (replaceWhere), never patched"),
    ("7 Metric layer", "Each metric defined once", "Gold", "Nothing stored; answers at query time", "Unity Catalog metric views", "Nothing to run"),
    ("8 Run recorder", "The one library every part calls to log", "-", "runtime: master_run_log, run_log, step_log, error_log, dq_result, config_snapshot", "Our Python library, writing to Aurora", "Rows are keyed by run id and step; writing the same row twice updates it"),
    ("9 Ops builder", "Every 15 minutes: copies the runtime rows, joins system tables and CloudWatch, works out freshness, raises alerts", "runtime schema, system tables, CloudWatch landing", "prod_ops tables, alerts, incidents", "A small Lakeflow job", "It recomputes the last hour each time, so a missed run is caught up by the next"),
    ("10 Heartbeat", "Proves the whole path is alive, even when no source sends anything", "A tiny synthetic source", "A row in every layer, every 15 minutes", "A generated dataset like any other", "Same as any dataset"),
]

INGEST_COLS = [
    ("Bronze", "_run_id, _batch_id, _source_file, _source_system, _ingested_at, _source_position", "Which run and which file brought this row, and where in the source it came from"),
    ("Silver", "_valid_from, _valid_to, _is_current, _first_run_id, _last_run_id, _is_deleted", "History (SCD2), and which runs created and last changed the row"),
    ("Quarantine", "_run_id, _rule_id, _reason, _quarantined_at", "Why the row was parked, and by which run"),
    ("Gold", "_run_id, _window_start, _is_complete", "Which run built this window, and whether all its inputs had arrived"),
]

# ------------------------------------------------------------------ the run, step by step
RUN_STEPS = [
    ("00:00:00  The mover keeps landing files.", "AWS DMS reads the MES database's change log continuously and writes a file of changes to landing/mes/press_event/ every few minutes, with a manifest: file names, row count, last change position."),
    ("00:15:00  The run controller starts a job run.", "The lander job for MES has a 15-minute schedule and a file-arrival trigger, whichever comes first. Lakeflow gives it a job run id."),
    ("00:15:02  First task: open the master run.", "It writes one master_run_log row (RUNNING), reads dataset_view for every enabled MES dataset, stores the merged settings once in config_snapshot by their fingerprint, and lists which datasets have new files."),
    ("00:15:05  One task per dataset, eight at a time.", "A for-each task runs the lander for each due dataset. Each opens its own run_log row (STARTED) with the master run id, the job's task run id and the window it will load."),
    ("00:15:06  The lander loads.", "Auto Loader reads only files it has not seen. The lander checks each file against its manifest (row count), tokenises personal columns, drops undeclared ones for personal-data sources, adds the ingest columns and appends to bronze. Each part is a step_log row with rows in and out."),
    ("00:15:40  The run closes after the commit.", "Only after the Delta commit: run_log becomes SUCCEEDED with rows read, written and rejected, and the source position from the manifest is stored as the watermark, in one database transaction."),
    ("00:15:45  The master run closes.", "SUCCEEDED if every dataset succeeded, PARTIAL if some failed (they get their own error_log rows), FAILED if none did. The next stage does not wait for the slowest dataset; it is started by the bronze tables themselves."),
    ("00:16:00  Bronze changes start silver.", "The silver pipeline for the manufacturing domain has a table-update trigger on its bronze tables, at most once every 15 minutes. A wrapper task opens a run_log row for the pipeline update and stores its update id."),
    ("00:16:05  The silver pipeline runs.", "Contract check, then the eleven bronze-to-silver steps; expectations park bad rows in quarantine; AUTO CDC applies changes and history. The integrator's materialized views refresh incrementally."),
    ("00:19:30  The wrapper reads the pipeline's event log.", "Rows per table, expectation results and errors are copied into run_log, step_log and dq_result, so a pipeline update looks like any other run."),
    ("00:20:00  Gold.", "Simple facts refresh as materialized views in the same pipeline. Multi-input facts (production per press-hour) run in the window-recompute job, which works out which hours changed in any input and rebuilds those hours whole."),
    ("00:30:00  The ops builder sees it.", "Its 15-minute run copies the new runtime rows into prod_ops, joins the job runs and their cost from system tables, and updates freshness: the MES-fed tables are green."),
]

TRIGGERS = [
    ("Schedule", "Batch sources with a fixed rhythm (SAP every 30 minutes in plant hours, full nightly)", "The lander job of that source"),
    ("File arrival", "Sources that drop files at unknown times (dealer sell-out, warranty files)", "The lander job of that source (" + CHECK + " for limits on watched paths)"),
    ("Table update", "Silver and gold: run when their inputs changed, not on a clock", "The pipeline of a domain, with a minimum gap between runs (" + CHECK + ")"),
    ("Continuous", "Sensor streams", "The streaming pipeline, always on"),
    ("Manual or API", "Re-runs, backfills, the heartbeat test", "Any job, with a run type that says why it ran"),
]

JOBS = [
    ("Lander job", "One per source", "Controller task, then a for-each over due datasets (concurrency from source_config), then a closing task", "Schedule or file arrival"),
    ("Domain pipeline", "One per business domain (manufacturing, quality, sales, aftermarket)", "Silver, integrated silver and simple gold as one Declarative Pipeline, wrapped by a task that records the run", "Table update"),
    ("Window-recompute job", "One per multi-input gold fact", "Find changed windows, rebuild them, reconcile, record", "Table update on any of its inputs"),
    ("Streaming pipeline", "One per stream family (press sensors, mixer sensors)", "Kinesis to bronze to silver per minute; hourly gold as a materialized view", "Continuous"),
    ("Ops builder", "One", "Copy runtime rows, join system tables and CloudWatch, freshness, alerts", "Every 15 minutes"),
    ("Housekeeping", "One", "Retention deletes, VACUUM, OPTIMIZE where predictive optimization is off, erasure requests", "Nightly"),
]

BUNDLE_YAML = """# Generated from dataset_view by the framework's generator; never edited by hand.
# (Asset Bundle job syntax: """ + CHECK + """)
resources:
  jobs:
    lander_mes:
      name: lander_mes
      trigger:
        file_arrival: { url: "s3://landing-prod/mes/" }
      schedule: { quartz_cron_expression: "0 0/15 * * * ?", timezone_id: "UTC" }
      max_concurrent_runs: 1                 # a run never overlaps the previous one
      tasks:
        - task_key: open_master_run
          python_wheel_task: { package_name: lake_ingest, entry_point: open_master_run,
                               parameters: ["--source", "mes"] }
        - task_key: load_each_dataset
          depends_on: [ { task_key: open_master_run } ]
          for_each_task:
            inputs: "{{tasks.open_master_run.values.due_datasets}}"
            concurrency: 8
            task:
              task_key: land_one
              python_wheel_task: { package_name: lake_ingest, entry_point: land,
                                   parameters: ["--dataset", "{{input}}"] }
              max_retries: 2                 # only for errors classed as transient
        - task_key: close_master_run
          depends_on: [ { task_key: load_each_dataset } ]
          run_if: ALL_DONE                   # closes the master run even after failures
          python_wheel_task: { package_name: lake_ingest, entry_point: close_master_run }"""

# ------------------------------------------------------------------ ids and log rows
IDS = [
    ("master_run_id", "Ours", "One trigger of one job: all the datasets loaded together", "master_run_log; every run_log row of that trigger"),
    ("job_run_id", "Databricks", "The Lakeflow job run", "Stored on master_run_log and run_log; joins system tables (timings, cost)"),
    ("run_id", "Ours", "One dataset through one stage (land, silver update, gold window)", "run_log, step_log, error_log, dq_result, and _run_id on every row it wrote"),
    ("task_run_id", "Databricks", "The task (or for-each iteration) that did the work", "Stored on run_log; links to the task's own log in Databricks"),
    ("update_id", "Databricks", "One update of a Declarative Pipeline", "Stored on run_log; joins the pipeline event log"),
    ("segment_id", "Ours", "One slice of a very large table load", "segment_run_log; run_log adds up its segments"),
    ("config fingerprint", "Ours", "The exact merged settings a run used", "config_snapshot; any run can be replayed with what it ran with"),
]

LOG_LEVELS = [
    ("master_run_log", "One per trigger of a job", "RUNNING, SUCCEEDED, PARTIAL, FAILED; counts of datasets attempted, succeeded, failed, skipped; run type; retry of which master run"),
    ("run_log", "One per dataset per stage", "STARTED, SUCCEEDED, FAILED, SKIPPED; window or watermark before and after; rows read, written, rejected; durations; retry count; cause class"),
    ("segment_run_log", "One per segment of a big load", "The segment's predicate, rows and status; the run adds them up"),
    ("step_log", "One per step inside a run", "land, tokenise, contract, quality, merge, reconcile: rows in and out, time taken"),
    ("error_log", "One per failure", "Cause class (source down, schema change, bad data, our bug, platform, capacity), scrubbed message, transient or not"),
    ("dq_result", "One per rule per run", "Passed or failed, failing rows, action taken"),
]

RECORDER_CALLS = [
    ("open_master_run(source, trigger)", "Writes the master run row; returns its id. Fails the job if it cannot write: no work without a record."),
    ("open_run(dataset, stage, window)", "Writes the run row with all ids it can see (job run, task run, update id)."),
    ("step(name, rows_in, rows_out)", "One step row; used as a context manager so the time is measured for you."),
    ("error(exc)", "Classifies the error, scrubs the message of data values, writes error_log, and says whether a retry makes sense."),
    ("quality(results)", "Writes dq_result rows from DQX or the pipeline's expectations."),
    ("close_run(status, counts, new_watermark)", "Marks the run and moves the watermark in one transaction, only when status is SUCCEEDED."),
]

# ------------------------------------------------------------------ streaming
STREAM_RUNTIME = [
    ("There are no runs, so we cut windows.", "Every 15 minutes the ops builder writes one run_log row per stream per window, from the pipeline's event log and streaming progress: rows in, rows out, how far behind (lag), errors."),
    ("The bookmark is not ours.", "The stream's checkpoint and Kinesis' sequence numbers are the watermark. We record where the checkpoint lives and the last sequence per shard, not a second bookmark."),
    ("Freshness is event time.", "A stream is fresh when the newest reading in silver is recent, not when the job is running. A running job that reads nothing is the silent failure we look for."),
    ("Gold from streams is hourly.", "The hourly gold materialized view refreshes after each hour closes, plus late readings within 2 hours; later ones are picked up by the window recompute."),
    ("Silent machines are checked separately.", "One press going quiet does not move a stream's totals, so a per-press check (no reading for 30 minutes in a planned shift) runs in the ops builder."),
]

# ------------------------------------------------------------------ failures
FAILURES = [
    ("Source down or slow", "Mover: CloudWatch alarm on DMS lag or AppFlow failure", "AWS retries; the lander finds no new files and ends as skipped", "Freshness alert at the promised time; incident for the source owner"),
    ("A file is empty, unreadable or does not match its manifest", "Lander, file check", "That dataset's run fails; the file moves to landing/_rejected; other datasets carry on (master run PARTIAL)", "The source owner re-sends; the next run picks it up"),
    ("Columns removed, renamed or retyped", "Silver, contract check", "That table's flow fails; its silver stays as it was; bronze still has everything", "New contract version and mapping; then replay from bronze"),
    ("Bad rows", "Silver, quality rules", "Rows parked in quarantine with the reason; the rest carry on; stop only past the bad-share limit", "Steward reviews weekly; fixed rows are released and re-merged"),
    ("Job or cluster dies halfway", "Lakeflow task failure", "Task retried (transient errors only, up to 2 times); nothing was committed, or the commit is replayed safely", "Nothing, unless retries run out"),
    ("Same file sent twice", "Lander", "Auto Loader skips a file it has seen; the same rows in a new file are removed by silver's duplicate step", "Nothing"),
    ("Data arrives late", "Lander and gold", "Lands normally; gold recomputes the windows it changes and logs a restatement", "Nothing; dashboards show the restatement note"),
    ("The metadata database is unreachable", "Run recorder, at open_master_run", "The job fails before doing any work; nothing half-done", "Platform on-call: the alert comes from Databricks job failure, which does not need our database"),
    ("A bug in our code", "Any stage", "Fails; error class 'our bug'; no retry", "Fix, release, then re-run the failed runs"),
]

RERUN = [
    ("Re-run failed", "Only the datasets that failed in a master run, with the same window", "A new master run with run type rerun and retry_of_master_run_id set; the watermark never moved, so the window is the same"),
    ("Replay from bronze", "Rebuild one silver table after a logic or contract fix", "A full refresh of that one table in its pipeline; bronze is the source of truth, so nothing is fetched from the source again"),
    ("Backfill", "Load or rebuild a past window on purpose", "A plan in Git with dataset, window, reason and cost; runs as its own run type and never moves the normal watermark; gold windows rebuilt and a restatement logged"),
    ("Re-extract", "Fetch from the source again", "Only for sources that can resend a window. Never for SAP, which moves its own delta token: we replay from landing or bronze instead"),
]

# ------------------------------------------------------------------ observability working parts
OBS_PARTS = [
    ("Run recorder", "Every part logs the same way, through six calls", "Built in the framework (Azure SQL today); the Aurora adapter is to do"),
    ("Ingest columns", "Every row in every layer says which run wrote it", "Partly built: bronze columns exist; silver and gold columns to add"),
    ("Pipeline wrapper", "Makes a Declarative Pipeline update look like any other run, from its event log", "To build"),
    ("Ops builder", "prod_ops every 15 minutes: runs, steps, quality, freshness, cost, movers", "To build; the health views exist in the framework for Azure"),
    ("Health views", "One row per dataset: last run, status, freshness against target, rows against the usual band, failing rules", "Built for Azure SQL (v_dataset_health); to port"),
    ("Heartbeat", "A synthetic dataset through every layer every 15 minutes, so a silent platform is noticed", "Designed in the framework (PL_HEARTBEAT); to build on Databricks"),
    ("Doctor", "A healthcheck before every deploy and on demand: database, secrets, buckets, grants, triggers reachable", "Built in the framework (lake-ingest doctor); AWS probes to add"),
]

HEALTH_COLS = """-- prod_ops.v_dataset_health: one row per dataset, the first thing on-call opens
SELECT d.dataset_name, d.tier, d.owner,
       r.status                          AS last_status,
       r.ended_at                        AS last_success_at,
       f.promised_by, f.minutes_late,    -- freshness against the target in dataset_config
       r.rows_written,
       b.rows_low, b.rows_high,          -- the usual band for this weekday
       q.rules_failed, q.rows_quarantined,
       c.cost_today_usd
FROM ops.dim_dataset d
LEFT JOIN ops.last_run r         USING (dataset_id)
LEFT JOIN ops.fct_freshness f    ON f.dataset_id = d.dataset_id AND f.day = current_date()
LEFT JOIN ops.volume_band b      USING (dataset_id)
LEFT JOIN ops.quality_today q    USING (dataset_id)
LEFT JOIN ops.cost_today c       USING (dataset_id);"""

DAY = [
    ("Continuous", "Press and mixer sensors stream into bronze and silver; hourly gold closes 15 minutes after each hour"),
    ("Every 15 min", "MES changes land and load; the manufacturing pipeline follows on table update; the ops builder refreshes freshness; the heartbeat passes through"),
    ("Every 30 min, 06:00-22:00", "SAP orders and deliveries in small batches"),
    ("01:00", "SAP full nightly extract; the sales pipeline follows"),
    ("02:00", "Dealer sell-out files arrive over the night; each starts its lander on arrival"),
    ("03:00", "Housekeeping: retention, erasures, VACUUM"),
    ("05:45", "Last hour of the night shift closes; the production window recompute finishes OEE inputs"),
    ("06:15", "Ops builder: every tier-1 data product green, amber or red; red pages the on-call"),
    ("06:30", "OEE ready for the plant morning meetings, with its completeness shown"),
    ("09:00", "Warranty claims ready (tier 2)"),
]


# ------------------------------------------------------------------ drawings
def runtime_map():
    b = []
    a = b.append
    a(rect(20, 20, 1100, 52, "#E6EAF7") + tx(570, 42, "Run controller: Lakeflow Jobs generated from the metadata (schedules, file arrival, table update)", 14.5, "middle")
      + tx(570, 62, "reads dataset_view in Aurora · writes master_run_log", 12, "middle", fill="#555"))
    cols = [("Sources", ["SAP", "MES database", "Quality lab, warranty", "Dealer files", "Press sensors"], "#F4F4F2"),
            ("Movers (AWS)", ["DMS, AppFlow,", "Transfer Family,", "SiteWise + Kinesis"], "#FFF4D9"),
            ("Landing (S3)", ["files + manifests", "per source, per batch"], "#F3E3D3"),
            ("Lander (ours)", ["Auto Loader", "tokenise, ingest cols", "append to bronze"], "#E6F4EC"),
            ("Silver builder", ["Declarative Pipeline", "per domain: contract,", "rules, AUTO CDC"], "#E6E6E6"),
            ("Gold builder", ["materialized views", "+ window recompute", "for multi-input facts"], "#F7E7B4"),
            ("Metric views", ["defined once;", "dashboards, Genie"], "#F8EBF1")]
    w, gap = 140, 20
    for i, (t, lines, f) in enumerate(cols):
        x = 20 + i * (w + gap)
        a(rect(x, 110, w, 150, f) + tx(x + w / 2, 136, t, 14, "middle", weight="700")
          + "".join(tx(x + w / 2, 160 + k * 19, ln, 12, "middle") for k, ln in enumerate(lines)))
        if i < len(cols) - 1:
            a(arr(x + w, 185, x + w + gap, 185))
        if 2 <= i <= 5:
            a(arr(x + w / 2, 72, x + w / 2, 110, dash=True))
    a(tx(20 + 2 * 160 + 70, 280, "the lander never talks to a source", 11.5, "middle", fill="#555"))
    a(rect(20, 300, 1100, 56, "#E0F1F7") + tx(570, 324, "Run recorder: every part writes run, step, error and quality rows with the same ids", 14.5, "middle")
      + tx(570, 344, "Aurora runtime schema → ops builder every 15 minutes → prod_ops: dashboard, alerts, incidents", 12, "middle", fill="#555"))
    for i in range(3, 6):
        x = 20 + i * 160 + 70
        a(arr(x, 260, x, 300, dash=True))
    return svg(1140, 370, "".join(b), "The runtime map: sources, AWS movers, S3 landing, our lander, the silver builder pipeline, the gold builder and metric views in a row. Above, the run controller (Lakeflow Jobs generated from metadata) starts the lander, silver and gold. Below, the run recorder takes the same log rows from every part into Aurora, and the ops builder copies them to prod_ops for the dashboard and alerts.")


def log_tree():
    b = []
    a = b.append
    a(rect(20, 20, 300, 60, "#E6EAF7") + tx(36, 46, "master_run_log", 15, weight="700") + tx(36, 66, "one trigger of the MES lander job", 12, fill="#555"))
    kids = [("run_log: press_event, land", 110), ("run_log: downtime, land", 180), ("run_log: work_order, land", 250)]
    for t, y in kids:
        a(f'<path d="M60,80 L60,{y + 25} L120,{y + 25}" fill="none" stroke="{INK}" stroke-width="1.4"/>')
        a(rect(120, y, 280, 50, "#E6F4EC") + tx(134, y + 31, t, 13))
    for k, s in enumerate(["step: read files", "step: tokenise", "step: append", "dq_result rows"]):
        y = 104 + k * 34
        a(f'<path d="M400,135 L440,135 L440,{y + 15} L470,{y + 15}" fill="none" stroke="{INK}" stroke-width="1.2"/>')
        a(rect(470, y, 180, 30, "#fff", r=8) + tx(482, y + 20, s, 12))
    a(rect(720, 20, 400, 60, "#F7E7B4") + tx(736, 46, "run_log: manufacturing pipeline update", 14, weight="700") + tx(736, 66, "started by the bronze tables, update id stored", 12, fill="#555"))
    a(rect(720, 110, 400, 50, "#F7E7B4") + tx(736, 140, "run_log: production fact, window recompute", 13))
    a(f'<path d="M300,110 C420,30 600,40 720,50" fill="none" stroke="{INK}" stroke-width="1.4" stroke-dasharray="4 3" marker-end="url(#ahx)"/>')
    a(arr(920, 80, 920, 110, dash=True))
    a(tx(560, 330, "Every box carries the job run id from Databricks, so system tables add timings and cost to each one.", 13, "middle"))
    a(tx(560, 350, "Every row written to a table carries the run id of the box that wrote it.", 13, "middle"))
    return svg(1140, 365, "".join(b), "The log hierarchy: one master run per job trigger, one run per dataset, steps and quality results under each run. Bronze changes start a silver pipeline update, recorded as its own run, which starts the gold window recompute, also its own run.")


# ------------------------------------------------------------------ page
FAQ = [
    ("Why not one big job from source to gold?", "Because sources arrive at different times. A job per source loads what has arrived; pipelines per domain run when their inputs change. Nothing waits for the slowest source, and a failure in one source does not block the others."),
    ("Why does a Declarative Pipeline need a wrapper task?", "The pipeline has its own event log and its own ids. The wrapper opens and closes our run row around each update and copies the counts and expectation results across, so on-call sees one kind of run everywhere."),
    ("What if the logging database is down?", "Jobs fail at their first task, before any work, so nothing is left half-done. The failure itself is visible in Databricks job alerts and system tables, which do not depend on our database."),
    ("How is this different from Azure Data Factory designs?", "In an ADF design the orchestrator also moves data. Here the AWS movers only move, Lakeflow Jobs only orchestrates, and our lander and pipelines only transform. The framework's contracts (master run, run, step, segment, watermark) are the same."),
]


def page():
    parts_table = table(["Part", "Does", "Reads", "Writes", "Runs as", "Safe to run twice because"], PARTS)
    cols_table = table(["Layer", "Columns added to every row", "So you can tell"], INGEST_COLS)
    trig_table = table(["Trigger", "Used for", "Starts"], TRIGGERS)
    jobs_table = table(["Job", "How many", "Inside", "Started by"], JOBS)
    ids_table = table(["Id", "Made by", "Means", "Found in"], IDS)
    levels_table = table(["Log table", "One row per", "Holds"], LOG_LEVELS)
    fail_table = table(["What goes wrong", "Caught by", "What happens by itself", "What a person does"], FAILURES)
    rerun_table = table(["Kind", "When", "How"], RERUN)
    obs_table = table(["Part", "Does", "Status"], OBS_PARTS)
    day_table = table(["When", "What runs"], DAY)
    faq = C.faq(FAQ)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › <a href="{BASE}">Data platform architecture</a> › <a href="{AWS}">On AWS + Databricks</a> › The ETL, end to end</p>
<p class="eyebrow" style="margin-top:22px">Data platform architecture · AWS + Databricks · runtime design</p>
<h1>The ETL, end to end</h1>
<p class="lede">How the core actually runs: which parts there are, what starts each one, how one load moves from a source system to a metric, the ids and log rows that tie it together, what happens when something breaks, and how we watch it. The concept pages say what each layer does; this page says how it runs.</p>
<div class="sib"><a href="{AWS}">↑ The platform on AWS + Databricks</a><a href="{BASE}ingestion/">Ingestion</a><a href="{BASE}bronze-to-silver/">Bronze to silver</a><a href="{BASE}gold/">Gold</a><a href="{BASE}metadata-store/">Metadata store</a></div>
<nav class="toc"><b>On this page</b><ol>
<li><a href="#rules">Six rules</a></li><li><a href="#map">The runtime map</a></li><li><a href="#parts">The ten working parts</a></li><li><a href="#run">One run, step by step</a></li>
<li><a href="#jobs">Jobs and triggers</a></li><li><a href="#logs">Ids and log rows</a></li><li><a href="#stream">Streaming</a></li><li><a href="#fail">When something breaks</a></li>
<li><a href="#rerun">Re-runs, replays and backfills</a></li><li><a href="#obs">Observability: the working parts</a></li><li><a href="#day">A day in the life</a></li><li><a href="#faq">Questions</a></li></ol></nav>

<section id="rules"><p class="eyebrow">Start here</p><h2>Six rules the whole runtime follows</h2>
<p>Everything below follows from these. If a design choice ever conflicts with one of them, the rule wins.</p>
{rules(PRINCIPLES)}</section>

<section id="map"><p class="eyebrow">The runtime map</p><h2>Ten parts, three bands</h2>
<p>Read the middle row left to right: data moves from source systems to metrics. The band above decides when things run; the band below records everything that ran. Nothing in the middle row starts itself, and nothing runs without being recorded.</p>
<figure class="diagram">{runtime_map()}<figcaption>The middle row moves and shapes data; the top band starts it; the bottom band records it.</figcaption></figure></section>

<section id="parts"><p class="eyebrow">The working parts</p><h2>What each part does, reads and writes</h2>
<p>Each part has one job and a fixed contract: what it reads, what it writes, and why running it twice is safe. The last column is the most important one: it is what lets the platform retry without a person checking.</p>
{parts_table}
<h3>Every row says where it came from</h3>
<p>The lander and the builders add the same columns to every table, so any number can be followed back to the run, the file and the source position that produced it.</p>
{cols_table}</section>

<section id="run"><p class="eyebrow">One run, step by step</p><h2>A quarter-hour of MES data, from database to gold</h2>
<p>Follow one load: changes to the press events table in the plant's MES database, picked up at 00:15 and in gold by 00:20. Times are illustrative.</p>
{rules(RUN_STEPS)}</section>

<section id="jobs"><p class="eyebrow">Jobs and triggers</p><h2>What starts what</h2>
<p>Lakeflow Jobs can start a job on a clock, when a file arrives, or when a table it reads has changed. We use all three, each where it fits, so data flows as soon as it can and nothing polls for no reason.</p>
{trig_table}
<h3>The jobs the generator writes</h3>
{jobs_table}
<p>One generated job, as an example. It is produced from the metadata for every source; people change the YAML in the metadata, never this file.</p>
{C.code(BUNDLE_YAML, "The lander job for the MES source, generated as an Asset Bundle resource.")}</section>

<section id="logs"><p class="eyebrow">Ids and log rows</p><h2>One id for every piece of work</h2>
<p>Seven ids, some ours and some Databricks', are written side by side, so our logs, Databricks' system tables and the data itself all join without guessing by time.</p>
{ids_table}
<figure class="diagram">{log_tree()}<figcaption>The log hierarchy for one MES trigger and the work it sets off.</figcaption></figure>
<h3>The log tables</h3>
<p>These are the framework's existing run tables, in the runtime schema of the metadata database.</p>
{levels_table}
<h3>The run recorder: six calls</h3>
<p>Every part logs through one small library, so the rows are always complete and always the same shape.</p>
{rules(RECORDER_CALLS)}</section>

<section id="stream"><p class="eyebrow">Streaming</p><h2>Sensors fit the same model</h2>
<p>A stream never ends, so it has no runs of its own. These five rules make it look like everything else to on-call and to the dashboard.</p>
{rules(STREAM_RUNTIME)}</section>

<section id="fail"><p class="eyebrow">When something breaks</p><h2>Each failure has one place it is caught</h2>
<p>For each kind of failure: where it is caught, what the platform does by itself, and the one thing a person needs to do. Retries happen only for errors classed as passing (a network blip, a busy cluster), never for bad data or bugs, because retrying those just fails again.</p>
{fail_table}</section>

<section id="rerun"><p class="eyebrow">Re-runs, replays and backfills</p><h2>Four ways to run again, each safe</h2>
{rerun_table}</section>

<section id="obs"><p class="eyebrow">Observability: the working parts</p><h2>What has to exist for anyone to see what ran</h2>
<p>The dashboard, alerts and incidents are described on <a href="{AWS}#ops">the platform page</a>. These are the parts underneath that make them possible, and where each stands today.</p>
{obs_table}
{C.code(HEALTH_COLS, "The health view on-call opens first: one row per dataset, everything joined on the dataset and run ids.")}</section>

<section id="day"><p class="eyebrow">A day in the life</p><h2>Twenty-four hours of the runtime</h2>
<p>What runs when on an ordinary day, for the plants' morning meeting at 06:30.</p>
{day_table}</section>

<section id="faq"><p class="eyebrow">Questions</p><h2>Questions engineers ask</h2>{faq}</section>

<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2>
<p><a href="{AWS}">↑ The platform on AWS + Databricks</a> · <a href="{BASE}ingestion/">Ingestion</a> · <a href="{BASE}bronze-to-silver/">Bronze to silver</a> · <a href="{BASE}gold/">Gold</a> · <a href="{BASE}metadata-store/">Metadata store</a> · <a href="{BASE}testing/">Test architecture</a></p></section>"""
    desc = "How the core ETL runs on AWS and Databricks: ten working parts, what starts each one, one run step by step from source to gold, ids and log rows, streaming, failures, re-runs and the observability parts."
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": "The ETL, end to end, on AWS and Databricks", "description": desc, "url": URL,
           "inLanguage": "en", "isAccessibleForFree": True, "dateModified": "2026-11-03",
           "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]
    head = D.CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page("The ETL, end to end, on AWS and Databricks", desc, URL, body, head)


def main():
    out = ROOT / "learn" / "data-platform-architecture" / "aws-databricks" / "etl"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("etl page ->", out)


if __name__ == "__main__":
    main()
