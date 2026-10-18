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
