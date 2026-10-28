"""Publish the certification prep sites under /certifications/.

The prep repos stay the source: edit there, then run this and commit the site.

    python3 _certifications/sync.py

Copies each repo's built pages (HTML, scripts, styles, images, lab code) into
certifications/<slug>/, keeping the repo's own folder layout so every relative
link still works. Leaves out build scripts, notes and question sources
(*.py except lab skeletons, *.md, parts/, src/). Links that point outside
what is copied go to the repo's own GitHub Pages copy instead. Ends by checking
that every relative link in the copy resolves, and refuses if one does not.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

HOME = Path.home()
SITE = Path(__file__).resolve().parents[1]
OUT = SITE / "certifications"

SOURCES = [
    {
        "slug": "claude-certified-architect",
        "repo": HOME / "ClaudeCertifiedArchitect",
        "folders": ["CCA-F", "CCAR-P"],
        "pages": "https://basantchoudhary.github.io/ClaudeCertifiedArchitect/",
    },
    {
        "slug": "azure-ai-engineer",
        "repo": HOME / "AzureAIEngineer",
        "folders": ["."],
        "pages": "https://basantchoudhary.github.io/AzureAIEngineer/",
    },
]

SKIP_FILES = {"publish_traps.sh", "link_plain.py", "build_plain_mocks.py"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", "parts", "src", ".claude"}
SKIP_SUFFIXES = {".md", ".pyc"}
SKIP_LINKS = ("http", "mailto:", "data:", "javascript:", "//", "/", "${")
LINK = re.compile(r'((?:href|src)\s*=\s*["\'])([^"\'#?]+)')


def wanted(path: Path, root: Path) -> bool:
    parts = path.relative_to(root).parts
    if path.name in SKIP_FILES:
        return False
    if any(p in SKIP_DIRS or p.startswith(".") for p in parts):
        return False
    if path.suffix in SKIP_SUFFIXES:
        return False
    return not (path.suffix == ".py" and "skeletons" not in parts)


def copy(source: dict) -> list[Path]:
    repo, dest = source["repo"], OUT / source["slug"]
    if dest.exists():
        shutil.rmtree(dest)
    copied = []
    for folder in source["folders"]:
        for path in sorted((repo / folder).rglob("*")):
            if path.is_file() and wanted(path, repo):
                target = dest / path.relative_to(repo)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
                copied.append(target)
    return copied


def relink(source: dict, files: list[Path]) -> int:
    """Point links at files that were not copied to the repo's GitHub Pages copy.
    The copy mirrors the repo root, so the path below `dest` is the path below
    the repo's Pages URL."""
    dest, changed = (OUT / source["slug"]).resolve(), 0
    for page in (f for f in files if f.suffix == ".html"):
        text = page.read_text(errors="ignore")

        def outward(m: re.Match[str]) -> str:
            nonlocal changed
            link = m.group(2)
            if link.startswith(SKIP_LINKS) or "{" in link:
                return m.group(0)
            target = (page.parent / link).resolve()
            in_repo = source["repo"] / os.path.relpath(target, dest)
            if target.exists() or not target.is_relative_to(dest) or not in_repo.exists():
                return m.group(0)
            changed += 1
            return m.group(1) + source["pages"] + os.path.relpath(target, dest).replace(os.sep, "/")

        new = LINK.sub(outward, text)
        if new != text:
            page.write_text(new)
    return changed


def broken(files: list[Path]) -> list[str]:
    found = []
    for page in (f for f in files if f.suffix in (".html", ".css")):
        for _, link in LINK.findall(page.read_text(errors="ignore")):
            if link.startswith(SKIP_LINKS) or "{" in link:
                continue
            if not (page.parent / link).exists():
                found.append(f"{page.relative_to(SITE)} -> {link}")
    return found


def commit(repo: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), "log", "-1", "--format=%h %cs"], capture_output=True, text=True
    ).stdout.strip()


def main() -> None:
    lines = []
    all_files: list[Path] = []
    for source in SOURCES:
        files = copy(source)
        moved = relink(source, files)
        all_files += files
        lines.append(
            f"{source['slug']}: {len(files)} files from {source['repo'].name}"
            f" {commit(source['repo'])}; {moved} links pointed at GitHub Pages"
        )
    bad = broken(all_files)
    if bad:
        raise SystemExit("broken links in the copy:\n  " + "\n  ".join(bad[:30]))
    (SITE / "_certifications" / "last-sync.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
