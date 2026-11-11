"""Streaming simulator: two pages sharing one engine (learn/streaming/sim/stream-sim.js).

    python3 _guides/streaming_sim.py      (then python3 _site/nav.py and python3 _site/seo.py)

/learn/streaming/sim/        Flow: IoT and non-IoT sources, hop by hop, fast lane and platform lane, incidents.
/learn/streaming/sim/lanes/  Three lanes over a simulated day: fast, near real time and batch, and where they meet.
Both pick a binding (AWS + Databricks, AWS only, Azure + Databricks, Databricks only) and a route
(direct, via the medallion, or both). Illustrative model of /learn/streaming/, not recorded runs.
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
DATE = "2026-11-11"
JS = "/learn/streaming/sim/stream-sim.js?v=11"

CSS = C.CSS + """<style>
  main.wrap { max-width:1320px; }
  main.wrap > p, main.wrap > ol, main.wrap > h2, main.wrap > section { max-width:860px; }
  .ss-ctl { display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:10px; margin:14px 0; }
  .ss-ctl fieldset { border:var(--line); border-radius:var(--wob); padding:8px 12px; margin:0; background:#fff; }
  .ss-ctl legend { font-family:var(--hand); font-size:19px; padding:0 4px; }
  .ss-ctl label { display:block; font-size:14px; margin:2px 0; cursor:pointer; }
  .ss-ctl button, .ss-bar button { font:inherit; font-size:13.5px; border:1.5px solid var(--ink); border-radius:999px; background:#fff; padding:3px 12px; margin:3px 4px 3px 0; cursor:pointer; }
  .ss-ctl button:hover, .ss-bar button:hover { background:var(--butter-wash); }
  .ss-bar { display:flex; flex-wrap:wrap; align-items:center; gap:10px; margin:8px 0; font-size:14.5px; }
  .ss-bar .clk { font-family:var(--mono); font-size:16px; border:var(--line); border-radius:8px; padding:2px 10px; background:#fff; }
  .ss-bar select { font:inherit; font-size:14px; }
  .ss-stage { border:var(--line); border-radius:var(--wob); background:#fff; padding:8px; overflow-x:auto; }
  #ssim-svg { width:100%; min-width:900px; height:auto; display:block; }
  #ssim-svg text { font-family:var(--hand); fill:#111; }
  #ssim-svg .bx rect { fill:#fff; stroke:#111; stroke-width:1.5; }
  #ssim-svg .fastb rect { fill:var(--peri-wash); } #ssim-svg .nrtb rect { fill:var(--rose-wash); }
  #ssim-svg .batchb rect { fill:var(--butter-wash); } #ssim-svg .shared rect { fill:var(--mint-wash); }
  #ssim-svg .ui rect { stroke-width:2.6; }
  #ssim-svg .bt { font-size:15px; } #ssim-svg .bp { font-size:12px; fill:#444; font-family:var(--sans,inherit) !important; }
  #ssim-svg .bc { font-size:11.5px; font-family:var(--mono) !important; fill:#222; }
  #ssim-svg .small rect { stroke-dasharray:4 3; } #ssim-svg .small .bt { font-size:13px; }
  #ssim-svg .cap { font-size:13.5px; letter-spacing:.04em; fill:#333; } #ssim-svg .cap.small { font-size:12px; }
  #ssim-svg .lane { fill:none; stroke:#111; stroke-width:1.2; stroke-dasharray:2 5; }
  #ssim-svg .wire { fill:none; stroke:#111; stroke-width:1.4; }
  #ssim-svg .arr { marker-end:url(#ah); } #ssim-svg .ahp { fill:#111; }
  #ssim-svg .dotted, #ssim-svg .ref { stroke-dasharray:5 4; } #ssim-svg text.ref { font-size:12.5px; }
  #ssim-svg .runinfo { font-size:12.5px; }
  #ssim-svg.no-fast .fastb, #ssim-svg.no-fast .fastw, #ssim-svg.no-fast .fast-lane, #ssim-svg.no-fast text.fast { opacity:.22; }
  #ssim-svg.no-nrt .nrtb, #ssim-svg.no-nrt .nrtw, #ssim-svg.no-nrt .nrt-lane, #ssim-svg.no-nrt text.nrt,
  #ssim-svg.no-nrt .batchb, #ssim-svg.no-nrt .batchw, #ssim-svg.no-nrt .batch-lane, #ssim-svg.no-nrt text.batch,
  #ssim-svg.no-nrt .shared, #ssim-svg.no-nrt .chip { opacity:.22; }
  #ssim-svg .bx.off { opacity:.35; }
  #ssim-svg.nolog [data-id=log] rect { stroke-dasharray:6 4; fill:#f4f4f4; }
  #ssim-svg .dot circle { fill:#222; } #ssim-svg .dot.tyre circle { fill:#fff; stroke:#222; stroke-width:1.6; }
  #ssim-svg .dot.app path { fill:#5468b0; } #ssim-svg .dot.cdc rect { fill:#a94d77; } #ssim-svg .dot.lims path { fill:#b88a12; }
  #ssim-svg .dot.run circle { fill:#2f7d5b; } #ssim-svg .dot.bad path { stroke:#c0392b; stroke-width:2.2; }
  #ssim-svg .shard { fill:#fff; stroke:#111; stroke-width:1; } #ssim-svg .shardl { font-size:9px; fill:#666; font-family:var(--mono) !important; }
  #ssim-svg .bt { font-weight:700; }
  #ssim-svg .pptag rect { stroke:#111; stroke-width:1; } #ssim-svg .pptag.push rect { fill:#cfe9d9; } #ssim-svg .pptag.pull rect { fill:#d9e0f5; }
  #ssim-svg .pptag text { font-size:8.5px; font-weight:700; font-family:var(--mono) !important; }
  .ss-rule { border:var(--line); border-radius:var(--wob); padding:8px 14px; background:#fff; }
  #ssim-svg .ppb { font-size:10px; font-family:var(--mono) !important; fill:#555; letter-spacing:.05em; }
  td.pp.push { background:var(--mint-wash); font-weight:700; } td.pp.pull { background:var(--peri-wash); font-weight:700; }
  .ss-costs { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:10px; margin:10px 0; }
  .ss-costs div { border:var(--line); border-radius:var(--wob); padding:8px 12px; background:#fff; font-size:13.5px; color:var(--muted); }
  .ss-costs b { display:block; font-family:var(--mono); font-size:21px; color:var(--ink); }
  td.dropc { font-size:13px; color:var(--ink-soft); }
  td.n { text-align:right; font-family:var(--mono); }
  #ssim-svg .chip rect { fill:#fff; stroke:#111; stroke-width:1.2; }
  #ssim-svg .chip.complete rect { fill:#cfe9d9; } #ssim-svg .chip.provisional rect { fill:#ffe9b0; }
  #ssim-svg .chip.restated rect { fill:#d9e0f5; } #ssim-svg .chip.running rect { stroke-dasharray:4 3; }
  #ssim-svg .chip.empty { display:none; }
  .ss-lat { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:10px; margin:12px 0; }
  .ss-lat div { border:var(--line); border-radius:var(--wob); padding:8px 12px; background:#fff; font-size:14px; }
  .ss-lat b { display:block; font-family:var(--mono); font-size:20px; }
  .ss-note { border:1.5px dashed var(--ink); border-radius:var(--wob); padding:8px 14px; font-size:14.5px; background:var(--butter-wash); }
  .ss-feed { list-style:none; padding:0; margin:8px 0; max-height:260px; overflow:auto; border:var(--line); border-radius:var(--wob); background:#fff; }
  .ss-feed li { padding:6px 12px; border-bottom:1px dashed var(--rule-firm); font-size:14px; }
  .ss-feed li.bad { background:var(--rose-wash); }
  .ss-legend { font-size:13.5px; color:var(--muted); }
  .ss-tabs { display:flex; gap:8px; margin:10px 0 0; flex-wrap:wrap; }
  .ss-tabs a { border:1.5px solid var(--ink); border-radius:999px; padding:3px 14px; text-decoration:none; color:var(--ink); font-size:14.5px; background:#fff; }
  .ss-tabs a.on { background:var(--rose-wash); font-weight:600; }
</style>"""

BINDING_OPTS = [("aws-dbx", "AWS + Databricks (recommended)"), ("aws", "AWS only"),
                ("az-dbx", "Azure + Databricks, Power BI"), ("dbx-only", "Databricks only (not recommended)")]
ROUTE_OPTS = [("both", "Both: live screen and reports"), ("direct", "Direct to the screen only"), ("medallion", "Through the medallion only")]


def radios(name, opts, first):
    return "".join(f'<label><input type="radio" name="{name}" value="{v}"{" checked" if v == first else ""}> {E(t)}</label>' for v, t in opts)


def tabs(on):
    t = [("flow", "/learn/streaming/sim/", "1 · Data flow, hop by hop"), ("lanes", "/learn/streaming/sim/lanes/", "2 · Three lanes together")]
    return '<div class="ss-tabs">' + "".join(f'<a href="{u}" class="{"on" if k == on else ""}">{E(n)}</a>' for k, u, n in t) + '<a href="/learn/streaming/">The streaming guide</a></div>'


def ld(title, desc, url, qa, crumbs):
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    out = [{"@context": "https://schema.org", "@type": "LearningResource", "name": title, "description": desc, "url": url,
            "inLanguage": "en", "isAccessibleForFree": True, "dateModified": DATE, "learningResourceType": "simulation",
            "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
            "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
           {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items},
           {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity":
            [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}]
    return "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in out)


def shell(mode, h1, lede, ctl_extra, below, qa):
    speeds = ('<option value="10">1 s = 10 s</option><option value="60" selected>1 s = 1 min</option><option value="300">1 s = 5 min</option>'
              if mode == "flow" else
              '<option value="300" selected>1 s = 5 min</option><option value="900">1 s = 15 min</option><option value="1800">1 s = 30 min</option>')
    crumbs_html = '<p class="crumbs"><a href="/">Home</a> › <a href="/data-engineering/">Data engineering</a> › <a href="/learn/streaming/">Streaming</a> › Simulator</p>'
    return f"""{crumbs_html}
<p class="eyebrow" style="margin-top:22px">Data engineering · simulator · illustrative</p>
<h1>{E(h1)}</h1>
<p class="lede">{lede}</p>
{tabs(mode)}
<div class="ss-ctl">
<fieldset><legend>Binding</legend>{radios("ssim-binding", BINDING_OPTS, "aws-dbx")}</fieldset>
<fieldset><legend>Route to the screen</legend>{radios("ssim-route", ROUTE_OPTS, "both")}</fieldset>
{ctl_extra}
</div>
<p class="ss-note" id="ssim-note"></p>
<div class="ss-bar"><span>Simulated time</span><span class="clk" id="ssim-clock">--:--</span>
<label>Speed <select id="ssim-speed">{speeds}</select></label><button id="ssim-pause">Pause</button>
<span class="ss-legend">Dots move at viewing speed; the numbers run on simulated time.</span></div>
<div class="ss-stage" id="ssim" data-mode="{mode}"><svg id="ssim-svg" role="img" aria-label="{E(h1)}: animated diagram"></svg></div>
{below}
<h2>What it costs to run</h2>
<p>Rough monthly list prices for the production example (5 plants, 300 readings a second), US regions, 2025 to 2026. They change with the binding, the route and the sources you turn on. Licences for Power BI users are not included. The full model, with every input, is in the <a href="/learn/data-systems/platform/cost/calculator/#streaming-services">cost calculator</a>.</p>
<div id="ssim-cost"></div>
<h2>What just happened</h2>
<ul class="ss-feed" id="ssim-feed"></ul>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(qa)}</section>
<section id="next"><p class="eyebrow">Related</p><h2>Where it connects</h2>
<p><a href="/learn/streaming/">Streaming architecture on AWS and Databricks</a> explains every box and option. <a href="/learn/real-time-analytics/">Real-time analytics</a> covers push to the screen; <a href="/learn/data-systems/upstreams/questionnaire/">the source questionnaire</a> (group O) lists what to ask a streaming source; <a href="/simulators/">all simulators</a>.</p></section>
<script src="{JS}" defer></script>"""


def flow_page():
    url = f"{SITE}/learn/streaming/sim/"
    title = "Streaming simulator: IoT and database data, hop by hop"
    desc = "Watch IoT readings, app events, CDC and lab files flow through the fast lane and the medallion to a live screen and Power BI, on AWS, Azure or Databricks bindings."
    extra = """<fieldset><legend>Sources</legend>
<label><input type="checkbox" data-src="press"> Curing presses (IoT, 300/s)</label>
<label><input type="checkbox" data-src="tyre"> Connected tyres (IoT, 3,333/s)</label>
<label><input type="checkbox" data-src="app"> Dealer app events</label>
<label><input type="checkbox" data-src="cdc"> SAP and MES changes (CDC)</label>
<label><input type="checkbox" data-src="lims"> Lab result files (LIMS)</label></fieldset>
<fieldset><legend>Break something</legend>
<button data-inc="offline">Plant gateway offline 10 min</button><button data-inc="restart">Live processor restarts</button>
<button data-inc="dups">Duplicate burst</button><button data-inc="bad">Broken messages</button><button data-inc="skip">Skip next platform run</button></fieldset>"""
    below = """<div class="ss-lat">
<div>Fast lane: reading to live screen<b id="ssim-lat-fast">-</b>target ≤ 5 s</div>
<div>Platform lane: reading to silver<b id="ssim-lat-silver">-</b>target ≤ 20 min</div>
<div>Platform lane: hour to gold report<b id="ssim-lat-gold">-</b>target ≤ 75 min</div></div>
<p class="ss-legend">Dots: filled circle = press reading, ring = connected tyre, triangle = app event, square = database change, diamond = lab file, green = a platform run moving rows, red cross = broken message.</p>
<h2>Push or pull, chosen and dropped, hop by hop</h2>
<p>Every arrow in the diagram carries a tag: green <b>PUSH</b> or blue <b>PULL</b>.</p>
<div id="ssim-pp"></div>
<h2>What starts each step: continuous, schedule or file event</h2>
<p>Only the fast lane runs all the time. Everything in the platform lane runs, finishes and stops; what differs is what starts it.</p>
<div class="tw"><table class="t"><tr><th>Step</th><th>Started by</th><th>How it behaves</th><th>Verdict</th></tr>
<tr><td>Fast lane (Flink, push to screens)</td><td><b>Continuous</b>, always on</td><td>Reads every record as it arrives; seconds behind.</td><td><b>Pursue</b>: someone acts within seconds</td></tr>
<tr><td>Kinesis records to bronze and silver</td><td><b>Schedule</b>: a Lakeflow job every 15 min</td><td>Starts, reads everything new since its checkpoint ("available now"), writes bronze and silver, stops. Not continuous.</td><td><b>Pursue</b>: minutes are enough, and you pay only for run time</td></tr>
<tr><td>App event and database change files</td><td><b>Same 15-min schedule</b></td><td>Files wait in S3; their file events wait in a queue; Auto Loader inside the run reads every new file once.</td><td><b>Pursue</b></td></tr>
<tr><td>Lab result files (once an hour, at odd times)</td><td><b>File event</b>: Databricks file arrival trigger</td><td>Databricks checks the folder about once a minute and starts the job when new files appear; Auto Loader inside reads all of them. A burst of files is one run.</td><td><b>Pursue</b> for irregular drops</td></tr>
<tr><td>Gold hours</td><td><b>Schedule</b>: hourly at :15</td><td>Recomputes the hours that changed. Option: a table update trigger (start when silver changes) instead of the clock.</td><td><b>Pursue</b> the schedule; try the table trigger later</td></tr>
<tr><td>SAP and MES masters</td><td><b>Schedule</b>: nightly 01:00</td><td>Batch; refreshes dimensions and reference data for the fast lane.</td><td><b>Pursue</b></td></tr>
<tr><td>Continuous streaming tables for the platform lane</td><td>Continuous</td><td>Silver about 1 minute behind, but a cluster runs all day.</td><td><b>Drop</b>: about $700 to $1,500 a month for minutes nobody needs</td></tr>
<tr><td>One pipeline run per file (S3 event, Lambda, run with the file path)</td><td>File event, per file</td><td>A start-up per file; runs queue; a missed event loses a file.</td><td><b>Drop</b></td></tr>
</table></div>

<h2>What to try</h2>
<ol>
<li><b>Watch one 15-minute run.</b> Stream readings pile up at lake ingest; at :00, :15, :30 and :45 a run moves them to bronze and silver. At :15 each hour, gold builds the previous hour and the report updates.</li>
<li><b>Watch Kinesis.</b> Each reading enters one shard, chosen by its press key, so one press stays in order. Two readers read the stream on their own: the live lane a couple of seconds behind, the lake reader up to 15 minutes behind until the next run (normal). Turn on connected tyres and the stream grows from 2 to 6 shards; on Azure the same box is Event Hubs with partitions.</li>
<li><b>Watch the files.</b> App events (bundled by Firehose) and database changes (written by DMS) land as files in S3 and wait there; the 15-minute run reads them with Auto Loader, which remembers which files it has already loaded. A lab file is different: it lands once an hour at an odd time, so a Databricks file arrival trigger starts a load about a minute after it lands, instead of waiting for the next run. Either way the pipeline is never handed a single file; Auto Loader finds every new file itself.</li>
<li><b>Switch the route to "Direct".</b> The screen stays live, but database changes and lab files have nowhere to go, and no number is ever final.</li>
<li><b>Switch to "Through the medallion".</b> Every number is governed, but the screen is 15 to 75 minutes behind.</li>
<li><b>Take a plant gateway offline.</b> The live screen goes stale, the gateway buffers, and when it returns the late readings are counted and the gold hour is marked provisional.</li>
<li><b>Change the binding.</b> The roles stay the same; only the product in each box changes. On Azure, live Power BI goes through Fabric Real-Time Intelligence.</li>
</ol>"""
    qa = [("Is this simulator showing real measured numbers?", "No. It is an illustrative model of the design on the streaming guide: rates, run times and delays are typical values, not recordings."),
          ("Why does the platform lane wait for runs instead of streaming continuously?", "Running every 15 minutes and stopping costs a fraction of an always-on cluster and meets a minutes-level promise. Only the fast lane runs all the time, and it only does light work."),
          ("Can Power BI show real-time data?", "Power BI's old push and streaming datasets are being retired (no new ones after 31 Oct 2027). For seconds-level screens use Fabric Real-Time Intelligence or a live web board; for reports, Power BI reads gold with automatic page refresh.")]
    body = shell("flow", "Streaming simulator: data flow, hop by hop",
                 "IoT readings and ordinary sources (app events, database changes, lab files) travel from the source to a live screen in seconds, and through bronze, silver and gold to a Power BI report in minutes. Pick a binding and a route, then break things.",
                 extra, below, qa)
    crumbs = [("Data engineering", f"{SITE}/data-engineering/"), ("Streaming", f"{SITE}/learn/streaming/"), ("Simulator", url)]
    return wb.page(title, desc, url, body, CSS + ld(title, desc, url, qa, crumbs))


def lanes_page():
    url = f"{SITE}/learn/streaming/sim/lanes/"
    title = "Streaming simulator: fast, near real time and batch together"
    desc = "A simulated day of a tyre plant: the fast lane, 15-minute near real time and the nightly batch, where they meet, and how gold hours go provisional, complete and restated."
    extra = """<fieldset><legend>Break something</legend>
<button data-inc="offline">Plant offline 1 hour</button><button data-inc="batchfail">Nightly batch fails tonight</button>
<button data-inc="limslate">Lab results 6 h late</button><button data-inc="reset">Lab results back to 2 h</button></fieldset>"""
    below = """<p class="ss-legend">Gold hours: green = complete, yellow = provisional, waiting for an input (lab = lab results, dims = nightly dimensions, gap = plant readings), blue = restated (recomputed after late data), dashed = the hour still running.</p>
<h2>How the three lanes meet</h2>
<ol>
<li><b>At the source.</b> The fast lane and the platform lane each read the same raw events from the event log. Neither reads the other's output.</li>
<li><b>Reference data, upward.</b> Limits and the press list are copied from silver and gold into the fast lane on a schedule. The fast lane never calls the platform. Watch new press P-1501 show as "unknown press" until the nightly batch brings it into the press list.</li>
<li><b>In gold.</b> Near real time and batch are the same tables at different cadences. Hourly sensor facts join nightly dimensions and lab results that arrive hours later, so a gold hour is only as fresh as its slowest input.</li>
<li><b>On the screen.</b> The live screen, the hourly report and the daily report sit side by side. They show one dataset at three speeds, and they are never added together.</li>
</ol>
<h2>What to try</h2>
<ol>
<li><b>Let a few hours pass.</b> Each hour turns provisional at :15 and complete about two hours later, when its lab results land.</li>
<li><b>Fail tonight's batch.</b> Dimensions go stale, hours stay provisional, the daily report is late, and the new press stays unknown. The next night fixes all of it, and the waiting hours are restated.</li>
<li><b>Take the plant offline for an hour.</b> The live screen goes stale. When the buffer arrives, that gold hour is restated.</li>
</ol>"""
    qa = [("Do near real time and batch need separate pipelines?", "No. In this design they are the same pipeline and the same tables, run at different cadences: streams every 15 minutes, master data nightly. Only the seconds lane is separate."),
          ("Where do the fast lane and the batch lane meet?", "In four places: the shared raw event log, reference data copied up into the fast lane, gold (where streams join batch dimensions) and the screen, where live and final numbers sit side by side."),
          ("Can one dataset be in all three speeds?", "Yes: press readings appear on the live screen in seconds, in hourly gold in minutes and in the daily report the next morning. Only bronze, silver and gold are the record; the live copy expires.")]
    body = shell("lanes", "Streaming simulator: three lanes together",
                 "One simulated day at a tyre plant. Watch the fast lane, the 15-minute near-real-time lane and the nightly batch run side by side, meet in gold, and land on three screens with three freshness promises.",
                 extra, below, qa)
    crumbs = [("Data engineering", f"{SITE}/data-engineering/"), ("Streaming", f"{SITE}/learn/streaming/"), ("Three lanes", url)]
    return wb.page(title, desc, url, body, CSS + ld(title, desc, url, qa, crumbs))


def main():
    out = ROOT / "learn" / "streaming" / "sim"
    (out / "lanes").mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(flow_page())
    (out / "lanes" / "index.html").write_text(lanes_page())
    print("streaming sim ->", out, "(flow + lanes)")


if __name__ == "__main__":
    main()
