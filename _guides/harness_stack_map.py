"""The agent harness architecture map: every concern, and which product fills it on each stack, at
/learn/agent-harness-stack-map/.

    python3 _guides/harness_stack_map.py && python3 _site/nav.py && python3 _site/seo.py

Written 20 Nov 2026 from the stack files in clean-ai-engineering/stacks (azure, aws, databricks, open-stack), resolved
against the AI Harness Catalog's 17 ports. There is NO stack file for GCP: that column is a proposal and is marked so.
Public page: no employer, no account, no personal names.
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("data_systems_hsm", ROOT / "_guides" / "data_systems.py")
ds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ds)
E, wb, SITE = ds.E, ds.wb, ds.SITE
URL = f"{SITE}/learn/agent-harness-stack-map/"
OUT = ROOT / "learn" / "agent-harness-stack-map" / "index.html"

CSS = """<style>
  main.wrap { max-width:1500px; }
  main.wrap > :not(.tw):not(.mm):not(.tabs):not(.panel) { max-width:860px; }
  .tw { overflow-x:auto; }
  table.map { border-collapse:collapse; width:100%; min-width:1180px; font-size:13.5px; margin:10px 0 18px; }
  table.map td, table.map th { border:1.5px solid var(--ink); padding:6px 8px; text-align:left; vertical-align:top; }
  table.map th { background:var(--peri-wash); position:sticky; top:0; }
  table.map td.fam { background:var(--butter-wash); font-weight:700; width:104px; }
  table.map td.con { width:118px; font-weight:700; }
  table.map td.ver { background:var(--rose-wash); width:250px; }
  table.map td.gcp { background:#fafafa; }
  .tag { display:inline-block; font-size:11px; border:1.5px solid var(--ink); border-radius:9px; padding:0 6px; margin-bottom:3px; background:#fff; }
  .tag.cloud { background:var(--peri-wash); } .tag.open { background:var(--butter-wash); } .tag.own { background:var(--rose-wash); }
  .st { font-size:11.5px; color:#555; display:block; margin-top:2px; }
  .box { background:var(--butter-wash); border:1.5px solid var(--ink); border-radius:var(--wob); padding:14px 20px; margin:16px 0; }
  .steps { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; margin:14px 0; }
  .steps div { border:1.5px solid var(--ink); border-radius:var(--wob); padding:12px 16px; background:var(--peri-wash); }
  .steps b { display:block; font-family:var(--hand); font-weight:400; font-size:23px; }
  .mm { width:100%; height:auto; margin:10px 0 6px; } .mm text { font-family:var(--hand), sans-serif; fill:#1a1a1a; }
  .legend span { margin-right:14px; font-size:13.5px; }
  .tabs { display:flex; flex-wrap:wrap; gap:8px; margin:12px 0; } .tab { font:inherit; font-size:15px; border:1.5px solid var(--ink); border-radius:var(--wob); background:#fff; padding:6px 14px; cursor:pointer; } .tab.on { background:var(--peri-wash); font-weight:700; }
  table.cut { min-width:980px; } table.cut td.con span.st { display:none; }
</style>"""

# kind: c = cloud service, o = open source product, b = built by us (the same code on every stack)
# status: run = built and run, dec = decided and not built, prop = proposed here, no stack file
R, D, P = "run", "dec", "prop"

FAMILIES = [
    ("The loop and where it runs", [
        ("Control loop", "Who owns the step budget, the no-progress check and the cost ceiling.",
         ("b", "Our bounded loop in a container", D), ("b", "Our bounded loop, wrapped in the Agent Framework interface so it can be traced and logged", D),
         ("b", "Our bounded loop in a container on ECS Fargate", D), ("b", "Our bounded loop on Cloud Run", P), ("b", "Our bounded loop", R),
         "Build it, the same on every stack. A loop you did not write cannot be made to stop where your specification says. Cloud agent runtimes can wrap it; they should not own it."),
        ("Hosting", "Where the agent, its tool servers and the review desk run.",
         ("c", "Container Apps", D), ("c", "Lakeflow job for batch work; Databricks App for an interactive desk", D),
         ("c", "ECS with Fargate (App Runner is closed to new customers; Lambda cannot hold a long wait)", D), ("c", "Cloud Run", P), ("o", "Containers from a compose file", R),
         "Use the container platform of the cloud you are already on. On Databricks a job fits batch investigations."),
    ]),
    ("Models", [
        ("Model access", "The one door every model call goes through: keys, limits, usage records.",
         ("c", "API Management as the AI gateway", D), ("c", "Foundation Model APIs; AI Gateway on top where a serving endpoint is allowed", R),
         ("c", "AgentCore Gateway in front of Bedrock or other providers", D), ("c", "Apigee or API Gateway in front of Vertex AI", P), ("o", "LiteLLM proxy", R),
         "Use the gateway of the cloud where the models and the data sit. Use LiteLLM when no enterprise gateway exists. One enforcement point per path."),
        ("Admission and limits", "How many calls run at once, who waits, who is turned away.",
         ("b", "Semaphores in the harness", D), ("b", "Semaphores in the harness", D), ("b", "Semaphores in the harness", D), ("b", "Semaphores in the harness", P), ("b", "Semaphores in the harness", R),
         "Build it. A few lines of your own beat any product, and it must see the unit of work."),
        ("Cost accounting", "Spend added up per task, with a ceiling that stops work.",
         ("b", "Per-task meter", D), ("b", "Per-task meter", D), ("b", "Per-task meter", D), ("b", "Per-task meter", P), ("b", "Per-task meter", R),
         "Build it. Cost per successful task needs your definition of successful. Cloud billing tables are a cross-check."),
    ]),
    ("Tools and knowledge", [
        ("Tool runtime", "How a tool call is run, under whose authority.",
         ("o", "MCP client", D), ("c", "Unity Catalog functions: typed, permissioned, no free SQL from the model", R),
         ("o", "MCP client", D), ("o", "MCP client", P), ("o", "MCP client", R),
         "MCP everywhere. On Databricks, register the data tools as Unity Catalog functions so permissions and lineage come with them."),
        ("Retrieval", "Turning a question into passages the caller is allowed to see.",
         ("o", "pgvector in the same PostgreSQL", D), ("c", "Vector Search; embeddings in Delta plus a function where Vector Search is refused", D),
         ("o", "pgvector in the same RDS PostgreSQL", D), ("o", "pgvector on Cloud SQL or AlloyDB, or Vertex AI Vector Search", P), ("o", "Not yet bound (pgvector is the natural fit)", D),
         "Start with pgvector in the database you already run: one store, one backup. Use Vector Search when the corpus already lives in Delta."),
    ]),
    ("State and long-running work", [
        ("State", "Conversation, checkpoints, idempotency records, case records.",
         ("c", "Azure Database for PostgreSQL", D), ("c", "Delta tables in Unity Catalog (Lakebase when row updates must be fast)", R),
         ("c", "RDS for PostgreSQL", D), ("c", "Cloud SQL or AlloyDB for PostgreSQL", P), ("o", "PostgreSQL", R),
         "Managed PostgreSQL of your cloud: the same engine on every stack, so the code does not change. On Databricks, Delta."),
        ("Workflow", "Durable steps and waits that survive a restart.",
         ("o", "DBOS, a library on the same PostgreSQL", D), ("c", "Lakeflow Jobs", D), ("o", "DBOS on the same RDS", D), ("o", "DBOS on Cloud SQL (Cloud Workflows is the managed alternative)", P), ("o", "Temporal", R),
         "DBOS by default: no new infrastructure. Temporal when undo flows grow. Lakeflow Jobs on Databricks, where a wait is a run that ends and a new run that starts on the decision."),
        ("Approval", "Where an irreversible action waits for a person.",
         ("o", "DBOS workflows", D), ("c", "A Databricks App writing the decision to a Delta table", D), ("o", "DBOS workflows", D), ("o", "DBOS workflows", P), ("o", "Temporal updates", R),
         "Follow the workflow choice. The decision is a message that your own rule validates, never a button the model can press."),
        ("Trigger", "What starts a run nobody is watching, once.",
         ("b", "Requests store", D), ("b", "Requests store", D), ("b", "Requests store", D), ("b", "Requests store", P), ("b", "Requests store", R),
         "Build it. Exactly-once starts are a rule about your request ids."),
        ("Channel", "The chat surface and the desk where a person takes over.",
         ("o", "Chatwoot agent bot", D), ("o", "Chatwoot agent bot", D), ("o", "Chatwoot agent bot", D), ("o", "Chatwoot agent bot", P), ("o", "Chatwoot agent bot", R),
         "Open source, same everywhere. Skip it if the agent is a job with no chat."),
    ]),
    ("Trust and policy", [
        ("Identity", "Who the unit of work acts for, carried to every tool.",
         ("c", "Entra ID (External ID for customers)", D), ("c", "Unity Catalog service principal; reviewer sign-in from the workspace", D),
         ("c", "Cognito", D), ("c", "Cloud IAM with Identity Platform", P), ("o", "Keycloak", R),
         "Your cloud's identity service. Keycloak only where there is no cloud identity to lean on."),
        ("Secrets", "A credential reference that becomes a secret only at the moment of use.",
         ("c", "Key Vault", D), ("c", "Secret scopes", D), ("c", "Secrets Manager", D), ("c", "Secret Manager", P), ("b", "Environment settings", R),
         "Your cloud's secret store. Environment settings are acceptable for a laptop only."),
        ("Policy", "Rules checked at declared points: before the model, after it, before a tool.",
         ("b", "Positioned rule lists", D), ("b", "Positioned rule lists", D), ("b", "Positioned rule lists", D), ("b", "Positioned rule lists", P), ("b", "Positioned rule lists", R),
         "Build it. No guardrail product knows that a draft's number must equal a tool's number. Cloud filters sit in front as a second layer."),
    ]),
    ("Observe, record and prove", [
        ("Telemetry", "One span per call and one identifier for the whole task.",
         ("c", "Application Insights through OpenTelemetry", D), ("c", "MLflow tracing", D), ("c", "OpenTelemetry to CloudWatch", D), ("c", "OpenTelemetry to Cloud Trace and Logging", P), ("o", "OpenTelemetry to Langfuse", R),
         "Emit OpenTelemetry everywhere; take the cloud's backend. Langfuse is a good choice off-cloud."),
        ("Recorder", "Capture a real interaction and replay it without a network.",
         ("b", "JSON cassettes", D), ("b", "JSON cassettes", D), ("b", "JSON cassettes", D), ("b", "JSON cassettes", P), ("b", "JSON cassettes (VCR library is the target)", R),
         "Build it small; swap to a recording library when it earns its place."),
        ("Evaluation entry point", "A callable the evaluations drive, with graders injected.",
         ("o", "AgentTwin", D), ("o", "AgentTwin", R), ("o", "AgentTwin", D), ("o", "AgentTwin", P), ("o", "AgentTwin", R),
         "AgentTwin on every stack: scenarios are written once, against a declared world."),
    ]),
    ("Release and configuration", [
        ("Configuration", "Model pins, flags, thresholds, allow-lists, outside the image.",
         ("c", "App Configuration", D), ("c", "Bundle variables and job parameters", D), ("c", "AppConfig", D), ("c", "A managed config service, or settings in Git", P), ("o", "Typed settings (OpenFeature is the target)", R),
         "Your cloud's config service. Keep the numbers in the specification and read them, never restate them."),
        ("Agent registry", "The catalogue of agents and tools that may run.",
         ("c", "API Center", D), ("c", "Unity Catalog models and functions", D), ("c", "Agent Registry (not offered in every region; a catalogue in Git works)", D), ("c", "Artifact Registry plus a catalogue in Git", P), ("o", "A catalogue in Git", R),
         "A catalogue in Git is enough to start. Use the platform registry when it gives you permissions you would otherwise build."),
    ]),
]

# ---------------------------------------------------------------------------------------------------------------
# The three-way cut. For each concern: what the PLATFORM gives out of the box (X), what the SHARED assets give (Y:
# the harness library, its adapters, AgentTwin, the evaluation library, the catalogues), and what EACH AGENT writes (Z).
# Levels: 2 = carries most of it, 1 = carries part of it, 0 = nothing for this concern.
# Shared status: "ready" = an adapter exists in the library, "write" = the port exists, the adapter does not,
# "own" = the shared asset is the whole answer (no platform adapter needed).
# ---------------------------------------------------------------------------------------------------------------
PLATFORMS = ["Azure", "Databricks", "AWS", "GCP (proposed)", "Open stack"]

CUT = [
    # concern, shared asset (Y), agent writes (Z), {platform: (level, out of the box, shared status, shared note)}
    ("Control loop",
     "The loop: step and cost budgets, repeat detection, typed endings",
     "Its budget numbers from the specification, its standing instruction, and what each ending does next",
     {"Azure": (0, "Nothing: it hosts the container", "own", ""), "Databricks": (1, "Agent Framework interface for logging and serving; the loop stays ours", "own", ""),
      "AWS": (1, "AgentCore Runtime and Bedrock Agents exist; deliberately not used for the loop", "own", ""),
      "GCP (proposed)": (1, "Agent runtimes exist (ADK, Agent Engine); would not own the loop", "own", ""), "Open stack": (0, "Nothing", "own", "")}),
    ("Hosting",
     "A service entry point and settings loader",
     "Its container or job definition and its environment settings",
     {"Azure": (2, "Container Apps with revisions for canary releases", "ready", "container build"), "Databricks": (2, "Lakeflow jobs; Databricks Apps for a desk", "write", "job wrapper"),
      "AWS": (2, "ECS on Fargate", "ready", "container build"), "GCP (proposed)": (2, "Cloud Run", "ready", "container build"), "Open stack": (1, "You run the containers", "ready", "compose file")}),
    ("Model access",
     "A model port with an OpenAI-compatible client, retries, a breaker and an approved-model list",
     "Which models are approved, their prices, and sampling settings",
     {"Azure": (2, "API Management as gateway; Azure's model service", "ready", "OpenAI-compatible client"), "Databricks": (2, "Foundation Model APIs; AI Gateway where a serving endpoint is allowed", "ready", "OpenAI-compatible client (used)"),
      "AWS": (2, "Bedrock; AgentCore Gateway", "ready", "OpenAI-compatible client"), "GCP (proposed)": (2, "Vertex AI model catalogue; Apigee as gateway", "write", "check Vertex's compatible endpoint"),
      "Open stack": (0, "Nothing; LiteLLM is the open-source gateway you run", "ready", "OpenAI-compatible client")}),
    ("Tools",
     "A tool client over MCP: result size limits, side-effect classes, idempotency keys, identity on every call",
     "Its own tools: names, input and output shapes, which are read or irreversible, who may call each",
     {"Azure": (0, "Nothing specific; you host MCP servers", "ready", "MCP client"), "Databricks": (2, "Unity Catalog functions: typed, permissioned, audited", "write", "tool client over UC functions"),
      "AWS": (1, "AgentCore Gateway turns APIs into tools", "ready", "MCP client"), "GCP (proposed)": (0, "Nothing specific; you host MCP servers", "ready", "MCP client"), "Open stack": (0, "Nothing", "ready", "MCP client")}),
    ("Knowledge retrieval",
     "A retrieval port: the caller's rights applied before ranking, a source on every passage",
     "Its corpus, how it is cut into passages, how sources are linked",
     {"Azure": (1, "AI Search exists; not chosen, pgvector is", "ready", "pgvector"), "Databricks": (2, "Vector Search, synced from Delta", "write", "Vector Search adapter"),
      "AWS": (1, "Knowledge Bases exist; not chosen, pgvector is", "ready", "pgvector"), "GCP (proposed)": (1, "Vertex AI Vector Search and Search exist", "ready", "pgvector on Cloud SQL"), "Open stack": (0, "Nothing", "ready", "pgvector")}),
    ("State and records",
     "State stores: checkpoints, idempotency records, facts, conversation",
     "Its own entities and their migrations (for example the drafts and decisions it keeps)",
     {"Azure": (2, "Azure Database for PostgreSQL", "ready", "PostgreSQL store"), "Databricks": (2, "Delta tables in Unity Catalog", "write", "Delta store"),
      "AWS": (2, "RDS for PostgreSQL", "ready", "PostgreSQL store"), "GCP (proposed)": (2, "Cloud SQL or AlloyDB for PostgreSQL", "ready", "PostgreSQL store"), "Open stack": (1, "You run PostgreSQL", "ready", "PostgreSQL store")}),
    ("Long waits and approvals",
     "Approval and escalation machinery: durable waits, expiry, a decision validated by a rule, a queue for a person",
     "Who may decide, how long a decision stays valid, and which conditions escalate (all from its specification)",
     {"Azure": (1, "Durable Functions and Logic Apps exist; not chosen", "ready", "DBOS workflows"), "Databricks": (1, "Lakeflow Jobs run steps; a wait is a job that ends and restarts", "write", "job per decision"),
      "AWS": (1, "Step Functions exist; not chosen", "ready", "DBOS workflows"), "GCP (proposed)": (1, "Cloud Workflows exists", "ready", "DBOS on Cloud SQL"), "Open stack": (0, "Nothing; Temporal is the open-source choice", "ready", "Temporal")}),
    ("Identity and access",
     "An identity carried into every tool call; the far end verifies it",
     "Its scopes, and which rows each caller may see or change",
     {"Azure": (2, "Entra ID; managed identity", "ready", "token exchange"), "Databricks": (2, "Unity Catalog service principal and workspace sign-in", "write", "workspace identity"),
      "AWS": (2, "Cognito and IAM", "ready", "signing helpers"), "GCP (proposed)": (2, "Cloud IAM; Identity Platform", "write", "Google identity"), "Open stack": (0, "Nothing; Keycloak is the open-source choice", "ready", "token check")}),
    ("Secrets",
     "A secrets port: a reference becomes a secret only at the moment of use",
     "Nothing but the names of the secrets it needs",
     {"Azure": (2, "Key Vault", "write", "Key Vault adapter"), "Databricks": (2, "Secret scopes", "write", "secret scope adapter"),
      "AWS": (2, "Secrets Manager and Parameter Store", "ready", "AWS adapter"), "GCP (proposed)": (2, "Secret Manager", "write", "Secret Manager adapter"), "Open stack": (0, "Nothing", "ready", "environment settings")}),
    ("Policy and guardrails",
     "Rule positions (before the model, after it, before a tool), output rules, redaction",
     "Its own rules: what it refuses, which checks a draft must pass (for example a number must equal a tool's number)",
     {"Azure": (1, "Content Safety filters: generic", "own", ""), "Databricks": (1, "AI Gateway safety and PII options: generic", "own", ""),
      "AWS": (1, "Bedrock Guardrails: generic", "own", ""), "GCP (proposed)": (1, "Vertex safety filters and Model Armor: generic", "own", ""), "Open stack": (0, "Nothing", "own", "")}),
    ("Telemetry",
     "One span per call, one identifier per task, redaction before export, standard span names",
     "Which domain facts it records, and the labels its dashboards need",
     {"Azure": (2, "Application Insights", "ready", "Azure Monitor distro"), "Databricks": (2, "MLflow tracing", "write", "MLflow exporter"),
      "AWS": (2, "CloudWatch; X-Ray", "ready", "OpenTelemetry export"), "GCP (proposed)": (2, "Cloud Trace and Logging", "ready", "OpenTelemetry export"), "Open stack": (1, "You run Langfuse or a collector", "ready", "OpenTelemetry export")}),
    ("Evaluation",
     "AgentTwin (worlds, scenarios, simulated users), the evaluation library, the four gates, the catalogues",
     "Its world, its scenarios, its labelled cases and its domain checks",
     {"Azure": (1, "Foundry evaluations: model-level", "own", ""), "Databricks": (1, "Agent Evaluation and MLflow evaluation: model-level", "own", ""),
      "AWS": (1, "Bedrock evaluations: model-level", "own", ""), "GCP (proposed)": (1, "Gen AI evaluation service: model-level", "own", ""), "Open stack": (0, "Nothing", "own", "")}),
    ("Configuration and release",
     "A profile loader: decisions, thresholds and accepted gaps resolved from a stack file",
     "Its profile answers and its own thresholds; it never restates the specification's numbers",
     {"Azure": (2, "App Configuration", "write", "config adapter"), "Databricks": (2, "Bundle variables and job parameters", "write", "bundle adapter"),
      "AWS": (2, "AppConfig", "ready", "AWS adapter"), "GCP (proposed)": (1, "A managed config service or Git", "write", "config adapter"), "Open stack": (0, "Nothing", "ready", "typed settings")}),
    ("Cost",
     "A per-task meter, a price table, a ceiling that stops work",
     "Its ceiling per task and what counts as a successful task",
     {"Azure": (1, "Cost Management: by resource, not by task", "own", ""), "Databricks": (1, "Billing system tables: by resource, not by task", "own", ""),
      "AWS": (1, "Cost Explorer: by resource, not by task", "own", ""), "GCP (proposed)": (1, "Billing export: by resource, not by task", "own", ""), "Open stack": (0, "Nothing", "own", "")}),
]

LEVEL_TXT = {2: "carries most of it", 1: "carries part of it", 0: "nothing for this"}
SHARED_TXT = {"ready": "adapter ready", "write": "adapter still to write", "own": "shared asset is the whole answer"}


def meter(level, shared):
    """Three boxes: platform, shared assets, the agent. Shade shows who carries the concern."""
    plat = {2: "#A3B5DF", 1: "#d9e1f2", 0: "#fff"}[level]
    shr = {"ready": "#FFD98A", "own": "#FFD98A", "write": "#fbeccb"}[shared]
    box = lambda c: f'<rect width="16" height="14" rx="3" fill="{c}" stroke="#1a1a1a" stroke-width="1.3"/>'
    return (f'<svg width="62" height="16" viewBox="0 0 62 16" aria-hidden="true">'
            f'<g transform="translate(1,1)">{box(plat)}</g><g transform="translate(21,1)">{box(shr)}</g><g transform="translate(41,1)">{box("#E6BFD2")}</g></svg>')


def cut_panel(plat):
    out = ('<div class="tw"><table class="map cut"><tr><th>Concern</th><th>Who carries it</th>'
           '<th>X · The platform gives out of the box</th><th>Y · Shared assets we reuse</th><th>Z · Each agent writes</th></tr>')
    for name, shared, agent, per in CUT:
        level, box, status, note = per[plat]
        out += (f'<tr><td class="con">{E(name)}</td><td>{meter(level, status)}<span class="st">platform {LEVEL_TXT[level]}</span></td>'
                f'<td>{E(box)}</td><td>{E(shared)}<span class="st">{SHARED_TXT[status]}' + (f": {E(note)}" if note else "") + f'</span></td><td class="ver">{E(agent)}</td></tr>')
    return out + "</table></div>"


def cut_section():
    tabs = "".join(f'<button type="button" class="tab" data-p="{i}">{E(p)}</button>' for i, p in enumerate(PLATFORMS))
    panels = "".join(f'<div class="panel" data-p="{i}"><h3>{E(p)}</h3>{cut_panel(p)}</div>' for i, p in enumerate(PLATFORMS))
    tally = ""
    for p in PLATFORMS:
        c = [per[p][2] for _, _, _, per in CUT]
        tally += f"<tr><td><b>{E(p)}</b></td><td>{sum(1 for _, _, _, per in CUT if per[p][0] == 2)}</td><td>{sum(1 for _, _, _, per in CUT if per[p][0] == 0)}</td><td>{c.count('ready')}</td><td>{c.count('write')}</td></tr>"
    return f"""<h2>The same map, cut three ways</h2>
<p>The first table says which product fills each concern. This one asks a different question for each platform: for every concern, how much does the platform hand you, how much comes from assets we already share across all our agents, and what is left that every single agent must write for itself.</p>
<div class="steps"><div><b>X · The platform</b>What the cloud or data platform gives out of the box. Different on every stack.</div>
<div><b>Y · Shared assets</b>The harness library, its adapters, AgentTwin, the evaluation library, the catalogues. Written once, reused by every agent. Where a platform has no adapter yet, that is the work of the stack, not of any agent.</div>
<div><b>Z · Each agent</b>Its specification, tools, rules, world, scenarios and thresholds. The same on every platform, and the only part that is yours.</div></div>
<p class="legend"><span>Boxes show who carries the concern: platform, shared assets, agent. A darker first box means the platform carries more.</span></p>
<div class="tabs">{tabs}</div>
{panels}
<h3>The count, per platform</h3>
<div class="tw"><table class="map" style="min-width:0"><tr><th>Platform</th><th>Concerns the platform mostly carries (of {len(CUT)})</th><th>Concerns it gives nothing for</th><th>Adapters ready in the shared library</th><th>Adapters still to write</th></tr>{tally}</table></div>
<div class="box"><b>What this shows.</b> Z does not change with the platform. Y shrinks or grows with the stack: Azure, AWS and the open stack have most adapters; Databricks and GCP need the library to grow before an agent can run there on platform services. X is where platforms differ most, and it is the column to read when choosing, but a platform that carries a concern does not remove the need for the agent to write its own rules and checks.</div>
<p class="note">The levels in this view are our reading of each platform, not a measurement. The adapter status comes from the shared library as of 20 November 2026; GCP and Databricks adapters do not exist yet. Platform product lists change quickly.</p>
<script>
(function(){{var t=document.querySelectorAll('.tab'),p=document.querySelectorAll('.panel');
function show(i){{t.forEach(function(b,k){{b.classList.toggle('on',k==i)}});p.forEach(function(d,k){{d.style.display=(k==i)?'block':'none'}})}}
t.forEach(function(b,k){{b.addEventListener('click',function(){{show(k)}})}});if(t.length){{show(0)}}}})();
</script>"""

TAG = {"c": ("cloud", "Cloud service"), "o": ("open", "Open source"), "b": ("own", "Built by us")}
STATUS = {R: "built and run", D: "decided, not built", P: "proposed, no stack file"}


def cell(c, gcp=False):
    kind, text, status = c
    cls, label = TAG[kind]
    return (f'<td class="gcp">' if gcp else "<td>") + f'<span class="tag {cls}">{label}</span><br>{E(text)}<span class="st">{STATUS[status]}</span></td>'


def table():
    head = ["Concern family", "Concern", "Azure", "Databricks", "AWS", "GCP (proposed)", "Open stack", "Verdict: what to select"]
    out = '<div class="tw"><table class="map"><tr>' + "".join(f"<th>{E(h)}</th>" for h in head) + "</tr>"
    for fam, rows in FAMILIES:
        for i, (name, what, az, db, aw, gc, op, verdict) in enumerate(rows):
            out += "<tr>"
            if i == 0:
                out += f'<td class="fam" rowspan="{len(rows)}">{E(fam)}</td>'
            out += f'<td class="con">{E(name)}<span class="st">{E(what)}</span></td>'
            out += cell(az) + cell(db) + cell(aw) + cell(gc, True) + cell(op)
            out += f'<td class="ver">{E(verdict)}</td></tr>'
    return out + "</table></div>"


def mindmap():
    """Centre node, seven family nodes round it, each with its concerns."""
    W, H = 1000, 700
    cx, cy = W / 2, H / 2
    pos = [(150, 100), (500, 70), (850, 100), (880, 350), (850, 600), (500, 630), (150, 600)]
    fills = ["var(--peri-wash)", "var(--butter-wash)", "var(--rose-wash)"]
    svg = [f'<svg class="mm" viewBox="0 0 {W} {H}" role="img" aria-label="Agent harness: seven families of concerns">']
    for (x, y) in pos[:len(FAMILIES)]:
        svg.append(f'<line x1="{cx}" y1="{cy}" x2="{x}" y2="{y}" stroke="#1a1a1a" stroke-width="1.5"/>')
    svg.append(f'<ellipse cx="{cx}" cy="{cy}" rx="105" ry="48" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>')
    svg.append(f'<text x="{cx}" y="{cy - 4}" text-anchor="middle" font-size="24">Agent harness</text>')
    svg.append(f'<text x="{cx}" y="{cy + 20}" text-anchor="middle" font-size="14">17 ports, one binding each</text>')
    for k, ((fam, rows), (x, y)) in enumerate(zip(FAMILIES, pos)):
        names = [r[0] for r in rows]
        h = 34 + 19 * len(names)
        w = 230
        svg.append(f'<rect x="{x - w / 2}" y="{y - h / 2}" width="{w}" height="{h}" rx="14" fill="{fills[k % 3]}" stroke="#1a1a1a" stroke-width="1.5"/>')
        svg.append(f'<text x="{x}" y="{y - h / 2 + 22}" text-anchor="middle" font-size="18">{E(fam)}</text>')
        for j, n in enumerate(names):
            svg.append(f'<text x="{x}" y="{y - h / 2 + 42 + 19 * j}" text-anchor="middle" font-size="14">{E(n)}</text>')
    svg.append("</svg>")
    return "".join(svg)


def page():
    legend = ('<p class="legend"><span><span class="tag cloud">Cloud service</span> the platform sells it</span>'
              '<span><span class="tag open">Open source</span> a product you can run anywhere</span>'
              '<span><span class="tag own">Built by us</span> a few lines of our own, identical on every stack</span></p>'
              f'<p class="legend"><span><b>built and run</b>: it has run in a real build</span><span><b>decided, not built</b>: chosen in a stack file, no running agent yet</span>'
              f'<span><b>proposed</b>: written for this page, no stack file</span></p>')
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/agent-harness/">Agent Harness</a> › Architecture map</p>
<p class="eyebrow" style="margin-top:22px">AI · Agent Harness</p>
<h1>Agent harness architecture map: what fills each concern, on every stack</h1>
<p class="lede">An agent harness is the same set of concerns whatever you build it on: a loop, a model door, tools, state, waits, identity, records, configuration. What changes between Azure, Databricks, AWS, GCP and an open-source stack is only the product that fills each one. This page puts all of them on one view, with a verdict on what to pick.</p>
<p class="note">Written 20 November 2026 from the open stack files, one per platform. Open Stack is the only column that has run end to end. Azure and AWS are decided in writing and not yet built. Databricks is part built. GCP has no stack file at all: that column is a proposal, shaded grey, to be checked before anyone relies on it. Product names and features change; check current documentation.</p>
<h2>The map</h2>
{mindmap()}
<h2>The table</h2>
<p>One row per concern. Read across to see what each stack uses. Read the last column for what to select.</p>
{legend}
{table()}
{cut_section()}
<h2>How to decide, in three rules</h2>
<div class="steps"><div><b>1 · Build the middle</b>The loop, limits, cost meter, policy rules and start-once triggers are the same few lines on every stack. Writing them is cheaper than adapting a product, and they must see your task.</div>
<div><b>2 · Lean on the cloud you are on</b>For hosting, identity, secrets, telemetry and configuration, take the platform's own service. It is already approved, billed and audited there.</div>
<div><b>3 · Keep one open default for the rest</b>PostgreSQL, a library for durable waits, MCP for tools, OpenTelemetry for records. They run on any cloud, so moving stacks is a change of adapter, not of code.</div></div>
<div class="box"><b>Why this works.</b> Every product sits behind a port: a small interface the harness owns. A stack is a file that says which product fills each port. Changing cloud means changing that file and writing one adapter per changed port. The agent, its specification and its tests stay put.</div>
<h2>What to check before relying on this</h2>
<ul><li><b>The GCP column.</b> It is our proposal, not a tested stack. Confirm each service against Google's current documentation and region availability.</li>
<li><b>Azure and AWS cells.</b> They record decisions. Few have been built against the real service.</li>
<li><b>Databricks limits.</b> On the free edition we found Vector Search and custom model serving refused, which also rules out AI Gateway on a custom endpoint. A paid workspace may differ.</li>
<li><b>Prices and tiers.</b> Not shown here on purpose. Get them from each vendor for your volume.</li></ul>
<h2>Where to go next</h2>
<ul><li><a href="/learn/agent-harness/">Agent Harness: the course</a>, concern by concern.</li>
<li><a href="/learn/agent-harness-databricks/">The agent harness on Databricks</a> and <a href="/learn/agent-harness-aws/">on AWS</a>.</li>
<li><a href="/learn/ai-gateways/">AI gateways: which one to use</a>, the model-access row in depth.</li>
<li><a href="https://dataagentsai.github.io/ai-harness-catalog/">Open spec: AI Harness Catalog</a>, where the ports are defined.</li></ul>"""
    desc = ("One map of the agent harness: every concern against Azure, Databricks, AWS, GCP and an open-source stack, "
            "what is built and what is only decided, and a verdict on what to select for each.")
    return wb.page("Agent harness architecture map: what fills each concern", desc, URL, body,
                   ds.CSS + CSS + ds.ld("Agent harness architecture map", desc, URL, [("Agent Harness", "/learn/agent-harness/"), ("Architecture map", "/learn/agent-harness-stack-map/")]))


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page())
    print("stack map ->", OUT)


if __name__ == "__main__":
    main()
