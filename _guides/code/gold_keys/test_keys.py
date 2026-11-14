"""Table-driven tests for the key functions."""
from datetime import date as D

import pytest

import keys as K

OPEN = D(9999, 12, 31)

DK_CASES = [
    ("new dealers get the next numbers", [], [("ERP", "D1"), ("ERP", "D7")], {("ERP", "D1"): 1, ("ERP", "D7"): 2}),
    ("a known code keeps its number", [("ERP", "D1", 1)], [("ERP", "D1"), ("ERP", "D9")], {("ERP", "D1"): 1, ("ERP", "D9"): 2}),
    ("a new code for a known dealer reuses its number", [("ERP", "D7", 2)], [("ERP2", "DLR-0007", "D7")], {("ERP", "D7"): 2, ("ERP2", "DLR-0007"): 2}),
]


@pytest.mark.parametrize("name,keymap,incoming,expected", DK_CASES, ids=[c[0] for c in DK_CASES])
def test_durable_keys(spark, name, keymap, incoming, expected):
    km = spark.createDataFrame(keymap, K.KEYMAP_S)
    if incoming and len(incoming[0]) == 3:
        inc = spark.createDataFrame(incoming, "source string, business_key string, same_as string")
    else:
        inc = spark.createDataFrame(incoming, "source string, business_key string")
    out = {(r.source, r.business_key): r.dealer_dk for r in K.assign_durable_keys(km, inc).collect()}
    assert out == expected


SK_CASES = [
    ("first versions", [], [(1, D(2024, 1, 1)), (2, D(2024, 3, 1))], {(1, D(2024, 1, 1)): 101, (2, D(2024, 3, 1)): 102}),
    ("a new version gets a new key; old keys stay", [(2, D(2024, 3, 1), 102)], [(2, D(2024, 3, 1)), (2, D(2026, 11, 12))],
     {(2, D(2024, 3, 1)): 102, (2, D(2026, 11, 12)): 103}),
]


@pytest.mark.parametrize("name,skmap,versions,expected", SK_CASES, ids=[c[0] for c in SK_CASES])
def test_version_keys(spark, name, skmap, versions, expected):
    sm = spark.createDataFrame(skmap, K.SKMAP_S)
    v = spark.createDataFrame(versions, "dealer_dk int, valid_from date")
    out = {(r.dealer_dk, r.valid_from): r.dealer_sk for r in K.assign_version_keys(sm, v).collect()}
    assert out == expected


ASOF_CASES = [
    ("before the move", "D7", 11, 102), ("on the day of the move", "D7", 12, 103), ("unknown dealer", "D9", 13, -1)]


@pytest.mark.parametrize("name,dealer,day,sk", ASOF_CASES, ids=[c[0] for c in ASOF_CASES])
def test_lookup(spark, name, dealer, day, sk):
    dim = spark.createDataFrame([("D7", 102, 2, D(2024, 3, 1), D(2026, 11, 12)), ("D7", 103, 2, D(2026, 11, 12), OPEN)],
                                "business_key string, dealer_sk int, dealer_dk int, valid_from date, valid_to date")
    f = spark.createDataFrame([("L", dealer, D(2026, 11, day))], "line_id string, dealer_id string, promised_date date")
    assert [r.dealer_sk for r in K.lookup_as_of(f, dim, "promised_date").collect()] == [sk]


def test_hash_is_stable_but_follows_the_code(spark):
    a = spark.createDataFrame([("D7", D(2024, 3, 1)), ("D7", D(2024, 3, 1)), ("DLR-0007", D(2024, 3, 1))], "business_key string, valid_from date")
    h = [r.hash_sk for r in K.hash_key(a, ["business_key", "valid_from"]).collect()]
    assert h[0] == h[1] and h[0] != h[2]


def test_lookup_via_keymap_new_system_same_version(spark):
    km = spark.createDataFrame([("ERP", "D7", 2), ("ERP2", "DLR-0007", 2)], K.KEYMAP_S)
    dim = spark.createDataFrame([(103, 2, D(2026, 11, 12), OPEN)], "dealer_sk int, dealer_dk int, valid_from date, valid_to date")
    f = spark.createDataFrame([("L7", "ERP2", "DLR-0007", D(2026, 11, 14)), ("L4", "ERP", "D7", D(2026, 11, 13))],
                              "line_id string, source string, dealer_id string, promised_date date")
    assert sorted((r.line_id, r.dealer_sk) for r in K.lookup_via_keymap(f, km, dim, "promised_date").collect()) == [("L4", 103), ("L7", 103)]


# ---------------------------------------------------------------- bridge tables
import bridge as BR  # noqa: E402

BRIDGE_CASES = [
    ("one rep: whole credit", [("G1", "Asha", 1.0)], {"Asha": 40000.0}),
    ("two reps 60/40: total stays 40,000", [("G2", "Asha", 0.6), ("G2", "Vik", 0.4)], {"Asha": 24000.0, "Vik": 16000.0}),
    ("three equal reps", [("G3", "Asha", 1 / 3), ("G3", "Vik", 1 / 3), ("G3", "Ravi", 1 / 3)], {"Asha": 13333.33, "Vik": 13333.33, "Ravi": 13333.33}),
]


@pytest.mark.parametrize("name,bridge,expected", BRIDGE_CASES, ids=[c[0] for c in BRIDGE_CASES])
def test_allocate(spark, name, bridge, expected):
    g = bridge[0][0]
    fact = spark.createDataFrame([("L3", g, 40000.0)], "line_id string, rep_group string, revenue double")
    b = spark.createDataFrame(bridge, "rep_group string, rep string, weight double")
    out = {r.rep: round(r.revenue_allocated, 2) for r in BR.allocate(fact, b, "rep_group", "revenue").collect()}
    assert out == expected and round(sum(out.values())) == 40000
    assert BR.weights_ok(b, "rep_group").count() == 0


def test_weights_that_do_not_add_up_are_caught(spark):
    b = spark.createDataFrame([("G2", "Asha", 0.6), ("G2", "Vik", 0.6)], "rep_group string, rep string, weight double")
    assert [r.rep_group for r in BR.weights_ok(b, "rep_group").collect()] == ["G2"]
