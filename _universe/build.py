"""Build the AI Universe: the map to draw before the trek.

    python3 _universe/build.py            # draft: _universe/preview/ (git-ignored, never served)
    python3 _universe/build.py --publish  # live: learn/ai-universe/

Pages: the mind map (families of stacks), concept vs physical, "place the new thing", one page per family.
"""
import html
import importlib.util
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("writing_build", ROOT / "_writing" / "build.py")
wb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wb)
kit = wb.kit
from data import FAMILIES, KINDS, PLATFORMS, PLACE, ZOOM  # noqa: E402

E = html.escape
KINDS = dict(KINDS, pattern=("Pattern", "a way of combining concepts, not a product", "RAG, ReAct, human-in-the-loop"))
FILL = {"rose": "#F7D5E3", "mint": "#CDEFD9", "lav": "#DCCFF3", "butter": "#FFE59A", "peri": "#D3E6F7", "peach": "#FBE0D0", "sage": "#DCEBC9"}
WASH = {"rose": "var(--rose-wash)", "mint": "var(--mint-wash)", "lav": "#F5F1FC", "butter": "var(--butter-wash)", "peri": "var(--peri-wash)", "peach": "#FDF3EC", "sage": "#F3F8EC"}
BASE = "/learn/ai-universe"

CSS = """<style>
  .crumbs { font-family:var(--sans); font-size:13.5px; color:var(--faint); margin:28px 0 0; } .crumbs a { color:var(--muted); }
  .zoom { display:inline-block; font:12px var(--sans); border:1.5px solid var(--ink); border-radius:999px; padding:1px 10px; background:var(--butter); margin-left:8px; vertical-align:middle; }
  .bucket { border:1.5px solid var(--ink); border-radius:var(--wob); padding:16px 20px; margin:18px 0; }
  .bucket h3 { font-size:26px; margin:0 0 2px; } .bucket .concept { font-size:16px; color:var(--ink-soft); margin:0 0 8px; }
  .parts { display:flex; gap:6px; flex-wrap:wrap; margin:0 0 10px; } .parts span { font:13px var(--sans); background:#fff; border:1.5px solid var(--ink); border-radius:999px; padding:1px 10px; }
  .phys { width:100%; border-collapse:collapse; font-size:14px; background:#fff; border:1.5px solid var(--ink); }
  .phys th { width:120px; text-align:left; font-size:11.5px; letter-spacing:.08em; text-transform:uppercase; color:var(--faint); padding:6px 10px; border-bottom:1px dashed var(--rule-firm); vertical-align:top; }
  .phys td { padding:6px 10px; border-bottom:1px dashed var(--rule-firm); }
  .label { font:11.5px var(--sans); letter-spacing:.1em; text-transform:uppercase; color:var(--faint); margin:0 0 4px; }
  .steps { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:12px; margin:16px 0; }
  .steps div { border:1.5px solid var(--ink); border-radius:var(--wob); padding:12px 16px; background:var(--peri-wash); }
  .steps b { display:block; font-family:var(--hand); font-weight:400; font-size:22px; }
  .tw { overflow-x:auto; } table.plain { border-collapse:collapse; width:100%; font-size:14.5px; margin:8px 0 18px; }
  table.plain th, table.plain td { text-align:left; padding:7px 10px; border-bottom:1px dashed var(--rule-firm); vertical-align:top; }
  table.plain th { font-size:11.5px; letter-spacing:.08em; text-transform:uppercase; color:var(--faint); }
  .kind { font:12px var(--sans); border:1.5px solid var(--ink); border-radius:999px; padding:0 8px; white-space:nowrap; }
  .fam-nav { display:flex; gap:8px; flex-wrap:wrap; margin:22px 0 0; } .fam-nav a { font:14px var(--sans); text-decoration:none; color:var(--ink); border:1.5px solid var(--ink); border-radius:var(--wob); padding:4px 12px; }
</style>"""


def link(p):
    return f"{BASE}/{p}/" if p else f"{BASE}/"


def crumbs(*parts):
    trail = [f'<a href="{link("")}">AI Universe</a>'] + list(parts)
    return f'<p class="crumbs">{" · ".join(trail)}</p>'


def fam_nav(cur=None):
    return '<div class="fam-nav">' + "".join(
        f'<a href="{link(fid)}" style="background:{FILL[col] if fid == cur else "#fff"}">{E(name)}</a>' for fid, name, _, col, _ in FAMILIES) + "</div>"


def mind_map():
    """The 5-second view: seven families around one AI system."""
    W, H, cx, cy = 1000, 690, 500, 345
    d = ""
    n = len(FAMILIES)
    spots = []
    for i, (fid, name, q, col, buckets) in enumerate(FAMILIES):
        a = -math.pi / 2 + 2 * math.pi * i / n
        x, y = cx + 360 * math.cos(a), cy + 245 * math.sin(a)
        spots.append((x, y))
        d += f'<line class="lnd" x1="{cx}" y1="{cy}" x2="{x}" y2="{y}"/>'
    d += f'<ellipse cx="{cx}" cy="{cy}" rx="128" ry="62" style="fill:#fff;stroke:#222;stroke-width:2.4"/>'
    d += kit.text(cx, cy - 4, "An AI system", "tt", "middle") + kit.text(cx, cy + 22, "seven families of stacks", "sm", "middle")
    for (x, y), (fid, name, q, col, buckets) in zip(spots, FAMILIES):
        w, h = 256, 128
        short = {"harness": "AI application (harness)", "assurance": "Assurance & operations", "compute": "Compute & infrastructure"}.get(fid, name)
        bx, by = x - w / 2, y - h / 2
        names = [b[0] for b in buckets]
        lines, cur = [], ""
        for nm in names:
            if len(cur) + len(nm) > 38:
                lines.append(cur)
                cur = nm
            else:
                cur = (cur + " · " + nm) if cur else nm
        lines.append(cur)
        body = (f'<rect x="{bx + 5}" y="{by + 5}" width="{w - 2}" height="{h - 2}" rx="18" style="fill:{FILL[col]};stroke:none"/>'
                f'<rect x="{bx}" y="{by}" width="{w}" height="{h}" rx="18" style="fill:transparent;stroke:#222;stroke-width:2"/>'
                + kit.text(x, by + 28, short, "tt", "middle") + kit.text(x, by + 48, q, "sm", "middle")
                + "".join(kit.text(x, by + 70 + j * 17, ln, "sm", "middle").replace('class="sm"', 'class="sm" style="font-size:13px"') for j, ln in enumerate(lines[:3])))
        d += f'<a class="lk" href="{link(fid)}"><title>Open: {E(name)}</title>{body}</a>'
    return wb.figure(W, H, d, "A mind map: an AI system in the middle, surrounded by seven families of stacks, each listing its concept buckets.",
                     "Every name you will ever hear goes into one of these seven families, and into one bucket inside it. Click a family to open it.")


def concept_figure():
    """Concept on top, its physical implementations underneath."""
    d = ""
    d += kit.box(330, 14, 340, 92, "Evaluation", ["the concept: inline, online and", "offline checks against a bar"], "solid")
    phys = [("Open source", "DeepEval · promptfoo"), ("Azure", "Foundry evaluation"), ("AWS", "Bedrock evaluations"),
            ("GCP", "Vertex Gen AI eval"), ("Vendors", "LangSmith · Braintrust")]
    for i, (p, t) in enumerate(phys):
        x = 10 + i * 198
        d += kit.arrow(500, 108, x + 92, 176, kind="lnd")
        d += kit.box(x, 178, 184, 70, p, [t], "bx")
    d += kit.text(500, 286, "learn the concept once · the products are where it happens to live", "bd", "middle")
    return wb.figure(1000, 300, d, "The concept of evaluation on top; five physical implementations underneath: open source, Azure, AWS, GCP and vendors.",
                     "The lavender box is the concept. The blue boxes are physical: products that do that job on one platform.")


def harness_figure():
    d = kit.box(300, 14, 400, 92, "Agent harness", ["the concept: loop, context, tools, state,", "checks, durable waits, tracing"], "solid")
    phys = [("Open stack", "Python + Pydantic AI", "/projects/reference-agent/"), ("Azure", "Container Apps + APIM", "/projects/claims-fnol-azure/"),
            ("AWS", "Bedrock AgentCore", None), ("GCP", "ADK + Agent Engine", None)]
    for i, (p, t, h) in enumerate(phys):
        x = 30 + i * 240
        d += kit.arrow(500, 108, x + 105, 176, kind="lnd")
        d += kit.box(x, 178, 210, 70, p, [t], "bx" if h else "bxm", href=None)
    d += kit.text(500, 286, "the same concerns everywhere; only the bindings change", "bd", "middle")
    return wb.figure(1000, 300, d, "The agent harness concept on top; four physical bindings underneath: open stack, Azure, AWS, GCP.",
                     "Solid blue: we have built it (see the projects). Dashed: same concept, not built by us yet.")


def place_figure():
    qs = [("1 · Which family?", "where does it sit in the map"), ("2 · Which bucket?", "what job does it do"),
          ("3 · What kind?", "implementation · bundle · protocol · wrapper · model · pattern"), ("4 · What do I already know?", "the concept's rules apply to it")]
    d = ""
    for i, (t, s) in enumerate(qs):
        x = 10 + i * 248
        d += kit.box(x, 30, 232, 100, t, [s] if len(s) < 34 else [s[:34], s[34:].strip()], "bxs" if i == 2 else "bx")
        if i < 3:
            d += kit.arrow(x + 234, 80, x + 246, 80)
    return wb.figure(1000, 150, d, "Four questions in a row: which family, which bucket, what kind, what do I already know.",
                     "Ask these four about any new name. Most of the time the answer to 4 is: a lot.")


def bucket_html(b, col):
    name, concept, parts, phys = b
    rows = "".join(f"<tr><th>{E(p)}</th><td>{E(phys.get(p, '—'))}</td></tr>" for p in PLATFORMS)
    return (f'<div class="bucket" style="background:{WASH[col]}"><p class="label">Concept</p><h3>{E(name)}</h3>'
            f'<p class="concept">{E(concept)}</p><div class="parts">{"".join(f"<span>{E(x)}</span>" for x in parts)}</div>'
            f'<p class="label">Physical: who does this job, where</p><table class="phys">{rows}</table></div>')


def index_page():
    fams = "".join(f'<li><a href="{link(fid)}">{E(name)}</a>: {E(q)} <span style="color:var(--faint)">({len(b)} buckets)</span></li>'
                   for fid, name, q, col, b in FAMILIES)
    body = f"""<div class="hero hub-hero"><div><h1>The AI Universe</h1>
<p class="thesis">So many names, every week. Before you climb, draw the map. Every product, library, protocol and model you will ever hear about fits into <em>one of seven families</em>, and into one bucket inside it. Learn the bucket once, as a concept; then every new name is just another way of doing a job you already understand.</p></div>
<img src="/assets/illustrations/learn.svg" alt="" width="420" height="300"></div>
<h2>The map, in five seconds <span class="zoom">zoom 1</span></h2>
{mind_map()}
<h2>How to use it</h2>
<div class="steps">
<div><b>Concept first</b>Each bucket is a job with rules, like the logic of a program. Learn that once.</div>
<div><b>Physical second</b>Products are where the job happens to be done: open source, Azure, AWS, GCP, a vendor. Like the language you write the logic in.</div>
<div><b>Place every new name</b>Four questions file anything new in under a minute. <a href="{link('place-it')}">Try it →</a></div>
<div><b>Then zoom in</b>Each family links to the course or project that goes deep. <a href="{link('harness')}">Start with the harness →</a></div>
</div>
<h2>The seven families</h2><ol>{fams}</ol>
<p>Next: <a href="{link('concept-and-physical')}">concept and physical, the one idea that makes this work →</a></p>
"""
    return wb.page("The AI Universe", "A map of the whole AI landscape: seven families of stacks, the concept buckets inside each, and the products that fill them.",
                   f"{wb.SITE}{link('')}", body, wb.kit_css() + CSS)


def concept_page():
    body = f"""{crumbs('Concept and physical')}
<div class="hero"><h1>Concept and physical</h1>
<p class="thesis">A <em>concept</em> is the job and its rules. A <em>physical</em> thing is a product doing that job somewhere. Sorting is a concept; writing it in Java or Python is physical. Evaluation is a concept; doing it in LangSmith or DeepEval is physical.</p></div>
{concept_figure()}
<h2>The same idea, for a whole system</h2>
<p>The agent harness is a concept too: a loop, context, tools, state, checks, durable waits and tracing around a model call. It can be built on any platform. We built it twice, the same concerns both times; only the bindings changed.</p>
{harness_figure()}
<h2>Why this matters when you learn</h2>
<div class="tw"><table class="plain"><tr><th>When you learn…</th><th>…you can</th></tr>
<tr><td>the concept (what the job is, what can go wrong)</td><td>judge any product that claims to do it, in an hour</td></tr>
<tr><td>only a product</td><td>use that one product, until it changes or you move platform</td></tr>
<tr><td>the concept, then one product properly</td><td>switch to the next product by mapping, not relearning</td></tr></table></div>
<h2>Five kinds of physical thing</h2>
<div class="tw"><table class="plain"><tr><th>Kind</th><th>What it is</th><th>Examples</th></tr>
{"".join(f"<tr><td><span class='kind'>{E(n)}</span></td><td>{E(w)}</td><td>{E(x)}</td></tr>" for n, w, x in KINDS.values())}</table></div>
<p>Next: <a href="{link('place-it')}">place the new thing →</a></p>
{fam_nav()}"""
    return wb.page("Concept and physical", "Learn the concept once; products are where it happens to live.", f"{wb.SITE}{link('concept-and-physical')}", body, wb.kit_css() + CSS)


def place_page():
    fam = {fid: (name, col) for fid, name, q, col, b in FAMILIES}
    rows = "".join(f"<tr><td><b>{E(n)}</b></td><td><a href='{link(f)}'>{E(fam[f][0])}</a></td><td>{E(b)}</td>"
                   f"<td><span class='kind'>{E(KINDS[k][0])}</span></td><td>{E(knew)}</td></tr>"
                   for n, f, b, k, knew in sorted(PLACE, key=lambda r: ([x[0] for x in FAMILIES].index(r[1]), r[2], r[0])))
    body = f"""{crumbs('Place the new thing')}
<div class="hero"><h1>Place the new thing</h1>
<p class="thesis">A new name appears. Before reading its docs, ask four questions. Most of the time you discover you already understand it: it is a known concept, done a new way.</p></div>
{place_figure()}
<h2>{len(PLACE)} names, already placed</h2>
<div class="tw"><table class="plain"><tr><th>Name</th><th>Family</th><th>Bucket</th><th>Kind</th><th>You already know it as</th></tr>{rows}</table></div>
<p>Some names sit in several buckets: a bundle like Microsoft Foundry or Databricks spans many families. Place it by the job you are using it for.</p>
{fam_nav()}"""
    return wb.page("Place the new thing", "Four questions that file any new AI name into a concept you already know.", f"{wb.SITE}{link('place-it')}", body, wb.kit_css() + CSS)


def family_page(fam, i):
    fid, name, q, col, buckets = fam
    zoom = "".join(f'<li><a href="{u}">{E(t)}</a></li>' for t, u in ZOOM.get(fid, []))
    prev_f = FAMILIES[i - 1] if i > 0 else None
    next_f = FAMILIES[i + 1] if i < len(FAMILIES) - 1 else None
    nav = (f'<a href="{link(prev_f[0])}">← {E(prev_f[1])}</a>' if prev_f else "") + (" · " if prev_f and next_f else "") + (f'<a href="{link(next_f[0])}">{E(next_f[1])} →</a>' if next_f else "")
    body = f"""{crumbs(E(name))}
<div class="hero"><h1>{E(name)} <span class="zoom">zoom 2</span></h1>
<p class="thesis">{E(q)} {len(buckets)} concept buckets. Each one is a job you can learn once; underneath it, who does that job on each platform.</p></div>
{"".join(bucket_html(b, col) for b in buckets)}
{f"<h2>Zoom in further</h2><ul>{zoom}</ul>" if zoom else ""}
<p style="font-family:var(--sans)">{nav}</p>
{fam_nav(fid)}"""
    return wb.page(name, f"{name}: {q}", f"{wb.SITE}{link(fid)}", body, wb.kit_css() + CSS)


def main():
    global BASE
    publish = "--publish" in sys.argv
    out = ROOT / "learn" / "ai-universe" if publish else HERE / "preview"
    if not publish:
        BASE = "/_universe/preview"
    pages = {"": index_page(), "concept-and-physical": concept_page(), "place-it": place_page()}
    for i, f in enumerate(FAMILIES):
        pages[f[0]] = family_page(f, i)
    for rel, html_ in pages.items():
        d = out / rel if rel else out
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(html_)
    print(f"{len(pages)} pages -> {out}")


if __name__ == "__main__":
    main()
