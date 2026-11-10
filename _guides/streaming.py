"""Streaming architecture on AWS and Databricks: one page at /learn/streaming/.

    python3 _guides/streaming.py      (then python3 _site/nav.py and python3 _site/seo.py)

Body lives in _guides/streaming_body.html (a public copy of the tyre-maker streaming design):
abstract roles first, then binding options per role with pros, cons and a verdict. Three speeds in
two lanes, Kappa through bronze, joins, SCD in silver, UI routes, DLT vs plain Structured Streaming,
Auto Loader and file triggers, S3, non-IoT sources, sizing, cost, replays, errors, the SLA report.
Prices are rough list prices; the page says so.
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
URL_PATH = "/learn/streaming/"
DATE = "2026-11-10"
TITLE = "Streaming architecture on AWS and Databricks"
DESC = ("Streaming for IoT and other sources on AWS and Databricks: seconds vs minutes, Kappa through bronze, "
        "joins, SCD, DLT or not, Auto Loader, S3, replays, errors, SLA report, cost.")

TOC = [("start", "Start here"), ("lesson", "What a stream is"), ("concept", "Abstract architecture"),
       ("sla", "Seconds or minutes"), ("speeds", "Three speeds: where they meet"), ("kappa", "Kappa, Lambda and us"),
       ("medallion", "Bronze, silver, gold, SCD"), ("joins", "Joining data in a stream"),
       ("ui", "To the UI: direct, fast layer, gold"), ("dbx", "DLT, Spark Streaming, Auto Loader"),
       ("s3", "Can S3 be used?"), ("noniot", "Streams that are not IoT"), ("physical", "Binding options per part"),
       ("stacks", "AWS-only vs AWS + Databricks"), ("perf", "Performance and sizing"), ("cost", "Cost"),
       ("replay", "Replays"), ("errors", "Error handling"), ("slareport", "End-to-end SLA report"),
       ("nfr", "Non-functional concerns"), ("decide", "Decisions to make"), ("notes", "Notes and sources")]

QA = [
    ("Should a 1 to 5 second streaming lane call Databricks?",
     "No. Keep it light and inside the streaming layer: validate, deduplicate, limit checks, one-minute windows, and "
     "small reference data copied in on a schedule. Databricks reads the raw stream separately and builds the numbers of record."),
    ("Where do SCD type 1 and type 2 happen in a streaming lakehouse?",
     "In silver, by dataset kind: master data as SCD type 2, transactions as type 1, sensor events append only. "
     "Gold builds dimensions from silver's history and joins facts as of event time."),
    ("DLT or plain Structured Streaming?",
     "Plain Structured Streaming in jobs as the default, because it is portable and fully testable; DLT's AUTO CDC "
     "is worth it for tables built from database changes, where out-of-order SCD2 is hardest to write by hand."),
    ("Can S3 be used as the stream?",
     "Not as the belt itself: one object per event is slow and costs a request each. S3 works well as minute-level "
     "landing for Auto Loader and as the long-term history that makes Kappa replays possible."),
    ("Should I trigger a DLT pipeline for each file that lands in S3?",
     "No. Use a file arrival trigger or a schedule and let Auto Loader pick up every new file, so a missed event never "
     "loses a file and ten files cost one run."),
]

CSS = C.CSS + """<style>
  .sx .lead { font-size:17px; color:var(--ink-soft); }
  .sx .muted { color:var(--muted); }
  .sx .box { border:var(--line); border-radius:var(--wob); padding:12px 16px; margin:14px 0; background:#fff; }
  .sx .box.do { background:var(--butter-wash); } .sx .box.warn { background:var(--butter-wash); border-style:dashed; }
  .sx .grid { display:grid; gap:12px; } .sx .g2 { grid-template-columns:1fr 1fr; } .sx .g3 { grid-template-columns:repeat(3,1fr); }
  .sx .card { border:var(--line); border-radius:var(--wob); padding:10px 14px; background:#fff; }
  .sx .card h4 { margin:0 0 4px; font-family:var(--hand); font-weight:400; font-size:21px; }
  .sx .tbl { overflow-x:auto; margin:8px 0 18px; }
  .sx table { border-collapse:collapse; width:100%; font-size:14.5px; }
  .sx th, .sx td { text-align:left; padding:7px 9px; border-bottom:1.5px dashed var(--rule-firm); vertical-align:top; }
  .sx th { font-size:11.5px; letter-spacing:.08em; text-transform:uppercase; color:var(--faint); }
  .sx td.v { font-weight:700; background:var(--mint-wash); } .sx td.v.drop { font-weight:400; background:var(--rose-wash); }
  .sx code { font-family:var(--mono); font-size:.84em; background:var(--surface-2); padding:1px 4px; border-radius:3px; }
  .sx .fig { border:var(--line); border-radius:var(--wob); padding:12px 14px; margin:16px 0; background:#fff; overflow-x:auto; }
  .sx .fig svg { width:100%; min-width:640px; height:auto; display:block; } .sx .fig text { font-family:var(--hand); }
  .sx .fig p { font-size:13.5px; color:var(--muted); margin:6px 0 0; }
  @media (max-width:760px) { .sx .g2, .sx .g3 { grid-template-columns:1fr; } }
</style>"""


def ld(url):
    crumbs = [("Learn", f"{SITE}/learn/"), ("Data engineering", f"{SITE}/data-engineering/"), ("Streaming", url)]
    out = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": TITLE, "description": DESC, "url": url,
            "inLanguage": "en", "isAccessibleForFree": True, "dateModified": DATE,
            "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
            "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
           {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement":
            [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]},
           {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity":
            [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in QA]}]
    return "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in out)


def page():
    url = f"{SITE}{URL_PATH}"
    body = (Path(__file__).parent / "streaming_body.html").read_text()
    toc = "".join(f'<li><a href="#{a}">{E(t)}</a></li>' for a, t in TOC)
    full = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/data-engineering/">Data engineering</a> › Streaming</p>
<p class="eyebrow" style="margin-top:22px">Data engineering · free guide · one page</p>
<h1>{E(TITLE)}</h1>
<p class="lede">IoT and ordinary sources, seconds and minutes, AWS alone or with Databricks: the architecture as roles first, then the options for every part with pros, cons and a verdict.</p>
<nav class="toc"><b>On this page</b><ol>{toc}</ol></nav>
<div class="sx">{body}</div>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(QA)}</section>
<section id="next"><p class="eyebrow">Related</p><h2>Where it connects</h2>
<p><a href="/learn/real-time-analytics/">Real-time analytics, drawn simply</a> · <a href="/learn/medallion-architecture/">Medallion architecture</a> · <a href="/learn/data-platform-architecture/aws-databricks/">Data platform on AWS + Databricks</a> · <a href="/data-engineering/">All data engineering</a></p></section>"""
    return wb.page(TITLE, DESC, url, full, CSS + ld(url))


def main():
    out = ROOT / "learn" / "streaming"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("streaming ->", out / "index.html")


if __name__ == "__main__":
    main()
