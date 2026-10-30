"""AgentTwin's open-source tools, one short card each: /learn/agenttwin/open-source/.

    python3 _guides/agenttwin_tools.py

Every tool AgentTwin uses, plans to use, is weighing, or has turned down, with the reason.
Each card: what it is, its job here, input, processing, output, how much work the input is
for the team, what it contributes, and the decision. Sources: ~/agenttwin/ADOPTION.md,
~/agenttwin/README.md and DataAgents.ai/70 (landscape), as of 30 Oct 2026.
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
from diagrams import FILL, arrow, box, svg, text  # noqa: E402

E = wb.E
SITE = wb.SITE
URL = f"{SITE}/learn/agenttwin/open-source/"

# decision -> (label, css class, meaning)
DEC = {
    "in": ("In use", "ok", "opted in and working today"),
    "next": ("Opt in next", "next", "chosen; not plugged in yet"),
    "eval": ("Evaluate", "part", "promising; must prove itself first"),
    "later": ("Later", "later", "right tool, not needed yet"),
    "binding": ("Cloud binding", "later", "the managed version on one cloud, behind the same seam"),
    "out": ("Opt out", "no", "turned down, for the reason given"),
}

# (group, name, decision, what it is, job here, input, processing, output, (effort, why), contributes, why the decision)
G_RUN, G_PICK, G_EDGE, G_TESTS, G_PEOPLE, G_ATTACK, G_GRADE, G_DATA, G_TIME, G_REAL, G_REACH = (
    "Run the tests", "Choose which scenarios to run", "Find the edge values", "Test the tests",
    "Play the people", "Attack the agent", "Grade soft qualities", "Make test data", "Control time",
    "Faults and real systems", "Reach more agents, and share")

TOOLS = [
    (G_RUN, "pytest", "in", "The standard Python test runner.",
     "Runs every scenario and test, and reports which passed.",
     "Test files, and AgentTwin's scenario files.", "Finds the tests, runs them, collects results.",
     "Pass or fail per test, as a JUnit report the gates read.",
     ("None", "the team already writes tests this way."),
     "One runner for unit tests and scenarios alike, so one report holds everything.",
     "The default in Python; a second runner would split the evidence."),
    (G_RUN, "Inspect (UK AI Security Institute)", "eval", "An open framework for running AI evaluations.",
     "Considered as a runner (turned down) and as a grader (still open).",
     "Evaluation tasks: a dataset, a solver, a scorer.", "Runs the tasks against a model or agent and scores them.",
     "Scores and logs per sample.", ("Medium", "each grader is a task to write."),
     "Well-built model graders, if we pick it over DeepEval.",
     "Out as a runner (pytest already does that); still a candidate for soft grading."),
    (G_RUN, "pytest-cov", "next", "Measures which lines of code the tests ran (line coverage).",
     "A floor that may only go up, never a target.",
     "The agent's code and its test run.", "Records each line executed during tests.",
     "A percentage and a list of lines never run.", ("None", "one plugin flag."),
     "Spots code nothing touches. Says nothing about whether the answers were right.",
     "Cheap and useful as a ratchet; misleading as a goal, so it is never the gate."),

    (G_PICK, "allpairspy", "in", "A small Python library for pairwise testing: choose a few combinations that still cover every pair of values.",
     "Picks scenarios across intent × state × customer type × fault.",
     "Lists of values per dimension, plus a rule for which can't go together.",
     "Builds a short list of combinations where every pair appears at least once.",
     "A list of combinations, each a scenario to write.",
     ("None", "AgentTwin reads the dimensions from the spec."),
     "Hundreds of meetings between two things covered by tens of scenarios, not thousands.",
     "Works, but left 187 of 468 possible pairs uncovered for the shop agent; our own code fills the rest."),
    (G_PICK, "PICT (Microsoft)", "eval", "Microsoft's pairwise tool, the industry standard, with first-class 'these can't go together' rules.",
     "A possible replacement for allpairspy.",
     "A model file: parameters, values, and constraints.", "Same job as allpairspy, with stronger constraint handling.",
     "A list of combinations.", ("None", "AgentTwin would write the model file from the spec."),
     "Fewer uncovered pairs, less of our own top-up code.",
     "Worth a test against allpairspy's 187 misses before switching."),
    (G_PICK, "GraphWalker", "out", "A model-based testing tool (Java): draw a system's states as a graph and it walks every arrow.",
     "Its technique is used; the tool is not.",
     "A graph of states and the moves between them.", "Finds paths that cross every move at least once.",
     "Test paths.", ("-", ""),
     "The idea behind AgentTwin's own state-machine walker.",
     "Our state machines are already in the spec; a Java tool for one algorithm would be a heavy dependency."),

    (G_EDGE, "Hypothesis", "in", "Property-based testing for Python: you state a rule that must always hold, it invents hundreds of inputs to break it.",
     "Edge values beyond the ones the spec declares.",
     "A property, such as 'a refused write changes nothing', and the shape of valid inputs.",
     "Generates inputs, runs the check, and when one fails shrinks it to the smallest failing example.",
     "A failing example, or confidence the property held.",
     ("Low", "the spec's own rules supply most properties."),
     "Finds odd inputs nobody would think to type.", "Mature, free, and already a dependency."),
    (G_EDGE, "hypothesis-jsonschema", "in", "Turns a JSON schema into Hypothesis inputs.",
     "Proves each stand-in keeps its own promises: every answer matches its declared shape.",
     "Each tool's input and output schema.", "Generates valid tool inputs and checks every answer.",
     "Failures where a stand-in answers outside its schema.", ("None", "the schemas come from the spec."),
     "Guards the stand-ins themselves; it found a real bug in the claims stand-in.",
     "Test-only dependency; never shipped."),
    (G_EDGE, "Schemathesis", "later", "Hypothesis for web APIs: reads an OpenAPI description and fires generated requests at the API.",
     "Checking a stand-in against a real REST API's contract.",
     "An OpenAPI (or GraphQL) description of the API.", "Generates requests from it and checks the responses.",
     "Responses that break the contract.", ("Low", "if the API already publishes OpenAPI."),
     "Keeps stand-ins honest once we test agents that call REST APIs.",
     "Needed only when non-MCP agents arrive."),

    (G_TESTS, "Mutation testing (the idea)", "next", "Break the system on purpose in small ways and see if any test notices. A break nobody notices is a missing test.",
     "AgentTwin's planned answer to 'are the tests enough?': remove a check, loosen a rule, drop the idempotency key, then run the suite.",
     "The agent's spec and harness settings, and its scenario suite.",
     "Makes many slightly broken copies ('mutants') and runs the suite on each.",
     "A list of surviving mutants: each one a named test that is missing.",
     ("None", "the breaks are generated from the spec's own rules."),
     "The only item on this page that measures how good the suite is, not just how big it is.",
     "We will build a small version that changes rules and checks, because the tools below change program text."),
    (G_TESTS, "mutmut", "out", "A mutation-testing tool for Python. It changes your code (a < becomes <=, a + becomes -) and reruns the tests.",
     "Shown here to explain the idea; not used as the tool.",
     "Python source code and its tests.", "Mutates the code one change at a time and reruns the tests.",
     "Which changes the tests missed.", ("None", ""),
     "Measures unit tests well.",
     "An agent's important rules live in its spec and harness settings, not in arithmetic; mutating Python text would mostly produce noise."),
    (G_TESTS, "Stryker", "out", "The same idea for JavaScript, TypeScript, C# and Scala.",
     "None.", "Source code and tests.", "Mutates and reruns.", "Surviving mutants.", ("-", ""),
     "-", "Wrong languages for us; the idea is what we take."),

    (G_PEOPLE, "LangWatch Scenario (user simulator only)", "in", "An open-source agent-testing library. A model plays the user with a persona, and a model judge scores the chat.",
     "Plays the customer when a scripted one is too predictable.",
     "A persona and a situation, both taken from the scenario.",
     "A model writes the customer's next message, turn by turn, until done or out of turns.",
     "A realistic conversation. AgentTwin then judges it by the world's state.",
     ("None", "the scenario already has it."),
     "Customers who say things nobody scripted. It found a real miss: 'my jacket is lost' never matched the 'lost in transit' rule.",
     "We use only the simulated user. Its judge is out: we judge by state, not by words. No cloud account, nothing uploaded."),
    (G_PEOPLE, "DeepEval Synthesizer + Conversation Simulator", "next", "Generates test conversations ('goldens') from documents or from scratch, then simulates them.",
     "Variety: many wordings and situations for each scenario draft.",
     "Documents (policies, FAQs) or a short description of the users.",
     "A model writes multi-turn situations with an expected outcome.",
     "Draft scenarios, which AgentTwin's loader then checks against the spec.",
     ("Low", "the agent's policy text already exists."),
     "Cuts the tester's hardest manual job: phrasing every case like a real person.",
     "Same family as the soft graders we may adopt; runs on a free hosted model."),
    (G_PEOPLE, "τ²-bench dual control", "eval", "A research benchmark where the customer also has tools and acts on their side (for example on their own phone).",
     "A customer kind that acts, not only talks.",
     "Tools for the customer side.", "Both sides act on one shared world.",
     "Runs where success needs both sides to act.", ("Medium", "customer-side tools must be described."),
     "Covers support flows where the customer must do something.",
     "Needed for telecom-style agents; not for the current ones."),
    (G_PEOPLE, "Azure AI Evaluation Simulator", "binding", "Microsoft's managed user simulator.",
     "The Azure binding of the same seam LangWatch fills.",
     "A persona and task.", "A model plays the user.", "Conversations.", ("Low", ""),
     "Same job on Azure, for teams already there.", "Used only when a project runs on Azure."),

    (G_ATTACK, "PyRIT (Microsoft)", "in", "Microsoft's open-source red-teaming toolkit: attack seeds, 'converters' that rewrite one attack many ways, attacker models, and scorers.",
     "Supplies attack text planted into fields the spec marks untrusted.",
     "An attack goal and the untrusted field (both from the spec).",
     "Rewrites the attack: encodings, ciphers, swapped or invisible characters, jailbreak templates.",
     "Many attack variants. AgentTwin judges each by what changed in the world.",
     ("None", "scaffold writes the goals."),
     "Breadth of attack wording without writing it by hand. 180 generated cases held on both agents.",
     "Only its fixed, free converters: its model-driven parts need a paid model or a download."),
    (G_ATTACK, "AgentDojo (ETH Zürich)", "in", "A research benchmark of prompt-injection attacks planted in emails, files and notes.",
     "Six attack templates and 27 injection tasks, used as data.",
     "The templates and tasks.", "Each task is mapped to a goal in the world's terms.",
     "Planted attacks, judged by state.", ("None", ""),
     "Proven attack shapes from published research.",
     "Copied in as data: installing the package would pull in five model vendors' SDKs."),
    (G_ATTACK, "promptfoo red team", "next", "Generates attacks tailored to your app from a short description of its purpose, with plugins per weakness.",
     "A model-driven red team, beyond PyRIT's fixed rewrites.",
     "A short 'purpose' paragraph: who the users are, what they may see and do.",
     "Plugins generate attacks per weakness; strategies make them harder.",
     "Attacks and a report.", ("Low", "one paragraph, which the spec can supply."),
     "Attacks aimed at this agent's own rules, not generic ones.",
     "Planned behind the same attack seam; AgentTwin keeps judging by state."),
    (G_ATTACK, "Giskard", "eval", "An open-source scanner that probes LLM apps for weaknesses such as injection and made-up answers.",
     "A second opinion scan.", "The agent wrapped as a function.", "Sends generated probes and checks replies.",
     "A list of suspected weaknesses.", ("Low", "a small wrapper."),
     "Quick extra coverage for answer quality.", "Not checked against our needs yet."),
    (G_ATTACK, "garak (NVIDIA)", "out", "A scanner that probes a language model for weaknesses.",
     "None.", "A model endpoint.", "Fires many probes at the model.", "A report of model weaknesses.", ("-", ""),
     "-", "It tests the model, not the agent around it. AgentTwin's question is whether anything harmful reached the world."),
    (G_ATTACK, "DeepTeam", "out", "A red-teaming library from the makers of DeepEval.",
     "None.", "A target and attack types.", "Generates and scores attacks.", "Results.", ("-", ""),
     "-", "Overlaps promptfoo; one red-team generator is enough."),
    (G_ATTACK, "Azure AI Red Teaming Agent", "binding", "Microsoft's managed red team, built on PyRIT.",
     "The Azure binding of the attack seam.", "A target.", "PyRIT attacks plus Azure scorers.", "Attack results.", ("Low", ""),
     "Same job on Azure.", "Used only on Azure projects."),

    (G_GRADE, "DeepEval (or Inspect) graders", "next", "Model judges with a written rubric, for qualities a rule can't check.",
     "Grades tone, clarity and completeness, which state judges can't see.",
     "The conversation and a rubric.", "A model scores it against the rubric.",
     "A score and a reason.", ("Low to medium", "a rubric per quality."),
     "Adds 'was it well said?' to 'was it right?'.",
     "One of the two will be chosen; soft scores never override a state judge."),

    (G_DATA, "Faker", "in", "Generates fake but realistic names, addresses, emails and dates.",
     "A population of customers and orders for long runs (in the Lab).",
     "Which fields to fill and how many rows.", "Generates values; AgentTwin checks every row against the spec's rules.",
     "Rows the world can load.", ("None", ""),
     "Volume and variety without real customer data.", "Small, free, and already in the Lab."),
    (G_DATA, "SDV (Synthetic Data Vault)", "later", "Learns the patterns in real tables and generates new, fake rows with the same patterns.",
     "Realistic messy data at volume.",
     "A sample of real data.", "Fits a model to the sample and generates look-alike rows.",
     "Synthetic tables.", ("High", "needs real data, which a new agent doesn't have, plus privacy review."),
     "Realistic skew and dirt, once an agent has real history.",
     "Every new agent starts with no real data, so it comes later."),

    (G_TIME, "time-machine", "in", "Moves a Python program's clock forward instantly.",
     "'Days have passed' without waiting.", "A target time.", "Fakes the clock the code reads.",
     "The agent sees the new time.", ("None", ""),
     "Tests return windows and expiry in seconds.", "In use in the Lab."),
    (G_TIME, "SimPy", "in", "A discrete-event simulation library: schedules events on a simulated timeline.",
     "The Lab's world that keeps running: arrivals, shifts, incidents.",
     "Rates and a calendar of events.", "Fires events in simulated time.",
     "A simulated day, week or month.", ("Low", ""),
     "Long-running tests of an agent over 30 simulated days.", "A tested engine; no reason to write our own."),

    (G_REAL, "Toxiproxy (Shopify)", "next", "A proxy that adds slowness, drops and errors to network traffic, on command.",
     "Network faults against a real system, not just the stand-in.",
     "A real store running behind it.", "Sits between agent and store and injects faults.",
     "The agent experiences real network trouble.", ("Medium", "needs the real system running."),
     "Checks fault handling holds outside the simulation.", "Planned for real mode."),
    (G_REAL, "Testcontainers", "eval", "Starts throwaway real services (databases, shops) in Docker for each test.",
     "A clean real system per run, in CI.", "A Docker image of the system.", "Starts it, seeds it, tears it down.",
     "A fresh real system.", ("Medium", "Docker images and seeding."),
     "Real-system tests without shared state.", "Per-run namespaces already do this; adopt if CI needs its own."),
    (G_REAL, "VCR.py / pytest-recording", "next", "Records real HTTP calls once, then replays them in later tests.",
     "Replay mode: real answers without calling the real system again.",
     "One recorded session against the real system.", "Saves calls to 'cassettes' and serves them back.",
     "Repeatable real responses.", ("Medium", "one recording run, kept fresh."),
     "Realism at stand-in speed.", "Planned; AgentTwin adds marking stale cassettes."),
    (G_REAL, "Saleor (and similar)", "in", "An open-source online shop.",
     "The real system the shop agent's stand-in is checked against (shadow mode).",
     "A seeded Saleor store.", "The same calls go to stand-in and Saleor; answers are compared.",
     "Where the stand-in differs from reality.", ("Medium", "run and seed it."),
     "Turns 'faithful' from a claim into a check.", "Borrowed, never built; shadow checks are not routine yet."),
    (G_REAL, "WireMock / Prism", "out", "Mock servers that return canned answers (Prism builds them from OpenAPI).",
     "None.", "Request-to-response rules.", "Returns the canned answer.", "Fixed replies.", ("-", ""),
     "-", "A canned mock would cancel a shipped order and the test would pass while proving nothing."),
    (G_REAL, "AWS Strands ToolSimulator", "eval", "A model pretends to be a tool and writes its replies.",
     "Only for read-only, low-stakes tools the spec doesn't describe.",
     "A tool's schema and a prompt.", "A model invents each reply, keeping shared state.",
     "Plausible tool replies.", ("Low", ""),
     "Covers the long tail cheaply.", "Never for a system whose rules matter: a model can be talked into allowing what the real system refuses."),
    (G_REAL, "PostgreSQL per run + pgaudit + wal2json", "later", "A real database per run, with logs of everything read and changed.",
     "Testing agents that query a database directly.",
     "The app's own database migrations and a mapping to the spec.", "Seeds a copy, runs the agent, captures reads and writes.",
     "Exactly what the agent read and changed.", ("Medium to high", "the mapping to the spec."),
     "Reaches agents that bypass tools.", "No such agent in scope yet."),

    (G_REACH, "mitmproxy (DNS interception)", "later", "An HTTPS proxy. Pointing an API's web address at it lets tests catch an unmodified agent's calls.",
     "Testing agents that don't use MCP, without changing them.",
     "A translator per API, from its calls to world actions.", "Intercepts each call and answers from the world.",
     "Any agent, unmodified, in the simulation.", ("High", "one translator per API."),
     "The biggest reach gain; today AgentTwin tests MCP agents only.", "Designed; comes after the current agents."),
    (G_REACH, "OpenEnv (Meta + Hugging Face)", "later", "A standard way to package environments for training agents.",
     "Export AgentTwin worlds so the research community can use them.",
     "An AgentTwin world.", "An adapter wraps it in OpenEnv's interface.", "A shareable environment.",
     ("Medium", "the adapter is ours."), "Reach, not testing power.", "A distribution route, not a dependency."),
    (G_REACH, "pass^k (from τ²-bench)", "in", "A measure, not a tool: run the same scenario k times; it passes only if all k pass.",
     "Reliability with live, random models.", "A scenario and k.", "Runs it k times.",
     "Pass only if every run passed.", ("None", ""),
     "Separates 'worked once' from 'works reliably'.",
     "In the Lab's day report; nightly runs designed. τ²-bench's own 165 tasks are not used as a dependency."),
]

CSS = """<style>
  .crumbs { font-size:13.5px; color:var(--faint); margin:28px 0 0; } .crumbs a { color:var(--muted); }
  .lede { font-size:20px; color:var(--ink-soft); }
  .diagram { margin:18px 0; border:var(--line); border-radius:var(--wob); padding:14px 16px; background:#fff; overflow-x:auto; }
  .diagram svg { width:100%; min-width:680px; height:auto; display:block; } .diagram text { font-family:var(--hand); }
  .diagram figcaption { font-size:13.5px; color:var(--muted); margin-top:6px; }
  .tw { overflow-x:auto; } table.t { border-collapse:collapse; width:100%; font-size:14.5px; margin:8px 0 18px; }
  table.t th, table.t td { text-align:left; padding:7px 9px; border-bottom:1.5px dashed var(--rule-firm); vertical-align:top; }
  table.t th { font-size:11.5px; letter-spacing:.08em; text-transform:uppercase; color:var(--faint); }
  .tag { display:inline-block; font-size:12px; font-weight:700; padding:1px 9px; border-radius:999px; border:1.5px solid var(--ink); white-space:nowrap; }
  .tag.ok { background:var(--mint-wash, #E3F4EA); } .tag.next { background:var(--peri-wash, #F1F4FB); } .tag.part { background:var(--butter-wash); }
  .tag.no { background:var(--rose-wash); } .tag.later { background:#fff; }
  .filters { display:flex; flex-wrap:wrap; gap:8px; margin:14px 0; }
  .filters button { font:inherit; font-size:14px; border:1.5px solid var(--ink); border-radius:999px; padding:3px 12px; background:#fff; cursor:pointer; color:var(--ink); }
  .filters button.on { background:var(--butter-wash); font-weight:700; }
  .tool { border:var(--line); border-radius:var(--wob); padding:14px 18px; margin:12px 0; background:#fff; }
  .tool h3 { margin:0; font-size:24px; display:flex; flex-wrap:wrap; gap:10px; align-items:center; }
  .tool .what { margin:4px 0 10px; color:var(--ink-soft); }
  .tool dl { display:grid; grid-template-columns:150px 1fr; gap:4px 14px; margin:0; font-size:15px; }
  .tool dt { color:var(--faint); font-weight:700; font-size:12px; letter-spacing:.06em; text-transform:uppercase; padding-top:3px; }
  .tool dd { margin:0; }
  .grp { margin-top:34px; }
  .note { font-size:14px; color:var(--faint); }
  @media (max-width:640px) { .tool dl { grid-template-columns:1fr; } }
</style>"""


def slug(s):
    return "".join(c if c.isalnum() else "-" for c in s.lower()).strip("-").replace("--", "-")


def drawing():
    jobs = [("Choose", "which scenarios", "peri"), ("Make data", "rows, edges", "butter"), ("Play people", "customer, approver", "rose"),
            ("Attack", "planted text", "grey"), ("Faults, time", "slow, lost, days", "lilac"), ("Run", "pytest", "white"),
            ("Judge", "state + soft", "mint"), ("Test the tests", "mutation", "gold")]
    b, x = "", 10
    for i, (t, s, f) in enumerate(jobs):
        b += box(x, 20, 126, 78, t, s, f)
        if i < len(jobs) - 1:
            b += arrow(x + 128, 59, x + 138, 59)
        x += 140
    b += text(560, 130, "each job has its own small group of tools below; AgentTwin builds only what none of them does", 15, fill="#1F1F1F")
    return svg(1120, 145, b, "Eight jobs in testing an agent: choose scenarios, make data, play people, attack, faults and time, run, judge, test the tests."), \
        "The jobs a test run needs, in order. Every tool below does one of them."


def page():
    groups = []
    for t in TOOLS:
        if t[0] not in groups:
            groups.append(t[0])
    counts = {k: sum(1 for t in TOOLS if t[2] == k) for k in DEC}
    summary = "".join(
        f'<tr><td><a href="#{slug(t[1])}">{E(t[1])}</a></td><td>{E(t[0])}</td><td><span class="tag {DEC[t[2]][1]}">{DEC[t[2]][0]}</span></td><td>{E(t[10])}</td></tr>'
        for t in TOOLS)
    legend = "".join(f'<tr><td><span class="tag {c}">{l}</span></td><td>{E(m)}</td><td>{counts[k]}</td></tr>' for k, (l, c, m) in DEC.items())
    cards = ""
    for g in groups:
        cards += f'<h2 class="grp" id="{slug(g)}">{E(g)}</h2>'
        for (_, name, dec, what, job, inp, proc, out, (eff, effwhy), contrib, why) in [t for t in TOOLS if t[0] == g]:
            effort = E(eff) + (f": {E(effwhy)}" if effwhy else "")
            cards += f"""<div class="tool" data-dec="{dec}" id="{slug(name)}"><h3>{E(name)} <span class="tag {DEC[dec][1]}">{DEC[dec][0]}</span></h3>
<p class="what">{E(what)}</p><dl>
<dt>Job here</dt><dd>{E(job)}</dd><dt>Input</dt><dd>{E(inp)}</dd><dt>Processing</dt><dd>{E(proc)}</dd><dt>Output</dt><dd>{E(out)}</dd>
<dt>Team effort for input</dt><dd>{effort}</dd><dt>Contributes</dt><dd>{E(contrib)}</dd><dt>Why this decision</dt><dd>{E(why)}</dd></dl></div>"""
    d_svg, d_cap = drawing()
    filt = '<button class="on" data-f="all">All</button>' + "".join(f'<button data-f="{k}">{l}</button>' for k, (l, _, _) in DEC.items())
    js = """<script>(function(){const bs=document.querySelectorAll('.filters button');bs.forEach(b=>b.onclick=()=>{bs.forEach(x=>x.classList.toggle('on',x===b));const f=b.dataset.f;
document.querySelectorAll('.tool').forEach(c=>c.style.display=(f==='all'||c.dataset.dec===f)?'':'none');});})();</script>"""
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › <a href="/learn/agenttwin/">AgentTwin, explained</a> › Open-source tools</p>
<p class="eyebrow" style="margin-top:22px">AgentTwin · the full tool list · {len(TOOLS)} tools</p>
<h1>The open-source tools behind AgentTwin</h1>
<p class="lede">AgentTwin is an assembler: where a proven open-source tool already does a job, it uses that tool behind a seam and builds only what nothing else does. Here is every tool we use, plan to use, are weighing, or turned down, each in one short card: what it is, what goes in, what comes out, how much work the input is for your team, and why we decided what we decided.</p>
<figure class="diagram">{d_svg}<figcaption>{E(d_cap)}</figcaption></figure>
<h2>The decisions at a glance</h2>
<div class="tw"><table class="t"><tr><th>Decision</th><th>Means</th><th>Tools</th></tr>{legend}</table></div>
<div class="tw"><table class="t"><tr><th>Tool</th><th>Job</th><th>Decision</th><th>Why</th></tr>{summary}</table></div>
<p><b>What AgentTwin builds itself, because no tool does it:</b> the world format, the stand-ins that enforce the agent's spec, the four judges that read the world's state, the switch between mock, replay, real and shadow modes, and (next) mutation testing over the spec's rules.</p>
<p class="note">'Team effort for input' means work for the team testing an agent, beyond writing the agent's spec. Most inputs are generated from the spec, so the effort is often none. Tools that need a model run on a free hosted open-weight model where possible.</p>
<h2>Each tool, in one card</h2>
<div class="filters">{filt}</div>
{cards}
<p style="margin-top:30px"><a href="/learn/agenttwin/">← Back to AgentTwin, explained</a></p>{js}"""
    ld = {"@context": "https://schema.org", "@type": "TechArticle", "headline": "The open-source tools behind AgentTwin",
          "description": "Every open-source tool AgentTwin uses or rejects, with input, processing, output, team effort and the reason.",
          "url": URL, "inLanguage": "en", "isAccessibleForFree": True, "dateModified": "2026-10-30",
          "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"}}
    head = CSS + f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
    desc = "Every open-source tool behind AgentTwin (pytest, Hypothesis, PyRIT, LangWatch Scenario, promptfoo, DeepEval, Faker and more): what each is for, input, output, team effort, opted in or out and why."
    return wb.page("The open-source tools behind AgentTwin", desc, URL, body, head)


def main():
    out = ROOT / "learn" / "agenttwin" / "open-source"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("agenttwin tools ->", out, len(TOOLS), "tools")


if __name__ == "__main__":
    main()
