"""How reads and writes work in Delta Lake and Spark: a section of 11 pages under /learn/how-delta-works/.

    python3 _guides/how_delta_works.py      (then python3 _site/nav.py and python3 _site/seo.py)

Every number on these pages comes from a real run on this author's laptop: Apache Spark 3.5.1 with open-source Delta Lake 3.2.0,
local mode with 2 cores. The code is in _guides/how_delta_works/lab/ and the raw results in _guides/how_delta_works/results/*.json.
Page text pulls numbers from those files through the R dict, so a page cannot drift from its measurement.
Things that only exist on Databricks (Photon, predictive I/O, liquid clustering, query profile) were NOT measured and are marked.
Page content lives in how_delta_works_pages.py; this file holds the shell, helpers and the build.
"""
import json
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "_paths"))
import bi_choice as B  # noqa: E402  (drawing kit + CSS)
import components as C  # noqa: E402

wb = C.wb
SITE = wb.SITE
BASE = "/learn/how-delta-works/"
DATE = "2026-11-21"
RES = HERE / "how_delta_works" / "results"
R = {p.stem: json.loads(p.read_text()) for p in RES.glob("*.json")}
bx, ar, svg, fig, t = B.bx, B.ar, B.svg, B.fig, B.t
FILLS = B.FILLS


# ------------------------------------------------------------------ number helpers
def n(x):
    return f"{int(x):,}"


def sz(b):
    b = float(b)
    if b >= 1e6:
        return f"{b / 1e6:.1f} MB"
    if b >= 1e3:
        return f"{b / 1e3:.0f} KB"
    return f"{int(b)} B"


def sec(x):
    return f"{float(x):.2f} s"


def pct(a, b):
    return f"{100 * a / b:.0f}%"


# ------------------------------------------------------------------ drawing helpers
def hbars(rows, x0=10, y0=10, label_w=250, bar_w=430, row_h=34, fill="b", note_x=None):
    """rows: (label, value, text, fill?) -> horizontal bars scaled to the max value; returns svg inner and height"""
    mx = max(v for _, v, *_ in rows) or 1
    out, y = "", y0
    for r in rows:
        label, v, text = r[0], r[1], r[2]
        f = r[3] if len(r) > 3 else fill
        w = max(3, bar_w * v / mx)
        out += t(x0 + label_w - 8, y + 20, label, 14, "end")
        out += f'<rect x="{x0 + label_w}" y="{y + 4}" width="{w:.0f}" height="{row_h - 12}" rx="5" fill="{FILLS[f]}" stroke="#111" stroke-width="1.3"/>'
        out += t(x0 + label_w + w + 8, y + 20, text, 14)
        y += row_h
    return out, y


def strip(x, y, vals, w, h, fills, size=13):
    out = ""
    for k, (v, f) in enumerate(zip(vals, fills)):
        out += bx(x + k * w, y, w - 3, h, [str(v)], f, size)
    return out


def code_box(x, y, w, lines, size=13, fill="w", line_h=19):
    h = 12 + line_h * len(lines)
    out = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{FILLS[fill]}" stroke="#111" stroke-width="1.4"/>'
    for i, ln in enumerate(lines):
        out += f'<text x="{x + 10}" y="{y + 20 + i * line_h}" font-size="{size}" xml:space="preserve" style="font-family:var(--mono);white-space:pre">{E(ln)}</text>'
    return out, h


# ------------------------------------------------------------------ section skeleton
CSS = B.CSS + """<style>
  .path { display:flex; flex-wrap:wrap; gap:8px; margin:16px 0 6px; }
  .path a { border:1.5px solid var(--ink); border-radius:999px; padding:3px 12px; background:#fff; color:var(--ink); text-decoration:none; font-size:14px; }
  .path a.on { background:var(--rose-wash); font-weight:700; }
  .bi .box { border:var(--line); border-radius:var(--wob); padding:10px 16px; margin:14px 0; background:var(--butter-wash); }
  .bi pre.code { font-family:var(--mono); font-size:12.5px; line-height:1.5; background:var(--surface-2); border:1px solid var(--rule); border-radius:8px; padding:12px 14px; overflow-x:auto; }
  .bi .fig text.mono { font-family:var(--mono); }
  .bi .steps { counter-reset:s; list-style:none; padding-left:0; } .bi .steps > li { counter-increment:s; border:var(--line); border-radius:var(--wob); padding:10px 16px 10px 52px; margin:10px 0; position:relative; background:#fff; }
  .bi .steps > li::before { content:counter(s); position:absolute; left:14px; top:9px; width:26px; height:26px; border:1.5px solid var(--ink); border-radius:50%; text-align:center; line-height:24px; font-family:var(--hand); background:var(--butter-wash); }
  .bi .real { border-left:4px solid #4a9a6a; background:#f3faf5; padding:8px 14px; margin:12px 0; border-radius:6px; font-size:14.5px; }
</style>"""

PAGES = [  # slug, short label, title, description
    ("", "Start here", "How reads and writes work in Delta Lake and Spark",
     "A picture-first guide, from zero to advanced, to what Spark and Delta Lake do when you read or write a table: files and the delta log, the read path, file layout, joins, shuffles, the driver, caching, Python and the JVM, Photon, query plans, the write paths, and why ClickHouse reads are fast."),
    ("files-on-disk/", "1 · Files", "What is on disk: Parquet files and the delta log",
     "A Delta table is a folder of Parquet files plus a transaction log. See a real log (the add action with its min and max statistics, the commit files, a checkpoint) and the real inside of a Parquet file: row groups, column chunks, encodings and the footer."),
    ("read-path/", "2 · Read path", "How a read works: one big table, six kinds of query",
     "Follow a query from SQL to bytes. Six queries on one table (select star, two columns, a sorted column, a random column, a column beyond the 32 statistics columns, a Z-ordered column) with measured files read and bytes read, how the driver scans the log, and why count star never touches the data."),
    ("layout/", "3 · Layout", "Layout: small files, min and max, columns and compression",
     "Why the way files are organised decides how fast reads are: the small file problem measured, overlapping min and max ranges, columnar storage and compression with real chunk sizes, and OPTIMIZE, Z-order, liquid clustering and partitioning."),
    ("joins/", "4 · Joins", "Joins: big with small, big with big, and how layout helps",
     "The join strategies Spark picks and why: broadcast hash, sort-merge, what AQE changes at run time, dynamic partition pruning that cut files read from 22 to 6, skew, and how organising files by the join key speeds joins up. Measured shuffle bytes for each."),
    ("inside-spark/", "5 · Inside Spark", "Inside Spark: narrow and wide, shuffles, the driver and caching",
     "Narrow and wide transformations, the kinds of shuffle (hash, range, round-robin, single, broadcast), when work actually runs, what travels to the driver for count, take, show, collect and write, and what caching does to a select, with measured bytes."),
    ("python-and-jvm/", "6 · Python and JVM", "PySpark: what runs in Python, what runs in the JVM",
     "How PySpark really works: the Python process, the Py4J bridge to the JVM, what the DataFrame API builds, what a Python UDF costs (measured), what collect converts, and why built-in functions are fast. Real process ids and timings."),
    ("photon/", "7 · Photon", "Photon: how it speeds up queries and when it does not",
     "What the Photon engine replaces, why a vectorised C++ engine beats row-at-a-time JVM execution, which operators it covers, where it cannot help, and how to see it in a plan. Written from the Databricks docs; Photon cannot run locally so it was not measured."),
    ("plan-and-ui/", "8 · Plan and UI", "Query plan, Spark UI and query profile: what each shows and when to look",
     "Read a real query plan bottom-up, then learn what the Spark UI tabs, the Databricks query profile, DESCRIBE DETAIL, DESCRIBE HISTORY and the delta log each tell you, with a symptom-to-tool table."),
    ("write-path/", "9 · Write path", "How writes work under the hood: append, overwrite, update, delete, merge",
     "What Delta does for each write: new files and a commit in the log. Real logs and counters for append, update, delete, delete with deletion vectors, merge, optimize and overwrite, why rewriting 10,000 rows to change 11 happens, and how time travel keeps old files."),
    ("clickhouse/", "10 · ClickHouse", "Why reads are so fast in ClickHouse",
     "How ClickHouse reads data: sorted parts, one file per column, the sparse primary index with 8,192-row granules, skipping indexes, codecs, vectorised parallel execution, and how that compares with Delta and Parquet, from the ClickHouse docs."),
]
LABEL = {s: lab for s, lab, _, _ in PAGES}


def path_nav(cur):
    return '<nav class="path" aria-label="Pages in this section">' + "".join(
        f'<a href="{BASE}{s}" class="{"on" if s == cur else ""}">{E(lab)}</a>' for s, lab, _, _ in PAGES) + "</nav>"


def nextprev(cur):
    i = [s for s, *_ in PAGES].index(cur)
    prev = f'<a href="{BASE}{PAGES[i - 1][0]}">← {E(PAGES[i - 1][1])}</a>' if i > 0 else ""
    nxt = f'<a href="{BASE}{PAGES[i + 1][0]}">{E(PAGES[i + 1][1])} →</a>' if i + 1 < len(PAGES) else ""
    return f'<p class="cap" style="display:flex;justify-content:space-between;margin-top:24px">{prev}<span></span>{nxt}</p>'


def section(id_, eyebrow, h2, inner):
    return f'<section id="{id_}"><p class="eyebrow">{E(eyebrow)}</p><h2>{E(h2)}</h2>{inner}</section>'


def real(text):
    return f'<div class="real"><b>Measured.</b> {text}</div>'


def render(slug):
    import how_delta_works_pages as P
    _, label, title, desc = next(p for p in PAGES if p[0] == slug)
    body, qa = getattr(P, "page_" + (slug.strip("/").replace("-", "_") or "start"))()
    url = f"{SITE}{BASE}{slug}"
    crumbs = f'<a href="/">Home</a> › <a href="/learn/">Learn</a> › ' + (f'<a href="{BASE}">How reads and writes work</a> › {E(label)}' if slug else "How reads and writes work")
    faq = f'<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(qa)}</section>'
    html_body = f"""<div class="bi"><p class="crumbs">{crumbs}</p>
<p class="eyebrow" style="margin-top:22px">Delta Lake and Spark · from zero to advanced</p>
<h1>{E(title)}</h1><p class="lede">{E(desc)}</p>{path_nav(slug)}
{body}
{faq}
{nextprev(slug)}</div>"""
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": title, "description": desc, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}]
    head = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(title, desc, url, html_body, head)


def build_all():
    return {f"learn/how-delta-works/{s}index.html": render(s) for s, *_ in PAGES}


def main():
    for rel, html in build_all().items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html)
        print("how delta works ->", path)


if __name__ == "__main__":
    main()
