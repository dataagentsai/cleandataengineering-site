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
    ("Residency", ["India: Mumbai + Hyd.", "EU only if legal asks"]),
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
           + tx(40, 132, "YAML in Git → loader → metadata store  ·  Lakeflow Jobs run the pipelines  ·  Databricks Asset Bundles + CI/CD: dev → pre-prod → prod", 15)))
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
    a(link("#foundation", rect(20, 732, 582, 112, "#F1F1EF") + tx(38, 758, "AWS foundation: your account", 19), "The foundation"))
    for k, ln in enumerate(["Customer-managed VPC · PrivateLink to Databricks", "S3 holds all data · KMS keys you own · IAM roles · CloudTrail",
                            "Mumbai, with Hyderabad for recovery · EU only if legal requires"]):
        a(tx(38, 784 + k * 22, ln, 15))
    a(link("#foundation", rect(618, 732, 582, 112, "#E6EAF7") + tx(636, 758, "Databricks on AWS: runs in your account", 19), "The foundation"))
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
    return svg(1400, 860, "".join(b), "Data platform on AWS and Databricks: agent plane and control plane on top; a spine from plant and business sources through ingestion, S3 landing, bronze, silver, gold, semantic and experiences; a streaming lane; a band of ten horizontal assets; the AWS and Databricks foundation; and a governance rail on the right.")


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
    ('<a href="/learn/data-platform-architecture/ingestion/">Common Ingestion Framework</a>', "A new source is a YAML entry, not a new notebook. One lander from landing to bronze, with ingest metadata, replay and watermarks.", "Ours, on Databricks; movers behind a port (DMS, AppFlow, Transfer Family, Kinesis, our puller)", "Built; first end-to-end Databricks run in progress"),
    ('<a href="/learn/data-platform-architecture/metadata-store/">Metadata store</a>', "One place where every source, table, rule, owner and budget is declared. Pipelines read it; nobody configures by hand.", "Ours; Aurora PostgreSQL", "Built in the framework (design published); the Aurora deployment is to do"),
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
    "X1": ("partial", "Asset Bundles, Unity Catalog tags", "Aurora PostgreSQL for the metadata store", "YAML in Git → loader → metadata store → generated jobs. Ours (Common Ingestion Framework)."),
    "X2": ("full", "Lakeflow Jobs: schedules, file-arrival triggers, retries", "EventBridge for events from outside", "Jobs generated from metadata, not clicked together. Ours."),
    "X3": ("partial", "Delta schema enforcement and evolution; Auto Loader rescued data", "Glue Schema Registry for streams, if used", "Contracts in the open ODCS standard, checked in CI and at run time. Ours."),
    "X4": ("partial", "Declarative Pipelines expectations; DQX (Databricks Labs)", "-", "Rules from metadata, quarantine, one results table. Ours, with DQX behind a port."),
    "X5": ("partial", "DQX profiler; Lakehouse Monitoring on tier-1 gold; Unity Catalog classification for PII (" + CHECK + ")", "-", "Profiling settings per dataset, profile compared with the last one, suggested rules as pull requests, all tied to the run id. Ours."),
    "X6": ("none", "-", "-", "Counts and sums from source to gold, per run. Ours."),
    "X7": ("full", "Unity Catalog table and column lineage", "-", "Lineage before Databricks (movers, source systems) from the run log and mover ids; joined to the run id. Ours."),
    "X8": ("partial", "System tables for jobs, queries, pipeline event logs", "CloudWatch for DMS, Kinesis, MSK", "One run log with one run id across both. Ours."),
    "X9": ("partial", "Job duration alerts; freshness checks in monitoring (" + CHECK + ")", "CloudWatch alarms", "A freshness promise per table, declared in metadata and alerted. Ours."),
    "X10": ("partial", "Billing system tables, budget policies, tags", "Cost and Usage Report, Cost Explorer, Budgets", "Cost per data product and per run, with findings. CostSherlock."),
    "X11": ("full", "Unity Catalog grants, row filters, column masks, ABAC (" + CHECK + ")", "IAM roles, KMS, VPC, PrivateLink", "Grants declared in metadata and applied by the pipeline. Ours."),
    "X12": ("partial", "Column masks, tags, data classification (" + CHECK + ")", "Macie scans landing buckets for personal data that slipped through; Comprehend finds names in free text such as warranty notes", "Tokenise at the door, the token vault, erasure, suppression and retention jobs. Ours."),
    "X13": ("partial", "Unity Catalog owners, comments, tags; Metric Views", "-", "Glossary and metric ownership workflow. Ours (OpenMetadata optional)."),
    "X14": ("partial", "Audit system tables", "CloudTrail", "Run log with a fingerprint of the config each run used. Ours."),
    "X15": ("partial", "Delta time travel, MERGE, full refresh of pipelines", "S3 versioning", "Backfill plans and watermark resets from metadata, never doubling a number. Ours."),
    "X16": ("full", "Asset Bundles, Git folders, Terraform provider", "GitHub Actions with short-lived OIDC sign-in; separate accounts per environment", "Templates only. Ours."),
    "X17": ("none", "-", "-", "Unit, contract and data tests (pytest), shift-left checks, DataTwin worlds. Ours, open source."),
    "X18": ("partial", "Time travel, deep clone, job retries", "S3 replication and deep clone to Hyderabad (no AWS Backup on personal data)", "A written, tested restore drill. Ours."),
    "X19": ("full", "Photon, liquid clustering, predictive optimization, serverless", "-", "Checks in CI and cost findings. Shift-left bundle + CostSherlock."),
    "X20": ("none", "-", "-", "Detect → fix proved on a pre-prod clone → pull request → verify → roll back. Ours."),
    "X21": ("partial", "Databricks Assistant for code", "Bedrock, if preferred for models", "Agents that draft manifest entries, rules and docs as pull requests. Ours."),
    "X22": ("none", "-", "-", "A pretend plant with planted faults (a press goes silent, a batch sent twice). DataTwin, ours."),
}

AWS_VS_DB = [
    ("Plant-floor data collection", "AWS IoT SiteWise, IoT Core, Greengrass", "Auto Loader / streaming tables read what SiteWise lands", "Keep SiteWise at the plant edge: it talks to the machines. Databricks takes the data from S3 or Kinesis for analytics."),
    ("Ingest from SAP", "AppFlow or a partner extractor", "SAP Business Data Cloud connector (" + CHECK + ")", "Use an SAP-certified route (Datasphere or a certified extractor) behind one port; never read SAP tables directly."),
    ("Ingest from databases (CDC)", "AWS DMS", "Lakeflow Connect", "DMS for v1, into S3 landing, so every source passes the lander's tokenising and run log. Lakeflow Connect writes straight into tables; revisit per source later."),
    ("Batch and streaming pipelines", "Glue jobs, EMR", "Lakeflow Declarative Pipelines and Jobs", "Pursue Databricks: one engine for batch and streaming, built-in quality rules and lineage."),
    ("Warehouse for BI", "Redshift", "Databricks SQL warehouse", "If Redshift is heavily used, keep it and let it read our tables as Iceberg (UniForm) or through Delta Sharing (" + CHECK + "); new work on Databricks SQL. See the migration plan."),
    ("Ad hoc queries on S3", "Athena", "SQL warehouse", "Keep Athena for small one-off queries; it can read the tables as Iceberg (UniForm)."),
    ("Catalog and access", "Glue Catalog, Lake Formation", "Unity Catalog", "Pursue Unity Catalog as the one catalog: lineage, masks and audit in one place. Avoid running two access models."),
    ("ML and AI", "SageMaker, Bedrock", "Mosaic AI: Vector Search, Model Serving", "Use Databricks for ML on lakehouse data; call Bedrock models from Databricks where the company already uses Bedrock."),
    ("Dashboards", "QuickSight (now part of Amazon Quick Suite, " + CHECK + ")", "AI/BI dashboards and Genie", "Keep existing QuickSight reports; build new ones on AI/BI over the same metric views."),
    ("Cost view", "Cost Explorer, CUR", "Billing system tables", "Use both; CostSherlock joins them per data product."),
]

FAQ = [
    ("Does our data leave our AWS account?", "No. Classic compute runs in your account and your VPC; serverless compute runs in Databricks' serverless plane in the same region. All tables live in your S3 buckets, encrypted with KMS keys you own. The Databricks control plane manages the workspace; for serverless compute, check the current data-residency terms for your region."),
    ("Why Databricks if we already have Glue, EMR and Redshift?", "One engine for batch and streaming, one catalog (Unity Catalog) for access, lineage and audit, and AI/BI with Genie on the same governed data. You do not have to switch everything at once: keep what works and put new work on the lakehouse."),
    ("What is a metric view?", "A definition of a business metric (for example, scrap rate) stored once in Unity Catalog, with its formula, dimensions and filters. Dashboards, Genie and the Conversation UI all use it, so the number is the same everywhere."),
    ("What are horizontal assets?", "Parts built once and reused by every pipeline and data product: ingestion, metadata, quality, cost, testing and the conversation layer. They are what makes the tenth data product much cheaper than the first."),
    ("How are compound recipes and personal data protected?", "Recipes and formulation data sit in a restricted catalog with its own storage and encryption key, readable only by a named group. Personal data of dealers, fleet drivers and consumers is swapped for tokens as it enters the platform; the real values live only in a separate token vault, and erasing a person means deleting their vault entry, blocking them from being loaded again, and erasing the recovery copies too. Commercial columns such as prices are masked by Unity Catalog for everyone outside finance and sales, in every tool, not only in dashboards. All data stays in India (Mumbai, with recovery in Hyderabad); personal data from the EU travels only as the law allows (see the privacy section), and a separate EU platform is added only if your legal team requires it. Access is audited in system tables and CloudTrail."),
]


# ---------------------------------------------------------------- metadata store and ingestion on AWS
MD_TABLES = [
    ("platform_config", "Settings for the whole platform: default storage paths, default quality action, budget limits", "Platform team, through YAML"),
    ("source_master", "One row per source system: SAP S/4HANA, MES, historian, quality LIMS, warranty, dealer DMS", "Through YAML"),
    ("source_config", "Key-value settings per source, grouped (ingestion, quality, cost): connection secret reference, mover, schedule", "Through YAML"),
    ("dataset_master", "One row per dataset (table) of a source, with its target schema and table", "Through YAML"),
    ("dataset_config", "Key-value settings per dataset: load mode, keys, history (SCD) type, profiling settings, PII purpose and retention, owner and deputy, freshness target and tier. Quality rules have their own table, dq_rule", "Through YAML"),
    ("dataset_view", "The one view every pipeline reads: platform, then source, then dataset settings merged into JSON, the most specific winning", "Generated"),
    ("run_log", "One row per run: dataset, status, row counts, cost, and a fingerprint of the exact settings used", "Pipelines"),
    ("watermark", "How far each incremental load has got", "Pipelines"),
]

GIT_VS_DB = [
    ("What it holds", "Configuration: sources, datasets, load modes, keys, rules, owners, PII tags, budgets",
     "The same configuration loaded from Git, plus runtime state: watermarks, run log, quality results"),
    ("Who writes it", "People, and agents, by pull request", "The loader writes configuration; pipelines write runtime state"),
    ("Why we need it", "Review and approval, full history, easy rollback, the same file promoted dev → pre-prod → prod",
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
    ("SAP S/4HANA (sales, stock, procurement, finance)", "Amazon AppFlow, SAP OData connector, on released CDS views and extractors with delta", "Never SAP tables directly; Datasphere or Business Data Cloud only if already licensed"),
    ("MES and quality / LIMS databases", "AWS DMS with change capture", "Change capture keeps loads small and brings deletes"),
    ("Small and reference tables, databases without CDC", "Our puller (the framework's built connectors) as a Databricks job", "Full copy or watermark, straight to bronze through the same lander steps (no landing)"),
    ("Plant historian and press / mixer sensors", "AWS IoT SiteWise → Kinesis or S3", "The streaming lane: same layers, continuous"),
    ("Dealer management system, CRM (SaaS)", "Amazon AppFlow; our puller's REST connector where AppFlow has none", "Lakeflow Connect is not used in v1"),
    ("Supplier files, raw-material prices", "AWS Transfer Family (SFTP) → S3", "The lander reads the new files listed in its file log"),
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
     "Pipelines write; nobody else", "Grows every run; monthly partitions, 13 months kept, then summarised into prod_ops"),
    ("audit", "Who changed what: config_load_log (every loader run, Git commit, who approved, what changed)",
     "Only the loader appends; never updated or deleted", "Small; kept 7 years, like the audit bucket"),
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
  status          text NOT NULL,           -- started, succeeded, failed, skipped, blocked
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
    ("Load safely", "Append to bronze, every row stamped with the run id. Bronze is never updated, so replay always works. Each batch is appended with a transaction id from the file log, so a batch committed before a crash is never appended twice."),
    ("Commit once", "Only after the data is committed: mark the run succeeded and move the watermark to high, in one database transaction."),
    ("Crash in between?", "The watermark did not move, so the next run reloads the same window, and silver's duplicate step makes that harmless."),
    ("Late rows", "A look-back overlap (say 2 hours, set in dataset_config) re-reads a little of the last window; silver drops the repeats."),
    ("Files and streams", "Auto Loader and streaming keep their own checkpoints; we record the checkpoint location, not a second watermark. CDC sources use the change position (LSN or SCN). SAP moves its own delta token when it hands over an extract, so after a failure we never ask SAP again: we replay from landing or bronze."),
]


# ---------------------------------------------------------------- bronze to silver steps (tier T2)
SILVER_STEPS = [
    ("Read what is new", "Only rows that arrived since the last run (change feed or watermark)."),
    ("Fix types", "Text to numbers and dates; units made the same (all temperatures in °C, all weights in kg)."),
    ("Standardise time", "Store UTC, and keep the plant's local time beside it, because shifts are local."),
    ("Check the contract", "At sources we do not control: the columns and types we were promised."),
    ("Run the quality rules", "From the metadata store; bad rows to the table's quarantine table with the reason."),
    ("Remove duplicates", "On the business keys, keeping the latest by a sequence column."),
    ("Conform keys", "Map each system's own codes to one key: SAP material and MES material become one material key."),
    ("Keep history", "SCD Type 1 (overwrite) or Type 2 (keep every version), as set per dataset."),
    ("Handle deletes", "Soft-delete with a flag and the time; never lose the row."),
    ("Merge and log", "One MERGE, then the run log row and a count reconcile with bronze."),
    ("Tag", "Confidential and recipe columns tagged so Unity Catalog masks apply. Personal columns arrive as tokens already and are tagged too, so nobody joins them back to the vault by accident."),
]


# ---------------------------------------------------------------- gold, semantic, AI/BI (tiers T2 gold + T6)
GOLD_DECISIONS = [
    ("How gold is modelled", "Star schemas (Kimball): facts at a stated grain, shared dimensions", "Pursue",
     "Business people read them, BI tools and Genie understand them, and shared dimensions make numbers line up across subjects. Data Vault adds a layer nobody here needs; one big flat table repeats data and breaks on history."),
    ("How gold is built", "SQL files in Git, run as materialized views in Declarative Pipelines", "Pursue",
     "Incremental refresh and lineage come with the platform. One model per file, so moving to dbt Core later is a copy, not a rewrite."),
    ("dbt", "Not now", "Drop for now",
     "Adopt dbt Core if the team already knows it, if gold passes about 50 models across teams, or if gold must run outside Databricks. Never dbt Cloud or a second metric layer."),
    ("Where metrics are defined", "Unity Catalog metric views, one per business process", "Pursue",
     "Defined once, governed by the catalog, read by dashboards, Genie and our Conversation UI alike. A separate semantic tool (Cube, AtScale) only if many tools outside Databricks need the same metrics."),
    ("Asking in plain words", "Genie for analysts and managers; our Conversation UI inside staff apps and wherever a wrong number is costly", "Pursue",
     "Genie is already in the platform. The Conversation UI never lets the model write SQL."),
    ("Existing BI tools", "Read through a serverless SQL warehouse, from metric views (" + CHECK + ") or gold", "Pursue",
     "Nobody has to throw away reports on day one."),
    ("Compute for questions", "Separate serverless SQL warehouses for dashboards, Genie and ad hoc work", "Pursue",
     "Each workload gets the right size, and CostSherlock can show what each one costs."),
]

BUS = ["Date", "Plant", "Press", "Shift", "Material", "Dealer", "Customer / fleet", "Defect"]
BUS_MATRIX = [
    ("Production", "one row per press per hour, split by batch type (production or trial)", "11111000"),
    ("Downtime", "one row per stop", "11110000"),
    ("Scrap", "one row per scrapped tyre batch", "11111001"),
    ("Quality tests", "one row per test result", "11101001"),
    ("SAP order lines", "one row per order line", "11001110"),
    ("Dealer sell-out", "one row per dealer per material per day", "10001110"),
    ("Warranty claims", "one row per claim", "11001111"),
]

GOLD_SCHEMAS = [
    ("prod_gold.shared", "The shared dimensions: date (with the April-to-March financial year), plant, press, shift, material, dealer, customer, defect code", "Platform team"),
    ("prod_gold.manufacturing", "Production, downtime, scrap", "Manufacturing data owner"),
    ("prod_gold.quality", "Quality tests, warranty claims", "Quality data owner"),
    ("prod_gold.sales", "SAP order lines, dealer sell-out, dealer stock", "Sales data owner"),
    ("prod_semantic.*", "Metric views only, one schema per business area; no tables", "Each metric's owner"),
]

MULTI_INPUT = [
    ("Give every input a role", "The driver (the events the fact counts), dimensions looked up as of the event time, and contributor facts that add measures."),
    ("Never lose a row to a missing dimension", "A press that is not in the master yet gets an 'unknown' member, flagged, and fixed when the master catches up. No inner joins to dimensions."),
    ("Join history as of the event", "A material's compound at the moment the tyre was cured, not today's."),
    ("Recompute changed windows", "When any input changes, recompute the affected hours or days in full and replace them. Simpler and safer than patching single rows."),
    ("Check after every run", "Totals reconcile with silver, and the share of 'unknown' members stays under its limit."),
]

METRICS = [
    ("OEE", "Availability × performance × quality, each computed from sums (run time over planned time; ideal cycle time × count over run time; good tyres over all tyres)", "Press, shift, plant, day", "Plant operations head"),
    ("Scrap rate", "Scrapped tyres over tyres cured, production batches only. Both counts come from the production fact; the breakdown by defect comes from the scrap fact, whose totals reconcile with it", "Press, material, day; defect through the scrap fact", "Quality head"),
    ("First-pass yield", "Tyres passing every test the first time, over tyres tested", "Plant, material, day", "Quality head"),
    ("Downtime hours", "Sum of stop durations, by cause", "Press, cause, shift", "Maintenance head"),
    ("On-time in-full (OTIF)", "Order lines delivered complete and on the promised date, over all order lines", "Plant, customer, week", "Supply chain head"),
    ("Sell-out units", "Tyres sold by dealers to end customers", "Dealer, material, region, week", "Sales head"),
    ("Warranty claim rate", "Claims per 10,000 tyres, counted against the month the tyres were made, not the month of the claim", "Plant, material, production month", "Quality head"),
]

SEMANTIC_RULES = [
    ("Metrics read gold only.", "Never silver, never another metric view's output."),
    ("Ratios are computed at query time, from sums.", "Never store a percentage and never average percentages: the average of three plants' OEE is not the company's OEE."),
    ("Every metric has an owner, a definition in plain words and a certified tag.", "Changing a definition is a pull request approved by the owner, who also updates the expected benchmark answers in the same pull request. Metric views recompute history with the new definition, so the change is logged with its date and shown on dashboards; where last year must stay comparable, the old definition is kept as a second measure for a year. Metrics that share a part (OEE's quality part and scrap rate) share one definition of it."),
    ("Shift metrics use plant local time.", "Stored in UTC, reported in the plant's time, so the night shift is not split across two days."),
    ("Joins live in the metric view.", "Pre-joined or pre-summed tables only when a dashboard is measured slow or costly, and then as materialized views in gold."),
    ("Front ends read metric views.", "Direct access to gold is for analysts and data scientists only."),
]

METRIC_YAML = """# prod_semantic.manufacturing.press_performance   (syntax: """ + CHECK + """)
version: 0.1
source: prod_gold.manufacturing.fct_production        # one row per press per hour
joins:
  - name: press
    source: prod_gold.shared.dim_press
    on: source.press_key = press.press_key
  - name: material                                    # SCD2: the version valid at cure time
    source: prod_gold.shared.dim_material
    on: source.material_key = material.material_key
dimensions:
  - name: Plant
    expr: press.plant_name
  - name: Batch type
    expr: source.batch_type
  - name: Press
    expr: press.press_code
  - name: Compound family
    expr: material.compound_family
  - name: Production date (plant time)
    expr: source.plant_local_date
measures:
  - name: Tyres cured
    expr: SUM(source.tyres_cured)
  - name: Scrap rate                                  # production batches only
    expr: SUM(source.tyres_scrapped) FILTER (WHERE source.batch_type = 'production') / NULLIF(SUM(source.tyres_cured) FILTER (WHERE source.batch_type = 'production'), 0)
  - name: Completeness                                # share of expected press-hours that arrived
    expr: SUM(source.hours_received) / NULLIF(SUM(source.hours_expected), 0)
  # OEE parts count complete press-hours only (top and bottom alike), so a silent press
  # makes OEE incomplete, never wrongly high or low; Completeness shows how much is missing.
  - name: Availability
    expr: SUM(source.run_minutes) FILTER (WHERE source.is_complete) / NULLIF(SUM(source.planned_minutes) FILTER (WHERE source.is_complete), 0)
  - name: Performance
    expr: SUM(source.ideal_cycle_seconds * source.tyres_cured) FILTER (WHERE source.is_complete) / NULLIF(SUM(source.run_minutes * 60) FILTER (WHERE source.is_complete), 0)
  - name: Quality
    expr: SUM(source.tyres_good) FILTER (WHERE source.is_complete) / NULLIF(SUM(source.tyres_cured) FILTER (WHERE source.is_complete), 0)
  - name: OEE                                         # good tyres x ideal cycle time over planned time
    expr: SUM(source.ideal_cycle_seconds * source.tyres_good) FILTER (WHERE source.is_complete) / NULLIF(SUM(source.planned_minutes * 60) FILTER (WHERE source.is_complete), 0)"""

GENIE_SPACES = [
    ("Plant performance", "Plant managers, shift leads", "Press performance, downtime and scrap metric views", "40 questions"),
    ("Quality and warranty", "Quality engineers", "Scrap, quality tests and warranty metric views", "40 questions"),
    ("Sales and dealers", "Sales and aftermarket managers", "Order lines, sell-out and dealer stock metric views", "30 questions"),
    ("Platform ops", "The data team", "Ops gold from the observability section", "20 questions"),
]

GENIE_RULES = [
    ("One space per audience, not one for everything.", "A small, curated space answers better than a large one; keep each to the views its audience needs."),
    ("Metric views first.", "They carry the definitions, so Genie picks a defined metric instead of inventing a formula."),
    ("Write instructions and example questions.", "Plant names and their short forms, which date to use, what 'last week' means, with worked examples."),
    ("Benchmark before go-live and after every change.", "A set of questions with known right answers, run once per role with test identities, so filtered answers are checked too; the space goes live at 90% right or better, and a change that lowers the score does not merge."),
    ("Say when a filter applied.", "The space instructions make Genie say 'for your plant' when the person's row filter narrowed the answer, so one plant's figure is never read as the company's."),
    ("Read the thumbs-down every week.", "Each wrong answer becomes a fix to the instructions or a new benchmark question."),
    ("Security comes from the catalog.", "Genie runs as the person asking, so a plant manager sees only that plant's rows."),
]


def star():
    b = []
    a = b.append
    a(rect(360, 120, 220, 110, "#F7E7B4", sw=2.2) + tx(470, 152, "fct_production", 17, "middle", weight="700")
      + tx(470, 176, "one row per press per hour", 12.5, "middle") + tx(470, 196, "tyres cured, scrapped,", 12, "middle", fill="#555")
      + tx(470, 214, "run and planned minutes", 12, "middle", fill="#555"))
    dims = [(60, 20, "dim_date", "financial year Apr-Mar"), (360, 10, "dim_plant", "India and Europe"), (660, 20, "dim_press", "curing press, line"),
            (60, 250, "dim_shift", "plant local time"), (660, 250, "dim_material", "SCD2: compound as of cure")]
    for x, y, n, sub in dims:
        a(rect(x, y, 220, 64, "#fff") + tx(x + 110, y + 28, n, 15, "middle") + tx(x + 110, y + 48, sub, 12, "middle", fill="#555"))
        cx, cy = x + 110, y + 32
        a(f'<line x1="{cx}" y1="{cy + (32 if y < 120 else -32)}" x2="470" y2="{120 if y < 120 else 230}" stroke="{INK}" stroke-width="1.5"/>')
    a(tx(470, 345, "Facts hold the numbers; dimensions hold the words you filter and group by.", 14, "middle"))
    return svg(940, 360, "".join(b), "A star schema: the production fact in the middle, one row per press per hour, joined to five dimensions: date, plant, press, shift and material, where material keeps history (SCD2).")


# ---------------------------------------------------------------- security, privacy, governance (tier T7)
SENSITIVITY = [
    ("Internal", "Production counts, OEE, scrap, downtime, stock", "prod_gold, prod_semantic", "Every employee group that needs it; plant staff see their own plant's rows", "Row filter by plant"),
    ("Confidential", "Prices, dealer discounts, margins, cost per tyre", "prod_gold.sales, columns tagged confidential", "Finance and sales groups", "Column mask for everyone else"),
    ("Personal", "Dealer contacts, fleet drivers, consumers who register a warranty, operator ids on shift logs, names inside free-text warranty notes", "Tokenised at the lander; real values only in the token vault (prod_pii_vault, its own bucket and key)", "Almost nobody needs the real value; the warranty team for a live claim", "Tokens everywhere, mask on the vault, purpose and retention per category"),
    ("Restricted", "Compound recipes, cure recipes, process settings", "prod_restricted only, its own bucket and key", "The named recipe keepers", "No Genie space, no copies except the encrypted recovery copy, every read alerted"),
]

ROLES = [
    ("Platform engineer", "Read and write in dev; read prod_ops", "Deploys only through CI/CD"),
    ("Data engineer", "Read and write in dev; read the results schemas in pre-prod", "Never writes to prod by hand; prod clones in pre-prod are readable only by CI"),
    ("Analyst, data scientist", "Read prod_gold and prod_semantic", "Personal data only as tokens; confidential columns masked"),
    ("Plant manager, shift lead", "Read prod_semantic; dashboards and the Plant performance Genie space", "Own plant's rows only"),
    ("Quality engineer", "Read quality and manufacturing gold and metric views", "Personal data only as tokens"),
    ("Sales and finance", "Read sales gold and metric views, confidential columns visible", "Own region's rows for regional managers"),
    ("Recipe keeper", "Read prod_restricted", "Named people, reviewed monthly"),
    ("Privacy case handler", "Read and erase in prod_pii_vault", "The privacy team and, for a live claim, the warranty team; every lookup logged"),
    ("Auditor", "Read audit system tables and the audit schema", "No business data"),
    ("Service principals", "One per pipeline area; write only their own target schemas in prod", "The only identities that write to prod"),
]

ACCESS_MECH = [
    ("Groups from your identity provider", "Every grant goes to a group, never to a person. Joining or leaving a group is the only way access changes."),
    ("Tags set from metadata", "In silver, the pipeline tags each column as personal, confidential or recipe, from dataset_config. Nobody tags by hand."),
    ("Policies on tags", "One policy per tag masks the column for every table that carries it, through attribute-based access control (" + CHECK + "). Where that is not yet available, the pipeline generates a column mask per table from the same tags."),
    ("Row filters by plant and region", "A small mapping table (group to plants, group to regions), loaded from Git like all config, drives one row-filter function used on every fact table."),
    ("Grants from metadata", "Catalog-level grants live in Terraform; schema and table grants are declared in YAML next to the datasets and applied by the deploy, so the catalog always matches Git and drift is reported."),
]

ERASURE = [
    ("Request arrives", "From the privacy team's case system, with the person's identifier."),
    ("Find the token", "Look up the person's token in the vault (prod_pii_vault)."),
    ("Find every place", "Lineage and tags list every table holding that token: silver, gold, quarantine tables."),
    ("Erase or restrict?", "The privacy lead decides. An open claim or a product recall may need the identity kept for now: processing is then restricted instead, and the decision is recorded in the case."),
    ("Erase", "Delete the vault row first: from that moment the token points to nobody. Add a one-way fingerprint of the identifier to the suppression list, so a re-sent extract cannot bring the person back. Then blank the token's rows in silver (including old SCD2 versions) and in the quarantine tables, and rebuild the affected gold windows. Where the law requires a claim to be kept (product liability), the claim stays and only the identity goes."),
    ("Erase the copies", "Run the same erasure on the recovery copies in Hyderabad, and delete the person's files from landing, including old versions."),
    ("Clean old files", "Delta keeps old file versions for 30 days; after VACUUM, the data is gone from storage. Bronze only ever held the token. VACUUM runs in Hyderabad too, every bucket expires old object versions within 30 days, and AWS Backup is not used for the vault or personal-data tables. No table may be restored to a version from before an erasure; if one is, the erasure log is replayed straight after."),
    ("Record evidence", "Write what was erased, where and when to the audit schema, and close the case."),
]

PRIVACY_RULES = [
    ("Tokenise at the door.", "The lander swaps names, phone numbers and emails for tokens before bronze, and checks the suppression list. Free-text fields such as warranty notes go through a personal-data detector behind a port, which must handle English and German (Amazon Comprehend's detection covers English and Spanish, check current status; an open-source detector such as Presidio with German models otherwise); until that is confirmed, EU free text is held out of bronze. For sources with personal data, a file with a column nobody declared is held and the dataset blocked until the contract says what it is (only the column's name is logged), so a new personal column cannot slip in as rescued data. Bronze stays append-only and still holds nothing personal, so erasure never fights the replay design."),
    ("Real values never wait in landing.", "Files from sources with personal data use their own landing folder, deleted one day after the lander has read them, with old versions expiring the same day. Macie scans landing weekly for personal data in the wrong place."),
    ("EU personal data leaves the EU only on a legal basis.", "India has no EU adequacy decision, so personal data from EU plants and dealers travels under the company's Standard Contractual Clauses with a transfer impact assessment, or is tokenised in the EU before it leaves. Your legal team picks; until then, EU sources are loaded without personal columns."),
    ("A purpose for every personal column.", "dataset_config records why it is kept (warranty claim handling, dealer payments) and for how long; columns without a purpose are not loaded."),
    ("Retention runs itself.", "A nightly job deletes personal data past its retention period and logs what it removed."),
    ("Logs never hold values.", "The lander, which sees real values before tokenising, never logs row values; its error messages are scrubbed before they reach error_log."),
    ("Tokens are random.", "A token is a random value, mapped to the person only in the vault, so deleting the vault entry really does make the data anonymous. The suppression fingerprint uses a separate secret key."),
    ("Consent stays at the source.", "Warranty and dealer systems collect consent; we load the consent flag and filter on it, we never decide it."),
    ("Breach response is written down.", "Who decides, who tells the regulator and the people affected, inside the deadlines of the DPDP Act and GDPR (72 hours for GDPR; DPDP Rules timelines: " + CHECK + ")."),
]

AI_GOV = [
    ("Genie and the Conversation UI run as the person asking.", "Row filters and masks apply exactly as in a dashboard."),
    ("prod_restricted and prod_pii_vault are never added to a Genie space or an agent's tools.", "Recipes and real identities are not answerable in plain words, by design."),
    ("Models run inside the platform or your AWS account.", "Databricks-hosted models or Amazon Bedrock in your account; no data is sent to a public chat service."),
    ("Every question and answer is logged.", "With the person, the metric used and the SQL the engine ran, in a separate schema (prod_ops.ai_log) that only the space owners and the platform lead can read, because answers carry other plants' figures and prices."),
    ("Row security is tested, not assumed.", "The gold-to-metrics test runs as a plant-manager test identity and must see one plant only, through every metric view and every Genie space. It is a release gate."),
]

GOV_ROLES = [
    ("Data owner", "A business head (plant operations, quality, sales)", "Decides who may see the data and signs off metric definitions"),
    ("Data steward", "A named person per source", "Writes quality rules, reviews quarantine weekly, approves suggested rules"),
    ("Custodian", "The platform team", "Runs the platform, applies the owner's decisions, never decides access"),
    ("Privacy lead", "From the legal or privacy team", "Owns purposes, retention, erasure requests and breach response"),
]


# ---------------------------------------------------------------- CI/CD and environments (tier T9)
REPOS = [
    ("platform-foundation", "Terraform for accounts, network, storage, keys, workspaces, catalogs", "Platform team", "Terraform plan on every pull request; apply after approval"),
    ("data-platform", "The framework code, all YAML config (sources, datasets, rules, contracts, grants), gold SQL, metric views, dashboards, Genie space definitions, Asset Bundles", "Shared, with CODEOWNERS per folder", "The release path below"),
]

OWNERS = [
    ("framework/", "Platform team"),
    ("config/sources/, config/datasets/", "Data engineers for that source"),
    ("config/dq/", "The source's data steward"),
    ("contracts/", "The producing team and the platform team"),
    ("gold/, semantic/", "The business area's data owner and an analytics engineer"),
    ("config/grants/, config/access/", "The data owner, plus the privacy lead for personal data"),
]

DEPLOYS = [
    ("Accounts, network, buckets, keys, workspaces, catalogs", "Terraform", "platform-foundation"),
    ("Jobs, pipelines, dashboards", "Databricks Asset Bundles", "data-platform"),
    ("Sources, datasets, rules, profiling settings", "Our config loader, into the metadata database", "data-platform"),
    ("Metric views, row filters, masks, schema and table grants", "SQL run by the deploy, generated from YAML", "data-platform"),
    ("Genie spaces", "Their definitions in Git, applied through the Genie API (" + CHECK + ")", "data-platform"),
]

PIPE_STAGES = [
    ("Pull request", "Lint, shift-left checks, unit tests, contract checks, config dry-run against the key registry, bundle validate, Terraform plan", "Laptop and CI runner, no Databricks needed", "minutes"),
    ("Merge to main", "Deploy to dev; per-hop integration tests on fixed fixtures", "Dev workspace, fresh schema per run", "about 20 minutes"),
    ("Release tag", "Deploy to pre-prod; end-to-end on synthetic data, DataTwin faults, real-data run on shallow clones, parallel run against prod, Genie benchmarks", "Pre-prod workspace", "an hour or two"),
    ("Approval", "The release report goes to the data owner of each changed area; one approval per area", "GitHub environment approval", "same day"),
    ("Prod deploy", "Deployed by the prod service principal; risky changes to one plant first for one full day, promoted to all only if the smoke checks and reconciliations stay green", "Prod workspace", "minutes, then one day"),
    ("After deploy", "Smoke checks: first runs green, row counts within band, metrics within band", "Prod", "first run"),
]

ENVS = [
    ("Dev", "Synthetic data and small samples; no personal data", "Data and platform engineers", "Small serverless; jobs stop after 2 hours; budget alert"),
    ("Pre-prod", "Shallow clones of prod, personal data already tokens, recipes and the vault excluded", "CI writes and reads prod; engineers see results", "Like prod, for an hour or two per release; DataTwin's nightly run happens in dev"),
    ("Prod", "Real data", "Read through groups; only service principals write; personal access tokens off for people", "Sized for the plants' shifts (see sizing); budget policies per data product"),
]

CICD_RULES = [
    ("No secrets in CI.", "GitHub Actions signs in to AWS and Databricks with short-lived OIDC tokens (" + CHECK + " for Databricks), not stored keys."),
    ("A config change is a deploy.", "A new rule or source goes through the same pipeline, with lighter gates when no code changed, except changes to quality limits, watermarks, replacement rules and grants, which always take the full gates."),
    ("Breaking schema changes are versioned.", "A new column passes: it lands in bronze and is ignored until someone maps it. A removed, renamed or narrowed column stops at silver's contract check and needs a new contract version, a migration step and a notice to consumers."),
    ("Rollback is redeploying the last tag.", "If wrong data was written for one plant, recompute only that plant's windows with the previous tag, so good runs for other plants are kept; watermarks are reset by a backfill plan, not by hand. A whole-table RESTORE only when every later run is also wrong, and never to a version before an erasure. The platform lead decides rollback or fix."),
    ("Small, frequent releases.", "Trunk-based: short branches, merged within a day or two, released weekly or on demand."),
]


def cicd_flow():
    b = []
    a = b.append
    st = [("Pull request", ["checks on the code"], "#F4F4F2"), ("Dev", ["per-hop tests"], "#E0F1F7"),
          ("Pre-prod", ["real data, DataTwin,", "parallel run, benchmarks"], "#FFF4D9"),
          ("Approval", ["data owners sign"], "#F8E6EF"), ("Prod", ["one plant first"], "#E6F4EC")]
    for i, (t, subs, f) in enumerate(st):
        x = 20 + i * 214
        a(rect(x, 40, 186, 84, f) + tx(x + 93, 70, t, 16, "middle") + "".join(tx(x + 93, 92 + k * 17, ln, 12, "middle", fill="#555") for k, ln in enumerate(subs)))
        if i < 4:
            a(arr(x + 186, 82, x + 214, 82))
    for who, x in [("developer opens it", 113), ("merge to main", 327), ("release tag", 541), ("release report", 755), ("prod service principal", 969)]:
        a(tx(x, 26, who, 11.5, "middle", fill="#555"))
    a(rect(20, 150, 1040, 50, "#fff", dash=True) + tx(540, 180, "One repo, three things deployed together: code (Asset Bundles), config (loader into the metadata database), definitions (metric views, grants, Genie)", 13, "middle"))
    a(rect(20, 216, 1040, 40, "#F8E6EF") + tx(540, 241, "If a release is wrong: redeploy the last tag, and restore each table to the version before the run", 13, "middle"))
    return svg(1080, 270, "".join(b), "The release path: pull request checks, deploy to dev with per-hop tests, release tag to pre-prod with real data, DataTwin, parallel run and benchmarks, approval by data owners, then prod, one plant first. Code, config and definitions are deployed together; rollback redeploys the last tag and restores tables.")


# ---------------------------------------------------------------- agents (tier T10)
AGENTS = [
    ("Triage", "An alert opens an incident", "Collects the evidence: the failed run, the error, recent config and code changes, upstream lineage, CloudWatch for the mover. Writes a diagnosis and the likely cause class into the incident.", "Read only"),
    ("Fix proposer", "A diagnosed incident with a known cause", "Starts only after a person has confirmed the triage diagnosis. Its clone runs go through the CI pipeline, so it never reads prod itself. Drafts the fix as a pull request (a widened type, a new rule limit, a watermark reset plan), and proves it by re-running the failed window on a shallow clone in pre-prod.", "Pull request + pre-prod clone"),
    ("Rule suggester", "A new profile or a full quarantine table", "Explains what changed in plain words and drafts quality rule changes for the steward.", "Pull request"),
    ("Source onboarder", "A sample file or a database table from a new source", "Drafts the source and dataset YAML, the contract and the first quality rules.", "Pull request"),
    ("Genie curator", "Thumbs-down answers and failed benchmark questions", "Drafts better instructions, example questions and new benchmark questions for the space owner.", "Pull request"),
    ("Cost finder", "CostSherlock findings", "Drafts the change behind each finding (a smaller warehouse, a job schedule, a clustering key) with the expected saving.", "Pull request"),
    ("Documenter", "A table or metric without a description", "Drafts table and column comments and glossary entries from the code, the contract and lineage.", "Pull request"),
]

AUTONOMY = [
    ("Read", "ops tables, metadata, lineage, code, profiles", "All agents"),
    ("Propose", "Open a pull request; comment on an incident", "All agents"),
    ("Act on a test copy", "Deploy a branch and re-run a window on a pre-prod shallow clone", "Fix proposer only"),
    ("Act in prod", "Change data, config or code in prod", "None. Prod changes only through the normal release path, approved by a person"),
]

AGENT_RULES = [
    ("Each agent is its own service principal.", "With read access to prod_ops and the metadata, and no access to prod_restricted or prod_pii_vault: agents see tokens, never personal data."),
    ("Tools are listed, not open.", "Each agent gets a short list of tools (read a run, read lineage, open a pull request); no general SQL on prod."),
    ("Every step is logged.", "Prompts, tool calls and outputs go to prod_ops.ai_log with the incident id (restricted like the Genie log), so a reviewer can see why the agent said what it said."),
    ("Tested before trusted, measured after.", "The DataTwin faults are the agents' exam: the triage agent must name the planted cause for each fault before it is switched on, and again after every change. In production, its cause is compared with the cause the person closes the incident with, and the hit rate is on the ops dashboard."),
    ("Models stay in the account.", "Databricks-hosted models or Amazon Bedrock in your AWS account."),
]



# ---------------------------------------------------------------- running it (design test fixes)
SIZING = [
    ("Plants", "7: five in India, two in Europe; three shifts", "Plant is the first key for clustering, row filters and canary releases"),
    ("Machines streaming", "About 2,000 curing presses and mixers, 20 signals each, one reading every 5 seconds: about 8,000 readings a second, 700 million a day", "Streaming tables read Kinesis directly; about 10 GB a day once compressed in Delta"),
    ("Business data", "SAP: about 200,000 order and delivery lines a day; 3,000 dealers sending daily sell-out; about 2,000 warranty claims a day", "Batch every 30 minutes in plant hours, full nightly"),
    ("Size after five years", "About 25 TB, mostly sensor history", "Bronze sensor data older than 3 years moves to cheaper storage"),
    ("Freshness", "A reading reaches silver within 5 minutes; press-hour gold within 15 minutes after the hour; OEE ready by 06:30", "These are the tier-1 targets the alerts watch"),
    ("People asking", "About 400 dashboard users, 50 queries at once at the peak (06:00 to 07:30, morning meetings)", "Dashboards answer in under 5 seconds for 95% of views; Genie in under 30 seconds"),
    ("What the platform is not", "Machine alarms and safety interlocks stay on the plant floor (SiteWise Edge, the machines' own controls)", "The platform is for analysis and decisions, not for stopping a press"),
]

STREAM_RULES = [
    ("One path for sensors.", "SiteWise or IoT Core at the plant edge, Amazon Kinesis Data Streams in Mumbai, a streaming table into bronze, cleaned per minute into silver; each closed hour's sensor aggregates feed the window-recompute job, the only writer of the production fact."),
    ("Late readings have a limit.", "Streams wait 2 hours for late readings (an event-time watermark). Anything later lands in bronze and is picked up by the gold window recompute, so it is never lost."),
    ("Replay has a window.", "Kinesis keeps 7 days; bronze keeps everything after that. Checkpoints live in S3 per environment."),
    ("If the link to AWS drops,", "the edge buffers readings and sends them when the link is back (" + CHECK + " for buffer size); OEE for those hours shows as incomplete until they arrive."),
]

RECOVERY = [
    ("Landing", "S3 cross-region replication, same expiry rules (personal-data files still deleted after a day)", "15 minutes", "Lets the lander replay the last minutes that had not reached bronze"),
    ("Bronze", "S3 cross-region replication to Hyderabad (tokens only)", "15 minutes", "Registered at the last version whose files have all arrived (replication does not keep order), then silver and gold catch up from bronze by run id"),
    ("Silver, gold, recipes, token vault", "Incremental Delta deep clone every 4 hours", "4 hours", "Registered on the clones; erasures since the last clone are replayed"),
    ("Metadata database (Aurora)", "Aurora Global Database with a copy in Hyderabad (" + CHECK + "; otherwise snapshots copied every hour)", "Seconds (or 1 hour)", "Promote the copy; watermarks and run log carry on"),
    ("Unity Catalog", "Not copied: Hyderabad has its own catalog, built from Git", "Nothing lost", "Terraform builds catalogs and catalog grants; the data-platform deploy adds schema grants, row filters, masks, metric views and Genie spaces"),
    ("Streams", "Checkpoints are not copied; a Kinesis stream in Hyderabad is built in advance", "Gap filled from the edge buffer", "The edges switch to the Hyderabad stream; streams start from the last bronze row"),
    ("Secrets", "Secrets Manager replicates every secret to Hyderabad", "Nothing lost", "Movers and the lander find their credentials in place"),
    ("Code and config", "In GitHub", "Nothing lost", "Deployed as in any release"),
]

RECOVERY_STEPS = [
    ("Declare.", "The head of IT, or their deputy, declares the disaster. Nobody else can."),
    ("Build.", "Terraform with dr.tfvars builds the workspace, catalogs, Kinesis stream and mover definitions in Hyderabad. The network path is already in place: the Transit Gateway in Hyderabad is peered, the Direct Connect gateway reaches both regions, and the EU plants' VPN tunnels to Hyderabad are configured but idle."),
    ("Reset the bookmarks.", "Aurora's copy is seconds behind, but bronze can be up to 15 minutes behind, so each watermark is set back to the highest window actually present in Hyderabad bronze, minus the usual overlap. The lander then replays the gap from the copied landing files; nothing is marked loaded that is not there."),
    ("Lock, then secure.", "Readers are locked out. The data-platform deploy applies column tags from dataset_config first, then every grant, row filter and mask; the security test then checks one row filter and one masked column as plant-manager and analyst test identities. Nobody reads until it passes."),
    ("Open by tier.", "Tier-1 data products open first (target: 24 hours), the rest within 72 hours. Dashboards show a banner saying the platform is running from recovery."),
    ("Fail back.", "When Mumbai returns, clone the changed tables back, reconcile counts, switch the movers, and close the incident with a review."),
    ("Rehearse.", "Twice a year, against the clock, with the results in the ops dashboard."),
]

RETENTION = [
    ("Landing", "30 days; files with personal data 1 day"),
    ("Bronze", "3 years in standard storage, then an archive class Spark can still read (S3 Glacier Instant Retrieval) until year 8, then deleted. Tokens only"),
    ("Silver", "8 years for anything that supports the accounts (as Indian company law asks for books of account); 5 years for the rest"),
    ("Gold", "10 years, for trends. Rows older than silver's retention are kept only as summaries without tokens, so an erasure never needs to rebuild them"),
    ("Quarantine tables", "90 days after the steward's decision"),
    ("Runtime and ops tables", "13 months live, then summarised"),
    ("AI question log", "1 year"),
    ("Audit bucket", "7 years, locked"),
    ("Token vault", "Per purpose: for warranty, the warranty period plus 3 years; then the entry is deleted and the tokens point to nobody"),
]

MASTER = [
    ("Plant: country, time zone, financial calendar", "SAP plant master, plus a small YAML file for time zone", "Plant operations head"),
    ("Press: line, ideal cycle time per material", "MES press master; ideal cycle times from process engineering (YAML if not in MES)", "Process engineering head"),
    ("Shift calendar and planned stops", "MES, or a YAML file per plant", "Each plant manager"),
    ("Material and compound family", "SAP material master", "SAP master data team"),
    ("Key mappings (SAP and MES material, dealer ids across systems)", "Mapping tables in silver, kept from SAP or YAML", "The steward of that domain; an unmapped key becomes 'unknown' and raises an alert"),
    ("Defect codes", "The quality system", "Quality head"),
]

ONBOARD = [
    ("Network path", "How the source reaches AWS (head office link, plant VPN, SaaS over a private endpoint)."),
    ("Mover and secret", "Which mover, and its credentials in Secrets Manager."),
    ("Source and dataset YAML", "Load mode, keys, history type, schedule, freshness target and tier."),
    ("Contract", "The ODCS file, agreed with the source's owner."),
    ("People", "Data owner, steward and their deputies, and the CODEOWNERS entry."),
    ("Personal data", "Which columns, the purpose and retention of each, or a statement that there is none."),
    ("Quality rules", "The first rules, then profiling switched on to suggest more."),
    ("Master data", "Key mappings, and for a new plant its time zone, shift calendar and ideal cycle times."),
    ("Access", "For a new plant, the row-filter mapping (which groups see it)."),
    ("Tests", "A DataTwin profile for the source, so its faults are tested from the first release."),
]

BACKFILL = [
    ("A backfill is a plan in Git.", "Dataset, window, reason, expected cost (from CostSherlock), reviewed like any change."),
    ("It runs on a clone first.", "In pre-prod, compared with prod, before it touches prod."),
    ("It never moves a watermark.", "A backfill is its own run type; the normal schedule carries on untouched."),
    ("It runs when it is cheap.", "Outside the 06:00 to 07:30 peak, with its own budget."),
    ("It is announced.", "The changed gold windows are logged as a restatement and shown on the dashboards."),
]

SECRETS = [
    ("One home.", "AWS Secrets Manager holds every password and key reference; Databricks reads them through a Unity Catalog service credential or an IAM role (" + CHECK + "), never a copy."),
    ("Rotated without people.", "Database passwords rotate every 90 days automatically."),
    ("Never in Git.", "The shift-left checks block a pull request that contains a secret."),
    ("No long-lived keys.", "CI signs in with OIDC; people sign in through your identity provider; personal access tokens are off."),
]

TEAM = [
    ("Platform team", "About 6: a lead, three data engineers, a cloud engineer, an analytics engineer", "Runs the platform and the horizontal assets; on-call in a weekly rota of four"),
    ("Security and privacy", "Part-time, from your existing teams", "Reviews access quarterly, owns erasure and breach response"),
    ("Data owners", "Business heads (plant operations, quality, sales, finance)", "Decide access, sign off metrics and releases in their area"),
    ("Stewards", "One per source, about two hours a week", "Rules, quarantine reviews, suggested rules"),
    ("Data forum", "Owners, stewards and the platform lead, monthly", "Priorities, metric changes, the incident and cost trends. This is the 'centre of excellence' the testing page refers to"),
]

# ---------------------------------------------------------------- migration, sharing, ML
MIGRATION = [
    ("Glue jobs", "Rebuilt as metadata-driven pipelines, one subject at a time, each run in parallel with the old job for two weeks", "Counts and sums reconcile for two weeks; then the Glue job is switched off"),
    ("Redshift", "Kept for existing reports; new gold on Databricks; Redshift reads our tables as Iceberg (UniForm) or through Delta Sharing while reports move", "The last report has moved; then the cluster is shut down"),
    ("Glue Catalog and Lake Formation", "Unity Catalog is the one catalog for everything new; old Glue tables are read through catalog federation during the move (" + CHECK + ")", "No new grants are made in Lake Formation from day one"),
    ("QuickSight", "Existing reports repointed to the SQL warehouse; new ones on AI/BI", "Each report reads gold or metric views"),
    ("Athena", "Kept for small one-off queries on S3", "Nothing to migrate"),
]

MIGRATION_RULES = [
    ("Inventory first.", "Every job, table, report and its users, with an owner and a move-or-retire decision."),
    ("One subject at a time.", "Production first, then quality, then sales, so each move is small and can be undone."),
    ("Never write twice.", "During a move the old system reads from the new one, not both from the source."),
    ("Dates for switching off.", "Every old system has an agreed shut-down date, or it never goes."),
]

SHARING = [
    ("Car makers (OEMs)", "Quality and traceability of the tyres fitted to their cars, by batch and DOT code", "Delta Sharing (an open protocol, readable without Databricks) of a gold view, filtered to that car maker", "No personal data; contract and owner per share"),
    ("Dealers", "Their own sell-out, stock and claim status", "The existing dealer portal reads an API over gold, or a Databricks App", "Each dealer sees only their own rows"),
    ("Suppliers", "Quality results for the lots they delivered", "Delta Sharing", "Filtered to the supplier"),
    ("Auditors and regulators", "Evidence packs: access reviews, erasure log, release reports", "Exported on request", "Approved by the data owner"),
]

ML_ROWS = [
    ("Features", "Feature tables in gold (prod_gold.features), built and tested like any gold table"),
    ("Models", "Tracked with MLflow and registered in Unity Catalog, with the same owners and grants"),
    ("Serving", "Batch scoring for forecasts; Model Serving where an app needs an answer in seconds"),
    ("First use", "Weekly demand forecast per material and region; later, predicting press breakdowns from sensor history"),
    ("Checks", "Each model is evaluated against a held-out period before release and watched for drift after (" + CHECK + " for inference tables)"),
]

# ---------------------------------------------------------------- open decisions and the design test
OPEN = [
    ("Can serverless compute reach Aurora and the plant network privately?", "Decides whether the lander runs serverless or on classic compute", "Platform lead", "Before the crawl starts"),
    ("Do row filters hold through metric views, and can outside BI tools query them?", "The whole Genie and dashboard security rests on it", "Platform lead and analytics engineer, by test", "Crawl, week 2"),
    ("Are tag-based access policies (ABAC) available in Mumbai?", "If not, the deploy generates a mask per table from the same tags", "Platform lead", "Crawl, week 1"),
    ("Which route out of SAP?", "Licence and support terms decide it", "SAP team and procurement", "Before the walk phase"),
    ("What is the legal basis for EU personal data in India?", "Until decided, EU sources load without personal columns", "Legal team", "Before the first EU source"),
    ("Does Databricks run in Hyderabad (ap-south-2)?", "The recovery plan builds the workspace there. If not, the data copies stay in Hyderabad and compute is rebuilt in the nearest supported region, with legal sign-off for data leaving India", "Platform lead and legal team", "Before go-live"),
    ("Which personal-data detector reads German free text?", "Until decided, EU warranty notes are held out of bronze", "Privacy lead and platform lead", "Before the first EU source"),
    ("Is Aurora Global Database available in Hyderabad?", "Sets the metadata recovery point: seconds or one hour", "Platform lead", "Before go-live"),
    ("What are the DPDP Rules timelines for breach notice?", "Fills in the breach runbook", "Legal team", "Before go-live"),
    ("Can Genie be embedded and driven by API?", "Decides how much of the Conversation UI we build", "Product owner", "Walk phase"),
]

DESIGN_TEST = [
    ("A new EU plant's MES must reach OEE within a sprint", "Passes with gaps", "Passes", "EU network path, master data owners, onboarding checklist, EU legal basis"),
    ("SAP renames a column without warning", "Passes with gaps", "Passes", "Contract check fixed at silver; replay from landing, never re-extract from SAP; freshness shown on every metric"),
    ("A press goes silent for 3 hours on the night shift", "Fails", "Passes (round 2 fixed how OEE treats incomplete hours)", "Gold writes incomplete rows instead of stopping; a completeness measure; a silent-press alert; paging by tier"),
    ("A warranty file arrives two days late", "Passes with gaps", "Passes", "Restatements logged and shown; freshness alerts grouped by date; warranty tier and target stated"),
    ("A consumer in Germany asks to be erased", "Fails", "Passes once two open decisions are settled: the legal basis and a German-capable detector", "Vault in its own catalog; landing purged in a day; recovery copies erased; suppression list; free text scanned; no restore across an erasure"),
    ("Scrap rate is redefined to exclude trial batches", "Passes with gaps", "Passes", "One source for scrap rate; batch type in gold; definition changes dated; owner updates benchmarks"),
    ("A release is wrong for one plant", "Passes with gaps", "Passes", "Recompute that plant only; canary for a full day; business banner; platform lead decides"),
    ("The Mumbai region is down for a day", "Fails", "Passes once Databricks in Hyderabad is confirmed", "Recovery per layer with targets; security deployed before readers; metadata database copied; network ready; who declares"),
    ("A plant manager asks Genie for all plants", "Passes with gaps", "Passes, once the metric-view test is green", "Row security as a release test; 'for your plant' wording; AI log restricted"),
    ("An engineer joins, a recipe keeper leaves", "Passes with gaps", "Passes", "Owners checked against the identity provider nightly; deputies; personal access tokens off; pre-prod sees results only"),
    ("The bill doubles overnight", "Passes with gaps", "Passes", "Cost-jump alert on the whole account; runbook to pause and shrink within the hour; cost as a cause"),
    ("An agent's diagnosis is wrong", "Passes with gaps", "Passes", "A person confirms the diagnosis; proof on a pre-prod clone; full gates for limits and watermarks; hit rate tracked"),
]


# ---------------------------------------------------------------- foundation (tier T0)
FOUNDATION = [
    ("AWS accounts", "One AWS account per environment: dev, pre-prod, prod. All three sit under your AWS Organization and send logs to your central security and log accounts.",
     "A mistake in dev cannot touch prod, permissions stay simple, and each environment's bill is separate."),
    ("Region", "Mumbai (ap-south-1) is home. Hyderabad (ap-south-2) holds the recovery copy.",
     "Both are in India, so recovery does not move data out of the country. The full recovery plan is in the running-it section."),
    ("EU plants", "Plant and production data from EU plants comes to Mumbai too. Personal data about EU people (staff, dealers, consumers) moves only under the legal basis your legal team picks, and is tokenised on arrival.",
     "Press readings and scrap counts are not personal data. One platform costs half of two. A separate EU platform (Frankfurt) only if your legal team requires it."),
    ("Databricks workspaces", "Three workspaces (dev, pre-prod, prod) on one Unity Catalog. Each catalog is bound to its workspace, so prod tables are visible only in prod.",
     "Databricks allows one Unity Catalog per region, so the three share it; binding keeps the environments apart."),
    ("Network", "No public IP addresses anywhere. Classic compute runs in your own VPC, across two availability zones; serverless compute runs in Databricks' serverless plane in the same region and reaches your data over private connections. Databricks is reached through PrivateLink, never the open internet.",
     "This is the first thing a manufacturer's security team asks. Two zones keep the platform up if one data centre fails."),
    ("Storage and keys", "One S3 bucket and one KMS key per catalog. A landing bucket per environment. Recipes get their own bucket and key with the tightest access.",
     "Recipes are the crown jewels: with their own key, revoking all access is one action, and every use of the key is logged."),
    ("Compute", "Serverless by default for SQL, jobs and pipelines. Classic compute (clusters inside your VPC) only where a job must reach a private system that serverless cannot yet reach.",
     "Starts in seconds, nothing to patch or size. Serverless private reach on AWS: " + CHECK + "."),
    ("Sign-in and identity", "People sign in through your existing identity provider; groups sync to Databricks automatically (SCIM). Jobs run as service principals, never as a person.",
     "When someone leaves, one change removes all their access, and no job breaks because its owner left."),
    ("How it is built", "Terraform builds all of the above from Git (AWS and Databricks providers). Pipelines are deployed separately with Databricks Asset Bundles.",
     "The whole foundation can be rebuilt the same way in every environment, and in Hyderabad after a disaster."),
]

ASSUMPTIONS = [
    ("Is there already an AWS landing zone (Control Tower or similar)?", "Yes, with central security and log-archive accounts", "If not, we add a minimal one first: an Organization, CloudTrail to a log account, guardrails (SCPs). About a week."),
    ("Which identity provider?", "Microsoft Entra ID", "Okta or another SAML / OIDC provider works the same way; only the Terraform settings change."),
    ("How do plants reach AWS?", "Direct Connect from the head office, Indian plants on the company network (MPLS or SD-WAN); EU plants through a site-to-site VPN to the Mumbai Transit Gateway", "With only VPN, sensor streaming is sized smaller and the plant historian is pulled in batches."),
    ("Where does SAP run?", "SAP S/4HANA on AWS (RISE) or in a data centre linked to AWS", "The mover changes (see the ingestion table); the foundation does not."),
    ("Must EU data stay in the EU?", "Not for plant data; personal data under Standard Contractual Clauses", "If yes for everything, add a fourth workspace in Frankfurt on its own Unity Catalog, and share gold tables back with Delta Sharing."),
]

BUCKETS = [
    ("landing-&lt;env&gt;", "Raw files from the movers, as they arrived", "Environment key", "Files deleted 30 days after they reach bronze; versioning on, old versions expire with them"),
    ("landing-pii-&lt;env&gt;", "Raw files from sources with personal data", "Its own key", "Deleted within a day of being loaded by an hourly purge; held files kept up to 7 days; old versions expire with them"),
    ("&lt;env&gt;-pii-vault", "The token vault and the suppression list", "Its own key; only privacy case handlers", "Every lookup logged"),
    ("&lt;env&gt;-bronze, -silver, -gold, -semantic, -ops", "The managed tables of each catalog", "One key per catalog", "Delta handles history; old versions cleaned by VACUUM after 30 days"),
    ("&lt;env&gt;-restricted", "Recipes and compound formulations", "Its own key; only the recipe group can use it", "Access logged and reviewed monthly"),
    ("audit-&lt;env&gt;", "Copies of audit and config change logs", "Environment key", "Object Lock: cannot be changed or deleted for 7 years"),
    ("dr-* (Hyderabad)", "Recovery copies: bronze, silver, gold, restricted and the vault", "Keys in Hyderabad, same groups", "See the recovery plan; erasures are applied here too; restore tested twice a year"),
]

BINDING = [
    ("dev_* catalogs", "Read and write", "Not visible", "Not visible"),
    ("preprod_* catalogs", "Not visible", "CI writes; engineers read the results schemas only, not the clones", "Not visible"),
    ("prod_bronze, prod_silver, prod_gold, prod_semantic", "Not visible", "Read only, by the CI service principal (for real-data tests and shallow clones); people in pre-prod see the results, not the prod rows", "Jobs write; people read through grants"),
    ("prod_restricted", "Not visible", "Not visible", "Recipe group only"),
    ("prod_pii_vault", "Not visible", "Not visible", "Privacy case handlers only"),
    ("prod_ops", "Not visible", "Read only", "Pipelines write; everyone on the platform reads, except the ai_log schema"),
]

TF_TREE = """foundation/                     # Terraform, one folder per layer, applied in this order
  1-org/          accounts, guardrails (SCPs), CloudTrail to the log account
  2-network/      VPC per env, private subnets in 2 zones, endpoints (S3, STS, Kinesis), PrivateLink
  3-storage/      buckets and KMS keys per catalog, IAM roles Databricks may assume
  4-databricks/   workspaces, metastore, catalogs, workspace bindings, external locations
  5-identity/     service principals, catalog-level grants (groups come from your identity provider)
  envs/           dev.tfvars, preprod.tfvars, prod.tfvars, dr.tfvars   # the only differences"""


def foundation_map():
    b = []
    a = b.append
    a(rect(20, 20, 170, 58, "#FFF4D9") + tx(36, 44, "Your login system", 14.5) + tx(36, 64, "Entra ID · groups synced", 11.5, fill="#555"))
    a(arr(190, 49, 220, 49))
    a(rect(220, 16, 700, 66, "#E6EAF7") + tx(570, 42, "Databricks account · Unity Catalog in Mumbai", 16, "middle")
      + tx(570, 64, "users and groups · system tables for audit, billing, lineage", 12, "middle", fill="#555"))
    envs = [("dev", "#E0F1F7"), ("pre-prod", "#FFF4D9"), ("prod", "#E6F4EC")]
    for i, (e, f) in enumerate(envs):
        x = 220 + i * 240
        a(arr(x + 110, 82, x + 110, 120, dash=True))
        a(tx(x + 118, 106, "PrivateLink", 11, fill="#555"))
        a(rect(x, 120, 220, 290, f))
        a(tx(x + 14, 144, f"AWS account: {e}", 15, weight="700"))
        a(rect(x + 12, 156, 196, 92, "#fff", r=10) + tx(x + 24, 178, "VPC, 2 zones, no public IPs", 12.5)
          + tx(x + 24, 198, "compute (classic, if needed)", 11.5, fill="#555") + tx(x + 24, 216, "Aurora metadata database", 11.5, fill="#555")
          + tx(x + 24, 234, "endpoints: S3, STS, Kinesis", 11.5, fill="#555"))
        a(rect(x + 12, 258, 196, 62, "#fff", r=10) + tx(x + 24, 282, f"Workspace: {e}", 13.5)
          + tx(x + 24, 302, f"sees {e.replace('-', '')}_* catalogs only", 11.5, fill="#555"))
        a(rect(x + 12, 330, 196, 68, "#fff", r=10) + tx(x + 24, 352, "S3: landing + a bucket", 12.5)
          + tx(x + 24, 370, "per catalog, each with", 12.5) + tx(x + 24, 388, "its own KMS key", 12.5))
    a(f'<path d="M700,300 C690,300 690,300 668,300" fill="none" stroke="{INK}" stroke-width="1.5" stroke-dasharray="4 3" marker-end="url(#ahx)"/>')
    a(tx(684, 430, "pre-prod reads prod, read only", 11.5, "middle", fill="#555"))
    a(rect(20, 180, 170, 92, "#F4F4F2") + tx(36, 204, "Plants + SAP", 14.5) + tx(36, 224, "Direct Connect", 11.5, fill="#555")
      + tx(36, 242, "to every VPC through", 11.5, fill="#555") + tx(36, 260, "a Transit Gateway", 11.5, fill="#555"))
    a(arr(190, 226, 220, 226))
    a(arr(920, 265, 950, 265))
    a(rect(950, 200, 170, 130, "#F8E6EF", dash=True) + tx(966, 224, "Hyderabad (recovery)", 14) + tx(966, 246, "bronze to gold, recipes, vault", 11.5, fill="#555")
      + tx(966, 264, "replicated and cloned", 11.5, fill="#555") + tx(966, 286, "workspace rebuilt", 11.5, fill="#555") + tx(966, 304, "from Terraform", 11.5, fill="#555"))
    return svg(1140, 445, "".join(b), "The foundation: your login system syncs groups to one Databricks account in Mumbai with one Unity Catalog. Below it, three AWS accounts (dev, pre-prod, prod), each with a private VPC in two zones, its own workspace that sees only its own catalogs, and S3 buckets with a key per catalog, reached over PrivateLink. Plants and SAP connect over Direct Connect. Pre-prod reads prod read-only. Prod data from bronze to gold, the recipes and the vault are copied to Hyderabad for recovery.")


# ---------------------------------------------------------------- data quality and profiling (tier T3)
DQ_ENGINES = [
    ("DQX (Databricks Labs)", "Every PySpark step: the lander, the gold window-recompute jobs, and any silver table not built as a Declarative Pipeline",
     "Pursue", "Rules as data (YAML or a table), row-level and table-level checks, splits good and bad rows, has a profiler that suggests rules. Open source, so no lock-in. Labs project: " + CHECK + " for support terms."),
    ("Lakeflow expectations", "Inside Declarative Pipelines (silver and gold tables built that way)",
     "Pursue", "The default for silver and gold built as Declarative Pipelines. Native to the pipeline, results land in the pipeline event log, no extra code. We generate them from the same rules, so a rule is written once."),
    ("Plain Spark SQL", "Fallback: any rule the two above cannot express, such as a reconcile across two tables",
     "Pursue", "A predicate in SQL: rows where it is true are the bad rows. This is how the framework's rules already work today; DQX is not yet wired into the framework."),
    ("Great Expectations, Soda", "Not used", "Drop", "Good tools, but a second rule language and a second results store. DQX plus expectations already cover the need inside Databricks."),
    ("AWS Glue Data Quality", "Only if a team already uses it on Glue jobs", "Drop", "Runs outside Databricks; results would not join our run id without extra work."),
]

DQ_HOPS = [
    ("Landing to bronze", "File checks only: readable, not empty, row count against the source's count. New or unexpected columns are kept (rescued data)",
     "Stop on an unreadable or empty file; bronze keeps everything else as it arrived, so it can be replayed"),
    ("Bronze to silver", "First the contract check (promised columns and types), then row rules: not null, ranges, allowed values, keys unique, references exist (press, plant, material)",
     "Bad rows go to the silver table's quarantine table; good rows carry on. Stop only if the bad share passes a limit"),
    ("Silver to gold", "Table rules: totals reconcile with silver, share of 'unknown' members under a limit, and every expected press-hour present",
     "Stop if totals do not reconcile: a wrong gold number is worse than a late one. A missing press-hour does not stop the load: it is written as an incomplete row, which OEE leaves out of both the top and the bottom of every part, so the number is on time, not skewed, and says how complete it is"),
    ("Gold to semantic", "Metric checks: OEE between 0 and 100%, scrap rate against last month's band, completeness of the period shown",
     "Warn, and flag the metric on the dashboard; every dashboard and Genie answer shows how complete and how fresh the data is"),
]

DQ_TABLES = [
    ("config.dq_rule", "One row per rule: dataset, layer, the check, when it runs, severity, action (warn, quarantine, stop), who wrote it, whether it was suggested by the profiler",
     "The loader, from YAML in Git"),
    ("runtime.dq_result", "One row per rule per run: passed or failed, failing row count, action taken, time taken",
     "Pipelines"),
    ("runtime.dq_violation", "Keys of a sample of failing rows (capped, 100 by default), for the steward to look at",
     "Pipelines"),
    ("runtime.dq_profile", "One row per column per profiled run: null share, distinct count, min, max, mean, top values, and the change from the last profile",
     "Pipelines"),
    ("&lt;table&gt;_quarantine (Delta)", "The failing rows themselves, next to each silver table, with the run id and the rule id",
     "Pipelines; stewards review weekly"),
]

PROFILE_KEYS = [
    ("profile.enabled", "true", "Turn profiling on or off for this dataset"),
    ("profile.when", "every_run, daily, weekly, on_change", "How often; daily is the default for silver, every run for tier-1 gold"),
    ("profile.scope", "new_rows, full_table", "Profile only what this run loaded, or the whole table"),
    ("profile.sample_pct", "10", "Share of rows to read; large sensor tables use a sample"),
    ("profile.columns", "all, or a list", "Which columns; recipe columns are always left out"),
    ("profile.suggest_rules", "true", "Let the profiler propose new rules (they are never switched on by themselves)"),
]

PROFILERS = [
    ("DQX profiler", "Every profiled dataset", "Measures columns and proposes candidate rules. Runs inside our step, so its output carries our run id."),
    ("Lakehouse Monitoring (data profiling)", "Tier-1 gold tables only (OEE, scrap, warranty claims)", "Managed profiles and drift over time, with its own dashboard. Costs compute on every refresh, so not everywhere. Name and features: " + CHECK + "."),
    ("Unity Catalog data classification", "Every catalog except restricted", "Finds columns that look like personal data (names, phone numbers, emails of dealers and fleet drivers) and suggests PII tags. " + CHECK.capitalize() + "."),
]

DQ_RULES_YAML = """# config/dq/silver_mes_press_reading.yaml  (one file per dataset and layer)
dataset: mes.press_reading
layer: silver
rules:
  - name: press_known
    check: press_id IN (SELECT press_id FROM ${silver}.mes.press)   # ${silver} = dev_silver, preprod_silver or prod_silver
    severity: error
    action: quarantine
  - name: cure_temp_in_range
    check: cure_temp_c BETWEEN 120 AND 220        # example range; the plant engineer owns it
    severity: error
    action: quarantine
  - name: not_in_future
    check: reading_ts <= current_timestamp() + INTERVAL 5 MINUTES
    severity: warning
    action: warn
  - name: bad_share_limit                         # table-level: stop if too much is bad
    check: quarantined_pct <= 2
    severity: error
    action: stop
profile:
  enabled: true
  when: daily
  scope: new_rows
  sample_pct: 10
  columns: all
  suggest_rules: true"""

DQ_STEPS = [
    ("Profile", "The profiler measures each column of new data and writes runtime.dq_profile with the run id."),
    ("Compare", "Each profile is compared with the last one. A big change (nulls jump from 0.1% to 8%, a new value in plant_code) raises a warning on the ops dashboard."),
    ("Suggest", "If suggest_rules is on, candidate rules are written as a pull request to the rules YAML, marked as suggested. They are never switched on automatically."),
    ("Approve", "The data steward for that source reviews the pull request, adjusts the limits and merges. The loader puts the rule in config.dq_rule."),
    ("Enforce", "From the next run the rule is checked at its hop; the result lands in runtime.dq_result, failing rows in quarantine."),
    ("Review", "Every week the steward looks at the quarantine tables, fixes the source or the rule, and releases or drops the parked rows."),
]


def dq_flow():
    b = []
    a = b.append
    a(rect(20, 20, 200, 64, "#FFF4D9") + tx(36, 46, "Rules YAML in Git", 15) + tx(36, 68, "written by stewards", 12, fill="#555"))
    a(arr(220, 52, 280, 52))
    a(rect(280, 20, 200, 64, "#F4F4F2") + tx(296, 46, "config.dq_rule", 15) + tx(296, 68, "loaded and validated", 12, fill="#555"))
    a(arr(380, 84, 380, 130))
    hops = [("bronze", "#F3E3D3"), ("silver", "#E6E6E6"), ("gold", "#F7E7B4")]
    for i, (h, f) in enumerate(hops):
        x = 200 + i * 130
        a(rect(x, 130, 110, 50, f) + tx(x + 55, 160, h, 15, "middle"))
        if i:
            a(arr(x - 20, 155, x, 155))
    a(tx(395, 205, "rules run at every hop (DQX, expectations, SQL)", 12.5, "middle", fill="#555"))
    outs = [("Pass", "row carries on", "#E6F4EC"), ("Warn", "logged, shown", "#FFF4D9"), ("Quarantine", "row parked", "#F8E6EF"), ("Stop", "load held, owner told", "#F8D7DA")]
    for i, (t, sub, f) in enumerate(outs):
        x = 100 + i * 150
        a(arr(395, 215, x + 67, 250))
        a(rect(x, 250, 135, 54, f) + tx(x + 67, 274, t, 14.5, "middle") + tx(x + 67, 293, sub, 11.5, "middle", fill="#555"))
    a(arr(395, 304, 395, 340))
    a(rect(280, 340, 230, 54, "#E9EDF8") + tx(395, 364, "runtime.dq_result", 14.5, "middle") + tx(395, 383, "+ run id, to the ops dashboard", 11.5, "middle", fill="#555"))
    # profiling loop on the right
    a(rect(700, 130, 210, 56, "#E0F1F7") + tx(716, 154, "Profiler", 15) + tx(716, 174, "DQX, Lakehouse Monitoring", 11.5, fill="#555"))
    a(arr(560, 155, 700, 158, dash=True))
    a(arr(805, 186, 805, 250))
    a(rect(700, 250, 210, 56, "#E0F1F7") + tx(716, 274, "runtime.dq_profile", 14.5) + tx(716, 294, "change vs last profile", 11.5, fill="#555"))
    a(arr(910, 278, 960, 278))
    a(rect(960, 230, 160, 96, "#fff", dash=True) + tx(1040, 258, "Suggested rules", 14, "middle") + tx(1040, 278, "pull request", 12, "middle")
      + tx(1040, 298, "steward approves", 12, "middle"))
    a(f'<path d="M1040,230 C1040,60 700,52 482,52" fill="none" stroke="{INK}" stroke-width="1.5" stroke-dasharray="4 3" marker-end="url(#ahx)"/>')
    return svg(1140, 410, "".join(b), "Rules written in Git are loaded into config.dq_rule and run at bronze, silver and gold; each check ends in pass, warn, quarantine or stop, and the result is written to runtime.dq_result with the run id. Beside it, the profiler measures the data, writes runtime.dq_profile, and proposes rules as a pull request that a steward approves back into Git.")


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
    return svg(1070, 300, "".join(b), "Four sources of signals, plus the targets from the metadata, flow into one ops gold layer, which feeds the ops dashboard, the alerts and an ops Genie space; alerts go to the named owner with a runbook.")


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
    ("Our runtime schema (Aurora)", "Every run, step, error, quality result and watermark, with the run id", "Copied into prod_ops every 15 minutes (see below)"),
    ("Databricks system tables", "Job and task runs, billing (DBUs and cost), lineage, audit of who read what", "Already in Unity Catalog; joined on the job run id"),
    ("Lakehouse Monitoring / data profiling", "Profiles and drift of key tables: nulls, distinct counts, distributions", "Check current status and name; behind our profiling port"),
    ("Amazon CloudWatch", "Health of AWS movers and the database: DMS lag, AppFlow failures, SiteWise ingestion, Aurora load", "CloudWatch alarms for the AWS side; a metric stream lands in prod_ops every 5 minutes"),
    ("Data contracts and freshness targets", "What each data product promises: by when, how complete, owner", "From dataset_config; the dashboard checks against them"),
]

OPS_PANELS = [
    ("Runs today", "Succeeded, failed, running, skipped; drill to the failing task", "System tables: job and task run timelines", "Ops / on-call"),
    ("Run time", "Duration against the usual 95th percentile; slow runs before they become late runs", "System tables: job run timeline", "Platform engineers"),
    ("Cost", "Cost per job, warehouse and cluster against budget", "System tables: billing usage × list prices (CostSherlock adds cost per data product)", "Platform lead, finance"),
    ("Compute and queries", "Busy or idle clusters, slow SQL queries, who ran what", "System tables: compute, query history, audit", "Platform engineers"),
    ("Lineage", "What feeds each table and what breaks if it fails", "System tables: table and column lineage", "Data engineers, stewards"),
    ("Failures by cause", "Source down, schema changed, bad data, our bug; trend over 7 and 30 days", "Mixed: failure state from system tables, the cause class from our error_log", "Platform lead"),
    ("Freshness against target", "Each data product green, amber or red against its promised time", "Ours: targets in dataset_config, judged against each input's bookmark (input_watermark), not the last run", "Data product owners, business"),
    ("Quality", "Failing rules, rows parked in quarantine, by dataset and plant", "Ours: dq_result (plus pipeline expectation events)", "Data quality lead, stewards"),
    ("Volumes", "Rows in and out against the usual range; sudden drops are the early warning", "Ours: run_log", "Ops"),
    ("Watermark lag", "How far behind each incremental source is", "Ours: watermark", "Ops"),
    ("AWS movers", "DMS replication lag, AppFlow flow failures, sensor stream delay", "Amazon CloudWatch", "Ops"),
]

ALERTS = [
    ("Pipeline failed after retries", "run_log status failed and retries used up", "High", "Teams/Slack + email; pager at night for tier-1 data products"),
    ("Data product late", "Freshness past the promised time in dataset_config", "High for tier 1, Medium otherwise", "Owner of the data product, on-call"),
    ("Quality rule set to stop failed", "dq_result failed on a rule whose action is stop", "High", "Data quality lead and steward; the load is held"),
    ("Volume out of range", "Rows written outside the usual band for that dataset and weekday; for streams, per 15-minute window", "Medium", "On-call; often the first sign of a source problem"),
    ("A press went silent", "A press in the press master sent no reading for 30 minutes during a planned shift", "High (OEE is tier 1, so it pages)", "Plant maintenance and on-call; one silent press is too small to move a volume band, so it gets its own check"),
    ("Schema changed at source", "Contract check finds a new, missing or retyped column", "Medium", "The source owner named in the contract; silver is protected by the contract"),
    ("Run much slower than usual", "Duration above 2 × the usual p95", "Low", "Platform engineers, next working day"),
    ("Cost over budget", "Daily or monthly cost per pipeline, per SQL warehouse or for the AWS side above its budget", "Medium", "Platform lead and finance (CostSherlock)"),
    ("Cost jump", "Yesterday's total cost (Databricks and AWS) more than 1.5 × its 7-day average", "High", "Platform lead; the runbook can pause tier-3 schedules and shrink warehouses within the hour"),
    ("Source mover unhealthy", "CloudWatch alarm: DMS lag, AppFlow failure, Aurora CPU or storage", "High", "On-call through Amazon SNS"),
]

ALERT_RULES = [
    ("Every alert has an owner and a deputy", "Both come from dataset_config. A nightly check compares every named owner with your identity provider; a leaver is flagged to the data owner the next morning."),
    ("Every alert has a runbook", "A link in the message to what to check first and how to re-run safely."),
    ("One alert per incident", "Repeats are grouped by run id and dataset, so a source outage pages once, not 40 times."),
    ("Severity follows the data product tier", "Paging: a High alert on a tier-1 product pages at any hour; on tier 2 it pages during plant hours; tier 3 and every Medium or Low alert wait for working hours. OEE for the morning meeting is tier 1; warranty claims are tier 2, due 09:00 daily."),
    ("Every alert is reviewed", "A noisy alert is tuned or removed within a week; an alert nobody acts on is deleted."),
]

SLOS = [
    ("Freshness", "Data product ready by its promised time", "OEE per plant by 06:30 for the morning meeting, on 99% of days"),
    ("Success", "Runs that succeed without a person stepping in", "98% of scheduled runs per week"),
    ("Quality", "Rows passing every rule", "99.5% of rows in silver; zero failures on stop rules"),
    ("Recovery from a failed run", "Time from failure to data back on time", "Under 2 hours for tier-1 data products (losing a region is covered by the recovery plan, not this target)"),
]


OPS_LANDING = [
    ("Our runtime schema (Aurora)", "A small job reads it through Lakehouse Federation every 15 minutes and MERGEs new rows into prod_ops", "15 minutes",
     "Dashboards never query Aurora directly, so a busy dashboard can never slow the pipelines that write to it"),
    ("Databricks system tables", "Read in place; nothing to copy", "Minutes to an hour, table by table (" + CHECK + ")",
     "Kept by Databricks for a limited time; ops gold keeps 13 months of the summaries we need"),
    ("Amazon CloudWatch metrics", "A metric stream sends DMS, AppFlow, Kinesis, SiteWise and Aurora metrics through Firehose to S3; Auto Loader reads them into prod_ops", "About 5 minutes",
     "Only the metrics we name are streamed, so the cost stays small"),
    ("CloudWatch alarms", "Alarm state changes go through EventBridge to the same S3 path", "Seconds to minutes", "So AWS-side alarms join the same incident list as Databricks alerts"),
    ("Pipeline event logs (Declarative Pipelines)", "Read from each pipeline's event log: expectation results, flow progress", "Per update", "Expectation results merge into the same quality fact as DQX results"),
    ("Spark driver and executor logs", "Not loaded. Kept in S3 for 30 days for debugging", "-", "Our framework writes structured events to the runtime tables; free-text logs are for engineers only"),
]

OPS_MODEL = [
    ("ops.dim_dataset", "One row per dataset", "Owner, tier, freshness target, volume band, budget, mover id; from the config schema"),
    ("ops.fct_run", "One row per dataset run", "Our run_log joined to the Databricks job run and its cost: status, timings, rows, cause of failure, cost, config fingerprint"),
    ("ops.fct_step", "One row per step of a run", "Land, bronze, silver, gold: timings and rows in and out"),
    ("ops.fct_quality", "One row per rule per run", "DQX results and pipeline expectation results together"),
    ("ops.fct_freshness", "One row per data product per day", "Promised time, actual time, met or missed, minutes late"),
    ("ops.fct_mover_health", "One row per mover per 5 minutes", "DMS lag, AppFlow failures, stream delay, Aurora load, from CloudWatch"),
    ("ops.fct_incident", "One row per incident", "Opened, owner, severity, cause class, acknowledged, resolved, linked runs and alerts, agent diagnosis"),
    ("ops.fct_access", "One row per read of sensitive data", "From audit system tables and CloudTrail; feeds the quarterly access review"),
]

INCIDENT_RULES = [
    ("Alerts open incidents; incidents are what people work.", "Several alerts about one cause (a source down, forty datasets late) group into one incident by source and time window. Freshness alerts, which have no run, group by dataset and expected date."),
    ("Every incident has an owner from the metadata.", "The data product's owner and the source's engineer, never a shared mailbox."),
    ("If business users saw a wrong or late number, tell them.", "A banner on the affected dashboards and a note to the metric owner, from the incident, until it is closed. Recomputed history is logged as a restatement in ops and shown the same way."),
    ("Close with a cause class.", "Source down, schema change, bad data, our bug, platform, capacity, cost. The trend of causes tells us what to fix next."),
    ("Tier-1 incidents get a short review.", "What happened, why the tests did not catch it, and the new test or rule that will. Each review adds a DataTwin fault."),
]


def ops_joins():
    b = []
    a = b.append
    boxes = [(20, 30, "runtime.run_log (ours)", ["run_id, dataset_id", "job_run_id"], "#E6F4EC"),
             (420, 30, "system.lakeflow job runs", ["job_id, run_id", "status, timings"], "#E6EAF7"),
             (820, 30, "system.billing.usage", ["usage_metadata.job_run_id", "DBUs, cost"], "#E6EAF7"),
             (20, 200, "config (dataset + source)", ["dataset_id, owner, tier", "mover_id, set per source"], "#F4F4F2"),
             (420, 200, "CloudWatch (via S3)", ["dimension: task or flow id", "lag, failures"], "#FFF4D9"),
             (820, 200, "runtime.dq_result + events", ["run_id, rule_id", "passed, rows failed"], "#E6F4EC")]
    for x, y, t, lines, f in boxes:
        a(rect(x, y, 300, 86, f) + tx(x + 16, y + 28, t, 15) + "".join(tx(x + 16, y + 52 + k * 19, ln, 12.5, fill="#555") for k, ln in enumerate(lines)))
    a(arr(320, 73, 420, 73)); a(tx(370, 64, "job_run_id", 11.5, "middle"))
    a(arr(720, 73, 820, 73)); a(tx(770, 64, "job_run_id", 11.5, "middle"))
    a(arr(170, 116, 170, 200)); a(tx(180, 162, "dataset_id", 11.5))
    a(arr(320, 243, 420, 243)); a(tx(370, 234, "mover_id", 11.5, "middle"))
    a(f'<path d="M320,108 C560,165 700,165 820,232" fill="none" stroke="{INK}" stroke-width="1.5" marker-end="url(#ahx)"/>')
    a(tx(560, 172, "run_id", 11.5, "middle"))
    a(tx(560, 320, "Four keys join everything: run_id, job_run_id, dataset_id and the mover id. Our framework writes all four into its own tables.", 13.5, "middle"))
    return svg(1140, 335, "".join(b), "How the ops tables join: our run_log carries the Databricks job run id, which joins job run system tables and billing usage; dataset_id joins the config, whose mover id joins CloudWatch metrics; run_id joins the quality results.")


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


# ---------------------------------------------------------------- testing and data contracts
def gates():
    b = []
    a = b.append
    G = [("Laptop", "pre-commit", ["shift-left checks", "purity check", "unit tests"], "#F4F4F2", "seconds"),
         ("Pull request", "CI", ["full shift-left scan", "unit + coverage", "contract checks"], "#E9EDF8", "minutes"),
         ("Dev", "after merge", ["one test per hop", "end to end, synthetic", "fresh schema"], "#E6F4EC", "15–30 min"),
         ("DataTwin", "nightly", ["pretend plant, 30 days", "planted faults", "caught? held?"], "#FFF4D9", "an hour"),
         ("Pre-production", "before release", ["real data (clones)", "parallel run vs prod", "profile compare"], "#FBE9DD", "an hour or two"),
         ("Production", "every run", ["contract check", "quality rules", "freshness alerts"], "#F8E6EF", "always on")]
    for i, (t, when, lines, f, dur) in enumerate(G):
        x = 14 + i * 176
        a(rect(x, 30, 160, 186, f) + tx(x + 80, 60, t, 17, "middle") + tx(x + 80, 80, when, 12, "middle", fill="#555"))
        for k, ln in enumerate(lines):
            a(tx(x + 12, 112 + k * 24, "· " + ln, 12))
        a(tx(x + 80, 204, dur, 12, "middle", fill="#555"))
        if i < 5:
            a(arr(x + 160, 122, x + 176, 122))
    a(tx(536, 250, "cheapest and fastest on the left · a problem caught one gate earlier costs a fraction to fix", 14, "middle"))
    return svg(1072, 262, "".join(b), "Six gates from laptop to production: shift-left checks and unit tests, pull request checks, per-hop integration in dev, a DataTwin run with planted faults, a pre-production run on real data compared with production, and always-on checks in production.")


TEST_LAYERS = [
    ("Shift-left checks", "Problems found by reading the code, before it runs: Python and PySpark anti-patterns, SQL injection, secrets, collect() on big data, cartesian joins, missing keys in MERGE, costly job settings, metric view mistakes",
     "Our shift-left bundle (built: 131 checks specified; caught 88 of 101 planted problems on a sample project with no false alarms) on Ruff, sqlfluff and dbt-bouncer", "Laptop and pull request"),
    ("Unit tests", "Each transformation as a pure function, tested table-driven: a table of input rows and expected output rows per case (SCD2 new, changed, unchanged, deleted; duplicates; late rows; time zones)",
     "pytest + local Spark and Delta (no cluster); the shift-left test kit for SCD2 and idempotency", "Laptop and pull request"),
    ("Contract tests", "Each contract is valid, and a change does not break consumers (a removed column, a narrowed type, a renamed key)",
     "ODCS schema validation + a breaking-change diff against the last released version", "Pull request"),
    ("Integration tests", "One slice end to end on real Databricks: lander, silver with SCD2, gold, metric view; run twice to prove re-runs change nothing; reconciliation counts and sums agree",
     "Databricks Asset Bundles deploy to the dev workspace on a fresh schema per run; small fixed sample files in S3", "After merge, in dev"),
    ("DataTwin", "A pretend plant and business that produce data for 30 simulated days with faults planted on purpose; checks that the platform caught each one, held bad data back, and every number is accounted for",
     "DataTwin (designed; the DataTwin Studio and Problem Lab are built and run on real Spark and Delta)", "Nightly in dev, and before each release in pre-prod"),
    ("Pre-production run", "The release on real data: shallow clones of prod, a parallel run against prod with every difference explained, profiles compared, Genie benchmarks per role",
     "The pre-prod workspace and the CI service principal", "Every release"),
    ("Production checks", "Contract check at silver, quality rules with warn / quarantine / stop, freshness and volume alerts",
     "Lakeflow expectations or DQX behind our quality port; rules from config.dq_rule", "Every run"),
]

TWIN_FAULTS = [
    ("SAP sends the same delivery twice", "No duplicate in silver; sales not doubled in gold"),
    ("MES adds a column and renames another", "Contract check stops it at silver; alert to the MES owner; gold untouched"),
    ("A press sensor goes silent for 3 hours", "The silent-press alert fires and pages; OEE is on time, marked incomplete, and neither too high nor too low"),
    ("The warranty file arrives a day late", "Freshness alert; the late rows land in the right day when they arrive"),
    ("A dealer's master record changes twice in a day", "SCD2 keeps both versions with correct dates"),
    ("Daylight saving at the plant in Europe", "No lost or doubled hour in hourly scrap"),
    ("A job dies halfway", "Watermark not moved; the re-run loads the same window once"),
]

CONTRACT_NEED = [
    ("At sources we do not control (SAP, MES, quality LIMS, dealer DMS)", "Yes", "Their teams change systems on their own timetable; a contract turns a silent break into a clear alert with an owner."),
    ("At data products other teams use (OEE, scrap rate, warranty claims)", "Yes", "Consumers need to know the columns, the meaning, how fresh and who to call; it is also what Genie and dashboards rely on."),
    ("Between our own internal layers (bronze to silver to gold)", "No", "Our tests and quality rules already cover them; a contract there is paperwork."),
    ("A full contract platform or marketplace tool", "Not now", "YAML in Git plus the checks we already run is enough to start; revisit when there are dozens of producing teams."),
]

CONTRACT_PARTS = [
    ("Schema", "Columns, types, keys, which may be empty", "Contract check at silver; breaking-change diff in pull requests"),
    ("Quality", "Rules such as 'scrap quantity is never negative'", "The same rules run as quality checks"),
    ("Freshness and volume", "Ready by 06:00, between 40k and 60k rows a day", "Freshness and volume alerts"),
    ("Meaning and owner", "What a column means; the producing and consuming owners", "Unity Catalog comments and tags; alert routing"),
    ("Privacy", "Which columns hold personal data or recipe IP", "Unity Catalog tags, column masks and restricted catalogs"),
    ("Version", "Major version for breaking changes, with notice to consumers", "Pull request review; consumers named in the contract approve"),
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
    test_table = table(["Layer", "What it proves", "Built with", "Runs"], TEST_LAYERS)
    twin_table = table(["Fault planted in the pretend plant", "The platform passes if"], TWIN_FAULTS)
    need_table = table(["Where", "Contract?", "Why"], CONTRACT_NEED)
    parts_table = table(["Part of the contract", "Example", "Enforced by"], CONTRACT_PARTS)
    adf_table = table(["Azure Data Factory part", "On AWS", "On Databricks"], ADF_MAP)
    silver_steps = "".join(f'<div class="rule"><b class="n">{i + 1}</b><div><b>{E(t)}</b> {E(d)}</div></div>' for i, (t, d) in enumerate(SILVER_STEPS))
    gold_dec_table = table(["Choice", "Our pick", "Verdict", "Why"], GOLD_DECISIONS)
    bus_rows = [(f, g) + tuple("✓" if c == "1" else "" for c in m) for f, g, m in BUS_MATRIX]
    bus_table = table(["Fact", "Grain"] + BUS, bus_rows)
    gold_schema_table = table(["Schema", "Holds", "Owner"], GOLD_SCHEMAS)
    multi_rules = "".join(f'<div class="rule"><b class="n">{i + 1}</b><div><b>{E(t)}</b> {E(d)}</div></div>' for i, (t, d) in enumerate(MULTI_INPUT))
    metric_table = table(["Metric", "Definition", "Broken down by", "Owner"], METRICS)
    sem_rules = '<div class="rules">' + "".join(f'<div class="rule"><b class="n">{i + 1}</b><div><b>{E(t)}</b> {E(d)}</div></div>' for i, (t, d) in enumerate(SEMANTIC_RULES)) + "</div>"
    genie_space_table = table(["Space", "For", "Reads", "Benchmark"], GENIE_SPACES)
    genie_rules = '<div class="rules">' + "".join(f'<div class="rule"><b class="n">{i + 1}</b><div><b>{E(t)}</b> {E(d)}</div></div>' for i, (t, d) in enumerate(GENIE_RULES)) + "</div>"
    sens_table = table(["Level", "Examples", "Where it lives", "Who sees it", "Protection"], SENSITIVITY)
    roles_table = table(["Role (a group)", "Gets", "Limits"], ROLES)
    access_rules = "".join(f'<div class="rule"><b class="n">{i + 1}</b><div><b>{E(t)}</b> {E(d)}</div></div>' for i, (t, d) in enumerate(ACCESS_MECH))
    privacy_rules = "".join(f'<div class="rule"><b class="n">{i + 1}</b><div><b>{E(t)}</b> {E(d)}</div></div>' for i, (t, d) in enumerate(PRIVACY_RULES))
    erasure_steps = "".join(f'<div class="rule"><b class="n">{i + 1}</b><div><b>{E(t)}</b> {E(d)}</div></div>' for i, (t, d) in enumerate(ERASURE))
    ai_rules = "".join(f'<div class="rule"><b class="n">{i + 1}</b><div><b>{E(t)}</b> {E(d)}</div></div>' for i, (t, d) in enumerate(AI_GOV))
    gov_table = table(["Role", "Who", "Decides"], GOV_ROLES)
    repo_table = table(["Repository", "Holds", "Owner", "Checks"], REPOS)
    owner_table = table(["Folder", "Approved by"], OWNERS)
    deploy_table = table(["What", "Deployed by", "From"], DEPLOYS)
    stage_table = table(["Step", "What runs", "Where", "Takes"], PIPE_STAGES)
    env_table = table(["Environment", "Data", "Who", "Size and cost guard"], ENVS)
    cicd_rules = "".join(f'<div class="rule"><b class="n">{i + 1}</b><div><b>{E(t)}</b> {E(d)}</div></div>' for i, (t, d) in enumerate(CICD_RULES))
    landing_table = table(["Signal", "How it reaches prod_ops", "Delay", "Note"], OPS_LANDING)
    ops_model_table = table(["Table", "One row per", "Holds"], OPS_MODEL)
    incident_rules = "".join(f'<div class="rule"><b class="n">{i + 1}</b><div><b>{E(t)}</b> {E(d)}</div></div>' for i, (t, d) in enumerate(INCIDENT_RULES))
    agents_table = table(["Agent", "Starts when", "Does", "May"], AGENTS)
    autonomy_table = table(["Level", "Means", "Who"], AUTONOMY)
    agent_rules = "".join(f'<div class="rule"><b class="n">{i + 1}</b><div><b>{E(t)}</b> {E(d)}</div></div>' for i, (t, d) in enumerate(AGENT_RULES))
    sizing_table = table(["What", "We assume", "What it means for the design"], SIZING)
    stream_rules = '<div class="rules">' + "".join(f'<div class="rule"><b class="n">{i + 1}</b><div><b>{E(t)}</b> {E(d)}</div></div>' for i, (t, d) in enumerate(STREAM_RULES)) + "</div>"
    recovery_table = table(["Layer", "How it is copied", "Most data lost (RPO)", "How it comes back"], RECOVERY)
    recovery_steps = '<div class="rules">' + "".join(f'<div class="rule"><b class="n">{i + 1}</b><div><b>{E(t)}</b> {E(d)}</div></div>' for i, (t, d) in enumerate(RECOVERY_STEPS)) + "</div>"
    retention_table = table(["Layer", "Kept for"], RETENTION)
    master_table = table(["Master data", "Comes from", "Owner"], MASTER)
    onboard_steps = '<div class="rules">' + "".join(f'<div class="rule"><b class="n">{i + 1}</b><div><b>{E(t)}</b> {E(d)}</div></div>' for i, (t, d) in enumerate(ONBOARD)) + "</div>"
    backfill_rules = '<div class="rules">' + "".join(f'<div class="rule"><b class="n">{i + 1}</b><div><b>{E(t)}</b> {E(d)}</div></div>' for i, (t, d) in enumerate(BACKFILL)) + "</div>"
    secret_rules = '<div class="rules">' + "".join(f'<div class="rule"><b class="n">{i + 1}</b><div><b>{E(t)}</b> {E(d)}</div></div>' for i, (t, d) in enumerate(SECRETS)) + "</div>"
    team_table = table(["Who", "Size", "Does"], TEAM)
    migration_table = table(["What you have", "How it moves", "Done when"], MIGRATION)
    migration_rules = '<div class="rules">' + "".join(f'<div class="rule"><b class="n">{i + 1}</b><div><b>{E(t)}</b> {E(d)}</div></div>' for i, (t, d) in enumerate(MIGRATION_RULES)) + "</div>"
    sharing_table = table(["Partner", "What they get", "How", "Protection"], SHARING)
    ml_table = table(["Part", "How"], ML_ROWS)
    open_table = table(["Open question", "Why it matters", "Who decides", "By when"], OPEN)
    test_result_table = table(["Situation", "First test", "After fixes", "What changed"], DESIGN_TEST)
    found_table = table(["Decision", "Our pick", "Why"], FOUNDATION)
    assume_table = table(["Question", "We assume", "If it is different"], ASSUMPTIONS)
    bucket_table = table(["Bucket", "Holds", "Key", "Rules"], BUCKETS, raw=(0,))
    binding_table = table(["Catalog", "Dev workspace", "Pre-prod workspace", "Prod workspace"], BINDING)
    dq_engine_table = table(["Engine", "Used for", "Verdict", "Why"], DQ_ENGINES)
    dq_hop_table = table(["Hop", "What is checked", "What happens to bad data"], DQ_HOPS)
    dq_tables = table(["Table", "Holds", "Written by"], DQ_TABLES, raw=(0,))
    profile_keys = table(["Setting", "Values", "Meaning"], PROFILE_KEYS)
    profilers_table = table(["Profiler", "Where", "What it does"], PROFILERS)
    dq_steps = "".join(f'<div class="rule"><b class="n">{i + 1}</b><div><b>{E(t)}</b> {E(d)}</div></div>' for i, (t, d) in enumerate(DQ_STEPS))
    faq = C.faq(FAQ)

    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › <a href="{BASE}">Data platform architecture</a> › On AWS + Databricks</p>
<p class="eyebrow" style="margin-top:22px">Data platform architecture · binding · AWS + Databricks</p>
<h1>The data platform on AWS and Databricks</h1>
<p class="lede">The same architecture as <a href="{BASE}">the abstract picture</a>, with a product in every box, for a tyre manufacturer that already runs on AWS and wants Databricks. The design stays the same; only the names change.</p>
<div class="sib"><a href="{BASE}">↑ The abstract picture</a><a href="{BASE}aws-databricks/etl/">The ETL, end to end</a><a href="/leaders/spec-driven/data-platform/">Spec-driven development for data</a><a href="/learn/medallion-architecture/">Medallion, drawn right</a></div>
<nav class="toc"><b>On this page</b><ol>
<li><a href="#minute">The one-minute version</a></li><li><a href="#picture">The big picture</a></li><li><a href="#assets">Horizontal assets</a></li><li><a href="#foundation">The foundation</a></li><li><a href="#metadata">Metadata and ingestion</a></li><li><a href="#quality">Data quality and profiling</a></li><li><a href="#ops">Observability and alerts</a></li><li><a href="#testing">Testing and data contracts</a></li>
<li><a href="#medallion">The right medallion</a></li><li><a href="#aibi">Gold, semantic layer and AI/BI</a></li><li><a href="#security">Security and privacy</a></li><li><a href="#cicd">CI/CD and environments</a></li><li><a href="#agents">Agents</a></li><li><a href="#run">Running it</a></li><li><a href="#edges">Migration, sharing and ML</a></li><li><a href="#binding">22 concerns, bound</a></li>
<li><a href="#aws">AWS native or Databricks</a></li><li><a href="#plan">How we would start</a></li><li><a href="#open">Open decisions</a></li><li><a href="#design-test">How we tested this design</a></li><li><a href="#faq">Questions</a></li></ol></nav>

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

<section id="foundation"><p class="eyebrow">The foundation</p><h2>Accounts, network, storage and keys, before any pipeline</h2>
<p>Before a single pipeline runs, the platform needs somewhere safe to live: AWS accounts to hold it, a private network, buckets for the data with keys you own, Databricks workspaces to work in, and one catalog that decides who sees what. Think of it as the land, the roads and the locks. Done right once, nobody thinks about it again; done wrong, every later layer inherits the problem.</p>
<figure class="diagram">{foundation_map()}<figcaption>Three environments, each in its own AWS account and private network, on one Unity Catalog. Nothing is reachable from the internet.</figcaption></figure>

<h3>The nine choices</h3>
{found_table}

<h3>What we assumed</h3>
<p>This design is written for a typical Indian manufacturer already on AWS. Where your answer differs, the right column says what changes. None of them changes the layers above.</p>
{assume_table}

<h3>Which workspace sees which catalog</h3>
<p>Catalogs are named by environment and layer (<code>prod_silver</code>, <code>dev_gold</code>). Binding each catalog to workspaces is what keeps a test in dev from ever writing to prod, even by mistake.</p>
{binding_table}

<h3>Buckets and keys</h3>
<p>Every bucket blocks public access, is encrypted with a KMS key you own, and is reached only through the VPC endpoint or by Databricks through an IAM role it is allowed to assume.</p>
{bucket_table}

<h3>Built from code</h3>
<p>The foundation is Terraform in Git, applied in five steps. The environments differ only in one settings file each, so dev, pre-prod and prod are the same platform at different sizes.</p>
{C.code(TF_TREE, "Folder layout of the foundation code. Pipelines are not here: they are deployed with Asset Bundles.")}
<p><b>Recovery:</b> if Mumbai is lost, the same Terraform with <code>dr.tfvars</code> builds the workspace in Hyderabad on the copied data, and the data-platform deploy puts back every grant, filter and mask before anyone can read. The full plan, with targets per layer, is in <a href="#run">running it</a>.</p>
</section>

<section id="metadata"><p class="eyebrow">Metadata and ingestion on AWS</p><h2>One metadata database, one ingestion framework</h2>
<p>The Common Ingestion Framework is <b>metadata-driven</b>: adding a source is a few lines of YAML, not a new pipeline. It follows the <a href="https://medium.com/@basant.choudhary09/metadata-db-design-for-data-engineering-components-ingestion-processing-data-quality-data-6b355ad5ecb9">Metadata DB Design for Data Engineering Platforms</a>, already built in our framework. Full table definitions, the view and the reader code are on <a href="{BASE}metadata-store/">the metadata store page</a>.</p>
<h3>The tables</h3>
{md_table}
<p><b>How it all runs</b>, step by step from a source to gold, with every job, trigger, id and log row: <a href="{BASE}aws-databricks/etl/">The ETL, end to end</a>.</p>
<p class="note">The framework also has a key registry (every allowed setting and its type), per-column settings, quality results and a PII policy table on the same database.</p>

<h3>YAML in GitHub, and a SQL database</h3>
<p>We need both, for different jobs. People write and approve settings as YAML in GitHub; a loader validates every key and writes them to the database, one database per environment (dev, pre-prod, prod) with the same schema. Pipelines only ever read the database.</p>
{git_table}
<p><b>Two rules.</b> Nobody edits configuration in the database by hand: the next load would overwrite it and Git would have no record. Runtime state (watermarks, run log) never goes into Git.</p>

<h3>Which database on AWS</h3>
<p>The metadata store needs keys between tables, fast small reads and writes, safe parallel writes from many jobs, and good JSON for the merged view. That is a relational database, and PostgreSQL fits the design as written.</p>
{db_table}
<p><b>Where it sits:</b> in your AWS account, in a private subnet, in the same region as the Databricks workspace (Mumbai; Frankfurt only if EU data must have its own platform). The password lives in AWS Secrets Manager; Databricks classic compute reaches it over the VPC, and serverless compute through a private endpoint. The runtime tables are copied into Delta every 15 minutes so dashboards and cost reports can join them without touching the database.</p>

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
<p>The full list of sources, the five ingestion technologies and the landing contract are on <a href="{BASE}aws-databricks/etl/#sources">The ETL, end to end</a>. Where this page and that one differ on how the runtime works, that page is the one to follow.</p>
<p>Ingestion has two steps. A <b>mover</b> brings raw data from the source into an S3 landing folder; which mover is a setting in <code>source_config</code>, so it can change without code. Then <b>one lander</b>, our PySpark job on Databricks that reads exactly the new files listed in its file log, reads its settings from <code>dataset_view</code>, writes bronze with arrival details, records a <code>run_log</code> row and is safe to run twice. Lakeflow Jobs are generated from the metadata and deployed with Databricks Asset Bundles.</p>
{mover_table}

<h3>Orchestration: which service runs what, and when</h3>
<p>One rule: <b>one orchestrator owns each pipeline</b>. Lakeflow Jobs owns everything from the landing folder onwards; AWS services only start the movers on the AWS side and hand over. Two schedulers for the same pipeline is the most common cause of runs that overlap or never start.</p>
{orch_table}

<p><b>Is there an Azure Data Factory on AWS?</b> Not as one tool; its parts are spread across services. We use them only as movers. The framework itself is Python, so it is tested, reviewed and portable, instead of hundreds of hand-built visual pipelines.</p>
{adf_table}
</section>

<section id="quality"><p class="eyebrow">Data quality and profiling</p><h2>Rules written once, checked at every hop</h2>
<p>Two different jobs. <b>Data quality rules</b> are checks we write down: "every reading belongs to a known curing press", "scrap quantity is never negative". <b>Profiling</b> measures what the data actually looks like (how many blanks, how many different values, the smallest and largest) so we notice when it changes, and so we can find rules nobody thought to write. Both are horizontal assets: switched on for every dataset from the metadata, not coded per pipeline.</p>
<figure class="diagram">{dq_flow()}<figcaption>Rules come from Git and run at every hop; every check ends in one of four actions and one result row. The profiler watches the data beside it and proposes new rules for a person to approve.</figcaption></figure>

<h3>Which engine checks the rules</h3>
<p>Rules are stored as data in the metadata store, and the engine sits behind our quality port (a fixed interface), so the engine can change without touching a single rule.</p>
{dq_engine_table}

<h3>What is checked at each hop</h3>
<p>Each layer checks what it promises, and nothing more. Bronze keeps data as it arrived, so the real cleaning checks start at silver.</p>
{dq_hop_table}

<h3>A rule file, for one table</h3>
<p>Stewards write rules as YAML next to the dataset's settings. The same file switches profiling on.</p>
{C.code(DQ_RULES_YAML, "Rules and profiling settings for curing-press readings in silver. Ranges are examples; the plant's process engineer owns the real ones.")}

<h3>Where the rules and results live</h3>
<p>In the same metadata database, split by the three schemas: rules and settings in <code>config</code> (changed only through Git), results in <code>runtime</code>. These tables already exist in our framework; on AWS they move to Aurora PostgreSQL.</p>
{dq_tables}

<h3>Profiling: three tools, each where it pays</h3>
<p>Profiling every table on every run costs compute for little gain. So the default profiler runs on new data, the managed monitor runs only on the tables the business watches most, and personal-data detection runs on the catalogs.</p>
{profilers_table}
<p>Profiling is set per dataset with six settings in <code>dataset_config</code>:</p>
{profile_keys}

<h3>From profile to rule: a person always decides</h3>
<div class="rules">{dq_steps}</div>
<p><b>Later, an agent:</b> it may read the profiles and quarantine tables, explain what changed in plain words and draft the rule change. It still arrives as a pull request for the steward.</p>
</section>

<section id="ops"><p class="eyebrow">Pipeline observability</p><h2>The ops dashboard and alerts</h2>
<p>Observability means that when a number looks wrong or a dashboard is late, anyone can see within a minute <b>what ran, what failed, why, and what it cost</b>, without opening a notebook. It is built once as a horizontal asset and switched on for every pipeline from the metadata.</p>
<figure class="diagram">{ops_flow()}<figcaption>Four sources of signals plus the targets from the metadata, one ops layer joined on the run id, three ways out: a dashboard, alerts and questions in plain words.</figcaption></figure>

<h3>Where the signals come from</h3>
{signals_table}

<h3>How each signal lands</h3>
<p>Everything lands in one catalog, <code>prod_ops</code>, so one SQL query can join it. The rule: read in place where Databricks already keeps it, copy only what lives outside.</p>
{landing_table}

<h3>How they join: four keys</h3>
<p>Signals from three systems only help if they line up. Our framework stamps the same keys everywhere, so a failed run can be followed to its cost, its quality results and the AWS mover that fed it.</p>
<figure class="diagram">{ops_joins()}<figcaption>The join map. No guessing by timestamps: every link is a key our framework writes.</figcaption></figure>

<h3>The ops tables</h3>
<p>A small star schema of its own, in <code>prod_ops</code>, built by an ordinary pipeline with the same tests as any other.</p>
{ops_model_table}

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
<h3>From alert to incident</h3>
<div class="rules">{incident_rules}</div>
<p><b>Later, self-healing:</b> for known causes (a source briefly down, a late file) an agent may propose the fix and prove it on a pre-prod clone; a person approves before anything touches production. See <a href="#agents">agents</a>.</p>
</section>

<section id="testing"><p class="eyebrow">Testing and data contracts</p><h2>Catch it early, prove it before release</h2>
<p>Most data platforms are tested by looking at the dashboard after go-live. We test in six gates, from the developer's laptop to production, and each gate catches what the earlier ones cannot. All of it is part of the platform from day one, not a project for later.</p>
<figure class="diagram">{gates()}<figcaption>Six gates. The same tests run for every pipeline, because the pipelines are generated from the same metadata.</figcaption></figure>
{test_table}
<p><b>The full test strategy</b>, cloud-neutral, is on <a href="/learn/data-platform-architecture/testing/">Test architecture for a data platform</a>.</p>
<p><b>How this uses what we are building.</b> The <a href="/learn/shift-left/">shift-left bundle</a> and its test kit run at the first two gates; the <a href="/learn/data-platform-sim/problems/">Problem Lab</a> scenarios (duplicates, late data, failure mid-job, schema drift, SCD2 pitfalls) become the unit and integration cases; <a href="/learn/datatwin/">DataTwin</a> is the release gate. Because pipelines are generated from metadata, a new source gets these tests without anyone writing them again.</p>

<h3>DataTwin: a pretend plant with faults planted on purpose</h3>
<p>Real data rarely shows the bad days on schedule. DataTwin produces data the way the plants and the business would, then plants the faults below. The release passes only if the platform catches every one and the dashboard still matches the pretend world's true numbers.</p>
{twin_table}

<h3>Data contracts: do we need them?</h3>
<p>A <b>data contract</b> is a written agreement between the team that produces data and the teams that use it: which columns, what they mean, how fresh, how good, and who owns it. It is written as a YAML file in Git using the open standard <b>ODCS</b> (Open Data Contract Standard, version 3), so it is both readable and checkable by machine. The short answer: <b>yes, at the two boundaries, and no, not everywhere.</b></p>
{need_table}
{parts_table}
<p>Nothing new has to be built to enforce them: the contract check at silver, the quality rules, the freshness and volume alerts and Unity Catalog tags already do it. The contract simply makes the promise explicit and gives every alert an owner. The open-source <code>datacontract</code> command-line tool lints the ODCS files and tests them in the pull-request gate.</p>
</section>

<section id="medallion"><p class="eyebrow">The right medallion</p><h2>One medallion, two speeds</h2>
<p>The medallion is the row of layers in the middle: bronze (raw), silver (clean) and gold (shaped for the business). Streaming does not need a second architecture. Nightly batches and continuous events flow through <b>the same tables</b>, with the same contracts and the same checks; only the speed differs.</p>
<figure class="diagram">{two_speeds()}<figcaption>Batch and streaming share one set of layers.</figcaption></figure>
<h3>What each layer promises</h3>
{layers_table}
<h3>Bronze to silver</h3>
<p>Thirteen generic stages run for every dataset, set per column in the metadata: contract check, select and rename, hygiene, parse and type, time, standardise values, personal data, row filter, quality rules, duplicates, keys, history (SCD type 1 or 2 by kind of data) and provenance. No business logic and no free-form SQL in this step. The stages, the column settings, the schema change rules and the history choices are on <a href="{BASE}aws-databricks/etl/#transforms">The ETL, end to end</a>.</p>
<p>Silver keeps one table per source entity, with conformed keys. Joining sources together (SAP orders with MES production, for example) is a separate, named step, not hidden inside a silver table. Each silver table has one quarantine table, which its steward reviews weekly.</p>
<h3>Common mistakes, and the fix</h3>{mistakes}
<p>More detail, with one record followed through every layer: <a href="/learn/medallion-architecture/">Medallion architecture, drawn right</a>.</p></section>

<section id="aibi"><p class="eyebrow">Gold, the semantic layer and AI/BI</p><h2>Shape it once, define each metric once, then ask in plain words</h2>
<p>Ask three tools for "scrap rate" and you can get three numbers. That happens when every report shapes the data and writes the formula itself. The fix has two halves: <b>gold</b> shapes the data once, as star schemas the business recognises, and the <b>semantic layer</b> defines each metric once, as a metric view in Unity Catalog. Every front end, from dashboards to Genie, reads those definitions. Then AI on top is safe: the model only chooses which metric, which breakdown and which filter.</p>

<h3>The choices</h3>
{gold_dec_table}

<h3>Gold: star schemas</h3>
<p>A <b>star schema</b> puts the numbers (facts) in the middle and the words people filter by (dimensions) around it. Each fact table states its <b>grain</b>: what one row means. Getting the grain right is most of the work.</p>
<figure class="diagram">{star()}<figcaption>The production fact and its dimensions. Other facts share the same dimensions.</figcaption></figure>
<p><b>The bus matrix</b> shows which facts share which dimensions. A shared ("conformed") dimension is what lets you put scrap next to warranty claims for the same material and get a sensible answer.</p>
{bus_table}
<h3>Where gold lives</h3>
{gold_schema_table}
<h3>Facts built from several inputs</h3>
<p>Some facts need more than one source: production needs MES counts, the press master, the material master and the shift calendar, which arrive at different times. Five rules keep them right.</p>
<div class="rules">{multi_rules}</div>

<h3>The semantic layer: metric views</h3>
<p>A <b>metric view</b> is a definition, not a table: which gold fact, which joins, which dimensions, and the formula for each measure. It is stored in Unity Catalog with an owner, so it is governed like a table.</p>
{C.code(METRIC_YAML, "One metric view for press performance. Formulas are sums divided by sums, computed for whatever slice is asked.")}
<h3>The starter metrics</h3>
{metric_table}
<h3>Six rules for the semantic layer</h3>
{sem_rules}
<p class="note">To confirm when building: whether reading a metric view also needs a grant on the gold tables under it, and whether outside BI tools can query metric views directly ({CHECK}).</p>

<h3>From a question to an answer</h3>
<figure class="diagram">{aibi()}<figcaption>From a question to an answer that shows its own definition.</figcaption></figure>

<h3>Genie: one space per audience</h3>
{genie_space_table}
{genie_rules}

<h3>Genie or our Conversation UI?</h3>
{genie_table}</section>

<section id="security"><p class="eyebrow">Security, privacy and governance</p><h2>Who may see what, and how we prove it</h2>
<p>Three kinds of data need protecting here: <b>personal data</b> (dealers, fleet drivers, consumers who register a warranty, operators on shift logs), <b>commercial data</b> (prices, discounts, margins) and the <b>recipes</b> that make the tyres. The design protects each one where the data lives, in the catalog, so the protection holds in every tool: a dashboard, a notebook, Genie or an agent.</p>

<h3>Four levels of sensitivity</h3>
{sens_table}

<h3>Roles and what they get</h3>
<p>People read; only service principals write to prod. That one rule removes most accidents.</p>
{roles_table}

<h3>How access is enforced</h3>
<div class="rules">{access_rules}</div>

<h3>Personal data: India's DPDP Act and the EU's GDPR</h3>
<p>Both laws ask the same things in practice: keep personal data only for a stated purpose, only as long as needed, protect it, and erase it when asked. The hard part in a lakehouse is erasure, because bronze keeps everything for replay. The design solves it at the door.</p>
<div class="rules">{privacy_rules}</div>
<h3>When someone asks to be erased</h3>
<div class="rules">{erasure_steps}</div>
<p class="note">Tokenising uses the framework's existing <code>pii_policy</code> table (actions: pass through, hash, mask, tokenise, redact, per environment). The vault is its own catalog, <code>prod_pii_vault</code>, with its own bucket and key, readable only by privacy case handlers; recipe keepers cannot read it, and the privacy team cannot read recipes. The fingerprint key and the vault key live in AWS Secrets Manager and KMS.</p>

<h3>Recipes</h3>
<p>Recipes and process settings sit in <code>prod_restricted</code>, in their own bucket with their own key. Gold carries only the compound family, never the recipe. Only the named recipe keepers can read it, every read raises a notice to the recipe owner (the head of compound development), access is reviewed every month, and revoking the key cuts all access at once. It is never added to Genie or to an agent.</p>

<h3>AI on governed data</h3>
<div class="rules">{ai_rules}</div>

<h3>Who decides</h3>
{gov_table}
<p><b>Proof, not promises.</b> Databricks audit system tables, AWS CloudTrail and KMS key-use logs are joined in prod_ops into an access report: who read what, from which tool. The data owners review it every quarter, and it is the evidence pack for an auditor.</p>
</section>

<section id="cicd"><p class="eyebrow">CI/CD and environments</p><h2>Every change takes the same path to production</h2>
<p>Code, configuration and definitions all change through Git and reach production the same way, through the six test gates. Nobody clicks a change into prod, and every release can be undone.</p>
<figure class="diagram">{cicd_flow()}<figcaption>From a pull request to production, with the checks at each step and the way back.</figcaption></figure>

<h3>Two repositories</h3>
{repo_table}
<h3>Who approves which folder</h3>
<p>GitHub CODEOWNERS sends each change to the people who own it: a quality rule to its steward, a metric to its owner.</p>
{owner_table}
<h3>What deploys what</h3>
{deploy_table}
<h3>The path, step by step</h3>
{stage_table}
<h3>Three environments</h3>
{env_table}
<h3>Five rules</h3>
<div class="rules">{cicd_rules}</div>
</section>

<section id="agents"><p class="eyebrow">Agents</p><h2>Agents propose, people decide</h2>
<p>Agents help most with work that is slow and repetitive for people: reading logs after a failure, drafting a quality rule, writing YAML for a new source. In this design an agent never changes production. It reads, explains, and proposes a change as a pull request, which then takes the same release path as any other change. The agents run on <a href="/learn/agent-harness-aws/">the agent harness on AWS</a>.</p>
<h3>Seven agents, one job each</h3>
{agents_table}
<h3>How far each may go</h3>
{autonomy_table}
<h3>Five rules</h3>
<div class="rules">{agent_rules}</div>
</section>

<section id="run"><p class="eyebrow">Running it</p><h2>Sizing, recovery, retention and the people</h2>
<p>A design is only finished when it says how big it is, how it comes back after a disaster, how long it keeps things, and who runs it. The numbers below are our assumptions for a typical tyre maker; each one is a setting, so the design holds if they change.</p>

<h3>Sizing and targets</h3>
{sizing_table}

<h3>Streaming sensor data</h3>
{stream_rules}

<h3>Recovery: what comes back, how fast, and what can be lost</h3>
<p>Two words first. The <b>recovery point</b> (RPO) is how much recent data can be lost; the <b>recovery time</b> (RTO) is how long until people can work again. Different layers get different targets, because they cost different amounts to copy.</p>
{recovery_table}
{recovery_steps}

<h3>How long each layer is kept</h3>
<p>Assumed periods; your legal and finance teams confirm them. Retention jobs run nightly and log what they delete.</p>
{retention_table}

<h3>Master data: who owns the facts everything joins on</h3>
<p>OEE is only right if each press's ideal cycle time and each plant's shift calendar are right. These are small tables with big effects, so each has a named owner.</p>
{master_table}

<h3>Adding a source: the checklist</h3>
<p>"A new source is a YAML entry" is true for the pipeline. The checklist is everything around it; the source onboarder agent drafts most of it as one pull request.</p>
{onboard_steps}

<h3>Backfills</h3>
{backfill_rules}

<h3>Secrets</h3>
{secret_rules}

<h3>The team</h3>
{team_table}
</section>

<section id="edges"><p class="eyebrow">Migration, sharing and ML</p><h2>What you already have, who outside needs data, and models</h2>

<h3>Moving from Glue, Redshift and QuickSight</h3>
{migration_table}
{migration_rules}

<h3>Sharing with partners</h3>
<p>Every share is a data product: it has a contract, an owner and a filter to the partner's own rows, and its use is audited and reviewed every quarter.</p>
{sharing_table}

<h3>Machine learning</h3>
<p>Models use the same platform, catalog and release path as everything else; nothing is copied out to a separate ML system.</p>
{ml_table}
</section>

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
<div><h3>Crawl · 4 to 6 weeks</h3><p>One slice end to end in your AWS account: curing-press sensor data and MES production records through silver to one gold fact, one metric view (OEE or scrap rate), one Genie space for plant managers with benchmark questions.</p><p><b>You see:</b> the whole path working, with quality, lineage and cost on from day one.</p></div>
<div><h3>Walk · next quarter</h3><p>Three to five more sources (SAP sales and stock, quality lab, warranty claims, dealer sell-out). The horizontal assets on by default. CostSherlock reporting cost per data product.</p><p><b>You see:</b> each new source added as a YAML entry, not a project.</p></div>
<div><h3>Run · after that</h3><p>A small platform team owns the assets; domain teams build data products on them. The Conversation UI in staff apps. Agents propose fixes as pull requests.</p><p><b>You see:</b> the tenth data product faster and safer than the first.</p></div>
</div></section>

<section id="open"><p class="eyebrow">Open decisions</p><h2>What must be settled before or during the first slice</h2>
<p>Most items marked "check current status" on this page are product details that do not change the design. These ten do: each has a fallback, an owner and a date.</p>
{open_table}
</section>

<section id="design-test"><p class="eyebrow">How we tested this design</p><h2>Twelve situations, walked through before anything was built</h2>
<p>We tested the design on paper first. Two reviewers who had not written it worked from the page alone. One walked twelve real situations through it step by step; the other checked every section against every other and against 25 topics a complete design must cover. They found 3 situations that failed outright, about 30 places where two sections disagreed, and several topics that were missing (sizing, recovery, migration, sharing). Every finding was fixed in the page above. A third reviewer then re-tested the three failures and looked for new contradictions; that round found 27 more, mostly in recovery and privacy details, and those are fixed too.</p>
{test_result_table}
<p class="note">Four situations pass only once an open decision is settled: the EU legal basis, a German-capable detector, Databricks in Hyderabad, and the metric-view security test. All are in the open decisions above.</p>
</section>

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
