SERVICE = {
    "slug": "s3-storage-classes",
    "name": "Amazon S3 storage classes and lifecycle (Intelligent-Tiering, Glacier)",
    "short": "S3 storage classes",
    "group": "storage",
    "one_line": "Price tiers for the same S3 object, plus lifecycle rules that move or delete objects as they age.",
    "status": ("Generally available. The S3 Glacier storage classes are current; the original vault-based Amazon Glacier "
               "service no longer accepts new customers, and AWS points new archive work to the Glacier classes inside S3. "
               "Reduced Redundancy Storage still exists but AWS recommends against it."),
    "checked": "2026-11-11",
    "site_verdict": ("Pursue", "Lifecycle rules are how the platform keeps its retention promises: landing files deleted 30 days "
                     "after they reach bronze, personal-data landing deleted after a day, bronze kept 3 years in S3 Standard and then "
                     "in S3 Glacier Instant Retrieval until year 8. Never put files of a live Delta table into Glacier Flexible "
                     "Retrieval or Deep Archive: Spark cannot read them without a restore."),
    "equivalents": {"azure": "Blob Storage access tiers (Hot, Cool, Cold, Archive) and lifecycle management",
                    "gcp": "Cloud Storage classes (Standard, Nearline, Coldline, Archive) and Autoclass",
                    "databricks": "none: Databricks reads whatever class S3 serves; Delta VACUUM and Predictive Optimization manage table history, not storage class",
                    "open_source": "MinIO lifecycle and tiering rules"},
    "plain": [
        "Every object you store in Amazon S3 has a storage class. The class does not change what the object is or how you name it. "
        "It changes three things: what you pay each month to keep it, what you pay each time you read it, and how fast you can get it back. "
        "S3 Standard is the default: no minimum time, no fee to read, millisecond access. The colder classes charge less to store and more "
        "to read, and some make you wait minutes or hours before the bytes come back.",
        "A lifecycle rule is a small piece of bucket configuration that says, for objects under a prefix or with a tag, after so many days "
        "move them to another class, or delete them. S3 runs the rule for you every day. Nobody writes a job and nobody has to remember. "
        "S3 Intelligent-Tiering is a special class that does the moving itself: it watches each object and moves it to a cheaper tier when "
        "nobody has read it for 30 days, and to a cheaper one again at 90 days, with no fee when it is read again.",
        "A concrete example from a tyre manufacturer. Curing presses in the plants send sensor readings every few seconds, and nightly SAP "
        "extracts arrive as files. The raw files land in a landing bucket and are loaded into bronze Delta tables within the hour. After that, "
        "nobody needs the landing copy, so a lifecycle rule deletes it 30 days later. Bronze tables are read often for the first months, then "
        "almost only by auditors and by the rare replay, so after three years their files move to S3 Glacier Instant Retrieval, which is "
        "still readable in milliseconds by Spark, and after year 8 they are deleted.",
    ],
    "analogy": "A warehouse with a front shelf, a back room and a locked basement: same boxes, cheaper rent the further back they sit, but fetching from the basement takes a day and costs a porter.",
    "big_picture": [
        "Storage classes sit in the store lane, under every bucket of the platform. They are not a separate service you call; they are a "
        "property of each object and a set of rules on each bucket. The movers (DMS, AppFlow, Transfer Family, Firehose) write into landing "
        "in S3 Standard. Databricks writes bronze, silver and gold Delta tables into one bucket per catalog, also in S3 Standard. Lifecycle "
        "rules then age that data according to the retention table the platform agreed with the data owners.",
        "The rules differ by layer. Landing is short-lived: files are deleted 30 days after bronze has them, and folders that carry personal "
        "data are deleted after one day, with old versions expiring the same day. Bronze is the replayable record, so it stays longest: three "
        "years in Standard, then Glacier Instant Retrieval until year 8. Silver and gold are rebuilt from bronze when needed, so their old "
        "file versions are cleaned by Delta VACUUM after 30 days rather than archived. The audit bucket keeps its copies for 7 years under "
        "Object Lock.",
        "The important boundary is between classes Spark can read directly and classes it cannot. S3 Standard, Standard-IA, Intelligent-Tiering "
        "(its automatic tiers) and Glacier Instant Retrieval all answer a normal GET in milliseconds, so a Delta table can sit on them and still "
        "work. Glacier Flexible Retrieval, Glacier Deep Archive and the optional archive tiers of Intelligent-Tiering need a restore first. "
        "A query that touches one of those files fails, so they are only for exports and copies that nobody queries.",
    ],
    "upstream": ["svc:s3", "svc:data-firehose", "svc:dms"],
    "downstream": ["Databricks (reads Delta files in any instant-access class)", "svc:athena", "svc:cost-management"],
    "concepts": [
        ("Storage class", "A per-object setting such as STANDARD, STANDARD_IA, INTELLIGENT_TIERING, GLACIER_IR, GLACIER or DEEP_ARCHIVE that sets price, retrieval fee and access speed."),
        ("Lifecycle rule", "Bucket configuration that transitions objects to another class, or expires (deletes) them, a set number of days after creation or after they stop being current."),
        ("Transition", "A lifecycle move from one class to a colder one. Each transition is billed as a request per object."),
        ("Expiration", "A lifecycle delete. On a versioned bucket it adds a delete marker; a separate noncurrent-version rule removes old versions for real."),
        ("Minimum storage duration", "The shortest time you are billed for: 30 days for the Infrequent Access classes, 90 days for Glacier Instant and Flexible Retrieval, 180 days for Deep Archive."),
        ("Minimum billable object size", "Standard-IA, One Zone-IA and Glacier Instant Retrieval bill any object smaller than 128 KB as if it were 128 KB."),
        ("Intelligent-Tiering", "A class that moves each object between Frequent, Infrequent (after 30 days unread) and Archive Instant Access (after 90 days) tiers for a small monitoring fee per object, with no retrieval fee."),
        ("Restore", "A request that makes a temporary readable copy of an archived object in Glacier Flexible Retrieval or Deep Archive; it takes minutes to hours and costs a retrieval fee."),
    ],
    "use_when": [
        "Use lifecycle expiration on every landing prefix, so raw files and their old versions disappear on the schedule the retention table promises.",
        "Use Glacier Instant Retrieval for old bronze files that must stay queryable for audits or replays but are read a few times a year.",
        "Use Intelligent-Tiering for large shared areas with unknown read patterns, such as an exports bucket or a data science scratch area, where most objects are well above 128 KB.",
        "Use Glacier Deep Archive for copies that exist only for legal reasons, such as a yearly export of finished tables that nobody queries.",
    ],
    "avoid_when": [
        "Avoid Glacier Flexible Retrieval and Deep Archive for files of any table that a query, a VACUUM or a time-travel read may touch; the read fails until someone restores the file.",
        "Avoid the Infrequent Access and Glacier Instant classes for buckets full of small files, such as raw sensor JSON of a few kilobytes, because each object is billed as 128 KB.",
        "Avoid colder classes for data that is deleted soon, because an object deleted before its minimum duration is billed for the full minimum anyway.",
        "Avoid lifecycle transitions on the managed table buckets for silver and gold; Delta VACUUM already removes old files, and archiving live files only adds retrieval fees.",
    ],
    "challenges": [
        ("Archived table files break queries",
         "A rule moved files older than a year under a Delta table prefix into Glacier Flexible Retrieval. Any query that still needs one of those files, including a full scan, fails with an invalid object state error.",
         "Scope transitions by prefix to bronze history only, and only to Glacier Instant Retrieval. Test the rule on a copy of one table and run a full scan afterwards."),
        ("Small files cost more after a transition",
         "Raw sensor messages of 2 to 20 KB were moved to Standard-IA to save money. The bill went up, because each object is billed as 128 KB and each transition is a paid request.",
         "Compact small files into bronze Delta tables first and archive the large Parquet files, not the raw messages. Use a size filter in the lifecycle rule (ObjectSizeGreaterThan)."),
        ("Early-delete charges",
         "Landing files were moved to Glacier Instant Retrieval at day 1 and deleted at day 30, so every file was billed for 90 days.",
         "Compare the class minimum with the expiry date. If data lives less than the minimum, leave it in Standard."),
        ("Versions that never expire",
         "Versioning is on, the expiration rule runs, but storage keeps growing. Expiration only adds a delete marker; noncurrent versions stay and are billed.",
         "Add NoncurrentVersionExpiration and ExpiredObjectDeleteMarker cleanup to every versioned bucket, and abort incomplete multipart uploads after a few days."),
        ("Intelligent-Tiering on tiny objects",
         "Objects under 128 KB are never moved to a cheaper tier, so a bucket of small files gains nothing, while large ones pay a monitoring fee per object.",
         "Use Intelligent-Tiering where most objects are large. Check the object size distribution in S3 Storage Lens before switching."),
        ("Archive tiers switched on by mistake",
         "Someone turned on the optional Archive Access tier of Intelligent-Tiering for a bucket Spark reads. After 90 days unread, files need a restore and jobs fail.",
         "Leave the optional archive tiers off on any bucket a query engine reads. Only the automatic tiers keep millisecond access."),
        ("Retention promise not in code",
         "The retention table says landing is deleted after 30 days, but nobody wrote the rule, so years of raw files with personal data remain.",
         "Declare lifecycle rules in Terraform next to the bucket, one rule per row of the retention table, and test them in pre-production."),
    ],
    "compare": [
        ("Azure Blob access tiers", "You build the same platform on Azure; Hot, Cool, Cold and Archive tiers with lifecycle management work the same way.", "You are on AWS; the S3 classes are the native option."),
        ("Google Cloud Storage classes and Autoclass", "You are on GCP; Autoclass is the closest twin to Intelligent-Tiering.", "You are on AWS."),
        ("Delta VACUUM and Predictive Optimization", "The aim is to remove old versions of table files; Delta knows which files a table still needs.", "The aim is to make files that must be kept cheaper; VACUUM deletes, it does not tier."),
        ("AWS Backup for S3", "You need point-in-time restore of a whole bucket for non-personal data.", "The data includes personal data that must really disappear on erasure; this platform does not use AWS Backup there."),
    ],
    "cost": {
        "model": ("Each class has its own price per GB-month of storage, per request (PUT, GET, transition) and, for the colder classes, per GB "
                  "retrieved. The colder the class, the lower the storage price and the higher the read and transition costs. Infrequent "
                  "Access and Glacier classes also have a minimum storage duration and, for some, a minimum billable size of 128 KB. "
                  "Intelligent-Tiering adds a small monthly monitoring fee per object of 128 KB or more and has no retrieval fee. Lifecycle "
                  "rules themselves are free; the transitions they trigger are billed as requests. Check list prices for your region."),
        "drivers": [
            "Total GB in each class, which for this platform is dominated by bronze history.",
            "Number of objects transitioned, because every transition is a request; many small files make this large.",
            "GB retrieved from Infrequent Access and Glacier classes, including reads by Spark scans and restores for audits.",
            "Noncurrent object versions kept by versioned buckets until a rule removes them.",
        ],
        "traps": [
            "Objects under 128 KB billed as 128 KB in Standard-IA, One Zone-IA and Glacier Instant Retrieval.",
            "Early-delete charges when an object leaves a class before its minimum duration.",
            "Glacier Flexible Retrieval and Deep Archive add about 40 KB of extra metadata per object, part of it billed at the Standard rate.",
            "Full-table Spark scans over Glacier Instant Retrieval data pay a retrieval fee per GB every time.",
            "Incomplete multipart uploads stay billed until an abort rule removes them.",
        ],
    },
    "security": [
        "Storage class does not change who can read an object; IAM, bucket policies, Unity Catalog grants and KMS still decide access, so archived data keeps its protection.",
        "Objects keep their encryption when they move between classes; with SSE-KMS each transition and restore can call KMS, so bucket keys help keep KMS request costs down.",
        "Lifecycle expiration is how retention and erasure promises become real for landing files that held personal data; Macie scans landing to catch files kept in the wrong place.",
        "Changes to lifecycle configuration (PutBucketLifecycleConfiguration) are recorded in CloudTrail; alert on them for the landing, table and audit buckets.",
    ],
    "monitor": [
        ("BucketSizeBytes by StorageType", "Daily CloudWatch storage metric per class; shows whether data is really ageing into cheaper classes."),
        ("NumberOfObjects", "Daily object count; a jump in small objects warns of small-file costs before transitions."),
        ("S3 Storage Lens", "Organisation-wide view of bytes per class, noncurrent versions, incomplete multipart uploads and lifecycle rule coverage."),
        ("Cost and Usage Report line items", "Usage types for TimedStorage, transitions (Requests-Tier) and retrieval per class, joined to data products by bucket and tag."),
        ("Lifecycle events in S3 Event Notifications", "LifecycleTransition and LifecycleExpiration events, for a log of what moved and what was deleted."),
    ],
    "limits": [
        ("Lifecycle rules per bucket", "Up to 1,000 rules in one lifecycle configuration"),
        ("Minimum storage duration", "30 days for Standard-IA and One Zone-IA, 90 days for Glacier Instant and Flexible Retrieval, 180 days for Deep Archive"),
        ("Minimum billable size", "128 KB for Standard-IA, One Zone-IA and Glacier Instant Retrieval"),
        ("Intelligent-Tiering monitoring", "Objects smaller than 128 KB are not monitored and stay in the Frequent Access tier"),
        ("Archived object access", "Glacier Flexible Retrieval and Deep Archive need a restore before any read"),
    ],
    "decisions": [
        ("Landing files from DMS, AppFlow and SFTP", "Standard, expire 30 days after bronze has them; personal-data prefixes after one day; old versions expire with them",
         "Pursue: cheapest is to delete, and the rule is the retention promise in code."),
        ("Bronze history older than three years", "Lifecycle transition to Glacier Instant Retrieval, delete at year 8",
         "Pursue: still readable in milliseconds by Spark for audits and replays, at a much lower storage price."),
        ("Moving old silver and gold files to Glacier Deep Archive", "Archive live table prefixes",
         "Drop: queries, VACUUM and time travel fail on archived files; Delta VACUUM already removes what is not needed."),
        ("Intelligent-Tiering as default on the table buckets", "Switch the class for all Delta files",
         "Pursue with care: fine for large Parquet files with unknown access, no gain for small files, and never turn on the optional archive tiers."),
        ("Raw sensor JSON of a few KB moved to Standard-IA", "Transition small objects",
         "Drop: each object is billed as 128 KB; compact into bronze first."),
        ("Existing vaults in the original Amazon Glacier service", "Keep them while you plan a move to S3 Glacier classes",
         "Keep if you have it: the vault service takes no new customers; new archives belong in S3 Glacier classes."),
    ],
    "faq": [
        ("Can Spark or Databricks read data in S3 Glacier?",
         "It depends on the class. Glacier Instant Retrieval answers normal reads in milliseconds, so Spark reads it directly but pays a retrieval fee per GB. Glacier Flexible Retrieval and Deep Archive need a restore first, and a read without one fails."),
        ("What is the difference between Amazon Glacier and S3 Glacier?",
         "The S3 Glacier storage classes live inside S3 buckets and use the S3 API. The original Amazon Glacier service used vaults and its own API; it no longer accepts new customers, and AWS recommends the S3 Glacier classes instead."),
        ("Is S3 Intelligent-Tiering always cheaper?",
         "No. It saves money on large objects whose reads drop off, with no retrieval fee. Objects under 128 KB never move tier, and every larger object pays a small monitoring fee, so a bucket of hot or tiny files can cost more."),
        ("Do lifecycle rules delete old versions on a versioned bucket?",
         "Only if you ask. A normal expiration adds a delete marker; you need a NoncurrentVersionExpiration rule to remove old versions, and a rule to clean up expired delete markers."),
        ("Should Delta table buckets have lifecycle rules at all?",
         "Yes, but narrow ones: noncurrent-version expiry, abort incomplete uploads, and for bronze a transition of old history to Glacier Instant Retrieval. Leave deleting table files to Delta VACUUM, which knows which files the table still needs."),
    ],
    "sources": [
        ("AWS docs: Understanding and managing Amazon S3 storage classes", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html"),
        ("AWS docs: Managing the lifecycle of objects", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html"),
        ("AWS docs: How S3 Intelligent-Tiering works", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/intelligent-tiering-overview.html"),
        ("AWS docs: S3 Glacier storage classes", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/glacier-storage-classes.html"),
        ("AWS docs: What is Amazon Glacier (vault service status)", "https://docs.aws.amazon.com/amazonglacier/latest/dev/introduction.html"),
        ("Amazon S3 pricing", "https://aws.amazon.com/s3/pricing/"),
    ],
    "related": [
        ("Amazon S3", "svc:s3"),
        ("S3 Versioning, Replication and Object Lock", "svc:s3-data-protection"),
        ("Who maintains your tables", "/learn/table-maintenance/"),
        ("Medallion architecture", "/learn/medallion-architecture/"),
        ("Data platform on AWS and Databricks", "/learn/data-platform-architecture/aws-databricks/"),
        ("Cost calculator", "/learn/data-systems/platform/cost/calculator/"),
    ],
}
