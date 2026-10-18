/* CCA-F Mock Exam #7 - scripted simulations for m7-s1-02, m7-s1-03, m7-s1-06, m7-s1-07.
   Same shape as sims.js: two worlds per question, one trace per option, deterministic. */
(function () {
  var L = window.SIMLIB, S = L.S, req = L.req, res = L.res, T = L.T, U = L.U, R = L.R, E = L.E;
  var tools1 = ['get_customer', 'lookup_order', 'process_refund', 'escalate_to_human', 'pause_subscription', 'Task'];

  /* ------------------------------------------------------------ m7-s1-02 explicit context to subagent */
  var claimMsg = 'The chicken thighs in last Tuesday\'s box were warm and smelled off when it arrived. I\'d rather have a replacement than a refund.';
  var shortPrompt = 'Check whether this customer\'s claim is eligible.';
  var fullPrompt = 'Check whether this claim is eligible.\nCustomer C-2291, box BX-4471, delivered Tue 2026-09-29.\nSpoiled: chicken thighs x2 (arrived warm, smelled off). Reported 2026-09-30.\nCustomer wants: a replacement, not a refund.\nReturn eligible yes/no, the policy reason, and the allowed remedy.';
  var goodVerdict = 'ELIGIBLE. Spoiled protein reported within 48 hours of delivery (box BX-4471, 2026-09-29). Replacement is an allowed remedy; ship chicken thighs x2 with the next box or as a one-off.';
  var hedge = 'Eligibility depends on which items were affected, when the box arrived and the remedy requested. Spoiled items are generally eligible if reported promptly. Unable to confirm for this customer.';
  function open02(chat) {
    return [S('cust', 'Customer writes', '', chat),
      req('Coordinator request', 'The coordinator sees the whole chat.', { tools: tools1, messages: [{ role: 'user', content: chat }] })];
  }
  function task02(id, prompt, note) {
    return res('Coordinator delegates through the Task tool', note, [U(id, 'Task', { subagent_type: 'policy-checker', description: 'Eligibility check', prompt: prompt })], 'tool_use');
  }
  function subSees(prompt, note, mark) {
    return S('sub', 'Policy subagent starts with only the Task prompt', note, { system: '(policy-checker AgentDefinition prompt)', messages: [{ role: 'user', content: prompt }] }, mark);
  }
  function tail02(id, verdict, reply, mark) {
    return [
      req('Coordinator receives the verdict as the Task result', '', { messages: ['\u2026chat\u2026', { role: 'assistant', content: '[Task ' + id + ']' }, { role: 'user', content: [R(id, verdict)] }] }),
      res('Coordinator replies', '', [T(reply)], 'end_turn'),
      S('cust', 'Customer sees', '', reply, mark)];
  }
  var okReply = 'Sorry about the chicken. Your claim qualifies, so I\'ll send two replacement chicken thighs with your next box at no charge.';
  var hedgeReply = 'Spoiled items are generally covered if reported promptly. Could you tell me more so I can check?';

  var formChat = 'I filed a claim in the app for last Tuesday\'s box. Can you sort it out?';
  var claimRec = { box_id: 'BX-4471', delivered: '2026-09-29', claim: { id: 'CL-3307', filed: '2026-09-30', spoiled: ['chicken thighs x2'], note: 'arrived warm', wants: 'replacement' } };

  var s102 = {
    id: 'm7-s1-02', who: 'Customer', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Which items spoiled, when the box arrived and what the customer wants are <b>only in the chat</b>, which the subagent cannot see.' },
      { id: 'B', label: 'Decider changed', desc: 'Customers file claims in the app, so those facts are <b>stored on the order record</b> and the chat just says "see my claim".' }
    ],
    runs: {
      A: [
        { steps: open02(claimMsg).concat([
            task02('toolu_21', fullPrompt, 'Option A: the coordinator writes the facts into the prompt.'),
            subSees(fullPrompt, 'Everything the verdict needs is in the prompt it receives.', 'ok'),
            S('sub', 'Subagent returns a specific verdict', '', goodVerdict)
          ]).concat(tail02('toolu_21', goodVerdict, okReply, 'ok')),
          outcome: { ok: true, text: 'A subagent knows only what its prompt says. The facts were in the chat, so the coordinator wrote them in, and the verdict became specific.' }, rate: 0.95 },
        { steps: open02(claimMsg).concat([
            task02('toolu_21', shortPrompt, 'Option B leaves the prompt as it was.'),
            subSees(shortPrompt, 'One line. No items, no date, no remedy.'),
            S('tool', 'Subagent calls lookup_order on its own', 'It has to guess the box; it picks the latest one.', { input: { box_id: 'BX-4471' }, output: { box_id: 'BX-4471', delivered: '2026-09-29', items: ['chicken thighs x2', 'basmati rice', 'lime', 'coriander'], status: 'delivered' } }),
            S('sub', 'Subagent still cannot tell what went wrong', 'The record lists what was shipped. Which item spoiled and the wish for a replacement exist only in the customer\'s words.', hedge, 'bad')
          ]).concat(tail02('toolu_21', hedge, hedgeReply, 'bad')),
          outcome: { ok: false, text: 'Lookup tools return backend records. Which item spoiled and what the customer wants are only in the chat, and no tool returns them.' }, rate: 0.4 },
        { steps: open02(claimMsg).concat([
            task02('toolu_21', shortPrompt, ''),
            subSees(shortPrompt, 'Option C improved the system prompt: policy text and two worked verdicts. The prompt is still one line.', 'warn'),
            S('sub', 'Subagent applies the policy to nothing', 'It now quotes the rule correctly, but has no case to apply it to.', 'Policy: spoiled items reported within 48h of delivery are eligible for refund or replacement. I do not know which items, the delivery date or the remedy wanted, so I cannot confirm eligibility.', 'bad')
          ]).concat(tail02('toolu_21', hedge, hedgeReply, 'bad')),
          outcome: { ok: false, text: 'Better instructions improve how the subagent reasons. It still lacks this case\'s facts, so the verdict still hedges.' }, rate: 0.45 },
        { steps: open02(claimMsg).concat([
            task02('toolu_21', shortPrompt, ''),
            S('sub', 'Subagent returns a structured "need more" verdict', 'Option D: honest, but empty.', { eligible: 'unknown', reason: 'case facts missing', needs: ['affected items', 'delivery date', 'requested remedy'] }, 'warn'),
            S('loop', 'Coordinator sends a second Task with the facts', 'A second subagent run for every claim. The coordinator had the facts the first time.', 'if verdict["eligible"] == "unknown":\n    task(prompt=restate_case(chat, verdict["needs"]))   # round trip 2', 'warn'),
            S('sub', 'Second run returns a specific verdict', '', goodVerdict, 'ok')
          ]).concat(tail02('toolu_22', goodVerdict, okReply, 'ok')),
          outcome: { ok: true, warn: true, text: 'It gets there, but every claim costs an extra round trip. The coordinator already has the facts and could send them the first time.' }, rate: 0.95 }
      ],
      B: [
        { steps: open02(formChat).concat([
            res('Coordinator looks up the record itself first', 'To restate the case it must fetch facts the chat does not hold.', [U('toolu_31', 'lookup_order', { box_id: 'BX-4471' })], 'tool_use'),
            S('tool', 'lookup_order returns the claim', 'The whole record now sits in the coordinator\'s context too.', { output: claimRec }, 'warn'),
            task02('toolu_32', fullPrompt, 'The coordinator copies the record into the prompt.'),
            S('sub', 'Subagent returns a specific verdict', '', goodVerdict)
          ]).concat(tail02('toolu_32', goodVerdict, okReply, 'ok')),
          outcome: { ok: true, warn: true, text: 'It works, but the coordinator fetches and copies records the subagent could read itself. Every claim fills the coordinator\'s context with backend data.' }, rate: 0.95 },
        { steps: open02(formChat).concat([
            task02('toolu_32', 'Check eligibility of the claim on customer C-2291\'s box from Tue 2026-09-29.', ''),
            S('tool', 'Subagent calls read-only lookup_order', 'Option B: the facts are in the record, and the tool returns them.', { input: { box_id: 'BX-4471' }, output: claimRec }, 'ok'),
            S('sub', 'Subagent returns a specific verdict', '', goodVerdict)
          ]).concat(tail02('toolu_32', goodVerdict, okReply, 'ok')),
          outcome: { ok: true, text: 'Here the facts live in a backend record, so a scoped read-only lookup lets the subagent gather them itself. This is the world where the runner-up wins.' }, rate: 0.95 },
        { steps: open02(formChat).concat([
            task02('toolu_32', shortPrompt, ''),
            subSees(shortPrompt, 'Better policy text, but no case and no tool to fetch it.', 'warn'),
            S('sub', 'Subagent hedges', '', hedge, 'bad')
          ]).concat(tail02('toolu_32', hedge, hedgeReply, 'bad')),
          outcome: { ok: false, text: 'Instructions do not supply facts. The subagent can neither see nor fetch the claim.' }, rate: 0.45 },
        { steps: open02(formChat).concat([
            task02('toolu_32', shortPrompt, ''),
            S('sub', 'Subagent returns a structured "need more" verdict', '', { eligible: 'unknown', needs: ['affected items', 'delivery date', 'requested remedy'] }, 'warn'),
            S('loop', 'Coordinator must fetch the record, then send a second Task', 'Two extra steps on every claim.', 'rec = lookup_order("BX-4471")\ntask(prompt=restate_case(rec))   # round trip 2', 'warn'),
            S('sub', 'Second run returns a specific verdict', '', goodVerdict, 'ok')
          ]).concat(tail02('toolu_33', goodVerdict, okReply, 'ok')),
          outcome: { ok: true, warn: true, text: 'It ends well, after a round trip and a lookup the subagent could have done itself.' }, rate: 0.9 }
      ]
    }
  };

  /* ------------------------------------------------------------ m7-s1-03 prompt vs hook for a nudge */
  var cancelMsg = 'Please cancel my subscription. We\'re travelling for most of November.';
  var offer = 'Before I pass this on: I can pause your deliveries for up to 8 weeks instead, so your plan is ready when you\'re back. Would you like that?';
  var decline = 'No thanks, please just cancel.';
  var escIn = { customer_id: 'C-2291', reason: 'cancellation', summary: 'Wants to cancel; travelling in November. Pause offered and declined.' };
  var escOut = { ticket: 'ESC-5520', queue: 'cancellations', eta: 'within 1 business day' };
  var handoff = 'Understood. I\'ve passed your cancellation to our team (ticket ESC-5520). They\'ll confirm within one business day.';
  var sysLine = 'When a customer asks to cancel, suggest pausing deliveries first. If they decline, route the request with escalate_to_human.';
  var sysShots = 'Example 1\nCustomer: Cancel my plan, it\'s too expensive.\nAgent: I can pause deliveries for a few weeks if that helps. Want me to?\nCustomer: No.\nAgent: [escalate_to_human reason="cancellation"]\n\nExample 2\nCustomer: We\'re moving, please cancel.\nAgent: Would a pause until you\'ve settled in work better?\nCustomer: Yes, 4 weeks.\nAgent: [pause_subscription weeks=4]';
  function nudge03(sys, note, offered) {
    var st = [S('cust', 'Customer writes', '', cancelMsg),
      req('Loop sends the request', note, { system: sys, tool_choice: { type: 'auto' }, tools: tools1, messages: [{ role: 'user', content: cancelMsg }] })];
    if (!offered) {
      return st.concat([
        res('Claude escalates straight away (chat 17 of 20)', 'Prompt guidance is followed most of the time, not every time.', [U('toolu_41', 'escalate_to_human', { customer_id: 'C-2291', reason: 'cancellation', summary: 'Wants to cancel; travelling in November.' })], 'tool_use', 'bad'),
        S('tool', 'escalate_to_human queues the cancellation', 'No pause was offered in this chat.', { output: escOut }),
        S('cust', 'Customer sees', '', handoff, 'bad')]);
    }
    return st.concat([
      res('Claude offers a pause first', '', [T(offer)], 'end_turn', 'ok'),
      S('cust', 'Customer replies', '', decline),
      res('Claude routes the cancellation to a person', '', [U('toolu_41', 'escalate_to_human', escIn)], 'tool_use'),
      S('tool', 'escalate_to_human queues the cancellation', '', { input: escIn, output: escOut }),
      S('cust', 'Customer sees', '', handoff, 'ok')]);
  }
  var hookCode = 'def offer_pause_first(input_data, tool_use_id, context):\n    if (input_data["tool_name"] == "escalate_to_human"\n            and is_cancellation(input_data["tool_input"])      # classifier to maintain\n            and not session.pause_offered):                    # set by a phrase check on replies\n        return {"hookSpecificOutput": {"hookEventName": "PreToolUse",\n            "permissionDecision": "deny",\n            "permissionDecisionReason": "Offer a pause before escalating a cancellation."}}\n    return {}';
  function hook03(mark, note) {
    return [S('cust', 'Customer writes', '', cancelMsg),
      res('Claude escalates straight away', '', [U('toolu_41', 'escalate_to_human', { customer_id: 'C-2291', reason: 'cancellation', summary: 'Wants to cancel.' })], 'tool_use'),
      S('hook', 'PreToolUse hook denies escalate_to_human', note, hookCode, mark),
      req('Denial goes back to Claude as an error result', '', { messages: ['\u2026', { role: 'user', content: [E('toolu_41', 'Blocked by hook: Offer a pause before escalating a cancellation.')] }] }),
      res('Claude offers a pause', '', [T(offer)], 'end_turn'),
      S('cust', 'Customer replies', '', decline),
      res('Claude escalates again; the hook now allows it', 'session.pause_offered was set when the reply contained "pause".', [U('toolu_42', 'escalate_to_human', escIn)], 'tool_use'),
      S('cust', 'Customer sees', '', handoff, 'ok')];
  }
  var forced03 = function (world) {
    return [S('cust', 'Customer writes', '', cancelMsg),
      req('Loop forces pause_subscription on the first cancel turn', 'Option A.', { tool_choice: { type: 'tool', name: 'pause_subscription' }, tools: tools1, messages: [{ role: 'user', content: cancelMsg }] }),
      res('Claude must call pause_subscription, so it does', 'Forced by name: no text, so no question to the customer.', [U('toolu_43', 'pause_subscription', { customer_id: 'C-2291', weeks: 4 })], 'tool_use'),
      S('tool', 'Subscription paused without asking', 'The customer agreed to nothing.', { output: { status: 'paused', resumes: '2026-11-03' } }, 'bad'),
      S('cust', 'Customer sees', '', 'I\'ve paused your deliveries until 3 November.', 'bad')];
  };
  var s103 = {
    id: 'm7-s1-03', who: 'Customer', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'A retention nudge: <b>missing the pause offer in some chats is acceptable</b>, and the change should be light to maintain.' },
      { id: 'B', label: 'Decider changed', desc: 'The offer is now a rule: <b>every</b> cancellation must get a pause offer before it reaches a person.' }
    ],
    runs: {
      A: [
        { steps: forced03('A'), outcome: { ok: false, text: 'Forcing the tool applies a pause instead of offering one. The goal was a question to the customer, not an action.' }, rate: 0 },
        { steps: nudge03(sysLine, 'Option B: one line in the system prompt.', true),
          outcome: { ok: true, text: 'A soft goal where some misses are fine is what prompt guidance is for. It is one line to maintain.' }, rate: 0.9 },
        { steps: hook03('warn', 'It works, but it needs a cancellation classifier and an "offer made" flag, both kept in sync with how Claude phrases things.'),
          outcome: { ok: true, warn: true, text: 'Every chat now gets the offer, which nobody asked for. Misses were acceptable, so this is code to maintain for a guarantee the goal does not need.' }, rate: 1 },
        { steps: nudge03(sysLine + '\n\n' + sysShots, 'Option D: two sample chats show the order and the tone.', true),
          outcome: { ok: true, text: 'A few examples show the offer, the hand-off and the tone. No code to maintain.' }, rate: 0.92 }
      ],
      B: [
        { steps: forced03('B'), outcome: { ok: false, text: 'Still applies a pause nobody agreed to.' }, rate: 0 },
        { steps: nudge03(sysLine, '', false),
          outcome: { ok: false, text: 'Prompt guidance has a small failure rate. When every cancellation must get the offer, one skipped chat is a failure.' }, rate: 0.9 },
        { steps: hook03('ok', 'Your code checks every escalation. Claude cannot skip the offer.'),
          outcome: { ok: true, text: 'A step that must happen every time belongs in code. The hook blocks the escalation until the offer is made. This is the world where the runner-up wins.' }, rate: 1 },
        { steps: nudge03(sysLine + '\n\n' + sysShots, 'Examples make the offer more consistent, not guaranteed.', false),
          outcome: { ok: false, text: 'Examples raise the hit rate but cannot guarantee it. A must-every-time step needs a deterministic check.' }, rate: 0.92 }
      ]
    }
  };

  /* ------------------------------------------------------------ m7-s1-06 tool description first */
  var boxMsg = 'Last Tuesday\'s box was missing the lime and the coriander.';
  var thinDesc = { name: 'lookup_order', description: 'Looks up a box', input_schema: { type: 'object', properties: { box_id: { type: 'string' } }, required: ['box_id'] } };
  var fullDesc = { name: 'lookup_order', description: 'Returns one delivered box: items, delivery date, refundable amount. box_id is the box ID, format BX-#### (e.g. BX-4471), never a date. If the customer names a box by date ("last Tuesday\'s box"), call get_customer first and pick the box whose delivered date matches. Example: lookup_order({"box_id": "BX-4471"}).', input_schema: thinDesc.input_schema };
  var custRec = { customer_id: 'C-2291', boxes: [{ box_id: 'BX-4438', delivered: '2026-09-22' }, { box_id: 'BX-4471', delivered: '2026-09-29' }] };
  var boxOut = { box_id: 'BX-4471', delivered: '2026-09-29', missing_items: ['lime', 'coriander'], refundable: 3.4 };
  var boxReply = 'Box BX-4471 (29 Sep) was short a lime and the coriander. I\'ve refunded $3.40 to your card.';
  function good06(note) {
    return [
      res('Claude calls get_customer first', note, [U('toolu_51', 'get_customer', { customer_id: 'C-2291' })], 'tool_use', 'ok'),
      S('tool', 'get_customer lists the box IDs with dates', '', { output: custRec }),
      res('Claude calls lookup_order with the matching ID', '2026-09-29 was last Tuesday, so BX-4471.', [U('toolu_52', 'lookup_order', { box_id: 'BX-4471' })], 'tool_use'),
      S('tool', 'lookup_order succeeds', '', { output: boxOut }),
      S('cust', 'Customer sees', '', boxReply, 'ok')];
  }
  function start06(desc, sys, chat, note) {
    var body = { tools: [desc, 'get_customer', '\u2026'], messages: [{ role: 'user', content: chat || boxMsg }] };
    if (sys) body.system = sys;
    return [S('cust', 'Customer writes', '', chat || boxMsg), req('Loop sends the request', note, body)];
  }
  var shot06 = 'Example\nCustomer: My box from last Tuesday was missing the salmon.\nAgent: [get_customer] \u2192 boxes with dates \u2192 [lookup_order box_id="BX-4471"]';
  var dateChat = 'The box that came on 22 September had a split bag of rice.';
  var s106 = {
    id: 'm7-s1-06', who: 'Customer', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'The whole <code>lookup_order</code> description is <b>"Looks up a box"</b>: no ID format, no example, no route from a date.' },
      { id: 'B', label: 'Decider changed', desc: 'The description <b>already gives the ID format, a sample call and the date-to-ID route</b>, and the agent still passes dates in some chats.' }
    ],
    runs: {
      A: [
        { steps: start06(fullDesc, null, null, 'Option A: the description now says what a box ID is and how to get one from a date.').concat(good06('The description told it to.')),
          outcome: { ok: true, text: 'The description is how Claude learns to call a tool. It said nothing about the input; now it does, and the bad call stops happening.' }, rate: 0.95 },
        { steps: start06(thinDesc, null, null, 'The description is still one line.').concat([
            res('Claude passes the date as the box ID', '', [U('toolu_51', 'lookup_order', { box_id: '2026-09-29' })], 'tool_use', 'warn'),
            S('tool', 'lookup_order returns a structured validation error', 'Option B: clear, but it arrives after the bad call.', { input: { box_id: '2026-09-29' }, output: { isError: true, errorCategory: 'validation', message: 'box_id must look like BX-#### (e.g. BX-4471). Box IDs are in the get_customer record.' } }),
            res('Claude recovers via get_customer', '', [U('toolu_52', 'get_customer', { customer_id: 'C-2291' })], 'tool_use'),
            S('tool', 'Then lookup_order BX-4471 succeeds', 'One wasted call in nearly every date-named chat.', { output: boxOut }),
            S('cust', 'Customer sees', '', boxReply, 'ok')]),
          outcome: { ok: true, warn: true, text: 'The agent recovers, after a failed call almost every time. The first step is to stop the bad call, and the description is where it starts.' }, rate: 0.9 },
        { steps: start06(thinDesc, shot06, dateChat, 'Option C: one example in the system prompt; the description still says "Looks up a box".').concat([
            res('Claude passes the date as the box ID', 'This customer gave a date, not "last Tuesday". The example does not match, and the tool never said what a box ID is.', [U('toolu_51', 'lookup_order', { box_id: '2026-09-22' })], 'tool_use', 'bad'),
            S('tool', 'lookup_order fails', '', { input: { box_id: '2026-09-22' }, output: { isError: true, content: 'not found' } }, 'bad'),
            S('cust', 'Customer sees', '', 'I couldn\'t find that box. Could you give me the box number?', 'bad')]),
          outcome: { ok: false, text: 'The example covers the phrasing it shows. The root cause is the one-line description, and it is still there.' }, rate: 0.85 },
        { steps: start06(thinDesc, null, null, 'Option D adds lookup_order_by_date, described as "Looks up a box by date".').concat([
            S('loop', 'New tool built, deployed and described', 'More work than a first step.', 'tools.append({"name": "lookup_order_by_date", "description": "Looks up a box by date"})', 'warn'),
            res('Claude calls the new tool with the customer\'s words', 'A minimal description again: no date format.', [U('toolu_51', 'lookup_order_by_date', { date: 'last Tuesday' })], 'tool_use', 'bad'),
            S('tool', 'lookup_order_by_date fails', '', { output: { isError: true, content: 'date must be YYYY-MM-DD' } }, 'bad')]),
          outcome: { ok: false, text: 'A new tool with a thin description gets misused the same way. The existing route through get_customer just needed describing.' }, rate: 0.8 }
      ],
      B: [
        { steps: start06(fullDesc, null, dateChat, 'Option A: the description is already this full. Nothing left to add.').concat([
            res('Claude still passes the date in this chat', '', [U('toolu_51', 'lookup_order', { box_id: '2026-09-22' })], 'tool_use', 'bad'),
            S('tool', 'lookup_order fails', '', { output: { isError: true, content: 'not found' } }, 'bad')]),
          outcome: { ok: false, text: 'The description already says everything. More of the same does not change the inconsistent chats.' }, rate: 0.85 },
        { steps: start06(fullDesc, null, dateChat, '').concat([
            res('Claude passes the date', '', [U('toolu_51', 'lookup_order', { box_id: '2026-09-22' })], 'tool_use', 'warn'),
            S('tool', 'Structured validation error', '', { output: { isError: true, errorCategory: 'validation', message: 'box_id must look like BX-####. Box IDs are in the get_customer record.' } }),
            res('Claude recovers via get_customer, then BX-4438', '', [U('toolu_52', 'get_customer', { customer_id: 'C-2291' })], 'tool_use'),
            S('cust', 'Customer sees', '', 'Box BX-4438 (22 Sep) had a split bag of rice. I\'ve refunded $1.80.', 'ok')]),
          outcome: { ok: true, warn: true, text: 'This is a reasonable next step here, but it fixes the bad call after it happens. An example prevents it.' }, rate: 0.95 },
        { steps: start06(fullDesc, shot06 + '\n\nExample\nCustomer: The box from 22 September was damaged.\nAgent: [get_customer] \u2192 [lookup_order box_id="BX-4438"]', dateChat, 'Option C: the description is clear; examples show the pattern in action.').concat([
            res('Claude follows the example: get_customer first', '', [U('toolu_51', 'get_customer', { customer_id: 'C-2291' })], 'tool_use', 'ok'),
            S('tool', 'get_customer lists the box IDs with dates', '', { output: custRec }),
            res('Claude calls lookup_order BX-4438', '', [U('toolu_52', 'lookup_order', { box_id: 'BX-4438' })], 'tool_use'),
            S('cust', 'Customer sees', '', 'Box BX-4438 (22 Sep) had a split bag of rice. I\'ve refunded $1.80.', 'ok')]),
          outcome: { ok: true, text: 'The description is full and behaviour is still inconsistent, which is when examples earn their tokens. This is the world where the runner-up wins.' }, rate: 0.95 },
        { steps: start06(fullDesc, null, dateChat, '').concat([
            S('loop', 'New tool built, deployed and described', '', 'tools.append({"name": "lookup_order_by_date", ...})', 'warn'),
            res('Claude calls lookup_order_by_date', '', [U('toolu_51', 'lookup_order_by_date', { date: '2026-09-22' })], 'tool_use'),
            S('cust', 'Customer sees', '', 'Box BX-4438 (22 Sep) had a split bag of rice. I\'ve refunded $1.80.', 'ok')]),
          outcome: { ok: true, warn: true, text: 'It works, but a new tool is far more to build and keep in sync than one example.' }, rate: 0.9 }
      ]
    }
  };

  /* ------------------------------------------------------------ m7-s1-07 structured business error */
  var pauseMsg = 'Can you pause my next box? We\'re away next week.';
  var nextBox = { box_id: 'BX-4502', delivers: '2026-10-06', region: 'NW-3', status: 'scheduled' };
  var bizErr = { isError: true, errorCategory: 'business', isRetryable: false, message: 'Box BX-4502 is past its packing cut-off (Fri 2026-10-02 18:00 for region NW-3). The next box that can be paused is BX-4530, delivering 2026-10-13.' };
  var bizReply = 'Next Tuesday\'s box (6 Oct) is already being packed, so it can\'t be paused. I can pause the one after, due 13 Oct. Shall I?';
  var downReply = 'Sorry, our system seems to be down right now. Please try again later.';
  function start07(note, desc) {
    var t = desc ? [{ name: 'pause_subscription', description: desc }, 'lookup_order', '\u2026'] : tools1;
    return [S('cust', 'Customer writes', '', pauseMsg), req('Loop sends the request', note, { tools: t, messages: [{ role: 'user', content: pauseMsg }] })];
  }
  var callPause = res('Claude calls pause_subscription', '', [U('toolu_61', 'pause_subscription', { customer_id: 'C-2291', box_id: 'BX-4502' })], 'tool_use');
  var goodEnd07 = [
    res('Claude explains and offers the next box', '', [T(bizReply)], 'end_turn', 'ok'),
    S('cust', 'Customer replies', '', 'Yes please.'),
    res('Claude pauses BX-4530', '', [U('toolu_62', 'pause_subscription', { customer_id: 'C-2291', box_id: 'BX-4530' })], 'tool_use'),
    S('tool', 'Pause succeeds', '', { output: { status: 'paused', box_id: 'BX-4530' } }, 'ok')];
  var cutDesc = 'Pauses a delivery. Pauses fail after the box\'s packing cut-off; check the box date with lookup_order before calling.';
  var fixedDesc = 'Pauses a delivery. Pauses close at 18:00 on the Friday before delivery, in every region. Check the box date with lookup_order first; if it is past the cut-off, offer the next box instead.';
  var s107 = {
    id: 'm7-s1-07', who: 'Customer', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'The packing cut-off <b>varies by region and only the backend knows it</b>; today a late pause returns "Request failed."' },
      { id: 'B', label: 'Decider changed', desc: 'The cut-off is <b>fixed and published</b>: 18:00 on the Friday before delivery, in every region.' }
    ],
    runs: {
      A: [
        { steps: start07('Option A: the description mentions the cut-off.', cutDesc).concat([
            res('Claude checks the box date first', '', [U('toolu_60', 'lookup_order', { box_id: 'BX-4502' })], 'tool_use'),
            S('tool', 'lookup_order returns the box, but no cut-off', 'The cut-off for NW-3 lives only in the backend. Claude has nothing to compare against.', { output: nextBox }, 'warn'),
            callPause,
            S('tool', 'pause_subscription still returns the old error', 'Claude guessed two days ahead was early enough. It was not.', { output: { isError: true, content: [{ type: 'text', text: 'Request failed.' }] } }, 'bad'),
            res('Claude retries, then gives up', '', [T(downReply)], 'end_turn'),
            S('cust', 'Customer sees', '', downReply, 'bad')]),
          outcome: { ok: false, text: 'A rule in the description helps only if the agent can check it. The cut-off varies by region and only the backend knows it.' }, rate: 0.3 },
        { steps: start07('').concat([callPause,
            S('tool', 'Structured, but labelled transient', '', { output: { isError: true, errorCategory: 'transient', isRetryable: false, message: 'Pause unavailable for this box.' } }, 'warn'),
            req('Error goes back to Claude', '', { messages: ['\u2026', { role: 'user', content: [E('toolu_61', '{"errorCategory":"transient","isRetryable":false,"message":"Pause unavailable for this box."}')] }] }),
            res('Claude reads "transient" as an outage', 'Retries stop, but the story is still "something is broken".', [T('We\'re having a temporary problem pausing boxes. Please try again in a little while.')], 'end_turn', 'bad'),
            S('cust', 'Customer sees', 'It will fail again later too. The customer has no true reason.', 'We\'re having a temporary problem pausing boxes. Please try again in a little while.', 'bad')]),
          outcome: { ok: false, text: 'The label says outage when it is a policy outcome, and the message gives Claude nothing true to tell the customer.' }, rate: 0.4 },
        { steps: start07('').concat([callPause,
            S('tool', 'pause_subscription returns a business error', 'Option C: the kind of failure, "do not retry", the cut-off and the next option.', { output: bizErr }, 'ok'),
            req('Error goes back to Claude', '', { messages: ['\u2026', { role: 'user', content: [E('toolu_61', JSON.stringify(bizErr))] }] })
          ]).concat(goodEnd07),
          outcome: { ok: true, text: 'Only the backend knows the cut-off, so the error is where the agent learns it. A business category with no retry stops the loop, and the note gives Claude something true to say.' }, rate: 1 },
        { steps: start07('').concat([callPause,
            S('tool', 'pause_subscription fails as before', '', { output: { isError: true, content: [{ type: 'text', text: 'Request failed.' }] } }),
            res('Claude retries', '', [U('toolu_62', 'pause_subscription', { customer_id: 'C-2291', box_id: 'BX-4502' })], 'tool_use'),
            S('hook', 'PreToolUse hook blocks the repeat and says escalate', 'The retries stop, but nobody learns why the pause failed.', { hookEventName: 'PreToolUse', permissionDecision: 'deny', permissionDecisionReason: 'Repeat pause_subscription call. Escalate to a human.' }, 'warn'),
            res('Claude escalates', '', [U('toolu_63', 'escalate_to_human', { customer_id: 'C-2291', reason: 'pause failed', summary: 'pause_subscription returned Request failed.' })], 'tool_use'),
            S('cust', 'Customer sees', 'A person now gets a case the agent could have explained itself.', 'I\'ve passed this to a colleague who will be in touch.', 'bad')]),
          outcome: { ok: false, text: 'Blocking repeats treats the symptom. The customer still gets no reason, and a person handles a policy outcome the agent could have explained.' }, rate: 0.5 }
      ],
      B: [
        { steps: start07('Option A: the description states the fixed cut-off.', fixedDesc).concat([
            res('Claude checks the box date first', '', [U('toolu_60', 'lookup_order', { box_id: 'BX-4502' })], 'tool_use'),
            S('tool', 'lookup_order: delivers Tue 2026-10-06', 'Cut-off was Fri 2026-10-02 18:00, already past. Claude can check that itself.', { output: nextBox }, 'ok'),
            res('Claude skips the doomed call and offers the next box', '', [T(bizReply)], 'end_turn'),
            S('cust', 'Customer sees', '', bizReply, 'ok')]),
          outcome: { ok: true, text: 'A fixed, published rule can be checked in advance, so the description prevents the failing call. This is the world where the runner-up wins.' }, rate: 0.95 },
        { steps: start07('').concat([callPause,
            S('tool', 'Structured, but labelled transient', '', { output: { isError: true, errorCategory: 'transient', isRetryable: false, message: 'Pause unavailable for this box.' } }, 'warn'),
            res('Claude reads it as an outage', '', [T('We\'re having a temporary problem pausing boxes. Please try again later.')], 'end_turn', 'bad')]),
          outcome: { ok: false, text: 'Still mislabelled and still empty.' }, rate: 0.4 },
        { steps: start07('').concat([callPause,
            S('tool', 'pause_subscription returns the business error', 'Clear and true, but this call could have been skipped: the rule is published.', { input: { box_id: 'BX-4502' }, output: bizErr }, 'warn')
          ]).concat(goodEnd07),
          outcome: { ok: true, warn: true, text: 'It still recovers well, but the agent makes a failing call it could have avoided by checking a known rule first.' }, rate: 1 },
        { steps: start07('').concat([callPause,
            S('hook', 'Hook blocks the retry and says escalate', '', { permissionDecision: 'deny', permissionDecisionReason: 'Repeat pause_subscription call. Escalate to a human.' }, 'warn'),
            S('cust', 'Customer sees', '', 'I\'ve passed this to a colleague who will be in touch.', 'bad')]),
          outcome: { ok: false, text: 'Still no reason for the customer, and a person gets a case the agent could have handled.' }, rate: 0.5 }
      ]
    }
  };

  [s102, s103, s106, s107].forEach(L.add);
})();
