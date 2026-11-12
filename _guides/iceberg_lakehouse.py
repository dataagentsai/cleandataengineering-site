"""Iceberg lakehouse on AWS with Databricks: who should own the catalog? One page at
/learn/iceberg-lakehouse-aws-databricks/.

    python3 _guides/iceberg_lakehouse.py      (then python3 _site/nav.py and python3 _site/seo.py)

Asked for on 12 Nov 2026: the conceptual big picture of a data platform with every concern, then two
physical pictures with Iceberg as the table format: Architecture B (AWS owns the catalog: S3 Tables,
Glue, Lake Formation; Databricks is a guest) and Architecture A (Unity Catalog owns it; AWS engines
are guests). Can Databricks do bronze to silver to gold in B, and AWS engines in A? What each one
restricts, compared concern by concern (maintenance, ETL, streaming, semantic, serving, cost,
governance, lineage and every other concern of the platform page), public case studies, and the
synthesis: who wins and what you accept with each.

main() refuses to write if a concern from _guides/data_platform.py is missing from the comparison.
"""
import json
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "_paths"))
import components as C  # noqa: E402
import table_formats as TF  # noqa: E402
import table_maintenance as TM  # noqa: E402

wb = C.wb
SITE = wb.SITE
URL_PATH = "/learn/iceberg-lakehouse-aws-databricks/"
DATE = "2026-11-12"
TITLE = "Iceberg lakehouse on AWS with Databricks: who should own the catalog?"
DESC = ("The whole data platform with every concern, then two physical designs with Iceberg: AWS owns the catalog "
        "(S3 Tables, Glue, Lake Formation) or Databricks Unity Catalog owns it. Who can write, what each restricts, "
        "maintenance, ETL, streaming, semantic, serving, cost, governance, lineage, case studies and the winner.")

BLUE, MINT, BUTTER, ROSE, LAV = TM.BLUE, TM.MINT, TM.BUTTER, TM.ROSE, TM.LAV
ARROW = '<defs><marker id="ila" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#111"/></marker></defs>'

CSS = TM.CSS + """<style>
  .tf tr.grp td { background:#f4f4f4; font-weight:700; font-size:13px; letter-spacing:.04em; text-transform:uppercase; }
  .tf td.win { font-weight:700; width:13%; } .tf table.cmp td:nth-child(2), .tf table.cmp td:nth-child(3) { width:32%; }
  .tf .verdict { border:var(--line); border-radius:var(--wob); padding:12px 18px; margin:16px 0; background:var(--mint-wash); }
  .tf .case { border:var(--line); border-radius:var(--wob); padding:10px 16px; background:#fff; margin:12px 0; }
  .tf .case h3 { margin:4px 0 4px; } .tf .case .tag { display:inline-block; font-size:12px; font-weight:700; border:1.5px solid #111; border-radius:999px; padding:0 8px; margin-left:6px; background:var(--butter-wash); }
</style>"""


def _t(x, y, s, size=13.5, anchor="middle"):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}">{E(s)}</text>'


def _rect(x, y, w, h, fill="#fff", dash=False, rx=8):
    d = ' stroke-dasharray="5 4"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="#111" stroke-width="1.5"{d}/>'


def _arrow(path, dash=False, width=1.4):
    d = ' stroke-dasharray="5 4"' if dash else ""
    return f'<path d="{path}" stroke="#111" stroke-width="{width}" fill="none"{d} marker-end="url(#ila)"/>'


# ----------------------------------------------------------------------------------- drawings
def drawing_concept():
    aria = ("The conceptual data platform. Sources on the left: databases, SaaS and APIs, files, events and IoT. "
            "In the middle, the line: ingest, bronze, silver, gold, semantic, with streaming as a second speed on the same line. "
            "Under the line, five layers: compute engines; catalog and governance, the one owner per table, which is the decision on this page; "
            "the table format, Apache Iceberg; object storage; and maintenance. On the right, consumers: BI dashboards, AI agents, apps and APIs, "
            "ML and features, data sharing, other engines. Along the bottom, the 24 concerns in five groups: Trust, See, Guard, Run and Self.")
    d = f'<svg viewBox="0 0 1000 650" role="img" aria-label="{E(aria)}">{ARROW}'
    # sources
    d += _rect(10, 50, 140, 330, "#fff", rx=12) + _t(80, 76, "Sources", 17)
    for i, s in enumerate(["databases", "SaaS and APIs", "files", "events and IoT", "machines (OT)"]):
        d += _rect(22, 92 + i * 56, 116, 40, BUTTER) + _t(80, 117 + i * 56, s)
    # platform
    d += '<rect x="168" y="20" width="634" height="400" rx="14" fill="none" stroke="#111" stroke-width="1.5" stroke-dasharray="2 4"/>'
    d += _t(485, 42, "the data platform", 16)
    for i, s in enumerate(["ingest", "bronze", "silver", "gold", "semantic"]):
        x = 180 + i * 124
        d += _rect(x, 56, 108, 52, [BUTTER, "#f3e6d6", "#eeeeee", "#fff1c4", LAV][i]) + _t(x + 54, 88, s, 16)
        if i:
            d += _arrow(f"M{x - 15},82 L{x - 2},82")
    d += '<path d="M186,128 L790,128" stroke="#111" stroke-width="1.4" stroke-dasharray="7 5" fill="none" marker-end="url(#ila)"/>'
    d += _t(488, 146, "streaming: a second, faster speed on the same line", 13)
    layers = [("compute engines: batch, SQL, streaming, ML", BLUE, False),
              ("catalog + governance: ONE owner per table (pointer, permissions, lineage)", LAV, True),
              ("table format: Apache Iceberg", BUTTER, False),
              ("object storage: S3, open Parquet files", MINT, False),
              ("maintenance: compaction, snapshot expiry, orphan files", ROSE, False)]
    for i, (s, f, hot) in enumerate(layers):
        y = 160 + i * 46
        d += f'<rect x="186" y="{y}" width="600" height="40" rx="8" fill="{f}" stroke="#111" stroke-width="{2.6 if hot else 1.5}"/>'
        d += _t(486, y + 25, s, 14.5)
    d += _t(486, 412, "the decision on this page is the thick box: who owns the catalog", 13)
    # consumers
    d += _rect(820, 20, 170, 400, "#fff", rx=12) + _t(905, 44, "Consumers", 17)
    for i, s in enumerate(["BI dashboards", "AI agents, Genie", "apps and APIs", "ML and features", "data sharing", "other engines"]):
        d += _rect(832, 58 + i * 58, 146, 42, MINT) + _t(905, 84 + i * 58, s)
    d += _arrow("M150,215 L176,90", width=1.8) + _arrow("M774,82 L818,82", width=1.8)
    # concerns band
    d += _t(500, 452, "across every hop: the 24 concerns", 16)
    groups = [("Trust", ["contracts & schema", "data quality", "profiling", "reconciliation"], BUTTER),
              ("See", ["lineage", "logs, metrics, traces", "freshness & SLOs", "cost & FinOps", "performance & scale"], BLUE),
              ("Guard", ["security & access", "privacy & PII", "governance & semantics", "audit & run log"], ROSE),
              ("Run", ["metadata & control", "orchestration", "replay & backfill", "environments & CI/CD", "testing", "resilience & DR", "layout", "streaming"], "#eeeeee"),
              ("Self", ["self-healing", "agent assistance", "simulation"], LAV)]
    for i, (g, items, f) in enumerate(groups):
        x = 10 + i * 198
        d += _rect(x, 466, 188, 176, "#fff", rx=10) + _rect(x, 466, 188, 30, f, rx=10) + _t(x + 94, 487, g, 16)
        for k, it in enumerate(items):
            d += _t(x + 14, 516 + k * 16, it, 12.5, "start")
    return d + "</svg>"


def drawing_arch_b():
    aria = ("Architecture B, AWS owns the catalog. In the centre, the AWS Glue Data Catalog with Lake Formation, also sold as the SageMaker lakehouse, "
            "holds the key. Under it, an S3 table bucket holds Iceberg tables for bronze, silver and gold, and S3 Tables does the chores. "
            "On the left, the owners write: Firehose and Managed Flink, Glue ETL and EMR Spark. On the right, AWS readers: Athena, Redshift Serverless, QuickSight. "
            "Bottom left, Databricks is a guest: it reads through Unity Catalog federation, read-only, and can write only from classic clusters through the Glue Iceberg REST endpoint, outside Unity Catalog.")
    d = f'<svg viewBox="0 0 1000 400" role="img" aria-label="{E(aria)}">{ARROW}'
    d += _rect(320, 20, 360, 86, LAV, rx=10)
    d += _t(500, 48, "AWS Glue Data Catalog + Lake Formation", 16) + _t(500, 72, "(the SageMaker lakehouse) owns the pointer", 13.5)
    d += _t(500, 94, "permissions: Lake Formation, LF-Tags", 13)
    d += '<circle cx="662" cy="36" r="8" fill="#fff" stroke="#111" stroke-width="1.5"/><line x1="654" y1="36" x2="630" y2="36" stroke="#111" stroke-width="2"/>'
    d += TM._bucket(385, 196, 230, "S3 table bucket", "Iceberg: bronze, silver, gold")
    d += TM._broom(640, 196) + _t(724, 252, "S3 Tables does", 13) + _t(724, 270, "the chores", 13)
    d += _arrow("M500,106 L500,184")
    d += _t(110, 20, "owners write", 14)
    for i, s in enumerate(["Firehose, Managed Flink", "Glue ETL, EMR Spark"]):
        d += _rect(20, 32 + i * 58, 220, 44, BUTTER) + _t(130, 59 + i * 58, s, 14)
    d += _arrow("M240,54 L318,50", width=2.2) + _arrow("M240,112 L318,86", width=2.2)
    d += _t(880, 20, "AWS readers", 14)
    for i, s in enumerate(["Athena", "Redshift Serverless", "QuickSight"]):
        d += _rect(780, 32 + i * 52, 200, 40, MINT) + _t(880, 57 + i * 52, s, 14)
    d += _arrow("M780,52 L682,50") + _arrow("M780,104 L682,80") + _arrow("M780,156 L682,100")
    d += _rect(20, 236, 300, 150, "#fff", dash=True, rx=10)
    d += _t(170, 262, "Databricks, a guest", 16)
    d += _t(36, 290, "reads: Unity Catalog federation,", 13.5, "start") + _t(36, 308, "foreign tables, read-only", 13.5, "start")
    d += _t(36, 336, "writes: classic clusters only, Iceberg", 13.5, "start") + _t(36, 354, "library + Glue REST endpoint,", 13.5, "start")
    d += _t(36, 372, "outside Unity Catalog governance", 13.5, "start")
    d += _arrow("M250,236 L360,108", dash=True)
    return d + "</svg>"


def drawing_arch_a():
    aria = ("Architecture A, Unity Catalog owns the catalog. In the centre, Databricks Unity Catalog holds the key, with grants, masks, lineage and audit. "
            "Under it, your S3 bucket holds managed Iceberg tables for bronze, silver and gold, and Predictive Optimization does the chores. "
            "On the left, the owners write: Lakeflow jobs and SQL, Auto Loader and Lakeflow Connect, which also pick up files that AWS services such as Firehose and DMS land. "
            "On the right, guests: Athena, Redshift and QuickSight read gold through Glue catalog federation with Lake Formation; EMR, Trino and Snowflake read, and can write, through Unity Catalog's Iceberg REST catalog.")
    d = f'<svg viewBox="0 0 1000 400" role="img" aria-label="{E(aria)}">{ARROW}'
    d += _rect(320, 20, 360, 86, LAV, rx=10)
    d += _t(500, 48, "Databricks Unity Catalog", 16) + _t(500, 72, "owns the pointer", 13.5)
    d += _t(500, 94, "grants, tags, lineage, audit, metric views", 13)
    d += '<circle cx="662" cy="36" r="8" fill="#fff" stroke="#111" stroke-width="1.5"/><line x1="654" y1="36" x2="630" y2="36" stroke="#111" stroke-width="2"/>'
    d += TM._bucket(385, 196, 230, "your S3 bucket", "managed Iceberg: bronze, silver, gold")
    d += TM._broom(640, 196) + _t(730, 252, "Predictive", 13) + _t(730, 270, "Optimization", 13)
    d += _arrow("M500,106 L500,184")
    d += _t(110, 20, "owners write", 14)
    for i, s in enumerate(["Lakeflow jobs, SQL", "Auto Loader, Connect"]):
        d += _rect(20, 32 + i * 58, 220, 44, BUTTER) + _t(130, 59 + i * 58, s, 14)
    d += _arrow("M240,54 L318,50", width=2.2) + _arrow("M240,112 L318,86", width=2.2)
    d += _rect(20, 236, 300, 110, "#fff", rx=10)
    d += _t(170, 262, "AWS landing (optional)", 15)
    d += _t(36, 290, "Firehose, DMS, apps drop files", 13.5, "start") + _t(36, 308, "in a landing bucket; Auto Loader", 13.5, "start")
    d += _t(36, 326, "picks them up into bronze", 13.5, "start")
    d += _arrow("M130,236 L130,138")
    d += _t(880, 20, "guests", 14)
    d += _rect(740, 32, 245, 86, MINT, dash=True)
    d += _t(862, 56, "Athena, Redshift, QuickSight", 14) + _t(862, 78, "read gold through Glue", 13) + _t(862, 98, "federation + Lake Formation", 13)
    d += _rect(740, 134, 245, 86, MINT, dash=True)
    d += _t(862, 158, "EMR, Trino, Snowflake", 14) + _t(862, 180, "read, and can write, through", 13) + _t(862, 200, "Unity Catalog's Iceberg REST", 13)
    d += _arrow("M740,74 L682,62", dash=True) + _arrow("M740,176 L682,96", dash=True)
    return d + "</svg>"


def drawing_writes():
    aria = ("Who can write where, a two by two grid. Rows: Databricks, AWS engines. Columns: Architecture A, Unity Catalog owns; Architecture B, AWS owns. "
            "A with Databricks: writes everything, serverless, Lakeflow, governed. A with AWS engines: Athena, Redshift and QuickSight read; EMR and Spark can write through Unity Catalog's Iceberg REST. "
            "B with Databricks: reads through federation; writes only from classic clusters, outside Unity Catalog. B with AWS engines: write everything natively.")
    d = f'<svg viewBox="0 0 1000 300" role="img" aria-label="{E(aria)}">'
    d += _t(412, 30, "A: Unity Catalog owns", 17) + _t(792, 30, "B: AWS owns", 17)
    rows = [("Databricks", [("writes everything: serverless,", "Lakeflow, SQL; fully governed", MINT),
                            ("reads via federation (read-only);", "writes only from classic clusters", ROSE)]),
            ("AWS engines", [("Athena, Redshift read gold;", "EMR, Spark can write via UC REST", BUTTER),
                             ("Glue, EMR, Firehose, Flink", "write everything natively", MINT)])]
    for r, (name, cells) in enumerate(rows):
        y = 48 + r * 122
        d += _rect(14, y, 200, 108, "#fff") + _t(114, y + 60, name, 17)
        for c, (l1, l2, f) in enumerate(cells):
            x = 232 + c * 380
            d += _rect(x, y, 360, 108, f) + _t(x + 180, y + 48, l1, 15) + _t(x + 180, y + 72, l2, 15)
    return d + "</svg>"


def fig(svg, cap):
    return f'<div class="fig">{svg}<p>{E(cap)}</p></div>'


# ----------------------------------------------------------------------------------- content
NAMES = [
    ("Amazon S3 Tables", "Storage: a table bucket that holds Iceberg tables and maintains them itself (compaction, snapshot expiry, unreferenced file removal)."),
    ("AWS Glue Data Catalog", "The catalog: which tables exist and, for Iceberg, the pointer to each table's current metadata file. Every AWS engine looks tables up here."),
    ("AWS Lake Formation", "Permissions on the Glue catalog: table, column, row and cell grants, LF-Tags, and short-lived credentials handed to engines."),
    ("SageMaker lakehouse", "AWS's umbrella name for Glue Data Catalog plus Lake Formation, reaching across S3, S3 Tables, Redshift storage and federated catalogs, with an Iceberg REST endpoint."),
    ("SageMaker Catalog", "A different thing: the business catalog (glossary, data products, access requests) on top. Formerly DataZone."),
    ("Databricks Unity Catalog", "Databricks' catalog, permissions, lineage, audit and sharing in one, with its own Iceberg REST catalog for outside engines."),
]

# Can Databricks do the ETL when AWS owns the catalog?
B_WRITE = [
    ("B1. AWS engines do all the ETL; Databricks only reads", "Glue ETL or EMR Spark writes bronze, silver and gold into S3 Tables. Databricks reads the tables through Unity Catalog federation for BI, ML or Genie.", "Clean, but Databricks is a reader you pay for", "Pursue when Databricks is a light guest"),
    ("B2. Databricks writes through the Glue Iceberg REST endpoint", "A classic Databricks cluster (dedicated access mode) loads the open-source Iceberg library and points a Spark catalog at the Glue Iceberg REST endpoint, signed with the cluster's IAM role; Lake Formation hands out credentials. Bronze to silver to gold runs as ordinary Spark jobs.", "Works. But no serverless, no Lakeflow pipelines, no Unity Catalog permissions, lineage or audit on these writes, and you keep Iceberg library versions in step yourself", "Pursue only for a short migration or a few jobs"),
    ("B3. Databricks writes to foreign tables through Unity Catalog", "Unity Catalog shows Glue tables as foreign Iceberg tables. Today these are read-only in Databricks, with no partition evolution.", "Not available as of November 2026; check the Databricks docs, this changes", "Drop for now"),
    ("B4. Databricks owns bronze and silver; AWS owns gold", "Split ownership by layer: Databricks writes Unity Catalog tables, then an AWS job copies or rebuilds gold into S3 Tables.", "Two catalogs, a copy, two permission systems, lineage breaks at the seam", "Drop"),
]

A_WRITE = [
    ("Athena, Redshift, QuickSight read gold", "Glue catalog federation to Unity Catalog fetches the table's current metadata from Unity Catalog's Iceberg REST endpoint; Lake Formation hands out short-lived credentials; files are read in place, no copy.", "Read-only for these engines; grant Lake Formation SELECT on the target tables", "Pursue"),
    ("EMR, Glue Spark, Trino, Snowflake write managed Iceberg", "They connect to Unity Catalog's Iceberg REST catalog with a Databricks service principal and write managed Iceberg tables directly, governed by Unity Catalog grants.", "Their writes are not in Unity Catalog lineage; Predictive Optimization still maintains the table", "Pursue only where an AWS engine really must write"),
    ("Firehose or DMS write into the lakehouse", "They land files in a landing bucket; Auto Loader or Lakeflow Connect loads them into bronze.", "One extra hop of seconds to minutes", "Pursue"),
]

# Comparison: (group, concern, ids, (class, A), (class, B), better)
# ids name the platform concerns covered (data_platform.CONCERNS); "+" rows are extra concerns.
COMPARE = [
    ("Tables and maintenance", None),
    ("Storage and table format", "+", ("y", "Managed Iceberg tables in your own S3 bucket, at a path Unity Catalog picks under the managed location"), ("y", "Iceberg in an S3 table bucket, reached through table APIs; or Glue Iceberg in your bucket"), "Tie"),
    ("Maintenance (compaction, snapshot expiry, orphan files, statistics, clustering)", "X19", ("y", "Predictive Optimization, automatic and required on managed Iceberg; runs on serverless, billed as DBUs"), ("y", "S3 Tables, automatic and on by default; billed per object and byte processed. Predictive Optimization cannot run on these tables"), "Tie: both automatic, one owner each"),
    ("Layout: catalogs, schemas, names", "X23", ("y", "catalog.schema.table names encode environment, layer and domain; one naming scheme"), ("p", "Table bucket, namespace, table; seen from Databricks through a federated catalog with a second set of names"), "A"),
    ("ETL", None),
    ("Ingestion (sources to bronze)", "+", ("y", "Auto Loader, Lakeflow Connect, Structured Streaming; AWS services land files that Auto Loader picks up"), ("y", "Firehose and DMS write Iceberg directly; Glue jobs; Databricks only from classic clusters"), "Tie: each is native on its own side"),
    ("Bronze to silver, silver to gold", "+", ("y", "Databricks jobs, SQL and Lakeflow on serverless; EMR or Glue Spark can also write through Unity Catalog's Iceberg REST"), ("p", "Glue ETL or EMR Spark natively; Databricks only on classic clusters through the Glue REST endpoint, ungoverned by Unity Catalog"), "A"),
    ("Orchestration", "X2", ("y", "Lakeflow Jobs with table-update triggers on owned tables"), ("p", "Step Functions or Airflow (MWAA) for AWS jobs; Databricks jobs called from them; two schedulers to watch"), "A"),
    ("Metadata & control", "X1", ("y", "One catalog to read every table's schema, owner and tags from"), ("p", "Glue holds the tables; Databricks-side settings live in a second place"), "A"),
    ("Replay & backfill", "X15", ("y", "Re-runs and MERGE on Databricks; time travel on snapshots"), ("p", "Re-runs on Glue or EMR; Databricks re-runs only from classic clusters"), "A"),
    ("Streaming", None),
    ("Streaming lane", "X24", ("p", "Structured Streaming and Lakeflow are strong, but streaming tables and materialized views are Delta, so the fast lane is Delta even when gold is Iceberg"), ("y", "Firehose and Managed Flink write Iceberg into S3 Tables natively; Databricks streaming into them is not practical"), "B if streams are AWS-native; A if Databricks streams"),
    ("Semantic layer", None),
    ("Governance & semantics: owners, glossary, metric definitions", "X13", ("y", "Unity Catalog metric views, tags, owners and certified tables, used by Genie and AI/BI dashboards"), ("p", "No lake-wide metric layer on AWS: QuickSight datasets, Redshift views, SageMaker Catalog glossary; Databricks metric views would sit over read-only foreign tables"), "A"),
    ("Serving", None),
    ("BI and SQL", "+", ("y", "Databricks SQL warehouses and AI/BI; Athena, Redshift and QuickSight read gold through federation"), ("y", "Athena, Redshift Serverless and QuickSight natively; Databricks SQL reads through federation"), "Tie"),
    ("Apps and APIs", "+", ("y", "Lakebase (managed Postgres) synced from Unity Catalog tables, Databricks Apps"), ("y", "DynamoDB or Aurora fed by Glue or EMR jobs, API Gateway and Lambda"), "Tie"),
    ("AI agents and ML", "+", ("y", "Genie, Vector Search, Model Serving, MLflow, features and models governed in Unity Catalog next to the data"), ("p", "Bedrock and SageMaker AI read through Athena or Redshift; Databricks ML reads foreign tables but keeps models and features in Unity Catalog, so governance splits"), "A"),
    ("Data sharing", "+", ("y", "Delta Sharing, open and cross-cloud; Iceberg REST for engines"), ("y", "Lake Formation across AWS accounts (RAM), Redshift data sharing"), "A outside AWS; tie inside AWS"),
    ("Cost", None),
    ("Cost & FinOps", "X10", ("y", "One main bill (DBUs plus S3); serverless everywhere; Athena per TB for AWS readers; one FinOps view from system tables"), ("p", "S3 Tables storage costs a little more per GB than S3 Standard, plus monitoring and compaction fees; Glue and EMR compute; Databricks on classic clusters only; two bills, two FinOps views"), "A if Databricks does most work; B if Databricks is light or absent"),
    ("Performance & scale", "X19", ("y", "Photon, liquid clustering and Predictive Optimization on owned tables"), ("p", "AWS engines tuned on their own tables; Databricks reads foreign tables without control of their layout"), "A"),
    ("Governance and security", None),
    ("Security & access", "X11", ("y", "Unity Catalog grants and tag-based policies; Lake Formation only at the read door for AWS readers of gold"), ("p", "Lake Formation for AWS engines; Unity Catalog grants on the foreign catalog for Databricks readers; Databricks writers (B2) bypass Unity Catalog"), "A"),
    ("Privacy & PII", "X12", ("p", "Row filters and column masks are not supported on managed Iceberg today (they are on Delta); use dynamic views, or keep PII tables in Delta with Iceberg reads"), ("p", "Lake Formation row and cell filters for AWS engines; outside engines with vended credentials generally cannot read filtered tables"), "Tie: both partial with Iceberg"),
    ("Audit & run log", "X14", ("y", "Unity Catalog audit and access system tables for all Databricks work; CloudTrail for AWS reads"), ("p", "CloudTrail and Lake Formation for AWS; Databricks audit for its share; two trails to join"), "A"),
    ("Lineage", None),
    ("Lineage", "X7", ("y", "Automatic table and column lineage for every Databricks job; writes by outside engines through Iceberg REST are not recorded"), ("n", "No automatic lineage in Glue or Lake Formation; SageMaker Catalog lineage needs OpenLineage set up; B2 Databricks writes are invisible to both"), "A"),
    ("Trust", None),
    ("Contracts & schema", "X3", ("y", "Contract checks in code; schema enforced on write (informational keys not on managed Iceberg)"), ("y", "Contract checks in code; Glue schema"), "Tie"),
    ("Data quality", "X4", ("y", "Lakeflow expectations, DQX, data quality monitoring on Unity Catalog tables"), ("y", "Glue Data Quality (DQDL), Deequ"), "Tie"),
    ("Profiling", "X5", ("p", "Data profiling on Unity Catalog tables; check Iceberg support"), ("p", "Glue Data Quality rule recommendations"), "Tie"),
    ("Reconciliation", "X6", ("y", "Engine-neutral checks; one catalog to compare against"), ("y", "Engine-neutral checks"), "Tie"),
    ("See", None),
    ("Logs, metrics, traces", "X8", ("y", "System tables for jobs, queries and billing in one place"), ("p", "CloudWatch for AWS jobs plus Databricks system tables; two places"), "A"),
    ("Freshness & SLOs", "X9", ("y", "Table-update triggers and freshness monitors on owned tables"), ("p", "EventBridge events from Glue and S3 Tables; Databricks cannot trigger on foreign table updates"), "A"),
    ("Run", None),
    ("Environments & CI/CD", "X16", ("y", "Databricks bundles plus Terraform for the bucket and IAM"), ("p", "CloudFormation, CDK or Terraform for S3 Tables, Glue and Lake Formation, plus bundles for Databricks; two toolchains"), "A"),
    ("Testing", "X17", ("y", "Table-driven tests, zero-copy clones for test data"), ("y", "Table-driven tests; Iceberg branches and tags for test data"), "Tie"),
    ("Resilience & DR", "X18", ("p", "Time travel, UNDROP for 7 days; plan how catalog metadata is rebuilt in another region"), ("p", "Snapshots and AWS-managed durability; plan cross-region copies of the table bucket"), "Tie"),
    ("Self", None),
    ("Self-healing", "X20", ("y", "One catalog and one run log to detect and fix from"), ("p", "Two systems to watch and fix"), "A"),
    ("Agent assistance", "X21", ("y", "Agents read one catalog, lineage and metric views"), ("p", "Agents must read two catalogs"), "A"),
    ("Simulation", "X22", ("y", "Engine-neutral"), ("y", "Engine-neutral"), "Tie"),
    ("Strategy", None),
    ("Lock-in and portability", "+", ("p", "Unity Catalog runs on AWS, Azure and Google Cloud; but it picks managed table paths, so leaving means re-registering or rewriting"), ("n", "AWS only; S3 Tables data is reached only through table APIs"), "A"),
    ("Team and support", "+", ("y", "One vendor for the data plane; Spark and SQL skills"), ("p", "AWS-native skills for the core, Databricks skills for the guest; two vendors to call"), "Depends on the team"),
]

IF_A = [
    "Athena, Redshift and QuickSight read gold through Glue federation and cannot write. EMR, Glue Spark or Trino can write managed Iceberg through Unity Catalog's Iceberg REST, but those writes are missing from Unity Catalog lineage.",
    "Lake Formation still appears, but only at the read door for AWS engines, on curated gold tables. Expose tables without row filters or masks there, or pre-filtered gold tables.",
    "Managed Iceberg today gives up row filters, column masks and informational keys; change data feed works only on Iceberg v3 and only for Databricks readers; Lakeflow streaming tables and materialized views are Delta. Keep those tables in Delta with Iceberg reads (UniForm), or use dynamic views.",
    "Check that managed Iceberg is generally available for your region and runtime before production; parts were still marked preview in the docs we checked.",
    "Firehose and DMS cannot write straight into Unity Catalog tables: they land files, and Auto Loader loads them.",
    "Databricks is the main bill. Predictive Optimization runs on serverless and shows up as DBUs.",
    "Unity Catalog picks the paths of managed tables. Leaving later means re-registering or rewriting tables.",
]

IF_B = [
    "Databricks sees AWS tables as foreign Iceberg tables: read-only, no partition evolution, and views defined on one side are not visible on the other.",
    "Databricks can do bronze to silver to gold only from classic clusters with the open-source Iceberg library pointed at the Glue REST endpoint: no serverless, no Lakeflow pipelines, no Unity Catalog permissions, lineage or audit on those writes.",
    "No Predictive Optimization, liquid clustering control, table-update triggers or Unity Catalog masks on these tables; Genie and metric views can only sit over read-only foreign tables.",
    "Permissions live in two systems: Lake Formation for AWS engines and Unity Catalog for Databricks readers. Tables with Lake Formation row or cell filters are generally not readable by outside engines.",
    "Lineage is fragmented: nothing automatic on the AWS side, and Databricks writes through the Glue endpoint are invisible to Unity Catalog.",
    "Two bills, two toolchains (CloudFormation or CDK and Databricks bundles), two monitoring places.",
    "AWS only. Moving to Azure, Fabric or Google Cloud later means a new catalog and new permissions.",
]

CASES = [
    ("United Airlines", "Architecture A, with Delta + Iceberg reads",
     "Before: petabytes in bronze, silver and gold, catalogued in Unity Catalog. Redshift could not see them, so tables were copied into Redshift storage with sync pipelines and a manually synced catalog, which AWS's write-up calls operationally expensive and prone to drift.",
     "After: Databricks does all processing and owns the tables (Delta with UniForm). A Glue federated catalog fetches metadata from Unity Catalog's Iceberg REST endpoint, Lake Formation vends scoped credentials, and Redshift Serverless reads the files in place. About $30K a month of duplicate ETL removed; 30 tables in production, 70 rolling out, hundreds planned.",
     "Grant Lake Formation SELECT on the target tables, not on the resource link; roll out the busiest tables first; name external schemas so readers know the data is federated.",
     "https://aws.amazon.com/blogs/big-data/how-united-airlines-uses-amazon-redshift-and-aws-glue-data-catalog-federation-to-query-databricks-managed-data/"),
    ("Razor Group", "Architecture B, without Databricks",
     "Before: more than 1,000 SQL models on always-on Redshift clusters, 98% of compute spent on batch ETL, data 4 to 6 hours old, workloads fighting for one cluster.",
     "After: S3 Tables (Iceberg) in bronze, silver and gold, Glue and Lake Formation as catalog and permissions, Spark on EC2 Spot for ETL, Athena for ad-hoc SQL, Redshift Serverless only for Tableau. About 40% of compute removed by moving ingestion alone, data fresh in minutes, Iceberg time travel saved over 35 Redshift hours a week.",
     "About 30% of SQL models needed a person to convert; running old and new side by side with row-by-row comparison avoided downtime; S3 Tables removed compaction and snapshot chores.",
     "https://aws.amazon.com/blogs/big-data/razor-groups-journey-to-a-modern-data-lakehouse-on-aws/"),
    ("HelloFresh", "Architecture A, Unity Catalog as the Iceberg REST catalog for many engines",
     "A decentralised mix of tools needed one table format and one catalog.",
     "Iceberg as the format, Unity Catalog serving as the Iceberg REST catalog for Spark, Flink and Snowflake.",
     "A conference talk: design, not audited numbers.",
     "https://www.databricks.com/dataaisummit/session/apache-iceberg-unity-catalog-hellofresh"),
    ("Riskified", "Architecture A, native Iceberg in Unity Catalog",
     "Wanted tables any engine could read, without tying the data to Databricks.",
     "Writes Iceberg tables through Unity Catalog that any Iceberg client can read, which the team describes as future-proofing the architecture.",
     "A press-release quote: direction, not detail.",
     "https://www.databricks.com/company/newsroom/press-releases/databricks-eliminates-table-format-lock-and-adds-capabilities"),
    ("Grab and Insider", "Storage step only: Hive tables to Iceberg, on either architecture",
     "Parquet under a Hive-style Glue catalog: too many small files, unsafe concurrent writes, slow file listing.",
     "Iceberg tables; Insider reports about 90% lower S3 costs.",
     "An in-place migration carries small files over, so rewrite or compact as you migrate; expect lock contention, timestamp mismatches and a temporary S3 cost spike (Grab).",
     "https://engineering.grab.com/our-journey-to-apache-iceberg-adoption"),
]

ANTI = [
    ("Copying lake data into a warehouse for a second engine", "Two copies, sync pipelines, drift (United before)", "Let the second engine read the same Iceberg files through federation"),
    ("The same table registered in Glue and Unity Catalog, both writing", "Two pointers to one table: writes conflict, one clean-up deletes files the other needs", "One authoritative catalog; the other federates it read-only"),
    ("Permissions defined twice for the same readers", "A row filter in Unity Catalog does not exist in Lake Formation, and the reverse", "Fine-grained rules where the table is owned; other engines get pre-filtered gold"),
    ("An always-on warehouse running batch ETL", "Paying for idle capacity while workloads fight (Razor before)", "Separate compute per workload, serverless where possible"),
    ("Iceberg maintenance with no owner", "Snapshots and orphan files pile up, queries slow, storage grows", "One owner of chores: Predictive Optimization or S3 Tables"),
]

# Added 12 Nov 2026 on request: who is on A, who is on B, where each wins and loses, which AWS
# services A shops keep, and whether any benchmark tells a clear A-versus-B story.
WHO = [
    # company, side, what they run, where they win, where they lose or what to watch, evidence
    ("United Airlines", "A", "Databricks writes everything into Unity Catalog (Delta with Iceberg reads); Redshift Serverless reads gold through Glue federation and Lake Formation.",
     "About $30K a month of copy pipelines removed; one catalog; Redshift users keep their tool.",
     "Redshift is read-only; only Iceberg or UniForm tables are visible; the Lake Formation grant must be on the target table, not the resource link.",
     "Detailed AWS blog"),
    ("Mastercard", "A", "Unity Catalog is the single source of truth, federated into AWS Glue so AWS engines can use the same tables.",
     "Ended the multi-catalog struggle; engineers pick the engine per job without metadata drifting.",
     "No numbers published.", "Summit talk abstract (2026)"),
    ("Decathlon", "A, moved from B", "Left the AWS Glue catalog for Unity Catalog because Glue metadata management strained at thousands of tables; kept EMR, Athena, Polars and DuckDB working against Unity Catalog.",
     "One governance layer at scale while outside engines stay open.",
     "The only public move between the two we found, and it went from B to A; no numbers published.", "Summit talk abstract"),
    ("HelloFresh", "A", "Iceberg as the format, Unity Catalog as the Iceberg REST catalog for Spark, Flink and Snowflake.",
     "One catalog across many tools.", "Design talk, no numbers.", "Summit talk"),
    ("Riskified", "A", "Writes Iceberg through Unity Catalog so any Iceberg client can read it.",
     "Avoids tying the data to one engine.", "A press quote, no detail.", "Press release"),
    ("Indeed", "B, no Databricks", "Moved a 101 PB lake (18,000 datasets, 190,000 queries a day) from Hive to Iceberg on S3 Tables, linked to its existing Glue catalog; Athena and EMR Spark among four engines.",
     "Expected 10% lower cost, 1,000+ developer hours a year back, 10x more transactions per second, team onboarding from a day to minutes.",
     "Most numbers are labelled expected, not measured; the talk lists Lake Formation integration, query performance and different logging as the hard parts.", "AWS case study"),
    ("Razor Group", "B, no Databricks", "S3 Tables in bronze, silver and gold; Glue and Lake Formation; Spark on EC2 Spot; Athena; Redshift Serverless only for Tableau.",
     "About 40% of compute removed by moving ingestion alone; data minutes old instead of 4 to 6 hours.",
     "About 30% of 1,000+ SQL models needed a person to convert.", "Detailed AWS blog"),
    ("Pendulum", "B, no Databricks", "Glue streaming and Glue ETL write three S3 table buckets; Athena, EMR Serverless, OpenSearch and QuickSight read.",
     "About 40% lower cost (mostly Glue DPUs spent on home-made compaction), daily job 1 hour to 10 minutes, about 70% faster queries.",
     "The before state was hand-written maintenance scripts, so part of the win is simply having an owner of the chores.", "AWS blog"),
    ("Tubular Labs", "B, no Databricks", "Spark on EKS writes 70 TB, 25 billion rows, into S3 Tables with write-audit-publish on Iceberg branches.",
     "Merge job 6 to 8 hours down to under 2; recovery from failures 12 to 16 hours down to about 40 minutes; about half of engineering time back.",
     "The before state was raw Parquet with no transactions, so most of the win is Iceberg itself, not the catalog.", "AWS blog"),
    ("Comcast", "B, no Databricks", "GraphQL on API Gateway and Lambda reads S3 Tables through its Iceberg REST endpoint; Athena, EMR and PyIceberg read the same tables.",
     "80x more concurrent requests, 38% lower cost, median latency 820 to 590 ms.",
     "Replaced per-team database copies, not another catalog.", "AWS blog"),
    ("Amica", "B, no Databricks", "S3 table buckets with Lake Formation grants tied to Identity Center groups; Athena reads.",
     "Fine-grained access for analysts without copies.", "No numbers published.", "AWS blog"),
]

MOVES = [
    ("B to A", "Decathlon", "Catalog from AWS Glue to Unity Catalog at thousands of tables; EMR, Athena, Polars and DuckDB kept reading.",
     "One governance layer that held up at scale; outside engines stayed open.", "No numbers; a summit talk abstract.", "Real move, unmeasured"),
    ("B to A", "Outreach", "Glue tables brought under Unity Catalog with the one-click foreign-to-managed conversion.",
     "\"Eliminated months of migration planning\" and sped up adoption of Unity Catalog and serverless.", "One quote in a Databricks post; no cost or speed figures.", "Real move, unmeasured"),
    ("A to B (roughly)", "Kargo", "ML pipelines left Databricks notebooks and Delta for Glue ETL writing Iceberg, Athena for training slices, SageMaker for training and serving.",
     "Lower compute cost from removing always-on clusters; pay-per-query Athena; easier CI/CD and reproducibility.", "Qualitative only, in an AWS blog; the catalog is not named and Unity Catalog was not the owner before.", "Weak: left Databricks for an ML-ops reason, not a catalog reason"),
    ("A to B", "Nobody else we could find", "No public team moved tables from Unity Catalog ownership to S3 Tables, Glue and Lake Formation while keeping Databricks.",
     "-", "-", "Absence is the finding"),
]

AWS_IN_A = [
    ("Amazon S3", "Holds every file of every layer, in your own bucket", "Everyone on A", "Keep"),
    ("Redshift Serverless", "Reads gold in place through Glue federation; no copy into Redshift storage", "United Airlines", "Keep if analysts already live there"),
    ("Athena", "Ad-hoc SQL on gold through Glue federation, paid per TB scanned", "Decathlon; AWS federation guide", "Keep for occasional readers"),
    ("EMR and Glue Spark", "Read, and can write, managed Iceberg through Unity Catalog's Iceberg REST catalog", "Decathlon; AWS EMR with Unity Catalog guide", "Keep where a job must stay on AWS; writes miss Unity Catalog lineage"),
    ("Glue Data Catalog", "Becomes a door, not an owner: a federated catalog that mirrors Unity Catalog", "United Airlines, Mastercard", "Keep as the door for AWS engines"),
    ("Lake Formation", "Hands short-lived credentials to AWS readers of gold", "United Airlines", "Keep, read door only"),
    ("IAM, KMS, PrivateLink", "Roles for the bucket, encryption keys, private network path between Databricks and your VPC", "Databricks and AWS networking guides", "Keep, always"),
    ("Firehose, DMS, MSK, Kinesis", "Land files or streams in a landing bucket that Auto Loader picks up", "Pattern in the guides; no named case", "Keep for capture"),
    ("QuickSight", "Dashboards over Athena or Redshift on federated gold", "Pattern in the guides; no named case", "Keep if already paid for"),
    ("Step Functions, MWAA", "Only for AWS-side jobs; Lakeflow Jobs runs the Databricks side", "Pattern; two schedulers is a cost", "Drop where Lakeflow can do it"),
]

BENCH = [
    ("S3 Tables: up to 3x faster queries, up to 10x more transactions per second", "AWS", "S3 Tables against Iceberg in an ordinary bucket that nobody compacts", "No. It measures maintained against unmaintained tables."),
    ("S3 Tables: about 2x faster than medium-file Iceberg and 4.6x to 37.6x faster than small-file Iceberg on Glue Spark (TPC-H, 104 GB); ingestion 1.7x to 3.1x faster; Athena was slower on S3 Tables than on plain Iceberg; storage about 17.5% dearer", "Loka (AWS partner)", "S3 Tables against self-managed Iceberg, same AWS engines", "No. Same catalog family, different maintenance."),
    ("Predictive Optimization: up to 20x faster selective queries, 2x lower storage cost; Anker 2x faster queries, 50% lower storage", "Databricks", "Unity Catalog managed tables against unmanaged ones", "No. Same idea as the S3 Tables claim, on the other side."),
    ("Redshift Serverless on Iceberg over 2x faster in 2025 (TPC-DS 10 TB)", "AWS", "Redshift this year against Redshift last year", "No. Helps both A and B, since Redshift reads Iceberg either way."),
    ("EMR Spark 4.5x faster than open-source Spark on Iceberg (TPC-DS 3 TB)", "AWS", "EMR runtime against open-source Spark", "No. An engine claim."),
    ("StarRocks 1.3x faster than Databricks Photon on catalog queries (TPC-DS 1 TB)", "CelerData (vendor)", "Engines; Photon ran on Delta, not managed Iceberg", "No. Engines, and a vendor test."),
    ("A head-to-head: same data, A against B, both engines, ETL plus queries plus chores plus cost", "Nobody, as of November 2026", "-", "This is the benchmark that would tell the story, and it does not exist."),
]

FAIR_BENCH = [
    ("Data", "TPC-DS at 1 TB as gold, plus a daily MERGE of 1% changed rows into silver"),
    ("Run A", "Databricks serverless writes managed Iceberg in Unity Catalog with Predictive Optimization; Athena and Redshift read gold through Glue federation"),
    ("Run B", "Glue or EMR Spark writes S3 Tables with Glue and Lake Formation; Databricks reads gold as foreign tables"),
    ("Measure", "ETL wall time and cost, query time per engine on both sides, maintenance cost (DBUs or S3 Tables fees), freshness from write to readable, and hours of setup"),
    ("Expected result", "Each side wins where its own engines write and maintain the tables; the guest side pays in features and governance, not speed. That is the claim to test."),
]

SCORE = [
    ("Databricks does most of the work (pipelines, ML, Genie, most SQL)", "A", "Everything Databricks offers works on owned tables; AWS engines still read gold in place."),
    ("AWS engines do most of the work; Databricks is used by one team, or not at all", "B", "S3 Tables, Glue and Lake Formation are native for Glue, EMR, Athena, Redshift, Firehose and Flink. Databricks reads through federation."),
    ("Streams arrive through Firehose or Managed Flink and must be queryable in Athena within seconds", "B for that lane", "Keep that domain AWS-owned and let Databricks read it; this is the one place a split by domain makes sense."),
    ("Separate teams already committed to each side, by domain", "Split by domain", "Each table still has exactly one owner; catalogs federate each other read-only. Highest effort to run."),
    ("You may move to Azure, Fabric or Google Cloud later", "A", "Unity Catalog is the same on every cloud; only the AWS reader door changes."),
]

QA = [
    ("Can Databricks write bronze to silver to gold when AWS owns the catalog?", "Only from classic clusters, using the open-source Iceberg library pointed at the Glue Iceberg REST endpoint with Lake Formation credentials. It works, but those writes skip Unity Catalog permissions, lineage and audit, cannot use serverless or Lakeflow pipelines, and you maintain library versions. Through Unity Catalog itself, AWS-owned tables are read-only foreign tables."),
    ("Can AWS engines write when Unity Catalog owns the catalog?", "Spark on EMR or Glue, Trino and Snowflake can write managed Iceberg tables through Unity Catalog's Iceberg REST catalog with a Databricks service principal, governed by Unity Catalog grants. Athena, Redshift and QuickSight read gold through Glue federation and do not write. Firehose and DMS land files that Auto Loader loads."),
    ("Are Glue with Lake Formation and the SageMaker lakehouse the same thing?", "Mostly. Glue Data Catalog is the catalog, Lake Formation is the permissions on it, and the SageMaker lakehouse is AWS's umbrella name for the two, reaching across S3, S3 Tables, Redshift storage and federated catalogs. SageMaker Catalog (formerly DataZone) is a different, business-facing layer."),
    ("Where does Redshift fit?", "As one more reader of the same Iceberg tables, through federation, if the client already uses it. Loading data into Redshift's own storage creates a second copy with its own permissions, which is the pattern the case studies moved away from."),
    ("Why not let both catalogs own tables?", "Two writers on one table means two pointers, conflicting commits and clean-ups that delete each other's files. Split by domain only if teams force it, and even then every table has exactly one owner."),
    ("Is Iceberg the right format on Databricks?", "It is a sound choice for openness. Inside Databricks, Delta still has features managed Iceberg lacks today (row filters, column masks, keys, Lakeflow streaming tables). Delta with Iceberg reads (UniForm) gives AWS engines Iceberg without giving those up, so many teams mix the two."),
]

SOURCES = [
    ("Apache Iceberg in Databricks", "https://docs.databricks.com/aws/en/iceberg"),
    ("Databricks external access and the Iceberg REST catalog", "https://docs.databricks.com/aws/en/external-access/"),
    ("Amazon S3 Tables integration with AWS analytics", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables-integration-overview.html"),
    ("Amazon SageMaker lakehouse architecture", "https://aws.amazon.com/sagemaker/lakehouse/"),
    ("AWS: access S3 Iceberg tables from Databricks through the Glue Iceberg REST catalog", "https://aws.amazon.com/blogs/big-data/access-amazon-s3-iceberg-tables-from-databricks-using-aws-glue-iceberg-rest-catalog-in-amazon-sagemaker-lakehouse/"),
    ("AWS: access Databricks Unity Catalog data through Glue catalog federation", "https://aws.amazon.com/blogs/big-data/access-databricks-unity-catalog-data-using-catalog-federation-in-the-aws-glue-data-catalog"),
    ("AWS: catalog federation for Iceberg tables in the Glue Data Catalog", "https://aws.amazon.com/blogs/big-data/introducing-catalog-federation-for-apache-iceberg-tables-in-the-aws-glue-data-catalog"),
    ("AWS: United Airlines, Redshift and Glue federation to Databricks", "https://aws.amazon.com/blogs/big-data/how-united-airlines-uses-amazon-redshift-and-aws-glue-data-catalog-federation-to-query-databricks-managed-data/"),
    ("AWS: Razor Group's journey to a lakehouse on AWS", "https://aws.amazon.com/blogs/big-data/razor-groups-journey-to-a-modern-data-lakehouse-on-aws/"),
    ("Grab: our journey to Apache Iceberg", "https://engineering.grab.com/our-journey-to-apache-iceberg-adoption"),
    ("Insider: migrating a production data lake to Iceberg", "https://medium.com/insiderengineering/how-we-migrated-our-production-data-lake-to-apache-iceberg-4d6892eca6e6"),
    ("LakeOps: cross-catalog sync for Polaris, Glue and Unity (third party)", "https://lakeops.dev/blog/cross-catalog-sync-polaris-glue-unity"),
    ("Onehouse: the catch in Databricks Iceberg support (critic)", "https://www.onehouse.ai/blog/databricks-iceberg-support-has-a-catch-its-called-unity-catalog"),
    ("Mastercard: breaking data silos with multi-engine catalog federation (talk)", "https://www.databricks.com/dataaisummit/session/sponsored-aws-breaking-data-silos-multi-engine-catalog-federation"),
    ("Decathlon: race to unified governance, Glue to Unity Catalog (talk)", "https://www.databricks.com/dataaisummit/session/decathlons-race-unified-governance-securing-interoperability-scale"),
    ("AWS: Indeed moves to S3 Tables", "https://aws.amazon.com/solutions/case-studies/indeed-s3-tables-case-study/"),
    ("AWS: Pendulum, 6x faster processing with S3 Tables", "https://aws.amazon.com/blogs/storage/how-pendulum-achieves-6x-faster-processing-and-40-cost-reduction-with-amazon-s3-tables"),
    ("AWS: Tubular Labs rebuilds a 70 TB pipeline on S3 Tables", "https://aws.amazon.com/blogs/storage/how-tubular-labs-reclaimed-50-of-engineering-capacity-by-rebuilding-their-70tb-pipeline-on-apache-iceberg-and-amazon-s3-tables/"),
    ("AWS: Comcast scales analytics 80x with S3 Tables", "https://aws.amazon.com/blogs/storage/how-comcast-scaled-analytics-80x-while-cutting-costs-38-with-graphql-and-amazon-s3-tables/"),
    ("AWS: Amica on S3 Tables", "https://aws.amazon.com/blogs/industries/amica-unlocks-value-from-core-insurance-applications-with-amazon-s3-tables/"),
    ("AWS: S3 Tables compaction, up to 3x faster queries", "https://aws.amazon.com/blogs/storage/how-amazon-s3-tables-use-compaction-to-improve-query-performance-by-up-to-3-times"),
    ("Loka: test driving S3 Tables (TPC-H)", "https://loka.com/blog/test-driving-s3-tables"),
    ("Databricks: Predictive Optimization, faster queries and lower cost", "https://www.databricks.com/blog/predictive-optimization-automatically-delivers-faster-queries-and-lower-tco"),
    ("AWS: 2x faster Iceberg queries on Redshift", "https://aws.amazon.com/blogs/big-data/achieve-2x-faster-data-lake-query-performance-with-apache-iceberg-on-amazon-redshift"),
    ("AWS: EMR Spark and Iceberg 4.5x faster than open-source Spark", "https://aws.amazon.com/blogs/big-data/run-apache-spark-and-iceberg-4-5x-faster-than-open-source-spark-with-amazon-emr"),
    ("CelerData: TPC-DS benchmark (vendor)", "https://docs.celerdata.com/BYOC/docs/benchmarking/TPC_DS_Benchmark"),
    ("Databricks: from the AWS Glue catalog to Unity Catalog, end to end", "https://community.databricks.com/t5/technical-blog/from-aws-glue-catalog-to-databricks-unity-catalog-an-end-to-end/ba-p/157190"),
    ("Databricks: migrating foreign HMS and Glue tables to Unity Catalog (Outreach quote)", "https://community.databricks.com/t5/technical-blog/upgrade-your-hms-and-aws-glue-tables-how-to-guide-for-migrating/ba-p/138835"),
    ("AWS: Kargo moves ML workloads from Databricks to AWS", "https://aws.amazon.com/blogs/industries/migrating-enterprise-ml-workloads-from-databricks-to-aws-for-large-scale-ml/"),
]


# ----------------------------------------------------------------------------------- page
def _cell(c):
    k, t = c
    return f'<td class="{k}">{E(t)}</td>'


def compare_table():
    out = '<div class="tw"><table class="t cmp"><tr><th>Concern</th><th>A: Unity Catalog owns</th><th>B: AWS owns</th><th>Better</th></tr>'
    for row in COMPARE:
        if row[1] is None:
            out += f'<tr class="grp"><td colspan="4">{E(row[0])}</td></tr>'
            continue
        name, ids, a, b, win = row
        tag = "" if ids == "+" else f' <span style="color:var(--muted);font-size:12px">{E(ids)}</span>'
        out += f"<tr><td><b>{E(name)}</b>{tag}</td>{_cell(a)}{_cell(b)}<td class=\"win\">{E(win)}</td></tr>"
    return out + "</table></div>"


def verdict_table(head, rows, bold_last=True):
    h = "".join(f"<th>{E(x)}</th>" for x in head)
    r = "".join("<tr>" + "".join(f"<td>{'<b>' + E(c) + '</b>' if i == 0 or (bold_last and i == len(row) - 1) else E(c)}</td>" for i, c in enumerate(row)) + "</tr>" for row in rows)
    return f'<div class="tw"><table class="t"><tr>{h}</tr>{r}</table></div>'


def tally():
    a = sum(1 for r in COMPARE if r[1] is not None and r[4] == "A")
    b = sum(1 for r in COMPARE if r[1] is not None and r[4].startswith("B"))
    tie = sum(1 for r in COMPARE if r[1] is not None and r[4].startswith("Tie"))
    other = sum(1 for r in COMPARE if r[1] is not None) - a - b - tie
    return a, b, tie, other


def cases_html():
    out = ""
    for name, kind, before, after, lesson, url in CASES:
        out += (f'<div class="case"><h3>{E(name)}<span class="tag">{E(kind)}</span></h3>'
                f'<p><b>Before.</b> {E(before)}</p><p><b>After.</b> {E(after)}</p><p><b>Lesson.</b> {E(lesson)}</p>'
                f'<p><a href="{url}">Read the write-up</a></p></div>')
    return out


def page():
    url = f"{SITE}{URL_PATH}"
    a, b, tie, other = tally()
    names = C.table(["Name", "What it really is"], NAMES)
    bw = verdict_table(["Way", "How it works", "What you give up", "Verdict"], B_WRITE)
    aw = verdict_table(["Who", "How it works", "Limit", "Verdict"], A_WRITE)
    anti = C.table(["Bad pattern", "Why it hurts", "Good pattern"], ANTI)
    score = verdict_table(["If this is true", "Pick", "Why"], SCORE, bold_last=False)
    who = verdict_table(["Company", "Side", "What they run", "Where they win", "Where they lose, or what to watch", "Evidence"], WHO, bold_last=False)
    aws_in_a = verdict_table(["AWS service", "Its job on A", "Who shows it", "Verdict"], AWS_IN_A)
    bench = verdict_table(["Claim", "Who measured", "What it really compares", "Does it pick A or B?"], BENCH)
    moves = verdict_table(["Direction", "Company", "What moved", "Gain claimed", "Measured?", "Verdict on the evidence"], MOVES)
    fair = verdict_table(["Part", "What to do"], FAIR_BENCH, bold_last=False)
    ifa = "".join(f"<li>{E(x)}</li>" for x in IF_A)
    ifb = "".join(f"<li>{E(x)}</li>" for x in IF_B)
    src = "".join(f'<li><a href="{u}">{E(n)}</a></li>' for n, u in SOURCES)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/data-engineering/">Data engineering</a> › Iceberg lakehouse on AWS with Databricks</p>
<p class="eyebrow" style="margin-top:22px">Data engineering · free guide · one page</p>
<h1>{E(TITLE)}</h1>
<p class="lede">You want an open lakehouse on AWS, with Apache Iceberg as the table format and Databricks in the picture. AWS offers S3 Tables, Glue, Lake Formation and the SageMaker lakehouse; Databricks offers Unity Catalog. The names spin heads, but there is one decision underneath: <b>which catalog owns the tables</b>. This page draws the whole platform first, then the two physical designs, then compares them concern by concern and picks a winner.</p>
<div class="tf">
<div class="box"><b>Short answer:</b> if Databricks does most of the work, let <b>Unity Catalog own the tables</b> (Architecture A): managed Iceberg in your own S3 bucket, Predictive Optimization doing the chores, and Athena, Redshift and QuickSight reading gold in place through Glue federation. If AWS engines do most of the work and Databricks is a light guest, let <b>AWS own them</b> (Architecture B): S3 Tables with Glue and Lake Formation. Never let both own the same table.</div>

<section id="concept"><p class="eyebrow">Step 1 · the conceptual big picture</p><h2>The whole data platform, with every concern</h2>
<p>Before any product name, here is the platform as jobs. Data comes from sources on the left, moves along one line (ingest, bronze, silver, gold, semantic) and reaches consumers on the right. Under the line sit five layers every table needs. Along the bottom are the 24 concerns that cut across every hop; each is explained on <a href="/learn/data-systems/platform/">the data platform page</a>.</p>
{fig(drawing_concept(), "Look at the thick box. Storage, the table format and compute are easy to agree on. Who owns the catalog decides who can write, who sets permissions, who sees lineage and who cleans the tables.")}
<p>Why the catalog matters so much: an Iceberg write only becomes real when the catalog swaps its pointer to the new metadata file. Whoever holds that pointer controls writes, permissions and clean-up. Every other engine is a guest. See <a href="/learn/table-maintenance/#pointer">Who maintains your tables</a> for the picture.</p></section>

<section id="names"><p class="eyebrow">Step 2 · the AWS names, decoded</p><h2>Six names, three jobs</h2>
<p>Several of these are layers of the same thing, which is why they confuse. Storage is S3 Tables. Catalog and permissions are Glue plus Lake Formation, sold together as the SageMaker lakehouse. Unity Catalog does both catalog and permissions on the Databricks side.</p>
{names}</section>

<section id="arch-b"><p class="eyebrow">Step 3 · physical design B</p><h2>Architecture B: AWS owns the catalog, Databricks is a guest</h2>
<p>Iceberg tables live in an S3 table bucket. The Glue Data Catalog holds each table's pointer and Lake Formation holds the permissions. S3 Tables compacts, expires snapshots and removes unreferenced files by itself. AWS engines write and read natively.</p>
{fig(drawing_arch_b(), "Owners on the left write through Glue. AWS readers on the right read through Glue. Databricks, dashed, is a guest.")}
<h3>Can Databricks do bronze to silver to gold here?</h3>
<p>This is the question most teams get wrong. Through Unity Catalog, AWS-owned Iceberg tables appear as <b>foreign tables, which are read-only</b>. The only way for Databricks to write them today is around Unity Catalog. Four ways, with verdicts:</p>
{bw}
<p>Databricks' support for foreign Iceberg tables changes every few months. Check the current docs before you rule writes in or out.</p></section>

<section id="arch-a"><p class="eyebrow">Step 4 · physical design A</p><h2>Architecture A: Unity Catalog owns the catalog, AWS engines are guests</h2>
<p>Iceberg tables live in your own S3 bucket as Unity Catalog <b>managed Iceberg</b> tables. Unity Catalog holds the pointer, the grants, the lineage and the audit. Predictive Optimization does the chores. Databricks writes every layer on serverless compute.</p>
{fig(drawing_arch_a(), "Owners on the left write through Unity Catalog. Guests on the right read in place, and Iceberg engines can even write, through Unity Catalog's Iceberg REST catalog.")}
<h3>And the other way round: can AWS engines work here?</h3>
{aw}</section>

<section id="writes"><p class="eyebrow">Step 5 · the asymmetry</p><h2>Who can write where</h2>
<p>This grid is the heart of the decision. Unity Catalog lets outside Iceberg engines write managed tables through its REST catalog, under its own grants. Glue lets Databricks write only around Unity Catalog. So A keeps the door open both ways; B closes Databricks' governed door.</p>
{fig(drawing_writes(), "Green: full, governed. Butter: works with a limit. Rose: read-only, or writes that skip governance.")}</section>

<section id="compare"><p class="eyebrow">Step 6 · concern by concern</p><h2>A and B compared on every concern</h2>
<p>Every one of the 24 platform concerns is here (their ids in grey), plus the serving, ingestion and strategy concerns. Green works fully, yellow works with a limit, rose does not. Checked against AWS and Databricks docs in November 2026; Iceberg support on both sides changes often.</p>
{compare_table()}
<div class="box"><b>Tally:</b> A is better on {a} concerns, B on {b}, they tie on {tie}, and {other} depend on your situation (streaming, cost, sharing, team). B's wins are real but narrow: AWS-native streaming, and cost when Databricks is light or absent.</div></section>

<section id="restrict"><p class="eyebrow">Step 7 · what each one restricts</p><h2>What you accept with each</h2>
<div class="two">
<div class="card"><h3>If you go with A (Unity Catalog owns)</h3><ul>{ifa}</ul></div>
<div class="card"><h3>If you go with B (AWS owns)</h3><ul>{ifb}</ul></div>
</div></section>

<section id="cases"><p class="eyebrow">Step 8 · evidence</p><h2>Case studies: from a bad design to a good one</h2>
<p>We found clear public write-ups of Architecture A (United Airlines, with Delta tables read as Iceberg) and of Architecture B without Databricks (Razor Group). We found no public case of B with Databricks as the main writer, which is itself a finding. Numbers come from the companies' or vendors' own blogs and are not audited.</p>
{cases_html()}
<h3>The bad patterns these teams left behind</h3>
{anti}</section>

<section id="market"><p class="eyebrow">Step 9 · the market</p><h2>Who chose A, who chose B, and what the benchmarks really say</h2>
<p>We looked for every public team running Iceberg on AWS that says which catalog owns its tables. The picture is very clean. <b>Teams with Databricks at the centre chose A. Teams that chose B do not use Databricks at all.</b> We found no public team running B with Databricks as a real writer, and the public moves between the two that keep Databricks (Decathlon, Outreach) all went from B to A.</p>
{who}
<div class="two">
<div class="card"><h3>Where A wins and loses in practice</h3><ul>
<li><b>Wins:</b> copy pipelines into Redshift disappear (United, about $30K a month); one catalog stays the truth for many engines (Mastercard, HelloFresh); it survived scale where Glue strained (Decathlon).</li>
<li><b>Loses:</b> AWS readers are read-only; only Iceberg or UniForm tables cross the door; Lake Formation grants have gotchas; almost none of these teams publish numbers, so A's case rests on design talks more than measurements.</li></ul></div>
<div class="card"><h3>Where B wins and loses in practice</h3><ul>
<li><b>Wins:</b> big, measured cost and speed gains (Razor 40% compute, Pendulum 40% cost and 6x jobs, Tubular merges 6 to 8 hours down to under 2, Comcast 38% cost).</li>
<li><b>Loses:</b> those gains are mostly against a bad before state (no maintenance, raw Parquet, an always-on warehouse), not against A; Lake Formation sharing and logging are the hard parts (Indeed; one team lost a month to cross-account sharing); none of them run Databricks.</li></ul></div>
</div>
<h3>Has anyone moved from one to the other, and did it pay?</h3>
<p>Moves are rare and almost never measured. Every B-to-A move we found was a Databricks-centred team leaving the Glue catalog; the only A-to-B-like move left Databricks entirely, for reasons about ML operations rather than the catalog. Nobody published a before-and-after cost or speed number for a pure catalog move in either direction.</p>
{moves}
<h3>On A, which AWS services do people still use?</h3>
<p>Choosing A does not mean leaving AWS. It means AWS stops owning the table pointer. Almost every AWS service keeps a job; Glue and Lake Formation change from owner to door.</p>
{aws_in_a}
<h3>Is there a benchmark that names a clear winner?</h3>
<p><b>No.</b> Every benchmark we found compares one side against a weaker version of itself, or one engine against another. None runs the same data through A and B. Read each claim for what it actually compares:</p>
{bench}
<div class="box"><b>The clear story the numbers do tell:</b> the big wins on both sides come from two things, giving the tables one owner of the chores (S3 Tables or Predictive Optimization) and deleting copies. Neither depends on which catalog you pick. So speed and cost do not decide A versus B; <b>where your work runs</b> does, because the side that writes gets every feature and the guest side gets read-only access. That is why Databricks-centred teams land on A and AWS-only teams land on B.</div>
<h3>The benchmark that would settle it</h3>
<p>If a client wants numbers, run this small test on their own account before committing. It is a few days of work and answers the question for their workload, which no public benchmark does.</p>
{fair}
</section>

<section id="winner"><p class="eyebrow">Step 10 · synthesis</p><h2>Who wins</h2>
<div class="verdict"><b>Winner for an AWS platform where Databricks does most of the work: Architecture A.</b> One owner for every table, every Databricks feature working on it, automatic lineage and audit, serverless everywhere, AWS engines reading gold in place, and Iceberg engines still able to write through Unity Catalog's REST catalog. It is also the design that moves to Azure, Fabric or Google Cloud with the fewest changes.<br><br>
<b>Architecture B wins only when AWS is the real home:</b> Glue, EMR, Athena, Redshift, Firehose and Flink do the work, and Databricks is a light guest or absent. Then S3 Tables, Glue and Lake Formation are native, cheaper and simpler, as Razor Group shows.</div>
{score}
<p>Whichever you choose, write it down as one rule: <b>one table, one catalog, one writer path, one owner of the chores.</b> List the other architecture under "options considered" with its reason; that is what a reviewer will ask for.</p></section>

<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(QA)}</section>
<section id="sources"><p class="eyebrow">Sources</p><h2>Checked against</h2>
<p>Checked in November 2026. Federation writes, managed Iceberg status and fine-grained access for outside engines change every few months; check before you commit.</p><ul>{src}</ul></section>
<section id="next"><p class="eyebrow">Related</p><h2>Where it connects</h2>
<p><a href="/learn/data-systems/platform/">The data platform, whole</a> · <a href="/learn/table-maintenance/">Who maintains your tables</a> · <a href="/learn/delta-vs-iceberg/">Delta vs Iceberg on Databricks</a> · <a href="/learn/data-platform-architecture/aws-databricks/">AWS + Databricks, ETL end to end</a> · <a href="/learn/aws-data-services/">AWS data services catalog</a> · <a href="/learn/streaming/">Streaming on AWS and Databricks</a></p></section>
</div>"""
    crumbs = [("Data engineering", f"{SITE}/data-engineering/"), ("Iceberg lakehouse on AWS with Databricks", url)]
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": TITLE, "description": DESC, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": t}} for q, t in QA]}]
    head = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(TITLE, DESC, url, body, head)


def check_concerns():
    """Refuse to build if a platform concern is missing from the comparison."""
    import data_platform as DP
    want = {c[0] for c in DP.CONCERNS}
    have = {r[1] for r in COMPARE if r[1] not in (None, "+")}
    missing = sorted(want - have, key=lambda x: int(x[1:]))
    if missing:
        sys.exit(f"comparison is missing concerns: {missing}")


def main():
    check_concerns()
    out = ROOT / "learn" / "iceberg-lakehouse-aws-databricks"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("iceberg lakehouse ->", out / "index.html")


if __name__ == "__main__":
    main()
