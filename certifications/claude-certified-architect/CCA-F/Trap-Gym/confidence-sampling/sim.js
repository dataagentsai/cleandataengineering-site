/* Confidence and sampling simulator. Deterministic: the samples are drawn with a fixed seed, so the
   same choice always shows the same grid and a recording can be repeated. The accuracies, volumes and
   catch rates are illustrative, chosen to show the shape the exam guide describes (5.5): a 97% average
   can hide a weak document type or field; stratified random sampling and field-level confidence
   calibrated on a labelled set find it and route review. */
(function () {
  const TYPES = [
    { k: "inv", label: "Invoices", vol: 5800 },
    { k: "rec", label: "Receipts", vol: 2500 },
    { k: "scan", label: "Scanned PDFs", vol: 1500 },
    { k: "hand", label: "Handwritten", vol: 200 },
  ];
  const FIELDS = ["Supplier", "Date", "Amount", "Ref."];
  // True accuracy (%) per type x field. Nobody sees this unless they measure it.
  const TRUE = {
    inv: [99.0, 98.8, 98.4, 98.2],
    rec: [98.4, 98.0, 97.6, 97.2],
    scan: [96.5, 95.5, 94.5, 93.5],
    hand: [86, 78, 64, 56],
  };
  const BAR = 97;     // a field may post without review only if measured at or above this
  const MIN_N = 30;   // fewer documents than this in a sample is too few to judge
  const SAMPLE = 400; // the labelling budget: 400 documents, whichever way they are picked

  const METHODS = {
    overall: { label: "Overall accuracy only", where: ["box-overall"] },
    random:  { label: "A plain random sample", where: ["box-random"] },
    self:    { label: "Claude rates its own confidence", where: ["box-self"] },
    strat:   { label: "Stratified sample by document type", where: ["box-strat"] },
    calib:   { label: "Stratified sample + calibrated field confidence", where: ["box-strat", "box-calib"] },
  };
  const VERDICT = {
    overall: ["Masks weak spots", "rose", "One number, about 97%, looks ready. It blends handwritten forms, wrong in nearly one field in three, into thousands of good documents."],
    random:  ["Too thin", "rose", "The sample was fair, but handwritten forms are 2% of documents, so it held just four, and by luck they looked fine. Four documents are too few to judge, so the 97% average decided for them. Scanned PDFs were common enough to catch, mostly."],
    self:    ["Uncalibrated", "rose", "Claude's own rating catches some errors, but nobody checked it against labelled data. Confident misreadings of handwriting went straight through."],
    strat:   ["Half the answer", "butter", "Sampling each type found the weak spots, and those fields stay with people. But every error in the fields that passed the bar still posts unseen."],
    calib:   ["Best fit (exam answer)", "mint", "Measured by type and field, then each field routed by a confidence score calibrated on labelled data. Weak fields go to people; the stratified sample keeps checking the confident ones."],
  };

  // Seeded random numbers (mulberry32), so every run draws the same documents.
  function rng(seed) {
    return function () {
      seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  const total = TYPES.reduce((s, t) => s + t.vol, 0);

  // Label n documents of one type: returns the count correct for each field.
  function label(r, type, n) {
    const ok = [0, 0, 0, 0];
    for (let d = 0; d < n; d++) FIELDS.forEach((_, f) => { if (r() * 100 < TRUE[type][f]) ok[f]++; });
    return ok;
  }
  // A plain random sample: pick each document's type by its share of volume.
  function randomSample() {
    const r = rng(826), n = {}, ok = {};
    TYPES.forEach((t) => { n[t.k] = 0; });
    for (let d = 0; d < SAMPLE; d++) {
      let x = r() * total;
      const t = TYPES.find((t) => (x -= t.vol) < 0) || TYPES[TYPES.length - 1];
      n[t.k]++;
    }
    TYPES.forEach((t) => (ok[t.k] = label(r, t.k, n[t.k])));
    return { n, ok };
  }
  // A stratified random sample: the same 400 documents, split evenly across the four types.
  function stratSample() {
    const r = rng(21), n = {}, ok = {};
    TYPES.forEach((t) => { n[t.k] = SAMPLE / TYPES.length; ok[t.k] = label(r, t.k, n[t.k]); });
    return { n, ok };
  }
  const RS = randomSample(), SS = stratSample();

  // Illustrative routing behaviour per field.
  // Self-rated confidence: flags 2% of fields plus some errors; handwriting misreads are often confident.
  const SELF_CATCH = { inv: 0.55, rec: 0.55, scan: 0.45, hand: 0.2 };
  // Calibrated: the threshold is set on a labelled set so a field below it goes to review.
  // Weak fields send most values to people; strong fields send few. 92% of errors are caught.
  const calibShare = (err) => Math.min(1, 0.01 + err * 2.5);
  const CAL_CATCH = 0.92;

  function outcome(m) {
    // For each type x field: what the team sees, and what happens to the values each month.
    const cells = {}, sample = m === "random" ? RS : m === "strat" || m === "calib" ? SS : null;
    let bad = 0, reviewed = 0, posted = 0;
    TYPES.forEach((t) => {
      cells[t.k] = FIELDS.map((_, f) => {
        const vol = t.vol, err = (100 - TRUE[t.k][f]) / 100, errors = vol * err;
        const c = { seen: null, n: 0, route: "auto" };
        if (sample) { c.n = sample.n[t.k]; c.seen = c.n ? (100 * sample.ok[t.k][f]) / c.n : null; }
        let caught = 0, rev = 0;
        if (m === "overall") { /* nothing per field: everything posts */ }
        else if (m === "random" || m === "strat") {
          const judged = c.n >= MIN_N;
          if (judged && c.seen < BAR) { c.route = "people"; rev = vol; caught = errors; }
          else if (!judged) c.route = "unjudged";
        } else if (m === "self") {
          c.route = "flagged"; caught = errors * SELF_CATCH[t.k]; rev = vol * 0.02 + caught;
        } else {
          if (c.seen < BAR) c.route = "routed"; else c.route = "routed-light";
          rev = vol * calibShare(err); caught = errors * CAL_CATCH;
        }
        c.share = rev / vol;
        bad += errors - caught; reviewed += rev; posted += vol - rev;
        c.passed = errors - caught;
        return c;
      });
    });
    let overallSeen = null;
    if (m === "overall") {
      let ok = 0;
      TYPES.forEach((t) => (ok += t.vol * TRUE[t.k].reduce((a, b) => a + b, 0) / 4));
      overallSeen = ok / total;
    }
    return { cells, bad, reviewed, posted, overallSeen };
  }

  const $ = (id) => document.getElementById(id);
  const n0 = (x) => Math.round(x).toLocaleString("en-GB");
  const pct = (x) => String(Math.round(x * 10) / 10) + "%";
  const tone = (v) => (v >= 98 ? "g" : v >= BAR ? "y" : "r");
  let m = "overall", showTruth = false;

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

  function highlight() {
    ["box-overall", "box-random", "box-self", "box-strat", "box-calib"].forEach((id) => {
      const r = $(id);
      if (r) r.setAttribute("stroke-width", METHODS[m].where.includes(id) ? "4" : "1.5");
    });
  }

  const ROUTE = {
    auto: "posts", unjudged: "posts anyway", people: "people check", flagged: "posts unless flagged",
    routed: "mostly people", "routed-light": "mostly posts",
  };

  function seenGrid(o) {
    if (m === "overall") {
      return `<p class="lbl">What your check shows</p><div class="one">Overall field accuracy: <b>${pct(o.overallSeen)}</b><br><span>Across every document, reported as one number. It looks ready to automate.</span></div>`;
    }
    if (m === "self") {
      return `<p class="lbl">What your check shows</p><div class="one">No accuracy measured per type or field.<br><span>Each field posts unless Claude rates itself unsure. Nobody compared those ratings with labelled answers.</span></div>`;
    }
    let h = `<p class="lbl">What your check shows (measured accuracy, then what happens to that field)</p><div class="tablewrap"><table class="g"><tr><th>Type <span>(sampled)</span></th>${FIELDS.map((f) => `<th>${f}</th>`).join("")}</tr>`;
    TYPES.forEach((t) => {
      const cs = o.cells[t.k];
      h += `<tr><td>${t.label} <span>(${cs[0].n})</span></td>` + cs.map((c) => {
        if (c.n < MIN_N) return `<td class="few">${c.n ? pct(c.seen) : "none"}<small>too few</small><small>${ROUTE[c.route]}</small></td>`;
        return `<td class="${tone(c.seen)}">${pct(c.seen)}<small>${ROUTE[c.route]}${m === "calib" ? `, ${Math.round(c.share * 100)}% checked` : ""}</small></td>`;
      }).join("") + "</tr>";
    });
    return h + "</table></div>";
  }

  function truthGrid(o) {
    let h = `<p class="lbl">What is really true (accuracy, and wrong values posted unseen each month)</p><div class="tablewrap"><table class="g"><tr><th>Type <span>(a month)</span></th>${FIELDS.map((f) => `<th>${f}</th>`).join("")}</tr>`;
    TYPES.forEach((t) => {
      h += `<tr><td>${t.label} <span>(${n0(t.vol)})</span></td>` + o.cells[t.k].map((c, f) =>
        `<td class="${tone(TRUE[t.k][f])}">${pct(TRUE[t.k][f])}<small>${n0(c.passed)} wrong posted</small></td>`).join("") + "</tr>";
    });
    return h + "</table></div>";
  }

  function draw() {
    buttons("sim-m", METHODS, m, (k) => (m = k));
    highlight();
    const o = outcome(m);
    $("sim-seen").innerHTML = seenGrid(o);
    $("sim-truth").innerHTML = showTruth ? truthGrid(o) : "";
    $("sim-show").textContent = showTruth ? "Hide what is really true" : "Show what is really true";
    const fields = total * 4, maxBad = outcome("overall").bad;
    $("sim-bad").style.width = (100 * o.bad / maxBad) + "%";
    $("sim-rev").style.width = (100 * o.reviewed / fields) + "%";
    $("sim-tally").innerHTML =
      `Wrong values posted without review: <b>${n0(o.bad)}</b> a month · ` +
      `Fields checked by people: <b>${n0(o.reviewed)}</b> of ${n0(fields)} (${Math.round(100 * o.reviewed / fields)}%) · ` +
      `Error rate among posted fields: <b>${pct(100 * o.bad / Math.max(1, o.posted))}</b>`;
    const v = VERDICT[m];
    $("sim-verdict").className = "box " + v[1];
    $("sim-verdict").innerHTML = `<span class="chip ${v[1]}">${v[0]}</span> ${v[2]}`;
  }

  window.addEventListener("DOMContentLoaded", () => {
    $("sim-show").onclick = () => { showTruth = !showTruth; draw(); };
    draw();
  });
  window.SIM_DEBUG = { outcome, RS, SS };
})();
