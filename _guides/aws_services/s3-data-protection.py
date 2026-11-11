SERVICE = {
    "slug": "s3-data-protection",
    "name": "S3 Versioning, Replication and Object Lock",
    "short": "S3 data protection",
    "group": "storage",
    "one_line": "Keep old versions of objects, copy them to another bucket or region, and lock records so nobody can change them.",
    "status": ("Generally available. Object Lock now also offers variable retention, where an event hold keeps an object locked "
               "until a business event and the retention clock starts when the hold is released."),
    "checked": "2026-11-11",
    "site_verdict": ("Pursue", "Versioning on landing, with old versions expiring alongside the files; cross-region replication of landing "
                     "and bronze to the recovery region; Object Lock in compliance mode for 7 years on the audit bucket. On table "
                     "buckets, expire old versions within 30 days so that Delta VACUUM and erasure really remove data."),
    "equivalents": {"azure": "Blob versioning, soft delete, object replication and immutable storage (WORM) policies",
                    "gcp": "Object Versioning, soft delete, dual-region or turbo replication, Bucket Lock and object retention",
                    "databricks": "Delta time travel, UNDROP for managed tables, deep clone to another region (protects tables, not raw buckets)",
                    "open_source": "MinIO versioning, bucket replication and object locking"},
    "plain": [
        "Three S3 features protect data in different ways. Versioning keeps every version of an object. When someone overwrites "
        "or deletes a file, the old version stays in the bucket and can be brought back. Replication copies new objects to another "
        "bucket, in the same region or a different one, a few seconds to minutes after they are written. Object Lock marks an object "
        "version as write-once-read-many, often called WORM: for a set time nobody can change or delete it, and in compliance mode "
        "not even the account's root user can.",
        "They answer different fears. Versioning answers 'someone deleted or overwrote the wrong file'. Replication answers 'the "
        "region is down' or 'we need a copy in another account'. Object Lock answers 'an auditor must be sure this record was never "
        "changed', and also 'ransomware must not be able to delete our backups'. Replication and Object Lock both need versioning switched on.",
        "A concrete example from a tyre manufacturer. Nightly SAP extracts and DMS change files land in a landing bucket in Mumbai. "
        "Versioning is on, so a supplier who re-sends a file with the same name does not destroy the first one. Landing and bronze "
        "replicate to a bucket in Hyderabad, so the platform can carry on if Mumbai fails. Copies of audit logs and config change logs go "
        "to an audit bucket where Object Lock keeps each one unchangeable for 7 years.",
    ],
    "analogy": "A filing room with three habits: never throw away the old page when a new one is filed, send a photocopy of every page to a second office, and seal some folders so that even the manager cannot open them until the date on the seal.",
    "big_picture": [
        "These features sit in the store lane, on the buckets every other service writes to. They are settings, not a separate service. "
        "The movers write into landing, Databricks writes Delta tables into one bucket per catalog, and CloudTrail and the platform's run "
        "log write into the audit bucket. Each of those buckets gets its own mix of versioning, replication and locking, declared in Terraform with the bucket.",
        "For the recovery plan, landing and bronze replicate to Hyderabad with a target of about 15 minutes. Landing replication lets the "
        "lander replay the last minutes that had not yet reached bronze. Bronze replication carries only tokens, never real personal values. "
        "Replication does not keep order: a Delta commit file may arrive before the data files it lists. So in the recovery region bronze is "
        "registered at the last table version whose files have all arrived, and silver and gold then catch up from bronze by run id. "
        "Silver and gold are not replicated file by file; they are rebuilt, or copied with Delta deep clone when a faster restart is needed.",
        "Versioning interacts with deletion. When Delta VACUUM deletes old table files, or a lifecycle rule expires a landing file, a "
        "versioned bucket keeps the old bytes as a noncurrent version. If nothing removes those, a person's data that the platform "
        "promised to erase is still on disk. That is why every versioned bucket on this platform expires noncurrent versions within 30 days, "
        "and personal-data landing folders within a day. It is also why AWS Backup is not used on the vault or personal-data tables: a backup "
        "would bring back what erasure removed.",
    ],
    "upstream": ["svc:s3", "svc:dms", "svc:cloudtrail"],
    "downstream": ["Recovery bucket in a second region", "Auditors and compliance reviews", "svc:kms"],
    "concepts": [
        ("Versioning", "A bucket setting that keeps every version of every object, each with a version id. Once on, it can be suspended but never fully switched off."),
        ("Noncurrent version", "An older version of an object that has been overwritten or deleted. It is still stored and billed until a lifecycle rule removes it."),
        ("Delete marker", "What a simple DELETE adds on a versioned bucket. The object looks gone, but older versions remain underneath."),
        ("Cross-Region Replication", "Live replication that copies new objects to a bucket in another AWS Region, asynchronously."),
        ("Same-Region Replication", "Live replication to another bucket in the same region, often in another account, for example to aggregate logs or keep a copy away from the producer's admins."),
        ("Replication Time Control", "An option that replicates 99.99 percent of new objects within 15 minutes, backed by an SLA, and adds replication metrics."),
        ("Batch Replication", "An on-demand S3 Batch Operations job that replicates objects that existed before the rule, or that failed to replicate."),
        ("Object Lock modes", "Governance mode can be bypassed by users with a special permission; compliance mode cannot be shortened or removed by anyone, including root, until the date passes."),
        ("Legal hold and event hold", "A legal hold locks an object version until someone removes it. An event hold, part of variable retention, keeps it locked until a business event, then starts a fixed retention period."),
    ],
    "use_when": [
        "Use versioning on landing buckets, so a re-sent or corrupted file never silently replaces the one bronze already loaded.",
        "Use Cross-Region Replication with Replication Time Control for landing and bronze when the recovery plan promises a restart in another region within minutes.",
        "Use Object Lock in compliance mode on the audit bucket, where copies of audit logs and config change logs must be provably unchanged for 7 years.",
        "Use Same-Region Replication into a separate account when a copy must sit out of reach of the people who administer the source account.",
        "Use Batch Replication once, when you add replication to a bucket that already holds data, or to retry objects marked FAILED.",
    ],
    "avoid_when": [
        "Avoid versioning without a noncurrent-version expiry rule; storage grows quietly and deleted personal data stays on disk.",
        "Avoid Object Lock compliance mode on any bucket that holds personal data subject to erasure; nobody can delete a locked version before its date.",
        "Avoid replicating silver and gold file by file and expecting a consistent table in the other region; rebuild them from bronze or use Delta deep clone.",
        "Avoid treating replication as a backup; deletes and overwrites can replicate too, so it protects against losing a region, not against a bad job.",
    ],
    "challenges": [
        ("Erased data lives on as old versions",
         "VACUUM deletes the files that held a person's data, but the bucket is versioned, so the bytes stay as noncurrent versions for months.",
         "Add NoncurrentVersionExpiration of 30 days or less on every table bucket and one day on personal-data landing. Test erasure end to end and check that no version remains."),
        ("Replicated Delta table is not consistent",
         "In the recovery region the latest _delta_log commit points to data files that have not arrived yet, so reads fail with missing files.",
         "Register bronze at the last version whose files all exist, by checking the files each commit lists. Rebuild silver and gold from bronze by run id."),
        ("Existing objects not replicated",
         "Replication was switched on for a bucket that already held two years of data; only new objects were copied.",
         "Run a Batch Replication job for existing objects once, and again for objects with status FAILED."),
        ("Replication fails on KMS-encrypted objects",
         "Objects encrypted with a customer managed key are skipped because the replication role cannot decrypt in the source or encrypt in the destination.",
         "Opt in to replicating SSE-KMS objects in the rule, give the replication role kms:Decrypt on the source key and kms:Encrypt on a key in the destination region."),
        ("Locked bucket cannot be cleaned",
         "Compliance mode was set on a test bucket with a 7-year default. Nobody can delete the objects, and the bucket is billed until the date passes.",
         "Try retention in governance mode first. Use compliance mode only on the audit bucket, set by Terraform after review."),
        ("Delete markers replicate or do not, by surprise",
         "Teams expect a delete in Mumbai to be mirrored in Hyderabad, or the opposite, and get the other behaviour.",
         "Decide delete-marker replication on purpose per rule and write it down. Remember that deletes of specific versions are never replicated."),
        ("Lag nobody watches",
         "Replication falls behind during a large backfill. The recovery copy is hours old, but the recovery plan says 15 minutes.",
         "Enable replication metrics and alarm on ReplicationLatency and OperationsPendingReplication. Throttle big backfills or schedule them."),
    ],
    "compare": [
        ("Azure Blob versioning, object replication and immutable storage", "You build the same platform on Azure; the features map closely.", "You are on AWS."),
        ("Google Cloud Storage versioning, dual-region and Bucket Lock", "You are on GCP; a dual-region bucket replaces most cross-region replication rules.", "You are on AWS."),
        ("Delta time travel and deep clone", "You need to undo a bad write to a table or copy a consistent table to another region.", "You need to protect raw files in landing or prove a log was never changed."),
        ("AWS Backup for S3", "You need point-in-time restore of a non-personal bucket with one backup policy across services.", "The bucket holds personal data that erasure must remove; a backup would bring it back."),
        ("Multi-Region Access Points", "Applications must fail over between two buckets behind one name, with two-way replication.", "Only the data platform reads the copy, and failover is a planned runbook step."),
    ],
    "cost": {
        "model": ("Versioning has no fee of its own, but every noncurrent version is stored and billed like a normal object until a rule "
                  "removes it. Replication bills the PUT requests into the destination, the storage of the copy in its class, and data "
                  "transfer between regions for cross-region rules; Replication Time Control adds a fee per GB replicated. Batch "
                  "Replication bills S3 Batch Operations jobs and requests. Object Lock has no separate fee, but locked objects must be "
                  "stored until their date. Check list prices for your region."),
        "drivers": [
            "GB of noncurrent versions kept, which depends on how often files are overwritten or deleted and how fast rules expire them.",
            "GB replicated across regions each month, mostly landing and bronze for this platform.",
            "Replication Time Control per-GB fee, if switched on.",
            "Storage class chosen for the replica bucket.",
            "Years of audit records held under Object Lock.",
        ],
        "traps": [
            "Versioning on a busy Delta bucket with no noncurrent-version expiry roughly doubles storage over time.",
            "Replicating silver and gold as well as bronze doubles the cross-region transfer for tables that could be rebuilt.",
            "KMS calls on both sides of replication add request charges; S3 bucket keys reduce them.",
            "Compliance-mode locks on the wrong bucket cannot be undone, so you pay for that storage until the date.",
        ],
    },
    "security": [
        "Only a few roles should be able to change versioning, replication or lock settings; deny PutBucketVersioning, PutReplicationConfiguration and PutObjectLockConfiguration to everyone else with bucket policies or SCPs.",
        "The replication role needs read on the source, write on the destination, and KMS permissions on both keys; scope it to the named buckets only.",
        "Replicas in another region must use a KMS key in that region and the same tight bucket policy; a copy is only as safe as its weakest bucket.",
        "Object Lock in compliance mode gives auditors evidence that audit logs were not changed; keep that bucket in an account with very few administrators.",
        "Personal data must be erasable, so never put it under Object Lock or AWS Backup, and keep noncurrent-version expiry short where it may appear.",
        "CloudTrail records changes to all three settings; alert on any change to the audit bucket's configuration.",
    ],
    "monitor": [
        ("ReplicationLatency", "Seconds the destination is behind the source for a replication rule; the main number for the recovery target."),
        ("OperationsPendingReplication", "Count of objects waiting to replicate; grows during backfills or failures."),
        ("OperationsFailedReplication", "Objects that failed to replicate; each needs a Batch Replication retry or a permission fix."),
        ("BytesPendingReplication", "Bytes still to copy, to judge how long a catch-up will take."),
        ("Noncurrent version bytes in S3 Storage Lens", "How much storage old versions use per bucket; should stay small if expiry rules work."),
        ("CloudTrail events on bucket configuration", "PutBucketVersioning, PutBucketReplication and PutObjectLockConfiguration calls, alerted for protected buckets."),
    ],
    "limits": [
        ("Replication Time Control", "99.99 percent of new objects within 15 minutes, backed by an SLA; does not apply to Batch Replication"),
        ("Prerequisite", "Versioning must be on in source and destination for replication, and on the bucket for Object Lock"),
        ("Live replication scope", "Only objects written after the rule exists; older objects need Batch Replication"),
        ("Compliance mode", "Retention cannot be shortened or removed by any user, including root, until the retain-until date"),
        ("Replication rules", "Up to 1,000 rules in one replication configuration"),
    ],
    "decisions": [
        ("Landing bucket for DMS, AppFlow and SFTP files", "Versioning on, noncurrent versions expire with the files (one day for personal-data folders)",
         "Pursue: protects against overwrites without keeping erased data."),
        ("Recovery region for landing and bronze", "Cross-Region Replication to Hyderabad with Replication Time Control and replication metrics",
         "Pursue: about 15 minutes of exposure, bronze registered at the last complete version."),
        ("Audit and config change logs", "Separate audit bucket, Object Lock compliance mode, 7 years",
         "Pursue: evidence that records were never changed."),
        ("Silver and gold tables in the recovery region", "Rebuild from bronze, or Delta deep clone for the most urgent tables",
         "Pursue with care: file-level replication of these buckets gives an inconsistent table and doubles transfer."),
        ("AWS Backup for the token vault and personal-data tables", "Back up the whole bucket",
         "Drop: a backup would bring back data that erasure removed."),
    ],
    "faq": [
        ("Does S3 replication copy existing objects?",
         "No. Live replication copies only objects written after the rule exists. Use S3 Batch Replication for older objects and for objects whose replication failed."),
        ("Can I turn off versioning once it is on?",
         "You can suspend it, which stops new versions being kept, but you cannot return the bucket to never-versioned, and existing versions stay until you delete them or a lifecycle rule expires them."),
        ("What is the difference between governance and compliance mode?",
         "In governance mode, users with the s3:BypassGovernanceRetention permission can delete a locked object or shorten its lock. In compliance mode nobody can, including the root user, until the retention date passes."),
        ("Is replication a backup?",
         "Not on its own. It protects against losing a region, but overwrites and, if configured, deletes are copied too. Versioning on both sides plus Delta time travel give the undo; replication gives the second location."),
        ("Can I replicate a Delta table with S3 replication?",
         "The files will arrive, but not in order, so the newest commit may list files that are still in flight. Register the table at the last version whose files all exist, or use Delta deep clone for a consistent copy."),
        ("Does versioning stop VACUUM from freeing space?",
         "Yes, unless you add a rule that expires noncurrent versions. VACUUM deletes the current object, and versioning keeps it as an old version that is still billed."),
    ],
    "sources": [
        ("AWS docs: Retaining multiple versions of objects with S3 Versioning", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html"),
        ("AWS docs: Replicating objects within and across Regions", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication.html"),
        ("AWS docs: Meeting compliance requirements with S3 Replication Time Control", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication-time-control.html"),
        ("AWS docs: Locking objects with Object Lock", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html"),
        ("Amazon S3 pricing", "https://aws.amazon.com/s3/pricing/"),
    ],
    "related": [
        ("Amazon S3", "svc:s3"),
        ("S3 storage classes and lifecycle", "svc:s3-storage-classes"),
        ("AWS Backup", "svc:aws-backup"),
        ("Who maintains your tables", "/learn/table-maintenance/"),
        ("Data platform on AWS and Databricks", "/learn/data-platform-architecture/aws-databricks/"),
    ],
}
