SERVICE = {
    "slug": "glue-data-catalog",
    "name": "AWS Glue Data Catalog (and table optimizers)",
    "short": "Glue Data Catalog",
    "group": "catalog",
    "one_line": "The AWS-native list of databases, tables and their file locations that Athena, EMR, Redshift and Glue jobs use to find data in S3.",
    "status": "Generally available. Table optimizers (compaction, snapshot retention, orphan file deletion) are generally available for Apache Iceberg tables only, including Iceberg v3.",
    "checked": "2026-11-11",
    "site_verdict": ("Keep if you have it",
                     "On this platform Unity Catalog is the one catalog for everything new. Existing Glue tables are read in place "
                     "through Unity Catalog catalog federation while they move, and AWS engines can reach Unity Catalog tables the other "
                     "way. Never let two catalogs write the same S3 path."),
    "equivalents": {"azure": "Microsoft Purview Unified Catalog (and the OneLake catalog in Fabric)",
                    "gcp": "BigLake metastore and Dataplex Universal Catalog",
                    "databricks": "Unity Catalog",
                    "open_source": "Apache Hive Metastore, Apache Polaris or any Iceberg REST catalog"},
    "plain": [
        "A data lake on S3 is, at bottom, millions of files in folders. A file called part-0001.parquet does not say which "
        "table it belongs to, what its columns are called or which folder holds the rest of the table. A catalog is the "
        "piece that answers those questions. It is a small database about your data, often called metadata, which "
        "simply means data that describes other data. For each table it records the name, the columns and their types, "
        "the S3 folder where the files live, the file format and, for partitioned tables, the list of partitions.",
        "The AWS Glue Data Catalog is the catalog that AWS's own engines share. When an analyst in Athena types "
        "SELECT * FROM sales.orders, Athena asks the Glue Data Catalog where sales.orders lives and what its columns are, "
        "then reads the files. EMR, Redshift Spectrum, Glue ETL jobs and Amazon Data Firehose all use the same catalog, "
        "so a table defined once is visible to all of them. There is one Data Catalog per account per region, organised "
        "as catalogs, databases (also called schemas) and tables.",
        "Take a retailer that lands daily order extracts from SAP as Parquet files in s3://retail-landing/orders/. Until "
        "someone registers a table, those files are just files. A Glue crawler, which is a job that reads sample files and "
        "guesses the schema, or a CREATE TABLE statement, writes a table entry called landing.sap_orders pointing at that "
        "folder. From then on Athena, EMR and Glue jobs can query it by name.",
        "For Apache Iceberg tables the catalog does one more job: it holds the pointer to the table's current metadata "
        "file, so a write only becomes real when Glue swaps that pointer. That makes Glue the owner of those tables. Glue "
        "table optimizers are optional managed jobs that tidy such Iceberg tables for you: they merge small files, expire "
        "old snapshots and delete orphan files that nothing references any more.",
    ],
    "analogy": "A library's card index: it does not hold the books, it tells every reader which shelf each book is on, and for Iceberg books it also decides which edition is the current one.",
    "big_picture": [
        "On this site's reference platform, the catalog role belongs to Unity Catalog. Databricks writes bronze, silver and "
        "gold as Unity Catalog managed tables in S3, and Unity Catalog holds their permissions, lineage, masks and audit. "
        "The Glue Data Catalog is therefore not on the main path. It sits across the platform as the catalog that AWS "
        "services already use, and it matters in three situations.",
        "First, migration. Many AWS estates already have hundreds of Glue tables behind Athena reports and EMR jobs. Rather "
        "than copy them, Unity Catalog federates to the Glue catalog: it shows those tables as foreign tables that another "
        "catalog owns, and Databricks reads them in place while the work moves. No new tables are created in Glue from day one.",
        "Second, AWS readers. Athena, Redshift and EMR still need to read some gold tables. The site's answer is Iceberg "
        "reads on Delta (UniForm) through Unity Catalog's Iceberg REST catalog. AWS also offers the reverse: Glue catalog "
        "federation can point at Unity Catalog so AWS engines see Unity Catalog tables through Glue, which AWS documents "
        "for reading. Either way there is still one owner per table.",
        "Third, AWS-only corners. S3 Tables integrate with Glue so AWS engines can find them, Firehose writes Iceberg "
        "tables registered in Glue, and Glue table optimizers keep Glue-owned Iceberg tables healthy. If a team runs such "
        "a corner without Databricks, Glue is the right catalog for it.",
    ],
    "upstream": ["svc:glue-etl", "svc:data-firehose", "Glue crawlers and CREATE TABLE statements"],
    "downstream": ["svc:athena", "svc:emr", "Databricks Unity Catalog (catalog federation)"],
    "concepts": [
        ("Catalog, database, table", "The three levels of naming. A catalog holds databases, a database holds tables, and a table records columns, format and an S3 location."),
        ("Partition", "A slice of a table stored in its own folder, such as one day of orders. Hive-style tables list every partition in the catalog, which is why partition counts matter."),
        ("Crawler", "A Glue job that samples files in an S3 path, guesses the schema and creates or updates table entries. Useful to start, risky as a permanent source of truth."),
        ("Iceberg metadata pointer", "For Iceberg tables, the catalog stores the location of the current metadata file. Swapping that pointer is the commit, so the catalog owns the table."),
        ("Table optimizers", "Managed jobs you switch on per Iceberg table or per catalog: compaction, snapshot retention and orphan file deletion. They run on AWS compute and are billed as Glue."),
        ("Catalog federation", "Showing tables that another catalog owns without copying them. Unity Catalog can federate to Glue, and Glue can federate to remote Iceberg REST catalogs such as Unity Catalog."),
        ("Iceberg REST endpoint", "An open web API that any Iceberg engine can use to ask a catalog for tables. Glue offers one, so non-AWS engines can also read Glue Iceberg tables."),
        ("Column statistics", "Counts, minimums, maximums and distinct values per column that Glue can compute and store, so query planners such as Athena and Redshift choose better plans."),
    ],
    "use_when": [
        "You already run Athena, EMR or Redshift Spectrum against tables registered in Glue and need them to keep working while you move to Databricks.",
        "An AWS-only part of the estate, without Databricks, needs a catalog for Firehose, Glue jobs and Athena.",
        "Another team owns Iceberg tables in Glue or S3 Tables and you only need to read them from Databricks through catalog federation.",
        "AWS engines must see Unity Catalog tables by name and the team prefers Glue federation over pointing each engine at Unity Catalog's Iceberg REST catalog.",
        "You own Glue Iceberg tables and want AWS to run compaction and clean-up for them, which is exactly what table optimizers are for.",
    ],
    "avoid_when": [
        "Do not use Glue as a second catalog for new Databricks tables. Unity Catalog is the catalog for everything new on this platform.",
        "Do not register the same S3 path in both Glue and Unity Catalog with both sides writing. One day a clean-up job deletes files the other still needs.",
        "Do not rely on crawlers as the long-term definition of production tables. Schemas should come from code or contracts, not guesses from sample files.",
        "Do not expect table optimizers to help Delta tables or Unity Catalog managed tables. They work only on Iceberg tables Glue owns.",
    ],
    "challenges": [
        ("Two catalogs, one path",
         "Glue and Unity Catalog both register the same folder. Each thinks it owns the files, and maintenance or a DROP on one side breaks the other.",
         "Give every table exactly one owning catalog. Other engines read through federation or Iceberg REST, never by a second registration with write rights."),
        ("Crawler drift",
         "A crawler sees a new file with an extra column or a different type and silently changes the table, or splits one table into many.",
         "Use crawlers only to bootstrap. Define production tables in code, set crawler schema change policy to log only, and alert on table version changes."),
        ("Partition explosion",
         "Hive-style tables partitioned by hour and plant create millions of partitions. Planning slows and you approach the 10 million partitions per table quota.",
         "Partition coarsely, use partition projection in Athena for predictable layouts, or move to Iceberg, which tracks files in its own metadata rather than catalog partitions."),
        ("Optimizers left off",
         "Firehose or streaming jobs write small Iceberg files every minute. Queries slow down and storage grows because old snapshots are never expired.",
         "Switch on compaction, snapshot retention and orphan file deletion, at catalog level if possible, and watch their run history and metrics."),
        ("Retention set too short",
         "Snapshot retention or orphan deletion runs aggressively, and long queries or time travel fail with file-not-found.",
         "Set retention to match how far back people actually travel in time, and keep orphan deletion's age threshold well above your longest job."),
        ("Permissions in two places",
         "Glue access is decided by IAM, by Lake Formation, or by both in hybrid mode, while Databricks uses Unity Catalog grants. Rules drift apart.",
         "Make no new grants on the AWS side, read Glue tables through Unity Catalog federation, and keep a dated list of the remaining AWS-side grants until they are retired."),
        ("Table versions pile up",
         "Every schema change or crawler run writes a new table version. Busy tables hit the 100,000 versions per table quota and updates fail.",
         "Stop needless crawler runs and delete old table versions with the Glue API on a schedule."),
    ],
    "compare": [
        ("Databricks Unity Catalog",
         "Databricks is the main engine and you want one place for grants, row filters, column masks, lineage and audit, with Predictive Optimization on managed tables.",
         "The estate is AWS-only and every engine is Athena, EMR, Redshift or Glue."),
        ("Amazon S3 Tables",
         "You are AWS-only and want storage, an Iceberg catalog and automatic maintenance in one service, the AWS twin of a managed table.",
         "You need a general catalog for Hive-style or Delta tables, or Databricks is your main writer."),
        ("Apache Hive Metastore",
         "You have legacy Hadoop or on-premises Spark jobs that speak only to a Hive metastore.",
         "You want a managed service; Glue is Hive-compatible and removes the database you would otherwise run."),
        ("Microsoft Purview and Fabric OneLake catalog",
         "The platform is on Azure and the catalog must also cover Power BI and Microsoft 365 assets.",
         "Your data and engines are on AWS."),
        ("Google BigLake metastore and Dataplex",
         "The platform is on Google Cloud with BigQuery as the main engine.",
         "Your data and engines are on AWS."),
        ("Apache Polaris or another Iceberg REST catalog",
         "You want an open, engine-neutral Iceberg catalog that you run yourself.",
         "You would rather not operate catalog infrastructure, or Unity Catalog already serves Iceberg REST for you."),
    ],
    "cost": {
        "model": "The Data Catalog is billed on two meters: the number of objects stored (tables, partitions, table versions, "
                 "indexes) above a free monthly allowance, and the number of requests above a free monthly allowance. AWS "
                 "lists the first million objects and the first million requests a month as free; list price, check your "
                 "region. Crawlers, table optimizers and column statistics runs are billed separately as Glue compute, by "
                 "data processing unit hours, where a data processing unit (DPU) is a fixed slice of CPU and memory.",
        "drivers": [
            "Partition counts on Hive-style tables, because each partition is a stored object.",
            "Request volume from Athena, EMR and Spark jobs that list partitions on every query.",
            "Crawler frequency and how many files each crawl samples.",
            "Compaction work by table optimizers, which grows with the number of small files written.",
        ],
        "traps": [
            "Crawlers scheduled hourly on big prefixes run all day and cost more than the catalog itself.",
            "Table optimizers on a busy streaming table can run almost continuously; the cost shows up as Glue DPU hours, not as catalog charges.",
            "Upkeep is billed twice if Databricks and AWS both maintain tables: AWS optimizers on one bill, Databricks compute on the other.",
            "Keeping a full second registration in Glue for every Unity Catalog table adds objects, requests and confusion for no reader that needs it.",
        ],
    },
    "security": [
        "Access to the catalog itself is IAM permissions on glue actions such as GetTable and GetPartitions. Access to the data is a separate S3 permission, unless Lake Formation is in charge.",
        "If Lake Formation is switched on for a database, it decides who sees which tables, columns and rows, and it hands engines short-lived credentials. On this platform, make no new Lake Formation grants.",
        "Encrypt catalog metadata with a KMS key you own through the Data Catalog encryption settings; connection passwords are encrypted too.",
        "Reach the Glue API through a VPC interface endpoint so jobs and Databricks clusters never call it over the internet.",
        "CloudTrail records every catalog call, including who changed a table definition. Keep these events for audit alongside Databricks audit system tables.",
        "Table names, column names and comments can reveal personal or secret information, such as a column called customer_aadhaar. Name and describe columns with that in mind.",
    ],
    "monitor": [
        ("Table optimizer run history", "Each compaction, retention and orphan deletion run, its status and the files it touched; a long gap or repeated failure means the table is not being tidied."),
        ("CloudWatch metrics for table optimizers", "Bytes and files compacted, and DPU hours used; a sudden rise points to a writer producing tiny files."),
        ("Glue crawler last run status and tables changed", "A crawler that changed a schema or created unexpected tables needs a human look."),
        ("CloudTrail events UpdateTable, DeleteTable and CreateTable", "Who changed or dropped a table and when; alert on changes to production databases."),
        ("Partition and table version counts", "Compare against the quotas before a busy table hits a hard stop."),
        ("Unity Catalog foreign catalog query errors", "Federated reads from Databricks failing usually means a permission or network change on the Glue side."),
    ],
    "limits": [
        ("Databases", "10,000 per catalog and 10,000 per account (adjustable)"),
        ("Tables", "200,000 per database and 1,000,000 per account (adjustable)"),
        ("Partitions", "10,000,000 per table and 20,000,000 per account (adjustable)"),
        ("Table versions", "100,000 per table and 1,000,000 per account (adjustable)"),
        ("Table optimizers", "Apache Iceberg tables only; compaction strategies are binpack, sort and Z-order"),
    ],
    "decisions": [
        ("Three hundred Glue tables behind existing Athena reports, moving to Databricks",
         "Federate Unity Catalog to Glue and read them in place; rebuild as Unity Catalog managed tables one domain at a time",
         "Keep if you have it: no copies, no new Glue tables, and a date for each domain to leave Glue."),
        ("New gold tables that Athena and Redshift must read",
         "Unity Catalog managed Delta with Iceberg reads (UniForm), read through the Iceberg REST catalog or Glue federation to Unity Catalog",
         "Pursue: one owner, many readers, no second registration with write rights."),
        ("A logistics team runs Firehose, Glue jobs and Athena with no Databricks",
         "Glue Iceberg tables with table optimizers on, or S3 Tables",
         "Pursue: right tool for an AWS-only corner; read it from Databricks through federation if needed."),
        ("Register every Databricks table in Glue too, just in case",
         "A full second catalog kept in step by scripts",
         "Drop: two owners for one path, double permissions and drift with no reader that needs it."),
        ("Crawlers as the permanent schema source for silver tables",
         "Hourly crawlers updating production tables",
         "Drop: schemas belong in code and contracts; use crawlers only to bootstrap landing."),
    ],
    "faq": [
        ("Is the Glue Data Catalog the same as AWS Glue?",
         "No. AWS Glue is a family: the Data Catalog, crawlers, ETL jobs, Data Quality and more. The Data Catalog is the metadata store that the others, and Athena, EMR and Redshift, all share. You can use it without running a single Glue ETL job."),
        ("Can Databricks use the Glue Data Catalog?",
         "Yes, in two ways. The recommended one is catalog federation, where Unity Catalog shows Glue tables as foreign tables and governs who reads them. The older way, pointing a cluster's metastore at Glue directly, bypasses Unity Catalog governance and should not be used for new work."),
        ("Do Glue table optimizers work on Delta Lake tables?",
         "No. They work on Apache Iceberg tables that Glue owns. Delta tables managed by Unity Catalog are tidied by Databricks Predictive Optimization; external Delta tables need your own OPTIMIZE and VACUUM jobs."),
        ("Can Athena query Unity Catalog tables without copying them?",
         "Yes. Turn on Iceberg reads (UniForm) for the Delta tables Athena needs and read them through Unity Catalog's Iceberg REST catalog, or set up Glue catalog federation to Unity Catalog, which AWS documents for reads. Either way the files stay where they are."),
        ("Should we migrate everything out of Glue on day one?",
         "No. Read existing tables in place through federation, move one domain at a time, and stop creating new tables in Glue. Retire each Glue database only after its last reader has moved."),
    ],
    "sources": [
        ("AWS docs: Optimizing Iceberg tables (Glue table optimizers)", "https://docs.aws.amazon.com/glue/latest/dg/table-optimizers.html"),
        ("AWS docs: AWS Glue endpoints and quotas", "https://docs.aws.amazon.com/general/latest/gr/glue.html"),
        ("AWS docs: What is AWS Lake Formation (federated catalogs, S3 Tables integration)", "https://docs.aws.amazon.com/lake-formation/latest/dg/what-is-lake-formation.html"),
        ("AWS: Glue catalog federation for remote Apache Iceberg catalogs", "https://aws.amazon.com/about-aws/whats-new/2025/11/aws-glue-catalog-federation-remote-apache-iceberg-catalogs"),
        ("AWS Big Data Blog: Access Unity Catalog data using catalog federation in the Glue Data Catalog", "https://aws.amazon.com/blogs/big-data/access-databricks-unity-catalog-data-using-catalog-federation-in-the-aws-glue-data-catalog"),
    ],
    "related": [
        ("Who maintains your tables", "/learn/table-maintenance/"),
        ("Delta Lake vs Apache Iceberg", "/learn/delta-vs-iceberg/"),
        ("Data platform on AWS and Databricks", "/learn/data-platform-architecture/aws-databricks/"),
        ("AWS Lake Formation", "svc:lake-formation"),
        ("Amazon S3 Tables", "svc:s3-tables"),
        ("Amazon Athena", "svc:athena"),
    ],
}
