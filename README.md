# cleandataengineering.ai

Static site for Clean Data Engineering: the open standards and research. Single `index.html`, no build step.

Served by GitHub Pages from `main`, root.

## /learn/agent-harness/

Generated, not hand-edited. Source: `~/agent-harness-tutorial` (the tutorial) and `~/Agent-Harness-Series.html` (the Series).
Republish with:

    python3 ~/agent-harness-tutorial/build.py --publish ~/cleandataengineering-site/learn/agent-harness

Publish mode points source links at the public GitHub repos and redacts live-deployment identifiers
(subscription and tenant ids, the Azure resource suffix) from every page, including the Series copy.

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
