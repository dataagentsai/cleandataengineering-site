SERVICE = {
    "slug": "athena",
    "name": "Amazon Athena",
    "short": "Athena",
    "group": "serving",
    "one_line": "Serverless SQL over files and tables in S3, billed by the data each query scans; good for small one-off questions.",
    "status": "Generally available. SQL engine version 3. Athena for Apache Spark now runs as Spark 3.5 inside SageMaker Unified Studio notebooks; the older in-console Spark notebooks stay on PySpark engine version 3.",
    "checked": "2026-11-11",
    "site_verdict": ("Keep if you have it",
                     "Keep Athena for small one-off queries on S3. It can read our gold and silver tables as Iceberg through UniForm, "
                     "but dashboards, scheduled reports and anything shared belong on the Databricks SQL warehouse, where Unity Catalog "
                     "applies masks, row filters, lineage and audit."),
    "equivalents": {"azure": "Synapse serverless SQL pool, or Fabric SQL analytics endpoint",
                    "gcp": "BigQuery (on-demand) with external or BigLake tables",
                    "databricks": "Databricks SQL serverless warehouse",
                    "open_source": "Trino (Athena engine version 3 is built on Trino) or Presto"},
    "plain": [
        "Amazon Athena lets you write ordinary SQL against files that already sit in Amazon S3, the object store where a data platform keeps its data. "
        "There is no server or cluster to start. You point Athena at a table definition, type a query, and AWS runs it on a shared fleet of machines "
        "that it manages. You pay for the amount of data the query reads, not for how long a machine was switched on.",
        "A table definition is a small record in a catalog that says: these files in this S3 folder are a table with these columns. Athena normally reads "
        "those definitions from the AWS Glue Data Catalog. The files themselves can be CSV, JSON, Parquet or ORC, or they can be open table formats such "
        "as Apache Iceberg, which add transactions and history on top of Parquet files. Athena does not store your data; it only reads and, for some "
        "statements, writes files in your bucket.",
        "Here is a concrete case. A quality engineer at a tyre plant wants to know how many curing-press readings arrived with a missing mould id last "
        "Tuesday. The raw readings land in S3 as Parquet files every few minutes. Rather than ask the platform team for a new report, she opens the Athena "
        "query editor, writes a twenty-line query with a date filter, and gets an answer in a few seconds for a few cents. That is the job Athena is best at: "
        "a question that someone asks once or twice, over data that is already in S3.",
        "Athena also has a second engine, Athena for Apache Spark, which runs Python and Spark code in notebooks. Since late 2025 the newer Spark 3.5 "
        "version lives inside Amazon SageMaker Unified Studio notebooks rather than the Athena console. On our platform Databricks already does all Spark "
        "work, so this page is mostly about the SQL engine.",
    ],
    "analogy": "A reference librarian you can phone with any question about the archive; quick and cheap for one question, but you would not ask them to run your daily newspaper.",
    "big_picture": [
        "Athena sits in the serving lane, at the very end of the platform, next to the Databricks SQL warehouse and Redshift. It reads; it is not a hop "
        "that any pipeline depends on. Data reaches S3 through the movers (DMS, AppFlow, Transfer Family, IoT Core and Firehose), Databricks turns it into "
        "bronze, silver and gold Delta tables, and Athena can then look at those tables without copying them.",
        "The connection works through UniForm. UniForm is a Delta Lake setting that writes Iceberg metadata beside the Delta metadata, so the same Parquet "
        "files can be read as an Iceberg table. Athena reads Iceberg natively. The Glue Data Catalog can now federate to Unity Catalog, which means it "
        "mirrors Unity Catalog's Iceberg tables so that Athena sees them without anyone registering them by hand. Lake Formation then hands out the "
        "permissions for those federated tables.",
        "Why keep it at all when the platform has a Databricks SQL warehouse? Because some people already use it, it costs nothing when nobody queries, "
        "and some AWS-side data never enters Unity Catalog: CloudTrail logs, S3 access logs, the Cost and Usage Report and VPC flow logs. Athena is the "
        "natural tool for those. For business data, the governed path is the SQL warehouse, because Athena does not see Unity Catalog's column masks or "
        "row filters.",
    ],
    "upstream": ["svc:s3", "svc:glue-data-catalog", "Databricks gold tables through UniForm (Iceberg)"],
    "downstream": ["Analysts and engineers in the query editor", "svc:quicksight", "Audit and cost queries on CloudTrail and CUR"],
    "concepts": [
        ("Data scanned", "The bytes Athena reads from S3 to answer a query. It is what you pay for under the default pricing, so column and partition pruning matter."),
        ("Workgroup", "A named bucket of settings and limits: where results go, which engine version, how much one query may scan, and who may use it. Use one per team or purpose."),
        ("Partition", "A folder split on a column such as date or plant, so a query with a filter on that column reads only the matching folders."),
        ("Partition projection", "A table setting that lets Athena calculate partition locations from a pattern instead of looking them up in the catalog; much faster on tables with many partitions."),
        ("Iceberg table", "An open table format with snapshots and transactions. Athena can read it, run UPDATE, DELETE and MERGE on it, and use its file statistics to skip data."),
        ("UniForm", "A Delta Lake feature that also writes Iceberg metadata, so Iceberg readers such as Athena can read a Databricks Delta table."),
        ("Federated query", "A query to a source outside S3, such as a database, through a connector that runs as a Lambda function."),
        ("Capacity reservation", "Dedicated compute measured in DPUs (data processing units) that you pay for by time instead of by bytes scanned; now from 4 DPUs for as little as one minute."),
        ("CTAS", "CREATE TABLE AS SELECT: a query whose result is written as a new table in S3, often used to make a smaller, cleaner copy."),
    ],
    "use_when": [
        "Someone needs a one-off answer from files or tables already in S3, and building a report would take longer than asking the question.",
        "You want to query AWS service logs such as CloudTrail, S3 access logs, VPC flow logs or the Cost and Usage Report, which never enter Unity Catalog.",
        "Query volume is low and uneven, so paying per query is cheaper than keeping a warehouse running.",
        "A team that already knows Athena needs read access to gold tables, and the tables are exposed as Iceberg through UniForm with permissions in Lake Formation.",
        "You need a quick check during an incident, for example counting rows in a landing folder before Databricks has picked them up.",
    ],
    "avoid_when": [
        "The query feeds a dashboard that many people refresh during the day; per-scan billing and shared capacity make cost and speed unpredictable.",
        "The data holds personal or sensitive columns that Unity Catalog masks; Athena does not see those masks, so access would bypass them.",
        "You want to build pipelines or transform bronze into silver; that work belongs in Databricks Lakeflow, with its quality rules and lineage.",
        "Queries scan raw CSV or JSON with no partitions; costs grow with every query and a CTAS copy to Parquet or Iceberg is the first fix.",
        "You need sub-second answers for an application; Athena queries queue and start in seconds, not milliseconds.",
    ],
    "challenges": [
        ("Surprise bill from a full scan",
         "One SELECT star over a year of raw sensor JSON scans terabytes, and someone running it in a loop turns it into a large bill.",
         "Set a per-query data-scanned limit on every workgroup, store data as Parquet or Iceberg, partition by date, and train people to select only the columns they need."),
        ("Too many small files",
         "Firehose and streaming writers create thousands of tiny files; Athena spends its time opening files rather than reading data and queries crawl.",
         "Compact files to a few hundred megabytes. For Delta tables Databricks OPTIMIZE does it; for Iceberg tables use OPTIMIZE in Athena or the Glue table optimizers."),
        ("Partition lookups slow every query",
         "A table with hundreds of thousands of partitions makes Athena spend seconds listing them in the Glue catalog before reading a byte.",
         "Use partition projection for date-based folders, or Iceberg tables where partitions are tracked in metadata rather than in the catalog."),
        ("Queued queries and TooManyRequestsException",
         "During month-end many analysts run queries at once; the account hits its active-query quota, which counts queued queries too, and new ones fail.",
         "Watch the quota in Service Quotas, retry with backoff in tools, request an increase, or buy a small capacity reservation for the busy workgroup."),
        ("Governance gap with Unity Catalog",
         "Athena reads the files through Glue and Lake Formation, so masks and row filters defined in Unity Catalog do not apply.",
         "Expose only tables without sensitive columns, or publish a separate masked gold view as its own table; keep personal data on the Databricks SQL warehouse."),
        ("Stale UniForm metadata",
         "Athena shows yesterday's numbers because the Iceberg metadata of a Delta table lags the latest Delta commit.",
         "Check that UniForm metadata generation succeeds after each write, and confirm the Glue federation points at the current metadata location."),
        ("Result files pile up",
         "Every query writes its result to the results bucket; years of results, some with personal data, sit there unencrypted and unmanaged.",
         "Put an S3 lifecycle rule on the results location, encrypt it with KMS, and enforce the location in the workgroup settings."),
        ("Federated connectors become hidden pipelines",
         "Someone uses a Lambda connector to join SAP or MES databases live, and production databases take the load of every query.",
         "Use federation only for small lookups; bring the data in through DMS or AppFlow and query the copy."),
    ],
    "compare": [
        ("Databricks SQL serverless warehouse",
         "Many users, dashboards, Genie, governed access through Unity Catalog with masks and lineage; the default for business data on this platform.",
         "One person asks one question a week about AWS logs; a warehouse adds little there."),
        ("Amazon Redshift (and Redshift Spectrum)",
         "You already run Redshift for BI and want lake data joined with warehouse tables in the same SQL.",
         "You have no Redshift today; do not start one just for ad hoc queries."),
        ("Amazon EMR with Trino",
         "You need Trino features or connectors Athena lacks, or very heavy steady query load where a cluster is cheaper.",
         "You do not want to run and patch a cluster."),
        ("Azure Synapse serverless SQL pool or Fabric SQL endpoint",
         "The data lives in Azure storage and the team works in the Microsoft stack.",
         "The data is in S3; cross-cloud reads cost egress and add latency."),
        ("Google BigQuery",
         "The platform is on GCP; BigQuery's on-demand pricing works the same way, per byte scanned.",
         "Data is in S3; BigQuery Omni exists but adds another vendor to run."),
        ("Self-run Trino or DuckDB",
         "A small team wants a free engine on a laptop or a container for quick file checks.",
         "Many users need shared access, audit and managed scaling."),
    ],
    "cost": {
        "model": "By default Athena SQL charges per terabyte of data scanned, rounded up to the nearest megabyte, with a 10 MB minimum per query (5 US dollars per TB in the AWS pricing example; list price, check your region). "
                 "DDL statements and partition management are not charged per scan, but failed and cancelled queries are billed for what they read. "
                 "Alternatively, capacity reservations charge per DPU-hour for dedicated compute, now from 4 DPUs and one minute, and queries in that workgroup are not billed by scan. "
                 "Athena for Apache Spark is billed per DPU-hour. S3 requests, Glue catalog calls and Lambda connectors are billed separately by those services.",
        "drivers": [
            "Bytes read per query, which depends on file format, compression, partitioning and the columns selected.",
            "How often the same query is run, especially by dashboards or scripts on a schedule.",
            "S3 GET requests on tables made of many small files.",
            "Reserved DPUs, if you choose capacity reservations, charged whether or not queries run.",
        ],
        "traps": [
            "A BI tool pointed at Athena refreshes every visual on every page open, so one dashboard can scan more than all analysts together.",
            "Queries over raw CSV or JSON read every byte, every time; converting to Parquet often cuts scan by ten times or more.",
            "Cancelled and failed queries are still billed for the data they read.",
            "Query results and CTAS outputs accumulate in S3 and are billed as storage forever unless a lifecycle rule removes them.",
        ],
    },
    "security": [
        "Access is IAM: grant athena actions per workgroup, plus Glue catalog read and S3 read on only the needed prefixes. Use Lake Formation for table and column grants on federated Unity Catalog tables.",
        "Encrypt query results with SSE-KMS and enforce this in the workgroup, so users cannot override it. Use the catalog's KMS key for the data buckets.",
        "Reach Athena, Glue and S3 through interface and gateway VPC endpoints so no traffic crosses the internet, in line with the platform's no-public-IP rule.",
        "CloudTrail records every StartQueryExecution call with the query text and the caller, which gives a simple audit trail.",
        "Personal data: Unity Catalog masks do not apply in Athena, so either keep tables with personal data out of the federated catalog or publish masked copies; Macie can scan the results bucket too.",
    ],
    "monitor": [
        ("ProcessedBytes", "Bytes scanned per query, by workgroup, in CloudWatch; the main cost signal."),
        ("TotalExecutionTime and QueryQueueTime", "How long queries take and how long they wait before starting; rising queue time means you are near the concurrency quota."),
        ("Workgroup data usage control alarms", "Alerts when a workgroup crosses a scanned-bytes threshold per hour or per day."),
        ("TooManyRequestsException errors", "Queries rejected because the active-query quota, which includes queued queries, is full."),
        ("DPUAllocated and DPUConsumed", "For capacity reservations: how much of the reserved compute you actually use."),
        ("CUR line items for Athena", "Spend per workgroup through cost allocation tags, to see which team scans what."),
    ],
    "limits": [
        ("Query string length", "262,144 bytes, not adjustable"),
        ("DML query timeout", "Default 30 minutes, increase up to 240 minutes"),
        ("Active DML queries", "Varies by Region; running and queued queries both count"),
        ("Partitions per scan", "Up to 1 million read in a single scan, on tables of up to 10 million partitions"),
        ("Workgroups", "1,000 per Region per account"),
    ],
    "decisions": [
        ("A plant quality engineer asks a one-off question about last week's readings in S3",
         "Athena on the Parquet or Iceberg table, inside a workgroup with a scan limit",
         "Keep if you have it: fast and cheap for the occasional question; no cluster to run."),
        ("The sales team wants a daily dashboard on gold order tables",
         "Databricks SQL warehouse with AI/BI dashboards or a BI tool",
         "Pursue with care: use the warehouse, not Athena; dashboards need steady speed and Unity Catalog masks."),
        ("Security wants to search a month of CloudTrail logs",
         "Athena over the CloudTrail bucket with partition projection, or CloudTrail Lake",
         "Pursue: AWS logs never enter Unity Catalog, and Athena is the natural tool."),
        ("An analyst wants live joins against the MES database through a Lambda connector",
         "Federated query",
         "Drop: bring the data in with DMS and query the copy; do not load production databases with ad hoc joins."),
    ],
    "faq": [
        ("Can Athena read Databricks Delta tables?",
         "Yes, the safest way is to turn on UniForm so the Delta table also has Iceberg metadata, then let Athena read it as Iceberg through the Glue Data Catalog, which can federate to Unity Catalog. Athena also has native Delta Lake reading, but the Iceberg route is the one the reference platform uses."),
        ("Is Athena cheaper than a Databricks SQL warehouse?",
         "For a handful of queries a day, usually yes, because Athena costs nothing when idle. For dashboards and many users, a warehouse that scales and caches results is usually cheaper and much more predictable. Measure with your own queries before deciding."),
        ("Why is my Athena query slow?",
         "The common causes are many small files, no partition filter, raw text formats, and queueing at the concurrency quota. Check QueryQueueTime first, then the bytes scanned, then the file count."),
        ("Does Athena still have Spark notebooks?",
         "Yes. The newer Apache Spark 3.5 engine runs inside SageMaker Unified Studio notebooks; the older PySpark engine version 3 keeps the in-console notebooks. On a Databricks platform you rarely need either."),
        ("How do I stop one query from costing a fortune?",
         "Set a per-query data usage control on every workgroup, enforce the workgroup settings, and alert on ProcessedBytes. Also convert raw folders to Parquet or Iceberg."),
    ],
    "sources": [
        ("AWS docs: Athena service quotas", "https://docs.aws.amazon.com/athena/latest/ug/service-limits.html"),
        ("AWS: Athena pricing", "https://aws.amazon.com/athena/pricing/"),
        ("AWS What's New: Athena 1-minute reservations and 4 DPU minimum (Feb 2026)", "https://aws.amazon.com/about-aws/whats-new/2026/02/amazon-athena-one-minute-capacity-reservations/"),
        ("AWS docs: Use Apache Spark in Amazon Athena", "https://docs.aws.amazon.com/athena/latest/ug/notebooks-spark.html"),
        ("AWS Big Data blog: Access Databricks Unity Catalog data using catalog federation in the Glue Data Catalog", "https://aws.amazon.com/blogs/big-data/access-databricks-unity-catalog-data-using-catalog-federation-in-the-aws-glue-data-catalog/"),
    ],
    "related": [
        ("AWS and Databricks reference platform", "/learn/data-platform-architecture/aws-databricks/"),
        ("Delta vs Iceberg", "/learn/delta-vs-iceberg/"),
        ("Amazon Redshift", "svc:redshift"),
        ("AWS Glue Data Catalog", "svc:glue-data-catalog"),
        ("Table maintenance", "/learn/table-maintenance/"),
    ],
}
