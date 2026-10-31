"""The three hub pages the site menu points to: /simulators/, /research/, /about/.

    python3 _site/hubs.py

Added 31 Oct 2026 with the new menu (_site/nav.py). Each page is a short list of cards that
point at the real pages; edit the lists below and rebuild. Run _site/seo.py afterwards.
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("writing_build", ROOT / "_writing" / "build.py")
wb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wb)
SITE = wb.SITE

CSS = """<style>
  .crumbs { font-size:13.5px; color:var(--faint); margin:28px 0 0; } .crumbs a { color:var(--muted); }
  .lede { font-size:19px; color:var(--ink-soft); }
  .group { margin:34px 0 0; } .group h2 { margin:0 0 4px; } .group > p { color:var(--ink-soft); }
  .cards { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:16px; margin:14px 0 0; }
  .card { border:var(--line); border-radius:var(--wob); padding:14px 18px; background:var(--w,#fff); display:flex; flex-direction:column; }
  .card h3 { font-family:var(--hand); font-weight:400; font-size:24px; margin:0 0 2px; } .card h3 a { color:var(--ink); text-decoration:none; }
  .card h3 a:hover { text-decoration:underline; text-decoration-style:wavy; }
  .card .v { font-size:12.5px; color:var(--faint); margin:0 0 6px; }
  .card p { font-size:15px; color:var(--ink-soft); margin:0 0 10px; line-height:1.5; }
  .card .links { margin-top:auto; display:flex; gap:14px; flex-wrap:wrap; font-size:14.5px; }
  .tag { display:inline-block; font-size:11.5px; font-weight:700; padding:0 8px; border-radius:999px; border:1.5px solid var(--ink); background:#fff; vertical-align:2px; }
  .tag.real { background:var(--mint-wash); } .tag.ill { background:var(--butter-wash); } .tag.plan { background:var(--rose-wash); }
  .loopmini { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin:16px 0; }
  .loopmini a { border:var(--line); border-radius:var(--wob); padding:10px 12px; text-decoration:none; color:var(--ink); background:var(--w); }
  .loopmini b { font-family:var(--hand); font-weight:400; font-size:24px; display:block; } .loopmini span { font-size:13.5px; color:var(--muted); }
  @media (max-width:640px) { .loopmini { grid-template-columns:1fr 1fr; } }
</style>"""


def card(title, href, v, text, links=(), wash="#fff", tag=None):
    t = {"real": ("recorded for real", "real"), "ill": ("illustrative", "ill"), "plan": ("planned", "plan")}
    tg = f' <span class="tag {t[tag][1]}">{t[tag][0]}</span>' if tag else ""
    ls = "".join(f'<a href="{h}">{n}</a>' for n, h in links)
    return (f'<div class="card" style="--w:{wash}"><h3><a href="{href}">{title}</a></h3><p class="v">{v}{tg}</p>'
            f'<p>{text}</p><div class="links">{ls}</div></div>')


def group(gid, h, p, cards):
    return f'<section class="group" id="{gid}"><h2>{h}</h2><p>{p}</p><div class="cards">{"".join(cards)}</div></section>'


def crumbs(name):
    return f'<p class="crumbs"><a href="/">Home</a> › {name}</p>'


# ---------------------------------------------------------------- simulators
def simulators():
    peri, rose, butter = "var(--peri-wash)", "var(--rose-wash)", "var(--butter-wash)"
    body = crumbs("Simulators") + """
<p class="eyebrow" style="margin-top:22px">Run it · step 2 of the loop</p>
<h1>Simulators</h1>
<p class="lede">Reading about a system is one thing; watching it work, step by step, and then breaking it on purpose is how it sticks. Every simulator here says whether its numbers were <b>recorded for real</b> or are <b>illustrative</b>, never passed off as measured.</p>""" + group(
        "agents", "AI agents", "Watch an agent work, then watch it fail and see what catches it.", [
            card("Agent Harness Simulator", "/learn/agent-harness-sim/", "the claims assistant, one turn at a time",
                 "Type a message and watch every step: the systems it talks to, the checks that fire, the code, the variables, the JSON to and from the model, and the trace.",
                 [("Open the simulator", "/learn/agent-harness-sim/"), ("The tutorial", "/learn/agent-harness/")], peri),
            card("AgentTwin: a tiny library agent", "/learn/agenttwin/#sim", "5 scenarios, a well-built and a faulty agent",
                 "Run each scenario against two agents and see which of four judges catches what: something owed and never done, a false reply, a leak, a planted instruction.",
                 [("Play it", "/learn/agenttwin/#sim"), ("The guide", "/learn/agenttwin/")], peri, "ill"),
            card("A day with Babuji", "/projects/babu-companion/simulation/", "a companion for older adults",
                 "Twelve moments from one day with Babu, a Hindi-speaking companion: what it says, and the rules behind each reply.",
                 [("Open it", "/projects/babu-companion/simulation/"), ("The project", "/projects/babu-companion/")], peri, "ill"),
        ]) + group(
        "data", "Data platforms: the DataTwin Studio", "Real runs on Apache Spark 3.5 and Delta Lake 3.2, recorded on a laptop, so you can see inside the engine.", [
            card("One batch, end to end", "/learn/data-platform-sim/", "scene 1 of the DataTwin Studio",
                 "Follow one day of orders from the source file to the dashboard: config, cluster, every layer, the files on disk, the Delta log. Then load the same file again and watch.",
                 [("Open the studio", "/learn/data-platform-sim/")], rose, "real"),
            card("The Problem Lab", "/learn/data-platform-sim/problems/", "19 problems every data team hits",
                 "Duplicates, re-runs, SCD2 pitfalls, late data, failure mid-job, schema drift, deletes, skew, personal data. Each one: what you see, the naive fix, the right fix.",
                 [("Open the lab", "/learn/data-platform-sim/problems/")], rose, "real"),
            card("Performance stories", "/learn/data-platform-sim/performance/", "the slow job, the clue, the fix",
                 "Detective cases from hours to minutes, each with the Spark UI and event-log clues and the before-and-after numbers.",
                 [("Open the stories", "/learn/data-platform-sim/performance/")], rose, "real"),
            card("Delta Lake internals", "/learn/data-platform-sim/delta/", "files, log, versions",
                 "What a commit writes, how a version is read, time travel, what MERGE really rewrites, deletion vectors.",
                 [("Open it", "/learn/data-platform-sim/delta/")], rose, "real"),
            card("Spark internals", "/learn/data-platform-sim/spark/", "jobs, stages, tasks, plans",
                 "From one query to the stages and tasks that ran it, with the query plan, shuffles and joins.",
                 [("Open it", "/learn/data-platform-sim/spark/")], rose, "real"),
            card("Data quality as metadata", "/learn/data-platform-sim/data-quality/", "one port, two engines",
                 "Rules written as YAML, run by Spark SQL and by Deequ with the same verdicts; quarantine, profiling and an anomaly check.",
                 [("Open it", "/learn/data-platform-sim/data-quality/")], rose, "real"),
            card("DataTwin: a tiny platform", "/learn/datatwin/#sim", "5 days, a well-built and a faulty platform",
                 "A day arrives twice, a column is renamed, a refund is negative, a real sale spike, a source goes dark. Is the dashboard still right?",
                 [("Play it", "/learn/datatwin/#sim"), ("The guide", "/learn/datatwin/")], rose, "ill"),
        ]) + group(
        "exam", "Exam practice", "Drills that put you in the trap before the exam does.", [
            card("CCA-F Trap Gym", "/certifications/claude-certified-architect/CCA-F/Trap-Gym/", "Claude Certified Architect",
                 "Interactive drills for the traps the exam sets: too many tools, a filling context window, a model reviewing its own work.",
                 [("Open the gym", "/certifications/claude-certified-architect/CCA-F/Trap-Gym/"), ("All certifications", "/certifications/")], butter),
        ])
    desc = "Simulators for learning data and AI engineering: step through a real agent turn, a real Spark and Delta batch, 19 data problems, performance stories and exam drills, each labelled real or illustrative."
    return "simulators", wb.page("Simulators", desc, f"{SITE}/simulators/", body, CSS)


# ---------------------------------------------------------------- research
def research():
    peri, rose, butter = "var(--peri-wash)", "var(--rose-wash)", "var(--butter-wash)"
    body = crumbs("Specifications") + """
<p class="eyebrow" style="margin-top:22px">Prove it · step 4 of the loop · open standards and research</p>
<h1>Specifications</h1>
<p class="lede">The interesting failures are almost never in the model or the engine. They are in what surrounds it: the context assembled wrongly, the retry that charged a customer twice, the file that arrived twice and doubled revenue. That part can be specified, built and tested by ordinary means. These specifications are published in the open, name no product, and are versioned and machine-readable.</p>
<p>Each family asks the same three questions: what must <b>exist</b>, what must be <b>true</b>, and what must the system <b>face</b> before it meets real people or real data. The working code built to these specs is under <a href="/assets/">Assets</a>.</p>""" + group(
        "agents", "Clean AI Engineering: for AI agents", "Published and in use: one reference agent passes all four gates.", [
            card("AI Assurance Catalog", "https://dataagentsai.github.io/ai-assurance-catalog/", "AAC · what must be TRUE",
                 "Test obligations for AI applications, by architecture type, with crosswalks to external frameworks.",
                 [("Read the catalog", "https://dataagentsai.github.io/ai-assurance-catalog/"), ("GitHub", "https://github.com/dataagentsai/ai-assurance-catalog")], peri),
            card("AI Harness Catalog", "https://dataagentsai.github.io/ai-harness-catalog/", "AHC · what must EXIST",
                 "Harness capabilities across sixteen layers and ten archetypes. Observability and evals are two of sixteen layers, and that is the point.",
                 [("Read the catalog", "https://dataagentsai.github.io/ai-harness-catalog/"), ("GitHub", "https://github.com/dataagentsai/ai-harness-catalog")], peri),
            card("AgentTwin", "/learn/agenttwin/", "what must be FACED",
                 "Keeps the agent real and simulates its world: customers, systems, data, approvers, faults and time. Then judges what changed, not what was said.",
                 [("Explained", "/learn/agenttwin/"), ("GitHub", "https://github.com/dataagentsai/agenttwin"), ("Its tools", "/learn/agenttwin/open-source/")], peri),
            card("Reference Agent", "https://github.com/dataagentsai/reference-agent", "all of it, built",
                 "A customer-support agent with no agent framework: one module per harness layer, exercised against AgentTwin worlds.",
                 [("GitHub", "https://github.com/dataagentsai/reference-agent"), ("The thesis", "https://github.com/dataagentsai/clean-ai-engineering")], peri),
            card("The agent guardrail catalog", "/learn/agent-guardrails/", "57 guardrails",
                 "Must or should have, rule, classifier or model judge, where each sits, and the test that proves it.",
                 [("Open the catalog", "/learn/agent-guardrails/")], peri),
            card("The AgentTwin Lab", "/lab/", "in progress",
                 "An agent runs for weeks inside a simulated business while an AI fixer repairs it. Does the fixer quietly weaken the checks that caught it?",
                 [("Results so far", "/lab/")], butter),
        ]) + group(
        "data", "Clean Data Engineering: for data platforms", "The same three questions asked of a data platform. Designed; being written spec by spec, with the learning studio already built.", [
            card("DataTwin", "/learn/datatwin/", "what must be FACED",
                 "Keeps the data platform real and simulates the business that feeds it, with planted incidents. Every simulated day, the dashboard is checked against the world's truth.",
                 [("Explained", "/learn/datatwin/"), ("The studio", "/learn/data-platform-sim/")], rose, "plan"),
            card("Data Platform Catalog", "/learn/data-platform-architecture/", "DPC · what must EXIST",
                 "The spine (sources to experiences), the 22 cross-cutting concerns and the port each is reached through. The sibling of the AI Harness Catalog.",
                 [("The architecture it describes", "/learn/data-platform-architecture/")], rose, "plan"),
            card("Data Assurance Catalog", "/learn/datatwin/#coverage", "DAC · what must be TRUE",
                 "Checkable obligations such as 'every silver row traces back to a bronze row', citing DAMA and ODCS instead of restating them.",
                 [("Where it fits", "/learn/datatwin/#setup")], rose, "plan"),
        ]) + """
<p class="note" style="font-size:13.5px;color:var(--faint);margin-top:22px">Code under Apache 2.0, specification prose under CC BY 4.0. Free to use, cite and disagree with.</p>"""
    desc = "Open specifications for AI agents and data platforms: the AI Assurance and Harness Catalogs, AgentTwin, DataTwin, the data platform specs, and the research behind them."
    return "research", wb.page("Specifications", desc, f"{SITE}/research/", body, CSS)


# ---------------------------------------------------------------- about
def about():
    body = crumbs("About") + f"""
<p class="eyebrow" style="margin-top:22px">About</p>
<h1>What this site is</h1>
<p class="lede">A free, open place for engineers who work with data and AI, to learn how real systems work and to build them together. It's a community, not a course you buy: no sign-up, no paywall, no ads, and it stays that way.</p>
<h2>How it is organised</h2>
<p>Everything follows one loop. You see a system drawn, you run it in a simulator, you build it with others, and you prove it against an open standard. What you build becomes the next thing someone else learns from.</p>
<div class="loopmini">
<a href="/learn/" style="--w:var(--mint-wash)"><b>1 · See it</b><span>Courses, paths, concepts</span></a>
<a href="/simulators/" style="--w:var(--peri-wash)"><b>2 · Run it</b><span>Simulators you can break</span></a>
<a href="/projects/" style="--w:var(--rose-wash)"><b>3 · Build it</b><span>Community projects</span></a>
<a href="/research/" style="--w:var(--butter-wash)"><b>4 · Prove it</b><span>Open standards</span></a>
</div>
<p><b>Not sure where to start?</b> <a href="/paths/">Pick your role and cloud</a> for a path from beginner to advanced. Worried about what AI means for your job? <a href="/mindset/">Read the lion story</a> first. Studying for an exam? <a href="/certifications/">Certification prep</a>.</p>
<h2>What we hold to</h2>
<ul>
<li><b>Free, always.</b> Everything here, for everyone.</li>
<li><b>Pictures before detail.</b> Every system is drawn first; every box opens the next level down, to the real code.</li>
<li><b>Honest numbers.</b> A number is either recorded from a real run or labelled illustrative. Every product page says what is built and what is not.</li>
<li><b>Ideas before products.</b> The specs name no product; a separate binding says which product does each job on each cloud.</li>
<li><b>Learn in public.</b> We write up what broke and what the fix turned out to be.</li>
</ul>
<h2>Who runs this</h2>
<p>Started by Basant Choudhary: twenty-three years inside enterprise data platforms, now building and reviewing AI systems that have to survive real data and real operations.</p>
<h2 id="join">Join in</h2>
<p>Pick a <a href="/projects/">project</a> with open work, or lead one that needs a lead. Write a lesson or a post: we help you shape it and share it in <a href="/writing/">Writing</a>. Code and specs are on <a href="https://github.com/dataagentsai">GitHub</a>.</p>
<p>Get in touch: <a href="mailto:basant@cleandataengineering.ai">basant@cleandataengineering.ai</a></p>"""
    desc = "About Clean Data Engineering: a free, open community to learn data and AI engineering by seeing, running, building and proving real systems. Who runs it, what it holds to, how to join."
    return "about", wb.page("About", desc, f"{SITE}/about/", body, CSS)


# ---------------------------------------------------------------- assets
def assets():
    peri, mint, rose = "var(--peri-wash)", "var(--mint-wash)", "var(--rose-wash)"
    body = crumbs("Assets") + """
<p class="eyebrow" style="margin-top:22px">Take it with you · open source</p>
<h1>Assets</h1>
<p class="lede">Working code you can clone, run and reuse in your own systems. Each one is built to the <a href="/specifications/">specifications</a>, tested in the open, and free under Apache 2.0. Each also has a project page that says what it does, what's built, and what work is open if you want to help.</p>""".replace("/specifications/", "/research/") + group(
        "agents", "For AI agents", "From a whole agent down to the libraries that test and check it.", [
            card("Reference Agent", "https://github.com/dataagentsai/reference-agent", "a whole agent, no framework",
                 "A customer-support agent for a clothing shop: one module per harness layer, tested against AgentTwin worlds, passing all four gates. Copy the shape for your own agent.",
                 [("GitHub", "https://github.com/dataagentsai/reference-agent"), ("Project page", "/projects/reference-agent/"), ("How it works", "/learn/agent-harness/")], peri),
            card("AgentTwin", "https://github.com/dataagentsai/agenttwin", "a Python library",
                 "Test any MCP agent in a simulated world: customers, systems, faults and time, judged by what changed. 397 tests; checked against 2,472 τ²-bench runs.",
                 [("GitHub", "https://github.com/dataagentsai/agenttwin"), ("Explained", "/learn/agenttwin/"), ("Project page", "/projects/agenttwin/")], peri),
            card("Eval Harness Framework", "https://github.com/dataagentsai/eval-harness-framework", "a Python framework",
                 "Rebuild each conversation from the agent's own traces and check it against rules written in plain YAML, mixing eval SDKs behind one interface.",
                 [("GitHub", "https://github.com/dataagentsai/eval-harness-framework"), ("The tutorial", "/learn/eval-harness/"), ("Project page", "/projects/eval-harness-framework/")], peri),
            card("Claims assistant on Azure", "https://github.com/dataagentsai/claims-fnol-azure", "a deployed agent",
                 "A motor-insurance claims assistant built to the specs and deployed on Azure: the same harness, with real cloud services in every box.",
                 [("GitHub", "https://github.com/dataagentsai/claims-fnol-azure"), ("Project page", "/projects/claims-fnol-azure/")], peri),
            card("AgentTwin Lab", "https://github.com/dataagentsai/agenttwin-lab", "a long-running test bed",
                 "A simulated business that keeps running for 30 days around an agent, with an AI fixer repairing it. Reuse it to test long-running agents.",
                 [("GitHub", "https://github.com/dataagentsai/agenttwin-lab"), ("Results so far", "/lab/")], peri),
        ]) + group(
        "data", "For data platforms", "Start-from-here code for data engineering.", [
            card("Ecom simple data platform", "https://github.com/basantchoudhary/ecomsimpledataplatformusingdatabricks", "a medallion on Databricks",
                 "A small shop's data platform, bronze to gold on Databricks, used as the first project in the data engineering training.",
                 [("GitHub", "https://github.com/basantchoudhary/ecomsimpledataplatformusingdatabricks"), ("Training portal", "https://basantchoudhary.github.io/DataEngineeringTraining/")], rose),
            card("DataTwin Studio recorders", "/learn/data-platform-sim/", "scripts that record real Spark and Delta runs",
                 "Re-run the Problem Lab, Delta and Spark scenes on your own laptop and get the same recordings the studio shows.",
                 [("The studio", "/learn/data-platform-sim/"), ("DataTwin, explained", "/learn/datatwin/")], rose),
        ])
    desc = "Open-source assets you can reuse: a reference AI agent, the AgentTwin testing library, an eval harness framework, a deployed Azure claims agent, the AgentTwin Lab and data platform starters."
    return "assets", wb.page("Assets", desc, f"{SITE}/assets/", body, CSS)


# ---------------------------------------------------------------- leaders
LEAD_CSS = """<style>
  table.one { border-collapse:collapse; width:100%; margin:14px 0 8px; font-size:16px; }
  table.one th, table.one td { text-align:left; vertical-align:top; padding:10px 12px; border-bottom:1.5px dashed var(--rule-firm); }
  table.one th { width:24%; font-family:var(--hand); font-weight:400; font-size:22px; color:var(--ink); }
  .qa { border-bottom:1.5px dashed var(--rule-firm); padding:14px 0; }
  .qa h3 { font-family:var(--hand); font-weight:400; font-size:24px; margin:0 0 4px; }
  .qa p { margin:0 0 6px; color:var(--ink-soft); } .qa .links { display:flex; gap:14px; flex-wrap:wrap; font-size:14.5px; }
  .cta { border:var(--line); border-radius:var(--wob); padding:14px 18px; background:var(--butter-wash); margin:22px 0; }
</style>"""

QUESTIONS = [
    ("Is our AI agent ready for real customers?",
     "Ready means it keeps every promise it owes, in every situation you can name, under the faults you know about. Ask your team for that list and the evidence for each item, not for a demo.",
     [("AgentTwin, explained", "/learn/agenttwin/"), ("It passed every test. Then it met a real customer.", "/writing/agent-met-real-customer/")]),
    ("Should we build our agent or buy one?",
     "A one-page guide: what you must own, what you can rent, and the questions that decide it.",
     [("Build or buy: a one-page guide for leaders", "/writing/build-or-buy-agent/")]),
    ("What will it cost to run?",
     "One conversation with our reference agent costs under a tenth of a cent. Agents that cost $4 a question usually make the same nine mistakes.",
     [("What one conversation costs", "/writing/one-conversation-cost/"), ("9 cost mistakes", "/writing/agent-cost-mistakes/")]),
    ("How do we know it's paying off?",
     "Count the work it removes and the errors it adds, before you scale it.",
     [("Measuring agent ROI", "/writing/agent-roi/")]),
    ("What can go wrong, and what stops it?",
     "57 common guardrails, each marked must or should, where it sits, and the test that proves it holds.",
     [("The guardrail catalog", "/learn/agent-guardrails/"), ("Security for autonomous agents", "/writing/agent-security/")]),
    ("Is the model the risky part?",
     "Mostly not. In our reference agent the code that calls the model is about 3% (817 of 24,631 lines). Failures live in the other 97%, which ordinary engineering can test.",
     [("Most of an agent is ordinary software", "/writing/agent-is-ordinary-software/")]),
    ("Can we trust the numbers on our dashboards?",
     "Only if someone checks them against the truth, not against last week. A file that arrives twice doubles revenue while every job stays green.",
     [("DataTwin, explained", "/learn/datatwin/"), ("19 data problems, recorded", "/learn/data-platform-sim/problems/"), ("Data contracts", "/writing/data-contracts/")]),
    ("Why is our data platform bill so high?",
     "The same ten leaks show up again and again, from clusters that never scale down to jobs that rewrite everything.",
     [("10 Databricks cost leaks", "/writing/databricks-cost-leaks/"), ("Performance stories, measured", "/learn/data-platform-sim/performance/")]),
    ("Which vendor or platform should we choose?",
     "Decide the design first, without product names; then map it to your cloud. Our specifications name no product, and each cloud gets its own binding.",
     [("One harness, five homes", "/writing/harness-five-homes/"), ("What has settled, what is still open", "/writing/moving-ship/")]),
    ("How do we get our team ready?",
     "Free paths for six roles on every major cloud, from beginner to advanced; a guided cohort for your team if you want one.",
     [("Find a path", "/paths/"), ("Team cohorts", "/business/#cohorts"), ("Data engineer to AI engineer", "/writing/data-engineer-to-ai-engineer/")]),
]


def leaders():
    one = [
        ("The problem", "Companies are putting AI agents in front of customers and AI on top of their data. Most of what goes wrong isn't the model. It is everything around it: the wrong context, a retry that charges a customer twice, a file that arrives twice and doubles revenue."),
        ("What we do", "Build, in the open, the checklists, test worlds and working code that show whether an AI system or a data platform is ready, and teach engineers to build them. Free, with no product to sell."),
        ("What exists today", "Two open checklists (118 things an AI application must have, 118 it must prove). A test world that judges an agent by what it changed, not what it said. A full reference agent that passes all four quality gates. A claims assistant deployed on Azure. A 167-page course and ten simulators."),
        ("Proof so far", "180 planted attacks, all held. On 2,472 recorded runs from an outside benchmark (τ²-bench), our verdicts matched theirs on every rule-breaking change in two of three domains. 19 data problems recorded on real Spark and Delta."),
        ("What isn't done", "Tests use a scripted model, not live models run many times. The test worlds haven't been checked against real systems yet. The data-platform test tool (DataTwin) is designed, due early 2027."),
        ("What it costs you", "Nothing to use: code under Apache 2.0, specifications under CC BY 4.0. Readiness reviews, team cohorts and sponsorship are by arrangement."),
    ]
    rows = "".join(f"<tr><th>{a}</th><td>{b}</td></tr>" for a, b in one)
    qs = "".join(f'<div class="qa"><h3>{q}</h3><p>{a}</p><div class="links">{"".join(f"<a href={chr(34)}{h}{chr(34)}>{n}</a>" for n, h in ls)}</div></div>' for q, a, ls in QUESTIONS)
    body = crumbs("For leaders") + f"""
<p class="eyebrow" style="margin-top:22px">For leaders · CEO, CTO, head of data or AI</p>
<h1>What's going on here, in one minute</h1>
<table class="one">{rows}</table>
<div class="cta"><b>Want this applied to your own systems?</b> <a href="/business/#reviews">Readiness reviews</a> · <a href="/business/#cohorts">team cohorts</a> · <a href="/business/">all the ways to work with us</a></div>
<section class="group" id="questions"><h2>Questions leaders ask</h2><p>Each answer is two lines, with the evidence one click away.</p>{qs}</section>"""
    desc = "The one-minute version for CEOs, CTOs and data and AI leaders: the problem, what exists today, the proof, what isn't done, and short answers to the questions leaders ask about AI agents and data platforms."
    return "leaders", wb.page("For leaders: the one-minute version", desc, f"{SITE}/leaders/", body, CSS + LEAD_CSS)


# ---------------------------------------------------------------- business
def business():
    mail = "mailto:basant@cleandataengineering.ai?subject="
    offers = [
        ("reviews", "Readiness reviews", "var(--peri-wash)",
         "We review an AI agent or a data platform against the open checklists and tell you, in plain words, what is proved, what is a known gap and what is missing, with the evidence for each. You keep the checklist and can rerun it.",
         "by arrangement", mail + "Readiness%20review", "Ask for a review"),
        ("cohorts", "Team cohorts", "var(--mint-wash)",
         "A guided cohort for your team on the free paths: each person on their role and cloud, regular sessions, and a real project at the end that your team keeps.",
         "by arrangement", mail + "Team%20cohort", "Ask about a cohort"),
        ("adopt", "Adopt the specs and code", "var(--rose-wash)",
         "Use the checklists as your team's definition of ready and the code as your starting point. Code under Apache 2.0, specifications under CC BY 4.0: no fee, no sign-up. Questions go to GitHub, where the answers help everyone.",
         "free", "/assets/", "See the assets"),
        ("sponsor", "Sponsor the work", "var(--butter-wash)",
         "Fund a specification, a simulator, or free cohorts for people starting out or between jobs. Sponsors are thanked by name if they wish. They never steer what a specification says, which is why the specifications name no product.",
         "by arrangement", mail + "Sponsorship", "Talk about sponsoring"),
    ]
    cards = "".join(f'<div class="card" id="{i}" style="--w:{w}"><h3>{t}</h3><p class="v">{v}</p><p>{d}</p><div class="links"><a href="{h}"><b>{c} →</b></a></div></div>' for i, t, w, d, v, h, c in offers)
    body = crumbs("For business") + f"""
<p class="eyebrow" style="margin-top:22px">For business</p>
<h1>Work with us</h1>
<p class="lede">Everything on this site is free and open, and stays that way. For companies that want more than the free material, there are four ways to work together.</p>
<div class="cards" style="grid-template-columns:repeat(auto-fit,minmax(300px,1fr))">{cards}</div>
<h2 style="margin-top:34px">How to start</h2>
<p>Write to <a href="mailto:basant@cleandataengineering.ai">basant@cleandataengineering.ai</a> with a few lines on what you have (an agent, a data platform, a team) and what you need to know. If you are a leader new to this, <a href="/leaders/">the one-minute version</a> is the best place to begin.</p>"""
    desc = "Work with Clean Data Engineering: readiness reviews of AI agents and data platforms, team cohorts, adopting the open specifications and code, and sponsoring the work."
    return "business", wb.page("Work with us", desc, f"{SITE}/business/", body, CSS)


# ---------------------------------------------------------------- papers
RELEASES = [
    ("AI Assurance Catalog: test obligations for AI applications, by architecture archetype", "0.17.1", "14 Oct 2026", "10.5281/zenodo.23366151", "ai-assurance-catalog"),
    ("AI Harness Catalog: harness capabilities for AI applications, by architecture archetype", "0.3.1", "14 Oct 2026", "10.5281/zenodo.23366156", "ai-harness-catalog"),
    ("AgentTwin: a world-description format and simulator for testing AI agents", "0.13.0", "13 Oct 2026", "10.5281/zenodo.23366041", "agenttwin"),
    ("Reference Agent: a production-grade customer-support agent built to the AI Harness Catalog", "0.4.0", "14 Oct 2026", "10.5281/zenodo.23366149", "reference-agent"),
    ("AgentTwin Lab: an agent runs simulated days in an AgentTwin world, and the world watches it", "0.4.0", "14 Oct 2026", "10.5281/zenodo.23366521", "agenttwin-lab"),
]


def papers():
    rows = "".join(f'<tr><td><b>{t}</b></td><td>{v}</td><td>{d}</td><td><a href="https://doi.org/{doi}">{doi}</a></td><td><a href="https://github.com/dataagentsai/{r}">code</a></td></tr>' for t, v, d, doi, r in RELEASES)
    body = crumbs("Technical papers") + f"""
<p class="eyebrow" style="margin-top:22px">For leaders and researchers</p>
<h1>Technical papers and citable releases</h1>
<p class="lede">The specifications and code are published as versioned releases with a DOI on Zenodo, so they can be cited like a paper. Each record holds the full text of the specification or the code at that version.</p>
<p class="note" style="font-size:14px;color:var(--faint)">Peer-reviewed papers: none yet. This page lists them as they appear.</p>
<div class="tw" style="overflow-x:auto"><table class="one" style="font-size:14.5px"><tr><th style="width:auto;font-family:var(--sans);font-size:12px">Title</th><th style="width:auto;font-family:var(--sans);font-size:12px">Version</th><th style="width:auto;font-family:var(--sans);font-size:12px">Released</th><th style="width:auto;font-family:var(--sans);font-size:12px">DOI</th><th style="width:auto;font-family:var(--sans);font-size:12px"></th></tr>{rows}</table></div>
<h2 style="margin-top:30px">Research write-ups</h2>
<div class="cards">
{card("The AgentTwin Lab", "/lab/", "research design and results so far", "Can an agent be judged by what it does to a simulated world, and do AI fixers quietly weaken the checks that oversee them? Two proposed studies, the evidence so far, and how to reproduce it.", [("Read it", "/lab/")], "var(--butter-wash)")}
{card("AgentTwin against τ²-bench", "https://github.com/dataagentsai/agenttwin#readme", "an outside benchmark", "2,472 recorded runs in three domains judged by AgentTwin from the published policies alone; every disagreement with τ²-bench's own verdicts has a stated cause.", [("The results table", "https://github.com/dataagentsai/agenttwin#readme")], "var(--peri-wash)")}
{card("Who checks the checker?", "/writing/oracle-problem/", "the oracle problem", "Why generating tests is easy and knowing the right answer is hard, and how a written spec becomes the oracle for agent simulation.", [("Read it", "/writing/oracle-problem/")], "var(--peri-wash)")}
{card("Most of an agent is ordinary software", "/writing/agent-is-ordinary-software/", "a measurement", "Every line of the reference agent sorted by job: the model call is about 3% of the code.", [("Read it", "/writing/agent-is-ordinary-software/")], "var(--peri-wash)")}
</div>
<h2 style="margin-top:30px">How to cite</h2>
<p>Cite the release you used. Each record's DOI resolves to all versions, and Zenodo also gives each release its own. Each repository's <code>CITATION.cff</code> renders as APA or BibTeX from GitHub's "Cite this repository" button.</p>"""
    desc = "Technical papers and citable releases: the AI Assurance and Harness Catalogs, AgentTwin, the Reference Agent and the AgentTwin Lab, each with a DOI, plus research write-ups."
    return "papers", wb.page("Technical papers and citable releases", desc, f"{SITE}/papers/", body, CSS + LEAD_CSS)


def main():
    for fn in (simulators, research, about, assets, leaders, business, papers):
        slug, html = fn()
        out = ROOT / slug
        out.mkdir(exist_ok=True)
        (out / "index.html").write_text(html)
        print("hub ->", slug)


if __name__ == "__main__":
    main()
