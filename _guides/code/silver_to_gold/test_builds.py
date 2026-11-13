"""Table-driven tests: small tables in, expected rows out. Each case is one line in a table."""
from datetime import date as D

import pytest

import builds as B
import harness as H
from data import DELS_S, LINES_S

OPEN = D(9999, 12, 31)

# ---------------------------------------------------------------- the OTIF build (transaction fact)
# case name, order line (qty, promised), deliveries [(qty, day)], expected (qty_delivered, on_time, in_full, otif)
OTIF_CASES = [
    ("on time and in full", (10, 10), [(10, 10)], (10, 1, 1, 1)),
    ("delivered a day late", (5, 10), [(5, 11)], (5, 0, 1, 0)),
    ("on time but short", (8, 11), [(6, 11)], (6, 1, 0, 0)),
    ("two deliveries: no double counting", (8, 11), [(6, 11), (2, 14)], (8, 0, 1, 0)),
    ("nothing delivered yet", (4, 13), [], (0, 0, 0, 0)),
    ("early delivery counts as on time", (4, 13), [(4, 12)], (4, 1, 1, 1)),
]


@pytest.mark.parametrize("name,line,dels,expected", OTIF_CASES, ids=[c[0] for c in OTIF_CASES])
def test_otif(spark, name, line, dels, expected):
    lines = spark.createDataFrame([("L1", "O1", "D1", "R15", line[0], D(2026, 11, line[1]), 1)], LINES_S)
    d = spark.createDataFrame([(f"X{i}", "L1", "WH-A", q, D(2026, 11, day), i) for i, (q, day) in enumerate(dels)], DELS_S)
    rows = B.build_otif(lines, d, {}).collect()
    assert len(rows) == 1, "one row per order line, always"
    r = rows[0]
    assert (r.qty_ordered, r.qty_delivered, r.on_time, r.in_full, r.otif) == (line[0],) + expected


# ---------------------------------------------------------------- key lookup as of the event
DIM = [("D7", 2, D(2024, 3, 1), D(2026, 11, 12)), ("D7", 3, D(2026, 11, 12), OPEN)]
KEY_CASES = [
    ("before the move: North version", "D7", 11, 2),
    ("on the day of the move: new version", "D7", 12, 3),
    ("after the move: West version", "D7", 13, 3),
    ("dealer not in the dimension yet", "D9", 13, -1),
]


@pytest.mark.parametrize("name,dealer,day,key", KEY_CASES, ids=[c[0] for c in KEY_CASES])
def test_lookup_keys(spark, name, dealer, day, key):
    dim = spark.createDataFrame(DIM, "dealer_id string, dealer_key int, valid_from date, valid_to date")
    fact = spark.createDataFrame([("L1", dealer, D(2026, 11, day))], "line_id string, dealer_id string, promised_date date")
    out = H.lookup_keys(fact, dim, "dealer_id", "dealer_key", "promised_date").collect()
    assert [r.dealer_key for r in out] == [key]


# ---------------------------------------------------------------- the other fact kinds
MOVES_S = "warehouse string, product string, move_date date, qty int"
STOCK_CASES = [
    ("stock carried over a quiet day", [(10, 100)], [10, 11], [100, 100]),
    ("in and out on one day", [(10, 100), (10, -10)], [10], [90]),
    ("a day before any movement shows 0", [(11, 5)], [10, 11], [0, 5]),
]


@pytest.mark.parametrize("name,moves,days,expected", STOCK_CASES, ids=[c[0] for c in STOCK_CASES])
def test_daily_stock(spark, name, moves, days, expected):
    m = spark.createDataFrame([("WH-A", "R15", D(2026, 11, d), q) for d, q in moves], MOVES_S)
    ds = spark.createDataFrame([(D(2026, 11, d),) for d in days], "day date")
    out = B.build_daily_stock(m, ds, {}).orderBy("snapshot_date").collect()
    assert [r.stock_on_hand for r in out] == expected


LIFE_CASES = [
    ("only ordered so far", [("ordered", 8)], (8, None, None, None)),
    ("ordered, shipped, delivered", [("ordered", 8), ("shipped", 10), ("delivered", 14)], (8, 10, 14, 6)),
]


@pytest.mark.parametrize("name,events,expected", LIFE_CASES, ids=[c[0] for c in LIFE_CASES])
def test_lifecycle(spark, name, events, expected):
    ev = spark.createDataFrame([("L3", m, D(2026, 11, d)) for m, d in events], "line_id string, milestone string, at date")
    r = B.build_line_lifecycle(ev, {}).collect()[0]
    day = lambda x: x.day if x else None  # noqa: E731
    assert (day(r.ordered_at), day(r.shipped_at), day(r.delivered_at), r.days_to_deliver) == expected


VISIT_CASES = [
    ("one visit", [("R1", "D1", 10)], 1),
    ("same visit sent twice counts once", [("R1", "D1", 10), ("R1", "D1", 10)], 1),
    ("two days are two visits", [("R1", "D1", 10), ("R1", "D1", 11)], 2),
]


@pytest.mark.parametrize("name,visits,expected", VISIT_CASES, ids=[c[0] for c in VISIT_CASES])
def test_visits(spark, name, visits, expected):
    v = spark.createDataFrame([(r, d, D(2026, 11, x)) for r, d, x in visits], "rep_id string, dealer_id string, visit_date date")
    assert B.build_visits(v, {}).count() == expected


PVA_CASES = [
    ("plan and actual", [("D1", 20)], [("D1", 15)], {"D1": (20, 15, -5)}),
    ("plan but no orders", [("D9", 5)], [], {"D9": (5, 0, -5)}),
    ("orders but no plan", [], [("D7", 12)], {"D7": (0, 12, 12)}),
]


@pytest.mark.parametrize("name,plan,actual,expected", PVA_CASES, ids=[c[0] for c in PVA_CASES])
def test_plan_vs_actual(spark, name, plan, actual, expected):
    p = spark.createDataFrame([(d, "2026-11", q) for d, q in plan], "dealer_id string, month string, plan_qty int")
    lines = spark.createDataFrame([(f"L{i}", "O", d, "R15", q, D(2026, 11, 10), i) for i, (d, q) in enumerate(actual)], LINES_S)
    out = {r.dealer_id: (r.plan_qty, r.actual_qty, r.gap) for r in B.build_plan_vs_actual(p, lines, {}).collect()}
    assert out == expected
