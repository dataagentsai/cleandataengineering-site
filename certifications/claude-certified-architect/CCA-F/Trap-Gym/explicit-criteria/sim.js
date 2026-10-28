/* Explicit criteria simulator. Fully deterministic: the same 40 code spots, and each instruction always flags
   the same ones, so a recording can be repeated. The behaviours and the trust figures are illustrative, chosen
   to show the shape the exam guide describes: vague, cautious or confidence wording leaves the same kind of
   noise; categorical criteria remove it; severity needs concrete examples; noise in one category costs trust
   in all of them. */
(function () {
  /* ---------- the 40 spots the review bot reads ---------- */
  // t: "real" (worth a finding) or "fine" (should be left alone). sev: the right level for a real one.
  // by: option codes that flag a "fine" doc comment. msg: what the bot posts when it flags it.
  const ITEMS = [
    // Doc comments: 6 real contradictions
    { id: "d1", cat: "doc", t: "real", sev: "major", code: "// Returns null when the booking is not found\nfun find(id: String): Booking =\n    repo.get(id) ?: throw NotFoundException(id)", msg: "The comment says null; the code throws NotFoundException. Callers that check for null will crash.", why: "A real contradiction: what the comment claims is not what the code does." },
    { id: "d2", cat: "doc", t: "real", sev: "critical", code: "// amount is in cents\ncharge(card, amount = booking.totalDollars)", msg: "The comment says cents; the code passes dollars. Anyone following the comment charges 100 times too much or too little.", why: "A real contradiction, and it touches money." },
    { id: "d3", cat: "doc", t: "real", sev: "major", subtle: true, code: "// Thread-safe: call from any worker\nfun add(s: Seat) { cache[s.id] = s }  // plain HashMap", msg: "The comment promises thread safety; the code writes to a plain HashMap with no lock.", why: "A real contradiction, but a subtle one: you have to know HashMap isn't safe across threads." },
    { id: "d4", cat: "doc", t: "real", sev: "minor", code: "// Retries 3 times before failing\nretry(times = 5) { partner.confirm(id) }", msg: "The comment says 3 retries; the code makes 5.", why: "A real contradiction, but small: no caller depends on the number." },
    { id: "d5", cat: "doc", t: "real", sev: "major", code: "// Sorted by departure, earliest first\nreturn legs.sortedByDescending { it.departs }", msg: "The comment says earliest first; the code sorts latest first.", why: "A real contradiction that would mislead the next person who uses the list." },
    { id: "d6", cat: "doc", t: "real", sev: "major", code: "// Validates the email format\nfun save(email: String) = repo.insert(email)", msg: "The comment says the email is validated; the code inserts it unchecked.", why: "A real contradiction: callers will skip their own check." },
    // Doc comments: 18 that are fine under the team's rule
    { id: "f1", cat: "doc", t: "fine", kind: "typo", by: "VCHXS", code: "// Recieve the confirmation from the partner API\nval conf = partner.confirm(id)", msg: "Typo in comment: “Recieve”.", why: "A spelling slip. The comment is still true." },
    { id: "f2", cat: "doc", t: "fine", kind: "typo", by: "VCHXS", code: "// calcualte the tax for each leg\nlegs.map { taxFor(it) }", msg: "Typo in comment: “calcualte”.", why: "A spelling slip. The comment is still true." },
    { id: "f3", cat: "doc", t: "fine", kind: "typo", by: "VCHXS", code: "// teh seat map is cached for 5 min\n@Cacheable(ttl = \"5m\")", msg: "Typo in comment: “teh”.", why: "A spelling slip, and the 5 minutes is correct." },
    { id: "f4", cat: "doc", t: "fine", kind: "missing doc", by: "VCHXS", code: "fun refund(b: Booking): Receipt {", msg: "Public function refund has no KDoc.", why: "No comment at all, so nothing can contradict the code. The team has no rule that every function needs one." },
    { id: "f5", cat: "doc", t: "fine", kind: "missing doc", by: "VCHS", code: "export function toIata(city: string) {", msg: "Exported function toIata has no JSDoc.", why: "No comment, so nothing to contradict." },
    { id: "f6", cat: "doc", t: "fine", kind: "missing doc", by: "VH", code: "private fun mergeLegs(a: Leg, b: Leg): Leg {", msg: "mergeLegs is undocumented.", why: "A private helper with a clear name. Nothing to contradict." },
    { id: "f7", cat: "doc", t: "fine", kind: "vague wording", by: "VCHXS", code: "// does the thing for the fare\nval fare = applyMarkup(base)", msg: "Comment is vague and doesn't explain the markup.", why: "Unhelpful, but not false." },
    { id: "f8", cat: "doc", t: "fine", kind: "vague wording", by: "VCXS", code: "// handle edge cases\nif (legs.isEmpty()) return Itinerary.EMPTY", msg: "Comment should name the edge cases it handles.", why: "Could be clearer, but it isn't wrong." },
    { id: "f9", cat: "doc", t: "fine", kind: "vague wording", by: "V", code: "// see below\nval tz = airport.zone", msg: "“see below” doesn't say what to look at.", why: "A lazy comment, not a false one." },
    { id: "f10", cat: "doc", t: "fine", kind: "vague wording", by: "V", code: "// magic number, ask Priya\nval bufferMinutes = 45", msg: "Comment should explain the 45 instead of naming a person.", why: "True as written. A style point, not a contradiction." },
    { id: "f11", cat: "doc", t: "fine", kind: "old-looking but true", by: "VCHXS", code: "// Added for JIRA-1234 (2019)\nfun legacyFareCode(f: Fare) =", msg: "Comment refers to a 2019 ticket and may be out of date.", why: "Old, but still true: the function was added for that ticket." },
    { id: "f12", cat: "doc", t: "fine", kind: "old-looking but true", by: "VCHXS", code: "// Workaround until the partner v2 API ships\nval id = raw.removePrefix(\"P-\")", msg: "Comment mentions the v2 API; check whether it has shipped.", why: "v2 hasn't shipped, so the comment is still accurate." },
    { id: "f13", cat: "doc", t: "fine", kind: "old-looking but true", by: "VC", code: "// Old pricing path, kept for legacy partners\nif (partner.legacy) return oldPrice(f)", msg: "“Old pricing path” may be stale.", why: "Legacy partners still use it. The comment is true." },
    { id: "f14", cat: "doc", t: "fine", kind: "explains why", by: "", code: "// Round down: partners round down too\nval total = floor(sum)", msg: "", why: "A good comment: it explains a decision, and the code matches it." },
    { id: "f15", cat: "doc", t: "fine", kind: "explains why", by: "", code: "// Deliberately not cached: prices change by the minute\nfun livePrice(f: Flight) = api.price(f)", msg: "", why: "A good comment, and the code matches it." },
    { id: "f16", cat: "doc", t: "fine", kind: "TODO", by: "VCH", code: "// TODO: move the 45 to config\nval bufferMinutes = 45", msg: "Unresolved TODO left in the code.", why: "A TODO is a note to the team, not a false claim about the code." },
    { id: "f17", cat: "doc", t: "fine", kind: "TODO", by: "", code: "// FIXME: slow for more than 500 legs\nlegs.forEach { relink(it, legs) }", msg: "", why: "True, and the team already knows." },
    { id: "f18", cat: "doc", t: "fine", kind: "borderline", by: "VCHXSEK", code: "// Returns the traveller\nfun find(id: String): Traveller?", msg: "The comment doesn't mention that find can return null.", why: "Incomplete rather than contradicted: the comment doesn't claim it never returns null. A borderline case every option flags." },
    // Security: rules already explicit, so the same every time
    { id: "s1", cat: "sec", t: "real", sev: "critical", code: "db.query(\"select * from booking where id = \" + req.id)", msg: "SQL built from request input: injection.", why: "A real security finding." },
    { id: "s2", cat: "sec", t: "real", sev: "critical", code: "@PostMapping(\"/admin/refund\")  // no @PreAuthorize\nfun refundAll()", msg: "Admin endpoint has no authorisation check.", why: "A real security finding." },
    { id: "s3", cat: "sec", t: "real", sev: "major", code: "log.info(\"card=${card.number}\")", msg: "Full card number written to the log.", why: "A real security finding." },
    { id: "s4", cat: "sec", t: "real", sev: "major", code: "res.redirect(req.query.next)", msg: "Open redirect: next is taken from the query string unchecked.", why: "A real security finding." },
    { id: "s5", cat: "sec", t: "fine", code: "db.query(\"select * from booking where id = ?\", req.id)", why: "A bound parameter. Correctly left alone." },
    { id: "s6", cat: "sec", t: "fine", code: "val hash = bcrypt.hash(password, cost = 12)", why: "Correctly left alone." },
    { id: "s7", cat: "sec", t: "fine", code: "@PreAuthorize(\"hasRole('ADMIN')\")\nfun purgeCache()", why: "Correctly left alone." },
    { id: "s8", cat: "sec", t: "fine", code: "log.info(\"card=****${card.last4}\")", why: "Masked. Correctly left alone." },
    // Performance: rules already explicit, one known false positive
    { id: "p1", cat: "perf", t: "real", sev: "major", code: "for (b in bookings) { repo.loadTraveller(b.travellerId) }", msg: "A database query inside a loop: one query per booking.", why: "A real performance finding." },
    { id: "p2", cat: "perf", t: "real", sev: "major", code: "val n = repo.findAll().size", msg: "Loads every row to count them; use a count query.", why: "A real performance finding." },
    { id: "p3", cat: "perf", t: "real", sev: "minor", code: "routes.forEach { r -> Regex(r.pattern).matches(path) }", msg: "Compiles a regex on every request; compile once.", why: "A real performance finding." },
    { id: "p4", cat: "perf", t: "fine", by: "VCHXSEKD", code: "listOf(adult, child, infant).sortedBy { it.age }", msg: "Sorting inside a request handler may be slow.", why: "Three items. A false positive the performance rule lets through on every option." },
    { id: "p5", cat: "perf", t: "fine", code: "val n = repo.countByStatus(OPEN)", why: "Correctly left alone." },
    { id: "p6", cat: "perf", t: "fine", code: "val byId = legs.associateBy { it.id }", why: "Correctly left alone." },
    { id: "p7", cat: "perf", t: "fine", code: "private val ROUTE = Regex(\"^/b/(\\\\w+)$\")", why: "Correctly left alone." },
    { id: "p8", cat: "perf", t: "fine", code: "repo.loadTravellers(bookings.map { it.travellerId })", why: "One batched query. Correctly left alone." },
  ];
  const CATS = { doc: "Doc comments", sec: "Security", perf: "Performance" };

  /* ---------- the knob: how the doc-comment category is written ---------- */
  const OPTS = {
    V: { group: "w", label: "“Check that comments are accurate”", where: "ec-rule", prompt: "Doc comments: check that comments are accurate." },
    C: { group: "w", label: "+ “Be conservative”", where: "ec-rule", prompt: "Doc comments: check that comments are accurate. Be conservative." },
    H: { group: "w", label: "+ “Only report high-confidence findings”", where: "ec-rule", prompt: "Doc comments: check that comments are accurate. Only report findings you are highly confident about." },
    E: { group: "w", label: "Explicit criteria", where: "ec-rule", prompt: "Doc comments: flag a comment only when the behaviour it claims contradicts what the code does.\nDo not flag: spelling, missing comments, vague or old-looking wording, TODOs." },
    K: { group: "w", label: "Explicit criteria + severity by example", where: "ec-rule", prompt: "Doc comments: flag a comment only when the behaviour it claims contradicts what the code does.\nDo not flag: spelling, missing comments, vague or old-looking wording, TODOs.\nSeverity:\n  critical: following the comment moves money or data wrongly, e.g. “// amount in cents” over a dollars value.\n  major: following it makes a caller write wrong code, e.g. “// returns null” over code that throws.\n  minor: a detail no caller relies on, e.g. a stated retry count." },
    X: { group: "f", label: "Vague rule + three example findings", where: "ec-ex", prompt: "Doc comments: check that comments are accurate.\n+ three example findings showing the layout and a severity for each." },
    S: { group: "f", label: "Vague rule + a second pass that double-checks", where: "ec-second", prompt: "Doc comments: check that comments are accurate.\n+ a second call per finding: “Is this comment really inaccurate? Keep or drop.”" },
    D: { group: "f", label: "Drop the doc-comment category", where: "ec-rule", prompt: "(no doc-comment category)" },
  };
  // Severity slips: without defined levels the model labels d2 (money) as minor and d4 (retry count) as major.
  const MISLABEL = { d2: "minor", d4: "major" };
  const SEV_OK = { X: true, K: true };

  function decide(it, o) {
    let flagged;
    if (it.t === "real") flagged = it.cat !== "doc" || (o !== "D" && !(o === "H" && it.subtle));
    else flagged = !!it.by && it.by.indexOf(o) >= 0;
    let sev = it.sev;
    if (flagged && it.t === "real" && it.cat === "doc" && !SEV_OK[o] && MISLABEL[it.id]) sev = MISLABEL[it.id];
    if (flagged && it.t === "fine") sev = "minor";
    const s = !flagged ? (it.t === "real" ? "miss" : "skip") : it.t === "real" ? "tp" : "fp";
    return { s: s, sev: sev, wrongSev: flagged && it.t === "real" && sev !== it.sev };
  }

  function run(o) {
    const rows = ITEMS.map((it) => Object.assign({ it: it }, decide(it, o)));
    const n = (f) => rows.filter(f).length;
    const tp = n((r) => r.s === "tp"), fp = n((r) => r.s === "fp"), miss = n((r) => r.s === "miss");
    const docTp = n((r) => r.s === "tp" && r.it.cat === "doc"), docFp = n((r) => r.s === "fp" && r.it.cat === "doc");
    const slips = n((r) => r.wrongSev);
    const precision = tp / (tp + fp);
    const trust = Math.max(5, 100 - 5 * fp - 4 * slips);
    const secActed = Math.round((4 * trust) / 100);
    const acted = Math.round((tp * trust) / 100);
    // The second pass checks every first-pass finding, and the first pass is the vague rule.
    const calls = o === "S" ? 1 + ITEMS.filter((it) => decide(it, "V").s === "tp" || decide(it, "V").s === "fp").length : 1;
    return { o: o, rows: rows, tp: tp, fp: fp, miss: miss, docTp: docTp, docFp: docFp, slips: slips, precision: precision, trust: trust, secActed: secActed, acted: acted, calls: calls, verdict: verdict(o) };
  }

  function verdict(o) {
    return {
      V: ["rose", "Breaks trust", "More than half of what gets posted is noise: typos, missing docs, old-looking but true comments. Developers learn to skim the whole review, so the real security findings go unread too."],
      C: ["rose", "Barely helps", "“Be conservative” doesn't say what counts. Claude still flags typos, missing docs and old-looking comments; it just flags a few fewer of them."],
      H: ["butter", "Only usually works", "Claude is highly confident that a typo is a typo. Confidence wording trims the count, not the kind of noise, and it dropped the subtle thread-safety contradiction."],
      E: ["mint", "Also works", "Precision jumps: almost everything posted is a real contradiction. But nothing defines the levels, so the cents-vs-dollars bug came out minor and the retry count came out major."],
      K: ["mint", "Best fit (exam answer)", "Categorical criteria say what to flag and what to skip, and each severity level has a concrete code example. The noise is gone, the levels are right, and trust recovers for every category."],
      X: ["butter", "Different problem", "The examples made the layout and the levels consistent. But the rule is still “check that comments are accurate”, so typos and old-looking comments keep coming."],
      S: ["butter", "Overbuilt", "Every finding is checked again against the same vague standard. The model making the second call is just as sure that a typo is inaccurate. Many more calls, the same kind of noise."],
      D: ["butter", "Delays the problem", "Trust recovers, but six real contradictions now ship unflagged, including the cents-vs-dollars charge. Explicit criteria keep the category and remove the noise."],
    }[o];
  }

  if (typeof module !== "undefined") { module.exports = { run, ITEMS, OPTS }; return; }

  /* ---------- the page ---------- */
  const $ = (id) => document.getElementById(id);
  let o = "V", sel = "f1";
  const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
  const STATE = { tp: ["mint", "Flagged, rightly"], fp: ["rose", "False positive"], miss: ["butter", "Missed"], skip: ["", "Left alone, rightly"] };

  function draw() {
    [["ec-w", "w"], ["ec-f", "f"]].forEach(([id, g]) => {
      const box = $(id);
      box.innerHTML = "";
      Object.entries(OPTS).filter(([, v]) => v.group === g).forEach(([k, v]) => {
        const b = document.createElement("button");
        b.className = "btn sm" + (k === o ? " on" : "");
        b.textContent = v.label;
        b.onclick = () => { o = k; draw(); };
        box.appendChild(b);
      });
    });
    ["ec-rule", "ec-ex", "ec-second"].forEach((id) => { const el = $(id); if (el) el.setAttribute("stroke-width", id === OPTS[o].where ? "4" : "1.5"); });
    render();
  }

  function render() {
    const R = run(o);
    $("ec-prompt").textContent = OPTS[o].prompt;
    const g = $("ec-grid");
    g.innerHTML = "";
    Object.keys(CATS).forEach((c) => {
      const rows = R.rows.filter((r) => r.it.cat === c);
      const row = document.createElement("div");
      row.className = "ec-row";
      row.innerHTML = `<div class="ec-cat">${CATS[c]} <span>(${rows.length})</span></div>`;
      const cells = document.createElement("div");
      cells.className = "ec-cells";
      rows.forEach((r) => {
        const b = document.createElement("button");
        b.className = "ec-cell " + r.s + (r.it.id === sel ? " sel" : "") + (r.wrongSev ? " slip" : "");
        b.title = STATE[r.s][1];
        b.setAttribute("aria-label", r.it.id + ": " + STATE[r.s][1]);
        b.onclick = () => { sel = r.it.id; render(); };
        cells.appendChild(b);
      });
      row.appendChild(cells);
      g.appendChild(row);
    });
    const r = R.rows.find((x) => x.it.id === sel), it = r.it, st = STATE[r.s];
    let did;
    if (r.s === "tp" || r.s === "fp") {
      did = `<b>Posted:</b> <span class="chip">${r.sev}</span>${esc(it.msg)}`;
      if (r.wrongSev) did += ` <span class="chip rose">should be ${it.sev}</span>`;
    } else did = `<b>Not posted.</b>`;
    $("ec-detail").innerHTML = `<div class="ec-dh"><span class="chip ${st[0]}">${st[1]}</span><span class="chip">${CATS[it.cat]}${it.kind ? " · " + it.kind : ""}</span></div>
      <pre>${esc(it.code)}</pre><p style="margin:.3em 0">${did}</p><p style="margin:.3em 0;color:var(--muted)">${esc(it.why)}</p>`;

    const pct = Math.round(R.precision * 100);
    $("ec-tally").innerHTML = `<b>${R.tp + R.fp}</b> findings posted · <b>${R.tp}</b> real · <b>${R.fp}</b> false positive${R.fp === 1 ? "" : "s"} (${R.docFp} of them doc comments) · <b>${R.miss}</b> real problem${R.miss === 1 ? "" : "s"} missed<br>
      Precision (the share of posted findings that are real): <b>${pct}%</b>` +
      (R.slips ? ` · <b>${R.slips}</b> real findings with the wrong severity` : "") +
      ` · Model calls: <b>${R.calls}</b>${R.calls > 1 ? " (one review, plus one check per finding)" : ""}`;
    const t = R.trust, tone = t >= 80 ? "mint" : t >= 45 ? "butter" : "rose";
    $("ec-meter-fill").style.width = t + "%";
    $("ec-meter-fill").className = "fill " + tone;
    $("ec-meter-n").textContent = t;
    $("ec-acted").innerHTML = `Developers act on about <b>${R.secActed} of 4</b> real security findings and <b>${R.acted} of ${R.tp}</b> real findings overall. They don't read the categories separately: noise in one costs trust in all.`;
    const v = R.verdict;
    $("ec-verdict").className = "box " + v[0];
    $("ec-verdict").innerHTML = `<span class="chip ${v[0]}">${v[1]}</span> ${v[2]}`;
  }

  window.addEventListener("DOMContentLoaded", draw);
})();
