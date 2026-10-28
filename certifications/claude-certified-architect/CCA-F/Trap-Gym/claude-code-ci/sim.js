/* Claude Code in CI simulator. Deterministic: the same toggles always replay the same pull request, the
   same CI log and the same five runs, so a recording can be repeated. The pull request has six planted
   issues; which ones the review catches follows exam guide 3.6 (CLAUDE.md gives the team's standards; an
   independent instance reviews better than the session that generated the code). Illustrative, not measured. */
(function () {
  const TOGGLES = {
    p:      { label: "-p / --print", on: "On", off: "Off" },
    json:   { label: "--output-format json", on: "On", off: "Off" },
    schema: { label: "--json-schema findings.schema.json", on: "On", off: "Off" },
    md:     { label: "CLAUDE.md with testing standards and review criteria", on: "Present", off: "Absent" },
    indep:  { label: "Who reviews", on: "An independent instance", off: "The session that wrote the code" },
  };
  // The pull request: new endpoint code plus tests that Claude generated earlier in the job.
  const ISSUES = [
    { k: "generic", at: "api/orders.py:42", sev: "high", msg: "SQL query built by string concatenation" },
    { k: "generic", at: "api/orders.py:77", sev: "medium", msg: "No check for a missing customer before use" },
    { k: "standard", at: "tests/test_orders.py:12", sev: "low", msg: "Uses the old mock factory; the team's standard is builders" },
    { k: "standard", at: "tests/test_client.py:1", sev: "low", msg: "Tests the generated API client, which the team leaves untested on purpose" },
    { k: "blind", at: "tests/test_orders.py:30", sev: "medium", msg: "Asserts on the mock's return value, not on the result" },
    { k: "blind", at: "tests/test_refunds.py:18", sev: "medium", msg: "Named “rejects over limit” but asserts the success path" },
  ];
  const WHY_MISSED = {
    standard: "no CLAUDE.md, so the team's testing standards were unknown",
    blind: "the session that wrote this test reviewed it, and read its own reasoning as settled",
  };
  // Five runs of the same job with JSON output but no schema: the envelope parses, the findings inside drift.
  const DRIFT = [
    [true, "run 1: posted"],
    [true, "run 2: posted"],
    [false, "run 3: KeyError: 'file'  (this time Claude named the key \"location\")"],
    [true, "run 4: posted"],
    [false, "run 5: no findings array found  (a sentence came after the JSON block)"],
  ];

  const $ = (id) => document.getElementById(id);
  const st = { p: false, json: false, schema: false, md: false, indep: false };
  let timers = [];

  function toggles() {
    const box = $("sim-k");
    box.innerHTML = "";
    Object.entries(TOGGLES).forEach(([k, v]) => {
      const row = document.createElement("div");
      row.className = "tg";
      row.innerHTML = `<span class="tl">${v.label}</span>`;
      [[true, v.on], [false, v.off]].forEach(([val, text]) => {
        const b = document.createElement("button");
        b.className = "btn" + (st[k] === val ? " on" : "");
        b.textContent = text;
        b.onclick = () => { st[k] = val; draw(); };
        row.appendChild(b);
      });
      box.appendChild(row);
    });
  }

  function highlight() {
    const set = (id, on) => { const r = $(id); if (r) { r.setAttribute("stroke-width", on ? "4" : "1.5"); r.setAttribute("stroke-dasharray", on ? "" : "6 4"); } };
    set("box-p", st.p);
    set("box-json", st.json && st.schema);
    set("box-md", st.md);
    set("box-post", st.p && st.json && st.schema);
    set("box-indep", st.indep);
    const g = $("box-gen");
    if (g) g.setAttribute("fill", st.indep ? "#ffffff" : "#fbf0f5");
  }

  function cmd(prompt) {
    let c = "claude" + (st.p ? " -p" : "") + ` "${prompt}"`;
    if (st.json) c += " \\\n    --output-format json";
    if (st.schema) c += " \\\n    --json-schema \"$(cat findings.schema.json)\"";
    return c;
  }

  // Each log line: [kind, text]. kinds: cmd, out, ok, err, note, step.
  function log(caught) {
    const L = [];
    const step = (t) => L.push(["step", `== step: ${t} ==`]);
    if (st.indep) {
      step("generate tests");
      L.push(["cmd", "$ " + cmd("Write tests for the new endpoints in this PR")]);
      L.push(["out", st.p ? "tests written: 3 files" : "(interactive session opened)"]);
      if (!st.p) return hang(L, step);
      step("review (fresh instance: gets the diff, not the generation turns)");
      L.push(["cmd", "$ " + cmd("Review this PR diff and report findings")]);
    } else {
      step("generate tests, then review, in one session");
      L.push(["cmd", "$ " + cmd("Write tests for the new endpoints, then review the whole PR")]);
      if (!st.p) return hang(L, step);
    }
    if (st.md) L.push(["note", "# CLAUDE.md loaded: testing standards, fixtures, review criteria"]);
    else L.push(["note", "# no CLAUDE.md in the repository: review uses general checks only"]);

    if (!st.json) {
      L.push(["out", "## Review findings"]);
      L.push(["out", "**api/orders.py**: the query on line 42 builds SQL from strings, which"]);
      L.push(["out", "risks injection. I'd also look at line 77, where the customer may be..."]);
      L.push(["out", "Overall the change looks solid. A few smaller notes:"]);
      L.push(["ok", "exit 0"]);
      if (st.schema) L.push(["note", "# The guide pairs --json-schema with --output-format json. Without the JSON format, the script still reads prose."]);
      step("post inline comments");
      L.push(["cmd", "$ python post_comments.py review.out"]);
      L.push(["err", "json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)"]);
      L.push(["err", "0 comments posted"]);
      return L;
    }
    if (!st.schema) {
      L.push(["out", '{"type": "result", "result": "Here are the findings:\\n```json\\n[{\\"file\\": ...'] );
      L.push(["note", "# The envelope is JSON, but the findings inside \"result\" are text Claude wrote, in whatever shape it chose"]);
      step("post inline comments (last five pull requests)");
      L.push(["cmd", "$ python post_comments.py review.json"]);
      DRIFT.forEach(([ok, t]) => L.push([ok ? "ok" : "err", t + (ok ? ` ${caught.length} comments` : "")]));
      return L;
    }
    L.push(["out", '{"findings": [{"file": "api/orders.py", "line": 42, "severity": "high",'] );
    L.push(["out", '  "message": "SQL query built by string concatenation"}, ...]}'] );
    L.push(["note", "# (result trimmed to the findings) every run matches findings.schema.json"]);
    step("post inline comments");
    L.push(["cmd", "$ python post_comments.py review.json"]);
    L.push(["ok", `${caught.length} inline comments posted`]);
    return L;
  }

  function hang(L, step) {
    L.push(["out", "(Claude answers, then waits at the prompt for the next message)"]);
    L.push(["note", "# nobody is there to type"]);
    L.push(["err", "45:00  the job exceeded its time limit and was cancelled"]);
    step("post inline comments");
    L.push(["err", "skipped: an earlier step was cancelled"]);
    return L;
  }

  function verdict(caught) {
    const n = caught.length;
    if (!st.p) return { v: "Breaks: hangs", c: "rose", note: "Without -p, Claude Code opens an interactive session and waits for someone to type. Nobody is there, so the job sits until the time limit cancels it. None of the other settings get a chance to matter." };
    if (!st.json) return { v: "Breaks: unparseable", c: "rose", note: "It runs unattended now, but the findings come back as prose. The script that posts inline comments can't parse it, so nothing reaches the pull request." + (st.schema ? " A schema alone doesn't change that: the guide pairs it with --output-format json." : "") };
    const q = quality(n);
    if (!st.schema) return { v: "Only usually works", c: "butter", note: `The JSON envelope parses, but the shape of the findings inside drifts, so 3 of 5 runs posted and 2 broke the script. --json-schema fixes the shape. ${q}` };
    if (st.md && st.indep) return { v: "Best fit (exam answer)", c: "mint", note: "Runs unattended, every run parses, findings land as inline comments, the review knows the team's standards, and a fresh instance catches the generated tests' mistakes: 6 of 6." };
    if (st.md) return { v: "Self-review blind spot", c: "butter", note: "A reliable pipeline with the team's standards, but the session that wrote the tests reviewed them. It still holds its own reasoning, so it missed both wrong assertions: 4 of 6." };
    if (st.indep) return { v: "Misses team standards", c: "butter", note: "A reliable pipeline and fresh eyes, but no CLAUDE.md, so it can't know the team uses builders or leaves the generated client untested: 4 of 6." };
    return { v: "Weak review", c: "rose", note: "The pipeline is reliable, but the review is generic and checks its own work: only the 2 general issues of 6 are caught." };
  }
  function quality(n) {
    if (n === 6) return "On the runs that posted, the review itself caught 6 of 6.";
    const gaps = [];
    if (!st.md) gaps.push("no CLAUDE.md");
    if (!st.indep) gaps.push("self-review");
    return `On the runs that posted, it caught ${n} of 6 (${gaps.join(" and ")}).`;
  }

  function draw() {
    toggles();
    highlight();
    timers.forEach(clearTimeout);
    timers = [];
    const caught = ISSUES.filter((i) => i.k === "generic" || (i.k === "standard" && st.md) || (i.k === "blind" && st.indep));
    const lines = log(caught);
    const pre = $("sim-log");
    pre.innerHTML = "";
    lines.forEach(([k, t], i) => {
      const s = document.createElement("span");
      s.className = "l-" + k;
      s.textContent = t + "\n";
      pre.appendChild(s);
      timers.push(setTimeout(() => s.classList.add("show"), 90 * i));
    });
    // The pull request view.
    const posted = st.p && st.json;
    const pr = $("sim-pr");
    let h = "";
    if (!posted) {
      h = `<p class="none">No comments on the pull request.</p>`;
    } else {
      h = (st.schema ? "" : `<p class="none">Posted on 3 of 5 runs. On the other 2, nothing.</p>`) +
        caught.map((i) => `<div class="cm"><code>${i.at}</code> <span class="chip ${i.sev === "high" ? "rose" : i.sev === "medium" ? "butter" : "peri"}">${i.sev}</span> ${i.msg}</div>`).join("");
    }
    const missed = ISSUES.filter((i) => !caught.includes(i));
    if (missed.length && st.p) h += `<p class="none" style="margin-top:10px">Planted issues the review missed:</p>` + missed.map((i) => `<div class="cm miss"><code>${i.at}</code> ${i.msg}<br><small>Missed because ${WHY_MISSED[i.k]}.</small></div>`).join("");
    pr.innerHTML = h;
    const n = st.p ? caught.length : 0;
    $("sim-q-n").textContent = !st.p ? "no review ran" : st.json ? `${n} of 6` : `${n} of 6, but none posted`;
    $("sim-q").style.width = (100 * n / 6) + "%";
    $("sim-q").className = n === 6 ? "full" : "";
    const v = verdict(caught);
    $("sim-verdict").className = "box " + v.c;
    $("sim-verdict").innerHTML = `<span class="chip ${v.c}">${v.v}</span> ${v.note}`;
  }

  window.addEventListener("DOMContentLoaded", draw);
})();
