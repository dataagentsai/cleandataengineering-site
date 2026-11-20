"""AWS-native Iceberg lakehouse vs Databricks: one wide comparison page at /learn/databricks-vs-aws-lakehouse/.

    python3 _guides/dbx_vs_aws.py      (then python3 _site/nav.py and python3 _site/seo.py)

Body text lives in _guides/dbx_vs_aws/body.html (sections s1..s14); this file holds the title,
FAQ, related links and the page shell. Reuses the CSS and shell of the Databricks compute guide.
Limitations (s13) were checked against vendor docs on DATE; prices are not quoted.
"""
import json
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "_paths"))
import components as C  # noqa: E402
import databricks_compute as D  # noqa: E402

wb = C.wb
SITE = wb.SITE
SLUG = "databricks-vs-aws-lakehouse"
BASE = f"/learn/{SLUG}/"
DATE = "2026-11-21"
BODY = Path(__file__).parent / "dbx_vs_aws" / "body.html"

TITLE = "AWS-native Iceberg vs Databricks: a like-for-like lakehouse comparison with limitations"
SHORT = "S3 Tables + EMR + Glue vs Unity Catalog + Delta + UniForm"
DESC = ("S3 Tables, Glue and Lake Formation with EMR or Glue Spark, against Unity Catalog with Delta, UniForm, Photon and Predictive Optimization: "
        "format, compute, upkeep, pipelines, Auto CDC and SCD2, Power BI, governance, lineage, orchestration, cost and hidden cost, "
        "with a scorecard and the current documented limitations.")

QA = [
    ("Does Databricks or AWS-native cost less?", "Per compute hour, AWS-native on spot and Graviton is usually cheaper. Databricks adds a DBU premium but can save engineering time and run faster with Photon. Measure the same pipeline on both and compare monthly cost, including storage requests, network and idle time."),
    ("Can Athena or Redshift read Databricks tables?", "Yes, through UniForm, which exposes Delta tables as Iceberg for reading. It is read-only, needs column mapping, and has limits such as deletion vectors on Iceberg v2 readers. Check the current UniForm page."),
    ("Which is better for Power BI?", "Databricks, because Power BI has a native connector with DirectQuery and passes user identity. Iceberg on S3 has no native Power BI connector, so you go through Athena, Redshift or a Trino service. The metric view path in Power BI is the least settled part, so pilot it."),
    ("Is compression a reason to choose one?", "No. Both write Parquet and you can choose the same codec. File size and table layout matter far more."),
]

RELATED = [
    ("Iceberg lakehouse: who owns the catalog?", "/learn/iceberg-lakehouse-aws-databricks/"),
    ("Databricks compute and cost", "/learn/databricks-compute/"),
    ("Delta vs Iceberg", "/learn/delta-vs-iceberg/"),
    ("Who maintains your tables", "/learn/table-maintenance/"),
    ("SCD2: AUTO CDC or own PySpark?", "/learn/scd2-auto-cdc-vs-pyspark/"),
    ("Power BI vs Databricks AI/BI", "/learn/power-bi-vs-databricks-ai-bi/"),
    ("Metric views", "/learn/metric-views/"),
    ("AWS data services catalog", "/learn/aws-data-services/"),
]


def render():
    url = f"{SITE}{BASE}"
    rel = " · ".join(f'<a href="{u}">{E(n)}</a>' for n, u in RELATED)
    body = f"""{D.DEFS}<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › AWS-native vs Databricks lakehouse</p>
<p class="eyebrow" style="margin-top:22px">Platform comparison · data engineering</p>
<h1>{E(TITLE)}</h1><p class="lede">{E(DESC)}</p>
<p class="verify">Prices, defaults, limits and preview status change often. No prices are quoted here. Limitations were checked against vendor documentation on {DATE}; confirm them on your runtime and region.</p>
{BODY.read_text()}
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(QA)}</section>
<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2><p>Related on this site: {rel}</p><p><a href="/data-engineering/">All data engineering</a> · <a href="/platforms/databricks/">Databricks on this site</a></p></section>"""
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": TITLE, "description": DESC, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in QA]}]
    head = D.CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(TITLE, DESC, url, body, head)


def build_all():
    return {f"learn/{SLUG}/index.html": render()}


def main():
    for rel, html in build_all().items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html)
        print("dbx vs aws ->", path)


if __name__ == "__main__":
    main()
