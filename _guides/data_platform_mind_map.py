"""The data platform architecture mind map: every concern against Azure, Databricks, AWS, GCP and an open-source
stack, then cut three ways (X what the platform gives, Y the horizontal asset we write once, Z what each platform
still has to implement), at /learn/data-platform-mind-map/.

    python3 _guides/data_platform_mind_map.py

Written 20 Nov 2026. The 24 concerns and their five families are the site's own list (learn/data-systems/platform,
catalog X1 to X24). Product names for the concerns that /_paths/data.py CONCEPTS already covers are taken from there,
so this page agrees with the rest of the site; the other cells were written today from general knowledge and are NOT
checked against each vendor's current documentation (the page says so). Y comes from the platform's concern list
(who provides it, where it starts in the code). Z comes from the Azure task list (AZ-1..AZ-11) and the platform's
adapter list; GCP has no cloud-layer file at all, so every GCP entry in Z is "not started".
Public page: no employer, no account, no personal names.
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("data_systems_dpmm", ROOT / "_guides" / "data_systems.py")
ds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ds)
E, wb, SITE = ds.E, ds.wb, ds.SITE
URL = f"{SITE}/learn/data-platform-mind-map/"
OUT = ROOT / "learn" / "data-platform-mind-map" / "index.html"

CSS = """<style>
  .tw { overflow-x:auto; }
  table.map { border-collapse:collapse; width:100%; min-width:1500px; font-size:13px; margin:10px 0 18px; }
  table.map td, table.map th { border:1.5px solid var(--ink); padding:6px 8px; text-align:left; vertical-align:top; }
  table.map th { background:var(--peri-wash); }
  table.map th.xyz { background:var(--rose-wash); }
  table.map th.band { text-align:center; font-family:var(--hand); font-weight:400; font-size:17px; letter-spacing:0; text-transform:none; background:#fff; }
  table.map td.fam { background:var(--butter-wash); font-weight:700; width:104px; }
  table.map td.fam span { display:block; font-weight:400; font-size:11.5px; color:#555; margin-top:3px; }
  table.map td.con { width:128px; font-weight:700; }
  table.map td.con span { display:block; font-weight:400; font-size:11.5px; color:#555; margin-top:2px; }
  table.map td.gcp { background:#fafafa; }
  table.map td.x { background:var(--sky-wash); } table.map td.y { background:var(--butter-wash); } table.map td.z { background:var(--rose-wash); }
  .st { font-size:11.5px; color:#555; display:block; margin-top:2px; }
  .box { background:var(--butter-wash); border:1.5px solid var(--ink); border-radius:var(--wob); padding:14px 20px; margin:16px 0; }
  .steps { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; margin:14px 0; }
  .steps div { border:1.5px solid var(--ink); border-radius:var(--wob); padding:12px 16px; background:var(--peri-wash); }
  .steps b { display:block; font-family:var(--hand); font-weight:400; font-size:23px; }
  .mm { width:100%; height:auto; margin:10px 0 6px; } .mm text { font-family:var(--hand), sans-serif; fill:#1a1a1a; }
</style>"""

# (family, the question it answers, [concerns]); concern = (id, name, one line, azure, databricks, aws, gcp, open, X, Y, Z)
# X = what a platform gives out of the box (the capability, whichever product). Y = the horizontal asset: written once, the
# same on every platform. Z = what each platform still has to implement for the concern to work there.
FAMILIES = [
    ("Run", "Does it run safely, every day?", [
        ("X1", "Metadata and control plane", "Everything declared in one manifest, validated, stored.",
         "Azure Database for PostgreSQL / Azure SQL", "Lakebase (managed Postgres)", "RDS for PostgreSQL", "Cloud SQL for PostgreSQL", "PostgreSQL",
         "A managed database to hold the manifest and the run records.",
         "The manifest format, the validator and loader, and the stored procedures that read and write it.",
         "A connection adapter per database. Azure: Lakebase project found and used (19 Nov). GCP: none. Open: Postgres adapter exists."),
        ("X2", "Orchestration", "What runs when, in what order, with retries.",
         "Data Factory / Fabric pipelines", "Lakeflow Jobs", "MWAA (Airflow) / Step Functions", "Cloud Composer (Airflow)", "Airflow or Dagster",
         "A scheduler that starts tasks, retries them and shows their state.",
         "The day loop, leases and bookmarks that keep order safe; one job entry per hop.",
         "A job or pipeline definition per platform. Azure Databricks: generated bundle, ran 3 days. AWS: a realm with a deployment record exists. GCP: none."),
        ("X15", "Replay, backfill and idempotency", "Re-running never doubles a number.",
         "Delta MERGE; Data Factory re-run", "Delta MERGE; Auto Loader checkpoints; repair run", "Iceberg MERGE; Glue job bookmarks", "BigQuery MERGE", "Delta or Iceberg MERGE; Airflow backfill",
         "A table format that can merge, and a way to re-run a failed task.",
         "Window ledgers, withdraw-and-rebuild, housekeeping, one writer per table.",
         "A table-writer adapter per table format. Delta: done. Iceberg on AWS: not checked here. BigQuery: none."),
        ("X16", "Environments, CI/CD and release", "Dev to test to production, infrastructure as code.",
         "Bicep or Terraform; GitHub Actions or Azure Pipelines", "Declarative Automation Bundles; GitHub Actions", "Terraform or CDK; GitHub Actions + CodeDeploy", "Terraform; GitHub Actions + Cloud Build", "Docker Compose; GitHub Actions",
         "Repositories, build runners and a way to describe infrastructure.",
         "The generated bundle from one engine file; the release gate's logic; naming rules per environment.",
         "One infrastructure module set per cloud. Azure: dev environment applied (45 resources). AWS: a realm exists. GCP: none. Build workflows are not in the public snapshot."),
        ("X17", "Testing", "Unit, contract, data and simulation tests.",
         "Azure Pipelines test tasks", "Databricks Connect + bundles with pytest", "CodeBuild with pytest", "Cloud Build with pytest", "pytest, chispa, dbt tests",
         "A runner that executes tests on every change. No platform tests your data rules for you.",
         "The table-driven tests, the simulated world, the daily end-to-end test (3 days, scale 0.1).",
         "A contract-test run per adapter against the real service. Azure storage: passed on a real account. Others: fakes only or not run."),
        ("X18", "Resilience and recovery", "Retries, retention, time travel.",
         "ADLS soft delete and geo-redundancy; Delta time travel", "Delta time travel and RESTORE; job retries", "S3 versioning; Iceberg snapshots", "Cloud Storage versioning; BigQuery time travel", "MinIO versioning; Delta or Iceberg snapshots",
         "Object versioning, table history and automatic retries.",
         "The source guard, landing retention and the recovery routines.",
         "Turn on and prove versioning and retention per account. Azure: versioning not yet checked. GCP: none."),
        ("X23", "Layout: catalogs and schemas", "From a table's name you know its environment, layer and domain.",
         "Storage account per environment, container per layer", "Unity Catalog: <env>_<layer>.<domain>.<table>", "Glue databases with S3 prefixes", "BigQuery datasets", "Folder paths and Postgres schemas",
         "A namespace for tables: catalog, schema or dataset.",
         "One naming rule (ADR-012) and the checker that tests table names.",
         "Map the rule onto each platform's namespace. Azure: written into Terraform. GCP: none."),
        ("X24", "Streaming", "A second speed on the same line, only where a decision needs it.",
         "Event Hubs / Fabric Eventstream", "Structured Streaming", "Kinesis / Amazon MSK", "Pub/Sub + Dataflow", "Kafka or Redpanda",
         "A durable event log and a stream engine.",
         "Trigger-once stream pipeline, the same checks and ledgers as batch.",
         "A stream adapter per log. AWS: Kinesis exists. Azure: Event Hubs not built (AZ-4). GCP: none. Open: local stream, laptop only."),
    ]),
    ("Trust", "Can I trust the number?", [
        ("X3", "Contracts and schema evolution", "A table says what it promises; a source changing shape is caught.",
         "Delta schema enforcement in Fabric", "Delta schema enforcement and constraints", "Glue Schema Registry; Iceberg schema evolution", "BigQuery schema checks", "dbt model contracts; Iceberg schema evolution",
         "The table format refuses a write with the wrong columns.",
         "The contract check and column rules read from the manifest.",
         "Nothing per cloud beyond the table writer. The registry formats the lander accepts are not all readable (AZ-9)."),
        ("X4", "Data quality", "Rules on rows and tables; bad rows set aside with a reason.",
         "Purview data quality", "Pipeline expectations", "Glue Data Quality", "Dataplex data quality", "Great Expectations or Soda",
         "A rule engine that can pass, warn or fail a table.",
         "The quality stage, the quarantine layer and the rule catalog (DAC) with tests.",
         "A quarantine write per format. The results table is not written in a normal run yet."),
        ("X5", "Profiling", "Knowing what the data looks like, so change is visible.",
         "Purview profiling", "Lakehouse Monitoring", "Glue DataBrew", "Dataplex profiling", "ydata-profiling or Great Expectations",
         "Column statistics on demand.",
         "Profile and drift functions that compare today with history.",
         "None per cloud: the code runs on rows. Wire the platform profile as a second opinion where wanted."),
        ("X6", "Reconciliation", "Counts and sums agree from source to gold.",
         "No native feature", "No native feature", "No native feature", "No native feature", "Soda or datacompy checks",
         "Nothing. Platforms offer SQL, not the idea of a reconciled hop.",
         "The compare function and live-source reconciliation, per dataset per day.",
         "A read adapter for each live source type. Azure: change capture not validated (AZ-6)."),
        ("X9", "Freshness and SLOs", "Is the data as new as promised.",
         "Azure Monitor alerts", "Data quality monitoring and job alerts", "CloudWatch alarms; Glue DQ freshness", "Dataplex freshness rule", "dbt source freshness or Soda",
         "Alerts on time and late jobs.",
         "Freshness checks and the success scorecard (20 rows).",
         "Route the alert to the platform's alert service. Not built on any cloud yet."),
    ]),
    ("See", "Can I see what happened and what it cost?", [
        ("X7", "Lineage", "Where each table came from and what it feeds.",
         "Purview lineage", "Unity Catalog lineage", "Amazon DataZone lineage", "Dataplex lineage", "OpenLineage + Marquez",
         "Automatic lineage inside the platform's own engines.",
         "A reader of the platform's lineage tables, and OpenLineage events built in tests.",
         "A reader per lineage store. Databricks: done. Azure, AWS, GCP: none."),
        ("X8", "Observability", "One run followable end to end.",
         "Azure Monitor + App Insights", "System tables + MLflow tracing", "CloudWatch + X-Ray", "Cloud Logging + Trace", "OpenTelemetry + Grafana",
         "Logs, metrics and traces collected and searchable.",
         "The run recorder, trace helper and operations page, written once.",
         "An OpenTelemetry exporter pointed at each cloud's backend. Exists as an adapter; run on none of the new clouds."),
        ("X10", "Cost and FinOps", "Who spent what, against which budget.",
         "Cost Management", "Billing system tables", "Cost Explorer + CUR", "Billing export to BigQuery", "Query plans and run times",
         "Billing data and budgets with alerts.",
         "Cost tags on every job. A separate tool reads the cost; the platform only tags.",
         "A budget per environment. Azure: $20 a month budget applied. Others: not set. Reading the bill is not built."),
        ("X19", "Performance", "File sizes, layout, compaction, right-sized compute.",
         "Fabric Spark autoscale; Delta OPTIMIZE", "Predictive optimization; liquid clustering", "Iceberg compaction (S3 Tables); Glue autoscaling", "BigQuery partitioning and clustering", "OPTIMIZE jobs; Spark adaptive execution",
         "Autoscaling compute and some automatic file maintenance.",
         "Hop timing, the daily time budget and the table store layout.",
         "A maintenance job per format. Measured on Azure Databricks: 5.7 minutes a day at scale 0.1 (target 6)."),
    ]),
    ("Guard", "Who may see and change what?", [
        ("X11", "Security and access", "Who may read or change each layer, granted on purpose.",
         "Entra ID + RBAC; Purview policies", "Unity Catalog grants, row filters, column masks", "IAM + Lake Formation", "IAM + BigQuery row and column security", "Keycloak + Postgres roles, Ranger or OPA",
         "Identity and permission enforcement on the data.",
         "The access model: who may do what, planned once and rendered into each platform's grants.",
         "A renderer per platform. Databricks: generated and tested locally, not applied. Azure, AWS, GCP: none applied."),
        ("X12", "Privacy and personal data", "Find, mask, keep only as long as allowed.",
         "Purview sensitivity labels", "Unity Catalog tags + column masks", "Macie + Lake Formation tags", "Sensitive Data Protection", "Presidio",
         "A scanner that finds personal data, and masks.",
         "Keyed tokens at landing, a separate store with a one-day purge for personal data, restricted columns declared.",
         "A separate personal-data account and purge rule per cloud. Azure: written and applied. Others: none."),
        ("X13", "Governance, catalog and semantics", "Owners, glossary, metric definitions.",
         "Microsoft Purview; Power BI semantic models", "Unity Catalog; metric views", "Glue Data Catalog; dbt semantic layer", "Dataplex; Looker", "OpenMetadata; Cube Core",
         "A catalog of tables and a place for metric definitions.",
         "Metric definitions as data, rendered into each engine; the question-and-answer checks.",
         "A metric renderer per semantic layer. Databricks: done. Others: not built."),
        ("X14", "Audit and run log", "A record of every run and every change.",
         "Azure Activity log", "System tables (audit)", "CloudTrail", "Cloud Audit Logs", "Postgres run log + OpenTelemetry",
         "Immutable logs of who did what in the cloud.",
         "The run log schema and recorder: what ran, with which config fingerprint.",
         "None beyond the metadata database. Cloud audit logs are read separately."),
    ]),
    ("Self", "Can it help fix itself, safely?", [
        ("X20", "Self-healing", "Detect, fix in development, deploy, verify, roll back.",
         "Retries and alerts only", "Repair run, retries", "Retries and alerts only", "Retries and alerts only", "Retries and alerts only",
         "Retries and notifications. No platform repairs a data fault by itself.",
         "Not built. Only the release gate's logic is written.",
         "Everything. No code exists on any platform."),
        ("X21", "Agent assistance", "Agents draft manifests, rules and docs.",
         "Copilot in Fabric", "Databricks Assistant", "Amazon Q", "Gemini in BigQuery", "Your own agent (see Agent Harness)",
         "A coding assistant inside the vendor's own tools.",
         "Not built. The specs, rules and manifests are written so an agent can read them.",
         "Everything. No agent code exists here."),
        ("X22", "Simulation", "A fake world that breaks the platform on purpose.",
         "None", "dbldatagen", "None", "None", "Faker or SDV",
         "Random-data generators. No platform simulates a company with planted faults.",
         "The world engine: a simulated company, 12 planted faults and the true totals; same on every platform.",
         "A mover per platform to land the world's files. Azure Databricks: ran. AWS: a realm exists. GCP: none."),
    ]),
]
FAM_FILL = ["var(--peri-wash)", "var(--butter-wash)", "var(--rose-wash)", "var(--mint-wash)", "var(--lilac-wash)"]


def table():
    head1 = ('<tr><th colspan="2" class="band">The concern</th><th colspan="5" class="band">Which product fills it, on each platform</th>'
             '<th colspan="3" class="band">The three-way cut</th></tr>')
    cols = ["Concern family", "Concern", "Azure", "Databricks", "AWS", "GCP", "Open stack"]
    head2 = "<tr>" + "".join(f"<th>{E(c)}</th>" for c in cols)
    head2 += ('<th class="xyz">X · What the platform provides</th><th class="xyz">Y · Horizontal asset (written once)</th>'
              '<th class="xyz">Z · What each platform still has to implement</th></tr>')
    out = '<div class="tw"><table class="map">' + head1 + head2
    for fam, question, rows in FAMILIES:
        for i, (cid, name, line, az, db, aw, gc, op, x, y, z) in enumerate(rows):
            out += "<tr>"
            if i == 0:
                out += f'<td class="fam" rowspan="{len(rows)}">{E(fam)}<span>{E(question)}</span></td>'
            out += f'<td class="con">{E(cid)} · {E(name)}<span>{E(line)}</span></td>'
            out += f"<td>{E(az)}</td><td>{E(db)}</td><td>{E(aw)}</td><td class='gcp'>{E(gc)}</td><td>{E(op)}</td>"
            out += f'<td class="x">{E(x)}</td><td class="y">{E(y)}</td><td class="z">{E(z)}</td></tr>'
    return out + "</table></div>"


def mindmap():
    W, H = 1000, 640
    cx, cy = W / 2, H / 2
    pos = [(150, 110), (850, 110), (880, 380), (500, 560), (120, 380)]
    svg = [f'<svg class="mm" viewBox="0 0 {W} {H}" role="img" aria-label="Data platform: five families of concerns">']
    for (x, y) in pos:
        svg.append(f'<line x1="{cx}" y1="{cy}" x2="{x}" y2="{y}" stroke="#1a1a1a" stroke-width="1.5"/>')
    svg.append(f'<ellipse cx="{cx}" cy="{cy}" rx="110" ry="50" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>')
    svg.append(f'<text x="{cx}" y="{cy - 4}" text-anchor="middle" font-size="24">Data platform</text>')
    svg.append(f'<text x="{cx}" y="{cy + 20}" text-anchor="middle" font-size="14">24 concerns, 5 families</text>')
    for k, ((fam, q, rows), (x, y)) in enumerate(zip(FAMILIES, pos)):
        names = [f"{r[0]} {r[1]}" for r in rows]
        h = 52 + 19 * len(names)
        w = 270
        svg.append(f'<rect x="{x - w / 2}" y="{y - h / 2}" width="{w}" height="{h}" rx="14" fill="{FAM_FILL[k]}" stroke="#1a1a1a" stroke-width="1.5"/>')
        svg.append(f'<text x="{x}" y="{y - h / 2 + 23}" text-anchor="middle" font-size="20">{E(fam)}</text>')
        svg.append(f'<text x="{x}" y="{y - h / 2 + 41}" text-anchor="middle" font-size="12.5">{E(q)}</text>')
        for j, n in enumerate(names):
            svg.append(f'<text x="{x}" y="{y - h / 2 + 62 + 19 * j}" text-anchor="middle" font-size="13.5">{E(n)}</text>')
    svg.append("</svg>")
    return "".join(svg)


def page():
    n = sum(len(r) for _, _, r in FAMILIES)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/data-platform-architecture/">Data platform architecture</a> › Mind map</p>
<p class="eyebrow" style="margin-top:22px">Data engineering · Data platform</p>
<h1>Data platform architecture mind map: every concern, on every platform</h1>
<p class="lede">A data platform is the same set of concerns whatever you build it on: it must run, be trusted, be seen, be guarded and, one day, help fix itself. What changes between Azure, Databricks, AWS, Google Cloud and an open-source stack is the product that fills each concern. This page puts all {n} concerns in one table, then cuts each one three ways: what the platform gives you, what we write once for all of them, and what each platform still has to implement.</p>
<p class="note">Written 20 November 2026. The Azure and Databricks entries in column Z come from real builds: a 3-day run passed on Azure Databricks that day. AWS entries come from the repository's files, not from a fresh run. GCP has no binding at all, so everything in its column is a plan. Product names for concerns the rest of this site already maps are taken from there; the others were written from general knowledge and are not checked against each vendor's current documentation.</p>
<h2>The map</h2>
{mindmap()}
<h2>The table</h2>
<div class="steps"><div><b>X · The platform</b>What the cloud or data platform gives out of the box. Different on every stack, and often just a building block.</div>
<div><b>Y · The horizontal asset</b>What we write once and reuse unchanged on every platform: the manifest, the rules, the stages, the checks, the simulated world. It is the same code on Azure as on AWS.</div>
<div><b>Z · Still to implement</b>The thin layer that each platform still needs before the asset can run there: an adapter, a job definition, a renderer. This is the real work of moving platform.</div></div>
{table()}
<div class="box"><b>What this shows.</b> Read down column Y: most of the platform is horizontal, written once. Read column Z: the work per platform is small and concrete (adapters and definitions), not a rewrite. The expensive rows are the ones where X says "nothing": reconciliation (X6), self-healing (X20) and simulation (X22). No cloud sells them, so the horizontal asset is the whole answer, or, for X20 and X21, there is no answer yet.</div>
<h2>What to check before relying on this</h2>
<ul><li><b>GCP.</b> No cloud-layer file exists for it. Treat the whole column as a proposal and confirm each service against Google's current documentation and region availability.</li>
<li><b>Product names.</b> Cells for concerns that the site already maps agree with <a href="/learn/data-platform-architecture/">the architecture page</a>. The rest were written without re-reading each vendor's page, and product names change often.</li>
<li><b>Column Z status words</b> such as "done" or "none" describe our own builds as of 20 November 2026. They are not a statement about the products.</li>
<li><b>Prices and tiers.</b> Not shown on purpose. Get them from each vendor for your volume.</li></ul>
<h2>Where to go next</h2>
<ul><li><a href="/learn/data-systems/platform/#concerns">All 24 concerns, grouped by the question they answer</a>.</li>
<li><a href="/learn/data-platform-architecture/">Data platform architecture</a>, with the diagrams.</li>
<li><a href="/learn/data-platform-suite/">Our platform, picture to code</a>, the same concerns down to the code.</li>
<li><a href="/learn/agent-harness-stack-map/">The same kind of map for the agent harness</a>.</li></ul>"""
    desc = ("One map of a data platform: 24 concerns against Azure, Databricks, AWS, GCP and open source, "
            "cut into what the platform gives, the horizontal asset written once, and what each platform still has to implement.")
    return wb.page("Data platform architecture mind map: every concern, on every platform", desc, URL, body,
                   ds.CSS + CSS + ds.ld("Data platform architecture mind map", desc, URL,
                                        [("Data platform architecture", "/learn/data-platform-architecture/"), ("Mind map", "/learn/data-platform-mind-map/")]))


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page())
    print("mind map ->", OUT)


if __name__ == "__main__":
    main()
