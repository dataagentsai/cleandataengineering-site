"""Project detail data, group "open": projects open for someone to lead or join.

Public page data. No client names, family details, funding or commercial strategy.
Not-started projects are written as proposals ("we would...") with every work item "todo".
"""

PROJECTS = [
    # ------------------------------------------------------------------ 1
    {
        "id": "data-eng-specs",
        "title": "Clean Data Engineering specs",
        "subject": "data",
        "group": "open",
        "status": "not-started",
        "started": "",
        "lead": "Open — looking for a lead",
        "one_liner": "Two open catalogs for data platforms: what parts must exist, and what must be true of the data.",
        "purpose": (
            "Every data team rebuilds the same platform from scratch and argues about the same gaps. "
            "We would write two neutral catalogs that any team can check itself against: a capability catalog "
            "that lists the parts a data platform must have, and an assurance catalog that lists what must be true "
            "of its data, each with a way to check it. "
            "Both would follow one path, from source systems through ingestion, bronze, silver and gold layers, "
            "a semantic model and consumption objects, to dashboards and conversational analytics. "
            "They would reuse existing open standards for data contracts and lineage rather than invent new ones."
        ),
        "audience": "Data engineers, data platform architects, analytics leads and auditors who need a shared checklist.",
        "benefits": [
            ("A shared checklist", "Teams can see in one place what their platform is missing before it bites them."),
            ("Faster reviews", "Architecture and audit reviews start from a standard list instead of a blank page."),
            ("Platform-neutral", "The same catalog applies on Databricks, Microsoft Fabric, AWS, GCP or an open stack."),
            ("Built on standards", "It points to existing data-contract and lineage standards, so teams adopt rather than rewrite."),
            ("Testable promises", "Each 'must be true' item comes with a check, so quality claims can be shown, not just stated."),
        ],
        "functional": [
            "List each platform capability (what must exist) with a plain description and what breaks without it.",
            "List each data obligation (what must be true) with how it is checked and what evidence counts.",
            "Tag every entry by stage on the data path and by cross-cutting concern, such as quality, lineage, privacy or cost.",
            "Map each entry to the matching part of the open data-contract standard (ODCS) and the open lineage standard (OpenLineage) where one exists.",
            "Describe test scenarios in the same world format the AgentTwin simulator uses, so a planted incident can be replayed.",
            "Give per-platform notes showing how each capability is usually met on Databricks, Fabric, AWS, GCP and an open stack.",
            "Lint the catalog so that every entry has an id, a stage, a concern and, for obligations, a check.",
        ],
        "nonfunctional": [
            "Entries cite standards and products; they never copy their text.",
            "Identifiers are flat and permanent, so a citation never breaks when the catalog is reorganised.",
            "The spec is plain text in a public repository, readable without any special tool.",
            "Product-specific advice lives in separate binding files, so the core catalog does not go stale with vendor releases.",
            "The licence lets anyone reuse and adapt the spec with credit.",
        ],
        "components": [
            ("Data path model", "Names the stages from sources to experiences and the cross-cutting concerns."),
            ("Capability catalog", "Lists what parts a data platform must have, stage by stage."),
            ("Assurance catalog", "Lists what must be true of the data and how each promise is checked."),
            ("Standards crosswalk", "Links entries to the data-contract and lineage standards they rely on."),
            ("Scenario library", "Holds replayable incidents, such as a renamed column or a late day of data."),
            ("Platform bindings", "Shows how each capability is usually met on each platform."),
            ("Linter and renderer", "Checks every entry is complete and builds the readable website."),
        ],
        "flows": [
            ("Data path model", "Capability catalog", "stages and concerns"),
            ("Data path model", "Assurance catalog", "stages and concerns"),
            ("Capability catalog", "Assurance catalog", "a capability makes a promise checkable"),
            ("Assurance catalog", "Standards crosswalk", "cite, do not restate"),
            ("Assurance catalog", "Scenario library", "incidents that test each promise"),
            ("Capability catalog", "Platform bindings", "how each part is met"),
            ("Platform bindings", "Linter and renderer", "complete entries only"),
        ],
        "bindings": {
            "Open stack": {
                "Ingestion": "Proposal: change capture from sources into object storage",
                "Bronze/Silver/Gold": "Proposal: DuckDB or ClickHouse with dbt models",
                "Data contracts": "Proposal: ODCS files checked in CI",
                "Lineage": "Proposal: OpenLineage events into Marquez",
                "Semantic model": "Proposal: Cube Core",
                "Experiences": "Proposal: Superset dashboards and a conversation UI over the semantic model",
            },
            "Databricks": {
                "Medallion": "Proposal: Delta tables with Lakeflow pipelines",
                "Catalog and lineage": "Proposal: Unity Catalog",
                "Semantic model": "Proposal: Metric Views",
                "Experiences": "Proposal: AI/BI dashboards and Genie",
            },
            "Azure": {
                "Platform": "Proposal: Microsoft Fabric lakehouse and OneLake",
                "Catalog and governance": "Proposal: Microsoft Purview",
                "Semantic model": "Proposal: Power BI semantic models",
                "Experiences": "Proposal: Power BI reports and Copilot",
            },
            "AWS": {
                "Storage and tables": "Proposal: S3 with Apache Iceberg tables",
                "Transform": "Proposal: Glue or EMR",
                "Catalog": "Proposal: Glue Data Catalog and DataZone",
                "Experiences": "Proposal: QuickSight",
            },
            "GCP": {
                "Warehouse": "Proposal: BigQuery",
                "Catalog and lineage": "Proposal: Dataplex",
                "Semantic model": "Proposal: Looker modelling layer",
                "Experiences": "Proposal: Looker dashboards",
            },
        },
        "work": [
            ("Agree the frame", [
                ("Write the data path model and the list of cross-cutting concerns", "todo", "M", "data architecture"),
                ("Write the entry schema for capabilities and obligations", "todo", "S", "spec writing"),
                ("Decide the boundary between the two catalogs, with five worked examples", "todo", "S", "data architecture"),
            ]),
            ("First core entries", [
                ("Draft about 20 capabilities across ingestion, bronze, silver and gold", "todo", "L", "data engineering"),
                ("Draft about 20 obligations for quality, freshness, schema and lineage", "todo", "L", "data quality"),
                ("Map each obligation to ODCS and OpenLineage fields", "todo", "M", "standards"),
            ]),
            ("Tooling", [
                ("Build the linter that rejects incomplete entries", "todo", "M", "Python or JavaScript"),
                ("Build the renderer that turns the catalog into web pages", "todo", "M", "web"),
            ]),
            ("Scenarios and bindings", [
                ("Write five replayable incidents in the AgentTwin world format", "todo", "M", "testing"),
                ("Write platform bindings for an open stack and one cloud", "todo", "M", "platform engineering"),
            ]),
            ("Prove it on a real platform", [
                ("Run the catalog against one small reference platform and publish the gaps found", "todo", "L", "data engineering"),
            ]),
        ],
        "roles": [
            ("Spec lead", 1, "4–6 hours/week", "Owns the frame, the schema and the boundary between the two catalogs."),
            ("Data engineer contributor", 3, "2–4 hours/week", "Drafts entries for the stages they know best."),
            ("Platform specialist", 2, "2 hours/week", "Writes the binding notes for one platform each."),
            ("Reviewer", 2, "1–2 hours/week", "Checks entries are plain, complete and not vendor advice in disguise."),
        ],
        "learn": [
            "How a data platform is laid out end to end, from sources to dashboards.",
            "How data contracts (ODCS) and lineage events (OpenLineage) work.",
            "How to write a requirement that can be checked, not just agreed with.",
            "How the same capability looks on different clouds.",
            "How open standards are written, reviewed and versioned.",
        ],
        "questions": [
            "Where exactly is the line between a capability (must exist) and an obligation (must be true)?",
            "Should the semantic model and conversational analytics be in the first release or a later one?",
            "How much of the data-contract standard can we point to before we have to add our own fields?",
            "Which small reference platform should we test the catalog against first?",
        ],
        "repo": None,
        "repo_public": False,
        "links": [
            ("AI Harness Catalog (the sibling 'must exist' catalog)", "https://github.com/dataagentsai/ai-harness-catalog"),
            ("AI Assurance Catalog (the sibling 'must be true' catalog)", "https://github.com/dataagentsai/ai-assurance-catalog"),
            ("AgentTwin (world format for scenarios)", "https://github.com/dataagentsai/agenttwin"),
            ("Open Data Contract Standard", "https://bitol-io.github.io/open-data-contract-standard/"),
            ("OpenLineage", "https://openlineage.io/"),
        ],
        "good_first": [
            "Write one capability entry for a stage you know well, such as ingestion.",
            "Write one obligation for data freshness, with how you would check it.",
            "Describe one real incident you have seen as a short replayable scenario.",
        ],
    },

    # ------------------------------------------------------------------ 2
    {
        "id": "hinglish-pretraining-data",
        "title": "Hinglish pre-training data",
        "subject": "llm",
        "group": "open",
        "status": "not-started",
        "started": "",
        "lead": "Basant Choudhary",
        "one_liner": "An open, cleaned corpus of Hindi written in English letters, proved by training small models on it.",
        "purpose": (
            "Hundreds of millions of people type Hindi in English letters, often mixed with English, which is called Hinglish. "
            "Today's open web datasets hold very little of it: one large open dataset has about 98,000 such documents, "
            "against more than 22 million in Hindi script, and a rough sample suggests a third of them are junk. "
            "We would harvest, clean, deduplicate and quality-score real Hinglish from the public web crawl, "
            "then show it helps by training identical small models on different versions of the data and comparing their scores. "
            "Finally we would fine-tune and shrink a small Hinglish model that can run on an Android tablet."
        ),
        "audience": "Language-model researchers, Indian AI builders, and data engineers who want to learn how pre-training data is made.",
        "benefits": [
            ("Fills a measured gap", "Gives builders far more clean Hinglish text than any open dataset has today."),
            ("Evidence, not claims", "Fixed-compute comparisons show whether the data actually improves models."),
            ("Better Indian products", "Chat and voice products can understand how Indians really type."),
            ("Runs on small devices", "A small model that fits a tablet makes Hinglish AI usable offline and cheaply."),
            ("Open to everyone", "Data, pipeline and results are published so others can build on them."),
        ],
        "functional": [
            "Pre-filter public web crawl text for likely Hinglish using common Hindi function words and Indian sites.",
            "Identify romanized Hindi with a language detector, telling it apart from English and Urdu.",
            "Remove near-duplicates, adult content, spam and personal details.",
            "Score each document's quality with a small classifier trained on examples labelled by an open model.",
            "Build a Hinglish test set: held-out text for perplexity and a hand-checked multiple-choice set.",
            "Train identical small models (about 150M and 400M parameters, then one 1B run) on each data version and compare.",
            "Fine-tune and compress the best small model so it runs on an Android tablet.",
        ],
        "nonfunctional": [
            "Success criteria are written down before any training run, so results cannot be cherry-picked.",
            "Every model traces back to the exact data version it was trained on.",
            "Each comparison uses at least two random seeds so noise is not mistaken for a gain.",
            "The pipeline is reproducible from public inputs with one documented command per stage.",
            "Licences of every source are recorded and respected in what is released.",
        ],
        "components": [
            ("Crawl harvester", "Pulls text from public web crawl dumps and keeps likely Hinglish pages."),
            ("Language identifier", "Decides which documents are really romanized Hindi."),
            ("Cleaner and deduplicator", "Removes near-copies, adult content, spam and personal data."),
            ("Quality scorer", "Gives each document a quality score from a small trained classifier."),
            ("Dataset versioner", "Freezes each data version with its counts and a record of how it was made."),
            ("Ablation trainer", "Trains identical small models on each data version with the same compute."),
            ("Evaluation suite", "Scores models on Hinglish and Hindi tests and tracks seeds."),
            ("Small-model packager", "Fine-tunes and compresses the winning model for a tablet."),
        ],
        "flows": [
            ("Crawl harvester", "Language identifier", "candidate pages"),
            ("Language identifier", "Cleaner and deduplicator", "romanized Hindi documents"),
            ("Cleaner and deduplicator", "Quality scorer", "clean unique documents"),
            ("Quality scorer", "Dataset versioner", "scored documents"),
            ("Dataset versioner", "Ablation trainer", "frozen data versions"),
            ("Ablation trainer", "Evaluation suite", "model checkpoints"),
            ("Evaluation suite", "Small-model packager", "the winning setup"),
        ],
        "bindings": {
            "Open stack": {
                "Pipeline": "Proposal: datatrove on spot CPU machines",
                "Language ID": "Proposal: IndicLID romanized model or GlotLID",
                "Deduplication": "Proposal: MinHash",
                "Quality scorer": "Proposal: fastText or XLM-R classifier",
                "Training": "Proposal: nanotron or a small Llama-style trainer",
                "Packaging": "Proposal: llama.cpp with 4-bit GGUF",
                "Release": "Proposal: Hugging Face datasets and models",
            },
            "Azure": {
                "Processing": "Proposal: Azure Batch on spot VMs",
                "Training": "Proposal: Azure Machine Learning with H100 VMs",
                "Storage": "Proposal: Blob Storage",
            },
            "AWS": {
                "Processing": "Proposal: EMR or Batch on spot instances next to Common Crawl in S3",
                "Training": "Proposal: SageMaker training jobs or EC2 GPU instances",
                "Storage": "Proposal: S3",
            },
            "GCP": {
                "Processing": "Proposal: Dataproc on spot VMs",
                "Training": "Proposal: Vertex AI custom training on GPUs",
            },
            "Android": {
                "On-device model": "Proposal: llama.cpp or MediaPipe LLM inference running the compressed model",
            },
        },
        "work": [
            ("Pilot one crawl dump", [
                ("Run the pre-filter and language ID on one crawl dump and measure the yield", "todo", "M", "data engineering"),
                ("Hand-check 500 sampled documents for real Hinglish and junk", "todo", "S", "Hindi reading"),
                ("Go or no-go decision on whether the yield justifies scaling", "todo", "S", "judgement"),
            ]),
            ("Build the corpus", [
                ("Clean, deduplicate and filter adult content and personal data", "todo", "L", "data engineering"),
                ("Label about 50,000 documents with an open model and train the quality scorer", "todo", "M", "machine learning"),
                ("Freeze and document the data versions", "todo", "S", "data engineering"),
            ]),
            ("Build the tests", [
                ("Build the Hinglish held-out set and the hand-checked multiple-choice set", "todo", "M", "Hindi, evaluation"),
            ]),
            ("Run the comparisons", [
                ("Train 150M models on each data version with two seeds", "todo", "M", "model training"),
                ("Confirm at 400M and run one 1B headline comparison", "todo", "L", "model training"),
            ]),
            ("Small model and release", [
                ("Fine-tune and compress a 1B Hinglish model for a tablet", "todo", "M", "machine learning"),
                ("Publish the data, pipeline, results and a write-up", "todo", "M", "writing"),
            ]),
        ],
        "roles": [
            ("Data pipeline engineer", 2, "4–6 hours/week", "Builds harvesting, cleaning, deduplication and versioning."),
            ("ML engineer", 1, "4–6 hours/week", "Runs the quality scorer, the small-model training and the comparisons."),
            ("Hindi and Hinglish reviewer", 2, "2 hours/week", "Hand-checks samples and the test set."),
            ("On-device engineer", 1, "2–4 hours/week", "Gets the compressed model running on an Android tablet."),
        ],
        "learn": [
            "How web-scale pre-training data is collected and cleaned.",
            "How language identification, deduplication and quality filtering work.",
            "How to run a fair data comparison with fixed compute and several seeds.",
            "How small language models are trained, fine-tuned and compressed.",
            "How to run a model on a phone or tablet.",
        ],
        "questions": [
            "How much real Hinglish is actually in the public web crawl, and how much is mislabelled as English?",
            "Does training on Hinglish improve Hinglish ability without hurting Hindi in its own script?",
            "Which language detector separates romanized Hindi from English and Urdu best?",
            "How small can the final model be and still hold a useful Hinglish conversation?",
        ],
        "repo": None,
        "repo_public": False,
        "links": [
            ("FineWeb-2 (the open baseline)", "https://huggingface.co/datasets/HuggingFaceFW/fineweb-2"),
            ("Common Crawl", "https://commoncrawl.org/"),
            ("datatrove pipeline library", "https://github.com/huggingface/datatrove"),
        ],
        "good_first": [
            "Read 100 sampled Hinglish documents and label them real, junk or mislabelled.",
            "Write 50 Hinglish multiple-choice questions for the test set.",
            "Compare two language detectors on a small labelled sample.",
        ],
    },

    # ------------------------------------------------------------------ 3
    {
        "id": "robotics-data-benchmark",
        "title": "Robotics data benchmark",
        "subject": "ai",
        "group": "open",
        "status": "not-started",
        "started": "",
        "lead": "Open — looking for a lead",
        "one_liner": "A fair test of which ways of cleaning robot demonstration data actually make robots succeed more.",
        "purpose": (
            "Robots learn tasks from recorded demonstrations, and many papers propose ways to pick the best demonstrations. "
            "Each paper tests on its own setup, so nobody can say which method really works. "
            "We would keep the robot policy, training recipe and simulator fixed, change only which demonstrations go in, "
            "and measure how often the robot actually completes its tasks across several runs. "
            "Behind it sits a small data engine with lineage, so every trained policy traces back to the exact demonstrations it saw."
        ),
        "audience": "Robot-learning researchers, robotics startups, and data engineers curious about data quality for physical AI.",
        "benefits": [
            ("One fair comparison", "Curation methods are compared on the same harness for the first time."),
            ("Measured on real success", "Scores come from the robot doing the task, not from training loss alone."),
            ("Less wasted data collection", "Teams learn which demonstrations are worth recording and keeping."),
            ("Reproducible", "Every result traces back to the exact data version and seed."),
        ],
        "functional": [
            "Load public demonstration datasets in a standard format and pin their exact revision.",
            "Check each dataset against a schema and flag metadata that contradicts the data.",
            "Inject known kinds of bad data, such as jerky or idle episodes, to create a ground truth.",
            "Apply each curation method to choose a subset under the same data budget.",
            "Train the same small policy on each subset with the same recipe.",
            "Run closed-loop trials in simulation over several seeds and report success rates with spread.",
            "Publish a leaderboard where anyone can submit a new curation method.",
        ],
        "nonfunctional": [
            "Results report at least three seeds and their spread, never a single run.",
            "Every checkpoint is linked to its episode set, scores and dataset revision.",
            "The whole benchmark runs on a modest GPU budget so others can repeat it.",
            "Simulation results are clearly labelled as simulation, not real-robot results.",
        ],
        "components": [
            ("Dataset loader", "Reads public demonstration datasets at a pinned revision."),
            ("Contract checker", "Checks schema and metadata and rejects broken episodes."),
            ("Corruption injector", "Plants known bad episodes so methods can be graded."),
            ("Curation runner", "Applies each method to pick a subset under one data budget."),
            ("Policy trainer", "Trains the same small policy on each subset."),
            ("Simulation evaluator", "Runs the robot in simulation and counts task successes per seed."),
            ("Lineage and leaderboard", "Records what produced each result and publishes the comparison."),
        ],
        "flows": [
            ("Dataset loader", "Contract checker", "episodes at a pinned revision"),
            ("Contract checker", "Corruption injector", "valid episodes"),
            ("Corruption injector", "Curation runner", "episodes with known bad ones"),
            ("Curation runner", "Policy trainer", "chosen subset"),
            ("Policy trainer", "Simulation evaluator", "policy checkpoint"),
            ("Simulation evaluator", "Lineage and leaderboard", "success rates per seed"),
        ],
        "bindings": {
            "Open stack": {
                "Data format": "Proposal: LeRobotDataset v3",
                "Policy": "Proposal: SmolVLA, with ACT or Diffusion Policy as cheap baselines",
                "Simulation": "Proposal: LIBERO and LIBERO-Plus, robomimic for the cheap first stage",
                "Lineage": "Proposal: OpenLineage events or MLflow runs",
                "Leaderboard": "Proposal: a static site from result files",
            },
            "Azure": {
                "Training and simulation": "Proposal: Azure Machine Learning on GPU VMs",
                "Storage": "Proposal: Blob Storage",
            },
            "AWS": {
                "Training and simulation": "Proposal: EC2 GPU instances or SageMaker",
                "Storage": "Proposal: S3",
            },
            "GCP": {
                "Training and simulation": "Proposal: Vertex AI or GPU VMs",
            },
        },
        "work": [
            ("Fixed harness", [
                ("Pick the policy, simulator and data budget and write them down", "todo", "S", "robot learning"),
                ("Reproduce a clean baseline success rate over three seeds", "todo", "M", "robot learning"),
            ]),
            ("Data engine", [
                ("Build the loader, contract checker and lineage records", "todo", "M", "data engineering"),
                ("Build the corruption injector with five kinds of bad episodes", "todo", "M", "data engineering"),
            ]),
            ("Compare methods", [
                ("Implement three published curation methods behind one interface", "todo", "L", "machine learning"),
                ("Run every method on the fixed harness over three seeds", "todo", "L", "GPU operations"),
            ]),
            ("Publish", [
                ("Publish the leaderboard, data versions and a write-up", "todo", "M", "writing"),
                ("Document how to submit a new method", "todo", "S", "writing"),
            ]),
        ],
        "roles": [
            ("Robot-learning lead", 1, "4–6 hours/week", "Owns the fixed harness and the fairness of the comparison."),
            ("Data engineer", 2, "3–4 hours/week", "Builds loading, contracts, corruption and lineage."),
            ("ML engineer", 1, "3–4 hours/week", "Implements curation methods and runs training."),
        ],
        "learn": [
            "How robots learn from demonstrations and how they are tested in simulation.",
            "Why low training loss can still mean a robot fails the task.",
            "How to design a fair benchmark with fixed compute and several seeds.",
            "How data lineage makes machine-learning results trustworthy.",
        ],
        "questions": [
            "Which simulator benchmark is hard enough that curation effects show, given that the standard one is nearly saturated?",
            "Do offline quality scores predict closed-loop success at all?",
            "How many seeds are enough to separate a real gain from noise?",
            "Which curation methods can run on a modest GPU budget?",
        ],
        "repo": None,
        "repo_public": False,
        "links": [
            ("LeRobot", "https://github.com/huggingface/lerobot"),
            ("LIBERO benchmark", "https://libero-project.github.io/"),
            ("DataComp (the idea we borrow)", "https://www.datacomp.ai/"),
        ],
        "good_first": [
            "Run one LeRobot dataset through a schema check and list what is inconsistent.",
            "Write a script that injects idle frames into an episode.",
            "Summarise one curation paper in a page: what it scores and how it was tested.",
        ],
    },

    # ------------------------------------------------------------------ 4
    {
        "id": "pain-registry-helpers",
        "title": "AI job-loss pain registry and helpers",
        "subject": "ai",
        "group": "open",
        "status": "starting",
        "started": "2026-10",
        "lead": "Basant Choudhary",
        "one_liner": "Evidence-backed problems of people losing work to AI, and simple free tools that help them earn again.",
        "purpose": (
            "Many people are losing work or income because of AI automation, and new work is not appearing fast enough. "
            "The registry lists their real, still-open problems, each backed by evidence and each naming how a product could exploit them. "
            "From it we would build simple helpers in order: an India laid-off kit, then a job-scam checker in Indian languages, "
            "then a catalog where displaced workers offer fixed-price AI setups to small businesses. "
            "The goal is genuine help, and no tool ever charges a desperate person upfront."
        ),
        "audience": "People in India who have lost or fear losing their job to AI, and volunteers who want to help them.",
        "benefits": [
            ("Stops money being lost", "People avoid scams and claim entitlements they would otherwise miss."),
            ("Shortens the gap", "Clear steps after a layoff help people reach their next income sooner."),
            ("Creates new work", "Displaced workers become paid AI helpers for small businesses."),
            ("Built on evidence", "Every tool links back to a documented, sourced problem."),
        ],
        "functional": [
            "Keep a registry of pain points, each with who feels it, evidence, severity and the harm risk of any product.",
            "Keep an ideas list where each idea links to the pain points it fixes and carries a pursue or drop verdict.",
            "Laid-off kit: one page covering provident fund choices, loan runway, entitlement checks, health cover deadlines and a plan for telling family.",
            "Scam checker: paste or forward a job message and get its red flags plus the official cyber-crime helpline and reporting links.",
            "Helper catalog: fixed-scope, fixed-price AI setups for small businesses, each with before-and-after proof.",
            "Offer the kit and the checker in Hindi and English first.",
        ],
        "nonfunctional": [
            "Plain rules first; an AI model is used only to translate or read messy text.",
            "No upfront charge to a person in distress, ever.",
            "No personal data is stored from the scam checker beyond what the person chooses to share.",
            "Pages load fast on a cheap phone over a slow connection.",
            "Every rule and figure in the kit cites its official source and date.",
        ],
        "components": [
            ("Pain registry", "Holds the evidence-backed problems as structured records."),
            ("Ideas board", "Links ideas to problems and records the verdict and reason."),
            ("Rules library", "Holds the plain rules behind the kit and the scam checks."),
            ("Laid-off kit site", "Walks a person through their first weeks after a layoff."),
            ("Scam checker", "Lists red flags in a job message and points to official help."),
            ("Helper catalog", "Lists fixed-price AI setups that displaced workers deliver to small businesses."),
        ],
        "flows": [
            ("Pain registry", "Ideas board", "problems each idea fixes"),
            ("Ideas board", "Rules library", "ideas chosen to build"),
            ("Rules library", "Laid-off kit site", "entitlement and deadline rules"),
            ("Rules library", "Scam checker", "red-flag rules"),
            ("Laid-off kit site", "Helper catalog", "an audience of people who want new work"),
        ],
        "bindings": {
            "Open stack": {
                "Registry": "Proposal: YAML files in git, the format already used",
                "Kit site": "Proposal: a static site generated from the rules library",
                "Scam checker": "Proposal: a small rules service, with an open model only for translation",
                "Catalog": "Proposal: a static listing first, a simple app later",
            },
            "Azure": {
                "Hosting": "Proposal: Azure Static Web Apps and Azure Functions",
                "Translation": "Proposal: Azure AI Translator",
            },
            "AWS": {
                "Hosting": "Proposal: S3 with CloudFront and Lambda",
                "Translation": "Proposal: Amazon Translate",
            },
        },
        "work": [
            ("Registry and ideas", [
                ("Record pain points with evidence and harm risk", "done", "M", "research"),
                ("Write the ideas list with verdicts and a build order", "done", "M", "product thinking"),
                ("Publish the registry and ideas in a public repository", "todo", "S", "git"),
            ]),
            ("India laid-off kit", [
                ("Write and source the rules for each part of the kit", "todo", "M", "Indian employment and finance rules"),
                ("Build the static kit site in Hindi and English", "todo", "M", "web"),
                ("Have the rules checked by a professional volunteer", "todo", "S", "law or accounting"),
            ]),
            ("Job-scam checker", [
                ("Turn the scam patterns in the registry into red-flag rules", "todo", "M", "rules engineering"),
                ("Build the paste-a-message checker with official help links", "todo", "M", "web"),
            ]),
            ("AI helper catalog", [
                ("Define five fixed-scope AI setups with before-and-after proof", "todo", "M", "small-business AI"),
                ("Pilot in one city and one trade", "todo", "L", "community"),
            ]),
        ],
        "roles": [
            ("Researcher", 2, "2–3 hours/week", "Adds sourced pain points and keeps evidence current."),
            ("Web developer", 1, "3–4 hours/week", "Builds the kit site and the scam checker."),
            ("Rules checker", 1, "1–2 hours/week", "A lawyer, accountant or HR professional who checks the kit's rules."),
            ("Translator", 2, "1–2 hours/week", "Translates and reviews pages in Indian languages."),
        ],
        "learn": [
            "How to turn real evidence into a product decision.",
            "How to build helpful tools with plain rules before reaching for AI.",
            "How job scams work and how to spot them.",
            "How to design for people under stress and on cheap phones.",
        ],
        "questions": [
            "Which part of the laid-off kit would help the most people in the first month?",
            "How do we keep the kit's rules correct as laws and deadlines change?",
            "How can a scam checker work inside the messaging apps people already use?",
            "How do we get both small businesses and helpers to show up at the same time for the catalog?",
        ],
        "repo": None,
        "repo_public": False,
        "links": [
            ("National Cyber Crime Reporting Portal (India)", "https://cybercrime.gov.in/"),
        ],
        "good_first": [
            "Add one sourced pain point to the registry.",
            "Write and source one rule for the laid-off kit, such as the provident fund withdrawal options.",
            "Collect five real job-scam messages and list their red flags.",
            "Translate one kit page into an Indian language.",
        ],
    },

    # ------------------------------------------------------------------ 5
    {
        "id": "babu-companion",
        "title": "Babu, an elderly-companion assistant",
        "subject": "ai",
        "group": "open",
        "status": "starting",
        "started": "2026-08",
        "lead": "Basant Choudhary",
        "one_liner": "A Hindi-speaking companion for older adults that remembers their life and keeps them connected.",
        "purpose": (
            "Many older adults spend long hours alone, and generic voice assistants forget everything between conversations. "
            "Babu is a companion that knows the person over time: their life story, the people they love, their routines and what is happening in their family's lives. "
            "At its core is a personal world model, a structured memory of people, events, facts, preferences and time, rather than a plain chat log. "
            "The work is requirements-first: the requirements, memory design and architecture came before any technology choice, "
            "and the first build is a prototype on a laptop before an Android tablet app."
        ),
        "audience": "Families caring for older relatives, elder-care organisations, and engineers interested in memory for AI companions.",
        "benefits": [
            ("Company that remembers", "Conversations build on what was said days or years ago, so they feel personal."),
            ("Speaks their language", "Hindi and English with natural mixing, so the person never has to adapt to the machine."),
            ("Family stays close", "Babu knows what is happening in the family's lives and brings it into conversation."),
            ("The person stays in control", "The older adult decides what is remembered, shared or forgotten."),
        ],
        "functional": [
            "Hold a natural conversation in Hindi, English or a mix of both.",
            "Remember people, relationships, events, preferences and routines, and bring them up naturally later.",
            "Find memories four ways: by exact facts, by meaning, by relationships and by time, then combine the results.",
            "Forget something completely when the person asks, including every copy and index of it.",
            "Handle sensitive moments, such as a bereavement, without saying anything false.",
            "Work out who the person means and what they are asking, and ask back when it is unclear.",
            "Offer gentle activities such as songs, proverbs and riddles.",
        ],
        "nonfunctional": [
            "The older adult is the owner of their own data; family members cannot consent for them.",
            "Built to meet India's data protection law, including deletion that really deletes.",
            "Private conversations are never sent to a model provider that may train on them.",
            "Replies come quickly enough to feel like a person thinking, not a machine loading.",
            "Large text, clear voice and no timers or menus the person must race against.",
            "Every remembered fact keeps who said it and the original words in the original language.",
        ],
        "components": [
            ("Speech and conversation interface", "Hears the person and speaks replies, starting as a typed chat."),
            ("Understanding step", "Works out who the person means and what kind of request it is."),
            ("Memory retrieval", "Searches the world model four ways and combines the results."),
            ("Permission gate", "Removes anything the person has not agreed to share in this context."),
            ("Prompt assembler", "Builds the model's instructions from the persona, the person and the retrieved memories."),
            ("Reply generator", "Makes the single model call that writes the reply."),
            ("Memory keeper", "Extracts new facts from the conversation and stores them with their source."),
            ("Personal world model store", "Holds people, events, facts, memories, preferences and time in one place."),
        ],
        "flows": [
            ("Speech and conversation interface", "Understanding step", "what the person said"),
            ("Understanding step", "Memory retrieval", "who and what they mean"),
            ("Personal world model store", "Memory retrieval", "facts, links and memories"),
            ("Memory retrieval", "Permission gate", "ranked memories"),
            ("Permission gate", "Prompt assembler", "only what may be used"),
            ("Prompt assembler", "Reply generator", "assembled instructions"),
            ("Reply generator", "Speech and conversation interface", "the reply"),
            ("Reply generator", "Memory keeper", "the exchange"),
            ("Memory keeper", "Personal world model store", "new facts with their source"),
        ],
        "bindings": {
            "Open stack": {
                "World model store": "PostgreSQL with pgvector, relationships as rows and recursive queries ✓",
                "Meaning search": "Multilingual embedding model (BGE-M3) ✓",
                "Schema changes": "Alembic migrations ✓",
                "Tests": "pytest with guarantee, retrieval and tone suites ✓",
                "Reply model": "Proposal: a hosted model with no-training terms, or self-hosted open weights",
                "Voice": "Proposal: speech-to-text and text-to-speech around the same chat loop",
            },
            "Azure": {
                "Store": "Proposal: Azure Database for PostgreSQL with pgvector",
                "Voice": "Proposal: Azure AI Speech for Hindi",
                "Model": "Proposal: Azure-hosted model with no-training terms",
            },
            "AWS": {
                "Store": "Proposal: Amazon RDS for PostgreSQL with pgvector",
                "Voice": "Proposal: Amazon Transcribe and Polly",
                "Model": "Proposal: Amazon Bedrock",
            },
            "Android": {
                "App": "Proposal: a tablet app with large text and voice first, after the laptop prototype",
                "On-device voice": "Proposal: Android speech services, only if they pass a Hindi quality test",
            },
        },
        "work": [
            ("Requirements and design", [
                ("Write and review the requirements catalogue, with a test for every must-have", "done", "L", "requirements"),
                ("Design the memory ontology and canonical schemas", "done", "L", "data modelling"),
                ("Choose the store and write the architecture and database design", "done", "M", "architecture"),
            ]),
            ("Memory core prototype", [
                ("Schema, write path and true deletion, with tests", "done", "M", "PostgreSQL, Python"),
                ("Seed a realistic fictional life of about 200 records", "done", "M", "writing, data"),
                ("Four-way retrieval, permission gate and conflict handling", "done", "L", "search, Python"),
                ("Understanding step: who is meant and what is asked", "done", "M", "NLP"),
            ]),
            ("Conversation prototype", [
                ("One-hour tone probe on real model replies", "todo", "S", "conversation design"),
                ("Prompt assembly, reply generation and memory keeping", "todo", "M", "LLM engineering"),
                ("Tone harness that fails the build on banned phrasing", "todo", "S", "testing"),
            ]),
            ("Voice", [
                ("Add speech in and out around the chat loop and test Hindi voice quality", "todo", "L", "speech"),
            ]),
            ("Android tablet MVP", [
                ("Build the tablet app on the proven prototype", "todo", "L", "Android"),
            ]),
        ],
        "roles": [
            ("Conversation designer", 1, "2–3 hours/week", "Writes and judges Hindi exchanges and the tone rules."),
            ("Backend engineer", 1, "4–6 hours/week", "Builds the reply pipeline and memory keeping."),
            ("Speech engineer", 1, "2–4 hours/week", "Tests and integrates Hindi speech in and out."),
            ("Android developer", 1, "4 hours/week", "Builds the tablet app once the prototype is proven."),
        ],
        "learn": [
            "How to design long-term memory for an AI assistant beyond a vector database.",
            "How to combine search by facts, meaning, relationships and time.",
            "How privacy law shapes a data model from the first record.",
            "How to design conversation for older adults and sensitive moments.",
            "How to work requirements-first and choose technology last.",
        ],
        "questions": [
            "Does Babu sound like a person rather than a form when you read its transcripts?",
            "Is on-device Hindi speech good enough to live with, or must voice run in the cloud?",
            "How should Babu handle a family member asking about something the person chose not to share?",
            "What is the smallest set of situations the prototype must handle beautifully?",
        ],
        "repo": None,
        "repo_public": False,
        "links": [],
        "good_first": [
            "Write a Hindi or Hinglish exchange for one everyday situation, such as a festival morning.",
            "Review a sample transcript and mark anything that sounds like a machine.",
            "Add a test case for who-does-he-mean, such as two people with the same name.",
        ],
    },
]
