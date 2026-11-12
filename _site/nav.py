"""The site's top bar, left panel and footer, in one place.

    python3 _site/nav.py

Writes the header (top bar + left panel) and footer into every site page that carries the site
menu (a <header> with class="brand"), starting with the home page. Generators copy the header and
footer from the home page (_writing/build.py site_parts), so a rebuild keeps them. The CSS and the
small script sit inside the header block on purpose: anything that copies the header copies them.

Layout: a left panel on every page, grouped by purpose
(Concepts · On your cloud · Your role · How we work · Causes and deep tech · About; see SECTIONS), fixed and scrolling on its own on wide
screens, opened from a Menu button below 900px. The page's own link is marked and its group
opened. The top bar keeps the name, Certifications, Blog, Find my path and For leaders.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

import sys
sys.path.insert(0, str(ROOT / "_paths"))
from data import DISCIPLINES, PLATFORMS  # noqa: E402

# Menu structure agreed with the owner on 10 Nov 2026. One tree of ideas shown twice:
#   CONCEPTS (platform-agnostic): for leaders, data systems, the data and AI platform with its
#     capabilities (data engineering, BI, ML, AI, across all), key concepts.
#   ON YOUR CLOUD: the same headings per platform (/platforms/<id>/#systems, #de, #bi, #ml, #ai, #across).
#   YOUR ROLE: paths through both trees, plus practice and projects. HOW WE WORK: skills that aren't a
#   technology. Open specs and code sit in the capability they serve. URLs never move; only the menu.
# Item: (name, href, children[, "cap"]); a child with href None is a small heading; "cap" indents an item.

CLOUD_HEADS = [("Data systems", "systems"), ("Data engineering", "de"), ("BI and analytics", "bi"), ("ML", "ml"),
               ("AI", "ai"), ("Across all of them", "across"), ("Learning paths", "paths"), ("Certifications", "certs")]


def cloud(name, pid, heads=None, extra=()):
    keys = heads or [k for _, k in CLOUD_HEADS]
    return (name, f"/platforms/{pid}/", [(n, f"/platforms/{pid}/#{k}") for n, k in CLOUD_HEADS if k in keys] + list(extra))


ROLE_KIDS = {
    "data-engineering": [("Start here", "/data-engineering/"), ("Learning path", "/paths/data-engineering/"),
                         ("Practice and simulators", "/data-engineering/#tools"), ("Projects to join", "/projects/?subject=data")],
    "ai-engineering": [("Learning path", "/paths/ai-engineering/"), ("Simulator: Agent Harness", "/learn/agent-harness-sim/"),
                       ("Vertical agents", "/ai-engineering/vertical-agents/"), ("Projects to join", "/projects/?subject=ai")],
    "llm-engineering": [("Learning path", "/paths/llm-engineering/"), ("Simulator: Claude API", "/learn/llm-api-sim/"),
                        ("Projects to join", "/projects/?subject=llm")],
}
ROLES = [(d["name"], "/data-engineering/" if d["id"] == "data-engineering" else f"/paths/{d['id']}/",
          ROLE_KIDS.get(d["id"], [("Learning path", f"/paths/{d['id']}/")]) + [("Key concepts", f"/concepts/#{d['id']}")])
         for d in DISCIPLINES]

SECTIONS = [
    ("Concepts", [
        ("For leaders", "/leaders/", [
            ("The one-minute version", "/leaders/"),
            ("Questions leaders ask", "/leaders/#questions"),
            ("Spec-driven development: agents", "/leaders/spec-driven/"),
            ("Spec-driven development: data platforms", "/leaders/spec-driven/data-platform/"),
            ("Technical papers", "/papers/"),
        ]),
        ("Data systems", "/learn/data-systems/", [
            ("The whole system, end to end", "/learn/data-systems/"),
            ("Upstreams", None),
            ("Know your sources", "/learn/data-systems/upstreams/"),
            ("API sources", "/learn/data-systems/upstreams/apis/"),
            ("File sources", "/learn/data-systems/upstreams/files/"),
            ("Learning the joins", "/learn/data-systems/upstreams/joins/"),
            ("Where the answers go", "/learn/data-systems/upstreams/answers/"),
            ("Source system questionnaire", "/learn/data-systems/upstreams/questionnaire/"),
            ("Downstreams", None),
            ("Know your consumers", "/learn/data-systems/downstreams/"),
        ]),
        ("Data and AI platform", "/learn/data-systems/platform/", [
            ("Conceptual architecture", None),
            ("The platform, whole", "/learn/data-systems/platform/"),
            ("Data platform architecture", "/learn/data-platform-architecture/"),
            ("Medallion architecture", "/learn/medallion-architecture/"),
            ("Real-time analytics", "/learn/real-time-analytics/"),
        ]),
        ("Data engineering", "/learn/data-systems/platform/#hops", [
            ("The hops", None),
            ("Hop 1: sources to bronze", "/learn/data-platform-architecture/ingestion/"),
            ("Hop 2: bronze to silver", "/learn/data-platform-architecture/bronze-to-silver/"),
            ("Hop 3: silver to gold", "/learn/data-platform-architecture/gold/"),
            ("The metadata store", "/learn/data-platform-architecture/metadata-store/"),
            ("Tables and formats", None),
            ("Delta vs Iceberg", "/learn/delta-vs-iceberg/"),
            ("Who maintains your tables", "/learn/table-maintenance/"),
            ("Iceberg lakehouse: who owns the catalog?", "/learn/iceberg-lakehouse-aws-databricks/"),
            ("Metric views, taught from zero", "/learn/metric-views/"),
            ("History, SCD and facts", None),
            ("SCD2: AUTO CDC or own PySpark?", "/learn/scd2-auto-cdc-vs-pyspark/"),
            ("Gold harness spec: facts and SCD2", "/learn/gold-harness-spec/"),
            ("Time travel as SCD Type 2?", "/learn/time-travel-vs-scd2/"),
            ("Streaming and real time", None),
            ("Streaming on AWS and Databricks", "/learn/streaming/"),
            ("Streaming: all options", "/learn/streaming/options/"),
            ("Streaming simulator", "/learn/streaming/sim/"),
            ("Databricks real time: RTM and Lakehouse//RT", "/learn/streaming/real-time-mode/"),
            ("Quality and testing", None),
            ("Shift left: fail fast on data code", "/learn/shift-left/"),
            ("Data quality, metadata-driven", "/learn/data-platform-sim/data-quality/"),
            ("Hands-on simulators", None),
            ("One batch through Spark and Delta", "/learn/data-platform-sim/"),
            ("Spark internals", "/learn/data-platform-sim/spark/"),
            ("Delta Lake internals", "/learn/data-platform-sim/delta/"),
            ("Spark performance: 12 problems", "/learn/data-platform-sim/performance/"),
            ("Problems solved: SCD2, late data, duplicates", "/learn/data-platform-sim/problems/"),
            ("On AWS", None),
            ("AWS + Databricks, ETL end to end", "/learn/data-platform-architecture/aws-databricks/"),
            ("Iceberg lakehouse on AWS: A vs B", "/learn/iceberg-lakehouse-aws-databricks/"),
            ("AWS data services catalog", "/learn/aws-data-services/"),
            ("Open specs", None),
            ("DataTwin", "/learn/datatwin/"),
            ("Clean Data Engineering specs", "/projects/data-eng-specs/"),
        ], "cap"),
        ("BI and analytics", "/concepts/semantic-layer/", [
            ("Hop 4: the semantic layer", "/concepts/semantic-layer/"),
            ("Genie and metric views", "/writing/genie-metric-views/"),
            ("Metric views, taught from zero", "/learn/metric-views/"),
            ("Power BI vs Databricks AI/BI", "/learn/power-bi-vs-databricks-ai-bi/"),
            ("Power BI and Fabric, in depth", "/learn/power-bi-vs-databricks-ai-bi/power-bi/"),
            ("Databricks AI/BI, in depth", "/learn/power-bi-vs-databricks-ai-bi/ai-bi/"),
            ("Know your consumers", "/learn/data-systems/downstreams/"),
        ], "cap"),
        ("ML", "/concepts/#ml-engineering", [
            ("Key ML ideas (pages coming)", "/concepts/#ml-engineering"),
        ], "cap"),
        ("AI", "/learn/ai-universe/", [
            ("The AI Universe", "/learn/ai-universe/"),
            ("Agent Harness", "/learn/agent-harness/"),
            ("Eval Harness", "/learn/eval-harness/"),
            ("Agent guardrails", "/learn/agent-guardrails/"),
            ("Open spec: AI Assurance Catalog", "https://dataagentsai.github.io/ai-assurance-catalog/"),
            ("Open spec: AI Harness Catalog", "https://dataagentsai.github.io/ai-harness-catalog/"),
            ("Open spec: AgentTwin", "/learn/agenttwin/"),
            ("The AgentTwin Lab", "/lab/"),
            ("Code: Reference Agent", "https://github.com/dataagentsai/reference-agent"),
            ("Code: AgentTwin library", "https://github.com/dataagentsai/agenttwin"),
            ("Code: Eval Harness Framework", "https://github.com/dataagentsai/eval-harness-framework"),
        ], "cap"),
        ("Across all of them", "/learn/data-systems/platform/#concerns", [
            ("All 24 concerns", "/learn/data-systems/platform/#concerns"),
            ("Layout: catalogs and schemas", "/learn/data-systems/platform/layout/"),
            ("Environments and CI/CD", "/learn/data-systems/platform/environments/"),
            ("Cost and FinOps", "/learn/data-systems/platform/cost/"),
            ("Test architecture for data", "/learn/data-platform-architecture/testing/"),
        ], "cap"),
        ("Key concepts, A to Z", "/concepts/#a-z", []),
    ]),
    ("On your cloud", [
        cloud("Databricks", "databricks"),
        cloud("AWS", "aws", extra=[("AWS data services: all 66", "/learn/aws-data-services/")]),
        cloud("Azure and Fabric", "azure"),
        cloud("Google Cloud", "gcp"),
        cloud("Open source", "open"),
        cloud("Claude (Anthropic)", "anthropic", ["ai", "certs"]),
        ("All certifications", "/certifications/", []),
    ]),
    ("Your role", [
        ("Find your path", "/paths/", []),
        *ROLES,
        ("Worried about AI?", "/mindset/", []),
        ("All projects to join", "/projects/", []),
    ]),
    ("How we work", [
        ("Thinking principles", "/how-we-work/#thinking", []),
        ("Business analysis", "/how-we-work/#ba", []),
        ("Project management", "/how-we-work/#pm", []),
        ("The technical anchor", "/learn/technical-anchor/", [
            ("The role", "/learn/technical-anchor/"),
            ("Discovery", "/learn/technical-anchor/discovery/"),
            ("Project review", "/learn/technical-anchor/project-review/"),
            ("Project review: the checks", "/learn/technical-anchor/project-review/checks/"),
        ]),
    ]),
    ("Causes and deep tech", [
        ("AI for a cause", "/ai-for-cause/", [
            ("Babu, companion for elders", "/projects/babu-companion/"),
            ("AI for road safety", "/road-safety/"),
            ("Raah, guide for blind people", "/ai-for-cause/raah/"),
        ]),
        ("Deep tech", "/deep-tech/", [
            ("Hard problems", "/problems/"),
            ("Hard problems by layer", "/learn/hard-problems/"),
            ("Hinglish pre-training data", "/projects/hinglish-pretraining-data/"),
            ("Robot data benchmark", "/projects/robotics-data-benchmark/"),
        ]),
    ]),
    ("About", [
        ("About this site", "/about/", []),
        ("Write or teach", "/about/#join", []),
        ("Blog", "/writing/", []),
        ("All open specifications", "/research/", []),
        ("All open-source code", "/assets/", []),
    ]),
]

CSS = """<style>
  .topbar { display:flex; align-items:center; gap:10px; padding:4px 0; }
  .topbar .brand { font-family:var(--hand); font-size:25px; color:var(--ink); text-decoration:none; margin-right:auto; line-height:1.2; }
  .topbar .lnk { font-size:14.5px; color:var(--ink-soft); text-decoration:none; padding:4px 6px; }
  .topbar .lnk:hover { text-decoration:underline; text-decoration-style:wavy; }
  .topbar .act { font-size:14px; font-weight:700; text-decoration:none; border:1.5px solid var(--ink); border-radius:999px; padding:4px 13px; color:var(--ink); background:#fff; white-space:nowrap; }
  .topbar .act.dark { background:var(--ink); color:#fff; }
  .menubtn { font:inherit; font-size:14px; font-weight:700; border:1.5px solid var(--ink); border-radius:999px; padding:4px 12px; background:var(--butter-wash); cursor:pointer; color:var(--ink); }
  .sidepanel { position:fixed; top:0; left:0; bottom:0; width:248px; overflow-y:auto; overscroll-behavior:contain; background:#fff;
    border-right:1.5px dashed var(--rule-firm); padding:22px 12px 40px 16px; z-index:60; font-family:var(--sans); font-size:14.5px; line-height:1.4; }
  .sidepanel .sbrand { font-family:var(--hand); font-size:22px; color:var(--ink); text-decoration:none; display:block; margin:0 0 6px 8px; }
  .sidepanel h4 { font-family:var(--sans); font-size:11.5px; font-weight:700; letter-spacing:.13em; text-transform:uppercase; color:var(--faint); margin:18px 0 4px 8px; }
  .sidepanel ul { list-style:none; margin:0; padding:0; } .sidepanel li { margin:0; }
  .sidepanel a { display:block; padding:4px 8px; border-radius:9px; color:var(--ink); text-decoration:none; }
  .sidepanel a:hover { background:var(--peri-wash); }
  .sidepanel a.on { background:var(--ink); color:#fff; }
  .sidepanel details > summary { list-style:none; display:flex; align-items:center; cursor:pointer; }
  .sidepanel details > summary::-webkit-details-marker { display:none; }
  .sidepanel details > summary a { flex:1; }
  .sidepanel details > summary::after { content:"›"; font-size:17px; color:var(--faint); padding:0 6px; transition:transform .15s; }
  .sidepanel details[open] > summary::after { transform:rotate(90deg); }
  .sidepanel details ul { margin:0 0 4px 12px; border-left:1.5px dashed var(--rule-firm); padding-left:4px; font-size:13.5px; }
  .sidepanel li.cap { margin-left:12px; border-left:1.5px dashed var(--rule-firm); padding-left:2px; }
  .sidepanel li.sub { font-size:10.5px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:var(--faint); padding:9px 8px 2px; }
  .sidepanel .close { display:none; }
  .scrim { display:none; }
  @media (min-width:900px) {
    body { padding-left:248px; }
    .menubtn { display:none; } .topbar .brand { visibility:hidden; }
  }
  @media (max-width:899px) {
    .sidepanel { display:none; width:min(300px,86vw); box-shadow:4px 0 0 var(--ink); border-right:1.5px solid var(--ink); }
    .sidepanel.open { display:block; } .sidepanel .close { display:block; float:right; font:inherit; border:0; background:none; font-size:24px; line-height:1; cursor:pointer; }
    .scrim.open { display:block; position:fixed; inset:0; background:rgba(0,0,0,.18); z-index:55; }
  }
  @media (max-width:640px) { .topbar .lnk, .topbar .act:not(.dark) { display:none; } .topbar .brand { font-size:17px; } .topbar .act.dark { padding:3px 10px; font-size:13px; } .menubtn { padding:3px 9px; font-size:13px; } }
</style>"""

JS = """<script>
(function(){
  var p = document.getElementById('sidepanel'), s = document.getElementById('scrim');
  function t(o){ p.classList.toggle('open', o); s.classList.toggle('open', o); }
  document.getElementById('menubtn').onclick = function(){ t(true); };
  p.querySelector('.close').onclick = s.onclick = function(){ t(false); };
  var here = location.pathname.replace(/index\\.html$/, '') + location.hash, best = null, len = 0;
  p.querySelectorAll('a[href^="/"]').forEach(function(a){
    var h = a.getAttribute('href');
    if (h !== '/' && here.indexOf(h) === 0 && h.length > len) { best = a; len = h.length; }
  });
  if (best) { best.classList.add('on'); for (var e = best.parentElement; e && e !== p; e = e.parentElement) if (e.tagName === 'DETAILS') e.open = true;
    if (best.getBoundingClientRect().bottom > innerHeight) best.scrollIntoView({block:'center'}); }
})();
</script>"""


def panel():
    out = ['<aside class="sidepanel" id="sidepanel" aria-label="Site sections"><button class="close" aria-label="Close menu">×</button>',
           '<a class="sbrand" href="/">Clean Data Engineering</a>']
    for g, items in SECTIONS:
        out.append(f"<h4>{g}</h4><ul>")
        for it in items:
            name, href, kids = it[0], it[1], it[2]
            cap = len(it) > 3 and it[3] == "cap"
            li = '<li class="cap">' if cap else "<li>"
            if kids:
                ks = "".join(f'<li class="sub">{n}</li>' if h is None else f'<li><a href="{h}">{n}</a></li>' for n, h in kids)
                out.append(f'{li}<details><summary><a href="{href}">{name}</a></summary><ul>{ks}</ul></details></li>')
            else:
                out.append(f'{li}<a href="{href}">{name}</a></li>')
        out.append("</ul>")
    out.append("</aside>")
    return "".join(out)


def header():
    return ("<header>\n  <div class=\"wrap\">\n    " + CSS + "\n"
            "    <nav class=\"topbar\" aria-label=\"Site\"><button class=\"menubtn\" id=\"menubtn\" aria-label=\"Open menu\">☰ Menu</button>"
            "<a class=\"brand\" href=\"/\">Clean Data Engineering</a>"
            "<a class=\"lnk\" href=\"/certifications/\">Certifications</a><a class=\"lnk\" href=\"/writing/\">Blog</a><a class=\"act\" href=\"/paths/\">Find my path</a>"
            "<a class=\"act dark\" href=\"/leaders/\">For leaders</a></nav>\n"
            "    " + panel() + "<div class=\"scrim\" id=\"scrim\"></div>\n    " + JS + "\n  </div>\n</header>")


def footer():
    cols = []
    for g, items in SECTIONS:
        links = "".join(f'<a href="{it[1]}">{it[0]}</a>' for it in items)
        cols.append(f"<div><b>{g}</b>{links}</div>")
    return ("<footer>\n  <div class=\"wrap\">\n    <style>.fcols{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px 20px;margin-bottom:18px}"
            ".fcols div{display:flex;flex-direction:column;gap:3px;font-size:13.5px}.fcols b{color:var(--ink)}</style>\n"
            "    <div class=\"fcols\">" + "".join(cols) + "</div>\n"
            "    &copy; 2026 Clean Data Engineering &middot; Everything here is free &middot;\n"
            "    <a href=\"https://github.com/dataagentsai\">GitHub</a> &middot;\n"
            "    <a href=\"/writing/feed.xml\">RSS</a> &middot;\n"
            "    <a href=\"mailto:basant@cleandataengineering.ai\">basant@cleandataengineering.ai</a>\n  </div>\n</footer>")


HEAD_RE = re.compile(r"<header>(?:(?!</header>).)*?class=\"brand\".*?</header>", re.S)
FOOT_RE = re.compile(r"<footer>(?:(?!</footer>).)*?Everything here is free.*?</footer>", re.S)


def main():
    h, f = header(), footer()
    n = 0
    for p in ROOT.rglob("*.html"):
        rel = p.relative_to(ROOT).as_posix()
        if rel.startswith((".git/", "_")) or "/_" in rel:
            continue
        s = p.read_text()
        t = HEAD_RE.sub(lambda m: h, s, count=1)
        t = FOOT_RE.sub(lambda m: f, t, count=1)
        if t != s:
            p.write_text(t)
            n += 1
    print("top bar, left panel and footer written to", n, "pages")


if __name__ == "__main__":
    main()
