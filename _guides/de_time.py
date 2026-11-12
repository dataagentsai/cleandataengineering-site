"""Where data engineering time goes: one page at /learn/where-data-engineering-time-goes/.

    python3 _guides/de_time.py      (then python3 _site/nav.py and python3 _site/seo.py)

Teach first with pictures: the iceberg (code is the tip), then two charts of where the hours go
(first build of a source vs a year of running it), then the chain that shows why misread source
meaning is the root of most of the rest. Second half: the non-technical work a data engineer ends up
doing, and how to shrink it, do it once, or hand it to the right person (verdict per move).

The percentages are a field estimate from projects, labelled so on the page; two public surveys are
quoted for comparison, both vendor-run. Chart colours checked with the dataviz validator
(#5B7FC7 / #E0A526: pass; contrast WARN relieved by ink outlines, direct labels and a table view).
"""
import json
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "_paths"))
import components as C  # noqa: E402
import table_formats as TF  # noqa: E402

wb = C.wb
SITE = wb.SITE
URL_PATH = "/learn/where-data-engineering-time-goes/"
DATE = "2026-11-12"
TITLE = "Where data engineering time really goes, and how to win it back"
DESC = ("Where a data engineer's hours go when onboarding a source and when running it: understanding what the "
        "source data means is the biggest share, code is the smallest. The non-technical work, and how to shrink it or hand it over.")

BUILD_C, RUN_C = "#5B7FC7", "#E0A526"   # validated pair
INK, MUTED = "#111", "#555"
BLUE, MINT, BUTTER, ROSE, LAV = "#eef3fb", "#eaf6ef", "#fff4d6", "#fbeef3", "#efeaf8"

CSS = TF.CSS + """<style>
  .tf .stat { display:flex; gap:14px; flex-wrap:wrap; margin:14px 0; }
  .tf .stat div { flex:1 1 180px; border:var(--line); border-radius:var(--wob); padding:10px 16px; background:#fff; }
  .tf .stat b { display:block; font-family:var(--hand); font-size:34px; line-height:1.1; }
  .tf .stat span { font-size:14px; color:var(--muted); }
  .tf .fig svg .bar:hover { stroke-width:2.6; }
  .tf details { margin:8px 0 14px; } .tf summary { cursor:pointer; font-size:14.5px; }
</style>"""

ARROW = '<defs><marker id="dta" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#111"/></marker></defs>'

# key, label, kind (n = non-technical, t = technical), % of hours in the first build, % in a year of running, what it is
ACTS = [
    ("sem", "Understanding what the source data means", "n", 28, 10,
     "What one row is, which columns are the key, what each status code means, how deletes show up, which date is which, how tables join."),
    ("rec", "Reconciling numbers with old reports", "n", 10, 12,
     "\"Finance says 1,204 orders, your table says 1,191.\" Finding and explaining every difference."),
    ("def", "Agreeing definitions with the business", "n", 8, 5,
     "What counts as an active customer, a sale, a return. Often two departments disagree."),
    ("acc", "Getting access and approvals", "n", 7, 3,
     "Credentials, firewall rules, security reviews, data-sharing sign-off, waiting."),
    ("mtg", "Meetings, status and handovers", "n", 7, 8,
     "Estimates, stand-ups, status reports, explaining delays, onboarding the next person."),
    ("code", "Writing the pipeline code", "t", 12, 8,
     "Ingestion, transforms, SCD2, gold tables, the part people picture when they hear 'data engineer'."),
    ("dq", "Fixing data quality problems", "t", 8, 20,
     "Nulls, duplicates, late files, a source that changed a column without telling anyone."),
    ("ops", "Running it: failures, reruns, backfills", "t", 7, 20,
     "A job failed at 3 a.m.; last month needs reloading; a backfill after a fix."),
    ("plat", "Platform, CI/CD, speed and cost", "t", 7, 9,
     "Clusters, deployments, permissions as code, tuning a slow join, the cloud bill."),
    ("test", "Testing", "t", 6, 5,
     "Unit tests on transforms, contract checks, end-to-end runs."),
]
assert sum(a[3] for a in ACTS) == 100 and sum(a[4] for a in ACTS) == 100


def _hatch(pid, colour):
    return (f'<pattern id="{pid}" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            f'<rect width="7" height="7" fill="{colour}"/><line x1="0" y1="0" x2="0" y2="7" stroke="#fff" stroke-width="2"/></pattern>')


def drawing_iceberg():
    d = f'<svg viewBox="0 0 1000 380" role="img" aria-label="An iceberg. Above the water line, a small tip labelled writing the pipeline code, about one hour in eight. Below the water, a much bigger mass labelled with what nobody sees: understanding what the source data means, reconciling numbers, agreeing definitions, getting access, meetings, fixing data quality, running and rerunning jobs.">{ARROW}'
    d += f'<rect x="0" y="120" width="1000" height="260" fill="{BLUE}"/>'
    d += '<path d="M0,120 q25,-8 50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0 t50,0" fill="none" stroke="#111" stroke-width="1.5"/>'
    # tip
    d += '<path d="M430,120 L470,46 L500,62 L530,30 L575,120 Z" fill="#fff" stroke="#111" stroke-width="1.5"/>'
    d += '<text x="640" y="56" font-size="17">what people picture:</text><text x="640" y="80" font-size="17">writing the pipeline code</text>'
    d += '<path d="M636,70 L560,72" stroke="#111" stroke-width="1.4" fill="none" marker-end="url(#dta)"/>'
    # body under water
    d += '<path d="M430,120 L300,200 L250,290 L330,360 L520,372 L700,350 L760,270 L700,180 L575,120 Z" fill="#fff" stroke="#111" stroke-width="1.5" stroke-dasharray="6 4"/>'
    lines = ["what the source data means", "reconciling the numbers", "agreeing definitions", "access, approvals, meetings",
             "fixing bad data", "reruns and backfills"]
    for i, t in enumerate(lines):
        d += f'<text x="505" y="{168 + i * 30}" text-anchor="middle" font-size="{18 if i == 0 else 15.5}">{t}</text>'
    d += '<text x="40" y="160" font-size="15">the water line</text><text x="40" y="350" font-size="14.5">what the plan never shows</text>'
    return d + "</svg>"


def chart_build():
    """Horizontal bars, single series (first build), grouped under two headings."""
    rows = [a for a in ACTS if a[2] == "n"] + [a for a in ACTS if a[2] == "t"]
    x0, scale, h, gap = 360, 17, 26, 10
    y = 54
    d = '<svg viewBox="0 0 1000 470" role="img" aria-label="Bar chart of where the hours go in the first build of a source. Non-technical work, 60 percent: understanding what the source data means 28, reconciling numbers 10, agreeing definitions 8, getting access 7, meetings 7. Technical work, 40 percent: writing code 12, fixing data quality 8, running it 7, platform 7, testing 6.">'
    d += '<text x="20" y="24" font-size="16">Share of hours, first build of one source (about three to six months)</text>'
    for kind, head in (("n", "Non-technical work: 60%"), ("t", "Technical work: 40%")):
        d += f'<text x="20" y="{y + 4}" font-size="17">{head}</text>'
        y += 14
        for key, label, k, b, r, what in [a for a in rows if a[2] == kind]:
            w = b * scale
            d += f'<text x="{x0 - 12}" y="{y + 18}" text-anchor="end" font-size="14.5">{E(label)}</text>'
            d += (f'<rect class="bar" x="{x0}" y="{y}" width="{w}" height="{h}" rx="4" fill="{BUILD_C}" stroke="#111" stroke-width="1.5">'
                  f'<title>{E(label)}: {b}% of hours in the first build</title></rect>')
            d += f'<text x="{x0 + w + 8}" y="{y + 18}" font-size="15">{b}%</text>'
            y += h + gap
        y += 18
    d += f'<line x1="{x0}" y1="40" x2="{x0}" y2="{y - 24}" stroke="#111" stroke-width="1"/>'
    return d + "</svg>"


def chart_build_vs_run():
    """Grouped horizontal bars: first build vs a year of running, two validated colours, legend + direct labels."""
    x0, scale, h = 360, 17, 15
    y = 70
    d = '<svg viewBox="0 0 1000 560" role="img" aria-label="Grouped bar chart comparing the first build with a year of running. Understanding source meaning falls from 28 to 10 percent; reconciling 10 to 12; definitions 8 to 5; access 7 to 3; meetings 7 to 8; writing code 12 to 8; fixing data quality rises from 8 to 20; running, reruns and backfills from 7 to 20; platform 7 to 9; testing 6 to 5.">'
    d += f'<defs>{_hatch("dth", RUN_C)}</defs>'
    d += '<text x="20" y="24" font-size="16">First build vs a year of running the same source</text>'
    d += f'<rect x="{x0}" y="36" width="18" height="14" rx="3" fill="{BUILD_C}" stroke="#111" stroke-width="1.2"/><text x="{x0 + 26}" y="48" font-size="14.5">first build</text>'
    d += f'<rect x="{x0 + 130}" y="36" width="18" height="14" rx="3" fill="url(#dth)" stroke="#111" stroke-width="1.2"/><text x="{x0 + 156}" y="48" font-size="14.5">a year of running</text>'
    for key, label, k, b, r, what in ACTS:
        d += f'<text x="{x0 - 12}" y="{y + 19}" text-anchor="end" font-size="14.5">{E(label)}</text>'
        d += (f'<rect class="bar" x="{x0}" y="{y}" width="{b * scale}" height="{h}" rx="4" fill="{BUILD_C}" stroke="#111" stroke-width="1.3">'
              f'<title>{E(label)}: {b}% in the first build</title></rect>')
        d += f'<text x="{x0 + b * scale + 6}" y="{y + 12}" font-size="12.5">{b}%</text>'
        d += (f'<rect class="bar" x="{x0}" y="{y + h + 2}" width="{r * scale}" height="{h}" rx="4" fill="url(#dth)" stroke="#111" stroke-width="1.3">'
              f'<title>{E(label)}: {r}% in a year of running</title></rect>')
        d += f'<text x="{x0 + r * scale + 6}" y="{y + 2 * h + 14}" font-size="12.5">{r}%</text>'
        y += 2 * h + 14
        if key == "mtg":
            d += f'<line x1="20" y1="{y - 5}" x2="980" y2="{y - 5}" stroke="#111" stroke-width="1" stroke-dasharray="3 5"/>'
            y += 6
    d += f'<line x1="{x0}" y1="62" x2="{x0}" y2="{y}" stroke="#111" stroke-width="1"/>'
    d += f'<text x="20" y="{y + 26}" font-size="14" fill="{MUTED}">above the dotted line: non-technical work · below: technical work</text>'
    return d + "</svg>"


def drawing_chain():
    steps = [("misread meaning", "status 'C' taken as Closed;\nit means Cancelled", ROSE),
             ("wrong rule in code", "cancelled orders\ncounted as sales", BUTTER),
             ("numbers don't match", "finance report\nis 3% lower", BUTTER),
             ("reconcile + rework", "two weeks of\nmeetings and fixes", BLUE),
             ("trust lost", "users go back\nto spreadsheets", LAV)]
    d = f'<svg viewBox="0 0 1000 220" role="img" aria-label="A chain of five boxes. Misread meaning: status C taken as Closed when it means Cancelled. Leads to a wrong rule in code: cancelled orders counted as sales. Leads to numbers that do not match: the finance report is 3 percent lower. Leads to reconcile and rework: two weeks of meetings and fixes. Leads to trust lost: users go back to spreadsheets.">{ARROW}'
    for i, (h, s, fill) in enumerate(steps):
        x = 10 + i * 198
        d += f'<rect x="{x}" y="40" width="172" height="130" rx="12" fill="{fill}" stroke="#111" stroke-width="1.5"/>'
        d += f'<text x="{x + 86}" y="74" text-anchor="middle" font-size="16.5">{h}</text>'
        for j, ln in enumerate(s.split("\n")):
            d += f'<text x="{x + 86}" y="{110 + j * 22}" text-anchor="middle" font-size="14">{E(ln)}</text>'
        if i < 4:
            d += f'<path d="M{x + 174},105 L{x + 196},105" stroke="#111" stroke-width="1.6" fill="none" marker-end="url(#dta)"/>'
    d += '<text x="500" y="204" text-anchor="middle" font-size="14.5">one question asked early would have cost ten minutes</text>'
    return d + "</svg>"


def drawing_who():
    """Hand the people work to the people whose job it is."""
    people = [("source owner", "answers what the data means;\nannounces changes", MINT),
              ("business owner", "signs off each definition\nand the reconciliation", BUTTER),
              ("analyst / anchor", "runs the questionnaire,\nchases answers, writes them down", LAV),
              ("data engineer", "builds, tests and runs\nfrom written answers", BLUE)]
    d = '<svg viewBox="0 0 1000 250" role="img" aria-label="Four people, each with their own job. Source owner: answers what the data means and announces changes. Business owner: signs off each definition and the reconciliation. Analyst or technical anchor: runs the questionnaire, chases answers and writes them down. Data engineer: builds, tests and runs from written answers.">'
    for i, (who, what, fill) in enumerate(people):
        cx = 125 + i * 250
        d += f'<circle cx="{cx}" cy="56" r="24" fill="#fff" stroke="#111" stroke-width="1.5"/>'
        d += f'<path d="M{cx - 40},126 q40,-60 80,0 Z" fill="{fill}" stroke="#111" stroke-width="1.5"/>'
        d += f'<circle cx="{cx - 8}" cy="52" r="2" fill="#111"/><circle cx="{cx + 8}" cy="52" r="2" fill="#111"/><path d="M{cx - 8},64 q8,6 16,0" stroke="#111" stroke-width="1.3" fill="none"/>'
        d += f'<text x="{cx}" y="156" text-anchor="middle" font-size="17">{who}</text>'
        for j, ln in enumerate(what.split("\n")):
            d += f'<text x="{cx}" y="{184 + j * 21}" text-anchor="middle" font-size="13.5">{E(ln)}</text>'
    return d + "</svg>"


# chore, why it eats a data engineer's time, how to cut it, who should own it, verdict
NONTECH = [
    ("Learning what the source data means",
     "Answers live in people's heads. The engineer finds out by trial and error, one surprise at a time, often after the code is written.",
     "Run the source questionnaire before any code. Ask the source team for 10 real records with the answers they expect. Profile the data automatically first (distinct values, nulls, key checks) so meetings start from facts. Write every answer into the metadata store, next to the column.",
     "Analyst or technical anchor asks; source owner answers; engineer reviews",
     "Shrink and do once. Never skip: it is the job"),
    ("Reconciling numbers with old reports",
     "Nobody agreed what 'matching' means, so every difference becomes an investigation.",
     "Before building, agree the report to match, the tolerance (for example 0.5%) and the known differences. Build automatic reconciliation checks (counts and sums against source control totals) that run every load.",
     "Business owner signs off; engineer automates the check",
     "Pursue"),
    ("Agreeing definitions",
     "Two departments define 'active customer' differently and the engineer is asked to pick.",
     "One named owner per metric. Definitions written once in the semantic layer (metric views) with a worked example. The engineer implements; never arbitrates.",
     "Business owner (data product owner)",
     "Pursue"),
    ("Getting access and approvals",
     "Requests start when coding starts, then the engineer waits weeks.",
     "Raise every access request on day one, in parallel, from a standard access pack. Make access-granted a gate before the build starts.",
     "Project manager or anchor",
     "Pursue"),
    ("Meetings and status reports",
     "Status is pulled from engineers by asking, in meetings.",
     "Status lives on one written plan page the engineer updates in two minutes. One weekly checkpoint. Stakeholder chasing belongs to the anchor, not the builder.",
     "Project manager",
     "Pursue"),
    ("Firefighting surprise source changes",
     "A source adds, renames or re-codes a column without notice; pipelines break or, worse, keep running with wrong numbers.",
     "A data contract with the source team (schema, meaning, change notice period). Schema-drift and value-drift alerts on bronze. Quarantine instead of silently loading.",
     "Source owner keeps the contract; engineer builds the alarms",
     "Pursue"),
    ("Hiring more engineers to absorb it",
     "More engineers each relearn the same meaning and attend the same meetings.",
     "Fix where the answers live instead.",
     "Nobody",
     "Drop"),
    ("Letting an AI assistant guess the meaning",
     "It drafts quickly but cannot ask the person who knows. A confident wrong guess is worse than a question.",
     "Use AI to draft questions, profile data and summarise docs; a person confirms every answer before it is written down.",
     "Analyst, with AI as helper",
     "Pursue as a helper only"),
]

TABLE_ROWS = [(lab, "Non-technical" if k == "n" else "Technical", f"{b}%", f"{r}%", what) for _, lab, k, b, r, what in ACTS]

SURVEYS = [
    ("Monte Carlo + Wakefield Research, 2022 (300 data professionals)", "About 40% of time spent checking or fixing data quality; about 4 hours to notice an incident and 9 to fix it.",
     "Vendor of data observability; self-reported. Close to our 'year of running' picture, where quality and reruns are the biggest shares."),
    ("dbt Labs, State of Analytics Engineering 2024 (456 people)", "55% name maintaining or organising data sets as a top task; 26% maintaining platforms or infrastructure.",
     "Vendor survey; 'top task', not a share of hours. Says the same thing: keeping existing data right beats building new."),
]

QUESTIONS = [
    "For your last source, how many weeks passed before you could say what one row means? Who answered, and where is the answer written now?",
    "Which report do your numbers have to match, within what tolerance, and who signed that off?",
    "Is there one named owner for each important definition, or does the engineer decide?",
    "How many hours last month went to reruns and fixes caused by a source change nobody announced?",
    "If your best engineer left tomorrow, which source meanings would leave with them?",
]

QA = [
    ("What do data engineers spend most of their time on?",
     "In our experience, understanding what the source data means: what a row is, the keys, the status codes, how deletes and dates work, how tables join. In a first build that is roughly a quarter to a third of the hours, more than writing code. Once a pipeline runs, fixing data quality problems and reruns take over, and many of those trace back to source meaning that changed or was misread."),
    ("Is the '80% of time is cleaning data' figure true?",
     "It is folklore from data science surveys and rarely sourced well. Public surveys of data teams land nearer 40% on data quality work. The point stands: most hours go to making data right and understood, not to writing new pipelines."),
    ("How do I reduce the non-technical work as a data engineer?",
     "Move it earlier and to the right person. Ask the source questions before coding, get access requested on day one, have a business owner sign off definitions and the reconciliation target, and write every answer down where the next person will find it. The work does not vanish, but it is done once instead of rediscovered."),
    ("Can AI understand source semantics for me?",
     "It can profile data, read documentation and draft good questions quickly. It cannot know that status 'C' means Cancelled in this one system unless someone wrote it down. Use it to prepare; let a person who knows confirm."),
    ("Are these percentages measured?",
     "No. They are a rounded field estimate from many data platform projects, shown to start a conversation. Measure your own: tag a month of your team's hours with these ten activities."),
]

SOURCES = [
    ("Monte Carlo survey: data engineers spend 40% of their workday on bad data (BigDATAwire, 2022)", "https://www.hpcwire.com/bigdatawire/2022/08/12/monte-carlo-survey-finds-data-engineers-spend-40-of-their-workday-on-bad-data/"),
    ("Data Engineers and Bad Data Survey (TDWI, 2022)", "https://tdwi.org/articles/2022/08/09/data-engineers-and-bad-data-survey.aspx"),
    ("Data downtime nearly doubled, Monte Carlo 2023 (Business Wire)", "https://www.businesswire.com/news/home/20230502005377/en/Data-Downtime-Nearly-Doubled-Year-Over-Year-Monte-Carlo-Survey-Says"),
    ("dbt Labs, State of Analytics Engineering 2024", "https://www.getdbt.com/resources/state-of-analytics-engineering-2024"),
]


def fig(svg, cap):
    return f'<div class="fig">{svg}<p>{E(cap)}</p></div>'


def page():
    url = f"{SITE}{URL_PATH}"
    data_table = C.table(["Activity", "Kind", "First build", "A year of running", "What it is"], TABLE_ROWS)
    nontech = ('<div class="tw"><table class="t"><tr><th>Non-technical chore</th><th>Why it eats the engineer\'s time</th><th>How to cut it</th><th>Who should own it</th><th>Verdict</th></tr>'
               + "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td>{E(c)}</td><td>{E(d)}</td><td><b>{E(v)}</b></td></tr>" for a, b, c, d, v in NONTECH)
               + "</table></div>")
    surveys = C.table(["Survey", "What it found", "How to read it"], SURVEYS)
    qs = "".join(f"<li>{E(q)}</li>" for q in QUESTIONS)
    src = "".join(f'<li><a href="{u}">{E(n)}</a></li>' for n, u in SOURCES)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/data-engineering/">Data engineering</a> › Where the time goes</p>
<p class="eyebrow" style="margin-top:22px">Data engineering · free guide · one page</p>
<h1>{E(TITLE)}</h1>
<p class="lede">Ask someone what a data engineer does and they say "writes pipelines". Watch one for a month and you see something else: most hours go to finding out what the source data means, chasing people, and making numbers match. This page shows where the time goes, why the meaning of source data sits at the root of it, and how to win the non-technical hours back.</p>
<div class="tf">
<div class="stat">
<div><b>~28%</b><span>of a first build goes to understanding what the source data means. The biggest single share.</span></div>
<div><b>~12%</b><span>goes to writing the pipeline code: the part on the plan.</span></div>
<div><b>~60%</b><span>of a first build is non-technical work: meaning, definitions, access, reconciling, meetings.</span></div>
</div>
<div class="box"><b>Read this first:</b> the numbers are a rounded field estimate from many data platform projects, not a measured study. Two public surveys are quoted below for comparison. Use the picture to start a conversation in your team, then measure your own.</div>

<section id="iceberg"><p class="eyebrow">In one picture</p><h2>Code is the tip of the iceberg</h2>
<p>A project plan lists the things you can see: ingest, transform, test, deploy. Underneath sits the work nobody plans for, and it is bigger.</p>
{fig(drawing_iceberg(), "What gets planned sits above the water. What takes the time sits below it.")}</section>

<section id="build"><p class="eyebrow">The first build</p><h2>Where the hours go when you onboard a source</h2>
<p>Take one new source, say an order system, from first meeting to first trusted gold table: usually three to six months. Here is how the hours split.</p>
{fig(chart_build(), "Understanding what the source data means takes more than twice the hours of writing the code.")}
<p>Why is meaning so expensive? Because the answers are rarely written anywhere. Which column is the real key? Does a cancelled order disappear or get a status? Is <code>updated_at</code> set by every change or only some? Which of the three date columns is the business date? Each answer needs a person, and each wrong guess is found late, when the numbers are already in front of a user.</p></section>

<section id="run"><p class="eyebrow">After go-live</p><h2>A year of running looks different</h2>
{fig(chart_build_vs_run(), "Once the pipeline runs, fixing bad data and reruns take the most hours. Hover a bar for its value.")}
<p>Meaning work drops once the source is learnt, but quality fixes and reruns grow to two fifths of the time. Look at why they happen: a source team re-codes a status, adds a column, starts sending deletes differently, back-dates a correction. Those are <b>changes in meaning</b> that nobody announced. The technical-looking work is mostly meaning work arriving late.</p>
<details><summary>Show the numbers as a table</summary>{data_table}</details></section>

<section id="root"><p class="eyebrow">Why meaning is the root</p><h2>One misread code, two weeks of work</h2>
<p>Most of the expensive hours on this page trace back to one small misunderstanding about the source. Here is a real-shaped example.</p>
{fig(drawing_chain(), "Reconciling, reworking and firefighting are often the bill for one question not asked early.")}
<p>So the cheapest hour on any project is the one spent asking the source team the right questions before the first line of code. That is what the <a href="/learn/data-systems/upstreams/">upstream questions</a> and the <a href="/learn/data-systems/upstreams/questionnaire/">source questionnaire</a> are for.</p></section>

<section id="surveys"><p class="eyebrow">Others' numbers</p><h2>What public surveys say</h2>{surveys}
<p>Both are run by vendors who sell a fix, and both count different things from ours. They agree on the shape: keeping existing data correct and understood takes more time than building new pipelines.</p></section>

<section id="nontech"><p class="eyebrow">The non-technical work</p><h2>The non-technical work, and how to cut it</h2>
<p>A data engineer cannot avoid non-technical work entirely; understanding the business data is part of the job. What you can avoid is doing it <b>late</b>, doing it <b>again</b>, and doing it <b>alone</b>. Three moves cover almost everything:</p>
<ol><li><b>Earlier.</b> Ask before coding, request access on day one, agree the reconciliation target before building.</li>
<li><b>Once.</b> Write every answer where the next person will find it: in the metadata store next to the column, and in the semantic layer for definitions.</li>
<li><b>By the right person.</b> Chasing people, chairing meetings and settling definitions belong to an analyst, a technical anchor or the business owner. The engineer builds from written answers.</li></ol>
{fig(drawing_who(), "Hand each kind of work to the person whose job it is. The engineer is not the default for all of it.")}
{nontech}
<p>For the people side in depth, see <a href="/how-we-work/">How we work</a> and the <a href="/learn/technical-anchor/">technical anchor</a> role, who owns discovery so engineers don't have to.</p></section>

<section id="check"><p class="eyebrow">Your turn</p><h2>Five questions for your own team</h2><ol>{qs}</ol></section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(QA)}</section>
<section id="sources"><p class="eyebrow">Sources</p><h2>Checked against</h2><ul>{src}</ul></section>
<section id="next"><p class="eyebrow">Related</p><h2>Where it connects</h2>
<p><a href="/learn/data-systems/upstreams/">Upstreams: know your sources</a> · <a href="/learn/data-systems/upstreams/questionnaire/">Source system questionnaire</a> · <a href="/learn/data-platform-architecture/metadata-store/">The metadata store</a> · <a href="/learn/metric-views/">Metric views</a> · <a href="/learn/technical-anchor/">Technical anchor</a> · <a href="/how-we-work/">How we work</a> · <a href="/data-engineering/">All data engineering</a></p></section>
</div>"""
    crumbs = [("Data engineering", f"{SITE}/data-engineering/"), ("Where the time goes", url)]
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": TITLE, "description": DESC, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in QA]}]
    head = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(TITLE, DESC, url, body, head)


def main():
    out = ROOT / "learn" / "where-data-engineering-time-goes"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("de time ->", out / "index.html")


if __name__ == "__main__":
    main()
