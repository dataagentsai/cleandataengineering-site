/* Stop reason simulator. Fully scripted: the same two choices always play the same run, so a recording
   can be repeated. Replies, tool results and dates are made up for the example. */
(function () {
  const ANSWER = "Your order 4471 is at the DHL depot in Leeds and should arrive on Thursday 30 October. Anything else I can help with?";
  const SLOT = "Your order 4471 is at the DHL depot in Leeds and will arrive on Thursday 30 October, between 9 am and 1 pm. Anything else I can help with?";
  const NODELAY = "Your order 4471 is at the DHL depot in Leeds. DHL reports no delays there, so it should arrive on Thursday 30 October. Anything else I can help with?";
  const CUT = "Your order 4471 is at the DHL depot in Leeds and should arr";
  const SEQ = "Your order 4471 is at the DHL depot in Leeds and should arrive on Thursday 30 October.";
  const PAUSED = "Checking for delays at the Leeds depot.";
  const HANDOFF = "I can't finish this one here, so I've passed it to a colleague, who will reply within the hour.";

  // The first two turns are the same in every run.
  const T1 = { sr: "tool_use", text: "Let me check that order.", call: 'lookup_order({"order_id": "4471"})',
    result: '{"status": "shipped", "carrier": "DHL", "tracking": "JD0144"}' };
  const T2 = { sr: "tool_use", text: "", call: 'check_carrier({"tracking": "JD0144"})',
    result: '{"at": "Leeds depot", "eta": "Thu 30 Oct"}' };

  // Turn 3, by the value the learner picks.
  const PICKS = {
    end_turn: { label: "end_turn", text: ANSWER,
      note: "Claude has the answer and has finished its turn." },
    tool_use: { label: "tool_use", text: "", call: 'get_delivery_slot({"order_id": "4471"})', result: '{"slot": "9 am to 1 pm"}',
      next: { sr: "end_turn", text: SLOT },
      note: "Claude wants one more tool: the delivery time slot." },
    max_tokens: { label: "max_tokens", text: CUT,
      next: { sr: "end_turn", text: ANSWER },
      note: "The reply hit the max_tokens limit your code set, so it stops mid-word." },
    stop_sequence: { label: "stop_sequence", text: SEQ, extra: 'stop_sequence: "</reply>"',
      note: "Your app told Claude to end the customer reply with </reply> and set that as a stop sequence. It fired." },
    pause_turn: { label: "pause_turn", text: PAUSED, server: 'web_search("DHL Leeds depot delays") ran on Anthropic\'s side',
      next: { sr: "end_turn", text: NODELAY },
      note: "The agent also has the web_search server tool. A long server-tool turn paused partway." },
    refusal: { label: "refusal", text: "", extra: 'stop_details: {"type": "refusal", "category": null}',
      note: "Unlikely for an order question; included so you can see the handling. Claude declined for safety reasons." },
  };

  const LOOPS = {
    all6: { label: "(a) Handle all six values", where: "box-sr",
      code: [
        "while True:",
        "    r = client.messages.create(**req, messages=msgs)",
        '    msgs.append({"role": "assistant", "content": r.content})',
        '    if r.stop_reason == "tool_use":',
        '        msgs.append({"role": "user", "content": run_tools(r)})  # tool_result blocks',
        '    elif r.stop_reason == "end_turn":',
        "        return text_of(r)",
        '    elif r.stop_reason == "max_tokens":',
        '        msgs.pop(); req["max_tokens"] *= 2   # cut off: drop it, raise, resend',
        '    elif r.stop_reason == "stop_sequence":',
        "        return text_of(r)                 # r.stop_sequence says which one fired",
        '    elif r.stop_reason == "pause_turn":',
        "        continue                          # send it back as-is; Claude carries on",
        '    elif r.stop_reason == "refusal":',
        "        return hand_to_person(r.stop_details)  # never resend the same request",
      ] },
    tooluse: { label: "(b) Loop while tool_use, else stop", where: "box-sr",
      code: [
        "while True:",
        "    r = client.messages.create(**req, messages=msgs)",
        '    msgs.append({"role": "assistant", "content": r.content})',
        '    if r.stop_reason != "tool_use":       # end_turn: Claude is done',
        "        return text_of(r)",
        '    msgs.append({"role": "user", "content": run_tools(r)})  # tool_result blocks',
      ] },
    text: { label: "(c) Stop when the reply has text", where: "box-text",
      code: [
        "while True:",
        "    r = client.messages.create(**req, messages=msgs)",
        '    msgs.append({"role": "assistant", "content": r.content})',
        '    if any(b.type == "text" for b in r.content):   # anti-pattern',
        "        return text_of(r)",
        '    msgs.append({"role": "user", "content": run_tools(r)})',
      ] },
    words: { label: "(d) Stop when it sounds finished", where: "box-words",
      code: [
        "for _ in range(10):                      # a safety net, not the stop",
        "    r = client.messages.create(**req, messages=msgs)",
        '    msgs.append({"role": "assistant", "content": r.content})',
        '    if "anything else" in text_of(r).lower():      # anti-pattern',
        "        return text_of(r)",
        "    if has_tool_calls(r):",
        '        msgs.append({"role": "user", "content": run_tools(r)})',
        "return text_of(r)",
      ] },
    cap: { label: "(e) Stop after 3 turns", where: "box-count",
      code: [
        "for turn in range(3):                    # anti-pattern: the cap is the stop",
        "    r = client.messages.create(**req, messages=msgs)",
        '    msgs.append({"role": "assistant", "content": r.content})',
        "    if has_tool_calls(r):",
        '        msgs.append({"role": "user", "content": run_tools(r)})',
        "return text_of(r)",
      ] },
  };

  const NOTHING = "(nothing: the last reply had no text)";
  const got = (t) => {
    const parts = [];
    if (t.text) parts.push(`text: “${t.text}”`);
    if (t.server) parts.push(t.server);
    if (t.call) parts.push(`tool call: ${t.call}`);
    if (t.extra) parts.push(t.extra);
    if (!parts.length) parts.push("no content blocks");
    return parts.join("\n");
  };
  const ran = (t) => `Ran ${t.call.split("(")[0]}, appended the tool_result: ${t.result}. Called Claude again.`;

  // Plays one run. Returns { turns, skipped, sees, calls, tools, v: [label, colour, note] }.
  function play(pick, loop) {
    const P = PICKS[pick];
    const t3 = Object.assign({ sr: pick }, P);
    const turns = [];
    let tools = 0;
    const add = (n, t, did) => turns.push({ n, sr: t.sr, got: got(t), did });
    const out = (sees, v, skipped) => ({ turns, skipped: skipped || "", sees, calls: turns.length, tools, v });

    // (c): stops at the first text block, which is turn 1 in every run.
    if (loop === "text") {
      add(1, T1, "Found a text block, so treated the run as finished. The lookup_order call was never run.");
      const r = out("Let me check that order.", ["Breaks", "rose",
        "Claude wrote a short line and asked for a tool in the same reply. The loop saw text and stopped, so nothing was looked up. Your turn-3 pick never happened."],
        "Turns 2 and 3 were never sent.");
      r.calls = 1;
      return r;
    }

    add(1, T1, loop === "words" ? "No “Anything else” in the text. " + ran(T1) : ran(T1)); tools++;
    add(2, T2, loop === "words" ? "No text at all. " + ran(T2) : ran(T2)); tools++;

    if (loop === "all6") {
      const finish = (did3, t4, did4, sees, v) => {
        add(3, t3, did3);
        if (t4) add(4, t4, did4);
        return Object.assign(out(sees, v), { calls: t4 ? 4 : 3 });
      };
      const R = (n) => ["Handled right", "mint", n];
      switch (pick) {
        case "end_turn": return finish("end_turn: showed the text as the answer.", null, "", ANSWER,
          ["Best fit (exam answer, and more)", "mint", "Read stop_reason after every call: two tool_use turns ran their tools, end_turn ended the loop. This is the guide's loop, with the other four values handled as well."]);
        case "tool_use": tools++; return finish("tool_use: " + ran(t3), P.next, "end_turn: showed the text as the answer.", SLOT,
          ["Best fit (exam answer, and more)", "mint", "A third tool_use is no different from the first two: run it, append the tool_result, call again. The loop ends on end_turn, after 4 calls, because that's when Claude was done."]);
        case "max_tokens": return finish("max_tokens: the reply was cut off, so it is not final. Dropped it, doubled max_tokens and resent.", P.next, "end_turn: showed the text as the answer.", ANSWER,
          R("max_tokens means “cut off”, not “finished”. The loop didn't show half a sentence; it gave Claude more room and asked again. (Beyond the exam guide.)"));
        case "stop_sequence": return finish("stop_sequence: the app's own “</reply>” fired. Took the text before it as the customer reply, as the app intended.", null, "", SEQ,
          R("A stop sequence is a stop your app asked for, so the text before it is what you wanted. The response's stop_sequence field says which one fired. (Beyond the exam guide.)"));
        case "pause_turn": return finish("pause_turn: sent the response back as-is so Claude could carry on.", P.next, "end_turn: showed the text as the answer.", NODELAY,
          R("pause_turn means a long server-tool turn paused, not that Claude finished. Sending the response back lets it continue. (Beyond the exam guide.)"));
        case "refusal": return finish("refusal: did not resend the same request. Read stop_details, told the customer, and routed the chat to a person.", null, "", HANDOFF,
          R("A refusal won't change if you resend the same request. Telling the customer and routing to a person is the honest path; stop_details gives a category when there is one. (Beyond the exam guide.)"));
      }
    }

    if (loop === "tooluse") {
      if (pick === "tool_use") {
        add(3, t3, "tool_use: " + ran(t3)); tools++;
        add(4, P.next, "end_turn: not tool_use, so the loop ended and showed the text.");
        return Object.assign(out(SLOT, ["Best fit (exam answer)", "mint", "Exactly the guide's loop: continue on tool_use, terminate on end_turn. It ran three tools because Claude asked for three, and stopped when Claude was done."]), { calls: 4 });
      }
      const sees = P.text || NOTHING;
      add(3, t3, `${pick}: not tool_use, so the loop ended and showed the text.`);
      const V = {
        end_turn: ["Best fit (exam answer)", "mint", "Exactly the guide's loop: continue on tool_use, terminate on end_turn. Two tools ran, and the loop stopped when Claude said it was done."],
        stop_sequence: ["Also works", "mint", "Stopping is right here: the stop sequence is one your app set, and the text before it is what you wanted. The guide's loop gets this right without a special case."],
        max_tokens: ["Gap: shows a cut-off reply", "butter", "The exam answer is still this loop. In real code, “not tool_use” isn't always “finished”: max_tokens means the reply was cut off, so the customer gets half a sentence. (Beyond the exam guide.)"],
        pause_turn: ["Gap: stops mid-search", "butter", "The exam answer is still this loop. In real code, pause_turn means Claude paused a server-tool turn; stopping shows a progress line, not an answer. (Beyond the exam guide.)"],
        refusal: ["Gap: says nothing", "butter", "The exam answer is still this loop. In real code, a refusal deserves its own branch: tell the customer and route to a person, rather than sending an empty reply. (Beyond the exam guide.)"],
      }[pick];
      return Object.assign(out(sees, V), { calls: 3 });
    }

    if (loop === "words") {
      if (pick === "end_turn") {
        add(3, t3, "Found “Anything else”, so stopped and showed the text.");
        return Object.assign(out(ANSWER, ["Only usually works", "butter", "Right answer, for the wrong reason. Claude happened to write “Anything else”. Had it said “Hope that helps!”, the loop would have kept calling."]), { calls: 3 });
      }
      if (pick === "tool_use" || pick === "pause_turn") {
        if (pick === "tool_use") { add(3, t3, "No text at all. " + ran(t3)); tools++; }
        else add(3, t3, "No “Anything else” in the text, so called again. (Sending the response back happens to be right for pause_turn.)");
        add(4, P.next, "Found “Anything else”, so stopped and showed the text.");
        return Object.assign(out(P.next.text, ["Only usually works", "butter", "It got there because the last reply happened to contain the magic words. Wording varies; a loop that parses it stops early or runs on when it changes."]), { calls: 4 });
      }
      // max_tokens, stop_sequence, refusal: the phrase never appears, so it runs to the 10-call safety net.
      const did = {
        max_tokens: "No “Anything else” in the text, so called again with nothing changed.",
        stop_sequence: "No “Anything else” in the text, so called again with nothing changed.",
        refusal: "No text, so resent the same request.",
      }[pick];
      add(3, t3, did);
      turns.push({ n: "4–10", sr: pick, got: pick === "refusal" ? "the same refusal, 7 more times" : "the same reply, 7 more times", did: "Still no “Anything else”. Stopped only when the 10-call safety net ran out." });
      const V = {
        max_tokens: ["Breaks", "rose", "The cut-off reply never contains the phrase, so the loop burns 10 calls and then shows half a sentence."],
        stop_sequence: ["Runs on", "butter", "The answer was ready at turn 3. Because the stop sequence ended the reply before any closing line, the loop kept calling for 7 more turns."],
        refusal: ["Breaks", "rose", "It resent a refused request 7 times. A refusal won't change on a resend, and the customer still gets nothing."],
      }[pick];
      return Object.assign(out(pick === "refusal" ? NOTHING : P.text, V), { calls: 10 });
    }

    if (loop === "cap") {
      const did = pick === "tool_use" ? "Turn 3 of 3: the cap is reached. Stopped; get_delivery_slot never ran."
        : "Turn 3 of 3: the cap is reached. Stopped and showed the text.";
      add(3, t3, did);
      const sees = P.text || NOTHING;
      const V = {
        end_turn: ["Only usually works", "butter", "Worked only because this job took exactly 3 calls. A 2-call job would get an extra wasted call; a 4-call job gets cut off."],
        stop_sequence: ["Only usually works", "butter", "The text is right, but only because the job ended on turn 3. The cap knows nothing about why Claude stopped."],
        tool_use: ["Breaks", "rose", "Claude asked for one more tool and the loop walked away. The customer gets nothing. A cap is a safety net, not the main stop."],
        max_tokens: ["Breaks", "rose", "The cap stopped on turn 3 and showed whatever was there: half a sentence."],
        pause_turn: ["Breaks", "rose", "The cap stopped while Claude was mid-search. The customer gets a progress line instead of an answer."],
        refusal: ["Breaks", "rose", "The cap stopped and showed an empty reply. Nobody routed the customer anywhere."],
      }[pick];
      return Object.assign(out(sees, V), { calls: 3 });
    }
  }

  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
  const chipFor = (sr) => ({ tool_use: "peri", end_turn: "mint", refusal: "rose" }[sr] || "butter");
  let pick = "end_turn", loop = "tooluse", timer = null;

  function buttons(boxId, items, current, set, mono) {
    const box = $(boxId);
    box.innerHTML = "";
    Object.entries(items).forEach(([k, v]) => {
      const x = document.createElement("button");
      x.className = "btn" + (k === current ? " on" : "");
      x.textContent = v.label;
      if (mono) x.style.fontFamily = "ui-monospace, Menlo, monospace";
      x.onclick = () => { set(k); draw(); };
      box.appendChild(x);
    });
  }

  function highlight() {
    ["box-sr", "box-text", "box-words", "box-count"].forEach((id) => {
      const r = $(id);
      if (r) r.setAttribute("stroke-width", id === LOOPS[loop].where ? "4" : "1.5");
    });
  }

  function draw() {
    buttons("sim-p", PICKS, pick, (k) => { pick = k; }, true);
    buttons("sim-l", LOOPS, loop, (k) => { loop = k; });
    $("sim-pnote").textContent = PICKS[pick].note;
    highlight();
    run();
  }

  function run() {
    clearTimeout(timer);
    const o = play(pick, loop);
    const trail = $("sim-trail");
    trail.innerHTML = "";
    const els = o.turns.map((t) => {
      const d = document.createElement("div");
      d.className = "step";
      d.innerHTML = `<b>Turn ${t.n}</b> <span class="chip ${chipFor(t.sr)}" style="font-family:ui-monospace,Menlo,monospace">${t.sr}</span>` +
        `<div class="lbl">What Claude returned</div><pre>${esc(t.got)}</pre>` +
        `<div class="lbl">What your code did</div><div>${esc(t.did)}</div>`;
      trail.appendChild(d);
      return d;
    });
    if (o.skipped) {
      const d = document.createElement("div");
      d.className = "step skipped";
      d.textContent = o.skipped;
      trail.appendChild(d);
      els.push(d);
    }
    let i = 0;
    (function step() { if (i < els.length) { els[i++].classList.add("in"); timer = setTimeout(step, 200); } })();
    $("sim-sees").textContent = o.sees;
    $("sim-tally").innerHTML = `<span class="chip">API calls</span>${o.calls} <span class="chip" style="margin-left:10px">Tools run</span>${o.tools}`;
    $("sim-verdict").className = "box " + o.v[1];
    $("sim-verdict").innerHTML = `<span class="chip ${o.v[1]}">${o.v[0]}</span> ${esc(o.v[2])}`;
    $("sim-code").textContent = LOOPS[loop].code.join("\n");
  }

  window.StopSim = { play, PICKS, LOOPS };
  if (typeof document !== "undefined") window.addEventListener("DOMContentLoaded", draw);
})();
