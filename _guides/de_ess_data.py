"""Content for the Data project essentials programme: failure causes, the cast, the three seats, and the corpus backlog.

Used by de_essentials.py. Agreed 23 Nov 2026 (roadmap v2): six themes / 28 causes; the corpus backlog sits between an
epic and a task list, owned by BA, Tech Anchor or PM; every item says which causes it prevents.
The causes and items are a synthesis from the site's pages and common project experience; the owner reviews and edits them here.
"""

# ------------------------------------------------------------------------ why projects fail
THEMES = [("A", "We don't know the data"), ("B", "We don't have the people"), ("C", "We don't agree"),
          ("D", "We don't prove it"), ("E", "We don't plan for reality"), ("F", "We don't run and adopt it")]

# n, theme, cause, punchline, early sign, layer slug, DDLC stage where it should be caught
CAUSES = [
    (1, "A", "Source meaning unknown", "The data was there. Its meaning wasn't.", "Nobody can name the person who explains a field.", "sources", 3),
    (2, "A", "Changes and deletes not understood", "The source forgot what it deleted.", "The owner cannot say how a record is deleted or corrected.", "sources", 3),
    (3, "A", "Data quality worse than expected", "Real data is messier than the sample.", "No one has profiled a real extract.", "clean", 3),
    (4, "A", "The old report's logic is hidden", "The old spreadsheet knows things nobody wrote down.", "'Don't touch it, the number is right.'", "sources", 3),
    (5, "A", "Volume and timing never tested", "Fine on a thousand rows. Dead on a hundred million.", "Nobody knows how long the full load takes.", "landing", 3),
    (6, "B", "Source owners not engaged", "Your plan depends on people who don't report to you.", "The first request to a source owner is in month three.", "sources", 2),
    (7, "B", "Access and approvals arrive late", "Weeks lost waiting for a key.", "No access request was raised in week one.", "across", 2),
    (8, "B", "No owner for each metric", "Everyone's number, nobody's decision.", "'Who owns this number?' gets three answers.", "meaning", 4),
    (9, "B", "One person holds the knowledge", "If Ravi leaves, the project does.", "One name answers every source question.", "sources", 3),
    (10, "B", "Vendors and third parties are outside control", "Someone else's delay is your delay.", "A key deliverable has no committed date from the vendor.", "sources", 2),
    (11, "C", "Departments define metrics differently", "Two reports, two revenues, one argument.", "Sales and finance quote different totals.", "meaning", 4),
    (12, "C", "Requirements change when people see real data", "Nobody knows what they want until they see it.", "The first demo is planned for the end.", "consumers", 3),
    (13, "C", "Scope grows silently", "'Just one more source.'", "The backlog grows, the date does not move.", "start", 2),
    (14, "C", "Sponsor, PM and team expect different things", "Three people, three projects.", "Each describes the goal in different words.", "start", 1),
    (15, "D", "No reconciliation to a trusted figure", "It ran. It was wrong. Nobody had checked.", "Reconciliation is planned for the last week.", "model", 6),
    (16, "D", "Acceptance late, or on fake data", "A demo on fake data proves nothing.", "Business testers first see the data at acceptance.", "consumers", 7),
    (17, "D", "Wrong grain for the question", "The table cannot answer the question that was asked.", "Nobody asked 'one row per what?'", "model", 3),
    (18, "D", "No daily data quality checks", "You find out when the CEO does.", "Quality is checked once, at go-live.", "clean", 6),
    (19, "E", "Estimates count code, not learning and waiting", "The estimate had only the easy part.", "No line in the estimate for access, meaning or reconciliation.", "start", 2),
    (20, "E", "Discovery skipped", "We saved two weeks and lost six months.", "Build starts before any real data has been seen.", "start", 3),
    (21, "E", "Built layer by layer, then a big-bang go-live", "Nothing usable until everything is done.", "The plan shows layers, not slices.", "start", 5),
    (22, "E", "Status reported as percent complete", "Eighty percent built, zero percent usable.", "Status reports contain no number that was proved.", "start", 6),
    (23, "E", "No BA or Tech Anchor in the team", "Everyone builds, and nobody holds the picture.", "Nobody can describe the whole system end to end.", "start", 4),
    (24, "F", "Nobody owns it after go-live", "The team left. The job failed on Sunday.", "Operations first hear of it at go-live.", "across", 8),
    (25, "F", "No monitoring, runbook or failure drill", "It fails silently.", "No alert goes to a named person.", "across", 8),
    (26, "F", "Cost surprise", "The bill is three times the plan.", "Nobody owns or watches the cost.", "across", 4),
    (27, "F", "Old report not retired, so adoption is low", "Built, but not used.", "There is no switch-off date for the old report.", "consumers", 4),
    (28, "F", "Sensitive data found late", "A stop, a clean-up and a call to a regulator.", "Nobody asked 'is any of this personal?'", "across", 3),
]

# ------------------------------------------------------------------------ the cast
CAST_GROUPS = [("Decide", ["Sponsor", "Business owners", "PMO and steering group"]),
               ("Own the data", ["Source system owners", "Data owners and stewards", "Finance", "Security, privacy, compliance", "Vendors and partners"]),
               ("Build and run", ["Data engineers", "BI developers", "Platform and cloud team", "Architects", "Test team", "Operations and support"]),
               ("Use", ["End users", "Analysts and data scientists", "Owners of downstream apps and AI", "Regulators and auditors"])]

# group, who, their role in one line, BA talks about, Tech Anchor talks about, PM talks about
CAST = [
    ("Decide", "Sponsor", "Pays for it; decides go, change or stop.", "Success measures; what the project is for.", "Rarely directly; risks that change the decision go through the PM.", "Weekly note; decisions; scope and date trade-offs."),
    ("Decide", "Business owners", "Own the question, the metric definitions and the acceptance.", "Requirements, definitions, acceptance, mock-ups.", "Feasibility, via the BA; sample numbers.", "Their time; sign-offs; their escalations."),
    ("Decide", "PMO and steering group", "Check the project against the portfolio and the gates.", "-", "-", "Gate reviews; status; budget; risk."),
    ("Own the data", "Source system owners", "Run the systems the data comes from.", "What each field means; how data changes.", "Access method, load windows, test copy, change notice.", "Requests with dates; their calendar; escalation."),
    ("Own the data", "Data owners and stewards", "Accountable for the data's quality and use.", "Definitions, quality rules, who may see what.", "Rules in the pipeline; access design.", "Approvals; ownership of issues."),
    ("Own the data", "Finance", "Own the numbers the business already trusts.", "Which report to match; tolerance; sign-off.", "How totals are built and reconciled.", "Their time at month-end; budget."),
    ("Own the data", "Security, privacy, compliance", "Protect people and the company; can stop a release.", "Which data is sensitive; who may see what.", "Design for masking, encryption, audit.", "Reviews and approvals; dates."),
    ("Own the data", "Vendors and partners", "Supply data, tools or people.", "Data terms; what the vendor's data means.", "Interfaces, limits, support.", "Contract, delivery dates, SLAs."),
    ("Build and run", "Data engineers", "Build and test the pipelines.", "Clarifying requirements and meaning, daily.", "Design, standards, reviews, unblocking.", "Capacity; plan; blockers."),
    ("Build and run", "BI developers", "Build reports and dashboards.", "What each report must answer; mock-ups.", "Data model, performance.", "Plan; users' access."),
    ("Build and run", "Platform and cloud team", "Provide environments, accounts and tooling.", "-", "Environments, access, cost, standards.", "Requests with dates; cost budget."),
    ("Build and run", "Architects", "Guard the standards across projects.", "-", "Design reviews; exceptions.", "Review dates."),
    ("Build and run", "Test team", "Test the system and the numbers.", "Acceptance checks; test data.", "Test strategy; environments.", "Test plan; defects."),
    ("Build and run", "Operations and support", "Run it after the project ends.", "What users will ask; how to answer.", "Runbook, alerts, recovery.", "Hand-over; hypercare; drills."),
    ("Use", "End users", "Use the reports and tools every day.", "Their questions; training; feedback.", "Rarely; performance complaints.", "Rollout; training dates."),
    ("Use", "Analysts and data scientists", "Use the data to answer questions.", "What data they need and how fresh.", "Access, tables, performance.", "Onboarding; support."),
    ("Use", "Owners of downstream apps and AI", "Depend on the data in other systems.", "Their needs; change notice.", "Interfaces, contracts, freshness.", "Change calendar."),
    ("Use", "Regulators and auditors", "Check that rules are followed.", "What must be evidenced.", "Audit trail, retention, lineage.", "Audit dates; evidence."),
]

# ------------------------------------------------------------------------ the three seats
SEATS = [
    ("BA", "Business Analyst", "Owns the question: what the business needs, in words the data can be tested against.",
     ["Business need as decisions and questions", "Requirements as acceptance checks on data", "Source and consumer registers and questionnaires", "Glossary and metric definitions, with the business owners",
      "Reconciliation plan with finance, and user acceptance", "Backlog content and priorities, with the product owner"],
     ["Technical design and tool choice", "Engineering estimates", "The plan, budget and dates", "Decisions that belong to a source owner"],
     ["Every requirement can be tested with a number", "Every source and every consumer has a named person", "A definition dispute ends with a written decision by the owner"],
     ["Writes requirements as wishes", "Learns the source from documents, not from data", "Lets definitions stay without an owner"],
     "Which question did we answer this week, and who confirmed it?"),
    ("TA", "Tech Anchor", "Owns the technical shape: will this work, end to end, for everyone who depends on it?",
     ["End-to-end design and its risks", "Feasibility spikes and fail-fast tests on real data", "Profiling real data and what it means for the design", "Technical estimates, as ranges, with the team",
      "Test strategy, release path and standards", "Technical decision log and engineering hand-over"],
     ["Business definitions and priorities", "Scope and sponsor decisions", "Stakeholder status and dates", "Writing all the code (but still reviews and unblocks)"],
     ["Bad news about the data arrives in week two", "Anyone can describe the whole system from the anchor's picture", "Each risky belief is tested before it is relied on"],
     ["Buried in code, holds no big picture", "Estimates the code only", "Says 'it's fine' without testing on real data"],
     "Which belief is most likely to be wrong, and have we tested it?"),
    ("PM", "Project or Delivery Manager", "Owns the plan: scope, dates, people and the outside dependencies, in the open.",
     ["Plan, milestones and the three gates", "Scope and change control", "Risks, assumptions, issues and dependencies", "Chasing access, approvals and outside owners",
      "Status note and stakeholder rhythm", "Budget, team, vendors and sign-offs"],
     ["Metric definitions", "Technical design", "Whether numbers reconcile (but makes sure it is planned)"],
     ["Every dependency has a person and a date", "Status reports what was proved, not percent built", "Scope changes are trades, made in the open"],
     ["Reports percent complete", "Lets the builders do the chasing", "Hears bad news late"],
     "What are we waiting on, since when, and who will unblock it?"),
]

# from, to, what they expect
EXPECT = [("BA", "Tech Anchor", "Tell me within a day if a requirement cannot work. Explain what the data really shows, in plain words."),
          ("BA", "PM", "Protect the business owners' time. Chase the source owners. Run change control."),
          ("Tech Anchor", "BA", "Requirements as testable checks. Source meaning answered. Definitions locked before build."),
          ("Tech Anchor", "PM", "Protect the team from scope creep. Access ready. Dates that match the range. Decisions within a day."),
          ("PM", "BA", "Priorities and acceptance criteria ready before each slice. Input to the weekly note. Early warning of stakeholder disagreement."),
          ("PM", "Tech Anchor", "Honest estimates as ranges. Effort against estimate every week. Risks raised when seen, not when they bite.")]
FRICTION = ["The BA says requirements are done; the Tech Anchor finds the data does not exist.", "The PM commits a date before discovery; the Tech Anchor learns of it from the sponsor.",
            "The Tech Anchor changes the design and does not tell the BA, so acceptance checks no longer match.", "The BA promises a stakeholder a feature without asking the PM about scope."]

# ------------------------------------------------------------------------ corpus backlog
AREAS = [("start", "Start and discovery", "PRJ"), ("sources", "Sources (upstream)", "SRC"), ("landing", "Landing", "LND"), ("clean", "Clean", "CLN"), ("model", "Model", "MDL"),
         ("meaning", "Meaning", "MNG"), ("consumers", "People use it (downstream)", "CON"), ("across", "Across everything", "QLT SEC COS RUN"), ("reviews", "Reviews and sign-offs", "REV"), ("golive", "Go-live and hand-over", "GLV")]

# id, title, owner seat, type, prevents (cause numbers), DDLC stage, applies when, typical size, acceptance criteria (|), evidence, depends on
BACKLOG = [
    # ---- start and discovery
    ("PRJ-01", "Business need written as decisions and questions", "BA", "Document", [12, 14], 1, "Always", "S", "The need names the decision it supports|At least three business questions the data must answer|Assumptions listed", "One-page brief signed by the business owner", "Business owner"),
    ("PRJ-02", "Success measures agreed", "BA", "Decision", [14, 27], 1, "Always", "S", "Three to five measures with a baseline and a target|Each can be measured with data the project will have|An owner for each", "Success measures sheet", "Business owner, sponsor"),
    ("PRJ-03", "Stakeholder and decision-owner map", "PM", "Document", [6, 8, 14], 1, "Always", "S", "Every group in the cast has a named person|Owners named for metric definition, scope, go-live and source access", "Map and decision-owner table", "Sponsor"),
    ("PRJ-04", "Scope in and out written", "BA + PM", "Decision", [13], 2, "Always", "S", "Sources, reports and users are listed in and out|A 'not now' list exists|Signed by the sponsor", "Scope page", "Sponsor, business owners"),
    ("PRJ-05", "Rough estimate as a range with assumptions", "TA + PM", "Document", [19], 2, "Always", "S", "A range, not one number|Top five assumptions listed|Discovery estimated separately; effort and calendar time kept apart", "Estimate sheet", "Team"),
    ("PRJ-06", "Risk and dependency register opened", "PM", "Document", [6, 7, 9, 10], 2, "Always", "S", "Every outside dependency has an owner and a date|Reviewed weekly|Top five risks have a first move", "Register", "-"),
    ("PRJ-07", "Discovery plan and timebox", "PM", "Document", [20], 2, "Always", "S", "Duration fixed (usually two to four weeks)|Fail-fast tests listed with owners|Exit criteria written", "Discovery plan", "Sponsor"),
    ("PRJ-08", "Fail-fast tests run", "TA + BA", "Spike", [1, 5, 7, 15], 3, "Always", "M", "Each of the eight tests has a result: pass, fail or unknown|Every fail or unknown has an action", "Results table", "Source owners, finance"),
    ("PRJ-09", "Discovery document written and reviewed", "TA", "Document", [14, 20], 3, "Always", "M", "Covers goals, sources, consumers, design, estimate, risks, test strategy|Reviewed by named reviewers|Bad news included", "Reviewed document", "BA, PM, reviewers"),
    ("PRJ-10", "Discovery sign-off: go, change or stop", "PM", "Decision", [14, 20], 4, "Always", "S", "The sponsor's decision is recorded by name and date|Open items have owners|The backlog for MVP 1 is agreed", "Sign-off record", "Sponsor, reviewers"),
    ("PRJ-11", "Team shape and seats named", "PM", "Decision", [9, 23], 4, "Always", "S", "BA, Tech Anchor and PM are named, with their time|A backup exists for each key knowledge holder", "Team page", "Sponsor"),
    ("PRJ-12", "Environments, access and release path ready", "TA + PM", "Slice", [7, 19], 5, "Always", "M", "Development, test and production exist|The team can release a trivial change through the pipeline|Nobody uses personal accounts", "A released trivial change", "Platform team, security"),
    ("PRJ-13", "Ready and Done checklists agreed", "BA + TA", "Decision", [15, 16], 5, "Always", "S", "Both lists written and visible|The team accepts them", "The two lists", "Team"),
    ("PRJ-14", "Weekly status note started", "PM", "Run", [14, 22], 5, "Always", "S", "Same five headings every week|Reports what was proved, not percent built", "Notes sent", "Sponsor"),
    ("PRJ-15", "Change control agreed", "PM", "Decision", [13], 5, "Always", "S", "A change is a trade: something out, or the date moves|Decided in the open, by the sponsor", "Process page", "Sponsor"),
    ("PRJ-16", "Glossary and decision log started", "BA", "Document", [11, 14], 3, "Always", "S", "Every business word in use has a meaning and an owner|Each decision has date, who, why", "Glossary, log", "Business owners"),
    # ---- sources
    ("SRC-01", "Source register: every source, its owner and an explainer", "BA", "Document", [1, 6, 9], 3, "Always", "S", "Every source has a named owner and a named person who can explain it|Nothing marked 'TBD'", "Register", "Source owners"),
    ("SRC-02", "Meaning review of the most-used fields", "BA", "Document", [1], 3, "Always", "M", "Each of the top ten fields per source has a written meaning confirmed by the owner|Unanswered fields are logged as risks", "Field meanings sheet", "Source owners"),
    ("SRC-03", "Real data sample received and profiled", "TA", "Spike", [1, 3, 5], 3, "Always", "M", "A real extract profiled: counts, blanks, duplicates, date ranges|Findings reviewed with the owner", "Profile report", "Source owners, access"),
    ("SRC-04", "Change and delete behaviour known", "TA", "Spike", [2], 3, "Always", "S", "The owner states how rows are edited and deleted|Whether a modified date exists is known|The effect on loading is written", "Short note", "Source owners"),
    ("SRC-05", "Hand-over method agreed per source", "TA", "Decision", [2, 5], 3, "Always", "S", "Pull, push or share is chosen per source|Frequency and format agreed", "Source sheet", "Source owners"),
    ("SRC-06", "Access requested and confirmed", "PM", "Slice", [7], 2, "Always", "M", "Requests raised in week one with dates|Access confirmed from the build environment", "A successful read from the build environment", "Security, network"),
    ("SRC-07", "Source owner commitments: change notice, test copy, contact", "PM", "Decision", [6, 10], 3, "Always", "S", "Notice period for changes agreed|A non-production copy available|A named contact for incidents", "Commitments note", "Source owners"),
    ("SRC-08", "Source volume, load window and impact", "TA", "Spike", [5], 3, "Always", "S", "Volume and growth known|A window that does not harm the source is agreed|Full load time estimated", "Load estimate", "Source owners"),
    ("SRC-09", "Sensitive and personal data flagged per source", "BA", "Document", [28], 3, "Always", "S", "Every source reviewed for personal or regulated fields|List shared with security", "Flagged field list", "Security, privacy"),
    ("SRC-10", "Source questionnaire completed", "BA", "Document", [1, 6, 9], 3, "Always", "M", "Completed for each source with the owner|Open answers become risks", "Completed questionnaire", "Source owners"),
    ("SRC-11", "Second explainer named for each critical source", "PM", "Decision", [9], 3, "Always", "S", "A second person who can explain the source is named|Or the knowledge is written down", "Register updated", "Source owners"),
    ("SRC-12", "Existing report reverse-engineered", "BA", "Spike", [4], 3, "Replacing an existing report", "M", "Every column and manual step explained by its owner|Hidden rules written down", "Report logic sheet", "Report owner"),
    ("SRC-13", "Vendor data terms and delivery commitments", "PM", "Document", [10], 3, "A vendor supplies data", "S", "Terms, frequency and support in writing|A committed delivery date", "Terms summary", "Vendor, procurement"),
    # ---- landing
    ("LND-01", "Freshness need per source agreed", "BA", "Decision", [5, 12], 3, "Always", "S", "How fresh the data must be is stated per consumer|What happens when it is late is agreed", "Freshness table", "Business owners"),
    ("LND-02", "History depth and first-load plan", "TA", "Decision", [5, 19], 3, "Always", "S", "How far back is decided with the business|Size and duration of the first load estimated", "Load plan", "Business owners"),
    ("LND-03", "Landing counts match the source", "TA", "Slice", [15, 18], 6, "Always", "S", "Source and landing counts compared on every load|A mismatch alerts a person", "A mismatch caught on purpose", "-"),
    ("LND-04", "Rerun safety shown", "TA", "Slice", [15, 25], 6, "Always", "S", "Running a load twice leaves the same result|Shown in a demo", "Demo", "-"),
    ("LND-05", "Late, failed and partial loads handled", "TA", "Slice", [18, 25], 6, "Always", "M", "A late file or half load is detected|A named person is alerted|The retry rule is written", "Failure test result", "Operations"),
    ("LND-06", "Source change handling agreed", "TA", "Decision", [2, 6], 3, "Always", "S", "What happens when a column is added, renamed or removed is agreed with the owner", "Note", "Source owners"),
    ("LND-07", "Load schedule agreed with the source owner", "PM", "Decision", [5, 6], 5, "Always", "S", "A schedule that fits the source's busy times|Escalation named if late", "Schedule", "Source owners"),
    ("LND-08", "Real-time need justified", "BA + TA", "Decision", [19, 26], 3, "Freshness under a few hours is asked for", "S", "The decision that needs fresh data is named|Cost compared with batch|Business owner accepts the cost", "Short decision note", "Business owner"),
    ("LND-09", "Historical backfill executed and reconciled", "TA", "Slice", [5, 15], 7, "History is needed", "M", "History loaded for the agreed period|Reconciled with the source and a trusted report", "Reconciliation", "Finance"),
    ("LND-10", "Raw copy retention and deletion rule", "BA", "Decision", [26, 28], 4, "Always", "S", "How long raw data is kept is agreed|Deletion of personal data is possible", "Rule", "Security, privacy"),
    # ---- clean
    ("CLN-01", "Identity rule: what makes a record the same", "BA", "Decision", [3, 11], 3, "Always", "S", "Written for each main thing (customer, product, order)|Confirmed by the data owner", "Rule sheet", "Data owner"),
    ("CLN-02", "Data quality rules written, each with an owner", "BA", "Document", [3, 18], 4, "Always", "M", "Each rule in plain words with an owner|Thresholds agreed", "Rule list", "Data owners"),
    ("CLN-03", "Handling of bad rows agreed", "BA", "Decision", [3, 15], 4, "Always", "S", "For each rule: drop, fix or park for a person|Business owner agrees", "Decision list", "Data owners"),
    ("CLN-04", "Rejected-row review pile, with a reviewer", "PM", "Run", [3, 24], 6, "Always", "S", "A named person reviews rejected rows|Frequency agreed|Counts are reported", "Review record", "Data owner"),
    ("CLN-05", "History need decided", "BA", "Decision", [12, 17], 3, "Always", "S", "For each main thing: do we need 'as it was then'?|Decided with the business owner", "Decision", "Business owner"),
    ("CLN-06", "Reference and master data source agreed", "BA", "Decision", [1, 11], 4, "Always", "S", "Country codes, product lists and similar have one trusted source|Owner named", "List of sources", "Data owners"),
    ("CLN-07", "Duplicates and keys tested on real data", "TA", "Slice", [3, 15], 6, "Always", "M", "Duplicate counts measured before and after|Keys proved unique on real data", "Test result", "-"),
    ("CLN-08", "Cleaning rules explained back to a source expert", "BA", "Slice", [1, 15], 6, "Always", "S", "The expert confirms the rules do what they meant|Differences logged", "Review note", "Source expert"),
    ("CLN-09", "Late and corrected records shown to work", "TA", "Slice", [2, 15], 6, "Always", "M", "A late row and a corrected row are demonstrated|The right number appears", "Demo", "-"),
    ("CLN-10", "Quality results visible to the business", "TA", "Slice", [18, 27], 6, "Always", "S", "Counts of passed and failed checks are visible|Business owner can read them", "A view or report", "Business owner"),
    # ---- model
    ("MDL-01", "Business questions turned into grain statements", "BA", "Document", [12, 17], 3, "Always", "S", "Each question has 'one row per what' written|Business owner confirms", "Grain sheet", "Business owner"),
    ("MDL-02", "Model design reviewed with a business owner", "TA + BA", "Decision", [11, 17], 4, "Always", "S", "The design can answer all the key questions|Questions it cannot answer are listed", "Review note", "Business owner"),
    ("MDL-03", "Metric definitions drafted: name, formula, owner", "BA", "Document", [8, 11], 4, "Always", "M", "Each metric has a name, a plain-words formula and an owner|Edge cases (returns, cancellations) included", "Draft catalogue", "Business owners, finance"),
    ("MDL-04", "Reconciliation plan with finance", "BA", "Document", [15], 3, "Always", "S", "The report to match and the tolerance are named|Finance agrees to sign off", "Plan", "Finance"),
    ("MDL-05", "Thin slice built: one source to one number", "TA", "Slice", [19, 21, 22], 6, "Always", "M", "One source goes through every layer to one number|Runs from the pipeline, not by hand", "Demo", "Source access"),
    ("MDL-06", "Thin slice reconciled and signed", "BA", "Slice", [15, 16], 6, "Always", "M", "The number matches the trusted report within tolerance|Finance signs it", "Signed reconciliation", "Finance"),
    ("MDL-07", "Date, currency, time zone and calendar rules", "BA", "Decision", [3, 11], 4, "Always", "S", "Which calendar, which time zone and which currency are stated|Edge cases such as month-end agreed", "Rule sheet", "Finance"),
    ("MDL-08", "Owners of dimensions and hierarchies", "BA", "Decision", [8, 11], 4, "Always", "S", "Product, region and organisation hierarchies each have an owner|Change process known", "Owner list", "Data owners"),
    ("MDL-09", "Model change process", "TA", "Decision", [11, 13], 5, "Always", "S", "New column or changed definition goes through a named route|Affected reports are listed before the change", "Process page", "BA"),
    ("MDL-10", "Performance checked at real volume", "TA", "Slice", [5, 26], 7, "Always", "S", "Key reports respond within the agreed time at production volume", "Test result", "-"),
    # ---- meaning
    ("MNG-01", "Metric catalogue with owners", "BA", "Document", [8, 11], 5, "Always", "M", "Every metric in use is listed with owner and formula|Published where users can find it", "Catalogue", "Business owners"),
    ("MNG-02", "Definition conflicts settled on real data", "BA", "Decision", [11], 5, "Always", "M", "Both numbers shown side by side on the same sample|The owner decides; the other is renamed|Written in the glossary and log", "Decision record", "Business owners"),
    ("MNG-03", "Access rules per role agreed", "BA + TA", "Decision", [28], 4, "Always", "M", "For each role: what they may see, by row and column|Approved by the data owner and security", "Access matrix", "Data owner, security"),
    ("MNG-04", "Access rules tested with real roles", "TA", "Slice", [16, 28], 7, "Always", "S", "A person in each role sees only what the matrix says", "Test record", "Security"),
    ("MNG-05", "Definition change notice process", "PM", "Decision", [11, 14], 5, "Always", "S", "A change to a definition is announced before it happens|The affected report owners are told", "Process page", "Business owners"),
    ("MNG-06", "AI assistant uses the same definitions", "TA", "Slice", [11], 7, "Natural-language or AI access to the data", "S", "The assistant gives the same answer as the dashboard for the same question", "Side-by-side test", "-"),
    ("MNG-07", "Sensitive fields masked", "TA", "Slice", [28], 6, "Personal or regulated data", "S", "Masked for roles that must not see it|Tested", "Test record", "Security"),
    # ---- consumers
    ("CON-01", "Consumer register", "BA", "Document", [12, 27], 3, "Always", "S", "Every consumer named, with an owner, contact and the decision they use the data for", "Register", "Business owners"),
    ("CON-02", "Needs per consumer: freshness, detail, who may see", "BA", "Document", [5, 12], 3, "Always", "M", "For each consumer: how fresh, how detailed, which people|Agreed by the consumer", "Needs sheet", "Consumers"),
    ("CON-03", "Mock-up shown to a real user in week two", "BA", "Spike", [12, 16], 3, "Always", "S", "The user says 'yes, this answers my question' or says what is missing", "Feedback note", "Users"),
    ("CON-04", "Old report inventory and switch-off date", "BA + PM", "Decision", [27], 4, "Replacing existing reports", "S", "Every old report listed with owner|A switch-off date agreed", "Inventory", "Report owners"),
    ("CON-05", "Report shows data-as-of and source", "TA", "Slice", [18, 27], 6, "Always", "S", "Each report shows when the data was last updated and where it comes from", "Report view", "-"),
    ("CON-06", "Acceptance with real users on real numbers", "BA", "Slice", [16], 7, "Always", "M", "Users test with numbers they recognise|Defects logged and resolved|Acceptance signed", "Signed acceptance", "Users, test team"),
    ("CON-07", "User access and licences ready", "PM", "Slice", [7], 6, "Always", "S", "Every user group can open the report before acceptance", "Access check", "Security, BI team"),
    ("CON-08", "Training and support route", "PM", "Run", [24, 27], 8, "Always", "S", "Users are trained|They know where to report a wrong number", "Training record", "Support"),
    ("CON-09", "Adoption measured at 30 and 90 days", "BA", "Run", [27], 10, "Always", "S", "Use counts against targets|Reasons for low use are written", "Adoption report", "-"),
    ("CON-10", "Old report switched off", "PM", "Decision", [27], 9, "Replacing existing reports", "S", "Switched off on the agreed date|The owner agreed", "Confirmation", "Report owner"),
    ("CON-11", "Downstream questionnaire completed", "BA", "Document", [12], 3, "Always", "M", "Completed with each consumer owner|Open answers become risks", "Questionnaire", "Consumers"),
    ("CON-12", "Consumer change notice process", "PM", "Decision", [14], 5, "Always", "S", "Consumers are told before a change that affects them", "Process page", "Consumers"),
    # ---- across everything
    ("QLT-01", "Quality dimensions and thresholds agreed", "BA", "Decision", [18], 4, "Always", "S", "Which checks (complete, unique, timely, valid) and what limits|Business owner agrees", "Quality sheet", "Data owners"),
    ("QLT-02", "Daily quality checks live and alerting", "TA", "Slice", [18, 25], 6, "Always", "M", "Checks run every load|A failure alerts a named person", "Alert test", "-"),
    ("QLT-03", "Quality scorecard shown to the business", "BA", "Run", [18, 27], 8, "Always", "S", "A simple scorecard is visible to business owners|Reviewed monthly", "Scorecard", "Business owners"),
    ("SEC-01", "Sensitive data classified", "BA", "Document", [28], 3, "Always", "M", "Every dataset classed (public, internal, confidential, personal)|Confirmed by data owners", "Classification list", "Security, privacy"),
    ("SEC-02", "Security and privacy review held early", "PM", "Decision", [7, 28], 3, "Always", "S", "Review held in discovery, not at the end|Outcome and conditions recorded", "Review record", "Security"),
    ("SEC-03", "Access approval route for people and systems", "PM", "Decision", [7, 28], 4, "Always", "S", "Who approves access to what is written|Approval times known", "Route", "Security"),
    ("SEC-04", "Audit trail needs known", "BA", "Decision", [28], 3, "Regulated data", "S", "What must be evidenced and for how long is written|Confirmed by compliance", "Requirement note", "Compliance"),
    ("COS-01", "Monthly cost budget and owner", "PM", "Decision", [26], 4, "Always", "S", "A budget and an owner named|Reviewed monthly", "Budget record", "Finance, platform team"),
    ("COS-02", "Cost alert and monthly review", "TA", "Run", [26], 8, "Always", "S", "An alert fires on a jump|A monthly review is held and noted", "Alert and notes", "Platform team"),
    ("COS-03", "Cost forecast per slice", "TA", "Document", [19, 26], 4, "Always", "S", "Each slice has a cost range|Compared with the budget", "Forecast", "-"),
    ("RUN-01", "Job schedule and dependencies documented", "TA", "Document", [25], 6, "Always", "S", "What runs when, and what each job waits for, is written|Operations can read it", "Schedule page", "Operations"),
    ("RUN-02", "Monitoring and alerts go to a named person", "TA", "Slice", [24, 25], 7, "Always", "M", "A failure alerts a person, not a mailbox|Tested by a deliberate failure", "Alert test", "Operations"),
    ("RUN-03", "Runbook written and used by someone else", "TA", "Document", [24, 25], 8, "Always", "M", "Someone who did not build it follows it and succeeds|Gaps fixed", "Runbook, test note", "Operations"),
    ("RUN-04", "Failure drill with operations", "PM", "Spike", [24, 25], 8, "Always", "S", "Something breaks on purpose|Operations fixes it from the runbook without the builders", "Drill report", "Operations"),
    ("RUN-05", "Support model: who, hours, escalation", "PM", "Decision", [24], 5, "Always", "S", "Names, hours and escalation path agreed with operations", "Support page", "Operations"),
    ("RUN-06", "Operations invited to demos from MVP 1", "PM", "Run", [24], 6, "Always", "S", "A named operations person attends demos|Questions logged", "Attendance", "Operations"),
    ("RUN-07", "Recovery: backup, rollback and rerun", "TA", "Slice", [25], 8, "Always", "M", "Each can be shown to work|Time to recover is known", "Recovery test", "Platform team"),
    # ---- reviews and sign-offs
    ("REV-01", "Review and sign-off calendar", "PM", "Document", [14, 20], 2, "Always", "S", "Every review and sign-off has a date, a reviewer and an owner|Lead time for external reviews is included|Reviewers have the dates in their diaries", "Calendar", "Sponsor, reviewers"),
    ("REV-02", "Review criteria and checklists per artefact", "TA + BA", "Decision", [15, 20], 5, "Always", "S", "For each artefact type, a short checklist of what 'good' means|Agreed before the review, not after", "Checklists", "Team"),
    ("REV-03", "Independent design review", "TA", "Spike", [20, 23], 4, "Always", "M", "A reviewer who did not build the design has read it|Findings logged with severity and owner|Blockers closed before build", "Review record", "Architect, reviewer"),
    ("REV-04", "Platform vendor architecture and design review", "TA", "Spike", [21, 25, 26], 4, "A platform vendor is in the design", "M", "Design pack shared with the vendor under the right agreement|Vendor findings received in writing|Each finding accepted, rejected or deferred, with a reason", "Vendor review report and decisions", "Vendor solution architect"),
    ("REV-05", "Cloud best-practice review of the design", "TA", "Spike", [25, 26], 4, "Always", "M", "The design is checked against the cloud provider's best-practice framework|Gaps on security, reliability, cost and operations are logged", "Framework review record", "Cloud provider, platform team"),
    ("REV-06", "Findings log with severity, owner and due date", "PM", "Run", [14, 22], 5, "Always", "S", "Every finding is rated (blocker, major, minor, note)|Each has an owner and a date|Reviewed weekly until closed", "Findings log", "Reviewers"),
    ("REV-07", "Peer review standard for pipeline code", "TA", "Decision", [15, 18], 5, "Always", "S", "Every change is read by a second engineer before release|The checklist includes tests, reruns and data checks", "Standard and sample reviews", "Team"),
    ("REV-08", "Test evidence reviewed before acceptance", "BA + TA", "Slice", [16], 7, "Always", "S", "Test results are read by someone other than the tester|Gaps are fixed or accepted knowingly", "Review note", "Test team"),
    ("REV-09", "Production readiness review", "PM", "Decision", [24, 25, 28], 8, "Always", "M", "Operations, security and the business owner have each reviewed their part|Runbook, monitoring, recovery and access are checked|Conditions are written", "Readiness checklist", "Operations, security"),
    ("REV-10", "Sign-off register", "PM", "Document", [14, 22], 4, "Always", "S", "Each sign-off lists what is signed, by whom, on what evidence, with what conditions|Signers confirm they have read it|Conditional sign-offs have owners and dates", "Register", "Sponsor, signers"),
    ("REV-11", "Independent review of the estimate", "TA", "Spike", [19], 2, "Always", "S", "A person who did not make the estimate checks assumptions and what is missing|Range widened if assumptions are weak", "Review note", "Reviewer"),
    ("REV-12", "Vendor advice recorded as decisions, accountability kept", "TA + PM", "Decision", [14, 21], 4, "A vendor reviews the design", "S", "Each piece of vendor advice becomes a recorded decision with a reason|A named person on our side is accountable|Commercial interest of the vendor is noted", "Decision log", "Vendor"),
    # ---- go-live
    ("GLV-01", "Cut-over and rollback rehearsed", "TA", "Spike", [21, 25], 8, "Always", "M", "Rehearsed end to end|Rollback time known", "Rehearsal report", "Operations"),
    ("GLV-02", "First production load reconciled", "BA", "Slice", [15], 9, "Always", "M", "History and first loads match the trusted figures|Finance signs", "Signed reconciliation", "Finance"),
    ("GLV-03", "Hypercare plan and exit criteria", "PM", "Document", [24], 8, "Always", "S", "The period, who watches, and what ends it are written", "Plan", "Operations"),
    ("GLV-04", "Production sign-off by business and operations", "PM", "Decision", [14, 24], 9, "Always", "S", "Both sign|Open defects accepted knowingly", "Sign-off record", "Business owner, operations"),
    ("GLV-05", "Hand-over pack", "TA + BA", "Document", [9, 24], 10, "Always", "M", "Decision log, glossary, runbook and tests are handed over|Support team confirms they can use them", "The pack", "Support"),
    ("GLV-06", "Support team makes one real change unaided", "PM", "Spike", [9, 24], 10, "Always", "S", "A real change made by support while the team watches", "Change record", "Support"),
    ("GLV-07", "Benefits measured against the success measures", "BA", "Slice", [12, 27], 10, "Always", "S", "Each measure from PRJ-02 measured|Result reported to the sponsor", "Benefits report", "Sponsor"),
    ("GLV-08", "Lessons learned, risk register closed", "PM", "Document", [], 10, "Always", "S", "Lessons written and shared|Open risks handed to an owner", "Closure note", "Sponsor"),
]


# ---- second batch and the full area list (added 23 Nov 2026)
from de_ess_data2 import BACKLOG2, NEW_AREAS, DISC_MAP  # noqa: E402
BACKLOG = BACKLOG + BACKLOG2
AREAS = NEW_AREAS
