SERVICE = {
    "slug": "data-exchange",
    "name": "AWS Data Exchange",
    "short": "Data Exchange",
    "group": "ingestion",
    "one_line": "A catalog and delivery service for third-party data: subscribe to files, APIs, Redshift shares or S3 access from providers, or send data grants.",
    "status": "Generally available. Lake Formation data sets are in preview. Not offered in Mumbai (ap-south-1); 11 Regions as of 2026-11-11.",
    "checked": "2026-11-11",
    "site_verdict": ("Pursue with care",
                     "Use it only when the outside data you need, such as rubber prices or weather, is sold there. Auto-export each new "
                     "revision into S3 landing so the lander treats it like a supplier file. For sharing our own data with car makers "
                     "and suppliers the site uses Delta Sharing, not Data Exchange."),
    "equivalents": {"azure": "Azure Marketplace data offers and Azure Data Share",
                    "gcp": "BigQuery sharing (formerly Analytics Hub)",
                    "databricks": "Databricks Marketplace and Delta Sharing",
                    "open_source": "Delta Sharing protocol, or plain signed URLs and SFTP"},
    "plain": [
        "AWS Data Exchange is a shop and a delivery service for data that comes from outside your company. Data providers, such as market "
        "data firms, weather services or commodity price publishers, list data products in AWS Marketplace. You subscribe, accept their terms "
        "and price, and the data arrives in your AWS account. When the provider publishes an update, it shows up as a new revision. A revision "
        "is a numbered version of a data set, a bit like a new edition of a magazine.",
        "The data can arrive in five shapes. Files are copied objects you can export into your own S3 bucket. API data sets let you call the "
        "provider's API through AWS with your subscription as the key. Amazon Redshift data sets give you read-only access to a provider's "
        "Redshift data share. Amazon S3 data access lets you read files directly in the provider's bucket without copying them. AWS Lake "
        "Formation data sets, which share tables in a provider's lake, are still in preview. Separately, anyone with an AWS account can send a "
        "data grant, which is a private, time-limited offer of a data set to one named account, without a Marketplace listing.",
        "A concrete example: a tyre maker buys natural rubber, synthetic rubber and carbon black, and the cost team wants daily commodity "
        "prices next to purchase orders from SAP. A price publisher sells a daily file product on Data Exchange. The team subscribes, turns on "
        "auto-export to the landing bucket, and every morning the new price file lands in S3 beside the other supplier files. Silver tables "
        "join prices to purchase orders by material and date.",
    ],
    "analogy": "A newsagent that delivers each new edition of the papers you subscribe to straight into your letterbox, and keeps the receipts.",
    "big_picture": [
        "On the reference platform Data Exchange is a minor mover in the Move in lane. It is not part of the core path; it is only used when "
        "an outside data product the business wants is sold there. Its job ends at the landing bucket: auto-export copies each new revision "
        "into S3, and from there the Common Ingestion Framework treats it exactly like a supplier file from Transfer Family.",
        "What feeds it is the provider's publishing process. What reads its output is Databricks Auto Loader, which appends the new files to "
        "a bronze table for that product. Silver then conforms units, currencies and material codes, and gold carries cost or market views. "
        "Redshift data sets can also be queried from the existing Redshift, but the site keeps new work on Databricks, so files are preferred.",
        "One practical snag sets the shape of the design. Data Exchange runs in 11 Regions and Mumbai is not one of them. A platform in "
        "Mumbai subscribes in a supported Region such as Singapore and exports revisions across Regions into the Mumbai landing bucket. That "
        "adds cross-Region transfer charges and one more place to watch, which is acceptable for small daily files and a reason to think "
        "twice for large ones.",
        "For the other direction, sharing our own gold data with car makers and suppliers, the site uses Delta Sharing from Unity Catalog. It "
        "is an open protocol readable without Databricks or AWS, and it keeps permissions in one catalog. Databricks Marketplace is the "
        "Databricks-native place to find and receive data products shared that way.",
    ],
    "upstream": ["Third-party data providers on AWS Marketplace", "Data grants from partner AWS accounts", "Open Data on AWS"],
    "downstream": ["svc:s3", "Databricks Auto Loader into bronze", "svc:redshift"],
    "concepts": [
        ("Data product", "A listing in AWS Marketplace that holds one or more data sets, with a description, samples and offers. It is what you subscribe to."),
        ("Offer and subscription", "An offer sets the price, duration and data subscription agreement. Accepting it creates a subscription that gives your account access for that term."),
        ("Data set", "A collection of data from one provider, of one type: Files, API, Amazon Redshift, Amazon S3 or Lake Formation (preview)."),
        ("Revision", "A published version of a file data set. Providers add revisions as data changes; each holds assets."),
        ("Asset", "One piece of data inside a revision: a file, an API, a Redshift datashare, an S3 location or a Lake Formation permission."),
        ("Auto-export", "An event action that copies every new revision of a file data set into an S3 bucket you choose, without anyone pressing a button."),
        ("Data grant", "A private, time-limited share of a data set from one AWS account to another, created without listing a product in Marketplace."),
        ("Bring Your Own Subscription (BYOS)", "An offer type that moves an existing contract with a provider onto Data Exchange delivery, without paying twice."),
    ],
    "use_when": [
        "The external data you need, such as commodity prices, weather or market indexes, is already sold as a Data Exchange product.",
        "You already pay a provider and they offer delivery through Data Exchange, so a BYOS offer replaces a fragile SFTP or email feed.",
        "Procurement prefers to buy data through the AWS bill and Marketplace contracts instead of a separate supplier agreement.",
        "You want each new release delivered into S3 automatically, with a clear revision history of what arrived when.",
        "A provider shares a Redshift data share and you still run Redshift for existing reports.",
    ],
    "avoid_when": [
        "You want to share your own gold data with partners; Delta Sharing from Unity Catalog keeps permissions in one place and needs no AWS account on their side.",
        "The provider offers a plain SFTP or API feed at a lower price; Transfer Family or our puller is enough.",
        "Your platform must keep all processing in one Region that Data Exchange does not support, and cross-Region copies are not allowed.",
        "You need table-level sharing through Lake Formation in production; that data set type is still in preview.",
        "The data is large and changes constantly; repeated revision exports and cross-Region copies become slow and expensive.",
    ],
    "challenges": [
        ("Region not supported", "Mumbai and several other Regions have no Data Exchange endpoint, so the subscription lives elsewhere.",
         "Subscribe in the nearest supported Region and auto-export across Regions into landing; record the Region in the source YAML and budget for transfer."),
        ("Full snapshots in every revision", "Some providers publish the whole history in each revision, so each export lands a complete copy and bronze grows quickly.",
         "Read the product's revision notes, keep only the latest snapshot in landing, and deduplicate by business key in silver."),
        ("Schema changes without warning", "Providers add columns, rename fields or change units between revisions.",
         "Keep raw files in bronze, check the schema in the lander, and subscribe to the provider's change notes."),
        ("Subscription expiry", "When a subscription or grant ends, access stops and exports fail, often noticed only when a dashboard goes stale.",
         "Track end dates in the source YAML, alert weeks ahead, and turn on auto-renew where the contract allows."),
        ("Licence terms on downstream use", "The data subscription agreement may forbid resharing, derived products or use outside named teams.",
         "Tag the bronze and silver tables with the licence in Unity Catalog and keep them out of external Delta Shares."),
        ("Export limits for large backfills", "A revision export handles up to 10,000 assets and a single asset is capped at 100 GB, so big backfills need many jobs.",
         "Script backfills revision by revision, stay within the concurrent job limits, and prefer S3 data access for very large sets."),
        ("Two sharing systems", "Teams start sharing internal data through Data Exchange grants as well as Delta Sharing, and nobody knows which copy is current.",
         "Write down one rule: Data Exchange in, Delta Sharing out, and review any exception."),
    ],
    "compare": [
        ("Databricks Marketplace and Delta Sharing", "The provider publishes through Delta Sharing, or you share data out to partners; tables arrive in Unity Catalog with no copy.",
         "The product you want is only sold on AWS Marketplace."),
        ("AWS Transfer Family (SFTP)", "The provider already sends files over SFTP and you have a direct contract.",
         "The provider only sells through Data Exchange, or you want Marketplace billing."),
        ("Provider API with our puller", "The provider has a simple REST API and charges less outside Marketplace.",
         "You want the subscription, entitlements and revision history managed for you."),
        ("Google BigQuery sharing", "The platform runs on Google Cloud and the data should arrive as linked BigQuery datasets.",
         "You are on AWS and the lake is in S3."),
        ("Azure Marketplace data offers and Azure Data Share", "The platform runs on Azure and providers deliver into Azure storage.",
         "You are on AWS with Databricks; Delta Sharing covers the same need across clouds."),
    ],
    "cost": {
        "model": "As a subscriber you pay the price the provider sets for the product, upfront, on a schedule or pay-as-you-go, billed through AWS Marketplace. "
                 "Data Exchange adds no separate subscriber fee in the published model, but you pay for the AWS services you use: S3 storage for exported files, "
                 "S3 transfer for cross-Region exports, and S3 request charges when reading a provider's bucket that uses Requester Pays. Providers pay "
                 "Marketplace fulfilment fees, and senders of data grants pay per hour a grant is active (list price, check your region).",
        "drivers": [
            "The provider's subscription price, which is usually far larger than any AWS charge.",
            "Cross-Region transfer when the subscription Region differs from the landing Region, as it does for Mumbai.",
            "S3 storage of exported revisions, especially when each revision is a full snapshot.",
            "Requests and downloads paid by you on S3 data access products with Requester Pays on.",
        ],
        "traps": [
            "Keeping every full-snapshot revision forever in landing and bronze multiplies storage for no new information.",
            "Auto-renewing subscriptions nobody uses any more; check last-read dates before renewal.",
            "Scanning a provider's large S3 bucket repeatedly from Databricks with Requester Pays turns into a request bill.",
            "Buying the same data twice, once directly and once on Marketplace; use BYOS to move an existing contract.",
        ],
    },
    "security": [
        "Limit who can subscribe and accept offers with IAM permissions on aws-marketplace and dataexchange actions; purchasing should sit with a small procurement role.",
        "Auto-export only into the landing bucket for the right catalog, encrypted with that catalog's KMS key, through a bucket policy scoped to the Data Exchange service.",
        "Reach S3 through the VPC endpoint from Databricks compute so no public path is needed after export.",
        "Record subscriptions, grants, exports and job runs in CloudTrail and keep the subscription ARN in the source YAML.",
        "Most bought data is not personal, but some marketing and location products are; check the data subscription agreement and let Macie scan the landing bucket.",
        "Keep licence limits in Unity Catalog tags and never include licensed tables in external Delta Shares.",
    ],
    "monitor": [
        ("Revision Published To Data Set events", "EventBridge event when a provider adds a revision; use it to expect a file and to start the lander."),
        ("Auto-export job status", "Export jobs move to COMPLETED or ERROR; alarm on errors so a missing price file is caught the same morning."),
        ("Landing file freshness", "The lander's file log should show a new file per expected revision; a gap means the provider or the export stopped."),
        ("Subscription end dates", "From the Data Exchange console or Marketplace API; alert well before expiry."),
        ("CloudTrail events for dataexchange", "Who subscribed, created grants or changed event actions."),
        ("Cross-Region transfer cost in CUR", "Shows whether cross-Region exports are growing faster than expected."),
    ],
    "limits": [
        ("Asset size", "100 GB per asset, not adjustable"),
        ("Assets per revision", "10,000 (adjustable)"),
        ("Auto-export event actions", "5 per data set; 50 event actions per account"),
        ("Concurrent export jobs to S3", "10 for assets, 5 for revisions, per Region"),
        ("Cross-Region revision export", "Up to 1,000 GB per revision"),
        ("Supported Regions", "11 Regions in the US, Europe and Asia Pacific; Mumbai is not one"),
    ],
    "decisions": [
        ("Daily rubber and carbon black prices sold only on AWS Marketplace", "Subscribe in Singapore and auto-export each revision to the Mumbai landing bucket",
         "Pursue with care: small daily files make cross-Region copies cheap, but watch expiry and licence terms."),
        ("Sharing quality results by batch with car makers", "Delta Sharing of a filtered gold view from Unity Catalog",
         "Drop: Data Exchange grants are the wrong tool; Delta Sharing is open and keeps permissions in one catalog."),
        ("A provider offering a Redshift data share", "Query it from the existing Redshift while reports move",
         "Keep if you have it: fine for current BI, but land a file copy for new Databricks work."),
        ("Weather history for demand forecasting", "Compare Open Data on AWS, Databricks Marketplace and paid products",
         "Pursue with care: free open data may be enough; pay only for what improves the forecast."),
    ],
    "faq": [
        ("What is AWS Data Exchange used for?", "It is used to find, subscribe to and receive third-party data inside AWS. Providers publish data products in AWS Marketplace, and subscribers get files, APIs, Redshift shares or S3 access. It also lets any AWS account send a private data grant to another account."),
        ("Is AWS Data Exchange available in the Mumbai Region?", "No. As of 11 November 2026 it runs in 11 Regions across the US, Europe and Asia Pacific, and Mumbai is not one. You can subscribe in a supported Region and export revisions to an S3 bucket in another Region."),
        ("Is there a fee for subscribers?", "You pay the provider's price through AWS Marketplace, plus normal AWS charges for storage, transfer and requests. Data Exchange's own per-hour grant fees fall on senders, not receivers."),
        ("Data Exchange or Delta Sharing?", "Use Data Exchange to receive data that is sold there. Use Delta Sharing to share your own tables with partners, because it is an open protocol, needs no AWS account on their side and keeps permissions in Unity Catalog."),
        ("Can Databricks read Data Exchange data directly?", "For file products, auto-export them into your S3 bucket and read them with Auto Loader. For S3 data access products, Databricks can read the provider's bucket if your IAM role is entitled, but you pay the requests."),
    ],
    "sources": [
        ("AWS docs: What is AWS Data Exchange", "https://docs.aws.amazon.com/data-exchange/latest/userguide/what-is.html"),
        ("AWS docs: AWS Data Exchange endpoints and quotas", "https://docs.aws.amazon.com/general/latest/gr/dataexchange.html"),
        ("AWS docs: AWS Data Exchange quotas and job guidelines", "https://docs.aws.amazon.com/data-exchange/latest/userguide/limits.html"),
        ("AWS: AWS Data Exchange pricing", "https://aws.amazon.com/data-exchange/pricing/"),
        ("AWS docs: AWS lifecycle changes", "https://docs.aws.amazon.com/general/latest/gr/service-lifecycle.html"),
    ],
    "related": [
        ("Common Ingestion Framework", "/learn/data-platform-architecture/ingestion/"),
        ("Data platform on AWS and Databricks", "/learn/data-platform-architecture/aws-databricks/"),
        ("AWS Transfer Family", "svc:transfer-family"),
        ("Amazon S3", "svc:s3"),
        ("Amazon Redshift", "svc:redshift"),
    ],
}
