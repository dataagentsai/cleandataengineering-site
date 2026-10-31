"""CCA-F mind maps: every decision table from the mock exams, on one page.

    python3 _certifications/mindmaps_extract.py   # only when the mocks change
    (merge raw/ into merged/d1..d5.json, see mindmaps/MERGE-BRIEF.md)
    python3 _certifications/mindmaps.py

Writes /certifications/cca-f-mind-maps/. Each question in Mocks 4 to 7 has a "Think it through"
mind map; similar maps were merged per exam objective, and this page lists them by what each map
is for. It lives outside certifications/claude-certified-architect/ because sync.py replaces
that folder on every run.

Refuses to build if any of the source maps is missing from the merge or counted twice.
"""
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent / "mindmaps"
spec = importlib.util.spec_from_file_location("writing_build", ROOT / "_writing" / "build.py")
wb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wb)
E = wb.E
URL = f"{wb.SITE}/certifications/cca-f-mind-maps/"
MOCK = "/certifications/claude-certified-architect/CCA-F/Foundations-Mock-Exam-{n}/"

DOMAINS = {
    1: "Agentic architecture and orchestration",
    2: "Tool design and MCP integration",
    3: "Claude Code configuration and workflows",
    4: "Prompt engineering and structured output",
    5: "Context management and reliability",
}
OBJECTIVES = {
    "1.1": "Agentic loops", "1.2": "Coordinator and subagents", "1.3": "Subagent invocation and context passing",
    "1.4": "Multi-step workflows, enforcement and hand-off", "1.5": "Agent SDK hooks", "1.6": "Task decomposition",
    "1.7": "Session state, resuming and forking",
    "2.1": "Tool descriptions and boundaries", "2.2": "Structured tool errors", "2.3": "Tool distribution and tool_choice",
    "2.4": "MCP servers in Claude Code and agents", "2.5": "Built-in tools (Read, Write, Edit, Bash, Grep, Glob)",
    "3.1": "CLAUDE.md hierarchy and scope", "3.2": "Slash commands and skills", "3.3": "Path-specific rules",
    "3.4": "Plan mode or direct execution", "3.5": "Iterative refinement", "3.6": "Claude Code in CI/CD",
    "4.1": "Explicit criteria and false positives", "4.2": "Few-shot examples", "4.3": "Structured output and JSON schemas",
    "4.4": "Validation, retry and feedback", "4.5": "Batch processing", "4.6": "Multi-pass review",
    "5.1": "Keeping key facts in long interactions", "5.2": "Escalation and ambiguity", "5.3": "Errors across agents",
    "5.4": "Context in large codebases", "5.5": "Human review and confidence", "5.6": "Sources, provenance and uncertainty",
}
ALLOWED = re.compile(r"<(?!/?(?:b|i|code)>)[^>]*>")


def cell(s):
    """Source cells are our own HTML: keep <b>, <i> and <code>, drop any other tag."""
    return ALLOWED.sub("", s)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def ref_link(r):
    n, q = r.split(":")
    n = n[1:]
    m = re.search(r"s(\d+)-(\d+)$", q)
    label = f"Mock {n}, scenario {int(m.group(1))} question {int(m.group(2))}" if m else f"Mock {n}, {q}"
    return f'<a href="{MOCK.format(n=n)}">{E(label)}</a>'


def load():
    raw = {m["ref"] for f in (HERE / "raw").glob("*.json") for m in json.loads(f.read_text())}
    domains = [json.loads((HERE / "merged" / f"d{d}.json").read_text()) for d in DOMAINS]
    seen = [x for d in domains for o in d["objectives"] for m in o["maps"] for x in m["from"]]
    missing, extra, dupes = raw - set(seen), set(seen) - raw, len(seen) - len(set(seen))
    if missing or extra or dupes:
        raise SystemExit(f"merge does not cover the source maps: missing {sorted(missing)}, extra {sorted(extra)}, twice {dupes}")
    n = 0
    for d in domains:
        for o in d["objectives"]:
            for m in o["maps"]:
                n += 1
                m["n"] = n
                m["id"] = f"m{o['obj'].replace('.', '-')}-{slug(m['for'])}"
                assert len(m["head"]) == 3 and all(len(r) == 3 for r in m["rows"]), m["for"]
    return domains, len(raw)


CSS = """<style>
  .crumbs { font-family:var(--sans); font-size:13.5px; color:var(--faint); margin:18px 0 0; }
  .crumbs a { color:var(--muted); }
  .how { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:12px; margin:18px 0 8px; font-family:var(--sans); font-size:15px; }
  .how div { border:1.5px solid var(--ink); border-radius:var(--wob); padding:10px 14px; background:var(--peri-wash); }
  .how div:nth-child(2) { background:var(--butter-wash); } .how div:nth-child(3) { background:var(--rose-wash); }
  .how b { display:block; font-family:var(--hand); font-size:19px; font-weight:400; }
  .find { width:100%; box-sizing:border-box; font:16px var(--sans); border:1.5px solid var(--ink); border-radius:999px; padding:9px 16px; margin:18px 0 6px; background:#fff; }
  .found { font-family:var(--sans); font-size:13.5px; color:var(--faint); margin:0 0 10px; min-height:1.2em; }
  .tw { overflow-x:auto; } table.idx, table.mm { border-collapse:collapse; width:100%; font-family:var(--sans); font-size:14.5px; }
  table.idx td, table.idx th, table.mm td, table.mm th { text-align:left; vertical-align:top; padding:7px 10px; border-bottom:1px solid var(--rule); }
  table.idx th, table.mm th { font-size:11.5px; letter-spacing:.08em; text-transform:uppercase; color:var(--faint); }
  table.idx .grp td { background:var(--surface-2, #F6F4EF); font-weight:700; font-size:13px; letter-spacing:.04em; }
  table.idx td.n { font-weight:700; color:var(--ink); white-space:nowrap; width:2.5em; }
  .mm-card h4 .num { display:inline-block; min-width:1.7em; margin-right:8px; padding:0 7px; border:1.5px solid var(--ink); border-radius:999px; background:var(--butter-wash); text-align:center; font-family:var(--sans); font-size:16px; font-weight:700; vertical-align:3px; }
  table.idx td.o { color:var(--faint); white-space:nowrap; font-size:13px; }
  table.idx a { color:var(--ink); }
  h2.dom { margin-top:46px; } h3.obj { margin:30px 0 4px; font-family:var(--hand); font-weight:400; font-size:24px; }
  h3.obj span { font-family:var(--sans); font-size:13px; color:var(--faint); margin-right:8px; }
  .mm-card { border:1.5px solid var(--ink); border-radius:var(--wob); padding:14px 18px 10px; margin:14px 0 20px; background:#fff; scroll-margin-top:16px; }
  .mm-card:target { background:var(--butter-wash); }
  .mm-card .for { font-family:var(--sans); font-size:11.5px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; color:var(--faint); margin:0; }
  .mm-card h4 { font-family:var(--hand); font-weight:400; font-size:23px; margin:0 0 6px; line-height:1.25; }
  .mm-card .ask { font-family:var(--sans); font-size:15.5px; margin:0 0 4px; }
  .mm-card .when { font-family:var(--sans); font-size:14.5px; color:var(--ink-soft); margin:0 0 10px; }
  table.mm th { background:var(--peri-wash); color:var(--ink); }
  table.mm td:first-child { width:38%; } table.mm code, table.idx code { font-family:var(--mono); font-size:.86em; background:var(--surface-2, #F6F4EF); padding:0 4px; border-radius:3px; }
  .rule { font-family:var(--sans); font-size:15px; background:var(--rose-wash); border:1.5px solid var(--ink); border-radius:12px; padding:8px 14px; margin:12px 0 8px; }
  .src { font-family:var(--sans); font-size:12.5px; color:var(--faint); margin:0 0 4px; }
  .src a { color:var(--muted); }
  .top { font-family:var(--sans); font-size:13px; } .hide { display:none; }
  @media print { .find, .found, header, footer, .top { display:none; } .mm-card { break-inside:avoid; } }
</style>"""

JS = """<script>
(function(){
  var box = document.getElementById('find'), out = document.getElementById('found');
  var cards = [].slice.call(document.querySelectorAll('.mm-card')), rows = [].slice.call(document.querySelectorAll('table.idx tr[data-for]'));
  box.addEventListener('input', function(){
    var q = box.value.trim().toLowerCase(), n = 0;
    cards.forEach(function(c){ var hit = !q || c.textContent.toLowerCase().indexOf(q) >= 0; c.classList.toggle('hide', !hit); if (hit) n++; });
    rows.forEach(function(r){ var c = document.getElementById(r.dataset.for); r.classList.toggle('hide', c.classList.contains('hide')); });
    document.querySelectorAll('h3.obj, h2.dom').forEach(function(h){
      var sec = h.parentElement, any = sec.querySelector('.mm-card:not(.hide)'); h.classList.toggle('hide', !!q && !any); });
    out.textContent = q ? n + ' mind map' + (n === 1 ? '' : 's') + ' mention "' + box.value.trim() + '"' : '';
  });
})();
</script>"""


def page():
    domains, total = load()
    nmaps = sum(len(o["maps"]) for d in domains for o in d["objectives"])

    idx = ['<div class="tw"><table class="idx"><tr><th>No.</th><th>Mind map for</th><th>Ask yourself</th><th>Objective</th></tr>']
    for d in domains:
        idx.append(f'<tr class="grp"><td colspan="4">Domain {d["domain"]}: {E(DOMAINS[d["domain"]])}</td></tr>')
        for o in d["objectives"]:
            for m in o["maps"]:
                idx.append(f'<tr data-for="{m["id"]}"><td class="n">{m["n"]}</td><td><a href="#{m["id"]}">{E(m["for"])}</a></td><td>{cell(m["ask"])}</td>'
                           f'<td class="o">{o["obj"]} {E(OBJECTIVES[o["obj"]])}</td></tr>')
    idx.append("</table></div>")

    secs = []
    for d in domains:
        objs = []
        for o in d["objectives"]:
            cards = []
            for m in o["maps"]:
                head = "".join(f"<th>{E(h)}</th>" for h in m["head"])
                rows = "".join("<tr>" + "".join(f"<td>{cell(c)}</td>" for c in r) + "</tr>" for r in m["rows"])
                src = "; ".join(ref_link(r) for r in sorted(m["from"], key=lambda r: (-int(r.split(':')[0][1:]), r)))
                cards.append(f'''<article class="mm-card" id="{m["id"]}"><p class="for">Mind map {m["n"]} of {nmaps} · for</p><h4><span class="num">{m["n"]}</span>{E(m["for"])}</h4>
<p class="ask"><b>Ask yourself:</b> {cell(m["ask"])}</p><p class="when"><b>Reach for it when:</b> {cell(m["when"])}</p>
<div class="tw"><table class="mm"><tr>{head}</tr>{rows}</table></div>
<p class="rule"><b>Rule to remember:</b> {cell(m["rule"])}</p>
<p class="src">Merged from {len(m["from"])} question{"s" if len(m["from"]) != 1 else ""}: {src}</p></article>''')
            objs.append(f'<div><h3 class="obj" id="o{o["obj"].replace(".", "-")}"><span>{o["obj"]}</span>{E(OBJECTIVES[o["obj"]])}</h3>{"".join(cards)}</div>')
        secs.append(f'<section id="d{d["domain"]}"><h2 class="dom">Domain {d["domain"]}: {E(DOMAINS[d["domain"]])}</h2>{"".join(objs)}'
                    f'<p class="top"><a href="#index">Back to the list</a></p></section>')

    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/certifications/">Certifications</a> › <a href="/certifications/claude-certified-architect/CCA-F/">CCA-F</a> › Mind maps</p>
<p class="eyebrow" style="margin-top:22px">Claude Certified Architect, Foundations · revision sheet</p>
<h1>CCA-F mind maps: every decision table in one place</h1>
<p class="lede">Every question in mock exams 4 to 7 ends with a mind map: a small table that says <b>what you see</b>, <b>what is really wrong</b>, and <b>which fix fits</b>. Many questions shared the same kind of decision, so their tables have been merged. That turns {total} tables into {nmaps} mind maps, each named by the decision it helps you make.</p>
<div class="how"><div><b>1. Find the decision</b>Read the "Mind map for" column below and pick the one that matches the question in front of you.</div>
<div><b>2. Match the symptom</b>In the table, find the row that describes what the question tells you. The fix in that row is usually the answer.</div>
<div><b>3. Check the neighbour row</b>The row next to it is often the runner-up option. Find the sentence in the question that rules it out.</div></div>

<h2 id="index">Which mind map is for what</h2>
<input class="find" id="find" type="search" placeholder="Search the mind maps, for example: hook, escalate, batch, CLAUDE.md" aria-label="Search the mind maps">
<p class="found" id="found"></p>
{"".join(idx)}
{"".join(secs)}
<section id="next"><p class="eyebrow">Next</p><h2>Practise with them</h2>
<p>Try a mind map on a fresh question: <a href="/certifications/claude-certified-architect/CCA-F/Foundations-Mock-Exam-7/plain/">Mock 7, plain style</a> is the best place to start, and <a href="/certifications/claude-certified-architect/CCA-F/Foundations-Mock-Exam-6/">Mock 6</a> is the stretch. Each trap on its own: <a href="/certifications/claude-certified-architect/CCA-F/Trap-Gym/">the trap gym</a>.</p></section>"""
    ld = {"@context": "https://schema.org", "@type": "LearningResource", "name": "CCA-F mind maps",
          "description": f"{nmaps} decision tables for the Claude Certified Architect Foundations exam, merged from {total} mock-exam explanations and listed by what each one decides.",
          "url": URL, "inLanguage": "en", "isAccessibleForFree": True, "dateModified": "2026-10-31",
          "educationalUse": "revision", "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{wb.SITE}/#about"}}
    head = CSS + f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
    desc = f"Every mind map from the CCA-F mock exams on one page: {nmaps} decision tables, merged from {total} questions and listed by what each one is for."
    return wb.page("CCA-F mind maps: every decision table in one place", desc, URL, body + JS, head)


def main():
    out = ROOT / "certifications" / "cca-f-mind-maps"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("CCA-F mind maps ->", out)


if __name__ == "__main__":
    main()
