"""The agent harness on AWS: one page at /learn/agent-harness-aws/.

    python3 _guides/agent_harness_aws.py && python3 _site/nav.py && python3 _site/seo.py

The AWS twin of the tutorial's Azure pages (arch-azure, tech). Same 22 concerns, same ids and
families as ~/agent-harness-tutorial/pages_tech.py; only the binding changes. Example is a
generic tyre manufacturer. Shell, CSS and drawing helpers come from spec_driven.py.
The x/y/z splits are judgements, labelled so on the page. AWS service status was checked from
memory (to mid 2026); newer services are marked "considered, check current status".
"""
import re
import sys
from html import escape as E
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import spec_driven as SD  # noqa: E402

I, WASH, INK = SD.I, SD.WASH, SD.INK
svg, box, t, arrow, fig = SD.svg, SD.box, SD.t, SD.arrow, SD.fig

ROOT = SD.ROOT
OUT = ROOT / "learn" / "agent-harness-aws" / "index.html"
TITLE = "The agent harness on AWS"
DESC = ("The same agent harness, specs and tests as on Azure, bound to AWS: the big picture for a tyre manufacturer "
        "group, every one of the 22 concerns mapped to an AWS service, open source or our own code, and the open decisions.")
URL = "https://cleandataengineering.ai/learn/agent-harness-aws/"
AH = "/learn/agent-harness/"

CSS = SD.CSS + """
  .aw-mark { display:inline-block; font-size:11.5px; font-weight:700; border:1.2px solid var(--ink); border-radius:10px; padding:0 7px; margin-right:4px; white-space:nowrap; }
  .aw-mark.use { background:#C9F2E3; } .aw-mark.plan { background:#FFF0C2; } .aw-mark.list { background:#fff; } .aw-mark.no { background:#F8DDE9; }
  .aw-fam td { background:var(--surface-2); font-family:var(--hand); font-size:22px; }
  .sd-table td ul { margin:0; padding-left:0; list-style:none; } .sd-table td li { margin:2px 0; }
  .sd-table td small { color:var(--muted); }
  .aw-key { font-size:14px; color:var(--muted); margin:8px 0; }
  .sd-table.wide td { font-size:14px; } .sd-table.wide td:first-child { min-width:150px; }
"""

# ------------------------------------------------------------------ the 22 concerns, bound to AWS
# (id, name, family, does, aws [(name, mark, why)], oss [(name, mark, why)], ours, azure, why, (x, y, z))
MARK = {"use": "use", "plan": "planned", "list": "considered", "no": "not used"}
C = [
 # ---- Think
 ("L1", "Context assembly", "Think", "What the model sees each turn, built in one place, within a budget.",
  [("Bedrock Prompt Management", "no", "stores prompts, does not assemble a turn")],
  [("Jinja templates", "use", "fixed replies only")],
  "Our assembler: cache-friendly order, fencing, trimming from the middle, transcript check; prompts in Git",
  "Our assembler + prompts in Git",
  "No product on any cloud assembles a turn the way a regulated agent needs, so we code it once.", (5, 60, 35)),
 ("L2", "Model invocation", "Think", "Every model call goes through one door.",
  [("Amazon Bedrock, Converse API", "use", "Claude, Llama, Mistral, Nova behind one API"),
   ("Cross-region inference profiles", "use", "keep inside the India geography where offered; check per model"),
   ("Bedrock Intelligent Prompt Routing", "no", "picks the model per prompt; not deterministic"),
   ("Bedrock AgentCore Gateway (inference endpoint)", "plan", "AWS's managed AI gateway: one door to models, tools and agents; fallback + circuit breaker (Oct 2026); token rate limits"),
   ("Bedrock application inference profiles", "use", "one per agent, tagged, so cost and quota are per agent")],
  [("LiteLLM proxy on ECS Fargate", "list", "fallback gateway if AgentCore Gateway lacks a rule we need, or for non-AWS models"),
   ("Pydantic AI", "use", "model layer only")],
  "Our gateway policy: allow-list per job, token budget, one retry budget, token metric per agent",
  "APIM AI gateway → Foundry Models",
  "AgentCore Gateway is AWS's AI gateway, the same job APIM's AI gateway does on Azure: one governed door with identity, rate and token limits, fallback and logging. Our policy (allow-list per job, budgets) sits on top as config. Check region availability and token-limit features before go-live. The agent never holds a provider key.", (55, 35, 10)),
 ("L4", "Control loop", "Think", "Plan, act, check, with step and no-progress limits.",
  [("Bedrock Agents", "no", "the platform would own the loop"),
   ("Bedrock AgentCore Runtime", "list", "could host our own loop; check current status")],
  [("Strands Agents", "no", "AWS's open SDK; fine for simple agents"), ("LangGraph", "no", "workflow-shaped agents only"),
   ("Claude Agent SDK", "no", "Claude-only, loop hidden")],
  "Hand-written loop, about 400 lines; budgets of 12 steps, 60 s and a cost cap per turn",
  "Hand-written loop (same code)",
  "Agents that touch orders, warranties and money need every step testable and checks at exact positions. Our own loop runs on any model and any cloud.", (0, 80, 20)),
 ("L5", "State & memory", "Think", "What is kept, for how long, and for whom.",
  [("Aurora PostgreSQL Serverless v2", "use", "HA, backups, IAM login, scales to near zero in dev"),
   ("DynamoDB", "list", "not picked"), ("ElastiCache for Valkey", "list", "caches only"),
   ("AgentCore Memory", "list", "check current status")],
  [("psycopg + pool", "use", "driver")],
  "5 agent tables + DBOS state in the same database; retention and erase per person",
  "Azure Database for PostgreSQL",
  "One managed store that also holds the approval engine and, later, pgvector: no extra infrastructure.", (40, 45, 15)),
 ("18", "Knowledge & retrieval", "Think", "Finds sourced passages, filtered by what this user may see.",
  [("pgvector on the same Aurora", "plan", "chosen"), ("Bedrock Knowledge Bases", "list", "managed RAG; less control of filters"),
   ("OpenSearch Serverless", "list", "if the corpus outgrows pgvector"), ("S3 Vectors", "list", "cheap cold vectors; check current status")],
  [("pgvector", "plan", "chosen"), ("Qdrant on ECS", "list", "alternative")],
  "Entitlement filter as SQL: a plant engineer sees machine manuals, a dealer sees only their own orders and price lists",
  "pgvector on Azure PostgreSQL",
  "One store, one backup, one access model; the entitlement check is just a SQL filter.", (45, 30, 25)),
 # ---- Act
 ("CH", "Channels & human desk", "Act", "How dealers, customers and staff reach the agent, and how a person takes over with the full history.",
  [("AWS End User Messaging", "plan", "SMS and WhatsApp"), ("Amazon SES", "plan", "email"),
   ("Amazon Connect", "plan", "contact centre, chat and hand-off to a person"), ("API Gateway WebSocket", "list", "push replies to the window")],
  [("Chatwoot", "plan", "web chat + desk if there is no contact centre"), ("A Next.js window alone", "list", "six more things to build")],
  "Our chat page and desk API; one conversation id across channels",
  "Communication Services, Bot Service, Chatwoot",
  "If the company already runs a contact centre, hand off into it (Connect). Otherwise Chatwoot gives the desk without building one.", (50, 35, 15)),
 ("L3", "Tool layer", "Act", "Actions through typed tools, checked before they run.",
  [("MCP servers on ECS Fargate or Lambda", "use", "one server per system of record"),
   ("Bedrock AgentCore Gateway", "plan", "the same gateway fronts our MCP tool servers: one door for tools and models")],
  [("MCP Python SDK", "use", "client + servers"), ("FastMCP", "list", "")],
  "Gating before every call, idempotency keys, size caps, argument checks with jsonschema",
  "MCP servers on Container Apps",
  "The tool protocol is open (MCP), so the servers move clouds unchanged. The gating that protects orders, prices and warranties is ours.", (25, 35, 40)),
 ("L6", "I/O contracts", "Act", "Typed inputs and outputs at every edge.",
  [("API Gateway request validation", "plan", "reject bad shapes at the edge")],
  [("Pydantic", "use", ""), ("JSON Schema", "use", ""), ("SAP OData / BAPI shapes", "plan", "typed at the ERP adapter")],
  "Frozen Pydantic models everywhere; MCP structured output",
  "Pydantic + jsonschema (same code)",
  "Contracts are code, not cloud. SAP and dealer-system shapes are typed once at their adapters.", (10, 50, 40)),
 ("L8", "Concurrency & flow", "Act", "Who gets served first when load spikes.",
  [("Amazon SQS FIFO", "plan", "one message group per conversation keeps order"),
   ("API Gateway usage plans", "use", "rate limits per client"), ("Bedrock quotas", "use", "tokens per minute, the real ceiling")],
  [("Own semaphores", "list", ""), ("LiteLLM limits", "list", "only if LiteLLM is the gateway")],
  "One turn per conversation (ledger row), priority classes (plant breakdowns before marketing), honest shedding",
  "Service Bus + APIM rate limit",
  "AWS gives the queue and the limits. Which request waits, and what we tell the person, is ours.", (50, 35, 15)),
 ("17", "Agent-to-agent", "Act", "Agents hand work to agents through typed, bounded, traced hand-offs.",
  [("A2A over HTTPS behind API Gateway", "plan", ""), ("AgentCore A2A support", "list", "check current status")],
  [("A2A SDK", "plan", ""), ("Backstage", "list", "registry")],
  "Registry in Git: who, which version, owner, autonomy level",
  "A2A endpoints + API Center",
  "A2A is an open protocol, so hand-offs work across clouds. The registry stays a file we own.", (20, 60, 20)),
 ("PS", "Performance & scalability", "Act", "Fast enough at the 95th percentile; more servers when load rises; the model quota is the real limit.",
  [("ECS Fargate service auto scaling", "use", ""), ("Bedrock prompt caching", "use", "cheaper, faster repeated context"),
   ("Distributed Load Testing on AWS", "plan", "AWS solution"), ("Bedrock provisioned throughput", "list", "only at steady high volume")],
  [("k6 / Locust", "list", "")],
  "Per-turn time budget (60 s), cache-friendly context order",
  "Container Apps autoscaling",
  "Servers are stateless and scale out; the model quota is what to plan and load-test.", (55, 35, 10)),
 # ---- Control
 ("L16", "Identity & authz", "Control", "Who is asking, and whose authority the agent acts with.",
  [("Amazon Cognito", "plan", "dealer, fleet and consumer sign-in, or federate the dealer portal"), ("IAM Identity Center", "use", "staff sign-in"),
   ("IAM roles for tasks", "use", "no keys in code"), ("Secrets Manager + KMS", "use", ""),
   ("Amazon Verified Permissions", "list", "Cedar policies for fine-grained rules")],
  [("PyJWT", "use", "local token check"), ("Keycloak", "list", "")],
  "Principal → dealer, customer or staff identity; on-behalf-of: the agent acts with the user's rights, never its own",
  "Entra ID, managed identity, Key Vault",
  "Checking a token is local and cloud-neutral. Ports make leaving Cognito a configuration change.", (70, 20, 10)),
 ("PV", "Privacy & data protection", "Control", "Personal data of dealers, fleet drivers and consumers used only for this case, kept in its region (India or EU), masked, and forgotten on request.",
  [("Comprehend PII", "plan", "names, phone, ids in text"),
   ("Amazon Macie", "plan", "finds personal data in S3"), ("Mumbai, Hyderabad; Frankfurt, Ireland", "use", "India data in India, EU data in the EU"),
   ("KMS, PrivateLink", "use", "")],
  [("Presidio", "list", "Aadhaar, PAN, GSTIN and vehicle numbers need custom recognisers anyway")],
  "redact() in telemetry (Aadhaar, PAN, phone, vehicle number), no_pii_echo rule, forget() + retention per the DPDP Act and GDPR",
  "AI Language PII + India regions",
  "Residency and encryption come from AWS. Which data a turn may use, masking and erasure are domain rules we code once.", (45, 40, 15)),
 ("L7", "Policy enforcement", "Control", "Guardrails on the way in and on the way out.",
  [("Bedrock Guardrails", "use", "prompt attacks, harmful content, denied topics, PII"),
   ("ApplyGuardrail API", "use", "the same checks on any model and on tool results"),
   ("Contextual grounding check", "plan", "answers must stay on the sources"),
   ("Automated Reasoning checks", "list", "check current status")],
  [("Llama Prompt Guard 2", "plan", "small local classifier"), ("NeMo Guardrails", "no", "wants to own the loop"),
   ("Llama Guard", "no", "an LLM, too slow")],
  "Our positioned rules (30 checks): no price or warranty promised outside policy, no order changed without OK, a dealer's own records only",
  "Content Safety + our rules",
  "We own every position and every rule; every check that protects money or a customer is ours. AWS supplies detectors behind one port.", (40, 40, 20)),
 ("L10", "Failure handling", "Control", "Typed failures, fallbacks, undo paths, honest messages.",
  [("Cross-region inference", "use", "spreads load when a region is busy"), ("ALB / ECS health checks", "use", "")],
  [("tenacity", "list", ""), ("Own resilience wrapper", "use", "one retry budget per turn")],
  "Typed failures, ledger abandon-and-retry, an honest message instead of a guess",
  "APIM backend pools + own wrapper",
  "Retries without a budget hide outages. One retry budget per turn is ours on any cloud.", (25, 55, 20)),
 ("L14", "Human-in-the-loop", "Control", "Approvals and hand-offs the agent cannot grant itself.",
  [("Step Functions task tokens", "list", "a managed wait; one more service to run"),
   ("Amazon Connect", "plan", "hand-off to a person with history")],
  [("DBOS", "use", "durable waits in our own Aurora"), ("Temporal", "list", "")],
  "Approval and escalation tables, desk API, approval cards to staff",
  "DBOS on PostgreSQL (same code)",
  "A warranty or order approval must survive restarts. DBOS keeps it in the database we already run, so it moves clouds unchanged.", (20, 55, 25)),
 ("AV", "Availability & disaster recovery", "Control", "A lost server or zone goes unnoticed; a lost region is rebuilt from code and backups.",
  [("Multi-AZ ECS + Aurora Multi-AZ", "plan", ""), ("Aurora Global Database", "list", "Mumbai ↔ Hyderabad; EU pair for Europe"),
   ("Route 53 health checks", "plan", ""), ("AWS Backup", "plan", "")],
  [("Terraform or AWS CDK", "use", "infrastructure as code")],
  "Stateless servers + durable state; a rebuild drill",
  "Zone redundancy, Front Door, Bicep",
  "Two Indian regions make a DR pair without data leaving the country; European data pairs inside the EU.", (65, 25, 10)),
 # ---- See
 ("L11", "Observability", "See", "Traces, metrics and alerts for every step.",
  [("CloudWatch + Application Signals", "use", "via the ADOT collector"), ("AWS X-Ray", "use", "traces"),
   ("Bedrock model invocation logging", "use", "to S3, for evidence"),
   ("CloudWatch generative AI observability", "list", "check current status"),
   ("Managed Prometheus + Grafana", "plan", "")],
  [("OpenTelemetry", "use", "behind one helper"), ("Langfuse", "list", "")],
  "Spans per step with GenAI attributes, personal data redacted before export, alert rules as code",
  "OpenTelemetry → App Insights",
  "OpenTelemetry keeps the code cloud-neutral; only the exporter changes.", (55, 35, 10)),
 ("L9", "Determinism & replay", "See", "A past decision can be re-run and explained.",
  [("(nothing on AWS)", "list", "invocation logs help, but do not replay")],
  [("VCR.py", "list", ""), ("Own recorder", "use", "")],
  "Run record + cassettes + config fingerprint",
  "Own recorder (same code)",
  "\"Why did the agent say that to this dealer?\" needs a replay. No cloud offers it, so it is ours.", (0, 85, 15)),
 ("L13", "Cost accounting", "See", "Spend measured per unit of business work.",
  [("Bedrock application inference profiles", "use", "one tagged profile per agent = cost per agent"),
   ("AWS Budgets", "use", ""), ("Cost Explorer", "use", ""), ("CUR 2.0 data exports", "plan", "")],
  [("Langfuse cost", "list", ""), ("Own meter", "use", "")],
  "Meter per turn and per case (cost per warranty claim triaged), hard budget stop",
  "Cost Management + APIM token metric",
  "AWS tells you cost per agent; only we know cost per warranty claim or per dealer order.", (35, 55, 10)),
 # ---- Change
 ("L12", "Eval harness", "Change", "Golden sets and graders that gate every release.",
  [("Bedrock model evaluation", "plan", "LLM-as-judge and human review"), ("Bedrock RAG evaluation", "plan", ""),
   ("AgentCore Evaluations", "list", "check current status")],
  [("AgentTwin, pytest, pydantic-evals", "use", ""), ("promptfoo, PyRIT", "plan", "red team")],
  "Golden sets owned by quality, warranty and dealer-service leads, hard graders, 4 CI gates, model selection run",
  "Foundry evaluation + AgentTwin",
  "The pretend dealer network and plant (AgentTwin) and the hard graders are the same on any cloud; AWS judges are one plug-in.", (25, 45, 30)),
 ("L15", "Release & config", "Change", "Prompt, model and policy versioned and rolled back together.",
  [("AWS AppConfig", "use", "kill switch, limits, model per job"), ("ECS blue/green deployments", "use", ""),
   ("Amazon ECR", "use", ""), ("CodePipeline", "list", "or GitHub Actions + OIDC")],
  [("GitHub Actions + OIDC", "use", ""), ("OpenFeature", "list", "")],
  "One release bundle: prompt + model + policy + config fingerprint",
  "App Configuration + revisions",
  "AppConfig is a close match for App Configuration; the bundle and rollback rule are ours.", (50, 35, 15)),
]
FAMILIES = [("Think", "how the agent decides"), ("Act", "how it reaches people and systems"),
            ("Control", "what keeps it safe"), ("See", "what we can see and prove"), ("Change", "how it changes safely")]
assert len(C) == 22


# ------------------------------------------------------------------ drawing: the big picture
def cell(n, x, y, w, h, title, sub="", fill="#fff", dark=False):
    s = box(n, x, y, w, h, fill, r=10)
    if dark:
        s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{I.PAL["lav"]}" '
             f'stroke="{INK}" stroke-width="2.4" filter="url(#rough{n})"/>')
    cy = y + h / 2 + (-3 if sub else 5)
    s += t(x + w / 2, cy, E(title), 12.5, bold=True)
    if sub:
        s += t(x + w / 2, cy + 15, E(sub), 10.5, fill="#444")
    return s


def band(n, x, y, w, label, rows, fill):
    out = t(x, y + 14, E(label), 17, hand=True, anchor="start")
    y += 22
    h0 = y
    for r in rows:
        k = len(r)
        cw = (w - 16 - (k - 1) * 8) / k
        for i, c in enumerate(r):
            title, sub = c[0], (c[1] if len(c) > 1 else "")
            out += cell(n, x + 8 + i * (cw + 8), y + 8, cw, 44, title, sub, "#fff", dark=len(c) > 2)
        y += 52
    out = (f'<rect x="{x}" y="{h0}" width="{w}" height="{y - h0 + 8}" rx="14" fill="{fill}"/>') + out
    return out, y + 18


LIFE = [("Idea & risk tier", "is AI the right fix?"), ("Build", "GitHub Actions"), ("Evaluate", "Bedrock + AgentTwin"),
        ("Red-team", "PyRIT, promptfoo"), ("Approve", "business owner"), ("Release", "ECS blue/green"),
        ("Monitor", "CloudWatch"), ("Learn", "misses → golden set")]
GOV = [("Organizations", "SCPs, Control Tower"), ("CloudTrail", "who did what"), ("Security Hub", "+ GuardDuty"),
       ("Identity Center", "access reviews"), ("Residency", "India + EU regions"), ("DPDP + GDPR", "consent, erasure"),
       ("Owner & risk tier", "in the registry"), ("AI council", "signs off high risk")]
ROWS = [
    ("End users · who asks", [[("Dealers", "Cognito / portal"), ("Fleet customers", "Cognito"), ("Consumers", "Cognito"),
                               ("Plant & quality", "Identity Center"), ("Sales & service", "Identity Center")]], WASH["sky"]),
    ("Channels · where they ask", [[("Dealer portal chat", "Chatwoot or own"), ("WhatsApp", "End User Messaging"),
                                    ("Email", "Amazon SES"), ("Contact centre", "Amazon Connect"), ("Staff chat", "Teams or Slack")]], WASH["mint"]),
    ("Front door · checks every request", [[("Edge", "CloudFront + WAF"), ("Hidden orders?", "Bedrock Guardrails"),
                                            ("Personal data?", "Comprehend PII"), ("In scope?", "our router rules"),
                                            ("Fair share", "API Gateway limits")]], WASH["butter"]),
    ("Orchestration · on ECS Fargate", [[("Router", "our code"), ("A2A hand-off", "A2A over HTTPS"),
                                         ("Agent registry", "Git + owner")]], WASH["lilac"]),
    ("Vertical agents · tyre manufacturer · one ECS service each",
     [[("Dealer assistant", "stock, price, orders: answers", 1), ("Warranty claim triage", "drafts for warranty desk"),
       ("Plant maintenance", "suggests, from manuals")],
      [("Quality deviation", "drafts root cause note"), ("B2B order assistant", "acts after OK"),
       ("Fleet tyre advisor", "answers, from telematics")]], WASH["rose"]),
    ("Horizontal assets · built once on AWS, reused by every agent",
     [[("Model gateway", "AgentCore Gateway"), ("Knowledge", "pgvector on Aurora"), ("Memory & state", "Aurora PostgreSQL"),
       ("Tool / MCP hub", "MCP on Fargate"), ("Channels", "Connect, SES, EUM"), ("Identity", "Cognito, IAM, KMS")],
      [("Guardrails", "Bedrock + our rules"), ("Human desk", "DBOS + Connect"), ("Observability", "CloudWatch, X-Ray"),
       ("Cost control", "profiles, Budgets"), ("Eval library", "Bedrock, AgentTwin"), ("Release", "AppConfig, ECR")]], WASH["peri"]),
    ("Systems of record · via MCP and PrivateLink",
     [[("SAP S/4HANA", "orders, stock, pricing"), ("Dealer management", "DMS"), ("MES", "plant execution"), ("Historian + IoT", "IoT SiteWise")],
      [("Quality · LIMS", ""), ("Warranty system", ""), ("CRM", ""), ("Supplier portal", "")]], "#F1F1EF"),
]


def fig_big():
    n = 21
    X, W = 150, 700
    b = ""
    y = 10
    for label, rows, fill in ROWS:
        part, y = band(n, X, y, W, label, rows, fill)
        b += part
        if label.startswith("Vertical"):
            b += t(X + W / 2, y - 4, "↓ every agent reuses the same assets ↓", 13, hand=True)
            y += 10
    H = y + 10
    step = (H - 40) / len(LIFE)
    b += t(70, 22, "LIFECYCLE", 12, bold=True)
    for i, (a, s) in enumerate(LIFE):
        b += cell(n, 10, 34 + i * step, 120, step - 12, a, s, WASH["butter"])
    step = (H - 40) / len(GOV)
    b += t(930, 22, "GOVERNANCE", 12, bold=True)
    for i, (a, s) in enumerate(GOV):
        b += cell(n, 870, 34 + i * step, 120, step - 12, a, s, WASH["butter"])
    return svg(n, 1000, H, b, "The agent harness on AWS: lifecycle rail on the left, governance rail on the right, and seven bands: "
               "end users, channels, front door, orchestration, vertical tyre-company agents, horizontal assets on AWS, systems of record")


# ------------------------------------------------------------------ drawing: x/y/z bars
def fig_split():
    n = 22
    rows = sorted(C, key=lambda c: (-c[9][0]))
    X0, BW, RH = 250, 640, 26
    b = ""
    b += (f'<rect x="{X0}" y="8" width="16" height="14" fill="#D9D9D6" class="o" style="stroke-width:1.2"/>'
          + t(X0 + 22, 20, "AWS gives", 13, anchor="start")
          + f'<rect x="{X0 + 120}" y="8" width="16" height="14" fill="{I.PAL["peri"]}" class="o" style="stroke-width:1.2"/>'
          + t(X0 + 142, 20, "we code once (horizontal asset)", 13, anchor="start")
          + f'<rect x="{X0 + 380}" y="8" width="16" height="14" fill="{I.PAL["rose"]}" class="o" style="stroke-width:1.2"/>'
          + t(X0 + 402, 20, "each agent team writes", 13, anchor="start"))
    for k, c in enumerate(rows):
        y = 36 + k * RH
        x, yy, z = c[9]
        b += t(X0 - 10, y + 15, E(f"{c[0]} · {c[1]}"), 12.5, anchor="end")
        cur = X0
        for v, fill in ((x, "#D9D9D6"), (yy, I.PAL["peri"]), (z, I.PAL["rose"])):
            w = BW * v / 100
            if w:
                b += f'<rect x="{cur:.0f}" y="{y}" width="{w:.0f}" height="19" fill="{fill}" class="o" style="stroke-width:1.1"/>'
                if v >= 10:
                    b += t(cur + w / 2, y + 14, f"{v}", 11)
            cur += w
    H = 36 + len(rows) * RH + 6
    return svg(n, 920, H, b, "Stacked bars per concern: grey is what AWS gives, blue is what we code once, pink is what each agent team writes")


# ------------------------------------------------------------------ tables
def marks(items):
    return "<ul>" + "".join(f'<li><span class="aw-mark {m}">{MARK[m]}</span>{E(nm)}' + (f" <small>{E(w)}</small>" if w else "") + "</li>"
                            for nm, m, w in items) + "</ul>"


def binding_table():
    out = ['<div class="sd-table wide"><table><tr><th>Concern</th><th>On AWS</th><th>Open source</th>'
           '<th>Ours, built once, and why</th></tr>']
    for fam, sub in FAMILIES:
        out.append(f'<tr class="aw-fam"><td colspan="4">{fam} <small style="font-family:var(--sans);font-size:14px">· {sub}</small></td></tr>')
        for cid, name, f, does, aws, oss, ours, az, why, _ in C:
            if f != fam:
                continue
            out.append(f"<tr><td><b>{cid} · {E(name)}</b><br><small>{E(does)}</small></td><td>{marks(aws)}</td><td>{marks(oss)}</td>"
                       f"<td>{E(ours)}<br><small><i>{E(why)}</i></small></td></tr>")
    out.append("</table></div>")
    return "".join(out)


def final_table():
    """Only what we picked: AWS and open-source items marked use or planned, plus our own code."""
    def picked(items):
        got = [E(nm) + (" <small>(planned)</small>" if m == "plan" else "") for nm, m, _ in items if m in ("use", "plan")]
        return "<br>".join(got) or "—"
    out = ['<div class="sd-table wide"><table><tr><th>Concern</th><th>AWS service</th><th>Open source</th><th>Our own code</th></tr>']
    for fam, sub in FAMILIES:
        out.append(f'<tr class="aw-fam"><td colspan="4">{fam}</td></tr>')
        for cid, name, f, does, aws, oss, ours, az, why, _ in C:
            if f == fam:
                out.append(f"<tr><td><b>{cid} · {E(name)}</b></td><td>{picked(aws)}</td><td>{picked(oss)}</td><td>{E(ours)}</td></tr>")
    out.append("</table></div>")
    return "".join(out)


DECISIONS = [
    ("Which model?", "Claude on Bedrock · Llama or Nova on Bedrock · a model outside AWS via the gateway",
     "Claude on Bedrock as the default for every job, behind our gateway. The golden set picks the model per job offline; cheaper models win where they pass.",
     "Pursue: Claude on Bedrock", "Data stays in the AWS account; switching model is one line in AppConfig."),
    ("Which gateway (the one door to models)?", "Bedrock AgentCore Gateway · LiteLLM proxy on ECS Fargate · API Gateway + Lambda (build it ourselves)",
     "AgentCore Gateway, with our policy (allow-list, budgets) as its rules; LiteLLM on Fargate kept as the fallback behind the same port.",
     "Pursue: AgentCore Gateway", "Managed by AWS, the closest match to APIM's AI gateway, and it also fronts MCP tools. LiteLLM only if a rule we need is missing or a non-AWS model is required. Check Mumbai availability first."),
    ("Where does our code run?", "ECS Fargate · Bedrock AgentCore Runtime · EKS",
     "ECS Fargate: the closest match to Azure Container Apps, no cluster to run.",
     "Pursue: ECS Fargate", "AgentCore Runtime is worth a pilot later; EKS only if the company already runs Kubernetes."),
    ("How do approvals wait?", "DBOS on Aurora · Step Functions task tokens",
     "DBOS: the same code as on Azure, state in the database we already run.",
     "Pursue: DBOS", "Step Functions works, but it is one more service and AWS-only."),
    ("How do dealers and customers sign in?", "Amazon Cognito · federate the existing dealer portal over OIDC",
     "Federate the existing portal if it speaks OIDC; Cognito only if there is no portal.",
     "Pursue: federate", "Dealers keep one login; the harness only needs a verified token."),
]

SWAP = [
    ("Front door", "Azure Front Door + WAF", "CloudFront + AWS WAF"),
    ("AI gateway", "API Management (AI gateway)", "Bedrock AgentCore Gateway (LiteLLM on Fargate as fallback)"),
    ("Models", "Foundry Models", "Amazon Bedrock (Converse API)"),
    ("Where code runs", "Azure Container Apps", "Amazon ECS on Fargate"),
    ("Sign-in", "Entra ID, External ID", "IAM Identity Center (staff), Cognito or portal OIDC (dealers, fleets, consumers)"),
    ("Secrets and keys", "Key Vault, managed identity", "Secrets Manager + KMS, IAM task roles"),
    ("Guardrails", "AI Content Safety, Prompt Shields", "Bedrock Guardrails (ApplyGuardrail)"),
    ("Finding personal data", "AI Language PII", "Comprehend PII, Macie for S3"),
    ("Database", "Azure Database for PostgreSQL", "Aurora PostgreSQL"),
    ("Queue", "Service Bus", "SQS FIFO"),
    ("Traces and metrics", "Application Insights, Managed Prometheus", "CloudWatch, X-Ray, Managed Prometheus"),
    ("Runtime config, kill switch", "App Configuration", "AWS AppConfig"),
    ("Cost", "Cost Management, APIM token metric", "Budgets, Cost Explorer, Bedrock inference-profile tags"),
    ("Evaluation", "Foundry evaluation, AI Red Teaming Agent", "Bedrock evaluations, PyRIT, promptfoo"),
    ("Infrastructure as code", "Bicep + azd", "Terraform or AWS CDK"),
    ("Contact centre", "Communication Services, Dynamics", "Amazon Connect, End User Messaging, SES"),
]
SAME = ["The 22 concerns and the specs (AI Harness Catalog, AI Assurance Catalog, agent specs)",
        "The agent code: router, loop, context assembler, tools, approval flows",
        "The tests: AgentTwin worlds, golden sets, hard graders, the four CI gates",
        "The rules: every guardrail position and every check that protects money or a customer",
        "The ports: each AWS service sits behind the same interface the Azure one did"]


BODY = f"""<main class="wrap">
<div class="hero"><p class="eyebrow">AI engineering · cloud binding</p><h1>{TITLE}</h1>
<p class="thesis">The same harness, the same specs and the same tests as on Azure. <em>Only the binding changes</em>: each box gets an AWS service, an open-source tool, or our own code.</p></div>

<div class="sd-answer">
<p><b>The one-minute version.</b> An agent that talks to dealers, customers and staff needs much more than a model: sign-in, guardrails, memory, tools, approvals, logging, cost limits, tests. We call that the <b>harness</b>, and we split it into 22 concerns.</p>
<p>The concerns never name a product. For each cloud we write a <b>binding</b>: which service does each job. This page is the AWS binding, with a tyre manufacturer as the example. On average, by our judgement, about a third of each concern comes from AWS (36%), nearly half is shared code we write once (45%), and about a fifth is what each agent team writes (19%).</p>
<p>Already seen the Azure version? Compare <a href="{AH}arch-azure.html">the harness on Azure</a> and <a href="{AH}tech.html">the Azure tech stack, concern by concern</a>. Why we work from specs: <a href="/leaders/spec-driven/">spec-driven development</a>.</p>
</div>

<div class="sd-stat">
<div><b>22 concerns</b>in five families: think, act, control, see, change</div>
<div><b>6 agents</b>for dealers, plants, quality and fleets, on one shared platform, each with its own autonomy level</div>
<div><b>12 horizontal assets</b>built once on AWS, reused by every agent</div>
<div><b>India + EU</b>Mumbai and Hyderabad for India, Frankfurt or Ireland for European plants; personal data stays in its region</div>
</div>

<section><p class="eyebrow">The big picture</p><h2>One request, top to bottom, on AWS</h2>
<p>Read it as one request: a dealer or an engineer asks, through a channel, past the front door, to one vertical agent, which uses the shared assets to reach the company's systems. The left rail is the life of every agent; the right rail is governance.</p>
{fig(fig_big(), "The dark cell is the first agent to build (the dealer assistant). The vertical-agents band changes per business; every other band is shared. Compare with the same picture on Azure: the boxes do not move, only the names change.")}
<div class="sd-table"><table>
<tr><th>Band</th><th>What it does on AWS</th></tr>
<tr><td>End users</td><td>Dealers, fleet customers and consumers sign in through Cognito or the existing dealer portal; plant, quality, sales and service staff through IAM Identity Center.</td></tr>
<tr><td>Channels</td><td>Web and app chat, WhatsApp and SMS through AWS End User Messaging, email through SES, and the contact centre through Amazon Connect.</td></tr>
<tr><td>Front door</td><td>CloudFront and WAF at the edge; Bedrock Guardrails for hidden instructions; Comprehend to find personal data; our router rules; API Gateway limits.</td></tr>
<tr><td>Orchestration</td><td>Our router picks one agent; agents hand work to each other over A2A; a registry in Git names the owner and version of each.</td></tr>
<tr><td>Vertical agents</td><td>One ECS service per business job. Each has an autonomy level: answers, suggests, drafts for a person, or acts after checks.</td></tr>
<tr><td>Horizontal assets</td><td>Twelve shared parts every agent reuses (next sections).</td></tr>
<tr><td>Systems of record</td><td>SAP S/4HANA, the dealer management system, MES, the plant historian and IoT SiteWise, quality and LIMS, warranty, CRM and the supplier portal, reached only through MCP tools with the user's own rights.</td></tr>
</table></div></section>

<section><p class="eyebrow">Every concern, bound to AWS</p><h2>The 22 concerns, one table</h2>
<p>For each concern: what AWS offers and whether we use it, the open-source options, and what we code once for every agent, and why.</p>
<p class="aw-key"><span class="aw-mark use">use</span> in the design &nbsp; <span class="aw-mark plan">planned</span> next phase &nbsp; <span class="aw-mark list">considered</span> not picked, or newer service to check &nbsp; <span class="aw-mark no">not used</span> and why</p>
{binding_table()}
<p class="aw-key">Services marked "check current status" are newer AWS offerings; confirm their availability in the Mumbai, Hyderabad, Frankfurt and Ireland regions before relying on them.</p>
</section>

<section><p class="eyebrow">Who builds what</p><h2>What AWS gives, what we build, what each agent writes</h2>
<p>For each concern, how much does AWS give us, how much do we code once for every agent, and how much does each agent team still write? AWS gives the plumbing. The parts that make an agent safe for dealers and customers stay in our code.</p>
{fig(fig_split(), "Our judgement, not a measurement. AWS gives the plumbing (gateway, identity, storage, logging); the parts that make an agent trustworthy stay in our code.")}
<p>The rule that keeps this healthy: when two agents write the same code, it moves into the shared middle (blue). When AWS catches up, it moves to the left (grey).</p></section>

<section><p class="eyebrow">Open decisions</p><h2>Five choices to make with the company's team</h2>
<div class="sd-table"><table>
<tr><th>Decision</th><th>Options</th><th>Our recommendation</th><th>Verdict</th><th>Why</th></tr>
{"".join(f"<tr><td><b>{E(q)}</b></td><td>{E(o)}</td><td>{E(r)}</td><td><b>{E(v)}</b></td><td>{E(w)}</td></tr>" for q, o, r, v, w in DECISIONS)}
</table></div></section>

<section><p class="eyebrow">Moving clouds</p><h2>Azure to AWS in one table</h2>
<div class="sd-table"><table>
<tr><th>Job</th><th>On Azure</th><th>On AWS</th></tr>
{"".join(f"<tr><td>{E(j)}</td><td>{E(a)}</td><td>{E(w)}</td></tr>" for j, a, w in SWAP)}
</table></div>
<div class="sd-answer"><p><b>What does not change: specs, tests and agent code.</b></p>
<ul>{"".join(f"<li>{E(s)}</li>" for s in SAME)}</ul>
<p>That is the point of binding through ports: moving from Azure to AWS is a new binding file and a set of adapters, not a rebuild.</p></div>
</section>

<section id="final"><p class="eyebrow">Finally</p><h2>What we are using</h2>
<p>The whole binding on one page: for each concern, only what we picked. AWS services and open-source tools marked <i>planned</i> are chosen but not yet switched on; everything else in the tables above was considered and left out.</p>
{final_table()}
</section>

<section><p class="eyebrow">Read next</p><h2>Go deeper</h2>
<p><a href="{AH}">Agent harness tutorial</a> (every concern explained, on the Azure example) · <a href="/leaders/spec-driven/">Spec-driven development</a> · <a href="/learn/data-platform-architecture/">Data platform architecture</a> · <a href="/learn/agent-guardrails/">Guardrail catalog</a> · <a href="/learn/agenttwin/">AgentTwin</a>.</p>
<p>To walk through this with your team, write to <a href="mailto:basant@cleandataengineering.ai?subject=Agent%20harness%20on%20AWS">basant@cleandataengineering.ai</a>.</p></section>
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
