"""Data platform architecture: the whole picture at /learn/data-platform-architecture/.

    python3 _guides/architecture.py

The parent of the medallion guide. The drawing is the one in ~/clean-data-engineering/PLAN.html
("The medallion, drawn right"), with plain names instead of spec acronyms (DPM, DBS) until
decision D1 locks them, the 22 concern chips drawn in, and every box linked one level down.
"""
import json
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
import medallion as M  # noqa: E402  (shares the page shell and CSS)

wb = M.wb
SITE = wb.SITE
URL = f"{SITE}/learn/data-platform-architecture/"
MED = "/learn/medallion-architecture/"

# id, name, one line, group, link (concept page or guide anchor)
CONCERNS = [
    ("X1", "Metadata & control", "Everything is declared in one manifest and validated", "Run", "/learn/data-platform-architecture/metadata-store/"),
    ("X2", "Orchestration", "What runs when, and in what order", "Run", "/concepts/orchestration/"),
    ("X3", "Contracts & schema", "What a table promises, and what happens when a source changes shape", "Trust", "/concepts/data-contracts/"),
    ("X4", "Data quality", "Rules on rows and tables; bad rows quarantined", "Trust", "/concepts/data-quality/"),
    ("X5", "Profiling", "Knowing what the data looks like, so change is visible", "Trust", None),
    ("X6", "Reconciliation", "Counts and sums agree from source to gold", "Trust", MED + "#rules"),
    ("X7", "Lineage", "Where each table came from and what it feeds", "See", "/concepts/lineage/"),
    ("X8", "Logs, metrics, traces", "One run is followable end to end", "See", "/concepts/observability/"),
    ("X9", "Freshness & SLOs", "Is the data as new as promised?", "See", "/concepts/freshness/"),
    ("X10", "Cost & FinOps", "Who spent what, against which budget", "See", "/concepts/cost-drivers/"),
    ("X11", "Security & access", "Who may read or change what", "Guard", "/concepts/least-privilege/"),
    ("X12", "Privacy & PII", "Find, mask, keep only as long as allowed, erase on request", "Guard", "/concepts/governance/"),
    ("X13", "Governance & semantics", "Owners, glossary, metric definitions", "Guard", "/concepts/semantic-layer/"),
    ("X14", "Audit & run log", "A record of every run and every change", "Guard", "#control"),
    ("X15", "Replay & backfill", "Re-running never doubles a number", "Run", "/concepts/backfill/"),
    ("X16", "Environments & CI/CD", "Dev → test → prod, infrastructure as code", "Run", "/concepts/ci-cd/"),
    ("X17", "Testing", "Unit, contract, data and simulation tests", "Run", "/concepts/testing/"),
    ("X18", "Resilience & DR", "Retries, retention, time travel, recovery", "Run", "/concepts/retries/"),
    ("X19", "Performance", "File sizes, layout, compaction, right-sized compute", "See", "/concepts/small-files/"),
    ("X20", "Self-healing", "Detect, fix in dev, deploy, verify, roll back", "Self", "#agents"),
    ("X21", "Agent assistance", "Agents draft manifests, rules and docs", "Self", "#agents"),
    ("X22", "Simulation", "A fake world that breaks the platform on purpose", "Self", "#simulation"),
]
GROUP = {"Trust": ("#FFF1D6", "Can I trust the number?"), "See": ("#E6F4EC", "Can I see what happened and what it cost?"),
         "Guard": ("#F8E6EF", "Who may see and change what?"), "Run": ("#F1F1EF", "Does it run safely, every day?"),
         "Self": ("#E6EAF7", "Can it help fix itself, safely?")}

STAGES = [  # x, name, lines, fill, link
    (30, "Sources", ["databases · CDC", "files · APIs", "event streams", "SaaS apps"], "#F4F4F2", "/concepts/cdc/"),
    (182, "Landing", ["files as received", "never changed", "short retention", "optional for CDC"], "#FFFFFF", "/learn/data-platform-architecture/ingestion/"),
    (334, "Bronze", ["raw, append-only", "+ ingest metadata", "source schema", "replayable"], "#F3E3D3", "/learn/data-platform-architecture/ingestion/"),
    (486, "Silver", ["typed, deduped", "conformed keys, SCD", "contract enforced", "bad rows quarantined"], "#ECEDEF", "/learn/data-platform-architecture/bronze-to-silver/"),
    (638, "Gold", ["business shape", "star schema, marts", "data products", "reads only silver"], "#FFF4D9", "/learn/data-platform-architecture/gold/"),
    (790, "Semantic", ["metrics defined once", "entities, joins", "governed names", "no tables of its own"], "#F8EBF1", "/concepts/semantic-layer/"),
    (942, "Experiences", ["dashboards", "conversation UI", "APIs, sharing", "ML features, RAG"], "#E9EDF8", "#serve"),
]


def drawing():
    t = []
    a = t.append
    a('<svg viewBox="0 0 1100 640" role="img" aria-label="Data platform architecture: an agent plane and a control plane above a spine of layers from sources to experiences, grouped into three services, a streaming lane, and 22 cross-cutting concerns below." font-family="DM Sans, sans-serif">')
    a('<defs><marker id="ah2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#2b2b2b"/></marker></defs>')
    a('<a href="#agents"><rect x="20" y="16" width="1060" height="52" rx="16" fill="#E9EDF8" stroke="#2b2b2b" stroke-width="1.5"/>'
      '<text x="40" y="38" font-family="Patrick Hand" font-size="20">Agent plane</text>'
      '<text x="40" y="58" font-size="12.5">onboarding · rule suggester · triage &amp; self-heal · cost advisor · docs · conversation UI. Agents open pull requests against the manifest; they never touch production.</text></a>')
    a('<a href="/learn/data-platform-architecture/metadata-store/"><rect x="20" y="82" width="1060" height="58" rx="16" fill="#EAF6EF" stroke="#2b2b2b" stroke-width="1.5"/>'
      '<text x="40" y="105" font-family="Patrick Hand" font-size="20">Control plane</text>'
      '<text x="40" y="126" font-size="12.5">Platform manifest (YAML) → validator → metadata DB → generators → pipelines for your platform\'s binding · orchestration · catalog · run log</text></a>')
    a('<line x1="550" y1="68" x2="550" y2="82" stroke="#2b2b2b" stroke-width="1.5" marker-end="url(#ah2)"/>')
    a('<line x1="550" y1="140" x2="550" y2="166" stroke="#2b2b2b" stroke-width="1.5" stroke-dasharray="4 3" marker-end="url(#ah2)"/>')
    for x1, w, cx, label in [(30, 586, 323, "Service A · Acquire (ingest → silver)"), (638, 282, 779, "Service B · Model (gold → semantic)"), (942, 130, 1007, "Service C · Serve")]:
        a(f'<a href="#services"><path d="M{x1},182 v-8 h{w} v8" fill="none" stroke="#2b2b2b" stroke-width="1.5"/>'
          f'<text x="{cx}" y="168" text-anchor="middle" font-family="Patrick Hand" font-size="18">{E(label)}</text></a>')
    for x, name, lines, fill, link in STAGES:
        body = (f'<rect x="{x}" y="196" width="130" height="150" rx="14" fill="{fill}" stroke="#2b2b2b" stroke-width="1.5"/>'
                f'<text x="{x + 65}" y="220" text-anchor="middle" font-family="Patrick Hand" font-size="19">{name}</text>'
                + "".join(f'<text x="{x + 12}" y="{246 + i * 18}" font-size="11.5">{E(l)}</text>' for i, l in enumerate(lines))
                + f'<circle cx="{x + 118}" cy="208" r="5" fill="#fff" stroke="#2b2b2b" stroke-width="1.2"/>')
        a(f'<a href="{link}"><title>Open: {name}</title>{body}</a>')
    a('<g stroke="#2b2b2b" stroke-width="1.5" marker-end="url(#ah2)">' + "".join(
        f'<line x1="{x + 130}" y1="271" x2="{x + 150}" y2="271"/>' for x, *_ in STAGES[:-1]) + "</g>")
    a('<a href="#streaming"><rect x="30" y="362" width="1042" height="42" rx="14" fill="#fff" stroke="#2b2b2b" stroke-width="1.5" stroke-dasharray="7 5"/>'
      '<text x="46" y="388" font-size="12.5"><tspan font-family="Patrick Hand" font-size="17">Streaming lane:</tspan> the same layers, run continuously. Event stream → bronze stream → silver streaming tables → gold incremental views. Same contracts, same checks.</text></a>')
    a('<rect x="20" y="420" width="1060" height="210" rx="16" fill="#FFF9EA" stroke="#2b2b2b" stroke-width="1.5"/>')
    a('<a href="#concerns"><text x="40" y="446" font-family="Patrick Hand" font-size="20">Cross-cutting: built in, declared in the manifest, never bolted on</text></a>')
    for i, (cid, name, _, grp, link) in enumerate(CONCERNS):
        col, row = i % 6, i // 6
        x, y = 34 + col * 174, 460 + row * 40
        chip = (f'<rect x="{x}" y="{y}" width="164" height="30" rx="12" fill="{GROUP[grp][0]}" stroke="#2b2b2b" stroke-width="1.2"/>'
                f'<text x="{x + 10}" y="{y + 20}" font-size="12">{cid} {E(name)}</text>')
        a(f'<a href="{link}"><title>{cid} {E(name)}</title>{chip}</a>' if link else chip)
    a("</svg>")
    return "".join(t)


AGENTS = [
    ("Onboarding", "source catalog, sample rows", "a draft manifest entry and a draft contract", "always, before merge"),
    ("Rule suggester", "profiles, history", "proposed quality rules", "a rule would tighten a contract"),
    ("Triage and self-heal", "incidents, lineage, run logs", "a fix as a pull request, tested in dev", "the fix touches a contract or a metric definition"),
    ("Cost advisor", "billing and query history", "findings and a fix pull request (file sizes, partitions, clusters)", "the change affects a service level"),
    ("Docs", "manifest, lineage", "table and metric documentation", "never (docs are easy to undo)"),
    ("Conversation UI", "the semantic layer only", "answers that cite a metric", "never; it never writes SQL"),
]

RULES = [
    ("The design names no product and no business.", "A bank and a clothing shop read the same architecture. Product names live only in the binding file for each platform."),
    ("Everything is declared in the manifest.", "No pipeline, table or check exists that the manifest didn't ask for. What runs is compared with what is declared."),
    ("Generators write pipelines; people and agents write the manifest.", "Generated code is never edited by hand; CI regenerates it and fails on a difference."),
    ("Every vendor sits behind a port.", "No 'if cloud == …' branches. Changing platform means a new adapter and a new binding file, never a redesign."),
    ("Cross-cutting jobs are on by default.", "Turning one off for a table needs a written waiver with a reason, an approver and an expiry date."),
    ("Agents propose, gates decide.", "Agents can only open pull requests against the manifest. Contracts and metric definitions are protected files."),
    ("Nothing passes by absence.", "A check that looked at 0 rows is an error, never a pass."),
    ("Data flows one way.", "Gold never reads bronze; a dashboard never reads silver. Lineage is checked against the allowed paths."),
    ("Every kind of incident has a planted test.", "If the simulated world can produce it, a detector must have been seen to catch it."),
]

BINDING = [
    ("Manifest → pipelines", "CDK or Terraform + Glue/Step Functions definitions", "Bicep or Terraform + Fabric/Data Factory items", "Terraform + Composer DAGs, Dataform", "Asset Bundles (bundles) + Lakeflow", "Python generator + Airflow/Dagster"),
    ("Orchestration", "MWAA (Airflow), Step Functions", "Data Factory / Fabric pipelines", "Cloud Composer", "Lakeflow Jobs", "Airflow or Dagster"),
    ("Compute", "Glue, EMR, Athena", "Fabric Spark, SQL", "Dataproc, BigQuery", "Databricks serverless and clusters", "Spark, DuckDB"),
    ("Tables", "Iceberg on S3", "Delta in OneLake", "BigQuery, Iceberg on BigLake", "Delta in Unity Catalog", "Delta or Iceberg"),
    ("Catalog, access, lineage", "Glue Catalog, Lake Formation, DataZone", "Microsoft Purview", "Dataplex", "Unity Catalog", "OpenMetadata, OpenLineage"),
    ("Streaming", "Kinesis, MSK", "Event Hubs, Eventstream", "Pub/Sub, Dataflow", "Structured Streaming", "Kafka + Spark"),
    ("Semantic layer", "dbt semantic layer", "Power BI semantic models", "Looker", "Metric views", "Cube Core"),
    ("Cost", "Cost Explorer, CUR", "Cost Management", "Billing export", "Billing system tables", "query plans and run times"),
]

FAQ = [
    ("What is a data platform architecture?", "The overall design of how data gets from the systems that create it to the people, dashboards and AI that use it: the layers it passes through, the services that move it, the control plane that configures it, and the jobs such as quality, lineage, security and cost that apply everywhere."),
    ("What is the difference between the control plane and the data plane?", "The data plane is where data actually moves: the layers from sources to experiences. The control plane decides what should move and how: it reads the manifest and metadata, generates the pipelines, schedules them and records every run."),
    ("Is medallion architecture the same as a data platform architecture?", "No. The medallion (bronze, silver, gold) is the middle row: the layers data moves through. A full platform architecture also has the control plane above, the cross-cutting jobs below, the services that own each part, and a plan for streaming."),
    ("Why a metadata-driven platform?", "Because then a new source is a few lines of YAML, not a new notebook. The manifest switches on quality, lineage, cost and access for each table, so nothing is forgotten, and every platform is built the same way."),
    ("Should AI agents be allowed to change pipelines?", "Not directly. Here agents can only propose changes as pull requests against the manifest; tests and people decide. Contracts and metric definitions are protected, so an agent can never loosen a rule to make a problem disappear."),
    ("Lambda, Kappa or one medallion for streaming?", "Most platforms do well with one medallion run at two speeds: the same layers and the same contracts, with hot tables flowing continuously. Kappa (everything as a stream) fits when the sources are streams to begin with."),
]


def page():
    groups = {}
    for cid, name, one, grp, link in CONCERNS:
        groups.setdefault(grp, []).append((cid, name, one, link))
    concern_html = ""
    for grp in ("Trust", "See", "Guard", "Run", "Self"):
        rows = "".join(f'<tr><td>{cid}</td><td><b>{f"<a href={chr(34)}{link}{chr(34)}>{E(n)}</a>" if link and link.startswith("/") else E(n)}</b></td><td>{E(o)}</td></tr>'
                       for cid, n, o, link in groups[grp])
        concern_html += f'<h3 style="margin-top:18px">{grp}: {E(GROUP[grp][1])}</h3><div class="tw"><table class="t">{rows}</table></div>'
    agents = "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td>{E(c)}</td><td>{E(d)}</td></tr>" for a, b, c, d in AGENTS)
    rules = "".join(f'<div class="rule"><b class="n">{i + 1}</b><div><b>{E(t)}</b> {E(d)}</div></div>' for i, (t, d) in enumerate(RULES))
    binding = "".join("<tr>" + "".join(f"<td>{'<b>' + E(c) + '</b>' if i == 0 else E(c)}</td>" for i, c in enumerate(r)) + "</tr>" for r in BINDING)
    faq = "".join(f'<details class="faq"><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in FAQ)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › Data platform architecture</p>
<p class="eyebrow" style="margin-top:22px">Data engineering · free guide · the whole picture</p>
<h1>Data platform architecture, drawn right</h1>
<p class="lede">One picture of a whole data platform, from the systems that make data to the dashboards and AI that use it: the layers in the middle, the control plane that runs them, the agents that may only suggest, and the jobs that keep every number honest. Click any box to go one level down, or <a href="/learn/data-platform-sim/">run it in DataTwin Studio</a>.</p>
<div class="sib" style="display:flex;flex-wrap:wrap;gap:8px;font-size:14px;margin:6px 0 0"><b style="padding:2px 0">Components:</b> <a href="/learn/data-platform-architecture/metadata-store/">Metadata store</a> · <a href="/learn/data-platform-architecture/ingestion/">Ingestion</a> · <a href="/learn/data-platform-architecture/bronze-to-silver/">Bronze to silver</a> · <a href="/learn/data-platform-architecture/gold/">Gold</a></div>
<nav class="toc"><b>On this page</b><ol>
<li><a href="#plain">In plain words</a></li><li><a href="#picture">The whole picture</a></li><li><a href="#control">Control plane and metadata</a></li>
<li><a href="#services">Three services</a></li><li><a href="#streaming">The streaming lane</a></li><li><a href="#concerns">22 cross-cutting concerns</a></li>
<li><a href="#agents">The agent plane</a></li><li><a href="#rules">Nine design rules</a></li><li><a href="#binding">One design, every platform</a></li>
<li><a href="#faq">Questions people ask</a></li><li><a href="#next">Where to go next</a></li></ol></nav>

<section id="plain"><p class="eyebrow">In plain words</p><h2>Think of a factory</h2>
<p>The <b>production line</b> moves raw material through stations until it becomes a finished product; that is the row of layers in the middle, the <a href="{MED}">medallion</a>. The <b>planning office</b> decides what each station does, from written instructions, and keeps a log of every shift; that is the control plane. <b>Advisors</b> walk the floor and suggest improvements, but they cannot touch the machines; that is the agent plane. And some jobs happen at <b>every station</b>: inspection, safety, costing, record-keeping; those are the cross-cutting concerns. A good factory builds those in from day one, instead of adding an inspector after the first recall.</p></section>

<section id="picture"><p class="eyebrow">The whole picture</p><h2>Planes on top, the line in the middle, concerns underneath</h2>
<p>Read it top to bottom, then left to right. Data moves one way along the middle row. Every box with a small circle opens its own page.</p>
<figure class="diagram" style="padding:10px">{drawing()}<figcaption>The data platform, drawn right. Click a layer, a band or a concern to go one level down.</figcaption></figure></section>

<section id="control"><p class="eyebrow">Control plane</p><h2>Written instructions in, pipelines out</h2>
<p>People (and agents, by pull request) describe each source and table in a short YAML file, the <b>platform manifest</b>: where it comes from, how it is loaded, its key, how history is kept, its contract, its quality checks, who owns it, its budget. Nothing else is hand-written.</p>
<ol><li><b>Validate.</b> A validator checks every key against a registry of allowed keys and types.</li>
<li><b>Load the metadata DB.</b> A loader writes the manifest into a metadata database: master tables for sources and datasets, key-value config tables, and one stable view that every pipeline reads. One database per environment (dev, test, prod), same schema. The design is described in <a href="https://medium.com/@basant.choudhary09/metadata-db-design-for-data-engineering-components-ingestion-processing-data-quality-data-6b355ad5ecb9">Metadata DB Design for Data Engineering Platforms</a>.</li>
<li><b>Generate.</b> Generators turn the metadata into pipelines for the chosen platform, using that platform's binding file.</li>
<li><b>Run and record.</b> The orchestrator runs them; every run is logged with a fingerprint of the exact config it used, so any replay or backfill can prove what it ran with.</li></ol>
<p>Runtime state (watermarks, run logs, quality results) is kept apart from configuration, so changing a setting never rewrites history.</p>
<p><b>Zoom in:</b> <a href="/learn/data-platform-architecture/metadata-store/">The metadata store</a>: the tables, the reader view, the YAML loader and the fingerprint, with code.</p></section>

<section id="services"><p class="eyebrow">Services</p><h2>Three services, three owners</h2>
<div class="tw"><table class="t"><tr><th>Service</th><th>Covers</th><th>Its job</th><th>Typical owner</th></tr>
<tr><td><b>A · Acquire</b></td><td>sources → landing → bronze → silver</td><td>Get every source in, faithfully and safely, and make one clean, trusted row per real thing.</td><td>Platform / ingestion team</td></tr>
<tr><td><b>B · Model</b></td><td>gold → semantic</td><td>Shape data for the business: facts, dimensions, marts, data products and metric definitions.</td><td>Analytics engineers with the business</td></tr>
<tr><td id="serve"><b>C · Serve</b></td><td>experiences</td><td>Put it in front of people and programs: dashboards, conversation UIs, APIs, sharing, ML features, documents for AI.</td><td>Product and BI teams</td></tr></table></div>
<p>Splitting them means each can change at its own pace, and a failure in one doesn't silently corrupt another: Serve only ever reads from Model, and Model only from Acquire's silver.</p></section>

<section id="streaming"><p class="eyebrow">Streaming</p><h2>One medallion, two speeds</h2>
<p>Streaming does not need a second architecture. Hot tables flow through the same layers continuously: event stream → bronze stream → silver streaming tables → gold incremental views. The contracts, quality checks, lineage and rules are the same; only the speed changes. Late events are handled with watermarks, and every step must still be safe to run twice.</p></section>

<section id="concerns"><p class="eyebrow">Cross-cutting</p><h2>22 concerns, built in from day one</h2>
<p>These are the jobs that apply to every table at every hop. Each one is declared per table in the manifest and is on by default. They fall into five questions.</p>{concern_html}</section>

<section id="agents"><p class="eyebrow">Agent plane</p><h2>Agents that may only suggest</h2>
<p>Agents help with two jobs: writing metadata, and handling incidents. Neither lets an agent change production. This is deterministic first: code that can decide something decides it, and an agent only comes in where judgement is really needed.</p>
<div class="tw"><table class="t"><tr><th>Agent</th><th>Reads</th><th>Writes</th><th>Needs a person when</th></tr>{agents}</table></div>
<p><b>The self-healing loop:</b> detect → triage → fix in dev → validate → gate → pull request → deploy → verify it held → roll back if not.</p>
<p id="simulation"><b>Simulation:</b> a pretend shop produces data on its own clock, and incidents are planted on purpose (a renamed column, a day sent twice, a source going dark). The platform must catch each one before production does.</p></section>

<section id="rules"><p class="eyebrow">Rules</p><h2>Nine design rules</h2>
<p>Each rule says what it forbids and can be checked by a machine.</p>{rules}</section>

<section id="binding"><p class="eyebrow">Concept vs product</p><h2>One design, every platform</h2>
<p>The picture above names no product. Each platform gets a binding: which product does each job. Moving platform means a new binding and new adapters, not a new design.</p>
<div class="tw"><table class="t"><tr><th>Job</th><th>AWS</th><th>Azure / Fabric</th><th>Google Cloud</th><th>Databricks</th><th>Open source</th></tr>{binding}</table></div>
<p class="note">Product names change often; check the current docs before you build.</p></section>

<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{faq}</section>

<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2>
<p><b>Zoom into the middle row:</b> <a href="{MED}">Medallion architecture, drawn right</a>: each layer, one order followed through all of them, the rules and the mistakes.</p>
<p><b>The ideas behind the boxes:</b> <a href="/concepts/#data-engineering">key data engineering concepts</a>, one short page each.</p>
<p><b>Learn it step by step:</b> <a href="/paths/data-engineering/">the Data Engineering path</a>, on AWS, Azure, Google Cloud, Databricks or open source.</p>
<p><b>Each component, in detail:</b> <a href="/learn/data-platform-architecture/metadata-store/">metadata store</a> · <a href="/learn/data-platform-architecture/ingestion/">ingestion</a> · <a href="/learn/data-platform-architecture/bronze-to-silver/">bronze to silver (SCD Type 1 and 2)</a> · <a href="/learn/data-platform-architecture/gold/">gold</a>.</p>
<p><b>Run it:</b> <a href="/learn/data-platform-sim/">DataTwin Studio</a>: watch one batch go through the whole platform, recorded from a real run, then send the same file again and see what breaks.</p></section>"""
    ld = [
        {"@context": "https://schema.org", "@type": "TechArticle", "headline": "Data platform architecture, drawn right",
         "description": "A free guide to modern data platform architecture: control plane, metadata-driven pipelines, medallion layers, three services, streaming, 22 cross-cutting concerns and agents that only propose.",
         "url": URL, "inLanguage": "en", "isAccessibleForFree": True, "dateModified": "2026-10-27",
         "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
         "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Learn", "item": f"{SITE}/learn/"},
            {"@type": "ListItem", "position": 2, "name": "Data platform architecture", "item": URL}]},
    ]
    css = M.CSS.replace(".diagram svg { width:100%; min-width:640px;", ".diagram svg { width:100%; min-width:760px;") + "<style>.diagram a:hover rect{stroke-width:2.6} .diagram a{cursor:pointer}</style>"
    head = css + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    desc = "Data platform architecture explained: control plane, metadata-driven pipelines, medallion layers, streaming, 22 cross-cutting concerns, products per platform."
    return wb.page("Data platform architecture, drawn right", desc, URL, body, head)


def main():
    out = ROOT / "learn" / "data-platform-architecture"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("architecture guide ->", out)


if __name__ == "__main__":
    main()
