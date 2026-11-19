"""Build an agent on Databricks: the whole design end to end, at /learn/databricks-ai-agent/.

    python3 _guides/databricks_agent.py      (then python3 _guides/platforms.py to refresh the Databricks page)

Written 19 Nov 2026 from the drug-safety signal investigator build (AG-113). Same seven parts as the
motor-claims (FNOL) guide: requirements, architecture, design, development, testing, deploy, monitor.
Public page: no workspace host, no account, no personal names. Status words are literal: "works" means we
ran it on a Databricks Free Edition workspace; "planned" means it is designed and not run.
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("data_systems_dbxagent", ROOT / "_guides" / "data_systems.py")
ds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ds)
E, wb, SITE = ds.E, ds.wb, ds.SITE
URL = f"{SITE}/learn/databricks-ai-agent/"

CSS = """<style>
  .strip { display:flex; flex-wrap:wrap; gap:8px; margin:14px 0 4px; }
  .strip span { border:1.5px solid var(--ink); border-radius:999px; padding:2px 12px; font-size:14px; background:#fff; }
  .strip .done { background:var(--mint-wash); } .strip .doing { background:var(--butter-wash); } .strip .todo { background:#fff; }
  .tw { overflow-x:auto; } table.t { border-collapse:collapse; width:100%; font-size:15px; margin:10px 0 18px; }
  table.t td, table.t th { border:1.5px solid var(--ink); padding:7px 11px; text-align:left; vertical-align:top; } table.t th { background:var(--peri-wash); }
  .st { display:inline-block; border:1.5px solid var(--ink); border-radius:999px; padding:0 9px; font-size:12.5px; white-space:nowrap; }
  .st.works { background:var(--mint-wash); } .st.planned { background:#fff; } .st.no { background:var(--rose-wash); }
  .qa b { display:block; font-family:var(--hand); font-weight:400; font-size:22px; margin-top:14px; }
  .box { background:var(--butter-wash); border:1.5px solid var(--ink); border-radius:var(--wob); padding:14px 20px; margin:16px 0; }
</style>"""

# service, what it is for, how this agent uses it, status
USING = [
    ("Unity Catalog", "One place that names, secures and tracks data, files, functions and models.", "Holds the schema, the tables, the raw-file volume and the agent's tools. The agent's login is granted only those tools and tables.", "works"),
    ("Delta Lake tables", "Tables that are safe to update and keep their history.", "80 drug-and-event count rows and 10 drug labels, loaded from public FDA data.", "works"),
    ("SQL warehouse (serverless)", "Compute that runs SQL and registered functions.", "Runs the table loads and the tool functions.", "works"),
    ("Unity Catalog functions", "Small named functions, registered and permissioned, that an agent may call as tools.", "Three read-only tools: report counts, signal statistics, label check. The model can call these and nothing else, so it never writes SQL.", "works"),
    ("Foundation Model APIs", "Ready-hosted models you pay for per use, behind an OpenAI-style web address.", "The reasoning model (gpt-oss-120b) ran the agent loop with tool calls and wrote a draft assessment.", "works"),
    ("MLflow tracing and evaluation", "Records every step of a run, and scores answers.", "The recorder: each model call and tool call becomes a trace the eval harness reads. Also scores the 20-case test set.", "planned"),
    ("Vector Search", "Finds text by meaning, with an index that stays in step with a Delta table.", "Finding the label passage for an adverse event, so 'swelling of the face' can find 'angioedema'. A keyword-and-synonym lookup does the job meanwhile.", "planned"),
    ("Mosaic AI Agent Framework", "Databricks' standard way to package, register and deploy an agent so it can be traced and served.", "A wrapper around our own loop (the loop stays ours); gives it the standard interface, tracing and registration.", "planned"),
    ("Databricks Apps", "Small web apps that run inside the workspace, signed in as the user.", "The screen where the safety scientist approves, edits or rejects a draft.", "planned"),
    ("Lakeflow Jobs", "Scheduled and triggered runs with retries.", "Runs an investigation as a job; a wait for a person ends the run and a new run starts on the decision.", "planned"),
    ("System tables", "Databricks' own usage, billing and audit records as tables.", "Cost per assessment from real billing rows.", "planned"),
    ("Genie", "Ask a governed table a question in plain English.", "A comparison, not part of the agent: what can Genie answer about the counts alone, and where does it stop?", "planned"),
]
NOT = [
    ("Agent Bricks", "Higher-level builders for common agents (question answering over documents, information extraction, a supervisor over several agents), mostly without code.", "It hides the parts this build exists to learn, and our agent has a typed tool contract, an approval step and its own checks. Worth knowing for a customer who wants a quick answer over documents."),
    ("AI Functions (ai_query, ai_classify and similar)", "SQL functions that call a model once per row.", "Our agent decides which tools to call per case. It is not a per-row batch job. They would fit tagging thousands of report narratives."),
    ("Custom Model Serving and AI Gateway", "Host your own model or agent as a web service, with limits, guardrails and logging in front.", "A person reviews each investigation later, so a job is enough and a live endpoint adds cost and a way in. Revisit when the agent is used interactively. AI Gateway sits in front of serving endpoints, so it comes back with them."),
    ("Feature engineering, model training and fine-tuning", "Build and tune your own models.", "There is no model to train: the statistics are formulas and the language model is used as it is."),
    ("Provisioned throughput", "Reserved model capacity.", "Pay-per-use is enough at this volume."),
    ("Lakehouse Monitoring", "Profiles data and tracks drift in tables.", "Optional here; the eval harness watches the agent, not the tables."),
    ("Delta Sharing, Clean Rooms, Marketplace", "Share data with other organisations.", "Nothing is shared."),
]

PARTS = [
    ("1 · Requirements", [
        ("What it must do", ["Take a drug and an adverse event, and report the counts of FDA reports.", "Compute disproportionality statistics (PRR, ROR) in code.", "Check whether the drug's current label already mentions the event.", "Draft an assessment, with its uncertainty stated, for a person to approve, edit or reject."]),
        ("How well", ["Every number and label statement in a draft equals what a tool returned, in 100% of drafts.", "At most 6 steps and about USD 0.05 of model spend per investigation.", "The agent drafts and never files, sends or decides.", "Text inside a label is data, never an instruction."]),
    ]),
    ("2 · Architecture", [
        ("The idea", ["The same agent harness as the other agents on this site: a loop, tools behind a contract, policy, cost limits, approval, tracing. Only the bindings change between clouds.", "On Databricks, each port of the harness is filled by a Databricks service: the model by Foundation Model APIs, the tools by Unity Catalog functions, the state by Delta tables, the telemetry by MLflow, the identity by a service principal, the approval screen by an App."]),
    ]),
    ("3 · Design", [
        ("Security", ["Least privilege: the agent's login can run exactly its three functions and read exactly its tables.", "No SQL from the model; typed functions only.", "Label text is untrusted: quotes enter the context as data. A hostile instruction hidden in a quote is tested and changes nothing."]),
        ("Reliability", ["The final answer has a typed output contract. An invalid answer gets one repair turn, then goes to a person.", "A failed model call is retried once, then goes to a person with the reason.", "A rate limit makes the client wait as long as the server asks."]),
        ("Cost", ["Cost is measured per investigation, from tokens now and from billing system tables later.", "Statistics are code, so the model never spends tokens on arithmetic."]),
    ]),
    ("4 · Development", [
        ("What exists", ["Data pipeline from the public FDA API into Delta tables.", "Three tools, first as tested Python and now as Unity Catalog functions, which must give the same answers.", "The agent loop, the output contract and a grounding check.", "A Databricks model client that has run an investigation end to end.", "The specification (AOAS), a generated brief of 76 capabilities and 57 obligations, and the first Databricks adapter in the shared harness library."]),
        ("Honest note", ["The first version was written standalone, outside the shared harness library, to test feasibility. Rebuilding it on the library, the way the other agents are built, is in progress. The tools and statistics carry over."]),
    ]),
    ("5 · Testing", [
        ("What ran", ["48 unit tests, table-driven, on the tools, the statistics and the loop (model invents a number, skips a tool, calls a tool that does not exist, never finishes, sends bad JSON, hides an instruction in a label).", "A 20-case run (10 known signals, 10 controls, ground truth taken from the data and the labels) on a stand-in model: 20 of 20 drafts, both required tools called, every number matched the tools.", "One run on the Databricks model: three tools, clean grounding check, 31 seconds."]),
        ("Still to do", ["Run the 20 cases on the Databricks model.", "Judge the quality of the written assessments, calibrated against human labels.", "A simulated world and scenarios in AgentTwin, and the four gates."]),
    ]),
    ("6 · Deploy and release", [
        ("Plan", ["An Asset Bundle that creates the schema, tables, functions and job together.", "The agent runs as a job under a service principal; releases are bundle versions.", "Vector Search and the approval App are added once their tiers pass."]),
    ]),
    ("7 · Monitor", [
        ("Plan", ["MLflow traces are read by the eval harness, which answers 62 everyday questions about any agent (is it failing, how fast, what does it cost, which tools fail, which guardrails fire) on a dashboard.", "The same 62 questions run on the Azure version of the harness, so one set of checks and questions covers both clouds. Where a platform cannot answer one, the dashboard says so and why."]),
    ]),
]

QA = [
    ("Are we using Mosaic AI?", "Yes, in part. Mosaic AI is Databricks' name for its AI products as a group: Foundation Model APIs, Model Serving, Vector Search, Agent Framework, Agent Evaluation and AI Gateway. We use Foundation Model APIs today, and Vector Search, Agent Framework and evaluation are planned. Model Serving and AI Gateway are deliberately not used yet. Databricks renames products often, so check the current docs."),
    ("Are we using Agent Bricks?", "No, on purpose. It builds common agents for you; we are building one by hand to learn the parts, and ours needs its own approval step and checks."),
    ("Why Unity Catalog functions and not letting the model write SQL?", "A function has typed inputs, a permission and an audit trail. A model that writes SQL can read anything its login can read, and can be talked into it by text in the data."),
    ("Why keep our own loop instead of Agent Framework's?", "The loop is where step limits, stop rules, approval and cost limits live, and we want them the same on every cloud. Agent Framework wraps the loop for packaging, tracing and registration."),
    ("Why not a live serving endpoint?", "Each investigation is reviewed by a person afterwards, so a job is enough. An endpoint adds cost and a way in."),
    ("What did the free workspace not allow?", "On one Free Edition workspace several calls were refused with 'try again later' on the day: Vector Search, serving and the SQL warehouse. A second Free Edition workspace allowed them, so the cause was a limit on the first workspace and not on Free Edition itself. A lesson in itself: test on more than one workspace before writing 'not supported'."),
]


def table(rows, head, status=False):
    out = '<div class="tw"><table class="t"><tr>' + "".join(f"<th>{E(h)}</th>" for h in head) + "</tr>"
    for r in rows:
        cells = "".join(f"<td>{E(c)}</td>" for c in r[:-1]) if status else "".join(f"<td>{E(c)}</td>" for c in r)
        if status:
            cells = f'<td><b>{E(r[0])}</b></td>' + "".join(f"<td>{E(c)}</td>" for c in r[1:-1]) + f'<td><span class="st {r[-1]}">{r[-1]}</span></td>'
        out += f"<tr>{cells}</tr>"
    return out + "</table></div>"


def page():
    parts = ""
    for title, blocks in PARTS:
        parts += f"<h2>{E(title)}</h2>"
        for h, items in blocks:
            parts += f"<h3>{E(h)}</h3><ul>" + "".join(f"<li>{E(i)}</li>" for i in items) + "</ul>"
    nots = '<div class="tw"><table class="t"><tr><th>Service</th><th>What it is for</th><th>Why we do not use it here</th></tr>' + "".join(
        f'<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td>{E(c)}</td></tr>' for a, b, c in NOT) + "</table></div>"
    qa = '<div class="qa">' + "".join(f"<b>{E(q)}</b><p>{E(a)}</p>" for q, a in QA) + "</div>"
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/platforms/">On your cloud</a> › <a href="/platforms/databricks/">Databricks</a> › Build an agent</p>
<p class="eyebrow" style="margin-top:22px">Databricks · AI</p>
<h1>Build an agent on Databricks: the whole design, end to end</h1>
<p class="lede">The purpose is two things at once: build a real agent on Databricks, and learn Databricks' AI offerings by using each one for a job. The agent is a drug-safety signal investigator: it counts adverse-event reports, computes statistics in code, checks the drug's label, and drafts an assessment for a person to decide. It follows the same seven parts as the claims (FNOL) guide.</p>
<div class="strip"><span class="done">Data in Delta: works</span><span class="done">Tools as Unity Catalog functions: works</span><span class="done">Databricks model runs the agent: works</span><span class="doing">Rebuild on the shared harness: in progress</span><span class="todo">MLflow tracing: planned</span><span class="todo">Vector Search: planned</span><span class="todo">Approval app: planned</span><span class="todo">Dashboards: planned</span></div>
<p class="note">Status as of 19 November 2026. The code is not public yet. Where this page says "works", we ran it on a Databricks Free Edition workspace.</p>
<h2>What we use, what it is for, and how</h2>
{table(USING, ["Service", "What it is for", "How this agent uses it", "Status"], status=True)}
<h2>What we are not using, and why</h2>
{nots}
<div class="box"><b>Mosaic AI</b> is Databricks' brand for the AI products as a group. So "are we using Mosaic AI?" is answered service by service in the two tables above. Product names change often; check the current Databricks docs before you build.</div>
{parts}
<h2>Questions this page answers</h2>
{qa}
<h2>Where to go next</h2>
<ul><li><a href="/learn/agent-harness/">The agent harness, end to end</a>: the generic design this agent is built on.</li>
<li><a href="/projects/claims-fnol-azure/">Claims FNOL assistant on Azure</a>: the first agent on the same harness.</li>
<li><a href="/projects/drug-safety-agent-databricks/">The project page</a>: tasks, roles and how to join.</li>
<li><a href="/platforms/databricks/">Databricks on this site</a>: the platform map.</li></ul>"""
    desc = "Build an agent on Databricks end to end: which Databricks AI services we use and which we do not, why, and the design in seven parts, from a drug-safety signal investigator."
    return wb.page("Build an agent on Databricks", desc, URL, body, ds.CSS + CSS + ds.ld("Build an agent on Databricks", desc, URL, [("Databricks", "/platforms/databricks/"), ("Build an agent", "/learn/databricks-ai-agent/")]))


def main():
    out = ROOT / "learn" / "databricks-ai-agent"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("databricks agent guide ->", out)


if __name__ == "__main__":
    main()
