"""Which AI model for which job, at /learn/which-model/.

    python3 _guides/which_model.py && python3 _site/nav.py && python3 _site/seo.py

Written 20 Nov 2026. No benchmark numbers are quoted: leaderboards disagree and age within weeks. The page gives a pick per
kind of work and a way to test. Model names come from vendor documentation and public reports of 20 Nov 2026 (several
secondary), so the last section lists what to verify. Public page: no employer, no account, no personal names.
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("data_systems_wm", ROOT / "_guides" / "data_systems.py")
ds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ds)
E, wb, SITE = ds.E, ds.wb, ds.SITE
URL = f"{SITE}/learn/which-model/"
OUT = ROOT / "learn" / "which-model" / "index.html"

CSS = """<style>
  main.wrap { max-width:1240px; }
  main.wrap > :not(.tw):not(.steps) { max-width:860px; }
  .tw { overflow-x:auto; }
  table.t { border-collapse:collapse; width:100%; font-size:14.5px; margin:10px 0 18px; min-width:900px; }
  table.t td, table.t th { border:1.5px solid var(--ink); padding:7px 10px; text-align:left; vertical-align:top; } table.t th { background:var(--peri-wash); }
  table.t td.v { background:var(--rose-wash); }
  .box { background:var(--butter-wash); border:1.5px solid var(--ink); border-radius:var(--wob); padding:14px 20px; margin:16px 0; }
  .steps { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; margin:14px 0; }
  .steps div { border:1.5px solid var(--ink); border-radius:var(--wob); padding:12px 16px; background:var(--peri-wash); }
  .steps b { display:block; font-family:var(--hand); font-weight:400; font-size:23px; }
</style>"""

# job, what it needs, class of model, examples seen in November 2026, verdict
JOBS = [
    ("Building: coding, long edits, writing specifications and pages", "The best reasoning and the longest reliable work on a task. A person watches.", "The strongest frontier model you can pay for",
     "Claude's top tier (Opus or above), OpenAI's flagship, Gemini's top tier", "Pay for the frontier here. The cost is small next to your time, and a weaker model costs you rework."),
    ("An agent in production: tool calls in a loop, structured answers", "Reliable tool calling, valid JSON every time, follows instructions, steady cost per task.", "A mid-tier model, tested on your scenarios",
     "Claude's mid tier (Sonnet class), OpenAI's mid models, Gemini Flash class, or an open model such as gpt-oss-120b", "Pick the smallest model that passes your own scenarios, then keep re-testing. Do not start at the top."),
    ("Bulk and cheap: classify, extract, route, tidy text", "Speed and low cost; the task is narrow and checkable.", "A small model",
     "Claude's small tier (Haiku class), Gemini Flash-lite class, small open models", "Use the smallest that meets your accuracy bar on a labelled sample. Check the errors, not the average."),
    ("Judging other models' answers", "Better than what it grades, consistent, and ideally from a different family.", "The strongest model you can afford, checked against human labels",
     "A frontier model from a different vendor than the one being graded", "Calibrate it on cases people have labelled. An uncalibrated judge is an opinion."),
    ("Reading long documents and specifications", "Long context that is actually used, not just accepted.", "A long-context model, tested on your documents",
     "Gemini's long-context models, Claude's long-context options", "Test recall on your own files: plant a fact in the middle and ask for it."),
    ("Regulated or private data (health, pharma, finance)", "The data terms, the region, and who may see prompts.", "A model reached through your own cloud account or hosted by you",
     "Models offered by your data platform or cloud (for example Databricks Foundation Model APIs, Azure, Bedrock, Vertex) or open-weight models you host", "Where the model runs decides first, which model second. Read the retention and training terms."),
    ("Personal and learning projects, no budget", "Free, good enough, no card needed.", "A free hosted open-weight model",
     "gpt-oss-120b and Llama 3.3 70B on a free data-platform workspace (we ran both)", "Start free. Move up only when a test shows the free model fails."),
    ("Search by meaning (embeddings)", "A good embedding model and a stable one.", "An embedding model, not a chat model",
     "bge or gte class models on your platform", "Changing it means re-embedding everything, so pick once and record why."),
]

MEASURES = [
    ("Tool-call reliability", "Does it call the right tool with valid arguments, and stop when it should?"),
    ("Valid structure", "Does it return the JSON shape you asked for every time, or only usually?"),
    ("Grounding", "Does every number in its answer match what a tool returned? Count the exceptions."),
    ("Refusing correctly", "Does it decline what it must (advice, filing, claims of cause) and still help with what it may?"),
    ("Cost per successful task", "Not price per token: total cost of runs that finished correctly, including retries."),
    ("Speed", "Time to a finished task, and how it behaves under load."),
    ("Data terms", "Region, retention, training use, and whether your cloud already approves the provider."),
    ("Availability", "Is it offered in your region and on your platform today, and for how long?"),
]


def page():
    jobs = "".join(f'<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td>{E(c)}</td><td>{E(d)}</td><td class="v">{E(e)}</td></tr>' for a, b, c, d, e in JOBS)
    meas = "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td></tr>" for a, b in MEASURES)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/agent-harness/">Agent Harness</a> › Which model</p>
<p class="eyebrow" style="margin-top:22px">AI · Choosing</p>
<h1>Which AI model for which job</h1>
<p class="lede">There is no best model. There is a best model for each kind of work, and it changes every few months. So this page gives you a pick per job and a way to test, not a ranking. For data and agent work the rule is short: pay for the strongest model when you build, and use the smallest model that passes your own tests when an agent runs.</p>
<p class="note">Written 20 November 2026. No benchmark scores are quoted, because leaderboards disagree and age within weeks. This page was written with Claude, a model from one of the vendors discussed, which is a reason to trust the method (test it yourself) and not the picks. The last section lists what to verify.</p>
<h2>The short answer</h2>
<div class="steps"><div><b>1 · Build with the best</b>Coding, specifications and long edits: the strongest frontier model. A weaker one costs you rework.</div>
<div><b>2 · Run with the smallest that passes</b>An agent in production: a mid-tier or open model, chosen by your own scenarios, not by a leaderboard.</div>
<div><b>3 · Keep the choice cheap to change</b>The model is a setting behind one interface, so swapping is a config change and a re-test, not a rewrite.</div></div>
<h2>A pick for each kind of work</h2>
<p>Read down for the job you have. The examples are what we saw on offer in November 2026 and will date.</p>
<div class="tw"><table class="t"><tr><th>Job</th><th>What it needs</th><th>Class of model</th><th>Examples on offer now</th><th>Verdict</th></tr>{jobs}</table></div>
<h2>How to choose, in five steps</h2>
<ul><li><b>1 · Collect real cases.</b> Twenty to fifty tasks from your own work, with answers you know. Include the ones that go wrong: unknown inputs, a tool that fails, a user who pushes for something the agent must refuse.</li>
<li><b>2 · Write checks that need no model.</b> Is the number equal to the tool's number? Is the JSON valid? Did it refuse? Use a judge model only for what code cannot check.</li>
<li><b>3 · Run two or three candidates.</b> One small, one mid, one frontier. Same cases, same tools, same instructions.</li>
<li><b>4 · Compare on cost per successful task.</b> A cheap model that fails and retries can cost more than a dear one that succeeds once.</li>
<li><b>5 · Pick the smallest that passes, write down why, and re-run on every new release.</b> Models change under the same name, and a new version can be better or worse for your task.</li></ul>
<h2>What to measure</h2>
<div class="tw"><table class="t" style="min-width:0"><tr><th>Measure</th><th>The question</th></tr>{meas}</table></div>
<div class="box"><b>One real example.</b> A drug-safety agent we built has a rule that every number in a draft must equal a tool result. We test candidate models on twenty drug and event pairs and count how many drafts break that rule. That one deterministic check told us more than any published score, and it works for any model you try.</div>
<h2>Where the model runs matters as much as which model</h2>
<ul><li><b>On your data platform.</b> Databricks, Azure, AWS and Google Cloud each offer models next to your data. Offered models differ by region and change; the free tier of a platform offers fewer.</li>
<li><b>Through the vendor's own API.</b> Often the newest features arrive here first. Check the data terms for your use.</li>
<li><b>Hosted by you.</b> Open-weight models give control and cost you operations.</li>
<li><b>Through a gateway.</b> One door for keys, limits and logs. See <a href="/learn/ai-gateways/">AI gateways: which one to use</a>.</li></ul>
<h2>Check before you rely on this</h2>
<ul><li><b>Names and tiers change.</b> Vendors rename and replace models often. Read the current model list in your own workspace or console.</li>
<li><b>Reports disagree.</b> Public comparisons conflict on which model leads, and many are written by sellers. Treat them as a way to pick candidates, never to pick the winner.</li>
<li><b>Platform availability.</b> Which models your data platform offers, in your region, on your plan, must be checked there. On one free workspace we could use gpt-oss-120b and Llama 3.3 70B; paid workspaces list more.</li>
<li><b>Sources used for the examples</b> (secondary reports; confirm with the vendor): <a href="https://www.tembo.io/blog/best-llm-for-agentic-coding">Best LLM for agentic coding</a>, <a href="https://mastra.ai/articles/best-llm-for-coding">Best LLM for coding</a>, <a href="https://docs.databricks.com/aws/en/machine-learning/foundation-models/supported-models">Databricks supported models</a>.</li></ul>
<h2>Where to go next</h2>
<ul><li><a href="/learn/agent-frameworks/">When to use an agent SDK or framework</a>.</li>
<li><a href="/learn/agent-harness-stack-map/">Agent harness architecture map</a>.</li>
<li><a href="/learn/ai-gateways/">AI gateways: which one to use</a>.</li>
<li><a href="/learn/eval-harness/">Eval Harness</a>: how to test, in depth.</li></ul>"""
    desc = ("Which AI model for which job: a pick for building, running agents, bulk work, judging, long documents, private data and free projects, "
            "with a five-step way to test candidates on your own cases.")
    return wb.page("Which AI model for which job", desc, URL, body,
                   ds.CSS + CSS + ds.ld("Which AI model for which job", desc, URL, [("Agent Harness", "/learn/agent-harness/"), ("Which model", "/learn/which-model/")]))


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page())
    print("which model ->", OUT)


if __name__ == "__main__":
    main()
