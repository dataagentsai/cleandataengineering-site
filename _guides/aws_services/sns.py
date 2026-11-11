SERVICE = {
    "slug": "sns",
    "name": "Amazon Simple Notification Service (SNS)",
    "short": "SNS",
    "group": "streaming",
    "one_line": "A managed publish and subscribe service that pushes each message to every subscriber: queues, functions, email, SMS and HTTPS endpoints.",
    "status": "Generally available. The default maximum message size is still 256 KiB, but a topic can now be set to accept up to 1 MiB.",
    "checked": "2026-11-11",
    "site_verdict": ("Pursue",
                     "Pursue for alerts: CloudWatch alarms on the AWS movers page on-call through SNS, and the fast lane sends SMS and "
                     "email alerts through it. Drop it as a log for analytics: SNS pushes and forgets, so standard topics have no replay "
                     "and no reader can catch up later. Kinesis Data Streams carries the events."),
    "equivalents": {"azure": "Event Grid (and Azure Monitor action groups for alerts)",
                    "gcp": "Pub/Sub push subscriptions (and Cloud Monitoring notification channels)",
                    "databricks": "none: Databricks job and SQL alert notifications cover alerts inside Databricks",
                    "open_source": "Apache Kafka for fan-out, or Alertmanager for alerts"},
    "plain": [
        "Amazon SNS is a publish and subscribe service. A producer publishes a message to a topic, which is a named channel such as "
        "plant-alerts. Every subscriber to that topic receives its own copy straight away. Subscribers can be SQS queues, Lambda "
        "functions, Amazon Data Firehose streams, HTTPS endpoints, email addresses, phone numbers for SMS, and mobile apps. The "
        "producer does not know or care who is listening; adding a new subscriber needs no change to the producer.",
        "SNS pushes. It does not wait for subscribers to ask. If a subscriber is down, SNS retries for a while according to a delivery "
        "policy, and after that the message can go to a dead-letter queue, which is an SQS queue that catches failed deliveries. A "
        "standard topic does not keep messages after delivery. That is the key difference from a log such as Kinesis: once SNS has "
        "delivered, there is nothing left to re-read.",
        "Subscribers can also filter. A filter policy is a small JSON rule on a subscription, such as only messages where severity is "
        "critical and plant is Pune. SNS checks each message against each filter and delivers only matches. There are also FIFO "
        "topics, which keep strict order per message group, remove duplicates and, unlike standard topics, can archive messages and "
        "replay them to subscribers.",
        "A concrete example from a manufacturing plant: a CloudWatch alarm watches how far behind the readers of the sensor stream "
        "are. When the lag passes five minutes, the alarm publishes to an SNS topic called platform-oncall. That topic sends an SMS to "
        "the engineer on call, an email to the data team list, and a copy to an SQS queue that a small function reads to open a "
        "ticket. One alarm, three channels, no custom code in the alarm.",
    ],
    "analogy": "A public address system in a factory: one announcement, heard at once by everyone tuned in, and not recorded for later.",
    "big_picture": [
        "On the reference platform SNS lives in the observability and alerting corner, not in the data lanes. The platform design "
        "routes CloudWatch alarms for the AWS movers, such as DMS lag, AppFlow failures, SiteWise ingestion and Kinesis reader delay, "
        "to on-call through Amazon SNS. Databricks job notifications and SQL alerts cover what happens inside Databricks, and both "
        "end up in the same team channel and pager.",
        "In the streaming fast lane, SNS is one of the alert outlets. The site's streaming design lists SNS for SMS and email and "
        "EventBridge for routing to ticketing and chat tools, both marked Pursue for alerts. In the lightest fast-lane option, Kinesis "
        "readings go to a Lambda that checks limits and publishes to SNS when a press runs too hot, with no Flink at all.",
        "SNS also appears in plumbing you may not build yourself. Databricks Auto Loader, in file notification mode, can set up S3 "
        "event notifications that flow through SNS into SQS, so that several queues can receive the same bucket events. What SNS is "
        "not, here, is a source for analytics. The site's verdict is that SQS, SNS and EventBridge are dropped as the log, because a "
        "pushed message cannot be replayed or read by a second consumer that joins later.",
    ],
    "upstream": ["svc:cloudwatch", "svc:lambda", "svc:s3"],
    "downstream": ["svc:sqs", "svc:lambda", "Email, SMS and HTTPS endpoints"],
    "concepts": [
        ("Topic", "A named channel that producers publish to; SNS delivers each message to every subscription on it."),
        ("Subscription", "One endpoint attached to a topic: an SQS queue, a Lambda function, a Firehose stream, an HTTPS URL, an email address, a phone number or a mobile app."),
        ("Fan-out", "The pattern of sending one message to many consumers at once, typically several SQS queues that each process it in their own way."),
        ("Filter policy", "A JSON rule on a subscription that lets through only messages whose attributes or body match, so each subscriber gets only what it needs."),
        ("Delivery policy", "Rules for how often and how long SNS retries an HTTPS endpoint that fails before giving up."),
        ("Dead-letter queue", "An SQS queue attached to a subscription that keeps messages SNS could not deliver, so they are not silently lost."),
        ("FIFO topic", "A topic that keeps strict order per message group, removes duplicates, and can archive and replay messages; it delivers only to SQS queues and a few other targets."),
        ("Message archiving and replay", "A FIFO-only feature that keeps published messages for a set period so a subscriber can ask for them again."),
    ],
    "use_when": [
        "Use it to send alarm notifications from CloudWatch to the people on call by SMS, email or a paging tool's HTTPS endpoint.",
        "Use it to fan one event out to several SQS queues, so each team or function processes the same notice independently.",
        "Use it when a simple rule-based alert in the fast lane, such as pressure above limit, must reach operators' phones within seconds.",
        "Use it to deliver S3 event notifications to more than one queue, for example one for Auto Loader and one for an audit function.",
        "Use a FIFO topic with SQS FIFO queues when several services must receive the same commands in the same order.",
    ],
    "avoid_when": [
        "Avoid it as the event log for analytics: a standard topic keeps nothing after delivery, so there is no replay and no late-joining reader.",
        "Avoid it for high-volume sensor data; per-message and per-delivery charges add up, and Kinesis is designed for that volume.",
        "Avoid it as the main channel to a chat tool or incident system when you need content-based routing to many SaaS targets; EventBridge API destinations do this better.",
        "Avoid SMS for anything non-critical: it costs per message, has a low default spend limit and country-specific rules.",
    ],
    "challenges": [
        ("Alert storms",
         "A flapping alarm or a broken check publishes hundreds of messages, phones buzz all night and people start to ignore alerts.",
         "Alarm on sustained conditions with several evaluation periods, use composite alarms, and send only critical severity to SMS."),
        ("SMS stops sending",
         "New accounts start in the SMS sandbox and have a spend threshold of 1 US dollar a month, so alerts silently stop once it is reached.",
         "Leave the sandbox, raise the spend threshold through a quota request, and alarm on SMSMonthToDateSpentUSD and NumberOfNotificationsFailed."),
        ("Email delivery throttled",
         "Email subscriptions are limited to 10 messages a second each, a hard limit; a burst of alerts queues up or fails.",
         "Use email only for summaries; send bursts to an SQS queue or a paging service over HTTPS."),
        ("Lost deliveries",
         "An HTTPS subscriber is down longer than the retry policy, and messages are dropped with only a metric to show for it.",
         "Attach a dead-letter queue to every important subscription and alarm on NumberOfNotificationsRedrivenToDlq."),
        ("Unconfirmed subscriptions",
         "Email and HTTPS subscriptions must be confirmed; someone forgets, and the on-call list never gets alerts.",
         "Use SQS or Lambda subscriptions for machine paths, review pending subscriptions, and test alerts with a monthly fire drill."),
        ("Filter policy mistakes",
         "A typo in a filter policy means a subscriber receives nothing, or everything.",
         "Keep filter policies in infrastructure code, test them with sample messages, and watch NumberOfNotificationsFilteredOut."),
        ("Message too large",
         "Alert messages that include full payloads exceed the default 256 KiB and publishing fails.",
         "Send a short summary and a link; if needed raise the topic's MaximumMessageSize to 1 MiB or use the extended client with S3."),
    ],
    "compare": [
        ("Amazon EventBridge",
         "You need routing on any field of the event, many SaaS and AWS targets, schedules, or the new bus with retention and ordered delivery.",
         "You need the simplest fast push to SMS, email, mobile and many SQS queues."),
        ("Amazon SQS",
         "A single consumer must pull work at its own pace and retry until done.",
         "Several consumers each need their own copy of every message; put SNS in front of several queues."),
        ("Kinesis Data Streams",
         "The events are data that analytics needs, with replay and several independent readers.",
         "The events are alerts or notices to push to people and functions."),
        ("Azure Event Grid and Monitor action groups",
         "The platform runs on Azure.",
         "You are on AWS: CloudWatch alarms call SNS directly."),
        ("Google Pub/Sub push subscriptions",
         "The platform runs on Google Cloud.",
         "You are on AWS."),
        ("Databricks job and SQL alert notifications",
         "The alert is about something inside Databricks, such as a failed job or a quality check.",
         "The alert comes from an AWS mover or a CloudWatch alarm; SNS is the native path."),
    ],
    "cost": {
        "model": "SNS bills per publish request and per delivery. Each 64 KB chunk of a published message counts as one request. "
                 "Deliveries are priced by endpoint type: deliveries to SQS and Lambda carry no per-message charge, though data "
                 "transfer is billed, HTTPS and email deliveries carry a small per-million charge, and SMS and mobile push are priced "
                 "per message by destination country and carrier. FIFO topics are billed on published messages, on subscription "
                 "messages and on payload data. Filtering on attributes is free; filtering on the message body is billed on data "
                 "scanned. FIFO archiving is billed on data stored and days kept. Use list prices from the pricing page and check your region.",
        "drivers": [
            "The number of messages published and their size in 64 KB chunks.",
            "The number of subscriptions each message is delivered to, and their endpoint types.",
            "SMS volume and destination countries, usually the biggest line for alerting.",
            "FIFO archiving retention and replays, if used.",
        ],
        "traps": [
            "An alert storm sent by SMS can cost more in a night than the topic costs in a year.",
            "Fan-out multiplies cost: one message to 20 subscriptions is 20 deliveries.",
            "Using SNS to carry sensor readings bills every reading, where Kinesis bills by throughput.",
            "Data transfer to HTTPS endpoints outside AWS is charged on top of delivery charges.",
        ],
    },
    "security": [
        "Control who can publish and subscribe with IAM and a topic access policy; allow CloudWatch or S3 to publish only with aws:SourceArn and aws:SourceAccount conditions.",
        "Turn on server-side encryption with a KMS key; publishers such as CloudWatch alarms then need permission to use that key, a common cause of silent failures.",
        "Use an interface VPC endpoint for SNS so functions and clusters in private subnets publish without going through a NAT gateway.",
        "Require HTTPS endpoints for webhook subscriptions and verify SNS message signatures on the receiving side.",
        "SNS data protection policies can detect and mask personal data such as phone numbers or emails in messages; keep alert text free of customer details anyway.",
        "Publish and subscription changes are recorded in CloudTrail; review who can add subscriptions, because a new email subscriber receives every alert.",
    ],
    "monitor": [
        ("NumberOfMessagesPublished", "How many messages reached the topic; a sudden spike signals an alert storm."),
        ("NumberOfNotificationsDelivered", "Successful deliveries to subscribers."),
        ("NumberOfNotificationsFailed", "Deliveries that failed after retries; alarm on any value for the on-call topic."),
        ("NumberOfNotificationsFilteredOut", "Messages dropped by filter policies; a sudden change points to a filter or attribute change."),
        ("NumberOfNotificationsRedrivenToDlq", "Messages that went to a dead-letter queue because delivery failed."),
        ("SMSMonthToDateSpentUSD", "SMS spend so far this month; alarm before it reaches the account spend threshold."),
    ],
    "limits": [
        ("Message size", "256 KiB by default; up to 1 MiB with the topic's MaximumMessageSize attribute; up to 2 GB through S3 with the extended client"),
        ("Subscriptions per topic", "12,500,000 for standard topics; 100 for FIFO topics"),
        ("Filter policies", "200 per topic and 10,000 per account"),
        ("Email delivery", "10 messages per second per email subscription, a hard limit"),
        ("SMS spend threshold", "1 US dollar per account by default; raised by quota request"),
        ("Publish rate", "Varies by region: 30,000 messages per second in US East (N. Virginia), 1,500 in Mumbai and several others, 300 in smaller regions for standard topics"),
    ],
    "decisions": [
        ("CloudWatch alarm on Kinesis reader lag must reach the on-call engineer",
         "SNS topic with SMS, email and an HTTPS subscription to the paging tool",
         "Pursue: native from CloudWatch, seconds to deliver, almost no cost at alert volumes."),
        ("Press temperature above limit must reach the shift supervisor's phone",
         "Lambda reading Kinesis publishes to an SNS topic filtered by plant",
         "Pursue: the light fast-lane option; filter policies route each plant's alerts to its own people."),
        ("Dealer app events that the lakehouse should ingest",
         "Publish every event to SNS and subscribe a queue for the lakehouse",
         "Drop: no replay and per-message charges; send to Firehose or Kinesis instead."),
        ("Alerts must open tickets in the IT service desk and post to Teams with routing by severity",
         "EventBridge with API destinations, SNS only for SMS",
         "Pursue with care: EventBridge handles content routing to SaaS; keep SNS for phones and email."),
    ],
    "faq": [
        ("What is the difference between SNS and SQS?",
         "SNS pushes one message to many subscribers at once; SQS holds messages until one consumer pulls and deletes each one. "
         "They are often used together: SNS fans a message out to several SQS queues, and each queue's consumer works at its own pace."),
        ("Can SNS replay messages?",
         "Only FIFO topics, which support message archiving and replay to subscribers. Standard topics keep nothing after delivery. "
         "For data that analytics may need to re-read, use Kinesis Data Streams or Kafka."),
        ("What is the SNS message size limit?",
         "256 KiB by default. You can raise a topic's MaximumMessageSize attribute to 1 MiB, and use the extended client library to "
         "send payloads up to 2 GB through S3."),
        ("Why did my SNS SMS alerts stop?",
         "Most often the account is still in the SMS sandbox or has hit the default monthly spend threshold of 1 US dollar. Request "
         "production access and a higher spend limit, and alarm on SMSMonthToDateSpentUSD."),
        ("Should I use SNS or EventBridge for alerts?",
         "Use SNS for direct push to SMS, email and SQS. Use EventBridge when alerts must be routed by their content to many "
         "targets such as ticketing systems or chat tools. Many platforms use both, as this site's design does."),
    ],
    "sources": [
        ("AWS General Reference: Amazon SNS endpoints and quotas", "https://docs.aws.amazon.com/general/latest/gr/sns.html"),
        ("AWS docs: Publishing large messages with Amazon SNS", "https://docs.aws.amazon.com/sns/latest/dg/large-message-payloads.html"),
        ("AWS docs: Amazon SNS message archiving and replay for FIFO topics", "https://docs.aws.amazon.com/sns/latest/dg/message-archiving-and-replay-topic-owner.html"),
        ("Amazon SNS pricing", "https://aws.amazon.com/sns/pricing/"),
    ],
    "related": [
        ("Streaming on AWS and Databricks", "/learn/streaming/"),
        ("Streaming options compared", "/learn/streaming/options/"),
        ("AWS and Databricks reference platform", "/learn/data-platform-architecture/aws-databricks/"),
        ("Amazon SQS", "svc:sqs"),
        ("Amazon EventBridge", "svc:eventbridge"),
        ("Amazon CloudWatch", "svc:cloudwatch"),
    ],
}
