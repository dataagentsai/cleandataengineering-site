"""Top project management mistakes in data projects: one page at /how-we-work/project-management-mistakes/.

    python3 _guides/pm_mistakes.py      (then python3 _site/nav.py and python3 _site/seo.py)

Teach first: why data projects break normal project management (discovery as much as delivery,
a dependency you don't control, done = numbers people trust), drawn. Then thirteen mistakes in five
groups, each with what it looks like, why it hurts and how to avoid it; one table with verdicts;
a healthier plan shape with sign-off gates; weekly warning signs. No statistics, no surveys.
Reuses de_time.py's CSS, figure helper and arrow marker.
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
URL_PATH = "/how-we-work/project-management-mistakes/"
DATE = "2026-11-12"
TITLE = "Top project management mistakes in data projects, and how to avoid them"
DESC = ("Thirteen project management mistakes that sink data projects: planning as if code were the work, no discovery gate, "
        "'migrate everything', no metric owners, late access, no reconciliation sign-off, percent-complete status, big-bang go-live, no plan for running.")

BLUE, MINT, BUTTER, ROSE, LAV = DT.BLUE, DT.MINT, DT.BUTTER, DT.ROSE, DT.LAV
ARROW = DT.ARROW  # marker id "dta"

CSS = DT.CSS + """<style>
  .tf .mk { border:var(--line); border-radius:var(--wob); padding:8px 16px 4px; margin:12px 0; background:#fff; }
  .tf .mk h3 { margin:6px 0 4px; } .tf .mk p { margin:4px 0 8px; font-size:15px; }
  .tf .mk .n { font-family:var(--hand); font-size:20px; margin-right:6px; }
  .tf ul.warn li { margin:4px 0; }
</style>"""


def _arrow(x1, y1, x2, y2, dash=False):
    da = ' stroke-dasharray="5 4"' if dash else ""
    return f'<path d="M{x1},{y1} L{x2},{y2}" stroke="#111" stroke-width="1.5" fill="none"{da} marker-end="url(#dta)"/>'


def _box(x, y, w, h, fill, lines, size=15):
    d = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="#111" stroke-width="1.5"/>'
    top = y + h / 2 - (len(lines) - 1) * 10 + 5
    for i, t in enumerate(lines):
        d += f'<text x="{x + w / 2}" y="{top + i * 20}" text-anchor="middle" font-size="{size if i == 0 else size - 1.5}">{E(t)}</text>'
    return d


def drawing_two_projects():
    d = (f'<svg viewBox="0 0 1000 340" role="img" aria-label="Two projects side by side. A software project: requirements, then build features, then ship; done means the feature works. '
         f'A data project: learn the sources, then build, then prove the numbers, with a loop back from prove to learn when numbers do not match, and a source system outside the team\'s control feeding in; done means people trust the numbers.">{ARROW}')
    d += '<g fill="none" stroke="#111" stroke-width="1.5"><rect x="10" y="10" width="470" height="320" rx="12" stroke-dasharray="2 4"/><rect x="520" y="10" width="470" height="320" rx="12" stroke-dasharray="2 4"/></g>'
    d += '<text x="24" y="38" font-size="20">A software project</text><text x="534" y="38" font-size="20">A data project</text>'
    # software: straight line
    d += _box(30, 110, 120, 60, BLUE, ["requirements"]) + _box(185, 110, 120, 60, BLUE, ["build", "features"]) + _box(340, 110, 120, 60, MINT, ["ship"])
    d += _arrow(150, 140, 183, 140) + _arrow(305, 140, 338, 140)
    d += '<text x="245" y="230" text-anchor="middle" font-size="15">the team controls most inputs</text>'
    d += '<text x="245" y="292" text-anchor="middle" font-size="16">done = the feature works</text>'
    # data: loop + outside dependency
    d += _box(540, 110, 125, 60, ROSE, ["learn the", "sources"]) + _box(695, 110, 120, 60, BLUE, ["build"]) + _box(845, 110, 125, 60, BUTTER, ["prove the", "numbers"])
    d += _arrow(665, 140, 693, 140) + _arrow(815, 140, 843, 140)
    d += '<path d="M907,172 C907,232 602,232 602,174" stroke="#111" stroke-width="1.5" fill="none" stroke-dasharray="5 4" marker-end="url(#dta)"/>'
    d += '<text x="755" y="244" text-anchor="middle" font-size="14">numbers don\'t match: back to learning</text>'
    d += f'<rect x="540" y="52" width="170" height="36" rx="8" fill="#fff" stroke="#111" stroke-width="1.5" stroke-dasharray="5 4"/><text x="625" y="75" text-anchor="middle" font-size="14">source system (not yours)</text>'
    d += _arrow(602, 88, 602, 108, dash=True)
    d += '<text x="755" y="292" text-anchor="middle" font-size="16">done = people trust the numbers</text>'
    return d + "</svg>"


def drawing_percent():
    """Percent complete by layer vs one source working end to end."""
    layers = ["ingest", "bronze", "silver", "gold", "report"]
    d = (f'<svg viewBox="0 0 1000 300" role="img" aria-label="Two ways to report status. Left, percent complete by layer: ingest 90 percent, bronze 80, silver 60, gold 30, report 10; the project reads as 54 percent done but nothing works for a user. '
         f'Right, one source working end to end: orders flow from ingest to report and the numbers match finance; one thing works, and everyone can see it.">{ARROW}')
    d += '<g fill="none" stroke="#111" stroke-width="1.5"><rect x="10" y="10" width="470" height="280" rx="12" stroke-dasharray="2 4"/><rect x="520" y="10" width="470" height="280" rx="12" stroke-dasharray="2 4"/></g>'
    d += '<text x="24" y="38" font-size="19">"54% done"</text><text x="534" y="38" font-size="19">"orders work end to end"</text>'
    for i, (lab, p) in enumerate(zip(layers, [90, 80, 60, 30, 10])):
        y = 62 + i * 38
        d += f'<text x="110" y="{y + 18}" text-anchor="end" font-size="14.5">{lab}</text>'
        d += f'<rect x="120" y="{y}" width="300" height="24" rx="5" fill="#fff" stroke="#111" stroke-width="1.3"/>'
        d += f'<rect x="120" y="{y}" width="{3 * p}" height="24" rx="5" fill="{BLUE}" stroke="#111" stroke-width="1.3"/>'
        d += f'<text x="428" y="{y + 18}" font-size="13.5">{p}%</text>'
    d += '<text x="245" y="272" text-anchor="middle" font-size="14.5">busy everywhere, nothing a user can use</text>'
    for i, lab in enumerate(layers):
        x = 540 + i * 89
        d += f'<rect x="{x}" y="110" width="74" height="44" rx="8" fill="{MINT}" stroke="#111" stroke-width="1.4"/><text x="{x + 37}" y="137" text-anchor="middle" font-size="14">{lab}</text>'
        if i < 4:
            d += _arrow(x + 74, 132, x + 87, 132)
    d += '<text x="760" y="88" text-anchor="middle" font-size="15">one source: orders</text>'
    d += f'<rect x="640" y="186" width="240" height="40" rx="8" fill="{BUTTER}" stroke="#111" stroke-width="1.4"/><text x="760" y="211" text-anchor="middle" font-size="14.5">matches finance within 0.5%</text>'
    d += '<text x="760" y="272" text-anchor="middle" font-size="14.5">one thing works, and everyone can see it</text>'
    return d + "</svg>"


def drawing_plan():
    steps = [("discovery", "2-4 weeks", ROSE), ("thin slice", "one source,\nend to end", BLUE), ("prove numbers", "reconcile,\nparallel run", BUTTER),
             ("widen", "next sources,\none at a time", BLUE), ("run", "support, reruns,\ncost", MINT)]
    gates = ["go / no-go", "slice works", "numbers signed", "handover"]
    d = (f'<svg viewBox="0 0 1000 260" role="img" aria-label="A healthier plan shape in five steps with a sign-off gate between each. Discovery, two to four weeks; gate: go or no-go. '
         f'Thin slice, one source end to end; gate: the slice works. Prove the numbers, reconcile and run in parallel; gate: numbers signed off by the business owner. '
         f'Widen, the next sources one at a time; gate: handover. Run: support, reruns and cost.">{ARROW}')
    for i, (h, s, fill) in enumerate(steps):
        x = 10 + i * 198
        d += f'<rect x="{x}" y="50" width="160" height="120" rx="12" fill="{fill}" stroke="#111" stroke-width="1.5"/>'
        d += f'<text x="{x + 80}" y="86" text-anchor="middle" font-size="17">{h}</text>'
        for j, ln in enumerate(s.split("\n")):
            d += f'<text x="{x + 80}" y="{118 + j * 20}" text-anchor="middle" font-size="14">{E(ln)}</text>'
        if i < 4:
            gx = x + 179
            d += _arrow(x + 160, 110, x + 196, 110)
            d += f'<path d="M{gx},180 L{gx},206" stroke="#111" stroke-width="1.2"/><path d="M{gx},180 l-6,6 M{gx},180 l6,6" stroke="#111" stroke-width="1.2"/>'
            d += f'<text x="{gx}" y="224" text-anchor="middle" font-size="13.5">gate: {gates[i]}</text>'
    d += '<text x="500" y="30" text-anchor="middle" font-size="15">each gate has a named person who signs it, in writing</text>'
    return d + "</svg>"


def drawing_chaser():
    d = (f'<svg viewBox="0 0 1000 230" role="img" aria-label="Left: the engineer in the middle, with arrows to the source owner, the business owner, security and the report user; the engineer chases everyone and builds in the gaps. '
         f'Right: the project manager or anchor in the middle doing the chasing, and the engineer to the side, building from written answers.">{ARROW}')
    d += '<g fill="none" stroke="#111" stroke-width="1.5"><rect x="10" y="10" width="470" height="210" rx="12" stroke-dasharray="2 4"/><rect x="520" y="10" width="470" height="210" rx="12" stroke-dasharray="2 4"/></g>'

    def person(cx, cy, fill, label, size=14):
        return (f'<circle cx="{cx}" cy="{cy}" r="15" fill="#fff" stroke="#111" stroke-width="1.4"/>'
                f'<path d="M{cx - 24},{cy + 42} q24,-36 48,0 Z" fill="{fill}" stroke="#111" stroke-width="1.4"/>'
                f'<text x="{cx}" y="{cy + 62}" text-anchor="middle" font-size="{size}">{label}</text>')
    others = [(80, 46, "source owner"), (410, 46, "business owner"), (80, 136, "security"), (410, 136, "report user")]
    d += '<text x="245" y="36" text-anchor="middle" font-size="16">what happens</text>'
    d += person(245, 90, BLUE, "engineer", 15)
    for cx, cy, lab in others:
        d += person(cx, cy, "#fff", lab, 13)
        d += _arrow(245 + (cx - 245) * 0.18, 112 + (cy - 90) * 0.1, cx + (30 if cx < 245 else -30), cy + 20)
    d += '<text x="755" y="36" text-anchor="middle" font-size="16">what works</text>'
    d += person(700, 90, LAV, "PM or anchor", 15)
    for cx, cy, lab in [(590, 46, "source owner"), (590, 136, "security"), (810, 46, "business owner")]:
        d += person(cx, cy, "#fff", lab, 13)
        d += _arrow(700 + (cx - 700) * 0.2, 112, cx + (30 if cx < 700 else -30), cy + 20)
    d += person(910, 136, BLUE, "engineer", 13)
    d += '<text x="910" y="102" text-anchor="middle" font-size="12.5">builds from</text><text x="910" y="118" text-anchor="middle" font-size="12.5">written answers</text>'
    return d + "</svg>"


# group, number, title, looks like, why it hurts, how to avoid
MISTAKES = [
    ("Planning", 1, "Planning as if the code were the work",
     "The plan lists ingest, transform, test, deploy, each with days of coding.",
     "Most hours go to understanding what the source data means, reconciling and waiting. A plan of code tasks is late from week one.",
     'Plan the understanding work as real tasks: questions per source, answers signed, reconciliation. See <a href="/learn/where-data-engineering-time-goes/">where data engineering time goes</a>.'),
    ("Planning", 2, "No discovery phase and no go / no-go gate",
     "The team starts building in week one because the deadline is fixed.",
     "The project learns in month four that a key source has no change date, or that two systems disagree on the customer. The plan breaks late, when it costs most.",
     'A short discovery with a written go / no-go decision before the build is funded. See <a href="/learn/technical-anchor/discovery/">discovery: fail fast for the whole project</a>.'),
    ("Planning", 3, "Estimates given as one number",
     "\"Twelve weeks.\" It goes on a slide and becomes a promise.",
     "Unknown sources make a single number a guess. When it slips, trust in the whole team drops.",
     'Give ranges, say what would move them, and narrow them after discovery. See <a href="/how-we-work/estimation/">estimation mistakes</a>.'),
    ("Scope and requirements", 4, "Scope as \"migrate everything\"",
     "The old warehouse has 900 tables and reports, so the new one must have all of them.",
     "Half of them nobody uses. The team spends months rebuilding reports that get switched off anyway.",
     "List who uses what (query logs help), then move by decision: the reports people act on first. Retire the rest on purpose."),
    ("Scope and requirements", 5, "Requirements as report mock-ups",
     "A picture of the dashboard, with no definition behind each number.",
     "\"Active customer\" means three things in three departments. The engineer picks one, and the argument happens at go-live.",
     "Each number on the mock-up gets a written definition, a worked example and a named owner who signs it."),
    ("People and dependencies", 6, "Source owners not committed",
     "The source team was told about the project, but answering questions is not in their plan.",
     "Every question waits days. The source is the one dependency the project cannot work around.",
     "Get a named source owner and an agreed answer time before the build starts. Put it in their plan, not just yours."),
    ("People and dependencies", 7, "Access requested when coding starts",
     "Week three: the engineer asks for credentials, a firewall rule and a security review.",
     "Approvals take weeks. The team waits, or works on samples that turn out different from the real data.",
     "Raise every access request on day one, in parallel. Make \"access granted\" a gate before the build."),
    ("People and dependencies", 8, "The engineer as the stakeholder chaser",
     "The engineer runs the meetings, chases answers and writes the status.",
     "Your most expensive builder spends the week in calls. Answers stay in their head and leave with them.",
     'The PM or a <a href="/learn/technical-anchor/">technical anchor</a> chases and writes answers down; the engineer builds from what is written.'),
    ("Delivery and quality", 9, "No reconciliation target or sign-off",
     "\"It should match the old report\", with no tolerance and no one to sign.",
     "Every small difference becomes an investigation. Go-live keeps moving because \"done\" was never defined.",
     "Agree up front: which report, which tolerance, the known differences, and who signs off. Automate the check."),
    ("Delivery and quality", 10, "Status by percent complete",
     "\"Bronze 80%, silver 60%, gold 30%: 54% done.\"",
     "Nothing works for a user until the last layer is done, so the percentages hide the real risk.",
     "Report what works end to end: \"orders reach the report and match finance\". Build thin slices so that sentence comes early."),
    ("Delivery and quality", 11, "Big-bang go-live with no parallel run",
     "The old system is switched off the day the new one goes live.",
     "The first month-end close is the first real test, and there is no way back.",
     "Run old and new side by side for at least one full business cycle, such as a month-end, and compare daily."),
    ("After go-live", 12, "No plan for running it",
     "The project ends at go-live. Nobody owns failures, reruns, source changes or the cloud bill.",
     "Quality fixes and reruns become the biggest share of the work, done by people already moved to the next project.",
     "Plan the run before go-live: who is on call, how reruns and backfills work, alerts on source changes, a cost budget."),
    ("After go-live", 13, "Success measured as pipelines built",
     "The closing slide counts tables, pipelines and terabytes.",
     "Nobody checks whether anyone decided anything differently. The next budget is hard to win.",
     "Name two or three decisions the data should change, at the start. Check them three months after go-live."),
]

VERDICT = [
    ("Plan understanding as tasks, not just code", "Code is the smaller share of a first build", "Do this"),
    ("Discovery with a written go / no-go", "Cheapest point to learn a source is broken", "Do this"),
    ("Single-number estimate on a slide", "Becomes a promise before anything is known", "Avoid"),
    ("Migrate everything", "Rebuilds unused reports at full cost", "Avoid"),
    ("Mock-ups without definitions and owners", "Moves the argument to go-live", "Avoid"),
    ("Named source owner with an answer time", "The one dependency you cannot work around", "Do this"),
    ("Access requested on day one", "Approvals take weeks; start the clock early", "Do this"),
    ("Engineer as chaser", "Burns builder time; answers live in one head", "Avoid"),
    ("Reconciliation target agreed and signed", "Defines done before the arguments start", "Do this"),
    ("Status by percent complete per layer", "Hides that nothing works yet", "Avoid"),
    ("Thin slice end to end first", "Shows real progress and real problems early", "Do this"),
    ("Big-bang switch-off", "No way back after the first month-end", "Avoid"),
    ("Run plan before go-live", "Running is most of the life of a pipeline", "Do this"),
    ("Success as decisions changed", "What the business paid for", "Do this"),
]

WARN = [
    "An open question to a source owner has waited more than three working days.",
    "An access request is still pending after the build has started.",
    "Status is reported in percent, and no source works end to end yet.",
    "A number on a report mock-up has no written definition or no owner.",
    "Nobody can say which report the new numbers must match, or within what tolerance.",
    "The same engineer is in most of the meetings this week.",
    "The go-live date is fixed but the parallel run is not in the plan.",
    "Nobody is named for on-call, reruns or the cloud bill after go-live.",
]

QUESTIONS = [
    "Where in your plan is the time to understand each source, and who answers those questions?",
    "Who signed the go / no-go after discovery, and what would have stopped the project?",
    "Which report must the new numbers match, within what tolerance, and who signs it off?",
    "Can you name one source that works end to end today, numbers checked?",
    "Which two or three business decisions should this data change, and how will you check?",
]

QA = [
    ("Why do data projects run late more often than other projects?",
     "Because a large part of the work is finding out what the source data means, and that depends on people outside the team. Plans written as lists of coding tasks leave that work out, so they are late from the start."),
    ("Should data projects use Agile or Waterfall?",
     "Neither label fixes the problem. What helps is a short discovery with a go / no-go decision, then thin slices that each take one source all the way to a trusted number, with written sign-off gates."),
    ("What should a data project status report show?",
     "What works end to end, with numbers checked, plus the open questions and how long each has waited. Percent complete per layer hides that nothing usable exists yet."),
    ("When is a data migration done?",
     "When the agreed reports match the old ones within the agreed tolerance through at least one full business cycle, the business owner has signed, and the old system can be switched off."),
    ("Who should chase source owners and business owners?",
     "The project manager or a technical anchor. Engineers should build from written answers, not spend their week in meetings collecting them."),
]


def fig(svg, cap):
    return DT.fig(svg, cap)


def page():
    url = f"{SITE}{URL_PATH}"
    groups, seen = "", []
    for g, *_ in MISTAKES:
        if g not in seen:
            seen.append(g)
    figs_after = {"People and dependencies": fig(drawing_chaser(), "The chasing has to happen. It should not land on the person who builds."),
                  "Delivery and quality": fig(drawing_percent(), "Percent complete per layer looks like progress. One source working end to end is progress.")}
    for g in seen:
        cards = ""
        for gg, n, t, looks, why, how in MISTAKES:
            if gg != g:
                continue
            cards += (f'<div class="mk"><h3><span class="n">{n}</span>{E(t)}</h3>'
                      f'<p><b>What it looks like:</b> {E(looks)}</p><p><b>Why it hurts:</b> {E(why)}</p><p><b>How to avoid it:</b> {how}</p></div>')
        gid = g.lower().replace(" ", "-")
        groups += f'<section id="{gid}"><p class="eyebrow">Mistakes: {E(g.lower())}</p><h2>{E(g)}</h2>{cards}{figs_after.get(g, "")}</section>'
    vt = ('<div class="tw"><table class="t"><tr><th>Practice</th><th>Why</th><th>Verdict</th></tr>'
          + "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td><b>{E(c)}</b></td></tr>" for a, b, c in VERDICT) + "</table></div>")
    warn = "".join(f"<li>{E(w)}</li>" for w in WARN)
    qs = "".join(f"<li>{E(q)}</li>" for q in QUESTIONS)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/how-we-work/">How we work</a> › Project management mistakes</p>
<p class="eyebrow" style="margin-top:22px">How we work · free guide · one page</p>
<h1>{E(TITLE)}</h1>
<p class="lede">Data projects rarely fail because the code was hard. They fail because the plan treated them like ordinary software projects: a list of things to build, a date, and percent complete each week. This page shows what is different about data projects, the thirteen mistakes we see most, and what to do instead.</p>
<div class="tf">
<section id="different"><p class="eyebrow">Teach first</p><h2>Why data projects break normal project management</h2>
<p>Three things make a data project different from building an app.</p>
<ol><li><b>It is discovery as much as delivery.</b> You don't know what the source data really means until you look, ask and test. Some of what you learn changes the plan.</li>
<li><b>The biggest dependency is not yours.</b> The source systems, and the people who know them, belong to other teams with their own priorities.</li>
<li><b>Done means trusted numbers, not shipped code.</b> A pipeline that runs but disagrees with finance is not done. Proving the numbers is a phase of its own.</li></ol>
{fig(drawing_two_projects(), "A software project is mostly a straight line. A data project loops back each time the numbers don't match, and depends on systems it doesn't own.")}
<div class="box"><b>In one line:</b> plan the learning, get the outside people committed, prove the numbers in thin slices, and plan the running before go-live.</div></section>
{groups}
<section id="table"><p class="eyebrow">All in one place</p><h2>Practices, with a verdict</h2>{vt}</section>
<section id="shape"><p class="eyebrow">What good looks like</p><h2>A healthier plan shape</h2>
<p>Instead of one long build ending in a go-live date, plan five steps with a signed gate between each. The thin slice is the key: one source, all the way to a number a business owner has checked. It shows real progress early and surfaces the real problems while they are still cheap.</p>
{fig(drawing_plan(), "Discovery, thin slice, prove, widen, run. Each gate has a named person who signs it.")}</section>
<section id="warning"><p class="eyebrow">Watch weekly</p><h2>Early warning signs</h2>
<p>A project manager can check these every week in ten minutes. Any one of them is worth raising the same day.</p><ul class="warn">{warn}</ul></section>
<section id="check"><p class="eyebrow">Your turn</p><h2>Five questions for your own project</h2><ol>{qs}</ol></section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(QA)}</section>
<section id="next"><p class="eyebrow">Related</p><h2>Where it connects</h2>
<p><a href="/how-we-work/">How we work</a> · <a href="/how-we-work/estimation/">Estimation mistakes in data projects</a> · <a href="/how-we-work/critical-thinking/">Critical thinking in data projects</a> · <a href="/learn/where-data-engineering-time-goes/">Where data engineering time goes</a> · <a href="/learn/technical-anchor/">The technical anchor</a> · <a href="/learn/technical-anchor/project-review/">Project review</a></p></section>
</div>"""
    crumbs = [("How we work", f"{SITE}/how-we-work/"), ("Project management mistakes", url)]
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": TITLE, "description": DESC, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in QA]}]
    head = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(TITLE, DESC, url, body, head)


def main():
    out = ROOT / "how-we-work" / "project-management-mistakes"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("pm mistakes ->", out / "index.html")


if __name__ == "__main__":
    main()
