"""Who maintains your tables: one page at /learn/table-maintenance/.

    python3 _guides/table_maintenance.py      (then python3 _site/nav.py and python3 _site/seo.py)

Answers the question "let AWS maintain Iceberg, use Databricks only for compute, like a Snowflake
warehouse?". Teach first: storage and compute are already split; every table has chores; who does
them depends on who owns the catalog pointer. Then the three kinds of table (UC managed, UC external,
AWS-managed Iceberg in Glue or S3 Tables), how Delta and Iceberg commit and clean up inside, what the
AWS wrapper adds, and the setup we recommend with verdicts. Reuses the Delta vs Iceberg drawing.
"""
import json
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "_paths"))
import components as C  # noqa: E402
import table_formats as TF  # noqa: E402

wb = C.wb
SITE = wb.SITE
URL_PATH = "/learn/table-maintenance/"
DATE = "2026-11-11"
TITLE = "Who maintains your tables? Managed, external and AWS-managed Iceberg"
DESC = ("Who runs compaction, VACUUM and snapshot expiry for Unity Catalog managed tables, external tables, "
        "Glue Iceberg and S3 Tables; whether 'AWS maintains Iceberg, Databricks only computes' is the right split; "
        "how Delta and Iceberg commit and clean up inside.")

CSS = TF.CSS + """<style>
  .tf .two { display:grid; grid-template-columns:1fr 1fr; gap:14px; } @media (max-width:760px) { .tf .two { grid-template-columns:1fr; } }
  .tf .card { border:var(--line); border-radius:var(--wob); padding:10px 16px; background:#fff; }
  .tf .card h3 { margin:4px 0 6px; }
</style>"""

ARROW = '<defs><marker id="tma" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#111"/></marker></defs>'
BLUE, MINT, BUTTER, ROSE, LAV = "#eef3fb", "#eaf6ef", "#fff4d6", "#fbeef3", "#efeaf8"


def _bucket(x, y, w, label, sub):
    """A cartoon storage bucket: a tub with a rim."""
    return (f'<path d="M{x},{y} L{x + 18},{y + 86} L{x + w - 18},{y + 86} L{x + w},{y} Z" fill="{MINT}" stroke="#111" stroke-width="1.5"/>'
            f'<ellipse cx="{x + w / 2}" cy="{y}" rx="{w / 2}" ry="10" fill="#fff" stroke="#111" stroke-width="1.5"/>'
            f'<text x="{x + w / 2}" y="{y + 42}" text-anchor="middle" font-size="16">{label}</text>'
            f'<text x="{x + w / 2}" y="{y + 64}" text-anchor="middle" font-size="13.5">{sub}</text>')


def _engine(x, y, label):
    """A small compute box with a power dot."""
    return (f'<rect x="{x}" y="{y}" width="130" height="46" rx="8" fill="{BLUE}" stroke="#111" stroke-width="1.5"/>'
            f'<circle cx="{x + 16}" cy="{y + 23}" r="5" fill="#fff" stroke="#111" stroke-width="1.3"/>'
            f'<text x="{x + 74}" y="{y + 29}" text-anchor="middle" font-size="14.5">{label}</text>')


def drawing_split():
    d = f'<svg viewBox="0 0 1000 330" role="img" aria-label="Two halves. Left, Snowflake: three virtual warehouses above one storage tub labelled Snowflake-managed storage. Right, Databricks: a SQL warehouse, a job cluster and a notebook cluster above one tub labelled your S3 bucket. In both, compute boxes start and stop and all read the same storage.">{ARROW}'
    d += '<g fill="none" stroke="#111" stroke-width="1.5"><rect x="10" y="10" width="470" height="310" rx="12" stroke-dasharray="2 4"/><rect x="520" y="10" width="470" height="310" rx="12" stroke-dasharray="2 4"/></g>'
    d += '<text x="24" y="36" font-size="20">Snowflake</text><text x="534" y="36" font-size="20">Databricks on AWS</text>'
    for i, lab in enumerate(["warehouse S", "warehouse M", "warehouse L"]):
        d += _engine(30 + i * 148, 60, lab)
    for i, lab in enumerate(["SQL warehouse", "job cluster", "notebook"]):
        d += _engine(540 + i * 148, 60, lab)
    d += '<text x="466" y="36" text-anchor="end" font-size="13.5">compute: start, query, stop</text>'
    d += '<text x="976" y="36" text-anchor="end" font-size="13.5">compute: start, query, stop</text>'
    d += '<g stroke="#111" stroke-width="1.4" fill="none" marker-end="url(#tma)">'
    for cx in (95, 243, 391):
        d += f'<path d="M{cx},108 L{cx + (245 - cx) * 0.35},176"/>'
    for cx in (605, 753, 901):
        d += f'<path d="M{cx},108 L{cx + (755 - cx) * 0.35},176"/>'
    d += '</g>'
    d += _bucket(130, 190, 230, "Snowflake's storage", "its own format, its account")
    d += _bucket(640, 190, 230, "your S3 bucket", "open Parquet, your account")
    return d + "</svg>"


def _broom(x, y):
    """A tiny cartoon broom, handle up."""
    return (f'<line x1="{x}" y1="{y}" x2="{x + 14}" y2="{y + 46}" stroke="#111" stroke-width="2.2"/>'
            f'<path d="M{x + 2},{y + 44} L{x + 28},{y + 40} L{x + 36},{y + 66} L{x + 2},{y + 70} Z" fill="{BUTTER}" stroke="#111" stroke-width="1.4"/>'
            + "".join(f'<line x1="{x + 8 + k * 7}" y1="{y + 52}" x2="{x + 6 + k * 8}" y2="{y + 69}" stroke="#111" stroke-width="1"/>' for k in range(4)))


def drawing_chores():
    chores = [("1  Compaction", "merge small files", "Delta: OPTIMIZE", "Iceberg: rewrite data files"),
              ("2  Old versions", "delete files no kept version needs", "Delta: VACUUM (7 days kept)", "Iceberg: expire snapshots"),
              ("3  Orphans", "files a crashed write left behind", "Delta: VACUUM covers it", "Iceberg: remove orphan files"),
              ("4  Metadata", "keep the contents page small", "Delta: checkpoints", "Iceberg: rewrite manifests")]
    d = f'<svg viewBox="0 0 1000 250" role="img" aria-label="A chore chart with four cards and a broom. One, compaction: merge small files; Delta OPTIMIZE, Iceberg rewrite data files. Two, old versions: delete files no kept version needs; Delta VACUUM with 7 days kept, Iceberg expire snapshots. Three, orphans: files a crashed write left behind; Delta VACUUM covers it, Iceberg remove orphan files. Four, metadata: keep the contents page small; Delta checkpoints, Iceberg rewrite manifests.">'
    d += '<text x="500" y="28" text-anchor="middle" font-size="18">the chore chart every open table needs</text>'
    for i, (h, s, dl, ic) in enumerate(chores):
        x = 14 + i * 246
        d += f'<rect x="{x}" y="48" width="230" height="180" rx="10" fill="#fff" stroke="#111" stroke-width="1.5"/>'
        d += f'<rect x="{x}" y="48" width="230" height="40" rx="10" fill="{BUTTER}" stroke="#111" stroke-width="1.5"/>'
        d += f'<text x="{x + 14}" y="74" font-size="17">{h}</text>'
        d += f'<text x="{x + 14}" y="114" font-size="13.5">{s}</text>'
        d += f'<rect x="{x + 12}" y="132" width="206" height="34" rx="7" fill="{BLUE}" stroke="#111" stroke-width="1.2"/><text x="{x + 22}" y="154" font-size="13.5">{dl}</text>'
        d += f'<rect x="{x + 12}" y="176" width="206" height="34" rx="7" fill="{MINT}" stroke="#111" stroke-width="1.2"/><text x="{x + 22}" y="198" font-size="13.5">{ic}</text>'
    return d + "</svg>"


def drawing_who_cleans():
    cols = [("Unity Catalog managed", "UC picks the folder in your bucket", "Databricks", "Predictive Optimization, automatic", LAV),
            ("Unity Catalog external", "you pick the path; UC registers it", "You", "your scheduled OPTIMIZE / VACUUM jobs", ROSE),
            ("AWS-managed Iceberg", "Glue catalog or an S3 table bucket", "AWS", "Glue optimizers or S3 Tables, automatic", BLUE)]
    d = f'<svg viewBox="0 0 1000 300" role="img" aria-label="Three tables, each with a broom and who holds it. Unity Catalog managed: Unity Catalog picks the folder in your bucket; Databricks holds the broom through Predictive Optimization, automatically. Unity Catalog external: you pick the path and Unity Catalog only registers it; you hold the broom with your own scheduled OPTIMIZE and VACUUM jobs. AWS-managed Iceberg: Glue catalog or an S3 table bucket; AWS holds the broom through Glue optimizers or S3 Tables, automatically.">'
    for i, (name, own, who, how, fill) in enumerate(cols):
        x = 14 + i * 330
        d += f'<rect x="{x}" y="14" width="310" height="272" rx="12" fill="#fff" stroke="#111" stroke-width="1.5" stroke-dasharray="2 4"/>'
        d += f'<text x="{x + 155}" y="44" text-anchor="middle" font-size="18">{name}</text>'
        # the table: a small grid
        d += f'<rect x="{x + 30}" y="62" width="150" height="96" rx="6" fill="{fill}" stroke="#111" stroke-width="1.5"/>'
        d += "".join(f'<line x1="{x + 30}" y1="{86 + k * 24}" x2="{x + 180}" y2="{86 + k * 24}" stroke="#111" stroke-width="1"/>' for k in range(3))
        d += f'<line x1="{x + 80}" y1="62" x2="{x + 80}" y2="158" stroke="#111" stroke-width="1"/><line x1="{x + 130}" y1="62" x2="{x + 130}" y2="158" stroke="#111" stroke-width="1"/>'
        d += _broom(x + 220, 80)
        d += f'<text x="{x + 236}" y="176" text-anchor="middle" font-size="17">{who}</text>'
        d += f'<text x="{x + 155}" y="210" text-anchor="middle" font-size="13.5">{own}</text>'
        d += f'<rect x="{x + 16}" y="226" width="278" height="40" rx="8" fill="{BUTTER}" stroke="#111" stroke-width="1.2"/>'
        d += f'<text x="{x + 155}" y="251" text-anchor="middle" font-size="13.5">{how}</text>'
    return d + "</svg>"


def drawing_pointer():
    d = f'<svg viewBox="0 0 1000 300" role="img" aria-label="A catalog box holding a key and a pointer to the current metadata file, which points down to the Parquet files. The engine that commits through this catalog is the owner: it writes, sets permissions and cleans. A second engine reaches the same table through federation as a guest: it can read, but writes, clean-up and some features belong to the owner.">{ARROW}'
    d += f'<rect x="330" y="20" width="340" height="70" rx="10" fill="{LAV}" stroke="#111" stroke-width="1.5"/>'
    d += '<text x="500" y="48" text-anchor="middle" font-size="18">the catalog</text><text x="500" y="72" text-anchor="middle" font-size="13.5">holds one pointer: "current = metadata v42"</text>'
    # key
    d += '<circle cx="652" cy="38" r="9" fill="#fff" stroke="#111" stroke-width="1.5"/><line x1="643" y1="38" x2="615" y2="38" stroke="#111" stroke-width="2"/><line x1="622" y1="38" x2="622" y2="46" stroke="#111" stroke-width="2"/>'
    d += f'<rect x="390" y="130" width="220" height="40" rx="8" fill="{BLUE}" stroke="#111" stroke-width="1.5"/><text x="500" y="155" text-anchor="middle" font-size="14.5">metadata v42</text>'
    d += f'<rect x="360" y="210" width="280" height="50" rx="8" fill="{MINT}" stroke="#111" stroke-width="1.5"/><text x="500" y="240" text-anchor="middle" font-size="14.5">Parquet files in your bucket</text>'
    d += '<g stroke="#111" stroke-width="1.4" fill="none" marker-end="url(#tma)"><path d="M500,90 L500,128"/><path d="M500,170 L500,208"/></g>'
    # owner
    d += f'<rect x="20" y="30" width="220" height="110" rx="10" fill="{BUTTER}" stroke="#111" stroke-width="1.5"/>'
    d += '<text x="130" y="58" text-anchor="middle" font-size="17">the owner</text>'
    d += '<text x="130" y="84" text-anchor="middle" font-size="13.5">commits through this catalog</text><text x="130" y="104" text-anchor="middle" font-size="13.5">writes, permissions, chores</text>'
    d += '<path d="M240,62 L328,56" stroke="#111" stroke-width="2.4" fill="none" marker-end="url(#tma)"/><text x="284" y="46" text-anchor="middle" font-size="13">swaps it</text>'
    # guest
    d += '<rect x="760" y="30" width="220" height="110" rx="10" fill="#fff" stroke="#111" stroke-width="1.5" stroke-dasharray="5 4"/>'
    d += '<text x="870" y="58" text-anchor="middle" font-size="17">a guest engine</text>'
    d += '<text x="870" y="84" text-anchor="middle" font-size="13.5">reaches it by federation</text><text x="870" y="104" text-anchor="middle" font-size="13.5">reads well, writes little</text>'
    d += '<path d="M760,62 L672,56" stroke="#111" stroke-width="1.4" stroke-dasharray="5 4" fill="none" marker-end="url(#tma)"/><text x="716" y="46" text-anchor="middle" font-size="13">reads it</text>'
    d += '<text x="500" y="290" text-anchor="middle" font-size="14">whoever holds the pointer owns the table, whatever the file format</text>'
    return d + "</svg>"


def drawing_recommended():
    d = f'<svg viewBox="0 0 1000 300" role="img" aria-label="The recommended setup. Databricks compute writes Unity Catalog managed tables, Delta with Iceberg reads or managed Iceberg, into your S3 bucket. Predictive Optimization, drawn with a broom, does the chores. Athena, EMR, Trino and Snowflake read the same files as Iceberg through Unity Catalog\'s Iceberg REST catalog. One copy, one owner, many readers.">{ARROW}'
    d += _engine(40, 40, "Databricks jobs") + _engine(40, 110, "SQL warehouse")
    d += f'<rect x="300" y="30" width="400" height="140" rx="12" fill="{LAV}" stroke="#111" stroke-width="1.5"/>'
    d += '<text x="500" y="60" text-anchor="middle" font-size="18">Unity Catalog managed tables</text>'
    d += '<text x="500" y="86" text-anchor="middle" font-size="13.5">Delta with Iceberg reads (UniForm),</text><text x="500" y="106" text-anchor="middle" font-size="13.5">or managed Iceberg where others must write</text>'
    d += f'<rect x="330" y="122" width="250" height="34" rx="7" fill="{BUTTER}" stroke="#111" stroke-width="1.2"/><text x="455" y="144" text-anchor="middle" font-size="13.5">Predictive Optimization</text>'
    d += _broom(628, 94)
    d += _bucket(385, 196, 230, "your S3 bucket", "one copy, open files")
    for i, lab in enumerate(["Athena / EMR", "Trino", "Snowflake"]):
        d += f'<rect x="820" y="{30 + i * 56}" width="150" height="42" rx="8" fill="#fff" stroke="#111" stroke-width="1.5" stroke-dasharray="5 4"/><text x="895" y="{56 + i * 56}" text-anchor="middle" font-size="14.5">{lab}</text>'
    d += '<g stroke="#111" stroke-width="1.4" fill="none" marker-end="url(#tma)">'
    d += '<path d="M170,63 L298,80"/><path d="M170,133 L298,120"/>'
    d += '<path d="M818,51 L702,80"/><path d="M818,107 L702,100"/><path d="M818,163 L702,130"/><path d="M500,170 L500,190"/>'
    d += '</g><text x="760" y="214" text-anchor="middle" font-size="13">read as Iceberg through</text><text x="760" y="232" text-anchor="middle" font-size="13">the Iceberg REST catalog</text>'
    d += '<text x="105" y="190" text-anchor="middle" font-size="13">write and query</text>'
    return d + "</svg>"


# kind, who owns files and catalog, who does the chores, what DROP does, best for
KINDS = [
    ("Unity Catalog managed (Delta or managed Iceberg)", "Unity Catalog picks the folder, inside a bucket you own and set as the catalog's or schema's managed location",
     "Databricks. Predictive Optimization runs OPTIMIZE, VACUUM and ANALYZE when a table needs it, on serverless compute billed to you", "Data can be brought back with UNDROP for 7 days, then is deleted",
     "Almost every table on a Databricks platform"),
    ("Unity Catalog external", "You choose the path; Unity Catalog only registers it and controls access",
     "You. Predictive Optimization does not run on external tables, so schedule OPTIMIZE and VACUUM yourself", "Removes the registration; files stay in place",
     "Files written by another system, such as a vendor drop zone"),
    ("Glue Data Catalog Iceberg", "AWS Glue holds the pointer to the current metadata file; files in your S3 bucket",
     "AWS, if you switch on Glue's table optimizers: compaction, snapshot retention, orphan file deletion. Billed as Glue compute", "Depends on the engine and settings; check before dropping",
     "AWS-only platforms using Glue, EMR and Athena"),
    ("S3 Tables (table buckets)", "A special S3 bucket that holds Iceberg tables and has its own catalog",
     "AWS, built in and on by default: compaction, snapshot management, unreferenced file removal. Billed per object and byte processed", "Deletes the table",
     "AWS-only platforms that want the AWS twin of a managed table"),
]

INSIDE = [
    ("Where the contents page lives", "A _delta_log folder beside the data: one numbered JSON file per commit", "A tree of metadata files; a catalog holds the pointer to the top one"),
    ("How a commit becomes real", "The writer creates the next numbered file. Only one writer can create it; the loser retries. On S3 this uses conditional writes, or Unity Catalog coordinates commits", "The catalog swaps its pointer from the old metadata file to the new one, only if nobody swapped it first"),
    ("How readers find the current table", "Start from the newest checkpoint (written every 10 commits) and replay the newer JSON files", "Ask the catalog for the pointer, then follow metadata, manifest list, manifests, data files"),
    ("What an update does", "Writes new files and marks old ones removed in the log (or marks deleted rows with deletion vectors)", "Writes new files, or delete files, and a new snapshot that lists them"),
    ("How old files go away", "VACUUM deletes removed files older than the retention (7 days by default)", "Expire snapshots drops old versions and the files only they used; remove orphan files deletes leftovers"),
    ("What breaks if you clean too early", "Time travel to older versions, and long queries still reading old files, fail with file-not-found", "Same: readers of an expired snapshot fail"),
]

AWS = [
    ("Glue Data Catalog", "A catalog. For Iceberg it stores the location of each table's current metadata file. Lake Formation adds permissions on top."),
    ("Glue table optimizers", "Managed jobs you switch on per table or catalog: compaction, snapshot retention and orphan file deletion, run on AWS compute."),
    ("S3 Tables", "A table bucket: S3 storage plus an Iceberg catalog plus maintenance in one service, reached through its own API, the Glue catalog integration or an Iceberg REST endpoint."),
    ("Athena, EMR, Redshift, Glue jobs", "The AWS engines that read and write those tables through the Glue catalog."),
]

GUEST = [
    "Writes from Databricks to foreign Iceberg tables are limited; reads work well. This changes often, so check the Databricks docs before relying on writes.",
    "Predictive Optimization, row filters, column masks and features built on tables (metric views, Lakeflow pipelines) need tables Unity Catalog owns.",
    "Unity Catalog lineage only sees work done on Databricks; AWS jobs that write the table are invisible to it.",
    "Permissions live in two places, Lake Formation and Unity Catalog, and must be kept in step by hand.",
    "Upkeep is billed twice over: AWS maintenance on one bill, Databricks compute on the other, watched by two teams.",
    "The workaround, writing Glue Iceberg tables from Databricks with the open-source Iceberg library on a classic cluster, bypasses Unity Catalog governance entirely.",
]

PICK = [
    ("Databricks is the main engine (this site's AWS default)", "Unity Catalog managed tables in your bucket, Predictive Optimization on, Iceberg reads through UniForm for the tables outside engines need", "Pursue"),
    ("Another engine must also write the same table", "Managed Iceberg in Unity Catalog, written by others through its Iceberg REST catalog. See the limits on the Delta vs Iceberg page", "Pursue only where needed"),
    ("Something outside Databricks drops the files", "Unity Catalog external table, plus a scheduled OPTIMIZE and VACUUM job", "Pursue, with an owner for the chores"),
    ("AWS-only platform (Firehose, Glue, EMR, Athena; no Databricks)", "S3 Tables, or Glue Iceberg with optimizers on", "Pursue"),
    ("Tables another team already owns in Glue or S3 Tables", "Read them in place through catalog federation; don't copy", "Pursue for reading"),
    ("AWS owns and maintains the tables, Databricks does most of the work as a guest", "Two owners, two permission systems, limited writes, no Predictive Optimization or masks", "Drop"),
    ("External tables everywhere 'to stay open'", "Managed tables are already open files in your bucket; external only hands the chores back to you", "Drop"),
]

MISTAKES = [
    ("Calling external tables more open", "Managed tables are also Parquet in your bucket. External only means you took the chores back."),
    ("Nobody owns the chores", "External tables with no OPTIMIZE or VACUUM job, or Glue tables with optimizers off. Small files pile up quietly and queries slow down."),
    ("Two catalogs claiming one path", "Glue and Unity Catalog both register the same folder and both write. One day a clean-up job deletes files the other still needs."),
    ("Retention set by accident", "Version removal runs on the default, then an auditor asks for the table as it was 30 days ago."),
    ("Copying tables for a second engine", "A nightly job copies Delta into Iceberg: double storage, a lag, two truths. Let readers in through the catalog instead."),
]

QUESTIONS = [
    "For each important table, which catalog holds its pointer, and does exactly one catalog write to it?",
    "Is each table managed or external, and was that a choice made on purpose?",
    "Who runs compaction and version removal for each table, and when did they last run?",
    "Does history retention match how far back people need to travel in time?",
    "Can Athena or another engine read your tables today without a copy job?",
]

QA = [
    ("Does AWS run VACUUM on Unity Catalog tables?", "No. AWS has no say over tables Unity Catalog owns. For managed tables Databricks' Predictive Optimization does it; for external tables you schedule it yourself. AWS maintains only tables its own catalog owns: Glue Iceberg tables with optimizers on, and S3 Tables."),
    ("Is Databricks like a Snowflake virtual warehouse?", "Yes, for compute. A Databricks SQL warehouse starts, queries and stops like a Snowflake warehouse, and storage is already separate. The difference is that the storage is your own S3 bucket in open formats, not Snowflake-managed storage."),
    ("Do I need Iceberg managed by AWS to keep storage and compute separate?", "No. Unity Catalog managed tables already keep data in your bucket, separate from compute. Who maintains a table is a separate question from where it is stored."),
    ("Does Predictive Optimization work on external tables?", "No. It runs only on Unity Catalog managed tables, Delta and managed Iceberg. External tables need your own OPTIMIZE and VACUUM jobs."),
    ("Can Databricks write to S3 Tables or Glue Iceberg tables?", "It can read them in place through catalog federation. Writing to foreign Iceberg tables is limited, and support is changing; check the current Databricks docs. Writing with the open-source Iceberg library on a classic cluster works but skips Unity Catalog governance."),
    ("How do other engines read Unity Catalog managed tables?", "Through Unity Catalog's Iceberg REST catalog. Delta tables need Iceberg reads (UniForm) switched on; managed Iceberg tables are readable, and writable, by Iceberg engines directly."),
]

SOURCES = [
    ("Predictive optimization for Unity Catalog managed tables", "https://docs.databricks.com/aws/en/optimizations/predictive-optimization"),
    ("Unity Catalog managed tables", "https://docs.databricks.com/aws/tables/managed"),
    ("Unity Catalog external tables", "https://docs.databricks.com/aws/en/tables/external"),
    ("Apache Iceberg in Databricks", "https://docs.databricks.com/aws/en/iceberg"),
    ("AWS Glue Data Catalog table optimizers", "https://docs.aws.amazon.com/glue/latest/dg/table-optimizers.html"),
    ("Amazon S3 Tables maintenance", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables-maintenance.html"),
    ("Delta Lake VACUUM", "https://docs.databricks.com/aws/en/sql/language-manual/delta-vacuum"),
    ("Iceberg maintenance", "https://iceberg.apache.org/docs/latest/maintenance/"),
]


def fig(svg, cap):
    return f'<div class="fig">{svg}<p>{E(cap)}</p></div>'


def page():
    url = f"{SITE}{URL_PATH}"
    kinds = C.table(["Kind of table", "Who owns the files and catalog", "Who does the chores", "What DROP does", "Best for"], KINDS)
    inside = C.table(["", "Delta Lake", "Apache Iceberg"], INSIDE)
    aws = C.table(["AWS part", "What it does"], AWS)
    pick = ('<div class="tw"><table class="t"><tr><th>Situation</th><th>Setup</th><th>Verdict</th></tr>'
            + "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td><b>{E(c)}</b></td></tr>" for a, b, c in PICK) + "</table></div>")
    guest = "".join(f"<li>{E(g)}</li>" for g in GUEST)
    mist = "".join(f"<li><b>{E(a)}.</b> {E(b)}</li>" for a, b in MISTAKES)
    qs = "".join(f"<li>{E(q)}</li>" for q in QUESTIONS)
    src = "".join(f'<li><a href="{u}">{E(n)}</a></li>' for n, u in SOURCES)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/data-engineering/">Data engineering</a> › Who maintains your tables</p>
<p class="eyebrow" style="margin-top:22px">Data engineering · free guide · one page</p>
<h1>{E(TITLE)}</h1>
<p class="lede">A question on almost every AWS project with Databricks: "Can we keep tables in Iceberg, let AWS do the maintenance, and use Databricks only for analytics, like a Snowflake virtual warehouse?" It mixes two questions. Are storage and compute separate? And who does the chores on each table? This page answers both, shows how Delta and Iceberg commit and clean up inside, and gives the setup we recommend.</p>
<div class="tf">
<div class="box"><b>Short answer:</b> Databricks already separates storage and compute, with your data in your own S3 bucket. Who cleans a table depends on which catalog owns it, not on the file format. On a Databricks platform, keep tables as Unity Catalog managed tables, let Predictive Optimization do the chores, and let other engines read them as Iceberg. AWS-managed Iceberg is right for an AWS-only platform. Mixing the two, with AWS owning tables that Databricks mostly works on, is the setup to avoid.</div>

<section id="split"><p class="eyebrow">Question one</p><h2>Storage and compute are already separate</h2>
<p>Snowflake made "separate storage and compute" famous: the data sits in one place, and you start as many virtual warehouses as you like to query it, paying only while they run. Databricks works the same way. A SQL warehouse is the direct match for a Snowflake virtual warehouse, and job and notebook clusters are more compute of the same kind. The difference is the storage: with Databricks it is <b>your own S3 bucket</b>, holding open Parquet files.</p>
{fig(drawing_split(), "Both split storage from compute. Databricks' storage is your bucket, in open files.")}
<p>So you don't need AWS to run maintenance to get the split. You already have it. The real question is the second one.</p></section>

<section id="chores"><p class="eyebrow">Question two</p><h2>Every table has chores</h2>
<p>An open table gets messier with every write. Small writes leave many small files. Updates and deletes never edit a file; they write new files and mark the old ones as removed, and the old files stay on disk so you can read the table as it was last week. Someone has to tidy up. The two formats name the chores differently, but they are the same four jobs.</p>
{fig(drawing_chores(), "Skip the chores and queries slow down while storage grows. Do them too eagerly and time travel breaks.")}</section>

<section id="who"><p class="eyebrow">The answer</p><h2>Who does the chores depends on who owns the table</h2>
{fig(drawing_who_cleans(), "Three kinds of table you meet on AWS with Databricks, and who holds the broom for each.")}
{kinds}
<div class="two">
<div class="card"><h3>Managed versus external, in one line</h3><p>Both keep open files in your bucket. Managed means Unity Catalog runs the table's whole life, chores included. External means you keep the path and the chores.</p></div>
<div class="card"><h3>Predictive Optimization</h3><p>Databricks' automatic upkeep for managed tables. It watches how each table is used and runs compaction, VACUUM and statistics only when they pay off. It is on by default for newer accounts and can be set per account, catalog or schema.</p></div>
</div></section>

<section id="inside"><p class="eyebrow">Under the hood</p><h2>How Delta and Iceberg work inside</h2>
<p>Both formats are the same Parquet files with a contents page on top. Delta keeps the contents page as an ordered diary of changes next to the data. Iceberg keeps it as a tree of metadata files, and a catalog holds the pointer to the top of the tree.</p>
{fig(TF.drawing(), "Same Parquet files, two different contents pages. For Iceberg, the catalog's pointer decides which version is current.")}
{inside}
<p>For the full feature comparison on Databricks, see <a href="/learn/delta-vs-iceberg/">Delta Lake vs Apache Iceberg</a>. To watch a Delta table commit, VACUUM and break time travel step by step, see <a href="/learn/data-platform-sim/delta/">Delta Lake internals, recorded</a>.</p></section>

<section id="pointer"><p class="eyebrow">Why it matters</p><h2>Whoever holds the pointer owns the table</h2>
<p>In Iceberg, a write only becomes real when the catalog swaps its pointer to the new metadata file. Delta is the same in spirit: whoever owns the log folder owns the commits. So whoever holds the pointer controls writes, permissions and clean-up. Every other engine is a guest.</p>
{fig(drawing_pointer(), "One owner commits and cleans. Guests read through federation.")}</section>

<section id="aws"><p class="eyebrow">The AWS wrapper</p><h2>What AWS adds around Iceberg</h2>
{aws}
<p>With Glue or S3 Tables holding the pointer, AWS is the owner and does the chores. Databricks then reaches those tables through <b>catalog federation</b>: Unity Catalog shows them as foreign tables that another catalog owns. That works for reading. As the main engine, it costs you:</p>
<ul>{guest}</ul></section>

<section id="pick"><p class="eyebrow">Choosing</p><h2>What we recommend</h2>
{fig(drawing_recommended(), "One copy, one owner doing the chores, many engines reading.")}
{pick}</section>

<section id="mistakes"><p class="eyebrow">What goes wrong</p><h2>Mistakes we see often</h2><ol>{mist}</ol></section>
<section id="check"><p class="eyebrow">Your turn</p><h2>Five questions to check your own setup</h2><ol>{qs}</ol></section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(QA)}</section>
<section id="sources"><p class="eyebrow">Sources</p><h2>Checked against</h2>
<p>AWS and Databricks change Iceberg support every few months. Check the docs below before relying on federation writes or preview features.</p><ul>{src}</ul></section>
<section id="next"><p class="eyebrow">Related</p><h2>Where it connects</h2>
<p><a href="/learn/delta-vs-iceberg/">Delta vs Iceberg on Databricks</a> · <a href="/learn/data-platform-architecture/aws-databricks/">Data platform on AWS + Databricks</a> · <a href="/learn/data-systems/platform/layout/">Layout: catalogs and schemas</a> · <a href="/learn/data-systems/platform/cost/">Cost and FinOps</a> · <a href="/data-engineering/">All data engineering</a></p></section>
</div>"""
    crumbs = [("Data engineering", f"{SITE}/data-engineering/"), ("Who maintains your tables", url)]
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": TITLE, "description": DESC, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in QA]}]
    head = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(TITLE, DESC, url, body, head)


def main():
    out = ROOT / "learn" / "table-maintenance"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("table maintenance ->", out / "index.html")


if __name__ == "__main__":
    main()
