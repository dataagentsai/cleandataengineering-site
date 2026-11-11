SERVICE = {
    "slug": "timestream",
    "name": "Amazon Timestream (LiveAnalytics and for InfluxDB)",
    "short": "Timestream",
    "group": "operational",
    "one_line": "AWS's time-series databases: LiveAnalytics, closed to new customers, and managed InfluxDB 2 and 3; dropped as the live store here.",
    "status": "Timestream for LiveAnalytics: closed to new customers since 20 Jun 2025; existing customers continue. Timestream for InfluxDB: generally available, with InfluxDB 3 Core and Enterprise since Oct 2025 and Enterprise clusters of up to 15 nodes since Mar 2026.",
    "checked": "2026-11-11",
    "site_verdict": ("Drop",
                     "LiveAnalytics is closed to new customers, so it is not an option. Timestream for InfluxDB works, but it means instances to size and "
                     "Influx skills to learn, while DynamoDB already holds the live board's latest values and 48-hour chart for about $50 a month, and "
                     "history lives in Delta tables. Revisit only if the team already runs InfluxDB."),
    "equivalents": {"azure": "Azure Data Explorer, or Eventhouse in Microsoft Fabric",
                    "gcp": "Bigtable for time-keyed data, or BigQuery",
                    "databricks": "Delta tables with liquid clustering on time and device; Lakebase for latest values",
                    "open_source": "InfluxDB, TimescaleDB, QuestDB, Prometheus for metrics"},
    "plain": [
        "A time-series database stores measurements stamped with a time, such as a temperature every second from each press, and is built to "
        "answer questions like the average per minute over the last hour, or the latest value for each sensor. It writes very fast, compresses "
        "repeated readings well, and has functions for time windows, gaps and interpolation.",
        "Amazon Timestream is the name for two different products. Timestream for LiveAnalytics is AWS's own serverless engine with a memory "
        "tier for recent data and a magnetic tier for history. AWS closed it to new customers on 20 Jun 2025. Existing customers can keep using "
        "it and add users and accounts under the same payer account, but a new platform cannot sign up. Timestream for InfluxDB is AWS running "
        "the open-source InfluxDB engine for you. It offers InfluxDB 2, a single instance or a Multi-AZ pair, and InfluxDB 3, built on Apache "
        "Arrow and Parquet files in S3, in a Core edition for recent data and an Enterprise edition with clusters, compaction and long history.",
        "A manufacturing example: a mixing line has 40 sensors, each sending a reading every second. Engineers want a chart of the last six hours "
        "and alerts when viscosity drifts. A time-series database would hold those readings and answer the chart query in milliseconds. On this "
        "platform, though, the same need is already covered: the live board's chart comes from DynamoDB, and the long history from silver and "
        "gold Delta tables in Databricks.",
    ],
    "analogy": "A lab notebook with a page per sensor and a line per second, indexed by the clock, instead of a filing cabinet indexed by customer.",
    "big_picture": [
        "Timestream appears in one place on the site: the comparison of live stores for the streaming design's fast lane. That lane takes plant "
        "readings from Kinesis through Managed Flink and must put the latest state and a 48-hour chart on screens within seconds. DynamoDB won "
        "that comparison, with Lakebase as the alternative. Timestream for LiveAnalytics was marked Drop because it is closed. Timestream for "
        "InfluxDB was marked Drop unless the team already knows Influx, because it brings instances to size and new skills for a job DynamoDB "
        "already does.",
        "History is a separate question, and the answer there is the lakehouse. Every reading lands in bronze through the platform lane, is "
        "cleaned into silver and summarised into gold. Delta tables clustered on time and device answer historical questions at much lower "
        "storage cost and stay governed in Unity Catalog. A time-series database would be a second copy of that history to secure and pay for.",
        "If a platform already runs Timestream for LiveAnalytics, the plan is migration, not growth. AWS recommends InfluxDB 3 Enterprise for "
        "most LiveAnalytics workloads and InfluxDB 2 for small, low-latency monitoring. On this platform the simpler path is usually to move "
        "the live part to DynamoDB and the history to Delta tables.",
    ],
    "upstream": ["svc:managed-flink", "svc:iot-core", "Telegraf or InfluxDB agents"],
    "downstream": ["svc:managed-grafana", "Custom dashboards and apps"],
    "concepts": [
        ("Time series", "A sequence of readings from one source over time, such as press 17's temperature, identified by its tags."),
        ("Measurement and tags", "In InfluxDB, a measurement is like a table; tags are indexed labels such as plant and press; fields are the readings themselves."),
        ("Cardinality", "The number of distinct series, meaning distinct tag combinations. High cardinality, such as one series per tyre serial number, strains InfluxDB 2."),
        ("Retention period", "How long data is kept before it is deleted automatically, such as 30 days of one-second readings."),
        ("Downsampling", "Rolling raw readings up into coarser ones, such as one-minute averages, to keep history small."),
        ("Memory and magnetic store", "LiveAnalytics' two tiers: a fast tier for recent writes and a cheaper tier for history, moved by retention settings."),
        ("InfluxDB 3 Core and Enterprise", "Core is a single node aimed at recent data with no compaction; Enterprise adds clusters of up to 15 nodes, read replicas, compaction and long history."),
        ("Flux, InfluxQL and SQL", "Query languages: InfluxDB 2 uses Flux and InfluxQL; InfluxDB 3 uses SQL and InfluxQL, not Flux."),
    ],
    "use_when": [
        "You already run Timestream for LiveAnalytics; keep it working and plan a migration, since it will not take new customers.",
        "The team already runs InfluxDB and its tools, such as Telegraf agents and Grafana dashboards, and wants AWS to manage the servers.",
        "Engineers need fast ad hoc time-window queries on recent readings that DynamoDB's key lookups cannot answer and ClickHouse is not an option.",
        "An operations team monitors equipment health metrics outside the data platform and wants a familiar time-series engine.",
    ],
    "avoid_when": [
        "You are a new customer looking at Timestream for LiveAnalytics; it is closed to you.",
        "The need is a live board with latest values and a 48-hour chart; DynamoDB does that for about $50 a month.",
        "The need is long history and analytics; Delta tables in Unity Catalog are cheaper and governed.",
        "Nobody on the team knows Influx; Flux, InfluxQL and InfluxDB 3 SQL each have their own habits.",
        "Ingest will exceed about 1 million records a second on one cluster; AWS says InfluxDB 3 Enterprise would then need sharding across clusters.",
    ],
    "challenges": [
        ("Closed service", "A design document still lists Timestream for LiveAnalytics; a new account cannot create it.",
         "Remove it from options. Existing users should follow AWS's migration guide to InfluxDB, or move live data to DynamoDB and history to Delta."),
        ("Cardinality blow-up", "Someone tags readings with a batch id or tyre serial, the number of series explodes and InfluxDB 2 slows down or runs out of memory.",
         "Keep identifiers with many values as fields, not tags. Use InfluxDB 3 if very high cardinality is truly needed."),
        ("Core used for history", "A team keeps months of data in InfluxDB 3 Core, which has no compaction, and queries get slower over time.",
         "Use Core only for recent data, typically a few days; use Enterprise for longer history, or keep history in Delta."),
        ("Query dialect surprises", "Queries written for LiveAnalytics or Flux do not run unchanged on InfluxDB 3.",
         "Test every business-critical query on a development instance before migrating, as AWS's guide advises."),
        ("Sizing instances", "Timestream for InfluxDB bills instances and storage like a database server, and an undersized instance drops writes at peak.",
         "Load-test at peak write rate with realistic tags; watch CPU and memory; size for the morning shift change, not the average."),
        ("A second copy of history", "Readings are kept both in the time-series database and in Delta tables, doubling storage and access reviews.",
         "Set a short retention period in the time-series store and treat Delta as the record."),
    ],
    "compare": [
        ("Amazon DynamoDB", "You need latest values and a fixed 48-hour chart with change push; the site's choice.",
         "Engineers need ad hoc time-window queries over many series."),
        ("Lakebase (Databricks managed PostgreSQL)", "You want SQL over recent values inside Unity Catalog and one fewer AWS service.",
         "You need push of changes or very high write rates."),
        ("ClickHouse Cloud", "Live screens need ad hoc slicing over 48 hours across many dimensions.",
         "You only need latest values; it adds a vendor."),
        ("Delta tables on Databricks", "The question is history and analytics: trends, yield, scrap and maintenance models.",
         "You need sub-second answers on the last few seconds of data."),
        ("Azure Data Explorer or Fabric Eventhouse", "You are on Azure and want a time-series and log analytics engine.", "You are on AWS."),
        ("Self-managed InfluxDB or TimescaleDB", "You need versions or settings the managed service lacks and can run servers.",
         "You want backups, patching and failover handled for you."),
    ],
    "cost": {
        "model": "Timestream for InfluxDB bills like a database server: per instance-hour by instance size, per GB-month of storage, and for "
                 "Multi-AZ standbys or extra cluster nodes. InfluxDB 3 keeps data as Parquet in S3-backed storage, and Enterprise is billed per "
                 "node in the cluster. Timestream for LiveAnalytics, for existing customers only, bills for writes, memory-store and "
                 "magnetic-store storage, and query compute. The site estimates Timestream for InfluxDB at about $100 or more a month for a small "
                 "live store; list prices, check your region.",
        "drivers": [
            "Instance size and count, which must cover peak write rate.",
            "Retention period and raw resolution, which set storage.",
            "Edition: Enterprise clusters cost more than a single Core node.",
            "Multi-AZ or read replicas for availability.",
        ],
        "traps": [
            "Running a time-series store and Delta history side by side pays twice for the same readings.",
            "Instances sized for the peak stay on all month.",
            "High-cardinality tags force a bigger instance than the data volume suggests.",
            "Long retention of one-second readings when one-minute averages would do.",
        ],
    },
    "security": [
        "Deploy Timestream for InfluxDB instances in private subnets with no public access, and limit inbound traffic to named security groups.",
        "Encryption at rest is on; use a customer managed KMS key if your policy requires it, and require TLS from clients.",
        "Store the InfluxDB admin token and user credentials in Secrets Manager; do not share one all-powerful token across jobs.",
        "Use IAM policies for the AWS control plane and InfluxDB's own users and tokens for data access; review both.",
        "CloudTrail records management calls; sensor readings rarely hold personal data, but operator ids attached as tags would, so keep them out.",
    ],
    "monitor": [
        ("CPUUtilization", "Instance CPU for Timestream for InfluxDB; sustained high values mean writes or queries will slow."),
        ("MemoryUtilization", "Memory used; InfluxDB 2 memory grows with cardinality."),
        ("DiskUtilization", "Storage used against what is allocated; a full disk stops writes."),
        ("Write errors in clients", "Rejected or timed-out writes reported by Flink or Telegraf; the first sign of an undersized instance."),
        ("Series cardinality", "Distinct series count from InfluxDB's own statistics; alarm on sudden jumps."),
    ],
    "limits": [
        ("LiveAnalytics availability", "Closed to new customers since 20 Jun 2025"),
        ("InfluxDB 3 Enterprise cluster", "Up to 15 nodes"),
        ("InfluxDB 3 Core", "Single node; best for data a few days old"),
        ("Ingest per InfluxDB 3 cluster", "Not more than about 1 million records per second, per AWS guidance"),
        ("InfluxDB 2 cardinality guidance", "Under about 10 million series"),
    ],
    "decisions": [
        ("New live store for 120 presses", "Timestream for LiveAnalytics",
         "Drop: closed to new customers since 20 Jun 2025."),
        ("New live store, team has no Influx experience", "Timestream for InfluxDB",
         "Drop: instances to size and new skills for a job DynamoDB already does."),
        ("Plant maintenance team already runs InfluxDB and Grafana on servers", "Move to Timestream for InfluxDB",
         "Keep if you have it: managed servers for an existing tool, outside the data platform; keep history in Delta."),
        ("Existing LiveAnalytics tables feeding a dashboard", "Migrate the live part to DynamoDB and history to Delta, or to InfluxDB 3 Enterprise",
         "Pursue with care: test every query; the SQL dialects differ."),
    ],
    "faq": [
        ("Is Amazon Timestream being discontinued?",
         "Timestream for LiveAnalytics closed to new customers on 20 Jun 2025; existing customers keep running and AWS still maintains it. Timestream for InfluxDB is open and growing, with InfluxDB 3 added in Oct 2025."),
        ("What should I use instead of Timestream for LiveAnalytics?",
         "AWS recommends Timestream for InfluxDB 3 Enterprise for most workloads, and InfluxDB 2 for small, low-latency monitoring. On this platform, DynamoDB serves live values and Delta tables hold history."),
        ("Is InfluxDB 3 SQL the same as Timestream SQL?",
         "No. InfluxDB 3 supports standard SQL through Apache DataFusion and InfluxQL, but AWS states the dialect does not match LiveAnalytics one to one. Test queries before moving."),
        ("Can Databricks read Timestream?",
         "Not natively as a governed source. Export data to S3 or write the same stream into bronze through the platform lane, which this design already does."),
    ],
    "sources": [
        ("AWS docs: Timestream for LiveAnalytics availability change", "https://docs.aws.amazon.com/timestream/latest/developerguide/AmazonTimestreamForLiveAnalytics-availability-change.html"),
        ("AWS docs: Alternatives and migration guidance", "https://docs.aws.amazon.com/timestream/latest/developerguide/timestream-availability-update.html"),
        ("AWS docs: Core and Enterprise versions in Timestream for InfluxDB 3", "https://docs.aws.amazon.com/timestream/latest/developerguide/core-and-enterprise-versions.html"),
        ("AWS What's New: Timestream supports InfluxDB 3 (Oct 2025)", "https://aws.amazon.com/about-aws/whats-new/2025/10/amazon-timestream-influxdb-3"),
        ("AWS What's New: InfluxDB 3 expanded multi-node clusters (Mar 2026)", "https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-timestream-for-influxdb-3-multi-node-cluster"),
    ],
    "related": [
        ("Streaming on AWS and Databricks", "/learn/streaming/"),
        ("Real-time analytics", "/learn/real-time-analytics/"),
        ("Amazon DynamoDB", "svc:dynamodb"),
        ("AWS IoT Events and IoT Analytics", "svc:iot-events-analytics"),
        ("Amazon Managed Grafana", "svc:managed-grafana"),
    ],
}
