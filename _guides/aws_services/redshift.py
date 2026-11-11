SERVICE = {
    "slug": "redshift",
    "name": "Amazon Redshift (provisioned, Serverless, data sharing)",
    "short": "Redshift",
    "group": "serving",
    "one_line": "AWS's managed SQL data warehouse, as clusters or Serverless; on this platform kept for existing BI while new work moves to Databricks SQL.",
    "status": "Generally available. DC2 nodes are no longer available (docs removed 2 Nov 2026); RA3 and the new Graviton-based RG nodes (since May 2026) remain. Python UDFs reached end of support after 30 Jun 2026.",
    "checked": "2026-11-11",
    "site_verdict": ("Keep if you have it",
                     "If Redshift already serves many reports, keep it and let it read our tables as Iceberg through UniForm, "
                     "or receive them through Delta Sharing, while reports move. Put new gold tables and new BI on the Databricks SQL warehouse, "
                     "and shut the cluster down when the last report has moved."),
    "equivalents": {"azure": "Fabric Data Warehouse, or Synapse dedicated SQL pool",
                    "gcp": "BigQuery",
                    "databricks": "Databricks SQL warehouse (serverless) on Delta tables in Unity Catalog",
                    "open_source": "No direct match; ClickHouse, Trino over Iceberg, or PostgreSQL with columnar extensions for small cases"},
    "plain": [
        "Amazon Redshift is a data warehouse: a database built for questions that read millions of rows and add them up, such as total sales by "
        "region and month, rather than for saving one order at a time. It stores data by column instead of by row, compresses it heavily, and spreads "
        "every query across many machines working in parallel. People connect to it with SQL from BI tools such as Power BI, Tableau or QuickSight.",
        "It comes in two shapes. A provisioned cluster is a fixed set of nodes, which are servers, that you choose and pay for by the hour; the "
        "current node families are RA3 and the newer RG, both of which keep data in Redshift Managed Storage on S3 and cache hot data on local SSDs. "
        "Redshift Serverless has no nodes to pick: you set a base capacity in RPUs (Redshift Processing Units) and pay per second while queries run.",
        "A retail example: a chain of 400 stores has run Redshift for six years. Every night a job loads point-of-sale lines, stock counts and promotions "
        "from SAP and the store systems. Two hundred reports in Tableau read from it, and the finance team has stored procedures that build the monthly "
        "margin pack. That is a working, valuable system. The question for this platform is not whether Redshift is good. It is whether to keep "
        "feeding it new work now that Databricks holds the governed gold tables.",
        "Redshift can also share data. Data sharing lets one Redshift warehouse read another's tables live, without copying, even across accounts. "
        "Redshift can now read and write Apache Iceberg tables in S3, which is how it reaches Databricks tables on this platform.",
    ],
    "analogy": "A long-established department store with loyal customers; you keep it open while the new mall next door fills up, and you stop stocking new lines there.",
    "big_picture": [
        "Redshift sits in the serving lane beside the Databricks SQL warehouse and Athena. In the reference design Databricks builds bronze, silver and "
        "gold as Delta tables in S3. Redshift is not on the main path. It is kept where it already serves reports, and it reads the gold tables instead of "
        "having its own nightly loads rebuilt.",
        "There are two ways for Redshift to read our tables. The first is UniForm: Databricks writes Iceberg metadata beside each Delta table, the Glue "
        "Data Catalog federates to Unity Catalog, and Redshift queries the tables as external Iceberg tables through a resource link in the default Glue "
        "catalog. The second is Delta Sharing, the open protocol Databricks uses to share tables with other tools; check how your Redshift version and tools "
        "consume it before relying on it. Either way, there is one copy of the data and Databricks owns it.",
        "The migration plan on the reference platform is simple. New gold tables and new dashboards go on Databricks SQL, with Metric Views, Genie and AI/BI. "
        "Existing reports keep running on Redshift, reading from the lake. Reports move one by one. When the last one has moved, the cluster is shut down. "
        "Zero-ETL integrations, which copy Aurora, RDS or DynamoDB into Redshift automatically, are an AWS-native alternative path that this platform does not use.",
    ],
    "upstream": ["Databricks gold tables through UniForm (Iceberg) or Delta Sharing", "svc:glue-data-catalog", "svc:zero-etl"],
    "downstream": ["Existing BI reports (Tableau, Power BI)", "svc:quicksight", "Finance stored procedures and extracts"],
    "concepts": [
        ("Columnar storage", "Each column is stored and compressed on its own, so a query that needs three columns out of eighty reads only those three."),
        ("RA3 and RG nodes", "Current provisioned node types. RA3 is Intel-based; RG is Graviton-based and arrived in May 2026. Both separate compute from Redshift Managed Storage."),
        ("Redshift Managed Storage", "The storage layer behind RA3, RG and Serverless: data lives in S3 and hot blocks are cached locally. Billed per GB-month on its own."),
        ("RPU", "Redshift Processing Unit, the capacity unit of Serverless. You set a base (from 4) and a maximum; billing is per RPU-hour, per second."),
        ("Distribution key and sort key", "Settings that decide which node holds each row and in what order rows are stored; good choices avoid moving data between nodes and let queries skip blocks."),
        ("WLM", "Workload management: queues and priorities that decide which queries run now and which wait. Automatic WLM is the default."),
        ("Concurrency scaling", "Extra temporary capacity that Redshift adds when many queries queue; each cluster earns one free hour a day."),
        ("Data sharing", "Live, read-only access from one Redshift warehouse to another's tables without copying, across accounts and Regions."),
        ("Spectrum", "The feature that queries data in S3 from Redshift. On RA3 it runs on a separate fleet; on RG it runs on the cluster's own nodes."),
    ],
    "use_when": [
        "You already run Redshift with many reports, stored procedures and trained users, and moving them all at once would be risky.",
        "Existing Redshift reports need fresh numbers from the new gold tables, and reading them as Iceberg avoids building a second load pipeline.",
        "A business unit outside the Databricks platform consumes data through Redshift data sharing and cannot change its tools this year.",
        "You need an AWS-only warehouse with no Databricks at all, for example in a small separate account; then Serverless is the simplest start.",
    ],
    "avoid_when": [
        "You are starting new BI on this platform; the Databricks SQL warehouse reads gold directly with Unity Catalog masks, lineage and Genie.",
        "You would have to load the same gold data into Redshift tables every night; that creates a second copy that drifts and costs twice.",
        "You still rely on Python UDFs; they reached end of support after 30 June 2026, so rewrite them as SQL or Lambda UDFs first.",
        "Data access rules live in Unity Catalog; Redshift does not enforce them, so you would maintain grants in two places.",
    ],
    "challenges": [
        ("Two warehouses, two truths",
         "Gold on Databricks and a separately loaded copy in Redshift drift apart; finance and sales report different margins.",
         "Never load gold into Redshift tables; read it as external Iceberg tables or through Delta Sharing, so there is one copy, and track which reports remain."),
        ("Slow external Iceberg queries",
         "Reports that were fast on local tables become slow on lake tables, especially on RG, where lake queries share the cluster's compute.",
         "Compact and cluster the Delta tables, keep UniForm metadata current, add materialized views in Redshift for hot reports, and size the RG cluster for lake load."),
        ("Queueing at month end",
         "Finance closes the month, hundreds of queries arrive, and WLM queues them; dashboards time out.",
         "Use automatic WLM with query priorities, turn on concurrency scaling with a usage limit, or use Serverless with a sensible maximum RPU."),
        ("Bad distribution and sort keys",
         "Large joins shuffle data between nodes and scans read every block; one query takes the cluster down for minutes.",
         "Use AUTO distribution and sort keys, check SVV_TABLE_INFO for skew, and read the Advisor recommendations in the console."),
        ("DC2 and old node migration",
         "Old DC2 clusters can no longer be bought or resized, and reserved nodes for them may not renew.",
         "Move to RA3, RG or Serverless by snapshot restore or elastic resize; test with the Redshift Test Drive tool first."),
        ("Python UDF end of support",
         "Reports that call Python UDFs fail once enforcement reaches the cluster.",
         "Find them in the system catalog and rewrite them as SQL UDFs or Lambda UDFs, or move the logic into Databricks gold."),
        ("Serverless bill creep",
         "A BI tool keeps sessions busy all day, so Serverless never idles and costs more than a small cluster would.",
         "Set a maximum RPU and a usage limit with alerts; compare a month of RPU-hours with a provisioned or reserved cluster."),
        ("Grants in two places",
         "Someone gets access to a column in Redshift that Unity Catalog masks; the governance story breaks.",
         "Expose only non-sensitive or pre-masked gold tables to Redshift through Lake Formation, and audit Redshift grants each quarter."),
    ],
    "compare": [
        ("Databricks SQL warehouse",
         "New BI on this platform: it reads gold in place with Unity Catalog masks, lineage, Metric Views and Genie, and scales serverless.",
         "Hundreds of existing Redshift reports and procedures cannot move yet."),
        ("Amazon Athena",
         "Occasional ad hoc queries on S3 with nothing running in between.",
         "Many users and dashboards that need steady speed."),
        ("Azure Fabric Data Warehouse or Synapse dedicated pool",
         "The company runs on Azure and Power BI with OneLake.",
         "The data and platform are on AWS."),
        ("Google BigQuery",
         "The platform is on GCP and you want fully serverless SQL warehousing.",
         "The data is in S3 and the team runs Databricks."),
        ("Snowflake",
         "The company already standardised on Snowflake for BI and data sharing.",
         "You would add a third warehouse beside Redshift and Databricks SQL."),
        ("ClickHouse",
         "Live screens need sub-second slicing over recent data at high concurrency.",
         "You need a general BI warehouse with mature tools and procedures."),
    ],
    "cost": {
        "model": "Provisioned clusters bill per node-hour by node type, billed per second, plus Redshift Managed Storage per GB-month (0.024 US dollars per GB-month in the AWS example; list price, check your region). "
                 "Reserved nodes for one or three years cut the hourly rate but are charged whether the cluster runs or is paused. "
                 "Serverless bills per RPU-hour, per second, with a 60-second minimum, and includes lake queries; base capacity runs from 4 to 1,024 RPUs. "
                 "Spectrum on RA3 is charged per TB scanned. Concurrency scaling beyond the free daily credit is charged per second. Snapshots beyond the free amount, data transfer and zero-ETL have their own charges.",
        "drivers": [
            "Node count and type, or RPU-hours on Serverless, which follow how long sessions keep the warehouse busy.",
            "Managed storage volume, including tables nobody reads any more.",
            "Concurrency scaling hours beyond the free credits.",
            "Bytes scanned by Spectrum on RA3 when reports read lake tables.",
        ],
        "traps": [
            "Paying for a reserved cluster and Databricks SQL for the same reports during a migration that never finishes.",
            "Loading gold into Redshift tables doubles storage and compute and adds a pipeline to maintain.",
            "Paused clusters still pay for storage and reserved nodes.",
            "Serverless with no maximum RPU or usage limit lets one runaway query or chatty BI tool set the bill.",
        ],
    },
    "security": [
        "Use IAM roles for Redshift to read S3 and Glue, IAM Identity Center or IAM authentication for users, and role-based access control inside the database; avoid shared admin passwords and keep any secrets in Secrets Manager.",
        "Encrypt clusters and Serverless namespaces with a customer-managed KMS key, and require SSL for all connections.",
        "Keep the warehouse private: no public access, a subnet group in private subnets, and Redshift-managed VPC endpoints for other VPCs or accounts.",
        "Turn on audit logging (connection, user and user-activity logs) to CloudWatch or S3; CloudTrail records API calls.",
        "For personal data, expose only masked or non-sensitive gold tables through Lake Formation, and use Redshift dynamic data masking for any local tables that remain.",
    ],
    "monitor": [
        ("WLMQueueLength and QueryDuration", "How many queries wait and how long they run; the first sign of month-end trouble."),
        ("CPUUtilization and PercentageDiskSpaceUsed", "Cluster load and local cache pressure on provisioned nodes."),
        ("ComputeCapacity and ComputeSeconds", "Serverless RPUs in use and RPU-seconds consumed; the cost signal for Serverless."),
        ("ConcurrencyScalingSeconds", "Extra capacity used beyond the free credits."),
        ("SYS_QUERY_HISTORY", "System view with every query, its runtime, queue time and errors; use it to find slow reports and track which ones still run."),
        ("SYS_EXTERNAL_QUERY_DETAIL", "Lake and Iceberg scan details for external tables, to see where reading gold is slow."),
    ],
    "limits": [
        ("RA3 or RG nodes per cluster", "128 (adjustable)"),
        ("Connections per cluster or workgroup", "2,000, hard limit"),
        ("Databases", "60 per cluster, 100 per Serverless namespace"),
        ("Tables per Serverless namespace", "200,000"),
        ("Serverless running query timeout", "24 hours"),
        ("Concurrency scaling clusters", "10 (adjustable)"),
    ],
    "decisions": [
        ("A retailer has 200 Tableau reports on a Redshift RA3 cluster",
         "Keep the cluster; point reports at gold through UniForm Iceberg tables; move reports one by one to Databricks SQL",
         "Keep if you have it: no big-bang migration; one copy of the data; shut down when the last report moves."),
        ("A new plant OEE dashboard",
         "Databricks SQL warehouse with Metric Views and AI/BI",
         "Pursue: new BI goes on Databricks SQL, not Redshift."),
        ("Old DC2 cluster with reserved nodes ending",
         "Snapshot restore to RG or Serverless, after a Test Drive run",
         "Pursue with care: necessary, but only if reports will stay for more than a year; otherwise move them now."),
        ("Load gold into Redshift tables every night to make reports faster",
         "Nightly COPY of gold into local tables",
         "Drop: a second copy that drifts; use materialized views over the Iceberg tables instead."),
    ],
    "faq": [
        ("Can Redshift read Databricks Delta tables?",
         "Yes, through Iceberg. Turn on UniForm so Delta tables also have Iceberg metadata, let the Glue Data Catalog federate to Unity Catalog, and query them in Redshift through a resource link in the default catalog. Delta Sharing is the other route; check tool support first."),
        ("Is Redshift being retired?",
         "No. Redshift is active and gained Graviton RG nodes, Iceberg v3 reads and writes, and Iceberg materialized views in 2026. What is retired is the old DC2 node type and Python UDFs."),
        ("Redshift Serverless or provisioned?",
         "Serverless suits uneven use and small teams because it bills only while queries run. A busy cluster used all day is usually cheaper as provisioned RG or RA3 nodes with reservations. Compare a month of real RPU-hours."),
        ("Should we migrate Redshift to Databricks?",
         "On this platform, yes, gradually. New work goes to Databricks SQL, and existing reports move one by one while Redshift reads from the lake, so nothing is loaded twice."),
        ("What replaces Redshift Python UDFs?",
         "SQL UDFs for simple logic, Lambda UDFs for code, or moving the logic upstream into Databricks gold tables."),
    ],
    "sources": [
        ("AWS docs: Quotas and limits in Amazon Redshift", "https://docs.aws.amazon.com/redshift/latest/mgmt/amazon-redshift-limits.html"),
        ("AWS docs: Considerations for provisioned clusters (RG and RA3)", "https://docs.aws.amazon.com/redshift/latest/mgmt/managing-cluster-considerations.html"),
        ("AWS: Redshift pricing", "https://aws.amazon.com/redshift/pricing/"),
        ("AWS docs: Redshift document history (DC2 no longer available)", "https://docs.aws.amazon.com/redshift/latest/mgmt/document-history.html"),
        ("AWS docs: Querying Glue IRC federated catalogs with Redshift", "https://docs.aws.amazon.com/redshift/latest/dg/glue-irc-federated-catalogs.html"),
        ("AWS What's New: Redshift supports Apache Iceberg v3 tables (Aug 2026)", "https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-redshift-supports-apache-iceberg-v3"),
    ],
    "related": [
        ("AWS and Databricks reference platform", "/learn/data-platform-architecture/aws-databricks/"),
        ("Power BI vs Databricks AI/BI", "/learn/power-bi-vs-databricks-ai-bi/"),
        ("Delta vs Iceberg", "/learn/delta-vs-iceberg/"),
        ("Amazon Athena", "svc:athena"),
        ("Zero-ETL integrations", "svc:zero-etl"),
    ],
}
