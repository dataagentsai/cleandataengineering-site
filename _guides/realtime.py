"""Real-time analytics: a hub and one page per topic under /learn/real-time-analytics/.

    python3 _guides/realtime.py

Teach first, then decide. Hub = the nine roles drawn left to right and a map of the pages.
Pages: basics (real time vs streaming vs near real time), Lambda vs Kappa, the components
left to right, change capture by source database, routes (direct to ClickHouse, BI, big-data
platform, is Kafka needed), eight abstract designs, physical designs per cloud, contracts and
bindings, push to the screen, cost, and which technologies are established.
Prices are rough list prices; the cost page says so.
"""
import json
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "_paths"))
import components as C  # noqa: E402  (page CSS, table(), faq())
from diagrams import FILL, arrow, box, svg, text  # noqa: E402

wb = C.wb
SITE = wb.SITE
BASE = "/learn/real-time-analytics/"
DATE = "2026-11-02"
table, faq = C.table, C.faq

CSS = C.CSS + """<style>
  .diagram a:hover rect { stroke-width:2.6 } .diagram a { cursor:pointer }
  .map { display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); gap:12px; margin:14px 0; }
  .map a { display:block; border:var(--line); border-radius:var(--wob); padding:12px 16px; text-decoration:none; color:var(--ink); background:#fff; }
  .map a:hover { background:var(--butter-wash); } .map b { font-family:var(--hand); font-weight:400; font-size:21px; display:block; } .map span { font-size:14px; color:var(--muted); }
  .map .n { font-size:12px; color:var(--faint); letter-spacing:.06em; text-transform:uppercase; }
  .design { border:var(--line); border-radius:var(--wob); padding:14px 18px; margin:16px 0; background:#fff; }
  .design h3 { margin:0 0 4px; font-size:25px; } .design .one { color:var(--ink-soft); margin:0 0 8px; }
  .pill { display:inline-block; font-size:12.5px; border:1.5px solid var(--ink); border-radius:999px; padding:1px 10px; margin-right:6px; background:var(--mint-wash); }
  .pill.drop { background:var(--rose-wash); } .pill.maybe { background:var(--butter-wash); }
  .warn { border:var(--line); border-radius:var(--wob); padding:10px 16px; background:var(--butter-wash); font-size:15px; }
</style>"""

# slug, short label, page title, one line for the map
PAGES = [
    ("basics", "Real time, explained", "Real time vs streaming vs near real time", "Three words people mix up, and the one question that decides which you need."),
    ("lambda-vs-kappa", "Lambda vs Kappa", "Lambda vs Kappa, drawn simply", "Two paths or one log. Why new builds pick Kappa."),
    ("components", "Components, left to right", "The components, left to right", "From the transaction system to the screen: every box, who runs it, and the products."),
    ("change-capture", "Change capture tools", "Change capture: who turns database changes into events", "Debezium, Qlik Replicate, GoldenGate and the rest, by source database."),
    ("routes", "Which route?", "Which route: straight to ClickHouse, straight to BI, or through a platform", "When you need Kafka, and when one tool from database to target is enough."),
    ("architectures", "Eight designs", "Eight real-time designs, without product names", "The same nine roles, combined eight ways. Which to pick, and which to drop."),
    ("physical", "Designs on each cloud", "The eight designs on Azure, AWS, Google Cloud and open source", "Which product plays each role, design by design."),
    ("contracts", "Contracts and bindings", "Contracts and bindings at every hop", "Producer, topic, consumer, repeated. The same spec at every hop."),
    ("push-to-ui", "Push to the screen", "Push to the screen: snapshot first, then small changes", "SSE or WebSocket, where the changes come from, and what BI tools cannot do."),
    ("cost", "What it costs", "What real-time analytics costs", "Rough monthly bills for small stacks, and the five things that drive the bill."),
    ("technologies", "Established technologies", "Which real-time technologies are established", "Safe choices, growing ones, and ones to drop, layer by layer."),
]
SHORT = {s: sh for s, sh, _, _ in PAGES}
TITLE = {s: t for s, _, t, _ in PAGES}

ROLES = [  # id, name, sub, fill
    ("R1", "Source", "the app and\nits database", "grey"),
    ("R2", "Capture", "turns changes\ninto events", "rose"),
    ("R3", "Event log", "keeps events,\nallows replay", "butter"),
    ("R4", "Process", "clean, join,\ncount windows", "lilac"),
    ("R5", "Serve", "fast answers,\nmany users", "mint"),
    ("R6", "History", "cheap, full\nhistory", "silver"),
    ("R7", "API", "metrics,\nsecurity", "peri"),
    ("R8", "Push", "sends changes\nto screens", "sky"),
    ("R9", "Screen", "dashboard\nor app", "white"),
]


def fig(s, cap):
    return f'<figure class="diagram">{s}<figcaption>{cap}</figcaption></figure>'


def siblings(cur):
    return '<div class="sib"><a href="' + BASE + '">↑ All of real-time analytics</a>' + "".join(
        f'<span>{SHORT[s]}</span>' if s == cur else f'<a href="{BASE}{s}/">{SHORT[s]}</a>' for s, *_ in PAGES) + "</div>"


def link(slug, label=None):
    return f'<a href="{BASE}{slug}/">{E(label or SHORT[slug])}</a>'


# ------------------------------------------------------------------ drawings
def roles_drawing():
    main = [r for r in ROLES if r[0] != "R6"]
    b, x = "", 10
    for i, (rid, n, sub, f) in enumerate(main):
        b += box(x, 20, 128, 92, n, sub, f)
        if i < len(main) - 1:
            b += arrow(x + 130, 66, x + 144, 66)
        x += 146
    # history hangs under the event log and process
    b += box(302, 168, 274, 62, "History (lakehouse)", "cheap, full history; also the replay source", "silver")
    b += arrow(370, 114, 370, 166) + arrow(512, 114, 512, 166)
    b += text(590, 262, "data moves left to right; the history store sits underneath, fed by the log", 15)
    return svg(1180, 276, b, "The nine roles of real-time analytics: source, capture, event log, process, serve, API, push and screen, with a history store under the log.")


def ladder():
    items = [("Hard real time", "microseconds,\nguaranteed", "rose"), ("Real time", "under\n1 second", "butter"),
             ("Near real time", "5 seconds to\n15 minutes", "mint"), ("Batch", "hours to\na day", "peri")]
    b, x = "", 10
    for i, (t, s, f) in enumerate(items):
        h = 70 + i * 22
        b += box(x, 150 - h, 210, h, t, s, f)
        x += 240
    b += arrow(20, 180, 930, 180, "")
    b += text(475, 205, "slower answers, but simpler and cheaper", 15)
    b += text(125, 228, "machines, not analytics", 13) + text(365, 228, "fraud, bidding, live ops", 13) + text(605, 228, "dashboards people watch", 13) + text(845, 228, "reports, planning", 13)
    return svg(960, 240, b, "Four tiers of freshness: hard real time, real time under a second, near real time from seconds to minutes, and batch.")


def lambda_kappa():
    b = text(250, 22, "Lambda: two paths, logic written twice", 17, fill="#1F1F1F")
    b += box(10, 90, 110, 60, "Source", "", "grey") + arrow(122, 120, 150, 120)
    b += box(152, 90, 110, 60, "Log", "", "butter")
    b += arrow(264, 110, 300, 70) + arrow(264, 130, 300, 170)
    b += box(302, 40, 150, 56, "Batch path", "correct, slow", "peri") + box(302, 146, 150, 56, "Speed path", "fresh, rough", "rose")
    b += arrow(454, 70, 490, 110) + arrow(454, 172, 490, 130)
    b += box(492, 90, 110, 60, "Merge", "", "mint")
    b += text(800, 22, "Kappa: one log, one path, replay to fix", 17, fill="#1F1F1F")
    b += box(640, 90, 100, 60, "Source", "", "grey") + arrow(742, 120, 770, 120)
    b += box(772, 90, 100, 60, "Log", "", "butter") + arrow(874, 120, 902, 120)
    b += box(904, 90, 110, 60, "Process", "written once", "lilac") + arrow(1016, 120, 1044, 120)
    b += box(1046, 90, 104, 60, "Serve", "", "mint")
    b += box(904, 186, 110, 46, "History", "", "silver") + arrow(959, 152, 959, 184)
    b += '<path d="M822,152 C822,215 870,215 900,205" fill="none" stroke="#1F1F1F" stroke-width="1.4" stroke-dasharray="5 4" marker-end="url(#ah)"/>'
    b += text(800, 250, "replay the log through new code", 13)
    return svg(1160, 262, b, "Lambda has a batch path and a speed path merged at the end. Kappa has one log, one processing path, and replays the log to fix logic.")


def pipeline():
    r1 = [("Transaction app", "orders, payments", "grey"), ("Database", "writes a change\nlog", "grey"), ("Change capture", "CDC or outbox", "rose"),
          ("Event log", "Kafka, Event\nHubs, Kinesis", "butter"), ("Stream process", "optional: clean,\njoin, windows", "lilac"), ("Curated topics", "back into\nthe log", "butter")]
    r2 = [("Serving store", "ClickHouse,\nPinot, Druid", "mint"), ("API", "metrics,\nsecurity", "peri"),
          ("Push gateway", "SSE or\nWebSocket", "sky"), ("Screen", "snapshot, then\nchanges", "white")]
    b, x = "", 10
    for i, (t, s, f) in enumerate(r1):
        b += box(x, 20, 170, 84, f"{i + 1}. {t}", s, f)
        if i < len(r1) - 1:
            b += arrow(x + 172, 62, x + 190, 62)
        x += 192
    b += '<path d="M1040,106 V140 H95 V166" fill="none" stroke="#1F1F1F" stroke-width="1.6" marker-end="url(#ah)"/>'
    x = 10
    for i, (t, s, f) in enumerate(r2):
        b += box(x, 170, 170, 84, f"{i + 7}. {t}", s, f)
        if i < len(r2) - 1:
            b += arrow(x + 172, 212, x + 190, 212)
        x += 192
    b += box(970, 170, 170, 84, "11. History", "Iceberg or\nDelta", "silver") + arrow(1090, 106, 1090, 168)
    b += text(585, 282, "the serving store and the history store both read the curated topics", 14)
    return svg(1170, 296, b, "Eleven components: transaction app, database, change capture, event log, stream processing, curated topics, then serving store, API, push gateway and screen, with a history store beside them.")


def cdc_drawing():
    b = '<rect x="10" y="40" width="190" height="130" rx="14" fill="#F3F3F1" stroke="#1F1F1F" stroke-width="1.6"/>'
    b += text(105, 70, "Database", 19, fill="#1F1F1F")
    b += box(30, 90, 150, 60, "its change log", "WAL, binlog, redo", "white")
    b += arrow(202, 105, 270, 105, "reads the log")
    b += box(272, 65, 190, 80, "CDC tool", "Debezium, Qlik,\nGoldenGate …", "rose")
    b += arrow(464, 90, 560, 40) + arrow(464, 105, 560, 105) + arrow(464, 120, 560, 172)
    b += box(562, 14, 230, 54, "Event log (Kafka)", "many consumers", "butter")
    b += box(562, 80, 230, 54, "Serving store directly", "e.g. ClickHouse", "mint")
    b += box(562, 146, 230, 54, "Lakehouse directly", "Delta, Iceberg", "silver")
    b += text(400, 228, "the app is untouched: the tool reads what the database already writes", 15)
    return svg(810, 240, b, "A CDC tool reads the database's own change log and writes events to Kafka, straight to a serving store, or straight to a lakehouse.")


def routes_drawing():
    lanes = [("A", [("Source", "grey"), ("Read replica", "grey"), ("BI tool", "white")]),
             ("B", [("Source", "grey"), ("CDC tool", "rose"), ("ClickHouse", "mint"), ("Screen", "white")]),
             ("C", [("Source", "grey"), ("CDC", "rose"), ("Kafka", "butter"), ("Flink", "lilac"), ("Store + lake", "mint"), ("Screen", "white")]),
             ("D", [("Source", "grey"), ("CDC tool", "rose"), ("Lakehouse", "silver"), ("Power BI", "white")])]
    b = ""
    for i, (k, items) in enumerate(lanes):
        y = 14 + i * 74
        b += f'<circle cx="26" cy="{y + 25}" r="16" fill="#fff" stroke="#1F1F1F" stroke-width="1.5"/>' + text(26, y + 31, k, 17, fill="#1F1F1F")
        x = 56
        for j, (t, f) in enumerate(items):
            b += box(x, y, 132, 50, t, "", f)
            if j < len(items) - 1:
                b += arrow(x + 134, y + 25, x + 150, y + 25)
            x += 152
    return svg(980, 310, b, "Four routes: A, BI reads a replica; B, CDC straight into ClickHouse; C, through Kafka and Flink; D, CDC into a lakehouse and Power BI.")


def strip(present, optional=()):
    """Nine role boxes; roles in `present` are drawn strong, `optional` dashed, others faded."""
    b, x = "", 6
    for rid, n, _, f in ROLES:
        if rid in present:
            b += f'<rect x="{x}" y="8" width="108" height="54" rx="12" fill="{FILL[f]}" stroke="#1F1F1F" stroke-width="2.4"/>' + text(x + 54, 43, n, 21, fill="#1F1F1F")
        elif rid in optional:
            b += f'<rect x="{x}" y="8" width="108" height="54" rx="12" fill="#fff" stroke="#1F1F1F" stroke-width="1.4" stroke-dasharray="5 4"/>' + text(x + 54, 43, n + " ?", 19, fill="#555")
        else:
            b += f'<rect x="{x}" y="8" width="108" height="54" rx="12" fill="#fff" stroke="#C8C8C8" stroke-width="1"/>' + text(x + 54, 43, n, 18, fill="#B0B0B0")
        x += 116
    return svg(1050, 70, b, "Roles used: " + ", ".join(n for rid, n, *_ in ROLES if rid in present))


def hops():
    b = box(10, 40, 130, 70, "Producer", "CDC or app", "rose") + arrow(142, 75, 176, 75)
    b += box(178, 30, 190, 90, "Topic 1", "contract + binding", "butter") + arrow(370, 75, 404, 75)
    b += box(406, 30, 190, 90, "Processor", "consumes 1,\nproduces 2", "lilac") + arrow(598, 75, 632, 75)
    b += box(634, 30, 190, 90, "Topic 2", "contract + binding", "butter") + arrow(826, 75, 860, 75)
    b += box(862, 40, 130, 70, "Consumer", "store, push", "mint")
    b += text(273, 150, "contract: schema, key,", 13) + text(273, 167, "meaning, compatibility", 13)
    b += text(729, 150, "binding: Kafka topic,", 13) + text(729, 167, "partitions, guarantees", 13)
    b += text(500, 200, "the same three-part spec repeats at every hop", 15)
    return svg(1000, 212, b, "Producer, topic, processor, topic, consumer. Each topic carries a contract and a binding.")


def push_drawing():
    b = box(10, 50, 170, 80, "Results topic", "or streaming DB\nsubscription", "butter") + arrow(182, 90, 236, 90)
    b += box(238, 50, 170, 80, "Push gateway", "keeps who sees\nwhat", "sky")
    b += arrow(410, 70, 560, 50, "1. snapshot on connect") + arrow(410, 110, 560, 130, "2. small changes")
    b += box(562, 20, 190, 140, "Browser", "", "white")
    b += '<rect x="584" y="76" width="64" height="60" rx="8" fill="#F0F8F3" stroke="#1F1F1F" stroke-width="1.2"/><rect x="660" y="96" width="70" height="40" rx="8" fill="#FFF8E8" stroke="#1F1F1F" stroke-width="1.2"/>'
    b += text(380, 196, "throttle: at most one update a second per widget; never forward raw events", 14)
    return svg(770, 208, b, "A push gateway reads a results topic, sends a snapshot when the browser connects, then only small changes.")


def cost_drawing():
    items = [("Near real time", "$0.5–2k", 60, "mint"), ("Azure-native", "$1–2.5k", 90, "peri"), ("Managed best", "$2–6k", 130, "butter"), ("Enterprise", "$20k+", 190, "rose")]
    b, x = "", 20
    for t, c, h, f in items:
        b += f'<rect x="{x}" y="{220 - h}" width="150" height="{h}" rx="12" fill="{FILL[f]}" stroke="#1F1F1F" stroke-width="1.6"/>'
        b += text(x + 75, 210 - h, c + " / month", 15, fill="#1F1F1F") + text(x + 75, 244, t, 16, fill="#1F1F1F")
        x += 190
    b += '<line x1="10" y1="220" x2="780" y2="220" stroke="#1F1F1F" stroke-width="1.6"/>'
    return svg(790, 256, b, "Rough monthly cost: near real time $0.5–2k, Azure-native real time $1–2.5k, managed best-of-breed $2–6k, enterprise scale $20k and up.")


def tech_drawing():
    cols = [("Established", "mint", ["Kafka, Event Hubs", "Debezium", "Flink, Spark", "ClickHouse, Pinot, Druid", "WebSocket, SSE"]),
            ("Growing", "butter", ["Redpanda", "Kafka on object storage", "RisingWave, Materialize", "AsyncAPI, ODCS", "Fabric Real-Time"]),
            ("Drop", "rose", ["Storm, Samza", "Spark DStreams", "ksqlDB", "Lambda serving layers", "long-polling"])]
    b, x = "", 10
    for t, f, items in cols:
        b += f'<rect x="{x}" y="10" width="290" height="230" rx="16" fill="{FILL[f]}" stroke="#1F1F1F" stroke-width="1.6"/>' + text(x + 145, 42, t, 20, fill="#1F1F1F")
        for i, it in enumerate(items):
            b += text(x + 145, 82 + i * 34, it, 15)
        x += 310
    return svg(930, 250, b, "Established: Kafka, Debezium, Flink, ClickHouse, WebSocket. Growing: Redpanda, object-storage Kafka, streaming databases. Drop: Storm, DStreams, ksqlDB.")


# ------------------------------------------------------------------ pages
def basics():
    body = f"""<section id="plain"><p class="eyebrow">In plain words</p><h2>The result vs the way of moving data</h2>
<p><b>Streaming</b> is a way of moving and processing data: one event at a time, all the time. <b>Real-time analytics</b> is a result: questions about very fresh data, answered in under a second, for many people at once. Streaming is usually how the data gets there, but you also need a store built for fast questions and a screen that receives updates.</p>
<p>You can have either without the other. A stream that feeds a report printed every night is still streaming. And you can send raw events straight into a fast analytics database, such as ClickHouse, with no stream-processing engine at all, and still get real-time answers.</p>
{table(["", "Streaming", "Real-time analytics"], [("What it is", "A way of moving data, event by event, continuously", "A result: fresh answers in under a second, for many users"), ("Question it answers", "How does data move?", "How fresh and how fast are the answers?"), ("Can it exist alone?", "Yes: streaming into a nightly report", "Yes: raw events straight into ClickHouse, no processing engine")])}</section>

<section id="tiers"><p class="eyebrow">Freshness</p><h2>Real time and near real time are different</h2>
{fig(ladder(), "Four tiers. Each step to the right is slower, but simpler and cheaper.")}
{table(["Tier", "Delay, end to end", "Who acts on it", "Examples", "Typical design"], [
        ("Hard real time", "Microseconds to milliseconds, guaranteed", "Machines", "Factory control, car brakes, high-frequency trading", "Embedded systems and special hardware. Not Kafka or analytics platforms; out of scope here."),
        ("Real time", "Under about 1 second", "Machines, or a person who must react right now", "Blocking a fraudulent payment, ad bidding, a live operations room", "Event log, stream processor, fast analytics store, push to the screen"),
        ("Near real time", "About 5 seconds to 15 minutes", "People watching dashboards", "Today's sales, stock levels, call-centre boards", "Small batches into a warehouse or lakehouse; the dashboard refreshes every 30 to 60 seconds"),
        ("Batch", "Hours to a day", "People planning", "Finance reports, monthly cost reports", "A nightly job")])}</section>

<section id="test"><p class="eyebrow">The one question</p><h2>Who acts, and how fast can they act?</h2>
<p>Ask what decision changes, who makes it, and how quickly they can act on it. A person watching a dashboard cannot act on a change that is half a second old, so near real time is almost always enough for people. A program that blocks a payment can act in milliseconds, so it needs real time.</p>
<p>Most requests for a "real-time dashboard" turn out to be near real time once you ask this question. That matters, because real time usually costs <b>three to ten times</b> as much as the batch version of the same report (see {link("cost", "what it costs")}).</p>
<p class="warn"><b>The cost line:</b> near real time stays cheap only while compute can switch off between batches. Below about a five-minute interval, warehouse compute never gets to pause, so you pay for always-on compute and still have a batch design. At that point a proper streaming design is often cheaper.</p></section>"""
    qa = [("Is real-time analytics the same as streaming?", "No. Streaming is a way of moving data, event by event. Real-time analytics is the result: fresh answers in under a second for many users. Streaming is usually the transport, but you also need a fast analytics store and a screen that receives updates."),
          ("What is the difference between real time and near real time?", "Real time is under about one second end to end and is needed when a machine acts on the data. Near real time is seconds to about fifteen minutes and is enough when people watch a dashboard. Near real time is usually much cheaper."),
          ("Is Kafka real time?", "Kafka itself moves events in milliseconds, but it is soft real time: fast on average, with no guaranteed deadline. Hard real-time systems, such as brakes, use special hardware, not Kafka.")]
    return "basics", "Real-time analytics is a result; streaming is one way to move data. Real time (under a second) and near real time (seconds to minutes) need different designs and budgets.", body, qa


def lambda_vs_kappa():
    body = f"""<section id="plain"><p class="eyebrow">In plain words</p><h2>Two paths or one</h2>
<p><b>Lambda</b> runs two paths side by side. A batch path recomputes correct history slowly, a speed path gives fresh but rough numbers, and a serving layer merges the two. <b>Kappa</b> keeps one path. Every change is an event in a log you can replay; to fix the logic, you replay the log through the new code.</p>
{fig(lambda_kappa(), "Lambda writes the logic twice. Kappa writes it once and replays the log when the logic changes.")}</section>

<section id="compare"><p class="eyebrow">Side by side</p><h2>How they compare</h2>
{table(["", "Lambda", "Kappa"], [
        ("Idea", "A batch path for correct history, a speed path for fresh numbers, merged at the end", "One path. Everything is an event in a replayable log."),
        ("Code", "The same logic written twice, and the two copies drift apart", "Logic written once"),
        ("Fixing history", "The batch job recomputes it", "Replay from the log, or from lakehouse tables when the log keeps only a few days"),
        ("When it fits", "An older setup where the batch path already exists and must stay", "Almost every new build"),
        ("Verdict", "Drop, unless you inherit it", "Pursue")])}</section>

<section id="modern"><p class="eyebrow">Today</p><h2>Kappa with a lakehouse underneath</h2>
<p>Modern Kappa also writes the same events to a lakehouse, as Iceberg or Delta tables. That gives you cheap history and a second place to replay from when the log only keeps a few days. The lakehouse is a second <i>destination</i>, not a second <i>logic path</i>, so the design is still Kappa.</p>
<p>A data platform built on the medallion layers can do the same thing: run the same layers at two speeds, with hot tables flowing continuously. See the <a href="/learn/data-platform-architecture/#streaming">streaming lane</a> of the data platform guide.</p></section>"""
    qa = [("What is the difference between Lambda and Kappa architecture?", "Lambda runs a batch path and a speed path and merges them, so the logic is written twice. Kappa sends everything through one replayable log and one processing path, and fixes history by replaying the log."),
          ("Is Lambda architecture dead?", "For new builds, mostly yes. It survives where a batch path already exists and must stay. New designs use Kappa, usually with a lakehouse for cheap history."),
          ("How does Kappa reprocess history if Kafka only keeps 7 days?", "It replays from the lakehouse copy (Iceberg or Delta), which keeps everything cheaply, or from Kafka's tiered storage if you keep a longer log.")]
    return "lambda-vs-kappa", "Lambda runs a batch path and a speed path and merges them; Kappa uses one replayable log. New builds pick Kappa with a lakehouse for history.", body, qa


def components():
    body = f"""<section id="picture"><p class="eyebrow">The whole line</p><h2>Eleven components, from the transaction to the screen</h2>
{fig(pipeline(), "Read the top row left to right, then the bottom row. Stream processing (5) is optional; history (11) sits beside the live path.")}</section>

<section id="table"><p class="eyebrow">Each box</p><h2>What each one does, and the products</h2>
{table(["#", "Component", "What it does", "Options", "On Azure"], [
        ("1", "Transaction system", "The business app: orders, payments, point of sale, bookings", "Your services", "App Service, AKS"),
        ("2", "Transaction database", "Stores the truth and records every change in its own log", "Postgres (WAL), MySQL (binlog), Oracle (redo log), SQL Server (transaction log), MongoDB (oplog)", "Azure SQL, Cosmos DB change feed, Azure Database for PostgreSQL"),
        ("3", "Change capture", "Turns a change into an event", "Log-based CDC (Debezium and others), outbox pattern, SDKs, IoT bridges", "Debezium, Fabric Eventstream CDC connectors"),
        ("4", "Event log", "Keeps events durably, in order per key, and lets consumers replay", "Kafka, Redpanda, Pulsar, Kinesis, Google Pub/Sub, plus a schema registry", "Event Hubs (speaks the Kafka protocol), Fabric Eventstream"),
        ("5", "Stream processing (optional)", "Cleans, removes duplicates, joins reference data, counts per time window, handles late events", "Flink, Kafka Streams, Spark Structured Streaming, RisingWave, Materialize", "Stream Analytics, Databricks, Fabric Eventstream"),
        ("6", "Curated topics", "Processed output goes back into the log as new topics, each with its own contract", "Same log as 4", "Event Hubs"),
        ("7", "Serving store", "Answers analytical questions fast, for many users", "ClickHouse, Pinot, Druid, StarRocks; Redis for single-key lookups; OpenSearch for search", "Fabric Eventhouse, Azure Data Explorer, Cosmos DB"),
        ("8", "Query / API layer", "One definition per metric, security, caching", "Cube, or your own REST or GraphQL service", "API Management plus your API"),
        ("9", "Push gateway", "Sends changes to browsers", "Server-Sent Events, WebSocket, GraphQL subscriptions; Socket.IO, Ably, Pusher", "Azure SignalR, Web PubSub, Fabric Activator"),
        ("10", "Screen", "Shows a snapshot, then applies small changes as they arrive", "React with a live-data client, or a BI tool", "Fabric Real-Time Dashboard, Power BI"),
        ("11", "History store", "Cheap long-term copy, and the replay source", "Iceberg or Delta tables", "ADLS with Delta, OneLake")])}</section>

<section id="sources"><p class="eyebrow">Step 3, closer</p><h2>Who can create an event?</h2>
{table(["Source", "How it works", "Watch out for", "Verdict"], [
        ("Log-based CDC", "A tool reads the database's own change log and emits each row change, with before and after values", "Events describe table rows, not business meaning", "Pursue as the default for databases"),
        ("Outbox pattern", "In the same transaction, the app writes a business event (OrderPlaced) to an outbox table; CDC ships it", "Needs one small change in the app", "Pursue for business events"),
        ("App writes to Kafka directly", "The app writes to its database and to Kafka separately", "If one write fails, the two disagree (the dual-write problem)", "Drop, unless the data never touches a database"),
        ("Clickstream SDK", "A script in the browser or app sends user actions", "Ad blockers, consent rules", "Pursue for user behaviour"),
        ("IoT and devices", "Devices publish over MQTT; a bridge writes to the log", "Bursty, out-of-order arrivals", "Pursue where relevant"),
        ("Logs and metrics", "Agents such as Fluent Bit, Vector or the OpenTelemetry Collector ship them", "Volume", "Pursue for operational analytics"),
        ("SaaS webhooks", "An HTTP endpoint receives the call and writes it to the log", "Retries send duplicates", "Pursue"),
        ("Files dropped in batches", "A file-arrival trigger turns each file into events", "It is batch underneath", "Use only as a bridge")])}
<p>The tools that do log-based CDC, by source database, are on their own page: {link("change-capture", "change capture tools")}.</p></section>

<section id="queue"><p class="eyebrow">Step 4, closer</p><h2>A queue is not a log</h2>
<p>RabbitMQ and SQS are <b>queues</b>: a message disappears once it has been read, so nothing can replay it. Kafka, Event Hubs, Kinesis and Pulsar are <b>logs</b>: they keep events for a set time, and any number of consumers can read, and re-read, at their own pace. Kappa needs a log.</p></section>

<section id="receivers"><p class="eyebrow">Step 5, closer</p><h2>Three kinds of receiver</h2>
<ol><li><b>A stream processor</b> (Flink and similar) reads raw topics, transforms them and writes curated topics.</li>
<li><b>A sink connector</b> (Kafka Connect, ClickPipes, Pinot's real-time ingestion) copies a topic as it is into a store.</li>
<li><b>A lakehouse writer</b> (Flink, Spark, or Confluent Tableflow) writes Iceberg or Delta tables.</li></ol>
<p>The processor's output is another topic with its own contract, so the same pattern repeats: producer, topic, consumer. See {link("contracts", "contracts and bindings")}.</p></section>"""
    qa = [("What are the components of a real-time analytics architecture?", "A transaction system and database, change capture, an event log such as Kafka, optional stream processing, curated topics, a fast serving store such as ClickHouse, a lakehouse for history, an API layer, a push gateway and the screen."),
          ("Who creates the events in a streaming pipeline?", "Usually a change data capture tool that reads the database's change log, or the app itself through the outbox pattern. Browser SDKs, IoT devices, log shippers and webhooks create events too."),
          ("Can I use RabbitMQ or SQS instead of Kafka?", "Not for analytics that need replay. Queues delete a message once it is read; Kafka-style logs keep events so any consumer can re-read them.")]
    return "components", "Every component of a real-time analytics pipeline, from the transaction database through change capture, Kafka, stream processing and ClickHouse to push on the screen.", body, qa


def change_capture():
    body = f"""<section id="plain"><p class="eyebrow">In plain words</p><h2>Read what the database already writes</h2>
<p>Every database keeps a log of its own changes, so it can recover after a crash. A change data capture (CDC) tool reads that log and turns each change into an event. The app does not change, and the database does very little extra work.</p>
{fig(cdc_drawing(), "One CDC tool can feed an event log, or write straight to a serving store or a lakehouse.")}</section>

<section id="tools"><p class="eyebrow">The tools</p><h2>Who does change capture</h2>
{table(["Tool", "Type", "Strongest sources", "Writes to", "Verdict"], [
        ("Debezium", "Open source", "Postgres, MySQL, MariaDB, SQL Server, MongoDB, Oracle, Db2, Cassandra, Vitess, Spanner, Informix", "Kafka through Kafka Connect; Debezium Server writes to Kinesis, Pub/Sub, Event Hubs, Redis and more", "Pursue: the open-source default; you run it"),
        ("Qlik Replicate (formerly Attunity)", "Commercial", "Very broad: Oracle, SQL Server, Db2 including mainframe, IMS, VSAM, SAP, Postgres, MySQL", "Kafka, Event Hubs, Snowflake, Databricks, Fabric, ADLS, S3 and more", "Pursue for many mixed or older sources; little code"),
        ("Oracle GoldenGate", "Commercial", "Oracle first; also SQL Server, Db2, MySQL, Postgres", "Kafka, big-data targets, databases", "Pursue for heavy Oracle; expensive"),
        ("Fivetran (with HVR)", "Commercial service", "Many databases and SAP; HVR for high-volume Oracle and SAP", "Warehouses and lakehouses, mostly directly", "Pursue for near real time with no operations work"),
        ("Striim", "Commercial", "Oracle, SQL Server, Postgres, MySQL", "Kafka, clouds, warehouses; reshapes data on the way", "Pursue when you want capture and light processing in one"),
        ("IBM Data Replication (IIDR)", "Commercial", "Db2 for z/OS, IBM i, IMS", "Kafka, databases", "Pursue for IBM mainframe and IBM i"),
        ("Precisely Connect, tcVISION", "Commercial", "Mainframe (VSAM, IMS, Db2), IBM i", "Kafka, cloud", "Alternatives for mainframe"),
        ("AWS DMS", "Cloud service", "Oracle, SQL Server, Postgres, MySQL, Db2, MongoDB", "Kinesis, MSK, S3, Redshift", "Pursue inside AWS; simpler than the others"),
        ("Google Datastream", "Cloud service", "Oracle, MySQL, Postgres, SQL Server", "BigQuery, Cloud Storage", "Pursue inside Google Cloud"),
        ("Fabric Mirroring", "Cloud service", "Azure SQL, SQL Server, Cosmos DB, Postgres, Snowflake, Oracle (newer)", "OneLake as Delta tables", "Pursue for near real time on Azure"),
        ("Fabric Eventstream CDC connectors", "Cloud service", "Azure SQL, Postgres, MySQL, Cosmos DB", "Eventstream, Eventhouse", "Pursue for real time on Azure"),
        ("Databricks Lakeflow Connect", "Platform", "SQL Server, Postgres, MySQL, SaaS apps", "Delta tables", "Pursue on Databricks"),
        ("Snowflake Openflow and connectors", "Platform", "Postgres, MySQL, SQL Server", "Snowflake", "Pursue on Snowflake"),
        ("ClickPipes / PeerDB", "Managed by ClickHouse", "Postgres (strongest), MySQL, MongoDB", "ClickHouse directly", "Pursue for Postgres straight into ClickHouse"),
        ("Flink CDC", "Open source", "MySQL, Postgres, Oracle, SQL Server, MongoDB, Db2", "Kafka, StarRocks, Doris, Paimon, Iceberg", "Pursue if Flink is already central"),
        ("Estuary Flow", "Commercial service, open core", "Postgres, MySQL, SQL Server, Oracle, MongoDB", "Kafka-compatible output, ClickHouse, Snowflake, Databricks and more", "Pursue as managed real time for small teams"),
        ("Airbyte (Debezium inside)", "Open source and service", "Postgres, MySQL, SQL Server, MongoDB", "Warehouses", "Minutes, not seconds; drop for real time"),
        ("Confluent managed CDC connectors", "Commercial", "Debezium-based for Postgres, MySQL, SQL Server, MongoDB; Oracle XStream (premium)", "Confluent Kafka", "Pursue on Confluent, so you do not run Connect yourself")])}</section>

<section id="by-source"><p class="eyebrow">By source</p><h2>What each database needs, and the gotcha</h2>
{table(["Source", "What must be switched on", "Best options", "Gotcha"], [
        ("PostgreSQL", "wal_level = logical, a replication slot, a publication", "Debezium, ClickPipes/PeerDB, Estuary, DMS, Datastream, Fabric Mirroring", "If the reader stops, the slot holds the log and the disk fills up. Watch slot lag."),
        ("MySQL, MariaDB", "Binlog in ROW format with full row images; GTID on", "Debezium, DMS, Datastream, Flink CDC, ClickPipes", "Binlog retention must outlast any reader outage."),
        ("SQL Server, Azure SQL", "CDC switched on per database and per table", "Debezium, Qlik, Fivetran, Fabric Mirroring, Lakeflow Connect, Striim", "The change tables add load; small Azure SQL tiers have limits."),
        ("Oracle", "ARCHIVELOG mode and supplemental logging", "GoldenGate, Qlik, Fivetran HVR, Striim, Debezium (LogMiner or OpenLogReplicator)", "Licensing: XStream needs a GoldenGate licence; LogMiner is free but struggles at high volume. Check early."),
        ("Db2 (Linux, Unix, Windows)", "Replication capture switched on", "Debezium, Qlik, IBM IIDR", ""),
        ("Mainframe (Db2 z/OS, IMS, VSAM)", "Log or exit-based capture on the mainframe", "Qlik, IBM IIDR, Precisely, tcVISION", "Mainframe CPU is billed; capture close to the log."),
        ("IBM i (AS/400)", "Journaling", "IBM IIDR, Precisely, Qlik", ""),
        ("SAP (ECC, S/4HANA)", "SLT or ODP extractors", "SAP Datasphere replication flows, SAP SLT, Qlik, Fivetran HVR, Theobald", "SAP licence terms limit reading the log directly; use approved paths."),
        ("MongoDB", "A replica set (change streams)", "Debezium, MongoDB Kafka Connector, Estuary, ClickPipes", "A single node has no change stream."),
        ("Cosmos DB, DynamoDB, Spanner", "The built-in change feed or stream", "The native feed with Functions or Lambda; Fabric Mirroring for Cosmos DB; Debezium for Spanner", "Use the native feed before a third-party tool.")])}</section>"""
    qa = [("What is log-based change data capture?", "A tool reads the change log a database already keeps for crash recovery and turns each insert, update and delete into an event, with no change to the app and little extra load."),
          ("Debezium or Qlik Replicate?", "Debezium is free and open source and covers the common open-source databases, but you run it. Qlik Replicate is commercial, covers mainframes and SAP, and needs little code. Pick Qlik for many mixed or older sources, Debezium otherwise."),
          ("What is the best CDC tool for Oracle?", "GoldenGate is the strongest, then Qlik Replicate, Fivetran HVR and Striim. Debezium works through LogMiner or OpenLogReplicator. Check Oracle licensing early: XStream needs a GoldenGate licence.")]
    return "change-capture", "Change data capture tools by source database: Debezium, Qlik Replicate, GoldenGate, Fivetran, Striim, cloud services, what each database needs, and the gotchas.", body, qa


def routes():
    body = f"""<section id="picture"><p class="eyebrow">Four routes</p><h2>Not every screen needs Kafka</h2>
{fig(routes_drawing(), "Route A reads a replica; B goes straight into ClickHouse; C goes through Kafka; D goes through a lakehouse.")}
{table(["Route", "Use it when", "Avoid when", "Verdict"], [
        ("A. The screen reads the source", "One system, small data (up to tens of millions of rows), few users, simple totals. Always a read replica, never the main database.", "Joins across systems, heavy scans, many users", "Pursue for small operational boards"),
        ("B. Straight into ClickHouse", "One or two sources, ClickHouse is the only consumer, sub-second answers for many users, a small team. Reshaping happens in ClickHouse materialized views.", "Other systems need the same changes; heavy joins while data is moving", "Pursue: the simplest real-time route"),
        ("C. Through Kafka", "Several consumers, replay needed, enrichment or time windows needed, traffic spikes to absorb, many sources", "One source and one target: Kafka only adds cost and work", "Pursue with two or more consumers"),
        ("D. Through a big-data platform", "A few minutes is fine; you need history, joins across many systems, machine learning, governance; the platform already exists", "Under about 5 seconds with many users at once", "Pursue for near real time at scale"),
        ("C and D together", "A live product screen and deep analytics", "A tight budget", "Pursue as the mature end state")])}</section>

<section id="kafka"><p class="eyebrow">Is Kafka mandatory?</p><h2>No. Five reasons to add it</h2>
<p>You need Kafka, or a cloud log such as Event Hubs, Kinesis or Pub/Sub, if <b>any</b> of these is true:</p>
<ol><li>Two or more systems consume the same changes.</li><li>You must be able to replay history through new logic.</li><li>You enrich, join or count per time window while data moves.</li><li>Microservices also react to the events, not only analytics.</li><li>The source must be shielded from slow or failing consumers.</li></ol>
<p>If none is true, use one change capture tool that writes straight to the target: ClickPipes into ClickHouse, Fabric Mirroring into OneLake, Datastream into BigQuery, Qlik Replicate into Snowflake, or Aurora zero-ETL into Redshift.</p></section>

<section id="bi"><p class="eyebrow">Power BI and friends</p><h2>Where BI tools fit</h2>
<ul><li>Power BI does not push sub-second updates. Its best is <b>automatic page refresh</b> over DirectQuery, down to about a second on Fabric or Premium capacity, with change detection.</li>
<li>It works well over Fabric Eventhouse or Azure Data Explorer, over ClickHouse (there is an official connector), and over Databricks SQL. That is near real time to about a second: fine for people.</li>
<li>Power BI real-time streaming datasets are being retired in favour of Fabric Real-Time Intelligence. Do not build on them.</li>
<li>For live operations boards, Grafana over ClickHouse or Azure Data Explorer refreshes every one to five seconds and costs less.</li>
<li>For true push on a customer-facing screen, build your own screen with SSE or WebSocket. See {link("push-to-ui", "push to the screen")}.</li></ul></section>

<section id="picks"><p class="eyebrow">Quick picks</p><h2>Common cases</h2>
{table(["Situation", "Pick"], [
        ("A Postgres app that needs a live analytics screen", "ClickPipes or PeerDB straight into ClickHouse, then SSE to the screen. No Kafka."),
        ("Azure SQL into Power BI, a few minutes is fine", "Fabric Mirroring into OneLake, then Power BI in Direct Lake mode. No Kafka."),
        ("Several databases, several consumers, real time", "Debezium or Qlik into Kafka or Event Hubs, then Flink, then ClickHouse and the lakehouse"),
        ("An Oracle- or mainframe-heavy enterprise", "GoldenGate or Qlik Replicate into Kafka, then the platform"),
        ("A small operations board on one system", "Grafana or Power BI DirectQuery on a read replica")])}</section>"""
    qa = [("Is Kafka mandatory for real-time analytics?", "No. One change capture tool writing straight to ClickHouse, a lakehouse or a warehouse is enough when one source feeds one target. Add Kafka when two or more systems consume the same changes, or when you need replay or processing in flight."),
          ("Can Power BI show real-time data?", "Near real time, yes: automatic page refresh over DirectQuery, down to about a second on Fabric capacity. True push is not possible; streaming datasets are being retired in favour of Fabric Real-Time Intelligence."),
          ("When should data go straight into ClickHouse?", "When one or two sources feed it, ClickHouse is the only consumer, and the reshaping is simple enough for ClickHouse materialized views.")]
    return "routes", "When to go straight to ClickHouse, straight to Power BI, or through a big-data platform, and the five reasons Kafka is worth adding.", body, qa


DESIGNS = [  # key, name, one line, present, optional, delay, cost, effort, verdict, kind, use, avoid
    ("L1", "Direct query", "The BI tool reads a replica of the source database.", {"R1", "R9"}, (), "Seconds (replica lag)", "Lowest", "Low", "Pursue for one system, small data", "",
     "One system, small data, few users", "Joins across systems, many users"),
    ("L2", "Direct capture into the serving store", "A change capture tool writes straight into ClickHouse or similar; reshaping happens inside the store.", {"R1", "R2", "R5", "R9"}, ("R8",), "1 to 5 s", "$500–2k a month", "Low to medium", "Pursue: the simplest real-time design", "",
     "One or two sources, one consumer, sub-second answers", "Other systems need the same changes"),
    ("L3", "Log-centred streaming (Kappa)", "Every change flows through an event log; a processor builds curated topics; a fast store serves; changes are pushed.", {"R1", "R2", "R3", "R4", "R5", "R7", "R8", "R9"}, ("R6",), "Under 1 to 3 s", "$2–6k a month", "High", "Pursue with several consumers", "",
     "Several consumers, replay, enrichment in flight", "One source, one target"),
    ("L4", "Lakehouse, near real time", "Change capture into Databricks, Fabric or Snowflake in small batches; the warehouse serves the dashboard.", {"R1", "R2", "R6", "R9"}, ("R3",), "1 to 15 min", "$0.5–3k a month", "Medium", "Pursue when people are the ones acting", "",
     "A few minutes is fine; history and joins across many systems", "Sub-second answers for many users"),
    ("L5", "Kappa plus lakehouse", "One log feeds a live store and a full history; the mature enterprise design.", {"R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9"}, (), "Under 1 s live, plus full history", "$5k+ a month", "High", "Pursue as the end state", "",
     "Live screens and deep analytics together", "A tight budget or a small team"),
    ("L6", "Streaming database", "One engine keeps query results up to date as data changes, and pushes the changes.", {"R1", "R2", "R5", "R8", "R9"}, ("R3", "R6"), "Under 1 s", "$1–4k a month", "Medium", "Pursue for continuous joins plus push", "maybe",
     "A live screen built on joins that must stay up to date", "You need wide tool support; the products are still maturing"),
    ("L7", "HTAP: one database for both", "The transaction database also answers analytical questions, using a column engine inside it.", {"R1", "R9"}, ("R8",), "Seconds", "Varies", "Low", "Pursue only for one system on a capable database", "maybe",
     "One system whose database has a column engine", "Several sources; analytics would slow the app"),
    ("L8", "Lambda", "A batch path and a speed path, merged in a serving layer.", {"R1", "R2", "R3", "R4", "R5", "R6", "R9"}, (), "Mixed", "High", "Very high", "Drop: legacy", "drop",
     "Only when you inherit it", "Any new build"),
]


def architectures():
    rows = [(k + " " + n, d, c, eff, v) for k, n, _, _, _, d, c, eff, v, *_ in DESIGNS]
    cards = ""
    for k, n, one, pres, opt, d, c, eff, v, kind, use, avoid in DESIGNS:
        cards += (f'<div class="design" id="{k.lower()}"><h3>{k} · {E(n)}</h3><p class="one">{E(one)}</p>'
                  f'<figure class="diagram" style="margin:8px 0">{strip(pres, opt)}<figcaption>Strong boxes are used; dashed boxes are optional; faded boxes are left out.</figcaption></figure>'
                  f'<p><span class="pill {kind}">{E(v)}</span></p><p><b>Use it when:</b> {E(use)}. <b>Avoid when:</b> {E(avoid)}. '
                  f'<a href="{BASE}physical/#{k.lower()}">Products for {k}</a></p></div>')
    roles = table(["#", "Role", "What it does"], [(r, n, s.replace("\n", " ")) for r, n, s, _ in ROLES])
    body = f"""<section id="roles"><p class="eyebrow">The building blocks</p><h2>Nine roles, no product names</h2>
<p>Every design on this page uses the same nine roles. A design is just a choice of which roles to use. Products come later, on the {link("physical", "physical designs")} page.</p>{roles}</section>

<section id="summary"><p class="eyebrow">At a glance</p><h2>Eight designs</h2>
{table(["Design", "Typical delay", "Small monthly cost", "Running effort", "Verdict"], rows)}
<p>Designs L1, L2, L6 and L7 <b>skip the log</b>; they are fine when one source feeds one consumer. L3 and L5 put <b>the log at the centre</b>, which you need once there are several consumers or a need to replay. L4 gives up speed for history and breadth. Costs are rough; see {link("cost", "what it costs")}.</p></section>

<section id="designs"><p class="eyebrow">Each design</p><h2>The eight, one by one</h2>{cards}</section>

<section id="choose"><p class="eyebrow">Choosing</p><h2>Which one?</h2>
{table(["If", "Then"], [("One system, small data, few users", "L1"), ("One or two sources, sub-second answers, only one consumer", "L2"),
                        ("A few minutes is fine; history and joins across many systems", "L4"), ("Several consumers, replay, enrichment in flight", "L3"),
                        ("All of that, plus live screens and deep analytics", "L5, usually reached by growing from L2 or L4"), ("A live screen built on joins that stay up to date, with push", "L6")])}
<p>A sensible path is to start with L2 or L4 and add the log when a second consumer appears. If each role sits behind its own interface, with a contract per topic and the product named only in a binding, moving between designs means swapping products, not rewriting. See {link("contracts", "contracts and bindings")}.</p></section>"""
    qa = [("What are the main real-time analytics architectures?", "Direct query on a replica, direct capture into a serving store, log-centred streaming (Kappa), lakehouse near real time, Kappa plus lakehouse, a streaming database, HTAP, and the older Lambda."),
          ("Which real-time architecture should I start with?", "Usually direct capture into a serving store such as ClickHouse (real time) or a lakehouse with small batches (near real time). Add an event log such as Kafka when a second consumer appears."),
          ("What is HTAP?", "Hybrid transactional and analytical processing: one database handles both the app's transactions and analytical queries, using a column engine inside it. Examples: SingleStore, TiDB, AlloyDB, SQL Server columnstore.")]
    return "architectures", "Eight abstract real-time analytics designs built from nine roles, with no product names: when to use each, delay, cost, effort and a verdict.", body, qa


PHYSICAL = {
    "L1": (["Role", "Azure", "AWS", "Open source"], [("Source and replica", "Azure SQL or Hyperscale named replica, Postgres Flexible read replica", "RDS or Aurora read replica", "Postgres or MySQL streaming replica"),
                                                    ("Screen", "Power BI DirectQuery with automatic page refresh", "QuickSight, Grafana", "Grafana, Metabase, Superset")]),
    "L2": (["Role", "Azure", "AWS", "Google Cloud", "Open source"], [("Capture", "Fabric Eventstream CDC connectors", "ClickPipes, or Aurora zero-ETL", "Datastream", "PeerDB, ClickPipes, Estuary"),
                                                                     ("Serve", "Fabric Eventhouse, or ClickHouse Cloud on Azure", "ClickHouse Cloud, or Redshift via zero-ETL", "BigQuery with continuous queries", "ClickHouse"),
                                                                     ("Reshaping", "KQL update policies", "ClickHouse materialized views", "BigQuery SQL", "ClickHouse materialized views"),
                                                                     ("Screen and push", "Real-Time Dashboard, Power BI; Activator for alerts", "Grafana, or a small SSE service", "Looker", "Grafana, or a service that polls the store and pushes only changes")]),
    "L3": (["Role", "Azure", "AWS", "Open source and neutral"], [("Capture", "Debezium on Container Apps or AKS, writing to Event Hubs; or Qlik", "DMS, or Debezium on MSK Connect", "Debezium"),
                                                                 ("Event log and schemas", "Event Hubs Premium with its schema registry", "MSK with Glue Schema Registry", "Confluent Cloud with Schema Registry, or Redpanda"),
                                                                 ("Process", "Stream Analytics, Databricks Structured Streaming, or Confluent Flink on Azure", "Managed Service for Apache Flink", "Confluent Flink, or Flink you run"),
                                                                 ("Serve", "Eventhouse or Azure Data Explorer, or ClickHouse Cloud", "ClickHouse Cloud, Pinot (StarTree), OpenSearch", "ClickHouse, Pinot, Druid"),
                                                                 ("API and push", "API on Container Apps with Azure Web PubSub or SignalR", "API Gateway WebSocket APIs, or AppSync subscriptions", "A Node or Go gateway that reads a results topic and sends SSE"),
                                                                 ("Screen", "React", "React", "React")]),
    "L4": (["Role", "Fabric", "Databricks", "Snowflake", "AWS", "Google Cloud"], [("Capture", "Fabric Mirroring", "Lakeflow Connect", "Openflow, Snowpipe Streaming", "DMS, or Aurora zero-ETL", "Datastream"),
                                                                                  ("Store and reshape", "OneLake Delta tables, materialized lake views", "Lakeflow Declarative Pipelines (streaming tables)", "Dynamic Tables with a target lag of about a minute", "S3 Tables (Iceberg) or Redshift", "BigQuery"),
                                                                                  ("Screen", "Power BI in Direct Lake mode", "Power BI, AI/BI dashboards", "Power BI, Sigma", "QuickSight", "Looker")]),
    "L5": (["Role", "Azure with Databricks", "Azure, all Fabric", "AWS", "Open source and neutral"], [("Capture", "Debezium or Qlik", "Eventstream CDC", "DMS or Debezium", "Debezium"),
                                                                                                    ("Event log", "Event Hubs", "Eventstream", "MSK", "Confluent Kafka"),
                                                                                                    ("Process", "Databricks Structured Streaming", "Eventstream transforms, KQL", "Managed Flink", "Flink"),
                                                                                                    ("Live serve", "Eventhouse, Azure Data Explorer, or ClickHouse", "Eventhouse", "ClickHouse, Pinot", "ClickHouse"),
                                                                                                    ("History", "Delta on ADLS (bronze, silver, gold)", "Eventhouse OneLake availability (the same data as Delta)", "Iceberg on S3 Tables", "Iceberg through Confluent Tableflow, read by Trino, Databricks or Snowflake"),
                                                                                                    ("Screen", "Power BI for analytics, your own SSE app for live", "Real-Time Dashboard, Power BI", "QuickSight and your own app", "Superset and your own app")]),
    "L6": (["Role", "Options"], [("Capture", "The engine's own Postgres or MySQL CDC, or reading from Kafka"), ("Engine", "RisingWave (its cloud, or run on AKS or EKS), Materialize"),
                                 ("Push", "SUBSCRIBE in the engine feeds a small SSE or WebSocket gateway"), ("On Azure", "No native service does this. The closest is Eventhouse materialized views plus Activator; otherwise the vendor's cloud or AKS.")]),
    "L7": (["Database", "How it does analytics", "Push"], [("Azure SQL, SQL Server", "Columnstore indexes on the transaction tables", "Power BI page refresh"), ("AlloyDB for Postgres", "A built-in column engine", "None built in"),
                                                          ("SingleStore, TiDB (TiFlash)", "Row and column storage in one database", "None built in"), ("Oracle Database In-Memory", "An in-memory column store", "None built in"),
                                                          ("Postgres with pg_duckdb or pg_mooncake", "The DuckDB engine inside Postgres", "Supabase Realtime, or LISTEN/NOTIFY"), ("Cosmos DB", "Fabric Mirroring (which replaces Synapse Link)", "Change feed")]),
    "L8": (["Role", "What it used to be"], [("Batch path", "Hadoop or Spark batch jobs"), ("Speed path", "Storm or Spark Streaming"), ("Serving", "HBase or Cassandra"), ("Verdict", "Drop; for recognising older systems only")]),
}


def physical():
    parts = ""
    for k, n, one, pres, opt, *_ in DESIGNS:
        head, rows = PHYSICAL[k]
        parts += (f'<div class="design" id="{k.lower()}"><h3>{k} · {E(n)}</h3><p class="one">{E(one)} <a href="{BASE}architectures/#{k.lower()}">The abstract design</a></p>'
                  f'<figure class="diagram" style="margin:8px 0">{strip(pres, opt)}</figure>{table(head, rows)}</div>')
    body = f"""<section id="plain"><p class="eyebrow">Concept vs product</p><h2>Same roles, different products</h2>
<p>The {link("architectures", "eight designs")} name no product. This page gives each role a product, on each cloud. The design is the logic; the product is the language you write it in. Changing cloud means a new set of products for the same roles, not a new design.</p>
<p class="note">Product names change often; check the current docs before you build.</p></section>
<section id="designs"><p class="eyebrow">Design by design</p><h2>Products for each role</h2>{parts}</section>"""
    qa = [("What is the Azure architecture for real-time analytics?", "For real time: Debezium or Fabric Eventstream CDC, Event Hubs, Stream Analytics or Databricks, Fabric Eventhouse or Azure Data Explorer, and SignalR or Web PubSub for push. For near real time: Fabric Mirroring into OneLake and Power BI in Direct Lake mode."),
          ("What is the AWS architecture for real-time analytics?", "DMS or Debezium, MSK or Kinesis, Managed Service for Apache Flink, ClickHouse Cloud or Pinot, and API Gateway WebSocket APIs. For near real time, Aurora zero-ETL into Redshift."),
          ("Can the same design run on any cloud?", "Yes, if every role sits behind its own interface. Only the binding, which product plays each role, changes.")]
    return "physical", "The eight real-time analytics designs with products for each role on Azure, Fabric, AWS, Google Cloud, Databricks, Snowflake and open source.", body, qa


def contracts():
    body = f"""<section id="plain"><p class="eyebrow">In plain words</p><h2>One small pattern, repeated</h2>
<p>Every hop has the same shape: a <b>producer</b>, a <b>topic</b> with a contract, and a <b>consumer</b>. A stream processor consumes one topic and produces another, so the pattern repeats along the line. Each topic gets the same spec, in three parts.</p>
{fig(hops(), "Producer, topic, consumer, and again. The contract says what; the binding says how.")}</section>

<section id="spec"><p class="eyebrow">The spec</p><h2>Three parts per topic</h2>
{table(["Part", "What it pins down", "Standard to use"], [
        ("Contract (what)", "Event schema, the key, what each field means, compatibility rules (usually backward compatible)", "Avro or Protobuf in a schema registry; CloudEvents for the envelope: id, source, type, time"),
        ("Promises", "Owner, freshness target, quality checks, how long events are kept", "ODCS, the Open Data Contract Standard"),
        ("Binding (how)", "The technology for this hop: Kafka topic name, partitions, consumer group, delivery guarantee; or the WebSocket or SSE details for the screen", "AsyncAPI, which has a bindings section for Kafka, WebSocket, MQTT, AMQP and more")])}
<p>AsyncAPI fits the idea of coding to an interface. The channel and message are the interface; the bindings block is the adapter. Moving from Kafka to Event Hubs changes the binding, not the contract.</p></section>

<section id="promises"><p class="eyebrow">Every hop</p><h2>Five promises every hop must state</h2>
{table(["Promise", "What to decide"], [
        ("Ordering", "Order is only kept within one partition, so pick the key with care, for example the order id."),
        ("Delivery", "At least once is the default, so consumers must cope with duplicates: upsert by key, for example ClickHouse ReplacingMergeTree. Use exactly once (Kafka transactions, Flink checkpoints) only where it is truly needed."),
        ("Deletes", "Change capture sends tombstone events for deletes; the serving store must apply them."),
        ("Late events", "Watermarks and an allowed lateness in the stream processor say how long to wait."),
        ("Replay", "How to rebuild: from the log, or from the lakehouse copy, and how to make sure nothing is counted twice.")])}</section>"""
    qa = [("What is AsyncAPI?", "An open standard for describing event-driven interfaces: channels (topics), messages and their schemas, and bindings for each protocol, such as Kafka or WebSocket. It is to events what OpenAPI is to REST."),
          ("What is the difference between a contract and a binding?", "The contract says what an event is: schema, key, meaning. The binding says how it travels on one hop: which topic, how many partitions, which delivery guarantee. Changing technology changes the binding only."),
          ("Do I need exactly-once delivery?", "Rarely. At-least-once with consumers that upsert by key gives the same result for most analytics. Use exactly-once for money movements and counters that cannot be rebuilt.")]
    return "contracts", "The spec at every hop of a streaming pipeline: contract, promises and binding, with Avro, CloudEvents, ODCS and AsyncAPI, plus ordering, delivery, deletes, late events and replay.", body, qa


def push_to_ui():
    body = f"""<section id="plain"><p class="eyebrow">In plain words</p><h2>Do not make the screen ask</h2>
<p>With <b>pull</b>, the screen asks every few seconds: "anything new?". With <b>push</b>, the server tells the screen when something changes. Push gives fresher screens with less load, but only if the server sends small changes, not every raw event.</p>
{fig(push_drawing(), "Snapshot first, then small, throttled changes.")}</section>

<section id="how"><p class="eyebrow">The pattern</p><h2>Snapshot, then changes</h2>
<ol><li>When the screen connects, send a <b>snapshot</b>: the current numbers.</li>
<li>Then send only <b>changes</b>, throttled to about one per second per widget.</li>
<li>On reconnect, send a fresh snapshot, so a dropped connection never leaves a wrong number on screen.</li>
<li>Never forward raw events to the browser; the server works out what changed.</li></ol></section>

<section id="channel"><p class="eyebrow">The channel</p><h2>SSE or WebSocket?</h2>
{table(["Channel", "What it is", "Use it when", "Verdict"], [
        ("Server-Sent Events (SSE)", "One-way updates from server to browser over plain HTTP; reconnects by itself", "Dashboards and live boards", "Pursue as the default"),
        ("WebSocket", "A two-way connection", "The user also sends things back: filters that change the live query, collaboration", "Pursue when you need two-way"),
        ("GraphQL subscriptions", "Push through a GraphQL API", "You already serve GraphQL", "Fine with a reason"),
        ("Long-polling", "The browser holds a request open until there is news", "Only very old browsers or proxies", "Drop")])}</section>

<section id="source"><p class="eyebrow">Where changes come from</p><h2>Most analytics stores do not push</h2>
<ul><li><b>A results topic.</b> The stream processor writes changed totals to a topic; the push gateway reads it. Works with any store.</li>
<li><b>A streaming database subscription.</b> Materialize SUBSCRIBE and RisingWave subscriptions push changed rows directly.</li>
<li><b>Poll on the server, push the difference.</b> ClickHouse, Pinot and Druid do not push by themselves. The gateway asks the store every second and sends the browser only what changed.</li></ul>
{table(["Gateway", "Azure", "AWS", "Open source and services"], [("Push service", "Azure SignalR, Azure Web PubSub", "API Gateway WebSocket APIs, AppSync subscriptions", "Socket.IO, a small Node or Go SSE service; Ably, Pusher")])}
<p>BI tools such as Power BI do not push; their best is automatic page refresh. See {link("routes", "which route")} for where they fit.</p></section>"""
    qa = [("SSE or WebSocket for a real-time dashboard?", "SSE for most dashboards: updates only flow one way, it runs over plain HTTP and reconnects by itself. Use WebSocket when the user also sends data back, such as filters that change a live query."),
          ("Does ClickHouse push changes to the browser?", "No. Either a stream processor writes changes to a results topic that a gateway reads, or the gateway polls ClickHouse every second and pushes only the difference."),
          ("How often should a dashboard update?", "About once a second per widget is plenty for people. Faster updates cost more and nobody can read them.")]
    return "push-to-ui", "Push semantics for real-time dashboards: snapshot then changes, SSE vs WebSocket, where changes come from when the store cannot push, and gateways per cloud.", body, qa


def cost():
    body = f"""<section id="plain"><p class="eyebrow">In plain words</p><h2>Real time is always on</h2>
<p>A nightly job runs for an hour and switches off. A real-time pipeline runs every minute of every day: the event log, the processor and the serving store never sleep. That is why real time usually costs <b>three to ten times</b> as much as the batch version of the same report, and why the question "{link("basics", "who acts, and how fast")}" matters.</p>
<p class="warn"><b>These are rough list prices remembered from 2025 and 2026, not quotes.</b> Prices change often; check each vendor's pricing page before you plan a budget.</p>
{fig(cost_drawing(), "Rough monthly cost of small stacks, about 1 to 5 MB of events a second.")}</section>

<section id="stacks"><p class="eyebrow">Whole stacks</p><h2>Small stacks, per month</h2>
{table(["Stack", "Rough monthly cost", "Verdict"], [
        ("Near real time: change capture into Snowflake or Databricks every 5 to 15 minutes, Power BI refresh", "$500–2k", "Pursue when people are the ones acting"),
        ("Azure-native real time: Event Hubs, Stream Analytics, Eventhouse or Azure Data Explorer, SignalR", "$1k–2.5k", "Pursue on Azure"),
        ("Managed best of breed: Confluent, Flink, ClickHouse Cloud, SSE", "$2k–6k", "Pursue when the product must not depend on one cloud"),
        ("Open source on your own machines", "$1k–3k for machines, plus one or two engineers to run it", "Drop unless you already have a platform team"),
        ("Enterprise scale, 50 to 100+ MB a second", "$20k–100k+", "Only with a clear revenue case")])}</section>

<section id="units"><p class="eyebrow">Unit prices</p><h2>Rough unit prices by layer</h2>
{table(["Layer", "Option", "Rough price", "Note"], [
        ("Capture", "Debezium", "Free; machines for Kafka Connect about $100–300 a month", "You run it"),
        ("Capture", "Fivetran, Striim", "Priced by rows changed; often $1k–10k+ a month", "Managed; grows with change volume"),
        ("Event log", "Azure Event Hubs Standard", "About $22 a month per throughput unit, plus about $0.03 per million events", "Cheap at small scale"),
        ("Event log", "Event Hubs Premium or Dedicated", "About $700+ a month per processing unit; Dedicated about $5k+ a month", "Isolation and longer retention"),
        ("Event log", "AWS Kinesis", "About $11 a month per shard, plus data", ""),
        ("Event log", "AWS MSK, three small brokers", "About $500–800 a month plus storage", "You still tune it"),
        ("Event log", "Confluent Cloud", "Small production about $1k–3k a month; dedicated clusters $5k–20k+", "Best tooling, highest price"),
        ("Event log", "Kafka on object storage (WarpStream, AutoMQ, diskless Kafka)", "Often 50–80% cheaper than classic Kafka", "Hundreds of milliseconds of delay; fine for near real time"),
        ("Process", "AWS Managed Flink", "About $80 a month per processing unit; a small job about $160–400", ""),
        ("Process", "Azure Stream Analytics", "About $80 a month per streaming unit", "SQL only, Azure only"),
        ("Process", "Databricks streaming", "A small always-on cluster about $500–2k a month", "Licence plus machines"),
        ("Serve", "ClickHouse Cloud", "Development under $100 a month; production about $500–3k", "Strong price for performance"),
        ("Serve", "Fabric capacity", "F2 about $260 a month; F64 about $8.4k a month", "One capacity covers all Fabric work"),
        ("Serve", "Azure Data Explorer", "Development about $150–250 a month; production $1k+", ""),
        ("Serve", "StarTree (Pinot), Imply (Druid)", "Enterprise contracts, usually $5k+ a month", "Thousands of users at once"),
        ("Push", "Azure SignalR, Web PubSub", "Free for 20 connections; about $50 a month per 1,000 connections", "")])}</section>

<section id="drivers"><p class="eyebrow">The bill</p><h2>Five things that drive it</h2>
<ol><li><b>Always-on compute.</b> Nothing pauses.</li>
<li><b>Network traffic between zones.</b> Kafka copies every event to three zones, which can be 30 to 50 percent of the bill. Let consumers read from a copy in their own zone, or use Kafka on object storage.</li>
<li><b>Retention.</b> Days of events on the log's disks. Move older events to the lakehouse.</li>
<li><b>Connectors and partitions.</b> Managed services charge per connector task or per partition.</li>
<li><b>People.</b> Running Kafka and Flink yourself is the biggest hidden cost.</li></ol></section>"""
    qa = [("How much does real-time analytics cost?", "Roughly, a small near-real-time stack runs $500–2k a month, a small Azure-native real-time stack $1k–2.5k, a managed best-of-breed stack $2k–6k, and enterprise scale $20k and up. These are rough list prices; check current pricing."),
          ("Why is real-time analytics expensive?", "Everything runs all day and night, Kafka copies every event across zones, events are kept on disk for days, managed services charge per connector and partition, and running it yourself needs engineers."),
          ("How can I cut the cost of Kafka?", "Read from a replica in the same zone, keep short retention and move history to the lakehouse, use fewer partitions, or use Kafka on object storage where a few hundred milliseconds of delay is fine.")]
    return "cost", "Rough monthly costs of real-time analytics stacks and unit prices for Event Hubs, Kinesis, MSK, Confluent, Flink, ClickHouse, Fabric and SignalR, plus what drives the bill.", body, qa


def technologies():
    body = f"""<section id="plain"><p class="eyebrow">At a glance</p><h2>Safe, growing, or drop</h2>
<p>A technology counts as established here when it is widely used in production, offered by more than one vendor or cloud, and easy to hire for. Growing ones are fine when you have a reason. The last column is for recognising older systems, not for new builds.</p>
{fig(tech_drawing(), "Established, growing, and drop, in brief.")}</section>

<section id="by-layer"><p class="eyebrow">Layer by layer</p><h2>The full list</h2>
{table(["Layer", "Established (safe)", "Growing (fine with a reason)", "Legacy or fading (drop)"], [
        ("Change capture", "Debezium, GoldenGate, AWS DMS, native change feeds (Cosmos DB, SQL Server CDC)", "Estuary, Flink CDC", "Trigger-based capture, polling timestamp columns"),
        ("Event log", "Apache Kafka (no ZooKeeper since 4.0), Kinesis, Event Hubs, Pub/Sub", "Redpanda; Kafka on object storage (WarpStream, AutoMQ, diskless Kafka)", "RabbitMQ or SQS for analytics (no replay); Pulsar is losing momentum"),
        ("Contracts", "Avro or Protobuf with a schema registry, CloudEvents", "AsyncAPI 3, ODCS data contracts", "JSON with no schema"),
        ("Processing", "Apache Flink, Spark Structured Streaming, Kafka Streams", "RisingWave, Materialize, Spark real-time mode", "Storm, Samza, Spark DStreams, ksqlDB (Confluent moved to Flink)"),
        ("Serving", "ClickHouse, Apache Pinot, Apache Druid, Elasticsearch or OpenSearch, Redis, Azure Data Explorer", "StarRocks, Fabric Eventhouse", "Lambda-style batch-plus-speed serving layers"),
        ("History", "Delta, Iceberg", "Confluent Tableflow (topics written straight to tables)", "Hive tables"),
        ("Push", "WebSocket, SSE, Azure SignalR, Socket.IO", "GraphQL subscriptions at scale", "Long-polling"),
        ("All-in-one platforms", "Confluent Cloud, Databricks", "Microsoft Fabric Real-Time Intelligence (generally available since 2024)", "HDInsight")])}</section>

<section id="default"><p class="eyebrow">The safe default</p><h2>If you have to pick today</h2>
<p>Debezium for change capture, Kafka or Event Hubs for the log, Flink only where you need joins or time windows, ClickHouse for serving, Iceberg or Delta for history, and SSE to the screen. Every piece is widely used in production, offered by more than one vendor, and easy to hire for. To place them, see the {link("components", "components")} and the {link("architectures", "eight designs")}.</p></section>"""
    qa = [("What is the standard technology stack for real-time analytics?", "Debezium for change capture, Kafka (or a cloud log such as Event Hubs or Kinesis), Flink or Spark for processing, ClickHouse, Pinot or Druid for serving, Iceberg or Delta for history, and WebSocket or SSE to the screen."),
          ("Is ksqlDB still a good choice?", "Not for new builds. Confluent moved its stream processing to Flink, and ksqlDB is no longer where the investment goes."),
          ("Kafka or Redpanda?", "Kafka is the established choice with the widest support. Redpanda speaks the Kafka protocol and is simpler to run; pick it with a reason, such as a small team or lower latency.")]
    return "technologies", "Which real-time analytics technologies are established, growing or fading, layer by layer: CDC, event logs, contracts, processing, serving, history and push.", body, qa


FUNCS = [basics, lambda_vs_kappa, components, change_capture, routes, architectures, physical, contracts, push_to_ui, cost, technologies]


def ld(title, desc, url, qa, crumbs):
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    out = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": title, "description": desc, "url": url, "inLanguage": "en",
            "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
            "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
           {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}]
    if qa:
        out.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]})
    return "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in out)


def short_desc(d):
    return d if len(d) <= 158 else d[:155].rsplit(" ", 1)[0] + "…"


def render(slug, desc, body, qa):
    title = TITLE[slug]
    url = f"{SITE}{BASE}{slug}/"
    i = [p[0] for p in PAGES].index(slug)
    nxt = PAGES[i + 1] if i + 1 < len(PAGES) else None
    full = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › <a href="{BASE}">Real-time analytics</a> › {E(SHORT[slug])}</p>
<p class="eyebrow" style="margin-top:22px">Real-time analytics · page {i + 1} of {len(PAGES)}</p>
<h1>{E(title)}</h1>
<p class="lede">{E(desc)}</p>{siblings(slug)}
{body}
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{faq(qa)}</section>
<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2>
{f'<p><b>Next page:</b> {link(nxt[0], nxt[2])}</p>' if nxt else ''}
<p><a href="{BASE}">↑ All of real-time analytics</a> · <a href="/learn/data-platform-architecture/">Data platform architecture</a> · <a href="/concepts/#data-engineering">Key concepts</a></p>
{siblings(slug)}</section>"""
    crumbs = [("Learn", f"{SITE}/learn/"), ("Real-time analytics", f"{SITE}{BASE}"), (SHORT[slug], url)]
    return wb.page(title, short_desc(desc), url, full, CSS + ld(title, desc, url, qa, crumbs))


def hub():
    url = f"{SITE}{BASE}"
    cards = "".join(f'<a href="{BASE}{s}/"><span class="n">{i + 1}</span><b>{E(sh)}</b><span>{E(one)}</span></a>' for i, (s, sh, _, one) in enumerate(PAGES))
    qa = [("What is the right architecture for real-time analytics?", "Usually Kappa: every change becomes an event in a replayable log such as Kafka, and everything downstream reads from it. Start smaller when you can: one change capture tool straight into ClickHouse, or into a lakehouse if a few minutes is fine."),
          ("Where should I start on this site?", "Start with real time explained, then the components left to right, then the eight designs. Cost and change capture tools are there when you need them.")]
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › Real-time analytics</p>
<p class="eyebrow" style="margin-top:22px">Data engineering · free guide · {len(PAGES)} short pages</p>
<h1>Real-time analytics, drawn simply</h1>
<p class="lede">How a change in a transaction database becomes a number on a screen within a second: the words people mix up, the components left to right, eight designs without product names, then the products on each cloud, the contracts at every hop, push to the screen, cost, and which technologies are safe.</p>

<section id="plain"><p class="eyebrow">In plain words</p><h2>A shop window that updates itself</h2>
<p>Imagine a shop where every sale is written in the till's notebook. Someone copies each new line onto a moving belt the moment it is written. Further down, people take lines off the belt, add them up, and update a big board in the window. Customers outside see the board change within a second, without asking.</p>
<p>The notebook is the <b>database's change log</b>. The copier is <b>change capture</b>. The belt is the <b>event log</b> (Kafka). The people adding up are the <b>stream processor</b>. The board's memory is the <b>serving store</b>, and the window is the <b>screen</b> that receives <b>push</b> updates.</p></section>

<section id="picture"><p class="eyebrow">The picture</p><h2>Nine roles, left to right</h2>
{fig(roles_drawing(), "Every real-time design uses some of these nine roles. Which ones you keep is the design.")}
<p><b>The short answer:</b> real-time analytics is not the same as streaming. For new builds the usual design is Kappa: every change becomes an event in a replayable log, and everything downstream reads from it. But many screens need less: one change capture tool straight into ClickHouse, or into a lakehouse when a few minutes is fine.</p></section>

<section id="pages"><p class="eyebrow">The pages</p><h2>Read in order, or jump in</h2><div class="map">{cards}</div></section>

<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{faq(qa)}</section>
<section id="next"><p class="eyebrow">Related</p><h2>Where it connects</h2>
<p><a href="/learn/data-platform-architecture/">Data platform architecture</a> shows where streaming sits in a whole platform, and <a href="/learn/medallion-architecture/">the medallion layers</a> show how the same layers run at two speeds. The ideas behind the boxes are in <a href="/concepts/#data-engineering">key concepts</a>, such as <a href="/concepts/cdc/">change data capture</a>.</p></section>"""
    crumbs = [("Learn", f"{SITE}/learn/"), ("Real-time analytics", url)]
    title = "Real-time analytics, drawn simply"
    desc = "Real-time analytics explained simply: streaming vs real time, Lambda vs Kappa, components from CDC and Kafka to push, eight designs, products per cloud, cost."
    return wb.page(title, desc, url, body, CSS + ld(title, desc, url, qa, crumbs))


def main():
    out = ROOT / "learn" / "real-time-analytics"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(hub())
    for fn in FUNCS:
        slug, desc, body, qa = fn()
        d = out / slug
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(render(slug, desc, body, qa))
    print("real-time analytics ->", out, f"(hub + {len(FUNCS)} pages)")


if __name__ == "__main__":
    main()
