"""Writes /learn/silver-to-gold/ as a short hub plus sub-pages (the old single page had grown to 290 KB).

    python3 _guides/silver_to_gold.py      (then python3 _site/nav.py and python3 _site/seo.py)

The sections still come from silver_to_gold.py and silver_to_gold_learn.py (one source of truth); this file only
decides which section lands on which page, rewrites in-page links to point at the right page, and adds the hub,
the breadcrumbs, a table of contents and previous/next links. Two pages are new and SQL-first
(silver_to_gold_sql.py): dimension examples and fact examples, run in DuckDB.
"""
import json
import re
from html import escape as E
from pathlib import Path

import silver_to_gold as S
import silver_to_gold_sql as SQL
from gold_harness_spec import CSS
import silver_to_gold_learn as LEARN

wb = S.wb
SITE = wb.SITE
ROOT = S.ROOT
BASE = "/learn/silver-to-gold/"
DATE = "2026-11-20"

# slug, short name, page title, description, lede, section ids (None = built from SQL examples), group, hub blurb
PAGES = [
    dict(slug="worked-example", short="The worked example", group="learn",
         title="Silver to gold, worked example: a tyre company over two nights",
         desc="One tiny tyre company followed through two nightly runs, a crash and a careless join, with the real tables at every step: watermarks, windows, keys as of the event, completeness, restatements and checks.",
         lede="Read this page first if the rest feels like too much. Every idea in the silver-to-gold layer happens here to a handful of real rows, in a picture and a table. The next page continues with a crash, a careless join and the tests.",
         ids=["a-story", "a-night", "a-night1", "a-night2"],
         blurb="One small company, two nights, every idea shown on real rows. Start here."),
    dict(slug="crash-join-tests", short="When it goes wrong, and the tests", group="learn",
         title="Silver to gold: a crash, a careless join, and how the build is tested",
         desc="What happens when the machine dies halfway through a run, what stops a careless join from doubling a number, and how each build is tested with small tables in and expected rows out.",
         lede="The worked example continued: a crash halfway, a careless join that the checks stop, and the small-tables-in, expected-rows-out tests behind every build.",
         ids=["a-crash", "a-careless", "a-tests"],
         blurb="A crash halfway, a careless join, and the tests behind every build."),
    dict(slug="kinds-of-fact", short="The six kinds of fact", group="learn",
         title="The six kinds of fact table, from zero",
         desc="Transaction, periodic snapshot, accumulating snapshot, factless, aggregate and consolidated facts: why there are six, everyday analogies, one bank over three days, nine businesses and four questions to pick the kind.",
         lede="Why one fact table is not enough, with everyday pictures first, then one bank over three days, nine businesses, and four questions that pick the kind.",
         ids=["b-feel", "b-why", "b-bank", "b-domains", "b-pick", "b-add", "b-confuse"],
         blurb="Why there are six, with a bank and nine businesses, and how to pick."),
    dict(slug="fact-examples", short="Fact examples in SQL", group="sql", sql="fact",
         title="Fact table examples in SQL: eight kinds, each run and checked",
         desc="Eight fact examples in SQL with silver tables in and gold tables out, every result from a real run: transaction, periodic snapshot, accumulating snapshot, factless, aggregate, consolidated, allocated header amounts and adjustment rows.",
         lede="Eight fact tables written as plain SQL on tiny tables. Each shows the silver in, the SQL, the gold out, when to use it and the trap that catches people. Every result is from a real run.",
         ids=None, blurb="Eight facts in SQL: transaction, snapshots, factless, aggregate, plan against actual, allocation, adjustments."),
    dict(slug="dimension-examples", short="Dimension examples in SQL", group="sql", sql="dim",
         title="Dimension table examples in SQL: eleven kinds, each run and checked",
         desc="Eleven dimension examples in SQL with silver tables in and gold tables out, every result from a real run: SCD Type 1, 2 and 3, mini-dimension, date, role-playing, junk, degenerate, bridge, hierarchy and inferred members.",
         lede="Eleven dimension tables written as plain SQL on tiny tables: overwrite, history, previous value, date, junk, bridge and more. Every result is from a real run.",
         ids=None, blurb="Eleven dimensions in SQL: Type 1, 2, 3, date, junk, bridge, hierarchy, late dealers."),
    dict(slug="building-each-kind", short="Building each kind of fact", group="learn",
         title="Building each kind of fact: reader, processor, writer",
         desc="Every gold build has three parts: a reader that finds what changed, a processor that holds the business rule, and a writer that replaces windows or merges by key. How each of the six fact kinds fills them in, with tested code.",
         lede="The three parts of every build, then each of the six kinds with its reader, processor and writer, the traps, and the tested code.",
         ids=["b-rpw", "b-kinds"], blurb="Reader, processor, writer for each fact kind, with the tested code."),
    dict(slug="bookmark", short="Who makes the bookmark?", group="learn",
         title="Who makes the bookmark, and can gold miss a change?",
         desc="Seven ways of writing silver and four ways of reading it, tested: which bookmarks miss updates, deletes and out-of-order commits, what a full overwrite of silver does to the change feed, and why the table's own change log is the safe bookmark.",
         lede="Incremental loading is only as safe as its bookmark. This page tests seven ways silver can be written against four ways gold can read it, and shows which misses what.",
         ids=["a-bookmark"], blurb="Can incremental loading miss a change? Tested seven ways."),
    dict(slug="declarative-pipeline", short="Databricks declarative pipeline?", group="decide",
         title="Can silver to gold be a Databricks declarative pipeline?",
         desc="Whether the silver-to-gold layer can be a Lakeflow declarative pipeline: the example as AUTO CDC and materialized views, replayed night by night, with pros, cons and a verdict per kind of gold table.",
         lede="AUTO CDC and materialized views can build gold. Here is what the example looks like that way, what you gain, what you give up, and a verdict for each kind of gold table.",
         ids=["c-short", "c-sketch", "c-pros"], blurb="AUTO CDC and materialized views: what you gain, what you give up."),
    dict(slug="sql-and-dbt", short="The fact in SQL and dbt", group="decide",
         title="The same fact in SQL and in dbt, and our harness against dbt",
         desc="Which part of the harness uses each setting, the OTIF fact written in SQL, the same fact in dbt with three nights replayed, and our harness against dbt: pros and cons.",
         lede="The business rule is a few lines of SQL. This page shows it in SQL and in dbt, what each tool does around it, and where they differ.",
         ids=["e-matrix", "e-sql", "e-dbt", "e-vs"], blurb="The OTIF fact in SQL and in dbt, and our harness against dbt."),
    dict(slug="fact-or-dimension", short="Fact or dimension?", group="decide",
         title="Is a delivery a fact or a dimension? And what if facts are versioned?",
         desc="Whether a delivery is a fact, a dimension or neither, and three ways to handle versioned facts: current state with a restatement log, versioned rows, or adjustment rows.",
         lede="A short page on two modelling questions: what a delivery is, and what to do when facts themselves have versions.",
         ids=["f-what", "f-versions"], blurb="A delivery, and what to do when facts have versions."),
    dict(slug="rulebook-harness", short="Rulebook 1: the harness", group="rule",
         title="The harness rulebook 1: steps, one harness for every fact, troubleshooting",
         desc="The rulebook for the silver-to-gold harness, part one: the steps of a run, one harness for every fact kind, SQL or PySpark builds, seeing intermediate results, the row ledger and many-to-many join checks.",
         lede="The first third of the rulebook: what the harness does in a run, how one harness builds every kind of fact, and how you see inside it when numbers look wrong.",
         ids=["plain", "harness", "one", "debug"], blurb="The steps of a run, one harness for all, seeing inside it."),
    dict(slug="rulebook-loading", short="Rulebook 2: loading rules", group="rule",
         title="The harness rulebook 2: incremental loading, watermarks, windows, late data",
         desc="The rulebook for the silver-to-gold harness, part two: incremental loading, watermarks, grain and windows, completeness and restatements, late facts and late dimensions, history loads, reloads and hiding a bad batch.",
         lede="The middle third of the rulebook: how a run finds what changed, which windows it rebuilds, when a window is complete, and what happens to late data.",
         ids=["incr", "watermark", "windows", "complete", "late", "history"], blurb="Incremental loads, watermarks, windows, completeness, late data."),
    dict(slug="rulebook-quality", short="Rulebook 3: testing and decisions", group="rule",
         title="The harness rulebook 3: testing, reliability, cost, decisions and FAQ",
         desc="The rulebook for the silver-to-gold harness, part three: pure functions and local tests, how the harness answers each gold problem, reliability and cost practices, whether the industry has solved it, what is built, decisions with verdicts and a FAQ.",
         lede="The last third of the rulebook: testing without a cluster, reliability and cost, what exists already, what is built, the decisions, and the questions people ask.",
         ids=["pure", "solves", "reliable", "cost", "industry", "status", "decide", "faq"], blurb="Testing, reliability, cost, what exists, decisions and the FAQ."),
]
GROUPS = [
    ("learn", "Learn it", "Start with the worked example. Everything else is easier after it.", "var(--mint-wash)"),
    ("sql", "Examples in SQL", "Dimensions and facts as plain SQL on tiny tables, every result from a real run.", "var(--butter-wash)"),
    ("decide", "Decide", "Declarative pipeline or harness, SQL or dbt, fact or dimension.", "var(--peri-wash)"),
    ("rule", "The rulebook", "For when you are building or reviewing. Three short reference pages.", "var(--rose-wash)"),
]
UNIT = {"worked-example": "A", "crash-join-tests": "A", "kinds-of-fact": "B", "building-each-kind": "B", "bookmark": "A8", "declarative-pipeline": "C", "sql-and-dbt": "D", "fact-or-dimension": "E"}

HUB_TITLE = "Silver to gold: the harness that builds facts and dimensions"
HUB_DESC = ("How gold facts and dimensions are built from silver every night without losing, doubling or silently changing a number: "
            "a worked example, the six kinds of fact, SQL examples of every dimension and fact kind, and the harness rulebook, one short page each.")


def chunks(html):
    parts = re.split(r'(?=<section id=")', html)
    out = {}
    for p in parts:
        m = re.match(r'<section id="([^"]+)"', p)
        if not m:
            assert not p.strip(), p[:80]
            continue
        assert p.count("<section") == p.count("</section>") and p.rstrip().endswith("</section>"), m.group(1)
        out[m.group(1)] = p.strip()
    return out


def words(html):
    return len(re.sub(r"<[^>]+>", " ", html).split())


def h2_of(sec):
    m = re.search(r"<h2>(.*?)</h2>", sec, re.S)
    return re.sub(r"<[^>]+>", "", m.group(1)) if m else ""


def fix_links(html, own, where):
    """Point #id links at the page that now holds the section."""
    def sub(m):
        i = m.group(1)
        if i in own:
            return m.group(0)
        if i in where:
            return f'href="{BASE}{where[i]}#{i}"' if where[i] else f'href="{BASE}#{i}"'
        raise SystemExit(f"unknown in-page link #{i}")
    return re.sub(r'href="#([A-Za-z0-9_-]+)"', sub, html)


def crumb(short=None):
    last = f'<a href="{BASE}">Silver to gold</a> › {E(short)}' if short else "Silver to gold"
    return (f'<p class="crumbs"><a href="/">Home</a> › <a href="/data-engineering/">Data engineering</a> › '
            f'<a href="/learn/gold-data-modelling/">Gold data modelling</a> › {last}</p>')


def toc_html(html, ids):
    items = []
    for i in ids:
        sec = re.search(r'<section id="%s".*?</section>' % re.escape(i), html, re.S).group(0)
        items.append(f'<li><a href="#{i}">{E(h2_of(sec) or i)}</a></li>')
    return '<ul class="toc">' + "".join(items) + "</ul>" if len(ids) > 2 else ""


def ld(title, desc, url, crumbs, faq=None):
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    out = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": title, "description": desc, "url": url, "inLanguage": "en",
            "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
            "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
           {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}]
    if faq:
        out.append({"@context": "https://schema.org", "@type": "FAQPage",
                    "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})
    return "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in out)


def main():
    secs = chunks(S.sections_html())
    # the new SQL pages carry their own sections
    sql_secs = {"fact": SQL.fact_sections(), "dim": SQL.dimension_sections()}
    where = {i: "" for i in ("start", "next")}
    for p in PAGES:
        if p["ids"] is None:
            p["html"] = sql_secs[p["sql"]]
            p["ids"] = list(chunks(p["html"]).keys())
        else:
            p["html"] = "\n".join(secs[i] for i in p["ids"])
        for i in p["ids"]:
            where[i] = f'{p["slug"]}/'
    used = {i for p in PAGES for i in p["ids"]} | {"start", "next"}
    missing = [i for i in secs if i not in used]
    assert not missing, f"sections with no page: {missing}"
    for p in PAGES:
        p["min"] = max(1, round(words(p["html"]) / 220))
    faq = S.faq_items()

    # ---------------------------------------------------------------- hub
    glossary = secs["start"].split("<h3>Words you will meet</h3>", 1)[1].rsplit("</section>", 1)[0]
    cards = ""
    for g, name, note, wash in GROUPS:
        cards += f'<h3>{E(name)}</h3><p class="note" style="margin:-2px 0 6px">{E(note)}</p><div class="roles" style="margin-top:8px">'
        for p in [x for x in PAGES if x["group"] == g]:
            tag = (f"Part {UNIT[p['slug']]} · " if p["slug"] in UNIT else "") + f"{p['min']} min read"
            cards += (f'<div class="role" style="--wash:{wash}"><h3><a href="{BASE}{p["slug"]}/">{E(p["short"])}</a></h3>'
                      f'<p>{E(p["blurb"])}</p><div class="pl" style="margin-top:auto">{E(tag)}</div></div>')
        cards += "</div>"
    hub = f"""{crumb()}
<p class="eyebrow" style="margin-top:22px">Data engineering · guide</p>
<h1>{E(HUB_TITLE)}</h1>
<p class="lede"><a href="/learn/gold-data-modelling/">Gold data modelling</a> said what to build: facts and dimensions. This is how to build them from silver every night, without losing, doubling or silently changing a number, and without the cost growing with history. It is split into short pages, so you can read one at a time.</p>
<div class="gh">
<div class="box"><b>In one paragraph.</b> One harness builds every gold table the same way. It reads only what changed in silver since its bookmark, works out which windows of the fact (days, months, hours) those changes touch, rebuilds just those windows with a small pure build per fact, looks up keys as of each event, checks everything before writing, replaces the windows, logs any number that changed after it was published, and moves the bookmark last. Because the build is pure, it is tested on a laptop with small tables and with a whole synthetic company that plants problems on purpose.</div>
<section id="start" class="part"><p class="eyebrow">Start here</p><h2>Which page do I read?</h2>
<div class="start"><p><b>If your head is spinning, read one page and stop: <a href="{BASE}worked-example/">the worked example</a>.</b> It follows one tiny tyre company through two nights, and every idea shows up as something that happens to real rows.</p>
<p><b>If you think in SQL, go to the SQL examples:</b> <a href="{BASE}dimension-examples/">eleven dimensions</a> and <a href="{BASE}fact-examples/">eight facts</a>, each as silver in, SQL, gold out.</p>
<p><b>If you are building or reviewing</b>, use the three rulebook pages. They are reference, not a story.</p></div>
{cards}
<h3>Words you will meet</h3>{glossary}</section>
{S.next_html()}
</div>"""
    hub_head = CSS + LEARN.EXTRA_CSS + ld(HUB_TITLE, HUB_DESC, f"{SITE}{BASE}", [("Data engineering", f"{SITE}/data-engineering/"), ("Gold data modelling", f"{SITE}/learn/gold-data-modelling/"), ("Silver to gold", f"{SITE}{BASE}")])
    out = ROOT / "learn" / "silver-to-gold"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(wb.page(HUB_TITLE, HUB_DESC, f"{SITE}{BASE}", hub, hub_head))
    print("hub ->", out / "index.html", len(hub) // 1024, "KB")

    # ---------------------------------------------------------------- sub pages
    for n, p in enumerate(PAGES):
        own = set(p["ids"])
        url = f"{SITE}{BASE}{p['slug']}/"
        toc = toc_html(p["html"], p["ids"])
        body_html = fix_links(p["html"], own, where)
        prev = PAGES[n - 1] if n else None
        nxt = PAGES[n + 1] if n + 1 < len(PAGES) else None
        pn = '<div class="sib" style="margin-top:34px">' + (f'<a href="{BASE}{prev["slug"]}/">← {E(prev["short"])}</a>' if prev else "") \
            + f'<a href="{BASE}">All the pages</a>' + (f'<a href="{BASE}{nxt["slug"]}/">{E(nxt["short"])} →</a>' if nxt else "") + "</div>"
        body = f"""{crumb(p["short"])}
<p class="eyebrow" style="margin-top:22px">Silver to gold · {E(dict((g, nm) for g, nm, _, _ in GROUPS)[p["group"]])} · {p["min"]} min read</p>
<h1>{E(p["title"])}</h1>
<p class="lede">{E(p["lede"])} <span class="note">This is one page of <a href="{BASE}">Silver to gold</a>.</span></p>
<div class="gh">
{toc}
{body_html}
{pn}
</div>"""
        faq_here = faq if "faq" in own else None
        head = CSS + LEARN.EXTRA_CSS + (SQL.CSS if p["group"] == "sql" else "") + ld(
            p["title"], p["desc"], url,
            [("Data engineering", f"{SITE}/data-engineering/"), ("Gold data modelling", f"{SITE}/learn/gold-data-modelling/"), ("Silver to gold", f"{SITE}{BASE}"), (p["short"], url)], faq_here)
        d = out / p["slug"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(wb.page(p["title"], p["desc"], url, body, head))
        print(p["slug"], "->", p["min"], "min,", len(body) // 1024, "KB")


if __name__ == "__main__":
    main()
