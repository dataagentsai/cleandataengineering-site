/* Tool failure simulator. Fully scripted: the same choice always plays the same trail, so a recording
   can be repeated. Durations are illustrative. */
(function () {
  const KNOWS = ["failure type", "retry or not", "what was tried", "partial results", "next options"];
  const FAILS = {
    search: { label: "Search times out", who: "Research system", decider: "coordinator", user: "the committee",
      story: "The literature-search subagent runs 5 journal queries. Queries 1 to 3 return 14 papers. Query 4 times out; the journal service is back in about 5 minutes." },
    payments: { label: "Payments API is down", who: "Support agent", decider: "coordinator", user: "the customer",
      story: "A customer asks for $60 back for a spoiled box. The policy subagent checks past refunds through the payments API, which is down for about an hour. (Hidden truth: this box was already refunded once.)" },
    rule: { label: "Business-rule refusal", who: "Support agent", decider: "agent", user: "the customer",
      story: "A customer asks to pause from the next box. That box is past its packing cut-off, so the backend refuses. The box after it can still be paused." },
    input: { label: "Bad input", who: "Support agent", decider: "agent", user: "the customer",
      story: "A customer asks about “last Tuesday's box”. The agent passes “last Tuesday” to lookup_order as the box ID. The box exists: B-7781." },
  };
  const HANDLE = {
    structured: { label: "Structured error", where: "box-tool" },
    generic:    { label: "Generic “Operation failed”", where: "box-tool" },
    empty:      { label: "Empty result marked success", where: "box-tool" },
    crash:      { label: "Exception that ends the run", where: "box-coord" },
    retry:      { label: "Retry with backoff, then “unavailable”", where: "box-sub" },
  };
  const ALL = [1, 1, 1, 1, 1], NONE = [0, 0, 0, 0, 0];
  // ret = what the tool returns; up = what reaches the decider; k = which of KNOWS it has; thinks = it believes success.
  const OUT = {
    search: {
      structured: { ret: '{ "isError": true, "errorCategory": "transient",\n  "isRetryable": true,\n  "attempted": "query 4 of 5: tranexamic acid, age 80+",\n  "partial": "14 papers from queries 1-3",\n  "alternatives": ["retry in a few minutes", "trial registry"] }',
        up: "The subagent passes the structured error up with its 14 papers.", k: ALL,
        does: "Keeps the 14 papers, asks the registry subagent to cover the gap now, and re-runs queries 4 and 5 after the outage.",
        told: "A summary of 19 papers, all cited, about 5 minutes later than usual.", lost: "", inv: "", time: "+5 min",
        v: ["Right fit", "mint", "The coordinator knows what failed, what was tried and what is already in hand, so it can choose: wait, use another source, or go on with a stated gap."] },
      generic: { ret: '{ "isError": true, "content": "Operation failed" }',
        up: "The subagent reports: “Operation failed.”", k: NONE,
        does: "Can't tell a timeout from a bad query. Re-runs the whole search from the start; the second run works once the outage is over.",
        told: "The full summary, 12 minutes late.", lost: "The 14 papers already found (fetched again from scratch).", inv: "", time: "+12 min",
        v: ["Recovers blindly", "butter", "It got there by guessing. With no category and no partial results, the coordinator redid finished work. On a long outage the same guess fails."] },
      empty: { ret: '{ "isError": false, "papers": [] }',
        up: "The subagent reports: “Search complete: 14 papers. Query 4: no results.”", k: NONE, thinks: true,
        does: "Believes there are no trials in patients over 80 and writes that into the summary.",
        told: "A summary of 14 papers that says “no trials have studied patients over 80”.", lost: "The 5 papers queries 4 and 5 would have found.", inv: "“No trials in patients over 80”. There are five.", time: "on time",
        v: ["Invents a fact", "rose", "A timeout dressed as an empty result turns “we don't know” into a confident, wrong finding in a guideline summary."] },
      crash: { ret: "TimeoutError: journal search exceeded 30 s\n  raised to the top-level handler",
        up: "Nothing. The handler ends the whole workflow.", k: NONE,
        does: "Stops. Finished work from the registry and analysis subagents is thrown away.",
        told: "“Run failed. Please resubmit the request.”", lost: "Every finished result in this run.", inv: "", time: "run lost",
        v: ["Ends the run", "rose", "One failed query of five shouldn't throw away the whole run. The coordinator never got the chance to recover."] },
      retry: { ret: "Query 4 retried 3 times over 45 s, each a timeout.\nThen: \"search unavailable\"",
        up: "The subagent reports: “search unavailable”.", k: [0, 0, 0, 0, 0],
        does: "Drops the literature search and writes the summary from the trial registry alone.",
        told: "A summary of 5 registry trials. No journal papers.", lost: "The 14 papers found before the timeout.", inv: "", time: "+45 s",
        v: ["Hides the context", "rose", "Retrying a blip locally is fine. Reporting only “unavailable” afterwards hides what was tried and the 14 papers already in hand."] },
    },
    payments: {
      structured: { ret: '{ "isError": true, "errorCategory": "transient",\n  "isRetryable": true,\n  "attempted": "refund history for C-1042",\n  "partial": "none",\n  "alternatives": ["re-check after the outage", "hand to a human"] }',
        up: "The policy subagent passes this up unchanged.", k: ALL,
        does: "Won't approve without the history. Logs the claim and queues a re-check for when the API is back.",
        told: "“Our payments system is down right now. I've logged your claim and we'll confirm by email within the hour.”", lost: "", inv: "", time: "about 1 h",
        v: ["Right fit", "mint", "The coordinator knows the check failed and that waiting will help. It doesn't guess; it tells the customer the truth and comes back. The re-check finds the earlier refund."] },
      generic: { ret: '{ "isError": true, "content": "Operation failed" }',
        up: "The policy subagent reports: “Operation failed.”", k: NONE,
        does: "Retries the subagent 3 times, gets the same failure, then gives up.",
        told: "“Sorry, something went wrong. Please try again later.”", lost: "The claim itself: nothing is logged.", inv: "", time: "+2 min",
        v: ["Leaves the user stuck", "butter", "Nothing false is said, but nothing useful either. The coordinator can't tell an outage from a bad request, so it can't plan a next step."] },
      empty: { ret: '{ "isError": false, "refunds": [] }',
        up: "The policy subagent reports: “No previous refunds found.”", k: NONE, thinks: true,
        does: "Approves the $60 refund.",
        told: "“Done! $60 is on its way.”", lost: "", inv: "“No previous refunds”. This box was already refunded, so the money goes out twice.", time: "on time",
        v: ["Invents a fact", "rose", "An outage reported as an empty history becomes a business decision made on a false fact. Real money leaves."] },
      crash: { ret: "ConnectionError: payments API unreachable\n  raised to the top-level handler",
        up: "Nothing. The chat session ends.", k: NONE,
        does: "Stops the conversation.",
        told: "“Something went wrong. This chat has ended.”", lost: "The claim and the whole chat.", inv: "", time: "chat lost",
        v: ["Ends the run", "rose", "One unreachable API ends a chat that could have been handled with an honest “we'll get back to you”."] },
      retry: { ret: "History check retried 3 times over 40 s, each unreachable.\nThen: \"history unavailable\"",
        up: "The policy subagent reports: “history unavailable”.", k: NONE,
        does: "Can't tell whether waiting will help, so it hands the case to a human with no detail.",
        told: "“I'm passing you to a colleague.” The colleague starts from scratch.", lost: "That the outage is temporary, and what was tried.", inv: "", time: "+40 s",
        v: ["Hides the context", "butter", "The retries were reasonable; the report after them wasn't. “Unavailable” drops the category, the retry advice and the options."] },
    },
    rule: {
      structured: { ret: '{ "isError": true, "errorCategory": "business",\n  "isRetryable": false,\n  "reason": "4 Nov box is past its packing cut-off",\n  "alternative": "pause can start from the 11 Nov box" }',
        up: "The agent reads the result directly.", k: ALL,
        does: "Doesn't retry. Explains the cut-off and offers the next pausable box.",
        told: "“Your 4 Nov box is already being packed, so it will still arrive. I can pause from 11 Nov. Shall I?”", lost: "", inv: "", time: "instant",
        v: ["Right fit", "mint", "A business error is not retryable and comes with a plain reason. The agent explains it and offers what is possible."] },
      generic: { ret: '{ "isError": true, "content": "Operation failed" }',
        up: "The agent reads: “Operation failed.”", k: NONE,
        does: "Retries 4 times, gets the same refusal each time, and assumes an outage.",
        told: "“Our system seems to be down. Please try again later.”", lost: "The reason and the 11 Nov option.", inv: "“The system is down”. It isn't; a rule refused the pause.", time: "+1 min",
        v: ["Misleads the user", "rose", "With no category, the agent can't tell a rule from an outage. It retries a refusal and then tells the customer something untrue."] },
      empty: { ret: '{ "isError": false }   (nothing was paused)',
        up: "The agent reads a success.", k: NONE, thinks: true,
        does: "Confirms the pause.",
        told: "“Done, your subscription is paused.”", lost: "", inv: "“Paused”. The 4 Nov box ships and is charged.", time: "instant",
        v: ["Invents a fact", "rose", "A refusal reported as success. The customer is told one thing and charged for another."] },
      crash: { ret: "PolicyError: packing cut-off passed\n  raised to the top-level handler",
        up: "Nothing. The chat session ends.", k: NONE,
        does: "Stops the conversation.",
        told: "“Something went wrong. This chat has ended.”", lost: "The request, the reason and the 11 Nov option.", inv: "", time: "chat lost",
        v: ["Ends the run", "rose", "A normal business refusal is treated as a crash. The customer leaves with nothing."] },
      retry: { ret: "Pause retried 3 times over 40 s, refused each time.\nThen: \"pause unavailable\"",
        up: "The agent reads: “pause unavailable”.", k: NONE,
        does: "Tells the customer to try later.",
        told: "“Pausing isn't available right now. Please try again later.”", lost: "The reason and the 11 Nov option.", inv: "", time: "+40 s",
        v: ["Retries a refusal", "rose", "A rule doesn't change on retry. Backoff wastes time and the customer comes back later to the same refusal."] },
    },
    input: {
      structured: { ret: '{ "isError": true, "errorCategory": "validation",\n  "isRetryable": false,\n  "detail": "box_id must look like B-1234; got \'last Tuesday\'",\n  "fix": "get_customer lists box IDs with dates" }',
        up: "The agent reads the result directly.", k: ALL,
        does: "Calls get_customer, finds Tuesday's box B-7781, and calls lookup_order again with the right ID.",
        told: "“Found it: your box from Tuesday, B-7781. What went wrong with it?”", lost: "", inv: "", time: "+2 s",
        v: ["Right fit", "mint", "A validation error says what was wrong with the input. The agent fixes the input; it doesn't repeat the same call."] },
      generic: { ret: '{ "isError": true, "content": "Operation failed" }',
        up: "The agent reads: “Operation failed.”", k: NONE,
        does: "Retries the same call with the same bad input 3 times.",
        told: "“I'm having trouble with our order system. Please try later.”", lost: "Why the call failed, and how to fix it.", inv: "“Trouble with the system”. The system is fine.", time: "+30 s",
        v: ["Retries blindly", "rose", "Without a category the agent can't see that the input was the problem, so it repeats a call that can never work."] },
      empty: { ret: '{ "isError": false, "orders": [] }',
        up: "The agent reads: no orders found.", k: NONE, thinks: true,
        does: "Concludes there is no such box.",
        told: "“I can't find a box from last Tuesday on your account.”", lost: "", inv: "“No box last Tuesday”. Box B-7781 exists.", time: "instant",
        v: ["Invents a fact", "rose", "Bad input reported as an empty result. The agent tells the customer their box doesn't exist."] },
      crash: { ret: "ValueError: invalid box_id 'last Tuesday'\n  raised to the top-level handler",
        up: "Nothing. The chat session ends.", k: NONE,
        does: "Stops the conversation.",
        told: "“Something went wrong. This chat has ended.”", lost: "The whole chat.", inv: "", time: "chat lost",
        v: ["Ends the run", "rose", "A fixable input mistake ends the chat. One more call would have solved it."] },
      retry: { ret: "Lookup retried 3 times over 40 s with the same input.\nThen: \"lookup unavailable\"",
        up: "The agent reads: “lookup unavailable”.", k: NONE,
        does: "Tells the customer to try later.",
        told: "“Our order system is unavailable. Please try again later.”", lost: "Why the call failed, and how to fix it.", inv: "“Unavailable”. It was the input, not the system.", time: "+40 s",
        v: ["Retries what can't change", "rose", "Backoff helps blips, not bad input. The same wrong ID fails every time."] },
    },
  };

  const $ = (id) => document.getElementById(id);
  let f = "search", h = "structured", timer = null;

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
    ["box-tool", "box-sub", "box-coord", "box-user"].forEach((id) => {
      const r = $(id);
      if (r) r.setAttribute("stroke-width", id === HANDLE[h].where ? "4" : "1.5");
    });
  }

  function draw() {
    buttons("sim-f", FAILS, f, (k) => { f = k; });
    buttons("sim-h", HANDLE, h, (k) => { h = k; });
    $("sim-story").innerHTML = `<span class="chip">${FAILS[f].who}</span>${FAILS[f].story}`;
    highlight();
    run();
  }

  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;"); }

  function run() {
    clearTimeout(timer);
    const F = FAILS[f], o = OUT[f][h];
    const knows = o.thinks ? `<span class="chip rose">thinks it succeeded</span>`
      : o.k.every((x) => !x) ? `<span class="chip rose">only that something failed</span>`
      : KNOWS.map((n, i) => `<span class="chip ${o.k[i] ? "mint" : "rose"}">${o.k[i] ? "" : "missing: "}${n}</span>`).join("");
    const steps = [
      ["1. The tool returns", `<pre>${esc(o.ret)}</pre>`],
      [`2. What reaches the ${F.decider}`, esc(o.up)],
      [`3. What the ${F.decider} knows`, knows],
      [`4. What the ${F.decider} does`, esc(o.does)],
      [`5. What ${F.user} is told`, `<div class="told">${esc(o.told)}</div>`],
    ];
    const trail = $("sim-trail");
    trail.innerHTML = "";
    const els = steps.map(([t, body]) => {
      const d = document.createElement("div");
      d.className = "step";
      d.innerHTML = `<b>${t}</b><div>${body}</div>`;
      trail.appendChild(d);
      return d;
    });
    let i = 0;
    (function step() { if (i < els.length) { els[i++].classList.add("in"); timer = setTimeout(step, 220); } })();
    $("sim-tally").innerHTML =
      `<span class="chip ${o.lost ? "rose" : "mint"}">Lost</span>${o.lost ? esc(o.lost) : "nothing"}<br>` +
      `<span class="chip ${o.inv ? "rose" : "mint"}">Invented</span>${o.inv ? esc(o.inv) : "nothing"}<br>` +
      `<span class="chip">Delay</span>${o.time}`;
    $("sim-verdict").className = "box " + o.v[1];
    $("sim-verdict").innerHTML = `<span class="chip ${o.v[1]}">${o.v[0]}</span> ${o.v[2]}`;
  }

  window.FailSim = { OUT, FAILS, HANDLE };
  window.addEventListener("DOMContentLoaded", draw);
})();
