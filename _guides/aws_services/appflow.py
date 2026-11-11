SERVICE = {
    "slug": "appflow",
    "name": "Amazon AppFlow",
    "short": "AppFlow",
    "group": "ingestion",
    "one_line": "A managed, no-code copier that pulls records from SaaS apps and SAP OData services into S3 on a schedule or on an event.",
    "status": "Generally available. Not on the AWS maintenance or sunset lists as of 2026-11-11.",
    "checked": "2026-11-11",
    "site_verdict": ("Pursue",
                     "The reference platform's mover for SaaS apps and for SAP through OData on released CDS views and extractors with delta. "
                     "It lands files in S3 landing so every source passes the same lander. Where AppFlow has no connector, our own REST puller "
                     "fills the gap; SAP tables are never read directly."),
    "equivalents": {"azure": "Data Factory copy activity with SaaS and SAP connectors",
                    "gcp": "Application Integration connectors, or Cloud Data Fusion",
                    "databricks": "Lakeflow Connect (managed SaaS connectors such as Salesforce and ServiceNow)",
                    "open_source": "Airbyte or dlt"},
    "plain": [
        "Amazon AppFlow copies records out of software-as-a-service applications and into AWS. A software-as-a-service (SaaS) application is "
        "a business system you rent over the internet, such as Salesforce for sales, ServiceNow for tickets or Zendesk for support. Each of "
        "these keeps your data behind its own web API, with its own login, paging rules and daily call limits. AppFlow already knows how to talk "
        "to dozens of them. You pick a source, pick a destination such as an S3 bucket, map the fields and choose when to run. AppFlow then "
        "does the calls, the paging and the retries for you, and writes the result as CSV, JSON or Parquet files.",
        "AppFlow also has an SAP OData connector. OData is a standard way of exposing business objects over HTTP, and SAP uses it to publish "
        "services on top of its ERP system. The important detail is that AppFlow can read from SAP's Operational Data Provisioning framework, "
        "usually shortened to ODP. ODP keeps a delta queue for each subscribed extractor or CDS view, so after the first full load AppFlow "
        "fetches only the records that changed since the previous run. A CDS view (Core Data Services view) is SAP's own released, documented "
        "view over its tables, which is the supported way to read SAP data.",
        "A concrete example: a tyre maker runs SAP S/4HANA for sales orders and stock, and a SaaS dealer management system for its dealer "
        "network. One AppFlow flow reads the sales-order CDS view through ODP every 15 minutes and writes the changed orders as Parquet files "
        "into the landing bucket. A second flow pulls new dealer accounts and service visits from the SaaS system every hour. The lakehouse "
        "never logs into either system; it only reads the files AppFlow left in S3.",
    ],
    "analogy": "A courier with a key to each supplier's office, who collects only the new paperwork on a timetable and drops it in your mailroom.",
    "big_picture": [
        "On the reference platform AppFlow sits in the Move in lane, between the business applications and the S3 landing zone. It is one of "
        "several movers behind a single port of the Common Ingestion Framework: DMS for databases, Transfer Family for supplier SFTP, IoT "
        "services and Kinesis for plants, and AppFlow for SaaS and SAP OData. A port here means one agreed interface; each mover writes files "
        "into landing in the same layout, and the lander moves them into bronze with ingest metadata, a run id and replay.",
        "What feeds it is SAP S/4HANA through released CDS views and extractors with delta, plus SaaS systems such as the dealer management "
        "system and the CRM. What reads its output is Databricks Auto Loader, on a scheduled Lakeflow Job, which picks up the new files and "
        "appends them to bronze tables. From there the usual medallion steps build silver and gold.",
        "Why it is there rather than something inside Databricks: in v1 the site keeps every source passing through S3 landing, so tokenising, "
        "file logs and the run log work the same way for every source. Lakeflow Connect writes straight into tables and is not used in v1. "
        "For SAP the rule is stronger: use an SAP-certified route behind one port, never read SAP tables directly, and only consider "
        "Datasphere or Business Data Cloud if they are already licensed.",
    ],
    "upstream": ["SAP S/4HANA OData and ODP services", "SaaS apps such as CRM and dealer systems", "svc:eventbridge"],
    "downstream": ["svc:s3", "Databricks Auto Loader into bronze", "svc:redshift"],
    "concepts": [
        ("Flow", "One configured copy job: a source object, a destination, field mappings, filters and a trigger. The unit you create, run and pay for."),
        ("Connector and connection", "A connector is AppFlow's built-in adapter for one application. A connection (connector profile) holds the address and credentials for one instance of that application."),
        ("Trigger", "What starts a flow: on demand, on a schedule as often as once a minute, or on an event the source emits, such as a Salesforce change event."),
        ("Incremental transfer", "A scheduled mode that copies only records changed since the last run, using a timestamp field or, for SAP ODP, a delta token."),
        ("ODP provider", "An SAP object that supports Operational Data Provisioning, such as a DataSource extractor, an ABAP CDS view or a BW object. It keeps a delta queue that AppFlow subscribes to."),
        ("Operational delta queue", "SAP's list of changes per subscriber. AppFlow creates the subscription but does not administer it; deleting the flow leaves the subscription in SAP."),
        ("Custom connector", "Your own connector, written with the AppFlow Custom Connector SDK in Python or Java and run as a Lambda function, for an application AppFlow does not ship."),
        ("Private connection", "A connection that reaches the source through AWS PrivateLink instead of the public internet, used for SAP behind a VPC endpoint service and for some SaaS apps."),
    ],
    "use_when": [
        "You need data from a SaaS application that AppFlow already supports and want no code and no servers to run.",
        "You read SAP S/4HANA or ECC through released OData services or ODP extractors and want delta loads into S3.",
        "Your platform lands every source as files in S3 first, so one lander and one run log treat all sources alike.",
        "Volumes per run are moderate, from thousands to a few million records, and minutes of delay are fine.",
        "You want the credentials and the API paging handled by a managed service, with encryption under your own KMS key.",
    ],
    "avoid_when": [
        "The application has no AppFlow connector and you would have to build and run a custom Lambda connector; a small REST puller of your own is often simpler.",
        "You need sub-second or seconds-level delivery; AppFlow runs in batches, at most once a minute on a schedule.",
        "The source is a database you can reach directly; use change data capture with DMS instead of an application API.",
        "The plan is to read raw SAP tables; that is unsupported by SAP licensing and fragile, so use released CDS views or a certified extractor.",
        "Very large historic loads would exceed the per-run caps or the source's daily API quota; split the history or use a bulk export.",
    ],
    "challenges": [
        ("API quota exhaustion", "Every flow run spends the source application's API calls, so frequent schedules on many objects can use up the daily allowance and block the business's own integrations.",
         "Agree a call budget with the application owner, prefer incremental transfers, run less often for slow-changing objects and alarm on API errors."),
        ("Stolen ODP subscription", "A new incremental flow on the same SAP ODP object removes the earlier subscription, so the old flow silently stops getting deltas.",
         "Keep exactly one scheduled flow per ODP object, record it in the source YAML and review subscriptions in SAP when flows change."),
        ("Orphaned delta queues", "Deleting a flow does not delete its ODP subscription, so SAP keeps collecting changes for a reader that will never come.",
         "Add a decommission step that removes the subscription in SAP, and check the delta queue monitor in SAP regularly."),
        ("Silent schema drift", "A SaaS vendor adds or renames fields, and the field mapping in the flow either drops the new field or fails.",
         "Map all fields or use passthrough where possible, keep the raw payload in bronze and run schema checks in the lander."),
        ("Full loads that cannot run often", "For SAP ODP, full transfers on a schedule can run no more often than daily, which surprises teams that expect hourly refreshes.",
         "Use incremental transfer for frequent runs and keep full loads for the first load and for repair."),
        ("Event buffer overflow", "Salesforce change events go through a fixed 10 MB buffer per channel; a burst of changes can be dropped.",
         "Size the burst, ask AWS Support for a larger buffer, and pair event flows with a scheduled incremental flow as a safety net."),
        ("Credential and token expiry", "OAuth refresh tokens or SAP passwords expire or are rotated, and flows fail until someone reconnects.",
         "Alarm on failed runs, document who owns each connection and rotate credentials on a known calendar."),
        ("Slow single-threaded SAP pulls", "Large OData objects page through 3,000 records at a time on one thread and take hours.",
         "Set concurrent processes, up to 10 for plain OData, and filter by date ranges; remember that ODP objects do not support concurrency."),
    ],
    "compare": [
        ("Lakeflow Connect (Databricks)", "You want managed SaaS and database connectors that write straight into Unity Catalog tables with no landing files.",
         "You need every source to pass through S3 landing and one lander, as the reference platform does in v1."),
        ("Our REST puller", "AppFlow has no connector for the application, or you need fine control over paging, rate limits and payloads.",
         "AppFlow already supports the application; then you are writing and running code for no gain."),
        ("AWS Glue connectors and Glue zero-ETL for SaaS", "You already run Glue jobs and want SaaS sources inside them, or a managed copy into Redshift or SageMaker lakehouse tables.",
         "Databricks does the processing and you only need files in S3."),
        ("Azure Data Factory copy activity", "The platform is on Azure; Data Factory has SaaS and SAP connectors and runs copies on a self-hosted or managed runtime.",
         "You are on AWS; running Data Factory across clouds adds egress and a second control plane."),
        ("SAP Datasphere or Business Data Cloud", "You already license them and want SAP-managed replication with business semantics kept.",
         "You only need a few CDS views into the lake; the licence cost is hard to justify for that alone."),
        ("Airbyte or dlt", "You want open-source connectors you can run anywhere and change yourself.",
         "You do not want to run and patch the connector runtime and its upgrades."),
    ],
    "cost": {
        "model": "AppFlow charges per flow run and per gigabyte of data processed. Every successful run counts, including a scheduled run that finds nothing new, "
                 "and for SAP each extra concurrent process counts as an additional run. AWS's pricing examples use $0.001 per flow run and $0.02 per GB "
                 "processed (list price, check your region). You also pay the normal S3 request and storage charges and KMS charges for your key.",
        "drivers": [
            "How often each flow runs, multiplied by the number of flows; a once-a-minute schedule is about 43,000 runs a month per flow.",
            "Gigabytes processed per run, which is small for deltas and large for full loads.",
            "Concurrent processes on SAP OData flows, each billed as an extra run.",
            "Downstream S3 PUT requests when flows write many small files.",
        ],
        "traps": [
            "Empty scheduled runs still cost a run; per-minute schedules on dozens of quiet objects add up for no data.",
            "The real cost is often on the source side: SaaS API call allowances and SAP gateway load, not the AWS bill.",
            "Many tiny files in landing make the downstream read slower and costlier; group objects and choose a sensible schedule.",
            "Rerunning full loads to repair gaps processes the whole object again; keep incremental state healthy instead.",
        ],
    },
    "security": [
        "Give AppFlow a destination bucket policy that allows only the AppFlow service principal with aws:SourceAccount and aws:SourceArn conditions, so no other account can write there.",
        "Encrypt connection credentials and data with a customer-managed KMS key; the reference design uses one key per catalog bucket.",
        "Use private connections: SAP through a VPC endpoint service shared with appflow.amazonaws.com, and PrivateLink for SaaS apps that support it, so no public IP is needed.",
        "For SAP use a technical user with read access only to the released services it needs; never a dialog user with broad table access.",
        "Audit flow creation, changes and runs through CloudTrail, and keep connection owners in the source YAML.",
        "SaaS and SAP extracts often carry customer names, emails and phone numbers; Macie scans the landing bucket and the lander tokenises personal fields before bronze.",
    ],
    "monitor": [
        ("FlowExecutionsFailed", "CloudWatch count of failed runs per flow; the main alarm for the on-call mover health view."),
        ("FlowExecutionsSucceeded and FlowExecutionsStarted", "Show whether scheduled flows are running at all; a flow that stops starting is as bad as one that fails."),
        ("FlowExecutionTime", "How long runs take; a steady rise points at source throttling or growing deltas."),
        ("FlowExecutionRecordsProcessed", "Records moved per run; a sudden zero on a busy object usually means a lost ODP subscription or a broken filter."),
        ("AppFlow End Flow Run Report events", "EventBridge events emitted when a run ends, used to trigger the lander or Databricks job and to log run ids."),
        ("Source API error rates", "Rate-limit and authentication errors in the run details; they warn of quota exhaustion and expiring tokens."),
    ],
    "limits": [
        ("Flows per account", "1,000 per Region (default)"),
        ("Concurrent flow runs", "1,000 at any time per account"),
        ("Flow runs per month", "10 million per account"),
        ("Maximum run time", "48 hours per flow run"),
        ("Schedule frequency", "At most once a minute; some sources such as Marketo hourly or Google Analytics daily"),
        ("SAP OData page size", "3,000 records for OData, 10,000 for ODP; up to 10 concurrent processes for plain OData only"),
    ],
    "decisions": [
        ("SAP S/4HANA sales orders and stock, every 15 minutes", "AppFlow SAP OData on released CDS views through ODP, incremental, over a private connection",
         "Pursue: delta tokens keep loads small, SAP stays supported, and files land in S3 like every other source."),
        ("Dealer management SaaS with an AppFlow connector", "AppFlow scheduled incremental flow into S3 landing",
         "Pursue: no code to run, credentials managed, and the lander treats it like any other file source."),
        ("A niche SaaS with a REST API and no connector", "Our REST puller instead of an AppFlow custom connector",
         "Pursue with care: a small puller behind the same port is simpler than a Lambda connector, but someone owns its code."),
        ("Reading SAP tables directly for speed", "Replicate raw tables through a generic tool",
         "Drop: unsupported, licence-risky and fragile; use released CDS views or a certified extractor."),
        ("Moving to Lakeflow Connect later", "Revisit per source once v1 is stable",
         "Keep if you have it: AppFlow stays until a source gains clear value from writing straight into tables."),
    ],
    "faq": [
        ("Is Amazon AppFlow being retired?", "No. As of 11 November 2026 AppFlow is not on the AWS lists of services in maintenance or sunset. It still receives connector updates, but always check the AWS lifecycle page before a long project."),
        ("Can AppFlow do change data capture from SAP?", "Yes, for ODP providers such as extractors and CDS views. The flow subscribes to SAP's operational delta queue and, after one full load, copies only changed records. For plain OData objects it uses a timestamp field you choose."),
        ("How fast can AppFlow run?", "A scheduled flow can run at most once a minute, and some sources allow only hourly or daily runs. Event-triggered flows from Salesforce are faster but still batch-like. For seconds-level data use a stream such as Kinesis."),
        ("AppFlow or Lakeflow Connect for a Databricks lakehouse?", "Lakeflow Connect writes straight into Unity Catalog tables and is simpler if that is all you need. The reference platform uses AppFlow in v1 because every source lands as files in S3 first, so one lander handles tokenising, run logs and replay."),
        ("Does AppFlow need public internet access to SAP?", "No. You can expose SAP through a VPC endpoint service and let AppFlow connect over PrivateLink. With OAuth, the authorization page must still be reachable from the network where you set up the connection."),
    ],
    "sources": [
        ("AWS docs: SAP OData connector for Amazon AppFlow", "https://docs.aws.amazon.com/appflow/latest/userguide/sapodata.html"),
        ("AWS docs: Quotas for Amazon AppFlow", "https://docs.aws.amazon.com/appflow/latest/userguide/service-quotas.html"),
        ("AWS: Amazon AppFlow pricing", "https://aws.amazon.com/appflow/pricing/"),
        ("AWS docs: AWS lifecycle changes", "https://docs.aws.amazon.com/general/latest/gr/service-lifecycle.html"),
        ("AWS: Service availability updates, June 2026", "https://aws.amazon.com/about-aws/whats-new/2026/06/aws-service-availability/"),
    ],
    "related": [
        ("Common Ingestion Framework", "/learn/data-platform-architecture/ingestion/"),
        ("Data platform on AWS and Databricks", "/learn/data-platform-architecture/aws-databricks/"),
        ("Medallion architecture", "/learn/medallion-architecture/"),
        ("AWS Database Migration Service", "svc:dms"),
        ("AWS Transfer Family", "svc:transfer-family"),
        ("Amazon S3", "svc:s3"),
    ],
}
