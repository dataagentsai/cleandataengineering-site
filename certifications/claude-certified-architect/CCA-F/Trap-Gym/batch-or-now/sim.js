/* Batch or now? simulator. Deterministic: the batch completion time for each job comes from a
   seeded generator, so the same choice always shows the same result and a recording can be repeated.
   Prices, token counts and times are illustrative, chosen to show the shape the exam guide describes
   (batch: 50% cost savings, up to a 24-hour window, no latency SLA, no multi-turn tool calling). */
(function () {
  const PRICE = 3; // illustrative $ per million input tokens, standard API; batch is half.
  const JOBS = {
    pr:      { label: "Pre-merge pull-request review", kind: "Developers wait", tone: "rose",
               reqs: 300, unit: "reviews a week", tok: 40000, trimTok: 12000,
               trimText: "the diff and the changed files only", fullText: "every file in the changed modules",
               needH: 10 / 60, needText: "within about 10 minutes", scaleH: 24, syncH: 1 / 60, syncText: "about 40 seconds each" },
    weekly:  { label: "Weekly risk report, read on Monday", kind: "Nobody waits", tone: "mint",
               reqs: 200, unit: "modules a week", tok: 120000, trimTok: 8000,
               trimText: "the build file and lockfile only", fullText: "each module's whole source tree",
               needH: 59, needText: "by the Monday 9:00 meeting (59 h after the Saturday run)", scaleH: 72, syncH: 0.5, syncText: "about 30 minutes for all of them" },
    archive: { label: "Re-extract 40,000 documents, due next week", kind: "Nobody waits", tone: "mint",
               reqs: 40000, unit: "documents", tok: 6000, trimTok: 6000,
               trimText: "the document, which is all it reads already", fullText: "the document",
               needH: 168, needText: "by the end of next week", scaleH: 192, syncH: 30, syncText: "about 30 hours, scheduled around live traffic" },
    agent:   { label: "Support agent that calls tools mid-chat", kind: "Needs tool calls", tone: "butter",
               reqs: 28000, unit: "turns a week (7,000 chats, 4 turns each)", tok: 10000, trimTok: 10000,
               trimText: "the chat so far, which it needs", fullText: "the chat so far",
               needH: 1 / 60, needText: "within seconds, each turn", scaleH: 24, syncH: 1 / 360, syncText: "a few seconds per turn" },
  };
  const APIS = { sync: { label: "Synchronous Messages API" }, batch: { label: "Message Batches API" } };
  const TRIMS = { full: { label: "Everything it sends today" }, trim: { label: "Trimmed to what the job reads" } };

  // Verdicts: [chip, tone, note]. Keyed job -> api -> trim.
  const OUT = {
    pr: {
      sync:  { full: ["Right API", "mint", "Developers get their comments in under a minute. It costs full price, and most of the tokens are files the review never comments on. Try trimming."],
               trim: ["Best fit", "mint", "Still synchronous, so nobody waits, and about 70% cheaper because each request carries only what the review reads."] },
      batch: { full: ["Blocks the team", "rose", "Half price, but the review came back hours after developers needed it. A batch has no latency promise: up to 24 hours. Polling faster doesn't make it finish sooner."],
               trim: ["Blocks the team", "rose", "Cheapest of all, and still useless for a blocking check. The saving from trimming didn't need a batch."] },
    },
    weekly: {
      sync:  { full: ["Pays double", "butter", "It works, but nobody reads the report until Monday. You paid full price for speed that was never used."],
               trim: ["Pays double", "butter", "Trimming saved most of the cost, but the remaining calls still pay full price for a report read days later."] },
      batch: { full: ["Right fit", "mint", "Half price, results back long before Monday. Now trim the requests: most of the tokens are source code the report never reads."],
               trim: ["Best fit", "mint", "Half price and a fraction of the tokens. Every module is still rated, ready well before the meeting."] },
    },
    archive: {
      sync:  { full: ["Pays double", "butter", "It finishes in time, but every call pays full price, and someone has to schedule and watch the run around live traffic."],
               trim: ["Pays double", "butter", "Nothing to trim here: each request is already just the document. The extra cost is the full price."] },
      batch: { full: ["Best fit", "mint", "Single calls, no tools, due next week: half the cost, and custom_id matches each result to its document. Resubmit only the failures by custom_id."],
               trim: ["Best fit", "mint", "Same as before: each request was already lean, so trimming changes nothing. Batch is the saving here."] },
    },
    agent: {
      sync:  { full: ["Right fit", "mint", "Each turn returns in seconds. When Claude asks for a tool, your code runs it and sends the result straight back."],
               trim: ["Right fit", "mint", "Nothing to trim: each turn needs the chat so far. Synchronous is the only way this agent works."] },
      batch: { full: ["Doesn't work", "rose", "A batch request returns one reply. Claude's reply stops at a tool call, and nothing in the batch runs the tool and carries on. Each round trip would be a new batch of up to 24 hours, while the customer waits."],
               trim: ["Doesn't work", "rose", "Trimming doesn't help: the problem is the tool loop, not the size. A batch request can't do multi-turn tool calling."] },
    },
  };

  function rng(seedStr) {
    let h = 1779033703 ^ seedStr.length;
    for (let i = 0; i < seedStr.length; i++) { h = Math.imul(h ^ seedStr.charCodeAt(i), 3432918353); h = (h << 13) | (h >>> 19); }
    let a = h >>> 0;
    return function () { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  }
  // One fixed example batch time per job, between 2 and 20 hours.
  const batchH = (j) => Math.round((2 + 18 * rng("batch:" + j)()) * 6) / 6;

  const $ = (id) => document.getElementById(id);
  let j = "pr", a = "batch", r = "full", timer = null;

  const money = (x) => "$" + (x >= 100 ? Math.round(x).toLocaleString("en-US") : x.toFixed(2));
  const hrs = (h) => {
    if (h < 1 / 60) return "seconds";
    if (h < 1) return Math.round(h * 60) + " min";
    if (h >= 48) return Math.round(h / 24 * 10) / 10 + " days";
    const m = Math.round(h * 60);
    return `${Math.floor(m / 60)} h ${String(m % 60).padStart(2, "0")} min`;
  };

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
    const on = a === "sync" ? ["box-code", "box-sync"].concat(j === "agent" ? ["box-tool"] : []) : ["box-reqs", "box-batch", "box-results"];
    ["box-code", "box-sync", "box-tool", "box-reqs", "box-batch", "box-results"].forEach((id) => {
      const e = $(id);
      if (e) e.setAttribute("stroke-width", on.includes(id) ? "4" : "1.5");
    });
  }

  function draw() {
    buttons("sim-j", JOBS, j, (k) => (j = k));
    buttons("sim-a", APIS, a, (k) => (a = k));
    buttons("sim-r", TRIMS, r, (k) => (r = k));
    highlight();
    run();
  }

  function run() {
    clearTimeout(timer);
    const J = JOBS[j], o = OUT[j][a][r];
    const tok = r === "trim" ? J.trimTok : J.tok;
    const full = J.reqs * J.tok * PRICE / 1e6;
    const cost = J.reqs * tok * PRICE / 1e6 * (a === "batch" ? 0.5 : 1);
    const works = !(j === "agent" && a === "batch");

    $("sim-cost").textContent = works ? money(cost) : money(cost) + " for nothing";
    $("sim-costsub").innerHTML = `${J.reqs.toLocaleString("en-US")} ${J.unit} × ${(tok / 1000).toLocaleString("en-US")}k tokens (${r === "trim" ? J.trimText : J.fullText})${a === "batch" ? ", at half price" : ""}. Full price, untrimmed: ${money(full)}.`;
    $("sim-costbar").className = a === "batch" || r === "trim" ? "" : "full";

    let arriveH, whenText;
    if (a === "sync") { arriveH = J.syncH; whenText = J.syncText; }
    else if (!works) { arriveH = J.scaleH; whenText = "a reply that stops at the first tool call"; }
    else { arriveH = batchH(j); whenText = `this run: ${hrs(arriveH)}. No promise: up to 24 hours`; }
    const late = !works || arriveH > J.needH;
    $("sim-when").textContent = a === "sync" ? (j === "weekly" || j === "archive" ? hrs(arriveH) : "seconds") : works ? hrs(arriveH) : "never finished";
    $("sim-whensub").textContent = `${whenText}. Needed ${J.needText}.`;
    $("sim-works").textContent = !works ? "No" : late ? "Too late" : "Yes";
    $("sim-workssub").textContent = !works ? "A batch request can't run a tool loop." : late ? "Correct results, but people were blocked waiting." : a === "sync" && (j === "weekly" || j === "archive") ? "Yes, at full price." : "On time.";

    $("sim-need").style.width = Math.max(0.6, 100 * Math.min(J.needH, J.scaleH) / J.scaleH) + "%";
    const got = $("sim-got");
    got.className = "got" + (late ? " late" : "");
    got.style.left = "0%";
    $("sim-costbar").style.width = "0%";
    timer = setTimeout(() => {
      got.style.left = Math.min(98, Math.max(1.5, 100 * arriveH / J.scaleH)) + "%";
      $("sim-costbar").style.width = (100 * cost / full) + "%";
    }, 60);
    const q = J.scaleH;
    $("sim-ticks").innerHTML = [0, q / 4, q / 2, 3 * q / 4, q].map((h) => `<span>${h === 0 ? "start" : hrs(h)}</span>`).join("");

    $("sim-verdict").className = "box " + o[1];
    $("sim-verdict").innerHTML = `<span class="chip ${o[1]}">${o[0]}</span> ${o[2]}`;
  }

  window.addEventListener("DOMContentLoaded", draw);
})();
