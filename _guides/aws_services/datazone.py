SERVICE = {
    "slug": "datazone",
    "name": "Amazon DataZone (and SageMaker Unified Studio catalog)",
    "short": "DataZone",
    "group": "catalog",
    "one_line": "A business data catalog and request-and-approve sharing portal, now the catalog layer inside Amazon SageMaker Unified Studio.",
    "status": ("Generally available. DataZone is now the catalog and governance layer under Amazon SageMaker Unified Studio "
               "(the SageMaker Catalog). Older DataZone domains (version V1) can be upgraded to SageMaker unified domains (V2) "
               "from the console only; the APIs stay the same, and both portals stay open until an admin turns off the DataZone portal. "
               "No per-user charge since 1 Nov 2024."),
    "checked": "2026-11-11",
    "site_verdict": ("Drop", "On an AWS plus Databricks platform, Unity Catalog already does discovery, lineage, tags, grants and sharing. "
                     "DataZone grants only reach Lake Formation tables and Redshift, so it would be a second shop window over data "
                     "it cannot govern. Keep it only if the wider company already runs SageMaker Unified Studio; then expose gold "
                     "tables to it through Glue catalog federation instead of copying them."),
    "equivalents": {"azure": "Microsoft Purview (Unified Catalog)", "gcp": "Dataplex Universal Catalog",
                    "databricks": "Unity Catalog with Catalog Explorer, tags, lineage and access requests",
                    "open_source": "OpenMetadata or DataHub"},
    "plain": [
        "Every company with a data platform eventually hits the same question from the business side: what data do we have, "
        "what does it mean, who owns it, and how do I get access? Amazon DataZone answers that with a business data catalog. "
        "A catalog here is a searchable list of data sets, each with a plain-language description, an owner, business terms "
        "and a history of who uses it. DataZone adds a shopping-style workflow on top: a user finds a data set, clicks "
        "subscribe, writes why they need it, and the owner approves or rejects the request.",
        "Picture a tyre and rubber manufacturer. The quality team publishes a table of curing press readings, and the sales "
        "team publishes daily orders by dealer. A planner in another business unit searches the portal for scrap rate, finds "
        "the quality team's table described as scrap by press and shift, sees the glossary term that defines scrap, and asks "
        "for access. The quality data owner approves, and DataZone grants the planner's project read access through Lake "
        "Formation, so the planner can query it in Athena the same afternoon.",
        "DataZone groups people into projects, which are teams working towards one goal, and groups projects into domains, "
        "which are the top-level boxes that hold a whole organisation's catalog, glossaries and rules. Since 2025 AWS has "
        "folded DataZone into Amazon SageMaker Unified Studio: the same service and the same APIs now sit underneath the "
        "SageMaker Catalog, and new users meet it as a part of SageMaker rather than as a separate product. The DataZone "
        "name, console and API remain, and older domains can be upgraded to the new kind.",
    ],
    "analogy": "A library's front desk and card index for company data: you search the cards, ask the librarian, and the librarian unlocks the shelf if the owner agrees.",
    "big_picture": [
        "DataZone sits in the band across the whole platform, next to the catalog and access control, rather than in any one "
        "lane. It does not store data or run queries. It reads technical metadata from the AWS Glue Data Catalog and Amazon "
        "Redshift, lets people add business meaning, and when a request is approved it asks Lake Formation or Redshift to "
        "grant access. For any other kind of data it only publishes an event to EventBridge and leaves the grant to you.",
        "On this site's reference platform the catalog job belongs to Unity Catalog in Databricks. Bronze, silver and gold "
        "tables, their lineage, their tags, their column masks and their grants all live there, and Catalog Explorer is where "
        "people search. Adding DataZone would mean a second catalog describing tables it does not own and cannot grant on, "
        "because Unity Catalog managed tables are not Lake Formation tables. Two catalogs drift apart within weeks.",
        "The one place it fits is a company where another division already runs SageMaker Unified Studio for analytics or "
        "machine learning. Then the right move is to let that side see our gold tables without copies: Glue catalog "
        "federation can expose Unity Catalog Iceberg tables in the Glue Data Catalog, and DataZone can list them from there. "
        "Ownership, quality and grants stay in Unity Catalog; DataZone becomes a shop window for that audience only.",
    ],
    "upstream": ["svc:glue-data-catalog", "svc:redshift", "Business owners adding descriptions"],
    "downstream": ["svc:lake-formation", "svc:athena", "svc:sagemaker"],
    "concepts": [
        ("Domain", "The top-level container for one organisation's catalog, glossaries, projects, users and policies. V1 domains are classic DataZone; V2 domains are SageMaker unified domains."),
        ("Project", "A team working space. Projects own the data they publish and subscribe to data owned by other projects."),
        ("Asset", "One catalogued item, such as a Glue table, a Redshift view or an S3 location, with its technical schema and business metadata."),
        ("Data product", "A bundle of assets published and requested together, such as all the tables behind a plant scrap report."),
        ("Business glossary", "A list of agreed business terms, such as scrap rate or first-pass yield, that can be attached to assets and columns."),
        ("Metadata form", "A template of extra fields an asset must carry, such as data owner, sensitivity or retention period."),
        ("Subscription", "A request by a project to use an asset, with a reason; the owner approves or rejects it and access is granted on approval."),
        ("Data source run", "A scheduled job that reads technical metadata from Glue or Redshift into the catalog so new tables and columns appear."),
        ("Domain unit", "A sub-division of a domain, such as a business unit, used to hand out authority to publish and approve."),
    ],
    "use_when": [
        "Your platform is built on AWS-native engines such as Athena, Redshift, Glue and EMR, and tables are governed by Lake Formation.",
        "The company has standardised on SageMaker Unified Studio, and business users already go there to find and request data.",
        "You need a request-and-approve workflow with a written reason and an audit trail, and Lake Formation grants are the target.",
        "Many accounts and business units share data, and you want a single portal where owners publish and consumers subscribe across accounts.",
        "You want business glossaries and required metadata fields attached to AWS tables without buying a separate catalog product.",
    ],
    "avoid_when": [
        "Databricks and Unity Catalog own your tables, because DataZone cannot grant access to Unity Catalog managed tables and would only describe them.",
        "You hope it will be the single source of lineage; its lineage only sees what is reported to it, while Unity Catalog records Databricks lineage automatically.",
        "Your consumers live mostly in Power BI, Databricks AI/BI or other tools outside AWS, where the subscription workflow has no effect.",
        "You have one small team and a handful of tables; a well-described Unity Catalog with tags and owners is enough.",
        "You would need to copy gold tables into Glue just so DataZone can see them; a copy creates two truths.",
    ],
    "challenges": [
        ("Two catalogs, two truths",
         "Descriptions, owners and tags are typed into Unity Catalog and again into DataZone, and the two disagree within a month.",
         "Pick one catalog of record. On this platform that is Unity Catalog; if DataZone must exist, fill it from Unity Catalog by automation, never by hand."),
        ("Grants that do nothing",
         "A subscription is approved, but the asset is not a Lake Formation or Redshift asset, so DataZone only emits an event and nobody gets access.",
         "Check which assets support managed fulfilment before you publish them; for the rest, wire the EventBridge event to a function that grants access where the data really lives."),
        ("Lake Formation fights",
         "DataZone grants through Lake Formation, but tables still in IAM-only mode or hybrid access mode behave differently, and users see access denied.",
         "Register the S3 locations and decide the Lake Formation mode per database before onboarding them to DataZone."),
        ("Stale metadata",
         "New columns or tables do not appear because data source runs are scheduled rarely or fail quietly.",
         "Schedule data source runs to match how often schemas change, and alert on failed runs; the default quota is 25 runs per data source per day."),
        ("V1 to V2 upgrade surprises",
         "After upgrading to a SageMaker unified domain, environments and environment profiles do not carry over, and infrastructure-as-code templates need changes.",
         "Rehearse the upgrade on a copy domain, rewrite templates to set the domain version, and keep the old portal open until users have moved."),
        ("Nobody curates",
         "The portal goes live with technical table names and no descriptions, people find nothing useful, and adoption stalls.",
         "Make a named owner and a description mandatory through metadata forms, and publish only curated gold data products at first."),
        ("Cross-account confusion",
         "Associated accounts rely on AWS Resource Access Manager shares, and a changed share or missing role breaks publishing from that account.",
         "Manage domain association and roles in code, and test publishing from each associated account after every change."),
    ],
    "compare": [
        ("Unity Catalog (Databricks)",
         "Databricks processes and owns the tables. It gives search, lineage, tags, masks, grants and access requests on the data it governs.",
         "Most of your data lives in Redshift and Glue tables that Databricks never touches."),
        ("AWS Lake Formation alone",
         "You need fine-grained grants on Glue tables but no business portal or approval workflow.",
         "Business users must find and request data themselves without asking engineers."),
        ("Microsoft Purview (Azure)",
         "Your estate is mostly Azure and Microsoft Fabric, and you want one catalog with data quality and sensitivity labels there.",
         "Your platform is on AWS; Purview can scan AWS sources but is not the natural home."),
        ("Dataplex Universal Catalog (Google Cloud)",
         "Your data lives in BigQuery and Cloud Storage and you want the Google-native catalog.",
         "You run on AWS."),
        ("OpenMetadata or DataHub",
         "You need one catalog across many platforms and clouds and are willing to run it yourself.",
         "You do not have the people to host, upgrade and connect an open-source catalog."),
        ("Commercial catalogs such as Collibra or Alation",
         "Governance is a company-wide programme with stewards, policies and many source systems.",
         "You only need a catalog for one platform that already has Unity Catalog."),
    ],
    "cost": {
        "model": ("Pay as you go with no user licence: since 1 Nov 2024 there is no monthly per-user charge. You pay for "
                  "billable API requests, for metadata storage per GB a month, and for compute units used when metadata is "
                  "ingested or business names are generated. Generative recommendations are billed per token. A small free "
                  "allowance per account each month covers light use. List prices, check your region. The services that "
                  "hold and query the data, such as Glue, Athena, Redshift, S3 and KMS, bill separately."),
        "drivers": [
            "How many assets and how much business metadata you keep, which drives metadata storage.",
            "How often data source runs read Glue and Redshift, which drives compute units.",
            "How many API calls your automation and portal users make, beyond the core calls AWS does not charge for.",
            "Use of generated descriptions and business names, which are billed per token.",
            "If you use the wider SageMaker Unified Studio, its notebooks and compute bill on their own meters.",
        ],
        "traps": [
            "Running data source runs every hour on schemas that change monthly burns compute units for nothing.",
            "The DataZone bill is small, but the hidden cost is people: stewards keeping a second catalog in step with Unity Catalog.",
            "Turning on generated descriptions for every asset has no free allowance and adds a token bill.",
            "Copying tables into Glue just to make them visible doubles storage and pipeline cost.",
        ],
    },
    "security": [
        "Users sign in through IAM Identity Center (single sign-on) or with IAM roles; map groups from your company identity provider rather than adding people one by one.",
        "Domain execution and service roles let the service act on your behalf; scope them to the accounts and databases the domain needs.",
        "Domain metadata is encrypted at rest; you can supply your own KMS key when you create the domain.",
        "Access is granted through Lake Formation and Redshift permissions, so the real enforcement point is there; audit those grants, not only the portal.",
        "Every API call is recorded in CloudTrail, and subscription approvals and rejections can be sent to EventBridge for an audit store.",
        "Business descriptions can leak personal or confidential detail; treat the catalog itself as internal data and do not paste sample rows with personal data.",
    ],
    "monitor": [
        ("Data source run status", "Failed or skipped metadata imports mean new tables and columns are missing from the catalog."),
        ("Subscription requests pending", "Requests waiting days for approval show owners who are not doing their part."),
        ("Subscription grant failures", "Approved requests whose Lake Formation or Redshift grant failed, so the user still has no access."),
        ("EventBridge subscription events", "Approval and rejection events, kept as an audit record and used to trigger custom grants."),
        ("CloudTrail datazone.amazonaws.com events", "Who changed glossaries, forms, projects and policies, and when."),
        ("Assets without owner or description", "A curation measure; a rising share means the catalog is filling with untended entries."),
    ],
    "limits": [
        ("Assets per domain", "1,000,000 by default, adjustable"),
        ("Data products per domain", "500,000 by default, adjustable"),
        ("Glossaries per domain", "1,000 by default; 10,000 business glossary terms"),
        ("Data source runs", "25 runs per data source per day by default"),
        ("Domain upgrade", "V1 to V2 upgrade is console only; rollback only while no project created in SageMaker Unified Studio exists"),
    ],
    "decisions": [
        ("Databricks owns all tables, Unity Catalog is the catalog",
         "Unity Catalog with descriptions, tags, owners and access requests",
         "Drop: DataZone would describe tables it cannot grant on."),
        ("A sister division already runs SageMaker Unified Studio and wants our gold data",
         "Glue catalog federation to Unity Catalog, listed in their SageMaker Catalog",
         "Keep if you have it: their portal, our ownership; no copies, grants stay in Unity Catalog."),
        ("AWS-only platform with Athena, Redshift and Lake Formation, many business units",
         "SageMaker unified domain (DataZone V2) as the business catalog",
         "Pursue with care: good fit, but name owners and required metadata before go-live."),
        ("Existing classic DataZone domain (V1)",
         "Upgrade to a SageMaker unified domain after a rehearsal",
         "Pursue with care: same APIs and identifiers, but environments do not carry over and templates need edits."),
    ],
    "faq": [
        ("Is Amazon DataZone being retired?",
         "No. It is generally available, and it now sits underneath Amazon SageMaker Unified Studio as the catalog and governance layer. Existing DataZone domains keep working and can be upgraded to SageMaker unified domains."),
        ("What is the difference between DataZone and SageMaker Catalog?",
         "They share one service and one API. SageMaker Catalog is how the catalog appears inside SageMaker Unified Studio on a V2 domain; a V1 domain uses the original DataZone portal."),
        ("Can DataZone govern Databricks Unity Catalog tables?",
         "Not directly. It grants access through Lake Formation and Redshift. Unity Catalog tables can be made visible in the Glue Data Catalog through catalog federation and listed, but the real permissions remain in Unity Catalog."),
        ("Does DataZone charge per user?",
         "No. Since 1 November 2024 there is no per-user subscription. You pay for requests, metadata storage and compute units, with a small free monthly allowance."),
        ("Do I need both DataZone and Lake Formation?",
         "If you use DataZone on AWS tables, yes: DataZone is the portal and workflow, and Lake Formation is the permission system it writes to."),
    ],
    "sources": [
        ("AWS docs: What is Amazon DataZone", "https://docs.aws.amazon.com/datazone/latest/userguide/what-is-datazone.html"),
        ("AWS docs: Upgrade DataZone domains to SageMaker unified domains", "https://docs.aws.amazon.com/sagemaker-unified-studio/latest/adminguide/upgrade-domain.html"),
        ("AWS: Amazon DataZone pricing", "https://aws.amazon.com/datazone/pricing/"),
        ("AWS docs: DataZone endpoints and quotas", "https://docs.aws.amazon.com/general/latest/gr/datazone.html"),
    ],
    "related": [
        ("Data platform on AWS + Databricks", "/learn/data-platform-architecture/aws-databricks/"),
        ("AWS Lake Formation", "svc:lake-formation"),
        ("AWS Glue Data Catalog", "svc:glue-data-catalog"),
        ("Amazon SageMaker AI and Unified Studio", "svc:sagemaker"),
        ("Metadata store", "/learn/data-platform-architecture/metadata-store/"),
    ],
}
