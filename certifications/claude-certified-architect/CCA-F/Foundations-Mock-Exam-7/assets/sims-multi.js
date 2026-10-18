/* CCA-F Mock Exam #7 - scripted simulations: multi-agent context, error propagation, review and human routing.
   Questions: m7-s3-02, m7-s3-03, m7-s3-10, m7-s5-10, m7-s6-07, m7-s6-09, m7-s6-10. See sims.js for the step format. */
(function () {
  var L = window.SIMLIB, S = L.S, req = L.req, res = L.res, T = L.T, U = L.U, R = L.R, E = L.E, X = L.X;
  function task(id, sub, prompt) { return U(id, 'Task', { subagent_type: sub, description: sub, prompt: prompt }); }

  /* ------------------------------------------------------------ m7-s3-02 per-request rules in the Task prompt */
  var ASK2 = 'Evidence summary for the Anaesthesia committee: does tranexamic acid cut blood transfusion after hip-fracture surgery?\nOur rules: only trials with at least 300 patients; exclude trials where patients took anticoagulants (DOACs).';
  var RULES2 = 'Inclusion rules for this request: at least 300 patients per trial; exclude any trial whose patients took DOACs.';
  var BARE2 = 'Analyse trials of tranexamic acid in hip-fracture surgery. Outcome: blood transfusion rate.';
  var SUBSYS2 = 'You analyse clinical trials. For each trial report design, size, outcome and the paper section it comes from.';
  var OLDRULES2 = 'Criteria: include trials with at least 100 patients. Exclude trials of patients on DOACs.\nIncluded example: Mehta 2021 (n = 140, no DOACs). Excluded example: Ruiz 2020 (n = 210, DOAC arm).';
  function ask2() { return S('cust', 'Anaesthesia committee submits a request', 'Each committee sets its own rules. This one wants big trials only.', ASK2); }
  var agreed2 = S('loop', 'Coordinator agrees the rules with the requester', 'The rules now sit in the coordinator\'s conversation.', 'Coordinator: "Confirmed: n >= 300, DOAC trials excluded. Starting the analysis."');
  function subSees(prompt, sys, mark, note) {
    return S('ctx', 'What the analysis subagent receives', note, { system: sys, messages: [{ role: 'user', content: prompt }] }, mark);
  }
  var wrong2 = S('sub', 'Analysis subagent returns', 'It includes trials the committee excluded: n = 140 and n = 210, and one DOAC trial.', 'Included 6 trials: Mehta 2021 (n = 140), Okoye 2022 (n = 210), Ruiz 2020 (n = 410, DOAC arm), Sato 2023 (n = 512), \u2026', 'bad');
  var wrongOut2 = S('cust', 'Committee receives', 'Three of the six trials break their own rules.', 'Pooled from 6 trials: transfusion 18% vs 31%. [Mehta 2021 \u00a73.1; Okoye 2022 \u00a74.2; Ruiz 2020 \u00a73.3; \u2026]', 'bad');
  var right2 = S('sub', 'Analysis subagent returns', 'Small trials and the DOAC trial are left out, each with a reason.', 'Included 3 trials (Sato 2023 n = 512, Lin 2022 n = 388, Adeyemi 2024 n = 301). Excluded: Mehta 2021 (n < 300), Okoye 2022 (n < 300), Ruiz 2020 (DOAC arm).', 'ok');
  var rightOut2 = S('cust', 'Committee receives', '', 'Pooled from 3 trials meeting your rules: transfusion 21% vs 33% [Sato 2023 \u00a73.2; Lin 2022 \u00a74.1; Adeyemi 2024 \u00a73.4].', 'ok');

  var FIXED2 = 'Network policy, all committees: at least 100 patients per trial; exclude trials of patients on DOACs.';
  var s302 = {
    id: 'm7-s3-02', who: 'Committee', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Each committee sets <b>its own rules on every request</b>. Today the Task prompt names only the drug and the outcome.' },
      { id: 'B', label: 'Decider changed', desc: 'Every committee uses <b>the same fixed network rules</b> (n &ge; 100, no DOAC trials) on every request.' }
    ],
    runs: {
      A: [
        { steps: [ask2(), agreed2,
            S('file', 'AgentDefinition for the analysis subagent', 'Option A. Written once, at deploy time, from last month\'s Orthogeriatrics request.', { name: 'trial-analysis', prompt: SUBSYS2 + '\n\n' + OLDRULES2 }),
            res('Coordinator delegates', 'The Task prompt still names only the drug and the outcome.', [task('toolu_01', 'trial-analysis', BARE2)], 'tool_use'),
            subSees(BARE2, SUBSYS2 + '\n\n' + OLDRULES2, 'bad', 'The criteria section is there, but it holds another committee\'s rules (n >= 100). Today\'s n >= 300 is nowhere.'),
            wrong2, wrongOut2],
          outcome: { ok: false, text: 'A system prompt is fixed for every run. These rules change on every request, so the fixed section always holds some other committee\'s rules.' }, rate: 0.2 },
        { steps: [ask2(), agreed2,
            S('loop', 'Coordinator\'s system prompt gets a criteria section', 'Option B. Rewritten for this request.', { system: 'You coordinate evidence reviews\u2026\n\nCriteria for this request: ' + RULES2 }),
            res('Coordinator delegates', '', [task('toolu_01', 'trial-analysis', BARE2)], 'tool_use'),
            subSees(BARE2, SUBSYS2, 'bad', 'A subagent gets its own system prompt and the Task prompt. The coordinator\'s system prompt is not passed on.'),
            wrong2, wrongOut2],
          outcome: { ok: false, text: 'The rules moved inside the coordinator\'s context, which subagents never inherit. The analysis still runs without them.' }, rate: 0.15 },
        { steps: [ask2(), agreed2,
            S('loop', 'Coordinator keeps a case-facts block', 'Option C. Safe from summarising in the coordinator\'s long run.', { case_facts: { drug: 'tranexamic acid', outcome: 'transfusion rate', min_patients: 300, exclude: ['DOAC trials'] } }),
            res('Coordinator delegates', 'The delegation is written the same way as before.', [task('toolu_01', 'trial-analysis', BARE2)], 'tool_use'),
            subSees(BARE2, SUBSYS2, 'bad', 'The case-facts block lives in the coordinator\'s messages. Nothing copies it into the delegation.'),
            wrong2, wrongOut2],
          outcome: { ok: false, text: 'A case-facts block keeps facts safe for the coordinator. It reaches a subagent only if written into the Task prompt.' }, rate: 0.15 },
        { steps: [ask2(), agreed2,
            res('Coordinator delegates with the rules written in', 'Option D: this request\'s rules, in full, beside the drug and outcome.', [task('toolu_01', 'trial-analysis', BARE2 + '\n' + RULES2)], 'tool_use'),
            subSees(BARE2 + '\n' + RULES2, SUBSYS2, 'ok', 'Its own fixed role, plus exactly this request\'s rules.'),
            right2, rightOut2],
          outcome: { ok: true, text: 'Subagents inherit nothing. Rules that change per request travel in that request\'s Task prompt, so the subagent applies the right ones.' }, rate: 0.96 }
      ],
      B: [
        { steps: [S('cust', 'A committee submits a request', 'Rules are network policy, the same for everyone.', 'Evidence summary: does tranexamic acid cut transfusion after hip-fracture surgery?'),
            S('file', 'AgentDefinition carries the fixed network criteria', 'Written once, true on every run.', { name: 'trial-analysis', prompt: SUBSYS2 + '\n\n' + FIXED2 + '\nIncluded example: Mehta 2021 (n = 140, no DOACs). Excluded example: Ruiz 2020 (DOAC arm).' }, 'ok'),
            res('Coordinator delegates', 'The Task prompt stays short: drug and outcome.', [task('toolu_01', 'trial-analysis', BARE2)], 'tool_use'),
            S('sub', 'Analysis subagent returns', '', 'Included 5 trials (n >= 100, no DOACs). Excluded: Ruiz 2020 (DOAC arm), Kaur 2019 (n = 64).', 'ok'),
            S('cust', 'Committee receives', '', 'Pooled from 5 trials: transfusion 19% vs 32% [Mehta 2021 \u00a73.1; Sato 2023 \u00a73.2; \u2026].', 'ok')],
          outcome: { ok: true, text: 'Rules that never change are role guidance. The system prompt holds them once, with examples, for every run. This is the world where the runner-up wins.' }, rate: 0.96 },
        { steps: [S('cust', 'A committee submits a request', '', 'Evidence summary: tranexamic acid and transfusion.'),
            S('loop', 'Network rules go in the coordinator\'s system prompt', '', { system: 'You coordinate evidence reviews\u2026\n' + FIXED2 }),
            subSees(BARE2, SUBSYS2, 'bad', 'Still not passed to the subagent.'),
            S('sub', 'Analysis subagent includes a DOAC trial', '', 'Included 6 trials, including Ruiz 2020 (DOAC arm).', 'bad')],
          outcome: { ok: false, text: 'Fixed or not, the coordinator\'s prompt does not reach a subagent.' }, rate: 0.2 },
        { steps: [S('cust', 'A committee submits a request', '', 'Evidence summary: tranexamic acid and transfusion.'),
            S('loop', 'Case-facts block holds the rules', '', { case_facts: { min_patients: 100, exclude: ['DOAC trials'] } }),
            subSees(BARE2, SUBSYS2, 'bad', 'Still the coordinator\'s own notes.'),
            S('sub', 'Analysis subagent includes a DOAC trial', '', 'Included 6 trials, including Ruiz 2020 (DOAC arm).', 'bad')],
          outcome: { ok: false, text: 'The block is not a delivery channel to subagents.' }, rate: 0.2 },
        { steps: [S('cust', 'A committee submits a request', '', 'Evidence summary: tranexamic acid and transfusion.'),
            res('Coordinator restates the network rules in every Task prompt', 'Same text, pasted into every delegation by the coordinator.', [task('toolu_01', 'trial-analysis', BARE2 + '\n' + FIXED2)], 'tool_use', 'warn'),
            S('sub', 'Analysis subagent applies them', '', 'Included 5 trials. Excluded: Ruiz 2020 (DOAC arm), Kaur 2019 (n = 64).', 'ok')],
          outcome: { ok: true, warn: true, text: 'It works, but fixed rules now depend on the coordinator restating them each time, with no examples. The definition is the place for fixed rules.' }, rate: 0.93 }
      ]
    }
  };

  /* ------------------------------------------------------------ m7-s3-03 parallel Task calls */
  var ASK3 = 'Evidence summary: does early mobilisation after hip-fracture surgery cut 30-day mortality?';
  var P_LIT = 'Find RCTs on mobilisation within 24 h after hip-fracture surgery; report 30-day mortality with paper and section.';
  var P_REG = 'Find registered trials on early mobilisation after hip-fracture surgery, with posted results.';
  var P_NOT = 'Find regulatory and safety notices on early mobilisation protocols after hip-fracture surgery.';
  var SUMM3 = 'Early mobilisation is linked to lower 30-day mortality (pooled RR 0.78) [Okafor 2023 \u00a73.2; NCT05514492 \u00a72]. No safety notices found.';
  var head3 = ['Step', 'Starts at', 'Ends at'];
  var serialTable = { head: head3, rows: [['Coordinator turn 1', '0 s', '10 s'], ['literature-search', '10 s', '150 s'], ['Coordinator turn 2', '150 s', '160 s'], ['trial-registry-search', '160 s', '255 s'], ['Coordinator turn 3', '255 s', '265 s'], ['notices-search', '265 s', '335 s'], ['Synthesis turn', '335 s', '345 s']] };
  function ask3() { return S('cust', 'Committee asks', 'Every request needs all three searches. None needs another\'s results.', ASK3); }
  function serialRun(title, note, mark) {
    return [res('Turn 1: one Task call', 'The coordinator waits for it before sending the next.', [task('toolu_01', 'literature-search', P_LIT)], 'tool_use'),
      res('Turn 2: next Task call, after the first result', '', [task('toolu_02', 'trial-registry-search', P_REG)], 'tool_use'),
      res('Turn 3: last Task call', '', [task('toolu_03', 'notices-search', P_NOT)], 'tool_use'),
      X(S('loop', title, note, 'elapsed: 345 s', mark), { table: serialTable })];
  }
  var s303 = {
    id: 'm7-s3-03', who: 'Committee', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Three independent searches, run one after another, and <b>every request needs all three</b>.' },
      { id: 'B', label: 'Decider changed', desc: 'Most requests are update checks that <b>need only one search</b> (regulatory notices); few need all three.' }
    ],
    runs: {
      A: [
        { steps: [ask3(),
            S('loop', 'Coordinator judges complexity and picks subagents', 'Option A.', 'Coordinator: "This question needs literature, registry and notices." \u2192 selected: 3 of 3'),
            ].concat(serialRun('Wait unchanged: all three were needed, so all three ran, still one at a time', 'Nothing could be skipped. In 2 of 20 runs it skipped notices on a "simple" request and missed a safety notice.', 'bad'), [
            S('cust', 'Committee receives the summary after 345 s', '', SUMM3, 'warn')]),
          outcome: { ok: false, text: 'Selecting subagents saves time only when some can be skipped. Every request needs all three, so the same three run in the same order.' }, rate: 0.1 },
        { steps: [ask3(),
            res('Coordinator sends three Task calls in one response', 'Option B: three tool_use blocks together. The SDK runs them at the same time.', [task('toolu_01', 'literature-search', P_LIT), task('toolu_02', 'trial-registry-search', P_REG), task('toolu_03', 'notices-search', P_NOT)], 'tool_use', 'ok'),
            X(S('sub', 'All three subagents run at once', 'Each result is ready when it is ready. The wait is the slowest search, not the sum.', { 'toolu_03': 'notices: none (70 s)', 'toolu_02': '2 registered trials (95 s)', 'toolu_01': '9 RCTs (140 s)' }),
              { table: { head: head3, rows: [['Coordinator turn 1', '0 s', '10 s'], ['notices-search', '10 s', '80 s'], ['trial-registry-search', '10 s', '105 s'], ['literature-search', '10 s', '150 s'], ['Synthesis turn', '150 s', '160 s']] } }),
            req('All three results go back in one user turn', '', { tools: ['Task'], messages: ['\u2026', { role: 'user', content: [R('toolu_01', '9 RCTs \u2026'), R('toolu_02', '2 registered trials \u2026'), R('toolu_03', 'no notices')] }] }),
            S('cust', 'Committee receives the summary after 160 s', 'Was 345 s.', SUMM3, 'ok')],
          outcome: { ok: true, text: 'The searches are independent, so they go out together. The wait drops from the sum of the three to the slowest one.' }, rate: 0.95 },
        { steps: [ask3(),
            res('Coordinator sends one Task call to a merged search subagent', 'Option C.', [task('toolu_01', 'all-search', P_LIT + ' ' + P_REG + ' ' + P_NOT)], 'tool_use'),
            X(S('sub', 'Merged subagent runs the searches itself, one after another', 'Three roles and three result sets now crowd one context.', 'journals \u2192 registry \u2192 notices   elapsed: 330 s', 'bad'),
              { meter: { total: 200000, parts: [{ label: 'system: three roles', tokens: 6000, kind: 'sys' }, { label: 'journal results', tokens: 41000, kind: 'tool' }, { label: 'registry results', tokens: 22000, kind: 'tool' }, { label: 'notices results', tokens: 15000, kind: 'tool' }] } }),
            S('cust', 'Committee receives the summary after 340 s', '', SUMM3, 'warn')],
          outcome: { ok: false, text: 'One subagent with every tool still searches in series, and mixes three jobs in one context. The time is lost to sequencing.' }, rate: 0.1 },
        { steps: [ask3(),
            S('loop', 'Search subagents return trimmed fields', 'Option D. The coordinator reads 2k tokens per result instead of 9k.', { trimmed_to: ['trial', 'n', 'result', 'paper', 'section'] }),
            ].concat(serialRun('Each coordinator turn is 2 s quicker; the searches still run one at a time', 'Elapsed 339 s instead of 345 s. The 305 s of searching is untouched.', 'bad'), [
            S('cust', 'Committee receives the summary after 339 s', '', SUMM3, 'warn')]),
          outcome: { ok: false, text: 'Trimming saves context tokens. The wait comes from running independent searches one after another.' }, rate: 0.1 }
      ],
      B: (function () {
        var mixHead = ['Request kind (20 runs)', 'Searches needed', 'Wait, selected + serial', 'Wait, all three parallel'];
        var mixRows = [['Update check (16)', 'notices', '80 s', '160 s'], ['Trial question (3)', 'literature + registry', '255 s', '160 s'], ['New topic (1)', 'all three', '345 s', '160 s'], ['Average', '', '118 s', '160 s']];
        var upd = 'Update check: any new safety notices on early mobilisation since our March summary?';
        return [
          { steps: [S('cust', 'Committee asks for an update check', '16 of 20 requests look like this.', upd),
              S('loop', 'Coordinator picks only the notices search', '', 'selected: notices-search (1 of 3)'),
              res('One Task call', '', [task('toolu_03', 'notices-search', 'Find notices on early mobilisation protocols since 2026-03-01.')], 'tool_use'),
              X(S('loop', 'Average wait drops most with selection', 'Searches that are not needed never run.', 'elapsed: 80 s', 'ok'), { table: { head: mixHead, rows: mixRows } }),
              S('cust', 'Committee receives the update after 80 s', '', 'No new notices since March. Summary unchanged.', 'ok')],
            outcome: { ok: true, text: 'Here most requests need one search, so skipping the rest cuts more than running all three at once. This is the world where the runner-up wins.' }, rate: 0.95 },
          { steps: [S('cust', 'Committee asks for an update check', '', upd),
              res('Three Task calls in one response', 'Two of them are not needed for an update check.', [task('toolu_01', 'literature-search', P_LIT), task('toolu_02', 'trial-registry-search', P_REG), task('toolu_03', 'notices-search', P_NOT)], 'tool_use'),
              X(S('loop', 'The wait is the slowest search, even when it was not needed', 'Every update check waits 140 s for a literature search it ignores, and pays for it.', 'elapsed: 160 s (60 searches run, 25 needed)', 'warn'), { table: { head: mixHead, rows: mixRows } }),
              S('cust', 'Committee receives the update after 160 s', '', 'No new notices since March.', 'ok')],
            outcome: { ok: true, warn: true, text: 'Parallel calls still beat the old 345 s, but most of the work is unneeded. Skipping it cuts the average further.' }, rate: 0.95 },
          { steps: [S('cust', 'Committee asks for an update check', '', upd),
              S('sub', 'Merged subagent runs all three searches in series', '', 'elapsed: 330 s', 'bad')],
            outcome: { ok: false, text: 'Merging neither skips nor parallelises.' }, rate: 0.1 },
          { steps: [S('cust', 'Committee asks for an update check', '', upd),
              S('loop', 'Trimmed results, three searches in series', '', 'elapsed: 339 s', 'bad')],
            outcome: { ok: false, text: 'Trimming saves tokens, not search time.' }, rate: 0.1 }
        ];
      })()
    }
  };

  /* ------------------------------------------------------------ m7-s3-10 structured error + partial results */
  var regTask = task('toolu_02', 'trial-registry-search', 'Find registered trials on early mobilisation after hip-fracture surgery, with posted 30-day mortality.');
  function start10(note) {
    return [S('cust', 'Committee asks', '', ASK3),
      res('Coordinator sends three Task calls in one response', '', [task('toolu_01', 'literature-search', P_LIT), regTask, task('toolu_03', 'notices-search', P_NOT)], 'tool_use'),
      S('sub', 'Literature and notices subagents finish', note || 'Finished work, held by the coordinator.', { 'toolu_01': '9 RCTs (n = 4,212) \u2026', 'toolu_03': 'no safety notices' })];
  }
  var down = S('tool', 'Registry MCP call fails partway through', 'The registry went down at 09:12. Outages like this last hours. 2 of 5 result pages were already read.', { error: '503 Service Unavailable', pages_read: 2, records_so_far: ['NCT05514492', 'NCT04882019'] }, 'warn');
  var crash = S('sub', 'Subagent raises an exception', 'Today\'s behaviour. Nothing goes back as a tool_result.', 'RegistryUnavailable: 503 from registry.example.org\n  \u2192 unhandled in subagent \u2192 run aborted', 'bad');
  var lost = S('cust', 'Committee receives nothing', 'The literature and notices results are thrown away with the run.', '(run failed: RegistryUnavailable)', 'bad');
  var structured = { status: 'failed', failure_type: 'source_unavailable', transient: false, detail: '503 since 09:12; status page reports a multi-hour outage', attempted_query: 'condition:"hip fracture" AND intervention:"early mobilisation" AND has_results', alternatives: ['WHO ICTRP mirror (no posted results)', 'wait for registry', 'publish with a noted gap'], partial_results: { records: ['NCT05514492 (posted 30-day mortality 5.8% vs 7.4%)', 'NCT04882019 (recruiting)'], pages_read: '2 of 5' } };
  function goodTail10(focus) {
    return [
      S('sub', 'Subagent returns a structured failure with its partial results', focus, null, 'ok'),
      req('Coordinator receives it as an error tool_result', 'is_error marks it as a failure. The run keeps going.', { tools: ['Task'], messages: ['\u2026', { role: 'user', content: [R('toolu_01', '9 RCTs \u2026'), E('toolu_02', JSON.stringify(structured)), R('toolu_03', 'no notices')] }] }),
      res('Coordinator chooses: publish with a noted gap', 'It has what it needs to decide: type, query, alternatives and the 2 records found.', [T('Registry is down for hours. I will publish with the two records retrieved and note the gap.'), task('toolu_04', 'report-writer', 'Draft the summary from 9 RCTs and registry records NCT05514492, NCT04882019. Note: registry search incomplete (2 of 5 pages) due to outage.')], 'tool_use'),
      S('cust', 'Committee receives the summary with a noted gap', '', SUMM3 + '\nNote: trial-registry search incomplete (registry outage 09:12); 2 of 5 result pages included.', 'ok')];
  }
  function withPayload(steps) { steps[0].payload = structured; return steps; }
  var s310 = {
    id: 'm7-s3-10', who: 'Committee', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Registry outages <b>last for hours</b>. The coordinator must choose: wait, switch source or publish with a gap.' },
      { id: 'B', label: 'Decider changed', desc: 'Registry failures are <b>brief blips</b>: a 503 that clears within a minute.' }
    ],
    runs: {
      A: [
        { steps: start10().concat([down,
            S('sub', 'Subagent retries locally with backoff', 'Option A. Nothing goes to the coordinator while it retries.', 'retry 1 after 30 s: 503\nretry 2 after 60 s: 503\nretry 3 after 2 min: 503\nretry 4 after 4 min: 503\nretry 5 after 8 min: 503\nretry 6 after 16 min: 503   (31 min gone)', 'warn'),
            S('sub', 'Retries used up: the exception is raised anyway', 'The outage lasts hours, so the backoff only delays the same crash.', 'RegistryUnavailable after 6 retries \u2192 run aborted', 'bad'),
            S('cust', 'Committee receives nothing, 31 minutes later', 'The coordinator never got to choose.', '(run failed: RegistryUnavailable)', 'bad')]),
          outcome: { ok: false, text: 'Backoff is right for a blip. These outages last hours, so retrying only delays the failure and keeps the coordinator from deciding.' }, rate: 0.05 },
        { steps: start10().concat([down], withPayload(goodTail10('Option B: failure type, the query it tried, and alternatives. (Paired with D, the 2 records already found ride along.)'))),
          outcome: { ok: true, text: 'A structured error tells the coordinator what failed, what was tried and what else could work, so it can choose the next step instead of the run ending.' }, rate: 1 },
        { steps: start10().concat([down,
            S('loop', 'Stack trace logged; on-call engineer paged', 'Option C. Useful for operations.', { dashboard: 'registry-subagent', alert: 'P2 RegistryUnavailable', paged: 'on-call: R. Iyer' }, 'warn'),
            crash, lost]),
          outcome: { ok: false, text: 'A person now knows. The coordinator still gets nothing to decide with, and the run still ends.' }, rate: 0.05 },
        { steps: start10().concat([down], withPayload(goodTail10('Option D: the two trial records read before the outage. (Paired with B, the failure type and query ride along.)'))),
          outcome: { ok: true, text: 'The records found before the outage are kept, so the coordinator can publish with a noted gap instead of losing them.' }, rate: 1 }
      ],
      B: (function () {
        var blip = S('tool', 'Registry MCP call returns 503', 'A blip: the registry is back 8 seconds later.', { error: '503 Service Unavailable', retry_after: '5 s' }, 'warn');
        var fine = S('cust', 'Committee receives the full summary', '', SUMM3, 'ok');
        return [
          { steps: start10().concat([blip,
              S('sub', 'Subagent retries locally with backoff', '', 'retry 1 after 2 s: 503\nretry 2 after 4 s: 200 OK (5 of 5 pages)', 'ok'),
              S('sub', 'Subagent returns complete results', 'The coordinator never sees the blip.', '2 registered trials; NCT05514492 posted 30-day mortality 5.8% vs 7.4%'), fine]),
            outcome: { ok: true, text: 'A blip clears in seconds, so the subagent handles it locally and returns full results. This is the world where the runner-up wins.' }, rate: 0.97 },
          { steps: start10().concat([blip,
              S('sub', 'Subagent returns a structured failure at once', 'A blip becomes a coordinator decision.', { failure_type: 'source_unavailable', transient: true }, 'warn'),
              res('Coordinator re-sends the registry task', 'An extra coordinator turn and a second subagent run for an 8-second blip.', [regTask], 'tool_use'), fine]),
            outcome: { ok: true, warn: true, text: 'It recovers, but it hands up a failure that a two-second retry would have fixed.' }, rate: 0.95 },
          { steps: start10().concat([blip, S('loop', 'On-call paged for a blip', '', { paged: 'on-call' }, 'warn'), crash, lost]),
            outcome: { ok: false, text: 'Paging does not stop the exception from ending the run.' }, rate: 0.6 },
          { steps: start10().concat([blip,
              S('sub', 'Subagent returns partial records with the failure', 'The other 3 pages were seconds away.', { partial_results: ['NCT05514492'], pages_read: '2 of 5' }, 'warn'),
              res('Coordinator re-sends the registry task', '', [regTask], 'tool_use'), fine]),
            outcome: { ok: true, warn: true, text: 'It works with an extra turn. A short retry would have returned everything.' }, rate: 0.95 }
        ];
      })()
    }
  };

  /* ------------------------------------------------------------ m7-s5-10 independent review instance */
  var PATCH = '--- a/booking/src/main/kotlin/com/trip/booking/FareCalculator.kt\n+++ b/\u2026\n-    fun total(b: Booking): Int = base(b) + TaxRules.cityTax(b)\n+    fun total(b: Booking): Int = base(b)   // tax now added by TaxRules.apply()';
  var CALLERS = 'payments/RefundService.kt:57    refund = FareCalculator.total(booking)        // expects tax included\ninvoicing/InvoiceBuilder.kt:112  line.amount = FareCalculator.total(booking)  // expects tax included';
  var CHECK = 'Check this patch for side effects. Look for: changed signatures, changed return meaning, changed units, removed defaults, callers in other modules.';
  var sameCtx = { total: 200000, parts: [{ label: 'system + CLAUDE.md', tokens: 9000, kind: 'sys' }, { label: 'fixing session: its own reasoning', tokens: 38000, kind: 'drop' }, { label: 'build log + files read', tokens: 21000, kind: 'tool' }, { label: 'check prompt', tokens: 1500, kind: 'new' }] };
  var freshCtx = { total: 200000, parts: [{ label: 'system + CLAUDE.md', tokens: 9000, kind: 'sys' }, { label: 'diff', tokens: 1200, kind: 'keep' }, { label: 'Grep of callers + files read', tokens: 14000, kind: 'tool' }, { label: 'check prompt', tokens: 1500, kind: 'new' }] };
  function open510() {
    return [S('cust', 'Build #4230 fails; autofix job starts', 'TaxServiceTest expects total() without city tax.', 'FAIL TaxServiceTest > totalExcludesCityTax'),
      S('tool', 'Autofix patch compiles and the test passes', 'Callers in payments/ and invoicing/ still compile. They now get a total with no tax.', PATCH)];
  }
  var approve = S('cust', 'Patch approved and merged', 'Two days later refunds come out short by the city tax.', 'payments: refund for BK-77120 = 18,400 (expected 19,320)', 'bad');
  var flagged = S('cust', 'Patch blocked with the finding', '', 'autofix #4231 held: total() no longer includes city tax; 2 callers in payments/ and invoicing/ expect it.', 'ok');
  var freshCall = 'claude -p "' + CHECK + '" --allowedTools "Read,Grep" --output-format json < patch.diff';
  var s510 = {
    id: 'm7-s5-10', who: 'CI job', labels: { loop: 'CI job' }, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'The side-effect check runs <b>in the same session that wrote the patch</b>, and approves nearly everything.' },
      { id: 'B', label: 'Decider changed', desc: 'The check <b>already runs as a fresh <code>claude -p</code> call</b>, and still misses patches that change what a value means to callers.' }
    ],
    runs: {
      A: [
        { steps: open510().concat([
            S('loop', 'Same session gets the check prompt plus worked examples', 'Option A: three past patches that broke callers, each with its clue.', CHECK + '\n\nExample 1: patch made price() return cents; clue: callers multiply by 100\u2026\n(+2 more)'),
            X(S('ctx', 'What the checker has in context', 'Its own reasoning for the patch is still there: "tax belongs in TaxRules.apply()".', 'same session', 'warn'), { meter: sameCtx }),
            res('Checker approves', 'It reads the code through the reasoning that produced it.', [T('{"approved": true, "note": "Tax moved to TaxRules.apply() by design; matches example patterns: none."}')], 'end_turn', 'bad'),
            approve]),
          outcome: { ok: false, text: 'Examples sharpen a reviewer that lacks a category. This reviewer is the author, still holding the reasoning that made the patch, so it confirms its own choice.' }, rate: 0.4 },
        { steps: open510().concat([
            req('Same session, extended thinking on', 'Option B.', { thinking: { type: 'enabled', budget_tokens: 8000 }, messages: ['\u2026fixing session\u2026', { role: 'user', content: CHECK + ' Trace each changed signature step by step.' }] }),
            res('Checker thinks longer, then approves', 'The trace re-tells why the patch was right.', [{ type: 'thinking', thinking: 'total() signature unchanged. I moved tax to TaxRules.apply(), which is the cleaner design\u2026 callers unaffected.' }, T('{"approved": true}')], 'end_turn', 'bad'),
            approve]),
          outcome: { ok: false, text: 'More thinking in the same session mostly re-confirms the author\'s reasoning.' }, rate: 0.4 },
        { steps: open510().concat([
            S('loop', 'Job runs the check as a fresh claude -p call', 'Option C: it gets the diff and the repository, not the fixing session.', freshCall, 'ok'),
            X(S('ctx', 'What the reviewer has in context', 'No author reasoning. Only the change and the code.', 'fresh instance', 'ok'), { meter: freshCtx }),
            S('tool', 'Reviewer greps for callers of total()', '', CALLERS),
            res('Reviewer flags both callers', '', [T('{"approved": false, "side_effects": [{"function": "FareCalculator.total", "change": "no longer includes city tax", "callers": ["RefundService.kt:57", "InvoiceBuilder.kt:112"]}]}')], 'end_turn', 'ok'),
            flagged]),
          outcome: { ok: true, text: 'A fresh instance has no stake in the patch. It reads what the code does now and finds the callers that depend on the old meaning.' }, rate: 0.92 },
        { steps: open510().concat([
            req('Same session, output schema needs side_effects per changed function', 'Option D.', { tools: [{ name: 'report_check', input_schema: { required: ['approved', 'side_effects'] } }], tool_choice: { type: 'tool', name: 'report_check' }, messages: ['\u2026fixing session\u2026', { role: 'user', content: CHECK }] }),
            res('Checker fills the field', 'A required field is filled just as confidently.', [U('toolu_31', 'report_check', { approved: true, side_effects: [{ function: 'FareCalculator.total', effect: 'none' }] })], 'tool_use', 'bad'),
            approve]),
          outcome: { ok: false, text: 'A schema shapes the report. The same reader fills it with "none".' }, rate: 0.4 }
      ],
      B: (function () {
        var freshNow = S('loop', 'Check already runs as a fresh claude -p call', '', freshCall);
        var miss = res('Independent reviewer approves', 'It sees the change but does not treat "tax no longer included" as a caller-facing change.', [T('{"approved": true, "note": "Signature unchanged; no compile-level impact."}')], 'end_turn', 'bad');
        return [
          { steps: open510().concat([freshNow,
              S('file', 'Check prompt gains worked examples', 'Each example shows a patch that changed a value\'s meaning, and the clue.', 'Example: patch dropped VAT from net(); clue: callers use the result as a gross amount.\n(+2 more)', 'ok'),
              S('tool', 'Reviewer greps for callers of total()', '', CALLERS),
              res('Reviewer flags both callers', 'It now knows this category.', [T('{"approved": false, "side_effects": [{"function": "FareCalculator.total", "change": "city tax removed", "callers": 2}]}')], 'end_turn', 'ok'),
              flagged]),
            outcome: { ok: true, text: 'The reviewer is already independent and misses one category, so examples of that category are the next fix. This is the world where the runner-up wins.' }, rate: 0.92 },
          { steps: open510().concat([freshNow,
              res('Reviewer thinks longer, still approves', 'Thinking time does not add the missing category.', [T('{"approved": true}')], 'end_turn', 'bad'), approve]),
            outcome: { ok: false, text: 'More thinking cannot teach a pattern the reviewer does not look for.' }, rate: 0.55 },
          { steps: open510().concat([freshNow,
              S('loop', 'Option C changes nothing', 'The check is already a fresh instance.', '(no change)', 'warn'), miss, approve]),
            outcome: { ok: false, text: 'The reviewer is already independent. The gap is in what it knows to look for.' }, rate: 0.5 },
          { steps: open510().concat([freshNow,
              res('Reviewer fills side_effects with "none"', '', [U('toolu_31', 'report_check', { approved: true, side_effects: [{ function: 'FareCalculator.total', effect: 'none' }] })], 'tool_use', 'bad'), approve]),
            outcome: { ok: false, text: 'A field to fill is not a pattern to recognise.' }, rate: 0.5 }
        ];
      })()
    }
  };

  /* ------------------------------------------------------------ m7-s6-07 facts into each subagent prompt */
  var EMAIL = 'From: Priya Shah (broker)\nClient: Linden Bakery LLC.\nCOI-8101 covers 12 Mill St (bakery).\nCOI-8102 covers 40 Dock Rd (warehouse).\nCOI-8103 covers 7 Elm Ave (retail shop).';
  var CERT2 = 'COI-8102  Harbor Specialty Ins. Co.  Policy HSP-4471902\nInsured: Linden Bakery LLC, 12 Mill St (mailing address)\nProperty: Building $2,000,000  Deductible $5,000';
  var LOCS = 'Client: Linden Bakery LLC. Locations: COI-8101 = 12 Mill St; COI-8102 = 40 Dock Rd; COI-8103 = 7 Elm Ave.';
  function open607() {
    return [S('cust', 'Submission SUB-2291 arrives: cover email + 3 certificates', '', EMAIL),
      S('loop', 'Coordinator reads the email', 'It now knows the client and which location each certificate covers.', { client: 'Linden Bakery LLC', locations: { 'COI-8101': '12 Mill St', 'COI-8102': '40 Dock Rd', 'COI-8103': '7 Elm Ave' } })];
  }
  var wrongLoc = S('sub', 'COI-8102 subagent assigns the location', 'The only address on the certificate is the mailing address.', { certificate: 'COI-8102', location: '12 Mill St', building_limit: 2000000 }, 'bad');
  var postedWrong = S('tool', 'Posted to the broker\'s system', '', { certificate: 'COI-8102', location: '12 Mill St (should be 40 Dock Rd)', status: 'posted' }, 'bad');
  var s607 = {
    id: 'm7-s6-07', who: 'Pipeline', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'The coordinator <b>already holds the client and location list</b>; each subagent receives only its certificate.' },
      { id: 'B', label: 'Decider changed', desc: 'Cover emails are long threads, and each certificate needs <b>a different, unpredictable fact</b> from them (a location, an added insured, a corrected policy number).' }
    ],
    runs: {
      A: [
        { steps: open607().concat([
            res('Coordinator spawns 3 subagents with the facts in each prompt', 'Option A.', [task('toolu_01', 'cert-extract', 'Extract COI-8101. ' + LOCS), task('toolu_02', 'cert-extract', 'Extract COI-8102. ' + LOCS), task('toolu_03', 'cert-extract', 'Extract COI-8103. ' + LOCS)], 'tool_use'),
            S('ctx', 'What the COI-8102 subagent receives', 'Its certificate, plus the client and location list, in its own prompt.', { messages: [{ role: 'user', content: 'Extract COI-8102. ' + LOCS + '\n\n' + CERT2 }] }, 'ok'),
            S('sub', 'COI-8102 subagent assigns the location', 'It knows 12 Mill St is only the mailing address.', { certificate: 'COI-8102', location: '40 Dock Rd', building_limit: 2000000 }, 'ok'),
            S('tool', 'All three post with the right locations', '', [{ 'COI-8101': '12 Mill St' }, { 'COI-8102': '40 Dock Rd' }, { 'COI-8103': '7 Elm Ave' }], 'ok')]),
          outcome: { ok: true, text: 'Subagents inherit nothing. The coordinator already had the exact facts, so writing them into each prompt gives every subagent what it needs, every time.' }, rate: 0.96 },
        { steps: open607().concat([
            res('Coordinator spawns 3 subagents, told to call get_cover_email first', 'Option B: a scoped tool to read the email.', [task('toolu_01', 'cert-extract', 'Extract COI-8101. Call get_cover_email first.'), task('toolu_02', 'cert-extract', 'Extract COI-8102. Call get_cover_email first.'), task('toolu_03', 'cert-extract', 'Extract COI-8103. Call get_cover_email first.')], 'tool_use'),
            S('tool', 'Two subagents call get_cover_email', 'An extra round trip each, to fetch facts the coordinator already had.', { calls: 2, each: '1 round trip, 1.1k tokens of email' }, 'warn'),
            S('sub', 'The COI-8102 subagent skips the call', 'Calling the tool is an instruction it can skip. Its certificate already shows an address.', '(no get_cover_email call)', 'bad'),
            wrongLoc, postedWrong]),
          outcome: { ok: false, text: 'A fetch tool adds a step that a subagent can skip, for facts the coordinator already held. Passing them in the prompt is simpler and certain.' }, rate: 0.85 },
        { steps: open607().concat([
            S('loop', 'Client and locations added to the coordinator\'s system prompt', 'Option C.', { system: 'You coordinate certificate extraction\u2026\n' + LOCS }),
            res('Coordinator spawns subagents: "Extract this certificate."', '', [task('toolu_02', 'cert-extract', 'Extract this certificate.')], 'tool_use'),
            S('ctx', 'What the COI-8102 subagent receives', 'Only its certificate. The coordinator\'s system prompt is not passed on.', { messages: [{ role: 'user', content: 'Extract this certificate.\n\n' + CERT2 }] }, 'bad'),
            wrongLoc, postedWrong]),
          outcome: { ok: false, text: 'Right facts, wrong agent. Subagents never see the coordinator\'s system prompt.' }, rate: 0.4 },
        { steps: open607().concat([
            res('Subagents spawned as before, asked for a location guess', 'Option D.', [task('toolu_02', 'cert-extract', 'Extract this certificate. Include your best location guess.')], 'tool_use'),
            S('sub', 'COI-8102 subagent guesses 12 Mill St', 'It also reads the limits and deductible for the 12 Mill St row of a two-row schedule.', { location: '12 Mill St', building_limit: 750000, deductible: 2500 }, 'warn'),
            S('loop', 'Coordinator corrects the location from the email', 'The location is fixed. The limits were read for the wrong building.', { location: '40 Dock Rd', building_limit: 750000, deductible: 2500 }, 'bad'),
            S('tool', 'Posted with the bakery\'s limits on the warehouse', '', { certificate: 'COI-8102', location: '40 Dock Rd', building_limit: '750,000 (should be 2,000,000)', status: 'posted' }, 'bad')]),
          outcome: { ok: false, text: 'Checking afterwards fixes one field. Everything else was still extracted without the context.' }, rate: 0.6 }
      ],
      B: (function () {
        var thread = S('cust', 'Submission SUB-2340 arrives: a 40-message email thread + 12 certificates', 'Locations, added insureds and a corrected policy number are scattered through the replies.', 'Thread: 40 messages, 31 locations, 2 endorsements, 1 correction ("COI-9007 policy number should read HSP-4471902-A")');
        var plan = S('loop', 'Coordinator cannot tell in advance what each certificate will need', '', 'COI-9003 needs: location?  COI-9005: added insured?  COI-9007: corrected policy no.?  (unknown until extraction)');
        return [
          { steps: [thread, plan,
              res('Each prompt gets the client and the location list', 'Option A, as written.', [task('toolu_07', 'cert-extract', 'Extract COI-9007. Client: Linden Bakery LLC. Locations: \u2026 31 entries \u2026')], 'tool_use'),
              S('sub', 'COI-9007 posts the old policy number', 'The correction was in message 31, which no prompt carried.', { certificate: 'COI-9007', policy_number: 'HSP-4471902 (should be HSP-4471902-A)' }, 'bad')],
            outcome: { ok: false, text: 'Locations alone do not cover the other facts each certificate needs, and nobody knows in advance which ones.' }, rate: 0.6 },
          { steps: [thread, plan,
              res('Coordinator spawns 12 subagents, each with a scoped get_cover_email(query) tool', 'Read-only, this submission only.', [task('toolu_07', 'cert-extract', 'Extract COI-9007. Use get_cover_email(query) for anything the certificate leaves open.')], 'tool_use'),
              S('tool', 'COI-9007 subagent asks the thread its own question', 'Only the lookups each subagent needs, when it needs them.', { query: 'corrections for COI-9007', result: 'Msg 31: policy number should read HSP-4471902-A' }, 'ok'),
              S('tool', 'All 12 post correctly', '', { posted: 12, lookups: 17, wrong: 0 }, 'ok')],
            outcome: { ok: true, text: 'When each subagent needs different facts nobody can list in advance, a scoped lookup tool lets it fetch exactly what it needs. This is the world where the runner-up wins.' }, rate: 0.92 },
          { steps: [thread, S('loop', 'Facts go in the coordinator\'s system prompt', '', '\u2026'), S('sub', 'Subagents see only their certificates', '', '(no thread facts)', 'bad')],
            outcome: { ok: false, text: 'The coordinator\'s prompt never reaches subagents.' }, rate: 0.3 },
          { steps: [thread, S('loop', 'Coordinator checks only the location guesses', 'The corrected policy number and added insureds go unchecked.', { checked: 'location', unchecked: ['policy_number', 'additional_insured'] }, 'bad')],
            outcome: { ok: false, text: 'Checking one field afterwards misses the others.' }, rate: 0.5 }
        ];
      })()
    }
  };

  /* ------------------------------------------------------------ m7-s6-09 stratified sample + calibrated field confidence */
  var uniHead = ['Document type', 'Docs in sample', 'Field accuracy'];
  var uniRows = [['Text PDF certificates', '380', '99.1%'], ['Scans, large carriers', '100', '97.4%'], ['Scans, small carriers', '20', '91% (only 20 docs)'], ['All documents', '500', '98.5%']];
  var stratRows = [['Text PDF certificates', '150', '99.0%'], ['Scans, large carriers', '150', '97.2%'], ['Scans, small carriers', '150', '86.4%'], ['  of which limits and deductibles', '150', '74.0%']];
  var calHead = ['Field (small-carrier scans)', 'Model says', 'Actually right', 'Calibrated cutoff'];
  var calRows = [['insured_name', '0.95', '98%', '0.80'], ['policy_number', '0.95', '96%', '0.85'], ['limit / deductible', '0.95', '74%', '0.99'], ['expiry_date', '0.95', '93%', '0.92']];
  var POL = 'Compliance: error rate for each document type before any field skips review.';
  function stratStep(mark, note) {
    return X(S('loop', 'Label a new sample with a quota of 150 per document type', note, 'sample = {doc_type: draw(150) for doc_type in TYPES}   # 450 labelled docs', mark), { table: { head: uniHead, rows: stratRows } });
  }
  function calStep(mark, note) {
    return X(S('loop', 'Calibrate each field\'s confidence on the labelled set; set a cutoff per field', note, 'cutoff[field] = lowest score where labelled accuracy >= 99%', mark), { table: { head: calHead, rows: calRows } });
  }
  function pairTail() {
    return [S('cust', 'Compliance signs off per type', 'Text PDFs and large-carrier scans may skip review below the cutoffs. Small-carrier limits always go to a person.', POL + '\nApproved: 3 types measured, small-carrier scans flagged.', 'ok'),
      S('tool', 'COI-8840 (small carrier scan): fields routed', 'Only the doubtful fields go to an account assistant.', { posted: ['insured_name', 'policy_number', 'expiry_date'], to_review: [{ field: 'building_limit', value: 250000, calibrated: 0.74 }] }, 'ok'),
      S('cust', 'Account assistant reviews one field', '', 'Limit reads $2,500,000 on the scan, not $250,000. Corrected.', 'ok')];
  }
  var s609 = {
    id: 'm7-s6-09', who: 'Reviewer', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Accuracy is high on a <b>uniform</b> sample where small-carrier scans are rare; compliance wants <b>per-type</b> error rates, and nothing is calibrated yet.' },
      { id: 'B', label: 'Decider changed', desc: 'A stratified labelled set already exists, compliance has signed off per type, and the model\'s own field confidence <b>has been checked against it and tracks accuracy</b> in every type.' }
    ],
    runs: {
      A: [
        { steps: [X(S('loop', 'Today: accuracy from a uniform random sample', 'High overall, with only 20 small-carrier scans.', 'overall field accuracy: 98.5%'), { table: { head: uniHead, rows: uniRows } }),
            S('loop', 'Model reports a confidence per field; fields under 0.90 go to review', 'Option A. No labelled check of what "0.95" means.', 'if field.confidence < 0.90: review(field) else: post(field)'),
            X(S('tool', 'Small-carrier limits post directly', 'The model says 0.95. Nobody has checked what 0.95 means: in fact about 1 in 4 of these limits is wrong, and all of them skip review.', { field: 'building_limit', value: 250000, model_confidence: 0.95, routed: 'posted', truth: 2500000 }, 'bad'), { table: { head: calHead, rows: calRows.map(function (r) { return [r[0], r[1], 'unknown', '0.90 for all']; }) } }),
            S('cust', 'Compliance: no per-type error rate, no sign-off', '', POL + '\nNot met: no measurement for small-carrier scans.', 'bad')],
          outcome: { ok: false, text: 'Routing per field is the right shape, but an unchecked confidence posts wrong limits at 0.95, and nothing gives compliance a rate per type.' }, rate: 0.3 },
        { steps: [X(S('loop', 'Today: accuracy from a uniform random sample', 'The 98.5% average hides a weak type with only 20 documents.', 'overall field accuracy: 98.5%', 'warn'), { table: { head: uniHead, rows: uniRows } }),
            stratStep('ok', 'Option B. With 150 small-carrier scans, the weak type shows: limits and deductibles are right only 74% of the time.'),
            calStep('', 'Paired with D: the same labelled set calibrates each field.')].concat(pairTail()),
          outcome: { ok: true, text: 'A quota per type gives compliance a real error rate for every type, including the rare scans the uniform sample buried.' }, rate: 1 },
        { steps: [X(S('loop', 'Label a larger uniform sample: 2,000 documents', 'Option C. Small-carrier scans are still 4%: 80 documents, pooled with the rest.', 'sample = draw_uniform(2000)'), { table: { head: ['Field (all documents)', 'Docs', 'Accuracy'], rows: [['insured_name', '2000', '99.4%'], ['policy_number', '2000', '99.0%'], ['limit / deductible', '2000', '97.6%'], ['expiry_date', '2000', '98.8%']] } }),
            S('loop', 'Per-field figures look safe to automate', 'The 74% on small-carrier limits is averaged into 97.6%.', 'limit / deductible: 97.6%  \u2192  "post directly"', 'bad'),
            S('cust', 'Compliance: still no rate per document type', '', POL + '\nNot met: types pooled.', 'bad')],
          outcome: { ok: false, text: 'A bigger uniform sample keeps rare scans rare, and per-field figures still pool them with every other type.' }, rate: 0.2 },
        { steps: [X(S('loop', 'Today: accuracy from a uniform random sample', '', 'overall field accuracy: 98.5%', 'warn'), { table: { head: uniHead, rows: uniRows } }),
            stratStep('', 'Paired with B: the stratified labelled set.'),
            calStep('ok', 'Option D. Calibrated, "0.95" on a small-carrier limit means 74% right, so its cutoff is 0.99 and it goes to a person.')].concat(pairTail()),
          outcome: { ok: true, text: 'Calibrated field confidence says which individual fields are doubtful, so only those go to an account assistant.' }, rate: 1 }
      ],
      B: (function () {
        var have = X(S('loop', 'Already in place: stratified labelled set, per-type sign-off', 'And on it, the model\'s stated confidence matches real accuracy in every type.', 'validated: stated 0.95 \u2192 94-96% right in each type'), { table: { head: uniHead, rows: stratRows.slice(0, 3) } });
        return [
          { steps: [have,
              S('loop', 'Fields under 0.90 self-reported confidence go to review', 'The scores were already checked against labelled answers.', 'if field.confidence < 0.90: review(field)', 'ok'),
              S('tool', 'Small-carrier limit routed to review', 'Here the model says 0.62 on the smudged limit, and that number is trustworthy.', { field: 'building_limit', model_confidence: 0.62, routed: 'review' }, 'ok'),
              S('cust', 'Account assistant reviews one field', '', 'Limit corrected to $2,500,000.', 'ok')],
            outcome: { ok: true, text: 'Self-reported confidence is fine once it has been validated on labelled data, as it has here. This is the world where the runner-up wins.' }, rate: 0.95 },
          { steps: [have, S('loop', 'Label another 450 documents by type', 'Compliance already has these numbers.', '450 more labelled docs', 'warn')],
            outcome: { ok: true, warn: true, text: 'Useful for monitoring, but the measurement already exists.' }, rate: 0.95 },
          { steps: [have, S('loop', 'Label 2,000 uniform documents', 'Pools the types again; routes nothing.', 'limit / deductible: 97.6%', 'bad')],
            outcome: { ok: false, text: 'A pooled number neither measures types nor routes fields.' }, rate: 0.3 },
          { steps: [have, S('loop', 'Re-fit per-field cutoffs', 'The validated scores barely move.', 'cutoff shifts: 0.90 \u2192 0.89-0.91', 'warn')],
            outcome: { ok: true, warn: true, text: 'Works, with calibration work the validated scores did not need.' }, rate: 0.95 }
        ];
      })()
    }
  };

  /* ------------------------------------------------------------ m7-s6-10 provenance per value */
  var FLAG = 'Flagged: COI-8102 against policy schedule HSP-4471902 (38 pages)';
  var timeHead = ['Field', 'Where it is', 'Time to find'];
  var s610 = {
    id: 'm7-s6-10', who: 'Reviewer', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Schedules run to dozens of pages, and <b>most review time goes into finding where each value was printed</b>.' },
      { id: 'B', label: 'Decider changed', desc: 'Certificates are one page with 30 fields; finding a value takes seconds, and <b>the time goes into checking every field</b> because nothing says which are doubtful.' }
    ],
    runs: {
      A: [
        { steps: [S('cust', 'Account assistant opens a flagged certificate', '', FLAG),
            S('tool', 'Extraction returns each value with page and quoted text', 'Option A.', { gl_each_occurrence: { value: 1000000, page: 17, quote: 'Each Occurrence ......... $1,000,000' }, gl_deductible: { value: 2500, page: 17, quote: 'Deductible per claim $2,500' }, expiry_date: { value: '2027-03-01', page: 1, quote: 'Policy Period: 03/01/2026 to 03/01/2027' } }, 'ok'),
            X(S('cust', 'Assistant clicks each value and lands on the line', '', 'Each value checked against its quoted line.', 'ok'), { table: { head: timeHead, rows: [['gl_each_occurrence', 'p.17, quoted', '10 s'], ['gl_deductible', 'p.17, quoted', '8 s'], ['expiry_date', 'p.1, quoted', '5 s'], ['Whole review', '', '2 min (was 14)']] } })],
          outcome: { ok: true, text: 'The time was spent finding values. A page and quote per value take the reviewer straight to the evidence.' }, rate: 0.95 },
        { steps: [S('cust', 'Account assistant opens a flagged certificate', '', FLAG),
            S('tool', 'Extraction returns a calibrated confidence per field', 'Option B. The review opens on the lowest score.', { gl_each_occurrence: { value: 1000000, confidence: 0.81 }, gl_deductible: { value: 2500, confidence: 0.88 }, expiry_date: { value: '2027-03-01', confidence: 0.99 } }),
            X(S('cust', 'Assistant starts on gl_each_occurrence, then hunts for it', 'The score says which field to check first, not where it was printed.', 'Scrolling 38 pages for "$1,000,000"\u2026', 'bad'), { table: { head: timeHead, rows: [['gl_each_occurrence', 'unknown', '5 min'], ['gl_deductible', 'unknown', '4 min'], ['expiry_date', 'unknown', '1 min'], ['Whole review', '', '13 min (was 14)']] } })],
          outcome: { ok: false, text: 'Ordering helps decide what to check first. The time goes into finding where each value came from, and a score does not say.' }, rate: 0.2 },
        { steps: [S('cust', 'Account assistant opens a flagged certificate', '', FLAG),
            S('tool', 'Viewer highlights every place each value\'s text appears', 'Option C.', { '$1,000,000': '14 matches on 9 pages', '$2,500': '6 matches on 5 pages', '03/01/2027': '3 matches' }, 'warn'),
            X(S('cust', 'Assistant works out which match the model used', 'Limits repeat across a schedule: GL, products, umbrella, each location.', 'p.4? p.17? p.22? \u2026 which $1,000,000 is GL each occurrence?', 'bad'), { table: { head: timeHead, rows: [['gl_each_occurrence', '1 of 14 matches', '4 min'], ['gl_deductible', '1 of 6 matches', '2 min'], ['expiry_date', '1 of 3 matches', '30 s'], ['Whole review', '', '9 min (was 14)']] } })],
          outcome: { ok: false, text: 'Close, but common values repeat, so the assistant still has to work out which match was used.' }, rate: 0.4 },
        { steps: [S('cust', 'Account assistant opens a flagged certificate', '', FLAG),
            S('tool', 'Values grouped under the schedule\'s section headings', 'Option D.', { 'Section 4 - Liability Coverages (pp. 12-24)': { gl_each_occurrence: 1000000, gl_deductible: 2500 }, 'Declarations (pp. 1-3)': { expiry_date: '2027-03-01' } }),
            X(S('cust', 'Assistant searches a 13-page section', 'Narrower, but the exact line is still unknown.', 'Scrolling pp. 12-24 for "$1,000,000"\u2026', 'bad'), { table: { head: timeHead, rows: [['gl_each_occurrence', 'somewhere in pp. 12-24', '4 min'], ['gl_deductible', 'somewhere in pp. 12-24', '3 min'], ['expiry_date', 'pp. 1-3', '1 min'], ['Whole review', '', '10 min (was 14)']] } })],
          outcome: { ok: false, text: 'A section narrows the search; sections span pages, so the hunt goes on.' }, rate: 0.3 }
      ],
      B: (function () {
        var flagB = 'Flagged: COI-9120 (one page, 30 fields)';
        var bHead = ['Approach', 'Fields checked', 'Review time'];
        return [
          { steps: [S('cust', 'Account assistant opens a flagged certificate', '', flagB),
              S('tool', 'Each value comes with page and quote', 'Every value is on page 1; finding one already took seconds.', { gl_each_occurrence: { value: 1000000, page: 1, quote: 'EACH OCCURRENCE $1,000,000' }, '\u2026': '29 more, all page 1' }),
              X(S('cust', 'Assistant still checks all 30 fields', 'Nothing says which fields are doubtful.', '30 of 30 checked', 'warn'), { table: { head: bHead, rows: [['Today', '30', '9 min'], ['Page + quote', '30', '8 min']] } })],
            outcome: { ok: false, text: 'On a one-page certificate the hunt was never the cost. Choosing which fields to check is.' }, rate: 0.3 },
          { steps: [S('cust', 'Account assistant opens a flagged certificate', '', flagB),
              S('tool', 'Review opens on the lowest calibrated scores', 'Fields above the calibrated cutoff are marked safe to skip.', { to_check: [{ field: 'umbrella_limit', confidence: 0.71 }, { field: 'gl_deductible', confidence: 0.84 }, { field: 'additional_insured', confidence: 0.88 }], safe: '27 fields >= 0.98' }, 'ok'),
              X(S('cust', 'Assistant checks 3 fields and approves', '', 'Umbrella limit corrected to $5,000,000. Approved.', 'ok'), { table: { head: bHead, rows: [['Today', '30', '9 min'], ['Calibrated order', '3', '2 min']] } })],
            outcome: { ok: true, text: 'Here the time goes into deciding which fields to check, and calibrated scores answer exactly that. This is the world where the runner-up wins.' }, rate: 0.95 },
          { steps: [S('cust', 'Account assistant opens a flagged certificate', '', flagB),
              S('tool', 'Matches highlighted on page 1', '', { highlights: 30 }), S('cust', 'Assistant still checks all 30 fields', '', '30 of 30 checked', 'warn')],
            outcome: { ok: false, text: 'Highlights show where, not which to check.' }, rate: 0.3 },
          { steps: [S('cust', 'Account assistant opens a flagged certificate', '', flagB),
              S('tool', 'Values grouped by section', '', { sections: 4 }), S('cust', 'Assistant still checks all 30 fields', '', '30 of 30 checked', 'warn')],
            outcome: { ok: false, text: 'Grouping does not say which fields are doubtful.' }, rate: 0.3 }
        ];
      })()
    }
  };

  [s302, s303, s310, s510, s607, s609, s610].forEach(L.add);
})();
