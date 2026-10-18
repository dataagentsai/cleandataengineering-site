/* CCA-F Mock Exam #7 — scripted simulations for m7-s1-08, m7-s1-09, m7-s4-02, m7-s4-04.
   Uses the helpers in sims.js (window.SIMLIB). Hand-written, deterministic traces. */
(function () {
  var L = window.SIMLIB, S = L.S, req = L.req, res = L.res, T = L.T, U = L.U, R = L.R, E = L.E;
  var tools1 = ['get_customer', 'lookup_order', 'process_refund', 'escalate_to_human', 'pause_subscription'];

  /* ------------------------------------------------------------ m7-s1-08 explicit request for a human */
  var askPerson = 'My salmon was missing again. I want to speak to a real person.';
  var frustrated = 'My salmon was missing again. Honestly, this is getting ridiculous.';
  var session = 'Session: customer C-2291 (Asha Rao), latest box BX-4471. Refund limit $150 per box.';
  var handoff = { customer_id: 'C-2291', box_id: 'BX-4471', missing_item: 'salmon fillet x2', reason: 'Customer asked for a person', refund_if_wanted: 12.5, note: 'Second missing-salmon report. Customer calm.' };
  var lookupOut = { box_id: 'BX-4471', delivered: '2026-09-29', missing_items: ['salmon fillet x2'], refundable: 12.5 };
  var historyOut = { customer_id: 'C-2291', refunds: [{ box_id: 'BX-4402', item: 'spinach', amount: 4.0, date: '2026-08-18' }], note: 'Earlier salmon miss was fixed with a replacement box, not a refund.' };
  var offer = 'Sorry your salmon was missing again. I can refund $12.50 for box BX-4471 right now. Shall I do that?';

  function open808(msg, sys) {
    return [S('cust', 'Customer writes', '', msg),
      req('Loop sends the request', sys ? 'The system prompt carries the escalation rule for this option.' : '', { system: session + (sys ? '\n' + sys : ''), tools: tools1, messages: [{ role: 'user', content: msg }] })];
  }
  function escalateRun(msg) {
    return open808(msg, 'If the customer explicitly asks for a person, call escalate_to_human at once with the facts.').concat([
      res('Claude escalates in the same turn', 'No investigation and no counter-offer. The facts go in the handoff.', [T('Of course. I\'m connecting you with a member of our team now.'), U('toolu_21', 'escalate_to_human', handoff)], 'tool_use', 'ok'),
      S('tool', 'escalate_to_human opens a ticket', 'The person who picks it up sees the box and the item, so nobody re-asks.', { input: handoff, output: { ticket: 'HT-5530', queue: 'support-l2', eta_minutes: 4 } }),
      req('Loop sends the result back', '', { messages: ['…', { role: 'user', content: [R('toolu_21', '{"ticket":"HT-5530","eta_minutes":4}')] }] }),
      res('Claude confirms', '', [T('You\'re in the queue (ticket HT-5530). Someone will join in about 4 minutes and already has your box details.')], 'end_turn'),
      S('cust', 'Customer sees', '', 'You\'re in the queue (ticket HT-5530). Someone will join in about 4 minutes and already has your box details.', 'ok')]);
  }
  function offerRun(msg, sys) {
    return open808(msg, sys).concat([res('Claude offers the refund first', '', [T(offer)], 'end_turn')]);
  }
  function lookupSteps(msg) {
    return open808(msg, 'Before refunding or escalating, confirm the missing item with lookup_order.').concat([
      res('Claude looks the box up first', '', [U('toolu_22', 'lookup_order', { box_id: 'BX-4471' })], 'tool_use'),
      S('tool', 'lookup_order confirms the missing salmon', '', { input: { box_id: 'BX-4471' }, output: lookupOut }),
      res('Claude now decides: the item is confirmed and in limit, so it offers the refund', '', [T('I\'ve confirmed box BX-4471 was missing 2 salmon fillets. I can refund $12.50 now.')], 'end_turn')]);
  }
  function historySteps(msg) {
    return open808(msg, 'Check refund history. Escalate only if the same item went missing on an earlier box.').concat([
      res('Claude checks the refund history', '', [U('toolu_23', 'get_customer', { customer_id: 'C-2291', include: ['refund_history'] })], 'tool_use'),
      S('tool', 'get_customer returns past refunds', 'The earlier salmon miss was replaced, so it is not in the refund list.', { output: historyOut }),
      res('No earlier salmon refund, so the rule says: do not escalate', '', [T(offer)], 'end_turn')]);
  }

  var s108 = {
    id: 'm7-s1-08', who: 'Customer', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'The customer <b>explicitly asks for a real person</b>, even though the agent could refund the box itself.' },
      { id: 'B', label: 'Decider changed', desc: 'The customer is frustrated but <b>does not ask for a person</b>; the $12.50 refund is well inside the limit.' }
    ],
    runs: {
      A: [
        { steps: offerRun(askPerson, 'Acknowledge, offer an in-limit fix first, and escalate if the customer asks for a person again.').concat([
            S('cust', 'Customer has to ask twice', 'The request was already clear. The agent made the customer repeat it.', 'No, I said I want to speak to a real person.', 'bad'),
            res('Claude escalates on the second ask', '', [U('toolu_21', 'escalate_to_human', handoff)], 'tool_use')]),
          outcome: { ok: false, text: 'Offering a fix first suits a customer who has not asked for a person. This one asked plainly, so the counter-offer only made them ask again.' }, rate: 0.15 },
        { steps: lookupSteps(askPerson).concat([
            S('cust', 'Customer sees', 'The lookup proved nothing the request needed. The person is still not on the way.', 'I\'ve confirmed box BX-4471 was missing 2 salmon fillets. I can refund $12.50 now.', 'bad')]),
          outcome: { ok: false, text: 'The customer asked for a person, and checking the order does not change that. It only delays the handoff, and here the agent talked itself into refunding instead.' }, rate: 0.3 },
        { steps: historySteps(askPerson).concat([
            S('cust', 'Customer sees', 'The request for a person was overruled by a refund list.', offer, 'bad')]),
          outcome: { ok: false, text: 'The history decided whether a person was called, and the history said no. A request for a person is a trigger on its own; it does not depend on past refunds.' }, rate: 0.35 },
        { steps: escalateRun(askPerson),
          outcome: { ok: true, text: 'An explicit request for a person is enough on its own. The agent escalates at once and hands over the box and item, so nobody has to ask again.' }, rate: 0.96 }
      ],
      B: [
        { steps: offerRun(frustrated, 'Acknowledge, offer an in-limit fix first, and escalate if the customer asks for a person.').concat([
            S('cust', 'Customer accepts', '', 'Yes please.'),
            res('Claude issues the refund', '', [U('toolu_24', 'process_refund', { box_id: 'BX-4471', amount: 12.5 })], 'tool_use'),
            S('tool', 'process_refund succeeds', '', { output: { refund_id: 'RF-7781', amount: 12.5, status: 'issued' } }, 'ok'),
            S('cust', 'Customer sees', 'Settled in one chat, no queue.', 'Done: $12.50 is on its way back to your card (RF-7781).', 'ok')]),
          outcome: { ok: true, text: 'Nobody asked for a person, and the fix is simple and inside the limit. Offering it first is right here, so this is the world where the runner-up wins.' }, rate: 0.95 },
        { steps: lookupSteps(frustrated).concat([
            S('cust', 'Customer sees', 'It gets there, one tool call later than needed.', 'I\'ve confirmed box BX-4471 was missing 2 salmon fillets. I can refund $12.50 now.', 'warn')]),
          outcome: { ok: true, warn: true, text: 'This ends in the right offer. The extra lookup is a small delay, not a wrong decision, when nobody asked for a person.' }, rate: 0.95 },
        { steps: historySteps(frustrated).concat([
            S('cust', 'Customer sees', 'Right result, but only because the history happened to say no.', offer, 'warn')]),
          outcome: { ok: true, warn: true, text: 'The offer is right, but it hung on the refund history. With a matching earlier refund, this rule would send a simple $12.50 case to a human.' }, rate: 0.9 },
        { steps: escalateRun(frustrated).map(function (st, i) { return i === 2 ? res('Claude escalates anyway', 'Nobody asked for a person, and the agent could settle this alone.', st.payload.content, 'tool_use', 'warn') : st; }),
          outcome: { ok: false, text: 'Here no one asked for a person. Escalating a simple in-limit refund makes the customer wait in a queue for something the agent could do now.' }, rate: 0.4 }
      ]
    }
  };

  /* ------------------------------------------------------------ m7-s1-09 access failure vs empty result */
  var custRefund = 'Box BX-4471 was missing the salmon. Can I get a refund?';
  var query = { customer_id: 'C-2291', since: '2026-01-01', pages: 'newest first' };
  var page1 = [{ box_id: 'BX-4471', amount: 12.5, date: '2026-09-30', reason: 'salmon missing', channel: 'phone' }];
  function open809() {
    return [S('cust', 'Customer writes', '', custRefund),
      res('Coordinator delegates the eligibility check', '', [U('toolu_31', 'Task', { subagent: 'policy-checker', prompt: 'Is C-2291 eligible for a $12.50 refund on BX-4471? Check past refunds.' })], 'tool_use')];
  }
  function apiCall(note, out, mark) { return S('tool', 'get_refund_history', note, { input: query, output: out }, mark); }
  var timeoutP2 = { page_1: page1, page_2: 'ERROR: payments API timed out after 10s' };
  var timeoutP1 = { page_1: 'ERROR: payments API timed out after 10s' };
  var structured = { status: 'lookup_failed', failure: 'timeout', source: 'payments API', query: query, partial_results: page1, missing: 'refunds before 2026-07-01' };
  function coordHolds(note, mark) {
    return [res('Coordinator sees BX-4471 was already refunded', note, [T('I can see box BX-4471 was already refunded $12.50 on 30 September, by phone. That refund should reach your card within 3 days.')], 'end_turn', mark),
      S('cust', 'Customer sees', '', 'I can see box BX-4471 was already refunded $12.50 on 30 September, by phone. That refund should reach your card within 3 days.', 'ok')];
  }

  var s109 = {
    id: 'm7-s1-09', who: 'Customer', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Payments API outages <b>usually last about an hour</b>; a timeout used to come back as "No previous refunds found."' },
      { id: 'B', label: 'Decider changed', desc: 'Payments API timeouts are <b>brief blips</b>: a retry a second later almost always works.' }
    ],
    runs: {
      A: [
        { steps: open809().concat([
            apiCall('The outage started 20 minutes ago.', timeoutP2),
            S('sub', 'Subagent retries with backoff: 1s, 4s, 16s', 'All three retries land inside the hour-long outage.', 'for wait in [1, 4, 16]:\n    sleep(wait); r = get_refund_history(q)   # timeout x3\nreturn "history unavailable"', 'warn'),
            S('sub', 'Subagent returns a bare status', 'Page 1 had already shown the 30 Sep refund. The bare status throws that away.', 'history unavailable', 'bad'),
            res('Coordinator cannot decide, so it escalates with nothing to go on', '', [U('toolu_32', 'escalate_to_human', { customer_id: 'C-2291', reason: 'refund history unavailable' })], 'tool_use'),
            S('cust', 'Customer sees', 'The answer was already in hand: BX-4471 was refunded on 30 Sep.', 'I can\'t check your past refunds right now, so I\'ve passed this to a colleague.', 'warn')]),
          outcome: { ok: false, text: 'An hour-long outage outlasts the retries. Then "unavailable" hides what was tried and the refund page 1 had already found, so the coordinator cannot act.' }, rate: 0.4 },
        { steps: open809().concat([
            apiCall('Page 1 arrives, page 2 times out.', timeoutP2),
            S('sub', 'Subagent reports a failed lookup with context', 'Failure type, the query it ran and what it did get.', structured, 'ok'),
            S('api', 'Coordinator receives the Task result', 'A failure no longer looks like "nothing found".', { role: 'user', content: [R('toolu_31', JSON.stringify(structured))] })
          ]).concat(coordHolds('The partial result settles it: no duplicate refund.', 'ok')),
          outcome: { ok: true, text: 'The report says the lookup failed, what it asked and what came back. The coordinator spots the earlier refund now, instead of waiting out an hour-long outage.' }, rate: 0.97 },
        { steps: open809().concat([
            apiCall('Page 1 arrives, page 2 times out.', timeoutP2),
            S('sub', 'Subagent returns isError, category transient', 'Failure is now separate from empty. The query and page 1 are dropped.', E('toolu_31', [{ type: 'text', text: JSON.stringify({ errorCategory: 'transient', isRetryable: true }) }]), 'warn'),
            S('loop', 'Coordinator reruns the subagent 5 minutes later', 'The outage lasts about an hour.', 'sleep(300); rerun("policy-checker")   # timeout again', 'bad'),
            S('cust', 'Customer sees', 'The earlier refund page 1 found is gone.', 'Our payments system is busy. Please try again later.', 'bad')]),
          outcome: { ok: false, text: 'This is half the fix: it no longer says "nothing found". But "try later" means an hour here, and the coordinator never sees the refund already retrieved.' }, rate: 0.45 },
        { steps: [S('cust', 'Customer writes', '', custRefund),
            res('Coordinator calls the payments API itself', 'Same wrapper, same reporting.', [U('toolu_33', 'get_refund_history', query)], 'tool_use'),
            S('tool', 'get_refund_history times out, wrapper returns an empty list', 'Moving the call did not change how a timeout is reported.', { input: query, output: { refunds: [] } }, 'bad'),
            res('Coordinator approves a repeat refund', '', [U('toolu_34', 'process_refund', { box_id: 'BX-4471', amount: 12.5 })], 'tool_use', 'bad'),
            S('cust', 'Customer sees', 'BX-4471 is now refunded twice.', 'Done: $12.50 is on its way back to your card.', 'bad')],
          outcome: { ok: false, text: 'The coordinator gets the same "empty" answer the subagent did. The problem was the report, not who makes the call.' }, rate: 0.3 }
      ],
      B: [
        { steps: open809().concat([
            apiCall('A 2-second blip on the first try.', timeoutP1),
            S('sub', 'Subagent retries after 1s and the call succeeds', 'Local recovery handles the blip.', 'sleep(1); r = get_refund_history(q)   # ok', 'ok'),
            S('sub', 'Subagent returns the full history', '', { status: 'ok', refunds: page1 })
          ]).concat(coordHolds('Full history, no duplicate refund.', 'ok')),
          outcome: { ok: true, text: 'When timeouts are brief, a quick local retry gets the real answer and the coordinator never sees the blip. This is the world where the runner-up wins.' }, rate: 0.98 },
        { steps: open809().concat([
            apiCall('A 2-second blip on the first page.', timeoutP1),
            S('sub', 'Subagent reports a failed lookup with no partial results', 'Correct, but a one-second retry would have succeeded.', { status: 'lookup_failed', failure: 'timeout', query: query, partial_results: [] }, 'warn'),
            S('loop', 'Coordinator holds the refund and delegates again', 'A second subagent run for a blip.', 'rerun("policy-checker")   # succeeds')
          ]).concat(coordHolds('Right answer, one extra round trip.', '')),
          outcome: { ok: true, warn: true, text: 'The report is honest, so nothing goes wrong. For a brief blip it costs a whole extra subagent run that a local retry would have avoided.' }, rate: 0.97 },
        { steps: open809().concat([
            apiCall('A 2-second blip.', timeoutP1),
            S('sub', 'Subagent returns isError, category transient', '', E('toolu_31', [{ type: 'text', text: JSON.stringify({ errorCategory: 'transient', isRetryable: true }) }]), 'warn'),
            S('loop', 'Coordinator reruns the subagent', 'The blip is over, so the rerun works.', 'rerun("policy-checker")   # ok')
          ]).concat(coordHolds('Right answer after a full rerun.', '')),
          outcome: { ok: true, warn: true, text: 'With brief blips the rerun works. It is heavier than retrying the one call inside the subagent.' }, rate: 0.95 },
        { steps: [S('cust', 'Customer writes', '', custRefund),
            res('Coordinator calls the payments API itself', '', [U('toolu_33', 'get_refund_history', query)], 'tool_use'),
            S('tool', 'A blip: the wrapper returns an empty list', '', { input: query, output: { refunds: [] } }, 'bad'),
            res('Coordinator approves a repeat refund', '', [U('toolu_34', 'process_refund', { box_id: 'BX-4471', amount: 12.5 })], 'tool_use', 'bad')],
          outcome: { ok: false, text: 'Even a short blip still turns into "no refunds" when the timeout is reported as empty.' }, rate: 0.6 }
      ]
    }
  };

  /* ------------------------------------------------------------ m7-s4-02 structured MCP errors */
  var engAsk = 'The fix for ENG-412 is merged. Move it to Done.';
  var moveIn = { issue_id: 'ENG-412', state: 'Done' };
  var ruleReason = 'Workflow rule: an issue needs a reviewer before it can move to Done. ENG-412 has no reviewer.';
  function open402(serverNote, serverCode) {
    return [S('cust', 'Engineer asks', '', engAsk),
      res('Claude calls move_issue', '', [U('toolu_41', 'move_issue', moveIn)], 'tool_use'),
      S('tool', 'Linear MCP server: move_issue', serverNote, serverCode)];
  }
  function retryLoop(content, note) {
    return S('api', 'Claude retries move_issue three more times', note, { attempts: [2, 3, 4], each_result: content }, 'bad');
  }

  var s402 = {
    id: 'm7-s4-02', who: 'Engineer', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'move_issue fails on timeouts <b>and on workflow rules</b>, such as closing an issue with no reviewer.' },
      { id: 'B', label: 'Decider changed', desc: 'The team has no workflow rules on moves, so <b>every failure is a Linear timeout</b>.' }
    ],
    runs: {
      A: [
        { steps: open402('The server sorts failures before returning them.', 'except LinearTimeout:\n    return error("transient", retryable=True, reason="Linear API timed out")\nexcept WorkflowRejected as e:\n    return error("business", retryable=False, reason=e.rule_message)').concat([
            S('api', 'Claude receives a structured error', 'Category and retryable flag answer "retry or stop?".', { role: 'user', content: [E('toolu_41', [{ type: 'text', text: JSON.stringify({ errorCategory: 'business', isRetryable: false, reason: ruleReason }) }])] }, 'ok'),
            res('Claude stops and explains', 'No retry: the flag says it cannot help.', [T('I couldn\'t move ENG-412 to Done: your workflow needs a reviewer first, and it has none. Want me to assign one?')], 'end_turn'),
            S('cust', 'Engineer sees', '', 'I couldn\'t move ENG-412 to Done: your workflow needs a reviewer first, and it has none. Want me to assign one?', 'ok')]),
          outcome: { ok: true, text: 'The error says what kind it is and whether retrying helps. Claude retries timeouts and explains rule rejections, so nothing is retried in vain.' }, rate: 1 },
        { steps: open402('Timeouts are retried inside the server. A rule rejection is not a timeout, so it goes straight back.', 'except LinearTimeout: retry_with_backoff()\nexcept Exception:\n    return error("Operation failed")').concat([
            S('api', 'Claude receives the rule rejection', 'Still no category and no reason.', { role: 'user', content: [E('toolu_41', 'Operation failed')] }, 'warn'),
            retryLoop('Operation failed', 'Claude cannot tell a rule from a timeout, so it keeps trying.'),
            res('Claude gives up without a reason', '', [T('I tried several times but couldn\'t move ENG-412. The Linear server just says "Operation failed".')], 'end_turn'),
            S('cust', 'Engineer sees', 'The missing reviewer is never mentioned.', 'I tried several times but couldn\'t move ENG-412. The Linear server just says "Operation failed".', 'bad')]),
          outcome: { ok: false, text: 'Server-side retries fix the timeouts. The workflow rejections still say only "Operation failed", so Claude retries a move that can never succeed.' }, rate: 0.6 },
        { steps: open402('The status code is added to the same text.', 'return error("Operation failed (HTTP " + resp.status + ")")').concat([
            S('api', 'Claude receives the error', '422 hints at a problem, but not which rule or whether to retry.', { role: 'user', content: [E('toolu_41', 'Operation failed (HTTP 422)')] }, 'warn'),
            retryLoop('Operation failed (HTTP 422)', 'Claude guesses the 422 might be a passing glitch.'),
            res('Claude guesses at the cause', '', [T('Linear rejected the move with HTTP 422. Maybe a field is invalid? I\'m not sure which.')], 'end_turn'),
            S('cust', 'Engineer sees', 'A clue, not a reason.', 'Linear rejected the move with HTTP 422. Maybe a field is invalid? I\'m not sure which.', 'bad')]),
          outcome: { ok: false, text: 'A status code is closer, but it does not say retry or stop, nor which workflow rule blocked the move.' }, rate: 0.65 },
        { steps: open402('Blocked moves come back as a normal result.', 'except WorkflowRejected as e:\n    return success("Move blocked: " + e.rule_message)').concat([
            S('api', 'Claude receives a success result', 'No is_error flag on a failure.', { role: 'user', content: [R('toolu_41', 'Move blocked: ' + ruleReason)] }, 'warn'),
            S('loop', 'Script logs the action as done', 'The script\'s error handling only looks at is_error.', 'if not block.is_error:\n    actions_done.append(("move_issue", "ENG-412"))   # ← fires here', 'bad'),
            S('cust', 'Engineer sees the run summary', 'The summary trusts the success flag.', 'Actions completed: moved ENG-412 to Done.', 'bad')]),
          outcome: { ok: false, text: 'A rule rejection is a failure. Sent as success, it slips past every check that looks at the error flag.' }, rate: 0.5 }
      ],
      B: [
        { steps: open402('Every failure here is a timeout.', 'return error("transient", retryable=True, reason="Linear API timed out")').concat([
            S('api', 'Claude receives a structured transient error', '', { role: 'user', content: [E('toolu_41', [{ type: 'text', text: JSON.stringify({ errorCategory: 'transient', isRetryable: true, reason: 'Linear API timed out' }) }])] }, 'warn'),
            res('Claude retries', 'An extra model turn for something the server could retry itself.', [U('toolu_42', 'move_issue', moveIn)], 'tool_use'),
            S('tool', 'move_issue succeeds', '', { output: { issue_id: 'ENG-412', state: 'Done' } }, 'ok')]),
          outcome: { ok: true, warn: true, text: 'It works, but every timeout costs a model turn. With only one kind of failure, the category adds little.' }, rate: 1 },
        { steps: open402('Timeouts are retried inside the server with backoff.', 'for wait in [0.5, 1, 2]:\n    try: return success(linear.move(issue, state))\n    except LinearTimeout: sleep(wait)').concat([
            S('tool', 'Second attempt succeeds', 'The timeout never reaches Claude.', { attempt: 2, output: { issue_id: 'ENG-412', state: 'Done' } }, 'ok'),
            S('api', 'Claude receives a success result', '', { role: 'user', content: [R('toolu_41', '{"issue_id":"ENG-412","state":"Done"}')] }),
            res('Claude confirms', '', [T('ENG-412 is now Done.')], 'end_turn'),
            S('cust', 'Engineer sees', '', 'ENG-412 is now Done.', 'ok')]),
          outcome: { ok: true, text: 'When every failure is a timeout, retrying inside the server is enough, and Claude never has to handle it. This is the world where the runner-up wins.' }, rate: 1 },
        { steps: open402('Every failure here is a timeout.', 'return error("Operation failed (HTTP 504)")').concat([
            S('api', 'Claude receives the error', '504 reads as a timeout; retrying is right.', { role: 'user', content: [E('toolu_41', 'Operation failed (HTTP 504)')] }, 'warn'),
            res('Claude retries', '', [U('toolu_42', 'move_issue', moveIn)], 'tool_use'),
            S('tool', 'move_issue succeeds', '', { output: { issue_id: 'ENG-412', state: 'Done' } }, 'ok')]),
          outcome: { ok: true, warn: true, text: 'Retrying every failure is right when every failure is a timeout. It still spends model turns the server could save.' }, rate: 0.95 },
        { steps: open402('No blocked moves exist, so this is today\'s behaviour.', 'return error("Operation failed")').concat([
            S('api', 'Claude receives the error', '', { role: 'user', content: [E('toolu_41', 'Operation failed')] }, 'warn'),
            res('Claude retries', '', [U('toolu_42', 'move_issue', moveIn)], 'tool_use'),
            S('tool', 'move_issue succeeds', '', { output: { issue_id: 'ENG-412', state: 'Done' } }, 'ok')]),
          outcome: { ok: true, warn: true, text: 'With no blocked moves, this change does nothing. Claude\'s blind retries happen to be right, at the cost of extra turns.' }, rate: 0.95 }
      ]
    }
  };

  /* ------------------------------------------------------------ m7-s4-04 tool_choice any */
  var clTools = [
    { name: 'record_changelog', description: 'Record the changelog entry for a merged PR.', input_schema: { type: 'object', properties: { pr: { type: 'integer' }, section: { type: 'string', enum: ['Added', 'Changed', 'Fixed'] }, entry: { type: 'string' } }, required: ['pr', 'section', 'entry'] } },
    { name: 'request_clarification', description: 'Ask the PR author a question when the change is unclear.', input_schema: { type: 'object', properties: { pr: { type: 'integer' }, question: { type: 'string' } }, required: ['pr', 'question'] } }
  ];
  var strictTools = clTools.map(function (t) { return Object.assign({ strict: true }, t); });
  var pr = 'PR #1874 "misc fixes" by dev-kiran. No description. Diff: lessons/streak.rb (+41 -12), app/javascript/StreakBadge.tsx (+8 -3).';
  var clarifyIn = { pr: 1874, question: 'This PR changes streak logic and the badge. Is it a user-facing fix, and what should the changelog say?' };
  var guessIn = { pr: 1874, section: 'Fixed', entry: 'Misc fixes.' };
  var parse = 'block = next(b for b in resp.content if b.type == "tool_use")\nhandle(block.name, block.input)';
  var prose = 'This PR seems to touch streak logic and the streak badge, but there is no description, so I can\'t tell what changed for users.';
  function reqCL(title, note, choice, tools, extra) {
    return req(title, note, Object.assign({ tool_choice: choice, tools: tools || clTools, messages: [{ role: 'user', content: pr }] }, extra || {}));
  }
  function proseFail() {
    return [res('Claude replies in prose', '"auto" lets Claude answer in text.', [T(prose)], 'end_turn', 'warn'),
      S('loop', 'Script parses tool input and finds none', 'The script can only read tool calls.', parse + '\n# StopIteration: no tool_use block', 'bad')];
  }
  function clarifyOk(note) {
    return [res('Claude asks the author', note, [U('toolu_51', 'request_clarification', clarifyIn)], 'tool_use', 'ok'),
      S('loop', 'Script parses the tool input', '', parse + '   # → request_clarification', 'ok'),
      S('tool', 'Question posted on PR #1874', '', { posted_comment: clarifyIn.question, pr: 1874 })];
  }
  var shotsSys = 'Example 1: PR #1801 → record_changelog({...})\nExample 2: PR #1815 (no description) → request_clarification({...})\nExample 3: PR #1820 → record_changelog({...})';

  var s404 = {
    id: 'm7-s4-04', who: 'Engineer', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: '<b>Either tool call is acceptable</b>: a changelog entry or a question to the author. Plain text breaks the parser.' },
      { id: 'B', label: 'Decider changed', desc: 'Every merged PR must get a changelog entry, so <b>only record_changelog is acceptable</b>. Both tools are still offered.' }
    ],
    runs: {
      A: [
        { steps: [reqCL('Request with tool_choice "auto" and few-shot examples', 'Every example ends in a tool call.', { type: 'auto' }, null, { system: shotsSys })].concat(proseFail()),
          outcome: { ok: false, text: 'Examples make a tool call more likely. "auto" still allows a text reply, and the parser cannot read one.' }, rate: 0.9 },
        { steps: [reqCL('Request with tool_choice "any"', 'A tool call is required; Claude picks which.', { type: 'any' })].concat(clarifyOk('No leading text with "any". Claude chose the question because the PR is unclear.')),
          outcome: { ok: true, text: '"any" rules out prose and leaves Claude the choice between two acceptable tools. Clear PRs get an entry, unclear ones get a question.' }, rate: 1 },
        { steps: [reqCL('Request forcing record_changelog by name', '', { type: 'tool', name: 'record_changelog' }),
            res('Claude must write an entry, even with nothing to go on', 'Forced by name: asking the author is no longer possible.', [U('toolu_52', 'record_changelog', guessIn)], 'tool_use', 'bad'),
            S('tool', 'Guessed entry recorded', '', { changelog: 'Fixed: Misc fixes. (#1874)' }, 'warn'),
            S('loop', 'Second request for clarifications', 'An extra call per PR, and the entry is already written.', 'resp2 = ask_if_unclear(pr)   # too late for #1874', 'warn')],
          outcome: { ok: false, text: 'Forcing one tool is right when only that tool is acceptable. Here a question was also acceptable, and forcing the entry took that choice away.' }, rate: 0.7 },
        { steps: [reqCL('Request with tool_choice "auto" and strict schemas', 'strict fixes the shape of tool input, not whether a call happens.', { type: 'auto' }, strictTools)].concat(proseFail()).concat([
            S('loop', 'Script retries the PR', 'A second paid request.', 'resp = retry(pr)', 'warn'),
            res('Claude calls a tool on the retry', '', [U('toolu_53', 'request_clarification', clarifyIn)], 'tool_use')]),
          outcome: { ok: true, warn: true, text: 'Retries clean up after prose arrives, at the cost of extra calls. "any" stops prose in the first place.' }, rate: 0.96 }
      ],
      B: [
        { steps: [reqCL('Request with tool_choice "auto" and few-shot examples', '', { type: 'auto' }, null, { system: shotsSys }),
            res('Claude asks a question instead', '"auto" allows either tool, or text.', [U('toolu_51', 'request_clarification', clarifyIn)], 'tool_use', 'bad'),
            S('tool', 'No changelog entry for #1874', '', { changelog: '(missing #1874)' }, 'bad')],
          outcome: { ok: false, text: 'Only an entry counts here, and "auto" lets Claude ask a question or reply in text.' }, rate: 0.8 },
        { steps: [reqCL('Request with tool_choice "any"', '', { type: 'any' }),
            res('Claude must call a tool, and picks the question', '"any" means any offered tool.', [U('toolu_51', 'request_clarification', clarifyIn)], 'tool_use', 'bad'),
            S('tool', 'No changelog entry for #1874', 'The one required result is missing.', { changelog: '(missing #1874)' }, 'bad')],
          outcome: { ok: false, text: 'With both tools offered, "any" can pick the one that is not acceptable. When one specific tool must run, force it by name.' }, rate: 0.85 },
        { steps: [reqCL('Request forcing record_changelog by name', '', { type: 'tool', name: 'record_changelog' }),
            res('Claude writes the entry from the diff', 'Forced by name: no text, no other tool.', [U('toolu_52', 'record_changelog', { pr: 1874, section: 'Fixed', entry: 'Streak count and badge now stay in sync after a missed day.' })], 'tool_use', 'ok'),
            S('loop', 'Script parses the tool input', '', parse + '   # → record_changelog', 'ok'),
            S('tool', 'Entry recorded', '', { changelog: 'Fixed: Streak count and badge now stay in sync after a missed day. (#1874)' }, 'ok')],
          outcome: { ok: true, text: 'Only one tool is acceptable, so name it and every PR gets an entry. This is the world where the runner-up wins.' }, rate: 1 },
        { steps: [reqCL('Request with tool_choice "auto" and strict schemas', '', { type: 'auto' }, strictTools),
            res('Claude asks a question', 'A tool call, so no retry fires.', [U('toolu_51', 'request_clarification', clarifyIn)], 'tool_use', 'bad'),
            S('tool', 'No changelog entry for #1874', '', { changelog: '(missing #1874)' }, 'bad')],
          outcome: { ok: false, text: 'Strict schemas and retries only catch missing tool calls. They do not stop Claude choosing the wrong tool.' }, rate: 0.8 }
      ]
    }
  };

  [s108, s109, s402, s404].forEach(L.add);
})();
