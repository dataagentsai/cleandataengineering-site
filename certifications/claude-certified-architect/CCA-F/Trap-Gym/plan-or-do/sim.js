/* Plan or just do it? simulator. Deterministic: every task x mode pair plays the same fixed steps,
   so a recording can be repeated. Minutes and context figures are illustrative, chosen to show the
   shape the exam guide describes (plan mode prevents rework on big or open changes; a simple,
   well-scoped change needs no plan; the Explore subagent keeps verbose discovery out of the session). */
(function () {
  const TASKS = {
    typo:    { label: "Fix a typo in one error message", kind: "Small, settled", tone: "mint" },
    check:   { label: "Add a validation check: reject an empty email", kind: "Small, settled", tone: "mint" },
    migrate: { label: "Move background jobs to a new library across 40 folders", kind: "Big, approach not agreed", tone: "rose" },
    csv:     { label: "Add a CSV export of bookings", kind: "Nobody said which columns", tone: "butter" },
  };
  const MODES = {
    direct:    { label: "Direct execution", where: ["box-direct"] },
    plan:      { label: "Plan mode", where: ["box-plan"] },
    planx:     { label: "Plan mode + Explore subagent", where: ["box-plan", "box-explore"] },
    interview: { label: "Interview first", where: ["box-interview"] },
    tests:     { label: "Tests first", where: ["box-tests", "box-direct"] },
  };
  // Each step: [kind, text, minutes]. kind: think | ask | do | test | rework.
  // ctx = share of the main session's context used. twice = folders or files edited twice.
  const OUT = {
    typo: {
      direct:    { ctx: 3, steps: [["do", "Claude edits the message", 1], ["test", "Runs the tests: pass", 1]],
                   v: "Right fit", c: "mint", note: "One file, one obvious change. Done in two minutes." },
      plan:      { ctx: 9, steps: [["think", "Claude explores the code", 3], ["think", "Writes a plan for the change", 2], ["ask", "You read and approve the plan", 2], ["do", "Claude edits the message", 1], ["test", "Runs the tests: pass", 1]],
                   v: "Overbuilt", c: "butter", note: "The same one-line change, four times slower. The plan only repeated the ticket." },
      planx:     { ctx: 5, steps: [["think", "Explore subagent searches the code", 3], ["think", "Its summary comes back", 1], ["think", "Claude writes a plan", 2], ["ask", "You read and approve the plan", 2], ["do", "Claude edits the message", 1], ["test", "Runs the tests: pass", 1]],
                   v: "Overbuilt", c: "butter", note: "Even more machinery. There was nothing to discover: you knew the file." },
      interview: { ctx: 4, steps: [["ask", "Claude asks what the message should say", 2], ["ask", "You answer: it's in the ticket", 1], ["do", "Claude edits the message", 1], ["test", "Runs the tests: pass", 1]],
                   v: "More than needed", c: "butter", note: "The ticket already said what was wanted. The questions only cost you time." },
      tests:     { ctx: 4, steps: [["test", "Claude writes a test for the message", 2], ["test", "Runs it: fails, as expected", 1], ["do", "Claude edits the message", 1], ["test", "Runs the tests: pass", 1]],
                   v: "More than needed", c: "butter", note: "A test for a typo is harmless but slower. The change didn't need it." },
    },
    check: {
      direct:    { ctx: 6, steps: [["do", "Claude adds the check to the form validator", 3], ["do", "Adds a test case for an empty email", 2], ["test", "Runs the tests: pass", 1]],
                   v: "Right fit", c: "mint", note: "This is the exam guide's own example: a single validation check is direct execution." },
      plan:      { ctx: 18, steps: [["think", "Claude explores every validator", 5], ["think", "Writes a plan", 4], ["ask", "You read and approve the plan", 3], ["do", "Claude adds the check", 3], ["do", "Adds a test case", 2], ["test", "Runs the tests: pass", 1]],
                   v: "Overbuilt", c: "butter", note: "Three times the time for the same two edits. Nothing in the plan was open." },
      planx:     { ctx: 8, steps: [["think", "Explore subagent maps every validator", 6], ["think", "Its summary comes back", 1], ["think", "Claude writes a plan", 4], ["ask", "You read and approve the plan", 3], ["do", "Claude adds the check", 3], ["do", "Adds a test case", 2], ["test", "Runs the tests: pass", 1]],
                   v: "Overbuilt", c: "butter", note: "A search and a plan for one known file. The slowest way to the same result." },
      interview: { ctx: 8, steps: [["ask", "Claude asks about the rule and the error text", 4], ["ask", "You answer from the ticket", 2], ["do", "Claude adds the check", 3], ["do", "Adds a test case", 2], ["test", "Runs the tests: pass", 1]],
                   v: "More than needed", c: "butter", note: "The rule was already clear. Twice the time for nothing new." },
      tests:     { ctx: 6, steps: [["test", "Claude writes a test for an empty email", 2], ["test", "Runs it: fails, as expected", 1], ["do", "Claude adds the check", 3], ["test", "Runs the tests: pass", 1]],
                   v: "Fine too", c: "mint", note: "Tests first is still direct execution, with the test written first. No plan needed, and the test proves the check works." },
    },
    migrate: {
      direct:    { ctx: 70, twice: 13, steps: [["do", "Claude converts the first folder", 10], ["do", "Converts 12 more folders, job by job", 60], ["rework", "Folder 14 uses a feature only the old library has: stop", 10], ["ask", "The team meets and picks switching everything at once", 20], ["rework", "Redo the 13 converted folders for the new approach", 65], ["do", "Convert the other 27 folders", 110], ["test", "Run the full test suite", 20]],
                   v: "Rework", c: "rose", note: "Editing first picked an approach by default. When the hard jobs showed up, 13 folders were redone." },
      plan:      { ctx: 82, steps: [["think", "Claude searches all 40 folders in the session", 35], ["think", "Finds 6 jobs that use old-only features", 5], ["think", "Compares job by job with all at once", 15], ["ask", "The team approves the plan", 15], ["do", "Convert all 40 folders to the plan", 140], ["test", "Run the full test suite", 20]],
                   v: "Best fit (exam answer)", c: "mint", note: "No rework: the hard jobs were found and the approach agreed before any edit. This is what the exam expects. The raw search output did fill most of the session." },
      planx:     { ctx: 28, steps: [["think", "Explore subagent searches all 40 folders", 30], ["think", "Summary back: 6 jobs use old-only features", 2], ["think", "Claude compares job by job with all at once", 15], ["ask", "The team approves the plan", 15], ["do", "Convert all 40 folders to the plan", 140], ["test", "Run the full test suite", 20]],
                   v: "Also right", c: "mint", note: "Plan mode plus an Explore subagent: the same plan and no rework, and the long search stayed in the subagent, so the session keeps room for the edits." },
      interview: { ctx: 72, twice: 13, steps: [["ask", "Claude asks about goals and the deadline", 10], ["ask", "Nobody knows which jobs use old-only features", 5], ["do", "Claude converts 13 folders, job by job", 70], ["rework", "Hard jobs found mid-way: stop", 10], ["ask", "The team meets and picks switching everything at once", 20], ["rework", "Redo the 13 converted folders", 65], ["do", "Convert the other 27 folders", 110], ["test", "Run the full test suite", 20]],
                   v: "Different problem", c: "rose", note: "Questions draw out what people want. The open questions here were about the code and the design, so the rework still happened." },
      tests:     { ctx: 75, twice: 13, steps: [["test", "Claude writes tests for the jobs in all 40 folders", 60], ["do", "Converts 13 folders until their tests pass", 70], ["rework", "Hard jobs found mid-way: stop", 10], ["ask", "The team meets and picks switching everything at once", 20], ["rework", "Redo the 13 folders and their tests", 80], ["do", "Convert the other 27 folders", 110], ["test", "Run the full test suite", 20]],
                   v: "Wrong order", c: "rose", note: "Tests make each conversion safer, but they don't choose the approach. The rework still happened, with tests to redo as well." },
    },
    csv: {
      direct:    { ctx: 20, twice: 4, steps: [["do", "Claude builds the export with guessed columns", 20], ["test", "Runs the tests: pass", 3], ["ask", "Demo to the product owner", 10], ["rework", "Owner wants other columns, and admins only: rebuild", 25], ["test", "Runs the tests: pass", 3]],
                   v: "Rework", c: "rose", note: "Claude guessed what was wanted. The demo found out, and most of the export was rebuilt." },
      plan:      { ctx: 30, twice: 4, steps: [["think", "Claude explores the bookings code", 8], ["think", "Plans around guessed columns", 6], ["ask", "You approve the plan", 5], ["do", "Claude builds the export", 20], ["test", "Runs the tests: pass", 3], ["ask", "Demo to the product owner", 10], ["rework", "Owner wants other columns, and admins only: rebuild", 25], ["test", "Runs the tests: pass", 3]],
                   v: "Different problem", c: "rose", note: "Plan mode designs the code. The open question was what the owner wanted, so a careful plan was built on a guess." },
      planx:     { ctx: 16, twice: 4, steps: [["think", "Explore subagent maps the bookings code", 7], ["think", "Its summary comes back", 1], ["think", "Claude plans around guessed columns", 6], ["ask", "You approve the plan", 5], ["do", "Claude builds the export", 20], ["test", "Runs the tests: pass", 3], ["ask", "Demo to the product owner", 10], ["rework", "Owner wants other columns, and admins only: rebuild", 25], ["test", "Runs the tests: pass", 3]],
                   v: "Different problem", c: "rose", note: "A tidier session, but the same guess. No amount of code searching tells you which columns the owner wants." },
      interview: { ctx: 18, steps: [["ask", "Claude asks: which columns, who may export, which date format, how many rows", 6], ["ask", "The owner answers", 6], ["do", "Claude builds the export", 20], ["test", "Runs the tests: pass", 3], ["ask", "Demo to the product owner: accepted", 10]],
                   v: "Right fit", c: "mint", note: "Claude asked before building, so the demo was a formality. Fastest of the five." },
      tests:     { ctx: 22, twice: 4, steps: [["test", "Claude writes tests for guessed columns", 10], ["do", "Builds the export until they pass", 20], ["test", "Runs the tests: pass", 3], ["ask", "Demo to the product owner", 10], ["rework", "Owner wants other columns: rewrite the tests and the export", 30], ["test", "Runs the tests: pass", 3]],
                   v: "Wrong order", c: "rose", note: "The tests locked in the guesses. Both the tests and the code were redone." },
    },
  };
  const BOXES = ["box-direct", "box-tests", "box-plan", "box-explore", "box-interview"];

  const $ = (id) => document.getElementById(id);
  let t = "typo", m = "plan", timers = [];

  const fmt = (min) => (min < 60 ? `${min} min` : `${Math.floor(min / 60)} h ${String(min % 60).padStart(2, "0")} min`);
  const total = (o) => o.steps.reduce((s, x) => s + x[2], 0);

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
    BOXES.forEach((id) => {
      const r = $(id);
      if (r) r.setAttribute("stroke-width", MODES[m].where.includes(id) ? "4" : "1.5");
    });
  }

  function draw() {
    buttons("sim-t", TASKS, t, (k) => (t = k));
    buttons("sim-m", MODES, m, (k) => (m = k));
    highlight();
    run();
  }

  function run() {
    timers.forEach(clearTimeout);
    timers = [];
    const o = OUT[t][m];
    // Scale the bar to the slowest mode for this task, so modes compare at a glance.
    const scale = Math.max(...Object.values(OUT[t]).map(total));
    const bar = $("sim-bar"), list = $("sim-steps");
    bar.innerHTML = "";
    list.innerHTML = "";
    o.steps.forEach(([k, text, min], i) => {
      const seg = document.createElement("i");
      seg.className = "k-" + k;
      seg.style.width = "0%";
      seg.title = `${text} (${fmt(min)})`;
      bar.appendChild(seg);
      const li = document.createElement("li");
      if (k === "rework") li.className = "rw";
      li.innerHTML = `<span class="sw k-${k}"></span><span class="tx">${text}</span><span class="mn">${fmt(min)}</span>`;
      list.appendChild(li);
      timers.push(setTimeout(() => { seg.style.width = (100 * min / scale) + "%"; li.classList.add("show"); }, 120 * i));
    });
    const T = total(o), R = o.steps.filter((s) => s[0] === "rework").reduce((s, x) => s + x[2], 0);
    let tally = `Total time: <b>${fmt(T)}</b> · Rework: <b>${R ? fmt(R) : "none"}</b>`;
    if (o.twice) tally += ` · <b>${o.twice}</b> ${t === "csv" ? "files" : "folders"} edited twice`;
    $("sim-tally").innerHTML = tally;
    $("sim-ctx-n").textContent = o.ctx + "%";
    $("sim-ctx").style.width = o.ctx + "%";
    $("sim-ctx").className = o.ctx >= 60 ? "hot" : "";
    $("sim-verdict").className = "box " + o.c;
    $("sim-verdict").innerHTML = `<span class="chip ${o.c}">${o.v}</span> ${o.note}`;
  }

  window.addEventListener("DOMContentLoaded", draw);
})();
