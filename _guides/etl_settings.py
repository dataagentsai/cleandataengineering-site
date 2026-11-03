"""The settings registry for the core ETL on AWS + Databricks.

Every setting the runtime design reads, one row each:
    (key, level, type and values, default, read by, scenarios, status, note)

level:   platform | source | dataset | column | gold_fact | domain
read by: the working part(s) on the ETL page (mover, controller, lander, silver, integrator, gold,
         recorder, ops, heartbeat, deploy). A setting no part reads is not allowed.
status against today's framework registry (data-platform-framework docs/metadata_keys.md):
    exists  - registered today and used as is
    adapt   - registered today, but Azure-shaped or with a changed meaning here
    new     - not registered yet
    retire  - registered today, Azure Data Factory only; not used on AWS + Databricks
scenarios: ids in etl_scenarios.py that exercise the setting (empty = not tested yet).
"""

SETTINGS = [
    # ---------------------------------------------------------------- platform (one set per environment)
    ("runtime_environment", "platform", "dev, preprod, prod", "prod", "recorder, deploy", ["S29"], "adapt", "'staging' becomes 'preprod'"),
    ("realm", "platform", "aws-databricks, adf-adls", "aws-databricks", "deploy", ["S29"], "adapt", "was default_realm; chooses which generators the deploy runs"),
    ("aws_region", "platform", "AWS region code", "ap-south-1", "deploy, mover", ["S29"], "new", ""),
    ("catalog_prefix", "platform", "text", "the environment name plus _", "lander, silver, gold, deploy", ["S23"], "new", "dev_, preprod_, prod_ in front of bronze, silver, gold, ops"),
    ("landing_bucket", "platform", "S3 bucket", "landing-<env>", "mover, lander", ["S01"], "new", "replaces target_storage_account"),
    ("landing_pii_bucket", "platform", "S3 bucket", "landing-pii-<env>", "mover, lander", ["S21"], "new", ""),
    ("secrets_backend", "platform", "aws_secrets_manager", "aws_secrets_manager", "mover, lander", ["S29"], "new", "replaces key_vault_uri"),
    ("secret_prefix", "platform", "text", "dp/<env>/", "mover, lander", ["S29"], "new", ""),
    ("metadata_db_endpoint", "platform", "Aurora endpoint and database", "none", "recorder, controller", ["S13"], "adapt", "was metadata_db_server (Azure SQL)"),
    ("recorder_timeout_seconds", "platform", "integer", "10", "recorder", ["S13"], "new", ""),
    ("recorder_retries", "platform", "integer", "2", "recorder", ["S13"], "new", ""),
    ("job_timeout_minutes", "platform", "integer", "30", "controller", ["S13", "S14"], "new", "every generated job; the sweeper uses it too"),
    ("metadata_schema_version", "platform", "integer", "none", "recorder, deploy", ["S29"], "exists", ""),
    ("default_file_format", "platform", "DELTA", "DELTA", "lander", ["S29"], "exists", ""),
    ("default_concurrency", "platform", "integer 1-50", "8", "controller", ["S01", "S05"], "adapt", "was default_batch_count (ADF ForEach); now the for-each concurrency"),
    ("redaction_extra_patterns", "platform", "list of patterns", "none", "recorder", ["S21"], "exists", ""),
    ("large_table_row_threshold, huge_table_row_threshold", "platform", "integers", "10 million, 1 billion", "controller", ["S30"], "exists", "decides segmenting in the bulk job"),
    ("auto_retry_on_partial, auto_retry_max_attempts, auto_retry_delay_minutes", "platform", "true or false; integers", "false, 2, 30", "controller", ["S20"], "exists", ""),
    ("tier_targets", "platform", "freshness and paging per tier", "tier 1: page any hour; tier 2: plant hours; tier 3: working hours", "ops", ["S03", "S11"], "new", ""),
    ("mass_delete_limit_pct", "platform", "percent", "5", "lander", ["S08"], "new", "datasets may override"),
    ("held_file_days", "platform", "integer", "7", "lander, ops", ["S17"], "new", ""),
    ("pii_landing_hours", "platform", "integer", "23", "ops", ["S21"], "new", "the hourly purge"),
    ("stream_late_allowance_minutes", "platform", "integer", "120", "gold", ["S10"], "new", ""),
    ("ops_interval_minutes", "platform", "integer", "15", "ops", ["S01", "S14"], "new", ""),
    ("heartbeat_interval_minutes", "platform", "integer", "15", "heartbeat, ops", ["S22"], "new", ""),
    ("key_vault_uri, target_storage_account, target_container_default, shir_name, staging_linked_service", "platform", "-", "-", "-", [], "retire", "Azure only"),
    ("flatten_function_url, flatten_function_secret_name, flatten_databricks_*", "platform", "-", "-", "-", [], "retire", "flattening moved into silver (stage 2)"),
    ("lifecycle_cool_days, lifecycle_archive_days", "platform", "-", "-", "-", [], "retire", "storage tiers set by Terraform and S3 lifecycle rules"),

    # ---------------------------------------------------------------- source
    ("source_type", "source", "sql_server, oracle, postgres, mysql, sap, saas, rest_api, partner_files, stream, upload", "none", "controller, mover", ["S01", "S02"], "adapt", "typed on source_master; adds sap, partner_files, stream, upload"),
    ("mover", "source", "dms, appflow, transfer_family, kinesis, puller, upload", "none", "mover, controller, deploy", ["S01", "S02", "S06", "S10"], "new", ""),
    ("clock", "source", "schedule, appflow_finished, upload_copied, continuous", "set by the mover", "controller", ["S01", "S02", "S04"], "new", "one clock per source"),
    ("schedule_cron, schedule_timezone", "source", "cron; time zone", "every 15 minutes; UTC", "controller", ["S01", "S04"], "adapt", "moves from dataset to source: the lander job is per source"),
    ("auth_method, connection_secret_name", "source", "as today; the secret is a Secrets Manager name", "none", "mover", ["S30"], "adapt", "kv:// references become Secrets Manager names"),
    ("connect_timeout_seconds, rate_limit_rps", "source", "integers", "30; none", "mover", ["S30"], "exists", "puller and REST"),
    ("max_concurrent_datasets", "source", "integer 1-50", "default_concurrency", "controller", ["S05"], "exists", "the for-each concurrency for this source"),
    ("server, database, service_name, base_url and other connection keys", "source", "per source type, as today", "none", "mover", ["S30"], "exists", "used by the puller"),
    ("integration_runtime", "source", "-", "-", "-", [], "retire", "ADF only"),
    ("dms_task_group", "source", "text", "one group per source", "mover, deploy", ["S18"], "new", "adding a table pauses only its group"),
    ("dms_min_log_retention_hours", "source", "integer", "72", "doctor", ["S03"], "new", "checked by the healthcheck, not enforced by us"),
    ("dms_latency_limit_seconds", "source", "integer", "300", "lander, ops", ["S03", "S22"], "new", "the quiet rule: bookmark is now minus latency while below this"),
    ("appflow_connector_profile, appflow_flow_prefix", "source", "names", "none", "mover, deploy", ["S02"], "new", ""),
    ("partner_login, partner_folder", "source", "names", "none", "mover, deploy", ["S06", "S07"], "new", ""),
    ("control_file", "source", "none, row_count_file", "none", "lander", ["S06"], "new", ""),
    ("kinesis_stream, kinesis_retention_days", "source", "name; integer", "none; 7", "lander, deploy", ["S10"], "new", ""),
    ("has_personal_data", "source", "true, false", "false", "mover, lander", ["S17", "S21"], "new", "routes landing to the personal-data bucket"),
    ("owner, deputy", "source", "people from the identity provider", "none", "ops", ["S16", "S25"], "new", "checked nightly against the identity provider"),
    ("contract_ref, contract_version", "source", "path in Git; semver", "none", "silver", ["S16", "S25"], "new", ""),
    ("source_timezone", "source", "IANA zone", "UTC", "silver", ["S24"], "new", "columns may override"),

    # ---------------------------------------------------------------- dataset
    ("dataset_type, load_type, schema_name, object_name, custom_query", "dataset", "as today", "none", "mover, lander", ["S01", "S08"], "exists", ""),
    ("dataset_kind", "dataset", "master, transaction, event, snapshot", "required", "silver", ["S27"], "new", "sets the default history"),
    ("domain", "dataset", "manufacturing, quality, sales, aftermarket", "required", "controller, silver", ["S01"], "new", "which domain pipeline builds it"),
    ("tier", "dataset", "1, 2, 3", "3", "ops", ["S03", "S11"], "new", ""),
    ("freshness_target", "dataset", "minutes behind, or a time of day", "from the tier", "ops", ["S03", "S22"], "adapt", "was sla_freshness_hours"),
    ("expected_delivery", "dataset", "a time and days", "none", "ops", ["S22"], "new", "partner files: freshness judged against it"),
    ("volume_band", "dataset", "auto, or fixed low and high", "auto (from the last 8 same weekdays)", "ops", ["S33"], "new", ""),
    ("owner, deputy, steward", "dataset", "people", "the source's", "ops", ["S05"], "new", ""),
    ("max_files_per_run, max_gb_per_run", "dataset", "integers", "500; 20", "lander", ["S18"], "new", "spreads big first loads over runs"),
    ("watermark_column, watermark_initial_value", "dataset", "as today", "none", "mover", ["S30"], "exists", "puller, append-only tables only"),
    ("change_order", "dataset", "dms, sap_counter, arrival, snapshot, event_time", "set by the mover", "silver", ["S01", "S02"], "new", "the sequence AUTO CDC uses"),
    ("delete_rule", "dataset", "dms_op, sap_change_mode, snapshot_compare, replace_slice, none", "set by the mover", "silver", ["S02", "S09"], "new", ""),
    ("replacement_scope", "dataset", "list of columns", "none", "silver", ["S07"], "new", "partner files: what a re-sent file replaces"),
    ("mass_delete_limit_pct", "dataset", "percent", "the platform's", "lander", ["S08"], "new", "override"),
    ("silver.columns", "dataset", "all_except_excluded, declared", "all_except_excluded", "silver", ["S23"], "new", "all by default; declared = projection to listed columns"),
    ("row_filter", "dataset", "a declared condition", "none", "silver", ["S32"], "new", ""),
    ("quarantine_max_pct", "dataset", "percent", "2", "silver", ["S32"], "new", "stop the table past this share of bad rows"),
    ("dedup.mode, dedup.business_keys, dedup.order_by", "dataset", "as today", "none", "silver", ["S27"], "exists", ""),
    ("history", "dataset", "append, scd1, scd2, snapshot", "from dataset_kind", "silver", ["S27"], "new", ""),
    ("history_track_columns", "dataset", "list of columns", "all listed columns", "silver", ["S27"], "new", ""),
    ("explode_path, parent_keys", "dataset", "a path; key paths", "none", "silver", ["S28"], "new", "child datasets from JSON arrays"),
    ("profile.enabled, profile.when, profile.scope, profile.sample_pct, profile.columns, profile.suggest_rules", "dataset", "see the platform page", "off, daily, new_rows, 10, all, true", "silver, ops", ["S34"], "new", ""),
    ("file_format, file_pattern, file_encoding, csv_*, excel_*, xml_record_xpath", "dataset", "as today", "as today", "lander", ["S06", "S24"], "adapt", "read by the lander instead of ADF"),
    ("load_profile, segmentation_*, segment_count", "dataset", "as today", "auto", "controller", ["S18"], "exists", "the bulk job"),
    ("budget_daily_usd", "dataset", "number", "none", "ops", ["S33"], "new", "judged against the estimated cost split per dataset"),
    ("realm", "dataset", "aws-databricks", "the platform's", "deploy", ["S29"], "adapt", "new realm name"),
    ("target_container, target_path_template", "dataset", "-", "-", "-", [], "retire", "the landing layout is fixed by the landing contract"),
    ("intended_dius, parallel_copies, enable_staging, sink_max_concurrent_connections, partition_*", "dataset", "-", "-", "-", [], "retire", "ADF copy settings"),
    ("flattening_mode, flattening_engine, flattening_path_separator, primary_array_path, array_max_explode_rows", "dataset", "-", "-", "-", [], "retire", "replaced by source_path, explode_path and array_strategy in silver"),
    ("lifecycle_cool_days, lifecycle_archive_days, lifecycle_delete_days", "dataset", "-", "-", "-", [], "retire", "retention set per layer by the platform"),

    # ---------------------------------------------------------------- column
    ("column_name, data_type, is_nullable, ordinal_position", "column", "as today", "from discovery", "silver", ["S23"], "exists", ""),
    ("is_primary_key", "column", "true, false", "false", "silver", ["S27"], "exists", ""),
    ("is_excluded", "column", "true, false", "false", "silver", ["S35"], "exists", "used with the default silver.columns = all_except_excluded"),
    ("required", "column", "true, false", "true for keys", "silver", ["S25"], "new", ""),
    ("silver_column_name", "column", "a name", "the source name", "silver", ["S23", "S25"], "exists", ""),
    ("source_path", "column", "a JSON path", "none", "silver", ["S28"], "exists", ""),
    ("array_strategy", "column", "keep, join_as_text, take_first", "keep", "silver", ["S35"], "adapt", "explode moves to explode_path"),
    ("silver_data_type", "column", "a Spark SQL type", "the bronze type", "silver", ["S24", "S26"], "exists", ""),
    ("date_format, timestamp_format", "column", "patterns", "ISO 8601", "silver", ["S24"], "new", ""),
    ("decimal_separator", "column", "point, comma", "point", "silver", ["S24"], "new", ""),
    ("on_cast_failure", "column", "quarantine, null_and_count, stop", "quarantine", "silver", ["S24"], "new", "replaces cast_safety"),
    ("cast_safety", "column", "-", "-", "-", [], "retire", "replaced by on_cast_failure"),
    ("source_timezone", "column", "IANA zone", "the source's", "silver", ["S24"], "new", ""),
    ("local_time_zone_from", "column", "a column naming the plant", "none", "silver", ["S31"], "new", ""),
    ("column_role", "column", "code, identifier, measure, text", "none", "silver", ["S31"], "exists", ""),
    ("transforms, skip_groups, skip_processors", "column", "lists", "none", "silver", ["S31"], "exists", ""),
    ("unit_from, unit_to", "column", "units", "none", "silver", ["S31"], "new", ""),
    ("code_map", "column", "a mapping table", "none", "silver", ["S31"], "new", ""),
    ("key_map", "column", "a mapping table", "none", "silver", ["S31"], "new", "conformed keys; unmapped becomes unknown"),
    ("null_replacement", "column", "a value", "none", "silver", ["S31"], "exists", ""),
    ("pii_class", "column", "none, name, email, phone, free_text and others", "none", "lander", ["S21"], "exists", ""),
    ("pii_purpose, pii_retention_days", "column", "text; integer", "required when pii_class is set", "lander, ops", ["S21"], "new", ""),

    # ---------------------------------------------------------------- gold fact (built by the window-recompute job)
    ("fact_name, grain", "gold_fact", "name; for example press-hour", "required", "gold", ["S01"], "new", ""),
    ("window, lookback", "gold_fact", "hour or day; a duration", "hour; 2 days", "gold", ["S03", "S10"], "new", ""),
    ("inputs", "gold_fact", "datasets with a role: driver, dimension as of, contributor", "required", "gold", ["S01", "S05"], "new", ""),
    ("completeness", "gold_fact", "on, off", "on", "gold", ["S03", "S05", "S11"], "new", ""),
    ("max_unknown_pct", "gold_fact", "percent", "1", "gold", ["S09"], "new", ""),
    ("partition_column", "gold_fact", "a date column", "the window's date", "gold", ["S12"], "new", ""),
    ("backfill_chunk_windows", "gold_fact", "integer", "24", "gold", ["S12"], "new", ""),
    ("reads_corrections", "gold_fact", "true, false", "false", "gold", ["S12"], "new", ""),

    # ---------------------------------------------------------------- domain (one Declarative Pipeline and wrapper each)
    ("domain_name", "domain", "name", "required", "controller, deploy", ["S01"], "new", ""),
    ("sources", "domain", "list of sources", "from its datasets", "controller", ["S01"], "new", "the marker tables its wrapper watches"),
    ("min_gap_minutes", "domain", "integer", "15", "controller", ["S36"], "new", ""),
    ("gold_facts", "domain", "list of facts", "none", "controller", ["S01"], "new", "recompute jobs the wrapper calls"),
]
