"""Table, view, materialized view or metric view? One page at /learn/table-view-materialized-view-metric-view/.

    python3 _guides/table_view_choice.py      (then python3 _site/nav.py and python3 _site/seo.py)

Body text lives in _guides/table_view_choice/body.html (sections s1..s11); the three drawings are built here.
Example numbers were computed by running the SQL on a local SQL engine (sqlite) with the tiny tables shown on the page.
Databricks behaviour is written from the author's knowledge of the docs, not re-checked live; see the callout in s11.
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
SLUG = "table-view-materialized-view-metric-view"
BASE = f"/learn/{SLUG}/"
DATE = "2026-11-21"
BODY = Path(__file__).parent / "table_view_choice" / "body.html"
bx, ar, svg, fig, t = B.bx, B.ar, B.svg, B.fig, B.t

TITLE = "Table, view, materialized view or metric view: which one, and why"
DESC = ("A plain guide to the four ways to keep a business number on Databricks: a physical table, a normal view, a materialized view and a metric view. "
        "Worked examples for the grain problem, the same code copied into many places, fan-out joins, filtered variants, speed and security, with a decision chart and a verdict for each scenario.")

QA = [
    ("Can a normal view do what a metric view does?", "Only for the grouping you wrote into it. A normal view fixes its GROUP BY when you create it, so a different grouping needs another view or a query on the base table. A metric view keeps the formula and lets each question choose the grouping."),
    ("Is a materialized view the same as a metric view?", "No. A materialized view stores the result of one query so it reads fast. A metric view stores no data (unless you switch on materialization); it stores the definition of measures and dimensions so any grouping is computed correctly."),
    ("Should I replace my gold tables with metric views?", "No. Metric views sit on top of clean gold tables. The tables hold the data; the metric view holds the meaning."),
    ("When is a plain table the right answer?", "When the data must be written, updated or deleted by a pipeline, when many readers need it fast, or when you need row filters and column masks applied directly to the data."),
]

RELATED = [
    ("Metric views, taught from zero", "/learn/metric-views/"),
    ("Grain, fan-out and kinds of measure", "/learn/metric-views/granularity/"),
    ("Speed: materialization and pre-aggregation", "/learn/metric-views/performance/"),
    ("Row-level security with metric views", "/learn/metric-views/security/"),
    ("Medallion architecture", "/learn/medallion-architecture/"),
    ("Declarative pipelines", "/learn/spark-declarative-pipelines/"),
]


def d_four():
    i = ""
    cols = [(10, "Physical table", ["stored data", "a pipeline writes it", "reads are fast"], "g"),
            (260, "Normal view", ["a saved question", "runs again on every read", "grouping is fixed"], "b"),
            (510, "Materialized view", ["a saved answer", "stored, refreshed later", "grouping is fixed"], "y"),
            (760, "Metric view", ["a saved formula", "nothing stored by default", "grouping chosen per question"], "l")]
    for x, h, lines, f in cols:
        i += bx(x, 20, 230, 130, [h] + lines, f, 17)
    i += t(500, 190, "Table and materialized view store a result. View and metric view store a definition.", 15, "middle")
    i += t(500, 214, "Only the metric view lets each question choose how to group and still gets ratios right.", 15, "middle")
    return svg(1000, 230, "Four objects side by side. A physical table is stored data written by a pipeline. A normal view is a saved question that runs again on every read, with the grouping fixed. A materialized view is a saved answer that is stored and refreshed, with the grouping fixed. A metric view is a saved formula that stores nothing by default and lets each question choose the grouping.", i)


def d_copies():
    i = t(250, 24, "Before: the formula is copied", 17, "middle") + t(760, 24, "After: written once", 17, "middle")
    sql = [("Sales dashboard", "SUM(orders)/SUM(visits)", "8.0%"), ("Finance report", "AVG(orders/visits)", "10.0%"), ("Agent query", "forgot other channels", "6.3%")]
    for k, (who, how, num) in enumerate(sql):
        y = 44 + k * 86
        i += bx(10, y, 190, 60, [who, how], "r", 14)
        i += ar(202, y + 30, 330, y + 30)
        i += bx(332, y, 140, 60, ["shows " + num], "w", 15)
    i += bx(560, 90, 190, 100, ["Metric view", "conversion_rate =", "SUM(orders) / SUM(visits)"], "l", 15)
    for k, who in enumerate(["Sales dashboard", "Finance report", "Agent query"]):
        y = 44 + k * 86
        i += ar(752, 140, 820, y + 30)
        i += bx(822, y, 170, 60, [who, "shows 8.0%"], "g", 14)
    i += t(250, 306, "...and 7 more copies elsewhere: 10 places to keep in step", 14, "middle")
    i += t(500, 330, "Ten copies drift and give several numbers. One definition gives one.", 15, "middle")
    return svg(1000, 342, "Left: three of ten consumers each write their own formula for conversion rate and show 8.0, 10.0 and 6.3 percent. Right: one metric view holds the formula and all three consumers show the same 8.0 percent.", i)


def d_decide():
    i = bx(340, 6, 320, 46, ["Does a pipeline need to write,", "update or delete this data?"], "w", 14)
    i += ar(340, 29, 190, 74, label="yes", lx=250, ly=46) + bx(60, 76, 260, 50, ["Physical table"], "g", 17)
    i += ar(660, 29, 800, 74, label="no", lx=750, ly=46)
    i += bx(640, 76, 320, 50, ["Do people choose their own grouping,", "or do many tools need one formula?"], "w", 14)
    i += ar(800, 126, 800, 176, label="yes", lx=822, ly=156) + bx(660, 178, 280, 50, ["Metric view (on gold tables)"], "l", 16)
    i += ar(640, 101, 500, 176, label="no", lx=548, ly=132)
    i += bx(340, 178, 300, 50, ["One fixed question, read often", "and slow to compute?"], "w", 14)
    i += ar(340, 203, 200, 252, label="yes", lx=250, ly=222) + bx(60, 254, 260, 50, ["Materialized view"], "y", 17)
    i += ar(490, 228, 490, 280, label="no", lx=512, ly=258) + bx(360, 282, 260, 50, ["Normal view"], "b", 17)
    return svg(1000, 345, "A decision chart. If a pipeline must write, update or delete the data, use a physical table. Otherwise, if people choose their own grouping or many tools need one formula, use a metric view on gold tables. Otherwise, if one fixed question is read often and is slow, use a materialized view. Otherwise use a normal view.", i)


def render():
    url = f"{SITE}{BASE}"
    rel = " · ".join(f'<a href="{u}">{E(n)}</a>' for n, u in RELATED)
    body = f"""<div class="bi"><p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › Table, view, materialized view, metric view</p>
<p class="eyebrow" style="margin-top:22px">Data modelling · Databricks</p>
<h1>{E(TITLE)}</h1><p class="lede">{E(DESC)}</p>
{BODY.read_text().replace("{{FOUR}}", fig(d_four(), "Two of these store a result. Two store only a definition.")).replace("{{COPIES}}", fig(d_copies(), "The same formula written in three places drifts. Written once, it cannot.")).replace("{{DECIDE}}", fig(d_decide(), "Follow the questions from the top. The first yes wins."))}
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
        print("table-view-choice ->", path)


if __name__ == "__main__":
    main()
