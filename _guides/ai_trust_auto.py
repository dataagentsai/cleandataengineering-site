"""What can be automated, and what large organizations publicly do. Companion to ai_trust_data.py."""

# capability number -> (level, what is automated, what stays with people)
AUTO = {
    1: ("Mostly", "Rows filled from gateway logs, billing and cloud inventories; changes detected.", "Owners confirm purpose and data."),
    2: ("Fully", "Weekly scans of proxy logs, repositories, app grants and expenses.", "Someone triages each finding and offers a safe route."),
    3: ("Assisted", "The tier is computed from the answers and recomputed when rules change.", "A person answers the questions honestly and can overrule with a recorded reason."),
    4: ("Mostly", "Rules enforced by the gateway, data platform and identity provider; tests on every rule change.", "People write the policy and decide the exceptions."),
    5: ("Human", "Checks that every live use has an owner, reviewer and approval on file.", "Who is accountable, and the decisions of the review group."),
    6: ("Assisted", "Evidence sections filled from test and monitoring data; reminders on change.", "Judging harm to people and whether the remaining risk is acceptable."),
    7: ("Assisted", "Questionnaire routing, trust-page and certificate expiry checks, your own test set run against the vendor feature.", "Contract terms and the decision to accept the vendor."),
    8: ("Mostly", "Tagging, lineage capture, quality gates, permission-aware retrieval tests.", "Purpose and consent decisions, and what data is off limits."),
    9: ("Fully", "Regression, attack and fairness suites run in CI; results stored with versions.", "Choosing what to test and where the pass marks sit."),
    10: ("Fully", "Input, output and action checks on every request; budgets and kill switch.", "Setting limits and handling the cases that are held for a person."),
    11: ("Fully", "Traces, drift alerts, scheduled canary tests, cost and guardrail-fire rates.", "Reviewing a weekly sample and acting on alerts."),
    12: ("Assisted", "Detection, trace capture, paging, deadline timers for reporting.", "Judging severity, containment, and what to tell regulators and customers."),
    13: ("Mostly", "Blocks promotion without passing tests on the exact bundle; approvals expire by default.", "Deciding what counts as a material change."),
    14: ("Assisted", "Model and system cards generated from the register and test results.", "Writing the plain-language explanation and notices."),
    15: ("Assisted", "Enrolment, completion tracking, scenario tests.", "Designing the training and running the workshops."),
    16: ("Mostly", "Controls run as tests that emit evidence into write-once storage; audit packs generated on demand.", "The auditor's judgment, and your statement of what is not covered."),
    17: ("Fully", "Per-use cost tagging, budgets, stop limits, monthly reports.", "Deciding whether the value justifies the spend."),
    18: ("Mostly", "One rule set compiled to each platform; the same tests run on every adapter.", "Choosing platforms and accepting lock-in on purpose."),
}

LEVELS = {
    "Fully": "A machine does it and a person only handles exceptions.",
    "Mostly": "A machine does the routine work; people confirm or decide the hard parts.",
    "Assisted": "A machine prepares the evidence; a person makes the call.",
    "Human": "A person's decision. Machines only check that it was made.",
}

# organization -> (what it publicly states or sells, kind of evidence)
BIGCO = [
    ("Google and Google Cloud",
     "Published AI Principles and a Secure AI Framework (SAIF) that sets security practice across the AI life cycle; a Frontier Safety Framework for its most capable models; model cards; and cloud products for the controls in this guide, such as Model Armor (screening prompts and responses), Sensitive Data Protection, and evaluation services. It has also stated ISO/IEC 42001 certification for parts of its AI offering.",
     "Public documents and product pages"),
    ("Microsoft",
     "A Responsible AI Standard applied through internal review, Transparency Notes for its services, an AI red team, and products that bring the controls together: Purview (data and compliance), Defender (threats), and content safety. It has stated ISO/IEC 42001 certification for Microsoft 365 Copilot.",
     "Public documents and product pages"),
    ("Amazon Web Services",
     "Bedrock Guardrails, AgentCore policy at the gateway, AI Service Cards, an Audit Manager framework for generative AI, and ISO/IEC 42001 certification announced for several AI services.",
     "Public documents and product pages"),
    ("Anthropic and other frontier labs",
     "Published scaling policies that tie capability levels to required safeguards, with evaluations that must pass before a model is released; Anthropic has stated ISO/IEC 42001 certification.",
     "Public documents"),
    ("Large banks and insurers",
     "Decades of model risk management under rules such as SR 11-7: a central model inventory, independent validation before use, and ongoing monitoring. The newest AI work extends this existing machinery.",
     "Regulation and supervisory guidance"),
]

HONEST = [
    "Certification is a snapshot. ISO/IEC 42001 certification is an audit at a point in time. What makes it continuous is evidence collected automatically between audits.",
    "Technical controls automate well; judgment controls do not. Gateways, tests, monitoring, lineage and cost can run themselves. Accountability, harm judgment and exceptions stay with people, and the honest design makes that division explicit.",
    "The firm-wide pieces are younger. Runtime guardrails and evaluation are common in products. A live register that fills itself, tiering that recomputes, and audit packs generated from evidence are newer, and mostly show up in vendor offerings and early adopters, not as settled practice.",
    "Public claims are not audits. What a company publishes shows its intent and its products. It does not show how complete its internal coverage is.",
]

PRODUCTS = [
    ("Compliance automation for security standards", "Vanta, Drata, Secureframe and similar tools collect evidence continuously for ISO/IEC 27001 and SOC 2, and have added ISO/IEC 42001 frameworks."),
    ("AI governance platforms", "Credo AI, IBM watsonx.governance, ServiceNow AI Control Tower, OneTrust and others offer a register, assessments and policy workflows. Check how much is automated evidence and how much is forms."),
    ("Cloud-native policy and audit", "AWS Config and Audit Manager, Azure Policy and Purview Compliance Manager, Google Security Command Center. Strong for infrastructure; AI-specific controls are still being added."),
    ("Open building blocks", "Open Policy Agent and Cedar for rules, OSCAL for machine-readable controls and compliance-trestle to work with it, OpenTelemetry and OpenLineage for evidence, plus the AI Assurance Catalog for the test obligations."),
]
