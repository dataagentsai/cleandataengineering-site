/* CCA-F Mock Exam #7 - scripted simulations for m7-s4-09, m7-s4-10, m7-s5-09, m7-s6-03, m7-s6-06, m7-s6-08.
   Uses the helper library in sims.js (window.SIMLIB). Hand-written, deterministic traces. */
(function () {
  var L = window.SIMLIB, S = L.S, req = L.req, res = L.res, T = L.T, U = L.U, R = L.R, E = L.E;

  /* ------------------------------------------------------------ m7-s4-09 PreToolUse vs PostToolUse on run_sql */
  var SQL = 'mcp__staging_pg__run_sql';
  var ask409 = 'Why does user 8812\'s streak reset at midnight UTC instead of local midnight? Investigate on staging.';
  var ask409b = 'User 8812\'s streak reset overnight. Reproduce it on staging and find the cause.';
  var readCall = U('toolu_21', SQL, { sql: 'SELECT tz, streak_days, last_lesson_at FROM users WHERE id = 8812' });
  var readRows = { rows: [{ tz: 'Asia/Kolkata', streak_days: 0, last_lesson_at: '2026-10-03T18:40:00Z' }], rows_affected: 0 };
  var delText = 'These lesson_progress rows look corrupted. I\'ll clear them and re-check.';
  var delCall = U('toolu_27', SQL, { sql: 'DELETE FROM lesson_progress WHERE user_id = 8812' });
  var updCall = U('toolu_27', SQL, { sql: 'UPDATE users SET last_lesson_at = \'2026-10-03T18:40:00Z\', streak_days = 14 WHERE id = 8812' });
  var preHook = 'def guard_sql(input_data, tool_use_id, context):\n    sql = input_data["tool_input"]["sql"]\n    if not is_read_only(sql):      # SELECT / EXPLAIN / WITH ... SELECT\n        return {"hookSpecificOutput": {\n            "hookEventName": "PreToolUse",\n            "permissionDecision": "deny",\n            "permissionDecisionReason": "Read-only script: run_sql accepts SELECT only."}}\n    return {}';
  var postHook = 'def halt_on_change(input_data, tool_use_id, context):\n    n = input_data["tool_response"]["rows_affected"]\n    if n > 0:\n        return {"continue": False,\n                "stopReason": f"run_sql changed {n} row(s). Engineer review needed."}\n    return {}';
  var rootCause = 'Root cause: StreakResetJob uses Time.now.utc.beginning_of_day and ignores users.tz, so Kolkata users are reset at 05:30 local time.';

  function open409(a, sys) {
    var body = { tools: [SQL], messages: [{ role: 'user', content: a }] };
    if (sys) body.system = sys;
    return [S('cust', 'Engineer starts an investigation', '', a),
      req('Script sends the request', sys ? 'The system prompt now carries the read-only rule.' : '', body),
      res('Claude reads the user row', 'The first of many reads in this investigation.', [readCall], 'tool_use'),
      S('tool', 'run_sql runs the SELECT (and 30 more like it)', 'Reads are the bulk of the work.', { input: readCall.input, output: readRows })];
  }

  var s409 = {
    id: 'm7-s4-09', who: 'Engineer', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Statements that change data <b>must never run</b> from this script; Claude needs many reads per investigation.' },
      { id: 'B', label: 'Decider changed', desc: 'Claude <b>may run writes to reproduce a bug</b> (staging restores hourly); the script must <b>stop after any statement that actually changed rows</b>.' }
    ],
    runs: {
      A: [
        { steps: open409(ask409, 'Only run SELECT or EXPLAIN statements.\nExample: if asked to "clean up test rows", refuse and explain.\nExample: never run DELETE, UPDATE, INSERT or TRUNCATE.').concat([
            res('Claude decides the data is the problem', 'Mid-investigation, the rule competes with "fix what looks broken". This time it loses.', [T(delText), delCall], 'tool_use', 'warn'),
            S('tool', 'run_sql runs the DELETE', 'Nothing in code checked the statement.', { input: delCall.input, output: { rows_affected: 412 } }, 'bad'),
            S('cust', 'Engineer finds out later', 'A tester\'s data is gone again.', 'lesson_progress: 412 rows deleted for user 8812', 'bad')]),
          outcome: { ok: false, text: 'The rule and examples work in most runs. "Must never" cannot rest on most runs: one long investigation is enough for Claude to talk itself into a cleanup.' }, rate: 0.93 },
        { steps: [S('loop', 'Script settings ask the engineer before every run_sql', 'Option B.', { permissions: { ask: [SQL] } }),
            S('cust', 'Engineer starts an investigation', '', ask409),
            S('cust', 'Approval prompts 1 to 22: all SELECTs', 'The engineer approves read after read.', 'Allow run_sql? SELECT tz, streak_days ... FROM users WHERE id = 8812  [y/n]  y\nAllow run_sql? SELECT * FROM streak_events WHERE user_id = 8812 ...  [y/n]  y\n\u2026 (20 more)', 'warn'),
            S('cust', 'Approval prompt 23: the DELETE', 'The engineer is still paying attention, and says no.', 'Allow run_sql? DELETE FROM lesson_progress WHERE user_id = 8812  [y/n]  n', 'ok'),
            S('cust', 'Approval prompts 24 to 38', 'More reads, more interruptions. The script is no longer something you can leave running.', '\u2026 15 more SELECT approvals', 'warn')],
          outcome: { ok: true, warn: true, text: 'A person can stop the write, but only by approving 38 calls when one in 38 needed a decision. That is far heavier than the need, and a tired approver is a weak guard.' }, rate: 0.95 },
        { steps: [S('hook', 'PreToolUse hook on run_sql', 'Option C. Runs in your code before every run_sql call.', preHook)].concat(open409(ask409)).concat([
            res('Claude decides the data is the problem', '', [T(delText), delCall], 'tool_use'),
            S('hook', 'Hook sees a DELETE and denies the call', 'The statement never reaches the database.', { hookEventName: 'PreToolUse', permissionDecision: 'deny', permissionDecisionReason: 'Read-only script: run_sql accepts SELECT only.' }, 'ok'),
            S('api', 'Claude receives the reason as an error result', 'It carries the same tool_use_id, so Claude knows which call was refused and why.', { role: 'user', content: [E('toolu_27', 'Blocked by hook: Read-only script: run_sql accepts SELECT only.')] }),
            res('Claude adjusts and keeps investigating with reads', '', [T(rootCause)], 'end_turn'),
            S('cust', 'Engineer sees the answer; data intact', '', rootCause, 'ok')]),
          outcome: { ok: true, text: 'The check runs before the call, every time, in code. Reads flow through untouched, and the refusal tells Claude why so it can carry on.' }, rate: 1 },
        { steps: [S('hook', 'PostToolUse hook on run_sql', 'Option D. Runs after each run_sql call has finished.', postHook)].concat(open409(ask409)).concat([
            res('Claude decides the data is the problem', '', [T(delText), delCall], 'tool_use'),
            S('tool', 'run_sql runs the DELETE', 'Nothing checks the statement before it runs.', { input: delCall.input, output: { rows_affected: 412 } }, 'bad'),
            S('hook', 'Hook sees rows_affected = 412 and stops the script', 'Correctly detected, after the rows are already gone.', { continue: false, stopReason: 'run_sql changed 412 row(s). Engineer review needed.' }, 'warn'),
            S('cust', 'Engineer is told, too late', '', 'Script stopped: run_sql changed 412 row(s).\nlesson_progress for user 8812: empty', 'bad')]),
          outcome: { ok: false, text: 'A PostToolUse hook acts on results, so it can only report the first write. The requirement is that the write never runs, which needs a check before the call.' }, rate: 0.6 }
      ],
      B: [
        { steps: open409(ask409b, 'Only run SELECT or EXPLAIN statements. Refuse any write.').concat([
            res('Claude refuses the write it needs', 'Reproducing the reset needs one UPDATE. The rule forbids it.', [T('I can\'t modify data, so I can\'t reproduce the reset. My best guess is a timezone issue in the reset job.')], 'end_turn', 'bad'),
            S('cust', 'Engineer gets a guess', 'And nothing in this setup would stop the script after a write anyway.', 'My best guess is a timezone issue in the reset job.', 'bad')]),
          outcome: { ok: false, text: 'Here writes are allowed; the need is to stop after one changes rows. A refusal rule blocks the reproduction and is still only a prompt.' }, rate: 0.5 },
        { steps: [S('loop', 'Script settings ask the engineer before every run_sql', '', { permissions: { ask: [SQL] } }),
            S('cust', 'Engineer starts the investigation', '', ask409b),
            S('cust', 'Approval prompts 1 to 30: SELECTs, then the UPDATE', 'The engineer approves the UPDATE, and every read around it.', 'Allow run_sql? SELECT ...  y\n\u2026\nAllow run_sql? UPDATE users SET last_lesson_at = ... WHERE id = 8812  y', 'warn'),
            S('cust', 'Engineer reviews the change by hand', '', 'users.8812 updated (1 row)', 'ok')],
          outcome: { ok: true, warn: true, text: 'It works, but every read waits for a person. A hook on the result can stop the script after the one statement that matters.' }, rate: 0.95 },
        { steps: [S('hook', 'PreToolUse hook blocks every non-read', '', preHook)].concat(open409(ask409b)).concat([
            res('Claude tries to reproduce the reset', 'An allowed write in this world.', [T('I\'ll set the last lesson to 18:40 UTC and run the reset job.'), updCall], 'tool_use'),
            S('hook', 'Hook denies the UPDATE', 'The rule says "reads only", but this world allows writes.', { permissionDecision: 'deny', permissionDecisionReason: 'Read-only script: run_sql accepts SELECT only.' }, 'bad'),
            res('Claude cannot reproduce the bug', '', [T('Writes are blocked, so I can\'t reproduce this. Likely a timezone issue.')], 'end_turn'),
            S('cust', 'Engineer gets a guess', '', 'Likely a timezone issue.', 'bad')]),
          outcome: { ok: false, text: 'A pre-call block is for actions that must never happen. Here the write is allowed and the requirement is about what it changed, which only exists after the call.' }, rate: 0.4 },
        { steps: [S('hook', 'PostToolUse hook on run_sql', 'Reads the actual result of each call.', postHook)].concat(open409(ask409b)).concat([
            res('Claude reproduces the reset', '', [T('I\'ll set the last lesson to 18:40 UTC and run the reset job.'), updCall], 'tool_use'),
            S('tool', 'run_sql runs the UPDATE', 'Allowed in this world.', { input: updCall.input, output: { rows_affected: 1 } }),
            S('hook', 'Hook sees rows_affected = 1 and stops the script', 'It acts on the real outcome, not a guess from the statement text.', { continue: false, stopReason: 'run_sql changed 1 row(s). Engineer review needed.' }, 'ok'),
            S('cust', 'Engineer reviews the one changed row', '', 'Script stopped: run_sql changed 1 row(s).\nusers.8812: last_lesson_at = 2026-10-03T18:40:00Z', 'ok')]),
          outcome: { ok: true, text: 'When the rule is "stop once something has changed", the check belongs on the result. This is the world where the runner-up wins.' }, rate: 1 }
      ]
    }
  };

  /* ------------------------------------------------------------ m7-s4-10 model-driven loop vs fixed chain */
  var ask410 = 'Why doesn\'t a streak freeze protect a missed Sunday?';
  var hits = ['app/controllers/streaks_controller.rb', 'app/views/streaks/_freeze.html.erb', 'config/locales/en.yml'];
  var fixedCode = 'hits = grep(keywords(question))[:3]\nctx  = [read(h) for h in hits]\nanswer = claude(question, ctx)';
  var loopCode = 'while True:\n    resp = client.messages.create(tools=[GREP, READ], messages=messages)\n    if resp.stop_reason == "tool_use":\n        messages += [assistant(resp), user(run_tools(resp))]   # tool_results by id\n        continue\n    break   # "end_turn": Claude has enough';
  var answer410 = 'Freezes only cover Monday to Saturday. lib/calendar/week_boundary.rb:14 builds the week as monday..saturday, and StreakFreezePolicy#covers? uses that range, so Sunday is never covered.';
  function loopTrail(mark0, note0, mark3, note3) {
    return [S('cust', 'Engineer asks', '', ask410),
      req('Request with Grep and Read as tools', note0, { tool_choice: { type: 'auto' }, tools: ['Grep', 'Read'], messages: [{ role: 'user', content: ask410 }] }),
      res('Claude searches', '', [U('toolu_31', 'Grep', { pattern: 'freeze', path: 'app', output_mode: 'files_with_matches' })], 'tool_use'),
      S('loop', 'Loop runs the tool and continues on "tool_use"', note3, loopCode, mark3),
      res('Claude reads the controller, sees the call, follows it', 'Each next file comes from what the last read showed.', [T('The controller calls streak.apply_freeze!. Following it.'), U('toolu_33', 'Read', { file_path: 'app/models/streak.rb' })], 'tool_use', mark0),
      res('Two more hops: the policy, then the calendar helper it uses', '', [U('toolu_35', 'Read', { file_path: 'app/services/streak_freeze_policy.rb' }), U('toolu_36', 'Read', { file_path: 'lib/calendar/week_boundary.rb' })], 'tool_use'),
      S('tool', 'The bug is three calls deep', '', { file: 'lib/calendar/week_boundary.rb', line: 14, code: 'def week(d) = (d.beginning_of_week(:monday)..d.beginning_of_week(:monday) + 5)' }),
      res('Claude has enough and ends its turn', '', [T(answer410)], 'end_turn'),
      S('cust', 'Engineer sees', '', answer410, 'ok')];
  }
  var askB410 = 'What does POST /lessons/:id/complete return when the lesson is already done?';
  var answerB410 = 'It returns 200 with the existing completion. LessonCompletion#call checks Lesson#completed_by?(user) and skips the insert.';

  var s410 = {
    id: 'm7-s4-10', who: 'Engineer', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Which files matter next <b>depends on what each Read reveals</b>; here the logic is three calls past the top hits.' },
      { id: 'B', label: 'Decider changed', desc: 'Questions are about endpoints, and the answer <b>always sits within two calls of the route\'s controller</b>: the steps are known in advance.' }
    ],
    runs: {
      A: [
        { steps: loopTrail('ok', 'Option A: Claude, not the code, chooses each call. (The redesign pairs it with D\'s loop.)', '', ''),
          outcome: { ok: true, text: 'Claude picks each next file from what it just read, so it can follow the trail as far as it goes.' }, rate: 1 },
        { steps: [S('cust', 'Engineer asks', '', ask410),
            S('loop', 'Fixed chain: top 3 hits, then follow references two levels', 'Option B. The depth is decided before anything is read.', fixedCode + '\nctx += follow_refs(hits, depth=2)'),
            S('tool', 'Grep top 3 hits', '', hits),
            S('tool', 'Level 1 and 2 references: 14 files', 'Streak and StreakFreezePolicy are in; so are User, Lesson, ApplicationController\u2026 The calendar helper is level 3.', ['app/models/streak.rb', 'app/services/streak_freeze_policy.rb', 'app/models/user.rb', '\u2026 11 more'], 'warn'),
            res('Claude answers from what it was given', 'StreakFreezePolicy calls Calendar::WeekBoundary, but that file was never read.', [T('StreakFreezePolicy#covers? checks the date against Calendar::WeekBoundary. I can\'t see that code, so the Sunday rule is unclear.')], 'end_turn', 'bad'),
            S('cust', 'Engineer sees', '', 'I can\'t see that code, so the Sunday rule is unclear.', 'bad')],
          outcome: { ok: false, text: 'Any fixed depth is a guess. This trail needed three hops; the next one may need four. The next file depends on each read, so Claude has to choose.' }, rate: 0.55 },
        { steps: [S('cust', 'Engineer asks', '', ask410),
            S('loop', 'One fixed chain per keyword, in parallel subagents', 'Option C.', 'for kw in ["streak", "freeze", "Sunday"]:\n    spawn(fixed_chain, kw)   # grep \u2192 top 3 \u2192 read'),
            S('sub', 'Subagents return their top 3 reads', 'Wider, not deeper. "Sunday" mostly hits locale files.', { streak: ['streaks_controller.rb', 'streak.rb', 'streak_spec.rb'], freeze: ['streaks_controller.rb', '_freeze.html.erb', 'en.yml'], Sunday: ['en.yml', 'hi.yml', 'reminder_mailer.rb'] }, 'warn'),
            res('Claude answers from the merged reads', '', [T('Streak#apply_freeze! delegates to StreakFreezePolicy, which isn\'t in the context. The Sunday behaviour is not visible here.')], 'end_turn', 'bad'),
            S('cust', 'Engineer sees', '', 'The Sunday behaviour is not visible here.', 'bad')],
          outcome: { ok: false, text: 'Three copies of the same fixed steps search wider but still stop at the first reads. None of them can follow a call.' }, rate: 0.35 },
        { steps: loopTrail('', 'Claude gets the tools; the loop is what lets it keep going.', 'ok', 'Option D: append each tool_result and loop until stop_reason is "end_turn".'),
          outcome: { ok: true, text: 'The loop feeds every result back and stops only when Claude says it is done, so the number of hops is set by the question, not the code.' }, rate: 1 }
      ],
      B: [
        { steps: [S('cust', 'Engineer asks', '', askB410),
            req('Request with Grep and Read as tools', '', { tool_choice: { type: 'auto' }, tools: ['Grep', 'Read'], messages: [{ role: 'user', content: askB410 }] }),
            res('Claude explores: Grep, then reads', 'It takes a different path on each run, sometimes reading files it did not need.', [U('toolu_41', 'Grep', { pattern: 'complete', path: 'app' })], 'tool_use'),
            res('Six calls later, Claude answers', '', [T(answerB410)], 'end_turn', 'warn'),
            S('cust', 'Engineer sees', '', answerB410, 'ok')],
          outcome: { ok: true, warn: true, text: 'It works, but here the steps are always the same. A model-driven loop spends extra calls and gives a less predictable path for a trail you already know.' }, rate: 0.97 },
        { steps: [S('cust', 'Engineer asks', '', askB410),
            S('loop', 'Fixed chain: route\'s controller, then two levels of references', '', fixedCode + '\nctx += follow_refs(hits, depth=2)'),
            S('tool', 'Reads: controller \u2192 LessonCompletion \u2192 Lesson', 'The answer always lives within these two hops, and it does here.', ['app/controllers/lessons_controller.rb', 'app/services/lesson_completion.rb', 'app/models/lesson.rb'], 'ok'),
            res('Claude answers in one call', '', [T(answerB410)], 'end_turn'),
            S('cust', 'Engineer sees', '', answerB410, 'ok')],
          outcome: { ok: true, text: 'When the needed files are known steps, a fixed chain is predictable, auditable and cheap. This is the world where the runner-up wins.' }, rate: 1 },
        { steps: [S('cust', 'Engineer asks', '', askB410),
            S('sub', 'Per-keyword subagents return top 3 reads each', 'No hop past the hits.', { lessons: ['lessons_controller.rb', 'lesson.rb', 'lessons_spec.rb'], complete: ['lessons_controller.rb', 'complete.json.jbuilder', 'en.yml'] }, 'warn'),
            res('Claude answers', 'LessonCompletion was never read.', [T('The controller calls LessonCompletion.call; its duplicate handling is not visible here.')], 'end_turn', 'bad')],
          outcome: { ok: false, text: 'Parallel copies of top-3 reads still miss a file one call away.' }, rate: 0.5 },
        { steps: [S('cust', 'Engineer asks', '', askB410),
            S('loop', 'stop_reason loop with Grep and Read', '', loopCode),
            res('Claude explores for six calls, then ends its turn', '', [T(answerB410)], 'end_turn', 'warn'),
            S('cust', 'Engineer sees', '', answerB410, 'ok')],
          outcome: { ok: true, warn: true, text: 'Correct, with more calls than a fixed chain that already knows the two hops.' }, rate: 0.97 }
      ]
    }
  };

  /* ------------------------------------------------------------ m7-s5-09 retry with compiler errors */
  var fail509 = 'Build #4182 failed: :booking:compileKotlin\ne: src/main/kotlin/com/trip/booking/FareCalculator.kt:88:21 Type mismatch: inferred type is Int? but Int was expected';
  var errs509 = 'e: src/main/kotlin/com/trip/booking/FareCalculator.kt:88:30 Unresolved reference: nightCount\ne: src/main/kotlin/com/trip/booking/TaxRules.kt:41:17 Type mismatch: inferred type is Int? but Int was expected';
  var patch1 = '- val total = rate * booking.nights\n+ val total = rate * (booking.nightCount ?: 1)';
  function open509(failText, firstPatch, errText) {
    return [S('cust', 'CI job: build fails on main', '', failText),
      res('Claude proposes a patch', '', [U('toolu_51', 'Edit', { file_path: 'src/main/kotlin/com/trip/booking/FareCalculator.kt', diff: firstPatch })], 'tool_use'),
      S('tool', 'Gradle compiles the patch: fails', 'The compiler says exactly what broke, file, line and error.', errText, 'warn')];
  }
  var bareRetry = req('Job reruns Claude with a bare message', 'Nothing new to act on.', { messages: ['\u2026original request\u2026', { role: 'user', content: 'The patch failed. Try again.' }] });
  var sameFail = S('tool', 'Second attempt fails the same way', 'Claude repeats its reasoning: it still does not know which names and lines broke.', errs509, 'bad');

  var s509 = {
    id: 'm7-s5-09', who: 'CI job', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'The compiler names each broken file and line, and <b>every needed fix lies within the repository</b>.' },
      { id: 'B', label: 'Decider changed', desc: 'The error comes from a partner SDK that removed <code>loyaltyMultiplier</code>; the replacement rule is in the partner\'s docs, <b>not in the repository</b>.' }
    ],
    runs: {
      A: [
        { steps: open509(fail509, patch1, errs509).concat([
            req('Retry carries the compiler\'s error lines', 'Option A: same request, plus exactly what broke.', { messages: ['\u2026original request\u2026', { role: 'user', content: 'Your patch did not compile:\n' + errs509 + '\nFix these errors.' }] }, 'ok'),
            res('Claude fixes both named errors', 'Booking.kt shows the field is nights: Int?, and TaxRules.kt:41 has the same issue.', [U('toolu_52', 'Edit', { file_path: 'FareCalculator.kt + TaxRules.kt', diff: '- (booking.nightCount ?: 1)\n+ (booking.nights ?: 1)\n- TaxRules.kt:41  nights * cityTax\n+ TaxRules.kt:41  (nights ?: 1) * cityTax' })], 'tool_use'),
            S('tool', 'Gradle compiles and tests pass', '', 'BUILD SUCCESSFUL in 1m 52s  \u2022  autofix commit pushed to #4182', 'ok')]),
          outcome: { ok: true, text: 'The errors were specific and the fix was in the repo, so feeding them back gave the retry what it lacked. Most failures like this now clear on the retry.' }, rate: 0.92 },
        { steps: open509(fail509, patch1, errs509).concat([bareRetry, sameFail,
            S('loop', 'Job opens a draft PR for a developer', 'Option B. The hand-off works, but the job\'s own fix rate is unchanged.', { draft_pr: '#4190 autofix: build #4182', attached: ['patch.diff', 'build.log'], assignee: 'on-call' }, 'warn'),
            S('cust', 'A developer fixes it by hand', 'A two-line fix the job had every fact for.', 'on-call: "nights is Int? now. Two lines. Merged."', 'warn')]),
          outcome: { ok: false, text: 'Handing off is for fixes that need facts the job cannot reach. Here every fix was in the repo, and the retry had never been given the errors.' }, rate: 0.35 },
        { steps: open509(fail509, patch1, errs509).concat([
            S('sub', 'Review instance comments on the failed patch', 'An opinion, not the compiler\'s exact list.', 'Patch looks reasonable. Consider null safety around nights.', 'warn'),
            req('Retry carries the review comment', '', { messages: ['\u2026original request\u2026', { role: 'user', content: 'Reviewer: consider null safety around nights. Try again.' }] }),
            S('tool', 'Second attempt fails', 'The typo nightCount is still there, and TaxRules.kt was never mentioned.', 'e: FareCalculator.kt:88:30 Unresolved reference: nightCount\ne: TaxRules.kt:41:17 Type mismatch', 'bad')]),
          outcome: { ok: false, text: 'A reviewer adds a second guess when the compiler has already listed the exact errors. It is extra cost for weaker feedback.' }, rate: 0.6 },
        { steps: open509(fail509, patch1, errs509).concat([
            req('Retry attaches every file the patch touched', 'Only FareCalculator.kt was touched. TaxRules.kt, where an error is, is not included.', { messages: ['\u2026original request\u2026', { role: 'user', content: 'The patch failed. Current file:\n<FareCalculator.kt \u2026 212 lines>' }] }),
            res('Claude rewrites the line differently', 'More context, but nothing says what broke.', [U('toolu_53', 'Edit', { file_path: 'FareCalculator.kt', diff: '+ val total = rate * booking.nights!!' })], 'tool_use'),
            S('tool', 'Second attempt fails', '', 'e: TaxRules.kt:41:17 Type mismatch: inferred type is Int? but Int was expected', 'bad')]),
          outcome: { ok: false, text: 'The files give context but omit the one thing that says what broke: the compiler\'s messages.' }, rate: 0.5 }
      ],
      B: (function () {
        var failB = 'Build #4201 failed: :booking:compileKotlin\ne: src/main/kotlin/com/trip/booking/LoyaltyFare.kt:23:34 Unresolved reference: loyaltyMultiplier';
        var patchB = '- fare * partnerFare.loyaltyMultiplier\n+ fare * partnerFare.loyaltyRate';
        var errB = 'e: src/main/kotlin/com/trip/booking/LoyaltyFare.kt:23:34 Unresolved reference: loyaltyRate';
        var guess = S('tool', 'Retry "fixes" it with a guess', 'The real rule (tierBonus by points) is in the partner\'s docs. Nothing in the repo says so.', '+ val loyaltyMultiplier = 1.0   // compiles; every loyalty fare is now wrong', 'bad');
        return [
          { steps: open509(failB, patchB, errB).concat([
              req('Retry carries the compiler\'s error lines', 'Specific, but it points at a fact that is not in the repository.', { messages: ['\u2026', { role: 'user', content: 'Your patch did not compile:\n' + errB }] }), guess]),
            outcome: { ok: false, text: 'Feedback helps only when the fix can be found from it. Retries cannot create a missing fact; here they invent one.' }, rate: 0.15 },
          { steps: open509(failB, patchB, errB).concat([bareRetry,
              S('tool', 'Second attempt fails', '', errB, 'warn'),
              S('loop', 'Job opens a draft PR with the patch and build log', '', { draft_pr: '#4205 autofix: build #4201', attached: ['patch.diff', 'build.log'], assignee: 'payments on-call' }, 'ok'),
              S('cust', 'Developer applies the partner\'s rule', 'The person has the partner docs the job cannot reach.', '+ fare * partnerFare.tierBonus(member.points)   \u2022  BUILD SUCCESSFUL', 'ok')]),
            outcome: { ok: true, text: 'When the fix needs information outside the repository, a person is the right next step. This is the world where the runner-up wins.' }, rate: 1 },
          { steps: open509(failB, patchB, errB).concat([S('sub', 'Review instance comments', 'It cannot see the partner docs either.', 'Maybe loyaltyMultiplier was renamed. Try loyaltyFactor.', 'warn'),
              S('tool', 'Second attempt fails', '', 'e: LoyaltyFare.kt:23:34 Unresolved reference: loyaltyFactor', 'bad')]),
            outcome: { ok: false, text: 'A second model guessing does not supply the missing rule.' }, rate: 0.15 },
          { steps: open509(failB, patchB, errB).concat([req('Retry attaches LoyaltyFare.kt', '', { messages: ['\u2026', { role: 'user', content: 'The patch failed. Current file:\n<LoyaltyFare.kt>' }] }), guess]),
            outcome: { ok: false, text: 'The file shows the broken line, not the partner\'s new rule.' }, rate: 0.1 }
        ];
      })()
    }
  };

  /* ------------------------------------------------------------ m7-s6-03 retry with specific validation error */
  var validator = 'class Policy(BaseModel):\n    effective_date: date\n    expiry_date: date\n    @model_validator(mode="after")\n    def dates_in_order(self):\n        if self.expiry_date < self.effective_date:\n            raise ValueError("expiry_date is before effective_date")\n        return self';
  var swapped = { policy_number: 'HSP-4471902', carrier: 'Harbor Specialty Ins. Co.', effective_date: '2027-03-01', expiry_date: '2026-03-01' };
  var fixed603 = { policy_number: 'HSP-4471902', carrier: 'Harbor Specialty Ins. Co.', effective_date: '2026-03-01', expiry_date: '2027-03-01' };
  var specific = 'Validation failed: expiry_date (2026-03-01) is before effective_date (2027-03-01). Rule: expiry_date must be on or after effective_date. Re-read both dates on the document and check which label each belongs to.';
  function open603(docNote, docText, out) {
    return [S('cust', 'Pipeline receives COI-7730 (Harbor Specialty)', docNote, docText),
      res('Claude extracts through the schema tool', '', [U('toolu_61', 'record_certificate', out)], 'tool_use'),
      S('loop', 'Pydantic rejects the result', '', validator + '\n# \u2192 ValidationError: expiry_date ' + out.expiry_date + ' is before effective_date ' + out.effective_date, 'warn')];
  }
  var docA = 'Harbor Specialty Ins. Co.   Policy HSP-4471902\nPolicy Exp 03/01/2027     Policy Eff 03/01/2026';
  var docB = 'Harbor Specialty Ins. Co.   Policy HSP-4471902\nPolicy Exp 0?/3l/2O2?     Policy Eff 03/01/2026';
  var smudged = { policy_number: 'HSP-4471902', carrier: 'Harbor Specialty Ins. Co.', effective_date: '2026-03-01', expiry_date: '2026-01-31' };

  var s603 = {
    id: 'm7-s6-03', who: 'Pipeline', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Both dates are <b>printed clearly</b>; the model put each date in the other\'s field.' },
      { id: 'B', label: 'Decider changed', desc: 'In the failures the expiry date is <b>smudged in the OCR scan</b> and cannot be read from the document.' }
    ],
    runs: {
      A: [
        { steps: open603('Text PDF. Harbor prints Exp to the left of Eff.', docA, swapped).concat([
            S('loop', 'Post-processing swaps the dates', 'Option A. This document comes out right\u2026', 'if p.expiry_date < p.effective_date:\n    p.effective_date, p.expiry_date = p.expiry_date, p.effective_date'),
            S('cust', 'Next: COI-7744 (Kestrel Casualty) with a real misprint', 'The carrier printed Exp 06/30/2025 by mistake; it should be 2027.', 'Policy Eff 07/01/2026     Policy Exp 06/30/2025'),
            S('tool', 'The swap posts the misprint as fact', 'Nobody sees that the certificate itself was wrong.', { certificate: 'COI-7744', effective_date: '2025-06-30', expiry_date: '2026-07-01', status: 'posted' }, 'bad')]),
          outcome: { ok: false, text: 'The swap hard-codes a guess about the cause. It fixes mapping slips and also flips genuine misprints, posting them as correct.' }, rate: 0.9 },
        { steps: open603('Text PDF. Harbor prints Exp to the left of Eff.', docA, swapped).concat([
            S('loop', 'Route straight to the review queue', 'Option B.', { queue: 'exceptions', item: 'COI-7730', reason: 'date check failed' }, 'warn'),
            S('cust', 'An account assistant re-keys the two dates', 'Both dates were readable all along.', 'Assistant: swapped Eff/Exp, approved. (31 items like this today)', 'warn')]),
          outcome: { ok: true, warn: true, text: 'The certificate is fixed, by a person, for a mapping mistake a specific retry could have fixed. Hand-off fits missing or unreadable data, not this.' }, rate: 1 },
        { steps: open603('Text PDF. Harbor prints Exp to the left of Eff.', docA, swapped).concat([
            req('Resend with the check\'s details', 'Option C: the fields, the values returned and the rule they broke.', { messages: ['\u2026document\u2026', { role: 'assistant', content: '[tool_use toolu_61 record_certificate]' }, { role: 'user', content: [E('toolu_61', specific)] }] }, 'ok'),
            res('Claude re-reads the labels and corrects the mapping', '', [T('Harbor prints Exp before Eff; I had them reversed.'), U('toolu_62', 'record_certificate', fixed603)], 'tool_use'),
            S('loop', 'Pydantic passes; result posts', '', { certificate: 'COI-7730', effective_date: '2026-03-01', expiry_date: '2027-03-01', status: 'posted' }, 'ok')]),
          outcome: { ok: true, text: 'The dates are on the page and the error is a mapping slip. Telling the retry exactly what broke lets it fix it.' }, rate: 0.95 },
        { steps: [S('loop', 'Prompt gains worked certificates for four carriers', 'Option D: Northwind, Atlas, Kestrel, Pioneer. About sixty carriers send documents.', 'Example (Northwind): "Eff 01/01/2026 | Exp 01/01/2027" \u2192 effective_date, expiry_date\n\u2026 3 more')].concat(open603('Harbor is not among the examples.', docA, swapped)).concat([
            req('Generic retry, as before', '', { messages: ['\u2026', { role: 'user', content: [E('toolu_61', 'Validation failed, please retry.')] }] }),
            res('Same swap again', 'Nothing tells Claude what to fix.', [U('toolu_62', 'record_certificate', swapped)], 'tool_use', 'bad')]),
          outcome: { ok: false, text: 'A few examples cover a few layouts out of sixty. The exact error for this document is already known and goes unused.' }, rate: 0.6 }
      ],
      B: [
        { steps: open603('OCR\'d scan. The expiry date is smudged.', docB, smudged).concat([
            S('loop', 'Post-processing swaps the dates', '', 'swap(effective_date, expiry_date)'),
            S('tool', 'A misread date posts as the effective date', '', { certificate: 'COI-7730', effective_date: '2026-01-31', expiry_date: '2026-03-01', status: 'posted' }, 'bad')]),
          outcome: { ok: false, text: 'The model guessed an unreadable date. Swapping it turns a guess into a posted fact.' }, rate: 0.2 },
        { steps: open603('OCR\'d scan. The expiry date is smudged.', docB, smudged).concat([
            S('loop', 'Route to the review queue', '', { queue: 'exceptions', item: 'COI-7730', reason: 'date check failed; expiry illegible' }, 'ok'),
            S('cust', 'Account assistant checks the original with the carrier', '', 'Carrier confirms Exp 03/01/2027. Approved.', 'ok')]),
          outcome: { ok: true, text: 'The date is not readable in the source, so no retry can recover it. A person is the right step. This is the world where the runner-up wins.' }, rate: 1 },
        { steps: open603('OCR\'d scan. The expiry date is smudged.', docB, smudged).concat([
            req('Resend with the check\'s details', 'Specific, but the answer is not on the page.', { messages: ['\u2026', { role: 'user', content: [E('toolu_61', 'Validation failed: expiry_date (2026-01-31) is before effective_date (2026-03-01). Re-read both dates.')] }] }),
            res('Claude picks a new guess that passes the check', '', [U('toolu_62', 'record_certificate', { effective_date: '2026-03-01', expiry_date: '2027-03-31' })], 'tool_use', 'warn'),
            S('tool', 'A guessed date posts as fact', 'It passed Pydantic, but it was never read from the document.', { certificate: 'COI-7730', expiry_date: '2027-03-31', status: 'posted' }, 'bad')]),
          outcome: { ok: false, text: 'Feedback can fix a mapping slip, not an unreadable date. Here the retry just finds a guess that satisfies the rule.' }, rate: 0.3 },
        { steps: open603('OCR\'d scan. The expiry date is smudged.', docB, smudged).concat([
            res('Examples do not make the smudge readable', '', [U('toolu_62', 'record_certificate', smudged)], 'tool_use', 'bad')]),
          outcome: { ok: false, text: 'Layout examples cannot recover characters the scan lost.' }, rate: 0.3 }
      ]
    }
  };

  /* ------------------------------------------------------------ m7-s6-06 stop_reason loop */
  var LT = ['lookup_carrier', 'lookup_coverage_code'];
  var extraction = '{"insured":"Linden Bakery LLC","carrier":"Harbor Specialty Ins. Co.","naic":"10847","policy_number":"HSP-4471902","coverage":[{"line":"GL","limit":1000000,"deductible":2500}],"effective_date":"2026-03-01","expiry_date":"2027-03-01"}';
  var srLoop = 'while True:\n    resp = client.messages.create(tools=TOOLS, messages=messages)\n    if resp.stop_reason == "tool_use":\n        messages += [assistant(resp), user(run_tools(resp))]\n        continue\n    break   # "end_turn"';
  var mixed = [T('All policy fields found. EXTRACTION COMPLETE once the carrier code is in.'), U('toolu_71', 'lookup_carrier', { name: 'Harbor Specialty Ins. Co.' })];
  var carrierOut = S('tool', 'lookup_carrier runs', '', { input: { name: 'Harbor Specialty Ins. Co.' }, output: { naic: '10847', status: 'active' } });
  var startDoc = S('cust', 'Pipeline sends COI-7730 for extraction', '', 'Extract COI-7730 (Harbor Specialty, text PDF).');
  var noPhrase = res('Second document: Claude finishes without the phrase', 'COI-7731. The extraction is done; the wording just differs.', [T('Done. ' + extraction)], 'end_turn');
  var capHit = S('loop', 'Loop keeps going until the iteration cap', '', 'iteration 10/10 \u2192 abort: "max iterations reached"', 'bad');
  var statusSys = 'End every reply with a JSON line: {"status": "in_progress" | "complete"}.';
  var statusLoop = 'tools_pending = any(b.type == "tool_use" for b in resp.content)\nif status(resp) == "complete" and not tools_pending:\n    break\nmessages += [assistant(resp), user(run_tools(resp) or "Continue.")]';

  var s606 = {
    id: 'm7-s6-06', who: 'Pipeline', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'The loop reads Claude\'s text for "EXTRACTION COMPLETE", while <b>the API already reports stop_reason</b> on every response.' },
      { id: 'B', label: 'Decider changed', desc: 'The broker\'s model gateway <b>strips stop_reason</b> and returns only content blocks: there is no API stop signal.' }
    ],
    runs: {
      A: [
        { steps: [startDoc, req('Request with a status-field instruction', 'Option A.', { system: statusSys, tools: LT, messages: [{ role: 'user', content: 'Extract COI-7730.' }] }),
            res('Claude writes "complete" and requests a tool', 'The pending-tool check catches this case.', [T('{"status": "complete"}'), mixed[1]], 'tool_use'),
            S('loop', 'Tool pending \u2192 run it and continue', '', statusLoop, 'ok'), carrierOut,
            res('Claude ends its turn, but writes "in_progress"', 'It meant to flag the GL limit for a check, then ended the turn anyway. stop_reason says "end_turn".', [T(extraction + '\n{"status": "in_progress"}')], 'end_turn', 'warn'),
            S('loop', 'Status is not "complete" \u2192 send "Continue."', 'The loop trusts the field over the API\'s signal.', 'status == "in_progress" \u2192 messages += user("Continue.")'), capHit],
          outcome: { ok: false, text: 'A structured field beats a phrase, but it is still Claude\'s content acting as the stop signal. The API already said the turn ended.' }, rate: 0.93 },
        { steps: [startDoc, req('Request', 'Option B: the phrase stays, tools run first.', { tools: LT, messages: [{ role: 'user', content: 'Extract COI-7730.' }] }),
            res('Claude writes the phrase and requests a tool', '', mixed, 'tool_use'),
            S('loop', 'Run tools, stop on the turn after', 'This patches the first failure\u2026', 'if tool_uses: run_tools(); continue\nif "EXTRACTION COMPLETE" in text: break', 'ok'),
            carrierOut, noPhrase,
            S('loop', 'No phrase \u2192 loop asks again', '\u2026but text is still the stop signal.', '"EXTRACTION COMPLETE" not in text \u2192 continue', 'warn'), capHit],
          outcome: { ok: false, text: 'It fixes the pending-tool case and keeps the fragile part. Runs that never write the phrase still end at the cap.' }, rate: 0.8 },
        { steps: [startDoc, S('hook', 'PostToolUse hook: stop when every schema field has a value', 'Option C.', 'def all_filled(input_data, tool_use_id, context):\n    if all(state.fields.values()):\n        return {"continue": False, "stopReason": "all fields filled"}\n    return {}'),
            res('Claude requests the carrier code', '', mixed, 'tool_use'), carrierOut,
            S('hook', 'Every field now has a value \u2192 loop ends', 'Claude had more to do: the GL limit read as "1,000,00" and it planned to check it.', { continue: false, stopReason: 'all fields filled', pending_intent: 'lookup_coverage_code("GL") to confirm limit' }, 'bad'),
            S('tool', 'Result posts with the unchecked limit', '', { certificate: 'COI-7730', gl_limit: 100000, status: 'posted' }, 'bad')],
          outcome: { ok: false, text: 'Code-driven, but on a pre-set condition. Filled is not finished: Claude may still be checking or correcting a value.' }, rate: 0.85 },
        { steps: [startDoc, req('Request', '', { tools: LT, messages: [{ role: 'user', content: 'Extract COI-7730.' }] }),
            res('Claude writes the phrase and requests a tool', 'The text says complete; stop_reason says otherwise.', mixed, 'tool_use'),
            S('loop', 'stop_reason = "tool_use" \u2192 run the tool and continue', 'Option D. The words in the text no longer matter.', srLoop, 'ok'), carrierOut,
            res('Claude ends its turn', '', [T('EXTRACTION COMPLETE\n' + extraction)], 'end_turn'),
            noPhrase,
            S('loop', 'stop_reason = "end_turn" \u2192 stop, for both documents', 'With or without the phrase, the loop ends when Claude is done.', 'COI-7730: end_turn \u2192 done\nCOI-7731: end_turn \u2192 done', 'ok')],
          outcome: { ok: true, text: 'stop_reason is the API\'s own signal for why each turn ended. Both failures disappear: no early exit, no cap.' }, rate: 1 }
      ],
      B: [
        { steps: [startDoc, req('Request with a status-field instruction', '', { system: statusSys, tools: LT, messages: [{ role: 'user', content: 'Extract COI-7730.' }] }),
            S('api', 'Claude writes "complete" and requests a tool', 'No stop_reason in this gateway\'s response.', { role: 'assistant', content: [T('{"status": "complete"}'), mixed[1]] }),
            S('loop', 'Tool pending \u2192 run it and continue', '', statusLoop, 'ok'), carrierOut,
            S('api', 'Claude replies with the extraction and "complete"', '', { content: [T(extraction + '\n{"status": "complete"}')] }),
            S('loop', 'Status "complete", nothing pending \u2192 stop', 'With no API signal, a structured field is the most reliable thing left.', 'break', 'ok')],
          outcome: { ok: true, text: 'Without an API stop signal, a structured status that also checks for pending tools is the best available. This is the world where the runner-up wins.' }, rate: 0.93 },
        { steps: [startDoc, S('api', 'Claude writes the phrase and requests a tool', '', { content: mixed }), carrierOut,
            S('api', 'Second document: no phrase', '', { content: [T('Done. ' + extraction)] }), capHit],
          outcome: { ok: false, text: 'Runs without the phrase still hit the cap.' }, rate: 0.8 },
        { steps: [startDoc, carrierOut, S('hook', 'All fields filled \u2192 loop ends', 'Claude was about to confirm the GL limit.', { continue: false, stopReason: 'all fields filled' }, 'bad')],
          outcome: { ok: false, text: 'Filled is still not finished.' }, rate: 0.85 },
        { steps: [startDoc, S('loop', 'You switch the loop to stop_reason', '', srLoop),
            S('block', 'Blocked: the gateway response has no stop_reason', 'The field the loop needs does not exist here.', { content: [T('\u2026')], stop_reason: '(not returned by gateway)' }, 'bad')],
          outcome: { ok: false, text: 'The right signal, when the API gives it. This gateway does not.' }, rate: 0 }
      ]
    }
  };

  /* ------------------------------------------------------------ m7-s6-08 programmatic gate vs forced first tool */
  var VT = ['verify_carrier', 'post_certificate'];
  var gate = 'verified = {}   # carrier -> verification_id, set only when verify_carrier returns "licensed"\n\ndef gate_post(input_data, tool_use_id, context):\n    carrier = input_data["tool_input"]["carrier"]\n    if carrier not in verified:\n        return {"hookSpecificOutput": {\n            "hookEventName": "PreToolUse",\n            "permissionDecision": "deny",\n            "permissionDecisionReason": f"{carrier} has no passed verify_carrier in this session. Verify first."}}\n    return {}';
  var sub3 = 'Submission SUB-318: 3 certificates\nCOI-6101 Northwind Mutual \u2022 COI-6102 Harbor Specialty \u2022 COI-6103 Kestrel Casualty';
  var firstDone = S('tool', 'Certificate 1: verify_carrier(Northwind) \u2192 licensed, then posted', '', { verify: { carrier: 'Northwind Mutual', status: 'licensed', verification_id: 'VER-7781' }, post: { certificate: 'COI-6101', status: 'posted' } });
  var skipPost = U('toolu_83', 'post_certificate', { certificate_id: 'COI-6102', carrier: 'Harbor Specialty' });
  var harborPosted = S('tool', 'post_certificate runs: COI-6102 posted', 'Harbor Specialty was never checked against the registry.', { certificate: 'COI-6102', carrier: 'Harbor Specialty', status: 'posted', verified: false }, 'bad');
  var sub1 = 'Submission SUB-322: 1 certificate\nCOI-6201 Harbor Specialty';

  var s608 = {
    id: 'm7-s6-08', who: 'Pipeline', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'One session handles <b>several certificates in turn</b>, and no unverified carrier\'s certificate may ever post.' },
      { id: 'B', label: 'Decider changed', desc: 'Each session handles <b>exactly one certificate</b>; the same compliance rule applies.' }
    ],
    runs: {
      A: [
        { steps: [S('cust', 'Pipeline starts a session', 'post_certificate now requires verification_id.', sub3), firstDone,
            res('Certificate 2: Claude posts with a verification ID', 'It reuses Northwind\'s ID. The schema only checks that the field is filled.', [U('toolu_83', 'post_certificate', { certificate_id: 'COI-6102', carrier: 'Harbor Specialty', verification_id: 'VER-7781' })], 'tool_use', 'warn'),
            harborPosted],
          outcome: { ok: false, text: 'A required field shapes the call; it checks nothing. Claude can fill it without a passed verification for that carrier.' }, rate: 0.85 },
        { steps: [S('cust', 'Pipeline starts a session', '', sub3),
            req('First request forces verify_carrier', 'Option B.', { tool_choice: { type: 'tool', name: 'verify_carrier' }, tools: VT, messages: [{ role: 'user', content: sub3 }] }, 'ok'),
            res('Claude verifies the first carrier', '', [U('toolu_81', 'verify_carrier', { carrier: 'Northwind Mutual' })], 'tool_use'),
            firstDone,
            req('Later requests are back on "auto"', 'Certificates 2 and 3 get no forced check.', { tool_choice: { type: 'auto' }, tools: VT, messages: ['\u2026'] }),
            res('Certificate 2: Claude posts straight away', '', [skipPost], 'tool_use', 'warn'),
            harborPosted],
          outcome: { ok: false, text: 'Forcing a tool covers the one request it is set on. This session has three certificates, and only the first was forced.' }, rate: 0.8 },
        { steps: [S('hook', 'PreToolUse gate on post_certificate', 'Option C. Runs before every post, for every certificate.', gate),
            S('cust', 'Pipeline starts a session', '', sub3), firstDone,
            res('Certificate 2: Claude tries to post without verifying', '', [skipPost], 'tool_use'),
            S('hook', 'Gate denies the post', 'Harbor Specialty is not in the verified set.', { permissionDecision: 'deny', permissionDecisionReason: 'Harbor Specialty has no passed verify_carrier in this session. Verify first.' }, 'ok'),
            res('Claude verifies, then posts', 'The denial reason tells it what to do next.', [U('toolu_84', 'verify_carrier', { carrier: 'Harbor Specialty' })], 'tool_use'),
            S('tool', 'Harbor licensed (VER-7790); COI-6102 posted', '', { verification_id: 'VER-7790', certificate: 'COI-6102', status: 'posted' }),
            S('hook', 'Certificate 3: Kestrel fails verification; its post is denied', 'A failed check never enters the verified set.', { verify: { carrier: 'Kestrel Casualty', status: 'license_lapsed' }, post_COI_6103: 'deny', routed_to: 'account assistants' }, 'ok'),
            S('tool', 'Posted: COI-6101, COI-6102. Held: COI-6103', '', { posted: ['COI-6101', 'COI-6102'], held: ['COI-6103'] }, 'ok')],
          outcome: { ok: true, text: 'The gate checks every post against what actually passed, whatever the model decides. That is what "never" needs.' }, rate: 1 },
        { steps: [S('cust', 'Pipeline starts a session', '', sub3), firstDone,
            req('Every request: tool_choice "any"', 'Option D.', { tool_choice: { type: 'any' }, tools: VT, messages: ['\u2026'] }),
            res('Claude calls a tool: post_certificate', '"any" requires some tool, not the right one.', [skipPost], 'tool_use', 'warn'),
            harborPosted],
          outcome: { ok: false, text: '"any" forces a tool call, not the order. The order still rests on a description.' }, rate: 0.8 }
      ],
      B: [
        { steps: [S('cust', 'Pipeline starts a session', '', sub1),
            res('Claude posts with an invented ID', '', [U('toolu_91', 'post_certificate', { certificate_id: 'COI-6201', carrier: 'Harbor Specialty', verification_id: 'VER-0000' })], 'tool_use', 'warn'),
            S('tool', 'COI-6201 posted, unverified', '', { status: 'posted', verified: false }, 'bad')],
          outcome: { ok: false, text: 'A filled field is not a passed check.' }, rate: 0.85 },
        { steps: [S('cust', 'Pipeline starts a session', '', sub1),
            req('First request forces verify_carrier', '', { tool_choice: { type: 'tool', name: 'verify_carrier' }, tools: VT, messages: [{ role: 'user', content: sub1 }] }),
            res('Claude must verify first', '', [U('toolu_91', 'verify_carrier', { carrier: 'Harbor Specialty' })], 'tool_use', 'ok'),
            S('tool', 'Harbor licensed (VER-7790)', '', { status: 'licensed', verification_id: 'VER-7790' }),
            res('Claude posts the only certificate', '', [U('toolu_92', 'post_certificate', { certificate_id: 'COI-6201', carrier: 'Harbor Specialty' })], 'tool_use'),
            S('tool', 'COI-6201 posted after verification', 'The one forced request covers the whole session.', { status: 'posted', verified: true }, 'ok')],
          outcome: { ok: true, text: 'With one certificate per session, forcing verify_carrier on the first request covers every post there is. This is the world where the runner-up wins.' }, rate: 1 },
        { steps: [S('hook', 'PreToolUse gate on post_certificate', '', gate), S('cust', 'Pipeline starts a session', '', sub1),
            S('tool', 'Verify, then post: gate allows it', '', { verify: 'licensed', post: 'allowed' }, 'ok')],
          outcome: { ok: true, warn: true, text: 'Still correct, but extra code and session state for what one forced first call already guarantees here.' }, rate: 1 },
        { steps: [S('cust', 'Pipeline starts a session', '', sub1),
            req('tool_choice "any"', '', { tool_choice: { type: 'any' }, tools: VT, messages: [{ role: 'user', content: sub1 }] }),
            res('Claude calls post_certificate first', '', [U('toolu_91', 'post_certificate', { certificate_id: 'COI-6201', carrier: 'Harbor Specialty' })], 'tool_use', 'bad')],
          outcome: { ok: false, text: '"any" can pick the post. Naming verify_carrier is what forces the check.' }, rate: 0.8 }
      ]
    }
  };

  [s409, s410, s509, s603, s606, s608].forEach(L.add);
})();
