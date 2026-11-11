SERVICE = {
    "slug": "elasticache",
    "name": "Amazon ElastiCache (Valkey, Redis OSS)",
    "short": "ElastiCache",
    "group": "operational",
    "one_line": "Managed in-memory cache (Valkey, Redis OSS or Memcached) for sub-millisecond lookups; dropped as the platform's primary live store.",
    "status": "Generally available, as node-based clusters or Serverless. Valkey is the engine AWS now leads with. Redis OSS 4 and 5 left standard support on 31 Jan 2026 and are billed for Extended Support; Redis OSS 6 follows on 31 Jan 2027.",
    "checked": "2026-11-11",
    "site_verdict": ("Drop",
                     "Dropped as the primary live store for the seconds lane: it is the fastest latest-value cache, but it keeps no durable history, "
                     "memory must be sized, and DynamoDB already gives push, a 48-hour chart and about $50 a month. Use it only as a cache in front of "
                     "an application or API that is measurably too slow, and choose Valkey if you do."),
    "equivalents": {"azure": "Azure Cache for Redis, or Azure Managed Redis",
                    "gcp": "Memorystore (Valkey, Redis, Memcached)",
                    "databricks": "None; Lakebase or a Databricks App's own memory for small caches",
                    "open_source": "Valkey, Redis, Memcached"},
    "plain": [
        "Amazon ElastiCache runs an in-memory data store for you. In memory means the data lives in the servers' RAM instead of on disk, so a read "
        "takes well under a millisecond. You choose an engine: Valkey, the open-source fork of Redis that AWS and others now maintain; Redis OSS, "
        "the older open-source Redis versions; or Memcached, a simpler cache. Valkey and Redis store keys with values that can be strings, lists, "
        "hashes, sorted sets or streams, and they can publish messages to subscribers.",
        "It comes in two shapes. Node-based clusters are a set of cache servers, called nodes, that you size and pay for by the hour, optionally split "
        "into shards for more memory and with replicas for failover. ElastiCache Serverless has no nodes to choose: you pay for the data stored "
        "and for processing units used by requests, and it scales on its own.",
        "A retail example: an online store shows a product page with price, stock and a delivery estimate. Computing the delivery estimate means "
        "calling three systems and takes 400 milliseconds. A cache holds the answer per product and postcode for five minutes, so the next shopper "
        "gets it in one millisecond. If the cache is emptied, nothing is lost; the page is just slower until the cache warms up again. That is the "
        "right mental model: a cache is a copy you can afford to lose.",
    ],
    "analogy": "A whiteboard beside the shop counter with today's answers written on it: instant to read, wiped clean if the power goes off.",
    "big_picture": [
        "On this platform ElastiCache appears in only one place: the list of options for the live store in the streaming design's fast lane. The "
        "fast lane takes plant readings from Kinesis through Managed Flink and must show alerts and a 48-hour chart on screens within seconds. "
        "The options were DynamoDB, Lakebase, ClickHouse Cloud, ElastiCache with Valkey, and the two Timestream engines.",
        "ElastiCache lost as the primary store for three reasons. It holds latest values well but has no durable history; a 48-hour chart in memory "
        "means paying for RAM to hold every minute of every press. Memory has to be sized, and running out evicts data or rejects writes. And it "
        "does not emit a change stream the way DynamoDB Streams does, so pushing changes to the WebSocket needs extra code using its publish and "
        "subscribe feature, which does not keep messages for a subscriber that was offline. DynamoDB does the job with less to run.",
        "It is not part of the batch platform at all. Databricks does not need a cache to build bronze, silver and gold. Where ElastiCache does fit "
        "is in front of an application or an API that serves platform data to many users, when that read path is measured and found too slow. "
        "Even then, check first whether the Databricks SQL warehouse result cache or Lakebase already answers fast enough.",
    ],
    "upstream": ["Application or API code", "svc:managed-flink"],
    "downstream": ["svc:api-gateway", "Web and mobile apps"],
    "concepts": [
        ("Valkey", "The open-source, Linux Foundation fork of Redis, compatible with Redis OSS clients and commands. AWS prices it lower than Redis OSS on ElastiCache."),
        ("Node", "One cache server with a fixed amount of memory. You pick the node type, such as a memory-optimised Graviton node, and pay per hour."),
        ("Shard", "A slice of the keyspace with one primary node and optional replicas. More shards mean more memory and write throughput (cluster mode enabled)."),
        ("Replica and Multi-AZ", "Read copies of a primary in other Availability Zones; with automatic failover, a replica takes over if the primary fails."),
        ("Serverless cache", "A cache with no nodes to size, billed per GB-hour of data stored and per ElastiCache Processing Unit (ECPU) consumed by requests."),
        ("Eviction", "What happens when memory is full: the engine removes keys by a policy, such as least recently used, so data silently disappears."),
        ("TTL", "An expiry time set on a key; the key is removed when it passes, which keeps a cache fresh and bounded."),
        ("Extended Support", "A paid period after a Redis OSS version leaves standard support, during which AWS still patches it at a premium on the hourly price."),
    ],
    "use_when": [
        "An application or API repeatedly computes or fetches the same answer and users notice the delay; cache the answer with a TTL.",
        "You need sub-millisecond reads of small values at very high request rates, such as session tokens or rate-limit counters.",
        "You want leaderboards, counters or sorted rankings that Valkey's sorted sets handle natively, for example the top ten lines by output right now.",
        "The data can be rebuilt from a durable source if the cache is lost, so losing it costs only speed.",
    ],
    "avoid_when": [
        "It would be the only copy of data you must keep, such as the 48-hour chart for the live board; use DynamoDB.",
        "You need changes pushed reliably to screens; DynamoDB Streams keeps changes for 24 hours, while publish and subscribe drops messages for absent listeners.",
        "The batch platform is slow; caching does not fix slow pipelines, and the Databricks SQL warehouse has its own result cache.",
        "Nobody has measured a slow read path; a cache adds a second copy to keep correct, which is a source of stale-data bugs.",
        "You would run an old Redis OSS version without a plan to upgrade; Extended Support charges grow each year.",
    ],
    "challenges": [
        ("Stale data", "The source changes but the cache still serves the old value, so a price or stock level on screen is wrong.",
         "Set short TTLs that match how fresh the data must be. Delete or update the key when the source changes, and document which source owns each key."),
        ("Memory full and evictions", "The cache grows past its memory and starts evicting keys or rejecting writes; hit rates drop and the database behind it is flooded.",
         "Alarm on memory use and Evictions. Set TTLs on every key. Add shards, or use Serverless with a maximum data limit you have chosen."),
        ("Thundering herd", "A popular key expires and hundreds of requests hit the slow source at the same moment.",
         "Add random jitter to TTLs, refresh popular keys before they expire, or let only one request rebuild a key while others wait."),
        ("Big or hot keys", "One huge key or one very busy key overloads one shard while others idle.",
         "Split large values, spread hot keys, and use the engine's tools to find big keys before go-live."),
        ("Failover surprises", "A primary fails over to a replica and clients holding old connections error for a short time.",
         "Use the cluster's configuration endpoint, enable Multi-AZ with automatic failover, and test a failover in pre-production."),
        ("Old engine versions", "Clusters on Redis OSS 4 or 5 were moved into paid Extended Support on 1 Feb 2026, and the bill rose with no change in use.",
         "Upgrade to Valkey; existing Redis OSS reservations apply to Valkey nodes of the same family. Plan Redis OSS 6 upgrades before 31 Jan 2027."),
        ("Security left at defaults", "A cache created without in-transit encryption or authentication is reachable by anything in the VPC.",
         "Turn on encryption in transit and at rest, use role-based access control users or IAM authentication, and allow access only from named security groups."),
    ],
    "compare": [
        ("Amazon DynamoDB", "You need a durable live store with a 48-hour history and change push; the site's recommended choice.",
         "You need sub-millisecond reads at extreme rates for data you can lose; then a cache in front can help."),
        ("Amazon MemoryDB", "You want Valkey or Redis semantics but durable, with a multi-AZ transaction log, as a primary database.",
         "A cache is enough; MemoryDB costs more and writes are slower than ElastiCache."),
        ("Lakebase (Databricks managed PostgreSQL)", "You want SQL, governance in Unity Catalog and one fewer AWS service, and milliseconds are fast enough.",
         "You need sub-millisecond reads at very high request rates."),
        ("Azure Cache for Redis or Azure Managed Redis", "You are building the same cache on Azure.", "You are on AWS."),
        ("Google Memorystore", "You are building the same cache on Google Cloud; it also offers Valkey.", "You are on AWS."),
        ("Self-managed Valkey on EC2 or EKS", "You need modules or settings ElastiCache does not offer and have a team to run it.",
         "You want patching, failover and backups handled for you."),
    ],
    "cost": {
        "model": "Node-based clusters bill per node-hour by node type, so a cluster with replicas in two zones pays for every node all the time; "
                 "reserved nodes lower the hourly rate for a one- or three-year commitment. Serverless bills per GB-hour of data stored, with a "
                 "minimum per cache, plus ElastiCache Processing Units for the requests served. AWS states Valkey is priced up to 20 percent lower "
                 "than Redis OSS for nodes and up to 33 percent lower for Serverless. Backups beyond the free allowance and data transfer across "
                 "zones are extra. Versions in Extended Support carry a premium on the hourly price that rises in year three. The site's estimate "
                 "for a live-store cache is about $50 to $150 a month; list prices, check your region.",
        "drivers": [
            "Memory needed, which sets the node type and number of shards, or the GB-hours in Serverless.",
            "Number of replicas for high availability, each billed as a full node.",
            "Request volume, which drives ECPUs in Serverless.",
            "Engine choice: Valkey costs less than Redis OSS for the same capacity.",
        ],
        "traps": [
            "Staying on Redis OSS 4, 5 or later 6 past standard support adds an Extended Support premium of 80 percent in years one and two and more in year three, per AWS's example.",
            "Over-sized clusters bought for a peak that never comes, billed every hour.",
            "Serverless caches with no maximum set can grow with careless keys that never expire.",
            "Cross-zone traffic between application and cache nodes adds data transfer charges at high request rates.",
        ],
    },
    "security": [
        "ElastiCache runs only inside your VPC; limit access with security groups to the application's own security group and never open it widely.",
        "Turn on encryption in transit (TLS) and at rest, with a customer managed KMS key if your policy requires one.",
        "Use role-based access control users with passwords, or IAM authentication for Valkey and Redis OSS, instead of a single shared token.",
        "CloudTrail records management calls such as creating or modifying caches; data commands are not logged, so keep sensitive data out.",
        "Do not cache personal data unless needed; if you must, keep TTLs short and treat the cache as in scope for data protection reviews.",
    ],
    "monitor": [
        ("CacheHitRate", "Share of reads answered from the cache; a falling rate means the cache is not helping and the source is under load."),
        ("Evictions", "Keys removed because memory was full; any steady value means the cache is too small or keys lack TTLs."),
        ("DatabaseMemoryUsagePercentage", "How full memory is; alarm well before 100 percent."),
        ("EngineCPUUtilization", "CPU used by the engine's main thread; Valkey and Redis process commands largely on one thread, so this saturates first."),
        ("CurrConnections", "Open client connections; a steady climb usually means a client is leaking connections."),
        ("ReplicationLag", "How far replicas are behind the primary; high lag means reads from replicas are stale."),
    ],
    "limits": [
        ("Nodes per cluster (Valkey or Redis OSS, cluster mode)", "Up to 500 nodes per cluster, adjustable by request"),
        ("Replicas per shard", "Up to 5 read replicas per shard"),
        ("Value size", "512 MB per string value in Valkey and Redis OSS; keep values far smaller in practice"),
        ("Redis OSS 4 and 5", "End of standard support 31 Jan 2026; Extended Support until 31 Jan 2029"),
        ("Redis OSS 6", "End of standard support 31 Jan 2027"),
    ],
    "decisions": [
        ("Primary live store for 120 presses with a 48-hour chart", "ElastiCache Valkey",
         "Drop: no durable history, memory to size, and no change stream; DynamoDB is the site's choice."),
        ("Product page delivery estimate takes 400 ms", "ElastiCache Serverless with Valkey, five-minute TTL",
         "Pursue with care: a classic cache use, owned by the app team; measure the hit rate."),
        ("Existing Redis OSS 5 cluster for sessions", "Upgrade in place to Valkey",
         "Keep if you have it: keep the cache, but move to Valkey to leave Extended Support charges behind."),
        ("Dashboards on gold tables feel slow", "Put ElastiCache in front of the SQL warehouse",
         "Drop: use the warehouse's result cache, Metric Views and a right-sized warehouse first."),
    ],
    "faq": [
        ("Is ElastiCache Valkey the same as Redis?",
         "Valkey is an open-source fork of Redis 7.2, made after Redis changed its licence in 2024. It speaks the same protocol and commands, so most Redis clients work unchanged, and AWS prices it lower than Redis OSS."),
        ("Can ElastiCache be my main database?",
         "Not safely. It is a cache and can lose recent writes on failure. If you want Valkey or Redis semantics with durability, use Amazon MemoryDB; for the live board, use DynamoDB."),
        ("Why did the site drop ElastiCache as the live store?",
         "The live board needs latest values, a 48-hour chart and changes pushed to screens. DynamoDB gives all three with TTL and Streams for about $50 a month; ElastiCache gives only fast latest values and needs memory sized for history."),
        ("What happens to my Redis OSS 5 cluster?",
         "Standard support ended on 31 Jan 2026 and the cluster moved into paid Extended Support. That ends on 31 Jan 2029, after which AWS upgrades remaining caches to the latest Valkey. Upgrading now saves the premium."),
        ("Serverless or node-based?",
         "Serverless for new or spiky caches where you do not want to size memory. Node-based with reserved nodes for large, steady caches where the hourly rate is lower."),
    ],
    "sources": [
        ("AWS docs: ElastiCache Extended Support versions", "https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/extended-support-versions.html"),
        ("AWS docs: ElastiCache Extended Support charges", "https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/extended-support-charges.html"),
        ("AWS docs: Engine versions and upgrading in ElastiCache", "https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/engine-versions.html"),
        ("AWS pricing: Amazon ElastiCache", "https://aws.amazon.com/elasticache/pricing/"),
    ],
    "related": [
        ("Streaming on AWS and Databricks", "/learn/streaming/"),
        ("Real-time analytics", "/learn/real-time-analytics/"),
        ("Amazon DynamoDB", "svc:dynamodb"),
        ("Amazon API Gateway", "svc:api-gateway"),
        ("Amazon Timestream", "svc:timestream"),
    ],
}
