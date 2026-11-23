"""Checks as code versus checks as documents, spec-driven gates, and the Ops Gate checklist: /learn/checks-as-code/.

    python3 _guides/de_gates.py      (then python3 _site/nav.py and python3 _site/seo.py)

One page: the concept (document vs code), spec-driven development, anatomy of a check, the gates across the lifecycle
(requirements, discovery, architecture, build, test, ops), how a gate runs, and the Ops Gate: ~105 checks in 14 categories
that a project must pass before production, so teams know what they will be tested on and can prepare.
The checks are a starting spec; the owner reviews and edits them here. Same field names as the project-review catalog.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import de_essentials as DE  # noqa: E402

E, R, T, table, fig, Lx, L, C = DE.E, DE.R, DE.T, DE.table, DE.fig, DE.Lx, DE.L, DE.C
BLUE, MINT, BUTTER, ROSE, LAV, GREY = DE.BLUE, DE.MINT, DE.BUTTER, DE.ROSE, DE.LAV, DE.GREY
URL_PATH = "/learn/checks-as-code/"
BASE = DE.BASE
REPO = "https://github.com/dataagentsai/data-project-review"
try:
    N_CATALOG = len(json.load(open(Path.home() / "data-project-review" / "catalog.json"))["checks"])
except Exception:
    N_CATALOG = 198

CATS = [("OWN", "Ownership and support", "Who answers when it breaks."), ("RUN", "Runbook and documentation", "Can someone else run it from the paper?"),
        ("MON", "Monitoring and alerting", "Will we know before the business does?"), ("REC", "Recovery and resilience", "Can we get back, and prove it?"),
        ("REL", "Release and deployment", "Can we ship and unship safely?"), ("DQ", "Data quality and reconciliation", "Are the numbers right, and shown to be?"),
        ("DAT", "Data operations", "Loads, changes, history and manual steps."), ("SEC", "Security and access", "Who can do what, and can we prove it?"),
        ("PRV", "Privacy and compliance", "Personal data, retention, rules."), ("PRF", "Performance and capacity", "Does it hold at real volume and peak?"),
        ("CST", "Cost and FinOps", "Is the bill owned, forecast and watched?"), ("CON", "Consumer readiness", "Are the users ready, and the old report retired?"),
        ("GOV", "Governance and sign-off", "Defects, risks, exceptions and signatures."), ("AIO", "AI and agent operations", "Only when AI or agents are in scope.")]

# category, check, evidence, owner, severity, how verified, prepare by stage
CHECKS = [
    ("OWN", "A named owner for the system, with a deputy", "Owner register entry", "Operations", "blocker", "manual", 5),
    ("OWN", "Support model agreed: hours, tiers, response times, who answers", "Support page signed by operations", "Operations", "blocker", "manual", 5),
    ("OWN", "Escalation path from first line to the build team and vendors, with names and numbers", "Contact sheet, tested once", "PM", "major", "drill", 8),
    ("OWN", "On-call rota covers the agreed hours for the first 90 days", "Rota", "Operations", "blocker", "manual", 8),
    ("OWN", "The support team has made one real change without the builders", "Change record", "PM", "major", "drill", 9),
    ("OWN", "Vendor support contracts and contacts are in place", "Contract and contact list", "PM", "major", "manual", 8),
    ("RUN", "A runbook exists for each job: what it does, normal duration, how to rerun", "Runbook", "Tech Anchor", "blocker", "manual", 7),
    ("RUN", "Someone who did not build it has followed the runbook and succeeded", "Test note", "Operations", "blocker", "drill", 8),
    ("RUN", "Known failure modes and their fixes are listed", "Failure list", "Tech Anchor", "major", "manual", 8),
    ("RUN", "The architecture picture and data flow are current", "Document with a date", "Tech Anchor", "major", "manual", 8),
    ("RUN", "The data dictionary and metric catalogue are published", "Link", "BA", "major", "manual", 8),
    ("RUN", "Lineage from source to report is documented", "Lineage document or tool view", "Tech Anchor", "major", "semi-automated", 8),
    ("RUN", "The decision log and open risks are handed over", "Log", "PM", "minor", "manual", 9),
    ("MON", "Every job failure alerts a named person, not a shared mailbox", "Alert test result", "Tech Anchor", "blocker", "automated", 7),
    ("MON", "Late or missing data is detected and alerted (freshness)", "Alert test result", "Tech Anchor", "blocker", "automated", 7),
    ("MON", "Data quality check failures raise an alert", "Alert test result", "Tech Anchor", "blocker", "automated", 7),
    ("MON", "Unusual volumes (too few or too many rows) raise an alert", "Alert configuration", "Tech Anchor", "major", "automated", 7),
    ("MON", "One operations dashboard shows pipeline health", "Dashboard link", "Tech Anchor", "major", "manual", 8),
    ("MON", "Alerts were tested by breaking something on purpose", "Test record", "Operations", "blocker", "drill", 8),
    ("MON", "No alert is routinely ignored; noise has been reviewed", "Review note", "Operations", "minor", "manual", 9),
    ("REC", "A backup or recovery method exists for the data and the configuration", "Recovery document", "Tech Anchor", "blocker", "manual", 7),
    ("REC", "A restore has been tested, and the time measured", "Restore test record", "Operations", "blocker", "drill", 8),
    ("REC", "Recovery targets (how long, how much data loss) are agreed and met", "Agreement and test result", "Sponsor", "major", "drill", 8),
    ("REC", "Any job can be rerun safely without double counting", "Rerun test", "Tech Anchor", "blocker", "automated", 6),
    ("REC", "A failed night can be recovered, including catching up", "Drill record", "Tech Anchor", "blocker", "drill", 8),
    ("REC", "Raw data is kept so the pipeline can be rebuilt from it", "Design and retention setting", "Tech Anchor", "major", "manual", 6),
    ("REC", "Behaviour when a source is late or down is defined and tested", "Document and test", "Tech Anchor", "major", "drill", 7),
    ("REC", "A failure drill has been held with operations", "Drill report", "PM", "blocker", "drill", 8),
    ("REL", "Release is by pipeline, with no manual steps", "Pipeline run", "Tech Anchor", "blocker", "automated", 5),
    ("REL", "The same code runs in test and production; settings are kept apart", "Configuration review", "Tech Anchor", "blocker", "semi-automated", 6),
    ("REL", "Rollback has been rehearsed", "Rehearsal report", "Tech Anchor", "blocker", "drill", 8),
    ("REL", "A cut-over plan exists, with timings and owners", "Plan", "PM", "blocker", "manual", 8),
    ("REL", "Release notes and version tags exist", "Notes", "Tech Anchor", "minor", "manual", 8),
    ("REL", "Secrets are in a secret store, not in code", "Scan result", "Tech Anchor", "blocker", "automated", 6),
    ("REL", "The change approval route is agreed with client IT", "Process", "PM", "major", "manual", 5),
    ("REL", "Test and production environments match closely enough", "Comparison", "Tech Anchor", "major", "semi-automated", 7),
    ("DQ", "Data quality checks run on every load", "Run log", "Tech Anchor", "blocker", "automated", 6),
    ("DQ", "Thresholds are agreed with the data owners", "Threshold sheet", "BA", "major", "manual", 5),
    ("DQ", "Reconciliation to the trusted report is signed by finance", "Signed reconciliation", "BA", "blocker", "manual", 7),
    ("DQ", "The plan to reconcile the first production load is agreed", "Plan", "BA", "major", "manual", 8),
    ("DQ", "Rejected rows are counted and reviewed by a named person", "Review record", "BA", "major", "manual", 7),
    ("DQ", "Late and corrected records give the right numbers (demonstrated)", "Demo", "Tech Anchor", "major", "automated", 7),
    ("DQ", "Deletes at the source are reflected correctly", "Test result", "Tech Anchor", "major", "automated", 7),
    ("DQ", "A quality scorecard is visible to the business owners", "Scorecard view", "BA", "minor", "manual", 8),
    ("DAT", "The load schedule and dependencies are documented and agreed with source owners", "Schedule page", "Tech Anchor", "blocker", "manual", 6),
    ("DAT", "A process exists for source schema changes: notice, test, release", "Process page", "Tech Anchor", "major", "manual", 7),
    ("DAT", "A backfill and history reload procedure is written and tested", "Procedure and test", "Tech Anchor", "major", "drill", 7),
    ("DAT", "The historical load is complete and reconciled", "Reconciliation", "BA", "blocker", "manual", 8),
    ("DAT", "Manual steps (file uploads, approvals) are listed and owned; none are hidden", "Manual steps list", "Tech Anchor", "major", "manual", 7),
    ("DAT", "Retention and archive jobs are scheduled", "Schedule", "Tech Anchor", "minor", "manual", 8),
    ("SEC", "Access follows least privilege, by role", "Access matrix", "Security", "blocker", "manual", 6),
    ("SEC", "Roles have been tested with real people in each role", "Test record", "Tech Anchor", "blocker", "drill", 7),
    ("SEC", "No shared or personal accounts run production jobs", "Account review", "Tech Anchor", "blocker", "automated", 6),
    ("SEC", "Keys and secrets rotate, with known owners", "Rotation record", "Tech Anchor", "major", "automated", 8),
    ("SEC", "Data is encrypted in transit and at rest", "Configuration", "Tech Anchor", "blocker", "automated", 6),
    ("SEC", "Audit logs capture who accessed what, kept for the agreed time", "Log configuration", "Security", "major", "automated", 7),
    ("SEC", "The security review is done and findings are closed (vulnerability scan; penetration test where required)", "Report", "Security", "blocker", "manual", 7),
    ("SEC", "An access review process exists for joiners, movers and leavers", "Process", "Security", "major", "manual", 8),
    ("SEC", "Network paths are approved", "Approval", "Client IT", "blocker", "manual", 6),
    ("PRV", "Personal and sensitive data is classified", "Classification list", "BA", "blocker", "manual", 3),
    ("PRV", "Lawful basis and purpose are recorded for each use", "Register", "Privacy", "blocker", "manual", 4),
    ("PRV", "Masking is applied where roles must not see data", "Test result", "Tech Anchor", "blocker", "automated", 7),
    ("PRV", "Retention rules are set and deletion is tested", "Deletion test", "Tech Anchor", "blocker", "drill", 7),
    ("PRV", "Data location (residency) meets the rules", "Review", "Privacy", "blocker", "manual", 4),
    ("PRV", "A privacy impact assessment is done where required", "Assessment", "Privacy", "major", "manual", 4),
    ("PRV", "Third-party terms allow this use of the data", "Terms summary", "PM", "major", "manual", 4),
    ("PRF", "A run at production volume finishes inside the window, with margin", "Load test", "Tech Anchor", "blocker", "automated", 7),
    ("PRF", "Key reports meet the agreed response times at production volume", "Test result", "Tech Anchor", "blocker", "automated", 7),
    ("PRF", "Concurrent users have been tested to the expected peak", "Test result", "Tech Anchor", "major", "automated", 7),
    ("PRF", "There is at least 12 months of growth headroom", "Forecast", "Tech Anchor", "major", "manual", 8),
    ("PRF", "Peak days (month-end, year-end) have been rehearsed", "Rehearsal", "Tech Anchor", "major", "drill", 8),
    ("PRF", "Loads have been checked not to harm the source", "Test note", "Tech Anchor", "major", "manual", 7),
    ("CST", "A monthly budget exists, with an owner", "Budget record", "PM", "blocker", "manual", 4),
    ("CST", "Cost allocation tags are on all resources", "Scan result", "Tech Anchor", "major", "automated", 6),
    ("CST", "A cost alert fires on a jump", "Alert test", "Tech Anchor", "major", "automated", 8),
    ("CST", "A 12-month cost forecast exists", "Forecast", "Tech Anchor", "major", "manual", 8),
    ("CST", "Idle resources shut down automatically", "Configuration", "Tech Anchor", "minor", "automated", 8),
    ("CST", "A monthly cost review is scheduled", "Calendar entry", "PM", "minor", "manual", 9),
    ("CON", "Every consumer is named, with an owner and contact", "Consumer register", "BA", "major", "manual", 5),
    ("CON", "Users have access and licences", "Access check", "PM", "blocker", "manual", 7),
    ("CON", "User acceptance is signed by the business owners", "Signed acceptance", "BA", "blocker", "manual", 7),
    ("CON", "Reports show when the data was last updated, and its source", "Report view", "Tech Anchor", "major", "manual", 7),
    ("CON", "Training and a support route for users exist", "Training record", "PM", "major", "manual", 8),
    ("CON", "Old reports have an agreed switch-off date", "Agreement", "BA", "major", "manual", 4),
    ("CON", "Users have been told about go-live and what changes", "Communication", "PM", "minor", "manual", 8),
    ("GOV", "Open defects are listed, and each is fixed or accepted in writing", "Defect list", "PM", "blocker", "manual", 8),
    ("GOV", "The risk register is current, with owners", "Register", "PM", "major", "manual", 8),
    ("GOV", "Design review findings are closed", "Findings log", "Tech Anchor", "blocker", "manual", 7),
    ("GOV", "Vendor review findings are recorded as decisions", "Decision log", "Tech Anchor", "major", "manual", 7),
    ("GOV", "Exceptions to this gate are recorded, with an owner and an expiry", "Exception list", "PM", "major", "manual", 8),
    ("GOV", "A hypercare plan with exit criteria exists", "Plan", "PM", "blocker", "manual", 8),
    ("GOV", "Sign-offs are collected: acceptance, security, operations", "Sign-off register", "PM", "blocker", "manual", 8),
    ("AIO", "Evaluation results meet the thresholds for this release", "Evaluation report", "Tech Anchor", "blocker", "automated", 7),
    ("AIO", "Guardrails are tested with attack and misuse cases", "Test result", "Security", "blocker", "automated", 7),
    ("AIO", "High-impact actions need human approval, with a queue and an owner", "Design and test", "BA", "blocker", "manual", 6),
    ("AIO", "Model, prompt and tool versions are recorded and can be rolled back", "Configuration and rollback test", "Tech Anchor", "blocker", "drill", 7),
    ("AIO", "Cost per task is measured and within budget", "Report", "Tech Anchor", "major", "automated", 7),
    ("AIO", "Quality, drift and cost are monitored, with alerts", "Dashboard and alert test", "Tech Anchor", "blocker", "automated", 7),
    ("AIO", "A Responsible AI review is done and the risk tier recorded", "Review record", "Risk", "blocker", "manual", 4),
    ("AIO", "The incident process covers AI failures: wrong answers, injection, outage", "Process and drill", "Operations", "major", "drill", 8),
    ("AIO", "A kill switch exists and has been tested", "Test record", "Tech Anchor", "blocker", "drill", 8),
]

GATES = [
    ("Requirements checklist", "1 to 2", "Is the request clear enough to estimate?", "BA lead, PM", "A subset of the project review checks on requirements, scope and stakeholders.", "Exists (subset)"),
    ("Discovery gate", "4", "Is it worth doing, and do we know how?", "Sponsor, business owner", "Project review checks for discovery; the discovery document; fail-fast test results.", "Exists"),
    ("Architecture gate", "4", "Will the design work, safely, at cost, for operations?", "Client architect, security, our architect", "Design checks from the project review, plus the vendor and cloud review findings.", "To derive from the checks"),
    ("Build readiness", "5", "Can the team build and release from day one?", "Tech Anchor, client IT", "Environments, access, pipeline, standards.", "To derive"),
    ("Test gate", "7", "Are the numbers right, and proven?", "Business owners, test lead", "Acceptance, reconciliation, performance and recovery evidence.", "To derive"),
    ("Ops gate", "8 to 9", "Can operations run it at 3 a.m. without the builders?", "Operations, with security and the business owner", "The checklist below.", "New, on this page"),
    ("Project close", "10", "Were the benefits delivered, and can support change it alone?", "Sponsor", "Benefits report; hand-over pack.", "To derive")]

DOC_VS_CODE = [
    ("Where it lives", "A Word, Excel or PDF file, copied around", "In a repository, next to the code"),
    ("When it is written", "Once, at the start", "Continuously, with history"),
    ("Who reads it", "The author, at the end", "Everyone, at every change"),
    ("What counts as evidence", "A tick by a person", "Evidence attached; some checks run themselves"),
    ("Drift", "Copies diverge and old versions circulate", "One source; differences are visible"),
    ("Same for every project", "Each project edits its own copy", "One spec; 'applies when' rules trim it"),
    ("Repeatability", "Depends on who runs it", "Same inputs, same result"),
    ("Coverage", "Unknown", "Counted: passed, failed, not yet known"),
    ("Cost of checking", "Manual every time", "Automatable for the checkable part"),
    ("Weakness", "Ignored once the deadline nears", "Needs upfront work; can be gamed; not everything is checkable")]

AUTOMATION = [("Manual", "A person looks at evidence and decides.", "Is the runbook usable? Are the definitions owned?"), ("Semi-automated", "A script collects the evidence; a person judges it.", "List all accounts that run production jobs; a person decides if each is allowed."),
              ("Automated", "The check runs and returns pass or fail.", "Did the last 30 loads alert on a deliberate failure? Is any secret in the code?"), ("Drill", "A rehearsal proves it works under stress.", "Restore from backup. Roll back a release. Run the runbook cold.")]

FIELDS = [("id", "A stable name, such as OPS-REC-02."), ("title", "The check in one sentence."), ("question", "The question a reviewer asks."), ("why", "What goes wrong without it, in one story."),
          ("applies", "When it applies: kind of project, components, patterns, such as 'AI in scope'."), ("owner", "The role accountable for passing it."), ("evidence", "What must be shown: documents and what 'good' looks like."),
          ("severity", "Blocker, major, minor."), ("due", "The lifecycle stage by which it should be ready."), ("fail_fast", "The cheapest early test to know if it will pass.")]

YAML = """id: OPS-REC-02
title: A restore has been tested, and the time measured
question: >
  Has someone restored the data and configuration from backup into a clean
  environment, with the time measured and compared with the agreed target?
why: >
  The backups ran for a year. The first real restore failed because the keys
  were not backed up. Recovery took three days instead of three hours.
applies:
  kind: [any]
  components: [storage, platform]
owner: operations
also: [tech-anchor]
evidence:
  docs: [recovery-document, restore-test-record]
  looks_like: A dated test record with the measured time and who ran it.
severity: blocker
due: 8            # lifecycle stage
fail_fast: Ask in discovery where backups live and who has ever restored one.
verify: drill"""

RUN_STEPS = [("Pre-flight", "Run the checks yourself, weeks before the gate. The gate holds no surprises."), ("Evidence pack", "Gather the evidence for each check in one place, named by check ID."),
             ("Gate review", "Reviewers go through the report, not the whole pack. Open items only."), ("Decision", "Pass, conditional pass, or not yet. Written, with names and dates."),
             ("After", "Conditions tracked to closure. Lessons feed back into the spec.")]

DECISIONS = [("Pass", "No open blockers. Every category has a named owner who has signed. Majors are fixed or accepted in writing with dates.", "Go to production."),
             ("Conditional pass", "No open blockers. A short list of majors, each with an owner and a date before or soon after go-live.", "Go, with conditions tracked weekly."),
             ("Not yet", "Any open blocker, or a category with no owner.", "Do not go. Fix, then re-run only the failed checks.")]

PREP = [("Stage 3 to 4", "Classify sensitive data. Record lawful basis. Agree budget and owner. Agree the old-report switch-off date. Run the Responsible AI review if AI is in scope."),
        ("Stage 5", "Name the owner and the support model. Agree release route. Release from a pipeline from day one. Name consumers."),
        ("Stage 6", "Make jobs safe to rerun. Move secrets to a store. Switch on data quality checks. Tag resources. Document schedules and dependencies."),
        ("Stage 7", "Alerts for failure, freshness and quality. Reconciliation signed. Load and performance tests. Security review. Role tests. Test acceptance."),
        ("Stage 8", "Runbook followed cold by someone else. Restore tested. Rollback rehearsed. Failure drill. Cut-over plan. Hypercare plan. Collect sign-offs."),
        ("Gate", "Run the whole checklist. Decide.")]

WRONG = [("Gate theatre", "Signatures with no evidence.", "Problems reach production", "Evidence for each check; spot-check by a reviewer"),
         ("Gate at the very end", "Nobody sees the checklist until the week before.", "A rush, then a delay", "Publish at stage 2; run pre-flight at stage 5 onwards"),
         ("Checklist bloat", "Every incident adds a check and none are removed.", "People stop reading it", "Review the spec each quarter; remove what never fails"),
         ("One size for every project", "The same 105 checks for a small report.", "Resentment and skipped checks", "'Applies when' rules; tiers by risk"),
         ("Waivers without expiry", "'We will do it after go-live.'", "It never happens", "Exceptions have an owner and an expiry"),
         ("Automating what you do not understand", "A check passes because it tests the wrong thing.", "False confidence", "Run each automated check against a known failure"),
         ("Gates owned by nobody", "No one can say stop.", "A gate that never stops anything", "Name the decider, and protect them"),
         ("Only the build team ticks", "Operations see it first at go-live.", "Operations reject it late", "Operations own their categories from stage 5")]

QA = [("What is the difference between a checklist and checks as code?", "A checklist is a document that people read and tick. Checks as code are written in a structured, versioned form, so they can be applied the same way every time, reported on, and partly automated. The thinking is the same. The discipline is higher."),
      ("Do all checks need to be automated?", "No. Many are judgements. The point of 'as code' is that each check is stated precisely, has evidence, an owner and a severity, and lives with the project, whether a person or a script verifies it."),
      ("Why one Ops gate instead of many?", "Operations meet the project once, at the end, and decide whether to take it. A single published gate means they know what they will test, and the project knows what to prepare, months ahead."),
      ("Is 105 checks too many?", "Not as a menu. Each category has a few checks and an owner, and the 'applies when' rules remove many. Use the categories to see where you stand, and open the checks only where you are weak."),
      ("How does this connect to spec-driven development?", "A spec says what must be true. Checks are derived from the spec, and run against evidence. When the spec changes, the checks change with it, and the gate report shows which parts of the spec are proven.")]


def d_docvscode():
    b = R(10, 20, 470, 180, ROSE, [], 15)
    b += T(245, 50, "A document", 19) + T(245, 80, "written once", 15) + T(245, 104, "read at the end", 15) + T(245, 128, "ticked by a person", 15) + T(245, 152, "copies drift", 15) + T(245, 184, "what is true is unknown", 15)
    b += R(520, 20, 470, 180, MINT, [], 15)
    b += T(755, 50, "A check as code", 19) + T(755, 80, "versioned with the project", 15) + T(755, 104, "run at every change", 15) + T(755, 128, "evidence attached", 15) + T(755, 152, "one source, visible differences", 15) + T(755, 184, "what is proven is counted", 15)
    b += DE.AR(484, 110, 516, 110)
    return DE.S(1000, 220, b, "A document is written once, read at the end, ticked by a person, copies drift, and what is true is unknown. A check as code is versioned with the project, run at every change, has evidence attached, has one source with visible differences, and what is proven is counted.")


def d_spec():
    b = R(10, 40, 180, 90, LAV, ["The spec", "what must be true"], 17) + DE.AR(192, 85, 228, 85) + R(230, 40, 180, 90, BLUE, ["The checks", "derived from the spec"], 17)
    b += DE.AR(412, 85, 448, 85) + R(450, 40, 180, 90, BUTTER, ["The evidence", "documents, logs, tests"], 17) + DE.AR(632, 85, 668, 85) + R(670, 40, 150, 90, MINT, ["The report", "proven, failed, unknown"], 15)
    b += DE.AR(822, 85, 858, 85) + R(860, 40, 130, 90, "#FFF1C2", ["The gate", "pass, conditional,", "not yet"], 15, sw=2.5)
    b += '<path d="M925,132 C925,200 100,200 100,132" stroke="#111" stroke-width="1.5" fill="none" stroke-dasharray="5 4" marker-end="url(#dta)"/>' + T(500, 195, "what the gate teaches us updates the spec, and so the checks", 14)
    return DE.S(1000, 220, b, "Spec-driven gates: the spec says what must be true, checks are derived from it, evidence is collected, a report shows what is proven, failed or unknown, and the gate decides pass, conditional pass or not yet. Lessons update the spec.")


def d_gates():
    b = ""
    names = [("1 to 2", "Requirements"), ("4", "Discovery"), ("4", "Architecture"), ("5", "Build ready"), ("7", "Test"), ("8 to 9", "OPS GATE"), ("10", "Close")]
    for i, (st, n) in enumerate(names):
        x = 14 + i * 140
        ops = n == "OPS GATE"
        b += R(x, 40 if not ops else 20, 126, 80 if not ops else 120, "#FFF1C2" if ops else [BLUE, BUTTER, BUTTER, GREY, MINT, "#FFF1C2", LAV][i], [n, f"stage {st}"], 16 if not ops else 20, sw=3.5 if ops else 1.5)
        if i < 6:
            b += DE.AR(x + 128, 80, x + 138, 80)
    b += T(500, 176, "Each gate is a spec of checks, published in advance. The Ops gate is the final one before production.", 15)
    return DE.S(1000, 196, b, "Seven gates along the project lifecycle: requirements, discovery, architecture, build readiness, test, the Ops gate before production, and project close. The Ops gate is the final gate before production.")


def ops_html():
    cats = {c: (n, d) for c, n, d in CATS}
    items = []
    count = {}
    for c, chk, ev, ow, sv, vf, st in CHECKS:
        count[c] = count.get(c, 0) + 1
        items.append(dict(id=f"OPS-{c}-{count[c]:02d}", category=cats[c][0], check=chk, evidence=ev, owner=ow, severity=sv, verify=vf, prepare_by_stage=st))
    tiles = ""
    secs = ""
    for c, n, d in CATS:
        its = [i for i in items if i["id"].startswith(f"OPS-{c}-")]
        blockers = sum(1 for i in its if i["severity"] == "blocker")
        owners = sorted({i["owner"] for i in its})
        tiles += f'<a class="ctile" href="#cat-{c}"><b>{E(n)}</b><span>{E(d)}</span><i>{len(its)} checks · {blockers} blockers</i></a>'
        rows = "".join(f'<tr class="chk" data-owner="{E(i["owner"])}" data-sev="{i["severity"]}" data-vf="{i["verify"]}"><td><b>{i["id"]}</b></td><td>{E(i["check"])}</td><td>{E(i["evidence"])}</td><td>{E(i["owner"])}</td><td><span class="sv {i["severity"]}">{i["severity"]}</span></td><td>{i["verify"]}</td><td>{i["prepare_by_stage"]}</td></tr>' for i in its)
        cond = ' <span class="tag">only when AI or agents are in scope</span>' if c == "AIO" else ""
        secs += (f'<details class="cat" id="cat-{c}" open><summary><b>{E(n)}</b> {cond}<span class="note"> · {len(its)} checks · owners: {E(", ".join(owners))}</span></summary>'
                 f'<div class="tw"><table class="t"><tr><th>ID</th><th>Check</th><th>Evidence</th><th>Owner</th><th>Severity</th><th>How verified</th><th>Prepare by stage</th></tr>{rows}</table></div></details>')
    return tiles, secs, items


def page():
    tiles, secs, items = ops_html()
    nb = sum(1 for i in items if i["severity"] == "blocker")
    dvc = table(["", "A document checklist", "A check as code"], [[f"<b>{E(a)}</b>", E(b), E(c)] for a, b, c in DOC_VS_CODE])
    fl = table(["Field", "What it holds"], [[f"<code>{E(a)}</code>", E(b)] for a, b in FIELDS])
    au = table(["Level", "What it means", "Example"], [[f"<b>{E(a)}</b>", E(b), E(c)] for a, b, c in AUTOMATION])
    gt = table(["Gate", "Stage", "The question", "Decides", "What it checks", "Status"], [[f"<b>{E(a)}</b>", E(b), E(c), E(d), E(e), E(f)] for a, b, c, d, e, f in GATES])
    rs = "<ol>" + "".join(f"<li><b>{E(a)}.</b> {E(b)}</li>" for a, b in RUN_STEPS) + "</ol>"
    dc = table(["Decision", "When", "What happens"], [[f"<b>{E(a)}</b>", E(b), E(c)] for a, b, c in DECISIONS])
    pp = table(["When", "Prepare"], [[f"<b>{E(a)}</b>", E(b)] for a, b in PREP])
    wr = table(["What goes wrong", "How it happens", "What it costs", "Prevention"], [[f"<b>{E(a)}</b>", E(b), E(c), E(d)] for a, b, c, d in WRONG])
    css = """<style>
  .tf .ctiles { display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:10px; margin:12px 0; }
  .tf .ctile { border:var(--line); border-radius:var(--wob); padding:8px 12px; background:#fff; text-decoration:none; color:inherit; display:block; }
  .tf .ctile b { display:block; font-family:var(--hand); font-size:19px; } .tf .ctile span { display:block; font-size:13.5px; color:var(--muted); } .tf .ctile i { font-style:normal; font-size:13px; font-weight:700; }
  .tf details.cat { border:var(--line); border-radius:12px; margin:10px 0; background:#fff; } .tf details.cat > summary { cursor:pointer; padding:9px 14px; list-style:none; } .tf details.cat > summary::-webkit-details-marker { display:none; }
  .tf details.cat > summary::before { content:"›"; display:inline-block; margin-right:8px; } .tf details.cat[open] > summary::before { transform:rotate(90deg); }
  .tf details.cat .tw { padding:0 10px 10px; } .tf .sv { font-size:12px; font-weight:700; border:1.5px solid var(--ink); border-radius:999px; padding:0 8px; background:#fff; }
  .tf .sv.blocker { background:#f8d6d6; } .tf .sv.major { background:#fdebc8; } .tf .sv.minor { background:#e6f2e6; }
  .tf .filters { display:flex; flex-wrap:wrap; gap:8px 10px; align-items:center; margin:12px 0; font-size:14.5px; } .tf .filters select, .tf .filters button { font:inherit; font-size:14px; border:1.5px solid var(--ink); border-radius:10px; padding:4px 10px; background:#fff; }
  .tf pre.yaml { border:var(--line); border-radius:var(--wob); background:#fff; padding:12px 16px; overflow-x:auto; font-size:13.5px; line-height:1.45; }
</style>"""
    js = """<script>
const OPS = %s;
function show(){const o=document.getElementById('f-owner').value,s=document.getElementById('f-sev').value,v=document.getElementById('f-vf').value;
  document.querySelectorAll('tr.chk').forEach(r=>{r.style.display=((!o||r.dataset.owner===o)&&(!s||r.dataset.sev===s)&&(!v||r.dataset.vf===v))?'':'none'});
  document.querySelectorAll('details.cat').forEach(d=>{d.style.display=[...d.querySelectorAll('tr.chk')].some(r=>r.style.display!=='none')?'':'none'});}
['f-owner','f-sev','f-vf'].forEach(i=>document.getElementById(i).addEventListener('change',show));
function dl(name,type,text){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{type}));a.download=name;a.click();}
document.getElementById('d-json').addEventListener('click',()=>dl('ops-gate.json','application/json',JSON.stringify(OPS,null,2)));
document.getElementById('d-csv').addEventListener('click',()=>{const c=Object.keys(OPS[0]);const e=v=>'"'+String(v).replace(/"/g,'""')+'"';dl('ops-gate.csv','text/csv',[c.join(',')].concat(OPS.map(i=>c.map(k=>e(i[k])).join(','))).join('\\n'));});
</script>""" % json.dumps(items, ensure_ascii=False)
    owners = sorted({i["owner"] for i in items})
    opts = lambda xs: "".join(f'<option value="{E(x)}">{E(x)}</option>' for x in xs)
    toc = "".join(f'<li><a href="#{a}">{b}</a></li>' for a, b in [("idea", "Document or code"), ("spec", "Spec-driven"), ("anatomy", "Anatomy of a check"), ("gates", "The gates"), ("run", "How a gate runs"),
                                                                   ("ops", "The Ops gate checklist"), ("prepare", "How to prepare"), ("wrong", "What can go wrong"), ("faq", "FAQ")])
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › Checks as code</p>
<p class="eyebrow" style="margin-top:22px">Learn · spec-driven delivery · free guide</p>
<h1>Checks as code, and the Ops gate</h1>
<p class="lede">A checklist in a document tells people what should be true. A check as code states it precisely, attaches evidence, and can be run the same way on every project. This page explains the idea, shows how discovery, architecture and operations gates can all be built from it, and gives a detailed Ops gate checklist, in categories, so a project knows what it will be tested on before it starts.</p>
<div class="tf">{css}<nav class="toc"><b>On this page</b><ol>{toc}</ol></nav>
<section id="idea"><p class="eyebrow">Teach first</p><h2>A document says. A check proves.</h2>
<p>Every project has a checklist somewhere: a sheet of things to confirm before go-live. Most are written once, copied from the last project, ticked by whoever is in a hurry, and never read again. The idea of a check as code is to write the same expectations in a precise, structured form, keep them with the project, and attach evidence to each.</p>
{fig(d_docvscode(), "The same expectations, written two ways. Only the second can be run, counted and trusted.")}{dvc}
<div class="box"><b>In one line:</b> checks as code do not remove judgement. They make each judgement explicit, owned, evidenced and repeatable.</div></section>
<section id="spec"><p class="eyebrow">Spec-driven</p><h2>The spec comes first. The checks follow.</h2>
<p>In spec-driven development, a specification says what must be true, and everything else is derived from it. The same works for gates. The spec of a good discovery, a good design or a ready-to-run system is written once. The checks come from it. A gate runs the checks against evidence, and reports what is proven, failed and not yet known.</p>
{fig(d_spec(), "One spec, many gates. A gate is a view of the spec, not a new document.")}
<p>The wider idea is on the {Lx('/leaders/spec-driven/', 'spec-driven development')} pages, and for data platforms in {Lx('/leaders/spec-driven/data-platform/', 'spec-driven data platforms')}.</p></section>
<section id="anatomy"><p class="eyebrow">Anatomy</p><h2>What one check looks like</h2>
<p>The project review that this site already publishes works this way: {N_CATALOG} checks, each a small structured record, filterable by stage and role (see the {Lx('/learn/technical-anchor/project-review/checks/', 'checks')} and the {L(REPO, 'open repository')}). The Ops gate uses the same fields.</p>
<pre class="yaml">{E(YAML)}</pre>{fl}
<h3 style="margin-top:18px">Four levels of verification</h3>{au}</section>
<section id="gates"><p class="eyebrow">The gates</p><h2>Each gate is a spec of checks</h2>
{fig(d_gates(), "Seven gates. The first two are largely covered by the existing project review. The Ops gate is written out in full below.")}{gt}
<p class="note">Requirement, discovery, architecture and close are views onto the same spec, filtered by stage and role. The {Lx('/learn/technical-anchor/project-review/', 'project review')} already covers much of the first four. See also {L(BASE + 'reviews/', 'Reviews and sign-offs')}.</p></section>
<section id="run"><p class="eyebrow">How a gate runs</p><h2>No surprises at the gate</h2>{rs}<h3 style="margin-top:18px">Three outcomes</h3>{dc}</section>
<section id="ops"><p class="eyebrow">The Ops gate</p><h2>The final gate before production: {len(items)} checks in 14 categories</h2>
<p><b>The question:</b> can operations run this at 3 a.m. without the builders? Operations meet the project once, at the end. If the project knows what they will test, it can prepare for months. Start with the categories. Open the checks only where you are weak.</p>
<div class="ctiles">{tiles}</div>
<p>{nb} of the {len(items)} checks are blockers. The Ops gate passes when no blocker is open and every category has a named owner who has signed. Checks marked 'applies when AI or agents are in scope' can be skipped otherwise.</p>
<div class="filters"><label>Owner <select id="f-owner"><option value="">Any</option>{opts(owners)}</select></label><label>Severity <select id="f-sev"><option value="">Any</option>{opts(["blocker", "major", "minor"])}</select></label>
<label>How verified <select id="f-vf"><option value="">Any</option>{opts(["manual", "semi-automated", "automated", "drill"])}</select></label><button id="d-csv" type="button">Download CSV</button><button id="d-json" type="button">Download JSON</button></div>
{secs}
<p class="note">This is a starting spec. Trim it with 'applies when', add what your organisation needs, and keep it in the project's repository.</p></section>
<section id="prepare"><p class="eyebrow">Prepare</p><h2>Do the work early. The gate is the last check, not the first</h2>{pp}</section>
<section id="wrong"><p class="eyebrow">What can go wrong</p><h2>Eight ways gates fail</h2>{wr}</section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(QA)}</section>
<section id="next"><p class="eyebrow">Go further</p><h2>Related pages</h2><ul><li>{Lx('/learn/technical-anchor/project-review/checks/', 'The project review checks')}</li><li>{Lx('/learn/technical-anchor/discovery/', 'Discovery')}</li><li>{L(BASE + 'reviews/', 'Reviews and sign-offs')}</li>
<li>{L(BASE + 'backlog/', 'The corpus backlog')}</li><li>{Lx('/learn/responsible-ai/', 'Responsible AI, explained')}</li><li>{Lx('/learn/ai-ops-dashboard/', 'AI ops dashboard: sample views')}</li></ul></section>
{js}</div>"""
    title = "Checks as code, and the Ops gate"
    desc = ("Checks as code versus checklist documents: spec-driven gates for discovery, architecture and operations, how a gate runs, and a detailed Ops gate checklist "
            "of about 105 checks in 14 categories that a project must pass before production.")
    return DE.page_shell(title, desc, URL_PATH, body, [("Learn", "/learn/"), ("Checks as code", URL_PATH)], QA)


def main():
    DE.write(URL_PATH, page())


if __name__ == "__main__":
    main()
