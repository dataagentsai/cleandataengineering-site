/* "MCP: where and what" simulator. No randomness: each need × where × what always plays the same
   tool-call log, so a recording can be repeated. Call counts are illustrative. */
(function () {
  const NEEDS = {
    jira:   { label: "Jira tickets for the team and CI", kind: "Standard service", tone: "peri", team: true, env: "JIRA_API_TOKEN",
              task: "Read PROJ-142, then add a comment linking the fix." },
    code:   { label: "Your team's code-search server", kind: "Internal system", tone: "peri", team: true, env: "CODESEARCH_TOKEN",
              task: "Find every caller of <code>applyDiscount</code> before changing it (12 callers, 3 through an interface)." },
    schema: { label: "Staging database schema (300 tables)", kind: "Internal system", tone: "peri", team: true, env: "PG_PASSWORD",
              task: "Which tables hold a learner's streak data?" },
    notes:  { label: "Your experimental notes server", kind: "Only me · trying it", tone: "rose", team: false, env: "NOTES_TOKEN",
              task: "Find my note about the cache bug." },
  };
  const WHERE = {
    penv:   { label: "Project .mcp.json, key as ${VAR}", box: "m-proj" },
    ppaste: { label: "Project .mcp.json, key pasted in", box: "m-proj" },
    user:   { label: "User ~/.claude.json", box: "m-user" },
  };
  const WHAT = {
    tshort: { label: "Own server: tool, one-line description", boxes: ["m-own", "m-tool"] },
    tfull:  { label: "Own server: tool, full description", boxes: ["m-own", "m-tool"] },
    res:    { label: "Own server: a resource (catalog)", boxes: ["m-own", "m-res"] },
    comm:   { label: "Install a community server", boxes: ["m-comm", "m-tool"] },
  };
  // Tool-call logs: [call, result, ok?]. ok: 1 = fine, 0 = failed or wasted.
  const LOGS = {
    jira: {
      tshort: { log: [["jira_request(\"PROJ-142\")", "error: expected a JQL query", 0], ["jira_request(\"key = PROJ-142\")", "ticket text", 1], ["jira_request(\"comment PROJ-142 …\")", "error: unknown action", 0], ["jira_request(\"POST comment\", …)", "comment added", 1]], done: "Done after 2 failed calls" },
      tfull:  { log: [["get_issue(\"PROJ-142\")", "ticket text", 1], ["add_comment(\"PROJ-142\", …)", "comment added", 1]], done: "Done, and the team now maintains a Jira client" },
      res:    { log: [["read resource jira://issues/PROJ-142", "ticket text", 1], ["(no tool to add a comment)", "stuck", 0]], done: "Half done: a resource can be read, not acted on" },
      comm:   { log: [["jira.get_issue(\"PROJ-142\")", "ticket text", 1], ["jira.add_comment(\"PROJ-142\", …)", "comment added", 1]], done: "Done, with a maintained server nobody on the team wrote" },
    },
    code: {
      tshort: { log: [["Grep \"applyDiscount\"", "9 matches", 1], ["Read cart/total.ts", "caller", 1], ["Read checkout/apply.ts", "caller", 1], ["Read promo/rules.ts", "caller", 1]], done: "Answer: 9 of 12 callers. Grep can't see the 3 calls through an interface" },
      tfull:  { log: [["find_usages(symbol=\"applyDiscount\")", "12 callers, 3 via interface", 1]], done: "Answer: 12 of 12 callers in one call" },
      res:    { log: [["read resource code://usages (whole index)", "about 40,000 lines", 0], ["(context nearly full)", "slow, costly", 0]], done: "Answer: 12 of 12, after reading the whole index into context" },
      comm:   { log: [["text_search(\"applyDiscount\")", "9 matches", 1], ["Read cart/total.ts", "caller", 1]], done: "Answer: 9 of 12 callers. A generic search is no better than Grep here" },
    },
    schema: {
      tshort: { log: [["describe_table(\"users\")", "no streak columns", 0], ["describe_table(\"streaks\")", "not found", 0], ["describe_table(\"learner_streak\")", "not found", 0], ["describe_table(\"activity\")", "no streak columns", 0], ["… 7 more guesses", "", 0], ["describe_table(\"learner_streaks\")", "found", 1]], done: "Answer after 12 calls, 11 of them guesses" },
      tfull:  { log: [["describe_table(\"learners\")", "hint: see learner_*", 0], ["describe_table(\"learner_activity\")", "no streak columns", 0], ["describe_table(\"learner_goals\")", "no streak columns", 0], ["describe_table(\"learner_streaks\")", "found", 1]], done: "Answer after 4 calls: better guesses, still guessing" },
      res:    { log: [["read resource schema://staging/tables", "300 tables, one line each", 1], ["describe_table(\"learner_streaks\")", "found", 1]], done: "Answer after 1 read and 1 call" },
      comm:   { log: [["query(\"select table_name from information_schema…\")", "300 names", 1], ["query(\"… columns where table like '%streak%'\")", "no match", 0], ["query(\"… columns like '%streak%'\")", "2 tables", 1], ["query(\"… learner_streaks\")", "found", 1]], done: "Answer after 4 queries: still exploring, now with SQL" },
    },
    notes: {
      tshort: { log: [["search_notes(\"cache bug\")", "1 note", 1]], done: "Found it. A short description is fine for your own experiment" },
      tfull:  { log: [["search_notes(\"cache bug\")", "1 note", 1]], done: "Found it" },
      res:    { log: [["read resource notes://index", "48 titles", 1], ["read resource notes://cache-bug", "the note", 1]], done: "Found it by reading the index" },
      comm:   { log: [["(no community server knows your private notes)", "", 0]], done: "Nothing to install: this server exists only for you" },
    },
  };
  const WHAT_V = {
    jira: {
      tshort: ["butter", "Overbuilt", "You build and maintain a Jira client, and its vague description costs failed calls."],
      tfull:  ["butter", "Overbuilt", "It works, but you now build and maintain a Jira client that already exists."],
      res:    ["rose", "Wrong primitive", "A resource is content to read. Adding a comment is an action, which needs a tool."],
      comm:   ["mint", "Right choice", "Jira is a standard integration: a maintained community server already has the tools."],
    },
    code: {
      tshort: ["rose", "Claude picks Grep", "“Find usages.” tells Claude nothing, so it reaches for the built-in Grep and misses the interface calls."],
      tfull:  ["mint", "Right choice", "A description that says what it covers and when to use it over Grep gets the capable tool chosen."],
      res:    ["butter", "Wrong primitive", "A lookup that takes a symbol is a tool. Dumping every usage as a catalog floods the context."],
      comm:   ["butter", "Less capable", "A generic text-search server knows no more than Grep. Only your server sees interface calls."],
    },
    schema: {
      tshort: ["rose", "Exploring", "Claude must already know a table's name, so it guesses one call at a time."],
      tfull:  ["butter", "Still exploring", "Better descriptions aim the guesses. The calls are still there to learn what exists."],
      res:    ["mint", "Right choice", "A resource is a catalog read once. It answers “what exists?” and the guessing stops."],
      comm:   ["butter", "Different problem", "A community Postgres server gives Claude a query tool, and it explores with SQL instead."],
    },
    notes: {
      tshort: ["mint", "Fine", "For your own experiment, a short tool description is enough while you try it out."],
      tfull:  ["mint", "Fine", "Works well. The lesson for this need is where the config lives."],
      res:    ["mint", "Fine", "An index of your notes as a resource works too."],
      comm:   ["butter", "Not available", "No community server exists for a private experiment. Use your own."],
    },
  };
  const WHERE_V = {
    team: {
      penv:   ["mint", "Right home", "Committed .mcp.json: every clone and CI get the server, and each fills in the key from its own environment."],
      ppaste: ["rose", "Leaks a secret", "Everyone gets the server, and everyone who can read the repo gets the key."],
      user:   ["rose", "Wrong home", "Only you have the server. The teammate and CI start without it."],
    },
    solo: {
      penv:   ["rose", "Wrong home", "Your experiment now appears for every teammate, and CI tries to start it."],
      ppaste: ["rose", "Wrong home and a leak", "Your experiment is pushed on the team, with your key committed in plain text."],
      user:   ["mint", "Right home", "Personal and experimental: ~/.claude.json keeps it yours, in every project."],
    },
  };

  const $ = (id) => document.getElementById(id);
  let need = "code", where = "user", what = "tshort";

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

  function highlight() {
    const on = [WHERE[where].box, ...WHAT[what].boxes];
    ["m-proj", "m-user", "m-comm", "m-own", "m-tool", "m-res"].forEach((id) => {
      const r = $(id);
      if (r) r.setAttribute("stroke-width", on.includes(id) ? "4" : "1.5");
    });
  }

  function logHtml(L) {
    return `<ol class="calls">` + L.log.map(([c, r, ok]) => `<li class="${ok ? "ok" : "bad"}"><code>${c}</code>${r ? ` → ${r}` : ""}</li>`).join("") + `</ol><p class="done"><b>${L.done}.</b></p>`;
  }

  function draw() {
    buttons("sim-n", NEEDS, need, (k) => (need = k));
    buttons("sim-w", WHERE, where, (k) => (where = k));
    buttons("sim-t", WHAT, what, (k) => (what = k));
    highlight();
    const N = NEEDS[need], L = LOGS[need][what];
    const shared = where !== "user";
    const wv = WHERE_V[N.team ? "team" : "solo"][where], tv = WHAT_V[need][what];
    const hasServer = !(need === "notes" && what === "comm");
    $("sim-task").innerHTML = `<b>Task:</b> ${N.task}`;
    let mate, ci;
    if (!hasServer) { mate = ci = "No server to configure."; }
    else if (shared) {
      mate = N.team ? "Gets the server on clone and the same tool calls as you." : "Gets your experiment on clone, wanted or not.";
      mate += where === "penv" ? ` Sets <code>${N.env}</code> once.` : " Also gets your key.";
      ci = where === "penv" ? `Gets the server; <code>${N.env}</code> comes from the CI secret store.` : "Gets the server, using the key committed in the repo.";
      if (!N.team) ci += " It has no use for it.";
    } else {
      mate = N.team ? "Nothing. The server isn't in the repo, so Claude falls back to other tools." : "Nothing, as intended.";
      ci = N.team ? "Nothing. The CI runner has no <code>~/.claude.json</code>." : "Nothing, as intended.";
    }
    const git = !hasServer ? "Nothing." : where === "penv" ? `<code>.mcp.json</code> holds <code>"\${${N.env}}"</code>, not the key.` : where === "ppaste" ? `<code>.mcp.json</code> holds the key in plain text.` : "Nothing: the config stays on your laptop.";
    $("sim-mate").innerHTML = mate;
    $("sim-ci").innerHTML = ci;
    $("sim-git").innerHTML = git;
    $("sim-log").innerHTML = logHtml(L);
    const calls = L.log.filter(([c]) => !c.startsWith("(") && !c.startsWith("…")).length + (L.log.some(([c]) => c.startsWith("… 7")) ? 7 : 0);
    const wasted = L.log.filter(([c, , ok]) => !ok && !c.startsWith("(") && !c.startsWith("…")).length + (L.log.some(([c]) => c.startsWith("… 7")) ? 7 : 0);
    $("sim-count").innerHTML = `Calls in your session: <b>${calls}</b> · failed or wasted: <b>${wasted}</b>`;
    const rank = { mint: 0, butter: 1, rose: 2 };
    const worst = rank[wv[0]] >= rank[tv[0]] ? wv[0] : tv[0];
    const head = worst === "mint" ? "Right fit" : worst === "butter" ? "Works, but" : "Fails here";
    $("sim-verdict").className = "box " + worst;
    $("sim-verdict").innerHTML = `<span class="chip ${worst}">${head}</span><br><b>Where:</b> <span class="chip ${wv[0]}">${wv[1]}</span> ${wv[2]}<br><b>What:</b> <span class="chip ${tv[0]}">${tv[1]}</span> ${tv[2]}`;
  }

  window.addEventListener("DOMContentLoaded", draw);
})();
