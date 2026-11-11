# Writer brief: AWS data services pages

You write content files for **cleandataengineering.ai/learn/aws-data-services/<slug>/**.
Each file is `_guides/aws_services/<slug>.py` and holds one Python dict, `SERVICE`.
`_guides/aws_services.py` turns it into the page. Never edit that generator. Only write your own files.

Check your files with:

    cd ~/cleandataengineering-site && python3 _guides/aws_services.py --check <slug> [<slug> ...]

Every one of your files must print `ok`. Do NOT run `--publish`, and do not run nav.py or seo.py. Do NOT git commit.

## Who reads it and how it should feel

- **Readers:** data engineers, learners and technology leaders. A leader should get the point from the verdict box and the first section. An engineer should get production depth from the tables.
- **Length:** each page is about a 10-minute read. The prose in the dict must be **1,600–2,700 words**; the check counts them.
- **Words:** plain, full sentences, the way a knowledgeable colleague talks. Define every term the first time it appears. No arrow chains, no "→" or "->" (the check rejects them), no cryptic lists of numbers, no emoji, no marketing tone.
- **Teach before deciding:** `plain` explains the service from zero. Use a concrete example from a manufacturing or retail data platform, such as sensor readings from plants, orders, customers or SAP data.
- **Never** mention Octave, JKH, DataAgents, Apollo or any client name. Don't name real customers.
- **Be honest about status.** If a service is retired, closed to new customers, renamed or in preview, say so in `status` and in the text. The check date is 2026-11-11. Your training data may be stale, so verify current status, renames and quotas with WebSearch or WebFetch against **docs.aws.amazon.com** or **aws.amazon.com** before writing, and put the URLs you used in `sources`. Examples of things that change: Amazon Data Firehose (renamed from Kinesis Data Firehose), QuickSight now part of Amazon Quick Suite, Timestream for LiveAnalytics closed to new customers, IoT Analytics and IoT Events end of support.
- **Prices:** describe the pricing *model* and what drives it. If you give a number, add "list price, check your region". Don't invent numbers.

## The reference platform (for `big_picture` and `site_verdict`)

The site's reference design is a data platform on AWS with **Databricks** doing processing, governance (Unity Catalog) and orchestration (Lakeflow Jobs). It uses S3 for storage, Delta tables (readable as Iceberg through UniForm) and a medallion layout (landing, bronze, silver, gold).

- **Movers:**
  - DMS for databases (full load plus ongoing CDC into S3 landing)
  - AppFlow for SaaS and SAP OData
  - Transfer Family for supplier SFTP
  - IoT Core and SiteWise Edge on Greengrass for plants
  - Kinesis Data Streams as the stream "belt", and Firehose for buffered files
- **Fast lane for seconds-level alerts:** Managed Flink plus DynamoDB, pushed to screens with API Gateway WebSocket or AppSync.
- **Serving and observability:**
  - Redshift stays for existing BI and reads tables through UniForm or Delta Sharing.
  - Athena is for ad hoc queries.
  - CloudWatch, CloudTrail and CUR feed health, audit and cost views.
- **Security:**
  - No public IPs.
  - PrivateLink to Databricks.
  - VPC endpoints for S3, STS and Kinesis.
  - One KMS key and one bucket per catalog.
  - Secrets Manager.
  - Macie scans landing buckets.

Read these before writing, to match the site's verdicts and wording. Search for your service's name in them:

- `_guides/dp_aws_databricks.py`: the reference platform, with verdicts per concern.
- `_guides/streaming_body.html`, `_guides/streaming_options.py` and `_guides/rtm.py`: streaming.
- `_guides/realtime.py` (PHYSICAL), `_guides/table_maintenance.py` and `_guides/medallion.py`.

`site_verdict` is one of **Pursue**, **Pursue with care**, **Keep if you have it** or **Drop**, followed by a reason. The verdict is for *this* platform, AWS plus Databricks. Where the site already gives a verdict, for example "Glue Workflows: Drop" or "IoT Analytics: Drop", keep it.

## Schema (every key is required)

```python
SERVICE = {
    "slug": "kinesis-data-streams",           # same as the file name
    "name": "Amazon Kinesis Data Streams",    # official name
    "short": "Kinesis Data Streams",          # used in pictures and lists
    "group": "streaming",                     # one of: ingestion streaming storage processing serving operational bi ml
                                              #         catalog orchestration security observability devops
    "one_line": "A managed, ordered log of events that many readers can replay for up to a year.",  # catalog row, 25 words max
    "status": "Generally available",          # or e.g. "Closed to new customers since 20 Jun 2025; existing users continue"
    "checked": "2026-11-11",
    "site_verdict": ("Pursue", "The stream belt for plant and app events; Databricks reads it directly ..."),
    "equivalents": {"azure": "Event Hubs", "gcp": "Pub/Sub", "databricks": "none: Databricks reads Kinesis",
                    "open_source": "Apache Kafka"},
    "plain": ["paragraph", "paragraph"],      # 2-4 paragraphs, from zero, with one concrete example
    "analogy": "One sentence picture, e.g. a conveyor belt with numbered trays that keeps every tray for a week.",
    "big_picture": ["paragraph", "paragraph"],  # 2-4: which lane and hop, what feeds it, what reads it, why it is there
    "upstream": ["svc:iot-core", "Apps and services"],    # up to 3; "svc:<slug>" links another service page, else plain text
    "downstream": ["svc:managed-flink", "Databricks Structured Streaming", "svc:data-firehose"],
    "concepts": [("Shard", "A unit of capacity ..."), ...],          # 6-10 (term, plain meaning)
    "use_when": ["...", ...],                 # 4-6 full sentences
    "avoid_when": ["...", ...],               # 3-6 full sentences
    "challenges": [("Hot shard", "One busy key overloads one shard; writes are throttled and data lags.",
                    "Pick a partition key with many values; watch WriteProvisionedThroughputExceeded; use on-demand mode."), ...],  # 6-10
    "compare": [("Amazon MSK", "You already use Kafka tools ...", "You want no cluster ..."), ...],   # 4-7, include the Azure/GCP and Databricks-native options
    "cost": {"model": "paragraph on how it is billed",
             "drivers": ["...", ...],         # 3-5
             "traps": ["...", ...]},          # 3-5
    "security": ["...", ...],                 # 4-6: IAM, encryption, network, private access, audit, personal data
    "monitor": [("IteratorAgeMilliseconds", "How far behind readers are ..."), ...],   # 4-8 real metric or signal names
    "limits": [("Record size", "1 MB per record"), ...],    # 3-6, real documented quotas
    "decisions": [("Plant sensors at 2,000 readings a second", "Kinesis on-demand", "Pursue: ..."), ...],  # 3-6; verdict text starts with one of the four verdicts
    "faq": [("Question people search for?", "Direct answer in 2-4 sentences."), ...],   # 4-6
    "sources": [("AWS docs: What is Kinesis Data Streams", "https://docs.aws.amazon.com/..."), ...],   # 2-6 official https URLs you checked
    "related": [("Streaming on AWS and Databricks", "/learn/streaming/"), ("Amazon MSK", "svc:msk")],  # 3-6; site paths must exist
}
```

All rows are **tuples**, not lists. Use plain Python string literals, with `"..."` for text that contains apostrophes.

Site paths that exist and are useful in `related`:

- `/learn/streaming/` and `/learn/streaming/options/`
- `/learn/streaming/real-time-mode/`
- `/learn/data-platform-architecture/aws-databricks/`
- `/learn/data-platform-architecture/ingestion/`
- `/learn/table-maintenance/` and `/learn/delta-vs-iceberg/`
- `/learn/medallion-architecture/`
- `/learn/real-time-analytics/`
- `/learn/data-systems/platform/cost/calculator/`
- `/learn/scd2-auto-cdc-vs-pyspark/`
- `/platforms/aws/`
- `/learn/data-platform-architecture/metadata-store/`
- `/learn/power-bi-vs-databricks-ai-bi/`

Other services: `svc:<slug>`. The full slug list is in `_guides/aws_services/SLUGS.txt`.
