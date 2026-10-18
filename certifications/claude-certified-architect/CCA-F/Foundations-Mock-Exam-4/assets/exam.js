/* CCA-F Mock Exam #6 — real-exam-style harness (forked from Mock #4/#5).
   Mock #6 additions:
     · practice mode (default) grades on click; exam mode keeps answers changeable until submit
     · domain/objective tags hidden until an item is graded (the real exam shows neither)
     · runner-up + decider shown on reveal; report counts how often the runner-up caught you
   Original header:
   Differences from the Mock 1–3 engine:
     · scenario item-sets with a persistent scenario brief
     · multiple-response items ("Select TWO") with all-or-nothing grading
     · per-option rationale revealed on grade (why each distractor fails)
     · trap-pattern tag on every item
     · 120-minute exam timer
     · domain breakdown + trap breakdown at the end
   Data contract: window.EXAM = { scenarios:[{id,title,brief,domains}], questions:[
     { id, sid, domain, obj, trap, select (1|2), question, options:[{t, why}],
       answer:[idx...], explanation }
   ]}
*/
(function () {
  var EXAM = window.EXAM;
  if (!EXAM) return;
  var Q = EXAM.questions, N = Q.length;
  var byId = {}; EXAM.scenarios.forEach(function (s) { byId[s.id] = s; });
  var root = document.getElementById('exam');
  var state = [], answered = 0, correct = 0, finished = false, reported = false;
  var NUMWORD = { 2: 'TWO', 3: 'THREE', 4: 'FOUR' };
  var EXAMMODE = false;
  try { EXAMMODE = localStorage.getItem('mock-mode') === 'exam'; } catch (e) {}
  var DURATION = (EXAM.minutes || 120) * 60, left = DURATION, timerId = null, started = false;

  var FAMILIES = {
    1: { name: "Prompt where enforcement was required",
         note: "A system-prompt rule, a few-shot example or a working mode standing in for a deterministic control. If the requirement is \u201cevery time\u201d, it needs a hook, a gate or a permission \u2014 not an instruction." },
    2: { name: "Disproportionate fix",
         note: "A classifier, a subagent fleet, a custom server or an extra model pass where a description, a config change or a checklist would do. Ask what the smallest change that addresses the root cause is." },
    3: { name: "Treating the symptom, or skipping the real problem",
         note: "Filtering output, capping counts, tuning a threshold, hedging language, or quietly assuming away the decision the question is actually about." },
    4: { name: "Right idea, wrong layer",
         note: "A genuinely good practice applied at the wrong point in the stack, or aimed at a different problem than the one described. These are the hardest distractors \u2014 they are things you should do, just not here." },
    5: { name: "More context or more reasoning instead of better structure",
         note: "A bigger window, higher effort, a longer prose spec, re-reading, or asking the model to concentrate. Structure the work so the model does not have to compensate." },
    6: { name: "Unreliable proxy",
         note: "Self-reported confidence, customer sentiment, aggregate accuracy, or cross-run agreement used as a stand-in for the property you actually care about." },
    7: { name: "Losing or fabricating information",
         note: "Generic error strings, silent suppression, summarisation over exact values, coercing to the nearest enum, required fields for data that may not exist, discarding partial results." },
    8: { name: "Wrong scope or wrong home",
         note: "Project versus user scope, always-loaded versus on-demand, tool versus resource, directory versus glob, Grep versus Glob. The mechanism exists \u2014 the choice of which one is wrong." },
    9: { name: "Non-existent or misunderstood feature",
         note: "Invented flags and modes, tool_choice used for the wrong guarantee, batch requests assumed to behave like sessions, resumption assumed to refresh the world, subagents assumed to inherit context." }
  };

  function shuffle(a) {
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function eqSet(a, b) {
    if (a.length !== b.length) return false;
    var s = a.slice().sort().join(','), t = b.slice().sort().join(',');
    return s === t;
  }

  function build() {
    root.innerHTML = ''; state = []; answered = 0; correct = 0; finished = false; reported = false;
    var lastSid = null;
    Q.forEach(function (q, qi) {
      if (q.sid !== lastSid) {
        lastSid = q.sid;
        var sc = byId[q.sid];
        var head = document.createElement('div');
        head.className = 'scenario';
        head.innerHTML =
          '<div class="sc-tag">Scenario · ' + esc(sc.domains) + '</div>' +
          '<h2>' + esc(sc.title) + '</h2>' +
          '<div class="sc-brief">' + sc.brief + '</div>';
        root.appendChild(head);
      }

      var order = shuffle(q.options.map(function (_, i) { return i; }));
      state.push({ q: q, order: order, picked: [], graded: false });

      var card = document.createElement('div');
      card.className = 'q'; card.id = 'q' + qi;

      var sel = q.select || 1;
      card.innerHTML =
        '<div class="qhead">' +
          '<span class="qnum">Q' + (qi + 1) + '</span>' +
          '<span class="qdom tagged">' + esc(q.domain) + '</span>' +
          '<span class="qobj tagged">' + esc(q.obj) + '</span>' +
          (sel > 1 ? '<span class="qmulti">Select ' + (NUMWORD[sel] || sel) + '</span>' : '') +
        '</div>' +
        '<div class="qtext">' + q.question + '</div>' +
        (q.eli5 ? '<details class="eli5q"><summary>Explain this question simply</summary><div>' + q.eli5.question + '</div></details>' : '');

      var ul = document.createElement('ul');
      ul.className = 'opts';
      order.forEach(function (orig, pos) {
        var li = document.createElement('li');
        li.className = 'opt';
        li.innerHTML =
          '<span class="tick"></span>' +
          '<span class="lbl"><b>' + String.fromCharCode(65 + pos) + '.</b> ' + q.options[orig].t + '</span>' +
          '<span class="mark ok">&#10003;</span><span class="mark no">&#10007;</span>';
        li.addEventListener('click', function () {
          var s = state[qi];
          if (s.graded) return;
          if (!started) startTimer();
          if (sel === 1) {
            s.picked = [orig];
            if (!EXAMMODE) { grade(qi); return; }
            ul.querySelectorAll('.opt').forEach(function (o) { o.classList.remove('sel'); });
            li.classList.add('sel'); markAnswered(qi); return;
          }
          var at = s.picked.indexOf(orig);
          if (at >= 0) { s.picked.splice(at, 1); li.classList.remove('sel'); }
          else if (s.picked.length < sel) { s.picked.push(orig); li.classList.add('sel'); }
          if (s.picked.length === sel && !EXAMMODE) grade(qi);
          if (EXAMMODE) markAnswered(qi);
        });
        ul.appendChild(li);
      });
      card.appendChild(ul);

      var ex = document.createElement('div'); ex.className = 'explain';
      card.appendChild(ex);
      root.appendChild(card);
    });
    updateBar();
  }

  function markAnswered(qi) {
    var s = state[qi];
    document.getElementById('q' + qi).classList.toggle('picked', s.picked.length === (s.q.select || 1));
    var n = state.filter(function (x) { return x.picked.length === (x.q.select || 1); }).length;
    var sb = document.getElementById('scorebar');
    sb.innerHTML = '<span class="big">' + n + ' / ' + N + '</span><span class="pct">answered \u2014 exam mode, graded on submit</span>' +
      '<span class="clock" id="clock">' + fmt(left) + '</span>';
    sb.classList.add('show');
  }

  function deepHtml(s) {
    var d = s.q.deep; if (!d) return '';
    var letter = {}; s.order.forEach(function (orig, pos) { letter[orig] = String.fromCharCode(65 + pos); });
    var L = function (t) { return String(t).replace(/\[\[(\d)\]\]/g, function (_, i) { return letter[+i] || '?'; }); };
    var table = '<div class="dtable"><table><tr>' + d.map.head.map(function (h) { return '<th>' + L(h) + '</th>'; }).join('') + '</tr>' +
      d.map.rows.map(function (r) { return '<tr>' + r.map(function (c) { return '<td>' + L(c) + '</td>'; }).join('') + '</tr>'; }).join('') +
      '</table></div>';
    var ev = '<ol class="dev">' + d.evidence.map(function (x) {
      return '<li><q>' + L(x.quote) + '</q><div>' + L(x.means) + '</div></li>'; }).join('') + '</ol>';
    return '<details class="deep" open><summary>Think it through</summary>' +
      '<h4>1 · The premise to correct</h4><p>' + L(d.premise) + '</p>' +
      (d.diagram ? '<pre class="ddia">' + esc(d.diagram) + '</pre>' : '') +
      '<h4>2 · Mind map: ' + L(d.mapTitle) + '</h4>' + table +
      '<h4>3 · Apply it to this question</h4>' + ev +
      '<h4>4 · Rule to remember</h4><blockquote class="drule">' + L(d.rule) + '</blockquote>' +
      '<p class="dguide">Exam guide, ' + esc(d.guide.obj) + ': <i>\u201c' + esc(d.guide.quote) + '\u201d</i></p>' +
      '</details>';
  }

  function grade(qi) {
    var s = state[qi]; if (s.graded) return;
    s.graded = true; answered++;
    var card = document.getElementById('q' + qi);
    card.classList.add('graded');
    var ok = eqSet(s.picked, s.q.answer);
    if (ok) correct++;

    var lis = card.querySelectorAll('.opt');
    s.order.forEach(function (orig, pos) {
      var li = lis[pos];
      li.classList.remove('sel');
      if (s.q.answer.indexOf(orig) >= 0) li.classList.add('correct');
      if (s.picked.indexOf(orig) >= 0 && s.q.answer.indexOf(orig) < 0) li.classList.add('wrongpick');
    });

    if (s.q.select > 1 && !ok && s.picked.length) {
      var hit = s.picked.filter(function (i) { return s.q.answer.indexOf(i) >= 0; }).length;
      s.partial = hit;
    }

    var res = s.picked.length === 0
      ? '<span class="res skip">Skipped</span>'
      : (ok ? '<span class="res ok">Correct</span>'
            : '<span class="res no">Incorrect' +
              (s.partial ? ' \u2014 ' + s.partial + ' of ' + s.q.select + ' right' : '') +
              '</span>');

    var ru = s.q.runnerUp;
    s.fellForRunnerUp = !ok && s.picked.indexOf(ru) >= 0;
    var el5 = s.q.eli5;
    var rows = s.order.map(function (orig, pos) {
      var isAns = s.q.answer.indexOf(orig) >= 0;
      return '<div class="why ' + (isAns ? 'w-ok' : (orig === ru ? 'w-ru' : 'w-no')) + '">' +
        '<b>' + String.fromCharCode(65 + pos) + '.</b> ' +
        (el5 ? el5.options[orig] + '<details class="tech"><summary>Technical detail</summary>' + s.q.options[orig].why + '</details>'
             : s.q.options[orig].why) + '</div>';
    }).join('');

    card.querySelector('.explain').innerHTML =
      '<div class="eh">Explanation ' + res + '<span class="trap">Trap: ' + esc(s.q.trap) + '</span></div>' +
      (el5 ? '<div class="eli5a"><div class="wh">In plain words</div>' +
             '<p><b>The question:</b> ' + el5.question + '</p><p><b>The answer:</b> ' + el5.answer + '</p></div>' : '') +
      deepHtml(s) +
      '<div class="whys"><div class="wh">Option by option</div>' + rows + '</div>' +
      (s.q.faq ? '<details class="deep faq" open><summary>Your follow-up questions</summary>' + s.q.faq.map(function (f) {
        return '<h4>' + f.q + '</h4><p>' + f.a + '</p>'; }).join('') + '</details>' : '') +
      (el5 ? '<details class="tech exam"><summary>Exam-level explanation</summary>' : '') +
      (s.q.decider ? '<div class="decider"><b>Deciding fact:</b> ' + s.q.decider + '</div>' : '') +
      '<div class="ebody">' + s.q.explanation + '</div>' +
      (el5 ? '</details>' : '');

    updateBar();
  }

  function updateBar() {
    var done = answered === N || finished;
    var denom = done ? N : answered;
    var pct = denom ? Math.round((correct / denom) * 100) : 0;
    var sb = document.getElementById('scorebar');
    var verdict = '';
    if (done) {
      var pass = (correct / N) >= (EXAM.passMark || 0.72);
      verdict = '<span class="verdict ' + (pass ? 'pass' : 'fail') + '">' +
        (pass ? 'PASS' : 'BELOW PASS') + '</span>';
    }
    sb.innerHTML =
      '<span class="big">' + correct + ' / ' + denom + '</span>' +
      '<span class="pct">' + pct + '%' + (done ? '' : ' so far') + '</span>' +
      verdict +
      '<span class="clock" id="clock">' + fmt(left) + '</span>' +
      '<span class="bar"><span style="width:' + pct + '%"></span></span>';
    sb.classList.add('show');
    if (done && !reported && (!finished || answered === N)) { reported = true; report(); }
  }

  function fmt(s) {
    var m = Math.floor(s / 60), r = s % 60;
    return (m < 10 ? '0' : '') + m + ':' + (r < 10 ? '0' : '') + r;
  }

  function startTimer() {
    started = true;
    timerId = setInterval(function () {
      left--;
      var c = document.getElementById('clock');
      if (c) { c.textContent = fmt(left); if (left < 600) c.classList.add('low'); }
      if (left <= 0) { clearInterval(timerId); finishAll(); }
    }, 1000);
  }

  function report() {
    var dom = {}, fam = {};
    state.forEach(function (s, idx) {
      var d = s.q.domain.split('\u00b7')[0].trim();
      dom[d] = dom[d] || [0, 0]; dom[d][1]++;
      if (eqSet(s.picked, s.q.answer)) { dom[d][0]++; return; }
      var f = s.q.fam || 0;
      fam[f] = fam[f] || [];
      fam[f].push(s.q.trap + ' (Q' + (idx + 1) + ')');
    });
    var rows = Object.keys(dom).sort().map(function (d) {
      var p = Math.round(dom[d][0] / dom[d][1] * 100);
      return '<tr><td>' + esc(d) + '</td><td>' + dom[d][0] + '/' + dom[d][1] + '</td>' +
        '<td class="' + (p >= 72 ? 'g' : 'r') + '">' + p + '%</td></tr>';
    }).join('');
    var fams = Object.keys(fam).sort(function (a, b) { return fam[b].length - fam[a].length; })
      .map(function (k) {
        var F = FAMILIES[k] || { name: 'Uncategorised', note: '' };
        return '<li><b>' + fam[k].length + '\u00d7 \u2014 ' + esc(F.name) + '</b>' +
          '<div class="fnote">' + esc(F.note) + '</div>' +
          '<div class="fitems">' + fam[k].map(esc).join(' \u00b7 ') + '</div></li>';
      }).join('');
    var ms = state.filter(function (s) { return s.q.select > 1; });
    var msOk = ms.filter(function (s) { return eqSet(s.picked, s.q.answer); }).length;
    var near = ms.filter(function (s) { return s.partial === s.q.select - 1; }).length;
    var single = state.length - ms.length;
    var singleOk = correct - msOk;
    var split = '<table class="dom" style="margin-top:14px">' +
      '<tr><th>Item format</th><th>Score</th><th>%</th></tr>' +
      '<tr><td>Single answer</td><td>' + singleOk + '/' + single + '</td><td class="' +
        (singleOk / single >= 0.72 ? 'g' : 'r') + '">' + Math.round(singleOk / single * 100) + '%</td></tr>' +
      (ms.length ? '<tr><td>Multiple response</td><td>' + msOk + '/' + ms.length + '</td><td class="' +
        (msOk / ms.length >= 0.72 ? 'g' : 'r') + '">' + Math.round(msOk / ms.length * 100) + '%</td></tr>' : '') +
      '</table>' +
      (near ? '<p class="fnote" style="margin-top:6px">' + near +
        ' of your multiple-response misses were one short of the full set \u2014 near misses, not content gaps.</p>' : '');

    var wrong = state.filter(function (s) { return !eqSet(s.picked, s.q.answer) && s.picked.length; });
    var ruHits = wrong.filter(function (s) { return s.fellForRunnerUp; }).length;
    split += wrong.length ? '<p class="fnote" style="margin-top:10px"><b>' + ruHits + ' of your ' + wrong.length +
      ' wrong answers were the runner-up</b> \u2014 the option that would be right if one fact in the stem were different. ' +
      (ruHits / wrong.length >= 0.5
        ? 'Your knowledge is fine; you are missing the deciding fact. Re-read each of those stems and find the sentence the decider points to.'
        : 'Most misses were not the runner-up \u2014 those are content gaps; revise the objectives listed below.') + '</p>' : '';
    var el = document.getElementById('report');
    el.innerHTML =
      '<h2>Result breakdown</h2>' +
      '<table class="dom"><tr><th>Domain</th><th>Score</th><th>%</th></tr>' + rows + '</table>' + split +
      (fams
        ? '<h3>Trap families that caught you \u2014 revise in this order</h3><ul class="traps">' + fams + '</ul>'
        : '<p class="clean">No trap family caught you. You are reading the distractors properly.</p>');
    el.classList.add('show');
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function finishAll() {
    finished = true;
    document.body.classList.add('done');
    if (timerId) clearInterval(timerId);
    state.forEach(function (s, qi) { if (!s.graded) { if (!EXAMMODE) s.picked = []; grade(qi); } });
    updateBar();
  }

  document.addEventListener('DOMContentLoaded', function () {
    var c = document.getElementById('qcount'); if (c) c.textContent = N;
    build();
    document.querySelectorAll('.modes button').forEach(function (b) {
      var isExam = b.getAttribute('data-mode') === 'exam';
      if (isExam === EXAMMODE) b.classList.add('on');
      b.addEventListener('click', function () {
        if (started && !confirm('Switching mode restarts the paper. Continue?')) return;
        try { localStorage.setItem('mock-mode', b.getAttribute('data-mode')); } catch (e) {}
        location.reload();
      });
    });
    var sb = document.getElementById('submitBtn');
    if (sb) sb.addEventListener('click', finishAll);
    var rb = document.getElementById('resetBtn');
    if (rb) rb.addEventListener('click', function () {
      if (timerId) clearInterval(timerId);
      left = DURATION; started = false;
      document.getElementById('report').classList.remove('show');
      build(); window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });
})();
