"""Check the simulator's code references and pin its GitHub links to commits.

    python3 _site/sim_links.py           check only; exit 1 on any broken reference
    python3 _site/sim_links.py --write   check, then write the pinned SRC map into the page

Every "X path:line symbol" in learn/agent-harness-sim/index.html must name a file
that exists, a line inside it, and (when a symbol is given) that symbol within two
lines of it. Links point at each repo's HEAD commit, which must already be on
origin/main, so a line anchor never drifts. The repo map is the tutorial's
(publish.REPOS), not a copy.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "agent-harness-tutorial"))
import publish  # noqa: E402

PAGE = Path(__file__).resolve().parent.parent / "learn/agent-harness-sim/index.html"
REF = re.compile(r"\b(?:([HFSACRE]) |(clean-ai-engineering)/)([\w./-]+\.(?:py|yaml|yml|json|md|toml))(?::(\d+))?(?: ([A-Za-z_][\w.]*))?")
MAP = re.compile(r"/\* src:start.*?\*/.*?/\* src:end \*/", re.S)


def problem(root, rel, line, symbol):
    repo, prefix = publish.REPOS[root]
    f = Path.home() / repo / prefix / rel
    if not f.exists():
        return "no such file"
    if not line:
        return None
    lines = f.read_text(errors="ignore").splitlines()
    n = int(line)
    if n > len(lines):
        return f"line {n} is past the end ({len(lines)} lines)"
    name = symbol.split(".")[-1] if symbol else ""
    if name and not re.search(rf"\b{re.escape(name)}\b", "\n".join(lines[max(0, n - 3):n + 2])):
        return f"'{name}' is not near line {n}: {lines[n - 1].strip()[:60]}"
    return None


def main(write):
    page = PAGE.read_text()
    refs = sorted({(m[0] or "C", m[2], m[3], m[4]) for m in REF.findall(page)})
    bad = [(r, p, l, s, why) for r, p, l, s in refs if (why := problem(r, p, l, s))]
    for r, p, l, s, why in bad:
        print(f"  BROKEN  {r} {p}{':' + l if l else ''} {s}: {why}")
    print(f"{len(refs)} references, {len(bad)} broken")
    if bad:
        sys.exit(1)
    if write:
        for r, p, l, _ in refs:
            publish.github_url(r, p, l)  # refuses an unpushed HEAD or a linked file with uncommitted edits
        roots = sorted({r for r, *_ in refs})
        body = ", ".join(f'{r}:"{publish.github_base(r)}"' for r in roots)
        stamp = "/* src:start (written by _site/sim_links.py; do not edit by hand) */"
        page = MAP.sub(lambda _: f"{stamp}\nconst SRC = {{{body}}};\n/* src:end */", page, count=1)
        PAGE.write_text(page)
        print("pinned:", ", ".join(f"{r}={publish.pin(publish.REPOS[r][0])[0][:7]}" for r in roots))


if __name__ == "__main__":
    main("--write" in sys.argv)
