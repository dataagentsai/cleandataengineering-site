/* Prompt vs hook simulator. Deterministic: the same choice always gives the same 1,000 chats,
   so a recording can be repeated. Rates are illustrative, chosen to show the shape the exam guide
   describes (prompts: high but non-zero failure rate; hooks: deterministic where they apply). */
(function () {
  const BEHAVIOURS = {
    pause:  { label: "Suggest a pause before escalating a cancellation", kind: "Nice to have", tone: "mint",
              miss: "chats where the customer was not offered a pause" },
    refund: { label: "Refunds above $150 go to a human", kind: "Must hold every time", tone: "rose",
              miss: "refunds above $150 paid out without a human" },
    card:   { label: "Never read a card number to a customer", kind: "Must never happen", tone: "rose",
              miss: "card numbers exposed to a customer" },
    tone:   { label: "Reply in a warm, plain tone", kind: "Style", tone: "mint",
              miss: "replies that sounded stiff" },
  };
  const MECHS = {
    prompt:   { label: "Prompt instruction", where: "box-prompt", effort: 1, effortText: "one line in the system prompt" },
    examples: { label: "Prompt + examples", where: "box-prompt", effort: 1, effortText: "a line plus two or three example chats" },
    pre:      { label: "PreToolUse hook", where: "box-pre", effort: 3, effortText: "code, tests and a deploy" },
    post:     { label: "PostToolUse hook", where: "box-post", effort: 3, effortText: "code, tests and a deploy" },
  };
  // follow = share of chats where the behaviour holds; block = share of chats wrongly blocked.
  const OUT = {
    pause: {
      prompt:   { follow: 0.93, v: "Works", c: "mint", note: "Good enough for a nice-to-have. A few misses cost little." },
      examples: { follow: 0.97, v: "Right size", c: "mint", note: "Cheap, and the examples make the wording consistent. This is the exam's answer." },
      pre:      { follow: 1, block: 0.03, v: "Overbuilt", c: "butter", note: "Code must spot cancellations and spot whether a pause was offered, in free text. When it misreads, customers who want a person get stuck. Lots of machinery for a nicety." },
      post:     { na: true, v: "Wrong hook", c: "rose", note: "There is no tool result to change. The suggestion is something Claude says, not something a tool returns." },
    },
    refund: {
      prompt:   { follow: 0.97, v: "Not reliable enough", c: "rose", note: "Most chats follow the rule, but a few refunds still go through. A rule about money must hold every time." },
      examples: { follow: 0.985, v: "Not reliable enough", c: "rose", note: "Better, still not zero. This is the exam's favourite trap: a clearer prompt for a rule that needs code." },
      pre:      { follow: 1, v: "Right fit", c: "mint", note: "The hook checks every process_refund call before it runs and hands larger ones to a human. Zero misses." },
      post:     { follow: 0.97, late: true, v: "Wrong hook", c: "rose", note: "PostToolUse sees the result after the refund is paid. It can flag the payment, not stop it." },
    },
    card: {
      prompt:   { follow: 0.97, v: "Not reliable enough", c: "rose", note: "Claude still has the number, so now and then it repeats it. For a must-never, “usually” isn't enough." },
      examples: { follow: 0.985, v: "Not reliable enough", c: "rose", note: "Fewer leaks, not zero. Claude still sees the number." },
      pre:      { follow: 1, block: 1, v: "Breaks the agent", c: "rose", note: "PreToolUse acts on the call. Blocking get_customer stops every chat from working, just to hide one field." },
      post:     { follow: 1, v: "Right fit", c: "mint", note: "The hook masks the number in the result before Claude reads it. Claude can't repeat what it never saw." },
    },
    tone: {
      prompt:   { follow: 0.92, v: "Works", c: "mint", note: "Tone is a style. A clear instruction does most of the work." },
      examples: { follow: 0.97, v: "Right size", c: "mint", note: "Examples are the best way to show a tone." },
      pre:      { na: true, v: "Can't do this", c: "rose", note: "Hooks see tool calls and tool results. They can't judge the wording of Claude's reply." },
      post:     { na: true, v: "Can't do this", c: "rose", note: "Hooks see tool calls and tool results. They can't judge the wording of Claude's reply." },
    },
  };
  const N = 1000;

  function rng(seedStr) {
    let h = 1779033703 ^ seedStr.length;
    for (let i = 0; i < seedStr.length; i++) { h = Math.imul(h ^ seedStr.charCodeAt(i), 3432918353); h = (h << 13) | (h >>> 19); }
    let a = h >>> 0;
    return function () { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  }

  const $ = (id) => document.getElementById(id);
  let b = "refund", m = "prompt", timer = null;

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
    ["box-prompt", "box-pre", "box-post"].forEach((id) => {
      const r = $(id);
      if (r) r.setAttribute("stroke-width", id === MECHS[m].where ? "4" : "1.5");
    });
  }

  function draw() {
    buttons("sim-b", BEHAVIOURS, b, (k) => (b = k));
    buttons("sim-m", MECHS, m, (k) => (m = k));
    highlight();
    run();
  }

  function run() {
    clearTimeout(timer);
    const o = OUT[b][m], grid = $("sim-grid"), r = rng(b + ":" + m);
    grid.innerHTML = "";
    const cells = [];
    let miss = 0, block = 0;
    for (let i = 0; i < N; i++) {
      const c = document.createElement("i");
      let s = "na";
      if (!o.na) {
        const x = r();
        if (o.block && x < o.block) { s = "block"; block++; }
        else if (r() > o.follow) { s = "miss"; miss++; }
        else s = "ok";
      }
      c.dataset.s = s;
      cells.push(c);
      grid.appendChild(c);
    }
    let i = 0;
    (function step() {
      for (let k = 0; k < 50 && i < N; k++, i++) cells[i].className = cells[i].dataset.s;
      if (i < N) timer = setTimeout(step, 16);
    })();
    const B = BEHAVIOURS[b], M = MECHS[m];
    let tally;
    if (o.na) tally = `<b>Not possible.</b> ${M.label} has nothing to act on for this behaviour.`;
    else {
      tally = `<b>${N - miss - block}</b> chats followed the behaviour · <b>${miss}</b> ${B.miss}`;
      if (block) tally += ` · <b>${block}</b> chats wrongly blocked`;
      if (o.late) tally += `<br>The hook saw each over-limit refund <i>after</i> it was paid, so it could only report it.`;
    }
    $("sim-tally").innerHTML = tally;
    $("sim-effort").innerHTML = `Build and upkeep: ${"●".repeat(M.effort)}${"○".repeat(3 - M.effort)} (${M.effortText})`;
    $("sim-verdict").className = "box " + o.c;
    $("sim-verdict").innerHTML = `<span class="chip ${o.c}">${o.v}</span> ${o.note}`;
  }

  window.addEventListener("DOMContentLoaded", draw);
})();
