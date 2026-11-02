"""Shift-left checks for data code: a hub and one page per topic under /learn/shift-left/.

    python3 _guides/shift_left.py

Teach first, then decide. Source of truth: ~/shift-left-bundle/PLAN.html and REUSE.md
(public repo dataagentsai/shift-left-bundle). No company product names on the site:
the cost rules are described, not named.
"""
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "_paths"))
import components as C  # noqa: E402  (page CSS, table(), faq(), code())
import realtime as R  # noqa: E402  (ld(), short_desc(), shared CSS)
from diagrams import FILL, arrow, box, svg, text  # noqa: E402

wb = C.wb
SITE = wb.SITE
BASE = "/learn/shift-left/"
REPO = "https://github.com/dataagentsai/shift-left-bundle"
table, faq, code = C.table, C.faq, C.code
CSS = R.CSS

# slug, short label, page title, one line for the map
PAGES = [
    ("basics", "Shift left, explained", "Shift left: find problems before the code runs", "Why a problem found in the editor costs a minute and the same problem on the cluster costs a morning."),
    ("how-software-solved-it", "How software solved it", "How the software world already solved this", "Ten standard practices and the open-source tools behind each. Nothing here is new."),
    ("syntax-trees", "Syntax trees", "Every language already has a syntax tree", "Linters read code as a tree. Python, SQL, PySpark and Databricks each have a mature parser."),
    ("pure-functions", "Pure functions", "Pure functions in PySpark: possible, and how we detect them", "Most data logic can be pure. How a tool tells pure, impure and unknown apart."),
    ("tests-and-coverage", "Tests, coverage, complexity", "Unit tests, coverage and complexity for PySpark", "coverage.py, its three blind spots, mutation testing, and a complexity score."),
    ("data-tests", "Testing data logic offline", "Testing SCD2, idempotency, duplicates and dropped rows without a cluster", "History tracking, reruns, duplicate keys, lost records and cartesian joins, all caught on a laptop."),
    ("clean-code", "Clean code", "Clean-code checks: early return and the rest", "Nested ifs, long functions, dead code. Ruff already has the rules; you switch them on."),
    ("security-and-cost", "Security and cost", "Security, secrets, vulnerable libraries and cost", "What can be caught without running anything, from leaked tokens to cartesian joins."),
    ("whats-missing", "What is missing", "The gap report: what a repo is missing", "Point it at a repo; it lists missing tests, missing checks and missing setup."),
    ("the-bundle", "The bundle", "The shift-left bundle: design, tools and status", "Check families, tools with verdicts, why not SonarQube, git layout, and where the work stands."),
]
SHORT = {s: sh for s, sh, _, _ in PAGES}
TITLE = {s: t for s, _, t, _ in PAGES}


def fig(s, cap):
    return f'<figure class="diagram">{s}<figcaption>{cap}</figcaption></figure>'


def siblings(cur):
    return '<div class="sib"><a href="' + BASE + '">↑ All of shift left</a>' + "".join(
        f'<span>{SHORT[s]}</span>' if s == cur else f'<a href="{BASE}{s}/">{SHORT[s]}</a>' for s, *_ in PAGES) + "</div>"


def link(slug, label=None):
    return f'<a href="{BASE}{slug}/">{E(label or SHORT[slug])}</a>'


# ------------------------------------------------------------------ drawings
def timeline():
    steps = [("Editor", "seconds", "mint"), ("Commit", "under 10 s", "mint"), ("Pull request", "under 5 min", "mint"), ("Pre-deploy", "under 1 min", "mint"),
             ("Test run", "hours", "white"), ("Production", "a failed job", "white"), ("The bill", "money spent", "rose")]
    b = '<rect x="6" y="6" width="600" height="120" rx="16" fill="none" stroke="#1F1F1F" stroke-width="1.6" stroke-dasharray="8 6"/>'
    b += text(306, 30, "shift-left checks work here: no cluster, no data", 16, fill="#1F1F1F")
    x = 14
    for i, (t, s, f) in enumerate(steps):
        b += box(x, 44, 132, 72, t, s, f)
        if i < len(steps) - 1:
            b += arrow(x + 134, 80, x + 150, 80)
        x += 150
    b += arrow(620, 150, 1040, 150, "")
    b += text(830, 175, "the cost of finding a problem goes up this way", 15)
    return svg(1060, 190, b, "A change moves from editor to commit, pull request, pre-deploy, test run, production and the bill. Shift-left checks cover the first four steps.")


def tree_drawing():
    b = box(10, 40, 170, 80, "Your code", ".py, .sql,\nnotebook, YAML", "white") + arrow(182, 80, 222, 80, "parse")
    b += box(224, 40, 170, 80, "Syntax tree", "nodes: call, join,\nfilter, loop", "peri") + arrow(396, 80, 436, 80, "walk")
    b += box(438, 40, 170, 80, "Rules", "if node looks like X,\nreport it", "butter") + arrow(610, 80, 650, 80)
    b += box(652, 40, 170, 80, "Finding", "file, line, id,\nwhy, fix", "mint") + arrow(824, 80, 864, 80)
    b += box(866, 40, 170, 80, "Pull request", "shown on the\nchanged line", "lilac")
    b += text(523, 160, "the parser comes off the shelf; we only write the rules nobody else has", 15)
    return svg(1050, 175, b, "Code is parsed into a syntax tree, rules walk the tree, findings carry file, line and fix, and show on the pull request.")


def shell_drawing():
    b = '<rect x="10" y="10" width="620" height="200" rx="18" fill="#F3F3F1" stroke="#1F1F1F" stroke-width="1.6"/>'
    b += text(320, 36, "impure shell: thin, tested by integration tests", 15, fill="#1F1F1F")
    b += box(30, 70, 120, 64, "Read", "spark.table", "rose") + arrow(152, 102, 196, 102)
    b += '<rect x="198" y="52" width="244" height="104" rx="16" fill="#F0F8F3" stroke="#1F1F1F" stroke-width="2.2"/>'
    b += text(320, 82, "pure core", 19, fill="#1F1F1F") + text(320, 106, "DataFrame in, DataFrame out", 14) + text(320, 128, "unit tests in seconds", 14)
    b += arrow(444, 102, 488, 102) + box(490, 70, 120, 64, "Write", "saveAsTable", "rose")
    b += text(320, 190, "clock, random, dbutils and secrets also stay in the shell and are passed in", 14)
    return svg(640, 220, b, "A pure core takes a DataFrame and returns a DataFrame. Reads, writes, the clock and dbutils stay in a thin impure shell around it.")


def verdict_drawing():
    cols = [("pure", "mint", ["only known-pure calls", "DataFrame in, out", "unit test it"]),
            ("impure", "rose", ["found a side effect", "reason + line shown", "keep it thin"]),
            ("unknown", "butter", ["calls something unseen", "counts as not pure", "until marked @pure"])]
    b, x = "", 10
    for t, f, items in cols:
        b += f'<rect x="{x}" y="10" width="250" height="160" rx="16" fill="{FILL[f]}" stroke="#1F1F1F" stroke-width="1.6"/>' + text(x + 125, 44, t, 22, fill="#1F1F1F")
        for i, it in enumerate(items):
            b += text(x + 125, 84 + i * 28, it, 15)
        x += 270
    return svg(820, 180, b, "Three verdicts: pure, impure with the reason and line, and unknown, which counts as not pure until marked.")


def gates_drawing():
    rows = [("On commit", "under 10 s", "lint, clean code, security, secrets, SQL and cost rules on changed files", "mint"),
            ("Pull request", "under 5 min", "+ unit tests, coverage on changed lines, purity, complexity, vulnerable libraries, plan check", "peri"),
            ("Nightly", "no limit", "mutation testing, repo security score, gap report, trends", "butter"),
            ("Before deploy", "under 1 min", "job and cluster config rules, bundle validation", "lilac")]
    b = ""
    for i, (t, s, what, f) in enumerate(rows):
        y = 10 + i * 66
        b += box(10, y, 170, 56, t, s, f) + text(200, y + 34, what, 15, anchor="start", fill="#1F1F1F")
    return svg(1000, 276, b, "Four places checks run: on commit in under 10 seconds, on the pull request in under 5 minutes, nightly, and before deploy.")


def sources_drawing():
    items = [("Python code", "loops, collect,\nUDFs, toPandas", "peri"), ("SQL text", "SELECT *, cross join,\nno partition filter", "butter"),
             ("Query plan", "EXPLAIN on\nempty tables", "lilac"), ("Job config", "auto-stop, cluster\ntype, tags", "rose")]
    b, x = "", 10
    for t, s, f in items:
        b += box(x, 20, 200, 84, t, s, f) + arrow(x + 100, 106, 470, 150)
        x += 230
    b += box(370, 152, 200, 56, "Cost findings", "", "mint")
    return svg(940, 220, b, "Cost checks look in four places: Python code, SQL text, the query plan on empty tables, and job configuration.")


# ------------------------------------------------------------------ pages
def basics():
    body = f"""<section id="plain"><p class="eyebrow">In plain words</p><h2>Move the checks to the left</h2>
<p>Draw the life of a change from left to right: you write it, commit it, open a pull request, deploy it, it runs, and the bill arrives. A problem costs more the further right it is found. A cartesian join caught in the editor costs one minute. The same join found on the cluster costs a failed job, a bill and a morning of someone's time.</p>
<p><b>Shift left</b> means moving as many checks as possible to the left end, where they need no cluster and no data: reading the code, running unit tests on tiny DataFrames, and checking job settings before deploy.</p>
{fig(timeline(), "The dashed box is where shift-left checks run. Everything inside it is cheap and fast.")}</section>

<section id="limits"><p class="eyebrow">Be honest about it</p><h2>What it can catch, and what it can't</h2>
{table(["Can catch before running", "Can't catch without running"], [
        ("Code shapes that are always wrong or costly: collect in a loop, SELECT *, cross join, DELETE without WHERE", "Data skew and real data volumes"),
        ("Secrets in the code, libraries with known vulnerabilities, unsafe code", "Flaky sources, late files, network failures"),
        ("Logic bugs, through unit tests on tiny DataFrames", "What the cluster actually costs at run time"),
        ("Untested and overly complex functions", "Problems that only appear with production data"),
        ("A bad query plan, from EXPLAIN on empty tables", "Performance at full scale"),
        ("Costly job and cluster settings", "Whether the business rule itself is right")])}
<p>So shift left is one part of testing and code review, not all of it. It removes the cheap problems early, so the expensive tests and the reviewers spend their time on the hard ones.</p></section>

<section id="noise"><p class="eyebrow">The one rule</p><h2>Noise kills adoption</h2>
<p>If a check cries wolf, developers stop reading all the checks. So at the start, only problems that must never ship block a change: security holes, leaked secrets and cartesian joins. Everything else warns. Existing code is recorded in a baseline, so only new problems fail. Rules that are often wrong are fixed or dropped. See {link("how-software-solved-it", "how the software world solved it")}.</p></section>"""
    qa = [("What is shift-left testing?", "Moving checks to the earliest point in a change's life, the editor, the commit and the pull request, where they are fast and need no cluster or data. A problem found there costs minutes instead of a failed job and a bill."),
          ("Can static analysis replace running the pipeline?", "No. It catches code shapes, secrets, vulnerable libraries, untested logic and bad plans. It can't see data skew, real volumes or run-time cost. Those need integration tests and monitoring."),
          ("Should every finding block a merge?", "No. Block only what must never ship (security, secrets, cartesian joins), warn on the rest, and baseline existing code so only new problems fail.")]
    return "basics", "Shift left means finding problems in PySpark, Python and SQL code before it runs: in the editor, on commit and on the pull request. What it can and can't catch.", body, qa


def how_software_solved_it():
    body = f"""<section id="plain"><p class="eyebrow">In plain words</p><h2>Nothing here is new</h2>
<p>Application developers have solved most of this over the last twenty years. Data code is usually behind because notebooks made it easy to skip the habits. The practices below are standard, and each one already has mature open-source tools.</p>
{table(["Practice", "The idea in one line", "Open source that does it"], [
        ("Functional core, imperative shell", "Keep the logic in pure functions (data in, data out) and push reads and writes to the edges. Pure functions are easy to unit test.", "A design rule; import-linter enforces that the core never imports the IO code"),
        ("Test pyramid", "Many fast unit tests, fewer slow integration tests, very few end-to-end runs.", "pytest, Spark's built-in assertDataFrameEqual"),
        ("Coverage on new code", "Don't fail on old debt; require coverage only on the lines a change touches.", "coverage.py and diff-cover"),
        ("Mutation testing", "Coverage shows a line ran, not that a test would catch a bug. Change the code on purpose and check that a test fails.", "mutmut"),
        ("Property-based tests", "Check rules such as 'never more rows out than in' on many generated inputs.", "Hypothesis"),
        ("Complexity budget", "Flag functions too tangled to read or test.", "Ruff C901 (cyclomatic), complexipy (cognitive)"),
        ("Static analysis in review, low noise", "Show findings on the pull request, on the changed line, and drop any rule developers mostly mark as wrong.", "SARIF format, shown by GitHub code scanning or the Azure DevOps SARIF tab"),
        ("Same checks everywhere", "The laptop and CI run the same configuration.", "pre-commit"),
        ("Ratchet", "Record today's findings; block only new ones; tighten over time.", "a baseline file"),
        ("Supply-chain hygiene", "Pinned libraries, known-vulnerability scans, no secrets, a scored checklist of repo practices.", "osv-scanner, gitleaks, OpenSSF Scorecard")])}</section>

<section id="lesson"><p class="eyebrow">The lesson that matters most</p><h2>Developers ignore noisy tools</h2>
<p>Large companies that run static analysis at scale learned the same thing: a check is only useful if developers act on it. Findings must appear in the code review, on the line that changed, with a clear fix, and the rate of wrong findings must stay low. A tool with a thousand findings on day one gets switched off.</p>
<p>That is why this guide starts every rule as a warning, baselines old code, and blocks only a short list. See {link("the-bundle", "the bundle")} for the gate policy.</p></section>"""
    qa = [("What is the functional core, imperative shell pattern?", "Put the logic in pure functions that take data and return data, and keep reading, writing and other side effects in a thin outer layer. The core is unit tested in seconds; the shell gets a few integration tests."),
          ("Is code coverage enough?", "No. Coverage shows that a line ran during a test, not that a test would notice if the line were wrong. Mutation testing checks that; run it on the pure functions, where it is fast."),
          ("How do I add checks to an old codebase without blocking everyone?", "Record today's findings in a baseline, block only new findings, and require coverage only on changed lines. Tighten the rules as the old findings get fixed.")]
    return "how-software-solved-it", "How software engineering already solved fail-fast checks: functional core, test pyramid, coverage on new code, mutation testing, complexity budgets, low-noise review, ratchets.", body, qa


def syntax_trees():
    body = f"""<section id="plain"><p class="eyebrow">In plain words</p><h2>A linter reads a tree, not text</h2>
<p>Searching code as plain text breaks easily: a comment or a string can look like a problem. A proper linter first <b>parses</b> the code into a <b>syntax tree</b>, where every call, join, filter and loop is a node. Rules then walk the tree: "if a <code>collect()</code> node sits inside a <code>for</code> node, report it."</p>
{fig(tree_drawing(), "Parse, walk, report. Every layer of a data project has a mature parser, so we only write rules.")}</section>

<section id="layers"><p class="eyebrow">Layer by layer</p><h2>The parser for each layer</h2>
{table(["Layer", "What it becomes", "Parser", "Also used by"], [
        ("Python", "Python syntax tree", "ast (built into Python); LibCST to rewrite code safely; astroid to know what a name refers to", "Most Python linters; Databricks UCX uses astroid"),
        ("SQL, Databricks dialect", "SQL syntax tree, with column lineage", "sqlglot (MIT licence, very active)", "Databricks UCX and Lakebridge"),
        ("SQL style", "SQL parse tree", "SQLFluff, with a databricks dialect", "dbt projects"),
        ("PySpark DataFrame code", "Spark's own plan (Catalyst), from EXPLAIN on local Spark with empty tables that have the real columns", "Spark itself", "Spark's optimiser"),
        ("Databricks jobs and clusters", "Bundle configuration (YAML)", "the bundle schema and databricks bundle validate", "Databricks CLI"),
        ("Azure Data Factory", "Pipeline JSON", "JSON", "Azure tooling")])}</section>

<section id="pyspark"><p class="eyebrow">The PySpark trick</p><h2>The plan is PySpark's real syntax tree</h2>
<p>PySpark code is Python, so the Python tree sees <code>df.join(other)</code> but not what Spark will do with it. Spark's plan does. Build each input as an <b>empty</b> DataFrame with the real columns, run the transformation, and call EXPLAIN. That takes a few seconds on a laptop, reads no data, and shows a cartesian product, Python UDF evaluation or a scan with no filter pushed down.</p>
{code('''orders = spark.createDataFrame([], "order_id INT, customer_id INT, country STRING")
customers = spark.createDataFrame([], "customer_id INT, name STRING")
plan = orders.join(customers).filter("country = 'IN'")      # no join key: a cartesian product
plan.explain()   # the plan names the join type; a rule reports a cartesian product or nested-loop join''', "Checked on Spark 3.5.1: with empty inputs, the physical plan shows CartesianProduct, without reading any data.")}
<p>It can't see sizes, so it can't judge broadcast choices or skew. Those need statistics or a real run.</p></section>"""
    qa = [("What is an abstract syntax tree?", "The structure of code after parsing: each call, condition, join and loop becomes a node in a tree. Linters walk the tree, which is far more reliable than searching the text."),
          ("Is there a SQL parser for Databricks SQL?", "Yes. sqlglot parses the Databricks dialect into a syntax tree and is used by Databricks' own UCX and Lakebridge tools. SQLFluff also has a databricks dialect for style rules."),
          ("How can I check a PySpark plan without data?", "Create empty DataFrames with the real schemas, run the transformation and call explain(). The physical plan shows join types, Python UDF evaluation and pushed filters in seconds.")]
    return "syntax-trees", "Linters read code as a syntax tree. The parsers for Python (ast, LibCST), Databricks SQL (sqlglot, SQLFluff), PySpark (the Spark plan) and Databricks config.", body, qa


def pure_functions():
    body = f"""<section id="plain"><p class="eyebrow">In plain words</p><h2>What a pure function is</h2>
<p>A <b>pure</b> function gives the same output for the same input and touches nothing outside itself: no reading a table, no writing, no clock, no random numbers, no secrets. Pure functions are the easiest code to test, because a test only has to pass data in and check what comes out.</p>
<p>Spark makes this easier than plain Python. A DataFrame never changes in place; every step returns a new one, and nothing runs until an action such as a write. So a function that takes a DataFrame and returns a DataFrame using only column expressions is pure. Spark even has <code>df.transform(f)</code> to chain such functions.</p>
{fig(shell_drawing(), "Most of the logic lives in the pure core. The shell around it is thin.")}</section>

<section id="refactor"><p class="eyebrow">Before and after</p><h2>Turning an impure function into a pure one</h2>
{code('''# Before: impure. It reads a table, uses the clock and writes, so a test needs real tables.
def load_silver_orders():
    df = spark.table("bronze.orders")
    df = df.dropDuplicates(["order_id"]).withColumn("load_ts", F.lit(datetime.now()))
    df.write.mode("append").saveAsTable("silver.orders")


# After: the logic is pure; the read, the clock and the write sit in a thin shell.
def dedupe_orders(orders: DataFrame) -> DataFrame:                      # pure
    return orders.dropDuplicates(["order_id"])

def add_load_ts(df: DataFrame, load_ts: datetime) -> DataFrame:         # pure: the time is passed in
    return df.withColumn("load_ts", F.lit(load_ts))

def run(spark):                                                         # impure shell
    orders = spark.table("bronze.orders")
    out = orders.transform(dedupe_orders).transform(add_load_ts, datetime.now())
    out.write.mode("append").saveAsTable("silver.orders")''')}
<p><b>What stays impure, on purpose:</b> reads, writes, MERGE, <code>dbutils</code> and job entry points. Keep them thin. For a MERGE, the "what to merge" logic (removing duplicates, building history rows) is pure and only the final MERGE call is not. Values like <code>current_timestamp()</code>, <code>rand()</code> and <code>uuid()</code> make a function give different answers each run, so pass them in. Keep actions such as <code>.count()</code> and <code>.collect()</code> out of pure functions too: they make Spark run, and running costs money.</p></section>

<section id="detect"><p class="eyebrow">Can a tool tell?</p><h2>How we detect a pure function</h2>
<p>The tool reads each function's syntax tree and looks for anything that touches the world outside it. Python is too dynamic to <i>prove</i> purity in every case, so it gives three answers instead of two.</p>
{fig(verdict_drawing(), "Unknown is honest: the tool says when it can't see far enough.")}
{table(["Verdict", "Meaning", "Examples"], [
        ("impure", "A side effect was found. The report shows the reason and the line.", "spark.table, .write, saveAsTable, DeltaTable.merge, dbutils, open, HTTP calls, os.environ, datetime.now, random, current_timestamp(), rand(), uuid(), a global spark, changing an argument or a global, actions such as collect(), count(), show()"),
        ("pure", "Every call is on a known-pure list and nothing outside is touched.", "DataFrame methods that return a new DataFrame (select, withColumn, filter, join, groupBy().agg, dropDuplicates, union), most column functions, math, re, and functions in the repo already found pure"),
        ("unknown", "It calls something the tool can't see into. Counted as not pure until someone marks it.", "a third-party library call, a function passed in as an argument, getattr tricks")])}
<ul><li><b>It follows calls.</b> If <code>dedupe_orders</code> calls a helper that reads a table, both are impure, and the report shows the chain.</li>
<li><b>Marking.</b> A developer can mark a function <code>@pure</code>, using the marker from the open-source <i>deal</i> library. The static check still runs, so a wrong mark is reported.</li>
<li><b>Proof at test time.</b> A test fixture makes Spark's read, write and catalog calls fail during unit tests of pure functions. If a "pure" function touches a table, its test fails. Each test also runs the function twice and checks the outputs match.</li>
<li><b>Measured, not claimed.</b> A sample repo with planted pure, impure and tricky functions, and a hidden answer key, tells us how often the verdict is right.</li></ul>
<p>The report then lists: how many functions are pure, which impure ones could be pure (with a hint such as "take the DataFrame as a parameter; move the read to the caller"), and which pure ones have no test. See {link("tests-and-coverage", "tests and coverage")}.</p></section>"""
    qa = [("Can PySpark code be written as pure functions?", "Yes, for most of the logic. DataFrames are immutable, so a function that takes a DataFrame and returns one using column expressions is pure. Reads, writes, MERGE calls and dbutils stay in a thin outer layer."),
          ("How can a tool tell whether a Python function is pure?", "It reads the syntax tree and looks for side effects: table reads and writes, dbutils, file and network calls, the clock, random values, globals and Spark actions. Calls it can't see into are reported as unknown, not as pure."),
          ("Is current_timestamp() pure in Spark?", "No. It gives a different value on each run, so a function using it can't be tested with a fixed expected result. Pass the timestamp in as a parameter.")]
    return "pure-functions", "Pure functions in PySpark: what they are, how to refactor impure code into a pure core and thin shell, and how a tool classifies functions as pure, impure or unknown.", body, qa


def tests_and_coverage():
    body = f"""<section id="test"><p class="eyebrow">Unit tests</p><h2>A table of cases, a tiny DataFrame, seconds to run</h2>
<p>A pure function is tested by building a few rows on a local Spark session and comparing the result with Spark's built-in <code>assertDataFrameEqual</code> (Spark 3.5 and later). Write the cases as one table: each row is a name, the input rows and the expected rows. Adding a case is adding a line.</p>
{code('''import pytest
from pyspark.testing import assertDataFrameEqual
from silver.orders import dedupe_orders

SCHEMA = "order_id INT, amount DOUBLE"
CASES = [
    # name,                     input rows,                 expected rows
    ("removes duplicate orders", [(1, 10.0), (1, 10.0)],     [(1, 10.0)]),
    ("keeps distinct orders",    [(1, 10.0), (2, 5.0)],      [(1, 10.0), (2, 5.0)]),
    ("empty input stays empty",  [],                         []),
]

@pytest.mark.parametrize("name, rows, expected", CASES, ids=[c[0] for c in CASES])
def test_dedupe_orders(spark, name, rows, expected):
    got = dedupe_orders(spark.createDataFrame(rows, SCHEMA))
    assertDataFrameEqual(got, spark.createDataFrame(expected, SCHEMA))''', "Run on Spark 3.5.1 on 2 Nov 2026: all cases pass in about 7 seconds. The spark fixture is one local session shared by all tests.")}
<p class="warn"><b>Two setup traps we hit running this.</b> In Spark 3.5, importing <code>pyspark.testing</code> needs pandas and pyarrow installed (and numpy below 2 with older pandas). And Spark's worker processes must use the same Python as the test: set <code>PYSPARK_PYTHON</code> to the test's Python, or the tests fail with a Python version mismatch.</p></section>

<section id="coverage"><p class="eyebrow">Coverage</p><h2>coverage.py works for PySpark too</h2>
<p>Python's standard coverage tool is <b>coverage.py</b>, usually run through <b>pytest-cov</b>. It measures PySpark the same way as any Python, because PySpark code is Python running on the driver. It reports which lines and which branches of each <code>if</code> ran during the tests.</p>
<p><b>diff-cover</b> then looks only at the lines a pull request changed, so the gate can be "80% of the changed lines are covered" without failing on years of old code.</p>
{table(["Blind spot", "Why", "What to do"], [
        ("Code inside Python UDFs", "It runs in separate worker processes", "Test the UDF's Python function directly, or configure coverage for subprocesses"),
        ("SQL text", "SQL has no lines that coverage can count", "Test SQL by checking its output on tiny tables"),
        ("Notebooks", "Hard to measure and import", "Put the logic in .py modules; keep notebooks as thin callers")])}
<p>The purity rule fixes all three: the logic sits in pure functions in modules, where coverage works.</p></section>

<section id="mutation"><p class="eyebrow">Do the tests bite?</p><h2>Mutation testing</h2>
<p>Coverage says a line ran, not that a test would notice if it were wrong. <b>mutmut</b> changes the code on purpose (<code>&gt;</code> becomes <code>&gt;=</code>, a column name is swapped) and checks that some test fails. The share of changes caught is the mutation score. It is slow, so it runs nightly, on the pure functions only. <b>Hypothesis</b> adds property-based tests that try many generated inputs against a rule such as "never more rows out than in".</p></section>

<section id="complexity"><p class="eyebrow">Complexity score</p><h2>How tangled is each function?</h2>
{table(["Score", "What it counts", "Tool", "Verdict"], [
        ("Cyclomatic complexity", "The number of paths through a function (each if, loop, and/or adds one)", "Ruff rule C901 (McCabe)", "Pursue"),
        ("Cognitive complexity", "How hard it is to read: nesting costs extra, so deep ifs score high", "complexipy (fast, MIT licence)", "Pursue"),
        ("Maintainability index, trends", "A combined score; history over git", "radon, wily", "Drop: no releases since 2023–2024"),
        ("Many languages", "Complexity for Scala, Java, SQL and others", "lizard", "Later, when other languages arrive")])}
<p>The useful view joins the three reports: <b>complex and untested</b> functions are where bugs hide, and <b>pure but untested</b> functions are the cheapest tests to add.</p>
{code('''PURITY      112 functions: 61 pure, 51 impure (29 of them could be pure)
TESTS       17 pure functions have no test · changed lines covered: 64% (gate 80%)  FAIL
COMPLEXITY  gold/kpis.py:build_daily_kpis  cognitive 31, cyclomatic 18, untested  <- fix first''', "Illustrative report, not measured on a real repo.")}</section>"""
    qa = [("Does Python have a code coverage tool?", "Yes. coverage.py is the standard; pytest-cov runs it with pytest. It reports line and branch coverage, and diff-cover limits the check to the lines a change touched."),
          ("How do I measure test coverage for PySpark?", "The same way as Python: coverage.py via pytest-cov, with a local Spark session in the tests. It doesn't see code inside Python UDFs running on workers, SQL text, or notebooks, so keep logic in pure functions in modules."),
          ("Is there a tool that gives a code complexity score for Python?", "Yes. Ruff's C901 rule gives cyclomatic complexity, and complexipy gives cognitive complexity, which punishes nesting and matches readability better.")]
    return "tests-and-coverage", "Unit tests for PySpark as a table of cases, coverage.py and its blind spots, coverage on changed lines, mutation testing, and complexity scores.", body, qa


def data_tests():
    ex = f"{REPO}/tree/main/examples/scd2"
    body = f"""<section id="plain"><p class="eyebrow">In plain words</p><h2>Yes, without a cluster, if the logic is a pure function</h2>
<p>"Without running it" means without a cluster, real tables or real data. The code still runs, on a local Spark session with a few hand-made rows. That takes seconds. The trick is the one from {link("pure-functions", "pure functions")}: write SCD2 as <i>history and batch in, new history out</i>. Then the MERGE or overwrite is a thin shell, and every rule is testable.</p>
<p>The working example is in the repo: <a href="{ex}">examples/scd2</a>. It ran on 2 Nov 2026 on Spark 3.5.1: <b>27 tests passed in about 26 seconds</b> on a laptop.</p></section>

<section id="scd2"><p class="eyebrow">The cases</p><h2>SCD2 as a table of cases</h2>
<p>Each row is a batch and the history we expect afterwards. These eight cases are where SCD2 code usually breaks:</p>
{table(["Case", "What must happen"], [
        ("New customer", "A current version is added"),
        ("Row with no real change", "Nothing changes"),
        ("City changed", "The old version is closed on the new date; the new one is current"),
        ("Two changes for one customer in one batch", "Two versions, in time order; only the last is current"),
        ("Same row twice in a batch", "Counted once"),
        ("Row older than the current version (late)", "Not applied, and reported as late, never lost silently"),
        ("Batch replayed", "Nothing changes"),
        ("Value changes back to an earlier one", "That is a new version")])}</section>

<section id="properties"><p class="eyebrow">Beyond single cases</p><h2>Five checks that run on every case</h2>
<p>Hand-written cases check specific answers. These checks hold for <i>every</i> input, so the test kit runs them on each case automatically:</p>
{table(["Question", "Check", "How"], [
        ("Is it idempotent?", "assert_idempotent", "Apply the batch, then apply it again to the result. The second run must change nothing."),
        ("Any duplicates?", "assert_unique", "One current row per customer; no two versions with the same start date."),
        ("Any records dropped?", "assert_nothing_dropped", "Every input key is in the output or in an explicit rejects list. An inner join that loses orders with no matching store fails this."),
        ("Did a join multiply rows?", "assert_no_fanout", "Rows out are not more than rows in for a lookup join. A duplicate key in the lookup fails this."),
        ("Cartesian join?", "assert_no_cartesian", "Read the plan with empty inputs. A join with no key, or an always-true condition, fails this.")])}
{code("""@pytest.mark.parametrize("name, batch, expected", CASES, ids=IDS)
def test_scd2_properties(spark, name, batch, expected):
    hist, b = spark.createDataFrame(BASE, H), spark.createDataFrame(batch, B)
    out = scd2(hist, b)
    kit.assert_idempotent(scd2, hist, b)                         # run twice, nothing changes
    kit.assert_unique(out, ["customer_id"], where="is_current")  # one current version per key
    kit.assert_unique(out, ["customer_id", "valid_from"])        # no duplicate versions
    kit.assert_nothing_dropped(b, out, "customer_id", rejects=late_rows(hist, b))
    kit.assert_no_cartesian(scd2(kit.schema_only(hist), kit.schema_only(b)))""", "From examples/scd2/test_scd2.py.")}
<p><b>Does the kit catch real bugs?</b> The example plants them: an append-only "SCD2" that never closes versions fails the idempotency and one-current-row checks. An inner join that loses orders fails the dropped-records check. A join with no key fails the cartesian check. A test kit that can't fail is worth nothing, so these planted bugs are part of the tests.</p>
<p class="warn"><b>A trap we hit.</b> Building the empty inputs with <code>df.limit(0)</code> let Spark notice they were empty and fold the whole join away, so the cartesian product never appeared in the plan. Empty inputs must come from an empty RDD, which Spark can't see through. The kit's <code>schema_only()</code> does that.</p></section>

<section id="draft"><p class="eyebrow">Existing code with no tests</p><h2>Can tests be written backwards from the code?</h2>
<p>Yes, in three ways, from cheapest to best:</p>
<ol><li><b>Snapshot tests</b> (syrupy): run the pure function on a small sample and save the output as the expected answer. It pins today's behaviour so a refactor can't change it by accident. It does not say today's behaviour is right.</li>
<li><b>Property skeletons</b> (Hypothesis ghostwriter): generates test outlines from the function's signature; we add a helper that turns a schema into generated rows with nulls, duplicates and edge dates.</li>
<li><b>Drafted case tables</b>: Claude reads each untested pure function from the purity report and drafts a table of cases. A drafted test is kept only if mutation testing shows it catches deliberate bugs, so the model never decides on its own that code is tested.</li></ol>
<p>Pynguin, a research tool that generates unit tests automatically, is on trial; it is unlikely to do well with DataFrame code.</p></section>

<section id="where"><p class="eyebrow">Where it runs</p><h2>Laptop, container, CI: the same tests</h2>
{table(["Where", "What runs", "Needs"], [
        ("Laptop", "pre-commit on commit; pytest when you choose", "Java 17, Python, pinned pyspark"),
        ("Dev container", "The same, in a container with Java 17, Python 3.11 and the pinned libraries", "Docker or a cloud dev environment"),
        ("CI on GitHub or Azure DevOps", "pre-commit on the changed files, all tests, coverage on changed lines (80%)", "The template pipeline")])}
<p>Two settings matter everywhere: pin pyspark to the cluster's Spark version, and set <code>PYSPARK_PYTHON</code> to the test's own Python, always. On our machine a shell setting started workers on a different Python and every test failed. The templates are in the repo; they are written but not yet run in a pipeline.</p></section>"""
    qa = [("Can SCD type 2 logic be unit tested without a cluster?", "Yes. Write it as a pure function (history and batch in, new history out) and test it on a local Spark session with a few rows: new key, no change, change, two changes in one batch, duplicate row, late row, replay, change back. The MERGE that writes the result stays a thin shell."),
          ("How do I test that a PySpark job is idempotent?", "Apply the batch to the state, then apply the same batch to the result. The second result must equal the first. Run it on every test case, not just one."),
          ("How do I catch rows silently dropped by a join?", "Check that every input key appears in the output or in an explicit rejects set. An inner join on a lookup with a missing key fails this check; a left join with a rejects list passes."),
          ("Can I detect a cartesian join in a test without data?", "Yes. Build empty inputs from an empty RDD with the real schema, run the transform and read the physical plan for CartesianProduct or BroadcastNestedLoopJoin. Don't use limit(0): Spark folds empty inputs away and hides the problem.")]
    return "data-tests", "Unit testing SCD2, idempotency, duplicates, dropped records and cartesian joins in PySpark without a cluster, with a test kit, drafted tests, and CI.", body, qa


def clean_code():
    body = f"""<section id="plain"><p class="eyebrow">In plain words</p><h2>Early return beats nesting</h2>
<p>Each level of nesting is one more condition a reader must hold in their head. Returning early for the simple cases keeps the main path flat.</p>
{code('''# Nested: three levels, and the reader tracks every else
def discount(order):
    if order is not None:
        if order.total > 100:
            if order.customer.is_member:
                return 0.10
            else:
                return 0.05
        else:
            return 0
    else:
        return 0


# Early return: each rule is one line, and nothing is nested
def discount(order):
    if order is None or order.total <= 100:
        return 0
    if order.customer.is_member:
        return 0.10
    return 0.05''', "Checked on 2 Nov 2026: Ruff reports the else after return (RET505), and complexipy scores the nested version 9 and the early-return version 3.")}</section>

<section id="rules"><p class="eyebrow">Already built</p><h2>Ruff has the clean-code rules; switch them on</h2>
<p>Ruff is one fast tool that reimplements the main Python linters. You choose which rule sets to turn on.</p>
{table(["Clean-code habit", "Ruff rules", "Originally from"], [
        ("Exit early; no else after return", "RET505 to RET508, SIM102 (collapsible if), PLR1702 (too many nested blocks)", "flake8-return, flake8-simplify, pylint"),
        ("Small functions", "C901, PLR0911 (returns), PLR0912 (branches), PLR0913 (arguments), PLR0915 (statements)", "mccabe, pylint"),
        ("Simpler forms", "SIM (ternary, any/all, context managers), FURB, UP, PERF", "flake8-simplify, refurb, pyupgrade, perflint"),
        ("Likely bugs", "B (mutable default argument, loop variable captured late), E722 (bare except), TRY, BLE", "bugbear, tryceratops"),
        ("Dead weight", "ARG (unused arguments), ERA (commented-out code), F401 (unused imports); vulture finds dead functions", "flake8-unused-arguments, eradicate"),
        ("Names and docs", "N (PEP 8 naming), D (docstrings on public functions)", "pep8-naming, pydocstyle"),
        ("Readability score", "complexipy cognitive complexity, which punishes nesting", ""),
        ("SQL clean code", "SQLFluff: explicit join type, aliases, ambiguous columns, consistent case", "")])}
<p>A stricter option exists, wemake-python-styleguide, but it is noisy, so it is not the default. Clean-code findings start as warnings, and the safe ones are fixed automatically with <code>ruff check --fix</code>.</p></section>"""
    qa = [("Is there a linter that checks Python clean-code practices like early return?", "Yes. Ruff includes flake8-return (RET505: else after return), flake8-simplify (SIM102: collapsible if) and pylint's refactor rules (too many branches, arguments, returns and nested blocks)."),
          ("Ruff or pylint?", "Ruff for the default: it is much faster and includes most of pylint's useful rules. Add pylint only for a specific check Ruff lacks."),
          ("Should clean-code findings block a merge?", "Not at the start. Warn, fix the safe ones automatically, and tighten later. Blocking on style early makes teams switch the checks off.")]
    return "clean-code", "Clean-code linting for Python and SQL: early return instead of nested ifs, small functions, dead code, naming. Which Ruff rule sets to switch on.", body, qa


def security_and_cost():
    body = f"""<section id="security"><p class="eyebrow">Security</p><h2>Unsafe code, secrets and vulnerable libraries</h2>
{table(["Problem", "Example", "Tool", "Gate"], [
        ("SQL built from strings", "spark.sql(f\"... WHERE country = '{{country}}'\")", "Ruff S608; Opengrep rules", "block"),
        ("Unsafe calls", "eval, pickle.loads, SSL verification turned off, subprocess with shell=True", "Ruff S rules (from Bandit)", "block"),
        ("Secret printed to a log", "print(dbutils.secrets.get(...))", "Opengrep rule", "block"),
        ("Secret in the repo or its history", "a token, key or connection string", "gitleaks", "block"),
        ("Library with a known vulnerability", "an old requests or urllib3", "osv-scanner (pip-audit as fallback)", "block on high"),
        ("Unpinned libraries, no lockfile", "pyspark>=3", "the gap report", "warn"),
        ("Infrastructure misconfiguration", "open storage, no encryption in Terraform", "Checkov", "block")])}
{code('''# Unsafe: the value becomes part of the SQL text
spark.sql(f"SELECT * FROM orders WHERE country = '{country}'")

# Safe: a named parameter (Spark 3.4 and later), and only the columns needed
spark.sql("SELECT order_id, amount FROM orders WHERE country = :country", args={"country": country})''')}
<p>Opengrep is the open-source fork of Semgrep's engine, used here for our own pattern rules. Semgrep's ready-made registry rules have a licence that limits them to internal use, so we write our own.</p></section>

<section id="cost"><p class="eyebrow">Cost</p><h2>Cost problems you can see before running</h2>
{fig(sources_drawing(), "Four places to look. All of them are read without a cluster.")}
{table(["Where", "Examples", "Gate"], [
        ("Python code", "collect() or toPandas() without a limit, a Spark call inside a loop, a Python UDF where a built-in function exists, withColumn in a loop, count() to test for emptiness, cache with no unpersist", "warn, then block once baselined"),
        ("SQL text", "SELECT *, cross join, a function on a partition column, MERGE without a partition predicate, ORDER BY with no LIMIT, the same table scanned several times", "warn; cross join blocks"),
        ("Query plan on empty tables", "cartesian product, nested-loop join, Python UDF evaluation, a scan with no filter pushed down, too many shuffles", "cartesian blocks"),
        ("Job and cluster config", "no auto-stop, an always-on cluster for a scheduled job, no cost tags, no limit on workers, continuous mode where triggered is enough", "block")])}
<p>These cost rules already exist from our earlier work on cost analysis, built on sqlglot and Python's ast: about 35 SQL rules, 11 Python rules, plan rules and job-config rules. They plug into the bundle as the cost adapter, so nothing is rebuilt. Younger open-source PySpark linters from 2026 (pyspark-antipattern, SparkDoctor) are tried against the sample repo, and only rules they add are kept.</p></section>"""
    qa = [("How do I prevent SQL injection in spark.sql?", "Don't build SQL from f-strings. Use named parameters, spark.sql(query, args={...}), available since Spark 3.4. Ruff's S608 rule flags SQL built from strings."),
          ("Which tool finds secrets in a git repository?", "gitleaks scans files and git history for tokens, keys and connection strings. It is a single binary and runs in pre-commit and CI."),
          ("Can you find Spark cost problems without running the job?", "Many of them: costly code shapes in Python and SQL, a cartesian product or Python UDF in the plan from EXPLAIN on empty tables, and costly job or cluster settings. Skew and real volumes still need a run.")]
    return "security-and-cost", "Static checks for PySpark and Databricks SQL: SQL injection, unsafe calls, secrets, vulnerable libraries, and cost problems in code, SQL, plans and job config.", body, qa


def whats_missing():
    body = f"""<section id="plain"><p class="eyebrow">In plain words</p><h2>Point it at a repo; it lists the gaps</h2>
<p>Findings say what is wrong in the code that exists. The gap report says what <b>should exist but doesn't</b>: a test for a function, a check in CI, a lockfile, a coverage threshold. It is the first thing to run on an inherited repo.</p>
{code('''SETUP
  missing  pre-commit configuration          -> add .pre-commit-config.yaml (template provided)
  missing  SQL lint for 14 .sql files and 9 SQL notebook cells
  missing  coverage threshold in CI
  missing  dependency lockfile
  present  tests folder, CI workflow, bundle validated before deploy
SECURITY PRACTICES
  pinned dependencies: no    branch protection: yes    static analysis in CI: no
TESTS
  17 pure functions with no test (listed)    3 modules with no test file
  29 impure functions that could be pure (listed, with a hint each)''', "Illustrative report, not measured on a real repo.")}</section>

<section id="how"><p class="eyebrow">Built from</p><h2>Off the shelf, plus data-specific checks</h2>
{table(["Part", "Tool", "Verdict", "Why"], [
        ("Framework for 'is this repo set up right?' checks", "repo-review (BSD licence)", "Pursue", "Checks are small plugins; we write the data-repo ones"),
        ("Python project checks", "sp-repo-review (Scientific Python's checks)", "Borrow", "pyproject, pre-commit and Ruff checks reused as they are"),
        ("Security practices score", "OpenSSF Scorecard", "Pursue", "Pinned dependencies, branch protection, static analysis in CI, and more"),
        ("Per-function gaps", "the purity, coverage and complexity reports", "Build", "Joins the three into one list"),
        ("Data-repo checks", "our plugins", "Build", "SQL lint present, bundle validated, notebooks thin, contract files present, plan check wired")])}
<p>The report ends with one list in fix-first order: missing setup that blocks everything else, then complex untested functions, then pure untested ones.</p></section>"""
    qa = [("Is there a tool that reports what a Python repo is missing?", "repo-review is a framework for repo checks, and Scientific Python's sp-repo-review ships many checks on it. OpenSSF Scorecard scores security practices. Data-specific checks are added as plugins."),
          ("What should a data engineering repo have before code review?", "A tests folder with unit tests for the pure logic, pre-commit with Python and SQL lint, a lockfile, CI that runs tests with a coverage threshold on changed lines, secret scanning, and bundle validation before deploy.")]
    return "whats-missing", "A gap report for data engineering repos: missing tests, checks, lockfiles and CI setup, built on repo-review and OpenSSF Scorecard plus per-function gaps.", body, qa


def the_bundle():
    body = f"""<section id="status"><p class="eyebrow">Where it stands</p><h2>Status: the spec is written and the runner works</h2>
<p>The plan, the reuse check and the eight starting decisions are done, and so is the spec: 131 checks in 13 families, with ids that name no product, each linked to the data assurance obligations it gives evidence for. They cover Python, PySpark, notebooks, SQL, dbt, materialized views and metric views. 20 block from day one, 82 warn and 29 only report. For Databricks, 76 of the 131 are found by rules that already exist, 50 we write, and 5 tools are on trial. The full list is in the repo's <a href="{REPO}/blob/main/catalog/INDEX.md">catalog index</a>. Then a sample repo with planted problems and a hidden answer key, so catch rates are measured, not claimed. The repo is open: <a href="{REPO}">github.com/dataagentsai/shift-left-bundle</a>.</p>
{table(["Tier", "What", "Status"], [
        ("0", "Ground: reuse check, decisions, plan, open repo, this guide", "done"),
        ("1", "Spec v0.1: 90 checks in 12 families, purity lists, gate policy, Databricks binding, a linter for the catalog", "done"),
        ("1b", "Spec 0.2: notebooks, dbt, materialized views, metric views, clean code on 404 Ruff rules, an SCD2 example with a test kit, CI and container templates", "done"),
        ("2", "Proof material: a sample shop with 101 planted problems, 16 false-alarm traps and a hidden answer key. Ruff alone catches 17 of 101 with no false alarms; the rest is what the next tiers build", "done"),
        ("3", "One runner over eight open-source tools, findings as SARIF on the pull request, block or warn, baseline for existing code. First measured run: 34 of 101 planted problems caught, no false alarms, under 8 seconds", "done"),
        ("4", "Cost rules plugged in (our earlier cost-analysis rules, SparkDoctor after a trial of three young PySpark linters, our own materialized-view and job-config rules). Second measured run: 64 of 101 caught, still no false alarms", "done"),
        ("5", "What we build: purity report, test-time purity guard, empty-table plan check, metric view and dbt checks, test drafts, a health page and pull-request summary. Fifth measured run: 88 of 101 caught; with our own pattern rules for the last nine checks, the sixth run catches 97 of 101, still no false alarms", "done"),
        ("6", "A real repo: cut the noise, feed gaps back into the spec", "next"),
        ("7", "Teach and release: this guide kept current, a Claude skill, CI templates, version 0.1", "alongside"),
        ("8", "Azure binding", "later")])}</section>

<section id="design"><p class="eyebrow">Spec-driven</p><h2>Spec, bindings, adapters</h2>
<p>It follows the same shape as the other open specifications on this site. The <b>catalog</b> says what to check and why, and names no product. A <b>binding</b> per platform (Databricks first, then Azure) maps each check to a tool and its rule. The <b>runner</b> talks to every tool through one interface, so swapping a tool means writing one adapter, not changing the checks.</p>
{table(["Family", "Asks", "Starting gate"], [
        ("COST-CODE, COST-PLAN, COST-CONFIG", "Does the code, the plan or the job config waste money?", "warn; cartesian joins and config problems block"),
        ("SEC, SECRET, DEP", "Is it unsafe, leaking secrets, or using vulnerable libraries?", "block"),
        ("PURE, TEST", "Is the logic pure and tested, and do the tests catch bugs?", "report; coverage on changed lines blocks below 80%"),
        ("CPLX, CLEAN, STYLE", "Is it tangled, unclean or inconsistent?", "warn; safe fixes automatic"),
        ("SETUP", "What is the repo missing?", "report")])}
<p><b>Deterministic first:</b> every check is a tool or a script with a fixed answer. A language model is used only to explain a finding or draft a refactor, never to decide pass or fail.</p></section>

<section id="tools"><p class="eyebrow">Reuse</p><h2>The tools, with verdicts</h2>
{table(["Need", "Tool", "Verdict", "Why"], [
        ("Runner", "pre-commit", "Pursue", "Same configuration on the laptop and in CI"),
        ("Python lint, clean code, security", "Ruff", "Pursue", "One fast tool replaces flake8, isort, black, most of Bandit and many pylint rules"),
        ("Custom pattern rules", "Opengrep", "Pursue", "Open engine for our own rules"),
        ("SQL", "sqlglot, SQLFluff", "Pursue", "Syntax-tree rules and style"),
        ("Purity", "deal", "Borrow", "Generic side effects; the Spark part is ours"),
        ("Tests and coverage", "pytest, assertDataFrameEqual, coverage.py, diff-cover, Hypothesis, mutmut", "Pursue", "Standard"),
        ("Complexity", "Ruff C901, complexipy", "Pursue", "radon and wily are stale"),
        ("Architecture rule", "import-linter", "Pursue", "The core never imports the IO code"),
        ("Secrets, vulnerabilities, infrastructure", "gitleaks, osv-scanner, Checkov", "Pursue", "Standard and light"),
        ("Gap report", "repo-review, OpenSSF Scorecard", "Pursue", "Frameworks exist"),
        ("Showing findings", "SARIF on GitHub or Azure DevOps", "Pursue", "No server to run"),
        ("Young PySpark linters", "pyspark-antipattern, SparkDoctor", "Trial", "From 2026, one maintainer each; keep only what they add"),
        ("Heavy platforms", "SonarQube, MegaLinter, DefectDojo", "Drop", "A server or a multi-gigabyte image")])}</section>

<section id="sonar"><p class="eyebrow">A common question</p><h2>Why not SonarQube?</h2>
<p>SonarQube needs a server and a database, pull-request analysis is in its paid editions, and it knows nothing about Spark cost or Databricks. What it gives, rules, a dashboard and "clean as you code", comes lighter here: Ruff and Opengrep for rules, SARIF findings on the pull request for the dashboard, and diff-cover with a baseline for clean as you code. Because the output is SARIF, a team that already runs SonarQube can import the findings.</p></section>

<section id="git"><p class="eyebrow">Git</p><h2>How the repo is laid out, and how a team uses it</h2>
{code('''shift-left-bundle/
  .pre-commit-hooks.yaml     teams install the bundle from here (a few lines in their config)
  catalog/checks/*.yaml      the spec, versioned on its own
  bindings/databricks.yaml   bindings/azure.yaml   (the only place product names appear)
  rules/                     Opengrep, SQLFluff, Ruff and import-linter configuration
  src/shiftleft/             runner: interfaces, adapters, purity, empty-table harness, report
  plugins/repo_review/       the gap-report checks
  templates/                 pre-commit config, GitHub Actions and Azure DevOps pipelines
  examples/sample-project/   planted problems; tests/answer-key.yaml''')}
{fig(gates_drawing(), "A team's repo runs the fast checks on commit and the full set on the pull request.")}
<p>Short-lived branches merge into a protected main through pull requests, with the bundle's pull-request job as a required check. Teams pin a version tag of the bundle, so a new rule never breaks them by surprise.</p></section>"""
    qa = [("Do I need SonarQube for a PySpark project?", "No. Ruff, Opengrep, SQLFluff, gitleaks, pip-audit and coverage tools cover the same ground with no server, and SARIF output shows findings on the pull request. SonarQube also has no Spark cost rules."),
          ("What is spec-driven about this bundle?", "The checks are written once, with ids and reasons and no product names. Each platform gets a binding that maps checks to tools, so adding Azure or another platform is a new binding, not new checks."),
          ("Can I use it today?", "Yes, as a preview: `shiftleft scan . --stage pr`, `shiftleft purity .` and `shiftleft draft-tests .` work today, as does the pre-commit hook. Version 0.1 follows a run on a real repo. Follow the GitHub repo.")]
    return "the-bundle", "The shift-left bundle for PySpark and Databricks: spec, bindings and adapters, check families, tools with verdicts, why not SonarQube, git layout and status.", body, qa


FUNCS = [basics, how_software_solved_it, syntax_trees, pure_functions, tests_and_coverage, data_tests, clean_code, security_and_cost, whats_missing, the_bundle]


def render(slug, desc, body, qa):
    title = TITLE[slug]
    url = f"{SITE}{BASE}{slug}/"
    i = [p[0] for p in PAGES].index(slug)
    nxt = PAGES[i + 1] if i + 1 < len(PAGES) else None
    full = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › <a href="{BASE}">Shift left</a> › {E(SHORT[slug])}</p>
<p class="eyebrow" style="margin-top:22px">Shift left · page {i + 1} of {len(PAGES)}</p>
<h1>{E(title)}</h1>
<p class="lede">{E(desc)}</p>{siblings(slug)}
{body}
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{faq(qa)}</section>
<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2>
{f'<p><b>Next page:</b> {link(nxt[0], nxt[2])}</p>' if nxt else ''}
<p><a href="{BASE}">↑ All of shift left</a> · <a href="{REPO}">The repo on GitHub</a> · <a href="/learn/technical-anchor/project-review/">Data project review</a></p>
{siblings(slug)}</section>"""
    crumbs = [("Learn", f"{SITE}/learn/"), ("Shift left", f"{SITE}{BASE}"), (SHORT[slug], url)]
    return wb.page(title, R.short_desc(desc), url, full, CSS + R.ld(title, desc, url, qa, crumbs))


def hub():
    url = f"{SITE}{BASE}"
    cards = "".join(f'<a href="{BASE}{s}/"><span class="n">{i + 1}</span><b>{E(sh)}</b><span>{E(one)}</span></a>' for i, (s, sh, _, one) in enumerate(PAGES))
    qa = [("What is shift-left testing for data engineering?", "Catching problems in PySpark, Python and SQL code before it runs: lint, security and cost rules, unit tests on tiny DataFrames, a plan check on empty tables, and job-config rules, on commit and on the pull request."),
          ("Where should I start?", "Shift left explained, then pure functions, then tests and coverage. The bundle page shows the tools and where the work stands.")]
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › Shift left</p>
<p class="eyebrow" style="margin-top:22px">Data engineering · free guide · {len(PAGES)} short pages</p>
<h1>Shift left: fail fast on data code</h1>
<p class="lede">How to catch problems in PySpark, Python and Databricks SQL before the code runs: cost, security, vulnerable libraries, untested logic, tangled functions, and what a repo is missing. Built from open-source tools the software world already trusts, with no heavy servers.</p>

<section id="picture"><p class="eyebrow">The picture</p><h2>Find it on the left, where it is cheap</h2>
{fig(timeline(), "Shift-left checks live in the dashed box: no cluster, no data, seconds to minutes.")}
<p><b>The short answer:</b> make most of the logic pure functions (DataFrame in, DataFrame out) so it can be unit tested in seconds. Read every file as a syntax tree and run a short list of rules on commit. Run the full set, with coverage on changed lines, on the pull request. Block only what must never ship, and warn on the rest, because noise kills adoption.</p></section>

<section id="pages"><p class="eyebrow">The pages</p><h2>Read in order, or jump in</h2><div class="map">{cards}</div></section>

<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{faq(qa)}</section>
<section id="next"><p class="eyebrow">Related</p><h2>Where it connects</h2>
<p><a href="/learn/technical-anchor/project-review/">Data project review</a> checks a project's documents; this guide checks its code. The open repo is <a href="{REPO}">shift-left-bundle on GitHub</a>.</p></section>"""
    crumbs = [("Learn", f"{SITE}/learn/"), ("Shift left", url)]
    title = "Shift left: fail fast on data code"
    desc = "Shift-left checks for PySpark, Python and Databricks SQL: pure functions, unit tests and coverage, clean code, security, cost, and a gap report, from open-source tools."
    return wb.page(title, desc, url, body, CSS + R.ld(title, desc, url, qa, crumbs))


def main():
    out = ROOT / "learn" / "shift-left"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(hub())
    for fn in FUNCS:
        slug, desc, body, qa = fn()
        d = out / slug
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(render(slug, desc, body, qa))
    print("shift left ->", out, f"(hub + {len(FUNCS)} pages)")


if __name__ == "__main__":
    main()
