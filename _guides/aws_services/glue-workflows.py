SERVICE = {
    "slug": "glue-workflows",
    "name": "AWS Glue Workflows and triggers",
    "short": "Glue Workflows",
    "group": "orchestration",
    "one_line": "Chains Glue jobs and crawlers with triggers on a schedule, on demand or on an event, inside the Glue console.",
    "status": "Generally available; no announced retirement. Starting a workflow from an Amazon EventBridge event, with batching of events, is supported.",
    "checked": "2026-11-11",
    "site_verdict": ("Drop",
                     "Glue Workflows only orchestrate Glue jobs and crawlers, and this platform does not use Glue jobs for transformation. "
                     "Lakeflow Jobs runs every Databricks task, and EventBridge handles AWS-side triggers, so a third orchestrator adds "
                     "nothing but another place to look when a run fails."),
    "equivalents": {"azure": "Azure Data Factory pipelines and triggers", "gcp": "Cloud Composer or Workflows",
                    "databricks": "Lakeflow Jobs (tasks, triggers, run history)", "open_source": "Apache Airflow, Dagster"},
    "plain": [
        "Orchestration means running steps in the right order at the right time: first load the orders, then load the customers, and only "
        "when both have finished, build the daily sales table. If a step fails, stop and tell someone. A tool that does this is an "
        "orchestrator.",
        "AWS Glue Workflows is the orchestrator built into AWS Glue. A workflow is a small graph of three kinds of things. Jobs are Glue ETL "
        "scripts. Crawlers scan files in S3 and record their tables in the Glue Data Catalog. Triggers decide when the next thing starts. A "
        "trigger can fire on a schedule written as a cron expression, on demand when someone presses start, on an event from Amazon "
        "EventBridge such as a file arriving in S3, or conditionally when earlier jobs or crawlers succeed, fail or stop.",
        "A concrete example from a retailer. At two in the morning a scheduled trigger starts a crawler over last night's point-of-sale "
        "files. When the crawler succeeds, a conditional trigger starts two Glue jobs in parallel, one for store sales and one for returns. "
        "When both succeed, another conditional trigger starts a job that builds the daily margin table. The Glue console draws this as a "
        "graph and shows each run with the status of every node.",
        "Workflows can also carry run properties, which are small named values that every job in the run can read and update, such as the "
        "business date being processed. Blueprints let you generate many similar workflows from one template with parameters.",
    ],
    "analogy": "A line of dominoes set up inside one room: neat for the pieces in that room, but it cannot knock over anything outside it.",
    "big_picture": [
        "Glue Workflows sit in the orchestration band that runs across every lane of the platform. In a Glue-centred AWS design, they start "
        "crawlers after files land, run the bronze, silver and gold Glue jobs in order, and refresh the catalog for Athena and Redshift "
        "Spectrum.",
        "On this site's reference platform the processing engine is Databricks, so the orchestrator lives there too. Lakeflow Jobs runs the "
        "lander, silver, gold, quality checks and metric view refreshes, with schedules, file-arrival and table-update triggers, retries, "
        "alerts and run history in system tables. On the AWS side, Amazon EventBridge reacts to events such as a DMS task finishing or a "
        "file landing, and calls the Databricks Jobs API. Step Functions is used only when a mover needs several AWS steps. Glue Workflows "
        "have no job to do in that picture, which is why the site marks them Drop.",
        "If a company already runs Glue Workflows, they retire together with the Glue jobs they drive. As each subject is rebuilt as a "
        "Databricks pipeline and its parallel run reconciles, the matching workflow is disabled and then deleted. There is no reason to "
        "rebuild a Glue workflow to call Databricks.",
    ],
    "upstream": ["svc:eventbridge", "Schedules and on-demand starts", "svc:s3"],
    "downstream": ["svc:glue-etl", "Glue crawlers", "svc:glue-data-catalog"],
    "concepts": [
        ("Workflow", "A named graph of Glue jobs, crawlers and triggers that runs as one unit and has its own run history."),
        ("Trigger", "The thing that starts jobs or crawlers. Types are scheduled, on demand, EventBridge event and conditional."),
        ("Conditional trigger", "Fires when watched jobs or crawlers reach a state such as succeeded, failed, stopped or timed out, with all or any logic."),
        ("Start trigger", "The first trigger of a workflow. Each workflow has one start trigger, which is scheduled, on demand or an EventBridge event."),
        ("Event batching", "For an EventBridge start trigger, wait for a number of events (1 to 100) or a time window (up to 900 seconds) before starting one run."),
        ("Run properties", "Small named values shared by all jobs in one workflow run, such as the business date, readable and writable from job code."),
        ("Blueprint", "A template plus a Python script that generates a workflow from parameters, so many similar pipelines share one definition."),
        ("Resume", "After fixing a failed node, you can resume a workflow run from that node instead of starting over."),
    ],
    "use_when": [
        "You already run Glue jobs and crawlers chained by workflows, and they will keep running only until the Databricks migration of each subject.",
        "A small AWS-only team needs a few Glue jobs in order and has no other orchestrator in the account.",
        "Several Glue jobs must start after a crawler has updated the catalog, and everything involved is inside Glue.",
        "You want a simple graph view of Glue runs in the console without adding Airflow or Step Functions.",
    ],
    "avoid_when": [
        "Avoid Glue Workflows when the work runs in Databricks; Lakeflow Jobs orchestrates Databricks tasks natively with lineage and run history.",
        "Avoid them when a pipeline spans many AWS services or outside systems; a workflow can only run Glue jobs and crawlers.",
        "Avoid them when you need rich branching, loops over a list of datasets or human approval steps.",
        "Avoid them for event-heavy ingestion where duplicates matter; Glue does not guarantee delivery or remove duplicate EventBridge events.",
        "Avoid building new blueprints as your metadata framework; the reference design keeps that framework in Databricks.",
    ],
    "challenges": [
        ("Silent partial runs",
         "A conditional trigger waits for all upstream jobs; one fails, the downstream job never starts, and nobody notices because the workflow is not marked as an alert.",
         "Send Glue job state changes from EventBridge to an alert channel. Add an explicit on-failure trigger that notifies the owner."),
        ("Lost or doubled events",
         "Glue does not guarantee delivery of EventBridge events and does not remove duplicates, so a file can be processed twice or not at all.",
         "Make every job idempotent and keep a file log of what was processed. Reconcile counts against the source each day."),
        ("Failed batch is not retried",
         "With event batching, if the run started by a batch fails, those events are not retried; a new run starts only when the next batch arrives.",
         "Record which files each run covered and replay them with a manual run after a failure."),
        ("Large graphs become slow and fragile",
         "AWS recommends keeping a workflow to 100 or fewer jobs, crawlers and triggers combined. Large graphs are hard to read and slow to load.",
         "Split by subject area. Better, move orchestration to Lakeflow Jobs during the migration."),
        ("Crawler schema drift",
         "A crawler sees a new column or a changed type and changes the table; the next job in the workflow breaks.",
         "Set the crawler to log rather than update on schema change, or drop crawlers and let the job write the table definition."),
        ("Changes made by hand in the console",
         "Someone edits a trigger in production; the change is not in Git, and the next deployment silently reverses it.",
         "Define workflows in CloudFormation, CDK or Terraform and block console edits in production with IAM."),
        ("Two orchestrators during migration",
         "Some subjects run in Glue Workflows and some in Lakeflow Jobs; a gold table depends on both and runs before its input is ready.",
         "Use a table-update or file-arrival trigger in Lakeflow Jobs on the Glue output, so the dependency is on data, not on a clock."),
    ],
    "compare": [
        ("Databricks Lakeflow Jobs",
         "The work runs in Databricks. It is the reference orchestrator: tasks, triggers, retries, alerts and run history in system tables, deployed with Asset Bundles.",
         "Never on this platform; Glue Workflows only make sense if all the work is Glue jobs."),
        ("Amazon EventBridge Scheduler and rules",
         "You need to start a mover or a Databricks job on a schedule or when an AWS event happens, with no graph.",
         "You need several Glue jobs in a fixed order with shared run properties."),
        ("AWS Step Functions",
         "A flow crosses several AWS services, such as starting an AppFlow flow, waiting, calling a Lambda and then a Databricks job.",
         "Everything is a Glue job or crawler and you want the Glue console view."),
        ("Amazon MWAA (managed Airflow)",
         "The company already runs Airflow and orchestrates many systems beyond AWS and Databricks.",
         "You want nothing to operate and only chain a few Glue jobs."),
        ("Azure Data Factory pipelines or Google Cloud Composer",
         "The platform is on Azure or Google Cloud; these are the closest equivalents there.",
         "Your data and accounts are on AWS."),
    ],
    "cost": {
        "model": ("Glue Workflows and triggers carry no separate charge. You pay for what they start: Glue job DPU-hours, crawler DPU-hours "
                  "and Data Catalog requests and storage, at the list prices for your region. EventBridge events that start workflows are "
                  "billed by EventBridge. So the cost of a workflow is the cost of its jobs and crawlers, plus the cost of any reruns."),
        "drivers": [
            "The Glue jobs and crawlers in the graph, which are the whole bill.",
            "Crawlers that rescan full buckets on every run instead of only new folders.",
            "Reruns of a whole workflow after a late failure, when resuming from the failed node would do.",
            "Event batching set to one event per run, which starts a full run for every file.",
        ],
        "traps": [
            "Thinking orchestration is free because the workflow has no line on the bill; the jobs it starts are the cost.",
            "Running the old Glue workflow and the new Databricks pipeline in parallel for longer than the agreed two weeks.",
            "Scheduled triggers left on in dev and test accounts after the team stopped using them.",
            "Crawlers kept only to refresh a table nobody queries any more.",
        ],
    },
    "security": [
        "Each job and crawler in a workflow runs with its own IAM role; the workflow itself does not grant access. Keep roles per subject, not one powerful shared role.",
        "Control who can create, change or start workflows and triggers with IAM actions such as glue:StartWorkflowRun and glue:UpdateTrigger, and allow changes only from the deployment pipeline in production.",
        "An EventBridge start trigger needs a role EventBridge can assume to call Glue; scope it to that one workflow.",
        "Run properties are visible to anyone who can read the run; never put passwords or tokens in them. Use Secrets Manager.",
        "CloudTrail records workflow and trigger changes and starts, which answers who changed a schedule and when.",
    ],
    "monitor": [
        ("Glue Workflow Run Status Change events in EventBridge", "Whether each workflow run completed, and when; the basis for alerts."),
        ("Glue Job State Change events (FAILED, TIMEOUT)", "Which node in the graph failed, so the owner can fix and resume from there."),
        ("Workflow run statistics", "Counts of total, running, succeeded, failed and stopped actions per run, from GetWorkflowRun."),
        ("Time from start trigger to last job end", "End-to-end duration against the time the business needs the data."),
        ("Crawler run time and tables changed", "Crawlers that slow down or change schemas unexpectedly."),
    ],
    "limits": [
        ("Workflows per account", "1,000 by default per region; adjustable."),
        ("Triggers per account", "1,000 by default per region; adjustable."),
        ("Jobs started by one trigger", "50 by default; adjustable."),
        ("Size of one workflow", "AWS recommends 100 or fewer jobs, crawlers and triggers combined."),
        ("EventBridge batching", "Batch size 1 to 100 events, window 1 to 900 seconds; default window 15 minutes."),
        ("Start triggers", "One start trigger per workflow, and a trigger can belong to only one workflow."),
    ],
    "decisions": [
        ("New pipelines on the AWS and Databricks platform",
         "Lakeflow Jobs for all Databricks work; EventBridge for AWS-side triggers",
         "Drop Glue Workflows: the work is not in Glue, so its orchestrator has nothing to run."),
        ("Thirty existing Glue workflows feeding Athena reports",
         "Leave them running until each subject's Databricks pipeline reconciles, then disable and delete the workflow",
         "Keep if you have it, for the migration window only; do not add new nodes to them."),
        ("A gold table needs one Glue output and one Databricks output during migration",
         "A table-update trigger in Lakeflow Jobs on the Glue output table",
         "Pursue with care: depend on data arrival, not on two clocks in two tools."),
        ("A team proposes blueprints to generate many similar pipelines",
         "The metadata-driven framework in Databricks, driven by the config tables",
         "Drop blueprints: one framework in one place, with lineage and quality results tied to the run id."),
    ],
    "faq": [
        ("Is AWS Glue Workflows deprecated?",
         "No. AWS has not announced a retirement, and it can still start from EventBridge events with batching. The Drop verdict here is about fit: on a platform where Databricks does the processing, Glue Workflows have nothing to orchestrate."),
        ("Glue Workflows or Step Functions?",
         "Glue Workflows only run Glue jobs and crawlers. Step Functions can call over two hundred AWS services and any HTTPS API, with branching, loops and error handling. If the flow touches anything beyond Glue, Step Functions is the better AWS-native choice."),
        ("Can a Glue workflow start a Databricks job?",
         "Only indirectly, by running a Glue Python shell job that calls the Databricks Jobs API. That adds a job to maintain and pay for. EventBridge or Lakeflow Jobs triggers do the same thing more simply."),
        ("How do I migrate Glue Workflows to Databricks?",
         "Move them with their jobs. Rebuild each subject's jobs as Databricks pipelines, express the order as tasks in a Lakeflow Job generated from metadata, run old and new side by side for two weeks until counts and sums reconcile, then disable the Glue workflow."),
        ("Do Glue Workflows cost extra?",
         "No. Workflows and triggers are free; you pay for the Glue jobs, crawlers and catalog use they start."),
    ],
    "sources": [
        ("AWS docs: Overview of workflows in AWS Glue", "https://docs.aws.amazon.com/glue/latest/dg/workflows_overview.html"),
        ("AWS docs: Starting a workflow with an Amazon EventBridge event", "https://docs.aws.amazon.com/glue/latest/dg/starting-workflow-eventbridge.html"),
        ("AWS docs: Blueprint and workflow restrictions", "https://docs.aws.amazon.com/glue/latest/dg/blueprint_workflow_restrictions.html"),
        ("AWS docs: AWS Glue endpoints and quotas", "https://docs.aws.amazon.com/general/latest/gr/glue.html"),
        ("AWS docs: Triggers API", "https://docs.aws.amazon.com/glue/latest/dg/aws-glue-api-jobs-trigger.html"),
    ],
    "related": [
        ("Data platform on AWS and Databricks", "/learn/data-platform-architecture/aws-databricks/"),
        ("AWS Glue ETL jobs", "svc:glue-etl"),
        ("AWS Step Functions", "svc:step-functions"),
        ("Amazon MWAA", "svc:mwaa"),
        ("Amazon EventBridge", "svc:eventbridge"),
    ],
}
