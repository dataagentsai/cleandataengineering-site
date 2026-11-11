SERVICE = {
    "slug": "lake-formation",
    "name": "AWS Lake Formation",
    "short": "Lake Formation",
    "group": "catalog",
    "one_line": "Database-style grants on Glue Data Catalog tables, down to columns, rows and cells, enforced across Athena, EMR, Redshift and Glue.",
    "status": "Generally available",
    "checked": "2026-11-11",
    "site_verdict": ("Keep if you have it",
                     "Unity Catalog is the one access model on this platform. Keep existing Lake Formation grants working while "
                     "readers move, make no new grants in Lake Formation from day one, and never run two access models for the same table."),
    "equivalents": {"azure": "Microsoft Purview data access policies and OneLake security in Fabric",
                    "gcp": "Dataplex and BigLake fine-grained access with IAM",
                    "databricks": "Unity Catalog grants, row filters, column masks and ABAC policies",
                    "open_source": "Apache Ranger"},
    "plain": [
        "Plain S3 security answers one question: may this role read these files? That is too coarse for a data lake. A "
        "sales analyst should see the orders table but not the customer phone column, and a plant manager in Pune should "
        "see only Pune's rows. Files cannot express that, because one Parquet file holds all the columns and many plants. "
        "You need permissions on tables, columns and rows, the way a database grants them.",
        "AWS Lake Formation adds exactly that to the Glue Data Catalog. An administrator writes grants such as GRANT SELECT "
        "on table sales.orders, excluding column phone, to the analyst role. When Athena, Redshift Spectrum, EMR or a Glue "
        "job asks to read the table, Lake Formation checks the grant and hands the engine short-lived credentials for just "
        "the files it needs. This is called credential vending. The engine then applies the column and row limits before "
        "showing results. The user never needs broad S3 permissions.",
        "Lake Formation also adds tags for scale. Instead of granting on hundreds of tables one by one, you attach an LF-Tag "
        "such as classification=confidential or domain=manufacturing to databases, tables or columns, and grant on the tag. "
        "A new table tagged domain=manufacturing is visible to the manufacturing group at once. Data filters add row and "
        "cell rules, for example plant_id = 'PUNE'.",
        "Lake Formation is also how AWS shares catalog tables across accounts, through AWS Resource Access Manager, and how "
        "it federates other sources such as Redshift and S3 Tables into one governed catalog. Its older data-loading "
        "features, blueprints that copy databases into the lake, still exist but are rarely the right mover today.",
    ],
    "analogy": "A bank vault's front desk: the vault holds every box, but the clerk checks your name against a list and opens only the boxes, and only the drawers, you are allowed to see.",
    "big_picture": [
        "On this site's reference platform, access is decided by Unity Catalog. Grants, row filters, column masks, tags and "
        "audit live there, Databricks enforces them on every read, and the S3 buckets are reachable only by the IAM roles "
        "Unity Catalog uses. Lake Formation is not on the main path. It sits in the band across the platform, beside the "
        "Glue Data Catalog, and matters only where Glue tables and AWS engines already exist.",
        "The typical case is a migration. An estate already protects its Glue tables with Lake Formation, and Athena reports "
        "and EMR jobs depend on those grants. While Databricks takes over, those grants keep working for the AWS readers that "
        "remain. Databricks reads the same Glue tables through Unity Catalog catalog federation, and Unity Catalog decides "
        "which Databricks users may see them. The rule from day one is that no new grants are made in Lake Formation.",
        "The danger is the middle period. For as long as both systems hold grants on overlapping data, the same person may be "
        "allowed a column in one and denied it in the other, and a change must be made twice by hand. That is why the site "
        "keeps the period short, keeps a dated list of what remains in Lake Formation, and retires each grant when its "
        "last AWS reader has moved.",
    ],
    "upstream": ["svc:glue-data-catalog", "svc:s3", "svc:iam"],
    "downstream": ["svc:athena", "svc:redshift", "svc:emr"],
    "concepts": [
        ("Data lake administrator", "A person or role allowed to grant Lake Formation permissions. Keep this list short; the default quota is 30 per catalog."),
        ("Registered location", "An S3 path you hand to Lake Formation. Once registered, engines get access to it through Lake Formation's vended credentials rather than through their own S3 permissions."),
        ("Credential vending", "Lake Formation gives an engine short-lived credentials scoped to the files of the table it may read, so users need no direct S3 access."),
        ("LF-Tags", "Key and value labels on databases, tables and columns, such as domain=manufacturing. Grants on tags apply to every resource carrying them, which scales far better than per-table grants."),
        ("Data filters", "Named rules that limit a grant to some columns, some rows (by a condition such as plant_id = 'PUNE'), or both, which gives cell-level security."),
        ("Hybrid access mode", "A setting that lets Lake Formation govern some tables or some users while others keep using plain IAM and S3 permissions. It allows a gradual start, and it means two models are live at once."),
        ("IAMAllowedPrincipals", "A special group that, when granted, tells Lake Formation to step aside and let IAM decide. Many old accounts still have it on every table, so Lake Formation is switched on in name only."),
        ("Cross-account sharing", "Granting tables to another account or organisation, carried out through AWS Resource Access Manager, so the other account sees them as resource links in its own catalog."),
    ],
    "use_when": [
        "You already protect Glue tables with Lake Formation and Athena, Redshift or EMR users depend on those grants while the platform moves to Databricks.",
        "An AWS-only part of the estate, with no Databricks, needs column, row or tag-based access on its Glue or S3 Tables data.",
        "You must share Glue catalog tables with another AWS account and want governed, revocable access rather than bucket policies.",
        "You need column masking or row limits for Athena users and cannot yet move those reports onto Databricks SQL.",
    ],
    "avoid_when": [
        "Do not add Lake Formation grants for new data on this platform. Unity Catalog grants, masks and row filters are the one access model.",
        "Do not run Lake Formation and Unity Catalog as two equal rule books for the same tables. They will drift, and the safer rule always loses somewhere.",
        "Do not use Lake Formation blueprints as your database mover. DMS, AppFlow or Lakeflow Connect fit this platform better.",
        "Do not switch it on across an old account in one step. Without hybrid mode and a plan, existing jobs lose access the moment IAMAllowedPrincipals is removed.",
    ],
    "challenges": [
        ("Two rule books",
         "A column is masked in Unity Catalog but fully visible through Athena with Lake Formation, or the other way round. Audit cannot say who could see what.",
         "Pick one owner per table. Read Glue tables from Databricks through federation, make no new Lake Formation grants, and keep a dated retirement list."),
        ("Switched on in name only",
         "IAMAllowedPrincipals is still granted on every database, so IAM decides everything and Lake Formation grants are silently ignored.",
         "List grants to IAMAllowedPrincipals, remove them table by table under hybrid access mode, and test each reader afterwards."),
        ("Surprise lockouts",
         "Registering an S3 location or removing IAM fallback breaks Glue jobs and crawlers that relied on their own S3 permissions.",
         "Use hybrid access mode, opt in one database and one set of users at a time, and grant job roles explicitly before switching."),
        ("Tag sprawl",
         "Every team invents tags, values multiply, and nobody can say what classification=internal2 means. The 1,000 tags per account quota looms.",
         "Agree a short tag vocabulary in code, review new tags, and apply them through infrastructure as code rather than the console."),
        ("Engines that do not enforce it",
         "A tool reading S3 directly, or a Spark cluster outside Lake Formation integration, skips the grants and reads every column.",
         "Keep bucket policies tight so only Lake Formation's vended credentials and named roles can read data paths, and check which engines are integrated."),
        ("Cross-account shares hard to trace",
         "Shares through Resource Access Manager create resource links in other accounts, and over time nobody knows who still uses them.",
         "Keep shares in code, tag them with an owner and an end date, and review CloudTrail for which accounts still read them."),
    ],
    "compare": [
        ("Databricks Unity Catalog",
         "Databricks is the main engine and you want grants, row filters, column masks, attribute-based policies, lineage and audit in one place.",
         "Every engine is AWS-native and there is no Databricks workspace."),
        ("Plain IAM and S3 bucket policies",
         "Access is genuinely file-level, such as a landing bucket written by one mover and read by one job.",
         "You need column or row limits, or many teams reading the same tables."),
        ("Amazon DataZone and SageMaker Unified Studio catalog",
         "You want a business catalog with request-and-approve subscriptions on top; it uses Lake Formation underneath for Glue tables.",
         "You only need grants; DataZone adds a portal and workflow, not a different enforcement layer."),
        ("Microsoft Purview and Fabric OneLake security",
         "The platform is on Azure with Fabric or Synapse engines.",
         "Your data and engines are on AWS."),
        ("Google Dataplex and BigLake",
         "The platform is on Google Cloud with BigQuery as the main engine.",
         "Your data and engines are on AWS."),
        ("Apache Ranger",
         "You run your own Hadoop, Hive or Trino clusters and want open-source policy enforcement.",
         "You want a managed service or already have Unity Catalog."),
    ],
    "cost": {
        "model": "Lake Formation permissions, tags, data filters and cross-account sharing carry no separate charge. You pay for "
                 "what it uses: the Glue Data Catalog for stored objects and requests, the engines that read data (Athena, "
                 "Redshift, EMR, Glue), AWS KMS calls for encrypted data, and S3. Its older data-loading blueprints run as "
                 "Glue jobs billed by DPU hours. Check the Lake Formation pricing page for your region, since AWS has charged "
                 "for some features, such as transaction APIs for governed tables, in the past.",
        "drivers": [
            "Glue Data Catalog requests, which rise with every engine query that checks grants and lists partitions.",
            "Engine compute in Athena, Redshift or EMR; row and cell filters add some work at query time.",
            "KMS requests when engines decrypt data through vended credentials.",
            "People time: designing tags, reviewing grants and running a migration off two access models.",
        ],
        "traps": [
            "The biggest cost is not on the bill: keeping grants in step by hand across Lake Formation and Unity Catalog during a long migration.",
            "Blueprint and crawler jobs left on a schedule keep running as Glue DPU hours long after anyone uses them.",
            "Row filters on very large tables can make Athena scan more than expected if the filter column does not match how the data is partitioned.",
        ],
    },
    "security": [
        "Lake Formation is itself a security control: grant on LF-Tags rather than single tables, keep data lake administrators to a named few, and remove IAMAllowedPrincipals where Lake Formation is meant to decide.",
        "Lock down S3 so that data paths are readable only through Lake Formation's vended credentials and the Unity Catalog roles, otherwise any engine with S3 rights skips the grants.",
        "Data stays encrypted with your KMS keys; the roles Lake Formation uses to register locations need decrypt rights on those keys, and nothing more.",
        "Reach Lake Formation, Glue and S3 through VPC endpoints so engines and Databricks clusters never call them over the internet.",
        "CloudTrail records grants, revokes and every credential Lake Formation vends, with the user and table. Keep these with Databricks audit tables so an auditor sees both sides.",
        "For personal data, mask or filter columns and rows, and keep the policy in one system. On this platform personal data is tokenised at the lander and governed in Unity Catalog.",
    ],
    "monitor": [
        ("CloudTrail GrantPermissions and RevokePermissions", "Every change to who may see what; on this platform any new grant should raise an alert, since none are planned."),
        ("CloudTrail GetDataAccess", "Each set of credentials vended to an engine, by user and table; shows which AWS readers still depend on Lake Formation."),
        ("Grants to IAMAllowedPrincipals", "Tables where Lake Formation is not really in charge; the list should shrink over time."),
        ("Access denied errors in Athena and Glue job logs", "A grant was removed too early or a reader was missed during migration."),
        ("Resource Access Manager shares", "Which accounts still receive shared tables, with an owner and end date for each."),
        ("Count of tables governed in both systems", "The overlap between Lake Formation and Unity Catalog; the migration is done when it reaches zero."),
    ],
    "limits": [
        ("LF-Tags", "1,000 per account, with up to 1,000 values per tag (adjustable)"),
        ("Registered S3 locations", "10,000 per catalog (adjustable)"),
        ("Data lake administrators", "30 per catalog (adjustable)"),
        ("LF-Tag policies", "50 per principal per resource type (adjustable)"),
        ("Registered path length", "700 characters per catalog (adjustable)"),
    ],
    "decisions": [
        ("Athena reports on Glue tables protected by Lake Formation, platform moving to Databricks",
         "Keep existing grants, read the tables from Databricks through Unity Catalog federation, add no new grants",
         "Keep if you have it: retire each grant when its last AWS reader moves."),
        ("New gold tables with masked customer columns",
         "Unity Catalog column masks and row filters, with Iceberg reads for any AWS readers",
         "Pursue: one access model, enforced by the owning catalog."),
        ("An AWS-only analytics account with no Databricks",
         "Lake Formation with LF-Tags on Glue or S3 Tables data",
         "Pursue with care: good fit there, but agree the tag vocabulary first and switch on with hybrid access mode."),
        ("Mirror every Unity Catalog grant into Lake Formation by script",
         "Two rule books kept in step automatically",
         "Drop: the script becomes the most important and least tested part of security."),
        ("Load databases into the lake with Lake Formation blueprints",
         "Blueprint-generated Glue workflows",
         "Drop: use DMS for change data capture into S3 landing, as the reference platform does."),
    ],
    "faq": [
        ("Is Lake Formation the same as the Glue Data Catalog?",
         "No. The Glue Data Catalog stores table definitions. Lake Formation adds a permission layer on top of it, with grants on databases, tables, columns and rows, and hands engines scoped credentials. They share the same tables."),
        ("Does Databricks enforce Lake Formation permissions?",
         "Not as its main model. Databricks enforces Unity Catalog grants. When Unity Catalog federates to Glue, Unity Catalog decides which Databricks users may read the foreign tables. Treat Lake Formation as the rule book for AWS engines only."),
        ("What is hybrid access mode?",
         "A setting that lets you turn on Lake Formation for chosen tables and chosen users while everything else keeps working with IAM and S3 permissions. It is the safe way to start, and also the reason two models can quietly live side by side for years."),
        ("Can Lake Formation do row and column security?",
         "Yes. Data filters limit a grant to certain columns, certain rows by a condition, or both, which gives cell-level security. Athena, Redshift Spectrum, EMR and Glue jobs honour them."),
        ("Should we remove Lake Formation once we move to Databricks?",
         "Yes, once no AWS engine reads those tables any more. Until then keep the grants, add none, and track the overlap with Unity Catalog until it reaches zero."),
    ],
    "sources": [
        ("AWS docs: What is AWS Lake Formation", "https://docs.aws.amazon.com/lake-formation/latest/dg/what-is-lake-formation.html"),
        ("AWS docs: Lake Formation endpoints and quotas", "https://docs.aws.amazon.com/general/latest/gr/lake-formation.html"),
        ("AWS docs: Lake Formation hybrid access mode", "https://docs.aws.amazon.com/lake-formation/latest/dg/hybrid-access-mode.html"),
        ("AWS docs: Lake Formation tag-based access control", "https://docs.aws.amazon.com/lake-formation/latest/dg/tag-based-access-control.html"),
    ],
    "related": [
        ("Data platform on AWS and Databricks", "/learn/data-platform-architecture/aws-databricks/"),
        ("Who maintains your tables", "/learn/table-maintenance/"),
        ("AWS Glue Data Catalog", "svc:glue-data-catalog"),
        ("Amazon DataZone", "svc:datazone"),
        ("AWS IAM and STS", "svc:iam"),
    ],
}
