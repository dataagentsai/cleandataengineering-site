"""Streaming options at a glance: one table of every fast-lane and platform-lane path, at /learn/streaming/options/.

    python3 _guides/streaming_options.py      (then python3 _site/nav.py and python3 _site/seo.py)

Each row: lane, path hop by hop, delay to the screen, how the screen gets data (push or pull),
governed in Unity Catalog, rough monthly cost (production example), verdict, reason, link to the
detail page. Filter buttons by lane and verdict. Numbers come from the streaming guide, the three
simulators and the real-time page; rough list prices.
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
URL_PATH = "/learn/streaming/options/"
DATE = "2026-11-11"
TITLE = "Streaming options at a glance: fast lane and platform lane"
DESC = ("Every fast-lane and platform-lane streaming option on AWS, Databricks and Azure in one table: path, delay to "
        "the screen, push or pull, Unity Catalog, cost, verdict and why, with links to the details.")

# verdict keys: pursue, alt (pursue with a condition), try, drop
P, ALT, TRY, DROP = "pursue", "alt", "try", "drop"
ROWS = [
    # lane, id, name, path, delay, screen gets data, UC, cost, verdict key, verdict text, why, link text, link
    ("fast", "F1", "AWS-native lane", "Kinesis, Managed Flink (windows, limits), DynamoDB, DynamoDB Streams read by Lambda, API Gateway WebSocket, React live board",
     "1 to 3 s", "Push", "No (IAM)", "~$530", P, "Pursue (default)",
     "Cheapest true push in milliseconds to seconds; serverless parts; the live store is a 48-hour copy, the record stays governed in gold.",
     "Simulator, AWS + Databricks", "/learn/streaming/sim/"),
    ("fast", "F2", "F1 with AppSync Events", "As F1, but the function publishes to an AppSync Events channel instead of tracking WebSocket connections",
     "1 to 3 s", "Push", "No", "~$500", TRY, "Try",
     "Same lane with less code: AWS handles the fan-out to screens, no connections table.",
     "Streaming guide, push and alerts", "/learn/streaming/#physical"),
    ("fast", "F3", "Alerts only, no Flink", "Kinesis, Lambda limit checks, SNS alerts and a small live store",
     "under 1 s", "Push", "No", "~$180", ALT, "Pursue if only limit alerts are needed",
     "Nearly free, but no time windows, no drift detection, no state.",
     "Streaming guide, live processor", "/learn/streaming/#physical"),
    ("fast", "F4", "Flink into ClickHouse", "Kinesis, Flink (or ClickPipes), ClickHouse; the gateway polls every second and pushes differences",
     "2 to 5 s", "Pull, then push", "No", "~$750 to $3,500", ALT, "Pursue only if live screens need slicing beyond 48 hours",
     "Fast ad-hoc filters for many users, but a new vendor, no push, and a third copy of the numbers.",
     "Streaming guide, to the UI", "/learn/streaming/#ui"),
    ("fast", "F5", "Flink into Lakebase", "Kinesis, Flink, Lakebase (Postgres in Databricks); the app polls Lakebase",
     "2 to 5 s", "Pull, then push", "Yes (store)", "~$450 to $650", ALT, "Pursue if the live store must be in Unity Catalog",
     "Keeps the cheap Flink lane but moves the live store under Unity Catalog; loses free push from DynamoDB Streams.",
     "Real time page, live store", "/learn/streaming/real-time-mode/#store"),
    ("fast", "F6", "Databricks real-time mode, serverless pipeline", "Kinesis or Kafka, Lakeflow pipeline in real-time mode (GA 29 Oct 2026), custom writer into Lakebase, Databricks App, browser",
     "1 to 3 s", "Pull, then push", "Yes", "~$700 to $1,100", ALT, "Pursue if one governed platform is worth the extra cost",
     "One engine and one platform, governed end to end, no cluster to size; costs more, cannot write Delta, the app polls.",
     "Real time page", "/learn/streaming/real-time-mode/"),
    ("fast", "F7", "Databricks real-time mode, classic job", "As F6, but a Structured Streaming job on a fixed classic cluster",
     "1 to 3 s", "Pull, then push", "Yes", "~$700 to $1,100", DROP, "Drop (prefer F6)",
     "Same result as F6, but you size and run a fixed always-on cluster.",
     "Real time page, two ways to run it", "/learn/streaming/real-time-mode/#packaging"),
    ("fast", "F8", "Azure: Fabric Real-Time Intelligence", "IoT Hub, Event Hubs, Fabric Eventstream, Eventhouse, Real-Time Dashboard or Power BI",
     "2 to 10 s", "Pull (auto-refresh)", "No (Fabric)", "~$650", ALT, "Pursue on Azure",
     "The Azure way to put live data in Power BI; needs Fabric capacity.",
     "Simulator, Azure binding", "/learn/streaming/sim/"),
    ("fast", "F9", "Lakehouse//RT as the fast lane", "Pipelines into Delta, Lakehouse//RT warehouse, dashboard",
     "minutes (table freshness)", "Pull", "Yes", "beta pricing", DROP, "Drop as a fast-lane replacement",
     "It makes queries fast, not data fresh: a screen is only as fresh as the table it reads.",
     "Real time page, Lakehouse//RT", "/learn/streaming/real-time-mode/#lakehouse-rt"),
    ("fast", "F10", "Power BI streaming or push datasets", "Processor pushes rows straight into Power BI",
     "seconds", "Push", "No", "-", DROP, "Drop",
     "Being retired (no new ones after 31 Oct 2027), rate-limited, and a second copy of the logic.",
     "Simulator, push or pull", "/learn/streaming/sim/"),
    ("fast", "F11", "Push with no live store", "Processor pushes straight to screens",
     "about 1 s", "Push", "No", "~$100", DROP, "Drop",
     "A screen that opens or reconnects has nothing to show until the next change; no last-hour chart.",
     "Streaming guide, to the UI", "/learn/streaming/#ui"),
    ("fast", "F12", "Zerobus as the only entry", "Devices straight into a bronze Delta table",
     "seconds to bronze", "-", "Yes", "-", DROP, "Drop for sensors",
     "One reader only: no shared event log for a live lane and the lake, no replay from the log.",
     "Streaming guide, front door", "/learn/streaming/#physical"),
    ("fast", "F13", "Timestream LiveAnalytics, IoT Events", "AWS time-series store and detector service",
     "-", "-", "No", "-", DROP, "Drop",
     "Timestream LiveAnalytics is closed to new customers; IoT Events reached end of support on 20 May 2026.",
     "Streaming guide, notes", "/learn/streaming/#notes"),

    ("platform", "P1", "Today: hourly gold, Pro refresh", "15-min scheduled Lakeflow pipeline (Kinesis + Auto Loader), silver, gold hourly at :15, Power BI Pro refresh every 30 min",
     "31 to 90 min (avg 60)", "Pull", "Yes", "~$670", DROP, "Replace with P2",
     "88% of the time is waiting for clocks: the hourly gold slot and Power BI's refresh timer.",
     "Faster platform lane, design A", "/learn/streaming/sim/faster/"),
    ("platform", "P2", "Chained steps", "15-min run, gold rebuilt provisionally on every run (table-update trigger), gold job starts the Power BI import refresh",
     "6 to 22 min (avg 14)", "Pull (refresh started by a push signal)", "Yes", "~$770 + Power BI PPU, Premium or Fabric", P, "Pursue (recommended)",
     "Removes the two big waits for about $100 a month more; viewers read Power BI's in-memory copy, no idle queries.",
     "Faster platform lane, design B", "/learn/streaming/sim/faster/"),
    ("platform", "P3", "Chained, every 5 minutes", "As P2 with 5-minute runs",
     "5 to 10 min", "Pull", "Yes", "~$1,900", ALT, "Pursue only with a named need under 10 min",
     "About three times the platform-lane compute for a few minutes less.",
     "Faster platform lane, design C", "/learn/streaming/sim/faster/"),
    ("platform", "P4", "Continuous pipeline", "Always-on streaming tables, gold kept up to date, warm SQL warehouse, DirectQuery change detection every minute",
     "2 to 4 min", "Pull", "Yes", "~$2,400", DROP, "Drop",
     "Three to four times the cost; if minutes are not enough, the need belongs in the fast lane.",
     "Faster platform lane, design D", "/learn/streaming/sim/faster/#flink-vs-dlt"),
    ("platform", "P5", "P2 plus Lakehouse//RT serving", "As P2; dashboards and apps query gold on a Lakehouse//RT warehouse",
     "as P2, queries in ms", "Pull", "Yes", "P2 + beta pricing (30% off to Jan 2027)", TRY, "Pursue once out of beta, when many users are the pain",
     "Millisecond queries for hundreds of users on governed gold; replaces ClickHouse for slicing. Does not make data fresher.",
     "Real time page, Lakehouse//RT", "/learn/streaming/real-time-mode/#lakehouse-rt"),
    ("platform", "P6", "AWS only", "Firehose into S3 Tables (Iceberg), Glue jobs, Athena, QuickSight or Power BI via Athena",
     "15 to 75 min", "Pull", "No (Glue, Lake Formation)", "~$1,000 (whole stack)", ALT, "Pursue only without Databricks",
     "Fewest vendors; you build silver and gold jobs and the semantic layer yourself.",
     "Delta vs Iceberg", "/learn/delta-vs-iceberg/"),
    ("platform", "P7", "Azure: Fabric reads gold directly", "Lakeflow pipeline into Delta, gold mirrored into Fabric, Power BI Direct Lake",
     "as the pipeline", "Pull (no refresh copy)", "Yes, mirrored to Fabric", "Fabric capacity", TRY, "Pursue on Azure, check availability",
     "Power BI reads the Delta files without an import refresh.",
     "Delta vs Iceberg, which to pick", "/learn/delta-vs-iceberg/#pick"),
    ("platform", "P8", "DirectQuery refreshing every minute", "Power BI queries the SQL warehouse on a 1-minute timer",
     "1 min after gold", "Pull", "Yes", "warehouse never sleeps", DROP, "Drop",
     "About 24,000 queries an hour for 50 viewers, almost all returning the same answer while gold changes hourly.",
     "Faster platform lane", "/learn/streaming/sim/faster/"),
    ("platform", "P9", "Push rows from Databricks into Power BI", "Gold job posts rows to a Power BI push dataset",
     "minutes", "Push", "No", "-", DROP, "Drop",
     "Push datasets are being retired, have limits, and duplicate the logic; push the signal (refresh), not the rows.",
     "Simulator, push or pull", "/learn/streaming/sim/"),
    ("platform", "P10", "File arrival trigger for irregular files", "Lab or partner file lands, Databricks file arrival trigger, Auto Loader reads every new file",
     "about 1 to 2 min to silver", "Pull (checks each minute)", "Yes", "~$30", P, "Pursue",
     "Event-driven without glue code; a burst of files is one run; a missed event never loses a file.",
     "Simulator, what starts each step", "/learn/streaming/sim/"),
    ("platform", "P11", "One pipeline run per file", "S3 event, Lambda, run the pipeline with the file path",
     "1 min + start-up", "Push", "Yes", "-", DROP, "Drop",
     "A start-up per file, runs queue, and passing paths skips Auto Loader's bookkeeping, so a missed event loses a file.",
     "Streaming guide, Databricks choices", "/learn/streaming/#dbx"),
    ("platform", "P12", "Database changes as files", "DMS (or Lakeflow Connect) writes change files to S3; the 15-min run reads them with Auto Loader",
     "minutes", "Pull", "Yes", "~$60", P, "Pursue",
     "No event log needed until a live reader appears; SCD type 1 and 2 built in silver.",
     "Streaming guide, non-IoT", "/learn/streaming/#noniot"),
]

VCLASS = {P: "v-p", ALT: "v-a", TRY: "v-t", DROP: "v-d"}

CSS = C.CSS + """<style>
  main.wrap { max-width:1320px; }
  main.wrap > p, main.wrap > h2, main.wrap > section { max-width:900px; }
  .so-filters { display:flex; flex-wrap:wrap; gap:8px; margin:14px 0; }
  .so-filters button { font:inherit; font-size:14px; border:1.5px solid var(--ink); border-radius:999px; background:#fff; padding:3px 14px; cursor:pointer; }
  .so-filters button.on { background:var(--rose-wash); font-weight:600; }
  table.so { border-collapse:collapse; width:100%; font-size:13.5px; }
  table.so th, table.so td { text-align:left; padding:7px 8px; border-bottom:1.5px dashed var(--rule-firm); vertical-align:top; }
  table.so th { font-size:11px; letter-spacing:.07em; text-transform:uppercase; color:var(--faint); position:sticky; top:0; background:#fff; }
  table.so tr.grp td { background:var(--surface-2); font-family:var(--hand); font-size:20px; }
  table.so td.id { font-family:var(--mono); font-weight:700; }
  table.so td.v-p { background:var(--mint-wash); font-weight:700; } table.so td.v-a { background:var(--peri-wash); font-weight:700; }
  table.so td.v-t { background:var(--butter-wash); font-weight:700; } table.so td.v-d { background:var(--rose-wash); }
  table.so td:last-child { min-width:130px; } table.so td:nth-child(9) { min-width:200px; }
  .so-key { font-size:13.5px; color:var(--muted); }
</style>"""

JS = """<script>
(function(){
  var lane='all', verdict='all';
  function apply(){
    document.querySelectorAll('table.so tbody tr[data-lane]').forEach(function(r){
      var ok=(lane==='all'||r.dataset.lane===lane)&&(verdict==='all'||(verdict==='keep'?r.dataset.v!=='drop':r.dataset.v===verdict));
      r.style.display=ok?'':'none';
    });
    document.querySelectorAll('table.so tbody tr.grp').forEach(function(g){ g.style.display=(lane==='all'||g.dataset.g===lane)?'':'none'; });
  }
  document.querySelectorAll('.so-filters button').forEach(function(b){
    b.addEventListener('click',function(){
      var k=b.dataset.k, val=b.dataset.val;
      if(k==='lane') lane=val; else verdict=val;
      document.querySelectorAll('.so-filters button[data-k="'+k+'"]').forEach(function(x){x.classList.toggle('on',x===b);});
      apply();
    });
  });
})();
</script>"""


def table():
    head = ["#", "Option", "Path, hop by hop", "Delay to the screen", "Screen gets data by", "In Unity Catalog", "Rough cost a month", "Verdict", "Why", "Details"]
    out = ['<div class="tw"><table class="so"><thead><tr>' + "".join(f"<th>{E(h)}</th>" for h in head) + "</tr></thead><tbody>"]
    for g, label in (("fast", "Fast lane: seconds, for acting now"), ("platform", "Platform lane: minutes, the number of record, to Power BI")):
        out.append(f'<tr class="grp" data-g="{g}"><td colspan="10">{E(label)}</td></tr>')
        for lane, i, name, path, delay, how, uc, cost, vk, vt, why, lt, link in ROWS:
            if lane != g:
                continue
            out.append(f'<tr data-lane="{lane}" data-v="{vk}"><td class="id">{i}</td><td><b>{E(name)}</b></td><td>{E(path)}</td><td>{E(delay)}</td>'
                       f'<td>{E(how)}</td><td>{E(uc)}</td><td>{E(cost)}</td><td class="{VCLASS[vk]}">{E(vt)}</td><td>{E(why)}</td>'
                       f'<td><a href="{link}">{E(lt)}</a></td></tr>')
    out.append("</tbody></table></div>")
    return "".join(out)


QA = [
    ("What is the recommended streaming design on AWS and Databricks?", "Two lanes. The fast lane (F1): Kinesis, Managed Flink, DynamoDB and a WebSocket to a live board, 1 to 3 seconds, about $530 a month. The platform lane (P2): 15-minute Lakeflow runs with gold rebuilt on every run and the gold job starting the Power BI refresh, 6 to 22 minutes, about $770 a month."),
    ("When should the fast lane run on Databricks instead?", "When having one platform governed end to end in Unity Catalog is worth about $200 to $600 a month more. Then use real-time mode in a serverless Lakeflow pipeline (F6), writing to Lakebase."),
    ("Does Lakehouse//RT replace the fast lane?", "No. It answers queries in milliseconds but a screen is only as fresh as the table it reads. It fits as the serving layer on gold (P5)."),
]


def page():
    url = f"{SITE}{URL_PATH}"
    n_p = sum(1 for r in ROWS if r[8] == P)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/data-engineering/">Data engineering</a> › <a href="/learn/streaming/">Streaming</a> › All options</p>
<p class="eyebrow" style="margin-top:22px">Data engineering · one table</p>
<h1>{E(TITLE)}</h1>
<p class="lede">Every way we looked at to get streaming data to a screen, in one table: {len(ROWS)} options, {n_p} recommended. Each row gives the whole path, how fresh the screen is, whether data is pushed or pulled to it, whether it sits in Unity Catalog, rough cost, the verdict and why, and a link to the details.</p>
<div class="box-do" style="border:var(--line);border-radius:var(--wob);padding:10px 16px;background:var(--butter-wash);max-width:900px"><b>The short answer:</b> fast lane <b>F1</b> (AWS-native, 1 to 3 s, ~$530) plus platform lane <b>P2</b> (chained, 6 to 22 min, ~$770), with <b>P10</b> for irregular files and <b>P12</b> for database changes. Switch the fast lane to <b>F6</b> only if one governed platform is worth the extra cost; add <b>P5</b> once Lakehouse//RT leaves beta and many users query gold.</div>
<div class="so-filters">
<button data-k="lane" data-val="all" class="on">Both lanes</button><button data-k="lane" data-val="fast">Fast lane</button><button data-k="lane" data-val="platform">Platform lane</button>
<span style="width:14px"></span>
<button data-k="v" data-val="all" class="on">All verdicts</button><button data-k="v" data-val="keep">Pursue or conditional</button><button data-k="v" data-val="drop">Dropped</button></div>
{table()}
<p class="so-key">Verdict colours: green = pursue, blue = pursue under a condition, yellow = try first, rose = drop. Delays are for the production example (5 plants, 300 readings a second). Costs are rough US list prices from 2025 and 2026 for that lane only; see the <a href="/learn/data-systems/platform/cost/calculator/#streaming-services">cost calculator</a>. "Screen gets data by" uses the rule: whoever starts the transfer; push if the sender starts it, pull if the screen or its server asks.</p>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(QA)}</section>
<section id="next"><p class="eyebrow">Related</p><h2>The detail pages</h2>
<p><a href="/learn/streaming/">Streaming guide</a> · <a href="/learn/streaming/sim/">Simulator: data flow</a> · <a href="/learn/streaming/sim/lanes/">Simulator: three lanes</a> · <a href="/learn/streaming/sim/faster/">Simulator: a faster platform lane</a> · <a href="/learn/streaming/real-time-mode/">Real-time mode and Lakehouse//RT</a> · <a href="/learn/delta-vs-iceberg/">Delta vs Iceberg</a> · <a href="/learn/data-systems/platform/cost/calculator/#streaming-services">Cost calculator</a></p></section>
{JS}"""
    crumbs = [("Data engineering", f"{SITE}/data-engineering/"), ("Streaming", f"{SITE}/learn/streaming/"), ("All options", url)]
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": TITLE, "description": DESC, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in QA]}]
    head = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(TITLE, DESC, url, body, head)


def main():
    out = ROOT / "learn" / "streaming" / "options"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("streaming options ->", out / "index.html", f"({len(ROWS)} options)")


if __name__ == "__main__":
    main()
