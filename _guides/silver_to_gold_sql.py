"""SQL example pages of /learn/silver-to-gold/: dimension-examples and fact-examples.

Reads _guides/code/silver_to_gold/sql_results.json, written by run_sql.py (DuckDB 1.4, every check passing), so
every table on these pages is a real result. Imported by silver_to_gold_split.py.
"""
import json
import sys
from html import escape as E
from pathlib import Path

HERE = Path(__file__).parent
CODE = HERE / "code" / "silver_to_gold"
sys.path.insert(0, str(CODE))
import sql_dimensions as DIM  # noqa: E402
import sql_facts as FACT  # noqa: E402

RES = json.loads((CODE / "sql_results.json").read_text())

CSS = """<style>
  .gh .ex { border:var(--line); border-radius:var(--wob); padding:6px 20px 14px; margin:26px 0; background:#fff; }
  .gh .ex h2 { font-size:30px; }
  .gh .q1 { background:var(--peri-wash); border:1.5px solid var(--ink); border-radius:var(--wob); padding:8px 16px; margin:8px 0 12px; font-size:16.5px; }
  .gh .step { margin:16px 0 4px; font-size:15.5px; }
  .gh .step b.no { display:inline-block; min-width:24px; font-family:var(--hand); font-size:22px; font-weight:400; }
  .gh pre.code { margin:6px 0 8px; }
  .gh .out { margin:0 0 6px; } .gh .out table.t td { font-family:var(--mono); font-size:12.5px; white-space:nowrap; }
  .gh .out .lbl, .gh .src .lbl { font-size:11.5px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:var(--faint); margin:6px 0 0; }
  .gh .src h4 { font-family:var(--mono); font-size:13.5px; margin:10px 0 0; font-weight:500; }
  .gh .wt { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin:14px 0 0; } @media (max-width:760px){ .gh .wt { grid-template-columns:1fr; } }
  .gh .wt div { border:1.5px solid var(--ink); border-radius:10px; padding:8px 14px; font-size:14.5px; }
  .gh .wt .w { background:var(--mint-wash); } .gh .wt .t { background:var(--rose-wash); }
  .gh .wt b { display:block; margin-bottom:2px; }
</style>"""

DIALECT = [
    ["A run of days", "unnest(generate_series(d1, d2, INTERVAL 1 DAY))", "explode(sequence(d1, d2, INTERVAL 1 DAY))"],
    ["Days between two dates", "date_diff('day', a, b)", "datediff(b, a)"],
    ["Date as 20261113", "strftime(d, '%Y%m%d')", "date_format(d, 'yyyyMMdd')"],
    ["Name of the weekday", "dayname(d)", "date_format(d, 'EEEE')"],
    ["Count rows that meet a condition", "count(*) FILTER (WHERE x)", "count_if(x) (the FILTER form also works)"],
    ["Keep the first row per group", "QUALIFY row_number() OVER (...) = 1", "A subquery with row_number() (QUALIFY exists on Databricks, not in open-source Spark 3.5)"],
    ["Hand out surrogate keys", "row_number() OVER (ORDER BY ...)", "An identity column, or a key map table, so keys never move between runs"],
    ["MERGE", "MERGE INTO ... USING ... (DuckDB 1.4)", "MERGE INTO on a Delta table"],
]

DIM_VERDICT = {
    "d-type1": ("Pursue", "The default for names, codes, descriptions"),
    "d-type2": ("Pursue", "Whenever the past matters for grouping"),
    "d-type3": ("Pursue with care", "Only for 'moved from X to Y' or a transition period"),
    "d-mini": ("Pursue with care", "Only for big dimensions with fast-changing bands"),
    "d-date": ("Pursue", "Every fact has a date"),
    "d-role": ("Pursue", "No second date table, ever"),
    "d-junk": ("Pursue with care", "Only when several small flags crowd a big fact"),
    "d-degenerate": ("Pursue", "Free: keep the number in the fact"),
    "d-bridge": ("Pursue with care", "Only for true many-to-many; always weight"),
    "d-hierarchy": ("Pursue", "Flatten once so reports never recurse"),
    "d-inferred": ("Pursue", "Facts that beat their dimension are normal"),
}
FACT_VERDICT = {
    "f-transaction": ("Pursue", "The default"),
    "f-periodic": ("Pursue", "For levels and balances"),
    "f-accumulating": ("Pursue", "For multi-step processes"),
    "f-factless": ("Pursue", "For coverage and 'who did not' questions"),
    "f-aggregate": ("Pursue with care", "Only where a question is slow and frequent"),
    "f-consolidated": ("Pursue", "For plan against actual"),
    "f-allocation": ("Pursue", "Whenever a header amount must reach lines"),
    "f-adjustment": ("Pursue", "For finance-grade numbers that must not silently change"),
}


def table(cols, rows, cls="t"):
    h = "".join(f"<th>{E(c)}</th>" for c in cols)
    b = "".join("<tr>" + "".join(f"<td>{E(c)}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tw"><table class="{cls}"><tr>{h}</tr>{b}</table></div>' if rows else '<p class="note">(no rows: that is the right answer here)</p>'


def example(ex, res, n):
    out = [f'<section id="{ex["id"]}" class="ex"><p class="eyebrow">{n}. {E(ex["kind"])}</p><h2>{E(ex["title"])}</h2>']
    out.append(f'<div class="q1"><b>The question:</b> {E(ex["question"])}</div>')
    if ex.get("grain"):
        out.append(f'<p><b>One row means:</b> {E(ex["grain"])}</p>')
    out.append(f'<p>{E(ex["plain"])}</p>')
    if ex.get("note"):
        out.append(f'<p class="note">{E(ex["note"])}</p>')
    for s in res["sources"]:
        out.append(f'<div class="src"><h4>{E(s["name"])}</h4><p class="lbl" style="margin-top:0">Silver in</p>{table(s["cols"], s["rows"])}'
                   f'<details class="code"><summary>Setup SQL to copy and run</summary><pre class="code"><code>{E(s["sql"])}</code></pre></details></div>')
    for i, st in enumerate(res["steps"], 1):
        out.append(f'<p class="step"><b class="no">{i}.</b> {E(st["cap"])}</p><pre class="code"><code>{E(st["sql"])}</code></pre>')
        if st["out"]:
            out.append(f'<div class="out"><p class="lbl">Result</p>{table(st["out"]["cols"], st["out"]["rows"])}</div>')
    out.append(f'<div class="wt"><div class="w"><b>Use it when</b>{E(ex["when"])}</div><div class="t"><b>The trap</b>{E(ex["trap"])}</div></div></section>')
    return "".join(out)


def pick_table(examples, verdicts):
    rows = "".join(
        f'<tr><td><a href="#{ex["id"]}"><b>{E(ex["short"])}</b></a></td><td>{E(ex["question"])}</td><td class="v">{E(verdicts[ex["id"]][0])}: {E(verdicts[ex["id"]][1])}</td></tr>'
        for ex in examples)
    return f'<div class="tw"><table class="t"><tr><th>Example</th><th>The question it answers</th><th>Verdict</th></tr>{rows}</table></div>'


def dialect_box(page_kind):
    return (f'<section id="dialect"><p class="eyebrow">Before you start</p><h2>How to read and run these</h2>'
            f'<p>Every example is plain SQL on tiny tables: <b>silver in, SQL, gold out</b>. The tables you see are the real results of running the SQL, '
            f'in DuckDB 1.4, from <code>_guides/code/silver_to_gold/</code> (<code>run_sql.py</code> runs all {len(DIM.EXAMPLES) + len(FACT.EXAMPLES)} examples; '
            f'a table-driven test checks {sum(len(e["checks"]) for e in DIM.EXAMPLES + FACT.EXAMPLES)} claims such as "the shares add up to the freight"). '
            f'Each <b>Setup SQL</b> box creates the silver table, so you can paste an example into any DuckDB and run it.</p>'
            f'<p>The tyre company is the one from the <a href="/learn/silver-to-gold/worked-example/">worked example</a>. '
            f'These pages show the <i>business rule</i> of each table, which is the part you write. '
            f'Finding changed rows, picking windows and moving the bookmark is the harness\'s job, shown on the <a href="/learn/silver-to-gold/">other pages</a>.</p>'
            f'<details class="code"><summary>If you run Spark or Databricks SQL instead: the few words that change</summary>'
            f'{table(["Thing", "DuckDB (used here)", "Spark / Databricks SQL"], DIALECT)}</details></section>')


def dimension_sections():
    exs = DIM.EXAMPLES
    return (dialect_box("dim")
            + '<section id="pick"><p class="eyebrow">Which one?</p><h2>The eleven examples at a glance</h2>'
              '<p>Start with Type 1 and Type 2: they cover most dimensions. The others solve one specific problem each; reach for one only when you have that problem.</p>'
            + pick_table(exs, DIM_VERDICT) + '</section>'
            + "".join(example(ex, RES["dimensions"][ex["id"]], i) for i, ex in enumerate(exs, 1)))


def fact_sections():
    exs = FACT.EXAMPLES
    return (dialect_box("fact")
            + '<section id="pick"><p class="eyebrow">Which one?</p><h2>The eight examples at a glance</h2>'
              '<p>Read them in order: the first builds <code>fact_order_line</code>, and the aggregate and plan-against-actual examples read it. '
              'The kind is chosen by the shape of the question, not by the data.</p>'
            + pick_table(exs, FACT_VERDICT) + '</section>'
            + "".join(example(ex, RES["facts"][ex["id"]], i) for i, ex in enumerate(exs, 1)))
