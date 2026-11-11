SERVICE = {
    "slug": "glue-data-quality",
    "name": "AWS Glue Data Quality",
    "short": "Glue Data Quality",
    "group": "catalog",
    "one_line": "Serverless data quality rules, written in DQDL, run against Glue Data Catalog tables or inside Glue ETL jobs, with anomaly detection.",
    "status": "Generally available. Recent additions: results written to Iceberg tables in the Data Catalog (Jul 2026) and Bedrock-based ADVANCED rule recommendations (Sep 2026).",
    "checked": "2026-11-11",
    "site_verdict": ("Drop", "Only if a team already uses it on Glue jobs. It runs outside Databricks, so its results would not join our run id "
                     "without extra work; on this platform rules live in metadata and run as Lakeflow expectations and DQX at every hop."),
    "equivalents": {"azure": "Microsoft Purview data quality", "gcp": "Dataplex data quality scans",
                    "databricks": "Lakeflow pipeline expectations, DQX, and data profiling (Lakehouse Monitoring)",
                    "open_source": "Great Expectations, Soda Core or Deequ"},
    "plain": [
        "Data quality means how fit a data set is for the job people use it for. A data quality rule is a check written down "
        "in advance, such as every order has a customer, or scrap quantity is never negative. AWS Glue Data Quality is a "
        "managed service that runs such rules for you, without servers to look after. You write rules in a small language "
        "called DQDL, the Data Quality Definition Language, and Glue runs them on Spark using Deequ, an open-source library "
        "from Amazon that computes the statistics behind the checks.",
        "Take a retail chain loading daily sales from its point-of-sale system into an S3 data lake. A ruleset for the sales "
        "table might say: the row count is above 90 percent of the average of the last ten days, store id is never empty, "
        "the amount is between zero and one hundred thousand, and every product id exists in the product table. Glue runs the "
        "ruleset after each load and returns a score, which is the share of rules that passed, plus the outcome of each rule.",
        "There are two ways in. The first is from the Glue Data Catalog: a data steward picks a catalogued table, asks Glue to "
        "recommend rules from a sample, edits them and schedules the check. This is quality at rest. The second is inside a "
        "Glue ETL job: the rules sit in the pipeline, and bad rows can be identified and sent aside before they land. This "
        "is quality in transit, and it is the only path that tells you exactly which records failed.",
        "On top of fixed rules, Glue Data Quality can learn what normal looks like. Analyzers gather statistics such as row "
        "counts or distinct values over time, and anomaly detection flags a value that breaks the pattern, even when no rule "
        "was written for it. These flags are called observations, meaning unconfirmed insights for a person to review.",
    ],
    "analogy": "A checklist inspector at the warehouse door who ticks boxes on every delivery and also notices when today's lorry is half the usual size.",
    "big_picture": [
        "Quality checks belong at every hop of the medallion layout, and the contract is enforced at the bronze-to-silver "
        "step, where rows that break it go to quarantine with a reason. Glue Data Quality can do that job on an AWS-native "
        "platform where Glue ETL jobs move data and the Glue Data Catalog holds the tables. It reads from S3, Redshift, JDBC "
        "sources and open table formats such as Iceberg, Delta and Hudi, and it can also check S3 Tables and Lake Formation "
        "managed Iceberg tables.",
        "This site's reference platform does the processing in Databricks. Rules are declared per table in the metadata store, "
        "run at every hop as Lakeflow pipeline expectations or DQX checks, park bad rows in quarantine tables, and write every "
        "outcome to one result table that carries the run id. That run id is how a number on a dashboard is traced back to "
        "the run, its lineage, its cost and its quality results.",
        "Glue Data Quality would run on separate Glue compute, against tables that Unity Catalog does not see through the same "
        "lens, and its results would land in CloudWatch, EventBridge, S3 or Glue's own result store with no link to our run "
        "id. You could build that link, but you would be maintaining a second rules language and a second results store for "
        "nothing Databricks lacks. So the site's verdict is Drop, unless a team already relies on it inside existing Glue jobs; "
        "then keep it there and feed its results into the shared quality table.",
    ],
    "upstream": ["svc:glue-data-catalog", "svc:glue-etl", "svc:s3"],
    "downstream": ["svc:cloudwatch", "svc:eventbridge", "Data quality results in S3 or Iceberg tables"],
    "concepts": [
        ("DQDL", "Data Quality Definition Language: a short declarative language for rules, such as IsComplete \"store_id\" or RowCount > 1000."),
        ("Rule", "One DQDL expression that checks one property of the data and returns pass or fail."),
        ("Ruleset", "A named set of rules attached to one Data Catalog table, stored as a Glue resource with its own identifier."),
        ("Data quality score", "The percentage of rules in a ruleset that passed in one evaluation run."),
        ("Analyzer", "A DQDL expression that only gathers statistics, such as distinct value counts, so trends can be learned without a pass or fail."),
        ("Dynamic rule", "A rule whose threshold comes from history, for example a row count above 90 percent of the average of the last ten runs."),
        ("Anomaly detection", "Machine learning over gathered statistics that flags unusual values as observations for a person to review."),
        ("Recommendation run", "Glue reads a sample of a catalogued table and proposes a starting ruleset; ADVANCED mode uses Amazon Bedrock."),
        ("Row-level results", "In ETL jobs, a per-record outcome column so failing rows can be filtered out or written to quarantine."),
    ],
    "use_when": [
        "Your pipelines are Glue ETL jobs and you want checks inside them without adding another library.",
        "Data stewards need to check tables already in the Glue Data Catalog without writing Spark code.",
        "You want rule recommendations as a starting point on many unfamiliar AWS tables.",
        "You run an AWS-only lakehouse on S3 Tables or Lake Formation managed Iceberg and want quality checks native to it.",
        "You want quality outcomes as EventBridge events to start alerts or downstream steps in Step Functions.",
    ],
    "avoid_when": [
        "Databricks runs your pipelines; Lakeflow expectations and DQX run in the same job and write results next to the run id.",
        "You need one rules language across Azure, Google Cloud and AWS; an open-source tool such as Great Expectations or Soda travels better.",
        "Your data is nested or holds lists; rules cannot evaluate nested or list-type sources until you flatten them.",
        "You need failing records identified when checking catalogued tables at rest; only the ETL entry point gives row-level results.",
        "You would be adding a second results store that nobody joins to lineage, cost and run history.",
    ],
    "challenges": [
        ("Results that do not join",
         "Scores land in Glue, CloudWatch or S3 with Glue run identifiers, and nobody can tie a failed rule to the pipeline run that produced the data.",
         "Pass your own run id into the job and write it with each result, or write results to Iceberg tables in the Data Catalog and join them there."),
        ("Recommendations taken as truth",
         "Recommended rules describe the sample as it was, including its mistakes, and fail the next day on normal variation.",
         "Treat recommendations as a draft; a steward reviews each rule, and fixed thresholds are replaced with dynamic rules where volume moves."),
        ("Alert fatigue from anomalies",
         "Anomaly detection flags every seasonal swing, such as Monday order spikes, and the team stops reading the observations.",
         "Let analyzers gather enough history first, exclude known seasonal patterns, and route only confirmed rules to paging."),
        ("Catalog runs scan too much",
         "A ruleset scheduled on a large table re-reads the whole table each time and the DPU bill grows with the table.",
         "Use pushdown predicates on catalog runs, or job bookmarks in ETL, to check only new partitions."),
        ("Rules split across places",
         "Some rules live in Glue rulesets, some in job code, some in another tool, and nobody knows which rule guards which table.",
         "Keep DQDL in version control, deploy rulesets with CloudFormation or Terraform, and generate them from one metadata source."),
        ("Ruleset size",
         "Generated rulesets for wide tables hit the limits of 2,000 rules or 65 KB per ruleset.",
         "Split by purpose, such as completeness, ranges and integrity, and use DQDL constants to keep long expressions short."),
        ("Format gaps",
         "Some Lake Formation managed tables and protected multi-dialect views have limitations, and nested columns are not checked.",
         "Check the supported source list for your table type, and flatten nested structures before the check."),
    ],
    "compare": [
        ("Lakeflow pipeline expectations (Databricks)",
         "Tables are built by Lakeflow Declarative Pipelines; rules sit in the pipeline and can warn, drop or stop, with results in the event log.",
         "You need checks across two tables, such as reconciliations; use DQX or plain SQL for those."),
        ("DQX (Databricks Labs)",
         "You run Spark jobs on Databricks and want rules from metadata, row-level quarantine and results in a Delta table.",
         "You want a fully supported product rather than a Labs library."),
        ("Databricks data profiling (Lakehouse Monitoring)",
         "You want managed profiles and drift over time on important gold tables with its own dashboard.",
         "You need hard pass or fail rules at load time; profiling observes, it does not block."),
        ("Great Expectations or Soda",
         "You need one rules language across several clouds and engines and are fine running it yourself.",
         "You want no library to maintain on an AWS-only Glue platform."),
        ("Microsoft Purview data quality (Azure)",
         "Your estate is on Azure and Fabric and quality sits with the Purview catalog.",
         "Your platform is on AWS."),
        ("Dataplex data quality scans (Google Cloud)",
         "Your tables are in BigQuery and you want Google-native scans.",
         "You run on AWS."),
    ],
    "cost": {
        "model": ("Billed as Glue compute in DPU-hours, where a DPU (data processing unit) is a slice of compute and memory. "
                  "Catalog evaluation and recommendation runs are charged for the DPUs they use for as long as they run. In ETL "
                  "jobs, the checks add run time to the job you already pay for. Anomaly detection adds compute for gathering "
                  "statistics and training. Storing statistics is free; results written to S3 or Iceberg tables pay normal "
                  "storage. ADVANCED recommendations also pay Amazon Bedrock for the model calls. List prices, check your region."),
        "drivers": [
            "How much data each run scans, which depends on table size and whether you check only new partitions.",
            "How often rulesets are scheduled.",
            "How many DPUs each catalog run is given.",
            "Whether anomaly detection and analyzers are on for many columns.",
            "Bedrock calls for ADVANCED recommendations.",
        ],
        "traps": [
            "Full-table catalog runs every hour on a table that grows daily make the bill grow with the table.",
            "Each Glue run has a minimum billed duration, so many tiny runs cost more than one batched run.",
            "Running the same checks in Glue and again in Databricks pays twice for one answer.",
            "Leaving recommendation runs scheduled after the rules are agreed wastes compute.",
        ],
    },
    "security": [
        "Runs use an IAM role that needs read access to the table's S3 data and Data Catalog entries; scope it to the databases being checked.",
        "Lake Formation permissions apply to catalog tables it governs, so the run role needs Lake Formation grants as well as IAM.",
        "Results and row-level outputs can contain real values from failing rows; write them to an encrypted bucket with a KMS key and short retention when personal data is involved.",
        "Run ETL jobs inside your VPC with S3 and Glue VPC endpoints, so data does not cross the internet.",
        "Ruleset changes and runs are recorded in CloudTrail; keep DQDL in version control so every rule change is reviewed.",
        "ADVANCED recommendations send table metadata and sampled rows to Amazon Bedrock; check that this is allowed for tables holding personal or restricted data.",
    ],
    "monitor": [
        ("glue.data.quality.rules.passed and rules.failed", "CloudWatch counts of passing and failing rules per run, for alarms."),
        ("Data Quality Evaluation Results Available event", "The EventBridge event emitted when a run finishes, used to start alerts or Step Functions."),
        ("Data quality score trend", "A falling score over days points to a drifting source before a hard rule breaks."),
        ("Observations", "Anomalies raised by anomaly detection, waiting for a person to confirm or dismiss."),
        ("Evaluation run status and duration", "Failed or slow runs mean data went unchecked or that scans are growing."),
        ("Rows sent to quarantine", "From ETL row-level results, the number of records filtered out per run and per source."),
    ],
    "limits": [
        ("Rules per ruleset", "2,000; split larger rulesets"),
        ("Ruleset size", "65 KB"),
        ("Statistics kept", "100,000 per account, retained for up to two years"),
        ("Concurrent evaluation runs", "50 per account by default, adjustable"),
        ("Concurrent recommendation runs", "25 per account by default, adjustable"),
        ("Rulesets per account", "1,000,000 by default"),
    ],
    "decisions": [
        ("Databricks builds bronze, silver and gold",
         "Rules from the metadata store, run as Lakeflow expectations and DQX, results in one table with the run id",
         "Drop: Glue Data Quality runs outside Databricks and would not join our run id."),
        ("A team already has Glue ETL jobs with DQDL rulesets feeding landing",
         "Keep the Glue rules, write their results with our run id into the shared quality table",
         "Keep if you have it: replace with Databricks checks when those jobs move."),
        ("AWS-only lakehouse on S3 Tables with Athena and Glue",
         "Glue Data Quality on catalog tables, rules in version control, anomaly detection on key tables",
         "Pursue: it is the native choice there."),
        ("Stewards want to explore a few hundred old Glue tables before migration",
         "One-off recommendation runs to profile them",
         "Pursue with care: use the output as a draft; the agreed rules move into the metadata store."),
    ],
    "faq": [
        ("What is DQDL?",
         "The Data Quality Definition Language, a short declarative language for writing rules such as completeness, uniqueness, value ranges, freshness and referential integrity. Rules are plain text, so they can be kept in Git and reviewed."),
        ("Is Glue Data Quality built on Deequ?",
         "Yes. It is built on the open-source Deequ library, which keeps the rules close to an open approach, though DQDL itself is an AWS language."),
        ("Can Glue Data Quality check Delta or Iceberg tables?",
         "Yes. Catalog checks support Iceberg, Hudi and Delta Lake tables, Amazon S3 Tables and Lake Formation managed Iceberg tables, with some limitations for Lake Formation managed formats."),
        ("Can it tell me which rows failed?",
         "Only inside Glue ETL jobs, where row-level results let you filter or quarantine bad records. Catalog runs give rule-level outcomes and scores, not failing rows."),
        ("Should I use it on a Databricks platform?",
         "Usually not. Lakeflow expectations and DQX run in the same job, write results beside the run id and keep one rules source. Keep Glue Data Quality only where Glue jobs already use it."),
    ],
    "sources": [
        ("AWS docs: AWS Glue Data Quality", "https://docs.aws.amazon.com/glue/latest/dg/data-quality.html"),
        ("AWS docs: DQDL reference", "https://docs.aws.amazon.com/glue/latest/dg/dqdl.html"),
        ("AWS docs: AWS Glue endpoints and quotas", "https://docs.aws.amazon.com/general/latest/gr/glue.html"),
        ("AWS: Glue Data Quality features and pricing", "https://aws.amazon.com/glue/features/data-quality/"),
    ],
    "related": [
        ("Medallion architecture", "/learn/medallion-architecture/"),
        ("Data platform on AWS + Databricks", "/learn/data-platform-architecture/aws-databricks/"),
        ("AWS Glue Data Catalog", "svc:glue-data-catalog"),
        ("AWS Glue ETL jobs", "svc:glue-etl"),
        ("Metadata store", "/learn/data-platform-architecture/metadata-store/"),
    ],
}
