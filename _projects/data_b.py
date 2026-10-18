# Project detail data, group "learning" (file B).
# Public page: no client names, family, credentials, hostnames or commercial strategy.

LEAD = "Basant Choudhary"

PROJECTS = [
    # ------------------------------------------------------------------ 1
    {
        "id": "learn-llm-stack",
        "title": "LearnLLMStack",
        "subject": "llm",
        "group": "learning",
        "status": "active",
        "started": "2026-10",
        "lead": LEAD,
        "one_liner": "Build a tiny version of every LLM layer, from your own model up to the agent, and connect them.",
        "purpose": (
            "LearnLLMStack builds a small, slow version of each layer between an agent's question and a model's token. "
            "It starts at the bottom, by training a tiny language model on a small corpus, then adds the engine, server, provider, gateway, harness, tool server and tracing on top. "
            "It is for engineers who use LLMs every day but have never seen what happens below the API. "
            "The connections between the layers are the real lesson, so one request should finally travel through code you wrote at every step."
        ),
        "audience": "Software and data engineers who call LLM APIs and want to understand the provider side: training, inference, hosting and routing.",
        "benefits": [
            ("Fewer cost surprises", "Engineers who know why reading a prompt is cheaper than writing an answer make better choices about context size and caching."),
            ("Better vendor decisions", "A team that has built a gateway and a provider can tell which controls belong to them and which belong to the host."),
            ("Realistic fine-tuning plans", "Learners find out when fine-tuning is worth it and when a prompt or retrieval is enough, before paying for GPU time."),
            ("Skills that transfer", "Every layer speaks the common chat-completions format, so each home-made part can be swapped for a real product with one setting."),
        ],
        "functional": [
            "Train a language model from scratch in seven steps: counting, tokenizer, transformer, check against published weights, pretraining, chat tuning and tool-call tuning.",
            "Run the model through a hand-written generation loop with sampling and a key-value cache.",
            "Serve the model over HTTP in the common chat-completions format, with streaming and a request queue.",
            "Put a provider layer (keys, rate limits, billing) and a separate gateway layer (guardrails, budgets, routing) in front of the server.",
            "Connect an existing agent harness and a hand-built tool server, so the model can ask for tools and the harness runs them.",
            "Trace one request across every layer.",
            "Teach each step with a picture-book design page, step-by-step walkthrough pages and a fine-tuning learning path.",
        ],
        "nonfunctional": [
            "Runs on a laptop: models up to about 124 million parameters, no containers needed.",
            "Each layer starts with one command and has its own README.",
            "Each layer has a 'done when' check with a number, such as held-out loss or tokens per second.",
            "Tests are table-driven.",
            "Free resources only for heavier work, such as free notebook GPUs for fine-tuning.",
        ],
        "components": [
            ("Own model and engine", "Holds the trained weights and runs the predict-pick-append loop that makes tokens."),
            ("Inference server", "Turns the engine into a network service with streaming, queueing and batching."),
            ("Provider", "Plays the hosting company: API keys, rate limits, usage and billing."),
            ("Gateway", "Plays the company using the model: guardrails, budgets and routing."),
            ("Agent harness", "Runs the conversation loop and executes tool calls the model asks for."),
            ("Tool server", "Exposes tools such as files or a database over a simple message protocol."),
            ("Tracing", "Follows one request through every layer and records time and tokens."),
        ],
        "flows": [
            ("Agent harness", "Gateway", "chat request"),
            ("Gateway", "Provider", "checked request"),
            ("Provider", "Inference server", "authorised request"),
            ("Inference server", "Own model and engine", "batched prompts"),
            ("Own model and engine", "Inference server", "tokens"),
            ("Agent harness", "Tool server", "tool call"),
            ("Tracing", "Agent harness", "spans from every layer"),
        ],
        "bindings": {
            "Open stack": {
                "Own model and engine": "Plain Python (step 1 built), then PyTorch on the laptop GPU (next)",
                "Inference server": "FastAPI with server-sent events",
                "Provider": "FastAPI with a small key and usage store",
                "Gateway": "Hand-written, compared with LiteLLM",
                "Agent harness": "Reused from an existing reference agent",
                "Tool server": "JSON-RPC over stdio by hand, then FastMCP",
                "Tracing": "OpenTelemetry",
            },
            "Azure": {
                "Own model and engine": "Azure Machine Learning training",
                "Inference server": "Azure Machine Learning online endpoint",
                "Provider": "Azure AI Foundry",
                "Gateway": "Azure API Management AI gateway",
                "Agent harness": "Azure Container Apps",
                "Tool server": "Azure Functions",
                "Tracing": "Azure Monitor / Application Insights",
            },
            "AWS": {
                "Own model and engine": "SageMaker training",
                "Inference server": "SageMaker endpoint",
                "Provider": "Amazon Bedrock",
                "Gateway": "API Gateway with Bedrock Guardrails",
                "Agent harness": "ECS Fargate",
                "Tool server": "AWS Lambda",
                "Tracing": "AWS X-Ray / CloudWatch",
            },
        },
        "work": [
            ("Design before code", [
                ("Picture-book design page for every layer", "done", "M", "technical writing"),
                ("Decisions, glossary and reuse ledger", "done", "S", "architecture"),
                ("Fine-tuning learning path, nine phases", "done", "M", "ML"),
            ]),
            ("Layer 1: your own model", [
                ("Step 1: character bigram model on a children's story corpus", "done", "S", "Python"),
                ("Whole-LLM-on-one-sentence toy and walkthrough", "done", "S", "ML teaching"),
                ("Step 2: hand-written byte-pair tokenizer with round-trip tests, including Hindi and emoji", "todo", "M", "Python"),
                ("Step 3: small GPT-style transformer", "todo", "L", "PyTorch"),
                ("Step 4: load published GPT-2 weights and match outputs token for token", "todo", "M", "PyTorch"),
            ]),
            ("Fine-tuning path", [
                ("Phase 0: setup lesson and notebook", "done", "S", "ML"),
                ("'Should you fine-tune at all?' lesson", "done", "S", "technical writing"),
                ("Phase 2: first fine-tune with a chat template, loss masking and LoRA", "doing", "M", "ML"),
            ]),
            ("Layers 2 to 7", [
                ("Inference server with streaming and a load test table", "todo", "M", "Python / HTTP"),
                ("Provider and gateway as separate layers", "todo", "M", "backend"),
                ("Hand-built tool server, then compare with a library", "todo", "S", "protocols"),
                ("Trace one request across all layers", "todo", "M", "observability"),
            ]),
        ],
        "roles": [
            ("ML learner-builder", 1, "4-6", "Works through the model steps and fine-tuning phases and records results."),
            ("Backend engineer", 1, "2-4", "Builds the server, provider and gateway layers in the common API format."),
            ("Reviewer / explainer", 1, "1-2", "Checks the pictures and lessons are correct and plain."),
        ],
        "learn": [
            "What a model actually learns, and why the tokenizer changes cost, especially for Hindi.",
            "Why prefill is cheaper per token than decode, and why the KV cache grows with the conversation.",
            "What temperature and top-p really change.",
            "Why a base model cannot follow instructions until it is chat-tuned.",
            "Where guardrails belong: in the gateway owned by the user, not the provider.",
        ],
        "questions": [
            "How small can a model be and still teach every layer honestly?",
            "Should the tokenizer be learned only from practice data, or from your own corpus?",
            "What does batching gain in throughput, and what does it cost each request in waiting time?",
            "Which friction points in fine-tuning could become a reusable tool?",
        ],
        "repo": None,
        "repo_public": False,
        "links": [],
        "good_first": [
            "Write the table-driven round-trip test cases for the step 2 tokenizer.",
            "Draw the token-count comparison table: GPT-2 tokenizer versus ours on the same sentences.",
            "Write a load script that sends 1, 4 and 8 requests at once and records time to first token.",
        ],
    },

    # ------------------------------------------------------------------ 2
    {
        "id": "learn-langgraph",
        "title": "LearnLangGraph",
        "subject": "ai",
        "group": "learning",
        "status": "active",
        "started": "2026-09",
        "lead": LEAD,
        "one_liner": "A hands-on LangGraph course in three waves: graphs without an LLM, then agents, then production patterns.",
        "purpose": (
            "LearnLangGraph teaches the LangGraph library by doing, one small runnable lesson at a time. "
            "Wave 1 uses no language model at all, so state, nodes, routing and loops are learned on plain code. "
            "Wave 2 adds a free open-weight model, and the agent loop becomes just one more node. "
            "It is for engineers who want to build agents on a clear mental model rather than copy examples."
        ),
        "audience": "Python developers and data engineers starting with agent workflows.",
        "benefits": [
            ("Faster onboarding", "A new engineer can go from zero to a tool-using agent with memory in a few evenings."),
            ("Fewer fragile agents", "Learning routing and loops on deterministic code first makes later agent bugs easier to find."),
            ("Zero model spend while learning", "Lessons run on a free model tier, and tests use a scripted fake model with no network."),
            ("A reusable teaching asset", "Every lesson is a runnable file plus a test, so a team can use it as its own internal course."),
        ],
        "functional": [
            "Teach state, nodes, edges, conditional routing, reducers, parallel branches, loops and streaming with no LLM.",
            "Finish Wave 1 with a capstone graph that triages Spark job anti-patterns.",
            "Teach an LLM as a node, raw tool calling, a hand-built ReAct loop, the prebuilt agent, memory and structured-output routing.",
            "Finish Wave 2 with a capstone cost assistant that combines a guard, an agent, tools and memory.",
            "Plan Wave 3: human approval, time travel, subgraphs, map-reduce, supervisor multi-agent, durable storage and evals.",
            "Publish the whole course as one generated HTML page with diagrams, code, real output and exercises.",
        ],
        "nonfunctional": [
            "Every lesson has a table-driven test.",
            "Tests need no API key; a scripted fake model replaces the real one.",
            "Switching model provider is two settings, not a code change.",
            "Real model output is cached so the page can be rebuilt without calling the model.",
        ],
        "components": [
            ("Lesson files", "One runnable file per concept, with a docstring and 'try this' exercises."),
            ("Shared tools", "Sample Spark jobs and tools the agent lessons call."),
            ("Model adapter", "One place that picks the model and provider."),
            ("Scripted fake model", "Replays fixed answers so tests run offline."),
            ("Tests", "Table-driven checks for every lesson."),
            ("Page builder", "Turns lessons, diagrams and captured output into one HTML course page."),
        ],
        "flows": [
            ("Lesson files", "Shared tools", "call tools"),
            ("Lesson files", "Model adapter", "ask the model"),
            ("Tests", "Scripted fake model", "replay answers"),
            ("Tests", "Lesson files", "check behaviour"),
            ("Page builder", "Lesson files", "read code and output"),
        ],
        "bindings": {
            "Open stack": {
                "Lesson files": "Python 3.12 + LangGraph 1.x ✓",
                "Shared tools": "Plain Python ✓",
                "Model adapter": "OpenAI-compatible client on Groq free tier ✓",
                "Scripted fake model": "Custom LangChain chat model ✓",
                "Tests": "pytest, table-driven ✓",
                "Page builder": "Python script + HTML template ✓",
            },
            "Azure": {
                "Model adapter": "Azure OpenAI / Azure AI Foundry",
                "Lesson files": "Azure Container Apps for a hosted agent",
            },
            "AWS": {
                "Model adapter": "Amazon Bedrock",
                "Lesson files": "AWS Lambda or ECS for a hosted agent",
            },
        },
        "work": [
            ("Wave 1: basics without an LLM", [
                ("Lessons 01 to 07 with tests", "done", "M", "Python"),
                ("Spark triage capstone", "done", "S", "Python"),
            ]),
            ("Wave 2: agents", [
                ("Lessons 08 to 14 on a free model", "done", "M", "LLM agents"),
                ("Offline fake model and cached real output", "done", "S", "testing"),
                ("Single-page HTML course", "done", "S", "technical writing"),
            ]),
            ("Wave 3: production patterns", [
                ("Lesson 15: pause for human approval and resume", "todo", "S", "LangGraph"),
                ("Lesson 16: time travel and forking a run", "todo", "S", "LangGraph"),
                ("Lessons 17 to 18: subgraphs and map-reduce", "todo", "M", "LangGraph"),
                ("Lesson 19: supervisor with worker agents", "todo", "M", "multi-agent"),
                ("Lessons 20 to 22: durable storage, evals and capstone", "todo", "L", "LangGraph"),
            ]),
        ],
        "roles": [
            ("Lesson author", 1, "3-4", "Writes one Wave 3 lesson at a time with its test."),
            ("Tester / reviewer", 1, "1-2", "Runs every lesson fresh and reports where it confuses."),
        ],
        "learn": [
            "A graph is a function: state goes in, state comes out.",
            "Reducers decide how two updates to the same key are merged.",
            "An agent is a graph with a loop where one node calls a model.",
            "Checkpointers give memory, pause and resume.",
            "How to test agent code without calling a model.",
        ],
        "questions": [
            "When does a graph framework help, and when is a plain loop clearer?",
            "How do you stop an agent loop safely?",
            "Where should a human approval step go in a real workflow?",
        ],
        "repo": None,
        "repo_public": False,
        "links": [],
        "good_first": [
            "Write lesson 15: an agent proposes a fix and pauses for approve or reject.",
            "Add 'try this' answers to a Wave 2 lesson.",
            "Run the course on a fresh machine and fix any setup step that breaks.",
        ],
    },

    # ------------------------------------------------------------------ 3
    {
        "id": "dataeng-training",
        "title": "DataEngineering Training: Ecom Simple Data Platform",
        "subject": "data",
        "group": "learning",
        "status": "active",
        "started": "2026-07",
        "lead": LEAD,
        "one_liner": "Learn data engineering by designing real projects; project 1 is a small e-commerce lakehouse on Databricks.",
        "purpose": (
            "This training track teaches data engineering by designing real project architectures, not by memorising tools. "
            "Every project goes from requirements to a tool-free conceptual design, then to a physical design that names the technology. "
            "Project 1 builds a small e-commerce lakehouse: raw files become clean, historised tables, a star schema and dashboards. "
            "It is for friends and newcomers who want the thinking a working data engineer uses every day."
        ),
        "audience": "People new to data engineering, and analysts or developers moving into it.",
        "benefits": [
            ("Job-ready skills", "Learners practise the write patterns (append, overwrite, merge, history) that real pipelines use daily."),
            ("Lower cloud spend while learning", "Everything runs on a free serverless edition with small sample data and nothing left running."),
            ("Better design habits", "Separating what a system must do from how well it must do it makes designs easier to review and cost."),
            ("Fewer production surprises", "Thirteen war-story pages show common failures, their cause and their fix before they happen at work."),
        ],
        "functional": [
            "Read raw daily files without ever changing them.",
            "Build clean tables, one notebook per table, each with the right write pattern: append, overwrite, merge or full history.",
            "Add standard audit columns to every clean table.",
            "Build a star schema with a sales fact and customer, product, category and date dimensions.",
            "Build consumption views and one or two dashboards.",
            "Run the whole pipeline as one scheduled workflow, incrementally, using high-water marks.",
            "Record row counts and a run id per step in an audit table.",
        ],
        "nonfunctional": [
            "Cost: serverless compute and small data; nothing left running.",
            "Reliability: every notebook is safe to re-run without duplicates.",
            "Security: governed catalog with per-schema grants; no mounts and no account keys.",
            "Data quality: schema enforcement, null and duplicate checks, and exactly one current row per key in history tables.",
            "Maintainability: one notebook per table and a small config that drives table-specific behaviour.",
        ],
        "components": [
            ("Sample data generator", "Creates synthetic raw files, including a second customer load to exercise history."),
            ("Raw zone", "Keeps every file received, as-is, for audit and replay."),
            ("Raw ingest", "Loads only new files into raw tables, driven by metadata and a watermark."),
            ("Clean layer", "Cleans, conforms and historises each table with the right write pattern."),
            ("Business layer", "Star schema and marts such as daily sales and customer lifetime value."),
            ("Serving and dashboards", "Views and dashboards for analysts."),
            ("Orchestration and audit", "Runs the steps in order and logs every run."),
            ("Governance", "Catalogs, secures and separates dev, test and prod."),
        ],
        "flows": [
            ("Sample data generator", "Raw zone", "daily files"),
            ("Raw zone", "Raw ingest", "new files only"),
            ("Raw ingest", "Clean layer", "raw rows"),
            ("Clean layer", "Business layer", "clean, historised rows"),
            ("Business layer", "Serving and dashboards", "facts and marts"),
            ("Orchestration and audit", "Raw ingest", "run in order"),
            ("Governance", "Clean layer", "grants and lineage"),
        ],
        "bindings": {
            "Databricks": {
                "Sample data generator": "PySpark notebook ✓",
                "Raw zone": "Unity Catalog Volume with Parquet ✓",
                "Raw ingest": "PySpark notebook, metadata and watermark driven ✓",
                "Clean layer": "Delta tables with MERGE and SCD2 ✓",
                "Business layer": "Delta tables ✓",
                "Serving and dashboards": "Databricks SQL views and dashboards",
                "Orchestration and audit": "Databricks Workflows / Asset Bundle ✓",
                "Governance": "Unity Catalog ✓",
            },
            "Azure": {
                "Raw zone": "ADLS Gen2 + Unity Catalog external location",
                "Raw ingest": "Azure Data Factory + Azure Databricks",
                "Clean layer": "Azure Databricks + Delta Lake",
                "Business layer": "Azure Databricks + Delta Lake",
                "Serving and dashboards": "Azure SQL Database / Power BI",
                "Orchestration and audit": "Azure Data Factory",
                "Governance": "Unity Catalog",
            },
            "AWS": {
                "Raw zone": "Amazon S3",
                "Raw ingest": "AWS Glue",
                "Clean layer": "Databricks on AWS or Glue with Delta",
                "Business layer": "Databricks on AWS",
                "Serving and dashboards": "Amazon QuickSight",
                "Orchestration and audit": "Step Functions / MWAA",
                "Governance": "Unity Catalog or Lake Formation",
            },
            "Open stack": {
                "Raw zone": "MinIO or local disk with Parquet",
                "Clean layer": "Apache Spark + Delta Lake",
                "Business layer": "Apache Spark + Delta Lake",
                "Serving and dashboards": "Apache Superset",
                "Orchestration and audit": "Apache Airflow",
            },
        },
        "work": [
            ("Training scaffold", [
                ("Explainers for the eight core technologies", "done", "M", "technical writing"),
                ("Project template and live portal page", "done", "S", "documentation"),
                ("Diagram-first theory pages, including Delta internals", "done", "M", "data engineering"),
            ]),
            ("Project 1 design", [
                ("Architecture: conceptual and physical", "done", "S", "architecture"),
                ("Design: write pattern per table, audit columns, star schema", "done", "M", "data modelling"),
            ]),
            ("Project 1 build", [
                ("Setup, sample data and raw ingest notebooks", "done", "M", "PySpark"),
                ("Clean customers (history), orders, products and order items", "done", "M", "PySpark / Delta"),
                ("Daily sales and customer lifetime value marts", "done", "M", "Spark SQL"),
                ("Light data-quality notebook", "done", "S", "data quality"),
                ("Consumption layer of views and features", "todo", "M", "Spark SQL"),
                ("Two dashboards on the business layer", "todo", "S", "BI"),
            ]),
            ("Next projects", [
                ("Project 2 using Data Factory and Azure SQL Database", "todo", "L", "Azure data engineering"),
            ]),
        ],
        "roles": [
            ("Learner", 4, "3-5", "Builds the project notebooks and answers the level-up questions."),
            ("Mentor", 1, "2-3", "Reviews designs and code and adds new projects one at a time."),
            ("Contributor", 1, "1-2", "Writes new war-story pages or theory pages."),
        ],
        "learn": [
            "When to append, overwrite, merge or keep full history for a table.",
            "How to make an append load safe to re-run.",
            "How to join a fact to the right version of a historised dimension.",
            "Views versus materialised views: freshness against speed.",
            "Conceptual architecture first, tools second.",
        ],
        "questions": [
            "What breaks at ten times the data volume?",
            "Which dashboard tiles justify a materialised view?",
            "How would you replay one bad day without rebuilding everything?",
            "Where should data-quality checks stop the pipeline instead of just warning?",
        ],
        "repo": "https://github.com/basantchoudhary/DataEngineeringTraining",
        "repo_public": True,
        "links": [
            ("Training portal", "https://basantchoudhary.github.io/DataEngineeringTraining/"),
            ("Project 1 code", "https://github.com/basantchoudhary/ecomsimpledataplatformusingdatabricks"),
        ],
        "good_first": [
            "Build one consumption view on the daily sales mart.",
            "Build the first dashboard: KPI tiles, a line chart and a bar chart.",
            "Add a freshness check to the data-quality notebook.",
            "Write a war-story page about a pipeline failure you have seen.",
        ],
    },

    # ------------------------------------------------------------------ 4
    {
        "id": "spark-cost-agent",
        "title": "Spark Cost Agent",
        "subject": "ai",
        "group": "learning",
        "status": "active",
        "started": "2026-08",
        "lead": LEAD,
        "one_liner": "A Spark cost analyst agent built as a lab for agent tracing, evaluation and cost per successful task.",
        "purpose": (
            "Spark Cost Agent is a real agent that reads Delta transaction logs and Spark event logs and finds cost anti-patterns such as small files, skew and cartesian joins. "
            "The agent is not the point: everything around it is, meaning traces, metrics, evaluations, guardrails and a cost model. "
            "It is for engineers who need to run agents in production and prove they work and what they cost. "
            "It follows a ten-stage plan and builds the observability by hand so every signal is understood."
        ),
        "audience": "AI and platform engineers responsible for running, evaluating and costing agents.",
        "benefits": [
            ("Know what each answer costs", "Cost per successful task shows whether an agent is worth its spend, not just total tokens."),
            ("Catch quality drops early", "Online evaluation, guardrails and alerts flag bad answers before users report them."),
            ("No vendor lock-in", "All telemetry goes through one neutral collector, so backends can be added or swapped without code changes."),
            ("Safer releases", "An offline evaluation gate with a pass-rate threshold stops a worse version from merging."),
        ],
        "functional": [
            "Answer questions about Spark and Delta cost from real logs, using four domain tools.",
            "Emit a trace for every task, model call and tool call, using the standard generative-AI attribute names.",
            "Price real token counts against a reference rate card, so cost stays meaningful on a free tier.",
            "Capture user feedback and cheap deterministic metrics on every run.",
            "Build a labelled evaluation dataset from the artifacts and from past incidents.",
            "Run online checks: guardrails, a sampled model judge, injection detection and quality alerts.",
            "Report coverage against an open AI assurance catalog.",
        ],
        "nonfunctional": [
            "No agent framework: the loop is hand-written so every span is owned code.",
            "Works without an API key for everything except asking the agent.",
            "Offline test suite runs with no network.",
            "Light enough for an 8 GB laptop; hosted free tiers used where local tools are too heavy.",
            "Model provider switch is a configuration change, never a code change.",
        ],
        "components": [
            ("Domain tools", "Read Delta logs and Spark event logs and return findings."),
            ("Agent loop", "Calls the model, runs tools and assembles the answer."),
            ("Telemetry emitter", "Writes spans and metrics with standard names."),
            ("Telemetry seam", "Receives all telemetry, redacts, samples and fans out to backends."),
            ("Trace and metric backends", "Store and display traces, metrics and scores."),
            ("Cost model", "Prices token usage and computes cost per successful task."),
            ("Evaluation suite", "Offline datasets, pass-rate gate, pairwise preference and judge checks."),
            ("Online guard", "Guardrails, sampled judging, feedback and alerts on live runs."),
        ],
        "flows": [
            ("Agent loop", "Domain tools", "tool call"),
            ("Agent loop", "Telemetry emitter", "task, model and tool events"),
            ("Telemetry emitter", "Telemetry seam", "spans and metrics"),
            ("Telemetry seam", "Trace and metric backends", "redacted, sampled data"),
            ("Cost model", "Trace and metric backends", "shadow cost"),
            ("Evaluation suite", "Agent loop", "test questions"),
            ("Online guard", "Agent loop", "checks on live answers"),
        ],
        "bindings": {
            "Open stack": {
                "Domain tools": "Python over Delta and Spark JSON logs ✓",
                "Agent loop": "Hand-written loop, OpenAI-compatible client on Groq ✓",
                "Telemetry emitter": "Manual OpenTelemetry, GenAI conventions ✓",
                "Telemetry seam": "OpenTelemetry Collector ✓",
                "Trace and metric backends": "Arize Phoenix + Prometheus, Langfuse and LangSmith free tiers ✓",
                "Cost model": "Python rate cards ✓",
                "Evaluation suite": "pytest-style runner + promptfoo ✓",
                "Online guard": "Python guardrails and sampled judge ✓",
            },
            "Azure": {
                "Agent loop": "Azure AI Foundry models",
                "Telemetry seam": "OpenTelemetry Collector on Azure Container Apps",
                "Trace and metric backends": "Azure Monitor / Application Insights",
                "Evaluation suite": "Azure AI Foundry evaluations",
                "Online guard": "Azure AI Content Safety",
            },
            "AWS": {
                "Agent loop": "Amazon Bedrock models",
                "Telemetry seam": "AWS Distro for OpenTelemetry",
                "Trace and metric backends": "AWS X-Ray / CloudWatch",
                "Evaluation suite": "Bedrock model evaluation",
                "Online guard": "Bedrock Guardrails",
            },
        },
        "work": [
            ("Tracing and the seam (stages 1 to 2)", [
                ("First real trace on screen", "done", "S", "OpenTelemetry"),
                ("Collector as the neutral seam with redaction and sampling", "done", "M", "OpenTelemetry"),
                ("Add a hosted system of record as a second exporter", "doing", "S", "observability"),
            ]),
            ("Cost and metrics (stages 4 to 5)", [
                ("Shadow pricing and cost per successful task", "done", "M", "FinOps"),
                ("Deterministic metrics and feedback capture", "done", "S", "Python"),
            ]),
            ("Evaluation (stages 6 to 9)", [
                ("Labelled dataset from artifacts and incidents", "done", "M", "evaluation"),
                ("Online guardrails, sampled judge and alerts", "done", "M", "evaluation"),
                ("Offline evaluation as a merge gate in CI", "doing", "M", "CI"),
                ("Validate the judge against human labels", "doing", "M", "statistics"),
            ]),
            ("Optimise (stage 10)", [
                ("Caching, model routing and context trimming against cost per success", "todo", "L", "LLM engineering"),
            ]),
        ],
        "roles": [
            ("AI engineer", 1, "4-6", "Builds the next stage and keeps the plan honest."),
            ("Observability engineer", 1, "2-3", "Owns the collector, backends and alerts."),
            ("Evaluator", 1, "1-2", "Labels answers by hand so the judge can be checked."),
        ],
        "learn": [
            "How to instrument an agent by hand with standard trace names.",
            "Why a collector between app and backends keeps you vendor-neutral.",
            "How to compute cost per successful task, not just cost per call.",
            "Offline versus online evaluation, and when a model judge can be trusted.",
            "Why counting only added files in a Delta log gives the wrong answer.",
        ],
        "questions": [
            "How much agreement with humans does a judge need before you trust it?",
            "What sampling rate catches quality drops without paying for every check?",
            "Which optimisation cuts cost per success most: caching, routing or trimming?",
        ],
        "repo": None,
        "repo_public": False,
        "links": [],
        "good_first": [
            "Label twenty agent answers by hand for the judge check.",
            "Add one new test question to the evaluation dataset.",
            "Write an alert rule for a rising tool-error rate.",
        ],
    },

    # ------------------------------------------------------------------ 5
    {
        "id": "myclaudecode",
        "title": "MyClaudeCode",
        "subject": "ai",
        "group": "learning",
        "status": "starting",
        "started": "2026-09",
        "lead": LEAD,
        "one_liner": "A mini coding agent used as an instrument to put numbers on unmeasured coding-agent advice.",
        "purpose": (
            "MyClaudeCode builds a small coding agent to understand how tools like Claude Code work from the inside. "
            "Official guidance already explains how to set these tools up, but it does not measure the mechanisms it describes. "
            "This project runs experiments to find the numbers: when instruction files get too big, when subagents pay off, what compaction forgets, and where answer quality starts to fall. "
            "It is for engineers using coding agents on large codebases who want evidence, not folklore."
        ),
        "audience": "Engineers and team leads who use coding agents on large codebases.",
        "benefits": [
            ("Lower token spend", "Knowing which always-loaded layer dominates the baseline lets a team cut it first."),
            ("Fewer lost instructions", "A catalogue of what compaction forgets tells teams what to back up or restate."),
            ("Evidence-based settings", "Thresholds for when to clear or compact come from measurement instead of guesses."),
            ("Reuse before building", "A reuse ledger shows which existing open-source tools already cover each need."),
        ],
        "functional": [
            "Provide a small coding agent with a trace from the first version.",
            "Split the always-loaded context baseline by layer.",
            "Force compaction on demand and record what kind of information it removes.",
            "Measure the break-even point where a subagent saves more than it costs.",
            "Measure how many skills can be loaded before selection breaks.",
            "Package a context-governance kit: status line, warning hook and pre-compaction backup.",
        ],
        "nonfunctional": [
            "Every published claim is backed by a number or a reproduced failure; unproven claims are cut.",
            "Measure context mechanics, which do not depend on the model; label anything model-dependent.",
            "Every experiment runs from a fresh clone by a stranger.",
            "Free open-weight models by default.",
        ],
        "components": [
            ("Agent loop", "Calls the model, runs tools and records every step."),
            ("Tools and editor", "Read, search and edit files under simple invariants."),
            ("Context assembler", "Builds what the model sees, in budgeted stages."),
            ("Transcript probes", "Split the baseline and examine what compaction removed."),
            ("Experiment runner", "Repeats each experiment and records the numbers."),
            ("Governance kit", "Status line, warning hook and backup for real coding agents."),
        ],
        "flows": [
            ("Agent loop", "Tools and editor", "tool calls"),
            ("Context assembler", "Agent loop", "budgeted context"),
            ("Experiment runner", "Agent loop", "forced scenarios"),
            ("Transcript probes", "Experiment runner", "measurements"),
            ("Experiment runner", "Governance kit", "evidence-based thresholds"),
        ],
        "bindings": {
            "Open stack": {
                "Agent loop": "Hand-written Python, OpenAI-compatible client on Groq",
                "Tools and editor": "Python",
                "Context assembler": "Python",
                "Transcript probes": "Python over local transcripts, plus ccusage and cc-analyzer",
                "Experiment runner": "Python scripts",
                "Governance kit": "Claude Code status line and hooks",
            },
            "Azure": {"Agent loop": "Azure AI Foundry models"},
            "AWS": {"Agent loop": "Amazon Bedrock models"},
        },
        "work": [
            ("Reposition and design", [
                ("Check whether the planned guide already exists", "done", "S", "research"),
                ("Decisions, glossary, reuse ledger and experiment list", "done", "M", "architecture"),
                ("Setup advisor and droppable skill spec", "done", "S", "technical writing"),
            ]),
            ("Measure the baseline", [
                ("Run existing usage tools over past sessions and read off baselines", "todo", "S", "analysis"),
                ("Baseline splitter and compaction forensics probes", "todo", "M", "Python"),
            ]),
            ("Mini agent", [
                ("Loop with a trace", "todo", "M", "Python"),
                ("Tools, invariants and a deliberately naive editor", "todo", "M", "Python"),
                ("Context assembly calibrated against the real tool", "todo", "M", "LLM engineering"),
            ]),
            ("Experiments and kit", [
                ("Compaction taxonomy and subagent break-even", "todo", "L", "experiment design"),
                ("Quality degradation threshold: cliff or slide", "todo", "L", "experiment design"),
            ]),
        ],
        "roles": [
            ("Agent builder", 1, "3-5", "Builds the mini agent and probes."),
            ("Experiment designer", 1, "2-3", "Designs repeatable experiments and checks the numbers."),
        ],
        "learn": [
            "Why most coding-agent features exist because the context window is finite.",
            "How compaction works and what it can lose.",
            "When delegating to a subagent saves tokens and when it wastes them.",
            "How to check whether something exists before building it.",
        ],
        "questions": [
            "At what size does an instruction file start losing compliance?",
            "Is quality loss near a full context a cliff or a slow slide?",
            "Can the key experiments be automated without paid model calls?",
        ],
        "repo": None,
        "repo_public": False,
        "links": [],
        "good_first": [
            "Run the existing usage tools over your own sessions and share the baseline split.",
            "Write the trace format for the mini agent's first version.",
            "Add one checked entry to the reuse ledger.",
        ],
    },

    # ------------------------------------------------------------------ 6
    {
        "id": "ontology-kg",
        "title": "Ontology and Knowledge Graph",
        "subject": "data",
        "group": "learning",
        "status": "active",
        "started": "2026-09",
        "lead": LEAD,
        "one_liner": "Build an ontology and knowledge graph from scratch over code, data, specs and AI assets.",
        "purpose": (
            "This project builds an ontology and a knowledge graph by hand, over a codebase and the data platform it touches. "
            "It parses Python, PySpark, SQL, databases and spec documents into one shared vocabulary, then reasons over it and checks rules. "
            "It is for engineers who want to understand how such a graph is designed, rather than learn one vendor's model. "
            "The payoff is impact analysis in one query: change a function and see every table, screen and team affected."
        ),
        "audience": "Data engineers, platform engineers and architects interested in lineage, metadata and agent context.",
        "benefits": [
            ("Safer changes", "Impact analysis shows every downstream table, screen and team before a change ships."),
            ("Find hidden relationships", "Value-overlap mining finds joins nobody declared, which documentation misses."),
            ("Lower compliance risk", "Rules flag personal data with no owner or unmasked samples."),
            ("Better agent answers", "A graph gives a coding agent precise context instead of reading the whole repository."),
        ],
        "functional": [
            "Parse Python and PySpark into functions, calls and table reads and writes.",
            "Parse SQL into table and column lineage, with the transforming expression.",
            "Reflect database schemas and profile columns with personal data masked.",
            "Find relationships from declared keys, observed joins and value overlap.",
            "Parse requirements, acceptance criteria, decision records and glossary terms from markdown.",
            "Reason transitive lineage and personal-data propagation, and validate rules.",
            "Answer a written list of competency questions with queries.",
        ],
        "nonfunctional": [
            "Pure Python with no containers, servers or paid APIs.",
            "Extractors are disposable; the vocabulary is durable and reviewed like code.",
            "Every class and property exists because a competency question needs it.",
            "One build command runs the whole demo end to end.",
        ],
        "components": [
            ("Sources", "Sample repository, sample warehouse and spec documents."),
            ("Extractors", "Turn code, SQL, databases and specs into graph statements."),
            ("Vocabulary", "One core model plus code, data, AI and spec lenses."),
            ("Graph store", "Holds all statements with provenance."),
            ("Reasoner", "Adds inferred edges such as transitive lineage."),
            ("Rule checker", "Validates what must be true, such as owned personal data."),
            ("Question layer", "Answers competency questions, later as task-shaped agent tools."),
        ],
        "flows": [
            ("Sources", "Extractors", "files and schemas"),
            ("Extractors", "Graph store", "statements"),
            ("Vocabulary", "Graph store", "shared terms"),
            ("Graph store", "Reasoner", "facts"),
            ("Reasoner", "Rule checker", "inferred facts"),
            ("Graph store", "Question layer", "queries"),
        ],
        "bindings": {
            "Open stack": {
                "Sources": "SQLite stand-in warehouse + sample repo ✓",
                "Extractors": "Python ast, sqlglot, SQLAlchemy, markdown parsing ✓",
                "Vocabulary": "RDF / OWL in Turtle files ✓",
                "Graph store": "rdflib ✓",
                "Reasoner": "owlrl ✓",
                "Rule checker": "pyshacl ✓",
                "Question layer": "SPARQL ✓; MCP tools planned",
            },
            "Azure": {
                "Graph store": "Azure Cosmos DB for Apache Gremlin",
                "Sources": "Microsoft Purview scans",
            },
            "AWS": {
                "Graph store": "Amazon Neptune",
                "Sources": "AWS Glue Data Catalog",
            },
            "Databricks": {
                "Sources": "Unity Catalog lineage system tables",
            },
        },
        "work": [
            ("Phase 1: build from scratch", [
                ("Core ontology and four lenses", "done", "M", "ontology design"),
                ("Python, SQL, database and spec extractors", "done", "L", "Python"),
                ("Reasoning, rule checks and question queries", "done", "M", "RDF / SPARQL"),
                ("Lessons 00, 05, 10 and 11", "done", "M", "technical writing"),
                ("TypeScript and web-app extractor", "todo", "M", "TypeScript parsing"),
                ("Git history extractor for code churn", "todo", "S", "Python"),
                ("Incremental re-extraction with named graphs", "todo", "M", "RDF"),
            ]),
            ("Phase 2: compare with existing tools", [
                ("Point an open metadata platform at the same repo and compare models", "todo", "L", "data governance"),
            ]),
            ("Phase 3: agent interface", [
                ("Expose task-shaped tools over the tool protocol", "todo", "M", "agents"),
            ]),
        ],
        "roles": [
            ("Ontology designer", 1, "2-3", "Owns the vocabulary and competency questions."),
            ("Extractor developer", 1, "2-4", "Writes new extractors for more languages and sources."),
            ("Lesson writer", 1, "1-2", "Turns planned lessons into plain prose."),
        ],
        "learn": [
            "What an ontology is, and how it differs from a knowledge graph.",
            "How to decide between a class, a property and an instance.",
            "Why PySpark defeats simple static analysis and how to track it anyway.",
            "Reasoning versus validation, and the open-world assumption.",
            "How to expose a graph to an agent as tools, not a raw query endpoint.",
        ],
        "questions": [
            "Which questions justify a graph over a plain catalog?",
            "When should you stop materialising inferred edges?",
            "How does a hand-made model compare with an off-the-shelf metadata platform?",
        ],
        "repo": None,
        "repo_public": False,
        "links": [],
        "good_first": [
            "Write one planned lesson, such as the RDF crash course.",
            "Add a competency question and the query that answers it.",
            "Write the git history extractor for code churn.",
        ],
    },

    # ------------------------------------------------------------------ 7
    {
        "id": "asksherlock",
        "title": "AskSherlock",
        "subject": "cost",
        "group": "learning",
        "status": "starting",
        "started": "2026-09",
        "lead": LEAD,
        "one_liner": "An open-source Genie-style chat over a ClickHouse cost store, where the model never writes SQL.",
        "purpose": (
            "AskSherlock lets a person ask a cost question in plain English and get the number, a chart and the SQL that produced it. "
            "It works over a ClickHouse cost store, as an open-source alternative to Databricks AI/BI Genie. "
            "The model only turns the question into a small validated intent from a fixed vocabulary; a semantic layer writes the SQL. "
            "It runs on a two-week time box, and the public write-up of what worked is the main deliverable."
        ),
        "audience": "Data and platform teams who want trustworthy natural-language questions over their own warehouse.",
        "benefits": [
            ("Answers match the dashboard", "Chat and dashboards share one set of metric definitions, so they cannot disagree."),
            ("Fewer confident wrong answers", "The model cannot invent a metric or a join, which removes a whole class of errors."),
            ("Auditable results", "The SQL is shown with every answer, so anyone can check it."),
            ("Low running cost", "Uses open-source parts and a free open-weight model on data already in the warehouse."),
        ],
        "functional": [
            "Accept a question in plain English.",
            "Turn it into an intent object naming measures, dimensions, filters and time grain from a closed vocabulary.",
            "Validate the intent against a schema and refuse anything invalid before touching the database.",
            "Resolve user words to real values using generated value dictionaries and synonyms.",
            "Compile the intent into SQL through a semantic layer and run it.",
            "Return the number, a chart chosen from the data's shape, and the SQL.",
        ],
        "nonfunctional": [
            "The model never writes SQL.",
            "An evaluation suite of about 120 cases runs in CI and reports intent and execution accuracy.",
            "Stop rule: below 85% accuracy with clean refusals at the checkpoint, stop building and write up why.",
            "Light on a laptop: the database is capped in memory and only runs while working.",
        ],
        "components": [
            ("Question input", "Takes the user's question."),
            ("Intent generator", "Maps the question to a structured intent using a small model."),
            ("Intent validator", "Checks the intent against the schema and the vocabulary."),
            ("Value resolver", "Maps user words to real dimension values."),
            ("Semantic layer", "Holds metric, dimension and join definitions and compiles SQL."),
            ("Cost store", "The warehouse that runs the query."),
            ("Answer view", "Shows the number, the chart and the SQL."),
            ("Evaluation suite", "Gold questions with expected intents and answers."),
        ],
        "flows": [
            ("Question input", "Intent generator", "question"),
            ("Intent generator", "Intent validator", "intent object"),
            ("Intent validator", "Value resolver", "valid intent"),
            ("Value resolver", "Semantic layer", "resolved intent"),
            ("Semantic layer", "Cost store", "compiled SQL"),
            ("Cost store", "Answer view", "result rows"),
            ("Evaluation suite", "Intent generator", "gold questions"),
        ],
        "bindings": {
            "Open stack": {
                "Question input": "Web panel in an existing Next.js app",
                "Intent generator": "Open-weight model on Groq",
                "Intent validator": "JSON Schema",
                "Value resolver": "Generated YAML value dictionaries",
                "Semantic layer": "Cube Core or a small hand-written compiler, authored in OSI shape",
                "Cost store": "ClickHouse",
                "Answer view": "Next.js charts",
                "Evaluation suite": "Table-driven tests + Langfuse",
            },
            "Databricks": {
                "Semantic layer": "Unity Catalog Metric Views",
                "Answer view": "AI/BI Genie (the reference being replaced)",
            },
            "Azure": {
                "Intent generator": "Azure AI Foundry models",
                "Cost store": "ClickHouse on an Azure VM",
            },
            "AWS": {
                "Intent generator": "Amazon Bedrock models",
                "Cost store": "ClickHouse on EC2",
            },
        },
        "work": [
            ("Research and decisions", [
                ("Open-source landscape and architecture", "done", "M", "research"),
                ("Six decision records: intent not SQL, no graph in v1, value dictionaries, model format", "done", "M", "architecture"),
            ]),
            ("Phase 0 to 1: questions and semantic layer", [
                ("Seed gold question set", "doing", "S", "analytics"),
                ("Model measures and dimensions over the main cost table", "todo", "M", "semantic modelling"),
                ("One-day spike: semantic engine versus hand-written compiler", "todo", "M", "SQL"),
                ("Value dictionary generator", "todo", "S", "Python / SQL"),
            ]),
            ("Phase 2 to 3: intents and evaluation", [
                ("Intent schema, validator, model call and refusal path", "todo", "M", "LLM engineering"),
                ("Evaluation harness of about 120 cases in CI", "todo", "M", "evaluation"),
            ]),
            ("Phase 4 to 5: UI and write-up", [
                ("Answer panel with chart and SQL", "todo", "M", "frontend"),
                ("Public write-up of results", "todo", "M", "technical writing"),
            ]),
        ],
        "roles": [
            ("Semantic modeller", 1, "3-4", "Defines metrics, dimensions and joins."),
            ("LLM engineer", 1, "2-3", "Builds intent generation, validation and refusal."),
            ("Evaluator", 1, "1-2", "Writes gold questions and checks answers."),
        ],
        "learn": [
            "Why letting a model write SQL fails on real enterprise schemas.",
            "How a semantic layer turns a fuzzy question into correct SQL by construction.",
            "How value dictionaries stop silent empty results.",
            "How to set a stop rule before you start building.",
        ],
        "questions": [
            "Can a semantic engine handle this warehouse's table engine cleanly, or is a small compiler simpler?",
            "What accuracy is good enough to ship a chat answer?",
            "Which questions should the system refuse?",
        ],
        "repo": None,
        "repo_public": False,
        "links": [],
        "good_first": [
            "Write ten gold questions with their expected intent objects.",
            "Draft the JSON Schema for the intent object.",
            "Write the value dictionary generator for one dimension.",
        ],
    },

    # ------------------------------------------------------------------ 8
    {
        "id": "conversation-ui-on-data",
        "title": "Conversation UI on Data",
        "subject": "data",
        "group": "learning",
        "status": "active",
        "started": "2026-09",
        "lead": LEAD,
        "one_liner": "A specification for chat-with-your-data where the model picks certified metrics and never writes SQL.",
        "purpose": (
            "This is a specification, not an implementation: the right architecture for asking questions of data in plain English. "
            "It covers two settings, data governed in Unity Catalog on Databricks, and data in PostgreSQL or ClickHouse on a virtual machine. "
            "Its core rule is that the model selects a certified metric and dimensions, and a deterministic engine writes the query. "
            "It is for teams planning a conversational analytics product who want answers that match their dashboards."
        ),
        "audience": "Data architects, analytics engineers and product teams planning natural-language analytics.",
        "benefits": [
            ("Trustworthy numbers", "Chat and dashboards read the same semantic layer, so they always give the same answer."),
            ("Less rework", "Writing the metric contract first stops gold tables being built in the wrong shape."),
            ("Clear tool choice", "The spec explains which semantic layer fits each setting and why."),
            ("Lower risk at launch", "Shipping dashboards before chat exposes definition bugs to a forgiving audience first."),
        ],
        "functional": [
            "Define what a right answer means in testable terms.",
            "Give a layered reference architecture from raw data to chat.",
            "Correct four common medallion assumptions, such as keeping gold atomic rather than aggregated.",
            "List what a semantic model must declare: grain, measures, dimensions, join paths, synonyms and owners.",
            "Map the architecture to each track's technology and compare semantic layer options.",
            "Set the order of work, from metric contract to golden questions to dashboards to chat.",
        ],
        "nonfunctional": [
            "No code is generated in this repository by design.",
            "Every claim about accuracy cites a public benchmark or source.",
            "Answers must be fast and cheap enough to ask a hundred times a day.",
            "Governance: access rules apply the same way in chat and dashboards.",
        ],
        "components": [
            ("Clean data layer", "Conformed, tested data from the source systems."),
            ("Atomic gold model", "Star-schema facts at the finest grain any metric needs."),
            ("Semantic layer", "Certified metrics, dimensions, joins and synonyms."),
            ("Pre-aggregation cache", "Speeds up slow queries below the semantic layer."),
            ("Dashboards", "First consumer of the semantic layer."),
            ("Conversation UI", "Maps questions to metrics and shows answers with provenance."),
            ("Feedback loop", "Turns refusals and failures into backlog."),
        ],
        "flows": [
            ("Clean data layer", "Atomic gold model", "conformed rows"),
            ("Atomic gold model", "Semantic layer", "facts and dimensions"),
            ("Pre-aggregation cache", "Semantic layer", "fast results"),
            ("Semantic layer", "Dashboards", "certified metrics"),
            ("Semantic layer", "Conversation UI", "compiled queries"),
            ("Conversation UI", "Feedback loop", "refusals and failures"),
        ],
        "bindings": {
            "Databricks": {
                "Clean data layer": "Delta tables in Unity Catalog",
                "Atomic gold model": "Delta star schema in Unity Catalog",
                "Semantic layer": "Unity Catalog Metric Views",
                "Dashboards": "AI/BI dashboards",
                "Conversation UI": "AI/BI Genie",
            },
            "Open stack": {
                "Clean data layer": "dbt Core on PostgreSQL or ClickHouse",
                "Atomic gold model": "dbt Core star schema",
                "Semantic layer": "Cube Core",
                "Pre-aggregation cache": "Cube pre-aggregations",
                "Dashboards": "Apache Superset",
                "Conversation UI": "Open-weight model calling Cube over MCP",
            },
            "Azure": {
                "Atomic gold model": "Azure Databricks or Microsoft Fabric",
                "Semantic layer": "Power BI semantic model",
                "Conversation UI": "Fabric data agent",
            },
            "AWS": {
                "Atomic gold model": "Amazon Redshift",
                "Dashboards": "Amazon QuickSight",
                "Conversation UI": "Amazon Q in QuickSight",
            },
        },
        "work": [
            ("Specification", [
                ("Requirements in testable terms", "done", "M", "requirements"),
                ("Reference architecture and four corrections", "done", "M", "architecture"),
                ("Databricks track and self-hosted track", "done", "M", "data platforms"),
                ("Semantic layer options compared", "done", "M", "analytics engineering"),
                ("Decisions, open questions and risks", "done", "S", "architecture"),
            ]),
            ("Prove it on real data", [
                ("Twenty real questions as metric, dimensions and grain", "todo", "M", "analytics"),
                ("Golden question set with human-checked answers", "todo", "M", "evaluation"),
                ("Apply the spec in a build (see AskSherlock)", "doing", "L", "data engineering"),
            ]),
        ],
        "roles": [
            ("Data architect", 1, "2-3", "Owns the spec and its decisions."),
            ("Analytics engineer", 1, "2-3", "Tests the spec against a real model and questions."),
            ("Reviewer", 1, "1", "Challenges claims and checks sources."),
        ],
        "learn": [
            "Why medallion layers and dimensional modelling are different axes.",
            "Why gold should be atomic and aggregates are a cache.",
            "The difference between a semantic compiler and a semantic runtime.",
            "Why dashboards should ship before chat.",
        ],
        "questions": [
            "How do you handle a question no certified metric covers?",
            "Who owns each metric definition as it drifts?",
            "When is a pre-aggregation worth its freshness cost?",
        ],
        "repo": None,
        "repo_public": False,
        "links": [],
        "good_first": [
            "Write twenty real business questions as metric, dimensions and grain.",
            "Review one track document and list any claim without a source.",
        ],
    },

    # ------------------------------------------------------------------ 9
    {
        "id": "llm-cost-explainer",
        "title": "LLM Cost Explainer",
        "subject": "cost",
        "group": "learning",
        "status": "active",
        "started": "2026-10",
        "lead": LEAD,
        "one_liner": "Explains why LLM spend changed and which mistakes cost money, from a provider usage export alone.",
        "purpose": (
            "LLM Cost Explainer reads the usage export from an LLM provider and explains in plain words why spend went up or down. "
            "It splits the change into volume, model mix, request size, caching and price, then drills down to the model, key or project behind it. "
            "Rules then name common costly mistakes, such as caching turned off or bulk work on the real-time API, with an estimated saving. "
            "It is for teams building on LLMs who see a bill change and cannot tell why; it needs no SDK and never reads prompt text."
        ),
        "audience": "Engineering and finance teams running applications on hosted LLM APIs.",
        "benefits": [
            ("Find wasted spend", "Rules point to fixable mistakes and estimate what each fix would save."),
            ("Faster answers on bill changes", "A team gets the cause of a cost jump in minutes instead of a day of spreadsheet work."),
            ("No privacy risk", "Only usage numbers are read; prompt text is never needed."),
            ("Numbers you can check", "No model computes a number; every figure comes from tested arithmetic."),
        ],
        "functional": [
            "Import usage pages from the OpenAI and Anthropic admin usage APIs into one usage table.",
            "Price tokens from a pinned, dated public price map, never from the source's own cost field.",
            "Compare a day against a baseline, such as the median of the last four same weekdays.",
            "Split the change five ways: volume, mix, size, cache and tier, and price.",
            "Drill down to the model, key, project or tier that explains the change.",
            "Flag unusual days and apply six cost rules with a savings estimate each.",
            "Write the explanation as text and as an HTML report.",
        ],
        "nonfunctional": [
            "No prompt text is ever read or stored.",
            "Fields that cannot be mapped are listed under data quality, never dropped silently.",
            "Each savings estimate prints the assumption behind it.",
            "Runs locally with one command; includes synthetic scenarios with known causes for testing.",
        ],
        "components": [
            ("Importer", "Turns provider usage pages into one usage table."),
            ("Price book", "Prices tokens from a pinned public price list."),
            ("Change splitter", "Compares with a baseline and splits the change by cause."),
            ("Drill-down", "Finds which model, key or project explains the change."),
            ("Trend check", "Flags unusual days against the same weekday."),
            ("Rule engine", "Detects costly patterns and estimates savings."),
            ("Explainer", "Writes the text and HTML report."),
        ],
        "flows": [
            ("Importer", "Price book", "usage buckets"),
            ("Price book", "Change splitter", "priced usage"),
            ("Change splitter", "Drill-down", "change by cause"),
            ("Price book", "Trend check", "daily cost"),
            ("Price book", "Rule engine", "priced usage"),
            ("Drill-down", "Explainer", "where"),
            ("Rule engine", "Explainer", "why and savings"),
        ],
        "bindings": {
            "Open stack": {
                "Importer": "Python 3.12 ✓",
                "Price book": "LiteLLM price map + DuckDB ✓",
                "Change splitter": "Python, LMDI decomposition ✓",
                "Drill-down": "Python, Adtributor method ✓",
                "Trend check": "Python, robust z-score ✓",
                "Rule engine": "YAML rule specs + SQL on DuckDB ✓",
                "Explainer": "Text templates + HTML ✓",
            },
            "AWS": {
                "Importer": "AWS Lambda behind an upload page",
                "Price book": "Amazon S3 + DuckDB",
                "Explainer": "Static report on Amazon S3",
            },
            "Azure": {
                "Importer": "Azure Functions behind an upload page",
                "Price book": "Azure Blob Storage + DuckDB",
                "Explainer": "Static report on Azure Storage",
            },
        },
        "work": [
            ("Design", [
                ("Data model, cost equation and rule catalogue", "done", "L", "FinOps"),
                ("Ingestion, normalisation, analysis and delivery design", "done", "L", "architecture"),
            ]),
            ("v0: export upload", [
                ("Importers for two providers", "done", "M", "Python"),
                ("Pricing, five-way split, drill-down and trend check", "done", "M", "analytics"),
                ("Six rules with savings estimates", "done", "M", "SQL"),
                ("Text and HTML report, synthetic scenarios and tests", "done", "M", "Python"),
            ]),
            ("Real data", [
                ("Run on a real export and fix the field mapping", "todo", "S", "data engineering"),
                ("Fetch command to pull usage pages with an admin key", "todo", "S", "Python / APIs"),
                ("Reconcile to the providers' cost endpoints: billed versus list", "todo", "M", "FinOps"),
            ]),
            ("More rules and delivery", [
                ("Add rules from the remaining catalogue that the export can support", "todo", "M", "SQL"),
                ("Upload page around the analysis", "todo", "M", "web"),
            ]),
        ],
        "roles": [
            ("Data / FinOps engineer", 1, "3-4", "Adds rules and reconciles list price to the bill."),
            ("Backend engineer", 1, "2-3", "Builds the fetch command and the upload page."),
            ("Tester with real data", 1, "1", "Runs it on a real export and reports mapping gaps."),
        ],
        "learn": [
            "How to split a cost change into volume, mix, size, cache and price.",
            "How to find which slice of the data explains a change.",
            "What drives LLM spend: model choice, caching, batch versus real-time, service tier.",
            "Why list price and the bill differ.",
        ],
        "questions": [
            "How close is list-price cost to the real bill for a typical team?",
            "Which costly patterns can be seen from an export alone, and which need live traces?",
            "How should overlapping findings be counted so savings are not double-counted?",
        ],
        "repo": None,
        "repo_public": False,
        "links": [],
        "good_first": [
            "Add a new synthetic scenario with a known cause and a test for it.",
            "Implement one more rule from the catalogue that needs only export data.",
            "Write the fetch command for one provider.",
        ],
    },
]
