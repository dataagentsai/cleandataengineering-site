/* Large codebase simulator. Deterministic: the same day and strategy always replay the same run, so a
   recording can be repeated. Token sizes and blur rates are illustrative, chosen to show the shape the
   exam guide describes (in a long exploration answers drift to "typical patterns"; scratchpad files keep
   findings across boundaries; subagents keep verbose output out; manifests recover from a crash;
   /compact reduces context use). */
(function () {
  const W = 200;            // context window, thousand tokens
  const BASE = 8;           // system prompt, CLAUDE.md, tools
  const TURNS = 60;
  const CRASH = 45;
  const CHECKS = [20, 40, 60];
  const isSearch = (n) => n % 6 === 3;           // turns 3, 9, 15 ... 57 search hundreds of files
  const READ = 2.6, SEARCH = 15, SUBSUM = 1.2;    // tokens per read turn, raw search output, subagent summary

  const DAYS = {
    normal: { label: "A long day, no interruptions", kind: "60 turns", tone: "peri",
              intro: "An engineer spends the day with Claude Code mapping how payments are authenticated across a large server/ codebase: 60 turns, with a broad search every sixth turn." },
    crash:  { label: "The laptop crashes at turn 45", kind: "60 turns + a crash", tone: "rose",
              intro: "The same day, but at turn 45 the laptop restarts. The session's context is gone; only what was written to disk survives." },
  };
  const STRATS = {
    keep:     { label: "Just keep going", effort: "nothing extra" },
    remind:   { label: "Ask Claude to keep findings in mind", effort: "one line in the prompt" },
    scratch:  { label: "Scratchpad file of key findings", effort: "Claude appends each finding to FINDINGS.md and reads it when asked" },
    sub:      { label: "Subagents for verbose searches", effort: "each broad search runs in a subagent that returns a short summary" },
    compact:  { label: "/compact when the meter is high", effort: "you run /compact when the context passes 70%" },
    manifest: { label: "Structured manifest", effort: "Claude keeps manifest.json: findings with file and line, modules done, modules left, next step" },
    combo:    { label: "Scratchpad + subagents + /compact", effort: "a findings file, subagents for broad searches, and /compact at 70%" },
  };

  const FINDINGS = [
    { at: 4,  label: "Where requests are authenticated", exact: "server/middleware/session_guard.ts, line 41", vague: "“typically an auth middleware”" },
    { at: 11, label: "Where the tenant comes from", exact: "JWT claim org_id (auth/claims.ts:18)", vague: "“from the token, as usual”" },
    { at: 19, label: "Unguarded route", exact: "/v1/refund skips session_guard (routes/legacy.ts:73)", vague: "“legacy routes may differ”" },
    { at: 28, label: "Webhook check", exact: "signature checked in routes/stripe_hook.ts:22", vague: "“webhooks are usually verified”" },
    { at: 37, label: "Payment retries", exact: "jobs/retry_payment.ts: 3 attempts, no idempotency key", vague: "“retries follow typical patterns”" },
    { at: 52, label: "Card numbers in logs", exact: "masked by lib/redact.ts before logging", vague: "“sensitive data is probably masked”" },
  ];
  // What Claude says at a check-in when asked "Where are requests authenticated?" (finding 1).
  const SAY = {
    exact: "In server/middleware/session_guard.ts, line 41, before every /api route.",
    vague: "Typically an Express app authenticates in a middleware before the routes.",
    lost:  "I believe it happens in routes/index.ts.",
    crash: "I haven't seen the authentication code in this session.",
  };

  const OUT = {
    normal: {
      keep:     { v: "Breaks", c: "rose", note: "The meter hit the limit and auto-compacted. Early findings came back as “typical patterns”, and the answer to the same question changed between check-ins." },
      remind:   { v: "Only usually works", c: "butter", note: "An instruction isn't storage. A few findings held on longer, but they still lived only in the context, and the compaction still blurred them." },
      scratch:  { v: "Also works", c: "mint", note: "Every finding comes back exact from FINDINGS.md. The context still filled with search output and auto-compacted, so the session ran crowded." },
      sub:      { v: "Helps, not enough", c: "butter", note: "The searches stayed in subagents, so the meter stayed lower. But the findings lived only in a long context, and the early ones still blurred." },
      compact:  { v: "Helps, not enough", c: "butter", note: "/compact freed room before the limit, and condensed well. Nothing was written down, though, so some specifics still blurred in the summaries." },
      manifest: { v: "Also works", c: "mint", note: "Findings survive exactly, like a scratchpad, and the progress list is ready if anything goes wrong. On a day with no crash, the scratchpad would do." },
      combo:    { v: "Best fit (exam answer)", c: "mint", note: "Findings live in a file, searches stay in subagents, and /compact clears the rest. The meter stays low and every answer names the exact file." },
    },
    crash: {
      keep:     { v: "Loses findings", c: "rose", note: "The crash wiped the context, and nothing was on disk. Five findings are gone; getting them back means redoing the morning." },
      remind:   { v: "Loses findings", c: "rose", note: "The reminder lived in the context too. The crash took it, along with every finding." },
      scratch:  { v: "Also works", c: "mint", note: "FINDINGS.md brought every finding back. It did not say which modules were finished, so a few turns were spent re-checking them." },
      sub:      { v: "Loses findings", c: "rose", note: "The subagents kept the context tidy, but their summaries lived in the context too. The crash took them." },
      compact:  { v: "Loses findings", c: "rose", note: "/compact reduces context use. It doesn't write anything to disk, so the crash still wiped the findings." },
      manifest: { v: "Best fit (exam answer)", c: "mint", note: "The new session read manifest.json and knew the findings, the modules done and the next step. It carried on at turn 46 with nothing redone." },
      combo:    { v: "Also works", c: "mint", note: "The findings file survived the crash, but it did not record which modules were done, so a few turns went on re-checking them. A manifest would have saved those too." },
    },
  };
  const REDO_SCRATCH = 8;   // turns spent re-checking finished modules after a crash, with findings but no progress list

  function rng(seedStr) {
    let h = 1779033703 ^ seedStr.length;
    for (let i = 0; i < seedStr.length; i++) { h = Math.imul(h ^ seedStr.charCodeAt(i), 3432918353); h = (h << 13) | (h >>> 19); }
    let a = h >>> 0;
    return function () { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  }

  function simulate(dk, sk) {
    // Common random numbers: each finding gets the same dice under every strategy.
    const u = (fi, k) => rng("lc:" + fi + ":" + k)();
    const file = sk === "scratch" || sk === "manifest" || sk === "combo";
    const sub = sk === "sub" || sk === "combo";
    const manual = sk === "compact" || sk === "combo";
    const pDrift = sk === "remind" ? 0.3 : 0.55;
    const F = FINDINGS.map((f) => ({ f, state: null, where: null, trail: [], born: 0 }));
    let used = BASE, total = 0, peak = 0, redo = 0, crashed = false;
    const frames = [], events = [], checks = [];

    function compactPass(n, isManual) {
      const from = used;
      F.forEach((x, fi) => {
        if (x.where !== "ctx") return;
        const k = (isManual ? "m" : "a") + events.length;
        if (x.state === "exact" && u(fi, k) < (isManual ? 0.35 : 0.5)) { x.state = "vague"; x.trail.push("vague"); }
        else if (x.state === "vague" && u(fi, k + "v") < (isManual ? 0.2 : 0.5)) { x.state = "lost"; x.trail.push("lost"); }
      });
      used = BASE + (file ? 1 : 0) + (isManual ? 14 : 12) + 6 * READ;
      events.push({ kind: isManual ? "compact" : "auto", at: n, from, to: used });
    }

    function drift(n) {
      // Context degradation: in a long context, findings far behind the current turn drift to "typical patterns".
      if (used <= 0.5 * W) return;
      F.forEach((x, fi) => {
        if (x.where !== "ctx" || x.state !== "exact") return;
        if (total - x.born > 60 && u(fi, "d" + n) < pDrift) { x.state = "vague"; x.trail.push("vague"); }
      });
    }

    function checkIn(n) {
      const x = F[0];
      const st = x.state === "lost" && x.where === "crash" ? "crash" : file && x.where === "file" ? "exact" : x.state;
      checks.push({ at: n, st });
    }

    let n = 0, stepNo = 0;
    while (n < TURNS) {
      n++;
      stepNo++;
      const tok = isSearch(n) ? (sub ? SUBSUM : SEARCH) : READ;
      used += tok;
      total += tok;
      F.forEach((x) => {
        if (x.f.at === n) { x.state = "exact"; x.where = file ? "file" : "ctx"; x.born = total; x.trail.push("exact"); if (file) used += 0.4; }
      });
      peak = Math.max(peak, used);
      frames.push({ n, used });
      if (manual && used > 0.7 * W) { compactPass(n, true); frames.push({ n, used, ev: events.length - 1 }); }
      else if (used > 0.95 * W) { compactPass(n, false); frames.push({ n, used, ev: events.length - 1 }); }
      if (CHECKS.includes(n)) { drift(n); checkIn(n); }
      if (dk === "crash" && n === CRASH && !crashed) {
        crashed = true;
        const from = used;
        F.forEach((x) => { if (x.state && x.where !== "file") { x.state = "lost"; x.where = "crash"; x.trail.push("crash"); } });
        used = BASE + (file ? 2 : 0);
        events.push({ kind: "crash", at: n, from, to: used });
        frames.push({ n, used, ev: events.length - 1 });
        if (file && sk !== "manifest") {
          redo = REDO_SCRATCH;
          for (let r = 1; r <= redo; r++) { used += READ; total += READ; frames.push({ n, used, redo: r }); }
        }
        if (!file) redo = CRASH - 1;
      }
    }
    drift(TURNS + 1);
    const exact = F.filter((x) => x.state === "exact").length;
    return { dk, sk, o: OUT[dk][sk], frames, events, checks, facts: F, used, peak, exact, redo, file, sub };
  }

  if (typeof module !== "undefined") { module.exports = { simulate, DAYS, STRATS, OUT }; return; }

  /* ---------- the page ---------- */
  const $ = (id) => document.getElementById(id);
  let dk = "normal", sk = "keep", timer = null;
  const STATE = { exact: ["mint", "exact"], vague: ["butter", "“typical patterns”"], lost: ["rose", "gone"], crash: ["rose", "lost in the crash"] };
  const WHERE = { file: "file on disk", ctx: "context only", crash: "was in the context" };
  const fmt = (k) => Math.round(k) + "k";

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
    const on = { keep: [], remind: ["lc-window"], scratch: ["lc-file"], sub: ["lc-sub"], compact: ["lc-compact"], manifest: ["lc-file"], combo: ["lc-file", "lc-sub", "lc-compact"] }[sk];
    ["lc-window", "lc-file", "lc-sub", "lc-compact"].forEach((id) => { const el = $(id); if (el) el.setAttribute("stroke-width", on.includes(id) ? "4" : "1.5"); });
    const t = $("lc-file-title");
    if (t) t.textContent = sk === "manifest" ? "Manifest file" : "Scratchpad file";
  }

  function draw() {
    buttons("lc-d", DAYS, dk, (k) => (dk = k));
    buttons("lc-m", STRATS, sk, (k) => (sk = k));
    highlight();
    run();
  }

  function evText(e) {
    if (e.kind === "crash") return [`rose`, `crash at turn ${e.at}: context ${fmt(e.from)} → empty`];
    if (e.kind === "compact") return [`peri`, `/compact at turn ${e.at}: ${fmt(e.from)} → ${fmt(e.to)}`];
    return [`butter`, `auto-compact at turn ${e.at}: ${fmt(e.from)} → ${fmt(e.to)}`];
  }

  function run() {
    clearTimeout(timer);
    const R = simulate(dk, sk);
    $("lc-intro").textContent = DAYS[dk].intro;
    const fill = $("lc-fill"), lab = $("lc-label"), log = $("lc-events"), ck = $("lc-checks");
    log.innerHTML = "";
    ck.innerHTML = "";
    $("lc-result").style.visibility = "hidden";
    let i = 0, nc = 0;
    (function step() {
      for (let k = 0; k < 2 && i < R.frames.length; k++, i++) {
        const f = R.frames[i];
        const pct = Math.min(100, (f.used / W) * 100);
        fill.style.width = pct + "%";
        fill.className = pct > 70 ? "hot" : "";
        lab.textContent = f.redo ? `After the crash: re-checking finished modules (${f.redo} of ${R.redo}) · ${fmt(f.used)} of ${W}k` : `Turn ${f.n} of ${TURNS} · ${fmt(f.used)} of ${W}k`;
        if (f.ev != null) {
          const [c, t] = evText(R.events[f.ev]);
          const s = document.createElement("span");
          s.className = "chip " + c;
          s.textContent = t;
          log.appendChild(s);
        }
        while (nc < R.checks.length && R.checks[nc].at <= f.n) addCheck(R.checks[nc++]);
      }
      if (i < R.frames.length) timer = setTimeout(step, 22);
      else { while (nc < R.checks.length) addCheck(R.checks[nc++]); finish(R); }
    })();
  }

  function addCheck(c) {
    const tag = c.st === "exact" ? ["mint", "specific"] : c.st === "vague" ? ["butter", "typical patterns"] : c.st === "lost" ? ["rose", "contradicts turn 4"] : ["rose", "starts from nothing"];
    const d = document.createElement("div");
    d.className = "ck";
    d.innerHTML = `<div class="ck-q">Turn ${c.at}: “Where are requests authenticated?”</div><div><b>Claude:</b> ${SAY[c.st]} <span class="chip ${tag[0]}">${tag[1]}</span></div>`;
    $("lc-checks").appendChild(d);
  }

  function finish(R) {
    if (!R.events.length) $("lc-events").innerHTML = `<span class="chip mint">no compaction needed</span>`;
    const rows = R.facts.map((x) => {
      const st = x.where === "crash" ? "crash" : x.state;
      const val = st === "exact" ? x.f.exact : st === "vague" ? x.f.vague : "—";
      return `<tr><td>${x.f.label}<div class="trail">found at turn ${x.f.at}</div></td><td><span class="chip ${STATE[st][0]}">${STATE[st][1]}</span> ${val}<div class="trail">${WHERE[x.where]}</div></td></tr>`;
    }).join("");
    $("lc-table").innerHTML = `<tr><th>Finding</th><th>What Claude has at the end of the day</th></tr>` + rows;
    const autos = R.events.filter((e) => e.kind === "auto").length;
    const answers = new Set(R.checks.map((c) => c.st)).size;
    let t = `<b>${R.exact} of 6</b> findings exact at the end · auto-compactions: <b>${autos}</b> · peak context: <b>${fmt(R.peak)}</b> of ${W}k`;
    t += `<br>Answers to the same question: <b>${answers === 1 && R.checks[0].st === "exact" ? "consistent" : answers === 1 ? "consistently vague" : answers + " different answers"}</b>`;
    if (R.dk === "crash") t += ` · turns to redo after the crash: <b>${R.redo === 0 ? "none" : R.redo === REDO_SCRATCH ? R.redo + " (done above)" : "about " + R.redo + " (not done)"}</b>`;
    $("lc-tally").innerHTML = t;
    $("lc-effort").textContent = "What it takes: " + STRATS[R.sk].effort + ".";
    $("lc-verdict").className = "box " + R.o.c;
    $("lc-verdict").innerHTML = `<span class="chip ${R.o.c}">${R.o.v}</span> ${R.o.note}`;
    $("lc-result").style.visibility = "visible";
  }

  window.addEventListener("DOMContentLoaded", draw);
})();
