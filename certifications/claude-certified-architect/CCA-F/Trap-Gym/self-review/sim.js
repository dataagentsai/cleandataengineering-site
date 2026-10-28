/* Self-review simulator. Fully scripted: the same change and the same reviewer always give the same
   findings, so a recording can be repeated. The bugs are seeded; which ones each reviewer catches is
   illustrative, chosen to show the shape the exam guide describes (the writing session keeps its own
   reasoning and won't question it; an independent instance catches subtle issues better than self-review or
   extended thinking; per-file passes plus a cross-file pass avoid attention dilution and contradictions). */
(function () {
  const CHANGES = {
    small: { label: "Small: fix proration, 2 files", kind: "3 seeded bugs", tone: "mint",
      files: ["billing/proration.py", "tests/test_proration.py"] },
    large: { label: "Large: multi-currency invoices, 12 files", kind: "8 seeded bugs", tone: "rose",
      files: ["config/settings.py", "money/currency.py", "money/rounding.py", "billing/proration.py", "billing/invoice.py", "billing/invoice_pdf.py",
              "ledger/ledger.py", "events/webhook.py", "api/refunds.py", "jobs/nightly_fx.py", "tests/test_proration.py", "tests/test_invoice.py"] },
  };
  const REVIEWERS = {
    same:  { label: "The same session that wrote it", where: ["box-self"] },
    think: { label: "Same session + extended thinking", where: ["box-self"] },
    fresh: { label: "An independent review instance", where: ["box-fresh"] },
    multi: { label: "Multi-pass: per-file passes + a cross-file pass", where: ["box-perfile", "box-integ"] },
  };
  // Bugs: [id, files (indexes), kind, text]. kind: plain = a slip anyone spots; mine = comes from the writer's
  // own decision, so the writer reads it as correct; cross = only visible by comparing two files.
  const BUGS = {
    small: [
      ["s1", [0], "mine", "Off by one on the last day of the month: uses < where it needs <="],
      ["s2", [1], "mine", "The new test expects the off-by-one result, so it passes"],
      ["s3", [0], "plain", "No guard for a zero-day period: divides by zero"],
    ],
    large: [
      ["b1", [2], "mine", "Rounds each line, then adds them up: totals drift by a cent"],
      ["b2", [3], "mine", "Off by one on the last day of the month"],
      ["b3", [1], "plain", "No check when an exchange rate is missing: crashes on None"],
      ["b4", [5], "plain", "Prints “$” for every currency"],
      ["b5", [11], "mine", "The test asserts the per-line-rounded total, locking in the rounding bug"],
      ["b6", [0, 9], "cross", "settings.py renames fx_source to fx_provider; the nightly job still reads fx_source"],
      ["b7", [1, 8], "cross", "convert(amount, to) became convert(amount, from, to); refunds still passes two arguments"],
      ["b8", [7, 6], "cross", "The webhook sends amounts in cents; the ledger reads them as whole units"],
    ],
  };
  // depth per file: d = read in depth, t = thin (skimmed), o = checked against its own plan.
  const OUT = {
    small: {
      same:  { caught: ["s3"], depth: "oo",
        says: "“Looks right. I added a guard for zero-day periods.”",
        v: ["Same blind spot", "rose", "It checked the code against the reasoning that wrote it, so the two bugs that came from that reasoning looked correct."] },
      think: { caught: ["s3"], depth: "oo",
        says: "“I re-derived the boundary step by step: < is correct for the last day. Guard added for zero days.”",
        v: ["Same blind spot", "rose", "More thinking, same assumptions. It re-derived the boundary the same way it first wrote it, and agreed with itself."] },
      fresh: { caught: ["s1", "s2", "s3"], depth: "dd",
        says: "“Line 41: the last day of the month is excluded. The test on line 18 expects that wrong value. Line 30 divides by zero for a zero-day period.”",
        v: ["Best fit (exam answer)", "mint", "A fresh instance sees only the code, not the reasoning behind it, so it reads what is there. For two files, one fresh pass is enough."] },
      multi: { caught: ["s1", "s2", "s3"], depth: "dd", passes: 3,
        says: "Pass 1 (proration.py): off by one, divide by zero. Pass 2 (test): expects the wrong value. Cross-file pass: nothing new.",
        v: ["Overbuilt", "butter", "The same three bugs as one fresh pass, for three runs instead of one. Split the review when the change is too big for one pass, not before."] },
    },
    large: {
      same:  { caught: ["b3", "b4"], depth: "oooooooooooo",
        says: "“Reviewed all 12 files. Fixed a missing-rate check and the currency symbol. Rounding and proration are as designed.”",
        v: ["Breaks", "rose", "It found the two plain slips and nothing else. Every bug that came from its own decisions, and every bug between files, passed as “as designed”."] },
      think: { caught: ["b3", "b4", "b7"], depth: "oooooooooooo",
        says: "“Traced each signature I changed: refunds still calls convert with two arguments, fixed. Rounding per line is intended.”",
        v: ["Same blind spot", "rose", "Extended thinking helped it trace a change it remembered making. It still trusted its own rounding and proration choices, and the tests it wrote to match them."] },
      fresh: { caught: ["b1", "b2", "b3", "b4"], depth: "ddddddtttttt", contra: true,
        says: "“rounding.py: round the invoice total once, not each line.” … “test_invoice.py: per-line rounding matches finance rules, looks right.”",
        v: ["Attention diluted", "butter", "Fresh eyes found the subtle bugs in the early files, then went thin from file 7 on, missed every cross-file bug and contradicted itself on rounding. Right reviewer, too much for one pass."] },
      multi: { caught: ["b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8"], depth: "dddddddddddd", passes: 13,
        says: "12 per-file passes: 5 local bugs. Cross-file pass, comparing each changed key, signature and unit with its users: 3 more.",
        v: ["Best fit (exam answer)", "mint", "Fresh instances, one file at a time, give each file full attention; then one pass across files catches what no single file shows. All 8 found, no contradictions."] },
    },
  };
  const KIND = { plain: "plain slip", mine: "from the writer's own decision", cross: "between files" };
  const BOXES = ["box-self", "box-fresh", "box-perfile", "box-integ"];

  const $ = (id) => document.getElementById(id);
  let c = "large", r = "same";

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
    buttons("sim-c", CHANGES, c, (k) => (c = k));
    buttons("sim-v", REVIEWERS, r, (k) => (r = k));
    BOXES.forEach((id) => { const e = $(id); if (e) e.setAttribute("stroke-width", REVIEWERS[r].where.includes(id) ? "4" : "1.5"); });
    run();
  }

  function run() {
    const o = OUT[c][r], bugs = BUGS[c], files = CHANGES[c].files;
    const got = (b) => o.caught.includes(b[0]);
    // File cards
    const fb = $("sim-files");
    fb.innerHTML = "";
    files.forEach((f, i) => {
      const mine = bugs.filter((b) => b[1].includes(i));
      const missed = mine.filter((b) => !got(b)).length, found = mine.length - missed;
      const d = o.depth[i];
      const card = document.createElement("div");
      card.className = "fc " + (missed ? "miss" : found ? "ok" : "clean") + (d === "t" ? " thin" : "");
      card.innerHTML = `<code>${f}</code><span class="dp">${d === "d" ? "read in depth" : d === "t" ? "skimmed" : "checked against its plan"}</span>` +
        `<span class="mk">${mine.map((b) => `<i class="${got(b) ? "y" : "n"}" title="${b[3]}">${got(b) ? "found" : "missed"}</i>`).join(" ")}</span>`;
      fb.appendChild(card);
    });
    // Bug table
    $("sim-bugs").innerHTML = `<tr><th>Seeded bug</th><th>Kind</th><th>Result</th></tr>` + bugs.map((b) =>
      `<tr class="${got(b) ? "y" : "n"}"><td>${b[3]}<br><span class="fl">${b[1].map((i) => files[i]).join(" and ")}</span></td><td>${KIND[b[2]]}</td><td><span class="chip ${got(b) ? "mint" : "rose"}">${got(b) ? "found" : "missed"}</span></td></tr>`
    ).join("");
    $("sim-says").innerHTML = `<b>The reviewer reports:</b> ${o.says}`;
    const n = (k) => bugs.filter((b) => b[2] === k).length, m = (k) => bugs.filter((b) => b[2] === k && got(b)).length;
    let t = `Found: <b>${o.caught.length} of ${bugs.length}</b> · plain slips <b>${m("plain")}/${n("plain")}</b> · from the writer's own decisions <b>${m("mine")}/${n("mine")}</b>`;
    if (n("cross")) t += ` · between files <b>${m("cross")}/${n("cross")}</b>`;
    t += ` · Contradictions: <b>${o.contra ? 1 : 0}</b> · Review runs: <b>${o.passes || 1}</b>`;
    $("sim-tally").innerHTML = t;
    $("sim-verdict").className = "box " + o.v[1];
    $("sim-verdict").innerHTML = `<span class="chip ${o.v[1]}">${o.v[0]}</span> ${o.v[2]}`;
  }

  window.addEventListener("DOMContentLoaded", draw);
})();
