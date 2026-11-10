"""Downstreams: block 3 of Data systems, at /learn/data-systems/downstreams/ (built by data_systems.py main()).

Same template as Upstreams: promise, a box for leaders, plain words, sections, one question table
(question, why we ask, what breaks in production, do this / not this), a consumer register checklist,
decisions with verdicts, FAQ. Agreed split (10 Nov 2026): Data systems = the whole and its edges
(upstreams in, downstreams out); Data platform = inside; Data Engineering = the role.
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("data_systems_for_down", ROOT / "_guides" / "data_systems.py")
ds = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ds)
E, wb, SITE, BASE = ds.E, ds.wb, ds.SITE, ds.BASE
D = f"{BASE}downstreams/"


def tbl(head, rows):
    h = "".join(f"<th>{E(x)}</th>" for x in head)
    b = "".join("<tr>" + "".join(f"<td>{'<b>' + E(c) + '</b>' if i == 0 else E(c)}</td>" for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="tw"><table class="t"><tr>{h}</tr>{b}</table></div>'


def picture():
    box, arrow, text, svg, FILL = ds.box, ds.arrow, ds.text, ds.svg, ds.FILL
    b = box(20, 110, 190, 110, "Data platform", "gold tables and the\nsemantic layer", "gold")
    doors = [("Semantic layer", "one meaning\nper metric", "mint", 20), ("SQL and APIs", "queries, lookups,\nserving", "sky", 128), ("Push out", "reverse ETL, sharing,\nevents, files", "lilac", 236)]
    for t, s, f, y in doors:
        b += box(290, y, 190, 90, t, s, f)
        b += arrow(212, 165, 288, y + 45)
    users = [("BI dashboards", "reports, KPIs"), ("Analysts, Genie", "ad-hoc questions"), ("AI agents", "tools over certified data"),
             ("ML", "features, training"), ("Apps", "lookups, recommendations"), ("SaaS tools", "CRM, marketing"), ("Partners, regulators", "shares, filings")]
    for i, (t, s) in enumerate(users):
        y = 10 + i * 50
        b += f'<rect x="600" y="{y}" width="230" height="42" rx="10" fill="#fff" stroke="#1F1F1F" stroke-width="1.3"/>'
        b += text(715, y + 18, t, 15, fill="#1F1F1F") + text(715, y + 34, s, 11)
    b += arrow(482, 65, 598, 55) + arrow(482, 173, 598, 180) + arrow(482, 281, 598, 300)
    b += text(425, 362, "every consumer is named, with an owner, a need and a way in", 14, fill="#1F1F1F")
    return svg(850, 375, b, "The data platform serves consumers through three doors: the semantic layer, SQL and APIs, and pushing data out. Consumers are BI, analysts and Genie, AI agents, ML, apps, SaaS tools, and partners and regulators."), \
        "Three doors out of the platform, and the consumers behind them."


KINDS = [
    ("BI dashboards and reports", "Sales, finance, operations dashboards", "The same number every time; clear freshness", "Semantic layer or metric views; scheduled refresh", "A metric defined inside a dashboard disagrees with another dashboard"),
    ("Ad-hoc analysts and Genie", "Analysts in SQL; business users asking in plain words", "Findable, documented, certified tables and metrics", "SQL warehouse; Genie over metric views", "Questions answered from the wrong table, with confidence"),
    ("AI agents and assistants", "Support agents, copilots, internal assistants", "Certified data through typed tools; documents for retrieval", "Tools over metric views and ops tables; vector search", "An agent writes its own SQL and returns a plausible wrong answer"),
    ("ML training and features", "Churn, fraud, demand models", "History as it was at the time; the same features in training and serving", "Feature tables; point-in-time joins; online tables", "A model trained on values that weren't known yet works in testing and fails live"),
    ("Operational apps", "Customer 360 lookups, recommendations in an app", "Millisecond reads, always on", "An API over a serving database or online table", "A dashboard warehouse kept on 24x7 to answer app lookups"),
    ("SaaS tools (reverse ETL)", "Scores into the CRM, audiences into marketing tools", "Fresh, correct records written to another system", "Reverse ETL", "A bad load overwrites thousands of CRM records"),
    ("Partners and other teams", "Suppliers, group companies, data products for other domains", "Governed access without copies", "Delta Sharing or a marketplace listing", "Emailed extracts that nobody can revoke"),
    ("Regulators and finance close", "Statutory filings, month-end close", "Numbers that reconcile and can be reproduced later", "Reconciled gold, snapshots, sign-off", "A filed number can't be reproduced a year later"),
]

DOORS = [
    ("Semantic layer (metric views)", "Pull", "Every metric defined once, used by BI, Genie and agents alike", "Needs owners for definitions; not for row-level exports"),
    ("SQL warehouse, direct", "Pull", "Analysts and tools that need tables", "Without the semantic layer, metric logic spreads into every query"),
    ("BI import or extract", "Pull, copied", "Fast dashboards on modest data", "A second copy with its own freshness; refresh schedules wake warehouses"),
    ("API or serving table", "Pull, low latency", "Apps and agents needing single records fast", "Always-on cost; design for the night-time load"),
    ("Reverse ETL", "Push", "Getting data into the tools people work in", "Writes into someone else's system: test, limit and log every write"),
    ("Sharing (Delta Sharing, marketplace)", "Push, no copy", "Partners and other platforms", "Who pays for the reads; revoking access"),
    ("Events out", "Push", "Other systems reacting to changes in seconds", "Ordering, duplicates, schema changes in messages"),
    ("File exports", "Push, copied", "Legacy and regulatory recipients", "Copies that live forever; hard to revoke"),
]

REGISTER = [
    ("Consumer", "The dashboard, app, model, agent or partner", "Finance revenue dashboard"),
    ("Owner", "The person who answers for it", "Head of FP&A"),
    ("Decision it supports", "What someone does with it", "Weekly forecast review"),
    ("Data it uses", "Gold tables and metrics, by name", "sales_metrics.net_revenue"),
    ("Freshness needed", "How old the data may be, and by when", "By 07:00, yesterday complete"),
    ("Criticality", "What happens if it is wrong or late", "Tier 1: board reporting"),
    ("Access rules", "Who may see which rows and columns", "Region managers see their region"),
    ("Way in", "Which door it uses", "Metric views via BI"),
    ("Change notice", "How much warning it needs before a change", "Two weeks"),
    ("Contact for incidents", "Who we tell when something is wrong", "fpa-oncall"),
]

DQ = [
    ("A", "Who consumes", "every consumer named, with an owner", [
        ("Which dashboards, reports, apps, models, agents, tools and partners use the data, and who owns each?",
         "We can't protect consumers we don't know about.",
         "A column change breaks a finance report nobody knew existed, on the day of the close.",
         "A consumer register, kept current from query history and lineage. Not: finding consumers through complaints."),
        ("What decision does each consumer support, and what happens if it is wrong or late?",
         "Criticality decides service levels, testing and who gets woken up.",
         "Every dashboard is treated the same; the board pack fails while effort goes to a dashboard nobody reads.",
         "Give each consumer a tier (for example 1 to 3) with matching freshness, testing and support. Not: one service level for everything."),
    ]),
    ("B", "What they need", "freshness, grain, history, completeness", [
        ("How fresh must the data be for each consumer, and by what time?",
         "Freshness is a promise to a person, and it sets the whole chain upstream.",
         "Streaming built for a report read once a week, or a daily load for a decision made hourly.",
         "Write the freshness need per consumer, then design the hops backwards from it. Not: one schedule for all."),
        ("At what level of detail do they need it: per transaction, per day, per customer?",
         "Grain decides gold table design and cost.",
         "A dashboard scans billions of rows to show a daily total.",
         "Agree the grain per use; build aggregates for the common ones. Not: raw facts for every dashboard."),
        ("Do they need history as it was (last year's region), or only as it is now?",
         "This decides Type 2 history and as-of joins upstream.",
         "Last year's numbers move whenever reference data changes.",
         "Name the reports that need as-of history and keep it for the columns they group by. Not: deciding after go-live."),
        ("Must they see complete periods only, or partial data as it arrives?",
         "Partial data looks like a drop in the business.",
         "This morning's half-loaded day shows sales down 60% and a manager escalates.",
         "Publish complete periods to most consumers; label partial data clearly where it is shown. Not: showing whatever has landed."),
    ]),
    ("C", "Meaning and definitions", "one meaning per number", [
        ("Which metrics do they use, who owns each definition, and are there competing versions today?",
         "Two definitions of revenue in two tools is the most common data argument.",
         "Two dashboards show two revenues in one meeting and both teams stop trusting the data.",
         "Each metric defined once in the semantic layer, with a named owner. Not: logic in each dashboard."),
        ("Is business logic hidden in today's reports, spreadsheets or BI models?",
         "Migrations break when that logic is left behind.",
         "The new dashboard is 'correct' but doesn't match the old one, because the old one excluded test orders.",
         "Harvest the logic from current reports and move it into the semantic layer or gold. Not: rebuilding visuals only."),
    ]),
    ("D", "Access and security", "who may see what, inside and outside", [
        ("Who may see which rows and columns: by region, by role, with or without personal data?",
         "Access rules belong in the platform, not in each tool.",
         "A filter in a dashboard is the only thing stopping a region manager seeing every region.",
         "Row filters and column masks in Unity Catalog, applied to every door. Not: security inside the BI tool only."),
        ("Does any data leave the organisation: partners, regulators, vendors, AI services?",
         "External use has legal and contractual limits.",
         "Customer data is sent to an outside AI service without anyone checking the contract.",
         "Approve every external flow, prefer sharing without copies, log what leaves. Not: ad-hoc exports."),
    ]),
    ("E", "How they read", "the door each consumer uses", [
        ("Through which door does each consumer read: semantic layer, SQL, BI extract, API, reverse ETL, sharing, events, files?",
         "The door decides cost, freshness and where logic lives.",
         "Every team picks its own way in, and metric logic is copied into each.",
         "Default to the semantic layer; other doors on purpose, recorded in the register. Not: direct table access by default."),
        ("How many people query at once, when, and how heavy are the queries?",
         "This sizes warehouses and decides how long they stay on.",
         "A warehouse sized for Monday 9 a.m. runs all week, or Monday's queries queue for minutes.",
         "Size from peak concurrency and use auto-scaling; schedule refreshes for when people read. Not: one large warehouse always on."),
        ("Does anything need answers in milliseconds, or around the clock?",
         "Low-latency, always-on serving is a different design from dashboards.",
         "An app's lookups keep the BI warehouse awake all night.",
         "A serving table or database for lookups, sized for night-time load. Not: the dashboard warehouse."),
    ]),
    ("F", "AI and agents", "certified data through tools", [
        ("Which questions should agents and Genie answer, and from which certified tables and metrics?",
         "AI answers are only as right as the data it is allowed to use.",
         "Genie answers from a staging table and gives a confident wrong number to an executive.",
         "Agents call typed tools over metric views and certified tables; Genie spaces over metric views only. Not: agents writing raw SQL on everything."),
        ("Which documents do assistants need, who owns them, and how are they kept current?",
         "Retrieval is only as current as its documents.",
         "An assistant quotes last year's policy.",
         "A document register with owners and refresh rules, like the consumer register. Not: a folder uploaded once."),
        ("How will we test AI answers, and what does each question cost?",
         "AI consumers need evaluation and a cost budget like any other.",
         "Quality drifts unnoticed and token costs double in a month.",
         "A set of known questions with expected answers, run on every change; cost per question tracked. Not: trying a few questions by hand."),
    ]),
    ("G", "ML", "features and training data", [
        ("Do models need features exactly as they were at prediction time, and the same in training and serving?",
         "Leakage and skew make models look good and fail live.",
         "A churn model uses a field filled in after the customer left; it is perfect in testing and useless in production.",
         "Point-in-time joins for training; one feature definition shared by training and serving. Not: features rebuilt separately for each."),
        ("How often do models retrain, and on how much history?",
         "Retraining cadence drives history retention and compute.",
         "History needed for retraining was cleaned up to save storage.",
         "Agree retention with the model owners. Not: retention set only by storage cost."),
    ]),
    ("H", "Change and contracts", "consumers are told before things change", [
        ("How do consumers hear about changes, and how much notice do they need?",
         "Most breakages are changes nobody announced.",
         "A renamed column breaks three dashboards and an agent tool overnight.",
         "Outbound contracts for published tables and metrics; change notice from the register; lineage to find who is affected. Not: changes discovered in production."),
        ("How are tables and metrics retired?",
         "Unused things cost money and confuse people; used things can't simply vanish.",
         "A table 'nobody uses' is dropped and the finance close fails.",
         "Check usage in query history, mark as deprecated, keep a view for a period, then remove. Not: deleting on a hunch."),
    ]),
    ("I", "Trust and support", "consumers know when to trust a number", [
        ("How does a consumer know whether today's data is complete and checked?",
         "Trust depends on seeing freshness and quality, not on promises.",
         "People keep their own spreadsheets because they can't tell when the dashboard is right.",
         "Show freshness and a quality status beside each dashboard and metric; mark certified data. Not: silent dashboards."),
        ("Who do consumers call when a number looks wrong, and how fast is the answer?",
         "Unanswered questions turn into lost trust.",
         "A wrong number circulates for a week before anyone on the data team hears.",
         "A named channel, an incident process and a note to affected consumers from the register. Not: personal messages to whoever built it."),
    ]),
    ("J", "Usage and cost", "who uses what, and what it costs", [
        ("Which dashboards, tables and metrics are actually used, by whom and how often?",
         "Usage tells you what to protect and what to retire.",
         "Hundreds of dashboards are refreshed every hour; a dozen are read.",
         "Usage from query and BI audit logs, reviewed quarterly. Not: keeping everything forever."),
        ("What does each consumer cost, and who pays?",
         "Warehouses, refreshes, serving and AI tokens are consumer-driven costs.",
         "One team's 15-minute refreshes double the warehouse bill.",
         "Tag consumer workloads and show cost per consumer. Not: one shared bill. See the cost calculator's hop 5."),
    ]),
]

DECISIONS = [
    ("What is the default way in for consumers?", [
        ("The semantic layer (metric views), with certified gold behind it", "pursue", "Pursue. One meaning per number for BI, Genie and agents."),
        ("Direct access to gold tables", "when", "Pursue for analysts and ML who need rows, with the register recording it."),
        ("Each tool defines its own metrics", "drop", "Drop. Guaranteed disagreement."),
    ]),
    ("How do AI agents reach data?", [
        ("Typed tools over metric views and certified tables", "pursue", "Pursue. Answers are checkable and permissions are enforced."),
        ("The model writes SQL against any table", "drop", "Drop. Plausible wrong answers, and access you can't reason about."),
    ]),
    ("How does data reach partners?", [
        ("Sharing without copies (Delta Sharing, marketplace)", "pursue", "Pursue. Governed, revocable, always current."),
        ("File exports", "when", "Pursue only when the recipient can't read a share; log and expire them."),
        ("Emailed extracts", "drop", "Drop. Uncontrolled copies."),
    ]),
    ("How do apps get fast lookups?", [
        ("A serving table or database sized for the lookups", "pursue", "Pursue. Milliseconds, without waking the dashboard warehouse."),
        ("The BI warehouse kept on 24x7", "drop", "Drop. Expensive, and still slow for single-record reads."),
    ]),
]

FAQ = [
    ("What are downstream consumers in a data platform?",
     "Everything that uses the data after the platform: dashboards and reports, analysts and Genie, AI agents, ML models, operational apps, SaaS tools fed by reverse ETL, partners through data sharing, and regulators."),
    ("Why keep a register of data consumers?",
     "So every consumer has an owner, a freshness need, a criticality tier and a contact. Then a change upstream can be traced to who it affects, service levels match importance, and unused things can be retired safely."),
    ("How should AI agents use enterprise data?",
     "Through typed tools over certified tables and metric definitions, not by writing their own SQL. Genie spaces should sit over metric views. Answers are then consistent with dashboards and permissions are enforced."),
]

LEADERS = [
    "Downstreams are where data earns its keep: dashboards, analysts, AI agents, ML models, apps, the tools people work in, partners and regulators.",
    "Each consumer needs something different: freshness, detail, history, speed, access. Writing those needs down first is what sizes and shapes the platform.",
    "One door by default: the semantic layer, where every metric is defined once, so dashboards, Genie and agents give the same answer.",
    "Every consumer is named in a register with an owner, a tier and a contact, so a change upstream can be traced to who it hurts.",
    "AI agents are consumers like any other: certified data through tools, tested answers, a cost per question.",
]


def page():
    p_svg, p_cap = picture()
    qt, n_q = ds.q_table(DQ)
    lead = "".join(f"<li>{E(x)}</li>" for x in LEADERS)
    faq = "".join(f'<details class="faq"><summary>{E(a)}</summary><p>{E(b)}</p></details>' for a, b in FAQ)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › <a href="{BASE}">Data systems</a> › Downstreams</p>
<p class="eyebrow" style="margin-top:22px">Data systems · block 3 of 3 · for data leaders, then builders</p>
<h1>Downstreams: know your consumers</h1>
<p class="promise">Every consumer is named, gets the data it needs through the right door, and hears about changes first.</p>
<p class="lede">Who uses the data after the platform, what each of them needs, the doors they come in by, and the questions to ask every consumer, each with the reason and what breaks in production when nobody asks.</p>
<div class="leaders"><h3>For leaders</h3><ul>{lead}</ul></div>
<nav class="toc"><b>On this page</b><ol>
<li><a href="#plain">In plain words</a></li><li><a href="#kinds">Kinds of consumers</a></li><li><a href="#doors">The doors out</a></li>
<li><a href="#register">The consumer register</a></li><li><a href="#questions">The question list ({n_q})</a></li><li><a href="#decisions">Design decisions</a></li>
<li><a href="#faq">Questions people ask</a></li><li><a href="#next">Where to go next</a></li></ol></nav>

<section id="plain"><p class="eyebrow">In plain words</p><h2>Different taps need different water</h2>
<p>A water company serves a hospital, a factory, homes and gardens. The hospital needs it clean and never interrupted. The factory needs pressure at 6 a.m. The garden doesn't mind a cut. A good company knows each customer, what they need, which pipe they're on, and calls them before maintenance. A data platform serves its consumers the same way.</p>
<figure class="diagram">{p_svg}<figcaption>{E(p_cap)}</figcaption></figure></section>

<section id="kinds"><p class="eyebrow">Kinds of consumers</p><h2>Eight kinds of consumers</h2>{tbl(["Kind", "Examples", "What they need most", "How they usually read", "What goes wrong"], KINDS)}</section>

<section id="doors"><p class="eyebrow">Integration patterns, outbound</p><h2>The doors out of the platform</h2>
<p>Upstreams can push, be pulled or share; downstreams are the same in reverse. Most consumers should come in through the semantic layer; every other door is chosen on purpose and recorded.</p>
{tbl(["Door", "Push or pull", "Good for", "Watch for"], DOORS)}</section>

<section id="register"><p class="eyebrow">Per consumer</p><h2>The consumer register: what we record for each</h2>
<p>The downstream twin of the upstream source questionnaire. It lives in the platform's metadata, kept current from query history and lineage, and it is how a change upstream is traced to the people it affects.</p>
{tbl(["Field", "What it is", "Example"], REGISTER)}</section>

<section id="questions"><p class="eyebrow">The question list</p><h2>Every question, why we ask, and what breaks if nobody does</h2>
<p>Ask it for each consumer, or each group of similar consumers. Answers go in the consumer register, the semantic layer and the outbound contracts.</p>{qt}</section>

<section id="decisions"><p class="eyebrow">Design decisions</p><h2>The decisions this block forces</h2>{ds.dec_html(DECISIONS)}</section>

<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{faq}</section>

<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2>
<p><b>The other edge:</b> <a href="{BASE}upstreams/">Upstreams: know your sources</a>.</p>
<p><b>Inside:</b> <a href="{BASE}platform/">The data platform, whole</a>; hop 4 (gold to semantic) and hop 5 (semantic to experiences) build what these consumers read.</p>
<p><b>Cost of serving consumers:</b> hop 5 in the <a href="{BASE}platform/cost/calculator/">Databricks cost calculator</a>.</p>
<p><b>Back up:</b> <a href="{BASE}">Data systems, end to end</a>.</p></section>"""
    title = "Downstreams: know your consumers"
    desc = f"Who uses a data platform's data and what each needs: BI, analysts and Genie, AI agents, ML, apps, reverse ETL, sharing and regulators; the doors out, a consumer register, and {n_q} questions with what breaks in production."
    url = f"{SITE}{D}"
    return wb.page(title, desc, url, body, ds.CSS + ds.ld(title, desc, url, [("Learn", "/learn/"), ("Data systems", BASE), ("Downstreams", D)], FAQ)), n_q


def main():
    out = ROOT / D.strip("/")
    out.mkdir(parents=True, exist_ok=True)
    html, n = page()
    (out / "index.html").write_text(html)
    print(f"downstreams -> {out} ({n} questions)")


if __name__ == "__main__":
    main()
