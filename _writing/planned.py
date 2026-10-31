"""Posts that are planned but not written yet. They show on /writing/ as "Coming soon".

To add one, copy a line and change it. Fields: title, stream, audience, kind, what it covers.
  stream:   data · analytics · ai · llm · cost · career   (labels in build.py SUBJECTS)
  audience: builders · leaders
  kind:     field-note · explainer · decision · build-log · leader-brief
When a post is written, give its .md file the same title; the "coming soon" line then disappears.
Every post must stay a 10-minute read or less (build.py warns when one runs over).
"""

PLANNED = [
    # ---- Data Engineering (Databricks)
    ("Bronze, Silver, Gold, and where most teams get it wrong", "data", "builders", "explainer",
     "The right medallion architecture: what each layer owns, what never belongs in it, and the common mistakes."),
    ("Stop writing pipelines: one metadata-driven ingestion framework for 500 tables", "data", "builders", "explainer",
     "A config table describes every source, so one generic pipeline replaces hundreds of hand-written ones."),
    ("Data quality as config, not code", "data", "builders", "explainer",
     "A metadata-driven data quality framework: rules live in a table, one engine runs them, bad rows go to quarantine."),
    ("Streaming on Databricks without the pain", "data", "builders", "decision",
     "The right streaming architecture: Lakeflow vs Structured Streaming, when a frequent batch is enough, and checkpoints."),
    ("Your Databricks bill has a leak: 10 cost mistakes we keep seeing", "data", "builders", "field-note",
     "Oversized clusters, all-purpose compute for jobs, small files, skew, idle warehouses and missing auto-stop."),
    ("Your Databricks cluster scales up and never comes back down", "data", "builders", "field-note", ""),
    ("What repeats is broken", "data", "builders", "explainer", ""),

    # ---- Data + AI (Analytics)
    ("Talk to your data the right way: Genie and metric views on Databricks", "analytics", "builders", "explainer",
     "The right architecture for a conversation UI: the model never writes raw SQL; metric views are the semantic layer and AI/BI Genie sits on top."),

    # ---- AI Engineering (autonomous agents)
    ("The model is 10%. The harness is the other 90%.", "ai", "builders", "explainer",
     "The right agent harness architecture: loop, tools, memory, context, guards and evals in one picture."),
    ("Choosing your agent loop: LangGraph vs OpenAI Agents SDK vs Claude Agent SDK vs plain code", "ai", "builders", "decision",
     "A comparison of orchestration and loop frameworks, with a 'pick this when' table."),
    ("DBOS vs Temporal: durable agents without the drama", "ai", "builders", "decision",
     "Durable execution for long-running agents: the two models, their trade-offs, and when you need neither."),
    ("Seatbelts for agents: guardrails that actually hold", "ai", "builders", "explainer",
     "Guardrails on input, tool calls, output and actions: one rule enforced in four places."),
    ("Your agent has the keys: security architecture for autonomous agents", "ai", "builders", "explainer",
     "Least-privilege tools, prompt injection, secrets, sandboxing, and who the agent acts as."),
    ("Human in the loop without humans in the way", "ai", "builders", "explainer",
     "The right human-in-the-loop architecture: approval points, risk tiers, async hand-offs, and what happens on timeout."),
    ("If you can't replay it, you can't fix it: tracing autonomous agents", "ai", "builders", "explainer",
     "Trace and logging design: a span per step and tool call, OpenTelemetry, and what to store vs redact."),
    ("Before it ships: offline evals for autonomous agents", "ai", "builders", "explainer",
     "Golden datasets, LLM-as-judge vs deterministic checks, baselines, and catching regressions."),
    ("The agent testing pyramid", "ai", "builders", "explainer",
     "The whole testing strategy: unit, tool contracts, simulation, evals and production monitoring."),
    ("Why your agent costs $4 per question: 9 cost mistakes", "ai", "builders", "field-note",
     "Context bloat, no caching, the wrong model per step, runaway loops, retries, and no per-task budget."),
    ("Answer without the model first: 104 ms vs 7 seconds", "ai", "builders", "build-log", ""),
    ("Most of an agent is ordinary software", "ai", "builders", "explainer", ""),
    ("Why we wrote our own agent loop", "ai", "builders", "decision", ""),
    ("The horse and the harness", "ai", "leaders", "leader-brief", ""),

    # ---- Cost
    ("What one conversation costs: under a tenth of a cent", "cost", "leaders", "leader-brief", ""),

    # ---- Career
    ("The AI engineer roadmap: what to learn, in what order, and what to skip", "career", "builders", "explainer",
     "A phased path from data or software engineer to AI engineer, with a picture map of the skills."),
]
