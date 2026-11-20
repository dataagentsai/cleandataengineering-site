"""Databricks interview prep: a hub and one page per topic at /learn/databricks-interview/.

    python3 _guides/databricks_interview.py      (then python3 _site/nav.py and python3 _site/seo.py)

Advanced Databricks for data engineering interviews, in plain words: what each command does, the
hard problems, how to answer. Pages that already exist on the site (declarative pipelines, metric
views, who maintains tables, Delta vs Iceberg) are linked, not repeated. Figures that change often
(limits, prices, preview status) are marked "check current docs" on the page.
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
BASE = "/learn/databricks-interview/"
DATE = "2026-11-20"
T = C.table
CODE = C.code
CSS = C.CSS + """<style>
  .tw { overflow-x:auto; } .fig { margin:16px 0; } .fig svg { width:100%; height:auto; max-width:1000px; } .fig p { font-size:13px; color:var(--faint); margin:4px 0 0; }
  .say { border:var(--line); border-radius:var(--wob); padding:10px 16px; background:var(--butter-wash,#fff4d6); margin:14px 0; } .say b { font-family:var(--hand); font-weight:400; font-size:20px; }
  .verify { font-size:13.5px; color:var(--faint); }
</style>"""

INK, BLUE, MINT, BUTTER, ROSE = "#1F1F1F", "#eef3fb", "#eaf6ef", "#fff4d6", "#fbeef3"
FILLS = [BLUE, MINT, BUTTER, ROSE]


def flow(labels, caption, label):
    """A row of boxes joined by arrows: the simple hand-drawn picture used on every page."""
    n = len(labels)
    w, gap = 1000 // n - 24, 24
    out = [f'<svg viewBox="0 0 1000 120" role="img" aria-label="{E(label)}"><defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker></defs>']
    for i, text in enumerate(labels):
        x = 12 + i * (w + gap)
        out.append(f'<rect x="{x}" y="26" width="{w}" height="68" rx="12" fill="{FILLS[i % 4]}" stroke="{INK}" stroke-width="1.5"/>')
        words, lines, cur = text.split(), [], ""
        for wd in words:
            if len(cur + " " + wd) > max(10, w // 9):
                lines.append(cur)
                cur = wd
            else:
                cur = (cur + " " + wd).strip()
        lines.append(cur)
        for j, ln in enumerate(lines[:3]):
            out.append(f'<text x="{x + w / 2}" y="{60 + (j - (len(lines[:3]) - 1) / 2) * 17}" text-anchor="middle" font-size="14.5" fill="{INK}">{E(ln)}</text>')
        if i < n - 1:
            out.append(f'<line x1="{x + w + 3}" y1="60" x2="{x + w + gap - 3}" y2="60" stroke="{INK}" stroke-width="1.5" marker-end="url(#a)"/>')
    out.append("</svg>")
    return f'<div class="fig">{"".join(out)}<p>{E(caption)}</p></div>'


def say(text):
    return f'<div class="say"><b>In an interview, say:</b> {E(text)}</div>'


def sec(id_, eyebrow, h2, html):
    return f'<section id="{id_}"><p class="eyebrow">{E(eyebrow)}</p><h2>{E(h2)}</h2>{html}</section>'


def ul(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def qlist(items):
    return "<ol>" + "".join(f"<li>{E(i)}</li>" for i in items) + "</ol>"


# ============================================================================ the pages
PAGES = []


def page_def(slug, title, short, desc, build):
    PAGES.append(dict(slug=slug, title=title, short=short, desc=desc, build=build))


# ---------------------------------------------------------------- 1. maintenance commands
def p_maintenance():
    rows = [
        ["OPTIMIZE", "Rewrites many small files into fewer big ones (about 1 GB target). Old files are marked removed but stay on disk.", "Delete anything. Change the data.", "Many small files from streaming or frequent appends."],
        ["OPTIMIZE … ZORDER BY", "Compaction plus putting rows with similar values of the chosen columns in the same files, so skipping works on several columns.", "Work incrementally (repeat runs get costlier). Help past 3 or 4 columns. Use partition columns.", "Older tables. New tables should use liquid clustering."],
        ["Liquid clustering (CLUSTER BY)", "Replaces partitioning and Z-order. Incremental: OPTIMIZE only touches data not yet clustered. Keys can change without rewriting the table. CLUSTER BY AUTO picks keys from query history.", "Combine with partitioning or ZORDER on the same table.", "Default for new tables, high-cardinality filters, skew, changing access patterns."],
        ["VACUUM", "Physically deletes files no longer referenced by the log and older than the retention period (7 days by default).", "Compact. Touch _delta_log.", "Storage cost control; GDPR physical deletion."],
        ["Optimized writes", "Shuffles before writing so each task writes fewer, bigger files.", "Fix files that already exist.", "Partitioned tables, MERGE-heavy jobs."],
        ["Auto compaction", "After a write, runs a small compaction on the files that write made.", "Replace a full OPTIMIZE.", "Streaming sinks you cannot schedule OPTIMIZE for."],
        ["Predictive Optimization", "Runs OPTIMIZE, VACUUM and ANALYZE for you on Unity Catalog managed tables when its cost model says it pays.", "Cover external tables.", "The default for managed tables."],
        ["ANALYZE TABLE … COMPUTE STATISTICS", "Computes table and column statistics for the query planner (join order, broadcast choice).", "Replace Delta's file-level min/max stats.", "Tables used in big joins."],
        ["Deletion vectors", "DELETE, UPDATE and MERGE mark rows as deleted in a side file instead of rewriting the whole file.", "Remove the rows physically.", "Cheap small updates."],
        ["REORG TABLE … APPLY (PURGE)", "Rewrites files that carry deletion vectors so deleted rows are really gone. Follow with VACUUM.", "Free space until VACUUM runs.", "Right to erasure (GDPR)."],
        ["RESTORE", "Moves the table back to an older version (a new commit).", "Work if the old files were vacuumed.", "Undo a bad write."],
        ["CLONE", "Shallow: copies metadata and points at source files. Deep: copies the data too.", "Keep a shallow clone alive if the source is vacuumed.", "Tests, backups, migration."],
    ]
    return (
        flow(["Write adds new files", "OPTIMIZE joins small files", "Old files still on disk", "VACUUM deletes them"], "OPTIMIZE makes the new files; VACUUM removes the old ones. Storage goes up in between.", "The life of files in a Delta table")
        + sec("model", "Start here", "One idea explains it all", "<p>A Delta table is Parquet files plus a transaction log. Every write adds new files and records \"add these, remove those\". Nothing is edited in place. So small files pile up (OPTIMIZE), old files pile up (VACUUM), and time travel works only while the old files and log entries still exist.</p>")
        + sec("commands", "Reference", "What each command does", T(["Command", "What it does", "What it does NOT do", "Use it when"], rows))
        + sec("retention", "Gotcha", "Time travel needs two things", "<p>The log entry (<code>delta.logRetentionDuration</code>, 30 days by default) and the data files (<code>delta.deletedFileRetentionDuration</code>, 7 days by default). Vacuuming at zero hours breaks time travel, long-running readers and streams that read older versions.</p>")
        + sec("conflicts", "Hard problem", "Concurrent writers and conflicts", "<p>Delta uses optimistic concurrency: two writers that touch the same files collide at commit (<code>ConcurrentAppendException</code>, <code>ConcurrentDeleteReadException</code>). Fixes: make writers touch disjoint data, put the partition or cluster predicate in the MERGE condition, use deletion vectors with row-level concurrency, retry with backoff. Do not lower the isolation level without knowing the trade-off.</p>")
        + sec("gdpr", "Hard problem", "Erasing a person from a huge table", "<p>DELETE with deletion vectors is only logical. Run REORG … APPLY (PURGE), then VACUUM past the retention period. Also cover derived copies: downstream tables, clones, backups and the change data feed. Cluster on the user key so the delete is cheap.</p>")
        + sec("ask", "Practice", "Questions to rehearse", qlist(["OPTIMIZE versus VACUUM: what does each do, and which frees storage?", "What happens if you VACUUM with retention 0?", "Z-order versus liquid clustering versus partitioning: when each?", "What are deletion vectors and what is the downside?", "Why can RESTORE fail?", "How do you fix ConcurrentAppendException?"]))
        + say("OPTIMIZE creates the new files, VACUUM removes the old ones, and neither changes the data. Never set VACUUM retention to zero in production."),
        [("Does OPTIMIZE delete old files?", "No. It marks them removed in the log. VACUUM deletes them after the retention period."),
         ("Can I partition and use liquid clustering together?", "No. Liquid clustering replaces partitioning and Z-order on a table."),
         ("Who runs these on managed tables?", "Predictive Optimization can run OPTIMIZE, VACUUM and ANALYZE for Unity Catalog managed tables. External tables need your own jobs.")])


page_def("delta-maintenance", "OPTIMIZE, VACUUM and compaction: what each does", "Maintenance commands",
         "OPTIMIZE, Z-order, liquid clustering, VACUUM, auto compaction, deletion vectors, REORG, RESTORE and CLONE: what each does, what it does not, and the hard follow-ups.", p_maintenance)


# ---------------------------------------------------------------- 2. security
def p_security():
    return (
        flow(["User runs a query", "Unity Catalog adds the row filter and column masks to the plan", "Engine scans the files", "User sees only allowed rows"], "The policy is a SQL function the engine injects into the query plan. The user never sees an unfiltered scan.", "How row filters work")
        + sec("how", "Implementation", "Row filters and column masks in Unity Catalog", CODE("""
-- the policy function
CREATE FUNCTION sec.region_filter(region STRING)
RETURN is_account_group_member('global_admins')
    OR EXISTS (SELECT 1 FROM sec.user_region_map m
               WHERE m.user_email = current_user() AND m.region = region);

ALTER TABLE sales.orders ADD ROW FILTER sec.region_filter ON (region);

-- column mask
CREATE FUNCTION sec.mask_ssn(ssn STRING)
RETURN CASE WHEN is_account_group_member('hr') THEN ssn ELSE '***-**-****' END;

ALTER TABLE hr.people ALTER COLUMN ssn SET MASK sec.mask_ssn;
"""))
        + sec("options", "Compare", "The ways to do it", T(["Approach", "How it works", "Weakness"], [
            ["Row filters and column masks", "Policy attached to the table, enforced everywhere", "Cost on big tables; a few feature limits"],
            ["Dynamic views", "Views with CASE WHEN is_member(...); users get the view only", "Bypassed if someone is granted the base table; policy repeated per view"],
            ["ABAC (tag-driven policies)", "Policy attached to a governed tag, so any tagged column or table gets it", "Newer feature; check current status and limits"],
            ["A copy of the table per group", "Physically separate data", "Storage and sync burden. Avoid."]]))
        + sec("hard", "Hard follow-ups", "Where it goes wrong", ul([
            "<b>Performance.</b> A mapping-table lookup becomes a semi-join on every query. Keep the mapping table small and broadcastable, cluster the main table on the filter column, and read EXPLAIN to confirm the filter does not block pushdown.",
            "<b>Bypass paths.</b> Direct access to the cloud files, or compute that does not enforce policies, leaks data. Managed tables with storage credentials locked down close the path.",
            "<b>Dedicated compute.</b> Fine-grained policies there are enforced through serverless filtering behind the scenes, which can add cost and delay. Standard access mode enforces them natively.",
            "<b>Sharing.</b> Tables with row filters have limits when shared through Delta Sharing. Check before promising a design.",
            "<b>The function.</b> Keep it cheap and predictable. Do not call outside services from it."]))
        + sec("see", "Related", "More on this site", '<p><a href="/learn/metric-views/">Metric views, taught from zero</a> includes row-level security on a semantic layer.</p>')
        + sec("ask", "Practice", "Questions to rehearse", qlist(["Implement row-level security and column masking. What are the performance and bypass risks?", "Dynamic views versus row filters: which would you choose and why?", "How would you give each tenant only their rows in a shared table?", "Why is a client-supplied tenant filter not safe?"]))
        + say("Row filters and masks are SQL functions attached to the table and enforced inside the plan. The risks are the lookup cost and any path that reaches the files without going through the engine."),
        [("Is a dynamic view as safe as a row filter?", "Only if nobody is granted the base table. A row filter travels with the table, so it holds on every route through the engine."),
         ("Do row filters slow queries?", "They can, especially with a large mapping table. Keep lookups small and cluster on the filter column.")])


page_def("row-level-security", "Row-level security and column masking", "Row-level security",
         "How row filters, column masks, dynamic views and tag-driven policies work in Unity Catalog, and the performance and bypass questions interviewers ask.", p_security)


# ---------------------------------------------------------------- 3. compute
def p_compute():
    return (
        flow(["Explore: serverless notebook or small shared cluster", "Run production: job cluster or serverless job", "Serve dashboards: serverless SQL warehouse"], "Develop interactively, run production on job compute, serve BI from a warehouse.", "Which compute for which stage")
        + sec("families", "The choices", "Compute families", T(["Compute", "Use it when", "Avoid it when"], [
            ["All-purpose (interactive) cluster", "Exploring, debugging, ad-hoc work shared by people.", "Scheduled jobs: higher cost per DBU, and idle time wastes money."],
            ["Job cluster", "Scheduled batch ETL; you need specific libraries, Spark configs or init scripts.", "Quick experiments: startup takes minutes."],
            ["Serverless notebooks and jobs", "New batch work, short or bursty jobs, teams that do not want to tune clusters.", "Init scripts, unusual libraries, GPUs, tight per-node cost control (check current limits)."],
            ["Serverless SQL warehouse", "Dashboards, ad-hoc SQL, many concurrent users, bursty demand.", "Heavy Python or ML."],
            ["Pro or classic SQL warehouse", "Steady load, or serverless not permitted in your network.", "Bursty load: startup takes minutes."],
            ["Pipeline compute (declarative pipelines)", "Streaming tables and materialized views in Lakeflow pipelines.", "Anything that is not a pipeline."],
            ["Instance pool", "Classic job clusters that must start fast, many short jobs.", "Low job volume: you pay for idle pool VMs."],
            ["Single node", "Small data, pandas, scikit-learn.", "Anything that needs distributed Spark."],
            ["GPU / ML runtime cluster", "Training and fine-tuning.", "Plain ETL."]]))
        + sec("access", "Sharing", "Access modes", T(["Mode", "Meaning", "Use for"], [
            ["Standard (was shared)", "Many users, isolated from each other, Unity Catalog security enforced natively.", "Teams sharing development compute."],
            ["Dedicated (was single user)", "One user or group; full language and library freedom. Fine-grained policies via serverless filtering.", "ML, R, custom libraries, jobs as a service principal."]]) + '<p class="verify">Mode names have changed over time; check the current labels.</p>')
        + sec("serverless", "Serverless", "What you can and cannot set", ul([
            "<b>Can:</b> performance mode for jobs (fast start versus lower cost; check current names), the environment version and libraries, budget policies and tags, warehouse size and auto-stop, network connectivity configuration.",
            "<b>Cannot (generally):</b> choose the node type, run init scripts, set most Spark configs, SSH in. This list shrinks over time, so verify."]))
        + sec("classic", "Classic knobs", "Settings that matter", T(["Knob", "Guidance"], [
            ["Autoscaling", "Good for variable load. For streaming and predictable jobs, fixed size is often steadier."],
            ["Spot instances", "Workers on fault-tolerant batch; keep the driver on-demand."],
            ["Photon", "Often a win for SQL and DataFrame work; compare cost per job."],
            ["Node type", "Memory-optimized for joins and caching; compute-optimized for CPU-bound work; storage-optimized for shuffle-heavy work."],
            ["Runtime", "Use an LTS version for production."],
            ["Cluster policies", "Cap size, force auto-termination, require tags. The main cost guardrail."]]))
        + sec("stream", "Streaming", "Best compute for streaming", ul([
            "Always-on stream: a <b>job cluster</b> (not all-purpose), fixed or tightly bounded size, mostly on-demand nodes, memory-optimized if stateful, RocksDB state store, an LTS runtime.",
            "Autoscaling reacts slowly for streams and moves state when nodes leave; size for peak and test.",
            "If freshness of minutes or hours is fine, do not run a 24/7 stream. Use <code>trigger(availableNow=True)</code> on a schedule. This is usually the biggest streaming saving.",
            "Streams inside declarative pipelines use pipeline compute; serverless pipelines manage scaling."]))
        + sec("driver", "Hard problem", "Driver memory and its problems", "<p>The driver plans the work, schedules tasks and collects small results. If it dies, the whole application dies.</p>"
              + T(["Cause", "Fix"], [
                  ["collect(), toPandas() on big data", "Keep data distributed; write out instead; limit() before inspecting."],
                  ["Large broadcast", "Lower the broadcast threshold or remove the hint; filter the small side first."],
                  ["Millions of files or tasks", "OPTIMIZE and compaction; fewer, larger partitions."],
                  ["Huge Delta log without checkpoints", "Make sure checkpoints are written; avoid thousands of tiny commits."],
                  ["Lineage growing in loops", "Write an intermediate table or checkpoint to cut the plan."],
                  ["Big Python objects in closures", "Broadcast variables or a join."],
                  ["Many notebooks on one shared cluster", "Fewer users per cluster; separate heavy users."],
                  ["Actions inside Python for-loops", "Batch the work into one job."]])
              + "<p>Symptoms: Java heap OOM on the driver, \"driver is up but is not responsive, likely due to GC\", <code>maxResultSize</code> exceeded, hangs between stages. Look at the cluster metrics page, the driver logs, and the code that returns data to the driver. A bigger driver is the last resort, not the first. Raising <code>spark.driver.maxResultSize</code> only hides the problem.</p>")
        + sec("ask", "Practice", "Questions to rehearse", qlist(["Why are all-purpose clusters dearer than job clusters, and what follows?", "When would you pick classic job clusters over serverless jobs today?", "Bigger warehouse versus more clusters: which fixes one slow query, and which fixes queueing?", "Why keep the driver on-demand when workers are spot?", "A job fails with driver OOM. What do you do?", "How would you cut the cost of a 24/7 stream?"]))
        + say("Develop on interactive or serverless, run production on job clusters or serverless jobs, serve BI from serverless SQL warehouses. For streams, ask first whether it needs to be always on."),
        [("Is serverless always cheaper?", "No. It usually wins for bursty, short or unpredictable work. A tuned classic job on spot nodes can win for large, steady workloads. Compare cost per run from system tables."),
         ("Does a bigger driver make a job faster?", "Usually not. It only helps when the bottleneck is on the driver: planning, collecting or broadcasting.")])


page_def("compute-choice", "Which compute for which job", "Compute choice",
         "All-purpose, job, serverless, SQL warehouse and pool compute: when to use each, serverless settings, the best setup for streaming, and driver memory problems.", p_compute)


# ---------------------------------------------------------------- 4. joins
def p_joins():
    return (
        flow(["What rows do I want? (logical join)", "How big is each side?", "Spark picks a strategy: broadcast, sort-merge, shuffle hash", "AQE can change it at run time"], "Two questions: which rows you want, and how Spark will compute them.", "Join type and join strategy")
        + sec("logical", "Which rows", "Logical join types", T(["Join", "Returns", "Use it when"], [
            ["Inner", "Rows that match on both sides", "You only want records present in both."],
            ["Left outer", "All left rows, nulls where the right has no match", "Keep every fact row even if the dimension is missing. The most common warehouse join."],
            ["Full outer", "All rows from both sides", "Reconciliation: find what is missing on either side."],
            ["Left semi", "Left rows that have a match, left columns only, no duplication", "\"Does it exist?\" checks. Faster and cleaner than IN or EXISTS."],
            ["Left anti", "Left rows with no match on the right", "Find missing or new records, incremental loads of rows not yet in the target."],
            ["Cross", "Every left row paired with every right row", "Tiny lookup tables only. Dangerous on big data."],
            ["Non-equi (range)", "Rows matching a condition like a BETWEEN b AND c", "Time-range and SCD lookups; needs care, see below."],
            ["ASOF (point in time)", "The nearest earlier row", "\"Price as of the trade time\". Otherwise use a window function."]])
              + "<p>Use semi and anti joins instead of inner join plus DISTINCT, and instead of <code>NOT IN</code>, which returns nothing if the right side contains one null.</p>")
        + sec("physical", "How computed", "Physical strategies", T(["Strategy", "How it works", "Best when", "Watch out for"], [
            ["Broadcast hash", "The small table is sent to every executor; no shuffle of the big table.", "One side is small (default threshold about 10 MB; AQE can switch at run time).", "The small side goes through the driver; a table that is not small causes driver OOM and timeouts."],
            ["Shuffle hash", "Both sides shuffled by key, one side built into a hash table per partition.", "One side much smaller but too big to broadcast.", "Memory per partition; a hot key can overflow it."],
            ["Sort-merge", "Both sides shuffled and sorted, then merged.", "The default for two big tables; spills safely.", "Expensive shuffle and sort; sensitive to skew."],
            ["Broadcast nested loop", "Compares every pair, one side broadcast.", "Non-equi conditions with one small side.", "Quadratic cost."],
            ["Cartesian", "Every pair across partitions.", "Explicit cross joins only.", "Often an accident from a missing condition."]]))
        + sec("choose", "Decide", "Choosing in practice", T(["Situation", "What to do"], [
            ["Big fact with small dimension", "Broadcast the dimension; keep statistics current with ANALYZE."],
            ["Two big tables", "Sort-merge; filter and select columns before the join to shrink the shuffle."],
            ["Same two big tables joined often", "Cluster both on the join key. This cuts files read; it does not remove the shuffle by itself."],
            ["Hot key", "See the skew page."],
            ["Range or time lookup", "Turn it into an equi-join by joining on a time bucket first, then filter exactly. Otherwise Spark falls back to nested loop."],
            ["Incremental merge into Delta", "MERGE with the key in the ON clause plus a cluster or partition filter."],
            ["Streaming", "Stream to static re-reads the static side each batch. Stream to stream needs watermarks and a time bound so state can be cleaned."]]))
        + sec("problems", "Hard problems", "When a join goes wrong", T(["Problem", "Symptom", "Fix"], [
            ["Skew", "One task far slower than the median", "AQE skew handling, isolate or salt the hot key."],
            ["Null keys", "One huge partition of nulls", "Nulls never match in an equi-join: filter them out and union back for outer joins."],
            ["Duplicate keys on both sides", "Row count explodes", "Check key uniqueness first; deduplicate the dimension; count rows before and after."],
            ["Key types differ", "Implicit cast, poor plan, wrong matches", "Cast both sides to the same type."],
            ["Join on expressions", "ON lower(a.x) = lower(b.x) blocks optimizations", "Store the normalized column and join on it."],
            ["Accidental cross join", "Very long job", "Check the condition."],
            ["Broadcast timeout", "Could not execute broadcast in 300 secs", "Remove the hint or pre-filter."]]))
        + sec("hints", "Tools", "Hints", CODE("""
SELECT /*+ BROADCAST(d) */ ...          -- force broadcast of d
SELECT /*+ MERGE(a, b) */ ...           -- force sort-merge
SELECT /*+ SHUFFLE_HASH(b) */ ...       -- prefer shuffle hash, b as build side
SELECT /*+ SKEW('a', 'key') */ ...      -- skew hint (Databricks)
""") + "<p>Use hints only after reading EXPLAIN. A broadcast hint on a table that doubles in size becomes tomorrow's outage.</p>")
        + sec("ask", "Practice", "Questions to rehearse", qlist(["Left semi versus inner join: when is semi better?", "Why is NOT IN risky and what do you use instead?", "How does Spark decide on a broadcast, and how can one fail the driver?", "A big join is slow because of one hot key. Walk through your fixes.", "How would you join events to a table of validity date ranges?", "After a join, row counts doubled. How do you debug it?"]))
        + say("Pick the join by the question you are asking: match, keep all, exists, missing. Then make the plan fit the sizes: broadcast the small side, sort-merge for two big sides, and fix nulls and skew before they take the job down."),
        [("What is the difference between a semi join and an inner join?", "A semi join only filters the left rows by existence on the right and never duplicates them. An inner join returns columns from both and can multiply rows."),
         ("Why did my plan change at run time?", "Adaptive query execution re-plans after shuffle stages using real sizes. Read the final plan in the query profile.")])


page_def("joins", "Join types and which to use when", "Joins",
         "Inner, outer, semi, anti, cross and range joins, then broadcast, shuffle-hash and sort-merge: which to use when, plus the join problems interviewers probe.", p_joins)


# ---------------------------------------------------------------- 5. skew and shuffle
def p_skew():
    return (
        flow(["Rows split by key", "One key is huge", "One task gets most of the data", "The stage waits for it"], "Skew is a shuffle problem: equal keys must meet, and one key is too big.", "How skew happens")
        + sec("shuffle", "First", "What a shuffle is", "<p>When an operation needs all rows with the same key in one place (join, groupBy, distinct, window, repartition), Spark moves rows across the network. Map tasks write their output split by target partition; reduce tasks fetch their piece from every map task. It costs disk, network, serialization and sorting, so it is usually the most expensive step.</p><p>No shuffle: filter, select, column expressions, union, coalesce (decreasing), broadcast joins.</p>")
        + sec("skew", "The problem", "Recognising skew", ul([
            "Spark UI stage page: the slowest task takes 5 times the median or more; shuffle read size per task is very uneven.",
            "One task spills to disk while others do not; one executor runs out of memory.",
            "A job sits at \"199 of 200 tasks\" for a long time.",
            "Typical causes: null or default keys (-1, unknown, empty string), one very popular customer or product, a dominant country, most data on one date."]))
        + sec("fixes", "Fix in this order", "Fixes for skew", T(["Fix", "How it works", "Use when"], [
            ["Remove or isolate null and default keys", "Filter before the join, process separately, union back.", "The hot key is junk. Cheapest and most common."],
            ["AQE skew join", "At run time, splits partitions much bigger than the median into several tasks.", "Sort-merge joins. On by default; check it fired in the query profile."],
            ["Broadcast the small side", "No shuffle of the big side.", "One side is small."],
            ["Skew hint", "Tell the optimizer the column and values.", "AQE misses it and you know the hot keys."],
            ["Isolate the hot keys", "Broadcast-join the hot rows, normal-join the rest, union.", "A few known hot keys."],
            ["Salting", "Spread a hot key over many partitions with a random suffix.", "groupBy or join skew that AQE does not fix."],
            ["Two-stage aggregation", "Partial aggregate, then final aggregate.", "Skewed groupBy with sum, count, min, max."],
            ["Change the grain", "Pre-aggregate upstream or pick a better key.", "The design is the cause."],
            ["More partitions", "Smaller partitions.", "Only moderate skew. A single giant key still lands in one partition."]]))
        + sec("salt", "Salting", "How salting works", "<p>A hot key always hashes to the same partition. Add a random number so key K becomes K_0, K_1, … K_15, which hash to different partitions.</p>"
              + CODE("""
from pyspark.sql import functions as F
N = 16

# skewed groupBy: aggregate in two steps
salted  = df.withColumn("salt", (F.rand() * N).cast("int"))
partial = salted.groupBy("key", "salt").agg(F.sum("amount").alias("p"))
final   = partial.groupBy("key").agg(F.sum("p").alias("total"))

# skewed join: salt the big side, replicate the small side N times
big   = big.withColumn("salt", (F.rand() * N).cast("int"))
small = small.withColumn("salt", F.explode(F.array([F.lit(i) for i in range(N)])))
joined = big.join(small, ["key", "salt"]).drop("salt")
""") + ul(["The other side grows N times, so salt only the hot keys if you can: give normal keys salt 0 and do not replicate them.",
           "For an average, carry sum and count separately. Exact distinct count needs a different approach.",
           "rand() can differ on a task retry; derive the salt from a row id if results must be exact.",
           "Prefer AQE, hints and key isolation first. Salting is the fallback."]))
        + sec("avoid", "Today", "Shuffling less", T(["Technique", "Effect"], [
            ["Broadcast joins", "No shuffle of the big table; AQE can switch to broadcast at run time."],
            ["Filter and select early", "Fewer rows and columns in the shuffle."],
            ["Aggregate before joining", "Reduces the big side when the join needs only aggregates."],
            ["Built-in aggregates", "Spark pre-aggregates inside each map task before the shuffle. Avoid collecting lists."],
            ["AQE partition coalescing", "No thousands of tiny shuffle tasks."],
            ["Liquid clustering and dynamic pruning", "Read fewer files, so there is less to shuffle."],
            ["Avoid needless repartition()", "Use coalesce to reduce partitions without a shuffle."],
            ["Reuse the same window partitioning", "Each different partitionBy triggers a shuffle."],
            ["dropDuplicates on keys, approx_count_distinct", "Cheaper than distinct on whole rows or exact counts."],
            ["Incremental processing", "Shuffle only new or changed data."],
            ["Bucketing / storage-partitioned joins", "Can avoid a shuffle but support on Delta is limited; rarely the answer. Check your runtime."]])
              + "<p>The goal is not zero shuffles. It is less data, shuffled less often.</p>")
        + sec("debug", "Routine", "When a job is slow", "<ol><li>Find the slowest stage.</li><li>Look at task time spread. Max far above median means skew; evenly slow means too much data or too little parallelism.</li><li>Check shuffle size and spill.</li><li>Count rows by the join or group key and look at the top 20 values.</li><li>Apply the cheapest fix. Salting last.</li><li>Compare stage times, not just total time.</li></ol>")
        + sec("ask", "Practice", "Questions to rehearse", qlist(["Which operations cause a shuffle and which avoid one?", "How do you detect skew in the Spark UI?", "Explain salting for a join. What happens to the smaller table?", "How is AQE skew handling different from salting, and when does AQE not help?", "Why does raising shuffle partitions not fix one hot key?", "A groupBy on 10 TB has one task running for an hour. What do you do?"]))
        + say("A shuffle moves rows so equal keys meet; skew is when one key is so big that one task does most of the work. I try the cheap fixes first: drop junk keys, broadcast, let AQE split, filter and aggregate early. Then key isolation, and salting last."),
        [("Does more shuffle partitions fix skew?", "Only moderate skew. One key always lands in one partition."),
         ("Can salting break correctness?", "For sums, counts, min and max it is safe with a two-step aggregation. Averages need sum and count carried separately.")])


page_def("skew-and-shuffle", "Skew, salting and avoiding shuffle", "Skew and shuffle",
         "What a shuffle is, how to spot skew, the fixes in order (AQE, hints, key isolation, salting with code), and how to shuffle less today.", p_skew)


# ---------------------------------------------------------------- 6. engines
def p_engines():
    return (
        flow(["Catalyst plans the query", "AQE re-plans at run time", "Photon runs supported operators natively", "Predictive Optimization keeps tables healthy"], "Four different layers: planning, re-planning, execution, maintenance.", "Where AQE, Photon and Predictive Optimization sit")
        + sec("aqe", "AQE", "Adaptive Query Execution", "<p>Spark normally builds one plan from guesses about data size. AQE re-plans between stages using the real sizes. It is in open-source Spark 3 and on by default on Databricks.</p>"
              + T(["What it does", "Effect"], [["Coalesces small shuffle partitions", "Fixes a badly chosen shuffle.partitions"], ["Switches join strategy at run time", "A sort-merge join becomes a broadcast when a side turns out small"], ["Splits skewed partitions", "Handles skew in sort-merge joins"], ["Dynamic partition and file pruning (related)", "Uses the other side's values to skip data"]])
              + "<p>Limits: it decides only at shuffle boundaries, cannot fix bad file layout, and the plan before the run can differ from what ran. Read the final plan in the query profile.</p>")
        + sec("po", "Predictive Optimization", "PO", "<p>A Databricks service that maintains Unity Catalog managed tables: OPTIMIZE, VACUUM and ANALYZE, run when its cost model says it pays. Related: automatic liquid clustering (<code>CLUSTER BY AUTO</code>) picks clustering keys from query history.</p>" + ul(["Billed as serverless usage; watch it in system tables.", "Does not cover external tables.", "You give up control of timing.", "It does not fix a bad design such as a streaming trigger that makes tiny files."]))
        + sec("photon", "Photon", "When to use it and when not", "<p>Photon is a native C++ vectorized engine that replaces Spark's JVM execution for supported operators. Catalyst, scheduling and the APIs stay Spark, and results are the same with or without it.</p>"
              + T(["Use it for", "Skip it for"], [
                  ["SQL and DataFrame ETL: scans, filters, joins, aggregations", "Python UDFs and RDD code: nothing to speed up"],
                  ["Large joins and group-bys", "Tiny jobs dominated by startup"],
                  ["Delta scans, MERGE, UPDATE, DELETE", "Jobs bound by an outside API, network or driver work"],
                  ["BI and dashboards on SQL warehouses", "ML training and non-SQL libraries"],
                  ["CPU-bound jobs", "Queries that fall back to Spark for most operators"]])
              + "<p>It costs more DBUs per hour, so judge cost per job, not per hour. In the query profile, look for operators labelled Photon and for fallback boundaries.</p>")
        + sec("inside", "How it works", "Photon inside", T(["Technique", "Meaning"], [
            ["Vectorized execution", "Processes batches of column values, not one row at a time; cache friendly and uses SIMD instructions."],
            ["Columnar in-memory format", "Data stays columnar from the Parquet read through the operators."],
            ["Native code, off-heap memory", "No JVM garbage collection pauses or object overhead; memory still accounted through Spark's manager."],
            ["Vectorized interpretation, not code generation", "Pre-compiled kernels run over vectors: easier to debug, better per-operator metrics, no compile time per query, easier to adapt."],
            ["Runtime adaptivity", "Chooses a code path per batch (nulls or not, all rows active or not, ASCII strings)."],
            ["Fast hash tables and I/O", "Vectorized hashing and probing with prefetching; native Parquet decoding and writing."],
            ["Where it plugs in", "A rule swaps supported operators bottom-up; at an unsupported operator the plan converts back to Spark. Each switch costs time."]]))
        + sec("new", "Newer things", "Other recent features to know", '<p class="verify">Names and status change quickly. Check the release notes before quoting any of these as generally available.</p>'
              + T(["Area", "Features"], [
                  ["Storage and Delta", "Liquid clustering and automatic liquid clustering, deletion vectors, row-level concurrency, column mapping, type widening, UniForm, managed Iceberg, change data feed, collations, the Variant type"],
                  ["Compute and engine", "Serverless compute, Photon, materialized views with incremental refresh, Spark Connect, Lakehouse Federation, query result and disk caching"],
                  ["Ingestion and pipelines", "Auto Loader, Lakeflow Declarative Pipelines, Lakeflow Connect, AUTO CDC, Lakeflow Jobs triggers, real-time mode, transformWithState"],
                  ["Governance", "Unity Catalog, row filters and masks, ABAC, Metric Views, system tables, volumes, Delta Sharing, data quality monitoring, budget policies"],
                  ["AI and apps", "Genie, AI functions in SQL, Vector Search, Model Serving, agent tooling, Databricks Apps, Lakebase"],
                  ["Developer experience", "Asset Bundles, Databricks Connect, Databricks Assistant"]])
              + '<p>Already on this site: <a href="/learn/spark-declarative-pipelines/">declarative pipelines, open source and Lakeflow</a>, <a href="/learn/metric-views/">metric views</a>, <a href="/learn/delta-vs-iceberg/">Delta vs Iceberg</a>, <a href="/learn/table-maintenance/">who maintains your tables</a>, <a href="/learn/streaming/real-time-mode/">real-time mode</a>.</p>')
        + sec("ask", "Practice", "Questions to rehearse", qlist(["What can AQE fix, and what can it not?", "What does Predictive Optimization run, who pays, and where do you see it?", "What does Photon replace and what stays Spark?", "Why vectorized interpretation instead of code generation?", "A job got dearer after enabling Photon. Why might that be?", "How do you decide on Photon for 200 nightly jobs?"]))
        + say("AQE re-plans with real sizes, Photon executes faster, Predictive Optimization maintains tables. Each has a limit, and I check each with the query profile or system tables, not by guessing."),
        [("Does Photon change query results?", "No. It keeps Spark semantics, so results are the same with or without it."),
         ("Does AQE replace statistics?", "No. Good statistics still give better first plans and join order.")])


page_def("aqe-photon-po", "AQE, Photon, Predictive Optimization and newer features", "AQE, Photon, PO",
         "What AQE, Photon and Predictive Optimization do, when each helps or does not, how Photon works inside, and a map of newer Databricks features.", p_engines)


# ---------------------------------------------------------------- 7. cost and performance
def p_levers():
    return (
        flow(["Measure with system tables and the query profile", "Fix the biggest item", "Lock it in with policies and tags", "Repeat"], "Measure first. Waste and data scanned are usually the biggest levers.", "The loop for cost and performance work")
        + sec("cost", "Cost", "The biggest cost lever: stop paying for compute that does no useful work", T(["Rank", "Lever", "First action"], [
            ["1", "Idle and always-on compute (interactive clusters left running, 24/7 streams that need only hourly freshness)", "Auto-termination via policy; availableNow on a schedule"],
            ["2", "Wrong compute type (scheduled jobs on all-purpose clusters)", "Job clusters or serverless jobs"],
            ["3", "Processing too much data (full reloads, wide scans)", "Incremental loads; better layout"],
            ["4", "Oversized or poorly tuned clusters", "Right-size from measured utilization"],
            ["5", "On-demand workers for fault-tolerant batch", "Spot workers, on-demand driver"],
            ["6", "Slow code (skew, spill, UDFs)", "Fix the top few expensive jobs"],
            ["7", "SQL warehouse size and auto-stop", "Short auto-stop; serverless for bursty BI"],
            ["8", "Storage and egress", "VACUUM; lifecycle rules; same-region compute"]])
              + "<p>Cost is price per hour times hours running. Tuning one query by 20 percent saves 20 percent of one job. Moving 50 jobs off all-purpose clusters saves a large part of the bill at once. Find your own lever first: query <code>system.billing.usage</code> with list prices, group by job, cluster and tag, and look at the top ten. Keep gains with cluster policies, budget policies, tags and spend alerts.</p>")
        + sec("perf", "Performance", "The biggest performance lever: read less data", T(["Rank", "Lever", "First action"], [
            ["1", "Data skipping through file layout", "Liquid clustering on filter and join columns; stats on those columns (first 32 by default)"],
            ["2", "Small files", "OPTIMIZE, optimized writes, auto compaction, Predictive Optimization"],
            ["3", "Shuffle volume", "Filter and select early, broadcast, aggregate before joining"],
            ["4", "Skew", "Remove junk keys, AQE, isolate or salt"],
            ["5", "Photon", "SQL-heavy workloads; measure cost per job"],
            ["6", "Python UDFs", "Built-in functions or vectorized pandas UDFs"],
            ["7", "Non-incremental processing", "Streaming tables, change data feed, incremental MERGE"],
            ["8", "Right-sized compute", "Scale on spill and utilization, not guesses"],
            ["9", "Caching", "Disk and result caches; avoid .cache() by habit"],
            ["10", "Statistics", "ANALYZE or Predictive Optimization"]])
              + "<p>Query time is roughly data scanned times cost per byte. Layout cuts the first factor for every query, forever. In the query profile check files read versus pruned, task time spread, shuffle and spill size, and time outside Photon.</p>")
        + sec("egress", "Network", "Egress and ingress", '<p>Data moving in is generally free; moving out is charged per GB. Full tables and hidden costs: <a href="/learn/databricks-interview/egress-and-ingress/">Cheapest way to move data in and out</a>.</p>')
        + sec("ask", "Practice", "Questions to rehearse", qlist(["How would you find your biggest cost lever?", "Why are idle clusters usually the biggest waste?", "A query is slow. In what order do you look?", "How do you lock in a saving so it does not drift back?", "How would you reduce egress between two regions?", "Auto Loader or COPY INTO for cheap ingestion?"]))
        + say("I start by measuring, in system tables and the query profile. The biggest cost lever is usually idle or mis-typed compute; the biggest performance lever is reading less data. Hardware is the last lever, because it makes a bad plan faster without making it smaller."),
        [("What is the quickest cost win?", "Auto-termination and moving scheduled work off all-purpose clusters. Both are settings, not code."),
         ("Is ingress free?", "The transfer into the cloud usually is. Source egress, network path, compute and requests are not.")])


page_def("cost-and-performance", "The biggest cost and performance levers", "Cost and performance levers",
         "Ranked levers for Databricks cost and performance, how to find your own with system tables and the query profile, plus egress and ingress costs.", p_levers)


# ---------------------------------------------------------------- 8a. declarative + semantic
def p_declarative():
    return (
        flow(["Imperative: you write the steps, order, retries, checkpoints", "Declarative: you write what each table should be", "The engine builds the graph and runs it in order"], "Declarative is the same idea as SQL, applied to a whole pipeline of tables.", "Imperative versus declarative")
        + sec("meaning", "The idea", "What declarative means", "<p><b>Imperative:</b> you write the steps. Read this file, filter, write it there; read that table, merge it in; run the next job. You decide order, retries, checkpoints, when to run and what to do on failure.</p><p><b>Declarative:</b> you write what the results should be. Table <code>orders_clean</code> is this query over <code>orders_raw</code>; table <code>daily_revenue</code> is this query over <code>orders_clean</code>. The engine works out the order, runs things in dependency order, processes incrementally, retries and keeps checkpoints.</p><p>Think of directions: imperative is turn-by-turn instructions to a driver; declarative is giving the address and letting the GPS choose and re-route. SQL is already declarative for one query; declarative pipelines apply it to many tables.</p>"
              + T(["Gain", "Cost"], [["The engine builds the dependency graph from your definitions", "Less control over exact execution steps"], ["Built-in incremental processing and checkpoints", "You work inside the framework's rules"], ["Retries and recovery handled", "Debugging happens at pipeline level"], ["Less code, easier to read", "Very custom side effects do not fit"]]))
        + sec("blocks", "Parts", "The building blocks (the same in both)", T(["Concept", "Meaning"], [["Streaming table", "Updated incrementally from an append-style source; each record processed once"], ["Materialized view", "A table defined by a query, kept current with that query's result"], ["Temporary view", "An intermediate step inside the pipeline, not published"], ["Flow", "The query that feeds a table (a table can have several flows)"], ["Dataflow graph", "The dependency graph built from all definitions"], ["Pipeline", "The set of definitions that run and refresh together"]]))
        + sec("diff", "The difference", "Apache Spark Declarative Pipelines versus Databricks", "<p>Databricks contributed the core of Delta Live Tables to Apache Spark as <b>Spark Declarative Pipelines</b> (announced in 2025, in the Spark 4.x line; I believe 4.1). The Databricks product is <b>Lakeflow Spark Declarative Pipelines</b> (earlier Delta Live Tables). Roughly: open source is the language and basic engine; Databricks is the operated product. Check the current release notes for how much has moved upstream.</p>"
              + T(["Area", "Open-source Spark", "Databricks Lakeflow"], [
                  ["What it is", "Authoring model and execution framework inside Spark", "The full managed product"],
                  ["Where it runs", "Any Spark cluster you run", "Serverless or classic Databricks compute"],
                  ["Operations", "You run the cluster, retries, upgrades", "Platform handles lifecycle, scaling, retries, upgrades"],
                  ["Scheduling", "Bring your own (Airflow, cron)", "Lakeflow Jobs; triggered or continuous"],
                  ["Governance", "Whatever catalog you configure", "Unity Catalog: lineage, access control, auditing"],
                  ["Data quality", "Basic", "Expectations: warn, drop or fail, with metrics"],
                  ["CDC / SCD", "Write the merge yourself, unless added upstream", "AUTO CDC / APPLY CHANGES for SCD1 and SCD2 with ordering"],
                  ["Materialized view refresh", "Limited", "Incremental refresh of only what changed (serverless)"],
                  ["Engine", "Open-source Spark", "Photon and Databricks optimizations"],
                  ["Ingestion", "Spark sources", "Auto Loader and Lakeflow Connect"],
                  ["Monitoring", "Spark UI and logs", "Pipeline UI, event log tables, lineage graph"],
                  ["Portability", "High", "Tied to Databricks features"],
                  ["Cost", "Your infrastructure", "DBUs for pipeline compute"]])
              + CODE("""
from pyspark import pipelines as dp   # module name in open source; check your runtime

@dp.table
def orders_clean():
    return spark.readStream.table("orders_raw").where("amount > 0")

@dp.materialized_view
def daily_revenue():
    return spark.read.table("orders_clean").groupBy("order_date").sum("amount")
""") + "<p>You do not write checkpoint paths, run order, write mode, triggers or retry loops. Anything that uses expectations, AUTO CDC, Unity Catalog options or Auto Loader will not run on plain Spark.</p>")
        + sec("when", "Choose", "When declarative is right", T(["Use declarative when", "Prefer imperative when"], [["Standard medallion ETL", "Custom logic and side effects such as calling APIs"], ["You want incremental processing without managing stream state", "You need exact control of write and merge behaviour"], ["Many interdependent tables", "One-off scripts"], ["Quality rules belong in the pipeline", "Runtime constraints rule the framework out"]]) + '<p>Full treatment, costs and harness patterns: <a href="/learn/spark-declarative-pipelines/">Declarative or not</a>.</p>')
        + sec("semantic", "Semantic layer", "Example: a Unity Catalog metric view", "<p>A metric view defines business measures once, so every dashboard, Genie space and notebook agrees on what revenue means.</p>"
              + CODE("""
CREATE VIEW main.sales.order_metrics
WITH METRICS LANGUAGE YAML AS $$
version: 0.1
source: main.sales.orders
joins:
  - name: customer
    source: main.sales.customers
    on: source.customer_id = customer.id
dimensions:
  - name: order_month
    expr: DATE_TRUNC('MONTH', order_date)
  - name: segment
    expr: customer.segment
measures:
  - name: total_revenue
    expr: SUM(amount)
  - name: avg_order_value
    expr: SUM(amount) / COUNT(DISTINCT order_id)
$$;

SELECT segment, MEASURE(total_revenue)
FROM main.sales.order_metrics
GROUP BY segment;
""") + "<p>The point to make: <code>avg_order_value</code> is a ratio and cannot be averaged across rows. The measure is re-evaluated at whatever grain the query groups by, which plain views get wrong. It is governed by Unity Catalog, so row filters and lineage apply. Check the current YAML version and syntax in the docs. Full course: <a href=\"/learn/metric-views/\">Metric views, taught from zero</a>.</p>")
        + sec("ask", "Practice", "Questions to rehearse", qlist(["What does declarative mean, versus workflow tasks?", "Streaming table versus materialized view?", "What did Databricks contribute to open-source Spark and what stayed proprietary?", "What are expectations and what three actions can you take?", "How does AUTO CDC handle out-of-order records?", "Metric view versus a plain SQL view?"]))
        + say("Declarative means I state what each table is and the engine decides order, increments and retries. Open-source Spark gives the language and basic engine; Databricks adds governance, expectations, AUTO CDC, incremental refresh and managed compute."),
        [("Is Lakeflow the same as Delta Live Tables?", "It is the renamed and extended successor. The core idea and much of the code are the same."),
         ("Why use a metric view?", "So a measure like average order value is defined once and stays correct at any grouping.")])


page_def("declarative-and-semantic", "What declarative means, and a semantic layer example", "Declarative and semantic",
         "Declarative versus imperative in plain words, Spark Declarative Pipelines versus Databricks Lakeflow, and a worked Unity Catalog metric view.", p_declarative)


# ---------------------------------------------------------------- 8b. asset bundles
def p_bundles():
    return (
        flow(["Project as files in Git", "bundle validate", "bundle deploy -t target", "Run as a service principal"], "The pull request is the change; one command deploys it.", "Asset Bundle workflow")
        + sec("what", "The idea", "What a bundle is", "<p>A bundle is the whole Databricks project as files: jobs, pipelines, notebooks, permissions, cluster settings. They live in Git and one command deploys them to a workspace. UI-built jobs cannot be reviewed, promoted from dev to prod, or kept free of drift. In newer docs the feature is also called Declarative Automation Bundles; the command is still <code>databricks bundle</code> and the file <code>databricks.yml</code>. Check the current name and engine details.</p>"
              + CODE("""
my_project/
  databricks.yml          # name, targets, variables, includes
  resources/ingest_job.yml
  resources/sales_pipeline.yml
  src/                    # notebooks, Python
  tests/
""") + CODE("""
# databricks.yml
bundle:
  name: sales_platform
include:
  - resources/*.yml
variables:
  catalog: { description: Target catalog, default: dev_catalog }
targets:
  dev:
    mode: development       # prefixes names, pauses schedules
    default: true
    workspace: { host: https://dev.cloud.databricks.com }
  prod:
    mode: production
    workspace: { host: https://prod.cloud.databricks.com }
    variables: { catalog: prod_catalog }
    run_as: { service_principal_name: "<application-id>" }
""") + CODE("""
# resources/ingest_job.yml
resources:
  jobs:
    ingest_job:
      name: ingest_${bundle.target}
      tasks:
        - task_key: load
          notebook_task:
            notebook_path: ../src/load.py
            base_parameters: { catalog: ${var.catalog} }
          job_cluster_key: main
      job_clusters:
        - job_cluster_key: main
          new_cluster: { spark_version: 15.4.x-scala2.12, node_type_id: i3.xlarge, num_workers: 2 }
"""))
        + sec("cmds", "Commands", "What to know", T(["Command", "What it does"], [["databricks bundle init", "New project from a template"], ["bundle validate", "Check config and show the resolved result"], ["bundle deploy -t prod", "Upload files and create or update resources"], ["bundle run <job> -t dev", "Trigger a job or pipeline"], ["bundle destroy -t dev", "Delete everything the bundle deployed"], ["bundle generate job", "Turn an existing UI job into YAML"], ["bundle deployment bind", "Link an existing resource so deploy updates it instead of duplicating"]]))
        + sec("concepts", "Concepts", "Targets, modes, variables, identity", T(["Concept", "Meaning"], [["Targets", "Environments (dev, staging, prod), each overriding workspace, variables, permissions and run identity"], ["Development mode", "Prefixes resource names with your user and pauses schedules, so people can deploy the same bundle without colliding"], ["Production mode", "Enforces safer rules, such as an explicit run_as and a non-personal root path"], ["Variables", "${var.name}, set per target or with --var"], ["Deployment state", "Stored in the workspace; the CLI compares it with your config. Historically Terraform underneath, with a newer direct engine; check which is the default"], ["run_as", "Production jobs run as a service principal, not a person"], ["Artifacts", "Build and upload Python wheels and libraries"]]))
        + sec("cicd", "CI/CD", "A pipeline for bundles", "<ol><li>Pull request: validate, unit tests, deploy to a dev or staging target and run an integration job.</li><li>Merge to main: deploy to staging, run smoke tests.</li><li>Release tag: deploy to prod with a service principal using OIDC or a CI secret, never a personal token.</li><li>Nobody edits prod in the UI; the next deploy overwrites it.</li></ol>")
        + sec("hard", "Hard problems", "Problems and answers", T(["Problem", "Answer"], [
            ["UI-created resources already exist in prod", "bundle generate to capture them, then deployment bind so deploy adopts them."],
            ["Someone changed a job in the UI (drift)", "Deploy overwrites it. Make only the service principal able to edit prod."],
            ["Same code, different catalogs and clusters per environment", "Variables plus target overrides. Never hard-code catalog or workspace names in notebooks."],
            ["Renamed a job and the old one kept running", "The resource key is the identity. Changing the key creates a new resource. Keep keys stable."],
            ["Secrets", "Reference secret scopes. No values in YAML."],
            ["Monorepo with many teams", "A bundle per domain, shared libraries as wheels, a common template, CODEOWNERS on target files."],
            ["Rollback", "Redeploy the previous Git tag. Data is not rolled back; pair with Delta RESTORE if needed."],
            ["Unity Catalog objects and metastore", "Bundles can manage some objects; check current support. Metastore and catalogs are usually Terraform."]]))
        + sec("tf", "Compare", "Bundles versus Terraform", T(["", "Bundles", "Terraform provider"], [["Best for", "Application layer: jobs, pipelines, notebooks, dashboards", "Platform layer: workspaces, metastore, networking, catalogs, identities"], ["Unit", "A project with code files", "Infrastructure state"], ["Owner", "Data engineers", "Platform team"]]) + "<p>Use both: Terraform for the foundation, bundles for what runs on it.</p>")
        + sec("ask", "Practice", "Questions to rehearse", qlist(["Why bundles instead of the UI or raw REST calls?", "How do you promote the same pipeline from dev to prod with different configs?", "What does mode: development change?", "How do you stop a prod job running as a person?", "Someone edited a job in the UI. What happens on the next deploy?", "How do you bring existing jobs under bundle management?", "Describe your CI pipeline for a bundle, including tests and secrets."]))
        + say("The bundle is the project as code. Targets give me environments, variables give me different configs, and a service principal runs production. Nobody edits prod by hand."),
        [("Do bundles replace Terraform?", "No. They cover the application layer; Terraform covers the platform."), ("What is the identity of a deployed job?", "Its resource key in the bundle, not its display name.")])


page_def("asset-bundles", "Asset Bundles: projects as code", "Asset Bundles",
         "What Databricks Asset Bundles are, a complete databricks.yml and job example, commands, CI/CD, hard problems and the Terraform split.", p_bundles)


# ---------------------------------------------------------------- 8c. lakeflow connect
def p_connect():
    return (
        flow(["Connection (credentials in Unity Catalog)", "Ingestion pipeline: pick tables, set destination", "Gateway reads the source (change log for databases)", "Delta tables in Unity Catalog"], "A managed copy from a source into your lakehouse, kept up to date.", "How Lakeflow Connect works")
        + sec("what", "The idea", "What it is", "<p>Lakeflow Connect is a set of managed ingestion connectors. You give a connection and a target; Databricks runs the pipeline that copies the data into Unity Catalog Delta tables and keeps it current. You write no extraction code and run no CDC infrastructure. For databases it reads the change log, so inserts, updates and deletes are captured. It runs on serverless pipeline compute and handles schema changes. It can also be set up in the UI, the API, or as a bundle.</p><p class=\"verify\">The connector list and status change often (SaaS apps such as Salesforce, Workday, ServiceNow and Google Analytics; databases such as SQL Server; SharePoint). Check the current list.</p>")
        + sec("when", "Choose", "When to use it and when not", T(["Situation", "Choice"], [
            ["Supported SaaS app, no wish to maintain API code", "Lakeflow Connect: pagination, rate limits, retries and schema changes handled"],
            ["Continuous replication from an operational database", "Lakeflow Connect: log-based CDC, low source load, deletes captured"],
            ["Small team, many sources", "Lakeflow Connect: one pattern instead of many jobs"],
            ["Files landing in cloud storage", "Auto Loader"],
            ["Message streams (Kafka, Event Hubs, Kinesis)", "Structured Streaming connectors"],
            ["Source not supported", "Custom code or a third-party tool"],
            ["Occasional queries, small data, freshness not critical", "Lakehouse Federation (query in place)"],
            ["Data already shared by another platform", "Delta Sharing"],
            ["Simple idempotent batch file load", "COPY INTO"],
            ["Heavy transformation during extraction", "Ingest raw first, transform in pipelines"],
            ["Private source the connector cannot reach", "Check private connectivity first"],
            ["Replacing a third-party ELT tool", "Compare real costs for the same sources"]]))
        + sec("hard", "Hard points", "Questions behind the features", ul(["<b>Deletes:</b> log-based CDC captures them; SaaS connectors depend on what the app exposes. Ask per source.", "<b>Schema changes:</b> the connector adapts to many, but downstream contracts must handle a new column.", "<b>First load:</b> a large first snapshot can be heavy; plan for source load and API quotas.", "<b>Source setup:</b> log-based CDC needs the source configured (for example change tracking); the database owner must agree.", "<b>Cost:</b> serverless compute for pipeline and gateway; watch it in system tables.", "<b>Latency:</b> near real time for databases; SaaS sources are limited by API rate and polling.", "<b>Medallion:</b> land as bronze; no business logic in ingestion.", "<b>Recovery:</b> know how a failed run and a full refresh behave."]))
        + sec("ask", "Practice", "Questions to rehearse", qlist(["Lakeflow Connect versus Auto Loader: how do you choose?", "Connect versus Lakehouse Federation: when do you copy and when query in place?", "How does log-based CDC avoid hammering the source?", "How are deletes propagated into the Delta target?", "The source adds a column. What happens?", "How would you justify replacing Fivetran with it?"]))
        + say("Query in place when volume and freshness needs are small; copy with Connect when I need performance, history or isolation from the source."),
        [("Is it the same as Auto Loader?", "No. Auto Loader ingests files from storage. Connect copies from apps and databases."), ("Does it capture deletes?", "Database connectors read the change log, so yes. SaaS depends on the source's API.")])


page_def("lakeflow-connect", "Lakeflow Connect: managed ingestion", "Lakeflow Connect",
         "What Lakeflow Connect is, how it works, when to use it versus Auto Loader, federation, sharing and COPY INTO, and the hard points to know.", p_connect)


# ---------------------------------------------------------------- 8d. uniform
def p_uniform():
    return (
        flow(["Delta commit", "Async step reads new log entries", "Writes Iceberg manifests and metadata.json", "Iceberg engines read the same Parquet"], "One copy of data, two sets of metadata.", "How UniForm works")
        + sec("idea", "The idea", "One copy of data, two sets of metadata", "<p>Delta and Iceberg both store Parquet. Only the metadata differs: Delta uses a JSON log; Iceberg uses metadata files, manifest lists and manifests. UniForm keeps Delta as the source of truth and writes Iceberg metadata beside it.</p>")
        + sec("steps", "Step by step", "What happens on each commit", "<ol><li>A Delta commit happens (write, MERGE, OPTIMIZE).</li><li>After it, asynchronously, a conversion step reads the new log entries.</li><li>It translates them into Iceberg structures (table below).</li><li>It writes new files in a <code>metadata/</code> folder next to <code>_delta_log/</code>: manifests, a manifest list and a new <code>metadata.json</code>.</li><li>The catalog points readers at the latest metadata.json; Unity Catalog exposes an Iceberg REST endpoint.</li><li>Trino, Snowflake, Athena, Flink and others read the Parquet files using that metadata.</li></ol>"
              + T(["Delta", "Iceberg"], [["Table version (commit N)", "A new snapshot"], ["add file action with statistics", "Data file entry in a manifest, with column min, max and null counts"], ["remove file action", "File marked deleted in the new snapshot"], ["Schema and column mapping", "Iceberg schema with field IDs"], ["Partition columns or clustering", "Partition spec"], ["Table properties", "Properties in metadata.json"]]))
        + sec("ids", "Why", "Column mapping and field IDs", "<p>Iceberg identifies columns by numeric field ID, not name. Plain Delta Parquet files usually carry no IDs. So UniForm requires Delta column mapping, which gives each column a stable ID that is also written into the Parquet files. The table must also be in an Iceberg-compatibility mode, which blocks Delta features Iceberg cannot represent. For example deletion vectors must be off or purged; check the current rules.</p>")
        + sec("props", "In practice", "What follows", T(["Property", "Consequence"], [["Single copy", "No duplicate storage, no sync job"], ["Generated metadata", "A small extra write per commit"], ["Asynchronous", "Iceberg readers can lag the latest Delta commit briefly; eventually consistent"], ["One-directional", "Delta writes; Iceberg clients read only"], ["Time travel", "Iceberg snapshots map to Delta versions, limited by retained history; VACUUM affects it"], ["Statistics", "Iceberg skipping uses stats carried over from Delta; no stats, no skipping"], ["Maintenance", "OPTIMIZE and VACUUM on Delta make new commits, which make new Iceberg snapshots"], ["Feature gaps", "Features with no Iceberg equivalent restrict what you can enable"]]))
        + sec("cmp", "Compare", "Related approaches", T(["Approach", "How it works", "Trade-off"], [["UniForm", "Delta writes; Iceberg metadata generated", "One copy, Delta-first, read-only for Iceberg"], ["Apache XTable", "Open-source metadata translator you run yourself", "Same idea, you schedule it"], ["Managed Iceberg tables", "Table is natively Iceberg", "Iceberg is primary; Delta features unused"], ["Copy to a second table", "Duplicate data", "Double cost, stale copies"], ["Delta Sharing", "Live data over a protocol", "For cross-organization sharing"]]) + '<p>See <a href="/learn/delta-vs-iceberg/">Delta vs Iceberg</a> and <a href="/learn/iceberg-lakehouse-aws-databricks/">who owns the catalog</a>.</p>')
        + sec("ask", "Practice", "Questions to rehearse", qlist(["What does UniForm duplicate, and what not?", "Why does it need column mapping?", "Is the Iceberg metadata updated synchronously?", "Can an Iceberg engine write to a UniForm table?", "What happens to Iceberg readers after OPTIMIZE or VACUUM?", "Why might an Iceberg engine scan more than Spark on the same table?", "UniForm or managed Iceberg tables?"]))
        + say("UniForm keeps Delta as the writer. After each commit it translates the log into Iceberg manifests and metadata.json beside the data, so the same Parquet serves both formats. It needs column mapping, is read-only and slightly delayed for Iceberg readers."),
        [("Does UniForm copy my data?", "No. It writes only metadata; the Parquet files are shared."), ("Why can Iceberg engines skip less?", "They rely on statistics carried over from Delta.")])


page_def("uniform", "How UniForm works inside", "UniForm",
         "How Delta UniForm generates Iceberg metadata, why column mapping and field IDs are required, and the consequences and alternatives.", p_uniform)


# ---------------------------------------------------------------- 8e. vector search
def p_vector():
    return (
        flow(["Source Delta table (text, key, optional vectors)", "Embedding model", "Index on a Vector Search endpoint", "Query: filters, hybrid, rerank, top-k"], "Documents become vectors; a query finds the nearest ones.", "Vector Search path")
        + sec("what", "The idea", "What it is", "<p>A managed service for similarity search: you store embeddings and, given a query embedding, it returns the nearest items. It is the retrieval step in RAG and semantic search. Indexes are Unity Catalog objects; a Delta table is the source of truth.</p>")
        + sec("inside", "Internals", "How it works", "<p>Exact search compares a query against every vector, which is too slow at millions. Production systems use approximate nearest neighbour (ANN) search. Databricks' service uses an HNSW-style graph: each vector links to nearby ones; a search enters at a sparse top layer, hops toward the query, drops to denser layers and finishes with a local search. Knobs trade recall, latency, memory and build time; the managed service mostly sets them for you. The distance measure (cosine, dot product, L2) must match the embedding model.</p>"
              + T(["Piece", "Role"], [["Source Delta table", "Text, primary key and optionally the embeddings"], ["Embedding model", "Managed (a hosted endpoint the index calls) or self-managed (you supply vectors)"], ["Endpoint", "The compute that hosts indexes and serves queries"], ["Index", "ANN structure plus stored metadata columns"], ["Sync process", "For Delta Sync indexes, reads changes from the table (needs Change Data Feed)"], ["Query path", "Embed the query, ANN search, filters, optional hybrid and rerank, return top-k with metadata"]])
              + T(["Index type", "How it is fed", "Use when"], [["Delta Sync Index", "Automatic from a Delta table; triggered or continuous sync", "Default"], ["Direct Vector Access", "You upsert and delete through the API", "Source not Delta, or you need control"]])
              + "<p>Search features: metadata filtering; <b>hybrid search</b> (vector plus keyword, merged by reciprocal rank fusion) helps with names and codes; <b>reranking</b> rescoring the top candidates for precision at extra latency.</p>")
        + sec("limits", "Limitations", "What it cannot do", '<p class="verify">Numbers change. Check current limits for index size, dimension, throughput and endpoint types (a standard type for low latency and a storage-optimized type for larger scale).</p>' + T(["Area", "Limitation"], [["Scale caps", "Maximum vectors per index and endpoint, embedding dimension, query and ingest throughput"], ["Eventual consistency", "New rows appear after the sync completes"], ["Change Data Feed", "Required on the source; breaking its history disrupts sync"], ["Schema", "Primary key must be stable; changing the embedding column or model usually means a rebuild"], ["Filter behaviour", "Syntax narrower than SQL; very selective filters can reduce recall or add latency"], ["One model per index", "Cannot mix vectors from different models"], ["No automatic row-level security", "Access is at index and endpoint level through Unity Catalog; per-user rows need filters your application enforces (check current state)"], ["Approximate", "Recall below 100 percent; results can shift after updates"], ["Quality is yours", "Chunking and embedding quality are not decided by the service"], ["Cost floor", "A running endpoint costs money when idle"], ["Availability", "Not every feature in every region or cloud"]]))
        + sec("ingest", "Ingestion", "How to get data in", "<ol><li>Land raw files in a Unity Catalog volume with Auto Loader.</li><li>Parse to text and clean (remove boilerplate and duplicates).</li><li>Chunk into passages of a few hundred tokens with some overlap, respecting headings. Make chunk IDs deterministic (document ID plus position) and keep metadata (source, section, date, access group, version).</li><li>Write chunks to a Delta table with Change Data Feed on and a primary key.</li><li>Create the Delta Sync index with managed or self-managed embeddings.</li><li>Sync after each pipeline run, or continuously if freshness demands.</li><li>Query through the SDK, REST or SQL, with filters and optional hybrid search.</li></ol>"
              + ul(["Batch embedding calls to respect model rate limits.", "Updates and deletes: delete all old chunks of a changed document, then write the new ones; otherwise stale chunks stay searchable.", "Keep parsing separate from embedding so you can re-embed without re-parsing.", "Store the embedding model name and version.", "Direct Vector Access: you own retries, idempotency and ordering."]))
        + sec("prod", "Production", "Production-grade challenges", T(["Challenge", "What to do"], [
            ["Retrieval quality", "Build an evaluation set of real questions with known relevant chunks; measure recall at k and answer quality; change one variable at a time"],
            ["Chunking", "Structure-aware chunks, overlap, parent-document metadata"],
            ["Latency", "Cache frequent query embeddings, limit k, rerank only the top candidates, measure each stage"],
            ["Throughput", "Load test before launch, scale or split indexes, rate-limit callers"],
            ["Filtered recall", "Test filter-heavy queries; consider separate indexes for very different partitions"],
            ["Multi-tenancy", "Enforce the tenant filter on the server, never trusting the client; separate indexes for sensitive tenants; restrict permissions"],
            ["Freshness", "Continuous or short triggered syncs; monitor lag"],
            ["Hybrid needs", "Pure vector search misses exact identifiers; test hybrid on your queries"],
            ["Model dependence", "Pin versions, plan migration, monitor endpoint health and quotas"],
            ["Cost", "Right-size the endpoint, drop unused indexes, avoid re-embedding unchanged content"],
            ["Observability", "Log queries, filters, retrieved chunk IDs, scores and feedback, with privacy controls"],
            ["Sensitive data", "Vectors can leak information about the source text; apply the source's classification and access rules"]]))
        + sec("maint", "Maintenance", "Maintenance challenges", T(["Task", "Detail"], [
            ["Changing the embedding model", "Re-embed the whole corpus and rebuild; run the new index in parallel, compare quality, then switch traffic"],
            ["Changing chunking", "Reprocess and rebuild"],
            ["Sync failures and lag", "Causes: CDF disabled or history vacuumed, schema change, embedding endpoint limits, permissions"],
            ["Source table changes", "Renaming or retyping the key or text column can break the index; treat the table as a contract"],
            ["Deletes and compliance", "Remove chunks from the source and confirm they leave the index; test it"],
            ["Index drift", "Re-run evaluation as data grows or shifts"],
            ["Orphaned or duplicate chunks", "From non-deterministic IDs; reconcile source and index counts regularly"],
            ["Endpoint lifecycle", "Upgrades and scaling may need parallel indexes"],
            ["Disaster recovery", "The index can be rebuilt from the Delta table; know the rebuild time"],
            ["Regression tests", "Run the evaluation set in CI whenever pipeline, model or chunking changes"]]))
        + sec("not", "Choose", "When it is not the right tool", T(["Situation", "Alternative"], [["Exact keyword matching is enough", "SQL, full-text or a search engine"], ["A few thousand vectors", "An in-memory library (governance may still favour the service)"], ["Transactional updates with vectors", "A database with vector support, or Lakebase (check status)"], ["Exotic ANN tuning or distance measures", "A dedicated vector database"], ["Relational queries mixed with similarity", "SQL on Delta for the structured part plus Vector Search for the semantic part"]]))
        + sec("ask", "Practice", "Questions to rehearse", qlist(["Why approximate rather than exact search, and what do you give up?", "Delta Sync versus Direct Vector Access?", "Why does Delta Sync need Change Data Feed?", "How do you handle updates and deletes so stale chunks never appear?", "A user says the answer is wrong. Is retrieval or generation at fault?", "How do you implement multi-tenant isolation?", "Describe a no-downtime embedding model migration.", "Why can strong filters reduce recall?", "How would you size 50 million chunks at 100 queries per second?"]))
        + say("Vector Search is an approximate nearest-neighbour index kept in sync from a Delta table. The hard parts are chunking, evaluation, tenant isolation, updates and deletes, freshness, and the migration whenever the embedding model changes."),
        [("Delta Sync or Direct Vector Access?", "Delta Sync when the data lives in Delta. Direct access when you need control of every upsert."), ("Do the source table's row filters apply to the index?", "Do not assume so. Enforce tenant filters in your application and check the current behaviour.")])


page_def("vector-search", "Vector Search: internals, limits, production and maintenance", "Vector Search",
         "How Databricks Vector Search works inside, its limits, how to ingest, production and maintenance challenges, and when not to use it.", p_vector)


# ---------------------------------------------------------------- 8f. dbt and ODCS
def p_dbt():
    return (
        flow(["SELECT files in Git", "ref() builds the dependency graph", "Tests and docs run with the build", "Tables and views appear in the lakehouse"], "dbt is the T in ELT: tested, documented, version-controlled SQL models.", "How dbt works")
        + sec("dbt", "dbt", "What problems it solves", "<p>dbt handles the transform step. Data is already loaded; dbt takes SELECT statements, works out their order, runs them on your engine, and adds tests, docs and version control. It does not extract, load or process data itself.</p>"
              + T(["Problem before dbt", "What dbt does"], [
                  ["Scattered scripts and procedures nobody can find", "Every transformation is a SQL file in a repo, one model per file"],
                  ["Execution order hand-wired in a scheduler", "{{ ref('orders') }} makes the dependency graph, so order is inferred"],
                  ["Hard-coded table names differ between dev and prod", "Targets switch schema and database; same code everywhere"],
                  ["No review or history for SQL", "Git: pull requests, blame, rollback"],
                  ["Quality checked by hand", "Built-in tests (unique, not null, accepted values, relationships) plus custom SQL tests"],
                  ["Nobody knows what a table means", "Docs next to code and a generated site with a lineage graph"],
                  ["Copy-pasted SQL", "Macros (Jinja) and packages"],
                  ["Boilerplate to create, insert, merge, drop", "You write only the SELECT; a materialization makes it a view, table, incremental model or snapshot"],
                  ["Full reloads of big tables", "Incremental models (append, merge, insert overwrite)"],
                  ["Tracking changing dimensions", "Snapshots implement SCD type 2"],
                  ["No CI for data code", "Run and test only changed models and dependents on a pull request"],
                  ["Metrics defined differently in each dashboard", "Semantic layer (MetricFlow) defines them once"]])
              + "<p><b>Does not solve:</b> ingestion, streaming, non-SQL transformation (Python models exist in some adapters), orchestration of everything else, performance tuning, platform governance, or a bad data design.</p>")
        + sec("dbx", "On Databricks", "dbt-databricks adapter", ul(["Runs SQL on a SQL warehouse or cluster; models become Delta tables and views in Unity Catalog with three-level names.", "Incremental strategies include merge, append, insert_overwrite and replace_where.", "Clustering, partitioning and table properties are set in model config; liquid clustering and materialized views or streaming tables as materializations are supported in recent adapter versions (verify).", "Run it as a task in Databricks Jobs."]))
        + sec("vs", "Compare", "dbt versus Lakeflow Declarative Pipelines", T(["", "dbt", "Declarative pipelines"], [["Language", "SQL with Jinja (Python models in some cases)", "SQL and Python"], ["Strength", "Engineering workflow for SQL models, tests, docs, portable across warehouses", "Streaming, incremental processing, expectations, CDC, managed compute"], ["Streaming", "Not its focus", "First-class"], ["Portability", "Many engines", "Databricks (core upstreamed to Spark)"], ["Testing", "Rich test framework and CI practice", "Expectations inside the pipeline"], ["Typical fit", "Analytics engineering, gold models, multi-warehouse teams", "Ingestion-heavy medallion pipelines, streaming, CDC"]]) + "<p>Many teams use pipelines for ingestion and bronze to silver, and dbt for gold. Others standardize on one. Choose by team skills, streaming needs and portability.</p>")
        + sec("odcs", "ODCS", "Open Data Contract Standard", "<p>ODCS is an open, vendor-neutral YAML specification for a data contract: an agreement between the team that produces a dataset and the teams that consume it. It is maintained by the Bitol project under the Linux Foundation and grew out of PayPal's template. Check the current spec version before quoting section names.</p><p>Most data breakage is communication failure between producers and consumers, not technology failure.</p>"
              + T(["Without a contract", "What goes wrong"], [["A source renames a column or changes a type", "Downstream pipelines and dashboards break; you hear from angry users"], ["A consumer assumes a column is never null", "Silent wrong numbers"], ["No owner named", "Incidents take days to route"], ["Freshness lives in someone's head", "A daily table arrives at noon"], ["Column meaning unclear (currency, tax)", "Different teams compute different answers"], ["Sensitive fields not marked", "Privacy mistakes"], ["Each consumer writes its own checks", "Duplicate, inconsistent rules"], ["Each platform has its own metadata format", "Contracts cannot move between tools"]])
              + T(["Section", "States"], [["Fundamentals", "Name, version, status, domain, description, purpose"], ["Schema", "Tables, columns, types, required, keys, descriptions, classification (such as PII), business terms"], ["Data quality", "Uniqueness, completeness, ranges, row counts, custom SQL checks, with severity"], ["Service levels", "Freshness, latency, availability, retention"], ["Team and roles", "Owner, steward, contacts, access"], ["Servers", "Where the data lives"], ["Support and pricing", "Channels, cost"], ["Custom properties", "Extensions"]])
              + CODE("""
apiVersion: v3.0.0
kind: DataContract
id: orders-contract
name: Orders
version: 1.2.0
status: active
domain: sales
schema:
  - name: orders
    properties:
      - name: order_id
        logicalType: string
        required: true
        unique: true
      - name: customer_email
        logicalType: string
        classification: PII
slaProperties:
  - property: freshness
    value: 24
    unit: h
""") + T(["Contract element", "Where enforced on Databricks"], [["Schema", "Delta schema and constraints, Unity Catalog tables"], ["Quality rules", "Pipeline expectations, dbt tests, generated checks"], ["Ownership, descriptions, tags", "Unity Catalog comments and governed tags"], ["Access", "Grants, row filters, column masks"], ["Freshness and SLAs", "Jobs monitoring, data quality monitoring, alerts"], ["Change management", "CI in Git comparing contract versions"]])
              + "<p>It does not enforce anything by itself; value comes from CI checks and runtime validation. It also does not fix organizational problems. dbt model contracts are narrower: they enforce column names and types at build time. Start with widely used, high-value datasets. See also <a href=\"/concepts/data-contracts/\">data contracts</a>.</p>")
        + sec("ask", "Practice", "Questions to rehearse", qlist(["What does ref() do and why is it more than a table name?", "Table, view, incremental and ephemeral models: when each?", "What can go wrong in an incremental model? (Late data, missing unique key causing duplicates, schema changes.)", "How do snapshots do SCD2?", "How would you run dbt in CI so a pull request builds only what changed?", "dbt versus Lakeflow Declarative Pipelines: how do you choose?", "What breaking changes would you detect in a data contract automatically?", "What happens when a producer violates a contract at 2am?"]))
        + say("dbt gives SQL transformations software-engineering discipline; ODCS gives producers and consumers one written, checkable agreement. Neither does ingestion or enforcement alone."),
        [("Does dbt process the data?", "No. It sends SQL to your engine, which does the work."), ("Is ODCS a tool?", "No. It is a file format; tools read it to generate and run checks.")])


page_def("dbt-and-odcs", "dbt and the Open Data Contract Standard", "dbt and ODCS",
         "What problems dbt solves and where it stops, how it compares with declarative pipelines, and what the Open Data Contract Standard solves.", p_dbt)


# ---------------------------------------------------------------- 8g. data movement cost
def p_movement():
    return (
        flow(["Don't move it", "Move less of it", "Move it by the cheapest path"], "The cheapest transfer is the one you never do.", "Order of preference for data movement")
        + sec("egress", "Egress", "The cheapest way to move data out", '<p class="verify">Prices vary by cloud, region and contract. Check your provider\'s price sheet before quoting a number.</p><p>Cloud providers charge for data leaving a region or the cloud and charge little or nothing for movement inside the same region.</p>'
              + T(["Step", "Options"], [
                  ["Do not move it", "Run compute in the same cloud and region as the storage; query in place and return only results; use Delta Sharing for live reads; move the consumer to the data. Cross-region sharing still incurs egress; Databricks supports a Cloudflare R2 replica for sharing, because R2 has no egress fees (check current support)."],
                  ["Move less", "Filter and aggregate first; select only needed columns; compress (Parquet with zstd or snappy); send increments with change data feed; export columnar not CSV or JSON; cache on the consumer side; cap result sizes so nobody pulls a whole table to a laptop."],
                  ["Cheapest path", "Same region is usually free; cross-region is cheaper than internet; private circuits (Direct Connect, ExpressRoute, Interconnect) have lower per-GB rates but a fixed fee, so they pay only at steady high volume; free-egress stores or a CDN for widely downloaded data; physical transfer devices for one-off petabyte moves; negotiated discounts at scale."]])
              + T(["Hidden egress costs in Databricks", "Detail"], [["Cross-AZ traffic", "Shuffle between zones is charged by some clouds"], ["NAT gateway processing", "Per-GB fees can exceed the transfer itself; use storage gateway endpoints"], ["Cross-region storage reads", "Every query from a workspace in another region is egress"], ["Disaster recovery replication", "Continuous cross-region copies are an ongoing bill; replicate critical tables incrementally"], ["Federation queries", "Pull data from external databases, possibly across regions"], ["Result downloads and exports", "From notebooks and warehouses to local machines"]])
              + "<p>To find the source: use the cloud cost tool filtered on data-transfer lines by region pair, storage access or flow logs, and Databricks system tables (billing, audit, query history). Fix the top one or two sources first.</p>")
        + sec("ingress", "Ingress", "The cheapest way to bring data in", "<p>Inbound transfer to AWS, Azure and Google Cloud is generally free. The cost is the source's egress, the network path you build, the compute that loads, and storage requests.</p>"
              + T(["Source", "Cheapest approach"], [
                  ["Files in cloud storage, same cloud", "Auto Loader, or COPY INTO for simple batch"],
                  ["Files in another region or cloud", "Copy once in bulk, compressed, then ingest locally"],
                  ["Operational database", "Log-based CDC (Lakeflow Connect where supported) or incremental queries on an indexed watermark; avoid full reloads"],
                  ["SaaS apps", "Managed connector if supported, else scheduled incremental API pulls using bulk endpoints"],
                  ["Event streams", "Structured Streaming; availableNow batches if freshness allows"],
                  ["On-premises data", "Compress and upload in bulk; transfer devices for huge one-offs"],
                  ["Another lakehouse or warehouse", "Federation or Delta Sharing, no copy"],
                  ["Big historical backfill", "One run on a right-sized job cluster with spot workers"]])
              + T(["Technique", "Effect"], [["Incremental loads", "Only new or changed data"], ["Compressed columnar files", "Parquet beats CSV and JSON"], ["Files of 128 MB to 1 GB", "Millions of tiny files raise request costs and slow Spark"], ["Land raw, transform later", "Cheap, rerunnable ingest job"], ["Scheduled instead of continuous", "availableNow runs when latency allows"], ["Serverless or job clusters with auto-termination", "Pay only while loading"], ["Spot workers", "Fault-tolerant batch ingestion"], ["File notification mode at large scale", "Avoids repeated listing of huge directories"], ["Lifecycle rules on the landing zone", "Move old raw files to cheaper tiers"]])
              + "<p><b>Hidden costs:</b> NAT gateway processing, private link hourly and per-GB fees, dedicated circuits, cross-AZ and cross-region traffic, third-party ELT tools that charge by rows, request charges, source load, and failed reruns that reload everything (use checkpoints and idempotent writes).</p>")
        + sec("ask", "Practice", "Questions to rehearse", qlist(["How would you reduce egress cost?", "Is Delta Sharing free of egress?", "What hidden costs come with private networking?", "What does ingress cost, really?", "How do you ingest cheaply at scale?", "When would you not ingest at all?"]))
        + say("Co-locate compute and storage, shrink what moves, make transfers incremental, and watch the hidden network fees. Inbound transfer is free; the source, network path and compute are not."),
        [("Is Delta Sharing free of egress?", "No. Data read across regions or clouds is still billed, unless it sits in a store with no egress fee."), ("Why is a NAT gateway a risk?", "It charges per GB processed, which can exceed the transfer cost; storage endpoints avoid it.")])


page_def("egress-and-ingress", "Cheapest way to move data in and out", "Egress and ingress",
         "The cheapest way to egress and ingress data on Databricks: avoid, shrink, then pick the path, with hidden network costs and a way to find them.", p_movement)


# ---------------------------------------------------------------- 9. question bank
def p_questions():
    return (
        flow(["Say the idea in one sentence", "Name the trade-off", "Say how you would measure it", "Give the failure you have seen"], "A shape that works for almost every hard question.", "How to structure an answer")
        + sec("challenges", "Overview", "Major challenges on Databricks and how to overcome them", T(["Challenge", "Why it hurts", "How to overcome it"], [
            ["Small files and bad layout", "Slow scans, high request cost", "Liquid clustering, compaction, Predictive Optimization, fix the writer"],
            ["Data skew", "One task holds up a stage", "Drop junk keys, AQE, isolate or salt hot keys"],
            ["Shuffle volume and spill", "Slow, memory failures", "Filter early, broadcast, aggregate first, right-size"],
            ["Cost overruns", "Idle and mis-typed compute", "Policies, job or serverless compute, incremental loads, tags and budgets"],
            ["Concurrent write conflicts", "Failed commits", "Disjoint data per writer, predicates in MERGE, row-level concurrency, retries"],
            ["Streaming correctness", "Duplicates, late data, state growth", "Checkpoints, idempotent sinks, watermarks, bounded state"],
            ["Governance at scale", "Leaks, unclear ownership", "Unity Catalog, row filters and masks, tags, system tables, contracts"],
            ["Environment drift", "Prod differs from dev", "Asset Bundles, targets, service principals"],
            ["Schema change", "Downstream breakage", "Column mapping, mergeSchema, expectations, versioned views, contracts"],
            ["Driver memory", "Whole application dies", "No collect, small broadcasts, compact files, bigger driver last"],
            ["Retrieval quality in AI features", "Wrong answers", "Evaluation set, chunking, hybrid search, tenant filters"]]))
        + sec("features", "Overview", "Advanced features to know", ul(["Unity Catalog: governance, lineage, system tables, volumes, Delta Sharing, Lakehouse Federation.", "Delta: deletion vectors, liquid clustering, change data feed, column mapping, type widening, UniForm.", "Ingestion and pipelines: Auto Loader, Lakeflow Declarative Pipelines, Lakeflow Connect, AUTO CDC, Lakeflow Jobs.", "Engine: AQE, Photon, serverless, Predictive Optimization, materialized views.", "Semantic and AI: metric views, Genie, Vector Search, AI functions, Model Serving.", "Delivery: Asset Bundles, Databricks Connect.", "Details and status are on the AQE, Photon and PO page; verify what is generally available."]))
        + sec("hard", "Scenarios", "The hardest problems and strong answers", T(["Problem", "Strong answer"], [
            ["Exactly-once streaming to Delta with late and duplicate data", "Checkpoints plus an idempotent sink. Deduplicate on an event ID inside the watermark. Use foreachBatch with MERGE on the event ID so a replayed batch gives the same result. State the late-data decision: data later than the watermark is dropped, so decide whether to keep a side channel."],
            ["ConcurrentAppendException in parallel writers", "Make writers touch disjoint data, put the partition predicate in the MERGE condition, use deletion vectors with row-level concurrency, retry with backoff."],
            ["CDC with out-of-order events and deletes (SCD2)", "AUTO CDC with a sequence column. If hand-written: deduplicate each batch to the latest per key first, because MERGE fails when several source rows match one target row, and guard with the sequence number."],
            ["Right to erasure in a huge table with time travel", "DELETE with deletion vectors, REORG … APPLY (PURGE), VACUUM past retention; cover clones, backups, derived tables and the change data feed."],
            ["20 TB table, every query scans everything", "Check stats coverage, then clustering keys against real filters from query history; move to liquid clustering, fix file sizes, add materialized views for top aggregations; verify with files pruned in the query profile."],
            ["Join skewed by a NULL or default key", "Filter NULLs out and union back; for a real hot key, isolate it and broadcast or salt only that key."],
            ["Multi-tenant platform", "Catalogs or schemas per tenant or domain, row filters or ABAC where tenants share tables, cluster policies with mandatory tags, system tables for chargeback, service principals for production jobs."],
            ["Schema evolution without breaking consumers", "Additive changes with mergeSchema, column mapping for renames, Auto Loader rescued column, expectations to quarantine bad records, versioned views as the consumer interface."],
            ["Migrating to Unity Catalog", "Inventory, upgrade managed and external tables, replace mounts with external locations and volumes, repoint jobs, convert ACLs to grants."],
            ["A job got slow", "Start from evidence: stage time, task spread (skew), spill, input size, plan changes. Most causes are file layout, skew, shuffle volume, a bad join or a UDF."]]))
        + sec("bank", "Rehearse", "Question bank", "<h3>Delta internals</h3>" + qlist([
            "What is in _delta_log and what is a checkpoint? (JSON commits; a Parquet checkpoint every 10 commits so the log need not be replayed from the start.)",
            "How does Delta give ACID on object storage? (Atomic create of the next commit file plus optimistic concurrency.)",
            "How does time travel interact with VACUUM and log retention?",
            "Deletion vectors: benefit and cost?"])
              + "<h3>Performance</h3>" + qlist(["A MERGE into a 5 TB table takes three hours. Diagnose and fix.", "Name AQE's three main features.", "When does a broadcast join fail?", "Why do only the first 32 columns get statistics by default, and what follows for table design?"])
              + "<h3>Streaming and ingestion</h3>" + qlist(["Auto Loader versus COPY INTO versus readStream on files.", "What happens if you change a streaming query's logic and restart on the same checkpoint?", "What does a watermark drop and what does it keep in state?"])
              + "<h3>Governance</h3>" + qlist(["Managed versus external tables: what happens on DROP?", "Dedicated versus standard compute for security.", "How do you give an auditor lineage and access logs? (System tables, audit logs.)"])
              + "<h3>Architecture</h3>" + qlist(["Where do you enforce quality in the medallion layers and where not?", "Design a pipeline that can be rebuilt from scratch. (Immutable bronze, idempotent transforms, deterministic keys.)", "Serverless versus classic for jobs: cost, control, startup."]))
        + sec("ten", "Remember", "Ten sentences to have ready", "<ol><li>OPTIMIZE creates new files, VACUUM removes old ones, and neither changes your data.</li><li>VACUUM shortens time travel and can break long-running readers.</li><li>Liquid clustering replaces partitioning and Z-order for new tables.</li><li>Predictive Optimization removes the maintenance job on managed tables.</li><li>Row filters and masks are SQL functions attached to the table and enforced in the plan.</li><li>Data skipping needs statistics and a layout that benefits from them.</li><li>Skew shows as one slow task, not a slow stage average.</li><li>A stream that does not need to be on all day should use availableNow.</li><li>Idempotent writes plus checkpoints give exactly-once, not the engine alone.</li><li>Measure first (Spark UI, query profile, system tables), then change one thing.</li></ol>")
        + sec("see", "Related", "Learn the base ideas first", '<p><a href="/learn/fundamentals/">Data engineering fundamentals</a> · <a href="/learn/spark-declarative-pipelines/">Declarative pipelines</a> · <a href="/learn/scd2-auto-cdc-vs-pyspark/">SCD2: AUTO CDC or own PySpark</a> · <a href="/learn/streaming/">Streaming on AWS and Databricks</a> · <a href="/learn/data-platform-sim/performance/">Spark performance: 12 problems</a> · <a href="/certifications/">Certifications</a></p>'),
        [("How should I answer a question I am unsure about?", "Say what you know, name what you would check in the docs or the query profile, and say how you would test it. That is a senior answer."),
         ("Which topics come up most for senior roles?", "Delta maintenance and layout, skew and joins, streaming correctness, cost control, and governance.")])


page_def("hard-problems-and-questions", "Hard problems and the question bank", "Question bank",
         "The hardest Databricks data engineering scenarios with strong answers, a question bank by topic, and ten sentences to have ready for an interview.", p_questions)


# ============================================================================ rendering
def siblings(cur):
    return '<div class="sib">' + "".join(
        f'<span>{E(p["short"])}</span>' if p["slug"] == cur else f'<a href="{BASE}{p["slug"]}/">{E(p["short"])}</a>' for p in PAGES) + "</div>"


def render(p, body, qa):
    url = f"{SITE}{BASE}{p['slug']}/"
    full = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › <a href="{BASE}">Databricks interview prep</a> › {E(p['short'])}</p>
<p class="eyebrow" style="margin-top:22px">Databricks interview prep · data engineering</p>
<h1>{E(p['title'])}</h1><p class="lede">{E(p['desc'])}</p>{siblings(p['slug'])}
<p class="verify">Defaults, limits and preview status change often. Check the current Databricks docs before quoting a number.</p>
{body}
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(qa)}</section>
<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2><p><a href="{BASE}">All Databricks interview topics</a> · <a href="/data-engineering/">All data engineering</a> · <a href="/platforms/databricks/">Databricks on this site</a></p>{siblings(p['slug'])}</section>"""
    return wb.page(p["title"], p["desc"], url, full, head(p, url, qa))


def head(p, url, qa):
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": p["title"], "description": p["desc"], "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}]
    return CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)


def hub():
    url = f"{SITE}{BASE}"
    title = "Databricks interview prep for data engineers"
    desc = "Advanced Databricks for data engineering interviews: table maintenance, security, compute, joins, skew, engines, cost, platform features and the hardest questions."
    cards = "".join(f'<div class="card"><h3><a href="{BASE}{p["slug"]}/">{E(p["title"])}</a></h3><p class="one">{E(p["desc"])}</p></div>' for p in PAGES)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › Databricks interview prep</p>
<p class="eyebrow" style="margin-top:22px">Interview prep · data engineering</p><h1>{E(title)}</h1>
<p class="lede">What a core Databricks interviewer asks when the questions get hard: what each command does, why jobs are slow or dear, how security is enforced, and how to answer. Plain words first, then the detail.</p>
<p class="verify">Defaults, limits and preview status change often. Check the current Databricks docs before quoting a number.</p>
<div class="cards">{cards}</div>
<section id="more"><p class="eyebrow">Already on this site</p><h2>Go deeper</h2><p><a href="/learn/spark-declarative-pipelines/">Declarative pipelines</a> · <a href="/learn/metric-views/">Metric views</a> · <a href="/learn/table-maintenance/">Who maintains your tables</a> · <a href="/learn/delta-vs-iceberg/">Delta vs Iceberg</a> · <a href="/learn/scd2-auto-cdc-vs-pyspark/">SCD2 on Databricks</a> · <a href="/learn/streaming/real-time-mode/">Real-time mode</a></p></section>"""
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "description": desc, "url": url, "inLanguage": "en", "isAccessibleForFree": True, "dateModified": DATE}]
    h = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(title, desc, url, body, h)


def build_all():
    """Return {relative path: html}. Pure, so tests can check it without writing files."""
    out = {f"learn/databricks-interview/index.html": hub()}
    for p in PAGES:
        body, qa = p["build"]()
        out[f"learn/databricks-interview/{p['slug']}/index.html"] = render(p, body, qa)
    return out


def main():
    for rel, html in build_all().items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html)
        print("databricks interview ->", path)


if __name__ == "__main__":
    main()
