"""Data platform on AWS + Databricks: /learn/data-platform-architecture/aws-databricks/.

    python3 _guides/dp_aws_databricks.py

The abstract architecture (architecture.py) with a product in every box, for a tyre manufacturer
that runs on AWS and wants Databricks. Reuses the page shell and CSS of components.py and the
22 concerns of architecture.py. Facts we are unsure of are marked "check current status".
"""
import json
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
import architecture as A  # noqa: E402  (CONCERNS, GROUP)
import components as C  # noqa: E402  (page shell, CSS, table helpers)

wb = C.wb
SITE = wb.SITE
URL = f"{SITE}/learn/data-platform-architecture/aws-databricks/"
BASE = "/learn/data-platform-architecture/"
INK = "#2b2b2b"
CHECK = "check current status"

CSS = C.CSS + """<style>
  .diagram.big svg { min-width:0; }
  .diagram.big { margin-left:-40px; margin-right:-40px; }
  @media (max-width:900px) { .diagram.big { margin-left:0; margin-right:0; } .diagram.big svg { min-width:900px; } }
  .diagram a:hover rect { stroke-width:2.6 } .diagram a { cursor:pointer }
  .answer { background:var(--butter-wash); border:var(--line); border-radius:var(--wob); padding:14px 20px; margin:18px 0; }
  .answer p { margin:6px 0; }
  .cov { display:inline-block; font-size:12px; font-weight:700; border:1.5px solid var(--ink); border-radius:999px; padding:0 9px; white-space:nowrap; }
  .cov.full { background:var(--mint-wash); } .cov.partial { background:var(--butter-wash); } .cov.none { background:var(--rose-wash); }
  .verdict { font-weight:700; white-space:nowrap; }
  .steps3 { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:14px; margin:14px 0; }
  .steps3 > div { border:var(--line); border-radius:var(--wob); padding:12px 16px; background:var(--sky-wash, #E0F1F7); }
  .steps3 h3 { font-size:23px; margin:0 0 6px; } .steps3 p { margin:6px 0; font-size:15px; }
</style>"""


# ------------------------------------------------------------------ drawing helpers
def rect(x, y, w, h, fill, dash=False, r=14, sw=1.5):
    d = ' stroke-dasharray="7 5"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{INK}" stroke-width="{sw}"{d}/>'


def tx(x, y, s, size=13.5, anchor="start", weight=None, fill=INK):
    w = f' font-weight="{weight}"' if weight else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{fill}"{w}>{E(s)}</text>'


def arr(x1, y1, x2, y2, dash=False):
    d = ' stroke-dasharray="4 3"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="1.5"{d} marker-end="url(#ahx)"/>'


def svg(w, h, body, label):
    return (f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{E(label)}">'
            '<defs><marker id="ahx" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker></defs>{body}</svg>')


def link(href, inner, title=""):
    t = f"<title>{E(title)}</title>" if title else ""
    return f'<a href="{href}">{t}{inner}</a>' if href else inner


# ------------------------------------------------------------------ 1. the big picture
SPINE = [
    ("Sources", "#F4F4F2", ["SAP S/4HANA (ERP)", "MES", "Plant historian,", "press + mixer sensors", "Quality / LIMS", "Warranty claims", "Dealer DMS, CRM", "Rubber prices, fleets"], "/concepts/cdc/"),
    ("Ingestion", "#E6F4EC", ["Common Ingestion", "Framework,", "metadata-driven", "SAP: Datasphere /", "certified extractor", "DBs: DMS, Lakeflow", "Files: Auto Loader", "Sensors: SiteWise,", "Kinesis or MSK"], BASE + "ingestion/"),
    ("S3 landing", "#FFFFFF", ["files as received", "never changed", "short retention", "KMS-encrypted", "in your bucket"], BASE + "ingestion/"),
    ("Bronze", "#F3E3D3", ["raw, append-only", "+ ingest metadata", "source schema", "replayable", "streaming tables"], BASE + "ingestion/"),
    ("Silver", "#ECEDEF", ["typed, deduped", "conformed keys", "SCD2 history", "(AUTO CDC)", "expectations", "bad rows parked", "personal data tagged"], BASE + "bronze-to-silver/"),
    ("Gold", "#FFF4D9", ["business shape", "star schema", "data products", "reads only silver", "liquid clustering"], BASE + "gold/"),
    ("Semantic", "#F8EBF1", ["Metric Views", "in Unity Catalog", "each metric once:", "OEE, scrap rate,", "first-pass yield,", "warranty rate", "no own tables"], "#aibi"),
    ("Experiences", "#E9EDF8", ["AI/BI dashboards", "Genie spaces", "Conversation UI", "(Databricks Apps)", "SQL warehouse", "for BI tools", "Vector Search +", "Model Serving", "Delta Sharing"], "#aibi"),
]

ASSETS = [
    ("CostSherlock", "cost per data product and run", "#assets"),
    ("Common Ingestion Framework", "a new source is a YAML entry", BASE + "ingestion/"),
    ("Metadata store", "one config every pipeline reads", BASE + "metadata-store/"),
    ("Data quality framework", "rules from metadata, behind a port", "#assets"),
    ("Semantic model template", "each metric defined once", "#aibi"),
    ("Conversation UI", "picks metrics, never writes SQL", "#aibi"),
    ("Shift-left checks", "catch problems before deploy", "/learn/shift-left/"),
    ("DataTwin", "a pretend plant, faults planted", "/learn/datatwin/"),
    ("Observability and run log", "one run id joins it all", "#binding"),
]

RAIL = [
    ("Lineage", ["table and column", "level, automatic"]),
    ("Access", ["grants, tags,", "ABAC (check status)"]),
    ("Masks and filters", ["rows and columns", "hidden by role"]),
    ("Personal data", ["dealers, drivers:", "tagged, masked"]),
    ("Recipe IP", ["compound recipes in", "a restricted catalog"]),
    ("Audit", ["audit system tables", "+ AWS CloudTrail"]),
    ("Residency", ["India: Mumbai, Hyd.", "EU: Frankfurt, Ireland"]),
    ("DPDP + GDPR", ["India and EU rules:", "consent, erasure"]),
    ("Owners", ["every table has", "a named owner"]),
]


def big_picture():
    b = []
    a = b.append
    W = 1180
    # agent plane
    a(link("#plan", rect(20, 16, W, 56, "#E9EDF8") + tx(40, 40, "Agent plane", 20)
           + tx(40, 61, "self-healing · onboarding drafts · rule suggester · cost advisor · docs. Agents open pull requests against the manifest; they never touch production.", 15)))
    a(arr(610, 72, 610, 84))
    # control plane
    a(link(BASE + "metadata-store/", rect(20, 84, W, 66, "#EAF6EF") + tx(40, 108, "Control plane", 20)
           + tx(40, 132, "Manifest (YAML in Git) → validator → metadata store  ·  Lakeflow Jobs run the pipelines  ·  Databricks Asset Bundles + CI/CD: dev → test → prod", 15)))
    a(arr(160, 150, 160, 192, dash=True))
    # bracket over bronze..gold
    x0 = 20 + 3 * 149
    x1 = 20 + 5 * 149 + 136
    a(f'<path d="M{x0},190 v-8 h{x1 - x0} v8" fill="none" stroke="{INK}" stroke-width="1.5"/>')
    a(tx((x0 + x1) / 2, 176, "Delta tables on S3 · Lakeflow Declarative Pipelines · governed by Unity Catalog", 15, "middle"))
    # spine
    for i, (name, fill, lines, href) in enumerate(SPINE):
        x = 20 + i * 149
        inner = rect(x, 196, 136, 250, fill) + tx(x + 68, 222, name, 19, "middle")
        inner += "".join(tx(x + 10, 251 + k * 23, ln, 15) for k, ln in enumerate(lines))
        a(link(href, inner, "Open: " + name))
        if i < len(SPINE) - 1:
            a(arr(x + 136, 321, x + 149, 321))
    # streaming lane
    a(link("#medallion", rect(20, 460, W, 40, "#fff", dash=True)
           + tx(36, 485, "Streaming lane: press and mixer sensor data through the same layers, run continuously. SiteWise, Kinesis or MSK → bronze streaming tables → silver → gold incremental. Same contracts, same checks.", 14)))
    # horizontal assets
    a(rect(20, 516, W, 200, "#FFF4D9"))
    a(tx(40, 544, "Horizontal assets: built once, reused by every pipeline and every data product", 20))
    for k, (name, sub, href) in enumerate(ASSETS):
        col, row = (k, 0) if k < 5 else (k - 5, 1)
        x, y = 36 + col * 230, 560 + row * 74
        inner = rect(x, y, 218, 62, "#fff", r=12) + tx(x + 12, y + 25, name, 17) + tx(x + 12, y + 48, sub, 14.5)
        a(link(href, inner, name))
    a(tx(36 + 4 * 230 + 109, 610 + 74, "all 22 concerns on by default", 14, "middle"))
    # foundation
    a(rect(20, 732, 582, 112, "#F1F1EF"))
    a(tx(38, 758, "AWS foundation: your account", 19))
    for k, ln in enumerate(["Customer-managed VPC · PrivateLink to Databricks", "S3 holds all data · KMS keys you own · IAM roles · CloudTrail",
                            "Regions: Mumbai for India · Frankfurt or Ireland for EU plants"]):
        a(tx(38, 784 + k * 22, ln, 15))
    a(rect(618, 732, 582, 112, "#E6EAF7"))
    a(tx(636, 758, "Databricks on AWS: runs in your account", 19))
    for k, ln in enumerate(["Workspace with serverless and classic compute · Photon", "Unity Catalog: one catalog for every table, file and model",
                            "System tables: billing, audit, lineage, job runs"]):
        a(tx(636, 784 + k * 22, ln, 15))
    # governance rail
    a(rect(1218, 16, 164, 828, "#F8E6EF"))
    a(tx(1300, 44, "Governance", 20, "middle"))
    for k, (title, sub) in enumerate(RAIL):
        y = 58 + k * 87
        a(rect(1228, y, 144, 78, "#fff", r=12) + tx(1300, y + 23, title, 15, "middle")
          + "".join(tx(1300, y + 45 + j * 18, s, 13.5, "middle") for j, s in enumerate(sub)))
    return svg(1400, 860, "".join(b), "Data platform on AWS and Databricks: agent plane and control plane on top; a spine from plant and business sources through ingestion, S3 landing, bronze, silver, gold, semantic and experiences; a streaming lane; a band of nine horizontal assets; the AWS and Databricks foundation; and a governance rail on the right.")


# ------------------------------------------------------------------ 2. medallion, two speeds
def two_speeds():
    b = []
    a = b.append
    a(rect(20, 30, 170, 56, "#F4F4F2") + tx(105, 54, "Batch sources", 16, "middle") + tx(105, 74, "SAP, MES: hourly", 12.5, "middle"))
    a(rect(20, 130, 170, 56, "#fff", dash=True) + tx(105, 154, "Event sources", 16, "middle") + tx(105, 174, "press sensors, IoT", 12.5, "middle"))
    for i, (n, f, s) in enumerate([("Bronze", "#F3E3D3", "Auto Loader"), ("Silver", "#ECEDEF", "AUTO CDC + rules"), ("Gold", "#FFF4D9", "marts, products")]):
        x = 260 + i * 200
        a(rect(x, 50, 160, 116, f) + tx(x + 80, 92, n, 20, "middle") + tx(x + 80, 120, s, 13, "middle") + tx(x + 80, 142, "one set of tables", 12, "middle", fill="#555"))
        if i < 2:
            a(arr(x + 160, 108, x + 200, 108))
    a(arr(190, 58, 260, 88) + arr(190, 158, 260, 128, dash=True))
    a(arr(820, 108, 860, 108))
    a(rect(860, 70, 150, 76, "#F8EBF1") + tx(935, 104, "Semantic", 18, "middle") + tx(935, 126, "Metric Views", 13, "middle"))
    a(tx(520, 210, "solid line: runs on a schedule · dashed line: runs continuously · same contracts and checks on both", 14, "middle"))
    return svg(1030, 222, "".join(b), "Batch and event sources both flow into the same bronze, silver and gold tables; only the speed differs.")


# ------------------------------------------------------------------ 3. AI/BI: question to answer
def aibi():
    b = []
    a = b.append
    steps = [
        ("Question", ["“Scrap rate last", "week at Plant A,", "by press?”"], "#F4F4F2"),
        ("Intent", ["model picks:", "metric, dimensions,", "filters, period"], "#E9EDF8"),
        ("Metric view", ["scrap_rate defined", "once: scrapped tyres", "over tyres cured"], "#F8EBF1"),
        ("Governed SQL", ["the engine writes it;", "Unity Catalog row", "filters apply"], "#EAF6EF"),
        ("Answer", ["numbers + chart", "+ the definition", "it used"], "#FFF4D9"),
    ]
    for i, (n, lines, f) in enumerate(steps):
        x = 20 + i * 206
        a(rect(x, 20, 180, 128, f) + tx(x + 90, 48, n, 19, "middle") + "".join(tx(x + 90, 76 + k * 21, s, 13.5, "middle") for k, s in enumerate(lines)))
        if i < 4:
            a(arr(x + 180, 84, x + 206, 84))
    a(tx(520, 192, "The model never writes SQL. It only chooses from metrics and dimensions that exist.", 15, "middle"))
    a(rect(120, 220, 800, 58, "#fff"))
    a(tx(520, 244, "Three front ends, one set of metric definitions", 17, "middle"))
    a(tx(520, 266, "AI/BI dashboards  ·  Genie spaces  ·  our Conversation UI  ·  BI tools through the SQL warehouse", 13.5, "middle"))
    return svg(1040, 290, "".join(b), "A question becomes an intent, the intent picks a metric view, the engine writes governed SQL, and the answer shows the definition it used. Dashboards, Genie and the Conversation UI all read the same metrics.")


# ------------------------------------------------------------------ tables
def table(head, rows, raw=()):
    """rows of strings; columns listed in raw are inserted as HTML."""
    h = "".join(f"<th>{E(x)}</th>" for x in head)
    body = ""
    for row in rows:
        cells = ""
        for i, c in enumerate(row):
            v = c if i in raw else E(c)
            cells += f"<td>{'<b>' + v + '</b>' if i == 0 else v}</td>"
        body += f"<tr>{cells}</tr>"
    return f'<div class="tw"><table class="t"><tr>{h}</tr>{body}</table></div>'


ASSET_ROWS = [
    ("CostSherlock", "Cost per data product, per pipeline run and per team, from Databricks billing system tables and the AWS Cost and Usage Report, with findings and fixes.", "Ours, on Databricks + AWS", "Separate briefing"),
    ('<a href="/learn/data-platform-architecture/ingestion/">Common Ingestion Framework</a>', "A new source is a YAML entry, not a new notebook. One lander from landing to bronze, with ingest metadata, replay and watermarks.", "Ours, on Databricks; movers behind a port (DMS, Lakeflow Connect, Auto Loader)", "Built; first end-to-end Databricks run in progress"),
    ('<a href="/learn/data-platform-architecture/metadata-store/">Metadata store</a>', "One place where every source, table, rule, owner and budget is declared. Pipelines read it; nobody configures by hand.", "Ours; a PostgreSQL database (Amazon RDS or Aurora)", "Built (design published, used by the framework)"),
    ("Data quality framework", "Rules declared per table, run at every hop, bad rows parked in quarantine, all results in one table.", "Databricks expectations and DQX behind one port; rules from the metadata store", "Partly built: rules from metadata run in silver; 66 assurance rules written"),
    ('<a href="/learn/medallion-architecture/">Medallion template</a>', "Bronze, silver and gold built the same way for every source, with the rules that keep each layer honest.", "Lakeflow Declarative Pipelines", "Built for the first slice"),
    ("Semantic model template", "A starter set of metric views (OEE, scrap rate, first-pass yield, warranty claim rate, sell-out) with owners and definitions.", "Unity Catalog Metric Views", "To build"),
    ("Conversation UI", "Staff ask questions in plain words and get answers that cite the metric used. The model picks metrics; it never writes SQL.", "Ours, on Databricks Apps, reading Metric Views", "Designed (spec written)"),
    ('<a href="/learn/shift-left/">Shift-left checks bundle</a>', "Checks that run on the code before it deploys: PySpark, SQL and Databricks mistakes caught in CI, not in production.", "Open source, ours; runs in CI", "Built: catches 88 of 101 planted problems, no false alarms"),
    ('<a href="/learn/datatwin/">DataTwin</a>', "A pretend tyre plant and dealer network that sends data on its own clock and breaks things on purpose, so the platform proves it catches each fault.", "Ours, open source", "Studio built; the full tool designed"),
    ("Observability and run log", "Every run gets one id that joins its quality results, lineage, cost and audit, so any number can be traced to evidence.", "System tables + CloudWatch + our run log", "Run log built; joined evidence view to build"),
]

LAYERS = [
    ("Landing (S3)", "Files exactly as received.", "Never changed. Short retention. Encrypted with your KMS key.", "S3 lifecycle rules; Unity Catalog volumes or external locations"),
    ("Bronze", "Everything that arrived, replayable.", "Append-only. Adds ingest metadata (file, time, batch id). Keeps the source schema. Safe to run twice.", "Auto Loader, streaming tables, rescued-data column"),
    ("Silver", "One clean, trusted row per real thing.", "Typed and deduplicated. Keys conformed (material, plant, press, batch, dealer). History kept as SCD Type 2. Bad rows go to quarantine, never silently dropped. Personal data and recipe columns tagged.", "AUTO CDC (formerly APPLY CHANGES) for SCD1/SCD2; expectations; column tags"),
    ("Gold", "Shaped for a business question.", "Reads only silver. Star schemas and data products with a stated grain. Rebuilt safely by partition.", "Materialized views; liquid clustering; predictive optimization"),
    ("Semantic", "Each metric defined once.", "No tables of its own. Definitions, joins and names that every tool uses.", "Unity Catalog Metric Views (" + CHECK + ")"),
]

MISTAKES = [
    ("Dashboards reading silver or bronze.", "Two numbers for the same metric. Fix: experiences read only gold through metric views; lineage is checked against the allowed paths."),
    ("A separate architecture for streaming.", "Twice the code and two answers. Fix: one medallion, two speeds: streaming tables in the same layers."),
    ("Dropping bad rows silently.", "Counts drift and nobody knows why. Fix: quarantine with a reason, and reconcile counts from source to gold."),
    ("Overwriting history in silver.", "Yesterday's report can no longer be explained. Fix: SCD Type 2 where the business needs history."),
    ("One notebook per source.", "A hundred sources become a hundred snowflakes. Fix: metadata-driven ingestion; a new source is a YAML entry."),
    ("Protecting recipes and personal data only in the dashboard.", "Anyone with SQL access sees them. Fix: tag in silver, use a restricted catalog and Unity Catalog column masks everywhere."),
]

GENIE_ROWS = [
    ("Analysts and managers asking new questions on curated tables", "Strong fit: fast to set up, curated by instructions and example questions", "Possible, but more work", "Genie", "Pursue Genie first; it is in the platform already."),
    ("Answers inside a staff app or chat channel, next to an agent", "Not designed for embedding in our own apps (" + CHECK + ")", "Built for this: an API and a chat window", "Conversation UI", "Pursue for embedded use."),
    ("A hard rule that the model never writes SQL", "Genie writes SQL, guided by trusted assets and instructions", "The model only picks metrics; the engine writes SQL", "Conversation UI", "Pursue where a wrong number is costly (finance, plant KPIs, warranty)."),
    ("Proving answers are right before go-live", "Benchmark questions built in", "Our eval harness with the same benchmark set", "Both", "Use the same benchmark questions for both."),
    ("Consumers or the public", "Not the right tool", "Only behind the agent harness, with its guardrails", "Neither directly", "Drop for now; route through the agent harness."),
]

# concern id -> (coverage, Databricks feature, AWS piece, gap and who fills it)
BIND = {
    "X1": ("partial", "Asset Bundles, Unity Catalog tags", "RDS or Aurora PostgreSQL for the metadata store", "Manifest → validator → metadata store → generators. Ours (Common Ingestion Framework)."),
    "X2": ("full", "Lakeflow Jobs: schedules, file-arrival triggers, retries", "EventBridge for events from outside", "Jobs generated from metadata, not clicked together. Ours."),
    "X3": ("partial", "Delta schema enforcement and evolution; Auto Loader rescued data", "Glue Schema Registry for streams, if used", "Contracts in the open ODCS standard, checked in CI and at run time. Ours."),
    "X4": ("partial", "Declarative Pipelines expectations; DQX (Databricks Labs)", "Glue Data Quality, if already used", "Rules from metadata, quarantine, one results table. Ours, with DQX behind a port."),
    "X5": ("partial", "Lakehouse Monitoring profiles (" + CHECK + ")", "Glue Data Quality", "Profile per run, drift alerts tied to the run id. Ours."),
    "X6": ("none", "-", "-", "Counts and sums from source to gold, per run. Ours."),
    "X7": ("full", "Unity Catalog table and column lineage", "-", "Lineage before Databricks (DMS, source systems) via OpenLineage; joined to the run id. Ours."),
    "X8": ("partial", "System tables for jobs, queries, pipeline event logs", "CloudWatch for DMS, Kinesis, MSK", "One run log with one run id across both. Ours."),
    "X9": ("partial", "Job duration alerts; freshness checks in monitoring (" + CHECK + ")", "CloudWatch alarms", "A freshness promise per table, declared in metadata and alerted. Ours."),
    "X10": ("partial", "Billing system tables, budget policies, tags", "Cost and Usage Report, Cost Explorer, Budgets", "Cost per data product and per run, with findings. CostSherlock."),
    "X11": ("full", "Unity Catalog grants, row filters, column masks, ABAC (" + CHECK + ")", "IAM roles, KMS, VPC, PrivateLink", "Grants declared in metadata and applied by the pipeline. Ours."),
    "X12": ("partial", "Column masks, tags, data classification (" + CHECK + ")", "Macie for personal data in S3; Comprehend for personal data in free text such as warranty notes", "Retention and erase-on-request across every layer. Ours."),
    "X13": ("partial", "Unity Catalog owners, comments, tags; Metric Views", "-", "Glossary and metric ownership workflow. Ours (OpenMetadata optional)."),
    "X14": ("partial", "Audit system tables", "CloudTrail", "Run log with a fingerprint of the config each run used. Ours."),
    "X15": ("partial", "Delta time travel, MERGE, full refresh of pipelines", "S3 versioning", "Backfill plans and watermark resets from metadata, never doubling a number. Ours."),
    "X16": ("full", "Asset Bundles, Git folders, Terraform provider", "CodePipeline or GitHub Actions; separate accounts per environment", "Templates only. Ours."),
    "X17": ("none", "-", "-", "Unit, contract and data tests (pytest), shift-left checks, DataTwin worlds. Ours, open source."),
    "X18": ("partial", "Time travel, deep clone, job retries", "S3 replication, AWS Backup, a second region", "A written, tested restore drill. Ours."),
    "X19": ("full", "Photon, liquid clustering, predictive optimization, serverless", "-", "Checks in CI and cost findings. Shift-left bundle + CostSherlock."),
    "X20": ("none", "-", "-", "Detect → fix in dev → pull request → verify → roll back. Ours."),
    "X21": ("partial", "Databricks Assistant for code", "Bedrock, if preferred for models", "Agents that draft manifest entries, rules and docs as pull requests. Ours."),
    "X22": ("none", "-", "-", "A pretend plant with planted faults (a press goes silent, a batch sent twice). DataTwin, ours."),
}

AWS_VS_DB = [
    ("Plant-floor data collection", "AWS IoT SiteWise, IoT Core, Greengrass", "Auto Loader / streaming tables read what SiteWise lands", "Keep SiteWise at the plant edge: it talks to the machines. Databricks takes the data from S3 or Kinesis for analytics."),
    ("Ingest from SAP", "AppFlow or a partner extractor", "SAP Business Data Cloud connector (" + CHECK + ")", "Use an SAP-certified route (Datasphere or a certified extractor) behind one port; never read SAP tables directly."),
    ("Ingest from databases (CDC)", "AWS DMS", "Lakeflow Connect", "Keep DMS where it already runs; Lakeflow Connect for new supported sources. Both sit behind one port."),
    ("Batch and streaming pipelines", "Glue jobs, EMR", "Lakeflow Declarative Pipelines and Jobs", "Pursue Databricks: one engine for batch and streaming, built-in quality rules and lineage."),
    ("Warehouse for BI", "Redshift", "Databricks SQL warehouse", "If Redshift is heavily used, keep it and read Delta from it (via Lakehouse Federation or Iceberg, " + CHECK + "); new work on Databricks SQL."),
    ("Ad hoc queries on S3", "Athena", "SQL warehouse", "Keep Athena for small one-off queries; it can read the tables as Iceberg (UniForm)."),
    ("Catalog and access", "Glue Catalog, Lake Formation", "Unity Catalog", "Pursue Unity Catalog as the one catalog: lineage, masks and audit in one place. Avoid running two access models."),
    ("ML and AI", "SageMaker, Bedrock", "Mosaic AI: Vector Search, Model Serving", "Use Databricks for ML on lakehouse data; call Bedrock models from Databricks where the company already uses Bedrock."),
    ("Dashboards", "QuickSight (now part of Amazon Quick Suite, " + CHECK + ")", "AI/BI dashboards and Genie", "Keep existing QuickSight reports; build new ones on AI/BI over the same metric views."),
    ("Cost view", "Cost Explorer, CUR", "Billing system tables", "Use both; CostSherlock joins them per data product."),
]

FAQ = [
    ("Does our data leave our AWS account?", "No. Databricks on AWS runs its compute in your account and your VPC, and all tables live in your S3 buckets, encrypted with KMS keys you own. The Databricks control plane manages the workspace; for serverless compute, check the current data-residency terms for your region."),
    ("Why Databricks if we already have Glue, EMR and Redshift?", "One engine for batch and streaming, one catalog (Unity Catalog) for access, lineage and audit, and AI/BI with Genie on the same governed data. You do not have to switch everything at once: keep what works and put new work on the lakehouse."),
    ("What is a metric view?", "A definition of a business metric (for example, scrap rate) stored once in Unity Catalog, with its formula, dimensions and filters. Dashboards, Genie and the Conversation UI all use it, so the number is the same everywhere."),
    ("What are horizontal assets?", "Parts built once and reused by every pipeline and data product: ingestion, metadata, quality, cost, testing and the conversation layer. They are what makes the tenth data product much cheaper than the first."),
    ("How are compound recipes and personal data protected?", "Recipes and formulation data sit in a restricted catalog with tag-based access; personal data of dealers, fleet drivers and consumers is tagged in silver and masked by Unity Catalog column masks and row filters for every reader, not only in dashboards. Indian data stays in Indian regions and European data in EU regions. Access is audited in system tables and CloudTrail."),
]


# ---------------------------------------------------------------- metadata store and ingestion on AWS
MD_TABLES = [
    ("platform_config", "Settings for the whole platform: default storage paths, default quality action, budget limits", "Platform team, through YAML"),
    ("source_master", "One row per source system: SAP S/4HANA, MES, historian, quality LIMS, warranty, dealer DMS", "Through YAML"),
    ("source_config", "Key-value settings per source, grouped (ingestion, quality, cost): connection secret reference, mover, schedule", "Through YAML"),
    ("dataset_master", "One row per dataset (table) of a source, with its target schema and table", "Through YAML"),
    ("dataset_config", "Key-value settings per dataset: load mode, keys, history (SCD) type, quality rules, PII tags, owner", "Through YAML"),
    ("dataset_view", "The one view every pipeline reads: platform, then source, then dataset settings merged into JSON, the most specific winning", "Generated"),
    ("run_log", "One row per run: dataset, status, row counts, cost, and a fingerprint of the exact settings used", "Pipelines"),
    ("watermark", "How far each incremental load has got", "Pipelines"),
]

GIT_VS_DB = [
    ("What it holds", "Configuration: sources, datasets, load modes, keys, rules, owners, PII tags, budgets",
     "The same configuration loaded from Git, plus runtime state: watermarks, run log, quality results"),
    ("Who writes it", "People, and agents, by pull request", "The loader writes configuration; pipelines write runtime state"),
    ("Why we need it", "Review and approval, full history, easy rollback, the same file promoted dev → test → prod",
     "Fast lookups, keys between tables, the merged view, many jobs writing at once"),
    ("Do pipelines read it?", "Never", "Always"),
]

DB_OPTIONS = [
    ("Amazon Aurora PostgreSQL Serverless v2", "Managed PostgreSQL with automatic failover, IAM sign-in, backups, and compute that scales down to almost nothing in dev. Strong JSON (jsonb) for the merged view. The same engine the agent harness uses on AWS, so one skill set.",
     "Pursue: default", "Best fit for the design as written; small, cheap, highly available."),
    ("Amazon RDS for PostgreSQL", "The same PostgreSQL on a small fixed-size server. Cheaper and simpler; slower failover and no automatic scaling.",
     "Pursue if cost matters most", "Fine for a single plant or a pilot; move to Aurora when many teams depend on it."),
    ("Databricks Lakebase (managed PostgreSQL inside Databricks)", "PostgreSQL run by Databricks, governed by Unity Catalog, reachable from serverless compute with no network setup. Generally available on AWS since early 2026 in selected regions.",
     "Test first", "Attractive because it removes the network hop; check Mumbai availability, cost and backup options before choosing."),
    ("Aurora MySQL or RDS MySQL", "Works, but JSON handling is weaker than PostgreSQL's and the view would need rewriting.", "Drop", "No gain over PostgreSQL for this design."),
    ("Amazon DynamoDB", "Key-value store with no joins, so no merged view and no keys between tables.", "Drop", "Wrong shape for relational metadata."),
    ("Delta tables in Unity Catalog only", "No keys between tables, slow small writes, write conflicts when many jobs log at once.", "Drop as the store", "Keep a copy of run_log in Delta for dashboards and cost reports."),
]

MOVERS = [
    ("SAP S/4HANA (sales, stock, procurement, finance)", "Amazon AppFlow (SAP OData), AWS DMS on the database, or an SAP-certified extractor", "Depends on the SAP licence and setup; agree the route with the SAP team first"),
    ("MES and quality / LIMS databases", "AWS DMS with change capture, or Lakeflow Connect where it has the connector", "Change capture keeps loads small"),
    ("Plant historian and press / mixer sensors", "AWS IoT SiteWise → Kinesis or S3", "The streaming lane: same layers, continuous"),
    ("Dealer management system, CRM (SaaS)", "Amazon AppFlow or Lakeflow Connect", "Whichever has a supported connector"),
    ("Supplier files, raw-material prices", "AWS Transfer Family (SFTP) → S3", "Auto Loader picks the files up"),
]

ADF_MAP = [
    ("Copy activity (databases, CDC)", "AWS DMS", "Lakeflow Connect"),
    ("Copy activity (SaaS, SAP OData)", "Amazon AppFlow", "Lakeflow Connect"),
    ("Files and SFTP", "AWS Transfer Family, DataSync", "Auto Loader"),
    ("Data flows (visual ETL)", "Glue Studio", "Notebooks, Declarative Pipelines"),
    ("Pipelines and triggers", "Step Functions, MWAA (Airflow), Glue Workflows", "Lakeflow Jobs"),
    ("Lookup + ForEach over a control table", "(build it)", "Our framework reading dataset_view"),
]


SCHEMAS = [
    ("config", "What to do: platform_config, source_master, source_config, dataset_master, dataset_config, the key registry, quality rules, PII policy, and dataset_view",
     "Only the loader writes; pipelines read", "Small; changes only through Git"),
    ("runtime", "What happened: run_log, step_log, error_log, dq_result, watermark, config_snapshot",
     "Pipelines write; nobody else", "Grows every run; monthly partitions, 13 months kept, older months copied to Delta"),
    ("audit", "Who changed what: config_load_log (every loader run, Git commit, who approved, what changed)",
     "Only the loader appends; never updated or deleted", "Small; kept for as long as audit rules require"),
]

LOG_TABLES = [
    ("run_log", "One row per run of one dataset", "run_id, dataset_id, Databricks job and run ids, status, started and ended, rows read / written / rejected, config fingerprint, Git commit, estimated cost"),
    ("step_log", "One row per step inside a run: land, bronze, silver, gold", "run_id, step, status, timings, row counts in and out"),
    ("error_log", "One row per failure", "run_id, step, error class (source down, schema change, bad data, bug), message, retry number, whether it was retried"),
    ("dq_result", "One row per quality rule checked", "run_id, rule id, passed or failed, failing row count, action taken (warn, quarantine, stop)"),
    ("config_snapshot", "The exact merged settings a run used, stored once per fingerprint", "fingerprint, merged JSON; any replay can prove what it ran with"),
]

RUNTIME_DDL = """
-- schema runtime: written only by pipelines
CREATE TABLE runtime.run_log (
  run_id          uuid PRIMARY KEY,
  dataset_id      uuid NOT NULL REFERENCES config.dataset_master(dataset_id),
  job_run_id      text,                    -- Databricks job run id, to join system tables
  status          text NOT NULL,           -- running, succeeded, failed, skipped
  started_at      timestamptz NOT NULL,
  ended_at        timestamptz,
  window_low      text,                    -- watermark this run started from
  window_high     text,                    -- watermark this run loaded up to
  rows_read       bigint, rows_written bigint, rows_rejected bigint,
  config_fp       text NOT NULL,           -- fingerprint of the merged settings
  git_commit      text,
  est_cost_usd    numeric(12,4)
);
CREATE TABLE runtime.watermark (
  dataset_id      uuid PRIMARY KEY REFERENCES config.dataset_master(dataset_id),
  wm_column       text NOT NULL,           -- e.g. updated_at, change sequence number
  wm_type         text NOT NULL,           -- timestamp, number, cdc_position, delta_token
  wm_value        text NOT NULL,           -- last value loaded successfully
  last_run_id     uuid REFERENCES runtime.run_log(run_id),
  updated_at      timestamptz NOT NULL DEFAULT now()
);"""

WM_STEPS = [
    ("Read", "Read the last good watermark (low) from runtime.watermark."),
    ("Fix the window", "Fix the upper end (high) at the start, e.g. the source's current maximum, minus a small safety gap. The run loads only rows above low and up to high, so it never chases a moving target."),
    ("Load safely", "Write to bronze with a key-based MERGE, so loading the same window twice never doubles a row."),
    ("Commit once", "Only after the data is committed: mark the run succeeded and move the watermark to high, in one database transaction."),
    ("Crash in between?", "The watermark did not move, so the next run reloads the same window, and the MERGE makes that harmless."),
    ("Late rows", "A look-back overlap (say 2 hours, set in dataset_config) re-reads a little of the last window; the MERGE drops the repeats."),
    ("Files and streams", "Auto Loader and streaming keep their own checkpoints; we record the checkpoint location, not a second watermark. CDC sources use the change position (LSN or SCN); SAP uses its delta token."),
]


# ---------------------------------------------------------------- pipeline observability, ops dashboard, alerts
def ops_flow():
    b = []
    a = b.append
    srcs = [("Our runtime schema", "run, step, error, quality, watermark"), ("Databricks system tables", "job runs, billing, lineage, audit"),
            ("Lakehouse Monitoring", "data profiles, drift (check status)"), ("Amazon CloudWatch", "DMS, AppFlow, SiteWise, Aurora")]
    for i, (t, sub) in enumerate(srcs):
        y = 20 + i * 70
        a(rect(20, y, 250, 56, "#F4F4F2") + tx(36, y + 24, t, 15) + tx(36, y + 44, sub, 12, fill="#555"))
        a(arr(270, y + 28, 340, 160))
    a(rect(340, 110, 210, 100, "#E6F4EC") + tx(445, 145, "Ops gold", 18, "middle") + tx(445, 168, "one run id joins it all", 12.5, "middle")
      + tx(445, 188, "Lakehouse Federation reads Aurora", 11.5, "middle", fill="#555"))
    outs = [("Ops dashboard", "AI/BI, one screen", "#E9EDF8"), ("Alerts", "SQL alerts, job alerts, CloudWatch", "#F8E6EF"), ("Ask about ops", "Genie: what failed last night, why?", "#FFF4D9")]
    for i, (t, sub, f) in enumerate(outs):
        y = 40 + i * 90
        a(arr(550, 160, 620, y + 28))
        a(rect(620, y, 230, 58, f) + tx(636, y + 25, t, 15) + tx(636, y + 45, sub, 12, fill="#555"))
    a(arr(850, 158, 900, 158))
    a(rect(900, 110, 150, 100, "#fff") + tx(975, 145, "On-call person", 15, "middle") + tx(975, 168, "owner from config", 12, "middle") + tx(975, 188, "+ runbook link", 12, "middle"))
    return svg(1070, 300, "".join(b), "Four sources of signals flow into one ops gold layer, which feeds the ops dashboard, the alerts and an ops Genie space; alerts go to the named owner with a runbook.")


def ops_board():
    b = []
    a = b.append
    a(rect(10, 10, 1040, 430, "#fff", r=18))
    a(tx(30, 44, "Platform ops · today", 20) + tx(1030, 44, "all plants · all data products", 12.5, "end", fill="#555"))
    tiles = [("Runs", "412", "398 ok · 9 failed · 5 running", "#E6F4EC"), ("Fresh on time", "46 / 48", "2 data products late", "#FFF4D9"),
             ("Quality", "3 rules", "failing; 1,240 rows parked", "#F8E6EF"), ("Cost today", "$186", "92% of daily budget", "#E9EDF8")]
    for i, (t, big, sub, f) in enumerate(tiles):
        x = 30 + i * 252
        a(rect(x, 64, 236, 96, f) + tx(x + 16, 88, t, 13.5, fill="#555") + tx(x + 16, 124, big, 28) + tx(x + 16, 148, sub, 12))
    a(rect(30, 178, 500, 244, "#fff") + tx(46, 202, "Freshness against target (SLO)", 14.5))
    rows = [("OEE per plant", "on time", "#BFE8CF"), ("Scrap rate", "on time", "#BFE8CF"), ("Warranty claims", "late 40 min", "#FFD98A"),
            ("Dealer sell-out", "on time", "#BFE8CF"), ("Demand plan", "late 3 h", "#F2B8CF"), ("Raw-material cost", "on time", "#BFE8CF")]
    for i, (n, st, f) in enumerate(rows):
        y = 220 + i * 32
        a(tx(46, y + 18, n, 13) + rect(330, y + 3, 180, 22, f, r=8, sw=1.2) + tx(420, y + 19, st, 12, "middle"))
    a(rect(550, 178, 480, 116, "#fff") + tx(566, 202, "Failures by cause (7 days)", 14.5))
    for i, (n, v) in enumerate([("source down", 11), ("schema changed", 6), ("bad data", 4), ("our bug", 2)]):
        y = 216 + i * 18
        a(tx(566, y + 12, n, 12) + f'<rect x="700" y="{y + 2}" width="{v * 24}" height="12" rx="4" fill="#A3B5DF" stroke="{INK}" stroke-width="1"/>' + tx(708 + v * 24, y + 12, str(v), 11.5))
    a(rect(550, 306, 480, 116, "#fff") + tx(566, 330, "Run time against its usual (p95)", 14.5))
    pts = [(570, 400), (620, 392), (670, 396), (720, 388), (770, 394), (820, 390), (870, 398), (920, 372), (970, 352), (1010, 346)]
    a('<polyline fill="none" stroke="#1F1F1F" stroke-width="1.8" points="' + " ".join(f"{x},{y}" for x, y in pts) + '"/>')
    a('<line x1="570" y1="372" x2="1010" y2="372" stroke="#C0577A" stroke-width="1.4" stroke-dasharray="6 5"/>' + tx(1010, 366, "usual p95", 11, "end", fill="#C0577A"))
    return svg(1060, 450, "".join(b), "A sketch of the ops dashboard: four tiles (runs, freshness, quality, cost), a freshness table per data product, failures by cause, and run time against its usual.")


OPS_SIGNALS = [
    ("Our runtime schema (Aurora)", "Every run, step, error, quality result and watermark, with the run id", "Read live through Lakehouse Federation, or copied to Delta every 15 minutes"),
    ("Databricks system tables", "Job and task runs, billing (DBUs and cost), lineage, audit of who read what", "Already in Unity Catalog; joined on the job run id"),
    ("Lakehouse Monitoring / data profiling", "Profiles and drift of key tables: nulls, distinct counts, distributions", "Check current status and name; behind our profiling port"),
    ("Amazon CloudWatch", "Health of AWS movers and the database: DMS lag, AppFlow failures, SiteWise ingestion, Aurora load", "CloudWatch alarms for the AWS side; a daily metrics export joins the ops gold"),
    ("Data contracts and freshness targets", "What each data product promises: by when, how complete, owner", "From dataset_config; the dashboard checks against them"),
]

OPS_PANELS = [
    ("Runs today", "Succeeded, failed, running, skipped; drill to the failing task", "System tables: job and task run timelines", "Ops / on-call"),
    ("Run time", "Duration against the usual 95th percentile; slow runs before they become late runs", "System tables: job run timeline", "Platform engineers"),
    ("Cost", "Cost per job, warehouse and cluster against budget", "System tables: billing usage × list prices (CostSherlock adds cost per data product)", "Platform lead, finance"),
    ("Compute and queries", "Busy or idle clusters, slow SQL queries, who ran what", "System tables: compute, query history, audit", "Platform engineers"),
    ("Lineage", "What feeds each table and what breaks if it fails", "System tables: table and column lineage", "Data engineers, stewards"),
    ("Failures by cause", "Source down, schema changed, bad data, our bug; trend over 7 and 30 days", "Mixed: failure state from system tables, the cause class from our error_log", "Platform lead"),
    ("Freshness against target", "Each data product green, amber or red against its promised time", "Ours: targets in dataset_config, last success in run_log", "Data product owners, business"),
    ("Quality", "Failing rules, rows parked in quarantine, by dataset and plant", "Ours: dq_result (plus pipeline expectation events)", "Data quality lead, stewards"),
    ("Volumes", "Rows in and out against the usual range; sudden drops are the early warning", "Ours: run_log", "Ops"),
    ("Watermark lag", "How far behind each incremental source is", "Ours: watermark", "Ops"),
    ("AWS movers", "DMS replication lag, AppFlow flow failures, sensor stream delay", "Amazon CloudWatch", "Ops"),
]

ALERTS = [
    ("Pipeline failed after retries", "run_log status failed and retries used up", "High", "Teams/Slack + email; pager at night for tier-1 data products"),
    ("Data product late", "Freshness past the promised time in dataset_config", "High for tier 1, Medium otherwise", "Owner of the data product, on-call"),
    ("Quality rule set to stop failed", "dq_result failed on a rule whose action is stop", "High", "Data quality lead and steward; the load is held"),
    ("Volume out of range", "Rows written outside the usual band for that dataset and weekday", "Medium", "On-call; often the first sign of a source problem"),
    ("Schema changed at source", "Contract check finds a new, missing or retyped column", "Medium", "Data engineer for that source; silver is protected by the contract"),
    ("Run much slower than usual", "Duration above 2 × the usual p95", "Low", "Platform engineers, next working day"),
    ("Cost over budget", "Daily or monthly cost per pipeline above its budget", "Medium", "Platform lead and finance (CostSherlock)"),
    ("Source mover unhealthy", "CloudWatch alarm: DMS lag, AppFlow failure, Aurora CPU or storage", "High", "On-call through Amazon SNS"),
]

ALERT_RULES = [
    ("Every alert has an owner", "The owner comes from dataset_config, not from a list someone keeps by hand."),
    ("Every alert has a runbook", "A link in the message to what to check first and how to re-run safely."),
    ("One alert per incident", "Repeats are grouped by run id and dataset, so a source outage pages once, not 40 times."),
    ("Severity follows the data product tier", "Tier 1 (for example OEE for the plant morning meeting) can page at night; tier 3 waits for morning."),
    ("Every alert is reviewed", "A noisy alert is tuned or removed within a week; an alert nobody acts on is deleted."),
]

SLOS = [
    ("Freshness", "Data product ready by its promised time", "OEE per plant by 06:30 for the morning meeting, on 99% of days"),
    ("Success", "Runs that succeed without a person stepping in", "98% of scheduled runs per week"),
    ("Quality", "Rows passing every rule", "99.5% of rows in silver; zero failures on stop rules"),
    ("Recovery", "Time from failure to data back on time", "Under 2 hours for tier-1 data products"),
]


ORCH = [
    ("Lakeflow Jobs (Databricks)", "Runs every Databricks task: lander, silver, gold, quality, refresh of metric views. Schedules, file-arrival and table-update triggers, retries, alerts, run history in system tables. Generated from metadata, deployed with Asset Bundles.",
     "Pursue: the main orchestrator", "Everything after the landing folder runs in Databricks, so the orchestrator should too; no second tool to run or pay for."),
    ("Amazon EventBridge (Scheduler and rules)", "Schedules and events on the AWS side: an S3 file arrived, a DMS task finished, a nightly start time.",
     "Pursue: for AWS-side triggers only", "Small, serverless, cheap; it starts a mover or calls the Databricks Jobs API."),
    ("AWS Step Functions", "A visual state machine over AWS services: start an AppFlow flow, wait, run a Lambda, then call a Databricks job.",
     "Use only if a mover needs several AWS steps", "Good glue for AWS services; avoid putting Databricks steps inside it."),
    ("Amazon MWAA (managed Airflow)", "Airflow as a service, for many systems beyond Databricks.",
     "Only if the company already runs Airflow", "A strong tool, but a second orchestrator to operate; Lakeflow Jobs covers our needs."),
    ("AWS Glue Workflows", "Orchestrates Glue jobs and crawlers.", "Drop", "We do not use Glue jobs for transformation."),
]


def page():
    concerns = []
    for cid, name, one, grp, _link in A.CONCERNS:
        cov, feat, aws, gap = BIND[cid]
        concerns.append((f"{cid} {name}", f'<span class="cov {cov}">{cov}</span>', feat, aws, gap))
    concern_table = table(["Concern", "Databricks covers", "Databricks feature", "AWS piece", "The gap, and who fills it"], concerns, raw=(1,))
    assets_table = table(["Asset", "What every team gets", "Built on", "Status"], ASSET_ROWS, raw=(0,))
    layers_table = table(["Layer", "Promise", "Rules", "Databricks features"], LAYERS)
    genie_table = table(["Need", "Genie", "Our Conversation UI", "Pick", "Verdict"], GENIE_ROWS)
    aws_table = table(["Job", "AWS native", "Databricks", "Verdict"], AWS_VS_DB)
    mistakes = "".join(f'<div class="rule"><b class="n">{i + 1}</b><div><b>{E(t)}</b> {E(d)}</div></div>' for i, (t, d) in enumerate(MISTAKES))
    md_table = table(["Table", "What it holds", "Written by"], MD_TABLES)
    git_table = table(["", "YAML in GitHub", "SQL metadata database"], GIT_VS_DB)
    db_table = table(["Database on AWS", "Fit", "Verdict", "Why"], DB_OPTIONS)
    mover_table = table(["Source", "Mover (first hop to S3)", "Note"], MOVERS)
    schema_table = table(["Schema", "Holds", "Who writes", "Size and retention"], SCHEMAS)
    log_table = table(["Table", "One row per", "Main columns"], LOG_TABLES)
    wm_rules = "".join(f'<div class="rule"><b class="n">{i + 1}</b><div><b>{E(t)}</b> {E(d)}</div></div>' for i, (t, d) in enumerate(WM_STEPS))
    signals_table = table(["Signal source", "What it tells us", "How it reaches the ops layer"], OPS_SIGNALS)
    panels_table = table(["Panel", "What it shows", "Built from", "Who looks"], OPS_PANELS)
    alerts_table = table(["Alert", "Fires when", "Severity", "Goes to"], ALERTS)
    alert_rules = "".join(f'<div class="rule"><b class="n">{i + 1}</b><div><b>{E(t)}</b> {E(d)}</div></div>' for i, (t, d) in enumerate(ALERT_RULES))
    slo_table = table(["Target (SLO)", "Measures", "Example"], SLOS)
    orch_table = table(["Service", "What it does here", "Verdict", "Why"], ORCH)
    adf_table = table(["Azure Data Factory part", "On AWS", "On Databricks"], ADF_MAP)
    faq = C.faq(FAQ)

    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › <a href="{BASE}">Data platform architecture</a> › On AWS + Databricks</p>
<p class="eyebrow" style="margin-top:22px">Data platform architecture · binding · AWS + Databricks</p>
<h1>The data platform on AWS and Databricks</h1>
<p class="lede">The same architecture as <a href="{BASE}">the abstract picture</a>, with a product in every box, for a tyre manufacturer that already runs on AWS and wants Databricks. The design stays the same; only the names change.</p>
<div class="sib"><a href="{BASE}">↑ The abstract picture</a><a href="/leaders/spec-driven/data-platform/">Spec-driven development for data</a><a href="/learn/medallion-architecture/">Medallion, drawn right</a></div>
<nav class="toc"><b>On this page</b><ol>
<li><a href="#minute">The one-minute version</a></li><li><a href="#picture">The big picture</a></li><li><a href="#assets">Horizontal assets</a></li><li><a href="#metadata">Metadata and ingestion</a></li><li><a href="#ops">Observability and alerts</a></li>
<li><a href="#medallion">The right medallion</a></li><li><a href="#aibi">The right AI/BI</a></li><li><a href="#binding">22 concerns, bound</a></li>
<li><a href="#aws">AWS native or Databricks</a></li><li><a href="#plan">How we would start</a></li><li><a href="#faq">Questions</a></li></ol></nav>

<section id="minute"><p class="eyebrow">The one-minute version</p><h2>Your account, your data, one catalog</h2>
<div class="answer">
<p><b>Databricks runs inside your own AWS account.</b> Data stays in your S3 buckets, in your VPC, encrypted with KMS keys you own. Databricks brings the engine, and <b>Unity Catalog</b> (its one catalog for tables, files and models) governs who sees what, tracks lineage and records every access.</p>
<p><b>The design does not depend on Databricks.</b> It follows the same specs and the same 22 cross-cutting concerns as the abstract architecture. This page is the <em>binding</em>: the one place where product names appear. That is what keeps you free to change a product later.</p>
<p><b>Most of the value is in the shared parts.</b> Ingestion, metadata, quality, cost, testing and the conversation layer are built once and reused, so each new data product (OEE, warranty claim rate, dealer sell-out, demand forecast) costs less than the one before.</p>
</div></section>

<section id="picture"><p class="eyebrow">The big picture</p><h2>One platform, from plant and business systems to answers</h2>
<p>Read it left to right along the middle row: data moves one way, from the plants' and the business's systems to dashboards, Genie and AI. Above it, the control plane decides what runs, and agents may only suggest. Below it, the horizontal assets serve every layer, on an AWS and Databricks foundation you own. Governance runs down the right side.</p>
<figure class="diagram big" style="padding:10px">{big_picture()}<figcaption>The data platform on AWS + Databricks. Click a layer or an asset to open its page.</figcaption></figure></section>

<section id="assets"><p class="eyebrow">Horizontal assets</p><h2>Built once, used by every data product</h2>
<p>A horizontal asset is something every pipeline needs, whatever the subject. Databricks gives the plumbing; these assets are the parts that make the platform trustworthy and cheap to grow. The status column is honest: some are built, some are designed, some are still to build.</p>
{assets_table}</section>

<section id="metadata"><p class="eyebrow">Metadata and ingestion on AWS</p><h2>One metadata database, one ingestion framework</h2>
<p>The Common Ingestion Framework is <b>metadata-driven</b>: adding a source is a few lines of YAML, not a new pipeline. It follows the <a href="https://medium.com/@basant.choudhary09/metadata-db-design-for-data-engineering-components-ingestion-processing-data-quality-data-6b355ad5ecb9">Metadata DB Design for Data Engineering Platforms</a>, already built in our framework. Full table definitions, the view and the reader code are on <a href="{BASE}metadata-store/">the metadata store page</a>.</p>
<h3>The tables</h3>
{md_table}
<p class="note">The framework also has a key registry (every allowed setting and its type), per-column settings, quality results and a PII policy table on the same database.</p>

<h3>YAML in GitHub, and a SQL database</h3>
<p>We need both, for different jobs. People write and approve settings as YAML in GitHub; a loader validates every key and writes them to the database, one database per environment (dev, test, prod) with the same schema. Pipelines only ever read the database.</p>
{git_table}
<p><b>Two rules.</b> Nobody edits configuration in the database by hand: the next load would overwrite it and Git would have no record. Runtime state (watermarks, run log) never goes into Git.</p>

<h3>Which database on AWS</h3>
<p>The metadata store needs keys between tables, fast small reads and writes, safe parallel writes from many jobs, and good JSON for the merged view. That is a relational database, and PostgreSQL fits the design as written.</p>
{db_table}
<p><b>Where it sits:</b> in your AWS account, in a private subnet, in the same region as the Databricks workspace (Mumbai for India; Frankfurt or Ireland if EU data needs its own platform). The password lives in AWS Secrets Manager; Databricks classic compute reaches it over the VPC, and serverless compute through a private endpoint. A copy of <code>run_log</code> lands in Delta every day so dashboards and cost reports can join it.</p>

<h3>Three schemas in one database</h3>
<p>One PostgreSQL database per environment, split into three schemas so that permissions are simple: the loader may write only <code>config</code> and <code>audit</code>, pipelines may write only <code>runtime</code>, and dashboards read everything.</p>
{schema_table}

<h3>Logging: every run can be followed and replayed</h3>
<p>Every run writes to the runtime schema. One run id ties the rows together, and it is also stored on the Databricks job run, so the logs join with Databricks system tables (cost, lineage, audit) and with the quality results.</p>
{log_table}

<h3>The watermark: load only what is new, safely</h3>
<p>A watermark is a bookmark: the last value loaded from a source (a timestamp, an id, a change position). The next run starts after it. The danger is moving the bookmark before the data is safely written, or never moving it after a crash. These rules prevent both.</p>
<div class="rules">{wm_rules}</div>
{C.code(RUNTIME_DDL, "The two runtime tables most people ask about first. The full config schema is on the metadata store page.")}

<h3>Ingestion: movers bring data in, our lander loads it</h3>
<p>Ingestion has two steps. A <b>mover</b> brings raw data from the source into an S3 landing folder; which mover is a setting in <code>source_config</code>, so it can change without code. Then <b>one lander</b>, our PySpark job on Databricks using Auto Loader, reads its settings from <code>dataset_view</code>, writes bronze with arrival details, records a <code>run_log</code> row and is safe to run twice. Lakeflow Jobs are generated from the metadata and deployed with Databricks Asset Bundles.</p>
{mover_table}

<h3>Orchestration: which service runs what, and when</h3>
<p>One rule: <b>one orchestrator owns each pipeline</b>. Lakeflow Jobs owns everything from the landing folder onwards; AWS services only start the movers on the AWS side and hand over. Two schedulers for the same pipeline is the most common cause of runs that overlap or never start.</p>
{orch_table}

<p><b>Is there an Azure Data Factory on AWS?</b> Not as one tool; its parts are spread across services. We use them only as movers. The framework itself is Python, so it is tested, reviewed and portable, instead of hundreds of hand-built visual pipelines.</p>
{adf_table}
</section>

<section id="ops"><p class="eyebrow">Pipeline observability</p><h2>The ops dashboard and alerts</h2>
<p>Observability means that when a number looks wrong or a dashboard is late, anyone can see within a minute <b>what ran, what failed, why, and what it cost</b>, without opening a notebook. It is built once as a horizontal asset and switched on for every pipeline from the metadata.</p>
<figure class="diagram">{ops_flow()}<figcaption>Four sources of signals, one ops layer joined on the run id, three ways out: a dashboard, alerts and questions in plain words.</figcaption></figure>

<h3>Where the signals come from</h3>
{signals_table}

<h3>The ops dashboard</h3>
<p>One AI/BI dashboard on the ops gold tables, for everyone from the on-call engineer to the plant's data product owner. Numbers in the sketch are made up.</p>
<figure class="diagram">{ops_board()}<figcaption>Sketch of the ops dashboard. Every tile drills down to the run, the step and the error.</figcaption></figure>
<p><b>Start with what Databricks already gives.</b> The first five panels come straight from Databricks <b>system tables</b> (read-only tables in Unity Catalog that record jobs, billing, compute, queries, lineage and audit), with no code of ours. Databricks also ships ready-made usage and job-monitoring dashboards to import and adapt (check current status). We add only what system tables cannot know: the business meaning (which data product, which plant, which target), quality results, row counts, watermarks and the cause of a failure. The job run id stored in our run_log is the join key.</p>
{panels_table}

<h3>Targets first, then alerts</h3>
<p>An alert only makes sense against a promise. Each data product states its targets in the metadata; the dashboard shows them and the alerts fire when they are missed.</p>
{slo_table}

<h3>Alerts</h3>
<p>Databricks SQL alerts and job notifications cover what happens inside Databricks; CloudWatch alarms with Amazon SNS cover the AWS movers and the database. All of them post to the same Teams or Slack channel and, for tier-1 data products, to the on-call pager.</p>
{alerts_table}
<div class="rules">{alert_rules}</div>
<p><b>Later, self-healing:</b> for known causes (a source briefly down, a late file) an agent may propose the fix and re-run in dev; a person approves before anything touches production.</p>
</section>

<section id="medallion"><p class="eyebrow">The right medallion</p><h2>One medallion, two speeds</h2>
<p>The medallion is the row of layers in the middle: bronze (raw), silver (clean) and gold (shaped for the business). Streaming does not need a second architecture. Nightly batches and continuous events flow through <b>the same tables</b>, with the same contracts and the same checks; only the speed differs.</p>
<figure class="diagram">{two_speeds()}<figcaption>Batch and streaming share one set of layers.</figcaption></figure>
<h3>What each layer promises</h3>
{layers_table}
<h3>Common mistakes, and the fix</h3>{mistakes}
<p>More detail, with one record followed through every layer: <a href="/learn/medallion-architecture/">Medallion architecture, drawn right</a>.</p></section>

<section id="aibi"><p class="eyebrow">The right AI/BI</p><h2>The semantic layer first, then the AI</h2>
<p>Ask three tools for "scrap rate" and you can get three numbers. The fix is to define each metric <b>once</b>, as a metric view in Unity Catalog, and make every front end read it. Then AI on top is safe: the model only chooses which metric, which breakdown and which filter; the engine writes the SQL, and Unity Catalog's row and column rules apply to whoever is asking.</p>
<figure class="diagram">{aibi()}<figcaption>From a question to an answer that shows its own definition.</figcaption></figure>
<ul>
<li><b>Genie spaces</b> are curated: a short list of trusted tables or metric views, written instructions, and example questions with their correct answers.</li>
<li><b>Benchmark questions</b> are run before go-live and after every change, so we know the answers are still right.</li>
<li><b>Security flows through:</b> a plant manager in one plant sees only that plant's rows, in a dashboard, in Genie and in the Conversation UI alike.</li>
</ul>
<h3>Genie or our Conversation UI?</h3>
{genie_table}</section>

<section id="binding"><p class="eyebrow">22 concerns, bound</p><h2>What Databricks gives, what AWS gives, what we add</h2>
<p>For each of the 22 cross-cutting concerns: reuse what Databricks does well, use AWS where the job sits outside Databricks, and fill only the gap. Every concern is switched on and configured from the metadata store, and every product sits behind a port (a fixed interface), so a product can be swapped without touching the pipelines.</p>
<p><b>Our main value is joining the dots:</b> one run id links the quality results, lineage, run log, cost and audit for every number, even where every piece underneath is Databricks or AWS.</p>
{concern_table}
<p class="note">Coverage is our judgement for a typical setup. Product names and preview status change often; items marked "{CHECK}" should be confirmed before the deck goes out.</p></section>

<section id="aws"><p class="eyebrow">AWS native or Databricks</p><h2>Which product for which job</h2>
<p>You do not have to replace what already works. This is our recommendation per job, with the reason.</p>
{aws_table}</section>

<section id="plan"><p class="eyebrow">How we would start</p><h2>One thin slice first</h2>
<div class="steps3">
<div><h3>Crawl · 4 to 6 weeks</h3><p>One slice end to end in your AWS account: curing-press sensor data and MES production records to silver, one metric view (OEE or scrap rate), one Genie space for plant managers with benchmark questions.</p><p><b>You see:</b> the whole path working, with quality, lineage and cost on from day one.</p></div>
<div><h3>Walk · next quarter</h3><p>Three to five more sources (SAP sales and stock, quality lab, warranty claims, dealer sell-out). The horizontal assets on by default. CostSherlock reporting cost per data product.</p><p><b>You see:</b> each new source added as a YAML entry, not a project.</p></div>
<div><h3>Run · after that</h3><p>A small platform team owns the assets; domain teams build data products on them. The Conversation UI in staff apps. Agents propose fixes as pull requests.</p><p><b>You see:</b> the tenth data product faster and safer than the first.</p></div>
</div></section>

<section id="faq"><p class="eyebrow">Questions</p><h2>Questions leaders ask</h2>{faq}</section>

<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2>
<p><a href="{BASE}">↑ The abstract architecture</a> · <a href="/leaders/spec-driven/data-platform/">Spec-driven development for data platforms</a> · <a href="/learn/medallion-architecture/">Medallion layers</a> · <a href="/learn/shift-left/">Shift-left checks</a> · <a href="/learn/datatwin/">DataTwin</a></p></section>"""

    desc = "A data platform on AWS and Databricks for a tyre manufacturer: the big picture, horizontal assets, the right medallion and AI/BI, and 22 concerns bound to products."
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": "The data platform on AWS and Databricks", "description": desc, "url": URL,
           "inLanguage": "en", "isAccessibleForFree": True, "dateModified": "2026-11-02",
           "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Learn", "item": f"{SITE}/learn/"},
              {"@type": "ListItem", "position": 2, "name": "Data platform architecture", "item": f"{SITE}{BASE}"},
              {"@type": "ListItem", "position": 3, "name": "On AWS + Databricks", "item": URL}]}]
    head = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page("The data platform on AWS and Databricks", desc, URL, body, head)


def main():
    out = ROOT / "learn" / "data-platform-architecture" / "aws-databricks"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("aws + databricks guide ->", out)


if __name__ == "__main__":
    main()
