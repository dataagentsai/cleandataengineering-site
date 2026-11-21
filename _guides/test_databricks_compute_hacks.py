"""Table-driven checks for the cost-saving hacks page and the AWS vs Databricks page
(run: python3 -m pytest _guides/test_databricks_compute_hacks.py)."""
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import databricks_compute as DC  # noqa: E402
import dbx_vs_aws as DV  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HACKS = DC.render(next(p for p in DC.PAGES if p["slug"] == "cost-saving-hacks"))
CHOOSE = DC.render(next(p for p in DC.PAGES if p["slug"] == "choosing-compute"))
VS = DV.render()
FORBIDDEN = [r"octave", r"jkh", r"dataagents(?!ai)"]  # the dataagentsai GitHub org links are allowed

# (page name, html, words that must appear)
REQUIRED = [
    ("hacks", HACKS, ["Standard performance mode", "statement timeout", "SPOT_WITH_FALLBACK", "first_on_demand", "Pursue", "Drop", "Not confirmed"]),
    ("hacks", HACKS, ["4 to 6 minutes", "2 days", "runs/submit", "node_timeline"]),
    ("choose", CHOOSE, ["serverless SQL warehouse", "serverless notebooks", "serverless jobs", "serverless pipelines", "Peak Queued Queries", "10 concurrent queries"]),
    ("choose", CHOOSE, ["Common mistakes", "Standard mode", "7 days", "dedicated", "budget policy", "Not confirmed"]),
    ("vs", VS, ["UniForm", "S3 Tables", "Lake Formation", "Predictive Optimization", "Scorecard", "Limitations to know"]),
    ("vs", VS, ["column mapping", "deletion vectors", "64 MB", "private to those customers"]),
]
PAGES = [("hacks", HACKS), ("choose", CHOOSE), ("vs", VS)]


@pytest.mark.parametrize("name,html,words", REQUIRED)
def test_required_words(name, html, words):
    missing = [w for w in words if w.lower() not in html.lower()]
    assert not missing, f"{name}: missing {missing}"


@pytest.mark.parametrize("name,html", PAGES)
def test_no_forbidden_names(name, html):
    hits = [f for f in FORBIDDEN if re.search(f, html, re.I)]
    assert not hits, f"{name}: {hits}"


@pytest.mark.parametrize("name,html", PAGES)
def test_internal_links_exist(name, html):
    bad = []
    for link in set(re.findall(r'href="(/learn/[^"#?]*)"', html)):
        path = ROOT / link.lstrip("/")
        if not ((path / "index.html").exists() or path.exists()):
            bad.append(link)
    assert not bad, f"{name}: missing {bad}"


@pytest.mark.parametrize("name,html", PAGES)
def test_tables_have_verdict_or_winner(name, html):
    # every page that gives options must say Pursue/Drop or name a winner
    assert re.search(r"Pursue|Winner|winner", html), name
