SERVICE = {
    "slug": "msk",
    "name": "Amazon Managed Streaming for Apache Kafka (Amazon MSK): Provisioned, Serverless, Connect and Replicator",
    "short": "Amazon MSK",
    "group": "streaming",
    "one_line": "Apache Kafka run by AWS: brokers you size (Standard or Express), a serverless option, managed Kafka Connect and cross-cluster replication.",
    "status": ("Generally available. Provisioned clusters offer Standard brokers and Express brokers (since Nov 2024, storage "
               "without limit and faster scaling). New clusters use KRaft rather than ZooKeeper. Since July 2026 Express "
               "clusters can deliver topics straight into Iceberg tables on S3 Tables."),
    "checked": "2026-11-11",
    "site_verdict": ("Pursue with care",
                     "Pursue only if Kafka tools are needed: Debezium change capture on MSK Connect, partner Kafka topics, or a "
                     "company that already runs Kafka. Otherwise Kinesis is the cheaper belt with nothing to size. MSK Serverless is "
                     "a Drop at plant scale because of its monthly floor; MSK Replicator is the way to copy a partner's topics in."),
    "equivalents": {"azure": "Event Hubs (Kafka endpoint) or Confluent Cloud on Azure", "gcp": "Google Cloud Managed Service for Apache Kafka",
                    "databricks": "none: Databricks reads and writes Kafka directly", "open_source": "Apache Kafka, Redpanda"},
    "plain": [
        "Apache Kafka is the most widely used open-source event log. Producers write events into topics, a topic is split into "
        "partitions for parallel work, and the cluster keeps events for as long as you configure. Consumers read at their own "
        "pace and track their position with offsets, so many teams can read the same topic and replay it. Around Kafka sits a large "
        "set of tools: Kafka Connect to move data in and out, Debezium to turn database changes into events, schema registries, "
        "and stream processors such as Flink. Running Kafka yourself means looking after brokers, the servers that store the data, "
        "and that is hard work.",
        "Amazon MSK runs Kafka for you. In the provisioned option you choose the number and size of brokers and AWS installs, "
        "patches and replaces them across availability zones. Standard brokers keep data on disks you size; Express brokers, added "
        "in late 2024, keep data in storage AWS manages without a size limit, recover faster and scale more quickly. MSK Serverless "
        "goes further: you create topics and pay for use, with no brokers to see at all. MSK Connect runs Kafka Connect workers, "
        "and MSK Replicator copies topics between clusters, including across Regions.",
        "A concrete example: a manufacturer wants every change in its SAP order tables and its warehouse Postgres database to flow "
        "as events within seconds. Debezium runs on MSK Connect, reads the database logs and writes one topic per table into MSK. "
        "A logistics partner also publishes shipment events on its own Kafka cluster, and MSK Replicator copies those topics in. "
        "Databricks then reads all the topics with its Kafka source into bronze tables.",
    ],
    "analogy": "A shared warehouse of numbered shelves that AWS staffs and maintains for you, while you still decide how many aisles to build and pay for them.",
    "big_picture": [
        "On the reference platform MSK is the alternative belt in the move-in lane, not the default. The architecture page lists "
        "sensors arriving through SiteWise, Kinesis or MSK, and the streaming design picks Kinesis provisioned for the plant stream "
        "because it is serverless to run, native to IoT Core, Firehose, Flink, Lambda and Databricks, and costs about $120 a month "
        "against about $480 for three small MSK brokers. MSK becomes the right answer when the Kafka ecosystem itself is needed.",
        "Three cases bring it in. First, change capture from many databases with Debezium, where the site's real-time pattern is "
        "Debezium on MSK Connect, with Avro in the Glue Schema Registry. The default for the platform remains DMS writing files to "
        "S3. Second, a partner's Kafka or Confluent topic: Databricks reads it directly, or MSK Replicator copies it into an "
        "account the platform controls. Third, a company that already runs Kafka: do not add Kinesis as a second belt.",
        "When MSK is used, the readers are the same as for Kinesis. Managed Service for Apache Flink reads topics for the seconds "
        "lane, Databricks Structured Streaming and Lakeflow pipelines read them for bronze, and Firehose can read a topic to write "
        "files. Databricks real-time mode also supports Kafka both as a source and as a sink, which Kinesis does not offer as a sink.",
    ],
    "upstream": ["Debezium on MSK Connect", "svc:dms", "Partner Kafka through MSK Replicator"],
    "downstream": ["svc:managed-flink", "Databricks Structured Streaming", "svc:data-firehose"],
    "concepts": [
        ("Broker", "A Kafka server that stores partitions and serves producers and consumers. MSK spreads brokers across two or three availability zones."),
        ("Topic and partition", "A topic is a named stream; it is split into partitions, each an ordered log that one consumer in a group reads."),
        ("Offset and consumer group", "An offset is a record's position in a partition. A consumer group is a set of readers that share the partitions and store their offsets."),
        ("Standard and Express brokers", "Standard brokers keep data on EBS disks you size. Express brokers keep it in managed storage without a limit and scale faster, at a higher hourly price."),
        ("Tiered storage", "On Standard brokers, older log segments move to cheaper storage so topics can keep months of data."),
        ("MSK Serverless", "Kafka with no brokers to size; you pay per cluster-hour, per partition-hour and per GB."),
        ("MSK Connect", "Managed Kafka Connect workers that run connectors such as Debezium sources or S3 sinks."),
        ("MSK Replicator", "A managed copier that keeps topics and consumer offsets in step between two MSK clusters, in one Region or across Regions."),
        ("KRaft", "Kafka's own way of storing cluster metadata, replacing ZooKeeper; Kafka 4.0 dropped ZooKeeper entirely."),
    ],
    "use_when": [
        "Use it when you run Debezium or other Kafka Connect connectors to capture changes from many databases as events.",
        "Use it when partners, other clouds or existing apps already exchange data as Kafka topics.",
        "Use it when the company already operates Kafka and has the skills to tune partitions, retention and clients.",
        "Use it when you need very long retention on the log itself, using tiered storage or Express brokers.",
        "Use it when you want the same event log technology on AWS, Azure and Google Cloud.",
    ],
    "avoid_when": [
        "Avoid it when AWS-native producers write a few MB a second and nobody needs Kafka tools; Kinesis is cheaper and has nothing to size.",
        "Avoid MSK Serverless for small, steady streams; its charge per cluster-hour and per partition-hour makes a monthly floor of several hundred dollars before data.",
        "Avoid it when the data only needs to land as files within minutes; Firehose or DMS files into S3 do that with less to run.",
        "Avoid it as a place to keep years of history for analytics; keep that in bronze tables.",
    ],
    "challenges": [
        ("Disk full on Standard brokers", "A retention change or a burst fills the EBS volumes and brokers stop accepting writes.",
         "Alarm on KafkaDataLogsDiskUsed at 70 percent, turn on storage auto scaling or tiered storage, or use Express brokers."),
        ("Too many partitions", "Each broker size has a recommended partition count; above it, leader elections and restarts slow down and updates can be blocked.",
         "Plan partitions per topic from throughput, not habit; watch PartitionCount per broker against the documented limits."),
        ("Consumer lag", "A slow consumer group falls behind and, if retention is short, loses data before reading it.",
         "Watch MaxOffsetLag and SumOffsetLag per group; scale consumers up to the partition count; size retention for the longest outage."),
        ("Under-replicated partitions", "A broker under stress or being patched leaves partitions with fewer copies than required, risking data loss on a second failure.",
         "Use three zones and replication factor 3 with min.insync.replicas 2; alarm on UnderReplicatedPartitions above zero for more than a few minutes."),
        ("Cross-zone traffic cost", "Producers and consumers in other zones than the partition leader pay data transfer on every byte.",
         "Use rack awareness so consumers read from the closest replica; keep heavy readers in the same zones."),
        ("Connection storms with IAM auth", "Each broker accepts about 3,000 IAM connections and 100 new connections a second; many short-lived clients get refused.",
         "Reuse producer and consumer instances, set reconnect.backoff.ms, and watch ClientConnectionCount and ConnectionCreationRate."),
        ("Connector drift on MSK Connect", "A Debezium connector stops after a database failover or schema change and nobody notices for hours.",
         "Alarm on connector state and on topic volume per table; keep source database logs long enough to restart."),
        ("Version upgrades", "Kafka versions reach end of support and must be upgraded, which rolls every broker.",
         "Schedule upgrades in quiet hours, test clients first, and keep ZooKeeper clusters moving to KRaft."),
    ],
    "compare": [
        ("Kinesis Data Streams", "AWS-native producers, a few MB a second, and a team that does not want to size brokers.",
         "You need Kafka Connect, Debezium, Kafka clients or topics shared with partners."),
        ("Confluent Cloud", "You want Kafka plus Confluent's Flink, Tableflow and connectors on any cloud, with a vendor that runs everything.",
         "You want one AWS bill and AWS-only networking, or the extra licence cost is not justified."),
        ("Azure Event Hubs with its Kafka endpoint", "The platform runs on Azure and clients only need the Kafka protocol, not brokers.",
         "You need full Kafka features such as Kafka Streams or compacted topics everywhere, or you are on AWS."),
        ("Google Cloud Managed Service for Apache Kafka", "The platform runs on Google Cloud.",
         "You are on AWS."),
        ("Redpanda or Kafka you run on EKS", "You need lower latency, special tuning, or Kafka on object storage to cut cost at very high volume.",
         "You do not have a team to run and patch it."),
        ("Databricks Zerobus Ingest", "One app stream has exactly one reader, a Delta table.",
         "Several readers or a live lane need the same events."),
    ],
    "cost": {
        "model": ("Provisioned Standard brokers bill per broker-hour by instance size plus EBS storage per GB-month, and tiered "
                  "storage per GB-month. Express brokers bill per broker-hour plus per GB written and per GB-month stored. MSK "
                  "Serverless bills per cluster-hour, per partition-hour, and per GB in and out, with storage per GB-month. MSK "
                  "Connect bills per worker-hour (MSK Connect units). MSK Replicator bills per hour plus per GB replicated, and "
                  "cross-Region copies add data transfer. The site's figures are about $480 a month for three m7g.large brokers with "
                  "storage, and about $700 for MSK Serverless at plant scale; list price, check your region."),
        "drivers": [
            "Broker size and count, which must cover peak throughput, partitions and three zones.",
            "Storage retained on brokers, or data written and stored on Express brokers.",
            "Cross-zone and cross-Region data transfer between clients, brokers and replicas.",
            "Partition-hours on MSK Serverless, which grow with every topic you create.",
            "MSK Connect workers left running for connectors that are idle most of the day.",
        ],
        "traps": [
            "Choosing MSK Serverless for a small stream: the cluster-hour and partition-hour charges make a floor of about $550 a month before any data, by the site's estimate.",
            "Sizing brokers for a peak that happens once a month; Express brokers scale faster, so start smaller.",
            "Ignoring consumers in other zones, which pay data transfer on every byte they read.",
            "Copying whole partner clusters with Replicator when only two topics are needed.",
        ],
    },
    "security": [
        "Use IAM access control so producers and consumers authenticate with roles and policies per topic and group; the alternative is TLS certificates or SASL/SCRAM with secrets in Secrets Manager.",
        "Keep encryption in transit on between clients and brokers and between brokers; encrypt storage with the platform's KMS key.",
        "Place brokers in private subnets with no public access; Databricks reaches them through VPC peering, Transit Gateway or multi-VPC private connectivity, never over the internet.",
        "Restrict security groups to the client subnets and the Databricks compute subnets only.",
        "CloudTrail logs cluster changes; turn on broker logs to CloudWatch Logs or S3 for client and authorization errors.",
        "Debezium topics carry full rows from source databases, often including personal data; limit who can read those topics and mask fields in silver.",
    ],
    "monitor": [
        ("MaxOffsetLag and SumOffsetLag", "How far each consumer group is behind, per topic; the main health signal for readers."),
        ("KafkaDataLogsDiskUsed", "Percent of broker disk used on Standard brokers; act long before it reaches 85 percent."),
        ("UnderReplicatedPartitions", "Partitions missing replicas; should be zero in normal running."),
        ("CpuUser plus CpuSystem", "Broker CPU; keep it under about 60 percent so a broker can absorb a neighbour's load during patching."),
        ("BytesInPerSec and BytesOutPerSec", "Throughput per broker or topic, against the broker size and Express throttle limits."),
        ("ClientConnectionCount", "IAM connections per broker, against the 3,000 limit."),
    ],
    "limits": [
        ("Brokers", "90 per account and 60 per KRaft cluster (30 for ZooKeeper clusters) by default"),
        ("Storage per Standard broker", "1 GiB to 16,384 GiB; Express brokers have no storage limit"),
        ("Express partition throughput", "Up to 15 MB a second per partition; broker limits by size, for example 23.4 MB a second in for express.m7g.large"),
        ("MSK Serverless", "200 MB a second in, 400 MB a second out, 2,400 partitions and 8 MiB messages per cluster"),
        ("IAM connections", "3,000 per broker, 100 new connections a second"),
        ("MSK Connect", "Up to 10 workers per connector and 60 workers per account by default"),
    ],
    "decisions": [
        ("Plant sensors, 8,000 readings a second, AWS gateways", "MSK provisioned instead of Kinesis",
         "Drop: about four times the cost of Kinesis for no tool the plant stream needs."),
        ("Change events from 20 databases within seconds", "Debezium on MSK Connect into MSK, Avro in Glue Schema Registry",
         "Pursue with care: right when several live readers need the changes; otherwise DMS files into S3 stay the default."),
        ("Partner publishes shipments on their Kafka", "Databricks reads their cluster directly, or MSK Replicator copies the topics in",
         "Pursue: read directly when allowed; replicate when we need our own copy and retention."),
        ("Small stream, want Kafka with nothing to manage", "MSK Serverless",
         "Drop: the monthly floor is higher than the whole Kinesis lane at this scale."),
        ("Company already runs MSK for applications", "Use the existing cluster as the belt",
         "Keep if you have it: one belt is better than two."),
    ],
    "faq": [
        ("What is the difference between MSK provisioned and MSK Serverless?",
         "Provisioned means you choose broker count and size and pay per broker-hour. Serverless hides brokers and bills per cluster-hour, "
         "partition-hour and GB, with fixed per-cluster limits such as 200 MB a second in. Serverless is simpler but has a monthly floor "
         "that makes it expensive for small streams."),
        ("What are MSK Express brokers?",
         "A broker type launched in November 2024 that keeps data in AWS-managed storage with no size limit, recovers and scales faster, "
         "and supports higher throughput per broker than Standard brokers. Since July 2026 they can also deliver topics straight into "
         "Iceberg tables on S3 Tables."),
        ("Can Databricks read from Amazon MSK?",
         "Yes. Structured Streaming and Lakeflow pipelines read Kafka topics with IAM or TLS authentication over private networking. "
         "Kafka is also supported as a source and a sink for Databricks real-time mode."),
        ("MSK or Kinesis for a data platform?",
         "Kinesis when producers are AWS-native and you want nothing to size. MSK when you need Kafka Connect, Debezium, Kafka clients, "
         "partner topics or the same tool on several clouds."),
        ("Does MSK still need ZooKeeper?",
         "No for new clusters, which can use KRaft mode. Kafka 4.0 removed ZooKeeper completely, so older ZooKeeper clusters should plan "
         "a move to KRaft."),
    ],
    "sources": [
        ("AWS docs: Amazon MSK quotas", "https://docs.aws.amazon.com/msk/latest/developerguide/limits.html"),
        ("AWS docs: MSK data delivery to Iceberg", "https://docs.aws.amazon.com/msk/latest/developerguide/msk-data-delivery-iceberg.html"),
        ("AWS What's New: Express brokers deliver to streaming tables (Jul 2026)", "https://aws.amazon.com/about-aws/whats-new/2026/07/aws-msk-streaming-tables-for-apache-iceberg"),
        ("AWS: Amazon MSK pricing", "https://aws.amazon.com/msk/pricing/"),
        ("AWS docs: What is Amazon MSK", "https://docs.aws.amazon.com/msk/latest/developerguide/what-is-msk.html"),
    ],
    "related": [
        ("Streaming on AWS and Databricks", "/learn/streaming/"),
        ("Every streaming option compared", "/learn/streaming/options/"),
        ("Real-time analytics", "/learn/real-time-analytics/"),
        ("Amazon Kinesis Data Streams", "svc:kinesis-data-streams"),
        ("AWS Glue Schema Registry", "svc:glue-schema-registry"),
        ("AWS DMS", "svc:dms"),
    ],
}
