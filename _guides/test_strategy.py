"""Test strategy for a data platform, as practised: /learn/data-platform-architecture/test-strategy/.

    python3 _guides/test_strategy.py

The companion of test_architecture.py. That page is the design (nine kinds of test, cloud-neutral). This page is the
strategy as it runs on the reference build: seventeen kinds of test grouped by the question they answer, the six
steps a change climbs, what blocks a release, what is proven and what is not yet, then how each kind works.
Reuses the shell and helpers of dp_aws_databricks.py.
"""
import json
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
import dp_aws_databricks as D  # noqa: E402  (shell, CSS, drawing and table helpers)

C, wb = D.C, D.wb
rect, tx, arr, svg, table = D.rect, D.tx, D.arr, D.svg, D.table
SITE = wb.SITE
URL = f"{SITE}/learn/data-platform-architecture/test-strategy/"
BASE = "/learn/data-platform-architecture/"
UPDATED = "2026-11-15"

DONE, PART, TODO = "done", "partly", "not yet"


def st(state, note=""):
    cls = {DONE: "ok", PART: "part", TODO: "no"}[state]
    tail = f" {E(note)}" if note else ""
    return f'<span class="st {cls}">{E(state)}</span>{tail}'


# ------------------------------------------------------------------ drawing
def ladder():
    """Six steps a change climbs; each is slower and closer to real data than the one before."""
    steps = [
        ("1. Commit", ["Static checks on", "changed code"], "seconds", "#F4F4F2"),
        ("2. Pull request", ["Unit and contract", "tests, two engines,", "specs, infrastructure"], "about 3 minutes", "#E9EDF8"),
        ("3. Merge", ["Three-day simulated", "world: every layer", "equals known answers,", "all faults handled"], "about 3 minutes", "#E6F4EC"),
        ("4. Deploy to dev", ["Every generated job", "runs once on the real", "platform, then the", "world is checked there"], "about 15 minutes", "#FFF4D9"),
        ("5. Release", ["The change on copies", "of production tables,", "compared per window;", "a person approves"], "minutes + approval", "#FBE9DD"),
        ("6. Every run", ["Contract rules,", "quarantine, source", "against silver, row", "ledger, metrics,", "freshness, alerts"], "inside the load", "#F8E6EF"),
    ]
    b, w, gap, base = [], 162, 12, 300
    for i, (name, lines, cost, fill) in enumerate(steps):
        x, h = 10 + i * (w + gap), 122 + i * 28
        y = base - h
        b.append(rect(x, y, w, h, fill, r=10) + tx(x + 10, y + 26, name, 16, weight=700))
        for k, line in enumerate(lines):
            b.append(tx(x + 10, y + 50 + k * 19, line, 14))
        b.append(tx(x + 10, base - 10, cost, 13, fill="#555"))
        if i < 5:
            b.append(arr(x + w, y + 14, x + w + gap, y - 12))
    return svg(1056, base + 12, "".join(b),
               "Six rising steps: commit, pull request, merge, deploy to dev, release, and every production run. "
               "Each step runs slower tests that are closer to real data.")


# ------------------------------------------------------------------ data
PRINCIPLES = [
    ("Test against known answers", "A simulated company produces the source data and also knows the correct total at every layer for every day. The platform's output must equal those totals."),
    ("Plant every fault you claim to handle", "Duplicates, late files, renamed columns and mass deletes are put into the data on purpose. Each one must be caught at the layer that is supposed to catch it."),
    ("Compare versions on the same input", "A change runs beside the current version on copies of production tables. Any difference nobody declared blocks the release."),
    ("Production runs test themselves", "Contract rules, reconciliation and row counts run on every load, so a problem in real data is caught the same way as a planted one."),
    ("Every rule has a test or a written waiver", "A rule catalog lists what must be true of the platform. Coverage is counted, not assumed."),
]

QUESTIONS = [
    ("A. Is the code right?", "Static checks, unit tests, contract tests, engine conformance, spec and infrastructure tests", "Every commit and pull request"),
    ("B. Is the data right?", "World against known answers, planted faults, metric known answers, checks inside every run", "Every merge, every deploy, every production run"),
    ("C. Is this change safe?", "Release gate with a data comparison, version comparisons, integration run in dev", "Before every release to production"),
    ("D. Does it hold up in operation?", "Scenario tests, recovery tests, performance and scale, security and privacy, a long unattended run", "On a schedule and before go-live"),
]

# number, name, question it answers, runs at step, state, note on the state, what, how, left to do
KINDS = [
    ("A. Is the code right?", [
        (1, "Static checks", "Does the code break a known rule before it runs?", "1, 2", PART, "no secret scan yet",
         "Checks that read the code without running it.",
         "A linter for style and common mistakes, strict type checks on the cloud adapters, and the shift-left checks for PySpark and SQL anti-patterns. The shift-left scan compares with a baseline: old findings are listed there, and any new finding blocks the pull request.",
         "Add a secret scan. Widen strict typing from the cloud adapters to the whole core."),
        (2, "Unit tests", "Does each function give the right output for each listed case?", "2", DONE, "1,269 pass",
         "Each pure function is tested with a list of cases: a name, the input and the expected output.",
         "The cases sit in a table at the top of the test file and one test runs them all, so a new case is one new row. Logic is kept in pure functions so most of it is tested with no cluster and no database. The whole set runs in under a minute.",
         ""),
        (3, "Contract tests", "Does every adapter behind an interface behave the same?", "2", DONE, "",
         "Every outside system sits behind an interface (a port). A contract test is one table of cases per port that every implementation (adapter) must pass.",
         "The same cases run against the in-memory adapter, the real one, and a simulator of the cloud service. Examples: 64 cases for the metadata store on memory and PostgreSQL; 23 for the table store on Delta and Iceberg; 8 history cases that both silver engines pass. Moving to another cloud means writing new adapters and passing the same tables.",
         ""),
        (4, "Engine conformance", "Does the same logic give the same result on two engines?", "2", DONE, "143 cases",
         "The silver steps and the gold builds give identical results on Spark and on DuckDB.",
         "The same test tables run once per engine in separate processes, and hashed keys must be equal on both. The first run found 20 differences, 6 of them silent wrong values.",
         ""),
        (5, "Spec and infrastructure tests", "Are the manifest, contracts, rules and infrastructure valid?", "2", DONE, "",
         "The things that drive the platform are valid before anything runs.",
         "Every rule, capability and decision record is linted. Data contracts are validated against the open data contract standard. The generated jobs must equal what the manifest would generate now. Infrastructure code is formatted, validated and planned against mocked providers for each environment.",
         ""),
    ]),
    ("B. Is the data right?", [
        (6, "World against known answers", "Does every layer hold exactly what it should, every day?", "3, 4", DONE, "laptop and a free Databricks workspace",
         "The end-to-end test. A simulated company writes a day of data into mock source systems, the platform loads it, and each layer is compared with the totals the world knows are right.",
         "For each day: bronze row counts per dataset, silver measures per dataset (some per hour) and gold measures per table. A day passes only when every number is equal. It runs with every hop in one process, and also with ingestion, silver and gold as separate processes, the shape deployed jobs have.",
         "Run it in CI on every merge. Run it at full scale for 14 days."),
        (7, "Planted faults", "Is each failure caught at the right layer, with none silent?", "3, 4", DONE, "11 of 11",
         "Eleven kinds of fault are put into the world's data on set days. Each names the check that must catch it.",
         "After each day the run gives a verdict per fault: handled, flagged or missed. A missed fault fails the run. A compressed calendar puts all eleven on days 2 and 3, so a three-day run covers them. The faults: a file sent twice, a file sent late, rows deleted at the source, a column renamed, readings out of order, a full copy that is 40% short, a correction to past data, a new dealer whose record arrives after its orders, a change feed that drops rows, a stream replayed, and a promised date changed out of order. A 14-day fixture also checks that nothing fires on a clean day.",
         ""),
        (8, "Metric known answers", "Is the business number the same in the metric, gold and the world?", "4, 6", DONE, "8 of 8",
         "The number a business user sees equals gold and equals the world's truth.",
         "After each run the certified metrics are recreated and asked fixed questions, for example order lines in November. Each answer is compared with gold and with the world. The plain-language question interface is checked the same way: its answer must equal the metric.",
         ""),
        (9, "Checks inside every run", "Is today's real load complete, valid and reconciled?", "6", DONE, "",
         "Tests that run on real data in production, as part of the load.",
         "Contract rules by severity: a broken critical rule holds the whole batch, a major one sends the row to quarantine, a minor one flags it. A second copy of a delivery is refused, and a full copy that would delete too much is held. The live source is compared with silver every day, naming the exact missing keys and the hop that lost them. In gold, rows in must equal rows out at every join, and the join that changes the count is named. Every check writes a step in the run log, which feeds the dashboards and the alerts.",
         ""),
    ]),
    ("C. Is this change safe?", [
        (10, "Release gate with data comparison", "Does the change alter any number nobody declared?", "5", PART, "built; not yet run against a production environment",
         "The data form of A/B testing. The new version and the current version run on the same data, and the outputs are compared.",
         "Each production table the change touches is shallow-cloned, which copies only the table's file list and so costs almost nothing. The change runs against the clones. Row counts, measure totals and key sets are compared with production, in total and per window, for example per day. A difference blocks unless the change declared it and someone wrote the explanation. The clones are dropped whatever happens.",
         "Run it from CI against a real production environment. Today it blocks two planted bad changes in tests."),
        (11, "Version comparisons", "Do two ways of doing the same job agree?", "2, 3", PART, "four built; format benchmark not built",
         "Where the platform offers two ways to do one job, both must agree.",
         "Spark against DuckDB. The job silver engine against the declarative one: equal rows on six datasets. Delta against Iceberg: the same 23 cases. One process against separate processes: every layer equal, with the same fault verdicts.",
         "A format benchmark: Iceberg, Delta and Hudi on the same world, measured for speed and cost."),
        (12, "Integration run in dev", "Does every deployed job run once and pass its checks?", "4", TODO, "written; waits for a paid cloud workspace",
         "After a deploy to dev, one world day goes through cloud storage and every generated job runs once. Any failed check fails the pipeline.",
         "The deploy pipeline calls it straight after the deploy, so a job that deploys but does not run is caught the same day.",
         "Run it. It needs the job generator updated for the current engine and a cloud account."),
    ]),
    ("D. Does it hold up in operation?", [
        (13, "Scenario tests", "Does the right alert fire once, and none on clean days?", "2", DONE, "laptop",
         "Eleven written stories of something going wrong in operation, each with the alert and the state expected afterwards.",
         "Each scenario is a small file: the situation, the fault, and what must be true after. One engine plays it against the platform with a simulated clock. Noise rules are tested too: one alert per incident, none on clean days, and snoozes expire.",
         "Send alerts to a live channel and play the scenarios against the deployed platform."),
        (14, "Recovery tests", "Can a bad load be withdrawn, rerun and rebuilt with nothing changed?", "2, 3", PART, "withdraw not yet proven on the real platform",
         "Proof that the platform can get back from a bad state.",
         "Loading the same day twice adds no rows and changes no window. Withdrawing a batch voids it, rebuilds silver from bronze, and recomputes gold, replacing only the changed windows and logging each as a restatement. After old bronze batches are removed, silver rebuilt from what is left has the same current rows. A second run on a table already being written skips with a reason. A past window rebuilt from its run log equals what was published.",
         "Prove the withdraw path on the real platform."),
        (15, "Performance and scale", "Does it finish in time at full volume?", "scheduled", TODO, "",
         "It finishes in time at real volume.",
         "Every hop stamps its time, and a report gives the delay per hop and names any breach. One day at one tenth scale takes about 5.8 minutes against a target of 6.",
         "Full scale for 14 days. Hop times and gold-ready-by-morning measured on the real platform. Cost per daily load, which needs a billed workspace."),
        (16, "Security and privacy", "Are secrets, personal data and access kept as declared?", "2, 4", PART, "scan and access check not running",
         "Secrets, personal data and access stay as declared.",
         "Error messages are redacted before they reach the run log. Personal values are replaced by tokens at landing. Column masks and grants are generated from one access model, with a check that compares the model with what the catalog holds.",
         "A scan of every layer for clear personal values, with planted ones to prove the scan works. A secret scan in CI. The access check on a workspace with account-level groups. Right to be forgotten."),
        (17, "Long unattended run", "Does it stay right for 30 days with nobody watching?", "before go-live", TODO, "",
         "Thirty days on a schedule with nobody watching, and at the end the dashboard equals the world.",
         "It comes last because it needs everything else in place: deployed jobs, live alerts and a billed workspace.",
         ""),
    ]),
]

GATES = [
    ("Pull request", "Any static check, unit, contract, conformance, spec or infrastructure test fails; a new shift-left finding appears; the generated jobs are out of date", "Nobody. A shift-left exception needs a written reason on the line"),
    ("Merge", "The three-day world differs from the known answers at any layer, or a planted fault is not handled", "Nobody"),
    ("Deploy to dev", "A generated job fails its checks on the real platform", "Nobody"),
    ("Release to production", "The change differs from production in a measure, a key set or a window, and the difference is not declared and explained; or the result misses the known answers beyond the agreed tolerance", "The data owner, by writing the explanation. The release also needs a named reviewer's approval"),
    ("Production run", "A critical contract rule is broken (the batch is held and nothing is written); a full copy would delete more than the allowed share; a delivery arrives twice", "The data owner, through a recorded rerun or correction plan"),
]

GAPS = [
    ("1", "Integration run in dev: every generated job once, checks must pass", "It proves the deployed jobs work, not only the proof run"),
    ("2", "The three-day world in CI on every merge, in both run modes", "Today it is run by hand"),
    ("3", "Both silver engines in CI", "Only the job engine runs there; the declarative engine is checked by hand"),
    ("4", "Release gate run from CI against a production environment", "The gate blocks planted bad changes, but only in tests"),
    ("5", "Secret scan in CI", "Redaction is tested, but nothing scans commits for secrets"),
    ("6", "Personal-data scan after every run", "Tokens are applied at landing, but no scan proves that no clear value got through"),
    ("7", "Hop times and gold-ready-by-morning measured on the real platform", "Timeliness is measured on the laptop only"),
    ("8", "Full-scale run, 14 days", "The laptop ran out of memory at full scale"),
    ("9", "Access check against the catalog", "Needs a workspace with account-level groups"),
    ("10", "Rule coverage from 47 to 89", "42 rules have no named test or waiver"),
    ("11", "Table format benchmark", "The format is chosen by decision, not by measurement"),
    ("12", "30 days unattended", "The last proof before calling it production-ready"),
]

DATA = [
    ("Small case tables written in the test file", "Unit, contract and conformance tests", "The reader sees the input and the expected output together"),
    ("The simulated world, with a fixed seed", "World, fault, metric, recovery and performance tests", "The same run gives the same data every time, and the world knows the right answer at every layer"),
    ("Shallow clones of production tables", "The release gate", "Real data and real volume, with no copy and no risk to production"),
    ("Real production data", "Checks inside every run", "Problems that no simulator thought of"),
]

ENVS = [
    ("Laptop", "Kinds 1 to 7, 11, 13 and 14: three days at one tenth scale, on Spark or DuckDB", DONE, ""),
    ("CI", "Kinds 1 to 5 on every pull request and push", DONE, "the world run is not in CI yet"),
    ("Dev on the real platform", "Kinds 6 to 9 through the proof run; kind 12 after each deploy", PART, "a free workspace stands in; kind 12 not running"),
    ("Production", "Kind 9 in every run; kind 10 before every release", TODO, "not deployed"),
]

NEW_DATASET = [
    ("From the data contract", "Column, type and row rules run in every load, with quarantine by severity"),
    ("From the manifest entry", "Duplicate-delivery refusal, the mass-delete guard for full copies, freshness, and the live source comparison for database sources"),
    ("From the gold definition", "The row ledger at each join, completeness per window, and the per-window comparison at the release gate"),
    ("What the author adds", "The dataset in the simulated world with its known answers, and a planted fault if it has a failure mode the existing eleven do not cover"),
]

WORDS = [
    ("Known answers", "The correct totals the simulated world works out for itself at every layer, used to judge the platform's output. Often called the oracle."),
    ("Table-driven test", "One test that runs a list of cases, each a name, an input and an expected output."),
    ("Port and adapter", "A port is the interface the platform's logic talks to. An adapter is one implementation of it, for example PostgreSQL or object storage."),
    ("Shallow clone", "A copy of a table that shares the original's data files, so it is quick and nearly free."),
    ("Window", "The slice of a table a run rebuilds, usually one business day."),
    ("Restatement", "A logged change to a number that was already published."),
    ("Hop", "One move of data between layers: landing to bronze, bronze to silver, silver to gold."),
    ("Shift left", "Catching a problem earlier, at commit or pull request, instead of in production."),
]

FAQ = [
    ("How do you do A/B testing on a data platform?",
     "Not in the classic sense of splitting live users between two versions, because a pipeline has no user behaviour to measure. The equivalent is to run the new version and the current version on the same data and compare the outputs. That is the release gate: the change runs on shallow clones of production tables, and any undeclared difference in a measure, a key set or a window blocks the release. True A/B testing belongs to user-facing AI, where two versions answer real questions and the answers are scored."),
    ("How is this page different from the test architecture page?",
     "The test architecture page is the design: nine kinds of test and why each exists, with no platform named. This page is the strategy as it is practised on a reference build: seventeen kinds grouped by the question they answer, when each runs, what blocks a release, and what is proven so far."),
    ("Why simulate a company instead of using sample data?",
     "Sample data has no right answer attached. A simulated company with a fixed seed produces the same data every time and also knows the correct total at every layer, so the test is a comparison of numbers and not a judgement."),
    ("Which test would you add first to an existing platform?",
     "The checks inside every run: contract rules with quarantine, and a daily comparison of the live source with silver. They need no simulator and they catch real problems from the first day."),
    ("What does a new dataset need before it can go live?",
     "Its contract and manifest entry give it most of its tests. The author adds the dataset to the simulated world with its known answers, and a planted fault if it has a failure mode the existing ones do not cover."),
]


def kinds_table():
    rows = []
    for group, items in KINDS:
        rows.append(("", f"<b>{E(group)}</b>", "", "", ""))
        for n, name, q, step, state, note, *_ in items:
            rows.append((str(n), f'<a href="#k{n}">{E(name)}</a>', E(q), E(step), st(state, note)))
    return table(["#", "Kind", "The question it answers", "Runs at step", "State on the reference build"], rows, raw=(0, 1, 2, 3, 4))


def how_cards():
    out = []
    for group, items in KINDS:
        out.append(f"<h3>{E(group)}</h3>")
        for n, name, _q, _step, state, note, what, how, left in items:
            left_p = f"<p><b>Left to do.</b> {E(left)}</p>" if left else ""
            out.append(f'<div class="kcard" id="k{n}"><h4>{n}. {E(name)} {st(state, note)}</h4>'
                       f"<p><b>What.</b> {E(what)}</p><p><b>How.</b> {E(how)}</p>{left_p}</div>")
    return "".join(out)


def page():
    principles = "".join(f"<p><b>{E(a)}.</b> {E(b)}</p>" for a, b in PRINCIPLES)
    q_t = table(["Question", "Test kinds that answer it", "When"], QUESTIONS)
    gates_t = table(["Gate", "Blocks when", "Who can override"], GATES)
    gaps_t = table(["#", "Not proven yet", "Why it matters"], GAPS)
    data_t = table(["Source of test data", "Used by", "Why"], DATA)
    envs_t = table(["Environment", "What runs there", "State"], [(a, b, st(s, n)) for a, b, s, n in ENVS], raw=(2,))
    new_t = table(["Where the tests come from", "What the dataset gets"], NEW_DATASET)
    words_t = table(["Word", "Meaning"], WORDS)
    faq = C.faq(FAQ)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › <a href="{BASE}">Data platform architecture</a> › Test strategy</p>
<p class="eyebrow" style="margin-top:22px">Data platform architecture · testing</p>
<h1>Test strategy for a data platform</h1>
<p class="lede">What we test, when each test runs, and what blocks a release: seventeen kinds of test on a reference build, with what is proven so far and how each one works.</p>
<div class="sib"><a href="{BASE}">↑ Data platform architecture</a><a href="{BASE}testing/">Test architecture (the design)</a><a href="/learn/shift-left/">Shift left</a><a href="/learn/datatwin/">DataTwin</a></div>
<nav class="toc"><b>On this page</b><ol>
<li><a href="#minute">The strategy on one page</a></li><li><a href="#ladder">When each test runs</a></li><li><a href="#kinds">Seventeen kinds of test</a></li>
<li><a href="#gates">What blocks a release</a></li><li><a href="#gaps">What is not proven yet</a></li><li><a href="#how">How each kind works</a></li>
<li><a href="#data">Test data</a></li><li><a href="#envs">Environments</a></li><li><a href="#new">Adding a dataset</a></li>
<li><a href="#words">Words used</a></li><li><a href="#faq">Questions</a></li></ol></nav>

<section id="minute"><p class="eyebrow">Part one · crisp</p><h2>The strategy on one page</h2>
<div class="answer">
<p><b>Aim.</b> A wrong number never reaches a dashboard without someone being told, and a bad change never reaches production. Tests run before the merge, at release, and inside every production run.</p>
</div>
<h3>Five principles</h3>
{principles}
<h3>Four questions the tests answer</h3>
{q_t}
<p>The <a href="{BASE}testing/">test architecture page</a> gives the design behind this: why logic lives in pure functions, and the nine kinds of test in general terms. This page shows the same ideas running on one build.</p></section>

<section id="ladder"><p class="eyebrow">When each test runs</p><h2>Six steps a change climbs</h2>
<p>Each step is slower and closer to real data than the one before, so cheap tests catch most problems first.</p>
<figure class="diagram">{ladder()}<figcaption>On the reference build, steps 1 to 3 run today. Steps 4 and 5 are written and wait for a paid cloud workspace. Step 6 runs inside every proof run.</figcaption></figure></section>

<section id="kinds"><p class="eyebrow">The test kinds</p><h2>Seventeen kinds of test, by the question they answer</h2>
{kinds_table()}
<p><b>Across all of them: rule coverage.</b> The rule catalog holds 89 rules. At the last count 47 were named in code or tests. The target is 89 of 89, each with a passing test or a written waiver.</p></section>

<section id="gates"><p class="eyebrow">Gates</p><h2>What blocks a release</h2>
{gates_t}</section>

<section id="gaps"><p class="eyebrow">Honest state</p><h2>What is not proven yet, in the order we would close it</h2>
{gaps_t}</section>

<section id="how"><p class="eyebrow">Part two · how</p><h2>How each kind works</h2>
{how_cards()}</section>

<section id="data"><p class="eyebrow">Test data</p><h2>Where the test data comes from</h2>
{data_t}
<p>The simulated world runs at any scale: one tenth for the daily loop on a laptop, full scale on the real platform. Personal data in it is made up, so no real personal data is used in a test.</p></section>

<section id="envs"><p class="eyebrow">Environments</p><h2>What runs where</h2>
{envs_t}</section>

<section id="new"><p class="eyebrow">Adding a dataset</p><h2>What a new dataset gets without anyone writing a test</h2>
<p>Most tests come from the dataset's entry in the manifest and its data contract, so adding a dataset adds its tests.</p>
{new_t}</section>

<section id="words"><p class="eyebrow">Words used</p><h2>Words used on this page</h2>
{words_t}</section>

<section id="faq"><p class="eyebrow">Questions</p><h2>Questions people ask</h2>{faq}</section>

<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2>
<p><b>The design behind it:</b> <a href="{BASE}testing/">Test architecture for a data platform</a>.</p>
<p><b>The static checks:</b> <a href="/learn/shift-left/">Shift left: fail fast on data code</a>. <b>The simulated company:</b> <a href="/learn/datatwin/">DataTwin, explained</a>.</p>
<p><b>The faults to test for:</b> <a href="/learn/data-platform-sim/problems/">the Problem Lab</a>, nineteen data problems run for real.</p></section>"""
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": "Test strategy for a data platform",
           "description": "Seventeen kinds of test for a data platform grouped by four questions, the six steps a change climbs from commit to production, what blocks a release, what is proven so far on a reference build, and how each kind works.",
           "url": URL, "inLanguage": "en", "isAccessibleForFree": True, "dateModified": UPDATED,
           "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
           "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]
    css = ("<style>.st{display:inline-block;font-size:12.5px;font-weight:600;padding:1px 9px;border-radius:10px;border:1.5px solid #1d2330;white-space:nowrap}"
           ".st.ok{background:#E6F4EC}.st.part{background:#FFF4D9}.st.no{background:#F8E6EF}"
           ".kcard{border:1.5px solid #1d2330;border-radius:12px;padding:12px 16px;margin:12px 0}.kcard h4{margin:0 0 8px;font-size:16.5px}.kcard p{margin:0 0 8px}</style>")
    head = D.CSS + css + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    desc = "Test strategy for a data platform: seventeen kinds of test by four questions, six steps from commit to production, what blocks a release, what is proven, and how each works."
    return wb.page("Test strategy for a data platform", desc, URL, body, head)


def main():
    out = ROOT / "learn" / "data-platform-architecture" / "test-strategy"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("test strategy ->", out)


if __name__ == "__main__":
    main()
