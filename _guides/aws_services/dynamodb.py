SERVICE = {
    "slug": "dynamodb",
    "name": "Amazon DynamoDB",
    "short": "DynamoDB",
    "group": "operational",
    "one_line": "A serverless key-value database that answers lookups by key in milliseconds; on this platform the fast lane's live store, not the metadata store.",
    "status": "Generally available. Recent additions in 2026: multi-account global tables (Feb), native vector search (Aug), filtered export to S3 (Oct) and bulk put items from S3 (Nov).",
    "checked": "2026-11-11",
    "site_verdict": ("Pursue",
                     "The live store for the seconds lane: Flink writes the latest value per press and short-lived 48-hour items, DynamoDB Streams "
                     "pushes each change to the WebSocket, and it costs about $50 a month when you write changes only. It sits outside Unity Catalog, "
                     "which is acceptable for a disposable copy. It was dropped as the metadata database, where Lakebase won."),
    "equivalents": {"azure": "Azure Cosmos DB (NoSQL API)",
                    "gcp": "Firestore or Bigtable",
                    "databricks": "Lakebase (managed PostgreSQL) if every store must be inside Unity Catalog",
                    "open_source": "Apache Cassandra or ScyllaDB (ScyllaDB also offers a DynamoDB-compatible API)"},
    "plain": [
        "Amazon DynamoDB is a database where you store items and fetch them back by a key. An item is a small record, like a row, made of named "
        "attributes. Every item has a partition key, which decides where it is stored, and can have a sort key, which orders items that share a "
        "partition key. You ask for one item by its full key, or for a range of items under one partition key, and DynamoDB answers in a few "
        "milliseconds no matter how big the table is. There are no servers to size: AWS spreads the table over as many machines as it needs.",
        "What it does not do matters just as much. There are no joins between tables, no free-form SQL over the whole table, and no aggregation "
        "such as summing a column across millions of items. You design the table for the questions you will ask, in advance. If a new question "
        "appears later, you add an index or a new table, or you send the question to a warehouse instead.",
        "A manufacturing example: a tyre plant has 120 curing presses, each reporting temperature and pressure every second. The operators' live "
        "board needs to show the current state of each press and a chart of the last two days. A DynamoDB table keyed by press holds one item with "
        "the latest values, plus one item per press per minute for the chart, each with an expiry time 48 hours ahead. The board reads the latest "
        "items when it opens and then receives only changes. Nobody asks this table for last year's scrap rate; that question goes to the gold "
        "tables in Databricks.",
    ],
    "analogy": "A wall of numbered lockers: you can open any locker instantly if you know its number, but you cannot ask the wall which lockers hold red boxes.",
    "big_picture": [
        "DynamoDB sits in the fast lane of the streaming design, the lane that must put an alert on a screen within seconds. Plant readings arrive "
        "on Kinesis Data Streams, Managed Service for Apache Flink computes windows and limit breaches, and Flink writes the results to DynamoDB. "
        "DynamoDB Streams then hands every change to a small Lambda function, which pushes it to the browser through an API Gateway WebSocket. A "
        "new screen first reads a snapshot from the table and then listens for changes.",
        "It holds a short-lived copy only. Items carry a time-to-live of 48 hours, so the table stays small and cheap. The governed record of the "
        "same readings is built separately in the platform lane, as bronze, silver and gold Delta tables in Unity Catalog. Because DynamoDB is not "
        "governed by Unity Catalog and is not a Lakehouse Federation source, the site accepts it only for this disposable copy. If policy says "
        "every store must be in Unity Catalog, the live store becomes Lakebase and the screen polls instead of being pushed.",
        "Reference data also flows into it. Limits, the press master and recipes are published from silver or gold every 15 minutes or daily, "
        "so the fast lane can label screens without calling the platform. DynamoDB was also considered for the metadata database, the store that "
        "holds sources, rules, watermarks and run logs. It was dropped there because that data is relational: it needs keys between tables and a "
        "merged view built with joins. Lakebase was chosen for that role.",
    ],
    "upstream": ["svc:managed-flink", "svc:lambda", "Reference data published from gold"],
    "downstream": ["svc:dynamodb-streams", "svc:api-gateway", "svc:appsync"],
    "concepts": [
        ("Item", "One record in a table, up to 400 KB, made of named attributes. Items in the same table do not need the same attributes."),
        ("Partition key", "The attribute DynamoDB hashes to decide where an item lives. Good keys have many distinct values, such as press_id, so load spreads evenly."),
        ("Sort key", "An optional second part of the key that orders items under one partition key, such as a minute timestamp, so you can read a time range."),
        ("Capacity mode", "On-demand bills per request and scales on its own; provisioned bills for a set number of reads and writes per second that you choose, optionally with auto scaling."),
        ("Read and write units", "The billing unit. One write unit covers an item up to 1 KB; one read unit covers a strongly consistent read up to 4 KB. Bigger items cost more units."),
        ("Global secondary index (GSI)", "A second copy of the table keyed differently, so you can look items up by another attribute. It is kept in step asynchronously and billed for its own writes."),
        ("Time to live (TTL)", "An attribute holding an expiry time. DynamoDB deletes expired items in the background at no write cost, usually within a few days of expiry, not at the exact second."),
        ("DynamoDB Streams", "An ordered log of every change to the table, kept for 24 hours, that Lambda or other readers can consume to react to changes."),
        ("Hot partition", "One key receiving far more traffic than the rest. Each partition has its own ceiling, so a hot key is throttled even when the table has spare capacity."),
    ],
    "use_when": [
        "You need the latest state of many things, such as presses, orders or delivery vans, read by key in milliseconds by an application or a live screen.",
        "You want changes pushed onward, because DynamoDB Streams emits every insert, update and delete in order per item.",
        "The data is short-lived and can expire on its own with TTL, such as a 48-hour chart window for a live board.",
        "Traffic is spiky or unknown and you do not want to size or patch servers; on-demand mode bills only for requests made.",
        "An application needs a simple, durable session, cart or idempotency table, for example to make sure a webhook from a supplier is processed once.",
    ],
    "avoid_when": [
        "The data is relational and needs joins, foreign keys or a merged view, as the metadata database does; use PostgreSQL, which on this platform means Lakebase.",
        "People will ask new analytical questions such as totals by plant and month; that belongs on Delta tables with a SQL warehouse.",
        "Every store must be governed by Unity Catalog, with lineage and masks, and no exception is allowed for a disposable copy.",
        "You need ad hoc slicing of live data across many dimensions; a column store such as ClickHouse fits that better.",
        "Items would routinely exceed 400 KB, such as images or large documents; store those in S3 and keep only a pointer in DynamoDB.",
    ],
    "challenges": [
        ("Hot partition", "All writes for a busy line land on one key, and DynamoDB throttles that key while the rest of the table sits idle.",
         "Choose keys with many values, such as press rather than plant. Add a suffix to spread a very busy key. Turn on CloudWatch Contributor Insights to find the hottest keys."),
        ("Writing every reading", "Flink writes every sensor reading instead of only changes. At stretch scale the site estimates this as the difference between $50 and $5,000 a month.",
         "Emit changes and one-minute window results only. Compare WriteRequestUnits against the number of presses before go-live."),
        ("TTL is not a timer", "Teams expect items to vanish exactly at expiry, but deletion can lag by days, so screens or queries show stale items.",
         "Filter on the expiry attribute when reading. Treat TTL as cleanup, not as business logic."),
        ("Throttling on a new table", "An on-demand table starts with limited warm capacity. A sudden launch-day spike can be throttled while DynamoDB adapts.",
         "Pre-warm the table using warm throughput settings before a planned spike, or load-test with realistic traffic the week before go-live."),
        ("Missing access pattern", "Months later someone needs live items by line or by shift, and the key design cannot answer it.",
         "Write down every read the screens need before creating the table. Add a GSI for each new pattern, and route analytical questions to the platform lane instead."),
        ("Large or growing items", "Appending readings to one item per press grows it towards 400 KB, and every update is billed on the full item size.",
         "Store one item per press per minute, not one ever-growing item. Keep the latest-value item small."),
        ("Outside the governed catalog", "The live table is not visible in Unity Catalog, so lineage and access reviews miss it.",
         "Register it in the platform's inventory as a disposable copy, keep only 48 hours, and keep personal data out of it."),
        ("Stream consumer lag", "The Lambda reading DynamoDB Streams falls behind or fails, so screens stop updating while the table looks healthy.",
         "Alarm on the Lambda IteratorAge metric and on errors. Set a failure destination and use the batch item failure response so one bad record does not block a shard."),
    ],
    "compare": [
        ("Lakebase (Databricks managed PostgreSQL)", "Every store must be in Unity Catalog, or you want SQL over the live data and one fewer AWS service.",
         "You want true push of changes; Lakebase does not emit a change stream, so the screen must poll, and compute is always on."),
        ("Amazon ElastiCache (Valkey)", "You need the fastest possible latest-value cache in front of something else.",
         "You need a 48-hour history and durable storage; the site marks ElastiCache Drop as the primary live store."),
        ("ClickHouse Cloud", "Live screens need ad hoc slicing over 48 hours, such as any filter on any column.",
         "You only need latest values and a fixed chart; it adds a vendor and does not push changes."),
        ("Azure Cosmos DB", "You are building the same live store on Azure; it has a change feed much like DynamoDB Streams.",
         "You are on AWS; there is no reason to cross clouds for a live store."),
        ("Google Firestore or Bigtable", "On Google Cloud: Firestore for app-style documents with listeners, Bigtable for very large time-keyed data.",
         "You are on AWS."),
        ("Aurora PostgreSQL or RDS with Lakehouse Federation", "You need relational data with joins for an application.",
         "You hope it makes the live store governed; the site marks this Drop because the live app still reads it directly, so governance is on paper only."),
    ],
    "cost": {
        "model": "On-demand mode bills per million write request units and read request units, plus storage per GB-month. Provisioned mode bills per "
                 "write and read capacity unit per hour, whether used or not, and can be cheaper for steady traffic, especially with reserved capacity. "
                 "Extra charges apply for global secondary indexes (each index write is billed), DynamoDB Streams reads beyond the free Lambda trigger "
                 "path, backups, point-in-time recovery, global table replication and exports to S3. AWS cut on-demand prices substantially in November "
                 "2024; check the current list price in your region. The site's live store is estimated at about $40 to $50 a month for a plant "
                 "writing changes only.",
        "drivers": [
            "Write volume: every write unit is billed, so writing only changes, not every reading, is the main lever.",
            "Item size: an item over 1 KB costs more than one write unit for each write.",
            "Number of global secondary indexes, since each one copies writes.",
            "Storage, which TTL keeps small by expiring the 48-hour items.",
            "Capacity mode: on-demand for spiky or small loads, provisioned with auto scaling for steady, high loads.",
        ],
        "traps": [
            "Writing every sensor reading turns a $50 table into a $5,000 one at larger scale.",
            "A GSI that projects all attributes doubles the write bill without anyone noticing.",
            "Point-in-time recovery and on-demand backups are billed per GB and are easy to leave on for disposable tables.",
            "Strongly consistent reads cost twice as much as eventually consistent ones; the live board rarely needs them.",
            "Global tables bill replicated writes in every Region; do not replicate a disposable live store by default.",
        ],
    },
    "security": [
        "Use IAM policies scoped to the table and, where useful, to key prefixes with the dynamodb:LeadingKeys condition, so the Flink role can write and the Lambda role can only read.",
        "Data is encrypted at rest by default; use a customer managed KMS key if your policy requires one key per domain, and note that KMS requests add a small cost.",
        "Reach DynamoDB from private subnets through a gateway VPC endpoint, so traffic never leaves the AWS network and no NAT gateway is needed.",
        "CloudTrail logs control-plane calls by default; turn on data-event logging for the table if you must audit who read or wrote items.",
        "Keep personal data out of the live store: press and line identifiers and readings only. If operators' names appear, mask them in Flink before writing.",
        "Turn on deletion protection for the table so an infrastructure change cannot drop it by mistake.",
    ],
    "monitor": [
        ("ThrottledRequests", "Requests DynamoDB rejected because a key or the table hit its limit; any sustained value means a hot key or too little capacity."),
        ("WriteThrottleEvents", "Writes throttled per table or index; alarm on it for the live store, since a throttled write is a stale screen."),
        ("ConsumedWriteCapacityUnits", "Write units actually used; compare with the expected changes-only rate to catch a job writing every reading."),
        ("SuccessfulRequestLatency", "Time DynamoDB takes to answer; it should stay in single-digit milliseconds for key lookups."),
        ("TimeToLiveDeletedItemCount", "Items removed by TTL; if it is zero for a day, expiry is misconfigured and the table will grow."),
        ("IteratorAge (on the stream's Lambda)", "How far behind the change consumer is; rising values mean screens are lagging."),
    ],
    "limits": [
        ("Item size", "400 KB per item, including attribute names"),
        ("Default throughput per table", "40,000 read and 40,000 write units per second, adjustable"),
        ("Per partition", "About 3,000 read units and 1,000 write units per second for one partition"),
        ("Global secondary indexes", "20 per table by default"),
        ("Tables per Region", "2,500 by default"),
        ("DynamoDB Streams", "Records kept for 24 hours; design for at most two readers per shard"),
    ],
    "decisions": [
        ("Live board for 120 presses, latest values plus a 48-hour chart", "DynamoDB on-demand, changes only, TTL 48 hours, Streams to Lambda to WebSocket",
         "Pursue: the site's recommended live store at about $50 a month, with true push."),
        ("Metadata database for sources, rules, watermarks and run logs", "DynamoDB",
         "Drop: key-value with no joins, so no merged view and no keys between tables; Lakebase was chosen."),
        ("Policy requires every store to be in Unity Catalog", "Lakebase as the live store, screen polls every second",
         "Pursue with care: governed end to end, but costs more and the app must poll."),
        ("Screens need any filter on any column over 48 hours", "DynamoDB",
         "Drop: no ad hoc slicing; use ClickHouse Cloud for that need."),
        ("Retail order-status lookups for a customer app", "DynamoDB keyed by order id",
         "Pursue with care: a good fit for an application store, but it belongs to the app team, not the data platform."),
    ],
    "faq": [
        ("Is DynamoDB governed by Unity Catalog?",
         "No. It is not governed by Unity Catalog and is not a Lakehouse Federation source. The site accepts it for a 48-hour disposable copy because the governed record of the same data lives in bronze, silver and gold."),
        ("Can I query DynamoDB with SQL?",
         "Partly. PartiQL gives a SQL-like syntax, but it still works by key; a statement without a key filter becomes a full scan, which is slow and expensive. For analytics, export to S3 and query there."),
        ("Why not use DynamoDB as the metadata database?",
         "Metadata is relational: datasets refer to sources, rules refer to datasets, and the merged view joins them. DynamoDB has no joins or foreign keys. The site chose Lakebase, a managed PostgreSQL."),
        ("How do I get DynamoDB data into the lakehouse?",
         "Use export to S3 (full or incremental) and read the files with Databricks, or read the change stream. On this platform the live store's data does not need to flow back, because the platform lane builds the same tables from Kinesis."),
        ("On-demand or provisioned?",
         "Start with on-demand. Move to provisioned with auto scaling only when traffic is steady and the bill shows a clear saving."),
    ],
    "sources": [
        ("AWS docs: Quotas in Amazon DynamoDB", "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ServiceQuotas.html"),
        ("AWS docs: What is Amazon DynamoDB?", "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html"),
        ("AWS docs: Time to Live (TTL)", "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/TTL.html"),
        ("AWS pricing: Amazon DynamoDB", "https://aws.amazon.com/dynamodb/pricing/"),
        ("AWS What's New: DynamoDB bulk put items (Nov 2026)", "https://aws.amazon.com/about-aws/whats-new/2026/11/amazon-dynamodb-now-supports-bulk-put-items/"),
    ],
    "related": [
        ("Streaming on AWS and Databricks", "/learn/streaming/"),
        ("Databricks real-time mode", "/learn/streaming/real-time-mode/"),
        ("Metadata store", "/learn/data-platform-architecture/metadata-store/"),
        ("Amazon DynamoDB Streams", "svc:dynamodb-streams"),
        ("Amazon API Gateway", "svc:api-gateway"),
        ("Amazon ElastiCache", "svc:elasticache"),
    ],
}
