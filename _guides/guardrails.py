"""The guardrail catalog: every common guardrail for autonomous agents, on one filterable page.

    python3 _guides/guardrails.py             # preview: _writing/preview/agent-guardrails/ (git-ignored)
    python3 _guides/guardrails.py --publish   # writes learn/agent-guardrails/

Data lives in _guides/guardrail_data.py; add a row there and rebuild.
"""
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "_guides"))
spec = importlib.util.spec_from_file_location("writing_build", ROOT / "_writing" / "build.py")
wb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wb)
from guardrail_data import CONCERNS, G, HOW, PRIORITY, WHERE  # noqa: E402

E = wb.E
URL = f"{wb.SITE}/learn/agent-guardrails/"
AAC = "https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/{}.yaml"

CSS = """<style>
  .crumbs { font-size:13.5px; color:var(--faint); margin:28px 0 0; } .crumbs a { color:var(--muted); }
  .lede { font-size:20px; color:var(--ink-soft); }
  .legend { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:10px; margin:14px 0 22px; font-family:var(--sans); font-size:14px; }
  .legend div { border:var(--line); border-radius:var(--wob); padding:10px 14px; background:#fff; }
  .legend b { display:block; font-size:15px; }
  .pill { display:inline-block; font:12.5px var(--sans); border:1.2px solid var(--ink); border-radius:20px; padding:0 9px; margin:2px 4px 2px 0; white-space:nowrap; }
  .p-must { background:var(--rose-wash); font-weight:700; } .p-should { background:var(--butter-wash); } .p-could { background:#fff; }
  .h-rule { background:var(--peri-wash); } .h-classifier { background:var(--mint-wash); } .h-judge { background:var(--lilac-wash); } .h-person, .h-platform { background:var(--sky-wash); }
  section.stage h2 { margin-top:34px; }
  .tw { overflow-x:auto; } table.g { border-collapse:collapse; width:100%; font-family:var(--sans); font-size:14px; }
  table.g th, table.g td { text-align:left; padding:8px 9px; border-bottom:1.5px dashed var(--rule-firm); vertical-align:top; }
  table.g th { font-size:11.5px; letter-spacing:.08em; text-transform:uppercase; color:var(--faint); }
  table.g td.n { min-width:170px; } table.g td.n b { display:block; font-size:15px; }
  table.g td.tools { color:var(--muted); font-size:13px; min-width:150px; } table.g td:last-child { white-space:nowrap; }
  .count { font-family:var(--sans); font-size:14px; color:var(--muted); margin:6px 0 0; }
</style>"""


def chips(name, opts):
    return (f'<div class="chips" data-f="{name}"><button class="on" data-v="">All</button>'
            + "".join(f'<button data-v="{k}">{E(v)}</button>' for k, v in opts.items()) + "</div>")


def row(r):
    name, catches, where, pri, how, fail, concern, aac, tools = r
    return (f'<tr data-priority="{pri}" data-how="{how}" data-concern="{concern}">'
            f'<td class="n"><b>{E(name)}</b><span class="pill p-{pri}">{PRIORITY[pri]}</span><span class="pill h-{how}">{HOW[how][0]}</span></td>'
            f'<td>{E(catches)}</td><td>{E(fail)}</td><td>{CONCERNS[concern]}</td>'
            f'<td class="tools">{E(tools)}</td><td><a href="{AAC.format(aac)}">{aac}</a></td></tr>')


def page():
    n = Counter(r[4] for r in G)
    pri = Counter(r[3] for r in G)
    stages = ""
    for k, label in WHERE.items():
        rows = "".join(row(r) for r in G if r[2] == k)
        stages += (f'<section class="stage" id="{k}"><h2>{E(label)}</h2><div class="tw"><table class="g">'
                   f'<tr><th>Guardrail</th><th>What it catches</th><th>If it fires</th><th>Concern</th><th>Tools that do it</th><th>Proven by</th></tr>'
                   f'{rows}</table></div></section>')
    legend = "".join(f'<div><b><span class="pill h-{k}">{v[0]}</span></b>{E(v[1])}<br><span style="color:var(--muted)">{E(v[2])} · {n[k]} in this list</span></div>'
                     for k, v in HOW.items())
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › Agent guardrails</p>
<p class="eyebrow" style="margin-top:22px">AI engineering · free reference · grows over time</p>
<h1>The agent guardrail catalog</h1>
<p class="lede">{len(G)} common guardrails for autonomous agents, sorted by where they sit in a turn. Each one is marked must, should or could have; says whether a rule, a small classifier, an LLM judge, a person or the platform decides; and links to the test that proves it works.</p>
{wb.drawing_guard_where()}
<p><b>{pri['must']} must-haves, {pri['should']} should-haves, {pri['could']} could-haves.</b> {n['rule']} of the {len(G)} are plain rules in code. Only {n['judge']} need an LLM judge. The short version, with pictures, is the post <a href="/writing/guardrails-sorted/">Every guardrail your agent needs, sorted</a>.</p>
<h2>How a guardrail decides</h2>
<div class="legend">{legend}</div>
<p><b>Must</b> means every agent that can change something in the real world. <b>Should</b> means most agents. <b>Could</b> depends on the use. "Proven by" links to the matching obligation in the <a href="https://github.com/dataagentsai/ai-assurance-catalog">AI Assurance Catalog</a>: the test that shows the guardrail really works.</p>
<h2>Filter</h2>
{chips("priority", PRIORITY)}{chips("how", {k: v[0] for k, v in HOW.items()})}{chips("concern", CONCERNS)}
<p class="count" id="count"></p>
{stages}
<h2>Add one</h2>
<p>Missing a guardrail you rely on? Email <a href="mailto:basant@cleandataengineering.ai">basant@cleandataengineering.ai</a> with what it catches and where it sits. Tool names are examples, not endorsements; check current docs before you build.</p>
<script>
(function(){{var f={{}};function run(){{var c=0;document.querySelectorAll('table.g tr[data-how]').forEach(function(tr){{
var ok=Object.keys(f).every(function(k){{return!f[k]||tr.dataset[k]===f[k]}});tr.style.display=ok?'':'none';if(ok)c++}});
document.querySelectorAll('section.stage').forEach(function(s){{s.style.display=s.querySelector('tr[data-how]:not([style*="none"])')?'':'none'}});
document.getElementById('count').textContent=c+' of {len(G)} guardrails shown'}}
document.querySelectorAll('.chips').forEach(function(c){{c.addEventListener('click',function(e){{var b=e.target.closest('button');if(!b)return;
c.querySelectorAll('button').forEach(function(x){{x.classList.toggle('on',x===b)}});f[c.dataset.f]=b.dataset.v;run()}})}});run()}})();
</script>"""
    ld = {"@context": "https://schema.org", "@type": "TechArticle", "headline": "The agent guardrail catalog",
          "description": f"{len(G)} common guardrails for autonomous agents: must or should have, rule, classifier or LLM judge, where each sits, and the test that proves it.",
          "url": URL, "inLanguage": "en", "isAccessibleForFree": True, "dateModified": "2026-10-31",
          "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{wb.SITE}/#about"},
          "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": wb.SITE}}
    head = CSS + wb.kit_css() + f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
    return wb.page("The agent guardrail catalog", ld["description"], URL, body, head)


def main():
    out = ROOT / ("learn" if "--publish" in sys.argv else "_writing/preview") / "agent-guardrails"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("guardrail catalog ->", out)


if __name__ == "__main__":
    main()
