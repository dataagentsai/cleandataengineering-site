"""The Forward Deployed Engineer (Data and AI) roadmap: one page at /forward-deployed/.

    python3 _guides/fde_roadmap.py      (then python3 _site/nav.py and python3 _site/seo.py)

A single starting page to talk from. It shows the role on one picture, our recommended roadmap
(principles, four phases, when each of eight tracks is learnt), then a card per track with what to be
able to do at crawl, walk and run, and links into the rest of the site: data engineering, AI engineering,
software, technical anchor, business analysis, agile and delivery, customer craft. Every internal link is
checked against the built site at generation time. Time spans are rules of thumb, stated as such.
"""
import json
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "_paths"))
import components as C  # noqa: E402

wb = C.wb
SITE = wb.SITE
URL_PATH = "/forward-deployed/"
DATE = "2026-11-20"
TITLE = "The Forward Deployed Engineer roadmap for data and AI"
DESC = ("A single roadmap for the forward deployed engineer who works across data engineering, AI engineering, software, "
        "technical anchor, business analysis and agile delivery: the role on one picture, four phases, eight tracks, and links to every guide.")

CLUSTER_FILL = {"data": "#eaf6ef", "ai": "#efeaf8", "eng": "#eef3fb", "cust": "#fff4d6"}

# id, short, name, cluster, what, [crawl, walk, run], links
TRACKS = [
    ("data", "Data engineering", "Data engineering", "data",
     "Moving, shaping and trusting data so every use case has something solid to stand on. This is the base the AI work sits on.",
     ["SQL and Python fluency. Read a source system. Build raw to gold on a small dataset, with tests. Know why file layout matters.",
      "Incremental loads, late data and history (SCD). Quality checks. Read a slow job and say where the time goes. One platform in depth.",
      "Design a customer's platform: layers, contracts, environments, cost model. Review someone's pipeline in ten minutes. Teach it."],
     [("Data engineering hub", "/data-engineering/"), ("Fundamentals: six mind-map guides", "/learn/fundamentals/"), ("Data systems, end to end", "/learn/data-systems/"),
      ("Medallion architecture", "/learn/medallion-architecture/"), ("Shift left: fail fast on data code", "/learn/shift-left/"), ("Learning path: data engineering", "/paths/data-engineering/")]),
    ("platform", "Platform, cost, security", "Platform, cost, security and governance", "data",
     "The cross-cutting concerns that decide whether a system is allowed to run and affordable to keep running.",
     ["Know what a lakehouse, a catalog and a cloud account are. Basic identity and least privilege. Read one line of a cloud bill.",
      "Right-size and schedule compute. Set up environments and CI. Apply masking and row rules. Read a query profile.",
      "Run a cost and security review of a customer platform. Set guardrails and policies. Estimate run cost before building."],
     [("Performance fundamentals", "/learn/fundamentals/performance/"), ("Cost fundamentals", "/learn/fundamentals/cost/"), ("Security fundamentals", "/learn/fundamentals/security/"),
      ("Storage fundamentals", "/learn/fundamentals/storage/"), ("Data platform architecture", "/learn/data-platform-architecture/"), ("Mind map: every concern", "/learn/data-platform-mind-map/"),
      ("AI governance", "/learn/ai-governance/")]),
    ("ai", "AI engineering", "AI engineering", "ai",
     "Putting a model to work inside a system that is tested, bounded and costed. Deterministic first, a model only where judgement on language is needed.",
     ["Call a model. Structured output and tool calling. Know tokens, context and hallucination. Apply the deterministic-first rule.",
      "Build an agent loop with tools and human approval. Evaluate on agreed cases. Add guardrails and tracing. Know the cost per case.",
      "Design a harness many customers can reuse. Set evaluation gates. Choose a model per job. Run it with governance."],
     [("Learning path: AI engineering", "/paths/ai-engineering/"), ("The AI universe", "/learn/ai-universe/"), ("Agent Harness: intro course", "/learn/agent-harness-intro/"),
      ("Which AI model for which job", "/learn/which-model/"), ("Eval Harness", "/learn/eval-harness/"), ("Agent guardrails", "/learn/agent-guardrails/"),
      ("Agent frameworks: when to use which", "/learn/agent-frameworks/"), ("Claude API simulator", "/learn/llm-api-sim/")]),
    ("software", "Software engineering", "Software engineering", "eng",
     "The craft that makes the rest shippable: version control, tests, interfaces, deployment and operating what you build.",
     ["Git, branches and code review. Tests. APIs. Packaging. Reading other people's code without fear.",
      "CI/CD, infrastructure as code, containers, observability. Design for failure and retries.",
      "Ports and adapters, templates and golden paths, decision records. Swap a vendor by writing one adapter."],
     [("Learning path: software engineering", "/paths/software-engineering/"), ("Key concepts: software", "/concepts/#software-engineering"), ("Learning path: LLM engineering", "/paths/llm-engineering/")]),
    ("anchor", "Technical anchor", "Technical anchor and design decisions", "eng",
     "The person who keeps the technical truth of a project: asks the hard questions early, writes decisions down, reviews against checks.",
     ["Understand the role. Write one decision with options and a recommendation. Know what to ask in technical discovery.",
      "Run a technical discovery. Review a data project against stage checks. Raise risk while it is cheap.",
      "Own architecture across a programme. Mentor. Say no, with evidence."],
     [("The technical anchor", "/learn/technical-anchor/"), ("Technical discovery", "/learn/technical-anchor/discovery/"), ("Project review checks", "/learn/technical-anchor/project-review/"),
      ("Critical thinking in data projects", "/how-we-work/critical-thinking/")]),
    ("ba", "Business analysis", "Business analysis and discovery", "cust",
     "Finding the real problem in the customer's words, agreeing how success is measured, and writing down what the system will not do.",
     ["Interview the people who feel the pain. Write the problem in one paragraph they agree with. Learn the source-system questions.",
      "Map data and owners. Write requirements that say what is out of scope. Reconcile numbers with the business.",
      "Run discovery across several workflows. Prioritise by value and effort. Build the business case."],
     [("Business analysis", "/how-we-work/#ba"), ("Discovery: the problem in their words", "/concepts/discovery/"), ("Agree the measure of success", "/concepts/success-measure/"),
      ("Scope by what it will not do", "/concepts/scope-out/"), ("Data map and owners", "/concepts/data-map/"), ("Source system questionnaire", "/learn/data-systems/upstreams/questionnaire/"),
      ("Where data engineering time goes", "/learn/where-data-engineering-time-goes/")]),
    ("agile", "Agile and delivery", "Agile, delivery and estimation", "cust",
     "Slicing work thin, estimating honestly, showing working things often, and keeping the customer's expectations and yours the same.",
     ["Sprints, backlog, definition of done. Slice work thin. A short weekly update.",
      "Estimate with the unknown source in mind. Manage approvals and dependencies. Demo something working every cycle.",
      "Plan multi-team delivery. Manage scope and expectations. Avoid the classic data-project mistakes."],
     [("Project management", "/how-we-work/#pm"), ("Estimation mistakes in data projects", "/how-we-work/estimation/"), ("Top project management mistakes", "/how-we-work/project-management-mistakes/")]),
    ("craft", "Customer craft", "Customer craft and judgement", "cust",
     "Writing, explaining, showing evidence, handing over. The skill that turns a good build into an engagement the customer keeps.",
     ["One-page writing. Ask five questions of any claim. Explain without jargon.",
      "Evidence pages instead of demos. Steering meetings. Handle disagreement. Write a runbook.",
      "Hand over so you are no longer needed. Build reusable assets. Earn trust over years, not weeks."],
     [("Evidence, not demos", "/concepts/evidence/"), ("Hand-over and runbooks", "/concepts/handover/"), ("One framework, many customers", "/concepts/reusable-assets/"),
      ("Mindset", "/mindset/"), ("First 30 days", "/mindset/first-30-days/"), ("Prototype vs product", "/concepts/prototype-product/")]),
]

# depth per phase (0 none, 1 taste, 2 build, 3 own)
DEPTH = {"data": [3, 3, 2, 2], "platform": [1, 2, 3, 3], "ai": [1, 3, 3, 3], "software": [3, 2, 2, 2],
         "anchor": [1, 2, 3, 3], "ba": [1, 2, 3, 3], "agile": [1, 2, 3, 3], "craft": [1, 2, 3, 3]}

PHASES = [
    ("1. Foundation", "about months 0 to 3", "Be a safe pair of hands on data and code.",
     "Data engineering and software engineering come first, because everything later stands on them. Touch every other track lightly.",
     ["You have built a small pipeline from raw to gold, with tests, in git.", "You can explain why a table is laid out the way it is.", "You can write a customer problem in one paragraph."],
     "One small pipeline repository and a one-page problem statement."),
    ("2. Build", "about months 3 to 6", "Add AI engineering and shape the platform.",
     "Build an agent with tools and a human approval step, and evaluate it on agreed cases. Learn what it costs per run. Start discovery and estimation practice.",
     ["You have an agent with an evaluation set and a cost per case.", "You can say what the model will not do, and why.", "You can read a slow or expensive job and name the bucket."],
     "An agent, its evaluation report and its cost page."),
    ("3. Deliver", "about months 6 to 12", "Run a real engagement, from discovery to hand-over.",
     "Discovery, prototype in days, deploy into the customer's cloud, show evidence, write the runbook. This is where the customer-facing tracks become the main work.",
     ["It runs in their account, not yours.", "You can show quality and cost on one page.", "Their engineers run it without you."],
     "An engagement case study with the evidence page and runbook."),
    ("4. Lead", "year 2 onward", "Make the second customer faster than the first.",
     "Reusable assets with a port and an adapter per customer, architecture ownership, mentoring, and saying no with evidence.",
     ["A second customer reuses your framework with a new configuration.", "Others rely on your reviews and templates.", "You choose which work not to do."],
     "A reusable framework and a design review you led."),
]

PRINCIPLES = [
    ("Deep in data, working across the rest", "A T shape. Data engineering is the deep stroke because AI systems are only as good as the data under them. The other tracks need working skill, not mastery.", "Pick data as your depth; reach 'build' level in every other track before aiming for 'own'."),
    ("Parallel tracks, not a queue", "A forward deployed engineer is never only technical. If customer craft waits until year two, you build the wrong thing very well.", "Touch discovery, estimation and writing from week one, in small doses."),
    ("Learn against one real engagement", "Courses teach vocabulary; a capstone teaches decisions. Choose one realistic problem and let it pull the learning.", "Keep one capstone repository and one decision log for the whole roadmap."),
    ("Deterministic first", "AI engineering sits on top of data and software engineering; it does not replace them. Use code where code works and a model only where judgement on language is needed.", "Before adding a model, write what plain code could do and what it cannot."),
    ("Evidence over demos", "Decision makers approve what they can check. Every phase should end with an artifact someone else can read.", "End each phase with a one-page evidence note: what you built, how you measured it, what it costs."),
    ("One platform deep, others by idea", "Tools change; ideas last. Go deep on one cloud and one data platform and learn the others as concepts.", "Choose your platform from the learning paths, and map every concept to it once."),
    ("Teach it back", "Writing an idea in plain words shows exactly where you do not understand it, and is how you earn trust with customers.", "Write one short note per week. Publish the good ones."),
]

LOOP = [("Discover", "discovery", "/concepts/discovery/"), ("Measure", "success", "/concepts/success-measure/"), ("Scope", "scope-out", "/concepts/scope-out/"),
        ("Map data", "data map", "/concepts/data-map/"), ("Prototype", "in days", "/concepts/prototype-product/"), ("Prove", "evidence", "/concepts/evidence/"),
        ("Deploy", "their cloud", "/concepts/deploy-their-cloud/"), ("Hand over", "runbook", "/concepts/handover/"), ("Reuse", "assets", "/concepts/reusable-assets/")]
LOOP_TEXT = [
    ("Discover", "Talk to the people who feel the pain and watch the work as it is done today.", "Business analysis", "ba"),
    ("Measure", "Agree one or two numbers that mean success, and measure today's value.", "Business analysis", "ba"),
    ("Scope", "Write what the system will not do. Code for the repeatable parts, a model where language needs judgement.", "Technical anchor, AI engineering", "anchor"),
    ("Map data", "Where the data lives, its shape, who can say yes. Most delay is access, not code.", "Data engineering", "data"),
    ("Prototype", "A working demo on their real data in days, not slides.", "Software, data and AI engineering", "ai"),
    ("Prove", "Evaluation on agreed cases, errors listed, cost per case, traces behind examples.", "AI engineering, customer craft", "craft"),
    ("Deploy", "Into their cloud, under their identity, network and approval rules.", "Software, platform, security", "platform"),
    ("Hand over", "Runbook, training, shadowing, clear ownership.", "Customer craft", "craft"),
    ("Reuse", "Keep the framework; bind it to each customer with an adapter and configuration.", "Software engineering, technical anchor", "software"),
]

CAPSTONES = [
    ("Claims first notice of loss on Azure", "/projects/claims-fnol-azure/", "An agent that reads claim emails and fills the form, deployed in a customer-style Azure setup. Good for the Deliver phase."),
    ("Clinical data review agent", "/projects/clinical-data-review-agent/", "A data layer plus an agent that finds issues in clinical trial data, evaluated honestly. Good for the Build phase."),
    ("Eval Harness framework", "/projects/eval-harness-framework/", "The evaluation piece on its own: stores, metrics and runs. Good for learning what 'evidence' means."),
    ("Your own real workflow", "/projects/", "Pick a workflow you or a colleague repeats weekly, write the one-page problem, and run the loop above on it."),
]

RHYTHM = [("About 40%", "Build on the capstone", "Decisions are learnt by making them. Keep a decision log."),
          ("About 20%", "Learn one track on purpose", "Rotate the track each fortnight so none goes cold."),
          ("About 20%", "Customer craft", "Interview someone, write a problem statement, give a short demo, ask for feedback."),
          ("About 10%", "Read other people's systems", "Code review, a postmortem, an architecture. It is the cheapest way to see mistakes."),
          ("About 10%", "Teach it back", "One short note a week, in plain words.")]

SKIP = [("Learning every tool", "Drop", "Tools churn. Learn one platform deep and the rest as concepts."),
        ("Collecting certifications before building", "Delay", "Build something first; take a certification when it confirms what you already do."),
        ("Fine-tuning models early", "Delay", "Most first problems are solved by data, prompts, tools and evaluation. Fine-tune only when an evaluation shows the need."),
        ("Hopping between agent frameworks", "Drop", "Learn the loop, tools, state and approval ideas once; frameworks are wrappers."),
        ("Deep machine learning theory", "Delay", "Useful if your engagements need modelling; not a prerequisite for most forward deployed work."),
        ("Slide-first demos", "Drop", "Show a working thing on their data, then the evidence page."),
        ("Streaming for everything", "Delay", "Real time costs more. Use it only where the business acts within seconds.")]

FAQ = [
    ("What is a forward deployed engineer, in this roadmap?", "An engineer who sits with a customer, finds the real problem and ships a working, evaluated, costed system in the customer's own environment, then hands it over. Here it covers data, AI, software, technical anchor, business analysis and agile delivery."),
    ("Do I need to be expert in all eight tracks?", "No. Be deep in one, usually data engineering, and reach working level in the others. Own the customer-facing tracks by the Deliver phase because that is where engagements are won or lost."),
    ("How long does this take?", "The spans are rules of thumb for someone working on it steadily. If you already work in data, the Foundation phase compresses a lot. If you are starting out, expect it to stretch. The checkpoints matter more than the months."),
    ("Data first or AI first?", "Data first, in small doses of AI from the start. AI built on weak data and weak software is the usual cause of agents that demo well and fail in use."),
    ("Where do certifications fit?", "After you have built something. Use them to confirm a level, not to reach it. The certifications page lists the options by platform."),
    ("Is this the only valid roadmap?", "No. It is our opinion, shaped by the pages on this site. Use the tracks as a menu and change the order to fit the work in front of you."),
]


# ------------------------------------------------------------------ link checking
def L(path):
    base = path.split("#")[0]
    if base and base != "/":
        assert (ROOT / base.strip("/") / "index.html").exists() or (ROOT / base.strip("/")).is_file(), f"missing page: {path}"
    return path


def chips(links):
    return "".join(f'<a class="chip" href="{L(u)}">{E(n)}</a>' for n, u in links)


# ------------------------------------------------------------------ drawings
def _text(x, y, s, size=16, anchor="middle", fill="#333", bold=False):
    w = ' font-weight="700"' if bold else ""
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{fill}"{w}>{E(s)}</text>'


def _rect(x, y, w, h, fill, rx=12, sw=1.6, op=1):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="#1F1F1F" stroke-width="{sw}" opacity="{op}"/>'


def _svg(w, h, body, label):
    defs = ('<defs><marker id="fa" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
            '<path d="M0,0 L10,5 L0,10 z" fill="#1F1F1F"/></marker></defs>')
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{E(label)}">{defs}{body}</svg>'


def drawing_role():
    clusters = [("Data", "data", ["Data engineering", "Platform, cost, security"]), ("AI", "ai", ["AI engineering", "evals, guardrails, harness"]),
                ("Engineering craft", "eng", ["Software engineering", "Technical anchor"]), ("Customer", "cust", ["Business analysis", "Agile and delivery", "Customer craft"])]
    b = ""
    for i, (name, key, lines) in enumerate(clusters):
        x = 10 + i * 232
        b += _rect(x, 12, 218, 150, CLUSTER_FILL[key]) + _text(x + 109, 44, name, 22, "middle", "#1F1F1F", True)
        for j, ln in enumerate(lines):
            b += _text(x + 109, 78 + j * 28, ln, 17, "middle", "#333")
        b += f'<line x1="{x + 109}" y1="164" x2="{x + 109}" y2="204" stroke="#1F1F1F" stroke-width="1.6" marker-end="url(#fa)"/>'
    b += _rect(10, 206, 920, 62, "#fff8e8") + _text(470, 233, "Forward Deployed Engineer, Data and AI", 22, "middle", "#1F1F1F", True)
    b += _text(470, 257, "ships a working, evaluated, costed system the customer's team can own", 17, "middle", "#555")
    return _svg(940, 284, b, "Four clusters of skill (data, AI, engineering craft, customer) combine into the forward deployed engineer who ships a working system the customer can own.")


def drawing_when():
    labels = ["1 Foundation", "2 Build", "3 Deliver", "4 Lead"]
    words = ["", "taste", "build", "own"]
    fills = ["#ffffff", "#eef3fb", "#c9d8f3", "#9fb7e6"]
    b = ""
    x0, cw, rh, top = 300, 154, 40, 14
    for i, lab in enumerate(labels):
        b += _text(x0 + i * cw + cw / 2, top + 22, lab, 18, "middle", "#1F1F1F", True)
    for r, (tid, short, name, cl, *_rest) in enumerate(TRACKS):
        y = top + 36 + r * rh
        b += _rect(10, y + 4, 12, rh - 8, CLUSTER_FILL[cl], rx=3, sw=1.2)
        b += f'<a href="#track-{tid}"><text x="30" y="{y + 26}" font-size="18" fill="#3B4F8F" text-decoration="underline">{E(short)}</text></a>'
        for i, d in enumerate(DEPTH[tid]):
            b += _rect(x0 + i * cw + 3, y + 3, cw - 6, rh - 6, fills[d], rx=6, sw=1.2)
            b += _text(x0 + i * cw + cw / 2, y + 26, words[d] or "-", 16, "middle", "#1F1F1F" if d else "#999")
    h = top + 36 + len(TRACKS) * rh + 8
    return _svg(940, h, b, "A grid showing, for each of eight tracks, how deep to go in each of four phases: taste, build or own."), h


def drawing_loop():
    b = ""
    n = len(LOOP)
    w, gap = 96, 8
    for i, (t, s, href) in enumerate(LOOP):
        x = 10 + i * (w + gap)
        fill = "#eaf6ef" if i < 4 else ("#efeaf8" if i < 7 else "#fff4d6")
        b += f'<a href="{L(href)}">' + _rect(x, 30, w, 76, fill) + _text(x + w / 2, 62, t, 17, "middle", "#1F1F1F", True) + _text(x + w / 2, 86, s, 14, "middle", "#555") + "</a>"
        b += _text(x + w / 2, 22, str(i + 1), 14, "middle", "#555")
        if i < n - 1:
            b += f'<line x1="{x + w + 1}" y1="68" x2="{x + w + gap - 1}" y2="68" stroke="#1F1F1F" stroke-width="1.6" marker-end="url(#fa)"/>'
    b += f'<path d="M{10 + (n - 1) * (w + gap) + w / 2} 108 Q {470} 150 {10 + w / 2} 108" fill="none" stroke="#1F1F1F" stroke-width="1.6" stroke-dasharray="5 4" marker-end="url(#fa)"/>'
    b += _text(470, 146, "the next engagement starts from the assets of the last", 15, "middle", "#555")
    return _svg(940, 160, b, "An engagement loop of nine steps from discover to reuse, each linking to a concept page.")


# ------------------------------------------------------------------ page
CSS = """<style>
  .fd .chip { display:inline-block; border:1.5px solid #1F1F1F; border-radius:999px; padding:2px 12px; margin:3px 4px 3px 0; font-size:14px; text-decoration:none; color:#1F1F1F; background:#fff; }
  .fd .chip:hover { background:#fff4d6; }
  .fd .jump { position:sticky; top:0; z-index:5; background:#fff; padding:8px 0; border-bottom:1.5px dashed #CFCAC0; margin:14px 0 0; }
  .fd .fig { margin:12px 0 16px; } .fd .fig svg { width:100%; height:auto; background:#fff; border:var(--line); border-radius:var(--wob); font-family:var(--hand), sans-serif; }
  .fd .fig p { font-size:13.5px; color:#555; margin:4px 2px 0; }
  .fd .phases { display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:14px; margin:14px 0; }
  .fd .ph { border:var(--line); border-radius:var(--wob); padding:14px 18px; background:#fff; } .fd .ph h3 { font-size:24px; margin:0 0 2px; } .fd .ph .when { color:#555; font-size:14px; margin:0 0 6px; }
  .fd .ph ul { margin:6px 0 8px; padding-left:18px; font-size:15px; } .fd .ph .art { font-size:14.5px; background:#f0f8f3; border-radius:8px; padding:6px 10px; }
  .fd .track { border:var(--line); border-radius:var(--wob); padding:14px 18px 10px; margin:16px 0; background:#fff; scroll-margin-top:60px; }
  .fd .track h3 { font-size:26px; margin:0 0 2px; } .fd .track .what { margin:0 0 8px; font-size:15.5px; }
  .fd .lv { display:grid; grid-template-columns:90px 1fr; gap:4px 12px; font-size:15px; margin:6px 0 10px; } .fd .lv b { font-family:var(--hand); font-weight:400; font-size:19px; }
  .fd .tag { display:inline-block; width:12px; height:12px; border:1.2px solid #1F1F1F; border-radius:3px; margin-right:8px; vertical-align:-1px; }
</style>"""


def page():
    url = f"{SITE}{URL_PATH}"
    jump = "".join(f'<a class="chip" href="#track-{t[0]}">{E(t[1])}</a>' for t in TRACKS)
    when_svg, _ = drawing_when()
    phases = "".join(
        f'<div class="ph"><h3>{E(n)}</h3><p class="when">{E(w)}</p><p><b>{E(goal)}</b> {E(focus)}</p><b>You are ready when</b><ul>{"".join(f"<li>{E(r)}</li>" for r in ready)}</ul><p class="art"><b>Leave behind:</b> {E(art)}</p></div>'
        for n, w, goal, focus, ready, art in PHASES)
    prin = '<div class="tw"><table class="t"><tr><th>Principle</th><th>Why</th><th>What to do</th></tr>' + "".join(
        f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td>{E(c)}</td></tr>" for a, b, c in PRINCIPLES) + "</table></div>"
    tracks = ""
    for tid, short, name, cl, what, lv, links in TRACKS:
        tracks += (f'<div class="track" id="track-{tid}"><h3><span class="tag" style="background:{CLUSTER_FILL[cl]}"></span>{E(name)}</h3><p class="what">{E(what)}</p>'
                   f'<div class="lv"><b>Crawl</b><span>{E(lv[0])}</span><b>Walk</b><span>{E(lv[1])}</span><b>Run</b><span>{E(lv[2])}</span></div>{chips(links)}</div>')
    loop = '<div class="tw"><table class="t"><tr><th>Step</th><th>What happens</th><th>Mostly uses</th></tr>' + "".join(
        f'<tr><td><a href="{L(LOOP[i][2])}"><b>{E(a)}</b></a></td><td>{E(b)}</td><td><a href="#track-{tid}">{E(c)}</a></td></tr>' for i, (a, b, c, tid) in enumerate(LOOP_TEXT)) + "</table></div>"
    caps = '<div class="tw"><table class="t"><tr><th>Capstone</th><th>What it teaches</th></tr>' + "".join(
        f'<tr><td><a href="{L(u)}"><b>{E(n)}</b></a></td><td>{E(d)}</td></tr>' for n, u, d in CAPSTONES) + "</table></div>"
    rhythm = C.table(["Share of your week", "What", "Why"], RHYTHM)
    skip = C.table(["Temptation", "Verdict", "Why"], SKIP)
    body = f"""<p class="crumbs"><a href="/">Home</a> › Forward deployed engineer roadmap</p>
<p class="eyebrow" style="margin-top:22px">Forward deployed engineering · start here · one page</p>
<h1>{E(TITLE)}</h1>
<p class="lede">A forward deployed engineer sits with a customer, finds the real problem and ships a working, evaluated, costed system in the customer's own environment, then hands it over. For data and AI that means being part data engineer, part AI engineer, part software engineer, and part technical anchor, business analyst and delivery lead. This page is the map: our recommended roadmap, and a way into every guide on the site.</p>
<div class="fd">
<div class="jump"><b style="font-size:14px">Jump to a track:</b> {jump}</div>

<section id="picture"><p class="eyebrow">The role on one picture</p><h2>Four kinds of skill, one outcome</h2>
<p>The job is the combination, not any one part. A data platform with no discovery solves the wrong problem; a clever agent on poor data fails in use; a good build the customer cannot run is not finished.</p>
<div class="fig">{drawing_role()}<p>Eight tracks in four clusters. Each track has a card below with what to be able to do and where to learn it.</p></div></section>

<section id="advice"><p class="eyebrow">Our recommendation</p><h2>The roadmap we would follow, and why</h2>
<p>Do not learn the tracks one after another. Learn them in parallel at rising depth, against a real engagement, with one piece of evidence at the end of each phase. Seven principles sit behind that.</p>{prin}</section>

<section id="when"><p class="eyebrow">When to learn what</p><h2>Eight tracks across four phases</h2>
<p>The grid shows how deep to go in each phase: <b>taste</b> (know it exists and try it), <b>build</b> (do it with help), <b>own</b> (do it alone and teach it). Click a track name to jump to its card.</p>
<div class="fig">{when_svg}<p>Depth by phase. Foundation leans on data and software; Build adds AI; Deliver and Lead are customer-facing. Time spans are rules of thumb.</p></div>
<div class="phases">{phases}</div>
<p style="font-size:14px;color:#555">Months are a guide for someone working on this steadily. If you already work in data engineering, Foundation compresses a lot. The checkpoints matter more than the calendar.</p></section>

<section id="tracks"><p class="eyebrow">The eight tracks</p><h2>What good looks like, and where to go next</h2>
<p>Each card says what you should be able to do at <b>crawl</b>, <b>walk</b> and <b>run</b> level, and links to the guides, simulators and learning paths for it. Find your level on each card, then open the next link.</p>{tracks}</section>

<section id="loop"><p class="eyebrow">The engagement</p><h2>One loop that ties the tracks together</h2>
<p>Every engagement runs the same nine steps. Each step is a concept page, and each uses a few of the tracks above.</p>
<div class="fig">{drawing_loop()}<p>Click a box to read the concept. The last step feeds the first step of the next customer.</p></div>{loop}</section>

<section id="capstone"><p class="eyebrow">Practise on something real</p><h2>Capstone projects</h2>
<p>Choose one and keep a decision log. Real constraints teach what courses cannot.</p>{caps}</section>

<section id="rhythm"><p class="eyebrow">Your week</p><h2>A weekly rhythm that keeps all tracks warm</h2>{rhythm}</section>

<section id="skip"><p class="eyebrow">What to leave for later</p><h2>Temptations, with a verdict</h2>{skip}</section>

<section id="certs"><p class="eyebrow">Certifications</p><h2>Where they fit</h2>
<p>Build first, certify to confirm. A sensible order: a platform or cloud certification near the end of Build, an AI certification once you have an agent with an evaluation, and an architect-level certification after your first Deliver. Options by platform are on the <a href="{L('/certifications/')}">certifications</a> page, and the <a href="{L('/paths/forward-deployed/')}">forward deployed learning path</a> lists them per cloud.</p></section>

<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(FAQ)}</section>

<section id="next"><p class="eyebrow">Related</p><h2>All the starting points</h2>
<p>{chips([("Data engineering", "/data-engineering/"), ("Fundamentals", "/learn/fundamentals/"), ("AI engineering path", "/paths/ai-engineering/"), ("Software engineering path", "/paths/software-engineering/"),
          ("Forward deployed learning path", "/paths/forward-deployed/"), ("Technical anchor", "/learn/technical-anchor/"), ("How we work", "/how-we-work/"), ("Mindset", "/mindset/"),
          ("Certifications", "/certifications/"), ("Projects to join", "/projects/"), ("Key concepts, A to Z", "/concepts/")])}</p>
<p style="font-size:14px;color:#555">This roadmap is our opinion, built from the pages on this site. Time spans are rules of thumb, not promises.</p></section>
</div>"""
    crumbs = [("Forward deployed engineer roadmap", url)]
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": TITLE, "description": DESC, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]
    head = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(TITLE, DESC, url, body, head)


def main():
    out = ROOT / "forward-deployed"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(page())
    print("fde roadmap ->", out / "index.html")


if __name__ == "__main__":
    main()
