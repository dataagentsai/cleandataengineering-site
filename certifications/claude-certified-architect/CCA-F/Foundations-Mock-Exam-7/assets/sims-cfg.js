/* CCA-F Mock Exam #7 - scripted simulations for the Claude Code configuration questions:
   m7-s2-01, m7-s2-02, m7-s2-04, m7-s2-05, m7-s4-06, m7-s4-07, m7-s5-01, m7-s5-02.
   Engine: "config loader". Which files exist, who has them, and what ends up in Claude's context
   for this person, this file, this CI run. Same shape as sims.js: two worlds, one trace per option. */
(function () {
  var L = window.SIMLIB, S = L.S, X = L.X;
  var LBL = { loop: 'Claude Code' };

  /* file step: path + scope in the title */
  function F(path, scope, body, note, mark) { return S('file', path + '  \u00b7  ' + scope, note, body, mark); }
  /* Claude Code step */
  function C(title, note, payload, mark) { return S('loop', title, note, payload, mark); }
  /* person step */
  function P(title, note, payload, mark) { return S('cust', title, note, payload, mark); }
  /* context step with a meter. parts: [label, tokens, kind] */
  function M(title, note, parts, mark, total) {
    var ps = parts.map(function (p) { return { label: p[0], tokens: p[1], kind: p[2] }; });
    var list = ps.filter(function (p) { return p.tokens > 0 && p.kind !== 'drop'; }).map(function (p) { return '\u2713 ' + p.label; })
      .concat(ps.filter(function (p) { return p.kind === 'drop'; }).map(function (p) { return (p.tokens > 0 ? '\u26a0 ' : '\u2717 ') + p.label; }));
    return X(S('ctx', title, note, list.join('\n'), mark), { meter: { total: total || 8000, parts: ps } });
  }
  function TB(title, note, head, rows, mark) { return X(S('cust', title, note, 'See the table.', mark), { table: { head: head, rows: rows } }); }

  /* ------------------------------------------------------------ m7-s2-01 personal vs project command */
  var standupMine = '---\ndescription: Summarise my commits since yesterday\n---\nRun git log --author="$(git config user.email)" --since=yesterday.\nRead ~/notes/standup.md for blockers.\nWrite three lines: Yesterday / Today / Blockers.';
  var standupTeam = '---\ndescription: Team standup from git log\n---\nRun git log --author="$(git config user.email)" --since=yesterday.\nWrite three lines: Yesterday / Today / Blockers.';
  var menuTeam = '/new-endpoint  (project)\n/gen-tests     (project)';
  var head01 = ['Who', 'Repository', '/standup listed?', 'Wanted?'];

  var s201 = {
    id: 'm7-s2-01', who: 'Engineer', labels: LBL, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'The command is <b>personal</b>: wanted in every repository Meera opens, and teammates have asked <b>not to see it</b>.' },
      { id: 'B', label: 'Decider changed', desc: 'The team adopts /standup as its <b>shared format for this repository</b> and wants it on clone. It reads only git log.' }
    ],
    runs: {
      A: [
        { steps: [F('.claude/commands/standup.md', 'project, committed', standupMine, 'Option A: committed to clinic-app, with a README line saying "optional".'),
            C('Teammate Tom pulls main and types /', 'Project commands reach everyone who clones the repository. A README note does not hide it.', '/standup      (project)  Summarise my commits since yesterday\n' + menuTeam, 'bad'),
            C('Meera opens Claude Code in another repository, infra-scripts', 'A project command lives in one repository only.', '> /standup\n\u2717 Unknown command: /standup', 'bad'),
            TB('Who sees /standup where', 'Wrong people, wrong places.', head01, [['Meera', 'clinic-app', 'yes', 'yes'], ['Meera', 'infra-scripts', 'no', 'yes \u2717'], ['Tom, Ana', 'clinic-app', 'yes', 'no \u2717']], 'bad')],
          outcome: { ok: false, text: 'A committed project command goes to every teammate and to no other repository. The command is personal, so both halves are wrong.' }, rate: 0.3 },
        { steps: [F('~/.claude/CLAUDE.md', 'user memory', '## Standup\nWhen I ask for standup: run git log for my commits since yesterday,\nread ~/notes/standup.md, write Yesterday / Today / Blockers.', 'Option B: the steps become a memory section.'),
            C('Claude Code starts in clinic-app', 'User memory loads at the start of every session, in every repository.', 'loaded: ~/.claude/CLAUDE.md (user), ./CLAUDE.md (project)'),
            M('Context at start', 'The standup text rides along in every session, used once a day.', [['Project CLAUDE.md', 1800, 'sys'], ['Standup section (every session)', 260, 'drop']]),
            P('Meera types /standup', '', '> /standup'),
            C('There is no such command', 'Memory is instructions Claude reads, not a command you can run.', '\u2717 Unknown command: /standup', 'bad')],
          outcome: { ok: false, text: 'A memory file holds always-loaded instructions. It does not create an invocable /standup command.' }, rate: 0.2 },
        { steps: [F('clinic-app/.claude/commands/standup.md + .gitignore', 'project folder, ignored', '.claude/commands/standup.md   (local copy)\n.gitignore:  .claude/commands/standup.md', 'Option C: a private copy, kept out of git.'),
            C('Meera in clinic-app: /standup works; teammates do not see it', '', '/standup      (project)\n' + menuTeam),
            C('Meera clones a new repository, booking-widget, and types /standup', 'No copy here yet. She must add the file and the ignore line again, in every repository.', '> /standup\n\u2717 Unknown command: /standup', 'bad')],
          outcome: { ok: false, text: 'It stays private, but it lives per repository, so every new repository needs another copy. User-level commands already follow the user everywhere.' }, rate: 0.7 },
        { steps: [F('~/.claude/commands/standup.md', 'user, outside any repository', standupMine, 'Option D.'),
            C('Meera starts Claude Code in clinic-app', 'User commands load from her home folder, in any repository.', '/standup      (user)\n' + menuTeam, 'ok'),
            C('Meera starts Claude Code in infra-scripts', '', '/standup      (user)', 'ok'),
            C('Tom starts Claude Code in clinic-app', 'Her home folder is not in the repository, so he never sees it.', menuTeam, 'ok'),
            TB('Who sees /standup where', '', head01, [['Meera', 'clinic-app', 'yes', 'yes'], ['Meera', 'infra-scripts', 'yes', 'yes'], ['Tom, Ana', 'clinic-app', 'no', 'no'], ['Meera', 'any new repo', 'yes', 'yes']], 'ok')],
          outcome: { ok: true, text: 'A user-level command is personal and available in every project she opens. Nobody else sees it.' }, rate: 1 }
      ],
      B: [
        { steps: [F('.claude/commands/standup.md', 'project, committed', standupTeam, 'The team agreed on one standup format.'),
            C('Tom pulls main and types /', 'Committed project commands arrive on clone.', '/standup      (project)  Team standup from git log\n' + menuTeam, 'ok'),
            P('Tom runs /standup', '', 'Yesterday: added GET /slots/:id. Today: slot tests. Blockers: none.', 'ok')],
          outcome: { ok: true, text: 'The team wants it on clone, so the repository\'s .claude/commands/ is the right home. This is the world where the runner-up wins.' }, rate: 1 },
        { steps: [F('~/.claude/CLAUDE.md', 'user memory, Meera only', '## Standup\n(steps)', ''),
            C('Tom types /standup', 'A memory section is not a command, and this one is on Meera\'s machine.', '\u2717 Unknown command: /standup', 'bad')],
          outcome: { ok: false, text: 'Memory is not a command, and user memory never reaches teammates.' }, rate: 0.1 },
        { steps: [F('.claude/commands/standup.md + .gitignore', 'ignored', '.gitignore:  .claude/commands/standup.md', ''),
            C('Tom pulls main and types /standup', 'The file is ignored, so it never reaches git.', '\u2717 Unknown command: /standup', 'bad')],
          outcome: { ok: false, text: 'An ignored file cannot be shared on clone.' }, rate: 0.2 },
        { steps: [F('~/.claude/commands/standup.md', 'user, Meera only', standupTeam, ''),
            C('Tom starts Claude Code in clinic-app', 'User commands belong to one person.', menuTeam + '\n> /standup\n\u2717 Unknown command: /standup', 'bad')],
          outcome: { ok: false, text: 'Only Meera has it. The team wanted it for everyone who clones.' }, rate: 0.3 }
      ]
    }
  };

  /* ------------------------------------------------------------ m7-s2-02 path-scoped rule for screens */
  var a11y = '# Screen accessibility\n- Every Pressable has accessibilityLabel and accessibilityRole.\n- Touch targets at least 44x44.\n- Text keeps allowFontScaling on.';
  var a11yRule = '---\npaths:\n  - "**/*.screen.tsx"\n---\n' + a11y;
  var goodScreen = '<Pressable onPress={cancel} accessibilityRole="button"\n  accessibilityLabel="Cancel appointment" style={styles.target44}>';
  var badScreen = '<Pressable onPress={cancel}>\n  <Text>Cancel</Text>\n</Pressable>\n// no accessibilityLabel, no accessibilityRole';
  var root02 = ['Root CLAUDE.md', 1500, 'sys'];

  var s202 = {
    id: 'm7-s2-02', who: 'Engineer', labels: LBL, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Screens are <code>*.screen.tsx</code> files in <b>two trees</b>: mobile/ feature folders and packages/shared/ui/.' },
      { id: 'B', label: 'Decider changed', desc: '<b>Every screen sits under mobile/</b>, and the team wants the conventions for all mobile UI work. packages/shared/ holds only types.' }
    ],
    runs: {
      A: [
        { steps: [F('mobile/CLAUDE.md', 'directory memory', a11y, 'Option A, file 1.'),
            F('packages/shared/ui/CLAUDE.md', 'directory memory', '@../../../mobile/CLAUDE.md', 'File 2 exists only to import file 1. One file per tree that holds screens.'),
            C('Server session: editing server/src/appointments/router.ts', 'No file under mobile/ or packages/shared/ui/ is read, so neither loads.', 'loaded: ./CLAUDE.md', 'ok'),
            C('Mobile session: editing mobile/features/booking/useSlots.ts', 'A data hook, not a screen. A directory file loads for every file in its tree.', 'loaded: ./CLAUDE.md, mobile/CLAUDE.md', 'warn'),
            M('Context for the hook edit', '', [root02, ['A11y conventions (no screen in this task)', 900, 'drop']], 'warn'),
            C('Editing packages/shared/ui/DatePicker.screen.tsx', 'Covered, but only because a second file was added for the second tree.', 'loaded: ./CLAUDE.md, packages/shared/ui/CLAUDE.md \u2192 @mobile/CLAUDE.md', 'ok')],
          outcome: { ok: true, warn: true, text: 'Screens are a filename pattern, not a folder. Folder files need one per tree and also load for every non-screen file in those trees.' }, rate: 1 },
        { steps: [F('.claude/skills/a11y/SKILL.md', 'project skill', '---\nname: a11y\ndescription: Use whenever a *.screen.tsx file is edited.\n---\n' + a11y, 'Only the name and description sit in context until Claude invokes the skill.'),
            P('Engineer asks', '', 'Add a cancel button to mobile/features/booking/BookingSlot.screen.tsx'),
            M('Context for the screen edit', 'The body is not loaded unless Claude decides to invoke the skill.', [root02, ['a11y skill description', 40, 'sys'], ['a11y skill body (not invoked)', 0, 'drop']], 'warn'),
            C('Claude edits the screen without invoking /a11y', 'Invoking a skill is Claude\'s choice. This time it went straight to the edit.', badScreen, 'bad')],
          outcome: { ok: false, text: 'A skill loads on demand. Relying on Claude to invoke it from a description is less dependable than a rule that loads by path.' }, rate: 0.85 },
        { steps: [F('.claude/rules/a11y-screens.md', 'project rule, committed', a11yRule, 'Option C: the paths: glob names the file pattern, not a folder.'),
            C('Server session: editing server/src/appointments/router.ts', 'No matching file, so the rule stays out.', 'loaded: ./CLAUDE.md', 'ok'),
            C('Editing packages/shared/ui/DatePicker.screen.tsx', 'Claude reads a file that matches **/*.screen.tsx, so the rule loads, whatever folder it is in.', 'loaded: ./CLAUDE.md, .claude/rules/a11y-screens.md', 'ok'),
            M('Context for the screen edit', '', [root02, ['a11y-screens rule (matched by path)', 900, 'new']]),
            C('Claude writes the screen', '', goodScreen, 'ok')],
          outcome: { ok: true, text: 'A rule with a paths glob loads whenever Claude works on a matching file, in either tree, and never in server sessions.' }, rate: 1 },
        { steps: [F('CLAUDE.md', 'project memory, root', '# clinic-app\n\u2026\n@docs/a11y-screens.md', 'Option D: the text moves to its own file, imported by the root.'),
            C('Server session: editing server/src/appointments/router.ts', 'An imported file loads with the file that imports it: every session.', 'loaded: ./CLAUDE.md, docs/a11y-screens.md (import)'),
            M('Context for server work', 'Same tokens as before the change.', [root02, ['a11y conventions (imported, server task)', 900, 'drop']], 'bad')],
          outcome: { ok: false, text: '@import organises memory into modules. The imported file still loads in every session, server work included.' }, rate: 0.4 }
      ],
      B: [
        { steps: [F('mobile/CLAUDE.md', 'directory memory', a11y, 'packages/shared/ui/ has no screens now; the second file never matters.'),
            C('Server session: editing server/src/appointments/router.ts', '', 'loaded: ./CLAUDE.md', 'ok'),
            C('Editing mobile/features/booking/BookingSlot.screen.tsx', 'All screens and all the UI work it covers are under mobile/.', 'loaded: ./CLAUDE.md, mobile/CLAUDE.md', 'ok'),
            C('Claude writes the screen', '', goodScreen, 'ok')],
          outcome: { ok: true, text: 'When the convention belongs to one folder, that folder\'s CLAUDE.md is a fine home. This is the world where the runner-up wins.' }, rate: 1 },
        { steps: [P('Engineer asks', '', 'Add a cancel button to BookingSlot.screen.tsx'),
            C('Claude edits without invoking /a11y', 'Still on demand.', badScreen, 'bad')],
          outcome: { ok: false, text: 'A skill still waits to be invoked.' }, rate: 0.85 },
        { steps: [F('.claude/rules/a11y-screens.md', 'project rule', a11yRule, ''),
            C('Editing mobile/features/booking/BookingSlot.screen.tsx', '', 'loaded: ./CLAUDE.md, .claude/rules/a11y-screens.md', 'ok'),
            C('Claude writes the screen', '', goodScreen, 'ok')],
          outcome: { ok: true, text: 'The rule works here too. With one folder, either home is fine.' }, rate: 1 },
        { steps: [C('Server session', '', 'loaded: ./CLAUDE.md, docs/a11y-screens.md (import)'),
            M('Context for server work', '', [root02, ['a11y conventions (imported)', 900, 'drop']], 'bad')],
          outcome: { ok: false, text: 'An import still loads everywhere.' }, rate: 0.4 }
      ]
    }
  };

  /* ------------------------------------------------------------ m7-s2-04 always-loaded team standard */
  var money = '## Money\nStore money as integer cents (number, named *Cents). Never floats.\nFormat only at the edge with formatCents().';
  var ticket04 = 'Ticket CL-212: charge a $15.50 no-show fee on missed appointments.';
  var goodFee = '// server/src/appointments/noShowFee.ts\nexport const NO_SHOW_FEE_CENTS = 1550;';
  var badFee = '// server/src/appointments/noShowFee.ts\nexport const noShowFee = 15.50;   // float';
  var rule04 = '---\npaths:\n  - "server/src/billing/**"\n  - "mobile/src/pricing/**"\n  - "packages/shared/money/**"\n---\n' + money;

  var s204 = {
    id: 'm7-s2-04', who: 'Engineer', labels: LBL, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Floats appear <b>wherever new code is generated</b>, and every engineer should get the rule <b>in every session</b>.' },
      { id: 'B', label: 'Decider changed', desc: 'Prices are only ever written in <b>three price modules</b>; the rule matters only when those files are edited.' }
    ],
    runs: {
      A: [
        { steps: [F('CLAUDE.md', 'project memory, committed', '# clinic-app conventions\n\u2026\n' + money, 'Option A: a short rule beside the other conventions.'),
            P('Engineer Ana starts Claude Code', '', ticket04),
            M('Context at start, any folder, any engineer', 'Project memory is always loaded, and everyone has it through git.', [['Root CLAUDE.md incl. money rule', 1600, 'sys']]),
            C('Claude creates a new file outside any price module', '', goodFee, 'ok')],
          outcome: { ok: true, text: 'A universal team standard belongs in always-loaded project memory. Every engineer gets it through the repository, in every session.' }, rate: 1 },
        { steps: [F('.claude/rules/money.md', 'project rule, committed', rule04, 'Option B: globs for the three price modules.'),
            P('Engineer Ana starts Claude Code', '', ticket04),
            C('Claude creates server/src/appointments/noShowFee.ts', 'Not under any glob. No matching file is read, so the rule never loads.', 'loaded: ./CLAUDE.md'),
            M('Context for this ticket', '', [['Root CLAUDE.md', 1500, 'sys'], ['money rule (no matching file)', 0, 'drop']], 'warn'),
            C('Claude writes the fee', 'Fees, deposits and refunds turn up in new files all over the code.', badFee, 'bad')],
          outcome: { ok: false, text: 'A path rule loads only when matching files are in play. Floats appear wherever new code is written, so the rule must be in every session.' }, rate: 0.6 },
        { steps: [F('~/.claude/CLAUDE.md', 'user memory, per engineer', money + '\n(copied from the wiki)', 'Option C: each person pastes the snippet.'),
            P('New engineer Leo, week 1, has not copied it yet', '', ticket04),
            M('Leo\'s context', 'His home folder has no money rule.', [['Root CLAUDE.md', 1500, 'sys'], ['money rule (not in his user file)', 0, 'drop']], 'warn'),
            C('Claude writes the fee', '', badFee, 'bad')],
          outcome: { ok: false, text: 'User-level memory is not shared through version control. It drifts per person, and new joiners start without it.' }, rate: 0.7 },
        { steps: [F('.claude/skills/money/SKILL.md', 'project skill', '---\nname: money\ndescription: Use for pricing work.\ncontext: fork\n---\n' + money, 'Option D: still a skill, now forked.'),
            P('Engineer Ana starts Claude Code', '', ticket04),
            M('Context for this ticket', 'Only the description is loaded. Even when invoked, a forked skill runs in its own context, apart from the session writing the code.', [['Root CLAUDE.md', 1500, 'sys'], ['money skill description', 30, 'sys'], ['money rule (not invoked)', 0, 'drop']], 'warn'),
            C('Claude writes the fee without invoking /money', '', badFee, 'bad')],
          outcome: { ok: false, text: 'A skill stays on demand, and a fork isolates it from the main session\'s work.' }, rate: 0.3 }
      ],
      B: [
        { steps: [F('CLAUDE.md', 'project memory', '\u2026\n' + money, ''),
            P('Engineer asks', '', 'Edit the cancellation fee in server/src/billing/fees.ts'),
            M('Context in every session', 'Loaded for price edits and for the many sessions that never touch prices.', [['Root CLAUDE.md', 1500, 'sys'], ['money rule (most sessions: unused)', 100, 'drop']], 'warn'),
            C('Claude writes cents', '', 'export const CANCEL_FEE_CENTS = 2000;', 'ok')],
          outcome: { ok: true, warn: true, text: 'It works, but it loads everywhere when only three modules need it.' }, rate: 1 },
        { steps: [F('.claude/rules/money.md', 'project rule', rule04, ''),
            P('Engineer asks', '', 'Edit the cancellation fee in server/src/billing/fees.ts'),
            C('Claude reads server/src/billing/fees.ts', 'Matches server/src/billing/**, so the rule loads.', 'loaded: ./CLAUDE.md, .claude/rules/money.md', 'ok'),
            M('Context for this edit', '', [['Root CLAUDE.md', 1500, 'sys'], ['money rule (matched by path)', 100, 'new']]),
            C('Claude writes cents', '', 'export const CANCEL_FEE_CENTS = 2000;', 'ok')],
          outcome: { ok: true, text: 'When the rule matters only for specific files, a path rule is the leaner home. This is the world where the runner-up wins.' }, rate: 1 },
        { steps: [P('New engineer Leo edits fees.ts', '', 'Edit the cancellation fee in server/src/billing/fees.ts'),
            C('No money rule in his user file', '', 'export const cancelFee = 20.0;', 'bad')],
          outcome: { ok: false, text: 'Still per person and not shared.' }, rate: 0.7 },
        { steps: [P('Engineer edits fees.ts', '', 'Edit the cancellation fee in server/src/billing/fees.ts'),
            C('Claude edits without invoking /money', '', 'export const cancelFee = 20.0;', 'bad')],
          outcome: { ok: false, text: 'A skill still waits to be invoked.' }, rate: 0.6 }
      ]
    }
  };

  /* ------------------------------------------------------------ m7-s2-05 user memory is not shared */
  var naming = '## Test names\n"<unit> <does what> when <condition>"\ne.g. "cancelAppointment refunds deposit when cancelled 24h ahead"\nFiles: *.test.ts beside the source.';
  var askLeo = 'Write tests for cancelAppointment.';
  var goodTests = "it('cancelAppointment refunds deposit when cancelled 24h ahead', \u2026)\nit('cancelAppointment keeps deposit when cancelled within 24h', \u2026)";
  var badTests = "it('works', \u2026)\nit('test cancel 2', \u2026)";
  var memOut = '> /memory\nMemory files loaded\n  User memory     ~/.claude/CLAUDE.md     (contains: ## Test names)\n  Project memory  ./CLAUDE.md';

  var s205 = {
    id: 'm7-s2-05', who: 'Engineer', labels: LBL, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'The cause is <b>already confirmed</b>: the conventions sit only in the senior\'s <code>~/.claude/CLAUDE.md</code>.' },
      { id: 'B', label: 'Decider changed', desc: '<b>Nobody knows yet</b> where the senior\'s conventions come from. Nothing has been checked.' }
    ],
    runs: {
      A: [
        { steps: [F('.claude/commands/test-names.md', 'project command', '---\ndescription: Rename tests to team style\n---\n' + naming, 'Option A.'),
            P('New engineer Leo asks', '', askLeo),
            M('Leo\'s context', 'The command is listed, but its text loads only when someone runs it.', [['Project CLAUDE.md (no naming rule)', 1500, 'sys'], ['/test-names (not run)', 0, 'drop']], 'warn'),
            C('Claude writes the tests', 'Leo did not know to run /test-names.', badTests, 'bad')],
          outcome: { ok: false, text: 'A command waits to be run. Naming conventions should apply while tests are written.' }, rate: 0.5 },
        { steps: [P('Senior runs /memory in clinic-app', 'Option B.', '> /memory'),
            C('/memory lists the loaded files', 'It shows what she already found. No new information.', memOut, 'warn'),
            P('New engineer Leo asks', 'Nothing has changed for him.', askLeo),
            M('Leo\'s context', '', [['Project CLAUDE.md (no naming rule)', 1500, 'sys'], ['test-name conventions', 0, 'drop']], 'warn'),
            C('Claude writes the tests', '', badTests, 'bad')],
          outcome: { ok: false, text: '/memory is the first step when the source is unknown. Here it is already known, so checking again fixes nothing.' }, rate: 0 },
        { steps: [F('docs/test-naming.md', 'committed', naming, 'Option C: one shared source file.'),
            F('~/.claude/CLAUDE.md', 'user memory, each engineer', '@~/code/clinic-app/docs/test-naming.md', 'Each person must add this line by hand.'),
            P('New engineer Leo joined Monday; nobody told him about the line', '', askLeo),
            M('Leo\'s context', '', [['Project CLAUDE.md', 1500, 'sys'], ['test-naming.md (not imported by Leo)', 0, 'drop']], 'warn'),
            C('Claude writes the tests', '', badTests, 'bad')],
          outcome: { ok: false, text: 'One file helps, but the wiring is still in each user-level file. New joiners miss it.' }, rate: 0.7 },
        { steps: [F('CLAUDE.md', 'project memory, committed', '# clinic-app\n\u2026\n' + naming, 'Option D: the conventions move into the repository.'),
            F('~/.claude/CLAUDE.md', 'user memory, senior', '(## Test names removed)', 'One copy left, so no two versions to drift.'),
            P('New engineer Leo asks', '', askLeo),
            M('Leo\'s context', 'Everyone who clones gets it.', [['Project CLAUDE.md incl. test names', 1650, 'sys']]),
            C('Claude writes the tests', '', goodTests, 'ok')],
          outcome: { ok: true, text: 'User-level memory is not shared through version control. Project memory reaches everyone on clone.' }, rate: 1 }
      ],
      B: [
        { steps: [P('New engineer Leo asks', '', askLeo),
            C('Claude writes the tests', '', badTests, 'bad')],
          outcome: { ok: false, text: 'A command still waits to be run.' }, rate: 0.5 },
        { steps: [P('Senior runs /memory in clinic-app', 'Nobody knows where the conventions come from, so look first.', '> /memory'),
            C('/memory lists the loaded files', 'Now the cause is known: they live in her user-level file, which nobody else has.', memOut, 'ok'),
            P('The team now knows the fix', '', 'Move ## Test names into the project CLAUDE.md.', 'ok')],
          outcome: { ok: true, text: 'With the cause unknown, listing loaded memory comes first. This is the world where the runner-up wins.' }, rate: 1 },
        { steps: [F('~/.claude/CLAUDE.md', 'user memory', '@docs/test-naming.md', 'A shared file, wired per person.'),
            C('Leo has no import line', '', badTests, 'bad')],
          outcome: { ok: false, text: 'Still per person, and done without knowing the source.' }, rate: 0.6 },
        { steps: [F('CLAUDE.md', 'project memory', naming, 'The senior guesses where her copy is and moves it.'),
            C('Leo\'s tests follow the conventions', 'It happens to be right; nobody checked first.', goodTests, 'warn')],
          outcome: { ok: true, warn: true, text: 'The guess was right this time. Without looking, they could have moved the wrong file or left a second copy.' }, rate: 0.9 }
      ]
    }
  };

  /* ------------------------------------------------------------ m7-s4-06 job conventions by glob */
  var jobs = '# Background jobs\n- perform is idempotent: check state before acting.\n- Set retry_on \u2026 attempts: explicitly.\n- Pass record IDs, never ActiveRecord objects.\n(\u2026 3,100 tokens)';
  var jobRule = '---\npaths:\n  - "**/*_job.rb"\n---\n' + jobs;
  var engJob = 'engines/billing/app/jobs/invoice_retry_job.rb';
  var goodJob = 'class InvoiceRetryJob < ApplicationJob\n  retry_on Stripe::APIConnectionError, attempts: 5\n  def perform(invoice_id)\n    invoice = Invoice.find(invoice_id)\n    return if invoice.paid?\n    \u2026';
  var badJob = 'class InvoiceRetryJob < ApplicationJob\n  def perform(invoice)        # whole object, no retry limit\n    invoice.charge!            # charges twice on a retry\n    \u2026';
  var reactSess = 'Front-end session: editing app/javascript/components/LessonCard.tsx';
  var root06 = ['Root CLAUDE.md', 1400, 'sys'];

  var s406 = {
    id: 'm7-s4-06', who: 'Engineer', labels: LBL, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'Job files all end in <code>_job.rb</code> but live in <b>many directories</b> across the engines.' },
      { id: 'B', label: 'Decider changed', desc: '<b>Every job class lives in app/jobs/</b>. The engines have none.' }
    ],
    runs: {
      A: [
        { steps: [F('.claude/rules/background-jobs.md', 'project rule', jobRule, 'Option A.'),
            C(reactSess, 'No *_job.rb file, so the rule stays out.', 'loaded: ./CLAUDE.md', 'ok'),
            C('Job session: editing ' + engJob, 'The file matches **/*_job.rb, deep inside an engine.', 'loaded: ./CLAUDE.md, .claude/rules/background-jobs.md', 'ok'),
            M('Context for the job edit', '', [root06, ['background-jobs rule (matched by path)', 3100, 'new']]),
            C('Claude writes the job', '', goodJob, 'ok')],
          outcome: { ok: true, text: 'A path-scoped rule loads only when Claude works on matching files, wherever they live.' }, rate: 1 },
        { steps: [F('CLAUDE.md', 'project memory, root', '# Lingo monolith\n\u2026\n@docs/job-conventions.md', 'Option B.'),
            C(reactSess, 'An imported file loads with the root file: every session.', 'loaded: ./CLAUDE.md, docs/job-conventions.md (import)'),
            M('Context for the front-end edit', '', [root06, ['job conventions (imported, no job here)', 3100, 'drop']], 'bad')],
          outcome: { ok: false, text: '@import keeps CLAUDE.md tidy, but the imported file still loads in every session.' }, rate: 0.3 },
        { steps: [F('CLAUDE.md', 'project memory, root', '## Job conventions (read first)\n' + jobs + '\n\n# Lingo monolith\n\u2026', 'Option C: moved to the top under a heading.'),
            C(reactSess, 'Position changes attention, not loading.', 'loaded: ./CLAUDE.md'),
            M('Context for the front-end edit', '', [['Job conventions (top of root file)', 3100, 'drop'], root06], 'bad')],
          outcome: { ok: false, text: 'First place with a heading gets attention. It still loads in every session.' }, rate: 0.3 },
        { steps: [F('app/jobs/CLAUDE.md', 'directory memory', jobs, 'Option D: where the generator puts new jobs.'),
            C('Editing app/jobs/lesson_reminder_job.rb', '', 'loaded: ./CLAUDE.md, app/jobs/CLAUDE.md', 'ok'),
            C('Editing ' + engJob, 'This job is not under app/jobs/, so the directory file never loads.', 'loaded: ./CLAUDE.md', 'bad'),
            M('Context for the engine job edit', '', [root06, ['job conventions (wrong folder)', 0, 'drop']], 'warn'),
            C('Claude writes the job', '', badJob, 'bad')],
          outcome: { ok: false, text: 'A directory CLAUDE.md covers one folder. These jobs are spread across many, so most never see it.' }, rate: 0.4 }
      ],
      B: [
        { steps: [F('.claude/rules/background-jobs.md', 'project rule', jobRule, ''),
            C('Editing app/jobs/invoice_retry_job.rb', '', 'loaded: ./CLAUDE.md, .claude/rules/background-jobs.md', 'ok'),
            C('Claude writes the job', '', goodJob, 'ok')],
          outcome: { ok: true, text: 'The rule still works with one folder.' }, rate: 1 },
        { steps: [C(reactSess, '', 'loaded: ./CLAUDE.md, docs/job-conventions.md (import)'),
            M('Context for the front-end edit', '', [root06, ['job conventions (imported)', 3100, 'drop']], 'bad')],
          outcome: { ok: false, text: 'An import still loads in every session.' }, rate: 0.3 },
        { steps: [C(reactSess, '', 'loaded: ./CLAUDE.md'),
            M('Context for the front-end edit', '', [['Job conventions (top)', 3100, 'drop'], root06], 'bad')],
          outcome: { ok: false, text: 'Still always loaded.' }, rate: 0.3 },
        { steps: [F('app/jobs/CLAUDE.md', 'directory memory', jobs, ''),
            C(reactSess, '', 'loaded: ./CLAUDE.md', 'ok'),
            C('Editing app/jobs/invoice_retry_job.rb', 'Every job is here, so the folder file reaches all of them.', 'loaded: ./CLAUDE.md, app/jobs/CLAUDE.md', 'ok'),
            C('Claude writes the job', '', goodJob, 'ok')],
          outcome: { ok: true, text: 'When all matching files share one folder, that folder\'s CLAUDE.md does the job. This is the world where the runner-up wins.' }, rate: 1 }
      ]
    }
  };

  /* ------------------------------------------------------------ m7-s4-07 runbook as a skill */
  var runbook = '# Restore staging from a snapshot\n1. Put staging in maintenance mode.\n2. Pick the snapshot (pg_restore --list).\n3. Restore into staging_restore, then swap.\n4. Re-run the PII scrub: bin/rails db:scrub.\n5. Leave maintenance mode; post in #staging.\n(\u2026 2,800 tokens)';
  var askRestore = 'Restore staging from last night\'s snapshot.';
  var badRestore = '$ pg_restore --clean -d staging snapshots/2026-10-03.dump\n# no maintenance mode, no PII scrub';
  var goodRestore = '1. maintenance on  2. snapshot 2026-10-03  3. restore \u2192 staging_restore, swap\n4. bin/rails db:scrub  5. maintenance off, posted in #staging';
  var dbGuide = '# Database config\n- Staging pool size <= 20.\n- Snapshot files: YYYY-MM-DD.dump.';
  var root07 = ['Root CLAUDE.md', 1400, 'sys'];

  var s407 = {
    id: 'm7-s4-07', who: 'Engineer', labels: LBL, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'The runbook is a task <b>run on request</b>, about once a month. It is <b>not tied to editing any file</b>.' },
      { id: 'B', label: 'Decider changed', desc: 'The text is <b>guidance for editing</b> config/database.yml and db/snapshots/ (pool sizes, snapshot naming). Nobody asks for it; edits trigger it.' }
    ],
    runs: {
      A: [
        { steps: [F('.claude/rules/db-restore.md', 'project rule', '---\npaths:\n  - "config/database.yml"\n  - "db/snapshots/**"\n---\n' + runbook, 'Option A.'),
            P('Engineer asks in a fresh session', '', askRestore),
            C('No matching file has been read when the request arrives', 'A path rule loads when Claude reads a matching file. A request is not a file.', 'loaded: ./CLAUDE.md'),
            M('Context when Claude plans the restore', '', [root07, ['restore runbook (no matching file read)', 0, 'drop']], 'warn'),
            C('Claude improvises the restore', 'Next week someone edits config/database.yml for a pool size and gets 2,800 tokens of runbook they did not ask for.', badRestore, 'bad')],
          outcome: { ok: false, text: 'Path rules are triggered by editing matching files. A restore is requested, so the trigger is wrong.' }, rate: 0.5 },
        { steps: [F('.claude/skills/restore-staging/SKILL.md', 'project skill, committed', '---\nname: restore-staging\ndescription: Restore the staging Postgres database from a snapshot.\n---\n' + runbook, 'Option B: shared through the repository.'),
            M('Context in an ordinary session', 'Only the name and description load until the skill is invoked.', [root07, ['restore-staging description', 30, 'sys']], 'ok'),
            P('Engineer asks', '', '/restore-staging last night'),
            M('Context after invoking', '', [root07, ['restore-staging description', 30, 'sys'], ['restore runbook (invoked)', 2800, 'new']]),
            C('Claude follows the runbook', '', goodRestore, 'ok')],
          outcome: { ok: true, text: 'Skills are on-demand task workflows. Shared through the repository, loaded only when someone asks.' }, rate: 1 },
        { steps: [F('CLAUDE.md', 'project memory, root', '\u2026\n@docs/restore-staging.md', 'Option C.'),
            C('Ordinary session: editing a React component', 'The imported runbook loads with the root file.', 'loaded: ./CLAUDE.md, docs/restore-staging.md (import)'),
            M('Context for unrelated work', '', [root07, ['restore runbook (imported, unused)', 2800, 'drop']], 'bad')],
          outcome: { ok: false, text: '@import organises CLAUDE.md, but the runbook still loads in every session.' }, rate: 0.3 },
        { steps: [F('db/CLAUDE.md', 'directory memory', runbook, 'Option D.'),
            P('Engineer asks in a fresh session', '', askRestore),
            C('No db/ file read yet, so db/CLAUDE.md is not loaded', 'Meanwhile every migration edit under db/migrate/ loads the runbook.', 'loaded: ./CLAUDE.md', 'bad'),
            C('Claude improvises the restore', '', badRestore, 'bad')],
          outcome: { ok: false, text: 'A directory file loads by folder, which has nothing to do with when a restore is requested.' }, rate: 0.4 }
      ],
      B: [
        { steps: [F('.claude/rules/db-config.md', 'project rule', '---\npaths:\n  - "config/database.yml"\n  - "db/snapshots/**"\n---\n' + dbGuide, ''),
            P('Engineer asks', '', 'Raise the staging pool size.'),
            C('Claude reads config/database.yml', 'A matching file, so the rule loads.', 'loaded: ./CLAUDE.md, .claude/rules/db-config.md', 'ok'),
            C('Claude edits within the guidance', '', 'staging:\n  pool: 20', 'ok')],
          outcome: { ok: true, text: 'Guidance for editing particular files is what a path rule is for. This is the world where the runner-up wins.' }, rate: 1 },
        { steps: [P('Engineer asks', '', 'Raise the staging pool size.'),
            C('Claude edits without invoking the skill', 'Nobody asked for it; edits do not invoke skills.', 'staging:\n  pool: 50', 'bad')],
          outcome: { ok: false, text: 'A skill waits to be invoked. Editing guidance should load by itself.' }, rate: 0.6 },
        { steps: [C('Every session loads the guidance', 'Works for config edits, and costs tokens everywhere else.', 'loaded: ./CLAUDE.md, docs/db-config.md (import)', 'warn')],
          outcome: { ok: true, warn: true, text: 'It works, but always loaded is heavier than needed.' }, rate: 1 },
        { steps: [C('Claude reads config/database.yml', 'Not under db/, so db/CLAUDE.md does not load.', 'loaded: ./CLAUDE.md', 'bad')],
          outcome: { ok: false, text: 'The files are not all in db/.' }, rate: 0.5 }
      ]
    }
  };

  /* ------------------------------------------------------------ m7-s5-01 review criteria in project memory */
  var criteria = '## Review criteria\n1. Flag hard-coded secrets, tokens or internal URLs in any file.\n2. Public API change needs a CHANGELOG line.\n3. No TODO without a ticket id (TRV-123).';
  var ciCmd = '$ claude -p "Review PR #815 and post inline comments." --output-format json\n# runner: fresh checkout, empty ~/.claude/';
  var pr815 = 'PR #815 changes: .github/workflows/deploy.yml (+ API_TOKEN: "sk_live_\u2026"), db/migrations/V42__fare_class.sql';
  var flagged = 'deploy.yml:14  Hard-coded token. Move it to a GitHub secret. (criterion 1)';
  var missed = '{"result": "No issues found."}';

  var s501 = {
    id: 'm7-s5-01', who: 'CI job', labels: LBL, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: 'The criteria apply to <b>every file</b> in the repository, in every language.' },
      { id: 'B', label: 'Decider changed', desc: 'The criteria cover <b>only Kotlin and TypeScript source files</b>, spread across modules. YAML and SQL have their own checks.' }
    ],
    runs: {
      A: [
        { steps: [F('.claude/rules/review.md', 'project rule, committed', '---\npaths:\n  - "**/*.kt"\n  - "**/*.ts"\n---\n' + criteria, 'Option A.'),
            P('CI review job starts', pr815, ciCmd),
            C('Claude reads deploy.yml and the SQL migration', 'Neither matches *.kt or *.ts, so the rule never loads.', 'loaded: ./CLAUDE.md'),
            M('Context for this review', '', [['Root CLAUDE.md', 1500, 'sys'], ['review criteria (no matching file)', 0, 'drop']], 'warn'),
            C('Claude posts its review', 'The token sits in a YAML file the criteria were meant to cover.', missed, 'bad')],
          outcome: { ok: false, text: 'A path rule loads only when matching files are in play. These criteria cover every file, so they must always load.' }, rate: 0.6 },
        { steps: [F('docs/review-criteria.md', 'committed', criteria, 'Option B.'),
            P('CI review job starts', '', '$ claude -p "Review PR #815. Follow docs/review-criteria.md." --output-format json'),
            C('CI flags the token', 'The prompt names the file, so CI reads it.', flagged, 'ok'),
            P('Developer Lina reviews a branch locally', '', '> Review my changes before I open a PR.'),
            M('Lina\'s context', 'Nothing points her session at the file.', [['Root CLAUDE.md', 1500, 'sys'], ['review criteria (only in the CI prompt)', 0, 'drop']], 'warn'),
            C('Claude reviews without the criteria', '', 'Looks good to me.', 'bad')],
          outcome: { ok: false, text: 'CI gets them; developers\' sessions never load a file that only the CI prompt mentions.' }, rate: 0.5 },
        { steps: [F('CLAUDE.md', 'project memory, committed', '# travel-booking\n\u2026\n' + criteria, 'Option C.'),
            P('CI review job starts', pr815, ciCmd),
            M('Context for the CI review', 'Headless runs load the project CLAUDE.md from the checkout, like local sessions.', [['Root CLAUDE.md incl. review criteria', 1650, 'sys']]),
            C('Claude posts its review', '', flagged, 'ok'),
            P('Developer Lina reviews locally', 'Same file, same criteria.', '> Review my changes before I open a PR.', 'ok')],
          outcome: { ok: true, text: 'Project CLAUDE.md is shared through version control and loads in every session, local or headless.' }, rate: 1 },
        { steps: [F('.claude/skills/review/SKILL.md', 'project skill', '---\nname: review\ndescription: Team review criteria.\n---\n' + criteria, 'Option D.'),
            P('CI review job starts', pr815, ciCmd),
            M('Context for the CI review', 'Only the description loads until the skill is invoked.', [['Root CLAUDE.md', 1500, 'sys'], ['review skill description', 30, 'sys'], ['review criteria (not invoked)', 0, 'drop']], 'warn'),
            C('Claude reviews without invoking /review', '', missed, 'bad')],
          outcome: { ok: false, text: 'Shared, but skills load on demand. A session that does not invoke it skips the criteria.' }, rate: 0.7 }
      ],
      B: [
        { steps: [F('.claude/rules/review.md', 'project rule', '---\npaths:\n  - "**/*.kt"\n  - "**/*.ts"\n---\n## Review criteria (Kotlin/TS)\n\u2026', ''),
            P('CI review job starts', 'PR #812 changes booking/src/main/kotlin/FareService.kt', '$ claude -p "Review PR #812 and post inline comments." --output-format json'),
            C('Claude reads FareService.kt', 'A match, so the rule loads, in CI and locally alike.', 'loaded: ./CLAUDE.md, .claude/rules/review.md', 'ok'),
            C('Claude posts its review', '', 'FareService.kt:88  TODO without a ticket id. (criterion 3)', 'ok')],
          outcome: { ok: true, text: 'Conventions for one file type spread across modules fit a path rule. This is the world where the runner-up wins.' }, rate: 1 },
        { steps: [P('Developer Lina reviews locally', '', '> Review my changes.'),
            C('Her session never loads the docs file', '', 'Looks good to me.', 'bad')],
          outcome: { ok: false, text: 'Still CI only.' }, rate: 0.5 },
        { steps: [C('Every review loads the criteria', 'Works, but YAML-only PRs carry Kotlin/TS criteria too.', 'loaded: ./CLAUDE.md (incl. criteria)', 'warn')],
          outcome: { ok: true, warn: true, text: 'Works, heavier than needed for file-type rules.' }, rate: 1 },
        { steps: [C('Claude reviews without invoking /review', '', missed, 'bad')],
          outcome: { ok: false, text: 'A skill still waits to be invoked.' }, rate: 0.7 }
      ]
    }
  };

  /* ------------------------------------------------------------ m7-s5-02 verify loaded memory first */
  var rules502 = '- Name tests "should <result> when <condition>".\n- Use FakeClock; never Thread.sleep or real time.\n- One behaviour per test.';
  var gen502 = '$ claude -p "Generate tests for CancelBookingController." --output-format json';
  var badTest = '@Test fun cancelTest() {\n  controller.cancel(id)\n  Thread.sleep(2000)    // breaks the clock rule\n  \u2026';
  var goodTest = '@Test fun `should refund fare when cancelled 24h ahead`() {\n  clock.advance(hours = 25)\n  \u2026';
  var memA = '> /memory\nMemory files loaded\n  Project memory  ./CLAUDE.md\n  (docs/testing-standards.md is NOT listed)';
  var memB = '> /memory\nMemory files loaded\n  Project memory  ./CLAUDE.md\n    @import       docs/testing-standards.md';
  var claudeMd = F('CLAUDE.md', 'project memory, committed', '@docs/testing-standards.md', 'One line, meant to pull in the testing rules.');

  var s502 = {
    id: 'm7-s5-02', who: 'Engineer', labels: LBL, lanes: true,
    worlds: [
      { id: 'A', label: 'As written', desc: '<b>Nobody has checked</b> whether the imported file loads. (In this replay a docs reorg moved it to docs/testing/standards.md.)' },
      { id: 'B', label: 'Decider changed', desc: 'A /memory check is done: <b>docs/testing-standards.md is listed as loaded</b>. The rules are in context and still followed loosely.' }
    ],
    runs: {
      A: [
        { steps: [claudeMd,
            P('Developer runs /memory in the local session', 'Option A.', '> /memory'),
            C('/memory lists the loaded files', 'The import is missing: "not loaded", not "loaded and ignored".', memA, 'ok'),
            M('What the session holds', '', [['CLAUDE.md (import line only)', 20, 'sys'], ['testing standards (import path broken)', 0, 'drop']], '', 3000),
            C('Developer fixes the import path; the generator reruns', '@docs/testing/standards.md', goodTest, 'ok')],
          outcome: { ok: true, text: '/memory shows which memory files loaded. That tells the developer which fix is needed: here, the import path.' }, rate: 1 },
        { steps: [claudeMd,
            F('Generator prompt', 'CI job', '+ two finished tests as worked examples', 'Option B.'),
            C('CI generator runs', '', gen502),
            M('What the run holds', 'The examples arrived. The standards file still did not.', [['CLAUDE.md (import line only)', 20, 'sys'], ['two example tests', 1200, 'new'], ['testing standards (never loaded)', 0, 'drop']], 'warn', 3000),
            C('Claude copies the examples\' naming, misses the clock rule', 'The examples hide the broken import for the cases they show.', badTest, 'bad')],
          outcome: { ok: false, text: 'Examples are the fix once the rules are confirmed loaded. Here they were never loaded, and the examples only mask that.' }, rate: 0.6 },
        { steps: [claudeMd,
            P('Developer asks Claude', 'Option C.', 'Quote the testing rules you were given.'),
            C('Claude answers', 'None of these came from the file. Claude filled the gap with plausible rules.', '1. Use descriptive test names.\n2. Aim for high coverage.\n3. Mock external services.', 'bad'),
            P('Developer concludes the rules are loaded', 'A wrong conclusion from a self-report.', 'Must be a prompting problem then.', 'bad')],
          outcome: { ok: false, text: 'The model\'s account of its own context is unreliable. It can paraphrase or invent rules.' }, rate: 0.4 },
        { steps: [F('CLAUDE.md', 'project memory, edited', rules502, 'Option D: the rules pasted in place of the import.'),
            C('Generator reruns', 'The output improves, but nobody learns why.', goodTest),
            C('What is left behind', 'The import is gone and docs/testing/standards.md now has a stale copy beside it. Future edits to the doc never reach Claude.', 'CLAUDE.md: pasted rules (copy 1)\ndocs/testing/standards.md (copy 2)', 'warn')],
          outcome: { ok: false, text: 'An experiment by changing config. It gives up the modular import and still does not show what was loaded.' }, rate: 0.7 }
      ],
      B: [
        { steps: [P('Developer runs /memory again', '', '> /memory'),
            C('/memory lists the loaded files', 'Already known. Nothing changes the output.', memB, 'warn'),
            C('Generator reruns', '', badTest, 'bad')],
          outcome: { ok: false, text: 'The check is done. Repeating it does not fix loose output.' }, rate: 0.6 },
        { steps: [claudeMd,
            F('Generator prompt', 'CI job', '+ two finished tests as worked examples', ''),
            M('What the run holds', 'Rules and examples, both in context.', [['CLAUDE.md', 20, 'sys'], ['testing standards (imported)', 600, 'sys'], ['two example tests', 1200, 'new']], '', 3000),
            C('Claude follows the pattern', '', goodTest, 'ok')],
          outcome: { ok: true, text: 'Rules confirmed loaded and still followed loosely: worked examples are the next step. This is the world where the runner-up wins.' }, rate: 0.9 },
        { steps: [P('Developer asks Claude to quote the rules', '', 'Quote the testing rules you were given.'),
            C('Claude paraphrases them', 'Even a good answer changes nothing in the output.', badTest, 'bad')],
          outcome: { ok: false, text: 'A self-report is not a fix.' }, rate: 0.6 },
        { steps: [C('Rules pasted inline; generator reruns', 'Same text, same place in context, same loose output.', badTest, 'bad')],
          outcome: { ok: false, text: 'The text was already loaded. Moving it does not make Claude follow it more closely.' }, rate: 0.6 }
      ]
    }
  };

  [s201, s202, s204, s205, s406, s407, s501, s502].forEach(L.add);
})();
