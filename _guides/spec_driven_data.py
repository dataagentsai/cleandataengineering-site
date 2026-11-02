"""Spec-driven development for the data platform, for leaders: /leaders/spec-driven/data-platform/.

    python3 _guides/spec_driven_data.py && python3 _site/nav.py && python3 _site/seo.py

The data sibling of /leaders/spec-driven/ (the agent page). It reuses that page's CSS, drawing
helpers and page shell from _guides/spec_driven.py, with its own drawings.
Numbers come from ~/clean-data-engineering/TODO.md "Start here" and ~/data-platform-catalog (2 Nov 2026):
22 concerns, 66 DAC obligations, 22 ports, 10 pipeline archetypes, 32 slice-1 capabilities.
The agent evidence (gaps 28 -> 8, runs 3 to 5) is from the agent page.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import spec_driven as SD  # noqa: E402
from spec_driven import I, INK, WASH, svg, box, t, arrow, paper, num, fig, checklist, cloud  # noqa: E402

ROOT = SD.ROOT
OUT = ROOT / "leaders" / "spec-driven" / "data-platform" / "index.html"
TITLE = "Spec-driven development for data platforms"
DESC = ("How a small data centre of excellence writes the platform's specs once and builds the shared assets once, "
        "so every pipeline and data product is built, tested, released and run from the same specs.")
URL = "https://cleandataengineering.ai/leaders/spec-driven/data-platform/"

CSS = SD.CSS + """
  .sd-card.sky { background:var(--sky-wash, #E0F1F7); }
"""


def cyl(x, y, w, h, fill):
    """A small database cylinder."""
    e = 7
    return (f'<path d="M{x},{y + e} L{x},{y + h - e} A{w / 2},{e} 0 0 0 {x + w},{y + h - e} L{x + w},{y + e}" fill="{fill}" class="o" style="stroke-width:1.5"/>'
            f'<ellipse cx="{x + w / 2}" cy="{y + e}" rx="{w / 2}" ry="{e}" fill="#fff" class="o" style="stroke-width:1.5"/>')


# ---------------------------------------------------------------- 1. the data COE
ROLES = [
    ("Data Architect", "the whole picture", I.PAL["blue"], 0),
    ("Platform Architect", "what must exist", I.PAL["teal"], 1),
    ("Data Eng. lead", "pipelines, framework", I.PAL["plum"], 2),
    ("Analytics Engineer", "metrics, semantics", I.PAL["coral"], 3),
    ("DataOps and SRE", "freshness, cost", I.PAL["orange"], 0),
    ("Quality and Test", "rules, test worlds", I.PAL["green"], 1),
    ("Data Steward", "owners, PII, glossary", I.PAL["navy"], 2),
]
TABS = [I.PAL["peri"], I.PAL["mint"], I.PAL["lav"], I.PAL["rose"], I.PAL["peach"], I.PAL["butter"], I.PAL["mint"]]


def fig_team():
    n = 11
    b = I.blob(500, 175, 490, 140, "#FBEFF4")
    for i, (role, what, shirt, skin) in enumerate(ROLES):
        x = 75 + i * 142
        b += paper(x + 30, 100, 40, 54, TABS[i])
        b += I.person(x, 250, shirt, I.PAL["navy"] if shirt != I.PAL["navy"] else I.PAL["plum"], skin, reach=(x + 34, 132), scale=.6)
        b += t(x, 282, role, 17, hand=True) + t(x, 300, what, 12, fill="#555")
        b += arrow(n, f"M{x},{308} C{x},{322} {500 + (x - 500) * .7},{326} {500 + (x - 500) * .72},{352}")
    b += box(n, 50, 356, 900, 54, WASH["rose"])
    for k in range(3):
        b += cyl(72 + k * 24, 366, 18, 34, TABS[k])
        b += cyl(858 + k * 24, 366, 18, 34, TABS[k + 3])
    b += t(500, 390, "One spec library for the data platform, versioned like code", 21, hand=True)
    return svg(n, 1000, 420, b, "Seven people of the data centre of excellence, each holding the spec they write, all feeding one spec library")


# ---------------------------------------------------------------- 2. the five specs as four kinds
QUADS = [
    (160, 40, WASH["peri"], "Catalogs (3 specs)", ["DPC: what every platform must have", "DAC: what must always be true", "DWD: the world it must face"], "written once, used by all"),
    (515, 40, WASH["rose"], "Manifest (DPM)", ["What this company's platform does:", "its sources, datasets, contracts,", "owners, schedules and targets"], "one per company"),
    (160, 245, WASH["mint"], "Binding (DBS)", ["Each concern mapped to a product:", "Databricks on AWS, Fabric, ...", "the only place products appear"], "one per platform"),
    (515, 245, WASH["butter"], "The running platform", ["Pipelines and data products live,", "with their SLOs, alerts, runbooks,", "costs and the gate evidence"], "one per release"),
]


def fig_quad():
    n = 12
    b = ""
    for x, y, fill, title, lines, tag in QUADS:
        b += box(n, x, y, 345, 190, fill)
        b += t(x + 22, y + 38, title, 25, hand=True, anchor="start")
        for k, ln in enumerate(lines):
            b += t(x + 22, y + 72 + k * 24, ln, 14.5, anchor="start")
        b += f'<rect x="{x + 22}" y="{y + 146}" width="{len(tag) * 7.4 + 20}" height="26" rx="13" fill="#fff" stroke="{INK}" stroke-width="1.4"/>'
        b += t(x + 32, y + 164, tag, 12.5, anchor="start", bold=True)
    b += cyl(800, 150, 30, 50, I.PAL["butter"]) + cyl(452, 360, 26, 44, I.PAL["mint"])
    b += arrow(n, "M135,440 L135,48") + arrow(n, "M135,48 L135,440")
    b += t(70, 130, "Tech", 20, hand=True) + t(70, 152, "agnostic", 20, hand=True) + t(70, 172, "no product names", 11.5, fill="#555")
    b += t(70, 335, "Tech", 20, hand=True) + t(70, 357, "binding", 20, hand=True) + t(70, 377, "names the product", 11.5, fill="#555")
    b += arrow(n, "M165,462 L860,462") + arrow(n, "M860,462 L165,462")
    b += t(332, 492, "Domain agnostic", 20, hand=True) + t(332, 510, "any company, any industry", 12, fill="#555")
    b += t(688, 492, "Company specific", 20, hand=True) + t(688, 510, "this company, this data", 12, fill="#555")
    return svg(n, 880, 520, b, "Two by two grid: catalogs top left, the manifest top right, the binding bottom left and the running platform bottom right")


# ---------------------------------------------------------------- 3. what the data COE builds
def fig_floors():
    n = 13
    b = ""
    b += box(n, 30, 30, 800, 110, WASH["rose"])
    b += t(50, 60, "Data products, built by domain teams (a hospital, say)", 21, hand=True, anchor="start")
    for k, name in enumerate(["Patient 360", "Bed occupancy", "Claims and TPA", "Lab turnaround", "Pharmacy stock"]):
        x = 50 + k * 155
        b += f'<rect x="{x}" y="80" width="138" height="46" rx="10" fill="#fff" class="o" style="stroke-width:1.6"/>'
        for j in range(3):
            b += f'<rect x="{x + 10 + j * 9}" y="{112 - (j + 1) * 6}" width="6" height="{(j + 1) * 6}" fill="{I.PAL["coral"]}"/>'
        b += t(x + 87, 108, name, 12.5)
    b += box(n, 30, 160, 800, 140, WASH["peri"])
    b += t(50, 190, "Horizontal assets, built once by the COE", 21, hand=True, anchor="start")
    assets = [("Ingestion", "framework"), ("Metadata", "store"), ("Quality", "framework"), ("Semantic", "model"),
              ("Conversation", "UI"), ("Cost", "control"), ("Shift-left", "checks"), ("DataTwin", "simulator")]
    for k, (a, c) in enumerate(assets):
        x = 46 + k * 97
        b += f'<rect x="{x}" y="208" width="90" height="74" rx="10" fill="#fff" class="o" style="stroke-width:1.6"/>'
        b += t(x + 45, 240, a, 13, bold=True) + t(x + 45, 259, c, 13)
    b += box(n, 30, 320, 800, 100, WASH["butter"])
    b += t(50, 350, "Specs, written by the COE", 21, hand=True, anchor="start")
    for k, (name, fill) in enumerate([("DPC", I.PAL["peri"]), ("DAC", I.PAL["peri"]), ("DWD", I.PAL["peri"]),
                                      ("DPM template", I.PAL["rose"]), ("DBS binding", I.PAL["mint"]), ("Release gate", I.PAL["butter"])]):
        x = 50 + k * 128
        b += f'<rect x="{x}" y="364" width="118" height="40" rx="10" fill="{fill}" class="o" style="stroke-width:1.6"/>'
        b += t(x + 59, 389, name, 14)
    for k, (cx, name) in enumerate([(160, "Databricks on AWS"), (430, "Microsoft Fabric"), (700, "Other clouds")]):
        b += cloud(cx, 470)
        b += t(cx, 480, name, 13, bold=True)
    b += t(430, 525, "one lakehouse underneath: the binding decides which", 14, fill="#555")
    b += arrow(n, "M845,90 C905,150 905,320 845,380", dash=True)
    b += f'<g transform="rotate(90 900 235)">{t(900, 230, "every data product feeds back down", 15, hand=True)}</g>'
    return svg(n, 940, 540, b, "A three-floor building: specs at the bottom, eight horizontal assets in the middle, hospital data products on top, standing on a lakehouse that can be Databricks on AWS or another platform")


# ---------------------------------------------------------------- 4. one spec, eight uses (data)
USES = [("Build", "pipelines generated from it"), ("Test", "every rule becomes a test"), ("Release", "the gate checklist"),
        ("Operate (SRE)", "freshness SLOs and alerts"), ("Reconcile", "source and gold must agree"),
        ("Audit", "evidence for every number"), ("Review", "check against it, not opinion"), ("Fail fast", "gaps show on day one")]
USE_FILL = [WASH["peri"], WASH["mint"], WASH["butter"], WASH["sky"], WASH["rose"], WASH["lilac"], WASH["rose"], WASH["mint"]]


def fig_uses():
    import math
    n = 14
    cx, cy = 450, 225
    b = ""
    pos = [(cx + 340 * math.cos(math.radians(-90 + k * 45)), cy + 172 * math.sin(math.radians(-90 + k * 45))) for k in range(8)]
    for x, y in pos:
        b += f'<line x1="{cx}" y1="{cy}" x2="{x:.0f}" y2="{y:.0f}" stroke="{INK}" stroke-width="1.4" stroke-dasharray="5 6"/>'
    for (x, y), (title, sub), fill in zip(pos, USES, USE_FILL):
        b += box(n, x - 100, y - 27, 200, 54, fill, r=12)
        b += t(x, y - 4, title, 15.5, bold=True) + t(x, y + 15, sub, 12.5)
    b += f'<ellipse cx="{cx}" cy="{cy + 4}" rx="122" ry="74" fill="#fff"/>'
    b += paper(cx - 70, cy - 52, 64, 82, I.PAL["rose"])
    b += cyl(cx + 6, cy - 46, 58, 76, I.PAL["mint"])
    b += t(cx, cy + 58, "The manifest", 22, hand=True)
    return svg(n, 900, 450, b, "A manifest page and a database in the middle, with dashed lines to eight uses: build, test, release, operate, reconcile, audit, review and fail fast")


# ---------------------------------------------------------------- 5. one thin slice, as a story
STORY = [("Spec", "manifest + catalogs"), ("Design", "ports and layers"), ("Build", "on Databricks"),
         ("DataTwin", "a pretend month"), ("Release gate", "all ticks, or stop"), ("Data product", "people use it")]


def world(x, y):
    """A pretend shop world: a small globe with a planted fault."""
    return (f'<circle cx="{x}" cy="{y}" r="50" fill="{WASH["mint"]}" stroke="{INK}" stroke-width="1.6" stroke-dasharray="5 5"/>'
            f'<path d="M{x - 30},{y - 8} q14,-22 30,-6 t28,4" class="t"/><path d="M{x - 26},{y + 18} q18,-12 34,0 t20,-2" class="t"/>'
            + cyl(x - 12, y - 16, 24, 30, I.PAL["butter"])
            + f'<path d="M{x + 26},{y - 40} l9,16 h-18 Z" fill="{I.PAL["coral"]}" class="o" style="stroke-width:1.4"/>'
            + t(x + 26, y - 26, "!", 12, bold=True))


def fig_story():
    n = 15
    xs = [85, 250, 415, 580, 745, 910]
    b = I.blob(500, 200, 490, 120, "#FBEFF4")
    b += arrow(n, "M745,140 C735,20 98,20 88,128", dash=True)
    b += num(300, 26, "7") + t(318, 31, "Every gap the slice finds is fixed in the spec first", 15, hand=True, anchor="start")
    b += paper(xs[0] - 34, 146, 68, 88, I.PAL["rose"])
    for j, (lay, col) in enumerate([("bronze", "#F3E3D3"), ("silver", "#ECEDEF"), ("gold", "#FFF4D9")]):
        b += f'<rect x="{xs[1] - 46 + j * 12}" y="{150 + j * 26}" width="80" height="22" rx="6" fill="{col}" class="o" style="stroke-width:1.5"/>'
        b += t(xs[1] - 6 + j * 12, 166 + j * 26, lay, 12)
    b += I.person(xs[2] - 18, 250, I.PAL["teal"], I.PAL["navy"], 2, reach=(xs[2] + 22, 200), scale=.58)
    b += f'<g transform="translate({xs[2] + 14},178) scale(.42)">{I.laptop(0, 0)}</g>'
    b += world(xs[3], 192)
    b += checklist(xs[4] - 42, 136)
    b += f'<rect x="{xs[5] - 50}" y="150" width="100" height="80" rx="10" fill="#fff" class="o"/>'
    for j, hgt in enumerate([22, 38, 30, 50]):
        b += f'<rect x="{xs[5] - 36 + j * 20}" y="{216 - hgt}" width="13" height="{hgt}" rx="2" fill="{[I.PAL["peri"], I.PAL["mint"], I.PAL["rose"], I.PAL["butter"]][j]}" class="o" style="stroke-width:1.3"/>'
    for k in range(5):
        a, c = xs[k] + 56, xs[k + 1] - 60
        if k == 2:
            a += 12
        if k == 4:
            c -= 2
        b += arrow(n, f"M{a},196 L{c},196")
    for k, (x, (title, sub)) in enumerate(zip(xs, STORY)):
        b += num(x - 52, 120, str(k + 1))
        b += t(x, 282, title, 19, hand=True) + t(x, 301, sub, 12.5, fill="#444")
    return svg(n, 1000, 320, b, "Six numbered steps for one thin slice: spec, design, build on Databricks, a DataTwin run with planted faults, the release gate, and a live data product; a dashed arrow carries every gap back to the spec")


# ---------------------------------------------------------------- 6. where we are, honestly
def fig_status():
    n = 16
    b = ""
    b += t(30, 34, "Agents: proven", 22, hand=True, anchor="start")
    base, x0 = 230, 40
    b += f'<line x1="{x0}" y1="{base}" x2="400" y2="{base}" class="t" style="stroke-width:1.8"/>'
    for k, (run, gaps, fill) in enumerate([("Run 3", 28, I.PAL["coral"]), ("Run 4", 24, I.PAL["yellow"]), ("Run 5", 8, I.PAL["green"])]):
        x = x0 + 25 + k * 115
        h = gaps * 5.5
        b += f'<rect x="{x}" y="{base - h}" width="70" height="{h}" rx="6" fill="{fill}" class="o" style="stroke-width:1.6"/>'
        b += t(x + 35, base - h - 8, str(gaps), 19, hand=True) + t(x + 35, base + 22, run, 14, bold=True)
    b += t(220, 278, "gaps found rebuilding an agent from the specs alone", 13, fill="#555")
    b += t(480, 34, "Data platforms: in progress", 22, hand=True, anchor="start")
    steps = [("done", "22 concerns, 10 pipeline types, 22 ports"), ("done", "66 rules in the assurance catalog"),
             ("done", "slice 1 specified: 32 capabilities"), ("now", "slice 1 running on Databricks"),
             ("next", "the 30-day DataTwin proof")]
    for k, (st, s) in enumerate(steps):
        y = 64 + k * 42
        fill = {"done": I.PAL["mint"], "now": I.PAL["butter"], "next": "#fff"}[st]
        b += f'<rect x="480" y="{y}" width="20" height="20" rx="5" fill="{fill}" class="o" style="stroke-width:1.5"/>'
        if st == "done":
            b += f'<path d="M484,{y + 10} l4,5 l8,-10" class="t" style="stroke:{I.PAL["green"]};stroke-width:2.4"/>'
        b += t(512, y + 16, s, 15, anchor="start") + t(880, y + 16, st, 12.5, anchor="end", bold=True, fill="#555")
    return svg(n, 900, 290, b, "Left: agent gaps fell from 28 to 24 to 8 over three runs. Right: the data platform checklist, with three steps done, slice 1 running now, and the 30-day proof next")


# ---------------------------------------------------------------- page text
ROLE_CARDS = [
    ("peri", "Data Architect", "The whole picture: which sources, which business questions, which layers, and the main risks to the numbers.",
     "Writes the platform's purpose, its data domains and owners, and the manifest's first draft."),
    ("mint", "Platform Architect", "What every platform must have underneath: storage, compute, catalog, identity, networking, metering.",
     "Writes the platform catalog (DPC) and the binding for each platform (DBS)."),
    ("lilac", "Data Engineering lead", "How data moves from source to gold, and the shared framework every pipeline is built on.",
     "Writes the pipeline types, the ingestion and transformation patterns, and the reference framework."),
    ("rose", "Analytics Engineer", "What the numbers mean: each metric defined once, with its joins and its grain (the level of detail one row stands for).",
     "Writes the semantic model: metrics, dimensions and their owners."),
    ("butter", "DataOps and SRE", "How it runs every day: freshness targets, alerts, runbooks, reruns and cost limits.",
     "Writes the operations part of the manifest and the release gate checklist."),
    ("sky", "Data Quality and Test lead", "How we prove the numbers are right: which rules, which tests, which faults to plant.",
     "Writes the assurance rules (DAC) and the test worlds (DWD) for DataTwin."),
    ("peri", "Data Steward", "Who owns each dataset, which columns hold personal data, and what each business term means.",
     "Writes ownership, privacy tags, retention and the glossary."),
]

CHECKS = [
    ("The data contract is validated: column names, types, keys and allowed values match what the source promised.", "Manifest (DPM) + data contract"),
    ("Every assurance rule for this dataset has a passing test, or a written waiver with a reason, an owner and an end date.", "Assurance catalog (DAC)"),
    ("A freshness target is set, an alert fires when it is missed, and the alert has a runbook and a named person on call.", "Manifest (DPM), operations part"),
    ("Counts and sums agree from the source to gold (reconciliation), within the agreed tolerance.", "Assurance catalog (DAC)"),
    ("Columns with personal data are tagged and masked for everyone who should not see them.", "Manifest (DPM) + steward's tags"),
    ("Each job has a cost budget, and the run log records what every run cost.", "Manifest (DPM) + binding (DBS)"),
    ("Replaying a day and backfilling a month were tried once, and no number doubled.", "Assurance catalog (DAC)"),
    ("Lineage is visible: from any number on a dashboard you can walk back to its source tables.", "Platform catalog (DPC) + binding (DBS)"),
]

PARALLEL = [
    ("What every system must have", "Data Platform Catalog (DPC)", "AI Harness Catalog (AHC)"),
    ("What must always be true", "Data Assurance Catalog (DAC)", "AI Assurance Catalog (AAC)"),
    ("The world it must face", "Data World Description (DWD)", "Agent world description"),
    ("What this one system does", "Data Platform Manifest (DPM), one per company", "Agent spec, one per agent"),
    ("Which product does each job", "Data Binding Spec (DBS)", "Binding per cloud"),
    ("Practice before it is real", "DataTwin", "AgentTwin"),
    ("Working example to copy", "Reference data platform framework", "Reference agent and Agent Core Framework"),
]

ASSETS = [
    ("Common Ingestion Framework", "One metadata-driven way to bring any source in: a new table is a few lines of configuration, not a new pipeline (<a href=\"/learn/data-platform-architecture/ingestion/\">ingestion, explained</a>)"),
    ("Metadata store", "One database that holds every source, dataset, rule and schedule, read by every pipeline (<a href=\"/learn/data-platform-architecture/metadata-store/\">metadata store, explained</a>)"),
    ("Data quality framework", "Rules declared in the manifest, run on every load, bad rows set aside (quarantined) instead of silently dropped"),
    ("Semantic model template", "Each metric defined once, so every dashboard and every question gets the same answer"),
    ("Conversation UI", "Ask the data a question in plain words; the answer comes from the semantic model, not from a guessed query"),
    ("CostSherlock", "Finds what each pipeline and query costs, and the patterns that waste money"),
    ("Shift-left checks", "Problems in pipeline code and SQL caught before they run, not after (<a href=\"/learn/shift-left/\">shift left, explained</a>)"),
    ("DataTwin", "A pretend company that sends late, duplicate and broken data on purpose, to test the platform before real data does (<a href=\"/learn/datatwin/\">DataTwin, explained</a>)"),
    ("Reference data platform framework", "Working code to copy: ports, adapters and the first slice on Databricks (the specs are open in the <a href=\"https://github.com/dataagentsai/data-platform-catalog\">data platform catalog</a>)"),
]

BODY = f"""<main class="wrap">
<div class="hero"><p class="eyebrow">For leaders · ways of working · data</p><h1>{TITLE}</h1>
<p class="thesis">A small data centre of excellence (COE) writes the platform's specs once and builds the shared parts once. After that, every pipeline and every data product is <em>built, tested, released and run from the same specs</em>, and each new data product makes the specs stronger for the next.</p></div>

{fig(fig_team(), "The data COE: seven roles, one spec library. Each role writes the part only they know well.")}

<div class="sd-stat">
<div><b>22 concerns</b>every platform must handle, from quality and lineage to cost and privacy</div>
<div><b>66 rules</b>in the assurance catalog, each one testable</div>
<div><b>5 specs</b>from "any company, any platform" down to "this company on Databricks"</div>
<div><b>8 uses</b>for one spec: build, test, release, operate, reconcile, audit, review, fail fast</div>
</div>

<div class="sd-answer">
<p><b>The one-minute version.</b> In most companies, what the data platform should do lives in people's heads and in old pipelines. Each team writes its own ingestion, quality rules are remembered rather than written, and two dashboards show two different numbers for the same thing.</p>
<p>With spec-driven development, that knowledge is written down once, in plain words, by the people who know it best. Pipelines are built from it, tests come from it, releases are checked against it, and auditors can trace every number back through it. When a number turns out wrong, we <b>fix the spec first</b>, so no later data product repeats the mistake.</p>
</div>

<section><p class="eyebrow">Why change</p><h2>Data platforms without specs, and with them</h2>
<div class="sd-table"><table>
<tr><th>Today, without specs</th><th>With spec-driven development</th></tr>
<tr><td>Every team writes its own ingestion code for every new source</td><td>One ingestion framework; a new source is a few lines in the manifest</td></tr>
<tr><td>Quality rules live in people's heads, or in one notebook nobody else reads</td><td>Every rule is written in the spec and runs on every load</td></tr>
<tr><td>Two dashboards show two different revenue numbers</td><td>Each metric is defined once in the semantic model, so every dashboard agrees</td></tr>
<tr><td>Cost is discovered at the end of the month, on the bill</td><td>Each job has a budget in the manifest, and every run records what it cost</td></tr>
<tr><td>Nobody can say where a number on the dashboard came from</td><td>Lineage and the run log link every number back to its source</td></tr>
<tr><td>A late or broken source file is found by a business user</td><td>DataTwin plants late and broken files before go-live; alerts fire before anyone sees a wrong number</td></tr>
<tr><td>Moving platform means rebuilding every pipeline</td><td>Moving platform means writing a new binding; the manifest and the rules stay the same</td></tr>
</table></div></section>

<section><p class="eyebrow">Who writes the specs</p><h2>The data COE team</h2>
<p>Seven roles. Each writes the part of the spec that only they know well. Nobody has to read the whole library; each opens the part that is theirs. In a small team one person can hold two roles.</p>
<div class="sd-cards">
{"".join(f'<div class="sd-card {c}"><h3>{r}</h3><p>{what}</p><p><span class="lbl">Writes</span>{writes}</p></div>' for c, r, what, writes in ROLE_CARDS)}
</div></section>

<section><p class="eyebrow">Five specs, four kinds</p><h2>Some specs fit every company, some fit one platform</h2>
<p>Two simple questions sort every spec. Does it name a product (tech binding), or not (tech agnostic)? Does it fit any company (domain agnostic), or only this company and its data (company specific)?</p>
{fig(fig_quad(), "Top left is written once and used by every company. Product names live only in the bottom row, so moving platform never touches the top row.")}
<div class="sd-table"><table>
<tr><th>Spec</th><th>In one line</th><th>Kind</th></tr>
<tr><td><b>DPC</b>, Data Platform Catalog</td><td>What every data platform must have: its layers, pipeline types and the 22 concerns, each behind a port (a fixed plug that any product can fill)</td><td>Catalog</td></tr>
<tr><td><b>DAC</b>, Data Assurance Catalog</td><td>What must always be true of the data, such as "a rerun never doubles a number", each written as a rule with a test</td><td>Catalog</td></tr>
<tr><td><b>DWD</b>, Data World Description</td><td>The world the platform must face: sources, volumes and the faults to plant, like late, duplicate or reshaped files</td><td>Catalog</td></tr>
<tr><td><b>DPM</b>, Data Platform Manifest</td><td>What this company's platform does: its sources, datasets, data contracts, owners, schedules and targets, one per company</td><td>Manifest</td></tr>
<tr><td><b>DBS</b>, Data Binding Spec</td><td>Which product does each job, for example Databricks on AWS; the only spec that names products</td><td>Binding</td></tr>
</table></div>
<p>Keeping these apart is what makes them reusable. The catalogs are the same for a hospital and a retailer; only the manifest changes.</p></section>

<section><p class="eyebrow">What the COE builds</p><h2>Specs first, then shared assets, then many data products</h2>
<p>The COE does not only write documents. It also builds the <b>horizontal assets</b>: the parts every data product needs, whatever its domain. Domain teams then build <b>data products</b> on top, one per business question.</p>
{fig(fig_floors(), "Like a building: the specs are the foundation, the shared assets are the middle floor, and each domain team adds its own data product on top.")}
<div class="sd-table"><table>
<tr><th>Horizontal asset</th><th>What it gives every data team</th></tr>
{"".join(f"<tr><td>{a}</td><td>{w}</td></tr>" for a, w in ASSETS)}
</table></div></section>

<section><p class="eyebrow">Not only for data engineers</p><h2>One spec, eight uses</h2>
<p>Most people think a spec is something engineers read before coding. Here the same manifest and rules also drive testing, release, daily operations, reconciliation and audit. That is where most of the saving comes from.</p>
{fig(fig_uses(), "Testers, reviewers, SRE, finance and auditors all work from the same manifest the pipelines were built from, so nobody works from a different idea of what 'correct' means.")}
<h3 style="font-family:var(--hand);font-size:26px;font-weight:400;margin:24px 0 4px">Example: the release gate for a data product</h3>
<p>Before a data product goes live, the gate is checked. Nobody writes this list by hand. It is generated from the specs, and every line says which spec it came from. If a line cannot be ticked, the release stops.</p>
<ul class="sd-check">
{"".join(f'<li><span class="box">✓</span><span>{c}</span><span class="from">From: {f}</span></li>' for c, f in CHECKS)}
</ul></section>

<section><p class="eyebrow">Then, the data products</p><h2>How one data product gets built: thin slices</h2>
<p>We never write the whole spec up front. We take one thin slice, such as "orders, from source to silver", and take it all the way through. Then the next slice.</p>
{fig(fig_story(), "Step 7 is the important one. Every gap a slice finds goes back into the specs and the shared assets.")}
<ol>
<li><b>Spec.</b> The domain team fills in the manifest for this slice: sources, datasets, contracts, owners, targets. The catalogs supply the rest.</li>
<li><b>Design.</b> The slice is mapped onto the layers and ports. Nothing new is invented if a shared asset already does the job.</li>
<li><b>Build.</b> Pipelines are built on the shared framework, on Databricks.</li>
<li><b>DataTwin.</b> A pretend company sends a month of data, with late, duplicate and broken files planted, and the numbers are checked against the pretend world's own totals.</li>
<li><b>Release gate.</b> Every line of the checklist is ticked, or the release stops.</li>
<li><b>Data product.</b> Dashboards, the semantic model and plain-language questions go live.</li>
<li><b>Fix the spec.</b> A missing rule, a new fault, a better default goes back to the COE.</li>
</ol></section>

<section><p class="eyebrow">Where we are</p><h2>Proven on agents, in progress for data</h2>
<p>We first used this method for AI agents. We rebuilt the same agent from the specs alone, fixed every gap it found, and rebuilt again. The gaps fell from 28 to 8, and none came back. For data platforms the specs and the first slice are written, and the first slice is being run end to end on Databricks now.</p>
{fig(fig_status(), "Left: measured on agents. Right: the data platform work as of 2 November 2026.")}
</section>

<section><p class="eyebrow">Same way as agents</p><h2>The same method we use for AI agents</h2>
<p>The data specs are siblings of the agent specs. The roles and the four kinds of spec are the same; only the subject changes.</p>
<div class="sd-table"><table>
<tr><th>Question the spec answers</th><th>Data engineering</th><th>AI engineering (agent harness)</th></tr>
{"".join(f"<tr><td>{q}</td><td>{d}</td><td>{a}</td></tr>" for q, d, a in PARALLEL)}
</table></div>
<p>Read more: <a href="/leaders/spec-driven/">spec-driven development for agents</a>, <a href="/learn/data-platform-architecture/">data platform architecture</a>, <a href="/learn/data-platform-architecture/aws-databricks/">the data platform on AWS and Databricks</a>, <a href="/learn/datatwin/">DataTwin, explained</a>.</p></section>

<section><p class="eyebrow">The case for leaders</p><h2>What you get, and what it takes</h2>
<div class="sd-cards">
<div class="sd-card peri"><h3>For business leaders</h3>
<p>One number for one question, because every metric is defined once.</p>
<p>New data products in weeks, because ingestion, quality and cost control are already built.</p>
<p>Audit-ready: every number can be traced to its source, its rules and its run.</p>
<p>No lock-in: moving platform is a new binding, not a rebuild.</p></div>
<div class="sd-card mint"><h3>For technology leaders</h3>
<p>One way of building pipelines across teams, so people can move between them.</p>
<p>Testers, SRE and stewards join at the start, not after the first wrong number.</p>
<p>Platform features are used to the full, but always through a port, so they can be swapped.</p>
<p>Cost is visible per job and per data product, not only per month.</p></div>
<div class="sd-card butter"><h3>What it takes</h3>
<p><b>Time up front.</b> The first data product is slower, because the shared layer is built alongside it.</p>
<p><b>Discipline.</b> "Fix the spec first" must be a rule, or the specs drift from the pipelines and stop being trusted.</p>
<p><b>Named owners.</b> The COE roles need people with time set aside, not volunteers.</p></div>
</div></section>

<section><p class="eyebrow">How to start</p><h2>Onboarding in three steps</h2>
<ol class="sd-steps">
<li><h3>1 · Crawl: one slice</h3><p>Pick one data product that matters but is not the riskiest. Write its manifest and use the open catalogs as they are.</p><p>Run the release gate on it, even by hand.</p><p><b>You learn:</b> where your teams' unwritten rules live.</p></li>
<li><h3>2 · Walk: form the COE</h3><p>Name the roles. Write the binding for your platform. Move the pilot onto the shared ingestion, quality and cost assets, and run DataTwin on it.</p><p><b>You get:</b> a second data product built in much less time than the first.</p></li>
<li><h3>3 · Run: every domain</h3><p>Domain teams build data products on the COE layer. DataTwin runs on every change, and the release gate is required for every release.</p><p><b>You get:</b> a platform that improves with every data product.</p></li>
</ol></section>

<section class="sd-qa"><p class="eyebrow">Questions</p><h2>Questions leaders ask</h2>
<h3>Isn't this just waterfall with a new name?</h3>
<p>No. We work in thin slices: write a little spec, build it, run it, and fix the spec where the run showed it was wrong. Then the next slice. The spec changes every week.</p>
<h3>We already have Databricks. Why do we need specs?</h3>
<p>Databricks gives excellent parts: storage, pipelines, a catalog, quality expectations, lineage, dashboards. It does not decide which rules your data must obey, who owns each dataset, or what "fresh enough" means for your business. The specs say that once, and the binding switches the Databricks features on to meet it. Our main job is joining the parts, so one run links its quality results, lineage, cost and audit.</p>
<h3>Who owns the specs?</h3>
<p>The COE owns the catalogs, templates and shared assets. Each domain team owns its part of the manifest. A change to a shared spec goes through the COE, like a change to shared code.</p>
<h3>Can AI write the specs for us?</h3>
<p>AI helps a lot with drafting: it can read existing pipelines and propose a manifest, or suggest quality rules from a profile of the data. But decisions such as who may see patient data, or what counts as a late file, belong to people who can be held accountable for them.</p>
<h3>What if we change platform later?</h3>
<p>Only the binding and its adapters change. The catalogs, the manifest and the tests stay as they are, because they never named a product.</p>
<h3>How does this relate to data contracts and other standards?</h3>
<p>We build on them, not instead of them. Data contracts follow the open ODCS standard (Open Data Contract Standard, version 3), and lineage follows OpenLineage. The specs add what those leave out: platform-wide rules, operations targets, cost, and a pretend world to test in.</p>
</section>

<section><p class="eyebrow">Talk to us</p><h2>Want to try this with your team?</h2>
<p>The catalogs and the DataTwin method are open. If you would like to walk through this with your leadership team, or pilot it on one data product, write to <a href="mailto:basant@cleandataengineering.ai?subject=Spec-driven%20data%20platforms">basant@cleandataengineering.ai</a>.</p>
<p><a href="/leaders/spec-driven/">Spec-driven development for agents</a> · <a href="/leaders/">Back to For leaders</a></p></section>
</main>
"""


def main():
    src = SD.SRC
    head_end = src.index("</style>")
    head = src[:head_end] + CSS + src[head_end:src.index("<main")]
    head = re.sub(r"<title>.*?</title>", f"<title>{TITLE} · Clean Data Engineering</title>", head, count=1)
    head = re.sub(r'(<meta name="description" content=")[^"]*', rf"\g<1>{DESC}", head, count=1)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', rf"\g<1>{TITLE}", head, count=1)
    head = re.sub(r'(<meta property="og:description" content=")[^"]*', rf"\g<1>{DESC}", head, count=1)
    head = head.replace("https://cleandataengineering.ai/mindset/", URL)
    foot = src[src.index("<footer>"):]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(head + BODY + foot)
    print("wrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
