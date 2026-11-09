"""Cost & FinOps (concern X10) and the Databricks data platform cost calculator.

    python3 _guides/dbx_cost.py            (then python3 _site/seo.py)

  /learn/data-systems/platform/cost/              the concern page (end to end and per hop)
  /learn/data-systems/platform/cost/calculator/   the interactive calculator (AWS first)

The calculator's model lives in _tools/dbx_cost/calculator.js and its prices in
_tools/dbx_cost/prices.json; both are copied next to the page. Refresh prices with
_tools/dbx_cost/refresh_prices.py (a monthly GitHub Action opens a pull request with the changes).
"""
import importlib.util
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("data_platform", ROOT / "_guides" / "data_platform.py")
dp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dp)
ds, E, wb, SITE, BASE, P = dp.ds, dp.E, dp.wb, dp.SITE, dp.BASE, dp.P
FILL, box, arrow, text, svg = dp.FILL, dp.box, dp.arrow, dp.text, dp.svg
TOOLS = ROOT / "_tools" / "dbx_cost"
PRICES = json.loads((TOOLS / "prices.json").read_text())
C = f"{P}cost/"
CALC = f"{C}calculator/"


# ---------------------------------------------------------------------------------------------
# The concern page
# ---------------------------------------------------------------------------------------------

def bill_picture():
    b = ""
    parts = [("Databricks", "DBUs: jobs, pipelines,\nwarehouses, notebooks", "rose"), ("AWS underneath", "EC2 (classic only),\nS3, network", "butter"),
             ("Hidden", "never stops, retries,\ndev/test, maintenance", "lilac")]
    x = 30
    for t, s, f in parts:
        b += box(x, 20, 250, 90, t, s, f)
        x += 290
    b += text(155, 135, "serverless folds the machines into the DBU price", 13) + text(445, 135, "storage and network are billed by AWS", 13) + text(735, 135, "often a third of the bill", 13)
    b += f'<rect x="30" y="160" width="830" height="44" rx="12" fill="{FILL["mint"]}" stroke="#1F1F1F" stroke-width="1.3" stroke-dasharray="6 5"/>'
    b += text(445, 187, "end to end: one budget per data product · per hop: a few drivers each · tags make both visible", 15, fill="#1F1F1F")
    return svg(890, 215, b, "A Databricks bill has three parts: Databricks DBUs, the AWS resources underneath, and hidden costs. End to end there is a budget per data product; per hop there are a few drivers."), \
        "The three parts of the bill, and the two ways to look at it."


VIEWS = [
    ("End to end", "What does this data product cost, all in, and is it worth it?", "The data product owner", "Usage tagged by product, summed across every hop, plus its share of shared costs"),
    ("Per hop", "Which layer is expensive, and why?", "The platform team", "Usage tagged by hop (job, pipeline or warehouse), with the hop's drivers next to it"),
    ("Per team", "Who spends on notebooks, monitoring and ad-hoc queries?", "Team leads", "Usage of notebooks and warehouses tagged by team"),
]

DRIVERS = [
    ("H1 · Sources to bronze", "Data volume and file format; connectors and CDC; runs per day; landing and bronze retention", "Incremental ingestion (Auto Loader); keep landing short; bronze history only as long as you need to replay"),
    ("H2 · Bronze to silver", "Merges on big tables: how many files each merge rewrites; history-keeping (SCD2); runs per day", "Liquid clustering and deletion vectors; fewer, larger runs; history only where it matters"),
    ("H3 · Silver to gold", "Full rebuilds versus incremental refresh; number of materialized views", "Incremental materialized views; drop gold tables nobody reads"),
    ("H4 · Gold to semantic", "Whether dashboards scan big fact tables or small aggregates", "Pre-computed aggregates behind metric views"),
    ("H5 · Semantic to experiences", "Warehouse size and hours on; refresh schedules; number of users; Genie and agents", "Serverless warehouses with short auto-stop; refresh schedules that match reading habits"),
    ("Streaming lane", "Always-on pipelines; how many tables share a pipeline", "Trigger every few minutes where seconds aren't needed; pack tables into fewer pipelines"),
]

HIDDEN = [
    ("A warehouse that never stops", "Each refresh is cheap; together they keep it on all night", "Warehouse hours outside business hours, in system.billing.usage", "Business-hours schedules; short auto-stop"),
    ("Dev and test", "It is 'not production', so nobody watches it", "Usage tagged by environment", "Smaller compute, auto-stop, sampled data"),
    ("Failed runs and retries", "The job finally succeeded, so nobody looks back", "Run history: compute spent on failed attempts", "Fix the top failing jobs; cap retries"),
    ("Table maintenance", "OPTIMIZE and VACUUM run in the background", "Predictive optimization and maintenance jobs in billing", "Let predictive optimization decide; skip tables nobody reads"),
    ("Old file versions", "Every merge leaves old files until VACUUM", "Storage growing faster than the data", "Short time-travel retention where replay isn't needed"),
    ("Monitoring by teams", "Each team builds its own cost and health dashboards", "Small warehouses running all night", "One shared monitoring warehouse; hourly refresh in business hours"),
    ("Idle notebooks", "Engineers stop typing; clusters keep billing", "All-purpose clusters idle before auto-termination", "Serverless notebooks, or short auto-termination by policy"),
    ("Cluster start-up and NAT", "Classic compute pays EC2 while starting; S3 traffic without a gateway endpoint pays NAT per GB", "EC2 and NAT lines on the AWS bill", "Serverless, or an S3 gateway endpoint and pools"),
    ("Backfills", "Planned as a one-off, repeated twice a year", "Usage spikes after releases", "Plan backfills as jobs with a cost estimate"),
]

C_LEADERS = [
    "A Databricks bill has three parts: Databricks DBUs, the AWS resources underneath (machines for classic compute, storage, network), and hidden costs nobody planned.",
    "Look at it two ways. End to end: one budget per data product, so value and cost sit side by side. Per hop: a few cost drivers per layer, so the platform team knows where to act.",
    "Hidden costs are often a third of the bill: warehouses that never stop, dev and test, retries, maintenance, monitoring dashboards, idle notebooks and file history.",
    "Streaming and real-time serving are always-on costs. Choose them per table, for a decision that needs seconds or minutes.",
    "Estimate before building with the calculator; once running, measure with Databricks' own billing tables and tags.",
]

C_QUESTIONS = [
    ("A", "Ownership and budgets", "who pays, and against what", [
        ("Does every data product have a named owner and a monthly budget?",
         "Cost without an owner only grows.",
         "The bill triples in a quarter and every team says it's someone else's.",
         "A budget per data product, with alerts at 80% and 100%. Not: one platform budget nobody owns."),
        ("Is every job, pipeline and warehouse tagged with product, hop, team and environment?",
         "Without tags, the bill can't be split end to end or per hop.",
         "Half the bill shows up as 'untagged' and can't be explained.",
         "Compute policies that require the tags; reject untagged compute. Not: tagging by convention."),
        ("Do we show costs to teams first, and charge them later?",
         "Charging before people trust the numbers starts arguments, not savings.",
         "Teams dispute the chargeback instead of fixing the cost.",
         "Show back for a quarter, then charge back. Not: charging on day one."),
    ]),
    ("B", "Per hop", "where each layer's money goes", [
        ("Which tables cost the most to merge, and how is their file layout?",
         "Merges on big, badly laid-out tables are usually the largest pipeline cost.",
         "One 50 TB table rewrites a fifth of its files every run and nobody knows.",
         "Cost per table from billing and job metrics; liquid clustering on the top ten. Not: tuning small tables first."),
        ("Which gold tables rebuild fully, and does anyone read them?",
         "Full rebuilds re-read all of silver, every run.",
         "Gold refresh costs more than everything upstream, for tables last queried months ago.",
         "Incremental refresh; retire unread tables using lineage and query history. Not: keeping every table forever."),
        ("How long are warehouses on, and how many hours is anyone actually querying?",
         "Warehouses are billed per hour on, not per query.",
         "A warehouse runs 730 hours a month for 200 hours of queries.",
         "Compare uptime with query hours; fix the schedules keeping it awake. Not: sizing up when it feels slow."),
    ]),
    ("C", "Hidden costs", "the costs no plan includes", [
        ("What do dev and test cost compared with production?",
         "Lower environments are rarely watched.",
         "Test costs as much as production because a full-size job runs on a schedule there.",
         "Tag by environment and set a target share (20-40%). Not: assuming non-prod is small."),
        ("What runs at night and at weekends, and why?",
         "Off-hours usage is usually refreshes, monitoring and forgotten jobs.",
         "Monitoring dashboards keep a warehouse awake every night.",
         "A weekly look at off-hours usage. Not: discovering it in the annual review."),
        ("How much compute goes on failed runs and retries?",
         "A job that succeeds on the third try costs three times.",
         "A flaky job doubles its cost for months.",
         "Track compute on failed attempts; fix the top offenders. Not: unlimited retries."),
    ]),
    ("D", "Streaming and real time", "always-on, on purpose", [
        ("Which tables need seconds, which need minutes, and which are fine daily?",
         "Always-on compute costs the same whether anyone looks or not.",
         "Twenty tables stream continuously for a dashboard read once a morning.",
         "Decide speed per table with its user; trigger every few minutes where seconds aren't needed. Not: streaming by default."),
        ("What answers real-time questions at night: a warehouse, a database, or an API?",
         "Real-time serving means something is always on.",
         "A large warehouse kept up 24x7 to answer a handful of API calls.",
         "Size the always-on part for the night-time load, and serve point lookups from a database or cache. Not: the daytime warehouse left on."),
    ]),
    ("E", "Measuring", "from estimate to evidence", [
        ("Do we read cost from Databricks' billing tables, joined with list prices and tags?",
         "Estimates are for planning; the billing tables are the truth.",
         "The estimate becomes the budget and nobody checks it against reality.",
         "A cost dashboard on system.billing.usage and system.billing.list_prices, per product and per hop. Not: the monthly invoice alone."),
        ("Do we compare the estimate with the real bill after the first month?",
         "The calculator's work rates are calibrated defaults, not your data.",
         "A design decision rests on a number that was off by 3x.",
         "Replace the calculator's work rates with measured ones and re-run the estimate. Not: trusting any calculator, ours included."),
    ]),
]

C_DECISIONS = [
    ("Serverless or classic compute for pipelines?", [
        ("Serverless by default", "pursue", "Pursue. No idle clusters, start-up time, NAT or tuning; costs follow the work."),
        ("Classic with spot workers for long, steady, large jobs", "when", "Pursue only where the calculator and billing show a clear saving and the team can tune clusters."),
        ("Classic everywhere because the DBU price is lower", "drop", "Drop. The EC2, start-up, idle and network costs come on top."),
    ]),
    ("How are costs split?", [
        ("Tags required by compute policy; show back, then charge back", "pursue", "Pursue. Both views (end to end and per hop) come from the same tags."),
        ("Split the bill by headcount", "drop", "Drop. It hides who drives the cost."),
    ]),
    ("How do streaming tables run?", [
        ("Triggered every few minutes, many tables per pipeline", "pursue", "Pursue for most 'near real time' needs."),
        ("Continuous", "when", "Pursue only where a decision needs seconds (fraud, stock, operations)."),
    ]),
    ("How are dashboards refreshed?", [
        ("On a schedule that matches when people read them", "pursue", "Pursue. Business hours, and hourly at most for most dashboards."),
        ("Every 15 minutes, around the clock", "drop", "Drop unless someone reads it at night. The warehouse never stops."),
    ]),
]

C_FAQ = [
    ("What makes up the cost of a Databricks data platform?",
     "Three parts: Databricks DBUs (for jobs, pipelines, SQL warehouses and notebooks), the cloud resources underneath (machines for classic compute, storage, network), and hidden costs such as warehouses that never stop, dev and test, retries, maintenance and monitoring."),
    ("Is serverless more expensive than classic compute on Databricks?",
     "The price per DBU is higher, but it includes the machines, and you don't pay for start-up, idle clusters or NAT. For bursty and scheduled work serverless is often cheaper overall; for long, steady jobs on spot machines classic can be cheaper. The calculator shows both for your settings."),
    ("Should Databricks cost be tracked per layer or end to end?",
     "Both. End to end per data product, so cost sits next to value; per hop, so the platform team knows which layer to fix. Both views come from the same tags on jobs, pipelines and warehouses."),
    ("What are the hidden costs of a Databricks platform?",
     "Warehouses kept awake by scheduled refreshes, dev and test environments, failed runs and retries, table maintenance, old file versions in storage, teams' monitoring dashboards, idle notebook clusters, and on classic compute, cluster start-up time and NAT gateway traffic."),
]


def cost_page():
    b_svg, b_cap = bill_picture()
    sections = [
        ("plain", "In plain words", f"""<p class="eyebrow">In plain words</p><h2>Like the electricity bill for a house</h2>
<p>A house's electricity bill has the appliances you use, the standing charge you pay anyway, and the things nobody notices: the TV on standby, the heater left on in an empty room. You can read it two ways. For the whole house, "is this worth it?". Room by room, "what's using so much?". A separate meter per room makes both possible.</p>
<p>A data platform's bill is the same. The appliances are the hops: ingestion, merges, gold refreshes, warehouses. The standing charges are storage and always-on services. The standby lights are the hidden costs. Tags are the meters.</p>
<figure class="diagram">{b_svg}<figcaption>{E(b_cap)}</figcaption></figure>
<p style="margin-top:14px"><a class="btn" href="{CALC}">Open the Databricks cost calculator</a></p>"""),
        ("views", "End to end and per hop", f"""<p class="eyebrow">Two views</p><h2>End to end, per hop, and per team</h2>
{dp.table(["View", "The question it answers", "Who owns it", "How it is measured"], VIEWS)}"""),
        ("drivers", "What drives each hop", f"""<p class="eyebrow">Per hop</p><h2>What drives the cost at each hop</h2>
{dp.table(["Hop", "What drives the cost", "The main lever"], DRIVERS)}"""),
        ("hidden", "Hidden costs", f"""<p class="eyebrow">Hidden costs</p><h2>The costs no plan includes</h2>
{dp.table(["Cost", "Why it hides", "How to see it", "Fix"], HIDDEN)}"""),
        ("measure", "Measuring it", f"""<p class="eyebrow">Evidence</p><h2>From estimate to evidence</h2>
<p>Estimate first with the <a href="{CALC}">calculator</a>. Once the platform runs, the truth is in Databricks' own billing tables: <code>system.billing.usage</code> (what ran, how many DBUs, with its tags) and <code>system.billing.list_prices</code> (the price of each product). Join them, group by the product, hop, team and environment tags, and you have both views. Add the AWS bill for EC2, S3 and network, split by the same tags.</p>"""),
    ]
    nxt = f"""<p><b>Try it:</b> <a href="{CALC}">the Databricks data platform cost calculator</a>, per hop and end to end, with streaming and hidden costs.</p>
<p><b>Read more:</b> <a href="/writing/databricks-cost-leaks/">Your Databricks bill has a leak</a> and <a href="/writing/cluster-never-scales-down/">Your cluster scales up and never comes back down</a> (blog).</p>"""
    return dp.concern_page("cost", "X10", "Cost & FinOps: end to end and per hop",
                           "Every dollar has an owner and a budget, end to end and per hop, and the hidden costs are counted before they surprise anyone.",
                           "What a data platform costs, how to read the bill end to end and per hop, the drivers at each layer, the hidden costs, and how streaming and real-time serving change the picture.",
                           C_LEADERS, sections, C_QUESTIONS, C_DECISIONS, C_FAQ, nxt,
                           "Data platform cost and FinOps: the three parts of a Databricks bill, end-to-end and per-hop views, cost drivers per layer, hidden costs, streaming and real-time, and measuring with billing tables.",
                           kind="both")


# ---------------------------------------------------------------------------------------------
# The calculator page
# ---------------------------------------------------------------------------------------------

CALC_CSS = """<style>
  .calc { display:grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.1fr); gap:18px; align-items:start; margin:18px 0; }
  @media (max-width:980px) { .calc { grid-template-columns:1fr; } }
  .panel { border:var(--line); border-radius:var(--wob); padding:14px 18px; background:#fff; }
  .panel h2 { margin:0 0 8px; font-size:26px; }
  .result { position:sticky; top:12px; background:var(--butter-wash); }
  .total { font-family:var(--hand); font-size:46px; line-height:1.1; margin:2px 0; }
  .sub { color:var(--ink-soft); margin:0; } .facts { font-size:13.5px; color:var(--muted); margin:6px 0 10px; }
  .bar { display:flex; height:30px; border:1.5px solid var(--ink); border-radius:10px; overflow:hidden; margin:10px 0; }
  .bar .seg { display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700; border-right:1px solid rgba(0,0,0,.25); }
  .hopcards { display:grid; grid-template-columns:repeat(auto-fill, minmax(118px, 1fr)); gap:8px; }
  .hc { border:1.5px solid var(--ink); border-radius:10px; padding:6px 9px; font-size:12.5px; display:flex; flex-direction:column; }
  .hc b { font-size:18px; } .hc .hid { font-size:11px; font-weight:700; color:var(--muted); } .hc .pct { color:var(--muted); }
  .prms { display:grid; grid-template-columns:repeat(auto-fill, minmax(260px, 1fr)); gap:10px 18px; }
  .prm label { display:block; font-weight:600; font-size:14.5px; margin-bottom:3px; }
  .prm select, .prm input[type=number] { width:100%; font:inherit; font-size:15px; padding:5px 8px; border:1.5px solid var(--ink); border-radius:8px; background:#fff; box-sizing:border-box; }
  .prm input[type=checkbox] { transform:scale(1.25); margin:4px 2px; }
  .hlp { font-size:12.5px; color:var(--muted); margin:3px 0 0; line-height:1.35; }
  .imp { font-size:10.5px; font-weight:700; letter-spacing:.04em; text-transform:uppercase; border-radius:999px; padding:0 7px; border:1px solid var(--ink); vertical-align:1px; }
  .imp.high { background:#FBD3CF; } .imp.med { background:var(--butter-wash); } .imp.low { background:var(--mint-wash); }
  .adv { display:none; } body.expert .adv { display:block; } body.expert details.grp.adv { display:block; }
  details.grp { border:var(--line); border-radius:var(--wob); padding:10px 16px; margin:10px 0; background:#fff; }
  details.grp > summary { cursor:pointer; font-size:17px; } .gsum { float:right; font-weight:700; }
  .gsub { display:block; font-size:13.5px; color:var(--muted); margin:2px 0 6px; } details.grp .prms { margin-top:10px; }
  #g_classic { display:none; } body.is-classic #g_classic { display:block; }
  .tools { display:flex; flex-wrap:wrap; gap:10px; align-items:center; margin:8px 0; }
  table.lines td.num, table.sv td.num { text-align:right; white-space:nowrap; font-weight:700; } table.lines td.k { font-size:13px; color:var(--muted); white-space:nowrap; }
  table.lines details summary { cursor:pointer; } table.lines details p { margin:4px 0 2px; font-size:13.5px; color:var(--ink-soft); }
  .hdn { font-size:10.5px; font-weight:700; text-transform:uppercase; letter-spacing:.04em; background:var(--lilac-wash); border:1px solid var(--ink); border-radius:999px; padding:0 7px; }
  .drv { display:grid; grid-template-columns:200px 1fr 260px; gap:10px; align-items:center; padding:5px 0; border-bottom:1.5px dashed var(--rule); font-size:14px; }
  .dt { position:relative; height:16px; } .dt .mid { position:absolute; left:50%; top:-3px; bottom:-3px; border-left:1.5px solid var(--ink); }
  .dt .db { position:absolute; top:2px; height:12px; background:#F3B9B2; border:1px solid var(--ink); border-radius:4px; }
  .dv { font-size:12.5px; color:var(--muted); }
  @media (max-width:700px) { .drv { grid-template-columns:1fr; } }
  .st-checked { color:#1d6b3a; font-weight:700; } .st-docs { color:#8a5a00; font-weight:700; } .st-estimate { color:#a3322b; font-weight:700; }
</style>"""


def price_rows():
    tiers = ("premium", "enterprise")
    rows = ""
    for k, v in PRICES["dbu"].items():
        src = f'<a href="{v["source"]}">source</a>'
        rows += (f"<tr><td><b>{E(v['label'])}</b>{('<br><span class=hlp>' + E(v['note']) + '</span>') if v.get('note') else ''}</td>"
                 + "".join(f"<td class='num'>${v[t]:.2f}</td>" for t in tiers)
                 + f"<td><span class='st-{v['status']}'>{v['status']}</span> {E(v.get('checked', ''))}</td><td>{src}</td></tr>")
    return rows


def other_rows():
    out = []
    ph = PRICES["photon_dbu_multiplier"]
    out.append(("Photon DBU multiplier", f"{ph['value']}x (range {ph['range'][0]}x to {ph['range'][1]}x)", ph["status"], ph["source"], ph["note"]))
    sm = PRICES["serverless_standard_mode_factor"]
    out.append(("Serverless standard mode", f"{int((1 - sm['value']) * 100)}% cheaper than performance mode", sm["status"], sm["source"], sm["note"]))
    wh = PRICES["sql_warehouse_dbu_per_hour"]
    out.append(("SQL warehouse DBU per hour", ", ".join(f"{k} {v}" for k, v in wh["sizes"].items()), wh["status"], wh["source"], wh["note"]))
    im = PRICES["instances_meta"]
    out.append(("EC2 on-demand prices", ", ".join(f"{k} ${v['usd_per_hour']:.3f}/h ({v['dbu_per_hour']} DBU/h)" for k, v in PRICES["instances"].items()), im["usd_status"] + " " + im["checked"], im["source"], im["note"]))
    for k, v in PRICES["aws"].items():
        out.append(("AWS " + k.replace("_", " "), f"${v['value']}", v["status"], v["source"], ""))
    for k, v in PRICES["estimates"].items():
        out.append((k.replace("_", " ").capitalize(), f"${v['value']}", v["status"], v.get("source", ""), v.get("note", "")))
    return "".join(f"<tr><td><b>{E(a)}</b>{('<br><span class=hlp>' + E(n) + '</span>') if n else ''}</td><td>{E(b)}</td><td><span class='st-{s.split()[0]}'>{E(s)}</span></td><td>{f'<a href={chr(34)}{u}{chr(34)}>source</a>' if u else ''}</td></tr>"
                   for a, b, s, u, n in out)


def calculator_page():
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › <a href="{BASE}">Data systems</a> › <a href="{P}">Data platform</a> › <a href="{C}">Cost</a> › Calculator</p>
<p class="eyebrow" style="margin-top:22px">Free tool · Databricks on AWS · list prices as of {E(PRICES['as_of'])}</p>
<h1>Databricks data platform cost calculator</h1>
<p class="lede">What a Databricks data platform costs end to end, hop by hop from sources to dashboards and agents, with the streaming lane, real-time serving and the hidden costs most estimates leave out. Answer eight questions; open a hop only if you want to change more.</p>

<div class="calc">
  <div class="panel"><h2>Eight answers</h2><div id="quick" class="prms"></div></div>
  <div class="panel result" aria-live="polite">
    <p class="eyebrow" style="margin:0">Whole platform, end to end</p>
    <p class="total" id="total"></p>
    <p class="sub"><span id="yearly"></span> · <span id="range"></span></p>
    <p class="facts" id="facts"></p>
    <div class="bar" id="bar"></div>
    <div class="hopcards" id="hopcards"></div>
    <p class="hlp" id="hidden" style="margin-top:10px;font-size:14px"></p>
  </div>
</div>

<section id="lines-sec"><p class="eyebrow">Where the money goes</p><h2>Every line, and how it was worked out</h2>
<div class="tools"><label>View <select id="view"><option value="hop">By hop (per layer)</option><option value="kind">By kind (Databricks, AWS, storage, network, AI)</option></select></label></div>
<p class="note">Open a line to see the numbers behind it. Lines marked "hidden cost" are the ones that rarely make it into a plan.</p>
<div class="tw"><table class="t lines"><tr><th>Line</th><th>Kind / hop</th><th>Per month</th></tr><tbody id="lines"></tbody></table></div></section>

<section id="drivers-sec"><p class="eyebrow">What matters</p><h2>What drives your cost</h2>
<p>Each row changes one setting both ways and keeps everything else the same. The longest bars are the settings worth getting right; the short ones you can leave at their defaults.</p>
<div id="drivers"></div></section>

<section id="savings-sec"><p class="eyebrow">Spend less</p><h2>Ways to spend less, for your settings</h2>
<div class="tw"><table class="t sv"><tr><th>Change</th><th>Saves per month</th></tr><tbody id="savings"></tbody></table></div></section>

<section id="adjust"><p class="eyebrow">More detail</p><h2>Adjust each hop</h2>
<p>Every hop has its own settings. "Show expert settings" adds the rest, including the work rates the model uses, so you can replace them with numbers from your own system tables.</p>
<div class="tools"><label><input type="checkbox" id="expert"> Show expert settings</label><button class="btn" id="share" type="button">Copy a link to these settings</button><button class="btn" id="reset" type="button">Start again</button></div>
<div id="groups"></div></section>

<section id="how"><p class="eyebrow">How it works</p><h2>How the estimate is made</h2>
<p>Each hop turns its data volumes into <b>work</b>, measured in classic DBU-hours: reading new data, merging changes (plus rewriting the files those changes land in), refreshing gold, pre-computing aggregates. The compute you choose turns work into dollars. Serverless multiplies by one DBU price that includes the machines. Classic multiplies by a lower DBU price and adds the EC2 machines, start-up time and network. SQL warehouses are priced by the hours they are on, which depends on users, schedules and auto-stop, not on the number of queries.</p>
<p>The work rates are calibrated defaults, not measurements of your system. Treat the result as a planning estimate (the range shown is roughly minus a third to plus a half) and confirm it against <code>system.billing.usage</code> once you run. The <a href="{C}">Cost & FinOps page</a> explains the drivers and hidden costs in words.</p></section>

<section id="prices"><p class="eyebrow">Prices used</p><h2>Prices used, and how sure we are</h2>
<p><span class="st-checked">checked</span>: checked against a published source on the date shown. <span class="st-docs">docs</span>: a long-standing published price, not re-fetched automatically yet. <span class="st-estimate">estimate</span>: our estimate. All prices are list prices for AWS US East (N. Virginia), in US dollars.</p>
<div class="tw"><table class="t"><tr><th>Databricks product</th><th>Premium $/DBU</th><th>Enterprise $/DBU</th><th>Status</th><th></th></tr>{price_rows()}</table></div>
<div class="tw"><table class="t"><tr><th>Other price</th><th>Value</th><th>Status</th><th></th></tr>{other_rows()}</table></div>
<p class="note">Prices are refreshed by a monthly job that opens a pull request: EC2 prices come from AWS's public price list, and Databricks prices from the <code>system.billing.list_prices</code> table when a workspace is connected. Check Databricks' <a href="https://www.databricks.com/product/pricing">pricing pages</a> before you commit to a budget.</p></section>

<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2>
<p><b>Understand the bill:</b> <a href="{C}">Cost & FinOps: end to end and per hop</a>.</p>
<p><b>The whole platform:</b> <a href="{P}">The data platform, whole</a>.</p></section>
<script>window.DBX_PRICES = {json.dumps(PRICES)};</script>
<script src="calculator.js"></script>"""
    title = "Databricks cost calculator"
    desc = "Free Databricks data platform cost calculator for AWS: whole-platform and per-hop cost from ingestion to dashboards and agents, streaming and real-time, hidden costs, what drives your bill and how to spend less. List prices with sources."
    url = f"{SITE}{CALC}"
    head = dp.CSS + CALC_CSS + ds.ld(title, desc, url, [("Learn", "/learn/"), ("Data systems", BASE), ("Data platform", P), ("Cost", C), ("Calculator", CALC)])
    return wb.page(title, desc, url, body, head)


def main():
    out_c = ROOT / C.strip("/")
    out_k = ROOT / CALC.strip("/")
    out_k.mkdir(parents=True, exist_ok=True)
    (out_c / "index.html").write_text(cost_page())
    (out_k / "index.html").write_text(calculator_page())
    shutil.copy(TOOLS / "calculator.js", out_k / "calculator.js")
    shutil.copy(TOOLS / "prices.json", out_k / "prices.json")
    print("cost pages ->", out_c)


if __name__ == "__main__":
    main()
