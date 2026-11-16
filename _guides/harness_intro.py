"""Agent Harness, the big picture: a roadmap page plus six detail pages at /learn/agent-harness-intro/.

    python3 _guides/harness_intro.py      (then python3 _site/nav.py and python3 _site/seo.py)

Made for talking through on a screen share: the roadmap page links to every stop, every stop has one
simple drawing, and two stops are simulations that run in the browser with scripted replies.

Stops 1 to 5 and 7 are built here. Stop 6 (the horse) and stop 8 (the worked example) already exist in
the Agent Harness tutorial and its simulator, so the roadmap links to them.

The code on the "same job, two ways" page is read from _guides/code/harness_intro/ and run at build
time, so the page always shows code that works and the output it really printed.
"""
import json
import subprocess
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "_paths"))
import components as C  # noqa: E402
import harness_intro_reqs as R  # noqa: E402
import harness_intro_sims as S  # noqa: E402

wb = C.wb
kit = wb.kit
SITE = wb.SITE
BASE = "/learn/agent-harness-intro/"
CODE_DIR = Path(__file__).parent / "code" / "harness_intro"
CODE_URL = "https://github.com/dataagentsai/cleandataengineering-site/tree/main/_guides/code/harness_intro"
TUTORIAL = "/learn/agent-harness/"

# n, page path (None = an existing page elsewhere), title, the question it answers, kind, link
STOPS = [
    (1, "kinds/", "Three kinds of AI application", "Single call, workflow or agent: who decides the next step?", "Page"),
    (2, "autonomous-agents/", "Autonomous agents", "What are they, and why do businesses want them?", "Page"),
    (3, "code/", "Same job, two ways", "What does ordinary code look like next to an agent?", "Code"),
    (4, "loop-sim/", "Simulation: the agent loop", "What goes to the model, what comes back, and why does it go round?", "Simulation"),
    (5, "no-guardrails-sim/", "Simulation: no guardrails", "What goes wrong without guardrails, and what does it cost?", "Simulation"),
    (6, None, "The horse and the harness", "What is an agent harness, in one picture?", "Page"),
    (7, "requirements/", "What a harness must do", "What are all the requirements, one simple picture at a time?", "Pages"),
    (8, "architecture/", "The architecture, simple then zoomed in", "Where does everything sit, and what are the five families of concerns?", "Page"),
    (9, None, "Worked example: one claim, end to end", "How does it all work in one real agent?", "Page and simulation"),
]
EXTERNAL = {6: TUTORIAL + "arch-horse.html", 9: TUTORIAL + "flow.html"}
REQ_BASE = BASE + "requirements/"


def url(n):
    stop = STOPS[n - 1]
    return EXTERNAL[n] if stop[1] is None else BASE + stop[1]


CSS = C.CSS + wb.kit_css() + R.CSS + """<style>
  .hi h2 { margin-top:38px; } .hi .lede { font-size:20px; }
  .stops { display:flex; flex-wrap:wrap; gap:6px; align-items:center; margin:14px 0 4px; font-size:14px; }
  .stops a, .stops span { border:1.5px solid var(--ink); border-radius:999px; padding:1px 11px; text-decoration:none; color:var(--ink); background:#fff; }
  .stops span.on { background:var(--ink); color:#fff; } .stops a.rm { background:var(--butter-wash); font-weight:600; }
  .zoom { font-size:12px; font-weight:700; letter-spacing:.07em; text-transform:uppercase; color:var(--muted); margin:18px 0 0; }
  table.road td:first-child { font-family:var(--hand); font-size:24px; width:34px; } table.road td { font-size:15px; }
  table.road .k { font-size:11.5px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; border:1.5px solid var(--ink); border-radius:999px; padding:1px 9px; white-space:nowrap; background:#fff; }
  table.road .k.Simulation { background:var(--butter); } table.road .k.Code { background:var(--peri-wash); }
  a.go { display:inline-block; font:600 14.5px var(--sans); border:1.5px solid var(--ink); border-radius:999px; padding:5px 16px; background:var(--ink); color:#fff; text-decoration:none; margin:4px 8px 4px 0; }
  a.go.alt { background:#fff; color:var(--ink); }
  .pn { display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap; border-top:1.5px dashed var(--rule-firm); margin-top:40px; padding-top:16px; }
  .say { border:var(--line); border-radius:var(--wob); padding:10px 18px; margin:16px 0; background:var(--butter-wash); font-size:16px; }
  .say b:first-child { font-family:var(--hand); font-weight:400; font-size:22px; display:block; }
  .hi table.t td { font-size:14.5px; } .hi pre.code { font-size:12.2px; }
  .hi .drawing a.lk:hover rect.ol { stroke-width:3.5px; }
  pre .l { display:block; } pre .l::before { content:attr(data-n); display:inline-block; width:2.2em; margin-right:1em; padding-right:.7em; text-align:right; color:var(--faint); border-right:1px solid var(--rule-firm); user-select:none; }
</style>"""


# ----------------------------------------------------------------------------- drawings

def fig(w, h, body, label, caption):
    return wb.figure(w, h, body, label, caption)


def d_roadmap():
    b, a, t, n = kit.box, kit.arrow, kit.text, kit.num
    cards = [(["Three kinds of", "AI application"], "who decides the next step?", "bx"),
             (["Autonomous", "agents"], "why businesses want them", "bx"),
             (["Same job,", "two ways"], "the code, side by side", "bx"),
             (["Simulation:", "the agent loop"], "request, response, repeat", "bxs"),
             (["Simulation:", "no guardrails"], "what goes wrong, the cost", "bxs"),
             (["The horse and", "the harness"], "keep it on the green road", "solid"),
             (["What a harness", "must do"], "one picture for each need", "bx"),
             (["The architecture"], "simple, then zoomed in", "bx"),
             (["Worked example:", "one claim"], "a real agent, end to end", "bx")]
    d = ""
    for i, (title, sub, kind) in enumerate(cards):
        top = i < 5
        col = i if top else 4 - (i - 5)
        x, y = 10 + col * 198, 34 if top else 184
        d += b(x, y, 184, 96, title, sub, kind, href=url(i + 1), tag="open") + n(x + 12, y + 2, i + 1)
        if top and i < 4:
            d += a(x + 186, y + 48, x + 196, y + 48)
        if not top and i < 8:
            d += a(x - 2, y + 48, x - 12, y + 48)
    d += a(894, 132, 894, 182)
    d += t(500, 312, "yellow = a simulation you can play · lavender = the picture everything else hangs on", "sm", "middle")
    return fig(1000, 325, d, "A road of nine numbered stops in two rows. Top row, left to right: three kinds of AI application, autonomous agents, same job two ways, the agent loop simulation, the no-guardrails simulation. Bottom row, right to left: the horse and the harness, what a harness must do, the architecture, and a worked example.",
               "The whole road on one picture. Click any stop to open it.")


def d_reqs():
    b, a, t = kit.box, kit.arrow, kit.text
    g = {slug: (title, len(reqs)) for slug, title, _blurb, reqs in R.GROUPS}
    d = t(40, 22, "ON THE PATH OF EVERY REQUEST", "lbl")
    path = [("receive", ["Receive", "the request"], "bxs"), ("think", ["Think: the loop", "and the model"], "solid"), ("act", ["Act: tools,", "checks, people"], "bx")]
    for i, (slug, title, kind) in enumerate(path):
        d += b(40 + i * 320, 40, 280, 92, title, f"{g[slug][1]} requirements", kind, href=REQ_BASE + slug + "/", tag="open")
        if i < 2:
            d += a(322 + i * 320, 86, 358 + i * 320, 86)
    d += t(10, 172, "AROUND EVERY REQUEST", "lbl")
    around = [("keep-going", ["Keep going"], "failures, speed, scale"), ("see", ["See"], "logs, traces, cost"), ("change", ["Prove and change"], "evals, tests, release"), ("protect", ["Protect"], "secrets, data, the law")]
    for i, (slug, title, sub) in enumerate(around):
        d += b(10 + i * 248, 190, 236, 92, title, [sub, f"{g[slug][1]} requirements"], "bxm", href=REQ_BASE + slug + "/", tag="open")
    return fig(1000, 296, d, "Seven groups of requirements. On the path of every request: receive the request, think with the loop and the model, act with tools, checks and people. Around every request: keep going, see, prove and change, protect.",
               "Seven groups. The top row is what an agent does. The bottom row is how well and how safely it does it.")


def d_kinds():
    b, a, t, p = kit.box, kit.arrow, kit.text, kit.path
    d = '<line class="lnd" x1="333" y1="12" x2="333" y2="226"/><line class="lnd" x1="667" y1="12" x2="667" y2="226"/>'
    d += t(165, 34, "1 · Single call", "tt", "middle")
    d += b(15, 60, 92, 62, "You ask", kind="bxm") + a(109, 91, 123, 91) + b(125, 60, 92, 62, "Model", kind="solid") + a(219, 91, 233, 91) + b(235, 60, 86, 62, "Answer", kind="bxm")
    d += t(165, 190, ["One question, one answer.", "There is no next step."], "sm", "middle")
    d += t(500, 34, "2 · Workflow", "tt", "middle")
    d += b(348, 60, 92, 62, "Step 1", "your code") + a(442, 91, 456, 91) + b(458, 60, 92, 62, "Step 2", "model", "solid") + a(552, 91, 566, 91) + b(568, 60, 88, 62, "Step 3", "your code")
    d += t(500, 190, ["Fixed steps in a fixed order.", "Your code decides the next step."], "sm", "middle")
    d += t(835, 34, "3 · Agent", "tt", "middle")
    d += b(690, 60, 120, 62, "Model", "decides", "solid") + b(868, 60, 120, 62, "Tools", "your code")
    d += a(812, 80, 866, 80) + a(866, 104, 812, 104) + p("M928,124 Q839,172 750,124")
    d += t(835, 190, ["Round and round until done.", "The model decides the next step."], "sm", "middle")
    d += a(60, 262, 940, 262) + t(500, 250, "more freedom for the model, so more harness is needed", "bd", "middle")
    return fig(1000, 280, d, "Three small pictures side by side. Single call: you ask, the model answers. Workflow: three fixed steps in a row, one of them a model call. Agent: the model and the tools in a loop. An arrow underneath says more freedom for the model means more harness is needed.",
               "Lavender boxes are model calls. Blue boxes are your own code. The kind depends on one thing: who decides the next step.")


def d_dial():
    b, a, t = kit.box, kit.arrow, kit.text
    levels = [("0 · Answer", ["a person reads it", "and decides"], "bxm"), ("1 · Suggest", ["a person takes", "the action"], "bx"),
              ("2 · Act with OK", ["a person approves", "each important step"], "bx"), ("3 · Act in limits", ["a person reviews", "afterwards"], "bxs"),
              ("4 · Unattended", ["a person sets goals", "and reads the report"], "solid")]
    d = "".join(b(10 + i * 198, 24, 184, 100, title, sub, kind) for i, (title, sub, kind) in enumerate(levels))
    d += a(30, 158, 970, 158) + t(500, 186, "more freedom for the AI, less checking by a person", "bd", "middle")
    return fig(1000, 200, d, "Five boxes in a row, levels zero to four: answer, suggest, act with approval, act within limits, run unattended. An arrow underneath says more freedom for the AI means less checking by a person.",
               "Autonomy is a dial with five positions, not a switch. Most business value today sits at levels 2 and 3.")


def loop_body(ids=False):
    b, a, t = kit.box, kit.arrow, kit.text

    def g(i, s):
        return f'<g class="st" id="{i}">{s}</g>' if ids else s

    d = b(10, 30, 142, 84, "A person", "asks", "bxm") + a(154, 72, 186, 72)
    d += g("s1", b(190, 30, 232, 84, "1 · Send the request", "all messages + the tool list"))
    d += g("s2", b(520, 30, 232, 84, "2 · The model replies", "an answer, or \"run this tool\"", "solid"))
    d += g("s3", b(520, 250, 232, 84, "3 · Run the tool", "our code runs it, not the model", "bxs"))
    d += g("s4", b(190, 250, 232, 84, "4 · Add the result", "to the messages"))
    d += g("sgoal", b(830, 30, 160, 84, "Goal reached", ["no tool asked for:", "that is the answer"], "bxm"))
    d += g("slimit", b(10, 250, 142, 84, "Limit reached", ["stop, and", "hand over"], "bxm"))
    d += a(424, 72, 518, 72) + a(636, 116, 636, 248) + a(518, 292, 424, 292) + a(306, 248, 306, 116)
    d += a(754, 72, 828, 72) + a(188, 292, 154, 292)
    d += t(646, 186, "it asked for a tool", "sm") + t(296, 186, "go again", "sm", "end")
    d += t(471, 176, "the agent loop", "bd", "middle") + t(471, 198, "one turn = one model call", "sm", "middle")
    return d


LOOP_LABEL = ("A loop of four boxes. One: our code sends the request with all messages and the tool list. Two: the model replies with an answer or a tool request. "
              "Three: our code runs the tool. Four: the result is added to the messages, and the loop goes again. Two exits: goal reached when the model asks for no tool, and limit reached when there have been too many turns.")


def d_loop():
    return fig(1000, 350, loop_body(), LOOP_LABEL, "The agent loop. It ends in one of two ways: the model answers, or our code says \"enough\".")


def d_arch_simple():
    b, a, t = kit.box, kit.arrow, kit.text
    d = b(10, 20, 124, 410, "Lifecycle", ["idea", "build", "test", "release", "monitor", "learn"], "bxm")
    d += b(866, 20, 124, 410, "Governance", ["a named owner", "a risk level", "an audit trail", "the law"], "bxm")
    d += b(160, 20, 680, 66, "People ask", "customers, partners and staff · on chat, WhatsApp, email", "bxm") + a(500, 88, 500, 104)
    d += b(160, 106, 680, 66, "The front door", "every request is checked before any agent sees it", "bxs") + a(500, 174, 500, 190)
    d += b(160, 192, 215, 66, "Claims intake", "an agent", "solid") + b(392, 192, 216, 66, "Policy servicing", "an agent") + b(625, 192, 215, 66, "Renewals", "and more agents")
    d += a(500, 260, 500, 276)
    d += b(160, 278, 680, 66, "Shared parts", "built once, used by every agent") + a(500, 346, 500, 362)
    d += b(160, 364, 680, 66, "Business systems", "policies, claims, payments: the real records", "bxm")
    return fig(1000, 450, d, "Five bands from top to bottom: people ask; the front door checks every request; agents, one per business job; shared parts built once and used by every agent; business systems holding the real records. A lifecycle rail runs down the left side and a governance rail down the right.",
               "The architecture in five bands and two rails. Only the row of agents changes from one business to the next.")


FAMILIES = [
    ("Think", ["What does it know,", "how does it decide?"], ["Model gateway", "Knowledge", "Memory & state"], "solid"),
    ("Act", ["What can it do?"], ["Tool hub", "Channel adapters"], "bx"),
    ("Control", ["Is it safe", "and allowed?"], ["Identity & access", "Guardrails", "Human desk"], "bxs"),
    ("See", ["What did it do,", "what did it cost?"], ["Observability", "Cost control"], "bx"),
    ("Change", ["Is it good? Can we", "change it safely?"], ["Eval library", "Release & config"], "bx"),
]


def d_families():
    b, t = kit.box, kit.text
    d = t(500, 26, "SHARED PARTS · zoomed in", "lbl", "middle")
    for i, (name, q, members, kind) in enumerate(FAMILIES):
        x = 10 + i * 198
        d += b(x, 40, 184, 92, name, q, kind)
        for j, m in enumerate(members):
            d += b(x + 8, 148 + j * 58, 168, 46, m, kind="bxm")
    return fig(1000, 330, d, "The shared parts zoomed in, as five families. Think: model gateway, knowledge, memory and state. Act: tool hub, channel adapters. Control: identity and access, guardrails, human desk. See: observability, cost control. Change: eval library, release and config.",
               "Twelve shared parts in five families. Each family answers one question a business will ask about any agent.")


def d_fnol():
    b, a = kit.box, kit.arrow
    steps = [("Rohan", ["reports a car", "accident on chat"], "bxm"), ("Front door", ["who is asking?", "anything hidden?"], "bxs"),
             (["Claims intake", "agent"], ["the loop from stop 4"], "solid"), ("Tools", ["look up the policy,", "create the claim"], "bx"),
             ("Rohan is told", ["claim C-501", "is registered"], "bxm")]
    d = ""
    for i, (title, sub, kind) in enumerate(steps):
        d += b(10 + i * 200, 20, 180, 104, title, sub, kind)
        if i < 4:
            d += a(192 + i * 200, 72, 208 + i * 200, 72)
    return fig(1000, 140, d, "Five boxes in a row: Rohan reports a car accident on chat; the front door checks who is asking and whether anything is hidden; the claims intake agent runs the loop; the tools look up the policy and create the claim; Rohan is told that claim C-501 is registered.",
               "One claim, end to end. Every box here is a place where the earlier stops show up again.")


# ----------------------------------------------------------------------------- shared page parts

def stepper(cur):
    out = [f'<a class="rm" href="{BASE}">Roadmap</a>']
    for n, _path, title, *_ in STOPS:
        out.append(f'<span class="on" title="{E(title)}">{n}</span>' if n == cur else f'<a href="{url(n)}" title="{E(title)}">{n}</a>')
    return f'<nav class="stops" aria-label="Stops on the road">{"".join(out)}</nav>'


def prevnext(cur):
    left = f'<a class="go alt" href="{url(cur - 1)}">← {cur - 1} · {E(STOPS[cur - 2][2])}</a>' if cur > 1 else f'<a class="go alt" href="{BASE}">← Roadmap</a>'
    right = f'<a class="go" href="{url(cur + 1)}">{cur + 1} · {E(STOPS[cur][2])} →</a>' if cur < len(STOPS) else ""
    return f'<div class="pn">{left}<a class="go alt" href="{BASE}">Roadmap</a>{right}</div>'


def say(title, body):
    return f'<div class="say"><b>{title}</b>{body}</div>'


def sub_page(cur, lede, body, desc, extra_css="", title=None, path=None, crumb=""):
    title = title or STOPS[cur - 1][2]
    path = STOPS[cur - 1][1] if path is None else path
    html = f"""<div class="hi">
<p class="crumbs"><a href="/learn/">Learn</a> › <a href="{BASE}">Agent Harness, the big picture</a> › Stop {cur}{crumb}</p>
{stepper(cur)}
<p class="zoom">Stop {cur} of {len(STOPS)} · {E(STOPS[cur - 1][4])}</p>
<h1>{E(title)}</h1>
<p class="lede">{lede}</p>
{body}
{prevnext(cur)}
</div>"""
    return wb.page(f"{title} · Agent Harness, the big picture", desc, SITE + BASE + path, html, CSS + extra_css)


def code_ln(src, cap=""):
    """Code with a line number in front of every line."""
    lines = "".join(f'<span class="l" data-n="{i}">{E(ln)}</span>' for i, ln in enumerate(src.rstrip("\n").split("\n"), 1))
    return f'<pre class="code ln">{lines}</pre>' + (f'<p class="cap">{E(cap)}</p>' if cap else "")


def loop_lines():
    """The loop in agent.py with its real line numbers, each tagged with the numbered comment it belongs to."""
    out, tag, inside = [], "", False
    for no, ln in enumerate((CODE_DIR / "agent.py").read_text().split("\n"), 1):
        if ln.startswith("def run("):
            inside = True
        if not inside:
            continue
        for k in "12345":
            if f"# {k}." in ln:
                tag = k
        this = tag
        if tag == "2" and "return" in ln:
            this = "2g"
        if tag in ("1", "2", "4") and f"# {tag}." not in ln and this != "2g":
            this = ""
        out.append([no, this if no > 0 and not ln.startswith("def run(") and "messages = [" not in ln and not ln.strip().startswith("for step") else "", ln])
        if "# 5." in ln:
            break
    return out


def line_of(marker):
    return next(no for no, ln in enumerate((CODE_DIR / "agent.py").read_text().split("\n"), 1) if marker in ln)


def tbl(head, rows, cls="t"):
    """A table whose cells may contain HTML."""
    h = "".join(f"<th>{c}</th>" for c in head)
    r = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f'<div class="tw"><table class="{cls}"><tr>{h}</tr>{r}</table></div>'


# ----------------------------------------------------------------------------- the roadmap page

def index_page():
    rows = []
    for n, path, title, q, kind in STOPS:
        where = "" if path else ' <span class="note">(in the Agent Harness tutorial)</span>'
        rows.append([str(n), f'<a href="{url(n)}"><b>{E(title)}</b></a>{where}', E(q), f'<span class="k {kind.split()[0]}">{E(kind)}</span>'])
    toc = "".join(f'<li><a href="#s{n}">{E(title)}</a></li>' for n, _p, title, *_ in STOPS)
    body = f"""<div class="hi">
<p class="crumbs"><a href="/learn/">Learn</a> › Agent Harness, the big picture</p>
<h1>Agent Harness, the big picture</h1>
<p class="lede">Before any design or any cloud: what kinds of AI application exist, what an agent really does on each turn of its loop,
what goes wrong when nothing holds it, and what an agent harness is. Nine stops, one simple picture each, two simulations you can play.</p>
<p class="note">No vendor names on this road. Everything here is the idea; the products come later.</p>

<h2 id="roadmap">The roadmap</h2>
{d_roadmap()}
{tbl(["", "Stop", "The question it answers", "Kind"], rows, "t road")}

<div class="toc"><b>On this page</b>, one picture per stop:<ol>{toc}</ol></div>

<h2 id="s1">1 · Three kinds of AI application</h2>
{d_kinds()}
<p>Every AI application is one of three kinds, and the difference is a single question: <b>who decides the next step?</b>
Nobody (there is only one step), your code, or the model. The more the model decides, the more can go wrong, so choose the simplest kind that does the job.</p>
<p><a class="go" href="{url(1)}">Open stop 1 →</a></p>

<h2 id="s2">2 · Autonomous agents</h2>
{d_dial()}
<p>An autonomous agent is an agent with less of a person watching it. Businesses want that because work stops waiting for office hours,
queues stop growing in a spike, and people spend their time on the cases that need judgement.</p>
<p><a class="go" href="{url(2)}">Open stop 2 →</a></p>

<h2 id="s3">3 · Same job, two ways</h2>
<div class="split"><div class="card"><h4>Ordinary code</h4><p>Four steps, written by us, in the same order every time. The input is a form.</p></div>
<div class="card"><h4>An agent</h4><p>One small loop. The model picks each step from what it has seen so far. The input is a sentence.</p></div></div>
<p>Both register the same insurance claim. Both are about twenty lines of Python, and both run on the page's own checks.</p>
<p><a class="go" href="{url(3)}">Open stop 3 →</a></p>

<h2 id="s4">4 · Simulation: the agent loop</h2>
{d_loop()}
<p>Step through one request a move at a time: the exact request our code sends, the exact reply the model returns, the tool our code runs,
and the result going back in. Then watch it stop for one of two reasons: the goal is reached, or the limit is.</p>
<p><a class="go" href="{url(4)}">Play the simulation →</a></p>

<h2 id="s5">5 · Simulation: no guardrails</h2>
{wb.drawing_planted_note()}
<p>Six short stories with the guardrails switched off, among them a document with hidden orders, a stranger who simply asks for someone else's data,
a refund nobody approved and a loop that runs all night. Each ends with what it cost the business. Then switch the guardrails on and play it again. Six real incidents follow.</p>
<p><a class="go" href="{url(5)}">Play the simulation →</a></p>

<h2 id="s6">6 · The horse and the harness</h2>
{wb.drawing_horse_road()}
<p>The model is a strong horse that does not know the road. The harness is everything that keeps it on the green path:
reins, blinkers, a driver and a cart. This is the picture the rest of the course hangs on.</p>
<p><a class="go" href="{url(6)}">Open the horse page →</a></p>

<h2 id="s7">7 · What a harness must do</h2>
{d_reqs()}
<p>Before the big picture, every requirement by itself: a front door, knowing who is asking, running the loop, calling the model, tools, four kinds of guardrails,
logs and traces, cost, evals, safe release, secrets and more. Thirty-three requirements, one small picture each, the way an architect would walk an engineer through them.</p>
<p><a class="go" href="{url(7)}">Open stop 7 →</a></p>

<h2 id="s8">8 · The architecture, simple then zoomed in</h2>
{d_arch_simple()}
<p>Five bands and two rails. Then one band, the shared parts, opened up into five families of concerns: Think, Act, Control, See and Change.
By now every box in it is a requirement you have already met.</p>
<p><a class="go" href="{url(8)}">Open stop 8 →</a></p>

<h2 id="s9">9 · Worked example: one claim, end to end</h2>
{d_fnol()}
<p>Everything above, in one working agent: a claims assistant that takes the first report of a car accident.
Follow one message from start to finish, then send your own in the simulator.</p>
<p><a class="go" href="{url(9)}">Follow one message →</a><a class="go alt" href="/learn/agent-harness-sim/">Open the simulator →</a></p>
</div>"""
    desc = ("A simple road into AI agents and the agent harness: three kinds of AI application, autonomous agents and why businesses want them, "
            "code side by side, a step-by-step agent loop simulation, a no-guardrails prompt injection simulation, and the architecture in five families.")
    return wb.page("Agent Harness, the big picture", desc, SITE + BASE, body, CSS)


# ----------------------------------------------------------------------------- stop 1: three kinds

def kinds_page():
    body = f"""{d_kinds()}
<h2>One question sorts them</h2>
<p>Ask of any AI application: <b>who decides the next step?</b> There are only three answers.</p>
{tbl(["Kind", "Who decides the next step", "An insurance example", "Good at", "Watch out for", "Harness needed"], [
    ["<b>Single call</b>", "Nobody. There is only one step.", "Turn a 12-page surveyor's report into five lines", "Cheap, fast and easy to test", "It only knows what you put in the request", "A little: check what goes in and what comes out"],
    ["<b>Workflow</b>", "Your code. The steps and their order are written in advance.", "Read a claim form, pull out the fields, check the policy, send an acknowledgement", "Predictable: every run takes the same path, so it is easy to audit", "It fails on a case that does not fit the steps you wrote", "Some: a check at each step"],
    ["<b>Agent</b>", "The model. It picks a tool, sees the result and picks again.", "A customer describes an accident in their own words; the assistant works out what to look up and what to do", "Handles cases nobody wrote a path for", "It can take a wrong step, a costly step, or too many steps", "A lot: limits, permissions, approvals and a record of every step"],
])}
{say("The same model can sit in all three.", "The kind is not about how clever the model is. It is about how much of the route you hand over to it.")}

<h2>How to choose</h2>
<ol>
<li><b>Can one request do the whole job?</b> Then it is a single call. Stop here.</li>
<li><b>Do you know the steps before you start?</b> Then write them down as a workflow, and use the model inside the steps that need it.</li>
<li><b>Do the steps depend on what turns up along the way?</b> Only then is it an agent.</li>
</ol>
<p>Choose the simplest kind that does the job. Each step up buys flexibility and costs you predictability, money and testing effort.</p>

<h2>The same three kinds in other industries</h2>
{tbl(["Industry", "Single call", "Workflow", "Agent"], [
    ["<b>Banking</b>", "Sort an incoming complaint email into the right team", "Check identity documents in a fixed order of steps", "Look into an unusual payment across several systems"],
    ["<b>Hotels</b>", "Translate a guest review", "Booking confirmed, then a welcome message, then an upgrade offer", "A concierge that books, changes and fixes a guest's plans"],
    ["<b>Retail</b>", "Write a product description from a specification sheet", "Return request, then the policy check, then the shipping label", "A shopping assistant that searches, compares and places the order"],
])}
<p>Next: the agent column is where the value is, and where the trouble is. Stop 2 looks at agents that work with less and less of a person watching.</p>"""
    return sub_page(1, "There are only three kinds, and one question tells them apart: who decides the next step?", body,
                    "The three kinds of AI application explained simply: single call, workflow and agent. One question tells them apart: who decides the next step? With examples from insurance, banking, hotels and retail.")


# ----------------------------------------------------------------------------- stop 2: autonomous agents

def autonomous_page():
    body = f"""<h2>What it is</h2>
<p><b>An autonomous agent is an agent that nobody is watching step by step.</b> It starts on an event or a schedule, works for minutes or hours,
and acts by itself inside limits that someone set in advance.</p>
<p>Autonomy is not a fourth kind of application. It is a second dial. The <b>kind</b> (stop 1) says who decides the next step.
<b>Autonomy</b> says how much a person checks.</p>
{d_dial()}
{tbl(["Level", "What the AI does", "What the person does", "Example"], [
    ["<b>0 · Answer</b>", "Answers one question", "Reads it and decides", "Summarise this email"],
    ["<b>1 · Suggest</b>", "Proposes an action", "Takes the action", "Drafts a reply for a claims handler to send"],
    ["<b>2 · Act with approval</b>", "Acts, but asks before anything important", "Approves or rejects", "Asks before making a refund"],
    ["<b>3 · Act within limits</b>", "Acts by itself inside a budget and a set of rules", "Reviews afterwards", "Settles small claims and logs every step"],
    ["<b>4 · Run unattended</b>", "Starts itself, runs for hours, recovers from problems", "Sets the goals and limits, reads the report", "Handles incidents overnight"],
])}

<h2>Why businesses want them</h2>
<p>Each benefit below comes with the number you would measure to prove it. A benefit you cannot measure is a claim, not a benefit.</p>
{tbl(["Benefit", "In an insurance claims team", "How you would prove it"], [
    ["<b>Work does not wait for office hours</b>", "A claim reported at 11 pm is checked and acknowledged at 11 pm", "Time to first response"],
    ["<b>Faster from start to finish</b>", "Small, simple claims settled in minutes, not days", "Time from report to settlement"],
    ["<b>Spikes without hiring</b>", "A storm triples the claims for a week; the queue does not triple", "Size of the backlog"],
    ["<b>People do the judgement work</b>", "Handlers take the disputed and the large claims; the agent takes the routine ones", "Share of staff time spent on exceptions"],
    ["<b>The same rules every time</b>", "Every claim is checked against the same policy wording, and every step is written down", "Rule breaks found in audit"],
    ["<b>Lower cost for each piece of work</b>", "The cost of a settled claim drops, most of all when simple rules run before the model is called", "Cost for each settled claim"],
])}

<div class="split">
<div class="card good"><h4>Worth it when the work is…</h4><ul><li>high in volume and repetitive</li><li>governed by clear rules</li><li>easy to undo, or cheap to get wrong</li><li>measurable: you can tell a good result from a bad one</li></ul></div>
<div class="card bad"><h4>Not worth it yet when the work is…</h4><ul><li>rare, or different every time</li><li>impossible to undo and high in stakes</li><li>impossible to judge afterwards</li><li>cheaper with a simple rule or a workflow</li></ul></div>
</div>

<h2>The catch</h2>
<p>With nobody watching, there is no person to catch a mistake. Each problem below has an answer, and the answers together are what this course calls the harness.</p>
{tbl(["Problem", "What it looks like", "Where we meet it"], [
    ["<b>It does not know when to stop</b>", "It loops all night, or says the job is done halfway", f'<a href="{url(4)}">Stop 4</a>: the limit in the loop'],
    ["<b>It can be tricked</b>", "A sentence hidden in a document becomes an order", f'<a href="{url(5)}">Stop 5</a>: the no-guardrails simulation'],
    ["<b>It can reach too much</b>", "It reads or changes things the person asking has no right to", f'<a href="{url(5)}">Stop 5</a>, second story'],
    ["<b>Small mistakes add up</b>", "A wrong reading at step 3 becomes a wrong payment at step 9", f'<a href="{url(6)}">Stop 6</a>: reins that pull it back early'],
    ["<b>Nobody can see what it did</b>", "A customer complains and there is no record of why", f'<a href="{url(8)}">Stop 8</a>: the See family'],
])}
<p>Next: enough talk. Stop 3 puts ordinary code and an agent side by side, doing the same job.</p>"""
    return sub_page(2, "What autonomous agents are, the five levels of autonomy, why businesses want them, and the catch.", body,
                    "Autonomous AI agents explained simply: what they are, five levels of autonomy, the business benefits with the number that proves each one, when they are worth it, and the problems that make an agent harness necessary.")


# ----------------------------------------------------------------------------- stop 3: code

def run_code(name):
    out = subprocess.run([sys.executable, name], cwd=CODE_DIR, capture_output=True, text=True, check=True)
    return out.stdout.strip()


def code_page():
    src = {n: (CODE_DIR / n).read_text() for n in ("deterministic.py", "agent.py", "world.py", "pretend_model.py", "test_both.py")}
    checks = run_code("test_both.py")
    body = f"""<p>The job: <b>register a motor insurance claim.</b> First with ordinary code, then with an agent. Both versions are complete and both run.</p>

<h2>Version 1: ordinary code</h2>
<p>We decide every step and the order. The caller must hand us three tidy values, the way a web form would.</p>
{code_ln(src["deterministic.py"])}
{C.code("$ python3 deterministic.py\n" + run_code("deterministic.py"), "What it prints.")}

<h2>Version 2: an agent</h2>
<p>We write one small loop and a list of tools. The model decides which tool to use next, turn by turn. The caller hands us a sentence.</p>
{code_ln(src["agent.py"])}
{C.code("$ python3 agent.py\n" + run_code("agent.py"), "What it prints. The second request is a question, which version 1 has no code for.")}
{say(f"Read the five numbered comments, on lines {line_of('# 1.')} to {line_of('# 5.')}.", "Ask the model. If it asks for no tool, that is the answer. Otherwise run the tool, show it the result, and go round again. After five turns, stop. That is the whole agent, and stop 4 turns those five lines into a simulation.")}

<h2>What is different</h2>
{tbl(["Question", "Ordinary code", "Agent"], [
    ["<b>Who decides the next step?</b>", "We do, when we write the code", "The model does, each time round the loop"],
    ["<b>What does the input look like?</b>", "Three typed values, like a form", "A sentence in the person's own words"],
    ["<b>A request nobody planned for?</b>", "Needs a new function (\"what does my policy cover?\" is not handled)", "The same loop handles it, with no new code"],
    ["<b>Can you predict the path?</b>", "Yes: the same four steps every time", "No: anything from one turn to five"],
    ["<b>How do you test it?</b>", "A table of inputs and expected outputs", "The same table, plus checks on which tools it used, plus watching real runs"],
    ["<b>What does a run cost?</b>", "Almost nothing", "One model call for each turn, and each turn sends more text than the last"],
    ["<b>What can go wrong?</b>", "A bug you can read in the code", "A wrong step, a costly step or an endless loop, and the code looks fine"],
    ["<b>Use it when</b>", "You know the steps in advance", "The steps depend on what turns up along the way"],
])}

<h2>Look at what the agent does not have</h2>
<p>Line {line_of("output = TOOLS[")} runs <b>whatever tool the model names, with whatever input the model gives, for whoever is asking</b>. Nothing checks any of it.
The only protection in the whole file is line {line_of("# 5.")}, the limit of five turns. Stop 5 shows what that costs.</p>

<h2>The rest of the files</h2>
<details class="faq"><summary>world.py: the pretend insurance company</summary>{code_ln(src["world.py"])}</details>
<details class="faq"><summary>pretend_model.py: the stand-in for a real model</summary>
<p>So that the example runs with no account and no cost, the model here is a few plain rules that return replies in the same shape a real model does.
It shows the loop, not intelligence. Replace it with a call to a real model and agent.py does not change.</p>{code_ln(src["pretend_model.py"])}</details>
<details class="faq"><summary>test_both.py: a table of checks for both versions</summary>{code_ln(src["test_both.py"])}{C.code("$ python3 test_both.py\n" + checks)}</details>
<p><a class="go alt" href="{CODE_URL}">The five files on GitHub</a></p>
<p>Next: stop 4 runs the loop slowly, so you can see every message that crosses between our code and the model.</p>"""
    return sub_page(3, "One job, written twice: once as ordinary code where we decide every step, and once as an agent where the model does.", body,
                    "Deterministic code and an AI agent side by side in about twenty lines of Python each: the same insurance claim registered with fixed steps and with an agent loop, plus a table of what differs.")


# ----------------------------------------------------------------------------- stop 4: the loop simulation

def loop_sim_page():
    js = (S.LOOP_JS.replace("__SCENARIOS__", json.dumps(S.LOOP_SCENARIOS)).replace("__TOOLS__", json.dumps(S.LOOP_TOOLS))
          .replace("__SYSTEM__", json.dumps(S.LOOP_SYSTEM)).replace("__CODE__", json.dumps(loop_lines())))
    body = f"""<p class="note">Nothing here calls a real model. The replies are scripted so that every run is the same. The shapes of the request and the response are the real ones.</p>
{say("How to read this page.", "One <b>turn</b> is one request from our code to the model and one response back. The page lays the turns out one under the other, so you can count them and read what crossed in each. Blue rows go to the model. Lavender rows come back from it. Yellow rows are our own code running a tool.")}
<div class="chat">
<p class="top"><span>What the person sees</span><span>Replies are scripted, so pick one of these messages</span></p>
<div class="sugg" id="sugg"></div>
<div class="bubbles" id="chat"></div>
<div class="composer"><input id="msg" readonly aria-label="Message to the assistant"><button class="act" id="send">Send</button></div>
</div>
<p class="behind">What happens behind it</p>
<figure class="drawing loopfig">{kit.DEFS}<svg viewBox="0 0 1000 350" role="img" aria-label="{E(LOOP_LABEL)}">{loop_body(ids=True)}</svg></figure>
<div class="simbar">
<div><label for="max">Limit on turns</label><input id="max" type="number" min="1" max="8" value="5"></div>
<button class="act" id="next">Next step</button><button class="act" id="turn">Next turn</button><button class="act alt" id="play">Play</button><button class="act alt" id="again">Start again</button>
<label class="chk"><input type="checkbox" id="json" checked> Show the exact JSON</label>
</div>
<div class="score"><div class="big" id="big"></div><div class="chips" id="chips"></div></div>
<div id="ladder"></div>
<h3>The line of code that is running</h3>
<pre class="loopcode" id="code"></pre>
<p class="note">This is the loop from agent.py in <a href="{url(3)}">stop 3</a>, with the same line numbers.</p>

<h2>Things to try</h2>
<ol>
<li><b>Send the first message, then press "Next turn" three times.</b> Count them: three requests and three responses for one sentence from the person. Nobody told the model the order of the steps.</li>
<li><b>Compare request 1 with request 3.</b> Request 3 carries five messages, because the model remembers nothing between turns and our code sends the whole conversation again. More turns means more text sent each time, which is what you pay for.</li>
<li><b>Send "What does my policy P-1001 cover?".</b> Same loop, same tools, two turns. No new code was written for it.</li>
<li><b>Send "Where is my claim C-777?".</b> The claims system is busy. The model would retry for ever. The only thing that stops it is our limit.</li>
<li><b>Set the limit to 2 and send the first message again.</b> The loop stops before the claim is created. A limit protects you, and a limit that is too tight breaks real work. Choosing it is a design decision.</li>
<li><b>Untick "Show the exact JSON"</b> when you want to explain the idea first and the detail later.</li>
</ol>

<h2>What the simulation shows</h2>
{tbl(["What you saw", "Why it matters"], [
    ["<b>The model never runs a tool.</b> It only asks.", "Our code runs every tool. So our code is the place to put every check."],
    ["<b>A reply with no tool request is the answer.</b>", "That is how the loop knows the goal is reached. There is no separate \"done\" signal."],
    ["<b>The model has no memory.</b> We send everything, every turn.", "What the model knows is exactly what we choose to send. That is a control, and a cost."],
    ["<b>The loop stops for one of two reasons.</b>", "The model says it is done, or our code says \"enough\". Only the second one is under our control."],
])}
<script>{js}</script>
<p>Next: the loop above trusts the model completely. Stop 5 shows what happens when someone takes advantage of that.</p>"""
    return sub_page(4, "One request, one move at a time: what our code sends to the model, what comes back, the tool we run, and round again until the goal or the limit.", body,
                    "A step-by-step simulation of the AI agent loop: see the request sent to the model, the tool request that comes back, the tool result going in, and the loop repeating until the goal or the step limit is reached.",
                    S.LOOP_CSS)


# ----------------------------------------------------------------------------- stop 5: no guardrails

def guard_sim_page():
    js = S.GUARD_JS.replace("__SCENARIOS__", json.dumps(S.GUARD_SCENARIOS))
    rows = [[f"<b>{E(who)}</b><br>{when}", E(what), E(kind), E(missing), f'<a href="{src}">source</a>'] for who, when, what, kind, missing, src in S.INCIDENTS]
    body = f"""<p class="note">The six stories are illustrations with made-up people and amounts. They are built to show the mechanism. The six incidents further down are real.</p>
{say("How to read this page.", "Each story is laid out turn by turn, exactly like the loop simulation in stop 4: the request our code sends, the response the model returns, and the tool our code runs. Watch what is inside each request. Rose means harm. Green means a harness check.")}
<div class="tabs2" id="tabs"></div>
<p class="kind" id="kind"></p><p class="intro" id="intro"></p><p class="real" id="real"></p>
<div class="simbar"><div><label>Guardrails</label><span class="switch"><button id="goff" class="off">Off</button><button id="gon" class="onn">On</button></span></div></div>
<div class="chat">
<p class="top"><span>What the person sees</span><span id="who"></span></p>
<div class="bubbles" id="chat"></div>
<div class="composer"><input id="msg" readonly aria-label="Message to the assistant"><button class="act" id="send">Send</button></div>
</div>
<p class="behind">What happens behind it</p>
<div class="simbar">
<button class="act" id="next">Next step</button><button class="act" id="turn">Next turn</button><button class="act alt" id="play">Play</button><button class="act alt" id="again">Start again</button>
</div>
<div class="score"><div class="big" id="big"></div><div class="chips" id="chips"></div></div>
<div id="ladder"></div>
<script>{js}</script>

<h2>What is prompt injection?</h2>
<p>A model reads its instructions and its data as one stream of text. <b>Prompt injection</b> is text that arrives as data and gets treated as an instruction.
It can be typed by the user (the second and third stories), or it can hide inside something the agent reads: a document, an email, a web page, a note in a record (the first story).
The hidden kind is worse, because the person using the agent did nothing wrong. The last three stories have no attacker at all: an agent with no guardrails can do damage by itself.</p>
{say("The model is not the fix.", "A better model is fooled less often, and never zero times. In every story with the guardrails on, the model still makes the same mistake. What changes is that being fooled no longer matters, because ordinary code checks every action before it happens.")}

<h2>It has already happened</h2>
<p>Six public cases. Most involve assistants far simpler than the agent above.</p>
{tbl(["Who and when", "What happened", "Kind of failure", "The guardrail that was missing", ""], rows)}
<p class="note">Each row was checked against its source on 16 November 2026. Two of the six were shown by security researchers before anyone was known to have used them.</p>

<h2>What a business actually loses</h2>
{tbl(["Loss", "How it happens", "Seen above in"], [
    ["<b>Money</b>", "A payment, a refund or a discount that nobody approved; or a bill for work that produced nothing", "Stories 1, 3 and 6"],
    ["<b>Data</b>", "Personal or confidential data shown to the wrong person", "Story 2, Slack AI, EchoLeak"],
    ["<b>Legal standing</b>", "The company answers for what its assistant says and does", "Air Canada, stories 2 and 5"],
    ["<b>Systems</b>", "Records changed or deleted with no way back", "Replit, story 4"],
    ["<b>Trust</b>", "Screenshots travel faster than apologies", "Chevrolet, DPD"],
])}
{say("This is why an agent harness exists.", "None of the fixes above made the model cleverer. Each one was a piece of ordinary software placed around the model: a fence, a check before a tool runs, a login that limits what a tool can reach, a limit on turns. Put those pieces together and give them a name, and you have the harness.")}
<p>Next: stop 6 draws that idea as one picture, a horse on a road.</p>"""
    return sub_page(5, "Six short stories with the guardrails switched off, each laid out turn by turn and ending with what it cost the business. Then switch them on and play it again.", body,
                    "A simulation of an AI agent with no guardrails: prompt injection hidden in a document, a user asking for someone else's data, and a loop with no limit, each with its business impact. Plus six real incidents and the guardrail each one was missing.",
                    S.GUARD_CSS)


# ----------------------------------------------------------------------------- stop 7: architecture

def architecture_page():
    fam_rows = []
    for name, q, members, _k in FAMILIES:
        fam_rows.append([f"<b>{name}</b>", " ".join(q), ", ".join(members), FAMILY_WHY[name]])
    body = f"""<h2>First, the simple picture</h2>
{d_arch_simple()}
<p>Read it from the top as one request travelling down.</p>
<ol>
<li><b>People ask.</b> Customers, partners and staff, on whatever channel they already use.</li>
<li><b>The front door</b> checks every request before any agent sees it: who is asking, is anything hidden in the message, is it in scope.</li>
<li><b>Agents.</b> One for each business job. Each has its own autonomy level from <a href="{url(2)}">stop 2</a>.</li>
<li><b>Shared parts.</b> Everything an agent needs that is not specific to its job. Built once, used by every agent.</li>
<li><b>Business systems.</b> The real records. Agents reach them only through tools, and only with the authority of the person asking.</li>
</ol>
<p>Two rails run alongside. <b>Lifecycle</b> is the path every agent takes from idea to production and back round through what it learned.
<b>Governance</b> is who owns the agent, how risky it is, and what the law requires.</p>
{say("Why it is drawn this way.", "Only the row of agents changes from one business to the next. Everything else is shared, so the second agent costs far less than the first. That is the whole argument for building a harness and not ten separate agents.")}

<h2>Now zoom in on the shared parts</h2>
{d_families()}
<p>Twelve parts is too many to hold in your head, so they are grouped into five families. Each family answers one question that a business will ask about any agent.</p>
{tbl(["Family", "The question it answers", "Parts", "Without it"], fam_rows)}

<h2>Where each requirement lives</h2>
<p>Stop 7 listed what a harness must do. Here is where each of those requirements sits in the picture.</p>
{tbl(["Part of the picture", "The requirements it answers"], [[f"<b>{part}</b>", ", ".join(req_link(n) for n in nums)] for part, nums in LIVES_IN])}

<h2>Where the earlier stops land</h2>
{tbl(["What you saw", "The family that owns it"], [
    [f'The request and response in the loop (<a href="{url(4)}">stop 4</a>)', "<b>Think</b>: the model gateway sends it; memory and state hold the messages"],
    [f'The tool our code ran (<a href="{url(4)}">stop 4</a>)', "<b>Act</b>: the tool hub"],
    [f'The check before the payout, and the handover to a person (<a href="{url(5)}">stop 5</a>)', "<b>Control</b>: guardrails and the human desk"],
    [f'The tool running with the user\'s authority (<a href="{url(5)}">stop 5</a>)', "<b>Control</b>: identity and access"],
    [f'The limit on turns and on spend (<a href="{url(4)}">stops 4</a> and <a href="{url(5)}">5</a>)', "<b>See</b>: cost control"],
    ["The record of the refused payout", "<b>See</b>: observability"],
    ["Knowing the fix still works after the next change", "<b>Change</b>: the eval library and release"],
])}

<h2>Go deeper when you are ready</h2>
<p>The same architecture exists at more zoom levels in the Agent Harness tutorial. Nothing new is added there; each picture opens one more level.</p>
<p><a class="go alt" href="{TUTORIAL}arch-abstract.html">The full abstract picture: seven bands, two rails</a><a class="go alt" href="{TUTORIAL}arch-assets.html">The five families, part by part</a><a class="go alt" href="{TUTORIAL}arch-northstar.html">A north star, not a checklist</a></p>
<p>Next: stop 9 follows one real message through all of it.</p>"""
    return sub_page(8, "The whole system in five bands and two rails. Then one band opened up into five families of concerns.", body,
                    "A simple agent harness architecture with no vendor names: people, the front door, agents, shared parts and business systems, then the shared parts zoomed into five families of concerns: Think, Act, Control, See and Change.")


# ----------------------------------------------------------------------------- stop 7: requirements

REQS = []  # (number, group slug, group title, the requirement tuple)
for _slug, _title, _blurb, _reqs in R.GROUPS:
    for _r in _reqs:
        REQS.append((len(REQS) + 1, _slug, _title, _r))

LIVES_IN = [("The front door", [1, 2, 4, 5]), ("Orchestration: the router and the loop", [6]), ("Think", [7, 8, 9, 15, 18, 19]), ("Act", [10, 16]),
            ("Control", [3, 11, 12, 13, 14, 17, 30, 32]), ("See", [20, 21, 22, 23]), ("Change", [25, 26, 27, 28, 29]), ("The governance rail", [24, 31, 33])]


def req_link(n):
    _n, slug, _g, r = REQS[n - 1]
    return f'<a href="{REQ_BASE}{slug}/#r{n}">{n} · {E(r[0])}</a>'


def group_nav(cur_slug=None):
    out = [f'<a href="{REQ_BASE}">All requirements</a>' if cur_slug else '<span class="on">All requirements</span>']
    for slug, title, _b, _r in R.GROUPS:
        short = title.split(":")[0]
        out.append(f'<span class="on">{E(short)}</span>' if slug == cur_slug else f'<a href="{REQ_BASE}{slug}/">{E(short)}</a>')
    return f'<nav class="groups" aria-label="Groups of requirements">{"".join(out)}</nav>'


def req_section(n, r):
    name, aka, q, items, caption, why, think, without, where = r
    label = f"{name}. " + ", then ".join(it[1] + (" " + " ".join(it[2]) if it[2] else "") for it in items) + "."
    return f"""<section class="req" id="r{n}">
<span class="no">Requirement {n} of {len(REQS)}</span>
<h2>{E(name)}</h2>
<p class="aka">Also called: {E(aka)}</p>
<p class="q">{E(q)}</p>
{R.picture(kit, wb.figure, items, label, E(caption))}
<div class="cols">
<div><h4>Why</h4><p>{E(why)}</p></div>
<div class="without"><h4>Without it</h4><p>{E(without)}</p></div>
</div>
<div class="cols" style="margin-top:14px"><div style="grid-column:1 / -1"><h4>Think about</h4><ul>{"".join(f"<li>{E(x)}</li>" for x in think)}</ul></div></div>
<p class="where">In the big picture: <b>{E(where)}</b></p>
</section>"""


def reqs_hub_page():
    rows = [[str(n), f'<a href="{REQ_BASE}{slug}/#r{n}"><b>{E(r[0])}</b></a>', E(r[1]), E(r[2]), E(g.split(":")[0])] for n, slug, g, r in REQS]
    body = f"""{group_nav()}
{say("How to read every picture.", "Left: what comes in. Lavender, in the middle: the requirement. Right: what comes out. A pink cross on an arrow means \"stopped here\".")}
{d_reqs()}
<p>The top row follows a request: it is <b>received</b>, the agent <b>thinks</b>, and the agent <b>acts</b>. These are the functional requirements, the things an agent does.
The bottom row applies to every request at once: <b>keep going</b>, <b>see</b>, <b>prove and change</b>, and <b>protect</b>. These are the non-functional requirements, how well and how safely it does them.</p>
<p>{"".join(f'<a class="go alt" href="{REQ_BASE}{slug}/">{E(title.split(":")[0])} →</a>' for slug, title, _b, _r in R.GROUPS)}</p>

<h2>All {len(REQS)} requirements</h2>
{tbl(["", "Requirement", "Also called", "The question an engineer asks", "Group"], rows, "t road")}

<h2>Guardrails come in four kinds</h2>
<p>"We need guardrails" is four different requirements, because there are four different places to stand.</p>
{tbl(["Where it stands", "Name", "What it catches", "Group"], [[f"<b>{E(a)}</b>", E(b), E(c), E(d)] for a, b, c, d in R.GUARDRAIL_KINDS])}

<h2>The usual names for the non-functional requirements</h2>
<p>If your team uses the standard words, this is where each one is covered.</p>
{tbl(["The usual word", "Covered by"], [
    ["<b>Security</b>", ", ".join(req_link(n) for n in (2, 3, 4, 11, 12, 30, 32))],
    ["<b>Privacy and compliance</b>", ", ".join(req_link(n) for n in (24, 31, 33))],
    ["<b>Reliability</b>", ", ".join(req_link(n) for n in (7, 15, 16, 17))],
    ["<b>Performance and scale</b>", ", ".join(req_link(n) for n in (5, 18, 19))],
    ["<b>Observability</b>", ", ".join(req_link(n) for n in (20, 21, 22))],
    ["<b>Cost</b>", ", ".join(req_link(n) for n in (5, 23))],
    ["<b>Quality</b>", ", ".join(req_link(n) for n in (14, 25, 26))],
    ["<b>Ease of change</b>", ", ".join(req_link(n) for n in (27, 28, 29))],
])}
{say("Not every agent needs all of them.", "A small internal helper needs a slice. An agent that moves money needs nearly everything. The risk level of the job decides, and that is the last requirement on the list.")}
<p>Next: stop 8 puts all of these into one picture. Every box in it will be a requirement you have already met.</p>"""
    return sub_page(7, f"Before the big picture: everything a harness has to do, one need at a time. {len(REQS)} requirements in seven groups, one small picture each.", body,
                    f"The requirements of an AI agent harness, functional and non-functional, one simple picture each: {len(REQS)} requirements from the front door and sign-in to the loop, the model call, tools, four kinds of guardrails, logs, traces, cost, evals, release and data protection.")


def reqs_group_page(gi):
    slug, title, blurb, _reqs = R.GROUPS[gi]
    mine = [(n, r) for n, s_, _g, r in REQS if s_ == slug]
    jump = "".join(f'<li><a href="#r{n}">{n} · {E(r[0])}</a></li>' for n, r in mine)
    prev = (f'<a class="go alt" href="{REQ_BASE}{R.GROUPS[gi - 1][0]}/">← {E(R.GROUPS[gi - 1][1].split(":")[0])}</a>' if gi else f'<a class="go alt" href="{REQ_BASE}">← All requirements</a>')
    nxt = (f'<a class="go" href="{REQ_BASE}{R.GROUPS[gi + 1][0]}/">{E(R.GROUPS[gi + 1][1].split(":")[0])} →</a>' if gi + 1 < len(R.GROUPS) else f'<a class="go" href="{url(8)}">Stop 8 · The architecture →</a>')
    body = f"""{group_nav(slug)}
<ul class="jump" style="list-style:none">{jump}</ul>
{"".join(req_section(n, r) for n, r in mine)}
<p style="margin-top:34px">{prev}{nxt}</p>"""
    return sub_page(7, E(blurb), body, f"{title}: {len(mine)} requirements of an AI agent harness, one simple picture each. " + "; ".join(r[0] for _n, r in mine) + ".",
                    title=title, path=f"requirements/{slug}/", crumb=f' › <a href="{REQ_BASE}">What a harness must do</a>')


FAMILY_WHY = {
    "Think": "The agent guesses from what the model happens to remember",
    "Act": "The agent can talk but cannot do anything",
    "Control": "The six stories in stop 5",
    "See": "Nobody can say what happened, or what it cost",
    "Change": "Every improvement is a gamble, so nothing gets improved",
}

PAGES = {"": index_page, "kinds/": kinds_page, "autonomous-agents/": autonomous_page, "code/": code_page,
         "loop-sim/": loop_sim_page, "no-guardrails-sim/": guard_sim_page, "requirements/": reqs_hub_page, "architecture/": architecture_page}
for _i, _g in enumerate(R.GROUPS):
    PAGES[f"requirements/{_g[0]}/"] = (lambda i=_i: reqs_group_page(i))


def main():
    for target in list(EXTERNAL.values()) + [TUTORIAL + "arch-abstract.html", TUTORIAL + "arch-assets.html", TUTORIAL + "arch-northstar.html", "/learn/agent-harness-sim/index.html"]:
        assert (ROOT / target.lstrip("/")).exists(), f"linked page is missing: {target}"
    out = ROOT / "learn" / "agent-harness-intro"
    for path, fn in PAGES.items():
        (out / path).mkdir(parents=True, exist_ok=True)
        (out / path / "index.html").write_text(fn())
    print("Agent Harness, the big picture:", len(PAGES), "pages ->", out)


if __name__ == "__main__":
    main()
