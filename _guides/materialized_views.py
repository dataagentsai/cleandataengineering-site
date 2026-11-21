"""Databricks materialized views, end to end: one page at /learn/materialized-views/.

    python3 _guides/materialized_views.py      (then python3 _site/nav.py and python3 _site/seo.py)

Body text lives in _guides/materialized_views/body.html (sections s1..s11); the drawings are built here.
Facts were read from docs.databricks.com/aws/en (incremental refresh, materialized views, CREATE and REFRESH syntax,
EXPLAIN CREATE MATERIALIZED VIEW, event log, billing system tables, serverless compute) on 21 Nov 2026.
Things the docs did not state are listed in the "Not confirmed" callout (s11); SQL marked "sketch" was not run.
"""
import json
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "_paths"))
import bi_choice as B  # noqa: E402  (drawing kit + CSS)
import components as C  # noqa: E402

wb = C.wb
SITE = wb.SITE
SLUG = "materialized-views"
BASE = f"/learn/{SLUG}/"
DATE = "2026-11-21"
BODY = Path(__file__).parent / "materialized_views" / "body.html"
bx, ar, svg, fig, t = B.bx, B.ar, B.svg, B.fig, B.t

TITLE = "Databricks materialized views: refresh types, cost, limits and how to avoid full refresh"
DESC = ("A complete guide to Databricks materialized views: where a refresh runs, incremental refresh vs full recompute, the refresh policies, "
        "what forces a full recompute, what it costs, tips, and how to find out which refresh really happened with EXPLAIN, the event log and system tables.")

QA = [
    ("Does a materialized view refresh incrementally?", "Only when the refresh runs on serverless compute, the query uses supported operations, the source tables allow it, and the cost model judges incremental cheaper than a full recompute. Otherwise Databricks recomputes everything."),
    ("How do I know whether a refresh was incremental or full?", "Query the pipeline event log for event_type = 'planning_information' (the message names the technique, for example ROW_BASED or FULL_RECOMPUTE), or look at the Incrementalization column in the UI. EXPLAIN CREATE MATERIALIZED VIEW tells you before you build whether the query can be incremental at all."),
    ("Can I stop a materialized view from silently doing a full recompute?", "Yes. Create it with REFRESH POLICY INCREMENTAL STRICT. If an incremental refresh is not possible, the refresh or create fails instead of recomputing everything."),
    ("What does a materialized view refresh cost?", "The docs say a refresh runs on serverless compute billed as serverless Lakeflow pipelines DBUs, and that cost scales with the volume of data processed, not with the size of your SQL warehouse. The docs I read give no price per DBU for it."),
]

RELATED = [
    ("Table, view, materialized view or metric view", "/learn/table-view-materialized-view-metric-view/"),
    ("Declarative pipelines", "/learn/spark-declarative-pipelines/"),
    ("Metric views: speed and materialization", "/learn/metric-views/performance/"),
    ("Databricks compute and cost", "/learn/databricks-compute/"),
    ("Who maintains your tables", "/learn/table-maintenance/"),
    ("Medallion architecture", "/learn/medallion-architecture/"),
]


def d_where():
    i = bx(10, 20, 250, 70, ["You, in a SQL warehouse", "(Pro or Serverless)", "CREATE / REFRESH statement"], "b", 15)
    i += bx(10, 130, 250, 70, ["Or: a Lakeflow pipeline", "you wrote (must be set", "to serverless)"], "b", 15)
    i += bx(340, 60, 300, 110, ["Backing pipeline", "type MV/ST, runs on", "serverless compute", "this is what you pay for"], "y", 16)
    i += bx(730, 60, 260, 110, ["The stored result", "a table in cloud storage", "that readers query fast"], "g", 16)
    i += ar(262, 55, 338, 100) + ar(262, 165, 338, 130) + ar(642, 115, 728, 115, label="writes", lx=685, ly=104)
    i += t(500, 235, "Cost follows the data the pipeline processes, not the size of the warehouse that sent the statement.", 15, "middle")
    i += t(500, 260, "If the pipeline is not serverless, every update is a full recompute.", 15, "middle")
    return svg(1000, 280, "Where a materialized view refresh runs. A SQL warehouse statement or a Lakeflow pipeline you wrote starts a backing serverless pipeline of type MV/ST, which writes the stored result table. You pay for the pipeline's serverless compute, not the warehouse size. Without serverless, every update is a full recompute.", i)


def d_engine():
    i = t(500, 22, "What happens on each refresh (AUTO policy)", 17, "middle")
    xs = [10, 250, 490, 730]
    qs = [["Serverless", "compute?"], ["Source data", "changed?"], ["Query can be", "incremental?"], ["Cost model says", "incremental is cheaper?"]]
    for k, (x, q) in enumerate(zip(xs, qs)):
        i += bx(x, 50, 190, 70, q, "w", 15)
        if k < 3:
            i += ar(x + 192, 85, xs[k + 1] - 2, 85, label="yes" if k != 1 else "yes", lx=x + 216, ly=76)
    i += bx(10, 200, 190, 56, ["Full recompute", "always"], "r", 15) + ar(105, 122, 105, 198, label="no", lx=124, ly=165)
    i += bx(250, 200, 190, 56, ["NO_OP", "nothing to do"], "g", 15) + ar(345, 122, 345, 198, label="no", lx=364, ly=165)
    i += bx(470, 200, 150, 56, ["Full recompute"], "r", 15) + ar(585, 122, 545, 198, label="no", lx=548, ly=165)
    i += bx(650, 200, 140, 56, ["Incremental"], "g", 15) + ar(800, 122, 720, 198, label="yes", lx=748, ly=165)
    i += bx(810, 200, 170, 56, ["Full recompute"], "r", 15) + ar(860, 122, 890, 198, label="no", lx=892, ly=165)
    i += t(500, 295, "Policy INCREMENTAL STRICT turns every red box into a failed refresh instead.", 15, "middle")
    return svg(1000, 312, "A decision chart for one refresh. If compute is not serverless the result is always a full recompute. If the source data has not changed nothing runs. If the query cannot be incremental it is a full recompute. Otherwise the cost model picks incremental or full. The INCREMENTAL STRICT policy turns every full recompute into a failed refresh.", i)


def render():
    url = f"{SITE}{BASE}"
    rel = " · ".join(f'<a href="{u}">{E(n)}</a>' for n, u in RELATED)
    body = f"""<div class="bi"><p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › Materialized views</p>
<p class="eyebrow" style="margin-top:22px">Databricks · tables and refresh</p>
<h1>{E(TITLE)}</h1><p class="lede">{E(DESC)}</p>
{BODY.read_text().replace("{{WHERE}}", fig(d_where(), "The statement starts a serverless pipeline, and the pipeline does the work and the billing.")).replace("{{ENGINE}}", fig(d_engine(), "One refresh, left to right. Red boxes are the full recomputes."))}
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(QA)}</section>
<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2><p>Related on this site: {rel}</p><p><a href="/data-engineering/">All data engineering</a> · <a href="/platforms/databricks/">Databricks on this site</a></p></section></div>"""
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": TITLE, "description": DESC, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in QA]}]
    head = B.CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(TITLE, DESC, url, body, head)


def build_all():
    return {f"learn/{SLUG}/index.html": render()}


def main():
    for rel, html in build_all().items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html)
        print("materialized views ->", path)


if __name__ == "__main__":
    main()
