"""Run the dbt version over the same three nights as e2e.py and compare its gold with the harness's.

    python run_dbt.py /path/to/dbt     (dbt-core 1.12 + dbt-duckdb; writes dbt_results.json)
"""
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
import data as X  # noqa: E402

DBT = sys.argv[1] if len(sys.argv) > 1 else "dbt"
KEYS = {"r1": [(1, "D1", "2024-01-01", "9999-12-31"), (2, "D7", "2024-03-01", "2026-11-12"), (3, "D7", "2026-11-12", "9999-12-31")]}
KEYS["r0"] = KEYS["r1"]
KEYS["r2"] = KEYS["r1"] + [(4, "D9", "2026-11-01", "9999-12-31")]
NIGHTS = [("r0", X.LINES_R0, X.DELS_R0, X.FILES_R0), ("r1", X.LINES_R1, X.DELS_R1, X.FILES_R1), ("r2", X.LINES_R2, X.DELS_R2, X.FILES_R2)]


def write(name, head, rows):
    with open(HERE / "seeds" / f"{name}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(head)
        w.writerows(rows)


def dbt(*args):
    p = subprocess.run([DBT, *args, "--profiles-dir", str(HERE), "--project-dir", str(HERE)], capture_output=True, text=True)
    import re
    clean = re.sub(r"\x1b\[[0-9;]*m", "", p.stdout)
    tail = [ln for ln in clean.splitlines() if "PASS" in ln or "FAIL" in ln or "ERROR" in ln or "Done." in ln]
    return p.returncode, tail


shutil.rmtree(HERE / "target", ignore_errors=True)
out = {"nights": []}
for rid, lines, dels, files in NIGHTS:
    write("order_lines", ["line_id", "order_id", "dealer_id", "product", "qty_ordered", "promised_date", "_seq"], lines)
    write("deliveries", ["delivery_id", "line_id", "warehouse", "qty", "delivered_date", "_seq"], dels)
    write("dim_dealer", ["dealer_key", "dealer_id", "valid_from", "valid_to"], KEYS[rid])
    write("delivery_files", ["warehouse", "file_date"], files)
    night = {"run": rid}
    night["seed"] = dbt("seed", "--full-refresh")[0]
    night["run_rc"], night["run_log"] = dbt("run", "--select", "fact_otif")
    night["test_rc"], night["test_log"] = dbt("test", "--select", "fact_otif")
    import duckdb
    c = duckdb.connect(str(HERE / "target" / "otif.duckdb"), read_only=True)
    night["rows"], night["bookmarks"] = c.execute("select count(*), max(_lines_seq) || ' / ' || max(_dels_seq) from main.fact_otif").fetchone()
    c.close()
    out["nights"].append(night)

# a careless join with a unique test: when do dbt's tests run, before or after the write?
rc, log = dbt("build", "--select", "fact_otif_careless")
out["careless"] = {"rc": rc, "log": [ln.split("  ", 1)[-1] for ln in log]}

import duckdb  # noqa: E402
con = duckdb.connect(str(HERE / "target" / "otif.duckdb"), read_only=True)
cols = ["line_id", "dealer_id", "promised_date", "qty_ordered", "qty_delivered", "on_time", "in_full", "otif", "dealer_key", "_is_complete"]
rows = con.execute(f"select {', '.join(cols)} from main.fact_otif order by line_id").fetchall()
dbt_rows = [dict(zip(cols, [str(v) if c == "promised_date" else v for c, v in zip(cols, r)])) for r in rows]
harness = json.loads((HERE.parent / "results.json").read_text())["fact"]["after r2"]
harness_rows = [{c: r[c] for c in cols} for r in harness]
out["careless"]["table_left_behind"] = con.execute(
    "select count(*), sum(qty_ordered) from main.fact_otif_careless where line_id = 'L3'").fetchone()
out["dbt_fact_after_r2"] = dbt_rows
out["same_as_harness"] = dbt_rows == harness_rows
(HERE / "dbt_results.json").write_text(json.dumps(out, indent=1, default=str))
print(json.dumps(out, indent=1, default=str))
