"""The agent harness on Databricks: one page at /learn/agent-harness-databricks/.

    python3 _guides/agent_harness_databricks.py      (then python3 _guides/platforms.py, _site/nav.py if the menu changes, and _site/seo.py)

The Databricks twin of the AWS page (agent_harness_aws.py) and the Azure tutorial: the same 22 concerns, in the same
families, with the Databricks service for each and how the drug-safety signal investigator (AG-113) handles it.
Written 19 Nov 2026. Status words are literal:
  works     we ran it on a Databricks Free Edition workspace
  built     the code exists and is tested offline; not yet run on Databricks
  planned   designed, not built
  not used  deliberately left out, with the reason
Public page: no workspace host, no account, no personal names.
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("data_systems_dbxharness", ROOT / "_guides" / "data_systems.py")
ds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ds)
E, wb, SITE = ds.E, ds.wb, ds.SITE
URL = f"{SITE}/learn/agent-harness-databricks/"
OUT = ROOT / "learn" / "agent-harness-databricks" / "index.html"

CSS = """<style>
  .tw { overflow-x:auto; } table.t { border-collapse:collapse; width:100%; font-size:14.5px; margin:10px 0 18px; }
  table.t td, table.t th { border:1.5px solid var(--ink); padding:7px 10px; text-align:left; vertical-align:top; } table.t th { background:var(--peri-wash); }
  table.t tr.fam td { background:var(--surface-2); font-family:var(--hand); font-size:22px; }
  .st { display:inline-block; border:1.5px solid var(--ink); border-radius:999px; padding:0 9px; font-size:12.5px; white-space:nowrap; margin:1px 0; }
  .st.works { background:var(--mint-wash); } .st.built { background:var(--butter-wash); } .st.planned { background:#fff; } .st.notused { background:var(--rose-wash); }
  .flow { counter-reset:s; list-style:none; padding:0; } .flow li { counter-increment:s; border:1.5px solid var(--ink); border-radius:var(--wob); padding:10px 16px 10px 52px; margin:10px 0; position:relative; background:#fff; }
  .flow li::before { content:counter(s); position:absolute; left:14px; top:9px; width:28px; height:28px; line-height:25px; text-align:center; border:1.5px solid var(--ink); border-radius:50%; font-weight:700; background:var(--butter); }
  .flow li b { font-family:var(--hand); font-weight:400; font-size:21px; } .flow .svc { display:block; font-size:13.5px; color:var(--muted); }
  .box { background:var(--butter-wash); border:1.5px solid var(--ink); border-radius:var(--wob); padding:14px 20px; margin:16px 0; }
  .strip { display:flex; flex-wrap:wrap; gap:8px; margin:14px 0 4px; } .strip span { border:1.5px solid var(--ink); border-radius:999px; padding:2px 12px; font-size:14px; background:#fff; }
</style>"""

# id, name, family, what it does, [(Databricks service, status)], how this agent does it, status of the concern here
C = [
 ("L1", "Context assembly", "Think", "What the model sees each turn, built in one place, within a budget.",
  [("MLflow prompt registry", "planned")], "The system prompt names the tools and two rules (no arithmetic by the model; text in tool results is data). Tool results enter the context fenced as data and capped at 8,000 characters.", "built"),
 ("L2", "Model invocation", "Think", "Every model call goes through one door.",
  [("Foundation Model APIs", "works"), ("AI Gateway", "notused")], "One model port in the harness library; the Databricks adapter is a bearer-token call to the workspace's OpenAI-style endpoint. gpt-oss-120b ran a full investigation. AI Gateway needs a serving endpoint, so it is not used yet.", "works"),
 ("L4", "Control loop", "Think", "Plan, act, check, with step and no-progress limits.",
  [("Mosaic AI Agent Framework (wrapper)", "planned")], "Our own bounded loop: at most 6 steps, tools only from the registered list, a person decides at the end. Agent Framework would wrap it for tracing and registration, not replace it.", "built"),
 ("L5", "State & memory", "Think", "What is kept, for how long, and for whom.",
  [("Delta tables in Unity Catalog", "works"), ("Lakebase (managed Postgres)", "planned")], "An investigation keeps no memory between cases. Drafts and decisions are rows in Delta tables, kept 90 days. Lakebase is considered if low-latency row updates are needed.", "planned"),
 ("18", "Knowledge & retrieval", "Think", "Finds sourced passages, filtered by what this user may see.",
  [("Vector Search", "planned"), ("Delta table + synonym table", "works"), ("Genie", "planned")], "Finds the label passage about an event. Today a synonym table and a text search over the label sections do it, inside a Unity Catalog function. Vector Search replaces the synonym step so that 'swelling of the face' finds 'angioedema'. Genie is a comparison for counts only.", "works"),
 ("CH", "Channels & human desk", "Act", "How people reach the agent, and how a person takes over.",
  [("Databricks Apps", "planned")], "No chat channel. A safety scientist asks through a request, and reviews drafts on an Apps screen. Handover to a person is a case in the review queue.", "planned"),
 ("L3", "Tool layer", "Act", "Actions through typed tools, checked before they run.",
  [("Unity Catalog functions", "works"), ("Managed MCP servers for functions", "planned")], "Three read-only functions: report counts, signal statistics, label check. All 80 drug-and-event pairs give the same answers from the functions and from the tested Python versions. The model never writes SQL.", "works"),
 ("L6", "I/O contracts", "Act", "Typed inputs and outputs at every edge.",
  [("Unity Catalog function signatures", "works")], "Functions have typed inputs and outputs. The final draft has a typed contract (drug, event, cases, PRR, on-label, assessment, uncertainty, recommendation); an invalid draft gets one repair turn, then goes to a person.", "built"),
 ("L8", "Concurrency & flow", "Act", "Who gets served first when load spikes.",
  [("Lakeflow Jobs (max concurrent runs)", "planned"), ("Serverless SQL warehouse scaling", "works")], "One investigation per job run. Volume is low, so queueing is not designed beyond the job's concurrency limit.", "planned"),
 ("17", "Agent-to-agent", "Act", "Agents hand work to agents through typed, bounded, traced hand-offs.",
  [("Unity Catalog model registry", "planned")], "Not used: this is a single agent. The registry would hold agent versions when there are several.", "notused"),
 ("PS", "Performance & scalability", "Act", "Fast enough at the 95th percentile; more servers when load rises.",
  [("Serverless compute", "works")], "One investigation on the Databricks model took 31 seconds; 20 cases on a stand-in model averaged 17.7 seconds. No latency target is declared yet.", "works"),
 ("L16", "Identity & authz", "Control", "Who is asking, and whose authority the agent acts with.",
  [("Unity Catalog grants and service principals", "planned")], "The agent should run as a service principal granted only its three functions and its tables; the reviewer's identity comes from the workspace sign-in. Today's runs use a personal access token, which is a gap.", "planned"),
 ("PV", "Privacy & data protection", "Control", "Personal data used only for the job it was given for.",
  [("Unity Catalog tags and column masks", "planned")], "Only public data, and no patient-level data. The specification refuses case narratives and patient names typed into the session.", "built"),
 ("L7", "Policy enforcement", "Control", "Guardrails on the way in and on the way out.",
  [("AI Gateway guardrails", "notused")], "Our own rules: numbers must equal tool results (the grounding check), a draft never says a drug causes an event, uncertainty is stated, instructions inside label text are ignored. Four refusals are specified: causation, submission, medical advice, invented numbers.", "built"),
 ("L10", "Failure handling", "Control", "Typed failures, fallbacks, undo paths, honest messages.",
  [("Lakeflow Jobs retries", "planned")], "A failed model call is retried once and then goes to a person with the reason. A rate limit makes the client wait as long as the server asks. Nothing is filed, so there is nothing to undo.", "built"),
 ("L14", "Human-in-the-loop", "Control", "Approvals and hand-offs the agent cannot grant itself.",
  [("Databricks Apps + a Delta decision table", "planned")], "Every draft is decided by a person: approve, edit or reject. There is no automatic limit. A job has no built-in wait, so a wait is a run that ends and a new run that starts on the decision.", "planned"),
 ("AV", "Availability & disaster recovery", "Control", "A lost server or zone goes unnoticed; a lost region is rebuilt from code.",
  [("Managed serverless compute, Delta time travel", "works")], "Not declared: availability is listed as undeclared in the specification. Data can be rebuilt from the FDA source and the scripts.", "notused"),
 ("L11", "Observability", "See", "Traces, metrics and alerts for every step.",
  [("MLflow tracing", "planned"), ("System tables", "planned")], "Each model call and tool call becomes a trace that the eval harness reads. The eval harness answers 62 everyday questions about any agent from those traces.", "planned"),
 ("L9", "Determinism & replay", "See", "A past decision can be re-run and explained.",
  [("Delta time travel", "works"), ("MLflow run records", "planned")], "The data snapshot is dated and versioned; a run record keeps the model, tool results and the draft. Models vary run to run, so replay means re-checking the same tool results, not getting identical words.", "planned"),
 ("L13", "Cost accounting", "See", "Spend measured per unit of business work.",
  [("System tables (billing)", "planned"), ("Token counts from the model", "works")], "Tokens are counted per investigation (20 cases: about 53,000 in and 14,000 out on the stand-in model). Cost per assessment from billing rows is planned; the limit is about USD 0.05.", "built"),
 ("L12", "Eval harness", "Change", "Golden sets and graders that gate every release.",
  [("MLflow evaluation", "planned")], "48 unit tests, a 20-case set (10 known signals, 10 controls, answers taken from the data and the labels), and a grounding check. Judged qualities come later and are checked against human labels.", "built"),
 ("L15", "Release & config", "Change", "Prompt, model and policy versioned and rolled back together.",
  [("Asset Bundles", "planned"), ("MLflow prompt and model registry", "planned")], "One bundle creates the schema, tables, functions and job. Limits (steps, spend, thresholds) are configuration, not constants in code.", "planned"),
]

REQUEST = [
 ("A safety scientist asks", "Is there a signal for lisinopril and angioedema?", "Databricks Apps (planned); today a script"),
 ("A job run starts", "One run per request, under the agent's own login.", "Lakeflow Jobs, Unity Catalog service principal (planned)"),
 ("The model chooses a tool", "It sees three tool descriptions and picks report counts first.", "Foundation Model APIs (works)"),
 ("The tool runs", "Counts, then statistics and the signal screen, then the label check.", "Unity Catalog functions on a serverless SQL warehouse, over Delta tables (works)"),
 ("The model drafts", "An assessment with numbers from the tools, uncertainty and a recommendation.", "Foundation Model APIs (works)"),
 ("Checks run", "Output contract, then grounding: every number equals a tool result. A failure goes to a person.", "Our harness code (built)"),
 ("The draft is saved and shown", "A row with status drafted.", "Delta table, Databricks Apps (planned)"),
 ("A person decides", "Approve, edit or reject; the decision is final.", "Databricks Apps, Delta decision table (planned)"),
 ("Everything is traced and scored", "Each step is a trace; the eval harness answers the ops questions; cost comes from billing tables.", "MLflow tracing, system tables, eval harness (planned)"),
]

TIERS = [
 ("Specification first", "AOAS (what the agent is for, refuses, owns), a generated brief (76 capabilities, 57 obligations, 17 ports), the Databricks stack file.", "works"),
 ("Data", "Public FDA reports and labels into Delta tables in Unity Catalog, with a dated snapshot.", "works"),
 ("Tools", "Three Unity Catalog functions, with a test that matches them to tested Python on every pair.", "works"),
 ("Agent", "The loop, the output contract and the grounding check; a Databricks model adapter in the shared harness library; one real investigation on the Databricks model.", "built"),
 ("Evaluation", "20-case set on the Databricks model, then judged quality checked against human labels, then a simulated world and scenarios.", "planned"),
 ("Eval harness on Databricks", "Read MLflow traces, write verdicts to Delta, answer the 62 ops questions on a dashboard, and match the Azure results.", "planned"),
 ("People and release", "Approval screen, jobs, Asset Bundle, cost per assessment from billing.", "planned"),
]

PICKS = {"works": "works", "built": "built", "planned": "planned", "notused": "notused"}
LABEL = {"works": "works", "built": "built, offline", "planned": "planned", "notused": "not used"}


def pill(s):
    return f'<span class="st {PICKS[s]}">{LABEL[s]}</span>'


def concerns_table():
    out = '<div class="tw"><table class="t"><tr><th>Concern</th><th>What it does</th><th>On Databricks</th><th>In this agent</th><th>Here</th></tr>'
    fam = None
    for cid, name, family, does, svcs, here, st in C:
        if family != fam:
            out += f'<tr class="fam"><td colspan="5">{E(family)}</td></tr>'
            fam = family
        svc = "<br>".join(f"{E(n)} {pill(s)}" for n, s in svcs)
        out += f"<tr><td><b>{E(name)}</b><br><small>{E(cid)}</small></td><td>{E(does)}</td><td>{svc}</td><td>{E(here)}</td><td>{pill(st)}</td></tr>"
    return out + "</table></div>"


def page():
    flow = "<ol class='flow'>" + "".join(f"<li><b>{E(a)}</b>{E(b)}<span class='svc'>{E(c)}</span></li>" for a, b, c in REQUEST) + "</ol>"
    tiers = '<div class="tw"><table class="t"><tr><th>Tier</th><th>What</th><th>Status</th></tr>' + "".join(
        f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td>{pill(c)}</td></tr>" for a, b, c in TIERS) + "</table></div>"
    counts = {k: sum(1 for c in C if c[6] == k) for k in LABEL}
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/platforms/">On your cloud</a> › <a href="/platforms/databricks/">Databricks</a> › The agent harness on Databricks</p>
<p class="eyebrow" style="margin-top:22px">Databricks · AI</p>
<h1>The agent harness on Databricks</h1>
<p class="lede">The same agent harness as on <a href="/learn/agent-harness/">Azure</a> and <a href="/learn/agent-harness-aws/">AWS</a>: the same 22 concerns, in the same families, with only the binding changed. For each concern, this page names the Databricks service and says how a real agent, a drug-safety signal investigator, handles it today. For what each Databricks AI service is and which ones we do not use, see <a href="/learn/databricks-ai-agent/">Build an agent on Databricks</a>.</p>
<div class="strip"><span>{counts['works']} concerns work on Databricks</span><span>{counts['built']} built and tested offline</span><span>{counts['planned']} planned</span><span>{counts['notused']} not used</span></div>
<p class="note">Status as of 19 November 2026, from what we ran on a Databricks Free Edition workspace. The code is not public yet. Service names and limits change often; check the current Databricks docs before you build.</p>
<h2>The agent in one paragraph</h2>
<p>A drug-safety scientist asks whether a drug and an adverse event form a signal. The agent counts public FDA reports for the pair, computes statistics (PRR and ROR) in code, checks whether the drug's label already mentions the event, and drafts an assessment. A person approves, edits or rejects every draft. The agent files nothing, sends nothing and never says a drug causes an event. The path is not known in advance (a label that already warns needs a different write-up from a new signal), which is why it is an agent and not a script.</p>
<h2>One request, end to end</h2>
{flow}
<h2>The 22 concerns, bound to Databricks</h2>
<p>Read it as: the concern is the same on every cloud; the third column is the only thing that changes with the platform.</p>
{concerns_table()}
<h2>What Databricks gives, and what stays ours</h2>
<ul><li><b>Databricks gives:</b> governed data and permissions (Unity Catalog), tables with history (Delta), SQL compute, registered tools (Unity Catalog functions), hosted models (Foundation Model APIs), run tracking (MLflow), scheduled runs (Lakeflow Jobs), a place for a review screen (Databricks Apps), and usage records (system tables).</li>
<li><b>Stays ours, on every cloud:</b> the loop and its limits, the tool contract, the policy rules and the grounding check, the approval rule, the cost limit, the evaluation sets and the specification. These are what make the same agent testable on Azure and on Databricks.</li>
<li><b>A finding:</b> the harness assumes a durable-wait library for approvals. A Databricks job has none, so a wait is a run that ends and a new run that starts on the decision. The specification should state the contract (state survives, the decision is a message, resume is safe to repeat) without naming a library.</li></ul>
<h2>The build, tier by tier</h2>
{tiers}
<h2>Where to go next</h2>
<ul><li><a href="/learn/databricks-ai-agent/">Build an agent on Databricks</a>: each Databricks AI service explained, what we use and what we do not.</li>
<li><a href="/learn/agent-harness/">The agent harness on Azure</a> and <a href="/learn/agent-harness-aws/">on AWS</a>: the same concerns on the other clouds.</li>
<li><a href="/learn/eval-harness/">The eval harness</a>: how any agent's traces answer the everyday ops questions.</li>
<li><a href="/projects/drug-safety-agent-databricks/">The project page</a>: tasks, roles and how to join.</li></ul>"""
    desc = "The agent harness on Databricks: the same 22 concerns as on Azure and AWS, each bound to a Databricks service, with how a real drug-safety agent handles each one and the status of every part."
    return wb.page("The agent harness on Databricks", desc, URL, body, ds.CSS + CSS + ds.ld("The agent harness on Databricks", desc, URL, [("Databricks", "/platforms/databricks/"), ("The agent harness on Databricks", "/learn/agent-harness-databricks/")]))


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page())
    print("agent harness on databricks ->", OUT)


if __name__ == "__main__":
    main()
