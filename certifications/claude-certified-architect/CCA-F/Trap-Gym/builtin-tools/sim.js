/* Built-in tools simulator. Fully scripted: the same job and tool always play the same trace, so a recording
   can be repeated. Token figures are illustrative, chosen to show the shape the exam guide describes:
   Grep = content, Glob = paths, Edit = one unique match, Read + Write = the fallback, explore incrementally. */
(function () {
  const CONTEXT = 200000;
  const JOBS = {
    tests:   { label: "Find every *.test.ts file", story: "The repo <code>shop-api</code> has about 1,200 TypeScript files. You need a list of every test file, all named <code>*.test.ts</code>, wherever they sit." },
    callers: { label: "Find where calculateTax is called", story: "You are about to change <code>calculateTax</code>. First you need every place that calls it. The callers could be anywhere, and their file names don't mention tax." },
    one:     { label: "Change one line in config", story: "In <code>config/app.yaml</code> (240 lines), change <code>timeout_ms: 3000</code> to <code>5000</code>. That text appears once in the file." },
    three:   { label: "Change a line that appears 3 times", story: "In <code>config/deploy.yaml</code>, the dev, staging and prod blocks each contain <code>replicas: 2</code>. Only <b>staging</b> must change to <code>4</code>. The block name sits far above the line." },
    flow:    { label: "Understand how a request flows", story: "A new engineer asks: what happens when <code>POST /checkout</code> arrives, all the way to the tax calculation? Nobody knows which files are involved." },
  };
  const TOOLS = {
    grep:        { label: "Grep", where: ["bt-grep"] },
    glob:        { label: "Glob", where: ["bt-glob"] },
    read:        { label: "Read", where: ["bt-read"] },
    edit:        { label: "Edit", where: ["bt-edit"] },
    write:       { label: "Write", where: ["bt-write"] },
    readwrite:   { label: "Read + Write", where: ["bt-read", "bt-write"] },
    bash:        { label: "Bash", where: ["bt-bash"] },
    readall:     { label: "Read everything up front", where: ["bt-read"], flowOnly: true },
    incremental: { label: "Grep entry points, then Read along imports", where: ["bt-grep", "bt-read"], flowOnly: true },
  };

  const NOTHING = (what) => ({ steps: [["(no call)", `The job is to ${what}, not to change a file. This tool has nothing to do.`]], tok: 0,
    v: ["Wrong tool", "rose", "Edit, Write and Read + Write change files. Nothing here needs changing."] });

  // steps: [tool call, simulated output]; fall: fallback steps shown after a failure; tok: tokens (illustrative).
  const OUT = {
    tests: {
      glob: { steps: [['Glob(pattern: "**/*.test.ts")', "src/cart/cart.test.ts\nsrc/checkout/order.test.ts\nsrc/tax/tax.test.ts\n… 39 more\n(42 files)"]], tok: 600,
        v: ["Best fit (exam answer)", "mint", "Glob matches file paths. The naming rule is the whole job, so one pattern lists every test file."] },
      grep: { steps: [['Grep(pattern: "describe\\(")', "Found 47 files\nsrc/cart/cart.test.ts\nsrc/test-utils/helpers.ts      (not a test file)\nscripts/describe-schema.ts     (not a test file)\n…\n(38 test files, 9 others; 4 test files that use only test() are missing)"]], tok: 900,
        v: ["Wrong tool", "rose", "Grep searches what is inside files. The job is about names, so it catches helpers and misses tests written differently."] },
      read: { steps: [['Read(file_path: "src/")', "Error: src/ is a directory. Read opens one file whose path you already know."]], tok: 50,
        v: ["Wrong tool", "rose", "Read opens a file you can already name. It can't list files by pattern."] },
      edit: NOTHING("find files"), write: NOTHING("find files"), readwrite: NOTHING("find files"),
      bash: { steps: [["Bash(command: \"find src -name '*.test.ts'\")", "src/cart/cart.test.ts\nsrc/checkout/order.test.ts\n… 40 more\n(42 files)"]], tok: 600,
        v: ["Works, but not the built-in", "butter", "Same list, but through a shell command. The built-in Glob tool is made for finding files by name."] },
    },
    callers: {
      grep: { steps: [['Grep(pattern: "calculateTax\\(", output_mode: "content", -n: true)', "src/checkout/order.ts:88:   const tax = calculateTax(cart, region)\nsrc/checkout/quote.ts:41:   return calculateTax(draft, region)\nsrc/invoices/build.ts:122:  line.tax = calculateTax(items, inv.region)\nsrc/admin/refunds.ts:57:    const back = calculateTax(refund, region)\nsrc/tax/tax.test.ts:12:     expect(calculateTax(…))\n… 2 more\n(7 matches in 5 files)"]], tok: 700,
        v: ["Best fit (exam answer)", "mint", "Grep searches inside files, so it finds every call wherever it lives. Claude then reads only those lines."] },
      glob: { steps: [['Glob(pattern: "**/*tax*")', "src/tax/tax.ts\nsrc/tax/tax.test.ts\nsrc/tax/rates.json\nsrc/admin/tax-report.ts\n(4 files)"]], tok: 200,
        v: ["Wrong tool", "rose", "Glob finds files named after tax. The callers in order.ts, quote.ts, build.ts and refunds.ts are not named that way, so they are missed."] },
      read: { steps: [['Read(file_path: "src/tax/tax.ts")', "export function calculateTax(cart, region) { … }\n(the definition, not the callers)"], ["Read × 1,214 files", "To find callers with Read alone, Claude must open every file in the repo."]], tok: 1400000,
        v: ["Overbuilt", "butter", "It would find the callers in the end, but it reads about 1,200 files to find 5. Grep goes straight to them."] },
      edit: NOTHING("find callers"), write: NOTHING("find callers"), readwrite: NOTHING("find callers"),
      bash: { steps: [["Bash(command: \"grep -rn 'calculateTax(' src\")", "src/checkout/order.ts:88:   const tax = calculateTax(cart, region)\n… 6 more\n(7 matches in 5 files)"]], tok: 700,
        v: ["Works, but not the built-in", "butter", "Same result through the shell. The built-in Grep tool is made for content search; Bash adds nothing here."] },
    },
    one: {
      edit: { steps: [['Edit(file_path: "config/app.yaml",\n     old_string: "timeout_ms: 3000",\n     new_string: "timeout_ms: 5000")', "The file config/app.yaml has been updated.\n(1 line changed)"]], tok: 300,
        v: ["Best fit (exam answer)", "mint", "The text appears once, so Edit's match is unique. One small, reviewable change."] },
      readwrite: { steps: [['Read(file_path: "config/app.yaml")', "240 lines read"], ['Write(file_path: "config/app.yaml", content: <all 240 lines>)', "File written. 240 lines replaced; the diff shows quoting and spacing changes on 11 other lines."]], tok: 6000,
        v: ["Overbuilt", "butter", "It works, but it rewrites the whole file for one value. The review is harder and formatting can drift. Edit was enough."] },
      write: { steps: [['Write(file_path: "config/app.yaml",\n      content: "timeout_ms: 5000\\n")', "File written (1 line).\nThe other 239 lines are gone."]], tok: 100,
        v: ["Breaks", "rose", "Write replaces the whole file with what it is given. Without reading first, everything else in the file is lost."] },
      read: { steps: [['Read(file_path: "config/app.yaml")', "240 lines read. Line 57: timeout_ms: 3000"]], tok: 3000,
        v: ["Half the job", "butter", "Read only looks. The value is found but not changed."] },
      grep: { steps: [['Grep(pattern: "timeout_ms", -n: true)', "config/app.yaml:57: timeout_ms: 3000"]], tok: 100,
        v: ["Half the job", "butter", "Grep finds the line. It changes nothing."] },
      glob: { steps: [['Glob(pattern: "config/*.yaml")', "config/app.yaml\nconfig/deploy.yaml"]], tok: 50,
        v: ["Wrong tool", "rose", "Glob finds the file's path. The job is a change inside it."] },
      bash: { steps: [["Bash(command: \"sed -i 's/timeout_ms: 3000/timeout_ms: 5000/'\n                 config/app.yaml\")", "(no output; exit code 0)"]], tok: 100,
        v: ["Works, but not the built-in", "butter", "It works here, but it leaves the file tools. Edit makes the same change and shows exactly what it matched."] },
    },
    three: {
      edit: { steps: [['Edit(file_path: "config/deploy.yaml",\n     old_string: "replicas: 2",\n     new_string: "replicas: 4")', "Error: Found 3 matches of the string to replace.\nThe old text must be unique. Provide more context to\nidentify one instance."]],
        fall: [['Read(file_path: "config/deploy.yaml")', "180 lines read\nline 12  (dev):     replicas: 2\nline 74  (staging): replicas: 2\nline 136 (prod):    replicas: 2"], ['Write(file_path: "config/deploy.yaml", content: <file with line 74 changed>)', "File written. Only line 74 differs: replicas: 4"]],
        tok: 4900, v: ["Fails: not unique", "rose", "Edit needs a unique text match, and this one appears 3 times. The guide's next move is shown under it: Read the whole file, then Write it back."] },
      readwrite: { steps: [['Read(file_path: "config/deploy.yaml")', "180 lines read\nline 12  (dev):     replicas: 2\nline 74  (staging): replicas: 2\nline 136 (prod):    replicas: 2"], ['Write(file_path: "config/deploy.yaml", content: <file with line 74 changed>)', "File written. Only line 74 differs: replicas: 4"]], tok: 4600,
        v: ["Best fit (exam answer)", "mint", "When Edit can't find a unique match, Read gives Claude the whole file, so it can use the block's position. Write puts it back with one line changed."] },
      write: { steps: [['Write(file_path: "config/deploy.yaml",\n      content: "replicas: 4\\n")', "File written (1 line).\nThe dev and prod blocks, and the rest of staging, are gone."]], tok: 100,
        v: ["Breaks", "rose", "Write without Read replaces the whole file with a guess. Read first, then Write."] },
      read: { steps: [['Read(file_path: "config/deploy.yaml")', "180 lines read. Staging's replicas is line 74."]], tok: 2300,
        v: ["Half the job", "butter", "Read is the right first step of the fallback, but on its own it changes nothing. Add the Write."] },
      grep: { steps: [['Grep(pattern: "replicas: 2", -n: true)', "config/deploy.yaml:12:  replicas: 2\nconfig/deploy.yaml:74:  replicas: 2\nconfig/deploy.yaml:136: replicas: 2"]], tok: 150,
        v: ["Half the job", "butter", "Grep shows the three matches. It changes nothing."] },
      glob: { steps: [['Glob(pattern: "config/deploy.yaml")', "config/deploy.yaml"]], tok: 50,
        v: ["Wrong tool", "rose", "Glob finds the path. The problem is inside the file."] },
      bash: { steps: [["Bash(command: \"sed -i 's/replicas: 2/replicas: 4/'\n                 config/deploy.yaml\")", "(no output; exit code 0)\ndev, staging and prod now all say replicas: 4"]], tok: 100,
        v: ["Breaks", "rose", "sed replaces every match, so dev and prod change too. A line-number version works but is fragile; the guide's route is Read + Write."] },
    },
    flow: {
      incremental: { steps: [
        ["Grep(pattern: \"'/checkout'\", -n: true)", "src/routes/checkout.ts:14: router.post('/checkout', checkoutHandler)"],
        ['Read(file_path: "src/routes/checkout.ts")', "import { placeOrder } from '../checkout/order'\ncheckoutHandler validates the cart, then calls placeOrder()"],
        ['Read(file_path: "src/checkout/order.ts")', "import { calculateTax } from '../tax/tax'\nplaceOrder() reserves stock, then calls calculateTax(cart, region)"],
        ['Read(file_path: "src/tax/tax.ts")', "calculateTax() looks up the region's rate in rates.json"]], tok: 9000,
        v: ["Best fit (exam answer)", "mint", "Grep finds the entry point; Read follows each import as the trail reaches it. Four files, the whole path in view, and the context stays light."] },
      readall: { steps: [['Glob(pattern: "src/**/*.ts")', "1,214 files"], ["Read × 1,214 files", "About 1,400,000 tokens. The context is full long before the end; the first files are summarised or pushed out."]], tok: 1400000,
        v: ["Overbuilt", "rose", "Reading everything floods the context with files that have nothing to do with checkout. Build understanding incrementally instead."] },
      grep: { steps: [["Grep(pattern: \"'/checkout'\", -n: true)", "src/routes/checkout.ts:14: router.post('/checkout', checkoutHandler)"]], tok: 200,
        v: ["Half the job", "butter", "The right first step: the entry point is found. Now Read along the imports to follow the flow."] },
      glob: { steps: [['Glob(pattern: "src/routes/**")', "src/routes/cart.ts\nsrc/routes/checkout.ts\n… 21 more\n(23 files)"]], tok: 400,
        v: ["Half the job", "butter", "File names give a guess at where to start, not the flow. Grep for the route, then Read along."] },
      read: { steps: [['Read(file_path: "src/index.ts")', "app setup: mounts 23 routers"], ["Read × 30 files, chosen by name", "Some are on the checkout path, many are not."]], tok: 60000,
        v: ["Only usually works", "butter", "Without a search, Claude guesses where to start and reads a lot on the way. Grep the entry point first."] },
      edit: NOTHING("understand the code"), write: NOTHING("understand the code"), readwrite: NOTHING("understand the code"),
      bash: { steps: [["Bash(command: \"cat $(find src -name '*.ts')\")", "1,214 files printed. About 1,400,000 tokens of output."]], tok: 1400000,
        v: ["Overbuilt", "rose", "The same read-everything plan through the shell. It floods the context the same way."] },
    },
  };

  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
  let j = "callers", t = "grep", timer = null;

  function buttons(boxId, items, current, set) {
    const box = $(boxId);
    box.innerHTML = "";
    Object.entries(items).forEach(([k, v]) => {
      if (v.flowOnly && j !== "flow") return;
      const x = document.createElement("button");
      x.className = "btn" + (k === current ? " on" : "");
      x.textContent = v.label;
      x.onclick = () => { set(k); draw(); };
      box.appendChild(x);
    });
  }

  function highlight() {
    ["bt-glob", "bt-grep", "bt-read", "bt-edit", "bt-write", "bt-bash"].forEach((id) => {
      const e = $(id);
      if (e) e.setAttribute("stroke-width", TOOLS[t].where.includes(id) ? "4" : "1.5");
    });
  }

  function draw() {
    if (TOOLS[t].flowOnly && j !== "flow") t = "grep";
    buttons("sim-j", JOBS, j, (k) => (j = k));
    buttons("sim-t", TOOLS, t, (k) => (t = k));
    $("sim-story").innerHTML = JOBS[j].story;
    highlight();
    run();
  }

  function stepHtml(call, out, n) {
    return `<div class="step"><b>${n}. Call</b><pre>${esc(call)}</pre><b>Output</b><pre>${esc(out)}</pre></div>`;
  }

  function run() {
    clearTimeout(timer);
    const o = OUT[j][t];
    let h = o.steps.map(([c, x], i) => stepHtml(c, x, i + 1)).join("");
    if (o.fall) h += `<p class="fallnote"><b>Next move: the Read + Write fallback</b></p>` + o.fall.map(([c, x], i) => stepHtml(c, x, o.steps.length + i + 1)).join("");
    const trail = $("sim-trail");
    trail.innerHTML = h;
    const els = [...trail.querySelectorAll(".step, .fallnote")];
    let i = 0;
    (function step() { if (i < els.length) { els[i++].classList.add("in"); timer = setTimeout(step, 220); } })();

    const pct = Math.min(100, (o.tok / CONTEXT) * 100);
    const over = o.tok > CONTEXT;
    $("sim-tok-n").textContent = o.tok === 0 ? "none" :
      `about ${o.tok.toLocaleString("en-US")} tokens` + (over ? ": far more than a 200,000-token context holds" : ` of a 200,000-token context`);
    const bar = $("sim-tok");
    bar.style.width = (o.tok && pct < 1 ? 1 : pct) + "%";
    bar.className = over ? "hot" : "";
    $("sim-verdict").className = "box " + o.v[1];
    $("sim-verdict").innerHTML = `<span class="chip ${o.v[1]}">${o.v[0]}</span> ${esc(o.v[2])}`;
  }

  window.BuiltinSim = { OUT, JOBS, TOOLS, set: (jj, tt) => { j = jj; t = tt; draw(); } };
  window.addEventListener("DOMContentLoaded", draw);
})();
