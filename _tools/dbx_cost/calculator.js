/* Databricks data platform cost calculator (AWS). Plain JS, no libraries.
 * Prices come from window.DBX_PRICES (built from _tools/dbx_cost/prices.json).
 * Model: every workload is measured in "work units" = classic, non-Photon DBU-hours. Each hop turns its
 * data volumes into work units with a published-in-the-page rate; the chosen compute (serverless or
 * classic) turns work units into dollars. Hidden costs are their own lines, tagged to the hop they belong to.
 */
(function () {
  "use strict";
  var P = window.DBX_PRICES;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var HOURS = 730, DAYS = 30.4;

  // ---------------------------------------------------------------- presets
  var PRESETS = {
    small:   {label: "Small: about 100 GB", n_small: 50,   n_big: 5,   n_vbig: 0,   n_huge: 0,  wh_size: "X-Small", engineers: 4,  bi_users: 30},
    big:     {label: "Big: about 30 TB",    n_small: 150,  n_big: 40,  n_vbig: 5,   n_huge: 0,  wh_size: "Small",   engineers: 10, bi_users: 150},
    verybig: {label: "Very big: about 400 TB", n_small: 400, n_big: 150, n_vbig: 30, n_huge: 2, wh_size: "Medium", engineers: 25, bi_users: 600},
    huge:    {label: "Very, very big: about 3 PB", n_small: 1000, n_big: 500, n_vbig: 150, n_huge: 20, wh_size: "Large", engineers: 60, bi_users: 2500}
  };

  // ---------------------------------------------------------------- parameters
  // group: quick | data | h1 | h2 | h3 | h4 | h5 | stream | across | classic | rates
  // impact: H (moves the bill a lot) | M | L ; adv: shown only in expert mode
  var SPEC = [
    {id: "tier", g: "quick", label: "Plan", type: "select", opts: [["premium", "Premium"], ["enterprise", "Enterprise"]], def: "premium", impact: "M",
      help: "Enterprise adds security and compliance features and costs more per DBU for jobs and notebooks. SQL Serverless costs the same on both."},
    {id: "compute", g: "quick", label: "Compute for pipelines", type: "select", opts: [["serverless", "Serverless"], ["classic", "Classic (your EC2 machines)"]], def: "serverless", impact: "H",
      help: "Serverless: one price per DBU that includes the machines, no start-up wait, no idle clusters. Classic: a lower DBU price plus the EC2 bill, start-up time and network costs."},
    {id: "size", g: "quick", label: "How much data", type: "select", opts: [["small", "Small: about 100 GB"], ["big", "Big: about 30 TB"], ["verybig", "Very big: about 400 TB"], ["huge", "Very, very big: about 3 PB"]], def: "big", impact: "H",
      help: "Sets a typical mix of small, big, very big and huge tables. Change the mix under 'Your data'."},
    {id: "runs", g: "quick", label: "Batch runs per day", type: "select", opts: [["1", "Once a day"], ["4", "4 times a day"], ["24", "Every hour"], ["96", "Every 15 minutes"]], def: "1", impact: "H",
      help: "Every run pays a fixed overhead per table, and merges rewrite some of the same files again. More runs, fresher data, bigger bill."},
    {id: "streaming_pct", g: "quick", label: "Tables on the streaming lane", type: "select", opts: [["0", "None (all batch)"], ["10", "10% of tables"], ["25", "25%"], ["50", "50%"], ["100", "All tables"]], def: "0", impact: "H",
      help: "Streaming tables move through the same layers within seconds or minutes, on compute that is always on (or wakes very often)."},
    {id: "bi_users", g: "quick", label: "People using dashboards", type: "number", def: 150, min: 0, impact: "H",
      help: "Drives how big the SQL warehouse must be and how long it runs."},
    {id: "ai", g: "quick", label: "AI on the data", type: "select", opts: [["none", "None"], ["genie", "Genie (ask in plain words)"], ["agents", "Agents with retrieval"], ["both", "Both"]], def: "none", impact: "M",
      help: "Genie runs its queries on your SQL warehouse. Agents add model tokens, a vector search endpoint and tool queries."},
    {id: "discount", g: "quick", label: "Your negotiated discount on DBUs (%)", type: "number", def: 0, min: 0, max: 60, impact: "M",
      help: "Committed-use contracts discount the DBU price. List prices are used when this is 0."},

    // your data: four table classes
    {id: "n_small", g: "data", label: "Small tables (about 1 GB each)", type: "number", def: 150, min: 0, impact: "L", help: "Reference data, lookups, small app tables."},
    {id: "n_big", g: "data", label: "Big tables (about 100 GB each)", type: "number", def: 40, min: 0, impact: "M", help: "Customers, orders, transactions for a mid-size business."},
    {id: "n_vbig", g: "data", label: "Very big tables (about 5 TB each)", type: "number", def: 5, min: 0, impact: "H", help: "Events, clickstream, years of transactions."},
    {id: "n_huge", g: "data", label: "Huge tables (about 100 TB each)", type: "number", def: 0, min: 0, impact: "H", help: "Telemetry, IoT, ad impressions. A few of these dominate everything."},
    {id: "sz_small", g: "data", label: "Small table size (GB)", type: "number", def: 1, adv: true, impact: "L"},
    {id: "sz_big", g: "data", label: "Big table size (GB)", type: "number", def: 100, adv: true, impact: "M"},
    {id: "sz_vbig", g: "data", label: "Very big table size (GB)", type: "number", def: 5000, adv: true, impact: "H"},
    {id: "sz_huge", g: "data", label: "Huge table size (GB)", type: "number", def: 100000, adv: true, impact: "H"},
    {id: "ch_small", g: "data", label: "Small tables: % changed per day", type: "number", def: 5, adv: true, impact: "L"},
    {id: "ch_big", g: "data", label: "Big tables: % changed per day", type: "number", def: 2, adv: true, impact: "M"},
    {id: "ch_vbig", g: "data", label: "Very big tables: % changed per day", type: "number", def: 1, adv: true, impact: "H"},
    {id: "ch_huge", g: "data", label: "Huge tables: % changed per day", type: "number", def: 0.5, adv: true, impact: "H"},

    // H1 sources to bronze
    {id: "ingest", g: "h1", label: "How data comes in", type: "select", opts: [["files", "Files (Auto Loader)"], ["connect", "Managed connectors (Lakeflow Connect)"], ["cdc", "Change data capture from databases"]], def: "files", impact: "M",
      help: "Parsing files is cheapest per GB; managed connectors and CDC do more work per row but catch deletes and save you building extractors."},
    {id: "engine", g: "h1", label: "Pipelines built with", type: "select", opts: [["jobs", "Jobs (notebooks, SQL, dbt)"], ["pipelines", "Declarative pipelines"]], def: "jobs", impact: "M",
      help: "On classic compute, declarative pipelines cost more per DBU (Core, Pro or Advanced) but handle CDC, quality rules and retries for you. On serverless the rate is the same."},
    {id: "edition", g: "h1", label: "Declarative pipelines edition (classic)", type: "select", opts: [["dlt_core", "Core"], ["dlt_pro", "Pro (CDC)"], ["dlt_advanced", "Advanced (CDC + quality rules)"]], def: "dlt_pro", adv: true, impact: "M"},
    {id: "landing_days", g: "h1", label: "Keep landing files for (days)", type: "number", def: 7, min: 0, impact: "L", help: "Long enough to replay a bad load. Longer is just storage."},
    {id: "bronze_days", g: "h1", label: "Keep bronze history for (days)", type: "number", def: 365, min: 0, impact: "M", help: "Bronze is append-only: every change ever received is kept. This is where storage quietly grows."},
    {id: "tables_per_job", g: "h1", label: "Tables per job or pipeline", type: "number", def: 25, min: 1, adv: true, impact: "L"},
    {id: "files_per_run", g: "h1", label: "Files written per table per run", type: "number", def: 4, min: 1, adv: true, impact: "L", help: "Drives storage request charges and the small-files problem."},

    // H2 bronze to silver
    {id: "layout", g: "h2", label: "Table file layout", type: "select", opts: [["good", "Good: liquid clustering, deletion vectors"], ["poor", "Poor: unclustered, no compaction"]], def: "good", impact: "H",
      help: "A merge has to rewrite every file that holds a changed row. With good layout it touches a few files; with poor layout it rewrites a large part of the table on every run."},
    {id: "scd2_pct", g: "h2", label: "Tables that keep full history (SCD Type 2), %", type: "number", def: 20, min: 0, max: 100, impact: "M", help: "History-keeping merges do about a third more work."},
    {id: "dq_on", g: "h2", label: "Quality rules on every load", type: "select", opts: [["yes", "Yes"], ["no", "No"]], def: "yes", impact: "L", help: "About 10% more work. Not having them is far more expensive, just not on this bill."},

    // H3 silver to gold
    {id: "gold_refresh", g: "h3", label: "How gold tables refresh", type: "select", opts: [["incremental", "Incrementally (materialized views, merges)"], ["full", "Full rebuild every run"]], def: "incremental", impact: "H",
      help: "A full rebuild reads all of silver on every run. Incremental refresh reads only what changed."},
    {id: "gold_pct", g: "h3", label: "Gold size as % of silver", type: "number", def: 30, min: 0, adv: true, impact: "L"},
    {id: "gold_read_pct", g: "h3", label: "Share of silver read by a full rebuild, %", type: "number", def: 60, min: 0, max: 100, adv: true, impact: "M"},

    // H4 gold to semantic
    {id: "metric_views", g: "h4", label: "Metric views (semantic layer)", type: "number", def: 10, min: 0, impact: "L", help: "Definitions cost nothing; the queries through them run on the warehouse (hop 5)."},
    {id: "mv_materialized", g: "h4", label: "Pre-computed aggregates behind metric views", type: "select", opts: [["yes", "Yes"], ["no", "No"]], def: "yes", impact: "M",
      help: "Pre-computed aggregates cost a small refresh each run but make every dashboard query cheaper (smaller warehouse)."},

    // H5 semantic to experiences
    {id: "wh_type", g: "h5", label: "SQL warehouse type", type: "select", opts: [["serverless", "Serverless"], ["pro", "Pro (classic machines)"], ["classic", "Classic"]], def: "serverless", impact: "M",
      help: "Serverless starts in seconds and stops quickly; Pro and Classic have a lower DBU price but add EC2 and take minutes to start, so they are left running longer."},
    {id: "wh_size", g: "h5", label: "Warehouse size", type: "select", opts: [["auto", "Pick from data size"], ["2X-Small", "2X-Small"], ["X-Small", "X-Small"], ["Small", "Small"], ["Medium", "Medium"], ["Large", "Large"], ["X-Large", "X-Large"], ["2X-Large", "2X-Large"]], def: "auto", impact: "H",
      help: "Each size step roughly doubles the DBUs per hour."},
    {id: "peak_pct", g: "h5", label: "Users active at the busiest time, %", type: "number", def: 20, min: 1, max: 100, impact: "M"},
    {id: "biz_hours", g: "h5", label: "Business hours per day", type: "number", def: 10, min: 1, max: 24, impact: "M"},
    {id: "workdays", g: "h5", label: "Working days per month", type: "number", def: 22, min: 1, max: 31, adv: true, impact: "L"},
    {id: "dashboards", g: "h5", label: "Dashboards with scheduled refresh", type: "number", def: 30, min: 0, impact: "L"},
    {id: "refresh", g: "h5", label: "Scheduled dashboard refresh", type: "select", opts: [["none", "None"], ["daily", "Daily"], ["hourly", "Hourly"], ["15min", "Every 15 minutes"]], def: "hourly", impact: "M",
      help: "Each scheduled refresh outside business hours wakes the warehouse, which then stays up until auto-stop."},
    {id: "refresh_247", g: "h5", label: "Scheduled refreshes run around the clock", type: "check", def: false, impact: "H",
      help: "A refresh every 15 minutes with a 10-minute auto-stop means the warehouse never stops: 730 hours a month."},
    {id: "auto_stop", g: "h5", label: "Warehouse auto-stop (minutes)", type: "number", def: 10, min: 1, impact: "M"},
    {id: "realtime", g: "h5", label: "Real-time dashboards or APIs (warehouse always on)", type: "check", def: false, impact: "H",
      help: "Real-time analytics needs something answering 24x7. Here: one warehouse cluster kept on all month."},
    {id: "genie_q", g: "h5", label: "Genie questions per user per day", type: "number", def: 2, min: 0, adv: true, impact: "L"},
    {id: "agent_q", g: "h5", label: "Agent questions per day", type: "number", def: 500, min: 0, impact: "M"},
    {id: "vs_units", g: "h5", label: "Vector search endpoint units", type: "number", def: 1, min: 0, adv: true, impact: "L"},

    // streaming lane
    {id: "trigger", g: "stream", label: "Streaming runs", type: "select", opts: [["continuous", "Continuously (seconds)"], ["5", "Every 5 minutes"], ["15", "Every 15 minutes"]], def: "continuous", impact: "H",
      help: "Continuous gives seconds of delay and never stops. Small, frequent triggers give minutes of delay and can be much cheaper."},
    {id: "st_per_pipe", g: "stream", label: "Streaming tables per pipeline", type: "number", def: 20, min: 1, impact: "M", help: "Each pipeline is a piece of always-on compute; packing tables together saves money."},
    {id: "st_dbu_h", g: "stream", label: "DBUs per hour for one streaming pipeline", type: "number", def: 4, min: 0.5, adv: true, impact: "H"},

    // across the platform
    {id: "engineers", g: "across", label: "Engineers working in notebooks", type: "number", def: 10, min: 0, impact: "M"},
    {id: "eng_hours", g: "across", label: "Notebook hours per engineer per day", type: "number", def: 4, min: 0, adv: true, impact: "M"},
    {id: "notebooks", g: "across", label: "Notebook compute", type: "select", opts: [["serverless", "Serverless notebooks"], ["classic", "All-purpose clusters"]], def: "serverless", adv: true, impact: "M"},
    {id: "autoterm", g: "across", label: "All-purpose auto-termination (minutes)", type: "number", def: 60, min: 10, adv: true, impact: "M", help: "Idle time before a cluster stops. Engineers stop typing; the cluster keeps billing."},
    {id: "devtest_pct", g: "across", label: "Dev and test, as % of production compute", type: "number", def: 30, min: 0, max: 200, impact: "H", help: "Lower environments are rarely free. 20-40% is common; above 50% usually means something is left running."},
    {id: "retry_pct", g: "across", label: "Failed runs and retries, % of pipeline compute", type: "number", def: 5, min: 0, impact: "M"},
    {id: "backfills", g: "across", label: "Full backfills per year", type: "number", def: 2, min: 0, impact: "M", help: "Rebuilding history after a logic change re-reads everything."},
    {id: "maint", g: "across", label: "Table maintenance", type: "select", opts: [["predictive", "Predictive optimization (automatic)"], ["manual", "Our own OPTIMIZE and VACUUM jobs"], ["none", "None"]], def: "predictive", impact: "M",
      help: "Compaction and clean-up cost compute, but skipping them makes every read slower and storage larger."},
    {id: "tt_days", g: "across", label: "Table history kept for (days, time travel)", type: "number", def: 7, min: 0, impact: "M", help: "Old file versions stay in storage until VACUUM removes them."},
    {id: "teams", g: "across", label: "Teams with their own monitoring dashboards", type: "number", def: 3, min: 0, impact: "M", help: "Observability by teams: system tables and cost dashboards, refreshed on their own warehouse."},
    {id: "mon_refresh", g: "across", label: "Monitoring dashboards refresh", type: "select", opts: [["hourly247", "Hourly, around the clock"], ["hourlybiz", "Hourly, business hours"], ["daily", "Daily"]], def: "hourly247", impact: "M"},
    {id: "dq_monitors", g: "across", label: "Tables with data quality monitoring", type: "number", def: 20, min: 0, impact: "L"},
    {id: "egress_gb", g: "across", label: "Data sent out to other clouds or the internet (GB/month)", type: "number", def: 100, min: 0, adv: true, impact: "L"},

    // classic only
    {id: "instance", g: "classic", label: "Worker machine type", type: "select", opts: Object.keys(P.instances).map(function (k) { return [k, k + " (" + P.instances[k].vcpu + " vCPU, " + P.instances[k].mem_gb + " GB)"]; }), def: "m5d.2xlarge", impact: "M"},
    {id: "spot", g: "classic", label: "Workers on spot machines", type: "check", def: false, impact: "M", help: "Spot machines cost about 60% less but can be taken back; fine for most batch jobs."},
    {id: "photon", g: "classic", label: "Photon on classic jobs", type: "check", def: false, impact: "M", help: "Photon raises the DBU rate about 2.5x but often runs 2-3x faster; the net effect depends on the workload."},
    {id: "photon_speedup", g: "classic", label: "Photon speed-up", type: "number", def: 2.2, min: 1, adv: true, impact: "M"},
    {id: "s3_endpoint", g: "classic", label: "S3 gateway endpoint set up", type: "check", def: true, impact: "H",
      help: "Without it, every byte between your clusters and S3 goes through the NAT gateway at $0.045 per GB. A classic hidden cost."},
    {id: "nat_gw", g: "classic", label: "NAT gateways", type: "number", def: 2, min: 0, adv: true, impact: "L"},
    {id: "external_pct", g: "classic", label: "Share of ingested data coming from outside AWS, %", type: "number", def: 30, min: 0, max: 100, adv: true, impact: "L"},
    {id: "start_min", g: "classic", label: "Cluster start-up time (minutes)", type: "number", def: 5, min: 0, adv: true, impact: "M", help: "You pay for EC2 while a classic cluster starts."},
    {id: "sl_mode", g: "classic", label: "Serverless performance mode", type: "select", opts: [["performance", "Performance optimized"], ["standard", "Standard (cheaper, slower start)"]], def: "performance", impact: "M",
      help: "Standard mode suits scheduled jobs that don't need to start within a minute."},

    // work rates
    {id: "k_files", g: "rates", label: "Ingest files: work units per GB", type: "number", def: 0.04, adv: true, impact: "M"},
    {id: "k_connect", g: "rates", label: "Ingest via connectors: work units per GB", type: "number", def: 0.06, adv: true, impact: "M"},
    {id: "k_cdc", g: "rates", label: "Ingest via CDC: work units per GB", type: "number", def: 0.05, adv: true, impact: "M"},
    {id: "k_merge", g: "rates", label: "Merge: work units per changed GB", type: "number", def: 0.08, adv: true, impact: "M"},
    {id: "k_rewrite", g: "rates", label: "Merge: work units per GB of files rewritten", type: "number", def: 0.03, adv: true, impact: "M"},
    {id: "k_touch_good", g: "rates", label: "Share of table rewritten per daily merge, good layout (%)", type: "number", def: 2, adv: true, impact: "H"},
    {id: "k_touch_poor", g: "rates", label: "Share of table rewritten per daily merge, poor layout (%)", type: "number", def: 20, adv: true, impact: "H"},
    {id: "k_gold_inc", g: "rates", label: "Gold incremental: work units per changed GB", type: "number", def: 0.10, adv: true, impact: "M"},
    {id: "k_gold_full", g: "rates", label: "Gold full rebuild: work units per GB read", type: "number", def: 0.02, adv: true, impact: "M"},
    {id: "k_run", g: "rates", label: "Fixed overhead per table per run (work units)", type: "number", def: 0.01, adv: true, impact: "M"}
  ];
  var GROUPS = [
    ["data", "Your data", "The mix of table sizes. Huge tables dominate the bill, so it matters more how many big ones you have than how many tables in total."],
    ["h1", "Hop 1 · Sources to bronze", "Getting data in, exactly as it arrived: landing files and bronze."],
    ["h2", "Hop 2 · Bronze to silver", "Cleaning and merging into one row per real thing. Merges on big tables are usually the biggest pipeline cost."],
    ["h3", "Hop 3 · Silver to gold", "Shaping tables for a use. Full rebuilds versus incremental refresh is the big lever."],
    ["h4", "Hop 4 · Gold to semantic", "Metric definitions, and the pre-computed aggregates that make queries cheap."],
    ["h5", "Hop 5 · Semantic to experiences", "Dashboards, ad-hoc questions, Genie, agents and real-time serving, on SQL warehouses and model endpoints."],
    ["stream", "Streaming lane", "The same layers at a second speed, for the tables that need seconds or minutes."],
    ["across", "Across the platform", "People, environments, maintenance, observability and the other costs that belong to no single hop."],
    ["classic", "Classic compute and network", "Only matters when pipelines or warehouses run on your own EC2 machines."],
    ["rates", "Work rates (expert)", "How much work each GB costs. Our calibrated defaults; replace them with numbers from your own system tables."]
  ];
  var HOPS = [["H1", "Sources to bronze"], ["H2", "Bronze to silver"], ["H3", "Silver to gold"], ["H4", "Gold to semantic"], ["H5", "Semantic to experiences"], ["S", "Streaming lane"], ["X", "Across the platform"]];
  var KINDS = [["dbu", "Databricks (DBUs)"], ["vm", "AWS machines (EC2)"], ["storage", "Storage (S3)"], ["network", "Network"], ["ai", "AI (tokens, vector search)"]];
  var HOP_COLOR = {H1: "#F5E3D3", H2: "#DDE1E7", H3: "#FFE7A3", H4: "#CDEBD8", H5: "#CFE3F2", S: "#E3D6F3", X: "#F3D3DF"};

  var state = {};
  SPEC.forEach(function (s) { state[s.id] = s.def; });

  // ---------------------------------------------------------------- the model
  function rate(sku, st) { return P.dbu[sku][st.tier] * (1 - st.discount / 100); }

  function model(st) {
    var L = [];
    function add(hop, kind, name, usd, why, hidden) { if (usd > 0.005) L.push({hop: hop, kind: kind, name: name, usd: usd, why: why, hidden: !!hidden}); }
    var classic = st.compute === "classic";
    var inst = P.instances[st.instance];
    var photon = classic && st.photon;
    var photonMult = P.photon_dbu_multiplier.value;
    var slFactor = st.sl_mode === "standard" ? P.serverless_standard_mode_factor.value : 1;
    var vmPerDbuH = inst.usd_per_hour / inst.dbu_per_hour;          // EC2 dollars per classic DBU-hour
    var spotFactor = st.spot ? (1 - 0.6 * 0.8) : 1;                   // 80% of nodes are workers; spot about 60% off
    var classicSku = st.engine === "pipelines" ? st.edition : "jobs_classic";

    // turn work units into dollar lines (DBU and, for classic, EC2)
    function pipeline(hop, name, wu, why, hidden, skuOverride) {
      if (wu <= 0) return 0;
      var dbuUsd, vmUsd = 0, txt;
      if (classic && !skuOverride) {
        var dbuH = photon ? wu * photonMult / st.photon_speedup : wu;
        var vmH = photon ? wu / st.photon_speedup : wu;
        dbuUsd = dbuH * rate(classicSku, st);
        vmUsd = vmH * vmPerDbuH * spotFactor;
        add(hop, "dbu", name, dbuUsd, why + " " + fmtN(dbuH) + " DBU-hours a month at $" + rate(classicSku, st).toFixed(2) + " per DBU (" + P.dbu[classicSku].label + ").", hidden);
        add(hop, "vm", name + ": EC2", vmUsd, "The EC2 machines under the same work: " + fmtN(vmH) + " DBU-hours of " + st.instance + (st.spot ? ", workers on spot." : "."), hidden);
      } else {
        var sku = skuOverride || "jobs_serverless";
        var f = sku === "jobs_serverless" ? slFactor : 1;
        dbuUsd = wu * f * rate(sku, st);
        add(hop, "dbu", name, dbuUsd, why + " " + fmtN(wu * f) + " DBU-hours a month at $" + rate(sku, st).toFixed(2) + " per DBU (" + P.dbu[sku].label + ", machines included).", hidden);
      }
      return dbuUsd + vmUsd;
    }

    // ---- data volumes
    var cls = [["small", st.n_small, st.sz_small, st.ch_small], ["big", st.n_big, st.sz_big, st.ch_big], ["vbig", st.n_vbig, st.sz_vbig, st.ch_vbig], ["huge", st.n_huge, st.sz_huge, st.ch_huge]];
    var nTables = 0, totalGb = 0, changeGb = 0;
    cls.forEach(function (c) { nTables += c[1]; totalGb += c[1] * c[2]; changeGb += c[1] * c[2] * c[3] / 100; });
    var sPct = Number(st.streaming_pct) / 100;
    var batchShare = 1 - sPct;
    var runs = Number(st.runs);
    var bTables = nTables * batchShare;
    var bChangeDay = changeGb * batchShare, bTotal = totalGb * batchShare;

    // ---- H1: sources to bronze
    var kIngest = {files: st.k_files, connect: st.k_connect, cdc: st.k_cdc}[st.ingest];
    var ingestWu = bChangeDay * kIngest * DAYS + bTables * runs * st.k_run * DAYS;
    var wuPipelines = 0;
    wuPipelines += ingestWu;
    pipeline("H1", "Ingestion into bronze", ingestWu, "Reading " + fmtGb(bChangeDay) + " of new and changed data a day into bronze, " + runs + " run(s) a day over " + Math.round(bTables) + " tables.");
    var landingGb = changeGb * st.landing_days;
    var bronzeGb = totalGb + changeGb * st.bronze_days;
    add("H1", "storage", "Landing files", landingGb * P.aws.s3_gb_month.value, fmtGb(landingGb) + " of files kept " + st.landing_days + " days, at $" + P.aws.s3_gb_month.value + " per GB-month.");
    add("H1", "storage", "Bronze tables", bronzeGb * P.aws.s3_gb_month.value, "Bronze keeps every change: " + fmtGb(totalGb) + " today plus " + st.bronze_days + " days of changes = " + fmtGb(bronzeGb) + ".", true);
    var puts = nTables * runs * st.files_per_run * 3 * DAYS;           // landing, bronze, silver writes
    add("H1", "storage", "Storage requests", puts / 1000 * P.aws.s3_put_per_1000.value + puts * 10 / 1000 * P.aws.s3_get_per_1000.value,
      fmtN(puts) + " file writes a month (and about ten reads per write). Many small files make this, and every read, worse.", true);

    // ---- H2: bronze to silver
    var touch = (st.layout === "good" ? st.k_touch_good : st.k_touch_poor) / 100;
    var touchedPerDay = bTotal * touch * Math.sqrt(runs);               // more runs rewrite the same files again
    var mergeWu = (bChangeDay * st.k_merge + touchedPerDay * st.k_rewrite) * DAYS;
    mergeWu *= 1 + 0.33 * st.scd2_pct / 100;
    if (st.dq_on === "yes") mergeWu *= 1.10;
    wuPipelines += mergeWu;
    pipeline("H2", "Merges into silver", mergeWu, "Merging " + fmtGb(bChangeDay) + " of changes a day; with " + (st.layout === "good" ? "good" : "poor") + " file layout each day's merges rewrite about " + fmtGb(touchedPerDay) + " of existing files.");
    add("H2", "storage", "Silver tables", totalGb * P.aws.s3_gb_month.value, fmtGb(totalGb) + " of clean tables.");

    // ---- H3: silver to gold
    var goldWu = st.gold_refresh === "incremental"
      ? bChangeDay * st.k_gold_inc * DAYS
      : bTotal * st.gold_read_pct / 100 * st.k_gold_full * runs * DAYS;
    goldWu += bTables * 0.3 * runs * st.k_run * DAYS;
    wuPipelines += goldWu;
    pipeline("H3", "Gold refresh", goldWu, st.gold_refresh === "incremental"
      ? "Incremental refresh: only the " + fmtGb(bChangeDay) + " that changed each day flows into gold."
      : "Full rebuild: about " + fmtGb(bTotal * st.gold_read_pct / 100) + " of silver read on every one of " + runs + " run(s) a day.",
      false, st.gold_refresh === "incremental" && !classic ? "jobs_serverless" : null);
    var goldGb = totalGb * st.gold_pct / 100;
    add("H3", "storage", "Gold tables", goldGb * P.aws.s3_gb_month.value, fmtGb(goldGb) + " of gold tables.");

    // ---- H4: gold to semantic
    if (st.mv_materialized === "yes" && st.metric_views > 0) {
      var aggWu = st.metric_views * runs * 0.15 * Math.max(1, Math.log10(1 + totalGb / 1000)) * DAYS;
      pipeline("H4", "Pre-computed aggregates", aggWu, st.metric_views + " metric views with aggregates refreshed " + runs + " time(s) a day, billed at the serverless pipeline rate.", false, "jobs_serverless");
    }

    // ---- H5: semantic to experiences (SQL warehouse)
    var sizes = P.sql_warehouse_dbu_per_hour.sizes, order = Object.keys(sizes);
    var autoSize = PRESETS[st.size].wh_size;
    var size = st.wh_size === "auto" ? autoSize : st.wh_size;
    if (st.mv_materialized === "no" && st.wh_size === "auto") size = order[Math.min(order.length - 1, order.indexOf(size) + 1)];
    var whDbuH = sizes[size];
    var whSku = {serverless: "sql_serverless", pro: "sql_pro", classic: "sql_classic"}[st.wh_type];
    var whRate = rate(whSku, st);
    var whVm = st.wh_type === "serverless" ? 0 : vmPerDbuH;
    function whCost(hours, dbuH) { return hours * dbuH * (whRate + whVm); }
    var peakConc = st.bi_users * st.peak_pct / 100 * 0.5;
    var peakClusters = Math.max(1, Math.ceil(peakConc / 10));
    var avgClusters = Math.max(1, peakClusters * 0.5);
    var bizH = st.biz_hours * st.workdays;
    var stopH = (st.wh_type === "serverless" ? st.auto_stop : Math.max(st.auto_stop, 30)) / 60;
    var biH = st.bi_users > 0 ? bizH * avgClusters + st.workdays * stopH : 0;
    var whTxt = size + " " + {serverless: "serverless", pro: "Pro", classic: "Classic"}[st.wh_type] + " warehouse, " + whDbuH + " DBU per hour per cluster";
    add("H5", "dbu", "SQL warehouse: business hours", whCost(biH, whDbuH) - biH * whDbuH * whVm,
      whTxt + ". " + st.bi_users + " people, about " + Math.round(peakConc) + " queries at once at the busiest time, so " + peakClusters + " cluster(s) at peak; " + fmtN(biH) + " cluster-hours a month.");
    if (whVm) add("H5", "vm", "SQL warehouse: EC2", biH * whDbuH * whVm, "Machines under the " + st.wh_type + " warehouse.");
    var offH = HOURS - bizH, offOn = 0, offTxt = "";
    if (st.realtime) { offOn = offH; offTxt = "Real-time serving keeps one cluster on outside business hours too: " + fmtN(offH) + " hours."; }
    else if (st.refresh !== "none" && st.dashboards > 0) {
      var perDay = {daily: 1, hourly: 24, "15min": 96}[st.refresh];
      var intervalMin = 1440 / perDay;
      var offRefreshes = st.refresh_247 ? perDay * (offH / HOURS) * DAYS : 0;
      if (st.refresh_247 && intervalMin <= stopH * 60 + 2) { offOn = offH; offTxt = "Refreshes come every " + intervalMin + " minutes and the warehouse waits " + Math.round(stopH * 60) + " minutes before stopping, so it never stops."; }
      else { offOn = Math.min(offH, offRefreshes * (stopH + 2 / 60)); offTxt = Math.round(offRefreshes) + " scheduled refreshes a month outside business hours, each keeping the warehouse up for " + Math.round(stopH * 60 + 2) + " minutes."; }
    }
    add("H5", st.wh_type === "serverless" ? "dbu" : "dbu", "SQL warehouse: outside business hours", whCost(offOn, whDbuH), offTxt, true);
    if (st.ai === "genie" || st.ai === "both") {
      var gq = st.bi_users * st.genie_q * st.workdays;
      add("H5", "dbu", "Genie questions", whCost(gq * 30 / 3600, whDbuH), fmtN(gq) + " questions a month, about 30 seconds of warehouse time each.");
    }
    if (st.ai === "agents" || st.ai === "both") {
      var aq = st.agent_q * DAYS;
      add("H5", "ai", "Agent model tokens", aq * P.estimates.llm_cost_per_agent_question.value, fmtN(aq) + " questions a month at about $" + P.estimates.llm_cost_per_agent_question.value + " each in tokens (an estimate; varies 10x by model).");
      add("H5", "ai", "Vector search endpoint", st.vs_units * HOURS * P.estimates.vector_search_unit_hour.value, st.vs_units + " endpoint unit(s) running all month (estimate).", true);
      add("H5", "dbu", "Agent tool queries", whCost(aq * 10 / 3600, whDbuH), "The agent's tools query certified tables: about 10 seconds of warehouse time per question.");
    }

    // ---- streaming lane
    if (sPct > 0) {
      var sTables = Math.max(1, Math.round(nTables * sPct));
      var pipes = Math.ceil(sTables / st.st_per_pipe);
      var sChange = changeGb * sPct;
      var needWu = sChange * (kIngest + st.k_merge) * DAYS * 1.2 + totalGb * sPct * touch * st.k_rewrite * 4 * DAYS;
      var capWu;
      if (st.trigger === "continuous") capWu = pipes * st.st_dbu_h * HOURS;
      else {
        var tr = 1440 / Number(st.trigger) * DAYS;
        var overheadMin = classic ? st.start_min : 0.5;
        capWu = Math.min(pipes * st.st_dbu_h * HOURS, pipes * tr * overheadMin / 60 * st.st_dbu_h);
      }
      var sWu = Math.max(capWu, 0) + needWu;
      var sTxt = sTables + " tables in " + pipes + " pipeline(s), " + (st.trigger === "continuous" ? "running continuously (" + fmtN(pipes * HOURS) + " pipeline-hours)" : "triggered every " + st.trigger + " minutes") + ", plus the work of merging " + fmtGb(sChange) + " of changes a day.";
      wuPipelines += needWu;
      pipeline("S", "Streaming pipelines", sWu, sTxt);
    }

    // ---- across the platform
    var prodPipeUsd = sumBy(L, function (l) { return ["H1", "H2", "H3", "H4", "S"].indexOf(l.hop) >= 0 && (l.kind === "dbu" || l.kind === "vm"); });
    var prodWhUsd = sumBy(L, function (l) { return l.hop === "H5" && (l.kind === "dbu" || l.kind === "vm"); });
    add("X", "dbu", "Failed runs and retries", prodPipeUsd * st.retry_pct / 100, st.retry_pct + "% of pipeline compute is spent on runs that fail and run again.", true);
    add("X", "dbu", "Dev and test environments", (prodPipeUsd + prodWhUsd) * st.devtest_pct / 100, st.devtest_pct + "% of production pipeline and warehouse compute.", true);
    add("X", "storage", "Dev and test storage", (totalGb * (1 + st.gold_pct / 100)) * 0.1 * P.aws.s3_gb_month.value, "Masked samples of silver and gold, about 10% of production.", true);
    if (st.backfills > 0) {
      var bfWu = totalGb * (kIngest + st.k_merge + st.k_gold_full) * st.backfills / 12;
      pipeline("X", "Backfills", bfWu, st.backfills + " full history rebuild(s) a year over " + fmtGb(totalGb) + ", spread per month.", true);
    }
    if (st.maint !== "none") {
      var mWu = wuPipelines * 0.10 + totalGb / 1000 * 0.2;
      pipeline("X", "Table maintenance (OPTIMIZE, VACUUM, statistics)", mWu,
        "Compaction and clean-up: about 10% of write work plus a little per TB kept" + (st.maint === "predictive" ? ", run by predictive optimization." : ", run as your own jobs."),
        true, st.maint === "predictive" ? "jobs_serverless" : null);
    }
    var rewriteDay = changeGb + touchedPerDay;
    add("X", "storage", "Old file versions (time travel)", rewriteDay * st.tt_days * P.aws.s3_gb_month.value,
      "Every merge leaves the old files behind until VACUUM: about " + fmtGb(rewriteDay) + " a day, kept " + st.tt_days + " days.", true);
    if (st.engineers > 0) {
      var engH = st.engineers * st.eng_hours * st.workdays;
      if (st.notebooks === "serverless") add("X", "dbu", "Engineers' notebooks", engH * 4 * rate("all_purpose_serverless", st), fmtN(engH) + " notebook hours a month at about 4 DBU per hour, serverless notebooks.");
      else {
        var idleH = st.engineers * 2 * st.workdays * st.autoterm / 60;
        var apDbuH = inst.dbu_per_hour * 3;
        add("X", "dbu", "Engineers' all-purpose clusters", engH * apDbuH * rate("all_purpose_classic", st), fmtN(engH) + " cluster hours a month on 3-node clusters.");
        add("X", "dbu", "All-purpose clusters left idle", idleH * apDbuH * rate("all_purpose_classic", st), "Two sessions per engineer per day, each idling " + st.autoterm + " minutes before auto-termination.", true);
        add("X", "vm", "All-purpose clusters: EC2", (engH + idleH) * apDbuH * vmPerDbuH, "Machines under the interactive clusters, including idle time.");
      }
    }
    if (st.teams > 0) {
      var monPerDay = {hourly247: 24, hourlybiz: st.biz_hours, daily: 1}[st.mon_refresh];
      var monDays = st.mon_refresh === "hourly247" ? DAYS : st.workdays;
      var monH = Math.min(HOURS, st.teams * 2 * monPerDay * monDays * (5 + 2) / 60);
      if (st.mon_refresh === "hourly247") monH = Math.min(HOURS * st.teams, Math.max(monH, st.teams * HOURS * 0.12));
      add("X", "dbu", "Monitoring dashboards by teams", monH * sizes["2X-Small"] * rate("sql_serverless", st),
        st.teams + " team(s), 2 dashboards each on system tables, refreshed " + {hourly247: "hourly around the clock", hourlybiz: "hourly in business hours", daily: "daily"}[st.mon_refresh] + ": " + fmtN(monH) + " small-warehouse hours.", true);
    }
    if (st.dq_monitors > 0) {
      add("X", "dbu", "Data quality monitoring", st.dq_monitors * runs * 0.15 * DAYS * rate("jobs_serverless", st), st.dq_monitors + " monitored tables profiled after each run, at the serverless rate.", true);
    }
    if (classic) {
      var jobsPerRun = Math.ceil(bTables / st.tables_per_job) * 3;
      var startUsd = jobsPerRun * runs * DAYS * st.start_min / 60 * inst.usd_per_hour * 5 * spotFactor;
      add("X", "vm", "Cluster start-up time", startUsd, fmtN(jobsPerRun * runs * DAYS) + " job clusters a month, each paying " + st.start_min + " minutes of EC2 (5 nodes) before work starts.", true);
      add("X", "network", "NAT gateways", st.nat_gw * HOURS * P.aws.nat_gateway_hour.value, st.nat_gw + " NAT gateway(s) running all month.", true);
      var natGb = changeGb * DAYS * st.external_pct / 100 + (st.s3_endpoint ? 0 : (changeGb + touchedPerDay) * DAYS * 4);
      add("X", "network", "Data through NAT", natGb * P.aws.nat_gateway_gb.value,
        fmtGb(natGb) + " a month through NAT" + (st.s3_endpoint ? " (data from outside AWS)." : ", including all S3 traffic because no S3 gateway endpoint is set up."), true);
    }
    add("X", "network", "Data sent out", st.egress_gb * P.aws.internet_egress_gb.value, fmtGb(st.egress_gb) + " a month to other clouds or the internet.", true);

    var total = sumBy(L, function () { return true; });
    return {lines: L, total: total, totalGb: totalGb, changeGb: changeGb, nTables: nTables, whSize: size};
  }

  function sumBy(L, f) { return L.reduce(function (a, l) { return a + (f(l) ? l.usd : 0); }, 0); }

  // ---------------------------------------------------------------- formatting
  function fmtUsd(v) {
    if (v >= 1e6) return "$" + (v / 1e6).toFixed(v >= 1e7 ? 1 : 2) + "M";
    if (v >= 1e4) return "$" + Math.round(v / 1e3) + "k";
    if (v >= 1e3) return "$" + (v / 1e3).toFixed(1) + "k";
    return "$" + Math.round(v);
  }
  function fmtN(v) { return v >= 1e6 ? (v / 1e6).toFixed(1) + "M" : v >= 1e4 ? Math.round(v / 1e3) + "k" : v >= 100 ? Math.round(v).toString() : (Math.round(v * 10) / 10).toString(); }
  function fmtGb(v) { return v >= 1e6 ? (v / 1e6).toFixed(1) + " PB" : v >= 1e3 ? (v / 1e3).toFixed(v >= 1e4 ? 0 : 1) + " TB" : Math.round(v) + " GB"; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]; }); }

  // ---------------------------------------------------------------- inputs
  function inputHtml(s) {
    var v = state[s.id], id = "p_" + s.id, ctl;
    if (s.type === "select") ctl = '<select id="' + id + '">' + s.opts.map(function (o) { return '<option value="' + o[0] + '"' + (String(v) === String(o[0]) ? " selected" : "") + ">" + esc(o[1]) + "</option>"; }).join("") + "</select>";
    else if (s.type === "check") ctl = '<input type="checkbox" id="' + id + '"' + (v ? " checked" : "") + ">";
    else ctl = '<input type="number" id="' + id + '" value="' + v + '" step="any"' + (s.min != null ? ' min="' + s.min + '"' : "") + (s.max != null ? ' max="' + s.max + '"' : "") + ">";
    var imp = {H: ["high", "High impact"], M: ["med", "Medium"], L: ["low", "Low"]}[s.impact];
    return '<div class="prm' + (s.adv ? " adv" : "") + '"><label for="' + id + '">' + esc(s.label) + ' <span class="imp ' + imp[0] + '">' + imp[1] + "</span></label>" + ctl + (s.help ? '<p class="hlp">' + esc(s.help) + "</p>" : "") + "</div>";
  }
  function bind() {
    SPEC.forEach(function (s) {
      var el = document.getElementById("p_" + s.id);
      if (!el) return;
      el.addEventListener(s.type === "number" ? "input" : "change", function () {
        state[s.id] = s.type === "check" ? el.checked : s.type === "number" ? (parseFloat(el.value) || 0) : el.value;
        if (s.id === "size") applyPreset(el.value);
        render();
      });
    });
  }
  function applyPreset(k) {
    var p = PRESETS[k];
    ["n_small", "n_big", "n_vbig", "n_huge", "engineers", "bi_users"].forEach(function (id) {
      state[id] = p[id];
      var el = document.getElementById("p_" + id); if (el) el.value = p[id];
    });
  }
  function buildInputs() {
    $("#quick").innerHTML = SPEC.filter(function (s) { return s.g === "quick"; }).map(inputHtml).join("");
    $("#groups").innerHTML = GROUPS.map(function (g) {
      var items = SPEC.filter(function (s) { return s.g === g[0]; });
      var allAdv = items.every(function (s) { return s.adv; });
      return '<details class="grp' + (allAdv ? " adv" : "") + '" id="g_' + g[0] + '"><summary><b>' + esc(g[1]) + '</b> <span class="gsum" id="gs_' + g[0] + '"></span><span class="gsub">' + esc(g[2]) + "</span></summary>" +
        '<div class="prms">' + items.map(inputHtml).join("") + "</div></details>";
    }).join("");
    bind();
  }

  // ---------------------------------------------------------------- output
  function render() {
    var r = model(state);
    document.body.classList.toggle("is-classic", state.compute === "classic");
    $("#total").textContent = fmtUsd(r.total) + " a month";
    $("#yearly").textContent = fmtUsd(r.total * 12) + " a year";
    $("#range").textContent = "Likely range " + fmtUsd(r.total * 0.65) + " to " + fmtUsd(r.total * 1.5) + " a month";
    var hidden = sumBy(r.lines, function (l) { return l.hidden; });
    $("#hidden").innerHTML = "<b>" + fmtUsd(hidden) + "</b> of it (" + Math.round(hidden / r.total * 100) + "%) is the kind of cost that rarely makes it into a plan.";
    $("#facts").textContent = r.nTables + " tables · " + fmtGb(r.totalGb) + " of data · " + fmtGb(r.changeGb) + " changing a day · " + r.whSize + " SQL warehouse";

    // stacked bar by hop
    var byHop = HOPS.map(function (h) { return [h[0], h[1], sumBy(r.lines, function (l) { return l.hop === h[0]; })]; });
    $("#bar").innerHTML = byHop.filter(function (h) { return h[2] > 0; }).map(function (h) {
      var pct = h[2] / r.total * 100;
      return '<div class="seg" style="width:' + pct + "%;background:" + HOP_COLOR[h[0]] + '" title="' + esc(h[1]) + ": " + fmtUsd(h[2]) + '">' + (pct > 7 ? h[0] : "") + "</div>";
    }).join("");
    $("#hopcards").innerHTML = byHop.map(function (h) {
      return '<div class="hc" style="background:' + HOP_COLOR[h[0]] + '"><span class="hid">' + h[0] + "</span><b>" + fmtUsd(h[2]) + "</b><span>" + esc(h[1]) + "</span><span class='pct'>" + (r.total ? Math.round(h[2] / r.total * 100) : 0) + "%</span></div>";
    }).join("");

    // group summaries
    var gmap = {h1: "H1", h2: "H2", h3: "H3", h4: "H4", h5: "H5", stream: "S", across: "X"};
    Object.keys(gmap).forEach(function (g) { var el = $("#gs_" + g); if (el) el.textContent = fmtUsd(sumBy(r.lines, function (l) { return l.hop === gmap[g]; })) + " a month"; });

    // line table
    var view = $("#view").value;
    var groups = view === "hop" ? HOPS : KINDS;
    var key = view === "hop" ? "hop" : "kind";
    $("#lines").innerHTML = groups.map(function (g) {
      var ls = r.lines.filter(function (l) { return l[key] === g[0]; }).sort(function (a, b) { return b.usd - a.usd; });
      if (!ls.length) return "";
      var sub = sumBy(ls, function () { return true; });
      return '<tr class="cat"><td colspan="3">' + (view === "hop" ? g[0] + " · " : "") + esc(g[1]) + '<span>' + fmtUsd(sub) + " · " + Math.round(sub / r.total * 100) + "%</span></td></tr>" +
        ls.map(function (l) {
          return "<tr><td><details><summary>" + esc(l.name) + (l.hidden ? ' <span class="hdn">hidden cost</span>' : "") + "</summary><p>" + esc(l.why) + "</p></details></td><td class='k'>" +
            (view === "hop" ? esc(KINDS.filter(function (k) { return k[0] === l.kind; })[0][1]) : esc(l.hop)) + "</td><td class='num'>" + fmtUsd(l.usd) + "</td></tr>";
        }).join("");
    }).join("");

    drivers(r.total);
    savings(r.total);
    saveHash();
  }

  function tryState(patch) { var s = Object.assign({}, state, patch); return model(s).total; }

  function drivers(base) {
    var scale = function (f) { return {n_small: state.n_small * f, n_big: state.n_big * f, n_vbig: state.n_vbig * f, n_huge: state.n_huge * f}; };
    var D = [
      ["Amount of data", scale(0.5), scale(2), "half", "double"],
      ["Batch runs per day", {runs: String(Math.max(1, Number(state.runs) / 4))}, {runs: String(Math.min(96, Number(state.runs) * 4))}, "a quarter", "4x"],
      ["Dashboard users", {bi_users: state.bi_users / 2}, {bi_users: state.bi_users * 2}, "half", "double"],
      ["Tables on the streaming lane", {streaming_pct: "0"}, {streaming_pct: String(Math.min(100, Number(state.streaming_pct) + 25))}, "none", "+25 points"],
      ["File layout", {layout: "good"}, {layout: "poor"}, "good", "poor"],
      ["Gold refresh", {gold_refresh: "incremental"}, {gold_refresh: "full"}, "incremental", "full rebuild"],
      ["Bronze history kept", {bronze_days: 30}, {bronze_days: 730}, "30 days", "2 years"],
      ["Warehouse auto-stop", {auto_stop: 5}, {auto_stop: 30}, "5 min", "30 min"],
      ["Dev and test share", {devtest_pct: 10}, {devtest_pct: 60}, "10%", "60%"],
      ["Compute", {compute: "serverless"}, {compute: "classic"}, "serverless", "classic"],
      ["Real-time serving", {realtime: false}, {realtime: true}, "off", "on"]
    ].map(function (d) { var lo = tryState(d[1]), hi = tryState(d[2]); return {name: d[0], lo: lo, hi: hi, loL: d[3], hiL: d[4], spread: Math.abs(hi - lo)}; })
      .sort(function (a, b) { return b.spread - a.spread; });
    var max = Math.max.apply(null, D.map(function (d) { return Math.max(Math.abs(d.lo - base), Math.abs(d.hi - base)); })) || 1;
    $("#drivers").innerHTML = D.map(function (d) {
      var a = (d.lo - base) / max * 50, b = (d.hi - base) / max * 50;
      var left = 50 + Math.min(a, b, 0), right = 50 + Math.max(a, b, 0);
      return '<div class="drv"><span class="dn">' + esc(d.name) + '</span><span class="dt"><span class="mid"></span><span class="db" style="left:' + left + "%;width:" + Math.max(0.5, right - left) + '%"></span></span>' +
        '<span class="dv">' + esc(d.loL) + " " + fmtUsd(d.lo) + " · " + esc(d.hiL) + " " + fmtUsd(d.hi) + "</span></div>";
    }).join("");
  }

  function savings(base) {
    var S = [];
    function opt(cond, name, patch, how) { if (!cond) return; var t = tryState(patch); if (base - t > base * 0.01) S.push({name: name, save: base - t, how: how}); }
    opt(state.compute === "classic", "Move pipelines to serverless", {compute: "serverless"}, "No idle clusters, start-up time or NAT; the DBU price is higher but includes the machines.");
    opt(state.compute === "serverless", "Move steady, large batch jobs to classic", {compute: "classic", spot: true}, "Classic with spot workers can be cheaper for long, predictable jobs; you take on cluster tuning.");
    opt(state.layout === "poor", "Fix file layout (liquid clustering, deletion vectors)", {layout: "good"}, "Merges touch far fewer files, so far less is rewritten every run.");
    opt(state.gold_refresh === "full", "Refresh gold incrementally", {gold_refresh: "incremental"}, "Materialized views and merges process only what changed.");
    opt(state.compute === "serverless" && state.sl_mode === "performance", "Use standard mode for scheduled serverless jobs", {sl_mode: "standard"}, "Jobs that don't need to start within a minute run cheaper.");
    opt(state.refresh_247, "Refresh dashboards only in business hours", {refresh_247: false}, "Lets the warehouse stop at night and at weekends.");
    opt(state.refresh === "15min", "Refresh dashboards hourly instead of every 15 minutes", {refresh: "hourly"}, "Most dashboards are not read four times an hour.");
    opt(state.auto_stop > 5, "Set warehouse auto-stop to 5 minutes", {auto_stop: 5}, "Serverless warehouses restart in seconds.");
    opt(state.devtest_pct > 20, "Shrink dev and test to 20% of production", {devtest_pct: 20}, "Smaller compute, auto-stop and sampled data in lower environments.");
    opt(Number(state.runs) > 1, "Run batch half as often where freshness allows", {runs: String(Math.max(1, Number(state.runs) / 4))}, "Ask which tables really need the fresher schedule.");
    opt(Number(state.streaming_pct) > 0 && state.trigger === "continuous", "Trigger streaming every 15 minutes instead of continuously", {trigger: "15"}, "Minutes of delay instead of seconds, without compute that never stops.");
    opt(state.compute === "classic" && !state.s3_endpoint, "Add an S3 gateway endpoint", {s3_endpoint: true}, "S3 traffic stops flowing through the NAT gateway. Free to set up.");
    opt(state.compute === "classic" && !state.spot, "Put job workers on spot machines", {spot: true}, "About 60% off the machines for batch jobs that can retry.");
    opt(state.bronze_days > 90, "Keep 90 days of bronze history instead of " + state.bronze_days, {bronze_days: 90}, "Bronze is append-only; older history is rarely replayed. Archive it to a cheaper storage class if you must keep it.");
    opt(state.maint === "manual", "Switch to predictive optimization", {maint: "predictive"}, "Maintenance runs only where it helps.");
    opt(state.mon_refresh === "hourly247" && state.teams > 0, "Refresh monitoring dashboards in business hours only", {mon_refresh: "hourlybiz"}, "Most cost and health dashboards are read in the morning.");
    S.sort(function (a, b) { return b.save - a.save; });
    $("#savings").innerHTML = S.length ? S.slice(0, 8).map(function (s) {
      return "<tr><td><b>" + esc(s.name) + "</b><br><span class='hlp'>" + esc(s.how) + "</span></td><td class='num'>" + fmtUsd(s.save) + "<br><span class='hlp'>" + Math.round(s.save / base * 100) + "% less</span></td></tr>";
    }).join("") : "<tr><td>Nothing obvious left to save with these settings.</td><td></td></tr>";
  }

  // ---------------------------------------------------------------- share link
  function saveHash() {
    var diff = {};
    SPEC.forEach(function (s) { if (state[s.id] !== s.def) diff[s.id] = state[s.id]; });
    var h = Object.keys(diff).length ? "#" + encodeURIComponent(JSON.stringify(diff)) : "";
    try { history.replaceState(null, "", location.pathname + h); } catch (e) { /* ignore */ }
  }
  function loadHash() {
    if (!location.hash || location.hash.length < 3) return;
    try {
      var d = JSON.parse(decodeURIComponent(location.hash.slice(1)));
      Object.keys(d).forEach(function (k) { if (k in state) state[k] = d[k]; });
    } catch (e) { /* ignore a bad link */ }
  }

  // ---------------------------------------------------------------- start
  function init() {
    loadHash();
    if (!location.hash || location.hash.length < 3) applyPresetState(state.size);
    buildInputs();
    $("#view").addEventListener("change", render);
    $("#expert").addEventListener("change", function () { document.body.classList.toggle("expert", this.checked); });
    $("#reset").addEventListener("click", function () { SPEC.forEach(function (s) { state[s.id] = s.def; }); applyPresetState(state.size); buildInputs(); render(); });
    $("#share").addEventListener("click", function () {
      var url = location.href;
      if (navigator.clipboard) navigator.clipboard.writeText(url).then(function () { $("#share").textContent = "Link copied"; setTimeout(function () { $("#share").textContent = "Copy a link to these settings"; }, 2000); });
    });
    render();
  }
  function applyPresetState(k) { var p = PRESETS[k]; ["n_small", "n_big", "n_vbig", "n_huge", "engineers", "bi_users"].forEach(function (id) { state[id] = p[id]; }); }
  window.DBX_MODEL = {model: model, state: state, SPEC: SPEC};   // for tests in the console
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
