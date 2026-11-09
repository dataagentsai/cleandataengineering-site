"""Data systems, end to end: the leader-first story at /learn/data-systems/.

    python3 _guides/data_systems.py

Three zoom levels (agreed with the owner, 9 Nov 2026):
  Level 0  /learn/data-systems/                         upstreams, the data platform, downstreams
  Level 1  /learn/data-systems/upstreams/               one page per block (upstreams first)
  Level 2  one page per hop (sources to bronze ... semantic to experiences), still to come
Plus a printable client questionnaire at /learn/data-systems/upstreams/questionnaire/.

Every page uses one template: the promise in one line, a summary for leaders, ONE question
table grouped by category (question, why we ask, what breaks in production, do this / not
this), design decisions with a verdict, then a link to the existing "how we build it" page.
These pages say what to ask and decide; /learn/data-platform-architecture/ says how to build.
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "_paths"))
spec = importlib.util.spec_from_file_location("writing_build", ROOT / "_writing" / "build.py")
wb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wb)
from diagrams import FILL, arrow, box, svg, text  # noqa: E402

E = wb.E
SITE = wb.SITE
BASE = "/learn/data-systems/"
MODIFIED = "2026-11-09"

CSS = """<style>
  .crumbs { font-size:13.5px; color:var(--faint); margin:28px 0 0; } .crumbs a { color:var(--muted); }
  .lede { font-size:20px; color:var(--ink-soft); }
  .toc { border:var(--line); border-radius:var(--wob); padding:12px 20px; background:var(--rose-wash); font-size:15px; margin:20px 0; }
  .toc ol { margin:6px 0 0; padding-left:20px; columns:2; column-gap:30px; } .toc li { margin:3px 0; }
  .diagram { margin:18px 0; border:var(--line); border-radius:var(--wob); padding:14px 16px; background:#fff; overflow-x:auto; }
  .diagram svg { width:100%; min-width:640px; height:auto; display:block; } .diagram text { font-family:var(--hand); }
  .diagram figcaption { font-size:13.5px; color:var(--muted); margin-top:6px; }
  .promise { font-family:var(--hand); font-size:26px; margin:8px 0 4px; }
  .leaders { border:var(--line); border-radius:var(--wob); padding:14px 20px; background:var(--butter-wash); margin:16px 0; }
  .leaders h3 { margin:0 0 6px; font-size:22px; } .leaders ul { margin:0; padding-left:20px; } .leaders li { margin:5px 0; }
  .cards { display:grid; grid-template-columns:repeat(3, 1fr); gap:14px; margin:14px 0; }
  .card { border:var(--line); border-radius:var(--wob); padding:14px 18px; background:var(--w, #fff); }
  .card h3 { margin:0 0 4px; font-size:24px; } .card p.one { margin:0 0 8px; color:var(--ink-soft); }
  .card ul { margin:0 0 10px; padding-left:18px; font-size:15px; } .card li { margin:4px 0; }
  .tag { display:inline-block; font-size:12px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; border:1.5px solid var(--ink); border-radius:999px; padding:1px 10px; background:#fff; }
  .tag.ready { background:var(--mint-wash); } .tag.next { background:var(--butter-wash); }
  .tw { overflow-x:auto; } table.t { border-collapse:collapse; width:100%; font-size:14.5px; margin:8px 0 18px; }
  table.t th, table.t td { text-align:left; padding:7px 9px; border-bottom:1.5px dashed var(--rule-firm); vertical-align:top; }
  table.t th { font-size:11.5px; letter-spacing:.08em; text-transform:uppercase; color:var(--faint); }
  table.t code, p code, li code { font-family:var(--mono); font-size:.84em; background:var(--surface-2); padding:1px 4px; border-radius:3px; }
  table.t tr.cat td { background:var(--rose-wash); font-family:var(--hand); font-size:21px; padding-top:10px; border-bottom:1.5px solid var(--ink); }
  table.t tr.cat td span { font-family:var(--body, inherit); font-size:13.5px; color:var(--muted); margin-left:8px; }
  table.t td.id { font-family:var(--mono); font-size:12.5px; color:var(--faint); white-space:nowrap; }
  table.q td:nth-child(2) { font-weight:600; min-width:220px; } table.q td:nth-child(4) { background:#FFF6F6; }
  table.rows td { font-family:var(--mono); font-size:12.5px; white-space:nowrap; } table.rows td.bad { background:var(--rose-wash); } table.rows td.new { background:var(--mint-wash); }
  .verdict { font-weight:700; white-space:nowrap; } .verdict.pursue { color:#1d6b3a; } .verdict.drop { color:#a3322b; } .verdict.when { color:#8a5a00; }
  .why { border:var(--line); border-radius:var(--wob); padding:14px 20px; background:var(--sky-wash, #EFF8FB); margin:16px 0; }
  .note { font-size:14px; color:var(--faint); }
  .ideas { display:flex; flex-wrap:wrap; gap:8px; margin:6px 0 14px; }
  .ideas a { font-size:14px; border:1.5px solid var(--ink); border-radius:999px; padding:2px 12px; background:#fff; color:var(--ink); text-decoration:none; }
  details.faq { border-bottom:1.5px dashed var(--rule-firm); padding:10px 0; } details.faq summary { cursor:pointer; font-weight:600; }
  details.faq p { margin:8px 0 0; }
  .btn { display:inline-block; border:1.5px solid var(--ink); border-radius:var(--wob); padding:6px 16px; background:var(--butter-wash); color:var(--ink); text-decoration:none; font-weight:600; cursor:pointer; font-size:15px; }
  @media (max-width:860px) { .cards { grid-template-columns:1fr; } }
  @media (max-width:640px) { .toc ol { columns:1; } }
</style>"""


def ld(title, desc, url, crumbs, faq=None):
    items = [
        {"@context": "https://schema.org", "@type": "TechArticle", "headline": title, "description": desc,
         "url": url, "inLanguage": "en", "isAccessibleForFree": True, "dateModified": MODIFIED,
         "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
         "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE},
         "about": [{"@type": "Thing", "name": "Data engineering"}, {"@type": "Thing", "name": "Data platform"}]},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": f"{SITE}{h}"} for i, (n, h) in enumerate(crumbs)]},
    ]
    if faq:
        items.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})
    return "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in items)


def q_table(questions):
    """The one question table: [(cat_id, category, subtitle, [(question, why, breaks, do), ...]), ...]."""
    q, n = "", 0
    for cid, cat, sub, rows in questions:
        q += f'<tr class="cat"><td colspan="5">{cid} · {E(cat)}<span>{E(sub)}</span></td></tr>'
        for i, (qq, why, breaks, do) in enumerate(rows):
            n += 1
            q += f"<tr><td class='id'>{cid}{i + 1}</td><td>{E(qq)}</td><td>{E(why)}</td><td>{E(breaks)}</td><td>{E(do)}</td></tr>"
    head = "<tr><th>#</th><th>Question to chase</th><th>Why we ask</th><th>What breaks in production if nobody asks</th><th>Do this (not this)</th></tr>"
    return f'<div class="tw"><table class="t q">{head}{q}</table></div>', n


def dec_html(decisions):
    """Design decisions: [(question, [(option, 'pursue'|'when'|'drop', why), ...]), ...]."""
    out = ""
    for qd, opts in decisions:
        out += f"<h3>{E(qd)}</h3><div class='tw'><table class='t'><tr><th>Option</th><th>Verdict</th></tr>"
        for o, v, why in opts:
            word = {"pursue": "Pursue", "drop": "Drop", "when": "Pursue when"}[v]
            out += f"<tr><td><b>{E(o)}</b></td><td><span class='verdict {v}'>{word}</span> · {E(why)}</td></tr>"
        out += "</table></div>"
    return out


# ---------------------------------------------------------------------------------------------
# Level 0: the whole system
# ---------------------------------------------------------------------------------------------

def water():
    b = ""
    items = [("Rivers and wells", "each one behaves\ndifferently", "grey"), ("Treatment plant", "cleaned in stages,\ntested at each", "rose"),
             ("Taps", "homes, hospitals,\nfactories", "sky")]
    x = 30
    for i, (t, s, f) in enumerate(items):
        b += box(x, 20, 230, 92, t, s, f)
        if i < 2:
            b += arrow(x + 234, 66, x + 296, 66)
        x += 300
    b += text(445, 145, "before laying a pipe you ask how much the well gives, when it runs dry, and whether it is clean", 15)
    return svg(890, 160, b, "A city's water: rivers and wells feed a treatment plant, which feeds taps in homes, hospitals and factories."), \
        "A city's water supply. Sources you do not control, a plant you run, and users who each need something different."


def big_picture():
    b = ""
    # three outer blocks
    blocks = [(10, "Upstreams", "the systems that create the data", "grey",
               [("Apps and databases", "orders, billing, HR"), ("SaaS apps", "CRM, ERP, payroll"), ("Files", "SFTP, partner drops"),
                ("APIs", "partners, public data"), ("Events and logs", "clicks, IoT, queues")]),
              (370, "Data platform", "what we run and are answerable for", "rose",
               [("Ingestion", "push or pull, landing"), ("Bronze", "raw, as it arrived"), ("Silver", "clean, one row per thing"),
                ("Gold", "shaped for a use"), ("Semantic", "one meaning per number")]),
              (730, "Downstreams", "where people and programs use it", "sky",
               [("BI dashboards", "reports, KPIs"), ("AI and agents", "chat with data, RAG"), ("ML", "features, models"),
                ("APIs and sharing", "apps, partners"), ("Back to apps", "reverse ETL")])]
    for x, title, sub, fill, inner in blocks:
        b += f'<rect x="{x}" y="10" width="330" height="372" rx="18" fill="{FILL[fill]}" stroke="#1F1F1F" stroke-width="1.6"/>'
        b += text(x + 165, 42, title, 24, fill="#1F1F1F") + text(x + 165, 64, sub, 14)
        for i, (t, s) in enumerate(inner):
            y = 80 + i * 59
            b += f'<rect x="{x + 20}" y="{y}" width="290" height="50" rx="12" fill="#fff" stroke="#1F1F1F" stroke-width="1.3"/>'
            b += text(x + 165, y + 22, t, 17, fill="#1F1F1F") + text(x + 165, y + 40, s, 13)
    b += arrow(342, 196, 368, 196) + arrow(702, 196, 728, 196)
    b += text(535, 410, "hops we own: 1 sources to bronze · 2 bronze to silver · 3 silver to gold · 4 gold to semantic · 5 semantic to experiences", 14, fill="#1F1F1F")
    return svg(1070, 425, b, "Three blocks: upstreams (apps, SaaS, files, APIs, events), the data platform (ingestion, bronze, silver, gold, semantic) and downstreams (BI, AI and agents, ML, APIs, reverse ETL)."), \
        "The whole data system on one page. We do not own the left block, but almost every production problem starts there."


BLOCKS = [
    ("Upstreams", "grey", "The systems that create the data. We don't own them, but we depend on how they behave.",
     ["Each source hands data over differently: it can push changes to us, we can pull them, or it can share them in place.",
      "How rows get inserted, updated and deleted decides whether a full or an incremental load is safe.",
      "Keys and dates must be named per dataset, or numbers drift without anyone noticing.",
      "Profiling real data, masked if needed, is how we find the edge cases before production does."],
     "ready", f"{BASE}upstreams/", "Read the upstreams page"),
    ("Data platform", "rose", "What we build and run: ingestion, then bronze, silver, gold and the semantic layer.",
     ["Ingestion is driven by metadata: one framework, and a new table is configuration, not code.",
      "Each layer makes one promise. Raw is kept, clean is checked, gold is reconciled and every metric has one definition.",
      "Each layer has its own decisions, ways to fail in production, patterns and anti-patterns.",
      "Quality, lineage, cost and access run on every hop, not as a box at the end."],
     "ready", f"{BASE}platform/", "Read the platform page"),
    ("Downstreams", "sky", "Where the data earns its keep: dashboards, AI, agents, ML and apps.",
     ["Each consumer needs a different freshness, grain and level of trust.",
      "Dashboards and AI must read the same metric definitions, or they will disagree in the same meeting.",
      "Agents call typed tools over certified data. They never write raw SQL.",
      "Every consumer is named with an owner, so a change upstream can be traced to who it hurts."],
     "next", None, "Coming soon"),
]

HOPS = [
    ("0", "Upstreams", "Know how each source behaves before writing a pipeline.", f"{BASE}upstreams/", None),
    ("·", "The data platform, whole", "Five hops, 24 concerns, one picture; layout and environments ready.", f"{BASE}platform/", "/learn/data-platform-architecture/"),
    ("1", "Sources to bronze", "Get everything in, exactly as it was, once.", None, "/learn/data-platform-architecture/ingestion/"),
    ("2", "Bronze to silver", "One clean, typed row per real thing, with history.", None, "/learn/data-platform-architecture/bronze-to-silver/"),
    ("3", "Silver to gold", "Tables shaped for a use, reconciled every run.", None, "/learn/data-platform-architecture/gold/"),
    ("4", "Gold to semantic", "Every metric defined once, with an owner.", None, "/concepts/semantic-layer/"),
    ("5", "Semantic to experiences", "Dashboards, AI and agents give the same answer.", None, None),
    ("6", "Downstreams", "Every consumer named, with what it needs and what it can tolerate.", None, None),
]

TEMPLATE = [
    ("The promise", "One line on what this layer guarantees to the next one."),
    ("For leaders", "Four or five sentences. A data leader can stop reading here and still know what to ask for."),
    ("The question list", "One table, grouped by category. Each row is a question to chase, why we ask it, what breaks in production if nobody asks, and the pattern to follow (with the anti-pattern to avoid)."),
    ("Design decisions", "The few real choices for this layer, with the options and a verdict: Pursue, Drop, or Pursue only when a condition holds."),
    ("How we build it", "A link to the build guide for the same layer, so the two pages don't repeat each other."),
]


def overview():
    w_svg, w_cap = water()
    p_svg, p_cap = big_picture()
    cards = ""
    for name, fill, one, bullets, status, href, cta in BLOCKS:
        tag = '<span class="tag ready">Ready</span>' if status == "ready" else '<span class="tag next">Coming</span>'
        link = f'<a class="btn" href="{href}">{E(cta)}</a>' if href else f'<span class="note">{E(cta)}</span>'
        cards += (f'<div class="card" style="--w:{FILL[fill]}"><h3>{E(name)}</h3><p class="one">{E(one)}</p><ul>'
                  + "".join(f"<li>{E(x)}</li>" for x in bullets) + f"</ul>{tag} {link}</div>")
    hops = ""
    for n, name, promise, href, build in HOPS:
        title = f'<a href="{href}">{E(name)}</a>' if href else E(name)
        status = '<span class="tag ready">Ready</span>' if href else '<span class="tag next">Coming</span>'
        b = f'<a href="{build}">build guide</a>' if build else '<span class="note">to come</span>'
        hops += f"<tr><td class='id'>{n}</td><td><b>{title}</b></td><td>{E(promise)}</td><td>{status}</td><td>{b}</td></tr>"
    tmpl = "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td></tr>" for a, b in TEMPLATE)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › Data systems, end to end</p>
<p class="eyebrow" style="margin-top:22px">Data engineering · for data leaders first, then builders</p>
<h1>Data systems, end to end</h1>
<p class="lede">A data system is bigger than a data platform. It starts in systems we don't own, runs through a platform we do, and ends wherever people and programs use the numbers. This page shows the whole thing at once. Every block opens a page with the questions to chase, the decisions to take and what goes wrong in production.</p>
<nav class="toc"><b>On this page</b><ol>
<li><a href="#plain">In plain words</a></li><li><a href="#picture">The whole picture</a></li><li><a href="#blocks">The three blocks, for leaders</a></li>
<li><a href="#hops">Drill down, hop by hop</a></li><li><a href="#template">How every page is laid out</a></li><li><a href="#next">Where to go next</a></li></ol></nav>

<section id="plain"><p class="eyebrow">In plain words</p><h2>Think of a city's water</h2>
<p>A city does not own the rivers and wells its water comes from. Each one behaves differently. One floods in the monsoon, one runs low in May, one carries silt. The treatment plant can only do its job if the engineers know these habits before they lay a pipe. At the other end, a hospital, a home and a factory all want water, but not the same water at the same pressure.</p>
<figure class="diagram">{w_svg}<figcaption>{E(w_cap)}</figcaption></figure>
<p>Data works the same way. The <b>upstreams</b> are the source systems: apps, SaaS tools, files, APIs and events. The <b>data platform</b> is the plant, cleaning in stages. The <b>downstreams</b> are the taps: dashboards, AI, agents, ML and other apps. Most production problems that look like platform bugs began upstream, in a question nobody asked.</p></section>

<section id="picture"><p class="eyebrow">The whole picture</p><h2>Upstreams, the data platform, downstreams</h2>
<figure class="diagram">{p_svg}<figcaption>{E(p_cap)}</figcaption></figure></section>

<section id="blocks"><p class="eyebrow">For leaders</p><h2>The three blocks, in four lines each</h2>
<div class="cards">{cards}</div></section>

<section id="hops"><p class="eyebrow">Drill down</p><h2>Hop by hop</h2>
<p>Each hop gets its own page with the same layout. These pages cover what to ask and what to decide. The build guide on the right covers how we build it.</p>
<div class="tw"><table class="t"><tr><th>#</th><th>Page</th><th>The promise</th><th>Status</th><th>How we build it</th></tr>{hops}</table></div></section>

<section id="template"><p class="eyebrow">One layout</p><h2>How every page is laid out</h2>
<p>Every page has the same five parts, so a leader reads the top and a builder reads the rest. There is one question list per page, not separate lists of risks, patterns and anti-patterns. Each question carries its own reason, its production failure and its pattern.</p>
<div class="tw"><table class="t"><tr><th>Part</th><th>What it holds</th></tr>{tmpl}</table></div></section>

<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2>
<p><b>Start upstream:</b> <a href="{BASE}upstreams/">Upstreams: know your sources</a>. It is the page to walk a client through before any build.</p>
<p><b>Hand it to a client:</b> the <a href="{BASE}upstreams/questionnaire/">printable source questionnaire</a>.</p>
<p><b>How we build it:</b> <a href="/learn/data-platform-architecture/">Data platform architecture, drawn right</a> and <a href="/learn/medallion-architecture/">Medallion architecture, drawn right</a>.</p>
<p><b>Running the project:</b> <a href="/learn/technical-anchor/discovery/">Technical anchor: discovery</a> covers the whole discovery phase. These pages are its source-by-source detail.</p></section>"""
    title = "Data systems, end to end"
    desc = "The data system on one page: upstreams, the data platform and downstreams, with a drill-down page per hop listing the questions to chase, decisions, production failures and patterns."
    url = f"{SITE}{BASE}"
    return wb.page(title, desc, url, body, CSS + ld(title, desc, url, [("Learn", "/learn/"), (title, BASE)]))


# ---------------------------------------------------------------------------------------------
# Level 1: upstreams
# ---------------------------------------------------------------------------------------------

LEADERS_UP = [
    "Every source system has habits: how it hands data over, how its rows change, when it is busy. A pipeline built without knowing those habits works in testing and fails in production.",
    "We ask a lot of questions about your sources. Each one exists because, on some past project, not asking it cost weeks or a wrong number in front of the board.",
    "The most important answers are how rows change (updates and deletes), which column says when a row changed, and what the business key is.",
    "We ask to profile a copy of production data, masked if it holds personal data. Real data shows the keys, gaps and odd values that our later layers depend on.",
    "Where a source can tell us when data is ready, or push its changes to us, we avoid the scheduling problems that cause most late or partial loads.",
]

SOURCE_TYPES = [
    ("Operational databases", "Oracle, SQL Server, PostgreSQL, MySQL behind your own apps", "Log-based CDC, read replica query, full extract", "Load on the live primary; hard deletes; bulk fixes run directly in the database"),
    ("Packaged and SaaS apps", "SAP, Salesforce, Dynamics, Workday, ServiceNow", "Vendor extractor or native connector, bulk API, change events", "Licence and API limits, custom fields, vendor upgrades changing the schema"),
    ("Files", "CSV or Excel from partners, SFTP drops, exports to object storage", "Source drops files (push), we poll a folder (pull)", "Partial files, re-sent files, column order changes, no done marker"),
    ("APIs", "Partner and payment APIs, public data, internal services", "Poll with a changed-since filter, webhooks", "Rate limits, paging over changing data, no way to see deletes"),
    ("Events and streams", "Kafka, Event Hubs, Kinesis, Pub/Sub, IoT, clickstream", "Subscribe (push), replay from an offset", "Duplicates, out-of-order events, schema changes inside messages, retention"),
    ("Shares and mirrors", "Delta Sharing, Snowflake shares, Fabric mirroring, BigQuery sharing", "Read in place, no copy job", "Whose cost it is, freshness, and what happens when the share is changed"),
    ("Spreadsheets and manual data", "Targets, mappings, budgets kept by hand", "Upload to a controlled place, form, or file drop", "No owner, no versioning, silent edits to past values"),
]

HANDOVER = [
    ("Log-based CDC", "Push", "Reads the database's transaction log and emits every insert, update and delete in order.", "Yes", "Busy tables, deletes matter, low latency, minimal load on source", "Needs logging switched on and enough log retention; DBA approval"),
    ("Trigger-based CDC", "Push", "Database triggers copy each change into a change table.", "Yes", "Rarely; only when the log can't be read", "Slows every write on the source. Usually an anti-pattern"),
    ("Outbox or business events", "Push", "The app publishes an event (order placed, order cancelled) alongside its own write.", "If designed in", "Event-driven apps, real-time needs, meaning-rich changes", "Only as complete as the developers made it; replay rules"),
    ("Webhooks", "Push", "The source calls our endpoint when something changes.", "Sometimes", "SaaS apps and payments", "Missed calls when our side is down; need a catch-up pull"),
    ("Vendor extractor or connector", "Push or pull", "The vendor's own tool hands changes over (for example SAP ODP, Salesforce change events or bulk API).", "Usually", "Packaged apps where direct database reads are not allowed", "Licensing, connector limits, version upgrades"),
    ("Source drops files", "Push", "The source writes files to a place we watch, ideally with a done marker.", "Only if sent", "Partners, legacy systems, mainframes", "Partial and re-sent files; no deletes unless agreed"),
    ("Incremental query (watermark)", "Pull", "We read rows whose modified time is after the last load.", "No", "Tables with a trustworthy modified column and soft deletes", "Misses hard deletes and any change that doesn't touch the column"),
    ("Full extract", "Pull", "We read the whole table every time and compare.", "Yes, by comparison", "Small tables, reference data, safety net for reconciling", "Cost and time grow with the table"),
    ("API polling", "Pull", "We call the API with a changed-since filter and page through results.", "Rarely", "SaaS without events", "Rate limits; unstable paging skips or repeats rows"),
    ("Share or mirror", "Neither (in place)", "The source exposes tables we read without copying.", "Yes, in the share", "Same platform or same vendor family", "We don't control freshness or schema changes"),
]

ROWS_DAY1 = [("101", "Asha", "Pune", "10:02"), ("102", "Ravi", "Delhi", "10:05"), ("103", "Meena", "Agra", "10:09")]

# One question table for the upstreams page. (id, question, why we ask, what breaks in production, do this / not this)
QUESTIONS = [
    ("A", "Ownership and change", "who answers questions and who tells us about changes", [
        ("Who owns this system, and who knows its data best?",
         "Someone has to answer 'is this value right?' and approve fixes on the source side.",
         "Questions wait for weeks; a data bug can't be fixed because nobody owns the source.",
         "Name a business owner and a technical owner per source in the data contract. Not: 'ask the app team'."),
        ("When does the source change (releases, upgrades, patches), and who tells us beforehand?",
         "A column renamed on their side is a broken pipeline on ours.",
         "Loads fail the Monday after a weekend release, or worse, load wrong values without failing.",
         "Get on their release calendar; the contract sets a notice period. Not: finding out from a failed job."),
        ("Is this system being replaced, migrated or merged in the next year?",
         "A deep integration with a system that retires in six months is wasted work.",
         "The integration is rebuilt from scratch, and history from the old system is lost.",
         "Build the old source behind the same contract the new one will meet. Not: custom logic tied to the old system's quirks."),
        ("What is the source's own support window and service level?",
         "Our freshness promise can never beat theirs.",
         "We promise data by 7 a.m.; their batch finishes at 8 a.m. on busy days.",
         "Derive our service level from theirs, with a margin. Not: promising a time before asking."),
    ]),
    ("B", "Access route", "how we are allowed to reach the data", [
        ("How can we reach the data: direct database read, a read replica, an API, files, an event stream, or a share?",
         "The route decides the tools, the security work and the cost.",
         "A route chosen late means security approvals start again and go-live slips.",
         "List every route the source supports and choose in discovery. Not: defaulting to whatever worked last project."),
        ("Can we read from a replica, standby or backup instead of the live system?",
         "Our extract must never slow down their customers.",
         "A month-end extract locks tables and the app slows down; we get switched off.",
         "Read a replica, or use log-based CDC. Not: heavy queries on the primary in business hours."),
        ("What are the limits: API rate limits, rows per call, extract windows, connection counts?",
         "Limits decide how long a backfill takes and how we page and retry.",
         "Throttled 80% of the way through a backfill; a partial load looks complete.",
         "Design paging, retries and checkpoints around the published limits. Not: discovering the limit in production."),
        ("What network path and credentials do we need: private link or VPN, firewall rules, a service account, password rotation?",
         "These requests are slow; they decide the start date, not the code.",
         "Go-live waits on a firewall ticket; a password expires and loads stop with nobody alerted.",
         "Raise access requests on day one; keep secrets in a vault with expiry alerts. Not: a personal account in a config file."),
    ]),
    ("C", "Protecting the source", "our extraction must never hurt the system that runs the business", [
        ("How much load can the source take, and when: peak hours, nightly batch, month-end close?",
         "Our extract competes with their business for the same database.",
         "An extract during month-end close slows the finance system, and our access is switched off.",
         "Agree an extract window and a load budget (queries, connections, rows per second) and throttle to it. Not: running whenever suits us."),
        ("Will we read through a read-only account with access to only the tables we need?",
         "An extraction account that can write, or see everything, is a risk to them and to us.",
         "A mistaken statement in a tool locks or changes source tables.",
         "A read-only service account with SELECT on named tables or views, no schema changes. Not: borrowing the app's or an admin account."),
        ("Do our extract queries use indexes, and has the source's DBA reviewed them?",
         "A filter on a column with no index reads the whole table on every run.",
         "An hourly 'changed since' query on an unindexed column scans 500 million rows each time.",
         "An index on the change column (or CDC instead), and a DBA review of every extract query. Not: SELECT * with an unindexed filter."),
        ("How do our long reads avoid blocking their writers?",
         "Long reads can hold locks or grow the source's undo and temp space.",
         "A three-hour extract blocks order updates, or fails with 'snapshot too old'.",
         "Read from a replica or a snapshot, and read in chunks by key range with short transactions. Not: one long transaction over a busy table."),
        ("For CDC: what does change capture cost the source, and who watches it?",
         "Change capture keeps log on the source until we read it.",
         "Our pipeline is down for a weekend; the replication slot keeps every log file, the source's disk fills and the app stops.",
         "Alerts on capture lag, a cap on retained log, and a runbook to drop the capture safely. Not: set up and forget."),
        ("Do we share an API quota with other users of the source, and how do we stay inside our part?",
         "API limits are often per company, not per integration.",
         "Our backfill uses the whole day's quota and the sales team's other integrations stop.",
         "Our own share of the quota, backoff on limit errors, backfills out of hours. Not: retrying as fast as possible."),
        ("Can the source team stop our extraction quickly if they need to?",
         "They must be able to protect their system without finding us first.",
         "During an incident on the source, nobody knows how to stop our jobs.",
         "A named contact, a pause flag in our metadata and a documented stop procedure. Not: 'call the data team'."),
    ]),
    ("D", "Push support", "what the source can send us without being asked", [
        ("Can the source push changes: log-based CDC, a vendor extractor, business events, webhooks, or files it drops?",
         "Push captures every change, including deletes, as it happens, without scanning tables.",
         "Polling misses deletes and the in-between states of a row (created, then cancelled within the hour).",
         "Prefer log-based CDC for busy databases. Not: trigger-based CDC, which slows every write."),
        ("For CDC: is the transaction log switched on at the level we need, and how long is it kept?",
         "If the log is cleared before we read it, those changes are gone for good.",
         "A two-day outage on our side outlasts a one-day log retention, and a full reload is forced.",
         "Keep log retention longer than our longest likely outage; alert on CDC lag. Not: default retention."),
        ("For events and webhooks: is delivery at least once, is order kept, can we replay, is there an event id and a sequence number?",
         "These answers decide how we remove duplicates and put changes in order.",
         "Duplicates double the counts; an old update arriving late overwrites a newer value.",
         "Remove duplicates on the event id; order by the source's sequence, not arrival time. Not: trusting arrival order."),
        ("Does the source say when a batch is complete: a done file, a row count, an event?",
         "Without it we cannot tell a half-written file from a whole one.",
         "A partial file loads, and the day's total drops by 40% with no error.",
         "Ask for a done marker with a row count (and ideally a checksum). Not: 'load whatever is in the folder at 2 a.m.'."),
    ]),
    ("E", "Pull support", "what we can fetch, and whether we can trust it", [
        ("Is there a column that reliably says when each row last changed?",
         "Incremental loads depend on it completely.",
         "Updates that don't touch the column are missed for months, and nobody notices.",
         "Test it during profiling: change a row, check the column moves. Not: trusting the column name."),
        ("Is that column set by the database on every change, including bulk fixes and scripts, or by the app?",
         "App-set times skip changes made outside the app.",
         "A DBA's correction script changes 10,000 rows and incremental loads never see it.",
         "Prefer a database-maintained time or CDC; ask the DBA how fixes are applied. Not: assuming every change goes through the app."),
        ("Can the API filter by changed-since time, and does it page in a stable order?",
         "Paging by position over changing data skips or repeats rows.",
         "Rows move between pages during the read; a few go missing on every run.",
         "Use cursor or key-based paging and a small overlap window. Not: page numbers over live data."),
    ]),
    ("F", "Full or incremental load", "per dataset: reload everything, or only what changed", [
        ("How big is each dataset, and how long does a full extract take and load the source?",
         "A full load's cost grows with the table, every run.",
         "A daily full load of a 2 TB table runs nine hours, spills into business hours and slows the source.",
         "Full loads for small and reference tables; incremental or CDC for large ones. Not: full for everything because it's simpler."),
        ("Is there any reliable way to get only the changes: a trusted modified column, CDC, or a change API?",
         "Without one, a full extract compared with what we hold is the only safe option.",
         "An incremental load built on an untrustworthy column silently misses changes for months.",
         "No reliable change signal means full snapshot and compare. Not: incremental on a guess."),
        ("For a full load, do we replace the table, or compare the new snapshot with what we hold?",
         "Replacing can't tell what changed and leaves the table empty if the load fails midway; comparing finds inserts, updates and deletes.",
         "Truncate-then-insert fails halfway and dashboards show an empty table for an hour.",
         "Land the snapshot in staging, check its row count, then merge by key or swap in one step. Not: truncate, then insert."),
        ("Can the source re-send a whole period (the last 7 days, the current month) instead of everything?",
         "A period reload is the middle ground for sources that restate recent data.",
         "Overlapping windows are appended and recent days are counted twice.",
         "Replace whole periods or partitions so a re-send is safe to repeat. Not: appending overlapping windows."),
        ("On incremental loads, how will we see rows that were deleted at the source?",
         "A 'changed since' query can't return a row that no longer exists.",
         "Cancelled and deleted orders stay in the platform forever.",
         "CDC, a soft-delete flag, or a regular key-only full extract compared with our keys. Not: ignoring deletes."),
        ("How often should a full comparison run alongside incremental loads: weekly, monthly?",
         "Incremental loads drift: missed changes, bulk fixes, clock problems.",
         "Small differences pile up for a year and nobody can say when they started.",
         "A scheduled full (or key and count) comparison that reports and repairs differences. Not: incremental forever with no check."),
        ("How will the first, historical load run: one big extract, or in chunks by date or key, and in which source window?",
         "The first load is the biggest and the most likely to hurt the source.",
         "A 30-hour initial extract fails at hour 28 and starts again from zero.",
         "Chunked, resumable loads with checkpoints, in an agreed window. Not: one giant query."),
        ("At what exact point do we switch from the first full load to incremental?",
         "A gap between the two loses rows; an overlap doubles them.",
         "Changes made while the initial load ran are never picked up.",
         "Record the CDC position or watermark before the full extract starts, begin incremental from it, and let the merge remove the overlap. Not: starting incremental 'from now'."),
    ]),
    ("G", "How the data changes", "the answers that decide the load method and how silver merges", [
        ("Which of these happen: inserts only, updates, hard deletes, soft deletes?",
         "This decides the load method and how the next layer merges rows.",
         "Hard deletes never reach the platform; cancelled orders keep counting as revenue.",
         "With hard deletes and no CDC, read all keys regularly to detect what disappeared. Not: assuming insert-only."),
        ("Can old records change: late arrivals, backdated entries, corrections to a closed period? How far back?",
         "This sets how far back each load looks, and when a period counts as final.",
         "Last month's numbers change after the board has seen them, and nobody can explain why.",
         "Set a look-back window from the answer, and agree a period-close rule. Not: loading only 'yesterday'."),
        ("Does the source ever resend or restate a whole period, or the whole table?",
         "A resend must replace, not add to, what we already hold.",
         "A re-sent month doubles that month's revenue.",
         "Make loads safe to repeat: merge on the key, or replace the whole period. Not: plain appends."),
        ("Can a business key change, be reused, or be merged (two customer records joined into one)?",
         "History must follow the real thing, not the number.",
         "Order history attaches to the wrong customer after a key is reused.",
         "Keep a stable key of our own and capture merge events. Not: treating the source key as eternal."),
        ("Are any changes made outside the app, such as data fixes, migrations or mass updates?",
         "These are the changes most likely to bypass change tracking.",
         "Silent gaps after every quarterly cleanup.",
         "Ask for the fix log; prefer CDC on sources with frequent fixes. Not: hoping fixes are rare."),
    ]),
    ("H", "Keys and dates", "what makes a row unique and which date means what", [
        ("What is the business key of each dataset: one column or several? Is it really unique?",
         "Keys drive de-duplication, merging and every join after this.",
         "A key that isn't unique multiplies rows in joins and inflates totals.",
         "Check uniqueness on real data during profiling. Not: trusting the documentation."),
        ("Which date means what: transaction, effective, posting, created, modified?",
         "Reports must use the right date for the right question.",
         "'Sales by day' on our dashboard disagrees with finance because they use posting date.",
         "Name every date and its use in the data contract. Not: one column called 'date'."),
        ("What time zone and precision are times stored in, and how is daylight saving handled?",
         "Rows near midnight and on clock changes go to the wrong day, or twice.",
         "Daily totals are off on the day the clocks change, every year.",
         "Store UTC alongside the source's local time and zone. Not: guessing the zone from the server."),
    ]),
    ("I", "Relationships and joins", "how datasets connect, so silver and gold join them correctly", [
        ("Which datasets relate to which (order, order lines, product, customer), and through which columns?",
         "Silver and gold are built by joining; the joins and the load order come from these relationships.",
         "Gold joins on the wrong column and totals are quietly wrong.",
         "A relationship map per source, confirmed by the owner and checked in profiling. Not: guessing from column names."),
        ("For each relationship, how many rows can match on each side: one-to-one, one-to-many, many-to-many?",
         "A join that is assumed one-to-one but isn't multiplies rows.",
         "Orders joined to a 'one per order' table that sometimes has two rows: revenue doubles for those orders.",
         "Measure it in profiling and test it on every load. Not: trusting the documentation."),
        ("Are foreign keys enforced in the source database, or only by the application?",
         "Unenforced relationships produce orphans: children without parents.",
         "Order lines point to orders that don't exist; an inner join silently drops their revenue.",
         "Profile orphan rates; decide per relationship whether to keep orphans under an 'unknown' parent or quarantine them. Not: inner joins that hide them."),
        ("Do related tables arrive together, from the same point in time?",
         "Parent and child read at different moments are out of step.",
         "Order lines arrive before their order header and drop out of the join until the next day.",
         "Read related tables from the same snapshot or log position, or handle late parents explicitly. Not: hoping the timing works out."),
        ("How do the same things link across systems (customer id in the CRM versus in billing)?",
         "Gold joins across sources; those joins need a known mapping.",
         "Orphan rows, and customers counted twice.",
         "Profile match rates across systems; give the mapping table an owner. Not: fuzzy joins in a dashboard."),
        ("Must some joins use the value as it was at the time (the customer's region on the order date)?",
         "Joining to today's value rewrites history.",
         "Last year's sales by region move every time a customer moves.",
         "Join as of the transaction date to the history kept in silver (SCD Type 2). Not: always joining to the current row."),
        ("Which join paths do the reports users trust today use?",
         "Trusted reports hold business rules inside their joins.",
         "Our joins are 'correct' but don't match the numbers the business knows.",
         "Get the logic of the trusted reports and test our joins against it. Not: designing joins from scratch."),
    ]),
    ("J", "Schema and meaning", "what the columns and codes mean", [
        ("Is there a data dictionary? What do the status codes and flags mean?",
         "A code means nothing to us without its definition.",
         "'Status 7' means cancelled in one region and refunded in another; revenue is wrong in both.",
         "Load code lists as reference data with an owner. Not: hard-coding codes in transforms."),
        ("How often does the schema change, with how much notice, and are changes only additions?",
         "Added columns are easy; renamed, retyped or removed columns break things.",
         "A column changes from number to text; the load succeeds and every value becomes null.",
         "Detect schema drift on every load; allow additions, stop on breaking changes. Not: silent type coercion."),
        ("Are there splits by company, country, tenant, currency or unit?",
         "Numbers in different currencies or units cannot be added.",
         "Rupees and dollars summed into one revenue figure.",
         "Carry company, currency and unit as columns on every row. Not: assuming one of each."),
        ("Are there free-text fields, JSON blobs or customer-specific custom fields?",
         "They need their own parsing, and often hold personal data.",
         "Names and phone numbers hidden in a 'notes' field reach a dashboard.",
         "Keep them raw in bronze; parse and scan them on purpose. Not: flattening blindly."),
    ]),
    ("K", "Volume and timing", "how much, how fast and when", [
        ("How many rows exist today, how many arrive per day, how fast is it growing, and when are the peaks?",
         "Sizing, cost and partitioning come from these numbers.",
         "The month-end load runs ten times longer and misses its deadline.",
         "Size for the peak, not the average; test with peak volume. Not: sizing from one quiet day."),
        ("How much history do we need, and does the source still hold it?",
         "This decides the backfill plan.",
         "The source keeps only 13 months; the three-year trend users asked for can't be built.",
         "Agree history needs early; secure archives before they are purged. Not: discovering purge rules at backfill."),
        ("When is the data ready at the source each day, and how fresh do users need it?",
         "Freshness is a chain; every link must fit.",
         "The dashboard refreshes before the data has landed and shows yesterday as today.",
         "Start from the user's need and work back through each step. Not: picking a schedule time first."),
        ("Can the source tell us when data is ready, so we start on that signal instead of a clock?",
         "Starting on a signal removes most late or partial loads.",
         "The 2 a.m. job runs on an empty folder because the source was late tonight.",
         "Prefer an event, file-arrival trigger or done marker. If only a schedule is possible, add a completeness check before loading. Not: a fixed time with no check."),
    ]),
    ("L", "Access to profile real data", "why we ask to scan your data", [
        ("Can we have a copy of production data in a sandbox: masked if it holds personal data, as is if it doesn't?",
         "Only real data shows real keys, gaps, odd values and edge cases.",
         "Logic built on test data breaks on the first real load.",
         "A masked production copy with consistent masking, so the same customer gets the same token everywhere and joins still work. Not: hand-made test data only."),
        ("If data cannot leave your environment, can we run profiling inside it and take only the results out?",
         "Profiles (counts, ranges, match rates) usually hold no personal data.",
         "Design proceeds on guesses, and errors surface in user testing.",
         "Run the profiler where the data lives and export the summary. Not: skipping profiling."),
        ("Who on your side will review the profile and confirm what is expected?",
         "Odd values are either bugs or business rules; only the owner knows which.",
         "We 'clean' values that were correct, or keep ones that were wrong.",
         "A short profile review with the data owner per source. Not: deciding alone."),
    ]),
    ("M", "Sensitivity and rules", "what the law and your policies require", [
        ("Which columns hold personal, health, payment or other sensitive data?",
         "This decides masking, who may see what and where data may be stored.",
         "Personal data shows up in a widely shared dashboard; an audit finding follows.",
         "Tag sensitive columns as they land; mask by default and grant access on purpose. Not: deciding at the dashboard."),
        ("What are the retention, deletion-on-request, residency and consent rules?",
         "A deletion request must reach every copy we hold.",
         "A customer asks to be deleted and they live in 40 tables nobody can list.",
         "Design the deletion path from day one, using lineage. Not: 'we will handle it when asked'."),
        ("Are there licence or contract limits on using third-party data?",
         "Some data may be used only for some purposes.",
         "Licensed data is shared with a partner and the contract is breached.",
         "Record usage limits as metadata on the dataset. Not: a note in someone's inbox."),
    ]),
    ("N", "Trust and reconciliation", "how we will prove nothing was lost", [
        ("What quality problems do you already know about?",
         "Known problems are cheap to plan for and expensive to discover live.",
         "We find them in front of executives and lose trust in week one.",
         "Write them down as expected exceptions with owners. Not: hoping profiling finds them all."),
        ("Can the source give control totals per load, such as row counts and the sum of amounts per day?",
         "This is the only way to prove nothing was lost or doubled.",
         "Rows go missing silently and the numbers are wrong for weeks.",
         "Reconcile every load against source totals and alert on the gap. Not: 'the job succeeded'."),
        ("Which report in the source system do users trust today?",
         "Users will compare our numbers with it on day one.",
         "Our total differs from the trusted report and nobody can explain why.",
         "Reconcile gold with that report before go-live and explain every difference. Not: launching first."),
    ]),
]

LOAD_PATTERNS = [
    ("Full replace (truncate, then load)", "Empty the table and load the whole extract", "No", "Almost never", "An empty or half-full table if the load fails; no record of what changed"),
    ("Full snapshot and compare", "Load the whole extract to staging, then merge by key", "Yes", "Small and medium tables, reference data, sources with no reliable change signal", "Cost grows with the table; needs a trustworthy key"),
    ("Period reload", "Replace a whole period or partition (last 7 days, this month) each run", "Within the period", "Sources that restate recent data", "Choose the window from how far back changes really happen"),
    ("Incremental by watermark", "Read rows changed since the last load, using a modified column", "No", "Large tables with a trustworthy modified column and soft deletes", "Misses hard deletes and changes that skip the column; needs an overlap window"),
    ("Incremental plus key compare", "Incremental for changes, plus a regular key-only full read to find deletes", "Yes, on the compare schedule", "Large tables with hard deletes and no CDC", "Deletes show up late, at the next compare"),
    ("Change data capture", "Read every insert, update and delete from the database log", "Yes", "Busy and large tables where deletes and order matter", "Log retention, capture lag, DBA approval"),
    ("Initial load, then incremental", "One chunked full load of history, then incremental from a recorded position", "Depends on the incremental method", "Every new source, once", "The hand-over point: record it before the full load starts"),
]

PROTECT = [
    "Agree an extract window and a load budget with the source owner: when, how many queries and connections, how many rows per second.",
    "Read through a read-only account limited to the tables you need, never the application's or an admin account.",
    "Prefer a replica, a standby or change data capture over queries on the live primary.",
    "Have the source's DBA review every extract query; make sure 'changed since' filters use an index.",
    "Read big tables in chunks by key range with short transactions, so their writers are never blocked.",
    "For CDC, alert on capture lag and cap the log kept for us, so a stalled pipeline can't fill the source's disk.",
    "Stay inside your share of any API quota, back off on limit errors and run backfills out of hours.",
    "Give the source team a named contact and a way to pause your extraction in minutes.",
]

FIELDS = [
    ("Business key", "The column or columns that identify one real thing.", "Merge, de-duplicate and join on it.", "order_no, or (company, invoice_no)"),
    ("Last modified time", "When this row last changed, set on every change.", "Find what changed since the last load.", "updated_at"),
    ("Created time", "When the row was first made.", "Late-arrival checks; first-seen history.", "created_at"),
    ("Transaction or event date", "When the business event happened.", "Report by the date the business means.", "order_date, posting_date"),
    ("Effective from and to", "The period a version was true, if the source keeps versions.", "Build history correctly.", "valid_from, valid_to"),
    ("Delete or status flag", "Marks a soft-deleted, cancelled or reversed row.", "Exclude or reverse it downstream.", "is_deleted, status = 'X'"),
    ("Change type", "Insert, update or delete, when a change feed is used.", "Apply each change the right way.", "op = I / U / D"),
    ("Source sequence", "The order of changes at the source (log position, version number).", "Apply changes in the right order.", "lsn, scn, row_version"),
    ("Company, tenant or country", "Which part of the business the row belongs to.", "Split, secure and report correctly.", "company_code"),
    ("Currency and unit", "What the amounts and quantities are measured in.", "Never add unlike numbers.", "currency, uom"),
    ("Source system", "Which system and instance the row came from.", "Lineage, and two systems sharing one key.", "src = 'SAP-EU'"),
]

PROFILE = [
    ("Row counts and growth", "Sizing, cost and the backfill plan"),
    ("Key uniqueness", "Whether the business key is safe to merge and join on"),
    ("Null and blank rates per column", "Which columns can be required in silver, and which need defaults"),
    ("Value ranges and outliers", "Quality rules with real thresholds, not guesses"),
    ("Distinct values and code lists", "Reference data, mappings and the meanings to confirm"),
    ("Date spread and late arrivals", "The look-back window and period-close rules"),
    ("Join match rates across tables and systems", "How silver joins into gold, and how many orphans to expect"),
    ("Hidden personal data in free text", "Masking rules before anything reaches a dashboard"),
]

DECISIONS = [
    ("Full or incremental for this table?", [
        ("Full snapshot and compare", "pursue", "Pursue for small and medium tables, reference data, and any table without a change signal you can trust."),
        ("Incremental (watermark or CDC), plus a regular full comparison", "pursue", "Pursue for large tables. The comparison catches drift and, without CDC, deletes."),
        ("Incremental with no comparison, ever", "drop", "Drop. Drift builds up silently."),
        ("Truncate and reload", "drop", "Drop. A failed load leaves an empty table, and nothing records what changed."),
    ]),
    ("How do we capture changes from a busy operational table?", [
        ("Log-based CDC", "pursue", "Pursue when updates or hard deletes matter or volumes are large. It catches everything with little load on the source."),
        ("Incremental query on a modified column", "when", "Pursue only when the column passes the profiling test and deletes are soft."),
        ("Full extract and compare", "when", "Pursue only for small tables, reference data, or as the weekly safety net beside incremental loads."),
        ("Triggers on the source tables", "drop", "Drop. They slow every write the business makes."),
    ]),
    ("Where do we read from?", [
        ("Read replica, standby or change log", "pursue", "Pursue. Our load never competes with their customers."),
        ("Live primary, outside business hours", "when", "Pursue only when no replica exists and the extract is light."),
        ("Live primary, any time", "drop", "Drop. The first slow month end ends the integration."),
    ]),
    ("When do loads start?", [
        ("On a signal from the source (event, file arrival, done marker)", "pursue", "Pursue wherever the source can signal. It removes most late and partial loads."),
        ("On a schedule, with a completeness check", "when", "Pursue when no signal is possible. Check the row count or marker before loading."),
        ("On a schedule with no check", "drop", "Drop. It loads whatever is there, half-written or not."),
    ]),
    ("How do we see real data before building?", [
        ("Masked production copy in a sandbox", "pursue", "Pursue. Use consistent masking so joins still work. A copy as is is fine when there is no personal data."),
        ("Profile in place, export only the results", "when", "Pursue when data may not leave the environment."),
        ("Hand-made test data only", "drop", "Drop for design. It never contains the edge cases that break production."),
    ]),
    ("How are the answers kept?", [
        ("A data contract per dataset, signed by the source owner", "pursue", "Pursue. The answers become checks that run on every load."),
        ("Notes in a discovery document", "drop", "Drop as the only record. Nobody re-reads it when the source changes."),
    ]),
]

FAQ_UP = [
    ("Why do data platform teams ask so many questions about source systems?",
     "Because the platform can only be as correct as its understanding of each source. How rows change, which column marks a change, what the key is, and when data is ready decide whether loads are complete, repeatable and on time. Each question exists because skipping it once caused a production problem."),
    ("Can we just do a full load every time and skip these questions?",
     "For small tables, often yes, and it is the simplest safe choice. For large or busy tables a full load gets slow and expensive, and you still need to know the keys, dates and deletes to merge and report correctly."),
    ("Why do you need production data? Can't you use test data?",
     "Test data is made by people who already know the rules, so it never contains the surprises: duplicate keys, nulls in required fields, codes nobody documented, dates in the wrong zone. A masked production copy shows them before go-live instead of after."),
    ("What is the difference between push and pull?",
     "With push, the source sends changes to us as they happen (change data capture, events, webhooks, files it drops). With pull, we ask the source on our schedule (queries, API calls, polling a folder). Push usually catches deletes and avoids timing problems. Pull is simpler to start but needs a trustworthy changed-since column."),
    ("What makes incremental loading safe?",
     "A column that changes every time the row changes, including fixes made outside the app; a known business key; a way to see deletes; and a look-back window long enough for late and backdated changes. Plus a periodic full comparison to prove nothing drifted."),
]


def push_pull():
    b = ""
    b += box(10, 70, 180, 110, "Source system", "database, app,\nfiles, API", "grey")
    b += box(560, 70, 180, 110, "Landing / bronze", "ours", "rose")
    b += f'<rect x="230" y="10" width="290" height="92" rx="14" fill="{FILL["mint"]}" stroke="#1F1F1F" stroke-width="1.4" stroke-dasharray="6 5"/>'
    b += text(375, 34, "Push: the source sends", 18, fill="#1F1F1F")
    b += text(375, 56, "change log (CDC), events, webhooks,", 13) + text(375, 74, "vendor extractor, files it drops", 13)
    b += text(375, 93, "sees deletes · starts when data is ready", 12, fill="#1d6b3a")
    b += f'<rect x="230" y="148" width="290" height="92" rx="14" fill="{FILL["butter"]}" stroke="#1F1F1F" stroke-width="1.4" stroke-dasharray="6 5"/>'
    b += text(375, 172, "Pull: we fetch", 18, fill="#1F1F1F")
    b += text(375, 194, "query since last load, full extract,", 13) + text(375, 212, "API polling, folder polling", 13)
    b += text(375, 231, "needs a trusted 'modified' column · runs on a clock", 12, fill="#8a5a00")
    b += arrow(192, 95, 228, 62) + arrow(522, 62, 558, 95)
    b += arrow(192, 155, 228, 188) + arrow(522, 188, 558, 155)
    b += text(650, 215, "or: read in place (share, mirror)", 13)
    return svg(750, 250, b, "Push: the source sends changes to us. Pull: we ask the source on our schedule. Or we read a share in place."), \
        "Push or pull. Push catches deletes and starts when data is ready; pull is simpler to start but runs on a clock and needs a trusted change column."


def rows_table(rows, marks=None):
    marks = marks or {}
    h = "<tr><th>customer_id</th><th>name</th><th>city</th><th>updated_at</th></tr>"
    for r in rows:
        cls = marks.get(r[0], "")
        h += "<tr>" + "".join(f'<td class="{cls}">{E(c)}</td>' for c in r) + "</tr>"
    return f'<div class="tw"><table class="t rows">{h}</table></div>'


def upstreams():
    pp_svg, pp_cap = push_pull()
    types = "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td>{E(c)}</td><td>{E(d)}</td></tr>" for a, b, c, d in SOURCE_TYPES)
    hand = "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td>{E(c)}</td><td>{E(d)}</td><td>{E(e)}</td><td>{E(f)}</td></tr>" for a, b, c, d, e, f in HANDOVER)
    q, n_q = q_table(QUESTIONS)
    loads = "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td>{E(c)}</td><td>{E(d)}</td><td>{E(e)}</td></tr>" for a, b, c, d, e in LOAD_PATTERNS)
    protect = "".join(f"<li>{E(x)}</li>" for x in PROTECT)
    fields = "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td>{E(c)}</td><td><code>{E(d)}</code></td></tr>" for a, b, c, d in FIELDS)
    prof = "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td></tr>" for a, b in PROFILE)
    dec = dec_html(DECISIONS)
    leaders = "".join(f"<li>{E(x)}</li>" for x in LEADERS_UP)
    faq = "".join(f'<details class="faq"><summary>{E(a)}</summary><p>{E(b)}</p></details>' for a, b in FAQ_UP)
    day2 = [("101", "Asha", "Mumbai", "10:02"), ("103", "Meena", "Agra", "10:09"), ("104", "Joseph", "Kochi", "09:15 (next day)")]
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › <a href="{BASE}">Data systems</a> › Upstreams</p>
<p class="eyebrow" style="margin-top:22px">Data systems · block 1 of 3 · for data leaders, then builders</p>
<h1>Upstreams: know your sources</h1>
<p class="promise">Know how each source behaves before writing a single pipeline.</p>
<p class="lede">This is the page to walk a client through before any build. It lists the kinds of sources, the ways each can hand data over, and the questions we need answered for every source and every dataset, each with the reason we ask.</p>
<div class="leaders"><h3>For leaders</h3><ul>{leaders}</ul>
<p style="margin:10px 0 0"><a class="btn" href="{BASE}upstreams/questionnaire/">Printable questionnaire for your team</a></p></div>
<nav class="toc"><b>On this page</b><ol>
<li><a href="#plain">In plain words</a></li><li><a href="#types">Kinds of sources</a></li><li><a href="#handover">Push, pull or share</a></li>
<li><a href="#trigger">Schedule or event</a></li><li><a href="#change">How a dataset changes</a></li><li><a href="#load">Full load or incremental</a></li><li><a href="#protect">Protecting the source</a></li><li><a href="#joins">Relationships and joins</a></li><li><a href="#questions">The question list ({n_q} questions)</a></li>
<li><a href="#fields">Fields we ask for in every dataset</a></li><li><a href="#profile">Why we ask to scan your data</a></li>
<li><a href="#decisions">Design decisions</a></li><li><a href="#faq">Questions people ask</a></li><li><a href="#next">How we build it</a></li></ol></nav>

<section id="plain"><p class="eyebrow">In plain words</p><h2>Ask about the well before laying the pipe</h2>
<p>An engineer connecting a town to a new well asks a few things first. How much water does it give? When does it run low? Does it flood? Who owns it, and will they tell us before they dig a new one? Is the water clean, and can we take a sample to test? None of this is about the pipe. All of it decides whether the pipe works.</p>
<p>Source systems are the wells. They were built to run a business, not to feed a data platform. Each one has habits: how it records changes, whether it really deletes rows, when its nightly jobs finish. The questions on this page find those habits early, while changing course is cheap.</p></section>

<section id="types"><p class="eyebrow">Kinds of sources</p><h2>Seven kinds of sources</h2>
<p>Most estates mix all seven. Each kind tends to offer some ways of handing data over and to fail in its own ways.</p>
<div class="tw"><table class="t"><tr><th>Kind</th><th>Examples</th><th>Usual ways to get the data</th><th>What to watch</th></tr>{types}</table></div></section>

<section id="handover"><p class="eyebrow">Integration patterns</p><h2>Push, pull or share</h2>
<p>There are three basic ways data can reach us. The source can <b>push</b> changes to us, we can <b>pull</b> them on our schedule, or the source can <b>share</b> tables that we read in place. Which one is possible depends on what the source supports, so we ask about all of them.</p>
<figure class="diagram">{pp_svg}<figcaption>{E(pp_cap)}</figcaption></figure>
<div class="tw"><table class="t"><tr><th>Pattern</th><th>Push or pull</th><th>How it works</th><th>Sees hard deletes?</th><th>Good for</th><th>Watch for</th></tr>{hand}</table></div></section>

<section id="trigger"><p class="eyebrow">Timing</p><h2>Schedule or event</h2>
<p>A scheduled load starts at a fixed time and hopes the data is ready. On the night the source runs late, it loads half a file, an empty folder or yesterday's data, and nothing fails. Most "the dashboard is wrong this morning" incidents start this way.</p>
<p>An event-driven load starts when the source says the data is ready: a change arrives on the CDC stream, a file lands with its done marker, or the source publishes a "batch complete" event. Time stops being a guess. So we ask every source whether it can signal readiness. When it can't, we still schedule, but we check completeness first (the expected row count, the marker file, the control total) and wait or alert instead of loading.</p></section>

<section id="change"><p class="eyebrow">How data changes</p><h2>How a dataset changes, and why we keep asking</h2>
<p>Here is a customer table on day one, and the same table the next day. We load incrementally using <code>updated_at</code>, taking only the rows changed since the last load.</p>
<p class="note">Day one</p>{rows_table(ROWS_DAY1)}
<p class="note">Day two: Asha moved to Mumbai, Ravi was deleted, Joseph was added</p>{rows_table(day2, {"101": "bad", "104": "new"})}
<p>Look at what the incremental query sees. Joseph is new, so his row is picked up. Asha's city changed, but the app's bulk-update script didn't touch <code>updated_at</code>, so her change is <b>missed</b>. Ravi was hard-deleted, so there is no row left to find, and he is <b>still a customer</b> in our platform. The load succeeded, and two of three changes were lost.</p>
<p>That is why the question list asks which kinds of change happen, who sets the modified time, and whether deletes are hard or soft. The answers decide between an incremental query, change data capture and a full comparison; the <a href="#load">load patterns</a> below set them side by side.</p></section>

<section id="load"><p class="eyebrow">Full or incremental</p><h2>Full load or incremental: the patterns</h2>
<p>Every dataset is loaded one of a few ways. A full load is the simplest and the safest when the table is small or the source has no reliable way to say what changed. An incremental load is cheaper for big tables but needs a change signal you can trust and a plan for deletes. Most platforms use both: incremental every run, and a full comparison now and then to prove nothing drifted.</p>
<div class="tw"><table class="t"><tr><th>Pattern</th><th>How it works</th><th>Sees hard deletes?</th><th>Use it for</th><th>Watch for</th></tr>{loads}</table></div>
<p>Questions F1 to F8 below decide which pattern each dataset gets.</p></section>

<section id="protect"><p class="eyebrow">Protecting the source</p><h2>Take the data without hurting the system</h2>
<p>The source system runs the business; our extraction is a guest. If we slow it down once, we lose access. These rules keep it safe (questions C1 to C7 below):</p>
<ul>{protect}</ul></section>

<section id="joins"><p class="eyebrow">Relationships</p><h2>How datasets join, and how joins go wrong</h2>
<p>Silver and gold are built by joining datasets: orders to order lines, lines to products, customers across the CRM and billing. Two things go wrong. A join assumed to match one row that sometimes matches two <b>multiplies</b> numbers: an order with two rows in a "one per order" table counts its revenue twice. A join to a parent that is missing <b>drops</b> rows: order lines whose order hasn't arrived disappear from an inner join. So we ask for the relationship map, then measure in profiling how many rows really match on each side and how many have no parent (questions I1 to I7 below).</p></section>

<section id="questions"><p class="eyebrow">The question list</p><h2>Every question, why we ask, and what breaks if nobody does</h2>
<p>One list, grouped by category. Ask it once per source system, then once per dataset for categories F, G, H and I. The fourth column is what we have seen go wrong in production when the question was skipped.</p>
{q}</section>

<section id="fields"><p class="eyebrow">Per dataset</p><h2>Fields we ask you to point at in every dataset</h2>
<p>For each dataset, we ask which column (if any) plays each role. A blank is fine, but it is a decision. For example, "no last modified time" means change data capture or a full comparison.</p>
<div class="tw"><table class="t"><tr><th>Role</th><th>What it is</th><th>Why we need it</th><th>Example</th></tr>{fields}</table></div></section>

<section id="profile"><p class="eyebrow">Profiling</p><h2>Why we ask to scan your data</h2>
<div class="why"><p style="margin:0">The later layers are written from what the data really contains. Silver's cleaning rules, gold's joins and the semantic layer's metric definitions all depend on it. Documentation describes what the data should contain; profiling shows what it does contain. So we ask for a copy of production data in a sandbox. If it holds personal data, it is masked consistently, so the same person gets the same token everywhere and joins still work. If it holds none, a read-only copy as is will do. If data may not leave your environment at all, we run the profiler inside it and take only the summary out.</p></div>
<div class="tw"><table class="t"><tr><th>What we look at</th><th>What it decides later</th></tr>{prof}</table></div></section>

<section id="decisions"><p class="eyebrow">Design decisions</p><h2>The decisions this block forces</h2>{dec}</section>

<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{faq}</section>

<section id="next"><p class="eyebrow">Next</p><h2>How we build it, and where to go next</h2>
<p><b>Hand it over:</b> the <a href="{BASE}upstreams/questionnaire/">printable questionnaire</a> has every question above with a blank answer column, plus a per-dataset sheet.</p>
<p><b>How we build ingestion:</b> <a href="/learn/data-platform-architecture/ingestion/">Ingestion: sources to bronze</a> (six ways in, a new source as a few lines of YAML) and <a href="/learn/data-platform-architecture/metadata-store/">the metadata store</a>, where these answers live as configuration.</p>
<p><b>The project around it:</b> <a href="/learn/technical-anchor/discovery/">Technical anchor: discovery</a>.</p>
<p><b>Back up:</b> <a href="{BASE}">Data systems, end to end</a>.</p>
<div class="ideas"><a href="/concepts/data-contracts/">Data contracts</a><a href="/concepts/idempotency/">Idempotency</a><a href="/concepts/data-quality/">Data quality</a><a href="/concepts/scd/">Slowly changing dimensions</a><a href="/concepts/lineage/">Lineage</a></div></section>"""
    title = "Upstreams: know your sources"
    desc = f"What a data platform team needs to know about every source system, and why: push, pull or share, schedule or event, how rows change, keys and dates, profiling with masked data, and {n_q} questions with what breaks in production if nobody asks."
    url = f"{SITE}{BASE}upstreams/"
    return wb.page(title, desc, url, body, CSS + ld(title, desc, url, [("Learn", "/learn/"), ("Data systems", BASE), ("Upstreams", f"{BASE}upstreams/")], FAQ_UP)), n_q


def questionnaire():
    q = ""
    for cid, cat, sub, rows in QUESTIONS:
        scope = " (answer per dataset)" if cid in ('F', 'G', 'H', 'I') else ""
        q += f'<tr class="cat"><td colspan="4">{cid} · {E(cat)}<span>{E(sub)}{scope}</span></td></tr>'
        for i, (qq, why, _b, _d) in enumerate(rows):
            q += f"<tr><td class='id'>{cid}{i + 1}</td><td>{E(qq)}</td><td>{E(why)}</td><td class='ans'></td></tr>"
    f = "".join(f"<tr><td><b>{E(a)}</b><br><span class='note'>{E(b)}</span></td><td class='ans'></td><td class='ans'></td></tr>" for a, b, _c, _d in FIELDS)
    css = CSS + """<style>
  .ans { min-width:220px; border-left:1.5px dashed var(--rule-firm); }
  .meta { display:grid; grid-template-columns:1fr 1fr; gap:6px 24px; border:var(--line); border-radius:var(--wob); padding:12px 18px; margin:14px 0; }
  .meta div { border-bottom:1.5px dashed var(--rule-firm); padding:6px 0; font-size:14px; color:var(--muted); }
  @media print {
    header, aside.sidepanel, .scrim, footer, .noprint { display:none !important; }
    body { background:#fff; } main, .wrap { max-width:none !important; margin:0 !important; padding:0 !important; }
    table.t { font-size:11px; } table.t tr { page-break-inside:avoid; } .ans { min-width:200px; }
    h2 { page-break-before:always; } h2.first { page-break-before:avoid; }
  }
</style>"""
    body = f"""<p class="crumbs noprint"><a href="/">Home</a> › <a href="/learn/">Learn</a> › <a href="{BASE}">Data systems</a> › <a href="{BASE}upstreams/">Upstreams</a> › Questionnaire</p>
<h1 style="margin-top:22px">Source system questionnaire</h1>
<p class="lede">Please fill one copy per source system. Sections F, G, H and I, and the dataset sheet at the end, are answered once per dataset. "Don't know" is a useful answer, because it tells us what to profile. The reasons behind every question are on the <a href="{BASE}upstreams/">Upstreams page</a>.</p>
<p class="noprint"><button class="btn" onclick="window.print()">Print or save as PDF</button></p>
<div class="meta"><div>Source system:</div><div>Date:</div><div>Business owner:</div><div>Technical owner:</div><div>Filled in by:</div><div>Datasets covered:</div></div>
<h2 class="first">Part 1 · The source system</h2>
<div class="tw"><table class="t"><tr><th>#</th><th>Question</th><th>Why we ask</th><th>Your answer</th></tr>{q}</table></div>
<h2>Part 2 · Per dataset: which column plays each role?</h2>
<p>Dataset name: ______________________ &nbsp; Approx. rows: __________ &nbsp; Rows per day: __________</p>
<div class="tw"><table class="t"><tr><th>Role</th><th>Column name(s), or "none"</th><th>Notes</th></tr>{f}</table></div>
<h2>Part 3 · Access to profile real data</h2>
<div class="tw"><table class="t"><tr><th>Option</th><th>Possible? (yes / no / with conditions)</th></tr>
<tr><td>A copy of production in a sandbox, as is (no personal data)</td><td class="ans"></td></tr>
<tr><td>A masked copy of production in a sandbox (consistent masking so joins work)</td><td class="ans"></td></tr>
<tr><td>Profiling run inside your environment; only the summary leaves</td><td class="ans"></td></tr>
<tr><td>Person who will review the profile with us</td><td class="ans"></td></tr></table></div>"""
    title = "Source system questionnaire"
    desc = "A printable questionnaire for source system owners: access, push and pull support, how data changes, keys and dates, schema, volume, profiling access, sensitivity and reconciliation."
    url = f"{SITE}{BASE}upstreams/questionnaire/"
    return wb.page(title, desc, url, body, css + ld(title, desc, url, [("Learn", "/learn/"), ("Data systems", BASE), ("Upstreams", f"{BASE}upstreams/"), ("Questionnaire", f"{BASE}upstreams/questionnaire/")]))


def main():
    out = ROOT / "learn" / "data-systems"
    (out / "upstreams" / "questionnaire").mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(overview())
    up, n_q = upstreams()
    (out / "upstreams" / "index.html").write_text(up)
    (out / "upstreams" / "questionnaire" / "index.html").write_text(questionnaire())
    print(f"data systems -> {out} ({n_q} upstream questions)")


if __name__ == "__main__":
    main()
