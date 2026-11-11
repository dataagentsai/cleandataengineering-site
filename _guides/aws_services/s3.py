SERVICE = {
    "slug": "s3",
    "name": "Amazon S3",
    "short": "S3",
    "group": "storage",
    "one_line": "Object storage that holds every file and table of the platform: landing files, Delta tables, checkpoints, logs and archives.",
    "status": "Generally available. Maximum object size raised from 5 TB to 50 TB in December 2025; default quota of 10,000 general purpose buckets per account",
    "checked": "2026-11-11",
    "site_verdict": ("Pursue",
                     "The floor of the whole platform. Every landing file and every Unity Catalog managed table lives in your own S3 buckets, "
                     "one bucket and one KMS key per catalog, reached only through a VPC endpoint. There is no real alternative on AWS, so the work is in setting it up well."),
    "equivalents": {"azure": "Azure Data Lake Storage Gen2 (Blob Storage with a hierarchical namespace)",
                    "gcp": "Cloud Storage",
                    "databricks": "none: Databricks stores managed tables and volumes in your S3 buckets",
                    "open_source": "MinIO, Ceph (RADOS Gateway) or any S3-compatible store"},
    "plain": [
        "Amazon S3 (Simple Storage Service) stores objects. An object is a file of any kind, from a few bytes to 50 TB, plus a little metadata about it. "
        "Objects live in buckets, which are named containers in one AWS Region. Each object has a key, its full name inside the bucket, such as "
        "landing/sap/orders/2026/11/11/orders_0800.csv. The slashes look like folders, but S3 has no real folders: the key is just a long name, and tools "
        "group keys that share a beginning, called a prefix.",
        "You do not size a disk or plan capacity. You put objects in, read them back over HTTPS with the S3 API, and pay for what you store and how often you touch it. "
        "AWS designs S3 Standard for eleven nines of durability by keeping copies across at least three Availability Zones, which are separate data centres in the Region. "
        "Since December 2020, reads after a write or delete are strongly consistent: once a write succeeds, every reader sees it.",
        "Picture a tyre manufacturer. Every night SAP order extracts arrive as CSV files, DMS drops change files from the plant maintenance database every few minutes, "
        "and curing presses send sensor readings through Kinesis that end up as Parquet files. All of these land in S3. Databricks then reads them and writes Delta tables, "
        "which are also just Parquet files plus a log folder, into other S3 buckets. The finance report that shows scrap cost per plant is, underneath, a few thousand objects in a bucket.",
        "S3 does not understand tables, rows or columns. It only stores and returns whole objects (or byte ranges of them). Everything that makes a table, such as commits, "
        "versions, schemas and permissions on rows, comes from a table format like Delta Lake or Apache Iceberg and from a catalog like Unity Catalog on top.",
    ],
    "analogy": "A vast, numbered warehouse of shelves where you can store any box and fetch it by its label, but the warehouse never opens the boxes or knows what is inside.",
    "big_picture": [
        "S3 sits in the store lane, and almost every arrow on the reference platform touches it. The movers write into a landing bucket per environment: DMS for databases, "
        "AppFlow for SaaS and SAP OData, Transfer Family for supplier SFTP, and Firehose for buffered streams. Files there stay exactly as received, are encrypted with the "
        "environment key, and are deleted 30 days after they reach bronze.",
        "Databricks Auto Loader picks the files up and writes bronze, silver and gold as Unity Catalog managed tables. Each catalog has its own bucket and its own KMS key, so the "
        "recipe catalog or the personal-data vault can be locked down without touching the rest. Unity Catalog reaches the buckets through storage credentials (an IAM role it assumes) "
        "and external locations, and Predictive Optimization does the compaction and VACUUM inside them.",
        "On the way out, Athena and Redshift read the same files as Iceberg through UniForm, so there is one copy and one owner. An audit bucket with Object Lock keeps copies of audit and "
        "config change logs for seven years, and the S3 Cost and Usage Report lands in S3 too. Network access goes through a gateway VPC endpoint, so no data path crosses the public internet.",
    ],
    "upstream": ["svc:dms", "svc:appflow", "svc:data-firehose"],
    "downstream": ["Databricks Auto Loader and Unity Catalog managed tables", "svc:athena", "svc:redshift"],
    "concepts": [
        ("Bucket", "A named container for objects in one Region. Names are global and cannot be changed later, and neither can the Region."),
        ("Object and key", "An object is the stored file plus metadata; the key is its full name in the bucket, slashes included."),
        ("Prefix", "The start of a key, such as landing/sap/. Tools show prefixes as folders, and S3 scales request rates per prefix."),
        ("Storage class", "How an object is stored and billed: Standard, Intelligent-Tiering, the infrequent-access classes and the Glacier archive classes. See the storage classes page."),
        ("Bucket policy", "A JSON document on the bucket that says who may do what, for example deny any request that does not come through our VPC endpoint."),
        ("Block Public Access", "Account and bucket settings that override anything that would make data public. On by default for new buckets."),
        ("SSE-KMS", "Server-side encryption with a KMS key you control. S3 encrypts on write and decrypts on read for callers allowed to use the key."),
        ("Gateway VPC endpoint", "A route that sends S3 traffic from your VPC to S3 over the AWS network, with no internet gateway or NAT. Free of charge."),
        ("Conditional write", "A PUT that succeeds only if the object does not exist yet (If-None-Match). Delta and Iceberg use it so two writers cannot both claim the same commit."),
        ("Lifecycle rule", "A bucket rule that moves objects to a cheaper class or deletes them after a number of days, or expires old versions."),
    ],
    "use_when": [
        "You need a home for raw files from every source, kept exactly as received, so loads can be replayed.",
        "You run Databricks on AWS: managed tables, volumes, checkpoints and job logs all live in S3 buckets you own.",
        "Several engines must read the same data, such as Databricks, Athena, Redshift Spectrum and an outside partner through Delta Sharing.",
        "You must keep data for years at low cost, moving it to cheaper classes as it ages and locking audit copies against deletion.",
        "You want storage that grows from gigabytes to petabytes with no capacity planning and no servers to patch.",
    ],
    "avoid_when": [
        "An application needs millisecond lookups of single rows by key; that is DynamoDB or a database, not files on S3.",
        "A tool expects a real file system with renames, appends and file locks; use Amazon EFS or FSx, or a Unity Catalog volume with care.",
        "Many tiny writes per second land as tiny objects with no compaction; buffer them with Firehose or a stream and write bigger files.",
        "You need single-digit millisecond access to hot objects next to compute; S3 Express One Zone exists for that narrow case.",
    ],
    "challenges": [
        ("Small files", "Streams and frequent micro-batches leave millions of tiny objects. Queries spend their time opening files, and request charges climb.",
         "Write bigger files (Firehose buffering, Auto Loader batch sizes), use managed tables so Predictive Optimization compacts them, and watch average file size per table."),
        ("503 Slow Down errors", "A burst of reads or writes to one prefix exceeds what S3 has scaled to so far, and requests are throttled.",
         "Spread keys across prefixes, let SDK retries with backoff do their job, and avoid a single hot prefix for all writers; S3 scales up gradually."),
        ("KMS throttling and cost", "With SSE-KMS every object read or write can call KMS. Large scans hit the KMS request quota and the KMS bill grows quietly.",
         "Turn on S3 Bucket Keys so S3 asks KMS far less often, and watch ThrottlingException from KMS in CloudTrail and CloudWatch."),
        ("NAT gateway charges", "Clusters in private subnets reach S3 through a NAT gateway because nobody added the endpoint, and every gigabyte pays a processing fee.",
         "Add the S3 gateway VPC endpoint to every route table on day one, and use the bucket policy to deny traffic that does not come through it."),
        ("Two catalogs on one path", "Glue and Unity Catalog both register the same folder and both write. A clean-up job in one deletes files the other still needs.",
         "One owner per path. Unity Catalog external locations must not overlap, and Glue reads Databricks tables only as a guest through federation or UniForm."),
        ("Deleted files are not really gone", "With versioning on, a delete only adds a delete marker; old versions stay and keep costing money, and personal data lingers.",
         "Pair versioning with lifecycle rules that expire noncurrent versions, within 30 days on the platform's table buckets, so erasure is real."),
        ("Accidental public access or wide policies", "A bucket policy with a wildcard principal, or an old ACL, exposes data.",
         "Keep Block Public Access on at account level, disable ACLs (bucket owner enforced), and review findings from IAM Access Analyzer and Macie."),
        ("Cross-Region data transfer", "A workspace in one Region reads a bucket in another; every scan pays inter-Region transfer and runs slower.",
         "Keep buckets and Databricks workspaces in the same Region, and copy on purpose with replication when another Region really needs the data."),
    ],
    "compare": [
        ("Azure Data Lake Storage Gen2", "The platform runs on Azure, and you want a real hierarchical namespace with cheap directory renames.",
         "You are on AWS; S3 now covers the same lakehouse needs, and tables avoid renames anyway."),
        ("Amazon S3 Tables", "An AWS-only team wants Iceberg tables with the catalog and maintenance built in.",
         "Databricks owns the tables; managed tables in general purpose buckets keep one owner and Predictive Optimization."),
        ("Amazon S3 Express One Zone", "A measured hot spot needs single-digit millisecond reads in one Availability Zone.",
         "The data is the long-term copy; one zone is not resilient to losing that zone, and many S3 features are missing."),
        ("Amazon EFS or FSx", "A tool needs a shared POSIX file system with locks and in-place edits.", "The data is analytics files; S3 is far cheaper and every engine reads it."),
        ("MinIO or another S3-compatible store", "Data must stay on premises or at a plant, and tools speak the S3 API.", "You are in AWS anyway; running your own store adds patching and durability work."),
    ],
    "cost": {
        "model": "You pay for storage per GB-month, which depends on the storage class, plus a charge per request (PUT, COPY, POST and LIST cost more than GET), plus data transfer out of the Region "
                 "or to the internet. Transfer into S3 and transfer to compute in the same Region are free. Features add their own lines: replication, Replication Time Control, "
                 "Intelligent-Tiering monitoring, S3 Inventory and Storage Lens advanced metrics. Object Lock costs nothing extra beyond the storage it keeps. SSE-KMS adds KMS request charges on KMS's bill. "
                 "Check the S3 pricing page for your Region; list prices vary by Region.",
        "drivers": [
            "Total stored GB, including old object versions and Delta files that VACUUM has not yet removed.",
            "Request counts, driven mostly by the number and size of files: small files mean many more requests for the same data.",
            "Data transfer across Regions, out to the internet, or through a NAT gateway instead of the free gateway endpoint.",
            "KMS calls when Bucket Keys are off.",
            "Retrieval and minimum-duration charges if lifecycle rules move data into archive classes too early.",
        ],
        "traps": [
            "Noncurrent versions with no expiry rule: the bucket looks small in the console but the bill keeps growing.",
            "Incomplete multipart uploads from failed jobs that sit forever; add a lifecycle rule to abort them after a few days.",
            "LIST-heavy jobs that scan huge prefixes on every run instead of using file notifications or Auto Loader's file events.",
            "S3 traffic through a NAT gateway, paying a per-GB processing fee for traffic that could have been free.",
            "Moving many small objects to an infrequent-access or Glacier class, where each is billed as at least 128 KB plus a minimum duration.",
        ],
    },
    "security": [
        "Access is IAM first: Databricks reaches each bucket through a Unity Catalog storage credential, which is an IAM role with a trust policy for Databricks and an external ID. No user gets direct bucket rights; people get Unity Catalog grants.",
        "Encrypt every bucket with SSE-KMS and a customer managed key, one key per catalog, and turn on Bucket Keys. Restricted catalogs, such as recipes and the personal-data vault, get their own bucket and key.",
        "Keep traffic private: a gateway VPC endpoint for S3, an endpoint policy that allows only the platform's buckets, and bucket policies that deny requests not coming through the endpoint (aws:SourceVpce) or not using TLS.",
        "Keep Block Public Access on at account level and ACLs disabled. Use IAM Access Analyzer to spot buckets shared outside the organisation.",
        "Audit with CloudTrail data events on sensitive buckets (they cost extra, so choose which), and S3 server access logs or CloudTrail for the rest.",
        "For personal data, tokenise at the lander, give personal-data landing folders a one-day expiry, and let Macie scan landing buckets for personal data in the wrong place.",
    ],
    "monitor": [
        ("BucketSizeBytes and NumberOfObjects", "Daily CloudWatch storage metrics per bucket and class. A sudden jump in objects often means small files or a stuck clean-up."),
        ("4xxErrors and 5xxErrors", "Request metrics (switch them on per bucket or prefix). A rise in 503s means throttling on a hot prefix; 403s mean a broken role or policy."),
        ("FirstByteLatency and TotalRequestLatency", "Request metrics that show whether slow jobs are waiting on S3 or on their own compute."),
        ("Average file size per table", "Not an S3 metric: compute it from S3 Inventory or Delta table details. Below a few tens of MB on a big table means compaction is not keeping up."),
        ("Cost by bucket in the Cost and Usage Report", "Tag buckets by catalog and environment so storage, request and transfer cost can be traced to a data product."),
    ],
    "limits": [
        ("Object size", "Up to 50 TB per object (raised from 5 TB in December 2025); a single PUT is limited to 5 GB, larger objects use multipart upload"),
        ("Request rate", "At least 3,500 PUT, COPY, POST or DELETE and 5,500 GET or HEAD requests per second per partitioned prefix, scaling gradually"),
        ("Buckets per account", "10,000 general purpose buckets by default; more on request through Service Quotas"),
        ("Objects per bucket", "No limit on the number of objects or the size of a bucket"),
        ("Multipart upload", "Up to 10,000 parts per upload"),
    ],
    "decisions": [
        ("Where Databricks managed tables live", "One general purpose bucket and one KMS key per catalog, set as the catalog's managed location",
         "Pursue: clear ownership, separate keys for restricted data, and clean cost per catalog."),
        ("Raw files from DMS, AppFlow, SFTP and Firehose", "One landing bucket per environment, files kept as received, deleted 30 days after reaching bronze",
         "Pursue: replayable loads with a short, enforced retention."),
        ("Audit and config change logs", "Separate audit bucket with Object Lock in compliance mode for seven years",
         "Pursue: nobody, root included, can alter the evidence."),
        ("Reaching S3 from private subnets", "Gateway VPC endpoint plus deny-unless-endpoint bucket policies",
         "Pursue: free, private and removes the NAT gateway charge."),
        ("One giant shared bucket for every team and layer", "Everything under prefixes in a single bucket",
         "Drop: one key, one policy and one blast radius for all data; hard to cost and hard to lock down."),
        ("External tables everywhere to stay open", "Register every path as an external table",
         "Drop: managed tables are already open Parquet files in your bucket; external only hands the chores back to you."),
    ],
    "faq": [
        ("Is S3 a data lake?", "S3 is the storage a data lake sits on. A lake or lakehouse also needs a table format (Delta or Iceberg), a catalog with permissions (Unity Catalog), and engines to read and write. S3 alone is a pile of files."),
        ("Does Databricks copy my data out of S3?", "No. Classic and serverless compute read and write your buckets in your account and Region. Caches on cluster disks are temporary. The tables themselves stay as Parquet files in S3, encrypted with your keys."),
        ("Is S3 strongly consistent now?", "Yes. Since December 2020 S3 gives strong read-after-write consistency for PUT and DELETE in all Regions, and list results reflect completed writes. Delta and Iceberg still need conditional writes or a catalog to stop two writers committing the same version."),
        ("How do I stop S3 costs creeping up?", "Expire noncurrent versions and incomplete multipart uploads, keep files large through compaction, use the gateway endpoint instead of NAT, turn on Bucket Keys, and tag buckets so the Cost and Usage Report shows cost per catalog."),
    ],
    "sources": [
        ("AWS docs: What is Amazon S3", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html"),
        ("AWS docs: General purpose bucket quotas", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/BucketRestrictions.html"),
        ("AWS docs: Optimizing Amazon S3 performance", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/optimizing-performance.html"),
        ("AWS What's New: S3 maximum object size 50 TB (Dec 2025)", "https://aws.amazon.com/about-aws/whats-new/2025/12/amazon-s3-maximum-object-size-50-tb"),
        ("AWS docs: S3 storage classes", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html"),
        ("Amazon S3 pricing", "https://aws.amazon.com/s3/pricing/"),
    ],
    "related": [
        ("Data platform on AWS and Databricks", "/learn/data-platform-architecture/aws-databricks/"),
        ("Who maintains your tables", "/learn/table-maintenance/"),
        ("Medallion architecture", "/learn/medallion-architecture/"),
        ("S3 storage classes and lifecycle", "svc:s3-storage-classes"),
        ("S3 Versioning, Replication and Object Lock", "svc:s3-data-protection"),
        ("Amazon S3 Tables", "svc:s3-tables"),
    ],
}
