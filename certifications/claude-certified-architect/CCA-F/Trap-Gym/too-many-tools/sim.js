/* Too many tools simulator. Fully scripted: the same request and the same distribution always play the
   same replay, so a recording can be repeated. Reliability figures and minutes are illustrative, chosen to
   show the shape the exam guide describes (18 tools degrade selection; off-specialisation tools get misused;
   scoped access plus a limited cross-role tool for a high-frequency need). */
(function () {
  // The 18 tools of a research system, by the role that owns them. verify_fact is the optional narrow extra.
  const ROLES = {
    search:    { label: "Search agent",    cls: "r-search",    tools: ["web_search", "search_journals", "fetch_url", "search_trial_registry"] },
    analysis:  { label: "Analysis agent",  cls: "r-analysis",  tools: ["read_pdf", "extract_citation_metadata", "extract_tables", "analyze_findings", "check_retractions"] },
    synthesis: { label: "Synthesis agent", cls: "r-synthesis", tools: ["read_findings", "compare_claims", "build_outline", "save_draft"] },
    reporting: { label: "Reporting agent", cls: "r-reporting", tools: ["format_report", "insert_citations", "render_chart", "export_pdf", "publish_report"] },
  };
  const ALL = Object.values(ROLES).flatMap((r) => r.tools);
  const owner = (t) => Object.keys(ROLES).find((k) => ROLES[k].tools.includes(t));

  const REQS = {
    review: { label: "Full review: does drug A shorten hospital stays?", kind: "Every agent works once", tone: "peri" },
    checks: { label: "Draft that needs 12 checks: 11 one-field lookups, 1 hard one", kind: "A frequent cross-role need", tone: "butter" },
  };
  const DIST = {
    all:    { label: "All 18 tools to every agent", rel: 74 },
    scoped: { label: "4 or 5 scoped tools per role", rel: 97 },
    cross:  { label: "Scoped + one narrow verify_fact for synthesis", rel: 96 },
    single: { label: "One agent with all 18 tools", rel: 70 },
  };

  // rel = chance an agent picks the right tool at one step, given how many it holds (illustrative).
  // Replay rows: [agent, what it needs, tool it calls, status, calls]. status:
  // ok = right tool; wrong = a similar tool from the same pile; misuse = a tool from another role's job;
  // trip = handed back through the coordinator (a round trip); cross = the narrow shared tool; gap = no tool, writes the gap down.
  const S = "search", A = "analysis", Y = "synthesis", R = "reporting", O = "single";
  const OUT = {
    review: {
      all: { min: 34, rows: [
        [S, "find registered trials", "search_trial_registry", "ok"],
        [S, "find journal papers", "web_search", "wrong", 1, "returns blog posts, not journals"],
        [A, "get page and DOI fields", "extract_citation_metadata", "ok"],
        [A, "pull the results tables", "extract_tables", "ok"],
        [Y, "load the approved findings", "read_findings", "ok"],
        [Y, "mid-draft, wonders if newer papers exist", "search_journals", "misuse", 1, "adds 2 papers nobody checked"],
        [Y, "save the draft", "export_pdf", "misuse", 1, "the draft lands as a PDF"],
        [R, "add the citations", "insert_citations", "ok"],
        [R, "export for sign-off", "publish_report", "wrong", 1, "publishes before anyone signs off"],
      ], v: ["Breaks", "rose", "Every agent could reach every tool, so some did. Two unchecked papers reached the draft and the report went out before sign-off."] },
      scoped: { min: 30, rows: [
        [S, "find registered trials", "search_trial_registry", "ok"],
        [S, "find journal papers", "search_journals", "ok"],
        [A, "get page and DOI fields", "extract_citation_metadata", "ok"],
        [A, "pull the results tables", "extract_tables", "ok"],
        [Y, "load the approved findings", "read_findings", "ok"],
        [Y, "mid-draft, wonders if newer papers exist", "(no search tool)", "gap", 1, "lists the gap for the coordinator"],
        [Y, "save the draft", "save_draft", "ok"],
        [R, "add the citations", "insert_citations", "ok"],
        [R, "export for sign-off", "export_pdf", "ok"],
      ], v: ["Best fit (exam answer)", "mint", "Each agent chose from the 4 or 5 tools its job needs. There was nothing off-role to misuse, so the gap was written down instead of filled with unchecked papers."] },
      cross: { min: 30, rows: [
        [S, "find registered trials", "search_trial_registry", "ok"],
        [S, "find journal papers", "search_journals", "ok"],
        [A, "get page and DOI fields", "extract_citation_metadata", "ok"],
        [A, "pull the results tables", "extract_tables", "ok"],
        [Y, "load the approved findings", "read_findings", "ok"],
        [Y, "mid-draft, wonders if newer papers exist", "(verify_fact can't search)", "gap", 1, "lists the gap for the coordinator"],
        [Y, "save the draft", "save_draft", "ok"],
        [R, "add the citations", "insert_citations", "ok"],
        [R, "export for sign-off", "export_pdf", "ok"],
      ], v: ["Also works", "mint", "The same clean run as scoped tools. The extra verify_fact tool sat unused: this request had no frequent lookup, so scoping alone is the answer here."] },
      single: { min: 52, rows: [
        [O, "find registered trials", "search_trial_registry", "ok"],
        [O, "find journal papers", "web_search", "wrong", 1, "returns blog posts, not journals"],
        [O, "get page and DOI fields", "read_pdf", "wrong", 1, "reads the whole PDF, misses the DOI"],
        [O, "pull the results tables", "extract_tables", "ok"],
        [O, "load the approved findings", "read_findings", "ok"],
        [O, "mid-draft, wonders if newer papers exist", "search_journals", "wrong", 1, "adds 2 papers that skip analysis"],
        [O, "save the draft", "save_draft", "ok"],
        [O, "add the citations", "insert_citations", "ok"],
        [O, "export for sign-off", "publish_report", "wrong", 1, "publishes before anyone signs off"],
      ], v: ["Breaks", "rose", "One agent choosing from 18 tools at every step picks worst of all, and nothing keeps one job's tools away from another's. It is also the slowest: one agent does every step in turn."] },
    },
    checks: {
      all: { min: 9, rows: [
        [Y, "load the approved findings", "read_findings", "ok"],
        [Y, "11 one-field lookups (a drug's generic name, a trial's year)", "web_search", "misuse", 11, "3 answers come from unreliable pages"],
        [Y, "hard check: do two papers report the same trial?", "search_journals", "misuse", 1, "one quick search; guesses “different trials” (wrong)"],
        [Y, "save the draft", "save_draft", "ok"],
      ], v: ["Breaks", "rose", "Fast, because synthesis did its own searching, and wrong for the same reason. The hard check needed real research across sources, and three quick lookups used poor sources."] },
      scoped: { min: 31, trips: 12, rows: [
        [Y, "load the approved findings", "read_findings", "ok"],
        [Y, "11 one-field lookups (a drug's generic name, a trial's year)", "back to the coordinator", "trip", 11, "11 round trips to the search agent"],
        [Y, "hard check: do two papers report the same trial?", "back to the coordinator", "trip", 1, "search and analysis agents answer: same trial"],
        [Y, "save the draft", "save_draft", "ok"],
      ], v: ["Too strict", "butter", "Every answer is right, but each one-field lookup waits for a round trip through the coordinator. For a need this frequent, the guide adds a limited cross-role tool."] },
      cross: { min: 12, trips: 1, rows: [
        [Y, "load the approved findings", "read_findings", "ok"],
        [Y, "11 one-field lookups (a drug's generic name, a trial's year)", "verify_fact", "cross", 11, "one field back each time, no round trip"],
        [Y, "hard check: do two papers report the same trial?", "back to the coordinator", "trip", 1, "too big for verify_fact; answer: same trial"],
        [Y, "save the draft", "save_draft", "ok"],
      ], v: ["Best fit (exam answer)", "mint", "The frequent, simple lookups use one narrow shared tool, and the hard question still goes through the coordinator. Least privilege for the common case, coordination for the rare one."] },
      single: { min: 14, rows: [
        [O, "load the approved findings", "read_findings", "ok"],
        [O, "8 one-field lookups (a drug's generic name)", "web_search", "ok", 8],
        [O, "3 one-field lookups (a trial's start year)", "web_search", "wrong", 3, "should have used search_trial_registry; 2 years wrong"],
        [O, "hard check: do two papers report the same trial?", "compare_claims", "wrong", 1, "compares the summaries only; misses that it's one trial"],
        [O, "save the draft", "save_draft", "ok"],
      ], v: ["Breaks", "rose", "No round trips, but with 18 tools to choose from at every step, picks slip: three lookups went to the wrong tool and the hard check used a shortcut."] },
    },
  };
  const LBL = { ok: "right tool", wrong: "wrong pick", misuse: "off-role misuse", trip: "round trip", cross: "narrow shared tool", gap: "notes the gap" };

  const $ = (id) => document.getElementById(id);
  let r = "review", d = "all", timers = [];

  function buttons(boxId, items, current, set) {
    const box = $(boxId);
    box.innerHTML = "";
    Object.entries(items).forEach(([k, v]) => {
      const x = document.createElement("button");
      x.className = "btn" + (k === current ? " on" : "");
      x.innerHTML = v.label + (v.kind ? ` <span class="chip ${v.tone}">${v.kind}</span>` : "");
      x.onclick = () => { set(k); draw(); };
      box.appendChild(x);
    });
  }

  // Which tools does each agent hold under this distribution?
  function holdings() {
    if (d === "single") return [["One research agent", ALL.slice()]];
    return Object.entries(ROLES).map(([k, v]) => {
      let tools = d === "all" ? ALL.slice() : v.tools.slice();
      if (d === "cross" && k === "synthesis") tools = tools.concat(["verify_fact"]);
      return [v.label, tools, k];
    });
  }

  function access() {
    const box = $("sim-access");
    box.innerHTML = "";
    holdings().forEach(([label, tools, role]) => {
      const row = document.createElement("div");
      row.className = "acc";
      const own = role ? tools.filter((t) => owner(t) === role).length : tools.length;
      const extra = tools.includes("verify_fact") ? " + verify_fact" : "";
      const other = role ? tools.filter((t) => t !== "verify_fact" && owner(t) !== role).length : 0;
      row.innerHTML = `<div class="acc-l"><b>${label}</b>: ${tools.length} tool${tools.length > 1 ? "s" : ""}` +
        (other ? ` <span class="warn">(${other} from other roles)</span>` : "") + (extra ? ` <span class="xt">(${own} its own${extra})</span>` : "") + `</div>`;
      const cells = document.createElement("div");
      cells.className = "cells";
      ALL.concat(["verify_fact"]).forEach((t) => {
        const c = document.createElement("i");
        const has = tools.includes(t);
        c.className = has ? (t === "verify_fact" ? "vf" : ROLES[owner(t)].cls) : "none";
        if (has && role && t !== "verify_fact" && owner(t) !== role) c.className += " off";
        c.title = t + (has ? "" : " (not held)");
        cells.appendChild(c);
      });
      row.appendChild(cells);
      box.appendChild(row);
    });
  }

  function diagram() {
    const counts = { search: 4, analysis: 5, synthesis: 4, reporting: 5 };
    Object.keys(counts).forEach((k) => {
      const t = $("cnt-" + k);
      if (!t) return;
      t.textContent = d === "all" ? "18 tools" : d === "single" ? "" : counts[k] + " tools" + (d === "cross" && k === "synthesis" ? " + 1" : "");
    });
    const vf = $("box-vf"), sg = $("box-single");
    if (vf) vf.style.display = d === "cross" ? "" : "none";
    if (sg) sg.style.display = d === "single" ? "" : "none";
    const sl = $("single-lbl");
    if (sl) sl.style.display = d === "single" ? "" : "none";
    ["box-search", "box-analysis", "box-synthesis", "box-reporting"].forEach((id) => {
      const e = $(id);
      if (e) e.setAttribute("fill", d === "all" ? "#fbf0f5" : d === "single" ? "#f4f5f7" : "#eef9f3");
    });
  }

  function draw() {
    buttons("sim-r", REQS, r, (k) => (r = k));
    buttons("sim-d", DIST, d, (k) => (d = k));
    access();
    diagram();
    run();
  }

  function run() {
    timers.forEach(clearTimeout);
    timers = [];
    const o = OUT[r][d];
    const list = $("sim-steps");
    list.innerHTML = "";
    o.rows.forEach(([who, need, tool, st, n, note], i) => {
      const li = document.createElement("li");
      li.className = "st-" + st;
      const name = who === "single" ? "One agent" : ROLES[who].label.replace(" agent", "");
      const off = st === "misuse" && who !== "single" && owner(tool) && owner(tool) !== who ? ` <span class="own">(${ROLES[owner(tool)].label.toLowerCase()}'s tool)</span>` : "";
      li.innerHTML = `<span class="who">${name}</span><span class="tx">${need}${n > 1 ? ` <b>×${n}</b>` : ""}<br><code>${tool}</code>${off}${note ? ` <span class="nt">${note}</span>` : ""}</span><span class="chip ${st === "ok" || st === "cross" || st === "gap" ? "mint" : st === "trip" ? "butter" : "rose"}">${LBL[st]}</span>`;
      list.appendChild(li);
      timers.push(setTimeout(() => li.classList.add("show"), 110 * i));
    });
    const calls = (s) => o.rows.filter((x) => s.includes(x[3])).reduce((a, x) => a + (x[4] || 1), 0);
    const choices = calls(["ok", "wrong", "misuse", "cross", "gap", "trip"]);
    const right = calls(["ok", "cross", "gap", "trip"]);
    $("sim-tally").innerHTML = `Right choice first time: <b>${right} of ${choices}</b> · Wrong picks: <b>${calls(["wrong"])}</b> · Off-role misuse: <b>${calls(["misuse"])}</b> · Round trips through the coordinator: <b>${o.trips || 0}</b> · Time: <b>${o.min} min</b>`;
    const rel = DIST[d].rel;
    $("sim-rel-n").textContent = rel + "%";
    $("sim-rel").style.width = rel + "%";
    $("sim-rel").className = rel < 85 ? "hot" : "";
    $("sim-verdict").className = "box " + o.v[1];
    $("sim-verdict").innerHTML = `<span class="chip ${o.v[1]}">${o.v[0]}</span> ${o.v[2]}`;
  }

  window.addEventListener("DOMContentLoaded", draw);
})();
