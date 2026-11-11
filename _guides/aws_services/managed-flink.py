SERVICE = {
    "slug": "managed-flink",
    "name": "Amazon Managed Service for Apache Flink",
    "short": "Managed Flink",
    "group": "streaming",
    "one_line": "Runs Apache Flink jobs for you: event-time windows, state and joins over streams, with checkpoints so a restart loses nothing.",
    "status": ("Generally available. Renamed from Amazon Kinesis Data Analytics in August 2023. The older Kinesis Data Analytics "
               "for SQL applications was discontinued: no new applications from 15 Oct 2025, and existing ones deleted from "
               "27 Jan 2026. Flink 2.2 is supported since 31 Mar 2026; Flink 1.6, 1.8 and 1.11 no longer run."),
    "checked": "2026-11-11",
    "site_verdict": ("Pursue",
                     "The processor of the fast lane: it reads plant readings from Kinesis, computes one-minute windows and limit "
                     "breaches in event time, and writes the live store in DynamoDB within seconds. A Lambda function beside it "
                     "handles simple threshold alerts. The platform lane does not use it; Databricks reads Kinesis itself."),
    "equivalents": {"azure": "Azure Stream Analytics, or Confluent Cloud for Apache Flink on Azure",
                    "gcp": "Dataflow (Apache Beam)",
                    "databricks": "Structured Streaming, and real-time mode for sub-second work",
                    "open_source": "Apache Flink on Kubernetes with the Flink Kubernetes Operator"},
    "plain": [
        "Apache Flink is an open-source engine for processing streams of events as they arrive, one event at a time, rather than "
        "in large batches. Its strength is state: it can remember things between events, such as the running average pressure of "
        "a curing press over the last minute, or whether a barcode scan has already arrived for a press cycle that started ten "
        "seconds ago. It keeps that memory safe by taking checkpoints, which are regular snapshots of all its state written to "
        "durable storage, so that after a crash it resumes exactly where it stopped.",
        "Amazon Managed Service for Apache Flink runs Flink for you. You upload your application, written in Java, Python or "
        "Flink SQL, and choose how much capacity it gets. AWS starts the cluster, stores checkpoints, restarts the job when a "
        "machine fails, and scales the job if you allow it. You never patch a server. Until August 2023 the same service was "
        "called Amazon Kinesis Data Analytics, which is why many older articles and some API names still use that name.",
        "A concrete example: a tyre plant has 2,000 curing presses, each sending twenty signals every five seconds. Operators want "
        "a screen that turns red within seconds when a press runs too hot for longer than thirty seconds, and supervisors want "
        "one-minute averages per press. A Flink job reads the readings from Kinesis Data Streams, groups them by press, waits a "
        "short time for late readings using a watermark, computes one-minute windows, compares them with the limits for the "
        "current recipe, and writes both the latest values and any alert into DynamoDB. From there the change is pushed to the "
        "screen.",
        "What makes this hard without Flink is event time. Readings do not arrive in perfect order: a gateway may buffer for a few "
        "seconds, or a network blip may delay a batch. Flink sorts this out by the time the reading was taken, not the time it "
        "arrived, so a one-minute window means the right minute even when data is late.",
    ],
    "analogy": "A quality inspector standing at the conveyor with a notebook, who remembers what came past in the last minute and photographs the notebook every few seconds in case they faint.",
    "big_picture": [
        "On the reference platform Flink lives only in the fast lane, the path that puts plant readings and alerts on screens within "
        "one to three seconds. Readings flow from the plant gateway into Kinesis Data Streams, Flink reads them, and its output "
        "goes to a small live store in DynamoDB. DynamoDB Streams then hands each change to a Lambda function that pushes it to "
        "browsers through an API Gateway WebSocket, or through AppSync Events. The site estimates this whole lane at roughly "
        "530 dollars a month, of which Flink with three processing units is about 250 dollars (list price, check your region).",
        "The platform lane, which builds bronze, silver and gold tables in Databricks every fifteen minutes, deliberately does not "
        "read Flink's output. It reads the same raw stream from Kinesis itself, so a bug in the fast lane can never corrupt the "
        "numbers of record. The only things Flink sends to the lake are facts it creates: alerts raised and acknowledged, and "
        "one-minute service-level summaries, which go through Firehose into bronze as their own dataset.",
        "Reference data travels the other way. Limits per recipe and the press master list are published from silver or gold every "
        "fifteen minutes or daily into DynamoDB or into Flink broadcast state, so the fast lane has its own copy and never calls "
        "the platform while running. Simple limit checks that need no memory, such as pressure above a fixed maximum, can run in "
        "a Lambda function reading Kinesis beside Flink, which is nearly free.",
        "Databricks real-time mode is the main rival. It would let one engine, Spark, serve both lanes. The site currently says "
        "Drop for now and revisit if the team wants one engine, because it needs a fixed always-on cluster and costs more than "
        "Flink for a small plant stream.",
    ],
    "upstream": ["svc:kinesis-data-streams", "svc:msk", "svc:dynamodb-streams"],
    "downstream": ["svc:dynamodb", "svc:data-firehose", "svc:kinesis-data-streams"],
    "concepts": [
        ("Kinesis processing unit (KPU)", "The unit of capacity and billing: one virtual CPU, 4 GiB of memory and 50 GiB of running application storage."),
        ("Parallelism", "How many copies of each step run at once. Total parallelism divided by parallelism per KPU decides how many KPUs you pay for."),
        ("Checkpoint", "An automatic, regular snapshot of the job's state and its read positions, used to recover after a failure without losing or repeating results."),
        ("Snapshot", "A checkpoint you keep on purpose, taken when you stop or update the application, so a new version can start from the old state."),
        ("Event time and watermark", "Event time is when a reading was taken. A watermark is Flink's statement that no reading older than a certain time is still expected, which lets windows close."),
        ("Window", "A slice of the stream grouped by time, such as every minute per press, over which Flink computes counts, averages or maximums."),
        ("Keyed state", "Memory Flink keeps per key, for example per press, stored in RocksDB on local disk and included in every checkpoint."),
        ("Back pressure", "When a later step or the sink cannot keep up, earlier steps slow down; latency grows until the bottleneck is fixed."),
        ("Broadcast state", "A small table, such as limits per recipe, copied to every parallel worker so each event can be checked without a remote lookup."),
    ],
    "use_when": [
        "You need time windows, running aggregates or pattern detection over a stream, with results in seconds rather than minutes.",
        "You must join two streams within a time bound, for example a press cycle start and the barcode scan that should follow it.",
        "You need correct results when events arrive late or out of order, which calls for event time and watermarks.",
        "You want exactly-once results into a sink that supports it, backed by checkpoints, without running a Flink cluster yourself.",
        "Your stream already lives in Kinesis or MSK and your team can write Java, Python or Flink SQL.",
    ],
    "avoid_when": [
        "The logic is a stateless check on each event, such as a single threshold; a Lambda function reading Kinesis is simpler and costs almost nothing.",
        "The result only needs to be fresh within fifteen minutes or an hour; a Databricks streaming table run on a schedule is cheaper and keeps one engine.",
        "Nobody on the team can support a Flink job; an always-on stateful service needs someone who understands checkpoints and back pressure.",
        "You want to write Delta tables governed by Unity Catalog as the main output; Databricks itself does that better.",
    ],
    "challenges": [
        ("Checkpoints get slower and then fail",
         "State grows over time, often because a window has no end or a join has no time-to-live, and each checkpoint takes longer until it times out and the job restarts in a loop.",
         "Set time-to-live on state, bound every join with time, watch lastCheckpointDuration and lastCheckpointSize, and alarm before checkpoints approach the timeout."),
        ("Back pressure from the sink",
         "DynamoDB throttles or a slow HTTP call blocks the job, so readers fall behind and alerts arrive late.",
         "Write only changes, not every reading; batch writes; use async I/O for lookups; watch backPressuredTimeMsPerSecond and DynamoDB throttles together."),
        ("Late or silent sources",
         "One plant gateway stops sending, the watermark stops advancing, and windows for every press never close.",
         "Configure idle-source handling for watermarks, and add a heartbeat per plant so a silent source raises its own alert."),
        ("Upgrades that break state",
         "A code change renames an operator or changes a state type, and the new version cannot restore the old snapshot.",
         "Give every operator a fixed id, test restores from a production snapshot in a lower environment, and keep the previous version ready to roll back."),
        ("Flink 2.x migration",
         "Flink 2.2 is a major version with breaking changes: Java 17 only, older APIs removed, and some connectors such as JDBC and OpenSearch had no 2.x release at launch.",
         "Check every connector you use for a 2.x release before upgrading, follow the AWS upgrade guide, and test state compatibility on a copy."),
        ("Paying for idle capacity",
         "You pay for allocated KPUs every hour, plus one extra KPU per application for orchestration, even when the plant is quiet at night.",
         "Right-size parallelism from measured CPU and back pressure, enable autoscaling with care, and merge small jobs where it is safe."),
        ("Restart storms",
         "A poison record, such as a malformed reading, throws an error on every attempt and the job restarts again and again.",
         "Catch parse errors and send bad records to a side output stored in S3, and alarm on fullRestarts and downtime."),
    ],
    "compare": [
        ("AWS Lambda reading Kinesis", "The rule is stateless, such as one fixed limit per reading, and you want almost no cost or code.", "You need windows, joins, late-event handling or exactly-once state."),
        ("Databricks Structured Streaming and real-time mode", "You want one engine and one governed platform for both lanes and accept a fixed always-on cluster.", "You want the cheapest true push lane in seconds; Flink with DynamoDB costs less today."),
        ("AWS Glue streaming jobs", "You already run Glue Spark jobs and need minute-level micro-batches.", "You need second-level latency or rich event-time state; the site drops Glue streaming for both lanes."),
        ("Self-managed Flink on Amazon EKS", "You need versions, connectors or tuning the managed service does not offer, and have a platform team.", "You do not want to operate Flink upgrades, high availability and checkpoint storage yourself."),
        ("Azure Stream Analytics, or Confluent Flink on Azure", "The platform is on Azure; Stream Analytics is SQL only and simpler.", "You are on AWS, or need full Flink APIs; Stream Analytics is less flexible."),
        ("Google Cloud Dataflow", "The platform is on Google Cloud and you like Apache Beam's model.", "You are on AWS; Beam code can run on Flink, but the operations differ."),
    ],
    "cost": {
        "model": ("You pay an hourly rate for each KPU allocated to the application, plus one extra KPU per application for "
                  "orchestration. Running application storage is billed per GB-month (50 GB comes with each KPU) and durable "
                  "backups, meaning snapshots you keep, are billed per GB-month too. The site uses about 80 dollars a month per KPU "
                  "as a rough figure, so a small job with two working KPUs plus orchestration is about 250 dollars a month (list "
                  "price, check your region). Data transfer and the services Flink reads and writes, such as Kinesis and DynamoDB, "
                  "are billed separately."),
        "drivers": [
            "Number of KPUs, which follows from parallelism and how many parallel tasks share one KPU.",
            "Number of applications, because each one carries its own orchestration KPU.",
            "State size, which drives storage, checkpoint time and sometimes the need for more memory.",
            "Writes to the sink; writing every reading into DynamoDB instead of only changes multiplies the sink bill.",
        ],
        "traps": [
            "Autoscaling scales up on high CPU but can leave you at the higher size for a long time; check the KPUs metric weekly.",
            "Many tiny applications each pay the orchestration KPU; one job with several outputs is often cheaper.",
            "Development and test applications left running around the clock cost the same as production.",
            "Kept snapshots accumulate; set a retention policy for old snapshots.",
        ],
    },
    "security": [
        "The application runs with an IAM service execution role; grant it read on the one Kinesis stream and write on the one DynamoDB table, nothing wider.",
        "Attach the application to private subnets in your VPC so it reaches Kinesis, DynamoDB and S3 through VPC endpoints, with no public internet path.",
        "Checkpoints and snapshots are encrypted by the service; application code and dependencies in S3 should sit in an encrypted bucket with the platform KMS key.",
        "Keep secrets such as database passwords in Secrets Manager and read them at start-up; never put them in runtime properties in plain text.",
        "Control-plane calls such as UpdateApplication and StopApplication are logged in CloudTrail, which shows who changed or stopped the job.",
        "Readings are usually not personal data, but connected-product streams can carry vehicle or customer ids; drop or hash them before the live store if screens do not need them.",
    ],
    "monitor": [
        ("millisBehindLatest", "How far the Kinesis source is behind the newest record; the first sign the job cannot keep up."),
        ("lastCheckpointDuration and lastCheckpointSize", "How long the last checkpoint took and how big state is; a steady climb predicts failures."),
        ("numberOfFailedCheckpoints", "Checkpoints that did not complete; any non-zero trend needs attention."),
        ("fullRestarts and downtime", "How often the job restarted and how long it was down; restart storms show here first."),
        ("backPressuredTimeMsPerSecond", "Time each task spends waiting for the next step; points at the slow operator or sink."),
        ("KPUs and containerCPUUtilization", "Allocated capacity and how busy it is; the basis for right-sizing and cost."),
        ("heapMemoryUtilization", "Memory pressure on the workers; high values precede out-of-memory restarts."),
    ],
    "limits": [
        ("KPU size", "1 vCPU, 4 GiB memory and 50 GiB running application storage per KPU"),
        ("KPUs", "64 by default; raise with a quota request naming the application"),
        ("Applications", "100 per Region per account by default"),
        ("Snapshots", "Up to 1,000 per application"),
        ("Application JAR", "512 MiB maximum"),
    ],
    "decisions": [
        ("Live board for 2,000 presses, alerts within 5 seconds, one-minute windows", "Managed Flink reading Kinesis, writing changes to DynamoDB", "Pursue: windows, late events and state in seconds, at about 250 dollars a month for the job."),
        ("Only fixed threshold alerts, no windows", "Lambda reading Kinesis, with SNS for alerts", "Pursue: nearly free and enough; add Flink when windows or drift detection appear."),
        ("Team wants one engine for both lanes", "Databricks real-time mode instead of Flink", "Keep if you have it: Flink stays the default; revisit real-time mode when one engine is worth the higher fixed cost."),
        ("Applications still on Kinesis Data Analytics for SQL", "Rewrite in Flink SQL on Managed Flink", "Drop: the SQL applications were deleted from 27 Jan 2026; anything left must be rebuilt."),
        ("Job on Flink 1.20 with the JDBC connector", "Stay on 1.20 until the connector has a 2.x release", "Pursue with care: upgrade to 2.2 only after every connector is ready and state restore is tested."),
    ],
    "faq": [
        ("Is Managed Service for Apache Flink the same as Kinesis Data Analytics?",
         "Yes. AWS renamed Kinesis Data Analytics for Apache Flink to Managed Service for Apache Flink in August 2023. The separate Kinesis Data Analytics for SQL applications was discontinued, and its applications were deleted from 27 January 2026."),
        ("Which Flink versions does it support?",
         "The newest is Flink 2.2, supported since 31 March 2026, alongside recent 1.x versions. Flink 2.2 needs Java 17 and some connectors lacked 2.x releases at launch, so check yours before upgrading."),
        ("When should I use Lambda instead of Flink for Kinesis?",
         "Use Lambda when each record can be judged alone, such as one fixed limit. Use Flink when you need windows, joins, late-event handling or state across many records."),
        ("How much does a small Flink job cost?",
         "Roughly 80 dollars a month per KPU plus one orchestration KPU per application, so a small job is about 160 to 400 dollars a month. These are rough list prices; check your region and measure."),
        ("Can Flink write Delta tables for Databricks?",
         "It can with the Delta connector, but the reference platform does not do that. Databricks reads the raw stream from Kinesis itself, and Flink sends only alerts and summaries to bronze through Firehose."),
    ],
    "sources": [
        ("AWS docs: Managed Service for Apache Flink quotas", "https://docs.aws.amazon.com/managed-flink/latest/java/limits.html"),
        ("AWS What's New: Managed Service for Apache Flink supports Flink 2.2", "https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-managed-service-flink-2-2"),
        ("AWS docs: Flink 2.2 on Managed Service for Apache Flink", "https://docs.aws.amazon.com/managed-flink/latest/java/flink-2-2.html"),
        ("AWS docs: Kinesis Data Analytics for SQL discontinuation", "https://docs.aws.amazon.com/kinesisanalytics/latest/dev/troubleshooting.html"),
        ("AWS pricing: Managed Service for Apache Flink", "https://aws.amazon.com/managed-service-apache-flink/pricing/"),
    ],
    "related": [
        ("Streaming on AWS and Databricks", "/learn/streaming/"),
        ("Every streaming option", "/learn/streaming/options/"),
        ("Databricks real-time mode", "/learn/streaming/real-time-mode/"),
        ("Real-time analytics", "/learn/real-time-analytics/"),
        ("Amazon Kinesis Data Streams", "svc:kinesis-data-streams"),
        ("Amazon DynamoDB", "svc:dynamodb"),
    ],
}
