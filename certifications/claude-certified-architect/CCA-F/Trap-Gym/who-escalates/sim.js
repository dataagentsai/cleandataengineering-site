/* Who escalates? simulator. Deterministic: the same ticket type and rule always give the same day of
   100 tickets, so a recording can be repeated. Rates are illustrative, chosen to show the shape the exam
   guide describes (explicit criteria + examples calibrate escalation; sentiment and self-reported
   confidence are unreliable proxies for complexity; a separate classifier is overbuilt). */
(function () {
  const TYPES = {
    simple:    { label: "Simple problem", n: 55, should: "resolve", tone: "mint",
                 msg: "“My box came without the yoghurt. Can I get that back?”",
                 why: "One missing item, well inside the refund limit. The agent can settle it." },
    angry:     { label: "Angry but simple", n: 15, should: "resolve", tone: "mint",
                 msg: "“THIRD late box this month!!! Just refund it, I'm sick of this.”",
                 why: "Upset, but a late-box refund is routine. Upset is not complex." },
    exception: { label: "Policy exception", n: 12, should: "escalate", tone: "rose",
                 msg: "“Please refund all four boxes from the trip I forgot to pause for.”",
                 why: "Over the $150 limit and outside policy. A person must decide." },
    complex:   { label: "Calm but complex", n: 8, should: "escalate", tone: "rose",
                 msg: "“No rush. I was charged for a gift box I sent to my mum after she closed her account.”",
                 why: "Polite and calm, but policy doesn't cover it. A gap needs a human call." },
    ask:       { label: "Asks for a person", n: 10, should: "escalate", tone: "rose",
                 msg: "“Salmon missing again. I'd like to talk to a real person, please.”",
                 why: "An explicit request. Escalate at once, even though the agent could fix it." },
  };
  const RULES = {
    vague:     { label: "“Escalate when needed”", where: "box-prompt", effort: 1, effortText: "one vague line in the prompt" },
    sentiment: { label: "Sentiment score", where: "box-sent", effort: 2, effortText: "a sentiment model and a threshold to tune" },
    confidence:{ label: "Self-rated confidence", where: "box-conf", effort: 1, effortText: "a prompt line and a threshold" },
    classifier:{ label: "Separate classifier", where: "box-clf", effort: 3, effortText: "labelled history, training, retraining as policy changes" },
    criteria:  { label: "Criteria + examples", where: "box-prompt", effort: 1, effortText: "a short list of triggers and three or four example chats" },
  };
  // p = share of this ticket type that gets escalated under this rule.
  const OUT = {
    simple: {
      vague:      { p: .12, v: "Mostly fine", c: "butter", note: "Most simple cases get settled, but some go to a person for no reason." },
      sentiment:  { p: .04, v: "Fine here", c: "mint", note: "Calm and simple: the score stays low and the agent settles it." },
      confidence: { p: .20, v: "Over-escalates", c: "butter", note: "The agent rates itself unsure on routine cases now and then, and hands them over." },
      classifier: { p: .06, v: "Fine here", c: "butter", note: "The classifier learned that simple cases stay with the agent. A big build for this." },
      criteria:   { p: .02, v: "Right", c: "mint", note: "No trigger applies, so the agent resolves it." },
    },
    angry: {
      vague:      { p: .55, v: "Mood decides", c: "rose", note: "Without criteria, the agent treats anger as a reason to hand over." },
      sentiment:  { p: .92, v: "Wrong signal", c: "rose", note: "Anger scores high, so nearly every one goes to a person. Sentiment is not complexity." },
      confidence: { p: .30, v: "Unreliable", c: "rose", note: "Angry messages make the agent rate itself less sure, though the fix is routine." },
      classifier: { p: .25, v: "Copies old habits", c: "butter", note: "Staff used to take angry chats, so the classifier learned to send them." },
      criteria:   { p: .04, v: "Right", c: "mint", note: "An example shows an angry customer with a late box getting the refund. The agent follows it." },
    },
    exception: {
      vague:      { p: .45, v: "Misses many", c: "rose", note: "More than half the exceptions stay with the agent, which sometimes promises what policy doesn't allow." },
      sentiment:  { p: .35, v: "Misses many", c: "rose", note: "Polite exceptions score calm and stay with the agent." },
      confidence: { p: .30, v: "Unreliable", c: "rose", note: "The agent feels sure it can help, so it doesn't escalate. Self-rated confidence is poorly calibrated." },
      classifier: { p: .80, v: "Works, overbuilt", c: "butter", note: "Past exceptions were escalated, so it catches most. Prompt criteria do as well for far less." },
      criteria:   { p: .95, v: "Right", c: "mint", note: "“Anything over $150 or outside the refund policy” is a written trigger." },
    },
    complex: {
      vague:      { p: .30, v: "Misses most", c: "rose", note: "Calm and polite, so “needed” doesn't feel needed. The agent improvises." },
      sentiment:  { p: .05, v: "Blind to it", c: "rose", note: "A calm customer scores as fine. The hardest case is the one sentiment misses." },
      confidence: { p: .25, v: "Unreliable", c: "rose", note: "The agent is confident about a case policy doesn't cover. That is exactly when it shouldn't be." },
      classifier: { p: .45, v: "Misses new cases", c: "rose", note: "Gaps are new by nature, and the classifier has seen few like them." },
      criteria:   { p: .90, v: "Right", c: "mint", note: "“Policy doesn't cover it” is a trigger, and an example shows one." },
    },
    ask: {
      vague:      { p: .75, v: "Not every time", c: "rose", note: "The agent often tries to fix it first. The customer has to ask twice." },
      sentiment:  { p: .50, v: "Misses calm asks", c: "rose", note: "A polite request for a person scores calm and gets ignored." },
      confidence: { p: .70, v: "Wrong question", c: "rose", note: "Confidence isn't the point: the customer asked. The agent sure it can help keeps the chat." },
      classifier: { p: .90, v: "Almost", c: "butter", note: "Catches most, misses unusual wording. An explicit ask should go every time." },
      criteria:   { p: 1, v: "Right", c: "mint", note: "“Customer asks for a person: escalate at once” is the first trigger." },
    },
  };
  const HANDOFF = {
    exception: { id: "C-48213", cause: "Asks refund for 4 boxes delivered while away; no pause set", amount: "$236 (over $150 limit)", action: "Decide on a goodwill credit; agent offered none" },
    complex:   { id: "C-30577", cause: "Charged for a gift box sent to an account closed in March", amount: "$64", action: "Check gift billing on closed accounts; refund if error" },
    ask:       { id: "C-51902", cause: "Salmon missing from box B-20931 (second time)", amount: "$18, inside limit", action: "Customer asked for a person; refund and apologise" },
  };
  const N = 100;

  function rng(seedStr) {
    let h = 1779033703 ^ seedStr.length;
    for (let i = 0; i < seedStr.length; i++) { h = Math.imul(h ^ seedStr.charCodeAt(i), 3432918353); h = (h << 13) | (h >>> 19); }
    let a = h >>> 0;
    return function () { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  }

  // The day's stream: same order of ticket types for every rule.
  const STREAM = (function () {
    const s = [];
    Object.entries(TYPES).forEach(([k, t]) => { for (let i = 0; i < t.n; i++) s.push(k); });
    const r = rng("stream");
    for (let i = s.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [s[i], s[j]] = [s[j], s[i]]; }
    return s;
  })();

  // For each type, exactly round(p * n) tickets escalate; which ones is a seeded shuffle.
  function day(rule) {
    const esc = {};
    Object.entries(TYPES).forEach(([k, t]) => {
      const m = Math.round(OUT[k][rule].p * t.n), f = [];
      for (let i = 0; i < t.n; i++) f.push(i < m);
      const r = rng(k + ":" + rule);
      for (let i = f.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [f[i], f[j]] = [f[j], f[i]]; }
      esc[k] = f;
    });
    const seen = {};
    return STREAM.map((k) => {
      const i = (seen[k] = (seen[k] || 0) + 1) - 1, e = esc[k][i], should = TYPES[k].should === "escalate";
      return { k, s: should ? (e ? "esc" : "kept") : (e ? "wrong" : "res") };
    });
  }

  const $ = (id) => document.getElementById(id);
  let t = "exception", rule = "vague", timer = null;

  function buttons(boxId, items, current, set, chips) {
    const box = $(boxId);
    box.innerHTML = "";
    Object.entries(items).forEach(([k, v]) => {
      const x = document.createElement("button");
      x.className = "btn" + (k === current ? " on" : "");
      x.innerHTML = v.label + (chips ? ` <span class="chip ${v.tone}">${v.should}</span>` : "");
      x.onclick = () => { set(k); draw(); };
      box.appendChild(x);
    });
  }

  function highlight() {
    ["box-prompt", "box-sent", "box-conf", "box-clf"].forEach((id) => {
      const r = $(id);
      if (r) r.setAttribute("stroke-width", id === RULES[rule].where ? "4" : "1.5");
    });
  }

  function draw() {
    buttons("sim-t", TYPES, t, (k) => (t = k), true);
    buttons("sim-r", RULES, rule, (k) => (rule = k));
    highlight();
    run();
  }

  function run() {
    clearTimeout(timer);
    const T = TYPES[t], R = RULES[rule], o = OUT[t][rule], d = day(rule), grid = $("sim-grid");
    grid.innerHTML = "";
    const cells = d.map((x) => { const c = document.createElement("i"); c.dataset.s = x.s + (x.k === t ? "" : " dim"); grid.appendChild(c); return c; });
    let i = 0;
    (function step() {
      for (let k = 0; k < 10 && i < N; k++, i++) cells[i].className = cells[i].dataset.s;
      if (i < N) timer = setTimeout(step, 30);
    })();
    const cnt = (k, s) => d.filter((x) => (k ? x.k === k : true) && x.s === s).length;
    $("sim-msg").innerHTML = `<b>Example ticket:</b> ${T.msg}<br><span style="color:var(--muted)">Should ${T.should}. ${T.why}</span>`;
    let tally;
    if (T.should === "escalate") {
      const e = cnt(t, "esc"), kept = cnt(t, "kept");
      tally = `Of the <b>${T.n}</b> “${T.label.toLowerCase()}” tickets: <b>${e}</b> escalated (right) · <b>${kept}</b> kept by the agent (wrong)`;
    } else {
      const r = cnt(t, "res"), w = cnt(t, "wrong");
      tally = `Of the <b>${T.n}</b> “${T.label.toLowerCase()}” tickets: <b>${r}</b> resolved by the agent (right) · <b>${w}</b> escalated for no reason (wrong)`;
    }
    $("sim-tally").innerHTML = tally;
    const res = cnt(null, "res"), wrong = cnt(null, "wrong"), kept = cnt(null, "kept");
    $("sim-day").innerHTML = `Whole day under this rule: first-contact resolution <b>${res}%</b> (best possible here: 70%) · <b>${wrong}</b> escalated that the agent could have settled · <b>${kept}</b> kept that needed a person`;
    $("sim-effort").innerHTML = `Build and upkeep: ${"●".repeat(R.effort)}${"○".repeat(3 - R.effort)} (${R.effortText})`;
    $("sim-verdict").className = "box " + o.c;
    $("sim-verdict").innerHTML = `<span class="chip ${o.c}">${o.v}</span> ${o.note}`;
    const h = HANDOFF[t];
    $("sim-handoff").innerHTML = h
      ? `<div class="grid2"><div class="box rose" style="margin:0"><b>Thin handoff</b><br>“Customer needs help.” + link to the chat<br><span style="font-size:.9rem;color:var(--muted)">The person reads the whole chat, or asks the customer again.</span></div>` +
        `<div class="box mint" style="margin:0"><b>Structured handoff</b><table class="ho"><tr><td>Customer</td><td>${h.id}</td></tr><tr><td>Cause</td><td>${h.cause}</td></tr><tr><td>Amount</td><td>${h.amount}</td></tr><tr><td>Next step</td><td>${h.action}</td></tr></table></div></div>`
      : `<p style="margin:0">No handoff needed: the agent should settle this one itself.</p>`;
  }

  window.addEventListener("DOMContentLoaded", draw);
})();
