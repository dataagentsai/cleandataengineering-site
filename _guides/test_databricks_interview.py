"""Table-driven checks for the Databricks interview guide (run: python3 -m pytest _guides/test_databricks_interview.py)."""
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import databricks_interview as DI  # noqa: E402

PAGES = DI.build_all()
FORBIDDEN = [r"octave", r"jkh", r"dataagents(?!ai)", r"agenttwin\.si"]  # the dataagentsai GitHub org links are allowed
# every topic the owner asked for must have a page (slug -> words that must appear on it)
REQUIRED = [
    ("delta-maintenance", ["OPTIMIZE", "VACUUM", "REORG", "RESTORE", "liquid clustering"]),
    ("row-level-security", ["ROW FILTER", "SET MASK", "dynamic views"]),
    ("compute-choice", ["serverless", "job cluster", "streaming", "driver"]),
    ("joins", ["semi", "anti", "sort-merge", "broadcast"]),
    ("skew-and-shuffle", ["salting", "AQE", "shuffle"]),
    ("aqe-photon-po", ["Photon", "Predictive Optimization", "vectorized"]),
    ("cost-and-performance", ["cost lever", "performance lever", "system.billing.usage"]),
    ("declarative-and-semantic", ["declarative", "Spark Declarative Pipelines", "MEASURE("]),
    ("asset-bundles", ["databricks.yml", "targets", "Terraform"]),
    ("lakeflow-connect", ["Auto Loader", "federation", "CDC"]),
    ("uniform", ["field ID", "column mapping", "metadata.json"]),
    ("vector-search", ["HNSW", "Delta Sync", "embedding model", "multi-tenancy"]),
    ("dbt-and-odcs", ["ref(", "ODCS", "Bitol"]),
    ("egress-and-ingress", ["egress", "ingress", "NAT gateway"]),
    ("table-maintenance-pictures", ["REORG", "deletion vector", "VERSION AS OF", "200 tiny files"]),
    ("clustering-and-compaction", ["snappy", "Hilbert", "minNumFiles", "partitioning"]),
    ("maintenance-strategy", ["Predictive Optimization", "external table", "691,000", "availableNow"]),
    ("slow-writes", ["8,000", "repartition", "optimized writes"]),
    ("backup-and-recovery-azure", ["deep clone", "UNDROP", "Terraform", "geo-redundant"]),
    ("tagging-best-practices", ["system.billing.usage", "budget", "governed tags", "chargeback"]),
    ("row-level-security", ["Photon", "SQL function", "entitlements"]),
    ("compute-choice", ["performance mode", "Premium"]),
    ("hard-problems-and-questions", ["Question bank", "Major challenges", "exactly-once"]),
]


@pytest.mark.parametrize("slug,words", REQUIRED)
def test_topic_present(slug, words):
    html = PAGES[f"learn/databricks-interview/{slug}/index.html"]
    for w in words:
        assert w.lower() in html.lower(), f"{slug} is missing {w!r}"


@pytest.mark.parametrize("rel", sorted(PAGES))
def test_page_rules(rel):
    html = PAGES[rel]
    low = html.lower()
    for f in FORBIDDEN:
        assert not re.search(f, low), f"{rel} mentions {f}"
    assert "<h1>" in html and "prefers-color-scheme: dark" not in low  # light only


@pytest.mark.parametrize("p", DI.PAGES, ids=lambda p: p["slug"])
def test_metadata(p):
    assert len(p["desc"]) <= 200 and p["title"] and p["short"]


@pytest.mark.parametrize("rel", sorted(PAGES))
def test_tables_are_rectangular(rel):
    for table in re.findall(r"<table.*?</table>", PAGES[rel], flags=re.S):
        widths = {len(re.findall(r"<t[hd]", row)) for row in re.findall(r"<tr>.*?</tr>", table, flags=re.S)}
        assert len(widths) == 1, f"{rel}: ragged table {widths}"


def test_hub_links_every_page():
    hub = PAGES["learn/databricks-interview/index.html"]
    for p in DI.PAGES:
        assert f'{DI.BASE}{p["slug"]}/' in hub
