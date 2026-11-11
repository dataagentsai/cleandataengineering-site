"""AWS services for data platforms and streaming: a master catalog plus one page per service.

    python3 _guides/aws_services.py --check            validate every service file, print word counts
    python3 _guides/aws_services.py --check s3 kinesis-data-streams   validate some
    python3 _guides/aws_services.py --publish          write /learn/aws-data-services/ and one page per service
    (then python3 _site/nav.py and python3 _site/seo.py)

Content lives in _guides/aws_services/<slug>.py, one SERVICE dict per file (schema in
_guides/aws_services/WRITER-BRIEF.md). This file only renders and validates; it never holds content.
The service list came from a sweep of the site's data-platform and streaming pages on 2026-11-11.
"""
import importlib.util
import json
import re
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "_paths"))
import components as C  # noqa: E402
from bi_choice import ar, bx, svg, t, vtable  # noqa: E402

wb = C.wb
SITE = wb.SITE
BASE = "/learn/aws-data-services/"
DIR = Path(__file__).parent / "aws_services"
DATE = "2026-11-11"

# Lanes of the big picture, left to right, then the band across the bottom.
LANES = [("sources", "Sources"), ("move", "Move in"), ("stream", "Stream"), ("store", "Store"),
         ("process", "Process"), ("serve", "Serve"), ("use", "Use")]
ACROSS = "across"

# group id -> (name, lane, plain description)
GROUPS = {
    "ingestion": ("Ingestion and CDC", "move", "Bring data in from databases, SaaS apps, files and devices."),
    "streaming": ("Streaming and events", "stream", "Carry events and messages while they happen."),
    "storage": ("Storage and table formats", "store", "Keep the data: files, tables, archive and protection."),
    "processing": ("Processing and compute", "process", "Run the code that cleans, joins and shapes data."),
    "serving": ("Query, warehouse and APIs", "serve", "Answer questions and hand data to apps."),
    "operational": ("Operational stores", "serve", "Fast databases for apps, live screens and metadata."),
    "bi": ("BI and dashboards", "use", "Show the numbers to people."),
    "ml": ("ML and AI", "use", "Train models and call language models over the data."),
    "catalog": ("Catalog and governance", ACROSS, "Know what data exists, who may see it and whether it is good."),
    "orchestration": ("Orchestration", ACROSS, "Run steps in the right order at the right time."),
    "security": ("Security, identity and network", ACROSS, "Keys, secrets, roles and private network paths."),
    "observability": ("Observability, audit and cost", ACROSS, "See health, who did what, and what it costs."),
    "devops": ("Infrastructure as code and CI/CD", ACROSS, "Build and change all of it from code."),
}
VERDICTS = ("Pursue", "Pursue with care", "Keep if you have it", "Drop")
REQ = {
    "slug": str, "name": str, "short": str, "group": str, "one_line": str, "status": str, "checked": str,
    "site_verdict": tuple, "equivalents": dict, "plain": list, "analogy": str, "big_picture": list,
    "upstream": list, "downstream": list, "concepts": list, "use_when": list, "avoid_when": list,
    "challenges": list, "compare": list, "cost": dict, "security": list, "monitor": list, "limits": list,
    "decisions": list, "faq": list, "sources": list, "related": list,
}
TUPLE_SIZES = {"concepts": 2, "challenges": 3, "compare": 3, "monitor": 2, "limits": 2, "decisions": 3, "faq": 2, "sources": 2, "related": 2}
MIN_WORDS, MAX_WORDS = 1600, 2700
BANNED = re.compile(r"\b(Octave|JKH|DataAgents|Apollo)\b|→|->", re.I)


# ------------------------------------------------------------------ loading and checks
def load(only=None):
    out = []
    for f in sorted(DIR.glob("*.py")):
        if f.name.startswith("_"):
            continue
        spec = importlib.util.spec_from_file_location(f"svc_{f.stem.replace('-', '_')}", f)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        s = m.SERVICE
        if only and s["slug"] not in only:
            continue
        out.append(s)
    return out


def words(x):
    if isinstance(x, str):
        return len(x.split())
    if isinstance(x, dict):
        return sum(words(v) for v in x.values())
    if isinstance(x, (list, tuple)):
        return sum(words(v) for v in x)
    return 0


def prose_words(s):
    skip = {"slug", "name", "short", "group", "status", "checked", "sources", "related", "upstream", "downstream"}
    return sum(words(v) for k, v in s.items() if k not in skip)


def check(s, slugs):
    errs = []
    for k, ty in REQ.items():
        if k not in s:
            errs.append(f"missing {k}")
        elif not isinstance(s[k], ty):
            errs.append(f"{k} should be {ty.__name__}")
    if errs:
        return errs
    if s["group"] not in GROUPS:
        errs.append(f"unknown group {s['group']}")
    if s["site_verdict"][0] not in VERDICTS:
        errs.append(f"site_verdict must start with one of {VERDICTS}")
    for k, n in TUPLE_SIZES.items():
        for row in s[k]:
            if not isinstance(row, tuple) or len(row) != n:
                errs.append(f"{k}: each row must be a {n}-tuple, got {row!r:.60}")
                break
    for row in s["decisions"]:
        if isinstance(row, tuple) and len(row) == 3 and not row[2].startswith(VERDICTS):
            errs.append(f"decisions verdict must start with one of {VERDICTS}: {row[2]!r:.40}")
    for k in ("azure", "gcp", "databricks", "open_source"):
        if k not in s["equivalents"]:
            errs.append(f"equivalents.{k} missing")
    for k in ("model", "drivers", "traps"):
        if k not in s["cost"]:
            errs.append(f"cost.{k} missing")
    mins = {"concepts": 6, "challenges": 6, "compare": 4, "faq": 4, "sources": 2, "decisions": 3, "monitor": 4}
    for k, n in mins.items():
        if len(s[k]) < n:
            errs.append(f"{k}: need at least {n}, have {len(s[k])}")
    for title, href in s["related"]:
        if href.startswith("svc:"):
            if href[4:] not in slugs:
                errs.append(f"related svc:{href[4:]} is not a service slug")
        elif not href.startswith("/") or not (ROOT / href.strip("/") / "index.html").exists():
            errs.append(f"related link not on the site: {href}")
    for title, url in s["sources"]:
        if not url.startswith("https://"):
            errs.append(f"source not https: {url}")
    blob = json.dumps(s, ensure_ascii=False)
    for m in set(BANNED.findall(blob)):
        errs.append(f"banned word or arrow: {m!r}")
    w = prose_words(s)
    if not MIN_WORDS <= w <= MAX_WORDS:
        errs.append(f"prose words {w}, want {MIN_WORDS}-{MAX_WORDS} (a 10-minute read)")
    return errs


# ------------------------------------------------------------------ drawings
def lane_x(i):
    return 10 + i * 140


def d_place(s, by_slug):
    """Where this service sits: the lanes strip with its lane lit, then upstream, it, downstream."""
    lane = GROUPS[s["group"]][1]
    i = ""
    for k, (lid, name) in enumerate(LANES):
        lit = lid == lane
        i += bx(lane_x(k), 10, 128, 40, [name], "y" if lit else "w", 14, dash=not lit)
        if k:
            i += ar(lane_x(k) - 12, 30, lane_x(k) - 2, 30)
    lit = lane == ACROSS
    i += bx(10, 60, 968, 34, ["Across everything: catalog · security · orchestration · observability and cost · infrastructure as code"], "y" if lit else "w", 13, dash=not lit)

    def nm(x):
        return by_slug[x[4:]]["short"] if x.startswith("svc:") and x[4:] in by_slug else x
    ups, downs = [nm(x) for x in s["upstream"][:3]], [nm(x) for x in s["downstream"][:3]]
    i += t(160, 128, "gets data from", 13, "middle") + t(840, 128, "hands data to", 13, "middle")
    for k, u in enumerate(ups):
        i += bx(40, 140 + k * 46, 240, 36, [u], "b", 13) + ar(280, 158 + k * 46, 378, 196)
    i += bx(380, 160, 240, 72, [s["short"], GROUPS[s["group"]][0]], "g", 16)
    for k, d in enumerate(downs):
        i += ar(620, 196, 718, 158 + k * 46) + bx(720, 140 + k * 46, 240, 36, [d], "b", 13)
    h = 150 + max(len(ups), len(downs), 2) * 46
    label = (f"{s['name']} sits in the {dict(LANES + [(ACROSS, 'across everything')]).get(lane, lane)} part of the data platform. "
             f"It gets data from {', '.join(ups) or 'nothing upstream'} and hands data to {', '.join(downs) or 'nothing downstream'}.")
    return svg(1000, h, label, i)


def d_catalog(services):
    by_lane = {lid: [] for lid, _ in LANES}
    by_lane[ACROSS] = []
    for s in services:
        by_lane[GROUPS[s["group"]][1]].append(s["short"])
    by_lane["sources"] = ["Databases", "SaaS apps", "Files, SFTP", "Devices, plants", "App events"]
    rows = max(len(v) for k, v in by_lane.items() if k != ACROSS)
    i = ""
    for k, (lid, name) in enumerate(LANES):
        x = lane_x(k)
        i += bx(x, 10, 128, 40, [name], "y" if lid != "sources" else "w", 15)
        if k:
            i += ar(x - 12, 30, x - 2, 30)
        for r, n in enumerate(sorted(by_lane[lid])):
            i += t(x + 64, 74 + r * 19, n, 12, "middle")
    top = 84 + rows * 19
    across = sorted(by_lane[ACROSS])
    i += bx(10, top, 968, 40, ["Across everything"], "l", 15)
    per = 6
    for r in range(0, len(across), per):
        i += t(494, top + 66 + (r // per) * 20, " · ".join(across[r:r + per]), 12, "middle")
    h = top + 76 + ((len(across) - 1) // per + 1) * 20
    return svg(1000, h, "The AWS services on this site placed on the data platform: sources, move in, stream, store, process, serve and use from left to right, with catalog, security, orchestration, observability and infrastructure services across everything.", i)


# ------------------------------------------------------------------ pages
CSS = C.CSS + """<style>
  .aw .fig { border:var(--line); border-radius:var(--wob); padding:12px 14px; margin:16px 0; background:#fff; overflow-x:auto; }
  .aw .fig svg { width:100%; min-width:720px; height:auto; display:block; } .aw .fig text { font-family:var(--hand); fill:#111; }
  .aw .fig p { font-size:13.5px; color:var(--muted); margin:6px 0 0; }
  .aw .box { border:var(--line); border-radius:var(--wob); padding:10px 16px; margin:14px 0; background:var(--butter-wash); }
  .aw .warn { border:var(--line); border-radius:var(--wob); padding:10px 16px; margin:14px 0; background:var(--rose-wash); }
  .aw table.t td { font-size:14px; } .aw td.v { font-weight:700; }
  .aw .facts { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:10px; margin:14px 0; }
  .aw .facts div { border:var(--line); border-radius:var(--wob); padding:8px 12px; background:#fff; font-size:14px; }
  .aw .facts b { display:block; font-size:12px; color:var(--muted); font-weight:600; text-transform:uppercase; letter-spacing:.04em; }
  .aw .two { display:grid; grid-template-columns:1fr 1fr; gap:16px; } @media (max-width:700px){ .aw .two { grid-template-columns:1fr; } }
  .aw .two > div { border:var(--line); border-radius:var(--wob); padding:8px 16px; background:#fff; min-width:0; }
  .aw .chips { display:flex; flex-wrap:wrap; gap:8px; margin:12px 0; }
  .aw .chips button { font:inherit; font-size:13.5px; border:var(--line); border-radius:999px; padding:3px 12px; background:#fff; cursor:pointer; color:#111; }
  .aw .chips button.on { background:var(--butter-wash); font-weight:700; }
  .aw #q { font:inherit; padding:6px 10px; border:var(--line); border-radius:8px; width:100%; max-width:360px; box-sizing:border-box; }
  .aw .pill { font-size:12px; border:var(--line); border-radius:999px; padding:0 8px; white-space:nowrap; }
</style>"""


def ul(items):
    return "<ul>" + "".join(f"<li>{E(x)}</li>" for x in items) + "</ul>"


def link_of(href, by_slug):
    if href.startswith("svc:"):
        return f"{BASE}{href[4:]}/"
    return href


def ld_for(title, desc, url, crumbs, qa):
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": title, "description": desc, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}]
    if qa:
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]})
    return "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)


def service_page(s, by_slug, order):
    url = f"{SITE}{BASE}{s['slug']}/"
    title = f"{s['name']} in a data platform"
    desc = f"{s['one_line']} How it fits the big picture, production problems, what to compare it with, cost and verdict."
    eq = s["equivalents"]
    k = order.index(s["slug"])
    prev_s, next_s = by_slug[order[k - 1]], by_slug[order[(k + 1) % len(order)]]
    mins = round(prose_words(s) / 220)
    v, why = s["site_verdict"]
    facts = "".join(f"<div><b>{E(a)}</b>{E(b)}</div>" for a, b in [
        ("Role", GROUPS[s["group"]][0]), ("Status", s["status"]), ("Verdict on this site", v),
        ("Azure", eq["azure"]), ("Google Cloud", eq["gcp"]), ("Databricks", eq["databricks"]), ("Open source", eq["open_source"])])
    rel = " · ".join(f'<a href="{link_of(h, by_slug)}">{E(n)}</a>' for n, h in s["related"])
    srcs = "".join(f'<li><a href="{u}">{E(n)}</a></li>' for n, u in s["sources"])
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/platforms/aws/">AWS</a> › <a href="{BASE}">AWS data services</a> › {E(s['short'])}</p>
<p class="eyebrow" style="margin-top:22px">AWS data services · {E(GROUPS[s['group']][0])} · about {mins} min read</p>
<h1>{E(s['name'])}</h1>
<p class="lede">{E(s['one_line'])}</p>
<div class="aw">
<div class="facts">{facts}</div>
<div class="box"><b>Verdict: {E(v)}.</b> {E(why)}</div>

<section id="plain"><p class="eyebrow">In plain words</p><h2>What it is</h2>{''.join(f'<p>{E(p)}</p>' for p in s['plain'])}
<p><i>{E(s['analogy'])}</i></p></section>

<section id="fit"><p class="eyebrow">Big picture</p><h2>Where it fits</h2>
<div class="fig">{d_place(s, by_slug)}<p>The lit lane is where {E(s['short'])} works. Boxes on the left feed it; boxes on the right use what it produces.</p></div>
{''.join(f'<p>{E(p)}</p>' for p in s['big_picture'])}</section>

<section id="how"><p class="eyebrow">How it works</p><h2>The ideas you need</h2>{C.table(["Idea", "What it means"], s['concepts'])}</section>

<section id="when"><p class="eyebrow">Choosing</p><h2>When to use it, and when not</h2>
<div class="two"><div><h3>Use it when</h3>{ul(s['use_when'])}</div><div><h3>Avoid it when</h3>{ul(s['avoid_when'])}</div></div></section>

<section id="prod"><p class="eyebrow">Production grade</p><h2>What goes wrong in production</h2>
{C.table(["Problem", "What breaks", "What to do"], s['challenges'])}</section>

<section id="compare"><p class="eyebrow">Alternatives</p><h2>What to compare it with</h2>
{C.table(["Alternative", "Pick the alternative when", f"Pick {s['short']} when"], s['compare'])}</section>

<section id="cost"><p class="eyebrow">Cost</p><h2>How you pay</h2><p>{E(s['cost']['model'])}</p>
<div class="two"><div><h3>What drives the bill</h3>{ul(s['cost']['drivers'])}</div><div><h3>Cost traps</h3>{ul(s['cost']['traps'])}</div></div>
<p class="cap">Prices change; check the AWS pricing page for your region before deciding.</p></section>

<section id="secure"><p class="eyebrow">Security and governance</p><h2>Keeping it safe</h2>{ul(s['security'])}</section>

<section id="run"><p class="eyebrow">Operating it</p><h2>What to watch, and the limits</h2>
{C.table(["Watch", "Why"], s['monitor'])}{C.table(["Limit", "Value and notes"], s['limits'])}
<p class="cap">Limits and quotas checked {E(s['checked'])}; many can be raised through Service Quotas.</p></section>

<section id="decide"><p class="eyebrow">Decisions</p><h2>Situations and verdicts</h2>{vtable(["Situation", "Choice", "Verdict"], s['decisions'])}</section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(s['faq'])}</section>
<section id="sources"><p class="eyebrow">Sources</p><h2>Checked against</h2><ul>{srcs}</ul><p class="cap">Checked {E(s['checked'])}.</p></section>
<section id="next"><p class="eyebrow">Related</p><h2>Where it connects</h2><p>{rel} · <a href="{BASE}">All AWS data services</a></p>
<p>← <a href="{BASE}{prev_s['slug']}/">{E(prev_s['short'])}</a> · <a href="{BASE}{next_s['slug']}/">{E(next_s['short'])}</a> →</p></section>
</div>"""
    crumbs = [("AWS", f"{SITE}/platforms/aws/"), ("AWS data services", f"{SITE}{BASE}"), (s["short"], url)]
    return wb.page(title, desc, url, body, CSS + ld_for(title, desc, url, crumbs, s["faq"]))


def catalog_page(services):
    url = f"{SITE}{BASE}"
    title = "AWS services for data platforms and streaming"
    desc = (f"All {len(services)} AWS services used on a data platform and in streaming, placed on one picture: what each does, "
            "its verdict, the Azure, Google Cloud and Databricks equivalent, and a 10-minute page for each.")
    rows = ""
    for gid, (gname, _, _) in GROUPS.items():
        for s in sorted((x for x in services if x["group"] == gid), key=lambda x: x["short"]):
            eq = s["equivalents"]
            rows += (f'<tr data-g="{gid}"><td><a href="{BASE}{s["slug"]}/"><b>{E(s["short"])}</b></a></td><td>{E(gname)}</td>'
                     f'<td>{E(s["one_line"])}</td><td class="v">{E(s["site_verdict"][0])}</td><td>{E(eq["azure"])}</td>'
                     f'<td>{E(eq["gcp"])}</td><td>{E(eq["databricks"])}</td></tr>')
    chips = '<button type="button" class="on" data-g="">All</button>' + "".join(
        f'<button type="button" data-g="{gid}">{E(g[0])}</button>' for gid, g in GROUPS.items() if any(s["group"] == gid for s in services))
    groups = C.table(["Group", "Its job"], [(g[0], g[2]) for gid, g in GROUPS.items() if any(s["group"] == gid for s in services)])
    vcount = {v: sum(1 for s in services if s["site_verdict"][0] == v) for v in VERDICTS}
    qa = [
        ("Which AWS services do I need for a data platform with Databricks?", "S3 for storage, IAM, KMS and VPC endpoints for access and privacy, a mover for each source type (DMS for databases, AppFlow for SaaS, Transfer Family for SFTP, Kinesis or MSK for streams) and CloudWatch, CloudTrail and cost reports to run it. Databricks does the processing, catalog and orchestration."),
        ("Kinesis or MSK?", "Kinesis Data Streams when you want a managed stream with no cluster and AWS-native producers; MSK when you already speak Kafka, need Kafka Connect or Debezium, or want the same tool on every cloud. Each has its own page here."),
        ("Is AWS Glue still needed if I use Databricks?", "Usually not for ETL; Databricks jobs and pipelines do that. The Glue Data Catalog still matters if Athena, Redshift or EMR must read the same tables, and Glue Schema Registry if streams use Avro."),
        ("What is the Azure equivalent of each AWS data service?", "Every row in the table above lists the Azure, Google Cloud and Databricks equivalent, and each service page compares them in more depth."),
    ]
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/platforms/aws/">AWS</a> › AWS data services</p>
<p class="eyebrow" style="margin-top:22px">On your cloud · AWS · master catalog</p>
<h1>{E(title)}</h1>
<p class="lede">Every AWS service our data platform and streaming pages use, on one picture and in one table. Each has its own page, about a 10-minute read: what it is in plain words, where it fits, what goes wrong in production, what to compare it with, cost, and a verdict.</p>
<div class="aw">
<div class="box"><b>How to read this:</b> data moves left to right, from the systems that create it to the people and apps that use it. The band at the bottom is the services every part needs. Verdicts are for a platform built on AWS with Databricks doing the processing: {vcount['Pursue']} Pursue, {vcount['Pursue with care']} Pursue with care, {vcount['Keep if you have it']} Keep if you have it, {vcount['Drop']} Drop.</div>
<section id="picture"><p class="eyebrow">The big picture</p><h2>Every service, in its place</h2>
<div class="fig">{d_catalog(services)}<p>Names under each lane are the services that do that job. Open any of them in the table below.</p></div>
{groups}</section>
<section id="all"><p class="eyebrow">The catalog</p><h2>All {len(services)} services</h2>
<label for="q" class="cap">Search</label> <input id="q" type="search" placeholder="Kinesis, CDC, warehouse ...">
<div class="chips" id="chips">{chips}</div>
<div class="tw"><table class="t" id="cat"><tr><th>Service</th><th>Group</th><th>What it does</th><th>Verdict</th><th>Azure</th><th>Google Cloud</th><th>Databricks</th></tr>{rows}</table></div>
<p class="cap" id="cnt"></p></section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(qa)}</section>
<section id="next"><p class="eyebrow">Related</p><h2>Where it connects</h2>
<p><a href="/platforms/aws/">AWS, on one page</a> · <a href="/learn/data-platform-architecture/aws-databricks/">Data platform on AWS + Databricks</a> · <a href="/learn/streaming/">Streaming on AWS and Databricks</a> · <a href="/learn/streaming/options/">Streaming options at a glance</a> · <a href="/learn/table-maintenance/">Who maintains your tables</a> · <a href="/learn/data-systems/platform/cost/calculator/">Databricks cost calculator</a></p></section>
</div>
<script>
(function(){{
  var g = '', q = document.getElementById('q'), rows = document.querySelectorAll('#cat tr[data-g]'), cnt = document.getElementById('cnt');
  function run(){{
    var s = q.value.toLowerCase(), n = 0;
    rows.forEach(function(r){{ var ok = (!g || r.dataset.g === g) && (!s || r.textContent.toLowerCase().indexOf(s) > -1); r.hidden = !ok; if (ok) n++; }});
    cnt.textContent = n + ' of ' + rows.length + ' services shown';
  }}
  document.getElementById('chips').addEventListener('click', function(e){{
    var b = e.target.closest('button'); if (!b) return;
    g = b.dataset.g; document.querySelectorAll('#chips button').forEach(function(x){{ x.classList.toggle('on', x === b); }}); run();
  }});
  q.addEventListener('input', run); run();
}})();
</script>"""
    crumbs = [("AWS", f"{SITE}/platforms/aws/"), ("AWS data services", url)]
    return wb.page(title, desc, url, body, CSS + ld_for(title, desc, url, crumbs, qa))


def main():
    args = sys.argv[1:]
    only = [a for a in args if not a.startswith("--")] or None
    services = load(only)
    planned = {ln.split()[0]: ln.split()[1] for ln in (DIR / "SLUGS.txt").read_text().splitlines() if ln.strip() and not ln.startswith("#")}
    allslugs = set(planned)
    bad = 0
    for s in services:
        errs = check(s, allslugs)
        if s.get("slug") not in planned:
            errs.append("slug not in SLUGS.txt")
        elif s.get("group") != planned[s["slug"]]:
            errs.append(f"group should be {planned[s['slug']]} (SLUGS.txt)")
        print(f"{'FAIL' if errs else 'ok  '} {s.get('slug', '?'):34} {prose_words(s):5} words")
        for e in errs:
            print("      -", e)
        bad += bool(errs)
    if "--publish" in args:
        if bad:
            sys.exit(f"{bad} service file(s) fail the checks; nothing written")
        services = load()
        by_slug = {s["slug"]: s for s in services}
        order = [s["slug"] for gid in GROUPS for s in sorted((x for x in services if x["group"] == gid), key=lambda x: x["short"])]
        out = ROOT / BASE.strip("/")
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(catalog_page(services))
        for s in services:
            d = out / s["slug"]
            d.mkdir(exist_ok=True)
            (d / "index.html").write_text(service_page(s, by_slug, order))
        print(f"wrote catalog + {len(services)} service pages under {out}")
    elif bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
