"""The ecosystem big picture and the Reviews and sign-offs page.

    python3 _guides/de_reviews.py     (then python3 _guides/de_essentials.py, python3 _site/nav.py, python3 _site/seo.py)

/how-we-work/data-essentials/ecosystem/   one big picture: client, us, vendors and platforms across the DDLC, failures in red
/how-we-work/data-essentials/ecosystem/picture/   the same picture on its own page, full width
/how-we-work/data-essentials/reviews/     internal and external reviews, platform vendor design review, sign-offs
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import de_essentials as DE  # noqa: E402
import de_ess_data as D  # noqa: E402

E, R, T, table, fig, Lx, L, C = DE.E, DE.R, DE.T, DE.table, DE.fig, DE.Lx, DE.L, DE.C
BLUE, MINT, BUTTER, ROSE, LAV, GREY = DE.BLUE, DE.MINT, DE.BUTTER, DE.ROSE, DE.LAV, DE.GREY
BASE = DE.BASE
RED = "#d03b3b"
INKC = "#111"

# ------------------------------------------------------------------------------------------ the big picture
DEFS = ('<defs><marker id="ga" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#111"/></marker>'
        '<marker id="gr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#d03b3b"/></marker></defs>')


def person(cx, y, fill, tag, label):
    lines = label if isinstance(label, list) else [label]
    d = f'<circle cx="{cx}" cy="{y + 10}" r="10" fill="#fff" stroke="#111" stroke-width="1.5"/>'
    d += f'<path d="M{cx - 21},{y + 48} Q{cx - 21},{y + 24} {cx},{y + 24} Q{cx + 21},{y + 24} {cx + 21},{y + 48} Z" fill="{fill}" stroke="#111" stroke-width="1.5"/>'
    d += f'<text x="{cx}" y="{y + 42}" text-anchor="middle" font-size="10.5" font-weight="700">{E(tag)}</text>'
    for i, t in enumerate(lines):
        d += f'<text x="{cx}" y="{y + 64 + i * 14}" text-anchor="middle" font-size="12.5">{E(t)}</text>'
    return d


def arrow(x1, y1, x2, y2, both=True):
    ms = ' marker-start="url(#ga)"' if both else ""
    return f'<path d="M{x1},{y1} L{x2},{y2}" stroke="#111" stroke-width="1.5" fill="none"{ms} marker-end="url(#ga)"/>'


def bad(x, y, n, text="", anchor="start", tx=None, ty=None):
    d = f'<circle cx="{x}" cy="{y}" r="11" fill="{RED}" stroke="#fff" stroke-width="1.5"/><text x="{x}" y="{y + 4.5}" text-anchor="middle" font-size="12.5" font-weight="700" style="fill:#fff">{n}</text>'
    d += f'<text x="{x - 3}" y="{y - 1}" text-anchor="middle" font-size="16" font-weight="700" style="fill:{RED}" opacity="0">✕</text>'
    if text:
        d += f'<text x="{tx if tx is not None else x + 16}" y="{ty if ty is not None else y + 4}" text-anchor="{anchor}" font-size="12" style="fill:{RED}" font-weight="700">{E(text)}</text>'
    return d


def label(x, y, lines, anchor="start", size=12):
    return "".join(f'<text x="{x}" y="{y + i * 13}" text-anchor="{anchor}" font-size="{size}">{E(t)}</text>' for i, t in enumerate(lines))


# number, what goes wrong, between, stage, effect, prevention (backlog ids)
FAILS = [
    (1, "Source owners are not engaged", "Source owners and the Sources", "2 to 3", "Meaning guessed, access late, changes unannounced", ["SRC-01", "SRC-02", "SRC-07"]),
    (2, "Scope and date drift; bad news arrives late", "Sponsor and PM", "all", "Surprises at gates; trust lost", ["PRJ-15", "PRJ-14"]),
    (3, "Requirements are wishes, not testable checks", "Business owners and BA", "1 to 3", "Rework at acceptance", ["PRJ-01", "CON-03"]),
    (4, "Two definitions of one number", "Business owners and Finance", "3 to 5", "Two reports, two revenues, one argument", ["MNG-02", "MDL-03"]),
    (5, "Hand-off gap between BA and Tech Anchor", "BA and Tech Anchor", "3 to 6", "Build does not match what was meant", ["PRJ-13", "MDL-02"]),
    (6, "No reconciliation plan", "Finance and the build team", "3 to 9", "It ran; it was wrong; nobody checked", ["MDL-04", "MDL-06"]),
    (7, "Environments late and cost unowned", "Client IT and Tech Anchor", "5", "Team idle; surprise bill", ["PRJ-12", "COS-01"]),
    (8, "Security and privacy approvals late", "Security and our architect", "3 to 8", "Late stop; clean-up; delayed go-live", ["SEC-02", "SEC-03"]),
    (9, "Users unavailable for acceptance", "End users and the test lead", "7", "Acceptance on fake data; rejection at go-live", ["CON-06", "CON-07"]),
    (10, "Operations not involved until go-live", "Operations and the BI developer", "6 to 9", "Nobody can run it", ["RUN-04", "RUN-06"]),
    (11, "Design review with the platform vendor skipped", "Our architect and the platform vendor", "4", "Limits, cost and design flaws found in production", ["REV-04", "REV-12"]),
    (12, "Cloud limits and costs unknown until the bill", "Cloud provider and the platform", "4 to 8", "Redesign or over-budget", ["REV-05", "COS-03"]),
    (13, "No support route agreed with the vendor", "Platform vendor and the platform", "8 to 9", "Slow fixes in an incident", ["REV-04", "RUN-05"]),
    (14, "Data vendor feed late or schema changed", "Data vendor and the Sources", "6 to 9", "Silent breakage upstream", ["SRC-13", "SRC-07"]),
    (15, "Old report kept; two truths", "Consumers and end users", "9 to 10", "Built, but not used", ["CON-04", "CON-10"]),
]

ROLES = [
    ("Client", "Source system owners", "Run the systems the data comes from.", "Own the source data and its changes.", "Explain, give access, announce changes.", "BA, Tech Anchor, data vendor", "2 to 9"),
    ("Client", "Sponsor", "Pays and decides go, change or stop.", "Scope, money, priorities, gate decisions.", "Does not touch data; owns the decision it supports.", "PM", "1, 4, 9, 10"),
    ("Client", "Business owners", "Own the question, definitions and acceptance.", "Metric definitions, requirements, acceptance.", "Define numbers, accept reports.", "BA, Finance", "1 to 9"),
    ("Client", "Finance", "Own the numbers the business trusts.", "Reconciliation targets; sometimes the budget.", "Provide figures to match; sign totals.", "BA, data engineers", "3, 7, 9"),
    ("Client", "Client IT and platform team", "Provide accounts, networks, environments, standards, cost control.", "Cloud accounts, network, tooling.", "Run the foundation the platform sits on.", "Tech Anchor, cloud provider", "2 to 9"),
    ("Client", "Security, privacy, compliance", "Protect people and the company; can stop a release.", "Access policy, privacy reviews, audit.", "Approve access and data use.", "Architect", "3 to 9"),
    ("Client", "End users", "Use the reports and tools daily.", "Acceptance and adoption.", "Consume the data; give feedback.", "Test lead, BI developer", "3, 7, 9, 10"),
    ("Client", "Operations and support", "Run the system after the project ends.", "Runbooks, alerts, incidents.", "Monitor, rerun, fix, escalate.", "BI developer, Tech Anchor", "5 to 10"),
    ("Us", "Project or delivery manager", "Plans, tracks, reports, chases.", "Plan, scope, risks, gates.", "Does not touch data; unblocks access.", "Sponsor, all", "all"),
    ("Us", "Business analyst", "Owns the question.", "Requirements, definitions, acceptance criteria.", "Understands sources and consumers.", "Business owners, Finance", "1 to 9"),
    ("Us", "Data engineers", "Build and run pipelines.", "Pipelines, tests, data quality.", "Land, clean, model the data.", "Tech Anchor, Finance", "5 to 9"),
    ("Us", "Tech Anchor", "Owns the technical shape end to end.", "Design, spikes, estimates, test strategy.", "Profiles data, designs the platform use.", "BA, PM, client IT, vendors", "all"),
    ("Us", "Our architect", "Designs and reviews architecture.", "Standards, design decisions.", "Shapes how the platform is used.", "Security, vendors", "3, 4, 8"),
    ("Us", "Test lead", "Plans and runs testing.", "Test strategy and evidence.", "Tests the numbers.", "End users", "5 to 9"),
    ("Us", "BI developer", "Builds reports and the semantic layer.", "Reports, metrics layer.", "Serves the data to people.", "Operations, end users", "6 to 9"),
    ("Vendors", "Cloud provider", "Supplies infrastructure, support and best-practice guidance.", "Reliability and limits of the cloud.", "Hosts storage, compute, security.", "Client IT, Tech Anchor", "3, 4, 8, 9"),
    ("Vendors", "Platform vendor (for example Databricks)", "Supplies the data platform, support and design guidance.", "The product and its roadmap.", "Runs pipelines, tables, governance, AI.", "Our architect", "3, 4, 8, 9"),
    ("Vendors", "BI tool vendor (for example Power BI)", "Supplies the reporting product.", "The reporting product.", "Serves reports to people.", "BI developer", "6 to 9"),
    ("Vendors", "Data or software vendor", "Supplies data feeds or a source application.", "Feed contents and schema.", "Is a source.", "Source owners", "2 to 9"),
]


def d_ecosystem():
    b = DEFS
    stages = [("1", "Need"), ("2", "Estimate"), ("3", "Discovery"), ("4", "Sign-off"), ("5", "MVP start"), ("6", "Build"), ("7", "Test"), ("8", "Deploy"), ("9", "Prod sign-off"), ("10", "Close")]
    gates = {4, 9, 10}
    for i, (n, nm) in enumerate(stages):
        b += R(20 + i * 128, 8, 120, 40, "#FFF1C2" if (i + 1) in gates else (BUTTER if i < 4 else MINT), [f"{n} {nm}"] + (["gate"] if (i + 1) in gates else []), 14, sw=2.5 if (i + 1) in gates else 1.5)
    b += T(272, 66, "Decide", 15) + T(848, 66, "Deliver, one small working piece (MVP) at a time", 15) + T(1232, 66, "Close", 15)
    # zones
    b += '<rect x="10" y="78" width="1280" height="124" rx="14" fill="#F1F4FB" fill-opacity="0.6" stroke="#111" stroke-width="1.3" stroke-dasharray="4 5"/>' + T(46, 96, "CLIENT", 14, "start")
    b += '<rect x="10" y="278" width="1280" height="124" rx="14" fill="#F0F8F3" fill-opacity="0.7" stroke="#111" stroke-width="1.3" stroke-dasharray="4 5"/>' + T(46, 296, "US (the delivery team)", 14, "start")
    b += '<rect x="10" y="616" width="1280" height="164" rx="14" fill="#FFF8E8" fill-opacity="0.8" stroke="#111" stroke-width="1.3" stroke-dasharray="4 5"/>' + T(46, 634, "PLATFORM VENDORS AND PARTNERS", 14, "start")
    cl = [(90, "SRC", "Source owners"), (240, "$", "Sponsor"), (390, "BO", "Business owners"), (540, "FIN", "Finance"), (690, "IT", "Client IT"), (840, "SEC", "Security"), (990, "USR", "End users"), (1140, "OPS", "Operations")]
    for cx, tag, nm in cl:
        b += person(cx, 104, BLUE, tag, nm if " " not in nm or len(nm) < 12 else nm.split(" ", 1))
    us = [(240, "PM", "PM"), (390, "BA", "BA"), (540, "DE", "Data engineers"), (690, "TA", "Tech Anchor"), (840, "ARC", "Our architect"), (990, "QA", "Test lead"), (1140, "BI", "BI developer")]
    for cx, tag, nm in us:
        b += person(cx, 300, MINT, tag, nm if len(nm) < 12 else nm.split(" ", 1))
    # data systems
    b += R(60, 450, 270, 100, GREY, ["Source systems", "apps, files, APIs"], 17)
    b += R(420, 450, 460, 100, "#fff", [], 15, sw=2.5)
    b += R(432, 458, 436, 40, BLUE, ["Cloud: storage, compute, network, security"], 14) + R(432, 504, 436, 40, LAV, ["Data platform (for example Databricks): pipelines, tables, governance, AI"], 13.5)
    b += R(970, 450, 270, 100, MINT, ["Consumers", "reports, apps, AI assistants"], 17)
    b += arrow(332, 500, 418, 500, False) + label(375, 490, ["land,", "clean"], "middle", 11.5) + arrow(882, 500, 968, 500, False) + label(925, 490, ["serve"], "middle", 11.5)
    b += T(10 + 640, 440, "THE DATA SYSTEM", 13) if False else ""
    # client -> us pairs
    b += arrow(240, 188, 240, 294) + label(250, 232, ["scope, dates,", "decisions"]) + bad(228, 262, 2, "bad news late", tx=250, ty=262)
    b += arrow(390, 188, 390, 294) + label(400, 232, ["needs, definitions,", "acceptance"]) + bad(378, 262, 3, "wishes, not checks", tx=400, ty=262)
    b += arrow(432, 150, 498, 150) + label(465, 142, ["define"], "middle", 11.5) + bad(465, 166, 4, "two revenues", "middle", tx=465, ty=184)
    b += arrow(540, 188, 540, 294) + label(550, 226, ["reconcile", "totals"]) + bad(528, 262, 6, "not planned", tx=550, ty=262)
    b += arrow(690, 188, 690, 294) + label(700, 226, ["environments,", "standards, cost"]) + bad(678, 262, 7, "late; cost unowned", tx=700, ty=262)
    b += arrow(840, 188, 840, 294) + label(850, 226, ["approve access,", "review design"]) + bad(828, 262, 8, "approvals late", tx=850, ty=262)
    b += arrow(990, 188, 990, 294) + label(1000, 226, ["acceptance", "testing"]) + bad(978, 262, 9, "users not there", tx=1000, ty=262)
    b += arrow(1140, 188, 1140, 294) + label(1150, 226, ["runbook,", "support"]) + bad(1128, 262, 10, "nobody can run it", tx=1150, ty=262)
    # BA <-> TA handoff
    b += f'<path d="M424,298 Q540,262 656,298" stroke="{RED}" stroke-width="1.8" fill="none" stroke-dasharray="5 4" marker-start="url(#gr)" marker-end="url(#gr)"/>' + bad(540, 276, 5, "", "middle")
    # source owners -> sources
    b += arrow(90, 188, 90, 448, False) + label(100, 232, ["explain, give", "access"]) + bad(90, 330, 1, "", "start") + label(104, 326, ["meaning guessed,", "access late"], "start", 12).replace('<text', '<text style="fill:#d03b3b;font-weight:700"')
    # us -> data
    b += arrow(370, 386, 300, 446, False) + label(330, 418, ["profile"], "end", 11.5)
    b += arrow(540, 386, 540, 446, False) + label(550, 418, ["build, run"], "start", 11.5)
    b += arrow(690, 386, 690, 446, False) + label(700, 418, ["design, release"], "start", 11.5)
    b += arrow(840, 386, 840, 446, False)
    b += arrow(990, 386, 1010, 446, False) + label(1020, 418, ["test the numbers"], "start", 11.5)
    b += arrow(1140, 386, 1140, 446, False) + label(1150, 418, ["build reports"], "start", 11.5)
    # architect <-> platform vendor design review (red)
    b += f'<path d="M868,342 L925,342 L925,598 L800,598 L800,652" stroke="{RED}" stroke-width="1.8" fill="none" stroke-dasharray="5 4" marker-start="url(#gr)" marker-end="url(#gr)"/>' + bad(925, 572, 11, "design review", "start", tx=942, ty=570) + label(942, 584, ["skipped or late"], "start", 12).replace('<text', '<text style="fill:#d03b3b;font-weight:700"')
    # vendors
    vend = [(40, "Data or software vendor", ["supplies data feeds,", "owns schema changes"]), (340, "Cloud provider", ["infrastructure, support,", "best-practice review"]), (640, "Platform vendor", ["(for example Databricks)", "product, design guidance"]), (940, "BI tool vendor", ["(for example Power BI)", "reporting product"])]
    for x, nm, fn in vend:
        b += R(x, 652, 250, 100, "#fff", [], 14)
        b += person(x + 36, 664, BUTTER, "VND", [])
        b += f'<text x="{x + 76}" y="684" font-size="13.5" font-weight="700">{E(nm)}</text>' + "".join(f'<text x="{x + 76}" y="{702 + i * 15}" font-size="12.5">{E(t)}</text>' for i, t in enumerate(fn))
    b += arrow(165, 650, 165, 552, False) + label(175, 600, ["feeds"], "start", 11.5) + bad(150, 598, 14, "late, changed", "end", tx=140, ty=602)
    b += arrow(460, 650, 460, 552, False) + label(470, 590, ["infrastructure,", "support"], "start", 11.5) + bad(448, 604, 12, "limits, cost unknown", "start", tx=480, ty=614) if False else ""
    b += arrow(460, 650, 460, 552, False) + label(470, 584, ["infrastructure,", "support"], "start", 11.5) + bad(448, 608, 12, "", "start") + label(463, 628, [], "start")
    b += label(480, 612, ["limits, cost unknown"], "start", 12).replace('<text', '<text style="fill:#d03b3b;font-weight:700"')
    b += arrow(740, 650, 740, 552, False) + label(750, 584, ["product,", "support"], "start", 11.5) + bad(728, 608, 13, "", "start") + label(748, 612, ["no support route"], "start", 12).replace('<text', '<text style="fill:#d03b3b;font-weight:700"')
    b += arrow(1060, 650, 1060, 552, False) + label(1070, 600, ["reporting", "product"], "start", 11.5)
    b += bad(1100, 520, 15, "old report kept", "start", tx=1114, ty=524) if False else ""
    b += bad(1105, 568, 15, "", "start") + label(1120, 572, ["old report kept; two truths"], "start", 12).replace('<text', '<text style="fill:#d03b3b;font-weight:700"')
    b += T(650, 800, "gray arrows: how the parties work together   ·   red numbered marks: where it breaks when they are not in tandem", 14)
    return f'<svg viewBox="0 0 1300 815" role="img" aria-label="The data project ecosystem across the lifecycle. Top: ten lifecycle stages with three sign-off gates. Client zone: source owners, sponsor, business owners, finance, client IT, security, end users, operations. Us zone: PM, BA, data engineers, Tech Anchor, architect, test lead, BI developer. Middle: source systems, a data platform on a cloud, and consumers. Bottom: data vendor, cloud provider, platform vendor, BI tool vendor. Gray arrows show how parties work together. Fifteen red numbered marks show where each link breaks when the parties are not in tandem.">{b}</svg>'


def ecosystem_page():
    url_path = f"{BASE}ecosystem/"
    fails = table(["#", "What goes wrong", "Between", "Stage", "What it costs", "Prevented by"],
                  [[f'<span style="color:{RED};font-weight:700">{n}</span>', f"<b>{E(w)}</b>", E(b), E(s), E(e), " ".join(f'<a href="{BASE}backlog/#{i}">{i}</a>' for i in p)] for n, w, b, s, e, p in FAILS])
    roles = table(["Party", "Role", "Does", "Owns", "Touches the data system by", "Works most with", "Stages"],
                  [[E(a), f"<b>{E(b)}</b>", E(c), E(d), E(e), E(f), E(g)] for a, b, c, d, e, f, g in ROLES])
    rules = ("<ol><li><b>Every link has a named pair.</b> If you cannot name the two people on a link, it is already red.</li><li><b>Raise outside dependencies first.</b> Source owners, security, client IT and vendors set your pace.</li>"
             "<li><b>Review with someone who did not build it.</b> The vendor and cloud reviews are part of the plan, not a favour.</li><li><b>Bring operations in at MVP 1.</b> Not at go-live.</li>"
             "<li><b>Settle definitions on real data.</b> Show both numbers, let the owner decide, write it down.</li><li><b>Keep the accountability.</b> A vendor can advise. Only we sign.</li></ol>")
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/how-we-work/">How we work</a> › <a href="{BASE}">Data essentials</a> › The ecosystem</p>
<p class="eyebrow" style="margin-top:22px">Topic 1 · Deep dive</p>
<h1>The ecosystem: who does what across the lifecycle</h1>
<p class="lede">One picture of everyone around a data project: the client, our team, and the vendors and platforms. It shows who works with whom, how each touches the data system, and in red, where the project breaks when they are not in tandem.</p>
<div class="tf"><style>.tf .wide{{overflow-x:auto;border:var(--line);border-radius:var(--wob);padding:8px;background:#fff;margin:16px 0}} .tf .wide svg{{min-width:1180px;width:100%;height:auto;display:block}} .tf .wide text{{font-family:var(--hand);fill:#111}}</style>
<section id="picture"><p class="eyebrow">The picture</p><h2>The whole ecosystem, in one view</h2>
<p>Read it from top to bottom. The timeline is the ten stages of the project, with three sign-off gates. The client is on top, our team below, then the data system, then the vendors. Gray arrows are the working relationships. Each red number is a place where the link breaks.</p>
<div class="wide">{d_ecosystem()}</div>
<p>{L(url_path + 'picture/', 'Open the picture full width')} (scroll sideways on a small screen). A person icon marks each role; the letters on the body are the role tag.</p>
<div class="box"><b>In one line:</b> a data project is a chain of hand-offs between about twenty roles in three organisations. It fails at the weakest hand-off, not at the hardest technology.</div></section>
<section id="fails"><p class="eyebrow">In red</p><h2>Fifteen places it breaks</h2>{fails}</section>
<section id="roles"><p class="eyebrow">Who is who</p><h2>Roles, functions and how each touches the data system</h2>{roles}</section>
<section id="rules"><p class="eyebrow">Working in tandem</p><h2>Six rules that keep the links green</h2>{rules}</section>
<section id="next"><p class="eyebrow">Go further</p><h2>Related pages</h2><ul><li>{L(BASE + 'reviews/', 'Reviews and sign-offs, internal and external')}</li><li>{L(BASE + 'cast/', 'The cast')}</li><li>{L(BASE + 'seats/', 'The three seats')}</li>
<li>{L(BASE + 'why-fail/', 'Why data projects fail')}</li><li>{L(BASE + 'ddlc/', 'DDLC by seat')}</li><li>{L(BASE + 'backlog/', 'The corpus backlog')}</li></ul></section>
</div>"""
    title = "The ecosystem: who does what across a data project"
    desc = ("One picture of the client, our team and the vendors and platforms across the data project lifecycle: roles, how each touches the data system, "
            "and in red the fifteen places it breaks when they are not in tandem.")
    return url_path, DE.page_shell(title, desc, url_path, body, [("How we work", "/how-we-work/"), ("Data essentials", BASE), ("The ecosystem", url_path)])


def picture_page():
    url_path = f"{BASE}ecosystem/picture/"
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>The data project ecosystem, full width · Clean Data Engineering</title><meta name="description" content="The client, our team and the vendors and platforms across the data project lifecycle, with failure points in red.">
<link rel="canonical" href="{DE.SITE}{url_path}"><meta name="color-scheme" content="light"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600&family=Patrick+Hand&display=swap">
<style>body{{margin:0;background:#fff;color:#111;font-family:'DM Sans',sans-serif}} header{{padding:14px 22px}} a{{color:#111}} svg{{width:100%;min-width:1100px;height:auto;display:block}} text{{font-family:'Patrick Hand',sans-serif;fill:#111}} .w{{overflow-x:auto}}</style></head>
<body><header><a href="{BASE}ecosystem/">← Back to the ecosystem page</a> · <b>The data project ecosystem, full width</b></header><div class="w">{d_ecosystem()}</div></body></html>"""
    return url_path, html


# ------------------------------------------------------------------------------------------ reviews
REVIEW_TYPES = [
    ("Self-check", "The author", "Before sharing anything", "Catch your own slips with a short checklist.", "None: the author checks their own work."),
    ("Peer review", "A colleague on the team", "Every change and document", "A second pair of eyes on detail: code, queries, definitions.", "Low: same team, shared assumptions."),
    ("Internal formal review", "Tech Anchor, architect, BA lead, test lead, from outside the working group", "At each gate: discovery, design, test, readiness", "Check the whole against criteria, from someone who did not build it.", "Medium: same company, different seat."),
    ("Client review and sign-off", "The client's owners: business, IT, security, finance, operations", "At each gate", "The people who will live with it confirm it fits.", "High for fit; they may lack technical depth."),
    ("External expert review", "Platform vendor, cloud provider, independent assessor, auditor, regulator", "Design (stage 4), readiness (stage 8), and when risk is high", "Specialist knowledge and independence.", "High; but vendors have a commercial interest."),
]

WHAT = [
    ("Requirements and scope", "1 to 4", "BA lead, PM", "Client business owners", "Testable; scope in and out; success measures; assumptions.", "Business owner, sponsor"),
    ("Estimate and plan", "2 to 4", "Tech Anchor, a second estimator", "PMO", "Range, assumptions, discovery costed, dependencies dated.", "Sponsor, PM"),
    ("Discovery document", "3 to 4", "Tech Anchor, BA lead, PM", "Client IT, security, sponsor", "Sources understood; beliefs tested; risks honest; bad news included.", "Sponsor, business owner"),
    ("Architecture and design", "4", "Architect, Tech Anchor, a peer architect", "Client IT architect, platform vendor, cloud provider", "Fit to requirements; security; reliability; cost; limits; operability.", "Client architect, security"),
    ("Data model and metric definitions", "4 to 6", "BA, Tech Anchor", "Business owners, Finance", "Grain; keys; definitions with owners; reconciliation plan.", "Metric owners, Finance"),
    ("Security and privacy design", "3 to 8", "Architect, security lead", "Client security, privacy, compliance", "Classification; access model; masking; retention; audit.", "Security, privacy"),
    ("Pipeline code and tests", "5 to 7", "Peer engineer, Tech Anchor", "None normally", "Reruns safe; tests; data checks; readability.", "Tech Anchor"),
    ("Cost model", "4 to 8", "Tech Anchor, FinOps", "Client IT, finance, cloud provider", "Forecast per slice; alerts; owner; budget.", "Sponsor, finance"),
    ("Test strategy and evidence", "4 to 7", "Test lead, BA", "Business owners, users", "Real numbers; edge cases; volume; recovery.", "Business owner"),
    ("Release and cut-over plan", "8", "Tech Anchor, release lead", "Operations, client IT", "Rehearsed; rollback; history load; timing.", "Operations, sponsor"),
    ("Operational readiness", "8", "Tech Anchor, PM", "Operations, security", "Runbook; monitoring; recovery; support; access.", "Operations"),
    ("Responsible AI use case", "3 to 8", "Tech Anchor, risk lead", "Privacy, legal, business owner", "Risk tier; fairness; oversight; evaluation.", "Business owner, risk"),
    ("Hand-over pack", "9 to 10", "Tech Anchor, BA", "Support team", "Support can make a change unaided.", "Operations"),
]

METHOD = [("1 Prepare", "Send the pack three working days ahead, with the criteria. One short summary page on top."), ("2 Read alone", "Each reviewer reads and logs findings before the meeting."),
          ("3 Meet", "30 to 60 minutes on findings only. No presentations. Decide, do not debate."), ("4 Decide", "Approve, approve with conditions, or reject. Say which."), ("5 Follow up", "Each finding has an owner and a date. Re-review the blockers.")]
SEVERITY = [("Blocker", "Stops the gate. Must be fixed before proceeding."), ("Major", "Fix before go-live, or accept in writing with a date."), ("Minor", "Fix when convenient. Track it."), ("Note", "An observation. No action needed.")]

VENDOR_AREAS = [
    ("Account, network and identity layout", "How accounts, workspaces, networks and identities are organised.", "Does the layout match our environments and our security rules?"),
    ("Data governance and access", "Catalogue, permissions, masking, audit.", "Can we enforce who sees what, and prove it?"),
    ("Ingestion and pipeline approach", "How data lands and moves.", "Does the pattern fit our sources, volumes and freshness?"),
    ("Data layout and file design", "Table design, file sizes, partitioning.", "Will it stay fast and cheap as it grows?"),
    ("Compute choice and sizing", "Which compute, how big, when it starts and stops.", "Is it right-sized, and what does it cost per run?"),
    ("Cost controls", "Tags, budgets, alerts, chargeback.", "Can we see and cap the bill by team and workload?"),
    ("Release and environments", "Deployment pipeline, environment parity, configuration.", "Can we release safely, with rollback?"),
    ("Reliability, backup and recovery", "Failure handling, backup, recovery targets.", "What happens in a failure, and how fast do we recover?"),
    ("Monitoring and operability", "Logs, metrics, alerts, runbooks.", "Can operations see and fix problems without the builders?"),
    ("Limits, quotas and known constraints", "Service limits and fair-use rules.", "Will we hit a limit at our volume?"),
    ("Support plan and escalation", "Support tiers, response times, named contacts.", "Who do we call at 3 a.m., and what do they promise?"),
    ("Roadmap and deprecations", "Features coming, features going.", "Are we building on something being retired?"),
]

VENDOR_PREP = ["Share a design pack: context, requirements, volumes, non-functional needs, the design and the alternatives you rejected.", "Agree scope and confidentiality in writing first. Share design and metadata, not real data.",
               "Ask for findings in writing, rated by severity, with the reasoning.", "Ask what the review does not cover. Vendors review how their product is used, not your business rules.",
               "Invite the people who will run it, not only the designers.", "Record each finding as accepted, rejected or deferred, with a reason, in the decision log."]
VENDOR_CAUTION = [("The vendor has a commercial interest", "Advice may favour more of their product. Ask for the cheapest design that meets the need, and a second opinion on big spend."),
                  ("A vendor review is not your sign-off", "You stay accountable. A vendor's 'looks fine' does not transfer responsibility."),
                  ("A review of the design is not a review of the data", "Vendors rarely see your real data problems. Keep profiling and reconciliation with us."),
                  ("Review services differ by agreement", "Check what your contract includes, how long it takes to book, and who from the vendor attends."),
                  ("Best-practice frameworks help", "Cloud providers publish best-practice frameworks for security, reliability, cost and operations, and platform vendors publish similar guidance. Use them as a checklist, and still think.")]

SIGNOFFS = [
    ("Discovery sign-off", "4", "Go, change or stop; scope, estimate, risks", "Sponsor, business owner; our delivery lead and Tech Anchor", "Reviewed discovery document; fail-fast test results", "Conditions: scope or date changes, written"),
    ("Design and security sign-off", "4", "Architecture, security and privacy design", "Client architect, security and privacy; our architect and Tech Anchor", "Design review record; vendor findings and decisions", "Conditions: named findings, dated"),
    ("Definitions and model sign-off", "4 to 6", "Metric definitions and the model", "Metric owners, Finance; our BA", "Metric catalogue; reconciliation plan", "Conditions: unresolved definitions listed"),
    ("Test and acceptance sign-off", "7", "The numbers and the reports", "Business owners; our test lead", "Test evidence; reconciliation; acceptance results", "Conditions: accepted defects, dated"),
    ("Operational readiness sign-off", "8", "Can operations run it?", "Operations, security; our Tech Anchor and PM", "Ops gate checklist; failure drill report", "Conditions: only minor items"),
    ("Production sign-off", "9", "It is live and reconciled", "Business owner, operations, sponsor", "First production reconciliation; hypercare plan", "Conditions: hypercare exit criteria"),
    ("Project sign-off", "10", "Benefits and hand-over", "Sponsor; our delivery lead", "Benefits report; support makes a change unaided", "Conditions: none open"),
]
SIGN_RULES = ["The signer has read it. Ask them to say what they are signing.", "One person is accountable. Others are consulted.", "'Conditional' means named conditions, with owners and dates.", "Silence is not a signature.",
              "The sign-off lists the evidence it rests on.", "A sign-off can be withdrawn if the evidence changes.", "Record it in one register: what, who, when, conditions."]

WRONG = [
    ("Rubber stamp", "Reviewers approve because the deadline is near.", "Problems reach production", "Reviewers can say stop; blockers are listed; the sponsor protects them"),
    ("Reviewer lacks context", "A fresh reviewer gets a 200-page pack.", "Shallow findings", "One-page summary on top; a short briefing"),
    ("Review too late", "Design review after build started.", "Rework costs weeks", "Put reviews in the plan at stage 4, not stage 8"),
    ("No independence", "The author picks and briefs the reviewer.", "Blind spots stay", "Reviewers from outside the working group"),
    ("Findings ignored", "No owner, no date.", "Same issue again", "Findings log with owners; blockers re-reviewed"),
    ("Review replaces testing", "'It was reviewed' stands in for evidence.", "Unproven numbers", "Reviews check evidence; they do not replace it"),
    ("Vendor review accepted as neutral", "Advice leads to more spend.", "Over-engineering, higher bill", "Record the interest; ask for the cheapest design that works; get a second opinion on big spend"),
    ("External review not booked", "Lead time is weeks.", "Design sign-off waits", "Book at stage 2, in the calendar"),
    ("Wrong person signs", "A delegate who does not own the risk signs.", "No real accountability", "Sign-off register names the accountable person"),
    ("Signing without reading", "A signature on a long document.", "Surprises later", "Ask the signer to state the three key points"),
    ("Confidential data shared", "Real data sent to a vendor for review.", "A privacy incident", "Share design and metadata only"),
    ("Non-functional ignored", "Review looks at features only.", "Slow, costly, fragile", "Criteria include performance, cost, recovery, security, operability"),
    ("Disagreement left open", "Two reviewers differ; nobody decides.", "Delay or inconsistency", "Name a decider before the review"),
    ("Review fatigue", "Too many reviews, all the same size.", "Everyone stops caring", "Scale the review to the risk")]

CAL = [("1 to 2", "Review calendar (REV-01). Independent estimate review (REV-11). Book external reviews."), ("3", "Discovery review; security and privacy review; responsible AI use-case review if AI is in scope."),
       ("4", "Design review, internal (REV-03); platform vendor and cloud reviews (REV-04, REV-05); design and discovery sign-off."), ("5 to 6", "Peer review of code (REV-07); data model and definitions review."),
       ("7", "Test evidence review (REV-08); acceptance sign-off."), ("8", "Production readiness review (REV-09); the Ops gate; operational readiness sign-off."), ("9 to 10", "Production sign-off; project sign-off; lessons learned.")]

QA = [("Who should review the design?", "Someone who did not build it: a peer architect or Tech Anchor from another project, plus the client's architect and security. For a platform design, ask the platform vendor and the cloud provider too."),
      ("Is a platform vendor review worth it?", "Usually yes for a new platform design, because they know limits and best practice that you may not. Treat it as advice with a commercial interest, record each finding as a decision, and keep your own accountability."),
      ("How many sign-offs are too many?", "Use the seven above for a typical project, and skip any that the risk does not justify. Fewer, with real evidence, beat many with signatures only.")]


def d_ladder():
    b = ""
    for i, (n, who, *_r) in enumerate(REVIEW_TYPES):
        h = 40 + i * 26
        x = 20 + i * 192
        b += R(x, 190 - h + 14, 180, h, [BUTTER, BLUE, MINT, LAV, ROSE][i] if False else [GREY, BLUE, MINT, BUTTER, LAV][i], [n], 15)
    b += DE.AR(40, 28, 960, 28) + T(500, 18, "more independence, more cost, more weight", 14)
    return DE.S(1000, 222, b, "A ladder of five kinds of review, rising from self-check to peer review, internal formal review, client review and sign-off, and external expert review. Independence and weight increase along the ladder.")


def d_method():
    b = ""
    for i, (n, s) in enumerate(METHOD):
        x = 12 + i * 198
        b += R(x, 20, 180, 90, [BLUE, GREY, BUTTER, MINT, LAV][i], [n], 17)
        if i < 4:
            b += DE.AR(x + 182, 65, x + 196, 65)
        b += f'<text x="{x + 90}" y="134" text-anchor="middle" font-size="12">{E(s[:38])}</text>' if False else ""
    return DE.S(1000, 130, b, "A five-step review method: prepare, read alone, meet, decide, follow up.")


def d_vendor():
    b = R(10, 40, 230, 80, BLUE, ["Our design pack", "design, volumes, needs"], 16) + DE.AR(242, 80, 288, 80) + R(290, 40, 230, 80, BUTTER, ["Vendor review", "findings in writing"], 16) + DE.AR(522, 80, 568, 80)
    b += R(570, 40, 230, 80, MINT, ["We decide", "accept, reject, defer"], 16, sw=2.5) + DE.AR(802, 80, 848, 80) + R(850, 40, 140, 80, LAV, ["Decision log", "we stay accountable"], 14)
    b += R(290, 150, 230, 56, "#fff", ["Vendor has a commercial interest"], 13, dash=True) + DE.AR(405, 148, 405, 122)
    d = b
    return DE.S(1000, 222, d, "Platform vendor review: our design pack goes to the vendor, who returns findings in writing; we decide to accept, reject or defer each, and record it in a decision log. We stay accountable. The vendor has a commercial interest.")


def reviews_page():
    url_path = f"{BASE}reviews/"
    types = table(["Kind", "Who", "When", "Purpose", "Independence"], [[f"<b>{E(a)}</b>", E(b), E(c), E(d), E(e)] for a, b, c, d, e in REVIEW_TYPES])
    what = table(["What", "Stage", "Internal reviewers", "External reviewers", "What to check", "Signs off"], [[f"<b>{E(a)}</b>", E(b), E(c), E(d), E(e), E(f)] for a, b, c, d, e, f in WHAT])
    sev = table(["Severity", "Meaning"], [[f"<b>{a}</b>", E(b)] for a, b in SEVERITY])
    meth = "<ol>" + "".join(f"<li><b>{E(a[2:])}.</b> {E(b)}</li>" for a, b in METHOD) + "</ol>"
    va = table(["Area to review", "What it covers", "The question"], [[f"<b>{E(a)}</b>", E(b), E(c)] for a, b, c in VENDOR_AREAS])
    vp = "<ol>" + "".join(f"<li>{E(x)}</li>" for x in VENDOR_PREP) + "</ol>"
    vc = table(["Caution", "Why"], [[f"<b>{E(a)}</b>", E(b)] for a, b in VENDOR_CAUTION])
    so = table(["Sign-off", "Stage", "What is signed", "Who signs", "Evidence", "If conditional"], [[f"<b>{E(a)}</b>", E(b), E(c), E(d), E(e), E(f)] for a, b, c, d, e, f in SIGNOFFS])
    sr = "<ul>" + "".join(f"<li>{E(x)}</li>" for x in SIGN_RULES) + "</ul>"
    wr = table(["What goes wrong", "How it happens", "What it costs", "Prevention"], [[f"<b>{E(a)}</b>", E(b), E(c), E(d)] for a, b, c, d in WRONG])
    cal = table(["Stage", "Reviews and sign-offs"], [[E(a), E(b)] for a, b in CAL])
    toc = "".join(f'<li><a href="#{a}">{b}</a></li>' for a, b in [("what", "What a review is"), ("kinds", "Internal and external"), ("items", "What to review"), ("how", "How to review"), ("vendor", "Platform vendor review"),
                                                                   ("signoffs", "Sign-offs"), ("calendar", "The review calendar"), ("wrong", "What can go wrong"), ("faq", "FAQ")])
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/how-we-work/">How we work</a> › <a href="{BASE}">Data essentials</a> › Reviews and sign-offs</p>
<p class="eyebrow" style="margin-top:22px">Topic 15 · Deep dive</p>
<h1>Reviews and sign-offs, internal and external</h1>
<p class="lede">What to review, who reviews it, how to run a review, what goes wrong, and who signs what. Includes reviews by the platform vendor and the cloud provider for architecture and design.</p>
<div class="tf"><nav class="toc"><b>On this page</b><ol>{toc}</ol></nav>
<section id="what"><p class="eyebrow">Teach first</p><h2>A review is a planned moment to be told you are wrong, cheaply</h2>
<p>A review is when someone who did not build the thing reads it against agreed criteria, with the power to say stop. A sign-off is the decision that follows. The cheapest time to find a flaw is before it is built. A review exists to move that moment earlier.</p>
<div class="box"><b>In one line:</b> reviews find problems, sign-offs take responsibility. Both need evidence, a named person and a date.</div></section>
<section id="kinds"><p class="eyebrow">Who reviews</p><h2>Five kinds, from self-check to external expert</h2>{fig(d_ladder(), "Each step up adds independence and weight, and costs more. Use the lowest step that matches the risk.")}{types}</section>
<section id="items"><p class="eyebrow">What to review</p><h2>Thirteen things worth a review, and who reviews each</h2>{what}</section>
<section id="how"><p class="eyebrow">How to review</p><h2>Five steps, and a way to rate findings</h2>{fig(d_method(), "Prepare, read alone, meet, decide, follow up.")}{meth}<h3 style="margin-top:18px">Rate every finding</h3>{sev}
<p class="note">A review checklist makes this repeatable. The {Lx('/learn/technical-anchor/project-review/checks/', 'project review checks')} are written as checks you can reuse as criteria. {L('/learn/checks-as-code/', 'Checks as code, and the Ops gate')} explains how.</p></section>
<section id="vendor"><p class="eyebrow">External</p><h2>Platform vendor and cloud review of the architecture and design</h2>
<p>Platform vendors and cloud providers often offer a review of how you plan to use their product. It is worth having, if you use it well.</p>
{fig(d_vendor(), "The vendor advises. We decide and stay accountable.")}
<h3>What to ask them to review</h3>{va}<h3 style="margin-top:18px">How to prepare</h3>{vp}<h3 style="margin-top:18px">Cautions</h3>{vc}</section>
<section id="signoffs"><p class="eyebrow">Decisions</p><h2>Seven sign-offs across the project</h2>{so}<h3 style="margin-top:18px">Seven rules for sign-offs</h3>{sr}</section>
<section id="calendar"><p class="eyebrow">When</p><h2>The review calendar</h2>{cal}</section>
<section id="wrong"><p class="eyebrow">What can go wrong</p><h2>Fourteen ways reviews fail</h2>{wr}</section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(QA)}</section>
<section id="next"><p class="eyebrow">Go further</p><h2>Related pages</h2><ul><li>{L(BASE + 'ecosystem/', 'The ecosystem: who does what')}</li><li>{L(BASE + 'ddlc/', 'DDLC by seat')}</li><li>{L(BASE + 'backlog/', 'The corpus backlog: Reviews and sign-offs')}</li>
<li>{Lx('/learn/technical-anchor/discovery/', 'Discovery')}</li><li>{Lx('/learn/technical-anchor/project-review/', 'Project review')}</li><li>{Lx('/learn/responsible-ai/', 'Responsible AI, explained')}</li></ul></section>
</div>"""
    title = "Reviews and sign-offs, internal and external"
    desc = ("What to review in a data project, who reviews it, how to run a review, what goes wrong, and who signs what, including platform vendor and cloud reviews of architecture and design.")
    return url_path, DE.page_shell(title, desc, url_path, body, [("How we work", "/how-we-work/"), ("Data essentials", BASE), ("Reviews and sign-offs", url_path)], QA)


def main():
    for rel, html in [ecosystem_page(), picture_page(), reviews_page()]:
        DE.write(rel, html)


if __name__ == "__main__":
    main()
