# cleandataengineering.ai

Static site for Clean Data Engineering: learn together, teach, community projects, research and product building. Plain HTML; small Python generators in the `_*` folders.

Served by GitHub Pages from `main`, root.

## /learn/agent-harness/

Generated, not hand-edited. Source: `~/agent-harness-tutorial` (the tutorial) and `~/Agent-Harness-Series.html` (the Series).
Republish with:

    python3 ~/agent-harness-tutorial/build.py --publish ~/cleandataengineering-site/learn/agent-harness

Publish mode points source links at the public GitHub repos and redacts live-deployment identifiers
(subscription and tenant ids, the Azure resource suffix) from every page, including the Series copy.

## /paths/

Learning paths: six roles (data, AI, LLM, ML, software, forward-deployed) × platforms (AWS, Azure, Google Cloud,
Databricks, open source) × three levels (Crawl, Walk, Run). Data in `_paths/data.py` (concepts with the product per
platform, projects, levels); build with `python3 _paths/build.py`. It also writes the home page's picker and role cards
between the `picker` and `paths` markers.

Key concepts (the ideas that are the same on every cloud) live in `_paths/concepts.py` (CARDS + ROLE_GROUPS); the same build
writes `/concepts/` (index by role and A–Z) and `/concepts/<id>/`, shows each role's concepts on its path page and each level's
key ideas on the platform pages. Drawings for concept pages are in `_paths/diagrams.py`.

## /learn/data-platform-sim/ (DataTwin Studio)

`_sim/record_batch.py` records a real run on local Spark + Delta (run with `env -u SPARK_HOME ~/CostIntelligence1/.venv/bin/python _sim/record_batch.py`) into `_sim/data/batch.json`; `python3 _sim/build.py` writes the studio page with the data embedded. Re-record only when the scene changes.

## Menu, footer and hubs

The site menu and footer live in `_site/nav.py` (Learn · Simulators · Projects · Research · Writing · About, with
dropdowns on desktop). `python3 _site/nav.py` writes them into every page that carries the site menu; generators copy
them from the home page, so run it after any build that touches hand-made pages. `python3 _site/hubs.py` writes the
hub pages `/simulators/`, `/research/` and `/about/`. The home page's first screen is the four-door loop (see it, run
it, build it, prove it); its styles are in the `home-css` block, which `_site/theme.py` leaves alone.

## SEO

`python3 _site/seo.py` writes `sitemap.xml`, `robots.txt` (search and AI crawlers welcome) and `llms.txt`, fills a
missing description or canonical on pages copied in from other repos, and audits every page (`--strict` exits 1 on
errors). Run it last, after every build. The growth plan is `_plan/GROWTH-PLAN.md`.

## /writing/

Posts are Markdown in `_writing/posts/` (Jekyll never serves folders starting with `_`).
Build with `python3 _writing/build.py`. Posts with `draft: true` are skipped; preview them with
`python3 _writing/build.py --drafts` (writes `_writing/preview/`, git-ignored).
The build writes each post page, `/writing/` (filterable), `/writing/feed.xml`, the home page's latest-three list,
and `_writing/cross/<slug>/` with a LinkedIn text and a dev.to copy (canonical link set) for cross-posting.

## /projects/

One page per project, generated from `_projects/data_a.py` (open standards & builds), `data_b.py` (learning builds)
and `data_c.py` (open to lead). Build with `python3 _projects/build.py`. Every page has the same ten sections:
purpose, business benefits, status and how to join, requirements, a very high-level architecture (no tool names),
tech stack per platform (✓ = built), what needs to be done, roles, what you'll learn, links.
To update a project, edit its dict (status, work items, good_first) and rebuild. `FDE_READY` in build.py marks
projects someone could take into a real customer setting (the forward-deployed practice label).

## The look

One theme, light only: white background, soft pastels (periwinkle = AI, mint = LLM, rose = data, butter = cost),
1.5px hand-drawn outlines, DM Sans for reading and Patrick Hand for headings, sketch-style diagrams.
It lives in `_site/theme.py` (`python3 _site/theme.py` re-applies it to the home page, /learn/ and the
certifications hub and redraws the home cartoon). /writing/ and /projects/ copy the home page's style when they build.
