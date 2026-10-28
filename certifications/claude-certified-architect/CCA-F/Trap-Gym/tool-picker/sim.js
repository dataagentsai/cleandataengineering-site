/* Tool picker simulator. Deterministic: the same request and fix always give the same 100 replays,
   so a recording can be repeated. Rates are illustrative, chosen to show the shape the exam guide
   describes (descriptions are the primary selection mechanism; minimal descriptions give unreliable
   selection among similar tools; routing layers and merged tools are bigger builds). */
(function () {
  const TOOLS = { get_customer: "get_customer", lookup_order: "lookup_order", track_delivery: "track_delivery" };
  const REQS = {
    track:   { label: "“Is box 20931 arriving today?”", short: "Is box 20931 arriving today?", right: "track_delivery",
               why: "The box is still on its way, so the courier's status is what the customer wants." },
    contents:{ label: "“What was in box 20931?”", short: "What was in box 20931?", right: "lookup_order",
               why: "The customer wants the contents and charges of one delivered box." },
    address: { label: "“I'm customer 48213, change my address”", short: "I'm customer 48213, change my address", right: "get_customer",
               why: "An account change. The customer number looks just like a box ID." },
    tuesday: { label: "“Last Tuesday's box was missing the salmon”", short: "Last Tuesday's box was missing the salmon", right: "get_customer",
               why: "No box ID given. get_customer comes first: its record lists the customer's boxes by date." },
  };
  const FIXES = {
    one:   { label: "One-line descriptions", where: "box-desc", effort: 1, effortText: "what most teams start with" },
    fmt:   { label: "+ input formats and examples", where: "box-desc", effort: 1, effortText: "edit three descriptions" },
    full:  { label: "+ edge cases and boundaries", where: "box-desc", effort: 1, effortText: "edit three descriptions" },
    shots: { label: "Few-shot examples in the prompt", where: "box-prompt", effort: 2, effortText: "examples to write, keep in step with the tools, and send on every call" },
    route: { label: "Keyword routing layer", where: "box-route", effort: 3, effortText: "keyword code, tests, and word lists to keep up as customers find new phrasings" },
    merge: { label: "Merge into one lookup tool", where: "box-tools", effort: 3, effortText: "server change, new schema, every caller updated" },
    any:   { label: "tool_choice: \"any\"", where: "box-choice", effort: 1, effortText: "one request parameter" },
  };
  const DESC = {
    one: `get_customer    "Gets a customer."
lookup_order    "Looks up an order."
track_delivery  "Tracks a delivery."`,
    fmt: `get_customer    "Finds a customer account. Input: customer number
                 (5 digits, from the welcome email) or email.
                 e.g. 'I'm customer 48213', 'my email is ...'"
lookup_order    "Shows one box: contents and charges. Input: box ID
                 (5 digits on the box label). e.g. 'what was in
                 box 20931?'"
track_delivery  "Courier status of a box. Input: box ID.
                 e.g. 'where is box 20931?'"`,
    full: `get_customer    "Finds a customer account: plan, address and
                 every box with its delivery date. Input: customer
                 number (5 digits) or email. Use first when the
                 customer names a box by date, not by ID."
lookup_order    "Contents and charges of a box already delivered.
                 Input: box ID (5 digits on the label). Not for a
                 box on its way: use track_delivery. Not for dates."
track_delivery  "Courier status of a box not yet delivered: 'is it
                 coming today?'. Input: box ID. Not for contents or
                 charges: use lookup_order."`,
    shots: `Descriptions stay one line ("Gets a customer." ...).
System prompt adds examples:
  "Where's box 20931?"          -> track_delivery
  "What was in box 20931?"      -> lookup_order
  "I'm customer 48213 ..."      -> get_customer`,
    route: `Code runs before Claude and offers a subset of tools:
  message mentions "box" or "delivery" -> lookup_order, track_delivery
  message mentions "customer" or "account" -> get_customer
  first rule that matches wins
Descriptions stay one line.`,
    merge: `lookup  "Looks something up."
        Input: { kind: "customer" | "order" | "delivery", id }
Claude now picks a kind instead of a tool.`,
    any: `Descriptions stay one line ("Gets a customer." ...).
Request sets tool_choice: {"type": "any"}
Claude must call some tool; it cannot reply in text.`,
  };
  // r = right tool, w = wrong tool, rest = no tool call (replied or asked in text). wt = the wrong tool it picks.
  const OUT = {
    track: {
      one:   { r: .52, w: .40, wt: "lookup_order", v: "Coin toss", c: "rose", note: "“Looks up an order” and “Tracks a delivery” both sound right for a box. Claude has nothing to choose by." },
      fmt:   { r: .70, w: .27, wt: "lookup_order", v: "Better, not there", c: "butter", note: "Both tools take the same box ID, so formats alone can't separate them. They need a boundary." },
      full:  { r: .96, w: .03, wt: "lookup_order", v: "Right fix", c: "mint", note: "“Not for a box on its way: use track_delivery” gives Claude the line between the two tools." },
      shots: { r: .82, w: .15, wt: "lookup_order", v: "Helps, later step", c: "butter", note: "The example matches this phrasing, so it mostly works. The descriptions still say nothing." },
      route: { r: .58, w: .40, wt: "lookup_order", v: "Still a coin toss", c: "rose", note: "The router narrows it to the two box tools, then Claude faces the same vague pair." },
      merge: { r: .55, w: .40, wt: "lookup_order", v: "Moves the problem", c: "rose", note: "Claude now picks kind: \"order\" or kind: \"delivery\". Same choice, same vague words, more work." },
      any:   { r: .52, w: .48, wt: "lookup_order", v: "Wrong lever", c: "rose", note: "“any” makes sure Claude calls a tool. It does nothing for which tool." },
    },
    contents: {
      one:   { r: .86, w: .12, wt: "track_delivery", v: "Mostly fine", c: "butter", note: "“Order” is close enough to “what was in”, so the one-liner usually works here." },
      fmt:   { r: .93, w: .06, wt: "track_delivery", v: "Good", c: "mint", note: "The example query is almost this question." },
      full:  { r: .97, w: .02, wt: "track_delivery", v: "Right fix", c: "mint", note: "“Contents and charges of a box already delivered” says it plainly." },
      shots: { r: .94, w: .05, wt: "track_delivery", v: "Works", c: "butter", note: "An example covers it. Fine, but you pay for the examples on every call." },
      route: { r: .90, w: .09, wt: "track_delivery", v: "Works here", c: "butter", note: "“box” sends it to the box tools, and this phrasing is clear enough. A lot of code for what a description does." },
      merge: { r: .85, w: .13, wt: "track_delivery", v: "No better", c: "rose", note: "Same result as one-liners, after a server change." },
      any:   { r: .86, w: .14, wt: "track_delivery", v: "No change", c: "rose", note: "Claude was already calling a tool. “any” only removes the text replies." },
    },
    address: {
      one:   { r: .58, w: .38, wt: "lookup_order", v: "Misrouted", c: "rose", note: "48213 looks like a box ID, and nothing says what each tool takes. The exam's “similar identifier formats” case." },
      fmt:   { r: .93, w: .05, wt: "lookup_order", v: "Fixed", c: "mint", note: "“Input: customer number … e.g. ‘I'm customer 48213’” tells Claude which ID goes where." },
      full:  { r: .97, w: .02, wt: "lookup_order", v: "Right fix", c: "mint", note: "Formats plus “plan, address and every box” make the account tool obvious." },
      shots: { r: .88, w: .10, wt: "lookup_order", v: "Helps, later step", c: "butter", note: "An example shows this case, but the descriptions still don't say what each tool takes." },
      route: { r: 0, w: .92, wt: "track_delivery", v: "Right tool removed", c: "rose", note: "“delivery address” matched the box rule first, so get_customer was never offered. Keyword code misread the request." },
      merge: { r: .60, w: .36, wt: "lookup_order", v: "Moves the problem", c: "rose", note: "Claude passes 48213 with kind: \"order\" about as often as it picked the wrong tool before." },
      any:   { r: .58, w: .42, wt: "lookup_order", v: "Wrong lever", c: "rose", note: "Forcing a call turns the few text replies into more wrong calls." },
    },
    tuesday: {
      one:   { r: .30, w: .55, wt: "lookup_order", v: "Wrong call", c: "rose", note: "Claude passes “last Tuesday” to lookup_order as the box ID, and the call fails." },
      fmt:   { r: .72, w: .20, wt: "lookup_order", v: "Better, not there", c: "butter", note: "Knowing lookup_order needs a box ID helps. Nothing says where to find one." },
      full:  { r: .94, w: .03, wt: "lookup_order", v: "Right fix", c: "mint", note: "The edge case is written down: no box ID, call get_customer first, its record lists boxes by date." },
      shots: { r: .62, w: .30, wt: "lookup_order", v: "Only if shown", c: "butter", note: "None of the examples names a box by date, so this new phrasing falls back to guessing." },
      route: { r: 0, w: .85, wt: "lookup_order", v: "Right tool removed", c: "rose", note: "“box” matched, so only the box tools were offered. Claude can't reach get_customer at all." },
      merge: { r: .35, w: .55, wt: "lookup_order", v: "Moves the problem", c: "rose", note: "kind: \"order\", id: \"last Tuesday\". Same mistake, new shape." },
      any:   { r: .30, w: .70, wt: "lookup_order", v: "Forced a guess", c: "rose", note: "Asking which box was at least safe. “any” removes that option and forces a wrong call." },
    },
  };
  const VERDICT = {
    one: "The starting point. Fine where the words are obvious, a coin toss where tools overlap.",
    fmt: "Fixes the ID mix-up. Still no line between the two box tools.",
    full: "The exam's answer as a first step: same cost as a one-liner, best on every request.",
    shots: "A later step: worth it when good descriptions still give inconsistent picks.",
    route: "Overbuilt, and it can hide the right tool. Code is guessing intent from words.",
    merge: "More work than a first step, and the choice just moves into a parameter.",
    any: "The right tool for a different problem: Claude replying in text when a call is required.",
  };
  const N = 100;

  function rng(seedStr) {
    let h = 1779033703 ^ seedStr.length;
    for (let i = 0; i < seedStr.length; i++) { h = Math.imul(h ^ seedStr.charCodeAt(i), 3432918353); h = (h << 13) | (h >>> 19); }
    let a = h >>> 0;
    return function () { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  }

  // Exact counts (rounded rates), placed in a seeded shuffle, so the tally always matches the stated rate.
  function replay(req, fix) {
    const o = OUT[req][fix], nr = Math.round(o.r * N), nw = Math.round(o.w * N);
    const s = [];
    for (let i = 0; i < N; i++) s.push(i < nr ? "ok" : i < nr + nw ? "miss" : "na");
    const r = rng(req + ":" + fix);
    for (let i = N - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [s[i], s[j]] = [s[j], s[i]]; }
    return { s, nr, nw, nt: N - nr - nw };
  }

  const $ = (id) => document.getElementById(id);
  let q = "track", f = "one", timer = null;

  function buttons(boxId, items, current, set) {
    const box = $(boxId);
    box.innerHTML = "";
    Object.entries(items).forEach(([k, v]) => {
      const x = document.createElement("button");
      x.className = "btn" + (k === current ? " on" : "");
      x.textContent = v.label;
      x.onclick = () => { set(k); draw(); };
      box.appendChild(x);
    });
  }

  function highlight() {
    ["box-route", "box-desc", "box-prompt", "box-choice", "box-tools"].forEach((id) => {
      const r = $(id);
      if (r) r.setAttribute("stroke-width", id === FIXES[f].where ? "4" : "1.5");
    });
    const merged = f === "merge";
    $("tools-three").style.display = merged ? "none" : "";
    $("tools-one").style.display = merged ? "" : "none";
    $("route-txt").textContent = f === "route" ? "offers a subset" : "(optional)";
  }

  function draw() {
    buttons("sim-q", REQS, q, (k) => (q = k));
    buttons("sim-f", FIXES, f, (k) => (f = k));
    highlight();
    run();
  }

  function run() {
    clearTimeout(timer);
    const o = OUT[q][f], R = REQS[q], F = FIXES[f], res = replay(q, f), grid = $("sim-grid");
    grid.innerHTML = "";
    const cells = res.s.map((s) => { const c = document.createElement("i"); c.dataset.s = s; grid.appendChild(c); return c; });
    let i = 0;
    (function step() {
      for (let k = 0; k < 10 && i < N; k++, i++) cells[i].className = cells[i].dataset.s;
      if (i < N) timer = setTimeout(step, 30);
    })();
    $("sim-desc").textContent = DESC[f];
    $("sim-need").innerHTML = `Right first call: <code>${R.right}</code>. ${R.why}`;
    const nm = (x) => f === "merge" ? `lookup(kind: "${{ get_customer: "customer", lookup_order: "order", track_delivery: "delivery" }[x]}")` : x;
    let t = `<b>${res.nr}</b> of 100 called <code>${nm(R.right)}</code> (right) · <b>${res.nw}</b> called <code>${nm(o.wt)}</code> (wrong)`;
    if (res.nt) t += ` · <b>${res.nt}</b> made no tool call`;
    $("sim-tally").innerHTML = t;
    $("sim-effort").innerHTML = `Build and upkeep: ${"●".repeat(F.effort)}${"○".repeat(3 - F.effort)} (${F.effortText})`;
    $("sim-verdict").className = "box " + o.c;
    $("sim-verdict").innerHTML = `<span class="chip ${o.c}">${o.v}</span> ${o.note}`;
    // All four requests under this fix.
    let total = 0;
    const rows = Object.keys(REQS).map((k) => {
      const x = replay(k, f);
      total += x.nr;
      return `<tr${k === q ? ' class="cur"' : ""}><td>${REQS[k].short}</td><td><span class="bar"><span style="width:${x.nr}%"></span></span> ${x.nr}</td></tr>`;
    }).join("");
    $("sim-all").innerHTML = `<tr><th>Request</th><th>Right picks of 100</th></tr>${rows}<tr><td><b>All four</b></td><td><b>${total} of 400</b></td></tr>`;
    $("sim-sum").innerHTML = `<b>${F.label}:</b> ${VERDICT[f]}`;
  }

  window.addEventListener("DOMContentLoaded", draw);
})();
