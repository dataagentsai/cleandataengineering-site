"""Responsible AI, explained in detail: one page at /learn/responsible-ai/.

    python3 _guides/responsible_ai.py      (then python3 _site/nav.py and python3 _site/seo.py)

Teach first (plain definition, food-safety analogy), then the eight principles with practices and proof,
the AI life cycle, risk tiers, frameworks and laws (with "check current status" flags), four public cases,
a one-page use-case review, the data-engineering side, mistakes with verdicts, FAQ.
Complements /learn/ai-governance/ (organisation-wide capabilities); this page is the plain, principle-by-principle view.
Public cases are summarised from widely reported sources; verify before quoting.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import de_essentials as DE  # noqa: E402

E, R, T, AR, S, table, fig, Lx, L, C = DE.E, DE.R, DE.T, DE.AR, DE.S, DE.table, DE.fig, DE.Lx, DE.L, DE.C
BLUE, MINT, BUTTER, ROSE, LAV, GREY = DE.BLUE, DE.MINT, DE.BUTTER, DE.ROSE, DE.LAV, DE.GREY
URL_PATH = "/learn/responsible-ai/"

# key, name, question, plain, goes wrong, do, proof, owner, data side
PRINCIPLES = [
    ("fairness", "Fairness", "Does it treat different groups of people fairly?",
     "AI learns from past data. If the past was unfair, or the data leaves some people out, the AI repeats that, at scale. Fair does not always mean identical results for everyone. It means you decided what fair means for this use, measured it, and can explain it.",
     "A recruiting tool trained on ten years of mostly male hires learns to prefer men. Nobody wrote that rule. The data taught it.",
     ["Name who could be harmed, before building.", "Check that the data includes them in fair proportion.", "Measure errors by group, not only overall accuracy.", "Agree a fairness threshold with the business and legal.", "Re-check after launch, because people and data change.", "Give people a way to challenge a result."],
     ["A fairness report by group, with the threshold and the result.", "A named sign-off.", "Monitoring that alerts when a gap opens."],
     "Product owner, data science, risk", "Profile the data by group; track missing groups; keep the label's origin."),
    ("transparency", "Transparency and explainability", "Can people tell when AI is involved, and understand why it decided?",
     "Two parts. Transparency: people know AI is being used, and what it can and cannot do. Explainability: for one decision, there are reasons a person can understand and act on, such as the main factors.",
     "A customer is refused a loan with no reason. Or a chatbot states a refund policy that does not exist, and the customer believes it.",
     ["Tell people when they are dealing with AI.", "Write a plain fact sheet for each system: purpose, data, limits.", "Give reasons or main factors for decisions about people.", "Keep a record that lets you rebuild why a decision was made.", "Say clearly what the system cannot do."],
     ["A user can find the explanation without asking an engineer.", "An auditor can reconstruct one decision from the logs."],
     "Product owner, legal", "Dataset documentation and lineage: where each input came from."),
    ("privacy", "Privacy and data protection", "Are we using personal data lawfully, minimally and safely?",
     "AI is hungry for data, but people keep rights over theirs. That means a lawful reason to use it, a stated purpose, no more data than needed, limited keeping, deletion on request, and nothing personal leaking out in an answer.",
     "Staff paste customer records into a public assistant. A model repeats a real person's details in an answer. Data is kept forever because nobody set a limit.",
     ["Classify data: which is personal or sensitive.", "Record the purpose and lawful basis for each use.", "Collect and send the minimum; mask or pseudonymise where you can.", "Set retention and test that deletion really works.", "Keep personal data out of prompts and logs unless needed.", "Run a privacy impact assessment for higher-risk uses."],
     ["A data map showing where personal data flows.", "A deletion test that passes.", "Access logs reviewed."],
     "Privacy officer, data engineering", "Classification tags, masking, retention and deletion pipelines, consent flags."),
    ("safety", "Safety and reliability", "Does it work as intended, including in unusual cases, and can we stop it?",
     "Working on the demo is not enough. It must hold up on rare cases and messy real data, fail safely, be watched after launch, and be stoppable. A person must be able to take over.",
     "A model gets worse quietly after the data changes. A chatbot gives unsafe advice. An agent takes an action nobody approved.",
     ["Write the intended use, and what is out of scope.", "Test on edge cases and realistic data, not only clean samples.", "Set quality thresholds before launch, not after.", "Design a safe fallback and a human takeover.", "Monitor for drift, errors and complaints.", "Have a kill switch and an incident process, and practise it."],
     ["Evaluation results against the thresholds.", "A rehearsed shutdown.", "An incident log with learning recorded."],
     "Engineering, product", "Data quality checks and drift monitors on the inputs."),
    ("security", "Security and robustness", "Can someone attack, trick or misuse it?",
     "AI adds new ways in on top of the usual ones. A hidden instruction in an email can steer an assistant (prompt injection). Bad training data can poison a model. Outputs can leak what they should not.",
     "An assistant reads a web page that contains a hidden instruction and sends private data to an attacker.",
     ["Threat-model the system, including the data and the tools it can call.", "Give it the least access it needs.", "Filter inputs and outputs where risk is high.", "Test with attackers' tricks before launch (red teaming).", "Check the models and datasets you bring in.", "Log what it did."],
     ["A red-team report with fixes.", "Tests showing known attacks are blocked.", "A list of what the system may access."],
     "Security, engineering", "Access control on training and retrieval data; checks for poisoned or injected content."),
    ("accountability", "Accountability and human oversight", "Who answers for it, and can a person step in?",
     "AI cannot be held responsible. People and organisations are. Each AI system needs a named owner. Where stakes are high, a person must review, with real power to disagree, not just click approve.",
     "'The system said so.' An automated risk-scoring system wrongly flagged many families for fraud and the harm was found late.",
     ["Keep a register of every AI system, each with a named owner.", "Match approval steps to risk (see the tiers below).", "Put a human review where decisions affect rights, money, health or work.", "Make sure the reviewer has time, information and authority to overrule.", "Give people an appeal route.", "Keep an audit trail."],
     ["The register, with owners.", "Decision logs.", "The rate at which reviewers overrule the AI (zero is a warning sign)."],
     "Executive sponsor, risk", "Ownership metadata and audit logs on data and models."),
    ("inclusiveness", "Inclusiveness and accessibility", "Does it work for everyone who needs to use it?",
     "Language, accent, disability, literacy, device and connection all change whether a system works for a person. A system that only works for some has quietly excluded the rest.",
     "A voice assistant fails on regional accents. A form works only in English. A chatbot cannot be used with a screen reader.",
     ["Involve affected people in design and testing.", "Test across languages, accents and abilities.", "Offer a non-AI route for anyone who needs it.", "Check accessibility standards."],
     ["Test results by user group.", "An accessibility check."],
     "Product, design", "Language and dialect coverage in the data."),
    ("impact", "Societal and environmental impact", "What does it do to work, society and the planet?",
     "Training and running large models uses energy and water. Automation changes jobs. Convincing fake content can mislead. Responsible teams look at these wider effects, not only the narrow task.",
     "A huge model is used for a task a small model or a simple rule would do better and cheaper. Staff learn about automation from a press release.",
     ["Use the smallest approach that works.", "Measure compute, cost and, where you can, energy.", "Assess effects on jobs and communities, and plan reskilling.", "Say honestly what AI can and cannot do, internally and externally."],
     ["An impact note.", "Cost and compute tracked per system."],
     "Sponsor, sustainability lead", "Compute and cost tracking per workload."),
]

LIFECYCLE = [("Idea", "Should we do this at all?"), ("Data", "Is it lawful and fair?"), ("Build", "Can we explain it?"), ("Test", "Is it fair and safe?"), ("Launch", "Who approved it?"), ("Run", "Are we watching?"), ("Retire", "Can we switch off?")]
LIFE_ROWS = [
    ("Idea", "Who could be harmed? Is AI the right tool? Which risk tier is this?", "Impact check; risk tier; named owner.", "Business owner, risk"),
    ("Data", "Do we have the right to use this data? Does it include everyone it affects? Is it documented?", "Data map; lawful basis; dataset fact sheet.", "Data owner, privacy"),
    ("Build", "Is the method one we can explain and test? Does it need personal data at all?", "Design note; model fact sheet.", "Engineering"),
    ("Test", "Does it meet quality, fairness, safety and security thresholds on realistic data?", "Evaluation report; red-team report.", "Engineering, security, risk"),
    ("Launch", "Who signed? What does the user see? Is there a human takeover and an appeal?", "Sign-off; user notice; runbook.", "Sponsor, product"),
    ("Run", "Are quality, drift, cost, incidents and complaints being watched, with alerts to a named person?", "Dashboard; incident log; regular review.", "Operations, owner"),
    ("Retire", "How is it switched off, data deleted and learning recorded?", "Decommission plan.", "Owner"),
]

TIERS = [("Unacceptable", "Banned. For example scoring people's social behaviour.", ROSE), ("High", "Hiring, credit, education, health, essential services. Strict duties.", BUTTER),
         ("Limited", "Chatbots and generated content. Tell people it is AI.", BLUE), ("Minimal", "Spam filters, simple recommendations. No special duty.", MINT)]

FRAMEWORKS = [
    ("NIST AI Risk Management Framework", "Voluntary guidance from the US standards body (version 1.0, January 2023), with a generative AI profile added in 2024.", "A clear structure: Govern, Map, Measure, Manage. Good for organising your own programme.", "Guidance, not law."),
    ("ISO/IEC 42001", "An international standard for an AI management system, published in 2023.", "A certifiable management system, like ISO 27001 is for security. Useful to show customers and auditors.", "You can be audited against it."),
    ("EU AI Act", "European law in force since 2024, with duties phased in over several years. It sorts AI by risk tier.", "Legal duties for high-risk systems and transparency duties for chatbots and generated content. Applies to anyone selling into the EU.", "Dates have been under review. Check the current timetable."),
    ("OECD AI Principles", "Five values-based principles adopted in 2019 and updated in 2024, used by many governments.", "The shared vocabulary behind many national policies.", "High level."),
    ("Data protection laws", "GDPR in Europe. In India, the Digital Personal Data Protection Act, 2023.", "Rules for lawful use, consent, purpose, retention and rights over personal data, which AI systems must follow.", "Rules and timetables are still being phased in. Check current status."),
    ("India, general guidance", "India has no single AI law at the time of writing; government bodies publish guidance and an AI mission.", "Follow sector rules (finance, health) and the data protection law, and watch for official AI guidance.", "Check MeitY and IndiaAI for the current position."),
]

CASES = [
    ("Recruiting tool that learned bias", "Widely reported in 2018: an experimental hiring tool at a large online retailer rated women's CVs lower, because it learned from years of mostly male hires. The company dropped it.", "Fairness; the data was the cause.", "Test results by group before any use; question the label, 'who was hired' is not 'who was good'."),
    ("Risk scores in courts", "A 2016 investigation of a US criminal risk-scoring tool found that Black defendants who did not reoffend were more often marked high risk than white defendants. The makers disputed the reading. The debate showed that fairness has more than one definition, and they cannot all be met at once.", "Fairness and transparency.", "Choose and document the fairness definition for your use, openly, with the people affected."),
    ("A chatbot that promised a refund", "In 2024 a Canadian tribunal held an airline responsible for wrong information its website chatbot gave a customer about fares. The airline argued the chatbot was separate. The tribunal disagreed.", "Accountability; transparency.", "You own what your AI says. Test answers on policies, and link answers to the source."),
    ("An automated benefits check", "In the Netherlands, an algorithmic fraud-risk system used in child benefit checks led to many families being wrongly accused and ordered to repay. The scandal contributed to the government's resignation in 2021.", "Accountability, oversight and fairness.", "Real human review with power to overrule, an appeal route, and early checks for who is being flagged."),
]

REVIEW = [("Purpose", "What is the AI for, in one sentence? What decision does it affect?"), ("People", "Who uses it? Who is affected by it, even if they never see it?"), ("Data", "What data does it use? Is any personal or sensitive? What is the lawful basis?"),
          ("Decision type", "Does it advise a person, or decide on its own?"), ("Risk tier", "Minimal, limited, high or unacceptable?"), ("The eight checks", "For each principle: the risk, the control, the owner, the evidence."),
          ("Human oversight", "Who reviews, when, with what power? What is the appeal route?"), ("Monitoring", "What is watched, who is alerted, and what stops it?"), ("Sign-off", "Named approver and date. Review date."), ]

TIER_RULES = [("Low", "No personal data, advises a person, easy to undo (for example summarising public documents).", "A short check and a named owner."),
              ("Medium", "Uses internal or personal data, or customers see the output.", "The full one-page review, tests, and monitoring."),
              ("High", "Affects someone's money, health, job, rights or safety.", "Full review, fairness and safety testing, human oversight with real authority, legal and privacy sign-off."),
              ("Stop", "Banned or you cannot explain, test or control it.", "Do not build it.")]

DATA_ROWS = [("Fairness", "Profile the data by group. Find who is missing. Document how labels were made.", "Group-level data profile"),
             ("Transparency", "Lineage from source to model input. A fact sheet for every dataset.", "Lineage graph, dataset fact sheet"),
             ("Privacy", "Classification tags, masking, retention rules, deletion that cascades to copies and backups.", "Deletion test that passes"),
             ("Safety", "Quality checks on every input feed. Drift monitors.", "Alerting data quality dashboard"),
             ("Security", "Access control on training and retrieval data. Checks for injected or poisoned content.", "Access review, ingest checks"),
             ("Accountability", "Owner metadata on every table and model. Audit logs.", "Owner on every dataset"),
             ("Inclusiveness", "Language and dialect coverage in the data.", "Coverage report"),
             ("Wider impact", "Compute and cost tracked per workload.", "Cost per system")]

MISTAKES = [("A values statement with no owners", "Nice words that nobody is accountable for.", "Drop"), ("Name an owner for every AI system", "Accountability is the difference between a principle and a practice.", "Pursue"),
            ("One review at launch only", "Data, users and models change. Risk changes with them.", "Drop"), ("Match the review to the risk tier", "Light for low risk, deep for high. Everyone's time is used well.", "Pursue"),
            ("Leave it to the data science team", "Many risks are legal, business or people questions.", "Drop"), ("A shared register of every AI system, including bought-in tools", "You cannot govern what you cannot see.", "Pursue"),
            ("'Human in the loop' as a rubber stamp", "If the reviewer cannot disagree, it is not oversight.", "Drop"), ("Measure more than accuracy", "Accuracy hides who is getting the errors.", "Pursue"),
            ("Ignore staff using public assistants", "Shadow AI is where personal data leaks. Give a safe, approved alternative.", "Drop"), ("Wait for the law before starting", "The practices are the same; start with the tiers.", "Drop")]

QA = [("What is Responsible AI?", "Building and using AI so that it is useful, and also fair, understandable, private, safe, secure, accountable and inclusive, with a named person answerable for the result."),
      ("Is Responsible AI the same as AI ethics?", "Ethics is the thinking about what is right. Responsible AI turns it into practice: owners, tests, controls and records, so you can show what you did."),
      ("Is Responsible AI the same as AI governance?", "Close, but not the same. Governance is the organisation-wide system of rules, roles and proof. Responsible AI is the set of qualities the system should have. Governance makes them real. See the AI governance guide for the organisation-wide view."),
      ("Does it slow teams down?", "Done by risk tier it does not. Low-risk uses get a short check. Only the few high-risk systems get a deep review, and finding a problem there is far cheaper than finding it in production."),
      ("Do small companies need it?", "Yes, in proportion. A one-page review, an owner and an inventory cost little, and protect against the same harms and the same customer questions."),
      ("Where do I start?", "Make a list of every AI system and tool in use, including bought ones. Name an owner for each. Tier them. Review the high tier first.")]


def d_principles():
    names = [("Fairness", "Fair to every group?"), ("Transparency", "Can people understand it?"), ("Privacy", "Is personal data used rightly?"), ("Safety", "Does it work? Can we stop it?"),
             ("Security", "Can it be attacked or tricked?"), ("Accountability", "Who answers? Can a person step in?"), ("Inclusiveness", "Does it work for everyone?"), ("Wider impact", "What does it do to work and planet?")]
    fills = [BUTTER, BLUE, ROSE, MINT, LAV, BUTTER, BLUE, MINT]
    b = R(20, 12, 960, 44, "#fff", ["Responsible AI: AI that works, and that you can defend"], 18, sw=2.5)
    for i, (n, q) in enumerate(names):
        x, y = 20 + (i % 4) * 245, 76 + (i // 4) * 120
        b += R(x, y, 225, 100, fills[i], [n, q], 18, href=f"#p-{PRINCIPLES[i][0]}")
    return S(1000, 330, b, "Eight principles of responsible AI: fairness, transparency, privacy, safety, security, accountability, inclusiveness and wider impact, each with the question it asks. Each box links to its section.")


def d_life():
    b = ""
    w, gap = 122, 20
    for i, (n, q) in enumerate(LIFECYCLE):
        x = 14 + i * (w + gap)
        b += R(x, 30, w, 80, [BLUE, GREY, BLUE, BUTTER, MINT, MINT, ROSE][i], [n, q], 16)
        if i < 6:
            b += AR(x + w + 1, 70, x + w + gap - 2, 70)
    b += '<path d="M780,112 C780,170 100,170 100,112" stroke="#111" stroke-width="1.5" fill="none" stroke-dasharray="5 4" marker-end="url(#dta)"/>' + T(440, 168, "what you learn while running goes back to the idea and the data", 14)
    return S(1000, 190, b, "The AI life cycle in seven stages: idea, data, build, test, launch, run, retire, each with the responsible question to ask. A loop returns from run to idea and data.")


def d_tiers():
    b = ""
    for i, (n, ex, f) in enumerate(TIERS):
        w = 300 + i * 190
        x = 500 - w / 2
        b += R(x, 14 + i * 74, w, 62, f, [n, ex], 17)
    b += T(500, 330, "match the care to the risk: more at the top, less at the bottom", 15)
    return S(1000, 346, b, "Four risk tiers drawn as a widening stack. Unacceptable: banned. High: strict duties, such as hiring or credit. Limited: tell people it is AI. Minimal: no special duty. Match the care to the risk.")


def d_fair():
    b = T(500, 24, "Same model, same overall accuracy, different errors by group", 17)
    b += T(120, 76, "Group A", 16, "end") + R(130, 54, 100, 34, BLUE, ["5% wrongly refused"], 13) + T(120, 136, "Group B", 16, "end") + R(130, 114, 300, 34, ROSE, ["15% wrongly refused"], 13)
    b += T(500, 190, "An average hides who is getting the errors. Measure by group.", 15)
    return S(1000, 210, b, "Two bars. Group A is wrongly refused five percent of the time and group B fifteen percent, although the overall accuracy is the same. Measure errors by group.")


def d_oversight():
    b = R(20, 50, 160, 70, GREY, ["A person's case"]) + AR(182, 85, 238, 85) + R(240, 50, 170, 70, BLUE, ["AI suggests", "and says why"]) + AR(412, 85, 468, 85)
    b += R(470, 50, 190, 70, BUTTER, ["A person decides", "can overrule"], 16, sw=2.5) + AR(662, 85, 718, 85) + R(720, 50, 260, 70, MINT, ["Outcome, with reasons", "and a way to appeal"])
    b += R(20, 150, 960, 40, LAV, ["every step is logged, and a stop button works"], 15)
    return S(1000, 210, b, "Human oversight: a person's case goes to the AI, which suggests an outcome and says why. A person decides and can overrule. The outcome comes with reasons and a way to appeal. Every step is logged and there is a stop button.")


def d_privacy():
    b = R(20, 40, 180, 70, GREY, ["Person's data", "with a lawful basis"]) + AR(202, 75, 258, 75) + R(260, 40, 200, 70, BLUE, ["Used for the stated", "purpose only"]) + AR(462, 75, 518, 75)
    b += R(520, 40, 200, 70, BUTTER, ["Kept for a limited", "time"]) + AR(722, 75, 778, 75) + R(780, 40, 200, 70, MINT, ["Deleted on request,", "everywhere"])
    b += R(260, 140, 460, 50, ROSE, ["Not: pasted into a public assistant"], 16, dash=True)
    return S(1000, 210, b, "The path of personal data: collected with a lawful basis, used only for the stated purpose, kept for a limited time, deleted on request everywhere. Not pasted into a public assistant.")


EXTRA = {"fairness": d_fair, "privacy": d_privacy, "accountability": d_oversight}
EXTRA_CAP = {"fairness": "Overall accuracy can look fine while one group takes most of the errors.", "privacy": "Each step needs an owner and a test. Deletion is the one most often missing.", "accountability": "Oversight only counts if the person can overrule."}


def principle_html():
    out = ""
    for key, name, q, plain, wrong, do, proof, owner, data in PRINCIPLES:
        ul = lambda xs: "<ul>" + "".join(f"<li>{E(x)}</li>" for x in xs) + "</ul>"
        out += (f'<div class="sess" id="p-{key}"><h3>{E(name)}</h3><dl><dt>The question</dt><dd><b>{E(q)}</b></dd><dt>In plain words</dt><dd>{E(plain)}</dd>'
                f'<dt>How it goes wrong</dt><dd>{E(wrong)}</dd><dt>What to do</dt><dd>{ul(do)}</dd><dt>How you know</dt><dd>{ul(proof)}</dd>'
                f'<dt>Who owns it</dt><dd>{E(owner)}</dd><dt>Data side</dt><dd>{E(data)}</dd></dl></div>')
        if key in EXTRA:
            out += fig(EXTRA[key](), EXTRA_CAP[key])
    return out


def page():
    life = table(["Stage", "Responsible question", "Evidence you keep", "Who"], [[f"<b>{E(a)}</b>", E(b), E(c), E(d)] for a, b, c, d in LIFE_ROWS])
    fw = table(["Framework or law", "What it is", "What it gives you", "Caution"], [[f"<b>{E(a)}</b>", E(b), E(c), E(d)] for a, b, c, d in FRAMEWORKS])
    cases = "".join(f'<div class="sess"><h3>{E(a)}</h3><dl><dt>What happened</dt><dd>{E(b)}</dd><dt>Principle</dt><dd>{E(c)}</dd><dt>The lesson</dt><dd>{E(d)}</dd></dl></div>' for a, b, c, d in CASES)
    rev = table(["Field", "Ask"], [[f"<b>{E(a)}</b>", E(b)] for a, b in REVIEW])
    tr = table(["Tier", "Looks like", "What it needs"], [[f"<b>{E(a)}</b>", E(b), E(c)] for a, b, c in TIER_RULES])
    dt = table(["Principle", "What data engineering does", "Evidence"], [[f"<b>{E(a)}</b>", E(b), E(c)] for a, b, c in DATA_ROWS])
    mv = table(["Practice", "Why", "Verdict"], [[f"<b>{E(a)}</b>", E(b), f"<b>{c}</b>"] for a, b, c in MISTAKES])
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › Responsible AI</p>
<p class="eyebrow" style="margin-top:22px">Learn · AI · free guide</p>
<h1>Responsible AI, explained</h1>
<p class="lede">Responsible AI means building and using AI so that it is useful, and also fair, understandable, private, safe, secure and accountable, with a named person answerable for the result. This page explains the idea from zero, then goes into detail: eight principles, the life cycle, risk tiers, laws and standards, four real cases, a one-page review you can copy, and the part data engineering plays.</p>
<div class="tf">
<nav class="toc"><b>On this page</b><ol><li><a href="#what">What it is</a></li><li><a href="#eight">The eight principles</a></li><li><a href="#detail">Each principle in detail</a></li><li><a href="#life">The AI life cycle</a></li><li><a href="#tiers">Risk tiers</a></li><li><a href="#laws">Frameworks and laws</a></li><li><a href="#cases">Four real cases</a></li><li><a href="#review">A one-page review</a></li><li><a href="#data">The data engineering side</a></li><li><a href="#mistakes">Mistakes and verdicts</a></li><li><a href="#faq">FAQ</a></li></ol></nav>
<section id="what"><p class="eyebrow">Teach first</p><h2>What Responsible AI is, in plain words</h2>
<p>Think of a restaurant kitchen. A tasty dish is not enough. Is the food safe? Is it labelled for allergies? Does every diner get the same care? Can you trace where an ingredient came from? Who is answerable if someone gets sick? Food safety is the discipline that answers those questions, so people can trust the kitchen.</p>
<p>Responsible AI is the same discipline for AI. 'Does it work?' is the first question. It is never the last.</p>
<div class="box"><b>In one line:</b> Responsible AI is AI that works, and that you can defend: to the people it affects, to your customers, to a regulator and to yourself.</div>
<h3>Why it matters</h3>
<ol><li><b>People get hurt.</b> AI makes decisions about jobs, loans, care and safety, at a scale no person could.</li><li><b>The law is arriving.</b> Data protection rules apply today. New AI laws add duties by risk tier.</li><li><b>Trust is the business.</b> One wrong, unexplained decision can cost more than a hundred good ones earn.</li></ol></section>
<section id="eight"><p class="eyebrow">The picture</p><h2>Eight principles</h2>
<p>Different organisations list five, six or ten principles. These eight cover what most lists contain. Click a box to jump to its detail.</p>
{fig(d_principles(), "Eight questions to ask of every AI system.")}</section>
<section id="detail"><p class="eyebrow">In detail</p><h2>Each principle: the question, what goes wrong, what to do</h2>{principle_html()}</section>
<section id="life"><p class="eyebrow">When to do it</p><h2>Responsible AI is not a step at the end</h2>
<p>It runs through the whole life of an AI system. The cheapest time to find a problem is at the start.</p>
{fig(d_life(), "Seven stages, one responsible question at each.")}{life}</section>
<section id="tiers"><p class="eyebrow">How much care</p><h2>Match the care to the risk</h2>
<p>Treating every AI use the same way wastes effort on trivial uses and under-protects serious ones. Sort each use into a tier and give it the matching care. The picture follows the tiers in the EU AI Act, which many organisations use as a model.</p>
{fig(d_tiers(), "Most uses are minimal or limited risk. A few are high, and those deserve the deepest review.")}{tr}</section>
<section id="laws"><p class="eyebrow">Rules and standards</p><h2>Frameworks and laws to know</h2>
<p>Rules change. The table gives the idea of each, and flags where you should check the current position.</p>{fw}
<p class="note">Legal dates and details change, and nothing here is legal advice. Check the official source for your country and sector.</p></section>
<section id="cases"><p class="eyebrow">What goes wrong</p><h2>Four real cases</h2>
<p>These are widely reported public cases, summarised in a few lines. Check the original reporting before you quote them.</p>{cases}</section>
<section id="review"><p class="eyebrow">Do it</p><h2>A one-page review you can copy</h2>
<p>For any AI use, fill in one page. It takes minutes for a low-risk use, and an afternoon for a high-risk one.</p>{rev}
<h3 style="margin-top:20px">How deep to go</h3>{tr}</section>
<section id="data"><p class="eyebrow">For data teams</p><h2>The data engineering side</h2>
<p>Most of Responsible AI is decided in the data, long before a model runs. A data team does a large share of it, often without a label for it.</p>{dt}</section>
<section id="mistakes"><p class="eyebrow">Common mistakes</p><h2>What to do and what to drop</h2>{mv}</section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(QA)}</section>
<section id="next"><p class="eyebrow">Go further</p><h2>Related pages</h2><ul>
<li>{Lx('/learn/ai-governance/', 'AI governance: running AI you can trust (the organisation-wide view, eighteen capabilities)')}</li>
<li>{Lx('/learn/agent-guardrails/', 'Agent guardrails')}</li><li>{Lx('/learn/eval-harness/', 'Eval Harness: how to prove it works')}</li>
<li>{Lx('/concepts/lineage/', 'Key idea: lineage')}</li><li>{Lx('/concepts/data-quality/', 'Key idea: data quality')}</li><li>{Lx('/concepts/governance/', 'Key idea: governance')}</li></ul></section>
</div>"""
    title = "Responsible AI, explained"
    desc = ("What Responsible AI is, in plain words, and in detail: eight principles with practices and proof, the AI life cycle, risk tiers, "
            "frameworks and laws, four real cases, a one-page review, and what data engineering does.")
    return DE.page_shell(title, desc, URL_PATH, body, [("Learn", "/learn/"), ("Responsible AI", URL_PATH)], QA)


def main():
    DE.write(URL_PATH, page())


if __name__ == "__main__":
    main()
