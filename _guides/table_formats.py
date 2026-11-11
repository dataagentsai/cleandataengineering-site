"""Delta Lake vs Apache Iceberg, and what differs on Databricks: one page at /learn/delta-vs-iceberg/.

    python3 _guides/table_formats.py      (then python3 _site/nav.py and python3 _site/seo.py)

Teach first (what a table format is, drawn), then the formats side by side, then the Databricks
feature matrix (managed Delta, Delta with Iceberg reads, managed Iceberg, foreign Iceberg): change
data feed, streaming, pipelines, lineage, clustering, masks. Then which to pick per binding.
Feature status checked against Databricks docs in Nov 2026; preview items are marked "check".
"""
import json
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "_paths"))
import components as C  # noqa: E402

wb = C.wb
SITE = wb.SITE
URL_PATH = "/learn/delta-vs-iceberg/"
DATE = "2026-11-11"
TITLE = "Delta Lake vs Apache Iceberg, and what differs on Databricks"
DESC = ("Delta Lake and Iceberg explained simply, side by side, then the Databricks features that differ: "
        "change data feed, streaming, pipelines, lineage, liquid clustering, masks, UniForm. Which to pick on AWS.")

CSS = C.CSS + """<style>
  .tf .fig { border:var(--line); border-radius:var(--wob); padding:12px 14px; margin:16px 0; background:#fff; overflow-x:auto; }
  .tf .fig svg { width:100%; min-width:640px; height:auto; display:block; } .tf .fig text { font-family:var(--hand); fill:#111; }
  .tf .fig p { font-size:13.5px; color:var(--muted); margin:6px 0 0; }
  .tf .box { border:var(--line); border-radius:var(--wob); padding:10px 16px; margin:14px 0; background:var(--butter-wash); }
  .tf td.y { background:var(--mint-wash); } .tf td.n { background:var(--rose-wash); } .tf td.p { background:var(--butter-wash); }
  .tf table.t td { font-size:14px; }
</style>"""


def drawing():
    return """<svg viewBox="0 0 1000 330" role="img" aria-label="Delta Lake and Iceberg side by side: the same Parquet data files, with different metadata on top. Delta keeps an ordered log of JSON commits with checkpoints; Iceberg keeps a metadata file that points to a manifest list, manifests, then data files. A catalog points at each table.">
<defs><marker id="tfa" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#111"/></marker></defs>
<g fill="#fff" stroke="#111" stroke-width="1.5">
<rect x="10" y="10" width="470" height="310" rx="12" stroke-dasharray="2 4"/><rect x="520" y="10" width="470" height="310" rx="12" stroke-dasharray="2 4"/>
<rect x="150" y="40" width="190" height="40" rx="8"/>
<rect x="60" y="110" width="370" height="70" rx="8" fill="#eef3fb"/>
<rect x="660" y="40" width="190" height="40" rx="8"/>
<rect x="660" y="100" width="190" height="34" rx="8" fill="#eef3fb"/><rect x="660" y="150" width="190" height="34" rx="8" fill="#eef3fb"/><rect x="620" y="200" width="270" height="34" rx="8" fill="#eef3fb"/>
<rect x="40" y="250" width="410" height="52" rx="8" fill="#eaf6ef"/><rect x="550" y="250" width="410" height="52" rx="8" fill="#eaf6ef"/>
</g>
<g font-size="16">
<text x="24" y="32" font-size="20">Delta Lake</text><text x="534" y="32" font-size="20">Apache Iceberg</text>
<text x="168" y="66">Catalog (Unity Catalog)</text>
<text x="72" y="134">_delta_log/  00000.json  00001.json  00002.json …</text>
<text x="72" y="156" font-size="14">one file per commit, in order; a checkpoint every so often</text>
<text x="72" y="172" font-size="14">the newest log file is the truth</text>
<text x="678" y="66">Catalog (REST, UC, Glue)</text>
<text x="672" y="122" font-size="14">metadata.json: schema, snapshots</text><text x="672" y="172" font-size="14">manifest list (one snapshot)</text>
<text x="632" y="222" font-size="14">manifests: which data files, with column stats</text>
<text x="54" y="274">Parquet data files (+ deletion vectors)</text><text x="54" y="294" font-size="13.5">the same kind of files in both formats</text>
<text x="564" y="274">Parquet data files (+ delete files or deletion vectors)</text><text x="564" y="294" font-size="13.5">the catalog's pointer to metadata.json is the truth</text>
</g>
<g stroke="#111" stroke-width="1.4" fill="none" marker-end="url(#tfa)">
<path d="M245,80 L245,108"/><path d="M245,180 L245,248"/>
<path d="M755,80 L755,98"/><path d="M755,134 L755,148"/><path d="M755,184 L755,198"/><path d="M755,234 L755,248"/>
</g>
</svg>"""


SPEC = [
    ("How the table is described", "An ordered log of commits (JSON) plus checkpoints, next to the data", "A tree: metadata file, manifest list per snapshot, manifests, data files"),
    ("What makes a commit atomic", "Writing the next log file; Unity Catalog can coordinate commits (catalog-managed commits)", "The catalog swaps its pointer to the new metadata file, so a catalog is required"),
    ("Data files", "Parquet", "Parquet (also ORC, Avro)"),
    ("Partitioning", "Liquid clustering (recommended) or classic partitions", "Hidden partitioning with transforms (day, bucket) and partition evolution; on Databricks, liquid clustering"),
    ("Renaming and dropping columns", "Needs column mapping turned on", "Built in: every column has an id"),
    ("Deletes and updates", "Deletion vectors mark deleted rows; files rewritten later", "v2: position or equality delete files; v3: deletion vectors"),
    ("Time travel", "VERSION AS OF, TIMESTAMP AS OF; shallow and deep clones", "Snapshots, plus named branches and tags"),
    ("Row-level change tracking", "Change data feed; row tracking (row ids)", "v3: row lineage (a permanent id per row); no change feed in the spec"),
    ("Semi-structured data", "VARIANT", "VARIANT (v3)"),
    ("Streaming", "First-class source and sink for Spark Structured Streaming and Lakeflow pipelines", "Strong with Flink; Spark reads new appends incrementally"),
    ("Who reads and writes it", "Databricks, Microsoft Fabric (OneLake), Spark, Trino, DuckDB, delta-rs; others through Iceberg reads (UniForm)", "Snowflake, AWS (Athena, Glue, EMR, Redshift, S3 Tables), BigQuery, Trino, Flink, Dremio, DuckDB, Databricks"),
    ("Housekeeping", "OPTIMIZE, VACUUM, ANALYZE (predictive optimization on Databricks)", "Rewrite data files, expire snapshots, remove orphan files (the catalog or predictive optimization runs them)"),
]

# feature, managed Delta, Delta with Iceberg reads (UniForm), managed Iceberg in Unity Catalog, foreign Iceberg (Glue, Snowflake...)
DBX = [
    ("Status on Databricks", ("y", "Generally available"), ("y", "Generally available (Runtime 14.3+)"), ("p", "Public Preview in the docs (Runtime 16.4+); announced as GA. Check before production"), ("y", "Read: generally available")),
    ("Who can write", ("y", "Databricks and Delta writers"), ("p", "Databricks writes; Iceberg engines read only"), ("y", "Databricks and any Iceberg engine through the Unity Catalog REST catalog"), ("n", "Its own catalog's engines; Databricks reads")),
    ("Change data feed (table_changes, readChangeFeed)", ("y", "Yes: delta.enableChangeDataFeed = true, or the automatic feed from row tracking"), ("p", "Yes for Databricks readers; Iceberg readers cannot see it"), ("p", "Only on Iceberg v3 (automatic feed from row lineage, Runtime 18+), only for Databricks readers"), ("n", "No")),
    ("Streaming read with Structured Streaming", ("y", "Yes"), ("y", "Yes, as Delta"), ("p", "Through the automatic change feed on v3; check"), ("n", "No (older docs: not supported)")),
    ("Lakeflow streaming tables and materialized views", ("y", "They are Delta tables"), ("n", "Iceberg reads cannot be turned on for them; Compatibility Mode (preview) writes a read-only copy"), ("n", "Pipelines write Delta"), ("n", "No")),
    ("Data lineage in Unity Catalog", ("y", "Yes, for work run on Databricks"), ("p", "Databricks work yes; reads by outside Iceberg engines are not recorded"), ("p", "Databricks work yes; writes by outside engines through the REST catalog are not recorded"), ("p", "Reads on Databricks only")),
    ("Row ids (row tracking, row lineage)", ("y", "Row tracking, a table property"), ("y", "Row tracking"), ("y", "Always on for v3"), ("p", "Depends on the source")),
    ("Liquid clustering", ("y", "Yes"), ("y", "Yes"), ("p", "Yes; no expression transforms (years(), bucket()) through Databricks SQL; partition evolution only from outside engines"), ("n", "Owned by the other catalog")),
    ("Predictive optimization", ("y", "Yes"), ("y", "Yes"), ("y", "Required: tables can only be created with it on"), ("n", "The other catalog maintains them")),
    ("Deletion vectors", ("y", "Yes"), ("p", "Not with Iceberg v2 reads; fine with v3"), ("y", "On by default for v3"), ("p", "Depends on the source")),
    ("Row filters and column masks", ("y", "Yes"), ("y", "Yes"), ("n", "Not supported"), ("n", "No")),
    ("Primary and foreign keys (informational)", ("y", "Yes"), ("y", "Yes"), ("n", "Not supported"), ("n", "No")),
    ("Time travel", ("y", "Yes"), ("y", "Yes (Delta side)"), ("y", "Yes (snapshots)"), ("y", "Read")),
    ("Upgrade to v3 / new features", ("y", "Table features can be added"), ("y", "Can be downgraded"), ("p", "Upgrading to v3 is one way"), ("p", "Source decides")),
]

LINEAGE = [
    ("Data lineage", "Which job, notebook or query read which tables and columns to produce which table. Unity Catalog records it for work run on Databricks compute, for any format.", "Impact analysis, audit, 'where did this number come from'"),
    ("Row lineage (Iceberg v3) or row tracking (Delta)", "A permanent id and a version number on every row, kept by the table itself.", "Cheap change feeds, incremental materialized views, matching a row across rewrites"),
]

PICK = [
    ("AWS + Databricks (this site's default)", "Managed Delta for bronze, silver and gold. Turn on Iceberg reads (UniForm) only for the gold tables that Athena, Redshift or Snowflake must read.", "Pursue"),
    ("AWS + Databricks, another engine must write the same table", "Managed Iceberg in Unity Catalog, written through its REST catalog. Mind: no row filters or masks, no keys, change feed only on v3 and only for Databricks readers.", "Pursue only where needed, after checking it is GA"),
    ("Tables owned by Glue, S3 Tables or Snowflake", "Foreign Iceberg: read in place through catalog federation; do not copy.", "Pursue"),
    ("AWS only (no Databricks)", "Iceberg in S3 Tables, with Athena, Glue and Redshift.", "Pursue; Delta here would be a second-class citizen"),
    ("Azure with Fabric", "Delta: OneLake is Delta-native.", "Pursue"),
    ("Streaming lane on Databricks", "Keep streaming tables and materialized views Delta; Iceberg reads cannot be turned on for them, and the change feed drives the gold window recompute.", "Pursue Delta"),
    ("Convert everything to Iceberg to be 'open'", "Delta is open source too, and UniForm already serves Iceberg readers. Converting adds risk and loses masks and keys today.", "Drop"),
]

QA = [
    ("Is Delta Lake or Iceberg better?", "Neither in general. Both put the same Parquet files under a different contents page. Delta is the native format on Databricks and Fabric; Iceberg is the native format on AWS analytics services and Snowflake. On Databricks, keep Delta and turn on Iceberg reads where other engines need it."),
    ("Does change data feed work on Iceberg tables in Databricks?", "Only on Iceberg v3 managed tables, where Databricks computes the feed from row lineage, and only Databricks readers can use it. Delta tables have it with delta.enableChangeDataFeed = true, or automatically with row tracking."),
    ("Can Lakeflow streaming tables be Iceberg?", "No. Pipelines write Delta, and Iceberg reads (UniForm) cannot be turned on for streaming tables or materialized views. Compatibility Mode, in preview, can write a read-only copy for other engines."),
    ("Does Unity Catalog lineage work for Iceberg tables?", "For work run on Databricks, yes. Reads and writes by outside engines through the Iceberg REST catalog are not recorded, so lineage has gaps when other engines write."),
    ("What is the difference between data lineage and row lineage?", "Data lineage says which job made which table from which tables. Row lineage (Iceberg v3) or row tracking (Delta) gives every row a permanent id inside the table, used for change feeds and incremental updates."),
]

SOURCES = [
    ("Apache Iceberg in Databricks", "https://docs.databricks.com/aws/en/iceberg"),
    ("Iceberg v3 features on Databricks", "https://docs.databricks.com/aws/en/iceberg/iceberg-v3"),
    ("Change data feed on Databricks", "https://docs.databricks.com/aws/en/tables/features/change-data-feed"),
    ("Read Delta tables with Iceberg clients (UniForm)", "https://docs.databricks.com/aws/en/delta/uniform"),
    ("Compatibility Mode", "https://docs.databricks.com/aws/en/external-access/compatibility-mode"),
    ("Unity Catalog managed tables", "https://docs.databricks.com/aws/tables/managed"),
]


def cell(c):
    k, t = c
    return f'<td class="{k}">{E(t)}</td>'


def page():
    url = f"{SITE}{URL_PATH}"
    spec = C.table(["", "Delta Lake", "Apache Iceberg"], SPEC)
    dbx = ('<div class="tw"><table class="t"><tr><th>Feature</th><th>Managed Delta</th><th>Delta with Iceberg reads (UniForm)</th><th>Managed Iceberg in Unity Catalog</th><th>Foreign Iceberg (Glue, Snowflake, Hive)</th></tr>'
           + "".join(f"<tr><td><b>{E(f)}</b></td>{cell(a)}{cell(b)}{cell(c)}{cell(d)}</tr>" for f, a, b, c, d in DBX) + "</table></div>")
    lin = C.table(["Kind", "What it is", "Used for"], LINEAGE)
    pick = ('<div class="tw"><table class="t"><tr><th>Situation</th><th>Choice</th><th>Verdict</th></tr>'
            + "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td><b>{E(c)}</b></td></tr>" for a, b, c in PICK) + "</table></div>")
    src = "".join(f'<li><a href="{u}">{E(n)}</a></li>' for n, u in SOURCES)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/data-engineering/">Data engineering</a> › Delta vs Iceberg</p>
<p class="eyebrow" style="margin-top:22px">Data engineering · free guide · one page</p>
<h1>{E(TITLE)}</h1>
<p class="lede">Delta Lake and Apache Iceberg both turn a folder of Parquet files into a table you can update safely. This page shows how each does it, then the Databricks features that behave differently for each (change data feed, streaming, pipelines, lineage, clustering, masks), and which to pick on AWS.</p>
<div class="tf">
<section id="plain"><p class="eyebrow">In plain words</p><h2>A contents page over the same files</h2>
<p>A data lake on its own is a pile of Parquet files. To know which files make up the table <i>right now</i>, which ones were replaced, and what the columns are, you need a contents page. That contents page is the <b>table format</b>. It is what makes updates all-or-nothing, lets two writers work without corrupting each other, and lets you read the table as it was last Tuesday.</p>
<p>Delta keeps its contents page as an ordered diary of changes next to the data. Iceberg keeps it as a tree of metadata files, and a catalog holds the pointer to the current top of the tree. The data files underneath are the same kind of Parquet, which is why Databricks can write Iceberg metadata for a Delta table (UniForm) without copying any data.</p>
<div class="fig">{drawing()}<p>Same Parquet files, two different contents pages. The catalog matters more for Iceberg: its pointer decides which version is current.</p></div></section>

<section id="side-by-side"><p class="eyebrow">The formats</p><h2>Side by side</h2>{spec}</section>

<section id="databricks"><p class="eyebrow">On Databricks</p><h2>Which Databricks features differ by format</h2>
<p>Databricks offers four kinds of table. Green works, yellow works with a limit, rose does not. Checked against the Databricks docs in November 2026; Iceberg support changes quickly, so check items marked "check" before you rely on them.</p>
{dbx}
<div class="box"><b>In short:</b> everything works on managed Delta. Iceberg reads (UniForm) add outside readers without giving anything up, except on streaming tables and materialized views. Managed Iceberg lets other engines write, but today gives up row filters, column masks and keys, and has a change feed only on v3 and only for Databricks readers.</div></section>

<section id="cdf"><p class="eyebrow">Change data feed</p><h2>Change data feed (the "enable CDC" switch)</h2>
<p>A change data feed lets a reader ask "what changed in this table since version 12?" and get the inserted, updated and deleted rows, instead of re-reading the whole table. Gold builds use it to find which hours changed.</p>
{C.code('''-- Delta: turn it on per table
ALTER TABLE silver.press_readings SET TBLPROPERTIES (delta.enableChangeDataFeed = true);

-- Read the changes since version 12 (batch)
SELECT * FROM table_changes('silver.press_readings', 12);

-- Or as a stream
spark.readStream.option("readChangeFeed", "true").option("startingVersion", 12).table("silver.press_readings")''', "The same table_changes and readChangeFeed calls work on managed Iceberg v3 tables, where Databricks computes the feed from row lineage.")}
<p>Outside Databricks, Iceberg has no change feed in its spec; Spark's Iceberg library can build a changelog view between two snapshots, and Flink reads Iceberg changes natively.</p></section>

<section id="lineage"><p class="eyebrow">Lineage</p><h2>Two different things called lineage</h2>{lin}
<p>Unity Catalog lineage is format-neutral but only sees work done on Databricks compute. If Trino or Flink writes a managed Iceberg table through the REST catalog, that write is missing from the lineage graph; record it with OpenLineage from the other engine if you need the full picture.</p></section>

<section id="pick"><p class="eyebrow">Choosing</p><h2>Which to pick, by platform</h2>{pick}</section>

<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(QA)}</section>
<section id="sources"><p class="eyebrow">Sources</p><h2>Checked against</h2><ul>{src}</ul></section>
<section id="next"><p class="eyebrow">Related</p><h2>Where it connects</h2>
<p><a href="/learn/medallion-architecture/">Medallion architecture</a> · <a href="/learn/streaming/">Streaming on AWS and Databricks</a> · <a href="/learn/data-platform-architecture/aws-databricks/">Data platform on AWS + Databricks</a> · <a href="/learn/data-platform-sim/delta/">Delta Lake internals, recorded</a> · <a href="/learn/table-maintenance/">Who maintains your tables</a> · <a href="/data-engineering/">All data engineering</a></p></section>
</div>"""
    crumbs = [("Data engineering", f"{SITE}/data-engineering/"), ("Delta vs Iceberg", url)]
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": TITLE, "description": DESC, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in QA]}]
    head = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(TITLE, DESC, url, body, head)


def main():
    out = ROOT / "learn" / "delta-vs-iceberg"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("delta vs iceberg ->", out / "index.html")


if __name__ == "__main__":
    main()
