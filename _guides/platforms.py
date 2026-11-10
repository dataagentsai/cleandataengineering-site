"""Platform hubs: /platforms/ and /platforms/<id>/ (Databricks, AWS, Azure, Google Cloud, Open source, Claude).

    python3 _guides/platforms.py      (then python3 _site/nav.py and python3 _site/seo.py)

The menu answers three questions (agreed with the owner, 10 Nov 2026): Foundations = what (data
systems, data platform; platform-neutral), Streams = who (data, AI, LLM, ML, software, FDE),
Platforms = with which product. A platform is a binding: each hub maps the concepts to its products,
lists the pages specific to it, each stream's path on it, and its certifications. Certifications
moved here from their own menu group.
"""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("data_systems_pf", ROOT / "_guides" / "data_systems.py")
ds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ds)
mspec = importlib.util.spec_from_file_location("medallion_pf", ROOT / "_guides" / "medallion.py")
med = importlib.util.module_from_spec(mspec)
mspec.loader.exec_module(med)
sys.path.insert(0, str(ROOT / "_paths"))
from data import DISCIPLINES  # noqa: E402

E, wb, SITE = ds.E, ds.wb, ds.SITE

# id: (name, column in medallion PRODUCTS or None, lede, pages, certifications)
PLATFORMS = {
    "databricks": ("Databricks", 4, "The lakehouse platform on any cloud: Unity Catalog, Lakeflow, SQL warehouses, Genie and Mosaic AI.", [
        ("Databricks cost calculator", "/learn/data-systems/platform/cost/calculator/", "Whole-platform and per-hop cost with streaming and hidden costs."),
        ("Data platform on AWS + Databricks", "/learn/data-platform-architecture/aws-databricks/", "The whole picture with a product in every box."),
        ("DataTwin Studio", "/learn/data-platform-sim/", "One batch through Spark and Delta Lake, recorded from a real run."),
        ("Unity Catalog done right", "/writing/unity-catalog-done-right/", "Blog: one governance model for data and AI."),
        ("Streaming on Databricks without the pain", "/writing/databricks-streaming/", "Blog: when and how to stream."),
        ("CI/CD with Asset Bundles", "/writing/databricks-asset-bundles/", "Blog: deploying Databricks like software."),
        ("Genie and metric views", "/writing/genie-metric-views/", "Blog: talk to your data the right way."),
        ("Your Databricks bill has a leak", "/writing/databricks-cost-leaks/", "Blog: ten cost mistakes."),
    ], [("Generative AI Engineer Associate, free prep", "/certifications/databricks-genai-engineer/")]),
    "aws": ("AWS", 1, "Amazon Web Services: S3, Glue, EMR, Redshift, Bedrock and the rest, used directly or under Databricks.", [
        ("Data platform on AWS + Databricks", "/learn/data-platform-architecture/aws-databricks/", "Every box of the data platform with its AWS and Databricks product."),
        ("The ETL, end to end (AWS)", "/learn/data-platform-architecture/aws-databricks/etl/", "One ETL followed from source to dashboard."),
        ("Agent Harness on AWS", "/learn/agent-harness-aws/", "The agent harness, concern by concern, on AWS services."),
        ("Databricks cost calculator (AWS prices)", "/learn/data-systems/platform/cost/calculator/", "Uses AWS EC2, S3 and network list prices."),
    ], []),
    "azure": ("Azure and Microsoft Fabric", 2, "Microsoft's cloud: OneLake and Fabric for data, Azure AI Foundry for AI, Azure Databricks.", [
        ("Claims assistant on Azure", "https://github.com/dataagentsai/claims-fnol-azure", "Open-source code: an insurance claims assistant built on Azure."),
    ], [("AI-103 Azure AI Engineer, free prep", "/certifications/azure-ai-engineer/")]),
    "gcp": ("Google Cloud", 3, "Google's cloud: BigQuery, Dataflow, Dataplex and Vertex AI.", [], []),
    "open": ("Open source", 5, "The same platform built from open-source parts: Spark, Delta or Iceberg, dbt, Airflow or Dagster, OpenMetadata.", [
        ("Open-source code from this site", "/assets/", "Reference Agent, AgentTwin, Eval Harness Framework and more."),
        ("Shift left: fail fast on data code", "/learn/shift-left/", "Open checks for PySpark, SQL and Databricks code."),
    ], []),
    "anthropic": ("Claude (Anthropic)", None, "The model platform the AI streams build on: the Claude API, tools, agents and Claude Code.", [
        ("Claude API Simulator", "/learn/llm-api-sim/", "See what goes in and out of the Claude API, step by step."),
        ("Agent Harness", "/learn/agent-harness/", "Everything around the model that makes an agent safe and useful."),
        ("Agent Harness Simulator", "/learn/agent-harness-sim/", "Run an agent through the harness and watch each concern act."),
    ], [("Claude Certified Architect (CCA-F)", "/certifications/claude-certified-architect/CCA-F/"),
        ("CCA-F mind maps", "/certifications/cca-f-mind-maps/"),
        ("Claude Architect, Professional", "/certifications/claude-certified-architect/CCAR-P/")]),
}
ORDER = ["databricks", "aws", "azure", "gcp", "open", "anthropic"]


def exists(href):
    if href.startswith("http"):
        return True
    path = href.split("#")[0].split("?")[0]
    return (ROOT / path.strip("/") / "index.html").exists() or (ROOT / path.strip("/")).is_file()


def cards(items):
    return '<div class="cards">' + "".join(
        f'<div class="card"><h3><a href="{h}">{E(n)}</a></h3><p class="one">{E(t)}</p></div>' for n, h, t in items if exists(h)) + "</div>"


def hub(pid):
    name, col, lede, pages, certs = PLATFORMS[pid]
    secs = []
    if col is not None:
        rows = "".join(f"<tr><td><b>{E(r[0])}</b></td><td>{E(r[col])}</td></tr>" for r in med.PRODUCTS)
        secs.append(("map", "Concepts to products", f"""<p class="eyebrow">The binding</p><h2>Each job of the data platform, on {E(name)}</h2>
<p>The jobs come from the <a href="/learn/data-systems/platform/">data platform foundations</a>; only the product changes per platform.</p>
<div class="tw"><table class="t"><tr><th>Job</th><th>Product on {E(name)}</th></tr>{rows}</table></div>
<p class="note">Product names change often; check the current docs before you build.</p>"""))
    if pages:
        secs.append(("pages", "Pages for this platform", f'<p class="eyebrow">On this site</p><h2>Pages for {E(name)}</h2>{cards(pages)}'))
    if pid != "anthropic":
        paths = "".join(f'<a href="/paths/{d["id"]}/{pid}/">{E(d["name"])}</a>' for d in DISCIPLINES if pid in d["platforms"])
        secs.append(("paths", "Paths by stream", f'<p class="eyebrow">By stream</p><h2>Learning paths on {E(name)}</h2><p>Crawl, walk and run for each role, on {E(name)}.</p><div class="ideas">{paths}</div>'))
    cert_html = ('<ul>' + "".join(f'<li><a href="{h}">{E(n)}</a></li>' for n, h in certs) + "</ul>") if certs else '<p>No free prep on this site yet. See <a href="/certifications/">all certifications</a>.</p>'
    secs.append(("certs", "Certifications", f'<p class="eyebrow">Certifications</p><h2>{E(name)} certifications</h2>{cert_html}'))
    toc = "".join(f'<li><a href="#{sid}">{E(t)}</a></li>' for sid, t, _ in secs)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/platforms/">Platforms</a> › {E(name)}</p>
<p class="eyebrow" style="margin-top:22px">Platform · a binding for the foundations and streams</p>
<h1>{E(name)}</h1>
<p class="lede">{E(lede)} Learn the ideas once in the <a href="/learn/data-systems/">foundations</a>; this page shows how they map to {E(name)}.</p>
<nav class="toc"><b>On this page</b><ol>{toc}</ol></nav>
""" + "".join(f'<section id="{sid}">{h}</section>' for sid, _t, h in secs)
    url = f"{SITE}/platforms/{pid}/"
    desc = f"{name} on Clean Data Engineering: data platform concepts mapped to {name} products, guides and tools for {name}, learning paths by role, and certification prep."
    return wb.page(name, desc, url, body, ds.CSS + ds.ld(name, desc, url, [("Platforms", "/platforms/"), (name, f"/platforms/{pid}/")]))


def index():
    items = "".join(f'<div class="card"><h3><a href="/platforms/{p}/">{E(PLATFORMS[p][0])}</a></h3><p class="one">{E(PLATFORMS[p][2])}</p></div>' for p in ORDER)
    body = f"""<p class="crumbs"><a href="/">Home</a> › Platforms</p>
<p class="eyebrow" style="margin-top:22px">With which product</p>
<h1>Platforms</h1>
<p class="lede">The site is arranged around three questions. <b>Foundations</b>: what a data system and a data platform are, the same everywhere. <b>Streams</b>: who does what, by role. <b>Platforms</b>: which product does each job on the platform you use. Learn the idea once; the platform is a binding.</p>
<div class="cards">{items}</div>"""
    url = f"{SITE}/platforms/"
    desc = "Data and AI platforms as bindings: Databricks, AWS, Azure and Fabric, Google Cloud, open source and Claude, each with concepts mapped to products, guides, learning paths and certification prep."
    return wb.page("Platforms", desc, url, body, ds.CSS + ds.ld("Platforms", desc, url, [("Platforms", "/platforms/")]))


def main():
    out = ROOT / "platforms"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(index())
    for p in ORDER:
        (out / p).mkdir(exist_ok=True)
        (out / p / "index.html").write_text(hub(p))
    print("platform hubs ->", out)


if __name__ == "__main__":
    main()
