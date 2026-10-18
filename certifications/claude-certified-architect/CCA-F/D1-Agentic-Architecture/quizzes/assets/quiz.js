/* Interactive quiz engine for CCA-F mock exams — PER-QUESTION instant feedback.
   A page defines window.QUIZ = { title, subtitle, passMark, questions:[
     { id, topic, question, options:[...], answer:<0-based idx>, explanation }
   ]}  and includes this script. Options are shuffled per attempt (no positional tell).
   The moment you pick an answer, that question locks and reveals the correct option
   plus a full explanation; a running score shows at the top. */
(function () {
  var QUIZ = window.QUIZ;
  if (!QUIZ) { return; }
  var PASS = QUIZ.passMark || 0.7;
  var TOTAL = QUIZ.questions.length;
  var root = document.getElementById('quiz');
  var state = [];        // per-question: { q, order:[shuffled origIdx...], picked, graded }
  var answered = 0, correct = 0, finished = false;

  function shuffle(a) {
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function build() {
    root.innerHTML = '';
    state = [];
    answered = 0; correct = 0; finished = false;
    QUIZ.questions.forEach(function (q, qi) {
      var order = shuffle(q.options.map(function (_, i) { return i; }));
      state.push({ q: q, order: order, picked: null, graded: false });

      var card = document.createElement('div');
      card.className = 'q';
      card.id = 'q' + qi;

      var head = document.createElement('div');
      head.className = 'qhead';
      head.innerHTML = '<span class="qnum">Q' + (qi + 1) + '</span>' +
        (q.topic ? '<span class="qtopic">' + esc(q.topic) + '</span>' : '');
      card.appendChild(head);

      var qt = document.createElement('div');
      qt.className = 'qtext';
      qt.textContent = q.question;
      card.appendChild(qt);

      var ul = document.createElement('ul');
      ul.className = 'opts';
      order.forEach(function (origIdx, pos) {
        var li = document.createElement('li');
        li.className = 'opt';
        li.dataset.qi = qi;
        li.dataset.orig = origIdx;
        var letter = String.fromCharCode(65 + pos);
        li.innerHTML =
          '<input type="radio" name="q' + qi + '" value="' + origIdx + '">' +
          '<span class="lbl"><b>' + letter + '.</b> ' + esc(q.options[origIdx]) + '</span>' +
          '<span class="mark ok">✓</span><span class="mark no">✗</span>';
        li.addEventListener('click', function () {
          if (state[qi].graded) return;              // locked once answered
          li.querySelector('input').checked = true;
          state[qi].picked = origIdx;
          gradeQuestion(qi);                          // instant feedback
        });
        ul.appendChild(li);
      });
      card.appendChild(ul);

      var ex = document.createElement('div');
      ex.className = 'explain';
      card.appendChild(ex);

      root.appendChild(card);
    });
    hideBar();
  }

  function gradeQuestion(qi) {
    var s = state[qi];
    if (s.graded) return;
    s.graded = true;
    var card = document.getElementById('q' + qi);
    card.classList.add('graded');
    var isCorrect = s.picked === s.q.answer;
    answered++;
    if (isCorrect) correct++;

    Array.prototype.forEach.call(card.querySelectorAll('.opt'), function (li) {
      var orig = parseInt(li.dataset.orig, 10);
      li.querySelector('input').disabled = true;
      if (orig === s.q.answer) li.classList.add('correct');
      if (orig === s.picked && !isCorrect) li.classList.add('wrongpick');
    });

    var res = s.picked === null
      ? '<span class="res skip">Skipped</span>'
      : (isCorrect ? '<span class="res ok">Correct</span>' : '<span class="res no">Incorrect</span>');
    card.querySelector('.explain').innerHTML =
      '<div class="eh">Explanation ' + res + '</div><div>' + esc(s.q.explanation) + '</div>';

    updateBar();
  }

  function updateBar() {
    var done = answered === TOTAL || finished;
    var denom = done ? TOTAL : answered;
    var pct = denom ? Math.round((correct / denom) * 100) : 0;
    var verdict = '';
    if (done) {
      var pass = (correct / TOTAL) >= PASS;
      verdict = '<span class="verdict ' + (pass ? 'pass' : 'fail') + '">' + (pass ? 'PASS' : 'BELOW 70%') + '</span>';
    }
    var sb = document.getElementById('scorebar');
    sb.innerHTML =
      '<span class="big">' + correct + ' / ' + denom + '</span>' +
      '<span class="pct">' + pct + '%' + (done ? '' : ' so far') + '</span>' +
      verdict +
      '<span class="bar"><span style="width:' + pct + '%"></span></span>';
    sb.classList.add('show');
  }

  function hideBar() {
    var sb = document.getElementById('scorebar');
    sb.classList.remove('show');
    sb.innerHTML = '';
  }

  function finishAll() {
    finished = true;
    state.forEach(function (s, qi) {   // reveal any skipped questions (correct answer + explanation)
      if (!s.graded) { s.picked = null; gradeQuestion(qi); }
    });
    updateBar();
    var b = document.getElementById('submitBtn');
    if (b) b.disabled = true;
    document.getElementById('scorebar').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function reset() {
    build();
    var b = document.getElementById('submitBtn');
    if (b) b.disabled = false;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var count = document.getElementById('qcount');
    if (count) count.textContent = TOTAL;

    // Refresh the intro copy to describe per-question mode.
    var intro = document.querySelector('.quiz-intro');
    if (intro) {
      var ps = intro.querySelectorAll('p');
      if (ps[0]) ps[0].innerHTML = '<strong>Exam-level, scenario-based questions with instant feedback.</strong> ' +
        'Pick an answer and the correct option plus a full explanation appear immediately for that question — ' +
        'the options are deliberately close, so read every one. Options reshuffle on each attempt.';
      if (ps[1]) ps[1].innerHTML = 'Your running score shows at the top. Use <em>Reveal remaining &amp; finish</em> ' +
        'to expose any you skipped, or <em>Reset &amp; reshuffle</em> to try again.';
    }

    build();

    var sb = document.getElementById('submitBtn');
    if (sb) { sb.textContent = 'Reveal remaining & finish'; sb.addEventListener('click', finishAll); }
    var rb = document.getElementById('resetBtn');
    if (rb) rb.addEventListener('click', reset);
    var un = document.getElementById('unanswered');
    if (un) un.classList.remove('show');
  });
})();
