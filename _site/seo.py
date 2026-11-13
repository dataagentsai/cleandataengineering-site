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
SKIP = ("preview", "_", ".", "google")  # google*.html = Search Console verification file, served as is

sys.path.insert(0, str(ROOT / "_paths"))
from data import DISCIPLINES, LEVELS, PLATFORMS  # noqa: E402
from concepts import CARDS, ROLE_GROUPS  # noqa: E402

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
    if s.startswith(("paths/", "concepts/")) or s in (CCA + "index.html", CCA + "CCA-F_Study_Guide.html"):
        return "0.9"
    if s.startswith(CCA) and s.count("/") == 4 and s.endswith("index.html"):
        return "0.7"  # CCA-F section pages: domains, mock exams, traps, mind maps
    if s.count("/") <= 1:
        return "0.8"
    return "0.5"


def write_sitemap(rels):
    items = []
    for rel in rels:
        s = (ROOT / rel).read_text(errors="ignore")
        if re.search(r'<meta name="robots" content="[^"]*noindex', s) or 'http-equiv="refresh"' in s:
            continue  # hidden pages and redirects do not belong in a sitemap
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
           "> Everything is free (no sign-up, no paywall, no ads). A free, open community to learn data engineering, AI engineering, LLM engineering, ML engineering, software engineering "
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
    out += ["", "## Key concepts (the same on every platform)", "",
            f"- [All key concepts, by role and A to Z]({SITE}/concepts/)"]
    for d in DISCIPLINES:
        names = ", ".join(f"[{CARDS[c]['name']}]({SITE}/concepts/{c}/)" for _, ids in ROLE_GROUPS[d["id"]] for c in ids)
        out.append(f"- {d['name']}: {names}")
    out += ["", "## Courses", "",
            f"- [Data platform architecture, drawn right]({SITE}/learn/data-platform-architecture/): control plane and metadata DB, three services, medallion layers, streaming lane, 22 cross-cutting concerns, agents that only propose, products per platform",
            f"- [DataTwin Studio]({SITE}/learn/data-platform-sim/): simulation of one batch through a data platform (metadata, Spark jobs, bronze/silver/gold rows, Delta Lake commits, query plans, logs, dashboard), recorded from a real Spark 3.5 + Delta 3.2 run; replay and naive-pipeline scenarios",
            f"- [Delta Lake internals, recorded]({SITE}/learn/data-platform-sim/delta/): simulation of Parquet files and the _delta_log, copy-on-write UPDATE and DELETE, checkpoints, time travel, RESTORE, concurrent writers (ConcurrentAppendException), deletion vectors, OPTIMIZE with real timings, VACUUM breaking time travel",
            f"- [Spark internals, recorded]({SITE}/learn/data-platform-sim/spark/): simulation of jobs, stages and tasks (waves on 2 cores), lazy evaluation, narrow vs wide and the shuffle, Catalyst plans and pushdown, broadcast vs sort-merge joins, skew and AQE skew-join splitting, caching",
            f"- [Problem Lab]({SITE}/learn/data-platform-sim/problems/): nineteen data engineering problems run for real (duplicates from at-least-once delivery, idempotent re-runs with replaceWhere, SCD Type 2 pitfalls, late-arriving data, failure mid-job, poison records and quarantine, schema drift and contract checks, hard deletes and key reconciliation, backfill after a bug, small files and OPTIMIZE, bad data and contract rules, late dimensions and inferred members, a source outage and freshness SLOs, reconciliation at every hop, time zones and daylight saving, two writers and optimistic concurrency, skew and salting, personal data masking and audit, self-healing with runbooks and gates), each with the naive fix and the right fix and pass/fail checks",
            f"- [Performance stories]({SITE}/learn/data-platform-sim/performance/): twelve Spark and Delta Lake performance problems measured before and after the fix at laptop scale (full reload vs incremental, reading the whole lake, tiny files and OPTIMIZE, skew and AQE, exploding joins on SCD2 dimensions, MERGE rewriting every file, spill, Python UDFs, broadcast joins, collect() on the driver, over-partitioning, an idle cluster bill), plus a combined slow job with a waterfall of fixes",
            f"- [Data quality as metadata]({SITE}/learn/data-platform-sim/data-quality/): metadata-driven, low-code data quality recorded on Spark and Deequ: rules as YAML in a metadata database, one port with Spark SQL and Deequ adapters (same verdicts), quarantine, stop and alert actions, Deequ column profiling and rule suggestions reviewed by a person, a metrics history with an anomaly check, onboarding a dataset with YAML only",
            f"- Components: [metadata store]({SITE}/learn/data-platform-architecture/metadata-store/), [ingestion]({SITE}/learn/data-platform-architecture/ingestion/), [bronze to silver with SCD Type 1 and 2]({SITE}/learn/data-platform-architecture/bronze-to-silver/), [gold]({SITE}/learn/data-platform-architecture/gold/)",
            f"- [Simulators]({SITE}/simulators/): every simulator on the site, for AI agents and data platforms, each labelled recorded or illustrative",
            f"- [Research and open standards]({SITE}/research/): AI Assurance and Harness Catalogs, AgentTwin, DataTwin, the reference agent and the AgentTwin Lab",
            f"- [About]({SITE}/about/): what the site is, the see-run-build-prove loop, what it holds to, who runs it, how to join",
            f"- [AgentTwin, explained]({SITE}/learn/agenttwin/): testing AI agents in a simulated world; AgentTwin vs a digital twin, how a given agent's tests are chosen, a step-through simulator, Assurance Catalog coverage, comparison with LangWatch and others",
            f"- [Claude API Simulator]({SITE}/learn/llm-api-sim/): interactive request and response for the Claude Messages API: change model, system prompt, max_tokens, effort, thinking, temperature, stop sequences, tools and streaming; see Python, TypeScript and cURL code, the JSON response or server-sent events, tokens and cost",
            f"- [The technical anchor]({SITE}/learn/technical-anchor/): how a developer thinks as the technical anchor of a data engineering project: the roles around them, failing fast on architecture, estimates, scope and decisions, stakeholders, risks, test-deploy-run, first 30 days",
            f"- [DataTwin, explained]({SITE}/learn/datatwin/): testing a data platform in a simulated business with planted incidents; DataTwin vs a digital twin and AgentTwin, how a platform's tests are chosen, the dashboard checked against the world's truth, a step-through simulator, comparison with data quality and observability tools, honest build status",
            f"- [Shift left: fail fast on data code]({SITE}/learn/shift-left/): 10 pages: catching problems in PySpark, Python and Databricks SQL before they run; pure functions and how a tool detects them, table-driven unit tests, testing SCD2, idempotency, duplicates, dropped rows and cartesian joins without a cluster, coverage.py and its blind spots, mutation testing, complexity scores, clean-code Ruff rules, SQL injection, secrets, vulnerable libraries, cost checks on code, SQL, empty-table plans and job config, a gap report, why not SonarQube",
            f"- [Streaming options at a glance]({SITE}/learn/streaming/options/): one table of 23 AWS fast-lane and platform-lane options (AWS-native Flink + DynamoDB, ClickHouse, Lakebase, Databricks real-time mode, Lakehouse//RT, chained 15-min runs, 5-min, continuous, AWS-only Iceberg, Power BI push and DirectQuery, file triggers) with delay, push or pull, Unity Catalog, cost, verdict and links",
            f"- [Streaming simulator]({SITE}/learn/streaming/sim/): illustrative animation of IoT readings, app events, CDC and lab files flowing through a fast lane and the medallion to a live screen and Power BI, per binding (AWS + Databricks, AWS only, Databricks only) and route (direct, medallion, both), with incidents; plus [three lanes together]({SITE}/learn/streaming/sim/lanes/): fast, near real time and batch over a simulated day and where they meet; plus [a faster platform lane]({SITE}/learn/streaming/sim/faster/): today, chained steps, 5-minute runs and continuous compared on screen data age and cost",
            f"- [Databricks real time: real-time mode and Lakehouse//RT]({SITE}/learn/streaming/real-time-mode/): real-time mode GA in jobs and Lakeflow pipelines, the new Lakehouse//RT engine (beta) and where it fits, GA status, sources and sinks (Kafka, Kinesis; no Delta sink), limits, rough cost against Flink + DynamoDB, a live store inside Unity Catalog (DynamoDB vs Lakebase), verdict",
            f"- [Iceberg time travel as SCD Type 2: is it a good pattern?]({SITE}/learn/time-travel-vs-scd2/): no; two clocks (business vs commit time), when it works, nine cases where it fails, what reprocessing, backfills, reloads, compaction, rollback, expiry and migration do to snapshots, why it is not clean design, the pattern (changelog feeds an SCD2 MERGE, as-of join, Iceberg tags for month-end copies)",
            f"- [SCD Type 2 on Databricks: AUTO CDC or our own PySpark?]({SITE}/learn/scd2-auto-cdc-vs-pyspark/): CDC vs full-snapshot input; Lakeflow AUTO CDC (SQL, Python, change data feed, FROM SNAPSHOT) vs one hand-written PySpark SCD2 writer with adapters per input; 11 table-driven tests and an end-to-end run on Spark + Delta; what AUTO CDC handles that own code must earn; DBU rates, cost drivers and a calculator",
            f"- [AWS services for data platforms and streaming]({SITE}/learn/aws-data-services/): master catalog of 66 AWS services (ingestion and CDC, streaming, storage, catalog, processing, orchestration, query and warehouse, operational stores, BI, ML and AI, security and network, observability and cost, IaC) placed on one data platform picture, each with a verdict for AWS + Databricks, Azure, Google Cloud and Databricks equivalents, and a 10-minute page per service: plain words, where it fits, production problems, alternatives, cost, security, what to watch, limits, decisions, FAQ, sources",
            f"- [Gold data modelling: grain, keys, facts and dimensions done right]({SITE}/learn/gold-data-modelling/): dimensional (Kimball) modelling for the gold layer: where Kimball helps, business ontology, grain, business vs primary vs surrogate keys, joining on surrogate or business key, SCD Type 2 joins, dimension and SCD types, fact kinds (transaction, periodic and accumulating snapshot, factless, aggregate, consolidated), what goes in a fact, 'Type 1 or Type 2 facts', requirement patterns and designs, bus matrix, metric views, materialized views, when to materialize and pre-aggregate and at what grain, Power BI and dashboard performance at volume, fan-out and chasm traps, schema layout, liquid clustering keys, a tyre example",
            f"- [Silver to gold: the harness that builds facts and dimensions]({SITE}/learn/silver-to-gold/): one metadata-driven harness for every fact kind: SQL vs PySpark builds, troubleshooting with intermediate results, the row ledger for record drops, many-to-many detection, incremental loading and watermarks, windows and lookback, completeness and restatements, late facts and dimensions, history load, reloads, hiding a bad batch, pure functions tested locally on a synthetic world, regression testing, reliability and cost practices, what is built",
            f"- [Declarative or not: Spark Declarative Pipelines, open source and on Databricks]({SITE}/learn/spark-declarative-pipelines/): imperative vs declarative pipelines; Apache Spark Declarative Pipelines (Spark 4.1+: streaming tables, materialized views, graph, dry-run, checkpoints) vs Databricks Lakeflow (AUTO CDC incl. snapshots, expectations, event log, continuous mode, incremental refresh, serverless); the AUTO CDC open-source question; DBU cost of jobs vs pipeline editions, classic vs serverless; where declarative helps and where not; bronze to silver, silver to gold; combining with a harness",
            f"- [Gold harness spec: facts and SCD2 dimensions from silver]({SITE}/learn/gold-harness-spec/): an open specification (requirements, design, low-level design, no code) for one metadata-driven harness that builds gold facts and SCD Type 1/2 dimensions from silver as robustly as AUTO CDC: change-feed watermarks, table update triggers, full vs incremental rules, durable and version surrogate keys, current vs as-of fact lookups, fact change modes, late-arriving dimensions (inferred members) and facts (re-key queue), fact-from-fact rules, pure functions, SCD2 tests, record-drop checks",
            f"- [Delta Lake vs Apache Iceberg on Databricks]({SITE}/learn/delta-vs-iceberg/): what a table format is, the two side by side, a Databricks feature matrix for managed Delta, Delta with Iceberg reads (UniForm), managed Iceberg and foreign Iceberg (change data feed, streaming, Lakeflow pipelines, lineage, liquid clustering, predictive optimization, masks, keys), data vs row lineage, which to pick on AWS",
            f"- [Power BI vs Databricks AI/BI, or both, on a lakehouse]({SITE}/learn/power-bi-vs-databricks-ai-bi/): 3 pages: where the semantic model and row-level security should live (Databricks, Power BI or both), how RLS works on both sides from one entitlements table, volume per storage mode, cost comparison, recommended architecture; Power BI and Fabric internals (VertiPaq, capacity, Direct Lake on Databricks data), troubleshooting, benchmarking, testing, limits, production problems; the same for Databricks AI/BI dashboards and Genie",
            f"- [Iceberg lakehouse on AWS with Databricks: who owns the catalog?]({SITE}/learn/iceberg-lakehouse-aws-databricks/): conceptual data platform with all 24 concerns; Architecture B (AWS owns: S3 Tables, Glue Data Catalog, Lake Formation, SageMaker lakehouse; Databricks as guest) vs Architecture A (Unity Catalog owns managed Iceberg; Athena, Redshift, QuickSight read through Glue federation); whether Databricks can write bronze to silver to gold in B; who can write where; maintenance, ETL, streaming, semantic, serving, cost, governance, lineage compared; United Airlines and Razor Group case studies; winner and restrictions",
            f"- [Where data engineering time goes]({SITE}/learn/where-data-engineering-time-goes/): field estimate of hours in a first source build vs a year of running (understanding source meaning ~28%, code ~12%, ~60% non-technical), why misread source meaning is the root of rework and firefighting, public surveys compared, the non-technical work and how to cut it (earlier, once, by the right person) with verdicts",
            f"- [Critical thinking in data projects]({SITE}/how-we-work/critical-thinking/): five questions for any claim, number or design in a data project; traps (averages, survivorship, correlation, Simpson's paradox, vendor benchmarks); worked examples; habits for reviews",
            f"- [Top project management mistakes in data projects]({SITE}/how-we-work/project-management-mistakes/): why data projects break normal project management (discovery, source dependencies, trusted numbers as done), the most common mistakes grouped by planning, scope, people, delivery and running, what to do instead with verdicts, a healthier plan shape, weekly warning signs",
            f"- [Estimation mistakes in data projects]({SITE}/how-we-work/estimation/): twelve estimation mistakes (estimating code not understanding, unknown sources, happy path, reconciliation, access waits, environments, backfills, single-point numbers) and how to avoid each, estimate by source complexity, ranges, a worked estimate",
            f"- [Who maintains your tables]({SITE}/learn/table-maintenance/): Unity Catalog managed vs external tables vs AWS-managed Iceberg (Glue, S3 Tables); who runs compaction, VACUUM and snapshot expiry; storage-compute split vs Snowflake; how Delta and Iceberg commit and clean up",
            f"- [Metric views, taught from zero]({SITE}/learn/metric-views/): 10 pages: what a semantic model is with no product in it (ten parts), Unity Catalog metric views vs the dbt Semantic Layer (MetricFlow) vs the Power BI semantic model, limits from eight seats with verdicts, every part of a metric view (joins, one_to_many, window and composed measures, parameters, agent metadata, relationships), grain and fan-out, additive kinds, row-level security with row filters and an entitlements table, materialization and pre-aggregation, production anti-patterns and table-driven tests, one tyre-sales example end to end with dbt and DAX equivalents",
            f"- [Streaming architecture on AWS and Databricks]({SITE}/learn/streaming/): IoT and non-IoT streams, seconds vs minutes in two lanes, Kappa through bronze, stream joins, SCD in silver, direct-to-UI vs ClickHouse vs gold, DLT vs Structured Streaming, Auto Loader and file arrival triggers, S3, replays, error handling, end-to-end SLA report, binding options with verdicts, rough cost",
            f"- [Real-time analytics, drawn simply]({SITE}/learn/real-time-analytics/): 11 pages: real time vs streaming vs near real time, Lambda vs Kappa, components from CDC and Kafka to push, change capture tools by source database (Debezium, Qlik Replicate, GoldenGate and more), when Kafka is needed vs straight to ClickHouse or Power BI, eight abstract designs, products per cloud, contracts and AsyncAPI bindings, SSE vs WebSocket, rough cost, established technologies",
            f"- [Test architecture for a data platform]({SITE}/learn/data-platform-architecture/testing/): nine kinds of test: static analysis with a purity check, unit tests on pure functions, coverage and mutation, contract tests, one integration test per layer hop, synthetic end to end, DataTwin simulation, end to end on real data with zero-copy clones, parallel run against production; one release report",
            f"- [The ETL, end to end, on AWS + Databricks]({SITE}/learn/data-platform-architecture/aws-databricks/etl/): how the core runs: ten working parts (movers, run controller, lander, silver and gold builders, run recorder, ops builder, heartbeat), one MES load step by step from database to gold, generated Lakeflow jobs and triggers, ids and the run-log hierarchy, streaming windows, failures, re-runs, replays, backfills and the observability parts",
            f"- [Data platform on AWS + Databricks]({SITE}/learn/data-platform-architecture/aws-databricks/): one big picture of a data platform on Databricks in your own AWS account: sources, metadata-driven common ingestion, medallion on S3 with Unity Catalog, semantic model with metric views, AI/BI dashboards, Genie and a conversation UI; shared assets; the right medallion and AI/BI designs; 22 concerns bound to Databricks and AWS with the gaps we fill",
            f"- [Agent Harness on AWS]({SITE}/learn/agent-harness-aws/): the agent harness big picture with an AWS service in every box (Bedrock, Bedrock Guardrails, ECS Fargate, Aurora PostgreSQL, Cognito, CloudWatch, AppConfig), all 22 concerns bound to AWS, open source and our own code, Azure-to-AWS swap table, open decisions",
            f"- [Spec-driven development for data platforms]({SITE}/leaders/spec-driven/data-platform/): for leaders: a small centre of excellence writes the data specs once (catalogs, manifest, binding), builds shared assets once, and every data product is built, tested, released and run from them",
            f"- [Medallion architecture, drawn right]({SITE}/learn/medallion-architecture/): bronze, silver and gold layers, one order through every layer, nine rules, common mistakes, products on each platform",
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
        dm = re.search(r'name="description" content="([^"]*)"', s)
        if dm and len(dm.group(1)) > 160:
            warns.append((rel, f"description {len(dm.group(1))} chars"))
        if 'name="description"' not in s:
            (errors if str(rel).startswith(("paths/", "index.html")) else warns).append((rel, "no meta description"))
        if 'rel="canonical"' not in s:
            warns.append((rel, "no canonical"))
        h1 = len(re.findall(r"<h1[\s>]", s))
        if h1 != 1:
            warns.append((rel, f"{h1} <h1>"))
        if "<html lang=" not in s:
            warns.append((rel, "no lang"))
        for m in re.finditer(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', s, re.S):
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


CCA = "certifications/claude-certified-architect/CCA-F/"

# Titles and descriptions for the pages we most want found. They use the words people type into a
# search box ("AI agent", "free", "simulator"), not only our own names. Applied after every build.
TITLES = {
    "learn/index.html": "Free data and AI engineering courses · Clean Data Engineering",
    "learn/agent-harness-sim/index.html": "AI Agent Harness Simulator: watch an AI agent work, step by step",
    "learn/agent-harness/index.html": "Agent Harness Tutorial: how an AI agent works, drawn simply",
    "learn/eval-harness/index.html": "Eval Harness Tutorial: check what an AI agent did from its traces",
    "learn/data-platform-sim/index.html": "Data Platform Simulator: one batch through Spark and Delta Lake",
    "simulators/index.html": "Free AI agent and data platform simulators · Clean Data Engineering",
    "research/index.html": "Open specifications for AI agents and data platforms",
    "writing/index.html": "Blog: data, AI and LLM engineering, explained simply",
    "projects/index.html": "Open-source data and AI community projects · Clean Data Engineering",
    "certifications/index.html": "Free Claude Certified Architect and Azure AI-103 exam prep",
    "problems/index.html": "79 hard, unsolved problems in data and AI engineering",
    # Courses and simulators: the phrase a learner types first ("medallion architecture explained",
    # "lambda vs kappa", "spark performance tuning"), our own name after it or not at all.
    "index.html": "Free Data and AI Engineering Courses · Clean Data Engineering",
    "paths/index.html": "Data and AI Engineering Roadmaps: Free Learning Paths",
    "concepts/index.html": "Data and AI Engineering Concepts, Explained Simply",
    "learn/medallion-architecture/index.html": "Medallion Architecture Explained: Bronze, Silver and Gold",
    "learn/data-platform-architecture/index.html": "Data Platform Architecture Explained, with Diagrams",
    "learn/data-platform-architecture/aws-databricks/index.html": "Databricks on AWS: Data Platform Reference Architecture",
    "learn/data-platform-architecture/aws-databricks/etl/index.html": "Metadata-Driven ETL on Databricks and AWS, End to End",
    "learn/data-platform-architecture/bronze-to-silver/index.html": "Bronze to Silver: Deduplication and SCD Type 1 and 2",
    "learn/data-platform-architecture/gold/index.html": "Gold Layer Design: Facts, Dimensions and Business Tables",
    "learn/data-platform-architecture/ingestion/index.html": "Data Ingestion Architecture: Sources to Bronze",
    "learn/data-platform-architecture/metadata-store/index.html": "Metadata-Driven Data Pipelines: the Metadata Store",
    "learn/data-platform-architecture/testing/index.html": "Data Platform Testing Strategy: Nine Kinds of Data Test",
    "learn/data-platform-sim/delta/index.html": "Delta Lake Internals: Transaction Log, Time Travel, VACUUM",
    "learn/data-platform-sim/spark/index.html": "Spark Internals Explained: Jobs, Stages, Tasks, Shuffle",
    "learn/data-platform-sim/performance/index.html": "Spark Performance Tuning: 12 Problems Measured and Fixed",
    "learn/data-platform-sim/problems/index.html": "Data Engineering Problems Solved: SCD2, Late Data, Duplicates",
    "learn/data-platform-sim/data-quality/index.html": "Data Quality with Deequ and Spark SQL, Metadata-Driven",
    "learn/streaming/options/index.html": "Streaming Architecture Options Compared: One Table with Verdicts",
    "learn/streaming/sim/index.html": "Streaming Simulator: IoT to Power BI via Fast Lane and Medallion",
    "learn/streaming/sim/faster/index.html": "Faster Databricks to Power BI: Four Designs Compared",
    "learn/streaming/sim/lanes/index.html": "Fast, Near Real-Time and Batch Lanes Together: Simulator",
    "learn/streaming/real-time-mode/index.html": "Databricks Real-Time Mode and Lakehouse//RT, Explained",
    "learn/delta-vs-iceberg/index.html": "Delta Lake vs Iceberg on Databricks: CDF, Lineage, UniForm",
    "learn/iceberg-lakehouse-aws-databricks/index.html": "Iceberg Lakehouse on AWS + Databricks: Who Owns the Catalog?",
    "learn/where-data-engineering-time-goes/index.html": "Where Data Engineering Time Really Goes (and How to Win It Back)",
    "how-we-work/critical-thinking/index.html": "Critical Thinking in Data Projects: Five Questions",
    "how-we-work/project-management-mistakes/index.html": "Top Project Management Mistakes in Data Projects",
    "how-we-work/estimation/index.html": "Estimation Mistakes in Data Projects, and How to Avoid Them",
    "learn/table-maintenance/index.html": "Who Maintains Your Tables? Managed, External, AWS Iceberg",
    "learn/metric-views/index.html": "Databricks Metric Views, Taught from Zero",
    "learn/scd2-auto-cdc-vs-pyspark/index.html": "SCD Type 2 on Databricks: AUTO CDC vs Own PySpark MERGE",
    "learn/aws-data-services/index.html": "AWS Services for Data Platforms and Streaming: 66 Explained",
    "learn/gold-harness-spec/index.html": "Gold Harness Spec: Facts and SCD2 Dimensions from Silver",
    "learn/gold-data-modelling/index.html": "Gold Data Modelling: Grain, Keys, Facts and Dimensions",
    "learn/silver-to-gold/index.html": "Silver to Gold: The Harness That Builds Facts and Dimensions",
    "learn/spark-declarative-pipelines/index.html": "Spark Declarative Pipelines: Open Source vs Databricks Lakeflow",
    "learn/streaming/index.html": "Streaming Architecture on AWS and Databricks, IoT to Gold",
    "learn/real-time-analytics/index.html": "Real-Time Analytics Architecture, Explained Simply",
    "learn/real-time-analytics/basics/index.html": "Real-Time vs Streaming vs Near Real-Time Analytics",
    "learn/real-time-analytics/lambda-vs-kappa/index.html": "Lambda vs Kappa Architecture, Explained Simply",
    "learn/real-time-analytics/change-capture/index.html": "Change Data Capture (CDC) Tools Compared: Debezium and More",
    "learn/real-time-analytics/cost/index.html": "Real-Time Analytics Cost: What Streaming Really Costs",
    "learn/real-time-analytics/push-to-ui/index.html": "Real-Time Dashboards: SSE vs WebSocket, Snapshot then Deltas",
    "learn/shift-left/index.html": "Shift-Left Testing for PySpark and Databricks SQL",
    "learn/shift-left/data-tests/index.html": "Unit Testing SCD2 and Idempotency in PySpark Without a Cluster",
    "learn/shift-left/tests-and-coverage/index.html": "PySpark Unit Testing, Code Coverage and Complexity",
    "learn/shift-left/pure-functions/index.html": "Pure Functions in PySpark: Testable Transformations",
    "learn/shift-left/security-and-cost/index.html": "PySpark Security Checks: Secrets, SQL Injection, Cost",
    "learn/technical-anchor/index.html": "Data Engineering Tech Lead Guide: Thinking for the Whole Project",
    "learn/technical-anchor/project-review/index.html": "Data Project Review Checklist: What Is Your Project Missing?",
    "learn/llm-api-sim/index.html": "Claude API Simulator: Try the Messages API, Free",
    "learn/agent-harness-aws/index.html": "AI Agent Architecture on AWS: Bedrock Agent Harness",
    "learn/agent-harness/series/index.html": "AI Agent Architecture on Azure: the Agent Harness Series",
    "learn/agent-guardrails/index.html": "AI Agent Guardrails: a Catalog of Guardrail Checks",
    "learn/ai-universe/index.html": "The AI Stack Explained: Models, Data, Agents and Compute",
    "learn/agenttwin/index.html": "AgentTwin: Testing AI Agents in a Simulated World",
    "learn/datatwin/index.html": "DataTwin: Testing a Data Platform in a Simulated Business",
    "ai-engineering/vertical-agents/index.html": "AI Agents by Industry: Banking, Healthcare, Retail and More",
    "assets/index.html": "Open-Source AI Agent and Data Engineering Tools",
    "mindset/index.html": "Worried About AI Taking Your Job? Start Here",
    # Claude Certified Architect: people search "claude certified architect foundations exam", "CCA-F
    # practice questions", "CCA-F mock exam", "CCA-F study guide", "CCAR-F". Lead with those words.
    f"{CCA}index.html": "Claude Certified Architect Foundations (CCA-F) Exam Prep, Free",
    f"{CCA}CCA-F_Study_Guide.html": "CCA-F Study Guide: Claude Certified Architect Foundations",
    f"{CCA}Foundations-Mock-Exam/index.html": "CCA-F Mock Exam 1: 77 Claude Certified Architect Questions",
    f"{CCA}Foundations-Mock-Exam-2/index.html": "CCA-F Mock Exam 2: Timed, 60 Questions in 120 Minutes",
    f"{CCA}Foundations-Mock-Exam-3/index.html": "CCA-F Mock Exam 3: Claude Certified Architect Scenarios",
    f"{CCA}Foundations-Mock-Exam-4/index.html": "CCA-F Mock Exam 4: Real-Exam-Style Practice Questions",
    f"{CCA}Foundations-Mock-Exam-5/index.html": "CCA-F Mock Exam 5: Real-Exam-Style Practice Questions",
    f"{CCA}Foundations-Mock-Exam-6/index.html": "CCA-F Mock Exam 6: Real-Exam-Style Practice Questions",
    f"{CCA}Foundations-Mock-Exam-7/index.html": "CCA-F Mock Exam 7: Exam-Level Practice Questions",
    f"{CCA}Trap-Gym/index.html": "CCA-F Exam Traps: the 30 Traps in Claude Certified Architect",
    f"{CCA}Mind-Maps/index.html": "CCA-F Mind Maps: the Five Exam Domains on One Page",
}
DESCRIPTIONS = {
    f"{CCA}index.html": "Free prep for the Claude Certified Architect – Foundations exam (CCA-F, also CCAR-F): study guide, "
                        "all five domains, practice questions, mock exams, mind maps and 30 exam traps.",
    f"{CCA}CCA-F_Study_Guide.html": "Free study guide for the Claude Certified Architect – Foundations (CCA-F) exam: format, "
                                    "the five domains and their weights, key concepts and how the questions are written.",
    f"{CCA}Foundations-Mock-Exam/index.html": "Free CCA-F mock exam: 77 Claude Certified Architect – Foundations practice "
                                              "questions with answers and explanations.",
    f"{CCA}Foundations-Mock-Exam-2/index.html": "Free timed CCA-F mock exam: 60 Claude Certified Architect – Foundations "
                                                "questions in 120 minutes, like the real exam, with explanations.",
    "learn/agent-harness-sim/index.html": "Free AI agent harness simulator. Send a message to a claims assistant and watch every step: "
                                          "tools, guardrail checks, code, the JSON to and from the model, and the trace.",
    "learn/agent-harness/index.html": "Free, hand-drawn tutorial on the agent harness: the code around an AI model that makes an agent "
                                      "safe and reliable. One real agent end to end, with real code.",
}
# Learning paths: people search "<role> roadmap", so every path page says it.
for _d in DISCIPLINES:
    TITLES.setdefault(f"paths/{_d['id']}/index.html", f"{_d['name']} Roadmap: Free Learning Path")
    for _p in _d["platforms"]:
        TITLES.setdefault(f"paths/{_d['id']}/{_p}/index.html", f"{_d['name']} on {PLATFORMS[_p]}: Free Roadmap")

OG_IMAGE = f"{SITE}/assets/og-card.png"
PERSON = {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/about/"}
ORG = {"@type": "Organization", "name": "Clean Data Engineering", "url": f"{SITE}/",
       "logo": {"@type": "ImageObject", "url": OG_IMAGE}}
COURSES = ("learn/agent-harness/", "learn/eval-harness/", CCA)
SIMS = ("learn/agent-harness-sim/", "learn/llm-api-sim/", "learn/data-platform-sim/")
SUFFIX = " · Clean Data Engineering"


def _attr(s):
    import html as h
    return h.escape(s, quote=True)


def _head(s):
    i = s.find("</head>")
    return (s[:i], s[i:]) if i >= 0 else (None, None)


def apply_titles(rels):
    """Swap in the search-friendly title and description on the pages in TITLES / DESCRIPTIONS."""
    n = 0
    for rel in rels:
        key = str(rel)
        if key not in TITLES and key not in DESCRIPTIONS:
            continue
        p = ROOT / rel
        s = p.read_text(errors="ignore")
        head, rest = _head(s)
        if head is None:
            continue
        new = head
        if key in TITLES:
            t = TITLES[key]
            new = re.sub(r"<title>.*?</title>", lambda m: f"<title>{_attr(t)}</title>", new, count=1, flags=re.S)
            new = re.sub(r'<meta property="og:title" content="[^"]*">', lambda m: f'<meta property="og:title" content="{_attr(t)}">', new)
        if key in DESCRIPTIONS:
            d = DESCRIPTIONS[key]
            new = re.sub(r'<meta name="description" content="[^"]*">', lambda m: f'<meta name="description" content="{_attr(d)}">', new, count=1)
            new = re.sub(r'<meta property="og:description" content="[^"]*">', lambda m: f'<meta property="og:description" content="{_attr(d)}">', new)
        if new != head:
            p.write_text(new + rest)
            n += 1
    return n


def _meta(head, rx):
    m = re.search(rx, head, re.S)
    return m.group(1).strip() if m else ""


def add_social(rels):
    """Open Graph and Twitter card tags so a shared link shows a title, summary and picture."""
    n = 0
    for rel in rels:
        p = ROOT / rel
        s = p.read_text(errors="ignore")
        head, rest = _head(s)
        if head is None or 'http-equiv="refresh"' in head:
            continue
        title = _meta(head, r'property="og:title" content="([^"]*)"') or _meta(head, r"<title>(.*?)</title>")
        desc = _meta(head, r'name="description" content="([^"]*)"')
        want = {
            'property="og:title"': f'<meta property="og:title" content="{title}">' if title else "",
            'property="og:description"': f'<meta property="og:description" content="{desc}">' if desc else "",
            'property="og:url"': f'<meta property="og:url" content="{url_of(rel)}">',
            'property="og:type"': f'<meta property="og:type" content="{"article" if str(rel).startswith("writing/") and str(rel).count("/") == 2 else "website"}">',
            'property="og:site_name"': '<meta property="og:site_name" content="Clean Data Engineering">',
            'property="og:image"': f'<meta property="og:image" content="{OG_IMAGE}">',
            'name="twitter:card"': '<meta name="twitter:card" content="summary_large_image">',
        }
        add = [tag for marker, tag in want.items() if tag and marker not in head]
        if add:
            p.write_text(head + "\n".join(add) + "\n" + rest)
            n += 1
    return n


def _post_date(slug):
    f = ROOT / "_writing" / "posts" / f"{slug}.md"
    if f.exists():
        m = re.search(r"^date:\s*(\d{4}-\d{2}-\d{2})", f.read_text(errors="ignore"), re.M)
        if m:
            return m.group(1)
    return None


def _clean_title(t):
    import html as h
    t = h.unescape(t)
    return t[: -len(SUFFIX)] if t.endswith(SUFFIX) else t


def add_jsonld(rels):
    """Give every page that has no structured data one block: what the page is (article, course, simulator,
    collection) plus a breadcrumb trail. Search engines and AI assistants read this to know what they are
    looking at. Pages whose builders already write JSON-LD are left alone. Re-running replaces our block."""
    import html as h
    auto = re.compile(r'\n?<script type="application/ld\+json" data-seo="auto">.*?</script>', re.S)
    titles = {}
    for rel in rels:
        s = (ROOT / rel).read_text(errors="ignore")
        titles[url_of(rel)] = _clean_title(_meta(s[: s.find("</head>")], r"<title>(.*?)</title>"))
    n = 0
    for rel in rels:
        p = ROOT / rel
        s = auto.sub("", p.read_text(errors="ignore"))
        head, rest = _head(s)
        if head is None or 'http-equiv="refresh"' in head or "application/ld+json" in s:
            continue
        key, url = str(rel), url_of(rel)
        name = titles[url]
        desc = h.unescape(_meta(head, r'name="description" content="([^"]*)"'))
        mod = lastmod(rel)
        base = {"name": name, "url": url, "description": desc, "inLanguage": "en", "isAccessibleForFree": True}
        course = next((c for c in COURSES if key.startswith(c)), None)
        if key.startswith("writing/") and key.count("/") == 2:
            main = {"@type": "BlogPosting", "headline": name[:110], **base, "datePublished": _post_date(rel.parts[1]) or mod,
                    "dateModified": mod, "author": PERSON, "publisher": ORG, "image": OG_IMAGE, "mainEntityOfPage": url}
        elif course and key == course + "index.html":
            main = {"@type": "Course", **base, "provider": ORG, "author": PERSON,
                    "offers": {"@type": "Offer", "price": 0, "priceCurrency": "USD", "category": "Free"},
                    "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "Online", "courseWorkload": "PT5H"}}
        elif course:
            main = {"@type": "LearningResource", **base, "isPartOf": {"@type": "Course", "url": f"{SITE}/{course}",
                    "name": titles.get(f"{SITE}/{course}", "")}, "author": PERSON, "publisher": ORG, "dateModified": mod}
        elif key.startswith(SIMS):
            main = {"@type": "LearningResource", **base, "learningResourceType": "Interactive simulation",
                    "author": PERSON, "publisher": ORG, "dateModified": mod}
        elif key.startswith(("learn/", "certifications/", "concepts/", "paths/", "problems/")) and key.count("/") >= 2:
            main = {"@type": "LearningResource", **base, "author": PERSON, "publisher": ORG, "dateModified": mod}
        elif key.count("/") == 1:
            main = {"@type": "CollectionPage", **base, "publisher": ORG}
        else:
            main = {"@type": "WebPage", **base, "publisher": ORG, "dateModified": mod}
        crumbs, path = [{"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"}], ""
        parts = [x for x in key.replace("index.html", "").split("/") if x]
        for part in parts:
            path += part if part.endswith(".html") else part + "/"
            u = f"{SITE}/{path}"
            crumbs.append({"@type": "ListItem", "position": len(crumbs) + 1,
                           "name": titles.get(u) or part.replace("-", " ").replace(".html", "").capitalize(), "item": u})
        graph = [{"@context": "https://schema.org", **main}]
        if len(crumbs) > 1:
            graph.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": crumbs})
        block = json.dumps(graph, ensure_ascii=False).replace("</", "<\\/")
        p.write_text(head + f'<script type="application/ld+json" data-seo="auto">{block}</script>\n' + rest)
        n += 1
    return n


# GoatCounter (chosen 1 Nov 2026): no cookies, no consent banner. Dashboard at
# https://cleandataengineering.goatcounter.com. Added here because this script runs last on every publish.
ANALYTICS = ('<script data-goatcounter="https://cleandataengineering.goatcounter.com/count" '
             'async src="//gc.zgo.at/count.js"></script>')


def add_analytics(rels):
    n = 0
    for rel in rels:
        p = ROOT / rel
        s = p.read_text()
        if "gc.zgo.at/count.js" in s or "</head>" not in s or 'http-equiv="refresh"' in s:
            continue
        p.write_text(s.replace("</head>", ANALYTICS + "\n</head>", 1))
        n += 1
    return n


def main():
    rels = list(pages())
    print(f"analytics added to {add_analytics(rels)} pages")
    print(f"filled description/canonical on {fill_gaps(rels)} pages")
    print(f"search titles/descriptions on {apply_titles(rels)} pages")
    print(f"social card tags on {add_social(rels)} pages")
    print(f"structured data (JSON-LD) on {add_jsonld(rels)} pages")
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
