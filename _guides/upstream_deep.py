"""Deeper Upstreams pages, by source type and by problem (run from _guides/data_systems.py main()).

  /learn/data-systems/upstreams/apis/    sources reached through APIs
  /learn/data-systems/upstreams/files/   sources that send files
  /learn/data-systems/upstreams/joins/   learning how the datasets join

Same template as every Data systems page: promise, a box for leaders, plain words, sections, one
question table (question, why we ask, what breaks in production, do this / not this), decisions,
FAQ. API_Q and FILE_Q also feed the optional parts of the printable questionnaire.
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("data_systems_for_deep", ROOT / "_guides" / "data_systems.py")
ds = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ds)
E, wb, SITE, BASE = ds.E, ds.wb, ds.SITE, ds.BASE
U = f"{BASE}upstreams/"
P_LAYOUT = f"{BASE}platform/layout/"


def tbl(head, rows):
    h = "".join(f"<th>{E(x)}</th>" for x in head)
    b = "".join("<tr>" + "".join(f"<td>{'<b>' + E(c) + '</b>' if i == 0 else E(c)}</td>" for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="tw"><table class="t"><tr>{h}</tr>{b}</table></div>'


def sub_page(slug, short, title, promise, lede, leaders, sections, questions, decisions, faq, next_html, desc):
    qt, n_q = ds.q_table(questions)
    toc = "".join(f'<li><a href="#{sid}">{E(t)}</a></li>' for sid, t, _ in sections)
    toc += f'<li><a href="#questions">The question list ({n_q})</a></li><li><a href="#decisions">Design decisions</a></li><li><a href="#faq">Questions people ask</a></li><li><a href="#next">Where to go next</a></li>'
    secs = "".join(f'<section id="{sid}">{html}</section>' for sid, _t, html in sections)
    lead = "".join(f"<li>{E(x)}</li>" for x in leaders)
    faqh = "".join(f'<details class="faq"><summary>{E(a)}</summary><p>{E(b)}</p></details>' for a, b in faq)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › <a href="{BASE}">Data systems</a> › <a href="{U}">Upstreams</a> › {E(short)}</p>
<p class="eyebrow" style="margin-top:22px">Data systems · upstreams, in depth · for data leaders, then builders</p>
<h1>{E(title)}</h1>
<p class="promise">{E(promise)}</p>
<p class="lede">{E(lede)}</p>
<div class="leaders"><h3>For leaders</h3><ul>{lead}</ul></div>
<nav class="toc"><b>On this page</b><ol>{toc}</ol></nav>
{secs}
<section id="questions"><p class="eyebrow">The question list</p><h2>Every question, why we ask, and what breaks if nobody does</h2>{qt}</section>
<section id="decisions"><p class="eyebrow">Design decisions</p><h2>The decisions to take</h2>{ds.dec_html(decisions)}</section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{faqh}</section>
<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2>{next_html}
<p><b>Back up:</b> <a href="{U}">Upstreams: know your sources</a>, and the <a href="{U}questionnaire/">printable questionnaire</a>.</p></section>"""
    url = f"{SITE}{U}{slug}/"
    return wb.page(title, desc, url, body, ds.CSS + ds.ld(title, desc, url, [("Learn", "/learn/"), ("Data systems", BASE), ("Upstreams", U), (short, f"{U}{slug}/")], faq))


# =============================================================================================
# APIs
# =============================================================================================

API_KINDS = [
    ("Paged REST API", "GET a page of records, then the next", "Most SaaS apps and partner APIs", "Pages shifting while you read; rate limits"),
    ("Bulk or export API", "Ask for a job; download one or more files when it finishes", "Backfills and big daily loads (Salesforce Bulk API, many ERPs)", "Job queues and size limits; still the best way to move volume"),
    ("Change feed or events API", "Read what changed since a cursor, including deletes", "Incremental loads that see deletes", "Cursor retention: if you fall behind too far, you must reload"),
    ("Webhooks", "The source calls us when something changes", "Low-latency updates", "Calls missed while we are down; need a catch-up pull"),
    ("OData and SAP-style services", "Query entities with filters and paging, often with delta tokens", "SAP and Microsoft business apps", "Delta tokens expire; server-side page limits"),
    ("GraphQL", "Ask for exactly the fields and nested objects you need", "Modern product APIs", "Query cost limits; nested paging inside one query"),
    ("SOAP and legacy services", "XML requests and responses", "Older enterprise and government systems", "Slow, verbose, strict; few changed-since filters"),
]

PAGING = [
    ("Offset or page number", "page=1, 2, 3 or offset=0, 100, 200", "Rows inserted or deleted while you read shift the pages: some rows are skipped, others read twice; deep pages get slow", "Only for small, static lists"),
    ("Cursor or page token", "Each response gives a token for the next page", "Stable while reading; tokens can expire mid-run", "The best general choice when offered"),
    ("Keyset", "Next page = records with id (or updated time, id) greater than the last one seen", "Stable and fast if the sort is unique; ties on time need a second sort column", "Best when you can choose the filter"),
    ("Time window", "Records changed between two times, one window at a time", "Depends on the API's clock and precision; records changed during the read can fall between windows", "Overlap each window a little and remove duplicates"),
]

API_PROBLEMS = [
    ("Rows shift between pages", "A few records missing or doubled every run, never the same ones", "Cursor or keyset paging; remove duplicates on the record id; compare counts"),
    ("Throttled (HTTP 429) half way", "A partial load that looks complete", "Back off with jitter, respect Retry-After, save a checkpoint after each page, check completeness before publishing"),
    ("Quota shared with other integrations", "Our backfill stops the sales team's other tools", "Our own share of the quota; backfills out of hours; bulk API for volume"),
    ("Changed-since filter uses another clock", "Changes near the window edges are missed", "Overlap each window, use the API's own time, remove duplicates"),
    ("API reads from a search index, not the database", "Recent changes appear minutes later", "Re-read a recent window on the next run"),
    ("Deletes are invisible", "Deleted records live on in the platform", "A deleted-records endpoint, a change feed, or a regular full list of ids"),
    ("Nested JSON keeps changing", "New fields lost; type changes break parsing", "Land the raw JSON in bronze; parse in silver with explicit schema-change rules"),
    ("Token expires mid-run", "Load stops after an hour, every night", "Refresh tokens automatically; keep secrets in a vault"),
    ("Version retired by the vendor", "A working integration stops on a date announced months ago", "Track the vendor's changelog and retirement dates in the source contract"),
    ("Each call costs money", "The data bill arrives from the vendor, not the cloud", "Incremental loads, larger pages, a cost budget per source"),
]

API_Q = [
    ("API", "APIs", "for sources reached through an API", [
        ("Besides the normal API, is there a bulk export, a change feed or a webhook?",
         "Normal APIs are built for apps reading a few records, not for copying everything.",
         "A backfill through the normal API takes nine days and burns the whole quota.",
         "Bulk export for backfills and big loads, a change feed for increments, webhooks only with a catch-up pull. Not: the record-by-record API for everything."),
        ("How does it page: offset, cursor, keyset or time window, and is the sort order stable and unique?",
         "Paging decides whether a read is complete.",
         "Offset paging over changing data misses a few records on every run.",
         "Cursor or keyset paging on a unique sort; remove duplicates on the id. Not: page numbers over live data."),
        ("Can we filter by 'changed since', on which clock, to what precision, and is the boundary inclusive?",
         "Incremental API loads depend on this filter being exact.",
         "Changes made in the same second as the last watermark are skipped.",
         "An overlap window and duplicate removal on every run. Not: trusting the boundary."),
        ("What are the limits: requests per second, daily quota, parallel connections, page size, and is the quota shared?",
         "Limits decide backfill time and how fast we can catch up after an outage.",
         "Throttled midway; the load stops and nobody notices it was partial.",
         "Plan calls against limits; back off and checkpoint; keep our share of the quota. Not: retrying as fast as possible."),
        ("Does the API charge per call or per record, and who pays?",
         "Some APIs bill by usage, outside the cloud bill.",
         "A full refresh every hour triples the vendor's invoice.",
         "Incremental loads, large pages, a monthly budget per source. Not: full pulls for convenience."),
        ("How do we learn about deleted records?",
         "Most APIs return only records that still exist.",
         "Deleted customers stay active in the platform.",
         "A deleted-records endpoint or change feed; otherwise a regular full id list compared with ours. Not: ignoring deletes."),
        ("Does the API give a total count, or anything else we can check completeness against?",
         "Without a total, a partial load looks complete.",
         "A load that stopped at page 40 of 60 is published as complete.",
         "Compare our count with the API's total, or with a separate count call. Not: assuming the last page was reached."),
        ("Does the API read the live database or a search index or replica that lags?",
         "Lag means recent changes appear late.",
         "Records changed in the last minutes before a run are missed until someone notices.",
         "Re-read a recent window each run. Not: a window that ends 'now'."),
        ("How are new fields and versions announced, and when do old versions retire?",
         "APIs change on the vendor's schedule, not ours.",
         "The integration stops on the day v1 is switched off.",
         "Pin the version, watch the changelog, record retirement dates in the source contract. Not: 'latest' with no watcher."),
        ("How does authentication work, how long do tokens last, and who rotates the secret?",
         "Expired credentials are the most common cause of silent stops.",
         "The load fails every night after the token's one-hour life.",
         "Automatic token refresh and secrets in a vault with expiry alerts. Not: a token pasted into a config file."),
    ]),
]

API_DECISIONS = [
    ("How do we pull large volumes?", [
        ("The bulk or export API", "pursue", "Pursue for backfills and big daily loads."),
        ("The paged record API, in parallel within the limits", "when", "Pursue only when no bulk API exists."),
        ("The paged API, one thread, all history", "drop", "Drop. Days of calls and a burnt quota."),
    ]),
    ("How do we page?", [
        ("Cursor or keyset on a unique sort", "pursue", "Pursue. Complete and repeatable."),
        ("Offset or page number", "drop", "Drop for data that changes while you read."),
    ]),
    ("How do we stay current?", [
        ("Change feed, or webhooks plus a scheduled catch-up pull", "pursue", "Pursue. Fast, and nothing is lost when we're down."),
        ("Webhooks only", "drop", "Drop. Every outage on our side loses changes."),
    ]),
]

API_FAQ = [
    ("Why do API data loads miss records?",
     "Usually because offset paging over changing data skips rows, a changed-since filter misses records at the window edges, throttling stops the load part way, or the API reads from an index that lags. Cursor or keyset paging, overlapping windows, checkpoints and a count comparison fix most of it."),
    ("How do you load a large dataset from a SaaS API?",
     "Use the vendor's bulk or export API for history and big daily loads, and a change feed or a changed-since filter for increments, within your share of the rate limits."),
]


def apis_page():
    sections = [
        ("plain", "In plain words", f"""<p class="eyebrow">In plain words</p><h2>Copying a library by asking at the desk</h2>
<p>An API is a librarian's desk. It is built for people asking for a few books at a time. Copying the whole library through it means asking for one shelf at a time, all day, while others queue behind you, the librarian limits how often you may ask, and books are being returned and moved while you work. It can be done, but only with a plan: use the bulk delivery service if there is one, keep your place, and count what you got.</p>"""),
        ("kinds", "Kinds of APIs", f"""<p class="eyebrow">Kinds of APIs</p><h2>Seven kinds of APIs</h2>{tbl(["Kind", "How it works", "Good for", "Watch for"], API_KINDS)}"""),
        ("paging", "Paging", f"""<p class="eyebrow">Pagination</p><h2>How paging decides whether a read is complete</h2>{tbl(["Paging", "Looks like", "What goes wrong", "Use it"], PAGING)}"""),
        ("problems", "Common problems", f"""<p class="eyebrow">In production</p><h2>Common API problems, and the fix</h2>{tbl(["Problem", "What you see", "Fix"], API_PROBLEMS)}"""),
        ("protect", "Load on the source", f"""<p class="eyebrow">Load and cost</p><h2>Load on the source, and cost</h2>
<p>Every API call is work for the source system, and some APIs charge per call or per record. Before the first load, work out the backfill: records to read, divided by records per page, times the time per call, against the rate limit. If it comes to days, ask for the bulk API or a file export. Run backfills out of hours, stay inside your share of the quota, and keep a pause switch the source team can use. The <a href="{U}#protect">protecting the source</a> rules apply to APIs too.</p>"""),
    ]
    nxt = f'<p><b>Other source types:</b> <a href="{U}files/">files</a>; databases are covered on the <a href="{U}">main Upstreams page</a> (change data capture, replicas, protecting the source).</p>'
    return sub_page("apis", "APIs", "API sources: paging, limits, cost and completeness",
                    "Every record the API holds arrives once, within the source's limits, and we can prove the load is complete.",
                    "What goes wrong when data comes through APIs, and the questions to ask first: bulk versus record APIs, paging, changed-since filters, rate limits and quotas, cost per call, deletes, versions and completeness.",
                    ["APIs are built for apps reading a few records, not for copying whole datasets. Bulk extraction through them fights their limits.",
                     "The main risks are missed or doubled records from paging, partial loads after throttling, invisible deletes, changing JSON and cost per call.",
                     "Prefer, in order: the vendor's bulk or export API or change feed, a managed connector, then plain paged polling.",
                     "Every API load ends with a completeness check: our count against the API's total."],
                    sections, API_Q, API_DECISIONS, API_FAQ, nxt,
                    "API data sources explained: bulk versus paged APIs, pagination that doesn't lose records, rate limits and shared quotas, cost per call, deletes, versions, and the questions to ask.")


# =============================================================================================
# Files
# =============================================================================================

FILE_KINDS = [
    ("Delimited text (CSV, TSV, pipe)", "Most exports and partner feeds", "Delimiters inside values, quoting, encodings, header changes"),
    ("Fixed width", "Mainframes and banks", "A layout document you must have; one shifted column corrupts every field after it"),
    ("Excel", "Finance, planning, hand-made data", "Merged cells, hidden sheets, formulas, manual edits, many tables on one sheet"),
    ("JSON and XML", "App exports, APIs dumped to files, B2B messages", "Nesting, optional fields, very large single documents"),
    ("Parquet and Avro", "Other data platforms and modern exports", "Schema inside the file: good, but changes still need rules"),
    ("Compressed and archived (gzip, zip)", "Large feeds", "A single gzip can't be split, so one huge file is read by one machine"),
    ("Documents (PDF, images)", "Invoices, forms, statements", "Need extraction (OCR or a model) before they are data; check the extraction"),
]

DELIVERY = [
    ("Source pushes to our SFTP or storage", "We control the landing place; need a done marker"),
    ("We pull from their SFTP or storage", "We must know when a file is complete; listing big folders is slow"),
    ("Object storage drop with events", "File-arrival events can start the load (no schedule guessing)"),
    ("Email attachments or shared drives", "Fragile and hard to secure; replace with SFTP or storage when you can"),
]

FILE_CONTRACT = [
    ("Name pattern", "Source, dataset, business date and sequence number in the name", "sales_eu_2026-11-09_003.csv"),
    ("Full or delta", "Whether the file holds everything or only changes, shown in the name", "…_full_… or …_delta_…"),
    ("Format", "Delimiter, quote and escape characters, header row, line endings", "comma, double quote, header yes"),
    ("Encoding", "Character set, and whether there is a byte-order mark", "UTF-8, no BOM"),
    ("Values", "Date and number formats, decimal separator, how nulls are written", "ISO dates, '.' decimals, empty = null"),
    ("Done marker", "A small file or trailer row saying the file is complete, with row count and checksum", "…_003.done with rows=120400"),
    ("Delivery", "Where, when, and how late is too late", "by 02:00 UTC daily"),
    ("Corrections", "How a fix is sent: a full resend, a correction file, or never edited in place", "resend whole day with next sequence"),
    ("Retention", "How long the source keeps files, so we can ask again", "30 days"),
]

FILE_PROBLEMS = [
    ("File read while still being written", "A day's total 40% low, no error", "Load only after the done marker, or after the size stops changing"),
    ("Same file delivered twice", "Doubled revenue for one day", "Keep a register of file names and checksums; skip a file already loaded"),
    ("Files out of order or missing in the sequence", "Tuesday loaded before Monday; history wrong", "Process by sequence number; hold the queue and alert on a gap"),
    ("Late file", "Gold runs on yesterday's data", "Freshness alert; downstream waits for the file or runs with a visible flag"),
    ("Columns added, removed or reordered", "Values land in the wrong columns", "Match columns by header name, not position; detect schema changes; quarantine the file"),
    ("Delimiter or line break inside values", "Rows split or merged", "A strict parser with quoting; count rejected rows; reject the file over a threshold"),
    ("Wrong encoding", "Names with accents turn into garbage", "Encoding stated in the contract and checked on arrival"),
    ("Ambiguous dates (03/04/2026)", "March or April, depending on the reader", "ISO dates in the contract; reject ambiguous ones"),
    ("Empty file", "Is it 'no sales today' or 'the export broke'?", "Agree what an empty file means; send an empty file with a done marker for 'no data'"),
    ("One huge compressed file", "One machine reads 50 GB for hours", "Ask for split or splittable files (several parts, or Parquet)"),
    ("Thousands of tiny files", "Slow listing and slow loads", "Ask for batching; compact after landing"),
    ("Hand-edited Excel", "A renamed tab or merged cell breaks the load", "A locked template, or move the data to a form or table"),
]

FILE_Q = [
    ("FL", "Files", "for sources that send files", [
        ("Is each file a full snapshot or only the changes, and does the file name say which?",
         "Full and delta files are loaded completely differently.",
         "A delta file treated as full deletes everything it doesn't mention.",
         "Full or delta in the name and the contract. Not: guessing from the size."),
        ("What is the naming pattern: source, dataset, business date, sequence number?",
         "The name is how we order, de-duplicate and find files.",
         "Two files for the same day can't be put in order.",
         "A fixed pattern with business date and sequence. Not: 'export.csv' overwritten daily."),
        ("How do we know a file is complete: a done file, a manifest with row count and checksum, a trailer row?",
         "A file being written looks like a file that is finished.",
         "A half-written file loads and a day's total drops by 40%.",
         "A done marker with row count and checksum, checked before loading. Not: loading whatever is in the folder."),
        ("How are corrections sent: a full resend, a correction file, or edits to the old file?",
         "Corrections decide whether we replace or add.",
         "A corrected file is appended next to the original and the day is doubled.",
         "Resend the whole business date with the next sequence number; we replace that date. Not: editing files in place."),
        ("Can files arrive late, twice or out of order, and in which order must they be processed?",
         "Order matters for history and for deltas.",
         "Tuesday's delta loads before Monday's and the latest values are wrong.",
         "Process by sequence; hold and alert on a gap; skip exact repeats. Not: process in arrival order."),
        ("What is the exact format: delimiter, quoting, header, encoding, line endings, nulls, date and number formats?",
         "Small format differences corrupt data silently.",
         "Accented names become garbage, or 03/04 is read as the wrong month.",
         "Write it in the file contract and check each file on arrival. Not: letting the parser guess."),
        ("How are column changes announced, and are columns matched by name or by position?",
         "Files change shape whenever the exporting system changes.",
         "A new column in the middle shifts every value after it.",
         "Match by header name, detect changes, quarantine files that break the contract. Not: positional reads of delimited files."),
        ("How big are the files, how many a day, and how are they compressed?",
         "Size and count decide parsing speed and cost.",
         "One 50 GB gzip is read by one machine for hours; or a million tiny files take longer to list than to load.",
         "Agree split or splittable files of sensible size. Not: whatever the export produces."),
        ("Where are files delivered, who can write there, and how long does the source keep them?",
         "The landing place is a security boundary and our replay window.",
         "Someone else's process overwrites a file; or we need a resend and the source deleted it.",
         "A dedicated landing place, write access for the sender only, retention on both sides. Not: a shared folder."),
        ("What does an empty file mean, and what does no file mean?",
         "'No data today' and 'the export broke' must look different.",
         "A broken export sends an empty file and today shows zero sales.",
         "An empty file with a done marker means no data; a missing file is an alert. Not: treating both the same."),
        ("Do files hold personal data, and are they encrypted in transit and at rest?",
         "Files are easy to copy and forget.",
         "Customer files sit unencrypted on an SFTP server for years.",
         "Encrypted transfer and storage, short retention, masked copies for testing. Not: plain files kept forever."),
        ("For Excel or hand-made files: is there a locked template, and who owns it?",
         "Hand-made files change whenever someone edits them.",
         "A renamed sheet breaks the monthly budget load on the day it's needed.",
         "A locked template with validation, or move the data to a form. Not: parsing whatever arrives."),
    ]),
]

FILE_DECISIONS = [
    ("How do we start loading a file?", [
        ("On the done marker or a file-arrival event", "pursue", "Pursue. No half-written files, no guessing the time."),
        ("On a schedule, with a size-stable check", "when", "Pursue only when the sender can't produce a marker."),
        ("On a schedule, whatever is in the folder", "drop", "Drop. Partial and duplicate loads."),
    ]),
    ("How do we read columns?", [
        ("By header name, with schema-change detection", "pursue", "Pursue. Reordered or added columns don't corrupt data."),
        ("By position", "drop", "Drop for delimited files. Fixed width is the exception: there the layout document is the contract."),
    ]),
    ("What happens to a bad file?", [
        ("Quarantine the whole file with a reason, and tell the sender", "pursue", "Pursue. Nothing half-loaded; the fix comes from the source."),
        ("Load the good rows, drop the bad ones", "when", "Pursue only with a rejected-row threshold and the rejects kept for review."),
    ]),
]

FILE_FAQ = [
    ("What should a file-based data feed agree up front?",
     "A file contract: the name pattern with business date and sequence, full or delta, the exact format and encoding, how values are written, a done marker with row count and checksum, the delivery time, how corrections are sent and how long files are kept."),
    ("How do you stop the same file being loaded twice?",
     "Keep a register of every file loaded, with its name and checksum, and skip any file already in it. Bronze also records which file every row came from, so a bad file can be withdrawn."),
]


def files_page():
    sections = [
        ("plain", "In plain words", f"""<p class="eyebrow">In plain words</p><h2>Parcels at a loading dock</h2>
<p>File feeds are parcels left at a loading dock. A good sender numbers each parcel, puts a packing list inside saying what should be there, and tells you when the last one is on the truck. A bad sender drops boxes whenever they like, sometimes twice, sometimes half-packed, and changes the box size without saying. Most file problems are solved by agreeing the packing list before the first delivery.</p>"""),
        ("kinds", "Kinds of files", f"""<p class="eyebrow">Kinds of files</p><h2>File formats and what to watch</h2>{tbl(["Format", "Where it comes from", "Watch for"], FILE_KINDS)}
<h3>How files arrive</h3>{tbl(["Delivery", "What it means for us"], DELIVERY)}"""),
        ("contract", "The file contract", f"""<p class="eyebrow">Agree it first</p><h2>What a file contract holds</h2>{tbl(["Part", "What it says", "Example"], FILE_CONTRACT)}"""),
        ("problems", "Common problems", f"""<p class="eyebrow">In production</p><h2>Common file problems, and the fix</h2>{tbl(["Problem", "What you see", "Fix"], FILE_PROBLEMS)}
<p>Landing keeps every file exactly as received, and bronze records which file each row came from, so any file can be replayed or withdrawn later.</p>"""),
    ]
    nxt = f'<p><b>Other source types:</b> <a href="{U}apis/">APIs</a>; databases are covered on the <a href="{U}">main Upstreams page</a>.</p>'
    return sub_page("files", "Files", "File sources: complete, once, in order",
                    "Every file arrives whole, once, in order and in the agreed shape, or it is held back with a reason.",
                    "What goes wrong with file-based sources, and what to agree before the first file: formats, naming, done markers, corrections, order, encoding, column changes, size and security.",
                    ["File feeds are the most common source and the least controlled: whoever writes them can change them without telling us.",
                     "Most problems are partial files, files sent twice or out of order, changed columns, wrong encodings and dates, and empty files that mean different things.",
                     "Agree a file contract before the first delivery: name pattern, full or delta, format, done marker with row count, delivery time and how corrections are sent.",
                     "Keep every file exactly as received, so any day can be replayed or withdrawn."],
                    sections, FILE_Q, FILE_DECISIONS, FILE_FAQ, nxt,
                    "File-based data sources explained: formats, delivery, the file contract (naming, done markers, corrections), and the common problems: partial, duplicate, late and out-of-order files, column changes and encodings.")


# =============================================================================================
# Learning the joins
# =============================================================================================

LADDER = [
    ("1 · Read what is declared", "Foreign keys in the database catalog; the vendor's published data model (Salesforce object relationships, SAP check tables)", "Exact, when present", "Cheap"),
    ("2 · Read how people already join", "Views, stored procedures, ETL code, report SQL, and the database's query history", "The joins the business really uses, including the rules inside them", "Cheap to medium"),
    ("3 · Propose candidates", "Matching names and types (customer_id to customers.id); an AI model reading names, comments and sample values", "Many candidates, some wrong", "Cheap"),
    ("4 · Measure on the data", "For each candidate: is the parent side unique, what share of child values exist in the parent, how many rows match on each side, how many orphans", "Evidence for or against each join", "Medium; use samples and compact value sketches on big tables"),
    ("5 · Confirm with the owner", "Show the map with the measurements; the owner accepts, rejects or corrects", "Agreed joins", "A meeting"),
    ("6 · Write it down and test it", "Relationships in the data contract (ODCS supports them since 3.1), tested on every load", "Joins that stay true", "Automatic after setup"),
]

SIGNALS = [
    ("Declared foreign key", "Strong", "Low, but the key may be declared and not enforced"),
    ("Used in existing views, reports or query history", "Strong", "Low; check the join conditions, not just the tables"),
    ("Same name and type (order_id in both)", "Medium", "Medium: generic names (id, code, type) match everything"),
    ("Most child values found in a unique parent column", "Strong", "High for small numbers: ids 1 to 100 overlap with almost anything"),
    ("AI model's suggestion", "Weak until measured", "Medium: plausible-sounding joins that the data doesn't support"),
]

JOIN_Q = [
    ("JN", "Learning the joins", "where relationships come from and how we prove them", [
        ("Does the database declare foreign keys, and does the vendor publish a data model?",
         "Declared relationships are the cheapest and most exact source.",
         "Weeks spent guessing joins the catalog already held.",
         "Read the catalog and the vendor's model first. Not: starting from sample data."),
        ("Can we read the views, procedures, ETL code, report SQL and query history that use this data?",
         "Existing joins carry the business rules too.",
         "Our joins are 'correct' but don't match the numbers people trust.",
         "Harvest join conditions from code and query history; ask about the odd ones. Not: ignoring the old system's logic."),
        ("For each proposed join: is the parent unique, what share of child values match, and how many orphans are there?",
         "A join is only real if the data agrees.",
         "A join on small ids that happen to overlap produces confident nonsense.",
         "Measure every candidate; require a unique parent and a high match rate; reject joins on generic low-number ids unless proven. Not: accepting a join because the names match."),
        ("Who confirms each relationship, and where is it recorded?",
         "Unconfirmed joins drift back into guesses.",
         "Two teams join the same tables two ways and report two numbers.",
         "The owner signs off; the relationship goes into the data contract and is tested on every load. Not: knowledge in one engineer's head."),
    ]),
]

JOIN_DECISIONS = [
    ("How are relationships found?", [
        ("Declared keys and existing code first, then candidates measured on the data, then owner sign-off", "pursue", "Pursue. Cheapest evidence first; nothing accepted unmeasured."),
        ("An AI model proposes joins and we use them", "drop", "Drop as a final answer. Keep it as a candidate generator only."),
        ("Ask the business to draw the model from memory", "when", "Pursue only as a starting sketch to check against the data."),
    ]),
]

JOIN_FAQ = [
    ("How do you find relationships between tables when there are no foreign keys?",
     "Read how people already join them (views, report SQL, ETL code, query history), propose candidates from names and types, then measure each on the data: the parent side must be unique, most child values must exist in it, and orphans must be few. The data owner confirms the result, and it is recorded in the data contract and tested every load."),
    ("Can AI find the joins between tables?",
     "It is good at proposing candidates from names, comments and sample values, and poor at proving them. Treat its suggestions as candidates and accept only those the data measurements and the owner confirm."),
]


def joins_page():
    sections = [
        ("plain", "In plain words", f"""<p class="eyebrow">In plain words</p><h2>A family tree from old letters</h2>
<p>Building a family tree, you start with what's written down: birth certificates and marriage records. Then the family's own stories. Then guesses from shared surnames and towns, which you check against dates before you write them in. A shared surname proves nothing on its own. Finding joins between datasets works the same way: written-down keys first, then the joins people already use, then guesses, and every guess checked against the data.</p>"""),
        ("ladder", "The ladder", f"""<p class="eyebrow">Smartly, cheapest first</p><h2>Six steps to learn the joins</h2>{tbl(["Step", "What we do", "What it gives", "Effort"], LADDER)}"""),
        ("signals", "Signals", f"""<p class="eyebrow">Evidence</p><h2>How much each signal is worth</h2>{tbl(["Signal", "Strength", "False-match risk"], SIGNALS)}
<p>The measurement in step 4 is what turns a guess into a join. For big tables it runs on samples and compact summaries of each column's values, inside the source's environment, so only the measurements leave it. See question L2 on the <a href="{U}#questions">Upstreams page</a>.</p>"""),
        ("wrong", "How joins go wrong", f"""<p class="eyebrow">Why it matters</p><h2>Two ways a wrong join hurts</h2>
<p>A join assumed to match one row that sometimes matches two <b>multiplies</b> numbers. A join to a parent that's missing <b>drops</b> rows from an inner join. Both look like correct output. The relationship questions I1 to I7 on the <a href="{U}#questions">Upstreams page</a> cover how many rows match on each side, orphans, timing and joins as of a past date.</p>"""),
    ]
    nxt = f'<p><b>Related:</b> <a href="{U}#joins">relationships and joins</a> and <a href="{U}#profile">why we ask to scan your data</a> on the Upstreams page.</p>'
    return sub_page("joins", "Learning the joins", "Learning the joins between datasets",
                    "Every join we build is declared, already used, or proven on the data, and confirmed by the owner.",
                    "How to find out how datasets join when nobody can tell you: read what's declared, harvest the joins already in use, propose candidates, measure them on the data, and get the owner to confirm.",
                    ["Wrong joins are the quietest way to get wrong numbers: they multiply or drop rows and still look like correct output.",
                     "Most sources don't declare their relationships, especially SaaS apps and older systems.",
                     "Learn the joins cheapest first: declared keys and the vendor's model, then joins already used in reports and code, then candidates measured on the data.",
                     "AI can propose joins; only measurements and the owner can confirm them."],
                    sections, JOIN_Q, JOIN_DECISIONS, JOIN_FAQ, nxt,
                    "How to learn the joins between datasets: declared keys, joins already in use, candidates from names and AI, measuring uniqueness, match rates and orphans on the data, owner sign-off and data contracts.")


# =============================================================================================
# Where the answers go
# =============================================================================================

def answers_flow():
    box, arrow, text, svg, FILL = ds.box, ds.arrow, ds.text, ds.svg, ds.FILL
    b = box(20, 20, 200, 80, "Questionnaire", "discovery, profiling,\nowner interviews", "grey")
    b += arrow(222, 60, 278, 60)
    b += box(280, 14, 300, 92, "1 · Data contract", "ODCS YAML in git, one per dataset:\nwhat the data promises", "butter")
    b += arrow(582, 60, 638, 60)
    b += box(640, 20, 240, 80, "Validate + generate", "in the deployment\npipeline", "lilac")
    xs = [20, 250, 480, 710]
    outs = [("2 · Manifest", "how we load it", "rose"), ("3 · Unity Catalog", "comments, tags, keys,\nmasks, clustering", "sky"),
            ("4 · Quality tests", "rules, thresholds,\nreconciliation", "mint"), ("5 · Ontology", "business meaning\nacross systems", "peri")]
    for x, (t, sub, f) in zip(xs, outs):
        b += box(x, 170, 210, 80, t, sub, f)
        b += f'<line x1="760" y1="102" x2="{x + 105}" y2="168" stroke="#1F1F1F" stroke-width="1.4" marker-end="url(#ah)"/>'
    b += box(150, 300, 600, 70, "6 · One generic engine: bronze → silver → gold", "reads the manifest and contract; no keys, columns or rules written in code", "silver")
    b += arrow(125, 252, 300, 298) + arrow(585, 252, 520, 298)
    b += box(790, 300, 240, 70, "7, 8 · Decisions, agreements", "decision records, source\nagreement, runbook", "white")
    return svg(1050, 385, b, "Questionnaire answers go into one data contract in git; the deployment pipeline validates it and generates the manifest, Unity Catalog metadata, quality tests and ontology links; one generic engine reads them. Decisions and agreements are kept separately."), \
        "Written once in the contract, generated everywhere else. Reasons and agreements live beside it."


HOMES = [
    ("1 · Data contract (ODCS)", "What the dataset promises: schema, keys, descriptions, relationships, classification, quality rules, freshness, owners", "YAML in git, one file per dataset", "The source owner and the data product owner", "Pull request, reviewed and versioned"),
    ("2 · Pipeline manifest", "How we load it: load pattern, watermark, CDC settings, merge keys, history type per column, clustering, schedule, throttling", "YAML in git, loaded into the metadata store", "The platform team", "Pull request; validated against the contract"),
    ("3 · Unity Catalog", "The enforced copy at run time: comments, tags, key constraints, masks, row filters, grants, clustering, lineage", "Generated by the deployment pipeline", "Nobody edits it by hand", "Every deploy"),
    ("4 · Quality tests", "Checks from the contract's rules and the profile's thresholds; reconciliation against control totals", "Generated into the quality framework", "The platform team", "Every deploy"),
    ("5 · Ontology and glossary", "Business entities and terms, and which datasets in which systems represent them", "A small model in git (YAML or a graph), linked from contracts", "Domain owners, data governance", "Pull request"),
    ("6 · The engine", "Generic bronze to silver to gold code that reads 2 and 1", "Code in git", "The platform team", "Normal releases; never edited per dataset"),
    ("7 · Decision records", "Why: full or incremental, why no CDC, why Type 2 on these columns", "Short documents in git", "The technical anchor", "Written when a decision is made"),
    ("8 · Source agreement and runbook", "Extract window, load budget, contacts, kill switch, escalation", "A document linked from the contract", "The source owner and the platform team", "Reviewed at each release of the source"),
]

ANS_MAP = [
    ("A · Ownership and change", "Contract: team, roles, support", "UC owner and tags; alert routing", "Every hop: who to call"),
    ("B · Access route", "Contract: servers. Secrets go in a vault, never in a contract", "Manifest connection reference", "Hop 1"),
    ("C · Protecting the source", "Source agreement (8)", "Manifest throttle and window; capture-lag alerts; runbook", "Hop 1, operations"),
    ("D, E, F · Push, pull, full or incremental", "Manifest (2), with the reason in a decision record (7)", "Hop 1 job settings", "Hop 1"),
    ("G · How data changes, history type", "Manifest: delete handling, look-back, Type 1 or 2 per column", "Merge settings", "Hop 2"),
    ("H · Keys, dates, ordering, duplicates", "Contract: primary key, types, descriptions. Manifest: merge key, sequence, tie-break", "UC primary key and comments; uniqueness tests", "Hop 2"),
    ("I · Relationships", "Contract: relationships. Ontology for links across systems", "UC foreign keys; orphan and cardinality tests", "Hop 3 joins"),
    ("J · Schema and meaning", "Contract: descriptions; reference tables; ontology terms", "UC comments; semantic layer definitions", "Hops 3 and 4, Genie, agents"),
    ("K · Volume and timing", "Contract: freshness promise. Manifest: schedule or trigger, clustering", "Freshness alerts; table layout; cost estimate", "Every hop"),
    ("L · Profiling", "Profile results in the ops catalog", "Quality thresholds in the contract", "Hops 1 to 3"),
    ("M · Sensitivity and rules", "Contract: classification, retention", "UC tags, column masks, row filters; storage lifecycle", "Every layer, hop 5 access"),
    ("N · Trust and reconciliation", "Contract: quality rules (counts, sums)", "Reconciliation jobs; tests against the trusted report", "Hops 1 to 3"),
]

SPLIT = [
    ("order_no is the business key", "Contract", "It's a promise about the data"),
    ("Merge on order_no; latest by updated_at, ties by ingest time", "Manifest", "It's how we load"),
    ("email is personal data", "Contract", "A fact about the data, used for masking everywhere"),
    ("Load incrementally with a 2-hour overlap; full compare weekly", "Manifest", "A loading choice; the reason goes in a decision record"),
    ("Data is no older than 24 hours by 07:00", "Contract", "A promise to consumers"),
    ("Cluster silver by order_no", "Manifest", "Physical layout, our choice"),
    ("The last watermark value", "Metadata store state", "Run-time state, not configuration"),
    ("The database password", "Vault", "Never in git"),
]

LAYOUT_OPTIONS = [
    ("Liquid clustering", "Rows with similar values in the same files; reorganised incrementally; keys can be changed without rewriting the table", "Default for new Delta tables on Databricks: silver and gold, merge-heavy tables, tables whose query patterns change", "Can't be combined with partitioning or Z-order on the same table; pick up to four keys"),
    ("Partitioning", "One folder per value of a column (usually a date)", "Only very large tables (well over a terabyte) on a low-cardinality column, when you need whole-partition operations: replace a day, drop old months, or other engines must read the layout", "High-cardinality columns create millions of tiny files; changing the scheme means rewriting the table"),
    ("Z-ordering", "OPTIMIZE ... ZORDER BY sorts data across files by a few columns", "Existing tables not yet moved to liquid clustering, or runtimes and engines without it", "Not incremental: each run rewrites data, and it must be re-run as data arrives"),
    ("Nothing", "Let file statistics and compaction do the work", "Small tables (a few GB), reference data, most bronze tables", "Fine until the table grows; review at a size threshold"),
]

CLUSTER = [
    ("Bronze", "Usually nothing, or the ingest date", "Bronze is read in batches by ingest time for replay; keep it cheap to write"),
    ("Silver", "The merge key, plus the most common date filter if there is one", "Merges then rewrite few files; this is the merge-cost lever in the cost calculator"),
    ("Gold facts", "The date plus the most filtered dimension key (customer, store)", "Dashboard queries skip most files"),
    ("Gold dimensions", "The business key, or nothing for small ones", "Small tables don't need clustering"),
    ("Not sure yet", "CLUSTER BY AUTO with predictive optimization", "Databricks picks keys from real query history; review the choice later"),
]

ANS_Q = [
    ("WA", "Where the answers go", "one home per answer", [
        ("Does every answer have exactly one home, and is everything else generated from it?",
         "Answers typed into several places drift apart.",
         "The key in the code, the catalog and the contract differ, and nobody knows which is right.",
         "One home per answer (the table above); the deployment pipeline generates the rest. Not: the same fact typed in three places."),
        ("Is anything edited by hand in Unity Catalog?",
         "Hand edits are overwritten on the next deploy, or block it.",
         "A mask added by hand disappears after a release; personal data is visible for a week.",
         "Unity Catalog metadata is generated from git. Not: console edits."),
        ("Does the code hold dataset-specific keys, columns or rules?",
         "Then every new dataset is a code change.",
         "A key change needs a release of the engine.",
         "The engine reads the manifest and the contract. Not: if table == 'orders' in code."),
        ("Who approves a contract change, and is the contract version checked at deploy time?",
         "A contract change is a change to a promise.",
         "A column is dropped from the contract and three consumers break.",
         "The owner approves in a pull request; breaking changes need a new major version. Not: editing the contract quietly."),
        ("How is each big table laid out (liquid clustering, partitioning or Z-order), on which columns, and why?",
         "Clustering decides how many files merges and queries touch.",
         "Silver merges rewrite a fifth of a 50 TB table every run.",
         "Choose from the merge key, the date filter and real query patterns, or CLUSTER BY AUTO; record it in the manifest. Not: clustering on whatever column comes first."),
    ]),
]

ANS_DECISIONS = [
    ("Where do loading settings live?", [
        ("Contract for promises, manifest for loading", "pursue", "Pursue. Each file has one job and one owner."),
        ("Everything in the ODCS contract, using customProperties", "when", "Pursue only for very small platforms; the contract turns into a config file."),
    ]),
    ("What role does Unity Catalog play?", [
        ("Generated target, enforced at run time", "pursue", "Pursue. Git stays the truth; the catalog can be rebuilt."),
        ("The place people edit metadata", "drop", "Drop. Edits are lost or conflict with deploys."),
    ]),
    ("How do we lay out a big table?", [
        ("Liquid clustering", "pursue", "Pursue for new silver and gold tables on Databricks."),
        ("Partition by date", "when", "Pursue only for very large tables that need whole-day or whole-month operations, or that other engines read by folder."),
        ("Partition by a high-cardinality column (customer, order)", "drop", "Drop. Millions of tiny files."),
        ("Z-order", "when", "Pursue only on existing tables until they move to liquid clustering."),
    ]),
    ("How do we choose clustering columns?", [
        ("From the merge key, date filters and query history, recorded in the manifest", "pursue", "Pursue for the big tables."),
        ("CLUSTER BY AUTO", "when", "Pursue where predictive optimization is on and query patterns aren't known yet."),
    ]),
]

ANS_FAQ = [
    ("Where should data contract information live on Databricks?",
     "In ODCS files in git, one per dataset, as the source of truth. The deployment pipeline generates Unity Catalog comments, tags, key constraints and masks from them, and the pipeline manifest holds how each dataset is loaded."),
    ("Which columns should a Delta table be liquid clustered on?",
     "For silver tables with merges, the merge key, plus the most common date filter if there is one. For gold facts, the date and the most filtered dimension key. Small tables need none. If you don't know the query patterns yet, CLUSTER BY AUTO lets Databricks choose from query history."),
    ("Should I partition, Z-order or liquid cluster a Delta table?",
     "On Databricks, liquid cluster new tables: it replaces partitioning and Z-order and adapts as query patterns change. Partition only very large tables that need whole-partition operations, on a low-cardinality column such as date. Use Z-order only on existing tables until they are moved to liquid clustering."),
    ("Are Unity Catalog primary and foreign keys enforced?",
     "No. They are informational: they document the key and help some query plans, but they don't stop duplicates or orphans. Uniqueness and orphan tests are still needed."),
]

EX_ODCS = """# contracts/erp-orders.yaml  (abridged and illustrative; check field names against the ODCS 3.2 schema)
apiVersion: v3.1.0
kind: DataContract
id: erp-orders
version: 1.2.0
domain: sales
team:
  - username: priya.s        # source owner (A1)
    role: owner
schema:
  - name: orders
    physicalName: SALES.ORDERS
    description: One row per customer order.
    properties:
      - name: order_no
        logicalType: string
        primaryKey: true      # H1: business key, never reused
        required: true
      - name: customer_id
        logicalType: string   # I1: joins to customers.customer_id
      - name: order_date
        logicalType: date
        description: When the customer ordered (transaction date, H6).
      - name: status
        logicalType: string
        description: See reference table order_status (J1).
      - name: email
        logicalType: string
        classification: restricted   # M1: personal data
      - name: updated_at
        logicalType: timestamp
        description: Set by the database on every change (E1, E2).
    quality:
      - metric: rowCount      # N2: compared with the source's daily control total
slaProperties:
  - property: freshness       # K3
    value: 24
    unit: h"""

EX_MANIFEST = """# manifest/erp/orders.yaml  (how we load it)
dataset: erp.orders
contract: contracts/erp-orders.yaml
source: {connection: erp_prod_replica, object: SALES.ORDERS}   # B2: read the replica
load:
  pattern: incremental_watermark        # F: decision record DR-014
  watermark_column: updated_at
  overlap: 2h
  full_compare: weekly                  # F5: catch deletes and drift
  window: "01:00-05:00"                 # C1: agreed with the source
  max_rows_per_second: 20000
silver:
  merge_keys: [order_no]
  sequence_by: updated_at               # H7
  tie_break: _ingested_at               # H4
  history: {type2: [status], type1: all_other}   # G2
  deletes: {soft_flag: is_deleted}      # G1
  lookback_days: 35                     # G: late corrections
  cluster_by: [order_no, order_date]    # merge key + date filter"""

EX_UC = """-- generated by the deployment pipeline from the two files above
COMMENT ON TABLE prod_silver.sales.orders IS 'One row per customer order.';
ALTER TABLE prod_silver.sales.orders ALTER COLUMN order_date COMMENT 'When the customer ordered (transaction date).';
ALTER TABLE prod_silver.sales.orders SET TAGS ('domain' = 'sales', 'owner' = 'priya.s', 'contract' = 'erp-orders@1.2.0');
ALTER TABLE prod_silver.sales.orders ALTER COLUMN email SET TAGS ('classification' = 'restricted');
ALTER TABLE prod_silver.sales.orders ALTER COLUMN email SET MASK governance.masks.email_mask;
ALTER TABLE prod_silver.sales.orders ADD CONSTRAINT orders_pk PRIMARY KEY (order_no);           -- informational
ALTER TABLE prod_silver.sales.orders ADD CONSTRAINT orders_customer_fk
  FOREIGN KEY (customer_id) REFERENCES prod_silver.sales.customers (customer_id);                 -- informational
ALTER TABLE prod_silver.sales.orders CLUSTER BY (order_no, order_date);"""


def answers_page():
    f_svg, f_cap = answers_flow()
    pre = lambda t: f'<pre style="background:var(--surface-2);border:var(--line);border-radius:12px;padding:12px 14px;overflow-x:auto;font-size:12.5px;line-height:1.45"><code>{E(t)}</code></pre>'
    sections = [
        ("plain", "In plain words", f"""<p class="eyebrow">In plain words</p><h2>One recipe card, many uses</h2>
<p>A restaurant writes each recipe once, on one card. The shopping list, the prep sheet, the allergy labels on the menu and the oven timer all come from that card. If the chef changes the recipe, everything else changes with it. Nobody keeps a second copy of the recipe in their head.</p>
<p>The answers from discovery work the same way. Each one is written once, in its home. The pipeline settings, the Unity Catalog metadata, the quality tests and the business glossary are generated from it, and the code reads them instead of hard-coding them.</p>
<figure class="diagram">{f_svg}<figcaption>{E(f_cap)}</figcaption></figure>"""),
        ("homes", "The eight homes", f"""<p class="eyebrow">The homes</p><h2>Eight homes, each with one job</h2>{tbl(["Home", "What it holds", "Format and place", "Owner", "Changed by"], HOMES)}"""),
        ("map", "Answer by answer", f"""<p class="eyebrow">The map</p><h2>Each group of answers, where it lives and who uses it</h2>
<p>Letters are the question groups on the <a href="{U}#questions">Upstreams page</a>. The last column is the part of the platform each answer shapes; it will link to the hop pages as they are written.</p>
{tbl(["Answers", "Home (written once)", "Generated into", "Used by"], ANS_MAP)}"""),
        ("split", "Contract or manifest", f"""<p class="eyebrow">The split</p><h2>Contract or manifest? The data's promise versus how we load it</h2>
<p>ODCS describes what a dataset promises. How we load it (watermarks, merge keys, history type, clustering, throttling) is our choice and changes more often, so it lives in the manifest, checked against the contract. Run-time state and secrets live in neither.</p>
{tbl(["Answer", "Home", "Why"], SPLIT)}"""),
        ("clustering", "Partitioning, Z-order or clustering", f"""<p class="eyebrow">Physical layout</p><h2>Partitioning, Z-order or liquid clustering</h2>
<p>All three decide which files a merge or a query must read and rewrite. On Databricks, <b>liquid clustering</b> is the default for new tables: it replaces both partitioning and Z-order, works incrementally, and its keys can be changed later without rewriting the table. <b>Partitioning</b> is kept for very large tables that need whole-partition operations. <b>Z-order</b> is for older tables until they move to clustering. The inputs come from upstream answers: the merge key (H), the date people filter by (H), the table's size and growth (K), retention rules (M) and how the data is read downstream.</p>
{tbl(["Option", "What it does", "Use it for", "Watch for"], LAYOUT_OPTIONS)}
<h3>Liquid clustering: which columns, by layer</h3>
<p>Up to four columns; fewer is usually better. The choice goes in the manifest and is generated into the table.</p>
{tbl(["Layer", "Cluster by", "Why"], CLUSTER)}
<p>On other platforms the same decision has different names: Iceberg has hidden partitioning and sort orders, BigQuery has partitioning and clustering, Snowflake has clustering keys. Pick by the same inputs.</p>"""),
        ("example", "Worked example", f"""<p class="eyebrow">Worked example</p><h2>One dataset, from answers to generated metadata</h2>
<p>An ERP's orders table. The comments point to the questions each line answers.</p>
<h3>The contract</h3>{pre(EX_ODCS)}
<h3>The manifest</h3>{pre(EX_MANIFEST)}
<h3>What the deployment generates in Unity Catalog</h3>{pre(EX_UC)}
<p>The engine then reads <code>merge_keys</code>, <code>sequence_by</code>, <code>history</code> and <code>deletes</code> to build silver. The quality framework turns the contract's rules into a uniqueness test on <code>order_no</code>, an orphan test on <code>customer_id</code> and a daily row-count reconciliation. Unity Catalog's key constraints are informational, so those tests are what actually catch duplicates and orphans.</p>"""),
    ]
    nxt = f'<p><b>Related:</b> <a href="/learn/data-platform-architecture/metadata-store/">the metadata store</a> (where the manifest is loaded), <a href="{P_LAYOUT}">Layout: catalogs, schemas and naming</a>, and <a href="/concepts/data-contracts/">data contracts</a>.</p>'
    return sub_page("answers", "Where the answers go", "Where the answers go: contract, manifest, catalog, code",
                    "Every answer is written once, in one home, and everything else is generated from it.",
                    "Where each discovery answer lives: the ODCS data contract, the pipeline manifest, Unity Catalog, quality tests, the ontology, the engine's code, decision records and the source agreement. With a worked example and how to choose liquid clustering columns.",
                    ["Each answer gets one home. Everything else (Unity Catalog metadata, pipeline settings, tests, the glossary) is generated from it, never typed by hand.",
                     "The data contract (ODCS) says what the data promises. The manifest says how we load it. Unity Catalog is where both are enforced at run time.",
                     "The ontology connects the same business thing across systems, which no single contract can do.",
                     "The code is one generic engine that reads these files; a new dataset is configuration, not a release."],
                    sections, ANS_Q, ANS_DECISIONS, ANS_FAQ, nxt,
                    "Where data discovery answers belong on a Databricks platform: ODCS data contracts, the pipeline manifest, generated Unity Catalog metadata, quality tests, ontology, decision records; with a worked example and liquid clustering choices.")


def main():
    out = ROOT / U.strip("/")
    for slug, fn in (("apis", apis_page), ("files", files_page), ("joins", joins_page), ("answers", answers_page)):
        (out / slug).mkdir(parents=True, exist_ok=True)
        (out / slug / "index.html").write_text(fn())
    print("upstreams in depth -> apis, files, joins")


if __name__ == "__main__":
    main()
