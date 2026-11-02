"""Vertical agents: industry agents built on the shared harness, one page per industry.

    python3 _guides/vertical_agents.py && python3 _site/nav.py && python3 _site/seo.py

Writes ai-engineering/vertical-agents/index.html (the hub) and
ai-engineering/vertical-agents/<industry>/index.html. Copies the site's <head>, top bar and
footer from mindset/index.html, like road_safety.py. To add an industry, add it to INDUSTRIES.
To move an agent along, change its status: built, building or planned.

Product names belong to their owners. Naming one means we plan a connector, not a partnership.
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = (ROOT / "mindset" / "index.html").read_text()
BASE = "/ai-engineering/vertical-agents/"
OUT = ROOT / "ai-engineering" / "vertical-agents"
E = html.escape

STATUS = {
    "built": ("Built", "--mint-wash", "Working and tested. Not yet connected to a live customer system."),
    "building": ("Building", "--butter-wash", "Work has started."),
    "planned": ("Planned", "#fff", "Designed at a high level. Nobody has started it yet."),
}

# Each industry: id, name, one-line why, the products we connect to, and the agents.
# Agent: (name, what it does, who it helps, status, note)
INDUSTRIES = [
    {"id": "hotels", "name": "Hotels and hospitality",
     "why": "Guests ask the same questions all day, and every answer lives in the property management system (PMS). An agent can answer them, and it hands anything to do with money or promises to staff.",
     "products": [("Oracle OPERA Cloud", "through the Oracle Hospitality Integration Platform (OHIP)"),
                  ("Apaleo", "open API, cloud PMS"), ("Mews", "open API, cloud PMS")],
     "agents": [
         ("Guest concierge", "Answers hotel questions and cites the source. Asks for late checkout and room preferences, but promises nothing until staff confirm.", "Guests, front desk", "built",
          "Passes all its tests. Connectors for OPERA, Apaleo and Mews are written and tested against simulated systems, not yet against live ones."),
         ("Reservation changes", "Changes dates and room types and adds extras. Quotes the new price from the PMS and waits for the guest to agree.", "Guests, reservations team", "planned", ""),
         ("Housekeeping coordinator", "Turns checkouts, early arrivals and guest requests into a room-cleaning order, and tells the front desk when each room is ready.", "Housekeeping, front desk", "planned", ""),
         ("Review responder", "Drafts replies to online reviews from the stay record. A manager approves every reply before it goes out.", "Guest relations", "planned", ""),
         ("Rate and inventory watcher", "Checks every morning that prices and rooms match across booking channels, and flags any gaps.", "Revenue manager", "planned", ""),
     ]},
    {"id": "insurance", "name": "Insurance",
     "why": "Claims and policy servicing are long chains of forms, documents and status questions. Agents take the paperwork, and people keep the decisions about payouts and cover.",
     "products": [("Guidewire", "ClaimCenter, PolicyCenter, BillingCenter"), ("Duck Creek", "claims, policy and billing"),
                  ("Sapiens", "including the former Majesco suite")],
     "agents": [
         ("Claims intake (first notice of loss)", "Takes the first report of a loss, collects documents, reports claim and policy status, and pays only after a claims handler approves.", "Policyholders, claims desk", "built",
          "Built and deployed once on Azure, on its own sample claims system. Not yet connected to any of the three products."),
         ("Policy servicing", "Handles address changes, adding a driver, and requests for documents. A person approves anything that changes the premium.", "Policyholders, service team", "planned", ""),
         ("Underwriting submission triage", "Reads broker submissions, pulls out the risk details, checks them against appetite rules and fills in the underwriter's file.", "Underwriters, brokers", "planned", ""),
         ("Subrogation finder", "Reads closed claims for signs that another party should pay, and builds the recovery file.", "Recovery team", "planned", ""),
         ("Broker desk", "Answers brokers' questions about a quote, policy or claim from the system record.", "Brokers", "planned", ""),
     ]},
    {"id": "pharma", "name": "Pharma and life sciences",
     "why": "Clinical and safety work is full of careful checking that must leave a trail for inspectors. Agents do the first pass and record every step, and qualified people sign off.",
     "products": [("Veeva Vault", "Clinical, Safety, QualityDocs, RIM"), ("Medidata Rave", "electronic data capture (EDC) for trials"),
                  ("Oracle Argus Safety", "drug safety case management")],
     "agents": [
         ("Clinical data review", "Checks trial data for missing, odd or inconsistent values, and drafts queries for site staff. A data manager approves each query.", "Clinical data managers", "built",
          "Version 1 is built on sample study data. Connectors to the three products are not built yet."),
         ("Adverse event intake", "Reads emails, call notes and forms for possible side effects and drafts a safety case with the four minimum facts. A safety reviewer confirms it.", "Pharmacovigilance team", "planned", ""),
         ("Regulatory document checker", "Checks submission documents against the template, cross-references and version rules before they are filed.", "Regulatory affairs", "planned", ""),
         ("Medical information answers", "Answers doctors' and pharmacists' questions from approved documents only, and cites the source.", "Medical information team", "planned", ""),
         ("Deviation and CAPA drafter", "Turns a quality deviation into a draft investigation and corrective action plan, linked to similar past cases.", "Quality assurance", "planned", ""),
     ]},
    {"id": "banking", "name": "Banking",
     "why": "Banks run on core systems that hold every account and payment. Agents take routine casework, and fixed rules and people guard every movement of money.",
     "products": [("Temenos", "Transact and Infinity"), ("Infosys Finacle", "core banking"), ("FIS", "core and card platforms")],
     "agents": [
         ("Card dispute handler", "Collects the facts of a disputed payment, checks the scheme rules and builds the chargeback file for an officer.", "Customers, disputes team", "planned", ""),
         ("KYC refresh", "Chases customers for out-of-date identity documents, checks what comes back and flags anything that needs a person.", "Compliance operations", "planned", ""),
         ("Loan document checker", "Checks a loan file is complete and consistent before it reaches credit.", "Loan operations", "planned", ""),
         ("Collections assistant", "Offers payment plans within set limits, records promises to pay, and hands hardship cases to a person.", "Collections team", "planned", ""),
     ]},
    {"id": "retail", "name": "Retail and e-commerce",
     "why": "Shops get the same order, return and stock questions at scale. This is where our reference support agent was born, so it is the shortest path to a working agent.",
     "products": [("Shopify", "store and orders API"), ("Salesforce Commerce Cloud", "orders and service"), ("SAP Commerce Cloud", "orders and catalog")],
     "agents": [
         ("Customer support", "Order status, cancellations, and returns and refunds behind human approval.", "Shoppers, support team", "built",
          "The open reference agent, running on a simulated shop. Store connectors are not built yet."),
         ("Returns triage", "Reads the return reason and photos, applies the returns policy and routes the item to restock, repair or write off.", "Warehouse, support team", "planned", ""),
         ("Catalog enricher", "Fills in missing product attributes and descriptions from supplier sheets. A merchandiser approves them in batches.", "Merchandising", "planned", ""),
         ("Stock-out watcher", "Spots products about to sell out and drafts reorder suggestions for the buyer.", "Buyers", "planned", ""),
     ]},
    {"id": "healthcare", "name": "Hospitals and clinics",
     "why": "Front-office and admin work takes clinicians' time. Agents can book, chase and draft, but they never make clinical decisions.",
     "products": [("Epic", "electronic health record"), ("Oracle Health", "formerly Cerner"), ("athenahealth", "athenaOne")],
     "agents": [
         ("Appointment scheduler", "Books, moves and reminds, following each clinic's rules, in the patient's language.", "Patients, front office", "planned", ""),
         ("Prior authorization", "Gathers the clinical notes an insurer needs and drafts the request for staff to send.", "Billing and admin staff", "planned", ""),
         ("Discharge summary drafter", "Drafts the discharge summary from the record. The doctor edits and signs it.", "Doctors", "planned", ""),
     ]},
    {"id": "manufacturing", "name": "Manufacturing",
     "why": "Plants lose hours waiting for parts, answers and paperwork. Agents read the ERP and shop-floor systems, chase people and draft documents. Machines stay under human control.",
     "products": [("SAP S/4HANA", "ERP, maintenance and quality"), ("Siemens Opcenter", "manufacturing execution"), ("Microsoft Dynamics 365", "supply chain and ERP")],
     "agents": [
         ("Maintenance troubleshooter", "Helps a technician find the cause of a fault from manuals and past work orders, then drafts the work order.", "Maintenance technicians", "planned", ""),
         ("Supplier delay chaser", "Watches open purchase orders, chases suppliers who are late and warns planners early.", "Planners, buyers", "planned", ""),
         ("Quality issue drafter", "Turns an inspection failure into a draft non-conformance report with likely causes.", "Quality engineers", "planned", ""),
     ]},
    {"id": "logistics", "name": "Logistics and freight",
     "why": "Every shipment produces exceptions: delays, damage, missing paperwork. Agents spot them early and handle the routine ones.",
     "products": [("SAP Transportation Management", "planning and freight"), ("Oracle Transportation Management", "planning and freight"), ("Blue Yonder", "warehouse and transport")],
     "agents": [
         ("Shipment exception handler", "Spots late or stuck shipments, tells the customer, and proposes a fix for the planner to approve.", "Planners, customers", "planned", ""),
         ("Proof-of-delivery checker", "Reads delivery documents and photos, matches them to the order and flags gaps before invoicing.", "Billing team", "planned", ""),
         ("Carrier booking assistant", "Gets quotes from approved carriers and books within the set limits.", "Transport desk", "planned", ""),
     ]},
    {"id": "telecom", "name": "Telecom",
     "why": "Billing questions, plan changes and outages fill telecom call centres. Agents answer from the billing and network records.",
     "products": [("Amdocs", "billing and customer management"), ("Salesforce Communications Cloud", "customer service"), ("ServiceNow", "telecom service management")],
     "agents": [
         ("Bill explainer and disputes", "Explains each line of a bill and raises a dispute within set credit limits.", "Customers, care team", "planned", ""),
         ("Plan change advisor", "Suggests a better plan from actual usage and switches it after the customer agrees.", "Customers", "planned", ""),
         ("Outage notifier", "Tells affected customers about an outage and keeps them updated until it is fixed.", "Customers, network operations", "planned", ""),
     ]},
    {"id": "property", "name": "Property management",
     "why": "Landlords and property managers handle repairs, renewals and rent questions all year. Agents keep tenants informed and work moving.",
     "products": [("Yardi", "Voyager and Breeze"), ("AppFolio", "property manager"), ("MRI Software", "residential and commercial")],
     "agents": [
         ("Maintenance request intake", "Takes repair requests with photos, sorts them by urgency and books an approved contractor.", "Tenants, property managers", "planned", ""),
         ("Lease renewal assistant", "Reminds tenants before the lease ends, offers terms within set limits and prepares the paperwork.", "Leasing team", "planned", ""),
         ("Rent arrears follow-up", "Sends polite reminders, offers payment plans within rules and hands hard cases to a person.", "Property managers", "planned", ""),
     ]},
]

CSS = """
  .va-stat { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:14px; margin:26px 0; }
  .va-stat div { border:var(--line); border-radius:var(--wob); padding:14px 18px; background:var(--peri-wash); font-size:15px; }
  .va-stat b { display:block; font-family:var(--hand); font-size:32px; font-weight:400; line-height:1.1; }
  .va-note { background:var(--butter-wash); border:var(--line); border-radius:var(--wob); padding:16px 22px; margin:22px 0; }
  .va-note p { margin:6px 0; }
  .va-fig { border:var(--line); border-radius:var(--wob); padding:18px; margin:18px 0; background:#fff; }
  .va-fig svg { width:100%; height:auto; display:block; }
  .va-fig figcaption { font-size:14px; color:var(--muted); margin-top:8px; }
  .va-cards { display:grid; grid-template-columns:repeat(auto-fit,minmax(270px,1fr)); gap:16px; margin-top:16px; }
  .va-card { border:var(--line); border-radius:var(--wob); padding:16px 20px; background:#fff; display:block; color:inherit; text-decoration:none; }
  .va-card:hover { background:var(--peri-wash); }
  .va-card h3 { font-size:24px; margin:0 0 6px; line-height:1.15; }
  .va-card p { margin:6px 0; font-size:15px; }
  .va-card .lbl { display:block; font-size:11.5px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; color:var(--faint); }
  .va-badge { display:inline-block; font-size:12.5px; font-weight:700; padding:1px 10px; border:1.5px solid var(--ink); border-radius:999px; margin-right:4px; }
  .va-table { overflow-x:auto; margin:10px 0 0; }
  .va-table table { border-collapse:collapse; width:100%; font-size:15px; }
  .va-table th, .va-table td { border-bottom:1px solid var(--rule-firm); padding:9px 10px; text-align:left; vertical-align:top; }
  .va-table th { background:var(--surface-2); font-weight:700; }
  .va-table td small { display:block; color:var(--muted); margin-top:4px; }
  .va-prod { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:12px; margin:14px 0; }
  .va-prod div { border:var(--line); border-radius:var(--wob); padding:12px 16px; background:var(--peri-wash); font-size:14px; }
  .va-prod b { display:block; font-family:var(--hand); font-size:22px; font-weight:400; }
  .va-fine { font-size:14px; color:var(--muted); }
"""


def badge(s):
    name, wash, _ = STATUS[s]
    return f'<span class="va-badge" style="background:var({wash})">{name}</span>' if wash.startswith("--") else f'<span class="va-badge">{name}</span>'


def fig(ind=None):
    """One shared harness in the middle; product connectors on the right, agents on the left."""
    if ind:
        left = [a[0] for a in ind["agents"]][:5]
        right = [p[0] for p in ind["products"]]
        title_l, title_r = "Agents", "Connectors"
        caption = (f"Every {ind['name'].lower()} agent uses the same harness. Switching from one product to another "
                   "means swapping a connector. The agent and its tests stay the same.")
    else:
        left = ["Hotels", "Insurance", "Pharma", "Banking", "Retail"]
        right = ["OPERA · Apaleo · Mews", "Guidewire · Duck Creek · Sapiens", "Veeva · Medidata · Argus", "Temenos · Finacle · FIS", "Shopify · SFCC · SAP"]
        title_l, title_r = "Industry agents", "Product connectors"
        caption = ("Industry agents sit on one shared harness, with its checks, approvals, tests and cost tracking. "
                   "Each product is a small connector, so one agent works with any of its industry's three products.")
    n = len(left)
    h = 70 + n * 52
    ys = [60 + i * 52 for i in range(n)]
    ry = [60 + i * (52 * (n - 1) / max(len(right) - 1, 1)) for i in range(len(right))]
    mid = h / 2
    g = [f'<svg viewBox="0 0 900 {h}" role="img" aria-label="{E(caption)}">',
         '<g font-family="Patrick Hand, cursive" font-size="20" fill="#1F1F1F" text-anchor="middle">',
         f'<text x="130" y="30">{title_l}</text><text x="770" y="30">{title_r}</text></g>',
         '<g fill="none" stroke="#1F1F1F" stroke-width="1.4">']
    for y in ys:
        g.append(f'<path d="M240 {y + 18} C 290 {y + 18}, 290 {mid}, 340 {mid}"/>')
    for y in ry:
        g.append(f'<path d="M560 {mid} C 610 {mid}, 610 {y + 18}, 660 {y + 18}"/>')
    g.append('</g><g stroke="#1F1F1F" stroke-width="1.5">')
    for y in ys:
        g.append(f'<rect x="20" y="{y}" width="220" height="36" rx="12" fill="#F1F4FB"/>')
    for y in ry:
        g.append(f'<rect x="660" y="{y}" width="220" height="36" rx="12" fill="#FFF8E8"/>')
    g.append(f'<path d="M346 {mid - 70} Q342 {mid - 78} 354 {mid - 78} L548 {mid - 80} Q560 {mid - 78} 558 {mid - 66} '
             f'L560 {mid + 66} Q558 {mid + 78} 546 {mid + 78} L352 {mid + 80} Q340 {mid + 78} 342 {mid + 66} Z" fill="#F0F8F3"/></g>')
    g.append('<g font-family="DM Sans, sans-serif" font-size="14" fill="#1F1F1F" text-anchor="middle">')
    for y, t in zip(ys, left):
        g.append(f'<text x="130" y="{y + 23}">{E(t)}</text>')
    for y, t in zip(ry, right):
        g.append(f'<text x="770" y="{y + 23}">{E(t)}</text>')
    g.append(f'<text x="450" y="{mid - 34}" font-family="Patrick Hand, cursive" font-size="24">Shared harness</text>')
    for i, t in enumerate(["checks and guardrails", "human approvals", "tests in a simulated world", "cost per conversation"]):
        g.append(f'<text x="450" y="{mid - 6 + i * 20}">{t}</text>')
    g.append('</g></svg>')
    return f'<figure class="va-fig">{"".join(g)}<figcaption>{E(caption)}</figcaption></figure>'


def counts(agents):
    c = {k: sum(1 for a in agents if a[3] == k) for k in STATUS}
    return " ".join(f"{badge(k)}{c[k]}" for k in STATUS if c[k])


def join_section(subject, who):
    return f"""<section><p class="eyebrow">Join</p><h2>Work with us on these</h2>
<p><b>{who}</b> If you use one of these products and one of these jobs costs you time, we would like to build and test the agent with you. Tell us your product and the job, and we will show you the agent running in a simulated copy of your setup first.</p>
<p><b>Engineers:</b> every agent here needs builders. Pick one and write to us.</p>
<p>Write to <a href="mailto:basant@cleandataengineering.ai?subject={subject}">basant@cleandataengineering.ai</a>.</p>
<p class="va-fine">Product names belong to their owners. Listing a product means we plan to build a connector to it. It does not mean we are partners with, or endorsed by, its maker.</p></section>"""


HOW = """<section><p class="eyebrow">How we build them</p><h2>Same harness, different industry</h2>
<ol>
<li><b>Code first, model second.</b> If a rule can decide something, such as a refund limit or a lab value outside its allowed range, code decides it. The model handles the language.</li>
<li><b>People approve anything risky.</b> Money, promises to customers and clinical or legal decisions always wait for a named person.</li>
<li><b>Each product is a connector.</b> The agent talks to one interface. OPERA, Apaleo and Mews are three plug-ins behind it, so moving to another product means swapping the plug-in, not rebuilding the agent.</li>
<li><b>Tested in a simulated world first.</b> Every agent passes a simulated week, with difficult customers, slow systems and failures, before it meets a real one. See <a href="/learn/agenttwin/">AgentTwin</a>.</li>
<li><b>Checks you can see.</b> Every guardrail comes from the <a href="/learn/agent-guardrails/">guardrail catalog</a>, and every agent's cost per conversation is measured.</li>
</ol></section>"""


def hub():
    all_agents = [a for i in INDUSTRIES for a in i["agents"]]
    built = sum(1 for a in all_agents if a[3] == "built")
    cards = []
    for i in INDUSTRIES:
        prods = " · ".join(p[0] for p in i["products"])
        cards.append(f'<a class="va-card" href="{BASE}{i["id"]}/"><h3>{E(i["name"])}</h3>'
                     f'<p><span class="lbl">Products</span>{E(prods)}</p>'
                     f'<p><span class="lbl">Agents</span>{counts(i["agents"])}</p>'
                     f'<p>{E(i["why"].split(". ")[0])}.</p></a>')
    legend = "".join(f"<li>{badge(k)} {E(v[2])}</li>" for k, v in STATUS.items())
    title = "Vertical agents, by industry"
    desc = (f"Agents for {len(INDUSTRIES)} industries, built on one shared harness, each with connectors to the "
            "three main products in its industry: hotels, insurance, pharma, banking, retail and more.")
    body = f"""<main class="wrap">
<div class="hero"><p class="eyebrow">AI Engineering · vertical agents</p><h1>{title}</h1>
<p class="thesis">A <em>vertical agent</em> does one real job in one industry, like checking in a hotel guest or taking a car insurance claim. It works inside the software that industry already runs on. For each industry we pick the three products most businesses use and build agents that connect to all three.</p></div>

<div class="va-stat">
<div><b>{len(INDUSTRIES)}</b>industries</div>
<div><b>{len(all_agents)}</b>agents listed</div>
<div><b>{built}</b>built and tested</div>
<div><b>3</b>products per industry</div>
</div>

<div class="va-note"><p><b>Most of this list is still a plan.</b> {built} agents are built and tested. The rest are planned, and we will build them one industry at a time. Each page says exactly where every agent stands.</p></div>

<section><p class="eyebrow">The idea</p><h2>One harness, many industries</h2>
<p>The hard parts of an agent are the same in every industry: checks before each action, a person approving anything risky, tests, and knowing the cost. We build those once. An industry agent then adds what is specific to its industry: the job itself, its rules, and a connector for each product.</p>
{fig()}</section>

<section><p class="eyebrow">Industries</p><h2>Pick an industry</h2>
<div class="va-cards">
{chr(10).join(cards)}
</div>
<ul class="va-fine" style="list-style:none;padding:0;margin-top:18px">{legend}</ul></section>

{HOW}
{join_section("Vertical%20agents", "Businesses:")}
</main>
"""
    return title, desc, body


def industry_page(i):
    rows = []
    for name, does, who, st, note in i["agents"]:
        rows.append(f"<tr><td><b>{E(name)}</b></td><td>{E(does)}{f'<small>{E(note)}</small>' if note else ''}</td>"
                    f"<td>{E(who)}</td><td>{badge(st)}</td></tr>")
    prods = "".join(f"<div><b>{E(p)}</b>{E(d)}</div>" for p, d in i["products"])
    title = f"Vertical agents for {i['name'].lower()}"
    desc = (f"{len(i['agents'])} agents for {i['name'].lower()}, each connecting to "
            f"{', '.join(p[0] for p in i['products'][:-1])} and {i['products'][-1][0]}.")
    others = " · ".join(f'<a href="{BASE}{o["id"]}/">{E(o["name"])}</a>' for o in INDUSTRIES if o["id"] != i["id"])
    body = f"""<main class="wrap">
<div class="hero"><p class="eyebrow"><a href="{BASE}">Vertical agents</a> · {E(i['name'])}</p><h1>{E(title[0].upper() + title[1:])}</h1>
<p class="thesis">{E(i['why'])}</p></div>

<section><p class="eyebrow">Products we connect to</p><h2>The three products</h2>
<p>Most businesses in this industry run on one of these. Each agent below gets a connector for all three.</p>
<div class="va-prod">{prods}</div></section>

<section><p class="eyebrow">The agents</p><h2>What each agent does</h2>
<div class="va-table"><table>
<tr><th>Agent</th><th>What it does</th><th>Who it helps</th><th>Status</th></tr>
{chr(10).join(rows)}
</table></div></section>

<section><p class="eyebrow">How it fits</p><h2>One harness under all of them</h2>
{fig(i)}</section>

{HOW}
{join_section(E(i['name']).replace(' ', '%20') + "%20agents", f"Businesses in {E(i['name'].lower())}:")}
<section><p class="eyebrow">More industries</p><p>{others}</p></section>
</main>
"""
    return title, desc, body


def write(path, url, title, desc, body):
    head_end = SRC.index("</style>")
    head = SRC[:head_end] + CSS + SRC[head_end:SRC.index("<main")]
    head = re.sub(r"<title>.*?</title>", f"<title>{E(title)} · Clean Data Engineering</title>", head, count=1)
    for pat in (r'(<meta name="description" content=")[^"]*', r'(<meta property="og:description" content=")[^"]*'):
        head = re.sub(pat, lambda m: m.group(1) + E(desc), head, count=1)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + E(title), head, count=1)
    head = head.replace("https://cleandataengineering.ai/mindset/", url)
    foot = SRC[SRC.index("<footer>"):]
    path.mkdir(parents=True, exist_ok=True)
    (path / "index.html").write_text(head + body + foot)
    print("wrote", (path / "index.html").relative_to(ROOT))


def main():
    write(OUT, f"https://cleandataengineering.ai{BASE}", *hub())
    for i in INDUSTRIES:
        write(OUT / i["id"], f"https://cleandataengineering.ai{BASE}{i['id']}/", *industry_page(i))


if __name__ == "__main__":
    main()
