/* CCA-F Mock Exam #7 - scripted simulations for context window, sessions and planning:
   m7-s1-10, m7-s2-09, m7-s2-10, m7-s3-09, m7-s4-08, m7-s3-05, m7-s2-03, m7-s4-05.
   Same shape as sims.js: two worlds per question, one trace per option, deterministic. */
(function () {
  var L = window.SIMLIB, S = L.S, req = L.req, res = L.res, T = L.T, U = L.U, R = L.R, X = L.X;
  /* P(label, tokens, kind) is one slice of a context bar; M(step, total, parts) attaches the bar.
     Slices are drawn left to right, so their order is their position in the window: start, middle, end. */
  function P(label, tokens, kind) { return { label: label, tokens: tokens, kind: kind }; }
  function M(step, total, parts) { return X(step, { meter: { total: total, parts: parts } }); }
  var CC = { loop: 'Claude Code' };

  /* ============================================================ m7-s1-10 case facts across summarisation */
  var W1 = 200000;
  var tools1 = ['get_customer', 'lookup_order', 'process_refund', 'escalate_to_human', 'pause_subscription', 'Task'];
  var promise = 'I am sorry about box BX-5130. I will credit $24.00 for the chicken thighs x2, the spinach and the feta.';
  var factsBlock = 'CASE FACTS (kept by your code, never summarised)\ncustomer: C-2291   box: BX-5130   claim: CL-3412\nitems listed by customer: chicken thighs x2, spinach, feta\npromised: credit $24.00 (turn 6)   status: awaiting customer reply on replacement';
  var blurSummary = 'Summary of turns 1-34: customer reported spoiled items in a recent box. The agent apologised and offered a credit. Customer later asked about delivery times and a replacement.';
  var lateAsk = 'OK so where is my credit? You said you would sort it.';
  var goodCredit = 'The $24.00 credit for the chicken thighs x2, spinach and feta on box BX-5130 is applied now. You will see it on your next invoice.';
  var badCredit = 'I can offer a $15.00 credit for the spoiled chicken. Would that work?';
  function before110(toolTok, toolLabel) {
    return M(S('ctx', 'Turn 35: the window nears the limit', 'Long dispute: the customer and agent have gone back and forth for 34 turns. The promise was made in turn 6.', null),
      W1, [P('system + tool defs', 4000, 'sys'), P('turns 1-10 (items listed, $24 promised)', 52000, 'keep'), P(toolLabel, toolTok, 'tool'), P('turns 11-34', 104000 - (toolTok - 6000), 'keep')]);
  }
  function summarise110(note, summary, mark) {
    return S('loop', 'SDK summarises older turns', note, summary, mark);
  }
  function after110(note, parts) {
    return M(S('ctx', 'Context after summarising', note, null), W1, parts);
  }
  var s110 = {
    id: 'm7-s1-10', who: 'Customer', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'The tool results are <b>short</b> (about 6k of the window). The window fills with long dispute turns, and the promise sits in the turns that get summarised.' },
      { id: 'B', label: 'Decider changed', desc: '<b>Bulky tool results fill the context</b>: every <code>get_customer</code> and <code>lookup_order</code> call returns 40+ fields, and they are most of the window.' }
    ],
    runs: {
      A: [
        { steps: [S('cust', 'Turn 6: the agent makes a promise', '', promise),
            S('loop', 'Your code writes the promise into a case-facts block', 'Option A. The block lives outside the message history, so the summariser never touches it.', factsBlock, 'ok'),
            before110(6000, 'tool results (short)'),
            summarise110('Turns 1-34 become a short summary. The amount and items blur, as summaries do.', blurSummary),
            after110('The case-facts block is still first in every request, word for word.', [P('system + tool defs', 4000, 'sys'), P('case-facts block', 400, 'keep'), P('summary of turns 1-34', 3000, 'drop'), P('recent turns', 12000, 'keep')]),
            S('cust', 'Turn 41: customer asks', '', lateAsk),
            req('Loop sends the request', 'The case-facts block leads the request.', { system: '(support prompt)\n\n' + factsBlock, tools: tools1, messages: ['[summary of turns 1-34]', '\u2026', { role: 'user', content: lateAsk }] }),
            res('Claude answers from the case facts', '', [T(goodCredit)], 'end_turn', 'ok'),
            S('cust', 'Customer sees', '', goodCredit, 'ok')],
          outcome: { ok: true, text: 'The promise and the items never pass through the summariser. Every request carries them exactly, at the top.' }, rate: 0.97 },
        { steps: [S('cust', 'Turn 6: the agent makes a promise', '', promise),
            S('loop', 'Your code trims each tool result to the fields used', 'Option B. The results were short already: 6k becomes 4k.', 'def trim(result): return {k: result[k] for k in USED_FIELDS}', 'warn'),
            before110(4000, 'tool results (trimmed, saved 2k)'),
            summarise110('Trimming saved 1% of the window, so the summary fires one turn later. Turn 6, with the promise, is still summarised.', blurSummary, 'bad'),
            after110('$24.00, spinach and feta now exist only as "offered a credit" and "spoiled items".', [P('system + tool defs', 4000, 'sys'), P('summary of turns 1-34 ($24, items lost)', 3000, 'drop'), P('recent turns', 12000, 'keep')]),
            S('cust', 'Turn 41: customer asks', '', lateAsk),
            res('Claude guesses an amount', 'The exact figure is gone from its context.', [T(badCredit)], 'end_turn', 'bad'),
            S('cust', 'Customer sees a smaller credit than promised', '', badCredit, 'bad')],
          outcome: { ok: false, text: 'Trimming fixes a window full of bulky tool output. These results were short, so the chat still crossed the threshold and the summary still blurred the promise.' }, rate: 0.55 },
        { steps: [S('cust', 'Turn 6: the agent makes a promise', '', promise),
            S('loop', 'Summarise threshold raised from 160k to 185k', 'Option C. More of each chat stays verbatim.', { summarize_at_tokens: 185000 }),
            M(S('ctx', 'Turn 48: the window reaches the new threshold', 'Long disputes keep going. They just take longer to get here.', null), W1, [P('system + tool defs', 4000, 'sys'), P('turns 1-10 ($24 promised)', 52000, 'keep'), P('tool results', 7000, 'tool'), P('turns 11-47', 123000, 'keep')]),
            summarise110('Turns 1-47 are summarised. Same lossy step, later.', blurSummary, 'bad'),
            S('cust', 'Turn 52: customer asks', '', lateAsk),
            res('Claude guesses an amount', '', [T(badCredit)], 'end_turn', 'bad')],
          outcome: { ok: false, text: 'A later threshold delays the loss. Disputes that run long still cross it, and the promise still goes through the summary.' }, rate: 0.7 },
        { steps: [S('cust', 'Turn 6: the agent makes a promise', '', promise),
            S('loop', 'Summariser prompt: "quote every amount and item"', 'Option D.', 'Summarise older turns. Quote every amount, item and ID exactly.'),
            summarise110('Pass 1 keeps the facts.', 'Summary 1: agent promised a $24.00 credit for chicken thighs x2, spinach, feta on BX-5130.', 'ok'),
            summarise110('Pass 2 summarises Summary 1 plus 30 more turns, with many more amounts to quote (delivery fee, replacement cost). One slips.', 'Summary 2: credits discussed ($24, $6.99 fee); spoiled chicken and spinach; replacement offered.', 'warn'),
            after110('Feta is gone, and which amount was the promise is now unclear.', [P('system + tool defs', 4000, 'sys'), P('summary 2 (feta lost, amounts mixed)', 4500, 'drop'), P('recent turns', 12000, 'keep')]),
            res('Claude answers from the summary', '', [T('The credit for the chicken and spinach is applied.')], 'end_turn', 'bad')],
          outcome: { ok: false, text: 'A better summary prompt helps, but every pass is lossy again. A separate facts block takes the facts out of that path.' }, rate: 0.8 }
      ],
      B: [
        { steps: [S('loop', 'Case-facts block kept at the top', '', factsBlock, 'ok'),
            M(S('ctx', 'Turn 12: the window is already near the limit', 'Each lookup returns 40+ fields: warehouse codes, carrier scans, nutrition data.', null), W1, [P('system + tool defs', 4000, 'sys'), P('case-facts block', 400, 'keep'), P('tool results (40+ fields each)', 138000, 'tool'), P('turns 1-11', 18000, 'keep')]),
            summarise110('Summaries now fire every few turns, because tool output keeps refilling the window.', 'Summary of turns 1-11 \u2026', 'warn'),
            res('Claude answers from the case facts', '', [T(goodCredit)], 'end_turn', 'ok')],
          outcome: { ok: true, warn: true, text: 'The facts survive, but the real problem is untouched: tool output fills the window and forces a summary every few turns, losing the rest of the chat.' }, rate: 0.95 },
        { steps: [S('cust', 'Turn 6: the agent makes a promise', '', promise),
            S('loop', 'Your code trims each tool result to the fields used', 'Option B. Each result drops from about 9k tokens to 300.', { kept: ['box_id', 'delivered', 'items', 'refundable'], dropped: '38 other fields' }, 'ok'),
            M(S('ctx', 'Turn 41: the window has room to spare', 'Tool output was the bulk. Without it the chat never reaches the summarise threshold.', null), W1, [P('system + tool defs', 4000, 'sys'), P('turns 1-10 ($24 promised, verbatim)', 18000, 'keep'), P('tool results (trimmed)', 5000, 'tool'), P('turns 11-40', 36000, 'keep')]),
            res('Claude reads its own promise in turn 6', '', [T(goodCredit)], 'end_turn', 'ok'),
            S('cust', 'Customer sees', '', goodCredit, 'ok')],
          outcome: { ok: true, text: 'Here the window filled with bulky tool output. Trimming it keeps the chat under the threshold, so nothing is summarised and the promise stays verbatim. This is the world where the runner-up wins.' }, rate: 0.95 },
        { steps: [S('loop', 'Threshold raised to 185k', '', { summarize_at_tokens: 185000 }),
            M(S('ctx', 'Turn 15: tool output reaches even the new threshold', '', null), W1, [P('system + tool defs', 4000, 'sys'), P('tool results (40+ fields)', 160000, 'tool'), P('turns 1-14', 22000, 'keep')]),
            summarise110('Summarised anyway. The promise blurs.', blurSummary, 'bad')],
          outcome: { ok: false, text: 'Bulky tool output fills any threshold quickly.' }, rate: 0.6 },
        { steps: [S('loop', 'Summariser told to quote every amount', '', 'Quote every amount, item and ID exactly.'),
            summarise110('The summariser also has to compress 140k of tool fields, and quotes those amounts too. The promise is one figure among dozens.', 'Credits/amounts: $24.00, $6.99, $12.40, $3.10, $58.20 \u2026', 'warn'),
            res('Claude picks the wrong figure', '', [T(badCredit)], 'end_turn', 'bad')],
          outcome: { ok: false, text: 'Summaries still fire every few turns, and each one is lossy.' }, rate: 0.7 }
      ]
    }
  };

  /* ============================================================ m7-s2-09 /compact for context pressure */
  var full209 = [P('system + CLAUDE.md', 12000, 'sys'), P('test output, runs 1-9', 121000, 'tool'), P('screen decisions + file edits', 41000, 'keep'), P('recent turns', 13000, 'keep')];
  function full209Step(note) {
    return M(S('ctx', 'Context is 187k of 200k', note || 'Most of it is old jest output. Claude\'s last answers still name exact files: the session is healthy, only space is short.', null), 200000, full209);
  }
  var good209 = 'Done: mobile/screens/RescheduleScreen.tsx uses SlotPicker from packages/shared/ui and the useClinicSlots hook, same as BookingScreen.tsx. Test added in RescheduleScreen.test.tsx.';
  var vague209 = 'I have created the reschedule screen following typical React Native patterns, with a date picker and a confirm button.';
  var s209 = {
    id: 'm7-s2-09', who: 'Engineer', labels: CC, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Context is nearly full, mostly old test output. Claude\'s answers are <b>still accurate and name specific files</b>. Nothing changed outside the session.' },
      { id: 'B', label: 'Decider changed', desc: 'Claude\'s answers have <b>turned vague and contradictory</b>: "typical patterns", and a prop name it already rejected comes back.' }
    ],
    runs: {
      A: [
        { steps: [full209Step(),
            S('loop', 'Claude writes NOTES.md with its decisions', 'Option A. Claude chooses what to write down.', '# Screens session notes\n- use SlotPicker from packages/shared/ui\n- data via useClinicSlots\n- done: Booking, Cancel, ClinicList\n- todo: Reschedule, Waitlist'),
            S('loop', 'Engineer opens a new session that reads NOTES.md', '', '$ claude\n> Read NOTES.md and continue with the remaining screens.'),
            M(S('ctx', 'New session context', 'Lean, but the working detail is gone: why SlotPicker takes clinicTz, which test helpers were fixed, the edits Claude had in view.', null), 200000, [P('system + CLAUDE.md', 12000, 'sys'), P('NOTES.md', 1200, 'new'), P('lost working detail', 0, 'drop')]),
            S('tool', 'Claude re-reads 7 files to rebuild what it knew', 'The old session had all of this and was still answering well.', 'Read mobile/screens/BookingScreen.tsx\nRead packages/shared/ui/SlotPicker.tsx\nRead mobile/hooks/useClinicSlots.ts\n\u2026 (4 more)', 'warn'),
            S('loop', 'Claude generates the Reschedule screen', '', good209)],
          outcome: { ok: true, warn: true, text: 'It works, at the cost of a new session and re-reading files. Answers were still specific, so there was no degradation to escape; only space was short.' }, rate: 0.92 },
        { steps: [full209Step(),
            S('file', 'New subagent for test runs', 'Option B. It will return only failing tests and causes.', '.claude/agents/test-runner.md\n---\nname: test-runner\ndescription: Run jest and return only failing tests and their causes.\n---'),
            S('ctx', 'The 121k of old test output is still in the window', 'The subagent helps future runs. It removes nothing already there.', null, 'bad'),
            S('loop', 'Next screen: context hits the limit mid-generation', '', 'Context low (2% remaining). Auto-compact triggered.', 'bad')],
          outcome: { ok: false, text: 'A good habit for later runs, but it does not free the context that is already nearly full.' }, rate: 0.5 },
        { steps: [full209Step(),
            S('loop', 'Engineer resumes the session in a new terminal', 'Option C.', '$ claude --resume screens-sprint'),
            M(S('ctx', 'Resumed session context', 'Resuming reloads the same conversation: same 187k.', null), 200000, full209.slice(0, 1).concat([P('test output, runs 1-9 (reloaded)', 121000, 'drop')]).concat(full209.slice(2))),
            S('loop', 'Nothing is freed', '', 'Context low (6% remaining).', 'bad')],
          outcome: { ok: false, text: 'A new terminal does not mean a new context. --resume brings back the same full conversation.' }, rate: 0.3 },
        { steps: [full209Step(),
            S('loop', 'Engineer runs /compact', 'Option D. Claude condenses the conversation so far, in this same session.', '> /compact keep screen decisions and file paths'),
            M(S('ctx', 'Context after /compact', 'Old test logs collapse to a line. The decisions and file paths stay in the summary.', null), 200000, [P('system + CLAUDE.md', 12000, 'sys'), P('compact summary: decisions, files, todo', 8000, 'keep'), P('test logs (dropped)', 300, 'drop')]),
            S('loop', 'Claude generates the Reschedule screen', 'Same session, same decisions, room to work.', good209, 'ok'),
            S('cust', 'Engineer sees a specific, correct answer', '', good209, 'ok')],
          outcome: { ok: true, text: 'The session was healthy and current; only space was short. /compact frees it and keeps the work in place.' }, rate: 0.97 }
      ],
      B: [
        { steps: [full209Step('Same fill, but the session has degraded: two answers contradict earlier decisions.'),
            S('loop', 'Claude writes NOTES.md; the engineer corrects it', 'Option A. The notes become a clean, checked record of the decisions.', '- use SlotPicker (NOT DatePickerModal, rejected on day 1)\n- times always in clinic timezone (clinicTz prop)'),
            M(S('ctx', 'Fresh session reads NOTES.md', 'No contradictions carried over.', null), 200000, [P('system + CLAUDE.md', 12000, 'sys'), P('NOTES.md (checked)', 1400, 'new')]),
            S('loop', 'Claude generates the Reschedule screen', '', good209, 'ok')],
          outcome: { ok: true, text: 'Answers had degraded, so a fresh start from a written, checked record is the fix. This is the world where the runner-up wins.' }, rate: 0.93 },
        { steps: [full209Step('Same fill; answers degraded.'), S('file', 'Test-runner subagent added', '', 'test-runner.md'), S('loop', 'Claude still answers vaguely', '', vague209, 'bad')],
          outcome: { ok: false, text: 'Future runs get leaner; the muddled context stays.' }, rate: 0.4 },
        { steps: [full209Step('Same fill; answers degraded.'), S('loop', 'claude --resume screens-sprint', '', 'same 187k reloaded', 'bad'), S('loop', 'Claude still answers vaguely', '', vague209, 'bad')],
          outcome: { ok: false, text: 'Resuming reloads the same muddled conversation.' }, rate: 0.3 },
        { steps: [full209Step('Same fill; answers degraded.'),
            S('loop', '/compact', '', '> /compact'),
            M(S('ctx', 'The compact summary is built from the muddled conversation', 'Both prop names survive as "decided". The contradiction is now compressed, not removed.', null), 200000, [P('system + CLAUDE.md', 12000, 'sys'), P('compact summary (both SlotPicker and DatePickerModal)', 8000, 'drop')]),
            S('loop', 'Claude generates the screen with the rejected component', '', 'RescheduleScreen.tsx uses DatePickerModal.', 'warn')],
          outcome: { ok: false, text: 'Compacting frees space but carries the confusion forward. Degraded answers need a fresh start from a clean record.' }, rate: 0.7 }
      ]
    }
  };

  /* ============================================================ m7-s2-10 lost in the middle */
  var digest210 = 'KEY RULES (read first)\n1. Late cancellation: within 24h of the slot -> charge 50% fee.\n2. Max 2 active bookings per patient.\n3. Slots lock 10 min while booking is in progress.\n4. Clinic timezone for all times.';
  var used210 = 'Claude\'s code used: overview (start), acceptance criteria (end). Missed: late-cancellation window, 2-booking cap (middle).';
  function spec210(note, lead) {
    var parts = [P('system + CLAUDE.md', 8000, 'sys')];
    if (lead) parts.push(lead);
    return M(S('ctx', 'Spec in the window', note, null), 200000, parts);
  }
  var s210 = {
    id: 'm7-s2-10', who: 'Engineer', labels: CC, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'The spec is 38k tokens and <b>fits easily</b> in a 200k window. The missed rules sit in the <b>middle</b>.' },
      { id: 'B', label: 'Decider changed', desc: 'The spec is the full product spec, <b>260k tokens</b>: too large for one context.' }
    ],
    runs: {
      A: [
        { steps: [S('loop', 'Engineer adds a key-rules list on top', 'Option A. The full spec follows under clear headings.', digest210, 'ok'),
            M(S('ctx', 'Window: key rules at the start, spec below', 'The rules that were missed now also sit where attention is strongest.', null), 200000, [P('system + CLAUDE.md', 8000, 'sys'), P('START: key rules (used)', 400, 'new'), P('## Overview', 3000, 'keep'), P('## Booking / ## Cancellation / ## Payments (headed)', 31000, 'keep'), P('END: ## Acceptance criteria', 4000, 'keep')]),
            S('loop', 'Claude writes the endpoint', '', 'if (slotStart - now < 24 * HOUR) fee = price * 0.5;\nif (activeBookings(patientId) >= 2) throw new BookingLimitError();', 'ok'),
            S('cust', 'Engineer reviews: all rules present', '', 'Late-cancel fee: yes. 2-booking cap: yes. Acceptance criteria: 9/9.', 'ok')],
          outcome: { ok: true, text: 'Models read the start and end of long input reliably and can skim the middle. Lifting the key rules to the top under headings fixes the position problem.' }, rate: 0.95 },
        { steps: [S('loop', 'Spec split into 6 sections, one pass each', 'Option B. Each pass sees one short section. But the whole spec is 38k of a 200k window: it already fit.', '$ for s in overview booking cancellation payments notifications acceptance; do claude -p "Implement $s" ; done'),
            X(S('loop', '6 section passes + 1 integration pass', 'Each pass reads its section well. Then an integration pass stitches six partial implementations together.', null, 'warn'), { table: { head: ['Approach', 'Passes', 'Input tokens', 'Merge conflicts'], rows: [['One prompt', '1', '38k', '0'], ['Split + integrate', '7', '61k', '3']] } }),
            S('loop', 'Integration pass resolves 3 conflicts in BookingService', 'The cancellation pass and the payments pass each wrote their own fee logic.', 'merge: keep cancellation fee from pass 3', 'warn'),
            S('cust', 'Engineer reviews: rules present, after extra work', '', 'Late-cancel fee: yes. Seven passes and three merge fixes.')],
          outcome: { ok: true, warn: true, text: 'It works, but splitting is for input too large for one context. This spec fits easily; the miss was about position, not size.' }, rate: 0.9 },
        { steps: [S('loop', 'Acceptance criteria moved to the top', 'Option C.', '## Acceptance criteria\n\u2026\n## Overview\n\u2026'),
            M(S('ctx', 'Window: the middle is unchanged', 'The criteria were already honoured. The cancellation rules are still in the middle.', null), 200000, [P('system + CLAUDE.md', 8000, 'sys'), P('START: acceptance criteria (used)', 4000, 'keep'), P('overview', 3000, 'keep'), P('MIDDLE: cancellation, booking cap (missed)', 31000, 'drop')]),
            S('loop', 'Claude writes the endpoint', '', 'cancelBooking(id) { return db.booking.delete({ where: { id } }); }   // no late fee', 'bad')],
          outcome: { ok: false, text: 'Right idea, wrong content. Moving what was already followed leaves the missed rules buried.' }, rate: 0.6 },
        { steps: [S('loop', 'Claude summarises the spec first', 'Option D.', 'Summary: patients book clinic slots; cancellations are allowed subject to policy; limits apply to bookings.'),
            M(S('ctx', 'Window: summary replaces the spec', 'The 24h window and the 2-booking cap became "subject to policy" and "limits apply".', null), 200000, [P('system + CLAUDE.md', 8000, 'sys'), P('summary', 1500, 'keep'), P('lost: 24h window, cap of 2', 0, 'drop')]),
            S('loop', 'Claude writes the endpoint', '', 'const LATE_CANCEL_HOURS = 48; // assumed', 'bad')],
          outcome: { ok: false, text: 'Summaries compress exactly the small details being missed.' }, rate: 0.55 }
      ],
      B: [
        { steps: [S('loop', 'Key rules on top, full 260k spec below', '', digest210),
            S('block', 'Blocked: the input does not fit', 'Layout cannot help when the input is larger than the window.', 'API Error: prompt is too long: 268412 tokens > 200000 maximum', 'bad')],
          outcome: { ok: false, text: 'Lifting key rules to the top fixes position, not size. This input cannot be sent at all.' }, rate: 0 },
        { steps: [S('loop', 'Spec split by section, one pass each', 'Option B.', '6 section passes + 1 integration pass'),
            M(S('ctx', 'Cancellation pass context', 'Each section fits with room to spare, so nothing sits in a buried middle.', null), 200000, [P('system + CLAUDE.md', 8000, 'sys'), P('## Cancellation section', 41000, 'keep')]),
            S('loop', 'Integration pass joins the code, not the spec', '', 'BookingService.ts: fee logic from the cancellation pass', 'ok'),
            S('cust', 'Engineer reviews: all rules present', '', 'Late-cancel fee: yes. 2-booking cap: yes.', 'ok')],
          outcome: { ok: true, text: 'When the input is too large for one context, per-section passes plus an integration pass is the way through. This is the world where the runner-up wins.' }, rate: 0.92 },
        { steps: [S('loop', 'Acceptance criteria moved to the top', '', ''), S('block', 'Blocked: the input does not fit', '', 'prompt is too long', 'bad')],
          outcome: { ok: false, text: 'Reordering does not change the size.' }, rate: 0 },
        { steps: [S('loop', 'Claude summarises 260k into 3k', '', 'cancellations allowed subject to policy'), S('loop', 'Claude writes the endpoint', '', 'no late fee', 'bad')],
          outcome: { ok: false, text: 'It fits now, but the summary dropped the rules.' }, rate: 0.5 }
      ]
    }
  };

  /* ============================================================ m7-s3-09 lost in the middle (synthesis input) */
  var WHO3 = 'Committee';
  var cover309 = function (n) { return 'Summary cites ' + n + ' of 24 papers.'; };
  var s309 = {
    id: 'm7-s3-09', who: WHO3, labels: { loop: 'Coordinator' }, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Findings from 24 papers, <b>already trimmed</b> to a few fields each (about 600 tokens), in the order found. The middle papers go missing.' },
      { id: 'B', label: 'Decider changed', desc: 'Each finding arrives as the <b>full analysis output: 40 fields, about 4k tokens</b>, mostly methods boilerplate, funding and affiliations.' }
    ],
    runs: {
      A: [
        { steps: [S('loop', 'Coordinator wraps the findings in a case-facts block', 'Option A. The block is refreshed after each paper, then sent to synthesis.', '<case_facts>\npaper 1: \u2026\npaper 2: \u2026\n\u2026 paper 24: \u2026\n</case_facts>'),
            M(S('ctx', 'Synthesis input: same list, same order', 'A new wrapper, the same 24 findings in arrival order. Papers 5-20 are still in the middle.', null), 200000, [P('system', 2000, 'sys'), P('START: papers 1-4 (used)', 2400, 'keep'), P('MIDDLE: papers 5-20 (often missed)', 9600, 'drop'), P('END: papers 21-24 (used)', 2400, 'keep')]),
            S('sub', 'Synthesis returns', 'The block guards facts across many turns. This is one input, read once.', cover309(10), 'bad')],
          outcome: { ok: false, text: 'A case-facts block protects details across a long conversation. It does not change how one long input is read.' }, rate: 0.5 },
        { steps: [M(S('ctx', 'Synthesis input as before', '', null), 200000, [P('system', 2000, 'sys'), P('START: papers 1-4', 2400, 'keep'), P('MIDDLE: papers 5-20 (missed)', 9600, 'drop'), P('END: papers 21-24', 2400, 'keep')]),
            S('sub', 'Synthesis draft', '', cover309(10), 'bad'),
            S('sub', 'Second synthesis instance reviews the draft', 'Option B. It lists 14 papers left out.', 'Missing: papers 5, 6, 7, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20', 'warn'),
            S('sub', 'Synthesis re-drafts with the list', 'An extra review and a re-draft on every run.', cover309(22), 'ok')],
          outcome: { ok: true, warn: true, text: 'Review catches the omissions after the fact. It treats the symptom and doubles the synthesis work on every run.' }, rate: 0.9 },
        { steps: [S('loop', 'Coordinator trims each finding further', 'Option C. There is little left to cut: 600 tokens become 520.', { kept: ['paper', 'outcome', 'effect_size', 'section'], dropped: ['population'] }, 'warn'),
            M(S('ctx', 'Synthesis input: barely shorter, same order', 'The middle is still the middle.', null), 200000, [P('system', 2000, 'sys'), P('START: papers 1-4 (used)', 2100, 'keep'), P('MIDDLE: papers 5-20 (still missed)', 8300, 'drop'), P('END: papers 21-24 (used)', 2100, 'keep')]),
            S('sub', 'Synthesis returns', 'And the dropped population field was one the committee needed.', cover309(11), 'bad')],
          outcome: { ok: false, text: 'Trimming fixes bloated input. These findings were already trimmed; the losses follow position, not size.' }, rate: 0.5 },
        { steps: [S('loop', 'Coordinator builds a digest and headings', 'Option D. A short list of key findings first; the detail grouped under outcome headings.', 'KEY FINDINGS\n- 30-day readmission down 18% (papers 3, 9, 14, 22)\n- no rise in falls (papers 7, 12, 16)\n\u2026\n## Readmission\n## Adverse events\n## Length of stay'),
            M(S('ctx', 'Synthesis input: digest first, detail under headings', 'Every paper is now named at the start, and the headings break the middle into labelled parts.', null), 200000, [P('system', 2000, 'sys'), P('START: digest naming all 24 papers', 1200, 'new'), P('## Readmission', 4800, 'keep'), P('## Adverse events', 4800, 'keep'), P('## Length of stay', 4800, 'keep')]),
            S('sub', 'Synthesis returns', '', cover309(24), 'ok'),
            S('cust', 'Committee reviewers check coverage', '', 'Middle papers now cited, each with paper and section.', 'ok')],
          outcome: { ok: true, text: 'Models attend best to the start and end. A leading digest and clear headings keep the middle from being lost.' }, rate: 0.95 }
      ],
      B: [
        { steps: [S('loop', 'Findings wrapped in a case-facts block', '', '<case_facts> 24 x 4k </case_facts>'),
            M(S('ctx', 'Synthesis input', '', null), 200000, [P('system', 2000, 'sys'), P('24 full outputs (mostly irrelevant fields)', 96000, 'drop')]),
            S('sub', 'Synthesis returns', '', cover309(9), 'bad')],
          outcome: { ok: false, text: 'Same bloated input, new wrapper.' }, rate: 0.4 },
        { steps: [S('sub', 'Draft, then a second instance lists omissions', '', cover309(9) + ' Reviewer lists 15 missing.', 'warn'), S('sub', 'Re-draft through the same 96k of noise', '', cover309(17), 'bad')],
          outcome: { ok: false, text: 'Review finds misses but cannot cut the noise causing them.' }, rate: 0.6 },
        { steps: [S('loop', 'Coordinator trims each output to the fields synthesis uses', 'Option C. 4k becomes 600 per paper.', { kept: ['paper', 'outcome', 'effect_size', 'population', 'section'], dropped: '35 fields: methods boilerplate, funding, affiliations' }, 'ok'),
            M(S('ctx', 'Synthesis input after trimming', '96k becomes 14k. The relevant findings are no longer spread thin through noise.', null), 200000, [P('system', 2000, 'sys'), P('24 trimmed findings', 14400, 'keep'), P('irrelevant fields (cut)', 0, 'drop')]),
            S('sub', 'Synthesis returns', '', cover309(23), 'ok')],
          outcome: { ok: true, text: 'Here the input was bloated with irrelevant fields, so trimming is the first fix. This is the world where the runner-up wins.' }, rate: 0.93 },
        { steps: [S('loop', 'Digest and headings over the full outputs', '', 'KEY FINDINGS \u2026'),
            M(S('ctx', 'Synthesis input', 'The digest helps, but 80k of irrelevant fields still sit under every heading.', null), 200000, [P('system', 2000, 'sys'), P('digest', 1200, 'new'), P('full outputs under headings', 96000, 'drop')]),
            S('sub', 'Synthesis returns', 'Better, at six times the input tokens of a trimmed run.', cover309(21), 'warn')],
          outcome: { ok: true, warn: true, text: 'Structure helps, but the noise should be cut first.' }, rate: 0.9 }
      ]
    }
  };

  /* ============================================================ m7-s4-08 resume a named session */
  var sess = 'Sessions\n  billing-audit     last week   "trace invoice rounding"\n  onboarding-docs   yesterday   "rewrite README setup steps"   <- most recent\n  lesson-api        2 weeks ago';
  var noChange = '$ git log --since="7 days ago" -- app/models/invoice.rb app/models/line_item.rb app/services/billing/\n(no commits)';
  var changed = '$ git log --since="7 days ago" -- app/models/invoice.rb app/models/line_item.rb app/services/billing/\na41c9e2  Use half-even rounding in Invoice#total_cents; move tax to LineItem#tax_cents (PR #2210)';
  var resumed = [P('system + CLAUDE.md', 10000, 'sys'), P('reads: invoice.rb, line_item.rb, rounding.rb', 31000, 'keep'), P('findings + open hypothesis', 6000, 'keep')];
  var next408 = 'Picking up where we stopped: Invoice#total_cents rounds each line with round(2) before summing (invoice.rb:88). Next I check LineItem#discount_cents, the last place I suspected double rounding.';
  var s408 = {
    id: 'm7-s4-08', who: 'Engineer', labels: CC, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'The billing-audit session read the billing files last week. <b>Nobody has changed the billing code since.</b> The most recent session is unrelated.' },
      { id: 'B', label: 'Decider changed', desc: 'Since last week a teammate <b>merged a rounding refactor</b> into the files billing-audit read.' }
    ],
    runs: {
      A: [
        { steps: [S('loop', 'Engineer starts a new session and pastes a summary', 'Option A.', '$ claude\n> Context: last week we traced invoice rounding. Lines are rounded before summing. Suspect discount rounding. Continue.'),
            M(S('ctx', 'New session context', 'Only what the summary says. Line numbers, the exact code read and the open hypothesis detail are gone.', null), 200000, [P('system + CLAUDE.md', 10000, 'sys'), P('pasted summary', 900, 'new'), P('last week\'s reads (not here)', 0, 'drop')]),
            S('tool', 'Claude re-reads the billing files', 'Billing code is unchanged, so last week\'s reads were still accurate. This is repeat work.', noChange + '\nRead app/models/invoice.rb\nRead app/models/line_item.rb\nRead app/services/billing/rounding.rb', 'warn'),
            S('loop', 'Claude continues', '', next408)],
          outcome: { ok: true, warn: true, text: 'A fresh start with a summary is for stale context. Nothing changed, so this throws away accurate work and re-reads files.' }, rate: 0.92 },
        { steps: [S('loop', 'Engineer runs claude --continue', 'Option B. --continue opens the most recent session.', sess),
            M(S('ctx', 'Context loaded: onboarding-docs', 'The wrong conversation: README edits, no billing work.', null), 200000, [P('system + CLAUDE.md', 10000, 'sys'), P('onboarding-docs conversation', 22000, 'drop')]),
            S('loop', 'Claude has no rounding work to pick up', '', 'I don\'t see earlier work on invoice rounding in this session. Shall I start investigating?', 'bad')],
          outcome: { ok: false, text: '--continue reopens the most recent session, which is the unrelated one.' }, rate: 0 },
        { steps: [S('loop', 'Engineer runs /memory in a new session', 'Option C.', '> /memory'),
            S('file', '/memory lists memory files', 'CLAUDE.md files, not conversations.', 'Memory files\n  ~/.claude/CLAUDE.md\n  ./CLAUDE.md\n  ./app/CLAUDE.md', 'bad'),
            M(S('ctx', 'Context', 'No billing-audit conversation was restored.', null), 200000, [P('system + CLAUDE.md', 10000, 'sys')])],
          outcome: { ok: false, text: '/memory shows which memory files are loaded. It does not restore a past conversation.' }, rate: 0 },
        { steps: [S('loop', 'Engineer runs claude --resume billing-audit', 'Option D: the session by name.', sess + '\n\n$ claude --resume billing-audit'),
            M(S('ctx', 'Context restored: billing-audit', 'Every file read, finding and open question from last week.', null), 200000, resumed),
            S('tool', 'Are those reads still current?', 'No commits to the billing code, so last week\'s tool results are still accurate.', noChange, 'ok'),
            S('loop', 'Claude continues exactly where it stopped', '', next408, 'ok')],
          outcome: { ok: true, text: '--resume with the name reopens that exact conversation. The code is unchanged, so its findings are still true.' }, rate: 1 }
      ],
      B: [
        { steps: [S('loop', 'New session with a structured summary', 'Option A.', '> Findings so far: \u2026 Note: PR #2210 changed rounding since. Re-read the billing files first.'),
            S('tool', 'Claude reads the current billing files', '', changed + '\nRead app/models/invoice.rb (new version)\nRead app/models/line_item.rb (new version)', 'ok'),
            M(S('ctx', 'New session context: current code only', '', null), 200000, [P('system + CLAUDE.md', 10000, 'sys'), P('summary', 900, 'new'), P('current reads', 29000, 'keep')]),
            S('loop', 'Claude continues on the new code', '', 'Invoice#total_cents now uses half-even rounding (invoice.rb:91). Tax moved to LineItem#tax_cents; checking that for double rounding next.', 'ok')],
          outcome: { ok: true, text: 'The files changed, so old tool results are stale. A fresh session with a structured summary reads the current code. This is the world where the runner-up wins.' }, rate: 0.95 },
        { steps: [S('loop', 'claude --continue', '', 'opens onboarding-docs'), S('loop', 'Wrong conversation', '', 'No billing work here.', 'bad')],
          outcome: { ok: false, text: 'Still the most recent, unrelated session.' }, rate: 0 },
        { steps: [S('file', '/memory lists memory files', '', './CLAUDE.md', 'bad')],
          outcome: { ok: false, text: 'Still no conversation restored.' }, rate: 0 },
        { steps: [S('loop', 'claude --resume billing-audit', '', ''),
            M(S('ctx', 'Context restored, but stale', 'The reads are of last week\'s code.', null), 200000, [P('system + CLAUDE.md', 10000, 'sys'), P('reads of OLD invoice.rb, line_item.rb', 31000, 'drop'), P('findings', 6000, 'keep')]),
            S('tool', 'The code changed since', '', changed, 'warn'),
            S('loop', 'Claude reasons from the old code', '', 'Invoice#total_cents rounds each line with round(2) (invoice.rb:88)\u2026   <- that line no longer exists', 'bad')],
          outcome: { ok: false, text: 'Resuming brings back tool results that no longer match the files.' }, rate: 0.6 }
      ]
    }
  };

  /* ============================================================ m7-s3-05 fixed pipeline vs adaptive */
  var fixedChain = ['efficacy: search -> analyze', 'safety: search -> analyze', 'cost: search -> analyze', 'guideline status: search -> analyze', 'integration pass'];
  var s305 = {
    id: 'm7-s3-05', who: WHO3, labels: { loop: 'Coordinator' }, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Four fixed template sections, <b>independent</b> of each other, and auditors must <b>replay every run step by step</b>.' },
      { id: 'B', label: 'Decider changed', desc: 'An <b>open-ended</b> question: "Why did readmissions rise after the 2025 protocol change?" The next step depends on what is found.' }
    ],
    runs: {
      A: [
        { steps: [S('loop', 'Coordinator runs a fixed chain', 'Option A. The same steps, in the same order, every time.', fixedChain.join('\n')),
            S('sub', 'Four section subagents run their fixed steps', 'No section waits on another\'s findings.', { efficacy: 'done', safety: 'done', cost: 'done', guideline_status: 'done' }),
            S('sub', 'One integration pass joins the four outputs', '', 'Evidence summary ES-0412: four sections, 31 citations.'),
            X(S('cust', 'Auditor replays three runs', 'Same structure, step for step.', null, 'ok'), { table: { head: ['Run', 'Steps', 'Order', 'Replay'], rows: [['ES-0410', '9', 'E S C G I', 'match'], ['ES-0411', '9', 'E S C G I', 'match'], ['ES-0412', '9', 'E S C G I', 'match']] } })],
          outcome: { ok: true, text: 'Steps known in advance and independent: a fixed pipeline is predictable and auditable.' }, rate: 1 },
        { steps: [S('loop', 'Coordinator plans from early findings', 'Option B. After each result it decides what to add.', 'efficacy found a subgroup signal -> add "elderly subgroup" subtask\nsafety quiet -> skip second search'),
            S('sub', 'Subtasks vary from run to run', 'Each run follows what it happened to find first.', { 'ES-0410': 'added elderly subgroup', 'ES-0411': 'added cost-model check', 'ES-0412': 'no additions' }),
            X(S('cust', 'Auditor replays three runs', 'The structure differs every time. The steps never needed to change, and audit needs repeatable runs.', null, 'bad'), { table: { head: ['Run', 'Steps', 'Order', 'Replay'], rows: [['ES-0410', '13', 'E E2 S C G I', 'differs'], ['ES-0411', '11', 'E S C C2 G I', 'differs'], ['ES-0412', '9', 'E S C G I', 'match']] } })],
          outcome: { ok: false, text: 'Adaptive decomposition fits work where findings decide the next step. Here nothing does, and the varying plan breaks step-by-step replay.' }, rate: 0.6 },
        { steps: [S('sub', 'Four sections drafted', '', 'draft v1'),
            S('loop', 'Coordinator checks for gaps and re-delegates', 'Option C. How many loops depends on each draft.', 'cost thin -> re-delegate\nsafety thin -> re-delegate'),
            X(S('cust', 'Auditor replays three runs', 'Run length varies with each draft.', null, 'bad'), { table: { head: ['Run', 'Steps', 'Order', 'Replay'], rows: [['ES-0410', '12', 'E S C G R:C I', 'differs'], ['ES-0411', '15', 'E S C G R:C R:S I', 'differs'], ['ES-0412', '10', 'E S C G I', 'differs'] ] } })],
          outcome: { ok: false, text: 'A refinement loop fills coverage gaps, but makes run length vary, which works against step-by-step replay.' }, rate: 0.7 },
        { steps: [S('loop', 'Coordinator sizes each request and picks subagents', 'Option D. Every request has the same four sections, so there is nothing to choose.', 'request ES-0412 looks efficacy-focused -> invoke efficacy, safety, guideline'),
            S('sub', 'Cost section skipped on one run', 'An extra model decision that can only go wrong here.', 'ES-0412: cost section missing', 'bad'),
            S('cust', 'Committee template check fails', '', 'Template requires 4 sections; found 3.', 'bad')],
          outcome: { ok: false, text: 'Dynamic selection suits requests of varying size. These all have the same shape.' }, rate: 0.8 }
      ],
      B: [
        { steps: [S('loop', 'Coordinator runs the fixed chain', '', fixedChain.join('\n')),
            S('sub', 'Efficacy analysis notes a lead', 'One trial changed dosing for patients with renal impairment.', 'Possible driver: dosing change in renal subgroup (Trial NCT-5521)'),
            S('loop', 'The chain has no step to follow the lead', 'The next fixed step is safety.', 'next: safety', 'bad'),
            S('cust', 'Committee gets four generic sections', 'The question "why" is not answered.', 'Readmission driver: not identified.', 'bad')],
          outcome: { ok: false, text: 'A fixed pipeline cannot follow a finding it did not plan for.' }, rate: 0.4 },
        { steps: [S('sub', 'First search returns a lead', '', 'Possible driver: dosing change in renal subgroup (Trial NCT-5521)'),
            S('loop', 'Coordinator adds subtasks from the finding', 'Option B. The next step comes from what was found.', 'add: registry search for renal-subgroup readmissions\nadd: analyze NCT-5521 dosing section', 'ok'),
            S('sub', 'New subtasks confirm the driver', '', 'Readmissions rose in the eGFR < 45 subgroup after the dose change (NCT-5521, s4.2).'),
            S('cust', 'Committee gets an answer with citations', '', 'Driver identified: renal-subgroup dosing, cited to paper and section.', 'ok')],
          outcome: { ok: true, text: 'When the next step depends on what was found, adaptive decomposition is the right fit. This is the world where the runner-up wins.' }, rate: 0.92 },
        { steps: [S('sub', 'Four template sections drafted', '', 'draft v1'), S('loop', 'Gaps re-delegated within the same four sections', 'The lead is outside the template.', 're-delegate: cost', 'bad')],
          outcome: { ok: false, text: 'Refining the template sections does not chase a new lead.' }, rate: 0.5 },
        { steps: [S('loop', 'Coordinator sizes the request and picks from fixed subagents', '', 'efficacy + safety'), S('sub', 'No subagent follows the renal lead', '', 'driver: not identified', 'bad')],
          outcome: { ok: false, text: 'Choosing which fixed subagents to call still cannot add new subtasks from findings.' }, rate: 0.5 }
      ]
    }
  };

  /* ============================================================ m7-s2-03 plan mode for an open design choice */
  var survey203 = 'Grep "apiClient\\." mobile/  ->  47 call sites in 23 screens\nRead mobile/api/client.ts\nRead server/openapi.yaml';
  var planText = 'PLAN (no files changed)\nOption 1: orval -> React Query hooks per endpoint. Screens switch from apiClient.get() in useEffect to useGetAppointments(). 23 screens restructured.\nOption 2: openapi-fetch -> typed client.GET("/appointments/{id}"). Mechanical swap at 47 call sites; screens keep their shape.\nShared concern: auth refresh in client.ts must move to a middleware either way.\nRecommend: decide with the team before any edit.';
  var s203 = {
    id: 'm7-s2-03', who: 'Engineer', labels: CC, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'The team has <b>not chosen</b> between orval (hooks) and openapi-fetch (typed client), and each shapes every call differently.' },
      { id: 'B', label: 'Decider changed', desc: 'The team <b>already chose openapi-fetch</b> (recorded in docs/adr/012). The approach is settled.' }
    ],
    runs: {
      A: [
        { steps: [S('loop', 'Claude edits mobile/screens/appointments with orval', 'Option A. The "likelier" library is a guess.', 'Edit AppointmentList.tsx, AppointmentDetail.tsx, \u2026 (6 files)\nnpm test -- appointments  ->  passing'),
            S('loop', 'Pattern rolled out to 4 more folders', 'Each folder copies the hooks style from the spike.', 'clinics/, patients/, waitlist/, settings/  ->  31 files edited'),
            S('cust', 'Team meeting picks openapi-fetch', 'The tests passed, but they checked the code, not the choice.', '5 folders, 37 files to redo.', 'bad')],
          outcome: { ok: false, text: 'A spike with tests suits a migration whose target is settled. With the library undecided, it bakes in a guess and later folders follow it.' }, rate: 0.5 },
        { steps: [S('loop', 'Engineer enters plan mode (Shift+Tab twice)', 'Option B. Claude may read and search, but not edit.', '\u23f8 plan mode on'),
            M(S('tool', 'Claude surveys the call sites and both libraries', 'Reading only.', survey203), 200000, [P('system + CLAUDE.md', 11000, 'sys'), P('client.ts, openapi.yaml, call sites', 38000, 'tool')]),
            S('loop', 'Claude proposes both approaches', '', planText, 'ok'),
            S('cust', 'Team agrees: openapi-fetch', 'The decision is made before any file changes.', 'Approved: Option 2, auth refresh as middleware.', 'ok'),
            S('loop', 'Edits begin from the agreed design', '', 'Edit mobile/api/client.ts \u2026')],
          outcome: { ok: true, text: 'An open choice with many files touched is what plan mode is for: explore, compare and agree a design before edits.' }, rate: 0.95 },
        { steps: [S('sub', 'Explore subagent maps call sites and both libraries', 'Option C. The main context stays clean.', 'Summary: 47 call sites; orval needs screen restructuring, openapi-fetch is a swap.'),
            M(S('ctx', 'Main context gets only the summary', '', null), 200000, [P('system + CLAUDE.md', 11000, 'sys'), P('Explore summary', 1800, 'new')]),
            S('loop', 'Claude goes straight to edits', 'No design was agreed. It picks orval because the hooks look tidier.', 'Edit mobile/api/client.ts\nEdit mobile/screens/appointments/*.tsx \u2026', 'bad')],
          outcome: { ok: false, text: 'Exploring in a subagent keeps the main context clean, but goes straight to edits with no agreed design.' }, rate: 0.6 },
        { steps: [S('loop', 'Claude interviews the engineer', 'Option D.', 'Q: Does the old client retry on 401?  A: Yes, once after refresh.\nQ: Any offline queue?  A: Only for check-in.'),
            S('loop', 'Claude makes direct edits', 'Edge cases are captured. Which library to use is still a guess.', 'Edit 23 screens using orval hooks', 'bad')],
          outcome: { ok: false, text: 'Interviewing gathers requirements. The open question is a design choice that needs the code surveyed and compared.' }, rate: 0.55 }
      ],
      B: [
        { steps: [S('file', 'docs/adr/012: use openapi-fetch', 'The choice is settled.', 'Decision: openapi-fetch typed client. Auth refresh as middleware.'),
            S('loop', 'Claude edits mobile/screens/appointments directly', 'Option A.', 'Edit 6 files\nnpm test -- appointments  ->  passing', 'ok'),
            S('loop', 'Pattern rolled out folder by folder, tests each time', '', '5 folders, 37 files, all tests passing', 'ok')],
          outcome: { ok: true, text: 'With the library chosen, nothing is left to design. Incremental direct edits with tests are the efficient path. This is the world where the runner-up wins.' }, rate: 0.95 },
        { steps: [S('loop', 'Plan mode', '', '\u23f8 plan mode on'), S('loop', 'Claude compares orval vs openapi-fetch', 'The ADR already decided this.', planText, 'warn'), S('loop', 'Edits begin', '', 'Edit \u2026')],
          outcome: { ok: true, warn: true, text: 'Works, but it re-opens a settled choice before starting.' }, rate: 0.95 },
        { steps: [S('sub', 'Explore subagent maps the call sites', '', '47 call sites'), S('loop', 'Claude edits all 23 screens in one go', 'No per-folder tests along the way.', 'Edit 37 files; 4 tests fail at the end', 'warn')],
          outcome: { ok: true, warn: true, text: 'Gets there, with a big-bang edit and a late test run.' }, rate: 0.9 },
        { steps: [S('loop', 'Interview about edge cases', '', 'retry on 401, offline queue'), S('loop', 'Direct edits with openapi-fetch', '', 'Edit 37 files', 'warn')],
          outcome: { ok: true, warn: true, text: 'Fine, though the questions add little once the library is fixed.' }, rate: 0.9 }
      ]
    }
  };

  /* ============================================================ m7-s4-05 plan mode for a multi-approach migration */
  var map405 = { head: ['Old-library feature', 'Jobs', 'Solid Queue equivalent'], rows: [['Sidekiq::Batch', '7 (report exports, streak recalcs)', 'none: redesign'], ['sidekiq-unique-jobs', '3', 'concurrency limits'], ['sidekiq_retry_in', '9', 'retry_on wait:'], ['plain perform_async', '45', 'perform_later']] };
  var s405 = {
    id: 'm7-s4-05', who: 'Engineer', labels: CC, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Moving 64 jobs from Sidekiq to Solid Queue. Engineers <b>disagree on job-by-job vs all at once</b>, and <b>nobody has mapped</b> which jobs use Sidekiq-only features.' },
      { id: 'B', label: 'Decider changed', desc: 'Every other job is already on Solid Queue with a documented pattern. One small job, <code>LessonReminderJob</code>, remains, and it uses <b>no Sidekiq-only features</b>.' }
    ],
    runs: {
      A: [
        { steps: [S('loop', 'Claude writes specs for all 64 jobs first', 'Option A.', 'Create spec/jobs/*_spec.rb (64 files) using Sidekiq::Testing.fake! and perform_async assertions'),
            S('loop', 'Claude converts jobs until specs pass', 'The specs assert Sidekiq APIs, so each conversion rewrites its spec too.', 'ReportExportJob: Sidekiq::Batch has no equivalent; spec cannot pass', 'bad'),
            S('cust', 'Strategy still undecided', 'Converting started before job-by-job vs all-at-once was chosen.', '64 specs written against the library being removed.', 'bad')],
          outcome: { ok: false, text: 'Test-first is a good refinement technique, but it starts converting before a strategy has been chosen.' }, rate: 0.5 },
        { steps: [S('loop', 'Claude converts the simplest job first', 'Option B. Direct execution, one diff at a time.', 'WelcomeEmailJob: include Sidekiq::Job -> < ApplicationJob'),
            S('cust', 'Engineer reviews each diff: looks fine', '12 jobs converted. Job-by-job has now been chosen by default.', '12 diffs approved'),
            S('loop', 'Job 13: ReportExportJob uses Sidekiq::Batch', 'Nobody mapped this. Solid Queue has no batches, and the 12 converted jobs feed this batch.', 'Sidekiq::Batch.new.jobs { \u2026 }   # no equivalent', 'bad'),
            S('cust', 'Rework', 'Each diff was fine on its own. The review never saw the dependency or the strategy.', 'Revert 4 converted jobs; redesign batch flow.', 'bad')],
          outcome: { ok: false, text: 'Direct execution with review suits a well-scoped change. This one has an open strategy choice and unmapped dependencies, and the first hard job shows it.' }, rate: 0.5 },
        { steps: [S('loop', 'Engineer enters plan mode', 'Option C. Claude reads and searches; no edits.', '\u23f8 plan mode on'),
            M(S('tool', 'Claude maps the job code', '', 'Grep "Sidekiq::Batch|unique:|sidekiq_retry_in" app/ engines/'), 200000, [P('system + CLAUDE.md', 12000, 'sys'), P('job classes, initializers, specs', 46000, 'tool')]),
            X(S('loop', 'Claude reports which jobs use Sidekiq-only features', '', null, 'ok'), { table: map405 }),
            S('loop', 'Claude weighs both strategies', '', 'Job by job: run both libraries, queue by queue; batches redesigned first.\nAll at once: one cutover; batches must be redesigned before it.\nRecommend: job by job, batch jobs first.', 'ok'),
            S('cust', 'Engineers approve the design', 'Then edits begin.', 'Approved: queue-by-queue, batch redesign first.', 'ok')],
          outcome: { ok: true, text: 'A large multi-file change with two valid approaches and unknown dependencies: plan mode explores and designs before any edits.' }, rate: 0.95 },
        { steps: [S('sub', 'Explore subagent finds Sidekiq-only usage', 'Option D. Good discovery.', '7 batch jobs, 3 unique jobs, 9 custom retries'),
            M(S('ctx', 'Main context gets the summary', '', null), 200000, [P('system + CLAUDE.md', 12000, 'sys'), P('Explore summary', 2000, 'new')]),
            S('loop', 'Claude converts jobs one by one', 'The strategy debate is settled by default. No design was approved.', 'ReportExportJob: replace batch with ad hoc counter in Redis', 'bad')],
          outcome: { ok: false, text: 'Discovery helps, but going straight to job-by-job conversion skips the design the team must approve.' }, rate: 0.65 }
      ],
      B: [
        { steps: [S('loop', 'Claude writes a spec, then converts', '', 'spec/jobs/lesson_reminder_job_spec.rb\nLessonReminderJob < ApplicationJob'), S('loop', 'Spec passes', 'A bit more ceremony than needed.', '1 example, 0 failures', 'warn')],
          outcome: { ok: true, warn: true, text: 'Works. A spec first is fine, if more than this small change needs.' }, rate: 0.95 },
        { steps: [S('file', 'docs/jobs.md: the documented conversion pattern', '', 'include Sidekiq::Job -> < ApplicationJob; sidekiq_options retry: N -> retry_on StandardError, attempts: N'),
            S('loop', 'Claude converts LessonReminderJob directly', 'Option B.', 'Edit app/jobs/lesson_reminder_job.rb', 'ok'),
            S('cust', 'Engineer reviews the diff', '', 'Approved. Specs green.', 'ok')],
          outcome: { ok: true, text: 'A small, well-understood edit with a settled pattern: direct execution with review is right. This is the world where the runner-up wins.' }, rate: 1 },
        { steps: [S('loop', 'Plan mode', '', '\u23f8 plan mode on'), S('loop', 'Claude maps one job and proposes the documented pattern', 'Nothing to decide.', 'Plan: follow docs/jobs.md', 'warn')],
          outcome: { ok: true, warn: true, text: 'Works, but planning adds nothing to a one-file change.' }, rate: 0.95 },
        { steps: [S('sub', 'Explore finds no Sidekiq-only features', '', '0 matches'), S('loop', 'Claude converts the job', '', 'Edit lesson_reminder_job.rb', 'warn')],
          outcome: { ok: true, warn: true, text: 'Fine, with an exploration that finds nothing.' }, rate: 0.95 }
      ]
    }
  };

  [s110, s209, s210, s309, s408, s305, s203, s405].forEach(L.add);
})();
