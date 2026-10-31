"""Hard problems: a master list at /problems/ and one page per problem at /problems/<slug>/.

    python3 _problems/build.py             # preview into _writing/preview/problems/ (git-ignored)
    python3 _problems/build.py --publish   # writes problems/

Data: _problems/data.json (79 problems in 10 groups; first extracted from the Founder-CTO Path by extract.py,
now the source of truth for the site). Diagrams: _problems/diagrams/*.py, each with DRAWINGS = {slug: fn};
a problem with no diagram yet gets a plain fallback picture.
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("writing_build", ROOT / "_writing" / "build.py")
wb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wb)
E, kit, figure = wb.E, wb.kit, wb.figure
SITE = wb.SITE
DATA = json.loads((ROOT / "_problems" / "data.json").read_text())

VERDICT = {"Solo: strong": ("strong", "Solo: strong", "One person can run a real test of this in about 8 weeks."),
           "Solo: possible": ("possible", "Solo: possible", "One person can test a narrow slice of it."),
           "Follow, don't build": ("follow", "Follow, don't build", "Needs labs, hardware or big teams. Learn it and watch it.")}

CSS = """<style>
  .crumbs { font-size:13.5px; color:var(--faint); margin:28px 0 0; } .crumbs a { color:var(--muted); }
  .lede { font-size:19px; color:var(--ink-soft); }
  .vd { display:inline-block; font:13px var(--sans); border:1.3px solid var(--ink); border-radius:20px; padding:1px 11px; margin:0 6px 4px 0; white-space:nowrap; }
  .vd-strong { background:var(--mint-wash); font-weight:700; } .vd-possible { background:var(--butter-wash); } .vd-follow { background:#fff; color:var(--muted); }
  .grp { font:13px var(--sans); color:var(--muted); }
  .pcards { display:grid; grid-template-columns:repeat(auto-fill,minmax(270px,1fr)); gap:12px; margin:10px 0 26px; }
  .pcard { display:block; border:var(--line); border-radius:var(--wob); padding:12px 15px; background:#fff; text-decoration:none; color:var(--ink); }
  .pcard:hover { background:var(--peri-wash); }
  .pcard b { display:block; font-size:16px; line-height:1.3; margin-bottom:5px; }
  .pcard span.w { display:block; font:13.5px var(--sans); color:var(--muted); margin-top:6px; line-height:1.4; }
  section.pg h2 { margin-top:30px; }
  .block { border:var(--line); border-radius:var(--wob); padding:14px 20px; margin:16px 0; background:#fff; }
  .block h2 { margin:0 0 6px; font-size:24px; } .block p { margin:0; }
  .b-why { background:var(--rose-wash); } .b-exp { background:var(--peri-wash); } .b-vd { background:var(--butter-wash); }
  .solo { font-family:var(--sans); font-size:14.5px; } .solo li { margin:4px 0; }
  .pn { display:flex; justify-content:space-between; gap:10px; margin:30px 0 10px; font-family:var(--sans); font-size:14.5px; flex-wrap:wrap; }
  .pn a { border:var(--line); border-radius:var(--wob); padding:6px 14px; text-decoration:none; max-width:48%; }
  .pn small { display:block; color:var(--faint); font-size:11.5px; letter-spacing:.06em; text-transform:uppercase; }
</style>"""

SOLO_TEST = """<ol class="solo">
<li><b>Can it be measured?</b> There is a number that shows you did better, such as an error rate, a catch rate or a cost per answer.</li>
<li><b>Is it cheap to try?</b> It runs on a laptop, free open models and open data, or under about ₹50,000 of rented GPU time.</li>
<li><b>Is there a public yardstick?</b> A benchmark or dataset others use, so your result can be compared and believed.</li>
<li><b>Would a small win get noticed?</b> A lab, a funder or a customer would care about a 10% improvement, not only a full solution.</li>
</ol><p class="solo">Four yeses means <b>Solo: strong</b>. Two or three means <b>Solo: possible</b>. Fewer means <b>Follow, don't build</b>.</p>"""


def load_diagrams():
    out = {}
    for f in sorted((ROOT / "_problems" / "diagrams").glob("*.py")):
        sp = importlib.util.spec_from_file_location(f"pd_{f.stem}", f)
        mod = importlib.util.module_from_spec(sp)
        mod.kit, mod.figure, mod.E, mod.ROOT = kit, figure, E, ROOT
        sp.loader.exec_module(mod)
        for k, v in mod.DRAWINGS.items():
            if k in out:
                raise SystemExit(f"diagram for '{k}' defined twice ({f.name})")
            out[k] = v
    return out


def fallback(p):
    b, a = kit.box, kit.arrow
    d = b(10, 30, 300, 110, "The problem", [p["title"][:40], p["title"][40:80]] if len(p["title"]) > 40 else [p["title"]], "solid")
    d += a(312, 85, 352, 85)
    d += b(355, 30, 290, 110, "Why it is stuck", "see below", "bxs")
    d += a(647, 85, 687, 85)
    d += b(690, 30, 300, 110, "One person's test", "8 weeks, see below", "bx")
    return figure(1000, 170, d, f"The problem, why it is stuck, and a test one person could run: {p['title']}", "A drawing for this problem is on its way.")


def all_problems():
    for g in DATA:
        for i, p in enumerate(g["problems"]):
            yield g, i, p


def problem_page(g, i, p, diagrams):
    v = VERDICT[p["verdict"]]
    pics = diagrams[p["slug"]]() if p["slug"] in diagrams else fallback(p)
    probs = g["problems"]
    prev = probs[i - 1] if i > 0 else None
    nxt = probs[i + 1] if i < len(probs) - 1 else None
    pn = '<div class="pn">'
    pn += (f'<a href="/problems/{prev["slug"]}/"><small>Previous</small>{E(prev["title"])}</a>' if prev else "<span></span>")
    pn += (f'<a href="/problems/{nxt["slug"]}/" style="text-align:right"><small>Next</small>{E(nxt["title"])}</a>' if nxt else "<span></span>")
    pn += "</div>"
    url = f"{SITE}/problems/{p['slug']}/"
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/problems/">Hard problems</a> › <a href="/problems/#{g['id']}">{E(g['title'].split(':')[0])}</a></p>
<div class="hero" style="padding-top:26px"><p class="grp">{E(g['title'])}</p>
<h1>{E(p['title'])}</h1>
<p><span class="vd vd-{v[0]}">{v[1]}</span><span class="grp">{E(v[2])}</span></p></div>
{pics}
<div class="block b-why"><h2>Why it is still open</h2><p>{E(p['why'])}</p></div>
<div class="block b-exp"><h2>An experiment one person can run in 8 weeks</h2><p>{E(p['experiment'])}</p></div>
<div class="block b-vd"><h2>Verdict: {v[1]}</h2><p>{E(p['reason'])}</p></div>
<h2 style="margin-top:28px">The solo test behind the verdict</h2>
{SOLO_TEST}
{pn}
<p class="grp"><a href="/problems/">All 79 hard problems</a> · Working on this, or know of a result we missed? <a href="mailto:basant@cleandataengineering.ai">basant@cleandataengineering.ai</a></p>"""
    desc = f"{p['title']}: why it is still unsolved, an 8-week experiment one person can run, and whether a solo builder can make progress."
    return wb.page(p["title"], desc, url, body, CSS + wb.kit_css())


def overview_drawing():
    """Ten groups as stacked bars: how many problems one person can really test."""
    t = kit.text
    d = t(500, 22, "79 problems in 10 groups: how many one person can test", "bd", "middle")
    colors = {"strong": "pf-bx", "possible": "pf-bxs", "follow": ""}
    y = 44
    for g in DATA:
        n = {"strong": 0, "possible": 0, "follow": 0}
        for p in g["problems"]:
            n[VERDICT[p["verdict"]][0]] += 1
        name = g["title"].split(":")[0]
        d += t(250, y + 19, name, "sm", "end")
        x = 262
        for k in ("strong", "possible", "follow"):
            w = n[k] * 36
            if w:
                cls = f"pf {colors[k]}" if colors[k] else "hz"
                d += f'<rect class="{cls}" x="{x + 3}" y="{y + 6}" width="{w}" height="20" rx="5"/>'
                d += f'<rect class="bx ol" x="{x}" y="{y + 3}" width="{w}" height="20" rx="5"/>'
                d += t(x + w / 2, y + 18, str(n[k]), "sm", "middle")
                x += w
        y += 30
    lx = 262
    for label, cls in (("Solo: strong", "pf pf-bx"), ("Solo: possible", "pf pf-bxs"), ("Follow, don't build", "hz")):
        d += f'<rect class="{cls}" x="{lx}" y="{y + 12}" width="22" height="14" rx="4"/>' + t(lx + 30, y + 24, label, "sm")
        lx += 200
    return figure(1000, y + 40, d, "Ten groups of hard problems as bars, split into Solo: strong, Solo: possible and Follow, don't build.",
                  "India has the most problems one person can test, because careful outside measurement is what India's problems lack most.")


def index_page():
    chips = ('<div class="chips" data-f="v"><button class="on" data-v="">All 79</button>'
             + "".join(f'<button data-v="{k}">{E(lbl)}</button>' for k, lbl, _ in VERDICT.values()) + "</div>")
    jump = " · ".join(f'<a href="#{g["id"]}">{E(g["title"].split(":")[0])}</a>' for g in DATA)
    groups = ""
    for g in DATA:
        cards = "".join(
            f'<a class="pcard" data-v="{VERDICT[p["verdict"]][0]}" href="/problems/{p["slug"]}/"><b>{E(p["title"])}</b>'
            f'<span class="vd vd-{VERDICT[p["verdict"]][0]}">{VERDICT[p["verdict"]][1]}</span>'
            f'<span class="w">{E(p["why"][:140].rsplit(" ", 1)[0] + "…" if len(p["why"]) > 140 else p["why"])}</span></a>'
            for p in g["problems"])
        groups += f'<section class="pg" id="{g["id"]}"><h2>{E(g["title"])} <span class="grp">({len(g["problems"])})</span></h2><div class="pcards">{cards}</div></section>'
    body = f"""<p class="crumbs"><a href="/">Home</a> › Hard problems</p>
<div class="hero" style="padding-top:26px"><p class="eyebrow">Research · open problems · free</p>
<h1>The hardest unsolved problems, and which ones one person can test</h1>
<p class="lede">79 problems nobody has solved yet, from the core of AI to India's own. Each one has its own page with a picture of the problem, why it is still open, an experiment one person could run in about 8 weeks, and a verdict.</p></div>
{overview_drawing()}
<p><b>How the verdict is decided.</b> Every problem was put through the same four questions:</p>
{SOLO_TEST}
<p class="grp" style="margin-top:14px">Jump to: {jump}</p>
{chips}
{groups}
<p><b>The pattern across all 79.</b> The problems one person can really test are mostly about measurement: building the test, the dataset or the honest comparison a field is missing. Labs have compute; what they lack is careful outside measurement, and India's problems get the least of it.</p>
<script>
(function(){{var c=document.querySelector('.chips');c.addEventListener('click',function(e){{var b=e.target.closest('button');if(!b)return;
c.querySelectorAll('button').forEach(function(x){{x.classList.toggle('on',x===b)}});var v=b.dataset.v;
document.querySelectorAll('.pcard').forEach(function(a){{a.style.display=!v||a.dataset.v===v?'':'none'}});
document.querySelectorAll('section.pg').forEach(function(s){{s.style.display=s.querySelector('.pcard:not([style*="none"])')?'':'none'}})}})}})();
</script>"""
    desc = "79 hard unsolved problems in AI, data, chips, robotics, security, science and India, each with an 8-week experiment one person could run and a verdict."
    return wb.page("Hard problems", desc, f"{SITE}/problems/", body, CSS + wb.kit_css())


def main():
    publish = "--publish" in sys.argv
    out = ROOT / ("problems" if publish else "_writing/preview/problems")
    diagrams = load_diagrams()
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(index_page())
    n = 0
    for g, i, p in all_problems():
        d = out / p["slug"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(problem_page(g, i, p, diagrams))
        n += 1
    missing = [p["slug"] for _, _, p in all_problems() if p["slug"] not in diagrams]
    print(f"{n} problem pages + index -> {out}; diagrams {n - len(missing)}/{n}")


if __name__ == "__main__":
    main()
