"""Upstreams, the big picture (run from _guides/data_systems.py main()).

  /learn/data-systems/upstreams/big-picture/

One page that puts every part of "source and source extraction" on one map: where sources live,
what happens to rows inside them, every route out (query pull, log-based replication, vendor
extractors such as SAP's, APIs, file drops, streams, events, shares), the bookmark we keep on each
route, and the problems a data engineer has to expect. It links into the sections of the Upstreams
page and its in-depth pages rather than repeating them. map_svg() is also shown on the Upstreams page.
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("data_systems_for_bp", ROOT / "_guides" / "data_systems.py")
ds = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ds)
E, wb, SITE, BASE = ds.E, ds.wb, ds.SITE, ds.BASE
FILL, arrow, svg, text = ds.FILL, ds.arrow, ds.svg, ds.text
U = f"{BASE}upstreams/"
SLUG = "big-picture"
INK = "#1F1F1F"
GREEN, AMBER, RED = "#1d6b3a", "#8a5a00", "#a3322b"

CSS = """<style>
  h3.sub { font-size:23px; margin:26px 0 6px; }
  .route { border:var(--line); border-radius:var(--wob); padding:12px 18px; background:var(--w, #fff); margin:14px 0; }
  .route h3 { margin:0 0 4px; font-size:24px; } .route p { margin:6px 0; } .route ul { margin:6px 0; padding-left:20px; } .route li { margin:4px 0; }
  .route .more { font-size:14.5px; color:var(--muted); }
  .warn { border:var(--line); border-radius:var(--wob); padding:12px 18px; background:#FFF6F6; margin:14px 0; }
  .warn p { margin:4px 0; }
  pre.bp { background:var(--surface-2); border:1px solid var(--rule); border-radius:6px; padding:12px 14px; overflow-x:auto; font-family:var(--mono); font-size:13px; line-height:1.5; }
  ol.steps { padding-left:22px; } ol.steps li { margin:6px 0; }
  table.t td .y { color:#1d6b3a; font-weight:700; } table.t td .n { color:#a3322b; font-weight:700; } table.t td .m { color:#8a5a00; font-weight:700; }
</style>"""


def tbl(head, rows, raw=False):
    """A table. With raw=True the cells are already HTML (used where a cell holds a link)."""
    h = "".join(f"<th>{E(x)}</th>" for x in head)
    b = ""
    for r in rows:
        cells = [c if raw else E(c) for c in r]
        b += "<tr>" + "".join(f"<td>{'<b>' + c + '</b>' if i == 0 else c}</td>" for i, c in enumerate(cells)) + "</tr>"
    return f'<div class="tw"><table class="t"><tr>{h}</tr>{b}</table></div>'


def a(href, label):
    return f'<a href="{href}">{E(label)}</a>'


# =============================================================================================
# Drawings
# =============================================================================================

SOURCES = [
    ("Databases, on-prem", "Oracle, SQL Server, DB2, mainframe"),
    ("Databases, cloud", "managed PostgreSQL, MySQL, NoSQL"),
    ("Packaged apps", "SAP, Dynamics, Oracle EBS"),
    ("SaaS apps", "Salesforce, Workday, ServiceNow"),
    ("Partners and people", "files, spreadsheets, portals"),
    ("Devices and apps", "IoT, clicks, logs, app events"),
]

# (route, what it does, sees deletes?, colour of that verdict, push or pull, fill)
ROUTES = [
    ("Query-based pull", "SELECT what changed since last time, or the whole table", "deletes: no", RED, "pull · on a clock", "butter"),
    ("Log-based replication (CDC)", "read the transaction log: every insert, update, delete", "deletes: yes", GREEN, "push · continuous", "mint"),
    ("Vendor extractor (SAP and others)", "ODP, SLT, CDS views: the vendor's own delta", "deletes: usually", AMBER, "push or pull", "mint"),
    ("API", "bulk export, paged reads, delta tokens", "deletes: rarely", RED, "pull · on a clock", "butter"),
    ("File drop", "SFTP or object storage, with a done marker or manifest", "deletes: only if sent", AMBER, "push · in batches", "butter"),
    ("Stream", "Kafka, Kinesis, Event Hubs: subscribe and replay", "deletes: if designed in", AMBER, "push · continuous", "mint"),
    ("Events and webhooks", "the source says 'this changed' or 'the batch is ready'", "deletes: sometimes", AMBER, "push · a signal", "mint"),
    ("Share or mirror", "read the tables in place, no copy job", "deletes: yes", GREEN, "in place", "peri"),
]

OURS = [
    ("Landing", ["as delivered, never edited"], 62),
    ("Bookmark", ["watermark, log position,", "offset, token, file ledger"], 80),
    ("Checks before load", ["complete? in order?", "seen before? counts match?"], 80),
    ("Bronze", ["every row, with when", "and how it arrived"], 80),
    ("Trigger", ["a clock, or a signal", "from the source"], 80),
]


def map_svg():
    b = ""
    # left: sources
    b += f'<rect x="10" y="10" width="250" height="492" rx="18" fill="{FILL["grey"]}" stroke="{INK}" stroke-width="1.6"/>'
    b += text(135, 40, "Sources", 24, fill=INK) + text(135, 60, "where the data is born", 15)
    for i, (t, s) in enumerate(SOURCES):
        y = 74 + i * 70
        b += f'<rect x="25" y="{y}" width="220" height="62" rx="12" fill="#fff" stroke="{INK}" stroke-width="1.3"/>'
        b += text(135, y + 26, t, 19, fill=INK) + text(135, y + 46, s, 14)
    # middle: routes
    b += f'<rect x="290" y="10" width="510" height="492" rx="18" fill="#fff" stroke="{INK}" stroke-width="1.6"/>'
    b += text(545, 40, "Ways out of the source", 24, fill=INK) + text(545, 60, "each route sees different changes", 15)
    for i, (t, s, d, dc, pp, fill) in enumerate(ROUTES):
        y = 74 + i * 53
        b += f'<rect x="305" y="{y}" width="480" height="46" rx="11" fill="{FILL[fill]}" stroke="{INK}" stroke-width="1.3"/>'
        b += text(318, y + 20, t, 19, anchor="start", fill=INK) + text(318, y + 38, s, 14.5, anchor="start")
        b += text(775, y + 20, d, 15, anchor="end", fill=dc) + text(775, y + 38, pp, 14, anchor="end")
    # right: our side
    b += f'<rect x="840" y="10" width="250" height="492" rx="18" fill="{FILL["rose"]}" stroke="{INK}" stroke-width="1.6"/>'
    b += text(965, 40, "Our side", 24, fill=INK) + text(965, 60, "what we must keep and check", 15)
    y = 74
    for t, lines, h in OURS:
        b += f'<rect x="855" y="{y}" width="220" height="{h - 8}" rx="12" fill="#fff" stroke="{INK}" stroke-width="1.3"/>'
        b += text(965, y + 24, t, 19, fill=INK)
        for j, ln in enumerate(lines):
            b += text(965, y + 43 + j * 16, ln, 14)
        y += h + (8 if h == 62 else 8)
    b += arrow(262, 256, 288, 256) + arrow(802, 256, 838, 256)
    # bottom: what goes wrong
    b += f'<rect x="10" y="516" width="1080" height="72" rx="16" fill="#FFF6F6" stroke="{INK}" stroke-width="1.4" stroke-dasharray="6 5"/>'
    b += text(550, 540, "What goes wrong on the way", 20, fill=INK)
    b += text(550, 561, "deletes nobody saw · updates with no modified time · a first load too big to read in one go · files read while still being written", 15)
    b += text(550, 579, "loads that start before the data is ready · duplicates and replays · changes out of order · schema changes · a source slowed down by us", 15)
    return svg(1100, 598, b, "The upstream map. Six kinds of sources on the left; eight ways out of a source in the middle, each marked with whether it sees deletes and whether it is push or pull; on the right what the platform keeps: landing, a bookmark, checks before load, bronze and a trigger. Underneath, the problems to expect."), \
        "The upstream map. Every source reaches us by one or more of eight routes. The route decides which changes we can see, and the rest of this page follows from that."


def clock_svg():
    def lane(y, label, ok):
        s = text(10, y + 18, label, 17, anchor="start", fill=INK)
        s += f'<rect x="325" y="{y}" width="408" height="26" rx="6" fill="{FILL["grey"]}" stroke="{INK}" stroke-width="1.2"/>'
        s += text(617, y + 18, "source is writing tonight's export", 13)
        if ok:
            s += f'<rect x="733" y="{y - 6}" width="5" height="38" fill="{GREEN}"/>'
            s += text(905, y - 12, "done marker and manifest land at 02:40", 13.5, anchor="end", fill=GREEN)
            s += f'<line x1="746" y1="{y - 2}" x2="746" y2="{y + 44}" stroke="{GREEN}" stroke-width="2"/>'
            s += text(905, y + 60, "load starts at 02:41 and the counts match the manifest", 13.5, anchor="end", fill=GREEN)
        else:
            s += f'<line x1="500" y1="{y - 10}" x2="500" y2="{y + 44}" stroke="{RED}" stroke-width="2"/>'
            s += text(500, y + 60, "load starts at 02:00, reads a half-written file, and succeeds", 13.5, fill=RED)
        return s
    b = ""
    for lab, x in [("01:00", 150), ("01:30", 325), ("02:00", 500), ("02:30", 675), ("03:00", 850)]:
        b += text(x, 20, lab, 13) + f'<line x1="{x}" y1="28" x2="{x}" y2="232" stroke="#ccc" stroke-width="1" stroke-dasharray="3 5"/>'
    b += lane(52, "On a clock", False) + lane(160, "On a signal", True)
    return svg(920, 240, b, "Two timelines for the same night. On a clock, the load starts at 02:00 while the source is still writing and reads half a file. On a signal, the load starts when the done marker lands at 02:40 and reads all of it."), \
        "The same night, twice. The source finished 40 minutes late. The scheduled load read half the data and reported success; the signalled load waited for the marker."


# =============================================================================================
# Content
# =============================================================================================

LEADERS = [
    "There are only about eight ways data leaves a source system. Which one a source allows decides what we can see, how fresh it is, and what can go wrong.",
    "The hardest facts to get are the ones the source does not record: that a row was deleted, or that a row changed. If the source can't tell us, we pay to work it out by comparing.",
    "Reading from the database's change log, or from the vendor's own extractor, sees every change. Querying tables on a schedule is easier to start and sees less.",
    "The first load of a big table is a small project of its own. It needs a plan agreed with the people who run the source.",
    "Loads that start on a signal from the source (the file is complete, the batch is done) remove most late and partial loads. Loads that start at a fixed time are guessing.",
]

WHERE = [
    ("On-premises", "Databases and apps in your own data centre, mainframes, plant systems",
     "A private link or VPN, and usually a small agent or gateway installed inside the network that reads the source and sends data out",
     "Firewall and access changes take weeks, so ask early. Bandwidth limits the first load. The source shares hardware with the business, so there are extraction windows. A DBA has to agree to log reading."),
    ("Cloud databases", "Managed PostgreSQL, MySQL, SQL Server, Oracle; NoSQL stores",
     "A private endpoint, a read replica, or the cloud's own change capture service writing to storage or a stream",
     "Moving data between regions or clouds is charged per gigabyte. A replica can lag. Change logs kept for our reader fill the source's disk if our reader stops."),
    ("SaaS applications", "Salesforce, Workday, ServiceNow, payment and marketing tools",
     "Only what the vendor exposes: APIs, bulk exports, change events, a connector, sometimes a share",
     "We never see the database. Rate limits are shared with every other integration. The vendor upgrades on its own calendar and fields change."),
    ("Partners and other companies", "Suppliers, banks, agencies, regulators",
     "Files over SFTP or object storage, sometimes an API",
     "The contract is the only control we have. Agree names, format, done marker, corrections and timing before the first file."),
    ("The edge", "Machines, sensors, vehicles, stores, mobile apps",
     "A gateway that buffers messages and forwards them to a stream or to files",
     "Connections drop, so data arrives late and in bursts. Device clocks are wrong. The same reading is sent twice after a retry."),
]

# what happens in the source | query pull | log CDC | how to track it
OPS = [
    ("Insert", "<span class='y'>Yes</span>, if the modified time or a rising id is set on insert", "<span class='y'>Yes</span>",
     "A created time or an id that only goes up. Both are easy; this is the one change every route sees."),
    ("Update through the app", "<span class='y'>Yes</span>, if the app sets the modified time", "<span class='y'>Yes</span>, with the old and new values if the log is set to keep them",
     "A modified time set by the database (a trigger or a default), not by each screen of the app."),
    ("Update that skips the modified time", "<span class='n'>No</span>. The row looks unchanged", "<span class='y'>Yes</span>",
     "Bulk scripts, data fixes run by a DBA and some batch jobs write straight to the table. Only the log or a full comparison finds these."),
    ("Soft delete", "<span class='y'>Yes</span>. It is an update to a flag or a deleted-at time", "<span class='y'>Yes</span>",
     "Ask which column, and whether soft-deleted rows are purged later (that purge is a hard delete)."),
    ("Hard delete", "<span class='n'>No</span>. There is no row left to find", "<span class='y'>Yes</span>, with the key of the row",
     "The log, a delete log table in the source, or a comparison of keys. See the section on deletes below."),
    ("Truncate or table reload", "<span class='m'>By accident</span>. Every row looks new, or the table looks empty", "<span class='m'>It depends</span>. One truncate event, or nothing at all",
     "Ask whether any job empties and refills the table. If one does, treat the dataset as a full load."),
    ("Key change", "<span class='m'>Partly</span>. The new key appears; the old key never leaves", "<span class='y'>Yes</span>, as a delete of the old key and an insert of the new",
     "Ask whether keys are ever corrected or merged (two customers made into one). Without the log, a key comparison finds the orphan."),
    ("Archiving and purging", "<span class='n'>No</span>", "<span class='y'>Yes</span>, and it looks exactly like a business delete",
     "Housekeeping removes old rows that the business still counts. Ask for the archiving rules, and do not delete from the platform when the source archives."),
    ("Late or backdated change", "<span class='m'>Only inside the look-back window</span>", "<span class='y'>Yes</span>, in the order it was committed",
     "A posting dated last month, entered today. Use the time the row changed to find it and the business date to place it."),
    ("Long transaction", "<span class='n'>Can be missed for good</span>", "<span class='y'>Yes</span>, when it commits",
     "A row stamped 10:00 that commits at 10:07 is invisible to a load at 10:05, and the next load starts after 10:05. Re-read an overlap on every run."),
    ("Schema change", "<span class='m'>Fails, or silently drops the new column</span>", "<span class='m'>It depends on the tool</span>",
     "Compare the source's column list with the last run before loading. Ask for notice of changes; expect not to get it."),
]

SAP_ROUTES = [
    ("ODP with the business extractors", "The same extractors SAP BW uses. They hold the business logic and hand over a delta from a queue inside SAP that remembers what each subscriber has had.",
     "Finance, logistics and sales data on ECC and S/4HANA where an extractor exists", "Not every extractor has a delta; some are full only. Some logistics extractors need set-up runs. Starting the delta again means a new full load."),
    ("ODP on CDS views", "On S/4HANA, views marked for extraction. Many carry change data capture, so the delta includes deletes.",
     "S/4HANA, and the direction SAP itself is taking", "Only views released for extraction. Custom fields may need the view extended."),
    ("SLT replication", "A replication server puts triggers on chosen tables and ships each change within seconds.",
     "Table-level, near real time, real deletes", "It is trigger-based, so it adds work to every write. It needs its own server or add-on and a licence. You get raw tables with no business logic."),
    ("Table reads over RFC", "A function call that reads a table directly.",
     "Small configuration and text tables", "No delta. Row width and size limits. Never for the large document tables."),
    ("OData services, APIs and BAPIs", "SAP's published services, some with delta tokens.",
     "S/4HANA Cloud, where little else is allowed; small and medium volumes", "Paging and volume limits; delta tokens expire."),
    ("IDocs and business events", "SAP sends a message when a business document is created or changed.",
     "Feeding other applications as things happen", "Only what was configured to be sent. It is not a complete copy of the data."),
    ("Reading the database or its log", "Change capture on the database underneath SAP.",
     "Rarely possible", "Most SAP licences do not allow other tools to read the database. On older ECC systems some tables are stored packed and cannot be read this way at all."),
    ("BW or Datasphere as the hand-over point", "SAP's own warehouse extracts, and we read its output.",
     "When BW or Datasphere already holds the data, modelled", "We inherit its schedule, its transformations and its gaps. Check the licence terms for sending data out."),
]

SAP_HABITS = [
    "Every table carries a client number. Filter to the right client, or test and training data mixes with production.",
    "Amounts are stored as if every currency had two decimals. Yen and other currencies without decimals have to be shifted using SAP's currency table, or they are wrong by a factor of 100.",
    "A deletion flag on a document is not a deleted row, and an archived document is not a business delete. Ask for both rules.",
    "Empty dates arrive as 00000000, and customer and material numbers carry leading zeros that screens hide. Decide once how keys are written, or joins miss.",
    "Texts live in separate tables, one row per language. Changes to documents are recorded in change-document tables, which is often the only history.",
    "Custom tables and fields (the Z ones) are not covered by standard extractors.",
]

DELETES = [
    ("Read the change log", "Every hard delete arrives as an event carrying the key.", "The only route that needs nothing from the app. Needs the log switched on and kept long enough."),
    ("Soft delete in the source", "The app marks the row instead of removing it. A query pull sees the update.", "Ask whether marked rows are purged later, and whether support staff ever delete directly in the database."),
    ("A delete log in the source", "A trigger or the app writes the key and time of each delete into a small table we read.", "A change on the source side; it has to be asked for. Cheap to read once it exists."),
    ("Compare the keys", "Pull only the key column (narrow and cheap), and find keys we hold that the source no longer has.", "A failed or partial key pull looks like a mass delete. Use the same filter on both sides."),
    ("Compare a full snapshot", "Read everything and compare with what we hold.", "Fine for small tables and as a weekly safety net. Costly on large ones."),
    ("A deleted-records call on an API", "Some APIs list what was deleted, usually only for a limited number of days.", "Read it more often than the retention period, or deletes are lost for good."),
    ("A delete record in the file or stream", "The row is sent with an operation of D, or an event with the key and an empty body.", "Has to be in the contract. A delta file with no delete records cannot carry deletes."),
]

MODIFIED_LIES = [
    "It is set by the app, and a bulk script or a fix run directly in the database does not go through the app.",
    "It holds a date with no time, so every change today has the same value and the boundary rows are loaded twice or not at all.",
    "It is the app server's clock, and two servers disagree by a few seconds.",
    "It is stamped when the change starts, and the row becomes visible later when the transaction commits, after our load has moved on.",
    "It is local time, and one hour repeats every autumn.",
    "A child row changes (a new order line) and the parent's modified time does not move.",
]

BIG_LOAD = [
    "Write down where you are starting from before reading anything: the log position or the time. Changes made during the copy are picked up from there afterwards.",
    "Split the table into chunks by key range, date or partition. Record each chunk as done, so a failure at 92% restarts one chunk and not the table.",
    "Read from somewhere that is not the live system if you can: a replica, a restored backup, or the database's own export to files.",
    "Run a few chunks in parallel, with the number agreed with the people who run the source, inside an agreed window.",
    "Check each chunk as it lands: row count and a total or two against the source.",
    "Switch to incremental from the position written down in step one. Rows copied and then changed arrive twice; a merge on the key makes that harmless.",
    "Load the newest data first when the business can use it before the history arrives.",
]

FULL_LOAD = [
    ("It gets slower every month", "A full load that took ten minutes at go-live takes three hours two years later and runs into the next one.", "Record the duration of every run. Move the dataset to incremental before it outgrows its window."),
    ("A half-finished load replaces good data", "The read fails at 60% and the target now holds 60% of the table.", "Load into a staging copy, check it, then swap it in as one step. A failed run leaves yesterday's table in place."),
    ("The source hands over nothing", "The export broke and wrote an empty file. The full load faithfully empties the table.", "Compare the row count with the last run and stop when it falls outside an agreed range."),
    ("'Full' is not the whole table", "The extract is the last two years only. Everything older looks deleted.", "Write the extract's filter into the contract and apply the same filter when comparing."),
    ("History is overwritten", "Yesterday's values are gone, so nobody can say what a report showed last week.", "Keep each day's snapshot in bronze, or compare snapshots and store the changes."),
    ("The table changes while it is read", "A row moves from one page to another during the read and is seen twice or not at all.", "Read as of one moment (a snapshot read) where the database supports it."),
]

HALF_FILE = [
    ("Write under a temporary name, then rename", "The source writes orders.csv.tmp and renames it when finished. A rename is one step, so the real name never points at a partial file.", "Best. Needs the source to do it."),
    ("A done marker or manifest written last", "A small second file appears only when the data file is complete.", "Best for sets of files, and it can carry counts."),
    ("An event when the object is complete", "Object storage shows an object only once the upload has finished, and can raise an event.", "Good for a single file. SFTP servers and shared drives do not behave this way. A set of files still needs a manifest."),
    ("Wait until the size stops changing", "Check the size twice, some minutes apart.", "A last resort. A stalled upload also stops changing."),
]

MANIFEST_SOLVES = [
    ("files, with rows and checksum", "A file cut short, or damaged on the way", "We count and checksum each file before loading and refuse a mismatch."),
    ("the list itself", "One file of a set is missing", "Three files are listed and two arrived, so we wait or raise an alert, and do not load two thirds of a day."),
    ("business_date", "Which day this is, whatever time it arrived", "A file for Friday that arrives on Monday is loaded as Friday."),
    ("sequence", "Files arriving out of order, or one skipped", "Sequence 41 after 39 means 40 is missing. A delta is never applied over a gap."),
    ("load_type", "Is this everything, or only changes?", "A full file can show deletes by comparison; a delta cannot."),
    ("replaces", "A corrected file sent again", "We know it is a correction of an earlier delivery and not new data to add on top."),
    ("total_rows and control totals", "Proof that nothing was lost", "The sum of amounts in the file equals the sum the source reported."),
    ("schema_version", "Columns added or reordered without notice", "A new version is held for review and not loaded into the wrong columns."),
    ("the manifest arriving at all", "Empty file or broken export?", "A manifest saying zero rows means no data today. No manifest by the deadline means something broke."),
]

MANIFEST_EXAMPLE = """{
  "dataset": "orders",
  "business_date": "2026-11-18",
  "sequence": 412,
  "load_type": "delta",
  "schema_version": 7,
  "replaces": null,
  "files": [
    {"name": "orders_20261118_001.csv.gz", "rows": 120400, "sha256": "9f2c..."},
    {"name": "orders_20261118_002.csv.gz", "rows": 118950, "sha256": "41ab..."}
  ],
  "total_rows": 239350,
  "control_totals": {"order_amount": "18422019.55"},
  "written_at": "2026-11-19T02:40:07Z"
}"""

SCHEDULE = [
    ("The source finishes late", "We load half the data, or yesterday's again, and report success.", "The load starts when the source says it is ready, however late."),
    ("The source finishes early", "The data sits unused until the clock comes round.", "The load starts the minute the data is ready."),
    ("Padding between chained jobs", "Each job is scheduled an hour after the one before, to be safe. Five jobs make five hours.", "Each step starts when the one before it finishes."),
    ("Time zones and clock changes", "02:00 happens twice one night a year and not at all on another.", "No clock is involved."),
    ("Month end and holidays", "The source runs a longer job, or does not run, and our schedule does not know.", "No data, no event, no load. A missing event is itself the alert."),
    ("A re-run on the source side", "The corrected data arrives after we have already loaded.", "The correction raises a new event and is loaded as a correction."),
]

EVENT_RULES = [
    "An event can arrive twice. The load must be safe to run twice for the same delivery.",
    "An event can be lost. Keep a slow sweep (list the folder, ask the API) that picks up anything with no event.",
    "Silence is not good news. Set a deadline: if no 'ready' event has arrived by 06:00, raise an alert.",
    "The event should say what is ready (which dataset, which business date, which manifest), not only that something happened.",
]

BOOKMARKS = [
    ("Query-based pull", "The highest modified time or id we have loaded, per table", "Save it only after the load has committed. Re-read an overlap each run. If it is lost, do a full comparison."),
    ("Log-based replication", "The position in the log (the names differ by database: LSN, SCN, binlog position)", "If our reader is down for longer than the log is kept, the changes are gone and the table needs a new snapshot."),
    ("SAP ODP", "A subscription held in SAP's delta queue", "The bookmark lives in the source. Starting the subscription again means a new full load."),
    ("API", "A cursor, a delta token, or a changed-since time", "Tokens expire. Know how long they last and what a full resync costs."),
    ("File drop", "A ledger of every delivery loaded: name, checksum, manifest sequence", "The ledger is what makes a re-sent file harmless and a missing file visible."),
    ("Stream", "An offset for each partition or shard", "Messages are kept for a fixed time. Fall further behind than that and there is a gap."),
    ("Events and webhooks", "The ids of events already handled, and the time of the last catch-up sweep", "Used to drop repeats and to know from when to sweep."),
    ("Share or mirror", "The version of the table we last read", "The provider decides how long old versions are kept."),
]

MORE = [
    ("Duplicates and replays", "Every route re-sends: a retry after a timeout, a file sent twice, a log reader restarting from an earlier position.",
     "Make every load safe to repeat: merge on the business key and keep the newest by an ordering column.",
     f'{a(U + "#keys", "No key, or duplicates")} · {a("/concepts/idempotency/", "Idempotency")}'),
    ("Changes out of order", "The cancellation arrives before the order. Two updates carry the same timestamp.",
     "Name the column that orders versions and a tie-breaker. Apply by that order, never by arrival.",
     f'{a(U + "#missing", "No ordering column")} · questions H and O'),
    ("Schema changes", "A column is added, renamed, widened or reordered, with no notice.",
     "Compare with the last known schema before loading. Accept additions, hold everything else for a person.",
     f'{a("/concepts/schema-evolution/", "Schema evolution")} · questions J'),
    ("Slowing the source down", "A heavy read at 10 a.m. slows the order screen, and the access is withdrawn.",
     "Read a replica or the log, in agreed windows, with a cap on parallel reads.",
     f'{a(U + "#protect", "Protecting the source")} · questions C'),
    ("Tables read at different moments", "Orders read at 02:00 and order lines at 02:10. Lines exist whose order we do not hold.",
     "Read related tables as of one moment, or keep the orphans and join again on the next run.",
     f'{a(U + "#joins", "How joins go wrong")} · {a(U + "joins/", "Learning the joins")}'),
    ("Paging over data that is changing", "Rows shift between pages while we read, so some are skipped and some repeat.",
     "Page by a stable key or a cursor, never by page number.",
     f'{a(U + "apis/#paging", "API pagination")}'),
    ("Limits and quotas", "The daily API quota is shared with five other integrations and runs out at 3 p.m.",
     "Know the quota and who else uses it. Prefer bulk exports for volume.",
     f'{a(U + "apis/#protect", "API load and cost")}'),
    ("Time zones and clocks", "A timestamp with no zone. A business day that ends at 6 a.m.",
     "Record the zone for every date column and store one standard zone.",
     f'{a(U + "#fields", "Fields in every dataset")} · questions H'),
    ("Text and number formats", "An accent turned to a question mark, 1.234 that meant one thousand, a comma inside a name.",
     "Fix encoding, separators and quoting in the file contract.",
     f'{a(U + "files/#problems", "Common file problems")}'),
    ("No proof that nothing was lost", "The load is green and the total is 2% low. Nobody can say where.",
     "Reconcile counts and totals with the source on every run.",
     f'questions N · {a("/concepts/data-quality/", "Data quality")}'),
    ("Personal and restricted data", "A free-text notes column holding card numbers.",
     "Classify columns before the first extract, and mask at the earliest point.",
     f'questions M · {a(U + "#profile", "Why we scan your data")}'),
    ("Nobody owns the source", "A column changes meaning and nobody tells us, because nobody knew we read it.",
     "A named owner and a data contract for every source.",
     f'questions A · {a("/concepts/data-contracts/", "Data contracts")}'),
]

CHOOSE = [
    "If the source can share or mirror its tables on a platform we already use, read them in place.",
    "If it is a packaged application, use the vendor's extractor. Do not read the database underneath without checking the licence.",
    "If it is a database we may read and deletes or freshness matter, read the change log.",
    "If the log is not allowed, pull by a modified time the database sets, re-read an overlap, and compare keys on a schedule to find deletes.",
    "If the table is small, load all of it every time. It is the simplest route and it sees everything.",
    "If the only way in is an API, use bulk export for volume and changed-since calls for the rest, with a full resync now and then.",
    "If the source can only send files, agree the contract and the manifest first.",
    "Whatever the route, start the load on a signal from the source where one exists, and check completeness before loading where it does not.",
]

FAQ = [
    ("What are the main ways to extract data from a source system?",
     "Eight: a query that pulls what changed, replication from the database's transaction log (change data capture), the vendor's own extractor for packaged applications such as SAP, an API, files the source drops, a stream we subscribe to, events or webhooks the source sends, and tables shared in place. Most estates use several."),
    ("How do you detect rows deleted in a source system?",
     "A hard delete leaves no row to query. The ways to see it are to read the database's change log, to have the source mark rows as deleted instead of removing them, to read a delete log the source keeps, or to compare the source's keys with ours and treat the missing ones as deleted. A guard should stop the load when far more rows than usual appear deleted."),
    ("What if a table has no last-modified column?",
     "Read the change log if the database allows it, use a row version or change tracking feature if the database has one, or read the whole table and compare a hash of each row with the last load. Asking the source team to add a modified time set by the database is also reasonable."),
    ("How do you avoid reading a file that is still being written?",
     "Do not load a file because it exists. Load it when the source says it is complete: the file is renamed from a temporary name, or a done marker or manifest is written after it. A manifest also lists the files, their row counts and checksums, so a partial or missing file is caught before loading."),
    ("Why is event-based ingestion better than a schedule?",
     "A schedule starts at a fixed time and assumes the data is ready. When the source is late, the load reads partial data and still succeeds. An event-based load starts when the source signals that the data is complete, so lateness delays the load and does not corrupt it. Keep a catch-up sweep and a deadline alert, because events can be lost."),
]


def big_picture():
    m_svg, m_cap = map_svg()
    c_svg, c_cap = clock_svg()
    leaders = "".join(f"<li>{E(x)}</li>" for x in LEADERS)
    faq = "".join(f'<details class="faq"><summary>{E(q)}</summary><p>{E(ans)}</p></details>' for q, ans in FAQ)
    li = lambda xs: "".join(f"<li>{E(x)}</li>" for x in xs)  # noqa: E731
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › <a href="{BASE}">Data systems</a> › <a href="{U}">Upstreams</a> › The big picture</p>
<p class="eyebrow" style="margin-top:22px">Data systems · upstreams · the whole map on one page</p>
<h1>Upstreams, the big picture</h1>
<p class="promise">Every way data leaves a source, what each way can and cannot see, and the problems to expect.</p>
<p class="lede">The <a href="{U}">Upstreams page</a> lists the questions to ask a source owner. This page is the map behind those questions: where sources live, what happens to rows inside them, the eight routes out, and what goes wrong on each. Every part links to the section that goes deeper.</p>
<div class="leaders"><h3>For leaders</h3><ul>{leaders}</ul></div>
<nav class="toc"><b>On this page</b><ol>
<li><a href="#map">The map</a></li><li><a href="#where">On-premises, cloud, SaaS, partners, the edge</a></li><li><a href="#ops">What happens inside a source, and how to track it</a></li>
<li><a href="#routes">The routes, one by one</a></li><li><a href="#sap">SAP: several ways in</a></li><li><a href="#deletes">Deletes: how do we know?</a></li>
<li><a href="#nomodified">Updates with no last-modified time</a></li><li><a href="#bigload">Big tables and full loads</a></li><li><a href="#halffile">A file read while it is being written</a></li>
<li><a href="#manifest">What a manifest does</a></li><li><a href="#schedule">Schedule or event</a></li><li><a href="#bookmark">Keeping our place</a></li>
<li><a href="#more">The rest of the problems</a></li><li><a href="#choose">Choosing a route</a></li><li><a href="#faq">Questions people ask</a></li><li><a href="#next">Where to go next</a></li></ol></nav>

<section id="map"><p class="eyebrow">The map</p><h2>Sources, the ways out, and what we keep</h2>
<p>Read it left to right. A source is one of six kinds. Its data leaves by one or more of eight routes. On our side we keep the data as delivered, a bookmark that says how far we have read, and a set of checks that run before anything is loaded.</p>
<figure class="diagram">{m_svg}<figcaption>{E(m_cap)}</figcaption></figure>
<p>Two labels on each route matter most. <b>Deletes</b> says whether the route can tell us a row was removed. <b>Push or pull</b> says who starts the conversation: on a pull we ask on our clock, on a push the source sends when something happens. The Upstreams page has the full comparison in <a href="{U}#types">Seven kinds of sources</a> and <a href="{U}#handover">Push, pull or share</a>.</p></section>

<section id="where"><p class="eyebrow">Where sources live</p><h2>On-premises, cloud, SaaS, partners and the edge</h2>
<p>Where a source runs decides how we are allowed to reach it, before any question about tables.</p>
{tbl(["Where", "Examples", "How we reach it", "What to watch"], WHERE)}
<p>Questions <a href="{U}#questions">B (access route) and C (protecting the source)</a> on the Upstreams page cover this for each system.</p></section>

<section id="ops"><p class="eyebrow">Inside the source</p><h2>What happens to rows in a source, and how each change can be tracked</h2>
<p>A source does more to its rows than insert, update and delete. Each of the things below happens in real systems. The two middle columns show whether a scheduled query and a log reader can see it.</p>
{tbl(["What happens in the source", "Does a query pull see it?", "Does a log reader see it?", "How to track it"], [(E(x), q, lg, E(h)) for x, q, lg, h in OPS], raw=True)}
<p>The worked example of a missed update and a missed delete is in <a href="{U}#change">How a dataset changes</a>. Questions <a href="{U}#questions">G (how the data changes)</a> ask a source owner about each row of this table.</p></section>

<section id="routes"><p class="eyebrow">The routes</p><h2>The routes out of a source, one by one</h2>

<div class="route" id="query" style="--w:var(--butter-wash)"><h3>1 · Database, query-based extraction</h3>
<p>We connect to the database and run a query. Either we read the whole table, or we read the rows whose modified time (or id) is higher than the highest one we loaded last time. That remembered value is called a watermark.</p>
<ul><li><b>Good for:</b> small and medium tables, sources with a modified time the database itself sets, teams that cannot get approval to read the log.</li>
<li><b>It cannot see:</b> hard deletes, and any change that did not move the modified time.</li>
<li><b>Watch for:</b> rows that commit late and fall behind the watermark, many rows sharing one timestamp at the boundary, a heavy query on the live system during business hours, and related tables read at different moments.</li>
<li><b>Do:</b> read from a replica, re-read an overlap on every run and merge on the key, and compare keys or run a full comparison on a schedule to catch what the query missed.</li></ul>
<p class="more">More: <a href="{U}#load">Full load or incremental: the patterns</a> · <a href="{U}#missing">No last-modified column</a> · <a href="/concepts/incremental-loads/">Incremental loads</a></p></div>

<div class="route" id="log" style="--w:var(--mint-wash)"><h3>2 · Database, log-based replication (change data capture)</h3>
<p>Every database writes each change to a transaction log before applying it, so that it can recover after a crash. A log reader follows that log and passes on every insert, update and delete, in the order they were committed. It does not query the tables, so the load on the source is small.</p>
<ul><li><b>Good for:</b> busy tables, deletes that matter, data needed within minutes, sources where the modified time cannot be trusted.</li>
<li><b>How it starts:</b> a first full copy of the table (the snapshot), then the stream of changes from the position noted before the copy began. Rows changed during the copy arrive twice, and a merge on the key settles them.</li>
<li><b>Watch for:</b> the database keeping log for us while our reader is stopped, which fills its disk; log removed before we read it, which forces a new snapshot; tables with no primary key; column changes on the source; one very large transaction arriving as millions of changes at once; and a reader that restarts and sends the last few changes again.</li>
<li><b>It needs:</b> the right logging switched on (so that updates and deletes carry the old values), a DBA who agrees, and monitoring of how far behind the reader is.</li></ul>
<p class="more">More: <a href="{U}#handover">Push, pull or share</a> (log-based and trigger-based capture compared) · <a href="/concepts/cdc/">Change data capture</a> · <a href="/learn/scd2-auto-cdc-vs-pyspark/">Applying a change feed as history</a></p></div>

<div class="route" id="vendor" style="--w:var(--mint-wash)"><h3>3 · The vendor's own extractor</h3>
<p>Packaged applications such as SAP, Salesforce and Dynamics usually do not let other tools read their database. They provide their own way to hand data over, which knows the application's business rules and its deletes. SAP has several, covered in <a href="#sap">the next section</a>.</p>
<p class="more">More: <a href="{U}#types">Seven kinds of sources</a></p></div>

<div class="route" id="api" style="--w:var(--butter-wash)"><h3>4 · API</h3>
<p>We call the application over the web and it returns records, a page at a time or as a bulk export. Changes come from a changed-since filter or a delta token.</p>
<ul><li><b>Watch for:</b> rate limits shared with other integrations, paging over data that is changing, tokens that expire, and deletes, which most APIs do not report.</li></ul>
<p class="more">More: <a href="{U}apis/">API sources</a> (kinds of APIs, pagination, limits, cost, deletes)</p></div>

<div class="route" id="files" style="--w:var(--butter-wash)"><h3>5 · File drop</h3>
<p>The source writes files to an SFTP server or to object storage, and we pick them up. It is the oldest route and still the most common one between companies.</p>
<ul><li><b>Watch for:</b> files read before they are complete, files sent twice, files out of order, one file of a set missing, and columns that change without notice. A <a href="#manifest">manifest</a> answers most of these.</li></ul>
<p class="more">More: <a href="{U}files/">File sources</a> (the file contract, done markers, corrections, formats)</p></div>

<div class="route" id="stream" style="--w:var(--mint-wash)"><h3>6 · Stream</h3>
<p>The source writes messages to a stream (Kafka, Kinesis, Event Hubs, Pub/Sub) and we subscribe. The stream keeps messages for a set time, so we can stop, restart and replay from where we were.</p>
<ul><li><b>Watch for:</b> the same message delivered twice, messages out of order across partitions, the shape of a message changing, messages that cannot be parsed (send them to a side queue, do not stop the stream), and falling behind by more than the stream keeps.</li></ul>
<p class="more">More: <a href="/learn/streaming/">Streaming</a> · <a href="{U}#questions">questions O (streams and real time)</a> · <a href="/concepts/queues/">Queues</a></p></div>

<div class="route" id="events" style="--w:var(--mint-wash)"><h3>7 · Events and webhooks</h3>
<p>The word covers two different things, and it helps to keep them apart.</p>
<ul><li><b>Events that carry data.</b> The app publishes "order placed" or "order cancelled" as it happens, or calls our address (a webhook). These hold business meaning that a table change does not. They are only as complete as the developers made them, so a catch-up pull is still needed.</li>
<li><b>Events that carry a signal.</b> "The file has landed", "tonight's batch is complete". These carry no data. They tell us when to start loading, and they are what replaces a schedule. See <a href="#schedule">Schedule or event</a>.</li></ul>
<p class="more">More: <a href="{U}#trigger">Schedule or event</a> · <a href="{U}#handover">Outbox and webhooks</a></p></div>

<div class="route" id="share" style="--w:var(--peri-wash)"><h3>8 · Share or mirror</h3>
<p>The source exposes its tables and we read them where they are, with no copy job. It works within a platform or a vendor family.</p>
<ul><li><b>Watch for:</b> who pays for the queries, how fresh the share is, and what happens to us when the owner changes or withdraws it.</li></ul>
<p class="more">More: <a href="{U}#handover">Push, pull or share</a></p></div>
</section>

<section id="sap"><p class="eyebrow">A packaged application</p><h2>SAP: several ways in, and none of them is "read the table"</h2>
<p>SAP is the clearest case of a source with its own rules. The data sits in thousands of tables with short names, the licence usually forbids reading the database directly, and the business meaning lives in the application layer. So the first question is which routes this SAP system and this licence allow.</p>
{tbl(["Route", "How it works", "Good for", "Watch for"], SAP_ROUTES)}
<div class="warn"><p><b>Check the licence before the design.</b> Two limits surprise teams. Many SAP database licences cover use by SAP only, which rules out a log reader on the database. And SAP has published a note (3255746) saying that tools from other vendors are not permitted to call the ODP interface over RFC; the OData route is the supported one. Ask the SAP team and the tool vendor for their current position in writing.</p></div>
<p><b>SAP habits to know before the first load:</b></p>
<ul>{li(SAP_HABITS)}</ul>
<p>The same thinking applies to any packaged application: ask for the vendor's extraction route first, and ask what it does about deletes and custom fields.</p></section>

<section id="deletes"><p class="eyebrow">Problem 1</p><h2>Deletes: how do we know?</h2>
<p>A row that was deleted cannot be queried, because it is not there. A scheduled query sees inserts and updates and reports success, and the deleted customer stays in every report. This is the most common way a platform drifts from its source.</p>
<p>There are seven ways to find out, best first:</p>
{tbl(["Way", "How it works", "Watch for"], DELETES)}
<p>Three rules hold whichever way is used:</p>
<ul><li><b>Never delete from bronze.</b> Record that the row was deleted and when we found out. Silver marks it; reports decide whether to show it.</li>
<li><b>Guard against a mass delete.</b> If a run would mark far more rows deleted than usual, stop and ask. It is nearly always a failed extract.</li>
<li><b>Separate archiving from deleting.</b> When the source moves old rows to an archive, the business still counts them. Ask for the archiving rules.</li></ul>
<p>More: <a href="{U}#change">How a dataset changes</a> · <a href="{U}#load">which load pattern sees hard deletes</a> · <a href="{U}#questions">questions G</a> · <a href="{U}apis/#problems">deletes on APIs</a></p></section>

<section id="nomodified"><p class="eyebrow">Problem 2</p><h2>Updates with no last-modified time, or one that cannot be trusted</h2>
<p>An incremental query depends on one column: the time the row last changed. Many tables do not have it. The options when it is missing are set out in <a href="{U}#missing">No last-modified column, or no date to order history</a>. In short: read the change log; use a row version or change tracking feature if the database has one; compare a hash of each row with the last load; treat a table that is only ever added to as append-only and follow its id; or ask the source team to add a modified time set by the database.</p>
<p>The harder case is a column that exists and is wrong some of the time. It fails without any error. These are the ways it happens:</p>
<ul>{li(MODIFIED_LIES)}</ul>
<p>So an incremental query is never the only check. Re-read an overlap on every run (the last hour or day again, merged on the key), and run a full comparison on a schedule to measure how much the query misses. If the comparison keeps finding differences, the column cannot be trusted and the dataset needs another route.</p>
<p>More: <a href="{U}#missing">Missing columns</a> · <a href="{U}#fields">Fields we ask for in every dataset</a> · <a href="{U}#questions">questions E and F</a></p></section>

<section id="bigload"><p class="eyebrow">Problems 3 and 4</p><h2>Big tables and full loads</h2>
<h3 class="sub">The first load of a very large table</h3>
<p>Every dataset is loaded in full at least once. For a table of a billion rows, a single query is the wrong tool. It runs for hours, the database gives up on keeping a consistent view for that long and ends the query, the network drops near the end, and everything starts again from zero. Meanwhile the table keeps changing.</p>
<p>What works is to treat the first load as a planned piece of work:</p>
<ol class="steps">{li(BIG_LOAD)}</ol>
<h3 class="sub">Full loads that run every day</h3>
<p>A daily full load is the simplest pattern and the right one for small tables: it needs no change column and it sees deletes. It has its own ways to fail.</p>
{tbl(["Problem", "How it shows up", "What to do"], FULL_LOAD)}
<p>More: <a href="{U}#load">Full load or incremental: the patterns</a> · <a href="{U}#protect">Take the data without hurting the system</a> · <a href="{U}#questions">questions F and K</a> · <a href="/concepts/backfill/">Backfill</a></p></section>

<section id="halffile"><p class="eyebrow">Problem 5</p><h2>The file was still being written when we started reading</h2>
<p>A large file takes minutes to write. A loader that picks up "whatever is in the folder" during those minutes reads the first part, finds a valid-looking file, and loads it. The day's total is 40% low and nothing failed. The same happens with a set of files when two of three have arrived.</p>
<p>The fix is for the source to tell us when it has finished. There are four ways, best first:</p>
{tbl(["Way", "How it works", "Verdict"], HALF_FILE)}
<p>More: <a href="{U}files/#contract">What a file contract holds</a> · <a href="{U}files/#problems">Common file problems, and the fix</a></p></section>

<section id="manifest"><p class="eyebrow">A small file that solves a lot</p><h2>What a manifest does</h2>
<p>A manifest is a small file the source writes last, after the data files, that describes the delivery. A done marker says "finished". A manifest says "finished, and here is what you should have received". Checking the delivery against it turns silent problems into loud ones.</p>
<pre class="bp">{E(MANIFEST_EXAMPLE)}</pre>
{tbl(["In the manifest", "The question it answers", "What we do with it"], MANIFEST_SOLVES)}
<p>The same idea works beyond files. An API export can return a count to check against. A database extract can come with a control row of counts and totals. We also keep a manifest of our own for every load, which is the ledger described under <a href="#bookmark">Keeping our place</a>.</p>
<p>More: <a href="{U}files/#contract">What a file contract holds</a> · <a href="{U}answers/">Where the answers go</a> (the pipeline manifest, which is a different file: our settings for how a dataset is loaded)</p></section>

<section id="schedule"><p class="eyebrow">Problem 6</p><h2>Schedule or event: when should the load start?</h2>
<p>A schedule says "start at 02:00". What we mean is "start when last night's data is complete". Those are the same on most nights, and the difference on the other nights is where wrong dashboards come from.</p>
<figure class="diagram">{c_svg}<figcaption>{E(c_cap)}</figcaption></figure>
{tbl(["Problem with a schedule", "What happens", "With a signal from the source"], SCHEDULE)}
<p>An event-based load has rules of its own:</p>
<ul>{li(EVENT_RULES)}</ul>
<p>Where the source cannot send a signal, keep the schedule and add a check in front of it: is the marker there, does the count look like a normal day, is the newest row recent enough? If not, wait and try again, then alert. A late load is far cheaper than a wrong one.</p>
<p>More: <a href="{U}#trigger">Schedule or event</a> · <a href="{U}#questions">questions D and K</a> · <a href="/concepts/orchestration/">Orchestration</a> · <a href="/concepts/freshness/">Freshness</a></p></section>

<section id="bookmark"><p class="eyebrow">State</p><h2>Keeping our place on each route</h2>
<p>Every incremental route depends on remembering how far we have read. That bookmark is small, and losing it or moving it at the wrong moment is behind many gaps and duplicates. Two rules apply to all of them: move the bookmark only after the data is safely written, and make the load safe to repeat, so that reading a little too much is harmless.</p>
{tbl(["Route", "The bookmark", "What to know"], BOOKMARKS)}
<p>More: <a href="/learn/data-platform-architecture/metadata-store/">The metadata store</a>, where bookmarks and the run log live · <a href="/concepts/idempotency/">Idempotency</a></p></section>

<section id="more"><p class="eyebrow">Problems 7 to 18</p><h2>The rest of the problems to expect</h2>
<p>Shorter, because each has a home elsewhere on the site.</p>
{tbl(["Problem", "How it shows up", "What to do", "Read more"], [(E(p), E(s), E(d), l) for p, s, d, l in MORE], raw=True)}
<p>The full set of challenges by layer, with the checks that catch them, is in <a href="/learn/hard-problems/">Hard problems by layer</a>.</p></section>

<section id="choose"><p class="eyebrow">Deciding</p><h2>Choosing a route for a source</h2>
<p>The route is chosen per dataset, and a source often uses two: one for daily changes and a slower one that proves nothing drifted. In rough order of preference:</p>
<ol class="steps">{li(CHOOSE)}</ol>
<p>The options and verdicts are in <a href="{U}#decisions">The decisions this block forces</a>, and the reasons get written down as described in <a href="{U}answers/">Where the answers go</a>.</p></section>

<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{faq}</section>

<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2>
<p><b>The questions to ask:</b> <a href="{U}">Upstreams: know your sources</a> and the <a href="{U}questionnaire/">printable questionnaire</a>.</p>
<p><b>In depth:</b> <a href="{U}apis/">API sources</a> · <a href="{U}files/">File sources</a> · <a href="{U}joins/">Learning the joins</a> · <a href="{U}answers/">Where the answers go</a>.</p>
<p><b>How we build it:</b> <a href="/learn/data-platform-architecture/ingestion/">Ingestion: sources to bronze</a> · <a href="/learn/streaming/">Streaming</a> · <a href="/learn/hard-problems/">Hard problems by layer</a>.</p>
<p><b>Back up:</b> <a href="{BASE}">Data systems, end to end</a>.</p>
<div class="ideas"><a href="/concepts/cdc/">Change data capture</a><a href="/concepts/incremental-loads/">Incremental loads</a><a href="/concepts/idempotency/">Idempotency</a><a href="/concepts/backfill/">Backfill</a><a href="/concepts/schema-evolution/">Schema evolution</a><a href="/concepts/data-contracts/">Data contracts</a><a href="/concepts/freshness/">Freshness</a></div></section>"""
    title = "Upstreams, the big picture"
    desc = "Source systems and extraction on one map: query-based and log-based database extraction, SAP routes, APIs, file drops, streams and events, with the problems to expect: deletes, missing modified times, big first loads, half-written files, manifests, and schedule versus event."
    url = f"{SITE}{U}{SLUG}/"
    return wb.page(title, desc, url, body, ds.CSS + CSS + ds.ld(title, desc, url, [("Learn", "/learn/"), ("Data systems", BASE), ("Upstreams", U), ("The big picture", f"{U}{SLUG}/")], FAQ))


def main():
    out = ROOT / "learn" / "data-systems" / "upstreams" / SLUG
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(big_picture())
    print("upstreams, the big picture -> big-picture")


if __name__ == "__main__":
    main()
