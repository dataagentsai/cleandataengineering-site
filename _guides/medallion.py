"""Medallion architecture: the full guide at /learn/medallion-architecture/.

    python3 _guides/medallion.py

Teach first (plain words and a picture), then the layers, one order's journey with rows,
the rules, mistakes, products per platform and an FAQ. Matches the "medallion, drawn right"
section of ~/clean-data-engineering/PLAN.html.
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "_paths"))
spec = importlib.util.spec_from_file_location("writing_build", ROOT / "_writing" / "build.py")
wb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wb)
from diagrams import DEFS, FILL, arrow, box, svg, text  # noqa: E402

E = wb.E
SITE = wb.SITE
URL = f"{SITE}/learn/medallion-architecture/"

CSS = """<style>
  .crumbs { font-size:13.5px; color:var(--faint); margin:28px 0 0; } .crumbs a { color:var(--muted); }
  .lede { font-size:20px; color:var(--ink-soft); }
  .toc { border:var(--line); border-radius:var(--wob); padding:12px 20px; background:var(--butter-wash); font-size:15px; margin:20px 0; }
  .toc ol { margin:6px 0 0; padding-left:20px; columns:2; column-gap:30px; } .toc li { margin:3px 0; }
  .diagram { margin:18px 0; border:var(--line); border-radius:var(--wob); padding:14px 16px; background:#fff; overflow-x:auto; }
  .diagram svg { width:100%; min-width:640px; height:auto; display:block; } .diagram text { font-family:var(--hand); }
  .diagram figcaption { font-size:13.5px; color:var(--muted); margin-top:6px; }
  .layer { border:var(--line); border-radius:var(--wob); padding:16px 20px; margin:14px 0; background:var(--w, #fff); }
  .layer h3 { font-size:27px; margin:0 0 4px; } .layer .one { font-size:17px; color:var(--ink-soft); margin:0 0 10px; }
  .layer dl { display:grid; grid-template-columns:150px 1fr; gap:4px 14px; margin:0; font-size:15px; }
  .layer dt { color:var(--faint); font-weight:700; font-size:12px; letter-spacing:.06em; text-transform:uppercase; padding-top:3px; }
  .layer dd { margin:0; }
  .tw { overflow-x:auto; } table.t { border-collapse:collapse; width:100%; font-size:14.5px; margin:8px 0 18px; }
  table.t th, table.t td { text-align:left; padding:7px 9px; border-bottom:1.5px dashed var(--rule-firm); vertical-align:top; }
  table.t th { font-size:11.5px; letter-spacing:.08em; text-transform:uppercase; color:var(--faint); }
  table.t code, .layer code, p code, li code { font-family:var(--mono); font-size:.84em; background:var(--surface-2); padding:1px 4px; border-radius:3px; }
  table.rows td { font-family:var(--mono); font-size:12.5px; white-space:nowrap; } table.rows td.bad { background:var(--rose-wash); } table.rows td.new { background:var(--mint-wash); }
  .rule { display:flex; gap:12px; padding:8px 0; border-bottom:1.5px dashed var(--rule); } .rule b.n { font-family:var(--hand); font-size:24px; min-width:34px; }
  .note { font-size:14px; color:var(--faint); }
  .ideas { display:flex; flex-wrap:wrap; gap:8px; margin:6px 0 14px; }
  .ideas a { font-size:14px; border:1.5px solid var(--ink); border-radius:999px; padding:2px 12px; background:#fff; color:var(--ink); text-decoration:none; }
  details.faq { border-bottom:1.5px dashed var(--rule-firm); padding:10px 0; } details.faq summary { cursor:pointer; font-weight:600; }
  details.faq p { margin:8px 0 0; }
  @media (max-width:640px) { .toc ol { columns:1; } .layer dl { grid-template-columns:1fr; } }
</style>"""


def kitchen():
    b = ""
    items = [("Groceries", "as delivered,\nstill in bags", "grey"), ("Store room", "unpacked, labelled,\nnothing thrown away", "bronze"),
             ("Prep counter", "washed, chopped,\nbad bits removed", "silver"), ("The dish", "cooked for\none purpose", "gold"),
             ("The menu", "one name per dish,\none price", "mint")]
    x = 10
    for i, (t, s, f) in enumerate(items):
        b += box(x, 20, 160, 88, t, s, f)
        if i < 4:
            b += arrow(x + 162, 64, x + 194, 64)
        x += 196
    b += text(495, 140, "you never cook straight from the delivery bag, and you can always go back to the store room", 15)
    return svg(990, 155, b, "A kitchen: groceries as delivered, a store room that keeps everything, a prep counter where food is cleaned, a dish cooked for one purpose, and a menu with one name per dish."), \
        "The same idea in a kitchen. Landing is the delivery bag, bronze the store room, silver the prep counter, gold the dish, semantic the menu."


def spine():
    b = f'<rect x="10" y="10" width="1100" height="58" rx="14" fill="{FILL["lilac"]}" stroke="#1F1F1F" stroke-width="1.4" stroke-dasharray="6 5"/>'
    b += text(560, 34, "Control plane: the manifest (YAML) → validator → generator → pipelines · orchestration · catalog · run log", 16, fill="#1F1F1F")
    b += text(560, 56, "Agents may only propose manifest changes by pull request; they never touch production", 13)
    layers = [("Sources", "databases, files,\nAPIs, events", "grey"), ("Landing", "files as received,\nnever changed", "white"),
              ("Bronze", "raw, append-only,\n+ audit columns", "bronze"), ("Silver", "typed, deduped,\none row per thing", "silver"),
              ("Gold", "shaped for a use:\nfacts, dims, marts", "gold"), ("Semantic", "metrics defined\nonce; no tables", "mint"),
              ("Experiences", "dashboards, AI,\nAPIs, ML", "sky")]
    x = 10
    for i, (t, s, f) in enumerate(layers):
        b += box(x, 96, 138, 96, t, s, f)
        if i < len(layers) - 1:
            b += arrow(x + 140, 144, x + 158, 144)
        x += 160
    b += text(560, 216, "data moves one way: each layer is built only from the one before it", 15, fill="#1F1F1F")
    b += f'<rect x="10" y="232" width="1100" height="58" rx="14" fill="{FILL["butter"]}" stroke="#1F1F1F" stroke-width="1.4" stroke-dasharray="6 5"/>'
    b += text(560, 256, "Cross-cutting, on every hop: contracts and quality · reconciliation · lineage · freshness · cost · access and PII · audit", 15, fill="#1F1F1F")
    b += text(560, 278, "declared once in the manifest, switched on by default, never bolted on at the end", 13)
    return svg(1120, 300, b, "The medallion spine: sources, landing, bronze, silver, gold, semantic, experiences, with the control plane above and cross-cutting concerns below."), \
        "The medallion, drawn right: a spine of layers, a control plane above it, and the cross-cutting jobs below it."


LAYERS = [
    ("Landing", "white", "Files exactly as they arrived, so a bad parse can be redone.",
     [("Holds", "Files from the mover: CSV, JSON, Parquet, exports, API pages, untouched."),
      ("Writes", "New files only. Never edited, never deleted by a pipeline."),
      ("Read by", "The bronze loader only."),
      ("Keep for", "Short: days or weeks. Long enough to replay a bad load."),
      ("Skip it when", "Change data capture writes straight into bronze.")]),
    ("Bronze", "bronze", "Raw data in the source's own shape, append-only, with notes on where each row came from.",
     [("Holds", "Every row ever received, in the source's columns and types (often all strings)."),
      ("Adds", "<code>_ingested_at</code>, <code>_source</code>, <code>_batch_id</code>, <code>_file</code>: when, from where, in which batch, from which file."),
      ("Writes", "Append only. Loading the same batch again is detected by <code>_batch_id</code> and skipped."),
      ("Read by", "Silver jobs only. No dashboard, no analyst, no model reads bronze."),
      ("Promise", "You can always rebuild silver from bronze.")]),
    ("Silver", "silver", "The first layer with an opinion: one clean row per real thing.",
     [("Holds", "One row per business entity (an order, a customer), typed, de-duplicated, with conformed keys."),
      ("Does", "Cast types, trim, standardise codes, fix time zones, handle nulls, keep the latest row per key, keep history (SCD Type 1 or 2)."),
      ("Enforces", "The data contract. A row that fails goes to quarantine with its reason; it is never silently dropped."),
      ("Writes", "MERGE on the business key, so re-running changes nothing."),
      ("Read by", "Gold jobs, data scientists, feature pipelines.")]),
    ("Gold", "gold", "Tables shaped for a use: a sales mart, a star schema, a feature table, a data product.",
     [("Holds", "Facts and dimensions, aggregates, marts, published data products."),
      ("Built from", "Silver only, never bronze."),
      ("Checked by", "Reconciliation: counts and sums agree with silver and with the source, within a tolerance."),
      ("Read by", "The semantic layer, dashboards, sharing, ML.")]),
    ("Semantic", "mint", "Definitions, not tables: each metric means one thing.",
     [("Holds", "Metric definitions (net revenue = gross minus refunds, excluding test orders), entities, joins, governed names."),
      ("Read by", "Dashboards and conversation UIs alike, so both give the same answer. The model never writes raw SQL."),
      ("Why", "It ends the 'why do two dashboards show two revenues' meeting.")]),
    ("Experiences", "sky", "Where people and programs use the data.",
     [("Includes", "Dashboards, conversation UIs, APIs, data sharing, ML features, documents for AI (RAG)."),
      ("Reads", "Only from semantic or gold.")]),
]

JOURNEY = """
<h3>1 · Landing: the file as it arrived</h3>
<pre style="font-size:13px;background:var(--surface-2);padding:12px;border-radius:8px;overflow-x:auto">orders_2026-10-27_0900.json
{"order_id":"1001","customer":"C-77","amount":"1,250.00","currency":"inr","placed":"27/10/2026 08:58","status":"PAID "}
{"order_id":"1002","customer":null,"amount":"-40","currency":"INR","placed":"27/10/2026 08:59","status":"paid"}
{"order_id":"1001","customer":"C-77","amount":"1,250.00","currency":"inr","placed":"27/10/2026 08:58","status":"PAID "}</pre>
<p>Order 1001 was sent twice. Order 1002 has no customer and a negative amount. Landing keeps all of it, untouched.</p>

<h3>2 · Bronze: the same rows, plus where they came from</h3>
<div class="tw"><table class="t rows"><tr><th>order_id</th><th>customer</th><th>amount</th><th>currency</th><th>placed</th><th>status</th><th>_ingested_at</th><th>_source</th><th>_batch_id</th><th>_file</th></tr>
<tr><td>1001</td><td>C-77</td><td>1,250.00</td><td>inr</td><td>27/10/2026 08:58</td><td>"PAID "</td><td class="new">2026-10-27T03:31:02Z</td><td class="new">shop_db</td><td class="new">b-0912</td><td class="new">orders_…0900.json</td></tr>
<tr><td>1002</td><td class="bad">null</td><td class="bad">-40</td><td>INR</td><td>27/10/2026 08:59</td><td>paid</td><td class="new">2026-10-27T03:31:02Z</td><td class="new">shop_db</td><td class="new">b-0912</td><td class="new">orders_…0900.json</td></tr>
<tr><td class="bad">1001</td><td>C-77</td><td>1,250.00</td><td>inr</td><td>27/10/2026 08:58</td><td>"PAID "</td><td class="new">2026-10-27T03:31:02Z</td><td class="new">shop_db</td><td class="new">b-0912</td><td class="new">orders_…0900.json</td></tr></table></div>
<p>Still strings (note the stray space after "PAID"), still the duplicate, still the bad row. Bronze is a faithful record, not a clean one. The green columns are the audit columns the loader adds.</p>

<h3>3 · Silver: one clean, typed row per order</h3>
<div class="tw"><table class="t rows"><tr><th>order_id</th><th>customer_key</th><th>amount_inr</th><th>placed_at_utc</th><th>status</th><th>_batch_id</th></tr>
<tr><td>1001</td><td>C-77</td><td>1250.00</td><td>2026-10-27 03:28:00</td><td>paid</td><td>b-0912</td></tr></table></div>
<div class="tw"><table class="t rows"><tr><th>quarantine: order_id</th><th>rule failed</th><th>_batch_id</th></tr>
<tr><td class="bad">1002</td><td class="bad">customer_key is required; amount must be ≥ 0</td><td>b-0912</td></tr></table></div>
<p>The duplicate collapsed to one row (latest per key). Text became numbers and timestamps, India time became UTC, codes were standardised. Order 1002 failed the contract and went to quarantine with its reason, where the owner can see it.</p>

<h3>4 · Gold: shaped for the question "how much did we sell?"</h3>
<div class="tw"><table class="t rows"><tr><th>fact_sales: date_key</th><th>store_key</th><th>customer_key</th><th>order_id</th><th>amount_inr</th></tr>
<tr><td>20261027</td><td>S-04</td><td>C-77</td><td>1001</td><td>1250.00</td></tr></table></div>
<div class="tw"><table class="t rows"><tr><th>daily_sales: date</th><th>orders</th><th>revenue_inr</th><th>reconciled</th></tr>
<tr><td>2026-10-27</td><td>1</td><td>1250.00</td><td class="new">✓ 2 distinct orders in the source = 1 in silver + 1 in quarantine</td></tr></table></div>

<h3>5 · Semantic: one meaning for "revenue"</h3>
<pre style="font-size:13px;background:var(--surface-2);padding:12px;border-radius:8px;overflow-x:auto">metric: net_revenue
  meaning: paid order amounts minus refunds, excluding test orders
  from: gold.fact_sales
  owner: finance</pre>
<p>The dashboard and the conversation UI both ask for <code>net_revenue</code>, so both say ₹1,250 for 27 October, and both can say why order 1002 is missing.</p>
"""

RULES = [
    ("Data moves one way.", "Each layer is built only from the one before it. Gold never reads bronze; a dashboard never reads silver directly."),
    ("Bronze is append-only and replayable.", "Nothing in bronze is edited. If silver is wrong, fix the job and rebuild silver from bronze."),
    ("Every row says where it came from.", "Audit columns in bronze, lineage on every hop, the batch id carried into silver."),
    ("Silver is one row per real thing.", "De-duplicated on the business key, typed, with history kept as decided (SCD Type 1 or 2)."),
    ("Bad rows are quarantined, never dropped.", "Each with the rule it failed, visible to its owner. A rule is never loosened just to make a job pass."),
    ("Every load can run twice.", "Bronze skips a batch it has seen; silver and gold use MERGE or partition overwrite. Run twice = run once."),
    ("Numbers reconcile across hops.", "Counts and sums agree from source to gold within a tolerance, every run."),
    ("Metrics are defined once.", "In the semantic layer, not in each dashboard."),
    ("Cross-cutting jobs are on by default.", "Quality, lineage, freshness, cost, access and PII are declared per table; turning one off needs a written waiver."),
]

MISTAKES = [
    ("Dashboards reading bronze", "Every report cleans the data its own way, so numbers disagree", "Point reports at gold or semantic; block bronze access for analysts"),
    ("Cleaning before landing a raw copy", "A bug in the cleaning has nothing to re-run from", "Land and keep the raw copy first (ELT)"),
    ("Dropping bad rows silently", "Totals are quietly wrong and nobody knows why", "Quarantine with a reason and alert the owner"),
    ("INSERT instead of MERGE in silver", "Every retry adds duplicates", "MERGE on the business key; skip seen batches in bronze"),
    ("One giant flat table per report in gold", "The same product is spelled three ways", "Facts and conformed dimensions; marts built from them"),
    ("Too many layers ('platinum', 'diamond', 'staging2')", "Nobody knows which one to read", "Keep the meaning of each layer; add tables, not layers"),
    ("Medallion per team, each with its own rules", "The same customer cleaned five ways", "One silver per business entity, owned and shared"),
    ("Metric logic in dashboards", "Two revenues in one meeting", "Define the metric once in the semantic layer"),
]

PRODUCTS = [
    ("Storage", "Amazon S3", "OneLake / ADLS Gen2", "Cloud Storage", "Unity Catalog volumes on cloud storage", "MinIO or local disk"),
    ("Table format", "Apache Iceberg (S3 Tables)", "Delta Lake", "Iceberg on BigLake", "Delta Lake", "Delta Lake or Iceberg"),
    ("Into landing", "AWS DMS, AppFlow", "Data Factory copy, mirroring", "Datastream", "Lakeflow Connect", "dlt or Airbyte"),
    ("Landing → bronze", "Glue (Spark) or EMR", "Fabric Spark / notebooks", "Dataproc (Spark)", "Auto Loader / Lakeflow pipelines", "PySpark"),
    ("Bronze → silver → gold", "Glue, EMR, or dbt on Athena/Redshift", "Fabric Spark or dbt on Fabric", "Dataform or dbt on BigQuery", "Lakeflow Declarative Pipelines or dbt", "PySpark or dbt + DuckDB"),
    ("Quality checks", "Glue Data Quality", "Purview data quality", "Dataplex data quality", "Pipeline expectations", "Great Expectations or Soda"),
    ("Catalog, access, lineage", "Glue Data Catalog + Lake Formation", "Microsoft Purview", "Dataplex", "Unity Catalog", "OpenMetadata + OpenLineage"),
    ("Semantic layer", "dbt semantic layer", "Power BI semantic models", "Looker (LookML)", "Metric views", "Cube Core"),
    ("Orchestration", "MWAA (Airflow), Step Functions", "Data Factory / Fabric pipelines", "Cloud Composer", "Lakeflow Jobs", "Airflow or Dagster"),
]

FAQ = [
    ("What is medallion architecture?", "A way to organise a data platform into layers of increasing quality: bronze keeps raw data as it arrived, silver holds clean, typed, de-duplicated data with one row per real thing, and gold holds tables shaped for a business use. Each layer is built only from the one before it."),
    ("Is medallion architecture only for Databricks?", "No. The name was popularised by Databricks, and Microsoft Fabric uses it too, but the idea (raw, then cleaned, then modelled) is much older and works on AWS, Google Cloud, Snowflake or open source. Only the product names change."),
    ("Is medallion a data model?", "No. It says how data moves and what each layer promises. You still choose a data model inside the layers: for example dimensional (star schema) in gold, or data vault in silver."),
    ("How many layers should there be?", "Three named layers (bronze, silver, gold), often with a landing area before bronze and a semantic layer after gold. If you feel you need a fourth medallion, you usually need more tables, not another layer."),
    ("Where should data quality checks go?", "Everywhere, but the contract is enforced at the bronze-to-silver hop: rows that break it go to quarantine with a reason. Gold adds reconciliation (counts and sums agree with silver and the source)."),
    ("Where does SCD Type 2 history live?", "In silver, for entities whose history matters (a customer's city, a product's price). Gold dimensions read that history."),
    ("Does streaming need a different architecture?", "Usually not: one medallion, two speeds. Hot tables flow through the same layers continuously; the rules (one-way flow, contracts, MERGE) stay the same."),
    ("Medallion vs Kimball vs data vault?", "They answer different questions. Medallion is the flow and the promise of each layer. Kimball (star schemas) is how to shape gold for analysis. Data vault is one way to model an integrated, historised silver. Many platforms use medallion with Kimball in gold."),
]


def page():
    k_svg, k_cap = kitchen()
    s_svg, s_cap = spine()
    layers = "".join(
        f'<div class="layer" style="--w:{FILL[f]}"><h3>{n}</h3><p class="one">{one}</p><dl>'
        + "".join(f"<dt>{dt}</dt><dd>{dd}</dd>" for dt, dd in rows) + "</dl></div>" for n, f, one, rows in LAYERS)
    rules = "".join(f'<div class="rule"><b class="n">{i + 1}</b><div><b>{E(t)}</b> {E(d)}</div></div>' for i, (t, d) in enumerate(RULES))
    mistakes = "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td>{E(c)}</td></tr>" for a, b, c in MISTAKES)
    prods = "".join("<tr>" + "".join(f"<td>{'<b>' + E(c) + '</b>' if i == 0 else E(c)}</td>" for i, c in enumerate(r)) + "</tr>" for r in PRODUCTS)
    faq = "".join(f'<details class="faq"><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in FAQ)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › Medallion architecture</p>
<p class="eyebrow" style="margin-top:22px">Data engineering · free guide · the same on every platform</p>
<h1>Medallion architecture, drawn right</h1>
<p class="note" style="margin:0 0 6px">Part of <a href="/learn/data-platform-architecture/">Data platform architecture, drawn right</a>: this page zooms into its middle row.</p>
<p class="lede">The most common way to organise a data platform: raw data in, clean data in the middle, business-ready data out, and each step simple enough to check and redo. This guide shows each layer, follows one order through all of them with real rows, and lists the rules, the mistakes and the products on each platform.</p>
<nav class="toc"><b>On this page</b><ol>
<li><a href="#plain">In plain words</a></li><li><a href="#spine">The whole picture</a></li><li><a href="#layers">Each layer, its job and its promise</a></li>
<li><a href="#journey">One order, through every layer</a></li><li><a href="#rules">Nine rules that keep it honest</a></li><li><a href="#mistakes">Common mistakes</a></li>
<li><a href="#platforms">On each platform</a></li><li><a href="#faq">Questions people ask</a></li><li><a href="#next">Where to go next</a></li></ol></nav>

<section id="plain"><p class="eyebrow">In plain words</p><h2>Think of a kitchen</h2>
<p>A restaurant never cooks straight from the delivery bag. Groceries go into a store room as they arrived, labelled with when they came. On the prep counter they are washed, chopped and the bad bits thrown out. Then they are cooked into a dish for one purpose, and the menu gives each dish one name and one price. If a dish goes wrong, the cook goes back to the store room, not to the supplier.</p>
<figure class="diagram">{k_svg}<figcaption>{E(k_cap)}</figcaption></figure>
<p>A data platform works the same way. <b>Bronze</b> is the store room: everything as it arrived. <b>Silver</b> is the prep counter: cleaned, one of each thing. <b>Gold</b> is the dish: shaped for a use. The <b>semantic layer</b> is the menu: one meaning per number. The name "medallion" just means bronze, silver and gold, in order of polish.</p></section>

<section id="spine"><p class="eyebrow">The whole picture</p><h2>The spine, with what sits above and below it</h2>
<p>Read it left to right. Data moves one way. Above the layers sits the <b>control plane</b>, which turns a written description of each table (the manifest) into pipelines. Below them sit the <b>cross-cutting jobs</b> such as quality, lineage and cost, which run on every hop, not as a box at the end.</p>
<figure class="diagram">{s_svg}<figcaption>{E(s_cap)}</figcaption></figure></section>

<section id="layers"><p class="eyebrow">Each layer</p><h2>Its job and its promise</h2>{layers}</section>

<section id="journey"><p class="eyebrow">Worked example</p><h2>One order, through every layer</h2>
<p>A clothing shop sends a small file at 9 a.m. It has three rows, and two problems in it. Watch what each layer does with them.</p>{JOURNEY}</section>

<section id="rules"><p class="eyebrow">Rules</p><h2>Nine rules that keep it honest</h2>
<p>Each rule can be checked by a machine, which is what keeps a medallion from slowly turning back into a swamp.</p>{rules}</section>

<section id="mistakes"><p class="eyebrow">Mistakes</p><h2>Common mistakes, and the fix</h2>
<div class="tw"><table class="t"><tr><th>Mistake</th><th>Why it hurts</th><th>Fix</th></tr>{mistakes}</table></div></section>

<section id="platforms"><p class="eyebrow">Concept vs product</p><h2>The same layers on each platform</h2>
<p>The layers and rules never change. Only the products that do each job change. Learn the job once; the product is a binding.</p>
<div class="tw"><table class="t"><tr><th>Job</th><th>AWS</th><th>Azure / Fabric</th><th>Google Cloud</th><th>Databricks</th><th>Open source</th></tr>{prods}</table></div>
<p class="note">Product names change often; check the current docs before you build.</p></section>

<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{faq}</section>

<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2>
<p><b>Zoom out:</b> <a href="/learn/data-platform-architecture/">Data platform architecture, drawn right</a>: the control plane, the three services, streaming, 22 cross-cutting concerns and the agents around the medallion.</p>
<p><b>The ideas behind each layer</b>, one short page each:</p>
<div class="ideas"><a href="/concepts/etl-elt/">ETL vs ELT</a><a href="/concepts/lakehouse/">Warehouse, lake and lakehouse</a><a href="/concepts/file-formats/">File formats</a><a href="/concepts/table-formats/">Open table formats</a><a href="/concepts/idempotency/">Idempotency</a><a href="/concepts/data-quality/">Data quality</a><a href="/concepts/data-contracts/">Data contracts</a><a href="/concepts/scd/">Slowly changing dimensions</a><a href="/concepts/dimensional/">Star schema</a><a href="/concepts/semantic-layer/">Semantic layer</a><a href="/concepts/lineage/">Lineage</a></div>
<p><b>Learn it step by step:</b> <a href="/paths/data-engineering/">the Data Engineering path</a> (Crawl, Walk, Run on AWS, Azure, Google Cloud, Databricks or open source).</p>
<p><b>Build one:</b> the <a href="/projects/dataeng-training/">Ecom simple data platform</a> project lands a shop's data through bronze, silver and gold. Join it, free.</p>
<p><b>Run it:</b> <a href="/learn/data-platform-sim/">DataTwin Studio</a> follows the same three orders through every layer, recorded from a real Spark and Delta Lake run. Then send the same file again and watch a naive pipeline double the revenue.</p></section>"""
    ld = [
        {"@context": "https://schema.org", "@type": "TechArticle", "headline": "Medallion architecture, drawn right",
         "description": "A free guide to medallion architecture: bronze, silver and gold layers, one order through every layer, nine rules, common mistakes and the products on each platform.",
         "url": URL, "inLanguage": "en", "isAccessibleForFree": True, "dateModified": "2026-10-27",
         "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
         "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE},
         "about": [{"@type": "Thing", "name": "Medallion architecture"}, {"@type": "Thing", "name": "Data engineering"}]},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Learn", "item": f"{SITE}/learn/"},
            {"@type": "ListItem", "position": 2, "name": "Medallion architecture", "item": URL}]},
    ]
    head = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    desc = "Medallion architecture explained: bronze, silver and gold layers, one order through every layer with real rows, nine rules, common mistakes and products per platform."
    return wb.page("Medallion architecture, drawn right", desc, URL, body, head)


def main():
    out = ROOT / "learn" / "medallion-architecture"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("medallion guide ->", out)


if __name__ == "__main__":
    main()
