"""Databricks real-time mode for a 1-second lane: one page at /learn/streaming/real-time-mode/.

    python3 _guides/rtm.py      (then python3 _site/nav.py and python3 _site/seo.py)

What real-time mode is, GA status, the 1-second lane built only on Databricks next to the
AWS-native lane, sources and sinks, limits, rough cost, a Unity Catalog live store (DynamoDB vs
Lakebase vs others), verdict. Checked against Databricks docs, Nov 2026; prices are rough list prices.
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
URL_PATH = "/learn/streaming/real-time-mode/"
DATE = "2026-11-11"
TITLE = "Databricks real-time mode for a 1-second lane"
DESC = ("Can Databricks real-time mode run a 1-second streaming lane? GA status, sources and sinks, limits, "
        "rough cost against Flink and DynamoDB, and a Unity Catalog live store.")

CSS = C.CSS + """<style>
  .rt .fig { border:var(--line); border-radius:var(--wob); padding:12px 14px; margin:16px 0; background:#fff; overflow-x:auto; }
  .rt .fig svg { width:100%; min-width:680px; height:auto; display:block; } .rt .fig text { font-family:var(--hand); fill:#111; }
  .rt .fig p { font-size:13.5px; color:var(--muted); margin:6px 0 0; }
  .rt .box { border:var(--line); border-radius:var(--wob); padding:10px 16px; margin:14px 0; background:var(--butter-wash); }
</style>"""


def lane(y, label, boxes, fill):
    out = [f'<text x="12" y="{y + 30}" font-size="17">{E(label)}</text>']
    x = 190
    for i, (t, sub, tag) in enumerate(boxes):
        out.append(f'<rect x="{x}" y="{y}" width="140" height="62" rx="8" fill="{fill}" stroke="#111" stroke-width="1.5"/>')
        out.append(f'<text x="{x + 8}" y="{y + 22}" font-size="15">{E(t)}</text><text x="{x + 8}" y="{y + 42}" font-size="12.5">{E(sub)}</text>')
        if i < len(boxes) - 1:
            out.append(f'<path d="M{x + 140},{y + 31} L{x + 160},{y + 31}" stroke="#111" stroke-width="1.4" marker-end="url(#rta)"/>')
            out.append(f'<rect x="{x + 135}" y="{y + 4}" width="30" height="13" rx="6" fill="{"#cfe9d9" if tag == "push" else "#d9e0f5"}" stroke="#111" stroke-width="1"/>'
                       f'<text x="{x + 150}" y="{y + 14}" font-size="8.5" text-anchor="middle" font-family="monospace" font-weight="700">{tag.upper()}</text>')
        x += 160
    return "".join(out)


def drawing():
    a = lane(30, "AWS-native (today)", [("Kinesis", "event log, 7 days", "pull"), ("Managed Flink", "windows, limits", "push"),
                                         ("DynamoDB", "live store, 48 h", "pull"), ("Lambda", "reads the stream", "push"),
                                         ("WebSocket", "to the live board", "push")], "#eef3fb")
    b = lane(130, "Databricks only", [("Kinesis", "or Kafka, MSK", "pull"), ("Real-time mode", "fixed classic cluster", "push"),
                                      ("Lakebase", "Postgres, in UC", "pull"), ("Databricks App", "polls every second", "push"),
                                      ("Browser", "server-sent events", "push")], "#fbeef3")
    return f"""<svg viewBox="0 0 1000 220" role="img" aria-label="Two ways to build a 1-second lane. AWS-native: Kinesis, Managed Flink, DynamoDB, Lambda reading the DynamoDB stream, WebSocket to the live board. Databricks only: Kinesis or Kafka, real-time mode on a fixed classic cluster, Lakebase, a Databricks App that polls, server-sent events to the browser.">
<defs><marker id="rta" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#111"/></marker></defs>
{a}{b}
<text x="190" y="214" font-size="13">Real-time mode cannot write Delta, so even the Databricks-only lane needs a non-Delta live store (Lakebase here).</text>
</svg>"""


STATUS = [
    ("What it is", "A trigger type for Spark Structured Streaming: records are processed as they arrive instead of in micro-batches. Databricks quotes latency under 100 ms, and as low as a few milliseconds."),
    ("Status", "Announced generally available in March 2026. Some documentation pages still say Public Preview; check your workspace before production."),
    ("Runtime", "Databricks Runtime 16.4 LTS or later."),
    ("Compute", "Classic compute with a fixed size: autoscaling off, Photon off, enough task slots for every task in every stage. On serverless, only through Lakeflow pipelines (set at the pipeline level)."),
]

SRC_SINK = [
    ("Kafka (and MSK, Event Hubs through its Kafka endpoint)", "Yes", "Yes"),
    ("Kinesis", "Yes (enhanced fan-out recommended; polling only on newer runtimes, check)", "No"),
    ("Delta tables", "No", "No"),
    ("Pub/Sub, Pulsar", "No", "No"),
    ("Custom writer (forEach), e.g. to Lakebase or DynamoDB", "-", "Yes"),
    ("forEachBatch", "-", "No"),
]

LIMITS = [
    ("Cannot write Delta", "The live store must be something else: Lakebase, DynamoDB, Kafka. Bronze still comes from the platform lane."),
    ("Fixed, always-on cluster", "No autoscaling and no scale to zero; you size for the peak and pay all day."),
    ("Update output mode only", "Each output is an upsert of the latest value, which suits a live store."),
    ("No event-time timers, no transformWithStateInPandas", "Some stateful patterns (alerts after N minutes of silence) need another approach."),
    ("No Photon", "CPU sizing as plain Spark."),
]

COST = [
    ("Processing", "Managed Flink, 2 + 1 units: about $250", "Real-time mode, driver + 1 to 2 workers (EC2 + jobs DBUs): about $430 to $650"),
    ("Live store", "DynamoDB, changes only: about $40 to $50", "Lakebase: about $100 to $300"),
    ("Push to screens", "Lambda + API Gateway WebSocket: about $130", "Databricks App: about $50 to $150"),
    ("Simple limit alerts", "Lambda: about $8", "Inside the same query"),
    ("Total, production example (300 readings a second)", "about $530 a month", "about $700 to $1,100 a month"),
    ("Governed in Unity Catalog", "No (IAM on AWS)", "Yes, end to end"),
    ("Push or pull into the screen", "Push (DynamoDB Streams then WebSocket)", "The app pulls from Lakebase every second, then pushes to the browser"),
]

STORES = [
    ("DynamoDB", "No; not a Lakehouse Federation source either", "Push via Streams; about $50; no servers to run", "Outside Unity Catalog", "Pursue if a disposable 48-hour copy may sit outside Unity Catalog"),
    ("Lakebase (Postgres run by Databricks)", "Yes: registered as a catalog with Unity Catalog permissions", "SQL; same platform; can also be the metadata store", "No free push (poll, or LISTEN/NOTIFY, which loses messages while disconnected); always on, about $100 to $300", "Pursue if every store must be in Unity Catalog"),
    ("RDS or Aurora Postgres with Lakehouse Federation", "Only queries made from Databricks", "Familiar", "The live app reads it directly, outside Unity Catalog", "Drop: governance on paper only"),
    ("A Delta table as the live store", "Yes", "Fully governed", "Not built for per-second single-row updates; real-time mode cannot write it anyway", "Drop"),
]

VERDICT = [
    ("Keep the AWS-native lane (Flink, DynamoDB, WebSocket)", "Cheapest, true push, milliseconds", "Two engines (Flink and Spark); the live store is outside Unity Catalog", "Pursue (default)"),
    ("Databricks-only lane, real-time mode in a Structured Streaming job (classic cluster)", "One platform, governed end to end, one engine; the proven path (announced GA)", "About $200 to $600 a month more; you size and run a fixed cluster; no Delta sink; the app polls Lakebase", "Pursue only if one governed platform is worth the extra cost"),
    ("Databricks-only lane, real-time mode in a Lakeflow pipeline (serverless)", "Same engine and lane, but no cluster to size or tune", "Newest path: status, limits and pricing not confirmed; still always on; same no-Delta-sink and polling limits", "Trial in a sandbox, compare with the job version"),
]

PACKAGING = [
    ("How you write it", "Ordinary PySpark: readStream, your logic, writeStream with the real-time trigger, run as a Lakeflow Job", "Declarative: a pipeline of flows and sinks, with real-time mode switched on for the pipeline"),
    ("Compute", "A classic cluster you size: fixed size, autoscaling off, Photon off, enough task slots for every task", "Serverless: Databricks picks and manages the machines"),
    ("Who tunes it", "You: machine type, number of workers, task slots", "Databricks"),
    ("Billing", "EC2 plus jobs DBUs, all day (about $430 to $650 a month in the example)", "Serverless DBUs, all day (still always on, no scale to zero); no published figure, measure it"),
    ("Status", "Announced generally available, March 2026", "Newer; check status, limits and pricing on your workspace"),
    ("The same in both", "Engine, sources (Kafka, Kinesis), no Delta sink, Lakebase live store, the app polling it", "Same"),
]

QA = [
    ("Is Databricks real-time mode generally available?", "Databricks announced it generally available in March 2026 for Spark Structured Streaming on Runtime 16.4 LTS and later. Some doc pages still say Public Preview, so check your workspace."),
    ("Can real-time mode write to Delta tables?", "No. Sinks are Kafka and custom forEach writers. For a live store, write to Lakebase or DynamoDB; keep bronze, silver and gold in the platform lane."),
    ("Does real-time mode work with Kinesis?", "Yes, as a source, with enhanced fan-out recommended. Kinesis is not supported as a sink."),
    ("How much does a 1-second lane on Databricks cost?", "Roughly $700 to $1,100 a month for a small plant stream: a fixed classic cluster, Lakebase and a Databricks App. The AWS-native lane (Flink, DynamoDB, WebSocket) is about $530. Rough list prices; measure."),
    ("Is DynamoDB governed by Unity Catalog?", "No. If every store must be in Unity Catalog, use Lakebase as the live store and accept that the app polls it."),
]

SOURCES = [
    ("Real-time mode in Structured Streaming", "https://docs.databricks.com/aws/en/structured-streaming/real-time"),
    ("Real-time mode reference (sources, sinks, limits)", "https://docs.databricks.com/aws/en/structured-streaming/real-time/reference"),
    ("General availability announcement", "https://www.databricks.com/blog/announcing-general-availability-real-time-mode-apache-spark-structured-streaming-databricks"),
]


def page():
    url = f"{SITE}{URL_PATH}"
    src = "".join(f'<li><a href="{u}">{E(n)}</a></li>' for n, u in SOURCES)
    stores = ('<div class="tw"><table class="t"><tr><th>Live store</th><th>In Unity Catalog?</th><th>Pros</th><th>Cons</th><th>Verdict</th></tr>'
              + "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td>{E(c)}</td><td>{E(d)}</td><td><b>{E(v)}</b></td></tr>" for a, b, c, d, v in STORES) + "</table></div>")
    verdict = ('<div class="tw"><table class="t"><tr><th>Option</th><th>Pros</th><th>Cons</th><th>Verdict</th></tr>'
               + "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td>{E(c)}</td><td><b>{E(v)}</b></td></tr>" for a, b, c, v in VERDICT) + "</table></div>")
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/data-engineering/">Data engineering</a> › <a href="/learn/streaming/">Streaming</a> › Real-time mode</p>
<p class="eyebrow" style="margin-top:22px">Data engineering · free guide · one page</p>
<h1>{E(TITLE)}</h1>
<p class="lede">The fast lane in the <a href="/learn/streaming/">streaming design</a> puts plant readings on a live board within seconds using Flink, DynamoDB and a WebSocket. Databricks real-time mode can do the same job inside Databricks. This page shows how, what it cannot do, what it costs, and when it is worth it.</p>
<div class="rt">
<section id="what"><p class="eyebrow">In plain words</p><h2>What real-time mode is</h2>
<p>Normal Spark streaming collects records for a moment and processes them as a small batch. Real-time mode processes each record as it arrives, so the delay drops from seconds to milliseconds. It is the same Spark code with a different trigger.</p>
{C.table(["", ""], STATUS)}</section>

<section id="arch"><p class="eyebrow">The picture</p><h2>The 1-second lane, two ways</h2>
<div class="fig">{drawing()}<p>Tags show who starts each transfer: PUSH, the sender; PULL, the receiver.</p></div></section>

<section id="io"><p class="eyebrow">Sources and sinks</p><h2>What it can read and write</h2>{C.table(["System", "As a source", "As a sink"], SRC_SINK)}</section>

<section id="limits"><p class="eyebrow">Limits</p><h2>What to know before you choose it</h2>{C.table(["Limit", "What it means here"], LIMITS)}</section>

<section id="cost"><p class="eyebrow">Cost</p><h2>Rough cost a month, side by side</h2>{C.table(["", "AWS-native lane", "Databricks-only lane"], COST)}
<p class="note">Rough US list prices from 2025 and 2026, production example (5 plants, 300 readings a second). Databricks publishes no fixed price for this setup; measure it on your workload. More in the <a href="/learn/data-systems/platform/cost/calculator/#streaming-services">cost calculator</a>.</p></section>

<section id="store"><p class="eyebrow">Governance</p><h2>A live store inside Unity Catalog</h2>
<p>DynamoDB is not governed by Unity Catalog and is not a Lakehouse Federation source. If policy says every store must be in Unity Catalog, the live store becomes Lakebase.</p>{stores}
<div class="box">The live store holds a 48-hour copy that expires. The record of the same readings is governed in bronze, silver and gold. That is why keeping DynamoDB outside Unity Catalog is usually acceptable.</div></section>

<section id="packaging"><p class="eyebrow">Two ways to run it</p><h2>A Structured Streaming job or a Lakeflow pipeline</h2><p>Both use the same real-time mode engine for the same Databricks-only lane. They differ in how you write the code and who runs the machines.</p>{C.table(["", "Structured Streaming job", "Lakeflow pipeline"], PACKAGING)}</section>

<section id="verdict"><p class="eyebrow">Choosing</p><h2>Verdict</h2>{verdict}</section>

<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(QA)}</section>
<section id="sources"><p class="eyebrow">Sources</p><h2>Checked against</h2><ul>{src}</ul></section>
<section id="next"><p class="eyebrow">Related</p><h2>Where it connects</h2>
<p><a href="/learn/streaming/">Streaming guide</a> · <a href="/learn/streaming/sim/">Streaming simulator</a> (pick the "Databricks only" binding) · <a href="/learn/streaming/sim/faster/">A faster platform lane</a> · <a href="/learn/delta-vs-iceberg/">Delta vs Iceberg</a></p></section>
</div>"""
    crumbs = [("Data engineering", f"{SITE}/data-engineering/"), ("Streaming", f"{SITE}/learn/streaming/"), ("Real-time mode", url)]
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": TITLE, "description": DESC, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in QA]}]
    head = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(TITLE, DESC, url, body, head)


def main():
    out = ROOT / "learn" / "streaming" / "real-time-mode"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("real-time mode ->", out / "index.html")


if __name__ == "__main__":
    main()
