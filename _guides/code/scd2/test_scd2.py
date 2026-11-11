import pytest
from scd2 import plan_scd2, row_hash

O, X = True, False   # open row, closed row
# name                              target rows (id, city, from, to, open)   events (id, op, seq, city)                       closes (id, at)  inserts (id, city, from, to)
CASES = [
    ("new key opens a row",           [],                          [(1, "I", 1, "Pune")],                          [],        [(1, "Pune", 1, None)]),
    ("no-op update is ignored",       [(1, "Pune", 1, None, O)],   [(1, "U", 2, "Pune")],                          [],        []),
    ("change closes and opens",       [(1, "Pune", 1, None, O)],   [(1, "U", 2, "Mumbai")],                        [(1, 2)],  [(1, "Mumbai", 2, None)]),
    ("two changes in one batch",      [(1, "Pune", 1, None, O)],   [(1, "U", 2, "Mumbai"), (1, "U", 3, "Delhi")],  [(1, 2)],  [(1, "Mumbai", 2, 3), (1, "Delhi", 3, None)]),
    ("no-op then change",             [(1, "Pune", 1, None, O)],   [(1, "U", 2, "Pune"), (1, "U", 3, "Delhi")],    [(1, 3)],  [(1, "Delhi", 3, None)]),
    ("delete closes, adds nothing",   [(1, "Pune", 1, None, O)],   [(1, "D", 2, None)],                            [(1, 2)],  []),
    ("delete then re-insert",         [(1, "Pune", 1, None, O)],   [(1, "D", 2, None), (1, "I", 3, "Pune")],       [(1, 2)],  [(1, "Pune", 3, None)]),
    ("late event is skipped",         [(1, "Delhi", 5, None, O)],  [(1, "U", 3, "Mumbai")],                        [],        []),
    ("replayed batch is a no-op",     [(1, "Delhi", 3, None, O)],  [(1, "U", 2, "Mumbai"), (1, "U", 3, "Delhi")],  [],        []),
    ("replay after delete stays deleted", [(1, "Pune", 1, 2, X)],  [(1, "I", 1, "Pune"), (1, "D", 2, None)],       [],        []),
    ("re-insert after delete",        [(1, "Pune", 1, 2, X)],      [(1, "I", 4, "Goa")],                           [],        [(1, "Goa", 4, None)]),
]


def by_key_and_start(row):
    return (row[0], row[2] if len(row) > 2 else row[1])


@pytest.mark.parametrize("name, target, events, closes, inserts", CASES, ids=[c[0] for c in CASES])
def test_plan_scd2(spark, name, target, events, closes, inserts):
    tgt = (spark.createDataFrame(target, "id INT, city STRING, valid_from INT, valid_to INT, is_current BOOLEAN")
                .withColumn("row_hash", row_hash(["city"])))
    ev = spark.createDataFrame(events, "id INT, op STRING, seq INT, city STRING")

    staged = plan_scd2(ev, tgt, key="id", seq="seq", tracked=["city"]).collect()

    got_closes = [(r.id, r.close_at) for r in staged if r.merge_key is not None]
    got_inserts = [(r.id, r.city, r.valid_from, r.valid_to) for r in staged if r.merge_key is None]
    assert sorted(got_closes, key=by_key_and_start) == sorted(closes, key=by_key_and_start)
    assert sorted(got_inserts, key=by_key_and_start) == sorted(inserts, key=by_key_and_start)
