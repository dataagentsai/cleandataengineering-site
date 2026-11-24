"""Builds the body fragment for /learn/databricks-compute/sharing-data-out/.

    python3 _guides/sharing_data_out_build.py   (then python3 _guides/databricks_compute.py)

Writes _guides/databricks_compute/sharing-data-out.html. Edit the METHODS tables and the prose
strings in this file, not the generated fragment. The clean-room teaching section (CLEAN_ROOM)
is hand-written prose with its own drawing.
Part A: others read data that Databricks owns.  Part B: Databricks reads data that others own.
"""
import textwrap
from html import escape as E
from pathlib import Path

OUT = Path(__file__).parent / "databricks_compute" / "sharing-data-out.html"

W = 900
BOX_W = {2: 250, 3: 210, 4: 180}
BOX_Y, BOX_H = 15, 120
STEP_WRAP = 104


def fig(nodes, arrows, steps, aria, cap=""):
    """nodes: [(class, [title, line, ...])]; arrows: [(from, to, number, class)]; steps: ["text", ...]."""
    n = len(nodes)
    bw = BOX_W[n]
    gap = (W - n * bw) / (n - 1)
    xs = [i * (bw + gap) for i in range(n)]
    parts = []
    for i, (cls, lines) in enumerate(nodes):
        title, rest = lines[0], lines[1:]
        assert len(title) <= bw / 8.4, f"title too long: {title}"
        assert len(rest) <= 4, f"too many lines in {title}"
        parts.append(f'<rect class="{cls}" x="{xs[i]:.0f}" y="{BOX_Y}" width="{bw}" height="{BOX_H}" rx="6"/>')
        cx = xs[i] + bw / 2
        parts.append(f'<text class="b" x="{cx:.0f}" y="{BOX_Y + 27}" text-anchor="middle">{E(title)}</text>')
        for j, t in enumerate(rest):
            assert len(t) <= bw / 6.8, f"line too long ({len(t)} > {bw / 6.8:.0f}): {t}"
            parts.append(f'<text class="m" x="{cx:.0f}" y="{BOX_Y + 51 + 20 * j}" text-anchor="middle">{E(t)}</text>')
    pair_count, arc_count = {}, 0
    for a, b, num, cls in arrows:
        if abs(a - b) == 1:
            pair_count[tuple(sorted((a, b)))] = pair_count.get(tuple(sorted((a, b))), 0) + 1
    pair_seen = {}
    max_depth = 0
    mk = {"ln": "ar", "lg": "arg"}
    for a, b, num, cls in arrows:
        if abs(a - b) == 1:
            key = tuple(sorted((a, b)))
            k = pair_seen.get(key, 0)
            pair_seen[key] = k + 1
            y = 75 if pair_count[key] == 1 else (55 if k == 0 else 97)
            x1 = xs[a] + bw if a < b else xs[a]
            x2 = xs[b] if a < b else xs[b] + bw
            parts.append(f'<path class="{cls}" d="M{x1:.0f} {y}L{x2:.0f} {y}" marker-end="url(#{mk[cls]})"/>')
            mx, my = (x1 + x2) / 2, y
        else:
            depth = 38 + 24 * arc_count
            arc_count += 1
            max_depth = max(max_depth, depth)
            x1, x2 = xs[a] + bw / 2, xs[b] + bw / 2
            y0 = BOX_Y + BOX_H
            parts.append(f'<path class="{cls}" d="M{x1:.0f} {y0}C{x1:.0f} {y0 + depth},{x2:.0f} {y0 + depth},{x2:.0f} {y0}" marker-end="url(#{mk[cls]})"/>')
            mx, my = (x1 + x2) / 2, y0 + 0.75 * depth
        parts.append(f'<circle cx="{mx:.0f}" cy="{my:.0f}" r="11" fill="#fff" stroke="#1F1F1F" stroke-width="1.5"/>'
                     f'<text class="b" x="{mx:.0f}" y="{my + 5:.0f}" text-anchor="middle">{num}</text>')
    y = BOX_Y + BOX_H + max_depth + 34
    for i, s in enumerate(steps, 1):
        lines = textwrap.wrap(s, STEP_WRAP)
        for j, ln in enumerate(lines):
            lead = f"{i}." if j == 0 else ""
            parts.append(f'<text class="b" x="6" y="{y}">{lead}</text><text x="30" y="{y}">{E(ln)}</text>')
            y += 21
        y += 3
    h = y + 4
    svg = f'<svg viewBox="0 0 {W} {h:.0f}" role="img" aria-label="{E(aria)}">' + "".join(parts) + "</svg>"
    return f'<figure><div class="fig">{svg}</div>' + (f"<figcaption>{E(cap)}</figcaption>" if cap else "") + "</figure>"


def ul(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def method(sec_id, part, title, intro, figure, hood, use, avoid, extra="", cs=None):
    cs_html = ""
    if cs:
        cs_html = ('<h3>Cost, performance and security</h3><div class="tw"><table class="t">'
                   '<tr><th>Cost and performance</th><th>Security</th></tr>'
                   f'<tr><td>{ul(cs[0])}</td><td>{ul(cs[1])}</td></tr></table></div>')
    return (f'<section id="s{sec_id}"><p class="eyebrow">{E(part)}</p><h2>{E(title)}</h2><p>{intro}</p>{figure}'
            f'<h3>Under the hood</h3>{ul(hood)}{extra}'
            f'<div class="tw"><table class="t"><tr><th>Use it when</th><th>Do not use it when</th></tr>'
            f'<tr><td>{ul(use)}</td><td>{ul(avoid)}</td></tr></table></div>{cs_html}</section>\n')


# label -> (cost and performance bullets, security bullets)
COSTSEC = {
    "A1": (["No pipeline and no copy, so no extra storage for the recipient.",
            "You pay for storage and for the storage requests their reads make. They pay for their compute.",
            "Reads go straight from storage in parallel, so scan speed is good. The first query adds a short round trip to the sharing service.",
            "Cross-region or cross-cloud reads are charged by the cloud provider, normally to the data's owner."],
           ["Access is a grant to one named recipient. It is read-only and can be revoked.",
            "Signed links are short-lived and cover only the files for that query.",
            "Access is recorded in audit logs. No token exists to leak.",
            "Once rows are read the recipient can copy them. To limit this, share a view with row and column rules, not the base table."]),
    "A2": (["Same cost shape as A1: your storage requests and transfer, their compute.",
            "Very wide client support, but each client's speed depends on its own engine."],
           ["The bearer token works like a password. Anyone holding it can read until it expires or you revoke it.",
            "Set a short expiry, rotate it, and add an allowed IP list for the recipient where you can.",
            "Prefer federated login through your identity provider over long-lived tokens.",
            "Share views, not base tables, if rows or columns must be limited."]),
    "A4": (["Costs grow with the number of consumers, because each one's reads hit your storage and may cross regions.",
            "Free listings can still run up transfer fees for you."],
           ["A public listing is visible to everyone. Never list data that is sensitive, even if you intend to approve requests.",
            "Use private listings and approval for anything controlled.",
            "State the terms of use in the listing. The platform can revoke access, but it cannot stop misuse of data already read."]),
    "A5": (["No Databricks compute is used for reads. The other engine's compute is billed to them.",
            "Direct Parquet reads are fast when files are well sized. Many small files slow every engine, so compact them.",
            "UniForm adds a small amount of work after each write to produce the Iceberg metadata.",
            "Check that table features you use, such as deletion vectors and column mapping, are supported by the Iceberg reader."],
           ["The engine receives short-lived storage credentials, so you must trust that engine and whoever runs it.",
            "Row filters and column masks are enforced by Databricks compute. An engine reading files directly bypasses them, so tables that use them generally cannot be exposed this way. Check the current rules.",
            "Scope the credentials to the table, keep them short-lived, and watch access logs on the bucket."]),
    "A6": (["Warehouse compute is billed by the second. A stopped warehouse adds start-up time to the first query.",
            "Photon and the result cache make repeat queries cheap and fast.",
            "Concurrency is limited by warehouse size and clusters. Spikes queue up.",
            "Pulling large tables through it wastes warehouse time and is slow."],
           ["The strongest enforcement of the Part A routes: Databricks runs the query, so row filters, column masks and grants all apply.",
            "The consumer sees only results. Every query is in the audit log.",
            "Use a service principal with least privilege per app, OAuth rather than shared personal tokens, and private networking or IP allowed lists."]),
    "A7": (["You pay job compute plus the target's write cost. Network transfer applies if the target is elsewhere.",
            "Speed is set by the target's write rate. More parallel connections is faster but can overload it."],
           ["Target credentials belong in a secret scope, never in the notebook.",
            "After the push the data lives outside Unity Catalog. Row filters and masks do not follow it.",
            "Use TLS to the target and a write-only account limited to the tables it needs.",
            "Personal data is now in a second place that must be deleted too."]),
    "A8": (["Compute to write, storage for the copies and transfer for the download. Every run makes a new copy.",
            "Large sequential Parquet files are fast to write and fast to download."],
           ["The weakest route. Once downloaded there is no audit and no revoke.",
            "Encrypt at rest, give the receiver short-lived signed links or a scoped credential, and expire old folders.",
            "Keep personal data out of file names. Remove or mask sensitive columns before export."]),
    "B1": (["Cost is warehouse compute, the load on the source, and network transfer. There is no storage cost in Databricks.",
            "Speed depends on pushdown. A filter that is pushed down is fast, and one that is not drags many rows across the network.",
            "Each run is slower than reading Delta, and cannot use Delta data skipping or caching of the source.",
            "A heavy federated workload can slow or cost money on the source side."],
           ["The connection uses one account at the source for everyone allowed to use the connection. A user may see more than their own source rights allow.",
            "Use a least-privilege, read-only source account limited to the schemas you want to expose.",
            "Grant the foreign catalog only to the right groups.",
            "Open the source firewall only to Databricks' network, or use private connectivity. Credentials sit in the connection, not in notebooks."]),
    "B2": (["Your compute and storage request charges at their bucket. The other engine's compute is not used.",
            "Direct Parquet reads are near-native speed when file sizes are good.",
            "Metadata lookups add a round trip, and results may trail the other engine's latest commit."],
           ["You need cross-account access to their bucket. Use a read-only role limited to the table paths.",
            "The other catalog's own permissions are not mirrored. Define who in Databricks may read, using grants on the foreign catalog.",
            "Row and column rules defined in the other engine are not enforced when Databricks reads files directly."]),
    "B3": (["You pay for storage requests, and nothing is optimised for you. Compaction and clean-up of files you do not manage stay your responsibility.",
            "Managed-table features such as automatic maintenance mainly cover managed tables. Plan maintenance for external ones.",
            "Speed depends on the folder's file layout and format."],
           ["The credential is scoped to a path and is the key to everything under it. Give the IAM role or managed identity only the folders you need.",
            "Do not let external locations overlap, and restrict who can read raw paths directly, because that bypasses table-level grants.",
            "Grants on the external table are checked by Unity Catalog, but anyone with the storage role outside Databricks is not."]),
    "B4": (["You pay for your compute. The provider pays for storage requests and often the transfer, so providers may limit heavy use.",
            "Reads depend on network speed to the provider's storage. Repeated scans of a big remote table are slow and costly. Copy it once instead."],
           ["Treat shared data as untrusted input. Validate schema and values before joining it into your trusted tables.",
            "The provider can see which of their tables you read.",
            "Keep your own sensitive data out of the shared catalog, and grant read on the shared catalog only to those who need it."]),
    "B5": (["You pay pipeline compute, staging storage and the target tables. Source API call limits can cap how fast you load.",
            "Incremental loads are far cheaper and faster than full reloads, and change capture puts little load on the source."],
           ["Create a dedicated read-only source user or app with the minimum scopes. Keep credentials in a Unity Catalog connection.",
            "Personal data now lands in bronze tables. Apply masks and access grants on arrival.",
            "Network access to the source must be allowed. Use private connectivity where offered."]),
    "B6": (["Listing a huge folder gets slow and makes many storage requests. Use event notifications for big or busy folders, which need a small queue set-up cost.",
            "Reading is parallel and scales with the cluster. A scheduled run that stops when idle is cheaper than a stream that never stops."],
           ["Whoever can write to the landing folder can inject data. Limit write access to the known sources.",
            "Use the rescued data column or a quarantine table for bad records, and validate before promotion.",
            "Encrypt the bucket and restrict who may read raw files."]),
    "B7": (["A running stream keeps a cluster on all day. Where seconds are not needed, a scheduled run that processes what has arrived is much cheaper.",
            "Broker throughput units or partitions are a separate bill at the cloud.",
            "Latency is seconds. Throughput scales with partitions and cluster size."],
           ["Broker credentials belong in secrets. Use TLS and a topic-level read-only permission.",
            "Events can carry personal data. Apply masks when they land.",
            "Producers can send malformed events. Parse defensively and send bad ones to a dead-letter table."]),
    "B8": (["The source carries the load of every slice query, and a missing partition column makes it one slow read.",
            "Memory on the driver limits how much a custom API loop can hold. Keep results streaming into Delta."],
           ["Never put a password in the JDBC URL in a notebook. Use a secret scope or a Unity Catalog connection.",
            "Use a read-only database user, and allow only Databricks' network at the source.",
            "If you build queries from user input, parameterise them, or you invite SQL injection."]),
}


CU, DB, BX, CA = "cu", "db", "bx", "ca"
PA, PB = "Part A · others read what Databricks owns", "Part B · Databricks reads what others own"

# ---------------------------------------------------------------- Part A
A = []
A.append(dict(
    title="A1. Delta Sharing, Databricks to Databricks",
    intro="Both sides use Unity Catalog. The recipient mounts your share as a catalog in their own workspace and queries it like any other table. Nothing is copied.",
    nodes=[(DB, ["THEIR COMPUTE", "a Databricks workspace", "queries the shared catalog", "and pays for its own compute"]),
           (BX, ["SHARING SERVICE", "run by Databricks; checks", "the grant held in your", "Unity Catalog"]),
           (CU, ["YOUR CLOUD STORAGE", "the table's Parquet files", "and _delta_log", "never copied or moved"])],
    arrows=[(0, 1, 1, "ln"), (1, 0, 2, "ln"), (0, 2, 3, "lg")],
    steps=["Their query on the shared catalog goes to the sharing service.",
           "The service checks your grant, picks the files for the current table version using the Delta log and its min and max statistics, and replies with short-lived signed links.",
           "Their compute downloads those Parquet files straight from your storage. The service never carries the data."],
    cap="Set-up before step 1: they send you their metastore identifier, you create a recipient and a share, and you grant the share to that recipient.",
    hood=["It is a live read of your table, not a snapshot. The recipient sees new commits as you make them.",
          "The recipient can read tables, views, volumes, notebooks and AI models, and can read the table history or stream the changes.",
          "Access is read-only, and you can revoke it at any time. Links expire in minutes, so revoking takes effect quickly.",
          "Governance, audit and lineage stay in Unity Catalog on both sides."],
    use=["The partner is also on Databricks with Unity Catalog", "You want live data with no pipeline and no copy", "You need to revoke or audit access", "You share inside one company across accounts or clouds"],
    avoid=["The partner is not on Databricks (use open sharing)", "The partner must not see rows at all (use a clean room)", "The partner is in another region or cloud and will read big tables repeatedly: transfer fees add up, so replicate once", "You need the partner to write back"]))
A.append(dict(
    title="A2. Delta Sharing, open sharing",
    intro="The same protocol, but the recipient is not on Databricks. They use a credential and any tool that has a Delta Sharing client.",
    nodes=[(DB, ["THEIR TOOL", "Spark, pandas, Power BI,", "Tableau, Snowflake or any", "Delta Sharing client"]),
           (BX, ["SHARING SERVER", "checks their bearer token", "or federated login, then", "the share grant"]),
           (CU, ["YOUR CLOUD STORAGE", "the table's Parquet files", "stay where they are"])],
    arrows=[(0, 1, 1, "ln"), (1, 0, 2, "ln"), (0, 2, 3, "lg")],
    steps=["The client presents its credential and asks for a table, with any filters.",
           "The server checks the credential and the share, and replies with short-lived signed links to only the needed files.",
           "The client downloads the files directly from your storage and builds the rows itself."],
    cap="Set-up before step 1: you create a recipient of the token type and send them the credential file, or set up login through your identity provider.",
    hood=["The credential is a token with an expiry. You must rotate it and treat the file like a password.",
          "The protocol is open, so any tool with a client can read. Databricks does not need to be on the other side.",
          "You can share a table, a view, or a slice, and use dynamic views for row and column filtering.",
          "Compute for reading is the recipient's, billed to them. The storage requests land on your bucket."],
    use=["The partner is on another platform, or on nothing but a Python notebook", "You want governed, revocable, audited access", "The partner is a different company"],
    avoid=["The partner is on Databricks (use the Databricks to Databricks route, with no token to rotate)", "The partner is a warehouse engine such as Athena or Redshift with no client (see the AWS section below)", "You cannot manage token rotation"]))
A.append(dict(
    title="A4. Marketplace",
    intro="A catalogue of listings built on top of Delta Sharing. It adds discovery, requests, approvals and optional payment. The data still moves by sharing.",
    nodes=[(CU, ["YOU (provider)", "create a listing from", "a share; set terms,", "free or paid"]),
           (BX, ["MARKETPLACE", "shows the listing;", "routes requests to you", "for approval"]),
           (DB, ["CONSUMER", "browses, requests access,", "then reads the share as", "in A1 or A2"])],
    arrows=[(0, 1, 1, "ln"), (2, 1, 2, "ln"), (1, 2, 3, "lg")],
    steps=["You publish a listing that points at a share, with a description and sample data.",
           "A consumer finds it and requests access. Private listings can be limited to chosen consumers.",
           "You approve (or it is instant for open listings). The consumer gets the share and reads live data."],
    hood=["Marketplace is a listing and approval layer, not a different transport. Reads are Delta Sharing reads.",
          "Listings can carry notebooks, models and sample queries so a consumer can try the data fast.",
          "You still carry the sharing, storage-request and transfer costs of every consumer's reads."],
    use=["Many consumers, some you do not know yet", "You are selling or publishing a dataset or an AI model", "You want a place consumers can discover and try the data"],
    avoid=["One known partner. A direct share is simpler.", "The data is private and must not be browsable", "You cannot afford many consumers reading across regions"]))
A.append(dict(
    title="A5. UniForm and the Iceberg REST catalog",
    intro="This lets <em>your own</em> other engines read the same files you already have, as an Iceberg table, under Unity Catalog permissions.",
    nodes=[(DB, ["YOUR OTHER ENGINE", "Trino, Flink, Spark, EMR,", "Snowflake, Athena", "uses its own compute"]),
           (BX, ["UNITY CATALOG", "Iceberg REST endpoint;", "checks permissions and", "hands out credentials"]),
           (CU, ["YOUR CLOUD STORAGE", "Parquet data files, the", "Delta log, and Iceberg", "metadata (UniForm)"])],
    arrows=[(0, 1, 1, "ln"), (1, 0, 2, "ln"), (0, 2, 3, "lg")],
    steps=["The engine connects to the REST catalog and asks for a table.",
           "Unity Catalog checks the caller's permission, and replies with where the table's Iceberg metadata is and short-lived storage credentials.",
           "The engine reads the metadata and data files directly from your storage with its own compute. Databricks compute is not involved."],
    hood=["UniForm writes Iceberg metadata after each Delta commit, pointing at the same Parquet files. There is one copy of the data in two formats.",
          "The metadata is produced after the commit, so an Iceberg reader can be a little behind. Test the lag before promising freshness.",
          "Managed Iceberg tables are natively Iceberg in Unity Catalog, with no Delta log at all. They are a different table type, not a view of a Delta one.",
          "The consumer must be trusted. It receives storage credentials, so the permission check happens at the catalog, not on every file."],
    extra=('<div class="tw"><table class="t"><tr><th></th><th>Delta Sharing</th><th>UniForm and Iceberg REST catalog</th></tr>'
           '<tr><td>What it is</td><td>A sharing protocol with recipients</td><td>A format plus a catalog endpoint</td></tr>'
           '<tr><td>Reader needs</td><td>A Delta Sharing client</td><td>An Iceberg-capable engine</td></tr>'
           '<tr><td>How rows reach the reader</td><td>Signed links from the sharing server</td><td>Storage credentials from Unity Catalog, then direct reads</td></tr>'
           '<tr><td>Best across an organisation</td><td>Yes: recipient, audit and revoke are built in</td><td>No. It assumes you trust the engine.</td></tr>'
           '<tr><td>Best inside your estate</td><td>Adds a boundary you do not need</td><td>Yes: many engines, one copy</td></tr></table></div>'),
    use=["Your own Snowflake, Trino, Flink or EMR should read tables Databricks writes", "You want one copy and no pipeline", "You are moving toward an open lakehouse with several engines"],
    avoid=["The reader is another company (use Delta Sharing)", "You need a recipient, expiry and revoke built in", "You cannot test the metadata lag against your freshness promise"]))
A.append(dict(
    title="A6. SQL warehouse API, JDBC and ODBC",
    intro="The consumer does not get tables. It sends SQL and gets answers back. Databricks does the reading with its own compute.",
    nodes=[(DB, ["APP OR BI TOOL", "Lambda, Tableau, Power BI,", "your own service", "signs in as a user or a", "service principal"]),
           (BX, ["SQL WAREHOUSE", "Databricks compute; runs", "the query on Photon and", "applies permissions,", "row filters and masks"]),
           (CU, ["YOUR TABLES", "in Unity Catalog", "read by the warehouse"])],
    arrows=[(0, 1, 1, "ln"), (1, 2, 2, "ln"), (1, 0, 3, "lg")],
    steps=["The app sends SQL over JDBC or ODBC, or calls the SQL Statement Execution API over HTTPS.",
           "The warehouse starts if it is stopped, checks the caller's permissions and reads the tables.",
           "Results come back. Small results arrive inline. Large results can be returned as links to files that the app downloads."],
    hood=["Every query uses warehouse compute and is billed, so many small queries on a stopped warehouse can cost more than expected from start-up time.",
          "Row filters and column masks apply because it is Databricks that runs the query.",
          "Result size and result cache both matter: the same query repeated may be answered from cache."],
    use=["Apps, dashboards and services that need answers, not tables", "You want all governance applied by Databricks", "The consumer is small and cannot run an engine"],
    avoid=["Bulk extraction of whole tables. It is slow and uses warehouse time. Share or export instead.", "The consumer wants to join your data with theirs using their own engine", "You need sub-second lookups for thousands of users (use a serving layer)"]))
A.append(dict(
    title="A7. Push to another system",
    intro="Instead of waiting for someone to read, your job writes the rows into the system that needs them: an operational database, a queue, a CRM or a serving store.",
    nodes=[(CU, ["YOUR JOB", "a Lakeflow job or a", "streaming query that", "reads your Delta table"]),
           (BX, ["WRITER", "JDBC write, Kafka or", "Event Hubs sink, or", "an API call in batches"]),
           (DB, ["TARGET SYSTEM", "operational database,", "queue, CRM or serving", "store, owns its own copy"])],
    arrows=[(0, 1, 1, "ln"), (1, 2, 2, "ln")],
    steps=["The job reads a batch, or streams only the changes, from a Delta table.",
           "The writer sends rows in parallel batches. Use keyed upserts so a retry does not duplicate rows.",
           "The target stores its own copy. After that, Databricks has no control over it."],
    hood=["The target gets a copy. If the source changes, the copy is wrong until the next push.",
          "Retries happen. Make every write idempotent with a business key, or use the sink's exactly-once feature where it exists.",
          "Too many parallel connections can overload the target. Cap the number of write partitions."],
    use=["An operational system must hold the data in its own store", "The target must be fast and independent of Databricks", "Events must reach a queue or a stream"],
    avoid=["Only analysts read it. Share it instead and avoid a second copy.", "You cannot make the writes idempotent", "The target cannot take the load"]))
A.append(dict(
    title="A8. File export",
    intro="You write files to a bucket or an SFTP drop and the other side collects them. It is the oldest way and the weakest.",
    nodes=[(CU, ["YOUR JOB", "selects the rows, writes", "Parquet, CSV or JSON", "to a path"]),
           (BX, ["A BUCKET OR SFTP", "S3, ADLS, GCS", "or a file drop with", "its own permissions"]),
           (DB, ["RECEIVER", "downloads the files", "when they choose to"])],
    arrows=[(0, 1, 1, "ln"), (2, 1, 2, "ln")],
    steps=["On a schedule, the job writes a snapshot of the data to a new folder.",
           "The receiver is told, or polls, and downloads the files with credentials you gave them.",
           "Once downloaded the files are outside Unity Catalog. There is no audit and no way to take them back."],
    hood=["A snapshot goes stale the moment it is written.",
          "Add a manifest or a marker file when the folder is complete, or the receiver may read half-written files.",
          "Expire old folders. Every export is a copy somebody else may keep for ever."],
    use=["The receiver can only take a file (a regulator, an old system)", "A one-off hand-over where live access is not worth building"],
    avoid=["Anything where a live route exists", "Data that must be revocable", "Large volumes repeated daily. It gets expensive and drifts."]))

# ---------------------------------------------------------------- Part B
B = []
B.append(dict(
    title="B1. Lakehouse Federation (query federation)",
    intro="Databricks queries an external database in place. An admin makes a <b>connection</b> and a <b>foreign catalog</b>, and the remote tables then look like tables in Unity Catalog.",
    nodes=[(CU, ["YOU", "write SQL on the", "foreign catalog, such", "as pg.sales.orders"]),
           (CU, ["DATABRICKS WAREHOUSE", "plans the query, pushes", "filters and some", "aggregates down to the", "source, applies UC grants"]),
           (DB, ["EXTERNAL DATABASE", "Postgres, MySQL, SQL", "Server, Snowflake,", "BigQuery, Redshift ...", "keeps the data"])],
    arrows=[(0, 1, 1, "ln"), (1, 2, 2, "ln"), (2, 1, 3, "lg"), (1, 0, 4, "lg")],
    steps=["You run SQL against the foreign catalog. Unity Catalog checks you may read it.",
           "Databricks turns the part it can push down into a query in the source's own dialect and sends it using the connection's credentials.",
           "The source runs that query on its own engine and returns only the matching rows over the network.",
           "Databricks joins, aggregates the rest and returns the result. Reads only: you cannot write to the source."],
    hood=["No data is stored in Databricks. Each query reads the source again, so the source carries the load.",
          "Pushdown decides the speed. A filter or aggregate that cannot be pushed down means pulling many rows across the network.",
          "Governance is Unity Catalog's: grants on the foreign catalog, with the connection's own credential used on the remote side.",
          "Credentials sit in the connection, so one account at the source serves everyone allowed to use the connection."],
    use=["Exploring or prototyping before you decide what to ingest", "Occasional joins of your lakehouse data with a small reference table", "One-off analysis", "Source data must stay where it is"],
    avoid=["The same big query runs often. Ingest instead, so the source is not hit each time.", "Large joins across the network", "The source database is busy production and cannot take analytic reads", "You need history, time travel or Delta features on that data"]))
B.append(dict(
    title="B2. Catalog federation",
    intro="The data is files in cloud storage, but another catalog (a Hive metastore, AWS Glue, Snowflake's open catalog or another Iceberg REST catalog) owns the metadata. Databricks asks that catalog <em>which files</em>, then reads the files itself.",
    nodes=[(CU, ["DATABRICKS COMPUTE", "Unity Catalog treats the", "external catalog as a", "foreign catalog"]),
           (DB, ["EXTERNAL CATALOG", "Hive metastore, Glue,", "Snowflake open catalog,", "Iceberg REST", "knows the table's files"]),
           (DB, ["STORAGE WITH THE FILES", "S3, ADLS or GCS", "Delta, Iceberg or Parquet", "written by the other engine"])],
    arrows=[(0, 1, 1, "ln"), (1, 0, 2, "ln"), (0, 2, 3, "lg")],
    steps=["Databricks asks the external catalog about the table.",
           "The catalog answers with the table's schema and the location and list of its files.",
           "Databricks reads those files directly from storage with its own compute, using an external location you configured. The other engine is not involved."],
    hood=["Compared with query federation, the other engine's compute is not used at all, so it carries no load.",
          "Reading is allowed to follow the other catalog's metadata, so what you see can be briefly behind its latest commit.",
          "Unity Catalog governs who in Databricks may read. You must still give Databricks permission on the bucket.",
          "Check which catalogs and table formats are supported in your region before you rely on this."],
    use=["Another engine owns and writes the table, and you want to read it from Databricks with no copy", "A lake that is governed by Glue or Snowflake today", "You are migrating slowly and both worlds must see the same data"],
    avoid=["The source is a normal database, not files (use query federation)", "You need to write to the table from Databricks", "The other catalog cannot be reached from your network"]))
B.append(dict(
    title="B3. External locations, external tables and volumes",
    intro="You point Unity Catalog at a folder in cloud storage, give it a credential, and then define tables or volumes over that folder. Databricks reads in place.",
    nodes=[(CU, ["DATABRICKS COMPUTE", "runs SELECT on an", "external table or reads", "a volume path"]),
           (BX, ["UNITY CATALOG", "external location = path +", "storage credential;", "grants decide who reads"]),
           (DB, ["CLOUD STORAGE", "a bucket or folder that", "other systems or teams", "also use"])],
    arrows=[(0, 1, 1, "ln"), (1, 0, 2, "ln"), (0, 2, 3, "lg")],
    steps=["The query names an external table. Databricks asks Unity Catalog about it.",
           "Unity Catalog checks the user's grants, then issues a short-lived credential scoped to that path only.",
           "Compute reads the files straight from the folder. Nothing is copied, and the folder's owner keeps full control."],
    hood=["Set-up is once per folder: a storage credential (an IAM role or managed identity) and an external location with the path.",
          "A table over files you do not manage gets none of the automatic maintenance that managed tables get. Compaction and clean-up stay your job.",
          "Other writers can change the files while you read. A Delta table makes that safe, but a folder of CSVs does not."],
    use=["Files are produced by other systems and you only need to read them", "A shared lake that other engines also use", "Raw landing folders, before ingestion", "Unstructured files such as PDFs and images (volumes)"],
    avoid=["Nobody else uses the data. A managed table is cheaper to run, because Databricks looks after it.", "The bucket belongs to another organisation you do not fully trust", "You need strong consistency while another system rewrites the files"]))
B.append(dict(
    title="B4. Delta Sharing as a recipient",
    intro="This is A1 and A2 seen from the receiving side. A provider shares tables with you, and you mount the share as a read-only catalog.",
    nodes=[(CU, ["YOUR COMPUTE", "queries the shared", "catalog like any other", "and pays for itself"]),
           (DB, ["PROVIDER SHARING SERVER", "checks who you are and", "that the share was granted", "to you"]),
           (DB, ["PROVIDER STORAGE", "their Parquet files,", "left where they are"])],
    arrows=[(0, 1, 1, "ln"), (1, 0, 2, "ln"), (0, 2, 3, "lg")],
    steps=["Your query is sent to the provider's sharing server along with your identity.",
           "The server answers with short-lived signed links to just the files your query needs.",
           "Your compute downloads those files from the provider's storage. The data is theirs and is never stored in your account."],
    cap="Set-up: send the provider your metastore identifier, or receive a credential file. Then create a catalog from the share and grant it inside your workspace.",
    hood=["It is read-only and live. You see what they publish, when they publish it.",
          "You do not control the provider's history, retention, schema changes or when they revoke.",
          "If the provider is in another region or cloud, every read can carry transfer fees. One fix is to copy once into your own region."],
    use=["A partner or vendor publishes data you want to use without a pipeline", "Public or commercial data from a marketplace", "You need current data and cannot wait for a file drop"],
    avoid=["You need to modify, annotate or keep history the provider will not keep (copy it first)", "You will scan the same big remote table many times (copy it once)", "You need guaranteed availability outside the provider's control"]))
B.append(dict(
    title="B5. Lakeflow Connect (managed connectors)",
    intro="Databricks runs the connection for you. It reads changes from a SaaS app or a database, lands them, and keeps your tables up to date incrementally.",
    nodes=[(DB, ["SOURCE", "Salesforce, Workday,", "SQL Server, ServiceNow,", "Google Analytics ..."]),
           (BX, ["MANAGED CONNECTOR", "reads changes through", "the source's API or its", "change log (CDC)"]),
           (BX, ["STAGING", "changes are written to", "a Unity Catalog", "volume"]),
           (CU, ["YOUR TABLES", "streaming tables, in", "bronze, kept current by", "incremental updates"])],
    arrows=[(0, 1, 1, "ln"), (1, 2, 2, "ln"), (2, 3, 3, "ln")],
    steps=["On a schedule, the connector reads what has changed at the source, using a credential you created for it.",
           "The changes are staged in a volume, with the position of the last change remembered.",
           "A pipeline applies the changes to Delta tables, so the lakehouse copy follows the source without full reloads."],
    hood=["It is a copy. You pay for the pipeline compute and the storage, and you gain speed and independence from the source.",
          "For databases, change capture needs the source's change log enabled and a small gateway that reads it.",
          "The list of supported sources grows and has limits per source. Check it before designing around a connector."],
    use=["The source is a supported SaaS app or database", "You want incremental loading with little code", "Many sources, one pattern"],
    avoid=["Your source is not on the list. Use files, streams or JDBC.", "You need to reshape the data before landing it", "A tiny one-off pull. A notebook is faster to build."]))
B.append(dict(
    title="B6. Auto Loader (files landing in storage)",
    intro="Other systems drop files into a bucket. Auto Loader notices new files and ingests each one exactly once.",
    nodes=[(DB, ["OTHER SYSTEMS", "export jobs, SaaS tools,", "devices, partners", "drop files in"]),
           (BX, ["CLOUD STORAGE", "a landing folder;", "new files appear over", "time"]),
           (CU, ["AUTO LOADER STREAM", "the cloudFiles source;", "a checkpoint remembers", "which files are done"]),
           (CU, ["YOUR TABLES", "a bronze Delta table", "with schema tracking"])],
    arrows=[(0, 1, 1, "ln"), (2, 1, 2, "ln"), (1, 2, 3, "lg"), (2, 3, 4, "ln")],
    steps=["Another system writes files into the landing folder.",
           "Auto Loader finds new files, either by listing the folder or by using the cloud's file-event notifications.",
           "It reads only the new files. The checkpoint records them, so a restart does not read them again.",
           "Rows are appended to a Delta table. New columns can be detected and handled by schema evolution."],
    hood=["Listing mode is simple but slows down in a very large folder. Notification mode scales better and needs some cloud set-up.",
          "The checkpoint is the memory. If you delete it, files are read again.",
          "It can run continuously or as a scheduled batch that stops when there is nothing new."],
    use=["Files arrive over time from other systems", "Millions of small files you cannot track by hand", "The schema may drift"],
    avoid=["A handful of files read once. A plain read is simpler.", "The source is a database or a message stream", "Files are overwritten in place. Auto Loader expects new files, not changed ones."]))
B.append(dict(
    title="B7. Streaming sources: Kafka, Event Hubs, Kinesis, Pub/Sub",
    intro="Events live in a broker for a while. A Structured Streaming query reads them in order and remembers how far it got.",
    nodes=[(DB, ["EVENT BROKER", "Kafka, Event Hubs,", "Kinesis or Pub/Sub;", "keeps events for days"]),
           (CU, ["STREAMING QUERY", "reads from a stored offset;", "a checkpoint holds the", "offset in your storage"]),
           (CU, ["DELTA TABLE", "append-only events table", "written exactly once"])],
    arrows=[(1, 0, 1, "ln"), (0, 1, 2, "lg"), (1, 2, 3, "ln")],
    steps=["The query asks the broker for events after the last offset it saved.",
           "The broker returns the next batch of events.",
           "The batch is appended to Delta and the new offset is saved. After a crash, the query restarts from the saved offset."],
    hood=["If the query is down for longer than the broker's retention, events are gone. Size retention for your worst outage.",
          "Delta as the sink makes the write exactly-once, so replays do not duplicate rows.",
          "Latency is seconds. Real-time lookups still belong in a serving layer."],
    use=["Events arrive continuously and need to be queryable within seconds or minutes", "You need replay after a failure"],
    avoid=["Data is daily or hourly and a batch is fine. A stream costs an always-on cluster.", "You need answers in milliseconds for an app (use a serving layer)"]))
B.append(dict(
    title="B8. JDBC and custom connectors in a job",
    intro="You write the reading code. Spark opens several connections to the source and reads slices of a table in parallel.",
    nodes=[(CU, ["YOUR SPARK JOB", "spark.read.jdbc with a", "partition column and", "lower and upper bounds"]),
           (CU, ["WORKERS", "each opens its own", "connection and reads", "one slice of the table"]),
           (DB, ["SOURCE", "any database or API", "with a JDBC driver,", "or a Python client"])],
    arrows=[(0, 1, 1, "ln"), (1, 2, 2, "ln"), (2, 1, 3, "lg")],
    steps=["The job splits the key range into slices, one per partition.",
           "Each worker sends its own query for its slice, such as WHERE id BETWEEN a AND b.",
           "Rows come back in parallel and are written to a Delta table by the job."],
    hood=["Without a partition column, Spark uses one connection and one task, so a large table is read very slowly.",
          "Each connection loads the source. Cap the partition count so you do not overload it.",
          "Custom Python or REST code runs on the driver or in functions. Large API pulls need their own paging and retries."],
    use=["No managed connector or federation covers the source", "You need custom logic, paging or authentication", "A one-off or rare extraction"],
    avoid=["A managed connector exists. It handles incremental loading and retries for you.", "The table has no good numeric or date key to slice on", "The source is production at its busiest hour"]))

CLEAN_ROOM = '''<section id="s{id}"><p class="eyebrow">Part A · others read what Databricks owns</p><h2>A3. Clean room, taught from zero</h2>
<p>Everything so far hands the other side <em>rows</em>. A clean room is for when you must not.</p>
<h3>The problem it solves</h3>
<p>A shop knows who bought what. A brand knows who saw its online advert. Together they could answer a valuable question: <b>"Of the people who saw the advert, how many bought?"</b> To answer it, somebody has to match the two customer lists. But neither side may hand its list to the other. Customer lists are private, and privacy law forbids passing them around.</p>
<h3>The old ways, and why they fail</h3>
<ul>
<li><b>Swap the lists.</b> Now each side holds the other's customers. This is exactly what you were not allowed to do.</li>
<li><b>Give both lists to a third party.</b> You moved the risk to someone else, and you must trust them completely.</li>
<li><b>Hash the emails and swap those.</b> Better, but the other side can still test any email they already know against the hashes.</li>
</ul>
<h3>The clean room idea</h3>
<p>Build a <b>locked room</b>. Both sides place their data inside it, and neither can look at the other's rows. The only thing that runs in the room is a piece of code that <b>both sides have read and approved</b>. Only the result of that code comes out, for example a count, never the rows.</p>
<figure><div class="fig">
<svg viewBox="0 0 900 390" role="img" aria-label="A shop and a brand each share data into a locked clean room. An approved notebook runs inside. Only a summary result comes out.">
<rect class="cu" x="10" y="105" width="200" height="120" rx="6"/><text class="b" x="110" y="132" text-anchor="middle">SHOP</text><text class="m" x="110" y="154" text-anchor="middle">customers and purchases</text><text class="m" x="110" y="172" text-anchor="middle">stays in the shop's own</text><text class="m" x="110" y="188" text-anchor="middle">Unity Catalog</text><text class="m" x="110" y="208" text-anchor="middle">brand never sees the rows</text>
<rect class="db" x="690" y="105" width="200" height="120" rx="6"/><text class="b" x="790" y="132" text-anchor="middle">BRAND</text><text class="m" x="790" y="154" text-anchor="middle">who saw the advert</text><text class="m" x="790" y="172" text-anchor="middle">stays in the brand's own</text><text class="m" x="790" y="188" text-anchor="middle">Unity Catalog</text><text class="m" x="790" y="208" text-anchor="middle">shop never sees the rows</text>
<rect class="ca ds" x="265" y="25" width="370" height="250" rx="10"/><text class="h" x="450" y="52" text-anchor="middle">THE CLEAN ROOM (locked)</text>
<rect class="bx" x="290" y="68" width="320" height="92" rx="6"/><text class="b" x="450" y="92" text-anchor="middle">Approved notebook</text><text class="m" x="450" y="112" text-anchor="middle">match the two lists on a hashed email</text><text class="m" x="450" y="130" text-anchor="middle">count shoppers who saw the advert</text><text class="m" x="450" y="148" text-anchor="middle">and bought, grouped by region</text>
<rect class="bx" x="290" y="178" width="320" height="82" rx="6"/><text class="b" x="450" y="202" text-anchor="middle">Rules of the room</text><text class="m" x="450" y="222" text-anchor="middle">both sides approved this exact code</text><text class="m" x="450" y="240" text-anchor="middle">every run is logged</text>
<path class="ln" d="M210 165L265 165" marker-end="url(#ar)"/><path class="ln" d="M690 165L635 165" marker-end="url(#ar)"/>
<text class="m" x="237" y="150" text-anchor="middle">shared in,</text><text class="m" x="663" y="150" text-anchor="middle">shared in,</text>
<text class="m" x="237" y="190" text-anchor="middle">not given</text><text class="m" x="663" y="190" text-anchor="middle">not given</text>
<path class="lg" d="M450 275L450 312" marker-end="url(#arg)"/>
<rect class="ca" x="260" y="316" width="380" height="60" rx="6"/><text class="b" x="450" y="341" text-anchor="middle">Only this comes out</text><text class="m" x="450" y="361" text-anchor="middle">"12,400 people saw it and bought. North 4,100, South 8,300."</text>
</svg></div>
<figcaption>Each side keeps its own data. A notebook that both sides approved runs in the room. Only the answer leaves.</figcaption></figure>
<h3>Under the hood</h3>
<div class="tw"><table class="t">
<tr><th>Promise</th><th>How it is kept</th></tr>
<tr><td>Raw data is not handed over</td><td>Each side keeps its tables in its own account. They are shared into the room using Delta Sharing, so the other side can see names and columns but not rows. Rows are only touched by approved code.</td></tr>
<tr><td>Only agreed code runs</td><td>A notebook is proposed by one side and must be approved by the others before anyone can run it. Changing the code means approving again.</td></tr>
<tr><td>Results are limited</td><td>The approved notebook runs on serverless compute that Databricks manages, and only its output tables come out, to the party that ran it.</td></tr>
<tr><td>You can prove what happened</td><td>Runs and approvals are recorded in an audit log.</td></tr>
</table></div>
<div class="callout w"><p><b>Where a clean room can still leak.</b> The room guarantees <em>who approved what code</em>. It does not judge whether the output is safe. A notebook that simply wrote out one customer per row would be approved and would run. So the privacy rule has to be written <em>into the notebook</em> and checked by the reviewers: for example, never output a group smaller than 100 people, and never output a column that identifies a person.</p></div>
<h3>Industry idea, Databricks product</h3>
<p>"Data clean room" is an industry idea that began in advertising. Snowflake, AWS, Google, LiveRamp and others sell their own versions, and they enforce privacy in different ways (query rules, thresholds, encryption). <b>Databricks Clean Rooms</b> is Databricks' version, built on Delta Sharing and Unity Catalog. When a client says "clean room", ask which one they mean.</p>
<div class="tw"><table class="t">
<tr><th>Use it when</th><th>Do not use it when</th></tr>
<tr><td><ul><li>Two parties must analyse data together and neither may reveal raw rows: ads measurement, shared-customer overlap, joint research, fraud signals across a bank and an insurer</li><li>You can state the question in advance, because the approved code <em>is</em> the room</li></ul></td>
<td><ul><li>The other party is allowed to see the rows. Use Delta Sharing; it is simpler and cheaper.</li><li>You only want to publish a dataset to many buyers (use Marketplace)</li><li>You do not yet know the question you want to answer together</li><li>Nobody will review the code properly. Then the room gives false comfort.</li></ul></td></tr>
</table></div>
<h3>Cost, performance and security</h3>
<div class="tw"><table class="t"><tr><th>Cost and performance</th><th>Security</th></tr>
<tr><td><ul><li>Each run uses serverless compute that is billed, and each side still pays for its own storage.</li><li>It is built for scheduled or on-demand batch analysis, not for interactive lookups. Expect start-up time per run.</li><li>Agree who pays for runs before you build the room.</li></ul></td>
<td><ul><li>The strongest privacy of any route: neither side sees the other's rows.</li><li>Only approved code runs, and each change needs approval again. Runs are audited.</li><li>The weak point is the notebook itself. Review it for minimum group sizes and for any column that identifies a person.</li><li>Limit what the output may contain, and who may read the output tables.</li></ul></td></tr></table></div></section>
'''

MAP_A = '''<div class="tw"><table class="t">
<tr><th>Way out</th><th>Consumer gets</th><th>Best for</th><th>Verdict</th></tr>
<tr><td><a href="#s{A1}">A1 Delta Sharing, Databricks to Databricks</a></td><td>Live read-only tables</td><td>Partner on Databricks</td><td class="v pursue">Pursue</td></tr>
<tr><td><a href="#s{A2}">A2 Delta Sharing, open</a></td><td>Live read-only tables</td><td>Partner on another platform</td><td class="v pursue">Pursue</td></tr>
<tr><td><a href="#s{A3}">A3 Clean room</a></td><td>Only approved answers</td><td>Rows may not be revealed</td><td class="v pursue">Pursue, only for a real privacy need</td></tr>
<tr><td><a href="#s{A4}">A4 Marketplace</a></td><td>A share, found through a listing</td><td>Many or unknown consumers</td><td class="v pursue">Pursue</td></tr>
<tr><td><a href="#s{A5}">A5 UniForm and Iceberg REST catalog</a></td><td>Direct file reads by their engine</td><td>Your own other engines</td><td class="v pursue">Pursue</td></tr>
<tr><td><a href="#s{A6}">A6 SQL warehouse API, JDBC, ODBC</a></td><td>Query answers</td><td>Apps and BI</td><td class="v pursue">Pursue</td></tr>
<tr><td><a href="#s{A7}">A7 Push to another system</a></td><td>Their own copy in their system</td><td>Operational targets</td><td class="v pursue">Pursue</td></tr>
<tr><td><a href="#s{A8}">A8 File export</a></td><td>Files</td><td>Receivers that can only take files</td><td class="v">Last resort</td></tr>
<tr><td>Storage keys on managed table paths</td><td>Everything, ungoverned</td><td>Nothing</td><td class="v drop">Drop: bypasses Unity Catalog, so no audit, masks or revoke</td></tr>
</table></div>
<h3>Choosing, step by step</h3>
<ol>
<li>Is the consumer an <b>app or a person</b>? Use A6, the SQL warehouse.</li>
<li>Is the consumer a data platform? Ask <b>"may they see my rows?"</b> If not, build a clean room (A3).</li>
<li>If yes and they are on Databricks, use A1. If not, use A2.</li>
<li>Many unknown buyers? Use the Marketplace (A4).</li>
<li>Your own other engines on your own data? Use A5.</li>
<li>Does an operational system need the data inside it? Push it (A7). Only a file will do? Export it (A8), last.</li>
</ol>'''

MAP_B = '''<div class="tw"><table class="t">
<tr><th>Way in</th><th>Where the data lives</th><th>Best for</th><th>Verdict</th></tr>
<tr><td><a href="#s{B1}">B1 Lakehouse Federation (query)</a></td><td>Stays in the source database</td><td>Exploring, small lookups, prototypes</td><td class="v pursue">Pursue, for light use</td></tr>
<tr><td><a href="#s{B2}">B2 Catalog federation</a></td><td>Stays in the other engine's files</td><td>A lake another engine owns</td><td class="v pursue">Pursue</td></tr>
<tr><td><a href="#s{B3}">B3 External locations, tables, volumes</a></td><td>Stays in the folder</td><td>Shared lake, raw landing files</td><td class="v pursue">Pursue</td></tr>
<tr><td><a href="#s{B4}">B4 Delta Sharing as a recipient</a></td><td>Stays at the provider</td><td>Partner or vendor data, no pipeline</td><td class="v pursue">Pursue</td></tr>
<tr><td><a href="#s{B5}">B5 Lakeflow Connect</a></td><td>Copied into Delta, kept current</td><td>Supported SaaS and databases</td><td class="v pursue">Pursue</td></tr>
<tr><td><a href="#s{B6}">B6 Auto Loader</a></td><td>Copied into Delta</td><td>Files landing over time</td><td class="v pursue">Pursue</td></tr>
<tr><td><a href="#s{B7}">B7 Streaming sources</a></td><td>Copied into Delta</td><td>Event streams</td><td class="v pursue">Pursue</td></tr>
<tr><td><a href="#s{B8}">B8 JDBC and custom code</a></td><td>Copied into Delta</td><td>Sources nothing else covers</td><td class="v">Fallback</td></tr>
</table></div>
<h3>Choosing, step by step</h3>
<ol>
<li>Must the data <b>stay where it is</b>, and the use is light or exploratory? Use B1.</li>
<li>Is it <b>files</b> that another engine or catalog owns? Use B2. Plain folders with no catalog? Use B3.</li>
<li>Is a partner publishing it through <b>Delta Sharing</b>? Use B4.</li>
<li>Do you need your <b>own copy</b>, kept fresh? Use B5 for a supported source, B6 for files, B7 for events and B8 only if nothing else fits.</li>
<li>Will the same remote table be read again and again? Stop federating. Copy it once and keep it current.</li>
</ol>'''

AWS = '''<section id="s{id}"><p class="eyebrow">Worked example</p><h2>Exposing Unity Catalog tables to AWS services</h2>
<p>The right route depends on what the AWS service needs.</p>
<div class="tw"><table class="t">
<tr><th>AWS consumer</th><th>Route</th><th>Verdict</th></tr>
<tr><td>Athena, Redshift, EMR, Glue reading the same tables</td><td>A5: Iceberg REST catalog. Athena and Redshift through Glue Data Catalog federation, so Lake Formation governs on the AWS side.</td><td class="v pursue">Pursue: no copy, no Databricks compute</td></tr>
<tr><td>Lambda, ECS, Step Functions, QuickSight needing answers</td><td>A6: SQL warehouse API, JDBC, or the QuickSight Databricks connector</td><td class="v pursue">Pursue</td></tr>
<tr><td>Another AWS account or another company's team</td><td>A2: Delta Sharing with a Spark or pandas client</td><td class="v pursue">Pursue: clean recipient boundary</td></tr>
<tr><td>A service that only takes files in S3</td><td>A8: scheduled Parquet export</td><td class="v">Last resort</td></tr>
<tr><td>Anything pointed straight at a managed table's S3 path</td><td>Bucket policy or keys</td><td class="v drop">Drop</td></tr>
</table></div>
<h3>Why not Delta Sharing for Athena and Redshift?</h3>
<p>Delta Sharing needs a <b>client</b> on the reading side: a connector that asks the sharing server for signed file links and downloads the files itself. Spark, pandas, Power BI and similar tools have one. To my knowledge Athena and Redshift do not, because they read through the AWS Glue catalog and Lake Formation instead. To use Delta Sharing with them you would build a Glue or EMR Spark job that reads the share and writes a copy into S3 or Redshift. That brings back a pipeline and a staleness window. Other reasons it fits badly inside your own AWS estate:</p>
<ul>
<li>The reader must understand the table's Delta features, and some AWS-side readers lag behind newer ones.</li>
<li>Every read goes through signed links, which suits modest tables more than large warehouse scans.</li>
<li>Delta Sharing is built for crossing an organisation boundary. Inside your own estate that boundary only adds cost.</li>
</ul>
<p>Use Delta Sharing for an AWS party that is a <em>different organisation</em>, or for one that reads through a Spark or pandas client.</p></section>
'''

COST = '''<section id="s{id}"><p class="eyebrow">Both directions</p><h2>Cost traps and things to watch</h2>
<div class="tw"><table class="t">
<tr><th>Trap</th><th>Why</th><th>What to do</th></tr>
<tr><td>Cross-region or cross-cloud reads</td><td>The cloud provider charges when data leaves a region, on every read</td><td>Keep the consumer in the data's region, or replicate once. See <a href="/learn/databricks-compute/delta-sharing-and-regions/#s25">cross-region cost</a>.</td></tr>
<tr><td>Direct reads by an outside engine (A5, B2, B3)</td><td>Their compute is billed to them, but the storage requests land on the bucket owner</td><td>Watch request costs on the bucket. Keep files compacted so there are fewer, larger ones.</td></tr>
<tr><td>Federated queries run again and again (B1)</td><td>Each run reads the source again, and the source's owner carries the load</td><td>Once a query is routine, ingest the table instead.</td></tr>
<tr><td>UniForm lag (A5)</td><td>Iceberg metadata is produced after the Delta commit</td><td>Test the lag before promising freshness.</td></tr>
<tr><td>Clean room compute (A3)</td><td>Approved notebooks run on serverless compute, which is billed</td><td>Agree who pays for runs before you build the room.</td></tr>
<tr><td>Copies from exports and pushes (A7, A8)</td><td>Each one is a new copy outside governance</td><td>Prefer a live route. If you must copy, expire the copy.</td></tr>
</table></div>
<h3>Security at a glance</h3>
<div class="tw"><table class="t">
<tr><th>Route</th><th>Who enforces row and column rules</th><th>What the other side can do with data</th><th>Can you revoke?</th></tr>
<tr><td>A1, A2 Delta Sharing</td><td>You, through the views you share</td><td>Read it, and copy what they read</td><td>Yes, quickly</td></tr>
<tr><td>A3 Clean room</td><td>The approved notebook</td><td>See only approved outputs</td><td>Yes, remove the collaborator</td></tr>
<tr><td>A5 Iceberg REST catalog</td><td>Only table-level checks at the catalog</td><td>Read the files and copy them</td><td>Credentials expire; revoke the grant</td></tr>
<tr><td>A6 SQL warehouse</td><td>Databricks, on every query</td><td>See results only</td><td>Yes, remove the grant</td></tr>
<tr><td>A7, A8 push or export</td><td>Nobody, after it leaves</td><td>Keep everything</td><td>No</td></tr>
<tr><td>B1 Query federation</td><td>The source account and your grants</td><td>(inbound) users see what the connection account can see</td><td>Yes, drop the grant or connection</td></tr>
<tr><td>B2, B3 Reading others' files</td><td>Only grants in Databricks</td><td>(inbound) their row rules are not applied</td><td>Yes, remove the role</td></tr>
</table></div>
<div class="callout w"><p><b>Not confirmed here, check the current documentation:</b> which AWS engines support Glue federation to Unity Catalog and in which regions; how many collaborators a Databricks clean room allows and which non-Databricks collaborators it supports; whether managed Iceberg tables are available in your account; the list of Lakehouse Federation sources and Lakeflow Connect connectors, which grows; which external catalogs catalog federation supports; and the size of UniForm metadata lag for your table type. This page was written from memory of the documentation.</p></div></section>
'''


def build():
    out = []
    n = 65
    out.append(f'''<section id="s{n}"><p class="eyebrow">Sharing data in and out</p><h2>Two directions, and three layers</h2>
<p>Two questions get mixed up. <b>Part A</b>: how can someone else read data that <em>Databricks owns</em>? <b>Part B</b>: how can Databricks read data that <em>someone else owns</em>? Each has its own set of methods. Every method below has a picture of how it works inside, a list for when to use it, and a list for when not to.</p>
<div class="tw"><table class="t">
<tr><th>Layer</th><th>The question it answers</th><th>Names you will meet</th></tr>
<tr><td><b>1. Reading the data</b></td><td>"Can they read my table, safely, without me copying it?"</td><td>Delta Sharing, Marketplace, SQL warehouse, Lakehouse Federation</td></tr>
<tr><td><b>2. Computing without seeing</b></td><td>"Can we answer one question together without either of us showing our rows?"</td><td>Clean room</td></tr>
<tr><td><b>3. File format and catalog</b></td><td>"Can another engine read the same files?"</td><td>UniForm, Iceberg REST catalog, catalog federation, managed Iceberg tables</td></tr>
</table></div>
<p>Delta Sharing is a <em>protocol</em> (layer 1). A clean room is a <em>product</em> that uses it (layer 2). UniForm is a <em>file format trick</em> (layer 3) and shares nothing by itself.</p>
<figure><div class="fig">
<svg viewBox="0 0 900 270" role="img" aria-label="Part A: others read data that Databricks owns, going out. Part B: Databricks reads data that others own, coming in.">
<rect class="cu" x="330" y="75" width="240" height="120" rx="6"/><text class="b" x="450" y="108" text-anchor="middle">DATABRICKS</text><text class="m" x="450" y="130" text-anchor="middle">Unity Catalog tables</text><text class="m" x="450" y="148" text-anchor="middle">and the files behind them</text>
<rect class="db" x="10" y="75" width="230" height="120" rx="6"/><text class="b" x="125" y="108" text-anchor="middle">OTHERS</text><text class="m" x="125" y="130" text-anchor="middle">partners, other engines,</text><text class="m" x="125" y="148" text-anchor="middle">databases, SaaS, buckets,</text><text class="m" x="125" y="166" text-anchor="middle">event streams</text>
<rect class="ca" x="660" y="75" width="230" height="120" rx="6"/><text class="b" x="775" y="108" text-anchor="middle">APPS AND OPERATIONAL</text><text class="m" x="775" y="130" text-anchor="middle">dashboards, services,</text><text class="m" x="775" y="148" text-anchor="middle">databases that need</text><text class="m" x="775" y="166" text-anchor="middle">the data</text>
<path class="lg" d="M330 100L240 100" marker-end="url(#arg)"/><text class="m" x="285" y="92" text-anchor="middle">Part A</text>
<path class="ln" d="M240 160L330 160" marker-end="url(#ar)"/><text class="m" x="285" y="182" text-anchor="middle">Part B</text>
<path class="lg" d="M570 135L660 135" marker-end="url(#arg)"/><text class="m" x="615" y="127" text-anchor="middle">Part A</text>
</svg></div>
<figcaption>Part A is data going out of Databricks, to others and to apps. Part B is data coming in.</figcaption></figure>
</section>
''')
    n += 1
    ids = {}
    out.append(f'<section id="s{n}"><p class="eyebrow">{PA}</p><h2>Part A: others read data Databricks owns, at a glance</h2>@@MAPA@@</section>\n')
    mapa_id = n
    n += 1
    # A1, A2, A3 (clean room), A4 ...
    for i, m in enumerate(A):
        label = m["title"].split(".")[0]
        if label == "A4":
            ids["A3"] = n
            out.append(CLEAN_ROOM.format(id=n))
            n += 1
        ids[label] = n
        figure = fig(m["nodes"], m["arrows"], m["steps"], m["title"] + ": how it works", m.get("cap", ""))
        out.append(method(n, PA, m["title"], m["intro"], figure, m["hood"], m["use"], m["avoid"], m.get("extra", ""), COSTSEC[label]))
        n += 1
    out.append(f'<section id="s{n}"><p class="eyebrow">{PB}</p><h2>Part B: Databricks reads data others own, at a glance</h2>@@MAPB@@</section>\n')
    mapb_id = n
    n += 1
    for m in B:
        label = m["title"].split(".")[0]
        ids[label] = n
        figure = fig(m["nodes"], m["arrows"], m["steps"], m["title"] + ": how it works", m.get("cap", ""))
        out.append(method(n, PB, m["title"], m["intro"], figure, m["hood"], m["use"], m["avoid"], m.get("extra", ""), COSTSEC[label]))
        n += 1
    out.append(AWS.format(id=n))
    n += 1
    out.append(COST.format(id=n))
    html = "".join(out)
    html = html.replace("@@MAPA@@", MAP_A.format(**ids)).replace("@@MAPB@@", MAP_B.format(**ids))
    OUT.write_text(html)
    return html


if __name__ == "__main__":
    h = build()
    print("wrote", OUT, len(h), "bytes")
