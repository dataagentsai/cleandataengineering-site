/* CCA-F Mock Exam #7 - scripted simulations for CLI output, built-in tools, MCP and batch:
   m7-s2-06, m7-s5-03, m7-s4-01, m7-s4-03, m7-s5-04, m7-s5-05, m7-s5-08, m7-s6-05.
   Uses the helper library in sims.js (window.SIMLIB). Hand-written, deterministic traces. */
(function () {
  var L = window.SIMLIB, S = L.S, req = L.req, res = L.res, T = L.T, U = L.U, R = L.R, E = L.E, X = L.X;

  /* ============================================================ m7-s2-06 claude -p: JSON output + schema (select 2) */
  var prompt206 = 'Generate Jest tests for the new endpoint POST /appointments/:id/reschedule. Run them.';
  var schema206 = { type: 'object', required: ['files_created', 'passed'], properties: {
    files_created: { type: 'array', items: { type: 'string' } }, passed: { type: 'boolean' }, failing_tests: { type: 'array', items: { type: 'string' } } } };
  var files206 = ['server/src/appointments/__tests__/reschedule.test.ts', 'server/src/appointments/__tests__/reschedule.fixtures.ts'];
  var envelope206 = { type: 'result', subtype: 'success', is_error: false, num_turns: 11, duration_ms: 48210,
    session_id: '7f3c2a91-5d0e-4b8a-9c61-2e4f0b7d1a33', total_cost_usd: 0.41,
    result: 'Created two test files for the reschedule endpoint. All 14 tests pass.',
    structured_output: { files_created: files206, passed: true, failing_tests: [] } };
  var cmdBoth = 'claude -p "$PROMPT" \\\n  --output-format json \\\n  --json-schema "$(cat tests.schema.json)"';
  var parseOk = 'out = json.loads(stdout)\nif out["is_error"]:\n    fail(out["result"])\nfiles  = out["structured_output"]["files_created"]\npassed = out["structured_output"]["passed"]';
  function run206(focus) {
    var st = [S('cust', 'Engineer merges a ticket; the script starts', '', prompt206)];
    if (focus === 'schema') st.push(S('file', 'tests.schema.json (option C)', 'The schema names the fields: a list of new files and a pass or fail flag. They are required.', schema206, 'ok'));
    st.push(S('loop', 'Script runs the CLI with both flags', focus === 'json' ? 'Option A adds --output-format json. It is half of the keyed pair; option C supplies the schema.' : 'Option C adds --json-schema. It works inside the JSON output that option A turns on.', cmdBoth));
    st.push(S('tool', 'stdout: one JSON object, the same keys every run', focus === 'json'
      ? 'The envelope is fixed: is_error, session_id and result are always there. Without a schema, "result" would still be free prose.'
      : 'The schema-shaped answer arrives in structured_output, separate from the prose in "result".', envelope206, 'ok'));
    st.push(S('loop', 'Script parses by field name', 'No searching through sentences. Wording can change; the keys cannot.', parseOk, 'ok'));
    st.push(S('cust', 'Engineer sees the ticket comment', '', 'reschedule: 2 test files created, tests passed', 'ok'));
    return st;
  }
  var proseRun = 'Done! I wrote the tests:\n```json\n{"files": ["server/src/appointments/__tests__/reschedule.test.ts"], "status": "pass"}\n```\nNote: one fixture file was also added, and I re-ran the flaky timezone test twice before it passed.';
  var s206 = {
    id: 'm7-s2-06', who: 'Engineer', labels: { loop: 'CI script' }, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'A <b>script parses</b> the reply and needs the same named fields on every run.' },
      { id: 'B', label: 'Decider changed', desc: 'The reply is pasted into the ticket for <b>a person to read</b>. A tidy, similar layout is enough; no code parses it.' }
    ],
    runs: {
      A: [
        { steps: run206('json'),
          outcome: { ok: true, text: 'The CLI prints a fixed JSON envelope, so the script reads fields by name instead of guessing from prose. With the schema (option C) the fields inside it are fixed too.' }, rate: 1 },
        { steps: [S('cust', 'Engineer merges a ticket; the script starts', '', prompt206),
            S('loop', 'Script runs the CLI with a JSON example in the prompt', 'Option B. No flags change; only the prompt asks for JSON.', 'claude -p "$PROMPT\n\nReply with ONLY this JSON:\n{\\"files_created\\": [\\"...\\"], \\"passed\\": true}"'),
            S('tool', 'stdout, runs 1 to 17: the JSON object alone', 'Most of the time Claude follows the example.', '{"files_created": ["server/src/appointments/__tests__/reschedule.test.ts"], "passed": true}', 'ok'),
            S('tool', 'stdout, run 18: prose around it, and renamed keys', 'Plain text output. Nothing outside the prompt holds the shape in place.', proseRun, 'warn'),
            S('loop', 'Script parses', 'The output starts with "Done!", so json.loads fails. Even after cutting out the block, "files_created" is now "files".', 'json.loads(stdout)\n# JSONDecodeError: Expecting value: line 1 column 1 (char 0)', 'bad'),
            S('cust', 'Engineer sees', 'The run passed, but the script reports a failure.', 'reschedule: could not read Claude output (parse error)', 'bad')],
          outcome: { ok: false, text: 'A JSON example in the prompt is followed most of the time, not every time. A parser needs a shape the CLI enforces, which is what the flags give.' }, rate: 0.9 },
        { steps: run206('schema'),
          outcome: { ok: true, text: 'The schema fixes which named fields exist: files_created and passed. Together with JSON output, the script gets exactly the fields it needs.' }, rate: 1 },
        { steps: [S('cust', 'Engineer merges a ticket; the script starts', '', prompt206),
            S('loop', 'Script runs the CLI with --verbose', 'Option D. The script plans to scrape the tool-call log.', 'claude -p "$PROMPT" --verbose'),
            S('tool', 'stdout: a diagnostic log, then the prose reply', 'Made for people debugging. Its layout is not a contract and changes between versions.', '[tool] Write server/src/appointments/__tests__/reschedule.test.ts\n[tool] Edit server/src/appointments/__tests__/helpers.ts\n[tool] Bash npx jest reschedule\n  Tests: 14 passed, 14 total\n\u2026\nCreated the tests. Everything passes.', 'warn'),
            S('loop', 'Script greps for "Write" lines and "passed"', 'Edit to an existing helper is counted as nothing; the pass status is a phrase in a sentence.', 'files  = re.findall(r"\\[tool\\] Write (\\S+)", stdout)   # misses 1 file\npassed = "Everything passes" in stdout              # next run says "All green"', 'bad'),
            S('cust', 'Engineer sees', '', 'reschedule: 1 file created, passed = false', 'bad')],
          outcome: { ok: false, text: 'Verbose output is a different free-text stream. The script still guesses from wording, just in a longer text.' }, rate: 0.6 }
      ],
      B: [
        { steps: [S('cust', 'Engineer merges a ticket; the script starts', '', prompt206),
            S('loop', 'Script runs the CLI with both flags and pastes stdout into the ticket', '', cmdBoth),
            S('tool', 'stdout: the JSON envelope', '', envelope206),
            S('cust', 'Engineer reads the ticket comment', 'Correct, but it is a JSON dump. Someone has to write code to turn it back into a sentence.', '{"type":"result","subtype":"success","is_error":false,"num_turns":11, \u2026 "result":"Created two test files \u2026"}', 'warn')],
          outcome: { ok: true, warn: true, text: 'Reliable, but heavier than needed. A person reading the reply does not need a machine envelope.' }, rate: 1 },
        { steps: [S('cust', 'Engineer merges a ticket; the script starts', '', prompt206),
            S('loop', 'Script runs the CLI with a format example in the prompt', '', 'claude -p "$PROMPT\n\nEnd with a short summary like:\nFiles: <list>\nTests: <passed|failed>"'),
            S('tool', 'stdout: a short summary in the requested layout', 'An occasional extra sentence does no harm; a person reads it.', 'Files: reschedule.test.ts, reschedule.fixtures.ts\nTests: passed (14/14)', 'ok'),
            S('cust', 'Engineer reads the ticket comment', '', 'Files: reschedule.test.ts, reschedule.fixtures.ts\nTests: passed (14/14)', 'ok')],
          outcome: { ok: true, text: 'When a person reads the reply, a format example in the prompt gives a consistent layout at no extra cost. This is the world where the runner-up wins.' }, rate: 0.95 },
        { steps: [S('cust', 'Engineer merges a ticket; the script starts', '', prompt206),
            S('loop', 'Script runs the CLI with a schema and pastes the fields', '', cmdBoth),
            S('cust', 'Engineer reads the ticket comment', 'The fields are right, but the explanation of the flaky test is gone. The schema had no box for it.', '{"files_created": [\u2026], "passed": true, "failing_tests": []}', 'warn')],
          outcome: { ok: true, warn: true, text: 'A schema fixes fields for code. For a person it removes the useful prose and adds work.' }, rate: 1 },
        { steps: [S('cust', 'Engineer merges a ticket; the script starts', '', prompt206),
            S('loop', 'Script runs the CLI with --verbose and pastes stdout', '', 'claude -p "$PROMPT" --verbose'),
            S('cust', 'Engineer reads the ticket comment', 'Ninety lines of tool log before the two lines that matter.', '[tool] Write \u2026\n[tool] Edit \u2026\n[tool] Bash npx jest \u2026\n\u2026 (88 more lines)', 'bad')],
          outcome: { ok: false, text: 'A debug log is not a readable summary for anyone.' }, rate: 0.5 }
      ]
    }
  };

  /* ============================================================ m7-s5-03 review job: --output-format json + --json-schema */
  var reviewCmd = 'claude -p "Review this PR diff. Report findings." \\\n  --output-format json \\\n  --json-schema "$(cat findings.schema.json)"';
  var findingsSchema = { type: 'object', required: ['findings'], properties: { findings: { type: 'array', items: { type: 'object',
    required: ['file', 'line', 'severity', 'message'], properties: { file: { type: 'string' }, line: { type: 'integer' }, severity: { enum: ['blocker', 'major', 'minor'] }, message: { type: 'string' } } } } } };
  var findings = [
    { file: 'booking/src/main/kotlin/FareQuoteService.kt', line: 88, severity: 'major', message: 'Currency is dropped when the quote is cached; EUR fares are served as USD.' },
    { file: 'web/src/checkout/PaymentStep.tsx', line: 41, severity: 'minor', message: 'useEffect has no cleanup; the timer leaks on unmount.' }
  ];
  var blockReply = 'Two issues found.\n\n```json\n{"findings": [{"file": "booking/src/main/kotlin/FareQuoteService.kt", "line": 88, \u2026}, \u2026]}\n```';
  var blockReplyTail = blockReply + '\n\nI did not review the generated OpenAPI client files.';
  var cutBlock = 'm = re.search(r"```json\\n(.*)\\n```\\s*$", stdout, re.S)   # block must END the reply\nif not m: return            # posts nothing';
  var s503 = {
    id: 'm7-s5-03', who: 'CI job', labels: { loop: 'CI script' }, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'A <b>script</b> posts each finding as an inline comment and needs file, line, severity and message <b>every time</b>.' },
      { id: 'B', label: 'Decider changed', desc: 'The review is posted as one PR comment that <b>people read</b>. Only a consistent layout matters.' }
    ],
    runs: {
      A: [
        { steps: [S('cust', 'Pull request #4127 opens; the review job starts', '', 'PR #4127: cache fare quotes per route'),
            S('loop', 'Job runs claude -p with two sample replies in the prompt', 'Option A. Few-shot examples make the layout more likely, nothing more.', 'claude -p "$REVIEW_PROMPT_WITH_2_EXAMPLES"'),
            S('tool', 'stdout, runs 1 to 18: the block ends the reply', '', blockReply, 'ok'),
            S('tool', 'stdout, run 19: one sentence after the block', 'The examples made this rarer. Plain text still lets it happen.', blockReplyTail, 'warn'),
            S('loop', 'Script cuts out the block', 'The block no longer ends the reply, so the pattern finds nothing.', cutBlock, 'bad'),
            S('cust', 'PR #4127 gets no review comments', 'The cached-currency bug merges unflagged.', '0 inline comments posted', 'bad')],
          outcome: { ok: false, text: 'Examples make the layout likelier, which suits a reader. A script needs a contract: the same fields every run, which only the CLI flags enforce.' }, rate: 0.93 },
        { steps: [S('loop', 'You plan a report_findings tool forced with tool_choice', 'Option B. This is how you would do it on the Messages API.', { tools: [{ name: 'report_findings', input_schema: findingsSchema }], tool_choice: { type: 'tool', name: 'report_findings' } }),
            S('block', 'Blocked: the job runs the Claude Code CLI, not the Messages API', 'claude -p has no flag that takes a tool_choice. Using it means rewriting the job as your own API agent, with its own repo access and MCP wiring.', 'claude -p --tool-choice ...\nerror: unknown option \'--tool-choice\'', 'bad')],
          outcome: { ok: false, text: 'Right pattern, wrong layer. The CLI has its own structured-output flags, so the job does not need to leave the CLI.' }, rate: 0 },
        { steps: [S('cust', 'Pull request #4127 opens; the review job starts', '', 'PR #4127: cache fare quotes per route'),
            S('tool', 'stdout: a sentence after the block', '', blockReplyTail, 'warn'),
            S('loop', 'No block found: rerun with the parse error appended', 'Option C. A second full review, paid again.', 'claude -p "$REVIEW_PROMPT\n\nYour last reply could not be parsed: the JSON block must be last."'),
            X(S('tool', 'stdout of the retry: parses this time', 'In 1 of 20 runs the retry also adds a note, and nothing is posted.', blockReply, 'warn'),
              { table: { head: ['', 'Reviews paid', 'Posted'], rows: [['Clean run', '1', 'yes'], ['Retried run', '2', 'usually'], ['Retry also fails', '2', 'no']] } })],
          outcome: { ok: false, text: 'Retrying recovers some runs but pays for a second review and keeps the fragile text format.' }, rate: 0.9 },
        { steps: [S('cust', 'Pull request #4127 opens; the review job starts', '', 'PR #4127: cache fare quotes per route'),
            S('file', 'findings.schema.json', 'Every finding must have file, line, severity and message.', findingsSchema),
            S('loop', 'Job runs claude -p with JSON output and the schema', 'Option D.', reviewCmd),
            S('tool', 'stdout: a JSON envelope; findings in structured_output', 'Prose can still appear in "result". The script never reads it.', { type: 'result', subtype: 'success', is_error: false, session_id: 'c21e8f40-77b2-4d1a-b0e9-5a3f6d2c8e17', result: 'Two issues found. I did not review the generated client files.', structured_output: { findings: findings } }, 'ok'),
            S('loop', 'Script posts one inline comment per finding', '', 'for f in json.loads(stdout)["structured_output"]["findings"]:\n    gh_review_comment(f["file"], f["line"], f"[{f[\'severity\']}] {f[\'message\']}")', 'ok'),
            S('cust', 'PR #4127 gets two inline comments', '', 'FareQuoteService.kt:88  [major] Currency is dropped when the quote is cached\u2026\nPaymentStep.tsx:41      [minor] useEffect has no cleanup\u2026', 'ok')],
          outcome: { ok: true, text: 'The CLI returns schema-shaped JSON, so a sentence after the findings no longer matters. Every finding carries the four fields the script needs.' }, rate: 1 }
      ],
      B: [
        { steps: [S('cust', 'Pull request #4127 opens; the review job starts', '', 'PR #4127: cache fare quotes per route'),
            S('loop', 'Job runs claude -p with two sample reviews in the prompt', '', 'claude -p "$REVIEW_PROMPT_WITH_2_EXAMPLES"'),
            S('tool', 'stdout: a review in the sample layout', 'The odd extra sentence is fine; people read it.', '## Findings\n- major  FareQuoteService.kt:88  Currency is dropped when the quote is cached.\n- minor  PaymentStep.tsx:41  useEffect has no cleanup.\n\nI did not review the generated client files.', 'ok'),
            S('cust', 'Reviewers read one consistent PR comment', '', 'Posted as a single comment on PR #4127', 'ok')],
          outcome: { ok: true, text: 'When people read the review and only the layout varied, examples give that consistency cheaply. This is the world where the runner-up wins.' }, rate: 0.95 },
        { steps: [S('block', 'Still blocked: tool_choice is not a CLI option', '', 'error: unknown option \'--tool-choice\'', 'bad')],
          outcome: { ok: false, text: 'The job still runs the CLI.' }, rate: 0 },
        { steps: [S('loop', 'Script reruns whenever no JSON block is found', 'People read the comment; there is no block to require.', 'claude -p "$REVIEW_PROMPT\n\nYour last reply could not be parsed\u2026"', 'warn')],
          outcome: { ok: false, text: 'A second paid review to fix a format nobody parses.' }, rate: 0.85 },
        { steps: [S('loop', 'Job runs claude -p with JSON output and the schema', '', reviewCmd),
            S('cust', 'Reviewers get the findings', 'Correct, but the script now has to render JSON into a readable comment.', '{"findings": [{"file": "booking/src/main/kotlin/FareQuoteService.kt", "line": 88, \u2026}]}', 'warn')],
          outcome: { ok: true, warn: true, text: 'Reliable, but more machinery than a human-read comment needs.' }, rate: 1 }
      ]
    }
  };

  /* ============================================================ m7-s4-01 Grep vs Glob for call sites */
  var ask401 = 'Find every place that calls legacy_price_round. We are removing it.';
  var sites = [
    'app/models/invoice_line.rb:42:    legacy_price_round(subtotal * qty)',
    'app/models/price_list.rb:18:    self.amount = legacy_price_round(raw)',
    'app/models/coupon.rb:77:    legacy_price_round(amount * pct / 100.0)',
    'app/services/price_calculator.rb:31:    base = legacy_price_round(plan.monthly)',
    'app/services/price_calculator.rb:58:    legacy_price_round(base - discount)',
    'app/jobs/reprice_subscriptions_job.rb:23:      sub.update!(price: legacy_price_round(p))',
    'app/jobs/legacy_export_job.rb:65:    row[:total] = legacy_price_round(order.total)',
    'app/views/invoices/_line.html.erb:9:  <%= legacy_price_round(line.total) %>',
    'app/views/plans/_card.html.erb:14:  <%= number_to_currency legacy_price_round(plan.monthly) %>',
    'lib/export/csv_row.rb:12:    legacy_price_round(value)'
  ];
  var openStep401 = S('cust', 'Engineer asks', '', ask401);
  var s401 = {
    id: 'm7-s4-01', who: 'Engineer', labels: { loop: 'Claude Code' }, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Calls can be anywhere, and <b>file names give no hint</b> which files call the helper.' },
      { id: 'B', label: 'Decider changed', desc: 'A lint rule allows the helper <b>only in files named <code>*price*.rb</code></b>, and CI enforces it. Names now identify the callers.' }
    ],
    runs: {
      A: [
        { steps: [openStep401,
            S('tool', 'Read lib/pricing/rounding.rb', 'Option A starts at the definition.', { input: { file_path: 'lib/pricing/rounding.rb' }, output: '1  module Pricing\n2    module Rounding\n3      def legacy_price_round(x) = (x * 20).round / 20.0\n\u2026' }),
            S('tool', 'Grep for files that require the module', 'Rails autoloads app/ code, so most callers never write a require line.', { input: { pattern: 'require.*pricing/rounding', output_mode: 'files_with_matches' }, output: ['lib/export/csv_row.rb', 'lib/tasks/reprice.rake'] }, 'warn'),
            S('tool', 'Read both files', 'reprice.rake loads the module but never calls the helper.', { 'lib/export/csv_row.rb': 'line 12: legacy_price_round(value)', 'lib/tasks/reprice.rake': '(no call)' }),
            S('loop', 'Claude reports 1 call site', 'Nine calls in models, jobs and views are missing.', 'Found 1 caller: lib/export/csv_row.rb:12', 'bad')],
          outcome: { ok: false, text: 'Files that load the module are a different set from files that call the helper. Autoloading means most callers have no require line.' }, rate: 0.2 },
        { steps: [openStep401,
            S('tool', 'Bash: run the suite with the helper stubbed to raise', 'Option B. Only code the tests reach can fail.', { input: { command: 'STUB_LEGACY_ROUND=raise bundle exec rspec' }, output: '2,914 examples, 6 failures\n  invoice_line_spec.rb, price_list_spec.rb, coupon_spec.rb,\n  price_calculator_spec.rb (x2), reprice_subscriptions_job_spec.rb' }),
            S('loop', 'Claude reports 6 call sites', 'legacy_export_job.rb, two view partials and csv_row.rb have no tests that reach the call.', 'Found 6 callers (from failing specs)', 'bad')],
          outcome: { ok: false, text: 'Tests find only covered callers. The four untested call sites stay hidden and would break after removal.' }, rate: 0.4 },
        { steps: [openStep401,
            S('loop', 'Claude chooses Grep', 'The target is text inside files: the helper\'s name.', 'Grep searches file contents; names do not matter.'),
            S('tool', 'Grep for the helper name across the repository', 'One call, every directory, with file and line.', { input: { pattern: 'legacy_price_round', output_mode: 'content', '-n': true }, output: sites.concat(['lib/pricing/rounding.rb:3:      def legacy_price_round(x) \u2026   (definition)']) }, 'ok'),
            S('loop', 'Claude reviews each match', '', '10 call sites in 9 files + 1 definition\nmodels 3 \u00b7 services 2 \u00b7 jobs 2 \u00b7 views 2 \u00b7 lib 1'),
            S('cust', 'Engineer gets the full list', '', 'Found 10 callers in models, services, jobs, views and lib (file:line listed).', 'ok')],
          outcome: { ok: true, text: 'Grep searches inside files, so it finds every call wherever it lives, including views and jobs with unrelated names.' }, rate: 1 },
        { steps: [openStep401,
            S('tool', 'Glob **/*price*.rb', 'Option D. Glob matches paths, not contents.', { input: { pattern: '**/*price*.rb' }, output: ['app/models/price_list.rb', 'app/services/price_calculator.rb', 'app/jobs/reprice_subscriptions_job.rb', 'spec/models/price_list_spec.rb'] }, 'warn'),
            S('tool', 'Read each of the four files', '', { found: ['price_list.rb:18', 'price_calculator.rb:31', 'price_calculator.rb:58', 'reprice_subscriptions_job.rb:23'] }),
            S('loop', 'Claude reports 4 call sites', 'invoice_line.rb, coupon.rb, legacy_export_job.rb, csv_row.rb and two .erb views do not have "price" in their names.', 'Found 4 callers', 'bad')],
          outcome: { ok: false, text: 'Glob is right when names identify the files. Here they do not: six of the ten callers have no "price" in their path.' }, rate: 0.3 }
      ],
      B: [
        { steps: [openStep401,
            S('tool', 'Grep for files that require the module', '', { input: { pattern: 'require.*pricing/rounding' }, output: ['lib/tasks/reprice.rake'] }, 'warn'),
            S('loop', 'Claude reports 0 call sites', 'Autoloaded callers still have no require line.', 'Found 0 callers', 'bad')],
          outcome: { ok: false, text: 'Still the wrong set of files.' }, rate: 0.2 },
        { steps: [openStep401,
            S('tool', 'Bash: run the suite with the helper stubbed to raise', '', { output: '2 failures: price_list_spec.rb, price_calculator_spec.rb' }),
            S('loop', 'Claude reports 2 call sites', 'reprice_subscriptions_job.rb is untested.', 'Found 2 callers', 'bad')],
          outcome: { ok: false, text: 'Tests still miss untested callers.' }, rate: 0.5 },
        { steps: [openStep401,
            S('tool', 'Grep for the helper name', '', { input: { pattern: 'legacy_price_round', output_mode: 'content', '-n': true }, output: ['app/models/price_list.rb:18', 'app/services/price_calculator.rb:31', 'app/services/price_calculator.rb:58', 'app/jobs/reprice_subscriptions_job.rb:23', 'lib/pricing/rounding.rb:3 (definition)'] }, 'ok')],
          outcome: { ok: true, text: 'A content search still works.' }, rate: 1 },
        { steps: [openStep401,
            S('file', 'Lint rule enforced in CI', 'This is the changed fact: callers can only live in *price*.rb files.', 'Pricing/LegacyRoundScope:\n  Include: ["**/*price*.rb"]   # legacy_price_round allowed only here'),
            S('tool', 'Glob **/*price*.rb', 'Now the names identify every possible caller.', { input: { pattern: '**/*price*.rb' }, output: ['app/models/price_list.rb', 'app/services/price_calculator.rb', 'app/jobs/reprice_subscriptions_job.rb'] }, 'ok'),
            S('tool', 'Read the three files', '', { found: ['price_list.rb:18', 'price_calculator.rb:31', 'price_calculator.rb:58', 'reprice_subscriptions_job.rb:23'] }),
            S('cust', 'Engineer gets the full list', '', 'Found 4 callers in the 3 files the rule allows.', 'ok')],
          outcome: { ok: true, text: 'When a name pattern defines the set of files, Glob is the right first tool. This is the world where the runner-up wins.' }, rate: 1 }
      ]
    }
  };

  /* ============================================================ m7-s4-03 Edit vs Read + Write */
  var yml = 'config/feature_flags.yml';
  var oldLine = '  streak_freeze_max_per_month: 2';
  var newLine = '  streak_freeze_max_per_month: 3';
  var ask403 = 'Raise streak_freeze_max_per_month to 3 in ' + yml + '.';
  var readMeter = { total: 40000, parts: [{ label: 'System + CLAUDE.md', tokens: 6000, kind: 'sys' }, { label: 'Read: feature_flags.yml (1,240 lines)', tokens: 14000, kind: 'tool' }, { label: 'Write: same 1,240 lines back', tokens: 14000, kind: 'drop' }] };
  var s403 = {
    id: 'm7-s4-03', who: 'Engineer', labels: { loop: 'Claude Code' }, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'The line being changed holds text that <b>appears only once</b> in the file.' },
      { id: 'B', label: 'Decider changed', desc: 'The same full line <b>appears six times</b> (one per region block), and the change must go into the production block only.' }
    ],
    runs: {
      A: [
        { steps: [S('cust', 'Engineer asks', '', ask403),
            S('tool', 'Bash: sed substitution', 'Option A. A shell command, not the editing tool.', { input: { command: 'sed -i \'\' \'s/  streak_freeze_max_per_month: 2/  streak_freeze_max_per_month: 3/\' ' + yml }, output: '(no output, exit 0)' }, 'warn'),
            S('loop', 'Nothing checked the match', 'sed exits 0 whether it changed one line, many, or none. Edit would have refused a missing or ambiguous match.', 'exit 0  \u2192  "done"   # no count of replacements', 'warn'),
            S('cust', 'Reviewer sees a one-line diff this time', '', '-  streak_freeze_max_per_month: 2\n+  streak_freeze_max_per_month: 3')],
          outcome: { ok: true, warn: true, text: 'It works here, but it bypasses the purpose-built Edit tool and its match checks. A typo in the pattern would silently change nothing.' }, rate: 0.9 },
        { steps: [S('cust', 'Engineer asks', '', ask403),
            S('tool', 'Grep finds the line', '', { input: { pattern: 'streak_freeze_max_per_month', '-n': true }, output: [yml + ':612:' + oldLine] }),
            S('tool', 'Edit with old_string "2"', 'Option B matches the value alone.', { input: { file_path: yml, old_string: '2', new_string: '3' } }),
            S('tool', 'Edit refuses', 'The digit 2 appears on 140 lines.', { is_error: true, content: 'Found 140 matches of the string to replace, but replace_all is false. To replace all occurrences, set replace_all to true. To replace only one occurrence, please provide more context to uniquely identify the instance.' }, 'bad')],
          outcome: { ok: false, text: 'The value alone is not unique. The full line is. With replace_all it would change 140 places.' }, rate: 0.3 },
        { steps: [S('cust', 'Engineer asks', '', ask403),
            S('tool', 'Read the whole file', 'Option C. 1,240 lines enter the context to change one.', { input: { file_path: yml }, output: '1  # Feature flags by environment\n\u2026\n612  streak_freeze_max_per_month: 2\n\u2026\n1240  leaderboard_v2: false' }),
            X(S('tool', 'Write the full file back', 'Formatting is kept this time, but the tool call carries the entire file.', { input: { file_path: yml, content: '# Feature flags by environment\n\u2026 (1,240 lines) \u2026' }, output: 'File written' }, 'warn'),
              { meter: readMeter }),
            S('cust', 'Reviewer opens the change', 'The change was one line. The text was unique, so Edit could have made only that change.', 'Write ' + yml + ': whole file replaced (1,240 lines)\nReviewer must confirm that 1,239 lines did not change.', 'warn')],
          outcome: { ok: true, warn: true, text: 'Read plus Write is the fallback when the match text is not unique. Here it is unique, so a full rewrite only adds review work and risk.' }, rate: 0.95 },
        { steps: [S('cust', 'Engineer asks', '', ask403),
            S('tool', 'Edit with the full line as old_string', 'Option D. The full line appears once, so the match is unique.', { input: { file_path: yml, old_string: oldLine, new_string: newLine } }, 'ok'),
            S('tool', 'Edit succeeds', 'Only the matched text changes; the rest of the file is untouched.', 'The file ' + yml + ' has been updated.'),
            S('cust', 'Reviewer sees a one-line diff', '', '@@ -612 +612 @@\n-  streak_freeze_max_per_month: 2\n+  streak_freeze_max_per_month: 3', 'ok')],
          outcome: { ok: true, text: 'Edit makes the targeted change through a unique text match. Reviewers check one line, and nothing else can be reformatted.' }, rate: 1 }
      ],
      B: [
        { steps: [S('tool', 'Bash: sed substitution', '', { input: { command: 'sed -i \'\' \'s/' + oldLine + '/' + newLine + '/\' ' + yml }, output: '(exit 0)' }),
            S('cust', 'Reviewer sees six lines changed', 'Every region changed, not just production.', '6 lines changed', 'bad')],
          outcome: { ok: false, text: 'sed replaces every match, silently.' }, rate: 0.3 },
        { steps: [S('tool', 'Edit with old_string "2"', '', { input: { old_string: '2', new_string: '3' } }),
            S('tool', 'Edit refuses', '', { is_error: true, content: 'Found 140 matches of the string to replace, but replace_all is false.' }, 'bad')],
          outcome: { ok: false, text: 'The value is still not unique.' }, rate: 0.2 },
        { steps: [S('cust', 'Engineer asks', '', 'Raise streak_freeze_max_per_month to 3 for production only.'),
            S('tool', 'Read the whole file', 'Claude finds the production block among the six.', { input: { file_path: yml }, output: '\u2026\n980  production:\n\u2026\n1012  streak_freeze_max_per_month: 2\n\u2026' }),
            S('tool', 'Write the file back with that one value changed', 'Formatting kept.', { input: { file_path: yml, content: '\u2026 (1,240 lines) \u2026' }, output: 'File written' }, 'ok'),
            S('cust', 'Reviewer sees the effective diff', '', '@@ -1012 +1012 @@\n-  streak_freeze_max_per_month: 2\n+  streak_freeze_max_per_month: 3', 'ok')],
          outcome: { ok: true, text: 'When the match text is not unique, Read plus Write is the fallback. This is the world where the runner-up wins.' }, rate: 0.95 },
        { steps: [S('tool', 'Edit with the full line as old_string', '', { input: { file_path: yml, old_string: oldLine, new_string: newLine } }),
            S('tool', 'Edit refuses', 'The full line now appears in six region blocks.', { is_error: true, content: 'Found 6 matches of the string to replace, but replace_all is false. To replace only one occurrence, please provide more context to uniquely identify the instance.' }, 'bad')],
          outcome: { ok: false, text: 'Edit needs a unique match; this line is not unique any more.' }, rate: 0.4 }
      ]
    }
  };

  /* ============================================================ m7-s5-04 MCP resource catalog vs better description */
  var SD = 'mcp__guidelines__search_docs';
  var listTools = { 'tools/list': [{ name: 'search_docs', description: 'Search the API guideline documents.' }, { name: 'search_code', description: 'Search the repository.' }], 'resources/list': [] };
  var probes = [
    { q: 'api guidelines', hits: 0 }, { q: 'rules', hits: 0 }, { q: 'rest', hits: 2 }, { q: 'standards', hits: 0 }, { q: 'versioning', hits: 1 },
    { q: 'endpoint', hits: 0 }, { q: 'style guide', hits: 0 }, { q: 'errors', hits: 1 }, { q: 'conventions', hits: 0 }, { q: 'overview', hits: 0 },
    { q: 'list documents', hits: 0 }, { q: 'table of contents', hits: 0 }, { q: 'kotlin api', hits: 0 }, { q: 'typescript api', hits: 0 }];
  var catalog = { uri: 'guidelines://catalog', mimeType: 'application/json', contents: [
    { id: 'API-01', title: 'Naming', sections: ['1.1 Resource names', '1.2 Query parameters'] },
    { id: 'API-02', title: 'Versioning', sections: ['2.1 URL version', '2.2 Deprecation headers'] },
    { id: 'API-03', title: 'Pagination', sections: ['3.1 Cursor pagination', '3.2 Page size limits'] },
    { id: 'API-04', title: 'Errors', sections: ['4.1 Problem+JSON body', '4.2 Retryable codes'] },
    { id: 'API-05', title: 'Idempotency', sections: ['5.1 Idempotency-Key header'] }] };
  var diff504 = 'PR #4133 adds GET /v2/bookings?page=3 and returns {"error": "not found"} on 404.';
  function probeStep(n, mark, note) {
    return S('tool', n + ' search_docs calls before the review starts', note, { calls: probes.slice(0, n).map(function (p) { return SD + '("' + p.q + '") \u2192 ' + p.hits + ' hits'; }) }, mark);
  }
  var s504 = {
    id: 'm7-s5-04', who: 'CI job', labels: { loop: 'Claude Code' }, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'The calls are an attempt to <b>learn which guideline documents exist</b> and how they are organised. The tool itself is used correctly.' },
      { id: 'B', label: 'Decider changed', desc: 'The reviewer already knows the documents. Calls fail because it <b>misuses the tool</b>: it pastes whole diff hunks as the query.' }
    ],
    runs: {
      A: [
        { steps: [S('cust', 'Review job starts on a PR', '', diff504),
            res('Reviewer delegates doc lookup to an Explore subagent', 'Option A.', [U('toolu_41', 'Task', { subagent_type: 'Explore', prompt: 'Find which API guidelines apply to pagination and error bodies.' })], 'tool_use'),
            S('sub', 'Subagent probes blindly, out of sight', 'It has the same tool and the same missing map.', { calls: 14, empty: 11, examples: ['search_docs("api guidelines") \u2192 0', 'search_docs("rules") \u2192 0', '\u2026'] }, 'bad'),
            S('sub', 'Subagent returns a short summary', 'The main context stays small. The call count does not change.', 'Found guidance on versioning and errors. Pagination guidance not found.'),
            S('cust', 'Review posted', 'The pagination rule was never found.', '1 comment (errors). Cursor pagination rule API-03 missed.', 'warn')],
          outcome: { ok: false, text: 'A subagent hides verbose output from the main context, but it makes the same 14 blind calls. The calls were the problem.' }, rate: 0.4 },
        { steps: [S('cust', 'Review job starts on a PR', '', diff504),
            S('loop', 'Client lists what the MCP server offers', 'Option B adds a resource next to the tools.', { 'tools/list': ['search_docs', 'search_code'], 'resources/list': [{ uri: 'guidelines://catalog', name: 'API guideline catalog', description: 'Titles and section outline of every API guideline.' }] }),
            S('ctx', 'Catalog read at the start of the run', 'The reviewer now knows what exists without asking.', catalog, 'ok'),
            res('Reviewer makes two targeted calls', 'It knows the diff touches pagination and error bodies, and which sections cover them.', [U('toolu_42', 'search_docs', { query: 'cursor pagination page size' }), U('toolu_43', 'search_docs', { query: 'problem+json error body' })], 'tool_use'),
            X(S('tool', 'Both calls return the right sections', '', { 'API-03 3.1': 'List endpoints must use cursor pagination, not page numbers.', 'API-04 4.1': 'Errors use application/problem+json with type, title, status.' }, 'ok'),
              { table: { head: ['', 'search_docs calls', 'Empty'], rows: [['Before', '14', '11'], ['With catalog resource', '2', '0']] } }),
            S('cust', 'Review posted', '', '2 comments: use cursor pagination (API-03 3.1); use problem+json (API-04 4.1).', 'ok')],
          outcome: { ok: true, text: 'A resource exposes the catalog directly. The reviewer stops probing to learn what exists and searches only for what it needs.' }, rate: 1 },
        { steps: [S('cust', 'Review job starts on a PR', '', diff504),
            S('loop', 'Client lists the tools: richer description, still no catalog', 'Option C. The label is better. It still does not say which documents exist.', { 'tools/list': [{ name: 'search_docs', description: 'Searches the API guideline docs. Input: 2 to 5 keywords. Covers naming, versioning, errors and more. Example: "pagination limits".' }], 'resources/list': [] }),
            probeStep(9, 'warn', 'Fewer calls, same purpose: Claude is still asking "what is in here?". The tool was never being misused.'),
            S('cust', 'Review posted', '', '1 comment (errors). Pagination rule found on the 9th call, after 6 empty ones.', 'warn')],
          outcome: { ok: false, text: 'A better description fixes wrong or vague tool use. Here the tool was used correctly; what was missing is a map of the content.' }, rate: 0.6 },
        { steps: [S('cust', 'Review job starts on a PR', '', diff504),
            S('loop', 'Client lists five area tools', 'Option D.', { 'tools/list': ['search_naming_docs', 'search_versioning_docs', 'search_pagination_docs', 'search_errors_docs', 'search_misc_docs'], 'resources/list': [] }),
            S('tool', '12 calls: each area probed with broad queries', 'More tools to probe still do not say what exists inside each area.', { calls: ['search_naming_docs("overview") \u2192 0', 'search_misc_docs("list") \u2192 0', '\u2026 10 more, 8 empty'] }, 'bad')],
          outcome: { ok: false, text: 'Splitting helps choose between overlapping tools. It does not show which documents exist, so the probing continues.' }, rate: 0.4 }
      ],
      B: [
        { steps: [S('sub', 'Explore subagent sends diff hunks as queries', '', { calls: ['search_docs("@@ -40,6 +40,18 @@ fun listBookings(page: Int) \u2026") \u2192 0'] }, 'bad')],
          outcome: { ok: false, text: 'The misuse just moves into the subagent.' }, rate: 0.4 },
        { steps: [S('ctx', 'Catalog read at the start', 'The reviewer already knew these titles.', { contents: ['API-01 Naming', 'API-02 Versioning', 'API-03 Pagination', '\u2026'] }),
            S('tool', 'Reviewer still pastes diff hunks as queries', '', { calls: ['search_docs("@@ -40,6 +40,18 @@ \u2026 150 lines") \u2192 0'] }, 'bad')],
          outcome: { ok: false, text: 'A catalog does not teach the tool\'s input format.' }, rate: 0.4 },
        { steps: [S('cust', 'Review job starts on a PR', '', diff504),
            S('loop', 'Client lists the tool with its new description', 'The description now states the input format and gives examples.', { name: 'search_docs', description: 'Searches API guideline docs by keyword. Input: 2 to 5 keywords, never code. Examples: "cursor pagination", "problem+json errors".' }, 'ok'),
            res('Reviewer sends keyword queries', '', [U('toolu_44', 'search_docs', { query: 'cursor pagination' }), U('toolu_45', 'search_docs', { query: 'problem+json errors' })], 'tool_use'),
            S('tool', 'Both calls hit', '', { 'API-03 3.1': 'Use cursor pagination.', 'API-04 4.1': 'Use problem+json.' }, 'ok')],
          outcome: { ok: true, text: 'When the tool is misused, a fuller description with input format and examples fixes it. This is the world where the runner-up wins.' }, rate: 0.95 },
        { steps: [S('tool', 'Each area tool still gets diff hunks', '', { calls: ['search_pagination_docs("@@ -40,6 \u2026") \u2192 0'] }, 'bad')],
          outcome: { ok: false, text: 'Splitting does not fix the query format.' }, rate: 0.4 }
      ]
    }
  };

  /* ============================================================ m7-s5-05 MCP tool description vs built-in Grep */
  var FU = 'mcp__codesearch__find_usages';
  var ask505 = 'PR #4140 changes FareRules.applyFare(quote) to applyFare(quote, currency). Review it.';
  var grepOut = ['booking/src/main/kotlin/QuoteController.kt:57:  fareRules.applyFare(q)', 'booking/src/main/kotlin/RefundService.kt:112:  fareRules.applyFare(original)', 'web/src/api/fares.ts:23:  // mirrors applyFare'];
  var fuOut = { callers: ['QuoteController.kt:57 (direct)', 'RefundService.kt:112 (direct)', 'BundleFareRule.kt:31 (via FareRule interface: rule.apply)', 'GroupFareRule.kt:44 (via FareRule interface: rule.apply)', 'FareRulesTest.kt:19 (direct)'] };
  var thinList = [{ name: 'Grep', description: 'A powerful search tool built on ripgrep. Supports full regex syntax\u2026 (about 40 lines)' }, { name: FU, description: 'Find usages.' }];
  var fullDesc = 'Resolves every caller of a Kotlin or TypeScript function across modules, including calls through interfaces and overrides, which text search misses. Input: fully qualified name, e.g. "FareRules.applyFare". Use this instead of Grep when you need the callers of a function or method; use Grep for plain text.';
  var missedReview = 'Signature change is safe: both callers (QuoteController, RefundService) are updated.';
  var goodReview = 'Blocker: BundleFareRule.kt:31 and GroupFareRule.kt:44 call applyFare through the FareRule interface and are not updated.';
  var s505 = {
    id: 'm7-s5-05', who: 'CI job', labels: { loop: 'Claude Code' }, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'The MCP tool\'s description reads only <b>"Find usages."</b> The tool works when called.' },
      { id: 'B', label: 'Decider changed', desc: 'The description <b>already explains</b> interface resolution and when to prefer it over Grep. Grep is still chosen in some reviews.' }
    ],
    runs: {
      A: [
        { steps: [S('cust', 'Review job starts', '', ask505),
            S('file', 'CLAUDE.md gains a rule', 'Option A. The description is still two words.', '## Code search\nFor callers of a function, use find_usages, not Grep.'),
            S('loop', 'Claude sees the tool list', 'Grep: 40 lines on what it does well. find_usages: "Find usages." The rule competes with that signal.', { tools: thinList }),
            S('tool', 'Most runs: find_usages is called and finds all 5 callers', '', { input: { symbol: 'FareRules.applyFare' }, output: fuOut }),
            S('tool', 'Run 4 of 20: deep into a long review, Claude greps', 'Nothing in the tool\'s own description says why it beats Grep here.', { tool: 'Grep', input: { pattern: 'applyFare', '-n': true }, output: grepOut }, 'warn'),
            S('cust', 'Review on that run', 'The interface calls are missed.', missedReview, 'bad')],
          outcome: { ok: false, text: 'A project rule is a reasonable second nudge. The primary signal Claude reads when it picks a tool is the description, and here it is two words.' }, rate: 0.85 },
        { steps: [S('cust', 'Review job starts', '', ask505),
            S('hook', 'PreToolUse hook on Grep', 'Option B guesses which patterns are symbol names.', 'if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", pattern):\n    deny("Use find_usages for symbols")'),
            S('tool', 'Grep "applyFare" is redirected; find_usages finds all 5', '', { output: fuOut }, 'ok'),
            S('tool', 'Grep "FARE_CACHE_TTL" (a key in application.yml) is denied too', 'A real text search, wrongly hijacked. find_usages only knows code symbols.', { hook: 'deny', then: FU + '("FARE_CACHE_TTL") \u2192 0 callers' }, 'bad'),
            S('cust', 'Review', 'The config check is skipped.', 'Could not find where FARE_CACHE_TTL is set.', 'warn')],
          outcome: { ok: false, text: 'Deterministic but brittle: deciding which Grep patterns are symbol lookups is guesswork, and it blocks legitimate text searches.' }, rate: 0.7 },
        { steps: [S('cust', 'Review job starts', '', ask505),
            S('loop', 'Claude sees the rewritten description', 'Option C. Now the tool says what it resolves and when to prefer it.', { tools: [{ name: 'Grep', description: 'A powerful search tool built on ripgrep\u2026' }, { name: FU, description: fullDesc }] }, 'ok'),
            res('Claude picks find_usages for the callers question', 'The description matches the job exactly.', [U('toolu_51', FU, { symbol: 'FareRules.applyFare' })], 'tool_use'),
            S('tool', 'find_usages returns all callers, including interface calls', '', { output: fuOut }, 'ok'),
            S('cust', 'Review posted', '', goodReview, 'ok')],
          outcome: { ok: true, text: 'Descriptions are how Claude picks tools. Once this one says what it finds that Grep misses, Claude has a reason to choose it.' }, rate: 0.95 },
        { steps: [S('cust', 'Review job starts', '', ask505),
            S('loop', 'Claude sees the renamed tool', 'Option D. Better name, same two-word description.', { tools: [{ name: 'Grep', description: 'A powerful search tool built on ripgrep\u2026' }, { name: 'mcp__codesearch__find_all_callers', description: 'Find usages.' }] }),
            S('tool', 'Claude still runs Grep on many reviews', 'The name cannot say that it resolves interface calls or what input it takes.', { tool: 'Grep', input: { pattern: 'applyFare' }, output: grepOut }, 'warn'),
            S('cust', 'Review', '', missedReview, 'bad')],
          outcome: { ok: false, text: 'A name helps a little. It cannot carry interface coverage, inputs or when to prefer the tool; the description is still two words.' }, rate: 0.75 }
      ],
      B: [
        { steps: [S('cust', 'Review job starts', '', ask505),
            S('loop', 'The description is already full', 'This is the changed fact.', { name: FU, description: fullDesc }),
            S('file', 'CLAUDE.md gains a rule', 'The next lever once the description is done.', '## Code search\nFor callers of a function, use find_usages, not Grep.', 'ok'),
            S('tool', 'find_usages is called and finds all 5 callers', '', { output: fuOut }, 'ok'),
            S('cust', 'Review posted', '', goodReview, 'ok')],
          outcome: { ok: true, text: 'With the description already full, a project instruction is the next nudge, and it closes the gap. This is the world where the runner-up wins.' }, rate: 0.95 },
        { steps: [S('hook', 'PreToolUse redirect on Grep', '', 'deny symbol-like patterns'), S('tool', 'Grep "FARE_CACHE_TTL" denied', '', { hook: 'deny' }, 'bad')],
          outcome: { ok: false, text: 'Still guesswork that blocks real text searches.' }, rate: 0.7 },
        { steps: [S('loop', 'Description rewritten again', 'It already said all of this. Nothing new for Claude to read.', { name: FU, description: fullDesc + ' (reworded)' }),
            S('tool', 'Grep is still chosen in 4 of 20 reviews', '', { tool: 'Grep', input: { pattern: 'applyFare' } }, 'warn')],
          outcome: { ok: false, text: 'The first lever is already used; rewriting it again changes nothing.' }, rate: 0.8 },
        { steps: [S('loop', 'Tool renamed', '', { name: 'mcp__codesearch__find_all_callers', description: fullDesc }),
            S('tool', 'Grep is still chosen in some reviews', '', { tool: 'Grep' }, 'warn')],
          outcome: { ok: false, text: 'A rename adds nothing the full description does not already say.' }, rate: 0.8 }
      ]
    }
  };

  /* ============================================================ m7-s5-08 batch + trim (select 2) */
  var batchReq = { requests: [
    { custom_id: 'services--payments-gateway', params: { model: L.MODEL, max_tokens: 1024, messages: [{ role: 'user', content: 'Rate dependency risk.\n<build.gradle.kts>\u2026</build.gradle.kts>\n<gradle.lockfile>\u2026</gradle.lockfile>' }] } },
    { custom_id: 'web--checkout', params: { model: L.MODEL, max_tokens: 1024, messages: ['\u2026package.json + package-lock.json\u2026'] } },
    '\u2026 118 more, one per module' ] };
  var costTable = { head: ['Setup', 'Input tokens / week', 'Price', 'Cost / week', 'Ready by'],
    rows: [['Sync, whole tree (today)', '18.0 M', 'full', '$54.00', 'Sun 01:00'],
           ['Batch, whole tree', '18.0 M', '50% off', '$27.00', 'within 24 h'],
           ['Sync, manifests only', '0.72 M', 'full', '$2.16', 'Sun 00:20'],
           ['Batch + manifests only', '0.72 M', '50% off', '$1.08', 'within 24 h']] };
  var costNote = 'Illustrative: 120 modules, $3 per million input tokens.';
  var trimMeter = { total: 160000, parts: [{ label: 'Prompt', tokens: 1000, kind: 'sys' }, { label: 'build.gradle.kts + gradle.lockfile', tokens: 5000, kind: 'keep' }] };
  var fullMeter = { total: 160000, parts: [{ label: 'Prompt', tokens: 1000, kind: 'sys' }, { label: 'build.gradle.kts + gradle.lockfile', tokens: 5000, kind: 'keep' }, { label: 'Application source (never used)', tokens: 144000, kind: 'drop' }] };
  var advisory = 'Thursday: CVE-2026-41877 published for okhttp 4.9.1 (used by services/payments-gateway).';
  var s508 = {
    id: 'm7-s5-08', who: 'CI job', labels: { loop: 'CI script' }, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Nobody reads the report until Monday; it reads only manifests; it <b>must rate every module every week</b>.' },
      { id: 'B', label: 'Decider changed', desc: 'Policy changes: <b>unchanged modules may keep last week\'s rating</b> (a separate advisory alert job covers new CVEs).' }
    ],
    runs: {
      A: [
        { steps: [S('loop', 'Script skips modules whose manifests did not change', 'Option A.', 'changed = [m for m in modules if sha(m.manifests) != last_week[m]]\n# 23 of 120 modules sent'),
            S('cust', 'Meanwhile', 'A new advisory can hit a lockfile that did not change.', advisory, 'warn'),
            S('loop', 'payments-gateway is skipped', 'Its lockfile is unchanged, so last week\'s rating is copied.', { module: 'services/payments-gateway', sent: false, rating: 'low (from last week)' }, 'bad'),
            S('cust', 'Monday report', 'Only 23 modules were rated this week, and the one with a new CVE shows "low".', 'payments-gateway: LOW  (not re-rated)', 'bad')],
          outcome: { ok: false, text: 'Skipping is a real saving, but the report must rate every module every week. A new advisory can make an unchanged lockfile risky.' }, rate: 0.6 },
        { steps: [S('loop', 'Saturday 22:00: script submits one batch', 'Option B. One request per module; custom_id allows letters, digits, - and _, so the path services/payments-gateway is written services--payments-gateway.', batchReq, 'ok'),
            S('api', 'Batch accepted', 'No latency promise; results come within 24 hours. Nobody needs them before Monday.', { id: 'msgbatch_01Hq7Wd3', processing_status: 'in_progress', request_counts: { processing: 120, succeeded: 0, errored: 0 } }),
            S('api', 'Sunday 03:40: batch ended', '', { processing_status: 'ended', request_counts: { processing: 0, succeeded: 120, errored: 0 } }),
            S('loop', 'Script matches each result to its module by custom_id', 'Results can come back in any order.', { custom_id: 'services--payments-gateway', result: { type: 'succeeded', message: { content: [T('HIGH: okhttp 4.9.1 affected by CVE-2026-41877. Upgrade to 4.12.0.')] } } }),
            X(S('cust', 'Monday report: all 120 modules rated', costNote + ' With trimming (option D) the two savings stack.', '120 / 120 rated \u00b7 payments-gateway: HIGH', 'ok'), { table: costTable })],
          outcome: { ok: true, text: 'Nobody waits on the results, so the 50% batch discount costs nothing in practice, and custom_id matches each result to its module. Coverage is untouched.' }, rate: 1 },
        { steps: [S('loop', 'Script merges modules into 8 product-area requests', 'Option C. Fifteen modules per request.', { requests: 8, modules_per_request: 15 }),
            res('Claude rates fifteen modules in one answer', 'Attention is spread thin: short ratings, one module left out.', [T('payments-gateway: medium. payments-ledger: medium. payments-fx: medium. \u2026 (loyalty-points not mentioned)')], 'end_turn', 'warn'),
            S('cust', 'Monday report', '', '119 / 120 rated \u00b7 several ratings copied across neighbours', 'bad')],
          outcome: { ok: false, text: 'Fewer, bigger requests lower the quality of each rating and can drop modules.' }, rate: 0.5 },
        { steps: [X(S('ctx', 'Before: one request per module', 'Most of each request is source the report never reads.', '150,000 tokens per module'), { meter: fullMeter }),
            X(S('loop', 'Script sends only the build file and lockfile', 'Option D. Same 120 requests, about 6,000 tokens each.', { custom_id: 'services--payments-gateway', input: ['build.gradle.kts', 'gradle.lockfile'] }, 'ok'), { meter: trimMeter }),
            res('Claude rates the module from its manifests', 'The rating used only these files anyway.', [T('HIGH: okhttp 4.9.1 affected by CVE-2026-41877. Upgrade to 4.12.0.')], 'end_turn'),
            X(S('cust', 'Monday report: all 120 modules rated', costNote + ' With batching (option B) the two savings stack.', '120 / 120 rated \u00b7 payments-gateway: HIGH', 'ok'), { table: costTable })],
          outcome: { ok: true, text: 'Trimming input to what the task reads cuts about 96% of the tokens and loses nothing the report uses. Every module is still rated.' }, rate: 1 }
      ],
      B: [
        { steps: [S('loop', 'Script skips modules whose manifests did not change', 'Allowed in this world.', '23 of 120 modules sent; 97 keep last week\'s rating'),
            S('cust', 'Advisory alert job flags payments-gateway separately', 'New CVEs no longer depend on this report.', advisory),
            S('cust', 'Monday report', 'All 120 have a valid rating; only changed modules were paid for.', '120 / 120 have a current rating (23 re-rated)', 'ok')],
          outcome: { ok: true, text: 'When unchanged modules may keep last week\'s rating, skipping them is a valid saving too. This is the world where the runner-up wins.' }, rate: 1 },
        { steps: [S('loop', 'Batch submission', '', { requests: 120 }), S('cust', 'Monday report', '', '120 / 120 rated', 'ok')],
          outcome: { ok: true, text: 'Batching still halves the price.' }, rate: 1 },
        { steps: [res('Fifteen modules per request', '', [T('\u2026 loyalty-points not mentioned')], 'end_turn', 'warn')],
          outcome: { ok: false, text: 'Merging still spreads attention thin.' }, rate: 0.5 },
        { steps: [S('loop', 'Manifests only', '', { input: ['build.gradle.kts', 'gradle.lockfile'] }), S('cust', 'Monday report', '', '120 / 120 rated', 'ok')],
          outcome: { ok: true, text: 'Trimming still cuts tokens.' }, rate: 1 }
      ]
    }
  };

  /* ============================================================ m7-s6-05 batch for 40,000 re-extractions */
  var rec = { name: 'record_certificate', input_schema: { type: 'object', required: ['insured_name', 'carrier', 'policy_number', 'coverage_lines', 'effective_date', 'expiry_date'] } };
  var batchCost = { head: ['Approach', 'Price', 'Cost (40,000 docs)', 'Done in', 'Live pipeline'],
    rows: [['Message Batches', '50% off', '$660', '< 24 h per batch', 'untouched'],
           ['Parallel subagents', 'full', '$1,320', '~9 h', 'shares rate limits'],
           ['Live pipeline, nightly chunks', 'full', '$1,320', '10 nights', 'shares capacity']] };
  var batchNote = 'Illustrative prices: about 6,000 input and 500 output tokens per certificate.';
  var s605 = {
    id: 'm7-s6-05', who: 'Pipeline', labels: { loop: 'Pipeline code' }, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Results are due <b>at the end of next week</b>; each document needs <b>one call and no other tools</b>.' },
      { id: 'B', label: 'Decider changed', desc: 'A carrier audit needs all 40,000 re-extracted <b>by 08:00 tomorrow</b>, about 10 hours away.' }
    ],
    runs: {
      A: [
        { steps: [S('loop', 'Batch requests ask Claude to fetch each PDF with a tool', 'Option A. The PDF is not in the request.', { custom_id: 'COI-2025-018834', params: { tools: [{ name: 'fetch_pdf' }, rec], messages: [{ role: 'user', content: 'Fetch certificate COI-2025-018834 and extract it.' }] } }),
            S('api', 'Batch ends; each result stops at the fetch request', 'A batch request is a single Messages call. Nobody can send the tool_result back inside the batch.', { custom_id: 'COI-2025-018834', result: { type: 'succeeded', message: { content: [U('toolu_61', 'fetch_pdf', { id: 'COI-2025-018834' })], stop_reason: 'tool_use' } } }, 'bad'),
            S('cust', 'Nothing extracted', 'The document needed no tool anyway; it could have been in the request.', '40,000 results, 0 extractions', 'bad')],
          outcome: { ok: false, text: 'Batch is the right channel, but the Batches API does not run multi-turn tool calls, and this job needs no fetch tool.' }, rate: 0 },
        { steps: [S('loop', 'Build one request per certificate, ID as custom_id', 'Option B. The PDF goes in the request; the extraction tool is forced, so one call returns the record.', { custom_id: 'COI-2025-018834', params: { tools: [rec], tool_choice: { type: 'tool', name: 'record_certificate' }, messages: [{ role: 'user', content: [{ type: 'document', source: { type: 'base64', media_type: 'application/pdf', data: '\u2026' } }] }] } }),
            S('api', 'Submit the archive as 20 batches of 2,000', 'Splitting keeps each batch well under the size limit.', { batches: 20, requests_each: 2000, processing_status: 'in_progress' }),
            S('api', 'Batches end within 24 hours; results by custom_id', 'The live pipeline keeps serving brokers at its normal price and speed.', { custom_id: 'COI-2025-018834', result: { type: 'succeeded', message: { content: [U('toolu_62', 'record_certificate', { insured_name: 'Harbor Freight Lines LLC', carrier: 'Northwall Mutual', policy_number: 'NM-GL-448120' })], stop_reason: 'tool_use' } } }, 'ok'),
            S('loop', 'Pydantic validates; 312 failures resubmitted by custom_id', 'Only the failures are sent again.', { validated: 39688, resubmitted: 312, second_pass_ok: 312 }),
            X(S('cust', 'All 40,000 re-extracted by Wednesday', batchNote, '40,000 / 40,000 posted, 6 days before the deadline', 'ok'), { table: batchCost })],
          outcome: { ok: true, text: 'Single-call requests with a week of slack are a textbook batch fit: half the price, and custom_id maps each result back to its certificate.' }, rate: 1 },
        { steps: [S('loop', 'Coordinator spawns extraction subagents, 8 per response', 'Option C. Real-time calls at full price.', [U('toolu_63', 'Task', { prompt: 'Extract COI-2025-018834' }), U('toolu_64', 'Task', { prompt: 'Extract COI-2025-018835' }), '\u2026 6 more']),
            S('sub', 'Subagents work through the archive', 'They share the account\'s rate limits with the live pipeline.', { done: '40,000 in ~9 hours', live_pipeline_p95: '4 s \u2192 11 s during the run' }, 'warn'),
            X(S('cust', 'Results ready next morning, a week early', 'The deadline was a week away. Speed bought nothing and cost twice the batch price.', '40,000 / 40,000 posted', 'warn'), { table: batchCost })],
          outcome: { ok: true, warn: true, text: 'Parallel subagents are right when someone is waiting. With the deadline a week away, the speed is unused and the cost is full price.' }, rate: 0.97 },
        { steps: [S('loop', 'Feed 4,000 archived certificates into the live pipeline each night', 'Option D. Failures resubmitted by document ID.', { nightly: 4000, nights: 10 }),
            X(S('cust', 'Done on night 10', 'Tidy, on time, and every call at real-time price.', '40,000 / 40,000 posted', 'warn'), { table: batchCost })],
          outcome: { ok: true, warn: true, text: 'Sensible chunking and targeted resubmits, but full real-time price for work with days of slack.' }, rate: 0.95 }
      ],
      B: [
        { steps: [S('api', 'Batch results stop at fetch_pdf', '', { stop_reason: 'tool_use' }, 'bad')],
          outcome: { ok: false, text: 'Still no multi-turn tool calls in a batch.' }, rate: 0 },
        { steps: [S('api', 'Submit 20 batches', '', { batches: 20, processing_status: 'in_progress' }),
            S('api', '08:00: 14 of 20 batches ended', 'Batches promise results within 24 hours, not within 10.', { ended: 14, in_progress: 6 }, 'bad'),
            S('cust', 'Audit starts without 12,000 certificates', '', '28,000 / 40,000 ready', 'bad')],
          outcome: { ok: false, text: 'The Batches API has no latency guarantee. A hard deadline in hours rules it out.' }, rate: 0.5 },
        { steps: [S('loop', 'Coordinator spawns extraction subagents, 8 per response', '', [U('toolu_63', 'Task', { prompt: 'Extract COI-2025-018834' }), '\u2026']),
            S('sub', 'Subagents finish the archive overnight', 'Full price, but this world needs the speed.', { done: '40,000 in ~9 hours' }, 'ok'),
            S('cust', 'All 40,000 ready at 07:10', '', '40,000 / 40,000 posted before the audit', 'ok')],
          outcome: { ok: true, text: 'When results are needed within hours, parallel real-time work is worth full price. This is the world where the runner-up wins.' }, rate: 0.95 },
        { steps: [S('loop', '4,000 per night through the live pipeline', '', { nights: 10 }), S('cust', 'Audit starts with 4,000 done', '', '4,000 / 40,000', 'bad')],
          outcome: { ok: false, text: 'Ten nights do not fit in ten hours.' }, rate: 0.1 }
      ]
    }
  };

  [s206, s503, s401, s403, s504, s505, s508, s605].forEach(L.add);
})();
