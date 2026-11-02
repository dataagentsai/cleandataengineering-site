"""Test architecture for a data platform: /learn/data-platform-architecture/testing/.

    python3 _guides/test_architecture.py

Cloud-neutral test strategy (agreed in discussion, 2 Nov 2026): logic in pure functions,
nine kinds of test from static analysis to a parallel run against production, one integration
test per layer hop, DataTwin for simulated bad days and pre-production runs on real data,
evidence collected into one release report. Reuses the shell and helpers of dp_aws_databricks.py.
"""
import json
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
import dp_aws_databricks as D  # noqa: E402  (shell, CSS, drawing and table helpers, gates())

C, wb = D.C, D.wb
rect, tx, arr, svg, table = D.rect, D.tx, D.arr, D.svg, D.table
SITE = wb.SITE
URL = f"{SITE}/learn/data-platform-architecture/testing/"
BASE = "/learn/data-platform-architecture/"


# ------------------------------------------------------------------ drawings
def pyramid():
    """Nine kinds of test: wide and cheap at the bottom, narrow and real at the top."""
    rows = [  # label, note, fill
        ("9 · Parallel run vs production", "real data, old vs new", "#F8E6EF"),
        ("8 · End to end on real data", "pre-production, clones", "#F8E6EF"),
        ("7 · DataTwin", "simulated bad days", "#FFF4D9"),
        ("6 · End to end, synthetic", "known answers", "#FFF4D9"),
        ("5 · Integration, one hop at a time", "four hops", "#E6F4EC"),
        ("4 · Contract tests", "promises between teams", "#E9EDF8"),
        ("3 · Coverage and mutation", "do the tests bite?", "#E9EDF8"),
        ("2 · Unit tests on pure functions", "most of the logic", "#E9EDF8"),
        ("1 · Static analysis (shift left)", "read the code, run nothing", "#F4F4F2"),
    ]
    b, cx, top, h = [], 430, 20, 46
    for i, (lbl, note, f) in enumerate(rows):
        w = 300 + i * 62
        y = top + i * (h + 6)
        b.append(rect(cx - w / 2, y, w, h, f, r=10) + tx(cx, y + 21, lbl, 14.5, "middle") + tx(cx, y + 38, note, 11.5, "middle", fill="#555"))
    y0, y1 = top + 4, top + 9 * (h + 6) - 10
    b.append(arr(880, y1, 880, y0) + tx(900, y0 + 14, "more real", 13) + tx(900, y0 + 32, "slower, costlier", 12, fill="#555"))
    b.append(tx(900, y1 - 18, "cheaper, faster", 13) + tx(900, y1, "run on every change", 12, fill="#555"))
    return svg(1040, top + 9 * (h + 6) + 10, "".join(b),
               "A pyramid of nine kinds of test: static analysis and unit tests wide at the bottom, integration and end-to-end in the middle, real-data runs and a parallel run against production narrow at the top.")


def core_shell():
    """Logic in the middle, input and output at the edges."""
    b = []
    b.append(rect(20, 30, 230, 150, "#F4F4F2") + tx(135, 62, "Read (impure)", 16, "middle")
             + tx(135, 90, "tables, files, APIs,", 12.5, "middle") + tx(135, 108, "metadata, the clock", 12.5, "middle")
             + tx(135, 150, "thin · tested by integration", 12, "middle", fill="#555"))
    b.append(rect(300, 14, 440, 182, "#E6F4EC") + tx(520, 48, "Pure core: all the business logic", 17, "middle"))
    for i, s in enumerate(["dedupe and latest-wins", "SCD2 versions and dates", "inferred members", "OEE and scrap formulas", "changed-window recompute"]):
        b.append(tx(330 + (i % 2) * 215, 82 + (i // 2) * 26, "· " + s, 13))
    b.append(tx(520, 178, "DataFrame in, DataFrame out · tested by unit tests, in seconds", 12, "middle", fill="#555"))
    b.append(rect(790, 30, 230, 150, "#F4F4F2") + tx(905, 62, "Write (impure)", 16, "middle")
             + tx(905, 90, "MERGE, run_log,", 12.5, "middle") + tx(905, 108, "watermark, alerts", 12.5, "middle")
             + tx(905, 150, "thin · tested by integration", 12, "middle", fill="#555"))
    b.append(arr(250, 105, 300, 105) + arr(740, 105, 790, 105))
    return svg(1040, 210, "".join(b), "Read on the left and write on the right are thin and impure; all business logic sits in a pure core in the middle, tested by fast unit tests.")


def hops():
    """One integration test per hop."""
    layers = [("Source", "#F4F4F2"), ("Bronze", "#F3E3D3"), ("Silver", "#ECEDEF"), ("Gold", "#FFF4D9"), ("Semantic", "#F8EBF1")]
    b = []
    for i, (n, f) in enumerate(layers):
        x = 20 + i * 210
        b.append(rect(x, 30, 150, 60, f) + tx(x + 75, 66, n, 17, "middle"))
        if i < 4:
            b.append(arr(x + 150, 60, x + 210, 60))
            b.append(rect(x + 110, 112, 130, 52, "#fff", dash=True, r=10) + tx(x + 175, 134, f"Test {i + 1}", 13.5, "middle")
                     + tx(x + 175, 152, ["ingestion", "bronze → silver", "silver → gold", "gold → metrics"][i], 11.5, "middle", fill="#555"))
            b.append(f'<line x1="{x + 180}" y1="62" x2="{x + 175}" y2="112" stroke="{D.INK}" stroke-width="1.2" stroke-dasharray="3 3"/>')
    b.append(rect(20, 186, 1000, 40, "#FFF4D9", r=10) + tx(520, 211, "End to end: all hops together, synthetic → DataTwin → real data in pre-production → parallel run", 13.5, "middle"))
    return svg(1040, 236, "".join(b), "Five layers with four hops between them; each hop has its own integration test with fixed input, then end-to-end runs cover all hops together.")


def evidence():
    """Every test kind writes evidence; one release report decides."""
    src = ["static analysis + purity", "unit + coverage", "integration, per hop", "DataTwin", "real-data run + compare", "profile comparison"]
    b = []
    for i, s in enumerate(src):
        y = 14 + i * 40
        b.append(rect(20, y, 250, 32, "#F4F4F2", r=8) + tx(36, y + 21, s, 13))
        b.append(arr(270, y + 16, 360, 130))
    b.append(rect(360, 90, 200, 80, "#E6F4EC") + tx(460, 124, "Test-run record", 15.5, "middle") + tx(460, 146, "one run id per release", 12, "middle", fill="#555"))
    b.append(arr(560, 130, 620, 130))
    b.append(rect(620, 80, 190, 100, "#FFF4D9") + tx(715, 116, "Release report", 15.5, "middle") + tx(715, 138, "every line from a test,", 12, "middle") + tx(715, 156, "never ticked by hand", 12, "middle"))
    b.append(arr(810, 130, 860, 130))
    b.append(rect(860, 92, 160, 76, "#F8E6EF") + tx(940, 124, "Release gate", 15.5, "middle") + tx(940, 146, "all pass, or stop", 12, "middle"))
    return svg(1040, 260, "".join(b), "Every kind of evidence (eight, listed in the table below) flows into one test-run record, which produces a release report that drives the release gate.")


# ------------------------------------------------------------------ data
KINDS = [
    ("1 · Static analysis", "Problems found by reading the code: bad PySpark patterns, collect() on big data, cartesian joins, MERGE without keys, SQL injection, secrets, costly job settings, metric view mistakes; and whether each function is pure",
     "none", "Laptop, pull request", "Shift-left bundle: 131 checks; purity classifier (pure, impure, unknown, and 'could be pure' hints)"),
    ("2 · Unit tests", "Each pure function returns the right rows, case by case: new, changed, unchanged, deleted, duplicated, late, across a clock change",
     "Small tables written inside the test (table-driven)", "Laptop, pull request; seconds", "pytest + local Spark and Delta; the shift-left test kit for SCD2, idempotency, duplicates and dropped rows"),
    ("3 · Coverage and mutation", "The tests really exercise the logic, and fail when the logic is broken on purpose",
     "—", "Pull request", "coverage.py (branch coverage) on the pure modules; mutation testing on critical logic"),
    ("4 · Contract tests", "Each data contract is valid, and a change does not break the teams that use the data",
     "—", "Pull request", "ODCS schema validation + breaking-change comparison with the last released version"),
    ("5 · Integration, one hop at a time", "One hop works on the real platform: source → bronze, bronze → silver, silver → gold, gold → metrics (table below)",
     "Fixed fixtures with known answers", "Dev environment, after merge, on a fresh schema", "Deployment bundle + the platform's job runner"),
    ("6 · End to end, synthetic", "All hops together give the expected numbers from source to metric",
     "A fixed synthetic dataset with known answers", "Dev or test", "Same as above, run as one job"),
    ("7 · DataTwin", "The platform survives bad days: 30 simulated days with faults planted on purpose; it catches each one, holds bad data back, and every number matches the simulated world's truth",
     "Generated by DataTwin", "Dev, nightly; pre-production, before each release", "DataTwin"),
    ("8 · End to end on real data", "The new version works on real data, with mess nobody imagined",
     "Zero-copy clones of production tables; personal data already tokens, recipes and the token vault left out", "Pre-production, before release", "Table clones (Delta shallow clone) + the same jobs"),
    ("9 · Parallel run and data compare", "The new version gives the same numbers as production, or differs exactly where we meant it to",
     "Same real input to the old and the new version", "Pre-production, for any change to existing logic", "Our compare job: full outer join on keys, counts and sums per key, every metric's result, with tolerances"),
]

HOP_TESTS = [
    ("Source → bronze", "Sample files and change records in the landing folder",
     "Every row lands once; arrival details added; the same file again changes nothing; unexpected new columns kept; run log and watermark right"),
    ("Bronze → silver", "A bronze table with duplicates, late rows, a schema change, a delete, and a record changed twice in a day",
     "Types and standardisation right; the contract check stops the schema change; duplicates removed; SCD2 versions and dates right; bad rows quarantined with a reason; a re-run changes nothing; rows in = rows out + quarantined"),
    ("Silver → gold", "Silver tables including a missing dimension row and a late-arriving contributing fact",
     "The fact's level of detail is right; no row dropped (reconciliation); an inferred member is created, then filled when the dimension arrives; changed windows recomputed; totals match silver"),
    ("Gold → metrics", "Gold tables with known answers",
     "Each metric returns the expected number (for example scrap rate for plant A on day 3 = 2.4%); joins and filters right; masked columns stay masked"),
]

TWIN_VS_REAL = [
    ("DataTwin (simulation)", "Faults we know about, on purpose, every night", "Late files, duplicates, schema changes, a job dying halfway, clock changes", "Cannot know this company's real formats and odd values"),
    ("End to end on real data", "This company's real data, before release", "Odd values, real volumes, real edge cases nobody wrote down", "Only the faults that happen to be in the data that week"),
    ("Parallel run", "That nothing changed that should not have", "A fix that also moves a number it should not", "Needs a production version to compare with"),
]

AB_ROWS = [
    ("Parallel run (shadow run, data diff)", "Old and new pipeline on the same data; outputs compared", "Pipelines: every change to existing logic", "Pursue"),
    ("Canary release", "The new version switched on for one plant or one business unit first, watched, then rolled out", "Risky pipeline changes", "Pursue for risky changes"),
    ("A/B testing (true sense)", "Users split between two versions; their behaviour measured", "The conversation UI and Genie: two ways of answering, measured on accuracy and ratings", "Only for user-facing AI, not pipelines"),
]

EVIDENCE_ROWS = [
    ("Static analysis", "No must-fix finding; impure functions in transformation modules did not grow"),
    ("Unit tests and coverage", "All pass; branch coverage on pure modules at or above target; mutation score on critical logic"),
    ("Contract tests", "All contracts valid; no unapproved breaking change"),
    ("Integration, per hop", "All four hops pass, including the re-run test"),
    ("DataTwin", "Every planted fault caught and held; dashboard matches the simulated truth"),
    ("Real-data run and compare", "Differences from production are zero, or each is explained and approved"),
    ("Profile comparison", "Row counts, empty rates, distinct counts and ranges within tolerance of the last good run"),
    ("Quality rules and reconciliation", "All stop-level rules pass; source totals = gold totals; rows in = rows out + quarantined"),
]

TARGETS = [
    ("Purity", "Transformation modules are mostly pure; the number of impure functions in them may not grow in a pull request", "Keeps logic unit-testable"),
    ("Branch coverage", "90% on pure modules; no target on the thin read and write layer", "Integration tests cover the edges"),
    ("Mutation testing", "On critical logic only: SCD2, deduplication, inferred members, key metrics", "Proves the tests would notice a wrong answer"),
    ("Integration", "One test per hop, every merge", "A failure points at one hop"),
    ("Real data", "Pre-production run + parallel run for every change to existing logic", "Catches what simulation cannot"),
    ("Canary", "One plant or unit first for risky changes", "Limits the blast radius"),
]

TOOLS = [
    ("Static analysis", "Shift-left bundle (Ruff, sqlfluff, dbt-bouncer underneath)", "Same, plus Databricks job and SQL checks", "Ours (built)"),
    ("Unit tests", "pytest + local Spark and Delta", "Same; no cluster needed", "Open source"),
    ("Coverage and mutation", "coverage.py, mutmut", "Same", "Open source"),
    ("Contract tests", "ODCS + datacontract CLI", "Same", "Open standard"),
    ("Integration and end to end", "Deployment bundle per environment, fresh schema per change", "Databricks Asset Bundles, Lakeflow Jobs", "Platform"),
    ("Real-data clones", "Zero-copy table clones", "Delta shallow clone in Unity Catalog", "Platform"),
    ("Simulation", "DataTwin", "DataTwin on Databricks", "Ours (designed; Studio built)"),
    ("Profiles and quality", "A profiler and a quality engine behind one port", "DQX profiler and checks", "Databricks Labs"),
    ("Compare", "Key-based compare job + metric comparison", "Same, in SQL", "Ours"),
]

FAQ = [
    ("Why not just test on production data and look at the dashboard?", "Because by then the wrong number has already been seen. Most problems are cheaper to catch in seconds on a laptop than in hours on a cluster, and the ones that only show on real data are caught in pre-production, before release."),
    ("Is DataTwin enough for end-to-end testing?", "No. DataTwin proves the platform survives the faults we know about. A run on real data in pre-production, compared with production, proves it works on this company's actual data. We need both."),
    ("Which one is A/B testing?", "In data pipelines, what people usually mean is a parallel run: old and new versions on the same data, outputs compared. True A/B testing splits users between two versions and belongs to user-facing AI like a conversation UI."),
    ("Why insist on pure functions?", "A pure function can be tested with a small table in seconds, without a cluster. If most logic is pure, unit tests cover most of it, and the slow integration tests only need to prove the plumbing."),
    ("Who owns the test strategy?", "The test strategy lead in the centre of excellence writes it into the specs; data engineers write the unit and integration tests; the release gate reads the evidence."),
]


def page():
    kinds = table(["Kind", "What it proves", "Data used", "Where and when", "Built with"], KINDS)
    hop_t = table(["Hop", "Fixed input", "The test passes when"], HOP_TESTS)
    twin_t = table(["Test", "Proves", "Catches", "Cannot catch"], TWIN_VS_REAL)
    ab_t = table(["Name", "What it is", "Use it for", "Verdict"], AB_ROWS)
    ev_t = table(["Evidence", "Passes when"], EVIDENCE_ROWS)
    tg_t = table(["Target", "Rule", "Why"], TARGETS)
    tools_t = table(["Job", "Any platform", "On Databricks", "Comes from"], TOOLS)
    faq = C.faq(FAQ)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › <a href="{BASE}">Data platform architecture</a> › Test architecture</p>
<p class="eyebrow" style="margin-top:22px">Data platform architecture · testing</p>
<h1>Test architecture for a data platform</h1>
<p class="lede">How to know the numbers are right before anyone sees them: nine kinds of test, from reading the code to comparing a new version with production on real data, and one release report that decides.</p>
<div class="sib"><a href="{BASE}">↑ Data platform architecture</a><a href="/learn/shift-left/">Shift left</a><a href="/learn/datatwin/">DataTwin</a><a href="{BASE}aws-databricks/">On AWS + Databricks</a></div>
<nav class="toc"><b>On this page</b><ol>
<li><a href="#minute">The one-minute version</a></li><li><a href="#pure">Logic in pure functions</a></li><li><a href="#kinds">Nine kinds of test</a></li>
<li><a href="#hops">One integration test per hop</a></li><li><a href="#real">Simulation and real data</a></li><li><a href="#ab">Parallel run, canary, A/B</a></li>
<li><a href="#evidence">Evidence and the release report</a></li><li><a href="#targets">Targets</a></li><li><a href="#gates">When each test runs</a></li>
<li><a href="#tools">Tools</a></li><li><a href="#faq">Questions</a></li></ol></nav>

<section id="minute"><p class="eyebrow">The one-minute version</p><h2>Cheap tests catch most problems; real-data tests catch the rest</h2>
<div class="answer">
<p><b>Push logic into pure functions.</b> Then fast unit tests on a laptop cover most of the logic, and slow tests only need to prove the plumbing.</p>
<p><b>Test each hop on its own.</b> Source to bronze, bronze to silver, silver to gold, gold to metrics: a failure points at one place.</p>
<p><b>Use simulation and real data, not one or the other.</b> DataTwin plants known faults; a pre-production run on real data, compared with production, catches what nobody imagined.</p>
<p><b>Release on evidence.</b> Every test writes its result to one record; the release report is generated from it, never ticked by hand.</p>
</div></section>

<section id="pure"><p class="eyebrow">Design for testing</p><h2>Logic in the middle, input and output at the edges</h2>
<p>A <b>pure function</b> gives the same output for the same input and touches nothing else: it reads no table, writes no file, calls no service and does not look at the clock. For data code that means <i>DataFrame in, DataFrame out</i>. Everything else is <b>impure</b>.</p>
<figure class="diagram">{core_shell()}<figcaption>Put all business logic in the pure core. The read and write layers stay thin, so there is little in them to go wrong.</figcaption></figure>
<p>Static analysis enforces it: the shift-left bundle marks every function pure, impure or unknown, shows where an impure function <i>could</i> be pure, and fails a pull request that adds impure functions to a transformation module.</p></section>

<section id="kinds"><p class="eyebrow">Nine kinds of test</p><h2>From reading the code to comparing with production</h2>
<figure class="diagram">{pyramid()}<figcaption>Many cheap tests at the bottom, few costly ones at the top. Each kind catches something the others cannot.</figcaption></figure>
{kinds}</section>

<section id="hops"><p class="eyebrow">Integration</p><h2>One integration test per hop</h2>
<p>Each hop between layers has its own integration test, with a fixed input and a known expected output, run on the real platform in the dev environment on a fresh schema. When one fails, you know which hop broke.</p>
<figure class="diagram">{hops()}<figcaption>Four hop tests, then end-to-end runs over all hops together.</figcaption></figure>
{hop_t}</section>

<section id="real"><p class="eyebrow">Simulation and real data</p><h2>DataTwin is not the whole story</h2>
<p><a href="/learn/datatwin/">DataTwin</a> runs the platform in a simulated business and plants faults on purpose, so the bad days happen on schedule. But a simulation only contains what someone thought of. Real data has formats, values and volumes nobody wrote down. So before release the new version also runs <b>end to end on real data</b> in pre-production, using zero-copy clones of production tables: instant, cheap, and production is never touched. Personal data stays masked and restricted data is left out.</p>
{twin_t}</section>

<section id="ab"><p class="eyebrow">Old version against new</p><h2>Parallel run, canary, and what A/B testing means here</h2>
<p>For any change to logic that already runs in production, the old and new versions run side by side on the same real input and the outputs are compared: row by row on keys, counts and sums per key, and the result of every metric. "Scrap rate per plant per day matches to 0.01%, except plant B, where the bug fix moved it as intended" is release evidence.</p>
{ab_t}</section>

<section id="evidence"><p class="eyebrow">Evidence</p><h2>Profiles, checks and one release report</h2>
<p>Every test run in the dev and pre-production environments also profiles its outputs and compares them with the last good run, and runs every quality rule and reconciliation. All results go to one test-run record, and the release report is generated from it.</p>
<figure class="diagram">{evidence()}<figcaption>Nobody ticks the release report by hand; every line comes from a test.</figcaption></figure>
{ev_t}</section>

<section id="targets"><p class="eyebrow">Targets</p><h2>What "good enough to release" means</h2>
{tg_t}</section>

<section id="gates"><p class="eyebrow">When each test runs</p><h2>Six gates from laptop to production</h2>
<figure class="diagram">{D.gates()}<figcaption>The earlier a problem is caught, the cheaper it is to fix.</figcaption></figure></section>

<section id="tools"><p class="eyebrow">Tools</p><h2>What does each job</h2>
{tools_t}
<p class="note">Product names change often; check the current docs before you build.</p></section>

<section id="faq"><p class="eyebrow">Questions</p><h2>Questions people ask</h2>{faq}</section>

<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2>
<p><b>The checks themselves:</b> <a href="/learn/shift-left/">Shift left: fail fast on data code</a>, with pure functions, table-driven tests, SCD2 tests, coverage and mutation testing.</p>
<p><b>The faults to test for:</b> <a href="/learn/data-platform-sim/problems/">the Problem Lab</a>, nineteen data problems run for real, each with the naive fix and the right one.</p>
<p><b>Simulation:</b> <a href="/learn/datatwin/">DataTwin, explained</a>. <b>On a real stack:</b> <a href="{BASE}aws-databricks/#testing">testing on AWS + Databricks</a>.</p></section>"""
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": "Test architecture for a data platform",
           "description": "Nine kinds of test for a data platform: static analysis with a purity check, unit tests on pure functions, coverage and mutation, contract tests, one integration test per layer hop, synthetic end to end, DataTwin simulation, end to end on real data, and a parallel run against production.",
           "url": URL, "inLanguage": "en", "isAccessibleForFree": True, "dateModified": "2026-11-02",
           "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]
    head = D.CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    desc = "Test architecture for a data platform: pure functions, nine kinds of test, one integration test per layer hop, DataTwin and real-data runs, parallel run against production, one release report."
    return wb.page("Test architecture for a data platform", desc, URL, body, head)


def main():
    out = ROOT / "learn" / "data-platform-architecture" / "testing"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("test architecture ->", out)


if __name__ == "__main__":
    main()
