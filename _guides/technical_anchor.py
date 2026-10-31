"""The technical anchor: the guide at /learn/technical-anchor/.

    python3 _guides/technical_anchor.py

How a developer thinks as the technical anchor of a data engineering project: the one person who
holds the whole technical picture and connects every role around it. Teach first (what the role
is, why it decides success), then a clickable map of the twelve roles around the anchor, then the
jobs (design, estimation, scope, decisions, stakeholders, risks, test-deploy-run), each with how to
fail fast, then a 30-day start, a weekly rhythm, mistakes and self-check questions.

Shares CSS and drawing helpers with _guides/agenttwin.py. Examples are illustrative (labelled).
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "_paths"))
spec = importlib.util.spec_from_file_location("writing_build", ROOT / "_writing" / "build.py")
wb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wb)
_at = importlib.util.spec_from_file_location("agenttwin_guide", ROOT / "_guides" / "agenttwin.py")
at = importlib.util.module_from_spec(_at)
_at.loader.exec_module(at)
from diagrams import FILL, arrow, box, svg  # noqa: E402

E = wb.E
SITE = wb.SITE
URL = f"{SITE}/learn/technical-anchor/"
INK = at.INK
T, panel, line = at.T, at.panel, at.line

CSS = at.CSS.replace("</style>", """
  .hub { border:var(--line); border-radius:var(--wob); padding:12px; background:#fff; margin:16px 0; }
  .hub svg { width:100%; height:auto; display:block; } .hub text { font-family:var(--hand); }
  .hub .spoke { cursor:pointer; } .hub .spoke:hover rect, .hub .spoke.on rect { stroke-width:3; fill:#FFF1C2; }
  .hub .detail { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:8px; }
  .hub .detail div { border:1.5px solid var(--ink); border-radius:12px; padding:9px 12px; font-size:15px; }
  .hub .detail b { display:block; font-size:11.5px; letter-spacing:.08em; text-transform:uppercase; color:var(--faint); margin-bottom:2px; }
  .hub .d1 { background:var(--peri-wash); } .hub .d2 { background:var(--mint-wash,#E3F4EA); } .hub .d3 { background:var(--butter-wash); } .hub .d4 { background:var(--rose-wash); }
  .hub h4 { font-family:var(--hand); font-weight:400; font-size:24px; margin:8px 0 0; }
  .tpl { font-family:var(--mono); font-size:13px; background:var(--surface-2); padding:12px; border-radius:8px; overflow-x:auto; white-space:pre; line-height:1.5; }
  @media (max-width:720px) { .hub .detail { grid-template-columns:1fr; } }
</style>""")


# ---------------------------------------------------------------- the clickable hub
ROLES = [
    ("users", "Business owner, users", "rose",
     "A number they can trust, on time, that they understand.",
     "The decisions behind the numbers (what counts as revenue, what a customer is), acceptance criteria, and time to review.",
     "Show them real numbers from their own data in week two, a profile and a draft table, and ask: is this right?",
     "They first see the numbers in user testing and say: that is not how we count revenue."),
    ("ba", "Business analyst", "rose",
     "What is possible, and what the data actually says.",
     "Requirements with worked examples, edge cases and definitions.",
     "Turn each requirement into a data check with an example row before anyone builds it.",
     "The requirement says 'all orders'; the source also holds cancelled, test and duplicate orders."),
    ("arch", "Architect", "peri",
     "How the design meets the standards, and every deviation with its reason.",
     "Patterns, guardrails and a timely approval.",
     "Bring a working thin slice and a one-page decision record in week two, not a full design in week six.",
     "The design is rejected at the review gate after the build has started."),
    ("pm", "PM and Agile lead", "butter",
     "Honest estimates as ranges, risks early, dependencies with dates.",
     "Protected time for spikes, a change process, and decisions escalated when they stall.",
     "Re-estimate after the first thin slice and show the gap openly.",
     "Status stays green until two weeks before go-live."),
    ("dev", "Developers", "peri",
     "A clear design, shared standards, quick unblocking and reviews.",
     "Early warning of anything that is harder than it looked.",
     "Pair on the riskiest piece first, and review code in the first week.",
     "Five developers, five different ways of doing an incremental load."),
    ("platform", "Platform team", "mint",
     "Your needs early: compute, storage, environments, access.",
     "Environments, service accounts and network paths to every source.",
     "Request access to every source and environment in week one, and deploy a small pipeline to a production-like environment that week.",
     "The firewall rule to the source system takes six weeks."),
    ("source", "Source system owners", "mint",
     "What you will read, how often, and the load it puts on them.",
     "The schema, how changes are announced, how deletes and history work, and a named contact.",
     "Pull a real extract in week one, and ask: how do you delete a record? What changes without notice?",
     "Deletes at the source never reach the platform; a column is renamed in their release."),
    ("consumers", "Data consumers", "lilac",
     "Stable tables, an agreed contract, and notice before anything changes.",
     "How they will query it: grain, latency, filters, volume.",
     "Agree a data contract on one gold table early, and let them query a sample.",
     "Gold is built at the wrong grain for the dashboard it was meant for."),
    ("test", "Test and QA", "butter",
     "Testable acceptance criteria, test data and expected results.",
     "A test strategy agreed early, and time to run it.",
     "Write reconciliation and data quality checks with the first pipeline, not after the build.",
     "Testing starts at user acceptance and the defects pile up in the last month."),
    ("deploy", "Release and DevOps", "grey",
     "Deployable pieces, configuration per environment, a cut-over plan.",
     "A working pipeline to every environment, and approvals that fit the schedule.",
     "Have deployment working before the second feature, and rehearse the cut-over.",
     "The first deployment to production happens on go-live day."),
    ("ops", "Operations and support", "grey",
     "A runbook, alerts, and what to do at three in the morning.",
     "Their monitoring standards and their on-call model.",
     "Run a failure drill with them in a test environment before go-live.",
     "The job fails on the first night and nobody knows how to rerun it safely."),
    ("sec", "Security, governance", "lilac",
     "What data, where it lives, who can see it, how long it is kept.",
     "Data classification and approvals.",
     "Classify the data and get the personal-data decision in the first two weeks.",
     "Go-live is blocked because masking of personal data was never designed."),
]


def hub():
    cx, cy, rx, ry, w, h = 560, 300, 430, 225, 210, 56
    import math
    body = ""
    pos = []
    for i in range(len(ROLES)):
        ang = -math.pi / 2 + i * 2 * math.pi / len(ROLES)
        pos.append((cx + rx * math.cos(ang), cy + ry * math.sin(ang)))
    for x, y in pos:
        body += f'<line x1="{cx}" y1="{cy}" x2="{x:.0f}" y2="{y:.0f}" stroke="{INK}" stroke-width="1.3" stroke-dasharray="5 5"/>'
    body += f'<ellipse cx="{cx}" cy="{cy}" rx="120" ry="62" fill="{FILL["gold"]}" stroke="{INK}" stroke-width="2.6"/>'
    body += T(cx, cy - 6, "Technical anchor", 22, fill=INK) + T(cx, cy + 18, "holds the whole picture", 14)
    for (k, name, fill, *_), (x, y) in zip(ROLES, pos):
        body += f'<g class="spoke" data-k="{k}" tabindex="0" role="button" aria-label="{E(name)}">{box(x - w / 2, y - h / 2, w, h, name, "", fill)}</g>'
    full = {"sec": "Security, privacy and governance", "consumers": "Data consumers: BI, data science, apps", "pm": "Project manager and Agile lead", "arch": "Architect and design authority"}
    data = {k: {"name": full.get(k, n), "need": a, "give": b, "ff": c, "miss": d} for k, n, _, a, b, c, d in ROLES}
    js = """<script>(function(){var D=%s,r=document.getElementById('hub'),o=r.querySelector('.out');
function show(k){var d=D[k];r.querySelectorAll('.spoke').forEach(function(g){g.classList.toggle('on',g.dataset.k===k)});
o.innerHTML='<h4>'+d.name+'</h4><div class="detail"><div class="d1"><b>They need from you</b>'+d.need+'</div><div class="d2"><b>You need from them</b>'+d.give+'</div><div class="d3"><b>Help them fail fast</b>'+d.ff+'</div><div class="d4"><b>If it is missed</b>'+d.miss+'</div></div>';}
r.querySelectorAll('.spoke').forEach(function(g){g.onclick=function(){show(g.dataset.k)};g.onkeydown=function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();show(g.dataset.k)}}});show('users');})();</script>""" % json.dumps(data)
    return (f'<div class="hub" id="hub">{svg(1120, 600, body, "The technical anchor in the middle, connected to twelve roles: business owner and users, business analyst, architect, project manager, developers, platform team, source system owners, data consumers, test, release, operations, and security.")}'
            f'<p class="note" style="margin:4px 0 0">Click any role (or tab to it and press Enter).</p><div class="out"></div></div>{js}')


# ---------------------------------------------------------------- drawings
def d_gaps():
    b = ""
    teams = [("Business", "rose"), ("Analysis", "rose"), ("Design", "peri"), ("Build", "peri"), ("Platform", "mint"), ("Test", "butter"), ("Run", "grey")]
    for i, (t, f) in enumerate(teams):
        b += box(20 + i * 157, 60, 125, 70, t, "", f)
    gaps = ["a definition\nnobody signed", "an edge case\nnot written", "a decision\nnot recorded", "access asked\ntoo late", "tests written\nafter the build", "no runbook\nfor night one"]
    for i, g in enumerate(gaps):
        x = 20 + i * 157 + 141
        b += f'<path d="M{x},50 L{x - 7},95 L{x + 7},105 L{x},150" fill="none" stroke="{INK}" stroke-width="2"/>'
        for j, l in enumerate(g.split("\n")):
            b += T(x, 182 + j * 18, l, 13, fill=INK)
    b += T(560, 30, "each team does its own part well; the project fails in the gaps between them", 15)
    b += f'<rect x="300" y="235" width="520" height="52" rx="14" fill="{FILL["gold"]}" stroke="{INK}" stroke-width="2.2"/>'
    b += T(560, 267, "the technical anchor's job is to watch the gaps", 18, fill=INK)
    return svg(1120, 300, b, "Seven teams in a row: business, analysis, design, build, platform, test, run. Between each pair is a crack: a definition nobody signed, an edge case not written, a decision not recorded, access asked too late, tests written after the build, no runbook for night one. The technical anchor watches the gaps."), \
        "Projects rarely fail inside a team. They fail between teams, where nobody owns the hand-off."


def d_failfast():
    b = '<line x1="60" y1="250" x2="1080" y2="250" stroke="#1F1F1F" stroke-width="1.6" marker-end="url(#ah)"/>'
    b += T(1060, 272, "time", 14)
    phases = [("Discover", 60), ("Design", 230), ("Build", 400), ("Test", 600), ("Deploy", 770), ("Run", 930)]
    for n, x in phases:
        b += f'<line x1="{x}" y1="244" x2="{x}" y2="256" stroke="{INK}" stroke-width="1.6"/>' + T(x + 70, 272, n, 15, fill=INK)
    b += f'<path d="M70,235 Q850,235 1040,40" fill="none" stroke="{INK}" stroke-width="2.4"/>'
    b += T(860, 50, "cost of a change", 15, "end")
    items = [("Profile real data", "week 1", 70, 95, 180, "mint"), ("Thin slice, end to end", "weeks 1 to 2", 265, 95, 215, "mint"),
             ("Re-estimate", "after the slice", 500, 36, 230, "butter"), ("Sign scope and decisions", "before build", 500, 108, 230, "butter")]
    for t, s, x, y, w, f in items:
        b += box(x, y, w, 62, t, s, f)
    return svg(1120, 290, b, "A timeline from discover through design, build, test, deploy and run, with the cost of a change rising steeply. Early, cheap moves are marked: profile real data in week 1, a thin slice end to end in weeks 1 to 2, re-estimate after the slice, sign scope and decisions before build."), \
        "The anchor pulls every discovery to the left of the curve, where changing course is still cheap."


def d_lenses():
    import math
    cx, cy = 560, 230
    lenses = [("Business", "right question,\nright definitions", "rose"), ("Data", "grain, history,\ndeletes, late rows", "mint"),
              ("Security", "who sees what,\npersonal data", "lilac"), ("Cost", "per run, per month,\nat 10x volume", "butter"),
              ("Performance", "volume today\nand in two years", "peri"), ("Operations", "rerun, monitor,\nrecover", "grey"),
              ("Change", "new source, new\nfield, new consumer", "sky"), ("Testability", "can each rule\nbe checked?", "butter")]
    b = ""
    for i, (t, s, f) in enumerate(lenses):
        a = -math.pi / 2 + i * 2 * math.pi / len(lenses)
        x, y = cx + 390 * math.cos(a), cy + 175 * math.sin(a)
        b += f'<line x1="{cx}" y1="{cy}" x2="{x:.0f}" y2="{y:.0f}" stroke="{INK}" stroke-width="1.2" stroke-dasharray="4 5"/>'
        b += box(x - 95, y - 34, 190, 68, t, s, f)
    b += f'<circle cx="{cx}" cy="{cy}" r="70" fill="#fff" stroke="{INK}" stroke-width="2.4"/>'
    b += T(cx, cy - 4, "Your design", 20, fill=INK) + T(cx, cy + 18, "seen 8 ways", 14)
    return svg(1120, 460, b, "A design in the middle, looked at through eight lenses: business, data, security, cost, performance, operations, change and testability, each with one question."), \
        "A design is good when it survives every lens, not just the one its author cares about most."


def d_estimate():
    b = box(20, 70, 230, 90, "1 Count the things", "sources, tables, rules,\nreports, interfaces", "peri")
    b += arrow(252, 115, 298, 115)
    b += box(300, 70, 230, 90, "2 Build one, measure", "the thin slice gives\nyour real rate", "mint")
    b += arrow(532, 115, 578, 115)
    b += box(580, 70, 230, 90, "3 Range, not a point", "best, likely, worst,\nwith assumptions", "butter")
    b += arrow(812, 115, 858, 115)
    b += box(860, 70, 240, 90, "4 Re-check weekly", "planned vs actual;\nsay the gap early", "rose")
    b += box(300, 190, 510, 56, "Unknowns get a timeboxed spike, not a guess", "", "white")
    b += T(560, 40, "an estimate is a belief too: test it the same way", 15)
    return svg(1120, 260, b, "Four steps to estimate: count the things; build one and measure the real rate; give a range with assumptions; re-check weekly. Unknowns get a timeboxed spike, not a guess."), \
        "Estimates fail fast when the first real piece of work is used to correct them."


# ---------------------------------------------------------------- tables
RESP = [
    ("Design and architecture", "One end-to-end design that works from every angle, written as short decision records"),
    ("Scope", "A written in-scope and out-of-scope list, signed, with a change process"),
    ("Estimation", "Ranges with assumptions, corrected by real progress"),
    ("Requirements into checks", "Every requirement turned into something the data can be tested against"),
    ("Decisions and sign-off", "A decision log: options, choice, reason, owner, who signed, when"),
    ("Risks and dependencies", "Top risks with an owner, a trigger and a mitigation, reviewed weekly"),
    ("Quality", "A test strategy from day one: data checks, reconciliation, performance"),
    ("Release and run", "Deployment working early, cut-over rehearsed, operations ready before go-live"),
    ("The team", "Standards, reviews, unblocking; making the next person able to do this job"),
    ("Communication", "Bad news early, in plain words, with a next step"),
]

SCOPE_TRAPS = [
    ("History and backfill", "Do we load five years of history, or start from today? Who checks the old numbers?"),
    ("Deletes at the source", "When a record is deleted upstream, must it disappear here, be flagged, or stay?"),
    ("Late and corrected data", "If yesterday's sales are corrected next week, which days do we rebuild?"),
    ("Changes over time", "Do we keep history of a customer's address (slowly changing dimensions) or only the latest?"),
    ("Bad rows", "Reject the batch, quarantine the rows, or load and flag them? Who fixes them?"),
    ("Data quality at the source", "Are we expected to fix the source's mistakes, or report them?"),
    ("Personal data", "Masking, retention, the right to be forgotten: designed in, or someone else's job?"),
    ("Reports and dashboards", "Are the reports in scope, or only the tables they read?"),
    ("Access and onboarding", "Who requests access for users, and who approves it?"),
    ("Recovery", "How fast must it recover after a failure, and how much data can be lost?"),
]

DECISIONS = [
    ("Definitions", "What counts as revenue: gross or net, with or without tax, booked or paid?"),
    ("Source of truth", "When the CRM and the billing system disagree on a customer, which one wins?"),
    ("Freshness", "Daily by 7 a.m., hourly, or near real time? Each costs very differently."),
    ("History", "Which tables keep history, and for how long?"),
    ("Bad data", "What happens to a row that fails a rule, and who is told?"),
    ("Tools and patterns", "Batch or streaming; which ingestion pattern; build or reuse a framework."),
]

FIRST30 = [
    ("Days 1 to 3", "Meet every role on the map. Ask each: what does success look like for you, and what has gone wrong before? Request all access and environments now."),
    ("Week 1", "Pull and profile real data from every source. Write the first list of beliefs the plan depends on. Start the risk and decision logs."),
    ("Weeks 1 to 2", "Build a thin slice: one source table, through every layer, to one tile or one query, deployed to a production-like environment."),
    ("Week 2", "Show real numbers to the business. Write the in-scope and out-of-scope list. Take the first decisions to sign-off."),
    ("Weeks 3 to 4", "Re-estimate from the slice. Agree the test strategy and the first data contract. Review the design through every lens with the people on the map, not only architects."),
]

WEEKLY = [
    ("Monday", "Top five risks: any moved? Decisions due this week, and who must sign."),
    ("Midweek", "Walk the board with developers: anything harder than it looked? Unblock or escalate."),
    ("Every two weeks", "Demo with real numbers to the business. Re-estimate. Update scope if anything changed, in writing."),
    ("Friday", "Three lines to stakeholders: what we learned, what changed, what we need from you."),
]

MISTAKES = [
    ("Being the best developer instead of the anchor", "Writing the hardest code yourself while the gaps between teams go unwatched."),
    ("Designing on paper for weeks", "A beautiful design that has never touched real data or a real environment."),
    ("A single-number estimate", "'Six weeks' becomes a promise. 'Five to eight weeks, if these three things hold' is a plan."),
    ("Verbal decisions", "Agreed in a meeting, never written down, reopened a month later by someone who wasn't there."),
    ("Silent scope", "Anything not written as out of scope will be assumed to be in."),
    ("Only managing upward", "Keeping the project manager informed while source owners, operations and security hear nothing until they are blocking."),
    ("Green until it's red", "Hiding a slipping date until it can't be fixed. Bad news early is a gift."),
]

QUESTIONS = [
    "Can you draw the whole system, from every source to every consumer, on one page?",
    "Which three beliefs does the plan depend on most, and has each been tested against real data?",
    "Is there a written list of what is out of scope, and has the business owner signed it?",
    "Which open decisions have a deadline and an owner?",
    "Has anything been deployed to a production-like environment yet?",
    "Do operations know what to do if the pipeline fails tonight?",
    "Which stakeholder have you not spoken to in two weeks?",
    "What is your estimate range today, and how did it change since the thin slice?",
]


# ---------------------------------------------------------------- page
def page():
    gaps_svg, gaps_cap = d_gaps()
    ff_svg, ff_cap = d_failfast()
    lens_svg, lens_cap = d_lenses()
    est_svg, est_cap = d_estimate()
    rows = lambda data: "".join("<tr>" + "".join(f"<td>{'<b>' + E(c) + '</b>' if i == 0 else E(c)}</td>" for i, c in enumerate(r)) + "</tr>" for r in data)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › The technical anchor</p>
<p class="eyebrow" style="margin-top:22px">Data engineering · a guide for developers stepping up</p>
<h1>The technical anchor: how to think for a whole data project</h1>
<p class="lede">On most data projects, one developer ends up holding the whole technical picture: how the sources, the pipelines, the platform, the tests, the release and the people all fit together. Call that person the <b>technical anchor</b>. This guide is about how to think in that seat: proactive, big picture, and failing fast on design, estimates, scope and decisions, for yourself and for everyone around you.</p>
<nav class="toc"><b>On this page</b><ol>
<li><a href="#what">What a technical anchor is</a></li><li><a href="#gaps">Why one role decides success</a></li>
<li><a href="#map">Everyone around you: the map</a></li><li><a href="#jobs">What the anchor owns</a></li>
<li><a href="#mindset">The mindset: proactive, big picture, fail fast</a></li><li><a href="#design">Fail fast on architecture</a></li>
<li><a href="#lenses">A design that works from every side</a></li><li><a href="#estimate">Fail fast on estimates</a></li>
<li><a href="#scope">In scope, out of scope</a></li><li><a href="#decisions">Decisions and sign-off</a></li>
<li><a href="#stake">Help your stakeholders fail fast</a></li><li><a href="#risks">Risks and dependencies</a></li>
<li><a href="#run">Test, deploy and run, from week one</a></li><li><a href="#first30">Your first 30 days</a></li>
<li><a href="#rhythm">A weekly rhythm</a></li><li><a href="#mistakes">Mistakes</a></li><li><a href="#check">Questions to check yourself</a></li></ol></nav>

<section id="what"><p class="q">Who is the technical anchor?</p><h2>What a technical anchor is</h2>
<p>Not the boss, and not only the architect. The technical anchor is the person the whole project can lean on for one question: <b>will this actually work, end to end, for everyone who depends on it?</b> Sometimes the title is tech lead, lead engineer or delivery architect. The title matters less than the habit.</p>
<p>An anchor holds a ship steady while everything around it moves. On a project, requirements shift, sources change, dates slip and people come and go. The anchor keeps the technical picture steady and connected, so the project doesn't drift.</p>
<p>The anchor still writes code. But their most valuable work is often not code at all: a question asked in week one, a decision written down, an access request sent early, a risk raised before it bites.</p></section>

<section id="gaps"><p class="q">Why does one role matter so much?</p><h2>Why one role decides success</h2>
<figure class="diagram">{gaps_svg}<figcaption>{E(gaps_cap)}</figcaption></figure>
<p>Look at how data projects actually fail. Rarely because a developer couldn't write the code. Usually because of something between teams: a definition of revenue nobody signed, a source that deletes records without telling anyone, a firewall rule requested too late, tests written after the build, an operations team that met the pipeline on go-live night.</p>
<p>Each team did its own part. Nobody owned the seams. That is the technical anchor's territory.</p></section>

<section id="map"><p class="q">Who do I need to think about?</p><h2>Everyone around you: the map</h2>
<p>The anchor sits in the middle of at least twelve roles. Each one needs something from you, and you need something from each of them. For every role there is also a question that helps <i>them</i> find their own mistakes early, which is where most of the anchor's value comes from.</p>
{hub()}
<p class="note">On a small project one person may wear several of these hats. The roles still exist; someone has to think about each one.</p></section>

<section id="jobs"><p class="q">What is actually on my plate?</p><h2>What the anchor owns</h2>
<p>You won't do all of this yourself. But you own making sure it happens, and noticing when it isn't.</p>
<div class="tw"><table class="t"><tr><th>Area</th><th>What "done well" looks like</th></tr>{rows(RESP)}</table></div></section>

<section id="mindset"><p class="q">How should I think, day to day?</p><h2>The mindset: proactive, big picture, fail fast</h2>
<ul>
<li><b>Proactive.</b> Don't wait to be asked. If a dependency will take six weeks, the right day to request it is today. If a stakeholder hasn't seen real numbers, show them before they ask.</li>
<li><b>Big picture.</b> Every change has an upstream and a downstream. Before changing a table, ask who feeds it and who reads it. Before choosing a pattern, ask which company goal the project serves, and whether this choice helps it.</li>
<li><b>Fail fast.</b> Every plan stands on beliefs: the data exists, the source can take the load, the business agrees on the definitions, the estimate holds. Write them down, and test the riskiest ones first, in the cheapest way that could prove you wrong. The blog post <a href="/writing/fail-fast-own-the-result/">fail fast, own the result</a> walks through the method.</li>
</ul>
<figure class="diagram">{ff_svg}<figcaption>{E(ff_cap)}</figcaption></figure></section>

<section id="design"><p class="q">How do I fail fast on the architecture?</p><h2>Fail fast on architecture</h2>
<ol class="steps">
<li><b>List the design's riskiest beliefs.</b> "CDC from the source is possible." "The volume fits a daily batch." "The gold table can serve the dashboard at this grain." "The platform allows this pattern."</li>
<li><b>Build a thin slice, end to end, in the first two weeks.</b> One source table, through landing, bronze, silver and gold, to one dashboard tile or one query, deployed to a production-like environment. It will expose access, network, format, volume and tooling problems that no diagram will. The <a href="/learn/data-platform-architecture/">data platform architecture</a> guide shows the layers it should cross.</li>
<li><b>Spike the unknowns, with a timebox.</b> "Two days to prove we can read the mainframe extract. If not, we escalate." A spike without a timebox is just slow building.</li>
<li><b>Write short decision records.</b> One page each: the question, the options, what you chose, why, and what would make you revisit it. They let others challenge the design early, and stop it being re-argued later.</li>
<li><b>Review it with the whole map, not only architects.</b> Ask operations how they would rerun it, security where personal data flows, testers how they would check it, consumers whether the grain fits.</li>
<li><b>Know your kill line.</b> Decide in advance what result would make you change the design, before the spike runs.</li>
</ol></section>

<section id="lenses"><p class="q">What makes a design good for this project?</p><h2>A design that works from every side</h2>
<p>A design usually reflects the angle its author cares about most: speed, elegance, cost, or the tool they know. A good design for a project works from every side. Look at it through eight lenses, and write one answer per lens.</p>
<figure class="diagram">{lens_svg}<figcaption>{E(lens_cap)}</figcaption></figure>
<p>For data projects, the <b>Data</b> lens hides the most traps. Ask early: what is the grain of each table; does the source delete or correct records; can rows arrive late; do we need history; can the same file arrive twice? Each of these is a recorded scene in the <a href="/learn/data-platform-sim/problems/">Problem Lab</a>, with what goes wrong and the right fix. Concepts worth knowing cold: <a href="/concepts/idempotency/">idempotency</a>, <a href="/concepts/incremental-loads/">incremental loads</a>, <a href="/concepts/scd/">slowly changing dimensions</a>, <a href="/concepts/schema-evolution/">schema evolution</a> and <a href="/concepts/data-contracts/">data contracts</a>.</p></section>

<section id="estimate"><p class="q">How do I stop estimates going wrong?</p><h2>Fail fast on estimates</h2>
<figure class="diagram">{est_svg}<figcaption>{E(est_cap)}</figcaption></figure>
<ul>
<li><b>Count before you guess.</b> Sources, tables, transformation rules, reports, interfaces, environments. Data projects are lists of similar things; estimate per thing.</li>
<li><b>Let the thin slice correct you.</b> Say the first table took six days including setting up the framework, and the next three took one and a half days each. Now you have a real rate for the remaining forty. (These numbers are an example.)</li>
<li><b>Give a range with its assumptions.</b> "Seven to ten weeks, assuming source access by the 15th, no history load, and definitions signed by week three." When an assumption breaks, the estimate changes, visibly and without blame.</li>
<li><b>Estimate the invisible work.</b> Access, environments, testing, data fixes, performance tuning, documentation, hand-over, the cut-over weekend. It is usually a third or more of the effort, and usually left out.</li>
<li><b>Track planned against actual every week,</b> and say the gap the week it appears.</li>
</ul></section>

<section id="scope"><p class="q">What is in, what is out?</p><h2>In scope, out of scope</h2>
<p>Anything not written as out of scope will be assumed to be in. Data projects have the same ten traps every time. Put each one explicitly in or out, in writing, and get it signed.</p>
<div class="tw"><table class="t"><tr><th>Scope trap</th><th>The question to settle</th></tr>{rows(SCOPE_TRAPS)}</table></div>
<p>Keep a "parking lot" for good ideas that are out of scope, so saying no doesn't feel like losing them. Any change after sign-off goes through the agreed change process, with its effect on the estimate shown. The concept page on <a href="/concepts/scope-out/">scoping out</a> has more.</p></section>

<section id="decisions"><p class="q">Which decisions need a signature?</p><h2>Decisions and sign-off</h2>
<p>One missed requirement or one decision nobody signed can cost weeks at the end. A decision that isn't written down will be reopened by someone who wasn't in the room. Keep a decision log from day one.</p>
<pre class="tpl">Decision:    What counts as revenue in the sales dashboard
Options:     A gross incl. tax   B net of tax   C net of tax and returns
Chosen:      C
Why:         matches the finance month-end report
Owner:       Head of sales analytics
Signed by:   Finance controller, 12 Nov
Revisit if:  finance changes its month-end definition</pre>
<p>The decisions data projects most often leave unsigned:</p>
<div class="tw"><table class="t"><tr><th>Kind</th><th>Example</th></tr>{rows(DECISIONS)}</table></div>
<p>Give each open decision a deadline and a default: "If we don't hear by Friday, we go with option C." It keeps the project moving and makes the cost of delay visible.</p></section>

<section id="stake"><p class="q">How do I manage stakeholders, beyond my own manager?</p><h2>Help your stakeholders fail fast</h2>
<p>Managing stakeholders is not only keeping them informed. The bigger job is helping each of them find <i>their</i> mistakes early: a business definition that doesn't match the data, a security rule nobody mentioned, an operations need nobody asked about. If they find it at go-live, it is your project that fails.</p>
<ul>
<li><b>Show real data early.</b> A profile of their own data in week one or two surfaces wrong assumptions faster than any meeting.</li>
<li><b>Demo every two weeks with real numbers,</b> not slides. People react to numbers they recognise.</li>
<li><b>Ask the question they haven't thought of.</b> "What should happen to a customer who is deleted in the CRM?" "Who reruns this if it fails on a holiday?"</li>
<li><b>Make the cost of a late change visible.</b> "Changing the grain now costs two days; after testing it costs three weeks."</li>
<li><b>Go beyond your immediate stakeholder.</b> Source owners, operations, security and downstream consumers are often not in the weekly meeting, and they are the ones who block go-live.</li>
<li><b>Bad news early, with a next step.</b> "The source can't provide deletes. We propose a weekly key reconciliation instead; it adds three days. We need your decision by Thursday."</li>
</ul>
<p>Click through the roles in <a href="#map">the map above</a>: each one has its own fail-fast question.</p></section>

<section id="risks"><p class="q">How do I keep risks under control?</p><h2>Risks and dependencies</h2>
<p>Keep one short log with four kinds of item, often called RAID: <b>R</b>isks (might happen), <b>A</b>ssumptions (believed, not yet proved), <b>I</b>ssues (happening now) and <b>D</b>ependencies (waiting on someone). Keep the top five visible and review them every week.</p>
<pre class="tpl">Risk:        Source team release on 20 Nov may rename columns
Likelihood:  medium     Impact: high (silver loads fail)
Trigger:     release notes not shared by 13 Nov
Mitigation:  contract check before each write; mapping in the manifest
Owner:       Technical anchor, with source system owner
Review:      weekly</pre>
<p>A risk without an owner and a trigger is a worry, not a risk. Assumptions are the most dangerous entries, because they look settled: test them like any other belief.</p></section>

<section id="run"><p class="q">How do I avoid a painful go-live?</p><h2>Test, deploy and run, from week one</h2>
<ul>
<li><b>Test from the first pipeline.</b> Row counts, sums and keys reconciled from source to gold; data quality rules on each table; a check that a rerun doesn't double anything. Tests written after the build find problems when they are most expensive.</li>
<li><b>Deploy from week one.</b> The thin slice should already travel through the release pipeline. The first production deployment should never be go-live day.</li>
<li><b>Design for the night shift.</b> For each pipeline, write how to tell it failed, how to rerun it safely, and who to call. Run a failure drill with operations before go-live.</li>
<li><b>Rehearse the cut-over.</b> Write the steps, run them in a test environment, time them, and agree the rollback point.</li>
<li><b>Plan the hand-over.</b> A runbook, the decision log, the tests the support team can rerun, and one person on their side who has made a change while you watched. The concept page on <a href="/concepts/handover/">hand-over</a> has the checklist.</li>
</ul></section>

<section id="first30"><p class="q">I've just been made the technical anchor. Where do I start?</p><h2>Your first 30 days</h2>
<div class="tw"><table class="t"><tr><th>When</th><th>What</th></tr>{rows(FIRST30)}</table></div></section>

<section id="rhythm"><p class="q">What does a normal week look like?</p><h2>A weekly rhythm</h2>
<div class="tw"><table class="t"><tr><th>When</th><th>What</th></tr>{rows(WEEKLY)}</table></div></section>

<section id="mistakes"><p class="q">What do new anchors get wrong?</p><h2>Mistakes</h2>
<ol class="steps">{"".join(f"<li><b>{E(a)}.</b> {E(b)}</li>" for a, b in MISTAKES)}</ol></section>

<section id="check"><p class="eyebrow">Self-check</p><h2>Questions to check yourself</h2>
<ol>{"".join(f"<li>{E(q)}</li>" for q in QUESTIONS)}</ol>
<p>The anchor doesn't make every decision or write every line. The anchor makes sure nothing important falls between the people who do.</p></section>

<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2>
<p><b>The thinking habit underneath:</b> <a href="/writing/fail-fast-own-the-result/">fail fast, own the result</a>. <b>The customer-facing cousin of this role:</b> <a href="/writing/forward-deployed-engineer/">what a forward-deployed engineer does</a>.</p>
<p><b>The system you are anchoring:</b> <a href="/learn/data-platform-architecture/">data platform architecture</a>, <a href="/learn/medallion-architecture/">the medallion</a>, and <a href="/learn/data-platform-sim/problems/">19 data problems, recorded</a>. <b>The path:</b> <a href="/paths/data-engineering/">data engineering, crawl to run</a>.</p></section>"""
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": "The technical anchor: how to think for a whole data project",
           "description": "A guide for developers acting as the technical anchor of a data engineering project: the roles around them, failing fast on architecture, estimates, scope and decisions, stakeholder management, risks, and test-deploy-run from week one.",
           "url": URL, "inLanguage": "en", "isAccessibleForFree": True, "dateModified": "2026-10-31",
           "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Learn", "item": f"{SITE}/learn/"},
              {"@type": "ListItem", "position": 2, "name": "The technical anchor", "item": URL}]}]
    head = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    desc = "How to think as the technical anchor of a data engineering project: the twelve roles around you, failing fast on architecture, estimates and scope, decisions and sign-off, stakeholders, risks, and a first-30-days plan."
    return wb.page("The technical anchor: how to think for a whole data project", desc, URL, body, head)


def main():
    out = ROOT / "learn" / "technical-anchor"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("technical anchor guide ->", out)


if __name__ == "__main__":
    main()
