/* AzureAIEngineer practice engine.
   Item types: single · multi · yesno · order · code · solution (problem/solution series).
   Modes: practice (explain after each answer) and exam (timed, scored at the end; solution items lock once answered). */
(function () {
  var BANK = window.BANK, KEY = 'aze.' + BANK.id + (BANK.v ? '.v' + BANK.v : '');
  var store = { get: function (k, d) { try { var v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } },
                set: function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} } };
  var M0 = BANK.mode || 'practice';
  var state = store.get(KEY, { mode: M0, answers: {}, started: M0 === 'exam' ? Date.now() : null, finished: false });
  var host = document.getElementById('bank');
  var L = 'ABCDEFGH';
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function md(s) { return esc(s).replace(/`([^`]+)`/g, '<span class="k">$1</span>').replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>'); }
  function save() { store.set(KEY, state); }

  // ---- scoring ----
  function isAnswered(q) { var a = state.answers[q.id]; if (a === undefined) return false;
    if (q.type === 'yesno') return a.length === q.statements.length && a.every(function (x) { return x !== null; });
    if (q.type === 'code') return a.length === q.blanks.length && a.every(function (x) { return x !== null; });
    if (q.type === 'multi') return a.length === q.pick;
    if (q.type === 'order') return a.length === q.answer.length;
    return true; }
  function points(q) { // returns [earned, possible]
    var a = state.answers[q.id];
    if (q.type === 'yesno') return [a ? q.statements.filter(function (s, i) { return a[i] === s.answer; }).length : 0, q.statements.length];
    if (q.type === 'code') return [a ? q.blanks.filter(function (b, i) { return a[i] === b.answer; }).length : 0, q.blanks.length];
    if (q.type === 'multi') return [a ? a.filter(function (x) { return q.answer.indexOf(x) >= 0; }).length : 0, q.answer.length];
    if (q.type === 'order') return [a && a.join() === q.answer.join() ? 1 : 0, 1];
    if (q.type === 'solution') return [a === q.answer ? 1 : 0, 1];
    return [a === q.answer ? 1 : 0, 1]; }
  function fullyRight(q) { var p = points(q); return p[0] === p[1]; }
  var reveal = function (q) { return state.mode === 'practice' ? isAnswered(q) : state.finished; };

  // ---- rendering ----
  function header() {
    var tot = 0, got = 0, done = 0;
    BANK.items.forEach(function (q) { var p = points(q); tot += p[1]; if (isAnswered(q)) { done++; got += p[0]; } });
    var timer = state.mode === 'exam' ? '<span class="timer" id="timer"></span>' : '';
    return '<div class="bankbar"><div class="modes">' +
      '<button data-mode="practice" class="' + (state.mode === 'practice' ? 'on' : '') + '">Practice mode</button>' +
      '<button data-mode="exam" class="' + (state.mode === 'exam' ? 'on' : '') + '">Exam mode · ' + BANK.minutes + ' min</button></div>' +
      '<span class="score">' + done + '/' + BANK.items.length + ' answered' + (reveal(BANK.items[0]) || state.mode === 'practice' ? ' · ' + got + '/' + tot + ' points' : '') + '</span>' + timer +
      (state.mode === 'exam' && !state.finished ? '<button class="act" id="finish">Finish and score</button>' : '') +
      '<button class="ghost" id="reset">Reset</button></div>' +
      (state.mode === 'exam' && state.finished ? summary() : '');
  }
  function summary() {
    var by = {}, tot = 0, got = 0;
    BANK.items.forEach(function (q) { var p = points(q); var k = q.skill || 'General'; by[k] = by[k] || [0, 0]; by[k][0] += p[0]; by[k][1] += p[1]; tot += p[1]; got += p[0]; });
    var scaled = Math.round(got / tot * 1000);
    return '<div class="result ' + (scaled >= 700 ? 'pass' : 'fail') + '"><b>Scaled estimate: ' + scaled + ' / 1000</b> · pass mark 700 · ' + got + ' of ' + tot + ' points' +
      '<div class="tbl"><table><thead><tr><th>Skill</th><th>Points</th></tr></thead><tbody>' +
      Object.keys(by).map(function (k) { return '<tr><td>' + esc(k) + '</td><td>' + by[k][0] + ' / ' + by[k][1] + '</td></tr>'; }).join('') +
      '</tbody></table></div><p class="note">A rough estimate: Microsoft scales scores per exam, so this is a direction, not a prediction.</p></div>';
  }
  function body(q, n) {
    var a = state.answers[q.id], show = reveal(q), locked = show || (state.mode === 'exam' && q.type === 'solution' && a !== undefined) || state.finished;
    var h = '<article class="q" id="Q-' + q.id + '"><div class="qtop"><span class="chip">Q' + n + '</span><span class="fmt">' + ({ single: 'Choose one', multi: 'Choose ' + (q.pick === 2 ? 'two' : 'three'), yesno: 'Yes / No for each statement', order: 'Put in order', code: 'Complete the code', solution: 'Problem and solution' }[q.type]) + '</span>' + (q.case && BANK.cases && BANK.cases[q.case] ? '<a class="chip" href="#CASE-' + q.case + '">Case: ' + esc(BANK.cases[q.case].short) + '</a>' : '') +
      (q.type === 'solution' ? '<span class="lockn">Can\'t be revisited in the real exam</span>' : '') + '</div>';
    if (q.scenario) h += '<div class="scen">' + md(q.scenario) + '</div>';
    h += '<p class="stem">' + md(q.stem) + '</p>';
    if (q.type === 'single' || q.type === 'solution' || q.type === 'multi') {
      var opts = q.type === 'solution' ? ['Yes', 'No'] : q.options;
      var ans = q.type === 'solution' ? (q.answer ? 0 : 1) : q.answer;
      var picks = q.type === 'multi' ? (a || []) : (q.type === 'solution' ? (a === undefined ? [] : [a ? 0 : 1]) : (a === undefined ? [] : [a]));
      h += '<div class="opts">' + opts.map(function (o, k) {
        var right = q.type === 'multi' ? ans.indexOf(k) >= 0 : k === ans, mine = picks.indexOf(k) >= 0, cls = '', tags = '';
        if (show) { if (right) cls += ' correct'; if (mine && !right) cls += ' wrongpick'; if (q.runner === k && !right) cls += ' runner';
          if (mine) tags += '<span class="chip t-pick">Your pick</span>'; if (right) tags += '<span class="chip t-ok">Correct</span>'; if (q.runner === k && !right) tags += '<span class="chip t-run">Runner-up</span>'; }
        else if (mine) cls += ' picked';
        return '<button class="opt' + cls + '" data-q="' + q.id + '" data-k="' + k + '"' + (locked ? ' disabled' : '') + '><span class="L">' + (q.type === 'multi' ? '☐' : L[k]) + '</span><span>' + md(o) + '</span><span class="tagz">' + tags + '</span></button>';
      }).join('') + '</div>';
    }
    if (q.type === 'yesno') {
      h += '<div class="tbl"><table class="yn"><thead><tr><th>Statement</th><th>Yes</th><th>No</th></tr></thead><tbody>' + q.statements.map(function (s, i) {
        var v = a ? a[i] : null, c = function (val) { var on = v === val, cls = on ? ' on' : ''; if (show) { if (s.answer === val) cls += ' ok'; else if (on) cls += ' bad'; }
          return '<td><button class="yb' + cls + '" data-yn="' + q.id + '" data-i="' + i + '" data-v="' + val + '"' + (locked ? ' disabled' : '') + '>' + (val ? 'Yes' : 'No') + '</button></td>'; };
        return '<tr><td>' + md(s.text) + (show ? '<div class="why">' + md(s.why) + '</div>' : '') + '</td>' + c(true) + c(false) + '</tr>';
      }).join('') + '</tbody></table></div>';
    }
    if (q.type === 'order') {
      var cur = a || [];
      h += '<div class="ord"><div class="pool"><h4>Actions</h4>' + q.pool.map(function (p, k) { var used = cur.indexOf(k) >= 0;
          return '<button class="pi" data-ord="' + q.id + '" data-k="' + k + '"' + (used || locked ? ' disabled' : '') + '>' + md(p) + '</button>'; }).join('') + '</div>' +
        '<div class="seq"><h4>Your sequence (' + q.answer.length + ' steps)</h4>' + (cur.length ? cur.map(function (k, i) { var ok = show && q.answer[i] === k;
          return '<div class="si' + (show ? (ok ? ' ok' : ' bad') : '') + '">' + (i + 1) + '. ' + md(q.pool[k]) + '</div>'; }).join('') : '<p class="note">Select actions in order.</p>') +
        (cur.length && !locked ? '<button class="ghost" data-undo="' + q.id + '">Undo last</button>' : '') +
        (show ? '<div class="si ok-list"><b>Correct order:</b> ' + q.answer.map(function (k, i) { return (i + 1) + '. ' + md(q.pool[k]); }).join(' → ') + '</div>' : '') + '</div></div>';
    }
    if (q.type === 'code') {
      var parts = q.code.split(/\[\[(\d)\]\]/);
      h += '<pre class="code">' + parts.map(function (p, i) { if (i % 2 === 0) return esc(p); var b = +p, bl = q.blanks[b], v = a ? a[b] : null;
        var cls = show ? (v === bl.answer ? ' ok' : ' bad') : '';
        return '<select class="blank' + cls + '" data-code="' + q.id + '" data-b="' + b + '"' + (locked ? ' disabled' : '') + '><option value="">▼ choose</option>' +
          bl.options.map(function (o, k) { return '<option value="' + k + '"' + (v === k ? ' selected' : '') + '>' + esc(o) + '</option>'; }).join('') + '</select>'; }).join('') + '</pre>';
      if (show) h += '<div class="box"><h4>Correct</h4><ul>' + q.blanks.map(function (bl, i) { return '<li>Blank ' + (i + 1) + ': <span class="k">' + esc(bl.options[bl.answer]) + '</span> — ' + md(bl.why) + '</li>'; }).join('') + '</ul></div>';
    }
    if (show) h += explain(q);
    else if (state.mode === 'practice' && (q.type === 'multi' || q.type === 'yesno' || q.type === 'code' || q.type === 'order')) h += '<p class="note">Complete every part to see the explanation.</p>';
    return h + '</article>';
  }
  function explain(q) {
    var p = points(q), ok = p[0] === p[1], t = q.think;
    var v = '<div class="verdict ' + (ok ? 'ok' : 'no') + '">' + (ok ? 'Correct.' : 'Not this time: ' + p[0] + ' of ' + p[1] + '.') + (q.runnerWhy ? ' Runner-up: ' + md(q.runnerWhy) : '') + '</div>';
    var tabs = '<div class="xtabs"><button class="on" data-x="0">Think it through</button><button data-x="1">ELI5</button><button data-x="2">Rule</button></div>';
    var think = '<div class="xp" data-xp="0"><div class="box"><h4>1 · Premise to correct</h4><p>' + md(t.premise) + '</p></div>' +
      (t.map ? '<div class="box"><h4>2 · Mind map</h4><div class="tbl"><table><thead><tr><th>You observe</th><th>Where the fault is</th><th>Fix</th></tr></thead><tbody>' +
        t.map.map(function (r) { return '<tr><td>' + md(r[0]) + '</td><td>' + md(r[1]) + '</td><td>' + md(r[2]) + '</td></tr>'; }).join('') + '</tbody></table></div></div>' : '') +
      (t.apply ? '<div class="box"><h4>3 · Apply it to the stem</h4>' + t.apply.map(function (x) { return '<blockquote class="quote">' + md(x[0]) + '</blockquote><p>' + md(x[1]) + '</p>'; }).join('') + '</div>' : '') + '</div>';
    var eli = '<div class="xp" data-xp="1" hidden><div class="box"><p>' + md(q.eli5) + '</p></div></div>';
    var rule = '<div class="xp" data-xp="2" hidden><div class="box"><h4>4 · Rule to remember</h4><p>' + md(t.rule) + '</p><p class="note">Exam guide: ' + md(t.guide) + '</p>' +
      (q.learn ? '<p class="note">Find it on Microsoft Learn (open during the exam): <a href="' + esc(q.learn) + '" target="_blank" rel="noopener">' + esc(q.learn.replace('https://learn.microsoft.com/en-us/', '')) + '</a></p>' : '') + '</div></div>';
    return '<div class="expl">' + v + tabs + think + eli + rule + '</div>';
  }
  function caseBlock(id) {
    var c = (BANK.cases || {})[id]; if (!c) return '';
    return '<section class="case" id="CASE-' + id + '"><div class="eyebrow"><b>Case study</b>' + esc(c.title) + '</div>' +
      '<p class="note">The next questions use this case. Open each tab; in the real exam the case stays available while you answer its questions.</p>' +
      '<div class="ctabs">' + c.tabs.map(function (t, k) { return '<button data-ct="' + id + '" data-k="' + k + '"' + (k === 0 ? ' class="on"' : '') + '>' + esc(t.name) + '</button>'; }).join('') + '</div>' +
      c.tabs.map(function (t, k) { return '<div class="cpane" data-cp="' + id + '-' + k + '"' + (k ? ' hidden' : '') + '>' + t.items.map(function (x) { return '<p>' + md(x) + '</p>'; }).join('') + '</div>'; }).join('') + '</section>';
  }
  function render() {
    host.innerHTML = header() + BANK.items.map(function (q, i) {
      var pre = '';
      if (q.case && (i === 0 || BANK.items[i - 1].case !== q.case)) pre = caseBlock(q.case);
      return pre + body(q, i + 1); }).join('');
    wire(); tick();
  }
  function wire() {
    host.querySelectorAll('[data-mode]').forEach(function (b) { b.onclick = function () {
      var m = b.getAttribute('data-mode'); if (m === state.mode) return;
      state = { mode: m, answers: m === 'practice' ? state.answers : {}, started: m === 'exam' ? Date.now() : null, finished: false }; save(); render(); }; });
    var r = document.getElementById('reset'); if (r) r.onclick = function () { state = { mode: state.mode, answers: {}, started: state.mode === 'exam' ? Date.now() : null, finished: false }; save(); render(); };
    var f = document.getElementById('finish'); if (f) f.onclick = function () { state.finished = true; save(); render(); host.scrollIntoView(); };
    host.querySelectorAll('.opt').forEach(function (b) { b.onclick = function () {
      var id = b.getAttribute('data-q'), k = +b.getAttribute('data-k'), q = byId(id);
      if (q.type === 'multi') { var a = state.answers[id] || []; var i = a.indexOf(k); if (i >= 0) a.splice(i, 1); else if (a.length < q.pick) a.push(k); state.answers[id] = a; }
      else if (q.type === 'solution') state.answers[id] = k === 0;
      else state.answers[id] = k;
      save(); keep(id); }; });
    host.querySelectorAll('[data-yn]').forEach(function (b) { b.onclick = function () {
      var id = b.getAttribute('data-yn'), q = byId(id), a = state.answers[id] || q.statements.map(function () { return null; });
      a[+b.getAttribute('data-i')] = b.getAttribute('data-v') === 'true'; state.answers[id] = a; save(); keep(id); }; });
    host.querySelectorAll('[data-ord]').forEach(function (b) { b.onclick = function () {
      var id = b.getAttribute('data-ord'), q = byId(id), a = state.answers[id] || []; if (a.length < q.answer.length) a.push(+b.getAttribute('data-k')); state.answers[id] = a; save(); keep(id); }; });
    host.querySelectorAll('[data-undo]').forEach(function (b) { b.onclick = function () { var id = b.getAttribute('data-undo'); (state.answers[id] || []).pop(); save(); keep(id); }; });
    host.querySelectorAll('select[data-code]').forEach(function (s) { s.onchange = function () {
      var id = s.getAttribute('data-code'), q = byId(id), a = state.answers[id] || q.blanks.map(function () { return null; });
      a[+s.getAttribute('data-b')] = s.value === '' ? null : +s.value; state.answers[id] = a; save(); keep(id); }; });
    host.querySelectorAll('[data-ct]').forEach(function (b) { b.onclick = function () {
      var id = b.getAttribute('data-ct'), k = b.getAttribute('data-k'), sec = document.getElementById('CASE-' + id);
      sec.querySelectorAll('[data-ct]').forEach(function (x) { x.classList.toggle('on', x === b); });
      sec.querySelectorAll('.cpane').forEach(function (p) { p.hidden = p.getAttribute('data-cp') !== id + '-' + k; }); }; });
    host.querySelectorAll('.xtabs button').forEach(function (b) { b.onclick = function () {
      var box = b.closest('.expl'); box.querySelectorAll('.xtabs button').forEach(function (x) { x.classList.toggle('on', x === b); });
      box.querySelectorAll('.xp').forEach(function (p) { p.hidden = p.getAttribute('data-xp') !== b.getAttribute('data-x'); }); }; });
  }
  function keep(id) { render(); var el = document.getElementById('Q-' + id); if (el) el.scrollIntoView({ block: 'nearest' }); }
  function byId(id) { for (var i = 0; i < BANK.items.length; i++) if (BANK.items[i].id === id) return BANK.items[i]; }
  var iv = null;
  function tick() {
    if (iv) clearInterval(iv); var t = document.getElementById('timer'); if (!t || state.finished) return;
    if (!state.started) { state.started = Date.now(); save(); }
    function upd() { var left = BANK.minutes * 60 - Math.floor((Date.now() - state.started) / 1000);
      if (left <= 0) { state.finished = true; save(); render(); return; }
      t.textContent = Math.floor(left / 60) + ':' + ('0' + (left % 60)).slice(-2) + ' left'; }
    upd(); iv = setInterval(upd, 1000);
  }
  render();
})();
