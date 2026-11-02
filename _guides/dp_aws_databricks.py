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
    faq = C.faq(FAQ)

    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › <a href="{BASE}">Data platform architecture</a> › On AWS + Databricks</p>
<p class="eyebrow" style="margin-top:22px">Data platform architecture · binding · AWS + Databricks</p>
<h1>The data platform on AWS and Databricks</h1>
<p class="lede">The same architecture as <a href="{BASE}">the abstract picture</a>, with a product in every box, for a tyre manufacturer that already runs on AWS and wants Databricks. The design stays the same; only the names change.</p>
<div class="sib"><a href="{BASE}">↑ The abstract picture</a><a href="/leaders/spec-driven/data-platform/">Spec-driven development for data</a><a href="/learn/medallion-architecture/">Medallion, drawn right</a></div>
<nav class="toc"><b>On this page</b><ol>
<li><a href="#minute">The one-minute version</a></li><li><a href="#picture">The big picture</a></li><li><a href="#assets">Horizontal assets</a></li>
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
