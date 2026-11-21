"""Row-oriented vs column-oriented: file formats and databases. One page at /learn/row-vs-column-storage/.

    python3 _guides/row_column_storage.py      (then python3 _site/nav.py and python3 _site/seo.py)

Body text lives in _guides/row_column_storage/body.html (s1..s10); drawings are built here. The measured demo is
_guides/row_column_storage/demo.py (standard library only); its code is pasted into the page by the {{DEMO}} placeholder.
General knowledge, not re-checked against vendor docs; see the callout in s10.
"""
import json
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "_paths"))
import bi_choice as B  # noqa: E402  (drawing kit + CSS)
import components as C  # noqa: E402

wb = C.wb
SITE = wb.SITE
SLUG = "row-vs-column-storage"
BASE = f"/learn/{SLUG}/"
DATE = "2026-11-21"
DIR = Path(__file__).parent / "row_column_storage"
BODY = DIR / "body.html"
DEMO = DIR / "demo.py"
bx, ar, svg, fig, t = B.bx, B.ar, B.svg, B.fig, B.t

TITLE = "Row-oriented vs column-oriented: file formats and databases, explained"
DESC = ("What row-oriented and column-oriented storage mean, drawn on one tiny table: how CSV, Avro, Parquet and ORC lay out bytes, how PostgreSQL and ClickHouse "
        "store tables, why analytics reads fewer bytes from columns, why single-row updates are awkward, with a measured demo, a verdict for each scenario and how it ties to Delta and Iceberg.")

QA = [
    ("Is Parquet row-oriented or column-oriented?", "Column-oriented. A Parquet file is split into row groups, and inside each group every column is stored as its own chunk, so a reader can load only the columns a query needs."),
    ("Is a column database the same as a column file format?", "No. A file format only says how bytes are laid out in a file. A database is an engine with storage, indexes, transactions and a query planner. ClickHouse is a column database with its own storage layout; Databricks SQL is an engine that reads column files such as Parquet."),
    ("Why are updates slow in column stores?", "A row's values are scattered across column chunks, and the files are written once and not edited in place. Changing one row means writing new data or marking old rows deleted, then merging later. Column systems prefer batched inserts."),
    ("Which should I use for an application with users and orders?", "A row-oriented database such as PostgreSQL, because the application reads and writes whole records one at a time. Copy the data to a column store for reporting."),
]

RELATED = [
    ("How reads and writes work in Delta and Spark", "/learn/how-delta-works/"),
    ("Delta vs Iceberg", "/learn/delta-vs-iceberg/"),
    ("Who maintains your tables", "/learn/table-maintenance/"),
    ("Table, view, materialized view or metric view", "/learn/table-view-materialized-view-metric-view/"),
    ("Databricks materialized views", "/learn/materialized-views/"),
    ("Medallion architecture", "/learn/medallion-architecture/"),
    ("Streaming architecture", "/learn/streaming/"),
]


def d_layout():
    i = t(130, 24, "The table", 16, "middle")
    heads = ["id", "region", "amount"]
    data = [["1", "North", "50"], ["2", "South", "20"], ["3", "North", "70"]]
    for c, h in enumerate(heads):
        i += bx(10 + c * 82, 36, 80, 30, [h], "l", 14)
    for r, row in enumerate(data):
        for c, v in enumerate(row):
            i += bx(10 + c * 82, 68 + r * 32, 80, 30, [v], "w", 14)
    i += t(580, 24, "Row layout on disk: one whole record, then the next", 16, "middle")
    fills_r = ["g"] * 3 + ["b"] * 3 + ["y"] * 3
    vals_r = ["1", "North", "50", "2", "South", "20", "3", "North", "70"]
    for k, (v, f) in enumerate(zip(vals_r, fills_r)):
        i += bx(270 + k * 78, 36, 74, 40, [v], f, 14)
    i += t(580, 112, "Neighbours on disk are the values of one record.", 14, "middle")
    i += t(580, 160, "Column layout on disk: one whole column, then the next", 16, "middle")
    vals_c = ["1", "2", "3", "North", "South", "North", "50", "20", "70"]
    for k, (v, f) in enumerate(zip(vals_c, fills_r)):
        i += bx(270 + k * 78, 172, 74, 40, [v], f, 14)
    i += t(580, 248, "Neighbours on disk are the values of one column.", 14, "middle")
    i += t(500, 285, "Same nine values. Only the order they are stored in changes.", 15, "middle")
    return svg(1000, 300, "One table of three rows with columns id, region and amount. In the row layout the nine values are stored record by record: 1 North 50, then 2 South 20, then 3 North 70. In the column layout they are stored column by column: 1 2 3, then North South North, then 50 20 70. The same nine values in a different order.", i)


def d_read():
    heads = ["id", "region", "channel", "qty", "amount"]
    i = t(180, 22, "Row store: reads every cell", 16, "middle") + t(700, 22, "Column store: reads only the columns it needs", 16, "middle")
    for gx, mode in [(20, "row"), (540, "col")]:
        for c, h in enumerate(heads):
            need = h in ("region", "amount")
            f = "r" if mode == "row" else ("g" if need else "w")
            i += bx(gx + c * 62, 36, 60, 30, [h], f, 13, dash=(mode == "col" and not need))
        for r in range(4):
            for c, h in enumerate(heads):
                need = h in ("region", "amount")
                f = "r" if mode == "row" else ("g" if need else "w")
                i += bx(gx + c * 62, 68 + r * 32, 60, 30, ["..."], f, 13, dash=(mode == "col" and not need))
    i += t(500, 235, "Question: SUM(amount) grouped by region", 16, "middle")
    i += t(500, 260, "It needs 2 of 5 columns. A column store can leave the other 3 on disk.", 15, "middle")
    return svg(1000, 275, "The query sum of amount grouped by region needs two of five columns. A row store reads every cell of every row, shown as five red columns. A column store reads only the region and amount columns, shown in green, and skips id, channel and qty.", i)


def d_stitch():
    i = t(80, 22, "position", 14, "middle")
    cols = [("id", ["1", "2", "3", "4"]), ("region", ["North", "South", "North", "East"]), ("amount", ["50", "20", "70", "10"])]
    for p in range(4):
        i += t(185 + p * 100, 22, str(p), 15, "middle")
    for r, (name, vals) in enumerate(cols):
        y = 36 + r * 48
        i += t(120, y + 26, name, 15, "end")
        for p, v in enumerate(vals):
            hit = p in (0, 2) and name != "id"
            i += bx(140 + p * 100, y, 90, 38, [v], "g" if hit else "w", 15)
    for p in (0, 2):
        i += f'<rect x="{136 + p * 100}" y="32" width="98" height="152" rx="8" fill="none" stroke="#111" stroke-width="1.6" stroke-dasharray="6 4"/>'
    i += t(185, 204, "row 0", 14, "middle") + t(385, 204, "row 2", 14, "middle")
    i += bx(140, 236, 190, 44, ["North, 50"], "y", 16) + bx(350, 236, 190, 44, ["North, 70"], "y", 16)
    i += ar(185, 210, 235, 234) + ar(385, 210, 445, 234)
    i += t(570, 50, "Question: region and amount where amount > 40", 15)
    i += t(570, 92, "1  Scan only the amount column.", 15) + t(570, 114, "    Positions 0 and 2 pass (50 and 70).", 14)
    i += t(570, 150, "2  Read region at positions 0 and 2.", 15) + t(570, 172, "    The id column is never touched.", 14)
    i += t(570, 208, "3  Stitch by position:", 15) + t(570, 230, "    the value at position p in each column", 14) + t(570, 250, "    belongs to the same row.", 14)
    i += t(500, 310, "A row is not stored. It is rebuilt from the same position in every column.", 16, "middle")
    return svg(1000, 325, "Four values per column stored in the same order. A query for region and amount where amount is over 40 scans the amount column, finds positions 0 and 2, reads the region values at those positions, and stitches them into the rows North 50 and North 70. The id column is never read. A row is rebuilt from the same position in every column.", i)


def render():
    url = f"{SITE}{BASE}"
    rel = " · ".join(f'<a href="{u}">{E(n)}</a>' for n, u in RELATED)
    demo = E(DEMO.read_text())
    body = f"""<div class="bi"><p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › Row vs column storage</p>
<p class="eyebrow" style="margin-top:22px">Data foundations · storage</p>
<h1>{E(TITLE)}</h1><p class="lede">{E(DESC)}</p>
{BODY.read_text().replace("{{LAYOUT}}", fig(d_layout(), "Same nine values, two orders.")).replace("{{READ}}", fig(d_read(), "A column store skips the columns the query does not use.")).replace("{{STITCH}}", fig(d_stitch(), "Dashed boxes are the rows rebuilt from positions 0 and 2.")).replace("{{DEMO}}", demo)}
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(QA)}</section>
<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2><p>Related on this site: {rel}</p><p><a href="/data-engineering/">All data engineering</a></p></section></div>"""
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": TITLE, "description": DESC, "url": url, "inLanguage": "en",
           "isAccessibleForFree": True, "dateModified": DATE, "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in QA]}]
    head = B.CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return wb.page(TITLE, DESC, url, body, head)


def build_all():
    return {f"learn/{SLUG}/index.html": render()}


def main():
    for rel, html in build_all().items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html)
        print("row vs column ->", path)


if __name__ == "__main__":
    main()
