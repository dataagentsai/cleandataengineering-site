"""The data platform block of "Data systems, end to end": /learn/data-systems/platform/.

    python3 _guides/data_platform.py      (then python3 _site/seo.py)

Agreed with the owner on 9 Nov 2026:
  * Two directions. Along the line: five hops, which are the medallion (landing and bronze in
    hop 1). Across the line: 24 cross-cutting concerns (the 22 from the architecture guide, plus
    Layout and Streaming; X19 renamed "Performance & scale").
  * Placement rule: each concern has ONE page (its end-to-end view, questions, decisions). A hop
    page carries one row per concern that changes at that hop, linking to the concern page.
  * Each concern is one of three kinds: per hop, both, or platform-wide.
  * Streaming is a second speed on the same line, not an extra layer.
Pages built here: the platform overview (picture, master table, matrix), Layout, and
Environments & CI/CD. Hop pages and the other concern pages come next, in the same template.
"""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("data_systems", ROOT / "_guides" / "data_systems.py")
ds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ds)

E, wb, SITE, BASE = ds.E, ds.wb, ds.SITE, ds.BASE
FILL, box, arrow, text, svg = ds.FILL, ds.box, ds.arrow, ds.text, ds.svg
P = f"{BASE}platform/"

CSS = ds.CSS + """<style>
  .kind { display:inline-block; font-size:11.5px; font-weight:700; letter-spacing:.05em; text-transform:uppercase; border:1.5px solid var(--ink); border-radius:999px; padding:0 8px; white-space:nowrap; }
  .kind.hop { background:var(--peri-wash); } .kind.both { background:var(--butter-wash); } .kind.wide { background:var(--lilac-wash); }
  table.mx td, table.mx th { text-align:center; } table.mx td:nth-child(1), table.mx th:nth-child(1), table.mx td:nth-child(2), table.mx th:nth-child(2) { text-align:left; }
  table.mx td.dot { font-size:18px; } table.mx td.wide { color:var(--muted); font-size:13px; font-style:italic; background:var(--lilac-wash); }
  table.mx th.h { font-size:11px; }
</style>"""

GROUPS = [
    ("Trust", "Can I trust the number?", "butter"),
    ("See", "Can I see what happened and what it cost?", "mint"),
    ("Guard", "Who may see and change what?", "rose"),
    ("Run", "Does it run safely, every day?", "grey"),
    ("Self", "Can it help fix itself, safely?", "peri"),
]

# id, name, group, kind (hop | both | wide), promise, our page slug (None = coming), read-now link
CONCERNS = [
    ("X3", "Contracts & schema", "Trust", "hop", "Each table says what it promises, and a source changing shape is caught on arrival.", None, "/concepts/data-contracts/"),
    ("X4", "Data quality", "Trust", "hop", "Rules on rows and tables at every hop; bad rows are quarantined with a reason, never dropped.", None, "/concepts/data-quality/"),
    ("X5", "Profiling", "Trust", "hop", "We know what the data looks like, so a change in shape or spread is visible.", None, f"{BASE}upstreams/#profile"),
    ("X6", "Reconciliation", "Trust", "both", "Counts and sums agree from the source to gold, every run.", None, "/learn/medallion-architecture/#rules"),
    ("X7", "Lineage", "See", "both", "For any table or column: where it came from and what it feeds.", None, "/concepts/lineage/"),
    ("X8", "Logs, metrics, traces", "See", "wide", "One run can be followed from the source file to the dashboard tile.", None, "/concepts/observability/"),
    ("X9", "Freshness & SLOs", "See", "both", "Each table has a promised age; the time budget is split across the hops.", None, "/concepts/freshness/"),
    ("X10", "Cost & FinOps", "See", "both", "Every cost has an owner and a budget, end to end and per hop.", "cost", None),
    ("X19", "Performance & scale", "See", "both", "Big data stays fast and cheap: file sizes, layout, merges, aggregates, right-sized compute.", None, "/concepts/small-files/"),
    ("X11", "Security & access", "Guard", "both", "Who may read or change each layer, granted on purpose.", None, "/concepts/least-privilege/"),
    ("X12", "Privacy & PII", "Guard", "both", "Personal data is found, tagged, masked, kept only as long as allowed and erasable.", None, "/concepts/governance/"),
    ("X13", "Governance & semantics", "Guard", "hop", "Every table and metric has an owner and one definition.", None, "/concepts/semantic-layer/"),
    ("X14", "Audit & run log", "Guard", "wide", "A record of every run and every change, kept as evidence.", None, "/learn/data-platform-architecture/#control"),
    ("X1", "Metadata & control", "Run", "wide", "Everything is declared in one manifest and validated; a new table is configuration.", None, "/learn/data-platform-architecture/metadata-store/"),
    ("X2", "Orchestration", "Run", "both", "What runs when, what waits for what, and what happens when a step fails.", None, "/concepts/orchestration/"),
    ("X15", "Replay & backfill", "Run", "both", "Any load can be re-run, and history rebuilt, without doubling a number.", None, "/concepts/backfill/"),
    ("X16", "Environments & CI/CD", "Run", "wide", "Every change reaches production the same way, from git, tested, approved and reversible.", "environments", None),
    ("X17", "Testing", "Run", "both", "Unit, contract, data and simulation tests, at every hop and end to end.", None, "/learn/data-platform-architecture/testing/"),
    ("X18", "Resilience & DR", "Run", "wide", "Retries, retention, time travel and a tested way back after a disaster.", None, "/concepts/retries/"),
    ("X23", "Layout: catalogs & schemas", "Run", "wide", "From a table's full name you can tell its environment, layer and domain, and who may read it.", "layout", None),
    ("X24", "Streaming", "Run", "both", "A second speed on the same line, used only where a decision needs it.", None, "/learn/real-time-analytics/"),
    ("X20", "Self-healing", "Self", "wide", "Detect, fix in dev, deploy, verify, roll back: with a person approving.", None, "/learn/data-platform-architecture/#agents"),
    ("X21", "Agent assistance", "Self", "wide", "Agents draft manifests, rules and docs; they never change production.", None, "/learn/data-platform-architecture/#agents"),
    ("X22", "Simulation", "Self", "wide", "A pretend world that breaks the platform on purpose, before production does.", None, "/learn/datatwin/"),
]

HOPS = [
    ("H1", "Sources to bronze", "Landing, Bronze", "Get everything in, exactly as it was, once.", "/learn/data-platform-architecture/ingestion/"),
    ("H2", "Bronze to silver", "Silver", "One clean, typed row per real thing, with history.", "/learn/data-platform-architecture/bronze-to-silver/"),
    ("H3", "Silver to gold", "Gold", "Tables shaped for a use, reconciled every run.", "/learn/data-platform-architecture/gold/"),
    ("H4", "Gold to semantic", "Semantic", "Every metric defined once, with an owner.", "/concepts/semantic-layer/"),
    ("H5", "Semantic to experiences", "Experiences", "Dashboards, AI and agents give the same answer.", None),
]

# Where a concern has real content per hop: 2 = a lot, 1 = some, 0 = nothing special. Platform-wide concerns have no row here.
MATRIX = {
    "X3": (2, 2, 2, 1, 1), "X4": (1, 2, 2, 1, 0), "X5": (2, 2, 1, 0, 0), "X6": (2, 2, 2, 1, 1),
    "X7": (1, 1, 1, 1, 1), "X9": (2, 1, 1, 1, 2), "X10": (1, 2, 2, 2, 1), "X19": (2, 2, 2, 2, 1),
    "X11": (1, 1, 2, 2, 2), "X12": (2, 2, 1, 1, 2), "X13": (0, 1, 2, 2, 1), "X2": (2, 1, 2, 1, 1),
    "X15": (2, 2, 2, 0, 0), "X17": (1, 2, 2, 1, 1), "X24": (2, 2, 1, 1, 1),
}
KIND = {"hop": ("hop", "Per hop"), "both": ("both", "Both"), "wide": ("wide", "Platform-wide")}


def concern_link(c):
    cid, name, _g, _k, _p, slug, now = c
    return f"{P}{slug}/" if slug else now


# ---------------------------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------------------------

def plant():
    b = ""
    items = [("Screens", "catch what\narrived", "white"), ("Settling", "kept, nothing\nthrown away", "bronze"), ("Filters", "cleaned, one\nstandard", "silver"),
             ("Treated", "ready for\none use", "gold"), ("Labelled", "one name,\none meaning", "mint")]
    x = 20
    for i, (t, s, f) in enumerate(items):
        b += box(x, 20, 150, 84, t, s, f)
        if i < 4:
            b += arrow(x + 152, 62, x + 180, 62)
        x += 182
    b += f'<rect x="20" y="124" width="878" height="44" rx="12" fill="{FILL["butter"]}" stroke="#1F1F1F" stroke-width="1.3" stroke-dasharray="6 5"/>'
    b += text(459, 151, "at every stage: sample tests · meters · valves run from one control room · maintenance · safety", 15, fill="#1F1F1F")
    return svg(920, 180, b, "A water treatment plant: screens, settling, filters, treated water, labelled supply, with tests and meters at every stage."), \
        "A treatment plant has stages, and jobs that happen at every stage. A data platform has both too."


def picture():
    b = ""
    b += f'<rect x="160" y="8" width="820" height="50" rx="14" fill="{FILL["lilac"]}" stroke="#1F1F1F" stroke-width="1.4" stroke-dasharray="6 5"/>'
    b += text(570, 30, "Control plane: metadata manifest · orchestration · run log", 17, fill="#1F1F1F")
    b += text(570, 49, "a new table is a few lines of configuration; the concerns below switch on by default", 13)
    b += box(10, 84, 120, 186, "Upstreams", "sources we\ndon't own", "grey")
    b += box(1010, 84, 120, 186, "Downstreams", "BI, AI, agents,\nML, apps", "sky")
    layers = [("Landing", "files as\nreceived", "white"), ("Bronze", "raw, append-\nonly, replayable", "bronze"), ("Silver", "clean, typed,\none row per thing", "silver"),
              ("Gold", "shaped for a use,\nreconciled", "gold"), ("Semantic", "metrics defined\nonce", "mint")]
    xs = [160, 330, 500, 670, 840]
    for (t, s, f), x in zip(layers, xs):
        b += box(x, 84, 140, 100, t, s, f)
    hop_at = [(130, 160, "1"), (300, 330, "1"), (470, 500, "2"), (640, 670, "3"), (810, 840, "4"), (980, 1010, "5")]
    for x1, x2, n in hop_at:
        b += arrow(x1 + 2, 134, x2 - 2, 134)
        b += f'<circle cx="{(x1 + x2) / 2}" cy="112" r="10" fill="#fff" stroke="#1F1F1F" stroke-width="1.2"/>' + text((x1 + x2) / 2, 117, n, 13, fill="#1F1F1F")
    b += f'<rect x="330" y="204" width="480" height="52" rx="14" fill="{FILL["sky"]}" stroke="#1F1F1F" stroke-width="1.3" stroke-dasharray="6 5"/>'
    b += text(570, 226, "Streaming lane: the same layers, continuously, for the tables that need it", 15, fill="#1F1F1F")
    b += text(570, 245, "same contracts, same keys, same checks; only the trigger and the cost differ", 12)
    b += text(570, 282, "circled numbers are the five hops; the medallion is the line itself", 13)
    names = {g: [c[1] for c in CONCERNS if c[2] == g] for g, _q, _f in GROUPS}
    x, w = 10, 216
    for g, q, f in GROUPS:
        h = 46 + 19 * len(names[g])
        b += f'<rect x="{x}" y="300" width="{w}" height="{h}" rx="14" fill="{FILL[f]}" stroke="#1F1F1F" stroke-width="1.4"/>'
        b += text(x + w / 2, 322, g, 18, fill="#1F1F1F") + text(x + w / 2, 340, q, 11)
        for i, n in enumerate(names[g]):
            b += text(x + w / 2, 362 + i * 19, n, 14, fill="#1F1F1F")
        x += w + 10
    b += text(570, 532, "Cross-cutting: 24 jobs that apply at every hop, grouped by the question each one answers", 15, fill="#1F1F1F")
    return svg(1140, 545, b, "The data platform: a control plane above; upstreams, then landing, bronze, silver, gold and semantic, then downstreams, with a streaming lane; 24 cross-cutting concerns in five groups below."), \
        "The data platform, whole. The line is the medallion; the bands underneath are the concerns that run at every hop."


LEADERS_P = [
    "The platform is one line of five hops. Each hop makes one promise to the next, and the medallion layers (landing, bronze, silver, gold, semantic) are that line.",
    "Twenty-four jobs cut across every hop: quality checks, cost, security, orchestration, testing, environments and more. Each has one page; each hop page shows only what changes there.",
    "Platforms rarely fail in the layers. They fail in the cross-cutting jobs nobody owned: cost, freshness, how changes reach production, who may read what.",
    "Everything is declared as metadata, so adding a table is configuration and the cross-cutting jobs switch on by default.",
    "Streaming is a second speed on the same line, used only where a decision needs data in seconds or minutes.",
]

PQUESTIONS = [
    ("A", "Trust", "can I trust the number?", [
        ("Which checks run on every load, and what happens to a row that fails?",
         "Trust is earned row by row, at every hop.",
         "Bad rows are silently dropped or silently kept, and numbers drift for weeks.",
         "Contract checks at each hop, failing rows quarantined with a reason. Not: dropping rows, or failing a whole load for one bad row."),
        ("How do we prove the gold total matches the source?",
         "A pipeline that succeeded can still have lost rows.",
         "The board sees revenue that is 3% short, and nobody can say where it went.",
         "Reconcile counts and sums at every hop, every run, against source control totals. Not: 'the job is green'."),
    ]),
    ("B", "See", "can I see what happened and what it cost?", [
        ("Can we follow one run from a source file to a dashboard tile?",
         "Incidents are solved by tracing, and tracing needs ids that travel with the data.",
         "A wrong number takes three days and four teams to trace.",
         "A run id and batch id on every row, plus lineage collected automatically. Not: reading job logs by hand."),
        ("How fresh is each table promised to be, and who is told when it isn't?",
         "Freshness is a promise to a person, not a schedule.",
         "Users find stale data before the team does, and stop trusting the dashboard.",
         "A freshness target per table, split across the hops, with alerts to the owner. Not: 'it runs at 2 a.m.'."),
        ("Who pays for each table, and what does each hop cost?",
         "Cost without an owner only grows.",
         "The bill triples in a quarter and nobody can say which table or team caused it.",
         "Tag compute and storage by data product; show cost per hop and per table. Not: one shared bill."),
    ]),
    ("C", "Guard", "who may see and change what?", [
        ("Who may read each layer?",
         "Layers are promises; reading the wrong one breaks them.",
         "Reports are built on bronze and break whenever a source changes.",
         "Grant by layer: only the platform reads bronze, analysts read gold and semantic. Not: one big 'data readers' group."),
        ("Where is personal data, and can we erase one person everywhere?",
         "Privacy law applies to every copy, not just the source.",
         "A deletion request can't be met because nobody knows which tables hold the person.",
         "Tag personal data as it lands, mask in silver, erase using lineage. Not: a spreadsheet of PII tables."),
    ]),
    ("D", "Run", "does it run safely, every day?", [
        ("Is a new table configuration, or new code?",
         "Five hundred hand-written pipelines are five hundred ways to be different.",
         "Every pipeline handles deletes, retries and quality a little differently, and each fails in its own way.",
         "One metadata-driven framework; a new table is a manifest entry. Not: copy-paste pipelines."),
        ("Can every load be re-run without doubling a number?",
         "Re-runs are normal: failures, late data, fixes.",
         "A retried load doubles a day's sales.",
         "Merge on keys or replace whole partitions, so every hop is safe to repeat. Not: plain appends."),
        ("What runs when, and what waits for what?",
         "Hops depend on each other and on sources that run late.",
         "Gold builds on half-loaded silver, and the dashboard shows half a day.",
         "Trigger each hop on its inputs being complete, not on a clock. Not: guessing gaps between scheduled times."),
        ("How does a change reach production?",
         "Most incidents follow a change.",
         "A fix made by hand in production is overwritten by the next deploy.",
         "From git, through test, by a pipeline, with a way back. Not: edits in the production UI."),
        ("Which tables need streaming, and why?",
         "Streaming costs more to run and to operate.",
         "Always-on compute for data that is read once a morning.",
         "Batch by default; stream a table only when a decision needs it in seconds or minutes. Not: streaming everything because it's modern."),
    ]),
    ("E", "Self", "can it help fix itself, safely?", [
        ("What may agents and automation do on the platform?",
         "Automation that can change production can also break it.",
         "An agent 'fixes' a pipeline in production and corrupts a table.",
         "Agents propose changes by pull request; people approve; the normal pipeline deploys. Not: agents with production write access."),
    ]),
]

PDECISIONS = [
    ("How are pipelines built?", [
        ("One metadata-driven framework; a table is a manifest entry", "pursue", "Pursue. Every table gets the same handling of deletes, retries, quality and lineage."),
        ("A low-code tool, one flow per table", "when", "Pursue only for a small team with a few sources, and plan the move to metadata."),
        ("A hand-written pipeline per table", "drop", "Drop beyond a handful of tables. It doesn't scale and every one differs."),
    ]),
    ("How many layers?", [
        ("Landing, bronze, silver, gold, semantic", "pursue", "Pursue. Each makes one promise; together they cover replay, cleaning, shaping and meaning."),
        ("Skip landing", "when", "Pursue only when change data capture writes straight into bronze."),
        ("Extra medallions (platinum and so on)", "drop", "Drop. If you need another layer, you usually need more tables in gold."),
    ]),
    ("Batch or streaming?", [
        ("Batch by default, streaming per table where needed, same layers", "pursue", "Pursue. One line, two speeds, one set of rules."),
        ("Separate batch and streaming code paths for the same table", "drop", "Drop. Two versions of the same logic will disagree."),
        ("Stream everything", "drop", "Drop. Always-on cost and harder operations for no business gain."),
    ]),
    ("Where do the cross-cutting jobs live?", [
        ("Declared per table in the manifest, on by default", "pursue", "Pursue. Nobody can forget quality or lineage for a new table."),
        ("Added per project when someone asks", "drop", "Drop. They are added after the first incident, one table at a time."),
    ]),
    ("One platform or one per domain?", [
        ("One platform with shared services; domains own their schemas and tables", "pursue", "Pursue. Shared plumbing, local ownership."),
        ("Each domain runs its own full stack", "when", "Pursue only in a large organisation with strong domain teams, and with shared standards."),
    ]),
]

FAQ_P = [
    ("What are cross-cutting concerns in a data platform?",
     "Jobs that apply to every table at every layer rather than to one step: data quality, lineage, cost, security, privacy, orchestration, testing, environments and so on. They are best declared per table and switched on by default, not added after go-live."),
    ("Should orchestration and cost be handled per layer or end to end?",
     "Both. Each has an end-to-end view (the whole dependency graph, the budget per data product) and a slice at each hop (what triggers this hop, what this hop costs). We keep the end-to-end view on one page and show each hop's slice on its hop page."),
    ("Where does the medallion architecture fit?",
     "The medallion is the line through the platform: landing and bronze in the first hop, then silver, gold and semantic. The cross-cutting concerns run across it."),
    ("Is streaming a separate architecture?",
     "Usually not. It is a second speed on the same layers, with the same contracts, keys and checks. Only the trigger, state handling and running cost differ."),
]


def master_table():
    out = ""
    for g, q, f in GROUPS:
        out += f'<tr class="cat"><td colspan="5">{E(g)}<span>{E(q)}</span></td></tr>'
        for c in CONCERNS:
            if c[2] != g:
                continue
            cid, name, _g, kind, promise, slug, now = c
            k, lab = KIND[kind]
            page = (f'<a href="{P}{slug}/"><b>Open</b></a> <span class="tag ready">Ready</span>' if slug
                    else f'<span class="tag next">Coming</span> <a href="{now}">read now</a>')
            out += f"<tr><td class='id'>{cid}</td><td><b>{E(name)}</b></td><td><span class='kind {k}'>{lab}</span></td><td>{E(promise)}</td><td>{page}</td></tr>"
    return f'<div class="tw"><table class="t"><tr><th>#</th><th>Concern</th><th>Scope</th><th>The promise</th><th>Page</th></tr>{out}</table></div>'


def matrix():
    dot = {2: "●", 1: "○", 0: ""}
    head = "<tr><th>#</th><th>Concern</th>" + "".join(f"<th class='h'>{h}<br>{E(n)}</th>" for h, n, *_ in HOPS) + "<th class='h'>End to end</th></tr>"
    rows = ""
    for g, q, f in GROUPS:
        rows += f'<tr class="cat"><td colspan="8">{E(g)}<span>{E(q)}</span></td></tr>'
        for c in CONCERNS:
            if c[2] != g:
                continue
            cid, name, _g, kind, *_ = c
            nm = f'<a href="{concern_link(c)}">{E(name)}</a>'
            if kind == "wide":
                rows += f"<tr><td class='id'>{cid}</td><td>{nm}</td><td class='wide' colspan='5'>platform-wide: the same at every hop</td><td class='dot'>●</td></tr>"
            else:
                cells = "".join(f"<td class='dot'>{dot[v]}</td>" for v in MATRIX[cid])
                e2e = "●" if kind == "both" else "○"
                rows += f"<tr><td class='id'>{cid}</td><td>{nm}</td>{cells}<td class='dot'>{e2e}</td></tr>"
    return f'<div class="tw"><table class="t mx">{head}{rows}</table></div>'


def overview():
    pl_svg, pl_cap = plant()
    pic_svg, pic_cap = picture()
    hops = "".join(f"<tr><td class='id'>{h}</td><td><b>{E(n)}</b></td><td>{E(l)}</td><td>{E(pr)}</td><td><span class='tag next'>Coming</span></td>"
                   f"<td>{f'<a href=\"{b}\">build guide</a>' if b else '<span class=note>to come</span>'}</td></tr>" for h, n, l, pr, b in HOPS)
    qt, n_q = ds.q_table(PQUESTIONS)
    leaders = "".join(f"<li>{E(x)}</li>" for x in LEADERS_P)
    faq = "".join(f'<details class="faq"><summary>{E(a)}</summary><p>{E(b)}</p></details>' for a, b in FAQ_P)
    counts = {k: sum(1 for c in CONCERNS if c[3] == k) for k in KIND}
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › <a href="{BASE}">Data systems</a> › Data platform</p>
<p class="eyebrow" style="margin-top:22px">Data systems · block 2 of 3 · for data leaders, then builders</p>
<h1>The data platform, whole</h1>
<p class="promise">Every row arrives once, is checked at every hop, and every number has one meaning.</p>
<p class="lede">The platform in one picture: five hops along the line (the medallion), and 24 jobs that cut across every hop. Each hop and each job has its own page with the questions to chase, what breaks in production and the decisions to take.</p>
<div class="leaders"><h3>For leaders</h3><ul>{leaders}</ul></div>
<nav class="toc"><b>On this page</b><ol>
<li><a href="#plain">In plain words</a></li><li><a href="#picture">The whole picture</a></li><li><a href="#hops">Along the line: five hops</a></li>
<li><a href="#rule">Across the line: where each concern lives</a></li><li><a href="#concerns">All 24 concerns</a></li><li><a href="#matrix">Concerns by hop</a></li>
<li><a href="#streaming">Streaming: a second speed</a></li><li><a href="#questions">Questions to chase ({n_q})</a></li><li><a href="#decisions">Design decisions</a></li>
<li><a href="#faq">Questions people ask</a></li><li><a href="#next">Where to go next</a></li></ol></nav>

<section id="plain"><p class="eyebrow">In plain words</p><h2>A treatment plant has stages, and jobs at every stage</h2>
<p>Water passes through screens, settling tanks and filters before it is treated and labelled for use. That is the line. But some jobs are done at every stage: someone takes samples, meters record the flow, valves are run from one control room, and everything is maintained on a schedule. If samples were only tested at the tap, a problem would be found after the town drank it.</p>
<figure class="diagram">{pl_svg}<figcaption>{E(pl_cap)}</figcaption></figure>
<p>A data platform is the same. The <b>line</b> is the medallion: landing, bronze, silver, gold and semantic. The <b>jobs at every stage</b> are the cross-cutting concerns: quality, cost, security, orchestration, testing and the rest. This page shows both, and where each one is explained.</p></section>

<section id="picture"><p class="eyebrow">The whole picture</p><h2>The line, the control plane, and the concerns underneath</h2>
<figure class="diagram">{pic_svg}<figcaption>{E(pic_cap)}</figcaption></figure></section>

<section id="hops"><p class="eyebrow">Along the line</p><h2>Five hops: the medallion</h2>
<p>A hop is the move from one layer to the next. Landing and bronze are both in hop 1, because their single job is to get data in exactly as it was. Each hop page will follow the same template as the <a href="{BASE}upstreams/">Upstreams page</a>.</p>
<div class="tw"><table class="t"><tr><th>#</th><th>Hop</th><th>Layers it builds</th><th>The promise</th><th>Page</th><th>How we build it</th></tr>{hops}</table></div></section>

<section id="rule"><p class="eyebrow">Across the line</p><h2>Where each concern lives</h2>
<p><b>The rule:</b> each concern has one page with its end-to-end view, its questions and its decisions. Each hop page has one row for every concern that changes at that hop, linking to the concern's page. Nothing is written twice.</p>
<div class="tw"><table class="t"><tr><th>Scope</th><th>What it means</th><th>Where the detail goes</th><th>How many</th></tr>
<tr><td><span class="kind hop">Per hop</span></td><td>The concern works differently at each hop (a silver contract is not a gold contract).</td><td>Mostly on the hop pages; the concern page is a short summary.</td><td>{counts['hop']}</td></tr>
<tr><td><span class="kind both">Both</span></td><td>There is a whole-platform view and a slice at each hop. Orchestration: the dependency graph end to end, and what triggers this hop. Cost: the budget per data product, and this hop's cost drivers.</td><td>The end-to-end view on the concern page; each hop's slice on its hop page.</td><td>{counts['both']}</td></tr>
<tr><td><span class="kind wide">Platform-wide</span></td><td>Decided once and the same at every hop (environments, layout, audit).</td><td>The concern page only; hop pages just link to it.</td><td>{counts['wide']}</td></tr></table></div></section>

<section id="concerns"><p class="eyebrow">The master list</p><h2>All 24 concerns, grouped by the question they answer</h2>
<p>These are the 22 concerns from the <a href="/learn/data-platform-architecture/#concerns">architecture guide</a>, with Performance renamed "Performance & scale" to cover big-data handling, plus two more: <b>Layout</b> (catalogs, schemas and naming) and <b>Streaming</b>. Where our page isn't written yet, "read now" goes to the closest existing page.</p>
{master_table()}</section>

<section id="matrix"><p class="eyebrow">The grid</p><h2>Concerns by hop</h2>
<p>A filled dot means the concern has a lot to say at that hop; an open dot means a little. Platform-wide concerns are the same at every hop, so they live on their own page.</p>
{matrix()}</section>

<section id="streaming"><p class="eyebrow">Two speeds</p><h2>Streaming: the same line, faster</h2>
<p>Streaming is not a sixth layer or a second platform. A streaming table goes through the same layers with the same contracts, keys and quality checks. What changes is the trigger (each change, not a schedule), the state the job must keep (for de-duplication and late data), and the cost of compute that never stops.</p>
<p>Hops 1 and 2 stream most often: changes captured from a database flow into bronze and are merged into silver within minutes. Gold streams when a decision needs it, such as fraud or stock levels. The semantic layer and dashboards read the result either way. Streaming is a "both" concern, so its page will cover the end-to-end choices, and each hop page will show what changes at streaming speed. Until then, read <a href="/learn/real-time-analytics/">Real-time analytics, drawn simply</a>.</p></section>

<section id="questions"><p class="eyebrow">The question list</p><h2>The headline questions for the whole platform</h2>
<p>One or two questions per group, the ones a data leader should be able to answer. Each concern's page has the full list.</p>
{qt}</section>

<section id="decisions"><p class="eyebrow">Design decisions</p><h2>The decisions that shape the whole platform</h2>{ds.dec_html(PDECISIONS)}</section>

<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{faq}</section>

<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2>
<p><b>Ready now:</b> <a href="{P}layout/">Layout: catalogs, schemas and naming</a>, <a href="{P}environments/">Environments and CI/CD</a> and <a href="{P}cost/">Cost and FinOps</a>, with the <a href="{P}cost/calculator/">Databricks cost calculator</a>.</p>
<p><b>Before the platform:</b> <a href="{BASE}upstreams/">Upstreams: know your sources</a>.</p>
<p><b>How we build it:</b> <a href="/learn/data-platform-architecture/">Data platform architecture, drawn right</a> and <a href="/learn/medallion-architecture/">Medallion architecture, drawn right</a>.</p>
<p><b>Back up:</b> <a href="{BASE}">Data systems, end to end</a>.</p></section>"""
    title = "The data platform, whole"
    desc = "The data platform in one picture: five medallion hops, 24 cross-cutting concerns (orchestration, cost, quality, security, environments, streaming and more), where each one lives, and the questions and decisions for the whole platform."
    url = f"{SITE}{P}"
    return wb.page(title, desc, url, body, CSS + ds.ld(title, desc, url, [("Learn", "/learn/"), ("Data systems", BASE), ("Data platform", P)], FAQ_P))


# ---------------------------------------------------------------------------------------------
# Shared page shell for a concern page
# ---------------------------------------------------------------------------------------------

def concern_page(slug, cid, title, promise, lede, leaders, sections, questions, decisions, faq, next_html, desc, kind="wide"):
    qt, n_q = ds.q_table(questions)
    toc = "".join(f'<li><a href="#{sid}">{E(t)}</a></li>' for sid, t, _ in sections)
    toc += f'<li><a href="#questions">The question list ({n_q})</a></li><li><a href="#decisions">Design decisions</a></li><li><a href="#faq">Questions people ask</a></li><li><a href="#next">Where to go next</a></li>'
    secs = "".join(f'<section id="{sid}">{html}</section>' for sid, _t, html in sections)
    lead = "".join(f"<li>{E(x)}</li>" for x in leaders)
    faqh = "".join(f'<details class="faq"><summary>{E(a)}</summary><p>{E(b)}</p></details>' for a, b in faq)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › <a href="{BASE}">Data systems</a> › <a href="{P}">Data platform</a> › {E(title.split(':')[0])}</p>
<p class="eyebrow" style="margin-top:22px">Data platform · concern {cid} · <span class="kind {KIND[kind][0]}">{KIND[kind][1]}</span></p>
<h1>{E(title)}</h1>
<p class="promise">{E(promise)}</p>
<p class="lede">{E(lede)}</p>
<div class="leaders"><h3>For leaders</h3><ul>{lead}</ul></div>
<nav class="toc"><b>On this page</b><ol>{toc}</ol></nav>
{secs}
<section id="questions"><p class="eyebrow">The question list</p><h2>Every question, why we ask, and what breaks if nobody does</h2>{qt}</section>
<section id="decisions"><p class="eyebrow">Design decisions</p><h2>The decisions to take</h2>{ds.dec_html(decisions)}</section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{faqh}</section>
<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2>{next_html}
<p><b>Back up:</b> <a href="{P}">The data platform, whole</a>, with all 24 concerns.</p></section>"""
    url = f"{SITE}{P}{slug}/"
    return wb.page(title, desc, url, body, CSS + ds.ld(title, desc, url, [("Learn", "/learn/"), ("Data systems", BASE), ("Data platform", P), (title.split(":")[0], f"{P}{slug}/")], faq))


def table(head, rows, code_cols=()):
    h = "".join(f"<th>{E(x)}</th>" for x in head)
    body = ""
    for r in rows:
        body += "<tr>" + "".join(
            f"<td>{'<b>' + E(c) + '</b>' if i == 0 else ('<code>' + E(c) + '</code>' if i in code_cols else E(c))}</td>" for i, c in enumerate(r)) + "</tr>"
    return f'<div class="tw"><table class="t"><tr>{h}</tr>{body}</table></div>'


# ---------------------------------------------------------------------------------------------
# Layout: catalogs, schemas, storage and naming
# ---------------------------------------------------------------------------------------------

def layout_grid():
    b = ""
    envs = [("dev", "white"), ("test", "white"), ("prod", "butter")]
    cols = [("bronze", "bronze"), ("silver", "silver"), ("gold", "gold"), ("semantic", "mint"), ("ops", "lilac")]
    for j, (c, f) in enumerate(cols):
        b += text(200 + j * 170, 26, c, 17, fill="#1F1F1F")
    for i, (e, ef) in enumerate(envs):
        y = 42 + i * 70
        b += text(55, y + 34, e, 18, fill="#1F1F1F")
        for j, (c, f) in enumerate(cols):
            x = 125 + j * 170
            b += f'<rect x="{x}" y="{y}" width="150" height="52" rx="12" fill="{FILL[f]}" stroke="#1F1F1F" stroke-width="{2.2 if e == "prod" else 1.3}"/>'
            b += f'<text x="{x + 75}" y="{y + 31}" text-anchor="middle" font-size="15" font-family="monospace" fill="#1F1F1F">{e}_{c}</text>'
    b += text(530, 270, "one catalog per environment and layer · each with its own storage, retention and grants", 14)
    b += text(530, 292, "inside each: one schema per source (bronze) or per business domain (silver, gold, semantic)", 14)
    return svg(1000, 305, b, "A grid of catalogs: dev, test and prod rows; bronze, silver, gold, semantic and ops columns; names like prod_silver."), \
        "Fifteen catalogs for three environments. The prod row is the one people read; the rest are for building and testing."


L_LEADERS = [
    "Every table has a three-part name: catalog, schema, table. How those three parts are used decides how environments are kept apart, who can read what, and where data is stored.",
    "We recommend one catalog per environment and layer (for example prod_silver), one schema per source system in bronze, and one schema per business domain in silver, gold and semantic.",
    "That turns the most important rules into one grant each: analysts read prod_gold and prod_semantic; only the platform reads bronze; nothing in dev can write to prod.",
    "Decide this before the first table. Renaming later breaks every job, report and agent tool that uses the old names.",
]

WHAT_GOES = [
    ("Workspace or account", "Compute, people and jobs for one environment", "One per environment", "the prod workspace"),
    ("Catalog", "One layer of one environment", "Environment and layer", "prod_silver"),
    ("Schema in bronze", "Tables from one source system, in its own shape", "By source system", "prod_bronze.sap_ecc"),
    ("Schema in silver and gold", "Tables for one business domain", "By business domain", "prod_silver.sales, prod_gold.finance"),
    ("Shared dimensions", "Customer, product, calendar used by every domain", "One shared schema", "prod_gold.shared.dim_customer"),
    ("Schema in semantic", "Metric definitions for one domain", "By business domain", "prod_semantic.sales"),
    ("Landing", "Files as received, not tables", "A storage volume per source", "prod_bronze.sap_ecc.landing (volume)"),
    ("Quarantine", "Rows that failed a check, with the reason", "Next to the table they failed", "prod_silver.sales.orders_quarantine"),
    ("Ops", "Metadata store, run log, quality results, cost", "By function", "prod_ops.run_log"),
    ("Sandboxes", "Personal experiments", "One schema per person, dev only, with expiry", "dev_sandbox.asha"),
]

NAMING = [
    ("Bronze tables", "The source object's own name, lower case", "prod_bronze.sap_ecc.vbak", "Anyone can find the source table"),
    ("Silver tables", "The business entity, plural", "prod_silver.sales.orders", "Names the real thing, not the source"),
    ("Gold facts and dimensions", "fact_ and dim_ prefixes", "prod_gold.sales.fact_order_line", "The grain and role are clear"),
    ("Gold aggregates and marts", "agg_ prefix with the grain", "prod_gold.sales.agg_sales_daily", "The time grain is in the name"),
    ("Semantic", "Domain and _metrics", "prod_semantic.sales.sales_metrics", "One place for each domain's metrics"),
    ("Views for consumers", "The stable name consumers use", "prod_gold.sales.orders_v", "Tables can change behind the view"),
]

ACCESS = [
    ("*_bronze", "The ingestion service only", "Silver jobs only"),
    ("*_silver", "Silver jobs only", "Gold jobs, data engineers, data scientists (personal data masked)"),
    ("*_gold", "Gold jobs only", "The semantic layer, BI service, analysts, ML"),
    ("*_semantic", "The deployment pipeline", "Everyone with rights to the domain: dashboards, conversation UIs, agent tools"),
    ("*_ops", "Platform services", "The platform team and auditors"),
    ("dev_*", "Engineers", "Engineers"),
]

L_PLATFORMS = [
    ("Databricks", "catalog.schema.table", "Unity Catalog; volumes for landing files; bind each catalog to its environment's workspace so dev can't write prod."),
    ("Microsoft Fabric", "workspace / lakehouse / schema / table", "A workspace per environment (and often per layer), a lakehouse per layer, schemas by domain; OneLake shortcuts instead of copies."),
    ("Snowflake", "database.schema.table", "A database per environment and layer; zero-copy clones help fill test."),
    ("Google BigQuery", "project.dataset.table", "A project per environment; with only two levels inside, name datasets layer_domain (silver_sales)."),
    ("AWS (Glue, Lake Formation, S3 Tables)", "catalog / database / table", "An account per environment; databases named layer_domain; Lake Formation grants per database."),
    ("Open source (Iceberg REST, Polaris, Unity OSS)", "catalog / namespace / table", "Namespaces can nest (silver.sales), so the recommended layout fits directly."),
]

L_QUESTIONS = [
    ("A", "Isolation", "keeping environments apart", [
        ("Can a job running in dev write to a production table?",
         "One wrong parameter shouldn't be able to touch production.",
         "A developer's test run overwrites the production orders table.",
         "A workspace per environment, with each catalog bound to its own workspace. Not: environments kept apart only by a name prefix."),
        ("Where do people experiment, and can experiments leak into production?",
         "Scratch tables become dependencies the moment someone builds a report on them.",
         "A personal table in a production schema feeds a board report; its owner leaves.",
         "A dev sandbox schema per person, with expiry. Not: scratch tables in production schemas."),
    ]),
    ("B", "Naming", "names people can read and trust", [
        ("Is there one written naming standard, and is it checked automatically?",
         "Names are the first thing people use to find and trust data.",
         "orders, Orders_v2 and ord_final all exist, and nobody knows which one is right.",
         "Write the standard into the manifest validator, so a bad name fails the build. Not: a wiki page."),
        ("Is the environment name written into code anywhere?",
         "Code is promoted unchanged; the environment must come from outside it.",
         "Code promoted to production still writes to the dev catalog.",
         "The catalog name comes from the deployment target's settings. Not: if env == 'prod' in code."),
        ("Do consumers read tables directly, or stable views and the semantic layer?",
         "Tables get rebuilt and renamed; consumers shouldn't notice.",
         "A table rename breaks 40 dashboards and three agent tools overnight.",
         "Publish through views and the semantic layer; change tables behind them. Not: dashboards on raw gold tables."),
    ]),
    ("C", "Splitting", "how catalogs and schemas are divided", [
        ("Do we split schemas by source, by domain, or by team?",
         "The split should outlive reorganisations.",
         "Team-named schemas have to be moved after every reorg.",
         "Bronze by source system; silver, gold and semantic by business domain. Not: by team."),
        ("Which domains are there, and who owns each one?",
         "A schema without an owner collects orphan tables.",
         "Nobody can say whether a table is safe to drop, so nothing is ever dropped.",
         "A short domain list with a named owner each, kept in metadata. Not: domains invented per project."),
        ("Where do shared dimensions such as customer, product and calendar live?",
         "Every domain needs them; there should be one copy.",
         "Three customer dimensions with three different customer counts.",
         "One shared schema in gold that all domains read. Not: a copy per domain."),
    ]),
    ("D", "Access", "who reads which layer", [
        ("Who may read each layer?",
         "Layers are promises; reading the wrong one breaks them.",
         "Reports built on bronze break whenever a source changes.",
         "Grant at catalog level by layer, as in the access table above. Not: one 'data readers' group for everything."),
        ("Where does personal data sit, masked and unmasked?",
         "Masked copies drift from the original.",
         "A 'PII-free' copy of a table misses a new column with email addresses.",
         "One table with column masks and row filters by role. Not: separate copies with columns removed."),
    ]),
    ("E", "Storage and retention", "where data sits and for how long", [
        ("Does each catalog have its own storage location, retention and encryption key?",
         "Layers need different retention and cost tiers.",
         "Landing files can't be cleaned after 7 days without touching gold; storage cost can't be split.",
         "A storage location per catalog, with its own lifecycle rules. Not: one bucket for everything."),
        ("How long is each layer kept, including table history (time travel)?",
         "Too short and you can't recover from a bad load; too long and storage grows forever.",
         "A bad load from last week can't be undone, or the storage bill doubles each year.",
         "Retention per layer in the manifest: landing days, bronze long and cheap, silver and gold by business need. Not: the default."),
    ]),
    ("F", "Change", "moving and renaming once in use", [
        ("How will we move or rename a table that people already use?",
         "Something will need to move eventually.",
         "A move breaks unknown consumers, found one complaint at a time.",
         "Use lineage to find consumers, keep the old name as a view for a deprecation period, then remove it. Not: rename and wait for complaints."),
    ]),
]

L_DECISIONS = [
    ("How do catalogs split?", [
        ("One per environment and layer (prod_silver)", "pursue", "Pursue. One grant per layer, one storage location per layer, environments fully apart."),
        ("One per environment; schemas carry layer and domain (prod.silver_sales)", "when", "Pursue only for a small platform with a few domains, where fewer catalogs matter more."),
        ("One per domain, with layers as schemas (sales.silver)", "when", "Pursue only when domain teams own their data end to end (data mesh), with environments kept apart by workspace."),
        ("One catalog, environments as name prefixes", "drop", "Drop. Nothing stops dev from writing to prod."),
    ]),
    ("How do schemas split?", [
        ("Bronze by source; silver, gold and semantic by business domain", "pursue", "Pursue. Bronze mirrors the sources, the rest mirrors the business."),
        ("By team", "drop", "Drop. Teams change more often than the business does."),
    ]),
    ("How do consumers read data?", [
        ("Through views and the semantic layer", "pursue", "Pursue. Tables can change without breaking anyone."),
        ("Directly from gold tables", "when", "Pursue only for a few known consumers, such as ML training jobs."),
    ]),
    ("Where does landing go?", [
        ("A storage volume per source inside the bronze catalog", "pursue", "Pursue. Same grants and lifecycle as bronze, short retention."),
        ("Its own catalog", "when", "Pursue only when landing is filled by a separate team or tool with separate access."),
    ]),
]

L_FAQ = [
    ("Should a catalog be per environment or per layer?",
     "Both, combined: one catalog per environment and layer, such as prod_silver. That keeps environments apart and lets one grant control who reads each layer. Smaller platforms can use one catalog per environment with layer and domain in the schema name."),
    ("Should bronze be organised by source system or by domain?",
     "By source system. Bronze keeps data in the source's own shape, so grouping by source makes it easy to find and replay. From silver onwards, data is shaped around the business, so it is grouped by domain."),
    ("Where do metric views or the semantic model live?",
     "In their own semantic catalog per environment, by domain, so consumers can be given the semantic layer and gold without seeing silver or bronze."),
]


def layout():
    g_svg, g_cap = layout_grid()
    sections = [
        ("plain", "In plain words", f"""<p class="eyebrow">In plain words</p><h2>Like a library: branch, floor, shelf, book</h2>
<p>A city library system has a branch in each area, floors inside each branch, shelves by subject on each floor, and books on the shelves. Members may use the reading room, but not the receiving room where new deliveries are unpacked. Anyone can find a book from its address.</p>
<p>A data platform names tables the same way. The <b>environment</b> is the branch (dev, test, prod). The <b>layer</b> is the floor (bronze is the receiving room; gold and semantic are the reading rooms). The <b>domain</b> is the shelf (sales, finance). The <b>table</b> is the book. Most platforms have three name levels (catalog, schema, table), so two of these four have to share one level. Which two share is the main decision on this page.</p>"""),
        ("grid", "The recommended layout", f"""<p class="eyebrow">The picture</p><h2>One catalog per environment and layer</h2>
<figure class="diagram">{g_svg}<figcaption>{E(g_cap)}</figcaption></figure>"""),
        ("what", "What goes where", f"""<p class="eyebrow">What goes where</p><h2>Catalog, schema, table, and the things that aren't tables</h2>
{table(["Level", "What it holds", "How we split it", "Example"], WHAT_GOES, code_cols=(3,))}"""),
        ("naming", "Naming", f"""<p class="eyebrow">Naming</p><h2>Table names by layer</h2>
{table(["Where", "Rule", "Example", "Why"], NAMING, code_cols=(2,))}"""),
        ("access", "Who reads what", f"""<p class="eyebrow">Access</p><h2>One grant per layer</h2>
<p>Because each layer is its own catalog, the main access rules are short. Personal data inside silver and gold is further protected with column masks by role.</p>
{table(["Catalog", "Who writes", "Who reads"], ACCESS)}"""),
        ("platforms", "On each platform", f"""<p class="eyebrow">Concept vs product</p><h2>The same layout on each platform</h2>
<p>Every platform has a name hierarchy; only the words and the number of levels differ.</p>
{table(["Platform", "Name levels", "How the layout maps"], L_PLATFORMS, code_cols=(1,))}
<p class="note">Product features change often; check the current docs before you build.</p>"""),
    ]
    nxt = f"""<p><b>Next concern:</b> <a href="{P}environments/">Environments and CI/CD</a>, which decides how changes move between the dev, test and prod rows above.</p>
<p><b>Related:</b> <a href="/writing/unity-catalog-done-right/">Unity Catalog done right</a> (blog) and <a href="/learn/data-platform-architecture/metadata-store/">the metadata store</a>, where the naming rules are checked.</p>"""
    return concern_page("layout", "X23", "Layout: catalogs, schemas and naming",
                        "From a table's full name you can tell its environment, layer and domain, and who may read it.",
                        "Where landing, bronze, silver, gold and semantic physically live: what becomes a catalog, what becomes a schema, how tables are named, and how that turns access, retention and isolation into simple rules.",
                        L_LEADERS, sections, L_QUESTIONS, L_DECISIONS, L_FAQ, nxt,
                        "How to lay out a data platform's catalogs and schemas: one catalog per environment and layer, schemas by source in bronze and by domain after, naming rules, access per layer, and the same layout on Databricks, Fabric, Snowflake, BigQuery and AWS.")


# ---------------------------------------------------------------------------------------------
# Environments and CI/CD
# ---------------------------------------------------------------------------------------------

def env_picture():
    b = ""
    b += f'<rect x="20" y="10" width="900" height="46" rx="12" fill="{FILL["lilac"]}" stroke="#1F1F1F" stroke-width="1.3"/>'
    b += text(470, 39, "git: code · manifests · table changes · grants · jobs · infrastructure · semantic definitions · dashboards", 15, fill="#1F1F1F")
    envs = [(60, "dev", "build and try", "white"), (380, "test", "prove it, at real size", "butter"), (700, "prod", "the real thing", "mint")]
    for x, n, s, f in envs:
        b += box(x, 100, 180, 90, n, s, f)
    b += arrow(150, 58, 150, 98, "") + arrow(470, 58, 470, 98, "") + arrow(790, 58, 790, 98, "")
    b += text(150, 80, "", 12)
    b += arrow(242, 130, 378, 130, "merge, then deploy") + arrow(562, 130, 698, 130, "approve, then deploy")
    b += f'<line x1="700" y1="178" x2="562" y2="178" stroke="#1F1F1F" stroke-width="1.5" stroke-dasharray="5 4" marker-end="url(#ah)"/>'
    b += f'<line x1="378" y1="178" x2="242" y2="178" stroke="#1F1F1F" stroke-width="1.5" stroke-dasharray="5 4" marker-end="url(#ah)"/>'
    b += text(631, 206, "masked sample of data", 12) + text(310, 206, "smaller masked sample", 12)
    b += text(470, 240, "code moves up, only through the pipeline · data never moves up · only masked data moves down", 15, fill="#1F1F1F")
    return svg(940, 255, b, "Git at the top deploys to dev, test and prod. Code moves from dev to test to prod through the pipeline; masked data samples move down from prod."), \
        "Code moves up through the pipeline. Data never moves up; only masked samples move down."


ENVS = [
    ("dev", "Engineers, each in their own space", "Small masked samples and synthetic edge cases", "Engineers deploy their own branch", "Static checks, unit tests"),
    ("test", "The CI pipeline; testers", "A masked copy of production, at real volume where it matters", "Only the pipeline, after merge", "Integration, contract and data tests, reconciliation, performance"),
    ("prod", "Service accounts only; people read", "Real data", "Only the pipeline, after approval", "Smoke tests after deploy, then monitoring"),
    ("UAT or pre-prod (optional)", "Business users signing off", "Masked production data", "Only the pipeline", "User acceptance; needed in some regulated settings"),
]

IN_GIT = [
    ("Transformation code", "SQL, PySpark, dbt models"),
    ("Manifests and metadata", "Table entries, quality rules, schedules, retention"),
    ("Table changes", "Migrations: add column, change type, backfill steps"),
    ("Permissions", "Grants, masks and row filters, as code"),
    ("Jobs and orchestration", "Job and pipeline definitions per environment target"),
    ("Infrastructure", "Workspaces, storage, networks, catalogs (Terraform and similar)"),
    ("Semantic definitions", "Metric views and semantic models"),
    ("Dashboards", "Exported definitions, deployed like code"),
    ("Tests", "Unit, contract and data tests, and their test data"),
]

STAGES_CI = [
    ("1 · Pull request", "Static checks, manifest validation, unit tests, review", "Syntax errors, bad names, broken rules, risky code patterns"),
    ("2 · Merge and deploy to test", "The pipeline deploys everything from git to test", "Anything that only works on the developer's machine"),
    ("3 · Test", "Integration, contract and data tests on masked data; reconciliation; performance at volume", "Wrong joins, broken contracts, slow merges, numbers that don't add up"),
    ("4 · Approve", "A named person approves, seeing test results and the change list", "Changes nobody expected"),
    ("5 · Deploy to prod", "The same artefact, with prod settings", "Drift between environments"),
    ("6 · Smoke test and watch", "A small run and comparison; freshness and quality alerts", "Problems only real data shows; roll back if needed"),
]

ENV_PLATFORMS = [
    ("Databricks", "A workspace per environment; catalogs bound to their workspace", "Asset Bundles with a target per environment; Terraform for workspaces; service principals deploy"),
    ("Microsoft Fabric", "A workspace per stage", "Deployment pipelines plus git integration; deployment rules switch connections per stage"),
    ("AWS", "An account per environment", "CDK, Terraform or CloudFormation; CodePipeline or GitHub Actions"),
    ("Google Cloud", "A project per environment", "Terraform; Cloud Build; Dataform release and workflow configurations"),
    ("Snowflake", "A database or account per environment", "Terraform or schemachange; zero-copy clones to fill test"),
    ("Open source", "Separate clusters or namespaces", "Terraform, GitHub Actions, dbt targets, Airflow deployments"),
]

V_LEADERS = [
    "Code moves up from dev to test to production through a pipeline. Data never moves up; only masked samples move down.",
    "Nobody changes production by hand. A pipeline deploys from git after tests pass and a named person approves.",
    "The hard parts of data CI/CD are not the code. They are realistic test data, source systems whose own test environments hold little real data, and changing tables that already hold years of history.",
    "Everything lives in git: code, table definitions, permissions, schedules, semantic definitions, dashboards and infrastructure, so any environment can be rebuilt.",
    "A realistic test environment costs money. Finding the same problem in production costs more.",
]

V_QUESTIONS = [
    ("A", "Environments", "how many, and kept apart how", [
        ("How many environments are there, and what is each one for?",
         "An environment with three jobs does none of them well.",
         "'Test' is used for demos, user sign-off and development at once, and is never stable.",
         "Dev, test and prod, each with one purpose; add UAT only when sign-off needs it. Not: one shared non-prod."),
        ("Are environments separate accounts or workspaces, with separate storage?",
         "Shared storage means a test job can delete production files.",
         "A clean-up script in test empties a production folder.",
         "Separate workspaces or accounts and storage per environment. Not: folders named /dev and /prod in one bucket."),
        ("Are environments built from code, and rebuilt regularly?",
         "Hand-built environments drift apart.",
         "It works in test and fails in production because a setting differs.",
         "Infrastructure as code for every environment; rebuild test from it on a schedule. Not: clicking in the console."),
    ]),
    ("B", "Data in lower environments", "what test data looks like", [
        ("What data does test hold, and at what size?",
         "Logic and performance problems only show on realistic data.",
         "Tests pass on 1,000 synthetic rows; production has 2 billion, skewed to one customer, and the merge runs for hours.",
         "A masked copy of production, plus volume tests on the biggest tables. Not: hand-made rows only."),
        ("Is personal data masked before it leaves production?",
         "Lower environments have more people and weaker controls.",
         "Real customer data ends up on a contractor's laptop.",
         "Mask inside production, consistently, before copying down. Not: copy first, mask later."),
        ("How is test data refreshed?",
         "Stale test data misses new codes and new shapes.",
         "A new status code appears in production that test has never seen; the release breaks.",
         "A scheduled refresh of the masked copy. Not: a copy taken once at the start of the project."),
    ]),
    ("C", "Source systems' own environments", "the part teams forget", [
        ("Does each source have a test environment, and does it hold realistic data?",
         "Source test systems often hold a dozen made-up records.",
         "Integration tests pass against the source's test system; production breaks on the first real file.",
         "Use the source's test system to prove connectivity; test logic on masked production copies. Not: trusting source test data."),
        ("Can test connect to sources without touching production sources?",
         "A test pipeline pointed at a production source can load it, or write back to it.",
         "A test job sends reverse-ETL updates into the production CRM.",
         "Separate connections per environment, set by the deployment target; write-backs go to a sandbox outside prod. Not: shared connection strings."),
    ]),
    ("D", "Promotion", "how a change reaches production", [
        ("Who can deploy to production, and how?",
         "Most incidents follow a change.",
         "A hotfix made in the production UI is overwritten by the next deploy.",
         "Only the pipeline's service account deploys; break-glass access is logged and reviewed. Not: personal admin rights in prod."),
        ("What must pass before a change reaches production?",
         "Gates turn 'we think it works' into evidence.",
         "A change that broke reconciliation in test is approved because nobody looked.",
         "Required checks in the pipeline, with results shown at approval. Not: an approval button with no evidence."),
        ("How do environment settings and secrets differ, and where do they live?",
         "Code is promoted unchanged; only settings change.",
         "A production password is found in dev settings, or code still points at dev after promotion.",
         "Settings per deployment target; secrets in a vault per environment. Not: if env == 'prod' in code."),
    ]),
    ("E", "Changing tables that hold data", "the hard part of data CI/CD", [
        ("How do we change the schema of a table with years of data?",
         "A data table can't be thrown away and recreated like a web page.",
         "A column-type change fails halfway, or a rebuild takes three days.",
         "Expand and contract: add the new column, backfill, move readers, then drop the old one, as migrations in git. Not: ALTER by hand in production."),
        ("When logic changes, how is history rebuilt, and who is told?",
         "A deploy can quietly change last year's numbers.",
         "Finance finds that last year's revenue moved after a release.",
         "Backfills are planned jobs: compare before and after, then announce. Not: letting the next run rewrite history."),
        ("What happens to streaming jobs and their checkpoints on deploy?",
         "A streaming job's saved position decides what it reads next.",
         "A redeploy re-reads a week of events, or skips an hour.",
         "Compatible changes keep the checkpoint; incompatible ones start a new one with a planned backfill. Not: deleting checkpoints to make it start."),
    ]),
    ("F", "Rollback", "the way back", [
        ("Can we undo a bad release: both the code and the data it wrote?",
         "Rolling back code doesn't fix data already written.",
         "The code is rolled back, but a day of wrong rows stays in gold.",
         "Keep table history (time travel) and restore; for big changes, build the new table alongside and switch a view. Not: code-only rollback."),
    ]),
    ("G", "Cost", "what non-production costs", [
        ("What do dev and test cost, and when are they switched off?",
         "Non-production can quietly cost as much as production.",
         "A full-size test environment runs all weekend, every weekend.",
         "Smaller compute, auto-stop, sampled data, scheduled shutdowns; scale up only for volume tests. Not: prod-sized and always on."),
    ]),
]

V_DECISIONS = [
    ("How many environments?", [
        ("Dev, test, prod", "pursue", "Pursue. Each has one purpose."),
        ("Add UAT or pre-prod", "when", "Pursue only when business sign-off or regulation needs a separate stage."),
        ("Dev and prod only", "drop", "Drop. Changes are first tested on real users."),
    ]),
    ("What data goes in test?", [
        ("A masked copy of production, plus synthetic edge cases", "pursue", "Pursue. Real shapes and volumes, no real people."),
        ("Synthetic data only", "when", "Pursue only before production exists (a new system)."),
        ("An unmasked copy of production", "drop", "Drop. It's a data breach waiting to happen."),
    ]),
    ("How do changes deploy?", [
        ("A pipeline from git, with infrastructure as code", "pursue", "Pursue. Every environment is built the same way."),
        ("By hand in each environment's UI", "drop", "Drop. Environments drift and nobody knows what changed."),
    ]),
    ("How do environments differ in code?", [
        ("Settings per deployment target", "pursue", "Pursue. The same artefact runs everywhere."),
        ("if env == 'prod' branches in code", "drop", "Drop. The production path is never tested."),
    ]),
    ("How do big tables change shape?", [
        ("Expand and contract, as migrations in git", "pursue", "Pursue. Readers never see a broken table."),
        ("Drop and rebuild", "when", "Pursue only for small tables that rebuild in minutes."),
        ("Build the new version alongside and switch a view", "when", "Pursue for large or risky logic changes; switching back is instant."),
    ]),
]

V_FAQ = [
    ("How many environments does a data platform need?",
     "Usually three: dev for building, test for proving on realistic masked data, and prod. Add a user-acceptance stage only when business sign-off or regulation requires one."),
    ("Should test use production data?",
     "A masked copy of production, yes: realistic shapes and volumes are what find problems. An unmasked copy, no. Mask inside production, consistently, before anything is copied down."),
    ("What is different about CI/CD for data compared with apps?",
     "Tables hold history, so you can't simply replace them; changes need migrations and planned backfills. Tests need realistic data. And a rollback must undo the data a bad release wrote, not just the code."),
]


def environments():
    e_svg, e_cap = env_picture()
    sections = [
        ("plain", "In plain words", f"""<p class="eyebrow">In plain words</p><h2>Rehearse, dress rehearsal, then opening night</h2>
<p>A theatre rehearses in a practice room, then holds a dress rehearsal on the real stage with real lights, then opens to the public. Nobody rewrites the script on opening night. If something goes wrong, they know exactly which version of the script was played.</p>
<p>A data platform works the same way. <b>Dev</b> is the practice room. <b>Test</b> is the dress rehearsal: real size, real shapes, masked people. <b>Prod</b> is opening night. Every change travels from git through test to production by the same pipeline, so it's always known what is running and how to go back.</p>"""),
        ("picture", "The picture", f"""<p class="eyebrow">The picture</p><h2>Code moves up, masked data moves down</h2>
<figure class="diagram">{e_svg}<figcaption>{E(e_cap)}</figcaption></figure>"""),
        ("envs", "The environments", f"""<p class="eyebrow">The environments</p><h2>What each environment is for</h2>
{table(["Environment", "Who works there", "What data", "How changes arrive", "What is checked"], ENVS)}
<p>The <a href="{P}layout/">layout page</a> shows how these become catalogs: dev_*, test_* and prod_*.</p>"""),
        ("git", "What lives in git", f"""<p class="eyebrow">Everything as code</p><h2>What lives in git</h2>
<p>If it isn't in git, it can't be reviewed, tested, promoted or rebuilt.</p>
{table(["What", "Examples"], IN_GIT)}"""),
        ("pipeline", "The pipeline", f"""<p class="eyebrow">CI/CD</p><h2>Six stages from pull request to production</h2>
{table(["Stage", "What happens", "What it catches"], STAGES_CI)}
<p>Stage 1 is where <a href="/learn/shift-left/">shift-left checks</a> run; stage 3 is the <a href="/learn/data-platform-architecture/testing/">test architecture for data</a>.</p>"""),
        ("platforms", "On each platform", f"""<p class="eyebrow">Concept vs product</p><h2>The same idea on each platform</h2>
{table(["Platform", "Keeping environments apart", "Deploying"], ENV_PLATFORMS)}
<p class="note">Product features change often; check the current docs before you build.</p>"""),
    ]
    nxt = f"""<p><b>Related concerns:</b> <a href="{P}layout/">Layout: catalogs, schemas and naming</a>; Testing (coming; until then, <a href="/learn/data-platform-architecture/testing/">test architecture for data</a>).</p>
<p><b>Read more:</b> <a href="/writing/databricks-asset-bundles/">CI/CD for Databricks with Asset Bundles</a> (blog), <a href="/concepts/ci-cd/">CI/CD</a> and <a href="/concepts/iac/">infrastructure as code</a>.</p>"""
    return concern_page("environments", "X16", "Environments and CI/CD",
                        "Every change reaches production the same way: from git, tested where it looks like production, promoted by a pipeline, and easy to undo.",
                        "How dev, test and production are kept apart, what data each one holds, how a change travels to production, and the problems special to data: test data, source systems' own test environments, and changing tables that already hold years of history.",
                        V_LEADERS, sections, V_QUESTIONS, V_DECISIONS, V_FAQ, nxt,
                        "Environments and CI/CD for a data platform: dev, test and prod, masked test data, source systems' test environments, the six-stage pipeline, schema changes on big tables, rollback of data and code, and the same on each platform.")


def main():
    out = ROOT / "learn" / "data-systems" / "platform"
    for sub, html in (("", overview()), ("layout", layout()), ("environments", environments())):
        d = out / sub
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(html)
    print("data platform ->", out)


if __name__ == "__main__":
    main()
