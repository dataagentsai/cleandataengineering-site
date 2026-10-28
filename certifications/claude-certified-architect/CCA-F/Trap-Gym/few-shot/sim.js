/* Few-shot simulator. Fully deterministic: each input gives the same two runs under the same technique, so a
   recording can be repeated. The behaviours, token counts and call counts are illustrative, chosen to show the
   shape the exam guide describes: instructions alone leave format drift and run-to-run swings on borderline
   cases; 2 to 4 targeted examples that show the reasoning fix format, ambiguous cases, varied layouts and
   invented values; examples of easy cases only teach what was already working. */
(function () {
  /* ---------- the two tasks and their six inputs ---------- */
  // Each input lists the outputs it can produce. g = right, in the house format.
  // f = format drift, v = all fields present but the fix isn't actionable, a = the other call on a borderline
  // case, w = wrong, h = an invented value, r = right after a retry.
  const TASKS = {
    review: {
      label: "Pull-request review", fields: "location · severity · issue · fix",
      inputs: [
        { k: "easy", label: "SQL built from input", src: "BookingRepo.kt:42  db.query(\"… where id = \" + req.id)",
          g: ["BookingRepo.kt:42", "critical", "SQL built from the request's id", "Bind it: db.query(\"… where id = ?\", req.id)"],
          f: ["BookingRepo.kt", "", "Looks like there could be an injection risk in this file.", "Consider sanitising input."] },
        { k: "easy", label: "Missing await", src: "fares.ts:18  const fare = pricing.quote(leg)  // then fare * 1.2",
          g: ["fares.ts:18", "major", "quote() returns a Promise; fare is used as a number", "const fare = await pricing.quote(leg)"],
          f: ["fares.ts, near the quote call", "High", "async issue", "Consider refactoring."],
          v: ["fares.ts:18", "major", "Async handling issue", "Consider refactoring the async flow."] },
        { k: "ambig", label: "Null on a guarded path", src: "CheckoutController.kt:77  user!!.email  (requireLogin() on line 70)",
          g: ["CheckoutController.kt:77", "minor", "user!! can't be null after requireLogin() on line 70, but the guard is far from the use", "val user = requireLogin(), then use user.email"],
          a: ["CheckoutController.kt:77", "critical", "Null dereference: user may be null", "Add a null check."],
          why: "Minor, because requireLogin() means it isn't reachable without a user. Critical is for paths an unauthenticated request can reach." },
        { k: "ambig", label: "Error rethrown on purpose", src: "PartnerClient.kt:31  catch (e: IOException) { throw BookingFailed(\"partner timeout\", e) }",
          g: null,
          a: ["PartnerClient.kt:31", "major", "Exception caught and rethrown", "Handle the error here instead of rethrowing."],
          why: "No finding: the error is wrapped with context and rethrown on purpose. Only errors caught and dropped are flagged." },
        { k: "novel", label: "Flag in a new form", src: "SeatMap.kt:12  @EnabledIf(\"beta.seatmap\") fun renderV2()  (never called directly)",
          g: null,
          w: ["SeatMap.kt:12", "minor", "Dead code: renderV2 is never called", "Delete renderV2."],
          why: "No finding: @EnabledIf switches it on at runtime. No example uses this annotation; the examples' reasoning about flags carries over." },
        { k: "layout", label: "Fix spans 12 lines", src: "Itinerary.ts:140–152  fare totals summed as floating-point dollars (file has 180 lines)",
          g: ["Itinerary.ts:140–152", "major", "Fare totals summed as floating-point dollars", "let cents = 0\nfor (const l of legs) cents += l.fareCents\nreturn cents / 100"],
          f: ["Itinerary.ts", "major", "Rounding problems with totals", "Consider refactoring the totals logic."],
          v: ["Itinerary.ts:140", "major", "Float maths in totals", "Consider refactoring."],
          h: ["Itinerary.ts:212", "major", "Float maths in totals", "Use a decimal type on line 212."], hWhat: "line 212 doesn't exist: the file has 180 lines" },
      ],
    },
    extract: {
      label: "Certificate extraction", fields: "limit · deductible · effective date",
      inputs: [
        { k: "easy", label: "Standard form A", src: "Each occurrence $1,000,000 · Deductible $2,500 · Effective 03/01/2026",
          g: ["$1,000,000", "$2,500", "2026-03-01"] },
        { k: "easy", label: "Standard form B", src: "Each occurrence $2,000,000 · Deductible $5,000 · Effective 07/15/2026",
          g: ["$2,000,000", "$5,000", "2026-07-15"], f: ["2M", "5k", "July 15, 2026"] },
        { k: "layout", label: "Limits in a paragraph", src: "“… a limit of $1,000,000 each occurrence and $2,000,000 in the aggregate …” · Deductible $2,500 · 01/04/2026",
          g: ["$1,000,000", "$2,500", "2026-04-01"], a: ["$2,000,000", "$2,500", "2026-04-01"], aWhat: "took the aggregate, not each occurrence" },
        { k: "layout", label: "Dates in a footnote", src: "Footnote table: “Period: to 2027-01-01 from 2026-01-01” · $1,000,000 · $1,000",
          g: ["$1,000,000", "$1,000", "2026-01-01"], a: ["$1,000,000", "$1,000", "2027-01-01"], aWhat: "read the first date, which is the end" },
        { k: "ambig", label: "Combined limit with a sublimit", src: "“Combined single limit $500,000, of which $100,000 per person” · $500 · 2026-05-01",
          g: ["$500,000", "$500", "2026-05-01"], a: ["$100,000", "$500", "2026-05-01"], aWhat: "took the per-person sublimit as the limit",
          why: "The limit is the combined $500,000; the $100,000 is a sublimit inside it." },
        { k: "novel", label: "New carrier, no deductible", src: "A carrier never seen before; three-column layout; no deductible printed · $1,000,000 · 2026-09-01",
          g: ["$1,000,000", null, "2026-09-01"], h: ["$1,000,000", "$1,000", "2026-09-01"], hWhat: "deductible $1,000 is not on the page",
          why: "null: the deductible is not printed. An example showed a missing value returned as null." },
      ],
    },
  };
  const KIND = { easy: "easy", ambig: "borderline", novel: "new pattern", layout: "varied structure" };

  /* ---------- the knob: technique ---------- */
  // pat: two letters per input (run 1, run 2), in input order.
  const TECH = {
    instr:  { group: "p", label: "Instructions only", where: "fs-instr", tokens: 0,
              pat: { review: ["gg", "gf", "ga", "ag", "gw", "hf"], extract: ["gg", "gf", "ag", "ga", "ag", "hg"] } },
    longer: { group: "p", label: "Longer, more detailed instructions", where: "fs-instr", tokens: 700,
              pat: { review: ["gg", "gg", "ga", "gg", "gw", "gf"], extract: ["gg", "gg", "ga", "gg", "ag", "hg"] } },
    few:    { group: "p", label: "3 targeted examples, with reasoning", where: "fs-ex", tokens: 1800,
              pat: { review: ["gg", "gg", "gg", "gg", "gg", "gg"], extract: ["gg", "gg", "gg", "gg", "gg", "gg"] } },
    easy:   { group: "p", label: "3 examples, easy cases only", where: "fs-ex", tokens: 1200,
              pat: { review: ["gg", "gg", "ag", "aa", "ww", "gf"], extract: ["gg", "gg", "aa", "ga", "ag", "hh"] } },
    many:   { group: "f", label: "20 examples, every case seen", where: "fs-ex", tokens: 12000,
              pat: { review: ["gg", "gg", "gg", "gg", "gg", "gg"], extract: ["gg", "gg", "gg", "gg", "gg", "gg"] } },
    schema: { group: "f", label: "JSON schema through tool use", where: "fs-schema", tokens: 300,
              pat: { review: ["gg", "gv", "ga", "ag", "gw", "hv"], extract: ["gg", "gg", "ag", "ga", "ag", "hg"] } },
    retry:  { group: "f", label: "Validate in code, retry on bad format", where: "fs-val", tokens: 0,
              pat: { review: ["gg", "gr", "ga", "ag", "gw", "hr"], extract: ["gg", "gr", "ag", "ga", "ag", "hg"] } },
  };

  const PROMPT = {
    review: {
      instr: "Review the diff. For each problem, give the location, a severity (critical, major or minor), the issue and a fix.",
      longer: "Review the diff. For each problem, give the location, a severity (critical, major or minor), the issue and a fix.\n+ 14 more rules: “use file:line”, “critical means reachable without login”, “do not flag deliberate rethrows”, “fixes must be code” …",
      few: "The same short instructions, plus 3 worked examples, each with the finding and a line of reasoning:\n1. A null use behind a login guard: minor, and why not critical.\n2. An error caught and dropped (flag) beside one wrapped and rethrown (skip), and why.\n3. A finding whose fix is several lines of replacement code.",
      easy: "The same short instructions, plus 3 examples:\n1. SQL injection: critical.  2. Hard-coded password: critical.  3. Unused variable: minor.\nAll three are cases the bot already got right.",
      many: "The same short instructions, plus 20 examples: one for every kind of finding the team has seen in the last six months.",
      schema: "Instructions only, but findings come back through a tool whose JSON schema requires location, severity (enum), issue and fix.",
      retry: "Instructions only. Code checks each finding for a file:line location, a severity from the list and a fix; if one is missing, it asks again.",
    },
    extract: {
      instr: "Extract the each-occurrence limit, the deductible and the effective date. Use $ amounts and YYYY-MM-DD dates.",
      longer: "Extract the each-occurrence limit, the deductible and the effective date. Use $ amounts and YYYY-MM-DD dates.\n+ 12 more rules: “prefer each occurrence over aggregate”, “periods may be written to/from”, “do not guess” …",
      few: "The same short instructions, plus 3 worked certificates, each with the JSON and a line of reasoning:\n1. A combined single limit with a per-person sublimit: the limit is the combined amount.\n2. Limits inside a paragraph: each occurrence, not aggregate.\n3. No deductible printed: deductible is null.",
      easy: "The same short instructions, plus 3 worked certificates, all on the standard industry form.",
      many: "The same short instructions, plus 20 worked certificates: one from every carrier and layout seen so far.",
      schema: "Instructions only, but the result comes back through a tool whose JSON schema requires limit, deductible and effective date, with formats.",
      retry: "Instructions only. Code checks the $ and date formats; if one is wrong, it asks again.",
    },
  };

  function outputOf(inp, letter) {
    if (letter === "r") return { o: inp.g, c: "r" };
    return { o: letter === "g" ? inp.g : inp[letter], c: letter };
  }

  function rowStatus(p, inp) {
    if (p.indexOf("h") >= 0) return ["rose", "Invented value"];
    if (p === "aa" || p === "ww") return ["rose", "Wrong both runs"];
    if (p.indexOf("a") >= 0 || p.indexOf("w") >= 0) return p[0] === p[1] ? ["rose", "Wrong"] : ["butter", "Runs disagree"];
    if (p.indexOf("f") >= 0) return ["butter", "Format drift"];
    if (p.indexOf("v") >= 0) return ["butter", "Fix not actionable"];
    if (p.indexOf("r") >= 0) return ["butter", "Right after a retry"];
    return ["mint", "Consistent and right"];
  }

  function run(task, tech) {
    const T = TASKS[task], P = TECH[tech].pat[task];
    const rows = T.inputs.map((inp, i) => ({ inp: inp, p: P[i], r1: outputOf(inp, P[i][0]), r2: outputOf(inp, P[i][1]), st: rowStatus(P[i], inp) }));
    const all = P.join("");
    const cnt = (ch) => all.split(ch).length - 1;
    const ambig = rows.filter((r) => r.inp.k === "ambig" || r.inp.k === "novel");
    return {
      rows: rows,
      consistent: rows.filter((r) => r.st[0] === "mint").length,
      formatOk: 12 - cnt("f") - cnt("v"),
      hard: ambig.filter((r) => r.p === "gg").length, hardN: ambig.length,
      invented: cnt("h"),
      retries: cnt("r"),
      calls: 12 + cnt("r"),
      tokens: TECH[tech].tokens,
      verdict: verdict(task, tech),
    };
  }

  function verdict(task, tech) {
    const rv = task === "review";
    return {
      instr: ["rose", "Inconsistent", rv ? "The borderline calls swing between runs, and the new annotation reads as dead code in one. Some findings drop the line number or say only “consider refactoring”, and one points at a line that doesn't exist." : "One standard form comes back as “2M” and “July 15, 2026”. The odd layouts and the sublimit swing between runs, and one run invents a deductible."],
      longer: ["butter", "Only usually works", rv ? "The new rules fixed the rethrow case they spell out. The guarded null still swings, the new annotation still reads as dead code in one run, and the 12-line fix still comes back as advice. Every case you can't foresee needs another rule." : "The new rules fixed the case they name. The sublimit and one layout still swing, and “do not guess” didn't stop an invented deductible."],
      few: ["mint", "Best fit (exam answer)", rv ? "Three examples, each with the reasoning for the call, cover the borderline cases and show a full fix. Every output has the same four parts, both runs agree, and the new annotation is handled by the same reasoning." : "Three worked certificates cover the sublimit, a paragraph layout and a missing value. Both runs agree, the footnote layout no example showed is read right, and the missing deductible comes back null."],
      easy: ["rose", "Misses the point", rv ? "The examples show cases the bot already got right. The rethrow and the new annotation now come out wrong in both runs, and the guarded null still swings: the examples taught nothing about the hard cases." : "Examples of the standard form teach what was already working. The odd layouts still go wrong, and the new carrier gets an invented deductible in both runs."],
      many: ["butter", "Overbuilt", "Every output is right, but the prompt carries about 12,000 extra tokens on every call, and someone has to keep twenty examples current. The guide's pattern is 2 to 4 targeted examples that let Claude generalise."],
      schema: ["butter", "Different problem", rv ? "Every finding now has all four fields, so nothing fails to parse. But a field can be present and empty of meaning (“consider refactoring”), and the borderline calls still swing. A schema fixes structure, not judgement." : "The formats are fixed, but the schema can't say which number is the limit or which date comes first, and a required deductible still gets invented."],
      retry: ["butter", "Delays the problem", "Code catches the missing fields and asks again, at extra calls. It can't tell that a borderline call went the wrong way, or that a value was invented. Examples would have prevented the drift in the first place."],
    }[tech];
  }

  if (typeof module !== "undefined") { module.exports = { run, TASKS, TECH }; return; }

  /* ---------- the page ---------- */
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
  let task = "review", tech = "instr";
  const CELL = { g: "", f: "butter", v: "butter", a: "rose", w: "rose", h: "rose", r: "butter" };
  const NOTE = { f: "format drift", v: "not actionable", a: "other call", w: "wrong", h: "invented", r: "after 1 retry" };

  function btns(id, items, cur, set, filter) {
    const box = $(id);
    box.innerHTML = "";
    Object.entries(items).filter(filter || (() => true)).forEach(([k, v]) => {
      const b = document.createElement("button");
      b.className = "btn sm" + (k === cur ? " on" : "");
      b.textContent = v.label;
      b.onclick = () => { set(k); draw(); };
      box.appendChild(b);
    });
  }

  function draw() {
    btns("fs-task", TASKS, task, (k) => (task = k));
    btns("fs-p", TECH, tech, (k) => (tech = k), ([, v]) => v.group === "p");
    btns("fs-f", TECH, tech, (k) => (tech = k), ([, v]) => v.group === "f");
    ["fs-instr", "fs-ex", "fs-schema", "fs-val"].forEach((id) => { const el = $(id); if (el) el.setAttribute("stroke-width", id === TECH[tech].where ? "4" : "1.5"); });
    render();
  }

  function cell(inp, out) {
    if (!out.o) return `<div class="out ${CELL[out.c]}"><i>No finding</i>${out.c !== "g" && out.c !== "r" ? ` <span class="chip ${CELL[out.c]}">${NOTE[out.c]}</span>` : ""}</div>`;
    const names = task === "review" ? ["location", "severity", "issue", "fix"] : ["limit", "deductible", "effective"];
    const lines = names.map((n, i) => {
      let v = out.o[i];
      const show = v === null ? "null" : v === "" ? "<span class=\"miss\">(missing)</span>" : esc(v).replace(/\n/g, "<br>");
      return `<div><span class="k">${n}</span> ${n === "fix" && v && v.indexOf("\n") >= 0 ? `<code class="blk">${show}</code>` : show}</div>`;
    }).join("");
    let note = "";
    if (out.c !== "g") {
      note = ` <span class="chip ${CELL[out.c]}">${NOTE[out.c]}</span>`;
      if (out.c === "h" && inp.hWhat) note += `<div class="why">${esc(inp.hWhat)}</div>`;
      if (out.c === "a" && inp.aWhat) note += `<div class="why">${esc(inp.aWhat)}</div>`;
    }
    return `<div class="out ${CELL[out.c]}">${lines}${note}</div>`;
  }

  function render() {
    const R = run(task, tech), T = TASKS[task];
    $("fs-prompt").textContent = PROMPT[task][tech];
    $("fs-fields").textContent = T.fields;
    $("fs-rows").innerHTML = R.rows.map((r, i) => `
      <div class="fs-row">
        <div class="fs-in"><b>${i + 1}. ${esc(r.inp.label)}</b> <span class="chip">${KIND[r.inp.k]}</span> <span class="chip ${r.st[0]}">${r.st[1]}</span>
          <div class="src">${esc(r.inp.src)}</div>${r.inp.why && r.p === "gg" ? `<div class="why">${esc(r.inp.why)}</div>` : ""}</div>
        <div class="fs-runs"><div><div class="rl">Run 1</div>${cell(r.inp, r.r1)}</div><div><div class="rl">Run 2</div>${cell(r.inp, r.r2)}</div></div>
      </div>`).join("");
    $("fs-tally").innerHTML = `Consistent and right: <b>${R.consistent} of 6</b> inputs · Outputs in the full, actionable format: <b>${R.formatOk} of 12</b> · Borderline and new cases handled right in both runs: <b>${R.hard} of ${R.hardN}</b> · Invented values: <b>${R.invented}</b><br>
      Extra prompt tokens on every call: <b>${R.tokens.toLocaleString("en-US")}</b> · Model calls: <b>${R.calls}</b>${R.retries ? ` (12, plus ${R.retries} ${R.retries === 1 ? "retry" : "retries"})` : ""}`;
    const v = R.verdict;
    $("fs-verdict").className = "box " + v[0];
    $("fs-verdict").innerHTML = `<span class="chip ${v[0]}">${v[1]}</span> ${v[2]}`;
  }

  window.addEventListener("DOMContentLoaded", draw);
})();
