"""Component pages under /learn/data-platform-architecture/<component>/.

    python3 _guides/components.py

One page per box of the architecture drawing: metadata store, ingestion, bronze to silver, gold.
Each page: you-are-here drawing, plain words, design with real code, the metadata it reads,
what goes wrong (and the fix), products per platform, FAQ, next.
"""
import json
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "_paths"))
import medallion as M  # noqa: E402
from diagrams import FILL, arrow, box, svg, text  # noqa: E402

wb = M.wb
SITE = wb.SITE
BASE = "/learn/data-platform-architecture/"
CSS = M.CSS + """<style>
  pre.code { font-family:var(--mono); font-size:12.5px; line-height:1.5; background:var(--surface-2); border:1px solid var(--rule); border-radius:8px; padding:12px 14px; overflow-x:auto; }
  .cap { font-size:13px; color:var(--faint); margin:-8px 0 16px; }
  .split { display:grid; grid-template-columns:1fr 1fr; gap:14px; } @media (max-width:760px) { .split { grid-template-columns:1fr; } }
  .card { border:var(--line); border-radius:var(--wob); padding:12px 16px; background:#fff; } .card h4 { font-family:var(--hand); font-weight:400; font-size:21px; margin:0 0 4px; }
  .card.good { background:var(--mint-wash); } .card.bad { background:var(--rose-wash); }
  .sib { display:flex; flex-wrap:wrap; gap:8px; margin:14px 0 0; font-size:14px; } .sib a, .sib span { border:1.5px solid var(--ink); border-radius:999px; padding:2px 12px; text-decoration:none; color:var(--ink); background:#fff; } .sib span { background:var(--ink); color:#fff; }
</style>"""

SPINE = [("Sources", "grey"), ("Landing", "white"), ("Bronze", "bronze"), ("Silver", "silver"), ("Gold", "gold"), ("Semantic", "mint"), ("Experiences", "sky")]


def here(highlight, control=False):
    """A small spine with the component's boxes highlighted (others faded)."""
    b = ""
    y0 = 70 if True else 20
    cp_style = 'stroke-width="2.6"' if control else 'stroke-width="1.2" opacity="0.45"'
    b += f'<rect x="10" y="8" width="1040" height="40" rx="12" fill="{FILL["mint"]}" stroke="#1F1F1F" {cp_style}/>'
    b += text(530, 33, "Control plane: manifest → metadata DB → generators → pipelines", 15, fill="#1F1F1F" if control else "#999")
    x = 10
    for i, (n, f) in enumerate(SPINE):
        on = n in highlight
        b += (f'<g opacity="{1 if on else 0.4}">' + box(x, y0, 132, 56, n, "", f).replace('stroke-width="1.6"', f'stroke-width="{2.8 if on else 1.2}"') + "</g>")
        if i < len(SPINE) - 1:
            b += arrow(x + 134, y0 + 28, x + 148, y0 + 28)
        x += 151
    b += text(530, 150, "you are here: " + (" + ".join(highlight) if highlight else "the control plane, which drives every layer"), 15, fill="#1F1F1F")
    return svg(1060, 160, b, "Where this component sits: " + ", ".join(highlight or ["control plane"]))


COMPONENTS = ["metadata-store", "ingestion", "bronze-to-silver", "gold"]
TITLES = {"metadata-store": "The metadata store", "ingestion": "Ingestion: sources to bronze", "bronze-to-silver": "Bronze to silver: clean, dedupe, keep history", "gold": "Gold: shaped for the business"}
SHORT = {"metadata-store": "Metadata store", "ingestion": "Ingestion", "bronze-to-silver": "Bronze to silver", "gold": "Gold"}


def siblings(cur):
    return '<div class="sib"><a href="' + BASE + '">↑ The whole picture</a>' + "".join(
        f'<span>{SHORT[c]}</span>' if c == cur else f'<a href="{BASE}{c}/">{SHORT[c]}</a>' for c in COMPONENTS) + "</div>"


def code(s, cap=""):
    return f'<pre class="code">{E(s.strip())}</pre>' + (f'<p class="cap">{E(cap)}</p>' if cap else "")


def table(head, rows):
    h = "".join(f"<th>{E(x)}</th>" for x in head)
    r = "".join("<tr>" + "".join(f"<td>{'<b>' + E(c) + '</b>' if i == 0 else E(c)}</td>" for i, c in enumerate(row)) + "</tr>" for row in rows)
    return f'<div class="tw"><table class="t"><tr>{h}</tr>{r}</table></div>'


def problems(rows):
    out = ""
    for name, see, naive, right in rows:
        out += (f'<h3 style="margin-top:16px">{E(name)}</h3><p>{E(see)}</p><div class="split">'
                f'<div class="card bad"><h4>Naive fix</h4>{E(naive)}</div><div class="card good"><h4>Right fix</h4>{E(right)}</div></div>')
    return out


def faq(items):
    return "".join(f'<details class="faq"><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in items)


# ======================================================================= metadata store
def metadata_store():
    ddl = """
-- PostgreSQL. One database per environment (dev, test, prod), same schema.
CREATE TABLE platform_config (
  config_key   text PRIMARY KEY,
  config_value text NOT NULL,
  description  text,
  updated_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE source_master (
  source_id   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_name text NOT NULL UNIQUE,
  source_type text NOT NULL,              -- postgres, sftp, rest, kafka …
  is_active   boolean NOT NULL DEFAULT true,
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE source_config (
  config_id    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id    uuid NOT NULL REFERENCES source_master(source_id),
  config_key   text NOT NULL,
  config_value text NOT NULL,
  config_group text NOT NULL,              -- ingestion, quality, cost …
  is_active    boolean NOT NULL DEFAULT true,
  updated_at   timestamptz NOT NULL DEFAULT now(),
  UNIQUE (source_id, config_key)
);

CREATE TABLE dataset_master (
  dataset_id   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  dataset_name text NOT NULL,
  source_id    uuid NOT NULL REFERENCES source_master(source_id),
  schema_name  text,
  table_name   text,
  is_active    boolean NOT NULL DEFAULT true,
  created_at   timestamptz NOT NULL DEFAULT now(),
  updated_at   timestamptz NOT NULL DEFAULT now(),
  UNIQUE (source_id, dataset_name)
);

CREATE TABLE dataset_config (            -- same shape as source_config
  config_id    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  dataset_id   uuid NOT NULL REFERENCES dataset_master(dataset_id),
  config_key   text NOT NULL,
  config_value text NOT NULL,
  config_group text NOT NULL,
  is_active    boolean NOT NULL DEFAULT true,
  updated_at   timestamptz NOT NULL DEFAULT now(),
  UNIQUE (dataset_id, config_key)
);"""
    view = """
CREATE VIEW dataset_view AS
SELECT
  dm.dataset_id, dm.dataset_name, dm.schema_name, dm.table_name,
  sm.source_id,  sm.source_name,  sm.source_type,
  COALESCE((SELECT jsonb_object_agg(sc.config_key, sc.config_value)
            FROM source_config sc
            WHERE sc.source_id = sm.source_id AND sc.is_active), '{}'::jsonb)   AS source_config_json,
  COALESCE((SELECT jsonb_object_agg(dc.config_key, dc.config_value)
            FROM dataset_config dc
            WHERE dc.dataset_id = dm.dataset_id AND dc.is_active), '{}'::jsonb) AS dataset_config_json,
  COALESCE((SELECT jsonb_object_agg(pc.config_key, pc.config_value)
            FROM platform_config pc), '{}'::jsonb)                             AS platform_config_json
FROM dataset_master dm
JOIN source_master  sm ON sm.source_id = dm.source_id
WHERE dm.is_active AND sm.is_active;"""
    reader = """
import hashlib, json

def load_combined_config(conn, dataset_id: str) -> dict:
    row = conn.execute(
        "SELECT dataset_name, platform_config_json, source_config_json, dataset_config_json "
        "FROM dataset_view WHERE dataset_id = %s", (dataset_id,)).fetchone()
    if row is None:
        raise LookupError(f"dataset {dataset_id} is missing or inactive")
    combined = {}
    combined.update(row["platform_config_json"])   # lowest priority
    combined.update(row["source_config_json"])     # source overrides platform
    combined.update(row["dataset_config_json"])    # dataset overrides source
    return {"dataset_name": row["dataset_name"], "config": combined}

def fingerprint(config: dict) -> str:
    canonical = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]"""
    yaml = """
# manifests/shop_db.yaml  (edited by pull request; key names are illustrative)
source: shop_db
type: postgres
config:
  ingestion.connection_ref: kv://shop-db-readonly   # a secret reference, never the secret
  ingestion.mode: incremental
datasets:
  - name: orders
    schema: public
    table: orders
    config:
      ingestion.watermark_column: updated_at
      silver.key: order_id
      silver.history: scd1
      quality.on_bad_row: quarantine
      cost.owner: sales-analytics
  - name: customers
    schema: public
    table: customers
    config:
      ingestion.mode: cdc                            # overrides the source default
      silver.key: customer_id
      silver.history: scd2"""
    runlog = """
CREATE TABLE run_log (
  run_id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  dataset_id         uuid NOT NULL REFERENCES dataset_master(dataset_id),
  batch_id           text NOT NULL,
  layer              text NOT NULL,               -- bronze, silver, gold
  status             text NOT NULL,               -- running, succeeded, failed
  config_fingerprint text NOT NULL,               -- which config this run used
  config_snapshot    jsonb NOT NULL,              -- the exact merged config
  rows_in            bigint, rows_out bigint, rows_quarantined bigint,
  started_at         timestamptz NOT NULL DEFAULT now(),
  ended_at           timestamptz
);
CREATE TABLE watermark (                          -- runtime state, never in the config tables
  dataset_id      uuid PRIMARY KEY REFERENCES dataset_master(dataset_id),
  watermark_value text NOT NULL,
  last_run_id     uuid REFERENCES run_log(run_id),
  updated_at      timestamptz NOT NULL DEFAULT now()
);"""
    body = f"""
<section id="plain"><p class="eyebrow">In plain words</p><h2>The platform's rule book</h2>
<p>Every pipeline needs to know things before it runs: where the source is, which columns are the key, how history is kept, which checks to run, who pays. In a metadata-driven platform none of that is written inside the pipeline. It lives in one place, the metadata store, and every pipeline reads its settings from there. Adding a source means adding rows, not writing code.</p>
<figure class="diagram">{here([], control=True)}<figcaption>The metadata store sits in the control plane and drives every layer.</figcaption></figure>
<p>The design here follows the article <a href="https://medium.com/@basant.choudhary09/metadata-db-design-for-data-engineering-components-ingestion-processing-data-quality-data-6b355ad5ecb9">Metadata DB Design for Data Engineering Platforms</a>. It has three rules: a new setting needs <b>no schema change</b>; master data and settings are <b>kept apart with real foreign keys</b>; and readers get <b>one stable interface</b> that never changes when settings are added.</p></section>

<section id="model"><p class="eyebrow">The model</p><h2>Five tables in two tiers</h2>
{table(["Table", "Tier", "One row per", "Why it exists"], [
        ("platform_config", "settings", "platform-wide setting", "Defaults for everything: time zone, retry count, alert channel"),
        ("source_master", "master", "upstream system", "A database, an API, a bucket, a topic"),
        ("source_config", "settings", "setting of one source", "Key-value, grouped (ingestion, quality, cost); new keys need no ALTER TABLE"),
        ("dataset_master", "master", "dataset of a source", "A table, a file pattern, a stream"),
        ("dataset_config", "settings", "setting of one dataset", "Overrides for this dataset only")])}
{code(ddl, "The tables, in PostgreSQL. UUID keys make it safe to copy settings between the dev, test and prod databases.")}
</section>

<section id="reader"><p class="eyebrow">Reading it</p><h2>One view, one function, one override order</h2>
<p>Pipelines never query the tables directly. They read one view, which returns one row per dataset with each tier's settings as a JSON object. Each tier is aggregated in its own subquery, so rows never multiply and a dataset with no settings gets an empty object instead of an error.</p>
{code(view)}
<p>The reader merges the three objects in a fixed order: <b>platform, then source, then dataset</b>. A dataset setting beats a source setting, which beats a platform default. It also computes a <b>fingerprint</b> of the merged settings.</p>
{code(reader, "Python. The fingerprint is a short hash of the merged settings, so two runs with the same fingerprint used exactly the same configuration.")}
</section>

<section id="yaml"><p class="eyebrow">Changing it</p><h2>YAML in git, a loader, then the database</h2>
<p>People and agents never edit the tables by hand. They change a YAML file through a pull request, where it is reviewed and tested. A loader then checks every key against a <b>key registry</b> (each key's table, type, allowed values and default) and writes the rows. Git is the history of every change; the database is what pipelines read at run time.</p>
{code(yaml)}
<div class="split"><div class="card"><h4>The loader</h4>Parses the YAML, rejects unknown keys and wrong types, then upserts source_master, source_config, dataset_master and dataset_config in one transaction. Removed keys are set <code>is_active = false</code>, not deleted, so history stays.</div>
<div class="card"><h4>Protected keys</h4>Keys that loosen a data contract or change a metric definition need an extra approver, and an agent can never change them on its own.</div></div>
</section>

<section id="runtime"><p class="eyebrow">Runtime</p><h2>Settings and state live apart</h2>
<p>Settings say what should happen. State records what did happen: watermarks, run logs, quality results. Keeping them in separate tables means changing a setting never rewrites history, and every run can prove which settings it used.</p>
{code(runlog, "Every run stores the fingerprint and a full copy of the settings it ran with. A replay or backfill months later can show exactly what it used.")}
{table(["Table", "Holds"], [("run_log", "One row per run per layer: status, counts, the settings fingerprint and snapshot"), ("watermark", "How far each dataset has been loaded; advanced only after a successful commit"), ("dq_results, dq_violations", "Each check's result per run, and the rows that failed"), ("dataset_config_columns", "Column-level settings: types, primary key, PII class, silver name and type, transforms")])}
</section>

<section id="problems"><p class="eyebrow">What goes wrong</p><h2>Common problems</h2>
{problems([
        ("A new setting needs a database change", "Every new option means an ALTER TABLE, a migration and a release, so teams start hard-coding settings in pipelines instead.", "Add a column each time and schedule a migration.", "Key-value settings with a key registry: a new key is a registry entry and a YAML line."),
        ("Nobody knows which settings a run used", "A number changed last month; the settings have been edited three times since.", "Read the current settings and hope they didn't change.", "Store the fingerprint and snapshot on every run_log row."),
        ("Dev settings leak into production", "A test bucket path ends up in a prod pipeline.", "An env column and careful WHERE clauses.", "One database per environment, same schema; YAML promoted through CI."),
        ("Settings edited directly in the database", "Production behaves differently from what is in git, and nobody knows why.", "Ask people to be careful.", "Only the loader writes; it is fed by YAML from git; direct writes are blocked by permissions.")])}
</section>"""
    plat = table(["Job", "AWS", "Azure", "Google Cloud", "Databricks", "Open source"], [
        ("Metadata database", "RDS or Aurora PostgreSQL", "Azure Database for PostgreSQL", "Cloud SQL for PostgreSQL", "Lakebase (Postgres)", "PostgreSQL"),
        ("Secrets referenced from config", "Secrets Manager", "Key Vault", "Secret Manager", "Databricks secrets", "Vault or sops"),
        ("YAML → loader in CI", "GitHub Actions or CodeBuild", "GitHub Actions or Azure Pipelines", "GitHub Actions or Cloud Build", "GitHub Actions + bundles", "GitHub Actions")])
    qa = [("Why not just keep the YAML and skip the database?", "YAML is great for writing and reviewing, but pipelines need fast, consistent reads, runtime state next to settings, and joins with run logs. The database gives that; git keeps the history."),
          ("Why key-value instead of proper columns?", "Settings grow every month. Key-value rows absorb a new setting without a schema change, and the key registry gives back the type safety that columns would have given."),
          ("Why one database per environment?", "So dev and test can never read or overwrite production settings by mistake, and so promoting a change is a normal release through CI."),
          ("What is the config fingerprint for?", "It proves which settings a run used. Two runs with the same fingerprint ran with identical settings; a backfill can reuse a past run's snapshot exactly.")]
    return "metadata-store", "The metadata store", "How a metadata-driven data platform stores its settings: five tables, one reader view, an override order, a YAML loader and a fingerprint on every run.", body, plat, qa


# ======================================================================= ingestion
def ingestion():
    modes = table(["Mode", "How it works", "Good for", "Watch out for"], [
        ("Full load", "Copy the whole table every run", "Small tables, reference data", "Gets slower and dearer as data grows"),
        ("Incremental (watermark)", "Copy rows changed since the last high-water mark, e.g. updated_at > last value", "Large tables with a reliable 'updated at'", "Misses hard deletes; needs a column that really changes on every update"),
        ("Change data capture (CDC)", "Read the database's change log: every insert, update and delete in order", "Big, busy tables; when deletes matter", "Needs log access on the source; ordering and schema changes"),
        ("File drop", "Pick up new files from a folder or bucket", "Partners, exports, legacy systems", "Half-written files, duplicates, late files"),
        ("API pull", "Call an API page by page", "SaaS apps", "Rate limits, pagination, changing payloads"),
        ("Event stream", "Read a topic continuously", "Clicks, devices, payments", "Late and duplicate events; see the streaming lane")])
    lander = """
from pyspark.sql import functions as F

def land_to_bronze(spark, cfg: dict, batch_id: str, files: list[str], run_log):
    if run_log.has_succeeded(cfg["dataset_id"], "bronze", batch_id):
        return 0                                    # seen this batch: re-running adds nothing

    df = (spark.read.format(cfg["landing.format"])  # files exactly as received
               .options(**cfg.get("landing.read_options", {}))
               .load(files))

    df = (df.withColumn("_ingested_at", F.current_timestamp())
            .withColumn("_source",   F.lit(cfg["source_name"]))
            .withColumn("_batch_id", F.lit(batch_id))
            .withColumn("_file",     F.col("_metadata.file_path")))

    (df.write.format("delta")
       .mode("append")                              # bronze is append-only
       .option("mergeSchema", cfg.get("bronze.allow_new_columns", "true"))
       .saveAsTable(cfg["bronze.table"]))

    rows = df.count()
    run_log.succeed(cfg["dataset_id"], "bronze", batch_id, rows_out=rows)
    return rows"""
    order = """
1. read watermark            -> 2026-10-26 09:00
2. mover copies rows with updated_at > watermark into landing/orders/batch=b-0912/
3. lander appends landing files to bronze (one commit)
4. run_log: bronze b-0912 succeeded, 1,204 rows
5. ONLY NOW advance watermark -> max(updated_at) in the batch = 2026-10-27 08:59"""
    body = f"""
<section id="plain"><p class="eyebrow">In plain words</p><h2>Get everything in, exactly as it was</h2>
<p>Ingestion has one job: copy data from the systems that create it into the platform, faithfully, without losing or doubling anything, and with a note on every row saying where and when it came from. It does <b>not</b> clean or reshape anything. That is silver's job.</p>
<figure class="diagram">{here(["Sources", "Landing", "Bronze"])}<figcaption>Ingestion covers sources, landing and bronze.</figcaption></figure>
<p>It is split into two parts with one boundary between them:</p>
<div class="split"><div class="card"><h4>The mover</h4>Gets bytes from a source into the <b>landing</b> area as files. Swappable: Spark JDBC, Data Factory, Lakeflow Connect, dlt, a partner's SFTP. Holds no business logic.</div>
<div class="card"><h4>The lander</h4>Our own code, the same on every platform. Reads landing files, adds the audit columns, appends to <b>bronze</b> in one commit, records the run. Owns watermarks, idempotency and schema drift.</div></div>
<p>Because the lander is the same everywhere, changing the mover (say, from Data Factory to Lakeflow Connect) never changes what bronze looks like.</p></section>

<section id="modes"><p class="eyebrow">Choosing</p><h2>Six ways to bring data in</h2>{modes}
<p>The mode is a setting per dataset (<code>ingestion.mode</code>), not a different pipeline. See also <a href="/concepts/incremental-loads/">full vs incremental</a> and <a href="/concepts/cdc/">change data capture</a>.</p></section>

<section id="metadata"><p class="eyebrow">Metadata-driven</p><h2>A new source is a few lines of YAML</h2>
<p>To onboard the <code>customers</code> table, someone adds a dataset entry to the source's YAML (mode, key, history, checks, owner) and opens a pull request. The loader writes it into the <a href="{BASE}metadata-store/">metadata store</a>; the generator produces the mover job, the lander job and the orchestration task from it. Nobody writes a new pipeline.</p></section>

<section id="landing"><p class="eyebrow">Landing</p><h2>Files as received</h2>
<ul><li>One folder per source, dataset and batch: <code>landing/shop_db/orders/batch=b-0912/</code>.</li>
<li>Files are never edited and never deleted by a pipeline; a retention rule removes them after a few weeks.</li>
<li>A batch is only picked up once a <code>_SUCCESS</code> marker (or the mover's own commit) says it is complete, so half-written files are never read.</li>
<li>Skipped when CDC writes straight into bronze.</li></ul></section>

<section id="lander"><p class="eyebrow">The lander</p><h2>Landing to bronze, safely</h2>
{code(lander, "PySpark with Delta Lake. Settings come from the metadata store's merged config (key names illustrative).")}
<p>Three things make it safe to run again and again:</p>
<ol><li><b>Batch check first.</b> If the run log says this batch already reached bronze, it stops: a retried job adds nothing.</li>
<li><b>One commit.</b> The append is a single Delta transaction: readers see the whole batch or none of it.</li>
<li><b>Watermark last.</b> The watermark moves only after the run is recorded as successful.</li></ol>
{code(order, "The order of a watermark load. If the job dies after step 3, the watermark hasn't moved, the batch check stops a double append, and the next run picks up cleanly.")}
<h3>When the source changes shape</h3>
<p>A new column is added to bronze automatically (bronze keeps the source's shape). A removed or renamed column, or a changed type, is <b>not</b> fixed in bronze: the data lands as it is, and the contract check at the bronze-to-silver hop stops it and alerts the owner.</p></section>

<section id="problems"><p class="eyebrow">What goes wrong</p><h2>Common problems</h2>
{problems([
        ("The same batch lands twice", "A retried job or a re-sent file doubles yesterday's rows in bronze.", "DISTINCT in every query downstream.", "Check the batch id against the run log before appending; dedupe by key again in silver."),
        ("Deleted rows never disappear", "A closed account still shows everywhere, because a watermark query only sees rows that still exist.", "Reload everything every night.", "CDC with delete events, or a periodic key comparison that flags missing keys as deleted in silver."),
        ("The watermark skips rows", "Rows updated in the same second as the last load are lost, or a row updated without touching updated_at never arrives.", "Subtract an hour from the watermark and accept duplicates.", "Use a column that always changes, overlap slightly and dedupe by key, or switch to CDC."),
        ("A half-written file is read", "Bronze gets a truncated batch.", "Wait a few minutes before reading.", "Only read a batch after its completion marker; the mover writes the marker last."),
        ("The source goes dark for six hours", "Alerts all night, then a flood.", "Page someone every hour.", "A freshness check with a sensible threshold, then a catch-up run; the batch check absorbs the flood without duplicates.")])}
</section>"""
    plat = table(["Job", "AWS", "Azure", "Google Cloud", "Databricks", "Open source"], [
        ("Mover: databases", "DMS, Glue JDBC", "Data Factory copy, mirroring", "Datastream", "Lakeflow Connect, Spark JDBC", "dlt, Airbyte, Spark JDBC"),
        ("Mover: files and APIs", "AppFlow, Transfer Family", "Data Factory", "Storage Transfer, Cloud Functions", "Auto Loader", "dlt"),
        ("Landing storage", "S3", "ADLS Gen2 / OneLake", "Cloud Storage", "Unity Catalog volumes", "MinIO"),
        ("Lander (our code)", "Glue or EMR Spark", "Fabric Spark", "Dataproc", "Databricks jobs", "PySpark"),
        ("Bronze tables", "Iceberg on S3", "Delta in OneLake", "Iceberg on BigLake", "Delta in Unity Catalog", "Delta or Iceberg")])
    qa = [("Why not let the ingestion tool write bronze directly?", "Then bronze looks different for every tool, and idempotency, audit columns and watermarks are re-implemented each time. A thin, shared lander keeps bronze identical whatever moved the data."),
          ("Should bronze have the source's types or all strings?", "Keep the source's shape. Many teams land everything as strings to avoid failed loads; either way, typing is silver's job, where a failed cast goes to quarantine with a reason."),
          ("Do I need a landing area with CDC?", "Usually not: CDC tools can write change events straight into bronze. Keep landing when you might need to re-parse the raw files."),
          ("How long should bronze be kept?", "Long enough to rebuild silver after any bug you might find late, often months to years, within your privacy rules. Landing is short-lived.")]
    return "ingestion", "Ingestion: sources to bronze", "How data gets into a platform safely: six ingestion modes, mover vs lander, landing files, audit columns, batch checks and watermarks.", body, plat, qa


# ======================================================================= bronze to silver
def bronze_to_silver():
    steps = table(["Step", "What it does", "Example"], [
        ("Select and rename", "Keep the agreed columns, give them their silver names", "cust → customer_id"),
        ("Cast types", "Text to numbers, dates, timestamps; a failed cast goes to quarantine", "'1,250.00' → 1250.00"),
        ("Trim and standardise", "Remove stray spaces, one case, one code list", "'PAID ' → 'paid'; 'inr' → 'INR'"),
        ("Fix time", "Parse with the source's time zone, store UTC", "27/10/2026 08:58 IST → 03:28 UTC"),
        ("Handle nulls", "Defaults only where the contract allows; otherwise quarantine", "country null → 'unknown' (allowed)"),
        ("Check the contract", "Required fields, ranges, allowed values, referential checks", "amount ≥ 0; customer_id not null"),
        ("Dedupe", "Keep the latest row per business key", "order 1001 sent twice → one row"),
        ("Keep history", "SCD Type 1 (overwrite) or Type 2 (new version)", "customer moves city"),
        ("Mask personal data", "Per the column's PII class and the reader's role", "phone → ******3210")])
    dedupe = """
from pyspark.sql import Window, functions as F

w = Window.partitionBy("order_id").orderBy(F.col("updated_at").desc(), F.col("_ingested_at").desc())
latest = (bronze_batch
          .withColumn("_rn", F.row_number().over(w))
          .filter("_rn = 1")
          .drop("_rn"))"""
    scd1 = """
MERGE INTO silver.orders AS t
USING staged_orders AS s                      -- one row per order_id, already cleaned
ON t.order_id = s.order_id
WHEN MATCHED AND t.row_hash <> s.row_hash THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;"""
    scd2 = """
MERGE INTO silver.customer AS t
USING (
  -- every staged row, keyed by customer_id: closes the current version if it changed
  SELECT s.customer_id AS merge_key, s.* FROM staged_customer s
  UNION ALL
  -- a second copy of changed rows, with no key, so it is inserted as the new version
  SELECT NULL AS merge_key, s.* FROM staged_customer s
  JOIN silver.customer c ON c.customer_id = s.customer_id AND c.is_current
  WHERE c.row_hash <> s.row_hash
) AS u
ON t.customer_id = u.merge_key AND t.is_current
WHEN MATCHED AND t.row_hash <> u.row_hash THEN
  UPDATE SET is_current = false, valid_to = u.changed_at
WHEN NOT MATCHED THEN
  INSERT (customer_id, name, city, email, row_hash, valid_from, valid_to, is_current)
  VALUES (u.customer_id, u.name, u.city, u.email, u.row_hash, u.changed_at, NULL, true);"""
    scd2rows = """
customer_id | city   | valid_from          | valid_to            | is_current
C-77        | Pune   | 2024-03-02 10:00:00 | 2026-11-15 09:00:00 | false
C-77        | Sydney | 2026-11-15 09:00:00 | NULL                | true"""
    body = f"""
<section id="plain"><p class="eyebrow">In plain words</p><h2>From a faithful record to one clean row per real thing</h2>
<p>Bronze is everything as it arrived: strings, duplicates, bad rows and all. Silver is the first layer with an opinion: <b>one clean, typed row per real thing</b> (an order, a customer), with history kept the way the business needs, and with every row that breaks the rules set aside with its reason.</p>
<figure class="diagram">{here(["Bronze", "Silver"])}<figcaption>This component is the hop from bronze to silver.</figcaption></figure></section>

<section id="steps"><p class="eyebrow">The steps</p><h2>Common transformations, in order</h2>{steps}
<p>Each step is driven by column-level settings in the <a href="{BASE}metadata-store/">metadata store</a> (silver name and type, PII class, transforms), not hand-written per table.</p></section>

<section id="quarantine"><p class="eyebrow">Bad rows</p><h2>Quarantine, never drop</h2>
<p>A row that fails a cast or a contract rule is written to a quarantine table with the rule it broke, the batch it came from and when. Silver gets only good rows. The owner sees a count and the reasons. Two rules: a row is <b>never silently dropped</b>, and a rule is <b>never loosened just to make a job pass</b>. A check that looked at zero rows is an error, not a pass.</p></section>

<section id="dedupe"><p class="eyebrow">Duplicates</p><h2>Latest row per key</h2>
{code(dedupe, "Keep one row per business key: the most recently updated, and if two tie, the most recently ingested.")}</section>

<section id="scd1"><p class="eyebrow">History: Type 1</p><h2>SCD Type 1: overwrite</h2>
<p>When only the current value matters (an order's status, a corrected email), update the row in place. MERGE on the business key makes it safe to run twice: the same change applied again changes nothing. A <code>row_hash</code> of the tracked columns skips rows that didn't really change.</p>
{code(scd1, "Delta Lake / Spark SQL.")}</section>

<section id="scd2"><p class="eyebrow">History: Type 2</p><h2>SCD Type 2: keep every version</h2>
<p>When history matters (which city a customer lived in when they ordered), a change closes the current row and opens a new one. One MERGE does both, using a well-known trick: changed rows are sent twice, once with the key (to close the old version) and once without (so it is inserted as the new version).</p>
{code(scd2, "Delta Lake / Spark SQL. staged_customer has one row per customer_id, with changed_at = when the change happened in the source.")}
{code(scd2rows, "Asha (C-77) moves from Pune to Sydney on 15 November. Last year's orders still join to Pune.")}
<h3>What makes Type 2 hard</h3>
<ul><li><b>Two changes for one key in one batch:</b> the MERGE above takes one row per key. Apply the changes in order (one MERGE per sequence step), or collapse them and lose the in-between version on purpose.</li>
<li><b>Changes out of order:</b> use the source's change time, never the load time, for <code>valid_from</code>; a late, older change must slot into the past, not become 'current'.</li>
<li><b>No-op updates:</b> compare <code>row_hash</code>, or every touch of a row opens a new version.</li>
<li><b>Deletes:</b> close the current row and mark it deleted (a soft delete), so history stays.</li>
<li><b>The guarantee to test:</b> exactly one current row per key, and no overlapping valid ranges.</li></ul>
<p>More: <a href="/concepts/scd/">slowly changing dimensions</a>, <a href="/concepts/idempotency/">idempotency</a>.</p></section>

<section id="problems"><p class="eyebrow">What goes wrong</p><h2>Common problems</h2>
{problems([
        ("Two current rows for one customer", "Reports double-count; joins fan out.", "Pick one at random in the query.", "Close and open in one MERGE; test 'one current row per key' after every run."),
        ("A column renamed upstream", "The silver column goes all null overnight.", "Map the new name by hand in production.", "The contract check fails the hop and quarantines; the mapping is fixed in the manifest by pull request."),
        ("Bad rows silently dropped", "Totals are a little low and nobody knows why.", "A WHERE clause that filters them out.", "Quarantine with a reason; reconcile counts: bronze = silver + quarantine."),
        ("Re-running adds rows", "A retried job inserts the batch again.", "Delete the batch by hand, then re-run.", "MERGE on the business key; INSERT never appears in silver code.")])}
</section>"""
    plat = table(["Job", "AWS", "Azure", "Google Cloud", "Databricks", "Open source"], [
        ("Transform engine", "Glue or EMR Spark; dbt on Athena", "Fabric Spark; dbt on Fabric", "Dataproc; Dataform or dbt on BigQuery", "Lakeflow Declarative Pipelines or jobs", "PySpark; dbt + DuckDB"),
        ("MERGE / upsert", "Iceberg MERGE", "Delta MERGE", "BigQuery MERGE", "Delta MERGE; AUTO CDC (formerly APPLY CHANGES) for SCD", "Delta or Iceberg MERGE"),
        ("Contract and quality checks", "Glue Data Quality", "Purview data quality", "Dataplex data quality", "Pipeline expectations", "Great Expectations or Soda"),
        ("Masking", "Lake Formation", "Purview + SQL masking", "Policy tags", "Unity Catalog column masks", "views per role")])
    qa = [("Should silver be modelled as a star schema?", "No: silver is one clean row per real thing, close to the source's entities. Shaping for questions (facts and dimensions) is gold's job."),
          ("SCD Type 1 or Type 2?", "Type 2 where history changes the meaning of past numbers (a customer's region, a product's category). Type 1 where only the current value matters or the old one was simply wrong."),
          ("Where do quality checks run?", "The contract is enforced at this hop, before rows reach silver. Gold adds reconciliation."),
          ("Can I use AUTO CDC (APPLY CHANGES) instead of writing MERGE?", "Yes on Databricks: Lakeflow Declarative Pipelines' AUTO CDC, formerly called APPLY CHANGES, handles Type 1 and Type 2, including out-of-order changes ordered by a sequence column. The rules on this page still apply.")]
    return "bronze-to-silver", "Bronze to silver: clean, dedupe, keep history", "The bronze-to-silver hop: common transformations, quarantine, dedupe by key, SCD Type 1 and Type 2 with MERGE, and the traps that make history hard.", body, plat, qa


# ======================================================================= gold
def gold():
    fact = """
-- Grain: one row per order line. Rebuilt per day, so re-running a day replaces it exactly.
INSERT OVERWRITE gold.fact_sales PARTITION (order_date = '2026-10-27')
SELECT                                              -- order_date is fixed by PARTITION (...), so it is not selected
  COALESCE(c.customer_sk, -1)  AS customer_sk,     -- -1 = inferred member (customer not arrived yet)
  p.product_sk,
  o.order_id, o.line_no, o.quantity, o.amount_inr
FROM silver.order_lines o
LEFT JOIN silver.customer c                         -- point-in-time join to the SCD2 version
  ON  c.customer_id = o.customer_id
  AND o.placed_at >= c.valid_from
  AND (c.valid_to IS NULL OR o.placed_at < c.valid_to)
JOIN gold.dim_product p ON p.product_id = o.product_id AND p.is_current
WHERE o.order_date = '2026-10-27';"""
    recon = """
SELECT
  (SELECT count(*)        FROM silver.order_lines WHERE order_date = '2026-10-27') AS silver_rows,
  (SELECT count(*)        FROM gold.fact_sales     WHERE order_date = '2026-10-27') AS gold_rows,
  (SELECT sum(amount_inr) FROM silver.order_lines WHERE order_date = '2026-10-27') AS silver_amount,
  (SELECT sum(amount_inr) FROM gold.fact_sales     WHERE order_date = '2026-10-27') AS gold_amount;
-- fail the run if rows differ, or amounts differ by more than the agreed tolerance"""
    body = f"""
<section id="plain"><p class="eyebrow">In plain words</p><h2>Tables built for the questions people ask</h2>
<p>Silver says what happened, one clean row per thing. Gold arranges it for a purpose: "how much did we sell, by store and month?", "which customers are at risk?", "what goes on the board report?". The classic shape is a <b>star</b>: a fact table of events with numbers, surrounded by dimension tables that describe them.</p>
<figure class="diagram">{here(["Silver", "Gold"])}<figcaption>Gold is built from silver only, never from bronze.</figcaption></figure></section>

<section id="grain"><p class="eyebrow">Step 1</p><h2>Say the grain first</h2>
<p>The grain is one sentence: what one row of the fact table means. "One row per order line." "One row per customer per day." Every column must be true at that grain, and every number must add up correctly at it. Most gold bugs are grain bugs: a join that turns one order line into three.</p></section>

<section id="star"><p class="eyebrow">Step 2</p><h2>Facts and dimensions</h2>
{table(["Table", "Holds", "Key"], [("fact_sales", "One row per order line: quantity, amount", "keys to each dimension + order id and line"), ("dim_customer", "Who: name, city, segment, with history from silver's SCD2", "customer_sk (surrogate key)"), ("dim_product", "What: name, category, brand", "product_sk"), ("dim_store", "Where: store, city, region", "store_sk"), ("dim_date", "When: day, week, month, holiday, fiscal period", "date_key")])}
<p>A <b>surrogate key</b> is a number made by the platform for each version of a dimension row, so the fact joins to the right version even after the customer moves city. <b>Conformed</b> dimensions are shared: the same dim_customer serves sales, returns and marketing, so 'customer' means one thing everywhere. See <a href="/concepts/dimensional/">star schema</a>.</p></section>

<section id="build"><p class="eyebrow">Step 3</p><h2>Build it so it can run twice</h2>
{code(fact, "Spark SQL. Overwriting one day's partition makes the rebuild idempotent: run it twice, get the same rows once.")}
<ul><li><b>Point-in-time join:</b> the order joins to the customer version that was valid when it was placed.</li>
<li><b>Inferred members:</b> if the order arrives before its customer, it joins to a placeholder (-1) instead of disappearing; when the customer arrives, the next rebuild fixes it.</li>
<li><b>Only from silver:</b> gold never reads bronze, so it inherits every check silver passed.</li></ul></section>

<section id="recon"><p class="eyebrow">Step 4</p><h2>Reconcile every run</h2>
{code(recon)}
<p>Counts and sums must agree with silver, and silver with the source (minus quarantine), within an agreed tolerance. When they don't, the run fails and names the hop where they diverged.</p></section>

<section id="products"><p class="eyebrow">Beyond the star</p><h2>Marts, aggregates and data products</h2>
<ul><li><b>Aggregates</b> (daily sales by store) make dashboards fast; they are rebuilt from the fact, never edited.</li>
<li><b>Marts</b> are subject areas for one team, built from the shared facts and dimensions.</li>
<li><b>Data products</b> are gold tables published for others with an owner, a contract, a freshness promise and documentation.</li>
<li>Metric definitions (what 'net revenue' means) go one level up, into the <a href="/concepts/semantic-layer/">semantic layer</a>, not into each dashboard.</li></ul></section>

<section id="problems"><p class="eyebrow">What goes wrong</p><h2>Common problems</h2>
{problems([
        ("The fan-out join", "Revenue triples after a new dimension is joined in.", "Add DISTINCT until it looks right.", "State the grain; make sure every dimension key is unique for the join (test it); join at the grain."),
        ("Orders vanish from the report", "A late customer feed means the inner join drops new orders.", "Wait for all feeds before building.", "Inferred member (-1) with a left join; count placeholders and alert if they don't clear."),
        ("Last year's numbers change", "A customer moved city and history was rewritten.", "Freeze a copy of last year.", "SCD2 in silver and a point-in-time join in gold."),
        ("A day loaded twice", "Gold totals are double for one day.", "Delete by hand.", "Overwrite by partition (or MERGE) and reconcile against silver every run.")])}
</section>"""
    plat = table(["Job", "AWS", "Azure", "Google Cloud", "Databricks", "Open source"], [
        ("Modelling", "dbt on Redshift or Athena", "dbt on Fabric, Fabric Warehouse", "Dataform or dbt on BigQuery", "dbt or Lakeflow Declarative Pipelines", "dbt + DuckDB"),
        ("Gold tables", "Redshift, Iceberg on S3", "Fabric Warehouse / Lakehouse", "BigQuery", "Delta in Unity Catalog", "Delta, DuckDB, Postgres"),
        ("Semantic layer", "dbt semantic layer", "Power BI semantic models", "Looker", "Metric views", "Cube Core"),
        ("Dashboards", "QuickSight", "Power BI", "Looker", "AI/BI dashboards", "Superset or Metabase")])
    qa = [("Do I always need a star schema in gold?", "No, but it is the safest default for analytics. Wide, flat tables are fine for a single dashboard or ML features, as long as they are built from the shared facts and dimensions."),
          ("Where do surrogate keys come from?", "The platform makes them when it builds the dimension, one per version of a row. Don't reuse the source system's id as the dimension key once you keep history."),
          ("Should gold be views or tables?", "Tables for anything large or used often (rebuilt by partition); views for thin, cheap layers on top."),
          ("How is gold different from the semantic layer?", "Gold holds the tables. The semantic layer holds the definitions on top of them (metrics, joins, names), so every tool computes 'revenue' the same way.")]
    return "gold", "Gold: shaped for the business", "Building gold: state the grain, facts and dimensions, surrogate keys, point-in-time joins, inferred members, idempotent rebuilds and reconciliation.", body, plat, qa


def render(slug, title, desc, body, plat, qa):
    url = f"{SITE}{BASE}{slug}/"
    full = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › <a href="{BASE}">Data platform architecture</a> › {E(SHORT[slug])}</p>
<p class="eyebrow" style="margin-top:22px">Data platform architecture · component · the same on every platform</p>
<h1>{E(title)}</h1>
<p class="lede">{E(desc)}</p>{siblings(slug)}
{body}
<section id="platforms"><p class="eyebrow">Concept vs product</p><h2>On each platform</h2>{plat}<p class="note">Product names change often; check the current docs before you build.</p></section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{faq(qa)}</section>
<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2>
<p><a href="{BASE}">↑ The whole picture</a> · <a href="/learn/medallion-architecture/">The medallion layers</a> · <a href="/concepts/#data-engineering">Key concepts</a> · <a href="/paths/data-engineering/">The Data Engineering path</a></p>
{siblings(slug)}
<p class="note" style="margin-top:12px">Coming soon: this component as a simulation you can run and break.</p></section>"""
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": title, "description": desc, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": "2026-10-27", "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Learn", "item": f"{SITE}/learn/"},
              {"@type": "ListItem", "position": 2, "name": "Data platform architecture", "item": f"{SITE}{BASE}"},
              {"@type": "ListItem", "position": 3, "name": SHORT[slug], "item": url}]}]
    head = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    d = desc if len(desc) <= 158 else desc[:155].rsplit(" ", 1)[0] + "…"
    return wb.page(title, d, url, full, head)


def main():
    for fn in (metadata_store, ingestion, bronze_to_silver, gold):
        slug, title, desc, body, plat, qa = fn()
        out = ROOT / "learn" / "data-platform-architecture" / slug
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(render(slug, title, desc, body, plat, qa))
        print("component ->", out)


if __name__ == "__main__":
    main()
