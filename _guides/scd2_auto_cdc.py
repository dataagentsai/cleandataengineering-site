"""SCD Type 2: AUTO CDC or our own PySpark? One page at /learn/scd2-auto-cdc-vs-pyspark/.

    python3 _guides/scd2_auto_cdc.py      (then python3 _site/nav.py and python3 _site/seo.py)

Teach first (what SCD2 keeps, the four input shapes), then the decision with verdicts, AUTO CDC code
for CDC, change-feed and snapshot input, our own writer (one writer, adapters per input) with
table-driven tests, what AUTO CDC gives you that own code must earn, cost with a calculator.

The own-PySpark code is read from _guides/code/scd2/ so the page shows exactly what was run:
11 table-driven tests plus an end-to-end run (CDC stream, replay, snapshots, change data feed) on
Spark 3.5.1 + Delta 3.2.0 on 2026-11-11. The AUTO CDC code is Lakeflow pipeline syntax and was not
run here (needs a Databricks workspace). AWS prices come from _tools/dbx_cost/prices.json; Azure
prices are our estimates.
"""
import json
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "_paths"))
import components as C  # noqa: E402
from bi_choice import ar, bx, svg, t, vtable  # noqa: E402

wb = C.wb
SITE = wb.SITE
URL_PATH = "/learn/scd2-auto-cdc-vs-pyspark/"
DATE = "2026-11-11"
TITLE = "SCD Type 2 on Databricks: AUTO CDC or our own PySpark?"
DESC = ("How to build SCD Type 2 history on Databricks when the input is CDC and when it is a full snapshot: "
        "Lakeflow AUTO CDC vs a hand-written PySpark MERGE, clean tested code for both, what each handles, and the cost.")
CODE = Path(__file__).parent / "code" / "scd2"
PRICES = json.loads((ROOT / "_tools" / "dbx_cost" / "prices.json").read_text())["dbu"]

CSS = C.CSS + """<style>
  .ac .fig { border:var(--line); border-radius:var(--wob); padding:12px 14px; margin:16px 0; background:#fff; overflow-x:auto; }
  .ac .fig svg { width:100%; min-width:680px; height:auto; display:block; } .ac .fig text { font-family:var(--hand); fill:#111; }
  .ac .fig p { font-size:13.5px; color:var(--muted); margin:6px 0 0; }
  .ac .box { border:var(--line); border-radius:var(--wob); padding:10px 16px; margin:14px 0; background:var(--butter-wash); }
  .ac .warn { border:var(--line); border-radius:var(--wob); padding:10px 16px; margin:14px 0; background:var(--rose-wash); }
  .ac table.t td { font-size:14px; } .ac td.v { font-weight:700; }
  .ac .calc { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1.2fr); gap:22px; margin:14px 0; }
  @media (max-width:760px) { .ac .calc { grid-template-columns:1fr; } }
  .ac .in { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px 12px; align-content:start; }
  .ac .in label { display:grid; gap:3px; font-size:13px; color:var(--muted); }
  .ac .in input, .ac .in select { font:15px ui-monospace,Menlo,monospace; padding:5px 8px; border:var(--line); border-radius:8px; background:#fff; color:#111; width:100%; box-sizing:border-box; }
  .ac .in .g { grid-column:1/-1; font-weight:700; color:#111; margin-top:4px; }
  .ac .res { border:var(--line); border-radius:var(--wob); padding:10px 14px; margin-bottom:10px; background:#fff; }
  .ac .res .top { display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap; }
  .ac .res .amt { font:700 19px ui-monospace,Menlo,monospace; font-variant-numeric:tabular-nums; }
  .ac .res .sub { font-size:13px; color:var(--muted); }
  .ac .res .bar { height:7px; border-radius:4px; background:#f1f1f1; margin-top:7px; overflow:hidden; }
  .ac .res .bar i { display:block; height:100%; }
  .ac .res.auto .bar i { background:#A3B5DF; } .ac .res.own .bar i { background:#FFD98A; }
  .ac .low { font-size:12px; border:var(--line); border-radius:999px; padding:0 8px; background:var(--mint-wash, #eaf6ef); }
</style>"""


def fig(d, cap):
    return f'<div class="fig">{d}<p>{E(cap)}</p></div>'


def src(name):
    return (CODE / name).read_text()


# ------------------------------------------------------------------ drawings
def d_history():
    i = t(500, 24, "customer 42 over one year", 17, "middle")
    rows = [("Pune", "4 Jan", "19 May", "w"), ("Mumbai", "19 May", "2 Sep", "w"), ("Delhi", "2 Sep", "1 Nov", "w")]
    for k, (city, f, to, c) in enumerate(rows):
        i += bx(60 + k * 300, 46, 260, 56, [f"42 · {city}", f"from {f} · to {to}"], c, 15)
    i += ar(320, 74, 358, 74) + ar(620, 74, 658, 74)
    i += bx(380, 130, 260, 44, ["1 Nov: deleted in source"], "r", 14) + ar(790, 104, 600, 128, True)
    i += t(500, 200, "nothing is overwritten: each change closes one row and opens the next", 14, "middle")
    return svg(1000, 212, "SCD Type 2 for customer 42: a Pune row from 4 January to 19 May, a Mumbai row to 2 September, a Delhi row to 1 November, when the customer was deleted in the source and no new row opened.", i)


def d_shapes():
    ins = [("CDC feed", "Debezium, SAP SLT, DMS"), ("Delta table we own", "change data feed"),
           ("Full snapshot", "daily extract, files"), ("updated_at pull", "JDBC incremental")]
    i = ""
    for k, (a, b) in enumerate(ins):
        y = 14 + k * 66
        i += bx(10, y, 230, 54, [a, b], "b" if k < 2 else "y", 14) + ar(240, y + 27, 368, 150)
    i += bx(370, 110, 240, 80, ["change events", "key · op · order · values"], "g", 15)
    i += ar(610, 135, 700, 80) + ar(610, 165, 700, 220)
    i += bx(702, 46, 280, 64, ["AUTO CDC", "(Lakeflow pipeline)"], "l", 15)
    i += bx(702, 190, 280, 64, ["our SCD2 writer", "(PySpark MERGE)"], "y", 15)
    i += t(500, 292, "turn every input into change events first; then SCD2 is the same problem every time", 14, "middle")
    return svg(1000, 302, "Four input shapes (CDC feed, a Delta table's change data feed, a full snapshot, an updated_at pull) all become change events with a key, an operation, an ordering value and the attributes. Those events feed either AUTO CDC in a Lakeflow pipeline or our own PySpark SCD2 writer.", i)


def d_writer():
    i = ""
    for k, (a, b) in enumerate([("run_cdc()", "stream, foreachBatch"), ("change_feed_events()", "Delta CDF to events"), ("snapshot_to_events()", "hash compare to events")]):
        y = 16 + k * 70
        i += bx(10, y, 250, 56, [a, b], "b", 14) + ar(260, y + 28, 338, 116)
    i += bx(340, 76, 250, 80, ["plan_scd2()", "pure: skip late, drop no-ops,", "build versions"], "y", 14)
    i += ar(590, 116, 650, 116)
    i += bx(652, 76, 170, 80, ["apply_scd2()", "one MERGE"], "y", 14) + ar(822, 116, 872, 116)
    i += bx(874, 76, 116, 80, ["dim table", "Delta"], "g", 14)
    i += t(465, 196, "tested with 11 table rows, no Delta needed", 13, "middle")
    return svg(1000, 230, "Our own design: three adapters (CDC stream, Delta change feed, snapshot compare) feed one pure planning function, plan_scd2, which skips late events, drops no-op changes and builds versions; apply_scd2 then runs one Delta MERGE into the dimension table.", i)


# ------------------------------------------------------------------ content
SHAPES = [
    ("CDC feed", "Debezium on Kafka or MSK, SAP SLT, AWS DMS, ADF CDC, Fivetran", "Already events. Order by commit time plus log position.", "Yes"),
    ("Delta table we own", "Silver tables, other teams' Delta tables", "Turn on delta.enableChangeDataFeed and read the change feed; order by _commit_version.", "Yes"),
    ("Full snapshot", "SAP table extracts, daily files, JDBC full loads", "Compare with the open rows by hash: new key = insert, different hash = update, missing key = delete.", "Yes, by absence"),
    ("Pull by updated_at", "JDBC 'where updated_at > last run'", "Each row is an update event, ordered by updated_at.", "No: add a periodic full key-list compare"),
]

DECIDE = [
    ("CDC", "Already on Lakeflow pipelines, or happy to adopt them", "AUTO CDC", "Pursue: ordering, deletes and duplicates handled; no SCD code to own"),
    ("CDC", "Jobs-only team, very high volume, cost-sensitive", "Own PySpark MERGE", "Pursue: lower DBU rate; only with the table-driven tests below"),
    ("CDC", "Custom rules: business-date effective dates, rewriting history in the middle of the timeline", "Own PySpark MERGE", "Pursue: AUTO CDC orders by one SEQUENCE BY value"),
    ("Snapshot", "Source is a Delta table we control", "Change data feed, then AUTO CDC", "Pursue: reads only changed rows"),
    ("Snapshot", "Full extract, small to medium table", "AUTO CDC FROM SNAPSHOT", "Pursue: simple and correct; Python only"),
    ("Snapshot", "Full extract, hundreds of millions of rows", "Own hash compare", "Pursue: compare only the partitions that changed"),
    ("Any", "A hand-written SCD2 notebook per source table", "None", "Drop: the same bugs fixed many times over"),
]

GAPS = [
    ("Events out of order", "Reorders by SEQUENCE BY, including events older than the current row (history rewritten correctly)", "Skips events not newer than what is applied; rewriting history mid-timeline needs extra code"),
    ("Several changes per key in one batch", "Handled", "Handled with lag and lead (test 'two changes in one batch')"),
    ("Deletes, delete then re-insert", "APPLY AS DELETE WHEN, plus tombstones for late deletes", "Handled (tests 6, 7, 10, 11); no tombstones"),
    ("Changes to untracked columns", "TRACK HISTORY ON ... EXCEPT updates them in place", "Ignored; extend apply_scd2 with an in-place update if needed"),
    ("Re-running a failed batch", "Pipeline checkpoint", "Safe through the sequence check, also for deleted keys (tests 9, 10)"),
    ("Schema changes", "Supported in pipelines", "We add columns ourselves"),
    ("Who can change the target", "The pipeline owns it; outside DML is limited", "A plain Delta table"),
    ("Full refresh", "History lost if bronze no longer holds it; set pipelines.reset.allowed = false", "No such switch; a rebuild is our own job"),
    ("Custom effective dates", "One ordering column", "Anything we can code"),
]

WORK = [
    ("CDC feed or change data feed", "Only new events, plus the matching target rows", "Same for both tools. Cluster the target on the key."),
    ("Full snapshot", "The whole snapshot plus the target, every run", "The biggest cost driver. Turn it into a change feed where you can; with own code, compare only changed partitions."),
    ("Pull by updated_at", "Changed rows, plus a weekly key-list compare for deletes", "Cheap, if the source really sets the timestamp."),
]

CHECK = [
    ("Ordering value", "Unique per key: commit time alone can tie, so add the log position (LSN) or commit version."),
    ("Protect AUTO CDC history", "pipelines.reset.allowed = false on the target; keep bronze as long as you might rebuild."),
    ("Noisy columns", "Exclude last-login or extract timestamps from tracking, or every run makes a new version."),
    ("Layout", "Cluster the target on the key and is_current so each MERGE touches few files; turn on deletion vectors."),
    ("Partial snapshots", "A partial extract must never read as 'everything else was deleted': check row counts before applying."),
    ("One valid_to convention", "NULL or 9999-12-31, the same everywhere, so Power BI and others filter the same way."),
    ("Tests in CI", "The table-driven tests run on every change to the writer."),
]

QA = [
    ("Should I use AUTO CDC or write my own SCD Type 2 MERGE?", "If the input is CDC and you can run Lakeflow pipelines, use AUTO CDC: it handles out-of-order events, deletes and duplicates. Write your own when you run only plain jobs at high volume, or need rules AUTO CDC cannot express. Then build one tested writer with an adapter per input type."),
    ("How do I build SCD2 from a full snapshot instead of CDC?", "If the source is a Delta table you own, turn on its change data feed and treat it as CDC. Otherwise compare the snapshot with the open target rows by a hash of the tracked columns: new keys are inserts, changed hashes are updates, missing keys are deletes. AUTO CDC FROM SNAPSHOT does this for you in Python pipelines."),
    ("Is AUTO CDC the same as APPLY CHANGES?", "Yes. APPLY CHANGES INTO was renamed AUTO CDC INTO when Delta Live Tables became Lakeflow Declarative Pipelines; the Python function is now create_auto_cdc_flow, and apply_changes_from_snapshot is create_auto_cdc_from_snapshot_flow."),
    ("Does AUTO CDC cost more?", "On classic compute it needs the Pro pipeline tier, about a third more per DBU than plain jobs compute on AWS list prices. The VM cost is the same, so the total gap is smaller, and often less than the engineering time to own the code. Serverless jobs and serverless pipelines are billed at the same rate."),
    ("Can a full refresh delete my SCD2 history?", "Yes, for an AUTO CDC target: a full refresh rebuilds from the source, and if bronze no longer holds all events, the history is gone. Set pipelines.reset.allowed = false on the target table."),
    ("How do I make a hand-written SCD2 MERGE safe to re-run?", "Skip any event whose ordering value is not newer than the latest point already applied for that key, counting closed rows too, so a deleted key is not brought back. The tests on this page cover replay, late events and replay after delete."),
]

SOURCES = [
    ("Databricks: AUTO CDC APIs (SCD Type 1 and 2)", "https://docs.databricks.com/aws/en/dlt/cdc"),
    ("Databricks: AUTO CDC INTO (SQL reference)", "https://docs.databricks.com/aws/en/dlt-ref/dlt-sql-ref-apply-changes-into"),
    ("Databricks: create_auto_cdc_from_snapshot_flow", "https://docs.databricks.com/aws/en/dlt-ref/dlt-python-ref-apply-changes-from-snapshot"),
    ("Delta Lake: change data feed", "https://docs.delta.io/latest/delta-change-data-feed.html"),
    ("Delta Lake: MERGE (upsert) and SCD Type 2 example", "https://docs.delta.io/latest/delta-update.html"),
]

AUTO_SQL = """CREATE OR REFRESH STREAMING TABLE dim_customer
  TBLPROPERTIES ('pipelines.reset.allowed' = 'false');   -- protect history from a full refresh

CREATE FLOW dim_customer_scd2 AS AUTO CDC INTO dim_customer
FROM STREAM(bronze.customer_cdc)
KEYS (customer_id)
APPLY AS DELETE WHEN op = 'D'
SEQUENCE BY commit_ts                          -- or struct(commit_ts, lsn) to break ties
COLUMNS * EXCEPT (op, commit_ts, _rescued_data)
STORED AS SCD TYPE 2
TRACK HISTORY ON * EXCEPT (last_login_ts);       -- noisy columns update in place"""

AUTO_PY = """from pyspark import pipelines as dp
from pyspark.sql.functions import col, expr

@dp.view
def customer_cdc():
    return spark.readStream.table("bronze.customer_cdc")

dp.create_streaming_table("dim_customer", table_properties={"pipelines.reset.allowed": "false"})

dp.create_auto_cdc_flow(
    target="dim_customer",
    source="customer_cdc",
    keys=["customer_id"],
    sequence_by=col("commit_ts"),
    apply_as_deletes=expr("op = 'D'"),
    except_column_list=["op", "commit_ts", "_rescued_data"],
    stored_as_scd_type=2,
    track_history_except_column_list=["last_login_ts"],
)"""

AUTO_CDF = """ALTER TABLE silver.material SET TBLPROPERTIES (delta.enableChangeDataFeed = true);

-- In the pipeline: drop pre-images, then feed AUTO CDC as above with SEQUENCE BY _commit_version
CREATE TEMPORARY VIEW material_changes AS
SELECT *, CASE _change_type WHEN 'delete' THEN 'D' ELSE 'U' END AS op
FROM STREAM(silver.material) WITH (readChangeFeed = true)
WHERE _change_type != 'update_preimage';"""

AUTO_SNAP = """from pyspark import pipelines as dp

dp.create_streaming_table("dim_material")

# Each pipeline update reads the latest full snapshot and compares it with the target.
dp.create_auto_cdc_from_snapshot_flow(
    target="dim_material",
    source="bronze.sap_mara_snapshot",
    keys=["material_id"],
    stored_as_scd_type=2,
    track_history_except_column_list=["extract_ts"],
)
# For a backfill from many dated snapshots, pass a function instead of a table name:
# it gets the last processed version and returns (next_df, next_version) or None."""

DDL = """CREATE TABLE gold.dim_customer (
  customer_id BIGINT, name STRING, email STRING, city STRING, segment STRING,
  row_hash STRING, valid_from TIMESTAMP, valid_to TIMESTAMP, is_current BOOLEAN
)
CLUSTER BY (customer_id, is_current)                    -- MERGE reads only matching files
TBLPROPERTIES ('delta.enableDeletionVectors' = 'true');  -- cheaper closes"""

E2E_OUT = """after CDC batch 2 (42 moves then is deleted; 7 gets a late event; 9 gets a no-op)
customer_id city    segment valid_from  valid_to    is_current
7           Chennai sme     2026-02-01  NULL        true        <- late Madurai event skipped
9           Goa     retail  2026-03-01  NULL        true        <- no-op ignored
42          Pune    retail  2026-01-04  2026-05-19  false
42          Mumbai  retail  2026-05-19  2026-09-02  false
42          Delhi   retail  2026-09-02  2026-11-01  false       <- closed by the delete
replay the whole CDC source -> rows before 5, after 5

after 3 daily snapshots, then day 3 again
1           Pune    retail  2026-11-01  2026-11-03  false       <- missing on day 3 = deleted
2           Goa     sme     2026-11-01  2026-11-02  false
2           Goa     corp    2026-11-02  NULL        true
3           Delhi   retail  2026-11-02  NULL        true
re-run day 3 -> rows before 4, after 4

change data feed: insert (v1), update (v2), delete (v3)
5           Pune    retail  1           2           false
5           Delhi   retail  2           3           false"""


def rate(k):
    return PRICES[k]["premium"]


CLOUDS = {
    "aws": {"label": "AWS (list, us-east-1, Premium)", "jobs": rate("jobs_classic"), "pro": rate("dlt_pro"), "srv": rate("jobs_serverless"), "vm": 0.30},
    "azure": {"label": "Azure (our estimate, Premium)", "jobs": 0.30, "pro": 0.38, "srv": 0.45, "vm": 0.35},
}

CALC = """<div class="calc">
<form class="in" id="ac-calc" onsubmit="return false">
  <label class="g" for="ac-cloud">Cloud<select id="ac-cloud"><option value="aws">AWS</option><option value="azure">Azure</option></select></label>
  <span class="g">Workload</span>
  <label for="ac-tables">Tables<input id="ac-tables" type="number" min="1" value="20"></label>
  <label for="ac-runs">Runs per day<input id="ac-runs" type="number" min="1" value="24"></label>
  <label for="ac-dbu">DBU per table per run<input id="ac-dbu" type="number" step="0.05" min="0" value="0.5"></label>
  <label for="ac-ovh">Classic start-up and idle, percent<input id="ac-ovh" type="number" min="0" value="25"></label>
  <span class="g">Rates, $ (filled by cloud, editable)</span>
  <label for="ac-jobs">Jobs compute per DBU<input id="ac-jobs" type="number" step="0.01"></label>
  <label for="ac-pro">Pipeline Pro per DBU<input id="ac-pro" type="number" step="0.01"></label>
  <label for="ac-srv">Serverless per DBU<input id="ac-srv" type="number" step="0.01"></label>
  <label for="ac-vm">Classic VM cost per DBU<input id="ac-vm" type="number" step="0.01"></label>
  <span class="g">Engineering, first year</span>
  <label for="ac-eown">Own code: days to build and maintain<input id="ac-eown" type="number" min="0" value="18"></label>
  <label for="ac-eauto">AUTO CDC: days<input id="ac-eauto" type="number" min="0" value="5"></label>
  <label for="ac-day">Cost per engineer-day<input id="ac-day" type="number" min="0" value="400"></label>
</form>
<div id="ac-out" aria-live="polite"></div>
</div>
<script>
(function(){
  var C = %s;
  var $ = function(id){ return document.getElementById(id); };
  var v = function(id){ var n = parseFloat($(id).value); return isNaN(n) ? 0 : n; };
  var m = function(n){ return '$' + Math.round(n).toLocaleString('en-US'); };
  function fill(){ var c = C[$('ac-cloud').value]; $('ac-jobs').value = c.jobs; $('ac-pro').value = c.pro; $('ac-srv').value = c.srv; $('ac-vm').value = c.vm; }
  function calc(){
    var runs = v('ac-tables') * v('ac-runs') * 30, dbu = v('ac-dbu'), o = 1 + v('ac-ovh') / 100, vm = v('ac-vm'), day = v('ac-day');
    var rows = [
      ['Own PySpark, classic jobs', 'own', dbu * o * (v('ac-jobs') + vm), v('ac-eown')],
      ['AUTO CDC, classic pipeline Pro', 'auto', dbu * o * (v('ac-pro') + vm), v('ac-eauto')],
      ['Own PySpark, serverless jobs', 'own', dbu * v('ac-srv'), v('ac-eown')],
      ['AUTO CDC, serverless pipeline', 'auto', dbu * v('ac-srv'), v('ac-eauto')]
    ].map(function(r){ var mo = r[2] * runs; return {n:r[0], c:r[1], mo:mo, eng:r[3]*day, yr:mo*12 + r[3]*day}; });
    var max = Math.max.apply(null, rows.map(function(r){ return r.yr; })) || 1;
    var best = rows.reduce(function(a,b){ return b.yr < a.yr ? b : a; });
    $('ac-out').innerHTML = rows.map(function(r){
      return '<div class="res ' + r.c + '"><div class="top"><b>' + r.n + (r === best ? ' <span class="low">lowest</span>' : '') +
        '</b><span class="amt">' + m(r.yr) + '</span></div><div class="sub">' + m(r.mo) + ' compute a month + ' + m(r.eng) +
        ' engineering, first year</div><div class="bar"><i style="width:' + (r.yr / max * 100).toFixed(1) + '%%"></i></div></div>';
    }).join('');
  }
  $('ac-cloud').addEventListener('change', function(){ fill(); calc(); });
  ['ac-tables','ac-runs','ac-dbu','ac-ovh','ac-jobs','ac-pro','ac-srv','ac-vm','ac-eown','ac-eauto','ac-day'].forEach(function(id){ $(id).addEventListener('input', calc); });
  fill(); calc();
})();
</script>"""


def page():
    url = f"{SITE}{URL_PATH}"
    aws, az = CLOUDS["aws"], CLOUDS["azure"]
    rates = C.table(["Compute", "AWS $/DBU", "Azure $/DBU (estimate)", "VM cost", "Runs"], [
        ("Jobs compute (classic)", f"{aws['jobs']:.2f}", f"{az['jobs']:.2f}", "extra, paid to the cloud", "Own PySpark"),
        ("Lakeflow pipeline Core (classic)", f"{rate('dlt_core'):.2f}", "0.30", "extra", "No AUTO CDC"),
        ("Lakeflow pipeline Pro (classic)", f"{aws['pro']:.2f}", f"{az['pro']:.2f}", "extra", "AUTO CDC"),
        ("Lakeflow pipeline Advanced (classic)", f"{rate('dlt_advanced'):.2f}", "0.54", "extra", "AUTO CDC plus expectations"),
        ("Serverless jobs and pipelines", f"{aws['srv']:.2f}", f"{az['srv']:.2f}", "included", "Either"),
    ])
    calc_cfg = json.dumps({k: {x: c[x] for x in ("jobs", "pro", "srv", "vm")} for k, c in CLOUDS.items()})
    srcs = "".join(f'<li><a href="{u}">{E(n)}</a></li>' for n, u in SOURCES)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/data-engineering/">Data engineering</a> › SCD2: AUTO CDC or own PySpark</p>
<p class="eyebrow" style="margin-top:22px">Data engineering · free guide · one page</p>
<h1>{E(TITLE)}</h1>
<p class="lede">Two ways to keep history of changing records on Databricks: let a Lakeflow pipeline do it with AUTO CDC, or write the MERGE ourselves. This page shows when each is right, for input that arrives as changes (CDC) and input that arrives as full snapshots, with clean code for both and what each costs.</p>
<div class="ac">
<div class="box"><b>Input is CDC:</b> use <b>AUTO CDC</b>. It handles events that arrive out of order, deletes and duplicate events, which is where hand-written SCD2 code usually goes wrong.<br>
<b>Input is not CDC:</b> if the source is a Delta table you own, turn on its change data feed so it <i>becomes</i> CDC. For true full extracts, <b>AUTO CDC FROM SNAPSHOT</b> is fine for small and medium tables; for very large ones our own hash compare can be cheaper because we choose what to compare.<br>
<b>Write our own</b> when the team runs only plain jobs at high volume, or needs rules AUTO CDC cannot express. Then build <b>one</b> tested SCD2 writer and give each input type a small adapter, never one SCD2 notebook per table.<br>
<b>Cost:</b> the per-DBU gap is usually smaller than the engineering time to own the code. What really moves the bill is how much each run reads, which the input shape decides, not the tool.</div>

<section id="plain"><p class="eyebrow">In plain words</p><h2>What SCD Type 2 keeps</h2>
<p>A Slowly Changing Dimension Type 2 never overwrites. When a tracked value changes, the current row is closed and a new one opened, and each row says when it was true: <code>valid_from</code>, <code>valid_to</code>, <code>is_current</code>. See <a href="/concepts/scd/">the SCD concept page</a>.</p>
{fig(d_history(), "One customer, three cities, then a delete. Facts join to the row valid on their own date.")}
<p>The hard cases every implementation must handle: two changes for one key in the same batch, an older event arriving after a newer one, a "change" that changes nothing we track, a delete, a delete then a re-insert, and a failed batch that runs again.</p></section>

<section id="inputs"><p class="eyebrow">Step 1</p><h2>Four input shapes, one idea</h2>
{fig(d_shapes(), "Whatever arrives, turn it into change events. After that, SCD2 is one problem, solved once.")}
{C.table(["Input you receive", "Typical source", "How it becomes change events", "Deletes?"], SHAPES)}</section>

<section id="decide"><p class="eyebrow">Step 2</p><h2>Which to use</h2>{vtable(["Input", "Situation", "Use", "Verdict"], DECIDE)}</section>

<section id="auto"><p class="eyebrow">Clean implementation 1</p><h2>AUTO CDC in a Lakeflow pipeline</h2>
<p>AUTO CDC is the new name for <code>APPLY CHANGES</code> in Lakeflow Declarative Pipelines (formerly Delta Live Tables). The target is a streaming table the pipeline owns; it adds <code>__START_AT</code> and <code>__END_AT</code> from the <code>SEQUENCE BY</code> value.</p>
<h3>Input is CDC, in SQL</h3>{C.code(AUTO_SQL, "Lakeflow pipeline SQL; needs a Databricks workspace, not run on this page.")}
<h3>Input is CDC, in Python</h3>{C.code(AUTO_PY, "Same flow in the Python API.")}
<h3>Input is a Delta table we own: turn on the change feed</h3>{C.code(AUTO_CDF)}
<h3>Input is a full snapshot (Python only)</h3>{C.code(AUTO_SNAP, "The snapshot flow reads the whole snapshot each update: without a change feed, comparing full key lists is the only way to see deletes.")}</section>

<section id="own"><p class="eyebrow">Clean implementation 2</p><h2>Our own PySpark: one writer, an adapter per input</h2>
<p>The writer only understands change events. Planning is a pure function from DataFrames to a DataFrame, so it is tested without Delta; the MERGE is a thin wrapper. Each input shape gets a small adapter.</p>
{fig(d_writer(), "Three adapters, one planning function, one MERGE.")}
<h3>The writer</h3>{C.code(src("scd2.py"), "Run on Spark 3.5.1 + Delta 3.2.0 on 2026-11-11.")}
<h3>The adapters</h3>{C.code(src("adapters.py"))}
<h3>Target table</h3>{C.code(DDL, "Delta DDL for Databricks; liquid clustering keeps each MERGE small.")}
<h3>What the end-to-end run printed</h3>{C.code(E2E_OUT, "From e2e.py: a CDC stream in two batches, a full replay, three daily snapshots plus a re-run, and a Delta change data feed. Columns trimmed for width; arrows are our notes.")}
<div class="warn"><b>A bug this run caught:</b> the first version checked late events only against <i>open</i> rows. A deleted customer has none, so replaying an old batch brought them back (5 rows became 8). The fix compares each event with the latest point applied for that key, closed rows included. Two test rows now guard it.</div></section>

<section id="tests"><p class="eyebrow">Proof</p><h2>Table-driven tests</h2>
<p>Because planning is pure, each hard case is one row. All 11 pass.</p>
{C.code(src("test_scd2.py"), "pytest, 11 passed on 2026-11-11. The Spark fixture is in conftest.py next to it.")}
<p>For the snapshot adapter, add a second table: unchanged row gives no event, changed row gives U, new key gives I, missing key gives D. See <a href="/learn/shift-left/">Shift left</a> for testing SCD2 without a cluster.</p></section>

<section id="gaps"><p class="eyebrow">Honest comparison</p><h2>What AUTO CDC gives you that own code must earn</h2>
{C.table(["Concern", "AUTO CDC", "Own PySpark (above)"], GAPS)}</section>

<section id="cost"><p class="eyebrow">Cost</p><h2>What it costs</h2>
<p>Three things make up the bill: the <b>DBU rate</b> of the compute type, the <b>amount of work</b> each run does (set by the input shape) and the <b>engineering time</b> to own the code. Pipelines cost more per DBU than plain jobs on classic compute; serverless is one rate for both and removes start-up and idle time.</p>
{rates}
<p class="cap">AWS rates are list prices from the site's price file (checked {E(PRICES['jobs_classic'].get('checked', ''))}); Azure rates are our estimates. Contract discounts change both: use your own price sheet.</p>
<h3>Where the work comes from</h3>{C.table(["Input shape", "Reads per run", "Cost lever"], WORK)}
<h3>Calculator</h3><p>The example is 20 dimensions loaded hourly. Change any number.</p>
{CALC % calc_cfg}
<p class="cap">Serverless rows assume the same DBU per run as classic; real serverless usage differs, so compare a week of system.billing.usage before deciding. Full model: <a href="/learn/data-systems/platform/cost/calculator/">the Databricks cost calculator</a>.</p></section>

<section id="check"><p class="eyebrow">Before going live</p><h2>Checklist</h2>{C.table(["Check", "Why"], CHECK)}</section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(QA)}</section>
<section id="sources"><p class="eyebrow">Sources</p><h2>Checked against</h2><ul>{srcs}</ul></section>
<section id="next"><p class="eyebrow">Related</p><h2>Where it connects</h2>
<p><a href="/concepts/scd/">Slowly changing dimensions</a> · <a href="/learn/data-platform-architecture/bronze-to-silver/">Bronze to silver, with SCD2 code</a> · <a href="/learn/time-travel-vs-scd2/">Time travel as SCD Type 2?</a> · <a href="/learn/delta-vs-iceberg/">Delta vs Iceberg (change data feed)</a> · <a href="/learn/streaming/">Streaming on AWS and Databricks</a> · <a href="/data-engineering/">All data engineering</a></p></section>
</div>"""
    crumbs = [("Data engineering", f"{SITE}/data-engineering/"), ("SCD2: AUTO CDC or own PySpark", url)]
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": TITLE, "description": DESC, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in QA]}]
    head = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(TITLE, DESC, url, body, head)


def main():
    out = ROOT / "learn" / "scd2-auto-cdc-vs-pyspark"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("scd2 auto cdc ->", out / "index.html")


if __name__ == "__main__":
    main()
