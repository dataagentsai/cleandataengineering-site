SERVICE = {
    "slug": "dynamodb-streams",
    "name": "Amazon DynamoDB Streams",
    "short": "DynamoDB Streams",
    "group": "streaming",
    "one_line": "A built-in change feed on a DynamoDB table: every insert, update and delete, in order per item, kept for 24 hours.",
    "status": "Generally available. Part of Amazon DynamoDB; no separate service to create.",
    "checked": "2026-11-11",
    "site_verdict": ("Pursue",
                     "The push step of the fast lane: Flink writes the latest state per press into DynamoDB, DynamoDB Streams hands "
                     "every change to a Lambda, and the Lambda pushes it through an API Gateway WebSocket to the live board. Nearly "
                     "free, serverless and true push. It is not a source for the lakehouse: the platform lane reads raw events from "
                     "Kinesis, never the fast lane's output."),
    "equivalents": {"azure": "Cosmos DB change feed",
                    "gcp": "Firestore listeners, or Bigtable and Spanner change streams",
                    "databricks": "Lakebase (Postgres) logical replication, or Delta change data feed for tables",
                    "open_source": "Debezium on a database's change log"},
    "plain": [
        "Amazon DynamoDB is a key-value database run by AWS: you store items, each with a key, and read or write them in a few "
        "milliseconds. DynamoDB Streams is a switch on a DynamoDB table. When it is on, every change to the table, whether a new item, "
        "an update or a delete, is also written as a stream record to a change feed. Programs can read that feed and react to each "
        "change within about a second.",
        "Each stream record says which item changed and, depending on the view type you pick, the item as it was before, as it is "
        "after, or both. Records for the same item appear in the order the changes happened, and each change appears exactly once. "
        "Records are kept for 24 hours and then trimmed. You do not size or pay for the stream itself; the usual reader is a Lambda "
        "function, and reads by Lambda triggers are free.",
        "This is change data capture, or CDC, built into the database. Instead of polling the table every second to ask what is new, a "
        "reader is told about each change once. The stream is organised in shards, which are slices of the feed that match the table's "
        "internal partitions. Shards split and close on their own as the table grows; Lambda and the Kinesis adapter library follow "
        "the parent and child shards for you so order is kept.",
        "A concrete example from a tyre plant: a live board shows each curing press's current temperature and status. A Flink job "
        "computes one-minute values and writes one item per press into a DynamoDB table only when the value changes. DynamoDB Streams "
        "passes each change to a small Lambda, which sends it over a WebSocket to every supervisor's browser. A screen that opens late "
        "first reads the current items from the table, then receives changes as they happen.",
    ],
    "analogy": "A doorbell wired to a filing cabinet: every time a folder is added, changed or removed, the bell rings once and tells you which folder.",
    "big_picture": [
        "On the reference platform DynamoDB Streams sits in the fast lane, the seconds-level path for plant alerts. The chain is "
        "Kinesis Data Streams, then Managed Service for Apache Flink for windows and limit checks, then DynamoDB as a small live "
        "store, then DynamoDB Streams read by Lambda, then API Gateway WebSocket to a React live board. The site's streaming design "
        "calls this route B, a small live store plus push, and marks it Pursue (recommended), at roughly 1 to 3 seconds end to end.",
        "The reason it is there is push. The live board must update without polling, and a screen that opens or reconnects must see "
        "the current state at once. DynamoDB gives the snapshot, and DynamoDB Streams gives the changes, so the gateway never has to "
        "ask the database what is new. The alternatives on the site, such as Lakebase or ClickHouse as the live store, lose this free "
        "push and need the app to poll every second.",
        "DynamoDB Streams does not feed the lakehouse. The platform lane reads the raw readings from Kinesis itself, so a bug in the "
        "fast lane can never corrupt the numbers of record in gold. What the fast lane creates, such as alerts raised and acknowledged, "
        "goes to bronze through Firehose as its own dataset. The DynamoDB table holds only about 48 hours of items, expired with a "
        "time to live, and the stream is how that small, hot copy reaches people.",
    ],
    "upstream": ["svc:managed-flink", "svc:dynamodb", "svc:lambda"],
    "downstream": ["svc:lambda", "svc:api-gateway", "svc:eventbridge"],
    "concepts": [
        ("Stream record", "One entry in the change feed describing one change to one item: its key, the type of change, and the before or after images you asked for."),
        ("Stream view type", "What each record carries: KEYS_ONLY, NEW_IMAGE, OLD_IMAGE or NEW_AND_OLD_IMAGES. It cannot be edited later; you turn the stream off and on again to change it."),
        ("Shard", "A slice of the stream that matches one table partition; shards split and close by themselves, and readers must finish a parent shard before its children."),
        ("Retention", "Records are kept for 24 hours and can be trimmed at any moment after that; there is no setting to keep them longer."),
        ("Event source mapping", "The Lambda feature that polls a stream for you, batches records and calls your function, with retries and failure handling."),
        ("Parallelization factor", "How many Lambda instances work on one shard at once, from 1 to 10, while still keeping order per item key."),
        ("Time to live (TTL)", "A DynamoDB setting that deletes items after a timestamp; each expiry also appears in the stream as a delete made by the service."),
        ("Kinesis Data Streams for DynamoDB", "A second, separate change feed that writes table changes into a Kinesis stream you own, with longer retention and more readers."),
    ],
    "use_when": [
        "Use it to push changes from a small live store to screens through Lambda and a WebSocket, as the site's fast lane does.",
        "Use it to react to a change in an operational table, for example sending an alert when a press status item flips to fault.",
        "Use it to keep a second store in step, such as updating a search index or a cache, when you only need the last 24 hours of changes.",
        "Use it with an EventBridge Pipe to forward selected changes to an event bus for other teams without writing a function.",
        "Use it to keep an audit trail of changes by having a Lambda write each record to Firehose, which lands it in S3.",
    ],
    "avoid_when": [
        "Avoid it as the source of record for analytics: 24 hours of retention and two readers per shard are too little; read raw events from Kinesis instead.",
        "Avoid it when more than two independent consumers need the changes; switch the table to Kinesis Data Streams for DynamoDB.",
        "Avoid it to export a whole table into the lakehouse; DynamoDB export to S3 or zero-ETL integrations fit full and incremental copies better.",
        "Avoid writing every sensor reading into DynamoDB just to stream it; write only changes, or the write bill and the stream volume grow with every reading.",
    ],
    "challenges": [
        ("Too many readers",
         "A third consumer is added to the same stream, reads per shard are throttled, and the live board starts to lag.",
         "Keep at most two readers per shard; fan out from one Lambda, use an EventBridge Pipe, or move to Kinesis Data Streams for DynamoDB."),
        ("Poison record blocks the shard",
         "One record makes the Lambda fail; by default Lambda retries it until it expires, and every later change for that shard waits.",
         "Set MaximumRetryAttempts, BisectBatchOnFunctionError and an on-failure destination such as an SQS queue; alarm on IteratorAge."),
        ("Lost changes after a long outage",
         "The consumer is broken for more than 24 hours and records are trimmed before they are read.",
         "Alarm early on IteratorAge; design screens to reload a snapshot from the table, so a gap heals itself on reconnect."),
        ("Write amplification",
         "Flink writes every reading rather than only changes, the table and the stream fill up, and DynamoDB writes become the biggest bill.",
         "Emit changes only and one-minute windows; the site's design notes this is the difference between about $50 and $5,000 a month at stretch scale."),
        ("TTL deletes flood consumers",
         "Expired items appear as deletes in the stream, and the live board receives thousands of removals at once.",
         "Filter them out in the event source mapping on userIdentity type Service, or ignore REMOVE events in the function."),
        ("Wrong view type",
         "The stream was turned on with KEYS_ONLY, the consumer needs the new values, and the view type cannot be edited.",
         "Pick NEW_IMAGE or NEW_AND_OLD_IMAGES from the start; changing it means turning the stream off and on, which creates a new stream ARN."),
        ("Ordering assumptions",
         "Developers assume global order across items; order is kept only per item key.",
         "Design consumers to handle each item independently; carry an event time or version number in the item and ignore older updates."),
    ],
    "compare": [
        ("Kinesis Data Streams for DynamoDB",
         "You need retention beyond 24 hours, more than two readers, or Firehose and Flink as direct consumers.",
         "You want the cheapest push to one Lambda, with exactly-once records in order per item; Kinesis may reorder or duplicate."),
        ("Lakebase as the live store",
         "The live store must sit under Unity Catalog and be queried with SQL.",
         "You want free push to screens; Lakebase needs the app to poll, which the site marks as the Databricks-leaning alternative."),
        ("Cosmos DB change feed",
         "The platform runs on Azure; the change feed keeps history as long as the data and supports many readers.",
         "You are on AWS with DynamoDB as the live store."),
        ("Debezium on a relational database",
         "The live store is Postgres or MySQL and you already run Kafka Connect.",
         "You want a serverless, built-in feed with nothing to run."),
        ("Polling the table every second",
         "Never for a live board; it costs reads all day and still adds a second of delay.",
         "Always prefer the stream for push."),
    ],
    "cost": {
        "model": "The stream itself has no hourly charge. Reads are billed as stream read request units, where each GetRecords call "
                 "counts as one unit and returns up to 1 MB. Reads made by Lambda triggers and by global tables replication are not "
                 "billed, except for Lambda functions on Lambda Managed Instances, and the first 2.5 million stream read requests a "
                 "month are free. The real costs are the DynamoDB writes that create the records and the Lambda invocations that "
                 "process them. Check the pricing page for your region's list prices.",
        "drivers": [
            "The number of writes to the table, because every write that changes data produces a stream record.",
            "The Lambda invocations, duration and batch size used to read the stream.",
            "GetRecords calls by consumers that are not Lambda, such as the Kinesis adapter library.",
            "Downstream push costs, such as API Gateway WebSocket messages for every change sent to every screen.",
        ],
        "traps": [
            "Writing every reading instead of only changes multiplies DynamoDB writes, Lambda calls and WebSocket messages together.",
            "Small Lambda batch sizes with no batching window cause many short invocations; set a batch window of a second or less for screens.",
            "Endless retries of a failing batch keep Lambda busy until records expire; cap retries.",
            "A custom consumer that polls with GetRecords in a tight loop pays for every empty call; Lambda reads are free.",
        ],
    },
    "security": [
        "Reading a stream needs dynamodb:DescribeStream, GetShardIterator, GetRecords and ListStreams on the stream ARN; give the Lambda execution role only these, for one table.",
        "Stream records are encrypted at rest with the table's encryption key, either the AWS owned key or the platform's customer managed KMS key.",
        "DynamoDB Streams has its own endpoint, separate from the table endpoint. Lambda's event source mapping reads it for you; a custom reader in a private subnet needs its own network path to that endpoint, so check VPC endpoint support for streams in your region before building one.",
        "Control-plane changes, such as turning a stream on or off, are recorded in CloudTrail; data reads are not logged by default.",
        "Keep personal data out of the live store: a press status board needs press IDs and readings, not operator names, and the stream copies whatever the item holds.",
    ],
    "monitor": [
        ("IteratorAge (Lambda)", "How old the last record processed by the Lambda was; the key signal that the push lane is falling behind."),
        ("ReturnedRecordsCount", "Records returned by GetRecords calls; a drop to zero during production hours means the writer has stopped."),
        ("ReturnedBytes", "Bytes returned per read; growth signals that items or view types are larger than expected."),
        ("Errors and Throttles (Lambda)", "Failed or throttled invocations of the stream consumer."),
        ("ApproximateNumberOfMessagesVisible (failure queue)", "Records the Lambda gave up on and sent to its SQS on-failure destination; any value above zero needs a look."),
        ("WriteThrottleEvents (table)", "Writes to the live store being throttled; the stream cannot carry changes that were never written."),
    ],
    "limits": [
        ("Retention", "24 hours; records older than that can be trimmed at any time"),
        ("Readers per shard", "No more than two processes should read the same shard at once, or reads are throttled"),
        ("View type", "Fixed once the stream is created; changing it needs a new stream"),
        ("Lambda parallelization factor", "1 to 10 concurrent batches per shard"),
        ("GetRecords", "Up to 1 MB or 1,000 records per call"),
    ],
    "decisions": [
        ("Live board for 2,000 presses must update within 3 seconds and show state on open",
         "Flink into DynamoDB, DynamoDB Streams to Lambda, API Gateway WebSocket",
         "Pursue: the site's recommended route; snapshot from the table plus push from the stream."),
        ("Three teams want every change to the live store, and one wants a week of history",
         "Kinesis Data Streams for DynamoDB instead of DynamoDB Streams",
         "Pursue with care: more readers and longer retention, but records may arrive out of order or twice."),
        ("Analysts want the fast lane's live values in the lakehouse",
         "Read DynamoDB Streams into bronze",
         "Drop: the platform lane reads raw events from Kinesis so the fast lane cannot corrupt gold; land alerts through Firehose as their own dataset."),
        ("Raise a ticket when a press item changes to fault status",
         "DynamoDB Streams with an EventBridge Pipe filtered on status, targeting an event bus",
         "Pursue: no function to write; the bus routes to the ticketing tool."),
    ],
    "faq": [
        ("How long does DynamoDB Streams keep data?",
         "24 hours. After that, records can be trimmed at any time, and there is no setting to extend it. If you need longer, use "
         "Kinesis Data Streams for DynamoDB, which keeps records as long as the Kinesis stream's retention."),
        ("What is the difference between DynamoDB Streams and Kinesis Data Streams for DynamoDB?",
         "DynamoDB Streams is built in, keeps 24 hours, gives each change exactly once in order per item, and suits up to two readers "
         "per shard. Kinesis Data Streams for DynamoDB writes changes to a Kinesis stream with longer retention and many readers, but "
         "records can be out of order or duplicated, and it is billed per change data capture unit plus Kinesis."),
        ("Is DynamoDB Streams free?",
         "Reads by Lambda triggers are not billed, and the first 2.5 million read requests a month are free. Other readers pay per "
         "GetRecords call. You still pay for the table writes that create the records and for the Lambda that reads them."),
        ("Does DynamoDB Streams guarantee order?",
         "Yes, per item: all changes to the same primary key appear in the order they happened. There is no order across different items."),
        ("Can I change the stream view type?",
         "No. To change it, turn the stream off and on again with the new view type, which creates a new stream with a new ARN. "
         "Update the Lambda event source mapping to point at it."),
    ],
    "sources": [
        ("AWS docs: Change data capture for DynamoDB Streams", "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html"),
        ("AWS docs: Kinesis Data Streams for DynamoDB", "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/kds.html"),
        ("AWS docs: DynamoDB Streams and Lambda triggers", "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.Lambda.html"),
        ("Amazon DynamoDB on-demand pricing", "https://aws.amazon.com/dynamodb/pricing/on-demand/"),
    ],
    "related": [
        ("Streaming on AWS and Databricks", "/learn/streaming/"),
        ("Streaming options compared", "/learn/streaming/options/"),
        ("Real-time mode on Databricks", "/learn/streaming/real-time-mode/"),
        ("Amazon DynamoDB", "svc:dynamodb"),
        ("Managed Service for Apache Flink", "svc:managed-flink"),
        ("Amazon API Gateway", "svc:api-gateway"),
    ],
}
