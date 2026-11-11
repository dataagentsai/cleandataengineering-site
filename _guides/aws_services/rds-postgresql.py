SERVICE = {
    "slug": "rds-postgresql",
    "name": "Amazon RDS for PostgreSQL",
    "short": "RDS PostgreSQL",
    "group": "operational",
    "one_line": "Community PostgreSQL on a managed server AWS patches and backs up; a common DMS source, dropped as this platform's metadata store.",
    "status": "Generally available. PostgreSQL 18 has been available since Nov 2025. PostgreSQL 13 left standard support on 28 Feb 2026 and is billed for Extended Support; PostgreSQL 14 follows on 28 Feb 2027.",
    "checked": "2026-11-11",
    "site_verdict": ("Keep if you have it",
                     "Keep it as a source: MES, quality and ordering systems on RDS PostgreSQL are read by DMS with change capture into S3 landing. "
                     "Drop it as the platform's metadata database: it has the same drawback as Aurora, one more AWS service to run, connect and back "
                     "up, with no gain over Lakebase."),
    "equivalents": {"azure": "Azure Database for PostgreSQL flexible server",
                    "gcp": "Cloud SQL for PostgreSQL",
                    "databricks": "Lakebase (Databricks managed PostgreSQL)",
                    "open_source": "PostgreSQL"},
    "plain": [
        "Amazon RDS for PostgreSQL is ordinary PostgreSQL, the open-source relational database, running on a server that AWS manages. RDS stands "
        "for Relational Database Service. You pick an instance size, such as two virtual CPUs and 8 GiB of memory, and a storage volume, and AWS "
        "installs PostgreSQL, applies patches in a maintenance window you choose, takes daily backups and keeps transaction logs so you can "
        "restore to any second within your retention period.",
        "Unlike Aurora, the storage is a normal block volume attached to one instance. For high availability you turn on Multi-AZ, which keeps "
        "a standby copy in another Availability Zone and fails over to it, usually within a minute or two. A newer Multi-AZ cluster option "
        "uses two readable standbys and fails over faster. Because it is community PostgreSQL, almost every extension and tool works the same "
        "way it does on your laptop.",
        "A retail example: a regional chain runs its loyalty programme on RDS for PostgreSQL. It holds members, points balances and redemptions, "
        "and the loyalty app writes to it all day. The data platform needs those tables for customer analytics. It does not query the loyalty "
        "database during the day. DMS copies the tables once and then reads the change log, landing changes in S3, and Databricks builds bronze "
        "and silver from them, with names and emails masked by Unity Catalog policies.",
    ],
    "analogy": "A rented flat where the landlord fixes the boiler and keeps spare keys; you still choose the size and pay rent whether you are home or not.",
    "big_picture": [
        "On the reference platform RDS for PostgreSQL is mainly a source. Operational systems such as MES, quality, loyalty and ordering run on "
        "it, owned by application teams. The ingestion pattern is DMS: a full load followed by ongoing change data capture into the S3 landing "
        "area, using PostgreSQL logical replication. Small reference tables without change capture can instead be pulled by the platform's own "
        "puller job in Databricks. Occasional exploratory queries can use Lakehouse Federation from Databricks without copying.",
        "It was also on the list for the metadata database, the relational store that declares sources, datasets, rules and owners and holds "
        "watermarks and the run log. RDS was marked Drop for that role. It is cheaper and simpler than Aurora, with slower failover and no "
        "automatic scaling, but it has the same drawback: one more AWS service to run, connect privately and back up. Lakebase, a managed "
        "PostgreSQL inside Databricks, was chosen on 4 Nov.",
        "It should not become a live store for the fast lane either. Exposing an RDS table through Lakehouse Federation while the live app reads "
        "it directly was marked Drop on the real-time mode page: governance on paper only.",
    ],
    "upstream": ["Applications (loyalty, ordering, MES)"],
    "downstream": ["svc:dms", "Databricks Lakehouse Federation (read-only queries)", "svc:zero-etl"],
    "concepts": [
        ("DB instance", "One managed server running PostgreSQL, with a size you choose and pay for by the hour whether busy or idle."),
        ("Multi-AZ", "A synchronous standby in another Availability Zone that takes over if the primary fails; the standby serves no reads in the classic option."),
        ("Read replica", "An asynchronous copy that serves reads, in the same or another Region; it can lag behind the primary."),
        ("Parameter group", "The set of PostgreSQL settings for an instance, such as rds.logical_replication, which DMS change capture needs turned on."),
        ("Logical replication", "PostgreSQL's way of publishing row changes from its write-ahead log so tools like DMS can stream inserts, updates and deletes."),
        ("Replication slot", "A marker that holds write-ahead log until the consumer has read it; if the consumer stops, log files pile up and fill the disk."),
        ("Extended Support", "Paid patching for a major version after its end of standard support, charged per vCPU-hour and rising in year three."),
        ("Blue/green deployment", "A managed copy kept in sync with production, used to test a major upgrade and switch over in about a minute."),
    ],
    "use_when": [
        "An application needs community PostgreSQL with managed patching and backups, and the load is small and steady.",
        "A source system already runs on it; read it with DMS change capture and leave it alone.",
        "You need a specific PostgreSQL extension or version that Aurora does not yet offer.",
        "Cost matters more than very fast failover, and a minute or two of failover is acceptable.",
    ],
    "avoid_when": [
        "It would be a new metadata database for this platform; Lakebase was chosen and RDS was marked Drop.",
        "You need many readers sharing one storage copy, or storage that grows on its own past 64 TiB; use Aurora.",
        "The workload is analytics over millions of rows; that belongs on Delta tables and a SQL warehouse.",
        "Load is idle most of the day; a provisioned instance bills every hour, while Aurora Serverless v2 can pause.",
        "It would hold the fast lane's live values behind Lakehouse Federation; the site marks that Drop.",
    ],
    "challenges": [
        ("Disk filled by a stalled slot", "A DMS task stops but its replication slot stays; write-ahead log grows until the volume fills and the database stops writing.",
         "Alarm on OldestReplicationSlotLag and TransactionLogsDiskUsage, turn on storage autoscaling with a maximum, and drop slots of retired tasks."),
        ("CDC not enabled", "DMS cannot capture changes because rds.logical_replication is off or tables lack primary keys.",
         "Set the parameter in a custom parameter group and reboot in a window; agree primary keys with the application team."),
        ("Extended Support bill", "An instance on PostgreSQL 13 moved into Extended Support on 1 Mar 2026 and the bill rose with no change in use.",
         "Track the release calendar and upgrade with blue/green deployments; PostgreSQL 14 enters Extended Support on 1 Mar 2027."),
        ("Heavy reads from the platform", "Analysts query the live database directly through Federation or a BI tool and slow the application.",
         "Read through DMS into S3 instead, or point federated queries at a read replica."),
        ("Burstable instance throttles", "A db.t-class instance runs out of CPU credits during a big DMS full load and crawls.",
         "Use a general-purpose instance for production sources, or schedule the full load out of hours."),
        ("Failover drops the CDC slot position", "After a Multi-AZ failover, logical replication slots may need to be recreated depending on version, and DMS needs a restart.",
         "Use versions that sync slots to the standby where available, and test DMS behaviour after a forced failover."),
        ("Storage cannot shrink", "A volume grown for a one-off load stays at that size and keeps billing.",
         "Size storage autoscaling with a sensible maximum; shrinking needs a dump and restore or blue/green to a smaller volume."),
    ],
    "compare": [
        ("Amazon Aurora PostgreSQL", "You need faster failover, up to 15 readers on shared storage, storage beyond 64 TiB or a database that pauses when idle.",
         "A small, steady database is enough and you want the lowest cost."),
        ("Lakebase (Databricks managed PostgreSQL)", "The database is for the platform itself, such as metadata, or a live store that must be in Unity Catalog.",
         "The database belongs to an application team running on AWS."),
        ("Self-managed PostgreSQL on EC2", "You need superuser access, unusual extensions or settings RDS does not allow.",
         "You want patching, backups and failover done for you."),
        ("Azure Database for PostgreSQL flexible server", "You are running the same workload on Azure.", "You are on AWS."),
        ("Google Cloud SQL for PostgreSQL", "You are running the same workload on Google Cloud.", "You are on AWS."),
    ],
    "cost": {
        "model": "You pay per instance-hour by instance class, doubled for a Multi-AZ standby, plus storage per GB-month by type (gp3 or io2) and any "
                 "provisioned IOPS or throughput above the baseline. Backup storage up to the database's size is included; beyond that it bills "
                 "per GB-month. Read replicas bill as separate instances. Extended Support adds a charge per vCPU-hour for major versions past "
                 "their end of standard support. Reserved instances and Database Savings Plans lower the hourly rate for steady use. List prices, "
                 "check your region.",
        "drivers": [
            "Instance class and whether Multi-AZ doubles it.",
            "Allocated storage and provisioned IOPS.",
            "Number of read replicas.",
            "Backup retention and manual snapshots.",
            "Extended Support for old major versions.",
        ],
        "traps": [
            "Extended Support charges for PostgreSQL 11, 12 and 13 instances nobody upgraded.",
            "Storage that autoscaled during a full load and never shrinks.",
            "A read replica created for one report and forgotten.",
            "Manual snapshots kept forever, billed per GB-month.",
        ],
    },
    "security": [
        "Keep instances in private subnets with public access off, and allow only the DMS replication instance's and the application's security groups.",
        "Encrypt storage with a KMS key at creation; an unencrypted instance needs a snapshot copy and restore to encrypt.",
        "Store the DMS user's credentials in Secrets Manager with rotation, or use IAM database authentication; grant only replication and SELECT rights.",
        "Force TLS with rds.force_ssl and use the current RDS certificate authority bundle.",
        "Enable pgAudit or log_statement settings for tables with personal data, and send logs to CloudWatch Logs.",
        "Mask personal data on the platform side with Unity Catalog policies after it lands; the source owner keeps responsibility for the source.",
    ],
    "monitor": [
        ("OldestReplicationSlotLag", "Write-ahead log held by the slowest slot; rising values mean DMS has stalled."),
        ("TransactionLogsDiskUsage", "Disk used by write-ahead log; watch it next to FreeStorageSpace."),
        ("FreeStorageSpace", "Space left on the volume; a full volume stops all writes."),
        ("CPUUtilization", "Instance CPU; sustained high values during DMS full loads mean the instance is too small."),
        ("DatabaseConnections", "Open connections against max_connections."),
        ("ReplicaLag", "Seconds a read replica trails the primary."),
    ],
    "limits": [
        ("Storage per instance", "Up to 64 TiB"),
        ("Read replicas", "Up to 15 per source instance"),
        ("DB instances per Region", "40 by default (20 in Mumbai, ap-south-1), shared with Aurora, adjustable"),
        ("Total storage per Region", "100,000 GB across all RDS instances by default, adjustable"),
        ("max_connections default", "Computed from memory, capped at 5,000 by default"),
    ],
    "decisions": [
        ("Metadata database for the platform", "RDS for PostgreSQL on a small instance",
         "Drop: same drawback as Aurora, one more AWS service, no gain over Lakebase."),
        ("Loyalty database on RDS PostgreSQL 16", "DMS full load plus CDC into S3 landing",
         "Keep if you have it: the standard path; watch slot lag and free storage."),
        ("Source still on PostgreSQL 13", "Upgrade to 17 with a blue/green deployment",
         "Pursue: it is already paying Extended Support; recreate DMS slots after switchover."),
        ("Analysts want to query the source directly", "Lakehouse Federation against a read replica",
         "Pursue with care: fine for occasional checks; regular use belongs on bronze and silver."),
    ],
    "faq": [
        ("Is RDS for PostgreSQL the same as Aurora PostgreSQL?",
         "No. Both run PostgreSQL for the application, but RDS uses a normal volume on one instance while Aurora uses shared, self-healing storage across three zones. Aurora fails over faster and scales reads further; RDS is cheaper and simpler."),
        ("When does PostgreSQL 14 on RDS leave standard support?",
         "On 28 Feb 2027, per the RDS release calendar. From 1 Mar 2027 it is billed for Extended Support until 28 Feb 2030. PostgreSQL 13 already moved on 1 Mar 2026."),
        ("How do I get RDS PostgreSQL data into Databricks?",
         "Use DMS for a full load and change capture into S3 landing, then build bronze and silver in Databricks. For small tables without change capture, a scheduled pull job works, and Lakehouse Federation suits occasional queries."),
        ("Why not use RDS PostgreSQL for the metadata store?",
         "It would work, but it adds an AWS service to run, connect privately and back up. Lakebase gives the same PostgreSQL inside Databricks, governed by Unity Catalog."),
    ],
    "sources": [
        ("AWS docs: Release calendar for RDS for PostgreSQL", "https://docs.aws.amazon.com/AmazonRDS/latest/PostgreSQLReleaseNotes/postgresql-release-calendar.html"),
        ("AWS docs: Quotas and constraints for Amazon RDS", "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Limits.html"),
        ("AWS docs: Amazon RDS DB instance storage", "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html"),
        ("AWS docs: Using Amazon RDS Extended Support", "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/extended-support.html"),
        ("AWS pricing: Amazon RDS for PostgreSQL", "https://aws.amazon.com/rds/postgresql/pricing/"),
    ],
    "related": [
        ("Metadata store", "/learn/data-platform-architecture/metadata-store/"),
        ("Ingestion", "/learn/data-platform-architecture/ingestion/"),
        ("AWS DMS", "svc:dms"),
        ("Amazon Aurora PostgreSQL", "svc:aurora-postgresql"),
        ("SCD2 with Auto CDC vs PySpark", "/learn/scd2-auto-cdc-vs-pyspark/"),
    ],
}
