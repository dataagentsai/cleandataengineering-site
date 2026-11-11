"""Power BI vs Databricks AI/BI on a lakehouse: three pages under /learn/power-bi-vs-databricks-ai-bi/.

    python3 _guides/bi_choice.py      (then python3 _site/nav.py and python3 _site/seo.py)

Page 1 (the decision): where the semantic model lives, where row-level security lives, how RLS
works on both sides at once, volume, cost comparison, the recommended architecture.
Page 2 (Power BI and Fabric in depth): how Fabric and the VertiPaq engine work, storage modes,
Direct Lake, RLS mechanics, troubleshooting, benchmarking, testing, limits, production problems.
Page 3 (Databricks AI/BI in depth): how dashboards and Genie run, RLS, volume, troubleshooting,
benchmarking, testing, limits, production problems.

Facts written from vendor docs as known in Nov 2026. Limits and prices change often; anything
marked "check" must be confirmed in the current docs before it goes into a design.
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
BASE = "/learn/power-bi-vs-databricks-ai-bi/"
DATE = "2026-11-11"

CSS = C.CSS + """<style>
  .bi .fig { border:var(--line); border-radius:var(--wob); padding:12px 14px; margin:16px 0; background:#fff; overflow-x:auto; }
  .bi .fig svg { width:100%; min-width:680px; height:auto; display:block; } .bi .fig text { font-family:var(--hand); fill:#111; }
  .bi .fig p { font-size:13.5px; color:var(--muted); margin:6px 0 0; }
  .bi .box { border:var(--line); border-radius:var(--wob); padding:10px 16px; margin:14px 0; background:var(--butter-wash); }
  .bi .warn { border:var(--line); border-radius:var(--wob); padding:10px 16px; margin:14px 0; background:var(--rose-wash); }
  .bi .tabs3 { display:flex; flex-wrap:wrap; gap:8px; margin:18px 0; }
  .bi .tabs3 a { border:1.5px solid var(--ink); border-radius:999px; padding:4px 14px; background:#fff; color:var(--ink); text-decoration:none; font-size:15px; }
  .bi .tabs3 a.on { background:var(--butter-wash); font-weight:700; }
  .bi table.t td { font-size:14px; }
  .bi td.v { font-weight:700; white-space:nowrap; }
  .bi .toc { columns:2; } @media (max-width:700px){ .bi .toc { columns:1; } }
</style>"""

# ---------------------------------------------------------------- tiny drawing kit
FILLS = {"b": "#eef3fb", "g": "#eaf6ef", "y": "#fff6dc", "r": "#fbeef3", "w": "#fff", "l": "#f1eefb"}


def bx(x, y, w, h, lines, f="w", size=15, dash=False):
    d = ' stroke-dasharray="3 4"' if dash else ""
    out = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{FILLS[f]}" stroke="#111" stroke-width="1.5"{d}/>'
    if isinstance(lines, str):
        lines = [lines]
    top = y + h / 2 - (len(lines) - 1) * (size + 3) / 2 + size / 3
    for i, ln in enumerate(lines):
        s = size if i == 0 else size - 2
        out += f'<text x="{x + w / 2}" y="{top + i * (size + 3)}" font-size="{s}" text-anchor="middle">{E(ln)}</text>'
    return out


def ar(x1, y1, x2, y2, dash=False, label="", lx=None, ly=None):
    d = ' stroke-dasharray="5 5"' if dash else ""
    out = f'<path d="M{x1},{y1} L{x2},{y2}" stroke="#111" stroke-width="1.4" fill="none" marker-end="url(#bia)"{d}/>'
    if label:
        out += f'<text x="{lx if lx is not None else (x1 + x2) / 2}" y="{ly if ly is not None else (y1 + y2) / 2 - 6}" font-size="13" text-anchor="middle">{E(label)}</text>'
    return out


def svg(w, h, label, inner):
    return (f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{E(label)}"><defs><marker id="bia" viewBox="0 0 10 10" refX="9" refY="5" '
            f'markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#111"/></marker></defs>{inner}</svg>')


def fig(drawing, cap):
    return f'<div class="fig">{drawing}<p>{E(cap)}</p></div>'


def t(x, y, s, size=14, anchor="start"):
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}">{E(s)}</text>'


# ---------------------------------------------------------------- drawings
def d_big_picture():
    i = bx(10, 150, 160, 80, ["Gold Delta tables", "in the lakehouse"], "g")
    i += bx(230, 110, 230, 160, ["Unity Catalog", "metric views (the numbers)", "row filters + masks", "entitlements table", "(who may see what)"], "y")
    i += bx(560, 20, 200, 52, ["AI/BI dashboards", "as the viewer"], "b")
    i += bx(560, 86, 200, 52, ["Genie", "questions in plain words"], "b")
    i += bx(560, 152, 200, 52, ["Agents", "typed tools, as the user"], "b")
    i += bx(560, 236, 200, 52, ["Power BI DirectQuery", "+ single sign-on"], "l")
    i += bx(560, 310, 200, 52, ["Power BI Import", "or Direct Lake (a copy)"], "r")
    i += bx(800, 270, 190, 92, ["Power BI model", "thin: measures 1:1", "with metric views;", "RLS role reads the", "same entitlements"], "r", 14)
    i += ar(170, 190, 228, 190)
    for y in (46, 112, 178, 262):
        i += ar(460, 190, 558, y)
    i += ar(460, 230, 558, 334, True, "copy leaves Unity Catalog", 400, 292)
    i += ar(760, 334, 798, 320)
    i += t(560, 395, "Blue and lavender: Unity Catalog rules apply, because the query runs as the person looking.", 13)
    i += t(560, 413, "Rose: data was copied out, so Power BI must apply the rules itself.", 13)
    return svg(1000, 420, "The recommended picture: gold Delta tables feed Unity Catalog metric views with row filters and an entitlements table. AI/BI dashboards, Genie, agents and Power BI DirectQuery with single sign-on all query as the user so Unity Catalog rules apply. Power BI Import or Direct Lake copies data, so a thin Power BI model applies its own RLS role that reads the same entitlements table.", i)


def d_semantic_three():
    i = ""
    cols = [(10, "A. Databricks side only", "b", ["metric views hold", "every definition"], ["Power BI model is thin:", "simple measures that", "match metric views"], "Pursue (default)"),
            (343, "B. Both sides, by hand", "r", ["metric views", "one version"], ["DAX measures", "a second version"], "Drop: numbers drift"),
            (676, "C. Power BI side only", "l", ["Databricks only", "stores tables"], ["the Power BI model", "is the only truth"], "Only if Power BI is the sole consumer")]
    for x, head, f, top, bot, verdict in cols:
        i += t(x + 157, 26, head, 17, "middle")
        i += bx(x + 20, 40, 274, 70, ["Databricks: " + top[0], top[1]], "g")
        i += bx(x + 20, 140, 274, 80, ["Power BI: " + bot[0]] + bot[1:], f)
        i += ar(x + 157, 110, x + 157, 138)
        i += t(x + 157, 250, verdict, 15, "middle")
    return svg(1000, 262, "Three places to keep the semantic model. A: definitions live in Databricks metric views and the Power BI model is thin, verdict pursue. B: definitions are written twice by hand, verdict drop because numbers drift. C: only Power BI holds definitions, only if Power BI is the sole consumer.", i)


def d_rls_both():
    i = bx(360, 10, 280, 70, ["entitlements table (gold)", "user_email · region"], "y")
    i += bx(40, 130, 330, 90, ["Unity Catalog row filter", "a SQL function on the table:", "current_user() in entitlements?"], "b")
    i += bx(630, 130, 330, 90, ["Power BI dynamic RLS role", "DAX: [user_email] =", "USERPRINCIPALNAME()"], "r")
    i += ar(430, 80, 260, 128)
    i += ar(570, 80, 760, 128, False, "imported like any table", 740, 100)
    i += bx(10, 270, 190, 60, ["AI/BI", "viewer credentials"], "w")
    i += bx(215, 270, 170, 60, ["Genie, agents"], "w")
    i += bx(400, 270, 200, 60, ["Power BI DirectQuery", "+ SSO (both apply)"], "l")
    i += bx(640, 270, 320, 60, ["Power BI Import, Direct Lake", "(Unity Catalog cannot see these)"], "w")
    for x in (105, 300, 470):
        i += ar(205, 220, x, 268)
    i += ar(795, 220, 795, 268)
    i += ar(700, 220, 530, 268, True)
    return svg(1000, 340, "One entitlements table in gold drives two enforcement points. A Unity Catalog row filter function protects AI/BI, Genie, agents and Power BI DirectQuery with single sign-on. A Power BI dynamic RLS role, which imports the same table, protects Import and Direct Lake models. With DirectQuery and single sign-on both apply.", i)


def d_pbi_modes():
    i = ""
    cols = [(10, "Import", ["refresh copies", "data into", "VertiPaq memory"], "fastest clicks;", "stale until refresh", "y"),
            (258, "DirectQuery", ["each visual sends", "SQL to Databricks", "every time"], "always fresh;", "every click costs", "b"),
            (506, "Direct Lake (Fabric)", ["reads Delta files in", "OneLake straight", "into memory"], "fast and fresh;", "needs OneLake", "g"),
            (754, "Composite", ["small tables imported,", "big facts DirectQuery,", "aggregations on top"], "balanced;", "most moving parts", "l")]
    for x, head, mid, a, b, f in cols:
        i += t(x + 118, 24, head, 18, "middle")
        i += bx(x + 10, 40, 216, 60, ["Power BI visual"], "w")
        i += bx(x + 10, 130, 216, 86, mid, f, 14)
        i += bx(x + 10, 246, 216, 50, ["Delta tables"], "w", dash=True)
        i += ar(x + 118, 100, x + 118, 128)
        i += ar(x + 118, 216, x + 118, 244)
        i += t(x + 118, 322, a, 14, "middle") + t(x + 118, 340, b, 14, "middle")
    return svg(1000, 352, "Four Power BI storage modes. Import refreshes a copy into VertiPaq memory: fastest, stale until refresh. DirectQuery sends SQL for every visual: fresh, every click costs. Direct Lake reads Delta files in OneLake into memory: fast and fresh but needs OneLake. Composite mixes them with aggregations.", i)


def d_pbi_engine():
    i = bx(10, 120, 130, 60, ["visual"], "w")
    i += bx(180, 120, 150, 60, ["DAX query"], "w")
    i += bx(370, 100, 190, 100, ["Formula engine", "one thread: the", "logic of the DAX"], "l")
    i += bx(610, 20, 180, 90, ["Storage engine", "VertiPaq: many threads,", "scans compressed columns"], "y", 14)
    i += bx(610, 190, 180, 90, ["DirectQuery", "SQL sent to the", "Databricks warehouse"], "b", 14)
    i += bx(830, 20, 160, 90, ["memory: columns", "dictionary + run-", "length encoded"], "g", 14)
    i += bx(830, 190, 160, 90, ["Delta tables", "(Photon does", "the work)"], "g", 14)
    i += ar(140, 150, 178, 150) + ar(330, 150, 368, 150)
    i += ar(560, 130, 608, 70) + ar(560, 170, 608, 230)
    i += ar(790, 65, 828, 65) + ar(790, 235, 828, 235)
    i += t(10, 300, "Slow query? Look at the split: lots of formula-engine time means the DAX is the problem; lots of storage-engine or SQL time means the data or the model is.", 13)
    return svg(1000, 312, "Inside a Power BI query: a visual sends a DAX query; the single-threaded formula engine works out the logic and asks the storage engine, which scans compressed in-memory columns in VertiPaq, or sends SQL to the Databricks warehouse in DirectQuery.", i)


def d_fabric():
    i = bx(330, 10, 340, 56, ["Fabric capacity (F2 … F2048)", "one pool of capacity units (CU)"], "y")
    for k, (x, lbl) in enumerate([(20, "Power BI"), (190, "Data Factory"), (360, "Spark / Lakehouse"), (530, "Warehouse"), (700, "Real-Time"), (850, "Data Science")]):
        i += bx(x, 110, 140 if k < 5 else 130, 50, [lbl], "b" if k == 0 else "w", 14)
        i += ar(500, 66, x + 70, 108)
    i += bx(100, 210, 800, 60, ["OneLake: one lake per tenant, Delta Parquet files", "shortcuts point at ADLS, S3 or GCS without copying; mirroring copies other databases in"], "g")
    i += ar(90, 160, 160, 208) + ar(430, 160, 430, 208) + ar(600, 160, 600, 208)
    return svg(1000, 282, "Microsoft Fabric: one capacity of capacity units shared by Power BI, Data Factory, Spark, Warehouse, Real-Time and Data Science, all reading one OneLake of Delta Parquet files, with shortcuts to ADLS, S3 or GCS.", i)


def d_aibi():
    i = bx(10, 120, 120, 60, ["viewer"], "w")
    i += bx(170, 100, 180, 100, ["AI/BI dashboard", "datasets: SQL or", "metric views"], "b")
    i += bx(390, 100, 200, 100, ["SQL warehouse", "serverless, Photon,", "result cache"], "y")
    i += bx(630, 100, 170, 100, ["Unity Catalog", "checks rights,", "adds row filter"], "y")
    i += bx(840, 100, 150, 100, ["Delta tables", "(gold)"], "g")
    i += ar(130, 150, 168, 150) + ar(350, 150, 388, 150, False, "SQL per widget", 369, 92) + ar(590, 150, 628, 150) + ar(800, 150, 838, 150)
    i += bx(170, 240, 420, 60, ["published with whose identity?", "viewer's (rules per person) or the publisher's (everyone sees the same)"], "r", 14)
    i += ar(260, 200, 300, 238, True)
    i += bx(630, 240, 360, 60, ["Genie: an LLM writes SQL over the space's", "tables and metric views, then runs it as the user"], "l", 14)
    return svg(1000, 312, "How an AI/BI dashboard runs: the viewer opens it, each widget sends SQL from its dataset to a SQL warehouse, Unity Catalog checks rights and adds the row filter, and Delta tables answer. The key choice is whether the dashboard runs as the viewer or as the publisher. Genie writes SQL and runs it as the user.", i)


# ---------------------------------------------------------------- shared bits
def vtable(head, rows):
    h = "".join(f"<th>{E(x)}</th>" for x in head)
    r = "".join("<tr>" + "".join(f"<td{' class=\"v\"' if i == len(row) - 1 else ''}>{'<b>' + E(c) + '</b>' if i == 0 else E(c)}</td>" for i, c in enumerate(row)) + "</tr>" for row in rows)
    return f'<div class="tw"><table class="t"><tr>{h}</tr>{r}</table></div>'


PAGES = [("", "The decision"), ("power-bi/", "Power BI and Fabric, in depth"), ("ai-bi/", "Databricks AI/BI, in depth")]


def tabs(cur):
    return '<div class="tabs3">' + "".join(f'<a class="{"on" if s == cur else ""}" href="{BASE}{s}">{E(n)}</a>' for s, n in PAGES) + "</div>"


def sec(id_, eyebrow, h2, html):
    return f'<section id="{id_}"><p class="eyebrow">{E(eyebrow)}</p><h2>{E(h2)}</h2>{html}</section>'


def p(*xs):
    return "".join(f"<p>{x}</p>" for x in xs)


def ul(items):
    return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


# =============================================================== PAGE 1: the decision
SEM_ROWS = [
    ("A. Databricks side: metric views hold every definition; Power BI keeps a thin model whose measures match them one to one",
     "One truth for dashboards, Genie, agents and Power BI. Power BI still needs a model (it cannot run without one), but the model holds no business logic of its own. An automated test checks every Power BI measure against its metric view.", "Pursue (default)"),
    ("B. Both sides, each written by hand",
     "Two teams, two languages (SQL/YAML and DAX), two release cycles. Within months 'revenue' differs by a filter. This is the most common real-world mess.", "Drop"),
    ("C. Power BI side only: Databricks stores tables, the Power BI model is the semantic layer",
     "Fine when Power BI is the only consumer and nobody else needs the numbers. Breaks the day you add Genie, an agent, an API or a second BI tool: they cannot read DAX measures.", "Only if Power BI is the sole consumer, forever"),
    ("B, done right: definitions in one source (metric-view YAML), Power BI measures generated or checked from it",
     "Both sides exist, but one is derived from the other and a test fails the build if they disagree.", "Pursue when Power BI is large"),
]

RLS_ROWS = [
    ("Databricks side only (Unity Catalog row filters and column masks)",
     "Works for every consumer that queries as the person looking: AI/BI with viewer credentials, Genie, agents acting on behalf of the user, Power BI DirectQuery with single sign-on.",
     "Power BI Import or Direct Lake: the data is copied out, so the filter is not there. Power BI DirectQuery with a shared service account: Databricks sees one user.", "Pursue (default)"),
    ("Power BI side only (roles in the model)",
     "Works inside Power BI for Import, Direct Lake and DirectQuery.",
     "Nothing else is protected: an analyst in Databricks, Genie or an agent sees every row. Workspace admins, members and contributors skip Power BI RLS entirely.", "Drop as the only layer"),
    ("Both sides, driven by one entitlements table",
     "Needed whenever Power BI uses Import or Direct Lake. Both rules read the same gold table (who may see which region, plant or customer), so access is changed in one place.",
     "Two enforcement points to test. The test suite runs the same user on both sides and expects the same row count.", "Pursue when Power BI copies data"),
    ("Both sides, each kept by hand (AD groups in Power BI roles, different groups in Unity Catalog)",
     "Looks fine on day one.", "Someone is removed in one place and not the other. Auditors find it.", "Drop"),
]

VOLUME_ROWS = [
    ("Power BI Import", "Compressed copy in memory (often 5 to 10 times smaller than Parquet text, depends on cardinality)",
     "Model memory limit per capacity size; 1 GB per model on Pro; refresh time windows; refresh doubles memory while it runs", "Gold aggregates up to tens of millions of rows; fastest clicks"),
    ("Power BI DirectQuery", "Nothing copied; every visual is a SQL query",
     "Each visual waits on the warehouse; a 1 million row cap on intermediate results; limited parallel connections", "Billions of rows, if you add aggregation tables and a well-clustered gold layer"),
    ("Power BI Direct Lake", "Delta files in OneLake loaded into memory column by column when first asked",
     "Guardrails per capacity size (rows per table, files and row groups per table, memory); beyond them it falls back to DirectQuery or fails", "Large Fabric-native data; Databricks data only through shortcuts or mirroring"),
    ("Databricks AI/BI", "Nothing copied; every widget is a SQL query on a SQL warehouse",
     "Warehouse size and number of clusters; result-size caps per widget; cost grows with clicks", "Any size the warehouse can scan quickly; clustered gold tables and materialized views keep it fast"),
]

COST_ASSUMPTIONS = ("Example: 25 report authors, 500 viewers, used 10 hours a day on 22 working days. US list prices as known in November 2026, "
                    "rounded; your discounts, region and Microsoft 365 agreement change them a lot. Databricks serverless SQL at about $0.70 per DBU; "
                    "a Small warehouse is 12 DBU an hour and a Medium is 24.")

COST_ROWS = [
    ("Power BI Pro for everyone, Import", "525 × $14 = about $7,350", "refresh only: about 22 hours of Small = about $185", "about $7,500", "Simple; cost grows with every viewer"),
    ("Fabric F64 (viewers free) + 25 Pro authors, Import or Direct Lake", "F64 about $5,000 reserved (about $8,400 pay-as-you-go) + $350", "about $185 for refresh", "about $5,500 to $9,000", "Pays off above roughly 400 viewers; capacity also runs other Fabric work"),
    ("Power BI Pro for everyone, DirectQuery", "about $7,350", "every click: Medium for 220 hours = about $3,700", "about $11,000", "The worst of both bills; use only where freshness or Unity Catalog RLS demands it"),
    ("Databricks AI/BI only", "none (no per-viewer licence)", "Small to Medium for 220 hours = about $1,850 to $3,700; auto-stop lowers it", "about $2,000 to $4,000", "Cheapest for many occasional viewers; costs follow usage"),
    ("Both: Power BI for 100 report users, AI/BI and Genie for the rest", "100 × $14 = $1,400 (often $0 if Microsoft 365 E5 already includes Pro)", "about $2,000 to $3,000", "about $2,000 to $4,500", "Usually the best value in a Microsoft shop"),
]

USE_ROWS = [
    ("Operations, platform and data-trust dashboards", "AI/BI", "Next to the data, no licences, Unity Catalog rules apply directly.", "Pursue"),
    ("Plain-language questions from business users", "Genie over metric views", "Answers use the same certified definitions as the dashboards.", "Pursue"),
    ("Agents that need numbers", "Typed tools over metric views (or the Genie API)", "Agents call tools; they never write free SQL against raw tables.", "Pursue"),
    ("Board packs, finance, paginated and printed reports, Excel, Teams", "Power BI", "Stronger formatting, paginated reports, Excel and Teams; Pro is often already paid for.", "Pursue in a Microsoft 365 company"),
    ("Heavy self-service modelling by analysts who know DAX", "Power BI on a certified thin model", "Let them build reports, not new definitions of revenue.", "Pursue with guardrails"),
    ("A company with no Microsoft estate", "AI/BI only", "Power BI would add licences, a second model and a second set of security rules for little gain.", "Drop Power BI"),
    ("Power BI Copilot as the agent layer", "—", "It works only over a Power BI model and needs Fabric capacity; it becomes a second source of truth for AI.", "Drop"),
]

FAQ1 = [
    ("Should the semantic model live in Databricks or in Power BI?", "Keep the definitions in Databricks (Unity Catalog metric views) and keep the Power BI model thin, with measures that match the metric views one to one and a test that checks they agree. Power BI always needs a model to run, but it should not invent its own business logic."),
    ("Where should row-level security live?", "In Unity Catalog, as row filters and column masks, driven by one entitlements table. Add a Power BI role that reads the same table only when Power BI copies data out (Import or Direct Lake), because then Unity Catalog cannot see the query."),
    ("Does Unity Catalog row-level security apply to Power BI?", "Only in DirectQuery with single sign-on, where each Power BI user's own identity reaches Databricks. With Import, Direct Lake, or a shared service account, it does not, and Power BI must apply its own role."),
    ("Is Databricks AI/BI cheaper than Power BI?", "For many occasional viewers, usually yes: AI/BI has no per-viewer licence and you pay only for warehouse time. For a few heavy users in a company that already pays for Microsoft 365 E5, Power BI can cost almost nothing extra. DirectQuery from Power BI pays both bills."),
    ("Can we use both?", "Yes, and many companies should: AI/BI and Genie for operations, engineering and plain-language questions, Power BI for formal reporting in Microsoft 365. The rule is one set of definitions and one entitlements table under both."),
]


def page_decision():
    url = SITE + BASE
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/concepts/semantic-layer/">BI and analytics</a> › Power BI vs Databricks AI/BI</p>
<p class="eyebrow" style="margin-top:22px">BI and analytics · free guide · three pages</p>
<h1>Power BI vs Databricks AI/BI, or both, on a lakehouse</h1>
<p class="lede">Your data already sits in a lakehouse (Delta tables in Databricks). Which BI tool should people use, where should the business definitions live, where should row-level security live, how does each handle big data, and what does it cost? This page decides. The two in-depth pages explain how each tool works inside, how to troubleshoot, benchmark and test it, and what goes wrong in production.</p>
<div class="bi">{tabs("")}
<div class="box"><b>The short answer.</b> Use both, with one rule: business definitions (metric views) and row-level security (row filters driven by one entitlements table) live once, in Databricks Unity Catalog. AI/BI dashboards, Genie and agents read them directly. Power BI is a thin reader for formal reporting in Microsoft 365 companies. If Power BI copies data (Import or Direct Lake), it applies a role that reads the same entitlements table.</div>
<ul class="toc"><li><a href="#plain">In plain words</a></li><li><a href="#semantic">Where the semantic model lives</a></li><li><a href="#rls">Where row-level security lives</a></li><li><a href="#rls-both">How RLS works on both sides</a></li><li><a href="#volume">How each handles big data</a></li><li><a href="#cost">Cost comparison</a></li><li><a href="#use">Which tool for which job</a></li><li><a href="#arch">The recommended architecture</a></li><li><a href="#faq">Questions people ask</a></li></ul>

{sec("plain", "In plain words", "Three things a BI tool needs", p(
"Every BI setup needs three things. <b>Data</b>: the tables, here gold Delta tables in the lakehouse. <b>Meaning</b>: the semantic model, which says what 'revenue' or 'on-time delivery' means, how tables join, and which filters apply. <b>Permission</b>: row-level security (RLS), which decides that a sales manager in the North sees only North rows.",
"Power BI and Databricks AI/BI can both hold the meaning and the permission. The question is not which tool is better. The question is <b>where meaning and permission should live so that every tool, and every AI agent, gives the same number to the same person</b>.")
+ fig(d_big_picture(), "The recommended picture. Meaning and permission live once in Unity Catalog. Tools that query as the person looking get the rules for free; Power BI copies get a thin model and a role that reads the same entitlements table."))}

{sec("semantic", "Decision 1", "Where should the semantic model live?",
fig(d_semantic_three(), "Three choices. Keep definitions in one place; a second hand-written copy always drifts.")
+ vtable(["Option", "What happens", "Verdict"], SEM_ROWS)
+ p("<b>What a thin Power BI model looks like:</b> tables or views from gold, relationships, and measures that are simple sums, counts or ratios with the same names and filters as the metric views. No calculated business rules that exist only in DAX. A nightly test runs each Power BI measure (through the XMLA endpoint or the executeQueries API) and the same metric view in Databricks, and fails if they differ.",
    "<b>Can Power BI read metric views directly?</b> Support for reading Unity Catalog metric views from outside Databricks is still changing (check the current Databricks and Power BI connector notes). If your setup cannot, point Power BI at gold aggregate views generated from the same metric-view YAML, so the definition still lives in one file."))}

{sec("rls", "Decision 2", "Where should row-level security live?",
vtable(["Option", "Works for", "Fails for", "Verdict"], RLS_ROWS)
+ '<div class="warn"><b>Two traps that leak data.</b> (1) An AI/BI dashboard published with the publisher\'s credentials runs every query as the publisher, so every viewer sees the publisher\'s rows. Publish secured dashboards with viewer credentials. (2) Power BI RLS does not apply to workspace Admins, Members and Contributors. Give report readers the Viewer role or an app audience, never Member.</div>')}

{sec("rls-both", "Decision 2, continued", "How RLS works on both sides at once",
fig(d_rls_both(), "One entitlements table, two enforcement points. With DirectQuery and single sign-on both apply, and the user sees the overlap.")
+ p("<b>The entitlements table</b> lives in gold and is owned by the data team, fed from HR or your identity system: one row per person (or group) per thing they may see, such as <code>user_email, region</code>.")
+ C.code('''-- Unity Catalog: a row filter function, then attach it to the table
CREATE FUNCTION sec.region_filter(region STRING) RETURN
  is_account_group_member('bi_all_regions')
  OR EXISTS (SELECT 1 FROM gold.entitlements e
             WHERE e.user_email = current_user() AND e.region = region);

ALTER TABLE gold.sales SET ROW FILTER sec.region_filter ON (region);

-- A column mask: only HR sees salaries
CREATE FUNCTION sec.mask_salary(v DECIMAL(12,2)) RETURN
  CASE WHEN is_account_group_member('hr') THEN v ELSE NULL END;
ALTER TABLE gold.employees ALTER COLUMN salary SET MASK sec.mask_salary;''',
"Databricks adds the filter to every query on Databricks compute (SQL warehouses, serverless, standard clusters), including queries from metric views, dashboards, Genie and Power BI DirectQuery.")
+ C.code('''// Power BI: a role on the imported Entitlements table
// Model: Entitlements[region] 1 ─► * Sales[region]  (filter flows to Sales)
[user_email] = USERPRINCIPALNAME()''',
"Power BI: the role filters the small Entitlements table and the relationship carries the filter to the fact table. Members of the role are Entra ID groups, assigned in the service.")
+ p("<b>What the user sees in DirectQuery with single sign-on:</b> Power BI's role filters first, then the SQL reaches Databricks as that user, so the Unity Catalog filter also applies. The user sees rows allowed by both. With one shared entitlements table the two always agree.",
    "<b>Why not just one side?</b> Unity Catalog cannot see inside a Power BI Import or Direct Lake model: those read a copy or the files directly. Fabric cannot mirror Databricks tables that have row filters or column masks (check the current mirroring limits), which pushes you to Power BI roles for Fabric-side copies."))}

{sec("volume", "Decision 3", "How each handles big data",
vtable(["Mode", "Where the data sits", "What limits it", "Good for"], VOLUME_ROWS)
+ p("<b>The rule that matters most is the same for both tools: build gold aggregates for dashboards.</b> A dashboard that scans 4 billion raw rows to draw 12 monthly bars is slow and costly in any tool. Pre-aggregate by day and the main dimensions, cluster on the filter columns, and keep the raw detail for drill-through only."))}

{sec("cost", "Decision 4", "Cost comparison",
p(E(COST_ASSUMPTIONS))
+ vtable(["Setup", "BI licences per month", "Databricks compute per month", "Total per month", "Comment"], COST_ROWS)
+ p("Rough, unverified list-price estimates. Run your own numbers in the <a href=\"/learn/data-systems/platform/cost/calculator/\">Databricks cost calculator</a> and with your Microsoft agreement. Two things move the answer most: whether Microsoft 365 E5 already includes Power BI Pro for everyone, and how many viewers open dashboards only a few times a month."))}

{sec("use", "Decision 5", "Which tool for which job", vtable(["Job", "Use", "Why", "Verdict"], USE_ROWS))}

{sec("arch", "Putting it together", "The recommended architecture", ul([
"<b>Gold</b>: Delta tables, liquid-clustered on the columns dashboards filter by, plus pre-aggregated gold tables or materialized views for dashboards.",
"<b>Semantic layer</b>: Unity Catalog metric views, written in YAML, kept in git, certified. The only place a business number is defined.",
"<b>Security</b>: one entitlements table in gold; Unity Catalog row filters and column masks read it; Power BI roles read it only where Power BI copies data.",
"<b>AI/BI dashboards</b> for operations and engineering, published with viewer credentials when data is sensitive.",
"<b>Genie</b> over metric views only, with instructions, example questions and benchmarks. <b>Agents</b> call typed tools over metric views.",
"<b>Power BI</b>: a thin, certified model. DirectQuery with single sign-on for sensitive, fresh data; Import for small, non-sensitive, heavily used aggregates; Direct Lake only if the company runs on Fabric and the data is in OneLake.",
"<b>Tests</b>: the same-number test (Power BI measure equals metric view), the same-rows test (one user sees the same row count in both tools), and a performance budget per dashboard (see the in-depth pages).",
]) + p("Swapping tools later is then cheap: a new BI tool is one more reader of the same metric views and the same security rules."))}

{sec("faq", "FAQ", "Questions people ask", C.faq(FAQ1))}
{sec("next", "Read on", "The in-depth pages", p(f'<a href="{BASE}power-bi/">Power BI and Fabric, in depth</a>: how it works inside, Direct Lake, RLS mechanics, troubleshooting, benchmarking, testing, production problems. <a href="{BASE}ai-bi/">Databricks AI/BI, in depth</a>: the same for AI/BI dashboards and Genie. Related: <a href="/concepts/semantic-layer/">the semantic layer</a> · <a href="/writing/genie-metric-views/">Genie and metric views</a> · <a href="/learn/data-systems/downstreams/">know your consumers</a>.'))}
</div>"""
    return url, body, FAQ1


# =============================================================== PAGE 2: Power BI and Fabric
FABRIC_ROWS = [
    ("Capacity", "You buy a capacity size (F2 up to F2048). Every Fabric job, including Power BI queries and refreshes, spends capacity units (CU) from it."),
    ("Smoothing", "Short spikes are spread out: interactive work (report clicks) over at least 5 minutes, background work (refreshes) over 24 hours. You pay for the average, not the peak."),
    ("Throttling", "If you keep borrowing from the future: after about 10 minutes of overuse, report clicks are delayed; after about 60 minutes, they are rejected; after 24 hours, refreshes are rejected too. Watch it in the Fabric Capacity Metrics app."),
    ("Licences", "Below F64, every viewer needs a Pro (or Premium Per User) licence. From F64 up, viewers with a free licence can read content; authors still need Pro."),
    ("OneLake", "One data lake per company, storing tables as Delta Parquet. Shortcuts point to ADLS, S3 or GCS without copying. Mirroring brings other databases in, including Azure Databricks Unity Catalog catalogs."),
    ("Workspaces", "Folders of items (semantic models, reports, lakehouses) with roles: Admin, Member, Contributor, Viewer. Only Viewers are held by RLS."),
]

MODE_ROWS = [
    ("Import", "Refresh reads the source and stores a compressed, column-by-column copy in VertiPaq memory.", "Fastest interaction; full DAX; works offline from the source.", "Stale between refreshes; refresh time and memory; Unity Catalog RLS is lost."),
    ("DirectQuery", "Each visual becomes SQL sent to the Databricks SQL warehouse at click time.", "Always fresh; no copy; Unity Catalog RLS applies with single sign-on.", "Every click costs warehouse time; slower; some DAX gets heavy; limits on rows and connections."),
    ("Dual", "A table that can act as Import or DirectQuery depending on the query.", "Small dimension tables in composite models.", "Must be refreshed like Import."),
    ("Composite + aggregations", "Import a small aggregate table, keep the big fact in DirectQuery; Power BI answers from the aggregate when it can.", "Big data with fast summary pages.", "The most moving parts; aggregate must match the detail."),
    ("Direct Lake", "Power BI reads the Delta Parquet files in OneLake straight into VertiPaq memory, column by column, when first needed. 'Refresh' only points the model at the newest Delta version (called framing).", "Import-like speed without copying; fresh after framing.", "Data must be in OneLake; guardrails per capacity size; Databricks-written files lack V-Order and read slower; Unity Catalog rules do not apply."),
]

DL_ROWS = [
    ("Shortcut from OneLake to the Databricks storage (ADLS on Azure, S3 on AWS)", "No copy; Direct Lake reads the files. On AWS the reads cross clouds and S3 charges data leaving AWS.", "Unity Catalog permissions are not checked on file reads: whoever can read the shortcut reads every row. Protect with Power BI roles or OneLake security.", "Pursue only on Azure, for non-sensitive or Power-BI-secured data"),
    ("Mirrored Azure Databricks catalog in Fabric", "Fabric reads Unity Catalog metadata and makes shortcuts for you.", "Tables with row filters or column masks are not mirrored (check the current limits).", "Pursue for non-sensitive gold on Azure"),
    ("Copy gold into a Fabric lakehouse with a pipeline", "A second copy, V-Ordered for Fabric.", "Two copies to keep in sync; drift risk.", "Drop unless the company is moving to Fabric"),
    ("Skip Direct Lake; use DirectQuery with single sign-on or Import", "Data stays in Databricks.", "DirectQuery cost and speed, or Import staleness.", "Pursue on AWS and GCP"),
]

PBI_RLS = [
    ("Static role", "A DAX filter with a fixed value, e.g. [region] = \"North\"; one role per region.", "Many roles to maintain; grows badly.", "Drop beyond a handful"),
    ("Dynamic role", "One role; the filter compares a column with USERPRINCIPALNAME() through an entitlements table.", "Needs the entitlements table and a single-direction relationship from it.", "Pursue"),
    ("Object-level security (OLS)", "Hides whole tables or columns from a role (e.g. salary).", "Reports that use the hidden column break for that role.", "Pursue for sensitive columns"),
    ("Embedded, 'app owns data'", "Your app passes an effective identity (user name and roles) in the embed token.", "Your app must pass the right identity every time.", "Pursue for customer-facing embedding"),
    ("DirectQuery with single sign-on", "The user's Entra ID identity is passed to Databricks, so Unity Catalog filters apply as well. Simple on Azure Databricks; on AWS and GCP check current OAuth support.", "Both rule sets apply; the user sees the overlap.", "Pursue for sensitive, fresh data"),
]

PBI_TROUBLE = [
    ("A report page is slow", "Performance Analyzer in Power BI Desktop: time per visual split into DAX query, visual display and other.", "Copy the slowest visual's DAX into DAX Studio."),
    ("One DAX query is slow", "DAX Studio with Server Timings and the query plan: formula engine vs storage engine time, number of storage engine queries.", "High formula-engine time: rewrite the DAX (iterators over big tables, nested CALCULATE). Many storage-engine queries: simplify the model or measure."),
    ("The model is big or refresh runs out of memory", "VertiPaq Analyzer (in DAX Studio or Tabular Editor): size per table and column, cardinality.", "Drop unused columns; split date and time; remove high-cardinality IDs and GUIDs; turn off auto date/time; prefer measures to calculated columns."),
    ("DirectQuery is slow", "Databricks query history and query profile for the SQL Power BI sent: bytes scanned, files pruned, Photon, queueing.", "Cluster gold on filter columns; add aggregation tables; reduce visuals per page; set 'assume referential integrity' on relationships to get inner joins."),
    ("Everyone is slow at 9 a.m.", "Fabric Capacity Metrics app: CU per item and operation, throttling, overage.", "Move refreshes off peak; fix the heaviest model; size up the capacity or split workloads across capacities."),
    ("Refresh is slow or fails", "Refresh history; Power Query diagnostics; Databricks query history for the refresh queries.", "Incremental refresh with partitions; fold transformations into SQL (or do them in gold); use a service principal, not a personal OAuth token that expires."),
    ("Good-practice audit", "Tabular Editor Best Practice Analyzer; Fabric workspace monitoring (logs into an Eventhouse) or Log Analytics for query logs.", "Run the analyzer in CI and fail on serious rules."),
]

PBI_TEST = [
    ("Model as code", "Save as Power BI Project (PBIP) with the model in TMDL text files; keep it in git through Fabric Git integration.", "Every change is reviewed as a diff."),
    ("Rules check", "Tabular Editor Best Practice Analyzer from the command line in CI.", "Catches bidirectional relationships, missing formats, unused columns before merge."),
    ("Same-number test", "Run each measure through the executeQueries REST API, the XMLA endpoint, or semantic link (sempy) in a Fabric notebook; run the matching metric view in Databricks; compare.", "Fails the build if Power BI and Databricks disagree."),
    ("RLS test", "executeQueries with impersonatedUserName (or 'View as role' by hand) for test users per region; assert row counts.", "Proves a North user sees only North, and matches the Unity Catalog row count for the same user."),
    ("Refresh test", "Deploy to a test workspace through deployment pipelines and refresh against test data.", "Catches broken sources and timeouts before production."),
    ("Performance test", "DAX Studio benchmark per key query; budget per page.", "Stops a slow change from shipping."),
]

PBI_LIMITS = [
    ("Model size", "1 GB per model on Pro; on Fabric the memory per model grows with capacity size (about 25 GB on F64, check the current table)."),
    ("Refresh", "8 scheduled refreshes a day on Pro, 48 on capacity; a refresh times out after about 2 hours on Pro and 5 hours on capacity."),
    ("DirectQuery", "About 1 million rows per intermediate result by default; a limited number of parallel connections to the source per model."),
    ("Direct Lake guardrails", "Rows per table, Parquet files and row groups per table, and memory per model, each scaling with capacity size (around 1.5 billion rows per table on F64, check)."),
    ("RLS", "Not applied to workspace Admins, Members and Contributors; only DAX filters on rows, no masking by value (use OLS to hide columns)."),
]

PBI_PROD = [
    ("Refresh fails at 3 a.m. because the person whose login it used left", "Use a service principal for data source credentials; alert on refresh failure."),
    ("Capacity throttled by one bad model; all reports slow", "Capacity Metrics alerts; separate capacities for critical and self-service work; fix the heavy model."),
    ("Ten copies of 'Sales model' made by analysts, each a little different", "One certified, endorsed thin model; others build reports on it (live connection), not new models."),
    ("A member of the workspace sees every row", "Readers get the Viewer role or an app; members are only the build team."),
    ("Export to Excel takes all rows out of the governed world", "Limit export in tenant settings for sensitive models; sensitivity labels."),
    ("DirectQuery bill on Databricks doubles", "Watch warehouse cost by query source; add aggregations; switch summary pages to Import."),
    ("Direct Lake falls back to DirectQuery silently and gets slow", "Watch the fallback in query traces; stay inside guardrails; run OPTIMIZE to cut file counts."),
    ("Private networking blocks the cloud service from Databricks", "Use the virtual network data gateway or a private-link setup, and plan it early."),
]

FAQ2 = [
    ("How does Direct Lake work with data in Databricks?", "Direct Lake reads Delta Parquet files in OneLake into memory. Databricks data reaches OneLake through a shortcut to its storage or through a mirrored Azure Databricks catalog. Unity Catalog row filters and masks do not apply to those file reads, so secure the data in Power BI or OneLake, and expect slower loads because Databricks does not write V-Order."),
    ("Why is my Power BI report slow?", "Find the slow visual with Performance Analyzer, then the slow part with DAX Studio Server Timings. Formula-engine time means the DAX needs rewriting; storage-engine or SQL time means the model, the data size or the source is the problem."),
    ("How do you test Power BI?", "Keep the model as code (PBIP and TMDL in git), run Best Practice Analyzer in CI, test each measure against the source (same-number test), test RLS with impersonated users, refresh in a test workspace, and benchmark key queries before release."),
    ("Does Power BI RLS apply to workspace members?", "No. Admins, Members and Contributors of the workspace see all rows. Only users with the Viewer role, or app audiences, are filtered."),
]


def page_pbi():
    url = SITE + BASE + "power-bi/"
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/concepts/semantic-layer/">BI and analytics</a> › <a href="{BASE}">Power BI vs Databricks AI/BI</a> › Power BI in depth</p>
<p class="eyebrow" style="margin-top:22px">BI and analytics · free guide · page 2 of 3</p>
<h1>Power BI and Fabric, in depth</h1>
<p class="lede">How the new Fabric-based Power BI works, what happens inside a query, how it handles volume and row-level security when the data is in a Databricks lakehouse, and how to troubleshoot, benchmark and test it before production.</p>
<div class="bi">{tabs("power-bi/")}
<ul class="toc"><li><a href="#fabric">How Fabric works</a></li><li><a href="#inside">Inside a Power BI query</a></li><li><a href="#modes">Storage modes and volume</a></li><li><a href="#direct-lake">Direct Lake on Databricks data</a></li><li><a href="#rls">How RLS works in Power BI</a></li><li><a href="#trouble">Troubleshooting slow reports</a></li><li><a href="#bench">Benchmarking</a></li><li><a href="#test">Testing</a></li><li><a href="#limits">Limits</a></li><li><a href="#prod">Production problems</a></li></ul>

{sec("fabric", "The new Power BI", "How Fabric works",
p("Power BI is now one part of Microsoft Fabric. Fabric is a software-as-a-service data platform: you do not run servers, you buy a capacity and every Fabric workload spends from it. Power BI Premium capacities (P sizes) have been replaced by Fabric capacities (F sizes).")
+ fig(d_fabric(), "One capacity, many workloads, one lake. Power BI is the reporting workload on top.")
+ vtable(["Idea", "What it means"], FABRIC_ROWS))}

{sec("inside", "Internals", "Inside a Power BI query",
fig(d_pbi_engine(), "Every visual sends a DAX query. Two engines answer it.")
+ p("<b>VertiPaq</b>, the in-memory engine, stores each column separately. It replaces each distinct value with a small number (dictionary encoding) and stores runs of the same number once (run-length encoding). So a column with few distinct values (country, status) shrinks enormously, and a column with millions of distinct values (timestamps to the second, GUIDs, free text) barely shrinks. <b>Cardinality decides model size and speed.</b>",
    "The <b>formula engine</b> works out what the DAX means and runs on one thread. The <b>storage engine</b> scans compressed columns on many threads, or, in DirectQuery, turns the request into SQL for Databricks. Both cache results, which is why the second run of a query is faster (test both cold and warm)."))}

{sec("modes", "Volume", "Storage modes and how volume is handled",
fig(d_pbi_modes(), "Where the data sits decides speed, freshness, cost and whether Unity Catalog security applies.")
+ vtable(["Mode", "How it works", "Good at", "Watch out for"], MODE_ROWS)
+ p("<b>Rules of thumb on a lakehouse:</b> Import for gold aggregates up to tens of millions of rows that refresh a few times a day; incremental refresh with partitions for bigger Import tables; DirectQuery with aggregation tables for billions of rows or minute-level freshness; Direct Lake only when the data is in OneLake already."))}

{sec("direct-lake", "Direct Lake", "Direct Lake when the data is in Databricks",
vtable(["Route", "How", "Catch", "Verdict"], DL_ROWS)
+ '<div class="warn"><b>Security note.</b> Direct Lake and shortcuts read files, not tables through Unity Catalog. Row filters and column masks are not applied. If the data is sensitive, either secure it in Power BI (roles and OLS) and OneLake, or stay on DirectQuery with single sign-on.</div>')}

{sec("rls", "Security", "How row-level security works in Power BI",
p("A role is a DAX filter on a table, written in the model. When a user opens a report, Power BI adds the filter for each role the user belongs to, and the filter flows along relationships from the 'one' side to the 'many' side. Several roles add up (a user in North and South roles sees both). Members are assigned in the service, ideally as Entra ID groups.")
+ vtable(["Kind", "How", "Catch", "Verdict"], PBI_RLS)
+ p("For the full both-sides design with Unity Catalog, see <a href=\"" + BASE + "#rls-both\">How RLS works on both sides</a>."))}

{sec("trouble", "When it is slow", "Troubleshooting Power BI performance",
vtable(["Symptom", "Tool to find the cause", "Usual fixes"], PBI_TROUBLE))}

{sec("bench", "Benchmarking", "How to benchmark Power BI",
ul(["<b>Set a budget first</b>: for example, every page renders in under 3 seconds at the 95th percentile, with 50 people using it at once, and costs under a set number of capacity units.",
    "<b>Single query</b>: DAX Studio's benchmark runs a query several times with a cold cache and a warm cache and reports both. Record the storage-engine and formula-engine split.",
    "<b>Whole page</b>: Performance Analyzer, exported as JSON, gives the time per visual. Keep the file per release to compare.",
    "<b>Many users</b>: Microsoft's Realistic Load Test Tool replays report sessions in browsers; watch the Capacity Metrics app (CU and throttling) and, for DirectQuery, the Databricks warehouse (queueing, clusters, p95 latency).",
    "<b>Same data, every run</b>: benchmark on a fixed copy of production-sized data, otherwise you compare data growth, not changes."]))}

{sec("test", "Testing", "How Power BI testing works", vtable(["Test", "How", "What it proves"], PBI_TEST))}
{sec("limits", "Limits", "Limits to know (check the current numbers)", C.table(["Area", "Limit"], PBI_LIMITS))}
{sec("prod", "Production", "Production-grade problems and their fixes", C.table(["Problem", "Fix"], PBI_PROD))}
{sec("faq", "FAQ", "Questions people ask", C.faq(FAQ2))}
{sec("next", "Read on", "The other pages", p(f'<a href="{BASE}">The decision</a> · <a href="{BASE}ai-bi/">Databricks AI/BI, in depth</a>'))}
</div>"""
    return url, body, FAQ2


# =============================================================== PAGE 3: Databricks AI/BI
AIBI_PARTS = [
    ("Dashboard", "A file (.lvdash.json) holding datasets, pages and widgets. Drafts are edited; a published copy is what viewers open."),
    ("Dataset", "A SQL query or a metric view. Widgets aggregate on top of it, and Databricks pushes that aggregation into SQL, so only small results travel to the browser."),
    ("SQL warehouse", "The compute that runs every widget query. Serverless starts in seconds, uses Photon, adds clusters when queries queue, and keeps a result cache."),
    ("Unity Catalog", "Checks the person's rights on each table and adds row filters and column masks, every query."),
    ("Sharing", "Share with users and groups in the Databricks account, even ones without workspace access; schedules email snapshots; dashboards can be embedded in other apps."),
    ("Genie space", "A set of tables or metric views, plus instructions, example SQL and trusted functions. An LLM turns a question into SQL, runs it as the user, and shows the result. Benchmarks measure its accuracy; an API lets apps and agents ask it."),
]

AIBI_RLS = [
    ("Viewer credentials (no embedded credentials)", "Each widget query runs as the viewer, so Unity Catalog filters apply per person.", "Results are not shared between viewers, so more warehouse work.", "Pursue for sensitive data"),
    ("Embedded (publisher's) credentials", "Every query runs as the publisher; viewers see what the publisher sees. Results are shared, so it is cheaper.", "Leaks data if the publisher can see more than the viewers.", "Pursue only for data everyone may see"),
    ("Row filters and column masks", "SQL functions attached to tables, using current_user() and is_account_group_member(), often with an entitlements table.", "Keep the function simple (a lookup), or every query slows down.", "Pursue"),
    ("Tag-based policies (attribute-based access control)", "One policy applies to every table or column carrying a tag such as pii.", "Newer; check its status in your region.", "Pursue when available, to avoid one filter per table"),
    ("Dynamic views with is_account_group_member()", "The older way: a view that filters, readers get only the view.", "One view per table to maintain; easy to bypass via the table.", "Drop for new work"),
]

AIBI_TROUBLE = [
    ("A widget is slow", "Query history filtered by the dashboard; the query profile for that query: bytes scanned, files pruned, spill, time spent queued.", "Cluster gold on the filter columns; build a pre-aggregated table or materialized view; avoid SELECT * datasets."),
    ("Slow only in the morning", "Warehouse monitoring: queued queries, number of clusters running.", "Raise max clusters; pre-warm with a schedule; spread refresh schedules."),
    ("First open is slow", "Cold start of the warehouse.", "Serverless (seconds), or keep a warehouse warm during working hours."),
    ("Cost is climbing", "system.billing.usage and system.query.history by dashboard and user.", "Publish non-sensitive dashboards with shared credentials; remove auto-refresh; size the warehouse right."),
    ("Genie gives wrong answers", "Genie benchmarks and the SQL it generated.", "Point it at metric views; add instructions, synonyms and example SQL; fewer, cleaner tables."),
]

AIBI_TEST = [
    ("Dashboards as code", "Keep .lvdash.json files in Git folders and deploy with Databricks Asset Bundles from dev to test to prod.", "Every change is reviewed and repeatable."),
    ("Same-number test", "Query each dataset and the metric view with the same filters; compare.", "Dashboards and Genie agree with the certified numbers."),
    ("RLS test", "Run the same query as test users or service principals in different groups; assert row counts and masked columns.", "A North user sees only North; matches the Power BI test for the same user."),
    ("Genie accuracy", "Genie benchmarks: questions with known-correct SQL, run on every change to the space.", "Accuracy does not slip when someone edits instructions."),
    ("Performance test", "Replay the dashboard's SQL from query history with many threads (Python with the Databricks SQL connector, JMeter or Locust); measure p50 and p95, queue time and DBUs; repeat with the result cache off (SET use_cached_result = false).", "The dashboard stays inside its time and cost budget."),
]

AIBI_LIMITS = [
    ("Formatting", "Fewer chart types and less control than Power BI; no custom visuals; no pixel-perfect paginated reports (snapshots by email instead)."),
    ("Modelling", "No in-tool model language like DAX; logic goes in SQL, metric views or dashboard-level calculations. Good for one truth, less freedom for analysts."),
    ("Result size", "Each widget's result has a size cap (tens of thousands of rows; check the current number). Fine for charts, not for exporting raw data."),
    ("Always live", "No import mode: every open runs queries, so cost follows usage. The result cache and shared credentials soften it."),
    ("Office tools", "Excel and Teams integration is weaker than Power BI's (check the current Excel connector and embedding options)."),
    ("Genie", "A limit on tables per space (check); answers are generated, so they need curation, benchmarks and a human check for important decisions."),
]

AIBI_PROD = [
    ("A sensitive dashboard published with embedded credentials", "Review every published dashboard's credential setting; make viewer credentials the default for gold tables with row filters."),
    ("Publisher leaves; dashboard stops refreshing", "Owners are groups or service principals, set in the bundle."),
    ("Warehouse cost spike from auto-refresh and many viewers", "Budgets and alerts on system.billing.usage; turn off frequent auto-refresh; shared credentials where allowed."),
    ("Dashboards built on silver, slow and inconsistent", "Datasets read only gold and metric views; a review check blocks silver."),
    ("Genie answer used in a decision without checking", "Show the SQL; certify questions in benchmarks; keep Genie to metric views."),
    ("Monday 9 a.m. queue", "Max clusters sized for the peak; Intelligent Workload Management on serverless; schedules staggered."),
    ("Dashboard sprawl, nobody knows which is official", "Certified folder and naming; owners; delete unused dashboards found through query history."),
]

FAQ3 = [
    ("Does AI/BI respect Unity Catalog row-level security?", "Yes, when the dashboard runs with viewer credentials: each widget query runs as the viewer and Unity Catalog adds the row filter. With embedded (publisher's) credentials, everyone sees what the publisher sees."),
    ("How does AI/BI handle large data?", "It never copies data. Each widget sends SQL to a SQL warehouse, which scans Delta tables with Photon and returns only the small aggregated result. Speed depends on the warehouse size and on how well gold is clustered and pre-aggregated."),
    ("What are the limitations of Databricks AI/BI dashboards?", "Fewer visual types and formatting options than Power BI, no paginated reports, no DAX-style modelling in the tool, caps on result size per widget, weaker Excel and Teams integration, and every view costs warehouse time."),
    ("How do you test AI/BI dashboards?", "Keep them as code in Databricks Asset Bundles, test datasets against metric views, test RLS by running queries as different test users, run Genie benchmarks, and replay dashboard SQL under load for performance."),
]


def page_aibi():
    url = SITE + BASE + "ai-bi/"
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/concepts/semantic-layer/">BI and analytics</a> › <a href="{BASE}">Power BI vs Databricks AI/BI</a> › AI/BI in depth</p>
<p class="eyebrow" style="margin-top:22px">BI and analytics · free guide · page 3 of 3</p>
<h1>Databricks AI/BI, in depth</h1>
<p class="lede">How AI/BI dashboards and Genie run on your lakehouse, how row-level security and volume work, how to troubleshoot, benchmark and test them, their limits, and what goes wrong in production.</p>
<div class="bi">{tabs("ai-bi/")}
<ul class="toc"><li><a href="#how">How it works</a></li><li><a href="#volume">How volume is handled</a></li><li><a href="#rls">How RLS works</a></li><li><a href="#trouble">Troubleshooting</a></li><li><a href="#test">Testing and benchmarking</a></li><li><a href="#limits">Limits</a></li><li><a href="#prod">Production problems</a></li></ul>

{sec("how", "Internals", "How an AI/BI dashboard works",
fig(d_aibi(), "No copy and no separate engine: the dashboard is a set of SQL queries the warehouse runs against Unity Catalog tables.")
+ C.table(["Part", "What it does"], AIBI_PARTS))}

{sec("volume", "Volume", "How volume is handled",
p("AI/BI has no in-memory copy. When a viewer opens a page, each widget's aggregation is turned into SQL and sent to the SQL warehouse. Photon scans only the columns and files needed (file pruning uses the clustering and statistics on the Delta tables) and returns a small result to the browser. So data size is limited by how fast the warehouse can scan it, not by memory in the BI tool.",
  "Three things keep it fast at large volume: <b>gold aggregates or materialized views</b> sized for the dashboard, <b>liquid clustering</b> on the columns people filter by (date, region, plant), and <b>enough clusters</b> on the warehouse for the busiest hour. The result cache answers a repeated query without scanning again; it works best when viewers share credentials."))}

{sec("rls", "Security", "How row-level security works in AI/BI",
vtable(["Choice", "How", "Catch", "Verdict"], AIBI_RLS)
+ p("Metric views inherit the row filters of their tables, and Genie runs as the asking user, so one set of rules covers dashboards, Genie and agents. The full code is on <a href=\"" + BASE + "#rls-both\">the decision page</a>."))}

{sec("trouble", "When it is slow", "Troubleshooting AI/BI performance", vtable(["Symptom", "Where to look", "Usual fixes"], AIBI_TROUBLE))}
{sec("test", "Testing", "Testing and benchmarking AI/BI", vtable(["Test", "How", "What it proves"], AIBI_TEST)
+ p("Set the same kind of budget as for Power BI: page under 3 seconds at the 95th percentile at expected peak users, and a monthly DBU ceiling per dashboard."))}
{sec("limits", "Limits", "Limitations (check the current numbers)", C.table(["Area", "Limit"], AIBI_LIMITS))}
{sec("prod", "Production", "Production-grade problems and their fixes", C.table(["Problem", "Fix"], AIBI_PROD))}
{sec("faq", "FAQ", "Questions people ask", C.faq(FAQ3))}
{sec("next", "Read on", "The other pages", p(f'<a href="{BASE}">The decision</a> · <a href="{BASE}power-bi/">Power BI and Fabric, in depth</a> · <a href="/writing/genie-metric-views/">Genie and metric views</a>'))}
</div>"""
    return url, body, FAQ3


TITLES = {
    "": ("Power BI vs Databricks AI/BI, or both, on a lakehouse",
         "Where the semantic model and row-level security should live when data is in a Databricks lakehouse, how RLS works on both sides, volume, cost comparison and the recommended architecture."),
    "power-bi/": ("Power BI and Fabric, in depth: internals, Direct Lake, RLS, testing",
                  "How Fabric and Power BI work inside, storage modes and Direct Lake on Databricks data, RLS mechanics, troubleshooting, benchmarking, testing, limits and production problems."),
    "ai-bi/": ("Databricks AI/BI dashboards and Genie, in depth",
               "How Databricks AI/BI dashboards and Genie run, row-level security, volume, troubleshooting, benchmarking, testing, limitations and production problems."),
}


def render(slug, url, body, qa):
    title, desc = TITLES[slug]
    crumbs = [("BI and analytics", f"{SITE}/concepts/semantic-layer/"), ("Power BI vs Databricks AI/BI", SITE + BASE)]
    if slug:
        crumbs.append((title, url))
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": title, "description": desc, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}]
    head = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(title, desc, url, body, head)


def main():
    for slug, fn in (("", page_decision), ("power-bi/", page_pbi), ("ai-bi/", page_aibi)):
        url, body, qa = fn()
        out = ROOT / BASE.strip("/") / slug
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(render(slug, url, body, qa))
        print("bi ->", out / "index.html")


if __name__ == "__main__":
    main()
