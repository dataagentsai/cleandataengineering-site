/* Checks assets/sims*.js against the question bank. Run: node check_sims.js
   Rules:
   - every sim keys on a real question id, has worlds A (as written) and B (decider changed),
     and one run per option in each world;
   - World A: every keyed answer passes cleanly; no other option passes cleanly (warn = "works, with a cost");
   - World B: the runner-up passes cleanly (that is the point of the world);
   - a failing run shows its failure: at least one step marked bad/warn or a constraint (block) step;
   - rate agrees with the outcome: a failing run has rate < 1, a clean pass has rate >= 0.9;
   - steps use known lanes and marks, and no text contains "undefined". */
const fs = require('fs'), path = require('path');
global.window = {};
const dir = path.join(__dirname, 'assets');
require(path.join(dir, 'questions.js'));
const files = ['sims.js'].concat(fs.readdirSync(dir).filter(f => /^sims-.+\.js$/.test(f)).sort());
files.forEach(f => require(path.join(dir, f)));

const Q = {}; window.EXAM.questions.forEach(q => { Q[q.id] = q; });
const LANES = new Set(['cust', 'loop', 'api', 'hook', 'tool', 'sub', 'block', 'file', 'ctx']);
const MARKS = new Set(['', 'ok', 'bad', 'warn']);
let errors = 0;
const err = (id, m) => { errors++; console.log('  ✗ ' + id + ': ' + m); };

for (const [id, s] of Object.entries(window.SIMS)) {
  const q = Q[id];
  if (!q) { err(id, 'no such question'); continue; }
  if (JSON.stringify(s).includes('undefined')) err(id, 'text contains "undefined"');
  const ws = (s.worlds || []).map(w => w.id).join('');
  if (ws !== 'AB') { err(id, 'worlds must be A then B, got ' + ws); continue; }
  for (const w of s.worlds) {
    if (!w.label || !w.desc) err(id, 'world ' + w.id + ' needs label and desc');
    const runs = s.runs && s.runs[w.id];
    if (!runs || runs.length !== q.options.length) { err(id, w.id + ': need ' + q.options.length + ' runs'); continue; }
    runs.forEach((r, i) => {
      const tag = id + ' ' + w.id + String.fromCharCode(65 + i);
      if (!r.steps || !r.steps.length) return err(tag, 'no steps');
      if (!r.outcome || typeof r.outcome.ok !== 'boolean' || !r.outcome.text) return err(tag, 'outcome needs ok + text');
      if (typeof r.rate !== 'number' || r.rate < 0 || r.rate > 1) err(tag, 'rate must be 0..1');
      r.steps.forEach((st, k) => {
        if (!LANES.has(st.lane)) err(tag, 'step ' + k + ' bad lane ' + st.lane);
        if (!MARKS.has(st.mark)) err(tag, 'step ' + k + ' bad mark ' + st.mark);
        if (!st.title) err(tag, 'step ' + k + ' no title');
        if (st.meter && !(st.meter.total > 0 && Array.isArray(st.meter.parts) && st.meter.parts.every(x => x.label && x.tokens >= 0))) err(tag, 'step ' + k + ' bad meter');
        if (st.meter && st.meter.parts.reduce((a, x) => a + x.tokens, 0) > st.meter.total) err(tag, 'step ' + k + ' meter over total');
        if (st.table && !(Array.isArray(st.table.head) && st.table.rows.every(r => r.length === st.table.head.length))) err(tag, 'step ' + k + ' bad table');
      });
      const clean = r.outcome.ok && !r.outcome.warn;
      if (!r.outcome.ok && !r.steps.some(st => st.mark === 'bad' || st.mark === 'warn' || st.lane === 'block')) err(tag, 'fails but no step shows the failure');
      if (!r.outcome.ok && r.rate >= 1) err(tag, 'fails but rate is 1');
      if (clean && r.rate < 0.9) err(tag, 'clean pass but rate < 0.9');
      const keyed = q.answer.indexOf(i) >= 0;
      if (w.id === 'A' && keyed && !clean) err(tag, 'keyed answer must pass cleanly in World A');
      if (w.id === 'A' && !keyed && clean) err(tag, 'non-keyed option passes cleanly in World A');
      if (w.id === 'B' && i === q.runnerUp && !clean) err(tag, 'runner-up must pass cleanly in World B');
    });
  }
}
// every question highlights 1-2 deciding sentences (simview.js clues; add hand marks to CLUES there if not)
require(path.join(dir, 'simview.js'));
window.EXAM.questions.forEach(q => {
  const k = window.SimView.clueCount(q);
  if (k < 1 || k > 2) err(q.id, 'deciding-sentence highlight covers ' + k + ' sentences (want 1-2)');
});
const n = Object.keys(window.SIMS).length;
console.log((errors ? errors + ' problem(s)' : 'ok') + ' — ' + n + ' sims from ' + files.join(', '));
process.exit(errors ? 1 : 0);
