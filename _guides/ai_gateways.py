"""AI gateways: which one to use, where it runs and what it costs, at /learn/ai-gateways/.

    python3 _guides/ai_gateways.py && python3 _site/nav.py && python3 _site/seo.py

Written 19 Nov 2026 from the Databricks agent build. Vendor features and prices are from the authors' knowledge
and the Databricks CLI's own help, not from testing every product: the page says so and lists what to verify.
Public page: no employer, no account, no personal names.
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("data_systems_aigw", ROOT / "_guides" / "data_systems.py")
ds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ds)
E, wb, SITE = ds.E, ds.wb, ds.SITE
URL = f"{SITE}/learn/ai-gateways/"
OUT = ROOT / "learn" / "ai-gateways" / "index.html"

CSS = """<style>
  .tw { overflow-x:auto; } table.t { border-collapse:collapse; width:100%; font-size:14.5px; margin:10px 0 18px; }
  table.t td, table.t th { border:1.5px solid var(--ink); padding:7px 10px; text-align:left; vertical-align:top; } table.t th { background:var(--peri-wash); }
  .box { background:var(--butter-wash); border:1.5px solid var(--ink); border-radius:var(--wob); padding:14px 20px; margin:16px 0; }
  .steps { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; margin:14px 0; }
  .steps div { border:1.5px solid var(--ink); border-radius:var(--wob); padding:12px 16px; background:var(--peri-wash); }
  .steps b { display:block; font-family:var(--hand); font-weight:400; font-size:23px; }
  .qa b { display:block; font-family:var(--hand); font-weight:400; font-size:22px; margin-top:14px; }
</style>"""

GATEWAYS = [
    ("Databricks AI Gateway", "Databricks, managed", "Settings on a model endpoint (UI, API or CLI)", "Workspace token or OAuth",
     "Databricks-hosted models, plus external models you register", "Databricks system tables and log tables in Delta", "Built-in safety and PII options on supported endpoints",
     "Agents whose models and data live in Databricks"),
    ("Azure API Management (AI gateway features)", "Azure, managed", "Policies on an API, written in XML", "Subscription key in a header, plus Entra sign-in",
     "Whatever backend you point it at", "Application Insights and Log Analytics", "Azure AI Content Safety, called from a policy",
     "Apps that run on Azure"),
    ("AWS AgentCore Gateway and Bedrock", "AWS, managed", "Gateway targets and guardrail settings", "AWS identity (signed requests) or a token",
     "Bedrock models and OpenAI-compatible providers", "CloudWatch", "Bedrock Guardrails",
     "Apps that run on AWS"),
    ("LiteLLM proxy", "You host it", "One YAML file", "Virtual keys it issues, with budgets", "Over a hundred providers",
     "Its own database, or Langfuse and similar", "Integrations with outside guardrail tools",
     "Laptops, prototypes, developer tools, and teams with no enterprise gateway"),
    ("Kong AI Gateway", "You host it, or Kong's cloud", "Plugins in declarative config", "Key, OAuth or OIDC plugins", "Several providers through its AI plugin",
     "Kong's log and metrics plugins", "Prompt-guard and PII plugins; can call cloud guardrail services (some in paid tiers)",
     "A company that already runs Kong and wants one policy across clouds"),
]

FACTORS = [
    ("Who owns policy and the audit trail", "If a security or platform team already owns a central gateway, model traffic goes through it, even if another would be neater."),
    ("Where the caller and the model sit", "Databricks agent to a Databricks-hosted model, Azure app to Azure's model service, or an app outside both."),
    ("Where identity lives", "Entra passthrough, workspace identity, or a key."),
    ("Who has to run it", "A managed service costs less in people than one you patch and keep available yourself."),
    ("Data terms", "Region, retention, zero-retention terms, private networking, and whether the provider is already an approved subprocessor."),
    ("Existing commitments", "A spend commitment or negotiated discount on one cloud can make one route much cheaper."),
    ("Feature parity", "A model's newest features (prompt caching, extended thinking, batch, structured output) tend to arrive first on the provider's own API and can lag on hosted versions."),
    ("Built-in guardrails", "A tie-breaker, not the decider: see below."),
]

COSTS = [
    ("Databricks AI Gateway", "No separate gateway charge that we know of. You pay for model usage, plus storage and compute for any log tables."),
    ("Azure API Management", "Priced per tier, from cheap per-call tiers to thousands of dollars a month at the top. The cheapest tier lacks token-limit and per-key rate-limit policies, so the tier you need decides the cost."),
    ("LiteLLM", "The software is free and adds no per-token markup. You pay for the containers, a database, high availability and logs, then people's time to run, patch and secure it. An enterprise licence exists for features such as single sign-on and stronger audit, by quote."),
    ("Kong", "Open source is free. Enterprise and cloud versions are licensed, typically a large annual figure. You also pay hosting and operations."),
    ("The model tokens", "Usually the largest cost, and it does not change with the gateway. The host sets the per-token price, and the same model can cost differently on different hosts."),
]

QA = [
    ("If the same model is on Azure, Databricks and through Kong, which do I call?", "Choose the model by running your own test set. Then choose the route by contract, data terms, feature parity and capacity. Then choose the gateway by who enforces policy. Re-run the test set on each route, because the host or gateway can add filters or change limits."),
    ("Should I stack two gateways?", "Avoid it. Two gateways on one path doubles latency, duplicates limits and splits the logs, so nobody can say which one blocked a call. If a central gateway must be the door, the platform gateway behind it should observe and pass through."),
    ("Which gateway do we use for our own agents?", "On Databricks we use the Databricks AI Gateway, which is attached to the hosted model endpoint with usage tracking on by default; we configure nothing else on it. On Azure the design uses API Management. On a laptop, LiteLLM. The harness hides the difference behind one model port."),
    ("Does a gateway replace our own guardrails?", "No. A gateway can't know that a drug-safety draft's statistic must equal what a tool returned, or that a draft must never say a drug causes an event. Those checks stay in the harness."),
]


def table(head, rows):
    out = '<div class="tw"><table class="t"><tr>' + "".join(f"<th>{E(h)}</th>" for h in head) + "</tr>"
    for r in rows:
        out += "<tr>" + f"<td><b>{E(r[0])}</b></td>" + "".join(f"<td>{E(c)}</td>" for c in r[1:]) + "</tr>"
    return out + "</table></div>"


def page():
    qa = '<div class="qa">' + "".join(f"<b>{E(q)}</b><p>{E(a)}</p>" for q, a in QA) + "</div>"
    body = f"""<p class="crumbs"><a href="/">Home</a> › AI gateways</p>
<p class="eyebrow" style="margin-top:22px">AI · Concepts</p>
<h1>AI gateways: which one, where it runs, what it costs</h1>
<p class="lede">An AI gateway is a control point in front of model calls: one address, one set of keys, limits, usage records, logs and checks. Organisations often end up with several (a cloud's, a data platform's, an open-source one), and the same model reachable through all of them. This page gives a way to choose, covers guardrails and cost, and treats developer tools such as coding assistants separately from your own agents.</p>
<p class="note">Written 19 November 2026. Vendor features and prices come from the authors' knowledge and product help, not from testing every product, and they change often. The last section lists what to check before relying on it.</p>
<h2>The short answer</h2>
<p>You are making three separate decisions, in this order. Do not let one decide the others.</p>
<div class="steps"><div><b>1 · The model</b>Choose by running your own test set on each candidate: accuracy, tool use, cost per task, speed. Not by platform.</div>
<div><b>2 · The route</b>Choose the host by contract, data terms, feature parity, capacity and existing commitments. This sets who bills the tokens.</div>
<div><b>3 · The gateway</b>Choose by who enforces policy and owns the audit trail. Use one enforcement point per path.</div></div>
<h2>The gateways compared</h2>
<p>They do the same job: take a chat request, apply limits and checks, forward it, record usage. They differ in who runs them, how you sign in, how policy is written and where the logs go. A policy written for one is not portable to another.</p>
{table(["Gateway", "Who runs it", "Where you configure it", "How callers sign in", "Which models", "Usage and logs", "Guardrails", "Fits"], GATEWAYS)}
<h2>What decides it</h2>
<table class="t"><tr><th>Factor</th><th>Why it matters</th></tr>{''.join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td></tr>" for a, b in FACTORS)}</table>
<h3>A default that works for most organisations</h3>
<ul><li><b>Enterprise apps and agents calling external or cross-cloud models:</b> the existing enterprise gateway, whichever the security team owns. Egress rules, data-loss checks and quotas belong there.</li>
<li><b>Agents inside Databricks calling Databricks-hosted models:</b> Databricks AI Gateway, for per-endpoint limits, guardrails and cost in system tables.</li>
<li><b>Apps on Azure calling Azure's model service:</b> Azure API Management.</li>
<li><b>Laptops and prototypes:</b> LiteLLM.</li></ul>
<div class="box"><b>One enforcement point per path.</b> If a central gateway must be the door, the platform gateway behind it observes and passes through. Stacking enforcement doubles latency, duplicates limits and splits the logs.</div>
<h2>Guardrails: built in, and what they cannot do</h2>
<p>Each route offers some: a safety filter and PII options (Databricks), Azure AI Content Safety with jailbreak and groundedness checks (Azure), Bedrock Guardrails (AWS), plugins and integrations (Kong, LiteLLM), and the safety training built into the model. Treat them as a tie-breaker, not the decider.</p>
<ul><li><b>Generic checks miss domain rules.</b> A gateway cannot know that a drug-safety draft's statistic must equal what a tool returned. Those checks live in the agent harness, on every cloud.</li>
<li><b>False positives are real.</b> A generic safety filter can block legitimate text in some fields. Pharmacovigilance text routinely contains terms such as suicidal ideation. Test any filter on your own text; a filter that blocks work gets switched off.</li>
<li><b>Compare:</b> categories covered; block, flag or mask modes; whether tool outputs and retrieved text are checked for hidden instructions and not only the user's prompt; false-positive rate on your data; whether every decision is logged; added latency and per-call cost.</li></ul>
<h2>What it costs</h2>
<p>You pay in layers: the tokens (set by the host), the gateway (a tier fee, a licence, or hosting plus people), and logging and network transfer. A gateway in front of a host does not change the host's token price.</p>
{table(["Item", "Cost shape"], COSTS)}
<p class="note">These are shapes, not quotes. Get a price for your expected volume from each route before you decide.</p>
<h2>Developer tools are a separate problem</h2>
<p>Coding assistants and chat tools carry your source code, so the same question comes up for them. There are two kinds of traffic.</p>
<ul><li><b>Tools that call a model API</b> and let you set the endpoint and key, or use a cloud provider's model service (for example Claude Code and the OpenAI command-line tools). These can go through a gateway.</li>
<li><b>Tools that call their own vendor's backend</b>: ChatGPT and Claude in the browser, and most editor assistants. A gateway cannot sit in front of them. You control them with the vendor's enterprise plan (single sign-on, retention and no-training terms), network and data-loss controls, and a written list of approved tools.</li></ul>
<h3>Which gateway for coding traffic</h3>
<table class="t"><tr><th>Option</th><th>Where it runs</th><th>Good when</th></tr>
<tr><td><b>LiteLLM proxy</b></td><td>Containers in your own cloud account with a small database, behind your network and single sign-on</td><td>No enterprise AI gateway yet, or you want per-developer keys and budgets quickly. It accepts Anthropic's request format, so streaming, tool calls and prompt caching pass through.</td></tr>
<tr><td><b>Kong or Azure API Management</b></td><td>Wherever your enterprise gateway already runs</td><td>One is already the approved door. It must pass the provider's request format and streaming through unchanged, so test that first.</td></tr>
<tr><td><b>The model through your cloud</b> (Bedrock, Vertex, or Microsoft's Foundry, where offered)</td><td>Nothing new to install; the tool uses your cloud identity</td><td>You already have a cloud agreement. Spend, limits and logs come from the cloud's tools.</td></tr>
<tr><td><b>Databricks AI Gateway</b></td><td>Part of Databricks</td><td>Not a first choice for developer coding traffic; it fits agents inside Databricks.</td></tr></table>
<h3>What it costs, and what to protect</h3>
<ul><li>The model tokens are the big cost and the gateway does not change them. Heavy daily coding use can run to tens or hundreds of dollars per developer per month.</li>
<li>Running LiteLLM: a small cloud bill (containers, a database, logs), plausibly one to a few hundred dollars a month, rising with traffic. This is an estimate. The larger cost is the people who run, patch, secure and keep it available.</li>
<li><b>Check how developers are billed.</b> On seat subscriptions the traffic goes to the vendor under each person's sign-in, and a gateway cannot meter it per developer the way it does for API keys. Using a gateway usually means moving to API-key billing. Compare the two on real usage.</li>
<li><b>Protect the logs.</b> Prompts contain source code. Restrict who can read the gateway's logs, set a short retention, and keep developer traffic in its own namespace with its own keys, budgets and retention, apart from production agents.</li>
<li>Confirm your vendor terms say API and commercial inputs are not used for training.</li></ul>
<h2>Questions</h2>
{qa}
<h2>Check before you rely on this</h2>
<ul><li>Each product's current guardrail features and which tier includes them.</li>
<li>Current prices, from each vendor, for your expected volume.</li>
<li>Whether each developer tool you use supports a custom endpoint today; test one small team first.</li>
<li>That a gateway passes streaming, tool calls and prompt caching through for your model.</li></ul>
<h2>Where to go next</h2>
<ul><li><a href="/learn/agent-harness-databricks/">The agent harness on Databricks</a>: how a real agent uses a gateway and handles guardrails, concern by concern.</li>
<li><a href="/learn/databricks-ai-agent/">Build an agent on Databricks</a>: each Databricks AI service explained.</li>
<li><a href="/learn/ai-governance/">AI governance: running AI you can trust</a>.</li>
<li><a href="/learn/agent-guardrails/">Agent guardrails</a>.</li></ul>"""
    desc = "AI gateways compared: Databricks AI Gateway, Azure API Management, AWS, LiteLLM and Kong. How to choose, where each runs, what built-in guardrails can and cannot do, what it costs, and what to do about developer coding tools."
    return wb.page("AI gateways: which one, where it runs, what it costs", desc, URL, body, ds.CSS + CSS + ds.ld("AI gateways", desc, URL, [("AI gateways", "/learn/ai-gateways/")]))


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page())
    print("ai gateways ->", OUT)


if __name__ == "__main__":
    main()
