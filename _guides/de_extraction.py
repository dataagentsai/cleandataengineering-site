"""Knowledge extraction from people and systems, upstream and downstream, with AI: /how-we-work/data-essentials/extraction/.

    python3 _guides/de_extraction.py      (then python3 _guides/de_essentials.py, python3 _site/nav.py, python3 _site/seo.py)

A catalogue of 22 things to extract (what, why, if missing, from whom, means, AI help, access, precautions, what goes wrong),
plus means, a safe AI-assisted workflow, access, precautions, failures, and a knowledge-record template.
Deterministic first: facts are computed by queries; AI drafts and explains; owners confirm.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import de_essentials as DE  # noqa: E402
import de_ess_data as D  # noqa: E402

E, R, T, AR, S, table, fig, Lx, L, C = DE.E, DE.R, DE.T, DE.AR, DE.S, DE.table, DE.fig, DE.Lx, DE.L, DE.C
BLUE, MINT, BUTTER, ROSE, LAV, GREY = DE.BLUE, DE.MINT, DE.BUTTER, DE.ROSE, DE.LAV, DE.GREY
BASE = DE.BASE
URL_PATH = f"{BASE}extraction/"

GROUPS = [("A", "Meaning and structure"), ("B", "Content and quality"), ("C", "Change and history"), ("D", "Downstream: the consumers"), ("E", "Rules, risk and non-functional")]

# id, group, name, direction (Up/Down/Both), what, why, if missing, people, systems, means, ai, ai limit, access, precautions, what goes wrong, backlog, needed by stage, priority
ITEMS = [
    (1, "A", "Business meaning of fields, codes and statuses", "Both", "What each field, code and status means, in business words.", "Every number depends on it.",
     "Wrong joins and filters. Numbers disagree with finance. Rework in the last weeks.", "Source owner, business owner, long-serving users.",
     "Data dictionary, lookup and code tables, screen labels, column comments.", "Walk through the real screen and the real table side by side. Read the lookup tables. Compare labels with column names.",
     "Drafts a glossary from column names, comments and sample values, and proposes meanings for codes.", "Sounds right and may be invented. Mark 'inferred' until the owner confirms.",
     "Metadata read, a sample extract, demo access to the application.", "Do not paste real customer values into unapproved AI. Confirm each code in writing.",
     "One code reused for two meanings over the years. An AI guess accepted as fact.", ["SRC-02", "SRC-10", "PRJ-16"], 3, "Must"),
    (2, "A", "Relationships between tables and entities", "Up", "How tables relate: one-to-many, many-to-many, optional links, orphans.", "Joins define every report.",
     "Rows duplicated or lost on joins. Wrong totals.", "Source developers, database administrators, power users.",
     "Declared foreign keys, ER diagrams, query logs, application code models.", "Read declared keys. Infer undeclared links by name and by value overlap, meaning what share of values in table A exist in table B. Read frequent joins from query logs. Count orphans.",
     "Suggests likely links from names and descriptions, and explains an ER diagram in plain words.", "Similar names mislead. Overlap must be computed, not guessed.",
     "Metadata read, a read-only query on a replica, query logs.", "Overlap queries scan big tables. Sample them and run off-peak.",
     "An undeclared relationship is missed. A many-to-many treated as one-to-many inflates totals.", ["SRC-03", "SRC-10"], 3, "Must"),
    (3, "A", "Keys", "Up", "What uniquely identifies a record: technical IDs, business keys, composite keys. Are keys reused or changed?", "Deduplication, updates, history and joins all rest on keys.",
     "Duplicates. Lost updates. History attached to the wrong record.", "Source owner, database administrator.",
     "Primary and unique constraints, index definitions, uniqueness measured on real data.", "Read constraints. Test uniqueness on real data. Test stability: does a key change over time? Check reuse after deletion.",
     "Proposes candidate keys and explains composite keys.", "Unique today is not a promise for tomorrow.",
     "Metadata read, read-only query on a replica.", "Test across the full history, not the last 30 days.",
     "Keys recycled after a delete. A key that is unique only within a region.", ["CLN-01", "CLN-07"], 3, "Must"),
    (4, "A", "Constraints and rules", "Up", "Declared and hidden limits: mandatory fields, allowed values, ranges, formats, referential rules, rules enforced only in the application.", "They define what 'valid' means.",
     "The pipeline rejects good rows or accepts bad ones.", "Source owner, testers.",
     "Schema constraints, check constraints, triggers, validation code in the application.", "Read the table definitions. Compare with the data: violations show a rule that is not enforced. Read the validation code.",
     "Summarises validation code and triggers into plain rules.", "Misses rules in other layers.",
     "Table definition read, code repository read.", "Rules on paper and rules in the data differ. Always test against data.",
     "A constraint exists but is switched off, and the data breaks it.", ["CLN-02", "CLN-03"], 3, "Should"),
    (5, "A", "System flow", "Both", "How data enters, moves and leaves the system: interfaces, jobs, order, dependencies, manual steps.", "It shows what depends on what.",
     "Surprise feeds. Wrong load order. Hidden manual fixes.", "Source owner, operations and support, integration team.",
     "Job scheduler, integration platform, API specifications, run logs, network diagrams.", "Draw the flow with the owner. Read scheduler definitions and run logs. Trace one record end to end.",
     "Turns scheduler settings and scripts into a draft flow diagram and dependency list.", "Cannot see manual steps or undocumented jobs.",
     "Scheduler read, log read, repository read.", "Read-only. Never trigger a job.",
     "A manual file upload at midnight that nobody mentions.", ["SRC-05", "RUN-01"], 3, "Must"),
    (6, "A", "Transactional (OLTP) or analytical (OLAP)", "Up", "Is the source transactional (many small writes, current state, normalised) or analytical (history, aggregated, read-heavy)?", "It decides the loading method and the risk to the source.",
     "Heavy queries slow a live system. Wrong expectations about grain and history.", "Database administrator, architect.",
     "Database type, workload statistics, indexes, replicas, table design.", "Ask workload questions. Read database statistics. Check for a read replica or a warehouse. Look at the design: normalised tables or a star shape.",
     "Classifies tables as transactional or analytical from their structure and describes load risks.", "Needs workload data to confirm.",
     "Database metadata, performance statistics.", "Never run big scans on a live transactional primary.",
     "A profiling query on the production primary slows the application.", ["SRC-08", "LND-02"], 3, "Must"),
    (7, "B", "Production data samples", "Up", "Real extracts, not test data, covering several periods and edge cases.", "Real data differs from test data in ways nobody predicts.",
     "Design on guessed data. Surprises at acceptance.", "Source owner, and security for approval.",
     "A read replica, a masked copy, an export.", "Request a masked sample across time (peaks, month-end, year-end) and a set of known-bad records. Compare with test environment data.",
     "Helps spot patterns once the data is masked.", "Never on raw sensitive data unless the environment is approved and private.",
     "Read-only access to a replica or a masked export, with written approval.", "Mask or pseudonymise personal data. Store only in approved places. Delete after use. Log what you took.",
     "A sample from a quiet week. Unmasked personal data on a laptop.", ["SRC-03", "SRC-09"], 3, "Must"),
    (8, "B", "Profiling", "Up", "Measured facts: row counts, blanks, distinct values, ranges, patterns, duplicates, date coverage, skew.", "It replaces opinion with measurement.",
     "Quality and volume problems are found late.", "An engineer runs it; the BA reads it with the owner.",
     "Profiling queries or a profiling tool on a replica or masked copy.", "Run a standard profile per table. Review it with the owner: is this normal? Compare periods.",
     "Writes the profiling queries, explains results in plain words and flags oddities.", "The facts must come from queries, not from the model's memory.",
     "Read-only query on a replica or a masked copy.", "Time-box and sample. Run off-peak. Profile the full history for keys and dates.",
     "Profiling masked data hides real format problems. A biased sample misleads.", ["SRC-03", "PRJ-08"], 3, "Must"),
    (9, "B", "Existing data quality", "Both", "Known problems, the rules in use today, manual fixes, who cleans what.", "It shows what 'good' already means, and what people quietly fix.",
     "Surprises that are then blamed on the new platform.", "Data stewards, report owners, support.",
     "Data quality tool results, incident tickets, error and reject tables.", "Ask 'what do you fix by hand?'. Read the tickets. Check the error and reject tables. Compare a report with its source.",
     "Summarises tickets into recurring themes.", "Misses problems nobody reported.",
     "Ticket system read, quality results read.", "Tickets can hold personal data.",
     "Teams hide known issues. Manual fixes in spreadsheets stay unseen.", ["CLN-02", "CLN-04"], 3, "Should"),
    (10, "B", "Volumes, growth and peaks", "Up", "Row counts, size, daily growth and peaks such as month-end or campaigns.", "It sizes the design, the window and the bill.",
     "An undersized design. A cost shock. A load that overruns its window.", "Database administrator, operations.",
     "Database statistics, storage metrics.", "Read the statistics. Chart growth over 12 to 24 months. Ask about peaks.",
     "Forecasts growth and explains charts.", "Needs real history to forecast from.",
     "Metrics read.", "Statistics may include test data.",
     "A peak ten times the average, found at go-live.", ["SRC-08", "LND-02"], 3, "Should"),
    (11, "C", "How records change", "Up", "How records are inserted, updated, corrected, arrive late. Is there a modified date? Can history be rewritten?", "It decides whether we can load only what changed.",
     "We cannot load only the changes. Silent changes. Wrong history.", "Source owner, source developer.",
     "Audit columns, change logs, change data capture, update patterns in the data.", "Ask. Inspect audit columns. Compare two extracts a day apart to see what changed. Check late arrivals.",
     "Reads the update code to explain what changes records.", "Cannot see behaviour that is not in the code.",
     "Read on a replica, log read.", "Do not trust a modified date until you have checked that it is maintained.",
     "Bulk fixes that do not update the modified date.", ["SRC-04", "LND-06", "CLN-09"], 3, "Must"),
    (12, "C", "How records are deleted", "Up", "Are records hard-deleted, flagged as deleted, archived or purged? Can deleted rows reappear?", "Deletes are invisible unless you plan for them.",
     "Deleted records stay in reports for ever. Totals drift.", "Source owner, database administrator.",
     "Delete flags, audit and trash tables, purge jobs, change events.", "Ask. Look for flags. Compare full snapshots to see what disappeared. Read the purge jobs.",
     "Finds purge and delete logic in code and scripts.", "Cannot see manual deletes.",
     "Read on a replica, code read.", "Know how privacy erasure requests must flow through.",
     "Hard deletes that an incremental load never sees.", ["SRC-04", "LND-10"], 3, "Must"),
    (13, "C", "Historical load", "Up", "How far back data exists, where old data lives, how formats and rules changed, how long a full load takes.", "The first load is often the hardest.",
     "History is incomplete or inconsistent. The first load fails.", "Source owner, finance for the periods needed.",
     "Archive tables, backups, old schemas.", "Map history by period. Sample the oldest and middle periods. List schema changes. Time a trial load.",
     "Compares schemas across years and lists the changes.", "Needs the old schemas to compare.",
     "Archive read.", "Old data may use different definitions. Run trial loads off-peak.",
     "A currency or code change mid-history. An archive in a different format.", ["LND-02", "LND-09"], 3, "Should"),
    (14, "C", "Schedules, windows and service levels", "Up", "When data refreshes, source batch windows, change freezes, existing service levels.", "It decides when we may load, and what 'fresh' means today.",
     "Our load collides with the source batch. Staleness complaints.", "Operations, source owner.",
     "Scheduler, calendars.", "Read schedules. Ask about freezes such as month-end and year-end.",
     "Summarises scheduler settings.", "Does not know the unwritten freezes.",
     "Scheduler read.", "Read-only.",
     "A freeze period blocks go-live.", ["LND-07", "RUN-01"], 3, "Should"),
    (15, "D", "Consumers and their needs", "Down", "Who uses the data, for which decision, how fresh, how detailed, and who may see what.", "It sizes and shapes the whole platform.",
     "Wrong freshness or detail. Surprise consumers at go-live.", "Business owners, users, owners of downstream applications.",
     "Report catalogue, access lists, API consumers, usage logs.", "Build a consumer register. Interview. Read access lists and usage logs to find consumers nobody mentioned.",
     "Groups usage logs into consumer groups and drafts the register.", "Usage is not importance.",
     "Usage logs read, access lists read.", "Usage logs identify people. Handle them as personal data.",
     "A finance spreadsheet that pulls data every night, unknown to IT.", ["CON-01", "CON-02", "CON-11"], 3, "Must"),
    (16, "D", "Existing Power BI dashboards", "Down", "What each report shows, and the model behind it: tables, relationships, measures, filters, row-level security, refresh schedule, data sources.", "It is the real specification of the numbers people already trust.",
     "The rebuild gives different numbers, and users reject the new platform.", "Report owners, report authors, power users.",
     "Power BI service and workspaces, the report files, the dataset model through its read endpoint, the admin inventory interface, usage metrics.",
     "Walk through each page with its author. Export the model: tables, relationships, measures. Read the measure formulas and the data-preparation steps. List data sources and refresh times. List slicers and security roles. Check usage. Test against known values.",
     "Explains the formulas and preparation steps in plain rules, compares two reports and drafts a metric catalogue.", "Filter context is subtle. Verify with known numbers.",
     "Workspace viewer or admin rights, read access to the dataset model, the admin inventory interface. No edit rights.", "Read-only. Do not change or refresh. Files may hold embedded credentials or data. Respect row-level security and tool licence terms.",
     "Measures that use hidden filters. Manual steps in a file. Hard-coded values. Personal copies of reports.", ["SRC-12", "CON-04", "MNG-01"], 3, "Must"),
    (17, "D", "Metric definitions in use today", "Down", "How each KPI is calculated today, and who owns it.", "Two numbers with one name start every argument.",
     "Disagreement over numbers after go-live.", "Finance, business owners.",
     "Report measures, spreadsheets, queries.", "Collect each KPI from every place it is used. Put them side by side on the same data.",
     "Extracts formulas from reports and queries and groups similar metrics.", "May merge metrics that differ in a small but important way.",
     "Report model read, query read.", "Show both numbers to the owner before deciding.",
     "Same name, different formula.", ["MDL-03", "MNG-02"], 3, "Must"),
    (18, "D", "Report and data usage", "Down", "Which reports and tables are actually used, by whom, how often.", "It keeps scope honest: do not migrate what nobody uses.",
     "Migrating everything. Effort spent on dead reports.", "BI administrators.",
     "Usage metrics, query logs.", "Read 6 to 12 months of usage.",
     "Summarises usage and flags what looks unused.", "A quarterly report looks unused in a one-month window.",
     "Admin usage logs read.", "Usage identifies people.",
     "A year-end report judged unused in March.", ["CON-04", "PRJ-04"], 3, "Should"),
    (19, "E", "Business rules hidden in code", "Both", "Rules in stored procedures, ETL jobs, macros, spreadsheets and scripts.", "These are the rules nobody wrote down.",
     "Rules are lost in the migration, and the numbers change.", "The authors, support.",
     "Code repositories, database procedures, ETL tool definitions, spreadsheet macros.", "Read the code with its owner. Trace one output column back to its sources.",
     "Explains SQL, ETL and stored procedures as plain rules and drafts column-level lineage.", "Can be wrong on dialect details. Verify by running both and comparing.",
     "Code read.", "Code may contain secrets. Do not paste it into unapproved tools.",
     "A rule that lives only in a macro on one person's laptop.", ["SRC-12", "CLN-02"], 3, "Must"),
    (20, "E", "Sensitive data and today's access rules", "Both", "Which fields are personal or regulated, who may see what today, masking and retention.", "It decides what we may copy, and where.",
     "A late stop. A leak.", "Security, privacy, data owners.",
     "Catalogue tags, access roles, database permissions, masking policies.", "Classify fields. Read permissions and roles. Compare real access with the policy.",
     "Suggests classifications from names and samples, for review.", "Never final. A person confirms.",
     "Security metadata read.", "Work from metadata. Avoid raw samples.",
     "Personal data hidden in free-text fields.", ["SRC-09", "SEC-01", "MNG-03"], 3, "Must"),
    (21, "E", "Non-functional behaviour of the existing system", "Both", "How the current system behaves: response times, availability, recovery targets, volumes, security, audit, support, cost, retention.", "Users judge the new system against the old one's behaviour, spoken or not.",
     "The new platform is slower or less available than the old one, and users complain.", "Operations, support, owners, finance.",
     "Monitoring, service-level reports, incident history, cost reports.", "Collect current service levels and real measurements. Ask what would make users say it is worse. Read incident statistics.",
     "Summarises monitoring reports and incident history.", "Measured and promised levels differ.",
     "Monitoring read, cost reports read.", "Quote measured numbers, not promises.",
     "An unwritten expectation, such as 'the report opens in three seconds'.", ["RUN-05", "COS-01", "MDL-10"], 3, "Should"),
    (22, "E", "Known issues, incidents and workarounds", "Both", "What breaks, how often, and the workarounds people use.", "A workaround is often the real process.",
     "We repeat the same failures.", "Support, power users.",
     "Tickets, incident reviews, email threads.", "Review the last 12 months of tickets. Ask for the workarounds.",
     "Groups tickets into themes.", "Misses problems that were never raised.",
     "Ticket system read.", "Tickets can hold personal data.",
     "A manual workaround that is the real process.", ["CLN-04", "RUN-05"], 3, "Could"),
]

MEANS = [
    ("People", "Interview", "One person, one topic, 45 minutes, with a real screen or report in front of you.", "Meaning, rules, history, pain.", "People describe the process as it should be."),
    ("People", "Workshop", "A small group draws the flow or settles a definition on a whiteboard.", "System flow, definitions, scope.", "Loud voices; quiet experts stay silent."),
    ("People", "Shadowing", "Watch a user or operator do the real task.", "Workarounds, manual steps, real use.", "Behaviour changes when watched."),
    ("People", "Questionnaire", "A written list answered by the owner.", "Many sources, same questions.", "Answers are short and unchecked. Follow up."),
    ("Systems", "Metadata query", "Read table, column, key and constraint definitions from the system catalogue.", "Structure, keys, constraints.", "Describes the design, not the data."),
    ("Systems", "Profiling", "Measure counts, blanks, ranges, patterns and duplicates.", "Quality, volumes, keys, dates.", "A sample can hide the problem."),
    ("Systems", "Snapshot comparison", "Compare two extracts a day apart.", "Updates, deletes, late records.", "Needs access twice."),
    ("Systems", "Logs", "Query logs, job logs, usage logs, change logs.", "Real joins, flow, consumers, usage.", "May contain personal data."),
    ("Artefacts", "Code reading", "Stored procedures, ETL jobs, macros, scripts.", "Hidden rules, lineage.", "Code may be dead or secret-laden."),
    ("Artefacts", "Report reverse engineering", "Export the model and formulas of existing reports.", "Metric definitions, filters, security.", "Context and filters are subtle."),
    ("Artefacts", "Documents and tickets", "Specifications, data dictionaries, incident history.", "Intent, known issues.", "Often out of date. Check the date."),
    ("With AI", "Draft and explain", "AI reads schemas, code, reports and transcripts, and drafts glossaries, rules and summaries.", "Speed on large text and code.", "Can invent. Owners confirm."),
]

AI_TASKS = [
    ("Draft a glossary from column names, comments and sample values", "Starting point for the owner's review", "Final meanings", "Owner confirms each; label 'inferred' until then"),
    ("Explain stored procedures, ETL and SQL as plain rules", "Fast reading of code nobody remembers", "Exact behaviour on dialect edge cases", "Run old and new on the same data and compare"),
    ("Translate report formulas and preparation steps into plain rules", "Reverse engineering of existing reports", "Subtle filter context", "Test against known values from the live report"),
    ("Suggest relationships and candidate keys from names and descriptions", "Narrowing where to look", "Deciding what is true", "Compute value overlap and uniqueness with queries"),
    ("Write profiling queries and explain the results", "Saves engineer time", "Producing the facts itself", "Facts come from the query output, not the model"),
    ("Summarise interview transcripts and tickets", "Themes across many documents", "What people did not say", "Read the source for anything that matters"),
    ("Cluster usage logs into consumer groups", "Finding unknown consumers", "Ranking importance", "Confirm each group with the business owner"),
    ("Suggest sensitive-data classifications", "A first pass over many columns", "A final classification", "Privacy owner confirms"),
    ("Draft a column-level lineage from code", "Fast first map", "Complete lineage", "Spot-check by tracing a real record")]

ACCESS = [
    ("Source database, read-only", "Profiling, keys, relationships, changes", "A read-only user on a replica or a masked copy", "Source owner and security", "1 to 4 weeks"),
    ("Metadata and catalogue read", "Structure, constraints, tags", "Read of definitions only, no data", "Source owner", "Days"),
    ("Query and usage logs", "Real joins, consumers, usage", "Aggregated or pseudonymised logs", "Security", "1 to 3 weeks"),
    ("Application demo access", "Meaning, screens, flow", "A training or demo account", "Application owner", "Days"),
    ("Code repository, read", "Hidden rules, lineage", "Read-only access to named repositories", "Engineering manager", "Days"),
    ("Scheduler and job logs, read", "Flow, schedules", "Read-only view", "Operations", "Days"),
    ("BI workspace and dataset model, read", "Dashboard reverse engineering", "Viewer or admin read, with no edit rights", "BI owner", "1 to 2 weeks"),
    ("Production data sample", "Real values, edge cases", "Masked, time-limited extract in an approved place", "Data owner, privacy and security", "2 to 6 weeks"),
    ("Monitoring and cost reports", "Non-functional, volumes, cost", "Read-only dashboards", "Operations, finance", "Days"),
    ("Time from people", "Everything", "A booked slot, with the questions sent first", "Their manager, via the PM", "1 to 3 weeks"),
]

PRECAUTIONS = [
    ("Read-only, always", "You are guests in someone else's system. A mistake is their incident."),
    ("Use a replica or a masked copy, not the live primary", "A heavy query can slow the application for everyone."),
    ("Run big queries off-peak, with a time limit and a sample", "Protects the source and your relationship with its owner."),
    ("Get access in writing, and log what you took", "Auditors and owners will ask."),
    ("Keep personal data out of notes, chats and AI tools", "Privacy law applies to your working copies too."),
    ("Use only approved AI, in an approved place", "Public assistants are the most common leak."),
    ("Label every statement: confirmed, observed, inferred or unknown", "So that a guess never becomes a fact."),
    ("Confirm in writing what you understood, and ask the owner to correct it", "Cheapest way to catch a misunderstanding."),
    ("Check the date of every document and the period of every sample", "Old documents and quiet-week samples mislead."),
    ("For reverse engineering, respect licence terms and row-level security", "Reports of your own organisation are fair game. Vendor products may restrict it."),
    ("Do not change anything in the source or the report", "Changing a refresh or a filter changes someone's numbers."),
    ("Bring findings as questions, not blame", "People who feel blamed stop helping.")]

WRONG = [
    ("A profiling query slows production", "Run on the primary at 10 a.m.", "The application slows; access is withdrawn", "Replica, off-peak, time limit"),
    ("An AI guess becomes a fact", "A drafted meaning is copied into the design", "Wrong numbers that look documented", "Status labels; owner confirms"),
    ("Sensitive data reaches an AI tool", "Real rows pasted to a public assistant", "A privacy incident", "Approved AI only; mask first; metadata not rows"),
    ("The sample is not representative", "Only the last 30 days or one region", "Surprises in production", "Sample across periods and edge cases"),
    ("An old document is trusted", "The data dictionary is three years old", "Wrong rules built in", "Check the date; compare with data"),
    ("Experts disagree and nobody settles it", "Two answers noted, none chosen", "Two definitions in production", "Side by side on real data; the owner decides"),
    ("Hidden manual steps are missed", "The code is clean but a person fixes files", "Migrated numbers differ", "Shadow the operator; ask what is fixed by hand"),
    ("Reverse engineering misses filter context", "A measure reads the same but filters differently", "The rebuilt report disagrees", "Test with known values at several filters"),
    ("Access takes weeks", "Requests start in week three", "The team waits", "Raise every request in week one"),
    ("The replica lags or differs", "The replica is hours behind", "Counts do not match the source", "Check lag before comparing"),
    ("Masked data hides the real problem", "Formats are changed by masking", "Real format issues found late", "Mask in a way that keeps the shape"),
    ("People feel blamed", "Findings delivered as faults", "Experts stop sharing", "Frame as questions; credit the source")]

RECORD = [("Statement", "One fact, in a sentence. 'A deleted order stays in the table with status X.'"), ("Evidence", "The query, the screenshot, the document or the transcript line."), ("Source", "A person or a system, with the date."),
          ("Status", "Confirmed by the owner / Observed in data / Inferred (AI or analyst) / Unknown."), ("Confirmed by", "Name and date, or blank."), ("Impact", "Which design, rule or backlog item depends on it."), ("Review date", "When it must be checked again.")]

QA = [("What if we cannot get any of this?", "Then every missing item becomes a risk with an owner and a date, and the estimate widens accordingly. Do not fill the gap with assumptions that nobody has agreed. The 'if missing' notes on each item say what usually breaks."),
      ("Where does AI help most?", "Reading large amounts of text and code: explaining old stored procedures, translating report formulas, drafting glossaries and summarising tickets. It helps least with facts about the data itself, which should be measured by queries."),
      ("Can I paste real data into an AI assistant?", "Only into an AI service your organisation has approved for that data class. Otherwise give it metadata, such as column names, types and a few made-up examples."),
      ("Which items are the minimum?", "The ones marked Must: meaning, relationships, keys, system flow, the type of system, a production sample, profiling, how records change and are deleted, consumers, existing dashboards, metric definitions, hidden rules and sensitive data."),
      ("Who does the extraction?", "The BA leads people and artefacts, the Tech Anchor leads systems and profiling, and the PM clears access and the owners' time. See the three seats page.")]


def d_map():
    b = R(150, 40, 380, 100, BLUE, ["Upstream · from people", "source owners, DBAs, support, long-serving users"], 17) + R(550, 40, 380, 100, GREY, ["Upstream · from systems", "tables, data, code, jobs, logs"], 17)
    b += R(150, 160, 380, 100, BUTTER, ["Downstream · from people", "business owners, report authors, users"], 17) + R(550, 160, 380, 100, MINT, ["Downstream · from systems", "reports, models, usage logs, access lists"], 17)
    b += T(90, 94, "Upstream", 17) + T(90, 214, "Downstream", 17) + T(340, 28, "People", 17) + T(740, 28, "Systems and artefacts", 17)
    b += R(150, 282, 780, 54, LAV, ["AI sits across all four: it drafts, explains and summarises. Owners confirm."], 16, sw=2.5)
    return S(1000, 350, b, "A map of where knowledge lives. Upstream from people: source owners, database administrators, support. Upstream from systems: tables, data, code, jobs and logs. Downstream from people: business owners, report authors, users. Downstream from systems: reports, models, usage logs and access lists. AI sits across all four, drafting and explaining, and owners confirm.")


def d_workflow():
    b = R(10, 40, 215, 90, BLUE, ["1 Compute the facts", "queries, profiling, counts"], 16) + AR(227, 85, 262, 85) + R(264, 40, 215, 90, LAV, ["2 AI drafts and explains", "meanings, rules, summaries"], 16)
    b += AR(481, 85, 516, 85) + R(518, 40, 215, 90, BUTTER, ["3 The owner confirms", "in writing"], 16, sw=2.5) + AR(735, 85, 770, 85) + R(772, 40, 218, 90, MINT, ["4 Record with evidence", "and a status label"], 16)
    b += R(264, 160, 215, 60, ROSE, ["Not allowed", "real data to unapproved AI"], 14, dash=True) + AR(371, 158, 371, 132, dash=True)
    b += T(118, 160, "facts are measured,", 14) + T(118, 178, "never recalled", 14) + T(625, 160, "no label, no design decision", 14)
    return S(1000, 240, b, "A safe AI-assisted workflow in four steps: compute the facts with queries, let AI draft and explain, the owner confirms in writing, then record with evidence and a status label. Real data must never go to an unapproved AI tool.")


def d_powerbi():
    layers = [("Report pages", "what users see: visuals, filters, slicers", BLUE), ("The model", "tables, relationships, security roles", MINT), ("Measures", "the formulas: how each number is calculated", BUTTER),
              ("Data preparation", "the steps that clean and shape each table", LAV), ("Sources and refresh", "where data comes from, and when", GREY)]
    notes = ["Walk through each page with its author. List filters.", "Export the model. List relationships and roles.", "Read each formula. Write it in plain words.", "Read each step. Note manual or hard-coded values.", "List sources, credentials owner, refresh time."]
    b = ""
    for i, (n, s, f) in enumerate(layers):
        y = 14 + i * 66
        b += R(10, y, 400, 54, f, [n, s], 16) + AR(412, y + 27, 470, y + 27) + R(472, y, 518, 54, "#fff", [notes[i]], 14)
    b += T(500, 354, "then test: pick known numbers from the live report and reproduce them", 15)
    return S(1000, 370, b, "Reverse engineering a Power BI dashboard in five layers: report pages, the model, measures, data preparation, sources and refresh. At each layer, a note says what to extract. Finally test by reproducing known numbers from the live report.")


def item_card(it):
    (n, g, name, direction, what, why, miss, people, systems, means, ai, ailimit, access, prec, wrong, bl, stage, prio) = it
    bl_links = " ".join(f'<a href="{BASE}backlog/#{b}">{b}</a>' for b in bl)
    dr = {"Up": "Upstream", "Down": "Downstream", "Both": "Upstream and downstream"}[direction]
    return (f'<div class="sess" id="x{n}"><h3><span class="n">{n}</span>{E(name)} <span class="tag">{dr}</span> <span class="tag">{prio}</span></h3><dl>'
            f'<dt>What to extract</dt><dd>{E(what)}</dd><dt>Why it matters</dt><dd>{E(why)}</dd><dt>If we do not have it</dt><dd>{E(miss)}</dd>'
            f'<dt>From people</dt><dd>{E(people)}</dd><dt>From systems</dt><dd>{E(systems)}</dd><dt>How</dt><dd>{E(means)}</dd>'
            f'<dt>How AI helps</dt><dd>{E(ai)} <i>Limit: {E(ailimit)}</i></dd><dt>Access needed</dt><dd>{E(access)}</dd><dt>Precautions</dt><dd>{E(prec)}</dd>'
            f'<dt>What can go wrong</dt><dd>{E(wrong)}</dd><dt>Backlog items</dt><dd>{bl_links}</dd></dl></div>')


def page():
    overview = table(["#", "What to extract", "Direction", "Priority", "From people", "From systems"], [[str(it[0]), f'<a href="#x{it[0]}"><b>{E(it[2])}</b></a>', {"Up": "Upstream", "Down": "Downstream", "Both": "Both"}[it[3]], it[17], E(it[7]), E(it[8])] for it in ITEMS])
    cards = ""
    for g, gname in GROUPS:
        cards += f'<section id="g{g}"><p class="eyebrow">Group {g}</p><h2>{E(gname)}</h2>' + "".join(item_card(it) for it in ITEMS if it[1] == g)
        if g == "D":
            cards += fig(d_powerbi(), "Reverse engineering a dashboard, layer by layer. The numbers people trust live in the formulas, not the visuals.")
        cards += "</section>"
    means = table(["Where", "Means", "How", "Good for", "Watch out"], [[E(a), f"<b>{E(b)}</b>", E(c), E(d), E(e)] for a, b, c, d, e in MEANS])
    ai = table(["AI task", "Good for", "Not for", "Check by"], [[E(a), E(b), E(c), E(d)] for a, b, c, d in AI_TASKS])
    acc = table(["Access", "Needed for", "Least-privilege version", "Approved by", "Typical wait"], [[f"<b>{E(a)}</b>", E(b), E(c), E(d), E(e)] for a, b, c, d, e in ACCESS])
    prec = table(["Precaution", "Why"], [[f"<b>{E(a)}</b>", E(b)] for a, b in PRECAUTIONS])
    wr = table(["What goes wrong", "How it happens", "What it costs", "Prevention"], [[f"<b>{E(a)}</b>", E(b), E(c), E(d)] for a, b, c, d in WRONG])
    rec = table(["Field", "What to write"], [[f"<b>{E(a)}</b>", E(b)] for a, b in RECORD])
    toc = "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in [("#map", "The map"), ("#list", "What to extract: the 22 items"), ("#items", "Each item in detail"), ("#means", "The means"), ("#ai", "Using AI, safely"), ("#access", "Access needed"),
                                                                   ("#precautions", "Precautions"), ("#wrong", "What can go wrong"), ("#record", "Recording what you learn"), ("#faq", "FAQ")])
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/how-we-work/">How we work</a> › <a href="{BASE}">Data essentials</a> › <a href="{BASE}gather/">Gather information</a> › Extraction in depth</p>
<p class="eyebrow" style="margin-top:22px">Topic 8 · Deep dive</p>
<h1>Extracting knowledge from people and systems</h1>
<p class="lede">What to find out about a source system and its consumers, from whom, how, with what access, with AI as an assistant, and what goes wrong if you do not. Twenty-two things to extract, each with what happens when it is missing, how to get it, and the precautions.</p>
<div class="tf">
<nav class="toc"><b>On this page</b><ol>{toc}</ol></nav>
<section id="map"><p class="eyebrow">Teach first</p><h2>Knowledge lives in four places</h2>
<p>Look at it from two directions. <b>Upstream</b> is the systems the data comes from. <b>Downstream</b> is the reports and applications that use it. In each direction, knowledge sits in people's heads and in the systems and artefacts, such as code, reports, tickets and logs. AI can speed up all four, but it never replaces the owner saying 'yes, that is right'.</p>
{fig(d_map(), "Four places to look. People and systems often disagree, and the disagreement is the finding.")}
<div class="box"><b>The rule:</b> measure facts with queries, let AI draft and explain, and have the owner confirm. Never the other way round.</div></section>
<section id="list"><p class="eyebrow">What to extract</p><h2>Twenty-two items, in five groups</h2><p>Priority is for a typical project: <b>Must</b> items should be answered in discovery, <b>Should</b> before build, <b>Could</b> when time allows.</p>{overview}</section>
<section id="items"><p class="eyebrow">Each in detail</p><h2>What, why, if missing, from whom, how, AI, access, precautions, what goes wrong</h2></section>
{cards}
<section id="means"><p class="eyebrow">The means</p><h2>Ways to get the knowledge</h2>{means}</section>
<section id="ai"><p class="eyebrow">Using AI</p><h2>Where AI helps, and how to keep it safe</h2>
<p>AI is good at reading large amounts of text and code and at drafting. It is not a source of facts about your data. Follow four steps.</p>
{fig(d_workflow(), "Facts are measured. AI drafts. The owner confirms. Everything is recorded with a status label.")}{ai}</section>
<section id="access"><p class="eyebrow">Access</p><h2>What access you will need, and the least you can ask for</h2><p>Always ask for the least-privilege version first. It is approved faster, and it is safer for everyone.</p>{acc}</section>
<section id="precautions"><p class="eyebrow">Precautions</p><h2>Twelve rules for working in someone else's system</h2>{prec}
<p class="note">Related: the {Lx('/learn/responsible-ai/', 'Responsible AI')} page covers privacy and approved AI use in more detail.</p></section>
<section id="wrong"><p class="eyebrow">What can go wrong</p><h2>Twelve ways extraction itself fails</h2>{wr}</section>
<section id="record"><p class="eyebrow">Recording it</p><h2>A knowledge record</h2><p>Every finding goes into one shared place, with the same seven fields. A finding without a status is a rumour.</p>{rec}</section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(QA)}</section>
<section id="next"><p class="eyebrow">Go further</p><h2>Related pages</h2><ul>
<li>{L(BASE + 'gather/', 'Gather information: the short version')}</li><li>{L(BASE + 'layers/sources/', 'Layer: Sources (upstream)')}</li><li>{L(BASE + 'layers/consumers/', 'Layer: People use it (downstream)')}</li>
<li>{L(BASE + 'backlog/', 'The corpus backlog')}</li><li>{L(BASE + 'why-fail/', 'Why data projects fail')}</li><li>{Lx('/learn/data-systems/upstreams/questionnaire/', 'Source system questionnaire')}</li>
<li>{Lx('/learn/data-systems/downstreams/', 'Downstreams: know your consumers (technical)')}</li><li>{Lx('/learn/power-bi-vs-databricks-ai-bi/power-bi/', 'Power BI and Fabric, in depth (technical)')}</li></ul></section>
<div class="pn">{L(BASE + 'gather/', '← Gather information')}{L(BASE, 'The roadmap')}{L(BASE + 'layers/landing/', 'Next: landing →')}</div>
</div>"""
    title = "Extracting knowledge from people and systems"
    desc = ("What to find out about source systems and consumers, from whom and how: twenty-two items from keys and deletes to existing Power BI dashboards, "
            "with AI assistance, access needed, precautions and what can go wrong.")
    return DE.page_shell(title, desc, URL_PATH, body, [("How we work", "/how-we-work/"), ("Data essentials", BASE), ("Gather information", BASE + "gather/"), ("Extraction in depth", URL_PATH)], QA)


def main():
    DE.write(URL_PATH, page())


if __name__ == "__main__":
    main()
