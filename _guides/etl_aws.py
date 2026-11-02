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
import etl_scenarios as SC  # noqa: E402  (the design-test table)
import etl_settings as ST  # noqa: E402  (the settings registry)
try:
    import etl_scenario_results as SR  # noqa: E402  (verdict per check, from the latest run)
except ImportError:
    SR = None

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
    ("Movers never write to bronze; the lander never talks to a source.", "AWS services (and our puller) bring data to S3 landing; our one lander takes it from there. Every batch source enters the same way, and a source outage never stops the other sources. Sensor streams are the one stated exception: Kinesis is their landing and the streaming table their lander, because readings carry no personal data and need seconds, not files."),
    ("Everything is a run, and every run leaves the same rows.", "A file load, a pipeline update and a 15-minute slice of a stream all get a run id and the same log rows, so one dashboard and one set of alerts cover all of them."),
    ("Every step can run twice.", "Re-running a step after a crash gives the same tables as running it once. That is what makes retries, re-runs and backfills safe without a person checking."),
    ("A number is complete only when every input has caught up.", "Each input carries its own bookmark: how far in source time it has been loaded. A gold hour is complete only when every input's bookmark is past the end of that hour. Otherwise it is published as incomplete, never as right."),
    ("One clock per source; Lakeflow runs the work.", "Each source has exactly one thing that says 'new data is ready': a schedule, or for AppFlow and partner uploads the AWS event that the transfer finished. Everything that processes batch data runs in Lakeflow Jobs; the streaming pipelines run continuously and are watched by the ops builder. Two clocks on one path is how runs overlap, wait or never start."),
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
    ("Unique names, never overwritten.", "Every file in landing has a name nobody else uses. Partners upload into their own staging folder; a Transfer Family workflow (a custom Lambda step) copies each upload to landing under a unique key (partner, file, arrival time) and removes it from staging. A re-sent or corrected file is therefore a new file; what it replaces is a rule in silver, written in the dataset's contract."),
    ("Complete or invisible.", "A file appears only when complete (S3 writes are all-or-nothing; uploads are copied to landing only after they finish)."),
    ("Say how many.", "Our puller writes a manifest with the row count. For AppFlow, an EventBridge rule on the flow-run event calls a small Lambda that writes the manifest and starts the lander through the Jobs API. Partners send a control file where agreed. DMS cannot, so DMS loads are reconciled daily per table against DMS's own table statistics."),
    ("Say what was deleted, and in what order.", "DMS adds its operation flag, commit time and change sequence to every row (full-load rows too). SAP rows carry the extractor's change mode where it exists. Full copies are compared with the previous copy in silver."),
    ("Keep the source's history long enough.", "Each database keeps its change log at least 72 hours, so DMS can catch up after an outage without a full reload."),
    ("No transforming.", "Movers change the format at most (to Parquet). Every rule about content lives in the lander and after."),
]

LANDER_MODES = [
    ("Files (DMS, AppFlow, puller, SFTP, uploads)", "The lander lists only the date folders that can hold new files, takes the files that are new or checked (never loaded, rejected or held ones), checks the new ones (readable, header, row count) and reads exactly that list with a plain batch read. A batch keeps its number until it is loaded, so a re-run reads the same batch with the same transaction id and it cannot land twice. A dataset takes at most a set number of files or gigabytes per run, so a large first load spreads over several runs and never holds back the other datasets. Nothing lists the folder on its own, so nothing unchecked can slip in between the check and the read", "The file log. Each batch is appended with a transaction id (the dataset and the batch number from the file log), so a batch committed before a crash is never appended twice"),
    ("DMS change files", "As files, read in commit order, keeping operation flag, commit time and change sequence as columns; silver applies them with AUTO CDC", "As above; a bad file blocks the dataset (see failures)"),
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

# ------------------------------------------------------------------ the standard transforms (bronze to silver)
TRANSFORM_PRINCIPLES = [
    ("Generic, never domain-specific.", "Every transform from bronze to silver is the same code for every table, switched on and tuned per column in the metadata. Business logic (joining sources, derived measures, totals) belongs after silver, in the integrator and gold."),
    ("No free-form SQL in this step.", "Only the transforms in the list below. A need they cannot meet is a new generic transform, added once with its own tests, or logic for the integrator or gold."),
    ("Silver's shape is ours, not the source's.", "Silver holds the columns listed for the dataset, with the names and types we chose. Bronze keeps everything the source sent, so nothing is lost and a column can be added later by replay."),
    ("A value is never silently lost.", "A value that cannot be converted goes to quarantine, or is set empty and counted, as the column says. It never just becomes empty without a trace."),
]

STAGES = [
    ("1 Contract check", "On the bronze columns: every required column present, types compatible (see schema changes below)", "required, data_type, contract version", "To build"),
    ("2 Select, extract and rename", "Only the listed columns go on, each can be renamed; for JSON payloads, only the listed paths are extracted into typed columns, and arrays of child records become their own silver table", "silver.columns, silver_column_name, source_path, explode_path", "Rename, exclude and flatten built; 'listed only' to build"),
    ("3 Hygiene", "Trim, collapse spaces, empty text to NULL, strip control characters and byte-order marks, normalise unicode and line endings", "On by default for text; transforms, skip lists", "Built"),
    ("4 Parse and type", "Convert to the silver type using the column's formats: dates, timestamps, comma or point decimals, epoch numbers, booleans; widen integers; one decimal scale", "silver_data_type, date_format, timestamp_format, decimal_separator, on_cast_failure", "Built; formats and the failure action to add"),
    ("5 Time", "Convert to UTC from the source's time zone; add the plant's local time beside it", "source_timezone, local_time_zone_from", "UTC built; source zone and local column to add"),
    ("6 Standardise values", "Upper-case codes; ISO country and currency codes; email and phone formats; unit conversion by factor; code mapping from a lookup table; a default for empty values", "column_role, transforms, unit_from / unit_to, code_map, null_replacement", "Written but not switched on in the engine; units and code mapping to build"),
    ("7 Personal data", "Tokenise, hash, mask or redact by the column's personal-data class", "pii_class, pii_policy", "Built"),
    ("8 Row filter", "Drop rows that match a declared condition (test records, a cancelled flag); dropped rows are counted", "row_filter", "To build"),
    ("9 Quality rules", "Rules from dq_rule; failing rows to quarantine with the reason", "dq_rule", "Built (SQL rules); DQX behind the same port"),
    ("10 Duplicates", "None, exact, first or latest per business key, or flag only", "dedup.mode, dedup.business_keys, dedup.order_by", "Built"),
    ("11 Keys", "Business key; conformed key from a mapping table (an unmapped code becomes 'unknown' and raises an alert)", "is_primary_key, key_map", "To build"),
    ("12 History and deletes", "Append, SCD type 1, SCD type 2 or snapshot; soft deletes; changes in source order", "dataset_kind, history, history_track_columns", "Designed"),
    ("13 Provenance", "Run id, load time, record hash, source file, batch", "None: always on", "Built"),
]

COLUMN_SETTINGS = [
    ("silver.columns (dataset)", "declared, all_except_excluded", "declared", "2"),
    ("silver_column_name", "a name", "the source name", "2"),
    ("source_path", "a path into a JSON payload, such as $.order.id", "none (a plain column)", "2"),
    ("explode_path, parent_keys (dataset)", "the array of child records; the keys carried down", "none", "2"),
    ("array_strategy", "keep, join_as_text, take_first", "keep", "2"),
    ("required", "true, false", "true for keys, false otherwise", "1"),
    ("silver_data_type", "a Spark SQL type", "the bronze type", "4"),
    ("date_format, timestamp_format", "a pattern such as dd.MM.yyyy", "ISO 8601", "4"),
    ("decimal_separator", "point, comma", "point", "4"),
    ("on_cast_failure", "quarantine, null_and_count, stop", "quarantine", "4"),
    ("source_timezone", "an IANA zone such as Europe/Budapest", "UTC", "5"),
    ("local_time_zone_from", "the column holding the plant", "none", "5"),
    ("column_role", "code, identifier, measure, text", "none", "6"),
    ("transforms", "a list of opt-in transforms", "none", "3, 6"),
    ("unit_from, unit_to", "units such as lbf and N, F and C", "none", "6"),
    ("code_map", "the name of a mapping table", "none", "6"),
    ("null_replacement", "a value", "none", "6"),
    ("pii_class", "none, name, email, phone, free_text and others", "none", "7"),
    ("row_filter (dataset)", "a declared condition", "none", "8"),
    ("is_primary_key, key_map", "true or false; a mapping table", "false; none", "11"),
    ("dataset_kind (dataset)", "master, transaction, event, snapshot", "required", "12"),
    ("history (dataset)", "append, scd1, scd2, snapshot", "from dataset_kind", "12"),
    ("history_track_columns (dataset)", "a list of columns", "all listed columns", "12"),
]

CAST_FAILURE = [
    ("quarantine", "The row goes to quarantine with the column, the value's problem and the rule; the rest of the table carries on", "Keys, measures, dates: anything a number depends on (the default)"),
    ("null_and_count", "The value is set empty and the failures are counted in the quality results", "Descriptive text the business can live without"),
    ("stop", "The table stops", "Rare: critical reference data where a bad value means the whole extract is wrong"),
]

SCHEMA_CHANGES = [
    ("A new column", "Kept (personal-data sources: the file is held)", "Ignored until someone lists it", "'New column seen', low"),
    ("A listed column is removed", "-", "Required column: the table stops. Optional column: filled with empty values and a warning", "'Schema changed'"),
    ("A listed column is renamed", "Kept under the new name", "Stops (it looks like a removal). Fixed by mapping the new source name to the same silver name, so silver does not change at all", "'Schema changed'"),
    ("A type is widened (int to bigint, longer text, more decimals)", "Kept", "Accepted automatically when the silver type can hold it", "None"),
    ("A type is narrowed or changed (text to number, number to text)", "Kept", "Stops", "'Schema changed'"),
    ("We add a column to silver", "-", "Filled from the next run; older rows refilled from bronze by a replay", "Release note"),
    ("We remove a column from silver", "-", "Never at once: it stops being filled for one contract version, then is removed with notice", "Release note"),
]

JSON_RULES = [
    ("Bronze keeps the payload whole.", "A JSON payload (an API response, an event) lands in bronze as one column, stored as VARIANT (Databricks' type for semi-structured data, " + CHECK + ") or as text, untouched. Nothing is flattened on the way in, so a field nobody needed today is still there tomorrow."),
    ("Silver extracts only listed paths.", "Each silver column names its path in the payload (source_path, for example $.order.customer.id) and its type. Paths not listed stay in bronze. This is the same rule as listed columns: the payload's shape is the source's, silver's shape is ours."),
    ("Arrays of child records become their own table.", "An order with an array of lines gives two silver tables: order headers, and order lines with the order's key. The lines are a second dataset reading the same bronze table, with explode_path naming the array and parent_keys naming the keys it carries down. One row per real thing, at every level."),
    ("Small arrays of values stay as arrays.", "A list of tags or codes on one record stays an array column, or is joined into text, as the column says (array_strategy). Only arrays of records are split into tables."),
    ("Payload changes follow the schema rules.", "A new field is a new column (ignored until listed). A listed path that disappears is a removed column (required: stop; optional: empty with a warning). A value of the wrong type follows the column's on_cast_failure."),
]

JSON_EXAMPLE = """# bronze.dealer_api.orders: one row per API response, payload kept whole
#   payload = {"order": {"id": "SO-1001", "dealer": {"code": "D-77"},
#              "date": "31.10.2026", "lines": [{"sku": "205/55R16", "qty": "4"},
#                                               {"sku": "195/65R15", "qty": "2"}]}}

# silver.dealer_orders  (one row per order)
columns:
  - { name: order_id,    source_path: "$.order.id",          type: STRING, is_primary_key: true }
  - { name: dealer_code, source_path: "$.order.dealer.code", type: STRING, column_role: code }
  - { name: order_date,  source_path: "$.order.date",        type: DATE,   date_format: dd.MM.yyyy }

# silver.dealer_order_lines  (one row per line: a second dataset on the same bronze table)
explode_path: "$.order.lines"
parent_keys:  { order_id: "$.order.id" }
columns:
  - { name: sku, source_path: "$.sku", type: STRING, column_role: code, is_primary_key: true }
  - { name: qty, source_path: "$.qty", type: INT, on_cast_failure: quarantine }"""

HISTORY_KINDS = [
    ("Master and reference data", "Press, material, dealer, customer, plant, defect codes", "SCD type 2", "Facts join as of the event (a tyre's compound at cure time, the ideal cycle time that month), which needs the old versions"),
    ("Transactions that change status", "Sales order lines, deliveries, warranty claims, work orders", "SCD type 1; type 2 where the business needs the past state", "Usually only the current state matters, and bronze keeps every change for audit. OTIF needs the date first promised, so that dataset is type 2"),
    ("Events and readings", "Press events, sensor readings, downtime, test results", "Append", "They never change; duplicates removed by event id"),
    ("Periodic snapshots", "Daily stock, open orders at month end", "Snapshot: append with the snapshot date", "Each day is its own fact, not a version"),
]

HISTORY_RULES = [
    ("Only chosen columns make a new version.", "history_track_columns lists the columns whose change opens a new version; changes to the others (a last-updated stamp, a free-text note) update the current version in place. Without this, noisy columns multiply rows."),
    ("The kind sets the default.", "dataset_kind (master, transaction, event, snapshot) sets the history, so most datasets need no history setting at all."),
    ("Changing a dataset's history type is a replay.", "Moving a table from type 1 to type 2 rebuilds it from bronze, which still holds every change, so history is filled in for the past too."),
]

TRANSFORM_DECISIONS = [
    ("D1", "Silver takes only the listed columns (silver.columns = declared) by default; 'all except excluded' stays as an opt-in", "Agreed"),
    ("D2", "A failed conversion never silently becomes empty; the default action is quarantine", "Agreed"),
    ("D3", "The schema change rules above, with required per column and minor or major contract versions", "Agreed"),
    ("D4", "No free-form SQL from bronze to silver; only the standard transforms", "Agreed"),
    ("D5", "The thirteen stages, in this order", "Agreed"),
    ("D7", "JSON stays whole in bronze; silver extracts only listed paths; arrays of child records become their own silver table", "Agreed"),
    ("D6", "History by dataset kind: type 2 for master data, type 1 for transactions (type 2 where needed), append for events, snapshot for snapshots; tracked columns only", "Agreed"),
]

# ------------------------------------------------------------------ the working parts
PARTS = [
    ("1 Mover", "Brings data from a source to S3 landing (or Kinesis, for streams)", "source_config", "Files in landing under the landing contract", "AWS DMS, AppFlow, Transfer Family, SiteWise and Kinesis, or our puller", "Unique file names; a re-sent file is a new file"),
    ("2 Run controller", "Starts the work: one clock per source, a marker for silver, the wrapper for gold", "dataset_view, schedules, triggers, markers", "master_run_log; the job run", "Lakeflow Jobs, generated from metadata", "Runs queue instead of overlapping; a run with nothing due ends as skipped"),
    ("3 Lander", "Landing to bronze: picks new files from the file log, checks them, tokenises personal data, adds ingest columns, appends; writes the batch-ready marker", "dataset_view, the file log, the suppression list", "Bronze tables, file_log, run_log and step_log rows, the marker", "Our PySpark job, one task per dataset", "The file log says what was read; each batch is appended with a transaction id, so it lands once"),
    ("4 Silver builder", "Bronze to silver: the thirteen standard stages (contract, select, clean, type, time, standardise, personal data, filter, quality, duplicates, keys, history, provenance), replacement rules", "Bronze, dq_rule, dataset_config", "Silver tables, quarantine tables, the pipeline event log", "A Declarative Pipeline per business domain, generated, started by markers", "AUTO CDC orders changes by a defined sequence, so reprocessing gives the same result"),
    ("5 Integrator", "Joins sources into one picture: MES production with SAP orders, materials mapped", "Silver tables, key mappings", "silver.integrated tables", "Materialized views in the same pipeline", "A materialized view is a result, not an append"),
    ("6 Gold builder", "Silver to gold: star schemas, multi-input facts, completeness per window; the only writer of each gold fact", "Silver, integrated silver, corrections, input watermarks", "Gold facts and dimensions", "Materialized views for simple facts; our window-recompute job for multi-input facts", "Each window is replaced whole (replaceWhere on date partitions), never patched, and only one job writes a gold fact"),
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
    ("DMS changes", "Sequence by commit time, then DMS's change sequence (AR_H_CHANGE_SEQ), so two changes in the same instant keep their order. Full-load rows carry an operation flag too (IncludeOpForFullLoad). Every load of a table has a generation number: a reload starts a new generation, its full-load rows sort after everything earlier and before its own changes, so stale changes can never win.", "Delete when _op = 'D'"),
    ("SAP deltas", "Sequence by the extraction run, then the extractor's change counter where it has one (" + CHECK + " per object).", "Delete when the change mode says deleted; objects whose delta does not carry deletes are loaded as a nightly full copy instead"),
    ("Full copies (puller, snapshots)", "Each copy is a snapshot in time. Silver compares it with the previous one (AUTO CDC from snapshot).", "A row missing from the new copy is deleted, unless the mass-delete guard stops the load"),
    ("Partner files", "Order by arrival time.", "Each dataset's contract says what a file replaces, for example all rows for that dealer and month; silver replaces that slice with the newest file"),
    ("Streams", "Event time; duplicates removed by reading id.", "Readings are never deleted"),
]

GUARDS = [
    ("Deletes are soft.", "Silver never removes a row. In history tables (SCD2) a delete closes the current version: _valid_to is set and _is_deleted is true. In tables without history, the row stays with _is_deleted true. Current views, and every metric, leave deleted rows out, so a deleted order line stops counting in sales."),
    ("The mass-delete guard runs in the lander, before bronze.", "For a full copy, the lander compares the keys in the checked files with silver's current keys before appending anything. If more than a set share would be deleted (5% by default, set per dataset), nothing is appended, the files are held, the dataset is BLOCKED and the 'mass delete stopped' alert fires. Bronze never holds the short copy, so no later pipeline update can apply it. A pull that came back short matches its own manifest, so only this guard catches it."),
    ("Deleted members stay in dimensions.", "A decommissioned press keeps its row in gold's press dimension, flagged, so old facts still find it. Facts join dimensions as of the event time, never just to the current row."),
    ("A change is not a correction.", "A change is something new in the world (a press gets a new mould): history keeps the old value up to that date. A correction says the old value was wrong (the ideal cycle time was always 92 seconds, not 95). Silver keeps what the source said; corrections live in their own table (silver.corrections: entity, field, corrected value, applies from, applies to, who, why, status), and gold lays the active ones over silver when it builds a window."),
    ("Corrections reach gold only through a backfill plan.", "A new correction is pending. Only the window-recompute job reads corrections, and only active ones; materialized views never read the corrections table, so a fact or dimension that needs corrections is built by the recompute job. The backfill plan activates a correction and says which windows to rebuild and when, so a correction never restates months by itself at a busy hour. Activating a correction is not an input change for the normal recompute; only the plan rebuilds its windows."),
]

SCHEMA_DRIFT = [
    ("A new column, source without personal data.", "Kept in bronze as rescued data and ignored until someone maps it. The contract check does not stop on an added column. A low-priority 'new column seen' note goes to the steward."),
    ("A new column, source with personal data.", "The file is held in the personal-data landing bucket (kept up to 7 days while held, instead of 1), the dataset is BLOCKED and the 'schema changed' alert fires, because an unknown column there could be personal. Its name is logged; its values never are. Once the contract says what it is, the held files load. Personal data is not kept waiting indefinitely: if the contract is not updated within 7 days, the held files are deleted (the alert escalates on day 5) and the source re-sends after the fix."),
    ("A removed, renamed or retyped column.", "Silver's contract check stops that table; silver stays as it was and the 'schema changed' alert goes to the source owner named in the contract. For sources without personal data, bronze still holds everything, so after the new contract version the table is replayed from bronze; for personal-data sources the held files are loaded under the new contract. SAP is never asked to re-extract."),
]

PERSONAL = [
    ("Tokenise before bronze.", "Names, phone numbers and emails are replaced by random tokens; the real values go only to the token vault (prod_pii_vault). Random, so deleting the vault entry really does make the data anonymous."),
    ("Scan free text.", "Free-text fields such as warranty notes go through a personal-data detector behind a port; names it finds are tokenised too."),
    ("Check the suppression list.", "People who asked to be erased are not loaded again."),
    ("Leave nothing behind.", "An hourly purge job deletes personal-data landing files the file log marks loaded more than 23 hours ago, so none outlives a day; held files are kept up to 7 days; a lifecycle rule at 8 days is only the backstop. No log row holds a real value: error messages are scrubbed, file_log reasons name the problem not the content, and dq_result holds counts and tokenised keys only."),
]

SETTINGS = [
    ("Every run records its settings.", "Lander runs store the merged settings in config_snapshot by their fingerprint. A pipeline is generated from settings too, and carries their fingerprint as a pipeline parameter; the wrapper stores it on the update's run row. Any run can say exactly which settings it used."),
    ("A settings change is a release.", "Settings go through the same release path as code. Changes to quality limits, watermarks, replacement rules and grants always take the full gates; other settings take the lighter path."),
    ("A change applies from the next run.", "A run in progress keeps the settings it started with; the next run picks up the new ones, and the logs show which run used which."),
]

ALERTS = [
    ("Dataset blocked", "A DMS file failed its check, a full copy hit the mass-delete guard, or a personal-data source changed shape (the schema-changed alert goes to the source owner too)", "High for tier-1 inputs, Medium otherwise", "The source's engineer; repeats once a day while blocked, as one incident"),
    ("Master run PARTIAL", "Some datasets of a trigger failed", "Medium", "The source's engineer"),
    ("Freshness missed", "A dataset's bookmark is behind its target", "From the data product's tier", "Data product owner and on-call"),
    ("Schema changed", "A contract check stopped a table", "Medium", "The source owner named in the contract"),
    ("Mass delete stopped", "The guard stopped a full copy", "High", "The source's engineer"),
    ("Stream down", "A streaming pipeline stopped, or windows marked DOWN", "High", "On-call; per-press alerts held back meanwhile"),
    ("Press silent", "No reading from one press for 30 minutes in a planned shift", "High (OEE is tier 1)", "Plant maintenance and on-call"),
    ("Heartbeat missing", "No heartbeat row for 30 minutes (a Databricks SQL alert, independent of Aurora)", "High", "Platform on-call"),
    ("Job slow or failed", "Databricks job health rules and failure notifications", "High", "Platform on-call"),
    ("Runs swept", "The sweeper closed stuck runs", "Low", "Platform team, next working day"),
    ("New column seen", "An added column kept as rescued data", "Low", "The steward"),
]

COMPLETENESS = [
    ("Every input has a bookmark in source time.", "The lander writes how far bronze is loaded after every run, empty runs included: for DMS the newest commit time; for SAP, SaaS and the puller the extraction time of the run; for partner files the business date of the newest file. The wrapper writes how far silver has applied it after each pipeline update. Streams write the newest event time, per machine."),
    ("Quiet sources still move forward.", "A run that finds nothing new still moves the bronze bookmark to the time it looked; for DMS, while the task is running and its source latency is low (CloudWatch), that is 'now minus the latency', and a stopped task or a large latency freezes it. Partner files start no run when nothing arrives, so their bookmark is the business date of the newest file and freshness is judged against the next expected delivery: on a quiet night nothing is expected and nothing is late. When bronze holds nothing silver has not applied, the silver bookmark is set equal to the bronze one by the ops builder, so a quiet source stays green without running silver."),
    ("Streams are tracked per machine.", "One silent press does not move a stream's newest event time, so the stream's bookmark is kept per press. Presses not in a planned shift are left out."),
    ("A window is complete when every input is past its end.", "The window-recompute job marks a press-hour complete only when every input it needs, including that press's sensor bookmark, is past the end of the hour (plus the late allowance for streams). Otherwise the hour is published as incomplete, left out of OEE's top and bottom, and the dashboard says so."),
    ("Incomplete hours are revisited.", "Each recompute run also takes the incomplete hours whose inputs have now caught up, even if no row in them changed. When the ops builder moves a bookmark past an incomplete hour, it queues a recompute run."),
    ("Freshness is the bookmark, not the last run.", "A dataset is fresh when its silver bookmark is within its target, whatever its runs say. A source that went quiet because it broke goes red; one that is genuinely quiet stays green."),
    ("Every rebuild of a published window is a restatement.", "Whether a late input caught up, a partner corrected a file, or a backfill ran, every window rebuilt after it was first published is logged in ops as a restatement and shown on the dashboards."),
]

# ------------------------------------------------------------------ the run, step by step
RUN_STEPS = [
    ("All the time: DMS lands change files.", "AWS DMS reads the MES database's change log and writes Parquet files to landing/mes/<table>/<date>/, each row with its operation flag, commit time and change sequence."),
    ("00:15:00  One clock starts the lander.", "The MES lander job runs on a 15-minute schedule; that is its only trigger. If the previous run is still going, the new one waits in the queue instead of overlapping."),
    ("00:15:02  Open the master run.", "The first task writes the master_run_log row (RUNNING), reads dataset_view for every enabled MES dataset, stores the merged settings once in config_snapshot, and lists datasets with files not yet loaded. If none has, it moves each dataset's bronze bookmark by its quiet rule (a stopped DMS task keeps it frozen) and closes the master run as SKIPPED."),
    ("00:15:05  One task per dataset, eight at a time.", "Each opens its run_log row (STARTED) with the master run id, job run id and task run id."),
    ("00:15:06  Check the files, then load exactly those.", "The new files are checked (readable, expected header) and written to file_log as one numbered batch, status checked. The lander reads exactly that list, tokenises personal columns, adds the ingest columns and appends to bronze with the batch's transaction id."),
    ("00:15:40  Close the run after the commit.", "After the Delta commit the file log marks the batch loaded, and run_log becomes SUCCEEDED with rows read, written and rejected and the newest commit time as the run's watermark, in one Aurora transaction. If that write fails, the sweeper finishes it later from the evidence in bronze."),
    ("00:15:45  Close the master run and write the marker.", "The closing task runs even after failures. It marks the master run SUCCEEDED, PARTIAL (some datasets failed or are blocked) or FAILED, and writes the batch-ready marker: one row per dataset that loaded (dataset, master run, status) in that source's own marker table (prod_ops.batch_ready_<source>), a Unity Catalog Delta table written with Spark, so each domain's trigger watches only its own sources; blocked datasets get no row. The job itself ends green when every failure was a handled data problem; PARTIAL raises its alert from our log, not from a job failure."),
    ("00:16:00  The marker starts silver.", "The manufacturing wrapper job is triggered by updates to the marker tables of its sources (MES, the press master), not by each bronze table, so it never runs on a half-loaded source. It opens a run_log row, starts the pipeline update itself through the Pipelines API, stores the update id it gets back and the settings fingerprint the pipeline was generated from, and waits for the update to finish."),
    ("00:16:05  The silver pipeline runs.", "The thirteen standard stages, AUTO CDC in the defined order, soft deletes."),
    ("00:19:30  The wrapper closes the update and starts gold.", "It copies rows, expectation results and errors from the pipeline's event log into our tables, writes each input's bookmark to input_watermark, closes the run, then starts the window-recompute job directly (never on a table trigger, which could fire in the middle of an update)."),
    ("00:20:00  Gold, with completeness.", "The recompute (the only writer of the production fact) takes the hours that changed in any input, plus any queued backfill chunk, rebuilds them whole with corrections laid over silver, and marks each hour complete only if every input's bookmark is past its end. Rebuilt hours that were already published are logged as restatements."),
    ("00:30:00  The ops builder sees it.", "It copies the runtime rows into prod_ops, joins job runs and cost from system tables, reads skipped and queued runs too, and updates freshness from the bookmarks."),
]

TRIGGERS = [
    ("Schedule", "Every DMS source (its files arrive all the time, so a clock is calmer than file events); the puller", "The lander job of that source"),
    ("AppFlow finished", "SAP and SaaS sources: an EventBridge rule on the flow-run event calls a Lambda that writes the manifest and starts the lander through the Jobs API", "The lander job of that source, so there is one clock: AppFlow's"),
    ("Upload copied", "Partner files and uploads: the Transfer Family workflow's Lambda step starts the lander after copying the file to landing", "The lander job of that source"),
    ("Table update on the marker", "Silver: runs when one of its sources has finished a batch", "The domain wrapper job, which starts the pipeline update through the API"),
    ("Called by the wrapper, the stream hour job or the ops builder", "Gold multi-input facts: after a pipeline update, after a sensor hour closes, or when bookmarks pass incomplete hours", "The window-recompute job, queued, never two at once"),
    ("Continuous", "Sensor streams", "The streaming pipeline, always on"),
    ("Manual or API, queued", "Re-runs, first loads, backfill plans, the heartbeat test", "A queued run of the lander or recompute job, or the bulk job for first loads, with a run type that says why"),
]

JOBS = [
    ("Lander job", "One per source", "Open, a for-each over due datasets (concurrency from source_config), close and write the marker", "Its one clock (schedule, AppFlow finished, or upload copied)"),
    ("Bulk job", "One per source without DMS", "First loads and full reloads for puller, AppFlow, historian and file sources, in segments; it writes to the same file log, so the lander job carries on exactly where it stopped. DMS tables use DMS's own full load instead, whose rows carry an operation flag and sort before every change", "Manual or API"),
    ("Domain wrapper and pipeline", "One per business domain (manufacturing, quality, sales, aftermarket)", "A small job that starts the domain's Declarative Pipeline update (silver, integrated silver, simple gold) through the API, records it, and calls gold", "Table update on its sources' markers"),
    ("Window-recompute job", "One per multi-input gold fact; the only writer of that fact", "Changed windows from the last update, plus one chunk of any queued backfill plan; corrections laid over silver; completeness; reconcile; record", "Called by the domain pipeline's wrapper; queued, never two at once"),
    ("Streaming pipeline", "One per stream family (press sensors, mixer sensors)", "Kinesis to bronze to silver per minute", "Continuous"),
    ("Stream hour job", "One per stream family", "Sensor aggregates for the closed hour and a re-check of the last 2 days (an input to gold); then calls the window recompute", "Hourly, at 15 minutes past"),
    ("Ops builder", "One", "Copy runtime rows, join system tables and CloudWatch, freshness, sweep stuck runs, alerts", "Every 15 minutes"),
    ("Personal-data purge", "One", "Deletes personal-data landing files loaded more than 23 hours ago, and held files past 7 days", "Hourly"),
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
    ("master_run_log", "One per trigger of a job", "RUNNING, SUCCEEDED, PARTIAL, FAILED, or SKIPPED when nothing was due; counts of datasets attempted, succeeded, failed, blocked; run type; retry of which master run"),
    ("run_log", "One per dataset per stage", "STARTED, SUCCEEDED, FAILED, SKIPPED, BLOCKED; rows read, written, rejected; the watermark before and after; durations; cause class"),
    ("segment_run_log", "One per segment of a bulk load", "The segment's predicate, rows and status; the run adds them up"),
    ("step_log", "One per step inside a run", "check, land, tokenise, guard, contract, quality, merge, reconcile: rows in and out, time taken"),
    ("file_log", "One per landing file", "Name, size, rows, which batch, and a status: checked, loaded, rejected or held, with the reason (never the content). The lander takes every file that is new or checked (never loaded, rejected or held)"),
    ("input_watermark", "One per input", "Two bookmarks in source time: how far bronze is loaded (written by the lander on every run, empty runs too) and how far silver has applied it (written by the wrapper after each pipeline update, and set equal to the bronze bookmark by the ops builder for inputs with nothing waiting). For streams, the stream hour job writes the per-press bookmarks. The basis of completeness and freshness"),
    ("error_log", "One per failure", "Cause class (source down, schema change, bad data, our bug, platform, capacity), scrubbed message, passing or not"),
    ("dq_result", "One per rule per run", "Passed or failed, failing row count, action taken; tokenised keys only"),
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
    ("The checkpoint plays the file log's role.", "The stream's checkpoint and Kinesis' sequence numbers decide what is read. input_watermark records the newest event time per press in silver, which is what freshness and completeness use."),
    ("Outages are bounded.", "Kinesis keeps 7 days, so a stream down for less than that loses nothing; on restart it reads from its checkpoint."),
    ("Streams feed gold; they do not write it.", "At 15 minutes past each hour the stream job builds the hourly sensor aggregates for the closed hour (an input, in silver.integrated), re-checks the last 2 days for late readings, moves the per-press bookmarks, and calls the window-recompute job, which alone writes the production fact."),
    ("Silent machines, but not alarm storms.", "A per-press check (no reading for 30 minutes in a planned shift) catches one quiet press. While the whole stream is down, the per-press check is held back, and one stream alert fires instead of hundreds."),
]

# ------------------------------------------------------------------ failures
FAILURES = [
    ("Source down or slow", "Mover: DMS task state-change events and AppFlow failure events (EventBridge); a lag alarm that treats missing data as breaching", "AWS retries; the lander finds nothing new and ends as skipped; the source's bookmark stops moving", "Freshness goes red from the bookmark at the promised time; incident for the source owner"),
    ("DMS stops for hours, then resumes", "As above, and the bookmark", "DMS catches up from the source's change log (kept 72 hours); the lander loads the backlog over a few runs; gold hours stay incomplete until the bookmark passes them, then fill in as restatements", "Nothing, unless the outage outlasts the change log: then DMS reloads the table (full load, then change capture)"),
    ("A partner or puller file is unreadable or short", "Lander, file check", "The file is moved to landing/_rejected and file_log says why; the dataset's run ends FAILED as handled; other datasets carry on; master run PARTIAL", "The partner or source re-sends; the next run loads it"),
    ("A DMS change file is unreadable", "Lander, file check", "The dataset is BLOCKED at that file: no later change files are loaded, because skipping one would lose changes or apply them out of order. Other datasets carry on; the master run is PARTIAL; the 'dataset blocked' alert fires; its bookmark stops, so gold shows the hours as incomplete", "Repair the file, or have DMS reload the table (full load, then change capture); then the dataset unblocks"),
    ("A source changes its columns", "Lander and silver, contract check", "See 'When a source changes shape' below", "Update the contract; replay"),
    ("Bad rows", "Silver, quality rules", "Rows parked in quarantine with the reason; the rest carry on; stop only past the bad-share limit", "Steward reviews weekly; fixed rows are released and re-merged"),
    ("A full copy comes back short", "Lander, mass-delete guard", "Nothing is appended to bronze; the files are held and the dataset BLOCKED; 'mass delete stopped' alert", "Check the source; re-pull; then release or reject the held files"),
    ("A partner re-sends a corrected file", "Lander and silver", "Lands as a new file with a unique name; silver replaces the slice the contract names (dealer and month) with the newest file; gold rebuilds the affected windows, of any age, as restatements", "Nothing"),
    ("Job or cluster dies halfway", "Lakeflow task failure", "Retried up to 2 times (only passing errors reach Lakeflow); the batch's transaction id stops a second append", "Nothing, unless retries run out"),
    ("Aurora is slow or down", "Run recorder timeouts; job timeouts and duration health rules", "Jobs fail fast at their first task instead of hanging; stuck runs are finished by the sweeper", "Platform on-call, alerted by Databricks job alerts and the heartbeat alert, neither of which needs Aurora"),
    ("A bug in our code", "Any stage", "Fails; cause class 'our bug'; no retry", "Fix, release, then re-run the failed runs"),
]

RERUN = [
    ("Re-run failed", "Only the datasets that failed in a master run", "A queued run of the same lander job with run type rerun, linked to the failed master run. The file log means only what was not loaded is read. It writes new run rows; the earlier FAILED rows stay as history"),
    ("Replay from bronze", "Rebuild one silver table after a logic or contract fix", "A full refresh of that one table in its pipeline; bronze is the source of truth, so nothing is fetched from the source again. Bronze is kept 3 years in standard storage (then archived, still readable), and retention jobs never delete from it inside that time"),
    ("Backfill", "Rebuild past gold windows on purpose, for example after a correction", "A plan in Git (fact, windows, reason, cost). The window-recompute job, the only writer of that fact, works through it one chunk per run between normal updates. It never moves a run watermark or an input bookmark. Every rebuilt window is a restatement. Materialized views never read corrections, so they need no restating"),
    ("First load of a new dataset", "A new table, or a new source", "For DMS tables, DMS's own full load then change capture, loaded by the normal lander (the full-load rows sort before every change). For other sources, the bulk job in segments, writing to the same file log; the lander job then takes only files the bulk job did not, so there is no gap and no double load"),
    ("Re-extract", "Fetch from the source again", "Only for sources that can resend. Never for SAP, which moves its own delta token: replay from landing or bronze. For DMS: DMS reloads the table, and the normal lander loads it"),
]

SWEEPER = [
    ("Finds stuck runs.", "Every 15 minutes the ops builder lists runs still STARTED past their job's timeout."),
    ("Looks for evidence.", "If bronze holds rows with that run id, the commit happened: the run is closed as SUCCEEDED with counts from bronze, its files are marked loaded and its watermark stored. If not, it is closed as FAILED and its files go back to 'checked', so the next run loads them."),
    ("Says what it did.", "Every sweep is logged, so a run closed by the sweeper is visible as such."),
]

NEW_DATASET = [
    ("YAML, reviewed.", "The dataset's settings, contract, rules and owners in one pull request."),
    ("Source side, generated.", "For DMS: the DBA enables CDC on the table (a checklist item), and the generator adds the table to its DMS task group; only that group pauses. For AppFlow or the puller: a new flow or pull."),
    ("Tables first.", "The deploy creates the empty bronze table from the contract and registers the dataset, and creates the source's marker table if it is new, before any trigger refers to them."),
    ("First load.", "A DMS table is fully loaded by DMS itself, then change capture follows; the normal lander loads both, full-load rows first. Other sources use the bulk job in segments, recording files in the same file log; from the next run the lander job takes only the files the bulk job did not."),
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
    ("Every 15 min", "MES changes land and load; the manufacturing pipeline follows on the marker; gold windows recompute; the ops builder refreshes bookmarks and freshness and sweeps; the heartbeat passes through"),
    ("Hourly, at :15", "The stream job builds the closed hour's sensor aggregates and calls the window recompute"),
    ("Hourly", "The personal-data purge deletes landing files loaded more than 23 hours ago"),
    ("Every 30 min, 06:00-22:00", "SAP orders and deliveries: AppFlow runs, then its lander"),
    ("01:00", "Nightly SAP full copies for objects without deletes in their delta; the sales pipeline follows"),
    ("Overnight", "Dealer sell-out files arrive; each starts its lander once copied to landing"),
    ("03:00", "Housekeeping: retention, erasures, VACUUM, the daily DMS reconcile"),
    ("06:00", "The night shift ends (shifts: 06:00, 14:00, 22:00, plant time)"),
    ("06:15", "The 05:00-06:00 sensor hour closes; the window recompute writes the production fact and sets completeness for the night shift"),
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


# ------------------------------------------------------------------ the design test, rendered from etl_scenarios.py
PART_NAMES = [("mover", "Mover"), ("controller", "Run controller"), ("lander", "Lander"), ("silver", "Silver"), ("integrator", "Integrator"),
              ("gold", "Gold"), ("metric", "Metric layer"), ("recorder", "Run recorder"), ("ops", "Ops builder"), ("heartbeat", "Heartbeat")]
CLASS_NAMES = [("normal", "Normal day"), ("source_down", "Source down"), ("bad_file", "Bad file"), ("schema_change", "Schema change"),
               ("resend", "Re-sent data"), ("late_or_order", "Late or out of order"), ("delete", "Deletes"), ("crash", "Crash"),
               ("slow_dependency", "Slow dependency"), ("overlap", "Overlapping runs"), ("correction", "Corrections"),
               ("new_config", "New or changed config"), ("personal_data", "Personal data"), ("stream", "Streaming"), ("bad_value", "Bad values")]


def verdicts(sid):
    """List of verdicts for a scenario's checks, or None if no run is recorded."""
    if SR is None:
        return None
    return [SR.RESULTS.get(f"{sid}.{i}", {}).get("verdict") for i in range(1, len(next(x for x in SC.SCENARIOS if x["id"] == sid)["then"]) + 1)]


def scenario_table():
    rows = []
    for s in SC.SCENARIOS:
        v = verdicts(s["id"])
        if v is None or all(x is None for x in v):
            res = "added after the last run"
        else:
            st, gp, ct = v.count("STATED"), v.count("GAP"), v.count("CONTRADICTED")
            res = "Passes" if st == len(v) else f"{st} of {len(v)} stated" + (f", {gp} gap" + ("s" if gp != 1 else "") if gp else "") + (f", {ct} contradicted" if ct else "")
        rows.append((f"{s['id']} {s['title']}", s["given"], s["when"], str(len(s["then"])), res))
    return table(["Situation", "Given", "When", "Checks", "Result"], rows)


def coverage_grid(key, names):
    head = "".join(f"<th>{E(n)}</th>" for _, n in names)
    body = ""
    for s in SC.SCENARIOS:
        cells = "".join(f"<td style='text-align:center'>{'●' if k in s[key] else ''}</td>" for k, _ in names)
        body += f"<tr><td><b>{E(s['id'])}</b></td>{cells}</tr>"
    totals = "".join(f"<td style='text-align:center'><b>{sum(1 for s in SC.SCENARIOS if k in s[key])}</b></td>" for k, _ in names)
    body += f"<tr><td><b>Total</b></td>{totals}</tr>"
    return f'<div class="tw"><table class="t"><tr><th></th>{head}</tr>{body}</table></div>'


def history_table():
    if SR is None:
        return ""
    rows = [(f"Run {h['run']} ({h['date']})", f"{h['stated']} of 100", str(h['gap']), str(h['contradicted']), f"{h['passing']} of {len(SC.SCENARIOS)}",
             str(h['feasibility']), 'not checked' if h['contradictions_in_page'] is None else str(h['contradictions_in_page'])) for h in SR.HISTORY]
    return table(["Run", "Checks stated", "Gaps", "Contradicted", "Situations passing", "Would not work as written", "Page disagrees with itself"], rows)


def example_scenario():
    s = next(x for x in SC.SCENARIOS if x["id"] == "S05")
    lines = [f"{s['id']}  {s['title']}", f"GIVEN  {s['given']}", f"WHEN   {s['when']}", "THEN"] + [f"  {s['id']}.{i}  {t}" for i, t in enumerate(s["then"], 1)]
    return C.code("\n".join(lines), "One row of the test table. Each THEN line is checked against this page and marked stated, gap or contradicted.")



# ------------------------------------------------------------------ the settings registry, rendered from etl_settings.py
LEVELS = [("platform", "Platform (per environment)"), ("source", "Source"), ("dataset", "Dataset"), ("column", "Column"),
          ("gold_fact", "Gold fact"), ("domain", "Domain")]
STATUSES = [("exists", "Exists"), ("adapt", "Adapt"), ("new", "New"), ("retire", "Retire")]


def settings_summary():
    rows = []
    for lv, name in LEVELS:
        r = [x for x in ST.SETTINGS if x[1] == lv]
        rows.append((name,) + tuple(str(sum(1 for x in r if x[6] == st)) for st, _ in STATUSES) + (str(len(r)),))
    tot = ("Total",) + tuple(str(sum(1 for x in ST.SETTINGS if x[6] == st)) for st, _ in STATUSES) + (str(len(ST.SETTINGS)),)
    return table(["Level"] + [n for _, n in STATUSES] + ["Rows"], rows + [tot])


def settings_tables():
    out = ""
    for lv, name in LEVELS:
        r = [x for x in ST.SETTINGS if x[1] == lv]
        rows = [(k, typ, dft, rd, ", ".join(sc) or "-", st, note) for k, _, typ, dft, rd, sc, st, note in r]
        out += f"<details><summary><b>{E(name)}</b> ({len(r)} rows)</summary>" + table(["Setting", "Values", "Default", "Read by", "Tested in", "Status", "Note"], rows) + "</details>"
    return out


def settings_checks():
    unread = [x[0] for x in ST.SETTINGS if x[6] != "retire" and x[4] in ("", "-")]
    untested = [x[0] for x in ST.SETTINGS if x[6] != "retire" and not x[5]]
    a = "Every setting in use names the part that reads it." if not unread else "Settings with no reader: " + "; ".join(unread)
    b = f"{len(untested)} settings in use are not exercised by any test situation yet: " + "; ".join(untested) + "."
    return f"<p><b>Checks.</b> {E(a)} {E(b)}</p>"


# ------------------------------------------------------------------ page
FAQ = [
    ("Why not one big job from source to gold?", "Because sources arrive at different times. A job per source loads what has arrived; pipelines per domain run when a source has finished a batch. Nothing waits for the slowest source, and completeness tells everyone what has not arrived yet."),
    ("Why a batch-ready marker instead of triggering on bronze tables?", "Each dataset commits to bronze at a slightly different moment. A trigger on the tables fires on the first one and runs silver on a half-loaded source. The marker is written once, after the whole batch, so silver always sees a finished batch."),
    ("Why does a Declarative Pipeline need a wrapper job?", "The pipeline has its own event log and ids. The wrapper starts each update itself through the API, so it knows the update id, opens and closes our run row around it, copies counts and expectation results across, and then starts gold, so on-call sees one kind of run everywhere and gold never starts in the middle of an update."),
    ("Why not let Lakeflow retry every failure?", "Lakeflow retries whatever fails. A bad file retried is still a bad file, and a retry after the file was moved away looks like success. So the lander ends data problems itself, as handled failures in our log, and only passing errors (a network blip, a busy cluster) reach Lakeflow's retry."),
    ("What if the logging database is down or slow?", "Every call to it has a timeout, so jobs fail at their first task instead of hanging. Databricks' own job alerts, duration rules and the heartbeat alert do not need our database, so the problem is still seen."),
]


def page():
    src_table = table(["Kind of source", "Examples here", "Brought in by", "What changes arrive", "Lands as", "How often"], SOURCES)
    lmode_table = table(["Landing", "Lander reads it with", "Remembers what it read in"], LANDER_MODES)
    notv1_table = table(["Not in v1", "Why"], NOT_V1)
    mstat_table = table(["Mover", "Set up how", "Status"], MOVER_STATUS)
    stages_table = table(["Stage", "What it does", "Set by", "Status"], STAGES)
    colset_table = table(["Setting", "Values", "Default", "Stage"], COLUMN_SETTINGS)
    castfail_table = table(["on_cast_failure", "What happens", "Use for"], CAST_FAILURE)
    schema_table = table(["Source change", "Bronze", "Silver", "Alert"], SCHEMA_CHANGES)
    scd_table = table(["Kind of data", "Examples", "History", "Why"], HISTORY_KINDS)
    tdec_table = table(["#", "Decision", "Status"], TRANSFORM_DECISIONS)
    parts_table = table(["Part", "Does", "Reads", "Writes", "Runs as", "Safe to run twice because"], PARTS)
    cols_table = table(["Layer", "Columns added to every row", "So you can tell"], INGEST_COLS)
    order_table = table(["Kind of input", "Order of changes", "Deletes"], ORDERING)
    trig_table = table(["Trigger", "Used for", "Starts"], TRIGGERS)
    jobs_table = table(["Job", "How many", "Inside", "Started by"], JOBS)
    ids_table = table(["Id", "Made by", "Means", "Found in"], IDS)
    levels_table = table(["Log table", "One row per", "Holds"], LOG_LEVELS)
    alert_table = table(["Alert", "Fires when", "Severity", "Goes to"], ALERTS)
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
<li><a href="#rules">Seven rules</a></li><li><a href="#sources">Sources and ingestion tech</a></li><li><a href="#transforms">The standard transforms</a></li><li><a href="#settings">The settings</a></li><li><a href="#map">The runtime map</a></li><li><a href="#parts">The ten working parts</a></li>
<li><a href="#order">Order, deletes, corrections, schema and personal data</a></li><li><a href="#complete">Completeness and freshness</a></li><li><a href="#run">One run, step by step</a></li>
<li><a href="#jobs">Jobs and triggers</a></li><li><a href="#logs">Ids and log rows</a></li><li><a href="#stream">Streaming</a></li><li><a href="#fail">When something breaks</a></li>
<li><a href="#rerun">Re-runs, backfills and first loads</a></li><li><a href="#obs">Observability: the working parts</a></li><li><a href="#day">A day in the life</a></li><li><a href="#tested">How this design is tested</a></li><li><a href="#faq">Questions</a></li></ol></nav>

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

<section id="transforms"><p class="eyebrow">The standard transforms</p><h2>Bronze to silver: thirteen generic stages, set per column</h2>
<p>All of this happens between bronze and silver: bronze only ever appends what arrived, and silver is where columns are chosen, typed, cleaned, flattened and given history. Bronze keeps what the source sent; silver holds one clean, typed row per real thing, in the shape we chose. Between them sits one fixed list of generic transforms. Nothing in this step knows it is handling tyres: the same code runs for every table, and the metadata says which columns, which types, which formats and which history.</p>
{rules(TRANSFORM_PRINCIPLES)}
<h3>The thirteen stages, in order</h3>
<p>The status column is where each stands in the framework today.</p>
{stages_table}
<h3>Example: 100 columns in bronze, 30 in silver</h3>
<p>A plant's MES table arrives with 100 columns. The dataset lists the 30 it needs; those 30 go on to silver, renamed and typed as listed; the other 70 stay in bronze. If the source adds a 101st column next month, bronze keeps it and silver does not change. If someone later needs one of the 70, they list it and replay from bronze.</p>
<h3>The column settings</h3>
<p>Set per column in the dataset's YAML (or per dataset where marked), loaded into the framework's column table. The last column says which stage reads it.</p>
{colset_table}
<h3>JSON payloads: flattening happens here, not on the way in</h3>
{rules(JSON_RULES)}
{C.code(JSON_EXAMPLE, "A dealer API order: two silver tables from one bronze payload, only the listed paths extracted.")}
<h3>When a value will not convert</h3>
{castfail_table}
<h3>When the source changes shape</h3>
<p>The rule behind all of these: silver's shape is defined by our column list, not by the source, so most source changes either do not reach silver or are fixed in the metadata without silver changing.</p>
{schema_table}
<p>Each column is required or optional, and each contract version is minor (additive) or major (breaking), so consumers can tell which changes affect them.</p>
<h3>History: SCD type 1 or type 2</h3>
<p>Both, chosen per dataset. SCD type 1 overwrites a row when it changes (only the current version exists); SCD type 2 keeps every version with its valid-from and valid-to. The kind of data sets the default.</p>
{scd_table}
{rules(HISTORY_RULES)}
<h3>Decisions</h3>
{tdec_table}
</section>

<section id="settings"><p class="eyebrow">The settings</p><h2>Every setting the runtime reads, and where it comes from</h2>
<p>The runtime is driven by metadata, so its settings are its real interface. This is the complete list for AWS and Databricks, at six levels: platform (one set per environment), source, dataset, column, gold fact and domain. Each setting names the part that reads it and the test situations that exercise it, and is compared with the framework's registry today: <b>exists</b> (used as is), <b>adapt</b> (exists but Azure-shaped or with a new meaning), <b>new</b>, or <b>retire</b> (Azure Data Factory only). A setting is written once at the level where it belongs, and lower levels may override it (platform, then source, then dataset, then column).</p>
{settings_summary()}
{settings_tables()}
{settings_checks()}
<p class="note">Source: <code>_guides/etl_settings.py</code>. Several rows group related keys (for example the six profiling settings). The framework's registry (<code>docs/metadata_keys.md</code>) will be updated from this list when building starts.</p>
</section>

<section id="map"><p class="eyebrow">The runtime map</p><h2>Ten parts, three bands</h2>
<p>Read the middle row left to right: data moves from source systems to metrics. The band above decides when things run; the band below records everything that ran. Nothing in the middle row starts itself, and nothing runs without being recorded.</p>
<figure class="diagram">{runtime_map()}<figcaption>The middle row moves and shapes data; the top band starts it; the bottom band records it.</figcaption></figure></section>

<section id="parts"><p class="eyebrow">The working parts</p><h2>What each part does, reads and writes</h2>
<p>Each part has one job and a fixed contract. The last column is the most important: it is what lets the platform retry without a person checking.</p>
{parts_table}
<h3>Every row says where it came from</h3>
{cols_table}</section>

<section id="order"><p class="eyebrow">Order, deletes and corrections</p><h2>Changes in the right order, deletes never missed, shape changes caught</h2>
<p>Silver keeps one row per real thing, with its history. That is only right if changes are applied in the order they happened, deletes are seen, and a fix to old data is told apart from a new change.</p>
{order_table}
{rules(GUARDS)}
<h3>When a source changes shape</h3>
{rules(SCHEMA_DRIFT)}
<h3>What the lander does to personal data</h3>
<p>The full privacy design is on <a href="{AWS}#security">the platform page</a>; these are the steps that happen in the lander.</p>
{rules(PERSONAL)}</section>

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
{fail_table}
<h3>The alerts this runtime raises</h3>
<p>Every alert has an owner from the metadata and goes to one incident per cause; the dashboard and paging rules are on <a href="{AWS}#ops">the platform page</a>.</p>
{alert_table}</section>

<section id="rerun"><p class="eyebrow">Re-runs, backfills and first loads</p><h2>Five ways to run again, none in the way of the normal runs</h2>
{rerun_table}
<h3>Adding a dataset to a running source</h3>
{rules(NEW_DATASET)}
<h3>Changing settings</h3>
{rules(SETTINGS)}</section>

<section id="obs"><p class="eyebrow">Observability: the working parts</p><h2>What has to exist for anyone to see what ran</h2>
<p>The dashboard, alerts and incidents are described on <a href="{AWS}#ops">the platform page</a>. These are the parts underneath, and where each stands today. Two of them (job health rules and the heartbeat alert) deliberately do not depend on our own log database, so they still work when it does not.</p>
{obs_table}
{C.code(HEALTH_COLS, "The health view on-call opens first: one row per dataset, judged by its bookmark, not by its last run.")}</section>

<section id="day"><p class="eyebrow">A day in the life</p><h2>Twenty-four hours of the runtime</h2>
<p>What runs when on an ordinary day, for the plants' morning meeting at 06:30.</p>
{day_table}</section>

<section id="tested"><p class="eyebrow">How this design is tested</p><h2>Twenty-two situations, each with checks it must pass</h2>
<p>The design is tested on paper before anything is built. Each situation is a row in a table (<code>_guides/etl_scenarios.py</code>): what is true before, what happens, and a list of checks written as facts the platform must produce: which tables change, which log rows appear, whether a bookmark moves, which alert fires. A reviewer who did not write the page marks every check as <b>stated</b> (the page says it, with a quote), <b>gap</b> (the page is silent) or <b>contradicted</b>. A situation passes only when every check is stated. The same rows become DataTwin faults and then integration tests on Databricks, so the test is written once.</p>
{example_scenario()}
<h3>The situations and their latest result</h3>
{scenario_table()}
<h3>What each situation touches</h3>
<p>A dot means the situation exercises that part. A column with few dots is a part the test barely covers.</p>
{coverage_grid("parts", PART_NAMES)}
<h3>Which kinds of trouble each situation covers</h3>
{coverage_grid("classes", CLASS_NAMES)}
<h3>Run by run</h3>
<p>Each run checks the same rows against the page as it stood. Between runs the design was fixed, not the wording polished: a check that failed because a mechanism would not work changed the mechanism. Where a fix deliberately changed the expected behaviour, the row was updated and the change recorded.</p>
{history_table()}
<p class="note">Before the table existed, a free-form walk-through of twelve situations found 3 failures and 9 with gaps, the biggest being that gold could call an hour complete while an input was missing. That led to the rewrite this table now checks.</p>
</section>

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
