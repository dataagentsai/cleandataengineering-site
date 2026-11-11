SERVICE = {
    "slug": "opensearch",
    "name": "Amazon OpenSearch Service (and Serverless)",
    "short": "OpenSearch",
    "group": "operational",
    "one_line": "Managed OpenSearch for full-text search, log analytics and vector search, as domains or Serverless; not on this platform's main path.",
    "status": "Generally available. The next generation of OpenSearch Serverless (GA May 2026) separates compute from storage and can scale to zero after 10 idle minutes; collection groups (Feb 2026) share capacity across collections.",
    "checked": "2026-11-11",
    "site_verdict": ("Keep if you have it",
                     "The reference platform does not need it: Databricks Vector Search serves retrieval for AI, CloudWatch holds operational logs, and "
                     "Delta tables answer analytics. Keep an existing OpenSearch estate for what it does well, full-text search in an application and "
                     "log search, and feed it from gold tables; do not add it as a second analytics store."),
    "equivalents": {"azure": "Azure AI Search, or Elastic on Azure",
                    "gcp": "Vertex AI Search, or Elastic Cloud on Google Cloud",
                    "databricks": "Databricks Vector Search for embeddings; SQL warehouse for analytics",
                    "open_source": "OpenSearch, Elasticsearch, Apache Solr"},
    "plain": [
        "Amazon OpenSearch Service runs OpenSearch, the open-source search and analytics engine that began as a fork of Elasticsearch. You send it "
        "JSON documents, it builds an inverted index, which is a list of every word pointing to the documents that contain it, and then it can "
        "answer text searches in milliseconds, rank results by relevance, handle typos and synonyms, and count results by category. It also "
        "stores vectors, the lists of numbers that AI models produce to represent meaning, and finds the nearest ones, which is the core of "
        "semantic search.",
        "It comes in two shapes. A managed domain is a cluster of nodes you size: data nodes hold shards of each index, dedicated manager nodes "
        "keep the cluster in order, and warm and cold tiers hold older data more cheaply. OpenSearch Serverless has no nodes to choose. You create "
        "collections for search, vector search or time series, and AWS adds and removes OpenSearch Compute Units (OCUs) as load changes. The next "
        "generation of Serverless, generally available since May 2026, keeps data in a shared storage layer and can scale compute to zero "
        "after ten idle minutes, waking in about ten seconds.",
        "A retail example: an online store with 200,000 products needs a search box that understands \"waterproof hiking boots size 9\", "
        "forgives a typo, and shows filters for brand and price with counts. That is what OpenSearch is built for. The product data itself is "
        "mastered elsewhere; a job takes the gold product table from Databricks every hour and indexes it into OpenSearch for the website.",
    ],
    "analogy": "The index at the back of a very large book, kept up to date as pages change, that can also find pages that mean the same thing as your words.",
    "big_picture": [
        "OpenSearch is not on the reference platform's main path. Ingestion runs through DMS, AppFlow, Transfer Family and Kinesis into S3; "
        "Databricks builds bronze, silver and gold; serving uses the Databricks SQL warehouse, Athena for ad hoc queries and Redshift where it "
        "is kept for existing reports. Each common reason to add OpenSearch is already covered: retrieval for AI assistants uses Databricks "
        "Vector Search on governed tables, operational logs and metrics live in CloudWatch, and analytics runs on Delta tables.",
        "Where it does fit is at the edge, as a consumer of gold. An application team that needs full-text search for a product catalog, a "
        "spare-parts catalogue for maintenance engineers or a knowledge base of quality reports can index from gold tables on a schedule. The "
        "gold table stays the record; the index is a derived copy that can be rebuilt. If the company already runs OpenSearch for log analytics "
        "or security events, keep it for that and do not move platform analytics into it.",
        "The governance gap is the main reason for caution. OpenSearch indices are outside Unity Catalog, so masks, lineage and access reviews "
        "do not follow the data there. Anything indexed must be reviewed for personal data before it leaves the platform.",
    ],
    "upstream": ["Gold tables in Databricks (scheduled export)", "svc:data-firehose", "Application logs"],
    "downstream": ["Website or app search", "OpenSearch Dashboards", "svc:bedrock"],
    "concepts": [
        ("Index", "A named collection of documents with a mapping that says how each field is stored and searched, much like a table."),
        ("Shard and replica", "An index is split into shards spread across nodes; replicas are copies for availability and read throughput."),
        ("Domain", "A managed OpenSearch cluster you size, with data nodes, optional dedicated manager nodes and storage tiers."),
        ("Collection", "The OpenSearch Serverless unit: a group of indices of one type (search, vector search or time series) with capacity managed by AWS."),
        ("OCU", "OpenSearch Compute Unit, the Serverless measure of indexing and search capacity, billed per hour."),
        ("Mapping", "The schema of an index; a field mapped as text is analysed into words, a keyword field is matched exactly. Changing it usually needs a reindex."),
        ("k-NN vector search", "Finding the stored vectors nearest to a query vector, used for semantic search and retrieval for AI assistants."),
        ("UltraWarm and cold storage", "Cheaper tiers on domains that keep older, read-only indices on S3-backed storage with slower queries."),
    ],
    "use_when": [
        "An application needs full-text search with relevance ranking, typo tolerance, synonyms and facet counts, such as a product or parts catalog.",
        "You already run OpenSearch or Elasticsearch for log or security analytics and want AWS to manage it.",
        "You need hybrid search, combining keyword and vector similarity, inside an application outside Databricks.",
        "Search load is spiky or idle most of the time, and next-generation Serverless can scale to zero between uses.",
    ],
    "avoid_when": [
        "The question is analytics over tables, such as sales by store and month; use the Databricks SQL warehouse.",
        "You want retrieval for an AI assistant over governed platform data; Databricks Vector Search keeps it inside Unity Catalog.",
        "It would be the record for any data; indices should be rebuildable copies of gold.",
        "You need joins across entities; OpenSearch works on denormalised documents and has no real joins.",
        "The team has no one to tune shards, mappings and memory on a domain, and Serverless does not fit the workload.",
    ],
    "challenges": [
        ("Too many small shards", "Each index gets the default shard count, daily indices multiply them, and the cluster spends memory managing thousands of tiny shards.",
         "Aim for shards of roughly 10 to 50 GB, use index templates and rollover, and watch the per-node shard limit."),
        ("Mapping explosion", "Dynamic mapping turns every new JSON key into a field until the mapping hits its field limit and indexing fails.",
         "Define explicit mappings, set dynamic to strict or false for untrusted data, and flatten free-form attributes."),
        ("Heap pressure", "Large aggregations or many vectors fill the Java heap, garbage collection stalls and nodes drop out.",
         "Alarm on JVMMemoryPressure, size nodes for vectors, and limit aggregation sizes."),
        ("Write rejections at peak", "Bulk indexing faster than the cluster can absorb leads to rejected requests and missing documents.",
         "Batch bulk requests, retry with backoff, and alarm on rejected thread-pool counts. Index from gold on a schedule, not row by row."),
        ("Stale or drifting index", "The index drifts from gold because deletes were never propagated.",
         "Rebuild the index from gold into a new index and switch an alias, or propagate deletes from the change feed of the gold table."),
        ("Serverless minimum cost", "Classic Serverless collections keep a minimum of OCUs running all month, even for a small test.",
         "Use next-generation collections with minimum capacity set to zero, or group collections to share OCUs."),
        ("Data outside governance", "Personal data indexed for search escapes Unity Catalog masks and access reviews.",
         "Index only the fields search needs, mask or drop personal data in the export job, and use fine-grained access control."),
    ],
    "compare": [
        ("Databricks Vector Search", "You need retrieval for AI assistants over platform data, governed in Unity Catalog and synced from Delta tables.",
         "An external application needs full-text search with facets and typo tolerance."),
        ("Databricks SQL warehouse", "The question is analytics: totals, trends and joins over tables.", "You need relevance-ranked text search."),
        ("Amazon CloudWatch Logs", "You need operational logs and alarms for AWS services and jobs, with Logs Insights queries.",
         "You need long-term, heavily searched log analytics at large scale with custom dashboards."),
        ("Elastic Cloud", "You want Elasticsearch features and support from Elastic itself.", "You prefer an AWS-managed open-source engine."),
        ("Azure AI Search", "You are building application search on Azure.", "You are on AWS."),
        ("Amazon S3 Vectors or Bedrock Knowledge Bases", "You want cheap vector storage or managed retrieval for a Bedrock application.",
         "You need full-text relevance and facets."),
    ],
    "cost": {
        "model": "Managed domains bill per instance-hour for every data, manager and warm node, plus EBS storage per GB-month, UltraWarm and cold "
                 "storage, snapshots beyond the free automated ones, and data transfer. Reserved instances lower the rate. OpenSearch Serverless "
                 "bills OCU-hours for indexing and search separately, plus storage per GB-month in S3-backed managed storage. Classic Serverless "
                 "collections keep a minimum number of OCUs running; next-generation collections can drop compute to zero when idle and bill "
                 "only storage. OpenSearch Ingestion pipelines bill their own capacity units. List prices, check your region.",
        "drivers": [
            "Node count and size on domains, including dedicated manager nodes and replicas.",
            "OCU-hours on Serverless, driven by indexing rate and query load.",
            "Data volume and retention, split across hot, warm and cold tiers.",
            "Vector count and dimensions, which need memory.",
        ],
        "traps": [
            "Classic Serverless minimum OCUs billed around the clock for a small or test collection.",
            "Clusters sized for peak with three zones of replicas that idle most of the day.",
            "Keeping months of logs in hot storage instead of warm or cold tiers.",
            "Re-indexing the full catalog every few minutes instead of only changes.",
        ],
    },
    "security": [
        "Create domains inside a VPC, or Serverless collections with VPC endpoints, and disable public access.",
        "Turn on fine-grained access control and map IAM roles or SAML groups to OpenSearch roles with index- and field-level permissions.",
        "Encrypt at rest with KMS, require node-to-node encryption and HTTPS with a modern TLS policy.",
        "Turn on audit logs for domains and send them to CloudWatch Logs; CloudTrail records configuration calls.",
        "Index only fields search needs; mask or drop personal data in the export job, because Unity Catalog policies do not follow data into OpenSearch.",
    ],
    "monitor": [
        ("ClusterStatus.red", "One or more primary shards are unassigned; some data cannot be searched or written."),
        ("JVMMemoryPressure", "Heap use on nodes; sustained values above about 80 percent precede garbage collection stalls and node loss."),
        ("FreeStorageSpace", "Disk left per node; low values block writes when the cluster sets indices to read-only."),
        ("ThreadpoolWriteRejected", "Bulk write requests rejected because the cluster is overloaded."),
        ("SearchLatency", "Time to answer searches; the measure users feel."),
        ("SearchOCU and IndexingOCU", "Capacity used by a Serverless collection, which is what you pay for."),
    ],
    "limits": [
        ("Shards per node", "1,000 per 16 GB of heap, up to 4,000, on OpenSearch 2.17 and later"),
        ("Data nodes per domain", "Up to 1,002 hot nodes across three zones, by instance family and request"),
        ("HTTP request payload", "10 MiB on small instance types, 100 MiB on larger ones"),
        ("Shard size", "65 GiB maximum per shard for Multi-AZ with Standby on most instance families"),
        ("Domain access policy", "100 KiB"),
    ],
    "decisions": [
        ("Website product search for 200,000 products", "OpenSearch indexed hourly from the gold product table",
         "Pursue with care: the right tool for full-text search, owned by the app team, with no personal data indexed."),
        ("Retrieval for an internal assistant over quality reports", "OpenSearch vector search",
         "Drop: use Databricks Vector Search so access and lineage stay in Unity Catalog."),
        ("Existing OpenSearch cluster for application and security logs", "Keep it",
         "Keep if you have it: it does that job well; do not move platform analytics into it."),
        ("Ad hoc analysis of sales by store", "OpenSearch aggregations",
         "Drop: use the Databricks SQL warehouse or Athena on the tables."),
    ],
    "faq": [
        ("Is OpenSearch the same as Elasticsearch?",
         "OpenSearch began as a fork of Elasticsearch 7.10 in 2021 and is now governed by the OpenSearch Software Foundation. The APIs are similar but have diverged; Amazon OpenSearch Service also still runs some older Elasticsearch versions."),
        ("Does OpenSearch Serverless still have a minimum cost?",
         "Classic collections keep a minimum number of OCUs running. The next generation, generally available since May 2026, can scale compute to zero after ten idle minutes, while storage is still billed."),
        ("Should I use OpenSearch or Databricks Vector Search for RAG?",
         "On this platform, Databricks Vector Search, because it syncs from Delta tables and stays governed by Unity Catalog. OpenSearch fits when an application outside Databricks needs hybrid keyword and vector search."),
        ("How do I load gold tables into OpenSearch?",
         "Run a scheduled Databricks job that reads the gold table, or only its changes, and bulk-indexes documents into OpenSearch, ideally into a new index switched in with an alias for full rebuilds."),
    ],
    "sources": [
        ("AWS docs: Amazon OpenSearch Service quotas", "https://docs.aws.amazon.com/opensearch-service/latest/developerguide/limits.html"),
        ("AWS What's New: next generation of OpenSearch Serverless GA (May 2026)", "https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-opensearch-serverless-next-generation-generally-available/"),
        ("AWS What's New: OpenSearch Serverless collection groups (Feb 2026)", "https://aws.amazon.com/about-aws/whats-new/2026/02/amazon-opensearch-serverless-supports-collection-groups"),
        ("AWS docs: Creating Serverless collections", "https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-create.html"),
        ("AWS pricing: Amazon OpenSearch Service", "https://aws.amazon.com/opensearch-service/pricing/"),
    ],
    "related": [
        ("AWS and Databricks reference platform", "/learn/data-platform-architecture/aws-databricks/"),
        ("Amazon CloudWatch", "svc:cloudwatch"),
        ("Amazon Bedrock", "svc:bedrock"),
        ("Amazon Athena", "svc:athena"),
        ("AWS on this site", "/platforms/aws/"),
    ],
}
