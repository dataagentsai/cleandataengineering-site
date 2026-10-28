/* tool_choice simulator. Deterministic: the same request and setting always replay the same 200 requests,
   so a recording can be repeated. Rates are illustrative, chosen to show the shape the exam guide describes:
   "auto" may return text, "any" must call a tool (Claude picks which), a forced tool runs that exact tool. */
(function () {
  const N = 200;
  const REQ = {
    invoice: {
      label: "Invoice pipeline", tools: ["extract_metadata", "enrich_vendor", "lookup_po"], forced: "extract_metadata",
      story: "Each invoice is one request. The tools are <code>extract_metadata</code>, <code>enrich_vendor</code> and <code>lookup_po</code>. Enrichment needs the vendor ID and PO number that extraction produces, so <b>extract_metadata must run first</b>. The script reads only tool input; a text reply is dropped.",
    },
    chat: {
      label: "Support chat", tools: ["lookup_order", "start_return"], forced: "lookup_order",
      story: "A customer chat. The tools are <code>lookup_order</code> and <code>start_return</code>. About 7 in 10 messages need <b>no tool</b> (“What time do you close on Sunday?”, “Thanks!”), and Claude should just answer in text. The rest ask about an order.",
    },
    docs: {
      label: "Unlabelled documents", tools: ["extract_certificate", "extract_endorsement", "extract_schedule"], forced: "extract_certificate",
      story: "Each uploaded document goes alone to a request with three extraction tools, one schema per document type. Uploads carry <b>no type label</b>. The output must <b>always be structured</b>: the parser reads only tool input. When Claude calls a tool, it already picks the right one.",
    },
  };
  const CHOICE = {
    auto:   { label: '"auto"', where: "tc-auto" },
    any:    { label: '"any"', where: "tc-any" },
    forced: { label: "forced named tool", where: "tc-tool" },
    none:   { label: '"none"', where: "tc-none" },
  };
  // Outcome kinds, one colour each in the grid.
  const KIND = {
    ok:       { c: "ok",   chip: "mint",  label: "what the step needed" },
    text:     { c: "miss", chip: "rose",  label: "text where a tool call was needed" },
    wrong:    { c: "warn", chip: "butter", label: "a tool ran, but the wrong one" },
    needless: { c: "warn", chip: "butter", label: "tool call where a plain answer was right" },
    cant:     { c: "miss", chip: "rose",  label: "needed a tool, but tools were off" },
  };

  // For each request and setting: share of each failure kind (the rest is ok), plus the verdict.
  // chat items are split: 30% need lookup_order, 70% need no tool.
  const OUT = {
    invoice: {
      auto:   { p: { text: 0.06, wrong: 0.09 }, v: ["Only usually works", "butter", "Claude usually starts with extract_metadata, but “auto” lets it reply in text or start with enrichment. A few invoices are dropped or enriched from a guess."] },
      any:    { p: { wrong: 0.10 }, v: ["Different problem", "butter", "“any” ends the text replies, but Claude still chooses which tool. Some invoices start with enrich_vendor before the fields exist."] },
      forced: { p: {}, v: ["Best fit (exam answer)", "mint", "Forcing extract_metadata on the first request makes that exact tool run first, every time. The next request goes back to “auto” so enrichment can choose its tools."] },
      none:   { p: { cant: 1 }, v: ["Breaks", "rose", "No tool may be called, so every invoice comes back as a prose summary and the script drops it."] },
    },
    chat: {
      auto:   { p: { needless: 0.01 }, only: "plain", v: ["Best fit (exam answer)", "mint", "Claude answers in text when no tool is needed and calls lookup_order when a message is about an order. This is what “auto” is for."] },
      any:    { p: { needless: 1 }, only: "plain", v: ["Breaks the chat", "rose", "Every reply must be a tool call, so “Thanks!” triggers an order lookup and nobody gets a plain answer. “any” is for steps that must end in a tool call, not for conversation."] },
      forced: { p: { needless: 1 }, only: "plain", v: ["Breaks the chat", "rose", "Every message runs lookup_order, even “What time do you close?”. A forced tool belongs on one request, not on a whole conversation."] },
      none:   { p: { cant: 1 }, only: "order", v: ["Breaks", "rose", "Plain questions are fine, but order questions can't be looked up. Claude can only apologise or guess. “none” is a real API value but not one the exam guide lists."] },
    },
    docs: {
      auto:   { p: { text: 0.07 }, v: ["Only usually works", "butter", "Most documents get the right extractor, but “auto” lets Claude reply with a prose summary now and then, and the parser drops it."] },
      any:    { p: {}, v: ["Best fit (exam answer)", "mint", "“any” guarantees a tool call rather than text, and leaves the choice of schema to Claude, which already picks well."] },
      forced: { p: { wrong: 1 }, only: "notcert", v: ["Breaks", "rose", "Every document is pushed into the certificate schema, so endorsements and schedules come out as wrong, half-empty records. Force one tool only when you know which one must run."] },
      none:   { p: { cant: 1 }, v: ["Breaks", "rose", "No tool may be called, so every document comes back as prose and the parser rejects it."] },
    },
  };

  // Sample trace per request and outcome kind: [response block, what happens next].
  const SAMPLE = {
    invoice: {
      input: "Invoice INV-2291 from Northwind Paper (PDF text)",
      ok: ['stop_reason: "tool_use"\ntool_use: extract_metadata\n{ "invoice_no": "INV-2291", "vendor": "Northwind Paper",\n  "po_number": "PO-7781", "total": 1840.00 }', "Extraction runs first. The next request (back on “auto”) calls enrich_vendor and lookup_po with real IDs."],
      text: ['stop_reason: "end_turn"\ntext: "This is an invoice from Northwind Paper\n       for $1,840.00, due 30 November."', "The script reads only tool input. Nothing to enrich: the invoice is dropped."],
      wrong: ['stop_reason: "tool_use"\ntool_use: enrich_vendor\n{ "vendor_name": "Northwind" }', "Enrichment ran on a guessed vendor name, with no PO number. The record is saved incomplete."],
      cant: ['stop_reason: "end_turn"\ntext: "Here is a summary of the invoice: Northwind\n       Paper, $1,840.00, PO-7781."', "No tool call, so the script has nothing to read. The invoice is dropped."],
    },
    chat: {
      plain: "Customer: What time do you close on Sunday?",
      order: "Customer: Where is order A-1043?",
      ok: ['stop_reason: "end_turn"\ntext: "We close at 6 pm on Sundays."', "A plain answer, straight away. Order questions still get lookup_order."],
      okOrder: ['stop_reason: "tool_use"\ntool_use: lookup_order\n{ "order_id": "A-1043" }', "The lookup returns “shipped Tuesday”, and Claude tells the customer."],
      needless: ['stop_reason: "tool_use"\ntool_use: lookup_order\n{ "order_id": "" }', "The lookup fails on an empty ID. An extra round trip, and the customer still has no answer about Sunday."],
      cant: ['stop_reason: "end_turn"\ntext: "I\'m sorry, I can\'t check orders right now.\n       It should arrive soon."', "No lookup was allowed. The customer gets an apology and a guess."],
    },
    docs: {
      input: "Endorsement no. 4 to policy P-552 (no type label)",
      inputCert: "Certificate of insurance for Harbor Freight Co. (no type label)",
      ok: ['stop_reason: "tool_use"\ntool_use: extract_endorsement\n{ "policy": "P-552", "endorsement_no": 4,\n  "effective": "2026-11-01", "change": "add vehicle" }', "The parser reads the endorsement record."],
      okCert: ['stop_reason: "tool_use"\ntool_use: extract_certificate\n{ "holder": "Harbor Freight Co.", "policy": "P-310",\n  "expires": "2027-03-31" }', "The parser reads the certificate record."],
      text: ['stop_reason: "end_turn"\ntext: "This document is an endorsement to policy\n       P-552 that adds a vehicle from 1 November."', "The parser finds no tool input and rejects the reply."],
      wrong: ['stop_reason: "tool_use"\ntool_use: extract_certificate\n{ "holder": null, "policy": "P-552",\n  "expires": null }', "A valid certificate record for a document that isn't a certificate. The endorsement details are lost."],
      cant: ['stop_reason: "end_turn"\ntext: "This document is an endorsement to policy\n       P-552 that adds a vehicle from 1 November."', "No tool call allowed, so the parser rejects every document."],
    },
  };

  function rng(seedStr) {
    let h = 1779033703 ^ seedStr.length;
    for (let i = 0; i < seedStr.length; i++) { h = Math.imul(h ^ seedStr.charCodeAt(i), 3432918353); h = (h << 13) | (h >>> 19); }
    let a = h >>> 0;
    return function () { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  }

  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
  let r = "invoice", c = "auto", timer = null;

  function choiceJson() {
    if (c === "forced") return `{ "type": "tool", "name": "${REQ[r].forced}" }`;
    return `{ "type": "${c}" }`;
  }

  function buttons(boxId, items, current, set, labelFn) {
    const box = $(boxId);
    box.innerHTML = "";
    Object.entries(items).forEach(([k, v]) => {
      const x = document.createElement("button");
      x.className = "btn" + (k === current ? " on" : "");
      x.innerHTML = labelFn ? labelFn(k, v) : v.label;
      x.onclick = () => { set(k); draw(); };
      box.appendChild(x);
    });
  }

  function highlight() {
    ["tc-none", "tc-auto", "tc-any", "tc-tool"].forEach((id) => {
      const e = $(id);
      if (e) e.setAttribute("stroke-width", id === CHOICE[c].where ? "4" : "1.5");
    });
    const n = $("tc-tool-name");
    if (n) n.textContent = "e.g. " + REQ[r].forced;
  }

  function draw() {
    buttons("sim-r", REQ, r, (k) => (r = k));
    buttons("sim-c", CHOICE, c, (k) => (c = k), (k, v) =>
      k === "forced" ? `forced <code>${REQ[r].forced}</code>` : `<code>${esc(v.label)}</code>`);
    $("sim-story").innerHTML = REQ[r].story;
    $("sim-req").textContent =
      `{ "model": "…", "tools": [ ${REQ[r].tools.map((t) => `"${t}"`).join(", ")} ],\n  "tool_choice": ${choiceJson()},\n  "messages": [ … ] }`;
    highlight();
    run();
  }

  // Build the 200 outcomes for the current request and setting.
  function outcomes() {
    const o = OUT[r][c], g = rng(r + ":" + c), items = [];
    for (let i = 0; i < N; i++) {
      let sub = null;
      if (r === "chat") sub = g() < 0.3 ? "order" : "plain";
      if (r === "docs") sub = g() < 1 / 3 ? "cert" : "notcert";
      let kind = "ok";
      const applies = !o.only || o.only === sub;
      if (applies) {
        const x = g();
        let acc = 0;
        for (const [k, p] of Object.entries(o.p)) { acc += p; if (x < acc) { kind = k; break; } }
      }
      items.push({ kind, sub });
    }
    return items;
  }

  function trace(kind, sub) {
    const S = SAMPLE[r];
    let input = S.input, resp, next;
    if (r === "chat") input = sub === "order" ? S.order : S.plain;
    if (r === "docs" && sub === "cert") input = S.inputCert;
    if (kind === "ok" && r === "chat" && sub === "order") [resp, next] = S.okOrder;
    else if (kind === "ok" && r === "docs" && sub === "cert") [resp, next] = S.okCert;
    else [resp, next] = S[kind];
    const K = KIND[kind];
    return `<div class="trace"><span class="chip ${K.chip}">${K.label}</span>` +
      `<div class="tl"><b>Input</b> ${esc(input)}</div>` +
      `<div class="tl"><b>Response</b><pre>${esc(resp)}</pre></div>` +
      `<div class="tl"><b>Next</b> ${esc(next)}</div></div>`;
  }

  function run() {
    clearTimeout(timer);
    const o = OUT[r][c], items = outcomes(), grid = $("sim-grid");
    grid.innerHTML = "";
    const cells = items.map((it) => { const e = document.createElement("i"); e.dataset.s = KIND[it.kind].c; grid.appendChild(e); return e; });
    let i = 0;
    (function step() {
      for (let k = 0; k < 25 && i < N; k++, i++) cells[i].className = cells[i].dataset.s;
      if (i < N) timer = setTimeout(step, 16);
    })();

    const count = {};
    items.forEach((it) => (count[it.kind] = (count[it.kind] || 0) + 1));
    const textReplies = items.filter((it) => it.kind === "text" || it.kind === "cant" || (it.kind === "ok" && r === "chat" && it.sub === "plain")).length;
    $("sim-tally").innerHTML =
      `<span class="chip">Response type</span><b>${N - textReplies}</b> tool_use · <b>${textReplies}</b> text<br>` +
      Object.keys(KIND).filter((k) => count[k]).map((k) => `<span class="chip ${KIND[k].chip}">${count[k]}</span>${KIND[k].label}`).join("<br>");

    // One sample trace per outcome kind seen, failures first (at most 3).
    const seen = [];
    const order = ["text", "cant", "wrong", "needless", "ok"];
    order.forEach((k) => {
      const subs = [...new Set(items.filter((it) => it.kind === k).map((it) => it.sub))];
      subs.forEach((s) => { if (seen.length < 3) seen.push([k, s]); });
    });
    $("sim-trace").innerHTML = seen.map(([k, s]) => trace(k, s)).join("");
    $("sim-verdict").className = "box " + o.v[1];
    $("sim-verdict").innerHTML = `<span class="chip ${o.v[1]}">${o.v[0]}</span> ${esc(o.v[2])}`;
  }

  window.ToolChoiceSim = { OUT, REQ, CHOICE, set: (rr, cc) => { r = rr; c = cc; draw(); } };
  window.addEventListener("DOMContentLoaded", draw);
})();
