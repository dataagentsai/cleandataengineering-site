"""Iceberg time travel as SCD Type 2: is it a good pattern? One page at /learn/time-travel-vs-scd2/.

    python3 _guides/time_travel_scd2.py      (then python3 _site/nav.py and python3 _site/seo.py)

Teach first (SCD2 and time travel, drawn), then the two clocks, a worked example with real
numbers, why it breaks, where time travel is right, the recommended pattern (changelog feeds an
SCD2 MERGE; tags for period-end copies), verdicts. The SCD2 MERGE and as-of join were run on
Spark 3.5.1 + Delta 3.2.0 on 2026-11-11 (same SQL on Iceberg in Spark). The Iceberg procedure and
tag DDL are Iceberg's Spark syntax and were not run here.
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
URL_PATH = "/learn/time-travel-vs-scd2/"
DATE = "2026-11-11"
TITLE = "Iceberg time travel as SCD Type 2: is it a good pattern?"
DESC = ("Can Apache Iceberg (or Delta) time travel replace a Slowly Changing Dimension Type 2 table? "
        "No: it keeps commit time, not business time, it expires, and it cannot join facts as of their own dates. "
        "Where time travel does help, and the pattern to use instead.")

CSS = C.CSS + """<style>
  .tt .fig { border:var(--line); border-radius:var(--wob); padding:12px 14px; margin:16px 0; background:#fff; overflow-x:auto; }
  .tt .fig svg { width:100%; min-width:680px; height:auto; display:block; } .tt .fig text { font-family:var(--hand); fill:#111; }
  .tt .fig p { font-size:13.5px; color:var(--muted); margin:6px 0 0; }
  .tt .box { border:var(--line); border-radius:var(--wob); padding:10px 16px; margin:14px 0; background:var(--butter-wash); }
  .tt .warn { border:var(--line); border-radius:var(--wob); padding:10px 16px; margin:14px 0; background:var(--rose-wash); }
  .tt table.t td { font-size:14px; } .tt td.v { font-weight:700; }
</style>"""


def fig(d, cap):
    return f'<div class="fig">{d}<p>{E(cap)}</p></div>'


def d_two_ideas():
    i = t(250, 26, "SCD Type 2: history as rows", 18, "middle") + t(750, 26, "Time travel: history as copies of the table", 18, "middle")
    i += bx(20, 50, 460, 40, ["customer 7 · Pune · from 1 Jan 2025 · to 10 Mar 2026"], "w", 14)
    i += bx(20, 100, 460, 40, ["customer 7 · Delhi · from 10 Mar 2026 · to (open) · current"], "g", 14)
    i += t(250, 172, "both versions sit in one table, side by side;", 14, "middle")
    i += t(250, 190, "a fact joins to the row valid on its own date", 14, "middle")
    for k, (lbl, f) in enumerate([("snapshot 1 · written 1 Jan 2025 · Pune", "w"), ("snapshot 2 · written 15 Mar 2026 · Delhi", "g")]):
        i += bx(540 + k * 18, 50 + k * 50, 400, 40, [lbl], f, 14)
    i += t(750, 172, "each version is the whole table at one commit;", 14, "middle")
    i += t(750, 190, "one query reads one snapshot", 14, "middle")
    return svg(1000, 205, "SCD Type 2 keeps history as rows in one table, each with valid-from and valid-to business dates. Time travel keeps history as snapshots of the whole table, one per commit, and one query reads one snapshot.", i)


def d_two_clocks():
    i = '<path d="M40,110 L960,110" stroke="#111" stroke-width="1.5" marker-end="url(#bia)"/>'
    for x, lbl in [(140, "1 Mar"), (330, "10 Mar"), (480, "12 Mar"), (620, "15 Mar")]:
        i += f'<path d="M{x},104 L{x},116" stroke="#111" stroke-width="1.5"/>' + t(x, 134, lbl, 14, "middle")
    i += bx(250, 20, 170, 54, ["customer moves", "to Delhi (business time)"], "g", 14) + ar(330, 74, 330, 102)
    i += bx(400, 160, 160, 54, ["order 101", "placed"], "y", 14) + ar(480, 158, 480, 118)
    i += bx(540, 20, 200, 54, ["our load writes it", "(commit time)"], "r", 14) + ar(620, 74, 620, 102)
    i += t(500, 245, "SCD2 knows the move happened on 10 Mar. Time travel only knows the table changed on 15 Mar.", 14, "middle")
    return svg(1000, 258, "Two clocks. The customer moved on 10 March (business time), order 101 was placed on 12 March, and the load wrote the change on 15 March (commit time). SCD2 records 10 March; time travel only knows 15 March.", i)


def d_pattern():
    i = bx(10, 80, 170, 70, ["silver.customer", "(Iceberg or Delta)"], "w")
    i += bx(220, 80, 200, 70, ["changelog since the", "last processed snapshot"], "b", 14)
    i += bx(460, 80, 200, 70, ["SCD2 MERGE", "close old row, add new"], "y", 14)
    i += bx(700, 80, 280, 70, ["gold.dim_customer", "valid_from · valid_to · is_current"], "g", 14)
    i += ar(180, 115, 218, 115) + ar(420, 115, 458, 115) + ar(660, 115, 698, 115)
    i += bx(220, 190, 440, 50, ["time travel's real job here: read only what changed"], "l", 14)
    i += ar(320, 188, 320, 152, True)
    i += bx(700, 190, 280, 50, ["tag month-end snapshots", "for frozen period copies"], "r", 14)
    return svg(1000, 250, "The recommended pattern: read the changelog of silver.customer since the last processed snapshot, apply an SCD2 MERGE that closes the old row and adds a new one, and write gold.dim_customer with valid-from and valid-to. Time travel's job is to find what changed. Tag month-end snapshots for frozen period copies.", i)


EXAMPLE = [
    ("Customer 7 moves from Pune to Delhi", "10 Mar 2026 (business time)"),
    ("The CRM extract with the move lands and is loaded", "15 Mar 2026 (commit time, snapshot 2)"),
    ("Order 101 placed by customer 7", "12 Mar 2026"),
    ("SCD2 join: order date between valid_from and valid_to", "Delhi (right)"),
    ("Time travel: dim_customer as of 12 Mar", "Pune (wrong: the move was not loaded yet)"),
    ("Time travel, 3 months later, after snapshots older than 5 days expired", "Error: no snapshot for 12 Mar"),
]

BREAKS = [
    ("Wrong clock", "Time travel records when we wrote the data (commit time). Reports need when it was true in the business (effective time). Late files, backdated corrections and reloads all put the change on the wrong date."),
    ("History expires", "Iceberg's snapshot expiry (by default it keeps about 5 days) and Delta's VACUUM (7 days by default) delete old versions on purpose. Managed tables run it for you. Keep snapshots forever and storage grows without end."),
    ("Facts cannot join 'as of their own date'", "A fact table with a million orders on 400 different days needs 400 versions of the dimension in one query. Time travel gives one version per table reference. SCD2 does it with one range join."),
    ("Storage cost explodes", "A one-row change rewrites a whole data file (copy-on-write), and compaction rewrites files again. Every old file is kept for time travel. SCD2 adds one small row per change."),
    ("Changes inside one load are lost", "Time travel only sees one state per commit. If an address changed twice between loads, the middle value never existed for it. A changelog or CDC feed with timestamps keeps both."),
    ("Answering 'when did this change?' is slow", "You must diff snapshots one pair at a time. In SCD2 it is a WHERE clause on valid_from."),
    ("Deleting a person's data (GDPR, DPDP)", "Removing one customer from old snapshots means expiring those snapshots for everyone, which wipes all history. In SCD2 you delete or mask that customer's rows."),
    ("Reloads look like changes", "A backfill, a schema change or a full reload creates a new snapshot where nothing changed in the business."),
    ("Tools cannot express it", "BI tools, metric views and Genie query tables, not snapshot ids. valid_from and valid_to are plain columns any tool can filter."),
]

WORKS = [
    ("Every change is loaded the same day it happens, and never backdated", "Then commit time is close enough to business time."),
    ("Readers only ask 'show me the whole table as of date X'", "One snapshot per query is fine; no fact needs its own date's version."),
    ("Snapshot retention is set longer than the history anyone will ask for", "Otherwise expiry deletes the history; default expiry and VACUUM keep only days."),
    ("The table is small and changes rarely", "So keeping every rewritten file costs little."),
    ("No duty to delete one person's data from history", "Otherwise you must destroy snapshots for everyone."),
    ("At most one change per key between loads", "Otherwise the in-between values never existed in any snapshot."),
]

OPS = [
    ("Reprocessing a day or a backfill", "A new snapshot, even if the business values are the same; with overwrite, every row in the rewritten partitions looks new.",
     "Fake changes dated on the rerun day; real history now mixed with technical noise.", "No new rows: the MERGE compares a hash of tracked columns, so unchanged values are skipped."),
    ("Full reload or INSERT OVERWRITE of the table", "One snapshot where the whole table is 'replaced'.",
     "Every record appears to change on reload day; earlier corrections can be undone silently.", "Same as above: only real differences make new rows, dated by the source effective date."),
    ("Correcting old data (a wrong city from January fixed in March)", "The fix lands in a March snapshot; January snapshots still hold the wrong value.",
     "Old reports keep the wrong value forever, or you lose the fix if you read as of January.", "Update the January row's attribute or valid dates on purpose, with an audit column; the change is visible and tested."),
    ("Compaction (Iceberg rewrite_data_files, Delta OPTIMIZE)", "A new snapshot with the same rows in fewer files; old files kept until expiry.",
     "Snapshot list fills with no-change versions; storage doubles until expiry runs.", "No effect on rows."),
    ("Snapshot expiry (expire_snapshots) or VACUUM", "Old snapshots and their files are deleted.",
     "History is gone. This runs automatically on managed tables.", "No effect: maintenance never removes rows."),
    ("Rollback (Iceberg rollback_to_snapshot, Delta RESTORE)", "Iceberg makes an older snapshot current; Delta writes a new version equal to an old one.",
     "Everything written after that point drops out of the 'history', or appears twice.", "Rerun the SCD2 build from the restored source; idempotent MERGE gives the same table."),
    ("Schema change (add, rename or drop a column)", "New snapshots carry the new schema; old ones keep theirs.",
     "Queries across versions see different columns; renamed columns break comparisons.", "Add the column with NULL for old rows; one schema for all history."),
    ("Re-creating the table (DROP and CREATE, moving catalog or region, migration to a new format)", "A new table starts with one snapshot; old history does not come along (a deep clone copies only the current version).",
     "All history lost at the move.", "Rows move with the data; history survives."),
    ("Deleting one person's data", "A delete commit; old snapshots still hold the person until they expire.",
     "To truly delete, expire those snapshots, which wipes everyone's history.", "Delete or mask that person's rows only."),
]

CLEAN = [
    ("Is the meaning explicit in the data model?", "No: history lives in table metadata, not in columns. Nobody reading the schema can see it.", "Yes: valid_from, valid_to, is_current are columns in the contract."),
    ("Who owns it?", "Whoever sets snapshot expiry or VACUUM, often a platform team or the managed service, for storage reasons.", "The data product owner, for business reasons."),
    ("Can a housekeeping change break it silently?", "Yes: one expire_snapshots run or a shorter retention deletes years of history.", "No: maintenance never deletes rows."),
    ("Does it use the right clock?", "Commit time only.", "Business effective time from the source."),
    ("Is it portable across engines and tools?", "Snapshot ids and syntax differ by engine and catalog; BI tools, metric views and Genie cannot use them.", "Plain columns and a range join work everywhere."),
    ("Can it be tested?", "Hard: depends on how many snapshots happen to exist.", "Yes: assert no overlaps, one current row per key, gaps closed."),
    ("Separation of concerns", "Mixes storage concerns (files, retention) with business concerns (history).", "Keeps them apart."),
]

GOOD = [
    ("Audit and debugging", "What did this table look like when last Tuesday's report ran?", "Pursue"),
    ("Rollback after a bad load", "Roll the table back to the snapshot before the bad commit.", "Pursue"),
    ("Reproducing an ML training set or a past report", "Record the snapshot id with the model or report; re-read it later (within retention, or tag it).", "Pursue"),
    ("Finding what changed since the last run", "Incremental reads and changelogs use snapshots to feed downstream jobs, including the SCD2 build.", "Pursue"),
    ("Period-end frozen copies (month-end balances)", "Tag the snapshot with a long retention: a named, kept version, separate from SCD2.", "Pursue, with tags"),
    ("Replacing SCD Type 2 dimensions", "Wrong clock, expiry, no as-of join, storage cost.", "Drop"),
]

DECIDE = [
    ("Dimension attributes that change and facts must see the value at their own date (customer region, product price band, employee grade)", "Explicit SCD2 table built by MERGE", "Pursue"),
    ("Only the current value matters", "SCD Type 1 (overwrite); time travel covers short-term debugging", "Pursue"),
    ("Need the table exactly as it was at each month-end, for regulators", "Iceberg tags (or Delta shallow clones) at each period end, with long retention", "Pursue"),
    ("Small reference table, a few changes a year, nobody joins facts to history", "Time travel for audit only, with retention set long enough", "Pursue only for audit, not reporting"),
    ("Keep every snapshot forever and call it SCD2", "—", "Drop"),
]

QA = [
    ("Can Iceberg time travel replace SCD Type 2?", "No. Time travel keeps versions by commit time, not business effective time; old snapshots are expired on purpose; and one query reads one snapshot, so facts cannot join to the dimension value valid on each fact's own date. Build an explicit SCD2 table and use time travel for audit, rollback and incremental reads."),
    ("Is Delta Lake time travel any different?", "No, for this question. Delta keeps versions by commit too, and VACUUM removes old files (7 days by default). The same reasons apply."),
    ("How do I use Iceberg snapshots to build SCD2?", "Read only what changed since the last processed snapshot (Iceberg's create_changelog_view procedure in Spark, or Delta's change data feed), then run an SCD2 MERGE that closes the current row and inserts the new one, using the business effective date from the source."),
    ("What are Iceberg tags good for?", "Keeping a named snapshot, for example month-end, for a set number of days even when normal snapshots expire. Good for frozen period copies and reproducible reports; not a replacement for SCD2."),
    ("Does reprocessing affect time travel history?", "Yes. Every rerun, backfill, full reload, compaction or rollback writes or replaces snapshots, so time travel shows technical changes as if the business changed, and expiry or table re-creation removes history. An SCD2 table built by an idempotent MERGE that compares a hash of tracked columns ignores reruns and compaction."),
    ("Why not just keep snapshots forever?", "Every rewrite and compaction keeps old data files, so storage grows with every change to any row in a file; deleting one person's data means destroying history; and you still have commit time, not business time."),
]

SOURCES = [
    ("Apache Iceberg: Spark queries and time travel", "https://iceberg.apache.org/docs/latest/spark-queries/"),
    ("Apache Iceberg: Spark procedures (expire_snapshots, create_changelog_view)", "https://iceberg.apache.org/docs/latest/spark-procedures/"),
    ("Apache Iceberg: branching and tagging", "https://iceberg.apache.org/docs/latest/branching/"),
    ("Delta Lake: table history and time travel", "https://docs.delta.io/latest/delta-utility.html"),
]


def page():
    url = f"{SITE}{URL_PATH}"
    ex = C.table(["What happens", "When / result"], EXAMPLE)
    brk = C.table(["Problem", "Why it bites"], BREAKS)
    good = vtable(["Use", "How", "Verdict"], GOOD)
    ops = C.table(["Operation", "What it does to snapshots", "If time travel is your SCD2", "Explicit SCD2 table"], OPS)
    works = C.table(["Condition", "Why it is needed"], WORKS)
    clean = C.table(["Clean-design test", "Time travel as SCD2", "Explicit SCD2 table"], CLEAN)
    dec = vtable(["Situation", "Use", "Verdict"], DECIDE)
    src = "".join(f'<li><a href="{u}">{E(n)}</a></li>' for n, u in SOURCES)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/data-engineering/">Data engineering</a> › Time travel vs SCD Type 2</p>
<p class="eyebrow" style="margin-top:22px">Data engineering · free guide · one page</p>
<h1>{E(TITLE)}</h1>
<p class="lede">Iceberg (and Delta) can read a table as it was at an earlier snapshot. So why build a Slowly Changing Dimension Type 2 table at all? This page shows, with one small example, why time travel is not a replacement, where it does help, and the pattern to use instead.</p>
<div class="tt">
<div class="box"><b>Will it work?</b> Only in a narrow case: a small table, changes loaded the day they happen, long retention, and nobody joining facts to past versions (<a href="#works">when it works</a>). <b>When does it not work?</b> Late or backdated data, snapshot expiry, facts that need the value on their own date, data deletion duties, storage cost (<a href="#breaks">nine cases</a>), and every rerun, backfill, reload, compaction or rollback, which time travel records as if the business changed (<a href="#ops">technical operations</a>). <b>Is it clean design?</b> No: it hides business history inside a storage housekeeping setting (<a href="#clean">why</a>).<br><br><b>So: not as a replacement.</b> Time travel remembers when <i>we wrote</i> data, keeps it only for days, and gives one version of the table per query. SCD Type 2 remembers when something was <i>true in the business</i>, keeps it as long as you need, and lets each fact join to the version valid on its own date. Use time travel to <b>feed</b> SCD2 (read only what changed), for audit and rollback, and use tags for frozen month-end copies.</div>

<section id="plain"><p class="eyebrow">In plain words</p><h2>Two ways to keep history</h2>
<p><b>SCD Type 2</b> (Slowly Changing Dimension, Type 2) keeps every version of a record as its own row, with the dates it was valid: <code>valid_from</code>, <code>valid_to</code> and <code>is_current</code>. When customer 7 moves city, the Pune row is closed and a Delhi row is added. See <a href="/concepts/scd/">the SCD concept page</a>.</p>
<p><b>Time travel</b> is a table-format feature. Every commit to an Iceberg or Delta table creates a new snapshot (version), and you can read an old one: <code>SELECT * FROM dim_customer TIMESTAMP AS OF '2026-03-12'</code>. It looks like free history. It is history, but of a different kind.</p>
{fig(d_two_ideas(), "SCD2 keeps versions as rows you can join. Time travel keeps versions as whole copies you can read one at a time.")}</section>

<section id="clocks"><p class="eyebrow">The core difference</p><h2>Two clocks</h2>
<p>Every change has two times. <b>Business time</b>: when it became true in the world (the customer moved on 10 March). <b>Commit time</b>: when our pipeline wrote it (the file arrived and loaded on 15 March). Reports, finance and regulators care about business time. Time travel only knows commit time.</p>
{fig(d_two_clocks(), "Late data is normal: files arrive late, corrections are backdated, reloads happen. Commit time is the wrong clock for reporting.")}
<h3>The example, with real dates</h3>{ex}
<p>The SCD2 answer was checked by running the SQL below on Spark 3.5.1 with Delta 3.2.0; the same SQL runs on Iceberg tables in Spark.</p></section>

<section id="works"><p class="eyebrow">Question 1</p><h2>Will it work? Only when all of these are true</h2>{works}
<p>If even one is false, you get wrong answers or lost history, usually months later, when someone asks for an old report.</p></section>

<section id="breaks"><p class="eyebrow">Question 2</p><h2>When it does not work: nine cases</h2>{brk}
<div class="warn"><b>The one that ends the debate:</b> a report joins a million orders, placed on hundreds of different days, to the customer's region <i>on the day of each order</i>. SCD2 does that in one join. Time travel would need one query per day.</div></section>

<section id="ops"><p class="eyebrow">Question 2, continued</p><h2>What technical operations do to time-travel 'history'</h2>
<p>A table changes for technical reasons all the time: reruns, backfills, reloads, compaction, rollbacks, migrations. Each one writes or removes snapshots. Time travel cannot tell a technical change from a business change, so every one of them corrupts or deletes the history. An explicit SCD2 table built with an idempotent MERGE ignores them.</p>
{ops}
<div class="warn"><b>In practice:</b> after the first reprocessing, time-travel "history" mixes real business changes with rerun noise, and nobody can separate them afterwards.</div></section>

<section id="clean"><p class="eyebrow">Question 3</p><h2>Is it clean design? No</h2>{clean}
<div class="box"><b>The clean-design rule:</b> history the business relies on is <i>data</i>, with its own columns, owner, contract and tests. Time travel is a <i>storage feature</i> for audit, rollback and incremental reads. Do not let one pretend to be the other.</div></section>

<section id="good"><p class="eyebrow">Where it is right</p><h2>What time travel is good for</h2>{good}</section>

<section id="pattern"><p class="eyebrow">The pattern</p><h2>Use the snapshots to feed SCD2</h2>
{fig(d_pattern(), "Snapshots find what changed; the MERGE turns it into business-dated history; tags keep the month-end copies.")}
<h3>1. Read only what changed (Iceberg, Spark)</h3>
{C.code('''-- Iceberg Spark procedure: a view of rows changed between two snapshots
CALL lake.system.create_changelog_view(
  table => 'silver.customer',
  options => map('start-snapshot-id', '<last processed snapshot>'),
  identifier_columns => array('customer_id'),   -- turns delete+insert pairs into updates
  net_changes => true,                           -- one net change per key
  changelog_view => 'customer_changes');''', "Iceberg's Spark syntax; not run on this page. On Delta, read the change data feed with table_changes() instead. Store the last processed snapshot id in your metadata store.")}
<h3>2. Apply SCD2 with the business date from the source</h3>
{C.code('''-- Close the current row when an attribute changed
MERGE INTO gold.dim_customer d
USING changes c
  ON d.customer_id = c.customer_id AND d.is_current
WHEN MATCHED AND d.city <> c.city THEN
  UPDATE SET d.valid_to = c.effective_date, d.is_current = false;

-- Add the new current row (new customers and changed ones)
INSERT INTO gold.dim_customer
SELECT c.customer_id, c.city, c.effective_date, DATE'9999-12-31', true
FROM changes c
LEFT JOIN gold.dim_customer d
  ON d.customer_id = c.customer_id AND d.is_current
WHERE d.customer_id IS NULL;''', "Run on Spark 3.5.1 + Delta 3.2.0: the Pune row closed on 2026-03-10 and a current Delhi row was added. effective_date comes from the source system, never from the load time.")}
<h3>3. Join facts as of their own date</h3>
{C.code('''SELECT f.order_id, f.order_date, d.city
FROM fact_orders f
JOIN gold.dim_customer d
  ON f.customer_id = d.customer_id
 AND f.order_date >= d.valid_from
 AND f.order_date <  d.valid_to;
-- order 100 (20 Feb) -> Pune,  order 101 (12 Mar) -> Delhi''', "Output from the same run. One join, every fact gets the version valid on its own date.")}
<h3>4. Keep frozen month-end copies with tags</h3>
{C.code('''-- Iceberg (Spark SQL): keep this snapshot for 7 years even when others expire
ALTER TABLE gold.account_balances CREATE TAG `eom-2026-10` RETAIN 2555 DAYS;

SELECT * FROM gold.account_balances VERSION AS OF 'eom-2026-10';''', "Iceberg's Spark syntax; not run on this page. On Delta, a shallow clone per period end does the same job.")}
<p>Pick SCD2 changes with a hash of the tracked columns for wide tables, handle several changes per key in one batch by ordering on the effective date, and keep the SCD2 build idempotent so a rerun gives the same table. The <a href="/learn/data-platform-architecture/bronze-to-silver/">bronze-to-silver page</a> has a full SCD2 MERGE with these cases.</p></section>

<section id="decide"><p class="eyebrow">Choosing</p><h2>Which to use, by situation</h2>{dec}</section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(QA)}</section>
<section id="sources"><p class="eyebrow">Sources</p><h2>Checked against</h2><ul>{src}</ul></section>
<section id="next"><p class="eyebrow">Related</p><h2>Where it connects</h2>
<p><a href="/concepts/scd/">Slowly changing dimensions</a> · <a href="/learn/data-platform-architecture/bronze-to-silver/">Bronze to silver, with SCD2 code</a> · <a href="/learn/delta-vs-iceberg/">Delta vs Iceberg</a> · <a href="/learn/table-maintenance/">Who maintains your tables (snapshot expiry, VACUUM)</a> · <a href="/data-engineering/">All data engineering</a></p></section>
</div>"""
    crumbs = [("Data engineering", f"{SITE}/data-engineering/"), ("Time travel vs SCD Type 2", url)]
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": TITLE, "description": DESC, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in QA]}]
    head = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(TITLE, DESC, url, body, head)


def main():
    out = ROOT / "learn" / "time-travel-vs-scd2"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("time travel vs scd2 ->", out / "index.html")


if __name__ == "__main__":
    main()
