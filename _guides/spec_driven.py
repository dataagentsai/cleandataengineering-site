"""Spec-driven development, for leaders: one page at /leaders/spec-driven/.

    python3 _guides/spec_driven.py && python3 _site/nav.py && python3 _site/seo.py

Copies the site's <head> styles, top bar and footer from mindset/index.html (nav.py then
rewrites the header with the current left panel), draws its pictures with the people from
_site/illustrations.py, and writes leaders/spec-driven/index.html.
Evidence numbers (generation runs 3 to 5) are from the clean-ai-engineering spec cycle, 8 Oct 2026.
"""
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "_site"))
import illustrations as I  # noqa: E402

SRC = (ROOT / "mindset" / "index.html").read_text()
OUT = ROOT / "leaders" / "spec-driven" / "index.html"

TITLE = "Spec-driven development"
DESC = ("How a small centre of excellence writes the specs once, builds the shared assets once, and then "
        "every agent and data platform is built, tested, released and run from the same specs, "
        "getting stronger with each one.")
URL = "https://cleandataengineering.ai/leaders/spec-driven/"

INK = "#1F1F1F"
WASH = dict(peri="#E4EAF8", butter="#FFF0CC", rose="#F8E1EC", mint="#DDF0E4", lilac="#ECE5F8", sky="#E0F1F7")

CSS = """
  .sd-stat { display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:14px; margin:26px 0; }
  .sd-stat div { border:var(--line); border-radius:var(--wob); padding:14px 18px; background:var(--peri-wash); font-size:15px; }
  .sd-stat b { display:block; font-family:var(--hand); font-size:32px; font-weight:400; line-height:1.1; }
  .sd-answer { background:var(--butter-wash); border:var(--line); border-radius:var(--wob); padding:16px 22px; margin:22px 0; }
  .sd-answer p { margin:6px 0; }
  .sd-fig { border:var(--line); border-radius:var(--wob); padding:18px; margin:18px 0; background:#fff; }
  .sd-fig svg { width:100%; height:auto; display:block; }
  .sd-fig figcaption { font-size:14px; color:var(--muted); margin-top:8px; }
  .sd-table { overflow-x:auto; margin:10px 0 0; }
  .sd-table table { border-collapse:collapse; width:100%; font-size:15px; }
  .sd-table th, .sd-table td { border-bottom:1px solid var(--rule-firm); padding:9px 10px; text-align:left; vertical-align:top; }
  .sd-table th { background:var(--surface-2); font-weight:700; }
  .sd-cards { display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:16px; margin-top:16px; }
  .sd-card { border:var(--line); border-radius:var(--wob); padding:14px 18px; background:var(--mint-wash); }
  .sd-card.peri { background:var(--peri-wash); } .sd-card.rose { background:var(--rose-wash); }
  .sd-card.butter { background:var(--butter-wash); } .sd-card.lilac { background:var(--lilac-wash); }
  .sd-card h3 { font-size:23px; margin:0 0 4px; line-height:1.15; }
  .sd-card p { margin:7px 0; font-size:15px; }
  .sd-card .lbl { display:block; font-size:11.5px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; color:var(--faint); }
  .sd-check { list-style:none; padding:0; margin:14px 0; border:var(--line); border-radius:16px; background:#fff; }
  .sd-check li { display:grid; grid-template-columns:28px 1fr; gap:6px 10px; padding:10px 16px; border-bottom:1px dashed var(--rule-firm); font-size:15px; }
  .sd-check li:last-child { border-bottom:0; }
  .sd-check .box { width:18px; height:18px; border:1.5px solid var(--ink); border-radius:5px; margin-top:2px; background:var(--mint-wash); text-align:center; line-height:15px; font-size:13px; font-weight:700; }
  .sd-check .from { grid-column:2; font-size:13px; color:var(--muted); }
  .sd-steps { counter-reset:s; list-style:none; padding:0; display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:16px; }
  .sd-steps li { border:var(--line); border-radius:var(--wob); padding:14px 18px; background:var(--sky-wash); }
  .sd-steps li h3 { font-size:23px; margin:0 0 6px; }
  .sd-steps li p { margin:6px 0; font-size:15px; }
  .sd-qa h3 { font-size:21px; margin:18px 0 4px; }
  .sd-qa p { margin:4px 0 10px; }
"""


# ---------------------------------------------------------------- drawing helpers
def rough(n):
    return (f'<filter id="rough{n}" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="{n}"/>'
            f'<feDisplacementMap in="SourceGraphic" scale="2"/></filter>'
            f'<marker id="ah{n}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
            f'<path d="M1,1 L9,5 L1,9" fill="none" stroke="{INK}" stroke-width="1.6" stroke-linecap="round"/></marker>')


def svg(n, w, h, body, label):
    return (f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{label}" xmlns="http://www.w3.org/2000/svg">'
            f'<defs>{I.STYLE}{rough(n)}</defs>{body}</svg>')


def box(n, x, y, w, h, fill, r=14):
    """Pastel pencil fill offset under a hand-drawn outline."""
    return (f'<rect x="{x + 5}" y="{y + 5}" width="{w}" height="{h}" rx="{r}" fill="{fill}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="none" stroke="{INK}" stroke-width="1.6" filter="url(#rough{n})"/>')


def t(x, y, s, size=14, hand=False, anchor="middle", bold=False, fill=INK):
    fam = "Patrick Hand, cursive" if hand else "DM Sans, sans-serif"
    wt = ' font-weight="700"' if bold else ""
    return f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" text-anchor="{anchor}" fill="{fill}"{wt}>{s}</text>'


def arrow(n, d, dash=False):
    da = ' stroke-dasharray="6 6"' if dash else ""
    return f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="1.6" stroke-linecap="round"{da} marker-end="url(#ah{n})"/>'


def paper(x, y, w, h, tab):
    lines = "".join(f'<line x1="{x + 9}" y1="{y + 22 + i * 10}" x2="{x + w - 9 - (i % 2) * 10}" y2="{y + 22 + i * 10}" stroke="#B9B6CC" stroke-width="1.6"/>'
                    for i in range(int((h - 28) / 10)))
    return (f'<path d="M{x},{y} L{x + w - 12},{y} L{x + w},{y + 12} L{x + w},{y + h} L{x},{y + h} Z" fill="#fff" class="o"/>'
            f'<rect x="{x + 8}" y="{y + 7}" width="{w * .45}" height="7" rx="3" fill="{tab}"/>{lines}')


def num(x, y, k):
    return f'<circle cx="{x}" cy="{y}" r="13" fill="{I.PAL["yellow"]}" class="o"/>' + t(x, y + 5, k, 15, bold=True)


# ---------------------------------------------------------------- 1. the COE team
ROLES = [
    ("Solution Architect", "the whole picture:", "flows, decisions, risks", I.PAL["blue"], 0),
    ("Platform Architect", "what must exist:", "runtime, data, security", I.PAL["teal"], 1),
    ("Application Architect", "how one agent works:", "tools, prompts, memory", I.PAL["plum"], 2),
    ("Ops and SRE", "how it runs:", "SLOs, alerts, runbooks", I.PAL["orange"], 3),
    ("Test Strategy", "how we prove it:", "evals, worlds, gates", I.PAL["green"], 0),
]
TABS = [I.PAL["peri"], I.PAL["mint"], I.PAL["lav"], I.PAL["peach"], I.PAL["butter"]]


def fig_team():
    n = 1
    b = I.blob(500, 165, 480, 140, "#EEF2FC")
    for i, (role, a, c, shirt, skin) in enumerate(ROLES):
        x = 100 + i * 200
        b += paper(x + 42, 92, 46, 62, TABS[i])
        b += I.person(x, 250, shirt, I.PAL["navy"], skin, reach=(x + 46, 128), scale=.68)
        b += t(x, 280, role, 20, hand=True) + t(x, 300, a, 13) + t(x, 316, c, 13, fill="#555")
        b += arrow(n, f"M{x},{324} C{x},{336} {500 + (x - 500) * .7},{340} {500 + (x - 500) * .72},{354}")
    b += box(n, 60, 358, 880, 52, WASH["butter"])
    for k in range(5):
        b += f'<rect x="{78 + k * 14}" y="{368}" width="10" height="32" rx="2" fill="{TABS[k]}" class="o" style="stroke-width:1.4"/>'
        b += f'<rect x="{852 + k * 14}" y="{368}" width="10" height="32" rx="2" fill="{TABS[4 - k]}" class="o" style="stroke-width:1.4"/>'
    b += t(500, 391, "The spec library: one place, versioned like code", 22, hand=True)
    return svg(n, 1000, 420, b, "Five people of the centre of excellence, each holding the spec they write, all feeding one spec library")


# ---------------------------------------------------------------- 2. four kinds of spec
QUADS = [
    (160, 40, WASH["peri"], "Catalogs", ["What every agent must have", "What must always be true", "How to describe a test world"], "written once, used by all"),
    (515, 40, WASH["rose"], "Agent spec", ["One agent's behaviour contract", "Its promises, limits, hand-offs", "Its world: customers and faults"], "one per agent"),
    (160, 245, WASH["mint"], "Bindings", ["Each concern mapped to a cloud", "Azure, AWS, GCP, Databricks", "The only place products appear"], "one per platform"),
    (515, 245, WASH["butter"], "The deployed agent", ["Claims agent on Azure: its config,", "its SLOs, alerts and runbooks,", "and the gate evidence"], "one per release"),
]


def fig_quad():
    n = 2
    b = ""
    for x, y, fill, title, lines, tag in QUADS:
        b += box(n, x, y, 345, 190, fill)
        b += t(x + 22, y + 38, title, 25, hand=True, anchor="start")
        for k, ln in enumerate(lines):
            b += t(x + 22, y + 72 + k * 24, ln, 14.5, anchor="start")
        b += f'<rect x="{x + 22}" y="{y + 146}" width="{len(tag) * 7.4 + 20}" height="26" rx="13" fill="#fff" stroke="{INK}" stroke-width="1.4"/>'
        b += t(x + 32, y + 164, tag, 12.5, anchor="start", bold=True)
    b += arrow(n, "M135,440 L135,48") + arrow(n, "M135,48 L135,440")
    b += t(70, 130, "Tech", 20, hand=True) + t(70, 152, "agnostic", 20, hand=True) + t(70, 172, "no product names", 11.5, fill="#555")
    b += t(70, 335, "Tech", 20, hand=True) + t(70, 357, "binding", 20, hand=True) + t(70, 377, "names the product", 11.5, fill="#555")
    b += arrow(n, "M165,462 L860,462") + arrow(n, "M860,462 L165,462")
    b += t(332, 492, "Domain agnostic", 20, hand=True) + t(332, 510, "any industry", 12, fill="#555")
    b += t(688, 492, "Domain and requirement specific", 20, hand=True) + t(688, 510, "one business, one agent", 12, fill="#555")
    return svg(n, 880, 520, b, "Two by two grid: tech agnostic or tech binding, against domain agnostic or domain specific, giving catalogs, agent specs, bindings and the deployed agent")


# ---------------------------------------------------------------- 3. what the COE builds
def fig_floors():
    n = 3
    b = ""
    # top floor: vertical agents
    b += box(n, 30, 30, 800, 110, WASH["rose"])
    b += t(50, 60, "Vertical agents, built by domain teams", 21, hand=True, anchor="start")
    for k, name in enumerate(["Insurance claims", "Banking service", "Hotel concierge", "Retail returns", "Clinical review"]):
        x = 50 + k * 155
        b += f'<path d="M{x},{125} L{x},{88} L{x + 67},{72} L{x + 135},{88} L{x + 135},{125} Z" fill="#fff" class="o" style="stroke-width:1.6"/>'
        b += t(x + 67, 110, name, 13.5)
    # middle floor: horizontal assets
    b += box(n, 30, 160, 800, 128, WASH["peri"])
    b += t(50, 190, "Horizontal assets, built once by the COE", 21, hand=True, anchor="start")
    assets = [("Reference", "architecture"), ("Reference", "implementation"), ("Agent Core", "Framework"),
              ("Eval", "Harness"), ("AgentTwin", "simulator"), ("Guardrail", "catalog")]
    for k, (a, c) in enumerate(assets):
        x = 50 + k * 128
        b += f'<rect x="{x}" y="206" width="118" height="66" rx="10" fill="#fff" class="o" style="stroke-width:1.6"/>'
        b += t(x + 59, 234, a, 14, bold=True) + t(x + 59, 254, c, 13.5)
    # ground floor: specs
    b += box(n, 30, 308, 800, 100, WASH["butter"])
    b += t(50, 338, "Specs, written by the COE", 21, hand=True, anchor="start")
    for k, (name, fill) in enumerate([("Catalogs", I.PAL["peri"]), ("Agent spec template", I.PAL["rose"]),
                                      ("Bindings per cloud", I.PAL["mint"]), ("Ops gate checklist", I.PAL["butter"])]):
        x = 50 + k * 194
        b += f'<rect x="{x}" y="352" width="182" height="40" rx="10" fill="{fill}" class="o" style="stroke-width:1.6"/>'
        b += t(x + 91, 377, name, 14)
    # cloud strip
    for k, (cx, name) in enumerate([(130, "Azure"), (330, "AWS"), (530, "GCP"), (730, "Databricks")]):
        b += (f'<path d="M{cx - 50},{462} C{cx - 70},{462} {cx - 70},{436} {cx - 48},{436} C{cx - 46},{418} {cx - 14},{414} {cx - 4},{428} '
              f'C{cx + 8},{412} {cx + 44},{416} {cx + 44},{436} C{cx + 66},{434} {cx + 68},{462} {cx + 48},{462} Z" fill="{WASH["sky"]}" class="o" style="stroke-width:1.6"/>')
        b += t(cx, 452, name, 14, bold=True)
    b += t(430, 492, "runs on any cloud: the binding decides which", 14, fill="#555")
    # feedback arrow
    b += arrow(n, "M845,90 C905,150 905,300 845,360", dash=True)
    b += f'<g transform="rotate(90 900 225)">{t(900, 220, "every agent feeds back down", 15, hand=True)}</g>'
    return svg(n, 940, 500, b, "A three-floor building: specs at the bottom, horizontal assets in the middle, vertical agents on top, running on any cloud, with a dashed arrow showing each agent feeds back into the floors below")


# ---------------------------------------------------------------- 4. one spec, many uses
USES = [("Build", "developers code to it"), ("Test", "test cases come from it"), ("Deploy", "release only if gates pass"),
        ("Operate (SRE)", "SLOs and alerts come from it"), ("Ops gate checklist", "tick every line, or stop"),
        ("Audit", "evidence for every rule"), ("Review", "check against it, not opinion"), ("Fail fast", "gaps show on day one")]
USE_FILL = [WASH["peri"], WASH["mint"], WASH["sky"], WASH["butter"], WASH["butter"], WASH["lilac"], WASH["rose"], WASH["mint"]]


def fig_uses():
    n = 4
    cx, cy = 450, 225
    b = ""
    pos = []
    for k in range(8):
        ang = math.radians(-90 + k * 45)
        pos.append((cx + 340 * math.cos(ang), cy + 172 * math.sin(ang)))
    for x, y in pos:
        b += f'<line x1="{cx}" y1="{cy}" x2="{x:.0f}" y2="{y:.0f}" stroke="{INK}" stroke-width="1.4" stroke-dasharray="5 6"/>'
    for (x, y), (title, sub), fill in zip(pos, USES, USE_FILL):
        b += box(n, x - 96, y - 27, 192, 54, fill, r=12)
        b += t(x, y - 4, title, 15.5, bold=True) + t(x, y + 15, sub, 12.5)
    b += f'<ellipse cx="{cx}" cy="{cy + 8}" rx="118" ry="70" fill="#fff"/>'
    b += I.book(cx - 90, cy - 30)
    b += f'<rect x="{cx - 58}" y="{cy + 58}" width="116" height="30" rx="8" fill="#fff"/>'
    b += t(cx, cy + 80, "The spec", 24, hand=True)
    return svg(n, 900, 450, b, "An open book labelled The spec in the middle, with dashed lines to eight uses: build, test, deploy, operate, ops gate checklist, audit, review and fail fast")


# ---------------------------------------------------------------- 5. one vertical agent, as a story
def robot(x, y):
    return (f'<circle cx="{x}" cy="{y}" r="56" fill="{WASH["mint"]}" stroke="{INK}" stroke-width="1.6" stroke-dasharray="5 5"/>'
            f'<line x1="{x}" y1="{y - 38}" x2="{x}" y2="{y - 28}" class="t"/><circle cx="{x}" cy="{y - 40}" r="4" fill="{I.PAL["coral"]}" class="o"/>'
            f'<rect x="{x - 22}" y="{y - 28}" width="44" height="30" rx="8" fill="#fff" class="o"/>'
            f'<circle cx="{x - 9}" cy="{y - 14}" r="3.5" fill="{INK}"/><circle cx="{x + 9}" cy="{y - 14}" r="3.5" fill="{INK}"/>'
            f'<rect x="{x - 18}" y="{y + 5}" width="36" height="28" rx="6" fill="{I.PAL["blue"]}" class="o"/>'
            f'<circle cx="{x - 38}" cy="{y + 22}" r="7" fill="{I.PAL["peach"]}" class="o" style="stroke-width:1.4"/>'
            f'<path d="M{x + 30},{y + 30} l6,-12 l6,12 Z" fill="{I.PAL["yellow"]}" class="o" style="stroke-width:1.4"/>')


def checklist(x, y):
    s = f'<rect x="{x}" y="{y}" width="84" height="108" rx="10" fill="#fff" class="o"/>'
    for k in range(4):
        yy = y + 22 + k * 22
        s += f'<rect x="{x + 12}" y="{yy - 8}" width="15" height="15" rx="3" fill="{I.PAL["mint"]}" class="o" style="stroke-width:1.5"/>'
        s += f'<path d="M{x + 15},{yy} l3,3 l6,-7" class="t" style="stroke:{I.PAL["green"]};stroke-width:2.4"/>'
        s += f'<line x1="{x + 34}" y1="{yy}" x2="{x + 72 - (k % 2) * 10}" y2="{yy}" stroke="#B9B6CC" stroke-width="1.8"/>'
    return s


def cloud(cx, cy):
    return (f'<path d="M{cx - 58},{cy + 26} C{cx - 84},{cy + 26} {cx - 84},{cy - 8} {cx - 56},{cy - 8} C{cx - 54},{cy - 32} {cx - 16},{cy - 38} {cx - 4},{cy - 20} '
            f'C{cx + 10},{cy - 40} {cx + 52},{cy - 34} {cx + 52},{cy - 8} C{cx + 80},{cy - 10} {cx + 82},{cy + 26} {cx + 56},{cy + 26} Z" fill="{WASH["sky"]}" class="o"/>')


STORY = [("Business owner", "says what it must do"), ("Agent spec", "COE specs + requirement"),
         ("Developer", "builds on the framework"), ("AgentTwin", "tests in a pretend world"),
         ("Ops gate", "all ticks, or no release"), ("Cloud", "serves real customers")]


def fig_story():
    n = 5
    xs = [85, 250, 415, 580, 745, 910]
    b = I.blob(500, 200, 490, 120, "#F6F2FC")
    b += arrow(n, "M910,140 C900,20 262,20 252,128", dash=True)
    b += num(380, 26, "7") + t(398, 31, "What each agent teaches us goes back into the specs and assets", 15, hand=True, anchor="start")
    b += I.person(xs[0], 250, I.PAL["coral"], I.PAL["navy"], 1, scale=.58)
    b += paper(xs[1] - 36, 140, 72, 92, I.PAL["rose"])
    b += I.person(xs[2] - 18, 250, I.PAL["teal"], I.PAL["navy"], 2, reach=(xs[2] + 22, 200), scale=.58)
    b += f'<g transform="translate({xs[2] + 14},178) scale(.42)">{I.laptop(0, 0)}</g>'
    b += robot(xs[3], 190)
    b += checklist(xs[4] - 42, 136)
    b += cloud(xs[5], 192)
    for k in range(5):
        a, c = xs[k] + 56, xs[k + 1] - 60
        if k == 2:
            a += 12
        if k == 4:
            c -= 28
        b += arrow(n, f"M{a},196 L{c},196")
    for k, (x, (title, sub)) in enumerate(zip(xs, STORY)):
        b += num(x - 52, 120, str(k + 1))
        b += t(x, 282, title, 19, hand=True) + t(x, 301, sub, 12.5, fill="#444")
    return svg(n, 1000, 320, b, "Six numbered steps: a business owner states the need, it becomes an agent spec, a developer builds it, AgentTwin tests it, the ops gate is ticked, and it runs in the cloud; a dashed arrow carries the lessons back to the spec")


# ---------------------------------------------------------------- 6. the flywheel, with evidence
def fig_flywheel():
    n = 6
    cx, cy, r = 262, 200, 150
    b = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{WASH["peri"]}" stroke="none"/>'
    for a0, a1 in [(-75, -15), (15, 75), (105, 165), (195, 255)]:
        p0 = (cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0)))
        p1 = (cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1)))
        b += arrow(n, f"M{p0[0]:.0f},{p0[1]:.0f} A{r},{r} 0 0 1 {p1[0]:.0f},{p1[1]:.0f}")
    nodes = [(cx, cy - r, "Build an agent", 150), (cx + r, cy, "Find the gaps", 140),
             (cx, cy + r, "Fix the specs and assets", 196), (cx - r, cy, "Next one starts stronger", 190)]
    for x, y, s, w in nodes:
        b += f'<rect x="{x - w / 2}" y="{y - 20}" width="{w}" height="40" rx="12" fill="#fff" class="o" style="stroke-width:1.6"/>'
        b += t(x, y + 6, s, 15, bold=True)
    b += t(cx, cy - 4, "The harness", 20, hand=True) + t(cx, cy + 20, "bundle grows", 20, hand=True)
    # bar chart
    x0, base = 540, 330
    b += t(700, 46, "Gaps found when the agent was rebuilt", 17, hand=True) + t(700, 66, "from the specs alone", 17, hand=True)
    b += f'<line x1="{x0}" y1="{base}" x2="880" y2="{base}" class="t" style="stroke-width:1.8"/>'
    for k, (run, gaps, fill, note) in enumerate([("Run 3", 28, I.PAL["coral"], ""), ("Run 4", 24, I.PAL["yellow"], "6 repeats"),
                                                  ("Run 5", 8, I.PAL["green"], "0 repeats")]):
        x = x0 + 30 + k * 115
        h = gaps * 7.5
        b += f'<rect x="{x}" y="{base - h}" width="70" height="{h}" rx="6" fill="{fill}" class="o" style="stroke-width:1.6"/>'
        b += t(x + 35, base - h - 10, str(gaps), 20, hand=True) + t(x + 35, base + 22, run, 14, bold=True)
        if note:
            b += t(x + 35, base + 40, note, 12.5, fill="#555")
    return svg(n, 900, 380, b, "A loop of build, find gaps, fix the specs, next one starts stronger; beside it a bar chart where gaps fall from 28 in run 3 to 24 in run 4 to 8 in run 5")


# ---------------------------------------------------------------- page text
def fig(svg_text, caption):
    return f'<figure class="sd-fig">{svg_text}<figcaption>{caption}</figcaption></figure>'


ROLE_CARDS = [
    ("peri", "Solution Architect", "The whole picture: which business flow, which decisions the agent may take on its own and which need a person, and the main risks.",
     "Writes the agent's purpose, its boundaries and who it hands over to."),
    ("mint", "Platform Architect", "What every agent must have underneath it: runtime, identity, secrets, data access, logging, cost metering.",
     "Writes the catalogs and the binding for each cloud."),
    ("lilac", "Application Architect", "How one agent is put together: its tools, its prompts, its memory, how it recovers when a tool fails.",
     "Writes the agent spec template and the reference implementation."),
    ("butter", "Ops and SRE", "How it runs in production: response-time and error targets (SLOs), alerts, runbooks, rollback, cost limits.",
     "Writes the operations spec and the ops gate checklist."),
    ("rose", "Test Strategy", "How we prove it works: which promises need tests, which pretend worlds and faults to try, what counts as a pass.",
     "Writes the test spec and the world descriptions for AgentTwin."),
]

CHECKS = [
    ("Every promise in the agent spec has a passing test.", "Agent spec + test strategy"),
    ("The agent passed its AgentTwin worlds, including faults: a tool goes down, a customer is angry, a request is out of scope.", "World description"),
    ("Response-time, error-rate and cost-per-conversation targets are set, and an alert fires when each is missed.", "Operations spec"),
    ("Every alert has a runbook and a named person on call.", "Operations spec"),
    ("Personal data is masked in logs; out-of-scope requests are refused and handed to a person.", "Assurance catalog"),
    ("Model and prompt versions are pinned, and rollback has been tried once.", "Platform catalog + binding"),
    ("A daily cost budget with a hard stop is switched on.", "Operations spec"),
]

PARALLEL = [
    ("What every system must have", "AI Harness Catalog (AHC)", "Data Platform Catalog (DPC)"),
    ("What must always be true", "AI Assurance Catalog (AAC)", "Data Assurance Catalog (DAC)"),
    ("The world it must face", "Agent world description", "Data World Description (DWD)"),
    ("What this one system does", "Agent spec, one per agent", "Data Platform Manifest (DPM), one per company"),
    ("Which product does each job", "Binding per cloud", "Data Binding Spec (DBS)"),
    ("Practice before it is real", "AgentTwin", "DataTwin"),
    ("Working example to copy", "Reference agent and Agent Core Framework", "Reference data platform framework"),
]

BODY = f"""<main class="wrap">
<div class="hero"><p class="eyebrow">For leaders · ways of working</p><h1>{TITLE}</h1>
<p class="thesis">A small centre of excellence (COE) writes the specs once and builds the shared parts once. After that, every agent and every data platform is <em>built, tested, released and run from the same specs</em>, and each one we build makes the specs stronger for the next.</p></div>

{fig(fig_team(), "The COE: five roles, five kinds of spec, one library. Each role writes the part only they know well.")}

<div class="sd-stat">
<div><b>5 roles</b>write the specs: solution, platform and application architects, Ops and SRE, test strategy</div>
<div><b>4 kinds</b>of spec, from "any company, any cloud" down to "this agent on Azure"</div>
<div><b>8 uses</b>for one spec: build, test, review, deploy, operate, gate, audit, fail fast</div>
<div><b>28 → 8</b>gaps when we rebuilt an agent from the specs alone, run 3 to run 5</div>
</div>

<div class="sd-answer">
<p><b>The one-minute version.</b> Today most teams build each agent from scratch, and the knowledge lives in people's heads. Testers guess what to test, Ops learns how it behaves after go-live, and reviews come down to opinion.</p>
<p>With spec-driven development, that knowledge is written down once, in plain words, by the people who know it best. Developers build to it, testers test against it, Ops releases against it as a checklist, and auditors read it. When something goes wrong, we <b>fix the spec first</b>, so the next agent never makes the same mistake.</p>
</div>

<section><p class="eyebrow">Why change</p><h2>Building without specs, and building with them</h2>
<div class="sd-table"><table>
<tr><th>Today, without specs</th><th>With spec-driven development</th></tr>
<tr><td>Each team reinvents logging, guardrails, retries and cost control</td><td>The COE builds them once; every agent reuses them</td></tr>
<tr><td>Testers read the code to guess what "working" means</td><td>Every promise in the spec becomes a test case</td></tr>
<tr><td>Ops meets the agent for the first time at go-live</td><td>Ops wrote its targets, alerts and runbooks into the spec before the build began</td></tr>
<tr><td>Reviews are opinion against opinion</td><td>Reviews check the work against the spec, line by line</td></tr>
<tr><td>Problems show up in production, from customers</td><td>Gaps show up on day one, when the spec cannot answer a question</td></tr>
<tr><td>Changing cloud means rebuilding</td><td>Changing cloud means writing a new binding; the specs stay the same</td></tr>
<tr><td>The tenth agent costs about as much as the first</td><td>The tenth agent is faster and safer, because nine agents improved the specs</td></tr>
</table></div></section>

<section><p class="eyebrow">Who writes the specs</p><h2>The COE team</h2>
<p>Five roles. Each writes the part of the spec that only they know well. No role has to read the whole library; each opens the part that is theirs.</p>
<div class="sd-cards">
{"".join(f'<div class="sd-card {c}"><h3>{r}</h3><p>{what}</p><p><span class="lbl">Writes</span>{writes}</p></div>' for c, r, what, writes in ROLE_CARDS)}
</div></section>

<section><p class="eyebrow">Four kinds of spec</p><h2>Some specs fit every company, some fit one agent</h2>
<p>Two simple questions sort every spec. Does it name a product or cloud (tech binding), or not (tech agnostic)? Does it fit any industry (domain agnostic), or one business and one requirement (domain specific)?</p>
{fig(fig_quad(), "Top left is written once and used by every agent. Bottom right exists once per release. Product names live only in the bottom row, so changing cloud never touches the top row.")}
<p>Keeping the four apart is what makes the specs reusable. The catalogs on the top left are the same for an insurance agent and a hotel agent, so the second agent gets them for free.</p></section>

<section><p class="eyebrow">What the COE builds</p><h2>Specs first, then shared assets, then many agents</h2>
<p>The COE does not only write documents. It also builds the <b>horizontal assets</b>: the parts every agent needs, whatever its industry. Domain teams then build <b>vertical agents</b> on top, one per business problem.</p>
{fig(fig_floors(), "Like a building: the specs are the foundation, the shared assets are the middle floor, and each domain team adds its own agent on top.")}
<div class="sd-table"><table>
<tr><th>Horizontal asset</th><th>What it gives every agent team</th></tr>
<tr><td>Reference architecture</td><td>The agreed picture of how an agent is put together, with no product names</td></tr>
<tr><td>Reference implementation</td><td>A working agent that passes every gate, to copy from (<a href="https://github.com/dataagentsai/reference-agent">reference agent</a>)</td></tr>
<tr><td>Agent Core Framework</td><td>The shared code: the agent loop, tools, memory, retries, logging and cost metering</td></tr>
<tr><td>Eval Harness</td><td>One way to score answers and behaviour, across test tools (<a href="https://github.com/dataagentsai/eval-harness-framework">Eval Harness Framework</a>)</td></tr>
<tr><td>AgentTwin</td><td>A pretend world of customers, tools and faults to test the agent in before it meets real people (<a href="/learn/agenttwin/">AgentTwin, explained</a>)</td></tr>
<tr><td>Guardrail catalog</td><td>57 common guardrails, each with the test that proves it holds (<a href="/learn/agent-guardrails/">the catalog</a>)</td></tr>
</table></div></section>

<section><p class="eyebrow">Not only for developers</p><h2>One spec, eight uses</h2>
<p>Most people think a spec is something developers read before coding. Here the same spec also drives testing, release, operations and audit. That is where most of the saving comes from.</p>
{fig(fig_uses(), "Testers, reviewers, Ops, SRE and auditors all work from the same spec the developers built to, so nobody works from a different idea of what 'done' means.")}
<h3 style="font-family:var(--hand);font-size:26px;font-weight:400;margin:24px 0 4px">Example: the ops gate checklist</h3>
<p>Before an agent goes live, Ops ticks a checklist. Nobody writes this list by hand. It is generated from the specs, and every line says which spec it came from. If a line cannot be ticked, the release stops.</p>
<ul class="sd-check">
{"".join(f'<li><span class="box">✓</span><span>{c}</span><span class="from">From: {f}</span></li>' for c, f in CHECKS)}
</ul>
<p>The same lines help testers (they know exactly what to prove), reviewers (they check the evidence, not the code style) and SRE (the targets and alerts were agreed before the build, not after an incident).</p></section>

<section><p class="eyebrow">Then, the vertical agents</p><h2>How one domain agent gets built</h2>
<p>Once the COE layer is in place, a domain team can build an agent for insurance, banking, hospitality, retail or healthcare by following the same six steps every time.</p>
{fig(fig_story(), "Step 7 is the important one. What each agent teaches us flows back into the COE's specs and shared assets.")}
<ol>
<li><b>The business owner</b> says, in plain words, what the agent must do, and what it must never do.</li>
<li><b>The agent spec</b> is built by filling in the COE template: the requirement plus the catalogs it inherits.</li>
<li><b>Developers</b> build on the Agent Core Framework, so they only write what is special to this business.</li>
<li><b>AgentTwin</b> tests the agent in a pretend world with realistic customers and faults, before any real customer sees it.</li>
<li><b>Ops</b> ticks the gate checklist. Every line traces back to a spec.</li>
<li><b>The cloud binding</b> deploys it to Azure, AWS, GCP or Databricks.</li>
<li><b>Lessons go back</b> to the COE: a missing rule, a new fault, a better default.</li>
</ol></section>

<section><p class="eyebrow">Why it gets better with time</p><h2>Every agent makes the bundle stronger</h2>
<p>The specs, the framework, the eval harness and AgentTwin together form the <b>harness bundle</b>. It is not finished when the COE starts. It grows a little with every agent built on it.</p>
{fig(fig_flywheel(), "Measured: we rebuilt the same agent from the specs alone, fixed every gap it found, and rebuilt again. Gaps fell from 28 (run 3) to 8 (run 5), and none of run 4's gaps came back.")}
<p>That is the business case in one picture. The first agent pays for the COE layer. Every agent after that costs less, takes less time, and fails less in production, because it starts from everything the earlier agents taught us.</p></section>

<section><p class="eyebrow">Same way for data</p><h2>The same method works for data engineering</h2>
<p>We use the same pattern for data platforms. The roles and the four kinds of spec are the same; only the subject changes.</p>
<div class="sd-table"><table>
<tr><th>Question the spec answers</th><th>AI engineering (agent harness)</th><th>Data engineering</th></tr>
{"".join(f"<tr><td>{q}</td><td>{a}</td><td>{d}</td></tr>" for q, a, d in PARALLEL)}
</table></div>
<p>Read more: <a href="/learn/data-platform-architecture/">data platform architecture</a>, <a href="/learn/datatwin/">DataTwin, explained</a>, <a href="https://dataagentsai.github.io/ai-harness-catalog/">AI Harness Catalog</a>, <a href="https://dataagentsai.github.io/ai-assurance-catalog/">AI Assurance Catalog</a>.</p></section>

<section><p class="eyebrow">The case for leaders</p><h2>What you get, and what it takes</h2>
<div class="sd-cards">
<div class="sd-card peri"><h3>For business leaders</h3>
<p>Faster second, third and tenth agents, because most of the work is already done.</p>
<p>Fewer surprises in production, because agents meet faults in AgentTwin first.</p>
<p>Audit-ready from day one: every rule has a spec line and evidence.</p>
<p>No lock-in: changing cloud is a new binding, not a rebuild.</p></div>
<div class="sd-card mint"><h3>For technology leaders</h3>
<p>One way of building across teams, so people can move between agents.</p>
<p>Testers, Ops and SRE join at the start, not at go-live.</p>
<p>Reviews become checks against the spec, so they are faster and fairer.</p>
<p>Gaps surface on day one, when they are cheap to fix.</p></div>
<div class="sd-card butter"><h3>What it takes</h3>
<p><b>Time up front.</b> The first agent is slower, because the COE layer is being built alongside it.</p>
<p><b>Discipline.</b> "Fix the spec first" must be a rule, or the specs drift from the code and stop being trusted.</p>
<p><b>Five named people.</b> The COE roles need owners with time set aside, not volunteers.</p></div>
</div></section>

<section><p class="eyebrow">How to start</p><h2>Onboarding in three steps</h2>
<ol class="sd-steps">
<li><h3>1 · Crawl: one pilot</h3><p>Pick one agent that matters but is not the riskiest. Use the open catalogs and the agent spec template as they are.</p><p>Run the ops gate checklist on it, even by hand.</p><p><b>You learn:</b> where your teams' unwritten knowledge lives.</p></li>
<li><h3>2 · Walk: form the COE</h3><p>Name the five roles. Write the binding for your cloud. Adopt the Agent Core Framework, Eval Harness and AgentTwin for the pilot.</p><p><b>You get:</b> a second agent built in much less time than the first.</p></li>
<li><h3>3 · Run: vertical agents</h3><p>Domain teams build agents on the COE layer. AgentTwin runs on every change, and the ops gate is required for every release.</p><p><b>You get:</b> a harness bundle that improves with every agent.</p></li>
</ol></section>

<section class="sd-qa"><p class="eyebrow">Questions</p><h2>Questions leaders ask</h2>
<h3>Isn't this just waterfall with a new name?</h3>
<p>No. We work in thin slices: write a little spec, build it, test it, and fix the spec where the build showed it was wrong. Then the next slice. The spec is a living document that changes every week, not a big document signed off up front.</p>
<h3>Won't writing specs slow us down?</h3>
<p>The first agent, a little. After that it is faster, because most of the spec is inherited from the catalogs, and testers, Ops and reviewers stop asking questions the spec already answers.</p>
<h3>Did you invent this method?</h3>
<p>No. We follow the open OpenSpec way of working and borrow good ideas from GitHub Spec Kit and Kiro. What we add is what those leave out for agents: behaviour promises, operations and SLOs, testing in a pretend world, and mapping to rules such as the EU AI Act and ISO 42001.</p>
<h3>Who owns the specs?</h3>
<p>The COE owns the catalogs, templates and shared assets. Each domain team owns its own agent spec. A change to a shared spec goes through the COE, like a change to shared code.</p>
<h3>Can AI write the specs for us?</h3>
<p>AI helps a lot with drafting and with asking clarifying questions. But the decisions in a spec, such as what the agent may do alone and when it must stop, belong to people who can be held accountable for them.</p>
<h3>What if we change cloud or vendor later?</h3>
<p>Only the binding changes. The catalogs, the agent specs and the tests stay as they are, because they never named a product.</p>
</section>

<section><p class="eyebrow">Talk to us</p><h2>Want to try this with your team?</h2>
<p>Everything on this page is open: the catalogs, the reference agent, the Eval Harness Framework and AgentTwin. If you would like to walk through it with your leadership team, or pilot it on one agent, write to <a href="mailto:basant@cleandataengineering.ai?subject=Spec-driven%20development">basant@cleandataengineering.ai</a>.</p>
<p><a href="/leaders/">Back to For leaders</a></p></section>
</main>
"""


def main():
    head_end = SRC.index("</style>")
    head = SRC[:head_end] + CSS + SRC[head_end:SRC.index("<main")]
    head = re.sub(r"<title>.*?</title>", f"<title>{TITLE} · Clean Data Engineering</title>", head, count=1)
    head = re.sub(r'(<meta name="description" content=")[^"]*', rf"\g<1>{DESC}", head, count=1)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', rf"\g<1>{TITLE}", head, count=1)
    head = re.sub(r'(<meta property="og:description" content=")[^"]*', rf"\g<1>{DESC}", head, count=1)
    head = head.replace("https://cleandataengineering.ai/mindset/", URL)
    foot = SRC[SRC.index("<footer>"):]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(head + BODY + foot)
    print("wrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
