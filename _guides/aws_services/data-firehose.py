SERVICE = {
    "slug": "data-firehose",
    "name": "Amazon Data Firehose",
    "short": "Data Firehose",
    "group": "streaming",
    "one_line": "A serverless delivery pipe that buffers records for a minute or more and writes them as files or table rows into S3 and other stores.",
    "status": ("Generally available. Renamed from Amazon Kinesis Data Firehose in February 2024; the API is still called "
               "firehose and streams are still DeliveryStream in the API. The database change capture source shown in preview "
               "ended its preview on 30 Sep 2025 and can no longer be used; no general availability has been announced."),
    "checked": "2026-11-11",
    "site_verdict": ("Pursue",
                     "The cheap way to turn records into files for sources that need minutes, not seconds: CloudWatch metric streams, "
                     "app events, webhooks from EventBridge and the fast lane's own alert events all land in S3 through Firehose and "
                     "reach bronze through Auto Loader. It is also the fallback if the Databricks Kinesis source falls short, and the "
                     "lake writer on an AWS-only platform."),
    "equivalents": {"azure": "Event Hubs Capture (or Stream Analytics)", "gcp": "Pub/Sub BigQuery and Cloud Storage subscriptions",
                    "databricks": "Auto Loader reads what Firehose writes; Zerobus Ingest for single-reader app streams",
                    "open_source": "Kafka Connect S3 sink, or Vector and Fluent Bit"},
    "plain": [
        "Amazon Data Firehose is a delivery service. You send it records, and it gathers them in a buffer until either a size or a "
        "time limit is reached, for example 64 MB or 60 seconds, then writes the whole buffer as one file or one batch into a "
        "destination. The main destinations are Amazon S3, Apache Iceberg tables (including S3 Tables), Redshift, OpenSearch, "
        "Snowflake, Splunk and plain HTTP endpoints. There are no servers, shards or clusters to size: you create a Firehose stream, "
        "point it at a destination, and it scales with the traffic.",
        "On the way, Firehose can do small, useful jobs. It can convert JSON into Parquet or ORC using a table definition in the Glue "
        "Data Catalog, compress files with GZIP, Snappy or ZSTD, call a Lambda function to fix or enrich each record, and split "
        "output into S3 folders by a field in the data, which AWS calls dynamic partitioning. Records that fail are written to an "
        "error folder rather than lost.",
        "Its source is either Direct PUT, where an app or AWS service calls the Firehose API, or a Kinesis data stream or MSK "
        "topic it reads from. A concrete example: a retail chain's dealer portal emits click and order events through API Gateway "
        "into Firehose. Firehose buffers for 60 seconds, writes one compressed Parquet file to the landing bucket, and Auto Loader "
        "picks up each new file into a bronze table a minute or two later. Nobody needed those clicks within seconds, so there is no "
        "stream to run.",
    ],
    "analogy": "A post room that collects letters in a sack and sends the full sack to the right building every minute, rather than running each letter across separately.",
    "big_picture": [
        "On the reference platform Firehose sits in the move-in lane as the file-maker. It turns a flow of records into files in "
        "the S3 landing bucket, and from there the platform's single lander, Auto Loader, brings them into bronze. The site's "
        "rule is simple: Kinesis is for records that need seconds and several readers; Firehose and S3 are for records that only "
        "need minutes. The streaming guide calls this streaming over files, with a delay of one to three minutes.",
        "Several sources feed it. A CloudWatch metric stream sends DMS, AppFlow, Kinesis and SiteWise health metrics through "
        "Firehose into S3, where the operations tables pick them up every five minutes. CloudWatch Logs subscriptions do the same "
        "for application logs. EventBridge sends SaaS webhooks and alarm state changes to Firehose. The fast lane writes the alerts "
        "it raises, a new fact the platform must keep, through Firehose into bronze. App events go through API Gateway into Firehose "
        "unless a live use appears.",
        "Firehose also has two backup roles. If the Databricks Kinesis source does not suit a stream, Firehose can read that Kinesis "
        "stream and write Parquet files for Auto Loader instead. And on an AWS-only version of the platform, Firehose writes the "
        "stream straight into Iceberg tables on S3 Tables, which Athena and Redshift read.",
    ],
    "upstream": ["svc:cloudwatch", "svc:eventbridge", "svc:kinesis-data-streams"],
    "downstream": ["svc:s3", "Databricks Auto Loader into bronze", "svc:s3-tables"],
    "concepts": [
        ("Firehose stream", "One delivery pipe from one source to one destination; called a delivery stream in older documents and in the API."),
        ("Direct PUT", "The source type where producers call PutRecord or PutRecordBatch on Firehose itself, rather than Firehose reading a stream."),
        ("Buffer hints", "The size and time limits that decide when Firehose writes a file, for example 64 MB or 60 seconds, whichever comes first."),
        ("Record format conversion", "Turning incoming JSON into Parquet or ORC using a schema stored in the Glue Data Catalog."),
        ("Dynamic partitioning", "Writing records into S3 folders named after a field inside them, such as plant or date, rather than only by arrival time."),
        ("Data transformation", "A Lambda function Firehose calls on each batch to clean, filter or enrich records before delivery."),
        ("Error output prefix", "The S3 folder where Firehose writes records it could not convert or deliver, so they can be fixed and replayed."),
        ("Apache Iceberg destination", "Firehose writing rows into Iceberg tables in S3 or S3 Tables, with optional routing to different tables and support for updates and deletes."),
    ],
    "use_when": [
        "Use it when data only needs to land within one to fifteen minutes and has a single destination, such as logs, metrics or app events.",
        "Use it when you want files of a sensible size in S3 rather than thousands of tiny objects written by each producer.",
        "Use it to land CloudWatch metric streams, CloudWatch Logs and EventBridge events in the lake with almost no code.",
        "Use it on an AWS-only platform to write a stream into Iceberg tables in S3 Tables for Athena and Redshift.",
        "Use it as the fallback reader of a Kinesis stream when a direct Databricks Kinesis read is not workable.",
    ],
    "avoid_when": [
        "Avoid it when someone acts on the data within seconds; its minimum buffer interval of 60 seconds for S3 rules that out.",
        "Avoid it as the only copy when several readers need the same events or replay; put Kinesis or MSK in front.",
        "Avoid it for heavy transformations, joins or windows; that work belongs in Flink or Databricks, not in a Lambda inside Firehose.",
        "Avoid planning on it for database change capture; that preview ended in 2025 with no general release, and DMS is the site's choice.",
    ],
    "challenges": [
        ("Small files", "A low-volume stream with a 60-second buffer writes one small file a minute per partition, which slows Auto Loader and queries.",
         "Raise the buffer size and interval where minutes are acceptable; partition by date, not by many keys; let Delta optimize or Iceberg compaction tidy bronze."),
        ("Throttled Direct PUT", "Outside the three largest Regions a Direct PUT stream starts at 1 MiB a second, 1,000 requests and 100,000 records a second; bursts are throttled.",
         "Batch with PutRecordBatch, retry failed records, request a higher limit before launch, or put Kinesis in front, which has no such limit for Firehose."),
        ("Silent conversion failures", "Records that do not match the Glue schema go to the error prefix, and nobody notices until a report is short.",
         "Alarm on the error prefix having new objects and on failed conversion metrics; land raw JSON when schemas change often."),
        ("Duplicates", "Firehose retries deliveries, so the same records can appear in two files after a timeout.",
         "Carry a unique event id and deduplicate in bronze or silver; never assume exactly once from Firehose."),
        ("Lost data after 24 hours", "With Direct PUT, if the destination is down Firehose keeps records for only 24 hours.",
         "Watch DeliveryToS3.DataFreshness and delivery success; read from Kinesis when a longer safety window is needed."),
        ("Lambda transform as a bottleneck", "A slow or failing transformation function holds up delivery for the whole stream.",
         "Keep transforms tiny; do real cleaning in silver; set timeouts and watch ExecuteProcessing.Success."),
        ("Dynamic partition limit", "More than 500 active partitions in the buffer fails delivery for that stream.",
         "Partition on a few low-cardinality fields; split very wide sources across several Firehose streams."),
    ],
    "compare": [
        ("Kinesis Data Streams streaming tables", "The stream already exists on Kinesis on-demand and you want append-only Iceberg tables with no transform.",
         "You need format conversion, Lambda transforms, routing to several tables, or a provisioned stream."),
        ("Databricks Auto Loader reading Kinesis directly", "Databricks already runs the platform lane and the Kinesis source works on your runtime; one less hop.",
         "You need files in S3 for other tools too, or the direct read falls short."),
        ("Azure Event Hubs Capture", "The platform runs on Azure; Capture writes Avro or Parquet files from Event Hubs to storage on a timer.",
         "You are on AWS."),
        ("Google Pub/Sub subscriptions to BigQuery or Cloud Storage", "The platform runs on Google Cloud.",
         "You are on AWS."),
        ("Kafka Connect S3 sink on MSK Connect", "Data already sits in Kafka topics and you want full control of file layout.",
         "You want no workers to size; Firehose can read MSK topics too."),
        ("Producers writing to S3 themselves", "A batch system already writes well-sized files on a schedule.",
         "Many small producers would create millions of tiny files."),
    ],
    "cost": {
        "model": ("Firehose bills per GB ingested, with each record rounded up to the nearest 5 KB for Direct PUT and Kinesis "
                  "sources. Extra charges apply per GB for format conversion to Parquet or ORC, for dynamic partitioning (plus a "
                  "charge per object delivered), and for delivery into a VPC. Lambda transformations are billed by Lambda. The "
                  "site estimates about $50 a month to write the plant stream into S3 Tables on an AWS-only platform; list price, "
                  "check your region."),
        "drivers": [
            "Total GB ingested, after rounding each record up to 5 KB.",
            "Format conversion and dynamic partitioning, each charged per GB on top of ingestion.",
            "Delivery into a VPC, for example to a private OpenSearch domain, charged per hour per Availability Zone and per GB.",
            "S3 request and storage costs at the destination, driven by how many files are written.",
        ],
        "traps": [
            "Sending one tiny record per event: a 200-byte click is billed as 5 KB, so batching several events into one record can cut the bill sharply.",
            "Raising the Direct PUT throughput limit far above real traffic, which makes Firehose deliver many small batches and raises costs at the destination.",
            "Paying for Parquet conversion when Auto Loader would read JSON and write Delta anyway; convert only if other tools read the files.",
            "Leaving debug Lambda transforms in place that run on every record.",
        ],
    },
    "security": [
        "Give Firehose its own IAM role that can write to one landing prefix and read from its source stream only; producers need only firehose:PutRecordBatch on that stream.",
        "Encrypt at rest with the platform's KMS key, both on the Firehose stream and on the destination bucket; Kinesis-sourced streams use the source stream's encryption.",
        "Producers inside the VPC reach Firehose through an interface VPC endpoint; deliveries to private destinations use Firehose's VPC delivery option.",
        "CloudTrail logs control-plane changes such as UpdateDestination; turn on Firehose error logging to CloudWatch Logs for delivery failures.",
        "Logs and app events often carry personal data such as email addresses or IP addresses; Macie scans the landing bucket, and a Lambda transform can drop fields that must never land.",
    ],
    "monitor": [
        ("DeliveryToS3.DataFreshness", "Age of the oldest record not yet delivered to S3; rising means delivery is stuck or slow."),
        ("DeliveryToS3.Success", "Share of S3 put operations that succeeded; anything below 1 needs a look."),
        ("IncomingRecords and IncomingBytes", "Volume in; a drop to zero shows a broken producer or webhook."),
        ("ThrottledRecords", "Direct PUT records rejected for exceeding the stream's throughput limit."),
        ("SucceedConversion.Records and FailedConversion.Records", "Records converted to Parquet or ORC, and records sent to the error prefix instead."),
        ("ExecuteProcessing.Success", "Share of Lambda transformation calls that succeeded."),
    ],
    "limits": [
        ("Record size", "1,000 KiB per record before base64 encoding"),
        ("PutRecordBatch", "Up to 500 records or 4 MiB per call, whichever is smaller"),
        ("Direct PUT throughput", "5 MiB a second in N. Virginia, Oregon and Ireland; 1 MiB a second elsewhere by default; adjustable"),
        ("Buffer interval", "60 to 900 seconds"),
        ("Retention when the destination is down", "24 hours for Direct PUT; the stream's own retention for a Kinesis source"),
        ("Dynamic partitioning", "500 active partitions per Firehose stream by default"),
    ],
    "decisions": [
        ("CloudWatch metrics and logs into the ops tables", "Metric stream and log subscription into Firehose, S3, Auto Loader",
         "Pursue: five-minute delay is fine and there is almost no code."),
        ("Dealer portal clicks, nobody acts on them live", "API Gateway into Firehose, S3, Auto Loader",
         "Pursue: minutes are enough; add Kinesis only if a live reader appears."),
        ("Plant sensor stream into bronze", "Databricks streaming table reading Kinesis every 15 minutes, with Firehose as fallback",
         "Pursue with care: use Firehose to S3 Parquet only if the direct Kinesis read falls short."),
        ("AWS-only platform, stream into Iceberg", "Firehose into S3 Tables",
         "Pursue: the site's choice for an AWS-only lake; compare with Kinesis streaming tables if the stream is on-demand."),
        ("Live alerts within seconds", "Firehose in the alert path",
         "Drop: a 60-second minimum buffer is too slow; use Flink and DynamoDB."),
    ],
    "faq": [
        ("Is Kinesis Data Firehose the same as Amazon Data Firehose?",
         "Yes. AWS renamed Kinesis Data Firehose to Amazon Data Firehose in February 2024. The service, its API and pricing did not "
         "change, so older articles still apply."),
        ("How fast does Firehose deliver data?",
         "It writes when a buffer fills or a time limit passes, with a minimum interval of 60 seconds for most destinations. In practice "
         "data lands in S3 one to a few minutes after it is sent, and Auto Loader adds its own short delay."),
        ("Can Firehose write Delta tables?",
         "No. Firehose writes files to S3 and Iceberg tables. On a Databricks platform it writes Parquet or JSON files into landing, "
         "and Auto Loader turns them into Delta bronze tables."),
        ("Does Firehose guarantee exactly once?",
         "No. Retries can deliver the same records twice, so give each record a unique id and deduplicate downstream."),
        ("Firehose or Kinesis Data Streams?",
         "Firehose when data must land somewhere within minutes and has one destination. Kinesis Data Streams when several readers need "
         "the same events within seconds, in order, with replay. Firehose can read from a Kinesis stream, so they combine well."),
    ],
    "sources": [
        ("AWS docs: Amazon Data Firehose quotas", "https://docs.aws.amazon.com/firehose/latest/dev/limits.html"),
        ("AWS docs: What is Amazon Data Firehose", "https://docs.aws.amazon.com/firehose/latest/dev/what-is-this-service.html"),
        ("AWS: Amazon Data Firehose pricing", "https://aws.amazon.com/firehose/pricing/"),
        ("AWS docs: replicate database changes to Iceberg (preview)", "https://docs.aws.amazon.com/firehose/latest/dev/database-as-source-iceberg.html"),
        ("AWS News Blog: database source preview, ended 30 Sep 2025", "https://aws.amazon.com/jp/blogs/aws/replicate-changes-from-databases-to-apache-iceberg-tables-using-amazon-data-firehose/"),
    ],
    "related": [
        ("Streaming on AWS and Databricks", "/learn/streaming/"),
        ("Every streaming option compared", "/learn/streaming/options/"),
        ("Ingestion framework", "/learn/data-platform-architecture/ingestion/"),
        ("Delta vs Iceberg", "/learn/delta-vs-iceberg/"),
        ("Amazon Kinesis Data Streams", "svc:kinesis-data-streams"),
        ("Amazon S3 Tables", "svc:s3-tables"),
    ],
}
