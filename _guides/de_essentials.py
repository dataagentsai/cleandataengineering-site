"""Data project essentials for non-technical roles: roadmap hub + new pages at /how-we-work/data-essentials/.

    python3 _guides/de_essentials.py      (then python3 _site/nav.py and python3 _site/seo.py)

Audience: business analysts, project and delivery managers, product owners, testers, sponsors.
Agreed 23 Nov 2026: ONE hub page that is the roadmap (10 sessions in 3 parts, one concept each),
linking existing pages and a few new ones: seven layer pages from one template (LAYERS), stakeholders,
backlog and agile, fail fast. Pictures first, plain words, only what a non-technical role needs.
Reuses de_time.py CSS and fig helper. Every link is checked to exist at build time.
"""
import json
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "_paths"))
import components as C  # noqa: E402
import de_time as DT  # noqa: E402
from concepts import CARDS  # noqa: E402

wb = C.wb
SITE = wb.SITE
BASE = "/how-we-work/data-essentials/"
DATE = "2026-11-23"
BLUE, MINT, BUTTER, ROSE, LAV = DT.BLUE, DT.MINT, DT.BUTTER, DT.ROSE, DT.LAV
GREY = "#f1f1ee"
ARROW = DT.ARROW

CSS = DT.CSS + """<style>
  .tf .steps { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:10px; margin:14px 0; }
  .tf .steps a { text-decoration:none; color:inherit; border:var(--line); border-radius:var(--wob); padding:8px 12px; background:#fff; display:block; }
  .tf .steps a b { font-family:var(--hand); font-size:22px; display:block; line-height:1.1; } .tf .steps a span { font-size:13.5px; color:var(--muted); }
  .tf .steps a.p1 { background:var(--peri-wash, #eef3fb); } .tf .steps a.p2 { background:var(--butter-wash); } .tf .steps a.p3 { background:var(--mint-wash); }
  .tf .part { font-family:var(--hand); font-size:22px; margin:22px 0 4px; }
  .tf .sess { border:var(--line); border-radius:var(--wob); padding:10px 16px 6px; margin:12px 0; background:#fff; }
  .tf .sess h3 { margin:4px 0; } .tf .sess .n { font-family:var(--hand); font-size:26px; margin-right:8px; }
  .tf .sess dl { display:grid; grid-template-columns:130px 1fr; gap:4px 12px; margin:8px 0; font-size:15px; }
  .tf .sess dt { font-weight:700; } .tf .sess dd { margin:0; }
  .tf .tag { font-size:12px; font-weight:700; border:1.5px solid var(--ink); border-radius:999px; padding:0 8px; background:#fff; white-space:nowrap; }
  .tf .tag.new { background:var(--butter-wash); } .tf .tag.old { background:var(--mint-wash); }
  .tf .cards3 { display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:12px; margin:12px 0; }
  .tf .cards3 > div { border:var(--line); border-radius:var(--wob); padding:8px 14px; background:#fff; } .tf .cards3 h3 { margin:4px 0; font-size:19px; }
  .tf ol.rules li { margin:6px 0; }
  .tf .chips { display:flex; flex-wrap:wrap; gap:8px; margin:10px 0; } .tf .chips a { border:var(--line); border-radius:999px; padding:2px 12px; text-decoration:none; background:#fff; font-size:14.5px; }
  .tf .pn { display:flex; justify-content:space-between; gap:12px; margin:26px 0 6px; flex-wrap:wrap; } .tf .pn a { border:var(--line); border-radius:var(--wob); padding:6px 14px; text-decoration:none; background:#fff; }
  .tf td.c { text-align:center; }
  .tf .cards3 .n { font-family:var(--hand); font-size:24px; margin-right:8px; }
</style>"""


# ----------------------------------------------------------------------------- helpers
def exists(href):
    return (ROOT / href.split("#")[0].strip("/") / "index.html").exists()


def L(href, text):
    return f'<a href="{href}">{E(text)}</a>'


def Lx(href, text):
    """A link to an existing page; fails the build if the page is missing."""
    assert exists(href) or href.startswith(BASE), f"missing page {href}"
    return L(href, text)


def fig(svg, cap):
    return DT.fig(svg, cap)


def S(w, h, body, label):
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{E(label)}">{ARROW}{body}</svg>'


def R(x, y, w, h, fill, lines, size=15, dash=False, sw=1.5, href=None):
    da = ' stroke-dasharray="5 4"' if dash else ""
    d = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="#111" stroke-width="{sw}"{da}/>'
    if isinstance(lines, str):
        lines = [lines]
    top = y + h / 2 - (len(lines) - 1) * 10 + 5
    for i, t in enumerate(lines):
        d += f'<text x="{x + w / 2}" y="{top + i * 20}" text-anchor="middle" font-size="{size if i == 0 else size - 1.5}">{E(t)}</text>'
    return f'<a href="{href}">{d}</a>' if href else d


def T(x, y, t, size=15, anchor="middle"):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}">{E(t)}</text>'


def AR(x1, y1, x2, y2, dash=False):
    da = ' stroke-dasharray="5 4"' if dash else ""
    return f'<path d="M{x1},{y1} L{x2},{y2}" stroke="#111" stroke-width="1.5" fill="none"{da} marker-end="url(#dta)"/>'


def page_shell(title, desc, url_path, body, crumbs, faq=None):
    url = f"{SITE}{url_path}"
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u if u.startswith("/") else u} for i, (n, u) in enumerate(crumbs)]
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": title, "description": desc, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}]
    if faq:
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})
    head = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(title, desc, url, body, head)


def write(rel, html):
    out = ROOT / rel.strip("/")
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(html)
    print("wrote", out / "index.html")


def table(head, rows, widths=None):
    h = "".join(f"<th>{E(x)}</th>" for x in head)
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tw"><table class="t"><tr>{h}</tr>{b}</table></div>'


# ----------------------------------------------------------------------------- the layers (data for the 7 layer pages)
LAYER_NAMES = ["Sources", "Landing", "Clean", "Model", "Meaning", "People use it"]

LAYERS = [
    dict(slug="sources", n=1, name="Sources", session=4, tech="upstreams, source systems",
         lede="The apps, files and services where data is born. Other teams own them, and almost every production problem starts here.",
         water="The rivers and wells. A treatment plant can only do its job if the engineers know how each river behaves: when it floods, when it runs low, what it carries.",
         job="Data is created by systems we don't run: a sales app, an HR tool, partner files, a payments service. We don't change them. We learn how they behave, agree how the data will leave them, and then depend on them for years.",
         matters=[("Meaning", "What each field, code and status really means, and which person can explain it. A column called status with the value 7 means nothing until someone says what 7 is."),
                  ("How data changes", "How rows are added, edited, deleted and corrected. If old rows are overwritten and nothing says when, we cannot load only what changed, and we lose history."),
                  ("Access and hand-over", "Who gives access, by which door (we pull, they send, they share), and when. Security approvals and network changes take weeks, not days.")],
         fails=[("The meaning is guessed", "Numbers disagree with finance in the last week, when the business first looks.", "Nobody can name the person who understands the source.", "Weeks of rework late in the project."),
                ("Deletes and corrections are invisible", "Totals drift. History is wrong. Every night reloads everything, and the bill grows.", "The source owner says 'I don't know' to 'how do you delete a record?'", "A redesign of the loading, often after go-live."),
                ("Access arrives late", "The team waits with nothing to build on, so estimates slip.", "The access request was not sent in week one.", "Calendar time lost. Effort is not lost, time is.")],
         depends=["The source owner's time (they have their own priorities and a change calendar).", "Security and network approvals to reach the source.", "A test copy of the source that is not production.", "A promise to be told before the source changes."],
         ask=["Who owns this system, and who can explain its fields to us?", "How do rows change, and how do you delete or correct one?", "Is there a test copy, and how real is its data?", "Will you tell us before you change anything, and how?"],
         done="Every source has a named owner, a sample we have looked at, an agreed way to hand data over, and an access date.",
         deeper=[("/learn/data-systems/upstreams/", "Upstreams: the 70 questions to chase, and why"), ("/learn/data-systems/upstreams/questionnaire/", "The source system questionnaire (printable)"),
                 ("/learn/data-systems/upstreams/answers/", "Where the answers go"), ("/learn/where-data-engineering-time-goes/", "Where data engineering time really goes")],
         techlinks=[("/learn/data-systems/upstreams/apis/", "How APIs hand over data"), ("/learn/data-systems/upstreams/files/", "How files hand over data")]),
    dict(slug="landing", n=2, name="Landing", session=5, tech="ingestion, bronze",
         lede="Getting the data in, exactly as it arrived, and keeping a copy we never change.",
         water="The intake pumps and the holding reservoir. The water is not clean yet. The point is to catch all of it, safely, and keep it so we can always start again.",
         job="A scheduled job (or a stream of events) copies data from each source into our platform. We keep the raw copy untouched, stamped with when it arrived. If anything later goes wrong, we fix the rules and replay from here instead of asking the source again.",
         matters=[("Completeness", "Did every row arrive, exactly once? The simplest check is the most valuable: the count in the source equals the count we landed."),
                  ("Safe to rerun", "A job that failed at 2 a.m. must be safe to run again. Running it twice must not double the numbers."),
                  ("History and timing", "How far back do we load, how big is that first load, how long does it take, and does it fit inside the window the source allows?")],
         fails=[("Rows go missing quietly", "A late file or half-finished extract lands, and a report is low for a day before anyone notices.", "Nobody compares counts between source and landing.", "Trust. One wrong report costs more than ten right ones earn."),
                ("A rerun doubles the data", "Totals jump after a failed night was retried.", "The team says 'we just rerun it' without saying what that does.", "Wrong numbers in front of senior people."),
                ("The first big load hurts the source", "The source slows down during business hours, and its owners block the load.", "Nobody asked how long the history load takes, or when it may run.", "A blocked project and an unhappy source owner.")],
         depends=["Source access and a network path (from the Sources layer).", "An environment ready for the team: development, test, production.", "The source's own batch times, so we don't load while it is busy.", "An agreed schedule: how fresh the data must be."],
         ask=["How fresh must this data be, and what happens if it is late?", "How much history do we need, and how big is it?", "What happens when the source adds or renames a column?", "Who is told when a load fails, and how fast?"],
         done="Counts match the source for a sample period. Running the load twice gives the same result. A failure alerts a named person.",
         deeper=[("/learn/data-systems/upstreams/", "Upstreams: how data leaves a source"), ("/learn/medallion-architecture/", "Medallion architecture, in pictures")],
         techlinks=[("/learn/data-platform-architecture/ingestion/", "Hop 1: how ingestion is built"), ("/learn/real-time-analytics/", "Real-time analytics"), ("/learn/shift-left/", "Shift left: catch it before it runs")]),
    dict(slug="clean", n=3, name="Clean", session=5, tech="silver",
         lede="One clean, trusted row for every real thing: one customer, one order, one product.",
         water="The treatment plant. Dirt is taken out by steps that were agreed and written down, so you can say what was removed and why.",
         job="Raw data has duplicates, wrong types, odd spellings and missing values. This layer applies written rules: what counts as the same customer, what counts as invalid, what to do with a bad record. It also keeps history, so we can say what a value was last March.",
         matters=[("Identity", "What makes two records the same thing? Same email, same phone, same ID? This one decision shapes every customer count."),
                  ("Rules that are written down", "What is invalid, and who decides? Dropped, fixed, or set aside for a person to look at? Rules hidden in code cannot be reviewed by the business."),
                  ("History", "Do we need 'as it was then'? If a customer moves city, do last year's sales stay in the old city? Deciding late means a rebuild.")],
         fails=[("Duplicate or merged people", "Customer counts are inflated, or two real customers become one.", "Nobody can say which customer ID is the real one.", "Every customer metric is doubtful."),
                ("Bad rows disappear", "A rule silently drops rows and totals fall short.", "Rejected rows are not counted or reviewed by anyone.", "Missing money that nobody can find."),
                ("History needed too late", "Someone asks for last year's view and the data cannot give it.", "'Do we need history?' was never asked.", "A rebuild and a reload of years of data.")],
         depends=["Source owners, to explain what the values mean.", "Business data owners, to decide the rules.", "Reference data (country codes, product lists) from a trusted place.", "Landing being complete (the layer before)."],
         ask=["What makes one record the same as another?", "When a record breaks a rule, do we drop it, fix it, or park it for a person?", "Do you ever need to see yesterday's version of a value?", "Who looks at the rejected rows, and how often?"],
         done="The rules are written and each has an owner. Rejected rows are counted and reviewed. Spot checks agree with the source expert.",
         deeper=[("/concepts/data-quality/", "Key idea: data quality"), ("/concepts/scd/", "Key idea: keeping history (SCD)"), ("/learn/medallion-architecture/", "Medallion architecture, in pictures")],
         techlinks=[("/learn/data-platform-architecture/bronze-to-silver/", "Hop 2: how cleaning is built"), ("/learn/time-travel-vs-scd2/", "Time travel or SCD2 for history")]),
    dict(slug="model", n=4, name="Model", session=6, tech="gold",
         lede="Clean data arranged the way the business thinks: sales, customers, products, days.",
         water="The pipes laid to each neighbourhood. Same clean water, but shaped for the people it serves.",
         job="Here the data becomes tables that answer business questions: a table of sales, and tables describing the date, the product, the store and the customer. Calculations such as net revenue are done once, here, and every report reuses them.",
         matters=[("The grain", "One row per what? Per order line, per order, per day? This single choice decides which questions can be answered without a rebuild."),
                  ("Shared definitions", "What exactly is a customer, an active user, revenue? Net or gross, with or without returns? Each needs one answer."),
                  ("Reconciliation", "The totals must match a number the business already trusts, such as the finance report, within a tolerance everyone agreed.")],
         fails=[("The grain is wrong for the question", "A report needs detail the table does not have.", "Nobody asked 'one row per what?' in a requirements meeting.", "A rebuild of the model and every report on top."),
                ("Two definitions of one word", "Sales and finance each show 'revenue', and they differ.", "Two people give different answers to 'what is revenue?'", "Meetings spent arguing about whose number is right."),
                ("The totals do not tie out", "The new report differs from the finance report and nobody can say why.", "Reconciliation was planned for the last week.", "The business refuses to switch, and the project stalls.")],
         depends=["Business owners of each metric.", "Finance, for the figures to reconcile against.", "A stable Clean layer.", "The BA's requirements, written as questions the data must answer."],
         ask=["One row per what?", "Who owns the definition of each number?", "Which existing report must this match, and who signs off the match?", "Which questions will you ask next year that you don't ask today?"],
         done="Each metric has a name, a formula and an owner. Totals reconcile with a known report within the agreed tolerance. The sign-off is recorded.",
         deeper=[("/concepts/dimensional/", "Key idea: facts and dimensions"), ("/learn/gold-data-modelling/", "Gold data modelling")],
         techlinks=[("/learn/silver-to-gold/", "Silver to gold: the harness"), ("/learn/data-platform-architecture/gold/", "Hop 3: how the model is built")]),
    dict(slug="meaning", n=5, name="Meaning", session=6, tech="semantic layer, metric definitions",
         lede="Each number is defined once, in one place, so every report and every AI assistant gives the same answer.",
         water="The meter and the tariff. A litre means the same litre to everyone, and the bill follows one published rule.",
         job="The meaning layer holds the official definition of each metric and the ways it may be sliced (by region, by month). Dashboards, spreadsheets and AI assistants all ask it, instead of each one calculating revenue its own way. It also holds who may see which rows.",
         matters=[("One definition, one owner", "Each metric has a name, a formula in plain words, and a person who owns it."),
                  ("Who sees what", "A regional manager sees their region. Salary and personal data are protected. Access rules are tested with real roles, not assumed."),
                  ("Change with notice", "Changing a definition changes every report that uses it. It must be a controlled change with warning, not a quiet edit.")],
         fails=[("Every dashboard calculates its own", "Three dashboards show three different revenue figures.", "Metrics are defined inside reports, not in one place.", "Nobody trusts any of them."),
                ("The wrong person sees the data", "A manager sees another region's figures, or personal data leaks.", "Access rules were written but never tested with real roles.", "A compliance incident, not just a rework."),
                ("A definition changes silently", "A trend line breaks and nobody knows why.", "There is no change log or notice process for definitions.", "A week of investigation before anyone finds the cause.")],
         depends=["Metric owners, who must agree the definitions.", "Security and governance, for the access rules.", "The BI tool chosen by the business.", "A stable Model layer underneath."],
         ask=["Who owns each metric, and where is its definition written?", "Who may see which rows, and who approved it?", "How are people told when a definition changes?", "Will the AI assistant use the same definitions as the dashboards?"],
         done="A metric catalogue with an owner for each metric. Access rules tested with real user roles. A change process everyone knows.",
         deeper=[("/concepts/semantic-layer/", "Key idea: the semantic layer"), ("/learn/data-systems/downstreams/", "Downstreams: know your consumers")],
         techlinks=[("/learn/metric-views/", "Metric views, taught from zero"), ("/learn/power-bi-vs-databricks-ai-bi/", "Power BI and Databricks AI/BI")]),
    dict(slug="consumers", n=6, name="People use it", session=7, tech="BI, reports, apps, AI",
         lede="The dashboards, spreadsheets, apps and assistants where people actually use the numbers.",
         water="The taps. A hospital, a factory and a garden want different water at different pressure. A good company knows each customer before it lays the pipe.",
         job="This is where the project proves its worth, or doesn't. Each consumer is named, with what they need: how fresh, how detailed, who may see it. Their old reports are switched off on an agreed date, so there is one truth.",
         matters=[("Named consumers with needs", "A register of who uses the data, for which decision, how fresh, with an owner and a contact. Consumers found at go-live are the costliest."),
                  ("Trust at the point of use", "The report shows when the data was last updated and where the numbers come from. People can tell good from stale."),
                  ("Adoption and switch-off", "Success is people using it, and the old report being retired. Two parallel truths are worse than one imperfect one.")],
         fails=[("Built before anyone confirmed the question", "A polished dashboard that nobody opens.", "The first mock-up was shown at the end, not in week two.", "The whole build, wasted."),
                ("The old report keeps running", "Two reports, two numbers, and meetings about which to believe.", "No switch-off date was agreed with the owner of the old report.", "The new platform never gets trusted."),
                ("Too slow at real volume", "Fast on the sample, slow on a year of data.", "Nobody tested with production-sized data.", "A late redesign or a bigger bill.")],
         depends=["Business users' time for acceptance testing.", "BI licences and access for each user group.", "The Meaning layer being ready.", "Training, and a support route when something looks wrong."],
         ask=["Who uses this, and for which decision?", "How fresh must it be, and what happens if it is late?", "What do you use today, and on what date do we switch it off?", "Who will test it with numbers they recognise?"],
         done="Each report has an owner and real users. Acceptance testing used numbers the business recognises. The old report has a retirement date.",
         deeper=[("/learn/data-systems/downstreams/", "Downstreams: know your consumers"), ("/learn/power-bi-vs-databricks-ai-bi/", "Power BI or Databricks AI/BI"), ("/concepts/freshness/", "Key idea: freshness")],
         techlinks=[]),
    dict(slug="across", n=7, name="Across everything", session=8, tech="quality, security, cost, operations",
         lede="Four jobs that sit across every layer: quality, security, cost, and running the thing every day.",
         water="The lab that tests the water, the guards at the plant, the budget, and the night crew. None of them appear on the map of pipes, and the supply fails without them.",
         job="Quality is checking the data every day, not once. Security is who may see what, and protecting personal data. Cost is the cloud bill, which grows quietly. Running is the schedule, the alerts, and the person who answers at 2 a.m. These are planned from the first week, not added before go-live.",
         matters=[("An owner for each of the four", "Quality, security, cost and running each have a named person. A job with no owner does not get done."),
                  ("Planned in the backlog", "Each has stories, estimates and acceptance criteria, like any feature. If it is not in the backlog, it is not in the plan."),
                  ("Rehearsed before go-live", "A failure drill: something breaks on purpose, and operations fixes it with the runbook, without the builders.")],
         fails=[("Personal data found late", "Sensitive fields are in a test environment, or a report shows them to everyone.", "Nobody asked 'is any of this personal or regulated?' in discovery.", "A stop, a clean-up and sometimes a report to a regulator."),
                ("A surprise cloud bill", "The monthly cost is several times the estimate.", "Nobody owns the cost, and nothing alerts on a jump.", "Funding questions, then pressure to cut things that matter."),
                ("Nobody is on call", "A job fails on Sunday and the first to notice is an executive with a blank dashboard.", "The runbook is written by the builders and never rehearsed.", "The project's reputation, after go-live.")],
         depends=["Security, privacy and compliance teams.", "The cloud cost owner (often finance or a platform team).", "The operations or support team that will run it.", "Monitoring and alerting set up by the build team."],
         ask=["Is any of this data personal, confidential or regulated?", "What is the monthly budget, and who watches it?", "Who is alerted when a job fails, and what do they do?", "How will we show data quality every day, to the business?"],
         done="Four named owners. Quality checks run daily and are visible. A cost budget with an alert. A rehearsed failure drill.",
         deeper=[("/learn/data-systems/platform/", "The data platform: the 24 concerns that run across it"), ("/learn/data-systems/platform/cost/", "Cost and FinOps"), ("/concepts/data-quality/", "Key idea: data quality"), ("/concepts/governance/", "Key idea: governance")],
         techlinks=[("/learn/shift-left/", "Shift left: fail fast on data code"), ("/learn/databricks-permissions/", "Databricks permissions")]),
]


def d_strip(active, w=1000):
    """The six layers in a row, one highlighted, with who owns what below."""
    b = ""
    bw, gap, x0 = 136, 30, 24
    for i, name in enumerate(LAYER_NAMES):
        x = x0 + i * (bw + gap)
        on = (i + 1 == active)
        b += R(x, 20, bw, 56, BUTTER if on else "#fff", [name], 17, sw=3 if on else 1.5)
        if i < 5:
            b += AR(x + bw + 2, 48, x + bw + gap - 3, 48)
    b += f'<path d="M24,100 L{x0 + bw},100" stroke="#111" stroke-width="1.5" fill="none"/>' + T(24 + bw / 2, 120, "we don't own it", 14)
    b += f'<path d="M{x0 + bw + gap},100 L{x0 + 5 * (bw + gap) - gap + bw - bw - 0},100" stroke="#111" stroke-width="1.5" fill="none"/>'
    b += T((x0 + bw + gap + x0 + 4 * (bw + gap) + bw) / 2, 120, "we build it", 14)
    b += f'<path d="M{x0 + 5 * (bw + gap)},100 L{x0 + 5 * (bw + gap) + bw},100" stroke="#111" stroke-width="1.5" fill="none"/>' + T(x0 + 5 * (bw + gap) + bw / 2, 120, "they use it", 14)
    return S(w, 134, b, "The six layers of a data project in a row: sources, landing, clean, model, meaning, people use it. Sources are owned by other teams, the middle four are built by the project, and the last is where people use the data. One is highlighted as 'you are here'.")


def d_layer(slug):
    b = ""
    if slug == "sources":
        b += R(20, 30, 250, 56, GREY, ["App database", "sales, HR, orders"]) + R(20, 100, 250, 56, GREY, ["Files from a partner", "arrive daily"]) + R(20, 170, 250, 56, GREY, ["Cloud service (API)", "ask it, it answers"])
        b += f'<rect x="8" y="14" width="274" height="226" rx="14" fill="none" stroke="#111" stroke-dasharray="3 5"/>' + T(145, 258, "owned and changed by other teams", 14)
        b += R(660, 50, 320, 150, BLUE, ["Our platform", "needs all three doors agreed"])
        b += AR(272, 58, 658, 100) + T(430, 66, "we pull it", 14) + AR(272, 128, 658, 128) + T(430, 118, "they send it", 14) + AR(272, 198, 658, 158) + T(430, 190, "they share it", 14)
        b += R(300, 236, 440, 50, ROSE, ["What does 'status = 7' mean?", "Only the owner knows. Ask in week one."])
        return S(1000, 300, b, "Three kinds of source system owned by other teams: an app database, files from a partner, and a cloud service. Each hands data to our platform a different way: we pull it, they send it, or they share it. A question box asks what status equals seven means, and says only the owner knows."), "Three doors out of a source, and the question that matters most: what do the fields mean?"
    if slug == "landing":
        b += T(250, 24, "Did everything arrive?", 18) + T(760, 24, "Run it twice: same result?", 18)
        b += R(30, 50, 170, 70, GREY, ["Source", "100 rows"]) + AR(202, 85, 298, 85) + T(250, 76, "copy, untouched", 13) + R(300, 50, 170, 70, BLUE, ["Landing", "96 rows"])
        b += R(300, 150, 170, 54, ROSE, ["4 rows missing", "alert a person"]) + AR(385, 122, 385, 148)
        b += T(250, 250, "compare counts every time", 15)
        b += R(540, 50, 130, 56, GREY, ["Run 1", "adds 100 rows"]) + R(700, 50, 130, 56, GREY, ["Run 2 (retry)", "same 100 rows"])
        b += AR(605, 108, 700, 160) + AR(765, 108, 765, 150) + R(660, 152, 200, 60, MINT, ["Still 100 rows", "not 200"])
        b += R(880, 150, 100, 60, ROSE, ["200 rows", "wrong"], dash=True) + AR(830, 80, 930, 148, dash=True) + T(930, 230, "what we avoid", 13)
        b += T(760, 250, "a retry must be safe", 15)
        return S(1000, 270, b, "Two checks at the landing layer. First, the source has 100 rows but only 96 landed, so four are missing and a person is alerted. Second, running the load twice should leave 100 rows, not 200."), "Two cheap checks that catch most landing problems: counts match, and a retry changes nothing."
    if slug == "clean":
        for i, t in enumerate(["Jon Smith, Pune", "J. Smith, Pune", "SMITH JON, Pune"]):
            b += R(20, 24 + i * 66, 220, 50, ROSE, [t])
        b += AR(244, 50, 380, 100) + AR(244, 116, 380, 106) + AR(244, 182, 380, 112)
        b += R(384, 70, 250, 70, BUTTER, ["Agreed rule", "same name + same phone = same person"], 15)
        b += AR(636, 105, 730, 105) + R(734, 70, 250, 70, MINT, ["Customer 1042", "Jon Smith, Pune"])
        b += R(384, 190, 250, 60, LAV, ["Review pile", "rows that break a rule"]) + AR(509, 142, 509, 188, dash=True)
        b += T(734 + 125, 200, "the pile is counted and someone looks at it", 14) + AR(636, 220, 730, 212, dash=True)
        return S(1000, 270, b, "Three spellings of the same customer go through an agreed rule, same name and same phone number means the same person, and come out as one customer record. Rows that break a rule go to a review pile that a person checks."), "Clean means written rules. What is kept, what is merged, and what is parked for a person."
    if slug == "model":
        b += R(330, 90, 250, 80, BUTTER, ["Sales", "one row per order line"]) + R(40, 20, 170, 50, BLUE, ["Date"]) + R(700, 20, 170, 50, BLUE, ["Product"]) + R(40, 200, 170, 50, BLUE, ["Store"]) + R(700, 200, 170, 50, BLUE, ["Customer"])
        b += AR(212, 60, 328, 105) + AR(698, 60, 582, 105) + AR(212, 210, 328, 156) + AR(698, 210, 582, 156)
        b += R(40, 100, 250, 60, MINT, ["Can answer", "sales by day, product, store, person"], 14)
        b += R(620, 100, 260, 60, ROSE, ["If the row were 'one per day'", "you could not ask about one customer"], 14)
        return S(920, 270, b, "A sales table with one row per order line sits in the middle, linked to date, product, store and customer tables. A note says what it can answer, and warns that if the table held one row per day, a question about one customer could not be answered."), "The grain, one row per what, decides which questions are possible. Ask it first."
    if slug == "meaning":
        b += T(250, 24, "Without one definition", 18) + T(750, 24, "With one definition", 18)
        for i, v in enumerate(["1.2M", "1.4M", "1.1M"]):
            b += R(30 + i * 150, 50, 130, 70, ROSE, [f"Revenue {v}", f"dashboard {i + 1}"], 15)
        b += T(250, 150, "three dashboards, three answers", 15)
        b += R(560, 50, 360, 56, BUTTER, ["Revenue = paid orders minus returns", "owner: Finance"], 15)
        for i in range(3):
            x = 540 + i * 140
            b += AR(740, 108, x + 55, 170) + R(x, 172, 120, 56, MINT, ["Revenue 1.2M"], 15)
        b += T(750, 252, "every report asks the same place", 15)
        return S(1000, 270, b, "Left: three dashboards show three different revenue figures, 1.2 million, 1.4 million and 1.1 million. Right: one definition of revenue, paid orders minus returns, owned by Finance, feeds three dashboards that all show 1.2 million."), "Define each number once, with an owner. Every report and every assistant asks that one place."
    if slug == "consumers":
        b += R(20, 100, 220, 70, BUTTER, ["One agreed door", "the Meaning layer"])
        items = [("Dashboards", 20), ("Spreadsheets", 90), ("Apps", 160), ("AI assistants", 230)]
        for t, y in items:
            b += AR(242, 135, 440, y + 22) + R(444, y, 220, 44, MINT, [t])
        b += R(730, 60, 250, 110, ROSE, ["The old report", "switch-off date agreed", "with its owner"], dash=True)
        b += T(855, 200, "or you have two truths", 15) + T(550, 292, "each consumer is named, has an owner, and a need for freshness", 14)
        return S(1000, 310, b, "One agreed door, the meaning layer, feeds dashboards, spreadsheets, apps and AI assistants. A dashed box shows the old report, which needs a switch-off date agreed with its owner, otherwise there are two truths."), "Everyone comes in by one door. The old report gets a switch-off date."
    if slug == "across":
        for i, nm in enumerate(LAYER_NAMES):
            b += R(20 + i * 158, 16, 140, 44, "#fff", [nm], 15)
        pillars = [("Quality", "checked every day:", "counts, duplicates, late data", BLUE), ("Security", "who sees what;", "personal data protected", ROSE),
                   ("Cost", "the cloud bill:", "owned, capped, watched", BUTTER), ("Running", "schedules, alerts,", "someone on call", MINT)]
        for i, (a, c, d, f) in enumerate(pillars):
            x = 20 + i * 238
            b += R(x, 96, 220, 110, f, [a, c, d], 18)
        b += T(500, 236, "all four run underneath every layer, from week one", 15)
        return S(1000, 256, b, "The six layers in a row, with four pillars underneath that run across all of them: quality checks every day, security with personal data protected, cost owned and capped, and running with schedules, alerts and someone on call."), "Four jobs under every layer. Each needs an owner and a place in the backlog."


def layer_page(i):
    ly = LAYERS[i]
    prev_l = LAYERS[i - 1] if i > 0 else None
    next_l = LAYERS[i + 1] if i + 1 < len(LAYERS) else None
    svg, cap = d_layer(ly["slug"])
    url_path = f"{BASE}layers/{ly['slug']}/"
    eyebrow = f"Session {ly['session']} · Layer {ly['n']} of 6" if ly["n"] <= 6 else f"Session {ly['session']} · Across all layers"
    matters = "".join(f'<div><h3><span class="n">{k + 1}</span>{E(a)}</h3><p>{E(b)}</p></div>' for k, (a, b) in enumerate(ly["matters"]))
    fails = table(["What goes wrong", "What it looks like", "Early warning sign", "What it costs"], [[f"<b>{E(a)}</b>", E(b), E(c), E(d)] for a, b, c, d in ly["fails"]])
    deeper = "".join(f"<li>{Lx(h, t)}</li>" for h, t in ly["deeper"])
    tech = ("<p class='note'>Optional, for the curious or for a technical colleague:</p><ul>" + "".join(f"<li>{Lx(h, t)}</li>" for h, t in ly["techlinks"]) + "</ul>") if ly["techlinks"] else ""
    pn = '<div class="pn">' + (L(f"{BASE}layers/{prev_l['slug']}/", f"← {prev_l['name']}") if prev_l else L(BASE, "← The roadmap")) + L(BASE, "The roadmap") + (L(f"{BASE}layers/{next_l['slug']}/", f"{next_l['name']} →") if next_l else L(f"{BASE}stakeholders/", "Next: stakeholders →")) + "</div>"
    strip = fig(d_strip(ly["n"]), "Where this layer sits.") if ly["n"] <= 6 else ""
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/how-we-work/">How we work</a> › <a href="{BASE}">Data essentials</a> › {E(ly['name'])}</p>
<p class="eyebrow" style="margin-top:22px">{E(eyebrow)}</p>
<h1>{E(ly['name'])}</h1>
<p class="lede">{E(ly['lede'])}</p>
<div class="tf">
{strip}
<section id="plain"><p class="eyebrow">In plain words</p><h2>What happens here</h2>
<p><b>Think of a city's water.</b> {E(ly['water'])}</p><p>{E(ly['job'])}</p>
{fig(svg, cap)}
<p class="note">Technical names you may hear for this layer: {E(ly['tech'])}.</p></section>
<section id="matters"><p class="eyebrow">What matters most</p><h2>Three things</h2><div class="cards3">{matters}</div></section>
<section id="fails"><p class="eyebrow">What makes it fail</p><h2>How this layer goes wrong</h2>{fails}</section>
<section id="depends"><p class="eyebrow">Dependencies</p><h2>What and who you depend on</h2><ul>{''.join(f'<li>{E(x)}</li>' for x in ly['depends'])}</ul></section>
<section id="ask"><p class="eyebrow">In the room</p><h2>Four questions to ask</h2><ol>{''.join(f'<li>{E(x)}</li>' for x in ly['ask'])}</ol>
<div class="box"><b>Done means:</b> {E(ly['done'])}</div></section>
<section id="deeper"><p class="eyebrow">Go deeper</p><h2>Existing material</h2><ul>{deeper}</ul>{tech}</section>
{pn}
</div>"""
    title = f"{ly['name']}: data project essentials"
    desc = f"{ly['lede']} What matters most, how it fails, who you depend on and the questions to ask, for business analysts, project managers and delivery leads."
    crumbs = [("How we work", "/how-we-work/"), ("Data essentials", BASE), (ly["name"], url_path)]
    return url_path, page_shell(title, desc, url_path, body, crumbs)


# ----------------------------------------------------------------------------- stakeholders
def d_grid():
    b = '<g fill="none" stroke="#111" stroke-width="1.5"><rect x="60" y="14" width="900" height="300" rx="12"/><path d="M510,14 L510,314 M60,164 L960,164" stroke-dasharray="3 5"/></g>'
    b += T(285, 36, "Keep satisfied", 17) + T(735, 36, "Manage closely", 17) + T(285, 186, "Watch", 17) + T(735, 186, "Keep informed", 17)
    b += f'<text x="26" y="170" font-size="15" transform="rotate(-90 26 170)" text-anchor="middle">influence on the project</text>' + T(510, 346, "how much they care about the project", 15)
    b += R(80, 52, 190, 44, ROSE, ["Source system owners"], 15, sw=2.5) + R(280, 52, 200, 44, LAV, ["Security, privacy, compliance"], 14) + R(80, 104, 190, 44, LAV, ["Finance"], 15)
    b += R(530, 52, 190, 44, BUTTER, ["Sponsor"]) + R(730, 52, 210, 44, BUTTER, ["Business owners"]) + R(530, 104, 210, 44, BUTTER, ["Platform and build team"], 14)
    b += R(530, 202, 190, 44, MINT, ["End users"]) + R(730, 202, 210, 44, MINT, ["Support and operations"], 14) + R(530, 254, 210, 44, MINT, ["Testers (business)"], 14)
    b += R(80, 202, 220, 44, GREY, ["Other teams on the platform"], 14)
    b += T(230, 124, "", 1) + R(300, 254, 180, 52, "#fff", ["The usual surprise:", "sources are high influence,", ], 13, dash=True)
    return S(1000, 360, b, "A grid of stakeholders by influence and interest. Manage closely: the sponsor, business owners and the build team. Keep satisfied: security and compliance, finance, and source system owners, highlighted because they have high influence but low interest in your project. Keep informed: end users, support and operations, business testers. Watch: other teams on the platform.")


STAKEHOLDERS = [
    ("Sponsor", "Pays, and decides go, change or stop at each gate.", "Honest risk and progress; a clear decision to make.", "Decisions on scope, money and priority; air cover when a team is slow.", "Told only good news until it is too late."),
    ("Business owners", "Own the question, the metric definitions and the acceptance.", "Their time, in the week it is needed. Sign-off on definitions.", "Early mock-ups; demos with real numbers; plain words.", "Appear at acceptance and change the question."),
    ("Source system owners", "Run the systems the data comes from. Not on your team, with their own priorities.", "Explanations, test data, access, a change calendar, a notice promise.", "A clear, small, early request. Their change windows respected. Thanks.", "First asked in month three, after the plan is signed."),
    ("Security, privacy, compliance", "Protect people and the company; can stop a release.", "Approvals, rules for personal data, access reviews.", "Sensitive-data list, data flow picture, early review.", "Brought in at the end, when they can only say no."),
    ("Finance", "Owns the numbers the business trusts; often the budget.", "Figures to reconcile against; sign-off that totals match.", "A reconciliation plan and cost forecast.", "Discovers the totals do not match at go-live."),
    ("Build team", "Designs, builds, tests and deploys.", "Clear priorities, answers within a day, a protected backlog.", "Shielding from scope creep; the chasing done for them.", "Becomes the one chasing sources and sponsors."),
    ("End users", "Use the reports and tools daily.", "Real feedback; acceptance testing.", "Training, a way to report wrong numbers, fast fixes.", "Told about the change on launch day."),
    ("Support and operations", "Will run the thing after the project ends.", "Their needs in the design; a rehearsal and a runbook they can follow.", "A hand-over that they have tried before the team leaves.", "Receive a system nobody explained."),
]

WEEKLY = [("Proved this week", "What now works end to end, with a number someone checked. Not 'percent complete'."),
          ("Next", "What we will prove next, in one or two lines."),
          ("Risks, with a date", "What could hurt us, who owns it, and by when we need an answer."),
          ("Waiting on", "Names of people we are waiting on, and since when."),
          ("Decisions needed", "What you need from the reader, by when, and what happens if it is late.")]

STK_VERDICT = [("Name a business owner for every metric", "Without one, definitions are argued forever.", "Pursue"),
               ("Raise every outside dependency on day one, with a date", "Waiting is the biggest source of delay.", "Pursue"),
               ("A weekly one-page note with the same five headings", "Readers learn where to look; bad news cannot hide.", "Pursue"),
               ("Escalate at day three of a block, not day thirty", "Early escalation is cheap and rarely offends.", "Pursue"),
               ("Report percent complete per layer", "Looks like progress; hides that nothing is usable.", "Drop"),
               ("One big review meeting with everyone at the end", "Surprises land in front of everyone; nothing can change.", "Drop")]


def stakeholders_page():
    url_path = f"{BASE}stakeholders/"
    rows = [[f"<b>{E(a)}</b>", E(b), E(c), E(d), E(e)] for a, b, c, d, e in STAKEHOLDERS]
    weekly = "".join(f"<li><b>{E(a)}.</b> {E(b)}</li>" for a, b in WEEKLY)
    v = table(["Practice", "Why", "Verdict"], [[f"<b>{E(a)}</b>", E(b), f"<b>{c}</b>"] for a, b, c in STK_VERDICT])
    decide = table(["Decision", "Decides", "Must be consulted", "Must be told"], [
        ["What a metric means", "The business owner of the metric", "Finance, BA, build team", "Every report owner"],
        ["Change the scope", "The sponsor", "Business owners, build team, PM", "Everyone affected"],
        ["Go live", "The sponsor, on evidence", "Operations, security, business owners", "End users"],
        ["Access to a source", "The source owner and security", "Build team, PM", "Sponsor if it blocks the plan"]])
    qa = [("Who is the most forgotten stakeholder?", "The source system owner. They have the most influence on your plan, the least interest in your project, and they are first asked too late."),
          ("How often should I update the sponsor?", "Weekly in writing, in five lines, plus a short call when a decision is needed. Fewer surprises matter more than longer reports.")]
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/how-we-work/">How we work</a> › <a href="{BASE}">Data essentials</a> › Stakeholders</p>
<p class="eyebrow" style="margin-top:22px">Session 9 · People</p>
<h1>Stakeholders in a data project</h1>
<p class="lede">A data project depends on more people outside the team than most projects. This page shows who they are, what each needs from you, and how to keep them with you without long meetings.</p>
<div class="tf">
<section id="map"><p class="eyebrow">The map</p><h2>Who matters, and how much</h2>
<p>The grid below is the standard way to sort people by how much they can change your project and how much they care about it. Data projects have one twist.</p>
{fig(d_grid(), "The twist: source system owners can change your plan the most, and care about your project the least.")}
<div class="box"><b>In one line:</b> spend your effort where influence is high and interest is low. That is the source owner, security and finance, not the sponsor who is already watching.</div></section>
<section id="needs"><p class="eyebrow">One by one</p><h2>What each needs, and what you need from each</h2>
{table(["Who", "Their role", "You need", "They need from you", "The usual trap"], rows)}</section>
<section id="decide"><p class="eyebrow">Who decides</p><h2>Four decisions that always need an owner</h2>{decide}</section>
<section id="status"><p class="eyebrow">The weekly note</p><h2>Status that tells the truth</h2>
<p>One page, five headings, every week, to everyone above. Keep the headings the same, so readers learn where to look.</p>
<ol>{weekly}</ol>
<p class="note">'Percent complete' is not on the list. A data project that is 80 percent built can still be 0 percent usable. Report what was proved.</p></section>
<section id="verdicts"><p class="eyebrow">All in one place</p><h2>Practices, with a verdict</h2>{v}</section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(qa)}</section>
<section id="deeper"><p class="eyebrow">Go deeper</p><h2>Existing material</h2><ul>
<li>{Lx('/learn/technical-anchor/', 'The technical anchor: the map of everyone around the project')}</li>
<li>{Lx('/how-we-work/project-management-mistakes/', 'Top project management mistakes in data projects')}</li>
<li>{Lx('/learn/where-data-engineering-time-goes/', 'Where data engineering time goes (the chasing nobody sees)')}</li></ul></section>
<div class="pn">{L(f'{BASE}layers/across/', '← Across everything')}{L(BASE, 'The roadmap')}{L(f'{BASE}alignment/', 'Next: alignment →')}</div>
</div>"""
    title = "Stakeholders in a data project"
    desc = "Who matters in a data project and how much, what each stakeholder needs, who decides what, and a five-line weekly status that tells the truth."
    return url_path, page_shell(title, desc, url_path, body, [("How we work", "/how-we-work/"), ("Data essentials", BASE), ("Stakeholders", url_path)], qa)


# ----------------------------------------------------------------------------- backlog and agile
def d_slices():
    b = T(250, 24, "Layer by layer (the usual way)", 18) + T(750, 24, "Slice by slice (the better way)", 18)
    rows = ["Meaning", "Model", "Clean", "Landing"]
    for r, nm in enumerate(rows):
        y = 44 + r * 54
        for c in range(4):
            fill = [BLUE, BUTTER, MINT, ROSE][3 - r] if True else "#fff"
            b += f'<rect x="{60 + c * 100}" y="{y}" width="94" height="48" rx="8" fill="{LAV if r > 0 else "#fff"}" stroke="#111" stroke-width="1.3"/>'
        b += T(30, y + 30, str(4 - r), 16)
    b += T(250, 278, "nothing usable until the top row is done", 15)
    for c in range(4):
        x = 560 + c * 100
        for r in range(4):
            y = 44 + r * 54
            on = (c == 0)
            b += f'<rect x="{x}" y="{y}" width="94" height="48" rx="8" fill="{MINT if on else "#fff"}" stroke="#111" stroke-width="{2.4 if on else 1.3}"/>'
        b += T(x + 47, 262, f"slice {c + 1}", 14)
    b += T(750, 286, "slice 1 is usable after a few weeks, then widen", 15)
    b += T(250, 40 + 0, "", 1)
    return S(1000, 300, b, "Two ways to cut the same work. On the left, three of four layers are built across all the sources before anything is usable. On the right, the work is cut in slices, and the first slice goes through every layer for one source, so it is usable early; the other slices widen it.")


def d_sprint():
    b = R(20, 90, 190, 80, BUTTER, ["Spike", "learn the riskiest thing"]) + AR(212, 130, 268, 130) + R(270, 90, 190, 80, BLUE, ["Slice", "build one thin piece"]) + AR(462, 130, 518, 130)
    b += R(520, 90, 190, 80, MINT, ["Prove", "reconcile the numbers"]) + AR(712, 130, 768, 130) + R(770, 90, 210, 80, LAV, ["Demo", "real numbers, real user"])
    b += f'<path d="M875,172 C875,250 115,250 115,172" stroke="#111" stroke-width="1.5" fill="none" stroke-dasharray="5 4" marker-end="url(#dta)"/>'
    b += T(495, 244, "what we learn changes the backlog", 15) + T(495, 40, "a two-week rhythm, repeated", 18)
    return S(1000, 270, b, "A two-week cycle: a spike to learn the riskiest thing, a slice to build one thin piece, prove it by reconciling the numbers, and demo it with real numbers to a real user. What is learned flows back to change the backlog.")


READY = ["The source and its owner are named.", "We have seen a real sample of the data.", "Access to the source works from our environment.", "The business owner of each metric is named.", "Acceptance criteria are written as checks on data, not wishes."]
DONE = ["Tested against the source: counts and totals match.", "Reconciled to a figure the business already trusts.", "Quality checks run daily and alert a named person.", "Deployed to the test environment by the pipeline, not by hand.", "Documented: where it came from and what it means.", "Shown to the business owner, who accepts it."]

ITEM_KINDS = [("Spike", "Learn something risky in a fixed time. Output: an answer, not a feature.", "Can we reach the billing system from our environment?"),
              ("Slice", "A thin piece that runs through every layer for one source and ends in a number a person checks.", "Daily sales by store, from the orders system, to one report."),
              ("Run", "What keeps it alive: alerts, runbook, cost watch, support rota.", "Alert the on-call person if the nightly load is late."),
              ("Fix or debt", "Something that works but will hurt later. Small, visible, and sized.", "Replace a manual file upload with the automatic load.")]

AGILE_VERDICT = [("Cut the backlog in slices that run through every layer", "Value and learning arrive early; risks show up in weeks.", "Pursue"),
                 ("Put spikes at the top of the backlog, riskiest first", "Fail fast means learning the dangerous thing before the easy ones.", "Pursue"),
                 ("A Definition of Ready for data items", "Stops the team starting work that cannot finish.", "Pursue"),
                 ("Track effort and calendar time separately", "Waiting for access is not effort; hiding it hides the real delay.", "Pursue"),
                 ("Plan whole layers, one after another, as phases", "Nothing usable until late; the first real test is at the end.", "Drop"),
                 ("Let scope changes in without removing anything", "The date does not move, the quality does.", "Drop")]


def backlog_page():
    url_path = f"{BASE}backlog/"
    kinds = table(["Kind of item", "What it is", "Example"], [[f"<b>{E(a)}</b>", E(b), E(c)] for a, b, c in ITEM_KINDS])
    ready = "".join(f"<li>{E(x)}</li>" for x in READY)
    done = "".join(f"<li>{E(x)}</li>" for x in DONE)
    v = table(["Practice", "Why", "Verdict"], [[f"<b>{E(a)}</b>", E(b), f"<b>{c}</b>"] for a, b, c in AGILE_VERDICT])
    qa = [("Does agile work for data projects?", "Yes, with two changes: slice through all the layers instead of building layer by layer, and treat learning about the source as work in the backlog, not as something that happens before it."),
          ("Should we estimate in story points?", "Use whatever your team uses, but also size by source complexity and give ranges. Waiting time is not effort, so track calendar time separately. See the estimation page.")]
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/how-we-work/">How we work</a> › <a href="{BASE}">Data essentials</a> › Backlog and agile</p>
<p class="eyebrow" style="margin-top:22px">Session 10 · Plan</p>
<h1>Backlog and agile for data projects</h1>
<p class="lede">Agile fits data projects, with one habit changed: cut the work into thin slices that go through every layer, instead of building the layers one by one. This page shows how to shape the backlog, when an item is ready, and when it is done.</p>
<div class="tf">
<section id="slices"><p class="eyebrow">Teach first</p><h2>Cut the work the right way</h2>
<p>The natural plan for a data platform is to build the landing layer for all sources, then the clean layer, then the model, then the reports. It looks tidy, and it hides the risk until the end. The better plan takes one source, all the way to one number a person checks, and then widens.</p>
{fig(d_slices(), "Same work, cut two ways. The first slice is the whole project in miniature, so every surprise appears in week three, not month six.")}
<div class="box"><b>In one line:</b> a slice is finished when a business person has checked a number that came from the real source.</div></section>
<section id="rhythm"><p class="eyebrow">The rhythm</p><h2>Learn, build, prove, show</h2>
{fig(d_sprint(), "Each cycle starts with the thing most likely to be wrong. The demo uses real numbers, because a demo on fake data proves nothing.")}</section>
<section id="kinds"><p class="eyebrow">Backlog items</p><h2>Four kinds, not one</h2><p>A data backlog is not only features. Name the kinds, so learning and running get planned like building.</p>{kinds}</section>
<section id="order"><p class="eyebrow">Order</p><h2>Riskiest first, then most valuable</h2>
<p>Normal advice is to order by value. For data projects, order by risk first: the belief that would sink the project if wrong goes to the top, as a spike. Once the risks are answered, order by value as usual. Scope changes go in as a trade: something of the same size comes out, or the date moves, in the open.</p></section>
<section id="ready"><p class="eyebrow">Two checklists</p><h2>Ready, and done</h2>
<div class="cards3"><div><h3>Ready to start</h3><ul>{ready}</ul></div><div><h3>Done</h3><ul>{done}</ul></div></div>
<p class="note">Write these on the wall of the team. An item that fails 'ready' goes back, with a reason and a person to chase.</p></section>
<section id="estimates"><p class="eyebrow">Estimates</p><h2>Ranges, not single numbers</h2>
<p>Early estimates are wide, and that is honest. They narrow after discovery and again after the first slice. Estimate the learning too, and keep effort and calendar time apart. The full set of mistakes is on its own page: {Lx('/how-we-work/estimation/', 'Estimation mistakes in data projects')}.</p></section>
<section id="verdicts"><p class="eyebrow">All in one place</p><h2>Practices, with a verdict</h2>{v}</section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(qa)}</section>
<section id="deeper"><p class="eyebrow">Go deeper</p><h2>Existing material</h2><ul>
<li>{Lx('/how-we-work/estimation/', 'Estimation mistakes in data projects')}</li>
<li>{Lx('/how-we-work/project-management-mistakes/', 'Top project management mistakes in data projects')}</li>
<li>{Lx('/learn/technical-anchor/', 'The data project lifecycle, stage by stage')}</li></ul></section>
<div class="pn">{L(f'{BASE}alignment/', '← Alignment')}{L(BASE, 'The roadmap')}{L(f'{BASE}fail-fast/', 'Next: fail fast →')}</div>
</div>"""
    title = "Backlog and agile for data projects"
    desc = "How to cut a data project into thin slices, order the backlog by risk, write a Definition of Ready and Done for data, and keep estimates honest."
    return url_path, page_shell(title, desc, url_path, body, [("How we work", "/how-we-work/"), ("Data essentials", BASE), ("Backlog and agile", url_path)], qa)


# ----------------------------------------------------------------------------- fail fast
def d_cost():
    stages = [("week 1", 1), ("discovery", 3), ("build", 9), ("test", 27), ("go-live", 60), ("running", 100)]
    b = T(500, 24, "The same problem, found at different times (relative cost, illustrative)", 17)
    for i, (s, v) in enumerate(stages):
        x = 70 + i * 150
        h = 8 + v * 2.0
        b += f'<rect x="{x}" y="{250 - h}" width="100" height="{h}" rx="8" fill="{[MINT, MINT, BUTTER, BUTTER, ROSE, ROSE][i]}" stroke="#111" stroke-width="1.5"/>'
        b += T(x + 50, 274, s, 15) + T(x + 50, 250 - h - 8, "x" + str(v), 15)
    return S(1000, 296, b, "Bars showing the relative cost of finding the same problem at different times. Week one costs one unit, discovery three, build nine, test twenty-seven, go-live sixty and running a hundred. The numbers are illustrative; the rising shape is the point.")


TESTS = [("1", "Sample test", "Day 1 to 3", "Get one real extract. Can we open it? Does it look like the description we were given?", "Business analyst with the source owner", "The sample is different from the description."),
         ("2", "Access test", "Week 1", "Can the team really reach the source from the build environment, with the right permissions?", "Delivery manager", "A firewall, an approval or a licence is needed."),
         ("3", "Meaning test", "Week 1 to 2", "Walk through ten fields with the source expert. Which ones cannot be explained?", "Business analyst", "Two or more fields have no owner."),
         ("4", "One-number test", "Week 2 to 3", "Pick one figure finance already knows. Can we rebuild it from the source?", "Analyst and finance", "We cannot get within the agreed tolerance."),
         ("5", "Volume and timing test", "Week 2 to 3", "How long does the full load take, and does it fit the window the source allows?", "Technical anchor", "It takes longer than the window, or slows the source."),
         ("6", "Change test", "Week 3", "What happens on a late, changed or deleted record? Can we see it at all?", "Business analyst", "The source overwrites or deletes without a trace."),
         ("7", "User test", "Week 2", "Show a mock-up to the person who will use it. Is this the answer to your question?", "Product owner", "'It is not what I meant.'"),
         ("8", "Running test", "Before go-live", "Break something on purpose. Who is alerted, and can operations fix it from the runbook?", "Delivery manager", "Nobody is alerted, or only the builders can fix it.")]

KILL = [("Go", "Every key belief is tested and holds; the estimate is a range everyone accepts.", "Start MVP 1."),
        ("Go with changes", "One belief failed, but there is a cheaper way to the same value.", "Change the scope, estimate and date in the open. Write down why."),
        ("Stop", "A belief we cannot fix fails (no access, no data, no owner, no value).", "Stop, and count it as a success: it cost weeks, not a year.")]


def fail_fast_page():
    url_path = f"{BASE}fail-fast/"
    tests = table(["#", "Test", "When", "What we do", "Who", "A fail looks like"], [[E(a), f"<b>{E(b)}</b>", E(c), E(d), E(e), E(f)] for a, b, c, d, e, f in TESTS])
    kill = table(["Decision", "When", "What happens"], [[f"<b>{E(a)}</b>", E(b), E(c)] for a, b, c in KILL])
    risks = table(["Risk", "Dependency behind it", "Early sign", "First move"], [
        ["Source meaning unknown", "Source owner's time", "Fields nobody can explain", "Meaning test in week 1 to 2"],
        ["Access late", "Security and network approvals", "No request sent in week 1", "Send the request on day 1, with a date"],
        ["Numbers do not match", "Finance's time and figures", "No reconciliation plan", "One-number test in week 2 to 3"],
        ["Scope grows quietly", "A sponsor who says yes to all", "'Just one more source'", "Change goes in as a trade, in the open"],
        ["Nobody runs it", "Operations", "Operations first hear of it at go-live", "Invite operations to demos from MVP 1"]])
    qa = [("Is failing fast the same as giving up?", "No. It means finding out cheaply, in week two, whether a belief is true, so you can change the plan while changing is cheap. Stopping a project in discovery is a good result."),
          ("Who owns the fail-fast tests?", "Each test has a named person. The business analyst owns tests about meaning and change, the delivery manager owns tests about access and running, and the technical anchor owns tests about volume and timing.")]
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/how-we-work/">How we work</a> › <a href="{BASE}">Data essentials</a> › Fail fast</p>
<p class="eyebrow" style="margin-top:22px">Session 11 · Protect</p>
<h1>Fail fast, in a data project</h1>
<p class="lede">Failing fast does not mean failing often. It means finding out in week two, and not in month six, whether something you are counting on is true. This page lists eight cheap tests, who runs them, and how to decide go, change or stop.</p>
<div class="tf">
<section id="why"><p class="eyebrow">Teach first</p><h2>The same problem costs more every week it hides</h2>
<p>A source that cannot be reached, a field nobody understands, a total that does not match: each is cheap to find in the first weeks and expensive to find at go-live. The cure is to test the dangerous beliefs first, on purpose.</p>
{fig(d_cost(), "The figures are illustrative. The shape is the point: the same problem costs far more later.")}
<div class="box"><b>In one line:</b> list what you are counting on, test the most dangerous first, and treat bad news early as the project working.</div></section>
<section id="tests"><p class="eyebrow">Eight tests</p><h2>Cheap ways to be wrong early</h2>{tests}
<p class="note">These match the discovery stage of the project lifecycle. The full document and its reviewers are on the {Lx('/learn/technical-anchor/discovery/', 'discovery page')}.</p></section>
<section id="gates"><p class="eyebrow">Go, change or stop</p><h2>Agree the rules before you test</h2><p>Decide in advance what counts as a pass. Otherwise a failed test gets explained away.</p>{kill}</section>
<section id="risks"><p class="eyebrow">Risks and dependencies</p><h2>A small register that gets used</h2>
<p>Five risks appear on almost every data project. Each has a dependency behind it, a sign you can see early, and a first move. Keep the register to one page and look at it every week.</p>{risks}</section>
<section id="review"><p class="eyebrow">Check a real project</p><h2>The project review</h2>
<p>When a project already exists, a review looks at its documents for gaps at its stage. The checks are listed by stage, so a non-technical reviewer can use them: {Lx('/learn/technical-anchor/project-review/', 'Project review')} and {Lx('/learn/technical-anchor/project-review/checks/', 'the full checks')}.</p></section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(qa)}</section>
<section id="deeper"><p class="eyebrow">Go deeper</p><h2>Existing material</h2><ul>
<li>{Lx('/learn/technical-anchor/discovery/', 'Discovery: fail fast for the whole project')}</li>
<li>{Lx('/how-we-work/critical-thinking/', 'Critical thinking in data projects')}</li>
<li>{Lx('/how-we-work/project-management-mistakes/', 'Top project management mistakes in data projects')}</li></ul></section>
<div class="pn">{L(f'{BASE}backlog/', '← Backlog and agile')}{L(BASE, 'The roadmap')}</div>
</div>"""
    title = "Fail fast in a data project"
    desc = "Eight cheap tests that find out in week two whether a data project's key beliefs are true, who runs each, the go, change or stop rule, and a one-page risk register."
    return url_path, page_shell(title, desc, url_path, body, [("How we work", "/how-we-work/"), ("Data essentials", BASE), ("Fail fast", url_path)], qa)


# ----------------------------------------------------------------------------- DDLC by role
DDLC = [
    (1, "Requirement received", False, "Write the need as questions, not a solution. List every assumption.", "Log it, name a sponsor, note who must be asked next.",
     "The need is accepted as 'build a dashboard', with no decision behind it.", "Which decision will this change?"),
    (2, "Rough estimate", False, "List what can be counted: sources, tables, reports, users.", "Give a range with its assumptions, and the cost of discovery.",
     "A number said in a corridor becomes the commitment.", "Which assumption, if wrong, moves this the most?"),
    (3, "Discovery", False, "Sources, real data, consumers, requirements written as tests.", "Timebox it. Plan the fail-fast tests. Open the risk register.",
     "It is skipped to save time, and the plan is built on guesses.", "Which belief would sink the project, and have we tested it?"),
    (4, "Discovery sign-off", True, "Walk reviewers through scope and open questions.", "Get sign-off by name: go, go with changes, or stop.",
     "People sign what they have not read or do not agree with.", "Is anyone signing something they disagree with?"),
    (5, "MVP 1 starts", False, "Acceptance criteria for every item, as checks on data.", "Environments, access, release pipeline, team ready on day one.",
     "The team waits weeks for access and a place to work.", "Can we deploy a thin slice this week?"),
    (6, "Build", False, "Answer questions within a day. Demo with real numbers.", "Track effort against estimate weekly. Run the change process.",
     "Status is percent complete, and scope creeps through side doors.", "What is turning out harder than it looked?"),
    (7, "Test", False, "Run acceptance with numbers users recognise.", "Book business testers early; they are busy.",
     "Business testers are not available, or see the data for the first time.", "Would the business recognise these numbers?"),
    (8, "Deploy", False, "Confirm the history load and what it covers.", "Rehearse cut-over and rollback. Run a failure drill with operations.",
     "There is no rollback, and operations first see the system on launch day.", "Have we rehearsed both cut-over and rollback?"),
    (9, "Production sign-off", True, "Reconcile the first production loads with finance.", "Hypercare: watch the first runs; confirm operations can run alone.",
     "The builders leave, and nobody else can fix a failure.", "Would operations accept this if the team left tomorrow?"),
    (10, "Project sign-off", True, "Measure the benefits promised in stage 1.", "Hand over decision log, runbook, glossary. Close the risks. Write lessons.",
     "Benefits are never measured, so nobody knows if it worked.", "Can the team run and change this without us?"),
]


def d_ddlc():
    b = ""
    w, gap, h = 170, 28, 70
    for i, (n, name, gate, *_r) in enumerate(DDLC):
        row = 0 if i < 5 else 1
        col = i if row == 0 else 9 - i
        x, y = 20 + col * (w + gap), 50 + row * 130
        fill = "#FFF1C2" if gate else (BUTTER if n == 3 else (MINT if n >= 5 else BLUE))
        b += R(x, y, w, h, fill, [f"{n} {name}"] + (["sign-off gate"] if gate else []), 15, sw=3 if gate else 1.5)
        if i < 4:
            b += AR(x + w + 2, y + h / 2, x + w + gap - 2, y + h / 2)
        elif i == 4:
            b += AR(x + w / 2, y + h + 2, x + w / 2, y + 130 - 2)
        elif i < 9:
            b += AR(x - 2, y + h / 2, x - gap + 2, y + h / 2)
    b += T(250, 30, "deciding: is it worth doing, and how?", 17) + T(600, 170 - 14, "", 1) + T(700, 196 - 30 + 0, "", 1)
    b += T(560, 282, "stages 5 to 9 repeat for every MVP (minimum viable product)", 15)
    return S(1000, 296, b, "The data development lifecycle in ten stages: requirement received, rough estimate, discovery, discovery sign-off, MVP 1 starts, build, test, deploy, production sign-off, project sign-off. Sign-off gates are stages 4, 9 and 10. Stages 5 to 9 repeat for every MVP.")


def ddlc_page():
    url_path = f"{BASE}ddlc/"
    rows = [[f"<b>{n} · {E(nm)}</b>" + (' <span class="tag">gate</span>' if g else ""), E(ba), E(pm), E(bad), f"<i>{E(q)}</i>"] for n, nm, g, ba, pm, bad, q in DDLC]
    t = table(["Stage", "Business analyst", "Project / delivery manager", "What goes wrong here", "Fail-fast question"], rows)
    qa = [("What is the DDLC?", "The data development lifecycle: the ten stages a data project goes through, from a business need arriving to the project closing. It looks like a software lifecycle, but discovery and proving the numbers carry much more weight."),
          ("What is the difference from the software lifecycle?", "In software the unknown is mostly what to build. In data the unknown is mostly what the sources really mean and whether the numbers can be trusted, so learning and proving are stages of their own.")]
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/how-we-work/">How we work</a> › <a href="{BASE}">Data essentials</a> › DDLC</p>
<p class="eyebrow" style="margin-top:22px">Session 2 · The lifecycle</p>
<h1>The data development lifecycle, by role</h1>
<p class="lede">Every data project goes through the same ten stages. This page shows them in one picture, what a business analyst and a project or delivery manager each does at every stage, and what usually goes wrong there.</p>
<div class="tf">
<section id="picture"><p class="eyebrow">Teach first</p><h2>Ten stages, three gates</h2>
<p>The first four stages decide whether the project is worth doing and how. The rest deliver one small working piece at a time, called an MVP, and repeat for each. At a sign-off gate, a named person says go, go with changes, or stop.</p>
{fig(d_ddlc(), "The gates are gold. Stage 3, discovery, is the one most often skipped, and the one that pays back most.")}
<div class="box"><b>In one line:</b> decide first (stages 1 to 4), then deliver in repeated small pieces (5 to 9), then hand over and measure (10).</div></section>
<section id="roles"><p class="eyebrow">Stage by stage</p><h2>What each role does, and what goes wrong</h2>{t}
<p class="note">The technical anchor's view of the same stages, with the technical jobs, is in {Lx('/learn/technical-anchor/', 'the full lifecycle')}.</p></section>
<section id="software"><p class="eyebrow">Why not the usual way</p><h2>Why a data project is not a software project</h2>
<ol><li><b>It is discovery as much as delivery.</b> You learn what the sources mean while you build.</li>
<li><b>The biggest dependency is outside the team.</b> Source owners, security and finance.</li>
<li><b>Done means trusted numbers.</b> A pipeline that runs but disagrees with finance is not done.</li></ol></section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(qa)}</section>
<section id="deeper"><p class="eyebrow">Go deeper</p><h2>Existing material</h2><ul>
<li>{Lx('/learn/technical-anchor/', 'The data project lifecycle, in full')}</li><li>{Lx('/learn/technical-anchor/discovery/', 'Discovery, step by step')}</li>
<li>{Lx('/how-we-work/project-management-mistakes/', 'Project management mistakes')}</li></ul></section>
<div class="pn">{L(BASE, '← The roadmap')}{L(f'{BASE}challenges/', 'Next: the hardest challenges →')}</div>
</div>"""
    return url_path, page_shell("The data development lifecycle (DDLC) by role", "The ten stages of a data project with three sign-off gates, what a business analyst and a project manager each do at every stage, and what goes wrong there.", url_path, body, [("How we work", "/how-we-work/"), ("Data essentials", BASE), ("DDLC", url_path)], qa)


# ----------------------------------------------------------------------------- hardest challenges
CHALLENGES = [
    ("Knowledge", "Nobody knows what the source means", "The knowledge is in a few heads, or in nobody's.", "Fields nobody can explain; 'ask Ravi, but he left'.", "Meaning test in week 1 to 2; a named owner per source; write answers down.", "sources"),
    ("Knowledge", "Old reports hide the rules", "The current report is a spreadsheet with years of manual fixes nobody documented.", "'The number is right, don't touch it', but nobody can say how it is made.", "Reverse-engineer the report with its owner before designing anything.", "gather"),
    ("Knowledge", "The data is worse than expected", "Real data has duplicates, gaps and odd codes that samples don't show.", "Profiling in week 2 shows 15 percent of rows break a rule.", "Profile real data in discovery, and agree what to do with bad rows.", "clean"),
    ("People", "Other teams own the sources", "They have their own priorities and no reason to help you quickly.", "Requests wait; answers come in weeks.", "Sponsor-backed requests, small and early, with dates. Treat source owners as stakeholders.", "stakeholders"),
    ("People", "Departments define things differently", "Revenue, customer and active mean different things to sales and finance.", "Two reports, two numbers, one argument.", "One owner per metric; show both numbers on real data; the owner decides; write it down.", "alignment"),
    ("People", "Requirements change when people see data", "Nobody knows what they want until they see their own numbers.", "'This isn't what I meant' at acceptance.", "Show real numbers in week two and every two weeks after. Slice thin.", "consumers"),
    ("Time", "Access and approvals take weeks", "Security, privacy and network changes follow their own calendar.", "The team has nothing to work on in week one.", "Send requests on day one, with dates; track waiting separately from effort.", "across"),
    ("Time", "The unknown is hard to estimate", "Estimates count code, and the real work is learning and waiting.", "The first number is two to three times too low.", "Ranges, effort and calendar apart, estimate discovery, re-estimate after the first slice.", "backlog"),
    ("Time", "Proving the numbers is slow", "Reconciling to finance finds differences that need a person to explain.", "Last week of the project: totals differ by 3 percent.", "Plan reconciliation as a stage from slice one, not a final week.", "model"),
    ("People", "Nobody owns it after go-live", "The team leaves; operations and the business are not ready.", "A job fails on Sunday and no one is alerted.", "Operations at demos from MVP 1; a rehearsed failure drill; named owners.", "across"),
]


def d_challenges():
    groups = [("Knowledge", BLUE), ("People", BUTTER), ("Time", MINT)]
    b = ""
    for gi, (g, f) in enumerate(groups):
        x = 20 + gi * 325
        b += R(x, 20, 300, 44, f, [g], 20, sw=2.5)
        items = [c[1] for c in CHALLENGES if c[0] == g]
        for k, t in enumerate(items):
            b += R(x, 80 + k * 50, 300, 42, "#fff", [t], 14)
    return S(1000, 280, b, "The ten hardest challenges in three groups. Knowledge: nobody knows what the source means, old reports hide the rules, the data is worse than expected. People: other teams own the sources, departments define things differently, requirements change, nobody owns it after go-live. Time: access takes weeks, the unknown is hard to estimate, proving numbers is slow.")


def challenges_page():
    url_path = f"{BASE}challenges/"
    hrefs = {"sources": f"{BASE}layers/sources/", "gather": f"{BASE}gather/", "clean": f"{BASE}layers/clean/", "stakeholders": f"{BASE}stakeholders/", "alignment": f"{BASE}alignment/",
             "consumers": f"{BASE}layers/consumers/", "across": f"{BASE}layers/across/", "backlog": f"{BASE}backlog/", "model": f"{BASE}layers/model/"}
    cards = ""
    for i, (g, t, why, sign, help_, ref) in enumerate(CHALLENGES):
        cards += (f'<div class="sess"><h3><span class="n">{i + 1}</span>{E(t)} <span class="tag">{E(g)}</span></h3><dl><dt>Why it is hard</dt><dd>{E(why)}</dd>'
                  f'<dt>Early sign</dt><dd>{E(sign)}</dd><dt>What helps</dt><dd>{E(help_)} <a href="{hrefs[ref]}">Read more →</a></dd></dl></div>')
    qa = [("What is the hardest part of a data project?", "Usually not the code. It is learning what the source data means, and getting people in other teams to agree on definitions and spare time. Both are about people and knowledge, so they have to be planned for."),
          ("How can I tell early that a project is in trouble?", "Three early signs: nobody can name the person who understands a source, no one has seen real data yet, and access has not been requested. Any one is worth raising the same day.")]
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/how-we-work/">How we work</a> › <a href="{BASE}">Data essentials</a> › Hardest challenges</p>
<p class="eyebrow" style="margin-top:22px">Session 3 · What goes wrong</p>
<h1>The hardest challenges in data projects</h1>
<p class="lede">Data projects rarely fail because the code was hard. They fail on knowledge nobody wrote down, people who are not on your team, and time spent waiting. Ten challenges, each with its early sign and what helps.</p>
<div class="tf">
<section id="map"><p class="eyebrow">Teach first</p><h2>Three groups</h2>
{fig(d_challenges(), "Knowledge, people and time. Only a small part of the work is the code.")}
<div class="box"><b>In one line:</b> the hard parts are knowing, agreeing and waiting. Plan for them in the backlog, as work.</div></section>
<section id="list"><p class="eyebrow">The ten</p><h2>Challenge by challenge</h2>{cards}</section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(qa)}</section>
<section id="deeper"><p class="eyebrow">Go deeper</p><h2>Existing material</h2><ul>
<li>{Lx('/how-we-work/project-management-mistakes/', 'Top project management mistakes in data projects')}</li><li>{Lx('/how-we-work/estimation/', 'Estimation mistakes in data projects')}</li>
<li>{Lx('/learn/where-data-engineering-time-goes/', 'Where data engineering time really goes')}</li></ul></section>
<div class="pn">{L(f'{BASE}ddlc/', '← DDLC')}{L(BASE, 'The roadmap')}{L(f'{BASE}layers/sources/', 'Next: upstream, sources →')}</div>
</div>"""
    return url_path, page_shell("The hardest challenges in data projects", "Ten challenges that make data projects fail, in three groups: knowledge, people and time, with the early sign of each and what helps.", url_path, body, [("How we work", "/how-we-work/"), ("Data essentials", BASE), ("Hardest challenges", url_path)], qa)


# ----------------------------------------------------------------------------- gather information
METHODS = [
    ("Talk to the business owner", "What they need, and which decision it drives.", "People describe the process as it should be, not as it is.", "'Walk me through last month's report, from the first click.'"),
    ("Watch a user work", "How the numbers are really used and fixed by hand.", "Takes time; users change behaviour when watched.", "Sit with an analyst for an hour on month-end."),
    ("Study existing reports", "What is really calculated, and for whom.", "Hidden logic in spreadsheets and macros.", "Ask the owner to explain every column and every manual step."),
    ("Read the documents", "Intended design, names and rules.", "Often old and wrong; check the date.", "Data dictionary, specs, contracts, old project plans."),
    ("Look at the data itself", "Counts, blanks, duplicates, ranges, dates, odd codes.", "A small sample can hide the problem.", "Ask for a real extract in week one; have an engineer profile it."),
    ("Read the code and queries", "Rules nobody remembers: filters, joins, fixes.", "Needs a technical colleague; code may be unused.", "Stored procedures and jobs that build today's report."),
    ("Check tickets and incidents", "Where it breaks, and how often.", "Not every problem becomes a ticket.", "Last year's incidents on the current reports."),
    ("Check who really uses what", "Which reports are used and which are dead.", "Usage logs may not exist.", "Open counts for each current dashboard."),
]

INTERVIEW = ["Walk me through the last time you used this number. What did you do first?", "What do you do when the number looks wrong?", "What would break if this report disappeared tomorrow?",
             "Which parts do you fix by hand, and why?", "Who else should I ask, and who disagrees with you?", "What have I not asked that I should have?"]

GVERDICT = [("Compare what people say, what documents say and what the data shows", "Where they disagree is the finding.", "Pursue"),
            ("Start from the report people use, then trace backwards", "It anchors the talk in something real.", "Pursue"),
            ("Write down who said what, and the date", "Memory fades and people move jobs.", "Pursue"),
            ("Confirm in writing what you heard", "Cheapest way to catch a misunderstanding.", "Pursue"),
            ("Trust the old document as the truth", "It is often out of date.", "Drop"),
            ("Ask one expert and stop", "One person knows part of it; others will disagree.", "Drop")]


def d_triangle():
    b = R(390, 20, 220, 60, BLUE, ["What people say", "interviews, watching"]) + R(90, 220, 220, 60, BUTTER, ["What documents say", "specs, old reports, code"]) + R(690, 220, 220, 60, MINT, ["What the data shows", "real extract, profiled"])
    b += AR(440, 82, 290, 218) + AR(560, 82, 710, 218) + AR(312, 252, 688, 252)
    b += R(390, 140, 220, 80, ROSE, ["Where they disagree", "is the finding"], 17, sw=2.5)
    return S(1000, 300, b, "Three views of the same system: what people say, what documents say, and what the data shows. They are compared with each other, and where they disagree is the finding.")


def d_steps5():
    labels = [("1", "Start from the output", "the report people use"), ("2", "Find owners", "per part of it"), ("3", "Look at the data", "real extract"), ("4", "Compare the three views", "note the gaps"), ("5", "Write and confirm", "send back to the owner")]
    b = ""
    for i, (n, a, c) in enumerate(labels):
        x = 20 + i * 196
        b += R(x, 30, 172, 90, [BLUE, BUTTER, MINT, ROSE, LAV][i], [f"{n} {a}", c], 15)
        if i < 4:
            b += AR(x + 174, 75, x + 194, 75)
    return S(1000, 150, b, "Five steps for gathering information: start from the output people use, find owners for each part, look at the real data, compare the three views and note the gaps, then write it down and confirm with the owner.")


def gather_page():
    url_path = f"{BASE}gather/"
    mt = table(["Method", "Good for", "Watch out", "Example"], [[f"<b>{E(a)}</b>", E(b), E(c), E(d)] for a, b, c, d in METHODS])
    iv = "".join(f"<li>{E(x)}</li>" for x in INTERVIEW)
    v = table(["Practice", "Why", "Verdict"], [[f"<b>{E(a)}</b>", E(b), f"<b>{c}</b>"] for a, b, c in GVERDICT])
    qa = [("Where should I start?", "With the output: the report or number people use today. Then trace backwards to the systems, and forwards to the decisions it drives."),
          ("What if two people tell me different things?", "Good: that is the finding. Put both answers side by side on a real sample of data, and ask the owner of the metric to decide. Write the decision down.")]
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/how-we-work/">How we work</a> › <a href="{BASE}">Data essentials</a> › Gather information</p>
<p class="eyebrow" style="margin-top:22px">Session 4 · Upstream understanding</p>
<h1>Gather information from people and existing systems</h1>
<p class="lede">Most of what a data project needs to know is in people's heads, old reports and the data itself. This page shows how to collect it, how to tell which of it is true, and how to write it down so it is not lost.</p>
<div class="tf">
<section id="three"><p class="eyebrow">Teach first</p><h2>Three views of the same thing</h2>
<p>People tell you how it should work. Documents tell you how it was meant to work, years ago. The data shows how it really works. Each is partly right. Always look at all three, and compare.</p>
{fig(d_triangle(), "Where the three views disagree, there is a risk or a hidden rule. That is what you are looking for.")}</section>
<section id="steps"><p class="eyebrow">Order</p><h2>Five steps</h2>{fig(d_steps5(), "Start from the output, and end by sending your notes back to the owner.")}</section>
<section id="methods"><p class="eyebrow">Eight ways</p><h2>Methods, and their traps</h2>{mt}</section>
<section id="interview"><p class="eyebrow">In the interview</p><h2>Six questions for anyone</h2><ol>{iv}</ol>
<div class="box"><b>Write it down:</b> who said it, on what date, and what you are unsure of. Send it back the same day: 'This is what I understood. Please correct me.' Keep the answers in a shared place, not in your notebook. The key idea card on {Lx('/concepts/data-map/', 'the data map')} shows what to record.</div></section>
<section id="verdicts"><p class="eyebrow">All in one place</p><h2>Practices, with a verdict</h2>{v}</section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(qa)}</section>
<section id="deeper"><p class="eyebrow">Go deeper</p><h2>Existing material</h2><ul>
<li>{Lx('/learn/data-systems/upstreams/questionnaire/', 'Source system questionnaire: what to ask every source owner')}</li><li>{Lx('/learn/data-systems/upstreams/answers/', 'Where the answers go')}</li>
<li>{Lx('/learn/data-systems/downstreams/', 'Downstreams: what to ask every consumer')}</li><li>{Lx('/learn/technical-anchor/discovery/', 'Discovery: the document these answers feed')}</li></ul></section>
<div class="pn">{L(f'{BASE}layers/sources/', '← Sources')}{L(BASE, 'The roadmap')}{L(f'{BASE}layers/landing/', 'Next: landing →')}</div>
</div>"""
    return url_path, page_shell("Gather information from people and existing systems", "How to collect what a data project needs to know: compare what people say, what documents say and what the data shows, with eight methods, six interview questions and a verdict table.", url_path, body, [("How we work", "/how-we-work/"), ("Data essentials", BASE), ("Gather information", url_path)], qa)


# ----------------------------------------------------------------------------- alignment
GAPS = [("Business and business", "Sales and finance mean different things by 'revenue'.", "One owner per metric. Show both numbers on real data. The owner decides, and the other is renamed."),
        ("Business and the build team", "'A dashboard of sales' means three different things.", "Write requirements as questions and checks on data. Show a mock-up in week two."),
        ("Build team and source owners", "The source owner has other priorities.", "A small, early, dated request with sponsor backing. Agree a notice period for changes."),
        ("Project manager and sponsor", "The date and the scope cannot both hold.", "Show the trade in the open: scope out, or date moves. Record who decided."),
        ("Project team and operations", "Operations see the system on launch day.", "Invite operations to demos from MVP 1. Rehearse the failure drill together.")]

TOOLS = [("One-page glossary", "Every business word the project uses, its meaning, and its owner. Short, shared, dated.", "Start in discovery. Review monthly."),
         ("Three conversations before each slice", "Business owner, analyst and engineer, together, for 30 minutes: what the question is, what the data has, how we will check the number.", "Before every slice, not once."),
         ("Acceptance as checks on data", "A requirement is finished when it can be tested: 'daily sales by store match the finance report within 0.5 percent'.", "Write with the item."),
         ("Demo with real numbers", "Every two weeks, to a real user. Fake data proves nothing.", "Fixed day, fixed audience."),
         ("Decision log", "Date, the decision, who made it, why, and what it replaced. One page, in a shared place.", "Add within a day."),
         ("Project on a page", "Goal, scope in and out, the three gates, the key dates and the owners. Everyone sees the same page.", "Update at each gate.")]

AVERDICT = [("Write first, meet second, record after", "A short note settles most issues without a meeting.", "Pursue"),
            ("Settle a definition dispute on real data", "People argue less when they see both numbers.", "Pursue"),
            ("One owner decides, in the open", "Consensus on definitions rarely arrives.", "Pursue"),
            ("Long status meetings with everyone", "Slow, and bad news hides in them.", "Drop"),
            ("Agreeing verbally and moving on", "Two people leave with two memories.", "Drop")]


def d_gaps():
    b = R(390, 125, 220, 70, LAV, ["One shared understanding", "words, numbers, dates"], 17, sw=2.5)
    pos = [(30, 20, "Business", "Business"), (730, 20, "Business", "Build team"), (30, 230, "Build team", "Source owners"), (730, 230, "Sponsor", "Project manager"), (380, 250, "Team", "Operations")]
    for i, (x, y, a, c) in enumerate(pos):
        b += R(x, y, 240, 54, [BUTTER, BLUE, MINT, ROSE, GREY][i], [GAPS[i][0]], 15)
        b += AR(x + 120, y + (54 if y < 100 else 0), 500, 125 if y < 100 else 195, dash=True)
    return S(1000, 320, b, "Five places where people drift apart, each pulled back to one shared understanding: business and business, business and the build team, the build team and source owners, sponsor and project manager, and the project team and operations.")


def alignment_page():
    url_path = f"{BASE}alignment/"
    gaps = table(["Where people drift apart", "What it looks like", "What helps"], [[f"<b>{E(a)}</b>", E(b), E(c)] for a, b, c in GAPS])
    tools = table(["Tool", "What it is", "When"], [[f"<b>{E(a)}</b>", E(b), E(c)] for a, b, c in TOOLS])
    v = table(["Practice", "Why", "Verdict"], [[f"<b>{E(a)}</b>", E(b), f"<b>{c}</b>"] for a, b, c in AVERDICT])
    qa = [("What do I do when two stakeholders define a metric differently?", "Do not pick. Put both numbers on the same real sample, show the difference, and ask the owner of the metric to decide. Rename the other one so both can live with different names. Write the decision down."),
          ("How do I keep engineers and the business aligned?", "Have the three conversations before each slice, write requirements as checks on data, and demo with real numbers every two weeks.")]
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/how-we-work/">How we work</a> › <a href="{BASE}">Data essentials</a> › Alignment</p>
<p class="eyebrow" style="margin-top:22px">Session 9 · People</p>
<h1>Alignment between stakeholders, analysts and engineers</h1>
<p class="lede">Most data projects have enough clever people. What they lack is the same understanding in all their heads. This page shows the five places people drift apart, and six small habits that keep them together.</p>
<div class="tf">
<section id="gaps"><p class="eyebrow">Teach first</p><h2>Five places people drift apart</h2>
{fig(d_gaps(), "Every gap is closed the same way: put it in writing, on real data, with an owner.")}{gaps}</section>
<section id="tools"><p class="eyebrow">Six habits</p><h2>What keeps people aligned</h2>{tools}</section>
<section id="example"><p class="eyebrow">An example</p><h2>The same word, two meanings</h2>
<p>Sales says an 'active customer' bought in the last 30 days. Finance says it has an open contract. Both are right for their purpose. On the same real sample, the counts are 1,200 and 1,850. The owner of the metric, here the head of customer, decides that 'active customer' means a contract, and renames the sales one 'recent buyer'. It goes in the glossary and the decision log, and both teams get a note the same day.</p></section>
<section id="verdicts"><p class="eyebrow">All in one place</p><h2>Practices, with a verdict</h2>{v}</section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(qa)}</section>
<section id="deeper"><p class="eyebrow">Go deeper</p><h2>Existing material</h2><ul>
<li>{Lx('/learn/technical-anchor/', 'The technical anchor: a design that works from every side')}</li><li>{Lx('/how-we-work/critical-thinking/', 'Critical thinking in data projects')}</li>
<li>{Lx('/concepts/data-contracts/', 'Key idea: data contracts')}</li></ul></section>
<div class="pn">{L(f'{BASE}stakeholders/', '← Stakeholders')}{L(BASE, 'The roadmap')}{L(f'{BASE}backlog/', 'Next: backlog and agile →')}</div>
</div>"""
    return url_path, page_shell("Alignment between stakeholders, analysts and engineers", "Five places people drift apart on a data project and six habits that keep them aligned: glossary, three conversations, acceptance as checks on data, real demos, decision log, one page.", url_path, body, [("How we work", "/how-we-work/"), ("Data essentials", BASE), ("Alignment", url_path)], qa)


# ----------------------------------------------------------------------------- the hub: the roadmap
# (n, part, title, one idea, you will be able to, [(href, text, status)], format exercise)
SESSIONS = [
    (1, 1, "The whole picture", "A data system has three blocks: what we don't own, what we build, and who uses it.",
     "Draw the six layers from memory and say what each is for in one sentence.",
     [("/learn/data-systems/", "Data systems, end to end", "old"), (BASE + "#picture", "The big picture (on this page)", "new")],
     "Take a data project you know. Mark which block each problem came from."),
    (2, 1, "The data development lifecycle (DDLC)", "Discover first, then deliver one thin slice at a time, with three sign-off gates.",
     "Name the ten stages and three gates, say what your role does at each, and why this is not a software project.",
     [(BASE + "ddlc/", "DDLC, stage by stage, by role", "new"), ("/learn/technical-anchor/", "The lifecycle, in full (technical anchor)", "old"), ("/learn/where-data-engineering-time-goes/", "Where the time goes", "old")],
     "Place your current project on the ten stages. Which gate is next, and who signs it?"),
    (3, 1, "What goes wrong: the hardest challenges", "Most failures are about knowledge, people and time, not code.",
     "Name the ten hardest challenges and the early sign of each.",
     [(BASE + "challenges/", "The hardest challenges", "new"), ("/how-we-work/project-management-mistakes/", "Project management mistakes", "old"), ("/how-we-work/estimation/", "Estimation mistakes", "old")],
     "Which three challenges is your project facing today? What is the evidence?"),
    (4, 2, "Upstream understanding", "We depend on systems we don't own, and their meaning is not obvious. Find out early, from people and from the systems.",
     "Run a source meeting, gather what is known from people and systems, and spot a missing owner.",
     [(BASE + "layers/sources/", "Layer 1: Sources", "new"), (BASE + "gather/", "Gather information from people and systems", "new"), ("/learn/data-systems/upstreams/", "Upstreams: the questions", "old"), ("/learn/data-systems/upstreams/questionnaire/", "Source questionnaire", "old")],
     "Pick a source. Answer the four questions from the layer page. What is unknown, and who could tell you?"),
    (5, 2, "Getting data in, and cleaning it", "Keep the raw copy untouched, then clean it with written rules.",
     "Ask for freshness, history, rerun safety and the rules for bad rows.",
     [(BASE + "layers/landing/", "Layer 2: Landing", "new"), (BASE + "layers/clean/", "Layer 3: Clean", "new"), ("/learn/medallion-architecture/", "Medallion architecture", "old")],
     "Write three cleaning rules for a customer list, and say who owns each."),
    (6, 2, "Shaping data, and defining numbers", "Choose the grain, and give every number one definition and one owner.",
     "Write a metric definition with an owner, and a reconciliation plan against a known report.",
     [(BASE + "layers/model/", "Layer 4: Model", "new"), (BASE + "layers/meaning/", "Layer 5: Meaning", "new"), ("/concepts/semantic-layer/", "Key idea: semantic layer", "old")],
     "Define 'active customer' in one sentence, with an owner. Do two people agree?"),
    (7, 2, "Downstream understanding", "Name every consumer; give one door; switch off the old report.",
     "Build a consumer register and agree a switch-off date.",
     [(BASE + "layers/consumers/", "Layer 6: People use it", "new"), ("/learn/data-systems/downstreams/", "Downstreams: know your consumers", "old")],
     "List five consumers for a sales report, and the freshness each needs."),
    (8, 2, "What runs across everything", "Quality, security, cost and running each need an owner and a place in the backlog.",
     "Check a plan has stories for all four, and a rehearsed failure drill.",
     [(BASE + "layers/across/", "Across everything", "new"), ("/learn/data-systems/platform/", "The data platform: all concerns", "old"), ("/learn/data-systems/platform/cost/", "Cost and FinOps", "old")],
     "Who gets the 2 a.m. call on your project? Have they seen the runbook?"),
    (9, 3, "People: stakeholders and alignment", "Spend effort where influence is high and interest is low, and make sure everyone means the same thing.",
     "Map stakeholders, name decision owners, write the five-line weekly note, and settle a definition dispute.",
     [(BASE + "stakeholders/", "Stakeholders", "new"), (BASE + "alignment/", "Alignment", "new"), ("/learn/technical-anchor/", "The map of everyone around the project", "old")],
     "Draw the grid for your project. Find one word that two people define differently."),
    (10, 3, "Plan: backlog, agile, estimates", "Cut in thin slices, order by risk, estimate in ranges.",
     "Reshape a layer-by-layer plan into slices, and write Ready and Done for data items.",
     [(BASE + "backlog/", "Backlog and agile", "new"), ("/how-we-work/estimation/", "Estimation mistakes", "old")],
     "Take a 6-month plan and cut it into three slices. What does slice 1 prove?"),
    (11, 3, "Protect: fail fast and risks", "Test the most dangerous belief first, and agree the go, change, stop rule.",
     "Run the eight tests, keep a one-page risk register, and review a project's documents.",
     [(BASE + "fail-fast/", "Fail fast", "new"), ("/learn/technical-anchor/discovery/", "Discovery", "old"), ("/learn/technical-anchor/project-review/", "Project review", "old")],
     "Review one real project document with the stage checks. Count the gaps."),
]
PARTS = {1: ("Part 1 · See the whole", "peri"), 2: ("Part 2 · Walk the layers", "butter"), 3: ("Part 3 · Run the project", "mint")}

ROLES = [("Business analyst", "●●●●○●●○●○●"), ("Project manager", "●●●●○○○●●●●"), ("Delivery manager", "●●●○○–○●●●●"),
         ("Product owner", "●●○○–●●○●●○"), ("Tester or QA", "●○○○●●●●–○○"), ("Sponsor or leader", "●●●––○●○○–●")]

RULES = ["Data projects are discovery first and delivery second.",
         "The source is the biggest unknown, and someone else owns it.",
         "Slice thin: one source to one trusted number, then widen.",
         "Every number has a name, a formula and an owner.",
         "Done means the totals match a figure the business already trusts.",
         "Raise every access and approval on day one, with a date.",
         "Estimate in ranges, and keep effort apart from calendar time.",
         "Say bad news early. It is the cheapest it will ever be.",
         "Plan the running before go-live: who is alerted, who fixes it.",
         "Switch off the old report, or you have two truths."]

FAILS = [("The meaning of the source is guessed", "Sources", "sources"), ("Rows go missing or double", "Landing", "landing"), ("Duplicates and silent drops", "Clean", "clean"),
         ("Wrong grain, two definitions", "Model", "model"), ("Metrics without owners", "Meaning", "meaning"), ("Built, but not used", "People use it", "consumers"),
         ("Nobody runs it", "Across everything", "across"), ("The plan counts code, not waiting", "Whole project", None)]

FORMATS = [("Weekly, 11 weeks", "One session a week, 60 minutes: 15 for the picture, 20 for the page, 15 for the exercise, 10 for 'what will you ask on Monday?'. Best for a team that works together."),
           ("Two-day workshop", "Parts 1 and 2 on day one, Part 3 on day two, with the exercises done on your own project. Best for a new team starting a project."),
           ("Express, 4 hours", "Sessions 1, 2, 3 and 11 only. Best for sponsors and senior leaders.")]

HUB_QA = [("Do I need to know how to code?", "No. Nothing here needs code. Where a page links to technical material, it is marked optional."),
          ("How long is the whole programme?", "Eleven sessions of about an hour. The pages can also be read alone, in any order, once you have seen the big picture."),
          ("Which pages are new and which already existed?", "The roadmap marks each link: 'new' means written for this programme, 'existing' means already on the site and reused as it is.")]


def d_picture():
    b = ""
    bw, gap, x0 = 140, 22, 25
    refs = ["sources", "landing", "clean", "model", "meaning", "consumers"]
    fills = [GREY, BLUE, BLUE, BLUE, BLUE, MINT]
    subs = ["apps, files, APIs", "raw, untouched", "one trusted row", "shaped for questions", "one definition each", "dashboards, apps, AI"]
    fl = ["Meaning guessed", "Rows missing or doubled", "Duplicates, silent drops", "Wrong grain", "Three revenues", "Built, not used"]
    for i, nm in enumerate(LAYER_NAMES):
        x = x0 + i * (bw + gap)
        b += R(x, 44, bw, 84, fills[i], [nm, subs[i]], 18, href=f"{BASE}layers/{refs[i]}/")
        if i < 5:
            b += AR(x + bw + 1, 86, x + bw + gap - 2, 86)
        b += R(x, 150, bw, 50, ROSE, [fl[i]], 14, dash=True)
    b += T(x0 + bw / 2, 30, "we don't own it", 15) + T(x0 + bw + gap + 2 * (bw + gap) + bw / 2 + 80, 30, "we build it", 15)
    b += T(x0 + 5 * (bw + gap) + bw / 2, 30, "they use it", 15) + T(500, 222, "how it usually fails", 14)
    b += R(25, 238, 950, 56, LAV, ["Across everything: quality · security · cost · running"], 17, href=f"{BASE}layers/across/")
    return S(1000, 310, b, "The whole data project on one page: six layers in a row, sources, landing, clean, model, meaning, and people use it, with how each usually fails written underneath in red dashes, and a band across the bottom for quality, security, cost and running. Each box links to its page.")


def hub_page():
    url_path = BASE
    steps = "".join(f'<a class="p{p}" href="#s{n}"><b>{n}</b><span>{E(t)}</span></a>' for n, p, t, *_ in SESSIONS)
    sess = ""
    cur = 0
    for n, p, t, idea, able, mats, ex in SESSIONS:
        if p != cur:
            cur = p
            sess += f'<p class="part">{PARTS[p][0]}</p>'
        mlinks = " ".join(f'<span class="tag {"new" if s == "new" else "old"}">{"new" if s == "new" else "existing"}</span> {Lx(h, tx)}' if True else "" for h, tx, s in mats)
        mlinks = "<br>".join(f'<span class="tag {"new" if s == "new" else "old"}">{"new" if s == "new" else "existing"}</span> {Lx(h, tx)}' for h, tx, s in mats)
        sess += (f'<div class="sess" id="s{n}"><h3><span class="n">{n}</span>{E(t)}</h3><dl><dt>One idea</dt><dd>{E(idea)}</dd>'
                 f'<dt>You can then</dt><dd>{E(able)}</dd><dt>Material</dt><dd>{mlinks}</dd><dt>Exercise</dt><dd>{E(ex)}</dd></dl></div>')
    role_rows = ""
    for r, marks in ROLES:
        role_rows += f"<tr><td><b>{E(r)}</b></td>" + "".join(f'<td class="c {"y" if m == "●" else ("p" if m == "○" else "")}">{m}</td>' for m in marks) + "</tr>"
    role_head = "<tr><th>Role</th>" + "".join(f"<th>{n}</th>" for n in range(1, 12)) + "</tr>"
    rules = "".join(f"<li>{E(r)}</li>" for r in RULES)
    fails = ""
    for t, layer, slug in FAILS:
        link = f'<a href="{BASE}layers/{slug}/">{E(layer)}</a>' if slug else E(layer)
        fails += f"<tr><td><b>{E(t)}</b></td><td>{link}</td></tr>"
    fmts = table(["Format", "How it runs"], [[f"<b>{E(a)}</b>", E(b)] for a, b in FORMATS])
    gloss_ids = ["etl-elt", "medallion", "data-quality", "data-contracts", "lineage", "governance", "semantic-layer", "freshness", "backfill", "scd", "idempotency", "orchestration", "observability", "cost-drivers", "data-map", "discovery"]
    chips = "".join(f'<a href="/concepts/{c}/">{E(CARDS[c]["name"])}</a>' for c in gloss_ids if c in CARDS)
    inv_old = [("/learn/data-systems/", "Data systems, end to end"), ("/learn/data-systems/upstreams/", "Upstreams: know your sources"), ("/learn/data-systems/upstreams/questionnaire/", "Source system questionnaire"),
               ("/learn/data-systems/downstreams/", "Downstreams: know your consumers"), ("/learn/technical-anchor/", "The technical anchor and the project lifecycle"), ("/learn/technical-anchor/discovery/", "Discovery"),
               ("/learn/technical-anchor/project-review/", "Project review"), ("/how-we-work/estimation/", "Estimation mistakes"), ("/how-we-work/project-management-mistakes/", "Project management mistakes"),
               ("/how-we-work/critical-thinking/", "Critical thinking in data projects"), ("/learn/where-data-engineering-time-goes/", "Where the time goes"), ("/learn/medallion-architecture/", "Medallion architecture"),
               ("/concepts/", "Key ideas A to Z")]
    inv_new = [(BASE + "layers/" + l["slug"] + "/", f"Layer: {l['name']}") for l in LAYERS] + [(BASE + "ddlc/", "DDLC by role"), (BASE + "challenges/", "The hardest challenges"), (BASE + "gather/", "Gather information"), (BASE + "stakeholders/", "Stakeholders"), (BASE + "alignment/", "Alignment"), (BASE + "backlog/", "Backlog and agile"), (BASE + "fail-fast/", "Fail fast")]
    inv = (f'<div class="cards3"><div><h3>Existing, reused as is</h3><ul>{"".join(f"<li>{Lx(h, t)}</li>" for h, t in inv_old)}</ul></div>'
           f'<div><h3>New, written for this programme</h3><ul>{"".join(f"<li>{Lx(h, t)}</li>" for h, t in inv_new)}</ul></div></div>')
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/how-we-work/">How we work</a> › Data essentials</p>
<p class="eyebrow" style="margin-top:22px">Roadmap · for business analysts, project and delivery managers, product owners, testers and sponsors</p>
<h1>Data project essentials, for non-technical roles</h1>
<p class="lede">How a data project is run from the first source system to the last dashboard, what matters in each layer, what makes it fail, and how to plan, staff and steer it. No code. Eleven sessions, one idea each, with a picture for every idea.</p>
<div class="tf">
<nav class="toc"><b>On this page</b><ol><li><a href="#picture">The whole picture</a></li><li><a href="#roadmap">The roadmap: 11 sessions</a></li><li><a href="#roles">Which sessions for which role</a></li><li><a href="#matters">What matters most: ten sentences</a></li><li><a href="#fails">Why data projects fail</a></li><li><a href="#formats">How to run it</a></li><li><a href="#words">Words you will hear</a></li><li><a href="#material">All the material</a></li></ol></nav>
<section id="picture"><p class="eyebrow">Start here</p><h2>The whole data project on one page</h2>
<p>A client says: 'We want to see our numbers in a dashboard.' Behind that sentence are six layers. The first belongs to other teams, the middle four are what the project builds, and the last is where people use the result. Under all of them run four jobs that nobody sees until they fail. Each box opens its own page.</p>
{fig(d_picture(), "Six layers, four jobs underneath, and in red the way each one usually fails. Click a box.")}
<div class="box"><b>For your role:</b> you do not build these layers. You make sure the questions are asked, the people are named, and the dates are real, in every layer, early.</div></section>
<section id="roadmap"><p class="eyebrow">The roadmap</p><h2>Eleven sessions in three parts</h2>
<p>Each session is about an hour and teaches one idea with one picture. Part 1 gives the whole picture, the project lifecycle and the hardest challenges. Part 2 walks the layers, one at a time, upstream first and downstream last. Part 3 is about running the project: people and alignment, plan, and risk.</p>
<div class="steps">{steps}</div>
{sess}</section>
<section id="roles"><p class="eyebrow">Which sessions for which role</p><h2>Everyone starts with 1 and 2</h2>
<div class="tw"><table class="t">{role_head}{role_rows}</table></div>
<p class="note">● the session is for your role, ○ useful, a dash means you can skip it. Green is must, yellow is useful.</p></section>
<section id="matters"><p class="eyebrow">What matters most</p><h2>Ten sentences to remember</h2><ol class="rules">{rules}</ol></section>
<section id="fails"><p class="eyebrow">What makes a data project fail</p><h2>Eight ways, and where each lives</h2>
<div class="tw"><table class="t"><tr><th>How it fails</th><th>Where to read about it</th></tr>{fails}</table></div>
<p>The full list of the ten hardest challenges is on {Lx(BASE + 'challenges/', 'its own page')}. The two ways that belong to the whole project are covered in {Lx('/how-we-work/project-management-mistakes/', 'Project management mistakes')} and {Lx('/how-we-work/estimation/', 'Estimation mistakes')}.</p></section>
<section id="formats"><p class="eyebrow">How to run it</p><h2>Three formats</h2>{fmts}</section>
<section id="words"><p class="eyebrow">Words you will hear</p><h2>Short ideas, one page each</h2><p>Each is a one-page card with an example and the usual mistake.</p><div class="chips">{chips}</div></section>
<section id="material"><p class="eyebrow">All the material</p><h2>What exists, and what is new</h2>{inv}</section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(HUB_QA)}</section>
</div>"""
    title = "Data project essentials for non-technical roles"
    desc = ("An eleven-session roadmap for business analysts, project and delivery managers and product owners: how a data project runs from source systems to dashboards, "
            "what matters in each layer, what makes it fail, stakeholders, backlog, estimates and fail fast.")
    return url_path, page_shell(title, desc, url_path, body, [("How we work", "/how-we-work/"), ("Data essentials", url_path)], HUB_QA)


def main():
    pages = [hub_page(), ddlc_page(), challenges_page(), gather_page(), alignment_page(), stakeholders_page(), backlog_page(), fail_fast_page()] + [layer_page(i) for i in range(len(LAYERS))]
    for rel, html in pages:
        write(rel, html)


if __name__ == "__main__":
    main()
