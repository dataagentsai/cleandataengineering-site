SERVICE = {
    "slug": "sqs",
    "name": "Amazon Simple Queue Service (SQS)",
    "short": "SQS",
    "group": "streaming",
    "one_line": "A managed queue that holds work items until one worker takes, finishes and deletes each one; no replay once read.",
    "status": "Generally available. The maximum message size was raised from 256 KiB to 1 MiB in August 2025, and standard queues gained fair queues.",
    "checked": "2026-11-11",
    "site_verdict": ("Pursue with care",
                     "Pursue for the S3 event notifications that tell Databricks Auto Loader a new file has landed, and as a work "
                     "queue or dead-letter queue beside Lambda and the movers. Drop it as the analytics log: a message is deleted once "
                     "it is read, so there is no replay, no second reader and no order per key. Kinesis Data Streams is the belt."),
    "equivalents": {"azure": "Azure Queue Storage or Service Bus queues",
                    "gcp": "Pub/Sub (pull subscriptions) or Cloud Tasks",
                    "databricks": "none: Auto Loader file notification mode creates and reads an SQS queue for you",
                    "open_source": "RabbitMQ, or Redis lists for small cases"},
    "plain": [
        "Amazon SQS is a queue that AWS runs for you. A queue is a waiting line for small pieces of work, called messages. One program, "
        "the producer, puts a message on the queue. Another program, the consumer, takes the message off, does the work and then "
        "deletes it. Until it is deleted, the message stays safely on the queue, even if the consumer crashes halfway through. There "
        "are no servers to size: you create a queue with one API call and pay per request.",
        "The key idea is the visibility timeout. When a consumer receives a message, SQS hides it from every other consumer for a "
        "set time, 30 seconds by default and up to 12 hours. If the consumer finishes and deletes the message in that time, the work "
        "is done. If it crashes, the message becomes visible again and another consumer picks it up. This is how SQS gives at-least-once "
        "delivery: every message is processed at least once, and occasionally twice, so consumers must be able to cope with a repeat.",
        "There are two kinds of queue. A standard queue accepts nearly unlimited throughput but makes no promise about order and may "
        "deliver a message more than once. A FIFO queue (first in, first out) keeps strict order within a message group and removes "
        "duplicates sent within five minutes, at a lower throughput. Messages can be kept from 60 seconds to 14 days; the default is "
        "four days.",
        "A concrete example from a retail data platform: every time a supplier drops a price file into the landing bucket in S3, S3 "
        "sends a small notification message to an SQS queue saying which file arrived. Databricks Auto Loader reads that queue, learns "
        "the exact file names, ingests them into bronze and deletes the messages. Nobody has to list millions of files in the bucket to "
        "find what is new.",
    ],
    "analogy": "A ticket rail in a restaurant kitchen: each order slip is taken by one cook, and the slip goes in the bin once the dish is out.",
    "big_picture": [
        "On the reference platform SQS is plumbing, not a lane. Its main job is in the batch and file path: S3 event notifications "
        "from the landing buckets go to SQS, and Auto Loader in file notification mode reads the queue to discover new files from DMS, "
        "AppFlow, Transfer Family and Firehose. The site's streaming design describes this as S3 used as micro-batch landing: Firehose "
        "writes a file every minute or so, S3 notifies SQS, and Auto Loader picks the file up within one to three minutes.",
        "Its second job is as a buffer and a safety net for small AWS-side functions. A Lambda that fails to process an event can send "
        "it to a dead-letter queue, a separate queue that keeps failed messages for someone to inspect and replay by hand. EventBridge "
        "Pipes and Lambda can read from SQS to smooth out bursts so that a downstream API is not overloaded.",
        "What SQS is not, on this platform, is the event log. The site's verdict is explicit: queues such as SQS, SNS and EventBridge "
        "are dropped as the analytics source because a queue deletes a message once it is read. That means no replay after a bug, no "
        "second independent reader such as the live lane and the platform lane both reading the same sensor readings, and no order per "
        "key. Plant readings and app events go to Kinesis Data Streams instead, which keeps them for seven days for every reader.",
    ],
    "upstream": ["svc:s3", "svc:lambda", "svc:eventbridge"],
    "downstream": ["Databricks Auto Loader (file notification mode)", "svc:lambda", "svc:eventbridge"],
    "concepts": [
        ("Message", "One piece of work or one notice, up to 1 MiB of text such as JSON, plus up to 10 metadata attributes."),
        ("Standard queue", "The default queue type: very high throughput, best-effort order, and at-least-once delivery, so a message can occasionally arrive twice."),
        ("FIFO queue", "First in, first out: strict order within each message group and removal of duplicates sent within a five-minute window, at lower throughput."),
        ("Visibility timeout", "How long a received message stays hidden from other consumers while one consumer works on it; 30 seconds by default, up to 12 hours."),
        ("Dead-letter queue", "A second queue where messages go after failing a set number of times, so one bad message does not block or loop forever."),
        ("Long polling", "A receive call that waits up to 20 seconds for a message to arrive instead of returning empty at once; it cuts empty requests and cost."),
        ("Message group ID", "A label on a message. In FIFO queues it defines the unit of ordering; in standard queues it turns on fair queues, so one noisy tenant cannot starve the others."),
        ("Retention period", "How long an unread message is kept before SQS deletes it: from 60 seconds to 14 days, four days by default."),
    ],
    "use_when": [
        "Use it to receive S3 event notifications for a landing bucket so that Auto Loader can find new files without listing the whole bucket.",
        "Use it as a dead-letter queue for Lambda functions, EventBridge targets and SNS subscriptions, so failed events are kept and can be inspected.",
        "Use it to put a buffer between a bursty producer and a slow consumer, such as webhook calls that trigger a rate-limited partner API.",
        "Use a FIFO queue when a small stream of commands must be processed strictly in order per key, for example status changes for one order.",
        "Use it to fan work out to many workers, where each item needs to be done once and order does not matter, such as resizing product images.",
    ],
    "avoid_when": [
        "Avoid it as the event log for analytics: a message is gone once read, so you cannot replay after a bug or add a second reader later.",
        "Avoid it when two independent consumers need the same events, such as a live alert lane and a lakehouse lane; use Kinesis Data Streams or Kafka.",
        "Avoid it for high-volume sensor readings where order per machine matters and you need to re-read history; a FIFO queue's throughput and lack of replay do not fit.",
        "Avoid it for payloads larger than 1 MiB unless you store the payload in S3 and send only a pointer, which the extended client library does for you.",
    ],
    "challenges": [
        ("Duplicate processing",
         "A standard queue can deliver a message twice, and a consumer that times out also causes a repeat, so a row can be written twice.",
         "Make every consumer idempotent: upsert by a business key or record the message ID; Auto Loader already tracks files it has ingested."),
        ("Visibility timeout too short",
         "Work takes longer than the timeout, the message reappears, a second worker starts the same job, and work is done twice or fails.",
         "Set the timeout to at least six times the function timeout for Lambda; extend it with ChangeMessageVisibility for long jobs."),
        ("Poison message loop",
         "One malformed message fails every time, is retried until retention runs out, and wastes compute or blocks a FIFO group.",
         "Attach a dead-letter queue with a sensible maxReceiveCount such as 5, alarm on its depth, and use redrive to send fixed messages back."),
        ("Silent backlog",
         "Consumers fall behind or stop, messages pile up and quietly expire after the retention period, and files are never ingested.",
         "Alarm on ApproximateAgeOfOldestMessage, not just queue depth; raise retention to 14 days for notification queues."),
        ("Missed S3 notifications",
         "Someone edits the bucket notification configuration, events stop flowing, and Auto Loader sees nothing new.",
         "Manage notifications in infrastructure code, alarm when NumberOfMessagesSent drops to zero during working hours, and run a periodic Auto Loader backfill."),
        ("FIFO throughput ceiling",
         "A FIFO queue without high-throughput mode allows 300 calls per second per action; a busy producer is throttled.",
         "Turn on high-throughput FIFO, batch 10 messages per call, and spread work across many message group IDs."),
        ("Empty receives costing money",
         "Consumers poll an idle queue with short polling, making millions of empty requests that are still billed.",
         "Use long polling with WaitTimeSeconds of 20; Lambda event source mappings already do this for you."),
        ("Using SQS as the log",
         "A team points the analytics pipeline at a queue; months later a bug needs a replay and the data no longer exists.",
         "Keep the record in Kinesis or in bronze tables; SQS only carries notices and work items."),
    ],
    "compare": [
        ("Kinesis Data Streams",
         "Many readers need the same ordered events and you want to replay up to a year back.",
         "Each item is a job for one worker and should disappear once done."),
        ("Amazon SNS",
         "One event must be pushed to many subscribers at once, such as email, SMS and several queues.",
         "A consumer must pull work at its own pace and retry until it succeeds."),
        ("Amazon EventBridge",
         "You need content-based routing of events to many AWS targets, schedules, or the new bus with retention and ordered delivery.",
         "You need a plain, cheap buffer between one producer and one consumer."),
        ("Azure Queue Storage or Service Bus",
         "The platform runs on Azure; Service Bus adds sessions for ordering, similar to FIFO.",
         "You are on AWS: SQS is the native choice and S3 notifies it directly."),
        ("Google Pub/Sub",
         "The platform runs on Google Cloud; one service covers both queue and fan-out patterns.",
         "You are on AWS."),
        ("Auto Loader directory listing mode",
         "File volumes are small or you cannot create queues and notifications in the account.",
         "Buckets hold millions of files; listing them on every run is slow and costly, so file notification mode with SQS wins."),
    ],
    "cost": {
        "model": "SQS is billed per request. Every send, receive, delete and change-visibility call is a request, and each 64 KB chunk "
                 "of a payload counts as one request, so a 256 KB message costs four. A batch of up to 10 messages is one request if "
                 "it stays under the size chunk. FIFO requests cost more than standard requests. There is a monthly free tier of one "
                 "million requests. Data transfer out of the region is billed separately. Check the pricing page for your region's "
                 "list price.",
        "drivers": [
            "The number of API calls, including empty receives from polling an idle queue.",
            "Message size, because every 64 KB chunk is billed as a separate request.",
            "FIFO versus standard: FIFO requests carry a higher per-request price.",
            "Encryption with a customer managed KMS key, which adds KMS request charges unless key reuse is configured.",
        ],
        "traps": [
            "Short polling on idle queues turns into millions of billed empty receives; use long polling.",
            "Large messages sent one by one cost several requests each; batch them or store payloads in S3.",
            "A customer managed KMS key with a short data key reuse period multiplies KMS calls; raise KmsDataKeyReusePeriodSeconds.",
            "Retries caused by a short visibility timeout double both SQS and downstream compute charges.",
        ],
    },
    "security": [
        "Access is controlled by IAM policies on producers and consumers plus a queue policy; the S3 bucket needs permission in the queue policy to send notifications, scoped with aws:SourceArn and aws:SourceAccount.",
        "Turn on server-side encryption: SSE-SQS with AWS owned keys is the default, or use SSE-KMS with the platform's customer managed key when audit requires it; the S3 notification then needs kms:GenerateDataKey on that key.",
        "Use an interface VPC endpoint for SQS so Databricks clusters and Lambda functions in private subnets reach the queue without a NAT gateway or public internet.",
        "API calls are recorded in CloudTrail; queue policies should deny any request that does not use TLS with aws:SecureTransport.",
        "Messages are notices, not data: keep personal data out of them and send only an S3 key or a record ID, so the queue never holds customer details for 14 days.",
    ],
    "monitor": [
        ("ApproximateAgeOfOldestMessage", "How long the oldest message has waited; the best single signal that consumers have stalled or fallen behind."),
        ("ApproximateNumberOfMessagesVisible", "The backlog waiting to be received; compare with normal levels for the time of day."),
        ("ApproximateNumberOfMessagesNotVisible", "Messages in flight with a consumer; a steady climb means work is timing out or hanging."),
        ("NumberOfMessagesSent", "Arrivals; a drop to zero on a notification queue usually means the S3 event configuration broke."),
        ("NumberOfEmptyReceives", "Receive calls that returned nothing; high values mean short polling is wasting money."),
        ("Dead-letter queue depth", "ApproximateNumberOfMessagesVisible on the dead-letter queue; any value above zero should alert someone."),
    ],
    "limits": [
        ("Message size", "1 MiB (1,048,576 bytes); larger payloads go through S3 with the extended client library, up to 2 GB"),
        ("Retention", "60 seconds to 14 days; default 4 days"),
        ("Visibility timeout", "0 seconds to 12 hours; default 30 seconds"),
        ("Batch size", "Up to 10 messages per send, receive or delete batch"),
        ("FIFO throughput", "300 calls per second per action per partition without high-throughput mode; high-throughput mode up to 70,000 calls per second in the largest regions"),
        ("Delivery delay", "0 to 15 minutes per message or per queue"),
    ],
    "decisions": [
        ("New supplier files in a landing bucket that holds millions of objects",
         "S3 event notifications to SQS, read by Auto Loader in file notification mode",
         "Pursue: finds new files in seconds without listing the bucket; Auto Loader can create the queue and notifications for you."),
        ("Lambda that sends alert messages to a partner API sometimes fails",
         "SQS dead-letter queue with an alarm on its depth",
         "Pursue: failures are kept for 14 days and can be redriven once the partner is back."),
        ("Plant sensor readings that both the live lane and the lakehouse need",
         "SQS as the shared stream",
         "Drop: a queue deletes each message once read, so there is no second reader and no replay; use Kinesis Data Streams."),
        ("Order status changes that must be applied in order per order number",
         "SQS FIFO queue with the order number as message group ID",
         "Pursue with care: fine for an operational service; for analytics, take the changes through DMS into bronze instead."),
    ],
    "faq": [
        ("What is the difference between SQS and Kinesis?",
         "SQS is a queue: each message is taken by one consumer and deleted once processed. Kinesis Data Streams is a log: records stay "
         "for a set time, any number of readers can read them at their own pace, and they can re-read history. Use SQS for jobs and "
         "notices, Kinesis for event data that analytics needs."),
        ("What is the maximum SQS message size?",
         "1 MiB since August 2025, up from 256 KiB. For larger payloads, put the data in S3 and send a pointer; the SQS extended client "
         "library does this automatically, up to 2 GB."),
        ("Does Databricks Auto Loader use SQS?",
         "Yes, on AWS. In file notification mode Auto Loader subscribes to S3 event notifications through SNS and SQS, which it can set "
         "up for you, or it can use a queue you provide. This avoids listing large buckets on every run."),
        ("Can SQS replay messages?",
         "No, not in the way a log can. Once a message is deleted it is gone. A dead-letter queue redrive moves failed messages back, "
         "but there is no way to re-read messages that were processed successfully."),
        ("Does SQS guarantee exactly-once delivery?",
         "Standard queues deliver at least once, so duplicates can happen. FIFO queues remove duplicates sent within five minutes, but "
         "a consumer that times out can still process a message twice. Design consumers to be idempotent."),
    ],
    "sources": [
        ("AWS docs: Amazon SQS message quotas", "https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/quotas-messages.html"),
        ("AWS docs: Amazon SQS visibility timeout", "https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html"),
        ("AWS docs: Amazon SQS fair queues", "https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-fair-queues.html"),
        ("Amazon SQS pricing", "https://aws.amazon.com/sqs/pricing/"),
    ],
    "related": [
        ("Streaming on AWS and Databricks", "/learn/streaming/"),
        ("Common Ingestion Framework", "/learn/data-platform-architecture/ingestion/"),
        ("Amazon SNS", "svc:sns"),
        ("Amazon Kinesis Data Streams", "svc:kinesis-data-streams"),
        ("Amazon EventBridge", "svc:eventbridge"),
    ],
}
