/* Context meter simulator. Deterministic: the same situation and strategy always replay the same run,
   so a recording can be repeated. Token sizes and blur rates are illustrative, chosen to show the shape
   the exam guide describes (summaries blur numbers and promises; the middle of a long context gets
   missed; trimming and a case-facts block fix the cause, a bigger window only postpones it). */
(function () {
  /* ---------- the four situations ---------- */
  function turns(n, tok, extra) { const a = []; for (let i = 1; i <= n; i++) a.push(Object.assign({ tok: tok }, extra ? extra(i) : {})); return a; }

  const SITS = {
    dispute: {
      label: "Long refund dispute", kind: "120 turns", tone: "peri", who: "Agent",
      intro: "A meal-kit customer argues about a spoiled box over three days. Tool results are short. The chat itself is long.",
      window: 200, sys: 6, keep: 12, sumTok: 3,
      steps: turns(120, 3),
      ask: "Customer, turn 120: “So is my money sorted or not?”",
      open: "",
      facts: [
        { at: 6, label: "Amount promised", exact: "$24.00 credit", vague: "“a credit”",
          say: ["Your $24.00 credit is confirmed.", "I can offer you a credit. Would $15 work?", "Let me see what compensation I can offer."] },
        { at: 9, label: "Items spoiled", exact: "chicken thighs x2, spinach, feta", vague: "“some spoiled items”",
          say: ["It covers the chicken thighs x2, the spinach and the feta.", "It covers the spoiled items.", "Which items were affected again?"] },
        { at: 30, label: "Box and date", exact: "box BX-5130, delivered 14 Oct", vague: "“a recent box”",
          say: ["That is box BX-5130 from 14 Oct.", "That is for your recent box.", "Which box was this about?"] },
        { at: 64, label: "What they want", exact: "refund to card, no replacement", vague: "“wants it resolved”",
          say: ["It goes back to your card, as you asked, with no replacement box.", "I'll get this resolved for you.", "Shall I send you a replacement box?"] },
        { at: 98, label: "Next delivery", exact: "Thu 23 Oct, 8–10am", vague: "“a new slot was agreed”",
          say: ["Your next box still arrives Thu 23 Oct, 8–10am.", "Your next delivery is booked.", "When would you like your next box?"] },
      ],
    },
    lookups: {
      label: "Chat with many order lookups", kind: "20 lookups", tone: "peri", who: "Agent",
      intro: "A customer asks about six boxes. Each lookup_order result has about 40 fields; the agent uses 5 of them.",
      window: 200, sys: 6, keep: 8, sumTok: 3, toolTrim: 0.08,
      steps: turns(50, 2, (i) => (i % 5 === 2 || i % 5 === 4 ? { tok: 11, tool: true } : {})),
      ask: "Customer, turn 50: “Great, can you sum up what happens now?”",
      open: "",
      facts: [
        { at: 4, label: "Boxes affected", exact: "BX-5130 and BX-5188", vague: "“two recent boxes”",
          say: ["Boxes BX-5130 and BX-5188 are covered.", "Your two recent boxes are covered.", "Which boxes were affected?"] },
        { at: 12, label: "Refund approved", exact: "$31.50 to card", vague: "“a refund”",
          say: ["$31.50 goes back to your card.", "A refund is on its way. I think it was around $20?", "Let me check whether a refund was agreed."] },
        { at: 20, label: "Allergy", exact: "peanut allergy: no nut swaps", vague: "“has dietary needs”",
          say: ["Replacements will contain no nuts, because of your peanut allergy.", "I've noted your dietary needs.", "I've added a peanut satay kit as a free replacement."] },
        { at: 33, label: "Pause agreed", exact: "pause 1 Nov to 30 Nov", vague: "“a pause next month”",
          say: ["Deliveries pause from 1 Nov to 30 Nov.", "Your deliveries pause next month.", "Did you want to pause at all?"] },
        { at: 45, label: "Promise", exact: "callback Friday before noon", vague: "“will follow up”",
          say: ["A colleague calls you Friday before noon.", "Someone will follow up.", "Is there anything else I can help with?"] },
      ],
    },
    input: {
      label: "One long input that fits", kind: "40 findings", tone: "peri", who: "Synthesis",
      intro: "The synthesis step gets one 170k-token input: findings from 40 papers in the order found. It fits in the window, so nothing is summarised.",
      window: 200, sys: 6, keep: 0, sumTok: 0, input: true,
      steps: turns(40, 4.25),
      ask: "Task: “Write the committee summary.”",
      facts: [
        { at: 2, label: "Paper 2", exact: "n=4,120; risk down 18%", vague: "“a large trial”",
          say: ["Paper 2 (n=4,120) found an 18% risk reduction.", "A large trial found a benefit.", "(paper 2 not mentioned)"] },
        { at: 11, label: "Paper 11", exact: "liver harm in 3% (§4.2)", vague: "“some side effects”",
          say: ["Paper 11 reports liver harm in 3% (§4.2).", "Some side effects were reported.", "(no safety signal mentioned)"] },
        { at: 19, label: "Paper 19", exact: "no benefit over 75 (§5.1)", vague: "“mixed results in older people”",
          say: ["Paper 19 found no benefit over age 75 (§5.1).", "Results in older people were mixed.", "(age limit not mentioned)"] },
        { at: 27, label: "Paper 27", exact: "cost $2,300/yr (§6)", vague: "“costly”",
          say: ["Paper 27 puts the cost at $2,300 a year (§6).", "The drug is costly.", "(cost not mentioned)"] },
        { at: 39, label: "Paper 39", exact: "guideline update 2026", vague: "“a recent guideline”",
          say: ["Paper 39 notes the 2026 guideline update.", "A recent guideline mentions it.", "(guideline status not mentioned)"] },
      ],
    },
    session: {
      label: "Long Claude Code session", kind: "test output piling up", tone: "peri", who: "Claude",
      intro: "An engineer builds seven billing screens in one session. Every few steps a test run dumps long output into the context.",
      window: 200, sys: 10, keep: 6, sumTok: 4, toolTrim: 0.1, trimFrom: 38, compactAt: 38,
      steps: turns(60, 2, (i) => (i % 4 === 0 ? { tok: 12, tool: true } : {})),
      ask: "Engineer, step 60: “Build screen 7 the same way as the others.”",
      facts: [
        { at: 5, label: "Where rounding lives", exact: "InvoiceTotals#round_cents", vague: "“somewhere in billing”",
          say: ["I'll call InvoiceTotals#round_cents for totals,", "I'll use the billing rounding helper,", "I'll round the totals in the screen itself,"] },
        { at: 14, label: "Decision made", exact: "keep banker's rounding", vague: "“rounding was discussed”",
          say: ["keeping banker's rounding as we decided,", "with the rounding we discussed,", "with standard rounding,"] },
        { at: 22, label: "Progress", exact: "screens 1–6 done, 7 left", vague: "“some screens done”",
          say: ["and this is the last screen (1–6 are done).", "and carry on with the remaining screens.", "and start with screen 1."] },
        { at: 30, label: "Team rule", exact: "use the shared Money type", vague: "“follow typical patterns”",
          say: ["Amounts use the shared Money type.", "Amounts follow the typical patterns.", "Amounts are stored as decimals."] },
        { at: 41, label: "Known flaky test", exact: "refund_spec line 88: ignore", vague: "“a flaky test”",
          say: ["The refund_spec line 88 failure is the known flaky one.", "One failure may be the flaky test.", "I'll rewrite refund_spec to fix the failing test."] },
      ],
    },
  };

  const STRATS = {
    big:     { label: "Bigger context window", effortText: "switch to a model with a 1M window; every turn re-sends more" },
    longsum: { label: "Longer, more detailed summaries", effortText: "summaries four times longer" },
    facts:   { label: "Case-facts block", effortText: "code keeps a small block of exact facts outside the summarised history" },
    trim:    { label: "Trim tool results", effortText: "a hook or the tool returns only the fields the agent uses" },
    keyfirst:{ label: "Key facts first + headers", effortText: "a key-points summary at the top, then sections with headers" },
    compact: { label: "/compact", effortText: "a Claude Code command run at a moment you choose" },
  };

  /* ---------- verdicts: one per situation × strategy ---------- */
  const OUT = {
    dispute: {
      big:      { v: "Delays it", c: "butter", note: "No summary pass now, but the turn-30 and turn-64 facts sit in the middle of a 366k history, where they get missed. And every turn re-sends all of it." },
      longsum:  { v: "Only slows the blur", c: "butter", note: "A longer summary keeps more for one pass, but each pass is a summary of a summary. Exact amounts still drift." },
      facts:    { v: "Right fit", c: "mint", note: "Amounts, items, dates and promises live in a block your code keeps word for word. Summaries can blur the chat; they can't touch the block." },
      trim:     { v: "Different problem", c: "butter", note: "The tool results here are already small. Trimming them barely moves the meter, so the summary passes still blur the facts." },
      keyfirst: { v: "Barely helps", c: "butter", note: "A summary with headers holds facts a little better, but it is still rewritten on every pass. The facts need a home outside the summary." },
      compact:  { na: true, v: "Not available here", c: "rose", note: "/compact is a Claude Code command. This is an Agent SDK support agent; the run below is the default." },
    },
    lookups: {
      big:      { v: "Delays it", c: "butter", note: "No summary pass, but 220k of order fields nobody reads now fill the middle, and facts there get missed. The cost per turn grows too." },
      longsum:  { v: "Only slows the blur", c: "butter", note: "A bigger summary keeps a little more, but it takes room the order fields already crowd, and the cause, bulky tool results, stays." },
      facts:    { v: "Helps, not the cause", c: "butter", note: "The facts are safe in the block, but the window still fills with order fields nobody reads, and the passes and the cost stay." },
      trim:     { v: "Right fit", c: "mint", note: "Each lookup keeps 5 fields instead of about 40. The meter never reaches the limit, so nothing is summarised and nothing blurs." },
      keyfirst: { v: "Helps a little", c: "butter", note: "Headers in the summary help, but the window still fills every few lookups. Cut the tool results at the source." },
      compact:  { na: true, v: "Not available here", c: "rose", note: "/compact is a Claude Code command. This is an Agent SDK support agent; the run below is the default." },
    },
    input: {
      big:      { v: "Different problem", c: "butter", note: "The input already fits. More room changes nothing: the middle papers are still read least carefully." },
      longsum:  { na: true, v: "Nothing to act on", c: "rose", note: "Nothing is summarised here; it is one input that fits. The run below is the default." },
      facts:    { na: true, v: "Wrong tool", c: "rose", note: "There is no conversation to carry facts across. For one long input, the same idea is “key facts first + headers”. The run below is the default." },
      trim:     { v: "Different problem", c: "butter", note: "Each finding is already cut to a few fields, so there is nothing left to trim. The middle papers still get missed." },
      keyfirst: { v: "Right fit", c: "mint", note: "A key-findings summary at the top, then one headed section per paper. Nothing important sits only in the middle." },
      compact:  { na: true, v: "Not available here", c: "rose", note: "/compact belongs to an interactive Claude Code session, not a synthesis step. The run below is the default." },
    },
    session: {
      big:      { v: "Delays it", c: "butter", note: "No compaction, but the early findings now sit in the middle of a 280k session full of test output, and Claude starts quoting “typical patterns”." },
      longsum:  { v: "Only slows the blur", c: "butter", note: "Auto-compact keeps more, but it still runs at the limit and still rewrites the early findings." },
      facts:    { v: "Good partner", c: "mint", note: "In Claude Code the case-facts block is a scratchpad file of key findings. It keeps them exact, though the test output still fills the window." },
      trim:     { v: "Helps later, not now", c: "butter", note: "Quieter test runs from here on are a good habit, but the output already in the window stays until something clears it." },
      keyfirst: { v: "Helps a little", c: "butter", note: "A tidier summary holds a bit more, but auto-compact still runs at the limit and rewrites everything." },
      compact:  { v: "Right fit", c: "mint", note: "Run /compact now, while answers are still accurate. Old test output goes; file names and decisions stay. Pair it with a findings file." },
    },
  };

  /* ---------- the engine ---------- */
  function rng(seedStr) {
    let h = 1779033703 ^ seedStr.length;
    for (let i = 0; i < seedStr.length; i++) { h = Math.imul(h ^ seedStr.charCodeAt(i), 3432918353); h = (h << 13) | (h >>> 19); }
    let a = h >>> 0;
    return function () { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  }
  const BLUR = { pb: 0.8, pl: 0.55 };           // chance a pass blurs an exact fact / drops a vague one
  const MIDDLE = { over: 150, risk: 0.55 };       // above 150k tokens, facts in the middle get missed about half the time

  function simulate(sk, mk) {
    const S = SITS[sk], o = OUT[sk][mk] || {};
    const m = o.na ? "none" : mk;
    // Common random numbers: each fact gets the same dice on every strategy, so strategies differ only by mechanics.
    const u = (fi, k) => rng(sk + ":" + fi + ":" + k)();
    const W = m === "big" ? 1000 : S.window;
    let pb = BLUR.pb, pl = BLUR.pl, sumTok = S.sumTok;
    if (m === "longsum") { pb = 0.45; pl = 0.3; sumTok = S.sumTok * 4; }
    if (m === "keyfirst") { pb = 0.6; pl = 0.4; }
    const pinned = m === "facts";
    const steps = S.steps.map((s, i) => {
      const trimmed = m === "trim" && s.tool && S.toolTrim && i + 1 >= (S.trimFrom || 0);
      return { tok: trimmed ? s.tok * S.toolTrim : s.tok, tool: !!s.tool };
    });
    const F = S.facts.map((f) => ({ f: f, state: null, where: null, trail: [] }));
    const base = S.sys + (pinned ? 1 : 0);
    let raw = [], summary = 0, used = base, cost = 0, peak = 0;
    const frames = [], passes = [];

    function pass(stepNo, manual) {
      const keep = raw.slice(-S.keep), go = raw.slice(0, raw.length - S.keep);
      const p = manual ? 0.12 : pb, q = manual ? 0.08 : pl;
      const k = passes.length;
      F.forEach((x, fi) => {
        if (!x.state || x.where === "pinned") return;
        const moving = x.where === "summary" || go.some((g) => g.n === x.f.at);
        if (!moving) return;
        x.where = "summary";
        if (x.state === "exact" && u(fi, k) < p) x.state = "vague";
        else if (x.state === "vague" && u(fi, k) < q) x.state = "lost";
        x.trail.push(x.state);
      });
      raw = keep;
      summary = sumTok;
      const before = used;
      used = base + summary + raw.reduce((a, b) => a + b.tok, 0);
      passes.push({ at: stepNo, manual: !!manual, from: before, to: used });
    }

    steps.forEach((s, i) => {
      const n = i + 1;
      raw.push({ n: n, tok: s.tok });
      used += s.tok;
      F.forEach((x) => { if (x.f.at === n) { x.state = "exact"; x.where = pinned ? "pinned" : "raw"; x.trail.push("exact"); } });
      peak = Math.max(peak, used);
      frames.push({ n: n, used: used });
      if (m === "compact" && n === S.compactAt) { pass(n, true); frames.push({ n: n, used: used, pass: true }); }
      else if (!S.input && used > 0.9 * W) { pass(n, false); frames.push({ n: n, used: used, pass: true }); }
      cost += used;
    });

    // Lost in the middle: in a long context, raw facts away from the start and end may be missed.
    const middleOn = used > MIDDLE.over && !(m === "keyfirst" && S.input);
    if (middleOn) {
      let acc = base + summary;
      const pos = {};
      raw.forEach((x) => { pos[x.n] = (acc + x.tok / 2) / used; acc += x.tok; });
      F.forEach((x, fi) => {
        if (x.where !== "raw" || x.state !== "exact") return;
        const p = pos[x.f.at];
        if (p > 0.15 && p < 0.85 && u(fi, "mid") < MIDDLE.risk) { x.state = "missed"; x.trail.push("missed"); }
      });
    }
    const exact = F.filter((x) => x.state === "exact").length;
    return { S: S, m: m, o: o, W: W, frames: frames, passes: passes, facts: F, used: used, peak: peak, cost: cost, exact: exact, middleOn: middleOn };
  }

  if (typeof module !== "undefined") { module.exports = { simulate, SITS, STRATS, OUT }; return; }

  /* ---------- the page ---------- */
  const $ = (id) => document.getElementById(id);
  let sk = "dispute", mk = "facts", timer = null;
  const STATE = {
    exact:  ["mint", "exact"],
    vague:  ["butter", "blurred"],
    lost:   ["rose", "gone"],
    missed: ["rose", "overlooked"],
  };
  const fmt = (k) => (k >= 1000 ? (k / 1000).toFixed(1) + "M" : Math.round(k) + "k");

  function buttons(boxId, items, current, set) {
    const box = $(boxId);
    box.innerHTML = "";
    Object.entries(items).forEach(([k, v]) => {
      const x = document.createElement("button");
      x.className = "btn" + (k === current ? " on" : "");
      x.innerHTML = v.label + (v.kind ? ` <span class="chip">${v.kind}</span>` : "");
      x.onclick = () => { set(k); draw(); };
      box.appendChild(x);
    });
  }

  function highlight() {
    const where = { big: "cm-window", longsum: "cm-summary", facts: "cm-facts", trim: "cm-tool", keyfirst: "cm-summary", compact: "cm-summary" }[mk];
    ["cm-window", "cm-summary", "cm-facts", "cm-tool"].forEach((id) => {
      const el = $(id);
      if (el) el.setAttribute("stroke-width", id === where ? "4" : "1.5");
    });
  }

  function draw() {
    buttons("cm-s", SITS, sk, (k) => (sk = k));
    buttons("cm-m", STRATS, mk, (k) => (mk = k));
    highlight();
    run();
  }

  function cellFor(x) {
    if (!x.state) return "";
    const st = STATE[x.state];
    const val = x.state === "exact" ? x.f.exact : x.state === "vague" ? x.f.vague : "—";
    return `<span class="chip ${st[0]}">${st[1]}</span> ${val}`;
  }

  function run() {
    clearTimeout(timer);
    const R = simulate(sk, mk), S = R.S, D = simulate(sk, "none");
    $("cm-intro").textContent = S.intro;
    const fill = $("cm-fill"), lab = $("cm-meter-label"), log = $("cm-passes");
    log.innerHTML = "";
    $("cm-result").style.visibility = "hidden";
    let i = 0, npass = 0;
    const frames = R.frames, W = R.W;
    (function step() {
      for (let k = 0; k < 2 && i < frames.length; k++, i++) {
        const f = frames[i];
        const pct = Math.min(100, (f.used / W) * 100);
        fill.style.width = pct + "%";
        fill.className = pct > 85 ? "hot" : "";
        lab.textContent = `${S.input ? "Section" : "Turn"} ${f.n} of ${S.steps.length} · ${fmt(f.used)} of ${fmt(W)}`;
        if (f.pass) {
          const p = R.passes[npass++];
          const li = document.createElement("span");
          li.className = "chip butter";
          li.textContent = `${p.manual ? "/compact" : "summary pass"} at ${S.input ? "section" : "turn"} ${p.at}: ${fmt(p.from)} → ${fmt(p.to)}`;
          log.appendChild(li);
        }
      }
      if (i < frames.length) timer = setTimeout(step, 22);
      else finish(R, D);
    })();
  }

  function finish(R, D) {
    const S = R.S;
    if (!R.passes.length) $("cm-passes").innerHTML = `<span class="chip mint">no summary pass</span>`;
    const rows = R.facts.map((x) => {
      const trail = x.trail.length > 1 ? `<div class="trail">${x.trail.map((t) => STATE[t][1]).join(" → ")}</div>` : "";
      const pin = x.where === "pinned" ? ` <span class="chip peri">in the block</span>` : "";
      return `<tr><td>${x.f.label}<div class="trail">${S.input ? "section" : S.who === "Claude" ? "step" : "turn"} ${x.f.at}</div></td><td>${cellFor(x)}${pin}${trail}</td></tr>`;
    }).join("");
    $("cm-facts-table").innerHTML = `<tr><th>Fact</th><th>What ${S.who.toLowerCase() === "synthesis" ? "the synthesis step" : S.who === "Claude" ? "Claude" : "the agent"} has at the end</th></tr>` + rows;
    const sayIdx = { exact: 0, vague: 1, lost: 2, missed: 2 };
    const said = R.facts.map((x) => x.f.say[sayIdx[x.state]]).join(" ");
    $("cm-ask").textContent = S.ask;
    $("cm-say").innerHTML = `<b>${S.who}:</b> ${said}`;
    let tally = `<b>${R.exact} of 5</b> facts come out exact · <b>${R.passes.length}</b> ${R.passes.length === 1 ? "summary pass" : "summary passes"} · tokens sent over the whole ${S.input ? "input" : "chat"}: <b>${fmt(R.cost)}</b>`;
    if (R.middleOn && R.facts.some((x) => x.state === "missed")) tally += `<br>The context ended at ${fmt(R.used)}; facts in its middle were overlooked.`;
    tally += `<br><span style="color:var(--muted)">With no change: ${D.exact} of 5 exact, ${D.passes.length} ${D.passes.length === 1 ? "pass" : "passes"}, ${fmt(D.cost)} tokens.</span>`;
    $("cm-tally").innerHTML = tally;
    $("cm-effort").textContent = "What it takes: " + STRATS[mk].effortText + ".";
    $("cm-verdict").className = "box " + R.o.c;
    $("cm-verdict").innerHTML = `<span class="chip ${R.o.c}">${R.o.v}</span> ${R.o.note}`;
    $("cm-result").style.visibility = "visible";
  }

  window.addEventListener("DOMContentLoaded", draw);
})();
