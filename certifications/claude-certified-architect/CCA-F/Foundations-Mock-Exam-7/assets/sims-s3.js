/* CCA-F Mock Exam #7 - scripted simulations for Scenario 3 (multi-agent research system).
   Questions: m7-s3-01, m7-s3-04, m7-s3-06, m7-s3-07, m7-s3-08. See sims.js for the step format. */
(function () {
  var L = window.SIMLIB, S = L.S, req = L.req, res = L.res, T = L.T, U = L.U, R = L.R, E = L.E;
  var WHO = 'Committee';
  var ASK = 'Evidence summary please: does mobilising patients within 24 h of hip-fracture surgery cut 30-day mortality?';
  function ask() { return S('cust', 'Guideline committee asks for a summary', '', ASK); }
  function task(id, sub, prompt) { return U(id, 'Task', { subagent_type: sub, description: sub, prompt: prompt }); }
  var LIT = '9 RCTs found (n = 4,212). Okafor 2023 BMJ §3.2: 30-day mortality 6.1% vs 7.9%. Lindqvist 2022 Lancet §4.1: no significant difference. (+7 more)';
  var FINAL = 'Early mobilisation within 24 h is linked to lower 30-day mortality (pooled RR 0.78) [Okafor 2023, §3.2; Lindqvist 2022, §4.1; NCT05514492 results, §2].';

  /* ------------------------------------------------------------ m7-s3-01 stop_reason in the coordinator loop */
  var litTask = task('toolu_01', 'literature-search', 'Find RCTs on mobilisation within 24 h after hip-fracture surgery; report 30-day mortality with paper and section.');
  var mixed = [T('Literature search found 9 RCTs. Next I will search the trial registry and check the citations.'),
    task('toolu_02', 'trial-registry-search', 'Find registered trials on mobilisation within 24 h after hip-fracture surgery, with posted 30-day mortality.'),
    task('toolu_03', 'citation-check', 'Check each of the 9 RCT citations against the paper and section it names.')];
  var textOnly = [T('Based on 9 RCTs, early mobilisation appears to lower 30-day mortality. Summary follows.')];
  var textLoop = S('loop', 'Loop checks: does the response contain a text block?', 'This is the bug in the question: any text ends the run.',
    'if any(b.type == "text" for b in resp.content):\n    send_to_report(text)   # ← fires here\n    break\nrun_tools(resp)', 'bad');
  function start01() {
    return [ask(), res('Coordinator delegates the literature search', '', [litTask], 'tool_use'),
      S('sub', 'Literature subagent returns', '', LIT)];
  }
  var earlyReport = S('cust', 'Committee receives', 'No registry search, no citation check. The two Task calls were dropped.', 'Literature search found 9 RCTs. Next I will search the trial registry and check the citations.', 'bad');
  var guessReport = S('cust', 'Committee receives a summary built on one search', 'No registry search and no citation check ran.', textOnly[0].text, 'bad');

  var s301 = {
    id: 'm7-s3-01', who: WHO, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Claude writes a short sentence <b>and</b> requests more Task calls in the same response.' },
      { id: 'B', label: 'Decider changed', desc: 'After the first search Claude replies <b>in text only, with no Task calls</b>, instead of delegating the rest.' }
    ],
    runs: {
      A: [
        { steps: start01().concat([
            res('Claude writes a sentence and asks for two more subagents', 'Look at stop_reason: Claude is saying "run these and come back".', mixed, 'tool_use'),
            S('loop', 'Loop reads stop_reason = "tool_use" → run the Task calls and continue', 'Option A: the loop reads the signal, not the content.',
              'if resp.stop_reason == "tool_use":\n    results = run_tools(resp)   # ← fires here\n    continue\nelif resp.stop_reason == "end_turn":\n    send_to_report(final_text)', 'ok'),
            S('sub', 'Registry and citation subagents return', '', { 'toolu_02': '2 registered trials; NCT05514492 posted results (30-day mortality 5.8% vs 7.4%)', 'toolu_03': '9/9 citations match paper and section' }),
            req('Loop sends both results back', 'Each tool_result carries its tool_use_id.', { tool_choice: { type: 'auto' }, tools: ['Task'], messages: ['…', { role: 'assistant', content: '[text + Task toolu_02 + Task toolu_03]' }, { role: 'user', content: [R('toolu_02', '2 registered trials; NCT05514492 …'), R('toolu_03', '9/9 citations match')] }] }),
            res('Claude finishes', '', [T(FINAL)], 'end_turn'),
            S('cust', 'Committee receives the full summary', '', FINAL, 'ok')]),
          outcome: { ok: true, text: 'The loop follows stop_reason. A sentence next to Task calls no longer ends the run, so the registry search and citation check both happen.' }, rate: 1 },
        { steps: [ask(),
            req('Coordinator requests now use tool_choice "any"', 'Option B: "any" until the report subagent has run.', { tool_choice: { type: 'any' }, tools: ['Task'], messages: [{ role: 'user', content: ASK }] }),
            res('Forced to call a tool, Claude writes no sentence first', 'While "any" is on, the text check never trips…', [litTask], 'tool_use'),
            res('… and Claude ends up calling the report subagent', '', [task('toolu_04', 'report-writer', 'Draft the committee summary from the 9 RCTs.')], 'tool_use'),
            S('loop', 'Report subagent has run → back to "auto"', 'The text check in the loop is unchanged.', 'tool_choice = {"type": "auto"}'),
            res('Claude writes a sentence and asks for a citation check', 'stop_reason is tool_use. Claude still has work to do.', [T('Report drafted. Two cited trials are new, so I will check them first.'), task('toolu_05', 'citation-check', 'Check the two new trial citations in the draft.')], 'tool_use'),
            textLoop,
            S('cust', 'Committee receives', 'The citation check was dropped, exactly as before.', 'Report drafted. Two cited trials are new, so I will check them first.', 'bad')],
          outcome: { ok: false, text: 'Claude was already calling tools; the loop is what drops them. "any" only hid the bug while it was on, and it also stops Claude ending the run on its own.' }, rate: 0.6 },
        { steps: start01().concat([
            res('Claude asks for the registry search and ends with a sentence', 'Text after tool calls. stop_reason is still tool_use.', [task('toolu_02', 'trial-registry-search', 'Find registered trials on early mobilisation after hip-fracture surgery.'), T('Once the registry results are in, I will send everything to citation checking.')], 'tool_use'),
            S('loop', 'Loop checks: is the last block text?', 'Option C runs the Task call, then exits.', 'run_tools(blocks before last)\nif resp.content[-1].type == "text":\n    send_to_report(text)   # ← fires here\n    break', 'bad'),
            S('sub', 'Registry subagent returns, but no one reads it', 'The result is never sent back to Claude.', '2 registered trials; NCT05514492 posted results', 'warn'),
            S('cust', 'Committee receives', '', 'Once the registry results are in, I will send everything to citation checking.', 'bad')]),
          outcome: { ok: false, text: 'Checking the last block is still reading the content. Claude can end a response with text while asking for more work; only stop_reason says it is done.' }, rate: 0.7 },
        { steps: start01().concat([
            S('loop', 'Loop now stops on a turn budget', 'Option D: 4 turns for an evidence summary.', 'BUDGET = {"evidence_summary": 4}\nfor turn in range(BUDGET[kind]):\n    resp = call(); run_tools(resp)\nsend_to_report(last_text)'),
            res('Turn 2: Claude asks for registry search and citation check', '', mixed, 'tool_use'),
            res('Turn 4: citation check flagged sections, Claude wants a recheck', 'Claude is mid-task.', [T('Citation check flagged 2 sections. Re-checking them against the full text.'), task('toolu_06', 'citation-check', 'Recheck Lindqvist 2022 §4.1 and §4.3 against full text.')], 'tool_use'),
            S('loop', 'Budget reached → stop and hand over the last text', '', 'turn == 4  →  send_to_report(last_text)   # ← fires here', 'bad'),
            S('cust', 'Committee receives', 'The run was cut off mid-check.', 'Citation check flagged 2 sections. Re-checking them against the full text.', 'bad')]),
          outcome: { ok: false, text: 'A turn cap stops at an arbitrary point. Long runs are cut off mid-task and short runs waste turns.' }, rate: 0.5 }
      ],
      B: [
        { steps: start01().concat([
            res('Claude replies in text only', 'No Task calls. Claude is guessing from one search.', textOnly, 'end_turn'),
            S('loop', 'Loop reads stop_reason = "end_turn" → stop', 'The loop is now correct, and it correctly stops.', 'stop_reason == "end_turn"  →  send_to_report(text)'),
            guessReport]),
          outcome: { ok: false, text: 'A correct loop cannot run Task calls Claude never made. Here the fault is that Claude answers in text.' }, rate: 0.6 },
        { steps: [ask(),
            req('Coordinator requests use tool_choice "any"', 'Until the report subagent has run.', { tool_choice: { type: 'any' }, tools: ['Task'], messages: [{ role: 'user', content: ASK }] }),
            res('Claude delegates the literature search', '', [litTask], 'tool_use'),
            S('sub', 'Literature subagent returns', '', LIT),
            res('No text-only answer is allowed, so Claude delegates the rest', 'This is where it used to stop and guess.', mixed.slice(1), 'tool_use', 'ok'),
            S('sub', 'Registry and citation subagents return', '', { 'toolu_02': '2 registered trials; NCT05514492 posted results', 'toolu_03': '9/9 citations match' }),
            res('Claude calls the report subagent', '', [task('toolu_04', 'report-writer', 'Draft the committee summary from the RCTs, registry results and checked citations.')], 'tool_use'),
            S('loop', 'Report subagent has run → back to "auto"; Claude ends with text', '', 'tool_choice = {"type": "auto"}\n# next response: text only, stop_reason "end_turn"', 'ok'),
            S('cust', 'Committee receives the full summary', '', FINAL, 'ok')],
          outcome: { ok: true, text: 'Here the problem is Claude answering in text instead of delegating. Requiring a tool call until the report runs fixes exactly that. This is the world where the runner-up wins.' }, rate: 1 },
        { steps: start01().concat([
            res('Claude replies in text only', '', textOnly, 'end_turn'),
            S('loop', 'Last block is text → stop', 'Nothing to run, so the loop exits.', 'resp.content[-1].type == "text"  →  send_to_report(text)', 'warn'),
            guessReport]),
          outcome: { ok: false, text: 'No loop rule can make Claude call a tool it chose not to call.' }, rate: 0.6 },
        { steps: start01().concat([
            res('Claude replies in text only', '', textOnly, 'end_turn'),
            S('loop', 'Turn budget not used up, but nothing to run', 'The loop resends; Claude repeats the same answer until turn 4.', 'turn 2..4: no tool_use → resend', 'warn'),
            guessReport]),
          outcome: { ok: false, text: 'A turn budget does not make Claude delegate. It only decides when to stop waiting.' }, rate: 0.6 }
      ]
    }
  };

  /* ------------------------------------------------------------ m7-s3-04 prerequisite gate on publish_summary */
  var pub = U('toolu_21', 'publish_summary', { draft_id: 'D-118', committee: 'Orthogeriatrics guideline committee' });
  var sysHard = 'Hard requirement: do not call publish_summary until the citation-check subagent has passed every citation in the draft.\nReason: an unchecked summary that reaches a committee is a reportable compliance incident.';
  var sent = { draft_id: 'D-118', sent_to: 'Orthogeriatrics guideline committee', citation_check: 'none on record' };
  var badClaim = 'Claim 4 cites Okafor 2023 §3.2, which reports 90-day, not 30-day, mortality.';
  function earlyPublish(note) { return res('Run 17 of 20: Claude calls publish_summary straight after synthesis', note || 'The check has not run.', [pub], 'tool_use', 'warn'); }
  function forcedRun() {
    return [S('loop', 'Loop forces the citation-check delegation on the request before publish', 'But the loop only knows "before publish" from where the run is.',
        'if state.next_step == "publish":\n    tool_choice = {"type": "tool", "name": "Task"}   # citation-check'),
      req('Run 17 of 20: the request after synthesis', 'state.next_step is still "synthesis", so tool_choice stays "auto".', { tool_choice: { type: 'auto' }, tools: ['Task', 'publish_summary'], messages: ['…', { role: 'user', content: [R('toolu_20', 'Draft D-118 ready (23 citations)')] }] }),
      earlyPublish('Claude decides it is time to publish. The forced request never comes.'),
      S('tool', 'publish_summary sends D-118', '', sent, 'bad'),
      S('cust', 'Committee receives an unchecked summary', '', 'D-118 — ' + badClaim, 'bad')];
  }
  function hookRun() {
    return [earlyPublish(),
      S('tool', 'publish_summary sends D-118', '', sent),
      S('cust', 'Committee receives D-118', '', 'D-118 (23 citations)', 'warn'),
      S('hook', 'PostToolUse hook runs the citation check', 'It runs after publish_summary returned. The summary is already out.', { draft_id: 'D-118', passed: 22, failed: 1, detail: badClaim }, 'bad')];
  }
  function gateRun() {
    return [earlyPublish('Claude still tries to publish early in some runs.'),
      S('tool', 'publish_summary checks the record first', 'Option C: the gate lives in the tool code, not in the prompt.',
        'def publish_summary(draft_id, committee):\n    if not citation_checks.passed(draft_id):\n        return error("No passing citation check on record for " + draft_id)\n    send(draft_id, committee)', 'ok'),
      S('api', 'Claude gets an error result', '', { role: 'user', content: [E('toolu_21', 'Refused: no passing citation check on record for D-118. Run citation-check first.')] }),
      res('Claude delegates the citation check', '', [task('toolu_22', 'citation-check', 'Check all 23 citations in draft D-118 against paper and section.')], 'tool_use'),
      S('sub', 'Citation check: one fix, then all pass; result recorded', '', { draft_id: 'D-118', passed: 23, failed: 0, fixed: 'Claim 4 now cites Okafor 2023 §3.4 (30-day)', recorded: true }),
      res('Claude publishes again', '', [U('toolu_23', 'publish_summary', { draft_id: 'D-118', committee: 'Orthogeriatrics guideline committee' })], 'tool_use'),
      S('cust', 'Committee receives a checked summary', '', 'D-118 (23/23 citations checked)', 'ok')];
  }
  function promptRun(world) {
    var st = [req('Coordinator request with the requirement in the system prompt', '', { system: world === 'A' ? sysHard : 'Quality goal: run the citation-check subagent before calling publish_summary.\nReason: committees trust summaries whose citations were checked.', tools: ['Task', 'publish_summary'], messages: ['…', { role: 'user', content: [R('toolu_20', 'Draft D-118 ready (23 citations)')] }] })];
    if (world === 'A') {
      return st.concat([earlyPublish('Most runs now wait. This one does not.'),
        S('tool', 'publish_summary sends D-118', 'Nothing in the code stops it.', sent, 'bad'),
        S('cust', 'Committee receives an unchecked summary', 'One reportable incident.', 'D-118 — ' + badClaim, 'bad')]);
    }
    return st.concat([res('Claude delegates the citation check first', 'It follows the stated goal.', [task('toolu_22', 'citation-check', 'Check all 23 citations in draft D-118.')], 'tool_use'),
      S('sub', 'Citation check passes', '', { draft_id: 'D-118', passed: 23, failed: 0 }),
      res('Claude publishes', '', [pub], 'tool_use'),
      S('cust', 'Committee receives a checked summary', '', 'D-118 (23/23 citations checked)', 'ok')]);
  }
  var s304 = {
    id: 'm7-s3-04', who: WHO, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Every early publish is a <b>reportable compliance incident</b>. The order must hold on every run.' },
      { id: 'B', label: 'Decider changed', desc: 'The check is a <b>quality goal</b>: an occasional early publish is caught at committee review and is not an incident.' }
    ],
    runs: {
      A: [
        { steps: forcedRun(), outcome: { ok: false, text: 'Forcing a tool works on one request. A run that decides to publish early never reaches that request, and the summary goes out unchecked.' }, rate: 0.95 },
        { steps: hookRun(), outcome: { ok: false, text: 'The hook is deterministic but runs after the call. The check happens; the committee already has the summary.' }, rate: 0.95 },
        { steps: gateRun(), outcome: { ok: true, text: 'The publish tool refuses until a passing check is on record. Claude can try early, but nothing goes out early, on any run.' }, rate: 1 },
        { steps: promptRun('A'), outcome: { ok: false, text: 'A firm requirement with its reason cuts the misses a lot. It cannot make them zero, and here every miss is an incident.' }, rate: 0.97 }
      ],
      B: [
        { steps: forcedRun(), outcome: { ok: false, text: 'Early publishers still skip the forced request, so nothing changes for them. The prompt goal improves the decision itself.' }, rate: 0.9 },
        { steps: hookRun(), outcome: { ok: false, text: 'The check still runs after the committee has the summary. It reports problems; it does not make Claude check first more often.' }, rate: 0.9 },
        { steps: gateRun(), outcome: { ok: true, warn: true, text: 'This works, but it changes the publishing service to enforce a goal that tolerates misses. Heavier than needed.' }, rate: 1 },
        { steps: promptRun('B'), outcome: { ok: true, text: 'For a quality goal with tolerable misses, a clear requirement and its reason in the coordinator prompt is enough. This is the world where the runner-up wins.' }, rate: 0.95 }
      ]
    }
  };

  /* ------------------------------------------------------------ m7-s3-06 append tool results to history */
  var LIT6 = '9 RCTs found: Okafor 2023 BMJ §3.2, Lindqvist 2022 Lancet §4.1, (+7 more)';
  var REG6 = '2 registered trials; NCT05514492 posted 30-day mortality';
  var dropLoop = S('loop', 'Loop builds each request from the question and the latest result only', 'The latest result is pasted as text, because its tool_use turn is gone.',
    'messages = [{"role": "user",\n             "content": QUESTION + "\\n\\nLatest result: " + last_result}]', 'warn');
  function onlyLatest(extra, note) {
    return req('Turn 3 request: question + latest result' + (extra ? ' + ' + extra.label : ''), note || 'The literature search from turn 1 is not in it.',
      { system: 'You coordinate an evidence review…', tools: ['Task'], messages: [{ role: 'user', content: ASK + (extra ? '\n\n' + extra.text : '') + '\n\nLatest result: ' + REG6 }] });
  }
  var repeatLit = res('Claude runs the literature search again', 'It cannot see that it already did.', [task('toolu_33', 'literature-search', 'Find RCTs on early mobilisation after hip-fracture surgery.')], 'tool_use', 'bad');
  function fullHistoryA() {
    return [S('loop', 'Loop appends every assistant turn and tool result', 'Option D.', 'messages.append({"role": "assistant", "content": resp.content})\nmessages.append({"role": "user", "content": tool_results})', 'ok'),
      req('Turn 3 request: the whole run so far', 'About 9k tokens of a 200k window.', { tools: ['Task'], messages: [{ role: 'user', content: ASK }, { role: 'assistant', content: [task('toolu_31', 'literature-search', '…')] }, { role: 'user', content: [R('toolu_31', LIT6)] }, { role: 'assistant', content: [task('toolu_32', 'trial-registry-search', '…')] }, { role: 'user', content: [R('toolu_32', REG6)] }] }),
      res('Claude moves on to the next step', 'It sees both searches and their findings.', [T('Both searches are in. Checking the 11 citations next.'), task('toolu_34', 'citation-check', 'Check the 9 RCT and 2 registry citations against paper and section.')], 'tool_use', 'ok')];
  }
  var tooLong = S('api', 'API rejects the request', 'The full history no longer fits.', { type: 'error', error: { type: 'invalid_request_error', message: 'prompt is too long: 231448 tokens > 200000 maximum' } }, 'bad');
  var s306 = {
    id: 'm7-s3-06', who: WHO, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Runs are short and use <b>a small part of the context window</b>; the loop simply drops earlier turns.' },
      { id: 'B', label: 'Decider changed', desc: 'Runs cover hundreds of papers and <b>outgrow the context window</b> before they finish.' }
    ],
    runs: {
      A: [
        { steps: [ask(),
            S('loop', 'Loop writes each search and its findings to scratchpad.md', 'Option A. The message list is still cut to the latest result.', 'scratchpad.append(f"- {sub}: {query} → {summary}")\nmessages = [user(QUESTION + scratchpad.read() + last_result)]'),
            onlyLatest({ label: 'scratchpad', text: 'Scratchpad:\n- literature-search → ' + LIT6 + '\n- trial-registry-search → ' + REG6 }, 'The findings are back, as a file read every turn.'),
            res('Claude moves on to the citation check', '', [task('toolu_34', 'citation-check', 'Check the 11 citations.')], 'tool_use'),
            S('loop', 'Repeats stop, at a cost', 'A file write and read every turn, and Claude\'s own reasoning from earlier turns is still gone. The history would have fit.', 'context used: 9k / 200k tokens', 'warn')],
          outcome: { ok: true, warn: true, text: 'It stops the repeats by rebuilding, in a file, a history the loop threw away. These runs fit in context, so the plain message list does the same with less.' }, rate: 0.93 },
        { steps: [ask(), dropLoop,
            onlyLatest({ label: 'case facts', text: 'Searches already run: literature-search(early mobilisation RCTs); trial-registry-search(early mobilisation)' }, 'Claude knows a literature search ran, but not what it found.'),
            res('Claude searches again to get the RCT list back', 'It needs the 9 papers to check them, and they are not here.', [task('toolu_33', 'literature-search', 'List the RCTs on early mobilisation after hip-fracture surgery, with sections cited.')], 'tool_use', 'bad')],
          outcome: { ok: false, text: 'A list of searches patches the missing history. The findings and the reasoning between turns are still dropped, so Claude repeats work to get them back.' }, rate: 0.7 },
        { steps: [ask(), dropLoop, onlyLatest(), repeatLit,
            S('tool', 'Search returns its cached result', 'Cheap and fast, but the repeat still happened.', { cache: 'hit', query: 'early mobilisation hip fracture RCT', result: LIT6 }, 'warn'),
            S('loop', 'Next turn sends only this result again', 'Now the registry search drops out, and Claude repeats that one.', 'messages = [user(QUESTION + last_result)]   # registry result gone', 'bad')],
          outcome: { ok: false, text: 'Caching makes repeats cheaper. Claude still cannot see what it already did, so it keeps repeating.' }, rate: 0.4 },
        { steps: [ask()].concat(fullHistoryA(), [res('Claude finishes', '', [T(FINAL)], 'end_turn'), S('cust', 'Committee receives the summary', 'No repeated searches. Run used 18k tokens.', FINAL, 'ok')]),
          outcome: { ok: true, text: 'The model knows only what you send. With every tool result in the history, Claude sees what it already did and moves on. The runs fit easily.' }, rate: 1 }
      ],
      B: [
        { steps: [ask(),
            S('loop', 'Loop keeps a compact scratchpad.md of searches and findings', '', 'scratchpad.append(f"- {sub}: {query} → {summary}")'),
            req('Turn 61 request: question + scratchpad + latest result', 'About 7k tokens, though 140 papers have been read.', { tools: ['Task'], messages: [{ role: 'user', content: ASK + '\n\nScratchpad:\n- literature-search → 142 RCTs …\n- citation-check batch 1–6 → 128/131 pass …\n\nLatest result: batch 7 → 11/11 pass' }] }),
            res('Claude moves on to the next batch', 'Nothing repeated, nothing lost.', [task('toolu_61', 'citation-check', 'Check citation batch 8 (11 citations).')], 'tool_use', 'ok'),
            S('cust', 'Committee receives the summary', '', FINAL, 'ok')],
          outcome: { ok: true, text: 'When the run outgrows the context window, findings have to live outside it. A scratchpad keeps them in a few thousand tokens. This is the world where the runner-up wins.' }, rate: 0.95 },
        { steps: [ask(), S('loop', 'Case-facts block lists searches run', '', 'facts = ["literature-search(...)", "citation-check batch 1..7"]'),
            req('Turn 61 request: question + case facts + latest result', 'It lists what ran, not what was found.', { tools: ['Task'], messages: [{ role: 'user', content: ASK + '\n\nSearches run: literature-search; citation-check batches 1–7\n\nLatest result: batch 7 → 11/11 pass' }] }),
            res('Claude re-runs the search to recover the paper list', '', [task('toolu_62', 'literature-search', 'List the RCTs again with sections.')], 'tool_use', 'bad')],
          outcome: { ok: false, text: 'The block remembers that searches ran, but not their findings. Claude has to fetch them again.' }, rate: 0.6 },
        { steps: [ask(), dropLoop, onlyLatest(), repeatLit,
            S('tool', 'Search returns its cached result', '', { cache: 'hit', result: '142 RCTs …' }, 'warn')],
          outcome: { ok: false, text: 'A cache cannot tell Claude what it already did.' }, rate: 0.4 },
        { steps: [ask(),
            S('loop', 'Loop appends every turn and tool result', '', 'messages.append(...)'),
            req('Turn 61 request: the whole run so far', '60 turns of full-text findings.', { tools: ['Task'], messages: ['… 120 messages, 142 papers of findings …'] }),
            tooLong,
            S('cust', 'Committee receives nothing', 'The run fails before synthesis.', '(run failed at turn 61)', 'bad')],
          outcome: { ok: false, text: 'The full history is right while it fits. These runs outgrow the window, so findings have to move out of the message list.' }, rate: 0.3 }
      ]
    }
  };

  /* ------------------------------------------------------------ m7-s3-07 forced tool_choice for extraction first */
  var docTools = ['extract_citation_metadata', 'analyze_findings'];
  var paperMsg = 'Paper P-07: Okafor 2023, BMJ. Full text attached.';
  var META = { paper_id: 'P-07', doi: '10.1136/bmj-2023-074512', pages: '1–11', sections: { '3.2': 'p.6', '3.4': 'p.7' } };
  var goodFindings = { findings: [{ claim: '30-day mortality 6.1% vs 7.9%', section: '3.2', page: 6, doi: META.doi }] };
  var noPageFindings = { findings: [{ claim: '30-day mortality 6.1% vs 7.9%', section: null, page: null, doi: null }] };
  function rq(choice, title, note, tools) { return req(title, note, { tool_choice: choice, tools: tools || docTools, messages: [{ role: 'user', content: paperMsg }] }); }
  var analyzeFirst = res('Paper 13 of 20: Claude calls analyze_findings first', 'A tool call, just the wrong one.', [U('toolu_71', 'analyze_findings', { paper_id: 'P-07' })], 'tool_use', 'bad');
  var noPages = S('tool', 'analyze_findings returns findings with no page numbers', 'No metadata had been extracted yet.', noPageFindings, 'bad');
  function extractThenAnalyze() {
    return [res('Claude calls extract_citation_metadata', '', [U('toolu_71', 'extract_citation_metadata', { paper_id: 'P-07' })], 'tool_use'),
      S('tool', 'Extraction returns page and DOI fields', '', META),
      req('Next request: tool_choice back to "auto", result sent back', '', { tool_choice: { type: 'auto' }, tools: docTools, messages: [{ role: 'user', content: paperMsg }, { role: 'assistant', content: '[tool_use toolu_71]' }, { role: 'user', content: [R('toolu_71', JSON.stringify(META))] }] }),
      res('Claude calls analyze_findings with the metadata', '', [U('toolu_72', 'analyze_findings', { paper_id: 'P-07', metadata: META })], 'tool_use'),
      S('tool', 'Findings carry page and DOI', '', goodFindings, 'ok')];
  }
  var proseReply = res('Paper 13 of 20: Claude replies in text', 'No tool call at all.', [T('This trial reports lower 30-day mortality with early mobilisation (6.1% vs 7.9%).')], 'end_turn', 'bad');
  var s307 = {
    id: 'm7-s3-07', who: WHO, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'The subagent <b>calls a tool on every turn</b>, but on some papers it calls analyze_findings first.' },
      { id: 'B', label: 'Decider changed', desc: 'The subagent picks extraction first when it uses a tool, but on some papers it <b>replies in plain text</b> instead of calling one.' }
    ],
    runs: {
      A: [
        { steps: [rq({ type: 'auto' }, 'Request with rewritten tool descriptions', 'Both descriptions now say extraction comes first.', [{ name: 'extract_citation_metadata', description: 'Run FIRST for every paper. Returns DOI, page range and section pages that analyze_findings needs.' }, { name: 'analyze_findings', description: 'Run AFTER extract_citation_metadata. Expects its page and DOI fields.' }]),
            analyzeFirst, noPages],
          outcome: { ok: false, text: 'Better descriptions make the right order more likely. The order is still the model\'s choice, so some papers still skip extraction.' }, rate: 0.9 },
        { steps: [rq({ type: 'tool', name: 'extract_citation_metadata' }, 'First request for the paper forces the extraction tool', 'Option B: tool_choice names the tool.')].concat(extractThenAnalyze()),
          outcome: { ok: true, text: 'A named tool_choice makes Claude call exactly that tool. Extraction runs first on every paper, then Claude is free to choose.' }, rate: 1 },
        { steps: [rq({ type: 'auto' }, 'Request unchanged', ''), analyzeFirst, noPages,
            S('hook', 'PostToolUse hook patches the result', 'It adds the DOI and page range for the paper, but cannot tell which page each finding came from.', { doi: META.doi, pages: '1–11', findings: [{ claim: '30-day mortality 6.1% vs 7.9%', page: null }] }, 'warn')],
          outcome: { ok: false, text: 'The hook repairs results after the wrong order. It hides the skipped step, and the per-finding pages are still missing.' }, rate: 0.8 },
        { steps: [rq({ type: 'any' }, 'Every request uses tool_choice "any"', 'Option D.'),
            res('Paper 13 of 20: Claude calls analyze_findings first', '"any" accepts any tool. The subagent already called one every turn.', [U('toolu_71', 'analyze_findings', { paper_id: 'P-07' })], 'tool_use', 'bad'),
            noPages],
          outcome: { ok: false, text: '"any" means "call some tool, not text". The subagent was already calling a tool every turn; it was the wrong tool first.' }, rate: 0.85 }
      ],
      B: [
        { steps: [rq({ type: 'auto' }, 'Request with rewritten tool descriptions', ''), proseReply,
            S('loop', 'No tool ran, so no metadata and no findings record', '', 'stop_reason == "end_turn"  →  paper P-07 has no findings', 'bad')],
          outcome: { ok: false, text: 'Descriptions guide which tool. They do not stop Claude answering in prose.' }, rate: 0.85 },
        { steps: [rq({ type: 'tool', name: 'extract_citation_metadata' }, 'First request forces the extraction tool', ''),
            res('Claude calls extract_citation_metadata', '', [U('toolu_71', 'extract_citation_metadata', { paper_id: 'P-07' })], 'tool_use'),
            S('tool', 'Extraction returns page and DOI fields', '', META),
            req('Next request: tool_choice back to "auto"', '', { tool_choice: { type: 'auto' }, tools: docTools, messages: ['…', { role: 'user', content: [R('toolu_71', JSON.stringify(META))] }] }),
            res('Claude replies in text instead of analysing', 'Only the first request was forced.', proseReply.payload.content, 'end_turn', 'bad')],
          outcome: { ok: false, text: 'Forcing the first tool fixes the first step only. The text reply comes on the next request, which is back on "auto".' }, rate: 0.85 },
        { steps: [rq({ type: 'auto' }, 'Request unchanged', ''), proseReply,
            S('hook', 'PostToolUse hook never fires', 'No tool ran, so there is nothing to patch.', '(no tool call)', 'bad')],
          outcome: { ok: false, text: 'A tool hook cannot act on a reply that called no tool.' }, rate: 0.85 },
        { steps: [rq({ type: 'any' }, 'Every request for the paper uses tool_choice "any"', 'Text-only replies are off the table.'),
            res('Claude calls extract_citation_metadata', 'It still chooses which tool, and it chooses well.', [U('toolu_71', 'extract_citation_metadata', { paper_id: 'P-07' })], 'tool_use', 'ok'),
            S('tool', 'Extraction returns page and DOI fields', '', META),
            req('Next request, still "any"', '', { tool_choice: { type: 'any' }, tools: docTools, messages: ['…', { role: 'user', content: [R('toolu_71', JSON.stringify(META))] }] }),
            res('Claude calls analyze_findings', '', [U('toolu_72', 'analyze_findings', { paper_id: 'P-07', metadata: META })], 'tool_use'),
            S('tool', 'Findings carry page and DOI', '', goodFindings, 'ok'),
            S('loop', 'Paper done → loop moves to the next paper', '', 'if findings_saved(paper): next_paper()')],
          outcome: { ok: true, text: 'Here the problem is prose instead of a tool call. "any" removes that option and keeps Claude\'s choice, which was already right. This is the world where the runner-up wins.' }, rate: 1 }
      ]
    }
  };

  /* ------------------------------------------------------------ m7-s3-08 scoped AgentDefinition tools */
  var ALL = ['search_journals', 'fetch_fulltext', 'search_registry', 'get_trial_record', 'extract_citation_metadata', 'analyze_findings', 'verify_citation', 'flag_citation',
    'read_analysis_results', 'save_draft', 'save_report', 'render_report_pdf', 'publish_summary', 'notify_committee'];
  var synthTask = res('Coordinator spawns the synthesis subagent', '', [task('toolu_81', 'synthesis', 'Write the evidence summary draft for D-118 from the analysis results of the 11 papers.')], 'tool_use');
  var readRes = S('tool', 'read_analysis_results', '', { input: { review_id: 'R-31' }, output: { papers: 11, findings: 26, example: 'Okafor 2023 §3.2 p.6: 30-day mortality 6.1% vs 7.9%' } });
  function template(extra) {
    return S('sub', 'Synthesis built from the shared template' + (extra ? ', ' + extra : ''), 'It holds all 14 tools; 12 belong to other roles.',
      'AgentDefinition(\n  description="Writes the evidence summary draft",\n  prompt=SYNTH_PROMPT,\n  tools=ALL_TOOLS   # ' + ALL.length + ' tools\n)');
  }
  var midSearch = S('sub', 'Mid-draft, synthesis calls search_registry', '"Checking for newer trials" — a job for the registry subagent.', { tool: 'search_registry', input: { query: 'early mobilisation hip fracture 2026' } }, 'bad');
  var wrongSave = S('sub', 'Synthesis saves with save_report', 'The reporting role\'s tool. The draft lands in the final-report store.', { tool: 'save_report', input: { review_id: 'R-31', body: '…draft…' } }, 'bad');
  var B_TOOLS = ['read_analysis_results', 'read_draft', 'save_draft', 'save_section'];
  var thinDesc = S('sub', 'Synthesis already has its own four tools, with one-line descriptions', 'save_draft: "Saves text."  save_section: "Saves text."',
    { tools: [{ name: 'save_draft', description: 'Saves text.' }, { name: 'save_section', description: 'Saves text.' }, '…'] });
  var wrongSaveB = S('sub', 'Synthesis saves the whole draft with save_section', 'Two identical descriptions: it guesses.', { tool: 'save_section', input: { draft_id: 'D-118', section: 'body', text: '…full draft…' } }, 'bad');
  var s308 = {
    id: 'm7-s3-08', who: WHO, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Synthesis holds the full 14-tool set; descriptions are already detailed and <b>most tools belong to other roles</b>.' },
      { id: 'B', label: 'Decider changed', desc: 'Synthesis already has its own four tools, but their descriptions are <b>one-liners</b> ("Saves text.").' }
    ],
    runs: {
      A: [
        { steps: [template('plus a prompt section'),
            S('loop', 'SYNTH_PROMPT gains an allowed-tools section', 'Option A.', 'You may use read_analysis_results and save_draft.\nsearch_*, save_report and the rest belong to other roles. Do not use them.'),
            synthTask, readRes, midSearch, wrongSave],
          outcome: { ok: false, text: 'The prompt says which tools are off-limits, but the subagent still holds all 14. Guidance cuts the misuse; it does not remove it.' }, rate: 0.85 },
        { steps: [template('plus an MCP resource'),
            synthTask,
            S('sub', 'Synthesis reads analysis://R-31 before drafting', 'Fewer exploratory calls to find the results.', { resource: 'analysis://R-31', papers: 11, findings: 26 }),
            wrongSave],
          outcome: { ok: false, text: 'The resource saves lookups, but every other role\'s tools are still in its hands, and it still picks the wrong save tool.' }, rate: 0.8 },
        { steps: [S('loop', 'Synthesis gets its own AgentDefinition', 'Option C.', 'agents = {"synthesis": AgentDefinition(\n  description="Writes the evidence summary draft",\n  prompt=SYNTH_PROMPT,\n  tools=["read_analysis_results", "save_draft"])}', 'ok'),
            synthTask,
            S('sub', 'What the synthesis subagent sees', 'Two tools. Searching and save_report are not options.', { tools: ['read_analysis_results', 'save_draft'] }),
            readRes,
            S('sub', 'Synthesis saves with save_draft', '', { tool: 'save_draft', input: { draft_id: 'D-118', body: '…' }, output: { saved: true } }, 'ok'),
            S('cust', 'Draft D-118 goes on to citation check', '', 'D-118 draft saved (26 findings, 11 papers)', 'ok')],
          outcome: { ok: true, text: 'A subagent cannot misuse a tool it does not have. With two role-fit tools, the stray searches and wrong saves stop.' }, rate: 1 },
        { steps: [template(),
            S('loop', 'Every description is rewritten again', 'They were already detailed. Now each adds "Not for synthesis."', { name: 'search_registry', description: 'Searches the trial registry by condition and intervention. Input: {query}. Example: {"query": "hip fracture mobilisation"}. Not for synthesis.' }),
            synthTask, readRes, midSearch],
          outcome: { ok: false, text: 'Descriptions were never the weak point. The subagent still holds 12 off-role tools and still reaches for them.' }, rate: 0.8 }
      ],
      B: [
        { steps: [thinDesc,
            S('loop', 'SYNTH_PROMPT names the four allowed tools', 'All four are already its tools.', 'You may use read_analysis_results, read_draft, save_draft and save_section.'),
            synthTask, wrongSaveB],
          outcome: { ok: false, text: 'The list of allowed tools was already right. The problem is that two tools look identical.' }, rate: 0.75 },
        { steps: [thinDesc, synthTask,
            S('sub', 'Synthesis reads analysis://R-31', '', { resource: 'analysis://R-31' }), wrongSaveB],
          outcome: { ok: false, text: 'A resource helps reading, not choosing between two save tools.' }, rate: 0.75 },
        { steps: [S('loop', 'Synthesis gets "its own" AgentDefinition', 'Its tools are the same four: it uses all of them.', 'tools=' + JSON.stringify(B_TOOLS)),
            thinDesc, synthTask, wrongSaveB],
          outcome: { ok: false, text: 'Scoping removes off-role tools. There are none here; the confusion is between two tools it needs.' }, rate: 0.75 },
        { steps: [S('loop', 'Descriptions rewritten with inputs, examples and boundaries', '', [{ name: 'save_draft', description: 'Saves a complete draft, replacing the previous version. Input: {draft_id, body}. Use after a full pass.' }, { name: 'save_section', description: 'Updates one named section of an existing draft. Input: {draft_id, section, text}. Not for whole drafts.' }]),
            synthTask, readRes,
            S('sub', 'Synthesis saves the full draft with save_draft', '', { tool: 'save_draft', input: { draft_id: 'D-118', body: '…' }, output: { saved: true } }, 'ok')],
          outcome: { ok: true, text: 'With one-line descriptions, rewriting them is the first fix: the two save tools now say what each is for. This is the world where the runner-up wins.' }, rate: 0.95 }
      ]
    }
  };

  [s301, s304, s306, s307, s308].forEach(L.add);
})();
