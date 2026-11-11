SERVICE = {
    "slug": "glue-schema-registry",
    "name": "AWS Glue Schema Registry",
    "short": "Glue Schema Registry",
    "group": "streaming",
    "one_line": "A free, serverless store of versioned Avro, JSON Schema and Protobuf schemas that checks every change against a compatibility rule.",
    "status": "Generally available and free to use. Not available in the Glue console in Middle East (UAE).",
    "checked": "2026-11-11",
    "site_verdict": ("Pursue",
                     "Holds the contract for each stream: Avro, backward-compatible changes only, with the reading id, press id as "
                     "key, event time and schema version in every record. It is free, works with Kinesis, MSK, Flink and Lambda, "
                     "and the new Kinesis streaming tables require it. Use Confluent Schema Registry only if you run MSK with "
                     "Confluent tools."),
    "equivalents": {"azure": "Azure Schema Registry in Event Hubs",
                    "gcp": "Pub/Sub schemas, or the schema registry in Managed Service for Apache Kafka",
                    "databricks": "none for streams; Unity Catalog governs tables, and from_avro reads Confluent Schema Registry natively",
                    "open_source": "Confluent Schema Registry (community licence), Apicurio Registry or Karapace"},
    "plain": [
        "A schema is a written description of what a record looks like: which fields it has, what type each field is, and which "
        "ones may be empty. In a stream, the producer and the consumer are usually different teams and different programs, often "
        "written months apart. If the producer quietly renames a field or changes a number into text, every consumer breaks, and "
        "usually at night. A schema registry is the shared place where the agreed schema lives, with every version kept.",
        "AWS Glue Schema Registry is that place on AWS. It stores schemas in three formats: Apache Avro, JSON Schema and Protocol "
        "Buffers (Protobuf). Each schema has a compatibility rule. When a producer tries to register a new version, the registry "
        "checks it against the rule and refuses changes that would break readers. It is serverless, you pay nothing for it, and "
        "AWS supplies open-source serializer and deserializer libraries (often shortened to serde) for Kafka clients, Kinesis "
        "clients, Flink and Lambda.",
        "A concrete example: the plant gateway sends curing press readings to Kinesis as Avro records. The schema says each record "
        "has reading_id, press_id, event_time, gateway_time, schema_version and a list of signal values. Six months later the "
        "plant adds a humidity sensor. The team adds an optional humidity field with a default, registers version 2, and the "
        "registry accepts it because old readers can still read new records and new readers can read old ones. If someone had "
        "tried to delete press_id, the registry would have refused the new version before a single bad record reached the stream.",
        "The serializer does one more useful thing: it puts a small header in front of each record that names the exact schema "
        "version used. The consumer reads the header, fetches that version from the registry once, caches it, and decodes the "
        "record. Records therefore stay small, because the schema is not repeated in every message.",
    ],
    "analogy": "A shared form template kept at the front office: anyone may print a newer version, but the clerk refuses any version that would make old filled-in forms unreadable.",
    "big_picture": [
        "On the reference platform the registry sits beside the stream belt rather than in the data path. The plant gateway "
        "registers or looks up the schema and writes Avro records to Kinesis Data Streams. Managed Flink in the fast lane and the "
        "Databricks streaming table in the platform lane both decode the same records using the same schema version. The site's "
        "streaming design lists this as the contract step: one contract per stream, Avro in a schema registry, key is press_id, "
        "every record carries reading_id and event time, and the stream keeps seven days.",
        "The registry is half of the contract. The other half is a data contract written in the open ODCS standard and kept in the "
        "catalog, which says what each field means, who owns it, and what quality checks apply. The registry enforces structure at "
        "write time; the contract and Delta schema enforcement protect the tables later. The reference platform's verdict table "
        "lists Glue Schema Registry for streams as the AWS piece of this concern, with the contract checks in CI and at run time "
        "built by the platform team.",
        "Two newer AWS features make the registry more central. Kinesis Data Streams streaming tables, launched in August 2026, "
        "deliver a stream straight into Apache Iceberg tables on S3 Tables, and they require the stream's schema to be in Glue "
        "Schema Registry in the same account. MSK data delivery channels to S3 Tables accept JSON with a Glue schema as one of "
        "their input formats. The site's Databricks platform does not use either today, but an AWS-only lane would.",
    ],
    "upstream": ["Plant gateways and app producers", "svc:iot-greengrass", "CI pipeline that registers schemas"],
    "downstream": ["svc:kinesis-data-streams", "svc:msk", "svc:managed-flink"],
    "concepts": [
        ("Registry", "A named container of schemas with its own ARN, used to group schemas and control access, for example one registry per domain."),
        ("Schema", "A named, versioned description of one record type, in Avro, JSON Schema or Protobuf."),
        ("Schema version", "One revision of a schema. Each version gets a unique id that producers put in the record header."),
        ("Compatibility mode", "The rule a new version must pass. There are eight: NONE, DISABLED, BACKWARD, BACKWARD_ALL, FORWARD, FORWARD_ALL, FULL and FULL_ALL."),
        ("Backward compatible", "Consumers using the new schema can still read records written with the previous one; adding an optional field or removing a field passes."),
        ("Checkpoint version", "The version that new versions are compared against; by default the first, and movable as the schema evolves."),
        ("Serde library", "The serializer and deserializer code AWS publishes, which writes and reads the schema-version header and caches schemas."),
        ("Auto-registration", "A producer setting that registers a new version automatically on first use; convenient in development, risky in production."),
    ],
    "use_when": [
        "Several programs read the same stream and you want a schema change to fail at the producer, not in every consumer.",
        "Your streams are on Kinesis Data Streams or Amazon MSK and you want a registry with no servers and no bill.",
        "You plan to use Kinesis streaming tables or MSK data delivery into S3 Tables, which rely on Glue Schema Registry.",
        "You want IAM to control who may register new versions, instead of a separate registry login.",
        "You send binary formats such as Avro or Protobuf and want small records with the schema kept elsewhere.",
    ],
    "avoid_when": [
        "Your Kafka estate already runs Confluent Schema Registry with Confluent connectors and tools; mixing two registries causes confusion.",
        "Producers outside AWS, such as a partner's Kafka, cannot use the AWS serde libraries or IAM credentials.",
        "The data is files that land in S3 and are read by Auto Loader; Delta schema enforcement and the data contract already cover them.",
        "You need a registry that works the same on every cloud; an open-source registry or Confluent Cloud is more portable.",
    ],
    "challenges": [
        ("Auto-registration lets anything through",
         "A producer with auto-registration on and mode NONE registers whatever it sends, so a broken change becomes version 7 and consumers fail.",
         "Turn auto-registration off in production, set BACKWARD or stricter on every schema, and register versions from CI after review."),
        ("Databricks cannot read the header directly",
         "Spark's from_avro understands Confluent's wire format, not the Glue header, so records decode as garbage or fail.",
         "Strip the Glue header and decode with the schema fetched from the registry, or use the AWS serde library in a UDF; test on your runtime first."),
        ("Schema id lookups throttled",
         "Many consumers starting at once each call GetSchemaVersion and hit API limits, slowing start-up.",
         "Keep the serde cache on, size its time-to-live sensibly, and avoid creating a new deserializer per record."),
        ("Hitting the version ceiling",
         "Auto-registration in test environments creates thousands of versions and reaches the 10,000 schema-version limit per Region.",
         "Use separate registries per environment, delete test schemas, and keep auto-registration off even in shared test accounts."),
        ("Breaking change that is truly needed",
         "Sometimes a field must change meaning or type, which backward compatibility rightly refuses.",
         "Create a new schema and a new stream or topic version, run both for a period, and retire the old one with the consumers."),
        ("Contract drifts from registry",
         "The ODCS contract in the catalog says one thing and the registered Avro says another, so documentation lies.",
         "Generate the Avro schema from the contract, or check in CI that both match before registering."),
    ],
    "compare": [
        ("Confluent Schema Registry", "You run MSK or Confluent Cloud with Confluent connectors, or want Databricks from_avro with its native registry option.", "You want no server to run and IAM for access; Glue is free and AWS-native."),
        ("Amazon EventBridge schema registry", "You want schemas discovered from events on an EventBridge bus and code bindings for applications.", "You need compatibility checks for streams; that registry documents events, it does not enforce evolution rules on Kinesis or Kafka."),
        ("Azure Schema Registry in Event Hubs", "The platform is on Azure and the stream is Event Hubs.", "You are on AWS."),
        ("Apicurio Registry or Karapace", "You want an open-source registry that runs on any cloud and speaks Confluent's API.", "You do not want to run and back up another stateful service."),
        ("No registry, JSON with a written contract", "One producer, one consumer, low volume, and a test suite that checks fields.", "Several teams read the stream; silent breaking changes become likely."),
    ],
    "cost": {
        "model": ("The registry itself is free: there is no charge for registries, schemas, versions or API calls. What you pay for "
                  "is the services around it, such as Kinesis or MSK carrying the records, and any Lambda or Flink code that "
                  "decodes them. The real cost is people: the time to agree schemas, review changes and fix consumers when a "
                  "change was not caught."),
        "drivers": [
            "Smaller records: binary Avro or Protobuf with a header is often several times smaller than JSON, which lowers Kinesis, Firehose and storage bills.",
            "Optional ZLIB compression in the serde library reduces records further at some CPU cost.",
            "Engineering time to build the CI check that registers versions and compares them with the data contract.",
        ],
        "traps": [
            "Moving to Confluent Schema Registry later for one feature adds a licence or a server you then have to run.",
            "Choosing JSON to avoid a registry saves a day now and pays in broken consumers and larger records later.",
            "Hitting the hard version limit forces a clean-up project at the worst moment.",
        ],
    },
    "security": [
        "Access is through IAM: give producers permission to read schemas and, only in CI, to register versions; consumers need read only.",
        "Scope policies to a registry ARN so one domain's team cannot change another domain's schemas.",
        "Calls such as CreateSchema, RegisterSchemaVersion and UpdateSchema are logged in CloudTrail, which shows who changed a contract and when.",
        "Reach the Glue API from private subnets through the Glue VPC endpoint, so producers and Databricks need no internet path.",
        "Schemas reveal field names; avoid putting personal data or secrets in schema metadata, and mark personal fields in the data contract instead.",
    ],
    "monitor": [
        ("RegisterSchemaVersion in CloudTrail", "Every new version; alert when it happens outside the CI role."),
        ("Schema version status FAILURE", "A version that failed its compatibility check; shows a producer tried a breaking change."),
        ("ThrottlingException on GetSchemaVersion", "Consumers are not caching schemas or too many start at once."),
        ("Deserialization errors in consumers", "Records that cannot be decoded; log them to a side output in S3 and count them in CloudWatch."),
        ("Records in the streaming table dead-letter bucket", "For Kinesis streaming tables, records that did not match the schema land in the required S3 dead-letter location."),
    ],
    "limits": [
        ("Registries", "100 per Region per account (hard limit)"),
        ("Schema versions", "10,000 per Region per account, across all schemas (hard limit)"),
        ("Schema payload", "170 KB maximum per schema definition"),
        ("Version metadata", "10 key-value pairs per schema version"),
        ("Formats", "Avro 1.11.4, JSON Schema drafts 04, 06 and 07, Protobuf proto2 and proto3 without extensions or groups"),
    ],
    "decisions": [
        ("Press readings on Kinesis, read by Flink and Databricks", "Avro in Glue Schema Registry, BACKWARD mode, versions registered from CI", "Pursue: free, enforced at the producer, and both readers share one definition."),
        ("Partner's Confluent Kafka topic", "Use the partner's Confluent Schema Registry as it is", "Pursue with care: do not copy their schemas into Glue; read with their registry and record the contract in the catalog."),
        ("Supplier CSV files over SFTP", "No stream registry; data contract and Delta schema enforcement", "Drop: a stream registry adds nothing to files read by Auto Loader."),
        ("AWS-only lane with Kinesis streaming tables into S3 Tables", "Glue Schema Registry in the same account and Region as the stream", "Pursue: the feature requires it, and schema changes need the delivery to be recreated."),
    ],
    "faq": [
        ("Is AWS Glue Schema Registry free?",
         "Yes. AWS states that the Schema Registry is serverless and free to use. You pay only for the streaming services and compute around it."),
        ("Which formats does Glue Schema Registry support?",
         "Apache Avro, JSON Schema (drafts 04, 06 and 07) and Protocol Buffers proto2 and proto3. Avro is the usual choice for sensor and event streams."),
        ("Which compatibility mode should I choose?",
         "BACKWARD for most streams: consumers on the new schema can still read older records, so you upgrade consumers first. Use FULL when producers and consumers upgrade in any order."),
        ("Can Databricks read Avro written with Glue Schema Registry?",
         "Yes, but not with the Confluent option of from_avro. Remove the Glue header and decode with the registered schema, or use the AWS serde library; test it on your runtime."),
        ("Glue Schema Registry or Confluent Schema Registry?",
         "Glue when you are on Kinesis or MSK and want IAM and no server. Confluent when you already run Confluent tools or connectors that expect its API."),
    ],
    "sources": [
        ("AWS docs: AWS Glue Schema Registry", "https://docs.aws.amazon.com/glue/latest/dg/schema-registry.html"),
        ("AWS docs: How the schema registry works", "https://docs.aws.amazon.com/glue/latest/dg/schema-registry-works.html"),
        ("AWS docs: Kinesis delivery quotas and limits", "https://docs.aws.amazon.com/streams/latest/dev/data-delivery-quotas.html"),
        ("AWS What's New: Kinesis Data Streams streaming tables", "https://aws.amazon.com/about-aws/whats-new/2026/08/kinesis/data-delivery-s3-tables"),
    ],
    "related": [
        ("Streaming on AWS and Databricks", "/learn/streaming/"),
        ("AWS plus Databricks reference platform", "/learn/data-platform-architecture/aws-databricks/"),
        ("Ingestion framework", "/learn/data-platform-architecture/ingestion/"),
        ("Amazon Kinesis Data Streams", "svc:kinesis-data-streams"),
        ("Amazon MSK", "svc:msk"),
    ],
}
