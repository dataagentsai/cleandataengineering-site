"""Declarative or not: Spark Declarative Pipelines, open source and on Databricks. One page at
/learn/spark-declarative-pipelines/.

    python3 _guides/declarative_pipelines.py      (then python3 _site/nav.py and python3 _site/seo.py)

Lesson first (what declarative means, with a picture), then: open-source SDP vs Databricks Lakeflow, cost (rates from
_tools/dbx_cost/prices.json, checked 9 Nov 2026), where declarative helps and where not, bronze to silver, silver to
gold, how it fits a harness, decisions with verdicts, what is not settled yet, FAQ, sources.
Facts from the Apache Spark guide (version 4.3) and Databricks docs, read 13 Nov 2026; the two disagree on whether
AUTO CDC is open source, and the page says so.
"""
import json
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "_paths"))
import components as C  # noqa: E402
from bi_choice import ar, bx, svg, t, vtable  # noqa: E402
from gold_harness_spec import CSS, fig  # noqa: E402

wb = C.wb
SITE = wb.SITE
URL_PATH = "/learn/spark-declarative-pipelines/"
DATE = "2026-11-13"
TITLE = "Declarative or not: Spark Declarative Pipelines, open source and on Databricks"
DESC = ("What declarative pipelines are, open-source Apache Spark Declarative Pipelines vs Databricks Lakeflow, what each "
        "costs, where declarative helps and where it does not, and how it fits bronze to silver, silver to gold and a "
        "metadata-driven harness.")
PRICES = json.loads((ROOT / "_tools" / "dbx_cost" / "prices.json").read_text())["dbu"]


# ------------------------------------------------------------------ drawings
def d_two_ways():
    i = bx(10, 10, 470, 220, [""], "w", 14) + t(245, 36, "you write the steps (imperative)", 16, "middle")
    for k, s in enumerate(["read new rows since my bookmark", "transform", "merge into the target",
                           "save the bookmark", "run table B after table A"]):
        i += bx(40, 52 + k * 34, 410, 28, [s], "y", 13)
    i += bx(520, 10, 470, 220, [""], "w", 14) + t(755, 36, "you declare the tables (declarative)", 16, "middle")
    i += bx(550, 60, 410, 56, ["table B = transform(table A)", "table C = summary of table B"], "g", 14)
    i += t(755, 146, "the engine works out:", 13, "middle")
    i += bx(550, 158, 410, 56, ["order, what is new, checkpoints,", "retries, full or incremental refresh"], "b", 13)
    return svg(1000, 242, "Two ways to build a pipeline. Imperative: you write every step yourself, from reading new rows "
                          "since a bookmark to merging, saving the bookmark and running tables in order. Declarative: you "
                          "declare each table as a transformation of others, and the engine works out the order, what is "
                          "new, checkpoints, retries and whether to refresh in full or incrementally.", i)


def d_layers():
    i = bx(10, 10, 980, 200, [""], "w", 14) + t(500, 34, "Databricks Lakeflow Spark Declarative Pipelines", 16, "middle")
    i += bx(30, 50, 450, 140, ["Apache Spark Declarative Pipelines", "(open source, Spark 4.1 and later)",
                               "tables, materialized views, views,", "the graph, dry-run, checkpoints"], "g", 14)
    extras = ["AUTO CDC from snapshots", "data quality expectations", "queryable event log",
              "update flows, foreachBatch sinks", "continuous mode", "incremental refresh, serverless, catalog"]
    for k, s in enumerate(extras):
        i += bx(510 + (k % 2) * 235, 50 + (k // 2) * 48, 225, 40, [s], "b", 13)
    return svg(1000, 222, "The open-source Apache Spark Declarative Pipelines engine (tables, materialized views, views, "
                          "the dependency graph, dry-run and checkpoints) sits inside Databricks Lakeflow, which adds AUTO "
                          "CDC from snapshots, data quality expectations, a queryable event log, update flows and "
                          "foreachBatch sinks, continuous mode, incremental refresh, serverless compute and the catalog.", i)


# ------------------------------------------------------------------ content
WORDS = [
    ("Imperative pipeline", "You write each step: read, transform, write, remember where you stopped, run the next table. A Spark job or notebook."),
    ("Declarative pipeline", "You declare what each table is (a transformation of other tables); the engine decides order, what is new and how to refresh."),
    ("Apache Spark Declarative Pipelines (SDP)", "The open-source declarative engine in Apache Spark from version 4.1, donated by Databricks; Python module pyspark.pipelines and the spark-pipelines command."),
    ("Lakeflow Spark Declarative Pipelines", "Databricks' product built on SDP (formerly Delta Live Tables), with production features on top."),
    ("Streaming table", "A table fed by one or more streaming flows; each run reads only what is new, using checkpoints."),
    ("Materialized view", "A query stored as a table, refreshed by the engine; one batch flow."),
    ("AUTO CDC", "Applies change records (insert, update, delete, out of order) to a table as SCD Type 1 or Type 2."),
    ("Expectation", "A data quality rule on a table: keep, drop or fail rows that break it."),
]

COMPARE = [
    ("Streaming tables, materialized views, temporary views", "Yes", "Yes"),
    ("Dependency graph from the code; parallel runs", "Yes", "Yes"),
    ("dry-run: syntax, missing tables or columns, cycles, without data", "Yes", "Yes (validate)"),
    ("Checkpoints, refresh and full refresh per table", "Yes", "Yes"),
    ("Sinks", "Append-only, Python only", "Plus update flows and foreachBatch sinks"),
    ("AUTO CDC from change records (SCD 1 and 2)", "Checked in Spark's source (13 Nov 2026): none in 4.1, SCD Type 1 only in 4.2, Type 1 and 2 in 4.3. Needs a target with row-level updates (Iceberg or similar). Databricks' comparison page still says Lakeflow only", "Yes"),
    ("AUTO CDC from full snapshots", "No", "Yes"),
    ("Data quality expectations", "No", "Yes"),
    ("Queryable event log", "No", "Yes"),
    ("Continuous mode", "No", "Yes"),
    ("Incremental refresh of materialized views", "Not stated in the guide", "Yes, when possible"),
    ("Where it runs", "Any Spark 4.x: a laptop, a cluster, other clouds' Spark services", "Databricks only, on its runtime and serverless"),
    ("Code portability", "-", "Databricks says transformation code stays portable to other SDP runtimes; Lakeflow-only features do not move"),
]


def cost_rows():
    def r(k):
        return PRICES[k]["premium"]
    jc, js = r("jobs_classic"), r("jobs_serverless")
    return [
        ("Jobs, classic compute", f"${jc:.2f}", "Plus the cloud machines", "Baseline"),
        ("Declarative pipelines Core, classic", f"${r('dlt_core'):.2f}", "Plus the cloud machines", f"{r('dlt_core') / jc:.1f}x jobs"),
        ("Declarative pipelines Pro, classic (needed for AUTO CDC)", f"${r('dlt_pro'):.2f}", "Plus the cloud machines", f"{r('dlt_pro') / jc:.1f}x jobs"),
        ("Declarative pipelines Advanced, classic (needed for expectations)", f"${r('dlt_advanced'):.2f}", "Plus the cloud machines", f"{r('dlt_advanced') / jc:.1f}x jobs"),
        ("Serverless jobs and serverless pipelines", f"${js:.2f}", "Machines included; same rate for both", "Same for declarative and not"),
        ("Open-source SDP on any Spark", "No licence charge", "You pay only for the Spark you run it on", "-"),
    ]


HELPS = [
    ("Many tables with dependencies", "The graph comes from the code; no hand-kept run order", "Helps"),
    ("Streaming or frequent incremental loads", "Checkpoints and what-is-new handled by the engine", "Helps"),
    ("Catching broken pipelines before they run", "dry-run finds missing columns and cycles with no data", "Helps"),
    ("SCD Type 1 or 2 from a change feed", "AUTO CDC handles order, duplicates and deletes", "Helps (Lakeflow; open source if confirmed)"),
    ("Data quality rules attached to tables", "Expectations with keep, drop or fail", "Helps on Lakeflow only"),
    ("Simple aggregates and summaries", "Materialized views refreshed by the engine", "Helps"),
    ("Logic that needs control of how it writes", "Replace only changed windows, merge by a key with custom rules, write to several tables in one step", "Does not help: you fight the engine"),
    ("Business bookkeeping around a load", "Completeness per window, restatement records, correction plans, a row ledger, a run log in your own metadata store", "Does not help: not its job"),
    ("Keys looked up as of an event, with late members", "Surrogate keys, unknown members, re-keying", "Does not help"),
    ("Seeing every intermediate step", "Declarative hides steps by design; the event log (Lakeflow) shows flows, not your step outputs", "Partly"),
    ("Local tests on a laptop with another engine (DuckDB)", "SDP code needs Spark 4.x", "Does not help; keep logic in plain functions"),
    ("Cost on classic compute", "Declarative rates are 1.3 to 2.4 times the jobs rate", "Costs more; same on serverless"),
]

BRONZE_SILVER = [
    ("Read new bronze rows incrementally", "Streaming table over bronze, with checkpoints", "Pursue (either version)"),
    ("SCD Type 1 and 2 from change records, out of order, deletes", "AUTO CDC", "Pursue with care: Lakeflow now; open source once tested on Iceberg"),
    ("SCD Type 2 from full daily copies", "AUTO CDC from snapshots", "Lakeflow only; own code elsewhere"),
    ("Quality rules: quarantine or flag by severity", "Expectations (keep, drop, fail)", "Lakeflow only; a quarantine table with reasons is richer, keep your own stage"),
    ("Standard cleaning stages (contract check, types, time zones, personal data, provenance)", "Plain DataFrame functions called inside a flow", "Keep your stages; let the engine run them"),
    ("Mass-delete guard, source-versioned history, void a bad batch and rebuild", "No", "Keep your own"),
    ("Files landing in storage", "Databricks file ingestion inside Lakeflow", "Bind per platform"),
]

SILVER_GOLD = [
    ("Dimensions, facts and aggregates in dependency order", "The graph", "Pursue with care: a job running the harness in order does this too"),
    ("Simple aggregates and summaries", "Materialized views (incremental on Lakeflow)", "Pursue with care: optional"),
    ("Facts rebuilt by changed window with a lookback", "No: a materialized view is one batch flow over the whole table", "Keep a harness"),
    ("Surrogate keys as of the event, unknown members, re-keying", "No", "Keep a harness"),
    ("Completeness from every owed feed, restatements, correction plans, row ledger", "No", "Keep a harness"),
    ("Accumulating snapshots updated by key", "AUTO CDC Type 1 on the fact grain can do it", "Pursue with care"),
]

FIT = [
    "Keep every transformation a plain, pure function that takes DataFrames and returns one, so it runs inside SDP, inside a harness, or in a test on a laptop.",
    "Let the declarative engine own the graph, checkpoints and simple refreshes.",
    "Let the harness own what the engine does not: windows, keys as of the event, completeness, restatements, the row ledger and the run log.",
    "On Databricks, bind Lakeflow's expectations and snapshot CDC where the team wants them; keep the rules declared in your own metadata so another platform can bind them differently.",
    "Run dry-run in continuous integration for every pipeline, declarative or not.",
]

RESTRICT = [
    ("The pipeline owns its tables", "No other job may write to a streaming table. A fix to one bad batch becomes a full refresh, or a correction fed through the change feed.", "Plan recovery around it"),
    ("Removed or renamed definitions leave tables behind", "We saw it twice: after a redeploy the new pipeline could not write the old tables, and renamed definitions left orphans.", "Drop them in teardown"),
    ("Creation-time properties need a new table", "Format features set at creation are kept even by a full refresh.", "Decide the format before the first run"),
    ("Source must be append-only", "A streaming read breaks if source rows are updated or deleted (unless told to skip them).", "Read bronze, not a rewritten table"),
    ("Full refresh replays only what the source still holds", "If bronze has aged out, history cannot be rebuilt.", "Keep a baseline batch before data ages out"),
    ("Logic or schema changes may need a full refresh", "Checkpoints belong to the query.", "Treat flow changes as releases"),
    ("AUTO CDC's fixed shape", "One key set, an orderable sequence column, SCD Type 1 or 2 only, fixed __START_AT and __END_AT columns.", "Other history kinds stay in your own code"),
    ("Format on Databricks", "Pipeline tables are Delta; to be read as Iceberg they need Iceberg v3 compatibility (UniForm), not native Iceberg.", "Datasets that must be native Iceberg stay on a job"),
]

TESTED = [
    ("Our own stage function inside the flow", "Passed: dealer codes cleaned by our hygiene rule"),
    ("SCD Type 2 versions in sequence order", "Passed: versions 10, 20, 30"),
    ("A late change with an older sequence", "Passed: kept as history, never current"),
    ("A delete", "Passed: the key's version is closed"),
    ("An update to a measure", "Passed: a new version opened"),
    ("Readable as Iceberg", "Only with Iceberg v3 compatibility; v2 failed (needs column mapping, and deletion vectors off)"),
    ("The same 8-case SCD Type 2 contract our own engine passes", "Passed: 8 of 8, compared by meaning (closed versus flagged deletes)"),
    ("Our whole silver stage chain over real tyre bronze, six datasets", "Passed: equal to our job engine's silver on every dataset (two SCD2, one SCD1, three append), 0 differing rows"),
    ("Streaming read of Iceberg bronze", "Passed: a declarative pipeline stream-reads Unity Catalog managed Iceberg"),
    ("Bad rows planted in bronze", "Quarantined with their rule names; the test also exposed a gap in our own engine (contract value rules were not run), now fixed in both"),
    ("Open-source SDP, same test on a laptop", "Blocked: SCD2 AUTO CDC needs Spark 4.3, and no Iceberg or Delta release runs on 4.3 yet"),
]

DECISIONS = [
    ("Bronze to silver on Databricks", "Lakeflow streaming tables and AUTO CDC around your own cleaning stages", "Pursue"),
    ("Bronze to silver portable across clouds", "Open-source SDP with AUTO CDC on Iceberg, once tested", "Pursue with care"),
    ("Silver to gold", "A harness for facts and dimensions; SDP only for some aggregates, as an option", "Pursue"),
    ("Data quality rules", "Declared once in your metadata; bound to expectations on Lakeflow, to your own stage elsewhere", "Pursue"),
    ("Classic compute with Advanced edition for every pipeline", "Paying 2.4 times the jobs rate for features most tables do not use", "Drop: pick the edition per pipeline, or use serverless"),
    ("All logic written in SDP decorators", "Ties tests to Spark 4.x and the engine", "Drop: decorators wrap plain functions"),
]

OPEN = [
    ("Is AUTO CDC open source?", "Yes, newly: we checked Spark's source on 13 Nov 2026. Spark 4.1 has none, 4.2 has SCD Type 1 only, 4.3 has Type 1 and 2. Databricks' comparison page has not caught up."),
    ("Can open-source SCD Type 2 run today?", "Not on an open table format. We tried on a laptop: Iceberg's newest runtime (1.12) is built for Spark 4.0 and 4.1 and fails to load on 4.3, and Delta's newest (4.4.1) supports Spark up to 4.2. Until a format supports Spark 4.3, open-source declarative SCD Type 2 waits; on Databricks, Lakeflow does it today."),
    ("Does open-source SDP refresh materialized views incrementally?", "Its guide does not say. Test before relying on it for large aggregates."),
    ("Expectations in open source?", "Not in the guide today. Keep quality rules in your own stage."),
]

QA = [
    ("Why use a streaming table for a batch load?", "Streaming describes how a streaming table reads, not how long it runs. In triggered mode each run reads only what is new since its checkpoint, writes it and stops: incremental batch, with no cluster left running. AUTO CDC can only write into a streaming table, because SCD history needs a target that remembers which changes it has applied."),
    ("Are jobs and declarative pipelines both serverless?", "On Databricks both can run on serverless or classic compute; on serverless they cost the same rate per DBU with machines included, on classic declarative pipelines cost more by edition. Open-source Spark Declarative Pipelines is not a serverless product: it runs on whatever Spark you give it."),
    ("Can AUTO CDC be used for SCD Type 2 in batch loads?", "Yes. AUTO CDC reads a stream of change records, but a pipeline run in triggered mode processes the changes available and stops, which is a batch run; for full daily copies Lakeflow has AUTO CDC from snapshots. The reasons not to use it are cost (the Pro edition on classic compute), portability and history kinds it does not cover, not batch."),
    ("What is the difference between Apache Spark Declarative Pipelines and Databricks Lakeflow Declarative Pipelines?", "Apache Spark Declarative Pipelines is the open-source engine in Spark 4.1 and later: streaming tables, materialized views, the dependency graph, dry-run and checkpoints. Databricks Lakeflow is built on it and adds AUTO CDC from snapshots, data quality expectations, a queryable event log, update flows, continuous mode, incremental refresh and serverless compute."),
    ("Do declarative pipelines cost more than jobs on Databricks?", "On classic compute, yes: in our price file (AWS, Premium, checked November 2026) jobs are $0.15 per DBU and declarative pipelines $0.20 (Core), $0.25 (Pro, needed for AUTO CDC) or $0.36 (Advanced, needed for expectations), plus machines in both cases. On serverless both are $0.35 per DBU with machines included. Open-source SDP has no licence charge."),
    ("When should I use declarative pipelines?", "For many dependent tables, streaming and incremental loads, SCD from change feeds and simple aggregates. Not for logic that must control how it writes, such as replacing only changed windows, or for business bookkeeping like completeness, restatements and surrogate keys looked up as of an event."),
    ("Do declarative pipelines replace a gold harness?", "No. They can run the graph and refresh aggregates, but they do not rebuild facts by changed window, look up surrogate keys as of the event, track completeness from every owed feed or record restatements. Keep a harness for those and keep logic in plain functions both can call."),
]


def page():
    url = f"{SITE}{URL_PATH}"
    toc = "".join(f'<li><a href="#{a}">{E(b)}</a></li>' for a, b in [
        ("plain", "In plain words"), ("compare", "1. Open source vs Databricks Lakeflow"), ("cost", "2. Does declarative cost the same?"),
        ("helps", "3. Where declarative helps, and where not"), ("b2s", "4. Bronze to silver"), ("s2g", "5. Silver to gold"),
        ("fit", "6. Declarative and a harness together"), ("restrict", "6b. What declarative restricts"), ("tested", "6c. What we tested"), ("decide", "7. Decisions"), ("open", "8. Not settled yet"), ("faq", "FAQ")])
    sources = [("Apache Spark Declarative Pipelines programming guide", "https://spark.apache.org/docs/latest/declarative-pipelines-programming-guide.html"),
               ("Databricks: Spark Declarative Pipelines vs Lakeflow", "https://docs.databricks.com/aws/en/ldp/concepts/spark-declarative-pipelines"),
               ("Databricks: Lakeflow pipeline concepts", "https://docs.databricks.com/aws/en/ldp/concepts/"),
               ("Databricks: Lakeflow Declarative Pipelines pricing", "https://www.databricks.com/product/pricing/lakeflow-declarative-pipelines")]
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/data-engineering/">Data engineering</a> › Declarative pipelines</p>
<p class="eyebrow" style="margin-top:22px">Data engineering · guide</p>
<h1>{E(TITLE)}</h1>
<p class="lede">Spark now has a declarative way to build pipelines, in open source and, with more features, on Databricks. It removes a lot of plumbing. It does not remove the hard business parts of a data platform, and on classic Databricks compute it costs more. This page says where it pays and where it does not.</p>
<div class="gh">
<div class="box"><b>In one paragraph.</b> Declarative pipelines let you say what each table is and let the engine work out order, what is new and how to refresh. Open-source Apache Spark Declarative Pipelines (Spark 4.1 and later) gives the engine, the graph, checkpoints and dry-run; Databricks Lakeflow adds snapshot change capture, data quality expectations, an event log, continuous mode and serverless. Use it for bronze to silver and for simple aggregates. Keep a harness for gold facts: changed windows, keys as of the event, completeness and restatements. On serverless it costs the same as a job; on classic compute 1.3 to 2.4 times as much.</div>
<ul class="toc">{toc}</ul>

<section id="plain"><p class="eyebrow">Lesson first</p><h2>In plain words</h2>
<p>A recipe can be a list of steps (chop, fry, stir, plate) or a description of the dish (a curry made of fried onions and tomatoes). A good cook given the description works out the steps. Declarative pipelines are the second kind: you describe each table, the engine does the steps.</p>
{fig(d_two_ways(), "Imperative: you own every step. Declarative: you own the definitions, the engine owns the steps.")}
{C.table(["Word", "What it means here"], WORDS)}</section>

<section id="compare"><p class="eyebrow">1. Two products</p><h2>Open-source SDP vs Databricks Lakeflow</h2>
{fig(d_layers(), "Lakeflow is the open-source engine plus production features that exist only on Databricks.")}
{C.table(["Feature", "Apache Spark Declarative Pipelines (open source)", "Lakeflow Spark Declarative Pipelines (Databricks)"], COMPARE)}</section>

<section id="cost"><p class="eyebrow">2. Cost</p><h2>Do declarative and non-declarative cost the same?</h2>
<p>On serverless, yes. On classic compute, no: Databricks charges a higher rate per unit of compute (DBU) for declarative pipelines, by edition. Rates below are per DBU, AWS, Premium tier, from our <a href="/learn/data-systems/platform/cost/calculator/">cost calculator's</a> price file (checked 9 Nov 2026; check current prices before deciding).</p>
{C.table(["Compute", "Per DBU", "Machines", "Compared with jobs"], cost_rows())}
<div class="box"><b>Worked example.</b> A pipeline that uses 10 DBUs an hour for one hour a day, on classic compute: as a job $1.50 a day, as declarative Core $2.00, Pro $2.50, Advanced $3.60, plus the same machine cost each way. On serverless: $3.50 a day either way, machines included. The edition is per pipeline: pay for Advanced only where expectations are used.</div></section>

<section id="helps"><p class="eyebrow">3. The honest list</p><h2>Where declarative helps, and where it does not</h2>{C.table(["Need", "Why", "Declarative"], HELPS)}</section>

<section id="b2s"><p class="eyebrow">4. Bronze to silver</p><h2>Bronze to silver: the best fit</h2>
<p>Silver is mostly the same steps for every table, often streaming, with history from change records: exactly what a declarative engine is good at. The cleaning stages themselves stay yours, as plain functions the engine calls.</p>
{vtable(["Silver need", "Declarative feature", "Verdict"], BRONZE_SILVER)}
<p>SCD Type 2 in depth, AUTO CDC against your own MERGE: <a href="/learn/scd2-auto-cdc-vs-pyspark/">SCD Type 2: AUTO CDC or own PySpark</a>.</p></section>

<section id="s2g"><p class="eyebrow">5. Silver to gold</p><h2>Silver to gold: help with the edges only</h2>
<p>Gold's hard parts are business bookkeeping, which a declarative engine does not model. Use it for the graph and the aggregates; keep a harness for the facts. Why and how: <a href="/learn/silver-to-gold/">Silver to gold</a>.</p>
{vtable(["Gold need", "Declarative feature", "Verdict"], SILVER_GOLD)}</section>

<section id="fit"><p class="eyebrow">6. Together</p><h2>Declarative and a harness, together</h2><ol class="steps">{''.join(f'<li>{E(s)}</li>' for s in FIT)}</ol></section>

<section id="restrict"><p class="eyebrow">6b. Restrictions</p><h2>What declarative restricts</h2>
{C.table(["Restriction", "What happens", "What to do"], RESTRICT)}</section>

<section id="tested"><p class="eyebrow">6c. Tested</p><h2>What we tested (13 and 14 Nov 2026)</h2>
<p>A tiny change feed of order lines (insert, update, a late change with an older sequence, a delete) through a declarative flow that calls one of our own stage functions, with AUTO CDC writing SCD Type 2, as two triggered updates on Databricks Free Edition (serverless), then the same on a laptop with open-source Spark.</p>
{C.table(["Check", "Result"], TESTED)}</section>

<section id="decide"><p class="eyebrow">7. Decisions</p><h2>Decisions with verdicts</h2>{vtable(["Decision", "Choice", "Verdict"], DECISIONS)}</section>
<section id="open"><p class="eyebrow">8. Not settled yet</p><h2>What is not settled yet</h2>{C.table(["Question", "Where it stands"], OPEN)}</section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(QA)}</section>
<section id="next"><p class="eyebrow">Sources and related</p><h2>Sources and where it connects</h2>
<p>{' · '.join(f'<a href="{u}">{E(n)}</a>' for n, u in sources)}</p>
<p><a href="/learn/silver-to-gold/">Silver to gold</a> · <a href="/learn/gold-data-modelling/">Gold data modelling</a> · <a href="/learn/scd2-auto-cdc-vs-pyspark/">SCD Type 2 on Databricks</a> · <a href="/learn/data-platform-architecture/bronze-to-silver/">Hop 2: bronze to silver</a> · <a href="/data-engineering/">All data engineering</a></p></section>
</div>"""
    crumbs = [("Data engineering", f"{SITE}/data-engineering/"), ("Declarative pipelines", url)]
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": TITLE, "description": DESC, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in QA]}]
    head = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(TITLE, DESC, url, body, head)


def main():
    out = ROOT / "learn" / "spark-declarative-pipelines"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("declarative pipelines ->", out / "index.html")


if __name__ == "__main__":
    main()
