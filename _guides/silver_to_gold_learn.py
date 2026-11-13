"""Learn-from-zero parts of /learn/silver-to-gold/ (imported by silver_to_gold.py).

Part A: one tiny tyre company followed through two nightly runs, a crash and a careless join, with pictures and the
        real tables. Part B: the six kinds of fact, why there are six, and each one as reader, processor, writer.
Part C: can this hop be a Databricks declarative pipeline, with pros, cons and verdicts.

Every number and code block comes from _guides/code/silver_to_gold/ (run 13 Nov 2026 on Spark 3.5.1 + Delta 3.2.0):
results.json is written by e2e.py, and the code is read straight from builds.py and harness.py.
The Lakeflow sketch in Part C was written for the page and has NOT been run on Databricks; the page says so.
"""
import ast
import json
import sys
from html import escape as E
from pathlib import Path

HERE = Path(__file__).parent
CODE = HERE / "code" / "silver_to_gold"
sys.path.insert(0, str(CODE))
import components as C  # noqa: E402
import data as X  # noqa: E402
from bi_choice import ar, bx, svg, t, vtable  # noqa: E402
from gold_harness_spec import fig  # noqa: E402

R = json.loads((CODE / "results.json").read_text())

EXTRA_CSS = """<style>
  .gh tr.hl td { background:#fff6dc; } .gh tr.dim td { color:#8a8a8a; }
  .gh .part { border-top:3px solid var(--ink); margin-top:44px; padding-top:8px; }
  .gh .kind { border:var(--line); border-radius:var(--wob); padding:4px 18px 10px; margin:22px 0; background:#fff; }
  .gh .rpw { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin:10px 0; }
  .gh .rpw div { border:1.5px solid var(--ink); border-radius:10px; padding:8px 12px; font-size:14.5px; }
  .gh .rpw b { display:block; margin-bottom:4px; }
  .gh .rpw .r { background:#eef3fb; } .gh .rpw .p { background:#eaf6ef; } .gh .rpw .w { background:#fff6dc; }
  @media (max-width:760px){ .gh .rpw { grid-template-columns:1fr; } }
  .gh .start { border:var(--line); border-radius:var(--wob); padding:10px 18px; margin:16px 0; background:#eaf6ef; }
  .gh details.code summary { cursor:pointer; font-weight:700; margin:10px 0; }
</style>"""


# ------------------------------------------------------------------ helpers
def src(file, *names):
    """The exact source of named functions or assignments from a tested file."""
    text = (CODE / file).read_text()
    out = []
    for node in ast.parse(text).body:
        n = getattr(node, "name", None) or (node.targets[0].id if isinstance(node, ast.Assign) else None)
        if n in names:
            out.append(ast.get_source_segment(text, node))
    return "\n\n\n".join(out)


def htable(head, rows, hl=(), dim=()):
    h = "".join(f"<th>{E(str(x))}</th>" for x in head)
    body = ""
    for i, row in enumerate(rows):
        cls = ' class="hl"' if i in hl else (' class="dim"' if i in dim else "")
        body += f"<tr{cls}>" + "".join(f"<td>{E('' if c is None else str(c))}</td>" for c in row) + "</tr>"
    return f'<div class="tw"><table class="t"><tr>{h}</tr>{body}</table></div>'


def nd(d):
    return f"{d.day} Nov" if hasattr(d, "day") else (f"{int(d[8:10])} Nov" if isinstance(d, str) and d[:4] == "2026" else d)


FCOLS = ["line_id", "dealer_id", "promised_date", "qty_ordered", "qty_delivered", "on_time", "in_full", "otif", "dealer_key", "_is_complete", "_run_id"]


def fact_rows(label):
    return [[nd(r[c]) if c == "promised_date" else r[c] for c in FCOLS] for r in R["fact"][label]]


def run(rid):
    return next(r for r in R["runs"] if r["run"] == rid)


# ------------------------------------------------------------------ drawings
def d_story():
    i = ""
    for k, s in enumerate(["1. sources", "2. silver", "3. the nightly run", "4. gold", "5. the answer"]):
        i += t([85, 295, 545, 780, 930][k], 22, s, 14, "middle")
    src_ = [["order system"], ["two warehouses", "WH-A and WH-B"], ["dealer list"]]
    sil = [["order_lines"], ["deliveries"], ["dealers", "(with history)"]]
    for k in range(3):
        y = 40 + k * 76
        i += bx(10, y, 150, 60, src_[k], "w", 14) + ar(160, y + 30, 218, y + 30)
        i += bx(220, y, 150, 60, sil[k], "b", 14) + ar(370, y + 30, 428, 136)
    i += bx(430, 40, 230, 212, [""], "y", 14) + t(545, 70, "the harness", 16, "middle")
    for k, (s, f) in enumerate([("reader: what changed?", "b"), ("processor: the OTIF rule", "g"), ("writer: replace windows", "y")]):
        i += bx(450, 88 + k * 52, 190, 40, [s], f, 13)
    i += ar(660, 120, 708, 96) + ar(660, 170, 708, 190)
    i += bx(710, 66, 140, 56, ["fact_otif", "one row per line"], "g", 14) + bx(710, 162, 140, 56, ["dim_dealer", "one row per version"], "g", 13)
    i += ar(850, 140, 878, 140) + bx(880, 96, 110, 90, ["on time", "and in full,", "% per region", "per day"], "w", 13)
    return svg(1000, 262, "The tyre company's story. Three sources (order system, two warehouses, dealer list) land in three "
                          "silver tables: order_lines, deliveries and dealers with history. Each night the harness runs a "
                          "reader, a processor with the OTIF rule, and a writer that replaces windows. It produces the gold "
                          "fact_otif, one row per order line, and dim_dealer, one row per dealer version, which answer: what "
                          "percent of lines were delivered on time and in full, per region per day.", i)


def d_night():
    steps = [["bookmarks:", "where did I stop?"], ["changed rows", "since then"], ["which windows", "(days) they touch"],
             ["build: the", "business rule"], ["keys as of", "the event date"], ["check and", "count rows"], ["replace windows,", "move bookmark"]]
    i = ""
    for k, s in enumerate(steps):
        x = 10 + k * 140
        i += f'<circle cx="{x + 64}" cy="22" r="14" fill="#fff" stroke="#111" stroke-width="1.5"/>' + t(x + 64, 27, str(k + 1), 14, "middle")
        i += bx(x, 44, 128, 66, s, "g" if k == 3 else "w", 13)
        if k:
            i += ar(x - 12, 77, x - 1, 77)
    for x0, x1, s, f in [(10, 418, "READER (generic)", "b"), (430, 558, "PROCESSOR (per fact)", "g"),
                         (570, 838, "HARNESS RULES (generic)", "l"), (850, 978, "WRITER (generic)", "y")]:
        i += bx(x0, 130, x1 - x0, 34, [s], f, 13)
    return svg(1000, 176, "A nightly run in seven numbered steps. 1 read the bookmarks, 2 read rows changed since then, 3 work "
                          "out which days they touch, 4 run the business rule, 5 look up keys as of the event date, 6 check "
                          "and count rows, 7 replace the windows and move the bookmark. Steps 1 to 3 are the reader, step 4 the "
                          "processor, steps 5 and 6 the harness rules, step 7 the writer. Only step 4 is written per fact.", i)


def d_bookmark():
    i = '<path d="M30,90 L970,90" stroke="#111" stroke-width="1.5" marker-end="url(#bia)"/>' + t(30, 116, "change number (_seq)", 13)
    i += '<circle cx="90" cy="90" r="9" fill="#eef3fb" stroke="#111" stroke-width="1.3"/>' + t(90, 140, "1001 (L0)", 13, "middle")
    i += '<path d="M150,40 L150,135" stroke="#111" stroke-width="2"/>' + t(150, 32, "watermark = 1001", 13, "middle")
    for k in range(6):
        x = 400 + k * 58
        i += f'<circle cx="{x}" cy="90" r="9" fill="#eaf6ef" stroke="#111" stroke-width="1.3"/>' + t(x, 124, f"{1041 + k} (L{k + 1})", 12, "middle")
    i += '<path d="M730,40 L730,135" stroke="#111" stroke-width="2" stroke-dasharray="5 4"/>' + t(730, 32, "high mark = 1046, fixed at start", 13, "middle")
    i += '<circle cx="850" cy="90" r="9" fill="#fff" stroke="#111" stroke-width="1.3" stroke-dasharray="3 3"/>' + t(850, 124, "1047", 13, "middle")
    i += t(850, 152, "arrives during the run:", 12, "middle") + t(850, 168, "waits for the next night", 12, "middle")
    i += t(440, 160, "run r1 reads only the rows between the two lines: 1002 to 1046", 14, "middle")
    return svg(1000, 182, "Bookmarks on order_lines for run r1. Changes are numbered. The watermark sits at 1001, the last change "
                          "the previous run used. The high mark is fixed at 1046 when the run starts. Run r1 reads only 1002 to "
                          "1046, which are the six new lines L1 to L6. Change 1047 arrives during the run and waits for the next night.", i)


def d_windows():
    i = ""
    days = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    note = {5: ["built by r0,", "untouched"], 10: ["L1, L2", "X1, X2"], 11: ["L3, X3"], 13: ["L4, L5, L6", "X4, X5"]}
    for k, d in enumerate(days):
        x = 20 + k * 97
        f = "g" if d in (10, 11, 13) else ("b" if d == 5 else "w")
        i += bx(x, 30, 86, 60, [f"{d} Nov"], f, 15)
        for j, s in enumerate(note.get(d, [])):
            i += t(x + 43, 114 + j * 17, s, 12, "middle")
    i += t(500, 170, "Delivery X2 happened on 11 Nov but lands in the 10 Nov window: a delivery belongs to its order line's promised date.", 13, "middle")
    i += t(500, 192, "Rebuild only the green days, whole. Every other day of history is left alone.", 13, "middle")
    return svg(1000, 204, "Which windows run r1 rebuilds. Ten days from 5 to 14 November. The changed order lines and deliveries "
                          "fall on 10 November (L1, L2, X1, X2), 11 November (L3, X3) and 13 November (L4, L5, L6, X4, X5); "
                          "those three days are rebuilt whole. 5 November was built by run r0 and is untouched. Delivery X2 "
                          "happened on 11 November but belongs to 10 November, its order line's promised date.", i)


def d_asof():
    def x(day):
        return 80 + (day - 8) * 120
    i = t(20, 72, "D7", 15) + t(20, 156, "D9", 15)
    i += bx(x(8), 50, x(12) - x(8), 36, ["key 2: Patel Motors, North"], "b", 13)
    i += bx(x(12), 50, x(15) - x(12), 36, ["key 3: Patel Motors, West"], "y", 13)
    i += bx(x(8), 136, x(15) - x(8), 36, ["night 1: not in the dealer list yet; night 2: arrives as key 4, South"], "w", 13, dash=True)
    for d in range(8, 16):
        i += t(x(d), 214, f"{d} Nov", 12, "middle")
    i += '<path d="M80,198 L940,198" stroke="#111" stroke-width="1"/>'
    i += ar(x(11), 20, x(11), 48) + t(x(11), 14, "L3 promised 11 Nov: key 2", 13, "middle")
    i += ar(x(13), 20, x(13), 48) + t(x(13), 14, "L4 promised 13 Nov: key 3", 13, "middle")
    i += ar(x(13), 104, x(13), 134) + t(x(13) + 8, 118, "L5 on night 1: no version found, key -1 (unknown)", 13)
    return svg(1000, 224, "Keys as of the event date. Dealer D7 was in the North region (key 2) until 12 November, then West "
                          "(key 3). Order line L3, promised 11 November, gets key 2; L4, promised 13 November, gets key 3. "
                          "Dealer D9 is not in the dealer list on night 1, so L5 gets the unknown key -1; on night 2 D9 arrives "
                          "as key 4 in the South.", i)


def d_ledger():
    L = run("r1")["ledger"]
    i = ""
    boxes = [[f"{L['read']} lines read", "(windows 10, 11, 13 Nov)"], [f"{L['filtered']} filtered", "test dealer TEST01"],
             [f"{L['after_join']} after the join", "must equal 6 - 1 = 5"], [f"{L['unknown_keys']} unknown dealer", "key -1, limit 25%"],
             [f"{L['written']} written"]]
    for k, b in enumerate(boxes):
        xx = 10 + k * 198
        i += bx(xx, 30, 180, 66, b, "r" if k == 1 else ("y" if k == 3 else "w"), 14)
        if k:
            i += ar(xx - 18, 63, xx - 1, 63)
    i += t(500, 132, f"the balance: {L['read']} read = {L['filtered']} filtered + {L['rejected']} rejected + {L['written']} written. If it does not balance, nothing is written.", 14, "middle")
    return svg(1000, 148, "The row ledger for run r1. 6 lines read; 1 filtered (test dealer TEST01); 5 after the join with "
                          "deliveries, which must equal 6 minus 1; 1 with an unknown dealer, under its 25 percent limit; 5 "
                          "written. The balance: 6 read equals 1 filtered plus 0 rejected plus 5 written. If it does not "
                          "balance, nothing is written.", i)


def d_doubling():
    i = bx(10, 10, 480, 220, [""], "w") + t(250, 34, "careless: join every delivery row", 15, "middle")
    i += bx(30, 60, 130, 50, ["L3", "8 ordered"], "b", 14) + ar(160, 85, 198, 70) + ar(160, 85, 198, 120)
    i += bx(200, 48, 130, 40, ["X3: 6 tyres"], "w", 13) + bx(200, 100, 130, 40, ["X6: 2 tyres"], "w", 13)
    i += ar(330, 68, 358, 68) + ar(330, 120, 358, 120)
    i += bx(360, 48, 120, 40, ["L3, 8 ordered"], "r", 13) + bx(360, 100, 120, 40, ["L3, 8 ordered"], "r", 13)
    i += t(250, 180, "two rows for one line: 16 tyres 'ordered'", 14, "middle") + t(250, 202, "stopped by the grain and ledger checks", 13, "middle")
    i += bx(510, 10, 480, 220, [""], "w") + t(750, 34, "right: one row per line first", 15, "middle")
    i += bx(530, 60, 130, 50, ["X3 + X6", "sum = 8 tyres"], "w", 14) + ar(660, 85, 698, 85)
    i += bx(700, 60, 130, 50, ["L3", "8 ordered"], "b", 14) + ar(830, 85, 858, 85) + bx(860, 60, 120, 50, ["L3, 8 and 8", "one row"], "g", 13)
    i += t(750, 180, "add deliveries up per line, then join", 14, "middle") + t(750, 202, "a lookup join can never add rows", 13, "middle")
    return svg(1000, 240, "Why joins double numbers. Careless: order line L3 (8 ordered) is joined to both of its deliveries, X3 "
                          "with 6 tyres and X6 with 2, giving two rows for one line and 16 tyres ordered; the grain and ledger "
                          "checks stop it. Right: add the deliveries up per line first (8 tyres), then join, so the line stays "
                          "one row.", i)


def d_crash():
    i = ""
    seq = [(["r2 starts", "bookmark 2205"], "w"), (["writes windows", "11 and 13 Nov"], "w"), (["crash!", "before the bookmark"], "r"),
           (["rerun reads", "2206 again"], "y"), (["plans from the last", "committed version"], "y"), (["same table,", "2 restatements"], "g")]
    for k, (s, f) in enumerate(seq):
        xx = 10 + k * 165
        i += bx(xx, 30, 150, 66, s, f, 13)
        if k:
            i += ar(xx - 14, 63, xx - 1, 63)
    i += t(500, 130, "Because the bookmark moves last and windows are replaced whole, a crash repeats work. It never skips or doubles it.", 14, "middle")
    return svg(1000, 146, "A crash in run r2. It starts at bookmark 2205, writes windows 11 and 13 November, then crashes before "
                          "moving the bookmark. The rerun reads change 2206 again, plans from the last committed version of "
                          "gold, and ends with the same table and two restatements. A crash repeats work; it never skips or "
                          "doubles it.", i)


def d_kinds():
    cards = [("1. Transaction", "What happened?", "a row per event, added", "g"),
             ("2. Periodic snapshot", "How much was there at the end of each day?", "a row per thing per period, quiet days too", "b"),
             ("3. Accumulating snapshot", "How far along is each order?", "one row per process, updated as it moves", "y"),
             ("4. Factless", "Did it happen? Who was visited?", "rows with no numbers at all", "w"),
             ("5. Aggregate", "A fast answer to a common question", "a summary built from another fact", "l"),
             ("6. Consolidated", "Plan against actual?", "two sources brought to one grain", "r")]
    i = ""
    for k, (n, q, rows, f) in enumerate(cards):
        xx, yy = 10 + (k % 3) * 330, 10 + (k // 3) * 132
        i += bx(xx, yy, 310, 118, [""], f) + t(xx + 155, yy + 30, n, 16, "middle")
        i += t(xx + 155, yy + 62, q, 13, "middle") + t(xx + 155, yy + 94, rows, 13, "middle")
    return svg(1000, 278, "Six kinds of fact, each for a different shape of question. Transaction: what happened, a row per event. "
                          "Periodic snapshot: how much was there at the end of each day, a row per thing per period. "
                          "Accumulating snapshot: how far along is each order, one row per process updated as it moves. "
                          "Factless: did it happen, rows with no numbers. Aggregate: a fast answer, a summary of another fact. "
                          "Consolidated: plan against actual, two sources at one grain.", i)


def d_rpw():
    i = bx(10, 10, 980, 236, [""], "w") + t(500, 34, "every gold table, every night", 15, "middle")
    i += bx(30, 54, 290, 120, ["READER", "what changed since my bookmark?", "which windows does it touch?", "read all rows of those windows"], "b", 14)
    i += ar(320, 114, 358, 114)
    i += bx(360, 54, 280, 120, ["PROCESSOR", "build(inputs, params) -> rows", "the business rule only", "no reads, writes or clock"], "g", 14)
    i += ar(640, 114, 678, 114)
    i += bx(680, 54, 290, 120, ["WRITER", "replace whole windows", "(or merge by key, for one kind)", "then move the bookmark"], "y", 14)
    i += t(175, 198, "generic: settings say what", 13, "middle") + t(500, 198, "written per fact: the only hand-written part", 13, "middle")
    i += t(825, 198, "generic: the fact kind says how", 13, "middle")
    i += t(500, 232, "around all three: keys as of the event, checks, the row ledger, completeness, restatements, the run log", 13, "middle")
    return svg(1000, 256, "Reader, processor, writer. The reader asks what changed since the bookmark, which windows it touches, "
                          "and reads all rows of those windows; it is generic and driven by settings. The processor is "
                          "build(inputs, params), the business rule only, with no reads, writes or clock; it is the only part "
                          "written per fact. The writer replaces whole windows, or merges by key for one kind, then moves the "
                          "bookmark; the fact kind says how. Around all three: keys, checks, the row ledger, completeness, "
                          "restatements and the run log.", i)


def d_ripple():
    i = ""
    for k, d in enumerate([10, 11, 12, 13]):
        xx = 120 + k * 200
        i += bx(xx, 40, 150, 56, [f"{d} Nov", "closing stock"], "y" if k else "g", 14)
        if k:
            i += ar(xx - 48, 68, xx - 1, 68)
    i += t(500, 128, "A movement corrected on 10 Nov changes the closing stock of 10 Nov AND every day after it.", 14, "middle")
    i += t(500, 150, "So the reader turns a change into 'from that day to today', not just 'that day'.", 14, "middle")
    return svg(1000, 162, "A correction to a stock movement on 10 November changes the closing stock on 10 November and every "
                          "later day, so the periodic snapshot's reader rebuilds from that day to today.", i)


def d_three():
    cols = [("A. All declarative", "y", ["dim_dealer: AUTO CDC (SCD2)", "fact_otif: materialized view", "aggregates: materialized views",
                                         "checks: expectations"], "Pursue with care"),
            ("B. Hybrid", "g", ["dims + aggregates: Lakeflow", "facts: the harness (a job task)", "one Databricks job runs",
                                "pipeline, then harness, then MVs"], "Pursue"),
            ("C. Harness only", "b", ["everything in the harness", "run by a Databricks job", "or any Spark, any cloud",
                                      "same code on a laptop"], "Pursue where portability matters")]
    i = ""
    for k, (n, f, lines, v) in enumerate(cols):
        xx = 10 + k * 330
        i += bx(xx, 10, 310, 248, [""], "w") + t(xx + 155, 38, n, 16, "middle")
        for j, s in enumerate(lines):
            i += bx(xx + 20, 56 + j * 42, 270, 34, [s], f, 13)
        i += t(xx + 155, 240, v, 14, "middle")
    return svg(1000, 268, "Three ways to run silver to gold on Databricks. A, all declarative: dimensions by AUTO CDC, facts and "
                          "aggregates as materialized views, checks as expectations; pursue with care. B, hybrid: dimensions and "
                          "aggregates in Lakeflow, facts in the harness as a job task, one Databricks job running pipeline, "
                          "harness, then materialized views; pursue. C, harness only, run by a job or any Spark on any cloud, "
                          "same code on a laptop; pursue where portability matters.", i)


# ------------------------------------------------------------------ Part A content
GLOSSARY = [
    ("Silver", "Clean copies of the source tables, still shaped like the source (an orders table, a deliveries table)."),
    ("Gold", "Tables shaped for questions: facts and dimensions. What dashboards, metric views and AI agents read."),
    ("Fact", "A table of things that happened or were measured, with numbers (tyres ordered, tyres delivered)."),
    ("Dimension", "A table that describes the who, what and where of a fact (the dealer, its name, its region)."),
    ("Grain", "What one row of a fact means, in one sentence. Here: one row per order line."),
    ("Surrogate key", "A number gold gives each dimension row (dealer_key 2), instead of the source's own id. It lets one dealer have several versions."),
    ("SCD Type 2", "Keeping history in a dimension: when a dealer moves region, the old row is closed and a new row opens. Both stay."),
    ("Window", "A slice of the fact rebuilt as one piece. Here: one day of promised date."),
    ("Watermark (bookmark)", "The last change number this table has already used. The next run starts after it."),
    ("High mark", "The newest change number when a run starts. The run reads up to it and no further."),
    ("Lookback", "How old a window may be and still be rebuilt automatically (35 days here). Older fixes need a correction plan."),
    ("Completeness", "A window is complete when every feed that owes data for it has sent it."),
    ("Restatement", "A number that was already published and has now changed. Logged with old value, new value and reason."),
    ("Idempotent", "Running it twice gives the same result as running it once."),
    ("Pure function", "Code that only turns inputs into outputs: it reads no tables, writes nothing and never asks the time."),
    ("Harness", "The shared code that runs every gold table the same way. Only the business rule is written per table."),
]


def silver_tables():
    L = [[r[0], r[2], r[4], nd(r[5]), r[6]] for r in X.LINES_R1]
    Dl = [[r[0], r[1], r[2], r[3], nd(r[4]), r[5]] for r in X.DELS_R1]
    Dr = [[r[0], r[1], r[2], nd(r[3]), "open" if r[4].year == 9999 else nd(r[4])] for r in X.DEALERS_R1]
    return (f"<h3>silver.order_lines</h3>{htable(['line_id', 'dealer_id', 'qty_ordered', 'promised_date', '_seq (change number)'], L, hl=range(1, 7), dim=[0])}"
            f"<h3>silver.deliveries</h3>{htable(['delivery_id', 'line_id', 'warehouse', 'qty', 'delivered_date', '_seq'], Dl, hl=range(1, 6), dim=[0])}"
            f"<h3>silver.dealers (history kept)</h3>{htable(['dealer_id', 'name', 'region', 'valid_from', 'valid_to'], Dr)}"
            "<p>Grey rows were already used by an earlier run (r0, on 5 Nov). Yellow rows are new since then. TEST01 is a test dealer that must never reach gold. Dealer D9 has placed an order (L5) but is not in the dealer list yet: that happens in real life all the time.</p>")


def part_a():
    r1, r2 = run("r1"), run("r2")
    asof = R["asof_vs_current"]
    asof_rows = [[a["line_id"], nd(a["promised_date"]), a["otif"], a["as_of_region"], a["current_region"]] for a in asof]
    dim1 = [[d["dealer_key"], d["dealer_id"], d["region"], nd(d["valid_from"]), "open" if d["valid_to"].startswith("9999") else nd(d["valid_to"])] for d in R["dim"]["after r2"]]
    rest = [[nd(x["window"]), x["run"], json.dumps({k: v for k, v in x["old"].items() if x["new"][k] != v}),
             json.dumps({k: v for k, v in x["new"].items() if x["old"][k] != v}),
             "late delivery for L3" if x["window"].endswith("11") else "dealer D9 arrived: L5 re-keyed"] for x in R["restatements"]]
    careless = R["careless"].split(": ", 1)[1]
    return f"""
<section id="start" class="part"><p class="eyebrow">Start here</p><h2>How to read this page</h2>
<div class="start"><p><b>If this layer feels complex, read Part A first and nothing else.</b> It follows one tiny tyre company through two nights. Every idea on this page (watermarks, windows, keys, completeness, restatements, checks) shows up there as something that happens to real rows, in a picture and in a table. Every number in Part A came out of a real run of the code shown, on Spark 3.5.1 and Delta 3.2.0.</p>
<ul><li><b>Part A</b>: learn it from zero with one example.</li>
<li><b>Part B</b>: the six kinds of fact, why there are six, and how each is built as reader, processor and writer.</li>
<li><b>Part C</b>: can this layer be a Databricks declarative pipeline? Pros, cons and verdicts.</li>
<li><b>Part D</b>: the full rulebook, for when you are building or reviewing.</li></ul></div>
<h3>Words you will meet</h3>{C.table(["Word", "What it means here"], GLOSSARY)}</section>

<section id="a-story" class="part"><p class="eyebrow">Part A · 1</p><h2>The story: a tyre company and one question</h2>
<p>A tyre maker sells to dealers. A sales director asks one question every morning: <b>what percent of order lines did we deliver on time and in full (OTIF), per region, per day?</b> "On time" means the last delivery came on or before the promised date. "In full" means all the tyres ordered were delivered. A line counts towards OTIF only if both are true.</p>
<p>Silver already holds clean data from three sources. Gold must turn it into a fact and a dimension that answer the question. A program called the harness does that every night.</p>
{fig(d_story(), "Sources land in silver; each night the harness turns silver into gold; gold answers the question.")}
<p>Here is silver just before the night of 13 November. These are the actual rows the code ran on.</p>
{silver_tables()}
<p>The OTIF rule for one line, worked by hand, so you can check the computer later:</p>
{htable(["line", "ordered", "delivered", "last delivery vs promised", "on time?", "in full?", "OTIF"], [
        ["L1", 10, 10, "10 Nov vs 10 Nov", "yes", "yes", "1"],
        ["L2", 5, 5, "11 Nov vs 10 Nov (a day late)", "no", "yes", "0"],
        ["L3", 8, 6, "11 Nov vs 11 Nov", "yes", "no (2 short)", "0"],
        ["L4", 4, 4, "13 Nov vs 13 Nov", "yes", "yes", "1"],
        ["L5", 6, 6, "13 Nov vs 13 Nov", "yes", "yes", "1"]])}
</section>

<section id="a-night" class="part"><p class="eyebrow">Part A · 2</p><h2>What one nightly run does, in seven steps</h2>
<p>Every gold table goes through the same seven steps, every night. Only step 4, the business rule, is written for each table. The rest is shared code (the harness) driven by a short settings file. Keep this picture in mind for the rest of the page.</p>
{fig(d_night(), "Reader, processor, harness rules, writer. Only the green box is written per fact.")}
<p>The settings file for fact_otif, as the code used it. This is all the harness needs to know about this table:</p>
{C.code(src("harness.py", "FACT_OTIF"))}
</section>

<section id="a-night1" class="part"><p class="eyebrow">Part A · 3</p><h2>Night 1 (run r1, 13 Nov), step by step</h2>
<h3>Steps 1 and 2: where did I stop, and what changed since?</h3>
<p>The metadata store says the last run used order lines up to change 1001 and deliveries up to change 2101. Those are the <b>watermarks</b>. At the start, the run notes the newest change numbers that exist right now, 1046 and 2205. Those are the <b>high marks</b>, and they do not move during the run. The run reads only the rows in between.</p>
{fig(d_bookmark(), "Read a closed range: after the watermark, up to the high mark. Anything newer waits.")}
{htable(["input", "watermark (from last run)", "high mark (fixed at start)", "rows read"], [
        ["order_lines", r1["read_from"]["order_lines"], r1["read_to"]["order_lines"], "L1 to L6 (6 rows)"],
        ["deliveries", r1["read_from"]["deliveries"], r1["read_to"]["deliveries"], "X1 to X5 (5 rows)"]])}
<p><b>Why change numbers and not times?</b> Two rows can have the same time, and clocks on different servers disagree. A change number only goes up and never repeats, so nothing is skipped or read twice.</p>
<h3>Step 3: which windows do the changes touch?</h3>
<p>The fact is rebuilt one day of promised date at a time. Each changed row points at one day. A delivery has no promised date of its own, so it points at the day of its order line.</p>
{fig(d_windows(), "Changes become a short list of days. Only those days are rebuilt.")}
<p>Result: run r1 rebuilds <b>{", ".join(nd(w) for w in r1["windows"])}</b>. The 5 Nov window is never read again. That is why the run's cost follows the number of changes, not the size of history. With years of history, a night still rebuilds only a few days.</p>
<p>The run then reads <b>every</b> silver row of those three days, not just the changed ones. A day is rebuilt whole, so it must be built from the full set of its rows.</p>
<h3>Step 4: the build (processor)</h3>
<p>The build is the only code written for this fact. It gets the order lines and deliveries for the three days and returns one row per line with the OTIF flags. Note the first thing it does: add up deliveries <b>per line</b> before joining. Section 6 below shows what happens without that.</p>
{C.code(src("builds.py", "build_otif"))}
<h3>Step 5: keys as of the event date</h3>
<p>Dealer D7 moved from North to West on 12 Nov. Which region should L3 count under? <b>The region that was true on the line's date.</b> L3 was promised on 11 Nov, when D7 was North. The harness finds the dimension version whose valid_from to valid_to range holds the promised date and takes its key.</p>
{fig(d_asof(), "Each line gets the dealer version that was true on its own date.")}
<p>The wrong way is to join each line to the dealer's <i>current</i> row. These rows come from the run. Compare the last two columns:</p>
{htable(["line", "promised", "OTIF", "region as of that date (right)", "region today (wrong)"], asof_rows, hl=[2])}
<p>With the right lookup, North's OTIF on these lines is 1 of 3 and West's is 1 of 1. With the wrong one, L3 jumps to West: North becomes 1 of 2 and West 1 of 2. Every past report would change each time a dealer moves. That is exactly what SCD Type 2 and as-of lookups prevent.</p>
<p>L5's dealer, D9, is not in the dimension at all. The line still goes into gold, but with key <b>-1</b> ("unknown dealer"), and it is counted. It is not dropped: dropping it would quietly lose 6 tyres from every total. The code:</p>
{C.code(src("harness.py", "lookup_keys"))}
<h3>Step 6: complete or not, check, and count</h3>
<p>Both warehouses owe a delivery file every day. On the night of 13 Nov, WH-B's file for 13 Nov has not come. So the 13 Nov window is written with <code>_is_complete = false</code>. Readers and dashboards can show "not final yet" instead of a number that will change. 10 and 11 Nov have both files, so they are complete.</p>
<p>Before writing anything, the harness counts rows at each step (the <b>row ledger</b>) and checks: one row per line, the ledger balances, the join added and lost nothing, and unknown dealers stay under their limit.</p>
{fig(d_ledger(), "Every row is accounted for. A missing or extra row stops the run before it writes.")}
<h3>Step 7: replace the windows, then move the bookmark</h3>
<p>The writer replaces the three days whole. It does not add rows on top: run it twice and you get the same table. Only after the write succeeds does the run log its work and move the watermarks to 1046 and 2205. If anything fails before that, the bookmark stays put and the next run simply does the work again.</p>
{C.code(src("harness.py", "replace_windows"))}
<p>Gold after night 1 (yellow rows were written by r1):</p>
{htable(FCOLS, fact_rows("after r1"), hl=range(1, 6), dim=[0])}
<p>Look at L5: dealer_key -1 and not complete. Both get fixed on night 2, by themselves.</p>
</section>

<section id="a-night2" class="part"><p class="eyebrow">Part A · 4</p><h2>Night 2 (run r2, 15 Nov): late data and a late dealer</h2>
<p>Three things arrived in silver since night 1:</p>
<ul><li>Delivery <b>X6</b>: the last 2 tyres of L3, delivered on 14 Nov (change 2206).</li>
<li>Dealer <b>D9</b> appears in the dealer list (South), and becomes dimension key 4.</li>
<li>WH-B's missing file for 13 Nov arrives.</li></ul>
<p>The reader finds the windows: X6 belongs to L3, so <b>11 Nov</b>. 13 Nov holds an unknown dealer that now exists, and it is still incomplete, so <b>13 Nov</b> too. The run rebuilds {", ".join(nd(w) for w in r2["windows"])}, and leaves 5 and 10 Nov alone.</p>
{htable(FCOLS, fact_rows("after r2"), hl=[3, 4, 5], dim=[0, 1, 2])}
<p>What changed: L3 now has 8 tyres delivered (in full), but the last one came on 14 Nov, after the promise, so it is still not OTIF. L5 now has key 4 instead of -1, so its tyres now count under South. 13 Nov is complete.</p>
<h3>Restatements: numbers that changed after they were shown</h3>
<p>11 Nov and 13 Nov were already published on night 1. Their numbers moved, so the harness logs each change: which window, what it was, what it is now, and which run. A finance reader can then see why a past number changed, instead of being surprised.</p>
{htable(["window", "run", "was", "now", "why"], rest)}
<p>The dimension after night 2:</p>
{htable(["dealer_key", "dealer_id", "region", "valid_from", "valid_to"], dim1, hl=[3])}
</section>

<section id="a-crash" class="part"><p class="eyebrow">Part A · 5</p><h2>What if the machine dies halfway?</h2>
<p>We made run r2 crash on purpose, after it had written gold but before it moved the bookmark ("{E(R["crash"])}"). Then we ran it again.</p>
{fig(d_crash(), "Bookmark last, windows replaced whole: a crash means repeated work, never lost or doubled numbers.")}
<p>Result: the table after the rerun is identical to the table the crashed run wrote: <b>{"yes" if R["rerun_same_as_crash"] else "NO"}</b>. Both restatements are logged once. Final watermarks: order_lines {R["watermarks"]["fact_otif.order_lines"]}, deliveries {R["watermarks"]["fact_otif.deliveries"]}.</p>
<div class="warn"><b>A real lesson from writing this example:</b> our first version planned the rerun by looking at gold as the crashed run had left it. The crashed run had already fixed L5's key and the 13 Nov flag, so the rerun thought 13 Nov needed nothing. It rebuilt only 11 Nov and lost the 13 Nov restatement. The fix: a run always plans and compares against the <b>last committed version</b> of gold (the version recorded when the bookmark last moved), never against whatever is in the table now. Delta and Iceberg keep old versions, which makes this one line.</div>
</section>

<section id="a-careless" class="part"><p class="eyebrow">Part A · 6</p><h2>What if someone writes a careless join?</h2>
<p>We swapped the build for a careless one that joins every delivery row straight onto the order lines. L3 has two deliveries now, so it became two rows.</p>
{fig(d_doubling(), "One line with two deliveries becomes two rows unless deliveries are added up first.")}
<p>The harness refused to write. The exact message from the run:</p>
{C.code(careless)}
<p>Wrote anything? <b>{"No" if R["careless_wrote_nothing"] else "YES"}</b>. Three separate checks caught it: the grain (L3 twice), the ledger balance, and the join row count. In a notebook without these checks, the dashboard would have shown 8 extra tyres ordered, and nobody would have known why.</p>
</section>

<section id="a-tests" class="part"><p class="eyebrow">Part A · 7</p><h2>How the build is tested: small tables in, expected rows out</h2>
<p>Because the build is pure, a test is just a few rows in and the expected flags out, written as a table. These run in about ten seconds on a laptop:</p>
{C.code(src("test_builds.py", "OTIF_CASES", "test_otif"))}
<p>Writing this page, one of these table tests caught a real bug in the stock build (Part B): days before the first stock movement were dropped instead of showing zero.</p>
<details class="code"><summary>The whole run, as tested (harness.py, run_fact)</summary>{C.code(src("harness.py", "run_fact"))}</details>
<details class="code"><summary>Reading and the metadata store (harness.py)</summary>{C.code(src("harness.py", "Meta", "high_mark", "read_changes", "assign_keys"))}</details>
<details class="code"><summary>Checks and the ledger (harness.py)</summary>{C.code(src("harness.py", "window_summary", "check"))}</details>
<p>All files: <code>_guides/code/silver_to_gold/</code> in the site's repository (builds.py, harness.py, data.py, test_builds.py, e2e.py).</p>
</section>"""


# ------------------------------------------------------------------ Part B content
WHY_KINDS = [
    ("Something happened, once", "An order line was placed; a tyre was scrapped", "Transaction", "New rows are added; old rows rarely change"),
    ("How much is there at a moment", "Stock in each warehouse at the end of each day", "Periodic snapshot", "A row per thing per period, even when nothing moved"),
    ("A process with steps that takes days", "An order: ordered, shipped, delivered, invoiced", "Accumulating snapshot", "One row per process, filled in as steps happen"),
    ("Something happened, but there is nothing to measure", "A sales rep visited a dealer", "Factless", "The row itself is the fact; you count rows"),
    ("The same big question, asked all day", "OTIF per region per day on the home dashboard", "Aggregate", "A small summary of a big fact, kept in step with it"),
    ("Two sources that must be compared", "Sales plan against actual orders", "Consolidated", "Each source brought to the same grain, then joined"),
]


def kind_block(n, title, plain, question, grain, rows_html, reader, processor, writer, traps, code=""):
    return f"""<div class="kind"><h3>{n}. {E(title)}</h3>
<p>{plain}</p>
<p><b>The tyre question:</b> {E(question)} <b>Grain:</b> {E(grain)}</p>
{rows_html}
<div class="rpw"><div class="r"><b>Reader</b>{reader}</div><div class="p"><b>Processor</b>{processor}</div><div class="w"><b>Writer</b>{writer}</div></div>
{code}
<p><b>Traps:</b> {traps}</p></div>"""


def part_b():
    stock = htable(["day", "movements that day", "closing stock (from the run)"],
                   [[nd(s["day"]), m, s["stock"]] for s, m in zip(R["stock"], ["+100 in, -10 out", "none (quiet day)", "-6 out", "+50 in"])], hl=[1])
    life = htable(["after", "ordered_at", "shipped_at", "delivered_at", "invoiced_at", "days_to_deliver"],
                  [[x["after"], nd(x["ordered_at"]), nd(x["shipped_at"]), nd(x["delivered_at"]), nd(x["invoiced_at"]), x["days_to_deliver"]]
                   for x in R["lifecycle"]])
    visits = htable(["rep", "dealer", "visit_date", "note"], [["R-Asha", "D1", "10 Nov", "kept"], ["R-Asha", "D1", "10 Nov", "same visit sent twice: dropped"],
                                                              ["R-Vik", "D7", "11 Nov", "kept"]], dim=[1])
    agg = htable(["promised_date", "region", "lines", "otif_lines", "otif_pct"],
                 [[nd(a["promised_date"]), a["region"], a["lines"], a["otif_lines"], a["otif_pct"]] for a in R["aggregate"]])
    pva = htable(["dealer", "month", "plan_qty", "actual_qty", "gap"],
                 [[p["dealer_id"], p["month"], p["plan_qty"], p["actual_qty"], p["gap"]] for p in R["plan_vs_actual"]])
    blocks = [
        kind_block(1, "Transaction fact", "One row per event. This is the OTIF fact from Part A. It is the most common kind and the default.",
                   "What happened to each order line?", "one row per order line",
                   "<p>Rows: the gold table in Part A.</p>",
                   "Rows changed since the bookmark, turned into the days (promised dates) they touch.",
                   "Add deliveries up per line, apply the on-time and in-full rule.",
                   "Replace those days whole. Re-running gives the same table.",
                   "joining child rows (deliveries) without adding them up first; looking up the dealer's current row instead of the row true on the date."),
        kind_block(2, "Periodic snapshot", "A photo of a level taken at the end of every period: stock, balances, headcount. The point is that <b>every</b> period gets a row, even when nothing moved, so a chart of stock over time has no gaps.",
                   "How many R15 tyres were in WH-A at the end of each day?", "one row per warehouse, product and day",
                   stock + fig(d_ripple(), "A change to one day's movement ripples into every later day."),
                   "Movements changed since the bookmark. <b>Unlike a transaction fact</b>, a change on 10 Nov touches every day from 10 Nov to today, because stock is carried forward.",
                   "For each warehouse, product and day, add up every movement up to the end of that day. Quiet days carry the previous level.",
                   "Replace the days from the earliest changed day to today. Periods closed by finance are frozen and only change through a correction plan.",
                   "never add stock up across days (100 on Monday plus 100 on Tuesday is not 200 tyres): it adds up across warehouses, not across time. Use the last day or the average instead. The bug our test caught lived here: a day before the first movement was dropped instead of showing 0.",
                   C.code(src("builds.py", "build_daily_stock"))),
        kind_block(3, "Accumulating snapshot", "One row for each process instance (an order line), with a date column per milestone. The row is <b>updated</b> as the order moves. It answers 'where is everything right now, and how long do the steps take?'",
                   "Where is line L3 in its journey, and how many days did delivery take?", "one row per order line",
                   life + f"<p>Still one row after three days (rows in the table: {R['lifecycle_rows']}). Each day filled in one more column.</p>",
                   "Milestone events changed since the bookmark (ordered, shipped, delivered, invoiced).",
                   "Turn events into one row per line with a column per milestone; work out days between them.",
                   "<b>MERGE by line_id</b>, the one kind that updates rows in place. A milestone already known is never blanked out by a later event that does not mention it.",
                   "this is the only fact kind where rows change after they are written, so every update is effectively a restatement; and a line that never reaches 'delivered' needs an 'open' flag, or averages hide it.",
                   C.code(src("builds.py", "MILESTONES", "build_line_lifecycle")) + C.code(src("harness.py", "merge_by_key"))),
        kind_block(4, "Factless fact", "A fact with no numbers. The row itself says something happened: a visit, a training, an enrolment. You answer questions by counting rows, or by finding what is <b>missing</b>.",
                   "Which dealers did our reps visit, and which did nobody visit?", "one row per rep, dealer and day",
                   visits + f"<p>Visits counted: {R['visits']}. Dealers nobody visited (dimension minus visits): {', '.join(R['not_visited'])}.</p>",
                   "Visit records changed since the bookmark, turned into visit days.",
                   "Keep rep, dealer and day; drop exact repeats so a re-sent visit counts once.",
                   "Replace those days whole.",
                   "'what did NOT happen' cannot be read from the fact alone: you compare it with the dimension (all dealers) or keep a coverage fact (which dealers were in scope)."),
        kind_block(5, "Aggregate fact", "A small summary of a big fact, built so the busiest question is fast. It is built <b>from gold</b>, never straight from silver, so its numbers always agree with the detail.",
                   "OTIF per region per day, for the home dashboard.", "one row per day and region",
                   agg,
                   "The days the atomic fact (fact_otif) rebuilt in this run, from its run log. Nothing else.",
                   "Join the fact to the dimension by its key (already looked up as of the date), group by day and region.",
                   "Replace those days. Runs after the fact, never before (dependency order).",
                   "store the counts (lines, otif_lines), not only the percent: percents cannot be added up across regions or days. A summary nobody reads is pure cost."),
        kind_block(6, "Consolidated fact", "Two or more sources about the same business, brought to one shared grain and joined, so they can be compared on one row.",
                   "Did each dealer order what we planned for November?", "one row per dealer and month",
                   pva + "<p>D1: 3 + 10 + 5 = 18 tyres against a plan of 20. D7: 8 + 4 = 12 against 10. TEST01 is filtered out.</p>",
                   "The plan (small, read in full) and the order lines of the months that changed.",
                   "Add actual orders up to dealer and month <b>first</b>, then a full outer join with the plan, so a dealer with a plan but no orders (or orders but no plan) still shows.",
                   "Replace the changed months.",
                   "joining at different grains (a monthly plan to daily orders) repeats the plan on every day and multiplies it; an inner join hides dealers that appear on one side only.",
                   C.code(src("builds.py", "build_plan_vs_actual"))),
    ]
    summary = [
        ("Transaction", "changed rows to their event days", "row rule", "replace windows", "Pursue: the default"),
        ("Periodic snapshot", "changed rows to that day and every later day", "running level per period", "replace from first changed period", "Pursue for levels and balances"),
        ("Accumulating snapshot", "changed milestone events", "pivot milestones into one row", "MERGE by key", "Pursue for multi-step processes"),
        ("Factless", "changed events to their days", "dedupe events", "replace windows", "Pursue for coverage questions"),
        ("Aggregate", "windows the source fact rebuilt", "group by", "replace windows", "Pursue only where a question is slow and frequent"),
        ("Consolidated", "changed periods of each source", "bring each to one grain, full outer join", "replace windows", "Pursue for plan vs actual, budget vs spend"),
    ]
    return f"""
<section id="b-why" class="part"><p class="eyebrow">Part B · 1</p><h2>Why are there so many kinds of fact?</h2>
<p>Because business questions come in a few different shapes, and each shape needs rows that behave differently over time. "What happened?" needs a row per event that never changes. "How much is in stock?" needs a row per day even on quiet days. "How far along is each order?" needs one row that keeps changing. Put the wrong shape in the wrong kind of table and the numbers come out wrong, or the queries crawl.</p>
<p>So the kind is not decoration. <b>It decides how the reader finds the windows and how the writer writes.</b> That is why the harness asks for it in the settings file, and why one harness can build all six: it knows six ways to read and two ways to write, and the business rule stays in the small build.</p>
{fig(d_kinds(), "Pick the kind from the shape of the question.")}
{C.table(["The question's shape", "Tyre example", "Kind of fact", "How its rows behave"], WHY_KINDS)}
</section>

<section id="b-rpw" class="part"><p class="eyebrow">Part B · 2</p><h2>Reader, processor, writer: the three parts of every build</h2>
{fig(d_rpw(), "Reader and writer are shared; the processor is the business rule.")}
<p><b>Reader.</b> Its job is to answer: what changed since my bookmark, and which windows does that touch? Then it reads every row of those windows, plus small dimension tables. It never decides business meaning. It is generic: the settings say which inputs, which bookmark column and which window column.</p>
<p><b>Processor.</b> A pure function, <code>build(inputs, params)</code>. It gets DataFrames and returns DataFrames. It holds the one thing only your business knows: what "on time" means, how stock carries forward, how a plan meets actuals. Because it reads and writes nothing, you can test it with three rows on a laptop. In our examples the six builds are 4 to 15 lines each.</p>
<p><b>Writer.</b> Its job is to put the rows into gold safely. For five kinds that means replacing whole windows, which is idempotent: twice is the same as once. For the accumulating snapshot it means a MERGE by key that never blanks a known milestone. Only after a successful write does the bookmark move.</p>
<p><b>Around all three</b>, the harness adds what no single build should have to remember: keys as of the date, completeness, checks, the row ledger, restatements and the run log.</p>
</section>

<section id="b-kinds" class="part"><p class="eyebrow">Part B · 3</p><h2>The six kinds, each with an example and its reader, processor and writer</h2>
<p>All six examples were run. The tables show their real output.</p>
{''.join(blocks)}
<h3>All six on one page</h3>{vtable(["Kind", "Reader finds windows by", "Processor", "Writer", "Verdict"], summary)}
</section>"""


# ------------------------------------------------------------------ Part C content
LAKEFLOW_SKETCH = '''
# Lakeflow Spark Declarative Pipelines (Databricks). A sketch written for this page: NOT run on Databricks yet.
from pyspark import pipelines as dp
from pyspark.sql import functions as F
from builds import build_otif                      # the same pure build as Part A, unchanged

# Dimension: SCD Type 2 from the dealer change feed. The engine handles order, repeats and deletes.
dp.create_streaming_table("dim_dealer")
dp.create_auto_cdc_flow(
    target="dim_dealer",
    source="dealer_changes",                       # a streaming view over silver dealer changes
    keys=["dealer_id"],
    sequence_by=F.col("effective_date"),           # versions are stamped with THIS column (see the cons)
    stored_as_scd_type=2,
)

# Dealer versions with a key and a date range, shared by the fact and the aggregate.
@dp.materialized_view(name="dealer_versions")
def dealer_versions():
    return (spark.read.table("dim_dealer")
            .select("dealer_id", "region",
                    F.xxhash64("dealer_id", "__START_AT").alias("dealer_key"),   # a hash, not 1, 2, 3
                    F.col("__START_AT").alias("vf"),
                    F.coalesce("__END_AT", F.lit("9999-12-31").cast("date")).alias("vt")))

# Fact: a materialized view. The engine decides each night whether it can refresh
# incrementally or must recompute; you do not choose which days are rebuilt.
@dp.materialized_view(name="fact_otif")
@dp.expect_or_fail("dealer looked up", "dealer_key IS NOT NULL")
def fact_otif():
    lines = spark.read.table("silver.order_lines").where("dealer_id NOT IN ('TEST01')")
    dels = spark.read.table("silver.deliveries")
    built = build_otif(lines, dels, {})
    dim = spark.read.table("dealer_versions").drop("region")
    on = ((built.dealer_id == dim.dealer_id)
          & (built.promised_date >= dim.vf) & (built.promised_date < dim.vt))
    return (built.join(dim, on, "left").drop(dim.dealer_id, "vf", "vt")
                 .withColumn("dealer_key", F.coalesce("dealer_key", F.lit(-1))))

# Grain check: expectations look at one row at a time, so a check across rows needs its own table.
@dp.materialized_view(name="check_fact_otif_grain")
@dp.expect_or_fail("one row per line", "n = 1")
def check_fact_otif_grain():
    return spark.read.table("fact_otif").groupBy("line_id").agg(F.count("*").alias("n"))

# Aggregate: the best fit for a materialized view.
@dp.materialized_view(name="otif_by_region_day")
def otif_by_region_day():
    return (spark.read.table("fact_otif")
            .join(spark.read.table("dealer_versions").select("dealer_key", "region"), "dealer_key", "left")
            .groupBy("promised_date", "region")
            .agg(F.count("*").alias("lines"), F.sum("otif").alias("otif_lines")))
'''

STEP_MAP = [
    ("1-2. Bookmarks, changed rows", "The engine keeps them (checkpoints, refresh tracking). You write none.", "Better: less code"),
    ("3. Which windows to rebuild", "A materialized view refreshes as the engine decides: incrementally when it can, otherwise a full recompute. You cannot say 'rebuild only 11 and 13 Nov'.", "Engine's choice, not yours"),
    ("4. The build", "The same pure function, called inside the decorated function.", "Same"),
    ("5. Keys as of the event", "Your own range join to the AUTO CDC table (__START_AT, __END_AT). No key map, so keys are hashes or business key plus start date.", "Possible, with work"),
    ("5b. Late dealer re-keyed", "In a materialized view, yes, on the next recompute. In a streaming table, no: a stream joined to a dimension sees the dimension as it was when each row was processed.", "Depends on the table type"),
    ("6. Completeness", "A column you compute in the view from a table of received files.", "Possible"),
    ("6b. Checks", "Expectations check one row at a time. Grain, totals and ledger balance need extra check tables, as in the sketch.", "Partly"),
    ("6c. Row ledger", "The event log has rows written per table and expectation pass and fail counts. Counts per filter and per join are not there.", "Partly"),
    ("Restatements", "A view keeps no record of the number it used to show. Comparing with the last published version needs a step outside the pipeline.", "Missing"),
    ("Correction plans for closed months", "No such idea. You change silver, or force a full refresh.", "Missing"),
    ("7. Write, then move the bookmark", "Each table's refresh is all or nothing. But the pipeline as a whole is not: for a while, readers can see the new fact with the old aggregate.", "Better per table; watch across tables"),
]

PROS = [
    ("Far less plumbing", "No bookmarks, run order, retries or checkpoints to write and test", "Small teams, many simple tables"),
    ("The dependency graph is drawn for you", "Tables run in the right order; lineage and a UI come free", "Many tables depending on each other"),
    ("SCD Type 2 dimensions in a few lines", "AUTO CDC handles out-of-order changes, repeats and deletes", "Every gold star on Databricks"),
    ("Late dimension members fixed by themselves", "A materialized view is recomputed against today's dimension, so L5's -1 becomes 4 with no extra code", "Facts built as materialized views"),
    ("Quality rules and run history in one place", "Expectations with keep, drop or fail; a queryable event log", "Teams without their own run log"),
    ("Aggregates kept up to date cheaply", "Incremental refresh of materialized views on serverless, when the engine can", "Dashboards over big facts"),
    ("Catches broken pipelines before they run", "Validate (dry-run) finds missing tables, columns and cycles with no data", "Every pipeline, in CI"),
    ("Your build still works", "The pure build from Part A runs inside unchanged, and is still tested on a laptop", "Keeping the option to leave"),
]

CONS = [
    ("You do not control how gold is written", "The engine chooses incremental or full recompute. A fact that silently falls back to full recompute costs more as history grows, and you may only notice on the bill.", "Check the refresh technique in the event log after every change"),
    ("No restatement log", "Published numbers change silently when late data arrives", "Add a job step that compares with the last published version"),
    ("No correction plans", "Fixing a closed month means changing silver or a full refresh", "Keep corrections in silver as records, never edits"),
    ("Keys are hashes, not a key map", "AUTO CDC does not hand out 1, 2, 3. Hash keys work, but are big and cannot be re-pointed", "Fine for most; finance-grade marts may want a key map"),
    ("AUTO CDC stamps versions with the sequence column", "If you sequence by a change number, __START_AT is that number, not a date, and you cannot look up 'as of 13 Nov'", "Sequence by an effective date, or keep a separate date column"),
    ("Checks across rows need extra tables", "Expectations see one row at a time; grain and totals need check views", "Write them, as in the sketch"),
    ("Streaming-table facts freeze the dimension", "Rows keep the dimension as it was when processed; a late dealer is never re-keyed without a full refresh", "Build facts as materialized views, not streaming tables"),
    ("Full refresh is a big hammer", "It rereads sources from the start; if old bronze or silver files have been removed, history is lost", "Protect important tables from full refresh"),
    ("Price on classic compute", "Declarative is 1.3 to 2.4 times the jobs rate per DBU on classic compute; the same rate on serverless", "Use serverless, or pick the edition per pipeline"),
    ("Tied to Databricks for the best parts", "Expectations, snapshot CDC and the event log are Lakeflow only; open-source Spark Declarative Pipelines has the engine, not these", "Keep builds as plain functions so you can leave"),
    ("Harder to see the middle", "Declarative hides steps by design; seeing one join's output means extra temporary views", "Use views for steps you need to inspect"),
]

FIT_KINDS = [
    ("SCD Type 2 dimensions", "AUTO CDC", "Pursue"),
    ("Aggregate facts", "Materialized views", "Pursue"),
    ("Factless facts", "Materialized views", "Pursue"),
    ("Transaction facts, small to medium history, no audit need", "Materialized views over silver", "Pursue with care: watch the refresh technique"),
    ("Transaction facts, large or finance-grade (restatements, correction plans)", "Harness as a job task", "Keep the harness"),
    ("Periodic snapshots", "Materialized view if small; a carried-forward level over years is costly to recompute", "Pursue with care"),
    ("Accumulating snapshots", "AUTO CDC Type 1 keyed by line, ignoring empty values in updates, can fill milestones in", "Pursue with care: test that known milestones are never blanked"),
    ("Consolidated facts", "Materialized views", "Pursue with care: same grain traps"),
]


def part_c():
    return f"""
<section id="c-short" class="part"><p class="eyebrow">Part C · 1</p><h2>Can silver to gold be a Databricks declarative pipeline?</h2>
<div class="box"><b>Short answer.</b> Yes, it can run as a Lakeflow Spark Declarative Pipeline. Dimensions, aggregates and simple facts fit very well. What a declarative pipeline does not give you is the bookkeeping: choosing which windows to rebuild, logging restatements, correction plans, a full row ledger, and checks across rows. Our recommendation is the <b>hybrid</b>: Lakeflow for dimensions and aggregates, the harness for facts that need that bookkeeping, both in one Databricks job. Go fully declarative only for small, simple marts where no one audits past numbers.</div>
<p>First, what "declarative" means: you say <i>what</i> each table is ("fact_otif is build_otif over these silver tables"), and the engine works out <i>how</i>: order, what is new, retries, refresh. The harness is the opposite. You (well, the shared code) say exactly how each night runs. More on the idea itself: <a href="/learn/spark-declarative-pipelines/">Declarative or not</a>.</p>
{fig(d_three(), "Three ways to run this layer on Databricks.")}
</section>

<section id="c-sketch" class="part"><p class="eyebrow">Part C · 2</p><h2>What Part A's example looks like as a declarative pipeline</h2>
<p>The same tyre example, written for Lakeflow. Read it next to Part A. The build is the same function. What changes is everything around it.</p>
<div class="warn"><b>Status:</b> this sketch was written for this page and has <b>not</b> been run on Databricks. Function names are from the Lakeflow Python API as documented in November 2026; check the current docs before copying.</div>
{C.code(LAKEFLOW_SKETCH)}
<h3>Each harness step, and what the declarative pipeline does instead</h3>
{C.table(["Harness step (Part A)", "In a declarative pipeline", "Compared with the harness"], STEP_MAP)}
<h3>Part A's nights, replayed in your head on Lakeflow</h3>
<ul><li><b>Night 1:</b> fact_otif is computed. L5 gets -1, 13 Nov is flagged incomplete (if you added the completeness column). No bookmark code was needed.</li>
<li><b>Night 2:</b> the view refreshes. L3 shows 8 delivered, L5 becomes key 4 by itself. Good. But nobody records that 11 Nov and 13 Nov changed after they were shown. Was it a refresh of three days or of all history? The event log tells you afterwards; you did not choose.</li>
<li><b>The crash:</b> the engine retries, and each table's refresh is all or nothing. Good, and no code needed.</li>
<li><b>The careless join:</b> caught only if you wrote the grain check view. Without it, the doubled L3 goes straight to the dashboard.</li></ul>
</section>

<section id="c-pros" class="part"><p class="eyebrow">Part C · 3</p><h2>Pros and cons</h2>
<h3>Pros</h3>{C.table(["Pro", "What it gives", "Matters most when"], PROS)}
<h3>Cons</h3>{C.table(["Con", "What goes wrong", "What to do about it"], CONS)}
<h3>Verdict per kind of table</h3>{vtable(["Gold table", "Declarative way", "Verdict"], FIT_KINDS)}
<h3>How to choose</h3>
<ul><li><b>Go all declarative</b> when you are on Databricks, the facts are small to medium, nobody needs a record of changed past numbers, and the team wants the least code.</li>
<li><b>Go hybrid</b> (our default) when some facts feed finance or regulators, when history is large, or when late data is common. Lakeflow builds the dimensions and aggregates, the harness builds those facts, and one Databricks job runs them in order.</li>
<li><b>Go harness only</b> when the same platform must run on other clouds or engines, or when every gold table needs the same audit trail.</li>
<li>In all three, keep the build a plain pure function. Then moving between them is a change of wrapper, not a rewrite.</li></ul>
<p>Cost per DBU, open source vs Lakeflow, and where declarative helps in bronze to silver: <a href="/learn/spark-declarative-pipelines/">Declarative or not</a>. SCD Type 2 with AUTO CDC against our own code: <a href="/learn/scd2-auto-cdc-vs-pyspark/">SCD Type 2 on Databricks</a>.</p>
</section>"""


QA_EXTRA = [
    ("Why are there so many types of fact table?", "Because business questions come in different shapes. Events that happened once need a row per event (transaction). Levels like stock need a row per period even on quiet days (periodic snapshot). Processes with several steps need one row updated as it moves (accumulating snapshot). Events with nothing to measure need rows without numbers (factless). Busy questions need a summary (aggregate), and comparing sources needs one shared grain (consolidated). The kind decides how a pipeline reads changes and how it writes."),
    ("Can the silver to gold layer be built as a Databricks declarative pipeline?", "Yes. AUTO CDC builds SCD Type 2 dimensions and materialized views build facts and aggregates, with expectations for quality. What it does not give is control over which windows are rebuilt, a restatement log, correction plans, a full row ledger or checks across rows. A hybrid works best: Lakeflow for dimensions and aggregates, a harness for facts that need that bookkeeping."),
    ("What are reader, processor and writer in a data pipeline?", "The reader finds what changed since the last run and reads the rows of the windows it touches. The processor is a pure function holding the business rule, which takes data in and returns data out. The writer puts the result into the target safely, by replacing whole windows or merging by key, and only then is the bookmark moved."),
]
