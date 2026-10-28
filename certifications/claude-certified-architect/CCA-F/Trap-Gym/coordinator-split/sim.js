/* Coordinator split simulator. Deterministic: every number comes from fixed tables below, so the same
   choice always gives the same run and a recording can be repeated. Times and counts are illustrative. */
(function () {
  const NEED = ["Visual arts", "Music", "Writing", "Film"];
  // dur = seconds for one subagent; src = sources it returns; old = sources older than 2024 when it isn't told the cut-off.
  const SUB = {
    "Visual arts":    { area: "Visual arts", dur: 84, src: 6, old: 3, oldT: 1 },
    "Music":          { area: "Music",       dur: 76, src: 5, old: 2, oldT: 1 },
    "Writing":        { area: "Writing",     dur: 92, src: 6, old: 2, oldT: 2 },
    "Film":           { area: "Film",        dur: 88, src: 5, old: 3, oldT: 1 },
    "Digital art":    { area: "Visual arts", dur: 70, src: 5, old: 2, oldT: 1 },
    "Graphic design": { area: "Visual arts", dur: 81, src: 6, old: 3, oldT: 1 },
    "Photography":    { area: "Visual arts", dur: 74, src: 5, old: 2, oldT: 1 },
  };
  const SPLITS = { narrow: ["Digital art", "Graphic design", "Photography"], broad: NEED };
  const PLAN = 12, SYNTH = 20, CHECK = 15;

  const SITS = {
    gap:   { label: "Whole topics missing", base: { split: "narrow", facts: true, style: "goal", par: true },
             story: "Every subagent reports success, yet the report covers only visual arts. Music, writing and film are missing." },
    rules: { label: "The user's rules ignored", base: { split: "broad", facts: false, style: "goal", par: true },
             story: "The user agreed two rules with the coordinator: sources from 2024 on, written for a museum board. The report quotes older sources anyway." },
    slow:  { label: "The run is too slow", base: { split: "broad", facts: true, style: "goal", par: false },
             story: "The four searches don't depend on each other, but the report takes six minutes to arrive." },
    thin:  { label: "Shallow, misses key studies", base: { split: "broad", facts: true, style: "steps", par: true },
             story: "Each subagent did exactly what its brief said, yet the report misses well-known studies on every topic." },
  };
  const FIXES = {
    none:  { label: "Change nothing", who: "", where: null },
    widen: { label: "Widen the split", who: "coordinator", where: "box-split" },
    facts: { label: "Put the agreed facts in each Task prompt", who: "coordinator", where: "box-brief" },
    goals: { label: "Brief with goals and quality criteria", who: "coordinator", where: "box-brief" },
    par:   { label: "Send all Task calls in one response", who: "coordinator", where: "box-timing" },
    tune:  { label: "Improve the subagents", who: "subagent", where: "box-subs" },
    gap:   { label: "Add a gap check and re-delegate", who: "loop", where: "box-check" },
  };
  const WHO = { coordinator: "peri", subagent: "rose", loop: "butter" };

  // Verdict for every situation x fix.
  const V = {
    gap: {
      none:  ["The problem", "rose", "Each subagent did its topic well. The coordinator only handed out visual-arts topics, so music, writing and film were never researched."],
      widen: ["Right fix", "mint", "The coordinator now splits into visual arts, music, writing and film. Same subagents, full coverage. The fault was the split."],
      facts: ["Different problem", "rose", "The subagents already had the request's facts. Better briefs on the same three visual-arts topics still leave three topics out."],
      goals: ["Different problem", "rose", "The briefs already state goals and a quality bar. The topics they were given are still all visual arts."],
      par:   ["Different problem", "rose", "The calls already go out together. Speed was never the problem; three topics are still missing."],
      tune:  ["Blames the subagent", "rose", "More searches inside digital art, graphic design and photography: more visual-arts sources, still nothing on music, writing or film. Nobody asked for them."],
      gap:   ["Works, but late", "butter", "The check spots the missing topics after round one and sends them out again. Coverage ends complete, after a wasted round, and the split is still wrong next time."],
    },
    rules: {
      none:  ["The problem", "rose", "The rules live in the coordinator's chat with the user. Subagents inherit nothing, and their Task prompts name only the topic."],
      widen: ["Different problem", "rose", "The split already covers all four topics. The subagents still don't know the date rule or the audience."],
      facts: ["Right fix", "mint", "Each Task prompt now carries the 2024 cut-off and the museum-board audience. No old sources. The subagents didn't change; their prompts did."],
      goals: ["Different problem", "rose", "The briefs already state a goal. What's missing are this request's facts, which only the coordinator holds."],
      par:   ["Different problem", "rose", "Already parallel. Faster or slower, the subagents still don't know the rules."],
      tune:  ["Blames the subagent", "rose", "A “prefer recent sources” line in the subagents' own prompts cuts the old sources, but not to zero: “recent” is a guess. Only the coordinator knows this user said 2024."],
      gap:   ["Different problem", "rose", "The check looks for missing topics, and none are missing. The old sources stay in."],
    },
    slow: {
      none:  ["The problem", "rose", "The coordinator sends one Task call, waits for the result, then sends the next. Four independent searches run in a queue."],
      widen: ["Different problem", "rose", "The split is already complete. The searches still wait in line."],
      facts: ["Different problem", "rose", "The briefs already carry the facts. Time is lost in the ordering, not the content."],
      goals: ["Different problem", "rose", "The briefs are already goals. The searches still wait in line."],
      par:   ["Right fix", "mint", "All four Task calls go out in one response and run together. Same work, same quality; the run takes as long as the slowest search."],
      tune:  ["Blames the subagent", "rose", "Asking each subagent for more makes each one slower, and they still wait in line. The time was lost in the coordinator's ordering."],
      gap:   ["Different problem", "rose", "Nothing is missing, so the check only adds time to an already slow run."],
    },
    thin: {
      none:  ["The problem", "rose", "Each brief is a recipe: search one phrase, open the top three results, summarise. The subagents follow it exactly and miss studies outside the top three."],
      widen: ["Different problem", "rose", "All four topics are covered already. Each one is still researched by recipe."],
      facts: ["Different problem", "rose", "The facts are already in the briefs. The recipe still caps what each subagent reads."],
      goals: ["Right fix", "mint", "Each brief now says what the board must decide and what good evidence looks like. The subagents choose their own searches and find the key studies. A little slower, much better."],
      par:   ["Different problem", "rose", "Already parallel. The recipe is the problem, not the timing."],
      tune:  ["Blames the subagent", "rose", "More searches per subagent find a few more key studies, but the step list still decides what they read. The brief says what to do, not what good looks like."],
      gap:   ["Different problem", "rose", "The check looks for missing topics, and all four are there. Thin sections pass straight through."],
    },
  };

  function config(sit, fix) {
    const c = Object.assign({ tuned: false, gap: false }, SITS[sit].base);
    if (fix === "widen") c.split = "broad";
    if (fix === "facts") c.facts = true;
    if (fix === "goals") c.style = "goal";
    if (fix === "par") c.par = true;
    if (fix === "tune") c.tuned = true;
    if (fix === "gap") c.gap = true;
    return c;
  }

  function runSub(name, c) {
    const s = SUB[name];
    let dur = s.dur, src = s.src, key = 3;
    if (c.style === "steps") { dur = Math.round(dur * 0.7); src = 3; key = 1; }
    if (c.tuned) { dur = Math.round(dur * 1.4); src += 3; if (c.style === "steps") key = 2; }
    let old = 0;
    if (!c.facts) old = c.style === "steps" ? 1 : c.tuned ? s.oldT : s.old;
    return { name, area: s.area, dur, src, old, key };
  }

  function brief(name, c) {
    const t = name.toLowerCase();
    if (c.style === "steps") {
      return `Topic: ${name}.\nSteps: 1. search "AI ${t}${c.facts ? " 2024" : ""}". 2. open the top 3 results. 3. summarise each in 100 words.`;
    }
    return `Topic: ${name}.\nGoal: ${c.facts ? "a museum board is deciding what to show next year; find" : "find"} how AI is changing ${t}.` +
      `\nQuality bar: the key studies and reports${c.facts ? ", from 2024 on" : ""}; each claim with its source and date.`;
  }

  function simulate(sit, fix) {
    const c = config(sit, fix);
    const rows = [], coord = [];
    let t = 0;
    coord.push({ s: 0, d: PLAN, l: "plan" }); t = PLAN;
    function round(names, r) {
      const out = names.map((n) => runSub(n, c));
      let end = t;
      out.forEach((o) => {
        const s = c.par ? t : end;
        rows.push(Object.assign({ s, round: r }, o));
        end = Math.max(end, s + o.dur);
      });
      t = end;
      return out;
    }
    let subs = round(SPLITS[c.split], 1);
    coord.push({ s: t, d: SYNTH, l: "write" }); t += SYNTH;
    let covered = new Set(subs.map((o) => o.area));
    let second = false;
    if (c.gap) {
      coord.push({ s: t, d: CHECK, l: "check" }); t += CHECK;
      const miss = NEED.filter((n) => !covered.has(n));
      if (miss.length) {
        second = true;
        subs = subs.concat(round(miss, 2));
        coord.push({ s: t, d: SYNTH, l: "rewrite" }); t += SYNTH;
        covered = new Set(subs.map((o) => o.area));
      }
    }
    let src = 0, old = 0, key = 0;
    subs.forEach((o) => { src += o.src; old += o.old; });
    NEED.forEach((n) => { key += Math.max(0, ...subs.filter((o) => o.area === n).map((o) => o.key)); });
    return { c, rows, coord, total: t, covered, src, old, key, second };
  }

  const $ = (id) => document.getElementById(id);
  const fmt = (s) => (s >= 60 ? `${Math.floor(s / 60)} min ${s % 60} s` : `${s} s`);
  let sit = "gap", fix = "none", timer = null;

  function buttons(boxId, items, current, set, chip) {
    const box = $(boxId);
    box.innerHTML = "";
    Object.entries(items).forEach(([k, v]) => {
      const x = document.createElement("button");
      x.className = "btn" + (k === current ? " on" : "");
      x.innerHTML = v.label + (chip && v.who ? ` <span class="chip ${WHO[v.who]}">${v.who}</span>` : "");
      x.onclick = () => { set(k); draw(); };
      box.appendChild(x);
    });
  }

  function highlight() {
    ["box-split", "box-brief", "box-timing", "box-subs", "box-check"].forEach((id) => {
      const r = $(id);
      if (r) r.setAttribute("stroke-width", id === FIXES[fix].where ? "4" : "1.5");
    });
  }

  function draw() {
    buttons("sim-s", SITS, sit, (k) => { sit = k; });
    buttons("sim-f", FIXES, fix, (k) => { fix = k; }, true);
    $("sim-story").innerHTML = SITS[sit].story;
    highlight();
    run();
  }

  function run() {
    clearTimeout(timer);
    const r = simulate(sit, fix), T = r.total;
    const tl = $("sim-tl");
    tl.innerHTML = "";
    const pct = (x) => (100 * x / T).toFixed(2) + "%";
    const bars = [];
    function row(label, segs, sub) {
      const w = document.createElement("div");
      w.className = "tl-row";
      w.innerHTML = `<div class="tl-l">${label}${sub ? `<small>${sub}</small>` : ""}</div><div class="tl-t"></div>`;
      segs.forEach((g) => {
        const b = document.createElement("span");
        b.className = "tl-b " + g.cls;
        b.style.left = pct(g.s);
        b.dataset.w = pct(g.d);
        b.style.width = "0";
        b.title = g.title || "";
        if (g.l) b.textContent = g.l;
        w.querySelector(".tl-t").appendChild(b);
        bars.push(b);
      });
      tl.appendChild(w);
    }
    row("Coordinator", r.coord.map((g) => ({ s: g.s, d: g.d, cls: "co", l: g.l })));
    r.rows.forEach((o) => {
      const bad = o.old > 0 || o.key < 3;
      const note = `${o.src} sources${o.old ? `, ${o.old} too old` : ""} · key studies ${o.key}/3`;
      row(o.name + (o.round === 2 ? " (round 2)" : ""), [{ s: o.s, d: o.dur, cls: bad ? "sub warn" : "sub" }], note);
    });
    let i = 0;
    (function step() {
      if (i < bars.length) { bars[i].style.width = bars[i].dataset.w; i++; timer = setTimeout(step, 90); }
    })();

    $("sim-cov").innerHTML = NEED.map((n) => r.covered.has(n)
      ? `<span class="chip mint">${n}: covered</span>` : `<span class="chip rose">${n}: missing</span>`).join("");

    const one = r.rows.find((o) => o.area === "Music") || r.rows[0];
    $("sim-brief").textContent = brief(one.name, r.c);
    $("sim-brief-h").textContent = `The Task prompt the ${one.name} subagent receives (all it knows):`;
    const unknown = [];
    if (!r.c.facts) unknown.push("the 2024 cut-off", "the museum-board audience");
    if (r.c.style === "steps") unknown.push("what the board needs to decide", "what counts as good evidence");
    $("sim-unknown").innerHTML = unknown.length
      ? `<b>Not in the prompt, so the subagent can't know:</b> ${unknown.join(", ")}.`
      : "Everything the subagent needs is in the prompt.";

    $("sim-tally").innerHTML = `Topics covered: <b>${r.covered.size} of 4</b> · Sources: <b>${r.src}</b>, of which <b>${r.old}</b> older than 2024` +
      ` · Key studies found: <b>${r.key} of 12</b> · Total time: <b>${fmt(T)}</b>` +
      (r.second ? `<br>A second round was needed for the topics the first split missed.` : "");
    const v = V[sit][fix];
    $("sim-verdict").className = "box " + v[1];
    $("sim-verdict").innerHTML = `<span class="chip ${v[1]}">${v[0]}</span> ${v[2]}`;
  }

  window.CoordSim = { simulate, V, SITS, FIXES };
  window.addEventListener("DOMContentLoaded", draw);
})();
