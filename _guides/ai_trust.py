"""Running AI you can trust: governance, safety, security and reliability, in one page.

    python3 _guides/ai_trust.py             # preview: _writing/preview/ai-governance/ (git-ignored)
    python3 _guides/ai_trust.py --publish   # writes learn/ai-governance/

Content lives in _guides/ai_trust_data.py and ai_trust_auto.py; edit a row there and rebuild.
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "_guides"))
sys.path.insert(0, str(ROOT / "_paths"))
spec = importlib.util.spec_from_file_location("writing_build", ROOT / "_writing" / "build.py")
wb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wb)
from ai_trust_auto import AUTO, BIGCO, HONEST, LEVELS, PRODUCTS  # noqa: E402
from ai_trust_data import C, GROUPS, KINDS, ORDER, WORDS  # noqa: E402
from ai_trust_frameworks import CASE, CASE_INTRO, CROSSWALK, LEARN, READING  # noqa: E402
from diagrams import box, svg, text  # noqa: E402

E = wb.E
URL = f"{wb.SITE}/learn/ai-governance/"
BY_N = {c["n"]: c for c in C}
GNAME = {g[0]: g for g in GROUPS}

CSS = """<style>
  .crumbs { font-size:13.5px; color:var(--faint); margin:28px 0 0; } .crumbs a { color:var(--muted); }
  .lede { font-size:20px; color:var(--ink-soft); }
  .tw { overflow-x:auto; } table.g { border-collapse:collapse; width:100%; font-family:var(--sans); font-size:14.5px; }
  table.g th, table.g td { text-align:left; padding:8px 9px; border-bottom:1.5px dashed var(--rule-firm); vertical-align:top; }
  table.g th { font-size:11.5px; letter-spacing:.08em; text-transform:uppercase; color:var(--faint); }
  .diagram { margin:18px 0; border:var(--line); border-radius:var(--wob); padding:14px 16px; background:#fff; overflow-x:auto; }
  .diagram svg { width:100%; min-width:680px; height:auto; display:block; } .diagram text { font-family:var(--hand); }
  .jump { display:flex; flex-wrap:wrap; gap:8px; margin:12px 0 4px; font-family:var(--sans); font-size:14px; }
  .jump a { border:1.5px solid var(--ink); border-radius:999px; padding:2px 12px; background:#fff; color:var(--ink); text-decoration:none; }
  .grp { border:var(--line); border-radius:var(--wob); padding:10px 18px; margin:36px 0 10px; background:var(--w, #fff); }
  .grp h2 { margin:0; } .grp p { margin:2px 0 0; color:var(--ink-soft); }
  .cap { border:var(--line); border-radius:var(--wob); padding:16px 20px; margin:14px 0; background:#fff; }
  .cap h3 { font-size:26px; margin:0 0 2px; } .cap .num { font-family:var(--hand); }
  .cap .q { font-size:17px; color:var(--ink-soft); margin:0 0 8px; font-style:italic; }
  .cap dl { margin:10px 0 0; display:grid; grid-template-columns:130px 1fr; gap:8px 14px; font-family:var(--sans); font-size:14.5px; }
  .cap dt { color:var(--faint); font-weight:700; font-size:12px; letter-spacing:.06em; text-transform:uppercase; padding-top:3px; }
  .cap dd { margin:0; } .cap ul { margin:0; padding-left:18px; } .cap li { margin:2px 0; }
  .cap .tl b { font-weight:700; }
  .pill { display:inline-block; font:12.5px var(--sans); border:1.2px solid var(--ink); border-radius:20px; padding:0 9px; white-space:nowrap; }
  .a-Fully { background:var(--mint-wash); } .a-Mostly { background:var(--sky-wash); } .a-Assisted { background:var(--butter-wash); } .a-Human { background:var(--rose-wash); }
  .box { border:var(--line); border-radius:var(--wob); padding:12px 18px; margin:14px 0; background:var(--butter-wash); }
  .box p { margin:6px 0; }
  @media (max-width:640px) { .cap dl { grid-template-columns:1fr; gap:2px; } .cap dt { padding-top:8px; } }
</style>"""


def ul(items):
    return "<ul>" + "".join(f"<li>{E(i)}</li>" for i in items) + "</ul>"


def links(ls):
    if not ls:
        return ""
    return '<dt>Go deeper</dt><dd>' + " · ".join(f'<a href="{h}">{E(t)}</a>' for t, h in ls) + "</dd>"


def card(c):
    t = c["tools"]
    lvl, auto, human = AUTO[c["n"]]
    return f"""<article class="cap" id="c{c['n']}">
<h3><span class="num">{c['n']}.</span> {E(c['name'])}</h3>
<p class="q">{E(c['q'])}</p>
<p>{E(c['plain'])}</p>
<dl>
<dt>Decide</dt><dd>{ul(c['design'])}</dd>
<dt>Build</dt><dd>{ul(c['build'])}</dd>
<dt>Standards and tools</dt><dd class="tl"><p><b>Open standards.</b> {E(t['standards'])}</p><p><b>Open source.</b> {E(t['open'])}</p><p><b>Cloud.</b> {E(t['cloud'])}</p></dd>
<dt>Make it better</dt><dd>{E(c['edge'])}</dd>
<dt>Prove it works</dt><dd>{E(c['proof'])}</dd>
<dt>Automation</dt><dd><span class="pill a-{lvl}">{lvl}</span> {E(auto)} <i>Stays with people:</i> {E(human)}</dd>
{links(c['links'])}
</dl></article>"""


def overview():
    """Six groups as boxes, each listing its capability numbers."""
    fills = {"peri": "peri", "butter": "butter", "mint": "mint", "rose": "rose", "lilac": "lilac", "sky": "sky"}
    b = ""
    w, gap, x = 150, 20, 10
    for gid, name, _, fill in GROUPS:
        ns = [c["n"] for c in C if c["g"] == gid]
        b += box(x, 20, w, 92, name, "", fills[fill])
        b += text(x + w / 2, 128, "capabilities " + ", ".join(str(n) for n in sorted(ns)), 14)
        x += w + gap
    b += text(530, 168, "Read left to right for a new program. Read any one box alone when you need that part.", 15)
    return svg(1050, 185, b, "Six groups: know what you have, decide the rules, prove it before launch, run it safely, be open and capable, and across everything.")


def groups_html():
    out = ""
    for gid, name, blurb, fill in GROUPS:
        cards = "".join(card(c) for c in sorted((c for c in C if c["g"] == gid), key=lambda c: c["n"]))
        out += f'<section id="{gid}"><div class="grp" style="--w:var(--{fill}-wash)"><h2>{E(name)}</h2><p>{E(blurb)}</p></div>{cards}</section>'
    return out


def words_html():
    rows = "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td>{E(c)}</td></tr>" for a, b, c in WORDS)
    return f'<div class="tw"><table class="g"><tr><th>Term</th><th>The question it answers</th><th>Where it lives below</th></tr>{rows}</table></div>'


def kinds_html():
    rows = "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td>{E(c)}</td></tr>" for a, b, c in KINDS)
    return f'<div class="tw"><table class="g"><tr><th>Kind of AI use</th><th>What it looks like</th><th>What makes it hard</th></tr>{rows}</table></div>'


def auto_html():
    leg = "".join(f'<p><span class="pill a-{k}">{k}</span> {E(v)}</p>' for k, v in LEVELS.items())
    rows = "".join(
        f'<tr><td><b>{n}. {E(BY_N[n]["name"])}</b></td><td><span class="pill a-{AUTO[n][0]}">{AUTO[n][0]}</span></td><td>{E(AUTO[n][1])}</td><td>{E(AUTO[n][2])}</td></tr>'
        for n in sorted(AUTO))
    return (f'<div class="box">{leg}</div><div class="tw"><table class="g"><tr><th>Capability</th><th>Automation</th><th>What a machine does</th><th>What stays with people</th></tr>{rows}</table></div>')


def bigco_html():
    rows = "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td>{E(c)}</td></tr>" for a, b, c in BIGCO)
    prod = "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td></tr>" for a, b in PRODUCTS)
    honest = "".join(f"<li>{E(h)}</li>" for h in HONEST)
    return (f'<div class="tw"><table class="g"><tr><th>Organization</th><th>What it publicly states or sells</th><th>Evidence</th></tr>{rows}</table></div>'
            f'<h3>What this does and does not tell you</h3><ul>{honest}</ul>'
            f'<h3>Tools that sell the automation</h3><div class="tw"><table class="g"><tr><th>Kind</th><th>Examples and what to check</th></tr>{prod}</table></div>')


def order_html():
    rows = ""
    for name, when, theme, ns, note in ORDER:
        caps = ", ".join('<a href="#c%d">%d. %s</a>' % (n, n, E(BY_N[n]["name"])) for n in ns)
        rows += (f"<tr><td><b>{name}</b><br>{E(when)}</td><td><b>{E(theme)}</b></td>"
                 f"<td>{caps}</td><td>{E(note)}</td></tr>")
    return f'<div class="tw"><table class="g"><tr><th>Stage</th><th>Theme</th><th>Capabilities</th><th>What exists at the end</th></tr>{rows}</table></div>'


def frameworks_html():
    learn = "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td>{E(c)}</td><td>{E(d)}</td><td>{E(v)}</td></tr>" for a, b, c, d, v in LEARN)
    cross = ""
    for ob, ns, nist, eu, iso in CROSSWALK:
        caps = ", ".join('<a href="#c%d">%d</a>' % (n, n) for n in ns)
        cross += f"<tr><td><b>{E(ob)}</b></td><td>{caps}</td><td>{E(nist)}</td><td>{E(eu)}</td><td>{E(iso)}</td></tr>"
    case = "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td>{E(c)}</td><td>{E(d)}</td><td>{E(e)}</td></tr>" for a, b, c, d, e in CASE)
    read = "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td>{E(c)}</td><td>{E(d)}</td><td>" + " · ".join(f'<a href="{u}">{E(t)}</a>' for t, u in ls) + "</td></tr>" for a, b, c, d, ls in READING)
    return f"""<section id="frameworks"><h2>Do you need to learn NIST, ISO/IEC 42001 and the EU AI Act?</h2>
<p>Yes, but not to the same depth. The three do different jobs. The EU AI Act is a law, so it says what you must have. NIST AI RMF is a free framework, so it gives you a way to organize the work. ISO/IEC 42001 is an auditable standard, so it lets you prove to others that you do the work. Learn the law in depth, NIST as your working vocabulary, and ISO/IEC 42001 at overview level.</p>
<div class="tw"><table class="g"><tr><th>Framework</th><th>What it is</th><th>What it is for</th><th>How deep to go</th><th>Verdict</th></tr>{learn}</table></div>
<h3>One job, three vocabularies</h3>
<p>The three mostly ask for the same things in different words. Once you see that, you stop memorizing three lists. The table lists fifteen things a trustworthy AI program needs. The second column links to the capability on this page that covers it. The other three columns say where each framework asks for it.</p>
<div class="tw"><table class="g"><tr><th>What you need</th><th>Capability</th><th>NIST AI RMF</th><th>EU AI Act</th><th>ISO/IEC 42001</th></tr>{cross}</table></div>
<p>Two notes on reading it. First, the EU AI Act puts most duties on <i>providers</i> (who build or sell the system) and some on <i>deployers</i> (who use it), so check which you are. Second, where a column names a broad area (a whole clause or Annex A group) the framework asks in general words; where it names an article, the ask is specific.</p>
<h3>Worked example: a CV-ranking assistant</h3>
<p>{E(CASE_INTRO)}</p>
<div class="tw"><table class="g"><tr><th>Step</th><th>What the team does</th><th>NIST AI RMF</th><th>EU AI Act</th><th>ISO/IEC 42001</th></tr>{case}</table></div>
<p>Notice that the team does one piece of work at each step, and all three frameworks are satisfied by it. That is the point of the crosswalk.</p>
<h3>What to read, and in what order</h3>
<div class="tw"><table class="g"><tr><th>Read</th><th>Cost</th><th>Time</th><th>Note</th><th>Links</th></tr>{read}</table></div>
<p>Read NIST first, then the EU risk tiers, then come back to the crosswalk above. The article and clause numbers here follow the official texts as we understand them; check each one against the source before you quote it in a compliance document.</p></section>"""


def page():
    jump = '<a href="#frameworks">NIST, ISO 42001, EU AI Act</a>' + "".join(f'<a href="#{g[0]}">{E(g[1])}</a>' for g in GROUPS) + '<a href="#automate">What can be automated</a><a href="#order">Order to build</a>'
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › Running AI you can trust</p>
<p class="eyebrow" style="margin-top:22px">AI governance · safety · security · reliability · free guide · grows over time</p>
<h1>Running AI you can trust</h1>
<p class="lede">Eighteen things an organization needs so that its AI is governed, safe, secure and reliable. Each one starts with the question a leadership team asks, goes down to what to build, names the open standards and tools, and ends with how you would know it works.</p>
<div class="box"><p><b>Who this is for.</b> Anyone who has to answer for AI across a whole organization, not for one system: many users, many tools, several clouds, many functions. It covers bought-in tools, staff using public assistants, classical models, language-model apps and agents.</p>
<p><b>How each capability is laid out.</b> The question, a plain explanation, what to decide, what to build, open standards and tools (open source and cloud), a way to make it better than the usual, how to prove it works, and how much of it can be automated.</p></div>
<div class="jump">{jump}</div>

<h2>Five words, one job</h2>
<p>People use these terms loosely. They are five angles on the same job: AI that you can rely on and defend.</p>
{words_html()}

{frameworks_html()}

<h2>Start with the full spread of AI use</h2>
<p>A program built only for the AI you built yourself misses most of the exposure. Six kinds of use need covering, and they need different tools.</p>
{kinds_html()}

<h2>The eighteen, in six groups</h2>
<figure class="diagram">{overview()}<figcaption>The groups follow the life of an AI use: you find it, set the rules, prove it, run it, tell people, and keep cost and platforms in order.</figcaption></figure>

{groups_html()}

<section id="automate"><h2>What can be automated</h2>
<p>A fair question is whether this can run itself, with automatic checks that tell you whether you meet ISO and other standards at any moment. Mostly yes for the technical controls, and no for the decisions. The table below says which is which, capability by capability.</p>
{auto_html()}
<h3>Checking standards automatically</h3>
<p>The pattern is the same one used for cloud security compliance. Write each requirement as a control. Make each control a test that runs on a schedule and emits a signed result. Store the results where nobody can alter them. Map each control to the clauses of every standard it satisfies. Then "are we aligned with ISO/IEC 42001?" becomes a query over current results, and an audit pack becomes a report. Open tools for this: Open Policy Agent for rules, OSCAL for the machine-readable control catalog, OpenTelemetry and OpenLineage for evidence, and the <a href="https://github.com/dataagentsai/ai-assurance-catalog">AI Assurance Catalog</a> for which tests are owed.</p>
</section>

<section id="bigco"><h2>What large organizations do</h2>
<p>The big platform companies publish a good deal about their approach. This summary uses only what they state publicly, and does not claim to know their internal systems.</p>
{bigco_html()}
</section>

<section id="order"><h2>The order to build in</h2>
<p>Do not build all eighteen at once. A small, honest version of the first group beats a polished version of the last.</p>
{order_html()}
</section>

<h2>Check before you rely on this</h2>
<p>Standards and laws change. ISO/IEC 42001 and 42005, the NIST AI Risk Management Framework and its generative AI profile, and the OWASP lists are current at the time of writing. The EU AI Act applies in phases, and its timetable has been under review, so confirm the dates that apply to you. Tool names are examples, not endorsements; check current documentation before you build. If you find something wrong or missing, tell us and we will correct it.</p>
<p>Related on this site: <a href="/learn/agent-guardrails/">the guardrail catalog</a> · <a href="/learn/agenttwin/">AgentTwin</a> · <a href="/learn/eval-harness/">Eval Harness</a> · <a href="/learn/agent-harness/">Agent Harness</a> · <a href="/learn/data-platform-suite/">the data platform suite</a> · <a href="/learn/hard-problems/">hard problems by layer</a>.</p>"""
    desc = "Eighteen capabilities for governing, securing and running AI across a whole organization: the leadership question, what to build, open standards and tools, how to make it better, how to prove it, and what can be automated."
    ld = {"@context": "https://schema.org", "@type": "TechArticle", "headline": "Running AI you can trust", "description": desc,
          "url": URL, "inLanguage": "en", "isAccessibleForFree": True, "dateModified": "2026-11-19",
          "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{wb.SITE}/#about"},
          "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": wb.SITE}}
    head = CSS + wb.kit_css() + f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
    return wb.page("Running AI you can trust", desc, URL, body, head)


def main():
    out = ROOT / ("learn" if "--publish" in sys.argv else "_writing/preview") / "ai-governance"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("ai governance guide ->", out)


if __name__ == "__main__":
    main()
