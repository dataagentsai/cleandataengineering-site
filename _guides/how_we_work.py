"""How we work: the skills that aren't a technology, at /how-we-work/.

    python3 _guides/how_we_work.py      (then python3 _site/nav.py and python3 _site/seo.py)

Agreed with the owner on 10 Nov 2026: a menu group of its own, after Your role, for skills every role
uses. Sections: thinking principles, business analysis, project management, the technical anchor.
More is coming in each (the owner named thinking principles, project management and BA); add pages to
the lists below and they appear here and can be added to the menu in _site/nav.py.
"""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("data_systems_hww", ROOT / "_guides" / "data_systems.py")
ds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ds)
sys.path.insert(0, str(ROOT / "_paths"))
from concepts import CARDS  # noqa: E402

E, wb, SITE = ds.E, ds.wb, ds.SITE
URL = f"{SITE}/how-we-work/"

# (id, title, one line, [(name, href, text)], [concept ids], what is coming)
SECTIONS = [
    ("thinking", "Thinking principles", "How we decide: the habits behind every design on this site.", [
        ("Questions first, then design", "/learn/data-systems/", "Every page here starts from the questions to chase, then the decisions; the Data systems pages show the pattern."),
        ("Critical thinking in data projects", "/how-we-work/critical-thinking/", "Five habits for claims, numbers and designs: what exactly is claimed, what is the evidence, what else explains it, what would prove it wrong, what does it cost to be wrong."),
    ], ["deterministic-first", "scope-out", "evidence", "reusable-assets"], "More principles: reuse first and build only the gap, design end to end before building, one home per fact, and others."),
    ("ba", "Business analysis", "Turning what people need into something a platform can promise.", [
        ("Source system questionnaire", "/learn/data-systems/upstreams/questionnaire/", "What to ask every source owner, with the reason for each question."),
        ("Know your consumers", "/learn/data-systems/downstreams/", "The consumer register: who uses the data, what for, and what they need."),
        ("Where the answers go", "/learn/data-systems/upstreams/answers/", "Turning answers into contracts, settings and tests."),
    ], ["success-measure", "data-map", "discovery"], "Requirements that can be tested against data, metric definitions with owners, and acceptance criteria."),
    ("pm", "Project management", "Running data and AI projects so they finish, and finish right.", [
        ("Discovery: fail fast for the whole project", "/learn/technical-anchor/discovery/", "The discovery document, the beliefs to test, reviews and sign-off."),
        ("Project review", "/learn/technical-anchor/project-review/", "Review a project's documents for gaps at its stage."),
        ("Top project management mistakes in data projects", "/how-we-work/project-management-mistakes/", "Why data projects break normal project management, the mistakes we see most, early warning signs and a healthier plan shape."),
        ("Estimation mistakes in data projects", "/how-we-work/estimation/", "Twelve mistakes that make data estimates wrong, why each happens, and how to avoid it, with a worked estimate."),
        ("Where data engineering time goes", "/learn/where-data-engineering-time-goes/", "Most hours go to understanding source meaning, not code; the non-technical work and how to cut it."),
    ], ["prototype-product", "handover", "deploy-their-cloud"], "Planning in tiers, estimating, risks and dependencies, status that tells the truth, and stakeholder updates."),
    ("anchor", "The technical anchor", "The person who holds a project's technical shape together, across roles.", [
        ("The technical anchor", "/learn/technical-anchor/", "What the role does, and why projects without one drift."),
        ("Project review: the checks", "/learn/technical-anchor/project-review/checks/", "The full list of checks, by stage."),
    ], [], ""),
]


def exists(href):
    return (ROOT / href.split("#")[0].strip("/") / "index.html").exists()


def page():
    secs, toc = "", ""
    for sid, title, one, pages, concepts, coming in SECTIONS:
        toc += f'<li><a href="#{sid}">{E(title)}</a></li>'
        cards = "".join(f'<div class="card"><h3><a href="{h}">{E(n)}</a></h3><p class="one">{E(t)}</p></div>' for n, h, t in pages if exists(h))
        chips = "".join(f'<a href="/concepts/{c}/">{E(CARDS[c]["name"])}</a>' for c in concepts if c in CARDS)
        secs += (f'<section id="{sid}"><p class="eyebrow">How we work</p><h2>{E(title)}</h2><p>{E(one)}</p>'
                 + (f'<div class="cards">{cards}</div>' if cards else "")
                 + (f'<h3>Short ideas</h3><div class="ideas">{chips}</div>' if chips else "")
                 + (f'<p class="note">Coming: {E(coming)}</p>' if coming else "") + "</section>")
    body = f"""<p class="crumbs"><a href="/">Home</a> › How we work</p>
<p class="eyebrow" style="margin-top:22px">Skills that aren't a technology</p>
<h1>How we work</h1>
<p class="lede">The skills every role uses, whatever the platform: how we think and decide, how we find out what people need, how we run projects, and the role that holds a project's technical shape together.</p>
<nav class="toc"><b>On this page</b><ol>{toc}</ol></nav>
{secs}"""
    desc = "How we work on data and AI projects: thinking principles, business analysis, project management and the technical anchor role, with discovery, project review and questionnaires."
    return wb.page("How we work", desc, URL, body, ds.CSS + ds.ld("How we work", desc, URL, [("How we work", "/how-we-work/")]))


def main():
    out = ROOT / "how-we-work"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(page())
    print("how we work ->", out)


if __name__ == "__main__":
    main()
