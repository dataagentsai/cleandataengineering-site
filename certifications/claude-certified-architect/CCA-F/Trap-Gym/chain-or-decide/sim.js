/* Fixed chain or Claude decides? simulator. Deterministic: every job x approach pair plays the same
   fixed steps, so a recording can be repeated. The jobs, files and findings are illustrative, chosen
   to show the shape the exam guide describes (1.6: prompt chaining for known steps, with each file
   analysed on its own and then a cross-file integration pass; adaptive decomposition when the next
   subtask depends on what was just found). */
(function () {
  const JOBS = {
    pr:   { label: "Review a 14-file pull request", kind: "Steps known", tone: "mint",
            story: "The pull request touches 14 files. Hidden in it: four bugs inside single files, and one bug that only shows when you look across files (a function renamed in one file, still called by its old name in another). Every file needs the same checklist." },
    slow: { label: "Find why the nightly job got slower", kind: "Next step depends on findings", tone: "rose",
            story: "The nightly sales job used to take 40 minutes. Since Monday it takes 2 hours. Nobody knows why. The cause is one thing, and it is not in the code." },
    one:  { label: "Review one small config file", kind: "One small item", tone: "butter",
            story: "A 30-line settings file changed. It has one mistake: a timeout set to 5 where 5000 was meant." },
  };
  const WAYS = {
    chain: { label: "Fixed chain: each item alone, then an integration pass", where: "box-chain" },
    adapt: { label: "Claude decides each next step from what it finds", where: "box-adapt" },
    big:   { label: "One big prompt with everything", where: "box-big" },
    tree:  { label: "Hard-coded decision tree", where: "box-tree" },
  };
  // Each step: [kind, text]. kind: run | find | decide | miss | waste.
  // n = steps run, f = found, of = things to find, w = wasted steps, rep = same steps next run.
  const OUT = {
    pr: {
      chain: { n: 15, f: 5, of: 5, w: 0, rep: "Yes, the same 15 steps every time",
        steps: [["find", "Pass on auth.ts alone: token expiry compares seconds with milliseconds"],
                ["find", "Pass on cart.ts alone: the discount loop skips the last item"],
                ["find", "Pass on orders.ts alone: save() is not awaited"],
                ["find", "Pass on emails.ts alone: the customer's name goes into the HTML unescaped"],
                ["run", "Passes on the other 10 files alone: full checklist each, nothing found"],
                ["find", "Integration pass over all 14 file notes: pricing.ts renamed getPrice, but checkout.ts still calls it"]],
        v: "Best fit (exam answer)", c: "mint",
        note: "The steps were known before you started, so a chain fits. Every file gets the same full attention, and one pass looks across them for what no single file shows." },
      adapt: { n: 12, f: 4, of: 5, w: 3, rep: "No, the files it picks can change next run",
        steps: [["decide", "Claude reads the description and chooses where to start: pricing.ts, the biggest change"],
                ["find", "Follows the rename to checkout.ts: finds the stale getPrice call"],
                ["decide", "Chooses auth.ts and cart.ts next, as they look risky"],
                ["find", "auth.ts: token expiry compares seconds with milliseconds"],
                ["find", "cart.ts: the discount loop skips the last item"],
                ["decide", "Chooses orders.ts, because checkout.ts calls it"],
                ["find", "orders.ts: save() is not awaited"],
                ["miss", "Judges emails.ts and 4 other files to be low risk and skips them: the unescaped name is missed"],
                ["waste", "Three planning steps spent choosing an order that was never in doubt"]],
        v: "Overbuilt", c: "butter",
        note: "It found most of the bugs, but a known checklist became a string of judgement calls. That costs more, and it varies from run to run: this time it skipped a file." },
      big: { n: 1, f: 2, of: 5, w: 0, rep: "Yes, but the depth drops for files later in the prompt",
        steps: [["run", "All 14 files and the checklist go into one prompt"],
                ["find", "auth.ts (file 2 in the prompt): token expiry bug found, in detail"],
                ["find", "cart.ts (file 4): discount loop bug found"],
                ["miss", "orders.ts (file 9): skimmed, the missing await is missed"],
                ["miss", "emails.ts (file 11): skimmed, the unescaped name is missed"],
                ["miss", "checkout.ts: called fine in one comment, flagged in another. The feedback contradicts itself"]],
        v: "Breaks", c: "rose",
        note: "Attention dilution: early files get detail, later files get skimmed, and the comments contradict each other. A bigger context window does not fix attention." },
      tree: { n: 14, f: 4, of: 5, w: 0, rep: "Yes, the same branches every time",
        steps: [["run", "Each file goes down the branch for its type: API, screen or config"],
                ["find", "API branch: auth.ts expiry bug, orders.ts missing await"],
                ["find", "Screen branch: cart.ts loop bug, emails.ts unescaped name"],
                ["miss", "No branch looks across files: the stale getPrice call in checkout.ts is missed"]],
        v: "Only half", c: "butter",
        note: "Every file was checked on its own, but nothing looked across them. The chain's last step, the integration pass, is what catches cross-file bugs." },
    },
    slow: {
      chain: { n: 7, f: 0, of: 1, w: 7, rep: "Yes, the same 7 steps every time",
        steps: [["run", "Pass on stage 1 alone (read orders): code unchanged, looks fine"],
                ["run", "Passes on stages 2 to 6 alone: code unchanged, all look fine"],
                ["run", "Integration pass over the 6 stage notes: no code changed, nothing joins up"],
                ["miss", "The cause is in the data. No step on the list was ever going to look at row counts"]],
        v: "Breaks", c: "rose",
        note: "A chain only runs the steps you wrote down. Here nobody could write them down, because each next step had to come from what was just found." },
      adapt: { n: 10, f: 1, of: 1, w: 0, rep: "No, but each step is logged with its reason",
        steps: [["decide", "Starts from the goal and the evidence: 40 minutes became 2 hours. Checks the run history first"],
                ["find", "The slowdown started on Monday night"],
                ["decide", "So it compares Monday's stage timings with last week's"],
                ["find", "The join stage went from 10 to 85 minutes; the other stages are unchanged"],
                ["decide", "So it checks the sizes of the join's inputs"],
                ["find", "The orders input is 3 times bigger than last week; customers is unchanged"],
                ["decide", "So it looks for duplicate orders"],
                ["find", "The same order_id appears up to 3 times since Monday"],
                ["decide", "So it checks what changed upstream on Monday"],
                ["find", "Root cause: another team's loader added a retry that re-inserts rows"]],
        v: "Best fit (exam answer)", c: "mint",
        note: "Each step came from the last finding. No one could have written this list on Monday morning, which is exactly when Claude should choose the steps." },
      big: { n: 1, f: 0, of: 1, w: 0, rep: "Yes, the same one guess",
        steps: [["run", "All the job's code, 7 nights of logs and every config go into one prompt"],
                ["run", "Claude spots that the join is the slowest stage"],
                ["miss", "Suggests more memory and a bigger cluster: that treats the symptom"],
                ["miss", "Row counts were never in the pile, and one prompt cannot go and fetch the next clue"]],
        v: "Breaks", c: "rose",
        note: "A pile of everything is not an investigation. The answer needed a clue that was not in the prompt, and one prompt has no next step." },
      tree: { n: 4, f: 0, of: 1, w: 4, rep: "Yes, the same branches every time",
        steps: [["run", "Out-of-memory errors? No"],
                ["run", "Did any stage's code change in the last deploy? No"],
                ["run", "Did the cluster size change? No"],
                ["miss", "The tree ends at “escalate to on-call”: duplicate input rows were not a branch anyone foresaw"]],
        v: "Too rigid", c: "rose",
        note: "A decision tree is a fixed chain with branches. It handles the causes you foresaw. An open problem needs the next step chosen from the last finding." },
    },
    one: {
      chain: { n: 2, f: 1, of: 1, w: 1, rep: "Yes",
        steps: [["find", "Pass on settings.yaml alone: timeout is 5, should be 5000"],
                ["waste", "Integration pass across one file: nothing to integrate"]],
        v: "More than needed", c: "butter",
        note: "Harmless, but a chain earns its keep when there are many items to keep apart. One file has nothing to keep apart." },
      adapt: { n: 6, f: 1, of: 1, w: 4, rep: "No, the extra files it reads can change",
        steps: [["decide", "Claude plans how to review the file"],
                ["find", "settings.yaml: timeout is 5, should be 5000"],
                ["decide", "Decides to check the three files that read this setting"],
                ["waste", "Reads three more files: nothing found"]],
        v: "Overbuilt", c: "butter",
        note: "There was nothing to discover. Planning and following leads tripled the work for the same single finding." },
      big: { n: 1, f: 1, of: 1, w: 0, rep: "Yes",
        steps: [["find", "One prompt with the file and the checklist: timeout is 5, should be 5000"]],
        v: "Right fit", c: "mint",
        note: "One small file cannot dilute attention. One prompt is the simplest thing that works. Splitting only pays once the prompt gets big." },
      tree: { n: 2, f: 1, of: 1, w: 1, rep: "Yes",
        steps: [["waste", "The tree picks the config branch (someone had to design the tree first)"],
                ["find", "Config branch: timeout is 5, should be 5000"]],
        v: "More than needed", c: "butter",
        note: "It works, but a tree had to be designed and kept up to date for a one-file job." },
    },
  };
  const BOXES = ["box-chain", "box-adapt", "box-big", "box-tree"];
  const KIND = { run: "step run", find: "found", decide: "Claude chooses", miss: "missed", waste: "wasted" };

  const $ = (id) => document.getElementById(id);
  let j = "pr", a = "big", timers = [];

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

  function draw() {
    buttons("sim-j", JOBS, j, (k) => (j = k));
    buttons("sim-a", WAYS, a, (k) => (a = k));
    BOXES.forEach((id) => { const r = $(id); if (r) r.setAttribute("stroke-width", WAYS[a].where === id ? "4" : "1.5"); });
    run();
  }

  function run() {
    timers.forEach(clearTimeout);
    timers = [];
    const o = OUT[j][a];
    $("sim-story").textContent = JOBS[j].story;
    const list = $("sim-steps");
    list.innerHTML = "";
    o.steps.forEach(([k, text], i) => {
      const li = document.createElement("li");
      li.className = "s-" + k;
      li.innerHTML = `<span class="tag k-${k}">${KIND[k]}</span><span class="tx">${text}</span>`;
      list.appendChild(li);
      timers.push(setTimeout(() => li.classList.add("show"), 140 * i));
    });
    const what = j === "slow" ? "Root cause found" : "Bugs found";
    $("sim-tally").innerHTML =
      `Steps run: <b>${o.n}</b> · ${what}: <b>${o.f} of ${o.of}</b> · Wasted steps: <b>${o.w || "none"}</b><br>Same steps next run? <b>${o.rep}</b>`;
    $("sim-found").style.width = (100 * o.f / o.of) + "%";
    $("sim-found").className = o.f === o.of ? "" : "hot";
    $("sim-verdict").className = "box " + o.c;
    $("sim-verdict").innerHTML = `<span class="chip ${o.c}">${o.v}</span> ${o.note}`;
  }

  window.addEventListener("DOMContentLoaded", draw);
})();
