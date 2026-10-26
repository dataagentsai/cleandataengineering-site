"""SEO and AI-SEO for the whole site: write sitemap.xml, robots.txt and llms.txt, then audit every page.

    python3 _site/seo.py           # write the three files and print the audit
    python3 _site/seo.py --strict  # same, but exit 1 if any page has an error (use in CI)

Audit per page: <title> length, meta description, canonical, one <h1>, lang, JSON-LD that parses,
and internal links that point at a file that exists. Run it after every build, before you push.
"""
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://cleandataengineering.ai"
SKIP = ("preview", "_", ".")

sys.path.insert(0, str(ROOT / "_paths"))
from data import DISCIPLINES, LEVELS, PLATFORMS  # noqa: E402

AI_BOTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "PerplexityBot",
           "Perplexity-User", "Google-Extended", "Applebot-Extended", "Bingbot", "CCBot", "Meta-ExternalAgent", "DuckAssistBot"]


def pages():
    for p in sorted(ROOT.rglob("*.html")):
        rel = p.relative_to(ROOT)
        if rel.parts[0].startswith(SKIP) or any(x.startswith(".") for x in rel.parts):
            continue
        yield rel


def url_of(rel):
    s = str(rel)
    if s == "index.html":
        return SITE + "/"
    if s.endswith("/index.html"):
        return f"{SITE}/{s[:-10]}"
    return f"{SITE}/{s}"


def lastmod(rel):
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(rel)], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        return out or date.today().isoformat()
    except Exception:
        return date.today().isoformat()


def priority(rel):
    s = str(rel)
    if s == "index.html":
        return "1.0"
    if s.startswith("paths/"):
        return "0.9"
    if s.count("/") <= 1:
        return "0.8"
    return "0.5"


def write_sitemap(rels):
    items = []
    for rel in rels:
        s = (ROOT / rel).read_text(errors="ignore")
        if re.search(r'<meta name="robots" content="[^"]*noindex', s):
            continue
        items.append(f"  <url><loc>{url_of(rel)}</loc><lastmod>{lastmod(rel)}</lastmod><priority>{priority(rel)}</priority></url>")
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                      + "\n".join(items) + "\n</urlset>\n")
    return len(items)


def write_robots():
    lines = ["# Search engines and AI assistants are welcome to read and cite everything here.", "User-agent: *", "Allow: /", ""]
    for b in AI_BOTS:
        lines += [f"User-agent: {b}", "Allow: /", ""]
    lines += [f"Sitemap: {SITE}/sitemap.xml", ""]
    (ROOT / "robots.txt").write_text("\n".join(lines))


def write_llms():
    out = ["# Clean Data Engineering", "",
           "> A free, open community to learn data engineering, AI engineering, LLM engineering, ML engineering, software engineering "
           "and forward-deployed engineering together. Every role has a crawl (beginner), walk (intermediate) and run (advanced) path "
           "on AWS, Azure, Google Cloud, Databricks and open source, with GitHub projects to build at each level. "
           "It also publishes open standards and research on building AI systems that hold up in production.", "",
           "Key idea: learn the concept (the job) once; the cloud product that does it is a binding. "
           "Deterministic first: if ordinary code can do it, code does it; the model handles the rest.", "",
           "## Learning paths", ""]
    out.append(f"- [All paths, role by platform]({SITE}/paths/): pick a role and a platform")
    for d in DISCIPLINES:
        plats = ", ".join(f"[{PLATFORMS[p]}]({SITE}/paths/{d['id']}/{p}/)" for p in d["platforms"])
        out.append(f"- [{d['name']}]({SITE}/paths/{d['id']}/): {d['who']} Platforms: {plats}")
    out += ["", "## Courses", "",
            f"- [The AI Universe]({SITE}/learn/ai-universe/): seven families of AI stacks, concept versus product, on open source, Azure, AWS and Google Cloud",
            f"- [Agent Harness, drawn simply]({SITE}/learn/agent-harness/): one real agent end to end, 167 hand-drawn pages with real code",
            f"- [The Agent Harness Series]({SITE}/learn/agent-harness/series/): the long version, 22 concerns, Azure architecture",
            f"- [Eval Harness, drawn simply]({SITE}/learn/eval-harness/): checking what an agent did from its own traces, rules in YAML",
            f"- [Certification prep]({SITE}/certifications/): free prep for Claude Certified Architect and Azure AI exams",
            "", "## Community projects", "",
            f"- [All projects]({SITE}/projects/): open projects with work packages, good first issues and roles",
            "", "## Research and open standards", "",
            "- [AI Assurance Catalog](https://dataagentsai.github.io/ai-assurance-catalog/): what must be true before an AI system is trusted",
            "- [AI Harness Catalog](https://dataagentsai.github.io/ai-harness-catalog/): what must exist around the model call, 16 layers",
            "- [AgentTwin](https://github.com/dataagentsai/agenttwin): simulate the agent's world to test a real agent",
            "- [Reference Agent](https://github.com/dataagentsai/reference-agent): a customer-support agent with no framework, one module per harness layer",
            f"- [AgentTwin Lab]({SITE}/lab/): research on long-running agents and autonomous fixers",
            "", "## Optional", "",
            f"- [Writing]({SITE}/writing/): notes from production ([RSS]({SITE}/writing/feed.xml))",
            f"- [Start here if AI worries you]({SITE}/mindset/)",
            "- Contact: basant@cleandataengineering.ai", ""]
    (ROOT / "llms.txt").write_text("\n".join(out))


def audit(rels):
    errors, warns = [], []
    files = {str(r) for r in pages()}
    for rel in rels:
        s = (ROOT / rel).read_text(errors="ignore")
        t = re.search(r"<title>(.*?)</title>", s, re.S)
        if not t:
            errors.append((rel, "no <title>"))
        elif len(t.group(1)) > 75:
            warns.append((rel, f"title {len(t.group(1))} chars"))
        if 'name="description"' not in s:
            (errors if str(rel).startswith(("paths/", "index.html")) else warns).append((rel, "no meta description"))
        if 'rel="canonical"' not in s:
            warns.append((rel, "no canonical"))
        h1 = len(re.findall(r"<h1[\s>]", s))
        if h1 != 1:
            warns.append((rel, f"{h1} <h1>"))
        if "<html lang=" not in s:
            warns.append((rel, "no lang"))
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
            try:
                json.loads(m.group(1))
            except Exception as e:  # noqa: BLE001
                errors.append((rel, f"bad JSON-LD: {e}"))
        for href in re.findall(r'href="(/[^"#?]*)', s):
            if href.startswith("//"):
                continue
            target = href.lstrip("/")
            cands = [target, target + "index.html", target + "/index.html"] if not target.endswith(".html") else [target]
            if target == "":
                continue
            if not any(c in files or (ROOT / c).exists() for c in cands):
                errors.append((rel, f"broken link {href}"))
    return errors, warns


def fill_gaps(rels):
    """Pages copied in from other repos (tutorials, certification prep) may lack a description or canonical.
    Add them in place; re-running is a no-op."""
    import html as h
    n = 0
    for rel in rels:
        p = ROOT / rel
        s = p.read_text(errors="ignore")
        if "</head>" not in s:
            continue
        add = []
        if 'rel="canonical"' not in s:
            add.append(f'<link rel="canonical" href="{url_of(rel)}">')
        if 'name="description"' not in s:
            body = s[s.find("<body"):]
            body = re.sub(r"<(script|style|svg|nav|header)\b.*?</\1>", " ", body, flags=re.S)
            text = ""
            for para in re.findall(r"<p\b[^>]*>(.*?)</p>", body, re.S):
                t = re.sub(r"\s+", " ", h.unescape(re.sub(r"<[^>]+>", "", para))).strip()
                if len(t) >= 60:
                    text = t
                    break
            if not text:
                t = re.search(r"<title>(.*?)</title>", s, re.S)
                text = (h.unescape(t.group(1)).strip() + " · Clean Data Engineering") if t else ""
            if text:
                if len(text) > 158:
                    text = text[:155].rsplit(" ", 1)[0] + "…"
                add.append(f'<meta name="description" content="{h.escape(text)}">')
        if add:
            p.write_text(s.replace("</head>", "\n".join(add) + "\n</head>", 1))
            n += 1
    return n


def main():
    rels = list(pages())
    print(f"filled description/canonical on {fill_gaps(rels)} pages")
    n = write_sitemap(rels)
    write_robots()
    write_llms()
    errors, warns = audit(rels)
    print(f"sitemap.xml: {n} urls · robots.txt · llms.txt")
    key = [r for r in rels if str(r) == "index.html" or str(r).startswith("paths/")]
    kerr = [e for e in errors if e[0] in key]
    print(f"audit: {len(rels)} pages, {len(errors)} errors ({len(kerr)} on home + paths), {len(warns)} warnings")
    seen = {}
    for rel, msg in errors:
        seen.setdefault(msg, []).append(str(rel))
    for msg, where in sorted(seen.items(), key=lambda x: -len(x[1]))[:25]:
        print(f"  ERROR {msg}: {len(where)} page(s), e.g. {where[0]}")
    wk = {}
    for rel, msg in warns:
        wk.setdefault(re.sub(r"\d+", "N", msg), []).append(str(rel))
    for msg, where in sorted(wk.items(), key=lambda x: -len(x[1])):
        print(f"  warn  {msg}: {len(where)} page(s), e.g. {where[0]}")
    if "--strict" in sys.argv and errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
