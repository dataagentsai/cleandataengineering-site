/* SimView — the simulator as a reusable component, used inline in each exam card (exam.js) and by sim.html.
   SimView.mount(el, qid, opts) renders the world switch, the options with badges, the controls, the trace,
   the outcome and the 20-run strip inside el. Several instances can live on one page.
   opts: { order: [orig index per displayed position] (default 0..n-1),
           pick:  [orig indices the learner chose] (adds "Your pick" badges),
           opt:   orig index to preselect, world: 'A' | 'B',
           qtextEl: element holding the question text, dimmed in World B }
   SimView.deep(q, letterOf) returns the "Think it through" body for a question. */
(function () {
  var BASE = { cust: 'Customer', loop: 'Your loop', api: 'Claude API', hook: 'Hook', tool: 'Tool', sub: 'Subagent',
    block: 'Constraint', file: 'Config file', ctx: 'Context window' };
  var QS = null;
  function qs() { if (!QS) { QS = {}; window.EXAM.questions.forEach(function (q) { QS[q.id] = q; }); } return QS; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  function meterHtml(m) {
    var used = m.parts.reduce(function (a, x) { return a + x.tokens; }, 0);
    var k = function (x) { return '--k:var(--k-' + (x.kind || 'keep') + ')'; };
    var fmt = function (n) { return n >= 1000 ? Math.round(n / 1000) + 'k' : String(n); };
    return '<div class="meter"><div class="bar">' + m.parts.map(function (x) {
        return '<i style="' + k(x) + ';width:' + (100 * x.tokens / m.total) + '%" title="' + esc(x.label) + '"></i>'; }).join('') +
      '</div><div class="keys">' + m.parts.map(function (x) { return '<span style="' + k(x) + '">' + esc(x.label) + ' ' + fmt(x.tokens) + '</span>'; }).join('') +
      '<span style="--k:transparent">' + fmt(used) + ' of ' + fmt(m.total) + ' tokens</span></div></div>';
  }
  function tableHtml(t) {
    return '<div class="dtable"><table><tr>' + t.head.map(function (h) { return '<th>' + esc(h) + '</th>'; }).join('') + '</tr>' +
      t.rows.map(function (r) { return '<tr>' + r.map(function (c) { return '<td>' + esc(c) + '</td>'; }).join('') + '</tr>'; }).join('') + '</table></div>';
  }

  function deep(q, letterOf) {
    var d = q.deep; if (!d) return '';
    var L = function (t) { return String(t).replace(/\[\[(\d)\]\]/g, function (_, i) { return letterOf(+i); }); };
    return '<h4>1 · The premise to correct</h4><p>' + L(d.premise) + '</p>' +
      (d.diagram ? '<pre class="ddia">' + esc(d.diagram) + '</pre>' : '') +
      '<h4>2 · Mind map: ' + L(d.mapTitle) + '</h4><div class="dtable"><table><tr>' +
      d.map.head.map(function (h) { return '<th>' + L(h) + '</th>'; }).join('') + '</tr>' +
      d.map.rows.map(function (r) { return '<tr>' + r.map(function (c) { return '<td>' + L(c) + '</td>'; }).join('') + '</tr>'; }).join('') +
      '</table></div><h4>3 · Apply it to this question</h4><ol class="dev">' +
      d.evidence.map(function (x) { return '<li><q>' + L(x.quote) + '</q><div>' + L(x.means) + '</div></li>'; }).join('') +
      '</ol><h4>4 · Rule to remember</h4><blockquote class="drule">' + L(d.rule) + '</blockquote>' +
      '<p class="dguide">Exam guide, ' + esc(d.guide.obj) + ': <i>“' + esc(d.guide.quote) + '”</i></p>';
  }

  /* Deciding sentences. Found from the ELI5 clue quote ("The clue is: “…”") or, failing that, the deep-layer
     evidence whose meaning names the decider. CLUES lists the few that need marking by hand. */
  var CLUES = {
    'm7-s5-08': ['Nobody reads it until the Monday planning meeting', 'the report uses only its build file and lockfile'],
    'm7-s6-09': ['Scans from small carriers are rare in that sample', 'Compliance wants error rates measured for each document type']
  };
  function norm(s) {
    return String(s).replace(/<[^>]+>/g, '').replace(/[“”]/g, '"').replace(/[‘’]/g, "'")
      .replace(/\s+/g, ' ').trim().toLowerCase().replace(/^["']+|[.,;:!?…"']+$/g, '');
  }
  function clues(q) {
    if (CLUES[q.id]) return CLUES[q.id].map(norm);
    var stem = norm(q.question), found = [];
    var eli = q.eli5 && q.eli5.question || '', at = eli.search(/clue/i);
    if (at >= 0) (eli.slice(at).match(/“[^”]+”|"[^"]+"/g) || []).forEach(function (m) {
      var c = norm(m); if (c && stem.indexOf(c) >= 0) found.push(c); });
    if (!found.length) ((q.deep && q.deep.evidence) || []).forEach(function (e) {
      if (/decid/i.test(e.means)) { var c = norm(e.quote); if (c && stem.indexOf(c) >= 0) found.push(c); } });
    return found;
  }
  function sentences(html) { return html.split(/(?<=[.?!][”"]?)\s+(?=[A-Z“"<])/); }
  function isHit(sent, cs) {
    if (/\?\s*$/.test(sent.replace(/<[^>]+>/g, ''))) return false;   // never the question line itself
    var n = norm(sent);
    return cs.some(function (c) { return n.indexOf(c) >= 0 || (n.length > 12 && c.indexOf(n) >= 0); });
  }
  /* mode: 'mark' (after answering), 'hint' (before answering), 'whatif' (World B: strike it, show the change) */
  function clueHtml(q, mode, desc) {
    var cs = clues(q), parts = sentences(q.question), last = -1;
    if (!cs.length) return q.question;
    var out = parts.map(function (s, i) {
      if (!isHit(s, cs)) return s;
      last = i;
      if (mode === 'whatif') return '<del class="clue">' + s + '</del>';
      return '<mark class="clue' + (mode === 'hint' ? ' hint' : '') + '" title="Deciding fact">' + s + '</mark>';
    });
    if (mode === 'whatif' && last >= 0) out[last] += ' <ins class="whatif">What if: ' + desc + '</ins>';
    return out.join(' ');
  }
  function clueCount(q) { var cs = clues(q); return sentences(q.question).filter(function (s) { return cs.length && isHit(s, cs); }).length; }

  function mount(el, qid, o) {
    o = o || {};
    var q = qs()[qid], sim = window.SIMS && window.SIMS[qid];
    if (!q || !sim) { el.innerHTML = '<p class="empty">No simulation for this question yet.</p>'; return; }
    var order = o.order || q.options.map(function (_, i) { return i; });
    var pick = o.pick || [];
    var letter = {}; order.forEach(function (orig, pos) { letter[orig] = String.fromCharCode(65 + pos); });
    var lanes = Object.assign({}, BASE, { cust: sim.who || 'Customer' }, sim.labels || {});
    var used = {}; ['A', 'B'].forEach(function (w) { sim.runs[w].forEach(function (r) { r.steps.forEach(function (st) { used[st.lane] = 1; }); }); });
    var cur = { world: o.world || 'A', opt: o.opt != null ? o.opt : (pick.length ? pick[0] : null), shown: 0 };

    el.classList.add('simview');
    el.innerHTML =
      '<div class="worlds"></div><p class="wdesc"></p><ul class="sopts"></ul>' +
      '<div class="ctl"><button data-a="step">Step ▸</button><button data-a="play">Play all ▸▸</button>' +
      '<button data-a="run20">Run 20 times</button><button data-a="reset">Reset</button></div>' +
      '<div class="legend">' + Object.keys(BASE).filter(function (k) { return used[k]; }).map(function (k) {
        return '<span style="--c:var(--l-' + k + ')">' + esc(lanes[k]) + '</span>'; }).join('') + '</div>' +
      '<ol class="trace"></ol><div class="soutcome"></div><div class="many"></div>';
    var $ = function (s) { return el.querySelector(s); };

    function run() { return cur.opt == null ? null : sim.runs[cur.world][cur.opt]; }
    function role(orig) {
      return q.answer.indexOf(orig) >= 0 ? 'correct' : (orig === q.runnerUp ? 'runner-up' : 'wrong');
    }
    function badges(orig) {
      var r = role(orig), b = '';
      if (pick.indexOf(orig) >= 0) b += '<span class="bdg you">● Your pick</span>';
      if (r === 'correct') b += '<span class="bdg ok">✓ ' + (cur.world === 'B' ? 'Exam answer' : 'Correct') + '</span>';
      if (r === 'runner-up') b += '<span class="bdg ru">◐ Runner-up</span>';
      return b;
    }

    function drawWorlds() {
      var w = sim.worlds.filter(function (x) { return x.id === cur.world; })[0], b = cur.world === 'B';
      $('.worlds').innerHTML = sim.worlds.map(function (x) {
        return '<button data-w="' + x.id + '" class="' + (x.id === cur.world ? 'on' : '') + '">' +
          (x.id === 'A' ? 'World A · the question as written' : 'World B · what if one fact changed?') + '</button>'; }).join('');
      var wd = $('.wdesc');
      wd.className = 'wdesc' + (b ? ' whatif' : '');
      var marked = clueCount(q) > 0;
      wd.innerHTML = b ? '<span class="wh">What if… (this is not the exam question)</span>' +
        (marked ? 'The struck-out sentence in the question is replaced: ' : 'The question is changed for this world: ') + w.desc +
        ' Anything in the question that says otherwise no longer holds. Watch which option wins now.' : w.desc;
      if (o.qtextEl) {
        o.qtextEl.innerHTML = b ? clueHtml(q, 'whatif', w.desc) : (o.markClue ? clueHtml(q, 'mark') : q.question);
        o.qtextEl.classList.toggle('dim', b && !marked);
      }
    }

    function stepHtml(s) {
      var p = s.payload == null ? '' : '<pre>' + esc(typeof s.payload === 'string' ? s.payload : JSON.stringify(s.payload, null, 2)) + '</pre>';
      return '<li class="m-' + s.mark + '" style="--c:var(--l-' + s.lane + ')"><span class="lane">' + esc(lanes[s.lane]) + '</span>' +
        '<span class="st">' + esc(s.title) + '</span>' + (s.note ? '<div class="note">' + esc(s.note) + '</div>' : '') +
        (s.meter ? meterHtml(s.meter) : '') + (s.table ? tableHtml(s.table) : '') + p + '</li>';
    }

    function draw() {
      $('.sopts').innerHTML = order.map(function (orig, pos) {
        return '<li data-i="' + orig + '" class="' + (orig === cur.opt ? 'on' : '') + '"><b>' + String.fromCharCode(65 + pos) + '.</b>' +
          '<span class="ot">' + q.options[orig].t + '</span><span class="bdgs">' + badges(orig) + '</span></li>'; }).join('');
      var r = run();
      $('[data-a=step]').disabled = $('[data-a=play]').disabled = !r || cur.shown >= r.steps.length;
      $('[data-a=run20]').disabled = !r;
      $('.many').innerHTML = '';
      if (!r) {
        $('.trace').innerHTML = '<li class="empty" style="--c:var(--line)">Click an option above to apply it to the system, then press Step or Play all.</li>';
        $('.soutcome').innerHTML = ''; return;
      }
      $('.trace').innerHTML = cur.shown ? r.steps.slice(0, cur.shown).map(stepHtml).join('') :
        '<li class="empty" style="--c:var(--line)">Option ' + letter[cur.opt] + ' is applied. Press <b>Step</b> to watch it one step at a time, or <b>Play all</b>.</li>';
      if (cur.shown >= r.steps.length) {
        var oc = r.outcome, cls = oc.ok ? (oc.warn ? 'wa' : 'ok') : 'no';
        var rl = role(cur.opt), mine = pick.indexOf(cur.opt) >= 0;
        var tag = 'Option ' + letter[cur.opt] + ' is ' + (rl === 'correct' ? 'the correct answer' : rl === 'runner-up' ? 'the runner-up' : 'a wrong answer') +
          ' in the exam question' + (mine ? ', and it is the one you picked.' : '.');
        $('.soutcome').innerHTML = '<div class="outcome ' + cls + '"><span class="v">' +
          (oc.ok ? (oc.warn ? 'Works, with a cost.' : 'Requirement met.') : 'Requirement not met.') + '</span>' + oc.text +
          '<div class="tagline">' + (cur.world === 'B' ? 'World B is a what-if. ' : '') + tag + '</div></div>';
      } else $('.soutcome').innerHTML = '';
    }

    function many() {
      var r = run(); if (!r) return;
      var fails = Math.round((1 - r.rate) * 20), dots = [];
      for (var i = 0; i < 20; i++) dots.push(false);
      for (var k = 0; k < fails; k++) dots[(k * 7 + 13) % 20] = true;
      $('.many').innerHTML = '<h4>The same change, 20 runs</h4><div class="dots">' +
        dots.map(function (x) { return '<i class="' + (x ? 'x' : '') + '"></i>'; }).join('') + '</div>' +
        '<div class="tagline">' + (20 - fails) + ' of 20 meet the requirement. ' +
        (r.rate === 1 ? 'Deterministic: the change is enforced in code, config or by the API.' : r.rate === 0 ? 'The change cannot be made under this world\'s constraint.' :
         'Probabilistic: the model usually complies. Whether that is enough depends on the requirement: <b>must never</b> or <b>should usually</b>.') + '</div>';
    }

    el.onclick = function (e) {
      var w = e.target.closest('.worlds button'), li = e.target.closest('.sopts li'), a = e.target.closest('.ctl button');
      if (w) { cur.world = w.dataset.w; cur.shown = 0; drawWorlds(); draw(); }
      else if (li) { cur.opt = +li.dataset.i; cur.shown = 0; draw(); }
      else if (a) {
        var r = run(); if (!r) return;
        if (a.dataset.a === 'step') cur.shown++;
        if (a.dataset.a === 'play' || a.dataset.a === 'run20') cur.shown = r.steps.length;
        if (a.dataset.a === 'reset') cur.shown = 0;
        draw(); if (a.dataset.a === 'run20') many();
      }
    };
    drawWorlds(); draw();
    return { setWorld: function (w, opt) { cur.world = w; if (opt != null) cur.opt = opt; cur.shown = 0; drawWorlds(); draw(); } };
  }

  window.SimView = { mount: mount, deep: deep, clueHtml: clueHtml, clueCount: clueCount };
})();
