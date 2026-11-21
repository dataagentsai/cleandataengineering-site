"""Table-driven checks for the materialized views page (run: python3 -m pytest _guides/test_materialized_views.py)."""
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import materialized_views as MV  # noqa: E402
import table_view_choice as TV  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HTML = MV.render()

REQUIRED = [
    ("refresh types", ["ROW_BASED", "PARTITION_OVERWRITE", "WINDOW_FUNCTION", "APPEND_ONLY", "GROUP_AGGREGATE", "GENERIC_AGGREGATE", "FULL_RECOMPUTE", "NO_OP"]),
    ("policies", ["AUTO", "INCREMENTAL STRICT", "REFRESH POLICY", "REFRESH MATERIALIZED VIEW name FULL"]),
    ("where it runs", ["Pro or Serverless", "MV/ST", "serverless", "every update is a full recompute", "Runtime 18.1"]),
    ("limits", ["LIMIT", "Recursive CTE", "DECIMAL", "PARTITION BY", "row tracking", "CLONE", "Aliases required"]),
    ("cost", ["serverless Lakeflow pipelines DBUs", "system.billing.usage", "dlt_pipeline_id", "uc_table_name", "no rate"]),
    ("how to know", ["EXPLAIN CREATE MATERIALIZED VIEW", "planning_information", "technique_information", "FLOW_FULL_RECOMPUTE", "MATERIALIZED_VIEW_NOT_INCREMENTALIZABLE", "INCREMENTAL_PLAN_REJECTED_BY_COST_MODEL"]),
    ("verdicts and honesty", ["Pursue", "Drop", "Not confirmed", "sketch"]),
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


def test_every_dollar_claim_is_labelled():
    # no invented prices: any "$" in the page must not be a rate per DBU
    assert not re.search(r"\$\s?\d+(\.\d+)?\s*(per|/)\s*DBU", HTML)


def test_old_page_links_to_new_page():
    assert "/learn/materialized-views/" in TV.render()
