"""Run the SQL examples in DuckDB and write sql_results.json (read by _guides/silver_to_gold_sql.py).

    uv run --no-project --with duckdb python run_sql.py

Each page's examples share one in-memory connection, in order. Every check must pass or this exits non-zero.
"""
import json
import sys
from decimal import Decimal
from pathlib import Path

import duckdb

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import sql_dimensions as DIM  # noqa: E402
import sql_facts as FACT  # noqa: E402


def cell(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, Decimal):
        return format(v, "f")
    if isinstance(v, float):
        return f"{v:g}"
    return str(v)


def grab(con, sql):
    cur = con.execute(sql)
    return {"cols": [d[0] for d in cur.description], "rows": [[cell(c) for c in r] for r in cur.fetchall()]}


def same(got, want):
    if isinstance(want, bool):
        return bool(got) == want
    if isinstance(want, (int, float)) and not isinstance(want, bool):
        return abs(float(got) - float(want)) < 1e-9
    return str(got) == str(want)


def run_page(examples):
    con = duckdb.connect(":memory:")
    out, results = {}, []
    for ex in examples:
        srcs = []
        for name, sql in ex["sources"]:
            con.execute(sql)
            srcs.append({"name": name, "sql": sql.strip(), **grab(con, f"SELECT * FROM {name}")})
        steps = []
        for st in ex["steps"]:
            con.execute(st["sql"])
            shown = None
            if st["show"]:
                shown = grab(con, st["sql"].strip().rstrip(";") if st["show"] == "=" else st["show"])
            steps.append({"cap": st["cap"], "sql": st["sql"].strip(), "out": shown})
        for label, sql, want in ex["checks"]:
            got = con.execute(sql).fetchone()[0]
            results.append((ex["id"], label, same(got, want), got, want))
        out[ex["id"]] = {"sources": srcs, "steps": steps}
    return out, results


def main():
    allres, bad = {}, []
    for page, examples in (("dimensions", DIM.EXAMPLES), ("facts", FACT.EXAMPLES)):
        out, results = run_page(examples)
        allres[page] = out
        bad += [r for r in results if not r[2]]
        print(page, len(examples), "examples,", len(results), "checks")
    (HERE / "sql_results.json").write_text(json.dumps(allres, indent=1))
    for b in bad:
        print("FAILED:", b)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
