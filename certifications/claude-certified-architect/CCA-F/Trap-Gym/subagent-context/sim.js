/* Subagent context simulator. Fully scripted: every prompt, output and time comes from the fixed tables below,
   so the same choice always plays the same run and a recording can be repeated. Times are illustrative. */
(function () {
  const KNOWS = ["the topic", "the vetted trial results", "the chair's size rule", "where each figure came from"];
  const SECTIONS = ["Efficacy", "Safety", "Cost"];
  const SPAWN = 4; // seconds the coordinator spends writing each Task call (illustrative)
  const SCALE = 320; // timeline width in seconds, fixed so runs can be compared by eye

  const PROMPT = {
    task: {
      label: "Just the task",
      text: "Write the efficacy section of the committee summary:\nDravelin versus placebo, monthly migraine days.",
      k: [1, 0, 0, 0], dur: [104, 96, 90], warn: true,
      out: "Across four trials, Dravelin cut migraine days by 1.6 to 3.0 a month versus placebo. The largest effect came from CEDAR (3.0 days), and an early pilot also looked promising.",
      cites: "Its own search results: four trials, two the committee never vetted.",
      facts: [["Repeats the research", "rose"], ["Includes CEDAR (140 patients), which the chair excluded", "rose"], ["No links to the vetted sources", "rose"]],
      v: ["Breaks", "rose", "It knew the topic but not the findings, so it searched again, picked up trials the chair ruled out, and cited sources nobody checked."],
    },
    prose: {
      label: "Task + findings as prose",
      text: "Write the efficacy section of the committee summary.\nOur research found that Dravelin cut monthly migraine days by\n2.1 in a large journal trial and by 1.6 in a second trial we\nfound in the registry. The chair wants small trials left out,\nso ignore the one with 140 patients.",
      k: [1, 1, 1, 0], dur: [44, 40, 36], warn: true,
      out: "In the two large trials, Dravelin cut migraine days by 1.6 to 2.1 a month versus placebo (a journal trial and a registry trial). A smaller trial was left out at the chair's request.",
      cites: "“a journal trial”, “a registry trial”: no URL, no document name, no page.",
      facts: [["Right figures", "mint"], ["Chair's rule kept", "mint"], ["Sources lost: a reviewer can't check a single figure", "rose"]],
      v: ["Only partly works", "butter", "The facts survived, but the sources were folded into sentences and lost. The guide asks for a structured format that keeps content apart from metadata."],
    },
    structured: {
      label: "Task + structured findings and sources",
      text: "Task: write the efficacy section of the committee summary.\nGoal: Dravelin versus placebo, monthly migraine days.\nRules from the chair: leave out trials under 200 patients.\nFindings (from the research subagent, complete):\n  - claim: 2.1 fewer migraine days a month\n    trial: ARC-1, 1,240 patients\n    source: ARC-1 final report, p. 14\n    url: https://journal.example.org/arc-1\n  - claim: 1.6 fewer migraine days a month\n    trial: BELL-2, 860 patients\n    source: Registry record BELL-2, p. 6\n    url: https://registry.example.org/bell-2\n  - claim: 3.0 fewer migraine days a month\n    trial: CEDAR, 140 patients (excluded by the rule)\n    source: CEDAR poster, p. 2\nReturn: the section text, with a citation after each figure.",
      k: [1, 1, 1, 1], dur: [42, 38, 34], warn: false,
      out: "In the two trials that meet the committee's size rule, Dravelin cut migraine days by 2.1 a month [ARC-1 final report, p. 14] and 1.6 a month [Registry record BELL-2, p. 6] versus placebo. CEDAR (140 patients) was left out under the committee's rule.",
      cites: "Every figure carries its document and page; the URLs are in the source list.",
      facts: [["Right figures", "mint"], ["Chair's rule kept", "mint"], ["Every figure cited", "mint"]],
      v: ["Best fit (exam answer)", "mint", "Complete findings, the user's rule and the sources, with content kept apart from metadata. The subagent needs nothing it wasn't given."],
    },
    none: {
      label: "Nothing: “use what we found above”",
      text: "Write the efficacy section from what we found above.",
      k: [0, 0, 0, 0], dur: [8, 7, 7], warn: true,
      out: "I don't have any earlier findings in my context. Please send the trials, the results and the sources you want summarised.",
      cites: "None. There was nothing to cite.",
      facts: [["Never saw the coordinator's history", "rose"], ["The job comes back undone", "rose"], ["The coordinator must send it all again", "rose"]],
      v: ["Breaks", "rose", "There is no “above”. Subagents have isolated context: they inherit nothing from the coordinator, so the prompt is the only channel."],
    },
  };

  const SPAWNS = {
    par: { label: "Three Task calls in one response (parallel)" },
    seq: { label: "One Task call per turn (sequential)" },
  };
  const TOOLS = {
    yes: { label: "allowedTools: [\"Task\", \"Read\"]" },
    no:  { label: "allowedTools: [\"Read\"]" },
  };

  const $ = (id) => document.getElementById(id);
  let p = "task", s = "par", t = "yes", timer = null;

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

  const esc = (x) => String(x).replace(/&/g, "&amp;").replace(/</g, "&lt;");
  const fmt = (sec) => (sec >= 60 ? `${Math.floor(sec / 60)} min ${sec % 60} s` : `${sec} s`);

  // Bars: [lane, start, length, class, label]
  function plan() {
    const P = PROMPT[p];
    const bars = [];
    let end = 0;
    if (s === "par") {
      bars.push(["Coordinator", 0, SPAWN * 3, "co", ""]);
      P.dur.forEach((d, i) => { bars.push([SECTIONS[i], SPAWN * 3, d, "sub" + (P.warn ? " warn" : ""), d + " s"]); end = Math.max(end, SPAWN * 3 + d); });
    } else {
      let at = 0;
      P.dur.forEach((d, i) => {
        bars.push(["Coordinator", at, SPAWN, "co", ""]);
        bars.push([SECTIONS[i], at + SPAWN, d, "sub" + (P.warn ? " warn" : ""), d + " s"]);
        at += SPAWN + d;
      });
      end = at;
    }
    return { bars, end };
  }

  function timeline(bars) {
    const lanes = ["Coordinator"].concat(SECTIONS);
    return lanes.map((lane) => {
      const bs = bars.filter((b) => b[0] === lane).map((b) =>
        `<div class="tl-b ${b[3]}" style="left:${(b[1] / SCALE) * 100}%;width:${(b[2] / SCALE) * 100}%">${b[4]}</div>`).join("");
      const sub = lane === "Coordinator" ? "writes Task calls" : "subagent";
      return `<div class="tl-row"><div class="tl-l">${lane}<small>${sub}</small></div><div class="tl-t">${bs}</div></div>`;
    }).join("");
  }

  function draw() {
    buttons("sim-p", PROMPT, p, (k) => { p = k; });
    buttons("sim-s", SPAWNS, s, (k) => { s = k; });
    buttons("sim-t", TOOLS, t, (k) => { t = k; });
    ["box-prompt", "box-fan", "box-tools"].forEach((id) => { const r = $(id); if (r) r.setAttribute("stroke-width", "1.5"); });
    run();
  }

  function run() {
    clearTimeout(timer);
    const P = PROMPT[p];
    const trail = $("sim-trail");
    let steps, verdict, tally;
    if (t === "no") {
      steps = [
        ["1. The coordinator tries to delegate", `<pre>Task(description="efficacy section", prompt=...)</pre>`],
        ["2. What happens", `<div class="told">The Task tool isn't in the coordinator's allowedTools, so the call is refused. No subagent starts.</div>`],
        ["3. What the subagents know", `<span class="chip rose">no subagent exists</span>`],
      ];
      $("sim-tl").innerHTML = timeline([["Coordinator", 0, 6, "co", "refused"]]);
      tally = `<span class="chip">Total</span>nothing delegated`;
      verdict = ["Breaks", "rose", "Subagents are spawned with the Task tool, and allowedTools must include \"Task\". Fix that first; the prompt doesn't matter yet."];
      ["box-tools"].forEach((id) => { const r = $(id); if (r) r.setAttribute("stroke-width", "4"); });
    } else {
      const knows = KNOWS.map((n, i) => `<span class="chip ${P.k[i] ? "mint" : "rose"}">${P.k[i] ? "" : "missing: "}${n}</span>`).join("");
      steps = [
        ["1. The Task prompt for the efficacy writer (the other two get the same treatment)", `<pre>${esc(P.text)}</pre>`],
        ["2. What the subagent knows", knows],
        ["3. What it writes", `<div class="told">${esc(P.out)}</div><div style="font-size:.9rem;margin-top:4px"><b>Citations:</b> ${esc(P.cites)}</div>`],
        ["4. Check against the committee's needs", P.facts.map((f) => `<span class="chip ${f[1]}">${esc(f[0])}</span>`).join("")],
      ];
      const pl = plan();
      $("sim-tl").innerHTML = timeline(pl.bars);
      const other = s === "par" ? null : (() => { const q = s; s = "par"; const e = plan().end; s = q; return e; })();
      tally = `<span class="chip">Time to all three sections</span>${fmt(pl.end)}` +
        (s === "seq" ? ` <span style="color:var(--muted)">(in parallel it would be ${fmt(other)}; the sections don't depend on each other)</span>` : "") +
        (p === "none" ? `<br><span class="chip rose">Not done</span>all three come back asking for the findings; the coordinator must send them again` : "");
      verdict = P.v.slice();
      if (s === "seq") {
        if (p === "structured") verdict = ["Right content, too slow", "butter", "The output is right, but three independent sections wait in a queue. Send several Task calls in one response so they run in parallel."];
        else verdict = [P.v[0] + ", and slow", P.v[1], P.v[2] + " Sending one call per turn also makes it wait in a queue."];
      }
      const r1 = $("box-prompt"); if (r1) r1.setAttribute("stroke-width", "4");
      if (s === "seq") { const r2 = $("box-fan"); if (r2) r2.setAttribute("stroke-width", "4"); }
    }
    trail.innerHTML = "";
    const els = steps.map(([h, body]) => {
      const d = document.createElement("div");
      d.className = "step";
      d.innerHTML = `<b>${h}</b><div>${body}</div>`;
      trail.appendChild(d);
      return d;
    });
    let i = 0;
    (function step() { if (i < els.length) { els[i++].classList.add("in"); timer = setTimeout(step, 200); } })();
    $("sim-tally").innerHTML = tally;
    $("sim-verdict").className = "box " + verdict[1];
    $("sim-verdict").innerHTML = `<span class="chip ${verdict[1]}">${verdict[0]}</span> ${verdict[2]}`;
  }

  window.CtxSim = { PROMPT, SPAWNS, TOOLS };
  window.addEventListener("DOMContentLoaded", draw);
})();
