SERVICE = {
    "slug": "emr",
    "name": "Amazon EMR (on EC2, Serverless, on EKS)",
    "short": "Amazon EMR",
    "group": "processing",
    "one_line": "AWS's managed big-data service for Spark, Hive, Trino, Flink and HBase, run on your own clusters, serverless, or on Kubernetes.",
    "status": ("Generally available in three deployment modes. Release 7.14.0 is the latest of the 7.x line (Spark 3.5). "
               "A separate line, the AWS runtime for Apache Spark (emr-spark-8.0.0 from May 2026, then 8.1.0 with Spark 4.1.1), "
               "carries Spark 4 on all three modes."),
    "checked": "2026-11-11",
    "site_verdict": ("Keep if you have it",
                     "Databricks is the one engine for batch and streaming on this platform, so new pipelines do not go on EMR. Existing "
                     "EMR workloads keep running until each subject is rebuilt and reconciled on Databricks, and EMR stays only for "
                     "open-source engines Databricks does not run, such as HBase or a Trino cluster a team depends on."),
    "equivalents": {"azure": "Azure HDInsight, Fabric Spark", "gcp": "Dataproc (clusters and Serverless)",
                    "databricks": "Databricks classic and serverless compute", "open_source": "Apache Spark, Hive, Trino on your own Hadoop or Kubernetes"},
    "plain": [
        "Amazon EMR runs open-source big-data engines for you. The main one is Apache Spark, which splits a large dataset into many pieces "
        "and processes them in parallel across machines. EMR also runs Hive for SQL over files, Trino and Presto for fast interactive SQL, "
        "Flink for streams, and HBase as a wide-column database. AWS packages tested versions of these engines into a release, installs "
        "them, and connects them to S3, IAM and CloudWatch.",
        "EMR comes in three forms. EMR on EC2 builds a cluster of virtual machines in your account; you pick the instance types, how many, "
        "and whether some are Spot instances, which are spare capacity sold at a deep discount that AWS can take back. EMR Serverless has "
        "no cluster: you create an application, submit jobs, and EMR finds the workers and releases them when the job ends. EMR on EKS runs "
        "Spark jobs as pods on a Kubernetes cluster you already run on Amazon EKS.",
        "A concrete example. A manufacturer collects vibration and temperature readings from presses in five plants, about two billion rows "
        "a day, landed in S3 as Parquet. Every night an EMR Serverless Spark job reads the day's readings, joins them to the machine master "
        "from SAP, computes hourly averages and alarms per press, and writes the result as Iceberg tables. Analysts query them with Athena. "
        "The job uses about 400 vCPUs for 40 minutes and then nothing until the next night.",
    ],
    "analogy": "A rental workshop fully stocked with open-source tools; you can rent the whole building, a bench by the hour, or a corner of a workshop you already own.",
    "big_picture": [
        "EMR sits in the processing lane, the same place as Glue and Databricks. In a classic AWS lake, movers drop files into S3 landing, "
        "EMR Spark jobs build bronze, silver and gold, the Glue Data Catalog holds the table definitions, and Athena, Redshift or "
        "QuickSight read the results. Orchestration is usually Step Functions or Airflow on MWAA.",
        "On this site's reference platform, Databricks does the processing, with Unity Catalog for access, lineage and audit, and Lakeflow "
        "Jobs for orchestration. One engine for batch and streaming means one set of quality rules, one lineage graph and one bill per data "
        "product. Adding EMR next to it would bring a second Spark, a second catalog path and a second set of clusters to tune, so new work "
        "does not go there.",
        "Two places where EMR stays. Existing EMR pipelines keep running while each subject is rebuilt as a Databricks pipeline, runs in "
        "parallel for two weeks, reconciles counts and sums, and is switched off. And some open-source engines have no place in Databricks: "
        "an HBase store behind an application, or a Trino cluster that another team uses as a query layer over many sources. Those can stay "
        "on EMR, reading the platform's tables as Iceberg through UniForm.",
    ],
    "upstream": ["svc:s3", "svc:kinesis-data-streams", "svc:msk"],
    "downstream": ["svc:s3", "svc:glue-data-catalog", "svc:athena"],
    "concepts": [
        ("Release", "A numbered bundle of engine versions, such as emr-7.14.0 with Spark 3.5. Each release has a support end date; the newer emr-spark-8.x line carries Spark 4."),
        ("Primary, core and task nodes", "On EMR on EC2, the primary node runs the cluster managers, core nodes run work and hold HDFS data, and task nodes only run work, which makes them safe for Spot."),
        ("Instance fleet", "A way to list several instance types and purchase options for each node group, so EMR can find capacity across types and Availability Zones."),
        ("Managed scaling", "EMR adds and removes nodes on an EC2 cluster based on the workload, between a minimum and maximum you set."),
        ("EMR Serverless application", "A named, versioned Spark or Hive environment that jobs are submitted to. It starts workers per job, and can keep some pre-initialised to cut start time."),
        ("Virtual cluster", "On EMR on EKS, a link between EMR and one Kubernetes namespace, so Spark jobs run as pods beside other workloads."),
        ("EMRFS and S3", "EMR reads and writes S3 directly as its main storage, so clusters can be short-lived and the data outlives them."),
        ("Runtime role", "An IAM role passed with each job or step, so different teams on one cluster only see their own data."),
    ],
    "use_when": [
        "You already run EMR pipelines that work and plan to migrate them to Databricks one subject at a time.",
        "You need an open-source engine that Databricks does not offer, such as HBase, Hive LLAP or a long-running Trino cluster.",
        "A team runs everything on Kubernetes and wants Spark jobs to share an existing EKS cluster through EMR on EKS.",
        "A platform without Databricks needs Spark with full control over versions, configuration and instance types.",
        "You need very large, steady batch jobs where tuned Spot fleets on EC2 make the bill noticeably lower, and the team can operate them.",
    ],
    "avoid_when": [
        "Avoid EMR for new pipelines on this platform; Databricks already provides the engine, catalog, quality rules and orchestration.",
        "Avoid long-running EMR on EC2 clusters that sit mostly idle; you pay for every instance-second whether or not jobs run.",
        "Avoid EMR on EKS unless you already run EKS well; it adds Kubernetes skills on top of Spark skills.",
        "Avoid putting HDFS on core nodes as the main store; when the cluster ends or a node fails, that data is at risk.",
        "Avoid two catalogs with two access models; if EMR must read platform tables, read them as Iceberg with clear, narrow permissions.",
    ],
    "challenges": [
        ("Spot interruptions",
         "AWS reclaims Spot instances. If core nodes or the primary node are Spot, the cluster or its HDFS data can be lost mid-run.",
         "Keep the primary and core nodes On-Demand; put Spot only on task nodes; use instance fleets with many instance types across zones."),
        ("Idle clusters",
         "A cluster created for a nightly job is left running all day, or an interactive cluster is forgotten over a weekend.",
         "Use transient clusters that end after their steps, set an idle auto-termination, or move the job to EMR Serverless."),
        ("Release end of support",
         "Old releases stop getting patches, and old Spark versions stop matching new connectors and table formats.",
         "Track releases per cluster and application. Upgrade with a parallel run, or treat the date as the migration deadline to Databricks."),
        ("Serverless quota surprises",
         "A new account starts at 16 concurrent vCPUs for EMR Serverless; a big job queues or fails on its first day.",
         "Request a higher Max concurrent vCPUs per account quota before go-live and set a maximum capacity per application."),
        ("Shuffle and skew",
         "One key, such as one very busy press, holds most of the rows; one task runs for an hour while others finish in a minute.",
         "Look at the Spark UI first. Turn on adaptive query execution, salt hot keys, and size shuffle storage for Serverless jobs."),
        ("Configuration drift between clusters",
         "Each cluster was launched by hand with slightly different settings, so the same job behaves differently in dev and prod.",
         "Define clusters and applications as code with CloudFormation, CDK or Terraform, and pin the release label."),
        ("Many small files",
         "Jobs write thousands of tiny files, and readers slow down.",
         "Write Iceberg tables and run compaction, or coalesce before writing."),
    ],
    "compare": [
        ("Databricks jobs and Lakeflow Declarative Pipelines",
         "You run Databricks: one engine for batch and streaming, Unity Catalog for access and lineage, serverless compute. This is the reference choice.",
         "You need an open-source engine Databricks does not run, or the work is an existing EMR pipeline awaiting migration."),
        ("AWS Glue ETL jobs",
         "You want serverless Spark with the least setup for a few jobs and no tuning.",
         "You need other engines, Spot fleets, custom images or fine control of Spark."),
        ("Amazon Athena",
         "The work is SQL over S3 and you want to pay per query with nothing to run.",
         "You need Python, heavy joins over billions of rows, or long-running jobs."),
        ("Azure HDInsight or Fabric Spark",
         "Your platform is on Azure; these are the closest equivalents there.",
         "Your data and accounts are on AWS."),
        ("Google Dataproc",
         "Your platform is on Google Cloud; Dataproc offers clusters and serverless Spark there.",
         "Your data and accounts are on AWS."),
    ],
    "cost": {
        "model": ("EMR charges per second with a one-minute minimum. On EC2 you pay the EC2 instance price, EBS storage and an EMR fee "
                  "per instance-hour on top, and the EMR fee differs by instance type. Spot instances cut the EC2 part by up to 90 percent "
                  "against On-Demand, at the risk of interruption. EMR Serverless bills vCPU-hours, GB-hours of memory and extra storage "
                  "for the time workers run. EMR on EKS adds an EMR fee per vCPU and GB to the cost of the EKS nodes. Check the EMR pricing "
                  "page for list prices in your region."),
        "drivers": [
            "Instance hours on EMR on EC2, including idle time between jobs and while clusters start.",
            "The share of Spot versus On-Demand, and whether Savings Plans cover the steady part.",
            "vCPU and memory per worker on Serverless, which is often set too high and never measured.",
            "Shuffle-heavy jobs that need more disk and longer run time.",
            "NAT gateway traffic when clusters in private subnets reach S3 without a gateway endpoint.",
        ],
        "traps": [
            "Clusters left running with no auto-termination.",
            "Pre-initialised capacity on Serverless applications that keeps warm workers billing all day.",
            "Running old EMR and new Databricks pipelines in parallel for longer than the agreed two weeks.",
            "Comparing only the EMR fee with a Databricks DBU price, without the EC2, idle and operations time behind each.",
        ],
    },
    "security": [
        "Give each cluster an EC2 instance profile with narrow S3 access, and use runtime roles so each job or step runs with its own IAM role.",
        "Use an EMR security configuration to turn on encryption at rest for S3 and local disks and in-transit encryption between nodes, with KMS keys you own.",
        "Launch clusters in private subnets with no public IPs; reach S3, STS and other AWS services through VPC endpoints. EMR Serverless can attach to your VPC for private sources.",
        "Use Lake Formation or Apache Ranger integration only if EMR must enforce table and column permissions; avoid running that alongside Unity Catalog grants for the same tables.",
        "CloudTrail logs EMR API calls; turn on S3 logging of step and application logs, and keep personal data tokenised before it reaches EMR outputs.",
    ],
    "monitor": [
        ("IsIdle", "EMR on EC2 metric that shows a cluster doing no work; alert to catch forgotten clusters."),
        ("YARNMemoryAvailablePercentage", "Free memory in the cluster; low values mean jobs are waiting for resources."),
        ("AppsPending", "Applications waiting for capacity, a sign the cluster is too small or managed scaling is capped."),
        ("Job run state on EMR Serverless", "Failed, cancelled and long runs per application, from the job run events in EventBridge."),
        ("Service quota usage in AWS/Usage", "Concurrent vCPUs used against the Serverless account quota."),
        ("Spot interruption notices", "How often task nodes are reclaimed, to widen instance fleets or change the Spot share."),
    ],
    "limits": [
        ("EMR Serverless concurrent vCPUs", "16 per account per region by default for new accounts; adjustable and raised automatically with use."),
        ("Instance fleet types", "Up to 5 instance types per fleet by default; up to 30 with an allocation strategy set through the CLI or API."),
        ("Instances per fleet", "Up to 4,000 EC2 instances per fleet with an allocation strategy on emr-7.7.0 and later."),
        ("Latest 7.x release", "emr-7.14.0, with standard support until September 2028."),
        ("Spark 4 releases", "emr-spark-8.0.0 (Spark 4.0.2) and emr-spark-8.1.0 (Spark 4.1.1), on EC2, Serverless and EKS."),
    ],
    "decisions": [
        ("New silver and gold pipelines for plant sensor data",
         "Databricks pipelines on serverless compute",
         "Drop EMR for this: one engine for batch and streaming, with lineage and quality in Unity Catalog."),
        ("Forty existing EMR Spark jobs feeding warehouse loads",
         "Keep them running; rebuild one subject at a time on Databricks, two-week parallel run, then switch off",
         "Keep if you have it: stable jobs keep running while the move happens in measured steps."),
        ("An HBase store that serves a product-lookup application",
         "Keep it on EMR, reading platform tables as Iceberg where needed",
         "Keep if you have it: Databricks does not run HBase, and moving the application is a separate decision."),
        ("A team wants Spark on its existing EKS cluster for experiments",
         "EMR on EKS in its own namespace, with platform tables read-only",
         "Pursue with care: fine for experiments, but production data products still go through Databricks."),
    ],
    "faq": [
        ("What is the difference between EMR on EC2, EMR Serverless and EMR on EKS?",
         "EMR on EC2 gives you a cluster of virtual machines you size and pay for while it runs. EMR Serverless has no cluster; you submit jobs and pay for the workers each job uses. EMR on EKS runs Spark jobs as pods on a Kubernetes cluster you already operate."),
        ("Is EMR cheaper than Databricks?",
         "Per hour of machine, EMR on EC2 with Spot can look cheaper. The full comparison must include idle clusters, start-up time, the people who tune and patch them, and the governance, lineage and quality features you would rebuild. Measure a real pipeline both ways before deciding."),
        ("Does EMR support Spark 4?",
         "Yes, through the AWS runtime for Apache Spark line: emr-spark-8.0.0 brought Spark 4.0.2 in May 2026, and emr-spark-8.1.0 carries Spark 4.1.1. The emr-7.x line stays on Spark 3.5."),
        ("Can EMR read Delta tables written by Databricks?",
         "EMR includes Delta Lake and Iceberg libraries. On the reference platform the simpler path is UniForm, which lets Delta tables be read as Iceberg, with read-only access granted to the EMR role."),
        ("Should I use Spot instances on EMR?",
         "Yes for task nodes on fault-tolerant batch jobs, using instance fleets with several instance types. Keep the primary and core nodes On-Demand so an interruption does not kill the cluster or lose data."),
    ],
    "sources": [
        ("AWS docs: What's new in Amazon EMR", "https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-whatsnew.html"),
        ("AWS docs: Amazon EMR release 7.14.0", "https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-7140-release.html"),
        ("AWS docs: AWS runtime for Apache Spark (emr-spark-8.0.0)", "https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-spark800-release.html"),
        ("AWS docs: EMR Serverless endpoints and quotas", "https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/endpoints-quotas.html"),
        ("AWS docs: Planning instance fleets", "https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-instance-fleet.html"),
        ("AWS: Amazon EMR pricing", "https://aws.amazon.com/emr/pricing/"),
    ],
    "related": [
        ("Data platform on AWS and Databricks", "/learn/data-platform-architecture/aws-databricks/"),
        ("AWS Glue ETL jobs", "svc:glue-etl"),
        ("Amazon EC2 for Databricks", "svc:ec2"),
        ("Amazon EKS", "svc:eks"),
        ("Delta vs Iceberg", "/learn/delta-vs-iceberg/"),
        ("Databricks cost calculator", "/learn/data-systems/platform/cost/calculator/"),
    ],
}
