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
    ("Swap anything, break nothing: software design patterns for agent harnesses", "ai", "builders", "explainer",
     "Inversion of control, ports and adapters, strategy, chain of responsibility for guards, decorators for retries, and contract tests per port."),
    ("The autonomous agent tech stack, one concern at a time", "ai", "builders", "explainer",
     "A complete map of the tools for each concern: loop, models, tools, memory, context, guardrails, security, human in the loop, tracing, evals, durability and cost."),
    ("One harness, five homes: the agent harness on Azure, GCP, AWS, Databricks and open source", "ai", "builders", "decision",
     "The same harness concerns mapped to each platform's products side by side, where each platform is strong or thin, and how to pick."),
    ("Building agents on a moving ship: what has settled, what is still open, and how not to get stuck", "ai", "builders", "decision",
     "Which parts of the agent stack are adopted and here to stay, which are still in flux, and how to keep your agent tool-agnostic with ports, adapters and contract tests."),
    ("Choosing your agent loop: LangGraph vs OpenAI Agents SDK vs Claude Agent SDK vs plain code", "ai", "builders", "decision",
     "A comparison of orchestration and loop frameworks, with a 'pick this when' table."),
    ("Just use Postgres: the one database your agent needs", "ai", "builders", "decision",
     "Why PostgreSQL is here to stay for agents: one database for state, memory with pgvector, checkpoints, durable workflows, queues and the audit log, on every cloud (Lakebase, Azure, AlloyDB, Aurora, Neon)."),
    ("Rust or Python for agents? Probably both", "ai", "builders", "decision",
     "Where Rust wins (sandboxes, gateways, tool runtimes, speed, memory safety, one small binary), where Python wins (libraries, evals, fast iteration), and the common split: Python for the thinking, Rust for the heavy lifting."),
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
    ("OpenTelemetry is here to stay: instrument your agent once, send traces anywhere", "ai", "builders", "decision",
     "Why OpenTelemetry is the one settled bet in a moving stack, its GenAI conventions, and how to adopt it so you can switch between Langfuse, Phoenix, Datadog or Azure Monitor without touching agent code."),
    ("Before it ships: offline evals for autonomous agents", "ai", "builders", "explainer",
     "Golden datasets, LLM-as-judge vs deterministic checks, baselines, and catching regressions."),
    ("The agent testing pyramid", "ai", "builders", "explainer",
     "The whole testing strategy: unit, tool contracts, simulation, evals and production monitoring."),
    # AgentTwin (simulation: what an agent must face before it meets real people)
    ("A flight simulator for your agent: what AgentTwin is, and what it is not", "ai", "builders", "explainer",
     "Testing what an agent will face, not just what it says; how an agent twin differs from a digital twin."),
    ("Your agent passed every test. Then it met a real customer.", "ai", "builders", "field-note",
     "Why scripted tests miss: simulated users, broken systems and attackers, shown with a good agent and a faulty one."),
    ("Describe the world, not the test", "ai", "builders", "explainer",
     "The AgentTwin world format: write the users, systems, data and faults once, and let the scenarios come from it."),
    ("Who checks the checker? The oracle problem in agent simulation", "ai", "builders", "explainer",
     "How a simulation decides pass or fail: deterministic checks first, an LLM judge only where nothing else works."),
    ("Build only the gaps: AgentTwin assembled from open-source tools", "ai", "builders", "decision",
     "38 open-source tools behind clean seams, and the four pieces that had to be built because nothing else did the job."),
    ("AgentTwin vs LangWatch, Veris and friends: the simulation landscape", "ai", "builders", "decision",
     "What each tool simulates, what it leaves out, and which one to pick for your agent."),
    ("Why your agent costs $4 per question: 9 cost mistakes", "ai", "builders", "field-note",
     "Context bloat, no caching, the wrong model per step, runaway loops, retries, and no per-task budget."),
    ("Answer without the model first: 104 ms vs 7 seconds", "ai", "builders", "build-log", ""),
    ("Most of an agent is ordinary software", "ai", "builders", "explainer", ""),
    ("Why we wrote our own agent loop", "ai", "builders", "decision", ""),
    ("The horse and the harness", "ai", "leaders", "leader-brief", ""),

    # ---- LLM Engineering
    ("There is no best model, only the best model for this step", "llm", "builders", "decision",
     "How to pick models for a vertical agent: test on your own tasks, weigh accuracy against cost and speed, open vs closed, where data may go, and a model per step."),

    # ---- Cost
    ("What one conversation costs: under a tenth of a cent", "cost", "leaders", "leader-brief", ""),

    # ---- Career
    ("The AI engineer roadmap: what to learn, in what order, and what to skip", "career", "builders", "explainer",
     "A phased path from data or software engineer to AI engineer, with a picture map of the skills."),
]
