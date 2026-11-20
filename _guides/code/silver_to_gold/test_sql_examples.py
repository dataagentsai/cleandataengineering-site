"""Table-driven checks for the SQL examples: every (example, claim, query, expected) row is one test case.

    uv run --no-project --with duckdb --with pytest python -m pytest -q test_sql_examples.py
"""
import pytest

import run_sql
import sql_dimensions as DIM
import sql_facts as FACT

# One DuckDB connection per page, run once; each case below then reads from it.
CASES = []
for page, examples in (("dimensions", DIM.EXAMPLES), ("facts", FACT.EXAMPLES)):
    _, results = run_sql.run_page(examples)
    CASES += [pytest.param(ex, label, ok, got, want, id=f"{page}:{ex}:{label}") for ex, label, ok, got, want in results]


@pytest.mark.parametrize("example,label,ok,got,want", CASES)
def test_claim_holds(example, label, ok, got, want):
    assert ok, f"{example}: {label}: got {got!r}, expected {want!r}"


@pytest.mark.parametrize("page,examples,minimum", [("dimensions", DIM.EXAMPLES, 11), ("facts", FACT.EXAMPLES, 8)])
def test_every_example_has_checks_and_a_trap(page, examples, minimum):
    assert len(examples) >= minimum
    for ex in examples:
        assert ex["checks"], ex["id"]
        assert ex["trap"] and ex["when"] and ex["question"], ex["id"]
