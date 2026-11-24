"""Databricks compute and cost: a hub and fourteen pages at /learn/databricks-compute/.

    python3 _guides/databricks_compute.py      (then python3 _site/nav.py and python3 _site/seo.py)

Cluster anatomy, SQL warehouses and serverless, Photon and every cache, how billing works,
dividing the bill, system tables, Delta Sharing and cross-region cost, backup and recovery.
Body text lives in _guides/databricks_compute/<slug>.html (sections with ids s1..s26);
this file holds titles, FAQ, related links and the page shell. Pages that already exist on
the site (compute choice, egress, Azure backup, tagging, UniForm) are linked, not repeated.
Prices and limits are illustrative and flagged on the page.
"""
import json
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "_paths"))
import components as C  # noqa: E402

wb = C.wb
SITE = wb.SITE
BASE = "/learn/databricks-compute/"
DATE = "2026-11-20"
SRC = Path(__file__).parent / "databricks_compute"

CSS = C.CSS + """<style>
  .tw { overflow-x:auto; margin:14px 0; } .tw table.t { min-width:620px; }
  .fig { margin:16px 0; overflow-x:auto; } .fig svg { display:block; width:100%; height:auto; max-width:1000px; } @media (max-width:760px) { .fig svg { min-width:700px; } } .fig p { font-size:13px; color:var(--faint); margin:4px 0 0; }
  .fig svg text { font-family:inherit; font-size:14.5px; fill:#1F1F1F; } .fig svg .b { font-weight:700; } .fig svg .h { font-weight:700; font-size:15.5px; } .fig svg .m { fill:#4a5565; font-size:13px; }
  .fig svg .bx { fill:#fff; stroke:#1F1F1F; stroke-width:1.5; } .fig svg .cu { fill:#fff4d6; stroke:#1F1F1F; stroke-width:1.5; } .fig svg .db { fill:#eef3fb; stroke:#1F1F1F; stroke-width:1.5; }
  .fig svg .ca { fill:#eaf6ef; stroke:#1F1F1F; stroke-width:1.5; } .fig svg .gr { fill:#f3f3f3; stroke:#777; stroke-width:1.3; } .fig svg .ds { stroke-dasharray:6 4; }
  .fig svg .ln { stroke:#1F1F1F; stroke-width:1.5; fill:none; } .fig svg .lg { stroke:#2f7d4f; stroke-width:1.8; fill:none; }
  .callout { border:var(--line); border-radius:var(--wob); padding:10px 16px; background:#eef3fb; margin:14px 0; } .callout.w { background:#fff4d6; } .callout.g { background:#eaf6ef; } .callout p, .callout code { color:#1F1F1F; } .callout p { margin:6px 0; }
  td.v { font-weight:600; white-space:nowrap; } .pursue { color:#2f7d4f; } .drop { color:#b0372c; }
  .tag { display:inline-block; font-size:12px; font-weight:600; padding:0 8px; border:1.5px solid #1F1F1F; border-radius:99px; } .tag.c { background:#fff4d6; } .tag.d { background:#eef3fb; }
  .verify { font-size:13.5px; color:var(--faint); }
</style>"""

DEFS = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'
        '<marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#1F1F1F"/></marker>'
        '<marker id="arg" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#2f7d4f"/></marker>'
        '</defs></svg>')

I = "/learn/databricks-interview/"
RELATED = {
    "compute-choice": ("Which compute for which job", I + "compute-choice/"),
    "aqe": ("AQE, Photon, Predictive Optimization", I + "aqe-photon-po/"),
    "levers": ("Biggest cost and performance levers", I + "cost-and-performance/"),
    "tags": ("Tagging best practices", I + "tagging-best-practices/"),
    "egress": ("Cheapest way to move data in and out", I + "egress-and-ingress/"),
    "backup-az": ("Backup and recovery on Azure", I + "backup-and-recovery-azure/"),
    "uniform": ("UniForm", I + "uniform/"),
    "maint": ("Who maintains your tables", "/learn/table-maintenance/"),
    "calc": ("Databricks cost calculator", "/learn/data-systems/platform/cost/calculator/"),
    "cost": ("Cost and FinOps for the platform", "/learn/data-systems/platform/cost/"),
}

PAGES = [
    dict(slug="cluster-architecture", title="Databricks cluster architecture: planes, driver, workers, memory and machine types", short="Cluster anatomy",
         desc="The control plane and compute plane, the driver and worker anatomy of every cluster, all-purpose and job clusters and pools, what lives in RAM and on local disk, and the five machine families.",
         related=["compute-choice", "aqe"],
         qa=[("What is the difference between the driver and a worker?", "The driver plans the query, cuts it into tasks and collects small results. Workers run an executor that executes the tasks, one task per CPU core at a time. A driver that runs out of memory kills the whole application."),
             ("Which machine family should I pick?", "General purpose when unsure, memory optimized when the Spark UI shows spill, storage optimized for read-heavy and interactive work that benefits from the SSD disk cache, compute optimized for CPU-bound jobs, GPU only for model training."),
             ("Why does a pool start clusters faster?", "A pool keeps booted idle VMs, so a cluster skips the cloud's VM boot step. You still pay the cloud for idle pool VMs, but no Databricks DBUs for them.")]),
    dict(slug="warehouses-and-serverless", title="SQL warehouses, serverless and who owns it: classic, pro, serverless, prod and dev, BU1 and BU2", short="Warehouses and serverless",
         desc="Classic, pro and serverless SQL warehouses compared, serverless notebooks and jobs, performance versus standard mode, who owns serverless (account, workspace, prod and dev, business units), and which to pick.",
         related=["compute-choice", "aqe"],
         qa=[("Will client A and client B get different serverless?", "Yes. They are different accounts and Databricks isolates each customer's serverless workloads from every other customer's. Nothing is shared at the VM level."),
             ("Can one client have separate serverless for prod and dev, or BU1 and BU2?", "Yes. Use separate workspaces for hard separation, and separate warehouses plus serverless budget policies per business unit for soft separation. Each workspace uses serverless independently."),
             ("Bigger warehouse or more clusters?", "A bigger size makes one query faster. More clusters let more queries run at once without queueing. They fix different problems.")]),
    dict(slug="choosing-compute", title="Choosing Databricks compute: classic, serverless, SQL warehouses, users, batch and live access, settings and mistakes", short="Choosing compute",
         desc="How many kinds of serverless there are, what you can and cannot configure on each, the factors that decide the choice (users, concurrency, latency, batch versus live, language, networking), scenarios with verdicts, sizing, common mistakes and what to watch out for.",
         related=["compute-choice", "levers", "tags", "cost"],
         qa=[("How many types of serverless does Databricks have?", "Four for your own code and SQL: serverless SQL warehouses, serverless notebooks, serverless jobs and serverless pipelines. Other features such as Model Serving and Predictive Optimization are separate serverless products with their own settings and billing."),
             ("What can I configure on serverless jobs?", "Performance mode, the environment version and libraries, the job timeout and retries, notifications, tags and a budget policy. You cannot choose machine types, worker counts, Photon or init scripts."),
             ("A warehouse is slow. Do I make it bigger or add clusters?", "Make it bigger when a single query is slow or spills to disk. Add clusters when queries wait in a queue. Size helps one query, clusters help concurrency."),
             ("When should I use classic compute instead of serverless?", "When you need Scala or RDD code, custom images or init scripts, custom networking, always-on low-latency streaming, runs longer than 7 days, or the lowest hourly price on spot for large steady work.")]),
    dict(slug="compute-settings", title="Databricks compute settings reference: SQL warehouse types, job clusters, node types, access modes and wrong settings", short="Compute settings",
         desc="Every kind of compute in one map, then the settings for SQL warehouses (serverless, pro, classic), serverless and classic jobs, all-purpose clusters and node types, with the good value, the wrong value and what to check.",
         related=["compute-choice", "levers", "tags", "cost"],
         qa=[("Do classic SQL warehouses still exist?", "Yes. The three types are serverless, pro and classic, and I found no deprecation notice. Serverless is the UI default where available, and classic or pro remain for custom networking, hybrid connections, or when serverless is not enabled."),
             ("Why might my warehouse be classic when I wanted serverless?", "Warehouses created through the API or Terraform without the type set have defaulted to classic. Set the warehouse type and the serverless flag explicitly."),
             ("Should I turn on autoscaling for a streaming job cluster?", "Databricks advises against it, because classic autoscaling is slow to shrink streaming clusters. Use a fixed size, or move the workload to a pipeline with enhanced autoscaling."),
             ("Can I use Graviton for everything?", "No. It is documented as unsupported for Databricks SQL, declarative pipelines and Container Services, and Python UDFs need runtime 15.2 or later. Test plain batch jobs first.")]),
    dict(slug="cost-by-workload", title="Databricks cost map: every workload type, every compute type, DBU rates, the mapping and what goes wrong", short="Cost by workload",
         desc="One table of workload types, one of compute types with illustrative DBU rates, and the mapping between them with worked monthly examples, the wrong-compute multipliers and a monthly check.",
         related=["levers", "calc", "tags", "cost"],
         qa=[("Why can the same job cost so differently on different compute?", "Because the price per DBU depends on the product, and classic compute adds a separate cloud bill for machines. In the examples, the same nightly job costs about 2.2 times more on an all-purpose cluster than on jobs compute."),
             ("Is serverless more expensive per DBU?", "Yes on paper, because the rate includes the machines. Compare the full monthly cost, including cloud VMs, boot time and idle time on classic."),
             ("Which numbers on this page can I rely on?", "Use them for ratios and mistakes only. The rates are third-party summaries of AWS list prices, not the official price list, and serverless DBU use is assumed equal to classic."),
             ("What is the quickest way to find a mismatch?", "List your top 10 costs, name the workload and the compute for each, and check them against the mapping table.")]),
    dict(slug="logs-and-visibility", title="Why serverless feels opaque: what Databricks logs, how to extract it programmatically and the cheapest way to read it", short="Logs and visibility",
         desc="What you lose and what you keep on serverless, every source of run, query, billing, audit and lineage information with retention, how to extract it by SQL and REST API, and the cheapest way to do it.",
         related=["tags", "levers", "cost", "calc"],
         qa=[("Why is serverless compute opaque?", "It runs in Databricks' account, so there are no machines to inspect. Databricks says Spark logs and the Spark UI are not available for serverless notebooks and jobs. You use the query profile, query history and system tables instead."),
             ("Can I see cost per job on serverless?", "Yes. The billing usage system table fills in the job run id for serverless jobs, so you can total DBUs per job or run."),
             ("What is the cheapest way to read the logs?", "Call the REST APIs on a schedule, which need no warehouse, and run one small daily incremental pull of the system tables on the smallest serverless warehouse. Keep the copy in your own store."),
             ("Is there an equivalent of reserved instances for serverless?", "Not for machines, because they are Databricks' own. A commit discount on DBUs applies to serverless. On classic compute you can also reserve the VMs.")]),
    dict(slug="photon-and-caches", title="Photon and every Databricks cache: result, Spark, disk, page and metadata caches", short="Photon and caches",
         desc="How Photon replaces Spark's JVM operators with a vectorized C++ engine, when it helps, and which cache each compute type supports: result cache, Spark cache, disk cache, OS page cache, Delta metadata cache.",
         related=["aqe", "levers"],
         qa=[("Does Photon speed up everything?", "No. It speeds up scans, joins, aggregations and big writes. It does nothing for Python UDFs, RDD code, very small queries or ML training."),
             ("Disk cache or Spark cache?", "The disk cache keeps data file copies on local SSD, is automatic and costs no RAM. The Spark cache keeps a specific DataFrame in memory and you manage it. Rely on the disk cache by default.")]),
    dict(slug="how-billing-works", title="How Databricks billing works: DBUs, two invoices, SKUs, autoscaling and billing tracing", short="How billing works",
         desc="The DBU formula, classic versus serverless invoices, illustrative rates and worked examples, SKU families, what autoscaling does to cost and what you can see, and why people say they need classic for billing tracing.",
         related=["tags", "levers", "calc", "cost"],
         qa=[("How is Databricks billed?", "Databricks charge = DBUs used x price per DBU. On classic compute you also pay your cloud for VMs, disks and network. On serverless the machines are inside a higher DBU price."),
             ("Why do people say they need classic for billing tracing?", "Tags on a classic cluster reach both the Databricks usage records and the cloud's VM costs, so you can reconcile two bills at machine level. Serverless has no VMs of yours to tag, though budget policies now tag serverless usage in the usage table."),
             ("Can I see autoscaling in the bill?", "Partly. Classic gives event logs and per-minute node data but billing is hourly, so you stitch them. Warehouses have scale events. Serverless jobs and notebooks show no scaling detail, only DBUs.")]),
    dict(slug="dividing-the-bill", title="Dividing the Databricks bill: the chargeback architecture", short="Dividing the bill",
         desc="Force tags, record usage, roll it up: the architecture for charging Databricks cost to business units and environments, the four workspace layouts compared, and the per-query gap.",
         related=["tags", "cost"],
         qa=[("What is the best layout for several business units?", "A workspace per business unit and environment, a catalog per business unit, and mandatory tags as a second check. It gives the cleanest bill and the cleanest access, at the cost of more workspaces to automate."),
             ("Can I get cost per query or per user?", "Not from billing. Billing stops at the warehouse or cluster. You can estimate shares from query history, which is why separate warehouses per BU are best.")]),
    dict(slug="system-tables", title="Databricks system tables: contents, why reading them costs money, copying them cheaply, and what is hidden", short="System tables",
         desc="What the system schemas hold, why querying them always costs compute, the cheapest incremental copy, whether Lakebase or UniForm would help, and the information Databricks does not show.",
         related=["tags", "uniform", "cost"],
         qa=[("Why does querying system tables cost money?", "A query needs a running warehouse or cluster, the tables are large, and you cannot index or reorganise them. Roll up once into your own small table and query that."),
             ("Does copying them to Lakebase solve it?", "No. The copy still reads the system tables with compute. Lakebase only makes later reads cheaper, and a small Delta table with a tiny serverless warehouse is usually cheaper and simpler."),
             ("Would UniForm make system tables free to read?", "No. Format is not what costs money. Any reader needs compute somewhere. UniForm would only let you choose a different engine.")]),
    dict(slug="delta-sharing-and-regions", title="Delta Sharing inside, and how to avoid cross-region cost on Databricks", short="Sharing and regions",
         desc="How Delta Sharing works internally (signed file links read straight from storage), when it helps with cost, why cross-region transfer is charged and the seven places it hides in Databricks.",
         related=["egress", "uniform"],
         qa=[("How does Delta Sharing work internally?", "The recipient asks a sharing server, which checks permission and returns short-lived signed links to the Parquet files. The recipient downloads straight from the provider's cloud storage. The server never carries the data."),
             ("How do I avoid cross-region cost?", "Keep compute and storage in the same region, share small aggregates instead of raw tables, replicate once to the recipient's region, and never read big remote tables repeatedly.")]),
    dict(slug="backup-and-recovery-architecture", title="Backup and recovery architecture for Databricks: the safe, clean design on any cloud", short="Backup architecture",
         desc="Time travel is not a backup. Three protections for three disasters: fast undo, an immutable backup in a separate account, and a rebuildable second region, with the design rules and a failure-to-tool table.",
         related=["backup-az", "egress"],
         qa=[("Is Delta time travel a backup?", "No. It lives in the same storage and VACUUM deletes old files by design. It is a fast undo."),
             ("Is copying the bucket to another region safe for Delta tables?", "Not by itself. Files can arrive out of order, so a table's log may point at files that have not arrived. Use deep clone or validate after replication.")]),
    dict(slug="sharing-data-out", title="Sharing data in and out of Databricks: Delta Sharing, clean rooms, UniForm, federation and every other way, with pictures",
         short="Sharing data in and out",
         desc="Two directions drawn method by method: how others read data Databricks owns (Delta Sharing, clean rooms, Marketplace, Iceberg REST catalog, SQL warehouse, push, export) and how Databricks reads data others own (federation, external locations, connectors, Auto Loader, streams), each with how it works inside, when to use it, when not to, cost, performance and security.",
         related=["egress", "uniform", "cost"],
         qa=[("Is a clean room the same as Delta Sharing?", "No. Delta Sharing gives the other side rows to read. A clean room lets both sides run one approved piece of code over combined data, and only the approved results come out. Databricks clean rooms use Delta Sharing underneath."),
             ("Is UniForm a way of sharing data?", "No. UniForm writes Iceberg metadata next to the Delta log so other engines can read the same files. Sharing needs a catalog and permissions as well, such as the Iceberg REST catalog or Delta Sharing."),
             ("Why not use Delta Sharing for Athena and Redshift?", "Delta Sharing needs a client on the reading side, and to my knowledge Athena and Redshift do not have one. For your own AWS engines, use the Iceberg REST catalog or Glue federation. Use Delta Sharing for a different organisation or for Spark and pandas clients."),
             ("When should I ingest instead of federate?", "When the same remote table is read again and again. Federation reads the source on every query, so a routine query is better served by a copy kept current.")]),
    dict(slug="cost-saving-hacks", title="Databricks cost-saving hacks: the biggest levers, hidden tricks and checked settings", short="Cost-saving hacks",
         desc="Find where the money goes, then the compute, warehouse, pipeline, data and cloud-side changes that cut a Databricks bill, each with a Pursue or Drop verdict and the limits that were checked against current documentation.",
         related=["levers", "tags", "compute-choice", "cost"],
         qa=[("What is the first thing to do to cut a Databricks bill?", "Rank spend by job, warehouse and cluster from the usage system table, then fix the top few. A small number of items usually carry most of the cost."),
             ("Is serverless Standard mode cheaper?", "It uses fewer DBUs than the default performance mode, and Databricks cites savings of up to 70 percent. Start-up is slower, typically 4 to 6 minutes, and the start-up time is not billed. It suits work that can wait."),
             ("How do I stop a runaway query?", "Set a statement timeout. The default is 2 days. You can set it for a session or the workspace. A warehouse-level setting is in Beta."),
             ("Why does a job keep billing after it hangs?", "Without a job timeout it runs until it ends. A timeout applies to each retry, so set the retry limit too.")]),
]
for p in PAGES:
    p["body_file"] = SRC / f"{p['slug']}.html"


def siblings(cur):
    return '<div class="sib">' + "".join(
        f'<span>{E(p["short"])}</span>' if p["slug"] == cur else f'<a href="{BASE}{p["slug"]}/">{E(p["short"])}</a>' for p in PAGES) + "</div>"


def related(keys):
    return " · ".join(f'<a href="{RELATED[k][1]}">{E(RELATED[k][0])}</a>' for k in keys)


def render(p):
    url = f"{SITE}{BASE}{p['slug']}/"
    body = p["body_file"].read_text()
    full = f"""{DEFS}<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › <a href="{BASE}">Databricks compute and cost</a> › {E(p['short'])}</p>
<p class="eyebrow" style="margin-top:22px">Databricks compute and cost · data engineering</p>
<h1>{E(p['title'])}</h1><p class="lede">{E(p['desc'])}</p>{siblings(p['slug'])}
<p class="verify">Prices, defaults, limits and preview status change often, and dollar figures here are illustrations. Check the current Databricks documentation and price list before quoting a number.</p>
{body}
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(p['qa'])}</section>
<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2><p>Related on this site: {related(p['related'])}</p><p><a href="{BASE}">All Databricks compute and cost pages</a> · <a href="/data-engineering/">All data engineering</a> · <a href="/platforms/databricks/">Databricks on this site</a></p>{siblings(p['slug'])}</section>"""
    return wb.page(p["title"], p["desc"], url, full, head(p, url))


def head(p, url):
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": p["title"], "description": p["desc"], "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["qa"]]}]
    return CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)


def hub():
    url = f"{SITE}{BASE}"
    title = "Databricks compute and cost, explained end to end"
    desc = "Every kind of Databricks compute drawn and explained: clusters, SQL warehouses, serverless, Photon, caches, how billing works, dividing the bill, system tables, Delta Sharing and cross-region cost, and backup and recovery."
    cards = "".join(f'<div class="card"><h3><a href="{BASE}{p["slug"]}/">{E(p["title"])}</a></h3><p class="one">{E(p["desc"])}</p></div>' for p in PAGES)
    body = f"""{DEFS}<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › Databricks compute and cost</p>
<p class="eyebrow" style="margin-top:22px">Databricks compute and cost · data engineering</p><h1>{E(title)}</h1>
<p class="lede">Read it in order once, then use it as a reference. Plain words first, a drawing for every mechanism, and a Pursue or Drop verdict wherever there is a choice.</p>
<p class="verify">Prices, defaults, limits and preview status change often, and dollar figures are illustrations. Check the current Databricks documentation before quoting a number.</p>
<section id="start"><p class="eyebrow">Start here</p><h2>Why it feels confusing: four separate questions</h2>{(SRC / '_hub_start.html').read_text()}</section>
<div class="cards">{cards}</div>
<section id="more"><p class="eyebrow">Already on this site</p><h2>Related pages</h2><p>{related(['compute-choice', 'aqe', 'levers', 'tags', 'egress', 'backup-az', 'uniform', 'maint', 'cost', 'calc'])}</p></section>
<section id="verify"><p class="eyebrow">Check these</p><h2>Bits to double-check against current docs</h2>{(SRC / '_hub_verify.html').read_text()}</section>"""
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "description": desc, "url": url, "inLanguage": "en", "isAccessibleForFree": True, "dateModified": DATE}]
    h = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(title, desc, url, body, h)


def build_all():
    out = {"learn/databricks-compute/index.html": hub()}
    for p in PAGES:
        out[f"learn/databricks-compute/{p['slug']}/index.html"] = render(p)
    return out


def main():
    for rel, html in build_all().items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html)
        print("databricks compute ->", path)


if __name__ == "__main__":
    main()
