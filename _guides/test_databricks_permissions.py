"""Table-driven checks for the Databricks permissions page (run: python3 -m pytest _guides/test_databricks_permissions.py)."""
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import databricks_permissions as DP  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HTML = DP.render()

REQUIRED = [
    ("layers", ["Five layers", "Entitlements", "Workspace object ACLs", "Unity Catalog", "Storage credential"]),
    ("admins", ["Account admin", "Metastore admin", "Workspace admin", "Cannot grant on, or change the owner of"]),
    ("read rule", ["USE CATALOG", "USE SCHEMA", "SELECT", "flow down", "Ownership does not flow down"]),
    ("owner vs manage", ["Exactly one principal", "MANAGE", "ALL PRIVILEGES", "No SQL <code>DENY</code>"]),
    ("acls", ["CAN MANAGE RUN", "CAN ATTACH TO", "CAN RESTART", "CAN MONITOR", "CAN QUERY", "IS OWNER"]),
    ("entitlements", ["Allow unrestricted cluster creation", "Consumer access", "Databricks SQL access", "Dedicated", "Standard", "14 September 2026"]),
    ("fine grained", ["ROW FILTER", "COLUMN MASK", "ABAC", "EXCEPT", "is_account_group_member", "Beta"]),
    ("storage and identity", ["READ FILES", "WRITE FILES", "service principal", "OAuth", "ISOLATED", "system.access.audit"]),
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


# privileges named in the Unity Catalog privileges reference; a typo in a GRANT example would fail here
VALID = {"USE CATALOG", "USE SCHEMA", "SELECT", "MODIFY", "CREATE TABLE", "CREATE SCHEMA", "READ METADATA", "READ FILES", "WRITE FILES",
         "CREATE EXTERNAL TABLE", "ALL PRIVILEGES", "EXECUTE", "READ VOLUME", "WRITE VOLUME", "BROWSE", "MANAGE", "REFRESH"}
SECURABLES = {"CATALOG", "SCHEMA", "TABLE", "VIEW", "VOLUME", "FUNCTION", "EXTERNAL LOCATION", "METASTORE"}


def _grants():
    text = re.sub(r"<[^>]+>", "", HTML).replace("&lt;", "<").replace("&gt;", ">")
    return re.findall(r"GRANT ([A-Z ,]+?) ON ([A-Z ]+?) [\w.`<>\-]+ TO ", text)


def test_grant_examples_use_real_privileges():
    found = _grants()
    assert len(found) >= 8
    bad = [(p, s) for privs, s in found for p in [x.strip() for x in privs.split(",")] if p not in VALID or s not in SECURABLES]
    assert bad == []


# (statement start, must appear): the three-part read rule is spelled out in code, not only in prose
RULE = [("USE CATALOG ON CATALOG main", True), ("USE SCHEMA, SELECT ON SCHEMA main.gold", True)]


@pytest.mark.parametrize("stmt,present", RULE)
def test_read_rule_in_code(stmt, present):
    assert (stmt in HTML) == present
