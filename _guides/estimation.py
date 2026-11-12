"""Estimation mistakes in data projects: one page at /how-we-work/estimation/.

    python3 _guides/estimation.py      (then python3 _site/nav.py and python3 _site/seo.py)

Teach first: why data estimates go wrong (the code is estimated, the source is unknown), effort vs
calendar time, the cone of uncertainty. Then twelve mistakes with how to avoid each, ways to estimate
with verdicts, sizing by source complexity, and one worked estimate drawn as range bars (what is
usually in the estimate vs what is usually forgotten). Figures are field estimates, labelled so.
Reuses de_time.py's CSS, figure helper and validated chart colours.
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

wb = C.wb
SITE = wb.SITE
URL_PATH = "/how-we-work/estimation/"
DATE = "2026-11-12"
TITLE = "Estimation mistakes in data projects, and how to avoid them"
DESC = ("Why data project estimates come in two to three times too low: estimating code instead of understanding, "
        "unknown sources, forgotten reconciliation, access waits and backfills. Twelve mistakes, sizing by source, a worked estimate.")
BLUE, MINT, BUTTER, ROSE, LAV = DT.BLUE, DT.MINT, DT.BUTTER, DT.ROSE, DT.LAV
IN_C, OUT_C = DT.BUILD_C, DT.RUN_C


def drawing_effort_calendar():
    d = f'<svg viewBox="0 0 1000 260" role="img" aria-label="Two timelines for the same work. Top, effort: ten days of an engineer actually working, drawn as a short bar. Bottom, calendar: the same ten days of work spread over six weeks, broken by gaps labelled waiting for access, waiting for the source team to answer, waiting for sign-off.">{DT.ARROW}'
    d += '<text x="20" y="40" font-size="17">effort</text><text x="20" y="150" font-size="17">calendar</text>'
    d += f'<rect x="140" y="20" width="240" height="34" rx="6" fill="{BLUE}" stroke="#111" stroke-width="1.5"/><text x="260" y="43" text-anchor="middle" font-size="14.5">10 days of real work</text>'
    segs = [(140, 70, "work"), (210, 150, "waiting for access"), (360, 60, "work"), (420, 190, "waiting for answers"), (610, 80, "work"), (690, 150, "waiting for sign-off"), (840, 30, "work")]
    for x, w, lab in segs:
        if lab == "work":
            d += f'<rect x="{x}" y="128" width="{w}" height="34" rx="6" fill="{BLUE}" stroke="#111" stroke-width="1.5"/>'
        else:
            d += f'<rect x="{x}" y="128" width="{w}" height="34" rx="6" fill="#fff" stroke="#111" stroke-width="1.5" stroke-dasharray="5 4"/><text x="{x + w / 2}" y="150" text-anchor="middle" font-size="13.5">{lab}</text>'
    d += '<path d="M140,190 L870,190" stroke="#111" stroke-width="1.4" fill="none" marker-end="url(#dta)"/><text x="505" y="214" text-anchor="middle" font-size="14.5">six weeks</text>'
    d += '<text x="500" y="248" text-anchor="middle" font-size="14.5">estimate effort and calendar separately; waiting costs time, not effort</text>'
    return d + "</svg>"


def drawing_cone():
    stages = ["idea", "after discovery", "one source end to end", "half the sources", "all live"]
    widths = [240, 160, 96, 52, 16]   # illustrative spread
    d = '<svg viewBox="0 0 1000 330" role="img" aria-label="The cone of uncertainty, drawn as a funnel lying on its side. At the idea stage the range of likely effort is very wide. It narrows after discovery, narrows a lot after one source runs end to end, more at half the sources, and is almost a single number when everything is live. Illustrative widths, not measured.">'
    cx0, step, mid = 110, 200, 165
    top = " ".join(f"{cx0 + i * step},{mid - w / 2}" for i, w in enumerate(widths))
    bot = " ".join(f"{cx0 + i * step},{mid + w / 2}" for i, w in reversed(list(enumerate(widths))))
    d += f'<polygon points="{top} {bot}" fill="{BUTTER}" stroke="#111" stroke-width="1.5"/>'
    d += f'<line x1="{cx0 - 20}" y1="{mid}" x2="{cx0 + 4 * step + 20}" y2="{mid}" stroke="#111" stroke-width="1" stroke-dasharray="4 5"/>'
    for i, s in enumerate(stages):
        x = cx0 + i * step
        d += f'<line x1="{x}" y1="{mid - widths[i] / 2}" x2="{x}" y2="{mid + widths[i] / 2}" stroke="#111" stroke-width="1.3"/>'
        d += f'<text x="{x}" y="316" text-anchor="middle" font-size="14.5">{s}</text>'
    d += f'<text x="{cx0 + 4 * step + 30}" y="{mid + 5}" font-size="14">actual</text>'
    d += '<text x="500" y="20" text-anchor="middle" font-size="15">how wide the honest range is, as the project learns (illustrative)</text>'
    return d + "</svg>"


# item, low days, high days, usually in the estimate?
WORKED = [
    ("Discovery: what the source data means", 12, 18, False),
    ("Access and environment setup (effort only)", 2, 3, False),
    ("Ingestion to bronze", 4, 6, True),
    ("Bronze to silver, with SCD2 history", 8, 12, True),
    ("Gold tables and metric definitions", 6, 10, True),
    ("Tests: unit, contract, reconciliation checks", 6, 9, False),
    ("Reconciling with finance and fixing", 8, 14, False),
    ("Loading history (backfill)", 3, 5, False),
    ("Deploy, CI/CD, monitoring, runbook", 4, 6, False),
    ("Support after go-live (first 4 weeks)", 5, 8, False),
]
LOW, HIGH = sum(w[1] for w in WORKED), sum(w[2] for w in WORKED)
CODE_LOW, CODE_HIGH = sum(w[1] for w in WORKED if w[3]), sum(w[2] for w in WORKED if w[3])


def chart_worked():
    x0, scale, h, gap = 380, 26, 22, 12
    y = 66
    d = f'<svg viewBox="0 0 1000 {y + len(WORKED) * (h + gap) + 40}" role="img" aria-label="Range bars for a worked estimate of one medium source, in person-days. Usually in the estimate: ingestion 4 to 6, bronze to silver 8 to 12, gold 6 to 10. Usually forgotten: discovery 12 to 18, access setup 2 to 3, tests 6 to 9, reconciliation 8 to 14, backfill 3 to 5, deployment and monitoring 4 to 6, support after go-live 5 to 8. Total {LOW} to {HIGH} days; the usual code-only estimate is {CODE_LOW} to {CODE_HIGH}.">'
    d += f'<defs>{DT._hatch("esh", OUT_C)}</defs>'
    d += '<text x="20" y="24" font-size="16">Worked estimate, one medium source, person-days (low to high)</text>'
    d += f'<rect x="{x0}" y="36" width="18" height="14" rx="3" fill="{IN_C}" stroke="#111" stroke-width="1.2"/><text x="{x0 + 26}" y="48" font-size="14.5">usually in the estimate</text>'
    d += f'<rect x="{x0 + 210}" y="36" width="18" height="14" rx="3" fill="url(#esh)" stroke="#111" stroke-width="1.2"/><text x="{x0 + 236}" y="48" font-size="14.5">usually forgotten</text>'
    for label, lo, hi, inside in WORKED:
        fill = IN_C if inside else "url(#esh)"
        d += f'<text x="{x0 - 12}" y="{y + 16}" text-anchor="end" font-size="14.5">{E(label)}</text>'
        d += f'<line x1="{x0}" y1="{y + h / 2}" x2="{x0 + lo * scale}" y2="{y + h / 2}" stroke="#bbb" stroke-width="1" stroke-dasharray="2 4"/>'
        d += (f'<rect class="bar" x="{x0 + lo * scale}" y="{y}" width="{(hi - lo) * scale}" height="{h}" rx="4" fill="{fill}" stroke="#111" stroke-width="1.4">'
              f'<title>{E(label)}: {lo} to {hi} person-days</title></rect>')
        d += f'<text x="{x0 + hi * scale + 8}" y="{y + 16}" font-size="13.5">{lo}–{hi}</text>'
        y += h + gap
    d += f'<line x1="{x0}" y1="60" x2="{x0}" y2="{y}" stroke="#111" stroke-width="1"/>'
    for t in (0, 5, 10, 15, 20):
        d += f'<text x="{x0 + t * scale}" y="{y + 18}" text-anchor="middle" font-size="12.5" fill="#555">{t}</text>'
    return d + "</svg>"


# mistake, what happens, how to avoid it
MISTAKES = [
    ("Estimating the code, not the understanding",
     "The estimate covers ingestion and transforms. Understanding the source, which takes more hours than code, is missing.",
     "Make discovery and source meaning their own line items. See where data engineering time goes."),
    ("Estimating a source nobody has looked at",
     "A number is given from the source's name ('it's just SAP'). The surprises arrive after commitment.",
     "Give a wide range at idea stage and a firm one only after a time-boxed look at the real data and docs."),
    ("One number instead of a range",
     "'Eight weeks' becomes a promise. Every unknown later reads as a slip.",
     "Always a range with the assumptions it rests on, and the event that will narrow it (for example, after the first source runs end to end)."),
    ("Effort and calendar mixed up",
     "Ten days of work is planned as two weeks, then access, answers and sign-offs stretch it to six.",
     "Estimate effort, then add waits separately. Start access and questions on day one."),
    ("Only the happy path",
     "Late files, duplicates, deletes, corrections and schema changes are not in any line item.",
     "For each source, list how it fails and budget handling, quarantine and tests for each."),
    ("Reconciliation left out",
     "Numbers are expected to match the old report on the first try. They never do.",
     "Put reconciliation with the business, and the fixes it causes, in as a line item with an owner and a tolerance."),
    ("History forgotten",
     "The pipeline handles today's data; loading five years of history, with its old formats, is found later.",
     "Ask how far back the data must go and estimate the backfill on its own."),
    ("Environments and deployment free",
     "Dev works; test, production, CI/CD, secrets and permissions take another two weeks.",
     "Estimate the path to production for the first source; later sources reuse it."),
    ("Every source the same size",
     "Twenty sources times one average gives a neat number that is wrong for the three hard ones.",
     "Size each source by complexity signals (keys, change column, docs, owner, volume) and estimate per size."),
    ("Nothing for running it",
     "The estimate ends at go-live; support, reruns and cost tuning in the first weeks come out of the next project.",
     "Add a support period after go-live and say who runs it after that."),
    ("The estimator is not the doer",
     "A lead or salesperson estimates; the engineers who know the traps never see the number.",
     "The people who build it estimate it, with someone who has done a similar source checking it."),
    ("Never re-estimating",
     "The first guess stays the plan until the deadline is missed.",
     "Re-estimate at each gate (after discovery, after the first source) and tell people the new range straight away."),
]

# way to estimate, how it works, verdict
METHODS = [
    ("Gut feel, one number", "Someone senior says a number in a meeting.", "Drop: no assumptions to check, no way to narrow it"),
    ("Task list, bottom up", "List every task and add the days.", "Pursue with care: good once the source is known, but misses what nobody thought to list"),
    ("Size by source complexity", "Put each source in a size (small to very large) by its signals, use an effort range per size.", "Pursue: the main method for many sources"),
    ("Compare with past projects", "Look at how long similar sources really took last time, not how long they were estimated.", "Pursue: the best check on any estimate; start keeping the records now"),
    ("Time-boxed look first", "Spend two to five days on the real data and docs, then estimate.", "Pursue: cheap, and removes the biggest unknowns"),
    ("Fixed price before discovery", "Commit to a cost before anyone has seen the data.", "Drop, or split: fix the price of discovery only, then estimate the rest"),
]

# size, signals, first build effort (person-weeks)
SIZES = [
    ("Small", "A few tables, clear keys, a reliable change column, docs exist, owner answers within a day", "1 to 2"),
    ("Medium", "Ten to thirty tables, some joins to learn, deletes need care, some docs, owner busy", "3 to 5"),
    ("Large", "Many tables or a packaged app (ERP, CRM), codes that need lookup, no change column, history in odd formats", "6 to 10"),
    ("Very large", "Several systems feeding one model, conflicting definitions, streaming plus batch, no reachable owner", "10 to 20, split it"),
]

QUESTIONS = [
    "Does your estimate have a line for understanding the source data, and is it bigger than the code line?",
    "Is it a range, and does it say what event will narrow the range?",
    "Are waits (access, answers, sign-off) shown apart from effort?",
    "Is reconciliation in, with a tolerance and someone to sign it off?",
    "Did the people who will build it make the estimate?",
]

QA = [
    ("Why are data project estimates usually too low?",
     "Because people estimate the code they can picture, and the code is the smallest part. Understanding source data, reconciling numbers, waiting for access, loading history and support after go-live are left out. In our worked example the usual code-only estimate is about a third of the honest one."),
    ("How do you estimate a data migration or a new source?",
     "Spend a few days looking at the real data and documents first. Size each source by its signals: number of tables, whether keys and a change column exist, whether docs and an owner are available. Use a range per size, add reconciliation, backfill and support, and show waits apart from effort."),
    ("Should a data project estimate be a range?",
     "Yes. A single number hides the unknowns and becomes a promise. Give a range, the assumptions behind it, and the point at which you will narrow it, usually after the first source runs end to end."),
    ("How much contingency should a data project have?",
     "Rather than a flat percentage on top, put the usually forgotten items in as real line items. Then keep a contingency for the sources you have not looked at yet, and shrink it as you look."),
    ("Are the numbers on this page measured?",
     "No. They are rounded field estimates from data platform projects, to show the shape. Your own past projects are the best source: record how long each source really took."),
]


def page():
    url = f"{SITE}{URL_PATH}"
    mist = C.table(["Mistake", "What happens", "How to avoid it"], MISTAKES)
    methods = ('<div class="tw"><table class="t"><tr><th>Way to estimate</th><th>How it works</th><th>Verdict</th></tr>'
               + "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td><b>{E(c)}</b></td></tr>" for a, b, c in METHODS) + "</table></div>")
    sizes = C.table(["Source size", "Signals", "First build, person-weeks"], SIZES)
    worked = C.table(["Line item", "Low (days)", "High (days)", "Usually in the estimate?"],
                     [(a, str(b), str(c), "yes" if d else "no, usually forgotten") for a, b, c, d in WORKED] + [("Total", str(LOW), str(HIGH), "")])
    qs = "".join(f"<li>{E(q)}</li>" for q in QUESTIONS)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/how-we-work/">How we work</a> › Estimation mistakes</p>
<p class="eyebrow" style="margin-top:22px">How we work · free guide · one page</p>
<h1>{E(TITLE)}</h1>
<p class="lede">Data projects are famous for running late. Usually the team did not work slowly; the estimate left out most of the work. This page shows why data estimates come in too low, the twelve mistakes we see most, and a way to estimate that holds up.</p>
<div class="tf">
<div class="stat">
<div><b>{CODE_LOW}–{CODE_HIGH}</b><span>person-days: the usual code-only estimate for one medium source.</span></div>
<div><b>{LOW}–{HIGH}</b><span>person-days: the same source with everything in. About three times as much.</span></div>
<div><b>6 weeks</b><span>of calendar for 10 days of work, once waits are counted.</span></div>
</div>
<div class="box"><b>Read this first:</b> the figures are rounded field estimates from data platform projects, there to show the shape, not a measured study. Your own past projects are the best numbers you have.</div>

<section id="why"><p class="eyebrow">In plain words</p><h2>Why data estimates go wrong</h2>
<p>In most software work, you can see the thing you are building. In data work, the hardest part is something you have not seen yet: the source data and what it means. Until someone has looked at it, every estimate is a guess about a stranger. And the part people can picture, the code, is the smallest part of the job; we show that on <a href="/learn/where-data-engineering-time-goes/">where data engineering time goes</a>.</p>
<p>Two more things make it worse. Effort and calendar time are different: a lot of a data project is waiting for someone else. And the honest range is wide at the start and narrows only as you learn.</p>
{DT.fig(drawing_effort_calendar(), "Ten days of work can take six weeks. Plan the waits, and start them early.")}
{DT.fig(drawing_cone(), "An honest estimate starts wide and narrows at each step. Promising a single number at the idea stage is promising a guess.")}</section>

<section id="mistakes"><p class="eyebrow">The mistakes</p><h2>Twelve estimation mistakes and how to avoid them</h2>{mist}</section>

<section id="worked"><p class="eyebrow">A worked estimate</p><h2>One medium source, estimated honestly</h2>
<p>An order system: about twelve tables, a daily batch, history kept with SCD2, a few gold tables and one dashboard that must match the finance report. The solid bars are what a code-only estimate covers. The striped bars are what usually gets forgotten.</p>
{DT.fig(chart_worked(), "Each bar runs from the low to the high estimate. Hover a bar for its range.")}
<details><summary>Show the numbers as a table</summary>{worked}</details>
<p>The code-only estimate says {CODE_LOW} to {CODE_HIGH} days. The honest one says {LOW} to {HIGH} days, roughly {round(LOW / 5)} to {round(HIGH / 5)} person-weeks, plus the waits for access and answers on the calendar. Nobody worked slowly; the first number just left most of the work out.</p></section>

<section id="sizes"><p class="eyebrow">Many sources</p><h2>Size each source before you add them up</h2>
<p>Twenty sources are never twenty copies of an average source. Put each one in a size by what you can see about it, then use a range per size.</p>{sizes}</section>

<section id="methods"><p class="eyebrow">Choosing</p><h2>Ways to estimate, with verdicts</h2>{methods}
<div class="box"><b>How to hand an estimate over:</b> a range, the assumptions behind it, the items that are usually forgotten shown on their own lines, the waits shown apart from effort, and the date you will re-estimate.</div></section>

<section id="check"><p class="eyebrow">Your turn</p><h2>Five questions for your next estimate</h2><ol>{qs}</ol></section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(QA)}</section>
<section id="next"><p class="eyebrow">Related</p><h2>Where it connects</h2>
<p><a href="/learn/where-data-engineering-time-goes/">Where data engineering time goes</a> · <a href="/how-we-work/project-management-mistakes/">Project management mistakes</a> · <a href="/how-we-work/critical-thinking/">Critical thinking in data projects</a> · <a href="/learn/technical-anchor/discovery/">Discovery</a> · <a href="/learn/data-systems/upstreams/questionnaire/">Source system questionnaire</a> · <a href="/how-we-work/">How we work</a></p></section>
</div>"""
    crumbs = [("How we work", f"{SITE}/how-we-work/"), ("Estimation mistakes", url)]
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": TITLE, "description": DESC, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in QA]}]
    head = DT.CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(TITLE, DESC, url, body, head)


def main():
    out = ROOT / "how-we-work" / "estimation"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("estimation ->", out / "index.html")


if __name__ == "__main__":
    main()
