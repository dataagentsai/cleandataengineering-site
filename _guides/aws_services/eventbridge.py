SERVICE = {
    "slug": "eventbridge",
    "name": "Amazon EventBridge (event buses, Pipes and Scheduler)",
    "short": "EventBridge",
    "group": "streaming",
    "one_line": "Serverless event router: buses match events to targets, Pipes link one source to one target, Scheduler fires timed calls.",
    "status": ("Generally available. On 24 Sep 2026 AWS relaunched custom event buses: the new Custom Event Bus keeps events for "
               "1 to 365 days, delivers in order per event group and uses subscribers, in 14 Regions at launch. The existing "
               "bus was renamed Custom Event Bus - Classic and keeps working unchanged. Event payloads up to 1 MB since early 2026."),
    "checked": "2026-11-11",
    "site_verdict": ("Pursue with care",
                     "Pursue for AWS-side triggers only: an S3 file arrived, a DMS task finished, a nightly start time, alarm "
                     "changes and webhooks routed to the right place. Drop it as the analytics log; Kinesis stays the stream belt "
                     "because Databricks and Flink read it natively, per key, at high volume. Lakeflow Jobs orchestrates everything "
                     "inside Databricks."),
    "equivalents": {"azure": "Event Grid, plus Logic Apps or Functions timers for schedules",
                    "gcp": "Eventarc, plus Cloud Scheduler",
                    "databricks": "Lakeflow Jobs triggers (schedule, file arrival, table update) for work inside Databricks",
                    "open_source": "CloudEvents with Knative Eventing, or cron plus a message broker"},
    "plain": [
        "An event is a small message that says something happened: a file landed, an order was paid, a database task finished, "
        "an alarm went red. Amazon EventBridge is AWS's serverless service for moving such events from the system that noticed "
        "them to the systems that should react, without the two knowing about each other. There are no servers or clusters to "
        "size; you pay per event or per byte.",
        "EventBridge has three parts. An event bus receives events from AWS services, from your applications and from software "
        "as a service partners such as Salesforce or Zendesk, and sends each one to every target whose filter matches. A pipe "
        "connects exactly one source, such as an SQS queue, a Kinesis stream or a DynamoDB stream, to exactly one target, with "
        "optional filtering and enrichment in between. Scheduler runs one-time or recurring calls, written as cron or rate "
        "expressions, against more than two hundred AWS services.",
        "A concrete example from a retail and manufacturing platform: a supplier drops a price file into the landing bucket. S3 "
        "sends an Object Created event to the default bus. A rule with the filter 'bucket is supplier-landing and key ends in "
        ".csv' starts a Lambda function that calls the Databricks Jobs API. Separately, a payment provider's webhook arrives "
        "through API Gateway onto a custom bus, and a rule sends it to Firehose so it lands as files in bronze. At two in the "
        "morning, a Scheduler schedule starts the nightly AppFlow flow that pulls SAP master data.",
        "The bus changed in September 2026. AWS launched a new Custom Event Bus that keeps every event for a period you choose, "
        "from one day to a year, delivers events in order within an event group, removes duplicates within five minutes, and "
        "lets each consuming team attach its own subscribers, including subscribers that start from a point in the past. The "
        "older rules-and-targets bus is now called Custom Event Bus - Classic and still works.",
    ],
    "analogy": "A building's mail room: letters arrive from everywhere, a clerk reads the address rules and drops copies into the right pigeonholes, and an alarm clock on the wall sends the scheduled ones.",
    "big_picture": [
        "On the reference platform EventBridge is the switchboard for AWS-side events, not a data pipe. The site's orchestration "
        "table rates it 'Pursue: for AWS-side triggers only' because it is small, serverless and cheap, and it can start a mover "
        "or call the Databricks Jobs API. Everything after the landing folder runs in Databricks under Lakeflow Jobs, so "
        "EventBridge never sequences silver and gold work.",
        "It carries four kinds of traffic. First, timed starts of movers through Scheduler, such as an AppFlow flow or a DMS "
        "task. Second, SaaS webhooks: low-volume, bursty events go from API Gateway to EventBridge, which routes and archives "
        "them, then to Firehose, S3 and bronze. Third, CloudWatch alarm state changes are routed to the same S3 path as the "
        "operational tables, so AWS-side alarms join one incident list with Databricks alerts. Fourth, fast-lane alerts, which "
        "go through EventBridge to ServiceNow or Teams, while SNS handles SMS and email.",
        "What it does not carry is sensor readings. The site's streaming design marks SQS, SNS and EventBridge as 'Drop as the "
        "log'. The new Custom Event Bus weakens one of the old reasons, since it now retains and replays events. Kinesis still "
        "stays the belt because Databricks and Flink have native Kinesis readers with checkpoints, a shard gives strict order "
        "per press at thousands of records a second, and the new bus is not yet in every Region the platform uses, for example "
        "Hyderabad, the disaster recovery Region. Revisit when it is.",
        "File arrival inside Databricks is a different case. The site drops the pattern 'S3 event, EventBridge, Lambda, run one "
        "job per file' because it bypasses Auto Loader's bookkeeping. Auto Loader with file notifications or Lakeflow file "
        "arrival triggers handles that instead.",
    ],
    "upstream": ["AWS services (S3, DMS, CloudWatch alarms)", "svc:api-gateway", "SaaS partners"],
    "downstream": ["svc:lambda", "svc:data-firehose", "svc:step-functions"],
    "concepts": [
        ("Event bus", "A router that receives events and passes them on. Every account has a default bus for AWS service events; you create custom buses for your own."),
        ("Custom Event Bus - Classic and rule", "The original bus. A rule holds an event pattern, a JSON filter, and up to five targets that receive matching events."),
        ("Custom Event Bus and subscriber", "The bus launched in September 2026. A subscriber holds filters and exactly one target, and can start from any point inside the bus's retention period."),
        ("Event group", "On the new bus, an id the publisher sets, such as an account number; events with the same id reach an ordered subscriber in sequence."),
        ("Archive and replay", "On the classic bus, a copy of matching events kept for a period you choose, which you can send back through the bus later."),
        ("Pipe", "A point-to-point link from one source, such as SQS, Kinesis or DynamoDB Streams, to one target, with optional filter, enrichment and transformation."),
        ("Schedule", "An EventBridge Scheduler entry that calls a target at a fixed time or on a cron or rate expression, with retries and a dead-letter queue."),
        ("API destination", "An HTTPS endpoint outside AWS, such as a ServiceNow API, that a rule or subscriber can call with stored credentials and a rate limit."),
        ("Dead-letter queue", "An SQS queue where events go after delivery retries are exhausted, so failures are kept rather than lost."),
    ],
    "use_when": [
        "You need to react to AWS service events, such as an S3 object created, a DMS task state change or an alarm changing state.",
        "You receive low-volume, bursty events from SaaS tools or webhooks and need to route them to several places with filters.",
        "You need reliable timed starts of AWS-side movers, such as a nightly AppFlow flow, without running a server for cron.",
        "You want to connect one queue or stream to one target with filtering, for example DynamoDB Streams to an alert service, without writing glue code.",
        "Several teams or accounts need their own view of the same business events; the new Custom Event Bus lets each attach subscribers.",
    ],
    "avoid_when": [
        "You need a high-volume, per-key ordered stream that Databricks and Flink read with checkpoints; use Kinesis Data Streams or MSK.",
        "You want to orchestrate Databricks tasks; Lakeflow Jobs does schedules, file arrival, table-update triggers and retries inside the platform.",
        "One run per arriving file would be started through the Jobs API; Auto Loader handles files with its own bookkeeping and no lost files.",
        "A workflow has many steps with waits and branches across AWS services; Step Functions is the better tool for that sequence.",
    ],
    "challenges": [
        ("Silent drops when targets fail",
         "A Lambda target errors or an API destination returns 500, retries run out after the default 24 hours or 185 attempts, and the event disappears.",
         "Attach a dead-letter queue to every rule target, subscriber and schedule; alarm on FailedInvocations and on messages in the dead-letter queue."),
        ("Events arrive more than once or out of order",
         "Delivery is at least once and, on the classic bus, unordered, so a 'task finished' event can trigger a job twice.",
         "Make targets idempotent, for example by keying runs on the event id; on the new bus use deduplication and event groups where order matters."),
        ("Invocation throttling",
         "A burst of S3 events exceeds the Region's invocation quota, around 1,100 a second in Mumbai on the classic bus, and deliveries are delayed.",
         "Watch ThrottledRules, batch at the source where possible, and request a quota increase before go-live."),
        ("Patterns that match too much or too little",
         "A broad pattern sends every S3 event in the account to Lambda; a typo in a field name matches nothing and nobody notices.",
         "Test patterns with TestEventPattern in CI, keep patterns narrow on bucket and prefix, and watch MatchedEvents per rule."),
        ("Infinite loops",
         "A target writes back to the source that produced the event, such as a Lambda writing to the same bucket prefix, and the rule fires forever.",
         "Write outputs to a different prefix or bucket, and add an alarm on unexpected growth in Invocations."),
        ("Pipeline logic hidden in rules",
         "Over time, routing, transformation and retries pile up in dozens of rules clicked together in the console, and nobody knows the real flow.",
         "Define buses, rules and schedules in Terraform or CDK next to the mover definitions, and keep business sequencing in Lakeflow Jobs."),
        ("New bus not available everywhere",
         "The Custom Event Bus launched in 14 Regions; a design that depends on it breaks in a Region it has not reached.",
         "Check Region availability for both primary and disaster recovery Regions before relying on retention or ordering."),
    ],
    "compare": [
        ("Amazon Kinesis Data Streams", "You need a high-volume stream with strict order per key, multiple readers with checkpoints, and native Databricks and Flink readers.", "You only route occasional events to a few targets; EventBridge needs no capacity planning."),
        ("Amazon SNS", "You need simple fan-out or human notifications by SMS, email or mobile push.", "You need content filtering across many sources, SaaS integrations, schedules or retention."),
        ("Databricks Lakeflow Jobs triggers", "The work runs in Databricks: schedules, file arrival and table updates start jobs with retries and history in system tables.", "The thing to start is an AWS service, such as AppFlow or a DMS task, or the event comes from outside Databricks."),
        ("AWS Step Functions", "A process has several AWS steps with waits, branches and error handling.", "You only need one event to start one action."),
        ("Azure Event Grid", "The platform is on Azure; Event Grid plays the same routing role.", "You are on AWS."),
        ("Google Eventarc and Cloud Scheduler", "The platform is on Google Cloud.", "You are on AWS."),
    ],
    "cost": {
        "model": ("Each part is billed on its own. On the classic bus you pay per million custom or partner events published, "
                  "counted in 64 KB chunks; most AWS service events on the default bus are free, and archives are billed per GB "
                  "stored plus per event replayed. The new Custom Event Bus is billed by data: bytes published, delivered to "
                  "subscribers and retained. Pipes are billed per million requests after filtering, Scheduler per million "
                  "invocations with a monthly free allowance, and API destinations per invocation. For the reference platform the "
                  "total is usually a few dollars a month (list price, check your region)."),
        "drivers": [
            "Number and size of custom events published, since each 64 KB chunk counts as one event on the classic bus.",
            "Retention period on the new bus, and archive size on the classic bus.",
            "Number of subscribers or targets each event is delivered to.",
            "What the targets cost, such as Lambda invocations or Databricks job runs started per event.",
        ],
        "traps": [
            "Using EventBridge to carry sensor readings turns a cheap router into one of the larger bills, and still gives no native Databricks reader.",
            "Starting one Databricks job run per file event multiplies compute start-up cost; batch with Auto Loader instead.",
            "A one-year retention on a busy new bus quietly stores every event for a year.",
            "Loops between a target and its own source can generate millions of events in hours.",
        ],
    },
    "security": [
        "Each rule target, subscriber, pipe and schedule uses an IAM role; give each one only the action it needs, such as lambda:InvokeFunction on one function.",
        "Use resource policies, or AWS RAM sharing on the new bus, for cross-account publishing, and restrict them to your AWS Organization.",
        "Encrypt buses, archives and schedules with the platform KMS key where customer-managed keys are supported.",
        "Reach EventBridge from private subnets through its VPC interface endpoint; store API destination credentials in connections, which keep them in Secrets Manager.",
        "CloudTrail logs control-plane changes such as PutRule, PutTargets and CreateSchedule, which shows who changed routing.",
        "Webhook payloads from SaaS tools can contain customer names and emails; filter or mask fields before they land in S3, and let Macie scan the landing bucket.",
    ],
    "monitor": [
        ("FailedInvocations", "Deliveries to a target that failed for good on the classic bus; any value needs a look."),
        ("InvocationsSentToDlq", "Events moved to the dead-letter queue after retries; pair with the queue depth alarm."),
        ("ThrottledRules", "Rule invocations delayed by the Region's invocation quota."),
        ("MatchedEvents and TriggeredRules", "Whether rules match what you expect; zero for a rule that should be busy points to a broken pattern."),
        ("IngestionToInvocationStartLatency", "Time from an event reaching the bus to delivery starting; rising values mean throttling or slow targets."),
        ("TargetErrorCount and InvocationDroppedCount", "Scheduler deliveries that failed or were dropped after retries."),
        ("ExecutionFailed", "Pipe executions that failed; check the pipe's log for which stage."),
    ],
    "limits": [
        ("Event size", "1 MB per PutEvents request entry (raised from 256 KB in early 2026); Scheduler target input stays 256 KB"),
        ("Classic bus targets", "5 targets per rule; 300 rules per bus in most Regions (adjustable)"),
        ("Classic PutEvents rate", "Varies by Region, for example 600 requests a second in Mumbai and 10,000 in N. Virginia (adjustable)"),
        ("New Custom Event Bus", "Retention 1 to 365 days; 5 buses per account by default; 500,000 events a second per bus"),
        ("Pipes", "1,000 pipes per account"),
        ("Scheduler", "10,000,000 schedules per Region; 1,000 invocations a second in main Regions (adjustable)"),
    ],
    "decisions": [
        ("Nightly start of an AppFlow flow for SAP master data", "EventBridge Scheduler calling AppFlow StartFlow", "Pursue: serverless, retries and a dead-letter queue, no cron server."),
        ("Payment provider and CRM webhooks into bronze", "API Gateway onto a custom bus, rule to Firehose, then S3 and Auto Loader", "Pursue: low volume, filters and an archive for replay."),
        ("2,000 presses sending 8,000 readings a second", "Custom Event Bus with one-year retention as the sensor log", "Drop: Kinesis stays the belt with native Databricks and Flink readers and per-key order at volume."),
        ("Start a Databricks job for every supplier file", "S3 event, EventBridge, Lambda, Jobs API run now", "Drop: one run per file is slow and costly and bypasses Auto Loader's bookkeeping."),
        ("Fast-lane alerts to ServiceNow and Teams", "EventBridge rule with API destinations, SNS for SMS and email", "Pursue: routing and retries without code."),
    ],
    "faq": [
        ("What is the difference between EventBridge and SNS?",
         "SNS fans a message out to subscribers, including SMS and email to people. EventBridge filters on event content, receives AWS service and SaaS events, schedules calls, and on the new bus retains and replays events."),
        ("What is the new EventBridge Custom Event Bus?",
         "Launched on 24 September 2026, it keeps events for 1 to 365 days, delivers in order within an event group, removes duplicates, and lets each team attach subscribers that can start from the past. The older bus is now called Custom Event Bus - Classic."),
        ("Can EventBridge replace Kinesis for streaming?",
         "Not on this platform. Kinesis gives per-key order at thousands of records a second and native readers in Databricks and Flink. EventBridge suits routing events and triggers."),
        ("What is the maximum EventBridge event size?",
         "PutEvents entries can be up to 1 MB since early 2026, up from 256 KB; some older pages still say 256 KB. Scheduler target input is still limited to 256 KB."),
        ("Should EventBridge orchestrate Databricks jobs?",
         "Only to start them from an AWS-side event. Lakeflow Jobs should run everything inside Databricks, including retries and dependencies."),
    ],
    "sources": [
        ("AWS docs: What is Amazon EventBridge", "https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-what-is.html"),
        ("AWS docs: What is the EventBridge Custom Event Bus", "https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-custom-bus-what-is.html"),
        ("AWS What's New: EventBridge relaunches custom event buses", "https://aws.amazon.com/about-aws/whats-new/2026/09/eventbridge-relaunches-custom-event-buses/"),
        ("AWS docs: EventBridge quotas", "https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-quota.html"),
        ("AWS docs: EventBridge Scheduler quotas", "https://docs.aws.amazon.com/scheduler/latest/UserGuide/scheduler-quotas.html"),
        ("AWS API reference: PutEvents", "https://docs.aws.amazon.com/eventbridge/latest/APIReference/API_PutEvents.html"),
    ],
    "related": [
        ("Streaming on AWS and Databricks", "/learn/streaming/"),
        ("AWS plus Databricks reference platform", "/learn/data-platform-architecture/aws-databricks/"),
        ("Ingestion framework", "/learn/data-platform-architecture/ingestion/"),
        ("Amazon SNS", "svc:sns"),
        ("AWS Step Functions", "svc:step-functions"),
        ("Amazon Kinesis Data Streams", "svc:kinesis-data-streams"),
    ],
}
