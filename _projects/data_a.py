"""Project detail data, group "standards" (file A).

Read by the projects page builder. Sources: each repo's README, plan pages,
git log (to 18 Oct 2026) and the owner's notes. Public page: no client names,
no cloud account ids or hostnames, no credentials, no funding details.

A trailing " ✓" on a binding's tech means that binding is actually built.
"""

LEAD = "Basant Choudhary"
GH = "https://github.com/dataagentsai/"

PROJECTS = [
    # ------------------------------------------------------------------ 1
    {
        "id": "aac",
        "title": "AI Assurance Catalog",
        "subject": "ai",
        "group": "standards",
        "status": "active",
        "started": "2026-08",
        "lead": LEAD,
        "one_liner": "An open list of what must be true of an AI application before it is trusted in production.",
        "purpose": (
            "The AI Assurance Catalog (AAC) is an open, machine-readable list of test obligations for AI "
            "applications, sorted by the kind of application: chatbot, document extractor, tool-using agent "
            "and so on. It is for architects, test leads and auditors who must say which tests an AI system "
            "owes before it goes live. Standards such as ISO/IEC 42001 and the EU AI Act say a system must be "
            "validated, and threat lists say what can go wrong, but nobody publishes which tests a given kind "
            "of application owes. This catalog is that missing link, and it turns a team's existing test "
            "results into one coverage report, gaps included."
        ),
        "audience": "AI architects, QA and test leads, risk and compliance teams, auditors preparing ISO/IEC 42001 or EU AI Act evidence.",
        "benefits": [
            ("Audit evidence without a Word document", "Test results become a coverage report that maps to ISO/IEC 42001, NIST AI RMF, OWASP and the EU AI Act."),
            ("Fewer surprises in production", "The obligations come from real agent failures, so known risks are tested before launch, not found by customers."),
            ("Faster design reviews", "An architect picks the application type and gets the list of tests it owes in minutes."),
            ("Honest gaps are a strength", "A named, owned, dated gap is acceptable to an auditor; a gap nobody noticed is a finding."),
            ("Reuse the tools you already pay for", "Results from promptfoo, DeepEval, Langfuse, LangSmith or JUnit feed the report as they are."),
        ],
        "functional": [
            "Lists 118 obligations, each with a permanent identifier (AAC-0001 and so on) that never changes.",
            "Marks 36 obligations as owed by every AI application and tags the rest by the kind of application that owes them.",
            "States for each obligation which kind of check can produce a verdict and at which stage of the life cycle.",
            "Maps obligations to OWASP, NIST AI RMF, ISO/IEC 42001 and the EU AI Act by identifier, and lists what does not map.",
            "Turns results from JUnit, promptfoo, DeepEval, Langfuse and LangSmith into one coverage report.",
            "Offers concrete build options for 60 of the obligations and plain-language guidance for 9.",
            "Renders the whole catalog as a filterable web page.",
        ],
        "nonfunctional": [
            "It is a join table, not a framework: it cites controls, threats and metrics and never restates them.",
            "A linter fails the build if a product name appears in an obligation's normative text.",
            "Specification text is CC BY 4.0 and tooling is Apache 2.0, so companies can adopt both.",
            "The repository never ships scorers, runners or dashboards; if its code ever judges a system, the boundary is crossed.",
            "Every release is archived on Zenodo with a DOI, so a specific version can be cited.",
            "The obligations, the mappings and the build options are versioned separately.",
        ],
        "components": [
            ("Obligation files", "One YAML file per obligation: statement, level, tags, mechanisms, stages."),
            ("Schema and linter", "Checks every file against the schema and the boundary rules."),
            ("Crosswalks", "Map obligation ids to outside standards, with an explicit unmapped list."),
            ("Evidence adapters", "Translate a test tool's results into evidence for named obligations."),
            ("Report builder", "Joins evidence with the obligations an application owes into one coverage report."),
            ("Renderer", "Builds the browsable catalog page from the YAML."),
        ],
        "flows": [
            ("Obligation files", "Schema and linter", "validated on every change"),
            ("Obligation files", "Crosswalks", "ids referenced"),
            ("Evidence adapters", "Report builder", "test results as evidence"),
            ("Obligation files", "Report builder", "what is owed"),
            ("Obligation files", "Renderer", "published page"),
        ],
        "bindings": {
            "Open stack": {
                "Obligation files": "YAML in Git ✓",
                "Schema and linter": "JSON Schema, Node.js linter ✓",
                "Evidence adapters": "JUnit, promptfoo, DeepEval, Langfuse, LangSmith ✓",
                "Report builder": "Node.js report tool and GitHub Action ✓",
                "Renderer": "static HTML on GitHub Pages ✓",
            },
            "Azure": {
                "Evidence adapters": "Azure AI evaluation results as evidence (not built)",
            },
            "AWS": {
                "Evidence adapters": "Bedrock evaluation results as evidence (not built)",
            },
        },
        "work": [
            ("Phases 0 to 5: the catalog itself", [
                ("Taxonomy, schema and linter", "done", "M", "Specification design"),
                ("118 obligations with permanent ids", "done", "L", "AI testing"),
                ("Crosswalks to OWASP, NIST AI RMF, ISO/IEC 42001 and the EU AI Act", "done", "L", "Standards and compliance"),
                ("Adapters for JUnit, promptfoo, DeepEval, Langfuse and LangSmith", "done", "M", "JavaScript"),
                ("Release 0.17.1 archived on Zenodo with a DOI", "done", "S", "Release management"),
            ]),
            ("Build options and guidance", [
                ("Build options for 60 of 118 obligations", "done", "L", "AI engineering"),
                ("Write build options for the 58 obligations that have none", "todo", "L", "AI engineering"),
                ("Write plain-language guidance for more obligations (9 written so far)", "todo", "M", "Technical writing"),
            ]),
            ("Patterns as portable detection rules", [
                ("Define a rule format over OpenTelemetry GenAI traces", "todo", "M", "Observability"),
                ("Rewrite the support agent's online rules in that format", "todo", "M", "Python"),
                ("Run the same rules on a second backend and compare verdicts", "todo", "L", "Observability"),
                ("Collect a trace for every rule that must fire it and one that must not", "todo", "M", "AI testing"),
            ]),
            ("Adoption", [
                ("Find three teams that publish a coverage report with their gaps", "todo", "L", "Community"),
                ("Add an adapter for one more test tool, such as Ragas or Inspect", "todo", "S", "JavaScript"),
            ]),
        ],
        "roles": [
            ("Obligation author", 2, "3-5 hours/week", "Writes and reviews obligations and build options from real failures."),
            ("Standards mapper", 1, "2-4 hours/week", "Keeps the crosswalks to ISO, NIST, OWASP and the EU AI Act accurate."),
            ("Adapter developer", 1, "2-4 hours/week", "Writes adapters that turn another tool's results into evidence."),
        ],
        "learn": [
            "How AI risk frameworks, threat lists and test tools fit together, and where they leave a gap.",
            "How to write a requirement that can be tested, without naming a product.",
            "How to map one standard to another honestly, including what does not map.",
            "How an audit treats a known gap differently from an unknown one.",
            "How to keep a public specification machine-readable and linted.",
        ],
        "questions": [
            "Which obligations does a retrieval chatbot owe that a document extractor does not, and why?",
            "Why does the catalog use flat ids instead of ids grouped by application type?",
            "What makes a coverage report acceptable to an ISO/IEC 42001 auditor?",
            "Where does an obligation end and a metric implementation begin?",
        ],
        "repo": GH + "ai-assurance-catalog",
        "repo_public": True,
        "links": [
            ("Browse the catalog", "https://dataagentsai.github.io/ai-assurance-catalog/"),
            ("DOI (all versions)", "https://doi.org/10.5281/zenodo.23366151"),
            ("Research: AgentTwin and the lab", "/lab/"),
        ],
        "good_first": [
            "Write a build option for one obligation that has none",
            "Check one crosswalk row against the standard's text",
            "Add a test case to the promptfoo adapter",
        ],
    },

    # ------------------------------------------------------------------ 2
    {
        "id": "ahc",
        "title": "AI Harness Catalog",
        "subject": "ai",
        "group": "standards",
        "status": "active",
        "started": "2026-08",
        "lead": LEAD,
        "one_liner": "An open list of the parts that must exist around a model call for production-grade AI.",
        "purpose": (
            "The AI Harness Catalog (AHC) lists the components that must exist around a model call: context "
            "assembly, tool calls, retries, cost limits, human approval, logging and more, across sixteen layers. "
            "It is for architects and engineers building AI applications, and for teams choosing an agent framework. "
            "Teams often build logging and evaluation and call the job done, then meet outages in the layers they "
            "skipped. The catalog names every layer, says what breaks without each part, and shows what a chosen "
            "framework leaves for you to build."
        ),
        "audience": "AI architects, platform engineers, teams choosing or reviewing an agent framework.",
        "benefits": [
            ("Fewer outages from missing parts", "Every capability states the failure that follows when it is absent, so gaps are found at design time."),
            ("Know what a framework leaves out", "Comparing a framework to the catalog shows what you still have to build before you commit."),
            ("Cheaper vendor changes", "Ports name the seams where the system meets outside services, so a provider can be swapped without a rewrite."),
            ("Linked to testing", "Each capability names the assurance obligations it helps meet, so build and test plans line up."),
        ],
        "functional": [
            "Lists 118 capabilities with permanent ids across 16 harness layers and 10 kinds of application.",
            "States for each capability what it must do, what breaks without it, and the design decisions it forces.",
            "Defines 18 ports, the seams where a harness meets a service it does not own.",
            "Provides a profile format in which a team declares what it built, what it accepts as a gap and what does not apply.",
            "Links each capability to the AI Assurance Catalog obligations it helps meet.",
            "Ships blueprints for two kinds of application: document extraction pipelines and tool-using agents.",
        ],
        "nonfunctional": [
            "It describes components and never ships them as a library.",
            "A linter rejects verification words in a requirement, so build and test statements stay in separate catalogs.",
            "It depends on the assurance catalog in one direction only.",
            "Named products come last, because they change faster than the requirements.",
            "Specification text is CC BY 4.0 and tooling is Apache 2.0; releases carry a DOI.",
        ],
        "components": [
            ("Capability files", "One YAML file per capability: requirement, failure mode, layers, decisions."),
            ("Ports", "The named seams to outside services, with the standards they cite."),
            ("Schema and linter", "Checks capabilities and the boundary with the assurance catalog."),
            ("Profile format", "Where an adopter records what is met, accepted as a gap, or not applicable."),
            ("Blueprints", "Per application type, the capabilities it owes and how they fit together."),
            ("Renderer", "Builds the filterable catalog page."),
        ],
        "flows": [
            ("Capability files", "Schema and linter", "validated"),
            ("Ports", "Capability files", "seams referenced"),
            ("Capability files", "Blueprints", "collated per application type"),
            ("Profile format", "Schema and linter", "adopter's claims checked"),
            ("Capability files", "Renderer", "published page"),
        ],
        "bindings": {
            "Open stack": {
                "Capability files": "YAML in Git ✓",
                "Schema and linter": "JSON Schema, Node.js linter ✓",
                "Profile format": "harness-profile.yaml, used by the support agent ✓",
                "Renderer": "static HTML on GitHub Pages ✓",
            },
            "Azure": {
                "Profile format": "the claims agent's profile on the Azure stack ✓",
            },
            "AWS": {
                "Profile format": "not built",
            },
        },
        "work": [
            ("Core catalog", [
                ("Taxonomy of 16 layers and 8 positions, schema and linter", "done", "M", "Specification design"),
                ("118 capabilities across all layers and application types", "done", "L", "AI architecture"),
                ("Settle all 118 open design decisions", "done", "M", "AI architecture"),
                ("Release 0.3.1 archived on Zenodo with a DOI", "done", "S", "Release management"),
            ]),
            ("Close the link to the assurance catalog", [
                ("Write a capability for repetition detection (AAC-0109)", "todo", "S", "AI architecture"),
                ("Write a capability for autonomy that widens only on measured agreement (AAC-0118)", "todo", "S", "AI architecture"),
            ]),
            ("Blueprints", [
                ("Blueprints for document extraction and tool-using agents", "done", "M", "AI architecture"),
                ("Write a blueprint for a retrieval chatbot", "todo", "M", "AI architecture"),
                ("Generate blueprints for the remaining application types", "todo", "L", "Technical writing"),
            ]),
            ("Realizations and coverage deltas", [
                ("List, per agent framework, which capabilities it does not provide", "todo", "L", "Agent frameworks"),
                ("Name product options per capability in one dated pass", "todo", "L", "Cloud and open source"),
                ("Decide whether the ports become a standard of their own", "todo", "M", "Architecture"),
            ]),
        ],
        "roles": [
            ("Capability author", 2, "3-5 hours/week", "Writes capabilities and design decisions from systems they have built."),
            ("Framework assessor", 2, "2-4 hours/week", "Compares one agent framework with the catalog and writes up what it leaves out."),
            ("Reviewer", 1, "1-2 hours/week", "Reviews pull requests for the boundary rules and plain wording."),
        ],
        "learn": [
            "What an agent harness is, layer by layer, beyond the model call.",
            "Why ports and adapters make AI systems cheaper to change.",
            "How to tell a build requirement from a test obligation.",
            "How to assess an agent framework by what it does not give you.",
            "How a profile declares accepted gaps honestly.",
        ],
        "questions": [
            "Which of the 16 layers does your current agent framework hide from you?",
            "When should a model choke point be in-process, at a gateway, or both?",
            "Why are named products the last thing added to the catalog?",
            "What is the difference between a gap you accept and a capability that does not apply?",
        ],
        "repo": GH + "ai-harness-catalog",
        "repo_public": True,
        "links": [
            ("Browse the catalog", "https://dataagentsai.github.io/ai-harness-catalog/"),
            ("DOI (all versions)", "https://doi.org/10.5281/zenodo.23366156"),
            ("Course: the agent harness, end to end", "/learn/agent-harness/"),
        ],
        "good_first": [
            "Draft the capability for AAC-0109 (repetition detected and broken)",
            "Assess one agent framework against three layers",
            "Fix unclear wording in one layer's capabilities",
        ],
    },

    # ------------------------------------------------------------------ 3
    {
        "id": "agenttwin",
        "title": "AgentTwin",
        "subject": "ai",
        "group": "standards",
        "status": "active",
        "started": "2026-09",
        "lead": LEAD,
        "one_liner": "Test an AI agent in a simulated world and judge what changed, not only what it said.",
        "purpose": (
            "AgentTwin places a real AI agent in a simulated world: its customers, the systems it calls, their data "
            "and their faults. It then checks what actually changed in that world, such as a refund issued without "
            "authority or one owed and never issued. It is for teams that build or buy agents that take actions, "
            "and for anyone who must judge an agent they did not build. Agents now move money and change records, "
            "and reading their replies is not enough to know whether they kept the rules."
        ),
        "audience": "Agent developers, QA teams, independent assessors, buyers checking a vendor's agent.",
        "benefits": [
            ("Catch costly actions before launch", "Rule-breaking writes, such as a refund over a limit, are found in simulation, not in the ledger."),
            ("Find what was never done", "It flags actions that were owed to a customer and never taken, which a reply check cannot see."),
            ("Privacy checks that leave a trace", "It notices when an agent reads another customer's record, even when nothing changed."),
            ("Judge an agent you did not build", "An assessor needs only the agent's policy and tool definitions, not its code."),
            ("No paid test infrastructure", "Runs on a laptop in seconds with scripted customers and no model calls."),
        ],
        "functional": [
            "Reads a world description (AWD) that names the agent's systems, records, rules and faults.",
            "Serves that world to the agent as the tools it calls, including as an MCP (Model Context Protocol) server.",
            "Plays customers and approvers from scripts, or hands the customer to a model for open-ended conversations.",
            "Injects faults such as slowness, lost replies and stale reads.",
            "Judges each run with four state checks: rule-breaking writes, owed actions, false statements and other customers' data.",
            "Plants injection attacks drawn from PyRIT, AgentDojo or built-in templates, and judges them by what changed.",
            "Reports which scenarios a suite is missing, using pairwise coverage.",
        ],
        "nonfunctional": [
            "It is a description format first; the simulator shows the format can be run.",
            "Outside tools are adopted behind seams; only the format, the stand-in, the judges and the mode switch are its own.",
            "Same world and seed give the same result, so failures can be reproduced.",
            "Its own tests use a lending library, so the format is checked on a domain it was not written for.",
            "Every adoption is labelled as adopted or still planned.",
        ],
        "components": [
            ("World loader", "Reads the world description and refuses one that breaks the format's rules."),
            ("Stand-in systems", "Present the world as the tools the agent calls, enforcing each tool's preconditions."),
            ("Actors", "Scripted or model-played customers and approvers."),
            ("Fault injector", "Adds slowness, lost replies and stale reads."),
            ("Agent under test", "The real agent, connected through a binding."),
            ("Judges", "Read the world's state and flag rule breaks, owed actions, false claims and privacy reads."),
            ("Run record", "One file per run with every call, effect and verdict."),
        ],
        "flows": [
            ("World loader", "Stand-in systems", "world projected as tools"),
            ("Actors", "Agent under test", "customer messages"),
            ("Agent under test", "Stand-in systems", "tool calls"),
            ("Fault injector", "Stand-in systems", "faults"),
            ("Stand-in systems", "Judges", "state before and after"),
            ("Judges", "Run record", "verdicts"),
        ],
        "bindings": {
            "Open stack": {
                "World loader": "Python, JSON Schema ✓",
                "Stand-in systems": "Python, official MCP SDK ✓",
                "Actors": "scripts; LangWatch Scenario for model-played customers ✓",
                "Fault injector": "built-in perturbations ✓; Toxiproxy (planned)",
                "Judges": "Python state checks; pass^k from τ²-bench ✓",
                "Run record": "pytest and JSON ✓",
            },
            "Azure": {
                "Agent under test": "the motor-claims agent built for Azure, run in-process ✓",
            },
            "AWS": {
                "Agent under test": "not built",
            },
        },
        "work": [
            ("Format and simulator", [
                ("World format, schema and loader", "done", "M", "Specification design"),
                ("Stand-in systems served over MCP", "done", "M", "Python"),
                ("Four state judges and the run command", "done", "M", "Python"),
                ("Release 0.13.0 with 397 passing tests", "done", "S", "Testing"),
            ]),
            ("Agents we did not build", [
                ("Judge τ²-bench's airline, retail and telecom agents from their policies alone", "done", "L", "AI testing"),
                ("Explain every disagreement with τ²-bench's own verdicts", "done", "M", "Analysis"),
                ("Run one more public benchmark agent through AgentTwin", "todo", "L", "AI testing"),
            ]),
            ("Adopt, don't build", [
                ("Adopt PyRIT, AgentDojo, Hypothesis, allpairspy and LangWatch Scenario", "done", "M", "Python"),
                ("Adopt an LLM grader such as DeepEval or Inspect behind a seam", "todo", "M", "AI evaluation"),
                ("Adopt Toxiproxy for network faults", "todo", "S", "Testing"),
                ("Adopt VCR.py for record and replay", "todo", "S", "Python"),
                ("Adopt SDV for realistic data volume", "todo", "M", "Data engineering"),
            ]),
            ("Format gaps", [
                ("Answer an injected read error as an error, not a refusal", "todo", "S", "Python"),
                ("Let the format express rules about a change (new versus old values)", "todo", "M", "Specification design"),
                ("Describe a customer who acts with their own tools", "todo", "L", "Specification design"),
            ]),
        ],
        "roles": [
            ("Simulator developer", 2, "3-5 hours/week", "Builds stand-ins, judges and adapters to adopted tools."),
            ("World author", 2, "2-4 hours/week", "Writes worlds and scenarios for a new domain."),
            ("Benchmark analyst", 1, "2-4 hours/week", "Runs public agents through AgentTwin and explains each disagreement."),
        ],
        "learn": [
            "Why judging an agent by the state it leaves beats judging its words.",
            "How to turn an agent's policy into a testable world.",
            "How to plant injection attacks and judge them fairly.",
            "How pairwise coverage shows which scenarios a suite is missing.",
            "How to adopt open-source tools behind seams instead of rebuilding them.",
        ],
        "questions": [
            "What can a final-state judge never see, and how does the ownership judge see it?",
            "Why does a mock that drifts from the real system make a test suite a toy?",
            "When should a customer be scripted, and when played by a model?",
            "How would you write a world for a domain you know, such as hotel bookings?",
        ],
        "repo": GH + "agenttwin",
        "repo_public": True,
        "links": [
            ("Research: AgentTwin and the lab", "/lab/"),
            ("The world format (SPEC.md)", GH + "agenttwin/blob/main/SPEC.md"),
            ("DOI (all versions)", "https://doi.org/10.5281/zenodo.23366041"),
        ],
        "good_first": [
            "Make an injected read error come back as an error",
            "Add a scenario to the lending-library test world",
            "Write a short how-to for running one τ² example",
        ],
    },

    # ------------------------------------------------------------------ 4
    {
        "id": "reference-agent",
        "title": "Reference Agent",
        "subject": "ai",
        "group": "standards",
        "status": "active",
        "started": "2026-08",
        "lead": LEAD,
        "one_liner": "An open customer-support agent built and tested to the catalogs, layer by visible layer.",
        "purpose": (
            "The Reference Agent is a working customer-support agent for a clothing web shop: order questions, "
            "cancellations, returns and refunds. It is built in the open, with no agent framework, so every layer "
            "of the harness is visible as its own module. It shows that the two catalogs and AgentTwin are enough "
            "to specify, build and test a production-grade agent. Teams can copy its structure, its tests and its "
            "four release gates instead of starting from a blank page."
        ),
        "audience": "Engineers building their first production agent, architects who want a worked example, course participants.",
        "benefits": [
            ("A proven starting point", "Teams start from a support agent that already passes behaviour, feature, structure and harness gates."),
            ("Money moves only with authority", "Refunds above a limit wait for a person, and the agent cannot be talked past that rule."),
            ("Answers without paying for a model", "Common questions such as order status are answered by code, which cuts model cost and latency."),
            ("Safe to change", "About 2,100 tests run in four minutes without network or keys, so a change is checked before release."),
        ],
        "functional": [
            "Answers order status, cancellation, return and refund questions for a clothing shop.",
            "Answers questions the specification can settle with code alone, without calling the model.",
            "Holds refunds above a limit for a person to approve, and resumes when they decide.",
            "Hands the conversation to a person when a rule says so, or when the model is unavailable.",
            "Refuses instructions planted in order notes and other untrusted text.",
            "Shows each customer only their own orders and conversations.",
        ],
        "nonfunctional": [
            "No agent framework: one module per harness layer, with an import contract that enforces the architecture.",
            "Strict typing, import rules and size limits run inside the test suite, so they cannot be skipped.",
            "Every test names the specification statement it checks, and a coverage map is generated from those tags.",
            "Model calls can be recorded and replayed, so the suite runs offline at zero cost.",
            "Every dependency it does not own sits behind an interface, built only in the composition root.",
        ],
        "components": [
            ("Channel", "Receives customer messages and sends replies."),
            ("Identity", "Proves who is asking from a credential the caller cannot forge."),
            ("Router", "Answers with code when it can; sends the rest to the agent loop."),
            ("Context assembly", "Builds what the model sees from the conversation and facts."),
            ("Control loop", "Runs model and tool steps within budgets for steps, time and tokens."),
            ("Tool layer", "Calls the shop's systems over MCP, with idempotency keys."),
            ("Approvals and escalation", "Durable waits for a person's decision or a handoff."),
            ("Telemetry and checks", "Traces every turn and runs reply checks inline and online."),
        ],
        "flows": [
            ("Channel", "Identity", "message with credential"),
            ("Identity", "Router", "verified customer"),
            ("Router", "Control loop", "needs the model"),
            ("Context assembly", "Control loop", "prompt"),
            ("Control loop", "Tool layer", "tool calls"),
            ("Tool layer", "Approvals and escalation", "refund over limit"),
            ("Control loop", "Telemetry and checks", "trace and reply"),
            ("Telemetry and checks", "Channel", "checked reply"),
        ],
        "bindings": {
            "Open stack": {
                "Channel": "Chatwoot ✓",
                "Identity": "Keycloak, PyJWT ✓",
                "Control loop": "hand-rolled Python loop; Groq through a LiteLLM gateway ✓",
                "Tool layer": "official MCP SDK; Saleor as the shop ✓",
                "Approvals and escalation": "Temporal ✓",
                "Telemetry and checks": "OpenTelemetry, Langfuse, Prometheus, Grafana ✓",
            },
            "Azure": {
                "Control loop": "the shared harness library carried to the Azure claims agent ✓ (the clothing agent itself is not deployed to Azure)",
            },
            "AWS": {
                "Control loop": "not built",
            },
        },
        "work": [
            ("Phase A: every layer built", [
                ("All eighteen modules, all sixteen harness layers covered", "done", "L", "Python"),
                ("Strict types, import contract and complexity limits in the suite", "done", "M", "Software design"),
                ("Every test tagged with the statement it checks", "done", "M", "Testing"),
            ]),
            ("Four gates pass", [
                ("Behaviour: 46 scenarios pass in AgentTwin", "done", "M", "AI testing"),
                ("Features: 171 of 171 owed statements exercised", "done", "M", "Testing"),
                ("Harness: 81 owed capabilities met, accepted or not applicable", "done", "M", "AI architecture"),
                ("Lost parcel in the customer's own words now reaches a person", "done", "S", "Python"),
                ("Exercise the 6 tool-using-agent obligations not yet tested", "todo", "M", "AI testing"),
            ]),
            ("Same agent, different stack", [
                ("Rebuild the support agent on LangGraph and run the same gates", "todo", "L", "LangGraph"),
                ("Rebuild it on the Claude Agent SDK and run the same gates", "todo", "L", "Agent SDKs"),
            ]),
            ("Same specs, different domain", [
                ("Write the hotel support agent's specification", "todo", "M", "Specification design"),
                ("Generate the hotel agent from the specs and measure reuse", "todo", "L", "AI engineering"),
            ]),
        ],
        "roles": [
            ("Agent engineer", 2, "4-6 hours/week", "Builds features and fixes findings, spec first."),
            ("Test engineer", 1, "3-5 hours/week", "Writes scenarios and keeps the gates honest."),
            ("Platform engineer", 1, "2-4 hours/week", "Keeps the open-stack services running in containers."),
        ],
        "learn": [
            "How a production agent is put together, one harness layer at a time.",
            "Why answering with code first saves money and errors.",
            "How durable waits let a person approve a refund hours later.",
            "How to enforce an architecture with tests rather than diagrams.",
            "How to route a failure to the specification instead of patching the agent.",
        ],
        "questions": [
            "Which questions can your agent answer without calling the model at all?",
            "What would break if a refund tool were called twice for one request?",
            "Why must the identity come from a credential and not from the conversation?",
            "What does an agent framework take over that this agent writes out by hand?",
        ],
        "repo": GH + "reference-agent",
        "repo_public": True,
        "links": [
            ("DOI (all versions)", "https://doi.org/10.5281/zenodo.23366149"),
            ("Clean AI Engineering: specs and gates", GH + "clean-ai-engineering"),
            ("Course: the agent harness, end to end", "/learn/agent-harness/"),
        ],
        "good_first": [
            "Write a scenario for one obligation in NOT_EXERCISED.md",
            "Add a paraphrase test case to the router",
            "Improve the run-it-yourself steps in the README",
        ],
    },

    # ------------------------------------------------------------------ 5
    {
        "id": "claims-fnol-azure",
        "title": "Claims FNOL assistant on Azure",
        "subject": "ai",
        "group": "standards",
        "status": "active",
        "started": "2026-10",
        "lead": LEAD,
        "one_liner": "A motor-insurance claims agent on Azure, built on the same harness as the support agent.",
        "purpose": (
            "This is a motor insurer's first-notice-of-loss (FNOL) assistant: the moment a policyholder first says "
            "\"a bus hit my car\". It registers the claim, gives a reference, answers status questions and pays small "
            "payouts; anything larger, or anyone hurt, goes to a person. It runs on Azure and reuses the support "
            "agent's harness library, which supplies about 84% of the code it runs. It proves the harness carries to "
            "a second domain and a second cloud, and it is the running example in the agent harness course."
        ),
        "audience": "Insurance and financial-services technology teams, Azure architects, course participants.",
        "benefits": [
            ("Small claims settled faster", "Claims are registered at once and payouts up to the limit are paid without waiting for a handler."),
            ("Payouts stay within authority", "Any payout above the limit waits for a handler's approval, enforced where the payment executes."),
            ("Injuries always reach a person", "A claim with someone hurt is handed to a handler, never decided by the agent."),
            ("Lower build cost", "About 84% of the code is reused from the support agent's library, unchanged."),
            ("Runs on free tiers", "The whole Azure deployment fits a free trial with a budget alert set first."),
        ],
        "functional": [
            "Registers a motor claim from a conversation and returns a claim reference.",
            "Answers claim status from the claims system without calling the model.",
            "Pays payouts up to the limit at once and holds larger ones for a handler on the desk.",
            "Hands any injury, or a request for a person, to a claims handler.",
            "Lets policyholders sign in and see only their own claims.",
            "Politely refuses questions about cover, which are left to an assessor.",
        ],
        "nonfunctional": [
            "The claims system verifies a short-lived token on every call and trusts nothing the agent asserts.",
            "Each app uses its own database role; no app runs as the admin.",
            "A tool's idempotency key comes from the message, so a crash cannot register a claim twice.",
            "The payout limit is read from configuration, so it changes without a redeploy.",
            "Infrastructure is code, with each service's free allowance checked before it is added.",
            "The same scenarios and four gates run on a laptop before anything reaches Azure.",
        ],
        "components": [
            ("Chat page and handler desk", "Where policyholders chat and handlers approve or take over."),
            ("Sign-in", "Proves who the policyholder or handler is."),
            ("Agent", "The harness, the claims rules and the model client."),
            ("Model gateway", "One door to the model, with an allow-list, token limits and content screening."),
            ("Claims system", "Registers claims and payouts over MCP, checking the caller's token."),
            ("Durable waits", "Hold a payout or handoff until a person decides."),
            ("State store", "The agent's conversations, approvals and the claims data."),
            ("Telemetry and alerts", "Traces every turn and raises alerts on the agent's signals."),
        ],
        "flows": [
            ("Chat page and handler desk", "Sign-in", "sign in"),
            ("Chat page and handler desk", "Agent", "message"),
            ("Agent", "Model gateway", "model call"),
            ("Agent", "Claims system", "tool call with token"),
            ("Agent", "Durable waits", "payout over limit"),
            ("Durable waits", "Chat page and handler desk", "approval request"),
            ("Agent", "State store", "turn saved"),
            ("Agent", "Telemetry and alerts", "trace"),
        ],
        "bindings": {
            "Open stack": {
                "Chat page and handler desk": "own web pages ✓",
                "Sign-in": "local test sign-in ✓",
                "Agent": "Python harness library, Pydantic AI ✓",
                "Model gateway": "Groq called directly ✓",
                "Claims system": "own MCP server ✓",
                "Durable waits": "DBOS ✓",
                "State store": "PostgreSQL ✓",
                "Telemetry and alerts": "local trace log ✓",
            },
            "Azure": {
                "Chat page and handler desk": "Azure Container Apps ✓",
                "Sign-in": "Microsoft Entra ID ✓",
                "Agent": "Azure Container Apps, App Configuration, Key Vault ✓",
                "Model gateway": "API Management in front of Groq, Content Safety ✓",
                "Claims system": "Azure Container Apps, on-behalf-of tokens ✓",
                "Durable waits": "DBOS on Azure Database for PostgreSQL ✓",
                "State store": "Azure Database for PostgreSQL with pgvector ✓",
                "Telemetry and alerts": "Application Insights, Log Analytics, log alerts ✓",
            },
            "AWS": {
                "Agent": "not built",
            },
        },
        "work": [
            ("Phase 1: on the laptop", [
                ("Specification, simulated world and 29 scenarios", "done", "M", "Specification design"),
                ("All four gates pass with a scripted model", "done", "M", "AI testing"),
                ("Chat with it locally with the real model", "done", "M", "Python"),
                ("Checks placed by YAML as plug-ins", "done", "M", "Python"),
            ]),
            ("Phase 1: in Azure", [
                ("All Azure resources created from Bicep and azd", "done", "L", "Azure infrastructure"),
                ("Security fixes for money and identity paths", "done", "M", "Security"),
                ("Live sign-in, on-behalf-of tokens and email alerts", "done", "M", "Azure"),
                ("Report a claim through the gateway and see it in Application Insights", "doing", "M", "Azure"),
                ("Deploy from GitHub Actions with a federated login", "todo", "S", "CI/CD"),
            ]),
            ("Evaluation loop and guided tour", [
                ("Turn the watch rules into online checks placed by YAML", "todo", "M", "Python"),
                ("A job that reads Application Insights and writes findings", "todo", "M", "Azure, KQL"),
                ("Write the guided tour of every Azure resource, with exercises", "todo", "M", "Technical writing"),
            ]),
            ("Phase 2", [
                ("Label about 500 motor-claims messages for a local router", "todo", "M", "Data labelling"),
                ("Answer policy-wording questions from retrieved clauses, with citations", "todo", "L", "RAG"),
                ("Measure cost per conversation and per outcome from real traces", "todo", "M", "Cost analysis"),
            ]),
        ],
        "roles": [
            ("Azure engineer", 1, "3-5 hours/week", "Owns the Bicep, the deploy pipeline and the Azure checks."),
            ("Agent engineer", 1, "3-5 hours/week", "Builds claims features and fixes findings, spec first."),
            ("Insurance domain reviewer", 1, "1-2 hours/week", "Checks the claims rules and wording against real practice."),
        ],
        "learn": [
            "How one harness library carries to a new domain and a new cloud.",
            "How to deploy an agent to Azure on free tiers, safely.",
            "How on-behalf-of tokens stop an agent acting beyond the user's rights.",
            "How durable waits let a handler approve a payout later.",
            "How to trace one conversation end to end in Application Insights.",
        ],
        "questions": [
            "Why does the claims system check a token instead of trusting the agent?",
            "What would you change to move the payout limit per policy type?",
            "Which checks belong at the gateway and which inside the agent?",
            "What would it take to swap Groq for a model hosted in an India region?",
        ],
        "repo": GH + "claims-fnol-azure",
        "repo_public": True,
        "links": [
            ("The README", GH + "claims-fnol-azure#readme"),
            ("Course: the agent harness, end to end", "/learn/agent-harness/"),
            ("Research: AgentTwin and the lab", "/lab/"),
        ],
        "good_first": [
            "Run the agent on your laptop and report what was unclear",
            "Draft one exercise for the guided Azure tour",
            "Add a scenario for withdrawing a claim",
        ],
    },

    # ------------------------------------------------------------------ 6
    {
        "id": "eval-harness-framework",
        "title": "Eval Harness Framework",
        "subject": "ai",
        "group": "standards",
        "status": "active",
        "started": "2026-10",
        "lead": LEAD,
        "one_liner": "One framework to check AI agents with any provider's evals, guardrails, cost and business rules.",
        "purpose": (
            "The Eval Harness Framework checks AI agents for quality, security, cost and a business's own rules. "
            "It mixes checks from several providers in one run and gives one result format. It is for teams running "
            "agents who already use tools such as LangSmith, Langfuse or Application Insights and are tired of writing "
            "glue between them. It brings no database, UI or dashboards of its own: it reads from and writes back to "
            "the tools a team already has."
        ),
        "audience": "Teams running AI agents in production, AI platform teams, ops and quality leads.",
        "benefits": [
            ("Write the glue once", "One adapter per provider replaces the custom code teams write each time they combine two eval tools."),
            ("Best check for each job", "A team can take three checks from one provider and five from another, with one comparable result."),
            ("No new platform to buy", "Results go back into the team's existing tracing and dashboards, so nothing new to run or pay for."),
            ("Business rules, not just scores", "Ops teams write rules like \"no cancel without an order lookup first\" in YAML."),
            ("Cost and security in the same run", "Cost rules and personal-data checks run alongside quality checks."),
        ],
        "functional": [
            "Runs checks from Azure AI Evaluation, DeepEval, Ragas and Presidio through one request and result shape.",
            "Loads which checks run, and where, from a YAML file a team can read on one screen.",
            "Ships a customer-support preset that a team's file overrides field by field.",
            "Checks whole conversations with five domain patterns, such as an action that needs another action first.",
            "Lets a free hosted model act as judge, so no paid cloud account is needed.",
            "Is already used by the support agent and the claims agent.",
        ],
        "nonfunctional": [
            "No vendor SDK is imported outside its own adapter.",
            "Every adapter must pass the same contract test table for its port.",
            "Deterministic code checks come before judge models.",
            "Version 1 must install with one command and produce a first report within an hour.",
            "A feature is added only when a real team asks for it, or it replaces something.",
        ],
        "components": [
            ("Trace source", "Reads conversations from where traces already land."),
            ("Plan", "The YAML that says which checks run, where, and with what threshold."),
            ("Evaluator adapters", "Translate in, call one provider's check, translate out."),
            ("Judge", "The model used by checks that need one."),
            ("Decide step", "Turns results into one action: allow, redact, block, escalate or alert."),
            ("Result sink", "Writes results back to the team's own tracing tool."),
        ],
        "flows": [
            ("Trace source", "Plan", "conversations"),
            ("Plan", "Evaluator adapters", "checks to run"),
            ("Evaluator adapters", "Judge", "judge calls"),
            ("Evaluator adapters", "Decide step", "results"),
            ("Decide step", "Result sink", "actions and scores"),
        ],
        "bindings": {
            "Open stack": {
                "Trace source": "OpenAI-format messages ✓; Phoenix, Langfuse (planned)",
                "Plan": "YAML ✓",
                "Evaluator adapters": "DeepEval, Ragas, Presidio ✓",
                "Judge": "Groq-hosted open model ✓",
                "Result sink": "OpenTelemetry evaluation events (planned)",
            },
            "Azure": {
                "Trace source": "Application Insights (planned)",
                "Evaluator adapters": "Azure AI Evaluation groundedness ✓; Content Safety (planned)",
                "Result sink": "Application Insights custom events (planned)",
            },
            "AWS": {
                "Evaluator adapters": "Bedrock evaluations and guardrails (planned)",
            },
            "GCP": {
                "Evaluator adapters": "planned, no work started",
            },
        },
        "work": [
            ("Tier 0: spike", [
                ("Run four providers through one request shape", "done", "M", "Python"),
                ("Record every provider's real answer for offline tests", "done", "S", "Testing"),
            ]),
            ("Tier 1: core package", [
                ("Check the competitor landscape with sources", "done", "M", "Research"),
                ("Extract the package and use it from both reference agents", "done", "M", "Python packaging"),
                ("Contract test table per port", "done", "S", "Testing"),
                ("A stability label on every adapter", "todo", "S", "Python"),
            ]),
            ("Tier 2: sessions and domain patterns", [
                ("Session shape and five domain patterns", "done", "M", "Python"),
                ("Worked example for the claims agent", "done", "S", "YAML"),
                ("Run the five patterns on real claims and support conversations", "todo", "M", "AI evaluation"),
            ]),
            ("Tiers 3 to 6: version 1 slice", [
                ("Read traces from Phoenix and Application Insights", "todo", "M", "Observability"),
                ("Write results back as OpenTelemetry evaluation events", "todo", "M", "OpenTelemetry"),
                ("Bring in the six built LLM cost rules", "todo", "M", "Cost engineering"),
                ("Add Indian ID formats (PAN, Aadhaar) to the personal-data check", "todo", "S", "Security"),
            ]),
        ],
        "roles": [
            ("Adapter developer", 2, "3-5 hours/week", "Adds and maintains one provider's adapter and its contract tests."),
            ("Rule author", 1, "2-3 hours/week", "Writes domain patterns and cost rules in YAML."),
            ("Pilot team contact", 1, "1-2 hours/week", "Runs version 1 on a real team's traces and reports what they found."),
        ],
        "learn": [
            "How the main eval and guardrail tools differ in their data shapes.",
            "How ports and adapters keep vendor code in one place.",
            "Why checking and deciding are separate steps.",
            "How to write a business rule that checks a whole conversation.",
            "How OpenTelemetry carries evaluation results.",
        ],
        "questions": [
            "When is a judge model the wrong tool, and a code check the right one?",
            "Why does a check that takes 500 ms belong online and not inline?",
            "How do you compare scores from two providers that use different scales?",
            "What should happen when a check itself fails: block or allow?",
        ],
        "repo": GH + "eval-harness-framework",
        "repo_public": True,
        "links": [
            ("The plan, tier by tier", GH + "eval-harness-framework/blob/main/docs/PLAN.html"),
            ("Spike findings", GH + "eval-harness-framework/blob/main/FINDINGS.md"),
            ("Course: eval in the agent harness", "/learn/agent-harness/"),
        ],
        "good_first": [
            "Add PAN and Aadhaar recognisers to the Presidio adapter",
            "Write contract test rows for one adapter",
            "Review the claims example YAML as a newcomer",
        ],
    },

    # ------------------------------------------------------------------ 7
    {
        "id": "agenttwin-lab",
        "title": "AgentTwin Lab",
        "subject": "ai",
        "group": "standards",
        "status": "active",
        "started": "2026-10",
        "lead": LEAD,
        "one_liner": "Simulated days for AI agents, to see whether automated fixers weaken the checks that caught them.",
        "purpose": (
            "The lab runs an AI agent through simulated days in an AgentTwin world, with customers arriving, "
            "incidents on a calendar and a monitor that raises them with evidence. When an incident is found, a "
            "coding agent tries to fix it, and the lab records whether the fix is honest or quietly weakens a test "
            "or a rule. A person approves every deploy before the next day. It is for researchers and teams who "
            "plan to let coding agents repair live AI systems, and need to know that the alarm was fixed, not silenced."
        ),
        "audience": "AI safety and oversight researchers, platform teams considering automated fixes, assessors.",
        "benefits": [
            ("Trust automated fixes", "Each change a fixer makes or tries is labelled as weakening or not, before it can ship."),
            ("A person stays in charge", "No fix reaches production without a person's approval through the lab's release pointer."),
            ("Find slow-burn faults", "Running whole days surfaces faults that a single test conversation never meets."),
            ("Cheap to repeat", "A simulated day takes about two seconds on a laptop, with no model calls."),
        ],
        "functional": [
            "Runs a simulated day: a generated population, visits on a curve and incidents from the world's calendar.",
            "Monitors every call and reply as it happens and raises incidents with their evidence.",
            "Turns an incident into a brief and runs a headless coding agent on it in a separate git worktree.",
            "Protects test and rule files in six layers, each logging what it stopped.",
            "Classifies every edit as weakening, strengthening, neutral or unclear, without a model.",
            "Records the loop of day, fix, approve, deploy and next day as one run with its report.",
        ],
        "nonfunctional": [
            "The lab builds only the day runner, the ledger and the report; every other job is an adopted tool behind a port.",
            "Same world, plan and seed give the same ledger.",
            "Nothing leaves the machine in a scripted run.",
            "Keys used by a real fixer are kept out of every record, and records are scanned to confirm it.",
            "Results report reliability over several seeded days, not one lucky run.",
        ],
        "components": [
            ("World and calendar", "The AgentTwin world, with incidents planted on a timetable."),
            ("Population and visits", "Generated customers and when they arrive."),
            ("Agent under test", "The reference support agent, through its gate binding."),
            ("Monitor", "Judges each call and reply and raises incidents."),
            ("Fixer harness", "Gives a coding agent the brief and records everything it tried."),
            ("Weakening classifier", "Labels each attempted edit."),
            ("Release pointer", "Deploys a fix only after a person approves."),
            ("Ledger and report", "Every turn, call and incident, and pass rates over seeded days."),
        ],
        "flows": [
            ("World and calendar", "Population and visits", "world state"),
            ("Population and visits", "Agent under test", "customer visits"),
            ("Agent under test", "Monitor", "calls and replies"),
            ("Monitor", "Fixer harness", "incident brief"),
            ("Fixer harness", "Weakening classifier", "attempted edits"),
            ("Weakening classifier", "Release pointer", "allowed fix"),
            ("Monitor", "Ledger and report", "incidents"),
        ],
        "bindings": {
            "Open stack": {
                "World and calendar": "AgentTwin, SimPy ✓",
                "Population and visits": "Faker (en_IN) ✓",
                "Agent under test": "reference agent in process; Temporal test server; time-machine ✓",
                "Monitor": "AgentTwin monitor, OpenTelemetry SDK ✓",
                "Fixer harness": "Claude Code headless in git worktrees; a LiteLLM proxy to a free hosted model ✓",
                "Weakening classifier": "Python ast and YAML diffs ✓",
                "Release pointer": "git, with GitHub as an option ✓",
            },
            "Azure": {
                "Agent under test": "not built",
            },
            "AWS": {
                "Agent under test": "not built",
            },
        },
        "work": [
            ("One simulated day", [
                ("Day runner, population, calendar and monitor", "done", "M", "Python"),
                ("Planted incident: parcels marked delivered that never arrived", "done", "S", "Scenario design"),
                ("Pass rates over several seeded days", "done", "S", "Statistics"),
            ]),
            ("The fixer and its guard rails", [
                ("Fixer harness with honest, gaming and rule-narrowing stubs", "done", "M", "Python"),
                ("Protected paths in six layers", "done", "M", "Security"),
                ("Weakening classifier over every attempted edit", "done", "M", "Static analysis"),
                ("Person-approved deploys and the full loop as one run", "done", "M", "Release engineering"),
            ]),
            ("Real fixers", [
                ("First real fixer runs through a free hosted model", "done", "M", "LLM tooling"),
                ("Run the fixer with a larger-context model and compare", "todo", "M", "LLM tooling"),
                ("Repeat runs on several incidents and publish the results", "todo", "L", "Research"),
            ]),
            ("Richer days", [
                ("Add turns that go through the model loop, with a scripted policy", "todo", "M", "Python"),
                ("Add refund requests and approvals to the day", "todo", "M", "Scenario design"),
                ("Run the claims agent through a simulated day", "todo", "L", "AI testing"),
            ]),
        ],
        "roles": [
            ("Research engineer", 1, "4-6 hours/week", "Runs fixer experiments and writes up what they show."),
            ("Lab developer", 1, "3-5 hours/week", "Extends days, incidents and the classifier."),
            ("Reviewer", 1, "1-2 hours/week", "Labels unclear edits and checks the classifier's verdicts."),
        ],
        "learn": [
            "Why an automated fixer might weaken the test instead of fixing the fault.",
            "How to run a whole simulated day deterministically.",
            "How to guard files from an agent in layers.",
            "How to classify code and spec changes without a model.",
            "Why a free model tier is too small for real repair work, measured.",
        ],
        "questions": [
            "If a fixer wrote nothing, is that evidence it is honest?",
            "What should happen to an edit the classifier marks unclear?",
            "Which protection layer would you trust least, and why?",
            "How many seeded days are enough to claim a fix holds?",
        ],
        "repo": GH + "agenttwin-lab",
        "repo_public": True,
        "links": [
            ("Research: AgentTwin and the lab", "/lab/"),
            ("DOI (all versions)", "https://doi.org/10.5281/zenodo.23366521"),
            ("AgentTwin", GH + "agenttwin"),
        ],
        "good_first": [
            "Plant a second incident on the day's calendar",
            "Add a classifier test for a loosened ceiling",
            "Run three seeded days and check the report reads clearly",
        ],
    },

    # ------------------------------------------------------------------ 8
    {
        "id": "agent-harness-course",
        "title": "The Agent Harness course",
        "subject": "ai",
        "group": "standards",
        "status": "active",
        "started": "2026-10",
        "lead": LEAD,
        "one_liner": "A hand-drawn course following one real agent from a customer's message to the real code.",
        "purpose": (
            "This course follows one real agent, the motor-insurance claims assistant on Azure, from the moment a "
            "customer types to the moment the reply goes back. It comes in two parts: a hand-drawn tutorial where "
            "every box opens the next level down until you reach the code, and a deep-dive Series with each of 22 "
            "concerns on its own page. It is for engineers and architects who can call a model but have not yet built "
            "everything around it. Real numbers, traces and code come from the live agent, and anything not yet built "
            "is labelled so."
        ),
        "audience": "Software engineers moving into AI, architects, technical leads, study groups.",
        "benefits": [
            ("Faster onboarding", "New team members learn a production agent's design in hours instead of reading code for weeks."),
            ("Fewer design mistakes", "Each concern shows what goes wrong without it, with real failures from a live agent."),
            ("Cloud choices made clearly", "Each concern compares the Azure option with open-source options."),
            ("Grounded in real code", "Code on each page is cut from the public repositories at build time, so it stays current."),
        ],
        "functional": [
            "Shows the architecture as drawings, from one block down to each component.",
            "Follows one message end to end, with every box linking to its design page.",
            "Draws 19 real conversation flows as the path each message took.",
            "Compares tech choices for 22 concerns: what we chose, Azure options and open-source options.",
            "Shows real code, call stacks and class diagrams on design pages.",
            "Covers cost, testing, evaluation and observability, each on its own pages.",
        ],
        "nonfunctional": [
            "Plain words and black-and-white drawings, readable without a cloud background.",
            "A build fails if any link points to a page that does not exist.",
            "Code snippets print \"code not found\" when the source moves, rather than going stale silently.",
            "The publish step redacts cloud account ids and resource names on every page.",
            "Each detail is written once, in its own page, and linked from elsewhere.",
        ],
        "components": [
            ("Content sources", "The live agent's repositories, plans and traces."),
            ("Page registry", "Each page's id, title, parent and summary, which drive navigation."),
            ("Drawing kit", "Hand-drawn boxes and arrows, each box clickable."),
            ("Code cutter", "Pulls real code from the repositories by anchor at build time."),
            ("Builder", "Writes every page and checks every link."),
            ("Publisher", "Redacts private details and copies the site to the public pages."),
        ],
        "flows": [
            ("Content sources", "Code cutter", "real code"),
            ("Page registry", "Builder", "page tree"),
            ("Drawing kit", "Builder", "drawings"),
            ("Code cutter", "Builder", "snippets"),
            ("Builder", "Publisher", "site"),
        ],
        "bindings": {
            "Open stack": {
                "Builder": "Python static site generator ✓",
                "Drawing kit": "inline SVG ✓",
                "Publisher": "GitHub Pages ✓",
            },
            "Azure": {
                "Content sources": "the claims agent on Container Apps, API Management, Entra ID and Application Insights ✓",
            },
            "AWS": {
                "Content sources": "not covered",
            },
        },
        "work": [
            ("The Series", [
                ("22 concerns, each on its own page", "done", "L", "AI architecture"),
                ("Live flow pages from real Azure turns", "done", "M", "Observability"),
                ("Study the flows not yet covered, such as withdrawing a claim", "todo", "M", "AI architecture"),
            ]),
            ("The tutorial", [
                ("Hand-drawn pages from architecture down to code", "done", "L", "Technical illustration"),
                ("Real code, call stacks and class diagrams on design pages", "done", "M", "Python"),
                ("Tech comparisons for every concern", "done", "M", "Cloud and open source"),
            ]),
            ("Published", [
                ("Live at /learn/agent-harness/ with a redacted Series", "done", "S", "Web publishing"),
                ("One page per lesson with a short exercise", "todo", "M", "Teaching"),
                ("Add a data engineering course in the same style", "todo", "L", "Data engineering"),
            ]),
        ],
        "roles": [
            ("Course reviewer", 2, "1-2 hours/week", "Reads pages as a newcomer and reports what was unclear."),
            ("Content author", 1, "3-5 hours/week", "Writes and draws new pages from the live agent."),
            ("Exercise designer", 1, "2-3 hours/week", "Writes hands-on exercises for each lesson."),
        ],
        "learn": [
            "What sits around a model call in a production agent, and why.",
            "How one message travels through sign-in, routing, the loop, tools and checks.",
            "How to choose between Azure services and open-source tools per concern.",
            "How evaluation, cost and testing are designed into an agent.",
            "How to read real agent code with a call stack and class diagram beside it.",
        ],
        "questions": [
            "Which step in one message's journey would fail first under load?",
            "Where in the loop would you put a check that blocks a reply?",
            "When does an agent need durable execution rather than a simple retry?",
            "What would you change to run the same agent on a different cloud?",
        ],
        "repo": None,
        "repo_public": False,
        "links": [
            ("The tutorial", "/learn/agent-harness/"),
            ("One message, end to end", "/learn/agent-harness/flow.html"),
            ("The Series (deep dive)", "/learn/agent-harness/series/"),
            ("All courses", "/learn/"),
        ],
        "good_first": [
            "Read the tutorial start to end and list unclear pages",
            "Draft an exercise for one lesson",
            "Check the code on three pages still matches the repository",
        ],
    },
]
