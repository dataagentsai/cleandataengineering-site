"""The programme page for Data project essentials: purpose, 26 sessions in 7 parts over 13 weeks, speaker and duration,
self-study, AI for BA / PMO / delivery, skills to prepare, templates for a data project.

    python3 _guides/de_programme.py     (then python3 _site/nav.py, python3 _site/seo.py)

/how-we-work/data-essentials/programme/   the schedule and everything attendees build
Also rewrites the hub (/how-we-work/data-essentials/) so its "How to run it" section links here.
Audience: non-technical roles. Plain words, no code.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import de_essentials as DE  # noqa: E402

E, R, T, table, fig, Lx, L, C = DE.E, DE.R, DE.T, DE.table, DE.fig, DE.Lx, DE.L, DE.C
BLUE, MINT, BUTTER, ROSE, LAV, GREY = DE.BLUE, DE.MINT, DE.BUTTER, DE.ROSE, DE.LAV, DE.GREY
BASE = DE.BASE
SPEAKER = "Basant Choudhary"
PER_WEEK = 2

CSS = """<style>
  .tf .pill { font-size:12px; font-weight:700; border:1.5px solid var(--ink); border-radius:999px; padding:0 8px; white-space:nowrap; background:#fff; }
  .tf .week { border:var(--line); border-radius:var(--wob); padding:8px 16px 4px; margin:12px 0; background:#fff; }
  .tf .week h3 { margin:4px 0; } .tf .week .n { font-family:var(--hand); font-size:26px; margin-right:8px; }
  .tf .week dl { display:grid; grid-template-columns:150px 1fr; gap:4px 12px; margin:8px 0; font-size:15px; }
  .tf .week dt { font-weight:700; } .tf .week dd { margin:0; }
  .tf pre.tree { border:var(--line); border-radius:var(--wob); padding:10px 16px; background:#fff; font-size:14px; line-height:1.5; overflow-x:auto; }
  @media (max-width:640px) { .tf .week dl { grid-template-columns:1fr; } }
</style>"""

# letter: (name, short name for the picture, colour, what it is for)
PARTS = {
    "A": ("The people and the three seats", "People", BLUE, "Who is in a data project, and what the BA, Tech Anchor and PM each own."),
    "B": ("Understand the project", "The project", BUTTER, "The picture, why projects fail, and the lifecycle with its gates."),
    "C": ("Walk the layers", "The layers", MINT, "What to ask at each layer, from the source systems to the people who use the result."),
    "D": ("Run it with the backlog", "The backlog", ROSE, "The reusable backlog, the plan in slices, and testing the riskiest belief first."),
    "E": ("Agile, spec-driven development and everything in git", "Agile, specs, git", LAV, "One way of working: a backlog in slices, a written spec before any build, and every document kept in git."),
    "F": ("Use of AI for BA, PMO and delivery functions", "AI at work", BUTTER, "Where an AI assistant saves time in each function, and how to check what it gives you."),
    "G": ("Skills, estimator, project review and the showcase", "Skills", MINT, "Turn what you learnt into reusable skills, and show one working on your own project."),
}

# number, part, title, minutes, one idea, you can then.  Sessions 1 to 15 are the roadmap topics on the hub page.
NEW = [
    (16, "E", "Agile for a data project: the backlog", 90, "A data backlog is cut in thin slices that run from one source to one trusted number. Each item has a Ready rule and a Done rule.",
     "Build an Agile backlog for a data project from the corpus backlog: slices, stories, Ready and Done."),
    (17, "E", "Spec-driven development", 90, "Write what must be true before anyone builds. The spec is the single source for the build, the test and the review.",
     "Turn a requirement into a short spec with acceptance checks a tester can run on data."),
    (18, "E", "Everything in git", 90, "Git is a shared folder that keeps every version, shows who changed what, and asks for a review before a change is accepted.",
     "Keep requirements, specs, decisions, the backlog and templates as text files in one project repository, and propose a change for review. No code."),
    (19, "E", "Templates for a data project: the starter kit", 60, "A new project should start from a copy of the last good one, not from a blank page.",
     "Copy the starter kit for your project and fill the first five templates."),
    (20, "F", "AI basics for delivery roles", 60, "An AI assistant drafts fast and can be wrong with confidence. You give it context, you check the answer, you stay accountable.",
     "Write a clear request, give the right context, check the result against the source, and know what must never be pasted."),
    (21, "F", "AI for the business analyst", 90, "AI is strongest on the BA's first drafts: questions, requirements, definitions and acceptance checks.",
     "Go from meeting notes to a draft spec, a source question list and a metric definition, then correct each one."),
    (22, "F", "AI for PMO and delivery", 90, "AI reads everything the project wrote and tells you what is missing, late or contradictory.",
     "Produce a weekly status report, a risk and dependency register and a gate pack from real project files."),
    (23, "G", "What a skill is, and how to build one", 90, "A skill is a short written instruction, a template and a checklist that an AI assistant follows the same way every time. It lives in git, so it is reviewed and improved like any document.",
     "Write, test and share your first skill for your own role."),
    (24, "G", "Skill workshop: the estimator for data projects", 90, "An estimate is a count of what can be counted, a range, and the assumptions behind it. Effort and calendar time are kept apart.",
     "Run the estimator on a sample scope, challenge its assumptions, and improve the skill."),
    (25, "G", "Skill workshop: project review", 90, "A review reads the project's documents against the checks for its stage and rates each finding.",
     "Run a project review on real documents and report the findings as Blocker, Major, Minor or Note."),
    (26, "G", "Showcase: your skill on your project", 120, "You have learnt it when you can show it working on your own project.",
     "Present one skill and one filled template from your project, and take a review from the group."),
]
PART_OF_TOPIC = {1: "A", 2: "B", 3: "C", 4: "D"}
SESSIONS = [(n, PART_OF_TOPIC[p], t, 60, idea, able, f"{BASE}#s{n}") for n, p, t, idea, able, *_ in DE.SESSIONS] + [(n, p, t, m, idea, able, f"#n{n}") for n, p, t, m, idea, able in NEW]
assert [s[0] for s in SESSIONS] == list(range(1, 27))

# week: (deep dive on your own: [(href, text)], extra reading in words, what you build)
WEEKS = {
    1: ([(BASE + "ecosystem/", "The ecosystem: one big picture"), ("/learn/technical-anchor/", "The technical anchor, in full")],
        "The list of people on your project against the four groups, and one page on what your seat owns."),
    2: ([(BASE + "alignment/", "Alignment"), ("/learn/data-systems/", "Data systems, end to end (optional)")],
        "A stakeholder grid for your project, and the six layers drawn for it from memory."),
    3: ([("/how-we-work/project-management-mistakes/", "Project management mistakes"), ("/how-we-work/estimation/", "Estimation mistakes")],
        "The failure causes you see on your project today, each with its evidence. Your project placed on the ten stages."),
    4: ([(BASE + "extraction/", "Extraction in depth"), ("/learn/data-systems/upstreams/questionnaire/", "Source system questionnaire")],
        "A filled source questionnaire for one real source, with the unknowns and who could answer them."),
    5: ([("/learn/medallion-architecture/", "Medallion architecture (optional)"), ("/concepts/semantic-layer/", "Semantic layer and metrics")],
        "Three cleaning rules with an owner each, and one metric definition with a formula, an owner and a figure to match."),
    6: ([("/learn/data-systems/downstreams/", "Downstreams, in depth (optional)"), ("/concepts/data-quality/", "Data quality dimensions"), ("/concepts/cost-drivers/", "Where data costs come from")],
        "A consumer register for one report, and a sheet that says who is alerted and who fixes it."),
    7: ([(BASE + "backlog/", "The corpus backlog and its planner"), (BASE + "plan/", "Plan: slices and estimates")],
        "A first backlog filtered to your seat, and a six-month plan cut into three slices."),
    8: ([(BASE + "reviews/", "Reviews and sign-offs"), (BASE + "fail-fast/", "Fail fast")],
        "A one-page risk register, and the Agile backlog template filled for your project."),
    9: ([("/leaders/spec-driven/", "Spec-driven development, for leaders"), ("/concepts/version-control/", "Version control")],
        "One spec with acceptance checks, and your first change proposed and reviewed in the project repository."),
    10: ([("/learn/responsible-ai/", "Responsible AI, explained"), ("/concepts/hallucination/", "Hallucination")],
         "The starter kit copied for your project with five templates filled, and your own list of what you will not paste into an AI tool."),
    11: ([("/concepts/evidence/", "Evidence"), ("/concepts/human-approval/", "Human approval")],
         "Business analysts: a draft spec from real notes, corrected by you. PMO and delivery: a status report and a risk register from real files, corrected by you."),
    12: ([("/how-we-work/estimation/", "Estimation mistakes, read again"), ("/concepts/reusable-assets/", "Reusable assets")],
         "Your first skill, in git, and an estimate for a sample scope given as a range with its assumptions."),
    13: ([("/learn/technical-anchor/project-review/", "Project review"), ("/learn/technical-anchor/project-review/checks/", "Project review: the checks")],
         "A review of one real project document, and your showcase: one skill and one filled template."),
}

PURPOSE = [
    ("Speak one language", "Everyone on a data project uses the same picture, the same ten stages and the same words, so hand-offs between BA, Tech Anchor and PM stop losing meaning."),
    ("Ask the right question early", "Each role knows what to ask at each layer and which early sign points to which failure, while it is still cheap to fix."),
    ("Work one way", "One backlog in slices, a written spec before any build, and every document in git with history and review."),
    ("Use AI safely in every function", "BA, PMO and delivery use an AI assistant for first drafts and checks, and know how to verify the result."),
    ("Leave with reusable assets", "Skills such as the estimator and the project review, and a starter kit of templates that the next project copies."),
]
OUTCOMES = ["Every attendee has filled the core templates for a real project.", "Every attendee has built and shared at least one skill for their role.",
            "The team has one project repository layout that new projects copy.", "Estimates are given as ranges with assumptions, from the same estimator.",
            "Reviews use the same checks and the same four ratings."]

HOW = [("Live session", "60 to 120 minutes", "The idea, the picture, one worked example, then the exercise started together."),
       ("Deep dive on your own", "About 2 hours a week", "You read the pages listed for the week and go deeper on the topic that matters most to your role."),
       ("Build", "Inside the 2 hours", "You fill a template or build a skill on your own project, and put it in the project repository."),
       ("Show", "First 10 minutes of the next session", "Two attendees show what they built. The group gives one improvement each.")]

# role, by the end you can, skills to prepare (names from SKILLS)
ROLE_SKILLS = [
    ("Business analyst", "Run a source meeting. Write a spec with testable acceptance checks. Define a metric with one owner. Compare what people say, what documents say and what the data shows.",
     ["Requirement to spec", "Source question list", "Metric definition writer", "Acceptance check reviewer", "Source-to-target mapping draft", "Glossary keeper"]),
    ("Project manager", "Plan in thin slices ordered by risk. Report what was proved, not percent complete. Keep risks and dependencies with owners and dates. Prepare a gate.",
     ["Backlog builder", "Weekly status report", "Risk and dependency register", "Ready checker", "Gate pack builder", "Change request impact"]),
    ("PMO", "Hold every project to the same stages, checks and ratings. See early signs across projects. Keep the templates and skills current.",
     ["Project review", "Portfolio health roll-up", "Template and skill keeper", "Lessons learnt collector"]),
    ("Delivery manager", "Challenge an estimate and its assumptions. Decide go, change or stop at a gate. Make sure someone can run it after go-live.",
     ["Data project estimator", "Project review", "Proposal and statement-of-work checker", "Handover and runbook checker"]),
    ("Product owner", "Order the backlog by value and risk. Accept a slice against its spec. Agree the date the old report is switched off.",
     ["Backlog builder", "Metric definition writer", "Change request impact"]),
    ("Tester or QA", "Turn acceptance checks into tests on data. Plan reconciliation to a figure the business already trusts.",
     ["Acceptance check reviewer", "Test and reconciliation plan writer"]),
    ("Tech Anchor", "Explain the design in plain words. Give a range with its assumptions. Name the riskiest belief and test it first.",
     ["Data project estimator", "Discovery pack summary", "Project review"]),
    ("Sponsor or leader", "Read a status report for what was proved. Ask the gate questions. Decide on evidence.",
     ["Gate pack builder (reads its output)", "Portfolio health roll-up (reads its output)"]),
]

# name, for, what it does, you give it, you get, session
SKILLS = [
    ("Data project estimator", "Tech Anchor, PM, delivery manager", "Counts what can be counted and gives an effort range with its assumptions. Keeps effort apart from calendar time.",
     "Number of sources, datasets, metrics, reports, environments and approvals; the unknowns.", "A low, likely and high estimate by stage, the assumptions, and what would change the number.", 24),
    ("Project review", "PMO, delivery manager, Tech Anchor", "Reads the project's documents against the checks for its stage.", "The project repository, or the documents for one gate.", "Findings rated Blocker, Major, Minor or Note, each with the evidence and an owner.", 25),
    ("Backlog builder", "PM, BA, product owner", "Pulls the right items from the corpus backlog and arranges them in slices.", "The metrics wanted, the sources, and the stage.", "An Agile backlog for the project with slices, stories, Ready and Done.", 16),
    ("Requirement to spec", "BA", "Turns notes into a short spec in the team's template.", "Meeting notes, an old report, a request.", "A draft spec with acceptance checks, and a list of open questions.", 21),
    ("Source question list", "BA, Tech Anchor", "Prepares the questions for a source meeting and records the answers.", "What is known about the source so far.", "Questions grouped by topic, then a filled questionnaire with the unknowns marked.", 21),
    ("Metric definition writer", "BA, product owner", "Writes one definition per number.", "The name of the number and how people describe it.", "Name, formula, grain, owner, the figure to match, and the questions still open.", 21),
    ("Acceptance check reviewer", "BA, tester", "Finds wishes that cannot be tested.", "A spec or a list of requirements.", "Each line marked as a check on data or a wish, with a suggested rewrite.", 17),
    ("Source-to-target mapping draft", "BA", "Drafts which source field feeds which target field.", "Source field lists and the target design.", "A mapping sheet with the gaps and the rules still to be agreed.", 21),
    ("Glossary keeper", "BA", "Keeps one meaning per business word.", "Specs, notes and reports.", "New words, words used two ways, and words with no owner.", 21),
    ("Discovery pack summary", "BA, Tech Anchor", "Compares what people say, what documents say and what the data shows.", "Interview notes, documents, profiling results.", "Where the three agree, where they disagree, and what to ask next.", 21),
    ("Meeting notes to actions and decisions", "Everyone", "Turns notes into actions and decision records.", "Notes or a transcript.", "Actions with an owner and a date, and entries for the decision log.", 20),
    ("Weekly status report", "PM", "Writes the report in the 'proved this week' format.", "The backlog, the risk register, the week's notes.", "What was proved, what is blocked, what is needed from whom, by when.", 22),
    ("Risk and dependency register", "PM, PMO", "Matches what it reads to the failure causes and their early signs.", "The project repository and the week's notes.", "Risks and dependencies with an owner, a date and the early sign that was seen.", 22),
    ("Ready checker", "PM, BA", "Checks a backlog item against the Ready rule before the sprint.", "A backlog item.", "Ready or not ready, and what is missing.", 16),
    ("Gate pack builder", "PM, delivery manager", "Gathers the evidence for a sign-off gate.", "The stage and the project repository.", "The list of evidence found, evidence missing, and who signs.", 22),
    ("Change request impact", "PM, product owner", "Shows what a change touches.", "The change and the current backlog and specs.", "Items affected, the effect on effort and date as a range, and the decision needed.", 22),
    ("Stakeholder map and communication plan", "PM, BA", "Places people by influence and interest.", "The cast list.", "A grid, and who hears what, how often, from whom.", 22),
    ("Test and reconciliation plan writer", "Tester", "Turns acceptance checks into tests on data.", "The spec and the trusted figures.", "Test cases, the figures to match, and the tolerance agreed.", 21),
    ("Proposal and statement-of-work checker", "Delivery manager, sponsor", "Reads a proposal for what is missing.", "The draft proposal and the estimate.", "Assumptions not stated, exclusions not stated, and dependencies on the client with no date.", 24),
    ("Handover and runbook checker", "Delivery manager", "Checks that someone else can run it.", "The runbook and the handover notes.", "What is missing: alerts, owners, the rerun steps, the escalation route.", 25),
    ("Portfolio health roll-up", "PMO", "Puts every project on one page, the same way.", "The status reports and review findings of all projects.", "One table: stage, next gate, open Blockers, early signs.", 25),
    ("Template and skill keeper", "PMO", "Checks that projects use the current templates and skills.", "The starter kit and the project repositories.", "Which projects are behind, and which local improvements should go back into the starter kit.", 23),
    ("Lessons learnt collector", "PMO, everyone", "Turns a retrospective into changes.", "Retrospective notes.", "Proposed changes to templates, checks and skills, each as a change for review.", 23),
]

# template, what it is for, folder, owner, first used in session
TEMPLATES = [
    ("Project one-pager", "The question, the people, the scope, the gates.", "00-project", "PM", 19),
    ("Cast and stakeholder map", "Who is on the project and who must hear what.", "00-project", "PM", 3),
    ("Glossary", "Every business word, its meaning and its owner.", "00-project", "BA", 3),
    ("Source register and source questionnaire", "Each source, its owner, and what is known and unknown.", "01-discovery", "BA", 7),
    ("Metric definition sheet", "Name, formula, grain, owner, the figure to match.", "02-specs", "BA", 10),
    ("Spec", "What must be true, with acceptance checks.", "02-specs", "BA", 17),
    ("Source-to-target mapping", "Which source field feeds which target field, and the rule.", "02-specs", "BA", 21),
    ("Agile backlog for a data project", "Slices, stories, Ready and Done, pulled from the corpus backlog.", "03-backlog", "PM", 16),
    ("Estimate sheet", "Counts, ranges, assumptions, effort apart from calendar time.", "03-backlog", "Tech Anchor", 24),
    ("Risk and dependency register", "Each risk with its early sign, owner and date.", "04-run", "PM", 15),
    ("Decision log", "What was decided, by whom, when, and why.", "04-run", "PM", 18),
    ("Weekly status report", "What was proved this week, what is blocked, what is needed.", "04-run", "PM", 22),
    ("Meeting notes", "Notes that end in actions and decisions.", "04-run", "Everyone", 20),
    ("Test and reconciliation plan", "The tests on data and the trusted figures to match.", "05-test", "Tester", 21),
    ("Review checklist and findings log", "The checks for the stage, and findings with a rating.", "06-reviews", "PMO", 25),
    ("Sign-off record", "What is signed, by whom, on what evidence.", "06-reviews", "PM", 25),
    ("Consumer register", "Who uses the result, how fresh it must be, and the switch-off date of the old report.", "07-handover", "BA", 11),
    ("Runbook and handover", "Who is alerted, who fixes it, how to rerun.", "07-handover", "Tech Anchor", 12),
    ("Retrospective", "What to keep, what to change, and the change proposed.", "07-handover", "PM", 26),
]

TREE = """project-name/
  README            what this project is, in one page
  00-project/       one-pager, cast and stakeholders, glossary
  01-discovery/     source register, questionnaires, interview notes
  02-specs/         specs, metric definitions, mapping
  03-backlog/       the Agile backlog, the estimate
  04-run/           status reports, risks, decisions, meeting notes
  05-test/          test and reconciliation plan, results
  06-reviews/       review findings, sign-off records
  07-handover/      consumer register, runbook, retrospective
  skills/           the skills this project uses
  templates/        the blank templates, copied from the starter kit"""

GIT_WORDS = [("Repository", "The project's shared folder. It keeps every version of every file."), ("Commit", "A saved change, with a short note saying why."),
             ("Branch", "Your own copy to work in, so the agreed version stays as it is."), ("Pull request", "A proposed change that someone else reads before it is accepted."),
             ("History", "Who changed what, when and why. It is also the audit trail.")]

AI_USE = [
    ("Business analysis", "Draft the questions for a source meeting. Turn notes into a spec. Draft a metric definition. Find requirements that cannot be tested. Draft a mapping.",
     "Every definition with its business owner. Every figure against the source."),
    ("PMO", "Check every project against the same stage checks. Roll up status across projects. Find the same early sign in several projects. Keep templates current.",
     "The finding against the document it came from. The rating."),
    ("Delivery", "First estimate from the counts. Challenge a plan for missing items. Draft the weekly status report. Build the gate pack. Read a proposal for missing assumptions.",
     "The assumptions. The range. Anything sent to a client."),
]
AI_RULES = ["You own the answer. The AI assistant drafts; a named person checks and signs.", "Give it the template, the spec and the context. A vague request gets a vague answer.",
            "Ask where each statement came from. No source, no trust.", "Client data, personal data and secrets do not go into a tool the client has not approved.",
            "Keep the request, the result and your correction in git, so the skill improves."]

QA = [("Is this for technical people?", "No. It is for business analysts, project and delivery managers, PMO, product owners, testers and sponsors. There is no code. Git is taught as a shared folder with history and review."),
      ("How much time does it take?", "Two live sessions a week for thirteen weeks, and about two hours a week on your own to read deeper and build."),
      ("What is a skill here?", "A short written instruction, a template and a checklist that an AI assistant follows the same way every time. For example the estimator for data projects, or the project review."),
      ("Do I need my own project?", "It helps. Every exercise is done on a real project. If you have none, use a past project you know well."),
      ("Can we run it faster?", "Yes. Parts A to D can run as a three-day workshop, and Parts E to G as five weekly sessions of half a day. The roadmap page lists the shorter formats.")]


def week_of(n):
    return (n - 1) // PER_WEEK + 1


def hm(minutes):
    h, m = divmod(minutes, 60)
    return f"{h} h" + (f" {m} min" if m else "")


def wk_range(nums):
    a, b = week_of(min(nums)), week_of(max(nums))
    return f"Week {a}" if a == b else f"Weeks {a} to {b}"


def pill(letter):
    return f'<span class="pill" style="background:{PARTS[letter][2]}">Part {letter}</span>'


def d_parts():
    b = ""
    for i, (k, (name, short, col, _)) in enumerate(PARTS.items()):
        nums = [s[0] for s in SESSIONS if s[1] == k]
        x = 8 + i * 142
        b += R(x, 34, 132, 92, col, [f"Part {k}", short, wk_range(nums).replace(" to ", "–"), f"{len(nums)} sessions"], 16, sw=2.5 if k in "EFG" else 1.5)
        if i < 6:
            b += DE.AR(x + 133, 80, x + 141, 80)
    b += T(288, 22, "The roadmap: 15 topics", 14) + T(785, 22, "New: ways of working, AI, skills", 14)
    b += T(500, 150, "Every week: two live sessions, a deep dive on your own, and something you build on your own project", 13.5)
    return DE.S(1000, 160, b, "Seven parts over thirteen weeks. Parts A to D are the fifteen roadmap topics: people, the project, the layers, the backlog. "
                              "Parts E to G are new: Agile, specs and git; use of AI for BA, PMO and delivery; skills and the showcase.")


def programme_page():
    url_path = f"{BASE}programme/"
    total = sum(s[3] for s in SESSIONS)
    nweeks = week_of(len(SESSIONS))
    # parts table
    prow = []
    for k, (name, _short, _col, what) in PARTS.items():
        ss = [s for s in SESSIONS if s[1] == k]
        nums = [s[0] for s in ss]
        prow.append([pill(k), f"<b>{E(name)}</b><br>{E(what)}", f"{min(nums)} to {max(nums)}", str(len(ss)), hm(sum(s[3] for s in ss)), wk_range(nums)])
    prow.append(["", "<b>Total</b>", "1 to 26", str(len(SESSIONS)), f"<b>{hm(total)}</b>", f"{nweeks} weeks"])
    parts = table(["Part", "What it covers", "Sessions", "Count", "Live time", "When"], prow)
    # schedule table
    srow = []
    for n, k, t, m, _idea, _able, href in SESSIONS:
        srow.append([f"Week {week_of(n)}", str(n), f'<a href="{href}">{E(t)}</a>', pill(k), E(SPEAKER), f"{m} min"])
    sched = table(["Week", "No.", "Session", "Part", "Speaker", "Duration"], srow)
    # week cards
    weeks = ""
    for w in range(1, nweeks + 1):
        ss = [s for s in SESSIONS if week_of(s[0]) == w]
        deep, build = WEEKS[w]
        sl = "<br>".join(f'{pill(k)} <b>{n}</b> <a href="{href}">{E(t)}</a> · {m} min' for n, k, t, m, _i, _a, href in ss)
        dl = "<br>".join(Lx(h, t) for h, t in deep)
        weeks += (f'<div class="week" id="w{w}"><h3><span class="n">Week {w}</span>{E(" and ".join(sorted({PARTS[s[1]][1] for s in ss}, key=lambda x: [p[1] for p in PARTS.values()].index(x))))}</h3>'
                  f'<dl><dt>Live sessions</dt><dd>{sl}</dd><dt>Speaker</dt><dd>{E(SPEAKER)}</dd><dt>Deep dive on your own</dt><dd>{dl}</dd><dt>You build</dt><dd>{E(build)}</dd></dl></div>')
    # new session cards
    newc = ""
    cur = ""
    for n, k, t, m, idea, able in NEW:
        if k != cur:
            cur = k
            newc += f'<p class="part">Part {k} · {E(PARTS[k][0])}</p>'
        newc += (f'<div class="sess" id="n{n}"><h3><span class="n">{n}</span>{E(t)}</h3><dl><dt>One idea</dt><dd>{E(idea)}</dd><dt>You can then</dt><dd>{E(able)}</dd>'
                 f'<dt>When</dt><dd>Week {week_of(n)} · {m} min · {E(SPEAKER)}</dd></dl></div>')
    purpose = "".join(f"<div><h3>{E(a)}</h3><p>{E(b)}</p></div>" for a, b in PURPOSE)
    outcomes = "".join(f"<li>{E(x)}</li>" for x in OUTCOMES)
    how = table(["Each week", "Time", "What happens"], [[f"<b>{E(a)}</b>", E(b), E(c)] for a, b, c in HOW])
    names = {s[0] for s in SKILLS}
    for _r, _c, sk in ROLE_SKILLS:
        for x in sk:
            assert x.split(" (")[0] in names, x
    roles = table(["Role", "By the end you can", "Skills to prepare for this role"], [[f"<b>{E(r)}</b>", E(c), "<br>".join(E(x) for x in sk)] for r, c, sk in ROLE_SKILLS])
    skills = table(["Skill", "For", "What it does", "You give it", "You get", "Built in"],
                   [[f"<b>{E(a)}</b>", E(b), E(c), E(d), E(e), f'<a href="#n{s}">Session {s}</a>'] for a, b, c, d, e, s in SKILLS])
    tmpl = table(["Template", "What it is for", "Folder", "Owner", "First used"],
                 [[f"<b>{E(a)}</b>", E(b), f"<code>{E(c)}</code>", E(d), f"Session {s}, week {week_of(s)}"] for a, b, c, d, s in TEMPLATES])
    gitw = table(["Word", "What it means, without the jargon"], [[f"<b>{E(a)}</b>", E(b)] for a, b in GIT_WORDS])
    aiuse = table(["Function", "Where AI helps", "What a person must still check"], [[f"<b>{E(a)}</b>", E(b), E(c)] for a, b, c in AI_USE])
    airules = "".join(f"<li>{E(x)}</li>" for x in AI_RULES)
    toc = "".join(f'<li><a href="#{a}">{b}</a></li>' for a, b in [("purpose", "Purpose of the programme"), ("parts", "Seven parts"), ("schedule", "The schedule: sessions, speaker, duration"),
                                                                   ("weeks", "Week by week"), ("new", "The new sessions"), ("git", "Everything in git"), ("ai", "Use of AI for BA, PMO and delivery"),
                                                                   ("roles", "Skills for each role"), ("skills", "Skills that can be prepared"), ("templates", "Templates for a data project"), ("faq", "FAQ")])
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/how-we-work/">How we work</a> › <a href="{BASE}">Data essentials</a> › The programme</p>
<p class="eyebrow" style="margin-top:22px">Programme · for business analysts, PMO, project and delivery managers, product owners, testers and sponsors</p>
<h1>Data project essentials: the {nweeks}-week programme</h1>
<p class="lede">How non-technical roles learn to run a data project: {len(SESSIONS)} sessions in seven parts over {nweeks} weeks, {hm(total)} of live time. No code. Each week you go deeper on your own and build something on your own project.</p>
<div class="tf">{CSS}
<nav class="toc"><b>On this page</b><ol>{toc}</ol></nav>
<section id="purpose"><p class="eyebrow">Why</p><h2>Purpose of the programme</h2>
<div class="box"><b>In one line:</b> every non-technical role on a data project should know what to ask, what to write down and what to check, and should work the same way: Agile, spec first, everything in git, with AI as a helper.</div>
<div class="cards3">{purpose}</div>
<h3 style="margin-top:18px">How we will know it worked</h3><ul>{outcomes}</ul></section>
<section id="parts"><p class="eyebrow">The shape</p><h2>Seven parts over {nweeks} weeks</h2>
{fig(d_parts(), "Parts A to D are the fifteen topics of the roadmap. Parts E to G add the way of working, AI and skills.")}{parts}
<h3 style="margin-top:18px">How each week runs</h3>{how}</section>
<section id="schedule"><p class="eyebrow">The schedule</p><h2>{len(SESSIONS)} sessions, speaker and duration</h2>
<p>Two sessions a week. Sessions 1 to 15 link to their topic on the {L(BASE, 'roadmap')}. Sessions 16 to 26 are described {L('#new', 'below')}.</p>{sched}
<p class="note">Total live time: {hm(total)}. With about two hours a week on your own, the whole programme is about {round((total / 60 + 2 * nweeks) / 5) * 5} hours.</p></section>
<section id="weeks"><p class="eyebrow">Week by week</p><h2>What you attend, read and build each week</h2>
<p>The live session gives the idea. You go deeper on your own with the pages listed, and you build one thing on your own project.</p>{weeks}</section>
<section id="new"><p class="eyebrow">Parts E, F and G</p><h2>The new sessions, one idea each</h2>{newc}</section>
<section id="git"><p class="eyebrow">Part E</p><h2>Everything in git, so AI and spec-driven development can work</h2>
<p>An AI assistant can only help with what it can read. If requirements are in emails, decisions in chat and the backlog in a slide, it reads none of them. When every document is a text file in one repository, a person or an AI assistant can read the whole project, a spec can drive the build and the test, and every change has an author, a reason and a reviewer.</p>
{gitw}<h3 style="margin-top:18px">The project repository</h3><p>One layout for every project. A new project copies it from the starter kit.</p><pre class="tree">{E(TREE)}</pre>
<p class="note">Read more: {Lx('/concepts/version-control/', 'version control')}, {Lx('/leaders/spec-driven/', 'spec-driven development, for leaders')} and {Lx('/learn/checks-as-code/', 'checks as code')}.</p></section>
<section id="ai"><p class="eyebrow">Part F</p><h2>Use of AI for BA, PMO and delivery functions</h2>{aiuse}
<h3 style="margin-top:18px">Five rules for using AI at work</h3><ol class="rules">{airules}</ol>
<p class="note">Read more: {Lx('/learn/responsible-ai/', 'Responsible AI, explained')}.</p></section>
<section id="roles"><p class="eyebrow">Skills development</p><h2>Skills for each role</h2>
<p>Two kinds of skill. What <b>you</b> can do by the end, and the reusable skills you prepare so an AI assistant does the first draft the same way every time.</p>{roles}</section>
<section id="skills"><p class="eyebrow">Part G</p><h2>{len(SKILLS)} skills that can be prepared</h2>
<p>The estimator and the project review are built together in the workshops. Attendees pick the others by role and build them in weeks 11 to 13. Each skill is a folder in git with an instruction, a template and a checklist.</p>{skills}
<p class="note">The skills build on pages that already exist: {Lx('/how-we-work/estimation/', 'estimation mistakes')}, {Lx(BASE + 'plan/', 'plan: slices and estimates')}, {Lx('/learn/technical-anchor/project-review/checks/', 'the project review checks')}, {Lx(BASE + 'reviews/', 'reviews and sign-offs')} and {Lx(BASE + 'backlog/', 'the corpus backlog')}.</p></section>
<section id="templates"><p class="eyebrow">The starter kit</p><h2>Templates for a data project</h2>
<p>{len(TEMPLATES)} templates, each a text file in the project repository. Every one is filled on a real project during the programme.</p>{tmpl}</section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(QA)}</section>
<section id="next"><p class="eyebrow">Go further</p><h2>Related pages</h2><ul><li>{L(BASE, 'The roadmap: 15 topics in 4 parts')}</li><li>{L(BASE + 'ddlc/', 'DDLC by seat')}</li><li>{L(BASE + 'backlog/', 'The corpus backlog')}</li><li>{L(BASE + 'reviews/', 'Reviews and sign-offs')}</li></ul></section>
</div>"""
    title = f"Data project essentials: the {nweeks}-week programme"
    desc = (f"A {nweeks}-week programme for non-technical roles on data projects: {len(SESSIONS)} sessions in seven parts with speaker and duration, Agile and spec-driven development, "
            "everything in git, use of AI for BA, PMO and delivery, skills to prepare for each role, and templates for a data project.")
    return url_path, DE.page_shell(title, desc, url_path, body, [("How we work", "/how-we-work/"), ("Data essentials", BASE), ("The programme", url_path)], QA)


def main():
    DE.write(*programme_page())
    DE.write(*DE.hub_page())


if __name__ == "__main__":
    main()
