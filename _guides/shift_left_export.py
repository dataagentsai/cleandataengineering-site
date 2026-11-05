"""Export the shift-left bundle's checks for the site: one JSON file the guide reads.

    uv run --no-project --with pyyaml python3 _guides/shift_left_export.py [path-to-shift-left-bundle]
    python3 _guides/shift_left.py

Reads the bundle's catalog (catalog/checks/*.yaml), its Databricks binding (bindings/databricks.yaml) and
its adapter registry (src/shiftleft/adapters), and writes _guides/shift_left_checks.json. Run it whenever the
checks change; the guide build itself needs no YAML library. Product names of our own earlier tools never reach
the site: they are mapped to a plain description here.
"""
import glob
import json
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
BUNDLE = Path(sys.argv[1] if len(sys.argv) > 1 else Path.home() / "shift-left-bundle")
OUT = HERE / "shift_left_checks.json"

# binding tool -> (name shown on the site, who provides it)
#   open     = an open-source tool's own rule, configured by us
#   ours     = a rule or report we wrote
#   platform = the data platform's own command
TOOLS = {
    "ruff": ("Ruff", "open"), "sqlfluff": ("SQLFluff", "open"), "sparkdoctor": ("SparkDoctor", "open"),
    "pyspark-antipattern": ("pyspark-antipattern", "open"), "gitleaks": ("gitleaks", "open"),
    "osv-scanner": ("osv-scanner", "open"), "vulture": ("vulture", "open"), "complexipy": ("complexipy", "open"),
    "jscpd": ("jscpd", "open"), "nbstripout": ("nbstripout", "open"), "dbt-bouncer": ("dbt-bouncer", "open"),
    "coverage": ("coverage.py and diff-cover", "open"), "mutmut": ("mutmut", "open"),
    "import-linter": ("import-linter", "open"), "scorecard": ("OpenSSF Scorecard", "open"),
    "pip-licenses": ("pip-licenses", "open"), "pylint": ("pylint", "open"),
    "opengrep": ("Opengrep (our rule)", "ours"),
    "mv-explain": ("Databricks EXPLAIN for materialized views", "platform"),
    "costlens": ("Our cost rules", "ours"), "patterns": ("Our pattern rules", "ours"),
    "purity": ("Our purity report", "ours"), "plan-harness": ("Our empty-table plan check", "ours"),
    "metricview": ("Our metric view checks", "ours"), "repo-checks": ("Our repo checks", "ours"),
    "repo-review": ("Our repo-review plugins", "ours"), "bundle-rules": ("Our bundle config rules", "ours"),
    "sqlglot": ("Our SQL rules (on sqlglot)", "ours"), "shiftleft-tests": ("Our test rules", "ours"),
    "test-kit": ("Our test kit", "ours"),
    "bundle-validate": ("databricks bundle validate", "platform"), "pip-audit": ("pip-audit", "open"),
    "dbt-score": ("dbt-score", "open"), "dbt-project-evaluator": ("dbt-project-evaluator", "open"),
}
# What each tool does, in plain words (from the bundle's REUSE.md and binding)
WHAT = {
    "ruff": "Python lint, clean code and security rules (most of Bandit), one fast tool",
    "complexipy": "cognitive complexity per function: how hard it is to read",
    "vulture": "dead code", "pylint": "module length (on trial)",
    "jscpd": "copied code in Python and SQL",
    "opengrep": "pattern-rule engine; used for one rule of ours (credentials in config files)",
    "sqlfluff": "SQL lint and format, Databricks dialect", "sqlglot": "SQL syntax tree; we write our own rules on it",
    "gitleaks": "secrets in files and git history", "pip-audit": "known vulnerabilities in Python libraries (fallback)",
    "osv-scanner": "known vulnerabilities from lockfiles (the OSV database)",
    "nbstripout": "strips notebook outputs on commit, so data samples don't leak",
    "dbt-bouncer": "rules over a dbt project's manifest, offline", "dbt-score": "scores dbt model metadata, offline",
    "dbt-project-evaluator": "dbt project best-practice rules (needs the warehouse, so trial only)",
    "mv-explain": "asks Databricks whether a materialized view can refresh incrementally, before deploy",
    "metricview": "checks metric view YAML and parses its expressions",
    "repo-checks": "what a repository is missing: tests, lockfile, pre-commit, CI setup",
    "bundle-rules": "Databricks bundle config rules: tags, timeouts, worker limits, auto-termination",
    "sparkdoctor": "PySpark performance lint; only its mapped rules are used",
    "pyspark-antipattern": "PySpark lint; two of its rules adopted (join with no condition, inferSchema)",
    "test-kit": "standard test tables for known data patterns: SCD2, dedupe, incremental, late data",
    "pip-licenses": "lists library licences (on trial)",
    "coverage": "test coverage, measured on changed lines only",
    "mutmut": "mutation testing: changes the code and checks a test fails",
    "import-linter": "architecture rule: the pure core never imports the IO code",
    "repo-review": "plugin host for repository checks; we write the data-repo plugins",
    "scorecard": "scores a repository's security practices", "bundle-validate": "validates Databricks bundle config",
    "costlens": "cost rules for SQL, Python, query plans and job config, from our earlier cost-analysis work",
    "plan-harness": "EXPLAIN on empty tables built from real schemas, on local Spark",
    "purity": "pure, impure or unknown for every function, with the reason and a refactor hint",
    "patterns": "our own pattern rules over Python syntax trees and notebook text",
    "shiftleft-tests": "rules over test files and coverage data",
}
# How a check is run when its tool has no adapter in the runner
DELIVERY = {"coverage": "CI template", "test-kit": "Test kit (pytest)", "shiftleft-tests": "Test kit (pytest)",
            "repo-review": "repo-review plugin"}
STATUS = {"adopt": "Open-source rule, configured", "cost": "Our earlier cost rules", "build": "Written by us",
          "trial": "On trial"}


def registry():
    """Adapter names the runner wires, and check ids an adapter emits directly."""
    names = {}
    for f in (BUNDLE / "src/shiftleft/adapters").glob("*.py"):
        m = re.search(r'^NAME\s*=\s*"([^"]+)"', f.read_text(), re.M)
        if m:
            names[f.stem] = m.group(1)
    init = (BUNDLE / "src/shiftleft/adapters/__init__.py").read_text()
    reg = re.search(r"REGISTRY = \{m\.NAME: m for m in \(([^)]*)\)", init, re.S).group(1)
    wired = {names[s.strip()] for s in reg.split(",") if s.strip() in names}
    emitted = set()
    for f in list((BUNDLE / "src/shiftleft/adapters").glob("*.py")) + list((BUNDLE / "src/shiftleft").glob("*.py")):
        emitted |= set(re.findall(r'Finding\("(SL-[A-Z-]+-\d+[a-z]?)"', f.read_text()))
    return wired, emitted


def main():
    binding = yaml.safe_load((BUNDLE / "bindings/databricks.yaml").read_text())
    families = yaml.safe_load((BUNDLE / "core/families.yaml").read_text())
    stages = yaml.safe_load((BUNDLE / "core/stages.yaml").read_text())
    gates = yaml.safe_load((BUNDLE / "core/gates.yaml").read_text())["levels"]
    wired, emitted = registry()
    checks = []
    for f in sorted(glob.glob(str(BUNDLE / "catalog/checks/*.yaml"))):
        for c in yaml.safe_load(Path(f).read_text()):
            b = binding["checks"].get(c["id"], {})
            tool = b.get("tool", "")
            shown, kind = TOOLS.get(tool, (tool or "not mapped", "ours"))
            if b.get("status") == "trial":
                kind = "trial"
            if tool in wired or c["id"] in emitted:
                runs = "Runner"
            else:
                runs = DELIVERY.get(tool, "Not wired yet")
            fam = c["id"].rsplit("-", 1)[0].removeprefix("SL-")
            checks.append({
                "id": c["id"], "title": c["title"], "family": fam,
                "family_name": families.get(fam, {}).get("name", fam), "level": c["level"], "stage": c["stage"],
                "gate": c["gate"], "found_by": c["found_by"], "applies_to": c.get("applies_to", []),
                "cost": c.get("cost_impact") or "none", "statement": c["statement"], "why": c.get("why", ""),
                "fix": c.get("fix", ""), "dac": c.get("dac", []), "provider": shown, "provider_kind": kind,
                "rules": [str(r) for r in b.get("rules", [])], "how": STATUS.get(b.get("status", ""), ""),
                "runs": runs,
            })
    tools = []
    used = Counter(binding["checks"][c["id"]]["tool"] for c in checks if c["id"] in binding["checks"])
    for name, meta in binding["tools"].items():
        shown, kind = TOOLS.get(name, (name, "ours"))
        licence = "ours" if name == "costlens" else str(meta.get("licence", "")).split(" (")[0]
        ways = Counter(c["runs"] for c in checks if binding["checks"].get(c["id"], {}).get("tool") == name)
        tools.append({"tool": shown, "kind": kind, "licence": licence, "what": WHAT.get(name, ""),
                      "checks": used.get(name, 0), "wired": name in wired,
                      "runs": ways.most_common(1)[0][0] if ways else "Not used by a check yet"})
    data = {"source": "shift-left-bundle catalog + bindings/databricks.yaml", "count": len(checks),
            "families": {k: v.get("name", k) for k, v in families.items()},
            "stages": {k: v.get("name", k) for k, v in stages.items()}, "gates": gates,
            "checks": checks, "tools": tools}
    text = json.dumps(data, indent=1, ensure_ascii=False)
    assert "costlens" not in text.lower() and "costsherlock" not in text.lower(), "own product name leaked"
    OUT.write_text(text)
    print(f"{len(checks)} checks, {len(tools)} tools -> {OUT}")


if __name__ == "__main__":
    main()
