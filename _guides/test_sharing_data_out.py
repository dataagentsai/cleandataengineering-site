"""Table-driven checks for the sharing-data-out page (run: python3 -m pytest _guides/test_sharing_data_out.py)."""
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import databricks_compute as DC  # noqa: E402
import sharing_data_out_build as SB  # noqa: E402

SB.build()
PAGE_DEF = next(p for p in DC.PAGES if p["slug"] == "sharing-data-out")
HTML = DC.render(PAGE_DEF)
FORBIDDEN = [r"octave", r"jkh", r"dataagents(?!ai)"]

METHODS = [f"A{i}." for i in range(1, 9)] + [f"B{i}." for i in range(1, 9)]


@pytest.mark.parametrize("label", METHODS)
def test_each_method_has_its_sections(label):
    assert re.search(rf"<h2>{re.escape(label)}", HTML), f"missing heading {label}"


@pytest.mark.parametrize("phrase", ["Under the hood", "Use it when", "Do not use it when", "Cost and performance", "Security", "Pursue", "Drop", "Not confirmed"])
def test_required_phrases(phrase):
    assert phrase in HTML


@pytest.mark.parametrize("pattern", FORBIDDEN)
def test_no_forbidden_words(pattern):
    assert not re.search(pattern, HTML, re.I)


def test_every_method_has_one_figure_and_cost_security_table():
    assert HTML.count("<figure>") >= 16
    assert HTML.count("Cost, performance and security") == 16


def test_ids_are_unique():
    ids = re.findall(r'<section id="(s\d+)"', HTML)
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("anchor", re.findall(r'href="#(s\d+)"', HTML))
def test_internal_anchors_resolve(anchor):
    assert f'id="{anchor}"' in HTML
