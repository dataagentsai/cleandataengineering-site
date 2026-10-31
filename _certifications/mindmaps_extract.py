"""Pull every mind map out of the CCA-F mock exams, grouped by exam objective.

    python3 _certifications/mindmaps_extract.py

Reads the "Think it through" layer (deep.map) of every question in Mocks 4 to 7 in
~/ClaudeCertifiedArchitect and writes one file per exam objective to
_certifications/mindmaps/raw/<objective>.json. Those raw files are the input for merging
(similar maps become one) into _certifications/mindmaps/merged/d<domain>.json, which
_certifications/mindmaps.py turns into the page.
"""
import json
import re
from collections import defaultdict
from pathlib import Path

CCA = Path.home() / "ClaudeCertifiedArchitect" / "CCA-F"
OUT = Path(__file__).resolve().parent / "mindmaps" / "raw"
MOCKS = [4, 5, 6, 7]


def objective(q):
    """The exam objective a question tests, as '1.1'. Odd labels fall back to the guide line."""
    for text in (q.get("obj", ""), q.get("deep", {}).get("guide", {}).get("obj", "")):
        m = re.match(r"\s*([1-5]\.[1-7])\b", text)
        if m:
            return m.group(1)
    raise ValueError(f"no objective for {q['id']}")


def main():
    groups = defaultdict(list)
    for n in MOCKS:
        for part in "abc":
            data = json.loads((CCA / f"Foundations-Mock-Exam-{n}" / "parts" / f"{part}.json").read_text())
            for q in data["questions"]:
                d = q["deep"]
                groups[objective(q)].append({
                    "ref": f"m{n}:{q['id']}",
                    "mock": n,
                    "title": d["mapTitle"],
                    "head": d["map"]["head"],
                    "rows": d["map"]["rows"],
                    "rule": d.get("rule", ""),
                })
    OUT.mkdir(parents=True, exist_ok=True)
    for obj, maps in sorted(groups.items()):
        (OUT / f"{obj}.json").write_text(json.dumps(maps, ensure_ascii=False, indent=1))
    print(sum(len(v) for v in groups.values()), "mind maps in", len(groups), "objectives ->", OUT)


if __name__ == "__main__":
    main()
