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
    body = crumbs("Research") + """
<p class="eyebrow" style="margin-top:22px">Prove it · step 4 of the loop</p>
<h1>Research and open standards</h1>
<p class="lede">The interesting failures are almost never in the model or the engine. They are in what surrounds it: the context assembled wrongly, the retry that charged a customer twice, the file that arrived twice and doubled revenue. That part can be specified, built and tested by ordinary means. These specifications are published in the open, name no product, and are versioned and machine-readable.</p>
<p>Each family asks the same three questions: what must <b>exist</b>, what must be <b>true</b>, and what must the system <b>face</b> before it meets real people or real data.</p>""" + group(
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
    desc = "Open standards and research for AI agents and data platforms: the AI Assurance and Harness Catalogs, AgentTwin, DataTwin, the reference agent and the AgentTwin Lab."
    return "research", wb.page("Research and open standards", desc, f"{SITE}/research/", body, CSS)


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
<h2>Join in</h2>
<p>Pick a <a href="/projects/">project</a> with open work, or lead one that needs a lead. Write a lesson or a post: we help you shape it and share it in <a href="/writing/">Writing</a>. Code and specs are on <a href="https://github.com/dataagentsai">GitHub</a>.</p>
<p>Get in touch: <a href="mailto:basant@cleandataengineering.ai">basant@cleandataengineering.ai</a></p>"""
    desc = "About Clean Data Engineering: a free, open community to learn data and AI engineering by seeing, running, building and proving real systems. Who runs it, what it holds to, how to join."
    return "about", wb.page("About", desc, f"{SITE}/about/", body, CSS)


def main():
    for fn in (simulators, research, about):
        slug, html = fn()
        out = ROOT / slug
        out.mkdir(exist_ok=True)
        (out / "index.html").write_text(html)
        print("hub ->", slug)


if __name__ == "__main__":
    main()
