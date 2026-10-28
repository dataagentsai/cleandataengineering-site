/* "Where does this instruction live?" simulator. No randomness: the same instruction and home always
   give the same six sessions, so a recording can be repeated. Token sizes are illustrative. */
(function () {
  // need per session: "A" = needed whenever it applies, "R" = wanted on request, absent = not needed.
  const INSTR = {
    review:  { label: "Review criteria for every change", kind: "Team · always", tone: "peri", name: "review", folder: "server/", glob: "**/*.{ts,tsx}", size: 600,
               need: { clone: "A", ci: "A", server: "A", screen: "A", restore: "A" } },
    tests:   { label: "Test conventions (test files in every folder)", kind: "Team · a file pattern", tone: "peri", name: "testing", folder: "server/", glob: "**/*.test.{ts,tsx}", size: 400,
               need: { clone: "A", ci: "A", screen: "A" } },
    screens: { label: "Screen conventions (*.screen.tsx in two folders)", kind: "Team · a file pattern", tone: "peri", name: "screens", folder: "mobile/", glob: "**/*.screen.tsx", size: 500,
               need: { screen: "A" } },
    server:  { label: "Server API conventions (only server/)", kind: "Team · one folder", tone: "peri", name: "server-api", folder: "server/", glob: "server/**", size: 500,
               need: { clone: "A", ci: "A", server: "A" } },
    runbook: { label: "Monthly staging-restore runbook", kind: "Team · on request", tone: "butter", name: "restore-staging", folder: "scripts/db/", glob: "scripts/db/**", size: 2500,
               need: { restore: "R" } },
    standup: { label: "My /standup command", kind: "Only me · on request", tone: "rose", name: "standup", folder: "server/", glob: "**/*", size: 300,
               need: { server: "R" } },
    style:   { label: "My preference: short answers, no recap", kind: "Only me · always", tone: "rose", name: "my-style", folder: "server/", glob: "**/*", size: 50,
               need: { server: "A", screen: "A", other: "A" } },
  };
  const HOMES = {
    usermd: { label: "~/.claude/CLAUDE.md", mode: "always", box: "h-usermd" },
    rootmd: { label: "Root CLAUDE.md", mode: "always", box: "h-rootmd" },
    import: { label: "@import from CLAUDE.md", mode: "always", box: "h-import" },
    folder: { label: "Folder CLAUDE.md", mode: "match", box: "h-folder" },
    rules:  { label: ".claude/rules/ + paths:", mode: "match", box: "h-rules" },
    skill:  { label: "Project skill", mode: "invoke", box: "h-skill" },
    pcmd:   { label: ".claude/commands/", mode: "invoke", box: "h-pcmd" },
    ucmd:   { label: "~/.claude/commands/", mode: "invoke", box: "h-ucmd" },
  };
  const SESSIONS = [
    { id: "clone",   label: "A new teammate clones the repo and changes <code>server/orders.ts</code> and its test", who: "mate", repo: true,
      files: ["server/orders.ts", "server/orders.test.ts"] },
    { id: "ci",      label: "CI runs <code>claude -p</code> to review a pull request on the same files", who: "ci", repo: true,
      files: ["server/orders.ts", "server/orders.test.ts"] },
    { id: "server",  label: "You fix a bug in <code>server/orders.ts</code> (your first session of the day)", who: "me", repo: true,
      files: ["server/orders.ts"] },
    { id: "screen",  label: "You build <code>packages/shared/ui/Cart.screen.tsx</code> and its test", who: "me", repo: true,
      files: ["packages/shared/ui/Cart.screen.tsx", "packages/shared/ui/Cart.screen.test.tsx"] },
    { id: "other",   label: "You open a different repository", who: "me", repo: false, files: [] },
    { id: "restore", label: "A teammate asks Claude to restore staging (then edits a seed file)", who: "mate", repo: true,
      files: ["scripts/db/seed.sql"] },
  ];
  // Verdict for every instruction × home: [chip colour, chip text, one-line note].
  const V = {
    review: {
      usermd: ["rose", "Wrong home", "Only your sessions load it. The new teammate and the CI review never see the criteria."],
      rootmd: ["mint", "Right fit", "Every clone and every CI run loads it. Always-on team standards live here."],
      import: ["mint", "Also right", "Loads exactly like the root file, from its own file. Tidy once the criteria grow."],
      folder: ["butter", "Partly", "Loads only for server work. Screen work and the seed-file change miss the criteria."],
      rules:  ["butter", "Works, but", "Only TypeScript files match, so the SQL change slips past. A glob for everything is CLAUDE.md with extra steps."],
      skill:  ["rose", "Only when invoked", "Standards that must always apply sit unused until someone remembers the skill."],
      pcmd:   ["rose", "Only when typed", "Teammates and CI get the criteria only if they run the command."],
      ucmd:   ["rose", "Wrong home", "Personal and on request: teammates and CI never get it, and you only when you type it."],
    },
    tests: {
      usermd: ["rose", "Wrong home", "Your sessions follow it; the new teammate's and CI's don't. User-level files are not in git."],
      rootmd: ["butter", "Works, but", "Everyone gets it, but it loads into every session, including ones with no test file."],
      import: ["butter", "Works, but", "A tidier file with the same loading as the root: every session pays for it."],
      folder: ["butter", "Partly", "A note on server/ misses the screen test in packages/shared/ui/."],
      rules:  ["mint", "Right fit", "Loads whenever a test file is touched, in any folder, and stays out of the rest."],
      skill:  ["rose", "Only when invoked", "Tests written without invoking the skill miss the conventions."],
      pcmd:   ["rose", "Only when typed", "Conventions that should apply by themselves now wait for someone to type a command."],
      ucmd:   ["rose", "Wrong home", "Only you can run it, and only when you remember to."],
    },
    screens: {
      usermd: ["rose", "Wrong home", "Only your sessions, and every project you open, even ones with no screens."],
      rootmd: ["butter", "Works, but", "Loads in server work and in CI too, where no screen is touched."],
      import: ["butter", "Works, but", "Same as the root file: loaded everywhere."],
      folder: ["rose", "Misses files", "The screen you built lives in packages/shared/ui/, outside mobile/. The folder note never loads."],
      rules:  ["mint", "Right fit", "Loads for any *.screen.tsx file, in any folder, and nowhere else."],
      skill:  ["rose", "Only when invoked", "Screens built without the skill miss the conventions."],
      pcmd:   ["rose", "Only when typed", "Conventions should load by themselves, not wait for a command."],
      ucmd:   ["rose", "Wrong home", "Personal and on request: nobody else ever gets it."],
    },
    server: {
      usermd: ["rose", "Wrong home", "The teammate and CI working on server/ never load it."],
      rootmd: ["butter", "Works, but", "Loads for screen work and restores too, where it doesn't apply."],
      import: ["butter", "Works, but", "Same as the root file: loaded everywhere."],
      folder: ["mint", "Right fit", "Everything server sits in one folder, so a CLAUDE.md there loads exactly when needed."],
      rules:  ["mint", "Also right", "Does the same job. For one folder, a folder CLAUDE.md is the simpler home."],
      skill:  ["rose", "Only when invoked", "Server work done without the skill misses the conventions."],
      pcmd:   ["rose", "Only when typed", "Conventions should load by themselves, not wait for a command."],
      ucmd:   ["rose", "Wrong home", "Personal and on request: nobody else ever gets it."],
    },
    runbook: {
      usermd: ["rose", "Wrong home", "The teammate who asks for the restore doesn't have it, and you carry it into every project."],
      rootmd: ["butter", "Works, but", "Found when asked, but the long runbook fills every session's context, every day."],
      import: ["butter", "Works, but", "Same cost: an @import loads with the root file, every session."],
      folder: ["rose", "Arrives late", "Loads only once Claude opens a file in scripts/db/. The request comes first."],
      rules:  ["rose", "Arrives late", "A restore starts with a request, not a file. The rule loads after Claude has started."],
      skill:  ["mint", "Right fit", "Shared through git and loaded only when someone asks for a restore. No cost the rest of the month."],
      pcmd:   ["mint", "Works", "Shared and on request too. A skill adds frontmatter such as allowed-tools and context: fork."],
      ucmd:   ["rose", "Wrong home", "Only you can run it; the teammate who needs it can't."],
    },
    standup: {
      usermd: ["butter", "Works, but", "Not a command: there is no /standup to type, and the steps load into every one of your sessions."],
      rootmd: ["rose", "Wrong home", "Teammates and CI load your standup steps, and they don't follow you to other repos."],
      import: ["rose", "Wrong home", "Teammates and CI load your standup steps, and they don't follow you to other repos."],
      folder: ["rose", "Wrong home", "Committed for everyone, and loaded only during server/ work."],
      rules:  ["rose", "Wrong home", "A rule is reading material for the whole team, not a command you run."],
      skill:  ["rose", "Wrong home", "Teammates see it, and it isn't there when you open another repo."],
      pcmd:   ["rose", "Wrong home", "Clutters teammates' command lists and stays behind when you open another repo."],
      ucmd:   ["mint", "Right fit", "Yours alone, in every repo, loaded only when you type /standup."],
    },
    style: {
      usermd: ["mint", "Right fit", "Your preference, in every project, and nobody else's sessions change."],
      rootmd: ["rose", "Wrong home", "Teammates and the CI review now answer your way, and your other repos don't."],
      import: ["rose", "Wrong home", "Teammates and the CI review now answer your way, and your other repos don't."],
      folder: ["rose", "Wrong home", "Shared with the team, and only in server/ at that."],
      rules:  ["rose", "Wrong home", "Committed, so every teammate and CI run gets your preference."],
      skill:  ["rose", "Only when invoked", "A preference you must invoke isn't a preference, and the team sees the skill."],
      pcmd:   ["rose", "Wrong home", "Shared with the team, and you'd have to type it every session."],
      ucmd:   ["butter", "Works, but", "Yours and everywhere, but you'd type it every session. A preference should just load."],
    },
  };

  const $ = (id) => document.getElementById(id);
  let ins = "screens", home = "folder";

  function where(I, h) {
    return {
      usermd: "a section in <code>~/.claude/CLAUDE.md</code> on your laptop",
      rootmd: "a section in the committed root <code>CLAUDE.md</code>",
      import: `<code>docs/${I.name}.md</code>, pulled in by the line <code>@docs/${I.name}.md</code> in the root <code>CLAUDE.md</code>`,
      folder: `<code>${I.folder}CLAUDE.md</code>, committed`,
      rules:  `<code>.claude/rules/${I.name}.md</code> with <code>paths: ${I.glob}</code>, committed`,
      skill:  `<code>.claude/skills/${I.name}/SKILL.md</code>, committed`,
      pcmd:   `<code>.claude/commands/${I.name}.md</code>, committed`,
      ucmd:   `<code>~/.claude/commands/${I.name}.md</code> on your laptop`,
    }[h];
  }

  function globMatch(glob, f) {
    if (glob === "**/*") return true;
    if (glob.endsWith("/**")) return f.startsWith(glob.slice(0, -2));
    const alts = glob.match(/\{([^}]+)\}/);
    const pats = alts ? alts[1].split(",").map((a) => glob.replace(alts[0], a)) : [glob];
    return pats.some((p) => f.endsWith(p.replace("**/*", "")));
  }

  // Is the file present in this session, and is it loaded by itself? Returns [present, loaded, why].
  function load(I, h, s) {
    const mine = s.who === "me";
    const whoNot = s.who === "ci" ? "the CI runner has no home-folder config" : "it isn't on their laptop";
    switch (h) {
      case "usermd": return mine ? [1, 1, "your home-folder memory loads in all your sessions"] : [0, 0, whoNot];
      case "ucmd":   return mine ? [1, 0, "on your laptop, in every repo"] : [0, 0, whoNot];
      case "rootmd":
      case "import": return s.repo ? [1, 1, "it loads with the repo"] : [0, 0, "it lives in the other repo"];
      case "folder": {
        if (!s.repo) return [0, 0, "it lives in the other repo"];
        const f = s.files.find((x) => x.startsWith(I.folder));
        return f ? [1, 1, `Claude worked in ${I.folder}`] : [1, 0, s.files.length ? `nothing in ${I.folder} was touched` : "no file was open yet"];
      }
      case "rules": {
        if (!s.repo) return [0, 0, "it lives in the other repo"];
        const f = s.files.find((x) => globMatch(I.glob, x));
        return f ? [1, 1, `<code>${f.split("/").pop()}</code> matches <code>${I.glob}</code>`] : [1, 0, s.files.length ? `no touched file matches <code>${I.glob}</code>` : "no file was open yet"];
      }
      default: return s.repo ? [1, 0, "in the repo, loads only when invoked"] : [0, 0, "it lives in the other repo"];
    }
  }

  // One session's outcome: [class, chip text, explanation].
  function outcome(k, h, s) {
    const I = INSTR[k], H = HOMES[h], need = I.need[s.id];
    const [present, loaded, why] = load(I, h, s);
    const personal = k === "standup" || k === "style";
    if (need === "A") {
      if (loaded) return ["hit", "Got it", why];
      if (present && H.mode === "invoke") return ["miss", "Missed", "it waits for someone to invoke it"];
      return ["miss", "Missed", why];
    }
    if (need === "R") {
      if (present && H.mode === "invoke") return ["hit", "Ready", `runs when asked: ${why}`];
      if (loaded && H.mode === "always") return ["hit", "Ready", `Claude finds the steps in memory: ${why}`];
      if (k === "runbook" && H.mode === "match") return ["miss", "Too late", "the request comes before any file in scripts/db/ is open"];
      if (k === "standup" && H.mode === "match" && loaded) return ["miss", "Missed", "a rule is text to follow, not a /standup you can run"];
      return ["miss", "Missed", why];
    }
    if (loaded) return ["noise", "Extra load", personal && s.who !== "me" ? `your preference now applies to them: ${why}` : `not needed here, but ${why}`];
    if (present && personal && s.who !== "me" && s.who !== "ci" && H.mode === "invoke") return ["noise", "Clutter", "it shows up in their list of commands"];
    return ["quiet", "Not needed", present && H.mode !== "always" ? "and not loaded" : why];
  }

  function buttons(boxId, items, current, set) {
    const box = $(boxId);
    box.innerHTML = "";
    Object.entries(items).forEach(([k, v]) => {
      const x = document.createElement("button");
      x.className = "btn" + (k === current ? " on" : "");
      x.innerHTML = v.label + (v.kind ? ` <span class="chip ${v.tone}">${v.kind}</span>` : "");
      x.onclick = () => { set(k); draw(); };
      box.appendChild(x);
    });
  }

  function highlight() {
    Object.values(HOMES).forEach((H) => {
      const r = $(H.box);
      if (r) r.setAttribute("stroke-width", H.box === HOMES[home].box ? "4" : "1.5");
    });
  }

  const CHIP = { hit: "mint", miss: "rose", noise: "butter", quiet: "" };

  function draw() {
    buttons("sim-i", INSTR, ins, (k) => (ins = k));
    buttons("sim-h", HOMES, home, (k) => (home = k));
    highlight();
    const I = INSTR[ins];
    $("sim-where").innerHTML = `The instruction now lives in ${where(I, home)}.`;
    let rows = "", hit = 0, miss = 0, noise = 0, tokens = 0, needed = 0;
    SESSIONS.forEach((s) => {
      const [c, chip, why] = outcome(ins, home, s);
      if (I.need[s.id]) needed++;
      if (c === "hit") hit++;
      if (c === "miss") miss++;
      if (c === "noise") { noise++; if (chip === "Extra load") tokens += I.size; }
      rows += `<tr class="r-${c}"><td>${s.label}</td><td><span class="chip ${CHIP[c]}">${chip}</span> ${why}</td></tr>`;
    });
    $("sim-rows").innerHTML = `<tr><th>Session</th><th>What happened to this instruction</th></tr>` + rows;
    $("sim-tally").innerHTML = `Needed in <b>${needed}</b> of 6 sessions · got it in <b>${hit}</b> · missed in <b>${miss}</b> · loaded or shown where not wanted in <b>${noise}</b>` +
      (tokens ? `<br>Context spent where it wasn't needed: about <b>${tokens.toLocaleString("en-US")}</b> tokens` : "");
    const [c, v, note] = V[ins][home];
    $("sim-verdict").className = "box " + c;
    $("sim-verdict").innerHTML = `<span class="chip ${c}">${v}</span> ${note}`;
  }

  window.addEventListener("DOMContentLoaded", draw);
})();
