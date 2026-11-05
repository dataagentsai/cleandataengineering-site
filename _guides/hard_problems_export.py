"""Export the hard problems of each data layer for the site: one JSON file the guide reads.

    uv run --no-project --with pyyaml python3 _guides/hard_problems_export.py [path-to-data-platform-catalog]
    python3 _guides/hard_problems.py

Reads the catalog's layers (layers/*.yaml), the practices they reuse as anti-patterns (practices/*.yaml) and the
ADR titles (adr/ADR-*.md), and writes _guides/hard_problems.json. Related shift-left checks are matched through the
data assurance obligations both cite, using _guides/shift_left_checks.json. Run it whenever the layers change; the
guide build itself needs no YAML library. Names that must never reach the site stop the export.
"""
import glob
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
CAT = Path(sys.argv[1] if len(sys.argv) > 1 else Path.home() / "data-platform-catalog")
OUT = HERE / "hard_problems.json"
FORBIDDEN = re.compile(r"octave|jkh|dataagents|costlens|costsherlock|apollo", re.I)

# framework parts, in plain words
COMPONENTS = {
    "contracts": "data contracts", "metadata_store": "metadata store", "puller": "puller", "lander": "lander",
    "silver_engine": "silver engine", "gold_harness": "gold harness", "des": "data expectation services",
    "semantic_generators": "semantic layer generators", "observability": "observability", "agents": "agents",
    "app": "the platform app",
}


def practices():
    out = {}
    for f in glob.glob(str(CAT / "practices" / "*.yaml")):
        for p in yaml.safe_load(open(f)) or []:
            if isinstance(p, dict) and p.get("id"):
                out[p["id"]] = p
    return out


def adr_titles():
    out = {}
    for f in glob.glob(str(CAT / "adr" / "ADR-*.md")):
        m = re.search(r"^# (ADR-\d+) (.+)$", open(f).read(), re.M)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def check_index():
    p = HERE / "shift_left_checks.json"
    if not p.exists():
        return {}
    idx = {}
    for c in json.loads(p.read_text())["checks"]:
        for d in c.get("dac", []):
            idx.setdefault(d, []).append(c["id"])
    return idx


def main():
    prac, adrs, checks = practices(), adr_titles(), check_index()
    layers = []
    for f in sorted(glob.glob(str(CAT / "layers" / "*.yaml"))):
        L = yaml.safe_load(open(f))
        chs = []
        for c in L.get("challenges", []):
            dac = c.get("dac", []) or []
            rel = sorted({cid for d in dac for cid in checks.get(d, [])})
            chs.append({
                "id": c["id"], "title": c["title"], "goes_wrong": c.get("goes_wrong", ""),
                "example": c.get("example", ""), "solution": c.get("solution", ""),
                "verdict": c["verdict"], "status": c["status"], "dac": dac,
                "adr": [{"id": a, "title": adrs.get(a, "")} for a in c.get("adr", []) or []],
                "world_day": c.get("world_day"), "checks": rel[:6], "n_checks": len(rel),
            })
        aps = []
        for a in L.get("anti_patterns", []) or []:
            if "practice" in a:
                p = prac.get(a["practice"])
                if not p:
                    sys.exit(f"{f}: practice {a['practice']} not found")
                aps.append({"title": p["title"], "why": p.get("why", ""), "instead": p.get("instead", "")})
            else:
                aps.append({"title": a["title"], "why": a.get("why", ""), "instead": a.get("instead", "")})
        layers.append({
            "id": L["id"], "order": L["order"], "title": L["title"], "purpose": L.get("purpose", ""),
            "components": [COMPONENTS.get(x, x.replace("_", " ")) for x in L.get("components", []) or []],
            "hop": "_to_" in L["id"], "challenges": chs, "anti_patterns": aps,
        })
    text = json.dumps({"layers": layers}, ensure_ascii=False, indent=1)
    bad = FORBIDDEN.search(text)
    if bad:
        sys.exit(f"refusing to export: '{bad.group(0)}' must not reach the site")
    OUT.write_text(text + "\n")
    n = sum(len(x["challenges"]) for x in layers)
    print(f"{OUT}: {len(layers)} layers, {n} challenges, {sum(len(x['anti_patterns']) for x in layers)} anti-patterns")


if __name__ == "__main__":
    main()
