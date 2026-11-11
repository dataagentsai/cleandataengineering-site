SERVICE = {
    "slug": "kinesis-data-streams",
    "name": "Amazon Kinesis Data Streams",
    "short": "Kinesis Data Streams",
    "group": "streaming",
    "one_line": "A managed, ordered log of events that many readers can replay, kept from one day up to a year, with no cluster to run.",
    "status": ("Generally available. Three changes since 2025: records can now be up to 10 MiB; an account-level On-demand "
               "Advantage mode (Nov 2025) lowers data prices but bills a floor of 25 MB/s; and streaming tables (Aug 2026) "
               "deliver a stream straight into Iceberg tables on S3 Tables, for on-demand streams only."),
    "checked": "2026-11-11",
    "site_verdict": ("Pursue",
                     "The stream belt for plant sensors and connected products. IoT gateways write to it, Managed Flink reads it for "
                     "the seconds lane, and a Databricks streaming table reads the same raw stream every 15 minutes for bronze. "
                     "Provisioned with 7 days of retention once volume is known; on-demand for the first months."),
    "equivalents": {"azure": "Event Hubs", "gcp": "Pub/Sub", "databricks": "none: Databricks reads Kinesis directly (Zerobus Ingest writes to a table, it is not a log)",
                    "open_source": "Apache Kafka (or Redpanda)"},
    "plain": [
        "Amazon Kinesis Data Streams is a managed event log. An event is a small record that says something happened: a curing "
        "press reported 182 degrees at 10:04:05, a shopper added a tyre to a basket, a vehicle sensor saw low pressure. Producers "
        "write these records into a stream, and the stream keeps them in arrival order for a retention period you choose, from 24 "
        "hours up to 365 days. Readers, called consumers, read the records at their own pace. Reading does not delete anything, so "
        "two, five or twenty different programs can read the same records, and any of them can go back and read again.",
        "A stream is cut into shards. A shard is a lane of fixed capacity: in provisioned mode each shard accepts up to 1 MB a second "
        "or 1,000 records a second of writes, and serves 2 MB a second of reads. Every record carries a partition key, such as a "
        "press number, and Kinesis hashes that key to choose the shard. All records with the same key land on the same shard in the "
        "same order, which is how you keep each machine's readings in sequence. You either choose the number of shards yourself "
        "(provisioned mode) or let AWS scale them for you (on-demand mode).",
        "A concrete example: a tyre plant has about 2,000 presses and mixers, each sending 20 signals every 5 seconds, roughly 8,000 "
        "readings a second. A gateway in each plant batches readings and writes them to one Kinesis stream in the Mumbai Region, "
        "keyed by press number. A Flink job reads the stream to raise an alert within seconds when a press drifts out of its limits. "
        "Separately, a Databricks streaming table reads the very same stream every 15 minutes and appends everything into a bronze "
        "Delta table. If the Databricks job breaks for a day, it catches up from its checkpoint.",
    ],
    "analogy": "A conveyor belt with numbered trays that keeps every tray for a week, so any station can walk back along the belt and pick up what it missed.",
    "big_picture": [
        "On the reference platform Kinesis Data Streams is the belt in the move-in lane for anything that arrives as a stream of "
        "records rather than as files. Plant gateways running SiteWise Edge on AWS IoT Greengrass write to it directly with an IAM "
        "role; IoT Core rules forward connected-tyre messages into it; app backends can write to it through API Gateway or the SDK. "
        "It is the split point of the streaming design: the raw event is written once, and every lane reads it from there.",
        "Two lanes read it. The fast lane, Managed Service for Apache Flink, computes windows and limit checks and writes results to "
        "DynamoDB, which pushes changes to screens. The platform lane, a Lakeflow streaming table, reads the raw stream on a "
        "15-minute trigger and lands it in bronze with the shard, sequence number and arrival time as envelope columns. Because the "
        "platform lane reads the raw stream rather than the fast lane's output, a bug in Flink can never corrupt the number of record.",
        "Kinesis keeps 7 days on this platform. That is enough to rebuild Flink state (the live lane only needs 48 hours) and to "
        "survive a long weekend of a broken Databricks job. Bronze keeps everything after that, forever, which is far cheaper than "
        "paying the stream to hold years of readings. For sources that only need minutes, the site skips the belt and writes files "
        "to S3 through Firehose instead.",
    ],
    "upstream": ["svc:iot-greengrass", "svc:iot-core", "Apps through API Gateway or the SDK"],
    "downstream": ["svc:managed-flink", "Databricks streaming tables", "svc:data-firehose"],
    "concepts": [
        ("Shard", "A unit of capacity inside a stream: 1 MB a second or 1,000 records a second in, 2 MB a second out, in provisioned mode."),
        ("Partition key", "A value you attach to each record, such as a press number. Kinesis hashes it to pick the shard, so the same key always keeps its order."),
        ("Sequence number", "A unique, increasing number Kinesis gives each record within a shard. Readers store it to know where they stopped."),
        ("Retention period", "How long records stay readable: 24 hours by default, up to 7 days as extended retention, and up to 365 days as long-term retention."),
        ("Shared throughput consumer", "A reader that polls with GetRecords. All such readers on a shard share its 2 MB a second and five calls a second."),
        ("Enhanced fan-out", "A registered consumer that gets its own 2 MB a second per shard, pushed over HTTP/2 in about 70 milliseconds. Up to 20 per stream, or 50 in On-demand Advantage mode."),
        ("Capacity mode", "Provisioned, where you set the shard count, or on-demand, where AWS scales shards and bills per GB. On-demand has a Standard and an Advantage pricing option."),
        ("Iterator age", "How old the last record a reader fetched was when it fetched it. A growing iterator age means the reader is falling behind."),
        ("Streaming tables", "A 2026 feature that delivers a stream straight into an Apache Iceberg table on S3 Tables, append only, for on-demand streams."),
    ],
    "use_when": [
        "Use it when two or more programs must read the same events, such as a live alert job and a lakehouse loader.",
        "Use it when readers must be able to replay the last hours or days after a bug fix or an outage.",
        "Use it when order per key matters, for example every reading of one press must be processed in sequence.",
        "Use it when the producers are AWS-native, such as IoT Core rules, Greengrass stream manager, DMS or CloudWatch, and you want no cluster to patch.",
        "Use it when volume is a few MB a second up to several GB a second and you prefer paying per shard or per GB to sizing brokers.",
    ],
    "avoid_when": [
        "Avoid it when the source only needs to arrive within minutes and has a single reader; Firehose writing files to S3 is cheaper and simpler.",
        "Avoid it when your team and tools already speak Kafka, for example Debezium, Kafka Connect or a partner's Kafka topics; MSK fits better.",
        "Avoid it as long-term storage for years of history; keep 7 days in the stream and the rest in bronze tables.",
        "Avoid it when you need one consumer to process each message once and then forget it, such as a work queue; that is SQS.",
    ],
    "challenges": [
        ("Hot shard", "One busy key, such as a single line controller that sends ten times more than others, overloads one shard; writes are throttled and data lags.",
         "Pick a partition key with many values (press number, not plant); watch WriteProvisionedThroughputExceeded per shard with enhanced metrics; use on-demand mode while volume is unknown."),
        ("Readers fighting over a shard", "Several polling readers share 2 MB a second and five GetRecords calls a second per shard, so adding a third reader slows the first two.",
         "Give each important reader enhanced fan-out; keep shared polling for one cheap reader at most."),
        ("Reader falls behind past retention", "A stalled reader that is more than the retention period behind silently loses records; they expire before it reads them.",
         "Alarm on GetRecords.IteratorAgeMilliseconds at a fraction of retention, for example 12 hours on a 7-day stream; keep bronze as the long memory."),
        ("Duplicates on retry", "Producers retry failed PutRecords calls and readers reprocess after a restart, so the same record can arrive twice.",
         "Put a unique reading_id in every record and deduplicate on it in bronze or silver; treat delivery as at least once."),
        ("Partial batch failures", "PutRecords accepts up to 500 records and can fail some of them while the call itself succeeds.",
         "Check FailedRecordCount in every response and retry only the failed records with backoff; the Kinesis Producer Library does this for you."),
        ("Resharding surprises", "Splitting or merging shards closes parent shards and opens children; a home-made reader that ignores the lineage reads out of order or misses data.",
         "Use the Kinesis Client Library, Flink's connector or Databricks' source, which follow parent and child shards; avoid writing raw GetRecords loops."),
        ("Large records", "Records can now be up to 10 MiB, but large records eat burst capacity and still count against the 1 MB a second per shard over time.",
         "Keep sensor records small and batch them; send big payloads to S3 and put only the object key on the stream."),
    ],
    "compare": [
        ("Amazon MSK", "Your team already uses Kafka tools such as Debezium, Kafka Connect or ksql clients, or you need topics shared with partners or other clouds.",
         "You want no brokers to size, patch or rebalance and your producers are AWS services."),
        ("Amazon Data Firehose on its own", "The data only needs to land as files in S3 or a table within minutes and nothing else reads it live.",
         "Two readers need the same events, or a reader needs replay and per-key order."),
        ("Azure Event Hubs", "The platform runs on Azure; Event Hubs also speaks the Kafka protocol, so Kafka clients connect without code changes.",
         "The platform runs on AWS; cross-cloud traffic adds cost and delay."),
        ("Google Pub/Sub", "The platform runs on Google Cloud and you want a global topic with no partitions to plan.",
         "You need strict order per key at high volume without ordering-key limits, on AWS."),
        ("Databricks Zerobus Ingest", "A single app stream has exactly one reader, the Delta table, and you want no belt at all.",
         "A live lane or a second reader needs the same events, or you need Kinesis-style replay; the site drops it for sensors."),
        ("Amazon SQS, SNS or EventBridge", "You need a work queue, fan-out notifications or event routing between services.",
         "You need an analytics log: a queue deletes a message once read, so there is no replay, no second reader and no per-key order."),
    ],
    "cost": {
        "model": ("Provisioned mode bills per shard-hour, plus a charge per PUT payload unit (each record rounded up to 25 KB), plus "
                  "extended retention per shard-hour beyond 24 hours, long-term retention per GB-month beyond 7 days, and enhanced "
                  "fan-out per consumer-shard-hour plus per GB read. On-demand Standard bills a per-stream hour plus per GB written "
                  "and read, with no shard planning. On-demand Advantage, an account-wide setting, removes the per-stream charge and "
                  "lowers per-GB prices, but bills at least 25 MB a second of ingest and of retrieval across all on-demand streams. The "
                  "site's sizing for the plant stream is about $120 a month provisioned (2 shards, 7 days, 2 dedicated readers) and "
                  "about $160 on-demand; list price, check your region."),
        "drivers": [
            "Shard count in provisioned mode, which follows the busier of bytes a second and records a second.",
            "Many tiny records: each one is at least one 25 KB PUT payload unit, so batching ten readings into one record cuts the bill.",
            "Retention beyond 24 hours, charged per shard-hour up to 7 days and per GB-month after that.",
            "Each enhanced fan-out reader, charged per shard-hour and per GB it reads.",
            "Delivery to streaming tables or S3, charged per TB delivered.",
        ],
        "traps": [
            "Turning on On-demand Advantage for a small platform: the 25 MB a second floor is far above a plant stream of a few MB a second, and the switch cannot be undone for 24 hours.",
            "Leaving on-demand mode on at steady, predictable load; provisioned is usually cheaper once you know the volume.",
            "Setting 365-day retention to avoid building bronze; you pay to store years in the stream and still cannot query it with SQL.",
            "Forgetting dev and test streams that keep running with shards and retention nobody uses.",
        ],
    },
    "security": [
        "Use IAM roles for every producer and reader: the plant gateway gets kinesis:PutRecords on one stream only, Databricks' instance profile or service credential gets read actions only.",
        "Turn on server-side encryption with the platform's KMS key; producers and readers then also need kms:GenerateDataKey or kms:Decrypt on that key.",
        "Reach Kinesis through an interface VPC endpoint so traffic from Databricks, Flink and Lambda never leaves the private network; add an endpoint policy that names the allowed streams.",
        "Use a resource policy on the stream for cross-account readers instead of sharing access keys.",
        "CloudTrail records control-plane calls such as CreateStream and UpdateShardCount; data-plane calls are not logged by default.",
        "If records carry personal data, such as a driver ID from a vehicle, keep retention short and mask the field in silver.",
    ],
    "monitor": [
        ("GetRecords.IteratorAgeMilliseconds", "How far behind polling readers are; alarm well before it reaches the retention period."),
        ("SubscribeToShardEvent.MillisBehindLatest", "The same lag for enhanced fan-out readers such as Flink."),
        ("WriteProvisionedThroughputExceeded", "Writes throttled because a shard or the stream is full; a sign of a hot key or too few shards."),
        ("ReadProvisionedThroughputExceeded", "Reads throttled because readers share a shard's limits; add enhanced fan-out or fewer pollers."),
        ("IncomingRecords and IncomingBytes", "Volume in; a drop to zero for one plant is the silent-stream signal the site alarms on."),
        ("PutRecords.FailedRecords", "Records rejected inside successful batch calls; producers must retry these."),
    ],
    "limits": [
        ("Record size", "Up to 10 MiB per record before base64 encoding; large records use burst capacity"),
        ("Shard write", "1 MB a second or 1,000 records a second per shard (provisioned)"),
        ("Shard read", "2 MB a second and five GetRecords calls a second per shard, shared by polling readers"),
        ("Retention", "24 hours default, up to 8,760 hours (365 days)"),
        ("Enhanced fan-out", "20 registered consumers per stream, or 50 with On-demand Advantage"),
        ("On-demand", "4 MB a second write at creation; scales to 200 MB a second in most Regions, 10 GB a second in the largest; 50 on-demand streams by default"),
    ],
    "decisions": [
        ("Plant sensors, about 8,000 readings a second, two readers", "Kinesis provisioned, 2 to 4 shards with batched records, 7 days",
         "Pursue: the cheapest belt that both Flink and Databricks read natively."),
        ("New source, volume unknown for the first months", "Kinesis on-demand Standard",
         "Pursue: no sizing while volume settles; switch to provisioned once the load is steady."),
        ("Land the stream as Iceberg tables with no code", "Kinesis streaming tables into S3 Tables",
         "Pursue with care: needs on-demand mode, cannot backfill or evolve the schema, and an AWS-only platform benefits more than one where Databricks already reads the stream."),
        ("Many accounts and streams at over 25 MB a second in total", "On-demand Advantage",
         "Pursue with care: lower per-GB prices only pay off above the floor; check the total first."),
        ("Debezium CDC from many databases and partner Kafka topics", "MSK instead of Kinesis",
         "Keep if you have it: if Kafka is already running, do not add a second belt."),
    ],
    "faq": [
        ("What is the difference between Kinesis Data Streams and Firehose?",
         "Data Streams is a log that keeps records so many readers can process them, in order, and replay them. Firehose is a delivery "
         "service that buffers records and writes them as files or table rows into S3, Redshift or other destinations. They are often "
         "used together: Firehose can read from a Kinesis stream."),
        ("Can Databricks read Kinesis directly?",
         "Yes. Structured Streaming and Lakeflow streaming tables have a Kinesis source, and enhanced fan-out is recommended. On the "
         "site's platform a streaming table reads the stream every 15 minutes and stops, so nothing runs continuously. Check that the "
         "trigger you want works with the Kinesis source on your runtime."),
        ("Should I use provisioned or on-demand mode?",
         "Start on-demand while you do not know the volume, then switch to provisioned once traffic is steady, because provisioned is "
         "usually cheaper at predictable load. You can switch a stream between modes twice in 24 hours. Streaming tables delivery "
         "needs on-demand mode."),
        ("How long should a Kinesis stream keep data?",
         "Long enough to rebuild your stream processors and to survive a reader being broken over a weekend, typically 7 days. Keep "
         "longer history in bronze tables, which are far cheaper and can be queried with SQL."),
        ("Kinesis or MSK?",
         "Kinesis when you want a managed stream with no cluster and AWS-native producers; MSK when you already speak Kafka, need "
         "Kafka Connect or Debezium, or want the same tool on every cloud."),
    ],
    "sources": [
        ("AWS docs: Kinesis Data Streams quotas and limits", "https://docs.aws.amazon.com/streams/latest/dev/service-sizes-and-limits.html"),
        ("AWS docs: Kinesis delivery quotas (streaming tables and S3)", "https://docs.aws.amazon.com/streams/latest/dev/data-delivery-quotas.html"),
        ("AWS What's New: On-demand Advantage mode (Nov 2025)", "https://aws.amazon.com/about-aws/whats-new/2025/11/amazon-kinesis-data-streams-ondemand-advantage"),
        ("AWS What's New: streaming tables on S3 Tables (Aug 2026)", "https://aws.amazon.com/about-aws/whats-new/2026/08/kinesis/data-delivery-s3-tables"),
        ("AWS: Kinesis Data Streams pricing", "https://aws.amazon.com/kinesis/data-streams/pricing/"),
    ],
    "related": [
        ("Streaming on AWS and Databricks", "/learn/streaming/"),
        ("Every streaming option compared", "/learn/streaming/options/"),
        ("Databricks real-time mode", "/learn/streaming/real-time-mode/"),
        ("Amazon MSK", "svc:msk"),
        ("Amazon Data Firehose", "svc:data-firehose"),
        ("Managed Service for Apache Flink", "svc:managed-flink"),
    ],
}
