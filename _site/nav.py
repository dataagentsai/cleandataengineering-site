"""The site menu and footer, in one place.

    python3 _site/nav.py

Writes HEADER and FOOTER into every site page that carries the site menu (a <header> with
class="brand"), starting with the home page. Generators copy the header and footer from the
home page (_writing/build.py site_parts), so a rebuild keeps them. The menu's CSS sits inside
the header block on purpose: anything that copies the header copies its look too.

Menu (31 Oct 2026), following the home page's loop:
  Learn (see it) · Simulators (run it) · Projects (build it) · Research (prove it) · Writing · About
Desktop: hovering or focusing a menu item opens a short list of what is inside.
Phone: the lists are hidden; each item opens its hub page.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MENU = [
    ("Learn", "/learn/", [
        ("Paths", "/paths/", "6 roles × 5 clouds, beginner to advanced"),
        ("Key concepts", "/concepts/", "84 ideas that are the same on every cloud"),
        ("Courses", "/learn/", "hand-drawn, every box opens the next level"),
        ("The AI Universe", "/learn/ai-universe/", "the map before the trek"),
        ("Certifications", "/certifications/", "Claude Architect, Azure AI-103"),
        ("The lion mindset", "/mindset/", "for anyone worried about AI"),
    ]),
    ("Simulators", "/simulators/", [
        ("Agent Harness Simulator", "/learn/agent-harness-sim/", "send a message, watch every step"),
        ("DataTwin Studio", "/learn/data-platform-sim/", "one real Spark batch, end to end"),
        ("Problem Lab", "/learn/data-platform-sim/problems/", "19 data problems, broken and fixed"),
        ("Performance stories", "/learn/data-platform-sim/performance/", "slow job, clue, fix, measured"),
        ("All simulators", "/simulators/", ""),
    ]),
    ("Projects", "/projects/", []),
    ("Research", "/research/", [
        ("Overview", "/research/", "open standards for agents and data"),
        ("AgentTwin, explained", "/learn/agenttwin/", "test an agent in a simulated world"),
        ("DataTwin, explained", "/learn/datatwin/", "test a data platform the same way"),
        ("The AgentTwin Lab", "/lab/", "30 simulated days, results so far"),
    ]),
    ("Writing", "/writing/", []),
    ("About", "/about/", []),
]

NAV_CSS = """<style>
  .sitenav { display:flex; align-items:center; gap:4px 6px; flex-wrap:wrap; }
  .sitenav .brand { font-family:var(--hand); font-size:25px; color:var(--ink); text-decoration:none; margin-right:auto; line-height:1.2; }
  .sitenav .dd { position:relative; }
  .sitenav .dd > a { display:inline-block; font-size:15px; color:var(--ink-soft); text-decoration:none; padding:6px 9px; border-radius:999px; }
  .sitenav .dd > a:hover, .sitenav .dd:focus-within > a { background:var(--butter-wash); color:var(--ink); }
  .sitenav .dd.has > a::after { content:" ▾"; font-size:11px; color:var(--faint); }
  .sitenav .menu { display:none; position:absolute; top:100%; left:-8px; z-index:50; min-width:300px; padding:8px; margin:0;
    background:#fff; border:1.5px solid var(--ink); border-radius:14px; box-shadow:4px 4px 0 var(--ink); list-style:none; }
  .sitenav .dd:hover .menu, .sitenav .dd:focus-within .menu { display:block; }
  .sitenav .menu a { display:block; padding:6px 10px; border-radius:10px; text-decoration:none; color:var(--ink); font-size:15px; line-height:1.3; }
  .sitenav .menu a:hover, .sitenav .menu a:focus { background:var(--peri-wash); }
  .sitenav .menu small { display:block; font-size:12.5px; color:var(--muted); }
  .sitenav .go { display:none; } body.home .sitenav .go { display:inline-block; }
  .sitenav .go { font-size:14px; font-weight:700; color:#fff; background:var(--ink); border:1.5px solid var(--ink); border-radius:999px; padding:5px 14px; text-decoration:none; margin-left:6px; }
  @media (max-width:760px) { .sitenav .brand { width:100%; } .sitenav .menu, .sitenav .dd:hover .menu, .sitenav .dd:focus-within .menu { display:none; }
    .sitenav .dd.has > a::after { content:""; } .sitenav .dd > a { padding:4px 7px 4px 0; font-size:13.5px; } .sitenav { gap:0 2px; } .sitenav .go, body.home .sitenav .go { display:none; } }
</style>"""


def header():
    items = []
    for name, href, sub in MENU:
        if sub:
            links = "".join(f'<li><a href="{h}">{n}{f"<small>{d}</small>" if d else ""}</a></li>' for n, h, d in sub)
            items.append(f'<div class="dd has"><a href="{href}">{name}</a><ul class="menu">{links}</ul></div>')
        else:
            items.append(f'<div class="dd"><a href="{href}">{name}</a></div>')
    return ("<header>\n  <div class=\"wrap\">\n    " + NAV_CSS + "\n    <nav class=\"sitenav\" aria-label=\"Site\">\n"
            "      <a class=\"brand\" href=\"/\">Clean Data Engineering</a>\n      " + "\n      ".join(items) +
            "\n      <a class=\"go\" href=\"/paths/\">Find my path</a>\n    </nav>\n  </div>\n</header>")


def footer():
    cols = []
    for name, href, sub in MENU:
        links = "".join(f'<a href="{h}">{n}</a>' for n, h, _ in sub if n not in ("Overview", "All simulators")) or f'<a href="{href}">{name}</a>'
        cols.append(f'<div><b><a href="{href}">{name}</a></b>{links if sub else ""}</div>')
    return ("<footer>\n  <div class=\"wrap\">\n    <style>.fcols{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:14px 20px;margin-bottom:18px}"
            ".fcols div{display:flex;flex-direction:column;gap:3px;font-size:13.5px}.fcols b a{color:var(--ink);text-decoration:none}</style>\n"
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
    print("menu and footer written to", n, "pages")


if __name__ == "__main__":
    main()
