"""The Data Engineering hub at /data-engineering/: every data engineering page on the site, leader-first.

    python3 _guides/de_hub.py      (then python3 _site/nav.py and python3 _site/seo.py)

Agreed with the owner on 10 Nov 2026: pages move into streams in the menu (Data Engineering, AI
Engineering, ...) instead of one long Courses list; URLs never change. This hub is the stream's landing
page. Order: the story (Data systems), architecture guides, tools and simulators, delivering projects,
key concepts (from _paths/concepts.py ROLE_GROUPS), then learning paths by platform.
"""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("data_systems_hub", ROOT / "_guides" / "data_systems.py")
ds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ds)
sys.path.insert(0, str(ROOT / "_paths"))
from concepts import CARDS, ROLE_GROUPS  # noqa: E402
from data import DISCIPLINES, PLATFORMS  # noqa: E402

E, wb, SITE = ds.E, ds.wb, ds.SITE
URL = f"{SITE}/data-engineering/"

STORY = [
    ("Data systems, end to end", "/learn/data-systems/", "rose", "Start here. Upstreams, the data platform and downstreams on one page, then a page per block and per hop with the questions to chase, what breaks in production and the decisions."),
    ("Upstreams: know your sources", "/learn/data-systems/upstreams/", "grey", "70 questions to ask about every source, with the reason for each; APIs, files, joins, and where the answers go."),
    ("The data platform, whole", "/learn/data-systems/platform/", "silver", "Five hops along the medallion and 24 cross-cutting concerns, with layout, environments and cost pages."),
]
GUIDES = [
    ("Data platform architecture", "/learn/data-platform-architecture/", "How we build it: control plane, metadata, three services, streaming lane, agents that only suggest."),
    ("Medallion architecture", "/learn/medallion-architecture/", "Bronze, silver and gold, one order through every layer, nine rules, products per platform."),
    ("Real-time analytics", "/learn/real-time-analytics/", "From a database change to a number on screen in a second: designs, products and cost."),
    ("Test architecture for data", "/learn/data-platform-architecture/testing/", "Unit, contract, data and simulation tests, and where each runs."),
    ("Shift left: fail fast on data code", "/learn/shift-left/", "Static and offline checks that catch PySpark and SQL problems before they run."),
    ("AWS + Databricks, and the ETL end to end", "/learn/data-platform-architecture/aws-databricks/", "The whole picture with a product in every box, and one ETL followed end to end."),
]
TOOLS = [
    ("Databricks cost calculator", "/learn/data-systems/platform/cost/calculator/", "Whole-platform and per-hop cost, streaming, hidden costs, what drives your bill."),
    ("Source system questionnaire", "/learn/data-systems/upstreams/questionnaire/", "The upstream questions as a printable form for source owners."),
    ("DataTwin Studio", "/learn/data-platform-sim/", "Watch one batch go through a real Spark and Delta Lake platform, then break it."),
    ("Problem Lab", "/learn/data-platform-sim/problems/", "Common data platform problems, reproduced and fixed."),
    ("Performance stories", "/learn/data-platform-sim/performance/", "Why jobs are slow, shown on real runs."),
]
DELIVER = [
    ("The technical anchor", "/learn/technical-anchor/", "The role that holds a data project's technical shape together."),
    ("Discovery", "/learn/technical-anchor/discovery/", "Fail fast for the whole project: the discovery document, beliefs to test, sign-off."),
    ("Project review", "/learn/technical-anchor/project-review/", "Review a data project's documents for gaps at its stage, with the checks."),
    ("Hard problems by layer", "/learn/hard-problems/", "The problems that are still hard at each layer of a data platform."),
]


MORE = [
    ("Spec-driven data platforms", "/leaders/spec-driven/data-platform/", "For leaders: describe the platform in specs, and generate and check the rest."),
    ("DataTwin, explained", "/learn/datatwin/", "Open spec: a fire drill for a data platform, with pretend sources and known answers."),
    ("Clean Data Engineering specs", "/projects/data-eng-specs/", "Open specs for what a data platform must have, be and face."),
    ("Data engineering projects to join", "/projects/?subject=data", "Real projects with a page each: why, architecture, tasks to pick up."),
]


def cards(items, with_fill=False):
    out = ""
    for it in items:
        if with_fill:
            name, href, fill, text = it
            style = f' style="--w:{ds.FILL[fill]}"'
        else:
            name, href, text = it
            style = ""
        out += f'<div class="card"{style}><h3><a href="{href}">{E(name)}</a></h3><p class="one">{E(text)}</p></div>'
    return f'<div class="cards">{out}</div>'


def page():
    de = next(d for d in DISCIPLINES if d["id"] == "data-engineering")
    groups = "".join(
        f'<h3>{E(g)}</h3><div class="ideas">' + "".join(f'<a href="/concepts/{c}/">{E(CARDS[c]["name"])}</a>' for c in ids if c in CARDS) + "</div>"
        for g, ids in ROLE_GROUPS["data-engineering"])
    paths = "".join(f'<a href="/paths/data-engineering/{p}/">{E(PLATFORMS[p])}</a>' for p in de["platforms"])
    body = f"""<p class="crumbs"><a href="/">Home</a> › Data Engineering</p>
<p class="eyebrow" style="margin-top:22px">Stream · free guides, tools and paths</p>
<h1>Data Engineering</h1>
<p class="lede">Everything on this site about building data platforms: the story from sources to dashboards and agents, the architecture guides, tools and simulators, how to deliver data projects, the key concepts, and learning paths for each platform.</p>
<nav class="toc"><b>On this page</b><ol>
<li><a href="#story">Start here: data systems, end to end</a></li><li><a href="#guides">Architecture guides</a></li><li><a href="#tools">Tools and simulators</a></li>
<li><a href="#deliver">Delivering data projects</a></li><li><a href="#more">Specifications, projects, leaders</a></li><li><a href="#concepts">Key concepts</a></li><li><a href="#paths">Learning path by platform</a></li></ol></nav>

<section id="story"><p class="eyebrow">Foundations · shared by every stream</p><h2>Start with the data system, then the platform</h2>
<p>For data leaders first, then builders: the whole data system in one picture, then a page for each part with the questions to chase and the decisions to take.</p>{cards(STORY, True)}</section>

<section id="guides"><p class="eyebrow">Foundations · data platform</p><h2>Architecture guides</h2>{cards(GUIDES)}</section>

<section id="tools"><p class="eyebrow">Data Engineering · practice</p><h2>Tools and simulators</h2>{cards(TOOLS)}</section>

<section id="deliver"><p class="eyebrow">Data Engineering · practice</p><h2>Delivering data projects</h2>{cards(DELIVER)}</section>

<section id="more"><p class="eyebrow">Data Engineering · build with us</p><h2>Open specifications, projects and leaders</h2>{cards(MORE)}</section>

<section id="concepts"><p class="eyebrow">Data Engineering · key concepts</p><h2>Key concepts</h2>
<p>Short pages on the ideas every data engineer uses, whatever the platform. The <a href="/concepts/#a-z">full A to Z</a> covers every stream.</p>{groups}</section>

<section id="paths"><p class="eyebrow">Data Engineering · on your platform</p><h2>Learning path by platform</h2>
<p>Crawl, walk and run on the platform you use, with projects. <a href="/paths/data-engineering/">See the whole path</a>.</p><div class="ideas">{paths}</div></section>"""
    title = "Data Engineering"
    desc = "Free data engineering guides, tools and learning paths: data systems end to end, upstream questions, medallion and platform architecture, a Databricks cost calculator, simulators and key concepts."
    return wb.page(title, desc, URL, body, ds.CSS + ds.ld(title, desc, URL, [("Data Engineering", "/data-engineering/")]))


def main():
    out = ROOT / "data-engineering"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(page())
    print("hub ->", out)


if __name__ == "__main__":
    main()
