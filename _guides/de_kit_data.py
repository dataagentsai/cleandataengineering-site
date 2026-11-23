"""Content of the data project starter kit: templates and skills. Read by de_kit.py.

Plain words, no code. Grounded in the pages of /how-we-work/data-essentials/ and /how-we-work/estimation/.
"""

STAGES = "1 Requirement received, 2 Rough estimate, 3 Discovery, 4 Discovery sign-off (gate), 5 MVP 1 starts, 6 Build, 7 Test, 8 Deploy, 9 Production sign-off (gate), 10 Project sign-off (gate)"

FOLDERS = [
    ("00-project", "The one-pager, the cast and stakeholder map, the glossary."),
    ("01-discovery", "The source register, source questionnaires, interview notes."),
    ("02-specs", "Specs, metric definitions, source-to-target mapping."),
    ("03-backlog", "The Agile backlog and the estimate."),
    ("04-run", "Weekly status reports, the risk and dependency register, the decision log, meeting notes."),
    ("05-test", "The test and reconciliation plan, and the results."),
    ("06-reviews", "Review findings and sign-off records."),
    ("07-handover", "The consumer register, the runbook, the retrospective."),
]

HEAD = "Project: ______  ·  Owner of this file: ______  ·  Last updated: ____-__-__\n"

# file name, title, folder it is copied to, owner seat, body
TEMPLATES = [
    ("project-one-pager.md", "Project one-pager", "00-project", "PM", """
## The decision this project supports
Which decision will change because of this project, and who makes it?

## The questions the data must answer
1.
2.
3.

## People
| Role | Name | What they decide or own |
|---|---|---|
| Sponsor | | Go, change or stop at each gate |
| Business owner | | The definitions and the acceptance |
| Business analyst | | The question and the acceptance checks |
| Tech Anchor | | The technical shape, end to end |
| Project manager | | The plan, the risks, the gates |

## Scope
| In | Out | Not decided yet |
|---|---|---|
| | | |

## Sources and what people will use
- Sources (systems we do not own):
- What people will use at the end (reports, apps, extracts):
- The old report that will be switched off, and when:

## Gates
| Gate | Stage | Planned date | Who signs |
|---|---|---|---|
| Discovery sign-off | 4 | | |
| Production sign-off | 9 | | |
| Project sign-off | 10 | | |

## Assumptions
List every assumption. Mark the one that would hurt most if wrong.

Done when: the business owner has read it and agrees with the decision and the questions.
"""),
    ("cast-and-stakeholder-map.md", "Cast and stakeholder map", "00-project", "PM", """
## The cast
One row per person. Groups: Client, Us, Vendors, Platform.

| Group | Role | Name | Owns | We need from them | By when | Who on our side talks to them |
|---|---|---|---|---|---|---|
| Client | Source system owner | | | Access, meaning, notice of changes | | BA |
| Client | Sponsor | | | | | PM |
| Client | Business owner | | | | | BA |
| Client | Finance | | | The figures to match | | BA |
| Client | Security and privacy | | | Approvals | | Tech Anchor |
| Client | Operations and support | | | To run it after go-live | | Tech Anchor |
| Client | End users | | | Acceptance | | BA |

Who is missing? Write the role here even if there is no name yet:

## Stakeholder grid
Place each name in one box.

| | Low interest | High interest |
|---|---|---|
| **High influence** | Keep satisfied: | Manage closely: |
| **Low influence** | Monitor: | Keep informed: |

## Who hears what
| Who | What | How often | From whom | How |
|---|---|---|---|---|
| Sponsor | Weekly status report | Weekly | PM | One page |
| | | | | |

Done when: every metric has a business owner by name, and every source has an owner by name.
"""),
    ("glossary.md", "Glossary", "00-project", "BA", """
One meaning per word. If two people use a word two ways, write both, and name who decides.

| Word | Meaning in this project | Owner | Also called | Not the same as | Agreed on |
|---|---|---|---|---|---|
| Active customer | | | | | |
| Revenue | | | | | |
| | | | | | |

## Words used two ways (open)
| Word | Meaning A (who) | Meaning B (who) | Who decides | By when |
|---|---|---|---|---|
| | | | | |

Done when: no word in a spec is missing here, and the open list is empty or dated.
"""),
    ("source-register.md", "Source register", "01-discovery", "BA", """
One row per source system. We do not own these systems, so the owner and the unknowns matter most.

| ID | Source | What it holds | Owner (name) | Expert (name) | Access status | How data comes out | How often | Size: small, medium, large, very large | Biggest unknown | Questionnaire done? |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | | | | | Requested on ____ | | | | | No |

Size signals:
- Small: a few tables, clear keys, a reliable change column, documents exist, the owner answers within a day.
- Medium: ten to thirty tables, some joins to learn, deletes need care, some documents, the owner is busy.
- Large: many tables or a packaged application, codes that need a lookup, no change column, history in odd formats.
- Very large: several systems feeding one model, conflicting definitions, no reachable owner. Split it.

Done when: every source has an owner by name and an access request with a date.
"""),
    ("source-questionnaire.md", "Source questionnaire", "01-discovery", "BA", """
Source: ______  ·  Answered by: ______  ·  Date: ____-__-__

Write UNKNOWN where nobody could answer, and who to ask next.

## 1. What it is and who owns it
| Question | Answer | Who said so |
|---|---|---|
| What business process does this system run? | | |
| Who owns the system? Who knows the data best? | | |
| Is there documentation? Where? | | |
| Is a change to the system planned in the next year? | | |

## 2. What the data means
| Question | Answer | Who said so |
|---|---|---|
| Which tables or files matter for our questions? | | |
| What identifies one record (the key)? | | |
| Which fields can nobody explain? | | |
| Which codes need a lookup list? Where is the list? | | |

## 3. How it changes
| Question | Answer | Who said so |
|---|---|---|
| How do we know a record changed? Is there a changed-on date we can trust? | | |
| Are records deleted? Can we see that they were? | | |
| Are old records corrected later? How late? | | |
| How much history is kept, and in what form? | | |

## 4. How we get it
| Question | Answer | Who said so |
|---|---|---|
| How can data come out (database copy, file, interface)? | | |
| When can we read it without slowing the system? | | |
| How large is it, and how fast does it grow? | | |
| What access and approvals are needed, from whom, how long do they take? | | |
| Is there personal or sensitive data? Which fields? | | |

## 5. How we will know we have it right
| Question | Answer | Who said so |
|---|---|---|
| Which existing report or figure should our numbers match? | | |
| Who will tell us when the system changes? | | |
| Who do we call when the data is late or wrong? | | |

## Unknowns to chase
| Unknown | Who could answer | Asked on | Answer by |
|---|---|---|---|
| | | | |

Done when: we have seen a real sample, and every UNKNOWN has a name and a date.
"""),
    ("metric-definition.md", "Metric definition sheet", "02-specs", "BA", """
One sheet per number. One definition, one owner.

| Field | Value |
|---|---|
| Name | |
| The question it answers | |
| Formula, in words | |
| Formula, exact | |
| Grain (one row is...) | |
| Included | |
| Excluded | |
| Time rule (which date, which calendar, which time zone) | |
| Business owner (name) | |
| Source systems and fields | |
| The figure it must match (report, period, value) | |
| Tolerance agreed | |
| Who signs that it matches | |
| Also called | |
| Not the same as | |

## Worked example
Take one real period. Show the inputs and the result, by hand.

## Open questions
| Question | Who decides | By when |
|---|---|---|
| | | |

Done when: the owner signs the definition and the worked example matches the trusted figure within tolerance.
"""),
    ("spec.md", "Spec", "02-specs", "BA", """
Spec ID: SPEC-___  ·  Status: Draft / In review / Agreed  ·  Agreed by: ______ on ____-__-__

Write what must be true, not how to build it. The build, the test and the review all read this file.

## 1. Purpose
Which question does this answer, for whom, and what will they do with it?

## 2. In and out
| In | Out |
|---|---|
| | |

## 3. Inputs
| Source | What we take | Owner | Known problems |
|---|---|---|---|
| | | | |

## 4. What must be true
Each line is a check a tester can run on data. If it cannot be tested, it is a wish: rewrite it.

| ID | Check | Example with real values | How it is tested | Who accepts |
|---|---|---|---|---|
| AC-1 | Total sales for March 2026 equal the finance report, within 0.5 percent | | Compare with finance report F-12 | Finance |
| AC-2 | Every order has exactly one customer | | Count orders with none or more than one | BA |
| AC-3 | Data is ready by 07:00 every working day | | Check load time for ten days | Operations |
| AC-4 | | | | |

## 5. Definitions used
Link each number to its metric definition sheet. Link each word to the glossary.

## 6. What happens when things go wrong
| Case | What must happen |
|---|---|
| The source is late | |
| A record is corrected after we loaded it | |
| A record breaks a rule | |

## 7. Who can see it
Who may see which data. Name any personal or sensitive fields.

## 8. Open questions
| Question | Who decides | By when |
|---|---|---|
| | | |

## 9. Changes to this spec
| Date | Change | Why | Agreed by |
|---|---|---|---|
| | | | |

Done when: every line in section 4 is a check on data, each has someone who accepts it, and section 8 is empty or dated.
"""),
    ("source-to-target-mapping.md", "Source-to-target mapping", "02-specs", "BA", """
For spec: SPEC-___

| Target field | Meaning | Source system | Source table or file | Source field | Rule, in words | Example in | Example out | Agreed by |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

## Gaps
| Target field with no source | What we will do | Who decides |
|---|---|---|
| | | |

## Rules still to be agreed
| Rule | Options | Who decides | By when |
|---|---|---|---|
| | | | |

Done when: every target field has a source or a decision, and every rule has a name against it.
"""),
    ("agile-backlog.md", "Agile backlog for a data project", "03-backlog", "PM", """
A data backlog is cut in thin slices. A slice runs from one source to one trusted number that a person checks. Do not plan layer by layer.

The same backlog is in `agile-backlog.csv`, to open as a sheet or load into your tracking tool.

## Kinds of item
| Kind | What it is | Example |
|---|---|---|
| Spike | Learn something risky in a fixed time. The output is an answer. | Can we reach the billing system from our environment? |
| Slice | A thin piece through every layer, for one source, ending in a number a person checks. | Daily sales by store, from the orders system, to one report. |
| Run | What keeps it alive. | Alert the on-call person if the nightly load is late. |
| Fix or debt | Works today, will hurt later. Small, visible and sized. | Replace a manual file upload with the automatic load. |

## Ready: an item can start when
- [ ] The source and its owner are named.
- [ ] We have seen a real sample of the data.
- [ ] Access to the source works from our environment.
- [ ] The business owner of each metric is named.
- [ ] Acceptance criteria are written as checks on data, not wishes.

## Done: an item is finished when
- [ ] Tested against the source: counts and totals match.
- [ ] Reconciled to a figure the business already trusts.
- [ ] Quality checks run daily and alert a named person.
- [ ] Deployed to the test environment by the pipeline, not by hand.
- [ ] Documented: where it came from and what it means.
- [ ] Shown to the business owner, who accepts it.

## The slices
Order by risk. Slice 0 is the spikes: test the most dangerous belief first.

| Slice | What it proves | Sources | The number a person checks | Who checks | Target date |
|---|---|---|---|---|---|
| 0 Spikes | The beliefs that could stop the project hold | | | | |
| 1 | One source to one trusted number, end to end | | | | |
| 2 | Widen: | | | | |
| 3 | Widen: | | | | |

## The items
Pull items from the corpus backlog (cleandataengineering.ai/how-we-work/data-essentials/backlog/). Keep its ID so the acceptance checks come with it.

| ID | Slice | Kind | Story | Corpus item | Seat | Stage | Size | Ready? | Acceptance checks | Evidence | Owner | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B-001 | 0 | Spike | Get one real extract and compare it with the description we were given | | BA | 3 | S | Yes | We can open it; it matches the description | Sample file and notes | | To do |
| B-002 | 0 | Spike | Reach the source from the build environment with the right permissions | | PM | 3 | S | No | A test read works from our environment | Screenshot or log | | To do |
| B-003 | 0 | Spike | Rebuild one figure finance already knows | | BA | 3 | M | No | Within the agreed tolerance | Worked example | | To do |
| B-004 | 1 | Slice | Daily sales by store, from the orders system, to one report | | Tech Anchor | 6 | L | No | Matches the finance report within tolerance | Reconciliation result | | To do |
| B-005 | 1 | Run | Alert a named person if the nightly load is late | | Tech Anchor | 6 | S | No | A test failure reaches the named person | Alert received | | To do |

Sizes: S, M, L. Give days as a range in the estimate sheet, not here.

## Each sprint
| Sprint | Goal: what will be proved | Items | Demo to whom, with which real numbers |
|---|---|---|---|
| 1 | | | |

Done when: slice 1 ends in a number a named person will check, and every item in the next sprint is Ready.
"""),
    ("estimate-sheet.md", "Estimate sheet", "03-backlog", "Tech Anchor", """
Estimate version: __  ·  Made by (the people who will build it): ______  ·  Date: ____-__-__  ·  Will be re-estimated on: ____-__-__ (after: ______)

## 1. What we counted
| What | Count | Notes |
|---|---|---|
| Source systems | | |
| Tables or files | | |
| Metrics | | |
| Reports or other things people use | | |
| Environments to set up | | |
| Approvals needed (access, security, privacy) | | |
| Years of history to load | | |

## 2. Each source, sized
| Source | Size | The signals that put it there | Low (person-weeks) | High (person-weeks) |
|---|---|---|---|---|
| | | | | |

## 3. Effort, as a range
The lines marked * are the ones usually forgotten. Keep them on their own lines.

| Line | Low (days) | High (days) | Assumption behind it |
|---|---|---|---|
| Discovery: what the source data means * | | | |
| Access and environment set-up (effort only) * | | | |
| Getting the data in | | | |
| Cleaning, with history | | | |
| Modelling and metric definitions | | | |
| Tests and checks * | | | |
| Reconciling with the trusted figure, and fixing * | | | |
| Loading history * | | | |
| Deploy, monitoring, runbook * | | | |
| Reports and what people use | | | |
| Project management, reviews and sign-offs * | | | |
| Support after go-live (first four weeks) * | | | |
| **Total effort** | | | |

## 4. Waiting, on the calendar (not effort)
| We wait for | From whom | Likely wait | Asked on |
|---|---|---|---|
| Access to the source | | | |
| Security or privacy approval | | | |
| Answers from the source owner | | | |
| Sign-off at each gate | | | |

## 5. Calendar
Team size: __. Effort range: __ to __ days. Waiting: __ to __ weeks. Likely end date: between ____ and ____.

## 6. Assumptions
Number them. Mark the one that moves the estimate most if wrong.

## 7. Not included
Say it here so nobody assumes it.

## 8. What will narrow the range
The event after which we re-estimate (usually the first source running end to end).

Done when: it is a range, the waits are apart from the effort, reconciliation is in with a tolerance and a signer, and the builders made it.
"""),
    ("risk-and-dependency-register.md", "Risk and dependency register", "04-run", "PM", """
One page. Review it every week. A risk has an early sign; when you see the sign, act.

Themes: A We don't know the data · B We don't have the people · C We don't agree · D We don't prove it · E We don't plan for reality · F We don't run and adopt it

## Risks
| ID | Risk | Theme | Early sign to watch | Seen yet? | Effect if it happens | What we do now | Owner | Answer needed by | Status |
|---|---|---|---|---|---|---|---|---|---|
| R-1 | The source owner is not engaged | B | Questions unanswered for more than three days | | Meaning guessed, access late | | | | Open |
| R-2 | No figure agreed to reconcile against | D | Nobody can name the report to match | | It runs, it is wrong, nobody checks | | | | Open |

## Dependencies (things we wait for from others)
| ID | We need | From whom (name) | Asked on | Needed by | Blocked since | Escalated to, on |
|---|---|---|---|---|---|---|
| D-1 | Read access to the source | | | | | |

Rule: escalate at day three of a block, not day thirty.

## The belief that could stop the project
| Belief | How we test it | By when | Result | Go, change or stop |
|---|---|---|---|---|
| | | | | |

Done when: every row has a name and a date.
"""),
    ("decision-log.md", "Decision log", "04-run", "PM", """
One row per decision. Never edit an old row: add a new one that replaces it.

| ID | Date | Decision | Why | Options we rejected | Decided by (name) | Who was consulted | Affects (spec, backlog item, estimate) | Replaces |
|---|---|---|---|---|---|---|---|---|
| DEC-001 | | | | | | | | |

Done when: anyone who was not in the room can read what was decided, by whom and why.
"""),
    ("weekly-status-report.md", "Weekly status report", "04-run", "PM", """
Week ending: ____-__-__  ·  Stage: __ of 10  ·  Next gate: ______ on ____-__-__  ·  Overall: On track / At risk / Off track

The same five headings every week. No 'percent complete'.

## 1. Proved this week
What now works end to end, with a number someone checked. Name the person who checked.

## 2. Next
What we will prove next, in one or two lines.

## 3. Risks, with a date
| Risk | Owner | Answer needed by |
|---|---|---|
| | | |

## 4. Waiting on
| Who | For what | Since |
|---|---|---|
| | | |

## 5. Decisions needed
| What we need from you | By when | What happens if it is late |
|---|---|---|
| | | |

## Effort and calendar
| | Estimated (range) | Used so far | Now expected (range) |
|---|---|---|---|
| Effort, days | | | |
| End date | | | |

Done when: a sponsor can read it in two minutes and knows what to decide.
"""),
    ("meeting-notes.md", "Meeting notes", "04-run", "Everyone", """
Meeting: ______  ·  Date: ____-__-__  ·  Present: ______  ·  Notes by: ______

## Why we met
One line.

## What we learnt
Facts only. Say who said each one.

## Decisions
Copy each one to the decision log.

| Decision | Decided by | Why |
|---|---|---|
| | | |

## Actions
| Action | Owner (one name) | By when |
|---|---|---|
| | | |

## Open questions
| Question | Who could answer | By when |
|---|---|---|
| | | |

Done when: every action has one name and one date, and the notes are in git the same day.
"""),
    ("test-and-reconciliation-plan.md", "Test and reconciliation plan", "05-test", "Tester", """
For spec: SPEC-___

## 1. The figures we must match
| Number | Trusted figure (report, period, value) | Tolerance | Who signs that it matches |
|---|---|---|---|
| | | | |

## 2. Tests, from the acceptance checks
One row per check in the spec. Test on real data.

| Test | Acceptance check | Data used | Expected | Result | Pass? | Evidence (where it is kept) |
|---|---|---|---|---|---|---|
| T-1 | AC-1 | | | | | |

## 3. Counts, layer by layer
| Step | Records in | Records out | Rejected | Explained? |
|---|---|---|---|---|
| Source to landing | | | | |
| Landing to clean | | | | |
| Clean to model | | | | |

## 4. What happens to bad records
Where they go, who looks at them, how often.

## 5. Acceptance by users
| User (name) | What they test | On real data? | Date | Accepted? |
|---|---|---|---|---|
| | | | | |

## 6. Differences found
| Difference | Size | Cause | Fixed, or accepted by whom |
|---|---|---|---|
| | | | |

Done when: every figure in section 1 matches within tolerance and is signed, on real data.
"""),
    ("review-findings-log.md", "Review checklist and findings log", "06-reviews", "PMO", """
What was reviewed: ______  ·  Stage: __  ·  Reviewer (did not build it): ______  ·  Date: ____-__-__

## How the review ran
- [ ] The pack was sent three working days ahead, with the criteria.
- [ ] Each reviewer read alone and logged findings before the meeting.
- [ ] The meeting discussed findings, not the document page by page.
- [ ] Every finding has a rating, an owner and a date.
- [ ] Someone follows up.

## Ratings
| Rating | Meaning |
|---|---|
| Blocker | Stops the gate. Must be fixed before proceeding. |
| Major | Fix before go-live, or accept in writing with a date. |
| Minor | Fix when convenient. Track it. |
| Note | An observation. No action needed. |

## Findings
| ID | Check that failed | Where (file, section) | What we saw | Rating | Owner | Fix by | Closed on |
|---|---|---|---|---|---|---|---|
| F-1 | | | | | | | |

## Result
Blockers: __  ·  Majors: __  ·  Minors: __  ·  Notes: __

Recommendation to the gate: Go / Go with conditions / Stop.

Done when: every Blocker is closed, or the gate has stopped.
"""),
    ("sign-off-record.md", "Sign-off record", "06-reviews", "PM", """
One record per sign-off. The seven usual ones: Discovery · Design and security · Definitions and model · Test and acceptance · Operational readiness · Production · Project.

| Field | Value |
|---|---|
| Sign-off | |
| Stage | |
| What is signed (in the signer's own words) | |
| Evidence (links to the files) | |
| Review findings still open | |
| Decision | Go / Go with conditions / Stop |
| Conditions, each with an owner and a date | |
| Signed by (one accountable name) | |
| Consulted | |
| Date | |

Rules:
- The signer has read it. Ask them to say what they are signing.
- One person is accountable. Others are consulted.
- 'Conditional' means named conditions, with owners and dates.
- Silence is not a signature.

Done when: the signer can say what they signed and where the evidence is.
"""),
    ("consumer-register.md", "Consumer register", "07-handover", "BA", """
Everyone and everything that uses the result.

| Consumer (person, team or system) | What they use | For which decision | How fresh it must be | How they get it | Owner on their side | Old report it replaces | Switch-off date of the old report | Accepted on |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

## When something changes
Who we tell before a number or a field changes, and how many days ahead.

Done when: every old report has a switch-off date that someone agreed to. Otherwise there are two truths.
"""),
    ("runbook-and-handover.md", "Runbook and handover", "07-handover", "Tech Anchor", """
Written for the person who gets the call, not for the person who built it.

## 1. What runs, and when
| What | When | How long it takes | Ready by |
|---|---|---|---|
| | | | |

## 2. Who is alerted, who fixes
| What can go wrong | How we know (alert) | Who is alerted | First thing to do | If that fails, call | Who tells the users |
|---|---|---|---|---|---|
| The load is late | | | | | |
| A quality check fails | | | | | |
| A number looks wrong | | | | | |
| The source changed | | | | | |

## 3. How to run it again safely
Steps, in order. Say what must not be done.

## 4. Cost
What it costs a month, who watches it, and at what figure they are alerted.

## 5. Access
Who can see what, who approves new access, how access is removed.

## 6. The failure drill
| Date | What we broke on purpose | Was the right person alerted? | Fixed from this runbook alone? | What we changed |
|---|---|---|---|---|
| | | | | |

## 7. Handover
| Item | Handed to (name) | Date | Accepted? |
|---|---|---|---|
| This runbook | | | |
| Open defects and known limits | | | |
| The project repository | | | |

Done when: someone who did not build it has fixed a failure using only this file.
"""),
    ("retrospective.md", "Retrospective", "07-handover", "PM", """
Date: ____-__-__  ·  Covers: sprint / slice / project  ·  Present: ______

## The numbers
| | Estimated (range) | Actual |
|---|---|---|
| Effort, days | | |
| Calendar, weeks | | |
| Waiting, weeks | | |

Copy the actuals to `03-backlog/actuals.md`. The next estimate starts from them.

## Keep
What worked, and why.

## Change
| What hurt | Early sign we missed | Change we propose | To which template, check or skill | Owner |
|---|---|---|---|---|
| | | | | |

Each proposed change goes to the starter kit as a change for review.

Done when: at least one change has been proposed to the starter kit.
"""),
]

BACKLOG_CSV = """ID,Slice,Kind,Story,Corpus item,Seat,Stage,Size,Ready,Acceptance checks,Evidence,Owner,Status
B-001,0,Spike,Get one real extract and compare it with the description we were given,,BA,3,S,Yes,We can open it; it matches the description,Sample file and notes,,To do
B-002,0,Spike,Reach the source from the build environment with the right permissions,,PM,3,S,No,A test read works from our environment,Screenshot or log,,To do
B-003,0,Spike,Rebuild one figure finance already knows,,BA,3,M,No,Within the agreed tolerance,Worked example,,To do
B-004,1,Slice,"Daily sales by store, from the orders system, to one report",,Tech Anchor,6,L,No,Matches the finance report within tolerance,Reconciliation result,,To do
B-005,1,Run,Alert a named person if the nightly load is late,,Tech Anchor,6,S,No,A test failure reaches the named person,Alert received,,To do
"""

RULES = """## Rules for every skill
- Use only what is in the files you were given. Do not invent a fact, a name, a number or a date.
- Where something is missing, write `UNKNOWN` and who could answer.
- After each statement taken from a file, say which file it came from.
- Use the words in `00-project/glossary.md`. If a word is used two ways, say so.
- Write in plain words, for people who do not write code.
- The result is a draft. End with the line: `Draft by an AI assistant. To be checked by: ______`.
- Client data, personal data and secrets stay out of any tool the client has not approved.
"""

# slug, name, for, when to use (description), you give it, steps, output, template or None, checks before hand-over, built in session
SKILLS = [
    ("data-project-estimator", "Data project estimator", "Tech Anchor, PM, delivery manager",
     "Estimates a data project as an effort range with assumptions, with waiting time kept apart. Use when someone asks how long or how much a data project, a new source or a change will take.",
     ["The scope: sources, tables or files, metrics, reports, environments, approvals, years of history.", "`01-discovery/source-register.md`, if it exists.", "`03-backlog/actuals.md` from past projects, if it exists.", "What is not known yet."],
     ["Count what can be counted. Fill section 1 of the estimate sheet. If a count is missing, ask for it; do not guess.",
      "Size each source as small, medium, large or very large, using the signals in `rates.md`. Say which signals you used.",
      "Fill every effort line, including the lines marked as usually forgotten. Give a low and a high figure and the assumption behind each.",
      "If past actuals exist, compare. Say where this estimate is lower than what similar work really took.",
      "List the waits (access, approvals, answers, sign-offs) in section 4 as calendar time. Never add them to effort.",
      "Give the calendar range from team size, effort and waits.",
      "Number the assumptions. Mark the one that moves the estimate most. Say what is not included.",
      "Say which event will narrow the range, and the date to re-estimate.",
      "Ask the five questions in `rates.md` and report any that fail."],
     "A filled estimate sheet saved as `03-backlog/estimate.md`, and three lines on top: the range, the biggest assumption, the re-estimate date.",
     "estimate-sheet.md",
     ["It is a range, never one number.", "The line for understanding the source data is bigger than the line for getting the data in.", "Waiting is shown apart from effort.", "Reconciliation is in, with a tolerance and a signer.", "The people who will build it have seen it."], 24),
    ("project-review", "Project review", "PMO, delivery manager, Tech Anchor",
     "Reviews a data project's documents against the checks for its stage and rates each finding. Use before a gate, when taking over a project, or when a project feels off.",
     ["The project repository, or the documents for one gate.", "The stage the project is at (1 to 10)."],
     ["Confirm the stage. If the documents disagree about the stage, that is the first finding.",
      "Read `checks.md`. Take the checks for this stage and every earlier stage.",
      "For each check, look for the evidence in the files. Quote the file and section. If there is none, the check fails.",
      "Rate each failed check as Blocker, Major, Minor or Note, using the meanings in the findings log.",
      "Look for contradictions between files: two definitions of one number, a date in the plan that the status report no longer supports, a risk with no owner.",
      "Match what you found to the six failure themes, and name the early signs that are showing.",
      "Recommend go, go with conditions, or stop. Give the conditions with an owner and a date left blank for people to fill."],
     "A filled findings log saved as `06-reviews/review-stage-N.md`, with the five most important findings on top.",
     "review-findings-log.md",
     ["Every finding names the file it came from, or says no file exists.", "No finding is rated on opinion alone.", "The reviewer named on the log is a person who did not build it."], 25),
    ("backlog-builder", "Backlog builder", "PM, BA, product owner",
     "Builds an Agile backlog for a data project in thin slices, from the corpus backlog. Use at the start of a project or when a new source or report is added.",
     ["The metrics wanted and the reports they appear in.", "The sources (`01-discovery/source-register.md`).", "The stage the project is at.", "The corpus backlog, downloaded as a sheet from the corpus backlog page."],
     ["List the beliefs that could stop the project. Make each one a spike in slice 0, riskiest first.",
      "Define slice 1: one source to one trusted number that a named person checks.",
      "Define the later slices by widening: more sources, more metrics, more users.",
      "For each slice, pull the corpus backlog items that apply. Common items once; per-source, per-dataset and per-product items once for each.",
      "Write each item as a story, keep the corpus ID, the seat, the stage and the acceptance checks.",
      "Mark each item Ready or not, using the five Ready rules. List what is missing.",
      "Add the Run items: alerts, runbook, cost watch."],
     "`03-backlog/agile-backlog.md` and `agile-backlog.csv`, and a short list of items that are not Ready and why.",
     "agile-backlog.md",
     ["No slice is a layer. Every slice ends in something a person checks.", "Slice 0 holds the riskiest belief.", "Every item has acceptance checks written as checks on data."], 16),
    ("requirement-to-spec", "Requirement to spec", "BA",
     "Turns meeting notes, an old report or a request into a draft spec with acceptance checks. Use when a requirement has been discussed but not written.",
     ["Meeting notes, emails, the old report or the request.", "`00-project/glossary.md` and any metric definitions."],
     ["Write the purpose: the question, who asks it, what they will do with the answer.", "List what is in and what is out. If the notes do not say, put it under open questions.",
      "Write what must be true as numbered acceptance checks. Each one must be testable on data and have an example with real values.",
      "For each number, link the metric definition. If there is none, list it as missing.", "Fill the cases where things go wrong: late source, corrected record, broken rule.",
      "List every open question, with who could decide."],
     "A draft saved as `02-specs/SPEC-NNN-short-name.md`, and a list of questions for the next meeting.", "spec.md",
     ["Nothing in the spec says how to build it.", "Every acceptance check can be run by a tester.", "Open questions are listed, not answered by guessing."], 21),
    ("source-question-list", "Source question list", "BA, Tech Anchor",
     "Prepares the questions for a meeting with a source system owner and records the answers. Use before and after every source meeting.",
     ["What is known about the source so far.", "The spec or the metrics that need this source."],
     ["Read what is known. Pre-fill the questionnaire with it, and say where each answer came from.", "List the questions still open, most important first: owner, key, changes and deletes, access, the figure to match.",
      "Add questions specific to the metrics: which fields feed which number.", "After the meeting, take the notes and fill the answers. Mark what is still UNKNOWN and who to ask.",
      "Update the source register row: owner, access status, size, biggest unknown."],
     "Before: a one-page question list. After: `01-discovery/questionnaire-SOURCE.md` filled, and the register updated.", "source-questionnaire.md",
     ["Every answer says who gave it.", "Nothing is filled from general knowledge of similar systems.", "The list of unknowns has names and dates."], 21),
    ("metric-definition-writer", "Metric definition writer", "BA, product owner",
     "Writes one definition for one number, with an owner and a figure to match. Use when a number is named in a requirement, or when two people mean different things by it.",
     ["The name of the number.", "How people describe it: notes, old reports, existing formulas.", "The glossary."],
     ["Collect every description of the number. If they differ, show them side by side and stop for a decision.", "Write the formula in words, then exactly. State the grain, what is included and excluded, and the time rule.",
      "Name the figure it must match, the tolerance and who signs. If unknown, write UNKNOWN.", "Draft a worked example for one real period, if real values were given.", "Add the word to the glossary, with 'also called' and 'not the same as'."],
     "`02-specs/metric-NAME.md`, and a list of decisions the owner must make.", "metric-definition.md",
     ["There is one owner, by name.", "Included and excluded are both filled.", "Two different meanings were not merged quietly."], 21),
    ("acceptance-check-reviewer", "Acceptance check reviewer", "BA, tester",
     "Finds requirements that cannot be tested and suggests a rewrite. Use before a spec goes for agreement.",
     ["A spec, or a list of requirements."],
     ["Read each line. Mark it as a check on data, or a wish.", "A wish has no number, no source of truth, or no way to test it. Words such as fast, accurate, user-friendly and complete are signs.",
      "For each wish, suggest a rewrite with a value, a comparison and who accepts. Leave the value blank if it is not known.", "List the checks that have no one to accept them.", "List what the spec does not cover: late data, corrections, bad records, who can see it."],
     "A table: line, check or wish, why, suggested rewrite. Then the gaps.", None,
     ["Suggested values are marked as suggestions.", "Every line of the spec was looked at."], 17),
    ("source-to-target-mapping-draft", "Source-to-target mapping draft", "BA",
     "Drafts which source field feeds which target field, and lists the gaps. Use after the spec and the source questionnaire exist.",
     ["The source field lists, with meanings.", "The spec and the metric definitions."],
     ["List the target fields the spec needs.", "For each, propose the source field and the rule in words. Say how sure you are and why.", "List target fields with no source.", "List rules where more than one option exists, with the options.", "Add an example in and out where real values were given."],
     "`02-specs/mapping-SPEC-NNN.md`.", "source-to-target-mapping.md",
     ["No mapping rests on a field name alone: the meaning was checked in the questionnaire.", "Gaps are listed, not filled."], 21),
    ("glossary-keeper", "Glossary keeper", "BA",
     "Keeps one meaning per business word across the project's files. Use weekly, and before any spec is agreed.",
     ["The glossary.", "The specs, notes and status reports."],
     ["List the business words used in the files that are not in the glossary.", "List the words used with two meanings, with the file for each.", "List the words with no owner.", "Propose an entry for each new word, taken from how the files use it."],
     "Proposed changes to `00-project/glossary.md`, and the list of words needing a decision.", "glossary.md",
     ["No meaning was taken from outside the project's files.", "Conflicts are shown, not resolved."], 21),
    ("discovery-pack-summary", "Discovery pack summary", "BA, Tech Anchor",
     "Compares what people say, what documents say and what the data shows. Use at the end of discovery, before the discovery sign-off.",
     ["Interview and meeting notes.", "Documents about the sources and the old reports.", "What was seen in the real data (counts, samples, profiling notes)."],
     ["For each topic (each source, each number), set the three views side by side.", "Mark where they agree.", "Mark where they disagree. A disagreement is a finding.", "Mark where one view is missing.",
      "List the results of the fail-fast tests: sample, access, meaning, one number, volume and timing, change, user, running.", "Say what to ask next, and whom."],
     "`01-discovery/discovery-summary.md`: agreements, disagreements, gaps, test results, next questions.", None,
     ["Each statement says which of the three views it came from.", "No disagreement was smoothed over."], 21),
    ("meeting-notes-to-actions", "Meeting notes to actions and decisions", "Everyone",
     "Turns raw notes or a transcript into actions, decisions and open questions. Use after every meeting, the same day.",
     ["Notes or a transcript.", "Who was present."],
     ["Write why the meeting happened, in one line.", "List the facts learnt, with who said each.", "List the decisions, with who decided and why. If it is not clear that it was decided, put it under open questions.",
      "List the actions. One owner each. If no owner or date was said, write UNKNOWN.", "Write the rows to add to the decision log."],
     "`04-run/notes-DATE-topic.md`, and rows for `04-run/decision-log.md`.", "meeting-notes.md",
     ["No action has two owners.", "Nothing is recorded as decided unless someone decided it."], 20),
    ("weekly-status-report", "Weekly status report", "PM",
     "Writes the weekly status report in five headings, starting with what was proved. Use every week.",
     ["The backlog.", "The risk and dependency register.", "This week's notes and test results.", "Last week's report."],
     ["Proved this week: only what works end to end with a number someone checked. Name who checked. If nothing was proved, say so.", "Next: what will be proved next week.",
      "Risks with a date, from the register. Add any early sign seen this week.", "Waiting on: names, and since when. Flag anything blocked more than three days.",
      "Decisions needed: what, from whom, by when, what happens if late.", "Compare with last week. Say what moved and what did not."],
     "`04-run/status-DATE.md`.", "weekly-status-report.md",
     ["There is no 'percent complete'.", "Bad news is in the first half of the page.", "Every wait has a name and a date."], 22),
    ("risk-and-dependency-register", "Risk and dependency register", "PM, PMO",
     "Reads the project's files for early signs of the known failure causes and keeps the register current. Use weekly.",
     ["The project repository.", "This week's notes.", "The current register."],
     ["Read for early signs: unanswered questions to a source owner, access not granted, a metric with no owner, two definitions, no figure to match, scope added with nothing removed, status in percent, no one named to run it.",
      "For each sign, add or update a risk, with its theme (A to F) and where the sign was seen.", "List every dependency on someone outside the team, with the date asked and the days blocked.",
      "Flag blocks older than three days for escalation.", "Leave owner and date blank for people to fill; never assign a person yourself."],
     "An updated `04-run/risk-and-dependency-register.md`, and the three items that need action this week.", "risk-and-dependency-register.md",
     ["Every risk names where its early sign was seen.", "No owner was invented."], 22),
    ("ready-checker", "Ready checker", "PM, BA",
     "Checks backlog items against the Ready rules before a sprint. Use at sprint planning.",
     ["The backlog items planned for the next sprint.", "The source register, the specs and the metric definitions."],
     ["For each item, check the five Ready rules against the files.", "Say Ready or Not ready.", "For Not ready, say exactly what is missing and who could supply it.", "Suggest the order: items whose missing piece has the longest wait first."],
     "A table: item, Ready or not, what is missing, who to ask.", None,
     ["Each rule was checked against a file, not assumed."], 16),
    ("gate-pack-builder", "Gate pack builder", "PM, delivery manager",
     "Gathers the evidence for a sign-off gate and says what is missing. Use two weeks before a gate.",
     ["The gate (for example discovery sign-off, production sign-off).", "The project repository."],
     ["List what this gate needs as evidence (see the sign-off record and `skills/project-review/checks.md`).", "Find each piece in the repository. Link it.", "List what is missing or out of date.",
      "List open review findings rated Blocker or Major.", "Draft the one-page summary for the signer: what they are signing, the evidence, the open points."],
     "`06-reviews/gate-NAME-pack.md`, and a draft sign-off record.", "sign-off-record.md",
     ["Every evidence link opens a real file.", "Missing evidence is on the first page, not the last."], 22),
    ("change-request-impact", "Change request impact", "PM, product owner",
     "Shows what a requested change touches and what decision is needed. Use when scope changes are asked for.",
     ["The change, in the requester's words.", "The specs, the backlog and the estimate."],
     ["Restate the change in one line and confirm what it is for.", "List the specs, metrics, backlog items, tests and reports it touches.", "Say which finished work must be redone.",
      "Give the effect on effort as a range, and on the date. Say what assumption this rests on.", "Say what could be removed to make room.", "Write the decision needed, by whom."],
     "A one-page impact note, and a draft row for the decision log.", None,
     ["Nothing was added without saying what it costs or what it displaces."], 22),
    ("stakeholder-map", "Stakeholder map and communication plan", "PM, BA",
     "Places the project's people by influence and interest and plans who hears what. Use at the start and at each gate.",
     ["The cast list.", "Notes on what each person cares about."],
     ["Check the cast against the four groups: client, us, vendors, platform. List the missing roles.", "Draft the grid from the notes. Mark each placement as a guess for the PM to confirm.",
      "Flag high influence with low interest: these need the most effort.", "Draft who hears what, how often, from whom."],
     "A filled `00-project/cast-and-stakeholder-map.md`.", "cast-and-stakeholder-map.md",
     ["Placements are marked as guesses until a person confirms.", "Missing roles are listed."], 22),
    ("test-and-reconciliation-plan-writer", "Test and reconciliation plan writer", "Tester",
     "Turns a spec's acceptance checks into tests on data and a reconciliation plan. Use when a spec is agreed.",
     ["The agreed spec.", "The metric definitions with the figures to match."],
     ["One test per acceptance check: data used, expected result, where evidence is kept.", "List the figures to match, with tolerance and signer. Flag any that are missing.", "Add the count checks between layers.",
      "Add tests for the cases where things go wrong.", "List the users who must accept, and what each tests."],
     "`05-test/test-plan-SPEC-NNN.md`.", "test-and-reconciliation-plan.md",
     ["Every acceptance check has a test.", "No test uses made-up data where real data is required."], 21),
    ("proposal-checker", "Proposal and statement-of-work checker", "Delivery manager, sponsor",
     "Reads a proposal or statement of work for what is missing or not said. Use before it goes to the client.",
     ["The draft proposal or statement of work.", "The estimate."],
     ["Compare scope in the proposal with the counts in the estimate. List differences.", "List assumptions in the estimate that are not in the proposal.", "List what is excluded but not said.",
      "List what the client must provide (access, people, approvals, figures to match) and whether each has a date.", "Check that discovery is priced on its own or that the price is a range.", "Check that support after go-live and the switch-off of the old report are covered."],
     "A findings list rated Blocker, Major, Minor, Note.", None,
     ["Each finding quotes the section it refers to."], 24),
    ("handover-and-runbook-checker", "Handover and runbook checker", "Delivery manager",
     "Checks that someone who did not build it can run it. Use before the operational readiness sign-off.",
     ["The runbook and the handover notes.", "The consumer register."],
     ["For each thing that can go wrong, check there is an alert, a named person, a first step and an escalation.", "Check the rerun steps are complete and say what must not be done.",
      "Check a failure drill was run, and what changed after it.", "Check cost has an owner and an alert figure.", "Check every old report has a switch-off date."],
     "A findings list rated Blocker, Major, Minor, Note.", "runbook-and-handover.md",
     ["A role without a name counts as missing."], 25),
    ("portfolio-health-roll-up", "Portfolio health roll-up", "PMO",
     "Puts every project on one page, the same way. Use monthly, or before a portfolio meeting.",
     ["The latest status report and review findings of each project."],
     ["One row per project: stage, next gate and date, open Blockers, waits older than three days, early signs showing.", "Flag projects whose status has no 'proved this week' for two weeks.",
      "Flag the same early sign appearing in several projects.", "List projects not using the current templates."],
     "One table and three lines: what needs a decision this month.", None,
     ["Every cell comes from a project file. Missing files show as missing, not as green."], 25),
    ("template-and-skill-keeper", "Template and skill keeper", "PMO",
     "Checks that projects use the current starter kit, and brings good local changes back. Use quarterly.",
     ["The starter kit.", "The project repositories."],
     ["Compare each project's templates and skills with the starter kit.", "List projects that are behind.", "List local improvements worth bringing back, with the reason.", "Draft each as a change for review to the starter kit."],
     "A list of projects behind, and proposed changes to the kit.", None,
     ["Nothing is changed in the kit without a review by a person."], 23),
    ("lessons-learnt-collector", "Lessons learnt collector", "PMO, everyone",
     "Turns a retrospective into proposed changes to templates, checks and skills. Use after each retrospective.",
     ["The retrospective notes.", "Estimated and actual effort and dates."],
     ["Record estimated against actual, effort and calendar apart, in `03-backlog/actuals.md`.", "For each thing that hurt, name the early sign that was missed.",
      "Propose one change per lesson: to a template, a check or a skill. Say which file.", "Drop lessons with no change attached."],
     "A filled `07-handover/retrospective.md` and a list of proposed changes.", "retrospective.md",
     ["Every lesson ends in a change to a named file."], 23),
]

ESTIMATOR_RATES = """# Rates and rules for the estimator

These are starting values, taken from the worked example on cleandataengineering.ai/how-we-work/estimation/.
Replace them with your own actuals as soon as you have any (`03-backlog/actuals.md`).

## Size each source
| Size | Signals | First build, person-weeks |
|---|---|---|
| Small | A few tables, clear keys, a reliable change column, documents exist, the owner answers within a day | 1 to 2 |
| Medium | Ten to thirty tables, some joins to learn, deletes need care, some documents, the owner is busy | 3 to 5 |
| Large | Many tables or a packaged application, codes that need a lookup, no change column, history in odd formats | 6 to 10 |
| Very large | Several systems feeding one model, conflicting definitions, no reachable owner | 10 to 20, split it |

Twenty sources are never twenty copies of an average source. Size each one.

## One medium source, estimated honestly
About twelve tables, a daily load, history kept, a few final tables and one dashboard that must match the finance report.

| Line | Low (days) | High (days) | Usually in the estimate? |
|---|---|---|---|
| Discovery: what the source data means | 12 | 18 | No |
| Access and environment set-up (effort only) | 2 | 3 | No |
| Getting the data in | 4 | 6 | Yes |
| Cleaning, with history | 8 | 12 | Yes |
| Final tables and metric definitions | 6 | 10 | Yes |
| Tests and checks | 6 | 9 | No |
| Reconciling with finance, and fixing | 8 | 14 | No |
| Loading history | 3 | 5 | No |
| Deploy, monitoring, runbook | 4 | 6 | No |
| Support after go-live, first four weeks | 5 | 8 | No |
| Total | 58 | 91 | |

A code-only estimate of this source says 18 to 28 days. The honest one is about three times that.
Use this table as the shape for other sizes. Scale it by the source size, then adjust each line with a stated reason.

## Rules
1. Give a range, with the assumptions behind it.
2. Show the usually forgotten lines on their own lines.
3. Show waits apart from effort. Waiting for access is not effort.
4. Do not add a flat percentage for contingency. Put the forgotten items in as real lines.
5. Say the date to re-estimate, usually after the first source runs end to end.
6. Before discovery, fix the price of discovery only.
7. Compare with what similar work really took, not with what it was estimated at.

## Five questions to ask of any estimate
1. Is there a line for understanding the source data, and is it bigger than the line for getting the data in?
2. Is it a range, and does it say what event will narrow it?
3. Are waits (access, answers, sign-off) shown apart from effort?
4. Is reconciliation in, with a tolerance and someone to sign it off?
5. Did the people who will build it make the estimate?
"""

REVIEW_CHECKS = """# Checks for a project review, by stage

A short list for non-technical reviewers. Check this stage and every stage before it.
The full catalogue is at cleandataengineering.ai/learn/technical-anchor/project-review/checks/.

For each check: find the evidence in the project's files. No evidence means the check fails.

## Stage 1. Requirement received
- The need names the decision it supports, not only 'build a dashboard'.
- There are at least three business questions the data must answer.
- A sponsor and a business owner are named.
- Assumptions are listed.

## Stage 2. Rough estimate
- The estimate is a range, with its assumptions.
- It lists what was counted: sources, tables, reports, users.
- The cost of discovery is shown on its own.
- Waiting is shown apart from effort.

## Stage 3. Discovery
- Every source has an owner by name and a filled questionnaire.
- The team has seen a real sample of each source.
- Access to each source has been requested, with a date, and tested.
- Every metric has one definition and one business owner.
- At least one figure has been rebuilt by hand and matches a figure the business trusts.
- Requirements are written as checks on data.
- The fail-fast tests have results: sample, access, meaning, one number, volume and timing, change, user.
- A risk and dependency register exists, with owners and dates.

## Stage 4. Discovery sign-off (gate)
- A review of the discovery document was held by someone who did not write it.
- The decision is recorded: go, go with changes, or stop, by a named signer.
- Conditions have owners and dates.
- The estimate was redone after discovery, and scope and date changes are written down.

## Stage 5. MVP 1 starts
- The backlog is cut in slices, not layers. Slice 1 ends in a number a named person checks.
- Every item in the first sprint meets the Ready rules.
- Environments and access work on day one.
- Design, security and privacy reviews are booked or done.

## Stage 6. Build
- The weekly status report says what was proved, with a number someone checked.
- Effort is tracked against the estimate weekly, apart from calendar time.
- Scope changes have a decision log entry and say what was removed.
- Demos use real numbers.
- No dependency has been blocked for more than three days without escalation.

## Stage 7. Test
- Every acceptance check in the spec has a test with a result.
- Totals match the trusted figure within the agreed tolerance, and someone signed.
- Counts between layers are explained.
- Users accepted on real data, by name.
- There is a rule for bad records, and someone looks at them.

## Stage 8. Deploy
- The release is done by the pipeline, not by hand, and has been rehearsed.
- Quality checks run daily and alert a named person.
- The runbook exists, and a failure drill was run from it by someone who did not build it.
- Cost has an owner and an alert figure.
- Access rules are in place and were reviewed.

## Stage 9. Production sign-off (gate)
- The first production run was reconciled to the trusted figure.
- Operations accepted the runbook, by name.
- Open findings rated Blocker are closed; Majors are accepted in writing with a date.
- Every old report has a switch-off date.

## Stage 10. Project sign-off (gate)
- The old reports were switched off, or there is a dated decision to keep them.
- The handover pack was accepted by the people who will run it.
- Estimated against actual is recorded, effort and calendar apart.
- A retrospective produced at least one change to the starter kit.

## At every stage
- Every document is in the project repository, with history.
- Every number has a name, a formula and an owner.
- Every risk, action and dependency has one name and one date.
- No file contradicts another on scope, dates or definitions.
"""

EXTRA = {"data-project-estimator": [("rates.md", ESTIMATOR_RATES)], "project-review": [("checks.md", REVIEW_CHECKS)]}
