"""Databricks permissions, end to end: one page at /learn/databricks-permissions/.

    python3 _guides/databricks_permissions.py      (then python3 _site/nav.py and python3 _site/seo.py)

Body text lives in _guides/databricks_permissions/body.html (s1..s13); the drawings are built here.
Facts were read from docs.databricks.com/aws/en (Unity Catalog privileges and ownership, admin roles, workspace ACLs, entitlements,
compute access modes, row filters and masks, ABAC, identities, service principals, storage credentials, audit logs, workspace binding)
on 21 Nov 2026. Several pages were only partly readable; everything the docs did not state is listed in the "Not confirmed" callout (s13).
SQL marked "sketch" was not run against a workspace.
"""
import json
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "_paths"))
import bi_choice as B  # noqa: E402  (drawing kit + CSS)
import components as C  # noqa: E402

wb = C.wb
SITE = wb.SITE
SLUG = "databricks-permissions"
BASE = f"/learn/{SLUG}/"
DATE = "2026-11-21"
BODY = Path(__file__).parent / "databricks_permissions" / "body.html"
bx, ar, svg, fig, t = B.bx, B.ar, B.svg, B.fig, B.t

TITLE = "Databricks permissions: who can do what, from account admin to a single table"
DESC = ("A plain guide to Databricks permissions: the five layers (identity, entitlements, workspace object ACLs, Unity Catalog privileges, storage), "
        "admin roles, the USE CATALOG + USE SCHEMA + SELECT rule, ownership vs MANAGE, row filters, column masks and ABAC, service principals, "
        "workspace binding and audit, with ready-made grants for common roles, mistakes to avoid and a verdict for each choice.")

QA = [
    ("What do I need to read a table in Unity Catalog?", "USE CATALOG on the catalog, USE SCHEMA on the schema, and SELECT on the table, or SELECT on the schema or catalog above it, which inherits downward. SELECT alone is not enough."),
    ("What is the difference between an owner and MANAGE?", "An object has exactly one owner, who has every capability on it. MANAGE can be given to several principals and lets them manage privileges, transfer ownership, rename and drop, but it does not give them data access. A MANAGE holder can still grant themselves SELECT. ALL PRIVILEGES does not include MANAGE."),
    ("Is there a DENY statement?", "I found no SQL DENY statement in the docs. Denial exists through ABAC DENY policies, which are labelled Beta."),
    ("Should I grant permissions to users or groups?", "Groups. Account groups can be granted Unity Catalog data access and workspace permissions, and a person who changes team only has to move between groups. Service principals, not people, should own and run production jobs."),
]

RELATED = [
    ("Row-level security with metric views", "/learn/metric-views/security/"),
    ("Databricks compute and cost", "/learn/databricks-compute/"),
    ("Who maintains your tables", "/learn/table-maintenance/"),
    ("Databricks materialized views", "/learn/materialized-views/"),
    ("Medallion architecture", "/learn/medallion-architecture/"),
    ("AI governance", "/learn/ai-governance/"),
]


def d_layers():
    steps = [("Who are you?", ["user, group,", "service principal"], "b"),
             ("May you use", ["this feature here?", "entitlements"], "g"),
             ("May you use this", ["workspace object?", "ACLs: notebook, job,", "cluster, warehouse"], "y"),
             ("May you touch", ["this data?", "Unity Catalog grants,", "filters and masks"], "l"),
             ("May the bytes", ["be read?", "storage credential,", "external location"], "r")]
    i = ""
    for k, (h, lines, f) in enumerate(steps):
        x = 10 + k * 198
        i += bx(x, 30, 176, 120, [h] + lines, f, 15)
        if k < 4:
            i += ar(x + 178, 90, x + 196, 90)
    i += t(500, 190, "Every layer has to say yes. A grant in one layer cannot make up for a no in another.", 16, "middle")
    i += t(500, 216, "Example: SELECT on a table still fails without USE CATALOG, and a notebook you can edit still cannot read data you were never granted.", 14, "middle")
    return svg(1000, 235, "Five layers of Databricks permissions, left to right: identity (who you are), entitlements (which features you may use in a workspace), workspace object ACLs (notebooks, jobs, compute, warehouses), Unity Catalog grants plus row filters and column masks (data), and storage credentials and external locations (the files). Every layer must allow the action.", i)


def d_hierarchy():
    i = bx(10, 10, 300, 52, ["Metastore", "one per region, attached to workspaces"], "w", 15)
    i += bx(10, 90, 300, 52, ["Catalog", "needs USE CATALOG"], "b", 15) + ar(160, 64, 160, 88)
    i += bx(10, 170, 300, 52, ["Schema", "needs USE SCHEMA"], "g", 15) + ar(160, 144, 160, 168)
    i += bx(10, 250, 300, 52, ["Table, view, volume, function", "needs SELECT (or another privilege)"], "y", 14) + ar(160, 224, 160, 248)
    i += bx(350, 90, 290, 212, ["Reading a table needs all three:", "", "USE CATALOG on the catalog", "USE SCHEMA on the schema", "SELECT on the table,", "or on the schema or catalog above,", "which flows down"], "y", 15)
    i += ar(312, 116, 348, 116) + ar(312, 196, 348, 196) + ar(312, 276, 348, 276)
    i += bx(690, 10, 300, 52, ["Storage credential", "a cloud role or key"], "r", 14)
    i += bx(690, 90, 300, 52, ["External location", "a path plus a credential"], "r", 14) + ar(840, 64, 840, 88)
    i += bx(690, 170, 300, 60, ["Also under the metastore:", "connections, shares,", "recipients, clean rooms"], "w", 13)
    i += t(840, 275, "Metastore-level privileges", 14, "middle") + t(840, 295, "do not flow down to data.", 14, "middle")
    return svg(1000, 320, "The Unity Catalog hierarchy: a metastore holds catalogs, catalogs hold schemas, and schemas hold tables, views, volumes and functions. Reading a table needs USE CATALOG, USE SCHEMA and SELECT, and a privilege granted on a catalog or schema flows down to everything below it. Storage credentials and external locations sit directly under the metastore, as do connections, shares and recipients.", i)


def render():
    url = f"{SITE}{BASE}"
    rel = " · ".join(f'<a href="{u}">{E(n)}</a>' for n, u in RELATED)
    body = f"""<div class="bi"><p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › Databricks permissions</p>
<p class="eyebrow" style="margin-top:22px">Databricks · governance and security</p>
<h1>{E(TITLE)}</h1><p class="lede">{E(DESC)}</p>
{BODY.read_text().replace("{{LAYERS}}", fig(d_layers(), "Five checks, one after another. All must pass.")).replace("{{HIERARCHY}}", fig(d_hierarchy(), "Grants flow down the left column. The right column is the rule for reading a table."))}
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(QA)}</section>
<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2><p>Related on this site: {rel}</p><p><a href="/data-engineering/">All data engineering</a> · <a href="/platforms/databricks/">Databricks on this site</a></p></section></div>"""
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": TITLE, "description": DESC, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in QA]}]
    head = B.CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(TITLE, DESC, url, body, head)


def build_all():
    return {f"learn/{SLUG}/index.html": render()}


def main():
    for rel, html in build_all().items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html)
        print("databricks permissions ->", path)


if __name__ == "__main__":
    main()
