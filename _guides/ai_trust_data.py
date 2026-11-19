"""Content for the AI governance guide: 18 capabilities, six groups.

Each capability: n, name, q (the question a leadership team asks), plain (what it is),
design (decisions to make), build (what to implement), tools (standards / open source / cloud),
edge (how to make it innovative), proof (how you know it works), links.
Tool and standard names are examples, not endorsements. Check current versions before you rely on them.
"""

KINDS = [
    ("Bought-in AI", "AI inside products you buy: a CRM that scores leads, an HR tool that ranks CVs, a help desk that drafts replies.", "You cannot test it, only question the vendor and limit its data."),
    ("Staff using public tools", "People pasting work into chat assistants, writing assistants and meeting recorders on their own.", "You cannot see it unless you look; policy and a safe approved option are the main levers."),
    ("Classical models", "Scoring, forecasting and recommendation models that are not language models: credit, churn, demand, fraud.", "Older rules (model risk management) already apply; fairness and drift are the main worries."),
    ("Language-model apps", "Your own summarisers, extractors, search-and-answer tools and chat assistants.", "Wrong answers, leaks and tricks through the text they read."),
    ("Agents", "Systems where the model chooses tools and takes actions: refunds, bookings, record changes.", "The largest risk, because a mistake changes something in the real world."),
    ("Models you train or tune", "Models trained or fine-tuned on your data, including open-weight models you host.", "Training-data rights, poisoning, model theft and reproducibility."),
]

GROUPS = [
    ("know", "Know what you have", "You cannot govern what you cannot see. These three produce the list that everything else hangs on.", "peri"),
    ("decide", "Decide the rules", "Who may do what, who answers for it, and what must be checked before a use is allowed.", "butter"),
    ("prove", "Prove it before launch", "Evidence, not promises. Data you may use, tests that pass, and a trail an auditor can follow.", "mint"),
    ("run", "Run it safely", "What holds while the system is live, and what happens when it goes wrong.", "rose"),
    ("open", "Be open and capable", "People who use AI, or are affected by it, are told and are able.", "lilac"),
    ("across", "Across everything", "Cost and platform choices that touch every other capability.", "sky"),
]

C = []

C.append(dict(
    n=1, g="know", name="Inventory (the AI register)",
    q="Can you list every AI use in the organization, who owns it, and what data it touches?",
    plain="A single maintained list of AI uses. One row per use, not per tool: the same chat assistant used for drafting emails and for screening applicants is two rows, because the risk is different.",
    design=[
        "What counts as an entry: any use where AI output affects a decision, a customer, or a document that leaves the building.",
        "The unit of the register: the use (purpose + system + data + audience), not the product.",
        "Who must register, and what happens to a use that is not registered after a set date.",
        "How entries stay true: owners confirm each quarter, and a change in model or data triggers an update.",
    ],
    build=[
        "Start with a spreadsheet or table with fixed columns: id, purpose, owner, system, model and version, vendor, data classes, users, region, autonomy level, risk tier, status, last review.",
        "Move to a small service with an API once there are more than a few dozen entries, so pipelines can read and write it.",
        "Feed it from places that already know: cloud billing for model spend, API gateway logs, identity provider app lists, procurement records.",
        "Publish an AI bill of materials per system (model, datasets, libraries) so an entry can be traced to its parts.",
    ],
    tools=dict(
        standards="ISO/IEC 42001 asks for a documented inventory of AI systems; EU AI Act expects providers and deployers to know their systems; CycloneDX (ML-BOM) and SPDX 3.0 (AI profile) describe an AI bill of materials.",
        open="Backstage catalog or any metadata catalog (DataHub, OpenMetadata) with a custom AI entity; MLflow Model Registry for models you train.",
        cloud="AWS SageMaker Model Registry and Bedrock model inventory; Azure AI Foundry and Purview; Databricks Unity Catalog for models and endpoints; Google Vertex AI Model Registry.",
    ),
    edge="Make the register live, not a document: generate most rows from gateway logs and cloud inventories, and ask owners only to confirm. A register that fills itself is far more accurate than one people maintain by hand.",
    proof="Coverage: of the AI calls seen in gateway and billing data, what share map to a registered use? Target it, publish it, and watch it rise.",
    links=[("AI Assurance Catalog", "https://github.com/dataagentsai/ai-assurance-catalog")],
))

C.append(dict(
    n=2, g="know", name="Discovery (finding what nobody registered)",
    q="What AI is in use that we have not been told about?",
    plain="The register only lists what people declare. Discovery looks for the rest: tools staff signed up for, features switched on inside software you already own, and scripts calling model APIs with a personal key.",
    design=[
        "Which signals you will watch: network and proxy logs, identity provider sign-ins, expense claims, browser extensions, code repositories, cloud accounts.",
        "What you do when you find something: an amnesty and a path to approval works better than blocking and punishing.",
        "What you will not do: read staff content. Discovery looks at which tools and how much, not what was typed.",
    ],
    build=[
        "Keep a list of known AI domains and API endpoints; match it against proxy or DNS logs weekly.",
        "Scan source repositories and notebooks for model SDK imports and API keys.",
        "List OAuth grants and SaaS apps in the identity provider; flag those with AI features.",
        "Review corporate card and expense lines for AI subscriptions.",
        "Send each finding to the owner with three choices: register it, replace it with an approved option, or stop.",
    ],
    tools=dict(
        standards="OWASP AI Exchange and OWASP LLM Top 10 name the risks of unmanaged use; NIST AI RMF 'Map' function covers knowing context and uses.",
        open="Gitleaks or TruffleHog (find keys in code), Semgrep rules for SDK imports, Zeek or Suricata for DNS and network logs, osquery for browser extensions.",
        cloud="Microsoft Defender for Cloud Apps and Purview (AI app discovery), AWS CloudTrail and Config, Google Cloud Asset Inventory, any secure web gateway.",
    ),
    edge="Pair discovery with an easy approved route. If getting a safe assistant takes a day, shadow use falls; if it takes three months, it grows.",
    proof="Count of unregistered uses found per month, and the time from finding one to it being registered, replaced or stopped.",
    links=[],
))

C.append(dict(
    n=3, g="know", name="Risk tiering",
    q="Which uses need heavy checking and which can move fast?",
    plain="A short rule that sorts every AI use into a few tiers. The tier decides how much testing, review and monitoring the use must have. Without it, you either check everything (too slow) or nothing (too risky).",
    design=[
        "The questions that set the tier. A useful set: how much can the output change a person's life or money? How autonomous is the system? What data does it use? Who sees the output? Can it be reversed?",
        "How many tiers. Three or four is enough: minimal, limited, high, and not allowed.",
        "What each tier requires, written as a table, so a tier is an instruction and not just a label.",
        "Who may overrule a tier, and how that is recorded.",
    ],
    build=[
        "Write the tiering questionnaire as code or a form that returns a tier plus its reasons.",
        "Store the answers, not just the result, so a tier can be re-computed when rules change.",
        "Link each tier to a checklist of required controls from the other capabilities in this guide.",
        "Align the top tier with the legal definitions that apply to you (for example the EU AI Act's high-risk list and banned practices).",
    ],
    tools=dict(
        standards="EU AI Act (prohibited, high-risk, limited-risk and minimal-risk categories); ISO/IEC 23894 (AI risk management guidance); NIST AI RMF 'Map' and 'Measure'; Australia's Voluntary AI Safety Standard; Singapore's Model AI Governance Framework.",
        open="A decision table in a rules engine (OPA, Drools) or plain YAML plus a validator.",
        cloud="No major cloud provides this for you; it is your policy, expressed as data.",
    ),
    edge="Tier by autonomy as well as impact. A tool that only suggests and a tool that acts can hold the same data yet need very different controls. Most frameworks tier on impact alone.",
    proof="Agreement test: give ten real uses to three reviewers independently. If they land on the same tier for at least nine, your questions are clear enough.",
    links=[],
))

C.append(dict(
    n=4, g="decide", name="Policy and acceptable use",
    q="Who may use which AI, for what, with which data?",
    plain="The written rules, split by role, function and data class, and the technical settings that make the rules real. A policy nobody can enforce is a wish.",
    design=[
        "A short principle-level policy that leadership signs, with detailed standards underneath it that change faster.",
        "A matrix: role (and function) by data class by AI route. For example, customer data may go only to the approved internal assistant.",
        "Which uses are banned outright, which need approval, and which are pre-approved.",
        "What a person does when the policy blocks something legitimate (an exception route with an expiry date).",
    ],
    build=[
        "Express the matrix as policy-as-code so the same rule is applied by the gateway, the data platform and the identity provider.",
        "Put one gateway in front of all model calls to apply the rules, log the calls, and strip or block sensitive data.",
        "Publish a one-page plain-language version that staff will actually read.",
        "Review the policy on a calendar and whenever a new class of tool appears.",
    ],
    tools=dict(
        standards="ISO/IEC 42001 clause on AI policy; ISO/IEC 38507 (governance implications of AI use); NIST AI RMF 'Govern'.",
        open="Open Policy Agent (Rego) or Cedar for rules; LiteLLM, Envoy AI Gateway or Kong AI Gateway as the single gateway; Microsoft Presidio for detecting personal data.",
        cloud="Amazon Bedrock Guardrails, Azure AI Content Safety, Google Cloud Model Armor, Microsoft Purview DLP.",
    ),
    edge="Treat policy as code with tests and versions, like software. Each rule has an example that must be blocked and one that must pass, run on every change.",
    proof="Share of AI calls that pass through the gateway, and the number of policy violations blocked versus found afterwards.",
    links=[("Agent guardrail catalog", "/learn/agent-guardrails/")],
))

C.append(dict(
    n=5, g="decide", name="Roles and accountability",
    q="When an AI use goes wrong, who is answerable, and who had to approve it?",
    plain="Named people for each AI use and a small body that decides the hard cases. Accountability that is shared across a committee is, in practice, accountability that is nobody's.",
    design=[
        "A single accountable owner per use (the business), a technical owner (builds and runs it), and an independent reviewer for higher tiers.",
        "A standing group with legal, security, data, risk and business members that meets on a fixed rhythm and has authority to say no.",
        "Which decisions need which sign-off, by tier, so approvals are not negotiated each time.",
        "Separation of duties: the builder does not approve their own high-risk system.",
    ],
    build=[
        "Add owner, reviewer and approver fields to every register entry and block go-live without them.",
        "Write a RACI (who is responsible, accountable, consulted, informed) for each stage in the AI lifecycle.",
        "Keep a decision log: what was decided, by whom, on what evidence, with what conditions.",
        "Run a review board cadence tied to tiers: fast lane for low risk, scheduled review for high.",
    ],
    tools=dict(
        standards="ISO/IEC 42001 (roles, responsibilities and authorities); NIST AI RMF 'Govern' (accountability structures); EU AI Act (human oversight and deployer duties).",
        open="Architecture decision records (ADRs) in a repository; a ticketing workflow with required approvers.",
        cloud="Approval workflows in ServiceNow, Jira or a GRC platform are the usual home; the design matters more than the tool.",
    ),
    edge="Publish the decision log (redacted). Showing how and why you said yes or no is the strongest signal of a real governance practice.",
    proof="Share of live uses with a named owner and a recorded approval, and the median days from request to decision per tier.",
    links=[],
))

C.append(dict(
    n=6, g="decide", name="Impact assessment",
    q="Before we launch, have we written down who could be harmed and how?",
    plain="A structured document completed before a use goes live. It covers who is affected, what could go wrong for them, what protects them, and what remains. Think of it as a risk assessment for people, not for the company.",
    design=[
        "When one is required: by tier, and whenever the purpose, data or model changes materially.",
        "Who completes it (the owner) and who challenges it (an independent reviewer).",
        "What it must cover: purpose, affected groups, data, fairness and bias, privacy, human oversight, failure modes, and how to appeal a decision.",
        "How it joins existing privacy and security reviews rather than becoming a third separate form.",
    ],
    build=[
        "Create a template with required fields and mark which answers force a higher tier.",
        "Link each answer to evidence, such as test results, so claims are checkable.",
        "Store assessments next to the register entry, versioned.",
        "Re-run it on a schedule and on any significant change.",
    ],
    tools=dict(
        standards="ISO/IEC 42005 (AI system impact assessment); GDPR Article 35 data protection impact assessment; EU AI Act Article 27 fundamental rights impact assessment for certain deployers; Canada's Algorithmic Impact Assessment tool as a worked model.",
        open="Templates from the OECD and from public-sector bodies; a Markdown or form template in a repository.",
        cloud="Microsoft publishes a Responsible AI Impact Assessment template; most clouds provide documentation, not a tool.",
    ),
    edge="Generate the evidence section automatically from the test run and monitoring data, and leave people to write only the judgments. It keeps assessments short and honest.",
    proof="Share of high-tier uses with a current assessment, and the number of changes to a design that the assessment actually caused. Zero changes in a year suggests a rubber stamp.",
    links=[],
))

C.append(dict(
    n=7, g="decide", name="Bought-in and vendor AI",
    q="What AI is inside the products we buy, and what are we accepting by using it?",
    plain="You do not control a vendor's model, but you do control what data it gets, what you ask of the vendor, and whether you can switch. Third-party AI needs its own review because most of your AI exposure is probably here.",
    design=[
        "A vendor questionnaire specific to AI: models used, training on your data, subprocessors, data location, change notices, incident duties.",
        "Contract terms: no training on your data without consent, notice of model changes, audit rights, exit and data return.",
        "How you test what you cannot see: sample outputs, a bias check on a data sample, a reliability check on your own cases.",
        "Concentration risk: what happens if the one model provider you depend on changes terms or goes down.",
    ],
    build=[
        "Add a vendor AI section to procurement and security review, and block purchases that skip it.",
        "Register every vendor AI feature as an entry, with the vendor as the owner of the model and you as owner of the use.",
        "Keep a fallback route (a second provider or an open-weight model) for important uses.",
        "Re-review at renewal, and whenever the vendor announces a model change.",
    ],
    tools=dict(
        standards="ISO/IEC 27001 and SOC 2 reports for the vendor; ISO/IEC 42001 certification as a signal; NIST AI RMF 'Govern' on third-party risk; EU AI Act provider and deployer duties.",
        open="Cloud Security Alliance AI Controls Matrix and its due-diligence questionnaire; the open Shared Assessments SIG content.",
        cloud="Vendor trust centres and model cards (AWS AI Service Cards, Azure Transparency Notes, Google model cards).",
    ),
    edge="Run your own small test set against each important vendor feature and keep the results. When the vendor updates the model, you will see the difference the day it happens.",
    proof="Share of vendor AI features with a completed review, and time to detect a vendor model change.",
    links=[],
))

C.append(dict(
    n=8, g="prove", name="Data governance for AI",
    q="Are we allowed to use this data, is it good enough, and can we trace it?",
    plain="AI inherits every problem your data has: wrong values, missing consent, personal data in places it should not be. This is the strongest foundation you can have, because most AI harm starts in data.",
    design=[
        "Which data classes may reach which AI routes, and the consent and purpose basis for each.",
        "Provenance for training, tuning, retrieval and evaluation data: where it came from, licence, date, who approved.",
        "Quality rules for AI inputs (freshness, completeness, duplicates) and for what you retrieve to answer questions.",
        "Retention, deletion and the right to be forgotten, including data already used to tune a model.",
    ],
    build=[
        "Tag columns and documents with sensitivity and purpose, and have the gateway and retrieval layer respect the tags.",
        "Capture lineage from source to prompt and to model, so any output can be traced back.",
        "Run data quality checks before data is used for tuning or retrieval, and fail closed.",
        "Keep dataset cards and a hash of each training set so a model can be reproduced and audited.",
    ],
    tools=dict(
        standards="ISO/IEC 5259 (data quality for analytics and machine learning); ISO/IEC 27701 (privacy); GDPR; India's DPDP Act 2023; EU AI Act Article 10 (data and data governance); OpenLineage for lineage; Datasheets for Datasets as documentation practice.",
        open="OpenLineage with Marquez, DataHub or OpenMetadata; Great Expectations or Soda for quality; Presidio for personal data detection; DVC or lakeFS for dataset versions.",
        cloud="Unity Catalog, Microsoft Purview, AWS Glue Data Catalog with Lake Formation, Google Dataplex.",
    ),
    edge="Make retrieval permission-aware: the assistant can only fetch passages the asking person could open themselves. Most leaks in document assistants come from skipping this.",
    proof="Share of AI data sources with lineage and sensitivity tags, and a test that an unauthorized user cannot retrieve restricted content through the assistant.",
    links=[("Data platform suite", "/learn/data-platform-suite/"), ("Shift left: fail fast on data code", "/learn/shift-left/")],
))

C.append(dict(
    n=9, g="prove", name="Pre-launch testing and validation",
    q="What evidence do we have that this system does what we claim, and fails safely?",
    plain="A catalog of tests chosen by the kind of system and its tier, with results kept as evidence. Different kinds of AI fail differently, so the tests differ: a summariser needs faithfulness checks, an agent needs checks on what it changed.",
    design=[
        "Which tests are owed for which kind of system (transform, extractor, retrieval answerer, assistant, workflow, agent, multi-agent) and for classical models (accuracy, stability, fairness).",
        "Pass marks set before running, not after seeing results.",
        "Separation of test data from tuning data, and a frozen test set for regression.",
        "Judging by outcomes in the world, not only by the text of the answer.",
    ],
    build=[
        "Build a regression suite of real cases, plus generated edge cases and attack cases.",
        "Run it in CI so every change to a prompt, model or tool is tested before release.",
        "Test agents in a simulated world with faults injected, and check what changed in the systems they touched.",
        "Store results with the model version and dataset hashes as evidence for the register entry.",
    ],
    tools=dict(
        standards="NIST AI RMF 'Measure'; NIST AI 600-1 (generative AI profile); OWASP LLM Top 10; MITRE ATLAS; ISO/IEC 42001 verification and validation controls; the AI Assurance Catalog (application type to test obligation).",
        open="promptfoo, DeepEval, Ragas, Inspect (UK AI Security Institute), lm-evaluation-harness, garak and PyRIT (attacks), Fairlearn and AIF360 (fairness), Giskard.",
        cloud="Bedrock evaluations, Azure AI Foundry evaluations, Vertex AI evaluation, MLflow evaluate.",
    ),
    edge="Check behaviour under test-like and live-like conditions. Systems that do better when they seem to be watched give false comfort, and few teams measure the gap.",
    proof="Share of owed tests that exist and pass, per tier. Report the obligations you could not test as well; the unmapped list is the honest gap.",
    links=[("AI Assurance Catalog", "https://github.com/dataagentsai/ai-assurance-catalog"), ("AgentTwin", "/learn/agenttwin/"), ("Eval Harness", "/learn/eval-harness/")],
))

C.append(dict(
    n=16, g="prove", name="Compliance mapping and audit evidence",
    q="Can we show an auditor, in an afternoon, how we meet each requirement?",
    plain="A cross-reference from each rule or standard to the control that meets it and the evidence that proves it. Done well, an audit becomes a query, not a project.",
    design=[
        "Which frameworks apply to you (law, sector rules, customer contracts, voluntary standards) and which you adopt as a baseline.",
        "One set of controls mapped to many frameworks, not one set per framework.",
        "Evidence rules: what counts, how long it is kept, who can alter it (nobody after the fact).",
        "What you say is not yet covered. A mapping with an honest 'not covered' list is more credible than a full one.",
    ],
    build=[
        "Keep a controls table: control id, description, owner, frameworks and clauses it satisfies, evidence source.",
        "Collect evidence automatically from pipelines (test reports, approvals, access logs) into a store with write-once retention.",
        "Generate an audit pack on demand: pick a use, get its tier, assessment, tests, approvals and monitoring summary.",
        "Test the mapping yearly by asking an outsider to find a requirement and trace it to proof.",
    ],
    tools=dict(
        standards="ISO/IEC 42001 (certifiable AI management system) and ISO/IEC 42006 (requirements for its auditors); NIST AI RMF; EU AI Act; OWASP and ATLAS crosswalks; OSCAL (NIST's machine-readable control format).",
        open="OSCAL tooling (compliance-trestle), OpenSSF Scorecard-style evidence checks, the AI Assurance Catalog crosswalk files.",
        cloud="AWS Audit Manager, Azure Policy and Purview Compliance Manager, Google Assured Workloads; GRC platforms as consumers of the evidence.",
    ),
    edge="Treat evidence as code. A control is a test that runs and emits a signed result; the audit pack is a view over those results.",
    proof="Time to assemble a complete audit pack for a named high-tier use, and the share of controls with automatically collected evidence.",
    links=[("AI Assurance Catalog crosswalks", "https://github.com/dataagentsai/ai-assurance-catalog")],
))

C.append(dict(
    n=10, g="run", name="Runtime controls",
    q="While the system is live, what stops it from doing something it should not?",
    plain="Checks that run on every request: what goes in, what comes out, and what actions are allowed. Testing shows it worked on your cases; runtime controls hold when the real world sends something you did not expect.",
    design=[
        "Where checks sit: on input, on retrieved content, on the model's output, and before any action with side effects.",
        "Which checks are plain rules (cheap, predictable), which are small classifiers, and which need a judge model. Use the simplest that works.",
        "What happens when a check fires: block, ask a person, retry safely, or degrade to a safe answer.",
        "Least privilege for tools: each agent gets only the actions it needs, with limits on amount and rate.",
    ],
    build=[
        "Put controls in a gateway or harness layer outside the model, so changing the model does not remove them.",
        "Require approval for irreversible or high-value actions, and keep a hard kill switch per use.",
        "Make actions idempotent so a retry cannot charge or send twice.",
        "Log every blocked and allowed decision with the rule that fired.",
    ],
    tools=dict(
        standards="OWASP LLM Top 10 (prompt injection, excessive agency, sensitive information disclosure); MITRE ATLAS; Google SAIF; EU AI Act Articles 14 and 15 (oversight, robustness and cybersecurity).",
        open="Open Policy Agent and Cedar for action rules; NeMo Guardrails, Guardrails AI, Llama Guard for content checks; Presidio for personal data.",
        cloud="Amazon Bedrock Guardrails and AgentCore policy, Azure AI Content Safety and Prompt Shields, Google Cloud Model Armor; Microsoft Agent Governance Toolkit.",
    ),
    edge="Write each guardrail as a rule plus the test that proves it holds, and keep both together. Then the catalog of controls and the catalog of tests cannot drift apart.",
    proof="Block rate on a standing set of attack and misuse cases, false-block rate on good cases, and time for the kill switch to take effect.",
    links=[("Agent guardrail catalog", "/learn/agent-guardrails/"), ("Agent Harness", "/learn/agent-harness/")],
))

C.append(dict(
    n=11, g="run", name="Monitoring and drift",
    q="How would we know, this week, that quality or behaviour has slipped?",
    plain="Continuous measurement after launch. Models, data, prompts, vendors and users all change, so something that passed in March can quietly fail by June.",
    design=[
        "What to measure: quality on sampled real traffic, fairness across groups, input drift, cost, latency, refusals, human overrides.",
        "Who looks at each signal and what threshold triggers action.",
        "Sampling and labelling: a small, steady stream of human-reviewed cases is worth more than a big one-time test.",
        "Privacy: monitor patterns and samples, and mask personal data in traces.",
    ],
    build=[
        "Emit traces for every model call using one common schema, with model version, prompt version, tool calls and outcome.",
        "Run the pre-launch test suite on a schedule against the live system (a canary).",
        "Compute drift on inputs and outputs and alert on the shift, not only on errors.",
        "Review a weekly sample of real conversations or decisions with a short rubric.",
    ],
    tools=dict(
        standards="OpenTelemetry GenAI semantic conventions; NIST AI RMF 'Manage'; EU AI Act Article 72 (post-market monitoring) and Article 12 (logging); SR 11-7 ongoing monitoring for models in banking.",
        open="OpenTelemetry, Langfuse, Arize Phoenix, OpenLLMetry, Evidently (drift), Prometheus and Grafana.",
        cloud="CloudWatch and Bedrock invocation logs, Azure Monitor and Application Insights, Cloud Monitoring, Databricks Lakehouse Monitoring, SageMaker Model Monitor.",
    ),
    edge="Monitor the controls themselves: track how often each guardrail fires. A guardrail that never fires, or fires on everything, is a silent failure.",
    proof="Time from a real quality drop to an alert, measured by planting a known regression in a staging copy.",
    links=[("Eval Harness", "/learn/eval-harness/")],
))

C.append(dict(
    n=12, g="run", name="Incident response and reporting",
    q="When an AI use harms someone or leaks something, what do we do in the first hour, and who do we tell?",
    plain="AI incidents are different from outages: the system may be 'up' while giving harmful answers. You need a way to recognise them, contain them, learn from them, and report them where the law requires.",
    design=[
        "What counts as an AI incident: harmful output, leak, discrimination, unauthorized action, serious near miss.",
        "Severity levels and who is called at each, including legal, communications and the affected business.",
        "Reporting duties: serious incidents to regulators, personal data breaches to privacy authorities, notices to customers.",
        "Containment options prepared in advance: switch off, fall back to a person, roll back a model, restrict a tool.",
    ],
    build=[
        "Extend the existing security incident process with AI-specific playbooks and severity guides.",
        "Give staff and customers an easy way to report a bad AI output, and route it to the owner.",
        "Capture the full trace (inputs, retrieved data, tool calls, versions) for any reported case.",
        "After each incident, add a regression test and update the relevant control; record both in the register entry.",
    ],
    tools=dict(
        standards="EU AI Act Article 73 (serious incident reporting for high-risk systems); GDPR breach notification; OECD AI incident reporting framework; NIST AI RMF 'Manage'; MITRE ATLAS case studies.",
        open="AI Incident Database (public incidents to learn from); OWASP guidance; incident tooling you already run.",
        cloud="Existing cloud security and on-call tooling; the AI-specific part is the playbook and the trace.",
    ),
    edge="Run tabletop exercises on AI scenarios (a leak through the assistant, an agent issuing wrong refunds) and publish the lessons. Few organizations have rehearsed these.",
    proof="Time to contain in a drill, share of incidents that produced a new test, and whether each reporting deadline was met.",
    links=[],
))

C.append(dict(
    n=13, g="run", name="Lifecycle: change, re-approval, retirement",
    q="When the model, prompt or data changes, is the approval still valid, and when do we turn things off?",
    plain="Approval is for a particular version in a particular setting. Model providers update models, teams edit prompts, data shifts. Without lifecycle rules, an approved system slowly becomes an unapproved one.",
    design=[
        "What counts as a material change that needs re-testing or re-approval, by tier.",
        "How model and prompt versions are pinned, and how upgrades are staged.",
        "When a use is reviewed even if nothing changed (a yearly review is common).",
        "How uses are retired: what happens to data, logs and users.",
    ],
    build=[
        "Version prompts, tools, models and test sets together; store the bundle with the register entry.",
        "Block promotion to production unless the owed tests pass on the exact bundle.",
        "Use staged rollout: shadow mode, small share of traffic, then full, with rollback.",
        "Schedule expiry dates on approvals so unused or unreviewed systems lapse by default.",
    ],
    tools=dict(
        standards="ISO/IEC 5338 (AI system life cycle processes); ISO/IEC 42001 operation and change controls; EU AI Act on substantial modification; SR 11-7 on model change.",
        open="Git and CI for prompts and configs, MLflow, DVC, feature-flag tools (OpenFeature), model signing with the OpenSSF model-signing project.",
        cloud="Model registries and deployment pipelines in the major clouds; provider model-deprecation notices.",
    ),
    edge="Give every approval an expiry. Approvals that lapse by default keep the register honest and force a conversation about what is still needed.",
    proof="Share of production systems whose running version matches an approved bundle, and the count of lapsed approvals found each quarter.",
    links=[],
))

C.append(dict(
    n=14, g="open", name="Transparency and documentation",
    q="Do people know when they are dealing with AI, and can we explain what it does?",
    plain="Three audiences need different documents: users need a notice, affected people need an explanation and a way to appeal, and technical reviewers need a full record of how the system works.",
    design=[
        "Where users must be told they are talking to AI or reading AI-made content.",
        "What an explanation looks like for a decision, in plain words, and how a person asks for human review.",
        "Technical documentation standard: model card, data card, intended use, limits, known failures, test results.",
        "How AI-made media is labelled and its source recorded.",
    ],
    build=[
        "Generate model and system cards from the register and test results, so they stay current.",
        "Add visible notices and a human-review route to user-facing flows.",
        "Attach provenance data to generated media where your channel supports it.",
        "Publish a public statement of how you use AI and what you will not do, if your sector expects it.",
    ],
    tools=dict(
        standards="EU AI Act Article 50 (transparency duties) and Annex IV (technical documentation); Model Cards and Datasheets for Datasets; C2PA content credentials; ISO/IEC 42001 documentation controls.",
        open="Hugging Face model card tooling, Google's Model Card Toolkit, C2PA open-source libraries, SHAP and LIME for explanations of classical models.",
        cloud="AWS AI Service Cards, Azure Transparency Notes, SageMaker Model Cards, Vertex AI model cards.",
    ),
    edge="Write the explanation for the person affected first, then derive the technical record from it. It forces clarity about what the system actually does.",
    proof="Test the notice and the explanation on real users: can they say, afterwards, that AI was involved and how to get a person?",
    links=[],
))

C.append(dict(
    n=15, g="open", name="AI literacy and training",
    q="Do the people using and approving AI understand what it can and cannot do?",
    plain="Rules do not work if people do not understand them. Training should differ by role: everyone needs the basics and the do-and-don't list, builders need secure and testable practice, approvers need to read evidence critically.",
    design=[
        "Role-based tracks: everyone, builders, approvers and reviewers, leaders.",
        "Short, practical content with real examples from your own incidents and near misses.",
        "How you check it worked: a test or a practical exercise, not attendance.",
        "A regular refresher, because the tools change quickly.",
    ],
    build=[
        "Build a one-hour baseline course with scenarios, and a half-day workshop for approvers.",
        "Add 'how do I check the AI's answer' habits to the course: sources, second checks, when to stop and ask.",
        "Track completion by role and link it to access to approved tools where appropriate.",
        "Run a yearly red-team day where staff try to trick internal assistants.",
    ],
    tools=dict(
        standards="EU AI Act Article 4 (AI literacy duty for providers and deployers); ISO/IEC 42001 competence controls; NIST AI RMF 'Govern'.",
        open="Open courses (for example Elements of AI, BlueDot Impact's AI safety courses), OWASP training material, Anthropic and other labs' public prompting guides.",
        cloud="Cloud training catalogs for builders; internal learning platforms for the rest.",
    ),
    edge="Teach by showing your own failures. A short, honest case from your incident log changes behavior more than any slide of rules.",
    proof="Scenario test scores by role before and after, and a fall in policy violations and shadow-tool findings.",
    links=[("Key concepts, A to Z", "/concepts/")],
))

C.append(dict(
    n=17, g="across", name="Cost control for AI",
    q="What does each AI use cost, who pays, and what happens when usage spikes?",
    plain="AI cost is variable and easy to lose track of: tokens, retries, long conversations, and idle GPUs. Cost is also a safety issue, since a runaway agent loop can burn a month's budget in an afternoon.",
    design=[
        "Cost per use, per team and per outcome (for example per resolved ticket), not just per model.",
        "Budgets and hard limits per use, with an alert before the limit and a stop at it.",
        "Which tasks deserve a large model and which a small one; routing rules and caching.",
        "How the benefit is measured, so that cost is compared with value.",
    ],
    build=[
        "Tag every model call with the register id so spend rolls up by use.",
        "Set per-use token and spend limits in the gateway, plus a limit on agent steps.",
        "Cache repeated requests, route easy ones to smaller models, and measure the quality you give up.",
        "Report monthly: cost per use, cost per outcome, top movers.",
    ],
    tools=dict(
        standards="FinOps Foundation framework and the FOCUS billing specification; OpenTelemetry for token and cost attributes.",
        open="LiteLLM and Portkey-style gateways for budgets, OpenCost, Kubecost, Langfuse cost tracking.",
        cloud="AWS Cost Explorer with application inference profiles, Azure Cost Management, Google Cloud Billing, Databricks system tables.",
    ),
    edge="Report cost per correct outcome, not cost per token. A cheap model that needs three retries and human fixes can be the expensive one.",
    proof="Share of AI spend attributed to a registered use, and forecast error month to month.",
    links=[("Cost and FinOps for data platforms", "/learn/data-systems/platform/cost/")],
))

C.append(dict(
    n=18, g="across", name="Multi-cloud and platform control",
    q="Can the same rules hold when AI runs on several clouds, tools and vendors?",
    plain="Real organizations use more than one cloud, several model providers and many SaaS tools. If every platform has its own rules, governance fragments. The aim is one set of rules, with a thin adapter for each platform.",
    design=[
        "Which controls are universal (policy, register, evidence) and which are implemented per platform (a gateway setting, a cloud guardrail).",
        "A 'paved road': the approved way to build and run AI, easy enough that teams choose it.",
        "How you avoid lock-in for critical uses: ports and adapters, with a second provider tested.",
        "Where data may be processed (region, residency) and how that is enforced.",
    ],
    build=[
        "Define interfaces for model calls, retrieval, tools, logging and policy; implement one adapter per vendor.",
        "Store the rules once as policy-as-code and compile them to each platform's native settings.",
        "Run the same test suite against each adapter on a schedule to catch drift between platforms.",
        "Standardize on a few open formats: OpenTelemetry for traces, OpenLineage for lineage, OSCAL for controls, CycloneDX for AI bills of materials.",
    ],
    tools=dict(
        standards="OpenTelemetry, OpenLineage, OSCAL, CycloneDX ML-BOM, Model Context Protocol for tool access, ISO/IEC 42001 as the management system that spans platforms.",
        open="Open Policy Agent, Envoy AI Gateway, LiteLLM, Terraform or OpenTofu, Kubernetes, Crossplane.",
        cloud="AWS, Azure, Google Cloud and Databricks each ship guardrail, registry and monitoring features. Use them behind your interfaces, not as the interface.",
    ),
    edge="Prove portability with a contract test: the same governance test suite must pass on every adapter. If switching provider is only an adapter plus a configuration file, you have control.",
    proof="Time and effort to move one important use to a second provider with all controls intact, measured in a drill.",
    links=[("Agent Harness", "/learn/agent-harness/"), ("Data platform suite", "/learn/data-platform-suite/")],
))

ORDER = [
    ("Crawl", "Weeks 1 to 6", "Know and decide", [1, 3, 4, 5], "A spreadsheet register, a three-tier rule, a one-page policy, named owners. Nothing else works without these."),
    ("Walk", "Months 2 to 4", "Prove and watch", [2, 6, 7, 8, 9, 10, 11], "Discovery, assessments, vendor review, data tags, a test suite in CI, a gateway with basic controls, traces."),
    ("Run", "Months 4 to 9", "Mature and automate", [12, 13, 14, 15, 16, 17, 18], "Incident drills, lifecycle expiry, transparency, training, audit packs, cost attribution, portability tests."),
]

WORDS = [
    ("AI governance", "Who decides what AI may be used, who is accountable, and how we prove it.", "The whole guide; strongest in capabilities 1 to 7 and 16."),
    ("Responsible AI", "Fair, explainable, private, and with a person answerable for the result.", "Capabilities 6, 8, 14, 15."),
    ("AI safety", "The system does not cause harm, even without an attacker, and we can stop it.", "Capabilities 9, 10, 12, 13."),
    ("AI security", "An attacker cannot steal, poison, trick or hijack the AI or its data.", "Capabilities 2, 7, 10, 11, 12."),
    ("Reliable AI", "It gives correct, consistent answers and keeps doing so as things change.", "Capabilities 9, 11, 13, 17."),
]
