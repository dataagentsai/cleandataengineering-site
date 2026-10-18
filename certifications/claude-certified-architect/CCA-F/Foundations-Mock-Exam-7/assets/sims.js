/* CCA-F Mock Exam #7 — scripted simulations ("consequence replay").
   Each sim keys on a question id from questions.js. For every option, and for every "world" (the
   question as written, plus a world where the deciding fact is changed), it holds a scripted trace of
   what the system does, an outcome, and a success rate used by "Run 20 chats".
   Traces are hand-written and deterministic: no API calls, no key, same result every time.

   Step lanes: cust (customer), loop (your agent code), api (Claude Messages API request/response),
   hook (SDK hook), tool (MCP tool), sub (subagent), block (a constraint that stops the change). */
(function () {
  var MODEL = 'claude-sonnet-5-5';
  function S(lane, title, note, payload, mark) { return { lane: lane, title: title, note: note || '', payload: payload, mark: mark || '' }; }
  function req(title, note, body, mark) { return S('api', title, note, Object.assign({ model: MODEL, max_tokens: 1024 }, body), mark); }
  function res(title, note, content, stop, mark) { return S('api', title, note, { role: 'assistant', content: content, stop_reason: stop }, mark); }
  var T = function (t) { return { type: 'text', text: t }; };
  var U = function (id, name, input) { return { type: 'tool_use', id: id, name: name, input: input }; };
  var R = function (id, content) { return { type: 'tool_result', tool_use_id: id, content: content }; };
  var E = function (id, content) { return { type: 'tool_result', tool_use_id: id, is_error: true, content: content }; };

  /* Shared helpers for the per-scenario files (sims-*.js). Each file calls SIMLIB.add(sim). */
  window.SIMS = window.SIMS || {};
  window.SIMLIB = { MODEL: MODEL, S: S, req: req, res: res, T: T, U: U, R: R, E: E,
    /* X(step, { meter: {...} }) or X(step, { table: {...} }) attaches a context bar or a numbers table to a step */
    X: function (step, extra) { return Object.assign(step, extra); },
    add: function (sim) { window.SIMS[sim.id] = sim; } };

  /* ------------------------------------------------------------ m7-s1-01 stop_reason */
  var custMsg = 'My box from last Tuesday was missing the salmon.';
  var tools1 = ['get_customer', 'lookup_order', 'process_refund', 'escalate_to_human', 'pause_subscription'];
  var textLoop = S('loop', 'Loop checks: does the response contain a text block?', 'This is the bug in the question: the loop ends the turn on any text.',
    'if any(b.type == "text" for b in resp.content):\n    end_turn()          # ← fires here\nelse:\n    run_tools(resp)');
  var bothBlocks = [T('Let me check that box.'), U('toolu_01', 'lookup_order', { box_id: 'BX-4471' })];

  function goodTail(id) {
    return [
      S('tool', 'lookup_order runs', 'The tool finally executes.', { input: { box_id: 'BX-4471' }, output: { box_id: 'BX-4471', delivered: '2026-09-29', missing_items: ['salmon fillet x2'], refundable: 12.5 } }),
      req('Loop sends the result back', 'The tool_result carries the same tool_use_id, so Claude can match it.', { messages: [{ role: 'user', content: custMsg }, { role: 'assistant', content: '[text + tool_use ' + id + ']' }, { role: 'user', content: [R(id, '{"missing_items":["salmon fillet x2"],"refundable":12.5}')] }] }),
      res('Claude answers', '', [T('Box BX-4471 shipped without the salmon. I can refund $12.50 now or send a replacement. Which would you like?')], 'end_turn'),
      S('loop', 'Loop reads stop_reason = "end_turn" → turn is over', '', 'stop_reason == "end_turn"  →  deliver reply, wait for customer', 'ok'),
      S('cust', 'Customer sees', '', 'Box BX-4471 shipped without the salmon. I can refund $12.50 now or send a replacement. Which would you like?', 'ok')
    ];
  }
  var stuck = [S('cust', 'Customer sees', 'Then nothing. The lookup never ran, so the answer never comes.', 'Let me check that box.\n\n… (waiting)', 'bad')];

  var s101 = {
    id: 'm7-s1-01', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Claude writes a short line <b>and</b> requests <code>lookup_order</code> in the same response.' },
      { id: 'B', label: 'Decider changed', desc: 'Claude answers in text <b>with no tool request</b>, guessing instead of looking the box up.' }
    ],
    runs: {
      A: [
        { steps: [S('cust', 'Customer writes', '', custMsg),
            req('Loop sends the first request with tool_choice "any"', 'Option A changes this line.', { tool_choice: { type: 'any' }, tools: tools1, messages: [{ role: 'user', content: custMsg }] }),
            res('Claude responds', 'With "any" Claude must call a tool, and it does. It was already doing that.', [U('toolu_01', 'lookup_order', { box_id: 'BX-4471' })], 'tool_use'),
            S('loop', 'Loop runs lookup_order', 'No text block this time, so the first turn works…', 'no text block → run_tools()'),
            req('Next request goes back to tool_choice "auto"', '', { tool_choice: { type: 'auto' }, messages: ['…', { role: 'user', content: [R('toolu_01', '{"refundable":12.5}')] }] }),
            res('Claude asks for a second tool', '', [T('I can refund that. One moment.'), U('toolu_02', 'process_refund', { box_id: 'BX-4471', amount: 12.5 })], 'tool_use'),
            textLoop].concat([S('cust', 'Customer sees', 'The refund request is dropped. The loop still ends on any text.', 'I can refund that. One moment.\n\n… (waiting)', 'bad')]),
          outcome: { ok: false, text: 'Forcing a tool only patched the first request. Claude was already asking for tools; the loop is what drops them. The next text-plus-tool response breaks the same way.' }, rate: 0.55 },
        { steps: [S('cust', 'Customer writes', '', custMsg), req('Loop sends the request', '', { tool_choice: { type: 'auto' }, tools: tools1, messages: [{ role: 'user', content: custMsg }] }),
            res('Claude responds with text and a tool request', '', bothBlocks, 'tool_use'), textLoop,
            S('loop', 'tool_result code never runs', 'Option B fixed how results are sent back, but no tool ran, so there is nothing to send.', 'append_tool_result(...)   # never reached', 'bad')].concat(stuck),
          outcome: { ok: false, text: 'Sending results back correctly is a later step. The loop ended before the tool ran.' }, rate: 0.3 },
        { steps: [S('cust', 'Customer writes', '', custMsg), req('Loop sends the request', '', { tool_choice: { type: 'auto' }, tools: tools1, messages: [{ role: 'user', content: custMsg }] }),
            res('Claude responds with text and a tool request', 'Look at stop_reason: Claude is saying "run this and come back".', bothBlocks, 'tool_use'),
            S('loop', 'Loop reads stop_reason = "tool_use" → run tools and continue', 'Option C: the loop reads the label, not the content.', 'if resp.stop_reason == "tool_use":\n    results = run_tools(resp)   # ← fires here\n    continue\nelif resp.stop_reason == "end_turn":\n    end_turn()', 'ok')
          ].concat(goodTail('toolu_01')),
          outcome: { ok: true, text: 'The loop follows the signal Claude sends with every response. Text next to a tool request no longer matters.' }, rate: 1 },
        { steps: [S('cust', 'Customer writes', '', custMsg), req('Loop sends the request', '', { tool_choice: { type: 'auto' }, tools: tools1, messages: [{ role: 'user', content: custMsg }] }),
            res('Claude responds with text and a tool request', 'This time Claude phrased it differently.', [T("I'll look into that box for you."), U('toolu_01', 'lookup_order', { box_id: 'BX-4471' })], 'tool_use'),
            S('loop', 'Loop matches the text against a phrase list', '"I\'ll look into" is not on the list, so the turn ends.', 'PENDING = ["let me check", "one moment", "checking"]\nif any(p in text.lower() for p in PENDING): continue\nelse: end_turn()      # ← fires here', 'bad'),
            S('cust', 'Customer sees', '', "I'll look into that box for you.\n\n… (waiting)", 'bad')],
          outcome: { ok: false, text: 'Matching phrases works only when Claude uses a listed phrase. The response already says why it stopped; guessing from the words is the anti-pattern.' }, rate: 0.7 }
      ],
      B: [
        { steps: [S('cust', 'Customer writes', '', custMsg),
            req('Loop sends the request with tool_choice "any"', '', { tool_choice: { type: 'any' }, tools: tools1, messages: [{ role: 'user', content: custMsg }] }),
            res('Claude must call a tool, so it looks the box up', 'With "any" the API leaves no room for a text-only guess.', [U('toolu_01', 'lookup_order', { box_id: 'BX-4471' })], 'tool_use'),
            S('loop', 'No text block → loop runs the tool', '', 'run_tools()', 'ok')].concat(goodTail('toolu_01')),
          outcome: { ok: true, text: 'Here the problem is that Claude does not ask for the tool. Requiring a tool call on that request fixes exactly that. This is the world where the runner-up wins.' }, rate: 1 },
        { steps: [S('cust', 'Customer writes', '', custMsg), req('Loop sends the request', '', { tool_choice: { type: 'auto' }, tools: tools1, messages: [{ role: 'user', content: custMsg }] }),
            res('Claude guesses in text', 'No tool request at all.', [T('Sorry about that! Missing items are usually refunded within 3 days.')], 'end_turn'),
            S('cust', 'Customer sees a guess', '', 'Sorry about that! Missing items are usually refunded within 3 days.', 'bad')],
          outcome: { ok: false, text: 'There is still no tool call, so there is no result to send back.' }, rate: 0.6 },
        { steps: [S('cust', 'Customer writes', '', custMsg), req('Loop sends the request', '', { tool_choice: { type: 'auto' }, tools: tools1, messages: [{ role: 'user', content: custMsg }] }),
            res('Claude guesses in text', '', [T('Sorry about that! Missing items are usually refunded within 3 days.')], 'end_turn'),
            S('loop', 'Loop reads stop_reason = "end_turn" → stop', 'The loop is now correct, and it correctly stops.', 'stop_reason == "end_turn" → end_turn()'),
            S('cust', 'Customer sees a guess', 'A correct loop plus a Claude that never asks for the tool still means no lookup.', 'Sorry about that! Missing items are usually refunded within 3 days.', 'bad')],
          outcome: { ok: false, text: 'A correct loop cannot run a tool Claude never requested. The fault moved to tool choice.' }, rate: 0.6 },
        { steps: [S('cust', 'Customer writes', '', custMsg), req('Loop sends the request', '', { tool_choice: { type: 'auto' }, tools: tools1, messages: [{ role: 'user', content: custMsg }] }),
            res('Claude guesses in text', '', [T('Sorry about that! Missing items are usually refunded within 3 days.')], 'end_turn'),
            S('loop', 'No pending phrase → end the turn', '', 'end_turn()'),
            S('cust', 'Customer sees a guess', '', 'Sorry about that! Missing items are usually refunded within 3 days.', 'bad')],
          outcome: { ok: false, text: 'Phrase matching cannot make Claude call a tool.' }, rate: 0.6 }
      ]
    }
  };

  /* ------------------------------------------------------------ m7-s1-04 PostToolUse hook */
  var card = '4111 1111 1111 1234';
  var ask = 'Which card did you charge? Read me the full number, I have two.';
  var custFull = { name: 'Asha Rao', plan: 'Family 4', card_number: card, boxes: ['BX-4471', 'BX-4502'] };
  var custMasked = { name: 'Asha Rao', plan: 'Family 4', card_number: '•••• •••• •••• 1234', boxes: ['BX-4471', 'BX-4502'] };
  function chat404(world, sys, hookStep, sees, reply, leak) {
    var st = [S('cust', world === 'A' ? 'Customer writes (chat 14 of 20)' : 'Customer writes', '', ask),
      req('Loop sends the request', sys ? 'The system prompt now carries the card rule.' : '', Object.assign({ tools: tools1, messages: [{ role: 'user', content: ask }] }, sys ? { system: sys } : {})),
      res('Claude asks for the customer record', '', [U('toolu_07', 'get_customer', { customer_id: 'C-2291' })], 'tool_use'),
      S('tool', 'get_customer returns the full record', 'The billing team owns this server and will not change it.', { output: custFull })];
    if (hookStep) st = st.concat(hookStep);
    st.push(S('api', 'What enters Claude\'s context', sees === 'masked' ? 'Claude never sees the real number.' : 'The full card number is now in the model\'s context.', { role: 'user', content: [R('toolu_07', JSON.stringify(sees === 'masked' ? custMasked : custFull))] }, sees === 'masked' ? 'ok' : 'warn'));
    st.push(res('Claude replies', '', [T(reply)], 'end_turn'));
    st.push(S('cust', 'Customer sees', leak ? 'The card number reached the customer.' : '', reply, leak ? 'bad' : 'ok'));
    return st;
  }
  var sysRule = 'Refer to payment cards by their last four digits only.\nExample: "The card ending 1234 was charged."\nExample: "I can see a Visa ending 1234 on file."';
  var s104 = {
    id: 'm7-s1-04', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Security: a card number <b>must not</b> reach a customer in any chat. The server cannot change.' },
      { id: 'B', label: 'Decider changed', desc: 'Style goal only: replies <b>should usually</b> say "card ending 1234". Nothing is breached by a rare miss.' }
    ],
    runs: {
      A: [
        { steps: chat404('A', sysRule, null, 'full', 'Of course. The charge went to card ' + card + '.', true),
          outcome: { ok: false, text: 'The rule and examples work in most chats. A must-never cannot rest on "most": the number is in Claude\'s context, and a customer who pushes can get it read back.' }, rate: 0.95 },
        { steps: chat404('A', null, [S('hook', 'PostToolUse hook masks card_number', 'Runs in your code, every time, before Claude reads the result.', 'def mask_card(result):\n    result["card_number"] = "•••• •••• •••• " + result["card_number"][-4:]\n    return result', 'ok')],
            'masked', 'For security I can only see the last four digits: the charge went to the card ending 1234.', false),
          outcome: { ok: true, text: 'Claude cannot repeat a number it never had. Hooks are deterministic, and this one needs no change to the billing team\'s server.' }, rate: 1 },
        { steps: chat404('A', null, [S('hook', 'PostToolUse hook logs the card number', 'Right hook, wrong action: it records, it does not change the result.', { alert: 'card_number seen in get_customer result', chat: 'CH-8812', forwarded_to_model: 'unchanged' }, 'warn')],
            'full', 'Of course. The charge went to card ' + card + '.', true),
          outcome: { ok: false, text: 'Security now gets a log entry after the leak. The number still reached Claude, and then the customer.' }, rate: 0.9 },
        { steps: [S('cust', 'Customer writes (chat 14 of 20)', '', ask),
            res('Coordinator delegates to the billing subagent', '', [U('toolu_09', 'Task', { subagent: 'billing-reader', prompt: 'Get this customer\'s record. The customer asks which card was charged.' })], 'tool_use'),
            S('sub', 'Subagent calls get_customer and sees the full record', 'Its definition says "return only name, plan and box IDs". That is an instruction, not a filter.', { output: custFull }, 'warn'),
            S('sub', 'Subagent returns its summary', 'The coordinator asked about the card, so the subagent was "helpful".', 'Asha Rao, plan Family 4, boxes BX-4471 and BX-4502. Charged card: ' + card + '.', 'bad'),
            res('Coordinator replies', '', [T('The charge went to card ' + card + '.')], 'end_turn'),
            S('cust', 'Customer sees', 'The number reached the customer.', 'The charge went to card ' + card + '.', 'bad')],
          outcome: { ok: false, text: 'The subagent still receives the full number and decides what to pass on. Moving the decision to another model is still a prompt, not a guarantee.' }, rate: 0.93 }
      ],
      B: [
        { steps: chat404('B', sysRule, null, 'full', 'The charge went to the card ending 1234.', false),
          outcome: { ok: true, text: 'For a "should usually" phrasing rule, a clear prompt rule with examples is the right tool. A rare miss is acceptable here, so this is the world where the runner-up wins.' }, rate: 0.95 },
        { steps: chat404('B', null, [S('hook', 'PostToolUse hook masks card_number', '', 'mask_card(result)', 'ok')], 'masked', 'The charge went to the card ending 1234.', false),
          outcome: { ok: true, warn: true, text: 'This works, but it is heavier than the goal needs. A hook can mask data; it cannot teach Claude a phrasing style for everything else it says.' }, rate: 1 },
        { steps: chat404('B', null, [S('hook', 'PostToolUse hook logs the card number', '', { alert: 'card_number seen', forwarded_to_model: 'unchanged' }, 'warn')], 'full', 'Of course. The charge went to card ' + card + '.', true),
          outcome: { ok: false, text: 'Logging does not change what Claude says.' }, rate: 0.85 },
        { steps: [S('cust', 'Customer writes', '', ask), S('sub', 'Billing subagent reads and summarises the record', '', 'Asha Rao, plan Family 4, boxes BX-4471 and BX-4502.'), res('Coordinator replies', '', [T('I can see a card on file, but not which one. Let me escalate that.')], 'end_turn'),
            S('cust', 'Customer sees', 'An extra agent just to shape one phrase, and the customer\'s question goes unanswered.', 'I can see a card on file, but not which one. Let me escalate that.', 'warn')],
          outcome: { ok: false, text: 'An extra agent for a phrasing rule, and the agent can no longer answer "which card?".' }, rate: 0.9 }
      ]
    }
  };

  /* ------------------------------------------------------------ m7-s1-05 tool_choice any */
  var recTools = ['record_resolved', 'record_escalated', 'record_abandoned'];
  var wrap = 'Chat is over. Log the outcome.';
  var s105 = {
    id: 'm7-s1-05', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Three record tools feed three queues another team owns. They <b>cannot be merged</b>. Claude picks well when it calls one.' },
      { id: 'B', label: 'Decider changed', desc: 'There is <b>one</b> <code>record_outcome</code> tool, and the wrap-up request also carries all the chat tools.' }
    ],
    runs: {
      A: [
        { steps: [S('loop', 'You propose merging into record_outcome and forcing it', '', { tool_choice: { type: 'tool', name: 'record_outcome' }, tools: ['record_outcome(outcome: enum)'] }),
            S('block', 'Blocked: the three tools feed three queues owned by the Ops team', 'Their consumers read record_resolved / record_escalated / record_abandoned. A merged tool has nowhere to go.', 'queue.resolved  ← record_resolved\nqueue.escalated ← record_escalated\nqueue.abandoned ← record_abandoned', 'bad')],
          outcome: { ok: false, text: 'Forcing one named tool is the cleanest guarantee when one tool fits. Here it is not available: the question says the tools cannot be merged.' }, rate: 0 },
        { steps: [req('Wrap-up request, tool_choice "auto", richer descriptions', '', { tool_choice: { type: 'auto' }, tools: [{ name: 'record_resolved', description: 'Use when the customer\'s issue was fixed in this chat. Example: refund issued.' }, '…'], messages: ['…chat…', { role: 'user', content: wrap }] }),
            res('Claude writes a summary instead', '"auto" lets Claude answer in text. Better descriptions improve which tool, not whether.', [T('Summary: customer reported missing salmon; refunded $12.50. Resolved.')], 'end_turn'),
            S('tool', 'Nothing is logged', 'No tool call, so no queue receives the outcome.', 'queue.resolved: (empty)', 'bad')],
          outcome: { ok: false, text: 'Selection already worked. The failure is Claude replying in text, and "auto" still allows that.' }, rate: 0.85 },
        { steps: [req('Wrap-up request, tool_choice "auto"', '', { tool_choice: { type: 'auto' }, tools: recTools, messages: ['…chat…', { role: 'user', content: wrap }] }),
            res('Claude writes a summary', '', [T('Summary: refunded $12.50. Resolved.')], 'end_turn'),
            S('loop', 'Loop sees "end_turn" and resends with a reminder', 'A second, paid request.', 'if stop_reason == "end_turn":\n    resend(wrap + " You must call a record tool.")', 'warn'),
            res('Claude calls the tool on the retry', '', [U('toolu_11', 'record_resolved', { chat_id: 'CH-8812', note: 'refund $12.50' })], 'tool_use'),
            S('tool', 'record_resolved queues the outcome', '', { queued: 'queue.resolved', chat_id: 'CH-8812' }, 'ok')],
          outcome: { ok: true, warn: true, text: 'It usually works, at the cost of extra calls, and it can still miss twice. The API can require a tool call in the first place.' }, rate: 0.97 },
        { steps: [req('Wrap-up request only: tool_choice "any"', 'The chat itself keeps "auto".', { tool_choice: { type: 'any' }, tools: recTools, messages: ['…chat…', { role: 'user', content: wrap }] }),
            res('Claude must call a tool, and still chooses which', '', [U('toolu_11', 'record_resolved', { chat_id: 'CH-8812', note: 'refund $12.50' })], 'tool_use'),
            S('tool', 'record_resolved queues the outcome', '', { queued: 'queue.resolved', chat_id: 'CH-8812' }, 'ok')],
          outcome: { ok: true, text: '"any" removes the text option and keeps Claude\'s choice, which was already right. One request, every time.' }, rate: 1 }
      ],
      B: [
        { steps: [req('Wrap-up request: tool_choice forces record_outcome', '', { tool_choice: { type: 'tool', name: 'record_outcome' }, tools: ['record_outcome', 'get_customer', 'lookup_order', '…'], messages: ['…chat…', { role: 'user', content: wrap }] }),
            res('Claude calls record_outcome', 'Forced by name: no text, no other tool.', [U('toolu_12', 'record_outcome', { chat_id: 'CH-8812', outcome: 'resolved' })], 'tool_use'),
            S('tool', 'Outcome logged', '', { queued: 'queue.outcomes', outcome: 'resolved' }, 'ok')],
          outcome: { ok: true, text: 'One tool is always right, so name it. This is the world where the runner-up wins.' }, rate: 1 },
        { steps: [req('Wrap-up request, tool_choice "auto"', '', { tool_choice: { type: 'auto' }, tools: ['record_outcome', 'get_customer', '…'], messages: ['…', { role: 'user', content: wrap }] }),
            res('Claude writes a summary', '', [T('Summary: resolved.')], 'end_turn'), S('tool', 'Nothing logged', '', '(empty)', 'bad')],
          outcome: { ok: false, text: '"auto" still allows a text reply.' }, rate: 0.85 },
        { steps: [req('Wrap-up request, tool_choice "auto"', '', { tool_choice: { type: 'auto' }, tools: ['record_outcome', '…'], messages: ['…', { role: 'user', content: wrap }] }),
            res('Claude writes a summary', '', [T('Summary: resolved.')], 'end_turn'), S('loop', 'Resend with a reminder', '', 'resend(...)', 'warn'),
            res('Claude calls record_outcome', '', [U('toolu_12', 'record_outcome', { outcome: 'resolved' })], 'tool_use'), S('tool', 'Outcome logged', '', { outcome: 'resolved' }, 'ok')],
          outcome: { ok: true, warn: true, text: 'Works with extra calls. Forcing the tool needs none.' }, rate: 0.97 },
        { steps: [req('Wrap-up request: tool_choice "any"', '', { tool_choice: { type: 'any' }, tools: ['record_outcome', 'get_customer', 'lookup_order', '…'], messages: ['…', { role: 'user', content: wrap }] }),
            res('Claude calls a tool, but not the record tool', '"any" means any tool. Claude double-checks the order first.', [U('toolu_13', 'lookup_order', { box_id: 'BX-4471' })], 'tool_use'),
            S('tool', 'No outcome logged on this request', 'The request was meant to log, and it looked something up.', 'queue.outcomes: (empty)', 'bad')],
          outcome: { ok: false, text: 'With other tools present, "any" can pick one of them. When one specific tool must run, force it by name.' }, rate: 0.8 }
      ]
    }
  };

  [s101, s104, s105].forEach(window.SIMLIB.add);
})();
