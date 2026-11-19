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
  .svc { border:1.5px solid var(--ink); border-radius:var(--wob); padding:12px 18px; margin:14px 0; background:#fff; }
  .svc h4 { font-family:var(--hand); font-weight:400; font-size:24px; margin:0 0 2px; } .svc .one { margin:0 0 6px; color:var(--ink-soft); }
  .svc dl { margin:0; } .svc dt { font-weight:700; font-size:13px; letter-spacing:.05em; text-transform:uppercase; color:var(--muted); margin-top:8px; } .svc dd { margin:0; } .svc code { font-size:13px; white-space:pre-wrap; }
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
    ("AI Gateway (default settings only)", "A control point in front of model endpoints: usage tracking, rate limits, guardrails, fallbacks.", "Usage tracking is on for the hosted model endpoint by default, so every call is counted by the platform. We configure nothing else on it.", "works"),
    ("Genie", "Ask a governed table a question in plain English.", "A comparison, not part of the agent: what can Genie answer about the counts alone, and where does it stop?", "planned"),
]
NOT = [
    ("Agent Bricks", "Higher-level builders for common agents (question answering over documents, information extraction, a supervisor over several agents), mostly without code.", "It hides the parts this build exists to learn, and our agent has a typed tool contract, an approval step and its own checks. Worth knowing for a customer who wants a quick answer over documents."),
    ("AI Functions (ai_query, ai_classify and similar)", "SQL functions that call a model once per row.", "Our agent decides which tools to call per case. It is not a per-row batch job. They would fit tagging thousands of report narratives."),
    ("Custom Model Serving", "Host your own model or agent as a web service.", "A person reviews each investigation later, so a job is enough and a live endpoint adds cost and a way in. Revisit when the agent is used interactively."),
    ("AI Gateway: limits, guardrails and fallbacks", "A control point in front of model endpoints.", "The hosted model endpoint we call already has AI Gateway attached with usage tracking on, by default. We have not configured rate limits, guardrails, request logging or fallbacks: our own harness enforces the step limit, the output contract and the grounding check. Worth configuring before more than one team uses the same endpoint."),
    ("Feature engineering, model training and fine-tuning", "Build and tune your own models.", "There is no model to train: the statistics are formulas and the language model is used as it is."),
    ("Provisioned throughput", "Reserved model capacity.", "Pay-per-use is enough at this volume."),
    ("Lakehouse Monitoring", "Profiles data and tracks drift in tables.", "Optional here; the eval harness watches the agent, not the tables."),
    ("Delta Sharing, Clean Rooms, Marketplace", "Share data with other organisations.", "Nothing is shared."),
]


# Detailed cards: name, layer, one line, problem it solves, how it works, a small example, how this agent uses it, the usual confusion
SERVICES = [
    ("Unity Catalog", "1 · Governed data", "One place that names, secures and tracks everything: tables, files, functions and models.",
     "Without it, every tool has its own login and nobody can say who touched what.",
     "Every object has a three-part name, catalog.schema.object. Permissions are granted on those names, and lineage records what read or wrote what.",
     "GRANT SELECT ON TABLE workspace.drugsafety.pair_counts TO `agent-service-principal`",
     "Holds the schema, the tables, a volume for the raw files and the three tool functions. The agent's login is granted only those.",
     "It is not a database. It is the permission and lineage layer over data stored elsewhere."),
    ("Delta Lake tables", "1 · Governed data", "A table format that is safe to update and remembers its history.",
     "Plain files cannot be updated safely by two writers, and cannot answer 'what did this look like last week?'.",
     "Data files plus a transaction log. Every change is a new version; older versions stay readable.",
     "SELECT * FROM pair_counts VERSION AS OF 3",
     "Holds 80 drug-and-event count rows and 10 drug labels from public FDA data. Later: each draft assessment and each reviewer decision, so an audit can replay the past.",
     "A Delta table is not a different database. It is files in cloud storage with a log beside them."),
    ("SQL warehouse (serverless)", "1 · Governed data", "Compute that runs SQL and the registered functions.",
     "Something has to run the queries and functions; you do not want to manage a cluster to do it.",
     "A serverless warehouse starts on demand and stops when idle. The Statement Execution API runs one SQL statement and returns rows.",
     "POST /api/2.0/sql/statements with a warehouse id and a statement",
     "Runs the table loads, the function registration and every tool call.",
     "A warehouse is for SQL. Notebooks and jobs use other compute."),
    ("Foundation Model APIs", "2 · Models", "Ready-hosted models you call and pay for per use, with no servers to run.",
     "Hosting a large model yourself is slow and costly.",
     "Each hosted model is an endpoint with an OpenAI-style chat format, including tool calls. Open models (gpt-oss, Llama, Qwen, Gemma) and embedding models (bge, gte) are listed in the workspace.",
     "POST /serving-endpoints/databricks-gpt-oss-120b/invocations with a list of chat messages",
     "The reasoning model runs the loop: it chooses which tool to call, reads the results and drafts the assessment.",
     "Pay-per-token and provisioned throughput are two ways of buying the same models: share a pool, or reserve capacity."),
    ("Model Serving and AI Gateway", "2 · Models", "Host your own model or agent as a web service; AI Gateway puts limits, guardrails and logging in front of model endpoints.",
     "Without a control point, every team enforces its own rate limit, privacy rule and cost report.",
     "Serving turns a registered model or agent into an endpoint that scales up and down. AI Gateway adds rate limits, guardrails, usage tracking and fallbacks in front of endpoints.",
     "an endpoint with a rate limit of N calls per minute per user",
     "Custom Model Serving is not used: each investigation is reviewed by a person afterwards, so a job is enough. AI Gateway is attached to the hosted model endpoint with usage tracking on by default (we checked the endpoint); we have not configured rate limits, guardrails or fallbacks.",
     "Foundation Model APIs are hosted for you. Model Serving is where you host your own."),
    ("Unity Catalog functions as tools", "3 · Tools and knowledge", "A small named SQL or Python function, registered in Unity Catalog, that an agent may call.",
     "Letting a model write SQL is unsafe: it can read anything its login can, and text in the data can talk it into doing so.",
     "A function has typed inputs, a comment the model reads as its description, a permission and an audit trail. The agent is shown only the functions registered for it.",
     "CREATE FUNCTION workspace.drugsafety.report_counts(drug STRING, event STRING) RETURNS TABLE (...) RETURN SELECT ... WHERE t.drug = lower(report_counts.drug) AND t.event = upper(report_counts.event)",
     "The three tools: report counts, signal statistics (PRR, ROR and the screen, computed in SQL) and label check. A test runs all 80 drug-and-event pairs through the functions and through the tested Python versions: every answer matches.",
     "A tool is a contract. The model chooses a tool and its inputs, and the platform decides whether it may run."),
    ("Vector Search", "3 · Tools and knowledge", "Finds text by meaning, with an index that stays in step with a Delta table.",
     "Keyword search misses 'swelling of the face' when the label says 'angioedema'.",
     "An embedding model turns text into a vector, a list of numbers where similar meanings sit close together. A query is embedded the same way and the nearest vectors win. A Delta Sync index re-embeds when the source table changes and inherits its permissions.",
     "search the labels for 'swelling of the face' and get the angioedema passage",
     "Planned for finding the label passage about an event. Today a synonym table does the job, and the guide's next step swaps it.",
     "A vector index finds similar text, not true statements. A retrieved passage still has to be checked."),
    ("AI Functions", "3 · Tools and knowledge", "SQL functions that call a model once per row: ai_query, ai_classify, ai_extract and others.",
     "Tagging or extracting from thousands of rows should not need a loop in Python.",
     "You call the function inside a SELECT, and the warehouse sends each row to a model endpoint.",
     "SELECT ai_classify(narrative, ARRAY('serious', 'non-serious')) FROM reports",
     "Not used. The agent chooses its steps per case; it is not a per-row batch job. They would fit tagging thousands of report narratives.",
     "They are not an agent. They run the same model call on every row."),
    ("Genie", "3 · Tools and knowledge", "Ask a governed table a question in plain English and get SQL and an answer.",
     "Many people need an answer from a table and cannot write SQL.",
     "A Genie space is configured with tables, instructions and example questions; it writes SQL, runs it and shows the result.",
     "'How many reports of angioedema for lisinopril?' returns the count and the SQL behind it",
     "A comparison, not part of the agent: what Genie answers about the counts alone, and where it stops. It cannot weigh evidence or draft an assessment.",
     "Genie answers questions about data. It does not carry out a multi-step investigation with approval."),
    ("Mosaic AI Agent Framework and Agent Bricks", "4 · The agent", "Agent Framework is Databricks' way to write, log, test, register and deploy an agent. Agent Bricks builds common agents for you, mostly without code.",
     "Agents need a standard shape to be traced, evaluated and served consistently.",
     "With Agent Framework you write the agent as a class with a standard interface (ResponsesAgent in current MLflow); MLflow logs it, Unity Catalog registers it, and a deploy step puts it behind an endpoint with a review app. Agent Bricks skips the code for document question-answering, information extraction and multi-agent supervision.",
     "log the agent with MLflow, register it as workspace.drugsafety.signal_investigator, deploy it",
     "Agent Framework is planned as a wrapper around our own loop, for tracing and registration. Agent Bricks is not used: this build exists to see and control the parts.",
     "Agent Framework is not a loop engine like LangGraph. It standardises packaging, tracing and deployment."),
    ("Databricks Apps", "4 · The agent", "Run a small web app (Streamlit, Dash, Gradio or FastAPI) inside the workspace, signed in as the user.",
     "You need a screen for people to act on what the agent produced, without hosting a server elsewhere.",
     "You deploy app code; the platform runs it, handles sign-in and lets it query governed data on the user's behalf.",
     "a page listing drafts, with Approve, Edit and Reject buttons that write a row",
     "Planned for the reviewer's screen: the decision is saved as a row in a Delta table.",
     "An App is a front end. The agent still runs as a job."),
    ("Lakeflow Jobs", "4 · The agent", "Scheduled and triggered runs with retries and a run history.",
     "A long or repeated piece of work should run without someone keeping a laptop open.",
     "A job is a set of tasks with a trigger and parameters. A wait for a person is modelled as a run that ends and a new run that starts on the decision.",
     "run one investigation per request, with two retries",
     "Planned for running investigations.",
     "A job has no built-in way to wait for a human; design the wait."),
    ("MLflow tracing", "5 · Watching and judging", "Records every step of an agent run: each model call and tool call, with inputs, outputs and timings.",
     "A black-box agent cannot be debugged, audited or costed.",
     "Decorate a function with @mlflow.trace, or turn on auto-logging for a model library, and each run appears as a tree of steps.",
     "one trace: model call, three tool calls, final answer, 31 seconds",
     "The raw material for the eval harness, which answers 62 everyday ops questions about any agent from its traces.",
     "Tracing records what happened. Evaluation judges whether it was good."),
    ("MLflow evaluation and judges", "5 · Watching and judging", "Scores agent answers against expectations, with code checks or a model acting as judge.",
     "Without scores, you cannot tell whether a change made the agent better or worse.",
     "You provide inputs, run the agent, and apply scorers: exact checks first, then judged qualities such as groundedness.",
     "does every number in the draft equal what the tools returned?",
     "Deterministic checks first (the output contract and the grounding check, 48 unit tests), then a 20-case set of known signals and controls. Judged qualities come later, checked against human labels.",
     "A judge is a model and can be wrong. Calibrate it before trusting it."),
    ("System tables", "5 · Watching and judging", "Databricks' own usage, billing and audit records, as tables you can query.",
     "Cost and access questions need real records, not estimates.",
     "Tables such as billing usage and audit events are maintained by the platform in a system catalog.",
     "SELECT usage_date, sum(usage_quantity) FROM system.billing.usage GROUP BY usage_date",
     "Planned: cost per assessment from real billing rows.",
     "System tables are read-only records about the workspace."),
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
        ("What exists", ["Data pipeline from the public FDA API into Delta tables.", "Three tools, first as tested Python and now as Unity Catalog functions, which must give the same answers.", "The agent loop, the output contract and a grounding check.", "The agent running on the shared harness loop, with a Databricks model, end to end: three tool calls, a clean grounding check, goal reached in four steps.", "The specification (AOAS), a generated brief of 76 capabilities and 57 obligations, and the first Databricks adapter in the shared harness library."]),
        ("Honest note", ["The first version was written standalone, outside the shared harness library, to test feasibility. It has since been rebuilt on the library, the way the other agents are built: the loop, the step and cost limits and the model port are the library's, and only the tools, the prompt, the output contract and the grounding check are this agent's. Running it on the Databricks model found a real incompatibility (Databricks rejects the newer output-cap field the library sent); it was fixed in the library's Databricks adapter and is covered by a test."]),
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
    ("Are we using Mosaic AI?", "Yes, in part. Mosaic AI is Databricks' name for its AI products as a group: Foundation Model APIs, Model Serving, Vector Search, Agent Framework, Agent Evaluation and AI Gateway. We use Foundation Model APIs today, and Vector Search, Agent Framework and evaluation are planned. Custom Model Serving is deliberately not used; AI Gateway is on for the model endpoint by default but we configure nothing on it. Databricks renames products often, so check the current docs."),
    ("Are we using Agent Bricks?", "No, on purpose. It builds common agents for you; we are building one by hand to learn the parts, and ours needs its own approval step and checks."),
    ("Why Unity Catalog functions and not letting the model write SQL?", "A function has typed inputs, a permission and an audit trail. A model that writes SQL can read anything its login can read, and can be talked into it by text in the data."),
    ("Why keep our own loop instead of Agent Framework's?", "The loop is where step limits, stop rules, approval and cost limits live, and we want them the same on every cloud. Agent Framework wraps the loop for packaging, tracing and registration."),
    ("Why not a live serving endpoint?", "Each investigation is reviewed by a person afterwards, so a job is enough. An endpoint adds cost and a way in."),
    ("What did the free workspace not allow?", "On one Free Edition workspace several calls were refused with 'try again later' on the day: Vector Search, serving and the SQL warehouse. A second Free Edition workspace allowed them, so the cause was a limit on the first workspace and not on Free Edition itself. A lesson in itself: test on more than one workspace before writing 'not supported'."),
]


def service_cards():
    out, layer = "", None
    for name, lay, one, problem, how, example, here, confusion in SERVICES:
        if lay != layer:
            out += f"<h3>{E(lay)}</h3>"
            layer = lay
        out += (f'<div class="svc"><h4>{E(name)}</h4><p class="one">{E(one)}</p><dl>'
                f"<dt>Problem it solves</dt><dd>{E(problem)}</dd><dt>How it works</dt><dd>{E(how)}</dd>"
                f"<dt>Small example</dt><dd><code>{E(example)}</code></dd><dt>In this agent</dt><dd>{E(here)}</dd>"
                f"<dt>Usual confusion</dt><dd>{E(confusion)}</dd></dl></div>")
    return out


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
<div class="strip"><span class="done">Data in Delta: works</span><span class="done">Tools as Unity Catalog functions: works</span><span class="done">Databricks model runs the agent: works</span><span class="done">Rebuilt on the shared harness: works</span><span class="doing">Tools as library tools call the Databricks functions: next</span><span class="todo">MLflow tracing: planned</span><span class="todo">Vector Search: planned</span><span class="todo">Approval app: planned</span><span class="todo">Dashboards: planned</span></div>
<p class="note">Status as of 19 November 2026. The code is not public yet. Where this page says "works", we ran it on a Databricks Free Edition workspace.</p>
<h2>What we use, what it is for, and how</h2>
{table(USING, ["Service", "What it is for", "How this agent uses it", "Status"], status=True)}
<h2>What we are not using, and why</h2>
{nots}
<div class="box"><b>Mosaic AI</b> is Databricks' brand for the AI products as a group. So "are we using Mosaic AI?" is answered service by service in the two tables above. Product names change often; check the current Databricks docs before you build.</div>
{parts}
<h2>Start here: the order to learn and build it</h2>
<ol><li><b>Governed data.</b> Create a schema, load a few tables, grant access. Draw the 2x2 table for one drug and one event by hand.</li>
<li><b>Tools.</b> Write one function that takes a drug and an event and returns the counts. Test it against a plain-Python answer.</li>
<li><b>Model and loop.</b> Call a hosted model with the function listed as a tool. Read one run's steps from start to finish.</li>
<li><b>Checks.</b> Add an output contract and a grounding check (every number equals a tool result). Break them on purpose with a scripted model.</li>
<li><b>Tracing and evaluation.</b> Trace a run in MLflow, then score 20 cases with known answers.</li>
<li><b>People and release.</b> Add the approval screen, run it as a job, and measure cost per investigation.</li></ol>
<h2>Each service explained</h2>
<p>The same services, one at a time, in the order a request meets them. Names and limits change often; check the current Databricks docs before you build.</p>
{service_cards()}
<h2>Questions this page answers</h2>
{qa}
<h2>Where to go next</h2>
<ul><li><a href="/learn/agent-harness-databricks/">The agent harness on Databricks</a>: the 22 concerns bound to Databricks services, and one request end to end.</li>
<li><a href="/learn/agent-harness/">The agent harness, end to end</a>: the generic design this agent is built on.</li>
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
