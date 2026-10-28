/* Hook clean-up simulator. Fully scripted: every tool result, answer and tally comes from the fixed tables below,
   so the same choice always plays the same chat and a recording can be repeated. Rates are illustrative. */
(function () {
  const STATUS = { 1: "requested", 2: "approved, not yet paid", 3: "paid out", 4: "rejected" };
  const CUST = {
    asha: { label: "Asha", rid: "R-4471", a: 1775037600, aIso: "2026-04-01T10:00:00Z", aDay: "1 April",
            b: "2026-03-31T16:00:00Z", bIso: "2026-03-31T16:00:00Z", bDay: "31 March", st: 3, first: "b",
            ask: "Which of my two boxes arrives first, and has my refund for the broken jar gone through?" },
    ben:  { label: "Ben", rid: "R-4502", a: 1775224800, aIso: "2026-04-03T14:00:00Z", aDay: "3 April",
            b: "2026-04-06T08:00:00+05:30", bIso: "2026-04-06T02:30:00Z", bDay: "6 April", st: 2, first: "a",
            ask: "Which box comes first, and is my refund paid yet?" },
    chen: { label: "Chen", rid: "R-4519", a: 1775642400, aIso: "2026-04-08T10:00:00Z", aDay: "8 April",
            b: "2026-04-09T09:00:00+01:00", bIso: "2026-04-09T08:00:00Z", bDay: "9 April", st: 1, first: "a",
            ask: "Will the pantry box or the weekly box get here first? And what's happening with my refund?" },
  };
  // How Claude misreads each raw value when nothing helps it (scripted, illustrative).
  const MISREAD = {
    asha: { aDay: "21 March", st: "still being processed" },
    ben:  { aDay: "3 April", st: "paid" },
    chen: { aDay: "18 April", st: "requested" },
  };

  const HANDLE = {
    nothing: { label: "Do nothing", where: null },
    prompt:  { label: "System-prompt instruction to convert", where: "box-prompt" },
    post:    { label: "PostToolUse hook that normalises", where: "box-post" },
    pre:     { label: "PreToolUse hook", where: "box-pre" },
    sub:     { label: "A normalising subagent", where: "box-sub" },
    owners:  { label: "Ask each tool's owner to change their API", where: "box-tools" },
  };

  const PROMPT_NOTE = "System prompt: \"lookup_order.est_delivery is Unix seconds; convert it to a date.\n  get_refund.status: 1 requested, 2 approved, 3 paid out, 4 rejected.\"";

  function raw(c) {
    return `lookup_order      { "box": "weekly",  "est_delivery": ${c.a} }\n` +
           `track_shipment    { "box": "pantry",  "eta": "${c.b}" }\n` +
           `get_refund        { "refund_id": "${c.rid}", "status": ${c.st} }`;
  }
  function clean(c) {
    return `lookup_order      { "box": "weekly",  "est_delivery": "${c.aIso}" }\n` +
           `track_shipment    { "box": "pantry",  "eta": "${c.bIso}" }\n` +
           `get_refund        { "refund_id": "${c.rid}", "status": "${STATUS[c.st].replace(/, /g, "_").replace(/ /g, "_")}" }`;
  }
  function answer(c, aDay, st) {
    const first = aDay === c.aDay ? c.first : (c.first === "a" ? "b" : "a");
    const firstBox = first === "a" ? `weekly box (${aDay})` : `pantry box (${c.bDay})`;
    const second = first === "a" ? `pantry box on ${c.bDay}` : `weekly box on ${aDay}`;
    return `Your ${firstBox} arrives first, then the ${second}. Your refund is ${st}.`;
  }

  // Which customer each handling gets right: [date right, status right]
  function outcome(h, k) {
    const c = CUST[k], m = MISREAD[k];
    if (h === "post" || h === "sub") return { aDay: c.aDay, st: STATUS[c.st] };
    if (h === "prompt") return { aDay: k === "chen" ? "10 April" : c.aDay, st: STATUS[c.st] };
    return { aDay: m.aDay, st: m.st };
  }

  const RATE = { nothing: 612, prompt: 958, post: 1000, pre: 612, sub: 991, owners: 612 };
  const COST = {
    nothing: "None. Nothing was done.",
    prompt:  "A few lines of prompt. Claude still does the conversion itself, every time.",
    post:    "A few lines of code, written once, run on every tool result.",
    pre:     "A hook that runs, but on the wrong side of the tool: it sees the call, never the result.",
    sub:     "An extra model call on every tool result: more tokens, about 2 s more per call, and its own error rate.",
    owners:  "Three tickets to three other teams. Nothing changes until each of them ships, and the next new tool brings a new format.",
  };
  const V = {
    nothing: ["Breaks", "rose", "Claude has to guess what a ten-digit number and a bare status code mean. Mixed formats reach the model as they are."],
    prompt:  ["Only usually works", "butter", "Most chats come out right, but Claude still does the arithmetic, and now and then it slips. Code converts the same way every time."],
    post:    ["Best fit (exam answer)", "mint", "The hook rewrites every result into one format before Claude reads it. Claude only ever sees clean dates and named statuses."],
    pre:     ["Wrong hook", "rose", "PreToolUse checks the outgoing call. The mess is in the result, which PreToolUse never sees."],
    sub:     ["Overbuilt", "butter", "It works, but it pays a model call, time and a small error rate for a job a few lines of code do exactly."],
    owners:  ["Slow and out of your hands", "butter", "Fine in the long run, but you don't control those teams. Today Claude still sees the raw formats."],
  };

  const $ = (id) => document.getElementById(id);
  let k = "asha", h = "nothing", timer = null;

  function buttons(boxId, items, current, set) {
    const box = $(boxId);
    box.innerHTML = "";
    Object.entries(items).forEach(([key, v]) => {
      const x = document.createElement("button");
      x.className = "btn" + (key === current ? " on" : "");
      x.textContent = v.label;
      x.onclick = () => { set(key); draw(); };
      box.appendChild(x);
    });
  }
  const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");

  function highlight() {
    ["box-prompt", "box-post", "box-pre", "box-sub", "box-tools"].forEach((id) => {
      const r = $(id);
      if (r) r.setAttribute("stroke-width", id === HANDLE[h].where ? "4" : "1.5");
    });
  }

  function draw() {
    buttons("sim-c", CUST, k, (x) => { k = x; });
    buttons("sim-h", HANDLE, h, (x) => { h = x; });
    $("sim-ask").innerHTML = `<span class="chip">${CUST[k].label} asks</span>“${esc(CUST[k].ask)}”`;
    highlight();
    run();
  }

  function run() {
    clearTimeout(timer);
    const c = CUST[k], o = outcome(h, k);
    const sees = (h === "post" || h === "sub") ? clean(c)
      : h === "prompt" ? raw(c) + "\n\n" + PROMPT_NOTE
      : h === "owners" ? raw(c) + "\n\n(Tickets filed with three teams. No release date yet.)"
      : h === "pre" ? raw(c) + "\n\n(The PreToolUse hook checked each call's input. The results are untouched.)"
      : raw(c);
    const dateOk = o.aDay === c.aDay, stOk = o.st === STATUS[c.st];
    const truth = `Truth: the ${c.first === "a" ? `weekly box (${c.aDay})` : `pantry box (${c.bDay})`} arrives first; the refund is ${STATUS[c.st]}.`;
    const steps = [
      ["1. What the three tools return (raw)", `<pre>${esc(raw(c))}</pre>`],
      ["2. What Claude sees", `<pre>${esc(sees)}</pre>`],
      ["3. Claude's answer to " + c.label, `<div class="told">${esc(answer(c, o.aDay, o.st))}</div><div style="font-size:.9rem;color:var(--muted);margin-top:4px">${esc(truth)}</div>`],
      ["4. Check", `<span class="chip ${dateOk ? "mint" : "rose"}">Which box first: ${dateOk ? "right" : "wrong"}</span><span class="chip ${stOk ? "mint" : "rose"}">Refund status: ${stOk ? "right" : "wrong"}</span>`],
    ];
    const trail = $("sim-trail");
    trail.innerHTML = "";
    const els = steps.map(([t, body]) => {
      const d = document.createElement("div");
      d.className = "step";
      d.innerHTML = `<b>${t}</b><div>${body}</div>`;
      trail.appendChild(d);
      return d;
    });
    let i = 0;
    (function step() { if (i < els.length) { els[i++].classList.add("in"); timer = setTimeout(step, 200); } })();
    const n = RATE[h];
    $("sim-meter").innerHTML = `<div class="meter-fill" style="width:${n / 10}%"></div>`;
    $("sim-tally").innerHTML =
      `<span class="chip">Right answers in 1,000 similar chats</span>${n.toLocaleString("en")}` +
      (h === "owners" ? " today (until all three teams ship)" : "") + `<br>` +
      `<span class="chip">What it costs</span>${esc(COST[h])}`;
    const v = V[h];
    $("sim-verdict").className = "box " + v[1];
    $("sim-verdict").innerHTML = `<span class="chip ${v[1]}">${v[0]}</span> ${v[2]}`;
  }

  window.HookSim = { CUST, HANDLE, RATE, V, outcome };
  window.addEventListener("DOMContentLoaded", draw);
})();
