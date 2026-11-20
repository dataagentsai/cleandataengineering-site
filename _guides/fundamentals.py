"""Data Engineering Fundamentals: a landing page at /learn/fundamentals/ and six pages under it.

    python3 _guides/fundamentals.py      (then python3 _site/nav.py and python3 _site/seo.py)

Pages: performance, cost, processing, security, storage, database-families. Content lives in
fundamentals_data.py. Each page: the data physics in plain words, a mind map of the topic, the topic
sections as tables with a verdict, the matching CostSherlock rules grouped by branch, FAQ, related.
Teach first, no jargon without a definition, no dark mode (white pages).
"""
import json
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "_paths"))
import components as C  # noqa: E402
from fundamentals_data import PAGES  # noqa: E402
from fundamentals_diagrams import FIGS  # noqa: E402

wb = C.wb
SITE = wb.SITE
BASE = "/learn/fundamentals/"
DATE = "2026-11-20"
RULE_NOTE = ("CostSherlock is our open set of cost and performance rules. Each rule below has a plain meaning here; the rule id is its name "
             "in CostSherlock.")

CSS = """<style>
  .fx .mm { display:grid; grid-template-columns:repeat(auto-fill,minmax(250px,1fr)); gap:12px; margin:14px 0 20px; }
  .fx .mm .c { border:var(--line); border-radius:var(--wob); padding:10px 14px; background:#fff; }
  .fx .mm .c h4 { font-family:var(--hand); font-weight:400; font-size:21px; margin:0 0 2px; }
  .fx .mm .c p { margin:3px 0; font-size:14.5px; } .fx .mm .c .qq { color:var(--muted); }
  .fx .centre { display:inline-block; border:2px solid #111; border-radius:999px; padding:6px 22px; font-family:var(--hand); font-size:24px; background:#fff4d6; margin:6px 0 4px; }
  .fx .phys { display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:12px; margin:12px 0; }
  .fx .phys div { border:var(--line); border-radius:var(--wob); padding:10px 14px; background:#eef3fb; font-size:15px; }
  .fx .phys b { display:block; margin-bottom:2px; }
  .fx .fig { margin:12px 0 16px; } .fx .fig svg { width:100%; height:auto; background:#fff; border:var(--line); border-radius:var(--wob); font-family:var(--hand), sans-serif; }
  .fx .fig p { font-size:13.5px; color:#555; margin:4px 2px 0; }
  .fx code { font-size:12.5px; }
  .fx .sib { display:flex; flex-wrap:wrap; gap:8px; margin:14px 0; font-size:14px; }
  .fx .sib a, .fx .sib span { border:1.5px solid #111; border-radius:999px; padding:2px 12px; text-decoration:none; color:#111; background:#fff; }
  .fx .sib span { background:#111; color:#fff; }
</style>"""


def sib(cur):
    items = "".join(f'<span>{E(p["short"])}</span>' if p["slug"] == cur else f'<a href="{BASE}{p["slug"]}/">{E(p["short"])}</a>' for p in PAGES)
    return f'<div class="sib"><a href="{BASE}">↑ All fundamentals</a>{items}</div>'


def mindmap(p):
    cards = "".join(
        f'<div class="c"><h4>{E(b)}</h4><p class="qq">{E(q)}</p><p>{E(what)}</p><p><b>First check:</b> {E(chk)}</p></div>'
        for b, q, what, chk in p["mindmap"])
    return f'<div style="text-align:center"><span class="centre">{E(p["short"])}</span></div><div class="mm">{cards}</div>'


def rules_html(p):
    out = ""
    for cat, rows in p["rules"]:
        body = "".join(f"<tr><td><code>{E(r)}</code></td><td>{E(m)}</td></tr>" for r, m in rows)
        out += f'<h3>{E(cat)}</h3><div class="tw"><table class="t"><tr><th>CostSherlock rule</th><th>What it catches, in plain words</th></tr>{body}</table></div>'
    return out


def page_for(p):
    url = f"{SITE}{BASE}{p['slug']}/"
    physics = "".join(f"<div><b>{E(a)}</b>{E(b)}</div>" for a, b in p["physics"])
    secs = ""
    toc = [("map", "The mind map")] + [(s[0], s[2]) for s in p["sections"]] + [("rules", "CostSherlock rules for this topic"), ("faq", "Questions people ask")]
    for sid, eyebrow, h2, intro, head, rows in p["sections"]:
        figs = "".join(f'<div class="fig">{sv}<p>{E(cap)}</p></div>' for sv, cap in (f() for f in FIGS.get(p["slug"], {}).get(sid, [])))
        secs += f'<section id="{sid}"><p class="eyebrow">{E(eyebrow)}</p><h2>{E(h2)}</h2><p>{E(intro)}</p>{figs}{C.table(head, rows)}</section>\n'
    nav = "".join(f'<li><a href="#{i}">{E(t)}</a></li>' for i, t in toc)
    others = " · ".join(f'<a href="{BASE}{q["slug"]}/">{E(q["short"])} fundamentals</a>' if q["slug"] != "database-families" else f'<a href="{BASE}{q["slug"]}/">Database families</a>' for q in PAGES if q is not p)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/data-engineering/">Data engineering</a> › <a href="{BASE}">Fundamentals</a> › {E(p['short'])}</p>
<p class="eyebrow" style="margin-top:22px">Data engineering fundamentals · free guide</p>
<h1>{E(p['title'])}</h1>
<p class="lede">{E(p['lede'])}</p>
<div class="fx">
{sib(p['slug'])}
<nav class="toc"><b>On this page</b><ol>{nav}</ol></nav>
<section id="physics"><p class="eyebrow">Start here</p><h2>The data physics</h2><p>Five plain facts that explain almost everything below. Read these and the rest follows.</p><div class="phys">{physics}</div></section>
<section id="map"><p class="eyebrow">The mind map</p><h2>The whole topic on one screen</h2><p>Each card is a branch. Walk them in order when you are stuck: the question tells you what the branch is about, and the first check tells you where to look.</p>{mindmap(p)}</section>
{secs}
<section id="rules"><p class="eyebrow">In practice</p><h2>CostSherlock rules for this topic</h2><p>{E(RULE_NOTE)} They are grouped by the same branches as the mind map, so a finding tells you which branch to open.</p>{rules_html(p)}</section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(p['faq'])}</section>
<section id="next"><p class="eyebrow">Related</p><h2>Where it connects</h2><p>{others} · <a href="/learn/where-data-engineering-time-goes/">Where data engineering time goes</a> · <a href="/learn/table-maintenance/">Who maintains your tables</a> · <a href="/data-engineering/">All data engineering</a></p>
<p style="font-size:14px;color:#555">The numbers and thresholds on this page are rules of thumb and orders of magnitude to build intuition, not benchmarks. Check your platform's current documentation and measure your own workload.</p></section>
</div>"""
    crumbs = [("Data engineering", f"{SITE}/data-engineering/"), ("Fundamentals", f"{SITE}{BASE}"), (p["short"], url)]
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": p["title"], "description": p["desc"], "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]}]
    head = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(p["title"], p["desc"], url, body, head)


def landing():
    url = f"{SITE}{BASE}"
    title = "Data engineering fundamentals: performance, cost, processing, security, storage, databases"
    desc = "Six plain-words guides to the fundamentals of data engineering, each as a mind map: performance, cost, processing, security, storage and database families."
    cards = "".join(
        f'<div class="card"><h3><a href="{BASE}{p["slug"]}/">{E(p["title"].split(":")[0] if ":" in p["title"] else p["short"])}</a></h3><p class="one">{E(p["desc"])}</p></div>'
        for p in PAGES)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/data-engineering/">Data engineering</a> › Fundamentals</p>
<p class="eyebrow" style="margin-top:22px">Data engineering · free guides</p>
<h1>Data engineering fundamentals</h1>
<p class="lede">The ideas every data engineer leans on, whatever the platform. Each page starts with the plain physics, shows the topic as a mind map, lists the decisions with a verdict, and links to the CostSherlock rules that catch the mistakes in practice.</p>
<div class="fx">{sib('')}<div class="cards">{cards}</div>
<section id="how"><p class="eyebrow">How to use these</p><h2>When something is wrong, pick the page by the symptom</h2>
{C.table(["Symptom", "Start with"], [("The job is slow", "Performance fundamentals"), ("The bill is high or surprising", "Cost fundamentals"), ("Results are wrong, duplicated or late", "Processing fundamentals"), ("Someone saw data they should not", "Security fundamentals"), ("Tables are slow, large or messy", "Storage fundamentals"), ("Choosing where data should live", "Database families")])}</section></div>"""
    crumbs = [("Data engineering", f"{SITE}/data-engineering/"), ("Fundamentals", url)]
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "description": desc, "url": url, "inLanguage": "en", "isAccessibleForFree": True},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}]
    head = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in ld)
    return wb.page(title, desc, url, body, head)


def main():
    out = ROOT / "learn" / "fundamentals"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(landing())
    for p in PAGES:
        d = out / p["slug"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(page_for(p))
    print("fundamentals ->", out)


if __name__ == "__main__":
    main()
