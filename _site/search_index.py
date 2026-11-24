"""Rebuild the site search index (Pagefind) into /pagefind/. Run after any page rebuild, then commit /pagefind/.

    python3 _site/search_index.py

Header and footer are excluded so the menu text doesn't match every query. The search box and /search/
page are in _site/nav.py and search/search.js.
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECTIONS = "about ai-engineering ai-for-cause business certifications concepts data-engineering deep-tech forward-deployed how-we-work leaders learn lab mindset papers paths platforms problems projects research road-safety simulators writing".split()
subprocess.run(["npx", "-y", "pagefind@1.3.0", "--site", str(ROOT), "--output-path", str(ROOT / "pagefind"),
                "--exclude-selectors", "header", "--exclude-selectors", "footer",
                "--glob", "{" + ",".join(SECTIONS) + "}/**/*.html"], check=True)
