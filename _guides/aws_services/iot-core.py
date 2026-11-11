SERVICE = {
    "slug": "iot-core",
    "name": "AWS IoT Core",
    "short": "IoT Core",
    "group": "ingestion",
    "one_line": "A managed MQTT front door that gives every device its own identity, routes its messages with rules, and sends commands back.",
    "status": "Generally available. Note that two older neighbours, AWS IoT Events and AWS IoT Analytics, have reached end of support; IoT Core itself is unaffected.",
    "checked": "2026-11-11",
    "site_verdict": ("Pursue with care",
                     "Pursue for connected products such as tyre sensors on fleet vehicles, and for sending commands back to devices, "
                     "because it gives each device its own certificate and a two-way channel. Drop it for plant machine readings: there a "
                     "Greengrass gateway writes straight to Kinesis, which avoids per-message charges of roughly a thousand dollars a month."),
    "equivalents": {"azure": "Azure IoT Hub (or Event Grid MQTT broker)",
                    "gcp": "none since Google Cloud IoT Core was retired in 2023; use a partner MQTT broker into Pub/Sub",
                    "databricks": "none: Databricks reads what IoT Core rules land in Kinesis or S3",
                    "open_source": "EMQX, HiveMQ CE or Eclipse Mosquitto as the MQTT broker"},
    "plain": [
        "AWS IoT Core is a managed message broker for devices. A device is anything with a chip and a network connection: a sensor "
        "clipped inside a tyre, a temperature probe in a cold store, a smart shelf in a retail shop. Devices usually speak MQTT, a "
        "small publish and subscribe protocol designed for weak networks and low power. A device publishes a message to a topic, "
        "which is just a name such as fleet/truck-0412/tyres, and anything subscribed to that topic receives it. IoT Core runs that "
        "broker for you at very large scale, so you never install or patch a broker server.",
        "Its second job is identity. Every device gets its own X.509 certificate, a digital ID card that it presents when it "
        "connects. A policy attached to the certificate says which topics that device may publish and subscribe to. If one truck is "
        "stolen, you revoke one certificate and the rest of the fleet carries on. This is the main reason to use IoT Core rather than "
        "letting devices write directly to a cloud service with a shared key.",
        "Its third job is routing. The rules engine runs a small SQL statement over each incoming message and sends the result to "
        "other AWS services: Kinesis Data Streams, Amazon Data Firehose, S3, DynamoDB, Lambda and others. Finally, IoT Core can talk "
        "back to devices through device shadows (a stored copy of the state each device should have) and jobs (a way to send a task, "
        "such as a firmware update, to many devices).",
        "A concrete example: a tyre maker fits pressure and temperature sensors to tyres on customer fleet trucks. Each truck has a "
        "small telematics box that collects readings from its tyres, batches ten readings into one message, and publishes it every "
        "minute over a mobile network to IoT Core. A rule forwards every message to a Kinesis stream. From there a Flink job raises "
        "a low-pressure alert within seconds, and Databricks lands the same data in bronze tables every fifteen minutes.",
    ],
    "analogy": "A building reception desk that checks each visitor's own badge, writes down who said what, and passes each note to the right department.",
    "big_picture": [
        "On the reference platform IoT Core sits at the very left edge of the move-in lane, as the front door for devices that live "
        "outside the plant: connected tyres on fleet vehicles today, and any product that needs commands sent back to it later. It "
        "receives MQTT messages, checks each device's certificate and policy, and a rule forwards the messages to Kinesis Data "
        "Streams, the stream belt that both the live lane and the platform lane read.",
        "Plant machines take a different path on purpose. Curing presses and mixers talk to a plant gateway running SiteWise Edge on "
        "AWS IoT Greengrass, and the gateway writes straight to Kinesis with an IAM role. The site's streaming design estimates that "
        "sending every press reading through IoT Core would add about a thousand dollars a month in message and rule charges for no "
        "extra benefit, because identity per gateway is enough inside a plant. So IoT Core is in the design, but only where per-device "
        "identity and a channel back to the device are worth paying for.",
        "Downstream, nothing reads IoT Core directly. Managed Service for Apache Flink and Databricks Structured Streaming read the "
        "Kinesis stream; Firehose can turn the same stream into files in S3 for the slower path. CloudWatch collects IoT Core metrics "
        "and logs so the operations team can see connection drops and rule failures alongside the other movers.",
    ],
    "upstream": ["Connected tyres and fleet telematics", "Retail and field devices over MQTT", "svc:iot-greengrass"],
    "downstream": ["svc:kinesis-data-streams", "svc:data-firehose", "svc:lambda"],
    "concepts": [
        ("MQTT", "A lightweight publish and subscribe protocol for devices on slow or unreliable networks. IoT Core supports versions 3.1.1 and 5."),
        ("Topic", "A text name that messages are published to, such as fleet/truck-0412/tyres. Subscribers can use wildcards to receive many topics at once."),
        ("Thing", "The registry entry for one device: its name, type and attributes. A certificate and a policy are attached to it."),
        ("X.509 certificate", "The device's own digital identity, used in mutual TLS so both the device and IoT Core prove who they are."),
        ("IoT policy", "A JSON document, like an IAM policy, that says which client IDs and topics a certificate may connect, publish and subscribe to."),
        ("Rules engine", "SQL statements that select and reshape incoming messages and send them to AWS services through rule actions."),
        ("Basic Ingest", "A reserved topic prefix ($aws/rules/<rule>) that sends a message straight to a rule without the publish step, so no messaging charge applies."),
        ("Device shadow", "A JSON document that stores a device's reported state and the desired state you want it to reach, even while it is offline."),
        ("Jobs", "A way to send a task, such as a firmware or settings update, to a list or group of devices and track progress."),
        ("Fleet provisioning", "A way for devices to get their own certificate on first boot, using a shared claim certificate or a trusted factory process."),
    ],
    "use_when": [
        "You have many devices outside your own network, such as vehicles or shop equipment, and each needs its own identity that you can revoke alone.",
        "You need to send commands or settings back to devices, not only receive data from them.",
        "Your devices speak MQTT over mobile or patchy networks and need a broker that handles reconnects and persistent sessions.",
        "You want a simple rule to fan device messages out to Kinesis, S3 or DynamoDB without running any servers.",
        "You must prove to auditors which device sent which message, because each connection is tied to one certificate.",
    ],
    "avoid_when": [
        "The data comes from machines inside a plant that already have a gateway; let the gateway write directly to Kinesis and skip the per-message fees.",
        "You are moving files or database tables; use Transfer Family, DataSync or DMS instead of squeezing them into small messages.",
        "Every reading would be sent as its own message at high frequency; at that scale messaging and rule charges dominate unless you batch on the device.",
        "Your apps call over HTTPS with user logins; API Gateway with a Cognito or IAM authorizer fits that better than device certificates.",
    ],
    "challenges": [
        ("Per-message cost surprise",
         "Charges are per message in 5 KB steps, plus per rule triggered and per action. A fleet that sends one small reading per message costs far more than one that batches.",
         "Batch several readings into one message on the device, keep messages near 5 KB, emit only changes, and use Basic Ingest topics to skip the messaging charge."),
        ("Certificate sprawl and expiry",
         "Thousands of certificates are created, a few are leaked or near expiry, and nobody knows which device owns which.",
         "Use fleet provisioning with a template, tag things with owner and site, rotate certificates with jobs, and turn on Device Defender audit checks."),
        ("Over-broad IoT policies",
         "A policy allowing iot:* on all topics lets one stolen device read or spoof the whole fleet.",
         "Use policy variables so a device may only publish to topics containing its own thing name, and only connect with a client ID equal to that name."),
        ("Silent rule failures",
         "A rule action fails, for example Kinesis throttles, and messages are dropped without anyone noticing.",
         "Configure an error action on every rule that writes to S3 or SQS, and alarm on the RuleMessageThrottled and failure metrics."),
        ("Duplicate client IDs",
         "Two devices, or one device after a reboot, connect with the same client ID and keep kicking each other off.",
         "Make the client ID equal to the thing name, enforce it in the policy, and watch the disconnect reasons in AWS IoT logs."),
        ("Per-connection throttling",
         "A device publishes faster than 100 messages a second on one connection and the excess is discarded.",
         "Batch on the device; if you truly need more, spread load over more connections or route bulk data another way."),
        ("Ordering and duplicates",
         "MQTT QoS 1 means at least once, so the same reading can arrive twice, and readings from a reconnecting device can arrive late.",
         "Put a device timestamp and sequence number in every message and deduplicate in silver, not at the broker."),
        ("Offline devices and lost messages",
         "Persistent sessions keep queued messages only for a limited time, one hour by default, so long outages lose commands.",
         "Use device shadows for desired state instead of one-off messages, and raise the session expiry quota if your vehicles go dark for longer."),
    ],
    "compare": [
        ("Greengrass gateway writing straight to Kinesis",
         "The devices are plant machines behind one gateway, identity per gateway is enough, and you want the cheapest path.",
         "Each device must have its own identity, or you need to send commands to individual devices."),
        ("Amazon API Gateway into Kinesis or Firehose",
         "Senders are apps or partner systems calling HTTPS with user or API-key auth.",
         "Senders are small devices on MQTT that need persistent sessions and a channel back."),
        ("Self-run MQTT broker (EMQX, HiveMQ, Mosquitto) on EC2 or EKS",
         "You need broker features IoT Core lacks, or want to avoid per-message prices at very high volumes and can run it well.",
         "You do not want to own patching, scaling, certificates and high availability of a broker."),
        ("Azure IoT Hub",
         "The platform lives on Azure; IoT Hub has the same identity, twin and routing ideas.",
         "You are on AWS; the concepts map one to one, so stay with IoT Core."),
        ("Google Cloud: partner broker into Pub/Sub",
         "You are on Google Cloud, where the native IoT Core was retired in August 2023.",
         "You are on AWS, where a managed broker still exists."),
        ("Databricks Zerobus Ingest",
         "One app stream should land directly in one Delta table with no belt in between.",
         "Several readers need the same events, or devices need identity and commands; the site drops it for sensors."),
    ],
    "cost": {
        "model": "IoT Core charges on four meters. Connectivity is charged per million connected minutes, which is tiny per device. "
                 "Messaging is charged per million messages, metered in 5 KB steps, so a 12 KB message counts as three. Device shadow "
                 "and registry operations are charged per million operations in 1 KB steps. The rules engine is charged per rule "
                 "triggered and per action run, also in 5 KB steps. Messages sent to Basic Ingest topics carry no messaging charge. "
                 "The site's design uses about one dollar per million messages and a fraction of that per rule action, list price, "
                 "check your region.",
        "drivers": [
            "How many messages each device sends, which is set by reading frequency and how much you batch per message.",
            "Message size, because every 5 KB step is charged again.",
            "How many rules fire per message and how many actions each rule runs.",
            "Shadow updates, especially if devices report state every few seconds.",
        ],
        "traps": [
            "Sending one reading per message: the site estimates about nine thousand dollars a month for connected tyres unbatched, and about one thousand with ten readings per message.",
            "Routing plant machines through IoT Core when a gateway could write to Kinesis directly, adding about a thousand dollars a month for nothing.",
            "Several rules subscribed to the same topic, each charged separately for every message.",
            "Verbose logging at DEBUG level sent to CloudWatch Logs for the whole fleet, which can cost more than the messages.",
        ],
    },
    "security": [
        "Give every device its own X.509 certificate, keep private keys in a secure element or TPM where the hardware allows, and never share one certificate across a fleet.",
        "Write IoT policies with the thing name variable so each device can only connect as itself and only use its own topics.",
        "Rule actions use an IAM role; scope that role to the one Kinesis stream or bucket the rule writes to.",
        "Use VPC interface endpoints for IoT Core data so back-end services inside the VPC reach it without public routes; devices themselves connect over TLS on port 8883 or 443.",
        "Turn on AWS IoT Device Defender audit for weak policies and shared certificates, and CloudTrail for control-plane changes such as new policies.",
        "Vehicle location and driver data can be personal data; keep it out of topic names, and tokenise it in the lander before bronze.",
    ],
    "monitor": [
        ("Connect.Success and Connect.ClientError", "Whether devices are connecting, and how many are being refused because of bad certificates or policies."),
        ("PublishIn.Success", "How many messages arrive; a sudden drop for one customer or region means devices have gone quiet."),
        ("RuleMessageThrottled", "Messages the rules engine could not process because of the account rate limit."),
        ("Failure (per rule action)", "Rule actions that failed, for example because the Kinesis stream throttled the write."),
        ("TopicMatch", "How many rules matched incoming messages, useful to spot a rule that stopped matching after a topic change."),
        ("AWS IoT logs in CloudWatch Logs", "Per-event detail on disconnects, authorisation failures and rule errors; keep at ERROR or WARN for the fleet."),
    ],
    "limits": [
        ("MQTT message size", "128 KB per message, not adjustable"),
        ("Publish rate per connection", "100 messages per second, inbound and outbound together, not adjustable"),
        ("Inbound publish rate per account", "20,000 per second by default (2,000 in some Regions), adjustable"),
        ("Connect requests per client ID", "1 per second"),
        ("Actions per rule", "10, not adjustable"),
        ("Persistent session expiry", "1 hour by default, adjustable"),
    ],
    "decisions": [
        ("Connected tyre sensors on 20,000 fleet trucks", "IoT Core with one certificate per truck, ten readings per message, rule into Kinesis",
         "Pursue: per-device identity and commands back are worth it; batching keeps the bill near one thousand dollars a month instead of nine."),
        ("Curing presses and mixers in a plant", "Greengrass gateway with SiteWise Edge, writing straight to Kinesis",
         "Drop: IoT Core adds per-message charges and no benefit, because identity per gateway is enough inside the plant."),
        ("Pushing new alarm thresholds to tyre sensors", "Device shadows with desired state, or a job for a fleet-wide change",
         "Pursue with care: only when control is in scope, and test on a small thing group first."),
        ("A retail chain's shelf sensors in 300 shops", "IoT Core through a shop hub using Basic Ingest topics",
         "Pursue with care: worth it if shelves need commands; otherwise a shop gateway writing to Kinesis is cheaper."),
    ],
    "faq": [
        ("Is AWS IoT Core the same as AWS IoT Analytics or IoT Events?",
         "No. IoT Core is the broker and routing service and is fully supported. IoT Analytics and IoT Events were separate services that have reached end of support; the replacements are Kinesis, Flink and Databricks for analysis and alerts."),
        ("How much does AWS IoT Core cost per device?",
         "Connection time costs very little; the bill is driven by how many messages each device sends and how many rule actions each message triggers. Batch readings into one message near 5 KB and the per-device cost drops many times over."),
        ("Can Databricks read from AWS IoT Core directly?",
         "Not directly. A rule sends messages to Kinesis Data Streams or to S3 through Firehose, and Databricks reads from there with Structured Streaming or Auto Loader."),
        ("Do I need IoT Core if I use Greengrass?",
         "A Greengrass device uses IoT Core for its identity, deployments and optional MQTT messaging, but the data itself can go straight to Kinesis through stream manager. That direct path is what the reference platform uses for plant data."),
        ("What is the difference between IoT Core and Kinesis?",
         "IoT Core is the front door: it knows each device, speaks MQTT and can talk back. Kinesis is the belt behind it: an ordered, replayable log that many readers consume. Most device platforms use both."),
    ],
    "sources": [
        ("AWS docs: What is AWS IoT Core", "https://docs.aws.amazon.com/iot/latest/developerguide/what-is-aws-iot.html"),
        ("AWS docs: AWS IoT Core endpoints and quotas", "https://docs.aws.amazon.com/general/latest/gr/iot-core.html"),
        ("AWS IoT Core pricing", "https://aws.amazon.com/iot-core/pricing/"),
        ("AWS docs: Basic Ingest", "https://docs.aws.amazon.com/iot/latest/developerguide/iot-basic-ingest.html"),
        ("AWS docs: AWS IoT Events end of support", "https://docs.aws.amazon.com/iotevents/latest/developerguide/iotevents-end-of-support.html"),
    ],
    "related": [
        ("Streaming on AWS and Databricks", "/learn/streaming/"),
        ("Streaming options at a glance", "/learn/streaming/options/"),
        ("AWS IoT Greengrass", "svc:iot-greengrass"),
        ("Amazon Kinesis Data Streams", "svc:kinesis-data-streams"),
        ("AWS IoT Events and IoT Analytics", "svc:iot-events-analytics"),
        ("Data platform on AWS and Databricks", "/learn/data-platform-architecture/aws-databricks/"),
    ],
}
