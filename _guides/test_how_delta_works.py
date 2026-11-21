"""Table-driven checks for the 'How reads and writes work' section
(run: python3 -m pytest _guides/test_how_delta_works.py). The pages read their numbers from results/*.json,
so these tests check that (a) the claims in the text follow from the measurements and (b) hard-coded numbers in FAQs match."""
import json
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import how_delta_works as H  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PAGES = {s: H.render(s) for s, *_ in H.PAGES}
R = H.R
Q = R["read"]["queries"]
J = R["joins"]["joins"]
SH = R["joins"]["shuffles"]
OPS = {o["label"]: o for o in R["write"]["ops"]}
D = R["spark"]["driver"]


def met(op, key):
    return int(OPS[op]["operationMetrics"].get(key, 0))


# (page, words that must appear)
REQUIRED = [
    ("", ["delta log", "Driver", "Executor", "Data skipping", "Predicate pushdown", "Real runs, not invented numbers"]),
    ("files-on-disk/", ["_delta_log", "add action", "minValues", "numRecords", "checkpoint", "_last_checkpoint", "row group", "footer", "VACUUM"]),
    ("read-path/", ["Six kinds of query", "data skipping", "first 32 columns", "dataSkippingNumIndexedCols", "dataSkippingStatsColumns", "ANALYZE TABLE", "LocalTableScan", "ReadSchema", "PushedFilters", "1 TB"]),
    ("layout/", ["small file", "400 files", "Z-order", "Liquid clustering", "dictionary", "256 MB", "Not measured"]),
    ("joins/", ["BroadcastHashJoin", "SortMergeJoin", "AQE", "dynamic partition pruning", "dynamicpruning", "skew", "256 MB"]),
    ("inside-spark/", ["Narrow", "Wide", "Exchange", "hashpartitioning", "rangepartitioning", "RoundRobinPartitioning", "SinglePartition", "BroadcastExchange", "collect()", "cache", "maxResultSize"]),
    ("python-and-jvm/", ["Py4J", "BatchEvalPython", "Arrow", "collect()", "process id"]),
    ("photon/", ["Photon", "vectorised", "C++", "hash joins", "2 seconds", "not measured", "ColumnarToRow"]),
    ("plan-and-ui/", ["EXPLAIN", "Spark UI", "query profile", "DESCRIBE DETAIL", "DESCRIBE HISTORY", "Exchange", "PushedFilters", "Not confirmed"]),
    ("write-path/", ["copy on write", "deletion vector", "readVersion", "isolationLevel", "MERGE", "OPTIMIZE", "VERSION AS OF", "VACUUM", "Method."]),
    ("clickhouse/", ["granule", "8192", "primary.idx", "sparse", "LowCardinality", "async_insert", "Not confirmed", "1,083"]),
]


@pytest.mark.parametrize("slug,words", REQUIRED)
def test_required_words(slug, words):
    assert [w for w in words if w not in PAGES[slug]] == []


@pytest.mark.parametrize("slug", list(PAGES))
def test_no_placeholders_and_clean(slug):
    html = PAGES[slug]
    assert "{{" not in html
    assert not re.search(r"octave|jkh|dataagents(?!ai)", html, re.I)


@pytest.mark.parametrize("slug", list(PAGES))
def test_internal_links_exist(slug):
    for href in set(re.findall(r'href="(/[^"#?]*)"', PAGES[slug])):
        target = ROOT / href.strip("/")
        assert (target / "index.html").exists() or target.is_file() or href == "/" or href.startswith("/learn/how-delta-works/"), href


@pytest.mark.parametrize("slug", list(PAGES))
def test_every_figure_has_a_description(slug):
    for m_ in re.finditer(r"<svg [^>]*>", PAGES[slug]):
        assert 'role="img"' in m_.group(0) and 'aria-label="' in m_.group(0)


# claims that follow from the measurements (a failure means the page text would now be wrong)
CLAIMS = [
    ("sorted column skips files", lambda: Q["q3_event_date"]["files"] < Q["q1_select_star"]["files"] / 5),
    ("random column skips nothing", lambda: Q["q4_user_id"]["files"] == Q["q1_select_star"]["files"]),
    ("column pruning reads far fewer bytes", lambda: Q["q2_two_columns"]["input_bytes"] < Q["q1_select_star"]["input_bytes"] * 0.4),
    ("no stats still reads less via Parquet footer", lambda: Q["q5_late_code_default_stats"]["input_bytes"] < Q["q1_select_star"]["input_bytes"] * 0.2 and Q["q5_late_code_default_stats"]["files"] == Q["q1_select_star"]["files"]),
    ("stats on all columns skips files", lambda: Q["q5b_late_code_stats_on_all"]["files"] == 1),
    ("zorder skips files", lambda: Q["q4z_user_id_zorder"]["files"] < R["read"]["zorder"]["files"] / 5),
    ("first add has 32 stat columns, not late_code", lambda: R["read"]["log_add_first_stats"]["stat_columns"] == 32 and not R["read"]["log_add_first_stats"]["has_late_code_stat"]),
    ("stats-on-all table has 40", lambda: R["read"]["log_stats_cols_T2"] == 40),
    ("small files need more tasks and bytes", lambda: R["read"]["small_files"]["s_all"]["tasks"] > R["read"]["small_files"]["t_all"]["tasks"] and R["build"]["S"]["bytes"] > R["build"]["T"]["bytes"]),
    ("count(*) answered from the log", lambda: R["count"]["count_star"]["first_plan_line"].startswith("LocalTableScan") and not R["count"]["count_star"]["reads_parquet"]),
    ("broadcast join has no shuffle", lambda: J["j1_big_small_broadcast"]["shuffle_write_bytes"] == 0 and J["j1_big_small_broadcast"]["join_kind"] == "BroadcastHashJoin"),
    ("forced sort-merge shuffles", lambda: J["j2_big_small_forced_sortmerge"]["join_kind"] == "SortMergeJoin" and J["j2_big_small_forced_sortmerge"]["shuffle_write_bytes"] > 1_000_000),
    ("aqe changed the join but still shuffled", lambda: J["j4b_big_big_aqe_on"]["join_kind"] == "BroadcastHashJoin" and J["j4b_big_big_aqe_on"]["shuffle_write_bytes"] > 1_000_000),
    ("dpp reads fewer files and rows", lambda: J["j5b_partitioned_dpp_on"]["has_dynamic_pruning"] and J["j5b_partitioned_dpp_on"]["files"] < J["j5_partitioned_dpp_off"]["files"] and J["j5b_partitioned_dpp_on"]["rows"] < J["j5_partitioned_dpp_off"]["rows"]),
    ("groupby shuffles little, orderby a lot", lambda: SH["wide_groupby"]["shuffle_write_bytes"] < 10_000 and SH["wide_orderby"]["shuffle_write_bytes"] > 1_000_000),
    ("narrow has no exchange", lambda: SH["narrow_filter_select"]["n_exchanges"] == 0),
    ("collect of all columns is the big one", lambda: D["collect_all_cols"]["result_bytes"] > 10 * D["collect_2_cols"]["result_bytes"] > 10 * D["count"]["result_bytes"]),
    ("udf slower than builtin and has a python node", lambda: R["spark"]["pyjvm"]["runs"]["python_udf"]["seconds"] > R["spark"]["pyjvm"]["runs"]["builtin_expr"]["seconds"] and any("BatchEvalPython" in l for l in R["spark"]["pyjvm"]["runs"]["python_udf"]["plan"])),
    ("python and JVM are different processes", lambda: R["spark"]["pyjvm"]["driver_python_pid"] != R["spark"]["pyjvm"]["jvm_pid"] and R["spark"]["pyjvm"]["driver_python_pid"] not in R["spark"]["pyjvm"]["worker_pids"]),
    ("cache reads no files", lambda: R["spark"]["cache"]["after"]["files"] == 0 and R["spark"]["cache"]["before"]["files"] > 0),
    ("append only adds", lambda: OPS["insert_append"]["actions"].get("remove", 0) == 0 and OPS["insert_append"]["actions"]["add"] > 0),
    ("update one file rewrites one", lambda: met("update_one_file", "numRemovedFiles") == 1 and met("update_one_file", "numCopiedRows") > 9000),
    ("delete with dv rewrites nothing", lambda: met("delete_with_deletion_vector", "numCopiedRows") == 0 and OPS["delete_with_deletion_vector"]["dv_adds"] == 1 and met("delete_with_deletion_vector", "numAddedFiles") == 0),
    ("merge cost follows files touched", lambda: met("merge_keys_in_every_file", "numTargetFilesRemoved") > 5 * met("merge_keys_in_one_file", "numTargetFilesRemoved")),
    ("overwrite keeps old files, time travel works", lambda: R["write"]["time_travel"]["parquet_files_on_disk"] > R["write"]["time_travel"]["files_in_current_version"] and R["write"]["time_travel"]["rows_version0"] == 100000),
]


@pytest.mark.parametrize("name,fn", CLAIMS, ids=[c[0] for c in CLAIMS])
def test_claim_follows_from_measurements(name, fn):
    assert fn()


# numbers typed into FAQ answers must equal what the results say
FAQ_NUMBERS = [
    ("inside-spark/", "838 bytes", SH["wide_groupby"]["shuffle_write_bytes"]),
    ("inside-spark/", "32.6 MB", round(SH["wide_orderby"]["shuffle_write_bytes"] / 1e6, 1)),
    ("inside-spark/", "33.1 MB", round(D["collect_all_cols"]["result_bytes"] / 1e6, 1)),
    ("joins/", "32.6 MB", round(J["j2_big_small_forced_sortmerge"]["shuffle_write_bytes"] / 1e6, 1)),
    ("joins/", "6 files and 40,010 rows", None),
    ("write-path/", "9,950", met("delete_rewrite", "numCopiedRows")),
    ("write-path/", "rewrote 10,000", met("update_one_file", "numCopiedRows") + met("update_one_file", "numUpdatedRows")),
]


@pytest.mark.parametrize("slug,text,value", FAQ_NUMBERS)
def test_faq_numbers_match_results(slug, text, value):
    assert text in PAGES[slug]
    if value is not None:
        num = re.sub(r"[^\d.]", "", text.split()[0] if text[0].isdigit() else text.split()[-1])
        assert abs(float(num) - float(value)) < 0.06 or str(value) in text.replace(",", "")
    else:
        assert J["j5b_partitioned_dpp_on"]["files"] == 6 and J["j5b_partitioned_dpp_on"]["rows"] == 40010


def test_lab_scripts_are_in_the_repo():
    lab = Path(__file__).parent / "how_delta_works" / "lab"
    assert {p.name for p in lab.glob("*.py")} >= {"lab.py", "part1_build.py", "part2_read.py", "part3_spark.py", "part3b_joins.py", "part4b_write.py", "part5_count.py"}
