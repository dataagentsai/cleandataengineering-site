"""The site's top bar, left panel and footer, in one place.

    python3 _site/nav.py

Writes the header (top bar + left panel) and footer into every site page that carries the site
menu (a <header> with class="brand"), starting with the home page. Generators copy the header and
footer from the home page (_writing/build.py site_parts), so a rebuild keeps them. The CSS and the
small script sit inside the header block on purpose: anything that copies the header copies them.

Layout (31 Oct 2026), agreed with the owner: a left panel on every page, grouped by purpose
(Learn · Build with us · For leaders · About), fixed and scrolling on its own on wide
screens, opened from a Menu button below 900px. The page's own link is marked and its group
opened. The top bar keeps the name, Certifications, Blog, Find my path and For leaders.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (group, [(name, href, [(child, href), ...]), ...])
SECTIONS = [
    ("Learn", [
        ("Find your path", "/paths/", []),
        ("Key concepts", "/concepts/", []),
        ("Courses", "/learn/", [
            ("The AI Universe", "/learn/ai-universe/"),
            ("Agent Harness", "/learn/agent-harness/"),
            ("Eval Harness", "/learn/eval-harness/"),
            ("Data platform architecture", "/learn/data-platform-architecture/"),
            ("Medallion architecture", "/learn/medallion-architecture/"),
            ("The technical anchor", "/learn/technical-anchor/"),
            ("Agent guardrails", "/learn/agent-guardrails/"),
        ]),
        ("Simulators", "/simulators/", [
            ("Claude API Simulator", "/learn/llm-api-sim/"),
            ("Agent Harness Simulator", "/learn/agent-harness-sim/"),
            ("DataTwin Studio", "/learn/data-platform-sim/"),
            ("Problem Lab", "/learn/data-platform-sim/problems/"),
            ("Performance stories", "/learn/data-platform-sim/performance/"),
        ]),
        ("Certifications", "/certifications/", [
            ("AI engineering", "/certifications/#ai"),
            ("Data engineering", "/certifications/#data"),
            ("Claude Certified Architect", "/certifications/claude-certified-architect/CCA-F/"),
            ("CCA-F mind maps", "/certifications/cca-f-mind-maps/"),
            ("Claude Architect, Professional", "/certifications/claude-certified-architect/CCAR-P/CCAR-P_Study_Guide.html"),
            ("Microsoft AI-103", "/certifications/azure-ai-engineer/"),
        ]),
        ("Worried about AI?", "/mindset/", []),
    ]),
    ("Build with us", [
        ("Join a project", "/projects/", []),
        ("Hard problems", "/problems/", []),
        ("Open specifications", "/research/", [
            ("AI Assurance Catalog", "https://dataagentsai.github.io/ai-assurance-catalog/"),
            ("AI Harness Catalog", "https://dataagentsai.github.io/ai-harness-catalog/"),
            ("AgentTwin, explained", "/learn/agenttwin/"),
            ("DataTwin, explained", "/learn/datatwin/"),
            ("The AgentTwin Lab", "/lab/"),
        ]),
        ("Open-source assets", "/assets/", [
            ("Reference Agent", "https://github.com/dataagentsai/reference-agent"),
            ("AgentTwin library", "https://github.com/dataagentsai/agenttwin"),
            ("Eval Harness Framework", "https://github.com/dataagentsai/eval-harness-framework"),
            ("Claims assistant on Azure", "https://github.com/dataagentsai/claims-fnol-azure"),
        ]),
        ("Write or teach", "/about/#join", []),
    ]),
    ("For leaders", [
        ("The one-minute version", "/leaders/", []),
        ("Questions leaders ask", "/leaders/#questions", []),
        ("Technical papers", "/papers/", []),
        ("Blog", "/writing/", []),
    ]),
    ("About", [
        ("About this site", "/about/", []),
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
        for name, href, kids in items:
            if kids:
                ks = "".join(f'<li><a href="{h}">{n}</a></li>' for n, h in kids)
                out.append(f'<li><details><summary><a href="{href}">{name}</a></summary><ul>{ks}</ul></details></li>')
            else:
                out.append(f'<li><a href="{href}">{name}</a></li>')
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
        links = "".join(f'<a href="{h}">{n}</a>' for n, h, _ in items)
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
