SERVICE = {
    "slug": "aurora-postgresql",
    "name": "Amazon Aurora PostgreSQL (incl. Serverless v2)",
    "short": "Aurora PostgreSQL",
    "group": "operational",
    "one_line": "AWS's PostgreSQL-compatible database on shared, self-healing storage; a common source for DMS, and the metadata store considered but not chosen.",
    "status": "Generally available. Serverless v2 can scale to 0 capacity units and pause when idle. Cluster storage reaches 256 TiB on PostgreSQL 15.13, 16.9, 17.5 and later (128 TiB on older versions).",
    "checked": "2026-11-11",
    "site_verdict": ("Keep if you have it",
                     "Aurora PostgreSQL is often a source system: DMS reads it with change capture into S3 landing, or zero-ETL feeds Redshift. "
                     "For the platform's own metadata database it was the default until 4 Nov and a good fit, but Lakebase was chosen to drop one AWS "
                     "service to run, connect privately and back up. Do not start a new Aurora database for the data platform itself."),
    "equivalents": {"azure": "Azure Database for PostgreSQL flexible server",
                    "gcp": "AlloyDB for PostgreSQL",
                    "databricks": "Lakebase (Databricks managed PostgreSQL)",
                    "open_source": "PostgreSQL with Patroni for failover"},
    "plain": [
        "Amazon Aurora PostgreSQL is a relational database that speaks PostgreSQL. Applications connect with normal PostgreSQL drivers, run SQL, use "
        "transactions, foreign keys and JSON columns, and most PostgreSQL extensions work. What AWS changed is the storage underneath. Instead of a "
        "disk attached to one server, an Aurora cluster writes to a shared storage volume that keeps six copies of the data across three "
        "Availability Zones and grows on its own.",
        "A cluster has one writer instance and up to 15 reader instances, all reading the same storage, so a reader can be promoted to writer in "
        "about a minute or less if the writer fails. Instances are either provisioned, with a fixed size you pick, or Serverless v2, measured in "
        "Aurora Capacity Units (ACUs) that rise and fall with load. Serverless v2 can now scale to zero ACUs and pause after an idle period you "
        "set, then resume in up to about 15 seconds when a connection arrives.",
        "A manufacturing example: a plant's manufacturing execution system, the MES that tracks work orders, batches and quality checks, runs on "
        "Aurora PostgreSQL. The data platform does not own that database; it reads from it. AWS DMS takes a full copy once and then follows the "
        "change log, writing every insert, update and delete as files into the S3 landing area. Databricks turns those files into bronze and "
        "silver tables. The MES team keeps running their database exactly as before.",
    ],
    "analogy": "A shop with one cashier and several helpers who all read from the same shared ledger, which is copied six times in three back rooms.",
    "big_picture": [
        "Aurora PostgreSQL shows up in two places on the reference platform. The first and most common is as a source. MES, quality and "
        "ordering systems often run on it. DMS reads them with change data capture, which uses PostgreSQL's logical replication to stream "
        "changes, and lands them in S3 for the Databricks medallion layers. Where Redshift is still in use, Aurora's zero-ETL integration can "
        "also copy tables into Redshift within seconds without a pipeline.",
        "The second place is the metadata database. The platform keeps one store that declares every source, table, rule, owner and budget, "
        "plus runtime state such as watermarks, the run log and quality results. That is relational data, and PostgreSQL fits it, including "
        "jsonb for the merged view. Aurora PostgreSQL Serverless v2 was the default choice until 4 Nov. It was not chosen in the end: "
        "Lakebase, a managed PostgreSQL inside Databricks, gives the same database without another AWS service to run, connect over private "
        "networking and back up, and it is reachable from serverless compute with no network setup.",
        "A third idea was rejected. Writing the fast lane's live values into Aurora and exposing them through Lakehouse Federation would look "
        "governed, but the live app would still read Aurora directly, outside Unity Catalog. The site marks that Drop: governance on paper only.",
    ],
    "upstream": ["Applications (MES, ordering, quality)", "svc:dms"],
    "downstream": ["svc:dms", "svc:zero-etl", "Databricks Lakehouse Federation (read-only queries)"],
    "concepts": [
        ("Cluster volume", "The shared storage behind every instance in a cluster: six copies across three zones, growing automatically up to 128 or 256 TiB depending on version."),
        ("Writer and readers", "One instance accepts writes; up to 15 readers serve reads from the same storage with typically small lag."),
        ("Aurora Capacity Unit (ACU)", "The Serverless v2 measure of capacity, roughly 2 GiB of memory with matching CPU and network; you set a minimum and maximum."),
        ("Scale to zero", "Serverless v2 with a minimum of 0 ACUs pauses after an idle time between 5 minutes and 24 hours, billing only storage until a connection wakes it."),
        ("Logical replication", "PostgreSQL's way of publishing row changes from the write-ahead log; DMS and Debezium use it for change data capture."),
        ("Replication slot", "A marker that holds the write-ahead log until a consumer has read it; an abandoned slot makes storage grow without limit."),
        ("I/O-Optimized", "A storage pricing option with no per-I/O charge and higher instance and storage prices; it pays off when I/O is a large share of the bill."),
        ("Global Database", "Copies a cluster to other Regions with typically under a second of lag, for disaster recovery or local reads."),
        ("RDS Proxy", "A managed connection pooler that shares a small number of database connections among many short-lived clients such as Lambda functions."),
    ],
    "use_when": [
        "An application team needs a relational database with fast failover and storage that grows on its own, and it lives on AWS.",
        "A source system already runs on it; the data platform reads it with DMS change capture, and nothing needs to change.",
        "You need many read replicas sharing one copy of storage, for example reporting reads for an ordering system.",
        "Dev and test databases sit idle most of the day; Serverless v2 with scale to zero cuts their compute bill to storage only.",
        "You want PostgreSQL with zero-ETL into Redshift for an existing Redshift estate.",
    ],
    "avoid_when": [
        "It would be a new metadata database for this platform; Lakebase was chosen to avoid one more AWS service to run and connect.",
        "You hope Lakehouse Federation makes a live store governed while apps still read it directly; the site marks that Drop.",
        "The workload is analytical, scanning millions of rows for totals; that belongs on Delta tables and a SQL warehouse.",
        "A small, steady database would do; RDS for PostgreSQL is cheaper and simpler for that.",
        "The data platform itself would write business tables there; gold tables belong in Unity Catalog.",
    ],
    "challenges": [
        ("Abandoned replication slot", "A DMS task is stopped but its slot remains; the write-ahead log is kept forever and storage and cost climb.",
         "Alarm on the replication slot lag metric and on transaction log disk use. Drop slots when a CDC task is retired."),
        ("CDC prerequisites missed", "DMS cannot start change capture because logical replication is off or tables lack primary keys.",
         "Set rds.logical_replication to 1 in the cluster parameter group (needs a reboot), and confirm every captured table has a primary key."),
        ("Failover breaks connections", "During a writer failover clients holding old connections fail for some seconds.",
         "Connect through the cluster endpoint, keep DNS caching short, use RDS Proxy for many short-lived clients, and test failover before go-live."),
        ("Too many connections", "Many jobs or Lambda functions each open their own connections and exhaust max_connections.",
         "Pool connections with RDS Proxy or PgBouncer and keep the pool small per job."),
        ("Serverless cold resume", "A dev database paused at 0 ACUs takes up to about 15 seconds to wake, and the first job times out.",
         "Keep a minimum of 0.5 ACU for databases with schedules, or raise client connect timeouts in dev."),
        ("Unexpected I/O bill", "On the Standard storage option a heavy workload pays per I/O and the bill jumps.",
         "Check the I/O share of the bill in Cost Explorer; switch to I/O-Optimized when I/O is more than about a quarter of Aurora spend."),
        ("Version end of support", "Major versions leave standard support and move into paid Extended Support.",
         "Track the Aurora PostgreSQL release calendar and plan one major upgrade a year, with blue/green deployments to cut downtime."),
    ],
    "compare": [
        ("Lakebase (Databricks managed PostgreSQL)", "You need PostgreSQL for the platform's own metadata or a governed live store; chosen on 4 Nov.",
         "The database belongs to an application team on AWS, or Lakebase is not yet available in your region."),
        ("Amazon RDS for PostgreSQL", "A small, steady database where a fixed-size server is enough and cost matters most.",
         "You need fast failover, many readers or storage that grows on its own."),
        ("Amazon Aurora DSQL", "A new distributed, serverless PostgreSQL-compatible database for active-active across Regions.",
         "You need the full PostgreSQL feature set and extensions; DSQL supports a subset."),
        ("Amazon DynamoDB", "Key-value lookups at any scale with no joins, such as the fast lane's live store.",
         "The data is relational, like metadata with keys between tables."),
        ("Azure Database for PostgreSQL or Google AlloyDB", "You are building on Azure or Google Cloud.", "You are on AWS."),
    ],
    "cost": {
        "model": "Provisioned instances bill per instance-hour by size; Serverless v2 bills per ACU-hour actually used, down to zero when paused. "
                 "Storage bills per GB-month of cluster volume. Under the Standard option you also pay per million I/O requests; under "
                 "I/O-Optimized there is no I/O charge but instance and storage prices are higher. Backups beyond the size of the database, "
                 "snapshot exports, Global Database replication and Extended Support for old major versions are extra. Reserved instances "
                 "and Database Savings Plans lower provisioned rates. List prices, check your region.",
        "drivers": [
            "Instance size and count, including every reader and any idle replicas.",
            "Serverless v2 minimum ACUs, which bill around the clock if not set to zero.",
            "I/O volume under the Standard option.",
            "Storage, which includes write-ahead log held by unread replication slots.",
            "Backup retention and manual snapshots kept forever.",
        ],
        "traps": [
            "A forgotten DMS replication slot keeps write-ahead log and storage grows every day.",
            "A Serverless v2 minimum set high for safety bills like a provisioned instance.",
            "Running a major version past end of standard support adds an Extended Support charge per vCPU-hour.",
            "Readers added for one report are never removed.",
            "Cross-Region Global Database copies bill storage and replicated I/O in each Region.",
        ],
    },
    "security": [
        "Place the cluster in private subnets with no public access, and allow only named security groups, such as the DMS replication instance's.",
        "Encrypt at rest with a customer managed KMS key; encryption must be set at creation and cannot be turned on later without a copy and restore.",
        "Use IAM database authentication or Secrets Manager with rotation for the DMS and application users; never put passwords in job code.",
        "Give the DMS user only the replication and SELECT rights it needs on the captured schemas.",
        "Turn on Database Activity Streams or pgAudit for audit of who read personal data, and send logs to CloudWatch.",
        "Force TLS for client connections with the rds.force_ssl parameter.",
    ],
    "monitor": [
        ("ServerlessDatabaseCapacity", "Current ACUs for Serverless v2; shows whether the minimum is too high or the maximum is being hit."),
        ("OldestReplicationSlotLag", "How much write-ahead log the slowest replication slot is holding; a rising value means a stalled CDC consumer."),
        ("TransactionLogsDiskUsage", "Space used by write-ahead log; climbs when slots are not consumed."),
        ("AuroraReplicaLag", "How far readers trail the writer; high values mean stale reads."),
        ("DatabaseConnections", "Open connections against max_connections; spikes point at missing pooling."),
        ("VolumeBytesUsed", "Cluster storage used; compare with the 128 or 256 TiB ceiling and with your bill."),
    ],
    "limits": [
        ("Cluster storage", "256 TiB on Aurora PostgreSQL 15.13, 16.9, 17.5 and later; 128 TiB on earlier versions"),
        ("Table size", "32 TiB per table"),
        ("Readers", "Up to 15 Aurora Replicas per cluster"),
        ("Serverless v2 capacity", "0 to 384 ACUs on recent Aurora PostgreSQL versions; check yours"),
        ("DB instances per Region", "40 by default (20 in Mumbai, ap-south-1), shared with RDS, adjustable"),
    ],
    "decisions": [
        ("Metadata database for the platform", "Aurora PostgreSQL Serverless v2",
         "Drop: considered, not chosen on 4 Nov; Lakebase gives the same PostgreSQL inside Databricks with one fewer AWS service."),
        ("MES database already on Aurora", "DMS full load plus CDC into S3 landing",
         "Keep if you have it: the normal path; enable logical replication and watch slot lag."),
        ("Live store exposed through Lakehouse Federation", "Aurora written by Flink, read by the app",
         "Drop: governance on paper only, since the app reads Aurora directly."),
        ("Existing Redshift reports need near-real-time order data", "Aurora zero-ETL into Redshift",
         "Pursue with care: no pipeline to run, but it feeds Redshift, which the platform is phasing down."),
        ("Lakebase not yet available in the platform's region", "Aurora PostgreSQL Serverless v2 for metadata as a stopgap",
         "Pursue with care: behind the metadata store's interface so it can move to Lakebase later."),
    ],
    "faq": [
        ("Aurora PostgreSQL or RDS for PostgreSQL?",
         "Aurora gives faster failover, up to 15 readers on shared storage and storage that grows on its own. RDS is cheaper and simpler for a small, steady database. Both are the same PostgreSQL to the application."),
        ("Can Aurora Serverless v2 scale to zero?",
         "Yes. Set the minimum to 0 ACUs and choose an idle time from 5 minutes to 24 hours. Compute stops billing while paused, storage still bills, and resuming takes up to about 15 seconds."),
        ("Why did the platform choose Lakebase over Aurora for metadata?",
         "Both are PostgreSQL and fit the design. Lakebase runs inside Databricks, is governed by Unity Catalog and is reachable from serverless compute with no network setup, so there is one fewer AWS service to run, connect privately and back up."),
        ("How does Databricks read an Aurora database?",
         "For bulk and ongoing loads, DMS lands changes in S3 and Databricks builds bronze from them. For occasional queries, Lakehouse Federation can query Aurora from Databricks without copying."),
        ("What does DMS need from Aurora PostgreSQL for CDC?",
         "Logical replication turned on in the cluster parameter group, a user with replication rights, and primary keys on captured tables. Then watch the replication slot so it never stalls."),
    ],
    "sources": [
        ("AWS docs: Quotas and constraints for Amazon Aurora", "https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_Limits.html"),
        ("AWS docs: Scaling to zero ACUs with automatic pause and resume", "https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2-auto-pause.html"),
        ("AWS docs: How Aurora Serverless v2 works", "https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.how-it-works.html"),
        ("AWS pricing: Amazon Aurora", "https://aws.amazon.com/rds/aurora/pricing/"),
    ],
    "related": [
        ("Metadata store", "/learn/data-platform-architecture/metadata-store/"),
        ("AWS and Databricks reference platform", "/learn/data-platform-architecture/aws-databricks/"),
        ("Ingestion", "/learn/data-platform-architecture/ingestion/"),
        ("AWS DMS", "svc:dms"),
        ("Amazon RDS for PostgreSQL", "svc:rds-postgresql"),
        ("Zero-ETL integrations", "svc:zero-etl"),
    ],
}
