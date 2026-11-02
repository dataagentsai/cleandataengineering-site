"""The ETL end to end on AWS + Databricks: /learn/data-platform-architecture/aws-databricks/etl/.

    python3 _guides/etl_aws.py

The runtime design of the core: which parts run, what starts them, how one run moves through
every hop, the ids and log rows that tie it together, failures, re-runs, streaming, and the
observability parts. The concept pages (ingestion, bronze to silver, gold, metadata store) say
WHAT each hop does; this page says HOW it runs. Names follow the framework (master run, run,
step, segment, watermark). Facts we are unsure of are marked "check current status".

Revised 3 Nov 2026 after a design test of 12 scenarios (3 failed, 9 with gaps): completeness by
source watermark, one clock per source, a batch-ready marker, lander-owned retries, file log,
unique file names and replacement rules, ordering and deletes for DMS and SAP, a mass-delete
guard, corrections that restate history, timeouts and a sweeper, separate bulk jobs.
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
    ("Movers never write to bronze; the lander never talks to a source.", "AWS services (and our puller) bring data to S3 landing; our one lander takes it from there. Every source enters the same way, and a source outage never touches Databricks."),
    ("Everything is a run, and every run leaves the same rows.", "A file load, a pipeline update and a 15-minute slice of a stream all get a run id and the same log rows, so one dashboard and one set of alerts cover all of them."),
    ("Every step can run twice.", "Re-running a step after a crash gives the same tables as running it once. That is what makes retries, re-runs and backfills safe without a person checking."),
    ("A number is complete only when every input has caught up.", "Each input carries its own bookmark: how far in source time it has been loaded. A gold hour is complete only when every input's bookmark is past the end of that hour. Otherwise it is published as incomplete, never as right."),
    ("One clock per source, one orchestrator per path.", "Each source has exactly one thing that starts its lander. Lakeflow Jobs owns everything from landing onwards; AWS only moves. Two clocks on one path is how runs overlap, wait or never start."),
    ("Jobs are generated, never hand-built.", "Jobs, pipelines and mover settings are generated from the metadata and deployed with Asset Bundles and Terraform. Adding a dataset changes YAML, not a job."),
    ("Log before you work; nothing waits forever.", "A run that cannot write its start row does not start. Every call to the log database and every job has a timeout, so a slow database fails loudly instead of freezing quietly."),
]

# ------------------------------------------------------------------ sources and ingestion tech
SOURCES = [
    ("Databases that change all day", "MES (SQL Server), quality lab LIMS (Oracle), warranty system, plant maintenance", "AWS DMS: full load once, then change data capture (CDC)", "Every insert, update and delete, with an operation flag, commit time and change sequence", "Parquet files, written continuously", "Loaded every 15 minutes"),
    ("Small or reference database tables", "Press master, shift calendars, code lists; any database where CDC logging is not allowed", "Our puller: the framework's built connectors (SQL Server, Oracle, PostgreSQL, MySQL) as a Databricks job over JDBC", "A full copy (needed for any table that can delete rows), or rows above a watermark for append-only tables", "Parquet plus a manifest", "On a schedule, often daily"),
    ("SAP S/4HANA", "Sales orders, deliveries, stock, procurement, finance", "Amazon AppFlow, SAP OData connector, reading released CDS views and extractors with delta", "Only what changed since the last call, with SAP's change mode (new, changed, deleted) where the extractor gives it", "Parquet plus a manifest written when the flow finishes", "Every 30 minutes in plant hours; a nightly full copy for objects whose delta has no deletes"),
    ("SaaS applications with an AppFlow connector", "CRM (for example Salesforce), IT service desk", "Amazon AppFlow", "Rows changed since the last run", "Parquet plus a manifest written when the flow finishes", "Hourly"),
    ("APIs without an AppFlow connector", "Dealer management system API, natural-rubber price feed, weather", "Our puller: the framework's built REST connector", "Pages since the last cursor or date", "JSON lines plus a manifest", "On a schedule"),
    ("Files from partners", "Dealer sell-out, supplier certificates of analysis, logistics partners", "AWS Transfer Family (SFTP), one login and folder per partner", "New files; a correction is a new file", "As received (CSV, Excel, XML), renamed on arrival to a unique key", "On arrival"),
    ("Machines and sensors", "Curing presses, mixers, live historian tags", "AWS IoT SiteWise Edge or IoT Core at the plant, into Amazon Kinesis Data Streams (7 days kept)", "Events, one per reading", "No files: the Kinesis stream is the landing", "Continuous"),
    ("Historian history", "Years of past press and mixer data, once", "The historian's own export to S3 through Transfer Family (" + CHECK + " for the historian's tools)", "One-off backfill", "Parquet or CSV", "Once, through the bulk job"),
    ("Spreadsheets people keep", "Ideal cycle times not in MES, targets, mappings", "YAML in Git first; otherwise an upload to a Unity Catalog volume by the named owner", "A new version of the file; a correction says from which date it applies", "As uploaded", "On upload"),
]

PICK_ORDER = [
    ("Is it machine data?", "Kinesis, through SiteWise or IoT Core."),
    ("Is it SAP?", "AppFlow with the SAP OData connector. If SAP Datasphere or Business Data Cloud is licensed, the SAP team may choose those instead; the landing contract stays the same."),
    ("Is it a database with many changes a day, or can rows be deleted?", "AWS DMS with change capture, or a full copy by our puller if the table is small. A watermark pull never sees deletes."),
    ("Is it a small, append-only table or a reference list?", "Our puller, full copy or by watermark."),
    ("Is it a SaaS application?", "AppFlow if it has a connector; otherwise our puller's REST connector."),
    ("Is it files from someone outside?", "Transfer Family SFTP, one folder and one login per partner, and a written rule for what a re-sent file replaces."),
    ("None of the above?", "Ask how it can become a file in landing. If it cannot, it is a design discussion, not a quick add."),
]

LANDING_CONTRACT = [
    ("One place.", "landing/<source>/<dataset>/<date>/, in the landing bucket of the environment. Personal-data sources use the personal-data landing bucket."),
    ("Unique names, never overwritten.", "Every file gets a name nobody else uses (partner, file, arrival time). A Transfer Family workflow renames partner uploads on arrival. A re-sent or corrected file is a new file; what it replaces is a rule in silver, written in the dataset's contract."),
    ("Complete or invisible.", "A file appears only when complete (S3 writes are all-or-nothing; SFTP uploads go to a temporary name first)."),
    ("Say how many.", "Our puller writes a manifest with the row count. For AppFlow, an EventBridge rule writes the manifest from the flow-run event when the flow finishes. Partners send a control file where agreed. DMS cannot, so DMS loads are reconciled daily per table against DMS's own table statistics."),
    ("Say what was deleted, and in what order.", "DMS adds its operation flag, commit time and change sequence to every row (full-load rows too). SAP rows carry the extractor's change mode where it exists. Full copies are compared with the previous copy in silver."),
    ("Keep the source's history long enough.", "Each database keeps its change log at least 72 hours, so DMS can catch up after an outage without a full reload."),
    ("No transforming.", "Movers change the format at most (to Parquet). Every rule about content lives in the lander and after."),
]

LANDER_MODES = [
    ("Files (DMS, AppFlow, puller, SFTP, uploads)", "First a file check against the file log (readable, header, row count), then Auto Loader, one stream per dataset, as availableNow", "The file log and Auto Loader's checkpoint, per dataset"),
    ("DMS change files", "As files, keeping operation flag, commit time and change sequence as columns; silver applies them in that order with AUTO CDC", "As above; a bad file blocks the dataset (see failures)"),
    ("Kinesis streams", "A streaming table reading Kinesis directly, always on", "Stream checkpoint and Kinesis sequence numbers"),
]

NOT_V1 = [
    ("Lakeflow Connect", "Its managed connectors write straight into tables, skipping landing, the lander's tokenising and our run recorder: a second way in. Revisit per source for SaaS without personal data."),
    ("Reading SAP tables directly", "Against SAP's licence terms for most customers, and fragile across upgrades. AWS DMS does not read SAP HANA as a source anyway (" + CHECK + ")."),
    ("Glue jobs as movers", "Glue is a transformation engine; using it to copy adds a second engine to run and pay for."),
    ("Fivetran, Airbyte and similar", "Not needed for these sources. If the company already pays for one, it can act as a mover by writing to S3 landing, under the same landing contract."),
    ("Documents and images", "PDF test reports and defect photos need a document pipeline; a later phase."),
    ("Email attachments", "Partners move to SFTP instead; email is not a reliable or auditable way in."),
]

MOVER_STATUS = [
    ("AWS DMS", "Tasks and table mappings generated from source_config into Terraform; one task per group of tables, so adding a table stops only its group", "To build (generator); DMS itself is a service"),
    ("Amazon AppFlow", "Flows generated from source_config, one per object; an EventBridge rule per flow writes the manifest and starts the lander", "To build (generator)"),
    ("AWS Transfer Family", "One server; a login, folder and rename workflow per partner, from source_config", "To build (generator)"),
    ("Our puller", "The framework's connectors: discovery and bulk reads for SQL Server, Oracle, PostgreSQL, MySQL, REST and SFTP", "Connectors built; the Databricks job and the manifest to build"),
    ("SiteWise / IoT Core and Kinesis", "Edge set up per plant with the plant's OT team; streams from Terraform", "To build, with the OT team"),
]

# ------------------------------------------------------------------ the working parts
PARTS = [
    ("1 Mover", "Brings data from a source to S3 landing (or Kinesis, for streams)", "source_config", "Files in landing under the landing contract", "AWS DMS, AppFlow, Transfer Family, SiteWise and Kinesis, or our puller", "Unique file names; a re-sent file is a new file"),
    ("2 Run controller", "Starts the work: one clock per source, a marker for silver, the wrapper for gold", "dataset_view, schedules, triggers, markers", "master_run_log; the job run", "Lakeflow Jobs, generated from metadata", "Runs queue instead of overlapping; a run with nothing due ends as skipped"),
    ("3 Lander", "Landing to bronze: checks files, adds ingest columns, tokenises personal data, appends; writes the batch-ready marker", "dataset_view, the file log, the suppression list", "Bronze tables, file_log, run_log and step_log rows, the marker", "Our PySpark job using Auto Loader, one task per dataset", "Auto Loader's checkpoint remembers every file; writes are idempotent (transaction app id and version)"),
    ("4 Silver builder", "Bronze to silver: contract check, the eleven steps, quality rules, history, replacement rules", "Bronze, dq_rule, dataset_config", "Silver tables, quarantine tables, input watermarks, the pipeline event log", "A Declarative Pipeline per business domain, generated, started by markers", "AUTO CDC orders changes by a defined sequence, so reprocessing gives the same result"),
    ("5 Integrator", "Joins sources into one picture: MES production with SAP orders, materials mapped", "Silver tables, key mappings", "silver.integrated tables", "Materialized views in the same pipeline", "A materialized view is a result, not an append"),
    ("6 Gold builder", "Silver to gold: star schemas, multi-input facts, completeness per window", "Silver, integrated silver, input watermarks", "Gold facts and dimensions", "Materialized views for simple facts; our window-recompute job for multi-input facts", "Each window is replaced whole (replaceWhere on date partitions), never patched"),
    ("7 Metric layer", "Each metric defined once", "Gold", "Nothing stored; answers at query time", "Unity Catalog metric views", "Nothing to run"),
    ("8 Run recorder", "The one library every part calls to log", "-", "runtime: master_run_log, run_log, step_log, file_log, error_log, dq_result, input_watermark, config_snapshot", "Our Python library, writing to Aurora, with timeouts", "Rows are keyed by run id and step; writing the same row twice updates it"),
    ("9 Ops builder", "Every 15 minutes: copies runtime rows, joins system tables and CloudWatch, works out freshness, sweeps stuck runs, raises alerts", "runtime schema, system tables, CloudWatch landing", "prod_ops tables, alerts, incidents", "A small Lakeflow job", "It recomputes the last hour each time, so a missed run is caught up by the next"),
    ("10 Heartbeat", "Proves the whole path is alive, even when no source sends anything, and is watched without our database", "A tiny synthetic source", "A row in every layer every 15 minutes; a Databricks SQL alert watches the newest one", "A generated dataset like any other", "Same as any dataset"),
]

INGEST_COLS = [
    ("Bronze", "_run_id, _file, _source_system, _ingested_at, and from the mover: _op, _commit_ts, _change_seq (DMS) or _change_mode (SAP)", "Which run and file brought this row, and its place in the source's order of changes"),
    ("Silver", "_valid_from, _valid_to, _is_current, _is_deleted, _source_run_id (the lander run that brought the latest version)", "History, and the lander run behind each version. The silver pipeline update itself is traced by its update id in run_log"),
    ("Quarantine", "_run_id, _rule_id, _reason, _quarantined_at", "Why the row was parked, and by which run"),
    ("Gold (our jobs)", "_run_id, _window_start, _is_complete, _inputs_as_of", "Which run built this window, whether every input had caught up, and how far each had"),
    ("Gold (materialized views)", "None: refreshed by the pipeline", "Traced by the pipeline update id in run_log and its event log"),
]

# ------------------------------------------------------------------ order, deletes, corrections, completeness
ORDERING = [
    ("DMS changes", "Sequence by commit time, then DMS's change sequence (AR_H_CHANGE_SEQ), so two changes in the same instant keep their order. Full-load rows carry an operation flag too (IncludeOpForFullLoad) and sort before every change.", "Delete when _op = 'D'"),
    ("SAP deltas", "Sequence by the extraction run, then the extractor's change counter where it has one (" + CHECK + " per object).", "Delete when the change mode says deleted; objects whose delta does not carry deletes are loaded as a nightly full copy instead"),
    ("Full copies (puller, snapshots)", "Each copy is a snapshot in time. Silver compares it with the previous one (AUTO CDC from snapshot).", "A row missing from the new copy is deleted, unless the mass-delete guard stops the load"),
    ("Partner files", "Order by arrival time.", "Each dataset's contract says what a file replaces, for example all rows for that dealer and month; silver replaces that slice with the newest file"),
    ("Streams", "Event time; duplicates removed by reading id.", "Readings are never deleted"),
]

GUARDS = [
    ("The mass-delete guard.", "If a full copy would delete more than a set share of the table (5% by default, set per dataset), the load stops before silver changes. A pull that came back short matches its own manifest, so only this guard catches it."),
    ("Deleted members stay in dimensions.", "A decommissioned press keeps its row in gold's press dimension, flagged, so old facts still find it. Facts join dimensions as of the event time, never just to the current row."),
    ("A change is not a correction.", "A change is something new in the world (a press gets a new mould): history keeps the old value up to that date. A correction says the old value was wrong (the ideal cycle time was always 92 seconds, not 95): it restates history from the date it names. Corrections arrive marked as such, with that date."),
    ("Corrections reach gold only through a backfill plan.", "A dimension correction never triggers a recompute of months by itself at a busy hour. It waits for a backfill plan, which says which windows to rebuild and when."),
]

COMPLETENESS = [
    ("Every input has a bookmark in source time.", "After each silver update, input_watermark records how far each input is loaded: the newest commit time for DMS, the extraction time for SAP and SaaS, the copy time for full copies, the newest event time for streams."),
    ("Quiet sources still move forward.", "At night MES may change nothing. If DMS is running and its source latency is low (from CloudWatch), the bookmark is 'now minus that latency'. If DMS is stopped or far behind, the bookmark stays where it is."),
    ("A window is complete when every input is past its end.", "The window-recompute job marks an hour complete only when every input's bookmark is past the end of that hour (plus the late allowance for streams). Otherwise it publishes the hour as incomplete, and the dashboard says so."),
    ("Freshness is the bookmark, not the last run.", "A dataset is fresh when its bookmark is within its target, whatever its runs say. A source that went quiet because it broke goes red; one that is genuinely quiet stays green."),
    ("Incomplete hours fill in by themselves.", "When the late input catches up, its bookmark moves, the affected windows are recomputed, marked complete, and logged as a restatement."),
]

# ------------------------------------------------------------------ the run, step by step
RUN_STEPS = [
    ("All the time: DMS lands change files.", "AWS DMS reads the MES database's change log and writes Parquet files to landing/mes/<table>/, each row with its operation flag, commit time and change sequence."),
    ("00:15:00  One clock starts the lander.", "The MES lander job runs on a 15-minute schedule; that is its only trigger. If the previous run is still going, the new one waits in the queue instead of overlapping."),
    ("00:15:02  Open the master run.", "The first task writes the master_run_log row (RUNNING), reads dataset_view for every enabled MES dataset, stores the merged settings once in config_snapshot, and lists datasets with files not yet in the file log."),
    ("00:15:05  One task per dataset, eight at a time.", "Each opens its run_log row (STARTED) with the master run id, job run id and task run id."),
    ("00:15:06  Check the files, then load.", "New files are checked (readable, expected header) and written to file_log. A good file goes to Auto Loader; the lander tokenises personal columns, drops undeclared ones for personal-data sources, adds the ingest columns and appends to bronze with an idempotent write."),
    ("00:15:40  Close the run after the commit.", "After the Delta commit, run_log becomes SUCCEEDED with rows read, written and rejected, and the newest commit time loaded becomes the run's watermark, in one Aurora transaction. If that write fails, the sweeper finishes it later from the evidence in bronze."),
    ("00:15:45  Close the master run and write the marker.", "The closing task runs even after failures. It marks the master run SUCCEEDED, PARTIAL or FAILED and writes one row to the batch-ready marker table: source, master run, which datasets loaded. The job itself ends green when every failure was a handled data problem; PARTIAL is alerted from our log, not by a job failure."),
    ("00:16:00  The marker starts silver.", "The manufacturing pipeline is triggered by updates to the marker tables of its sources (MES, the press master), not by each bronze table, so it never starts on a half-loaded source. A wrapper task opens a run_log row and stores the pipeline's update id."),
    ("00:16:05  The silver pipeline runs.", "Contract check, the eleven steps, quality rules, AUTO CDC in the defined order. At the end, each input's bookmark is written to input_watermark."),
    ("00:19:30  The wrapper closes the update and starts gold.", "It copies rows, expectation results and errors from the pipeline's event log into our tables, closes the run, then starts the window-recompute job directly (never on a table trigger, which could fire in the middle of an update)."),
    ("00:20:00  Gold, with completeness.", "The recompute finds the hours that changed in any input, rebuilds them whole, and marks each hour complete only if every input's bookmark is past its end. Simple facts refresh as materialized views in the pipeline."),
    ("00:30:00  The ops builder sees it.", "It copies the runtime rows into prod_ops, joins job runs and cost from system tables, reads skipped and queued runs too, and updates freshness from the bookmarks."),
]

TRIGGERS = [
    ("Schedule", "Every DMS source (its files arrive all the time, so a clock is calmer than file events); the puller", "The lander job of that source"),
    ("AppFlow finished", "SAP and SaaS sources: an EventBridge rule on the flow-run event writes the manifest and starts the lander through the Jobs API", "The lander job of that source, so there is one clock: AppFlow's"),
    ("File arrival", "Partner files and uploads only, with file events switched on for the landing location (" + CHECK + " for limits)", "The lander job of that source"),
    ("Table update on the marker", "Silver: runs when one of its sources has finished a batch", "The domain pipeline, through its wrapper task"),
    ("Called by the wrapper", "Gold multi-input facts", "The window-recompute job, after the domain pipeline closes"),
    ("Continuous", "Sensor streams", "The streaming pipeline, always on"),
    ("Manual or API, queued", "Re-runs, backfills, first loads, the heartbeat test", "The bulk job of that source, or a queued run of the normal job, with a run type that says why"),
]

JOBS = [
    ("Lander job", "One per source", "Open, a for-each over due datasets (concurrency from source_config), close and write the marker", "Its one clock (schedule, AppFlow finished, or file arrival)"),
    ("Bulk job", "One per source", "First loads and backfills, in segments, with their own Auto Loader checkpoints and their own landing paths; hands over to the lander job when done", "Manual or API"),
    ("Domain pipeline", "One per business domain (manufacturing, quality, sales, aftermarket)", "Silver, integrated silver and simple gold as one Declarative Pipeline, wrapped by a task that records the run", "Table update on its sources' markers"),
    ("Window-recompute job", "One per multi-input gold fact", "Find changed windows, rebuild them, set completeness, reconcile, record", "Called by the domain pipeline's wrapper; backfills through a plan"),
    ("Streaming pipeline", "One per stream family (press sensors, mixer sensors)", "Kinesis to bronze to silver per minute", "Continuous"),
    ("Stream gold job", "One per stream family", "Hourly gold for the closed hour and a re-check of the last 2 days for late readings", "Hourly, at 15 minutes past"),
    ("Ops builder", "One", "Copy runtime rows, join system tables and CloudWatch, freshness, sweep stuck runs, alerts", "Every 15 minutes"),
    ("Housekeeping", "One", "Retention deletes, VACUUM, OPTIMIZE where predictive optimization is off, erasure requests, daily DMS reconcile", "Nightly"),
]

BUNDLE_YAML = """# Generated from dataset_view by the framework's generator; never edited by hand.
# (Asset Bundle job syntax: """ + CHECK + """)
resources:
  jobs:
    lander_mes:
      name: lander_mes
      schedule: { quartz_cron_expression: "0 0/15 * * * ?", timezone_id: "UTC" }   # the one clock
      max_concurrent_runs: 1
      queue: { enabled: true }               # a run waits; it never overlaps or vanishes
      timeout_seconds: 1800                  # nothing waits forever
      health:
        rules:
          - { metric: RUN_DURATION_SECONDS, op: GREATER_THAN, value: 900 }   # alert without our database
      tasks:
        - task_key: open_master_run
          python_wheel_task: { package_name: lake_ingest, entry_point: open_master_run,
                               parameters: ["--source", "mes"] }
          timeout_seconds: 120
        - task_key: load_each_dataset
          depends_on: [ { task_key: open_master_run } ]
          for_each_task:
            inputs: "{{tasks.open_master_run.values.due_datasets}}"
            concurrency: 8
            task:
              task_key: land_one
              python_wheel_task: { package_name: lake_ingest, entry_point: land,
                                   parameters: ["--dataset", "{{input}}"] }
              max_retries: 2                 # reached only by passing errors: the lander
              min_retry_interval_millis: 60000   # ends data errors itself, as handled
        - task_key: close_master_run
          depends_on: [ { task_key: load_each_dataset } ]
          run_if: ALL_DONE                   # closes the master run and writes the marker
          python_wheel_task: { package_name: lake_ingest, entry_point: close_master_run }"""

# ------------------------------------------------------------------ ids and log rows
IDS = [
    ("master_run_id", "Ours", "One trigger of one job: all the datasets loaded together", "master_run_log, the batch-ready marker, every run_log row of that trigger"),
    ("job_run_id", "Databricks", "The Lakeflow job run", "Stored on master_run_log and run_log; joins system tables (timings, cost, skipped and queued runs)"),
    ("run_id", "Ours", "One dataset through one stage (land, silver update, gold window)", "run_log, step_log, file_log, error_log, dq_result, and _run_id on rows our jobs write"),
    ("task_run_id", "Databricks", "The task (or for-each iteration) that did the work", "Stored on run_log; links to the task's own log in Databricks"),
    ("update_id", "Databricks", "One update of a Declarative Pipeline", "Stored on run_log; joins the pipeline event log"),
    ("segment_id", "Ours", "One slice of a bulk load", "segment_run_log; run_log adds up its segments"),
    ("config fingerprint", "Ours", "The exact merged settings a run used", "config_snapshot; any run can be replayed with what it ran with"),
]

LOG_LEVELS = [
    ("master_run_log", "One per trigger of a job", "RUNNING, SUCCEEDED, PARTIAL, FAILED; counts of datasets attempted, succeeded, failed, skipped; run type; retry of which master run"),
    ("run_log", "One per dataset per stage", "STARTED, SUCCEEDED, FAILED, SKIPPED, BLOCKED; rows read, written, rejected; the watermark before and after; durations; cause class"),
    ("segment_run_log", "One per segment of a bulk load", "The segment's predicate, rows and status; the run adds them up"),
    ("step_log", "One per step inside a run", "check, land, tokenise, contract, quality, merge, reconcile: rows in and out, time taken"),
    ("file_log", "One per landing file", "Name, size, rows, checked or rejected and why, which run loaded it. The lander's list of what is new"),
    ("input_watermark", "One per input per domain", "How far in source time each input is loaded; the basis of completeness and freshness"),
    ("error_log", "One per failure", "Cause class (source down, schema change, bad data, our bug, platform, capacity), scrubbed message, passing or not"),
    ("dq_result", "One per rule per run", "Passed or failed, failing rows, action taken"),
]

RECORDER_CALLS = [
    ("open_master_run(source, trigger)", "Writes the master run row; returns its id. Times out after 10 seconds and retries twice; if it still cannot write, the job fails before any work."),
    ("open_run(dataset, stage)", "Writes the run row with all ids it can see (job run, task run, update id)."),
    ("step(name, rows_in, rows_out)", "One step row, measured for you. Step and quality rows are buffered and retried; a failure to log a step never fails the data work."),
    ("error(exc)", "Classifies the error, scrubs the message of data values, writes error_log, and says whether it is passing (retry) or not (end as handled)."),
    ("quality(results)", "Writes dq_result rows from DQX or the pipeline's expectations."),
    ("close_run(status, counts, watermark)", "Marks the run and stores its watermark in one Aurora transaction, after the Delta commit. If it cannot, the sweeper finishes the run later from the evidence in bronze."),
]

# ------------------------------------------------------------------ streaming
STREAM_RUNTIME = [
    ("There are no runs, so we cut windows, and always write one.", "Every 15 minutes the ops builder writes one run_log row per stream per window from the pipeline's progress: rows, lag, errors. If there was no progress and the pipeline is not running, the row says DOWN; a stopped stream is never just a missing row."),
    ("The bookmark is not ours.", "The stream's checkpoint and Kinesis' sequence numbers decide what is read. input_watermark records the newest event time in silver, which is what freshness and completeness use."),
    ("Outages are bounded.", "Kinesis keeps 7 days, so a stream down for less than that loses nothing; on restart it reads from its checkpoint."),
    ("Gold from streams is hourly, on its own clock.", "At 15 minutes past each hour a job builds the closed hour, and re-checks the last 2 days for readings that arrived late. Hours not yet caught up are marked incomplete."),
    ("Silent machines, but not alarm storms.", "A per-press check (no reading for 30 minutes in a planned shift) catches one quiet press. While the whole stream is down, the per-press check is held back, and one stream alert fires instead of hundreds."),
]

# ------------------------------------------------------------------ failures
FAILURES = [
    ("Source down or slow", "Mover: CloudWatch alarm on DMS lag or AppFlow failure", "AWS retries; the lander finds nothing new and ends as skipped; the source's bookmark stops moving", "Freshness goes red from the bookmark at the promised time; incident for the source owner"),
    ("DMS stops for hours, then resumes", "CloudWatch, and the bookmark", "DMS catches up from the source's change log (kept 72 hours); the lander loads the backlog over a few runs; gold hours stay incomplete until the bookmark passes them, then fill in", "Nothing, unless the outage outlasts the change log: then a full reload through the bulk job"),
    ("A partner or puller file is unreadable or short", "Lander, file check", "The file is rejected (moved to landing/_rejected, logged in file_log); the dataset's run ends FAILED as handled; other datasets carry on; master run PARTIAL", "The partner or source re-sends; the next run loads it"),
    ("A DMS change file is unreadable", "Lander, file check", "The dataset is BLOCKED at that file: no later change files are loaded, because skipping one would lose changes or apply them out of order. Its bookmark stops, so gold shows the hours as incomplete", "Repair the file, or reload that table through the bulk job; then the dataset unblocks"),
    ("Columns removed, renamed or retyped", "Silver, contract check", "That table's flow fails; silver stays as it was; bronze still has everything", "New contract version and mapping; then replay from bronze"),
    ("Bad rows", "Silver, quality rules", "Rows parked in quarantine with the reason; the rest carry on; stop only past the bad-share limit", "Steward reviews weekly; fixed rows are released and re-merged"),
    ("A full copy comes back short", "Silver, mass-delete guard", "The load stops before silver changes", "Check the source; re-pull"),
    ("A partner re-sends a corrected file", "Lander and silver", "Lands as a new file with a unique name; silver replaces the slice the contract names (dealer and month) with the newest file", "Nothing"),
    ("Job or cluster dies halfway", "Lakeflow task failure", "Retried up to 2 times (only passing errors reach Lakeflow); writes are idempotent", "Nothing, unless retries run out"),
    ("Aurora is slow or down", "Run recorder timeouts; job timeouts and duration health rules", "Jobs fail fast at their first task instead of hanging; stuck runs are finished by the sweeper", "Platform on-call, alerted by Databricks job alerts and the heartbeat alert, neither of which needs Aurora"),
    ("A bug in our code", "Any stage", "Fails; cause class 'our bug'; no retry", "Fix, release, then re-run the failed runs"),
]

RERUN = [
    ("Re-run failed", "Only the datasets that failed in a master run", "A queued run of the same lander job with run type rerun. Auto Loader and the file log pick up whatever was not loaded; nothing is read twice"),
    ("Replay from bronze", "Rebuild one silver table after a logic or contract fix", "A full refresh of that one table in its pipeline; bronze is the source of truth, so nothing is fetched from the source again"),
    ("Backfill", "Rebuild past gold windows on purpose, for example after a correction", "A plan in Git (dataset, windows, reason, cost) run by the bulk job on windows older than 2 days, so it never writes the partitions the normal job writes. Simple-fact materialized views are restated by a full refresh at night"),
    ("First load of a new dataset", "A new table, or a new source", "The bulk job, in segments, with its own checkpoint; the normal job takes over when it is done, so a big first load never holds back the rest of the source"),
    ("Re-extract", "Fetch from the source again", "Only for sources that can resend. Never for SAP, which moves its own delta token: replay from landing or bronze. For DMS: a table reload through the bulk job"),
]

SWEEPER = [
    ("Finds stuck runs.", "Every 15 minutes the ops builder lists runs still STARTED past their job's timeout."),
    ("Looks for evidence.", "If bronze holds rows with that run id, the commit happened: the run is closed as SUCCEEDED with counts from bronze and its watermark is stored. If not, it is closed as FAILED and the files stay unloaded for the next run."),
    ("Says what it did.", "Every sweep is logged, so a run closed by the sweeper is visible as such."),
]

NEW_DATASET = [
    ("YAML, reviewed.", "The dataset's settings, contract, rules and owners in one pull request."),
    ("Source side, generated.", "For DMS: the DBA enables CDC on the table (a checklist item), and the generator adds the table to its DMS task group; only that group pauses. For AppFlow or the puller: a new flow or pull."),
    ("Tables first.", "The deploy creates the empty bronze table and its marker entry from the contract, before any trigger refers to them."),
    ("First load in the bulk job.", "In segments, with its own checkpoint; then the normal lander job includes the dataset from the next run."),
]

# ------------------------------------------------------------------ observability working parts
OBS_PARTS = [
    ("Run recorder", "Every part logs the same way, through six calls, with timeouts", "Built in the framework (Azure SQL today); the Aurora adapter and timeouts are to do"),
    ("File log", "Every landing file: checked, loaded or rejected, by which run", "To build"),
    ("Input watermarks", "How far each input is loaded, in source time: completeness and freshness", "To build"),
    ("Ingest columns", "Rows say which run and file wrote them, and their order in the source", "Partly built: bronze columns exist; DMS and SAP order columns to add"),
    ("Pipeline wrapper", "Makes a Declarative Pipeline update look like any other run, and starts gold", "To build"),
    ("Ops builder and sweeper", "prod_ops every 15 minutes; finishes stuck runs", "To build; the health views exist in the framework for Azure"),
    ("Health views", "One row per dataset: last run, status, bookmark against target, rows against the usual band, failing rules", "Built for Azure SQL (v_dataset_health); to port"),
    ("Heartbeat", "A synthetic dataset through every layer every 15 minutes, watched by a Databricks SQL alert that does not need Aurora", "Designed in the framework (PL_HEARTBEAT); to build on Databricks"),
    ("Job health rules", "Duration and failure alerts from Databricks itself, for when our own logging is the problem", "To generate with the jobs"),
    ("Doctor", "A healthcheck before every deploy and on demand: database, secrets, buckets, grants, triggers, DMS tasks", "Built in the framework (lake-ingest doctor); AWS probes to add"),
]

HEALTH_COLS = """-- prod_ops.v_dataset_health: one row per dataset, the first thing on-call opens
SELECT d.dataset_name, d.tier, d.owner,
       r.status                          AS last_status,      -- incl. BLOCKED and DOWN
       w.as_of                           AS loaded_up_to,     -- the bookmark, in source time
       d.freshness_target_minutes,
       timestampdiff(MINUTE, w.as_of, current_timestamp()) AS minutes_behind,
       r.rows_written, b.rows_low, b.rows_high,              -- the usual band for this weekday
       q.rules_failed, q.rows_quarantined,
       f.files_rejected_today,
       c.cost_today_usd
FROM ops.dim_dataset d
LEFT JOIN ops.last_run r          USING (dataset_id)
LEFT JOIN ops.input_watermark w   USING (dataset_id)
LEFT JOIN ops.volume_band b       USING (dataset_id)
LEFT JOIN ops.quality_today q     USING (dataset_id)
LEFT JOIN ops.files_today f       USING (dataset_id)
LEFT JOIN ops.cost_today c        USING (dataset_id);"""

DAY = [
    ("Continuous", "Press and mixer sensors stream into bronze and silver"),
    ("Every 15 min", "MES changes land and load; the manufacturing pipeline follows on the marker; gold windows recompute; the ops builder refreshes freshness and sweeps; the heartbeat passes through"),
    ("Hourly, at :15", "Stream gold builds the hour that just closed, and re-checks the last 2 days"),
    ("Every 30 min, 06:00-22:00", "SAP orders and deliveries: AppFlow runs, then its lander"),
    ("01:00", "Nightly SAP full copies for objects without deletes in their delta; the sales pipeline follows"),
    ("Overnight", "Dealer sell-out files arrive; each starts its lander on arrival"),
    ("03:00", "Housekeeping: retention, erasures, VACUUM, the daily DMS reconcile"),
    ("06:00", "The night shift ends (shifts: 06:00, 14:00, 22:00, plant time)"),
    ("06:15", "Stream gold closes the 05:00-06:00 hour; the window recompute sets completeness for the night shift"),
    ("06:20", "Ops builder: tier-1 data products green, amber or red from their bookmarks; red pages on-call"),
    ("06:30", "OEE for the morning meeting, with completeness shown. Readings that arrive later restate the hour and say so"),
    ("09:00", "Warranty claims ready (tier 2)"),
]


# ------------------------------------------------------------------ drawings
def runtime_map():
    b = []
    a = b.append
    a(rect(20, 20, 1100, 52, "#E6EAF7") + tx(570, 42, "Run controller: Lakeflow Jobs generated from the metadata. One clock per source; silver on the batch-ready marker; gold called by silver", 13.5, "middle")
      + tx(570, 62, "reads dataset_view in Aurora · writes master_run_log · queues, never overlaps", 12, "middle", fill="#555"))
    cols = [("Sources", ["SAP", "MES database", "Quality lab, warranty", "Dealer files", "Press sensors"], "#F4F4F2"),
            ("Movers", ["DMS, AppFlow,", "Transfer Family,", "Kinesis, our puller"], "#FFF4D9"),
            ("Landing (S3)", ["unique file names", "the landing contract"], "#F3E3D3"),
            ("Lander (ours)", ["file check, tokenise,", "append to bronze,", "write the marker"], "#E6F4EC"),
            ("Silver builder", ["Declarative Pipeline", "per domain: contract,", "rules, AUTO CDC"], "#E6E6E6"),
            ("Gold builder", ["window recompute,", "completeness from", "input bookmarks"], "#F7E7B4"),
            ("Metric views", ["defined once;", "dashboards, Genie"], "#F8EBF1")]
    w, gap = 140, 20
    for i, (t, lines, f) in enumerate(cols):
        x = 20 + i * (w + gap)
        a(rect(x, 110, w, 150, f) + tx(x + w / 2, 136, t, 14, "middle", weight="700")
          + "".join(tx(x + w / 2, 160 + k * 19, ln, 12, "middle") for k, ln in enumerate(lines)))
        if i < len(cols) - 1:
            a(arr(x + w, 185, x + w + gap, 185))
        if 3 <= i <= 5:
            a(arr(x + w / 2, 72, x + w / 2, 110, dash=True))
    a(tx(20 + 2 * 160 + 70, 280, "the lander never talks to a source", 11.5, "middle", fill="#555"))
    a(rect(20, 300, 1100, 56, "#E0F1F7") + tx(570, 324, "Run recorder: run, step, file, error, quality and bookmark rows with the same ids, with timeouts", 14.5, "middle")
      + tx(570, 344, "Aurora runtime schema → ops builder every 15 minutes (and the sweeper) → prod_ops: dashboard, alerts, incidents", 12, "middle", fill="#555"))
    for i in range(3, 6):
        x = 20 + i * 160 + 70
        a(arr(x, 260, x, 300, dash=True))
    return svg(1140, 370, "".join(b), "The runtime map: sources, movers, S3 landing, our lander, the silver builder pipeline, the gold builder and metric views in a row. Above, the run controller gives each source one clock, starts silver from a batch-ready marker and gold from silver. Below, the run recorder takes the same log rows from every part into Aurora, and the ops builder copies them to prod_ops.")


def log_tree():
    b = []
    a = b.append
    a(rect(20, 20, 300, 60, "#E6EAF7") + tx(36, 46, "master_run_log", 15, weight="700") + tx(36, 66, "one trigger of the MES lander job", 12, fill="#555"))
    kids = [("run_log: press_event, land", 110), ("run_log: downtime, land", 180), ("run_log: work_order, land", 250)]
    for t, y in kids:
        a(f'<path d="M60,80 L60,{y + 25} L120,{y + 25}" fill="none" stroke="{INK}" stroke-width="1.4"/>')
        a(rect(120, y, 280, 50, "#E6F4EC") + tx(134, y + 31, t, 13))
    for k, s in enumerate(["file_log: 4 files checked", "step: tokenise, append", "dq_result rows"]):
        y = 108 + k * 34
        a(f'<path d="M400,135 L440,135 L440,{y + 15} L470,{y + 15}" fill="none" stroke="{INK}" stroke-width="1.2"/>')
        a(rect(470, y, 200, 30, "#fff", r=8) + tx(482, y + 20, s, 12))
    a(rect(720, 20, 400, 52, "#FFF4D9") + tx(736, 51, "batch-ready marker: MES, this master run", 13.5, weight="700"))
    a(f'<path d="M320,40 C500,20 620,30 720,44" fill="none" stroke="{INK}" stroke-width="1.4" stroke-dasharray="4 3" marker-end="url(#ahx)"/>')
    a(rect(720, 100, 400, 56, "#F7E7B4") + tx(736, 124, "run_log: manufacturing pipeline update", 13.5, weight="700") + tx(736, 144, "update id stored; input_watermark written", 12, fill="#555"))
    a(arr(920, 72, 920, 100, dash=True))
    a(rect(720, 184, 400, 50, "#F7E7B4") + tx(736, 214, "run_log: production fact, window recompute", 13))
    a(arr(920, 156, 920, 184, dash=True))
    a(tx(560, 330, "Every box carries the job run id from Databricks, so system tables add timings and cost to each one.", 13, "middle"))
    a(tx(560, 350, "Every row our jobs write carries the run id of the box that wrote it.", 13, "middle"))
    return svg(1140, 365, "".join(b), "The log hierarchy: one master run per job trigger, one run per dataset with its file, step and quality rows. The closing task writes a batch-ready marker, which starts the pipeline update (its own run, with input bookmarks), which calls the gold window recompute (its own run).")


# ------------------------------------------------------------------ page
FAQ = [
    ("Why not one big job from source to gold?", "Because sources arrive at different times. A job per source loads what has arrived; pipelines per domain run when a source has finished a batch. Nothing waits for the slowest source, and completeness tells everyone what has not arrived yet."),
    ("Why a batch-ready marker instead of triggering on bronze tables?", "Each dataset commits to bronze at a slightly different moment. A trigger on the tables fires on the first one and runs silver on a half-loaded source. The marker is written once, after the whole batch, so silver always sees a finished batch."),
    ("Why does a Declarative Pipeline need a wrapper task?", "The pipeline has its own event log and ids. The wrapper opens and closes our run row around each update, copies counts and expectation results across, and then starts gold, so on-call sees one kind of run everywhere and gold never starts in the middle of an update."),
    ("Why not let Lakeflow retry every failure?", "Lakeflow retries whatever fails. A bad file retried is still a bad file, and a retry after the file was moved away looks like success. So the lander ends data problems itself, as handled failures in our log, and only passing errors (a network blip, a busy cluster) reach Lakeflow's retry."),
    ("What if the logging database is down or slow?", "Every call to it has a timeout, so jobs fail at their first task instead of hanging. Databricks' own job alerts, duration rules and the heartbeat alert do not need our database, so the problem is still seen."),
]


def page():
    src_table = table(["Kind of source", "Examples here", "Brought in by", "What changes arrive", "Lands as", "How often"], SOURCES)
    lmode_table = table(["Landing", "Lander reads it with", "Remembers what it read in"], LANDER_MODES)
    notv1_table = table(["Not in v1", "Why"], NOT_V1)
    mstat_table = table(["Mover", "Set up how", "Status"], MOVER_STATUS)
    parts_table = table(["Part", "Does", "Reads", "Writes", "Runs as", "Safe to run twice because"], PARTS)
    cols_table = table(["Layer", "Columns added to every row", "So you can tell"], INGEST_COLS)
    order_table = table(["Kind of input", "Order of changes", "Deletes"], ORDERING)
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
<p class="lede">How the core actually runs: which sources come in and how, the parts that move and shape the data, what starts each one, how one load moves from a source system to a metric, how we know a number is complete, the ids and log rows that tie it together, what happens when something breaks, and how we watch it. The concept pages say what each layer does; this page says how it runs.</p>
<div class="sib"><a href="{AWS}">↑ The platform on AWS + Databricks</a><a href="{BASE}ingestion/">Ingestion</a><a href="{BASE}bronze-to-silver/">Bronze to silver</a><a href="{BASE}gold/">Gold</a><a href="{BASE}metadata-store/">Metadata store</a></div>
<nav class="toc"><b>On this page</b><ol>
<li><a href="#rules">Seven rules</a></li><li><a href="#sources">Sources and ingestion tech</a></li><li><a href="#map">The runtime map</a></li><li><a href="#parts">The ten working parts</a></li>
<li><a href="#order">Order, deletes and corrections</a></li><li><a href="#complete">Completeness and freshness</a></li><li><a href="#run">One run, step by step</a></li>
<li><a href="#jobs">Jobs and triggers</a></li><li><a href="#logs">Ids and log rows</a></li><li><a href="#stream">Streaming</a></li><li><a href="#fail">When something breaks</a></li>
<li><a href="#rerun">Re-runs, backfills and first loads</a></li><li><a href="#obs">Observability: the working parts</a></li><li><a href="#day">A day in the life</a></li><li><a href="#tested">How this was tested</a></li><li><a href="#faq">Questions</a></li></ol></nav>

<section id="rules"><p class="eyebrow">Start here</p><h2>Seven rules the whole runtime follows</h2>
<p>Everything below follows from these. If a design choice ever conflicts with one of them, the rule wins.</p>
{rules(PRINCIPLES)}</section>

<section id="sources"><p class="eyebrow">Sources and ingestion tech</p><h2>What we load, and what brings each one in</h2>
<p>Nine kinds of source cover a tyre maker. Five technologies bring them in: four AWS services (DMS, AppFlow, Transfer Family, Kinesis with SiteWise) and our own puller, built from the framework's existing connectors. All five deliver to the same landing area under one contract, which is why one lander can take it from there.</p>
{src_table}
<h3>How to pick, in order</h3>
<p>For a new source, ask these questions in order and stop at the first yes.</p>
{rules(PICK_ORDER)}
<h3>The landing contract: what every mover must deliver</h3>
{rules(LANDING_CONTRACT)}
<h3>How the lander reads each kind of landing</h3>
{lmode_table}
<h3>Not in the first version, and why</h3>
{notv1_table}
<h3>Where each mover stands</h3>
{mstat_table}
</section>

<section id="map"><p class="eyebrow">The runtime map</p><h2>Ten parts, three bands</h2>
<p>Read the middle row left to right: data moves from source systems to metrics. The band above decides when things run; the band below records everything that ran. Nothing in the middle row starts itself, and nothing runs without being recorded.</p>
<figure class="diagram">{runtime_map()}<figcaption>The middle row moves and shapes data; the top band starts it; the bottom band records it.</figcaption></figure></section>

<section id="parts"><p class="eyebrow">The working parts</p><h2>What each part does, reads and writes</h2>
<p>Each part has one job and a fixed contract. The last column is the most important: it is what lets the platform retry without a person checking.</p>
{parts_table}
<h3>Every row says where it came from</h3>
{cols_table}</section>

<section id="order"><p class="eyebrow">Order, deletes and corrections</p><h2>Changes applied in the right order, deletes never missed</h2>
<p>Silver keeps one row per real thing, with its history. That is only right if changes are applied in the order they happened, deletes are seen, and a fix to old data is told apart from a new change.</p>
{order_table}
{rules(GUARDS)}</section>

<section id="complete"><p class="eyebrow">Completeness and freshness</p><h2>Knowing a number is complete, not just on time</h2>
<p>Sources arrive at different speeds, and sometimes one stops. Without care, gold builds an hour from the inputs that happened to arrive and calls it done, and OEE is wrong with nobody told. These five rules prevent that.</p>
{rules(COMPLETENESS)}</section>

<section id="run"><p class="eyebrow">One run, step by step</p><h2>A quarter-hour of MES data, from database to gold</h2>
<p>Follow one load: changes to the press events table in the plant's MES database, picked up at 00:15 and in gold by 00:20. Times are illustrative.</p>
{rules(RUN_STEPS)}</section>

<section id="jobs"><p class="eyebrow">Jobs and triggers</p><h2>What starts what</h2>
<p>Each source has exactly one clock. Silver starts when a source has finished a batch, and gold starts when silver has finished. Nothing polls for no reason, and nothing starts on a half-written input.</p>
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
<p>The framework's run tables, plus two new ones (file_log and input_watermark), in the runtime schema of the metadata database.</p>
{levels_table}
<h3>The run recorder: six calls</h3>
{rules(RECORDER_CALLS)}
<h3>The sweeper: no run stays stuck</h3>
<p>The Delta commit and the log database are two separate systems, so a crash between them can leave a run marked as started forever. The sweeper closes such runs from the evidence.</p>
{rules(SWEEPER)}</section>

<section id="stream"><p class="eyebrow">Streaming</p><h2>Sensors fit the same model</h2>
<p>A stream never ends, so it has no runs of its own. These five rules make it look like everything else to on-call and to the dashboard.</p>
{rules(STREAM_RUNTIME)}</section>

<section id="fail"><p class="eyebrow">When something breaks</p><h2>Each failure has one place it is caught</h2>
<p>For each kind of failure: where it is caught, what the platform does by itself, and the one thing a person needs to do. Only passing errors are retried; the lander ends data problems itself, as handled failures, so a retry never hides a bad file.</p>
{fail_table}</section>

<section id="rerun"><p class="eyebrow">Re-runs, backfills and first loads</p><h2>Five ways to run again, none in the way of the normal runs</h2>
{rerun_table}
<h3>Adding a dataset to a running source</h3>
{rules(NEW_DATASET)}</section>

<section id="obs"><p class="eyebrow">Observability: the working parts</p><h2>What has to exist for anyone to see what ran</h2>
<p>The dashboard, alerts and incidents are described on <a href="{AWS}#ops">the platform page</a>. These are the parts underneath, and where each stands today. Two of them (job health rules and the heartbeat alert) deliberately do not depend on our own log database, so they still work when it does not.</p>
{obs_table}
{C.code(HEALTH_COLS, "The health view on-call opens first: one row per dataset, judged by its bookmark, not by its last run.")}</section>

<section id="day"><p class="eyebrow">A day in the life</p><h2>Twenty-four hours of the runtime</h2>
<p>What runs when on an ordinary day, for the plants' morning meeting at 06:30.</p>
{day_table}</section>

<section id="tested"><p class="eyebrow">How this was tested</p><h2>Twelve situations, walked through before building</h2>
<p>A reviewer who had not written this page walked twelve situations through it: a normal day, an SAP delete, DMS down for two hours, overlapping runs, one bad dataset out of twelve, silver starting mid-load, a reference row deleted, a partner re-sending a corrected file, the sensor stream down for 40 minutes, a three-month backfill, a slow log database, and a new dataset. Three failed and nine passed with gaps. The biggest finding was that gold could call an hour complete while an input was missing, so OEE could be wrong with nobody told; the completeness rules above are the fix. The other fixes are the one clock per source, the batch-ready marker, retries owned by the lander, the file log, unique file names with replacement rules, ordering and deletes for DMS and SAP, the mass-delete guard, corrections that restate history, timeouts and the sweeper, and the bulk job.</p></section>

<section id="faq"><p class="eyebrow">Questions</p><h2>Questions engineers ask</h2>{faq}</section>

<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2>
<p><a href="{AWS}">↑ The platform on AWS + Databricks</a> · <a href="{BASE}ingestion/">Ingestion</a> · <a href="{BASE}bronze-to-silver/">Bronze to silver</a> · <a href="{BASE}gold/">Gold</a> · <a href="{BASE}metadata-store/">Metadata store</a> · <a href="{BASE}testing/">Test architecture</a></p></section>"""
    desc = "How the core ETL runs on AWS and Databricks: nine kinds of source and five ingestion technologies, ten working parts, completeness from input bookmarks, one run step by step from source to gold, jobs and triggers, ids and log rows, streaming, failures, re-runs and the observability parts."
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
