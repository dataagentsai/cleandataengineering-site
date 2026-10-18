# cleandataengineering.ai

Static site for Clean Data Engineering: the open standards and research. Single `index.html`, no build step.

Served by GitHub Pages from `main`, root.

## /learn/agent-harness/

Generated, not hand-edited. Source: `~/agent-harness-tutorial` (the tutorial) and `~/Agent-Harness-Series.html` (the Series).
Republish with:

    python3 ~/agent-harness-tutorial/build.py --publish ~/cleandataengineering-site/learn/agent-harness

Publish mode points source links at the public GitHub repos and redacts live-deployment identifiers
(subscription and tenant ids, the Azure resource suffix) from every page, including the Series copy.
