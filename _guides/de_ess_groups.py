"""Classify every corpus backlog item by hop (where in the flow), phase (when) and scope (how often it repeats).

Agreed 23 Nov 2026: the corpus is organised by phase and hop (Discovery, Source to Land, Land to Bronze, Bronze to Silver,
Silver to Gold, Gold to Semantic, Semantic to Consumption, ...). Common work is done once; some work repeats per source,
per dataset or per data product. Tags are guidance: the owner edits them here.
"""
HOPS = [
    ("discovery", "Discovery", "Everything to learn and decide before design: the full list of discovery activities.", "Mostly once; source and dataset items repeat for each source and dataset."),
    ("setup", "Project set-up and governance", "Team, change control, status, scope and the MVP plan after discovery.", "Once for the project."),
    ("foundation", "Architecture and data foundation", "Architecture decisions, environments, access, metadata, CI/CD, orchestration, logging, standards.", "Once for the platform, then reused by every dataset."),
    ("build", "Build practices", "Standards, branching, CI/CD, test data, Done checks, demos.", "Once for the platform."),
    ("h1", "Source to Land", "Getting data out of each source system into the landing area: access, connectivity, extract method, schedule, contracts, change detection.", "Repeats per source system."),
    ("h2", "Land to Bronze", "Landing to raw tables: raw design, counts, safe reruns, late and failed loads, retention.", "Repeats per dataset."),
    ("h3", "Bronze to Silver", "Cleaning: identity, rules, quality checks, rejects, late and corrected records, history and SCD2.", "Repeats per dataset."),
    ("h4", "Silver to Gold", "Modelling: facts, dimensions, measures, conformed dimensions, performance, build rules.", "Repeats per data product."),
    ("h5", "Gold to Semantic", "Metric catalogue, definitions, access rules, KPI design, change notice.", "Repeats per data product."),
    ("h6", "Semantic to Consumption", "Reports and users: access, acceptance, training, adoption, retiring the old report.", "Repeats per data product."),
    ("hx", "Historical load", "One-time history: sources, formats, strategy, trial, reconciliation, hand-over to incremental.", "Once per dataset, one time."),
    ("e2e", "End to end: reconciliation, lineage, testing", "Work that spans hops: reconciliation, lineage, orchestration, the test levels.", "Strategy once; execution per data product."),
    ("ops", "Operations and run", "Quality monitoring, security, cost, runbook, alerts, support, recovery drills.", "Set up once; reviewed per data product."),
    ("reviews", "Reviews and sign-offs", "Design reviews, vendor reviews, readiness review, sign-off register.", "Once per gate."),
    ("golive", "Go-live and hand-over", "Cut-over, first production reconciliation, hypercare, hand-over pack, benefits.", "Once per MVP."),
]
SCOPES = [("project", "Once for the project", "Done one time for the whole project.", "Scope, team, change control, business case."),
          ("platform", "Once for the platform (common)", "Built once, reused by every source and dataset.", "Environments, CI/CD, access model, metadata store, standards."),
          ("source", "Per source system", "Repeats for each source system.", "Access, extract method, change and delete behaviour, contract."),
          ("dataset", "Per dataset (table)", "Repeats for each table or file.", "Profile, keys, quality rules, SCD2, raw design, history load."),
          ("product", "Per data product (MVP)", "Repeats for each report, model or product delivered.", "KPIs, facts, metrics, acceptance, adoption, test evidence.")]
PHASES = ["Discover", "Design", "Build", "Test", "Run and close"]

DISC_EXTRA = {"PRJ-10", "PRJ-11", "DSC-06", "DSC-13", "KPI-07", "KPI-08", "KPI-09", "PRO-06"} | {f"NFR-0{i}" for i in range(1, 10)}
HOP_OVERRIDE = {
    "MET-04": "h1", "MET-05": "e2e", "MET-09": "e2e", "MET-10": "ops", "DSN-01": "e2e", "DSN-02": "h1", "DSN-03": "h2", "DSN-04": "h3", "DSN-05": "h4", "DSN-06": "h5", "DSN-07": "h3", "DSN-08": "h3",
    "DSN-09": "foundation", "DSN-10": "build", "DSN-11": "foundation", "DSN-12": "foundation", "DSN-13": "foundation", "DSN-14": "e2e", "DSN-15": "reviews",
    "BLD-06": "e2e", "BLD-11": "setup", "BLD-15": "setup", "LND-03": "h2", "LND-04": "h2", "LND-05": "h2", "LND-07": "h1", "LND-09": "hx", "LND-10": "h2", "HST-06": "h4",
    "RCN-05": "h1", "RCN-06": "h3", "RCN-07": "h4", "RCN-08": "h6", "MNG-04": "h5", "CON-04": "h6",
}
PREFIX_HOP = {"PRJ": "setup", "DSC": "setup", "ARC": "foundation", "FND": "foundation", "MET": "foundation", "DSN": "e2e", "BLD": "build", "LND": "h2", "HLD": "hx", "CLN": "h3", "HST": "h3", "MDL": "h4",
              "MNG": "h5", "KPI": "h5", "RCN": "e2e", "CON": "h6", "TST": "e2e", "QLT": "ops", "COS": "ops", "SEC": "ops", "RUN": "ops", "REV": "reviews", "GLV": "golive", "SRC": "h1", "PRO": "h3", "NFR": "setup"}
SCOPE_OVERRIDE = {"LND-01": "source", "LND-06": "source", "LND-07": "source", "LND-08": "source", "SRC-12": "product", "SRC-13": "source", "SRC-11": "source", "RCN-05": "dataset", "RCN-06": "dataset", "RCN-07": "dataset",
                  "DSN-06": "product", "DSN-09": "platform", "DSN-10": "platform", "DSN-11": "platform", "DSN-12": "platform", "DSN-13": "platform", "DSN-14": "product", "DSN-15": "project", "MET-03": "dataset", "MET-06": "dataset",
                  "MET-07": "source", "MET-04": "source", "MET-10": "platform", "BLD-06": "dataset", "BLD-07": "platform", "BLD-10": "platform", "BLD-11": "project", "BLD-13": "product", "BLD-15": "project",
                  "TST-01": "platform", "TST-04": "platform", "TST-12": "platform", "TST-02": "product", "TST-03": "product", "TST-13": "product", "TST-14": "product", "TST-15": "product", "QLT-01": "dataset", "QLT-02": "dataset", "QLT-03": "product",
                  "COS-03": "product", "CON-08": "product", "NFR-04": "dataset", "NFR-07": "project", "PRO-06": "dataset", "KPI-07": "product", "HST-10": "dataset"}
PREFIX_SCOPE = {"PRJ": "project", "DSC": "project", "NFR": "project", "REV": "project", "GLV": "project", "ARC": "platform", "FND": "platform", "MET": "platform", "BLD": "platform", "RUN": "platform", "SEC": "platform",
                "COS": "platform", "QLT": "platform", "SRC": "source", "PRO": "dataset", "LND": "dataset", "HLD": "dataset", "CLN": "dataset", "HST": "dataset", "DSN": "dataset", "MDL": "product", "MNG": "product",
                "KPI": "product", "CON": "product", "RCN": "product", "TST": "product"}
THEME = {"PRJ": "Project, scope, plan and stakeholders", "DSC": "Discovery document: sections that had no item", "NFR": "Non-functional requirements", "SRC": "Sources: understand each source", "PRO": "Profiling",
         "KPI": "KPI understanding", "HLD": "Historical load: what is needed", "LND": "Loading needs: freshness, history, change", "CLN": "Cleaning needs: identity and history", "MDL": "Modelling needs: grain and reconciliation",
         "CON": "Consumers and downstream", "SEC": "Security and privacy", "ARC": "Architecture options", "RCN": "Reconciliation approach", "HST": "History needs", "REV": "Reviews planned", "MNG": "Meaning", "DSN": "Design",
         "TST": "Test", "COS": "Cost", "RUN": "Run", "QLT": "Quality", "MET": "Metadata", "FND": "Foundation", "BLD": "Build", "GLV": "Go-live"}


def classify(item):
    iid, stage = item[0], item[5]
    pre = iid[:3]
    hop = "discovery" if (stage <= 3 or iid in DISC_EXTRA) else HOP_OVERRIDE.get(iid, PREFIX_HOP[pre])
    phase = "Discover" if hop == "discovery" else ("Design" if stage == 4 else "Build" if stage <= 6 else "Test" if stage == 7 else "Run and close")
    scope = SCOPE_OVERRIDE.get(iid, PREFIX_SCOPE[pre])
    return hop, phase, scope, THEME[pre]
