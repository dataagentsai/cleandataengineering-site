"""One-off: pull the 79 hard problems out of ~/Founder-CTO-Path.html (#hard) into _problems/data.json."""
import html, json, re
from pathlib import Path
src = (Path.home() / "Founder-CTO-Path.html").read_text()
sec = src[src.index('<section id="hard">'):src.index('<!-- ============ BENCHMARKS')]
def clean(s): return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()
def slug(t):
    s = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
    return "-".join(s.split("-")[:7])
groups, seen = [], set()
for gid, h3, body in re.findall(r'<div class="tk" id="(hp-[a-z]+)"><h3[^>]*>(.*?)</h3>(.*?)</tbody>', sec, re.S):
    title = clean(re.sub(r'<span class="muted tkn">.*?</span>', "", h3))
    title = re.sub(r"^\d+\.\s*", "", title)
    rows = []
    for tr in re.findall(r"<tr>(.*?)</tr>", body, re.S):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        if len(tds) != 4: continue
        m = re.match(r"(.*?)<span[^>]*>(.*?)</span>", tds[3], re.S)
        verdict, reason = (clean(m.group(1)), clean(m.group(2))) if m else (clean(tds[3]), "")
        s = slug(clean(tds[0]))
        while s in seen: s += "-2"
        seen.add(s)
        rows.append(dict(slug=s, title=clean(tds[0]), why=clean(tds[1]), experiment=clean(tds[2]),
                         verdict=verdict.rstrip("."), reason=reason))
    groups.append(dict(id=gid.replace("hp-", ""), title=title, problems=rows))
Path("_problems/data.json").write_text(json.dumps(groups, indent=1, ensure_ascii=False))
print(sum(len(g["problems"]) for g in groups), "problems in", len(groups), "groups")
for g in groups: print(g["id"], len(g["problems"]), g["title"])

# Public-site cleanup: drop pointers to the author's private plans and CTO-page cards.
FIX = {
    "control-staying-safe-even-if-the-ai": ("reason", "Mostly systems engineering, and a young field."),
    "energy-per-answer": ("reason", "A clear number that every buyer of AI cares about."),
    "too-little-robot-training-data": ("reason", "A data quality problem, which one careful person can measure."),
    "batteries-limit-every-robot": ("experiment", "No solo build. Track how battery energy per kilogram improves each year."),
    "power-and-cooling-for-ai-data-centres": ("reason", "A strong explainer built from public data."),
    "computing-with-light-or-analog-circuits": ("experiment", "No solo build. Track the lab results and the first products."),
    "ageing-and-fusion": ("experiment", "None solo. Read one good review a quarter to keep up."),
    "ai-in-indian-languages-costs-more-and": ("reason", "Few measure it carefully, and the IndiaAI Mission and funders care."),
    "voice-clone-and-upi-scams-in-indian": ("reason", "A clear gap and a clear number."),
    "credit-for-people-with-no-credit-history": ("reason", "Measurable, and lenders and regulators care."),
}
data = json.loads(Path("_problems/data.json").read_text())
for g in data:
    for p in g["problems"]:
        if p["slug"] in FIX:
            k, v = FIX[p["slug"]]
            p[k] = v
Path("_problems/data.json").write_text(json.dumps(data, indent=1, ensure_ascii=False))
print("cleaned", len(FIX))
