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
        "group, every one of the 22 concerns mapped to an AWS service, open source or our own code, the end-to-end design tier by tier, and the plan for the reference implementation.")
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
   ("Bedrock AgentCore Gateway, inference targets", "use", "any provider incl. OpenAI-compatible ones like Groq; translates OpenAI, Anthropic and Bedrock dialects; model fallback with circuit breaker; request and token-per-minute limits per user, model or target; Bedrock Guardrails in gateway policy (checked 3 Nov 2026)"),
   ("Bedrock application inference profiles", "use", "one per agent, tagged, so cost and quota are per agent")],
  [("LiteLLM proxy on ECS Fargate", "list", "fallback gateway if AgentCore Gateway lacks a rule we need, or for non-AWS models"),
   ("Pydantic AI", "use", "model layer only")],
  "Our gateway policy: allow-list per job, token budget, one retry budget, token metric per agent",
  "APIM AI gateway → Foundry Models",
  "AgentCore Gateway is AWS's AI gateway, the same job APIM's AI gateway does on Azure: one governed door with identity, rate and token limits, fallback and logging. Our policy (allow-list per job, budgets) sits on top as config. Check region availability and token-limit features before go-live. The agent never holds a provider key.", (55, 35, 10)),
 ("L4", "Control loop", "Think", "Plan, act, check, with step and no-progress limits.",
  [("Bedrock Agents", "no", "the platform would own the loop"),
   ("Bedrock AgentCore Runtime", "list", "could host our own loop; pilot later"),
   ("AgentCore managed harness", "no", "AWS's own harness (CreateHarness, GA 2026): AWS runs the loop, memory and evaluation; our loop is the kept delta")],
  [("Strands Agents", "no", "AWS's open SDK; fine for simple agents"), ("LangGraph", "no", "workflow-shaped agents only"),
   ("Claude Agent SDK", "no", "Claude-only, loop hidden")],
  "Hand-written loop, about 400 lines; budgets of 12 steps, 60 s and a cost cap per turn",
  "Hand-written loop (same code)",
  "Agents that touch orders, warranties and money need every step testable and checks at exact positions. Our own loop runs on any model and any cloud.", (0, 80, 20)),
 ("L5", "State & memory", "Think", "What is kept, for how long, and for whom.",
  [("Amazon RDS for PostgreSQL, Multi-AZ", "use", "HA, backups, IAM login; one instance holds state, DBOS waits and pgvector"),
   ("Aurora PostgreSQL", "list", "when one RDS instance is not enough; Serverless v2 never pauses while DBOS holds a connection"),
   ("DynamoDB", "list", "not picked"), ("ElastiCache for Valkey", "list", "caches only"),
   ("AgentCore Memory", "list", "check current status")],
  [("psycopg + pool", "use", "driver")],
  "5 agent tables + DBOS state in the same database; retention and erase per person",
  "Azure Database for PostgreSQL",
  "Plain RDS PostgreSQL, the same engine as on Azure. One managed store that also holds the approval engine and, later, pgvector: no extra infrastructure.", (40, 45, 15)),
 ("18", "Knowledge & retrieval", "Think", "Finds sourced passages, filtered by what this user may see.",
  [("pgvector on the same RDS PostgreSQL", "plan", "chosen"), ("Bedrock Knowledge Bases", "list", "managed RAG; less control of filters"),
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
 ("PV", "Privacy & data protection", "Control", "Personal data of dealers, fleet drivers and consumers used only for this case, kept in its country, masked, and forgotten on request.",
  [("Comprehend PII", "plan", "names, phone, ids in text"),
   ("Amazon Macie", "plan", "finds personal data in S3"), ("Mumbai (Hyderabad for DR)", "use", "India data stays in India"), ("Frankfurt", "plan", "a second copy of the stack, only when EU personal data arrives"),
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
  [("Step Functions task tokens", "list", "a managed wait, now callable as an MCP tool through the Gateway; but a second state store, and AWS-only"),
   ("Amazon Connect", "plan", "hand-off to a person with history")],
  [("DBOS", "use", "durable waits in our own PostgreSQL"), ("Temporal", "list", "")],
  "Approval and escalation tables, desk API, approval cards to staff",
  "DBOS on PostgreSQL (same code)",
  "A warranty or order approval must survive restarts. DBOS keeps it in the database we already run, so it moves clouds unchanged.", (20, 55, 25)),
 ("AV", "Availability & disaster recovery", "Control", "A lost server or zone goes unnoticed; a lost region is rebuilt from code and backups.",
  [("Multi-AZ ECS + RDS Multi-AZ", "use", ""), ("RDS cross-region read replica", "plan", "Mumbai → Hyderabad, promoted in a disaster"),
   ("Route 53 health checks", "plan", ""), ("AWS Backup", "plan", "")],
  [("Terraform or AWS CDK", "use", "infrastructure as code")],
  "Stateless servers + durable state; a rebuild drill",
  "Zone redundancy, Front Door, Bicep",
  "Two Indian regions make a DR pair without data leaving the country. Target: back within 4 hours, at most 15 minutes of data lost.", (65, 25, 10)),
 # ---- See
 ("L11", "Observability", "See", "Traces, metrics and alerts for every step.",
  [("AWS Distro for OpenTelemetry (ADOT) collector", "use", "a sidecar in every ECS task; receives OTLP from our code, sends traces to X-Ray, metrics and logs to CloudWatch"),
   ("CloudWatch + Application Signals", "use", "dashboards, SLOs, alarms"), ("AWS X-Ray", "use", "traces, read through the OTLP endpoint"),
   ("Bedrock model invocation logging", "use", "to S3, for evidence"),
   ("CloudWatch generative AI observability", "list", "check current status"),
   ("Managed Prometheus + Grafana", "plan", "")],
  [("OpenTelemetry SDK + GenAI semantic conventions", "use", "the only telemetry API our code calls"), ("Langfuse", "list", "takes OTLP too, if a team wants an LLM trace viewer")],
  "One telemetry helper on the OpenTelemetry SDK: spans per step with GenAI attributes, personal data redacted before export, alert rules as code",
  "OpenTelemetry → App Insights",
  "OpenTelemetry is the one standard from code to collector: the code never imports an AWS SDK for telemetry. On Azure the same spans go to Application Insights; on AWS the ADOT collector sends them to X-Ray and CloudWatch. Moving clouds changes the collector's config file, not the code.", (55, 35, 10)),
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
   ("AgentCore Evaluations", "plan", "one more evaluator provider inside our eval framework (includes DeepEval evaluators; online evaluation of live traces)")],
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
       ("Identity Center", "access reviews"), ("Residency", "India first; EU later"), ("DPDP + GDPR", "consent, erasure"),
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
     [[("Model gateway", "AgentCore Gateway"), ("Knowledge", "pgvector on RDS"), ("Memory & state", "RDS PostgreSQL"),
       ("Tool / MCP hub", "MCP on Fargate"), ("Channels", "Connect, SES, EUM"), ("Identity", "Cognito, IAM, KMS")],
      [("Guardrails", "Bedrock + our rules"), ("Human desk", "DBOS + Connect"), ("Observability", "OpenTelemetry → ADOT"),
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



# ------------------------------------------------------------------ end-to-end design, tier by tier (all decided)
# (id, name, plain, [(decision, we use, not used, why)])
TIERS = [
 ("H0", "Foundation", "The plot of land: accounts, region, private network, keys, and the code that builds it all.", [
  ("Accounts", "AWS Organizations + Control Tower: agents-dev, agents-test, agents-prod, plus shared security, log-archive, network and shared-services accounts",
   "one account for everything", "Agents face the internet; a problem in one account cannot reach another. The data platform has its own accounts in the same organisation."),
  ("Region", "Mumbai (ap-south-1) primary, Hyderabad (ap-south-2) for disaster recovery; a policy (SCP) blocks every other region except us-east-1 for global services",
   "active-active across regions", "Indian personal data stays in India. A Frankfurt copy is the same Terraform with another region, built only when EU personal data arrives."),
  ("Network", "One VPC per account across 2 zones, private subnets only; the load balancer is the only public part; Transit Gateway in the network account; outbound only through Network Firewall with a domain allow-list",
   "open NAT egress", "One way in, one way out, both inspected."),
  ("Private paths", "VPC endpoints for Bedrock, AgentCore, STS, KMS, Secrets Manager, CloudWatch Logs, X-Ray, ECR, SQS, AppConfig; S3 gateway endpoint",
   "public AWS endpoints", "No call to the model or to a secret crosses the internet."),
  ("Keys", "KMS customer keys per kind of data: agent state, logs and transcripts, knowledge", "one key for all", "Erasing or rotating one kind of data leaves the others alone."),
  ("Blueprint", "Terraform for everything, shared modules with the data platform", "AWS CDK", "One tool for AWS and Databricks (it has a Terraform provider)."),
 ]),
 ("H1", "Model door", "Every model call goes through one governed door, so models can be swapped and spend can be capped.", [
  ("Gateway", "Bedrock AgentCore Gateway in front of Bedrock; LiteLLM on Fargate as the fallback behind the same port", "agents calling Bedrock directly",
   "The counterpart of APIM's AI gateway: identity, limits, fallback and logging in one place. The agent never holds a model key."),
  ("Models", "Claude on Bedrock: Sonnet for reasoning, Haiku for routing and short jobs; the model per job lives in AppConfig. The reference implementation's dev setup uses a free open-weight model (Groq) behind the same gateway",
   "Intelligent Prompt Routing", "Picking the model is a decision we test offline with the golden set, not one the platform makes per prompt."),
  ("Residency", "Calls carrying Indian personal data run in Mumbai; no Asia-Pacific cross-region profile for them", "APAC cross-region inference for personal data",
   "That profile can route to Tokyo, Singapore or Sydney."),
  ("Spend", "One application inference profile per agent (tagged), a token budget per turn, prompt caching on the fixed part of the context", "",
   "Cost per agent comes from AWS; cost per business case comes from our meter (H7)."),
 ]),
 ("H2", "Runtime and loop", "Where our code runs, and the loop that plans, acts and checks.", [
  ("Compute", "ECS on Fargate: one service for the router, one per agent, one per MCP tool server", "AgentCore Runtime, EKS, Lambda",
   "No cluster to run, the closest match to Container Apps. AgentCore Runtime gets a pilot later; Lambda's cold starts and limits fit a 60-second turn badly."),
  ("Loop", "Our hand-written loop (about 400 lines): 12 steps, 60 seconds and a cost cap per turn; Pydantic AI only as the model layer", "Bedrock Agents, Strands, LangGraph",
   "The loop is where every check has an exact position; it stays ours on every cloud."),
  ("Model layer", "Pydantic AI under our loop: typed calls, structured output and one interface for Bedrock and Groq", "Claude Agent SDK, raw boto3 Converse",
   "The Agent SDK is Claude-only and runs its own loop out of sight. Calling boto3 directly would mean rebuilding typing, retries and output checks. Pydantic AI helps without taking over the loop."),
  ("Front", "Production: CloudFront + WAF → Application Load Balancer. Dev: API Gateway HTTP API, with the channel's webhook answered before the turn runs", "",
   "API Gateway caps a request at 30 seconds, below the 60-second turn."),
  ("Flow", "SQS FIFO with one message group per conversation; one turn per conversation at a time; priority classes", "", "Order is kept per conversation; a plant breakdown goes before a marketing question."),
  ("Registry", "A catalogue file in Git: agent, version, owner, autonomy level", "AWS Agent Registry", "Not offered in Mumbai; Git is enough."),
 ]),
 ("H3", "State, memory, knowledge", "What the agent keeps, for how long, for whom, and where it finds sourced answers.", [
  ("Database", "Amazon RDS for PostgreSQL, Multi-AZ: one instance, schemas agent_state, dbos and knowledge; one database role per app", "Aurora Serverless v2, DynamoDB",
   "PostgreSQL, the same engine as on Azure. Serverless v2 never pauses while DBOS holds a connection, so plain RDS is cheaper and simpler."),
  ("Memory", "Conversation and case tables; retention per data class; erase per person (DPDP Act)", "AgentCore Memory", "Memory must follow our retention and erasure rules."),
  ("Knowledge", "pgvector in the same database, Bedrock embeddings; the entitlement filter is a SQL WHERE clause", "Bedrock Knowledge Bases, OpenSearch",
   "A dealer sees only their own price list and orders; one store, one backup, one access model."),
  ("When to outgrow it", "Stay on pgvector (HNSW index) up to roughly 10 million passages or when searches start slowing turns; then move knowledge to OpenSearch Serverless or S3 Vectors behind the same retrieval port", "", "State and memory are ordinary rows and stay in PostgreSQL; only knowledge search would move."),
  ("Recovery", "Automated backups + AWS Backup; a read replica in Hyderabad, promoted in a disaster (back within 4 hours, at most 15 minutes lost)", "Aurora Global Database", "Enough for the stated targets at a fraction of the cost."),
 ]),
 ("H4", "Tools to systems of record", "How agents reach SAP, the dealer system, the plants and the data platform, with the user's own rights.", [
  ("Tool servers", "One MCP server per system on Fargate: SAP S/4HANA, dealer management, MES and historian, warranty, CRM. Read tools first; write tools only behind an approval", "agents calling systems directly",
   "The protocol is open, so the servers move clouds unchanged."),
  ("Gating", "Before every call: argument check (JSON Schema), scope check (this dealer's records only), idempotency key, size cap", "", "Protects orders, prices and warranties; ours on every cloud."),
  ("On behalf of", "Our token issuer mints a 5-minute token for the far system on behalf of the user, signed with a KMS key; tool servers check it against our published keys (JWKS)", "AgentCore Identity",
   "The same pattern as the Azure FNOL agent; Cognito has no on-behalf-of exchange."),
  ("SAP", "SAP's OData APIs over Direct Connect or VPN through Transit Gateway", "reading SAP's database", "SAP's own rules and locks stay in force."),
  ("Data platform", "One MCP tool over a Databricks SQL warehouse (Metric Views) through PrivateLink, with the user's Unity Catalog rights", "reading raw S3 files", "Numbers come from the governed semantic layer."),
 ]),
 ("H5", "Identity, privacy, guardrails", "Who is asking, what data the turn may use, and the checks on the way in and out.", [
  ("People", "Cognito user pool for dealers, fleets and consumers, federating the dealer portal over OIDC; staff through IAM Identity Center", "", "Dealers keep one login; the harness only needs a verified token."),
  ("Services", "IAM task roles; secrets in Secrets Manager encrypted with KMS", "keys in code or environment", "Nothing to leak."),
  ("Way in", "Bedrock Guardrails through the ApplyGuardrail API (prompt attacks, denied topics) on user input and on tool results", "NeMo Guardrails", "One detector port; works with any model."),
  ("Way out", "Our 30 positioned rules (no price or warranty outside policy, no order changed without OK, a dealer's own records only) + contextual grounding check", "", "Every rule that protects money or a customer is ours."),
  ("Personal data", "Comprehend PII plus our recognisers for Aadhaar, PAN, GSTIN and vehicle numbers, redacting before telemetry; Macie on the buckets", "", "Telemetry and logs never carry raw personal data."),
 ]),
 ("H6", "Channels and the human desk", "How people reach the agent, and how a person takes over or approves.", [
  ("Web chat", "Our chat page inside the dealer portal", "", "Simple, and the portal already has the sign-in."),
  ("Other channels", "WhatsApp and SMS through AWS End User Messaging; email through SES; one conversation id across channels", "", "Dealers in India live on WhatsApp."),
  ("Desk", "Chatwoot on Fargate as the human desk; Amazon Connect adapter when a contact centre exists", "building our own desk", "A desk with the full history, without building one."),
  ("Approvals", "DBOS durable waits in the same PostgreSQL; an approval card to the sales or warranty desk; autonomy level per agent", "Step Functions task tokens", "Survives restarts, same code as on Azure, no extra service."),
 ]),
 ("H7", "Observability, replay, cost", "What we can see, prove and pay for. Everything goes through OpenTelemetry.", [
  ("Telemetry standard", "OpenTelemetry SDK in our code, one helper, GenAI semantic conventions; personal data redacted before export", "AWS SDK calls for telemetry",
   "The code never changes between clouds; only the collector's config does."),
  ("Collector", "AWS Distro for OpenTelemetry (ADOT) as a sidecar in every ECS task: traces to X-Ray, metrics and logs to CloudWatch", "", "AWS's supported build of the OpenTelemetry collector."),
  ("Dashboards and alerts", "CloudWatch Application Signals for SLOs; alarms as code (Terraform) to SNS email and chat", "", "Turn latency at the 95th percentile, error rate, guardrail blocks, cost per hour."),
  ("Evidence", "Bedrock model invocation logging to S3 in the log-archive account (1 year); CloudTrail for who changed what", "", "Answers an auditor's question months later."),
  ("Replay", "Run record + cassettes + config fingerprint in S3", "", "\"Why did the agent tell this dealer that price?\" needs a replay; no cloud offers one."),
  ("Cost", "Inference profile tags + Budgets + CUR 2.0; our meter per turn and per case with a hard budget stop", "", "Cost per warranty claim triaged, not just per agent."),
 ]),
 ("H8", "Evaluation and release", "How a change is proven safe and rolled out, and rolled back.", [
  ("CI", "GitHub Actions with OIDC into AWS (no stored keys); four gates: AgentTwin world, golden sets, red team (PyRIT, promptfoo), cost and latency", "CodePipeline", "The same gates as on Azure."),
  ("Images", "Amazon ECR, scanned on push", "public registries in production", "Private images, close to Fargate."),
  ("Release", "One release bundle (prompt + model + policy + config fingerprint); ECS blue/green through CodeDeploy with alarms that roll back", "", "Prompt, model and policy change together and roll back together."),
  ("Runtime config", "AWS AppConfig: kill switch per agent, limits, model per job, read before every turn", "", "A bad behaviour is switched off in seconds, without a deploy."),
  ("Online evaluation", "Each night a sample of live turns is graded; Bedrock evaluation is one judge plug-in; misses go to the golden set", "", "The golden set keeps learning from production."),
 ]),
]

WALK = [
 ("Dealer", "A dealer in Pune asks in the portal chat: \"Can I get 40 of 205/55 R16 by Friday, and at what price?\" The portal's sign-in gives a token (Cognito, federated)."),
 ("Edge", "CloudFront and WAF filter the request; the load balancer passes it to the router on ECS."),
 ("Router", "Checks the token, runs the input guardrail (ApplyGuardrail), opens the turn in PostgreSQL (one turn per conversation) and picks the dealer assistant."),
 ("Context", "The assembler builds the turn: recent conversation from PostgreSQL, the dealer's own price list passages from pgvector."),
 ("Model", "The loop calls the model through AgentCore Gateway to Claude on Bedrock in Mumbai; the gateway checks the allow-list and the token budget."),
 ("Tools", "The model asks for check_stock and get_price. Gating checks the arguments and the dealer scope; our issuer mints a 5-minute token on the dealer's behalf; the SAP MCP server calls SAP over Direct Connect."),
 ("Way out", "Our rules check the reply: the price comes from this dealer's list, the date from SAP's confirmed stock. The grounding check confirms nothing was invented."),
 ("Reply", "The dealer gets stock, price and date. \"Place the order\" would start an approval: a DBOS wait and a card to the sales desk."),
 ("Trace", "Every step was an OpenTelemetry span sent to the ADOT sidecar, then on to X-Ray and CloudWatch; the model call is logged to S3; the meter wrote the cost of the turn."),
]


def fig_deploy():
    n = 23
    b = ""
    b += t(80, 22, "PEOPLE AND CHANNELS", 12, bold=True)
    for i, (a, sub) in enumerate([("Dealer portal chat", "our page"), ("WhatsApp, SMS", "End User Messaging"), ("Email", "Amazon SES"),
                                  ("Contact centre", "Connect (optional)"), ("Staff", "Identity Center")]):
        b += cell(n, 10, 40 + i * 62, 140, 48, a, sub, WASH["sky"])
    b += cell(n, 172, 150, 120, 52, "CloudFront + WAF", "the one way in", WASH["butter"])
    b += cell(n, 172, 240, 120, 52, "Cognito", "portal OIDC", WASH["butter"])
    for i in range(5):
        b += arrow(n, f"M152 {64 + i * 62} L168 176")
    # region
    b += f'<rect x="312" y="30" width="458" height="560" rx="16" fill="{WASH["peri"]}" stroke="{INK}" stroke-width="1.6" stroke-dasharray="7 5"/>'
    b += t(326, 52, "agents-prod account · Mumbai · private VPC, 2 zones", 13, bold=True, anchor="start")
    b += cell(n, 330, 66, 200, 44, "Load balancer", "the only public part", "#fff")
    b += arrow(n, "M294 176 C310 150 315 100 328 90")
    b += f'<rect x="326" y="124" width="428" height="168" rx="12" fill="{WASH["lilac"]}"/>'
    b += t(338, 144, "ECS on Fargate", 15, hand=True, anchor="start")
    b += cell(n, 336, 154, 200, 46, "Router + 6 agents", "our loop, Pydantic AI", "#fff", dark=True)
    b += cell(n, 546, 154, 198, 46, "ADOT collector", "OpenTelemetry sidecar", "#fff")
    b += cell(n, 336, 214, 200, 46, "Token issuer", "on-behalf-of, KMS key", "#fff")
    b += cell(n, 546, 214, 198, 46, "MCP tool servers", "SAP, DMS, MES, warranty", "#fff")
    b += t(540, 280, "Chatwoot desk runs here too", 12, fill="#444")
    b += arrow(n, "M430 112 L430 152")
    b += arrow(n, "M500 202 L590 212")
    b += cell(n, 330, 308, 200, 52, "RDS for PostgreSQL", "state · DBOS · pgvector", WASH["mint"])
    b += cell(n, 546, 308, 208, 52, "SQS FIFO", "one group per conversation", WASH["mint"])
    b += t(330, 392, "Private endpoints (PrivateLink)", 13, bold=True, anchor="start")
    b += cell(n, 330, 402, 200, 52, "AgentCore Gateway", "→ Bedrock (Claude)", WASH["rose"])
    b += cell(n, 546, 402, 208, 52, "Bedrock Guardrails", "+ Comprehend PII", WASH["rose"])
    b += cell(n, 330, 470, 130, 48, "Secrets + KMS", "", "#fff")
    b += cell(n, 470, 470, 130, 48, "AppConfig", "kill switch", "#fff")
    b += cell(n, 610, 470, 144, 48, "X-Ray + CloudWatch", "via OTLP", "#fff")
    b += t(540, 548, "Network Firewall: outbound only to an allow-list", 12, fill="#444")
    b += t(540, 568, "everything built by Terraform", 12, fill="#444")
    b += arrow(n, "M746 182 C772 230 772 440 712 468")
    b += arrow(n, "M334 190 C316 260 316 380 328 425")
    # right side
    b += t(890, 52, "OUTSIDE THE ACCOUNT", 12, bold=True)
    b += cell(n, 790, 66, 200, 46, "Transit Gateway", "network account", WASH["butter"])
    b += cell(n, 790, 124, 200, 60, "Plants and SAP", "Direct Connect / VPN", "#F1F1EF")
    b += cell(n, 790, 200, 200, 52, "Data platform account", "Databricks SQL, PrivateLink", WASH["mint"])
    b += cell(n, 790, 300, 200, 52, "Hyderabad", "RDS replica for DR", WASH["sky"])
    b += cell(n, 790, 380, 200, 52, "Log-archive account", "CloudTrail, model logs", WASH["sky"])
    b += cell(n, 790, 460, 200, 52, "Shared services", "GitHub OIDC, ECR", WASH["sky"])
    b += arrow(n, "M746 230 C766 170 760 100 788 90")
    b += arrow(n, "M890 114 L890 122")
    b += arrow(n, "M746 240 L788 228")
    b += arrow(n, "M440 362 C520 384 720 384 788 330", dash=True)
    return svg(n, 1000, 600, b, "Deployment on AWS: channels and people on the left, through CloudFront and WAF into the agents-prod account in Mumbai, "
               "which runs the router, agents, ADOT collector, MCP servers and token issuer on ECS Fargate, with RDS PostgreSQL, SQS, and private endpoints to "
               "AgentCore Gateway, Bedrock Guardrails, secrets, AppConfig, X-Ray and CloudWatch; on the right Transit Gateway to plants and SAP, the data platform, "
               "the Hyderabad replica, log-archive and shared services")


def fig_libs():
    n = 24
    b = ""
    # agents
    b += t(40, 22, "AGENTS · domain code only", 12, bold=True, anchor="start")
    b += cell(n, 40, 32, 190, 52, "claims_fnol", "motor claims agent (built)", WASH["rose"])
    b += cell(n, 240, 32, 190, 52, "dealer assistant", "tyre maker (next)", WASH["rose"])
    b += cell(n, 440, 32, 200, 52, "config/<env>.yaml", "local · azure · aws (new)", WASH["butter"])
    # specs
    b += t(690, 22, "SPECS AND CATALOGS · data, not code", 12, bold=True, anchor="start")
    b += cell(n, 690, 32, 130, 52, "Guardrail catalog", "rule ids, places", "#F1F1EF")
    b += cell(n, 830, 32, 130, 52, "AOAS · AHC · AAC", "what must be true", "#F1F1EF")
    b += cell(n, 690, 92, 270, 36, "stacks/azure.yaml · stacks/aws.yaml", "", "#F1F1EF")
    # harness
    b += f'<rect x="40" y="150" width="600" height="190" rx="14" fill="{WASH["peri"]}" stroke="{INK}" stroke-width="2"/>'
    b += t(56, 174, "agent-harness · the core library (unchanged)", 16, hand=True, anchor="start")
    mods = ["loop", "context", "tools + gating", "policy", "approvals", "cost meter", "telemetry", "watch", "replay"]
    for i, m in enumerate(mods):
        b += cell(n, 54 + (i % 5) * 116, 184 + (i // 5) * 46, 108, 36, m, "", "#fff")
    b += f'<rect x="54" y="282" width="572" height="46" rx="10" fill="{WASH["lilac"]}" stroke="{INK}" stroke-width="1.4" stroke-dasharray="5 4"/>'
    b += t(340, 300, "ports (adapters/): model · state · identity · secrets · config", 12, bold=True)
    b += t(340, 318, "telemetry · waits · tools · records · cost ledger", 12, bold=True)
    # evalharness + agenttwin
    b += f'<rect x="690" y="150" width="270" height="118" rx="14" fill="{WASH["mint"]}" stroke="{INK}" stroke-width="2"/>'
    b += t(704, 174, "evalharness · eval framework", 16, hand=True, anchor="start")
    b += t(825, 198, "ports: Evaluator · TraceSource", 12)
    b += t(825, 216, "Judge · ResultSink", 12)
    b += t(825, 240, "domain patterns · cost rules", 12, fill="#444")
    b += t(825, 256, "five positions, input to release", 12, fill="#444")
    b += f'<rect x="690" y="284" width="270" height="56" rx="14" fill="#fff" stroke="{INK}" stroke-width="1.6" stroke-dasharray="6 5"/>'
    b += t(825, 306, "agenttwin · pretend worlds", 14, bold=True)
    b += t(825, 324, "tests and gates only", 12, fill="#444")
    # arrows: agents -> harness, harness -> evalharness, agent -.-> agenttwin, specs -> things
    b += arrow(n, "M135 86 L135 148")
    b += arrow(n, "M335 86 L335 148")
    b += arrow(n, "M540 86 C540 120 560 260 560 280")
    b += arrow(n, "M642 210 L688 210")
    b += arrow(n, "M400 86 C450 132 665 118 665 200 L665 288 C665 302 674 310 688 312", dash=True)
    b += arrow(n, "M720 86 C700 120 650 130 610 182")
    b += arrow(n, "M760 86 L760 148")
    b += arrow(n, "M688 110 C668 106 660 70 644 62")
    # open source
    b += t(40, 376, "OPEN SOURCE UNDERNEATH", 12, bold=True, anchor="start")
    oss = [("Pydantic AI", "model layer"), ("DBOS", "durable waits"), ("MCP SDK", "tools"), ("OpenTelemetry", "SDK + OTLP"),
           ("psycopg", "PostgreSQL"), ("Pydantic", "contracts"), ("Starlette", "HTTP edge")]
    for i, (a, sub) in enumerate(oss):
        b += cell(n, 40 + i * 132, 386, 124, 46, a, sub, WASH["sky"])
    b += arrow(n, "M340 342 L340 384")
    # extras
    b += t(40, 470, "CLOUD EXTRAS · pip install agent-harness[azure] or [aws], evalharness[azure] or [aws]", 12, bold=True, anchor="start")
    b += f'<rect x="40" y="480" width="440" height="118" rx="14" fill="#F1F1EF" stroke="{INK}" stroke-width="1.4"/>'
    b += t(56, 502, "[azure] · built", 15, hand=True, anchor="start")
    for i, line in enumerate(["model → APIM AI gateway", "state → Azure PostgreSQL · sign-in → Entra ID",
                              "secrets → Key Vault · config → App Configuration", "telemetry → Azure Monitor · guardrails → Content Safety",
                              "evals → Azure AI evaluation, App Insights traces"]):
        b += t(56, 522 + i * 16, E(line), 12, anchor="start")
    b += f'<rect x="520" y="480" width="440" height="118" rx="14" fill="{WASH["butter"]}" stroke="{INK}" stroke-width="2.4"/>'
    b += t(536, 502, "[aws] · new, step R1", 15, hand=True, anchor="start")
    for i, line in enumerate(["model → AgentCore Gateway → Bedrock", "state → RDS PostgreSQL · sign-in → Cognito + our issuer",
                              "secrets → Secrets Manager · config → AppConfig", "telemetry → OTLP → ADOT · guardrails → Bedrock Guardrails",
                              "evals → AgentCore Evaluations, CloudWatch traces"]):
        b += t(536, 522 + i * 16, E(line), 12, anchor="start")
    b += arrow(n, "M168 330 L168 478", dash=True)
    b += arrow(n, "M564 330 L564 478")
    b += arrow(n, "M900 270 C985 360 985 440 900 478")
    return svg(n, 1000, 610, b, "Library dependencies: agents depend on the agent-harness core library, which depends on evalharness and on open-source "
               "libraries; agenttwin is used by tests only; specs and the guardrail catalog feed the harness and the eval framework; "
               "cloud extras [azure] (built) and [aws] (new) bind the ports to cloud services")


def tiers_html():
    out = []
    for tid, name, plain, rows in TIERS:
        out.append(f'<h3 id="{tid.lower()}">{tid} · {E(name)}</h3><p>{E(plain)}</p>'
                   '<div class="sd-table wide"><table><tr><th>Decision</th><th>We use</th><th>Not used</th><th>Why</th></tr>')
        out += [f"<tr><td><b>{E(d)}</b></td><td>{E(u)}</td><td>{E(nu) or '—'}</td><td>{E(w)}</td></tr>" for d, u, nu, w in rows]
        out.append("</table></div>")
    return "".join(out)


IMPL = [
 ("R0", "Binding written down", "clean-ai-engineering/stacks/aws.yaml: every port named with its AWS adapter", "done on paper (19 Oct)"),
 ("R1", "AWS adapters", "In the agent_harness library: agentcore-gateway, rds-postgresql, cognito + our token issuer, secrets-manager, appconfig, otel → ADOT; a contract test per port, the same tests the Azure adapters pass", "done (3 Nov), tested offline; live recordings wait for an AWS account"),
 ("R2", "The FNOL agent on AWS, unchanged", "Add config/aws.yaml to the motor-claims FNOL agent: a new overlay, no change to the agent's code. This proves that only the binding changes", "planned"),
 ("R3", "Infrastructure as code", "Terraform for H0 to H8 at dev size (one account, budget alarm), checked offline first", "planned"),
 ("R4", "Running on AWS", "Deploy to AWS dev; first claim end to end, traced in X-Ray through ADOT", "planned"),
 ("R5", "Tyre dealer assistant", "The second agent on the same stack: SAP and dealer-system MCP servers against an AgentTwin dealer world", "planned"),
]



REUSE = [
 ("Agent harness library (agent_harness)", "Loop, context assembler, tool gating, DBOS approvals, telemetry helper, ports and adapters, the four offline gates with AgentTwin",
  "Unchanged. Add the AWS adapters (model, state, identity, secrets, config, telemetry); each passes the contract tests the Azure ones pass. Offline gates run in GitHub Actions and need no cloud."),
 ("Guardrail catalog", "Every check, with its id, what it catches and where it may run",
  "The catalog stays the source of truth. Each rule is bound to a place: our code inside the loop (most rules), Bedrock Guardrails at the gateway for detector-type checks (prompt attack, harmful content, PII), the eval framework for online and release checks. Same rule id everywhere, so one report covers all places."),
 ("Eval framework (evalharness)", "Evaluator, TraceSource, Judge and ResultSink ports; domain patterns; cost rules; five positions",
  "Add AWS adapters: a trace source that reads OpenTelemetry spans from CloudWatch, Bedrock Guardrails and AgentCore Evaluations as evaluator providers, Bedrock as a judge model, and a result sink that writes scores back as OpenTelemetry evaluation events to CloudWatch. Nightly online run as a scheduled ECS task."),
 ("Trace viewer (the LangSmith job)", "We never built our own; local dev uses self-hosted Langfuse",
  "Production: CloudWatch generative AI observability, fed by the same ADOT pipeline, with our scores written next to the traces. Langfuse on ECS is an optional second destination for teams that want prompt playground and annotation queues; adding it is a collector config change."),
]



AGENTCORE = [
 ("Gateway", "Use", "The one door to models and MCP tools: any provider, fallback, request and token limits per user, guardrails at the door.", "Our gateway policy (allow-list per job, budgets) rides on it"),
 ("Policy", "Use", "Cedar rules on who may call which tool; Bedrock Guardrails at the gateway for detector-type checks.", "Rules from our guardrail catalog that are detector-shaped"),
 ("Observability", "Use", "Shows our OpenTelemetry traces in CloudWatch; nothing to install in our code.", "Our telemetry helper + ADOT"),
 ("Evaluations", "Use, as a plug-in", "One more evaluator provider inside our eval framework, including online evaluation of live traces.", "evalharness decides what runs where"),
 ("Identity", "Not now", "Token vault and OAuth to third-party tools. Add it when a SaaS tool needs a user's consent.", "Our on-behalf-of token issuer for SAP and the dealer system"),
 ("Memory", "No", "Our memory must follow our retention and erasure rules and sit next to the approvals.", "Memory tables in RDS PostgreSQL"),
 ("Runtime", "Not now", "Managed hosting for agent containers; worth a pilot later.", "ECS on Fargate"),
 ("Managed harness", "No", "AWS runs the loop, memory and evaluation for you.", "Our loop, the part we keep on every cloud"),
 ("Code Interpreter, Browser", "No", "No tyre-company job needs them yet.", "—"),
 ("Agent Registry", "No", "Not offered in Mumbai.", "Catalogue file in Git"),
]


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
    ("How do approvals wait?", "DBOS on RDS PostgreSQL · Step Functions task tokens",
     "DBOS: the same code as on Azure, state in the PostgreSQL we already run.",
     "Pursue: DBOS", "Step Functions works, but it is one more service and AWS-only."),
    ("How do dealers and customers sign in?", "Amazon Cognito · federate the existing dealer portal over OIDC",
     "Cognito user pool, federating the dealer portal over OIDC.",
     "Pursue: Cognito + portal federation", "Dealers keep one login; the harness only needs a verified token."),
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
    ("Database", "Azure Database for PostgreSQL", "Amazon RDS for PostgreSQL"),
    ("Queue", "Service Bus", "SQS FIFO"),
    ("Traces and metrics", "OpenTelemetry → Application Insights", "OpenTelemetry → ADOT collector → X-Ray + CloudWatch"),
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
<div><b>India first</b>Mumbai, with Hyderabad for disaster recovery; a Frankfurt copy of the same stack only when EU personal data arrives</div>
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

<section id="design"><p class="eyebrow">End to end</p><h2>The design, from account to release</h2>
<p>This is a reference architecture, so every choice below is made. The tyre maker is only the example. Read the drawing first, then follow one request through it, then the nine design tiers (H0 to H8).</p>
{fig(fig_deploy(), "The production account in Mumbai. The dark box is our code: the router, the loop and the agents. Everything telemetry-related flows through OpenTelemetry into the ADOT sidecar, then on to X-Ray and CloudWatch. Dashed arrow: the replica in Hyderabad.")}
<h3>One request, step by step</h3>
<div class="sd-table"><table><tr><th>#</th><th>Where</th><th>What happens</th></tr>
{"".join(f"<tr><td>{i}</td><td><b>{E(w)}</b></td><td>{E(d)}</td></tr>" for i, (w, d) in enumerate(WALK, 1))}
</table></div>
{tiers_html()}
</section>

<section><p class="eyebrow">Every concern, bound to AWS</p><h2>The 22 concerns, one table</h2>
<p>For each concern: what AWS offers and whether we use it, the open-source options, and what we code once for every agent, and why.</p>
<p class="aw-key"><span class="aw-mark use">use</span> in the design &nbsp; <span class="aw-mark plan">planned</span> next phase &nbsp; <span class="aw-mark list">considered</span> not picked, or newer service to check &nbsp; <span class="aw-mark no">not used</span> and why</p>
{binding_table()}
<p class="aw-key">Services marked "check current status" are newer AWS offerings; confirm their availability in Mumbai and Hyderabad (and Frankfurt, if the EU copy is built) before relying on them.</p>
</section>

<section><p class="eyebrow">Who builds what</p><h2>What AWS gives, what we build, what each agent writes</h2>
<p>For each concern, how much does AWS give us, how much do we code once for every agent, and how much does each agent team still write? AWS gives the plumbing. The parts that make an agent safe for dealers and customers stay in our code.</p>
{fig(fig_split(), "Our judgement, not a measurement. AWS gives the plumbing (gateway, identity, storage, logging); the parts that make an agent trustworthy stay in our code.")}
<p>The rule that keeps this healthy: when two agents write the same code, it moves into the shared middle (blue). When AWS catches up, it moves to the left (grey).</p></section>

<section><p class="eyebrow">The five big choices</p><h2>Decided, with the options we dropped</h2>
<div class="sd-table"><table>
<tr><th>Decision</th><th>Options</th><th>We chose</th><th>Verdict</th><th>Why</th></tr>
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

<section id="libs"><p class="eyebrow">How the code fits</p><h2>Library dependencies</h2>
<p>Agents hold only their domain code. Everything else comes from two libraries we own and a handful of open-source ones. Moving to AWS adds one install option, <code>[aws]</code>, to each library: new adapters behind the same ports, nothing else.</p>
{fig(fig_libs(), "Solid arrows: depends on. Dashed from the agent to agenttwin: tests only, never at run time. Dashed into [azure]: the extra we built. The yellow box is the only new code for AWS.")}
</section>

<section id="agentcore"><p class="eyebrow">AgentCore, part by part</p><h2>Which AgentCore parts we use</h2>
<p>AgentCore is AWS's set of building blocks for agents. We take the parts that are plumbing and keep the parts that make our agents ours.</p>
<div class="sd-table wide"><table><tr><th>AgentCore part</th><th>Verdict</th><th>Why</th><th>What of ours sits there</th></tr>
{"".join(f"<tr><td><b>{E(a)}</b></td><td><b>{E(v)}</b></td><td>{E(w)}</td><td>{E(o)}</td></tr>" for a, v, w, o in AGENTCORE)}
</table></div></section>

<section id="reuse"><p class="eyebrow">Reuse, don't rebuild</p><h2>What we already built, and how it lands on AWS</h2>
<div class="sd-table wide"><table><tr><th>Asset</th><th>What it is</th><th>On AWS</th></tr>
{"".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b_)}</td><td>{E(c)}</td></tr>" for a, b_, c in REUSE)}
</table></div>
<p>AWS's gateway gives the door: any model, fallback, rate and token limits per user, guardrails at the door. It does not give spend in money per turn or per business case, a retry budget per turn, rules at exact positions inside the loop, or replay. Those stay ours.</p></section>

<section id="impl"><p class="eyebrow">From design to running code</p><h2>The reference implementation</h2>
<p>The same path the motor-claims FNOL agent took on Azure: write the binding, write the adapters, add a configuration overlay, build the infrastructure, run it, then add the next agent. The agent's code and tests do not change.</p>
<div class="sd-table"><table><tr><th>Step</th><th>What</th><th>How</th><th>State</th></tr>
{"".join(f"<tr><td>{a}</td><td><b>{E(b_)}</b></td><td>{E(c)}</td><td>{E(d)}</td></tr>" for a, b_, c, d in IMPL)}
</table></div></section>

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
