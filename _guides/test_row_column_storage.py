"""Table-driven checks for the row vs column page (run: python3 -m pytest _guides/test_row_column_storage.py)."""
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "row_column_storage"))
import demo  # noqa: E402
import row_column_storage as RC  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HTML = RC.render()

REQUIRED = [
    ("layouts", ["Row-oriented", "Column-oriented", "row groups", "stripes", "late materialization", "same position", "rebuilt"]),
    ("formats", ["CSV", "JSON Lines", "Avro", "Parquet", "ORC", "Arrow"]),
    ("databases", ["PostgreSQL", "ClickHouse", "Redshift", "DuckDB", "Lakebase", "Databricks SQL"]),
    ("numbers", ["5,437,347", "2,458,232", "1,444,777", "1,722,204", "1.19 times", "90,344", "1,100,402"]),
    ("verdicts and honesty", ["Pursue", "Drop", "Not confirmed", "The demo is not Parquet"]),
]


@pytest.mark.parametrize("name,words", REQUIRED)
def test_required_words(name, words):
    assert [w for w in words if w not in HTML] == []


def test_forbidden_names():
    assert not re.search(r"octave|jkh|dataagents(?!ai)", HTML, re.I)


def test_internal_links_exist():
    for href in set(re.findall(r'href="(/[^"#?]*)"', HTML)):
        target = ROOT / href.strip("/")
        assert (target / "index.html").exists() or target.is_file() or href == "/", href


def test_no_unfilled_placeholders():
    assert "{{" not in HTML


# the figures printed on the page are what the demo returns for n=200,000 (sizes are fixed by the seed)
FULL = demo.run()
SIZE_CASES = [
    ("raw row", FULL["raw_row"], 5_437_347),
    ("zlib row", FULL["zlib_row"], 1_722_204),
    ("zlib column", FULL["zlib_col"], 1_444_777),
    ("region alone", FULL["zlib_col_each"]["region"], 90_344),
    ("bytes read by column query", FULL["bytes_read_col"], 2_458_232),
]


@pytest.mark.parametrize("name,got,expected", SIZE_CASES)
def test_page_sizes_match_demo(name, got, expected):
    assert got == expected


def test_demo_claims_hold():
    assert FULL["same_answer"]
    assert FULL["zlib_col"] < FULL["zlib_row"]
    assert FULL["bytes_read_col"] / FULL["bytes_read_row"] < 0.5
    assert FULL["zlib_col_each"]["region"] * 10 < 1_100_402
