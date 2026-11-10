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

# The same headings as the concepts tree (agreed 10 Nov 2026): data systems, data engineering, BI, ML, AI,
# across all, certifications. Each heading: a job -> product table (DE comes from the medallion guide's
# PRODUCTS table) and this site's pages for that cloud under that heading.
SECTIONS = [("systems", "Data systems: in and out"), ("de", "Data engineering"), ("bi", "BI and analytics"),
            ("ml", "ML"), ("ai", "AI"), ("across", "Across all of them"), ("paths", "Learning paths by role"), ("certs", "Certifications")]
COLS = {"aws": 1, "azure": 2, "gcp": 3, "databricks": 4, "open": 5}

MAPS = {  # heading -> [(job, {platform: product})]
    "systems": [
        ("Change data capture from databases", {"databricks": "Lakeflow Connect", "aws": "AWS DMS", "azure": "Data Factory, Fabric mirroring", "gcp": "Datastream", "open": "Debezium"}),
        ("Connectors to SaaS apps", {"databricks": "Lakeflow Connect", "aws": "Amazon AppFlow", "azure": "Data Factory connectors", "gcp": "BigQuery Data Transfer Service", "open": "Airbyte or dlt"}),
        ("Sharing data out", {"databricks": "Delta Sharing, Marketplace", "aws": "AWS Data Exchange, Lake Formation sharing", "azure": "OneLake shortcuts, Azure Data Share", "gcp": "Analytics Hub", "open": "Delta Sharing (open protocol)"}),
    ],
    "bi": [
        ("Semantic layer", {"databricks": "Metric views", "aws": "dbt semantic layer", "azure": "Power BI semantic models", "gcp": "Looker (LookML)", "open": "Cube Core"}),
        ("Dashboards", {"databricks": "AI/BI dashboards", "aws": "Amazon QuickSight", "azure": "Power BI", "gcp": "Looker, Looker Studio", "open": "Apache Superset"}),
        ("Ask in plain words", {"databricks": "Genie", "aws": "Amazon Q in QuickSight", "azure": "Copilot in Power BI", "gcp": "Gemini in Looker", "open": "Your own, over Cube"}),
    ],
    "ml": [
        ("Experiments and model registry", {"databricks": "MLflow (managed)", "aws": "SageMaker experiments and model registry", "azure": "Azure Machine Learning", "gcp": "Vertex AI experiments and registry", "open": "MLflow"}),
        ("Features", {"databricks": "Feature engineering in Unity Catalog", "aws": "SageMaker Feature Store", "azure": "Azure ML feature store", "gcp": "Vertex AI Feature Store", "open": "Feast"}),
        ("Model serving", {"databricks": "Model Serving", "aws": "SageMaker endpoints", "azure": "Azure ML online endpoints", "gcp": "Vertex AI endpoints", "open": "KServe or BentoML"}),
    ],
    "ai": [
        ("Models", {"databricks": "Foundation Model APIs, AI Gateway", "aws": "Amazon Bedrock", "azure": "Azure AI Foundry models", "gcp": "Vertex AI (Gemini)", "open": "Open-weight models served with vLLM", "anthropic": "Claude API"}),
        ("Agents", {"databricks": "Mosaic AI Agent Framework", "aws": "Bedrock AgentCore", "azure": "Foundry Agent Service", "gcp": "Vertex AI Agent Builder", "open": "LangGraph, or your own harness", "anthropic": "Claude Agent SDK; tools through MCP"}),
        ("Retrieval", {"databricks": "Vector Search", "aws": "Bedrock Knowledge Bases", "azure": "Azure AI Search", "gcp": "Vertex AI Vector Search", "open": "pgvector or Qdrant", "anthropic": "Bring your own; connect through tools"}),
        ("Evaluation and guardrails", {"databricks": "Agent Evaluation (MLflow)", "aws": "Bedrock Guardrails and evaluations", "azure": "Content Safety, Foundry evaluations", "gcp": "Vertex AI evaluation", "open": "Eval Harness Framework (this site)", "anthropic": "Your harness and evals around the API"}),
    ],
    "across": [
        ("Governance and access", {"databricks": "Unity Catalog", "aws": "Lake Formation, IAM", "azure": "Microsoft Purview, Entra ID", "gcp": "Dataplex, IAM", "open": "OpenMetadata"}),
        ("Cost", {"databricks": "Billing system tables, budgets", "aws": "Cost Explorer, Budgets", "azure": "Cost Management", "gcp": "Cloud Billing", "open": "Your own cost tables"}),
        ("Observability", {"databricks": "System tables, data quality monitoring", "aws": "CloudWatch", "azure": "Azure Monitor", "gcp": "Cloud Monitoring", "open": "OpenTelemetry"}),
        ("Infrastructure as code", {"databricks": "Asset Bundles, Terraform", "aws": "CDK or CloudFormation, Terraform", "azure": "Bicep, Terraform", "gcp": "Terraform", "open": "Terraform or OpenTofu"}),
    ],
}

# id: (name, lede, {heading: [pages]}, certifications)
PLATFORMS = {
    "databricks": ("Databricks", "The lakehouse platform on any cloud: Unity Catalog, Lakeflow, SQL warehouses, Genie and Mosaic AI.", {
        "de": [("Data platform on AWS + Databricks", "/learn/data-platform-architecture/aws-databricks/", "The whole picture with a product in every box."),
               ("DataTwin Studio", "/learn/data-platform-sim/", "One batch through Spark and Delta Lake, recorded from a real run."),
               ("Streaming on Databricks without the pain", "/writing/databricks-streaming/", "Blog: when and how to stream.")],
        "bi": [("Genie and metric views", "/writing/genie-metric-views/", "Blog: talk to your data the right way.")],
        "across": [("Databricks cost calculator", "/learn/data-systems/platform/cost/calculator/", "Whole-platform and per-hop cost with streaming and hidden costs."),
                   ("Unity Catalog done right", "/writing/unity-catalog-done-right/", "Blog: one governance model for data and AI."),
                   ("CI/CD with Asset Bundles", "/writing/databricks-asset-bundles/", "Blog: deploying Databricks like software."),
                   ("Your Databricks bill has a leak", "/writing/databricks-cost-leaks/", "Blog: ten cost mistakes.")],
    }, [("Generative AI Engineer Associate, free prep", "/certifications/databricks-genai-engineer/")]),
    "aws": ("AWS", "Amazon Web Services: S3, Glue, EMR, Redshift, Bedrock and the rest, used directly or under Databricks.", {
        "de": [("Data platform on AWS + Databricks", "/learn/data-platform-architecture/aws-databricks/", "Every box of the data platform with its AWS and Databricks product."),
               ("The ETL, end to end (AWS)", "/learn/data-platform-architecture/aws-databricks/etl/", "One ETL followed from source to dashboard.")],
        "ai": [("Agent Harness on AWS", "/learn/agent-harness-aws/", "The agent harness, concern by concern, on AWS services.")],
        "across": [("Databricks cost calculator (AWS prices)", "/learn/data-systems/platform/cost/calculator/", "Uses AWS EC2, S3 and network list prices.")],
    }, []),
    "azure": ("Azure and Microsoft Fabric", "Microsoft's cloud: OneLake and Fabric for data, Azure AI Foundry for AI, Azure Databricks.", {
        "ai": [("Claims assistant on Azure", "https://github.com/dataagentsai/claims-fnol-azure", "Open-source code: an insurance claims assistant built on Azure.")],
    }, [("AI-103 Azure AI Engineer, free prep", "/certifications/azure-ai-engineer/")]),
    "gcp": ("Google Cloud", "Google's cloud: BigQuery, Dataflow, Dataplex and Vertex AI.", {}, []),
    "open": ("Open source", "The same platform built from open-source parts: Spark, Delta or Iceberg, dbt, Airflow or Dagster, OpenMetadata.", {
        "de": [("Shift left: fail fast on data code", "/learn/shift-left/", "Open checks for PySpark, SQL and Databricks code.")],
        "across": [("Open-source code from this site", "/assets/", "Reference Agent, AgentTwin, Eval Harness Framework and more.")],
    }, []),
    "anthropic": ("Claude (Anthropic)", "The model platform the AI capability builds on: the Claude API, tools, agents and Claude Code.", {
        "ai": [("Claude API Simulator", "/learn/llm-api-sim/", "See what goes in and out of the Claude API, step by step."),
               ("Agent Harness", "/learn/agent-harness/", "Everything around the model that makes an agent safe and useful."),
               ("Agent Harness Simulator", "/learn/agent-harness-sim/", "Run an agent through the harness and watch each concern act.")],
    }, [("Claude Certified Architect (CCA-F)", "/certifications/claude-certified-architect/CCA-F/"),
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


def headings(pid):
    return ["ai", "certs"] if pid == "anthropic" else [k for k, _ in SECTIONS]


def hub(pid):
    name, lede, pages, certs = PLATFORMS[pid]
    titles = dict(SECTIONS)
    secs = []
    for key in headings(pid):
        if key == "paths":
            paths = "".join(f'<a href="/paths/{d["id"]}/{pid}/">{E(d["name"])}</a>' for d in DISCIPLINES if pid in d["platforms"])
            html = f'<p>Crawl, walk and run for each role, on {E(name)}.</p><div class="ideas">{paths}</div>'
        elif key == "certs":
            html = ('<ul>' + "".join(f'<li><a href="{h}">{E(n)}</a></li>' for n, h in certs) + "</ul>") if certs else '<p class="note">No free prep on this site yet. See <a href="/certifications/">all certifications</a>.</p>'
        else:
            if key == "de" and pid in COLS:
                rows = [(r[0], r[COLS[pid]]) for r in med.PRODUCTS]
            else:
                rows = [(job, m[pid]) for job, m in MAPS.get(key, []) if pid in m]
            html = ""
            if rows:
                html += '<div class="tw"><table class="t"><tr><th>Job</th><th>Product on ' + E(name) + "</th></tr>" + "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td></tr>" for a, b in rows) + "</table></div>"
            pg = [x for x in pages.get(key, []) if exists(x[1])]
            html += cards(pg) if pg else '<p class="note">No pages for this on ' + E(name) + ' yet; the concepts apply as they are.</p>'
        secs.append((key, titles[key], f'<p class="eyebrow">{E(name)}</p><h2>{E(titles[key])}</h2>{html}'))
    toc = "".join(f'<li><a href="#{sid}">{E(t)}</a></li>' for sid, t, _ in secs)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/platforms/">On your cloud</a> › {E(name)}</p>
<p class="eyebrow" style="margin-top:22px">On your cloud · the same headings as the concepts</p>
<h1>{E(name)}</h1>
<p class="lede">{E(lede)} The headings match the concepts tree: learn the idea in the <a href="/learn/data-systems/">concepts</a>, then see here which {E(name)} product does each job. Product names change often; check the current docs before you build.</p>
<nav class="toc"><b>On this page</b><ol>{toc}</ol></nav>
""" + "".join(f'<section id="{sid}">{h}</section>' for sid, _t, h in secs)
    url = f"{SITE}/platforms/{pid}/"
    desc = f"{name} for data and AI: data systems, data engineering, BI, ML, AI and cross-cutting jobs mapped to {name} products, with guides, learning paths and certification prep."
    return wb.page(name, desc, url, body, ds.CSS + ds.ld(name, desc, url, [("On your cloud", "/platforms/"), (name, f"/platforms/{pid}/")]))


def index():
    items = "".join(f'<div class="card"><h3><a href="/platforms/{p}/">{E(PLATFORMS[p][0])}</a></h3><p class="one">{E(PLATFORMS[p][1])}</p></div>' for p in ORDER)
    body = f"""<p class="crumbs"><a href="/">Home</a> › On your cloud</p>
<p class="eyebrow" style="margin-top:22px">With which product</p>
<h1>On your cloud</h1>
<p class="lede">The site has one tree of ideas, shown twice. <b>Concepts</b> explain data systems and the data and AI platform (data engineering, BI, ML, AI and what cuts across them) without naming products. <b>On your cloud</b> shows the same headings for each platform, with the product that does each job. Learn the idea once; the cloud is a binding.</p>
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
