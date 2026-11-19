"""Project detail data, group "standards" (file D): the two pharma agents (19 Nov 2026).

Public page: no employer, no personal names beyond the lead, no account ids.
A trailing " ✓" on a binding's tech means that binding is actually built or confirmed.
"""

LEAD = "Basant Choudhary"

PROJECTS = [
    {
        "id": "clinical-data-review-agent",
        "title": "Clinical-trial data review agent",
        "subject": "ai",
        "group": "standards",
        "status": "active",
        "started": "2026-10",
        "lead": LEAD,
        "one_liner": "An agent that finds impossible or inconsistent patient data in a clinical trial and drafts the query sent to the site.",
        "purpose": (
            "In a clinical trial, a data manager reads patient records looking for things that cannot be true: a visit before "
            "consent, a lab value out of range, a serious adverse event with no matching entry. Fixed rules catch many of "
            "these; the rest need someone to read across one patient's whole record and use judgement. This agent does that "
            "reading and drafts the question to send to the trial site. A person approves every query; the agent never "
            "sends one itself. It uses the public CDISC pilot study data, so no real patient or employer data is involved."
        ),
        "audience": "Clinical data managers, pharma data engineers, anyone learning how an agent fits a regulated data job.",
        "benefits": [
            ("Less reading, same care", "The agent reads the whole record and proposes only the queries worth sending."),
            ("Rules first, model second", "Deterministic checks run before any model call, so the model sees only what rules cannot decide."),
            ("A person sends every query", "Drafts wait for approval, so nothing reaches a site unreviewed."),
            ("Measured, not claimed", "A planted trial with known problems gives recall and cost per patient from real runs."),
            ("Safe with hostile text", "A hidden instruction planted in the data is tested, and was resisted in both runs."),
        ],
        "functional": [
            "Reads one patient's visits, labs, adverse events and medications through typed read-only tools.",
            "Runs deterministic edit checks first and keeps their findings separate from the agent's.",
            "Drafts a plain-language query for each problem worth raising, with the evidence attached.",
            "Waits for a data manager to approve, edit or reject each draft.",
            "Scores itself against a planted trial of 24 known problems and 16 clean patients.",
        ],
        "nonfunctional": [
            "The model never writes SQL; it calls named tools over certified tables.",
            "Text inside patient records is treated as data, never as instructions.",
            "Every run is recorded so a past review can be replayed.",
            "Cost per patient is measured and reported with the results.",
            "No real patient data and no employer system or data is used.",
        ],
        "components": [
            ("Trial system", "Holds the study data and receives approved queries."),
            ("Data layer", "Lays the study data out in standard clinical tables."),
            ("Edit checks", "Rules that catch the problems rules can catch."),
            ("Agent", "Reads across a patient's record and drafts queries."),
            ("Model", "Judges whether a finding is worth sending."),
            ("Reviewer desk", "Where a data manager approves or rejects drafts."),
            ("Evaluation", "Scores recall, checks and cost against a planted trial."),
        ],
        "flows": [
            ("Trial system", "Data layer", "study data"),
            ("Data layer", "Edit checks", "tables"),
            ("Data layer", "Agent", "read tools"),
            ("Agent", "Model", "judgement call"),
            ("Edit checks", "Reviewer desk", "findings"),
            ("Agent", "Reviewer desk", "draft queries"),
            ("Reviewer desk", "Trial system", "approved query"),
            ("Agent", "Evaluation", "run record"),
        ],
        "bindings": {
            "Open stack": {
                "Trial system": "OpenClinica Community 3.x, public CDISC pilot data (set up)",
                "Data layer": "SDTM-aligned tables, local files ✓",
                "Edit checks": "Python rules, 202 of 202 checks pass ✓",
                "Agent": "Claude tool-use loop, in-process tools ✓",
                "Model": "Claude ✓",
                "Reviewer desk": "files for the data manager to mark ✓",
                "Evaluation": "planted trial, scorer, batch runner ✓",
            },
            "Databricks": {
                "Data layer": "Delta tables in Unity Catalog (designed, not built)",
                "Agent": "tools as Unity Catalog functions (designed, not built)",
                "Evaluation": "MLflow evaluation (designed, not built)",
            },
            "Azure": {
                "Agent": "not built",
            },
        },
        "work": [
            ("Version 1", [
                ("Planted trial: 24 problems of 12 kinds, 16 clean patients", "done", "M", "Clinical data"),
                ("Deterministic edit checks (202 of 202 pass)", "done", "M", "Python"),
                ("Agent loop with read tools, scored: recall 21 of 24 (87.5%), $0.21 per patient", "done", "M", "Agents"),
                ("Injection test: hidden instruction resisted 2 of 2", "done", "S", "Security"),
                ("First reviewer labels: 5 of 5 drafts worth sending", "done", "S", "Clinical data review"),
            ]),
            ("Version 2", [
                ("Visit-window and age rules", "todo", "M", "Clinical data"),
                ("Study notes for study-wide blanks", "todo", "M", "Agents"),
                ("The worth-sending gate", "todo", "M", "AI testing"),
            ]),
            ("On a lakehouse", [
                ("Ingest the pilot data into Delta tables with clinical-standard layers", "todo", "L", "Data engineering"),
                ("Write approved queries back to the trial system as discrepancy notes", "todo", "M", "Integration"),
            ]),
        ],
        "roles": [
            ("Clinical data reviewer", 1, "1-2 hours/week", "Labels drafts, says which queries are worth sending."),
            ("Data engineer", 1, "3-5 hours/week", "Owns the data layer and the edit checks."),
            ("Agent engineer", 1, "3-5 hours/week", "Owns the agent loop, tools and evaluation."),
        ],
        "learn": [
            "Where an agent fits in clinical data management, and where plain rules are better.",
            "How to give a model typed tools over certified tables instead of raw SQL.",
            "How to build a planted-problem test set and measure recall and cost honestly.",
            "How to test for instructions hidden inside data.",
        ],
        "questions": [
            "Which of the 24 planted problems should a rule catch instead of the agent?",
            "What would you change so a reviewer's rejection teaches the agent?",
            "What breaks first when this runs on a real study with 100 times the patients?",
        ],
        "repo": "",
        "repo_public": False,
        "links": [
            ("Course: the agent harness, end to end", "/learn/agent-harness/"),
            ("Companion project: drug-safety signal investigator on Databricks", "/projects/drug-safety-agent-databricks/"),
        ],
        "good_first": [
            "Review a sample of draft queries and say which you would send",
            "Propose one more planted problem and its expected finding",
        ],
    },

    {
        "id": "drug-safety-agent-databricks",
        "title": "Drug-safety signal investigator on Databricks",
        "subject": "ai",
        "group": "standards",
        "status": "starting",
        "started": "2026-11",
        "lead": LEAD,
        "one_liner": "A pharmacovigilance agent built only on Databricks' own AI services, from public FDA data.",
        "purpose": (
            "Drug-safety teams ask a recurring question: is there a signal that this drug causes this event? Answering it "
            "means counting adverse-event reports, comparing against other drugs, checking whether the label already warns "
            "about it, and judging whether the pattern is real or a reporting artefact. The path is not known in advance, "
            "which is what makes it a fit for an agent. This project builds that investigator end to end using Databricks' "
            "own AI offerings: Unity Catalog, Foundation Model APIs, Unity Catalog functions as tools, Mosaic AI Agent "
            "Framework and MLflow. It is also the worked example for the Databricks AI row of the platform page. A safety "
            "scientist approves every assessment; the agent files nothing. Data is public openFDA reports and drug labels."
        ),
        "audience": "Databricks and pharma data teams, architects choosing a lakehouse AI stack, people preparing for AI architect roles.",
        "benefits": [
            ("Numbers by code, judgement by model", "Report counts and disproportionality statistics are computed in code, never by the model."),
            ("Governed by design", "Data, tools and permissions sit in Unity Catalog, so the agent sees only what it is allowed to."),
            ("Every step traced", "MLflow records each tool call, so an assessment can be audited later."),
            ("Honest about the platform", "Where a Databricks service is not available on a free workspace, the guide says so and shows the workaround."),
            ("Reusable pattern", "The same shape fits other safety, quality and compliance investigations."),
        ],
        "functional": [
            "Takes a drug and an event and reports how many cases exist and how that compares with other drugs.",
            "Checks whether the drug's label already mentions the event.",
            "Flags likely duplicate reports and obvious reporting artefacts.",
            "Drafts a signal assessment with the evidence and the uncertainty stated.",
            "Waits for a safety scientist to approve, edit or reject the assessment.",
            "Scores itself on drugs with known label changes and on control drugs.",
        ],
        "nonfunctional": [
            "The model calls named tools only; it never writes SQL.",
            "Statistics are deterministic and unit tested.",
            "Every run is traced and replayable.",
            "Cost per assessment is measured from system tables.",
            "Only public data is used; no employer data and no personal data.",
            "Anything a free workspace cannot do is recorded as a limit, not hidden.",
        ],
        "components": [
            ("Public safety data", "FDA adverse-event reports and drug labels."),
            ("Governed tables", "Cleaned reports, counts and label text, with permissions."),
            ("Statistics tools", "Counts, disproportionality and duplicate checks."),
            ("Label finder", "Finds the label passage about a given event."),
            ("Agent", "Plans the investigation and drafts the assessment."),
            ("Model service", "The reasoning and embedding models."),
            ("Tracing and evaluation", "Records each step and scores results against known signals."),
            ("Reviewer desk", "Where a safety scientist approves or rejects."),
        ],
        "flows": [
            ("Public safety data", "Governed tables", "ingest"),
            ("Governed tables", "Statistics tools", "tables"),
            ("Governed tables", "Label finder", "label text"),
            ("Agent", "Statistics tools", "tool call"),
            ("Agent", "Label finder", "tool call"),
            ("Agent", "Model service", "model call"),
            ("Agent", "Reviewer desk", "draft assessment"),
            ("Agent", "Tracing and evaluation", "trace"),
        ],
        "bindings": {
            "Databricks": {
                "Public safety data": "openFDA API, reachable ✓",
                "Governed tables": "Delta tables in Unity Catalog",
                "Statistics tools": "Unity Catalog functions",
                "Label finder": "embeddings in Delta plus a function (Vector Search is not available on the free workspace)",
                "Agent": "Mosaic AI Agent Framework",
                "Model service": "Foundation Model APIs, gpt-oss-120b and bge-large available ✓",
                "Tracing and evaluation": "MLflow tracing and evaluation",
                "Reviewer desk": "Databricks Apps, or a job that writes a review file",
            },
            "Open stack": {
                "Agent": "not built",
            },
        },
        "work": [
            ("Phase 0: check", [
                ("Check what Databricks AI services the free workspace allows (models, tables and Genie work; Vector Search, serving, warehouse start and model queries were refused on the day, cause unconfirmed)", "doing", "S", "Databricks"),
                ("Plan, mapping each need to a Databricks service", "done", "S", "Architecture"),
                ("Design against the agent harness, assurance and evaluation standards (Databricks stack file added; profile written)", "doing", "M", "Architecture"),
            ]),
            ("Phase 1: data", [
                ("Ingest 10 drugs and 8 events: 21 million reports and labels, as local files", "done", "M", "Data engineering"),
                ("Load into Delta tables in Unity Catalog with data-quality checks", "todo", "M", "Databricks"),
            ]),
            ("Phase 2: tools and agent", [
                ("Tools as plain Python with tests: counts, PRR and ROR, label check", "done", "M", "SQL, Python"),
                ("Register the tools as Unity Catalog functions", "todo", "M", "SQL, Python"),
                ("Agent loop with output contract, grounding check and 48 tests; run on a stand-in model", "done", "L", "Agents"),
                ("Package with Agent Framework and trace in MLflow", "todo", "L", "Agents"),
            ]),
            ("Phase 3: evaluation and guide", [
                ("Score on 10 known signals and 10 controls", "doing", "M", "AI testing"),
                ("Write the guide, with the free-workspace limits stated", "todo", "M", "Technical writing"),
            ]),
        ],
        "roles": [
            ("Databricks engineer", 1, "3-5 hours/week", "Owns the tables, functions and MLflow set-up."),
            ("Agent engineer", 1, "3-5 hours/week", "Builds the agent and its evaluation."),
            ("Drug-safety reviewer", 1, "1-2 hours/week", "Checks the signal logic and the assessment wording."),
        ],
        "learn": [
            "What each Databricks AI service does and when to use which.",
            "How to expose governed tools to an agent with Unity Catalog functions.",
            "How to trace and evaluate an agent with MLflow.",
            "How signal detection works: counts, comparisons and their limits.",
        ],
        "questions": [
            "Which steps of a signal assessment should never be left to the model?",
            "What changes when Vector Search and model serving are available?",
            "How would you cap the cost of one assessment?",
        ],
        "repo": "",
        "repo_public": False,
        "links": [
            ("Databricks on the platform page", "/platforms/databricks/"),
            ("Companion project: clinical-trial data review agent", "/projects/clinical-data-review-agent/"),
        ],
        "good_first": [
            "Pick five drugs with a known label change for the test set",
            "Review the signal logic in the plan",
        ],
    },
]
