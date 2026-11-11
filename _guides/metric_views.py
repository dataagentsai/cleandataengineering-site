"""Metric Views, taught from zero: a section of 10 pages under /learn/metric-views/.

    python3 _guides/metric_views.py      (then python3 _site/nav.py and python3 _site/seo.py)

Order (teach before design): the idea of a semantic model with no product in it; three products that
implement it (Unity Catalog metric views, the dbt Semantic Layer, the Power BI semantic model); limits of
each seen from eight seats; then metric views in depth (parts, grain, row-level security, speed,
production) and one example end to end, with the same model written in dbt and DAX.

Facts checked against docs.databricks.com/aws/en/uc-semantics/ and docs.getdbt.com on 11 Nov 2026.
Metric views change every few months; runtime and YAML minimums are in RUNTIME and must be re-checked.
The example SQL in EX_* was run on Databricks Free Edition when TESTED is set (see the example page).
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
BASE = "/learn/metric-views/"
DATE = "2026-11-11"
TESTED = ""  # set to a date string once the example has been run end to end on Databricks

bx, ar, svg, fig, t = B.bx, B.ar, B.svg, B.fig, B.t

CSS = B.CSS + """<style>
  .path { display:flex; flex-wrap:wrap; gap:8px; margin:16px 0 6px; }
  .path a { border:1.5px solid var(--ink); border-radius:999px; padding:3px 12px; background:#fff; color:var(--ink); text-decoration:none; font-size:14px; }
  .path a.on { background:var(--rose-wash); font-weight:700; }
  .bi .grid2 { display:grid; grid-template-columns:1fr 1fr; gap:14px; } @media (max-width:760px) { .bi .grid2 { grid-template-columns:1fr; } }
  .bi .card { border:var(--line); border-radius:var(--wob); padding:10px 16px; background:#fff; }
  .bi .card h3 { margin:4px 0 6px; } .bi .card.good { background:var(--mint-wash); } .bi .card.bad { background:var(--rose-wash); }
  .bi .steps { counter-reset:s; list-style:none; padding-left:0; } .bi .steps > li { counter-increment:s; border:var(--line); border-radius:var(--wob); padding:10px 16px 10px 52px; margin:10px 0; position:relative; background:#fff; }
  .bi .steps > li::before { content:counter(s); position:absolute; left:14px; top:9px; width:26px; height:26px; border:1.5px solid var(--ink); border-radius:50%; text-align:center; line-height:24px; font-family:var(--hand); background:var(--butter-wash); }
  .bi pre.code { font-family:var(--mono); font-size:12.5px; line-height:1.5; background:var(--surface-2); border:1px solid var(--rule); border-radius:8px; padding:12px 14px; overflow-x:auto; }
  .bi .cap { font-size:13px; color:var(--faint); margin:-8px 0 16px; }
  .bi .gloss dt { font-weight:700; margin-top:8px; } .bi .gloss dd { margin:2px 0 0 0; }
</style>"""

PAGES = [  # slug, short label, title, description
    ("", "Start here", "Metric views, taught from zero",
     "A learning section on semantic models and Databricks Unity Catalog metric views: the idea first, then metric views, dbt and Power BI side by side, limits, parts, grain, row-level security, speed, production and one example end to end."),
    ("semantic-model/", "1 · The idea", "What a semantic model is, before any product",
     "The semantic model with no product in it: ten parts every semantic layer has (grain, relationships, dimensions, measures, metrics, scope, access, business names, query interface, speed layer), drawn simply."),
    ("three-ways/", "2 · Three products", "One idea, three products: metric views, dbt, Power BI",
     "How Unity Catalog metric views, the dbt Semantic Layer (MetricFlow) and the Power BI semantic model each build the ten parts of a semantic model, with the same metric written in all three, and where Cube, LookML, Snowflake semantic views and Apache Ossie fit."),
    ("limits/", "3 · Limits", "Limits of each, seen from eight seats",
     "The limits of metric views, the dbt Semantic Layer and the Power BI semantic model from the seat of the author, business user, BI tool, AI agent, security, performance, cost and change, with a Pursue/Drop verdict for common setups."),
    ("anatomy/", "4 · Parts", "The parts of a metric view",
     "Every part of a Unity Catalog metric view: version, source, filter, joins (star, snowflake, one-to-many, rely), fields, measures, composed and window measures, parameters, agent metadata, materialization, MEASURE() queries, relationships, BI tools and runtime minimums."),
    ("granularity/", "5 · Grain", "Grain, fan-out and the kinds of measure",
     "Granularity for metric views: what grain means, fan-out and how one_to_many joins fix it, additive, semi-additive and non-additive measures, ratio of sums vs average of ratios, distinct counts, mixed grains and time grains."),
    ("security/", "6 · Row-level security", "Row-level security with metric views",
     "Where row-level security lives for metric views: row filters and column masks on gold tables driven by one entitlements table, whose identity applies, why a YAML filter is not security, why materialization is blocked, and how to test it."),
    ("performance/", "7 · Speed", "Speed: materialization, pre-aggregation and layout",
     "How a metric view query runs and what makes it fast: gold table layout, keys and rely, materialization (aggregated, unaggregated, exact, rollup and relaxed mode), pre-aggregation by grain, freshness, cost and how to check what was used."),
    ("production/", "8 · Production", "Metric views in production: challenges, anti-patterns, best practices",
     "Running Unity Catalog metric views in production: twelve challenges, fourteen anti-patterns with the fix, best practices, a release flow from git to certified, table-driven number tests and a review checklist."),
    ("example/", "9 · Example", "One example end to end: tyre sales to dealers",
     "A complete worked example: business questions, a gold star schema, an entitlements table and row filter, a metric view with composed, year-over-year and semi-additive measures, queries, materialization choices, dashboard and Genie, number tests, and the same model in dbt and Power BI DAX."),
]
LABEL = {s: lab for s, lab, _, _ in PAGES}


def path_nav(cur):
    return '<nav class="path" aria-label="Pages in this section">' + "".join(
        f'<a href="{BASE}{s}" class="{"on" if s == cur else ""}">{E(lab)}</a>' for s, lab, _, _ in PAGES) + "</nav>"


def sec(id_, eyebrow, h2, inner):
    return f'<section id="{id_}"><p class="eyebrow">{E(eyebrow)}</p><h2>{E(h2)}</h2>{inner}</section>'


def p(*xs):
    return "".join(f"<p>{x}</p>" for x in xs)


def ul(items, ordered=False):
    tag = "ol" if ordered else "ul"
    return f"<{tag}>" + "".join(f"<li>{x}</li>" for x in items) + f"</{tag}>"


def code(s, cap=""):
    return C.code(s, cap)


def vtable(head, rows):
    """Table whose last column is a verdict (bold)."""
    h = "".join(f"<th>{E(x)}</th>" for x in head)
    r = "".join("<tr>" + "".join(
        f'<td class="v">{E(c)}</td>' if i == len(row) - 1 else (f"<td><b>{E(c)}</b></td>" if i == 0 else f"<td>{E(c)}</td>")
        for i, c in enumerate(row)) + "</tr>" for row in rows)
    return f'<div class="tw"><table class="t"><tr>{h}</tr>{r}</table></div>'


def nextprev(cur):
    slugs = [s for s, *_ in PAGES]
    i = slugs.index(cur)
    out = '<p style="margin-top:28px">'
    if i > 0:
        out += f'← <a href="{BASE}{slugs[i - 1]}">{E(LABEL[slugs[i - 1]])}</a>'
    if i < len(slugs) - 1:
        out += f'{" · " if i > 0 else ""}Next: <a href="{BASE}{slugs[i + 1]}">{E(LABEL[slugs[i + 1]])}</a> →'
    return out + "</p>"


# =============================================================== drawings
def d_menu():
    i = bx(20, 70, 230, 150, ["The kitchen", "gold tables:", "invoice lines, dealers,", "products, dates"], "g")
    i += bx(370, 40, 260, 210, ["The menu", "= the semantic model", "'Net revenue'", "'Margin %'", "'by region, by month'", "one recipe per dish"], "y")
    for k, (lab, f) in enumerate([("Dashboard", "b"), ("Genie: questions in words", "b"), ("Excel / Power BI", "l"), ("An AI agent", "b")]):
        i += bx(750, 20 + k * 66, 230, 52, [lab], f)
        i += ar(630, 145, 748, 46 + k * 66)
    i += ar(250, 145, 368, 145, label="cooks from")
    i += t(500, 285, "Diners order from the menu. Nobody walks into the kitchen and cooks their own revenue.", 15, "middle")
    return svg(1000, 300, "A restaurant picture. The kitchen holds the gold tables. The menu is the semantic model: named dishes like net revenue and margin percent, each with one recipe, and the ways you can slice them. Diners, meaning dashboards, Genie, Excel or Power BI and AI agents, order from the menu instead of cooking from raw tables.", i)


PARTS = [
    ("1  Grain", "what one row means"), ("2  Relationships", "how tables join, one or many"),
    ("3  Dimensions", "ways to slice: region, month"), ("4  Measures", "sums and counts over rows"),
    ("5  Metrics", "built from measures: ratios, last year"), ("6  Scope", "what counts at all"),
    ("7  Access", "who sees which rows"), ("8  Business names", "labels, synonyms, formats, owner"),
    ("9  Query interface", "metric + slices in, SQL out"), ("10  Speed layer", "cache and pre-aggregates"),
]


def d_parts():
    i = bx(390, 150, 220, 90, ["the semantic", "model"], "y", 19)
    for k, (h, s) in enumerate(PARTS):
        col, row = k % 2, k // 2
        x = 20 if col == 0 else 690
        y = 12 + row * 76
        f = "g" if k < 2 else ("b" if k < 5 else ("r" if k < 7 else "l"))
        i += bx(x, y, 290, 60, [h, s], f, 16)
        i += ar(x + 290 if col == 0 else x, y + 30, 388 if col == 0 else 612, 195, True)
    i += t(500, 400, "green: the data's shape · blue: the numbers · rose: rules · lavender: how it is served", 13.5, "middle")
    return svg(1000, 410, "The ten parts of any semantic model around one box: grain, relationships, dimensions, measures, metrics, scope, access, business names, query interface and speed layer.", i)


def d_three():
    i = bx(330, 10, 340, 70, ["The idea: one semantic model", "(the ten parts)"], "y", 17)
    cols = [(20, "Unity Catalog metric view", ["YAML inside a view", "in Unity Catalog", "MEASURE() in SQL", "runs on Databricks"], "b"),
            (350, "dbt Semantic Layer", ["YAML in your dbt repo", "MetricFlow compiles", "metric + slices to SQL", "runs on your warehouse"], "g"),
            (680, "Power BI semantic model", ["tables + relationships", "+ DAX measures", "VertiPaq engine", "runs in Power BI / Fabric"], "l")]
    for x, h, lines, f in cols:
        i += ar(500, 80, x + 150, 118)
        i += bx(x, 120, 300, 150, [h] + lines, f, 17)
    i += t(500, 300, "Same ten parts. Different place, language and engine.", 15, "middle")
    return svg(1000, 310, "One idea, three products. The semantic model idea at the top points to a Unity Catalog metric view (YAML inside a view, MEASURE in SQL, runs on Databricks), the dbt Semantic Layer (YAML in the dbt repo, MetricFlow compiles to SQL on your warehouse) and the Power BI semantic model (tables, relationships, DAX measures on the VertiPaq engine in Power BI or Fabric).", i)


def d_anatomy():
    rows = [("version: 1.1", "which YAML spec", "w"), ("source: gold.fact_sales_line", "the grain: one row = one invoice line", "g"),
            ("filter: status <> 'CANCELLED'", "scope: what always counts", "r"), ("joins: dealer, product", "relationships to dimensions", "g"),
            ("fields: region, month, segment", "dimensions: ways to slice", "b"), ("measures: net_revenue, margin_pct", "aggregations, composed, windows", "b"),
            ("display_name / synonyms / format", "business names for people and Genie", "l"), ("materialization: (optional)", "speed layer: pre-aggregates", "y")]
    i = '<rect x="20" y="10" width="440" height="380" rx="10" fill="#fff" stroke="#111" stroke-width="1.5"/>'
    i += t(36, 34, "CREATE VIEW sales_mv WITH METRICS LANGUAGE YAML AS $$", 13)
    for k, (yaml, what, f) in enumerate(rows):
        y = 50 + k * 42
        i += bx(36, y, 408, 34, [yaml], f, 14)
        i += ar(446, y + 17, 528, y + 17)
        i += t(536, y + 22, what, 15)
    i += t(36, 386, "$$", 13)
    return svg(1000, 400, "The parts of a metric view, line by line: version, source (the grain), filter (scope), joins (relationships), fields (dimensions), measures, business metadata such as display names and synonyms, and optional materialization (the speed layer).", i)


def d_query_flow():
    i = bx(10, 40, 200, 90, ["SELECT region,", "MEASURE(margin_pct)", "... GROUP BY ALL"], "w", 14)
    i += bx(260, 40, 200, 90, ["Unity Catalog", "expands the measure", "and the joins"], "y")
    i += bx(510, 40, 220, 90, ["plain SQL on gold:", "SUM(...)/SUM(...)", "fact JOIN dealer"], "g")
    i += bx(780, 40, 200, 90, ["SQL warehouse", "(Photon) runs it", "as the user"], "b")
    i += ar(210, 85, 258, 85) + ar(460, 85, 508, 85) + ar(730, 85, 778, 85)
    i += bx(510, 190, 220, 80, ["materialized view", "(if one matches)"], "l", 15, True)
    i += ar(360, 130, 508, 230, True, "rewrite if it fits", 420, 205)
    i += ar(730, 230, 860, 132, True)
    i += t(500, 300, "No match: it reads the gold tables live. Match: it reads the pre-computed answer.", 14, "middle")
    return svg(1000, 310, "How a metric view query runs. A query with MEASURE goes to Unity Catalog, which expands the measure and the joins into plain SQL on the gold tables; a SQL warehouse runs it as the user. If a materialized view matches, the query is rewritten to read the pre-computed answer instead.", i)


def d_fanout():
    i = t(250, 26, "Order header joined to its 3 lines", 16, "middle")
    i += bx(30, 50, 160, 60, ["order 101", "freight = 100"], "y")
    for k in range(3):
        i += bx(300, 40 + k * 46, 160, 38, [f"line {k + 1}"], "g", 14)
        i += ar(190, 80, 298, 59 + k * 46)
    i += bx(60, 200, 380, 60, ["SUM(freight) after the join = 300", "the truth is 100"], "r", 16)
    i += t(750, 26, "The fix", 16, "middle")
    i += bx(560, 50, 380, 70, ["keep each measure at its own grain:", "freight lives on the header table"], "g", 15)
    i += bx(560, 140, 380, 70, ["metric view on headers, lines joined", "with cardinality: one_to_many"], "b", 15)
    i += bx(560, 230, 380, 50, ["SUM(freight) = 100, line counts still work"], "y", 15)
    return svg(1000, 290, "Fan-out. One order header with freight 100 joined to its three lines repeats the header three times, so summing freight gives 300 instead of 100. The fix: keep each measure at its own grain; put the metric view on headers and join lines as one_to_many, so freight sums to 100 and line counts still work.", i)


def d_additive():
    jars = [("Additive", "add across every slice", ["net revenue", "units sold", "line count"], "g"),
            ("Semi-additive", "add across some, not time", ["stock on hand", "account balance", "headcount"], "y"),
            ("Non-additive", "never add pieces", ["margin %", "distinct dealers", "median price"], "r")]
    i = ""
    for k, (h, s, ex, f) in enumerate(jars):
        x = 20 + k * 330
        i += f'<path d="M{x + 30},60 L{x + 50},250 L{x + 250},250 L{x + 270},60" fill="{B.FILLS[f]}" stroke="#111" stroke-width="1.5"/>'
        i += f'<ellipse cx="{x + 150}" cy="60" rx="120" ry="12" fill="#fff" stroke="#111" stroke-width="1.5"/>'
        i += t(x + 150, 30, h, 18, "middle") + t(x + 150, 100, s, 14, "middle")
        for j, e in enumerate(ex):
            i += t(x + 150, 140 + j * 30, e, 15, "middle")
    i += t(500, 285, "Know which jar a measure is in before you pre-aggregate it, or the numbers lie.", 15, "middle")
    return svg(1000, 295, "Three jars. Additive measures like net revenue, units and line count add across every slice. Semi-additive measures like stock on hand, balances and headcount add across some slices but not across time. Non-additive measures like margin percent, distinct dealers and median price never add from pieces.", i)


def d_rls():
    i = bx(10, 40, 170, 70, ["Asha, North", "manager"], "b")
    i += bx(10, 150, 170, 70, ["Ravi, all", "regions"], "b")
    i += bx(240, 90, 180, 80, ["sales_mv", "(metric view)"], "y")
    i += bx(480, 70, 220, 120, ["fact_sales_line", "row filter:", "region allowed", "for current_user()?"], "g", 15)
    i += bx(760, 20, 220, 70, ["entitlements table", "user → regions"], "r")
    i += bx(760, 150, 220, 70, ["Asha sees North rows", "Ravi sees every row"], "w")
    i += ar(180, 75, 238, 120) + ar(180, 185, 238, 145) + ar(420, 130, 478, 130)
    i += ar(700, 110, 758, 60, label="looks up", lx=720, ly=70) + ar(700, 160, 758, 185)
    i += bx(240, 240, 460, 50, ["materialization is refused while a row filter is on the source"], "r", 14, True)
    return svg(1000, 300, "Row-level security. Asha, a North manager, and Ravi, who sees all regions, both query the same metric view. The row filter on the gold fact table looks up the entitlements table for the current user, so Asha sees North rows and Ravi sees every row. Materialization is refused while a row filter is on the source.", i)


def d_grains():
    levels = [("invoice line", "millions of rows", "g"), ("day × dealer × product", "pre-aggregate A", "b"),
              ("day × region × segment", "pre-aggregate B", "b"), ("month × region", "what the dashboard shows", "y")]
    i = ""
    for k, (h, s, f) in enumerate(levels):
        w = 520 - k * 110
        x = 250 + (520 - w) / 2
        y = 230 - k * 66
        i += bx(x, y, w, 56, [h, s], f, 15)
    i += ar(820, 250, 820, 70, label="", lx=0, ly=0)
    i += t(838, 160, "roll up:", 14) + t(838, 180, "SUM, COUNT, MIN, MAX", 14) + t(838, 200, "work", 14)
    i += bx(20, 60, 200, 110, ["COUNT(DISTINCT dealer)", "cannot roll up:", "the same dealer sits", "in many days"], "r", 14)
    return svg(1000, 300, "A pyramid of grains. Invoice line at the bottom with millions of rows, then day by dealer by product, then day by region by segment, then month by region at the top, which is what the dashboard shows. Additive measures roll up from a finer pre-aggregate to a coarser one; distinct counts cannot, because the same dealer appears on many days.", i)


def d_release():
    steps = [("YAML in git", "one file per metric view", "w"), ("pull request", "review + lint", "y"), ("CI tests", "golden numbers, row counts", "g"),
             ("deploy", "ALTER VIEW by a", "b"), ("certify", "tag + owner + docs", "l"), ("watch", "query history, cost", "r")]
    i = ""
    for k, (h, s, f) in enumerate(steps):
        x = 10 + k * 165
        lines = [h, s] + (["service principal"] if h == "deploy" else [])
        i += bx(x, 60, 150, 90, lines, f, 15)
        if k < len(steps) - 1:
            i += ar(x + 150, 105, x + 163, 105)
    i += t(500, 190, "Nobody edits a production metric view in the UI. The file in git is the truth.", 15, "middle")
    return svg(1000, 200, "The release flow for a metric view: YAML in git, one file per metric view; a pull request with review and lint; CI tests with golden numbers and row counts; deploy with ALTER VIEW by a service principal; certify with tag, owner and docs; then watch query history and cost.", i)


def d_example():
    i = bx(10, 30, 170, 60, ["dim_dealer", "region, channel"], "g")
    i += bx(10, 110, 170, 60, ["dim_product", "segment, rim"], "g")
    i += bx(10, 190, 170, 60, ["fact_sales_line", "one row per line"], "g")
    i += bx(10, 270, 170, 60, ["fact_stock_daily", "one row per day"], "g")
    i += bx(240, 30, 180, 60, ["region_access", "who sees what"], "r")
    i += bx(470, 110, 200, 80, ["sales_mv", "revenue, margin %,", "year over year"], "y")
    i += bx(470, 240, 200, 70, ["stock_mv", "units on hand (last)"], "y")
    for k, lab in enumerate(["AI/BI dashboard", "Genie space", "Power BI", "agent tool"]):
        i += bx(780, 20 + k * 78, 200, 56, [lab], "b" if lab != "Power BI" else "l")
        i += ar(670, 150, 778, 48 + k * 78, True)
    i += ar(180, 60, 468, 130) + ar(180, 140, 468, 145) + ar(180, 220, 468, 165) + ar(180, 300, 468, 275)
    i += ar(330, 90, 330, 205, True, "row filter", 290, 160)
    i += ar(670, 275, 778, 270, True)
    return svg(1000, 340, "The worked example. Gold tables dim_dealer, dim_product, fact_sales_line and fact_stock_daily feed two metric views: sales_mv with revenue, margin percent and year over year, and stock_mv with units on hand. A region_access table drives the row filter on the fact table. An AI/BI dashboard, a Genie space, Power BI and an agent tool read the metric views.", i)


# =============================================================== page 0: start here
GLOSSARY = [
    ("Semantic model", "A layer of business meaning on top of tables: which numbers exist, how each is calculated, how tables join, and how you may slice them. Also called a semantic layer or metrics layer."),
    ("Metric view", "Databricks' product for a semantic model: a Unity Catalog object, written in YAML, that holds measures and dimensions and is queried with MEASURE()."),
    ("Grain", "What one row of a table means, such as one invoice line or one dealer per day."),
    ("Dimension (field)", "A way to slice a number: region, month, product segment. Metric views call them fields."),
    ("Measure", "An aggregation such as SUM(net_amount). It has no fixed grouping; the query decides it."),
    ("Composed measure", "A measure built from other measures, such as margin = gross margin / net revenue."),
    ("Fan-out", "When a join repeats rows, so sums come out too big."),
    ("Row-level security (RLS)", "Rules that decide which rows each person sees."),
    ("Materialization", "Pre-computed results that the engine reads instead of the raw tables when a query fits."),
    ("MetricFlow", "dbt's open-source engine that turns a metric request into SQL."),
    ("DAX", "Power BI's formula language for measures."),
]


def page_start():
    cards = "".join(f'<li><a href="{BASE}{s}"><b>{E(lab)}: {E(title)}</b></a><br>{E(desc.split(":")[0] if len(desc) > 180 else desc)}</li>' for s, lab, title, desc in PAGES[1:])
    gl = "".join(f"<dt>{E(a)}</dt><dd>{E(b)}</dd>" for a, b in GLOSSARY)
    body = f"""{p('''Ask three teams for "revenue last quarter" and you often get three numbers. Each team wrote its own SQL: one forgot returns, one counted cancelled orders, one joined a table that doubled rows. A <b>semantic model</b> fixes this by writing each business number once, with its recipe, and making every dashboard, spreadsheet and AI agent ask for the number by name.''',
'''This section teaches the idea first, with no product in it. Then it shows three products that build the idea, Databricks <b>metric views</b>, the <b>dbt Semantic Layer</b> and the <b>Power BI semantic model</b>, and where each falls short. Then it goes deep on metric views, and ends with one example built end to end.''')}
{fig(d_menu(), "The semantic model is the menu between the kitchen (tables) and the diners (tools and people).")}
<div class="box"><b>The short answer.</b> On a Databricks lakehouse, write business numbers once as Unity Catalog metric views over atomic gold tables; keep row-level security on the gold tables, driven by one entitlements table; keep YAML in git with number tests; make every tool, Genie and agents included, read the metric views. Use dbt's Semantic Layer when metrics must travel across several warehouses, and keep Power BI models thin readers rather than a second home for the same logic.</div>
{sec("path", "The path", "Ten pages, in this order", '<ol class="steps">' + cards + "</ol>")}
{sec("words", "Words used", "A small glossary", f'<dl class="gloss">{gl}</dl>')}
{sec("next", "Related", "Where it connects", p('<a href="/concepts/semantic-layer/">The semantic layer (key concept)</a> · <a href="/learn/power-bi-vs-databricks-ai-bi/">Power BI vs Databricks AI/BI</a> · <a href="/writing/genie-metric-views/">Genie and metric views</a> · <a href="/learn/data-platform-architecture/gold/">Gold: shaped for the business</a> · <a href="/data-engineering/">All data engineering</a>'))}"""
    qa = [("What is a Databricks metric view?", "A Unity Catalog object that defines business measures and dimensions once, in YAML, over a source table and its joins. You query it with SELECT field, MEASURE(measure) ... GROUP BY ALL, and Unity Catalog turns that into SQL on the source tables."),
          ("Is a metric view the same as a normal view?", "No. A normal view fixes the grouping when you create it. A metric view keeps measures unaggregated until query time, so the same measure can be grouped by any field the question needs."),
          ("Do I still need gold tables if I have metric views?", "Yes. Metric views sit on top of clean, atomic gold tables. They hold the meaning and the recipes, not the data cleaning.")]
    return body, qa


# =============================================================== page 1: the idea
PART_ROWS = [
    ("1  Grain", "What one row of each table means.", "Every number is computed from rows. If you don't know what a row is, you can't know what SUM means.", "Invoice line, not invoice."),
    ("2  Relationships", "How tables join, and whether each join is one-to-one, many-to-one or one-to-many.", "A wrong join repeats rows and inflates sums without any error.", "Each line has one dealer; a dealer has many lines."),
    ("3  Dimensions", "The ways a number can be sliced, including time at several grains and hierarchies.", "Business questions are 'X by Y': revenue by region by month.", "region, dealer, segment, invoice month"),
    ("4  Measures", "Aggregations over rows, without a fixed grouping.", "The grouping comes from the question, so one measure serves every report.", "SUM(net_amount)"),
    ("5  Metrics", "Numbers built from measures: ratios, differences, last year, running totals.", "Most arguments are about these, because they hide choices (ratio of sums or average of ratios?).", "margin % = gross margin / net revenue"),
    ("6  Scope", "Rules about what counts at all.", "Cancelled orders, test dealers and internal sales must never sneak in.", "status <> 'CANCELLED'"),
    ("7  Access", "Who may see which rows and columns.", "The same metric must give each person only their part.", "North managers see North."),
    ("8  Business names", "Labels, descriptions, synonyms, formats, owner, certified or not.", "People and AI find numbers by words, not column names.", "'zone' means region; show as ₹ with no decimals."),
    ("9  Query interface", "How a tool asks: metric + dimensions + filters in, an answer out.", "Tools stop writing their own SQL, so they can't get the recipe wrong.", "MEASURE(net_revenue) by region"),
    ("10  Speed layer", "Caches and pre-computed aggregates, used only when they give the same answer.", "Big tables and busy dashboards need answers in seconds.", "a daily-by-region aggregate"),
]

IDEA_POINTS = [
    "<b>It is a contract, not a report.</b> A report answers one question. A semantic model answers every question built from its parts, and promises that the same question always gets the same number.",
    "<b>It holds meaning, not data.</b> The data stays in tables. The model holds names, recipes and rules. Change a recipe once, and every tool sees the change.",
    "<b>It sits on clean, atomic data.</b> Feed it pre-summed tables and it can only slice what someone already summed. Feed it the finest grain any metric needs, and it can answer questions nobody planned.",
    "<b>Its users are tools.</b> Dashboards, spreadsheets, notebooks, Genie and agents ask it questions. That is why business names and synonyms are part of the model, not decoration.",
]


def page_idea():
    body = f"""{p('''Forget every product for a moment. A semantic model is a <b>written agreement about what business numbers mean</b>, kept in one place, in a form a machine can turn into a query. When a sales manager asks for "net revenue by region last month", the semantic model knows which table, which column, which join, which rows to leave out and which rows that manager may see.''')}
{fig(d_menu(), "Kitchen, menu, diners. The menu names each dish and holds the recipe; diners never cook from the raw ingredients.")}
{sec("why", "Why it exists", "The problem it solves", p('''Without one, every dashboard holds its own SQL. Over time the copies drift: one adds returns, one leaves out a dealer type, one joins a table that repeats rows. Then meetings start with "whose number is right?". With one, the recipe lives once, so the argument happens once, when the metric is defined, and never again in each meeting.''',
'''AI makes this sharper. A model writing SQL straight on raw tables guesses joins and filters, and guesses differently each time. A model that picks a named metric and named slices from a semantic model cannot invent a recipe. That is the main reason semantic models are back in fashion.'''))}
{sec("parts", "The parts", "Ten parts every semantic model has", fig(d_parts(), "The ten parts. Every product on the next page builds these, in its own words.") + C.table(["Part", "What it is", "Why it matters", "Example (tyre sales)"], PART_ROWS))}
{sec("ideas", "Four ideas to hold on to", "What makes a semantic model good", ul(IDEA_POINTS))}
{sec("concept", "Concept vs physical", "Keep the idea separate from the product", p('''The ten parts are the <b>concept</b>: the job and its logic. A metric view, a dbt semantic model or a Power BI dataset is the <b>physical</b> thing doing the job, like Java or Python doing the same algorithm. Learn the parts once and you can read any product: ask where it keeps the grain, how it declares joins, how it composes metrics, where access rules live and how tools ask it questions.'''))}
{nextprev("semantic-model/")}"""
    qa = [("What is the difference between a semantic model and a data model?", "A data model shapes the tables: facts, dimensions, keys. A semantic model sits on top and adds meaning: named measures and metrics, allowed slices, scope rules, access rules and business names, plus a way for tools to ask for them."),
          ("Is a semantic layer the same as a semantic model?", "In practice yes. 'Semantic layer' is the layer in the architecture; 'semantic model' is what you write in it. Some vendors also call it a metrics layer."),
          ("Why should gold tables be atomic under a semantic model?", "Because a semantic model can only slice what is in its source. If gold is already summed by month and region, nobody can ask by dealer or by day, and ratios computed before summing come out wrong.")]
    return body, qa


# =============================================================== page 2: three products
MAP_ROWS = [
    ("1  Grain", "source: one table, view or SQL query per metric view", "each dbt model with a semantic_model block; primary entity", "each table in the model; relationships set the direction"),
    ("2  Relationships", "joins: under the metric view (star, nested snowflake, one_to_many, rely); relationships between metric views (Beta)", "entities (primary, foreign, unique, natural); MetricFlow finds join paths at query time", "relationships drawn in the model, with cardinality and filter direction"),
    ("3  Dimensions", "fields: SQL expressions; time grains as separate fields", "dimensions: categorical and time, with granularity; time spine", "columns, hierarchies, a marked date table"),
    ("4  Measures", "measures: any SQL aggregate", "simple metrics with agg (sum, count, average, median ...)", "DAX measures (SUM, COUNTROWS ...)"),
    ("5  Metrics", "composed with MEASURE(other); window measures (trailing, cumulative, offset, semiadditive)", "ratio, derived, cumulative and conversion metrics; offset windows", "DAX: DIVIDE, CALCULATE, time intelligence; calculation groups"),
    ("6  Scope", "filter: at the top", "filter on a metric, or where on the model", "filters in measures or the model; RLS is not scope"),
    ("7  Access", "Unity Catalog grants; row filters and masks on source tables", "none of its own: the warehouse decides, as the identity the query runs under", "RLS and object-level security roles inside the model"),
    ("8  Business names", "comment, display_name, synonyms, format (agent metadata); UC tags and certification", "label, description, meta config", "display folders, descriptions, format strings, synonyms for Q&A/Copilot"),
    ("9  Query interface", "SQL with MEASURE(); dashboards, Genie, alerts, JDBC/ODBC", "Semantic Layer APIs (JDBC, GraphQL, SDK), dbt MCP server, partner tools; mf / dbt sl CLI", "Power BI reports, Excel, XMLA endpoint, DAX queries"),
    ("10  Speed layer", "materialization: managed materialized views with query rewrite", "caching and exports to tables (dbt platform)", "Import (VertiPaq in memory), aggregations, Direct Lake"),
]

OTHERS = [
    ("Cube (Cube Core, open source)", "A semantic layer server: YAML or JS models, SQL/REST/GraphQL APIs, pre-aggregations and row-level rules in the server. Works over many databases.", "Good when the data is not on one lakehouse, or for embedded analytics."),
    ("LookML (Looker)", "Looker's modeling language; also served to other tools through Looker's semantic layer connectors.", "Strong where Looker is already the BI tool."),
    ("Snowflake semantic views", "Snowflake's native object for metrics and dimensions, used by Cortex Analyst.", "Snowflake's equivalent of metric views."),
    ("Apache Ossie (incubating)", "Was Open Semantic Interchange (OSI), started by Snowflake in Sept 2025 with dbt Labs, Salesforce and others; joined the Apache Incubator in 2026; Databricks is listed among its 50+ backers. A neutral YAML format to move semantic models between tools.", "Watch it: a common file format would reduce lock-in for all three products here."),
]


def page_three():
    mv = """version: 1.1
source: main.sales_gold.fact_sales_line
filter: status <> 'CANCELLED'
joins:
  - name: dealer
    source: main.sales_gold.dim_dealer
    on: source.dealer_id = dealer.dealer_id
fields:
  - name: region
    expr: dealer.region
  - name: invoice_month
    expr: DATE_TRUNC('MONTH', invoice_date)
measures:
  - name: net_revenue
    expr: SUM(net_amount)
  - name: gross_margin
    expr: SUM(net_amount - cost_amount)
  - name: margin_pct
    expr: MEASURE(gross_margin) / NULLIF(MEASURE(net_revenue), 0)"""
    dbt = """models:
  - name: fact_sales_line
    semantic_model:
      enabled: true
    agg_time_dimension: invoice_date
    columns:
      - name: line_id
        entity: { type: primary, name: sales_line }
      - name: dealer_id
        entity: { type: foreign, name: dealer }
      - name: invoice_date
        granularity: day
        dimension: { type: time }
    metrics:
      - name: net_revenue
        type: simple
        agg: sum
        expr: net_amount
        filter: "{{ Dimension('sales_line__status') }} != 'CANCELLED'"
      - name: gross_margin
        type: simple
        agg: sum
        expr: net_amount - cost_amount

  - name: dim_dealer
    semantic_model:
      enabled: true
    columns:
      - name: dealer_id
        entity: { type: primary, name: dealer }
      - name: region
        dimension: { type: categorical }

metrics:
  - name: margin_pct
    type: ratio
    numerator: gross_margin
    denominator: net_revenue"""
    dax = """-- Power BI: tables fact_sales_line, dim_dealer, dim_date with relationships;
-- scope (no cancelled rows) is usually applied in the source view or Power Query.
Net Revenue  := SUM ( fact_sales_line[net_amount] )
Gross Margin := SUMX ( fact_sales_line, fact_sales_line[net_amount] - fact_sales_line[cost_amount] )
Margin %     := DIVIDE ( [Gross Margin], [Net Revenue] )"""
    ask = """-- Metric view: plain SQL
SELECT region, invoice_month, MEASURE(margin_pct) AS margin_pct
FROM main.sales_gold.sales_mv
GROUP BY ALL;

# dbt: a metric request, MetricFlow writes the SQL
mf query --metrics margin_pct --group-by dealer__region,metric_time__month   # open-source MetricFlow
dbt sl query --metrics margin_pct --group-by dealer__region,metric_time__month  # dbt platform

// Power BI: a DAX query (or simply drag Margin % onto a visual)
EVALUATE SUMMARIZECOLUMNS ( dim_dealer[region], dim_date[month], "Margin %", [Margin %] )"""
    body = f"""{p('''Three products, three homes. A <b>metric view</b> lives in the Databricks catalog. A <b>dbt semantic model</b> lives in your dbt project and compiles to SQL for whatever warehouse dbt runs on. A <b>Power BI semantic model</b> lives in Power BI or Fabric and runs on Power BI's own engine. All three build the same ten parts.''')}
{fig(d_three(), "Same idea, three places to keep it.")}
{sec("map", "Side by side", "How each product builds the ten parts", C.table(["Part", "Unity Catalog metric view", "dbt Semantic Layer (MetricFlow)", "Power BI semantic model"], MAP_ROWS))}
{sec("same", "The same metric, three times", "Net revenue and margin % in each language",
     "<h3>Metric view (YAML inside CREATE VIEW ... WITH METRICS)</h3>" + code(mv) +
     "<h3>dbt Semantic Layer (latest YAML spec, dbt 1.12+ or Fusion)</h3>" + code(dbt, "In the latest spec, simple metrics sit inside the model; ratio and derived metrics sit in a top-level metrics list. Older projects use separate semantic_models with measures and type_params; check the spec your dbt version runs.") +
     "<h3>Power BI (DAX)</h3>" + code(dax) +
     "<h3>Asking for it</h3>" + code(ask))}
{sec("feel", "How they feel", "The real difference in one paragraph each",
     '<div class="grid2"><div class="card"><h3>Metric view</h3><p>Lives where the data and the permissions already are. No extra server. Every Databricks surface (SQL, dashboards, Genie, alerts, notebooks) reads it natively, and Unity Catalog row filters apply. Outside Databricks, tools must send MEASURE() through custom SQL until their connectors learn it.</p></div>'
     '<div class="card"><h3>dbt Semantic Layer</h3><p>Lives in git next to the models that build the tables, and is warehouse-neutral. MetricFlow, the compiler, is open source (Apache 2.0) since Oct 2025; the serving parts (APIs, caching, MCP server for agents) need a paid dbt platform plan. It has no access rules of its own.</p></div>'
     '<div class="card"><h3>Power BI semantic model</h3><p>The richest calculation language (DAX) and a very fast in-memory engine. Business users already know it. But the logic lives inside Power BI/Fabric; Genie, agents and other tools can only reach it through XMLA or Power BI APIs, and an Import copy needs its own security.</p></div>'
     '<div class="card"><h3>The common pattern</h3><p>Keep one home for definitions and make the others thin readers. On a Databricks platform that home is the metric view; Power BI keeps a thin model whose measures match it one to one, checked by a test. See <a href="/learn/power-bi-vs-databricks-ai-bi/">Power BI vs Databricks AI/BI</a>.</p></div></div>')}
{sec("others", "Also on the map", "Other semantic layers worth knowing", C.table(["Product", "What it is", "When it fits"], OTHERS))}
{nextprev("three-ways/")}"""
    qa = [("Is MetricFlow open source?", "Yes. dbt Labs open-sourced MetricFlow under Apache 2.0 in October 2025. It compiles metric requests to SQL. Serving metrics to BI tools and agents through the Semantic Layer APIs, caching and the MCP server is part of the paid dbt platform."),
          ("Can Power BI read a Databricks metric view?", "Yes, with limits. Today you send MEASURE() through the Databricks connector's native query in DirectQuery mode, or read a wrapper view. Publishing a metric view as a Power BI semantic model is in Private Preview. Check the current Databricks BI tools page."),
          ("Which one should I pick?", "Where the data lives decides most of it. Databricks-centred: metric views. Several warehouses, or dbt already central: the dbt Semantic Layer. Power BI is the only consumer and data fits in Import: a Power BI model can be enough. Whatever you pick, keep definitions in one home.")]
    return body, qa


# =============================================================== page 3: limits
SEATS = [
    ("Author (who writes it)", "YAML plus SQL expressions; ALTER VIEW replaces the whole definition; only the owner edits; window measures need care with ordering and gaps.", "YAML plus Jinja filters; entity and time-spine concepts to learn; spec changed in 2026 (old and new formats in the wild).", "DAX is powerful but hard to review; models are binary files unless you use PBIP/TMDL folders."),
    ("Business user", "Sees friendly names, formats and synonyms in dashboards and Genie; needs a Databricks login.", "Reaches metrics only through a connected tool (Sheets, Excel, Tableau and others on the integrations list).", "Best experience: drag and drop in a tool they know; Excel via Analyze in Excel."),
    ("BI tool outside the platform", "Tools must send MEASURE() in custom SQL or read wrapper views; publish-to-Power-BI is Private Preview; partner native support is arriving.", "Partners integrate through the Semantic Layer APIs; the list is finite.", "Outside Microsoft tools, reach is through XMLA, which few non-Microsoft tools use well."),
    ("AI and agents", "Genie reads metric views natively; agent metadata (synonyms, display names) helps; agents call them through SQL tools or Genie API.", "dbt MCP server gives agents governed metrics (paid platform).", "Copilot in Power BI uses it; agents outside Microsoft reach it with effort."),
    ("Security", "Unity Catalog grants, row filters and masks on source tables apply as the user; no materialization while those filters exist.", "No RLS of its own; depends on the warehouse identity; a shared service account sees everything.", "RLS and OLS roles in the model; Import copies data out, so rules live twice if Databricks has them too."),
    ("Performance at scale", "Compiles to SQL on gold; speed comes from table layout, the warehouse and optional materialization; no query-time joins with other tables (use a CTE).", "Adds a hop (API → compile → warehouse); declarative caching and exports help.", "Import is very fast until model size, refresh time and capacity memory bite; DirectQuery depends on the source."),
    ("Cost", "No licence; you pay warehouse compute per query and pipeline compute for materialization.", "MetricFlow free; serving needs a dbt platform plan; plus warehouse compute.", "Per-user licences or Fabric capacity; refresh compute; Import duplicates storage."),
    ("Portability and change", "Databricks-only object (sharing across metastores is Beta); YAML features depend on runtime version; Apache Ossie may help later.", "Most portable: same YAML runs on several warehouses.", "Locked to Power BI/Fabric; TMDL and Git integration make change control possible."),
]

MV_LIMITS = [
    ("No SELECT *; every measure needs MEASURE() (or AGG on runtime 18.1+)", "BI tools that generate their own SQL can't use metric views without custom SQL or a compatibility mode."),
    ("No joins with other tables at query time", "Wrap the metric view query in a CTE, then join the result."),
    ("Materialization refused when the view or its sources use row filters, column masks or ABAC policies", "Secured data must be sped up some other way (layout, your own secured aggregate tables)."),
    ("Parameterized metric views can't be materialized", "Pick: flexibility or pre-computation."),
    ("at_most_one_match is a promise, not a check", "If the join is not truly many-to-one, sums are silently wrong."),
    ("Relationships between metric views are Beta, metadata only, not enforced, SQL only", "Tools choose join paths; treat them as hints."),
    ("ALTER VIEW replaces the whole YAML; DROP is permanent; owner-only edits", "Treat the YAML file in git as the source; deploy, don't hand-edit."),
    ("Wildcards expand at create time", "New columns in the source don't appear until you recreate the view."),
    ("Features are gated by runtime and YAML 1.1", "A warehouse or cluster on an older runtime may reject a view that works elsewhere."),
    ("No data profiling on metric views", "Profile the gold tables underneath instead."),
]

VERDICTS = [
    ("Data on Databricks; dashboards, Genie and agents on Databricks", "Metric views as the only home for definitions", "Pursue"),
    ("Same, plus Power BI for formal reports", "Metric views, plus a thin Power BI model whose measures match them, with a number test", "Pursue"),
    ("dbt builds gold; several warehouses or tools outside Databricks", "dbt Semantic Layer as the home; Databricks reads gold as normal tables", "Pursue"),
    ("Power BI is the only consumer, data fits in Import, no AI on top", "Power BI semantic model alone", "Pursue (small scope)"),
    ("Definitions written in both metric views and DAX by hand", "Two homes that drift", "Drop"),
    ("Metric views and dbt metrics both defined for the same numbers", "Two compilers, two truths", "Drop"),
    ("No semantic layer; each dashboard and Genie writes its own SQL on silver", "Fastest to start, slowest to trust", "Drop"),
]


def page_limits():
    body = f"""{p('''Every product has limits. What matters is which seat you sit in. A table that is fine for an author may be painful for a security reviewer. Below are the three products seen from eight seats, then the hard limits of metric views, then verdicts for common setups.''')}
{sec("seats", "Eight seats", "Limits seen from each seat", C.table(["Seat", "Metric view", "dbt Semantic Layer", "Power BI semantic model"], SEATS))}
{sec("mv", "Metric views", "Hard limits of metric views today, and what they mean", C.table(["Limit (from the Databricks docs, Nov 2026)", "What it means for you"], MV_LIMITS))}
<div class="warn"><b>Check before you design.</b> Metric views gained parameters, one-to-many joins, wildcards and relationships in 2026 alone. Anything here can change; the <a href="https://docs.databricks.com/aws/en/uc-semantics/metric-views/feature-availability">feature availability page</a> is the place to confirm.</div>
{sec("verdicts", "Choosing", "Common setups with a verdict", vtable(["Situation", "Setup", "Verdict"], VERDICTS))}
{nextprev("limits/")}"""
    qa = [("What is the biggest limit of metric views?", "Reach outside Databricks: tools must send MEASURE() through custom SQL until their connectors support metric views natively. Inside Databricks, the biggest design limit is that materialization is refused when source tables use row filters or masks."),
          ("What is the biggest limit of the dbt Semantic Layer?", "It has no access rules of its own and its serving layer (APIs, caching, MCP) is a paid dbt platform feature. The open-source MetricFlow only compiles SQL."),
          ("What is the biggest limit of a Power BI semantic model?", "Its logic is locked inside Power BI and Fabric. Genie, agents and non-Microsoft tools can't easily reuse DAX, and Import mode copies data, so security rules must be applied twice.")]
    return body, qa


# =============================================================== page 4: anatomy
PARTS_MV = [
    ("version", "Yes", "The YAML spec version (1.1 today), not your own revision number. 1.1 is needed for agent metadata, one-to-many joins, wildcards and window offsets."),
    ("comment", "No", "What the metric view is for. Shows in Catalog Explorer and helps Genie."),
    ("source", "Yes", "A table, view, materialized view, streaming table, another metric view, or a SQL query. Sets the grain."),
    ("filter", "No", "A boolean SQL expression applied to every query: scope, such as no cancelled orders."),
    ("joins", "No", "Star joins (name, source, on or using); nested joins for a snowflake; cardinality many_to_one (default) or one_to_many; rely.at_most_one_match."),
    ("fields (or dimensions)", "One of fields/measures", "Scalar SQL expressions to group and filter by. Can carry comment, display_name, format, synonyms (up to 10)."),
    ("measures", "One of fields/measures", "Aggregate expressions. Can reference other measures with MEASURE(). Can carry a window and the same metadata as fields."),
    ("parameters", "No", "Named, typed values passed at query time when the view is called like a table function. Blocks materialization."),
    ("materialization", "No", "Schedule, mode: relaxed, and a list of aggregated or unaggregated materialized views. A managed Lakeflow pipeline keeps them fresh."),
]

WINDOW_ROWS = [
    ("order", "The field that orders the window, usually a date field defined in the view. Must be deterministic."),
    ("range", "current, cumulative, trailing N unit, leading N unit, or all. trailing and leading exclude the anchor row unless you add inclusive."),
    ("semiadditive", "first or last (default last): what to return when the order field is not in the GROUP BY. This is how stock and balances work."),
    ("offset", "Shifts the frame, such as -12 month for last year. Needs YAML 1.1."),
]

RUNTIME = [
    ("Metric views", "16.4"), ("Temporary metric views", "17.2"), ("Materialization, snowflake joins, agent metadata (YAML 1.1), JDBC/ODBC", "17.3"),
    ("BI compatibility mode, REFRESH MATERIALIZED VIEW", "18.0"), ("Materialization refresh_policy", "18 LTS"),
    ("One-to-many joins, window offset, inclusive/exclusive, rely.at_most_one_match, AGG()", "18.1"),
    ("Parameters, wildcards", "18.2"), ("Relationships between metric views (Beta), numeric offsets, derived names", "19 (or a SQL warehouse)"),
]


def page_anatomy():
    create = """CREATE OR REPLACE VIEW main.sales_gold.sales_mv
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: "Tyre sales to dealers. One row per invoice line. Owner: Sales Finance."
source: main.sales_gold.fact_sales_line
filter: status <> 'CANCELLED'
joins:
  - name: dealer
    source: main.sales_gold.dim_dealer
    on: source.dealer_id = dealer.dealer_id
    rely:
      at_most_one_match: true        # a promise: dim_dealer has one row per dealer_id
  - name: product
    source: main.sales_gold.dim_product
    on: source.product_id = product.product_id
fields:
  - name: invoice_month
    expr: DATE_TRUNC('MONTH', invoice_date)
    display_name: Invoice month
  - name: region
    expr: dealer.region
    synonyms: ['zone', 'sales region']
  - name: segment
    expr: CASE product.segment WHEN 'PCR' THEN 'Passenger car' WHEN 'TBR' THEN 'Truck and bus' ELSE 'Two-wheeler' END
measures:
  - name: net_revenue
    expr: SUM(net_amount)
    display_name: Net revenue
    synonyms: ['revenue', 'sales']
  - name: gross_margin
    expr: SUM(net_amount - cost_amount)
  - name: margin_pct
    expr: MEASURE(gross_margin) / NULLIF(MEASURE(net_revenue), 0)
    display_name: Margin %
$$;"""
    query = """-- 1. Basic: fields plus MEASURE(), then GROUP BY ALL
SELECT region, invoice_month, MEASURE(net_revenue) AS revenue, MEASURE(margin_pct) AS margin
FROM main.sales_gold.sales_mv
WHERE invoice_month >= '2025-01-01'
GROUP BY ALL
ORDER BY region, invoice_month;

-- 2. Joining with another table: not allowed directly, so use a CTE
WITH m AS (
  SELECT region, MEASURE(net_revenue) AS revenue FROM main.sales_gold.sales_mv GROUP BY ALL
)
SELECT m.region, m.revenue, t.target_amount, m.revenue / t.target_amount AS attainment
FROM m JOIN main.sales_gold.region_target_2025 t USING (region);

-- 3. See the stored YAML and metadata
DESCRIBE TABLE EXTENDED main.sales_gold.sales_mv AS JSON;"""
    window = """measures:
  - name: net_revenue
    expr: SUM(net_amount)
  - name: net_revenue_ly                # same month last year
    expr: SUM(net_amount)
    window:
      - order: invoice_month
        range: current
        offset: -12 month
  - name: yoy_growth_pct
    expr: (MEASURE(net_revenue) - MEASURE(net_revenue_ly)) / NULLIF(MEASURE(net_revenue_ly), 0)
  - name: dealers_last_28_days          # distinct dealers in a trailing window
    expr: COUNT(DISTINCT dealer_id)
    window:
      - order: invoice_date
        range: trailing 28 day inclusive"""
    rel = """-- Relationships between metric views (Beta, runtime 19+ or a SQL warehouse):
-- metadata only, tells Genie and BI tools how two metric views fit together.
ALTER VIEW main.sales_gold.sales_mv
  ADD CONSTRAINT sales_to_dealer MANY TO ONE RELATIONSHIP TO main.sales_gold.dealer_mv
  USING (dealer_id);"""
    body = f"""{p('''A metric view is a view in Unity Catalog whose body is YAML instead of a SELECT. You create it with <code>CREATE VIEW ... WITH METRICS LANGUAGE YAML</code>, grant SELECT on it like any view, and query it with <code>MEASURE()</code>. Here is every part, mapped back to the ten parts of the idea.''')}
{fig(d_anatomy(), "Each YAML key is one of the ten parts of a semantic model.")}
{sec("keys", "Top-level keys", "What each key does", C.table(["Key", "Required", "What it does"], PARTS_MV))}
{sec("create", "Writing one", "A complete metric view", code(create, "Names with spaces need backticks in queries; quote any expression that contains a colon; use | for long multi-line expressions."))}
{sec("query", "Asking it questions", "How to query a metric view", code(query) + p("Measures are always wrapped in <code>MEASURE()</code>; fields are used like normal columns in SELECT, WHERE and GROUP BY. Under the hood Unity Catalog turns your query into plain SQL over the source and its joins.") + fig(d_query_flow(), "From a MEASURE() query to SQL on gold tables, or to a materialized answer."))}
{sec("composed", "Building on measures", "Composed and window measures", p("Write <b>atomic</b> measures first (one aggregation each), then <b>compose</b> them with <code>MEASURE(name)</code>, so a change to net revenue flows into margin and growth automatically. <b>Window measures</b> add time logic: trailing and leading windows, running totals, last year, and semi-additive balances.") + code(window) + C.table(["Window key", "What it does"], WINDOW_ROWS))}
{sec("meta", "For people and Genie", "Agent metadata", p("With YAML 1.1, fields and measures take <code>display_name</code> (up to 255 characters), <code>format</code> (currency, percent, number), <code>synonyms</code> (up to 10) and <code>comment</code>. Genie and dashboards use them to understand questions like 'sales by zone'. Unity Catalog tags and the certified status sit on the view itself, as on any table."))}
{sec("rel", "Several metric views", "Relationships between metric views (Beta)", code(rel) + p("One metric view per business process (sales lines, stock snapshots, targets) is cleaner than one giant view. Relationships tell tools how they connect through shared dimensions. They are not enforced and not used for query speed."))}
{sec("tools", "Outside Databricks", "How other tools read metric views", C.table(["Tool", "How, Nov 2026"], [
    ("AI/BI dashboards, Genie, alerts, SQL editor, notebooks", "Native."),
    ("Power BI", "Native query with MEASURE() in DirectQuery, or a wrapper view; publishing as a Power BI semantic model is Private Preview."),
    ("Tableau", "Custom SQL with MEASURE(), or BI compatibility mode set in Initial SQL."),
    ("Sigma, other JDBC/ODBC tools", "Custom or pass-through SQL with MEASURE()."),
    ("Wrapper views", "A normal view over the metric view with fixed dimensions; works everywhere, but you need one per dimension set.")]))}
{sec("runtime", "Versions", "Minimum Databricks Runtime per feature", C.table(["Feature", "Minimum runtime"], RUNTIME) + p("SQL warehouses get new features first. Check the current list before you rely on a feature on job clusters."))}
{nextprev("anatomy/")}"""
    qa = [("How do I query a metric view?", "SELECT the fields you want, wrap each measure in MEASURE(), and end with GROUP BY ALL. SELECT * is not allowed, and the metric view can't be joined to other tables directly; wrap it in a CTE first."),
          ("What is the difference between a field and a measure?", "A field is a scalar expression you group or filter by, like region or month. A measure is an aggregate, like SUM(net_amount), that is evaluated for whatever grouping the query asks for."),
          ("Can a measure use another measure?", "Yes. Write MEASURE(other_measure) inside the expression, for example MEASURE(gross_margin) / NULLIF(MEASURE(net_revenue), 0). This keeps each recipe in one place.")]
    return body, qa


# =============================================================== page 5: granularity
RATIO = [("North", "100", "10", "10%"), ("South", "900", "270", "30%"), ("Average of the two ratios", "", "", "20%  (wrong)"), ("Ratio of the sums", "1000", "280", "28%  (right)")]
KINDS = [
    ("Additive", "SUM, COUNT", "Any slice, any rollup", "Safe to pre-aggregate at any grain."),
    ("Semi-additive", "stock on hand, balances", "Across dealers yes, across days no", "Window measure with range: current and semiadditive: last."),
    ("Non-additive", "ratios, COUNT(DISTINCT), median, percentiles", "Never from pieces", "Compose ratios from additive parts; distinct counts can't roll up from pre-aggregates."),
]
MIXED = [
    ("Sales at invoice-line grain, targets at month × region", "Two metric views; join their results in a CTE (or declare a relationship for tools)", "Pursue"),
    ("Force targets onto the sales fact by repeating them on every line", "Targets get multiplied by the line count", "Drop"),
    ("Stock snapshots and sales in one metric view", "Different grains in one source; one of them fans out", "Drop"),
    ("Header amounts (freight) with line amounts", "Metric view on headers with lines as one_to_many, or allocate freight to lines in gold", "Pursue"),
]


def page_grain():
    stock = """version: 1.1
source: main.sales_gold.fact_stock_daily        # one row per dealer, product and day
fields:
  - name: snapshot_date
    expr: snapshot_date
  - name: region
    expr: region
measures:
  - name: units_on_hand
    expr: SUM(units_on_hand)
    window:
      - order: snapshot_date
        range: current
        semiadditive: last          # by month: the last day's stock, not the sum of 30 days"""
    o2m = """version: 1.1
source: main.sales_gold.fact_invoice_header     # one row per invoice
joins:
  - name: lines
    source: main.sales_gold.fact_sales_line
    on: lines.invoice_id = source.invoice_id
    cardinality: one_to_many                    # runtime 18.1+, YAML 1.1
measures:
  - name: freight
    expr: SUM(freight_amount)                   # counted once per invoice
  - name: line_count
    expr: COUNT(lines.line_no)                  # aggregated at the line grain"""
    body = f"""{p('''<b>Grain</b> is what one row means. It is the first question to ask about any metric view, because every measure is computed over those rows. Most wrong numbers in semantic models are grain mistakes: a join that repeats rows, an average of averages, or a distinct count added up from pieces.''')}
{sec("rule", "The rule", "The source grain is the finest slice any metric needs", p('''Pick the source of a metric view at the finest grain any of its metrics must be sliced by. If someone will ever ask "by product", the source can't be at region level. This is why gold should be <b>atomic</b> (one row per business event) and why pre-summed gold tables make bad sources: they answer only the questions someone already thought of.'''))}
{sec("fanout", "Silent wrong numbers", "Fan-out: when a join repeats rows", fig(d_fanout(), "Joining down to a finer table repeats the coarser rows.") + p('''Metric view joins are <b>many-to-one</b> by default: each source row should find at most one row in the joined table. If the joined table has duplicates (a dealer table with two rows for one dealer after an SCD2 change, say), you get wrong numbers with no error: either the sale rows repeat and sums inflate, or (for a many-to-many match, per the docs) the engine takes the first matching row, so the sale lands in an arbitrary slice. The docs say it plainly: if the join fans out, measures are wrong.''') + code(o2m, "When you do need the finer table, join it as one_to_many: the source rows are not repeated, and measures over the joined table are aggregated at their own grain. One-to-many columns can't be fields, and their materializations only match exactly (no rollup).") + p("<b>Guard it:</b> join dimensions on a key that is unique in gold (the current row of an SCD2 dimension, or the surrogate key), declare primary keys, and test uniqueness in CI. Only set <code>rely.at_most_one_match: true</code> when that test exists, because the flag is not checked."))}
{sec("kinds", "Three kinds of measure", "Additive, semi-additive, non-additive", fig(d_additive(), "Which jar a measure is in decides how it may be summed and pre-aggregated.") + C.table(["Kind", "Examples", "Adds across", "How to model it"], KINDS) + code(stock, "A semi-additive measure: summed across dealers on one day, but by month it returns the last day's value."))}
{sec("ratios", "The most common mistake", "Ratio of sums, not average of ratios", p("Margin % by region, then 'overall':") + C.table(["", "Net revenue", "Gross margin", "Margin %"], RATIO) + p("Averaging the two regional percentages gives 20%; the true company margin is 28%. Always define a ratio as <code>MEASURE(numerator) / MEASURE(denominator)</code> so the engine sums first and divides last, at whatever grain the query asks for. Never store a pre-computed percentage in gold and SUM or AVG it."))}
{sec("distinct", "Distinct counts", "Distinct counts don't add up", p("Active dealers in January plus active dealers in February is not active dealers in Q1: a dealer who bought both months is counted twice. COUNT(DISTINCT) must be computed from the atomic rows at the grain asked for. This is also why a materialized aggregate can answer a distinct count only on an exact match of its dimensions, never by rolling up."))}
{sec("mixed", "Different grains", "When metrics live at different grains", vtable(["Situation", "Setup", "Verdict"], MIXED))}
{sec("time", "Time grains", "Time is a dimension at several grains", ul([
    "Define date, week, month and quarter as separate fields (DATE_TRUNC), so users and Genie can pick a grain by name.",
    "Join a date dimension for fiscal periods, holidays and working days rather than computing them in each expression.",
    "Window measures order by a named field: define hierarchy levels on that field by name, not on the raw source column, or rollups go wrong.",
    "Gaps break trailing windows: a dealer with no sales in a week has no rows, so 'last 4 weeks' may reach back further than you think. Densify where it matters.",
    "For period-over-period on months, use month offsets (-12 month), not day offsets, so month lengths and leap years are handled.",
]))}
{nextprev("granularity/")}"""
    qa = [("What is fan-out in a metric view?", "A join where one source row matches several rows in the joined table, so the source row is repeated and sums and counts come out too big, with no error. Metric view joins assume many-to-one; use one_to_many cardinality when you really need the finer table."),
          ("How do I model stock or account balances?", "As a window measure with range: current and semiadditive: last ordered by the snapshot date. It sums across dealers on one day but returns the last day's value when you group by month."),
          ("Why is my overall margin different from the average of regional margins?", "Because the average of ratios is not the ratio of sums. Define margin as MEASURE(gross_margin) / MEASURE(net_revenue) so the engine sums before dividing.")]
    return body, qa


# =============================================================== page 6: security
WHERE_RLS = [
    ("Row filter on the gold table, driven by an entitlements table", "Applies to every reader of the table: metric views, SQL, dashboards, Genie, notebooks. One place to change who sees what.", "Pursue (default)"),
    ("ABAC policies (tag-based row filters and masks)", "Same idea at scale: tag columns once, write the policy once for many tables. Since 28 Apr 2026, ABAC policies on base tables behind views are evaluated as the session user.", "Pursue at scale"),
    ("filter: in the metric view YAML using current_user()", "Easy to bypass: anyone with SELECT on the gold table skips it; it is scope, not security; and it blocks materialization anyway.", "Drop"),
    ("One metric view per region (sales_north_mv, sales_south_mv ...)", "Copies multiply, definitions drift, Genie gets confused.", "Drop"),
    ("Dynamic views that hide rows with CASE on group membership", "The older pattern; works, but row filters are simpler and travel with the table.", "Only for legacy"),
]

RLS_TESTS = [
    ("North manager", "SELECT region, MEASURE(net_revenue) ... GROUP BY ALL", "Only North rows; North total equals the finance figure for North"),
    ("All-regions user", "Same query", "Every region; grand total equals finance's company total"),
    ("User with no entitlement row", "Same query", "Zero rows, not an error and not everything"),
    ("North manager via Genie", "'What was revenue by zone last month?'", "Only North, same number as the SQL"),
    ("North manager via Power BI DirectQuery with SSO", "Report page", "Only North (runs as the user)"),
    ("Power BI Import model", "Report page as a North user", "Only North because the Power BI role reads the same entitlements table"),
]


def page_security():
    ddl = """-- 1. One entitlements table: who may see which region. Owned by a security team.
CREATE TABLE main.security.region_access (user_email STRING, region STRING);
INSERT INTO main.security.region_access VALUES
  ('asha@example.com', 'North'),
  ('ravi@example.com', '*');                        -- '*' = every region

-- 2. A row filter function. It runs for every row the user reads.
CREATE OR REPLACE FUNCTION main.security.region_filter(p_region STRING)
RETURN EXISTS (
  SELECT 1 FROM main.security.region_access a
  WHERE a.user_email = current_user() AND (a.region = p_region OR a.region = '*')
);

-- 3. Attach it to the gold fact. Keep region ON the fact (copied from the dealer
--    in gold) so the filter needs no join per row.
ALTER TABLE main.sales_gold.fact_sales_line
  SET ROW FILTER main.security.region_filter ON (region);

-- 4. People only get SELECT on the metric view, not on the gold tables.
GRANT SELECT ON VIEW main.sales_gold.sales_mv TO `sales-managers`;"""
    mask = """-- A column mask: only finance sees cost, so gross margin is null for others.
CREATE OR REPLACE FUNCTION main.security.cost_mask(cost DECIMAL(18,2))
RETURN CASE WHEN is_account_group_member('finance') THEN cost ELSE NULL END;
ALTER TABLE main.sales_gold.fact_sales_line ALTER COLUMN cost_amount SET MASK main.security.cost_mask;"""
    body = f"""{p('''Row-level security (RLS) means the same metric gives each person only their part: Asha manages the North and sees North revenue; Ravi runs sales nationally and sees all of it. With metric views, the rule of thumb is short: <b>put RLS on the gold tables, not in the metric view</b>, and drive it from one entitlements table.''')}
{fig(d_rls(), "The rule lives on the table. Every path to the data, the metric view included, passes through it.")}
{sec("how", "How it works", "Whose identity applies", p('''A metric view is a view. As with any Unity Catalog view, <b>access to the base tables is checked as the view's owner</b>, which is why users need SELECT only on the metric view, not on the gold tables. But <b>row filters and column masks on those tables run with the person querying</b>: inside the filter function, <code>current_user()</code> and <code>is_account_group_member()</code> see the querying user. So one metric view, shared with everyone, returns different rows to different people.''',
'''Databricks made this explicit for tag-based (ABAC) policies: since 28 April 2026 they are evaluated as the session user for tables reached through views. Test it in your own workspace with two users before you go live (tests below).'''))}
{sec("build", "Building it", "Entitlements table, row filter, grant", code(ddl) + code(mask, "Masked columns flow into measures: a measure over a masked column returns null (or the masked value) for people outside the group."))}
{sec("where", "Where to put it", "Options with a verdict", vtable(["Where RLS lives", "What happens", "Verdict"], WHERE_RLS))}
{sec("conflict", "The trade-off", "Security blocks materialization", p('''Databricks refuses to materialize a metric view whose view or source tables use row filters, column masks or ABAC policies, and refuses invoker functions such as <code>current_user()</code> in materializations. The reason is sound: a materialization is computed once, as the owner, so it would hold everyone's rows. What to do instead:''') + ul([
    "Make the gold tables fast: liquid clustering on the filter columns (date, region), statistics, predictive optimization. Most dashboards are fast enough on a right-sized warehouse.",
    "Build your own aggregate table in gold (for example day × region × segment) in the pipeline, put the same row filter on it, and point a second metric view at it for the hot dashboards. It is small, so it is fast without materialization.",
    "Split data that needs no security (company-wide KPIs shown to everyone) into its own metric view, and materialize that one.",
]))}
{sec("powerbi", "Power BI too", "When Power BI copies the data", p('''Power BI DirectQuery with single sign-on runs as the user, so the Unity Catalog row filter applies. Import and Direct Lake copy the data out, so Power BI must apply its own role. Make that role read the <b>same entitlements table</b>, so there is still one list of who sees what. Details: <a href="/learn/power-bi-vs-databricks-ai-bi/#rls-both">RLS on both sides</a>.'''))}
{sec("test", "Prove it", "Security tests to run before go-live", C.table(["Who", "Asks", "Must see"], RLS_TESTS))}
{nextprev("security/")}"""
    qa = [("Where should row-level security live with metric views?", "On the gold tables, as Unity Catalog row filters (or ABAC policies) driven by one entitlements table. Every reader, including the metric view, then sees only allowed rows. Don't put security in the metric view's YAML filter."),
          ("Does a metric view run as the owner or as the user?", "Access to the base tables is checked as the owner, like any view, so users only need SELECT on the metric view. Row filters and column masks on those tables evaluate as the querying user, so current_user() inside them is the person asking."),
          ("Can I materialize a metric view that has row-level security?", "No. Databricks refuses materialization when the view or its sources use row filters, column masks or ABAC policies, because a materialization is computed once as the owner. Speed it up with table layout or your own secured aggregate table instead.")]
    return body, qa


# =============================================================== page 7: performance
LEVERS = [
    ("1  Gold layout", "Liquid clustering on the columns queries filter by (date, region); predictive optimization for OPTIMIZE and statistics; no small files.", "Always. Cheapest and helps every reader, not just metric views."),
    ("2  Keys and rely", "Primary and foreign keys with RELY on gold; rely.at_most_one_match on joins that are truly many-to-one, so the optimizer can skip joins a query doesn't need.", "When joins are proven unique by a test."),
    ("3  Right warehouse", "Serverless SQL warehouse sized for the dashboard's concurrency; the result cache answers repeated identical queries.", "Before any pre-aggregation."),
    ("4  Fewer, bigger questions", "Dashboards that ask one query per tile at a sensible grain, instead of pulling line-level rows into the tool.", "Always."),
    ("5  Materialization", "Aggregated materialized views for the hot slices; one unaggregated one for heavy joins. Built and refreshed by a managed pipeline.", "When the same slices are asked often, data is not secured by row filters, and steps 1–4 are not enough."),
    ("6  Own aggregate tables", "A day × region aggregate built in the gold pipeline, with its own row filter, and a metric view over it.", "When secured data still needs speed."),
]
MATCH = [
    ("Exact match", "The query's GROUP BY equals the materialization's dimensions, and its measures are a subset.", "Any measure, distinct counts included."),
    ("Rollup match", "The query asks for a coarser grain than was materialized (month from day).", "Only additive measures: SUM, COUNT, MIN, MAX. Not with one-to-many joins."),
    ("Unaggregated match", "Falls back to the unaggregated materialization (the joined, filtered rows).", "Anything, but less saving."),
    ("No match", "Reads the source tables live.", "Always correct, slowest."),
]
PREAGG = [
    ("Daily sales by region and segment, shown on the CEO dashboard 500 times a day, no RLS", "Aggregated materialization at day × region × segment; month queries roll up", "Pursue"),
    ("Distinct dealers by month", "Its own aggregated entry at exactly month × region; it can't roll up from days", "Pursue"),
    ("Materialize every dimension combination 'just in case'", "Pipeline cost and refresh time for slices nobody asks", "Drop"),
    ("Secured sales data (row filter on the fact)", "Not allowed; use layout or an own aggregate table with the same filter", "Use the alternative"),
    ("Parameterized metric view", "Can't be materialized", "Drop the parameter or skip materialization"),
    ("Data refreshed once a night, dashboards read by day", "Schedule the materialization right after the gold load so live and materialized answers agree", "Pursue"),
]


def page_perf():
    mat = """materialization:
  schedule: every 1 hour              # or a CRON; no schedule = manual refresh only
  mode: relaxed                       # the only mode: rewrite checks fields, not freshness
  materialized_views:
    - name: day_region_segment
      type: aggregated
      dimensions: [invoice_date, region, segment]
      measures: [net_revenue, gross_margin, units]
      cluster_by:
        cols: [invoice_date, region]
    - name: month_region_dealers       # distinct counts need their own exact grain
      type: aggregated
      dimensions: [invoice_month, region]
      measures: [active_dealers]
    - name: baseline                   # the joined, filtered rows; at most one
      type: unaggregated
      refresh_policy: incremental      # fails at create time if incremental isn't possible"""
    check = """-- Did my query use a materialization? The leaf node names it if so.
EXPLAIN EXTENDED
SELECT invoice_month, region, MEASURE(net_revenue) FROM main.sales_gold.sales_mv GROUP BY ALL;

-- Refresh by hand (for example right after the nightly gold load)
REFRESH MATERIALIZED VIEW main.sales_gold.sales_mv;"""
    body = f"""{p('''A metric view stores no data. Every query is turned into SQL over the gold tables and run on the warehouse. So speed comes, in order, from the tables underneath, the warehouse, and only then from pre-computed answers. Reach for materialization last, not first.''')}
{fig(d_query_flow(), "Two roads: live SQL on gold, or a rewrite to a materialized answer.")}
{sec("levers", "In order", "Six levers, cheapest first", C.table(["Lever", "What it is", "When"], LEVERS))}
{sec("mat", "Materialization", "How materialization works", p('''Add a <code>materialization</code> block and Databricks creates a managed Lakeflow pipeline that builds and refreshes materialized views (serverless compute must be on; runtime 17.3+). At query time the optimizer tries, in order, an exact match, a rollup match, the unaggregated match, and finally the live source tables.''') + code(mat) + C.table(["Match", "When it happens", "Which measures"], MATCH))}
{sec("fresh", "The catch", "Relaxed mode and freshness", p('''In <b>relaxed</b> mode the rewrite only checks that a materialization has the right fields and measures. It does <b>not</b> check freshness, session settings (time zone, ANSI mode) or determinism. So a query that matches reads the last refresh, while a query that doesn't match reads live data, and the two can disagree for a while. Schedule refreshes right after the gold load (or trigger them from it) so both roads give the same answer.''') + code(check))}
{sec("grain", "Pre-aggregation", "Pick the grain of each pre-aggregate", fig(d_grains(), "Pre-aggregate at the finest grain the hot dashboards need; coarser questions roll up from it.") + vtable(["Situation", "What to do", "Verdict"], PREAGG))}
{sec("limits", "Limits", "What can't be materialized", ul([
    "Metric views with parameters.",
    "Metric views whose view or source tables use row filters, column masks or ABAC policies; invoker functions like current_user() are refused too.",
    "Group-owned metric views (materialized ones need a single owner, and the owner can't change after materialization exists).",
    "TRIGGER ON UPDATE schedules.",
    "Rollup across one-to-many joins (exact match only).",
]) + p("<b>Cost:</b> refreshes are billed as Lakeflow pipeline usage and inherit the custom tags of the SQL warehouse that ran the statement; tag warehouses so the cost lands on the right team. See the <a href=\"/learn/data-systems/platform/cost/calculator/\">Databricks cost calculator</a>."))}
{nextprev("performance/")}"""
    qa = [("Do metric views store data?", "No. They store the definition. Each query is compiled into SQL on the source tables, unless a materialization matches, in which case it reads the pre-computed result."),
          ("How do I know if a query used a materialization?", "Run EXPLAIN EXTENDED on the query: the leaf node names the materialization if one was used. The query profile also shows a metric view materialization match insight."),
          ("Can a COUNT(DISTINCT) measure use a materialization?", "Only with an exact match: the query must group by exactly the materialization's dimensions. Distinct counts can't roll up from a finer pre-aggregate.")]
    return body, qa


# =============================================================== page 8: production
CHALLENGES = [
    ("Definition drift", "The same KPI is redefined in a dashboard, a notebook and Power BI.", "One home (metric views), thin readers, a same-number test against Power BI."),
    ("Silent fan-out", "A dimension gains duplicate keys after an SCD2 change; revenue doubles for some dealers.", "Uniqueness tests on every join key in CI; join on current rows; never set at_most_one_match without the test."),
    ("Mixed grains", "Targets, stock and sales forced into one view.", "One metric view per business process; CTE joins or relationships between them."),
    ("Freshness disagreement", "Materialized and live answers differ after a load.", "Refresh right after the gold load; show 'data as of' on dashboards."),
    ("Security vs speed", "Row filters block materialization.", "Layout first; secured own-aggregate tables for hot paths."),
    ("Tool reach", "A BI tool can't send MEASURE().", "Native query/custom SQL; wrapper views for the few fixed shapes; watch partner support."),
    ("Breaking changes", "A measure is renamed and three dashboards and a Genie space break.", "Treat names as an API: add new, deprecate old, remove later; lineage before every change."),
    ("Runtime differences", "A YAML 1.1 feature works on the SQL warehouse but fails on a job cluster on an older runtime.", "Pin the minimum runtime per feature; test on every compute that reads the view."),
    ("Ownership", "One engineer owns the view and leaves; only the owner can edit.", "Owner = a service principal (or group, if not materialized); deploy from CI."),
    ("Genie quality", "Genie picks the wrong measure for 'sales'.", "Synonyms, display names and comments; Genie benchmarks with known answers."),
    ("Cost surprises", "Materialization pipelines refresh hourly for slices nobody reads.", "Query history review monthly; drop unused materializations; tag warehouses."),
    ("Accidental drop", "DROP VIEW is permanent.", "Restricted MANAGE rights; re-create from git; lineage check first."),
]
ANTI = [
    ("A metric view per dashboard", "One per business process, shared by every dashboard."),
    ("Business logic copied into DAX or the BI tool", "Thin readers; measures match the metric view one to one."),
    ("Source is silver", "Source is atomic gold, tested, with keys."),
    ("Source is a pre-summed gold table", "Atomic source; pre-aggregation is a speed layer, not the model."),
    ("Stored percentages summed or averaged", "Ratios composed from additive measures."),
    ("Distinct counts added across periods", "COUNT(DISTINCT) at the asked grain; exact-match materialization only."),
    ("YAML filter used as security", "Row filters / ABAC on gold, entitlements table."),
    ("at_most_one_match set without a uniqueness test", "Test first, then declare."),
    ("Editing the production view in the UI", "YAML in git, deploy from CI by a service principal."),
    ("One giant metric view with every table joined", "Small views per process; relationships for navigation."),
    ("Cryptic names (amt_net_v2, rgn)", "Business names, display names, synonyms, comments."),
    ("Materialize everything", "Materialize the measured hot slices only."),
    ("Wildcards in production views", "Explicit fields; wildcards are fixed at create time and carry no metadata."),
    ("No tests because 'it is only YAML'", "Golden-number tests, uniqueness tests, RLS tests in CI."),
]
BEST = [
    "<b>Metrics first.</b> Write the metric list (name, definition, owner, grain, slices) with the business before building gold; build gold to serve it.",
    "<b>One metric view per business process</b> (sales lines, stock snapshots, targets), each at its natural grain.",
    "<b>Atomic measures, then composed ones</b>, all through MEASURE(), so each recipe lives once.",
    "<b>Scope in the filter</b> (no cancelled, no test dealers) so nobody can forget it.",
    "<b>Names for humans and Genie:</b> display_name, format, synonyms, comment on every field and measure.",
    "<b>Security on gold</b>, driven by one entitlements table; SELECT granted only on metric views.",
    "<b>Git, CI, service principal:</b> the YAML file is the truth; ALTER VIEW replaces the whole definition, so deploy the whole file.",
    "<b>Tests:</b> golden numbers, join uniqueness, RLS per persona, same number in every tool.",
    "<b>Certify</b> with Unity Catalog tags and an owner; uncertified views are drafts.",
    "<b>Measure, then materialize:</b> look at query history, pre-aggregate only the hot slices, align refresh to loads.",
    "<b>Names are an API:</b> version changes, deprecate before removing, check lineage first.",
]
CHECKLIST = [
    "Is the source atomic gold at the finest grain any measure needs?",
    "Is every join key unique in the joined table, and is that tested?",
    "Are ratios composed from additive measures, never stored percentages?",
    "Are semi-additive measures windowed with semiadditive: last?",
    "Is scope in the filter, and security on the gold tables?",
    "Does every field and measure have a business name, comment and (where useful) synonyms?",
    "Do golden-number tests pass, and does each persona see only their rows?",
    "Is the YAML in git, deployed by a service principal, on a runtime that supports every feature used?",
    "Is it certified, with a named business owner?",
    "Is materialization (if any) justified by query history and aligned with the load?",
]


def page_prod():
    deploy = """# deploy_metric_views.py  — run by CI with a service principal.
# Reads every metric_views/*.yaml file and (re)creates the view with the whole YAML.
import pathlib
from databricks import sql   # databricks-sql-connector

def ddl(name: str, yaml_text: str) -> str:
    return f"CREATE OR REPLACE VIEW {name} WITH METRICS LANGUAGE YAML AS $$\\n{yaml_text}\\n$$"

with sql.connect(server_hostname=HOST, http_path=WAREHOUSE_PATH, access_token=TOKEN) as c, c.cursor() as cur:
    for f in sorted(pathlib.Path("metric_views").glob("*.yaml")):
        cur.execute(ddl(f"main.sales_gold.{f.stem}", f.read_text()))
        cur.execute(f"ALTER VIEW main.sales_gold.{f.stem} SET TAGS ('certified' = 'true', 'owner' = 'sales-finance')")"""
    tests = """# test_metric_views.py — table-driven golden-number tests (pytest).
# Each row: a question, the metric-view query, the number finance signed off.
import pytest

CASES = [
    # name,                          query,                                                                                   expected
    ("revenue_2025_total",           "SELECT MEASURE(net_revenue) FROM main.sales_gold.sales_mv WHERE year(invoice_month)=2025", 1_234_500.00),
    ("revenue_north_jan_2025",       "SELECT MEASURE(net_revenue) FROM main.sales_gold.sales_mv WHERE region='North' AND invoice_month='2025-01-01'", 98_400.00),
    ("margin_pct_2025",              "SELECT MEASURE(margin_pct) FROM main.sales_gold.sales_mv WHERE year(invoice_month)=2025", 0.2810),
    ("cancelled_never_counted",      "SELECT MEASURE(net_revenue) FROM main.sales_gold.sales_mv WHERE invoice_id='INV-CANCELLED-1'", None),
]

@pytest.mark.parametrize("name,query,expected", CASES, ids=[c[0] for c in CASES])
def test_golden_number(cursor, name, query, expected):
    got = cursor.execute(query).fetchone()[0]
    if expected is None:
        assert got is None
    else:
        assert got == pytest.approx(expected, rel=1e-6)

# Join keys must be unique, or measures fan out silently.
UNIQUE_KEYS = [("main.sales_gold.dim_dealer", "dealer_id"), ("main.sales_gold.dim_product", "product_id")]

@pytest.mark.parametrize("table,key", UNIQUE_KEYS)
def test_join_key_unique(cursor, table, key):
    dupes = cursor.execute(f"SELECT COUNT(*) FROM (SELECT {key} FROM {table} GROUP BY {key} HAVING COUNT(*) > 1)").fetchone()[0]
    assert dupes == 0"""
    body = f"""{p('''Writing a metric view takes an afternoon. Keeping a few dozen of them right for years, with many teams, tools and Genie spaces reading them, is the real work. This page collects what goes wrong, the patterns to avoid, and how to run them.''')}
{sec("challenges", "Twelve challenges", "Production challenges and how to handle them", C.table(["Challenge", "What it looks like", "How to handle it"], CHALLENGES))}
{sec("anti", "Anti-patterns", "Fourteen anti-patterns, and the fix", '<div class="tw"><table class="t"><tr><th>Don\'t</th><th>Do</th></tr>' + "".join(f"<tr><td>{E(a)}</td><td>{E(b)}</td></tr>" for a, b in ANTI) + "</table></div>")}
{sec("best", "Best practices", "What good looks like", ul(BEST, True))}
{sec("release", "Release flow", "From a YAML file to a certified metric", fig(d_release(), "The release flow. The YAML file in git is the truth.") + code(deploy, "Deploy the whole file every time: ALTER VIEW and CREATE OR REPLACE replace the whole definition. Upgrading to YAML 1.1 with ALTER VIEW drops Unity Catalog comments unless they are in the YAML comment fields."))}
{sec("tests", "Tests", "Number tests, table-driven", p("Golden numbers are figures the business has signed off. Run them on every change, against a test copy of gold with fixed data (a clone or seeded tables), so a recipe change that moves a number fails the build instead of a board meeting.") + code(tests) + p("Add the RLS persona tests from the <a href=\"" + BASE + "security/#test\">security page</a> and a Power BI same-number test if Power BI reads the same metrics."))}
{sec("check", "Review checklist", "Ten questions before a metric view is certified", ul([E(x) for x in CHECKLIST], True))}
{nextprev("production/")}"""
    qa = [("How should metric views be deployed?", "Keep each metric view's YAML in git, review it in a pull request, run number and uniqueness tests in CI, and deploy the whole file with CREATE OR REPLACE VIEW ... WITH METRICS by a service principal. Never hand-edit the production view in the UI."),
          ("How do I test a metric view?", "Table-driven golden-number tests (query, expected figure signed off by the business) on fixed test data, uniqueness tests on every join key, and row-level security tests per persona."),
          ("Should I build one big metric view for everything?", "No. Build one per business process at its natural grain (sales lines, stock snapshots, targets) and connect them through shared dimensions, CTE joins or relationships.")]
    return body, qa


# =============================================================== page 9: example
EX_QUESTIONS = [
    ("Net revenue by region and month", "net_revenue", "region, invoice_month"),
    ("Margin % by segment", "margin_pct", "segment"),
    ("Growth on the same month last year", "yoy_growth_pct", "invoice_month (+ region)"),
    ("Active dealers in a month", "active_dealers", "invoice_month, region"),
    ("Average invoice value", "avg_invoice_value", "any"),
    ("Units on hand at month end", "units_on_hand", "snapshot_month, region"),
]

EX_GOLD = """-- Gold, atomic, one row per business event. Catalog 'main' (on Free Edition use 'workspace').
CREATE SCHEMA IF NOT EXISTS main.sales_gold;

CREATE OR REPLACE TABLE main.sales_gold.dim_dealer (
  dealer_id STRING NOT NULL, dealer_name STRING, city STRING, region STRING, channel STRING,
  CONSTRAINT pk_dealer PRIMARY KEY (dealer_id) RELY);
INSERT INTO main.sales_gold.dim_dealer VALUES
  ('D1','Sharma Tyres','Delhi','North','Retail'),
  ('D2','Punjab Wheels','Ludhiana','North','Fleet'),
  ('D3','Chennai Treads','Chennai','South','Retail');

CREATE OR REPLACE TABLE main.sales_gold.dim_product (
  product_id STRING NOT NULL, sku STRING, segment STRING, rim_inches INT,
  CONSTRAINT pk_product PRIMARY KEY (product_id) RELY);
INSERT INTO main.sales_gold.dim_product VALUES
  ('P1','PCR-185-15','PCR',15), ('P2','TBR-295-22','TBR',22), ('P3','2W-90-17','2W',17);

-- One row per invoice line. region is copied from the dealer in gold so the
-- row filter needs no join. Returns are negative lines.
CREATE OR REPLACE TABLE main.sales_gold.fact_sales_line (
  invoice_id STRING, line_no INT, invoice_date DATE, dealer_id STRING, region STRING,
  product_id STRING, qty INT, net_amount DECIMAL(18,2), cost_amount DECIMAL(18,2), status STRING)
CLUSTER BY (invoice_date, region);
INSERT INTO main.sales_gold.fact_sales_line VALUES
  ('I-001',1,'2024-01-10','D1','North','P1', 10,  40000, 30000,'INVOICED'),
  ('I-002',1,'2024-01-18','D3','South','P2',  4,  80000, 62000,'INVOICED'),
  ('I-003',1,'2025-01-08','D1','North','P1', 12,  50400, 37200,'INVOICED'),
  ('I-003',2,'2025-01-08','D1','North','P3', 20,  30000, 21000,'INVOICED'),
  ('I-004',1,'2025-01-21','D2','North','P2',  2,  42000, 33000,'INVOICED'),
  ('I-005',1,'2025-01-25','D3','South','P2',  5, 105000, 80000,'INVOICED'),
  ('I-006',1,'2025-01-28','D3','South','P1', -2,  -8400, -6200,'RETURNED'),
  ('I-007',1,'2025-01-30','D2','North','P1', 50, 210000,150000,'CANCELLED'),
  ('I-008',1,'2025-02-05','D1','North','P3', 10,  15500, 10500,'INVOICED'),
  ('I-009',1,'2025-02-14','D3','South','P1',  8,  33600, 24800,'INVOICED');

-- Stock: one row per dealer, product and day (a snapshot, semi-additive).
CREATE OR REPLACE TABLE main.sales_gold.fact_stock_daily (
  snapshot_date DATE, dealer_id STRING, region STRING, product_id STRING, units_on_hand INT);
INSERT INTO main.sales_gold.fact_stock_daily VALUES
  ('2025-01-30','D1','North','P1',40), ('2025-01-31','D1','North','P1',35),
  ('2025-01-30','D3','South','P2',12), ('2025-01-31','D3','South','P2',10);"""

EX_MV = """CREATE OR REPLACE VIEW main.sales_gold.sales_mv
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: "Tyre sales to dealers, one row per invoice line. Cancelled lines excluded; returns are negative lines. Owner: Sales Finance."
source: main.sales_gold.fact_sales_line
filter: status <> 'CANCELLED'
joins:
  - name: dealer
    source: main.sales_gold.dim_dealer
    on: source.dealer_id = dealer.dealer_id
  - name: product
    source: main.sales_gold.dim_product
    on: source.product_id = product.product_id
fields:
  - name: invoice_date
    expr: invoice_date
    display_name: Invoice date
  - name: invoice_month
    expr: DATE_TRUNC('MONTH', invoice_date)
    display_name: Invoice month
  - name: region
    expr: source.region
    display_name: Region
    synonyms: ['zone', 'sales region']
  - name: dealer_name
    expr: dealer.dealer_name
    display_name: Dealer
  - name: channel
    expr: dealer.channel
  - name: segment
    expr: CASE product.segment WHEN 'PCR' THEN 'Passenger car' WHEN 'TBR' THEN 'Truck and bus' WHEN '2W' THEN 'Two-wheeler' ELSE 'Other' END
    display_name: Segment
    synonyms: ['category', 'product line']
measures:
  - name: net_revenue
    expr: SUM(net_amount)
    display_name: Net revenue
    comment: "Invoiced amount after discounts, returns netted off, excluding tax."
    synonyms: ['revenue', 'sales', 'turnover']
  - name: gross_margin
    expr: SUM(net_amount - cost_amount)
    display_name: Gross margin
  - name: margin_pct
    expr: MEASURE(gross_margin) / NULLIF(MEASURE(net_revenue), 0)
    display_name: Margin %
  - name: units
    expr: SUM(qty)
    display_name: Units sold
  - name: invoices
    expr: COUNT(DISTINCT invoice_id)
  - name: avg_invoice_value
    expr: MEASURE(net_revenue) / NULLIF(MEASURE(invoices), 0)
    display_name: Average invoice value
  - name: active_dealers
    expr: COUNT(DISTINCT dealer_id) FILTER (WHERE status = 'INVOICED')
    display_name: Active dealers
  - name: net_revenue_ly
    expr: SUM(net_amount)
    display_name: Net revenue, same month last year
    window:
      - order: invoice_month
        range: current
        offset: -12 month
  - name: yoy_growth_pct
    expr: (MEASURE(net_revenue) - MEASURE(net_revenue_ly)) / NULLIF(MEASURE(net_revenue_ly), 0)
    display_name: Growth vs last year %
$$;

CREATE OR REPLACE VIEW main.sales_gold.stock_mv
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: "Dealer stock, one row per dealer, product and day."
source: main.sales_gold.fact_stock_daily
fields:
  - name: snapshot_date
    expr: snapshot_date
  - name: snapshot_month
    expr: DATE_TRUNC('MONTH', snapshot_date)
  - name: region
    expr: region
measures:
  - name: units_on_hand
    expr: SUM(units_on_hand)
    display_name: Units on hand
    window:
      - order: snapshot_date
        range: current
        semiadditive: last
$$;"""

EX_Q = """-- Q1 Net revenue and margin by region and month
SELECT region, invoice_month,
       MEASURE(net_revenue) AS revenue, MEASURE(margin_pct) AS margin
FROM main.sales_gold.sales_mv
GROUP BY ALL ORDER BY region, invoice_month;

-- Q2 Growth on the same month last year (January 2025 vs January 2024)
SELECT region, invoice_month,
       MEASURE(net_revenue) AS revenue, MEASURE(net_revenue_ly) AS revenue_ly, MEASURE(yoy_growth_pct) AS growth
FROM main.sales_gold.sales_mv
WHERE invoice_month = DATE'2025-01-01'
GROUP BY ALL ORDER BY region;

-- Q3 Company margin: ratio of sums, not the average of regional margins
SELECT MEASURE(margin_pct) AS company_margin FROM main.sales_gold.sales_mv WHERE year(invoice_date) = 2025;

-- Q4 Stock at month end (semi-additive): last day, not the sum of days
SELECT region, snapshot_month, MEASURE(units_on_hand) AS units_on_hand
FROM main.sales_gold.stock_mv GROUP BY ALL ORDER BY region;"""

EX_EXPECT = [
    ("Q1", "North, 2025-01", "122,400.00", "margin 0.2549  (31,200 margin; cancelled I-007 left out)"),
    ("Q1", "South, 2025-01", "96,600.00", "margin 0.2360  (105,000 minus an 8,400 return)"),
    ("Q2", "North, 2025-01", "122,400 vs 40,000", "growth 2.06 (206%)"),
    ("Q2", "South, 2025-01", "96,600 vs 80,000", "growth 0.2075 (20.75%)"),
    ("Q3", "2025, all regions", "268,100 revenue, 67,800 margin", "0.2529: summed first, divided last"),
    ("Q4", "North and South, 2025-01", "35 and 10", "the 31 Jan values, not 75 and 22"),
]

EX_RLS = """CREATE SCHEMA IF NOT EXISTS main.security;
CREATE OR REPLACE TABLE main.security.region_access (user_email STRING, region STRING);
INSERT INTO main.security.region_access VALUES ('asha@example.com','North'), ('ravi@example.com','*');

CREATE OR REPLACE FUNCTION main.security.region_filter(p_region STRING)
RETURN EXISTS (SELECT 1 FROM main.security.region_access a
               WHERE a.user_email = current_user() AND (a.region = p_region OR a.region = '*'));

ALTER TABLE main.sales_gold.fact_sales_line  SET ROW FILTER main.security.region_filter ON (region);
ALTER TABLE main.sales_gold.fact_stock_daily SET ROW FILTER main.security.region_filter ON (region);

GRANT SELECT ON VIEW main.sales_gold.sales_mv TO `sales-managers`;
GRANT SELECT ON VIEW main.sales_gold.stock_mv TO `sales-managers`;"""

EX_DBT = """# models/gold/sales.yml  (dbt 1.12+ latest spec; same gold tables)
models:
  - name: fact_sales_line
    semantic_model:
      enabled: true
    agg_time_dimension: invoice_date
    columns:
      - name: line_key                        # invoice_id || '-' || line_no, built in the model
        entity: { type: primary, name: sales_line }
      - name: dealer_id
        entity: { type: foreign, name: dealer }
      - name: product_id
        entity: { type: foreign, name: product }
      - name: invoice_date
        granularity: day
        dimension: { type: time }
      - name: region
        dimension: { type: categorical }
      - name: status
        dimension: { type: categorical }
    metrics:
      - name: net_revenue
        type: simple
        label: Net revenue
        agg: sum
        expr: net_amount
        filter: "{{ Dimension('sales_line__status') }} != 'CANCELLED'"
      - name: gross_margin
        type: simple
        agg: sum
        expr: net_amount - cost_amount
        filter: "{{ Dimension('sales_line__status') }} != 'CANCELLED'"

metrics:
  - name: margin_pct
    type: ratio
    label: Margin %
    numerator: gross_margin
    denominator: net_revenue
  - name: yoy_growth_pct
    type: derived
    label: Growth vs last year %
    expr: (net_revenue - net_revenue_ly) / nullif(net_revenue_ly, 0)
    input_metrics:
      - name: net_revenue
      - name: net_revenue
        offset_window: 1 year
        alias: net_revenue_ly

# Ask:  mf query --metrics net_revenue,margin_pct,yoy_growth_pct --group-by sales_line__region,metric_time__month
# Note: no RLS here; the warehouse identity running the query decides what rows exist."""

EX_DAX = """-- Power BI (thin model over the same gold tables, DirectQuery with SSO or Import)
Net Revenue      := CALCULATE ( SUM ( fact_sales_line[net_amount] ), fact_sales_line[status] <> "CANCELLED" )
Gross Margin     := CALCULATE ( SUMX ( fact_sales_line, fact_sales_line[net_amount] - fact_sales_line[cost_amount] ),
                               fact_sales_line[status] <> "CANCELLED" )
Margin %         := DIVIDE ( [Gross Margin], [Net Revenue] )
Net Revenue LY   := CALCULATE ( [Net Revenue], SAMEPERIODLASTYEAR ( dim_date[date] ) )
Growth vs LY %   := DIVIDE ( [Net Revenue] - [Net Revenue LY], [Net Revenue LY] )
Units on Hand    := CALCULATE ( SUM ( fact_stock_daily[units_on_hand] ), LASTDATE ( dim_date[date] ) )

-- RLS role 'Region' on fact tables (needed only for Import / Direct Lake copies):
-- reads the SAME entitlements table, loaded into the model as region_access
VAR me = USERPRINCIPALNAME ()
RETURN
  CONTAINS ( region_access, region_access[user_email], me, region_access[region], "*" )
  || CONTAINS ( region_access, region_access[user_email], me, region_access[region], fact_sales_line[region] )"""


def page_example():
    tested = (f'<div class="box"><b>Run and checked</b> on Databricks (Free Edition, serverless SQL warehouse) on {E(TESTED)}: every statement below ran, and the expected results table is what the queries returned.</div>'
              if TESTED else '<div class="warn"><b>Not yet run on Databricks.</b> The expected numbers were worked out by hand from the sample rows. Run the scripts in order and compare; tell us if anything differs.</div>')
    body = f"""{p('''A tyre maker sells to dealers in two regions. Sales Finance wants one set of numbers for a dashboard, a Genie space for managers, and Power BI for the monthly pack, and each regional manager must see only their region. Here it is, built end to end, small enough to run in a free workspace.''')}
{fig(d_example(), "Four gold tables, one entitlements table, two metric views, four readers.")}
{tested}
<ol class="steps">
<li><b>Agree the metrics first.</b> Before any table, write the questions and the metric each needs.{C.table(["Question", "Metric", "Sliced by"], EX_QUESTIONS)}<p>Two grains show up straight away: sales happen per invoice line; stock is counted per dealer per day. So: two fact tables, two metric views.</p></li>
<li><b>Build atomic gold.</b> One row per business event, keys declared, region copied onto the facts for cheap security, clustered by what dashboards filter on.{code(EX_GOLD)}</li>
<li><b>Write the metric views.</b> Atomic measures first, then composed ones; scope in the filter; names and synonyms for Genie; a window for last year; a semi-additive window for stock.{code(EX_MV)}</li>
<li><b>Ask questions.</b>{code(EX_Q)}{C.table(["Query", "Slice", "Result", "Why"], EX_EXPECT)}</li>
<li><b>Add row-level security</b> on the gold tables, from one entitlements table. Asha now sees only North; Ravi sees both. Users get SELECT on the metric views only.{code(EX_RLS)}</li>
<li><b>Decide on speed.</b> With row filters on the facts, materialization is refused. At this size nothing is needed. At real size: clustering is already on; if the CEO dashboard is still slow, build a day × region × segment aggregate table in the gold pipeline with the same row filter and a small metric view over it. Company-wide KPIs with no security can live in a separate, materialized metric view.</li>
<li><b>Serve it.</b> An AI/BI dashboard with datasets on the metric views (one tile = one MEASURE query). A Genie space over <code>sales_mv</code> and <code>stock_mv</code> only, with example questions and benchmarks ("revenue by zone last month" must equal Q1). Power BI reads through native query with MEASURE() in DirectQuery, or a thin model (step 9).</li>
<li><b>Test it.</b> The Q1–Q4 numbers become golden-number tests (see <a href="{BASE}production/#tests">the table-driven tests</a>); join-key uniqueness on dim_dealer and dim_product; RLS tests as Asha, Ravi and a user with no row. Commit the YAML, deploy from CI, certify.</li>
<li><b>The same model in dbt and Power BI</b>, for comparison. Notice what each needs that the metric view got from Unity Catalog: dbt has no security of its own, and Power BI needs a role when it holds a copy.
<h3>dbt Semantic Layer</h3>{code(EX_DBT)}<h3>Power BI DAX</h3>{code(EX_DAX)}</li>
</ol>
{sec("learned", "What the example shows", "Six lessons in one small model", ul([
    "Agreeing the metrics first decided the gold tables and their grain.",
    "The filter kept cancelled invoice I-007 (210,000) out of every number, in every tool.",
    "Margin was composed from sums, so the company margin (25.3%) is summed first and divided last, at any grain.",
    "Last year and stock needed windows, not new tables.",
    "Security lived on gold, once; the metric views needed no change to respect it.",
    "The same model in dbt and DAX is longer and must add the security story itself.",
]))}
{nextprev("example/")}"""
    qa = [("Can I run this example on Databricks Free Edition?", "Yes. Use the catalog 'workspace' instead of 'main', run the gold script, then the metric views, then the queries on the serverless SQL warehouse. Row filters need a second user to see the effect."),
          ("Why copy region onto the fact table?", "So the row filter checks a column on the row itself, without a join per row. The dealer table still holds region for slicing; gold keeps the two in step."),
          ("Why two metric views instead of one?", "Sales and stock have different grains: invoice lines versus dealer-product-day snapshots. Putting them in one view would make one of them fan out.")]
    return body, qa


# =============================================================== render
BUILDERS = {"": page_start, "semantic-model/": page_idea, "three-ways/": page_three, "limits/": page_limits, "anatomy/": page_anatomy,
            "granularity/": page_grain, "security/": page_security, "performance/": page_perf, "production/": page_prod, "example/": page_example}


def render(slug):
    _, lab, title, desc = next(x for x in PAGES if x[0] == slug)
    url = f"{SITE}{BASE}{slug}"
    inner, qa = BUILDERS[slug]()
    crumb = f'<a href="/">Home</a> › <a href="/data-engineering/">Data engineering</a> › ' + (f'<a href="{BASE}">Metric views</a> › {E(lab)}' if slug else "Metric views")
    body = f"""<p class="crumbs">{crumb}</p>
<p class="eyebrow" style="margin-top:22px">Data engineering · BI and analytics · free guide{' · ' + E(lab) if slug else ''}</p>
<h1>{E(title)}</h1>
{path_nav(slug)}
<div class="bi">
{inner}
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(qa)}</section>
<section id="sources"><p class="eyebrow">Sources</p><h2>Checked against (11 Nov 2026)</h2><ul>
<li><a href="https://docs.databricks.com/aws/en/metric-views/">Databricks: Unity Catalog metric views</a> and the <a href="https://docs.databricks.com/aws/en/metric-views/data-modeling/syntax">YAML reference</a></li>
<li><a href="https://docs.databricks.com/aws/en/uc-semantics/metric-views/materialization">Materialization</a> · <a href="https://docs.databricks.com/aws/en/uc-semantics/metric-views/advanced-techniques">Advanced techniques</a> · <a href="https://docs.databricks.com/aws/en/uc-semantics/metric-views/relationships">Relationships</a> · <a href="https://docs.databricks.com/aws/en/uc-semantics/metric-views/bi-tools">BI tools</a> · <a href="https://docs.databricks.com/aws/en/uc-semantics/metric-views/feature-availability">Feature availability</a></li>
<li><a href="https://docs.databricks.com/aws/en/data-governance/unity-catalog/filters-and-masks/">Row filters and column masks</a> · <a href="https://kb.databricks.com/upcoming-change-to-abac-policy-evaluation-for-tables-accessed-through-views-and-functions">ABAC evaluation through views (KB)</a></li>
<li><a href="https://docs.getdbt.com/docs/build/semantic-models">dbt semantic models</a> · <a href="https://www.getdbt.com/blog/dbt-labs-affirms-commitment-to-open-semantic-interchange-by-open-sourcing-metricflow">MetricFlow open-sourced</a> · <a href="https://ossie.apache.org/updates/ossie-enters-apache-incubator/">Apache Ossie</a></li>
</ul><p>Metric views change every few months. Confirm runtime minimums and preview status before a design depends on them.</p></section>
</div>"""
    crumbs = [("Data engineering", f"{SITE}/data-engineering/"), ("Metric views", f"{SITE}{BASE}")] + ([(lab, url)] if slug else [])
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": title, "description": desc, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}]
    head = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(title, desc, url, body, head)


def main():
    for slug, *_ in PAGES:
        out = ROOT / BASE.strip("/") / slug
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(render(slug))
        print("metric views ->", out / "index.html")


if __name__ == "__main__":
    main()
