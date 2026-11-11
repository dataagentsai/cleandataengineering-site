SERVICE = {
    "slug": "glue-etl",
    "name": "AWS Glue ETL jobs (Spark, Python shell, streaming)",
    "short": "Glue ETL jobs",
    "group": "processing",
    "one_line": "Serverless Apache Spark and plain Python jobs on AWS, billed per worker-second, for moving and reshaping data between stores.",
    "status": ("Generally available. Glue 6.0 (Spark 4.1.1, Python 3.13) is the newest version and 5.1 is the default for new jobs. "
               "Glue for Ray closed to new customers on 30 Apr 2026. Glue 0.9, 1.0 and 2.0 Spark jobs reached end of life on 1 Apr 2026, "
               "and Python shell 3.6 on 1 Jun 2026."),
    "checked": "2026-11-11",
    "site_verdict": ("Keep if you have it",
                     "Do not start new Glue jobs on this platform: Databricks is the one engine for batch and streaming. Existing Glue jobs "
                     "are rebuilt as Databricks pipelines one subject at a time, run side by side for two weeks until counts and sums "
                     "reconcile, then switched off. The Glue Data Catalog can still matter if Athena or Redshift read the same tables."),
    "equivalents": {"azure": "Azure Data Factory data flows, Fabric Spark", "gcp": "Dataproc Serverless, Dataflow",
                    "databricks": "Lakeflow Jobs and Lakeflow Declarative Pipelines on serverless compute",
                    "open_source": "Apache Spark on any cluster"},
    "plain": [
        "AWS Glue is a family of data tools. This page is about one part of it: Glue ETL jobs. ETL stands for extract, transform and load, "
        "which means reading data from somewhere, changing its shape, and writing it somewhere else. A Glue job is a script, written in "
        "Python or Scala, that AWS runs for you on a temporary group of machines. You do not create or patch servers. You say how many "
        "workers you want, AWS starts them, runs the script, stops them, and bills you for the seconds they ran.",
        "There are three job types. A Spark job runs Apache Spark, an engine that splits a big dataset into pieces and works on the pieces "
        "in parallel across many machines. A streaming job is a Spark job that never ends; it keeps reading from a stream such as Kinesis "
        "or Kafka and writes small batches as data arrives. A Python shell job runs a single plain Python script on a small slice of a "
        "machine, for small tasks such as calling an API or running a SQL statement in a warehouse. A fourth type, Glue for Ray, is closed "
        "to new customers since 30 April 2026.",
        "A concrete example. A tyre maker exports SAP sales orders as CSV files every night into an S3 bucket. A Glue Spark job reads the "
        "new files, fixes the date formats, joins each order to the customer master, removes duplicate lines, and writes Parquet files "
        "partitioned by order date. A Glue crawler or the job itself then updates the Glue Data Catalog so that Athena can query the "
        "result. A feature called job bookmarks remembers which files were already processed, so the next night only new files are read.",
    ],
    "analogy": "A hired kitchen crew that arrives when you call, cooks exactly the recipe you hand them, and leaves; you pay by the minute, but you still write the recipe.",
    "big_picture": [
        "In a plain AWS data platform, Glue sits in the processing lane. Movers such as DMS, AppFlow and Transfer Family drop files into an "
        "S3 landing area, and Glue jobs turn landing into bronze, silver and gold tables. Glue Workflows or Step Functions start the jobs, "
        "and Athena, Redshift Spectrum or QuickSight read the results through the Glue Data Catalog.",
        "On this site's reference platform, that processing job belongs to Databricks. Lakeflow Declarative Pipelines and Lakeflow Jobs "
        "read the landing folder, write Delta tables in the medallion layout, check quality rules, record lineage in Unity Catalog and run "
        "both batch and streaming on one engine. Running Glue alongside would mean two Spark engines, two ways to grant access, two places "
        "to look for failures and two bills to explain. So Glue is not part of the target design.",
        "Glue still appears in two honest ways. First, many companies already have dozens or hundreds of Glue jobs. The migration plan "
        "rebuilds them as metadata-driven Databricks pipelines one subject at a time, for example sales orders first and then inventory, "
        "runs the old and new jobs in parallel for two weeks, compares row counts and sums, and only then switches the Glue job off. "
        "Second, the Glue Data Catalog, which is a separate part of Glue, may stay as the catalog that Athena and Redshift use, kept in step "
        "with Unity Catalog through catalog federation during the move.",
    ],
    "upstream": ["svc:dms", "svc:appflow", "svc:kinesis-data-streams"],
    "downstream": ["svc:s3", "svc:glue-data-catalog", "svc:athena"],
    "concepts": [
        ("DPU", "Data processing unit, the measure Glue bills by. One DPU is 4 vCPUs and 16 GB of memory. A G.1X worker is one DPU, a G.2X worker is two."),
        ("Worker type", "The size of each machine in the job. G.025X for small streams, G.1X and G.2X for most work, G.4X to G.16X for heavy joins, and R types with extra memory for jobs that run out of memory."),
        ("Glue version", "The bundle of Spark, Python and libraries the job runs on. 5.1 is the default; 6.0 brings Spark 4.1.1. Old versions reach end of support and then end of life, when runs stop."),
        ("DynamicFrame", "Glue's own wrapper around a Spark DataFrame that tolerates columns whose type changes between files. Handy for messy input, but it ties the code to Glue."),
        ("Job bookmark", "State that Glue keeps between runs so a job only reads files or rows it has not seen before. It is how most Glue jobs become incremental."),
        ("Flex execution", "A cheaper class for jobs that are not urgent. Glue runs them on spare capacity, so start times and run times can stretch. Only G.1X and G.2X workers."),
        ("Auto scaling", "Glue adds and removes workers during a run, up to the number you set, and bills each worker only for the time it ran."),
        ("Connection", "A stored definition of how to reach a database or a private network, including the VPC subnet and security group the workers join."),
    ],
    "use_when": [
        "You already run Glue jobs that work, and the plan is to keep them stable until each subject is rebuilt on Databricks.",
        "A team outside the data platform needs a small, occasional Spark job in an AWS-only account where Databricks is not available.",
        "You need a quick Python shell job that calls an AWS API or runs a SQL statement, and the account has no other scheduler.",
        "A job must write to the Glue Data Catalog for Athena users, and the team has no plan to adopt Unity Catalog.",
        "You want serverless Spark with no cluster to size, and the workload is a few jobs, not a platform.",
    ],
    "avoid_when": [
        "Avoid building new pipelines in Glue on a platform where Databricks already does processing; you would run two engines with two access models.",
        "Avoid Glue streaming jobs for always-on, low-latency work; a job that never ends bills every worker for every second of the month.",
        "Avoid DynamicFrame-heavy code if you may move later; plain Spark DataFrame code moves to Databricks or EMR with far fewer changes.",
        "Avoid Glue for Ray; it is closed to new customers and AWS points users toward Ray on Amazon EKS instead.",
        "Avoid using Glue as the place where business rules live if lineage, quality results and access must be shown in one catalog.",
    ],
    "challenges": [
        ("Version end of life",
         "When a Glue version reaches end of life, its jobs can no longer start. Glue 0.9, 1.0 and 2.0 Spark jobs stopped on 1 Apr 2026.",
         "Keep an inventory of jobs by GlueVersion. Upgrade one version at a time with a parallel run, or use the end-of-life date as the deadline to move the job to Databricks."),
        ("Bookmarks miss or repeat data",
         "A bookmark is reset, a file lands late with an old timestamp, or a script lacks the transformation_ctx name, and files are skipped or read twice.",
         "Make writes idempotent with a merge on a business key. Log file names and row counts per run. Never reset a bookmark without a written backfill plan."),
        ("Out of memory on large joins",
         "The driver or an executor dies with an out-of-memory error, often on a skewed key such as one huge customer or plant.",
         "Use R worker types or a larger G type for that job only, repartition on the join key, and broadcast the small side. Check the skew in the Spark UI first."),
        ("Slow cold starts and capacity waits",
         "Larger worker types and R types start more slowly, and Flex runs can wait for spare capacity, so a nightly load misses its window.",
         "Use standard execution for jobs with a deadline. Turn on job run queuing so runs wait instead of failing. Alert on time to start, not only on failure."),
        ("Default timeout cuts long jobs",
         "From Glue 5.0 the default timeout is 480 minutes. A job upgraded from 4.0, which defaulted to 2,880 minutes, is stopped mid-run.",
         "Set the timeout explicitly on every job, close to its expected run time plus margin. The maximum is 7 days."),
        ("VPC IP exhaustion",
         "Jobs that join a VPC take one IP address per worker. A busy night with many jobs runs the subnet out of addresses and runs fail.",
         "Give Glue its own large subnets, or a secondary CIDR range. Watch free IP addresses per subnet."),
        ("Logic scattered across scripts",
         "Each job has its own copy of cleaning rules, and nobody can say which rule changed a number.",
         "Treat the migration as the fix: one metadata-driven framework, rules in config, quality results stored with a run id."),
    ],
    "compare": [
        ("Databricks Lakeflow Declarative Pipelines and Jobs",
         "You run Databricks: one engine for batch and streaming, quality rules, lineage and access in Unity Catalog, and serverless compute. This is the reference choice.",
         "The account has no Databricks and the need is a handful of small jobs."),
        ("Amazon EMR (Serverless, on EC2, on EKS)",
         "You need open-source engines beyond Spark, such as Trino, Hive or HBase, or full control of Spark settings and instance types.",
         "You want no cluster or application to manage and a simpler per-job setup."),
        ("Amazon Athena with dbt",
         "The transformations are plain SQL over S3 tables and the team thinks in SQL, not in Spark.",
         "You need Python logic, complex parsing or machine learning steps."),
        ("AWS Lambda",
         "The task is small, event-driven and finishes in well under 15 minutes, such as unzipping one file or calling one API.",
         "The data is large enough to need parallel processing across machines."),
        ("Azure Data Factory data flows or Fabric Spark",
         "Your platform is on Azure; these are the closest equivalents for visual and Spark-based transforms.",
         "Your data and accounts are on AWS."),
    ],
    "cost": {
        "model": ("Glue bills Spark and streaming jobs by DPU-hour, charged per second with a one-minute minimum on current versions. "
                  "The bill for a run is the number of DPUs times the time they ran, so a job with ten G.1X workers for six minutes uses "
                  "one DPU-hour. Flex execution charges a lower rate per DPU-hour for jobs that can wait. Python shell jobs use either "
                  "one-sixteenth of a DPU or one DPU. Interactive sessions are billed the same way while the session is open. The Data "
                  "Catalog and crawlers are billed separately. Check the Glue pricing page for your region's list price."),
        "drivers": [
            "The number and size of workers you request; most jobs are over-provisioned because nobody measures them.",
            "Run time, which grows with skew, small files and full re-reads when bookmarks are not used.",
            "Streaming jobs, which bill every worker for every second because they never stop.",
            "Retries: a job set to retry three times can cost four runs on a bad day.",
            "Crawlers that rescan whole buckets on a schedule.",
        ],
        "traps": [
            "A streaming job left running in a dev account bills all month even with no data arriving.",
            "Interactive sessions left open after a notebook is closed keep billing until their idle timeout.",
            "Large worker types chosen to fix one out-of-memory error, then copied to every job as a template.",
            "Running old and new pipelines in parallel during migration doubles cost for that subject; keep the window to the agreed two weeks.",
            "NAT gateway charges for jobs in a VPC that reach S3 without an S3 gateway endpoint.",
        ],
    },
    "security": [
        "Each job runs as an IAM role. Give each job, or each subject, its own role scoped to its own buckets and prefixes, not one shared role with S3 full access.",
        "Use a Glue security configuration to encrypt job output, CloudWatch logs and job bookmarks with KMS keys you own.",
        "Jobs that reach databases join your VPC through a Glue connection. Keep them in private subnets with no public IP and reach S3, STS and Glue through VPC endpoints.",
        "Store database passwords in Secrets Manager and reference them from the connection; never put them in job parameters, which are visible in the console and logs.",
        "Glue may create a temporary bucket for scripts and temp files that can allow public access; turn on S3 Block Public Access at the account level.",
        "CloudTrail records job creation, changes and runs. Personal data such as customer names should be tokenised before it reaches any Glue output that many people can read.",
    ],
    "monitor": [
        ("Job run state and duration", "Failed, timed-out and unusually long runs; the first sign a source or volume has changed."),
        ("glue.driver.aggregate.numFailedTasks", "Failed Spark tasks within a run that later succeeds; a hint of skew or bad input."),
        ("glue.ALL.jvm.heap.usage", "Memory pressure on the driver and executors before a job dies of out-of-memory."),
        ("glue.driver.ExecutorAllocationManager.executors.numberAllExecutors", "How many executors auto scaling actually used, to right-size the requested workers."),
        ("DPU-hours per job from billing tags", "Cost per job per day, so that the costliest jobs are migrated or tuned first."),
        ("Streaming batch processing time", "For streaming jobs, whether each micro-batch finishes inside its window or falls behind."),
    ],
    "limits": [
        ("Concurrent job runs per account", "2,000 by default per region; adjustable."),
        ("Jobs per account", "2,000 by default per region; adjustable."),
        ("Concurrent DPUs per account", "1,000 in the largest regions and 500 elsewhere, by default; adjustable."),
        ("Job timeout", "Up to 7 days (10,080 minutes); default 480 minutes from Glue 5.0."),
        ("Retries per job", "0 to 10 automatic retries; runs that hit the timeout are not retried."),
        ("Worker type availability", "G.12X, G.16X and R types need Glue 4.0 or later and are only in some regions; Flex supports only G.1X and G.2X."),
    ],
    "decisions": [
        ("New pipeline for plant sensor data on the reference platform",
         "Databricks streaming table on serverless compute",
         "Drop Glue for this: Databricks is the one engine for batch and streaming, with quality and lineage in Unity Catalog."),
        ("200 existing Glue jobs feeding Athena reports",
         "Keep them running; rebuild one subject at a time on Databricks, two-week parallel run, then switch off",
         "Keep if you have it: stable jobs keep the business running while the move happens in measured steps."),
        ("Glue 2.0 jobs still in the account after 1 Apr 2026",
         "They no longer run; move them straight to Databricks rather than upgrading twice",
         "Pursue with care: treat end of life as the migration deadline, and check nothing downstream silently stopped."),
        ("Small API call each night to fetch exchange rates",
         "EventBridge Scheduler and Lambda, or a small Databricks job",
         "Drop Glue Python shell here: a whole job type for one call is more to run than it is worth."),
    ],
    "faq": [
        ("Is AWS Glue being deprecated?",
         "No. Glue ETL is generally available and Glue 6.0 with Spark 4.1.1 is the newest version. What ends are old versions: Glue 0.9, 1.0 and 2.0 Spark jobs reached end of life on 1 April 2026, and Glue for Ray closed to new customers on 30 April 2026."),
        ("Should I use Glue or Databricks for ETL on AWS?",
         "If the platform runs Databricks, use Databricks for new work so that one engine, one catalog and one access model cover everything. Glue fits small, AWS-only needs, and existing Glue jobs can keep running until they are migrated."),
        ("Can Databricks read tables that Glue jobs write?",
         "Yes. Databricks can read Parquet, Iceberg or Delta files in S3, and Unity Catalog can federate the Glue Data Catalog so Glue tables appear during a migration. That makes a side-by-side run straightforward."),
        ("What is the difference between a Glue job and a Glue workflow?",
         "A job is one script that processes data. A workflow is a chain of jobs, crawlers and triggers that run in order. On the reference platform, Lakeflow Jobs replaces workflows, and Glue Workflows are marked Drop."),
        ("How do I make Glue jobs cheaper?",
         "Measure actual executor use and cut the worker count, use Flex for jobs that can wait, use bookmarks so each run reads only new data, stop idle streaming jobs, and add an S3 gateway endpoint so traffic does not pay NAT charges."),
    ],
    "sources": [
        ("AWS docs: Configuring job properties for Spark jobs", "https://docs.aws.amazon.com/glue/latest/dg/add-job.html"),
        ("AWS docs: AWS Glue version support policy", "https://docs.aws.amazon.com/glue/latest/dg/glue-version-support-policy.html"),
        ("AWS docs: AWS Glue for Ray end of support", "https://docs.aws.amazon.com/glue/latest/dg/awsglue-ray-jobs-availability-change.html"),
        ("AWS docs: AWS Glue endpoints and quotas", "https://docs.aws.amazon.com/general/latest/gr/glue.html"),
        ("AWS docs: Python shell jobs in AWS Glue", "https://docs.aws.amazon.com/glue/latest/dg/add-job-python.html"),
        ("AWS: AWS Glue pricing", "https://aws.amazon.com/glue/pricing/"),
    ],
    "related": [
        ("Data platform on AWS and Databricks", "/learn/data-platform-architecture/aws-databricks/"),
        ("Medallion architecture", "/learn/medallion-architecture/"),
        ("AWS Glue Workflows", "svc:glue-workflows"),
        ("AWS Glue Data Catalog", "svc:glue-data-catalog"),
        ("Amazon EMR", "svc:emr"),
        ("Databricks cost calculator", "/learn/data-systems/platform/cost/calculator/"),
    ],
}
