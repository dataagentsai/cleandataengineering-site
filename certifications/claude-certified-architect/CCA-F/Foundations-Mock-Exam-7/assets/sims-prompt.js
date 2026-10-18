/* CCA-F Mock Exam #7 - scripted simulations for the prompt-engineering and structured-output questions:
   m7-s2-07, m7-s2-08, m7-s5-06, m7-s5-07, m7-s6-01, m7-s6-02, m7-s6-04.
   These are judgement questions, so the traces show the prompt or schema after each option is applied, then
   Claude's outputs on a few representative inputs. Rates are model compliance (share of 20 runs that meet the
   requirement). Uses the helper library in sims.js (window.SIMLIB). Plain ES5, ASCII only. */
(function () {
  var L = window.SIMLIB, S = L.S, req = L.req, res = L.res, T = L.T, U = L.U, X = L.X;
  function tbl(step, head, rows) { return X(step, { table: { head: head, rows: rows } }); }

  /* ============================================================ m7-s2-07 few-shot vs path rule (error format) */
  var prose207 = 'Errors: answer with the right HTTP status and a JSON body holding an "error" object.\n' +
    'The object has a machine "code" in SCREAMING_SNAKE_CASE, a human "message", and "details"\n' +
    'when a specific field is at fault.';
  var cmd207 = '.claude/commands/new-endpoint.md\n---\ndescription: Generate an Express + Prisma endpoint from a ticket\n---\nCreate the endpoint described in $ARGUMENTS under server/src/routes/.\n';
  var good207 = '// POST /appointments\nif (!parsed.success)\n  return res.status(400).json({ error: { code: \'VALIDATION_FAILED\', message: \'Invalid request.\', details: parsed.error.flatten() } });\nif (!patient)\n  return res.status(404).json({ error: { code: \'PATIENT_NOT_FOUND\', message: \'No patient with that id.\' } });\nif (clinic.closedOn(date))\n  return res.status(422).json({ error: { code: \'CLINIC_CLOSED\', message: \'The clinic is closed that day.\' } });\nif (slotTaken)\n  return res.status(409).json({ error: { code: \'SLOT_TAKEN\', message: \'That slot is already booked.\' } });';
  var drift207 = '// POST /appointments  (run 7 of 20)\nif (!parsed.success)\n  return res.status(400).json({ message: \'Invalid patientId\', field: \'patientId\' });     // no error object\nif (!patient)\n  return res.status(404).json({ error: { code: \'PATIENT_NOT_FOUND\', message: \'No patient.\' } });\nif (clinic.closedOn(date))\n  return res.status(400).json({ error: \'Clinic closed\' });                                // string, wrong status\nif (slotTaken)\n  return res.status(409).json({ error: { code: \'slotTaken\', msg: \'Slot taken\' } });   // wrong case, wrong key';
  var simple207 = '// GET /clinics/:id\nif (!clinic)\n  return res.status(404).json({ error: { code: \'CLINIC_NOT_FOUND\', message: \'No clinic with that id.\' } });';
  var head207 = ['Endpoint', 'Failure cases', 'Runs with the team shape'];
  var quote207 = S('cust', 'Engineer asks: "What is our error format?"', 'Claude quotes the rule word for word. The rule is in context.', '> ' + prose207.replace(/\n/g, '\n> '));
  var ticket207 = S('cust', 'Engineer runs the command on three tickets', 'One simple endpoint and two with several failure cases.', '/new-endpoint GET /clinics/:id\n/new-endpoint POST /appointments\n/new-endpoint PATCH /appointments/:id/reschedule');
  var followup207 = 'Add a 409 when the new slot overlaps the patient\'s other booking.';
  var drift207b = '// PATCH /appointments/:id/reschedule  (follow-up edit, no command)\nif (overlaps)\n  return res.status(409).json({ success: false, reason: \'Overlapping booking\' });   // invented shape';

  var s207 = {
    id: 'm7-s2-07', who: 'Engineer', labels: { loop: 'Claude Code' }, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Claude <b>can quote the error rules</b>: they load with the command. Output still varies on endpoints with several failure cases.' },
      { id: 'B', label: 'Decider changed', desc: 'Most handler work is follow-up edits made <b>without the command</b>. On those edits the rules are <b>not loaded</b>, and Claude cannot quote them.' }
    ],
    runs: {
      A: [
        { steps: [S('file', 'Option A: the prose becomes a numbered checklist', 'Sharper wording, still instructions only.', cmd207 + '\nError responses:\n1. Validation failure -> 400, code VALIDATION_FAILED, details = field errors.\n2. Missing record -> 404, code <THING>_NOT_FOUND.\n3. Business rule broken -> 422, code names the rule.\n4. Conflict -> 409, code names the conflict.\nShape for all: { "error": { "code": ..., "message": ..., "details"?: ... } }'),
            quote207, ticket207,
            S('loop', 'Simple endpoint: one failure case, right shape', '', simple207, 'ok'),
            tbl(S('loop', 'POST /appointments: four failure cases, the shape drifts', 'Claude knows the checklist. Juggling four cases at once, it still writes them differently from run to run.', drift207, 'bad'),
              head207, [['GET /clinics/:id', '1', '20/20'], ['POST /appointments', '4', '14/20'], ['PATCH .../reschedule', '5', '12/20']])],
          outcome: { ok: false, text: 'The rules were already loaded and understood. A tidier checklist is still prose, and prose is exactly what varies on the hard cases.' }, rate: 0.65 },
        { steps: [S('file', 'Option B: three real handlers added to the command', 'Each example is a complete handler from the repo, chosen to cover many failure cases.', cmd207 + '\n' + prose207 + '\n\nExamples of finished handlers (copy their error style exactly):\n<example file="server/src/routes/patients.ts"> ...validation 400, 404, 409 duplicate email... </example>\n<example file="server/src/routes/clinics.ts"> ...404, 422 outside opening hours... </example>\n<example file="server/src/routes/billing.ts"> ...400 with details, 402, 409, 422... </example>', 'ok'),
            quote207, ticket207,
            S('loop', 'Simple endpoint: right shape', '', simple207, 'ok'),
            tbl(S('loop', 'POST /appointments: four failure cases, every one in the team shape', 'Claude copies a shape it has seen across many failures, rather than rebuilding it from a description.', good207, 'ok'),
              head207, [['GET /clinics/:id', '1', '20/20'], ['POST /appointments', '4', '19/20'], ['PATCH .../reschedule', '5', '19/20']])],
          outcome: { ok: true, text: 'Rules loaded but applied unevenly is the sign for examples. Complete handlers that cover the hard cases show the exact shape, so the output stops varying.' }, rate: 0.95 },
        { steps: [S('file', 'Option C: the rules move to a path-scoped rule file', 'It loads whenever Claude touches a route handler.', '.claude/rules/error-format.md\n---\npaths:\n  - "server/src/routes/**/*.ts"\n---\n' + prose207),
            X(S('ctx', 'What is in context during /new-endpoint', 'The same rule text, now loaded twice. It was never missing.', 'command body: error rules (prose)\n.claude/rules/error-format.md: error rules (prose, same text)', 'warn'),
              { meter: { total: 200000, parts: [{ label: 'system + CLAUDE.md', tokens: 9000, kind: 'sys' }, { label: 'rules via command', tokens: 400, kind: 'keep' }, { label: 'same rules via paths: rule', tokens: 400, kind: 'drop' }, { label: 'ticket + code read', tokens: 18000, kind: 'tool' }] } }),
            ticket207,
            tbl(S('loop', 'POST /appointments: the shape still drifts', 'Loading the rules a second way does not change how Claude applies them.', drift207, 'bad'),
              head207, [['GET /clinics/:id', '1', '20/20'], ['POST /appointments', '4', '11/20'], ['PATCH .../reschedule', '5', '9/20']])],
          outcome: { ok: false, text: 'A path rule fixes rules that do not load. Claude could already quote these, so loading was never the problem.' }, rate: 0.55 },
        { steps: [S('file', 'Option D: a fresh session reviews each endpoint before merge', '', 'claude -p "Review this diff against the error rules in .claude/commands/new-endpoint.md. List every response that breaks them."'),
            ticket207,
            S('loop', 'Generation is unchanged: POST /appointments drifts', '', drift207, 'bad'),
            S('sub', 'Reviewer session flags three responses', 'It catches the mistakes after they are written.', '- line 3: body has no "error" object\n- line 7: error is a string, status should be 422\n- line 9: code "slotTaken" is not SCREAMING_SNAKE_CASE', 'warn'),
            S('cust', 'Engineer fixes them by hand, on every complex endpoint', 'Consistency comes from rework, not from generation.', '3 fixes on POST /appointments, 4 on PATCH .../reschedule', 'warn')],
          outcome: { ok: false, text: 'An independent review catches errors afterwards. The question asks for the change that makes generation itself consistent.' }, rate: 0.75 }
      ],
      B: [
        { steps: [S('file', 'Checklist added to the command', '', cmd207 + '\nError responses:\n1. Validation failure -> 400 ...\n4. Conflict -> 409 ...'),
            S('cust', 'Engineer asks for a follow-up edit, no command', '', followup207),
            S('ctx', 'Context for this edit', 'The command is not invoked, so the checklist never loads.', 'root CLAUDE.md, server/src/routes/appointments.ts\n(error rules: not loaded)', 'warn'),
            S('loop', 'Claude invents a shape', '', drift207b, 'bad')],
          outcome: { ok: false, text: 'A better-written rule that does not load for this edit cannot be followed.' }, rate: 0.4 },
        { steps: [S('file', 'Three example handlers added to the command', '', cmd207 + '\n<example file="server/src/routes/patients.ts"> ... </example> (x3)'),
            S('cust', 'Engineer asks for a follow-up edit, no command', '', followup207),
            S('ctx', 'Context for this edit', 'The examples live in the command too, so they are not loaded either.', '(error rules and examples: not loaded)', 'warn'),
            S('loop', 'Claude invents a shape', 'Unless Claude happens to open a sibling handler and copy it.', drift207b, 'bad')],
          outcome: { ok: false, text: 'Examples help Claude apply rules it has. On these edits it has neither the rules nor the examples.' }, rate: 0.5 },
        { steps: [S('file', '.claude/rules/error-format.md with a paths: glob', 'Loads whenever Claude reads or edits a matching file, with or without the command.', '.claude/rules/error-format.md\n---\npaths:\n  - "server/src/routes/**/*.ts"\n---\n' + prose207),
            S('cust', 'Engineer asks for a follow-up edit, no command', '', followup207),
            S('ctx', 'Claude opens appointments.ts and the rule loads', 'The glob matches, so the rules arrive exactly when needed.', 'root CLAUDE.md\nserver/src/routes/appointments.ts\n.claude/rules/error-format.md   <- loaded by paths:', 'ok'),
            S('loop', 'Claude adds the case in the team shape', 'Follow-ups add one case at a time, which the prose handles well once it is present.', 'if (overlaps)\n  return res.status(409).json({ error: { code: \'BOOKING_OVERLAP\', message: \'The patient already has a booking at that time.\' } });', 'ok')],
          outcome: { ok: true, text: 'Here the rules were not loading for handler files, so scoping them to those files is the fix. This is the world where the runner-up wins.' }, rate: 0.93 },
        { steps: [S('cust', 'Engineer asks for a follow-up edit, no command', '', followup207),
            S('loop', 'Claude invents a shape', '', drift207b, 'bad'),
            S('sub', 'Reviewer session flags it before merge', '', '- line 2: body has no "error" object', 'warn')],
          outcome: { ok: false, text: 'Review catches the miss after the fact. The rules still do not reach Claude while it writes.' }, rate: 0.7 }
      ]
    }
  };

  /* ============================================================ m7-s2-08 explicit criteria vs labelled examples */
  var cmd208 = '.claude/commands/check-migration.md\n---\ndescription: Review the newest Prisma migration\n---\nRead the newest folder under server/prisma/migrations/ and ';
  var migs208 = '20261001_add_appointment_notes   ALTER TABLE "Appointment" ADD COLUMN "notes" TEXT;\n' +
    '20261002_index_slot_start       CREATE INDEX "Slot_start_idx" ON "Slot"("start");\n' +
    '20261003_drop_patient_fax       ALTER TABLE "Patient" DROP COLUMN "fax";\n' +
    '20261004_clinic_timezone        ALTER TABLE "Clinic" ADD COLUMN "timezone" TEXT NOT NULL;';
  var head208 = ['Month of migrations', 'Flagged', 'Truly risky', 'False positives'];
  var base208 = ['Before (prompt says "risky")', '18 of 20', '3', '15'];
  var run208 = S('cust', 'Engineer runs /check-migration on last month\'s 20 migrations', 'Four of them shown here. Only the last two match the team\'s definition of risky.', migs208);

  var s208 = {
    id: 'm7-s2-08', who: 'Engineer', labels: { loop: 'Claude Code' }, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'The team <b>can name exactly</b> what is risky: drop a column, change a column type, add a required column with no default.' },
      { id: 'B', label: 'Decider changed', desc: 'Risk is a <b>judgement the team cannot list</b>: it depends on table size, traffic and lock time, and seniors decide case by case.' }
    ],
    runs: {
      A: [
        { steps: [S('file', 'Option A: "be conservative" added', '', cmd208 + 'flag risky changes.\nBe conservative: report a migration only when you are highly confident it is risky.'),
            run208,
            tbl(S('loop', 'Claude is confident about the wrong things', 'It still decides what "risky" means. A new index "may lock Slot"; a nullable column "may break old clients". Both feel certain.', '20261001  RISKY (high confidence): new column may break older mobile clients\n20261002  RISKY (high confidence): index build can lock Slot\n20261003  RISKY: drops data\n20261004  RISKY: NOT NULL without default fails on existing rows', 'bad'),
              head208, [base208, ['After "be conservative"', '15 of 20', '3', '12']])],
          outcome: { ok: false, text: 'Confidence wording does not define risky. Claude is sure about its own idea of risk, so the false positives stay.' }, rate: 0.3 },
        { steps: [S('file', 'Option B: six past migrations labelled risky or safe', 'Claude must infer the line from the labels.', cmd208 + 'flag risky changes.\n<example verdict="risky">DROP COLUMN "insuranceId" - loses data</example>\n<example verdict="safe">ADD COLUMN "nickname" TEXT - nullable, no backfill</example>\n<example verdict="risky">ALTER COLUMN "dob" TYPE DATE - rewrites rows</example>\n<example verdict="safe">CREATE TABLE "AuditLog" - new table</example>\n... (2 more)'),
            run208,
            tbl(S('loop', 'Claude guesses a broader line than the team\'s', 'The examples never show an index. Claude reasons "rewrites or locks a big table = risky" and flags it.', '20261001  safe\n20261002  RISKY: index build locks Slot, like the type change example\n20261003  RISKY: loses data\n20261004  RISKY: existing rows have no value', 'bad'),
              head208, [base208, ['After 6 labelled examples', '7 of 20', '3', '4']])],
          outcome: { ok: false, text: 'Better, but Claude has to guess the boundary from cases. The team can simply state it, and a stated rule leaves nothing to guess.' }, rate: 0.75 },
        { steps: [S('file', 'Option C: the three operations become the criteria', 'Each with a tiny snippet, and everything else explicitly passes.', cmd208 + 'flag the migration ONLY if it does one of these:\n1. Drops a column.            e.g. ALTER TABLE "Patient" DROP COLUMN "fax";\n2. Changes a column\'s type.   e.g. ALTER TABLE "Slot" ALTER COLUMN "start" TYPE TIMESTAMPTZ;\n3. Adds a required column with no default.\n                              e.g. ADD COLUMN "timezone" TEXT NOT NULL;\nAnything else passes. Say which rule matched.', 'ok'),
            run208,
            tbl(S('loop', 'Claude flags only what matches a rule', '', '20261001  pass\n20261002  pass\n20261003  FLAG (rule 1: drops a column)\n20261004  FLAG (rule 3: required column, no default)', 'ok'),
              head208, [base208, ['After explicit criteria', '3 of 20', '3', '0']])],
          outcome: { ok: true, text: 'The vague word "risky" is gone. Categorical criteria with a snippet each tell Claude exactly what counts, so engineers can trust a flag again.' }, rate: 0.95 },
        { steps: [S('file', 'Option D: severity scores, show only "high"', '', cmd208 + 'flag risky changes. Give each finding a severity: low, medium or high.\n(CI wrapper shows engineers only "high".)'),
            run208,
            tbl(S('loop', 'The scores are as vague as the flags', 'The index scores high ("locks a hot table"); the required column scores medium and is hidden.', '20261001  medium\n20261002  HIGH: index build locks Slot\n20261003  HIGH: drops data\n20261004  medium: needs a default   <- hidden from engineers', 'bad'),
              head208, [base208, ['Shown after "high" filter', '9 of 20', '2 (1 hidden)', '7']])],
          outcome: { ok: false, text: 'A score built on the same vague word is just as noisy, and the filter hid a real risk.' }, rate: 0.35 }
      ],
      B: [
        { steps: [S('file', '"Be conservative" added', '', cmd208 + 'flag risky changes. Report only when highly confident.'),
            run208,
            S('loop', 'Claude still flags most migrations', '', '15 of 20 flagged', 'bad')],
          outcome: { ok: false, text: 'Confidence wording does not show Claude where the team draws the line.' }, rate: 0.3 },
        { steps: [S('file', 'Six past migrations, each labelled with the senior\'s reason', 'The reasons carry the judgement: table size, traffic, lock time.', cmd208 + 'flag risky changes.\n<example verdict="risky">CREATE INDEX on "Slot"(40M rows) - locks writes during booking hours; needs CONCURRENTLY</example>\n<example verdict="safe">DROP COLUMN "legacyFax" on "Referral"(2k rows, column always null) - nothing to lose</example>\n<example verdict="risky">ADD COLUMN ... DEFAULT now() on "Appointment" - backfills 12M rows</example>\n... (3 more)', 'ok'),
            S('cust', 'Engineer runs /check-migration', '', 'CREATE INDEX "Slot_clinic_idx" ON "Slot"("clinicId");\nALTER TABLE "Referral" DROP COLUMN "oldCode";'),
            tbl(S('loop', 'Claude applies the seniors\' reasoning to new cases', '', 'Slot_clinic_idx   RISKY: Slot is 40M rows; build without CONCURRENTLY locks booking writes\nReferral.oldCode  safe: tiny table, column unused', 'ok'),
              ['Month of migrations', 'Flagged', 'Truly risky', 'False positives'], [['After labelled examples', '4 of 20', '4', '0']])],
          outcome: { ok: true, text: 'When the line is a judgement nobody can list, labelled examples with reasons show it. This is the world where the runner-up wins.' }, rate: 0.9 },
        { steps: [S('file', 'The closest list the team can write', '', cmd208 + 'flag ONLY: 1. drops a column  2. changes a type  3. required column with no default.'),
            S('cust', 'Engineer runs /check-migration', '', 'CREATE INDEX "Slot_clinic_idx" ON "Slot"("clinicId");\nALTER TABLE "Referral" DROP COLUMN "oldCode";'),
            S('loop', 'The list misses what really matters here', 'It passes a locking index on a 40M-row table and flags a harmless drop.', 'Slot_clinic_idx   pass\nReferral.oldCode  FLAG (rule 1)', 'bad')],
          outcome: { ok: false, text: 'Criteria only work when the rule can be stated. Here it cannot, so the list is wrong in both directions.' }, rate: 0.5 },
        { steps: [S('file', 'Severity scores, show only "high"', '', cmd208 + 'flag risky changes with a severity.'),
            S('loop', 'Scores swing from run to run', '', 'Slot_clinic_idx: high, medium, high, low ...', 'bad')],
          outcome: { ok: false, text: 'A score does not teach the judgement.' }, rate: 0.4 }
      ]
    }
  };

  /* ============================================================ m7-s5-06 explicit criteria vs sample findings */
  var job506 = '.github/workflows/review.yml\n  run: claude -p "$(cat .claude/review-prompt.md)" --output-format json\n\n.claude/review-prompt.md (performance section)\n';
  var diff506 = 'BookingService.kt:41   bookings.forEach { b -> seatRepo.findByBooking(b.id) }        // query per fetched row\nFareController.kt:88   log.info("fare " + fare.id + " for " + user.id)\nPromoUtil.kt:12        codes.map { it.trim() }.filter { it.isNotEmpty() }   // codes has 3 items\nReportJob.kt:27        val all = bookingRepo.findAll()                             // every booking ever';
  var head506 = ['Performance findings / week', 'Posted', 'Dismissed', 'Real bugs caught'];
  var base506 = ['Before', '40', '31 (78%)', '2 of 2'];
  var pr506 = S('cust', 'A pull request touches four places', 'Two are real performance bugs (lines 41 and 27). Two are noise.', diff506);

  var s506 = {
    id: 'm7-s5-06', who: 'CI job', labels: { loop: 'Claude Code' }, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'The category has <b>no definition</b>: only "flag performance problems", plus a "highly confident" line that changed nothing.' },
      { id: 'B', label: 'Decider changed', desc: 'The prompt <b>already lists five concrete performance conditions</b>. The reviewer applies them unevenly on borderline cases.' }
    ],
    runs: {
      A: [
        { steps: [S('file', 'Option A: the vague line becomes concrete conditions', 'The confidence line goes too; it never helped.', job506 + 'Flag a performance problem ONLY when the diff shows one of:\n- a database or HTTP call inside a loop over rows already fetched\n- a query with no limit or page that loads a whole table into memory\n- a blocking call (Thread.sleep, runBlocking, sync HTTP) on a request path\n- nested loops over two collections fetched from the database\nDo not flag string building, small in-memory collections or style.', 'ok'),
            pr506,
            tbl(S('loop', 'Reviewer posts two findings, both real', '', 'BookingService.kt:41  N+1: one seat query per booking. Fetch seats with one IN query.\nReportJob.kt:27       findAll() loads every booking. Page it or stream it.', 'ok'),
              head506, [base506, ['After concrete conditions', '9', '1 (11%)', '2 of 2']])],
          outcome: { ok: true, text: 'The reviewer now knows what a performance problem is. Precision comes from categorical criteria, and the real bugs are still caught.' }, rate: 0.93 },
        { steps: [S('file', 'Option B: three sample findings added', 'Each shows flagged code and the reasoning. There is still no definition.', job506 + 'Flag performance problems. Report only findings you are highly confident about.\n<sample>for (u in users) userRepo.findOrders(u.id) - a query per user; batch it.</sample>\n<sample>Regex("...").matches(s) inside a request loop - compiles every call.</sample>\n<sample>items.map{..}.filter{..}.map{..} - three passes allocate three lists.</sample>'),
            pr506,
            tbl(S('loop', 'Reviewer copies what the samples look like', 'Sample 3 makes any map/filter chain look like a finding, even over three items. Samples show cases; they do not draw the line.', 'BookingService.kt:41  query per booking (like sample 1)\nFareController.kt:88  string concatenation allocates on every call\nPromoUtil.kt:12       map + filter allocates two lists (like sample 3)\nReportJob.kt:27       findAll() may be slow', 'bad'),
              head506, [base506, ['After 3 sample findings', '33', '19 (58%)', '2 of 2']])],
          outcome: { ok: false, text: 'With no criteria, the samples have nothing to illustrate. Claude generalises from their surface, so the noise drops only a little.' }, rate: 0.6 },
        { steps: [S('file', 'Option C: performance category switched off', '', job506 + '(performance section removed)'),
            pr506,
            S('loop', 'Reviewer posts no performance findings', 'Quiet, and the N+1 query on line 41 merges.', '(no performance findings)', 'bad'),
            S('cust', 'Two weeks later in production', 'The team said real performance bugs reach production. This is one.', 'Booking page p95 latency 4.8 s: 1 seat query per booking on large group bookings', 'bad')],
          outcome: { ok: false, text: 'Pausing stops the noise and the real catches together. The team wants to keep the category.' }, rate: 0.2 },
        { steps: [S('file', 'Option D: each finding carries a confidence score; post only above 0.8', '', job506 + 'Flag performance problems. Add "confidence": 0..1 to each finding.\n(CI wrapper posts findings with confidence > 0.8.)'),
            pr506,
            tbl(S('loop', 'Claude rates its own guesses highly', 'Self-reported confidence is the same lever as the "highly confident" line, in numbers.', 'BookingService.kt:41  0.93\nFareController.kt:88  0.86\nPromoUtil.kt:12       0.84\nReportJob.kt:27       0.81', 'bad'),
              head506, [base506, ['After confidence > 0.8', '36', '28 (78%)', '2 of 2']])],
          outcome: { ok: false, text: 'The filter keeps almost everything, because the scores rest on the same missing definition.' }, rate: 0.35 }
      ],
      B: [
        { steps: [S('file', 'The five conditions are reworded', 'They already existed. New wording, same gaps on the borderline.', job506 + 'Flag ONLY: 1. a DB or HTTP call inside a loop over fetched rows  2. ...  5. ...'),
            S('cust', 'A borderline pull request', '', 'for (code in listOf("EUR","USD","GBP")) rateRepo.find(code)   // 3 fixed codes\nfor (leg in itinerary.legs) fareRepo.find(leg.id)            // legs fetched from DB'),
            S('loop', 'Reviewer is inconsistent across runs', 'Run 3 flags the 3-item constant loop; run 5 skips the real one.', 'run 3: flags rateRepo loop (3 constants)\nrun 5: skips fareRepo loop (rows from DB)', 'bad')],
          outcome: { ok: false, text: 'The criteria were already written. Rewording them does not show how to decide the borderline cases.' }, rate: 0.7 },
        { steps: [S('file', 'Three sample findings with reasoning, beside the five conditions', 'Each sample shows a borderline case and why it is or is not condition 1.', job506 + 'Flag ONLY: 1. a DB or HTTP call inside a loop over fetched rows  2. ...  5. ...\n<sample verdict="flag">for (leg in itinerary.legs) fareRepo.find(leg.id) - legs come from the DB, count is unbounded: condition 1.</sample>\n<sample verdict="skip">for (c in listOf("EUR","USD")) rateRepo.find(c) - a fixed list in code, not fetched rows: not condition 1.</sample>\n<sample verdict="flag">orders.forEach { http.get(...) } - HTTP counts as a call: condition 1.</sample>', 'ok'),
            S('cust', 'A borderline pull request', '', 'for (code in listOf("EUR","USD","GBP")) rateRepo.find(code)\nfor (leg in itinerary.legs) fareRepo.find(leg.id)'),
            tbl(S('loop', 'Reviewer decides borderline cases the same way every run', '', 'skip: rateRepo loop over 3 constants\nflag: fareRepo loop over fetched legs (condition 1)', 'ok'),
              head506, [['Before samples', '14', '5 (36%)', '2 of 2'], ['After samples', '10', '1 (10%)', '2 of 2']])],
          outcome: { ok: true, text: 'Once criteria exist, examples with reasoning make them applied consistently. This is the world where the runner-up wins.' }, rate: 0.92 },
        { steps: [S('file', 'Performance category switched off', '', job506 + '(removed)'),
            S('loop', 'Real N+1 queries merge unflagged', '', '(no performance findings)', 'bad')],
          outcome: { ok: false, text: 'The team wants to keep catching real bugs.' }, rate: 0.2 },
        { steps: [S('file', 'Confidence scores, post above 0.8', '', job506 + 'Add "confidence" to each finding.'),
            S('loop', 'Borderline findings score 0.8 to 0.9 either way', '', 'rateRepo loop: 0.84 (posted)\nfareRepo loop: 0.79 (hidden)', 'bad')],
          outcome: { ok: false, text: 'Self-reported confidence does not settle borderline cases.' }, rate: 0.4 }
      ]
    }
  };

  /* ============================================================ m7-s5-07 varied worked cases vs exhaustive list */
  var rule507 = 'Dead code: report code no caller can reach. Code is NOT dead if any feature flag can turn it on.';
  var prs507 = '1  if (config.getBoolean("checkout.v2")) { newCheckout() }           // config lookup\n' +
    '2  @FeatureToggle("seat-map-3d") fun renderSeatMap3d() { ... }        // Kotlin annotation\n' +
    '3  if (process.env.ENABLE_LOYALTY === "1") { showLoyalty() }          // environment check\n' +
    '4  if (await ofClient.getBooleanValue("fare-lock", false)) { ... }    // OpenFeature, adopted last week';
  var head507 = ['Flag form', 'In prompt?', 'Verdict', 'Correct?'];
  var pr507 = S('cust', 'Four pull requests each add flag-guarded code', 'Form 4 comes from a library one team adopted last week.', prs507);
  var list507 = 'Feature flags in this repo take these forms (code behind them is live):\n- config.getBoolean("<key>")\n- @FeatureToggle("<key>")\n- process.env.ENABLE_<NAME>\n- LaunchDarkly: ldClient.boolVariation("<key>", ...)';

  var s507 = {
    id: 'm7-s5-07', who: 'CI job', labels: { loop: 'Claude Code' }, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Flags take many forms, and <b>new forms keep appearing</b> as teams adopt new libraries.' },
      { id: 'B', label: 'Decider changed', desc: 'Flags come in <b>three fixed forms</b>; a lint rule rejects any other flag form at merge.' }
    ],
    runs: {
      A: [
        { steps: [S('file', 'Option A: a complete list of today\'s flag forms', 'Accurate on the day it was written.', '.claude/review-prompt.md\n' + rule507 + '\n' + list507),
            pr507,
            tbl(S('loop', 'Reviewer honours every listed form and misses the new one', 'OpenFeature is not on the list, so getBooleanValue reads as an ordinary call and the branch looks unreachable.', '1  live (config.getBoolean is a listed flag)\n2  live (@FeatureToggle is listed)\n3  live (ENABLE_ env is listed)\n4  DEAD CODE: fare-lock branch has no reachable caller', 'bad'),
              head507, [['config.getBoolean', 'yes', 'live', 'yes'], ['@FeatureToggle', 'yes', 'live', 'yes'], ['process.env.ENABLE_*', 'yes', 'live', 'yes'], ['OpenFeature getBooleanValue', 'no (new)', 'dead', 'no']])],
          outcome: { ok: false, text: 'A list works only for the forms it names. New forms keep arriving, so the list is always one library behind.' }, rate: 0.75 },
        { steps: [S('file', 'Option B: "treat flag-guarded code as live unless certain"', '', '.claude/review-prompt.md\n' + rule507 + '\nTreat any flag-guarded code as live unless you are certain otherwise.'),
            pr507,
            tbl(S('loop', 'Reviewer is "certain" about forms it does not recognise as flags', 'The problem is recognition. Claude does not see an annotation or env check as a flag, so it is certain the code is dead.', '1  live\n2  DEAD CODE: renderSeatMap3d has no callers\n3  DEAD CODE: ENABLE_LOYALTY is never set in the repo\n4  DEAD CODE: fare-lock branch unreachable', 'bad'),
              head507, [['config.getBoolean', '(rule only)', 'live', 'yes'], ['@FeatureToggle', '(rule only)', 'dead', 'no'], ['process.env.ENABLE_*', '(rule only)', 'dead', 'no'], ['OpenFeature getBooleanValue', '(rule only)', 'dead', 'no']])],
          outcome: { ok: false, text: 'It restates the rule Claude already has, with a confidence condition. It adds nothing about what a flag looks like.' }, rate: 0.4 },
        { steps: [S('file', 'Option C: a fresh instance rechecks each dead-code finding', '', 'claude -p "Recheck this finding against the dead-code rule: ' + rule507 + '"'),
            pr507,
            S('loop', 'First pass flags forms 2, 3 and 4 as dead', '', '2 DEAD, 3 DEAD, 4 DEAD', 'bad'),
            S('sub', 'Second instance agrees with all three', 'Same rule, same model, same blind spot about what a flag looks like.', '2 confirmed dead\n3 confirmed dead\n4 confirmed dead', 'bad')],
          outcome: { ok: false, text: 'An independent check helps with self-review bias. Here both passes fail to recognise the same unfamiliar flag forms.' }, rate: 0.4 },
        { steps: [S('file', 'Option D: four worked cases using different flag forms', 'Each gives the verdict and the reason. The reason is the pattern: a runtime value set outside the code decides the branch.', '.claude/review-prompt.md\n' + rule507 + '\n<case>if (config.getBoolean("search.v2")) {...} -> LIVE. The value comes from config at runtime, so it can be switched on.</case>\n<case>@FeatureToggle("promo-banner") fun banner() -> LIVE. The framework calls it when the toggle is on, even with no direct caller.</case>\n<case>if (System.getenv("BETA_FARES") == "true") -> LIVE. An environment value set at deploy time decides it.</case>\n<case>if (DEBUG_FALLBACK && false) {...} -> DEAD. A literal false: nothing outside the code can change it.</case>', 'ok'),
            pr507,
            tbl(S('loop', 'Reviewer recognises the new form it has never seen', 'getBooleanValue reads a value at runtime from a flag service: the same pattern as the cases.', '1  live\n2  live (framework calls it when the toggle is on)\n3  live (deploy-time environment value)\n4  live (flag service value read at runtime)', 'ok'),
              head507, [['config.getBoolean', 'as a case', 'live', 'yes'], ['@FeatureToggle', 'as a case', 'live', 'yes'], ['process.env.ENABLE_*', 'similar case', 'live', 'yes'], ['OpenFeature getBooleanValue', 'never shown', 'live', 'yes']])],
          outcome: { ok: true, text: 'Varied cases with reasons teach the pattern, not the spelling. The reviewer generalises to flag forms that did not exist when the prompt was written.' }, rate: 0.93 }
      ],
      B: [
        { steps: [S('file', 'A complete list of the three allowed forms', 'Lint guarantees no fourth form can merge, so the list is complete and stays complete.', '.claude/review-prompt.md\n' + rule507 + '\nFlags take exactly these forms (code behind them is live):\n- config.getBoolean("<key>")\n- @FeatureToggle("<key>")\n- process.env.ENABLE_<NAME>', 'ok'),
            S('cust', 'Pull requests add flag-guarded code', '', '1  config.getBoolean("checkout.v2")\n2  @FeatureToggle("seat-map-3d")\n3  process.env.ENABLE_LOYALTY'),
            tbl(S('loop', 'Reviewer matches each form against the list', '', '1 live, 2 live, 3 live', 'ok'),
              head507, [['config.getBoolean', 'yes', 'live', 'yes'], ['@FeatureToggle', 'yes', 'live', 'yes'], ['process.env.ENABLE_*', 'yes', 'live', 'yes']])],
          outcome: { ok: true, text: 'For a small fixed set, listing every form is complete and checkable. This is the world where the runner-up wins.' }, rate: 0.97 },
        { steps: [S('file', '"Live unless certain" line', '', rule507 + '\nTreat flag-guarded code as live unless certain.'),
            S('loop', 'Annotation and env forms still read as dead', '', '2 DEAD, 3 DEAD', 'bad')],
          outcome: { ok: false, text: 'Restating the rule still does not say what a flag looks like.' }, rate: 0.5 },
        { steps: [S('loop', 'First pass flags forms 2 and 3 as dead', '', '2 DEAD, 3 DEAD', 'bad'),
            S('sub', 'Second instance confirms both', 'Same blind spot.', 'confirmed', 'bad')],
          outcome: { ok: false, text: 'A second pass shares the first one\'s blind spot.' }, rate: 0.5 },
        { steps: [S('file', 'Four worked cases with reasons', '', rule507 + '\n<case>...</case> x4'),
            S('loop', 'Reviewer gets all three forms right', 'It works, but the reviewer is inferring a set the team could simply write down.', '1 live, 2 live, 3 live', 'ok')],
          outcome: { ok: true, warn: true, text: 'It works, but with a fixed set of three, the explicit list is shorter, complete and easy to check.' }, rate: 0.93 }
      ]
    }
  };

  /* ============================================================ m7-s6-01 nullable field vs worked examples */
  var EXTRACT = 'record_certificate';
  function schema601(deductible, extra) {
    var props = { insured_name: { type: 'string' }, line_type: { type: 'string' }, limit: { type: 'number' }, deductible: deductible };
    var required = ['insured_name', 'line_type', 'limit', 'deductible'];
    if (extra) { props.deductible_status = extra; required.push('deductible_status'); }
    return [{ name: EXTRACT, description: 'Record one coverage line from a certificate of insurance.', input_schema: { type: 'object', properties: props, required: required } }];
  }
  var dedReq = { type: 'number', description: 'Deductible for this coverage line, in USD.' };
  var certs601 = 'Cert 1  Harbor Mutual  General Liability  Each occurrence $1,000,000  Deductible $2,500\n' +
    'Cert 2  Pinecrest Ins.  Auto Liability     Combined single limit $1,000,000  (no deductible printed)\n' +
    'Cert 3  Atlas Casualty  Umbrella           Each occurrence $5,000,000  (no deductible printed)';
  var head601 = ['Certificate', 'Printed deductible', 'Value posted', 'Honest?'];
  var in601 = S('cust', 'Three certificates arrive', 'Two print no deductible at all.', certs601);
  function call601(sys, tools, note) { return req('Pipeline sends each certificate with the extraction tool', note || '', { system: sys, tool_choice: { type: 'tool', name: EXTRACT }, tools: tools, messages: [{ role: 'user', content: '[certificate text]' }] }); }
  var sys601 = 'Extract the coverage line exactly as printed. Do not guess.';

  var s601 = {
    id: 'm7-s6-01', who: 'Pipeline', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Many certificates print no deductible, and the schema marks deductible as a <b>required number</b>.' },
      { id: 'B', label: 'Decider changed', desc: 'Deductible is <b>already nullable</b> with a "return null if not printed" description, yet the model still writes 0 on some blank certificates.' }
    ],
    runs: {
      A: [
        { steps: [in601,
            call601(sys601 + '\nIf no deductible is printed, enter -1.', schema601(dedReq), 'Option A: the field stays a required number; -1 is the agreed marker.'),
            res('Claude returns -1 for the blank certificates', '', [U('toolu_61', EXTRACT, { insured_name: 'Lakeview Dental LLC', line_type: 'auto', limit: 1000000, deductible: -1 })], 'tool_use'),
            S('loop', 'Pydantic accepts it: -1 is a valid number', 'Nothing downstream knows the convention.', 'CoverageLine(deductible=-1.0)  # valid', 'warn'),
            tbl(S('tool', 'Broker system posts the line', 'The marker is now a value. A premium report sums deductibles and goes negative.', { posted: { line: 'auto', deductible: -1 } }, 'bad'),
              head601, [['Cert 1', '$2,500', '2500', 'yes'], ['Cert 2', 'none', '-1', 'no: a number'], ['Cert 3', 'none', '-1', 'no: a number']])],
          outcome: { ok: false, text: 'A marker number is still a number. Every reader must know the convention, and -1 can post as a real value.' }, rate: 0.55 },
        { steps: [in601,
            call601(sys601, schema601({ type: ['number', 'null'], description: 'Deductible in USD as printed. Return null when the certificate prints no deductible. Never use 0 or the limit as a stand-in.' }), 'Option B: deductible may be null, and the description says when.'),
            res('Claude returns null for the blank certificates', 'The schema now has an honest way to say "not printed".', [U('toolu_62', EXTRACT, { insured_name: 'Lakeview Dental LLC', line_type: 'auto', limit: 1000000, deductible: null })], 'tool_use', 'ok'),
            S('loop', 'Pydantic accepts null (Optional[float])', '', 'CoverageLine(deductible=None)  # valid', 'ok'),
            tbl(S('tool', 'Broker system shows "not printed"', 'Assistants can now tell a real deductible from a missing one.', { posted: { line: 'auto', deductible: null, shown_as: 'not printed' } }, 'ok'),
              head601, [['Cert 1', '$2,500', '2500', 'yes'], ['Cert 2', 'none', 'null', 'yes'], ['Cert 3', 'none', 'null', 'yes']])],
          outcome: { ok: true, text: 'A required number forced a guess. A nullable field with a clear description removes the reason to invent one.' }, rate: 0.96 },
        { steps: [in601,
            call601(sys601 + '\n<example>Certificate: Auto Liability, CSL $1,000,000, no deductible printed.\nOutput: {"line_type":"auto","limit":1000000,"deductible": null}</example>\n<example>Certificate: Umbrella, $2,000,000, no deductible printed.\nOutput: {"line_type":"umbrella","limit":2000000,"deductible": null}</example>', schema601(dedReq), 'Option C: two worked certificates. The schema still requires a number.'),
            res('Claude follows the examples and returns null', '', [U('toolu_63', EXTRACT, { insured_name: 'Lakeview Dental LLC', line_type: 'auto', limit: 1000000, deductible: null })], 'tool_use'),
            S('loop', 'Pydantic rejects it: deductible must be a number', 'The examples show an output the schema forbids. There is no valid empty answer to demonstrate.', 'ValidationError: deductible\n  Input should be a valid number [input_value=None]', 'bad'),
            res('On retry with the error, Claude supplies a number', 'Told a number is required, it falls back to a guess.', [U('toolu_64', EXTRACT, { insured_name: 'Lakeview Dental LLC', line_type: 'auto', limit: 1000000, deductible: 0 })], 'tool_use', 'bad'),
            tbl(S('tool', 'The invented 0 posts', '', { posted: { line: 'auto', deductible: 0 } }, 'bad'),
              head601, [['Cert 1', '$2,500', '2500', 'yes'], ['Cert 2', 'none', '0 (after retry)', 'no'], ['Cert 3', 'none', '5000000 (after retry)', 'no']])],
          outcome: { ok: false, text: 'Examples reduce hallucination once a blank is allowed. While the schema demands a number, the only valid outputs are invented ones.' }, rate: 0.5 },
        { steps: [in601,
            call601(sys601, schema601(dedReq, { type: 'string', enum: ['printed', 'not_printed'] }), 'Option D: a status enum beside the still-required number.'),
            res('Claude labels the gap, and still fills the number', '', [U('toolu_65', EXTRACT, { insured_name: 'Lakeview Dental LLC', line_type: 'auto', limit: 1000000, deductible: 0, deductible_status: 'not_printed' })], 'tool_use', 'warn'),
            tbl(S('tool', 'Record keeps deductible = 0', 'not_printed lines go to an assistant queue, but the record still holds the invented 0, and reports read the number.', { posted: { line: 'auto', deductible: 0, deductible_status: 'not_printed' } }, 'bad'),
              head601, [['Cert 1', '$2,500', '2500', 'yes'], ['Cert 2', 'none', '0 + not_printed', 'no: 0 stored'], ['Cert 3', 'none', '5000000 + not_printed', 'no: limit stored']])],
          outcome: { ok: false, text: 'The status labels the gap, but a required number still forces an invented value into the record.' }, rate: 0.6 }
      ],
      B: [
        { steps: [in601, call601(sys601 + '\nIf no deductible is printed, enter -1.', schema601({ type: ['number', 'null'] })),
            res('Claude returns -1', '', [U('toolu_66', EXTRACT, { line_type: 'auto', deductible: -1 })], 'tool_use'),
            S('tool', '-1 posts as a value', '', { deductible: -1 }, 'bad')],
          outcome: { ok: false, text: 'A marker number replaces an honest null that the schema already allows.' }, rate: 0.55 },
        { steps: [in601, call601(sys601, schema601({ type: ['number', 'null'], description: 'Return null when no deductible is printed.' }), 'The field is already nullable with this description. Option B changes nothing.'),
            tbl(res('Claude still writes 0 on some blank certificates', 'The structure was never the problem in this world; the behaviour is.', [U('toolu_67', EXTRACT, { line_type: 'auto', limit: 1000000, deductible: 0 })], 'tool_use', 'bad'),
              ['Blank certificates (of 20)', 'null', '0', 'limit copied'], [['Nullable, description only', '16', '3', '1']])],
          outcome: { ok: false, text: 'Making the field nullable is already done. It removed the forced guess; it did not stop the habit.' }, rate: 0.8 },
        { steps: [in601,
            call601(sys601 + '\n<example>Certificate: Auto Liability, CSL $1,000,000, no deductible printed.\nOutput: {"line_type":"auto","limit":1000000,"deductible": null}</example>\n<example>Certificate: Umbrella, $2,000,000, no deductible printed.\nOutput: {"line_type":"umbrella","limit":2000000,"deductible": null}</example>', schema601({ type: ['number', 'null'], description: 'Return null when no deductible is printed.' }), 'Two worked certificates, and now null is a valid output to show.'),
            res('Claude returns null, as the examples show', '', [U('toolu_68', EXTRACT, { line_type: 'auto', limit: 1000000, deductible: null })], 'tool_use', 'ok'),
            tbl(S('loop', 'Pydantic accepts; the line posts as "not printed"', '', 'CoverageLine(deductible=None)', 'ok'),
              ['Blank certificates (of 20)', 'null', '0', 'limit copied'], [['Nullable, description only', '16', '3', '1'], ['Plus two worked examples', '19', '1', '0']])],
          outcome: { ok: true, text: 'With the field already optional, worked examples are the next lever against extraction hallucination. This is the world where the runner-up wins.' }, rate: 0.94 },
        { steps: [in601, call601(sys601, schema601({ type: ['number', 'null'] }, { type: 'string', enum: ['printed', 'not_printed'] })),
            res('Claude sets not_printed and still writes 0 sometimes', '', [U('toolu_69', EXTRACT, { deductible: 0, deductible_status: 'not_printed' })], 'tool_use', 'bad')],
          outcome: { ok: false, text: 'A status field labels the gap without changing the habit.' }, rate: 0.75 }
      ]
    }
  };

  /* ============================================================ m7-s6-02 other + detail vs nullable enum */
  var LINES = ['general_liability', 'auto', 'workers_comp', 'umbrella', 'property'];
  function schema602(lineType, extra) {
    var props = { line_type: lineType, limit: { type: 'number' } };
    if (extra) props.line_type_detail = extra;
    return [{ name: EXTRACT, input_schema: { type: 'object', properties: { coverage_lines: { type: 'array', items: { type: 'object', properties: props, required: ['line_type', 'limit'] } } } } }];
  }
  var cert602 = 'Certificate, Brightwave Analytics Inc.\n  COMMERCIAL GENERAL LIABILITY   Each occurrence $1,000,000\n  CYBER LIABILITY                Aggregate       $2,000,000\n  PROFESSIONAL LIABILITY (E&O)   Each claim      $1,000,000\n  CRIME / FIDELITY               Each loss       $250,000     <- new on certificates this month';
  var head602 = ['Printed line', 'line_type posted', 'Detail kept', 'Right?'];
  var in602 = S('cust', 'A certificate with four lines', 'Every line heading is printed clearly.', cert602);
  function call602(tools, note) { return req('Pipeline sends the certificate with the extraction tool', note, { tool_choice: { type: 'tool', name: EXTRACT }, tools: tools, messages: [{ role: 'user', content: '[certificate text]' }] }); }
  var cert602b = 'Certificate, OCR scan, Brightwave Analytics Inc.\n  COMMERCIAL GENERAL LIABILITY   Each occurrence $1,000,000\n  ##### ##B#L#TY (smudged)       Aggregate       $2,000,000';

  var s602 = {
    id: 'm7-s6-02', who: 'Pipeline', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Certificates list lines outside the five-value enum, and the line type is <b>printed clearly</b> on every one.' },
      { id: 'B', label: 'Decider changed', desc: 'On the problem lines the type is <b>not readable</b>: the OCR scan smudges the heading and only the limit survives.' }
    ],
    runs: {
      A: [
        { steps: [in602,
            call602(schema602({ type: ['string', 'null'], enum: LINES.concat([null]), description: 'null when the line matches none of the listed values.' }), 'Option A: line_type may be null.'),
            res('Claude returns null for three lines', 'Correctly avoids the wrong bucket, and throws away the printed name.', [U('toolu_71', EXTRACT, { coverage_lines: [{ line_type: 'general_liability', limit: 1000000 }, { line_type: null, limit: 2000000 }, { line_type: null, limit: 1000000 }, { line_type: null, limit: 250000 }] })], 'tool_use'),
            tbl(S('tool', 'Three lines post as "type unknown"', 'The type was printed. An assistant must reopen the PDF to learn what null stands for.', { posted: ['general_liability', 'unknown', 'unknown', 'unknown'] }, 'bad'),
              head602, [['General Liability', 'general_liability', '-', 'yes'], ['Cyber Liability', 'null', 'no', 'no: lost'], ['Professional (E&O)', 'null', 'no', 'no: lost'], ['Crime / Fidelity', 'null', 'no', 'no: lost']])],
          outcome: { ok: false, text: 'Null means "we do not know". Here the type is printed, so null discards information the certificate gave.' }, rate: 0.5 },
        { steps: [in602,
            call602(schema602({ type: 'string', enum: LINES.concat(['cyber', 'professional_liability']) }), 'Option B: two values added to the enum.'),
            res('Claude places cyber and E&O, then forces crime', 'Crime is new this month and not in the list.', [U('toolu_72', EXTRACT, { coverage_lines: [{ line_type: 'general_liability', limit: 1000000 }, { line_type: 'cyber', limit: 2000000 }, { line_type: 'professional_liability', limit: 1000000 }, { line_type: 'general_liability', limit: 250000 }] })], 'tool_use', 'bad'),
            tbl(S('tool', 'Crime posts as general liability', 'Same failure, next line type, until someone edits the schema again.', { posted: ['general_liability', 'cyber', 'professional_liability', 'general_liability'] }, 'bad'),
              head602, [['General Liability', 'general_liability', '-', 'yes'], ['Cyber Liability', 'cyber', '-', 'yes'], ['Professional (E&O)', 'professional_liability', '-', 'yes'], ['Crime / Fidelity', 'general_liability', '-', 'no']])],
          outcome: { ok: false, text: 'It fixes today\'s two lines. The list keeps growing, so each new line breaks the same way.' }, rate: 0.8 },
        { steps: [in602,
            call602(schema602({ type: 'string', enum: LINES }), 'Option C: same enum, plus a validator comparing the printed heading to line_type.'),
            res('Claude forces cyber into general_liability', '', [U('toolu_73', EXTRACT, { coverage_lines: [{ line_type: 'general_liability', limit: 2000000 }] })], 'tool_use'),
            S('loop', 'Validator: "CYBER LIABILITY" does not match general_liability. Retry.', '', 'retry 1: "Line 2 heading is CYBER LIABILITY; general_liability does not match."', 'warn'),
            res('Retry picks the next-nearest wrong value', 'The right value is not in the enum, so no retry can find it.', [U('toolu_74', EXTRACT, { coverage_lines: [{ line_type: 'property', limit: 2000000 }] })], 'tool_use', 'bad'),
            S('loop', 'Retries exhausted; certificate goes to the exception queue', '', 'retry 2: umbrella (mismatch)\n-> exception queue: 3 lines', 'bad')],
          outcome: { ok: false, text: 'Retrying with the error fixes mapping mistakes. It cannot help when the correct value does not exist in the enum.' }, rate: 0.3 },
        { steps: [in602,
            call602(schema602({ type: 'string', enum: LINES.concat(['other']), description: 'Use other when the printed line is none of the listed types.' }, { type: ['string', 'null'], description: 'When line_type is other: the line name exactly as printed.' }), 'Option D: other in the enum, plus a detail string for the carrier\'s wording.'),
            res('Claude uses other and keeps the printed name', '', [U('toolu_75', EXTRACT, { coverage_lines: [{ line_type: 'general_liability', limit: 1000000 }, { line_type: 'other', line_type_detail: 'Cyber Liability', limit: 2000000 }, { line_type: 'other', line_type_detail: 'Professional Liability (E&O)', limit: 1000000 }, { line_type: 'other', line_type_detail: 'Crime / Fidelity', limit: 250000 }] })], 'tool_use', 'ok'),
            tbl(S('tool', 'Lines post with their real names', 'Next month\'s new line type will land the same way, with no schema edit.', { posted: ['general_liability', 'other: Cyber Liability', 'other: Professional Liability (E&O)', 'other: Crime / Fidelity'] }, 'ok'),
              head602, [['General Liability', 'general_liability', '-', 'yes'], ['Cyber Liability', 'other', 'Cyber Liability', 'yes'], ['Professional (E&O)', 'other', 'Professional Liability (E&O)', 'yes'], ['Crime / Fidelity', 'other', 'Crime / Fidelity', 'yes']])],
          outcome: { ok: true, text: 'The value is present but unlisted. other plus a detail string keeps it, for any line type carriers add.' }, rate: 0.96 }
      ],
      B: [
        { steps: [S('cust', 'An OCR scan with a smudged line heading', 'Only the limit survives on line 2.', cert602b),
            call602(schema602({ type: ['string', 'null'], enum: LINES.concat([null]), description: 'null when the line type is not printed or not readable.' }), 'line_type may be null.'),
            res('Claude returns null for the unreadable line', 'An honest "not available".', [U('toolu_76', EXTRACT, { coverage_lines: [{ line_type: 'general_liability', limit: 1000000 }, { line_type: null, limit: 2000000 }] })], 'tool_use', 'ok'),
            S('tool', 'Line posts as "type unknown" and goes to an assistant', 'Nothing was printed to keep, so nothing is lost.', { posted: ['general_liability', 'unknown'], exception_queue: 'line 2: type unreadable' }, 'ok')],
          outcome: { ok: true, text: 'When the value is missing or unreadable, null is the honest answer. This is the world where the runner-up wins.' }, rate: 0.95 },
        { steps: [S('cust', 'An OCR scan with a smudged line heading', '', cert602b),
            res('Claude guesses a listed value', 'More enum values give it more ways to guess.', [U('toolu_77', EXTRACT, { coverage_lines: [{ line_type: 'general_liability', limit: 1000000 }, { line_type: 'professional_liability', limit: 2000000 }] })], 'tool_use', 'bad')],
          outcome: { ok: false, text: 'Adding values does not help when the type cannot be read.' }, rate: 0.6 },
        { steps: [S('cust', 'An OCR scan with a smudged line heading', '', cert602b),
            res('Claude guesses general_liability', '', [U('toolu_78', EXTRACT, { coverage_lines: [{ line_type: 'general_liability', limit: 2000000 }] })], 'tool_use'),
            S('loop', 'Validator has no readable heading to compare; the guess passes', '', 'heading: "##### ##B#L#TY" -> no match rule -> accepted', 'bad')],
          outcome: { ok: false, text: 'A check against the printed name has nothing to check here.' }, rate: 0.5 },
        { steps: [S('cust', 'An OCR scan with a smudged line heading', '', cert602b),
            res('Claude picks other and invents a detail', 'other says "known but unlisted". Nothing is known, so the detail is a guess from the surviving letters.', [U('toolu_79', EXTRACT, { coverage_lines: [{ line_type: 'general_liability', limit: 1000000 }, { line_type: 'other', line_type_detail: 'Cyber Liability', limit: 2000000 }] })], 'tool_use', 'bad'),
            S('tool', 'A guessed line name posts as if printed', '', { posted: ['general_liability', 'other: Cyber Liability'] }, 'bad')],
          outcome: { ok: false, text: 'other plus detail is for present but unlisted values. For an unreadable value it invites a fabricated detail.' }, rate: 0.65 }
      ]
    }
  };

  /* ============================================================ m7-s6-04 worked documents vs longer descriptions */
  function schema604(desc) {
    return [{ name: EXTRACT, input_schema: { type: 'object', properties: { coverage_lines: { type: 'array', items: { type: 'object', properties: {
      line_type: { type: 'string', description: desc.line },
      each_occurrence: { type: ['number', 'null'], description: desc.occ },
      aggregate: { type: ['number', 'null'], description: desc.agg } } } } } } }];
  }
  var detailed = { line: 'Coverage line as printed, mapped to the enum.', occ: 'The per-occurrence limit in USD: the most the policy pays for one event. Not the aggregate, not a sublimit.', agg: 'The general aggregate limit in USD: the most paid in the policy period. Ignore products/completed-ops aggregates.' };
  var docs604 = 'A  ACORD 25 form (standard)       EACH OCCURRENCE $1,000,000 | GENERAL AGGREGATE $2,000,000\n' +
    'B  Schedule, prose paragraph      "...shall not exceed one million dollars ($1,000,000) for any one occurrence, subject to..."\n' +
    'C  Schedule, footnote             Each Occurrence $1,000,000 (3)   ...   (3) Reduced to $500,000 for claims arising from mold.\n' +
    'D  Schedule, multi-column table   | Coverage | Occ.  | Agg.  |  with limits for 2 lines side by side, wrapped across columns';
  var head604 = ['Layout', 'Before', 'After'];
  var in604 = S('cust', 'Four documents, four layouts', 'The standard form, then three carrier schedules.', docs604);
  function call604(sys, desc, note, mark) { return req('Pipeline sends each document with the extraction tool', note, { system: sys, tool_choice: { type: 'tool', name: EXTRACT }, tools: schema604(desc), messages: [{ role: 'user', content: '[document text]' }] }, mark); }
  var sys604 = 'Extract every coverage line and its limits exactly as stated in the document.';
  var wrongD = { coverage_lines: [{ line_type: 'general_liability', each_occurrence: 2000000, aggregate: 1000000 }] };

  var s604 = {
    id: 'm7-s6-04', who: 'Pipeline', lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Field descriptions are <b>already detailed</b>; the prompt has <b>no worked document</b>. Accuracy drops on carrier schedules.' },
      { id: 'B', label: 'Decider changed', desc: 'Field descriptions are <b>one-liners</b> ("occurrence: the occurrence limit"), and errors appear on the standard form too.' }
    ],
    runs: {
      A: [
        { steps: [in604,
            call604(sys604 + '\n\n<worked_example layout="prose schedule">...shall not exceed one million dollars ($1,000,000) for any one occurrence and two million ($2,000,000) in the aggregate...\nFound: each_occurrence 1000000 in sentence 1; aggregate 2000000 in the same sentence.</worked_example>\n<worked_example layout="footnoted schedule">Each Occurrence $1,000,000 (2) ... (2) Reduced to $250,000 for flood.\nFound: each_occurrence 1000000; footnote 2 is a sublimit, not the limit.</worked_example>\n<worked_example layout="multi-column table">Two lines side by side; the Occ. column for line 2 wraps under line 1.\nFound: read down each column, match by row label.</worked_example>', detailed, 'Option A: three worked schedules, each showing where every limit was found.', 'ok'),
            res('Document D: Claude reads the table column by column', '', [U('toolu_81', EXTRACT, { coverage_lines: [{ line_type: 'general_liability', each_occurrence: 1000000, aggregate: 2000000 }, { line_type: 'auto', each_occurrence: 1000000, aggregate: null }] })], 'tool_use', 'ok'),
            tbl(S('loop', 'Field accuracy on 200 held-out documents, by layout', 'The model has now seen where limits hide in unfamiliar layouts.', 'accuracy by layout', 'ok'),
              head604, [['Standard form', '98%', '98%'], ['Prose paragraph', '71%', '94%'], ['Footnote', '64%', '92%'], ['Multi-column table', '68%', '95%']])],
          outcome: { ok: true, text: 'The descriptions already said what to extract. Worked documents across layouts show where to find it, which prose alone does not.' }, rate: 0.94 },
        { steps: [in604,
            call604(sys604, { line: detailed.line, occ: detailed.occ + ' In prose schedules it may be written in words ("one million dollars") inside a sentence. Check footnotes, which may reduce or qualify it. In multi-column tables, read down the column headed Occ. or Each Occurrence.', agg: detailed.agg + ' In multi-column tables it may sit in a wrapped cell under another line.' }, 'Option B: each description gains notes on non-standard layouts.'),
            res('Document D: Claude still swaps the wrapped columns', 'The notes describe the layout. Faced with the real table, Claude still pairs the wrong cells.', [U('toolu_82', EXTRACT, wrongD)], 'tool_use', 'bad'),
            tbl(S('loop', 'Field accuracy on 200 held-out documents, by layout', 'A small gain. The descriptions were already detailed; more prose about layout is weaker than showing a layout.', 'accuracy by layout', 'bad'),
              head604, [['Standard form', '98%', '98%'], ['Prose paragraph', '71%', '77%'], ['Footnote', '64%', '72%'], ['Multi-column table', '68%', '71%']])],
          outcome: { ok: false, text: 'Fuller descriptions help when descriptions are thin. These were already detailed, so describing layouts in more words adds little.' }, rate: 0.72 },
        { steps: [in604,
            S('loop', 'Option C: classify first, then route', '', 'kind = classify(doc)            # "acord_form" | "carrier_schedule"\nprompt = PROMPTS[kind]           # schedule prompt: instructions only'),
            call604('You are reading a carrier policy schedule. ' + sys604, detailed, 'The schedule prompt is narrower, and still has no worked document.'),
            res('Document D: same swapped columns', 'Routing narrowed the prompt; the unfamiliar layout is the same.', [U('toolu_83', EXTRACT, wrongD)], 'tool_use', 'bad'),
            tbl(S('loop', 'Field accuracy on 200 held-out documents, by layout', '', 'accuracy by layout', 'bad'),
              head604, [['Standard form', '98%', '98%'], ['Prose paragraph', '71%', '73%'], ['Footnote', '64%', '66%'], ['Multi-column table', '68%', '70%']])],
          outcome: { ok: false, text: 'A separate prompt for schedules still faces the same varied layouts with no examples.' }, rate: 0.68 },
        { steps: [in604,
            call604(sys604 + '\nIf a limit is not in a standard box, return null.', detailed, 'Option D: limits may be null; schedules with nulls go to the account assistants.'),
            res('Document B: Claude returns null for a limit that is printed', '"one million dollars ... any one occurrence" is right there in the paragraph.', [U('toolu_84', EXTRACT, { coverage_lines: [{ line_type: 'general_liability', each_occurrence: null, aggregate: null }] })], 'tool_use', 'warn'),
            tbl(S('cust', 'Account assistants receive the schedules to key by hand', 'The values were in the documents; the work moved to people.', 'exception queue: 61 of 200 documents (all with printed limits)', 'bad'),
              ['Layout', 'Wrong values posted', 'Sent to people'], [['Standard form', '2%', '0%'], ['Prose paragraph', '3%', '29%'], ['Footnote', '4%', '35%'], ['Multi-column table', '3%', '31%']])],
          outcome: { ok: false, text: 'Nullable fields are for values that are absent. These limits are printed, so this hides the error by handing it to people.' }, rate: 0.6 }
      ],
      B: [
        { steps: [in604,
            call604(sys604 + '\n\n<worked_example layout="prose schedule">...</worked_example> (x3)', { line: 'The line.', occ: 'The occurrence limit.', agg: 'The aggregate.' }, 'Worked schedules added; the field descriptions stay one-liners.'),
            res('Document A: Claude puts the products aggregate in aggregate', 'Nothing says which aggregate is meant. The examples never needed to say it.', [U('toolu_85', EXTRACT, { coverage_lines: [{ line_type: 'general_liability', each_occurrence: 1000000, aggregate: 3000000 }] })], 'tool_use', 'bad'),
            tbl(S('loop', 'Field accuracy by layout', 'Layouts improve, but every layout still confuses fields.', 'accuracy by layout', 'bad'),
              head604, [['Standard form', '81%', '84%'], ['Prose paragraph', '62%', '79%'], ['Footnote', '55%', '76%'], ['Multi-column table', '58%', '80%']])],
          outcome: { ok: false, text: 'Examples show where values sit. They do not define which value a thin field means.' }, rate: 0.78 },
        { steps: [in604,
            call604(sys604, detailed, 'Descriptions rewritten in full: what each limit is, which aggregate, sublimits excluded.', 'ok'),
            res('Document A: the right aggregate in the right field', '', [U('toolu_86', EXTRACT, { coverage_lines: [{ line_type: 'general_liability', each_occurrence: 1000000, aggregate: 2000000 }] })], 'tool_use', 'ok'),
            tbl(S('loop', 'Field accuracy by layout', 'Most errors were field confusion. Clear descriptions fix them on every layout.', 'accuracy by layout', 'ok'),
              head604, [['Standard form', '81%', '98%'], ['Prose paragraph', '62%', '91%'], ['Footnote', '55%', '90%'], ['Multi-column table', '58%', '92%']])],
          outcome: { ok: true, text: 'When descriptions are thin, making them detailed is the first fix. This is the world where the runner-up wins.' }, rate: 0.92 },
        { steps: [in604, S('loop', 'Classify, then route to a schedule prompt', 'The thin descriptions come along.', 'prompt = PROMPTS[classify(doc)]'),
            res('Field confusion continues', '', [U('toolu_87', EXTRACT, { coverage_lines: [{ line_type: 'general_liability', aggregate: 3000000 }] })], 'tool_use', 'bad')],
          outcome: { ok: false, text: 'Routing does not clarify what a field means.' }, rate: 0.6 },
        { steps: [in604, call604(sys604 + '\nIf unsure, return null.', { line: 'The line.', occ: 'The occurrence limit.', agg: 'The aggregate.' }, ''),
            S('cust', 'Assistants key a third of documents by hand', '', 'exception queue: 70 of 200', 'bad')],
          outcome: { ok: false, text: 'The limits are printed; null moves the work to people.' }, rate: 0.55 }
      ]
    }
  };

  [s207, s208, s506, s507, s601, s602, s604].forEach(L.add);
})();
