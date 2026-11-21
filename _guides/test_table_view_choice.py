"""Table-driven checks for the table/view/materialized view/metric view page
(run: python3 -m pytest _guides/test_table_view_choice.py)."""
import re
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import table_view_choice as TV  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HTML = TV.render()

REQUIRED = [
    ("ten places", ["ten places", "10 places", "Fan-out", "one_to_many", "MEASURE(conversion_rate)"]),
    ("four objects", ["Physical table", "Normal view", "Materialized view", "Metric view", "Pursue", "Drop", "Not confirmed"]),
    ("incremental", ["Examples where it recomputes everything", "LIMIT", "Recursive CTE", "Expectations", "DECIMAL", "serverless", "INCREMENTAL STRICT", "row tracking"]),
    ("numbers", ["175 / 2200 = 8.0%", "10.0%", "6.4%", "9.5%", "140", "340"]),
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


# (sql, expected rows): the numbers printed on the page are what a real engine returns
DATA = """create table daily(day text, region text, channel text, visits int, orders int, revenue real);
insert into daily values ('2026-01-01','North','web',1000,50,5000),('2026-01-01','South','web',100,20,2000),
('2026-01-02','North','app',1000,100,9000),('2026-01-02','South','web',100,5,400);
create table oh(order_id int, freight real); create table ln(order_id int, line_id int, amt real);
insert into oh values (1,100),(2,40); insert into ln values (1,1,50),(1,2,30),(1,3,20),(2,1,70);"""
SQL_CASES = [
    ("overall ratio", "select round(sum(orders)*100.0/sum(visits),1) from daily", [(8.0,)]),
    ("average of rates", "select round(avg(orders*100.0/visits),1) from daily", [(10.0,)]),
    ("by day", "select round(sum(orders)*100.0/sum(visits),1) from daily group by day order by day", [(6.4,), (9.5,)]),
    ("web only", "select round(sum(orders)*100.0/sum(visits),2) from daily where channel='web'", [(6.25,)]),
    ("freight right", "select sum(freight) from oh", [(140.0,)]),
    ("freight fan-out", "select sum(o.freight) from oh o join ln l using(order_id)", [(340.0,)]),
    ("web revenue by region", "select region, sum(revenue) from daily where channel='web' group by region order by region", [("North", 5000.0), ("South", 2400.0)]),
]


@pytest.mark.parametrize("name,sql,expected", SQL_CASES)
def test_page_numbers_are_real(name, sql, expected):
    c = sqlite3.connect(":memory:")
    c.executescript(DATA)
    assert c.execute(sql).fetchall() == expected
