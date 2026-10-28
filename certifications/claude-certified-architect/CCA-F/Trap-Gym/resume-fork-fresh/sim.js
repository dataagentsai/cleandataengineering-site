/* Resume, fork or start fresh? simulator. Deterministic: every situation x action pair plays the same
   fixed run, so a recording can be repeated. Minutes are illustrative, chosen to show the shape the exam
   guide describes (--resume continues a prior conversation; fork_session branches from a shared baseline;
   a new session with a structured summary is more reliable than resuming with stale tool results). */
(function () {
  const SITS = {
    same:    { label: "Nothing changed since yesterday", kind: "one path", tone: "mint",
               intro: "Yesterday, in a named session called invoice-rounding, Claude read six billing files and agreed a plan to change how invoices are rounded. Nobody has touched the code since." },
    changed: { label: "A teammate changed 3 of the files overnight", kind: "one path", tone: "rose",
               intro: "Same session, same plan. But overnight a teammate's merge changed three of the six files Claude read yesterday." },
    twoways: { label: "Try two approaches from the same start", kind: "two paths", tone: "butter",
               intro: "Nothing has changed. You want to try two ways to fix the rounding, A (round each line) and B (round once, on the total), and keep the better one." },
  };
  const ACTS = {
    resume:  { label: "--resume invoice-rounding", where: ["box-resume"] },
    tell:    { label: "Resume, and tell it which files changed", where: ["box-resume", "box-tell"] },
    fork:    { label: "fork_session", where: ["box-fork"] },
    fresh:   { label: "New session + structured summary", where: ["box-fresh"] },
    scratch: { label: "New session from scratch", where: ["box-scratch"] },
  };

  // The six files Claude read yesterday. "now" is set only for the files the teammate changed.
  const FILES = [
    { f: "billing/invoice_totals.py", old: "round_cents() rounds the total (line 42)", now: "renamed to round_money() (line 40)", sum: "total is rounded by one helper" },
    { f: "billing/line_items.py", old: "each line is rounded before summing (line 88)", sum: "lines are rounded before summing" },
    { f: "billing/discounts.py", old: "discount applied after rounding (line 31)", now: "discount applied before rounding (line 29)", sum: "discount order matters" },
    { f: "billing/tax.py", old: "TAX_RATE = 0.20 for every region (line 12)", now: "rate read per region from config (line 15)", sum: "tax is added after the discount" },
    { f: "billing/credits.py", old: "credit notes round away from zero (line 57)", sum: "credit notes round differently" },
    { f: "tests/test_totals.py", old: "14 tests, 2 skipped", sum: "14 tests cover totals" },
  ];

  // Status of each file in Claude's context. cur = current; stale = out of date; both = old and new copies
  // in history; reread = read again today; sum = from the summary only; none = not known yet.
  const ST = {
    cur:    ["mint", "current"],
    stale:  ["rose", "stale"],
    both:   ["butter", "old and new copy"],
    reread: ["mint", "read again today"],
    sum:    ["peri", "summary only"],
    none:   ["", "not known yet"],
  };
  function statuses(s, a) {
    return FILES.map((x) => {
      const ch = s === "changed" && !!x.now;
      if (a === "scratch") return "none";
      if (a === "fresh") return ch ? "reread" : "sum";
      if (!ch) return "cur";
      return a === "tell" ? "both" : "stale";
    });
  }
  // Extra row for the two-approach situation: where attempt A's reasoning ends up.
  const AROW = {
    resume:  ["rose", "in the context while B is built", "carried over"],
    tell:    ["rose", "in the context while B is built", "carried over"],
    fork:    ["mint", "only in branch A; branch B never sees it", "kept apart"],
    fresh:   ["mint", "only in session A", "kept apart"],
    scratch: ["mint", "only in session A", "kept apart"],
  };

  // Steps: [kind, text, minutes]. kind: think | ask | do | test | rework.
  const OUT = {
    same: {
      resume:  { steps: [["think", "Claude picks up at yesterday's last message, plan and all", 1], ["do", "Edits invoice_totals.py and line_items.py as planned", 12], ["test", "Runs the tests: 14 pass, 2 skipped as before", 3]],
                 v: "Best fit (exam answer)", c: "mint", note: "Nothing changed, so every tool result in the session is still true. Resuming the named session keeps all of it for free." },
      tell:    { steps: [["ask", "You tell Claude: nothing has changed since yesterday", 1], ["think", "Claude picks up at yesterday's last message", 1], ["do", "Edits invoice_totals.py and line_items.py as planned", 12], ["test", "Runs the tests: 14 pass, 2 skipped as before", 3]],
                 v: "Fine too", c: "mint", note: "There was nothing to tell, so this is just --resume with one extra sentence." },
      fork:    { branches: true, steps: [["think", "fork_session makes branch A and branch B from yesterday's state", 1], ["do", "Branch A edits the two files as planned", 12], ["test", "Runs the tests: 14 pass", 3], ["ask", "Branch B is never used", 0]],
                 v: "Overbuilt", c: "butter", note: "Forking is for two paths. With one plan to carry out, the second branch is just clutter." },
      fresh:   { steps: [["think", "Claude writes a structured summary of yesterday's findings", 4], ["think", "A new session reads the summary", 1], ["think", "Claude re-reads 3 files to see the code it must edit", 8], ["do", "Edits invoice_totals.py and line_items.py", 12], ["test", "Runs the tests: 14 pass", 3]],
                 v: "Loses detail", c: "butter", note: "The summary keeps the findings but not the code they came from, so Claude reads files that were already in the session. Nothing was stale." },
      scratch: { steps: [["think", "A new session explores the billing code from the start", 40], ["think", "Works out yesterday's plan again", 10], ["do", "Edits invoice_totals.py and line_items.py", 12], ["test", "Runs the tests: 14 pass", 3]],
                 v: "Wastes work", c: "butter", note: "Same result, four times slower. Yesterday's exploration was still valid and was thrown away." },
    },
    changed: {
      resume:  { steps: [["think", "Claude picks up at yesterday's last message", 1], ["do", "Edits invoice_totals.py to call round_cents()", 5], ["rework", "Tests fail: round_cents() no longer exists", 6], ["rework", "Rounds after the discount, as it read yesterday: totals off by a cent", 15], ["rework", "EU tax tests fail: it assumed 0.20 for every region", 12], ["think", "Re-reads the 3 files and redoes the edits", 14], ["test", "Runs the tests: pass", 3]],
                 v: "Stale results", c: "rose", note: "Claude trusted yesterday's tool results. Three of them were out of date, and each one became a failed edit." },
      tell:    { steps: [["ask", "You tell Claude which 3 files changed overnight", 1], ["think", "Claude re-reads those 3 files", 6], ["do", "Edits as planned, now using round_money()", 12], ["rework", "One answer mixes in round_cents() from the old copy still in the history; the tests catch it", 5], ["test", "Runs the tests: pass", 3]],
                 v: "Also works", c: "mint", note: "The exam guide says to tell the agent about changes when you resume. It works, but the old copies stay in the history next to the new ones. With only one small change, this would be the best fit." },
      fork:    { branches: true, steps: [["think", "fork_session copies yesterday's state into branch A and branch B", 1], ["rework", "Both branches call round_cents() and round after the discount", 20], ["rework", "Both branches re-read the 3 files and redo their edits", 20], ["test", "Runs the tests in each branch: pass", 6]],
                 v: "Copies the problem", c: "rose", note: "A fork shares the starting point, stale tool results included. Now two branches are wrong in the same way." },
      fresh:   { steps: [["think", "Claude writes a structured summary: findings, decisions, what's left", 4], ["think", "A new session reads the summary", 1], ["think", "Claude re-reads the 3 changed files", 6], ["do", "Edits as planned, now using round_money()", 12], ["test", "Runs the tests: pass", 3]],
                 v: "Best fit (exam answer)", c: "mint", note: "The summary carries what still holds; the changed files are read fresh. No stale tool result is left in the session to mislead Claude." },
      scratch: { steps: [["think", "A new session explores all 6 files from the start", 40], ["think", "Works out yesterday's plan again", 10], ["do", "Edits as planned, using round_money()", 12], ["test", "Runs the tests: pass", 3]],
                 v: "Works, slowly", c: "butter", note: "Nothing is stale, but three unchanged files and yesterday's decisions were redone. A summary would have kept them." },
    },
    twoways: {
      resume:  { steps: [["think", "Resume, then try approach A: round each line", 1], ["do", "Build approach A", 15], ["test", "A: 2 credit-note tests fail", 3], ["do", "Same session: try approach B", 15], ["rework", "B copies A's credit-note workaround, which B never needed", 8], ["test", "B passes, but the comparison is muddied", 3]],
                 v: "Polluted context", c: "butter", note: "It works, but approach A's reasoning was still in the context and coloured approach B. You are not comparing two clean tries." },
      tell:    { steps: [["ask", "Nothing changed, so there is nothing to tell", 0], ["do", "Build approach A", 15], ["test", "A: 2 credit-note tests fail", 3], ["do", "Same session: try approach B", 15], ["rework", "B copies A's credit-note workaround, which B never needed", 8], ["test", "B passes, but the comparison is muddied", 3]],
                 v: "Polluted context", c: "butter", note: "Telling it what changed solves stale results, not two paths. One session still carries attempt A into attempt B." },
      fork:    { branches: true, steps: [["think", "fork_session: branch A and branch B from yesterday's state", 1], ["do", "Branch A builds approach A", 15], ["test", "A: 2 credit-note tests fail", 3], ["do", "Branch B builds approach B", 15], ["test", "B: all tests pass", 3], ["ask", "Compare two clean results and keep B", 2]],
                 v: "Best fit (exam answer)", c: "mint", note: "Both branches start with every tool result from yesterday, and neither sees the other's attempt. That is what fork_session is for." },
      fresh:   { steps: [["think", "Claude writes a structured summary", 4], ["think", "Two new sessions read the summary", 2], ["think", "Each re-reads the code it needs", 10], ["do", "Session A builds approach A", 15], ["test", "A: 2 credit-note tests fail", 3], ["do", "Session B builds approach B", 15], ["test", "B: all tests pass", 3]],
                 v: "Loses detail", c: "butter", note: "Two clean starts, but from a summary, not from yesterday's full tool results. Each session reads the code again. A fork keeps everything." },
      scratch: { steps: [["think", "Two new sessions each explore the billing code from the start", 80], ["do", "Session A builds approach A", 15], ["test", "A: 2 credit-note tests fail", 3], ["do", "Session B builds approach B", 15], ["test", "B: all tests pass", 3]],
                 v: "Wastes work", c: "butter", note: "Clean, but yesterday's exploration is done twice more. fork_session gives both branches that baseline for free." },
    },
  };

  if (typeof module !== "undefined") { module.exports = { SITS, ACTS, FILES, OUT, statuses }; return; }

  const BOXES = ["box-resume", "box-tell", "box-fork", "box-fresh", "box-scratch"];
  const $ = (id) => document.getElementById(id);
  let s = "changed", a = "resume", timers = [];
  const fmt = (min) => (min < 60 ? `${min} min` : `${Math.floor(min / 60)} h ${String(min % 60).padStart(2, "0")} min`);

  function buttons(boxId, items, current, set) {
    const box = $(boxId);
    box.innerHTML = "";
    Object.entries(items).forEach(([k, v]) => {
      const x = document.createElement("button");
      x.className = "btn" + (k === current ? " on" : "");
      x.innerHTML = (k === "resume" || k === "fork" ? `<code>${v.label}</code>` : v.label) + (v.kind ? ` <span class="chip ${v.tone}">${v.kind}</span>` : "");
      x.onclick = () => { set(k); draw(); };
      box.appendChild(x);
    });
  }

  function highlight() {
    BOXES.forEach((id) => { const r = $(id); if (r) r.setAttribute("stroke-width", ACTS[a].where.includes(id) ? "4" : "1.5"); });
    const ov = $("box-overnight");
    if (ov) ov.setAttribute("fill", s === "changed" ? "#fbf0f5" : "#ffffff");
    const ot = $("txt-overnight");
    if (ot) ot.textContent = s === "changed" ? "3 files changed" : "nothing changed";
  }

  function draw() {
    buttons("rf-s", SITS, s, (k) => (s = k));
    buttons("rf-a", ACTS, a, (k) => (a = k));
    highlight();
    run();
  }

  function table() {
    const st = statuses(s, a);
    let stale = 0;
    let rows = FILES.map((x, i) => {
      const k = st[i], ch = s === "changed" && !!x.now;
      if (k === "stale" || k === "both") stale++;
      const believes = k === "none" ? "—" : k === "sum" ? `finding: ${x.sum}` : k === "reread" ? x.now : k === "both" ? `${x.old}, and also: ${x.now}` : x.old;
      const truth = ch ? x.now : x.old;
      const cls = k === "stale" ? ' class="stale"' : k === "both" ? ' class="mixed"' : "";
      return `<tr class="fh"><td colspan="2"><code>${x.f}</code> <span class="chip ${ST[k][0]}">${ST[k][1]}</span></td></tr><tr${cls}><td>${believes}</td><td>${truth}</td></tr>`;
    }).join("");
    if (s === "twoways") {
      const r = AROW[a];
      rows += `<tr class="fh"><td colspan="2">Attempt A's reasoning <span class="chip ${r[0]}">${r[2]}</span></td></tr><tr${r[0] === "rose" ? ' class="stale"' : ""}><td colspan="2">${r[1]}</td></tr>`;
    }
    const brn = OUT[s][a].branches ? `<p class="rf-note">Both branches start with exactly this context.</p>` : "";
    $("rf-table").innerHTML = `<tr><th>What Claude's context says</th><th>What is true now</th></tr>` + rows;
    $("rf-branch").innerHTML = brn;
    return stale;
  }

  function run() {
    timers.forEach(clearTimeout);
    timers = [];
    $("rf-intro").textContent = SITS[s].intro;
    const stale = table();
    const o = OUT[s][a];
    const list = $("rf-steps");
    list.innerHTML = "";
    o.steps.forEach(([k, text, min], i) => {
      const li = document.createElement("li");
      li.className = k === "rework" ? "rw" : "";
      li.innerHTML = `<span class="sw k-${k}"></span><span class="tx">${text}</span><span class="mn">${min ? fmt(min) : ""}</span>`;
      list.appendChild(li);
      timers.push(setTimeout(() => li.classList.add("show"), 120 * i));
    });
    const tot = o.steps.reduce((t, x) => t + x[2], 0);
    const rw = o.steps.filter((x) => x[0] === "rework").reduce((t, x) => t + x[2], 0);
    const best = Math.min(...Object.values(OUT[s]).map((q) => q.steps.reduce((t, x) => t + x[2], 0)));
    $("rf-tally").innerHTML = `Stale tool results in the context: <b>${stale}</b> · Rework: <b>${rw ? fmt(rw) : "none"}</b> · Total: <b>${fmt(tot)}</b>` +
      `<br><span style="color:var(--muted)">Quickest action for this situation: ${fmt(best)}.</span>`;
    $("rf-verdict").className = "box " + o.c;
    $("rf-verdict").innerHTML = `<span class="chip ${o.c}">${o.v}</span> ${o.note}`;
  }

  window.addEventListener("DOMContentLoaded", draw);
})();
