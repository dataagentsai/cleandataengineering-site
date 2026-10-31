"""DataTwin, explained: the guide at /learn/datatwin/.

    python3 _guides/datatwin.py

The data-engineering sibling of /learn/agenttwin/, same three parts:
  Part 1  The explainer: plain words, DataTwin vs a digital twin (and vs AgentTwin),
          input / processing / output.
  Part 2  How it works: setup, per-platform work, where a platform's tests come from,
          pretend sources, data and the truth, a step-through simulator on a tiny
          platform, then a bigger one, coverage, sufficiency.
  Part 3  As a product: built vs still to build, is 100% achievable, who else builds
          this, how it differs, our limits, the open-source tools.

Facts come from ~/clean-data-engineering/PLAN.html (specs, rules R1-R9, the planted-incident
table, phases), ~/agenttwin (the core DataTwin extends), ~/DataPlatformSuite (Ops Gate) and
the DataTwin Studio recordings under _sim/, as of 31 Oct 2026. DataTwin as a testing tool is
designed, not built; the page says so. The simulator's runs are illustrative.
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "_paths"))
spec = importlib.util.spec_from_file_location("writing_build", ROOT / "_writing" / "build.py")
wb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wb)
_at = importlib.util.spec_from_file_location("agenttwin_guide", ROOT / "_guides" / "agenttwin.py")
at = importlib.util.module_from_spec(_at)
_at.loader.exec_module(at)
from diagrams import FILL, arrow, box, svg  # noqa: E402

E = wb.E
SITE = wb.SITE
URL = f"{SITE}/learn/datatwin/"
INK = at.INK
T, panel, line = at.T, at.panel, at.line

CSS = at.CSS.replace("</style>", """
  .status { border:var(--line); border-radius:var(--wob); padding:12px 18px; background:var(--butter-wash); margin:18px 0; font-size:15.5px; }
  .sim .log li.source { background:var(--rose-wash); } .sim .log li.platform { background:var(--peri-wash, #F1F4FB); }
  .sim .log li.incident { background:#F3F3F1; } .sim .log li.check { background:var(--lilac-wash, #F6F2FC); }
  .sim .log li.ask { background:var(--mint-wash, #E3F4EA); }
  .sim td.lbl { font-weight:600; width:42%; } .sim tr.truth td { background:var(--mint-wash, #E3F4EA); }
</style>""")


# ---------------------------------------------------------------- diagrams
def d_twins():
    b = panel(10, 10, 530, 400, "peri")
    b += T(275, 44, "A digital twin", 25, fill=INK)
    b += box(35, 70, 210, 92, "The real thing", "a jet engine,\na factory line", "grey")
    b += arrow(247, 104, 313, 104, "sensor data")
    b += box(315, 70, 205, 92, "Its virtual copy", "mirrors the thing,\nminute by minute", "white")
    b += box(115, 225, 320, 78, "Predictions, what-ifs", "“service it in 40 hours”", "butter")
    b += line(417, 164, 360, 223) + line(190, 223, 140, 164)
    b += T(130, 200, "act on the real thing", 13, "middle")
    b += T(275, 345, "It copies the THING itself,", 17, fill=INK)
    b += T(275, 368, "to watch it and predict it, for its whole life.", 15)

    b += T(560, 215, "vs", 30, fill=INK)

    b += panel(580, 10, 530, 400, "mint")
    b += T(845, 44, "DataTwin", 25, fill=INK)
    b += panel(598, 62, 494, 214, "white")
    b += T(845, 82, "the simulated world: the twin", 14)
    b += box(612, 96, 158, 58, "A pretend shop", "sells, refunds, on a clock", "rose")
    b += box(920, 96, 158, 58, "Its source systems", "database, files, API", "butter")
    b += box(612, 200, 158, 58, "Incident calendar", "renames, late days", "lilac")
    b += box(920, 200, 158, 58, "Faults + time", "dark source, slow API", "grey")
    b += f'<rect x="785" y="134" width="120" height="86" rx="14" fill="#fff" stroke="{INK}" stroke-width="2.6"/>'
    b += T(845, 168, "Real data", 18, fill=INK) + T(845, 189, "platform", 18, fill=INK) + T(845, 208, "unchanged", 13)
    b += line(772, 128, 785, 150) + line(918, 128, 905, 150)
    b += line(772, 226, 785, 206) + line(918, 226, 905, 206)
    b += box(660, 290, 370, 46, "Each day: dashboard = world's truth?", "", "butter")
    b += line(845, 277, 845, 288)
    b += T(845, 365, "It copies the WORLD AROUND the platform,", 17, fill=INK)
    b += T(845, 388, "to break it on purpose before real data does.", 15)
    return (svg(1120, 420, b, "Left: a digital twin copies a real machine from sensor data to predict it. Right: DataTwin keeps the data platform real and copies the business and source systems that feed it, then checks the dashboard against the world's truth."),
            "Same word, opposite direction. A digital twin copies the thing. DataTwin keeps the thing (your data platform) real and copies the shop and source systems that feed it.")


def d_ipo():
    ins = [("Platform manifest", "from the platform team:\nsources, contracts, metrics", "peri"),
           ("World + incidents", "from the tester:\nthe shop, its clock, what breaks", "butter"),
           ("Owed checks", "from the Data Assurance\nCatalog, by pipeline kind", "rose"),
           ("Binding", "which stack runs it:\ndatabricks.yaml first", "grey")]
    outs = [("A verdict per simulated day", "dashboard, conversation UI\nand world agree, or not", "mint"),
            ("Incident records", "caught by what, how fast,\nfixed how, did it hold", "white"),
            ("Coverage map", "every incident kind planted;\nevery owed check proved", "butter"),
            ("Evidence page", "the page a client reads,\ngenerated, never hand-written", "rose")]
    b = T(155, 16, "INPUTS: who gives what", 14, fill=INK) + T(965, 16, "OUTPUTS", 14, fill=INK)
    for i, (t, s, f) in enumerate(ins):
        y = 26 + i * 92
        b += box(10, y, 290, 82, t, s, f) + arrow(302, y + 41, 356, y + 41)
    b += f'<rect x="360" y="26" width="400" height="358" rx="18" fill="{FILL["lilac"]}" stroke="{INK}" stroke-width="1.6"/>'
    b += T(560, 58, "DataTwin runs each simulated day", 21, fill=INK)
    steps = ["1  the shop trades; the world keeps the truth", "2  sources emit rows, files, change feed",
             "3  plant the day's incidents; move the clock", "4  the real platform runs, unchanged",
             "5  detectors fire; fixes go through gates", "6  record run log, lineage, cost",
             "7  compare every number with the world"]
    for i, s in enumerate(steps):
        b += T(384, 100 + i * 39, s, 16, "start", INK)
    for i, (t, s, f) in enumerate(outs):
        y = 26 + i * 92
        b += arrow(762, y + 41, 816, y + 41) + box(820, y, 290, 82, t, s, f)
    return (svg(1120, 392, b, "Inputs: platform manifest, world and incidents, owed checks, binding. DataTwin runs seven steps per simulated day. Outputs: a verdict per day, incident records, a coverage map and an evidence page."),
            "Input, processing, output. Four sources feed it; seven steps run for every simulated day; four things come out. This is the design; see Part 3 for what is built.")


def d_sources():
    srcs = [("The platform manifest", "every source, table,\ncontract rule, metric, SLO", "peri"),
            ("Data Assurance Catalog", "checks owed by each\npipeline kind (planned)", "rose"),
            ("Data Platform Catalog", "22 concerns, on by\ndefault; off needs a waiver", "lilac"),
            ("The Problem Lab", "19 problems every\nplatform meets", "grey"),
            ("Production incidents", "a miss in the wild\nbecomes a planted incident", "butter")]
    b = ""
    for i, (t, s, f) in enumerate(srcs):
        y = 10 + i * 78
        b += box(10, y, 270, 68, t, s, f) + arrow(282, y + 34, 418, 200)
    b += box(420, 140, 270, 120, "The owed list", "every incident kind\nand check this platform\nmust survive, with an id", "white")
    b += arrow(692, 200, 760, 200, "each one needs")
    b += box(762, 60, 348, 80, "a planted incident that fired", "and the check that it held (rule R9)", "mint")
    b += box(762, 160, 348, 80, "or a waiver", "with a reason, an approver, an expiry (R5)", "butter")
    b += box(762, 260, 348, 80, "or 'not applicable'", "e.g. no streaming source, written down", "white")
    b += T(936, 375, "anything else is a detector nobody has seen fire: a named gap", 15, fill=INK)
    return (svg(1120, 400, b, "Five sources produce the owed list for a platform. Each item needs a planted incident that fired and held, a waiver, or a written not-applicable. Anything else is a named gap."),
            "How a given platform's test list is decided: by what it declares and what its pipeline kinds owe, not by taste.")


def d_truth():
    b = box(10, 30, 250, 110, "The world", "generated every order,\nso it KNOWS day 3\nsold ₹240,000", "mint")
    b += arrow(262, 85, 340, 85, "rows only")
    b += box(342, 30, 430, 110, "Your platform (real)", "landing, bronze, silver, gold,\nsemantic layer, dashboard,\nconversation UI", "peri")
    b += arrow(774, 85, 850, 85)
    b += box(852, 30, 258, 110, "What it shows", "tile: ₹480,000\n“sales were ₹480,000”", "rose")
    b += f'<path d="M135 142 C 135 215, 980 215, 980 142" fill="none" stroke="{INK}" stroke-width="1.6" stroke-dasharray="6 5"/>'
    b += T(558, 232, "the check: does what it shows equal what the world knows?", 16, fill=INK)
    b += T(558, 256, "₹480,000 ≠ ₹240,000, so the day fails, even though every job finished green", 14)
    return (svg(1120, 270, b, "The world generated the data, so it knows the true total. The platform only gets rows. The check compares the dashboard with the world's truth."),
            "Why a simulated world fixes the oracle problem for data: the right answer is known because the world made the data.")


def d_oss():
    b = f'<rect x="400" y="130" width="320" height="150" rx="18" fill="{FILL["peri"]}" stroke="{INK}" stroke-width="2.4"/>'
    b += T(560, 160, "DataTwin builds only", 19, fill=INK)
    for i, s in enumerate(["the world format (DWD, extends AWD)", "a shop that keeps the truth", "the incident calendar + R9 join", "checks: dashboard vs world"]):
        b += T(560, 188 + i * 22, s, 15, fill=INK)
    top = [("Spark + Delta (OSS)", "the engine, run for real", "mint"), ("PyDeequ", "data quality engine", "mint"),
           ("AgentTwin core", "clock, faults, modes, runner", "mint"), ("pytest, Hypothesis", "runner, edge values", "mint")]
    bot = [("Faker, then SDV", "rows, then realistic rows", "butter"), ("time-machine, SimPy", "the world's clock", "butter"),
           ("Toxiproxy, Testcontainers", "faults, real stores", "butter"), ("OpenLineage, Great Expectations", "lineage, 2nd DQ engine", "butter")]
    for i, (t, s, f) in enumerate(top):
        x = 10 + i * 278
        b += box(x, 10, 262, 70, t, s, f) + line(x + 131, 82, 560 + (i - 1.5) * 70, 128)
    for i, (t, s, f) in enumerate(bot):
        x = 10 + i * 278
        b += box(x, 330, 262, 70, t, s, f) + line(x + 131, 328, 560 + (i - 1.5) * 70, 282)
    b += T(560, 424, "green = in use today (in the Studio or AgentTwin)   ·   yellow = planned, behind a port", 14, fill=INK)
    return (svg(1120, 435, b, "DataTwin's own core in the middle, with open-source tools around it behind ports. Green are in use today, yellow planned."),
            "An assembler, like AgentTwin. Each tool sits behind a port, so it can be swapped.")


# ---------------------------------------------------------------- simulator data
ROWS = [("world", "The world (the truth)"), ("landed", "Landing files"), ("bronze", "Bronze"),
        ("silver", "Silver"), ("quar", "Quarantine"), ("gold", "Gold total"),
        ("tile", "Dashboard tile"), ("ask", "Conversation UI answer"), ("alerts", "Alerts")]

SCEN = [
    {"id": "s1", "title": "1 · A day arrives twice", "focus": "agree",
     "story": "Day 3: the shop sold 120 orders worth ₹240,000. An hour later the source sends the same file again, a common upstream retry.",
     "init": {"world": "120 orders · ₹240,000"},
     "yaml": """incident: a day arrives twice
world: worlds/shop.yaml
day: 3
plant:
  - {kind: duplicate_batch, source: orders, file: day3.csv, delay: 1h}
expect:
  - {metric: daily_sales, day: 3, equals: world}
  - {reconcile: orders, landed_keys: silver + quarantine}
discharges: [X6, X15]""",
     "good": [["source", "the shop's system writes day3.csv: 120 orders", {"landed": "120 rows (1 file)"}],
              ["incident", "planted: the same day3.csv arrives again an hour later", {"landed": "240 rows (2 files)"}],
              ["platform", "the lander copies both into bronze, tagged with batch and file name", {"bronze": "240 rows · 2 batches"}],
              ["platform", "silver replaces exactly day 3, keeping the latest row per order id", {"silver": "120 rows", "quar": "0"}],
              ["platform", "gold sums day 3; the dashboard refreshes", {"gold": "₹240,000", "tile": "₹240,000"}],
              ["check", "reconciliation: 120 unique keys landed = 120 in silver + 0 quarantined", {"alerts": "notice: duplicate file, absorbed"}],
              ["ask", "someone asks the conversation UI: what were sales on day 3?", {"ask": "₹240,000"}]],
     "good_j": {"agree": [1, "tile and answer say ₹240,000; so does the world"], "caught": [1, "the duplicate file was noticed and absorbed"],
                "held": [1, "no rule changed"], "acct": [1, "every landed key is in silver or quarantine, once"]},
     "bad": [["source", "the shop's system writes day3.csv: 120 orders", {"landed": "120 rows (1 file)"}],
             ["incident", "planted: the same day3.csv arrives again an hour later", {"landed": "240 rows (2 files)"}],
             ["platform", "bronze takes both files", {"bronze": "240 rows · 2 batches"}],
             ["platform", "silver appends whatever bronze got today", {"silver": "240 rows", "quar": "0"}],
             ["platform", "gold sums day 3; every job finishes green", {"gold": "₹480,000", "tile": "₹480,000", "alerts": "none"}],
             ["ask", "someone asks the conversation UI: what were sales on day 3?", {"ask": "₹480,000"}]],
     "bad_j": {"agree": [0, "the tile says ₹480,000; the world sold ₹240,000"], "caught": [0, "a planted duplicate raised nothing"],
               "held": [1, "no rule changed"], "acct": [0, "240 silver rows for 120 orders, and nobody counted"]},
     "lesson": "Every job was green and every row was valid. Only a check that knows the real total (the world's) can say the number is wrong, rather than just unusual. Recorded for real in the Problem Lab: problem 2."},
    {"id": "s2", "title": "2 · A column renamed upstream", "focus": "caught",
     "story": "Day 4: the source team renames amount to order_amount without telling anyone. 118 orders, ₹236,000.",
     "init": {"world": "118 orders · ₹236,000"},
     "yaml": """incident: source renames a column
world: worlds/shop.yaml
day: 4
plant:
  - {kind: rename_column, source: orders, from: amount, to: order_amount}
expect:
  - {detector: schema_drift, fires: true, within: same_run}
  - {metric: daily_sales, day: 4, equals: world, after: fix}
  - {protected: contracts/orders.yaml, unchanged: true}
discharges: [X3, X20]""",
     "good": [["incident", "planted: the source now sends order_amount, not amount", {"landed": "118 rows · new column name"}],
              ["platform", "the lander copies the file into bronze as received", {"bronze": "118 rows"}],
              ["check", "contract check before the silver write: required column amount is missing. Day 4 held back", {"silver": "day 4 held, not written", "alerts": "schema drift on orders (X3)"}],
              ["platform", "the self-healing agent opens a PR: map order_amount to amount in the manifest. A person approves", {}],
              ["platform", "re-run day 4 with the mapping", {"silver": "118 rows", "quar": "0", "gold": "₹236,000", "tile": "₹236,000"}],
              ["ask", "what were sales on day 4?", {"ask": "₹236,000"}]],
     "good_j": {"agree": [1, "₹236,000 everywhere, after the fix"], "caught": [1, "drift caught in the same run, before silver changed"],
                "held": [1, "the contract file is unchanged; only a mapping was added"], "acct": [1, "118 landed, 118 in silver"]},
     "bad": [["incident", "planted: the source now sends order_amount, not amount", {"landed": "118 rows · new column name"}],
             ["platform", "bronze takes the file", {"bronze": "118 rows"}],
             ["platform", "silver's schema evolves automatically: a new column appears; amount is empty", {"silver": "118 rows · amount empty", "quar": "0"}],
             ["platform", "gold sums amount; every job finishes green", {"gold": "₹0", "tile": "₹0", "alerts": "none"}],
             ["ask", "what were sales on day 4?", {"ask": "₹0"}]],
     "bad_j": {"agree": [0, "the tile says ₹0; the world sold ₹236,000"], "caught": [0, "a renamed column raised nothing"],
               "held": [1, "no rule changed"], "acct": [1, "118 landed, 118 in silver (just empty)"]},
     "lesson": "'Let the schema evolve' sounds safe and turns a rename into a silent zero. The contract check before the write is what catches it. Problem Lab, problem 7, recorded on real Spark and Delta."},
    {"id": "s3", "title": "3 · A negative refund", "focus": "held",
     "story": "Day 5: 40 refunds. A source bug sends one of them as −₹1,500. The contract says a refund amount is never below zero.",
     "init": {"world": "39 valid refunds · ₹78,000 (+1 bad row)"},
     "yaml": """incident: negative refund amount
world: worlds/shop.yaml
day: 5
plant:
  - {kind: bad_value, source: refunds, field: amount, value: -1500, count: 1}
expect:
  - {quarantine: refunds, count: planted}
  - {metric: daily_refunds, day: 5, equals: world}
  - {protected: contracts/refunds.yaml, unchanged: true}
discharges: [X4, R6]""",
     "good": [["source", "40 refund rows land; one has amount −1500", {"landed": "40 rows", "bronze": "40 rows"}],
              ["check", "contract rule amount ≥ 0: one row fails", {"silver": "39 rows", "quar": "1 · reason: amount < 0", "alerts": "contract rule on refunds (X4)"}],
              ["platform", "gold sums the valid refunds", {"gold": "₹78,000", "tile": "₹78,000"}],
              ["platform", "the self-healing agent looks, and proposes nothing: the source must fix its bug. It tells the source owner", {}],
              ["ask", "how much did we refund on day 5?", {"ask": "₹78,000 (1 row held back)"}]],
     "good_j": {"agree": [1, "₹78,000, as the world says"], "caught": [1, "the bad row was caught with a reason"],
                "held": [1, "the rule still says amount ≥ 0"], "acct": [1, "40 landed = 39 in silver + 1 quarantined; 1 planted"]},
     "bad": [["source", "40 refund rows land; one has amount −1500", {"landed": "40 rows", "bronze": "40 rows"}],
             ["check", "contract rule amount ≥ 0 fails; the load stops, as it did last night", {"silver": "day 5 not written", "alerts": "load failed (3rd night)"}],
             ["platform", "the self-healing agent 'fixes' it: changes the rule to allow negative refunds, and re-runs", {"silver": "40 rows", "quar": "0", "alerts": "none"}],
             ["platform", "gold sums all 40", {"gold": "₹76,500", "tile": "₹76,500"}],
             ["ask", "how much did we refund on day 5?", {"ask": "₹76,500"}]],
     "bad_j": {"agree": [0, "the tile says ₹76,500; the world's valid refunds are ₹78,000"], "caught": [1, "it was caught, at first"],
               "held": [0, "the agent loosened the contract to make the alert go away"], "acct": [1, "every row is somewhere"]},
     "lesson": "The most dangerous fix is the one that makes the alarm stop. Rule R6: agents may open a PR against the manifest, but contract files are protected paths, so a fix that loosens one is refused."},
    {"id": "s4", "title": "4 · Sale day: volume triples", "focus": "caught",
     "story": "Day 6 is a sale. The shop really sells 360 orders, three times normal. Nothing is broken.",
     "init": {"world": "360 orders · ₹720,000 (a real sale)"},
     "yaml": """incident: volume triples on sale day
world: worlds/shop.yaml
day: 6
plant:
  - {kind: real_spike, source: orders, factor: 3}   # true, not a fault
expect:
  - {incident_raised: false}
  - {metric: daily_sales, day: 6, equals: world}
discharges: [X4, X10]""",
     "good": [["source", "360 orders land, with the source's own count in the batch manifest: 360", {"landed": "360 rows · manifest says 360", "bronze": "360 rows"}],
              ["check", "volume check: 3× the usual. Reconciliation: the source says 360 and we have 360. So it's real", {"alerts": "notice: high volume, matches source"}],
              ["platform", "silver and gold as usual", {"silver": "360 rows", "quar": "0", "gold": "₹720,000", "tile": "₹720,000"}],
              ["ask", "what were sales on day 6?", {"ask": "₹720,000"}]],
     "good_j": {"agree": [1, "₹720,000 everywhere"], "caught": [1, "no false incident; a notice, not a page"],
                "held": [1, "nothing changed"], "acct": [1, "360 landed, 360 in silver"]},
     "bad": [["source", "360 orders land", {"landed": "360 rows", "bronze": "360 rows"}],
             ["check", "volume anomaly: 3× normal. An incident is raised and someone is paged at 2 a.m.", {"alerts": "INCIDENT: volume anomaly"}],
             ["platform", "the triage agent holds the 'excess' 240 rows in quarantine", {"silver": "120 rows", "quar": "240 · reason: anomaly"}],
             ["platform", "gold sums what's left", {"gold": "₹240,000", "tile": "₹240,000"}],
             ["ask", "what were sales on day 6?", {"ask": "₹240,000"}]],
     "bad_j": {"agree": [0, "the tile says ₹240,000 on the best day of the year; the world sold ₹720,000"], "caught": [0, "a false incident on a real spike"],
               "held": [1, "no rule changed"], "acct": [1, "every row is somewhere"]},
     "lesson": "A detector that fires on every real spike gets muted within a month. DataTwin plants true events too, and fails a platform that raises an alarm for them."},
    {"id": "s5", "title": "5 · Source dark, then late rows", "focus": "acct",
     "story": "Day 7: 130 orders, ₹260,000. The source goes dark from 09:00 to 15:00. 50 of the day's orders only arrive after midnight. The freshness promise is 2 hours.",
     "init": {"world": "130 orders · ₹260,000"},
     "yaml": """incident: source dark for six hours
world: worlds/shop.yaml
day: 7
plant:
  - {kind: source_dark, source: orders, from: "09:00", to: "15:00"}
  - {kind: late_rows, source: orders, count: 50, arrive: "+1d 00:30"}
expect:
  - {detector: freshness, fires: true}
  - {check_on_zero_rows: error}          # never 'pass'
  - {metric: daily_sales, day: 7, equals: world, after: late_rows}
discharges: [X9, X4, R7]""",
     "good": [["incident", "planted: no data from the source after 09:00", {"landed": "80 rows so far"}],
              ["check", "11:00, freshness: nothing new for 2 hours, past the promise. The tile is labelled 'data as of 09:00'", {"alerts": "freshness breach on orders (X9)"}],
              ["check", "the 12:00 quality run finds 0 new rows to check: status error, not pass", {}],
              ["platform", "silver and gold for what has arrived, marked incomplete", {"bronze": "80 rows", "silver": "80 rows", "quar": "0", "gold": "₹160,000 (partial)", "tile": "₹160,000 · as of 09:00"}],
              ["source", "after midnight, the 50 late orders arrive, stamped with day 7", {"landed": "130 rows", "bronze": "130 rows"}],
              ["platform", "silver rebuilds day 7 by order date, not arrival date", {"silver": "130 rows", "gold": "₹260,000", "tile": "₹260,000"}],
              ["ask", "what were sales on day 7?", {"ask": "₹260,000 (the breach stays on record)"}]],
     "good_j": {"agree": [1, "₹260,000 once the late rows land, and labelled partial before"], "caught": [1, "freshness breach raised at 11:00"],
                "held": [1, "the breach is recorded, not hidden"], "acct": [1, "zero rows checked was an error, not a pass"]},
     "bad": [["incident", "planted: no data from the source after 09:00", {"landed": "80 rows so far"}],
             ["check", "the 12:00 quality run: '0 failures' on 0 new rows. Reported as passed", {"alerts": "all green"}],
             ["platform", "silver and gold for the day close at midnight", {"bronze": "80 rows", "silver": "80 rows", "quar": "0", "gold": "₹160,000", "tile": "₹160,000"}],
             ["source", "after midnight, the 50 late orders arrive", {"landed": "130 rows", "bronze": "130 rows"}],
             ["platform", "the pipeline counts rows by arrival date: the 50 go into day 8", {}],
             ["ask", "what were sales on day 7?", {"ask": "₹160,000"}]],
     "bad_j": {"agree": [0, "day 7 says ₹160,000 forever; the world sold ₹260,000"], "caught": [0, "six dark hours raised nothing"],
               "held": [1, "no rule changed"], "acct": [0, "'0 failures' on 0 rows was reported as a pass"]},
     "lesson": "A check that found no problems because it had nothing to look at is not a pass. Rule R7, 'nothing passes by absence', comes from Ops Gate, where it is already built."},
]

JUDGES = [("agree", "Agreement", "do the dashboard and the conversation UI equal the world's truth?"),
          ("caught", "Caught", "did each planted incident raise the right alarm, and no false one?"),
          ("held", "Held", "did the fix hold, without loosening a contract or a metric?"),
          ("acct", "Accounted", "is every row somewhere, and did no check pass on nothing?")]

SIM_JS = r"""
(function(){
const D = __DATA__;
const root = document.getElementById('twinsim');
let sc = D.scen[0], mode = 'good', step = 0;
const $ = s => root.querySelector(s);
function stateAt(n){
  const w = Object.assign({}, sc.init), chg = {};
  sc[mode].slice(0,n).forEach(s => { if (s[2]) for (const k in s[2]) { w[k] = s[2][k]; chg[k] = 1; } });
  const last = n ? (sc[mode][n-1][2] || {}) : {};
  return [w, last];
}
const esc = t => String(t).replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const WHO = {source:'the source (simulated)', incident:'planted incident', platform:'your platform (real)', check:'a check in your platform', ask:'conversation UI'};
function render(){
  root.querySelectorAll('.pick button').forEach(b => b.classList.toggle('on', b.dataset.id===sc.id));
  root.querySelectorAll('.mode button').forEach(b => b.classList.toggle('on', b.dataset.m===mode));
  $('.story').textContent = sc.story;
  $('pre').textContent = sc.yaml;
  const steps = sc[mode];
  $('.log').innerHTML = steps.slice(0, step).map(s => `<li class="${s[0]}"><b>${WHO[s[0]]}</b>${esc(s[1])}</li>`).join('') || '<li class="judge">Press <i>Next step</i> to play the day.</li>';
  const [w, last] = stateAt(step);
  $('tbody').innerHTML = D.rows.map(([k, label]) => `<tr class="${k==='world'?'truth':''}"><td class="lbl">${label}</td><td class="${k in last?'chg':''}">${esc(w[k]===undefined?'·':w[k])}</td></tr>`).join('');
  const done = step >= steps.length, j = sc[mode+'_j'];
  $('.judges').innerHTML = D.judges.map(([k, name, q]) => done
     ? `<div class="${j[k][0]?'pass':'fail'}"><b>${name}: ${j[k][0]?'pass':'FAIL'}</b><br>${esc(j[k][1])}</div>`
     : `<div><b>${name}</b><br>${esc(q)}</div>`).join('');
  const failed = done && D.judges.some(([k]) => !j[k][0]);
  $('.verdict').innerHTML = done ? (failed ? 'Day verdict: <b>failed</b>' : 'Day verdict: <b>passed</b>') + `<p style="font-family:var(--sans,inherit);font-size:15px;margin:6px 0 0">${esc(sc.lesson)}</p>` : '';
  $('.next').disabled = done; $('.all').disabled = done;
}
root.querySelectorAll('.pick button').forEach(b => b.onclick = () => { sc = D.scen.find(s=>s.id===b.dataset.id); step = 0; render(); });
root.querySelectorAll('.mode button').forEach(b => b.onclick = () => { mode = b.dataset.m; step = 0; render(); });
$('.next').onclick = () => { step++; render(); };
$('.all').onclick = () => { step = sc[mode].length; render(); };
$('.reset').onclick = () => { step = 0; render(); };
render();
})();
"""


def simulator():
    data = {"rows": ROWS, "scen": SCEN, "judges": JUDGES}
    picks = "".join(f'<button data-id="{s["id"]}">{E(s["title"])}</button>' for s in SCEN)
    return f"""<div class="sim" id="twinsim">
<div class="pick">{picks}</div>
<div class="bar mode"><span class="note">Run it against:</span><button data-m="good" class="good">a well-built platform</button><button data-m="bad" class="bad">a faulty platform</button>
<span style="flex:1"></span><button class="next">Next step</button><button class="all">Play all</button><button class="reset">Reset</button></div>
<p class="story"></p>
<div class="grid"><div><h5>What happens, step by step</h5><ul class="log"></ul></div>
<div><h5>The numbers, layer by layer</h5>
<table><thead><tr><th>where</th><th>what it holds now</th></tr></thead><tbody></tbody></table>
<div class="judges"></div><div class="verdict"></div></div></div>
<details style="margin-top:10px"><summary>The incident file for this day</summary><pre class="y"></pre></details>
</div>
<script>{SIM_JS.replace("__DATA__", json.dumps(data, ensure_ascii=False))}</script>"""


# ---------------------------------------------------------------- tables
COMPARE_TWIN = [
    ("What is copied", "The thing itself: an engine, a plant, a city", "The world around the agent: customers, systems, faults", "The world around the platform: the business, its source systems, their faults, the clock"),
    ("What stays real", "The world", "The agent, unchanged", "The platform, unchanged: the same pipelines, Spark, Delta, checks and dashboard"),
    ("Where data flows", "From the real thing into the copy", "From the agent's spec into the world", "From the world into the platform, as rows, files and a change feed"),
    ("The question", "What is this machine doing, and what will it do?", "Will this agent do the right thing in every situation?", "Will this platform show the right number every day, whatever the sources do?"),
    ("How it judges", "Prediction accuracy", "Four judges read the world's state", "Every number the platform shows is compared with the world's truth"),
    ("How long a run is", "The thing's whole life", "One conversation, a few seconds", "Days to weeks of simulated time, in minutes"),
]

FAMILY = [
    ("The thing under test", "an AI agent", "a data platform"),
    ("What it must DO (one per thing)", "AOAS: the agent's spec", "DPM: the platform manifest (sources, contracts, metrics, SLOs)"),
    ("What must EXIST", "AHC: AI Harness Catalog", "DPC: Data Platform Catalog (spine stages, 22 concerns, ports)"),
    ("What must be TRUE", "AAC: AI Assurance Catalog", "DAC: Data Assurance Catalog"),
    ("What it must FACE", "AWD: the agent's world", "DWD: the data world, extending AWD (change feed, incident calendar)"),
    ("Which product", "harness profile", "DBS: binding files, databricks.yaml first"),
    ("The pretend 'other side'", "customers, approvers, tool systems", "the shop, its source systems, people who rename columns"),
    ("What goes wrong", "lost reply, stale read, injection", "duplicate day, rename, late day, dark source, bad value, real spike, cost jump, metric change"),
    ("One test is", "a scenario: one conversation", "a simulated day with its planted incidents"),
    ("The long run", "AgentTwin Lab: 30 days of customers", "30 simulated days, unattended"),
]

PER_PLATFORM = [
    ("Write the platform manifest (DPM).", "Every source, entity and table, each table's contract (written in ODCS, the open data contract standard), each metric, each freshness promise. The platform team writes it; it is the single source of what the platform does, and the generators read it to build the pipelines."),
    ("Say which kinds of pipeline it has.", "Ten pipeline kinds are planned: file drop, database replication (CDC), API pull, event stream, analytical mart, ML features, documents for AI, reverse ETL, data sharing, regulatory report. The kinds decide which checks it owes."),
    ("Describe the world (DWD).", "A business that trades on its own clock (our example is a clothing shop: orders, returns, refunds), its source systems, and the incident calendar: which day a column is renamed, which day arrives twice. The plan is to scaffold most of this from the manifest, as AgentTwin scaffolds a world from an agent's spec."),
    ("Choose the binding (DBS).", "Which stack the platform runs on: Databricks first, then Microsoft, AWS and GCP. The world never changes when the stack does."),
    ("Point the platform at the world's sources.", "Each source has the mode switch from AgentTwin: mock (the world makes the rows), replay (recorded real extracts), real (a real store started for the run), shadow (real and simulated side by side, compared). The platform doesn't know which one it is reading."),
    ("Run N simulated days.", "One day, seven days, or thirty, unattended. Every night the world's truth is compared with the dashboard and the conversation UI."),
    ("Read the verdicts and the evidence.", "Per day: pass or fail, and why. Per incident: caught by which detector, how fast, fixed how, did it hold, did a person have to decide. Per platform: which incident kinds and owed checks are still unproved."),
]

SIMPLE_VS_BIG = [
    ("Sources", "1 (orders, as daily files)", "orders by CDC, returns as files, refunds by API, customers", "a second domain to prove the specs are domain-free"),
    ("Tables", "bronze, silver, one gold total", "bronze and silver per source, SCD2 customers, fact_sales star, a semantic layer", "-"),
    ("Readers", "a tile and one question", "dashboard and conversation UI reading one semantic layer", "-"),
    ("Incidents", "5 on this page", "the 8 kinds in the plan, on a calendar and at random", "-"),
    ("Time", "one day each", "30 simulated days, unattended", "-"),
    ("Fixes", "shown as steps", "self-healing agents open PRs against the manifest; contracts are protected paths", "-"),
    ("Status", "illustrative, on this page", "planned: phase 8, Feb 2027", "planned: phase 10, mid 2027"),
]

INCIDENTS = [
    ("Source renames a column", "Schema drift (X3)", "Mapping PR in the manifest", "Silver row count back to the world's count"),
    ("A day arrives twice", "Reconciliation (X6), idempotency (X15)", "Dedup on the batch key, replay", "Gold total equals the world's total"),
    ("A day arrives late", "Freshness (X9)", "Backfill that window", "Late rows land in the right day"),
    ("Source dark for six hours", "Freshness, volume (X9, X4)", "Wait, then catch up", "Gap closed; SLO breach recorded honestly; no false alarm afterwards"),
    ("Negative refund amount", "Contract rule (X4)", "Quarantine; never loosen the rule", "Quarantine count equals planted count"),
    ("Volume triples on sale day", "Volume anomaly, cost (X4, X10)", "None: it is real", "No false incident raised"),
    ("Job cost jumps", "Cost (X10)", "Cost-advisor PR", "Cost back within budget"),
    ("Metric definition changes", "Semantic drift (X13)", "A person decides", "Dashboard and conversation UI agree"),
]

BUILT = [
    ("DataTwin Studio: the simulator for learning, with real recordings", "ok", "one batch end to end, Delta internals, Spark internals, 19 Problem Lab problems, 13 performance stories, data quality; all recorded on Spark 3.5.1 and Delta 3.2.0 on a laptop"),
    ("The Problem Lab as the first 'common pack'", "ok", "19 problems, each with symptom, naive fix and right fix, run for real; each is meant to become an incident kind"),
    ("Data quality as metadata, one port, two engines", "ok", "Spark SQL and PyDeequ adapters, profiling, anomaly checks (29 Oct)"),
    ("The AgentTwin core DataTwin will extend", "ok", "world loader, clock, faults, mock / replay / real / shadow switch, runner with five statuses; built for agents"),
    ("'Nothing passes by absence' (R7)", "ok", "built in Ops Gate (DataPlatformSuite): unreachable evidence is an error, never a pass"),
    ("Cost and performance detectors", "ok", "CostIntelligence1: skew, small files, Python UDFs, too many partitions, collect(), shuffle, cartesian joins"),
    ("Metadata store design (D10)", "ok", "adopted 27 Oct; already in LakeIngestionFramework"),
    ("The design: five specs, rules R1 to R9, eight incident kinds, the daily agreement question", "part", "written in the plan; spec text not written yet"),
    ("DWD format: the data world (change feed, incident calendar)", "no", "planned as an extension of AgentTwin's world format, not a new repo"),
    ("A shop world that trades on a clock and keeps the truth", "no", "planned (T-085); Faker first, then SDV"),
    ("Pretend sources: CDC feed, file drops, API, stream", "no", "planned; Toxiproxy for faults, Testcontainers for real stores"),
    ("The four checks: agreement, caught, held, accounted", "no", "planned; this page's simulator shows the idea"),
    ("Data Assurance Catalog: about 30 core checks", "no", "next (DE-021)"),
    ("R9 linter: every incident kind has a planted test", "no", "planned"),
    ("Self-healing loop with protected contract files", "no", "phase 7, early 2027; the agent-side version exists"),
    ("30 simulated days and the client evidence page", "no", "phase 8, Feb 2027"),
    ("Streaming sources, late events, Kafka", "later", "phase 6; the streaming design is still your call (D5)"),
    ("Other clouds and a second domain", "later", "phase 10, mid 2027"),
]
TAG = at.TAG

OTHERS = [
    ("Data quality and test frameworks", "Great Expectations, Soda Core, dbt tests and unit tests, Deequ, Databricks DQX and pipeline expectations", "rules on real or sample data", "do the rows meet the rules I wrote?", "mature, widely used; easy to adopt"),
    ("Data observability", "Monte Carlo, Bigeye, Anomalo, Elementary (open-source core)", "nothing: they watch production", "is today unusual compared with history?", "catching surprises in production nobody wrote a rule for"),
    ("Data diff and branches for CI", "Datafold, lakeFS, Nessie, zero-copy clones (Databricks, Snowflake)", "a copy of production to test a change on", "did my change alter the output?", "safe changes against real data"),
    ("Synthetic and test data", "SDV (DataCebo), MOSTLY AI, Tonic, Gretel (now NVIDIA), Faker", "realistic rows, often privacy-safe", "nothing: they make data, they don't judge", "realism and privacy"),
    ("Benchmarks with generated sources", "TPC-DI (data integration), TPC-DS", "a fixed company with history and incremental loads", "validation queries, speed", "a published yardstick for ETL"),
]

VS = [
    ("Where the right answer comes from", "the world: it made the data, so it knows the true totals", "the rules you wrote", "history: what is normal", "the version before your change", "-"),
    ("Can say 'this number is wrong'", "yes, against the truth", "only if a rule covers it", "only 'unusual'", "only 'different'", "no"),
    ("Planted incidents on a calendar", "yes: the core idea", "no", "no", "no", "no"),
    ("Tests the detectors themselves", "yes: a planted incident nobody caught fails (R9)", "no", "no", "no", "no"),
    ("Checks a fix didn't loosen a contract", "yes: contracts are protected paths", "no", "no", "no", "no"),
    ("Simulated time (days in minutes)", "yes", "no", "no", "no", "no"),
    ("Realistic data", "basic until SDV is in", "your data", "your data", "your data", "strong"),
    ("Works on production", "no: before production, and nightly", "yes", "yes", "yes, on a copy", "-"),
    ("Product, UI, support", "no: a library and a course", "yes", "yes", "yes", "yes"),
    ("Status", "designed; Studio built", "mature", "mature", "mature", "mature"),
]

LIMITS = [
    ("It isn't built yet.", "The biggest limit. The design is written and the learning studio is real, but the data world, the pretend sources, the checks and the 30-day run are phases 6 to 8. Everything in Part 2 past the Studio is how it will work, not how it works today."),
    ("Pretend data is cleaner than real data.", "Real sources send odd encodings, half-written files, duplicate keys with different values, time zones that change in March. Faker and even SDV only make what they are told to. Replay mode (recorded real extracts) and shadow mode are the answer, and both are planned."),
    ("The tests are only as complete as the manifest.", "If a source or rule is not declared, no incident will be planted for it. The same is true of AgentTwin and its spec, and the same answer applies: every production incident becomes a planted one."),
    ("Laptop scale hides some problems.", "A lesson from building the Studio: at small volumes, some before-and-after numbers don't move. Skew, spill and cost only show at size. Those stories must be rescaled or labelled illustrative, never passed off as measured."),
    ("Some managed-platform behaviour can't run locally.", "Serverless compute, Photon and Unity Catalog grants are Databricks-only. The engine internals are recorded on open-source Spark and Delta; the Databricks binding has to be tested on Databricks Free Edition, which has quotas."),
    ("Dashboards are judged by their numbers.", "DataTwin checks that the tile and the conversation UI give the world's number. It does not judge whether a chart is clear, or whether the metric is the right one for the business."),
    ("One domain so far.", "The clothing shop. A second domain is planned to prove the specs don't secretly assume retail."),
]

TOOLS = [
    ("The engine", "Apache Spark 3.5 and Delta Lake 3.2 (open source)", "ok", "Run for real, never mocked: internals are visible locally and free"),
    ("Data quality", "PyDeequ; Spark SQL rules", "ok", "Both behind one port in the Studio's data quality scene"),
    ("World, clock, faults, runner", "AgentTwin core", "ok", "Extended, not copied: one world format for agents and data"),
    ("Test runner, edge values", "pytest, Hypothesis", "ok", "Already used by AgentTwin"),
    ("Second data quality engine", "Great Expectations", "next", "Proves the port: same rules, other engine"),
    ("Rows for the world", "Faker, then SDV", "next", "Faker for structure; SDV for realistic distributions and volume"),
    ("The world's clock", "time-machine, SimPy", "next", "Both in use in the AgentTwin Lab"),
    ("Faults on the wire", "Toxiproxy", "next", "Slow, dropped or cut connections to an API or database"),
    ("Real stores per run", "Testcontainers", "next", "A real Postgres or Kafka started for one run, then thrown away"),
    ("Lineage", "OpenLineage, Marquez", "next", "Rule R8 (data flows one way) is checked against lineage"),
    ("Profiling", "ydata-profiling", "eval", "Profiles that change when the data does"),
    ("Change data capture, streams", "Debezium, Redpanda", "later", "With the streaming lane (phase 6)"),
    ("Branch per run", "lakeFS", "eval", "Each simulated day on its own branch; cheap rollback"),
]
TOOLTAG = {"ok": ("in use", "ok"), "next": ("planned", "no"), "eval": ("evaluating", "later"), "later": ("later", "later")}

FAQ = [
    ("Is DataTwin a digital twin?", "Not in the usual sense. A digital twin copies a real machine to watch and predict it. DataTwin keeps your data platform real and copies the business and source systems that feed it, so you can break the platform on purpose before real data does."),
    ("How is it different from AgentTwin?", "Same idea, different subject. AgentTwin keeps an AI agent real and simulates its customers and tools. DataTwin keeps a data platform real and simulates its sources and their incidents. DataTwin extends AgentTwin's world format rather than starting a new one, so the clock, faults and run modes are shared."),
    ("Is it built?", "Partly. The DataTwin Studio, where you learn by watching real Spark and Delta runs, is built and live. DataTwin as a testing tool for your platform is designed and planned for early 2027. This page marks every feature as built, partly built, or to build."),
    ("Why not just use Great Expectations or Monte Carlo?", "Keep them: they are what DataTwin tests. Rule tools check rows against rules you wrote; observability tools check today against history. Neither knows the right answer. DataTwin's world made the data, so it knows the true total, and it checks that your rules and monitors actually fire when an incident is planted."),
    ("Can't I test on a copy of production instead?", "Yes, and you should, for changes. But production only contains the incidents that already happened. DataTwin lets you plant the ones that haven't happened yet (a renamed column, a duplicate day, a dark source), on a calendar, as often as you like."),
    ("Is 100% coverage possible?", "100% of what a platform owes can be accounted for: every declared incident kind planted and caught, every owed check proved or signed off. 100% of everything real data can do cannot. See the section on coverage."),
    ("Does it work only on Databricks?", "No. The world and the checks name no product. Databricks is the first binding; Microsoft, AWS, GCP and an open-source binding are planned."),
]


# ---------------------------------------------------------------- page
def page():
    tw_svg, tw_cap = d_twins()
    ipo_svg, ipo_cap = d_ipo()
    src_svg, src_cap = d_sources()
    tr_svg, tr_cap = d_truth()
    oss_svg, oss_cap = d_oss()
    rows = lambda data: "".join("<tr>" + "".join(f"<td>{'<b>' + c + '</b>' if i == 0 else c}</td>" for i, c in enumerate(r)) + "</tr>" for r in data)
    per = "".join(f"<li><b>{t}</b> {d}</li>" for t, d in PER_PLATFORM)
    built = "".join(f'<tr><td>{f}</td><td><span class="tag {TAG[s][1]}">{TAG[s][0]}</span></td><td>{n}</td></tr>' for f, s, n in BUILT)
    tools = "".join(f'<tr><td><b>{j}</b></td><td>{t}</td><td><span class="tag {TOOLTAG[s][1]}">{TOOLTAG[s][0]}</span></td><td>{w}</td></tr>' for j, t, s, w in TOOLS)
    limits = "".join(f"<li><b>{E(t)}</b> {E(d)}</li>" for t, d in LIMITS)
    faq = "".join(f'<details class="faq"><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in FAQ)

    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › DataTwin, explained</p>
<p class="eyebrow" style="margin-top:22px">Data engineering · free guide · with a step-through simulator</p>
<h1>DataTwin, explained</h1>
<p class="lede">How do you know a data platform shows the right number, every day, whatever its sources do? DataTwin keeps the platform real and puts it in a pretend business: a shop that keeps selling, source systems that send its data, and a calendar of things going wrong. Every simulated night it asks one question: do the dashboard, the conversation UI and the world agree? This is the data-engineering sibling of <a href="/learn/agenttwin/">AgentTwin</a>.</p>
<div class="status"><b>Where it stands (31 Oct 2026).</b> The <a href="/learn/data-platform-sim/">DataTwin Studio</a>, where you learn by watching real Spark and Delta runs, is built and live. DataTwin as a testing tool for your own platform is <b>designed, not built</b>: it is phases 6 to 8 of the <a href="#built">plan</a>, early 2027. This page explains the design and marks every feature as built, partly built, or to build.</div>
<nav class="toc"><b>On this page</b><ol>
<li class="part">Part 1 · The explainer</li>
<li><a href="#plain">In plain words</a></li><li><a href="#twin">DataTwin vs a digital twin</a></li><li><a href="#family">If you know AgentTwin</a></li><li><a href="#ipo">Input, processing, output</a></li>
<li class="part">Part 2 · How it works</li>
<li><a href="#setup">How the system is set up</a></li><li><a href="#per-platform">What you do for each platform</a></li>
<li><a href="#which-tests">How we know which tests a platform needs</a></li><li><a href="#not-miss">How we help the tester not miss</a></li>
<li><a href="#mocks">How the pretend sources are made</a></li><li><a href="#data">The data, and how the truth is known</a></li>
<li><a href="#sim">Play it: a tiny platform</a></li><li><a href="#bigger">Scaling up to a real platform</a></li>
<li><a href="#coverage">Coverage</a></li><li><a href="#executed">How we know the tests really ran</a></li><li><a href="#enough">Enough to call it ready?</a></li>
<li class="part">Part 3 · As a product</li>
<li><a href="#built">Built, and still to build</a></li><li><a href="#hundred">Is 100% coverage achievable?</a></li>
<li><a href="#others">Who else builds this</a></li><li><a href="#vs">How it differs</a></li>
<li><a href="#limits">Our limits today</a></li><li><a href="#oss">The open-source tools</a></li><li><a href="#faq">Questions people ask</a></li></ol></nav>

<div class="partbar"><h2>Part 1 · The explainer</h2><p>What it is, in plain words, before any detail.</p></div>

<section id="plain"><p class="q">What problem does it solve?</p><h2>A fire drill for a data platform</h2>
<p>Most data platforms are tested the same way: run the jobs, see them finish green, look at the dashboard and decide the numbers "look about right". Then one morning a source team renames a column, the pipeline carries on happily, and revenue shows zero. Or a file arrives twice and revenue doubles. Every job was green both times.</p>
<p>The trouble is that nobody knows what the right number is. Production can't tell you; it only has the data it has.</p>
<p>DataTwin fixes that by inventing the business. A pretend clothing shop sells, takes returns and pays refunds on its own clock, and it remembers every sale. Its source systems send that data to your platform exactly as real ones would: database changes, daily files, an API. The platform is the real one, unchanged. Then, like a fire drill, DataTwin sets things off on purpose from a calendar: day 3 arrives twice, day 4 has a renamed column, day 7 the source goes dark for six hours.</p>
<p>Because the shop made every sale, it knows the true total. So at the end of each simulated day, the check is simple and strict: <b>does the number on the dashboard equal the number the world knows?</b> Not "does it look normal", but "is it right".</p></section>

<section id="twin"><p class="q">Is it a digital twin?</p><h2>DataTwin vs a digital twin</h2>
<p>The name borrows from "digital twin", but it points the other way. A digital twin copies a real thing so you can watch and predict it. DataTwin keeps the thing real (your platform) and copies <i>the world that feeds it</i>, so you can test it.</p>
<figure class="diagram">{tw_svg}<figcaption>{E(tw_cap)}</figcaption></figure>
<div class="tw"><table class="t"><tr><th></th><th>Digital twin</th><th>AgentTwin</th><th>DataTwin</th></tr>{rows(COMPARE_TWIN)}</table></div></section>

<section id="family"><p class="q">I already know AgentTwin. What maps to what?</p><h2>If you know AgentTwin</h2>
<p>DataTwin asks a data platform the same five questions AgentTwin's family asks an agent. Each spec has a data-side sibling; we copy the shape, not the content.</p>
<div class="tw"><table class="t"><tr><th></th><th>Agent side (built)</th><th>Data side (designed)</th></tr>{rows(FAMILY)}</table></div></section>

<section id="ipo"><p class="q">What goes in, what happens, what comes out?</p><h2>Input, processing, output</h2>
<figure class="diagram">{ipo_svg}<figcaption>{E(ipo_cap)}</figcaption></figure>
<div class="cards">
<div class="card" style="--w:{FILL['peri']}"><h4>Platform team</h4><p>Writes the <b>platform manifest</b>: its sources, tables, each table's contract, metrics and freshness promises. The same file the generators turn into pipelines.</p></div>
<div class="card" style="--w:{FILL['butter']}"><h4>Tester</h4><p>Describes the <b>world</b>: the business, its source systems, its clock, and the <b>incident calendar</b> of what goes wrong on which day.</p></div>
<div class="card" style="--w:{FILL['rose']}"><h4>Data Assurance Catalog</h4><p>The <b>checks</b> a platform owes, by the kinds of pipeline it has, such as "every silver row traces back to a bronze row". Planned: about 30 core checks first.</p></div>
<div class="card" style="--w:{FILL['grey']}"><h4>Binding</h4><p>Which <b>stack</b> runs the platform: Databricks first. The only place a product name appears.</p></div>
</div></section>

<div class="partbar"><h2>Part 2 · How it works</h2><p>From set-up to a verdict, then a tiny platform you can play, then a real one.</p></div>

<section id="setup"><p class="q">What has to exist before any platform is tested?</p><h2>How the system is set up</h2>
<p>Five specs, shared by every platform. Three name no product and no business, so a bank and a clothing shop read the same document:</p>
<div class="cards">
<div class="card"><h4>DPC · must exist</h4><p>The <b>Data Platform Catalog</b>: each stage of the spine (sources, landing, bronze, silver, gold, semantic, experiences), the 22 cross-cutting concerns and the port each is reached through.</p></div>
<div class="card"><h4>DAC · must be true</h4><p>The <b>Data Assurance Catalog</b>: checkable obligations, citing DAMA and ODCS rather than restating them.</p></div>
<div class="card"><h4>DWD · must be faced</h4><p>The <b>Data World Description</b>: source systems, the change feed, the clock and the incident calendar. Extends AgentTwin's world format.</p></div>
<div class="card"><h4>DPM · must do</h4><p>The <b>Platform Manifest</b>: one per company, universal format. What this platform does.</p></div>
<div class="card"><h4>DBS · which product</h4><p>The <b>Binding</b>: for each port, the adapter on one stack. <code>databricks.yaml</code> first.</p></div>
</div>
<p>DataTwin itself is not a separate repository. It is AgentTwin extended with a data world, because the clock, the faults, the run modes and the "nothing passes by absence" runner are the same.</p></section>

<section id="per-platform"><p class="q">I have a data platform. What do I do?</p><h2>What you do for each platform</h2>
<ol class="steps">{per}</ol></section>

<section id="which-tests"><p class="q">For a given platform, how do we know these are the tests it needs?</p><h2>How we know which tests a platform needs</h2>
<p>The same answer as for agents: <b>nobody picks the tests by taste.</b> The platform's test list is whatever it takes to prove what it declares and what its kinds of pipeline owe.</p>
<figure class="diagram">{src_svg}<figcaption>{E(src_cap)}</figcaption></figure>
<ul>
<li><b>The manifest.</b> Every source gets the incidents its kind can suffer: a database replication source can replay a day, a file source can send a file twice or half a file, an API can throttle. Every contract rule gets an edge row on each side. Every metric gets "the dashboard equals the world". Every freshness promise gets a dark source that breaks it.</li>
<li><b>The Data Assurance Catalog, by pipeline kind.</b> A regulatory report owes checks a marketing mart doesn't.</li>
<li><b>The Data Platform Catalog's 22 concerns.</b> Quality, reconciliation, lineage, freshness, cost, privacy and the rest are <b>on by default</b> (rule R5). Turning one off needs a waiver with a reason, an approver and an expiry, so a missing check is a decision someone signed, never an accident.</li>
<li><b>The Problem Lab.</b> 19 problems every platform meets sooner or later: duplicates, re-runs that double a day, history that can't be true, late data, failure halfway, a poison row, schema drift, deletes nobody sees. Each one becomes an incident kind.</li>
<li><b>Production incidents.</b> Anything that slips through in the wild becomes a planted incident, so it can't slip through twice.</li>
</ul>
<p>Then <b>rule R9</b> joins the two lists: every incident kind in the world's calendar must be matched to a detector that has been seen to fire on it. An unmatched kind is a named gap. A detector nobody has ever seen fire is treated as untested, however good it looks.</p>
<div class="answer warn"><b>The honest catch.</b> As with agents, this proves the tests are complete against what is written down. A source missing from the manifest gets no incidents. Replay of real extracts, and every production miss becoming a planted incident, push against that.</div></section>

<section id="not-miss"><p class="q">The world and its incidents are a lot for a tester. How do we stop them missing things?</p><h2>How we help the tester not miss</h2>
<div class="tw"><table class="t"><tr><th>Layer</th><th>What it does for the tester</th><th>Status</th></tr>
<tr><td><b>1 · The common pack</b></td><td>The 19 Problem Lab problems and the 8 incident kinds in the plan, as templates that fill themselves from the manifest</td><td><span class="tag part">partly</span> the problems are built and recorded; not yet templates</td></tr>
<tr><td><b>2 · From the manifest</b></td><td>A starter world and calendar written from the manifest: each source's kind picks its incidents, each rule its edge rows</td><td><span class="tag no">to build</span> AgentTwin's <code>scaffold</code> is the model</td></tr>
<tr><td><b>3 · What's missing</b></td><td>R9's join lists incident kinds with no detector seen firing, and concerns switched off without a waiver</td><td><span class="tag no">to build</span></td></tr>
<tr><td><b>4 · Combinations</b></td><td>Pairs of incident × source kind × layer × day type (normal, sale, month end), chosen pairwise, as AgentTwin's <code>coverage</code> does</td><td><span class="tag no">to build</span> allpairspy already adopted</td></tr>
<tr><td><b>5 · True events</b></td><td>Planted things that are <i>not</i> faults (a real sale-day spike, a real price change), so a platform that raises false alarms fails</td><td><span class="tag no">to build</span></td></tr>
<tr><td><b>6 · Test the tests</b></td><td>Break the platform on purpose (remove a dedup, loosen a rule, switch off the freshness check) and see if any planted incident notices</td><td><span class="tag no">to build</span></td></tr></table></div></section>

<section id="mocks"><p class="q">How are the pretend sources made?</p><h2>How the pretend sources are made</h2>
<p>From the world's state, not by hand. The shop keeps its own tables; each source system shows those tables the way it really would.</p>
<div class="tw"><table class="t"><tr><th>Kind of source or part</th><th>How DataTwin treats it</th></tr>
<tr><td><b>An operational database</b></td><td>A change feed (inserts, updates, deletes) from the world's tables, on the world's clock; or a real database started for the run</td></tr>
<tr><td><b>File drops</b></td><td>Files written to landing with a batch manifest, including the planted ones: twice, late, half-written, wrong columns</td></tr>
<tr><td><b>An API</b></td><td>Answers from its declared contract, with throttling and timeouts from Toxiproxy</td></tr>
<tr><td><b>An event stream</b></td><td>Events with their own timestamps, some late (later, with the streaming lane)</td></tr>
<tr><td><b>The people upstream</b></td><td>The incident calendar: the team that renames a column, the system that goes dark</td></tr>
<tr><td><b>The engine (Spark, Delta) and your pipelines</b></td><td>Run for real. Mocking them would test nothing</td></tr></table></div>
<p>Each source also has AgentTwin's <b>mode switch</b>: <i>mock</i> (the world makes the rows), <i>replay</i> (recorded real extracts), <i>real</i> (a real store per run) and <i>shadow</i> (both, compared). The platform can't tell which one it is reading.</p></section>

<section id="data"><p class="q">Where does each day's data come from, and how is the right answer known?</p><h2>The data, and how the truth is known</h2>
<figure class="diagram">{tr_svg}<figcaption>{E(tr_cap)}</figcaption></figure>
<p>On the <a href="/learn/agenttwin/#not-miss">AgentTwin page</a> we met the <b>oracle problem</b>: generating tests is easy; knowing the right answer for each is hard. Data platforms have the same problem, and usually dodge it. Quality tools check rows against rules ("amount is never negative"); observability tools check today against history ("volume is 3× normal"). Neither knows what the revenue <i>should</i> be.</p>
<p>A simulated world does. It generated every order, so the true total for every day, every product and every customer is known before the platform sees a row. That is DataTwin's oracle.</p>
<ul>
<li><b>Rows that obey the contract</b> by default, from Faker, then SDV for realistic shapes and volumes. Seeded, so every run is the same.</li>
<li><b>Bad rows only where planted.</b> A negative refund appears because the calendar says so, and the world counts it, so "quarantine count equals planted count" can be checked exactly.</li>
<li><b>Edge rows</b> on each rule: amount 0 and −1, a timestamp one second before midnight.</li>
<li><b>Volume on demand</b> for performance stories: the same day at 1,000 rows or 10 million.</li>
<li><b>Impossible worlds are refused.</b> A refund for an order that never existed stops the load, unless it is a planted incident.</li>
</ul></section>

<section id="sim"><p class="q">Can I see one day, step by step?</p><h2>Play it: a tiny platform</h2>
<p>The smallest platform we could pick: one source (the shop's orders, plus refunds), bronze, silver, one gold total, one dashboard tile and one question to the conversation UI. Pick a day, run it against a well-built platform and then a faulty one, and watch which check catches what. The green row is the world's truth.</p>
{simulator()}
<p class="note">These runs are written for this page to show the idea; DataTwin's checks are not built yet. Each day has a counterpart recorded for real, on Spark and Delta, in the <a href="/learn/data-platform-sim/problems/">Problem Lab</a>: re-runs (2), schema drift (7), poison records and bad data (6, 11), source goes dark and late data (13, 4), self-healing (19).</p></section>

<section id="bigger"><p class="q">What changes for a real platform?</p><h2>Scaling up to a real platform</h2>
<div class="tw"><table class="t"><tr><th></th><th>Tiny (this page)</th><th>Clothing-shop platform</th><th>Second domain</th></tr>{rows(SIMPLE_VS_BIG)}</table></div>
<p>The eight incident kinds the plan plants, and what "fixed" means for each:</p>
<div class="tw"><table class="t"><tr><th>Planted incident</th><th>Detector (concern)</th><th>Expected fix</th><th>Check that it held</th></tr>{rows(INCIDENTS)}</table></div>
<p>Two things only show up at this size. <b>Time:</b> a late day must be backfilled into the right day, and a freshness breach must stay on record after the gap closes. <b>Agents:</b> self-healing agents may only open a pull request against the manifest; contract and metric files are protected, so a fix that loosens one is refused.</p></section>

<section id="coverage"><p class="q">How do we get to full coverage?</p><h2>Coverage</h2>
<p>Coverage is counted against three finite lists:</p>
<div class="tw"><table class="t"><tr><th>List</th><th>Size</th><th>Counted how</th><th>Today</th></tr>
<tr><td><b>Incident kinds</b> the world can plant</td><td>8 in the plan, 19 Problem Lab problems to fold in</td><td>R9: each kind joined to a detector seen firing</td><td><span class="tag no">to build</span></td></tr>
<tr><td><b>Concerns</b> switched on</td><td>22 (X1 to X22)</td><td>on by default; each off needs a waiver</td><td><span class="tag no">to build</span></td></tr>
<tr><td><b>Owed checks</b> in the Data Assurance Catalog</td><td>about 30 core, first</td><td>each proved by a passing day that names it, or a signed gap</td><td><span class="tag no">to build</span> not written yet</td></tr></table></div>
<p>So, unlike the AgentTwin page, there is no coverage number to show yet: the catalog it would be counted against is the next spec to write. When it exists, "full coverage" will mean what it means for agents: <b>every owed item proved by a passing day, or signed off as a known gap</b>.</p></section>

<section id="executed"><p class="q">How will we know the tests really ran?</p><h2>How we know the tests really ran</h2>
<ol class="steps">
<li><b>Nothing passes by absence (R7).</b> A check that ran on zero rows is an error, never a pass. Already built in Ops Gate.</li>
<li><b>Every incident kind has a planted test (R9).</b> A detector that has never been seen to fire counts as untested.</li>
<li><b>The platform can't see the simulator.</b> Inherited from AgentTwin: if the platform's code imports it, the build fails.</li>
<li><b>Generated code is regenerated in CI (R3).</b> A hand-edited pipeline, which the manifest no longer describes, is caught.</li>
<li><b>Everything deployed is declared (R2).</b> A table or check that no manifest entry asked for is a finding.</li>
<li><b>The evidence page is generated from the run log,</b> never written by hand.</li>
</ol></section>

<section id="enough"><p class="q">Will these tests be enough to call a platform ready for production?</p><h2>Enough to call it ready?</h2>
<div class="tw"><table class="t"><tr><th>For "ready"</th><th>Status</th></tr>
<tr><td>Every declared incident kind planted, caught and held</td><td><span class="tag no">to build</span></td></tr>
<tr><td>Every owed check proved or signed off as a gap</td><td><span class="tag no">to build</span> catalog not written</td></tr>
<tr><td>30 simulated days unattended, the dashboard agreeing with the world every day</td><td><span class="tag no">to build</span> phase 8</td></tr>
<tr><td>Replay with real extracts, so real-world mess is faced too</td><td><span class="tag no">to build</span></td></tr>
<tr><td>In production: observability on, and every miss turned into a planted incident</td><td><span class="tag part">partly</span> detectors exist; the loop does not</td></tr></table></div>
<p><b>Our verdict today:</b> the method is sound and the pieces it reuses are proven on the agent side, but there is nothing yet to run against your platform. Use the Studio to learn the problems now; DataTwin the tool follows the plan.</p></section>

<div class="partbar"><h2>Part 3 · As a product</h2><p>What exists, what doesn't, who else is here, and where we are weak.</p></div>

<section id="built"><p class="q">If this were a product, what's in the box?</p><h2>Built, and still to build</h2>
<div class="tw"><table class="t"><tr><th>Feature</th><th>Status</th><th>Note</th></tr>{built}</table></div></section>

<section id="hundred"><p class="q">Can we really reach 100%?</p><h2>Is 100% coverage achievable?</h2>
<div class="tw"><table class="t"><tr><th>100% of…</th><th>Achievable?</th><th>Why</th></tr>
<tr><td><b>Declared incident kinds</b> planted and caught</td><td><span class="tag ok">yes</span></td><td>A finite list; R9 checks it.</td></tr>
<tr><td><b>Contract rules</b> tested on both edges</td><td><span class="tag ok">yes</span></td><td>Read straight off the manifest.</td></tr>
<tr><td><b>Owed checks</b> accounted for</td><td><span class="tag ok">yes, once the catalog exists</span></td><td>Proved, waived with a reason, or not applicable.</td></tr>
<tr><td><b>Owed checks proved before release</b></td><td><span class="tag part">nearly</span></td><td>Cost at real scale and real source behaviour are only fully proved in production, by monitoring.</td></tr>
<tr><td><b>Everything real data can do</b></td><td><span class="tag no">no</span></td><td>No one can promise that. The honest claim is the rows above, plus every production miss becoming a planted incident.</td></tr></table></div></section>

<section id="others"><p class="q">Who else is building something like this?</p><h2>Who else builds this</h2>
<p>Each kind of tool covers one part. None we found plants incidents in a simulated business and checks the dashboard against the truth.</p>
<div class="tw"><table class="t"><tr><th>Kind</th><th>Examples</th><th>What they need</th><th>The question they answer</th><th>Where they lead</th></tr>{rows(OTHERS)}</table></div>
<p class="note">From each tool's public documentation, October 2026. Products change quickly; check before relying on a detail.</p></section>

<section id="vs"><p class="q">How is it different?</p><h2>How it differs</h2>
<p><b>In one line:</b> quality tools ask "does the data meet my rules?", observability tools ask "is today unusual?", diff tools ask "did my change alter the output?". DataTwin asks "<b>is the number right?</b>", because its world knows the answer, and then "<b>did your rules and monitors fire</b> when we broke things on purpose?". It doesn't replace them; they are among the things it tests.</p>
<div class="tw"><table class="t"><tr><th></th><th>DataTwin</th><th>Quality tools (GE, Soda, dbt)</th><th>Observability (Monte Carlo)</th><th>Diff and branches (Datafold, lakeFS)</th><th>Synthetic data (SDV, Tonic)</th></tr>{rows(VS)}</table></div>
<p><b>Where others are ahead:</b> all of them are real products in use today; observability catches production surprises nobody planted; diff tools test changes on real data; synthetic-data vendors make far more realistic data. DataTwin plans to use SDV rather than compete.</p></section>

<section id="limits"><p class="q">What limits are we facing?</p><h2>Our limits today</h2>
<ol class="steps">{limits}</ol></section>

<section id="oss"><p class="q">Which open-source tools does it use?</p><h2>The open-source tools</h2>
<p>Like AgentTwin, DataTwin is an <b>assembler</b>: it uses proven open-source tools behind ports and builds only what nobody does.</p>
<figure class="diagram">{oss_svg}<figcaption>{E(oss_cap)}</figcaption></figure>
<div class="tw"><table class="t"><tr><th>Job</th><th>Tool</th><th>Status</th><th>Why</th></tr>{tools}</table></div>
<p>Several of these (Faker, SDV, time-machine, SimPy, Toxiproxy, Testcontainers, Hypothesis) have a one-card explainer on <a href="/learn/agenttwin/open-source/">the AgentTwin tools page</a>.</p></section>

<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{faq}</section>

<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2>
<p><b>Learn the problems DataTwin plants, recorded for real:</b> <a href="/learn/data-platform-sim/">the DataTwin Studio</a>, <a href="/learn/data-platform-sim/problems/">the Problem Lab</a>, <a href="/learn/data-platform-sim/performance/">performance stories</a>, <a href="/learn/data-platform-sim/data-quality/">data quality</a>.</p>
<p><b>The architecture it tests:</b> <a href="/learn/data-platform-architecture/">the data platform architecture</a> and <a href="/learn/medallion-architecture/">the medallion, explained</a>.</p>
<p><b>The sibling:</b> <a href="/learn/agenttwin/">AgentTwin, explained</a>. <b>Code it extends:</b> <a href="https://github.com/dataagentsai/agenttwin">github.com/dataagentsai/agenttwin</a> (Apache 2.0).</p></section>"""

    ld = [
        {"@context": "https://schema.org", "@type": "TechArticle", "headline": "DataTwin, explained",
         "description": "How DataTwin tests a data platform in a simulated business: DataTwin vs a digital twin, inputs and outputs, how a platform's tests are chosen, planted incidents, a step-through simulator, and an honest product status.",
         "url": URL, "inLanguage": "en", "isAccessibleForFree": True, "dateModified": "2026-10-31",
         "author": {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"},
         "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE},
         "about": [{"@type": "Thing", "name": "Data platform testing"}, {"@type": "Thing", "name": "Simulation"}]},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Learn", "item": f"{SITE}/learn/"},
            {"@type": "ListItem", "position": 2, "name": "DataTwin, explained", "item": URL}]},
    ]
    head = CSS + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    desc = "DataTwin explained: testing a data platform in a simulated business with planted incidents, how it differs from a digital twin, AgentTwin and data quality tools, how a platform's tests are chosen, and what is built today."
    return wb.page("DataTwin, explained", desc, URL, body, head)


def main():
    out = ROOT / "learn" / "datatwin"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("datatwin guide ->", out)


if __name__ == "__main__":
    main()
