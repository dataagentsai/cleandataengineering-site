/* Extraction honesty simulator. Fully deterministic: each document behaves the same way every time under
   the same design, so a recording can be repeated. The behaviours are illustrative, chosen to show the
   shape the exam guide describes: a required field with nothing on the page invites an invented value,
   a closed list forces a wrong category, a vague retry repeats the mistake, and no retry can find what
   the page does not contain. */
(function () {
  const TRUTH = { insured: "Harbour Bakery Ltd", carrier: "Northgate Mutual", policy: "NG-448120", line: "General liability", limit: "$1,000,000", deductible: "$2,500", effective: "2026-03-01", expiry: "2027-03-01" };

  const DOCS = {
    std:      { label: "Standard form", kind: "all printed", printed: ["Insured: Harbour Bakery Ltd", "Carrier: Northgate Mutual", "Policy NG-448120 · General liability", "Limit $1,000,000 · Deductible $2,500", "Effective 2026-03-01 · Expires 2027-03-01"] },
    nodeduct: { label: "No deductible printed", kind: "a field is absent", printed: ["Insured: Harbour Bakery Ltd", "Carrier: Northgate Mutual", "Policy NG-448120 · General liability", "Limit $1,000,000 · (no deductible shown)", "Effective 2026-03-01 · Expires 2027-03-01"] },
    cyber:    { label: "New line: cyber", kind: "not in the list", printed: ["Insured: Harbour Bakery Ltd", "Carrier: Northgate Mutual", "Policy NG-448120 · Cyber liability", "Limit $1,000,000 · Deductible $2,500", "Effective 2026-03-01 · Expires 2027-03-01"] },
    schedule: { label: "Carrier's own schedule", kind: "odd layout", printed: ["Long policy schedule, 14 pages", "Limits in a paragraph on page 3", "Dates in a footnote table:", "  “Period: to 2027-03-01 from 2026-03-01”", "Policy NG-448120 · Deductible $2,500"] },
    cutoff:   { label: "Policy number cut off", kind: "scan damage", printed: ["Insured: Harbour Bakery Ltd", "Carrier: Northgate Mutual", "Policy NG-44▒▒▒▒ (scan cut at the edge)", "Limit $1,000,000 · Deductible $2,500", "Effective 2026-03-01 · Expires 2027-03-01"] },
  };

  const GROUPS = {
    out:     { label: "How Claude returns the data", opts: { text: "Ask for JSON in the reply", tool: "Tool with a JSON schema" } },
    missing: { label: "A field that may not be printed", opts: { required: "Required", sentinel: "Sentinel: 0 or “N/A”", nullable: "Optional / nullable" } },
    cat:     { label: "Coverage line", opts: { fixed: "Fixed list of five", other: "List + “other” + detail" } },
    ex:      { label: "Prompt", opts: { none: "Instructions only", few: "+ worked examples of odd layouts" } },
    fail:    { label: "When the validator fails a record", opts: { blind: "Retry: “try again”", specific: "Retry with the specific error", route: "Specific error; nulls go to a person" } },
  };
  const DIAGRAM = { out: "ex-schema", missing: "ex-schema", cat: "ex-schema", ex: "ex-prompt", fail: "ex-validator" };

  /* ---------- the engine: one document through one design ---------- */
  function extract(dk, d) {
    const r = Object.assign({}, TRUTH), flag = {};
    if (dk === "nodeduct") {
      if (d.missing === "required") { r.deductible = "$2,500"; flag.deductible = "invented"; }
      else if (d.missing === "sentinel") { r.deductible = "0"; flag.deductible = "sentinel"; }
      else { r.deductible = null; flag.deductible = "null"; }
    }
    if (dk === "cutoff") {
      if (d.missing === "required") { r.policy = "NG-448129"; flag.policy = "invented"; }
      else if (d.missing === "sentinel") { r.policy = "N/A"; flag.policy = "sentinel"; }
      else { r.policy = null; flag.policy = "null"; }
    }
    if (dk === "cyber") {
      if (d.cat === "fixed") { r.line = "General liability"; flag.line = "wrong"; }
      else { r.line = "other · “Cyber liability”"; flag.line = "otherok"; }
    }
    if (dk === "schedule" && d.ex === "none") { r.effective = TRUTH.expiry; r.expiry = TRUTH.effective; flag.effective = "swapped"; flag.expiry = "swapped"; }
    return { r: r, flag: flag };
  }

  function validate(dk, d, rec, parsed) {
    if (!parsed) return { type: "parse", text: "Reply is not valid JSON (a sentence follows the closing brace)." };
    if (rec.flag.effective === "swapped") return { type: "dates", text: "expiry 2026-03-01 is earlier than effective 2027-03-01." };
    if (rec.r.policy === null) return { type: "policy", text: "policy_number is null; the broker's system needs one." };
    if (rec.r.policy === "N/A") return { type: "policy", text: "policy_number “N/A” does not match the carrier's format." };
    return null;
  }

  function run(dk, d) {
    const steps = [];
    let calls = 1, rec = extract(dk, d), parsed = !(d.out === "text" && dk === "schedule");
    steps.push(["Claude", parsed ? describe(rec) : "Replies with the JSON, then adds “Let me know if you need anything else.”"]);
    let err = validate(dk, d, rec, parsed), retries = 0, end = null, cause = null;
    while (err) {
      steps.push(["Validator", err.text, "rose"]);
      if (d.fail === "route" && err.type === "policy" && rec.r.policy === null) {
        steps.push(["Pipeline", "Null means “not on the page”. No retry: the certificate goes to a person with the scan.", "mint"]);
        end = "person-direct"; break;
      }
      if (retries === 2) { steps.push(["Pipeline", "Two retries used. The certificate goes to a person.", "butter"]); end = "person-late"; cause = err.type; break; }
      retries++; calls++;
      const msg = d.fail === "blind" ? "“Validation failed. Please try again.”" : "“" + err.text + "”";
      steps.push(["Retry " + retries, "Sends the certificate again with " + msg]);
      if (err.type === "parse") { parsed = true; steps.push(["Claude", describe(rec)]); }
      else if (err.type === "dates") {
        if (d.fail === "blind") steps.push(["Claude", "Same reading of the footnote: the dates come back swapped again."]);
        else { rec.r.effective = TRUTH.effective; rec.r.expiry = TRUTH.expiry; delete rec.flag.effective; delete rec.flag.expiry; rec.fixed = true; steps.push(["Claude", "Told which two fields broke which rule, it swaps them back. Both dates are on the page."]); }
      } else if (err.type === "policy") {
        if (d.fail === "blind") steps.push(["Claude", "Nothing new to go on: returns " + (rec.r.policy === null ? "null" : "“N/A”") + " again."]);
        else { rec.r.policy = "NG-448126"; rec.flag.policy = "invented-retry"; steps.push(["Claude", "Told a policy number is needed, it returns NG-448126. The page shows only NG-44 and a smudge."]); }
      }
      err = validate(dk, d, rec, parsed);
    }
    if (!end) { end = "posted"; steps.push(["Pipeline", "Validator passes. The record is posted to the broker's system.", "peri"]); }
    return { steps: steps, rec: rec, calls: calls, retries: retries, end: end, cause: cause, verdict: verdict(dk, d, rec, end, cause, retries, calls) };
  }

  function describe(rec) {
    const odd = Object.keys(rec.flag).filter((k) => rec.flag[k] !== "otherok");
    if (!odd.length) return "Calls the tool with every field filled from the page.";
    return "Returns a record. " + odd.map((k) => `${NAMES[k]}: ${show(rec.r[k])}`).join(", ") + ".";
  }
  const NAMES = { insured: "insured", carrier: "carrier", policy: "policy_number", line: "line_type", limit: "limit", deductible: "deductible", effective: "effective", expiry: "expiry" };
  const show = (v) => (v === null ? "null" : v);

  function verdict(dk, d, rec, end, cause, retries, calls) {
    const f = rec.flag;
    const posted = end === "posted";
    if (posted && (f.policy === "invented-retry")) return ["rose", "Invented value posted", "The page has no full policy number. A retry that insists on one pushed the model to make one up, and it matched the format, so it was posted."];
    if (posted && Object.values(f).includes("invented")) return ["rose", "Invented value posted", `The schema demanded ${dk === "cutoff" ? "a policy number" : "a deductible"} and the page has none, so the model supplied a plausible one. Nothing downstream can tell it from a printed value.`];
    if (posted && f.line === "wrong") return ["rose", "Wrong value posted", "Cyber cover was forced into general liability. A closed list gave the model no honest way to say “something else”."];
    if (posted && f.deductible === "sentinel") return ["rose", "Fake zero posted", "0 reads as “no deductible” to everyone downstream. A sentinel looks like a real value; null says “not printed”."];
    if (end === "person-late" && cause === "dates") return ["butter", "Caught, the slow way", "“Try again” gave the model nothing to correct, so the same swap came back. The dates were on the page; a specific error would have fixed it."];
    if (end === "person-late" && cause === "policy") return ["butter", "Caught, the slow way", d.missing === "sentinel" ? "“N/A” failed the format check, then two retries could not find a number that is not on the page. Wasted calls before a person saw it." : "Two retries could not find a number that is not on the page. Wasted calls before a person saw it."];
    if (end === "person-direct") return ["mint", "Honest: sent to a person", "The model said the number is not printed, and nobody retried. A person checks the scan straight away."];
    if (posted && rec.fixed) return ["mint", "Fixed on retry", "The retry named the two fields and the rule they broke. The dates are on the page, so one retry fixed them." + (d.out === "text" ? " (The first reply also needed a parse retry.)" : "")];
    if (posted && d.out === "text" && dk === "schedule") return ["butter", "Right, one wasted call", "The first reply was not valid JSON. A retry fixed it, but a tool with a JSON schema removes syntax errors altogether."];
    if (posted && f.deductible === "null") return ["mint", "Honest record", "deductible: null, posted as “not printed”. Reviewers can see the gap instead of trusting a made-up number."];
    if (posted && f.line === "otherok") return ["mint", "Honest record", "“other” plus the detail “Cyber liability”: true, and still inside the list the system expects."];
    if (posted && dk === "schedule") return ["mint", "Right first time", "A worked example of a schedule like this showed where the dates sit, so the first pass read them correctly."];
    return ["mint", "Clean", "Everything is printed and plain. Any sensible design gets this one right; the other documents tell designs apart."];
  }

  function design(d) {
    const all = Object.keys(DOCS).map((k) => run(k, d));
    const bad = all.filter((x) => x.verdict[0] === "rose").length;
    const person = all.filter((x) => x.end !== "posted").length;
    const calls = all.reduce((a, x) => a + x.calls, 0);
    return { all: all, bad: bad, person: person, good: 5 - bad - person, calls: calls };
  }

  if (typeof module !== "undefined") { module.exports = { run, design, DOCS, GROUPS }; return; }

  /* ---------- the page ---------- */
  const $ = (id) => document.getElementById(id);
  let dk = "nodeduct", last = "missing";
  const d = { out: "tool", missing: "required", cat: "fixed", ex: "none", fail: "blind" };

  function draw() {
    const box = $("ex-docs");
    box.innerHTML = "";
    Object.entries(DOCS).forEach(([k, v]) => {
      const b = document.createElement("button");
      b.className = "btn" + (k === dk ? " on" : "");
      b.innerHTML = `${v.label} <span class="chip">${v.kind}</span>`;
      b.onclick = () => { dk = k; draw(); };
      box.appendChild(b);
    });
    const g = $("ex-design");
    g.innerHTML = "";
    Object.entries(GROUPS).forEach(([gk, gv]) => {
      const row = document.createElement("div");
      row.className = "grp";
      row.innerHTML = `<div class="gl">${gv.label}</div>`;
      Object.entries(gv.opts).forEach(([ok, ol]) => {
        const b = document.createElement("button");
        b.className = "btn sm" + (d[gk] === ok ? " on" : "");
        b.textContent = ol;
        b.onclick = () => { d[gk] = ok; last = gk; draw(); };
        row.appendChild(b);
      });
      g.appendChild(row);
    });
    ["ex-prompt", "ex-schema", "ex-validator"].forEach((id) => { const el = $(id); if (el) el.setAttribute("stroke-width", id === DIAGRAM[last] ? "4" : "1.5"); });
    render();
  }

  const FLAG = { invented: ["rose", "invented"], "invented-retry": ["rose", "invented"], sentinel: ["rose", "fake value"], wrong: ["rose", "wrong"], swapped: ["rose", "swapped"], null: ["mint", "not printed"], otherok: ["mint", "other + detail"] };

  function render() {
    const R = run(dk, d), D = DOCS[dk];
    $("ex-printed").innerHTML = D.printed.map((l) => `<div>${l}</div>`).join("");
    $("ex-trace").innerHTML = R.steps.map((s) => `<li${s[2] ? ` class="t-${s[2]}"` : ""}><b>${s[0]}:</b> ${s[1]}</li>`).join("");
    if (R.end === "posted") {
      const rows = Object.keys(NAMES).map((k) => {
        const fl = R.rec.flag[k];
        const chip = fl ? `<span class="chip ${FLAG[fl][0]}">${FLAG[fl][1]}</span>` : "";
        return `<tr><td><code>${NAMES[k]}</code></td><td>${show(R.rec.r[k])} ${chip}</td></tr>`;
      }).join("");
      $("ex-record").innerHTML = `<tr><th>Field</th><th>Posted value</th></tr>` + rows;
      $("ex-record-h").textContent = "What got posted";
    } else {
      $("ex-record").innerHTML = `<tr><td>Not posted. It waits in the review queue with ${R.retries ? R.retries + " retr" + (R.retries === 1 ? "y" : "ies") + " spent" : "no retries spent"}.</td></tr>`;
      $("ex-record-h").textContent = "What got posted";
    }
    $("ex-verdict").className = "box " + R.verdict[0];
    $("ex-verdict").innerHTML = `<span class="chip ${R.verdict[0]}">${R.verdict[1]}</span> ${R.verdict[2]}`;
    const A = design(d);
    $("ex-all").innerHTML = Object.keys(DOCS).map((k, i) => `<span class="chip ${A.all[i].verdict[0]}" title="${A.all[i].verdict[2]}">${DOCS[k].label}: ${A.all[i].verdict[1].toLowerCase()}</span>`).join(" ");
    let line = `Across all five: <b>${A.good}</b> posted correctly · <b>${A.bad}</b> posted with an invented or wrong value · <b>${A.person}</b> sent to a person · <b>${A.calls}</b> model calls (5 is the minimum).`;
    if (!A.bad && A.calls === 5) line += ` <span class="chip mint">This is the exam's design</span>`;
    else if (!A.bad) line += ` <span class="chip butter">Honest, but wasteful</span>`;
    $("ex-tally").innerHTML = line;
  }

  window.addEventListener("DOMContentLoaded", draw);
})();
