"""Critical thinking in data projects: one page at /how-we-work/critical-thinking/.

    python3 _guides/critical_thinking.py      (then python3 _site/nav.py and python3 _site/seo.py)

Teach first: what critical thinking means here (check a claim before you build on it), the five
questions drawn as cards, where claims hide at each project stage, traps with numbers (averages,
survivorship, correlation, Simpson's paradox with a worked tyre-returns table, denominators, vendor
benchmarks, "the doc says"), three worked stories, team habits with verdicts, and using AI critically.
Reuses de_time.py for CSS, fig() and the drawing palette. No statistics are quoted; the Simpson's
paradox numbers are a made-up teaching example, labelled so.
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
URL_PATH = "/how-we-work/critical-thinking/"
DATE = "2026-11-12"
TITLE = "Critical thinking in data projects: five questions for every claim"
DESC = ("How to apply critical thinking in data projects: five questions for any claim, number or design; where claims hide "
        "from discovery to running; traps with numbers like averages, survivorship and Simpson's paradox; team habits and AI answers.")

BLUE, MINT, BUTTER, ROSE, LAV = DT.BLUE, DT.MINT, DT.BUTTER, DT.ROSE, DT.LAV
ARROW = DT.ARROW
fig = DT.fig

FIVE = [
    ("1", "What exactly", "is claimed?", BUTTER),
    ("2", "What is the", "evidence?", BLUE),
    ("3", "What else", "could explain it?", MINT),
    ("4", "What would", "prove it wrong?", ROSE),
    ("5", "What does it cost", "if we are wrong?", LAV),
]


def drawing_five():
    d = ('<svg viewBox="0 0 1000 250" role="img" aria-label="Five cards, one per question. One: what exactly is claimed? '
         'Two: what is the evidence? Three: what else could explain it? Four: what would prove it wrong? '
         'Five: what does it cost if we are wrong? Each card has a small picture: a speech bubble, a magnifying glass, '
         'a fork in the road, a hammer, and a price tag.">')
    for i, (n, a, b, fill) in enumerate(FIVE):
        x = 10 + i * 198
        d += f'<rect x="{x}" y="14" width="182" height="222" rx="14" fill="#fff" stroke="#111" stroke-width="1.5"/>'
        d += f'<rect x="{x}" y="14" width="182" height="44" rx="14" fill="{fill}" stroke="#111" stroke-width="1.5"/>'
        d += f'<text x="{x + 91}" y="44" text-anchor="middle" font-size="22">{n}</text>'
        cx, cy = x + 91, 112
        if n == "1":   # speech bubble
            d += f'<path d="M{cx - 44},{cy - 26} h88 a10,10 0 0 1 10,10 v32 a10,10 0 0 1 -10,10 h-56 l-16,16 v-16 h-16 a10,10 0 0 1 -10,-10 v-32 a10,10 0 0 1 10,-10 z" fill="{BUTTER}" stroke="#111" stroke-width="1.5"/>'
            d += f'<text x="{cx}" y="{cy + 2}" text-anchor="middle" font-size="15">"it is clean"</text>'
        elif n == "2":  # magnifier
            d += f'<circle cx="{cx - 8}" cy="{cy - 6}" r="24" fill="{BLUE}" stroke="#111" stroke-width="1.6"/>'
            d += f'<line x1="{cx + 10}" y1="{cy + 12}" x2="{cx + 34}" y2="{cy + 36}" stroke="#111" stroke-width="4" stroke-linecap="round"/>'
        elif n == "3":  # fork in the road
            d += f'<path d="M{cx},{cy + 36} L{cx},{cy} L{cx - 36},{cy - 30} M{cx},{cy} L{cx + 36},{cy - 30}" fill="none" stroke="#111" stroke-width="3" stroke-linecap="round"/>'
            d += f'<circle cx="{cx - 36}" cy="{cy - 30}" r="7" fill="{MINT}" stroke="#111" stroke-width="1.4"/><circle cx="{cx + 36}" cy="{cy - 30}" r="7" fill="{MINT}" stroke="#111" stroke-width="1.4"/>'
        elif n == "4":  # hammer
            d += f'<rect x="{cx - 30}" y="{cy - 32}" width="60" height="22" rx="4" fill="{ROSE}" stroke="#111" stroke-width="1.5"/>'
            d += f'<rect x="{cx - 5}" y="{cy - 10}" width="10" height="48" rx="3" fill="#fff" stroke="#111" stroke-width="1.5"/>'
        else:           # price tag
            d += f'<path d="M{cx - 34},{cy - 22} h48 l22,22 l-22,22 h-48 z" fill="{LAV}" stroke="#111" stroke-width="1.5"/>'
            d += f'<circle cx="{cx + 16}" cy="{cy}" r="4" fill="#fff" stroke="#111" stroke-width="1.3"/><text x="{cx - 12}" y="{cy + 6}" text-anchor="middle" font-size="18">$</text>'
        d += f'<text x="{x + 91}" y="190" text-anchor="middle" font-size="16">{a}</text>'
        d += f'<text x="{x + 91}" y="214" text-anchor="middle" font-size="16">{b}</text>'
    return d + "</svg>"


def drawing_average():
    """Dot strip: most loads take 2-3 minutes, a few take 30; the average of 6 describes none of them."""
    import random
    rnd = random.Random(7)
    vals = [round(rnd.uniform(1.6, 3.4), 1) for _ in range(26)] + [28, 31, 34]
    avg = sum(vals) / len(vals)
    x0, sc = 60, 25
    d = (f'<svg viewBox="0 0 1000 220" role="img" aria-label="A strip of dots showing 29 nightly load times in minutes. '
         f'Twenty-six dots crowd between 2 and 3 minutes; three dots sit far right near 30 minutes. A dashed line marks the average, '
         f'about {avg:.0f} minutes, where there are no dots at all. The average describes no real night.">{ARROW}')
    d += f'<line x1="{x0}" y1="140" x2="{x0 + 36 * sc}" y2="140" stroke="#111" stroke-width="1.4"/>'
    for t in (0, 5, 10, 15, 20, 25, 30, 35):
        d += f'<line x1="{x0 + t * sc}" y1="136" x2="{x0 + t * sc}" y2="146" stroke="#111" stroke-width="1"/><text x="{x0 + t * sc}" y="166" text-anchor="middle" font-size="14">{t}</text>'
    d += f'<text x="{x0 + 18 * sc}" y="192" text-anchor="middle" font-size="14">minutes per nightly load</text>'
    seen = {}
    for v in vals:
        k = round(v * 4) / 4
        seen[k] = seen.get(k, 0) + 1
        d += f'<circle cx="{x0 + v * sc}" cy="{129 - (seen[k] - 1) * 11}" r="5" fill="{DT.BUILD_C}" stroke="#111" stroke-width="1.2"/>'
    ax = x0 + avg * sc
    d += f'<line x1="{ax}" y1="40" x2="{ax}" y2="140" stroke="#111" stroke-width="1.5" stroke-dasharray="5 4"/>'
    d += f'<text x="{ax + 10}" y="46" font-size="15">average: {avg:.0f} minutes</text><text x="{ax + 10}" y="66" font-size="14">no real night looks like this</text>'
    d += f'<text x="{x0 + 31 * sc}" y="92" text-anchor="middle" font-size="14">three bad nights</text>'
    d += f'<text x="{x0 + 1.3 * sc}" y="112" text-anchor="end" font-size="14">most nights</text>'
    return d + "</svg>"


# plant, tyre, sold, returned
SIMPSON = [("Plant A", "Car", 900, 18), ("Plant A", "Truck", 100, 8),
           ("Plant B", "Car", 200, 3), ("Plant B", "Truck", 800, 56)]


def _rate(r, s):
    return 100 * r / s


def drawing_simpson():
    groups = [("Car tyres", [("A", 900, 18), ("B", 200, 3)]),
              ("Truck tyres", [("A", 100, 8), ("B", 800, 56)]),
              ("All tyres", [("A", 1000, 26), ("B", 1000, 59)])]
    d = ('<svg viewBox="0 0 1000 300" role="img" aria-label="Return rates for two tyre plants. Car tyres: Plant A 2.0 percent, '
         'Plant B 1.5 percent, so B is better. Truck tyres: Plant A 8.0 percent, Plant B 7.0 percent, so B is better again. '
         'All tyres together: Plant A 2.6 percent, Plant B 5.9 percent, so B looks worse, only because B makes mostly truck tyres, '
         'which are returned more often.">')
    base, sc = 240, 22
    for gi, (g, bars) in enumerate(groups):
        gx = 60 + gi * 320
        for bi, (p, s, r) in enumerate(bars):
            rate = _rate(r, s)
            h = rate * sc
            x = gx + bi * 100
            fill = BUTTER if p == "A" else BLUE
            d += f'<rect x="{x}" y="{base - h}" width="70" height="{h}" rx="4" fill="{fill}" stroke="#111" stroke-width="1.5"/>'
            d += f'<text x="{x + 35}" y="{base - h - 8}" text-anchor="middle" font-size="15">{rate:.1f}%</text>'
            d += f'<text x="{x + 35}" y="{base + 20}" text-anchor="middle" font-size="15">Plant {p}</text>'
        d += f'<text x="{gx + 85}" y="{base + 46}" text-anchor="middle" font-size="16.5">{g}</text>'
        verdict = "B is better" if gi < 2 else "B looks worse"
        d += f'<text x="{gx + 85}" y="28" text-anchor="middle" font-size="15">{verdict}</text>'
    d += f'<line x1="40" y1="{base}" x2="960" y2="{base}" stroke="#111" stroke-width="1.2"/>'
    d += '<line x1="680" y1="20" x2="680" y2="285" stroke="#111" stroke-width="1" stroke-dasharray="3 5"/>'
    return d + "</svg>"


def drawing_labels():
    notes = [("FACT", "measured, with\nthe query linked", MINT, "\"2.1% of order rows\nhave no customer id\""),
             ("ASSUMPTION", "believed, not yet\nchecked; has an owner", BUTTER, "\"the source sends\nevery delete\""),
             ("OPINION", "someone's judgement;\nsay whose", ROSE, "\"Iceberg is the\nbetter format\"")]
    d = ('<svg viewBox="0 0 1000 250" role="img" aria-label="Three sticky notes. Fact, in green: measured, with the query linked, '
         'for example 2.1 percent of order rows have no customer id. Assumption, in yellow: believed but not yet checked, with an owner, '
         'for example the source sends every delete. Opinion, in pink: someone\'s judgement, say whose, for example Iceberg is the better format.">')
    for i, (h, sub, fill, ex) in enumerate(notes):
        x = 40 + i * 320
        rot = (-2, 1.5, -1)[i]
        d += f'<g transform="rotate({rot} {x + 130} 120)">'
        d += f'<path d="M{x},20 h260 v190 l-26,20 h-234 z" fill="{fill}" stroke="#111" stroke-width="1.5"/>'
        d += f'<path d="M{x + 260},210 l-26,0 l0,20" fill="#fff" stroke="#111" stroke-width="1.3"/>'
        d += f'<text x="{x + 130}" y="56" text-anchor="middle" font-size="22">{h}</text>'
        for j, ln in enumerate(sub.split("\n")):
            d += f'<text x="{x + 130}" y="{88 + j * 21}" text-anchor="middle" font-size="14.5">{E(ln)}</text>'
        for j, ln in enumerate(ex.split("\n")):
            d += f'<text x="{x + 130}" y="{158 + j * 22}" text-anchor="middle" font-size="15">{E(ln)}</text>'
        d += "</g>"
    return d + "</svg>"


QUESTIONS5 = [
    ("1. What exactly is being claimed?",
     "Write the claim as one sentence with numbers and a scope. \"The data is clean\" is not a claim anyone can check. "
     "\"Fewer than 0.1% of order rows since January have no customer id\" is. Half of all arguments in a project end here, because people find they meant different things."),
    ("2. What is the evidence, and who measured it?",
     "Ask how the person knows. Did they run a query, read a document, hear it in a meeting, or remember it? Who measured it, on what data, when, and do they gain if it is true? "
     "A vendor's benchmark, a source team's spec and last year's profiling are all evidence, but of different strength."),
    ("3. What else could explain it?",
     "Before accepting a cause, list two other causes that would produce the same numbers. Sales dropped after the release; so did the number of rows loaded, because a file was late. "
     "If you cannot name another explanation, you have not looked yet."),
    ("4. What would prove it wrong, and can we test that cheaply?",
     "Name the observation that would break the claim, then look for it. \"No duplicates\" breaks if one key appears twice: a single GROUP BY finds out in seconds. "
     "Looking for the counter-example is faster and more honest than collecting examples that agree."),
    ("5. What does it cost if we are wrong?",
     "Not every claim deserves a week of checking. If being wrong costs an hour of rework, accept it and move on. If it costs a wrong number in a board report or a regulator's file, check it hard. "
     "Match the effort to the price of the mistake."),
]

# stage, typical claim, the question to ask, cheap check
STAGES = [
    ("Discovery", "\"Users need this data daily.\"", "Who said it, and what decision do they make with it each day?", "Ask for the last three times they needed it and what they did."),
    ("Source onboarding", "\"The key is unique; deletes are flagged.\"", "Says who: the doc, the DBA, or the data?", "Profile a month of data: count keys, look for rows that vanish between loads."),
    ("Design", "\"Streaming is needed; batch is too slow.\"", "Too slow for which decision, by how many minutes?", "Ask what happens today when the number is an hour old."),
    ("Build", "\"This join is correct.\"", "What would a wrong join look like?", "Compare row counts before and after the join; check one known customer by hand."),
    ("Testing", "\"All tests pass.\"", "Would these tests fail if the code were wrong?", "Break the code on purpose once and see whether a test catches it."),
    ("Go-live", "\"Numbers match the old report.\"", "Match on which days, at what tolerance, and what about the days that don't?", "Reconcile a bad month, not just a quiet one."),
    ("Running", "\"The pipeline is healthy; it is green.\"", "Green means it ran. Did it load the right rows?", "Track rows in and rows out per load, not just job status."),
]

TRAPS = [
    ("An average hides the spread", "\"Loads take 5 minutes on average.\" Most take 2 or 3; three nights took about 30. Plan for the 30.", "Look at the spread: the median, the slowest 5%, and a picture of every value."),
    ("Only the survivors were looked at", "\"Every load this month had valid dates.\" The loads that failed were never counted.", "Ask what was excluded, and count the rejected and quarantined rows too."),
    ("Moved together is not caused", "\"The new index made queries faster.\" The cluster was also resized that day.", "Change one thing at a time, or compare against a group that did not change."),
    ("The total disagrees with every part", "Plant B is better for every tyre type, yet worse overall (worked example below).", "Split by the obvious groups before comparing totals."),
    ("The denominator changed", "\"Error rate fell by half.\" The count of records checked doubled when a new source was added.", "Always show both numbers of a rate, and say what was counted."),
    ("The benchmark compared unlike things", "\"Engine X is 5 times faster.\" On a different data size, file layout and warm cache.", "Re-run on your own data shape, same size machines, cold and warm."),
    ("\"The source document says\"", "The document was written for version 3; the system is on version 5.", "Treat documents as claims to test, and date every answer you write down."),
]

HABITS = [
    ("Write the claim and its evidence in the decision log", "Every decision lists the claims it rests on, each marked fact, assumption or opinion, with a link to the query or source.",
     "Pursue", "Cheap, and the next person can check the reasoning instead of guessing it."),
    ("Ask \"how do we know?\" in every review", "One person's job in each design review is to ask it of every key claim.",
     "Pursue", "Turns doubt into a routine, so it never feels personal."),
    ("Pre-mortem before a big build", "Imagine it is six months later and the project failed. Each person writes why. Turn the top reasons into checks.",
     "Pursue", "Finds the risks people were too polite to raise."),
    ("Red-team review for big decisions", "Someone argues the other side on purpose, with evidence.",
     "Pursue for decisions that are hard to undo", "Too slow for small choices; worth it for the platform and the format."),
    ("Test the counter-example first", "Before collecting evidence for a claim, write the one query that would prove it wrong, and run it.",
     "Pursue", "Usually a few minutes, and it catches the most expensive mistakes."),
    ("Check everything to the same depth", "Every claim gets a full investigation.",
     "Drop", "Burns time on cheap mistakes; use question five to choose."),
    ("Trust the most senior voice", "The most experienced person's view settles the question.",
     "Drop", "Experience is evidence, but of one kind; it still has to meet the data."),
]

STORIES = [
    ("\"The source has no duplicates\"",
     "The source team said so in the first meeting, and the design used order_id as the key. Question four asked what would prove it wrong: one order_id twice. "
     "A GROUP BY over three months found 412 keys appearing twice, all on days when the source system was restarted mid-batch. The claim was true for normal days and false on bad ones. "
     "The fix cost one dedupe rule in silver, written before go-live instead of after the first wrong report."),
    ("\"Engine X is 5 times faster\"",
     "A vendor slide showed a query running five times faster on their engine. Question two asked who measured it and on what: the vendor, on a tidy data set ten times smaller than ours, with a warm cache. "
     "Question five asked the cost of being wrong: a platform choice for five years. So the team ran three of its own slowest queries on both engines at the same size and price. The gap was real but smaller, and on one query it went the other way. "
     "The decision was made on our numbers, written in the decision log."),
    ("\"Sales dropped 12% after the release\"",
     "A dashboard showed sales down 12% the day after a pipeline release, and the release was blamed. Question three asked what else could explain it. "
     "Rows loaded were also down 12%: one region's file arrived after the load ran. Sales had not dropped; the data had. The release was fine. "
     "The lasting fix was a freshness check per region, so a late file shows as \"incomplete\" on the dashboard instead of as a fall in sales."),
]

AI = [
    "An answer from an AI assistant is a claim like any other. Ask the same five questions of it.",
    "It writes with the same confidence whether it is right or wrong, so its tone is not evidence.",
    "Ask it for the query, the document or the reasoning behind an answer, then run or read that yourself.",
    "Use it well: to list other explanations (question three), to draft the counter-example query (question four), and to spot claims in a long document.",
    "Never let it fill in what a source system means. It can draft the question; a person who knows answers it.",
]

CHECK = [
    "Pick the three claims your current design rests on most. For each, can you point to the query or document that supports it?",
    "Which of your project's beliefs are still assumptions, and who owns checking each one?",
    "When did a test last fail because the code was wrong, rather than because the environment broke?",
    "Does your pipeline report rows in and rows out per load, or only success and failure?",
    "Which decision in your project would be the most expensive to get wrong, and how hard was it checked?",
]

QA = [
    ("What is critical thinking in a data project?",
     "Checking a claim before you build on it. In practice, asking five questions: what exactly is claimed, what is the evidence, what else could explain it, what would prove it wrong, and what it costs to be wrong."),
    ("Doesn't this slow the project down?",
     "It speeds it up when you match the effort to the cost of being wrong. Most checks are one query or one question. The slow projects are the ones that find a wrong assumption after go-live."),
    ("How do I question a senior person's claim without causing offence?",
     "Make it a routine, not a challenge. If every review asks \"how do we know?\" of every key claim, nobody is singled out. Ask for the evidence, not for their reasons."),
    ("What is Simpson's paradox, simply?",
     "A comparison that holds in every group can reverse when the groups are added together, because the groups are mixed in different amounts. Plant B returns fewer tyres of every type but more overall, because it makes mostly truck tyres, which are returned more often."),
    ("Should I trust a vendor benchmark?",
     "Treat it as a claim made by someone who gains if it is true. Check the data size, file layout, cache and machine size, then re-run your own slowest queries on equal terms before deciding."),
]


def page():
    url = f"{SITE}{URL_PATH}"
    five = "".join(f"<h3>{E(h)}</h3><p>{E(t)}</p>" for h, t in QUESTIONS5)
    stages = C.table(["Stage", "Typical claim", "The question to ask", "A cheap check"], STAGES)
    traps = C.table(["Trap", "What it looks like", "What to do"], TRAPS)
    simpson_rows = [(p, t, f"{s:,}", f"{r}", f"{_rate(r, s):.1f}%") for p, t, s, r in SIMPSON]
    simpson_rows += [("Plant A", "All", "1,000", "26", "2.6%"), ("Plant B", "All", "1,000", "59", "5.9%")]
    simpson = C.table(["Plant", "Tyre type", "Sold", "Returned", "Return rate"], simpson_rows)
    habits = ('<div class="tw"><table class="t"><tr><th>Habit</th><th>What it means</th><th>Verdict</th><th>Why</th></tr>'
              + "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td><b>{E(v)}</b></td><td>{E(w)}</td></tr>" for a, b, v, w in HABITS)
              + "</table></div>")
    stories = "".join(f"<h3>{E(h)}</h3><p>{E(t)}</p>" for h, t in STORIES)
    ai = "".join(f"<li>{E(x)}</li>" for x in AI)
    chk = "".join(f"<li>{E(q)}</li>" for q in CHECK)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/how-we-work/">How we work</a> › Critical thinking</p>
<p class="eyebrow" style="margin-top:22px">How we work · free guide · one page</p>
<h1>{E(TITLE)}</h1>
<p class="lede">A data project runs on claims. The source team says the key is unique. A vendor says their engine is five times faster. A dashboard says sales fell. A requirement says users need it in real time. Critical thinking, here, means one plain thing: check a claim before you build on it. This page gives five questions to ask, shows where claims hide at each stage of a project, and lists the traps numbers set.</p>
<div class="tf">
<div class="box"><b>Why data projects need it more than most:</b> numbers look certain. A figure with two decimal places feels like a fact even when it came from a half-loaded table or a guess in a meeting. And a wrong claim found late costs far more than one found early, because by then reports, people and decisions are built on it.</div>

<section id="five"><p class="eyebrow">The method</p><h2>Five questions for every claim</h2>
<p>You do not need all five every time. Use them as a checklist when a claim matters: when a design, a number in a report, or a promise to a user rests on it.</p>
{fig(drawing_five(), "Five questions. The fifth decides how hard to push on the other four.")}
{five}</section>

<section id="stages"><p class="eyebrow">Where to look</p><h2>Where claims hide in a data project</h2>
<p>Every stage has its favourite claims. Each one below sounds reasonable, and each has gone wrong on real projects. The right-hand column is the cheap check: usually one query or one question.</p>
{stages}</section>

<section id="traps"><p class="eyebrow">Traps with numbers</p><h2>Seven ways numbers mislead</h2>
<p>Numbers do not lie, but they leave things out. These are the traps we meet most often.</p>
{fig(drawing_average(), "Twenty-six quiet nights and three bad ones. The average sits where no night ever was.")}
{traps}
<h3>A worked example: the total that disagrees with every part</h3>
<p>Two plants make car and truck tyres. Management asks which plant has fewer returns. The overall numbers say Plant A, clearly. Split by tyre type and Plant B wins both times. Both statements are true. Plant B makes mostly truck tyres, which come back more often whoever makes them, so its total is dragged up by its mix, not its quality. This is called Simpson's paradox. The numbers are made up to teach the idea.</p>
{fig(drawing_simpson(), "Plant B is better for car tyres and for truck tyres, yet looks worse overall.")}
{simpson}
<p>The lesson for any comparison: before comparing totals, split by the obvious groups (product, region, channel, source system) and check the mix is similar.</p></section>

<section id="stories"><p class="eyebrow">In practice</p><h2>Three claims, checked</h2>{stories}</section>

<section id="habits"><p class="eyebrow">For teams</p><h2>Habits that make it routine</h2>
<p>Critical thinking works best as a team habit, not one sceptical person. Start by labelling what you write down, so everyone can see which parts are known and which are hoped.</p>
{fig(drawing_labels(), "Three labels for anything in a design or decision log. An assumption always has an owner who will check it.")}
{habits}</section>

<section id="ai"><p class="eyebrow">AI answers</p><h2>Using AI critically</h2><ul>{ai}</ul></section>

<section id="check"><p class="eyebrow">Your turn</p><h2>Five questions for your own project</h2><ol>{chk}</ol></section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(QA)}</section>
<section id="next"><p class="eyebrow">Related</p><h2>Where it connects</h2>
<p><a href="/how-we-work/">How we work</a> · <a href="/how-we-work/estimation/">Estimation mistakes in data projects</a> · <a href="/learn/where-data-engineering-time-goes/">Where data engineering time goes</a> · <a href="/learn/technical-anchor/discovery/">Discovery: fail fast for the whole project</a> · <a href="/learn/data-systems/upstreams/">Upstreams: know your sources</a></p></section>
</div>"""
    crumbs = [("How we work", f"{SITE}/how-we-work/"), ("Critical thinking", url)]
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": TITLE, "description": DESC, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in QA]}]
    head = DT.CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(TITLE, DESC, url, body, head)


def main():
    out = ROOT / "how-we-work" / "critical-thinking"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("critical thinking ->", out / "index.html")


if __name__ == "__main__":
    main()
