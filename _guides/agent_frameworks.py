"""When to use an agent SDK or framework, and when to write the loop yourself, at /learn/agent-frameworks/.

    python3 _guides/agent_frameworks.py && python3 _site/nav.py && python3 _site/seo.py

Written 20 Nov 2026. The method (five positions, fourteen concerns, three archetypes, exit cost) is from our own
framework research notes; the product facts for Microsoft, Google, OpenAI, Anthropic and LangChain were checked against
public reports on 20 Nov 2026, several of them secondary sources, so the last section lists what to verify.
Public page: no employer, no account, no personal names.
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("data_systems_afw", ROOT / "_guides" / "data_systems.py")
ds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ds)
E, wb, SITE = ds.E, ds.wb, ds.SITE
URL = f"{SITE}/learn/agent-frameworks/"
OUT = ROOT / "learn" / "agent-frameworks" / "index.html"

CSS = """<style>
  main.wrap { max-width:1280px; }
  main.wrap > :not(.tw):not(.mm):not(.pos):not(.flow) { max-width:860px; }
  .tw { overflow-x:auto; }
  table.t { border-collapse:collapse; width:100%; font-size:14px; margin:10px 0 18px; min-width:1000px; }
  table.t td, table.t th { border:1.5px solid var(--ink); padding:7px 10px; text-align:left; vertical-align:top; } table.t th { background:var(--peri-wash); }
  table.t td.v { background:var(--rose-wash); width:220px; }
  .box { background:var(--butter-wash); border:1.5px solid var(--ink); border-radius:var(--wob); padding:14px 20px; margin:16px 0; }
  .mm { width:100%; height:auto; margin:10px 0 6px; } .mm text { font-family:var(--hand), sans-serif; fill:#1a1a1a; }
  .pos { display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:10px; margin:14px 0; }
  .pos div { border:1.5px solid var(--ink); border-radius:var(--wob); padding:10px 12px; font-size:14px; background:var(--peri-wash); }
  .pos div b { display:block; font-family:var(--hand); font-weight:400; font-size:21px; line-height:1.2; }
  .pos div:nth-child(2) { background:var(--butter-wash); } .pos div:nth-child(4) { background:var(--rose-wash); }
  .pos small { display:block; margin-top:6px; color:#444; }
  .flow { display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:12px; margin:14px 0; }
  .flow div { border:1.5px solid var(--ink); border-radius:var(--wob); padding:12px 16px; background:#fff; }
  .flow b { display:block; font-family:var(--hand); font-weight:400; font-size:22px; }
  @media (max-width:900px) { .pos { grid-template-columns:1fr; } }
</style>"""

POSITIONS = [
    ("1 · Plain loop", "You write about 200 lines: build the messages, call the model, run the tool, repeat to a cap.", "Everything: control flow, context, budget, errors."),
    ("2 · Provider tool-runner", "The model vendor's own SDK runs the loop over tools you define, with hooks for approval and errors. No built-in tools.", "Context policy, durability, delegation."),
    ("3 · Harness SDK", "Loop plus context management, permissions, built-in tools and a sandbox. Example: the Claude Agent SDK.", "Process shape, and survival past one session."),
    ("4 · Graph runtime", "Loop as a graph, with saved state, waits for a person and replay. Examples: LangGraph, Google ADK 2.0 workflows, Microsoft Agent Framework workflows.", "Context policy, autonomy, your own limits."),
    ("5 · Managed runtime", "A cloud runs the agent and its operations for you. Examples: Foundry hosted agents, Bedrock AgentCore, Google's agent runtime.", "Very little. The exit cost is the highest here."),
]

# name, position, what it gives, what you still own, model, cloud, exit cost, choose when, avoid when, verdict
OPTIONS = [
    ("Plain loop (your own code)", "1", "Nothing you did not write", "All of it", "Any", "Any", "None: it is yours",
     "Short stateless runs (3 to 8 tool calls, under a minute); you are learning; another system already owns durability; your control flow is unusual and you can name what a framework forbids.",
     "Runs that last hours, wait for people, or must be replayed. You will end up writing a framework with one maintainer.",
     "Default for short, simple agents. Also right when you must own the stop rules."),
    ("Provider tool-runner (for example Anthropic's tool runner, OpenAI's chat tools)", "2", "The loop over your tools, with hooks", "Context, durability, delegation, everything else", "One vendor's models (some adapters exist)", "Any", "Days: it is thin",
     "A simple agent that only needs tools and a few hooks, and you are happy with one model family.",
     "You need long runs, saved state or several model vendors.",
     "Often overlooked and often enough. Try it before a framework."),
    ("Claude Agent SDK", "3", "Loop, context compaction, permissions, hooks, sessions, built-in file and shell tools, sandboxing, MCP", "Durability past a session, identity, evaluation, cost limits", "Claude models only (also via Bedrock and Vertex)", "Any; Claude is reachable from the big three clouds", "Weeks; the model family is a business decision",
     "An autonomous worker that needs a computer: code, data, document or operations work where the path is not known in advance.",
     "A plain conversational service, or a case where you need another vendor's model.",
     "Pick it for autonomous workers on Claude. Keep state and traces yours."),
    ("OpenAI Agents SDK", "2 to 3", "Agents, handoffs between them, guardrails, tools, tracing, newer sandbox and sub-agent support", "Durable state, human approval flows, identity, cost limits", "Built around OpenAI's API; other models through adapters, check first", "Any; hosted agent products are separate and deeper", "1 to 3 weeks for the SDK; months if you adopt the hosted runtime",
     "A conversational service that routes to specialists: handoffs match the problem.",
     "Long-running work that must survive restarts or wait days for a decision.",
     "Pick it for conversational routing on OpenAI models."),
    ("LangGraph", "4", "Graph control flow, checkpointed state, waits for a person, replay, model-agnostic", "Context policy, sandboxing, safety rules, identity", "Any model", "Any", "4 to 8 weeks to re-platform; run history stays in your database",
     "Long-horizon processes: reconciliations, migrations, multi-day approvals, where durability and human steps are the point.",
     "A short stateless agent: you carry weight you do not use. Past a week of waiting, pair it with a workflow engine.",
     "Pick it for long-running, auditable, multi-model work."),
    ("Microsoft Agent Framework (Azure)", "4", "Agents, graph workflows, multi-agent patterns, .NET and Python, successor to Semantic Kernel and AutoGen (1.0 reported April 2026); hosting in Foundry", "Context policy, evaluation, identity mapping, cost limits", "Many models; strongest with Azure's", "Azure first, not Azure only", "Weeks; deeper if you use Foundry hosted agents",
     "You are an Azure and .NET shop, or you already run Semantic Kernel or AutoGen and are migrating.",
     "You are not on Azure and have no .NET code: a lighter choice may cost less.",
     "Pick it on Azure, especially for .NET teams."),
    ("Google ADK (GCP)", "4", "Agent building blocks, graph workflows in version 2, Python, Go, TypeScript and Java, runs locally or on Google's managed agent runtime", "Context policy, evaluation, identity mapping, cost limits", "Many models; strongest with Gemini", "Google Cloud first, runs anywhere", "Weeks; deeper with the managed runtime",
     "You are on Google Cloud or use Gemini and want Google's runtime and protocols (such as A2A).",
     "Another cloud is the home of your data and identity.",
     "Pick it on Google Cloud. Note the platform was renamed in 2026: check current names."),
    ("AWS: Strands Agents and Bedrock AgentCore", "3 to 5", "Open-source agent SDK; AgentCore adds a managed runtime, gateway, memory and identity", "Context policy, evaluation, the loop's stop rules if you want them yours", "Many models; strongest with Bedrock", "AWS first", "Weeks; months if you adopt the managed runtime fully",
     "You are on AWS and want the platform's identity, gateway and runtime.",
     "You need to own the loop's stop rules, or must stay portable across clouds.",
     "Pick on AWS if you accept the runtime lock; otherwise use it only for gateway and identity."),
    ("Managed agent products (Foundry hosted agents, Bedrock agents, Google's runtime)", "5", "Hosting, scaling, tracing, sometimes memory and identity", "Very little", "Per product", "That cloud", "Highest of all",
     "A small team, one cloud, no wish to operate infrastructure, and a use case the product fits.",
     "You need your own stop rules, portability or full trace ownership.",
     "Use for speed; plan the exit on day one."),
]


def mindmap():
    W, H = 1180, 800
    cx, cy = W / 2, H / 2
    branches = [
        ("Do you need the surroundings?", ["context that shrinks over a long run", "surviving a restart", "waiting days for a person", "replaying a past run", "none of these: plain loop"], (190, 130)),
        ("What kind of agent?", ["conversational, minutes: OpenAI Agents SDK", "long-horizon, days: LangGraph", "autonomous worker: Claude Agent SDK", "short and simple: plain loop"], (590, 90)),
        ("Who owns durability already?", ["a workflow engine or queue: plain loop", "nobody: a graph runtime", "the cloud: its managed runtime", "never two owners of restarts"], (990, 130)),
        ("Which models and cloud?", ["one vendor: its SDK", "many models: LangGraph, Google ADK, Microsoft", "Azure: Microsoft Agent Framework", "Google Cloud: ADK", "AWS: Strands, AgentCore"], (990, 640)),
        ("What does leaving cost?", ["keep state, traces, tool contracts yours", "managed runtimes lock deepest", "model family is a business lock", "write the revisit trigger"], (590, 710)),
        ("Who runs and maintains it?", ["team language: .NET, Python, TypeScript", "how fast the product renames", "who gets the 3 a.m. page", "pilot the task that breaks it"], (190, 640)),
    ]
    svg = [f'<svg class="mm" viewBox="0 0 {W} {H}" role="img" aria-label="Which agent SDK or framework: six questions">']
    for _, _, (x, y) in branches:
        svg.append(f'<line x1="{cx}" y1="{cy}" x2="{x}" y2="{y}" stroke="#1a1a1a" stroke-width="1.5"/>')
    svg.append(f'<ellipse cx="{cx}" cy="{cy}" rx="120" ry="56" fill="#fff" stroke="#1a1a1a" stroke-width="2"/>')
    svg.append(f'<text x="{cx}" y="{cy - 6}" text-anchor="middle" font-size="25">Which SDK or</text><text x="{cx}" y="{cy + 22}" text-anchor="middle" font-size="25">framework?</text>')
    fills = ["var(--peri-wash)", "var(--butter-wash)", "var(--rose-wash)"]
    for k, (title, leaves, (x, y)) in enumerate(branches):
        w = 330
        h = 40 + 21 * len(leaves)
        svg.append(f'<rect x="{x - w / 2}" y="{y - h / 2}" width="{w}" height="{h}" rx="14" fill="{fills[k % 3]}" stroke="#1a1a1a" stroke-width="1.5"/>')
        svg.append(f'<text x="{x}" y="{y - h / 2 + 25}" text-anchor="middle" font-size="19">{E(title)}</text>')
        for j, leaf in enumerate(leaves):
            svg.append(f'<text x="{x}" y="{y - h / 2 + 49 + 21 * j}" text-anchor="middle" font-size="14.5">{E(leaf)}</text>')
    svg.append("</svg>")
    return "".join(svg)


def positions():
    return '<div class="pos">' + "".join(f"<div><b>{E(a)}</b>{E(b)}<small><b style='font-family:inherit;font-size:13px'>You still own:</b> {E(c)}</small></div>" for a, b, c in POSITIONS) + "</div>"


def options_table():
    head = ["Option", "Position", "What it gives you", "What you still own", "Models", "Cloud", "Exit cost", "Choose it when", "Avoid it when", "Verdict"]
    out = '<div class="tw"><table class="t"><tr>' + "".join(f"<th>{E(h)}</th>" for h in head) + "</tr>"
    for r in OPTIONS:
        out += "<tr><td><b>" + E(r[0]) + "</b></td>" + "".join(f"<td>{E(c)}</td>" for c in r[1:9]) + f'<td class="v">{E(r[9])}</td></tr>'
    return out + "</table></div>"


def page():
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/agent-harness/">Agent Harness</a> › Agent frameworks</p>
<p class="eyebrow" style="margin-top:22px">AI · Agent Harness</p>
<h1>When to use an agent SDK or framework, and when to write the loop yourself</h1>
<p class="lede">The loop is small: build the messages, call the model, run the tool, repeat. A framework does not sell you the loop. It sells you what surrounds it: keeping the context under control on long runs, surviving a restart, waiting days for a person, and replaying a run. So the choice is one question: do you need the surroundings?</p>
<p class="note">Written 20 November 2026. The method is from our own framework research notes. Product facts were checked against public reports on that date, several of them secondary, and these products change fast. The last section says what to verify.</p>
<h2>The mind map: six questions</h2>
<p>Work round it in order. Most teams answer the first two and stop; the last four are where choices go wrong a year later.</p>
{mindmap()}
<h2>Five positions, not two</h2>
<p>"No framework" and "framework" hide five different things. Most simple agents belong in position 1 or 2 and never need more.</p>
{positions()}
<h2>The options side by side</h2>
<p>One row per option, with a verdict. Scroll sideways on a small screen.</p>
{options_table()}
<h2>A decision path in four steps</h2>
<div class="flow"><div><b>1 · Do you need the surroundings?</b>Write what your agent does in plain sentences first. If runs are short and a crash means an acceptable retry, stop here: write the loop, or use the model vendor's tool-runner.</div>
<div><b>2 · Does something else own durability?</b>If a workflow engine, a job scheduler or a queue already handles retries and restarts, keep the inner loop plain. Two systems that both think they own restarts will disagree at the worst moment.</div>
<div><b>3 · What shape is the work?</b>Conversational and routing: handoff-style SDKs. Long-horizon with waits for people: a graph runtime. Autonomous and needs a computer: a harness SDK. Then let your cloud and model choice break ties.</div>
<div><b>4 · Can you leave?</b>Whatever you pick, state, traces and tool contracts stay yours. Write down the trigger that would make you revisit, for example "runs exceed an hour" or "approvals enter the flow".</div></div>
<h2>Six situations where a plain loop wins</h2>
<ul><li><b>Short, stateless runs.</b> This is the commonest case and the one where adopting a framework is most often reflex, not reasoning.</li>
<li><b>You are learning the mechanics.</b> Build it once by hand and the concerns stop being a list.</li>
<li><b>Something else owns durability.</b> One durability system per run.</li>
<li><b>The control flow is unusual.</b> If you cannot name what the framework forbids, you do not have this case.</li>
<li><b>You must own the stop rules.</b> Step budget, repeat detection and cost ceiling live in the only place that sees the whole trajectory. We keep the loop ourselves for this reason and adopt everything around it.</li>
<li><b>Auditability.</b> The exact bytes sent to the model must be yours.</li></ul>
<h2>Where we landed, and why</h2>
<div class="box"><b>Our own agents keep the loop in-house and adopt the rest.</b> The loop is a small piece of code whose limits (steps, repeat detection, cost) must sit where the whole run is visible, so we write it. Around it we adopt: a model gateway, a database for state, a library for durable waits, OpenTelemetry for traces. Frameworks are a supported choice on our stacks, but the stack files for a Claude Agent SDK stack and a LangGraph stack are still placeholders: we have not built agents on them, so we do not claim a verdict from experience. Our scores for each framework are a dated starting hypothesis, not a measurement.</div>
<h2>How to run the choice</h2>
<ul><li><b>Mark the concerns first.</b> Take the list of fourteen concerns and mark each Must, Should or Won't. At most five Musts. The Won'ts are the most useful marks, because they let you reject a capable product cleanly.</li>
<li><b>Count what you would still build.</b> For each candidate, list the Musts it scores low on. That is your build list. Identity, evaluation and cost limits are supplied by none of them.</li>
<li><b>Pilot two tasks.</b> One representative real task, and one that breaks things: a long run, an approval, a tool failing halfway, an adversarial user. Every framework demos well on the first. Differences show only in failure.</li>
<li><b>Write the decision down</b> with the alternatives, what you accepted, the exit cost and the trigger to revisit.</li></ul>
<h2>Check before you rely on this</h2>
<ul><li><b>Names and versions move.</b> The Microsoft framework merged Semantic Kernel and AutoGen (reported 1.0 in April 2026). Google's agent platform was renamed during 2026 and reports disagree on ADK version dates. The Claude Agent SDK was formerly the Claude Code SDK.</li>
<li><b>Model support.</b> Whether the OpenAI SDK works well with non-OpenAI models, and which models each cloud's framework supports, should be tested on your own task.</li>
<li><b>Hosted runtimes.</b> Features, regions and exit paths differ by cloud and change; read the vendor's current documentation.</li>
<li><b>Sources used for the product facts</b> (mostly secondary reports; confirm against vendor pages): <a href="https://visualstudiomagazine.com/articles/2026/04/06/microsoft-ships-production-ready-agent-framework-1-0-for-net-and-python.aspx">Visual Studio Magazine on Microsoft Agent Framework 1.0</a>, <a href="https://infoq.com/news/2026/08/agent-framework-harness-ga">InfoQ on the Agent Framework harness</a>, <a href="https://developers.googleblog.com/en/agents-adk-agent-engine-a2a-enhancements-google-io/">Google Developers Blog on ADK and Agent Engine</a>, <a href="https://rubinlake.com/en/technology-radar/ai-and-data-engineering/google-adk">Rubin Lake radar on Google ADK</a>, <a href="https://dev.to/dibi8/claude-agent-sdk-vs-openai-agents-sdk-in-2026-which-to-build-on-16p8">Claude Agent SDK vs OpenAI Agents SDK</a>, <a href="https://wetheflywheel.com/en/comparisons/claude-agent-sdk-vs-openai-agents-sdk-vs-langgraph/">Claude Agent SDK vs OpenAI Agents SDK vs LangGraph</a>.</li></ul>
<h2>Where to go next</h2>
<ul><li><a href="/learn/agent-harness-stack-map/">Agent harness architecture map</a>: what fills each concern on each cloud.</li>
<li><a href="/learn/agent-harness/">Agent Harness: the course</a>.</li>
<li><a href="/learn/ai-gateways/">AI gateways: which one to use</a>.</li>
<li><a href="/learn/agent-guardrails/">Agent guardrails</a>.</li></ul>"""
    desc = ("When to use an agent SDK or framework and when to write the loop yourself: Claude Agent SDK, OpenAI Agents SDK, LangGraph, "
            "Microsoft Agent Framework, Google ADK, AWS and a plain loop, with a mind map of the six questions and a verdict for each.")
    return wb.page("When to use an agent SDK or framework", desc, URL, body,
                   ds.CSS + CSS + ds.ld("When to use an agent SDK or framework", desc, URL, [("Agent Harness", "/learn/agent-harness/"), ("Agent frameworks", "/learn/agent-frameworks/")]))


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page())
    print("agent frameworks ->", OUT)


if __name__ == "__main__":
    main()
