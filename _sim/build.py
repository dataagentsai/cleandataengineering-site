"""DataTwin Studio: build /learn/data-platform-sim/ from recorded scenes.

    python3 _sim/build.py

Reads _sim/data/batch.json (made by record_batch.py from a real local Spark + Delta run) and writes
one page: eight panels, a numbered step list, step/play controls and three scenarios.
"""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("writing_build", ROOT / "_writing" / "build.py")
wb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wb)
SITE = wb.SITE
URL = f"{SITE}/learn/data-platform-sim/"

TAB_FOR_STEP = {4: ["landing", None], 5: ["bronze", "bronze.orders"], 6: ["silver", "silver.orders"], 7: ["gold", "gold.fact_sales"], 10: ["bronze", "bronze.orders"], 11: ["silver", "silver.orders"], 12: ["gold", "gold.fact_sales"], 13: ["gold", "naive_silver.orders"], 14: ["gold", "naive_bronze.orders"]}
GROUP_FOR_STEP = {5: ["normal-bronze"], 6: ["normal-silver"], 7: ["normal-gold"], 11: ["replay-silver"], 12: ["replay-gold"], 13: ["naive-first"], 14: ["naive-again"]}
SCENARIOS = [
    {"id": "normal", "label": "1 · Normal run", "steps": [1, 2, 3, 4, 5, 6, 7, 8], "blurb": "The shop's orders file goes from onboarding to the dashboard."},
    {"id": "replay", "label": "2 · Same file again, our pipeline", "steps": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "blurb": "A retry re-sends the batch. The batch check and MERGE keep every number right."},
    {"id": "naive", "label": "3 · Same file again, naive pipeline", "steps": [1, 2, 3, 4, 13, 14], "blurb": "No batch check, INSERT instead of MERGE: watch revenue double."},
]

CSS = """<style>
  .crumbs { font-size:13.5px; color:var(--faint); margin:28px 0 0; } .crumbs a { color:var(--muted); }
  main.wrap { max-width:1280px; }
  .lede { font-size:18px; color:var(--ink-soft); max-width:900px; }
  .real { display:inline-block; font-size:12px; font-weight:700; border:1.5px solid var(--ink); border-radius:999px; padding:1px 10px; background:var(--mint); }
  .scen { display:flex; flex-wrap:wrap; gap:8px; margin:14px 0 4px; }
  .scen button, .ctl button { font:inherit; font-size:14.5px; border:1.5px solid var(--ink); border-radius:var(--wob); padding:5px 14px; background:#fff; color:var(--ink); cursor:pointer; }
  .scen button.on { background:var(--ink); color:#fff; }
  .ctl { display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin:10px 0; }
  .ctl .pos { font-size:14px; color:var(--muted); margin-left:6px; }
  .studio { display:grid; grid-template-columns:260px 1fr; gap:16px; margin-top:8px; }
  .steps { border:var(--line); border-radius:14px; padding:8px; background:#fff; align-self:start; position:sticky; top:10px; max-height:92vh; overflow:auto; }
  .steps { min-width:0; } .steps button { box-sizing:border-box; display:flex; gap:8px; width:100%; text-align:left; font:inherit; font-size:14px; border:0; background:none; padding:7px 8px; border-radius:10px; cursor:pointer; color:var(--ink-soft); }
  .steps button b { font-family:var(--hand); font-size:19px; min-width:24px; color:var(--ink); }
  .steps button.on { background:var(--butter-wash); color:var(--ink); outline:1.5px solid var(--ink); }
  .steps button.done { color:var(--ink); }
  .insp { box-sizing:border-box; overflow-wrap:anywhere; border:var(--line); border-radius:var(--wob); padding:14px 18px; background:var(--butter-wash); margin-bottom:14px; }
  .insp h2 { font-size:28px; margin:0 0 6px; } .insp p { margin:0 0 10px; font-size:16.5px; }
  .insp pre, .panel pre { font-family:var(--mono); font-size:12px; line-height:1.45; background:#fff; border:1px solid var(--rule); border-radius:8px; padding:10px 12px; overflow-x:auto; margin:6px 0; white-space:pre; }
  .grid8 { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
  .panel { border:1.5px solid #bbb; border-radius:14px; padding:10px 12px; background:#fff; min-width:0; overflow-wrap:anywhere; transition:border-color .2s, box-shadow .2s; }
  .panel.focus { border:2.4px solid var(--ink); box-shadow:0 0 0 4px var(--butter-wash); }
  .panel.wide { grid-column:1 / -1; }
  .panel h3 { font-size:21px; margin:0 0 6px; display:flex; justify-content:space-between; align-items:baseline; gap:8px; }
  .panel h3 small { font-family:var(--sans); font-size:11.5px; color:var(--faint); font-weight:700; letter-spacing:.06em; text-transform:uppercase; }
  .panel .empty { color:var(--faint); font-size:14px; }
  .tabs { display:flex; flex-wrap:wrap; gap:6px; margin:0 0 6px; } .tabs button { font:inherit; font-size:12.5px; border:1.2px solid var(--ink); border-radius:999px; padding:1px 10px; background:#fff; cursor:pointer; }
  .tabs button.on { background:var(--ink); color:#fff; } .tabs button.new::after { content:" •"; color:#c0392b; }
  .tw { overflow-x:auto; } table.d { border-collapse:collapse; font-family:var(--mono); font-size:11.5px; width:100%; }
  table.d th, table.d td { text-align:left; padding:4px 7px; border-bottom:1px dashed var(--rule-firm); white-space:nowrap; } table.d th { color:var(--faint); font-weight:700; }
  table.d td.null { color:#c0392b; }
  .count { font-size:12.5px; color:var(--muted); margin:4px 0 0; }
  .tiles { display:grid; grid-template-columns:repeat(4,1fr); gap:8px; } .tile { border:1.5px solid var(--ink); border-radius:12px; padding:8px 10px; background:var(--mint-wash); }
  .tile span { display:block; font-size:12px; color:var(--muted); } .tile b { font-family:var(--hand); font-size:30px; font-weight:400; } .tile.bad { background:var(--rose-wash); }
  .bars { display:flex; flex-direction:column; gap:3px; margin:6px 0; } .bar { display:flex; align-items:center; gap:6px; font-size:11.5px; font-family:var(--mono); }
  .bar i { display:inline-block; height:10px; background:var(--peri); border:1px solid var(--ink); border-radius:3px; min-width:2px; }
  .log { font-family:var(--mono); font-size:11.5px; } .log div { padding:2px 0; border-bottom:1px dashed var(--rule); } .log .ERROR { color:#b0281a; font-weight:700; } .log .WARN { color:#8a6100; }
  details.c summary { cursor:pointer; font-family:var(--mono); font-size:12px; } .kv { font-family:var(--mono); font-size:12px; }
  .note { font-size:13px; color:var(--faint); }
  @media (max-width:980px) { .studio { grid-template-columns:minmax(0,1fr); } .studio > div { min-width:0; } .steps { position:static; max-height:none; } .grid8 { grid-template-columns:1fr; } .tiles { grid-template-columns:1fr 1fr; } }
</style>"""

JS = r"""
const D = JSON.parse(document.getElementById('sim-data').textContent);
const S = D.scenarios, BY = {}; D.steps.forEach(s => BY[s.n] = s);
let scen = S[0], idx = 0, timer = null, curStep = 1, lastStep = null;
const tabState = {};
const esc = s => s == null ? '' : String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function tbl(t, max) {
  if (!t || !t.cols) return '<p class="empty">empty</p>';
  const rows = t.rows.slice(0, max || 20);
  return '<div class="tw"><table class="d"><tr>' + t.cols.map(c => '<th>' + esc(c) + '</th>').join('') + '</tr>' +
    rows.map(r => '<tr>' + r.map(v => v == null ? '<td class="null">null</td>' : '<td>' + esc(v) + '</td>').join('') + '</tr>').join('') + '</table></div>' +
    (t.count != null ? '<p class="count">' + t.count + ' row' + (t.count === 1 ? '' : 's') + '</p>' : '');
}
function tabs(panel, names, cur, changed) {
  return '<div class="tabs">' + names.map(n => '<button data-p="' + panel + '" data-t="' + n + '" class="' + (n === cur ? 'on ' : '') + (changed.includes(n) ? 'new' : '') + '">' + esc(n) + '</button>').join('') + '</div>';
}
function state(upto) {            // panels as they stand after step `upto` of the scenario
  const st = {}, changed = {};
  scen.steps.slice(0, upto + 1).forEach((n, i) => {
    const s = BY[n];
    for (const [k, v] of Object.entries(s.panels)) { st[k] = Object.assign({}, st[k] || {}, v); if (i === upto) changed[k] = Object.keys(v); }
    st.logs = (st.logs || []).concat(s.logs); st.run_log = (st.run_log || []).concat(s.run_log);
  });
  return {st, changed};
}
const R = {
  inputs(p) {
    if (!p) return '<p class="empty">Nothing yet.</p>';
    if (!p.user) return '<pre style="white-space:pre-wrap">' + esc(p.text) + '</pre>';
    return '<p style="margin:0 0 6px;font-size:14.5px">' + esc(p.user) + '</p>' + (p.file ? '<p class="note">' + esc(p.file) + '</p>' : '') + '<pre>' + esc(p.text) + '</pre>';
  },
  config(p, ch) {
    if (!p) return '<p class="empty">Nothing yet.</p>';
    const names = ['yaml'].concat(p.db ? ['metadata DB'] : []).concat(p.merged ? ['merged config'] : []);
    const cur = tabState.config && names.includes(tabState.config) ? tabState.config : names[names.length - 1];
    let h = tabs('config', names, cur, ch.includes('merged') ? ['merged config'] : ch.includes('db') ? ['metadata DB'] : []);
    if (cur === 'yaml') h += '<pre>' + esc(p.yaml) + '</pre>';
    if (cur === 'metadata DB') h += Object.entries(p.db).map(([t, v]) => '<details class="c"' + (t.startsWith('dataset_config') ? ' open' : '') + '><summary>' + t + ' (' + v.rows.length + ')</summary>' + tbl(v) + '</details>').join('');
    if (cur === 'merged config') h += '<p class="note">platform &lt; source &lt; dataset</p><div class="tw"><table class="d"><tr><th>key</th><th>value</th><th>from</th></tr>' +
      Object.entries(p.merged).map(([k, v]) => '<tr><td>' + esc(k) + '</td><td>' + esc(v) + '</td><td>' + (k in p.view.dataset ? 'dataset' : k in p.view.source ? 'source' : 'platform') + (k in p.view.platform && k in p.view.dataset ? ' (overrides platform: ' + esc(p.view.platform[k]) + ')' : '') + '</td></tr>').join('') +
      '</table></div><p class="kv">fingerprint: <b>' + esc(p.fingerprint) + '</b></p>';
    return h;
  },
  cluster(_, __, step) {
    const env = D.env, gs = D.group_for_step[step.n] || (step.group ? [step.group] : []);
    let h = '<p class="kv">' + esc(env.master) + ' · driver ' + esc(env.executors.map(e => e.host + ', ' + e.cores + ' cores').join('; ')) + ' · Spark ' + esc(env.spark) + (env.delta && env.delta !== 'n/a' ? ' · Delta ' + esc(env.delta) : '') + '</p>';
    if (!gs.length) return h + '<p class="empty">' + (D.order.some(o => o[0] === 'dashboard') && step.n === 10 ? 'No Spark job ran: the batch check stopped it before any work.' : 'No Spark jobs recorded for this step.') + '</p>';
    const jobs = gs.flatMap(g => D.jobs[g] || []);
    const stages = jobs.flatMap(j => j.stages), tasks = stages.reduce((a, s) => a + s.tasks, 0), ms = jobs.reduce((a, j) => a + j.ms, 0);
    const shuffle = stages.reduce((a, s) => a + (s.shuffle_write != null ? s.shuffle_write : (s.sw || 0)), 0);
    h += '<div class="tiles" style="grid-template-columns:repeat(4,1fr);margin:6px 0"><div class="tile"><span>jobs</span><b>' + jobs.length + '</b></div><div class="tile"><span>stages</span><b>' + stages.length + '</b></div><div class="tile"><span>tasks</span><b>' + tasks + '</b></div><div class="tile"><span>time</span><b>' + (ms / 1000).toFixed(1) + 's</b></div></div>';
    const top = jobs.slice().sort((a, b) => b.ms - a.ms).slice(0, 8), mx = Math.max(...top.map(j => j.ms), 1);
    h += '<div class="bars">' + top.map(j => '<div class="bar"><i style="width:' + Math.round(160 * j.ms / mx) + 'px"></i>job ' + j.job + ' · ' + j.ms + ' ms · ' + j.stages.map(s => s.tasks).join('+') + ' tasks · ' + esc(j.desc.replace(/^(Delta: )+/, '')) + '</div>').join('') + '</div>';
    h += '<p class="note">Shuffle written: ' + shuffle + ' bytes.' + (D.order.some(o => o[0] === 'storage') ? ' Many stages have 50 tasks: that is Delta rebuilding the table\'s state from its log (50 partitions by default), not your data. On small data, that bookkeeping is most of the work.' : '') + '</p>';
    return h;
  },
  layers(p, ch) {
    if (!p) return '<p class="empty">No data yet.</p>';
    const names = Object.keys(p);
    const hint = (D.tab_for_step[curStep] || [])[0]; const cur = (tabState.layers && names.includes(tabState.layers)) ? tabState.layers : (names.includes(hint) ? hint : names[names.length - 1]);
    return tabs('layers', names, cur, ch) + tbl(p[cur]);
  },
  storage(p, ch) {
    if (!p) return '<p class="empty">No files yet.</p>';
    const names = Object.keys(p).filter(k => k !== 'landing');
    let h = p.landing ? '<p class="kv">landing/ ' + esc(p.landing.join(', ')) + '</p>' : '';
    if (!names.length) return h;
    const hint = (D.tab_for_step[curStep] || [])[1]; const cur = (tabState.storage && names.includes(tabState.storage)) ? tabState.storage : (names.includes(hint) ? hint : names[names.length - 1]);
    const t = p[cur];
    h += tabs('storage', names, cur, ch) + '<p class="kv">' + esc(t.table) + ': ' + (t.data_files != null ? t.data_files + ' Parquet file(s) on disk, ' : '') + t.commits.length + ' commit(s) in _delta_log/' + (t.other_files && t.other_files.filter(f => f !== '_commits').length ? '; also: ' + esc(t.other_files.filter(f => f !== '_commits').join(', ')) : '') + '</p>' +
      (t.last_checkpoint ? '<p class="kv">_last_checkpoint → ' + esc(JSON.stringify(t.last_checkpoint)) + '</p>' : '');
    const cs = t.commits.slice().reverse(); h += (cs.length > 12 ? '<p class="count">showing the latest 12 of ' + cs.length + ' commits</p>' : '');
    h += cs.slice(0, 12).map((c, i) => {
      const ci = (c.actions.find(a => a.commitInfo) || {}).commitInfo || {};
      const m = ci.operationMetrics || {};
      const keys = ['numOutputRows', 'numTargetRowsInserted', 'numTargetRowsUpdated', 'numTargetRowsCopied', 'numTargetFilesAdded', 'numTargetFilesRemoved', 'numFiles', 'numRemovedFiles', 'numAddedFiles', 'numUpdatedRows', 'numDeletedRows', 'numCopiedRows', 'numDeletionVectorsAdded', 'numRestoredFiles'].filter(k => k in m);
      return '<details class="c"' + (i === 0 ? ' open' : '') + '><summary>_delta_log/' + c.file + ' · ' + esc(ci.operation) + ' · ' + keys.map(k => k.replace('numTarget', '').replace('num', '') + '=' + m[k]).join(' ') + '</summary><pre>' + esc(JSON.stringify(c.actions.slice(0, 6), null, 1)) + '</pre>' + (c.actions.length > 6 ? '<p class="count">… and ' + (c.actions.length - 6) + ' more actions in this commit (' + c.actions.filter(a => a.add).length + ' add, ' + c.actions.filter(a => a.remove).length + ' remove)</p>' : '') + '</details>';
    }).join('');
    return h;
  },
  stages(_, __, step) {
    const gs = step.group ? (D.jobs[step.group] || []) : [];
    const st = gs.flatMap(j => j.stages).sort((a, b) => a.submitted - b.submitted);
    if (!st.length) return '<p class="empty">' + (step.group ? 'No stages recorded.' : 'No job ran in this step: nothing was executed.') + '</p>';
    const kb = x => x >= 1048576 ? (x / 1048576).toFixed(1) + ' MB' : x >= 1024 ? (x / 1024).toFixed(1) + ' KB' : x + ' B';
    return st.map(s => {
      const ts = s.task_list, span = Math.max(1, ...ts.map(t => t.offset + t.ms)), mx = Math.max(...ts.map(t => t.ms));
      const med = ts.map(t => t.ms).sort((a, b) => a - b)[Math.floor(ts.length / 2)] || 0;
      const skew = ts.length > 3 && s.sr > 0 && mx >= 100 && mx > 3 * Math.max(med, 1);   // key skew shows after a shuffle
      const bars = ts.slice(0, 60).map(t => '<div style="position:relative;height:7px;margin:1px 0"><i title="task ' + t.i + ': ' + t.ms + ' ms" style="position:absolute;left:' + (100 * t.offset / span).toFixed(1) + '%;width:' + Math.max(0.6, 100 * t.ms / span).toFixed(1) + '%;height:7px;border-radius:2px;background:' + (skew && t.ms === mx ? '#d9534f' : 'var(--peri)') + ';border:0.5px solid var(--ink)"></i></div>').join('');
      return '<div style="border-top:1px dashed var(--rule-firm);padding:6px 0"><p class="kv" style="margin:0"><b>stage ' + s.id + '</b> · ' + esc(s.name.replace(/ at .*$/, '')) + ' · <b>' + s.tasks + ' task' + (s.tasks === 1 ? '' : 's') + '</b> · ' + s.ms + ' ms' +
        (s.sw ? ' · shuffle write ' + kb(s.sw) : '') + (s.sr ? ' · shuffle read ' + kb(s.sr) : '') + (s.spill ? ' · <b style="color:#b0281a">spill ' + kb(s.spill) + '</b>' : '') + '</p>' +
        '<div style="margin:4px 0 2px">' + bars + '</div>' + (ts.length > 60 ? '<p class="count">first 60 of ' + ts.length + ' tasks</p>' : '') +
        '<p class="count">task time: slowest ' + mx + ' ms, median ' + med + ' ms' + (skew ? ' · <b style="color:#b0281a">one task ' + (mx / Math.max(med, 1)).toFixed(1) + '× the median: skew</b>' : '') + '</p></div>';
    }).join('') + '<p class="note">Each bar is one task, placed on its stage\'s own timeline. Two cores means at most two bars overlap: that is a wave.</p>';
  },
  checks(p) {
    if (!p) return '<p class="empty">No checks yet.</p>';
    const ok = p.items.filter(c => c[2]).length;
    return '<p class="kv"><b>' + ok + ' of ' + p.items.length + ' checks pass</b></p>' +
      p.items.map(c => '<div style="display:flex;gap:10px;align-items:baseline;padding:6px 0;border-bottom:1px dashed var(--rule)"><b style="font-size:20px;color:' + (c[2] ? '#1d6b3a' : '#b0281a') + '">' + (c[2] ? '✓' : '✗') + '</b><span style="flex:1">' + esc(c[0]) + '</span><code style="font-family:var(--mono);font-size:12px;color:var(--muted)">' + esc(c[1]) + '</code></div>').join('') +
      '<p class="note" style="margin-top:6px">These are the checks a real pipeline should run after every load. Red means the problem is still there.</p>';
  },
  files(p) {
    if (!p) return '<p class="empty">No files yet.</p>';
    const ix = [0, 5, 2, 3, 4, 1], re = r => ix.map(i => r[i]);
    return '<p class="kv"><b>' + esc(p.summary) + '</b></p>' + tbl({cols: re(p.cols), rows: p.rows.map(re)}, 14) + (p.rows.length > 14 ? '<p class="count">… ' + (p.rows.length - 14) + ' more files</p>' : '') +
      '<p class="note">live = part of the current version. removed = no longer in the current version, but still on disk so older versions can be read, until VACUUM.</p>';
  },
  engine(p) {
    if (!p) return '<p class="empty">' + (scen.id === 'naive' && curStep > 4 ? 'Plans were not recorded for the naive pipeline; see scenario 1 for the plans of each hop.' : D.order.some(o => o[0] === 'stages') ? 'No plan captured for this step.' : 'Nothing yet.') + '</p>';
    if (p.error || p.history || p.metrics) {
      let h = '';
      if (p.error) h += '<p class="note">The error, as Spark and Delta reported it:</p><pre style="color:#b0281a;white-space:pre-wrap">' + esc(p.error) + '</pre>';
      if (p.metrics) h += '<div class="tiles" style="grid-template-columns:repeat(3,1fr);margin:4px 0 8px"><div class="tile bad"><span>query before</span><b>' + p.metrics.before_ms + ' ms</b></div><div class="tile"><span>OPTIMIZE took</span><b>' + p.metrics.optimize_ms + ' ms</b></div><div class="tile"><span>query after</span><b>' + p.metrics.after_ms + ' ms</b></div></div>';
      if (p.history) h += '<p class="note">DESCRIBE HISTORY: every version, its operation and metrics</p>' + tbl(Object.assign({}, p.history, {rows: p.history.rows.slice().reverse()}), 14);
      return h;
    }
    return '<p class="note">The physical plan Spark chose for this step (EXPLAIN FORMATTED, recorded):</p><pre>' + esc(p.plan) + '</pre>';
  },
  logs(_, __, step, st) {
    const lines = (st.logs || []).slice(-9);
    let h = '<div class="log">' + lines.map(l => '<div class="' + l[1] + '">' + esc(l[0]) + ' ' + esc(l[1]) + ' ' + esc(l[2]) + '</div>').join('') + '</div>';
    if ((st.run_log || []).length) h += '<p class="note" style="margin-top:8px">run_log</p>' + tbl({cols: ['pipeline', 'layer', 'batch', 'status', 'config fingerprint', 'rows'], rows: st.run_log.slice(-6)});
    return h;
  },
  dashboard(p) {
    if (!p) return '<p class="empty">' + (D.order.some(o => o[0] === 'checks') ? 'Not used in this problem.' : 'No data yet.') + '</p>';
    return '<div class="tiles">' + p.tiles.map(t => '<div class="tile' + (/✗|2,500/.test(t[1]) ? ' bad' : /✓/.test(t[1]) ? '' : '') + '"><span>' + esc(t[0]) + '</span><b>' + esc(t[1]) + '</b></div>').join('') + '</div>' + (p.note ? '<p class="note" style="margin-top:6px">' + esc(p.note) + '</p>' : '');
  },
};
const ORDER = D.order;
function render() {
  const n = scen.steps[idx], step = BY[n], {st, changed} = state(idx);
  curStep = n; if (lastStep !== n) { for (const k in tabState) delete tabState[k]; lastStep = n; }
  document.querySelectorAll('.scen button').forEach(b => b.classList.toggle('on', b.dataset.s === scen.id));
  document.getElementById('steps').innerHTML = scen.steps.map((sn, i) => '<button data-i="' + i + '" class="' + (i === idx ? 'on' : i < idx ? 'done' : '') + '"><b>' + (i + 1) + '</b><span>' + esc(BY[sn].title) + '</span></button>').join('');
  document.getElementById('insp').innerHTML = '<p class="eyebrow">Step ' + (idx + 1) + ' of ' + scen.steps.length + ' · ' + esc(scen.label) + '</p><h2>' + esc(step.title) + '</h2><p>' + esc(step.plain) + '</p>' + (step.code ? '<details' + (idx > 0 ? ' open' : '') + '><summary style="cursor:pointer;font-size:14px">The code that ran</summary><pre>' + esc(step.code) + '</pre></details>' : '');
  document.getElementById('pos').textContent = (idx + 1) + ' / ' + scen.steps.length;
  document.getElementById('grid').innerHTML = ORDER.map(([k, t]) => '<div class="panel' + (step.focus.includes(k) || (k === 'cluster' && (D.group_for_step[n] || step.group)) ? ' focus' : '') + (k === 'storage' || k === 'engine' ? '' : '') + '" id="p-' + k + '"><h3>' + t + '<small>' + (step.focus.includes(k) ? 'changed' : '') + '</small></h3>' + R[k](st[k], changed[k] || [], step, st) + '</div>').join('');
}
document.addEventListener('click', e => {
  const b = e.target.closest('button'); if (!b) return;
  if (b.dataset.s) { scen = S.find(x => x.id === b.dataset.s); idx = 0; stop(); render(); }
  else if (b.dataset.i) { idx = +b.dataset.i; stop(); render(); }
  else if (b.dataset.p) { tabState[b.dataset.p] = b.dataset.t; render(); }
  else if (b.id === 'prev') { idx = Math.max(0, idx - 1); stop(); render(); }
  else if (b.id === 'next') { idx = Math.min(scen.steps.length - 1, idx + 1); stop(); render(); }
  else if (b.id === 'play') { if (timer) stop(); else { b.textContent = '❚❚ Pause'; timer = setInterval(() => { if (idx >= scen.steps.length - 1) return stop(); idx++; render(); }, 3500); } }
});
function stop() { if (timer) clearInterval(timer); timer = null; const p = document.getElementById('play'); if (p) p.textContent = '▶ Play'; }
document.addEventListener('keydown', e => { if (e.key === 'ArrowRight') document.getElementById('next').click(); if (e.key === 'ArrowLeft') document.getElementById('prev').click(); });
render();
"""


DELTA_SCENARIOS = [
    {"id": "files", "label": "1 · Files plus a log", "steps": [1, 2, 3, 4, 5], "blurb": "Create, insert, insert, update, delete: watch files and commits."},
    {"id": "versions", "label": "2 · Old versions, checkpoints, RESTORE", "steps": [6, 7, 8], "blurb": "Continues from scenario 1."},
    {"id": "writers", "label": "3 · Two writers at once", "steps": [9, 10], "blurb": "Optimistic concurrency, recorded with two real threads."},
    {"id": "dv", "label": "4 · Deletion vectors", "steps": [11, 12, 13], "blurb": "The same changes without rewriting files."},
    {"id": "small", "label": "5 · Small files and OPTIMIZE", "steps": [14, 15], "blurb": "300 tiny files, then compaction, with real timings."},
    {"id": "vacuum", "label": "6 · VACUUM and time travel", "steps": [16, 17], "blurb": "Why old versions stop working."},
]
BATCH_ORDER = [["inputs", "1 · Inputs"], ["config", "2 · Config & metadata"], ["cluster", "3 · Cluster"], ["layers", "4 · Layers"], ["storage", "5 · Storage (Delta log)"], ["engine", "6 · Engine (query plan)"], ["logs", "7 · Logs"], ["dashboard", "8 · Dashboard"]]
DELTA_ORDER = [["inputs", "1 · Command"], ["layers", "2 · Table rows"], ["files", "3 · Files on disk"], ["storage", "4 · _delta_log"], ["engine", "5 · History & errors"], ["cluster", "6 · Spark jobs"], ["logs", "7 · Logs"]]

SPARK_SCENARIOS = [
    {"id": "tasks", "label": "1 · Jobs, stages, tasks", "steps": [1, 2], "blurb": "Partitions become tasks; two cores run them in waves."},
    {"id": "lazy", "label": "2 · Lazy evaluation", "steps": [3, 4], "blurb": "Transformations run nothing; actions run everything."},
    {"id": "wide", "label": "3 · Narrow vs wide", "steps": [5, 6], "blurb": "filter vs groupBy, and the shuffle between stages."},
    {"id": "plan", "label": "4 · The query plan", "steps": [7, 8], "blurb": "Parsed, analysed, optimised, physical; pushdown."},
    {"id": "join", "label": "5 · Joins", "steps": [9, 10], "blurb": "Broadcast hash join vs sort-merge join."},
    {"id": "skew", "label": "6 · Skew and AQE", "steps": [11, 12], "blurb": "One hot key, one slow task; AQE splits it."},
    {"id": "cache", "label": "7 · Caching", "steps": [13, 14], "blurb": "The same query twice, then cached."},
]
SPARK_ORDER = [["inputs", "1 · Code"], ["layers", "2 · Result"], ["stages", "3 · Stages & tasks"], ["engine", "4 · Query plan"], ["cluster", "5 · Jobs"], ["logs", "6 · Logs"]]

PROBLEM_SCENARIOS = [
    {"id": "dupes", "label": "1 · Duplicates", "steps": [1, 2, 3], "blurb": "At-least-once delivery counts an order three times."},
    {"id": "idem", "label": "2 · Re-runs (idempotency)", "steps": [4, 5, 6], "blurb": "A retried job doubles a day."},
    {"id": "scd2", "label": "3 · SCD Type 2 pitfalls", "steps": [7, 8, 9], "blurb": "Two changes in one batch, a no-op, a late older change."},
    {"id": "late", "label": "4 · Late-arriving data", "steps": [10, 11, 12], "blurb": "Yesterday's order arrives today."},
    {"id": "fail", "label": "5 · Failure mid-job", "steps": [13, 14, 15], "blurb": "Silver moved on, gold did not."},
    {"id": "poison", "label": "6 · Poison records", "steps": [16, 17, 18], "blurb": "One bad line fails the whole load, every night."},
    {"id": "drift", "label": "7 · Schema drift", "steps": [19, 20, 21], "blurb": "A column renamed upstream; revenue goes to zero."},
    {"id": "deletes", "label": "8 · Hard deletes", "steps": [22, 23, 24], "blurb": "Incremental loads never see a deleted row."},
    {"id": "backfill", "label": "9 · Reload and backfill", "steps": [25, 26, 27], "blurb": "A bug corrupted five days; the fix is in. Now what?"},
    {"id": "smallfiles", "label": "10 · Small files", "steps": [28, 29, 30], "blurb": "The same query, slower with every small write."},
]
PROBLEM_ORDER = [["inputs", "1 · Code"], ["checks", "2 · Checks"], ["layers", "3 · Tables"], ["dashboard", "4 · Dashboard"], ["storage", "5 · _delta_log"], ["logs", "6 · Logs"]]

SCENES = [
    {"slug": "", "data": "batch.json", "scenarios": SCENARIOS, "order": BATCH_ORDER, "groups": GROUP_FOR_STEP, "tabs": TAB_FOR_STEP,
     "nav": "One batch, end to end", "eyebrow": "DataTwin Studio · scene 1 · one batch, end to end", "h1": "Watch one batch go through a data platform",
     "title": "DataTwin Studio: one batch, end to end",
     "desc": "Watch one batch move through a data platform: metadata, Spark jobs, bronze, silver, gold, Delta Lake commits, query plans, logs and the dashboard, recorded from a real run.",
     "lede": "A clothing shop's orders file travels from the moment a data engineer onboards the table to the dashboard tile. Every panel shows what that part of the platform holds at that step: the YAML and the metadata database, the Spark jobs and tasks, the rows in each layer, the Delta Lake commit files, the query plan, the logs and the dashboard. Then break it: send the same file again.",
     "real": "with a real SQLite metadata store. Only the story (who merged the pull request, why the file was re-sent) is made up."},
    {"slug": "delta", "data": "delta.json", "scenarios": DELTA_SCENARIOS, "order": DELTA_ORDER, "groups": {}, "tabs": {},
     "nav": "Delta Lake internals", "eyebrow": "DataTwin Studio · Delta Lake internals", "h1": "Delta Lake internals, recorded",
     "title": "Delta Lake internals: files, log, versions, DVs",
     "desc": "See Delta Lake from the inside: Parquet files and the _delta_log, copy-on-write updates, checkpoints, time travel, concurrent writers, deletion vectors, OPTIMIZE and VACUUM.",
     "lede": "What really happens on disk when you create, insert, update and delete in a Delta table. Each step shows the command, the table's rows, every Parquet file on disk (live, or kept only for time travel), the commit files in _delta_log, the table history and the Spark jobs. Six scenarios, from 'a table is files plus a log' to 'why VACUUM breaks time travel'.",
     "real": "Nothing here is drawn by hand: the files, commits, errors and timings are what Delta actually wrote and reported."},
    {"slug": "spark", "data": "spark.json", "scenarios": SPARK_SCENARIOS, "order": SPARK_ORDER, "groups": {}, "tabs": {},
     "nav": "Spark internals", "eyebrow": "DataTwin Studio · Spark internals", "h1": "Spark internals, recorded",
     "title": "Spark internals: jobs, stages, tasks, plans",
     "desc": "See Spark from the inside: jobs, stages and tasks, lazy evaluation, the shuffle, Catalyst query plans, broadcast vs sort-merge joins, skew and AQE, and caching.",
     "lede": "What Spark actually does with your code. Each step shows the code, the result, every stage with its tasks as a timeline (so you can see waves and the one slow task), the query plan, the jobs and the logs. Seven scenarios on 2 million orders, from 'an action becomes tasks' to 'AQE splits a skewed join'.",
     "real": "Every stage, task, byte shuffled, plan and timing comes from Spark's own event log and EXPLAIN. Timings are from a laptop with 2 cores: compare them with each other, not with a cluster."},
    {"slug": "problems", "data": "problems.json", "scenarios": PROBLEM_SCENARIOS, "order": PROBLEM_ORDER, "groups": {}, "tabs": {},
     "nav": "Problem Lab", "eyebrow": "DataTwin Studio · Problem Lab · ten problems every data team hits",
     "h1": "The Problem Lab: break it, try the naive fix, fix it right",
     "title": "Problem Lab: ten data engineering problems, run for real",
     "desc": "Ten data problems run on Spark and Delta: duplicates, re-runs, SCD2, late data, failures, poison rows, schema drift, deletes, backfill, small files.",
     "lede": "The problems that cost real teams their nights. Each one is told in three steps: what you see (the checks go red), the naive fix (applied for real, and it fails or makes things worse), and the right fix (the checks go green). Every table, check, error and commit comes from a real Spark and Delta Lake run.",
     "real": "The naive fixes were run too, so their failures are real, not described."},
]


def page(sc):
    data = json.loads((ROOT / "_sim" / "data" / sc["data"]).read_text())
    data["scenarios"] = sc["scenarios"]
    data["order"] = sc["order"]
    data["group_for_step"] = sc["groups"]
    data["tab_for_step"] = sc["tabs"]
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    env = data["env"]
    url = URL + (sc["slug"] + "/" if sc["slug"] else "")
    scen_btns = "".join(f'<button data-s="{s["id"]}" title="{s["blurb"]}">{s["label"]}</button>' for s in sc["scenarios"])
    nav = "".join(f'<span class="real" style="background:var(--ink);color:#fff">{x["nav"]}</span>' if x is sc else f'<a href="/learn/data-platform-sim/{x["slug"] + "/" if x["slug"] else ""}" style="font-size:14px">{x["nav"]}</a>' for x in SCENES)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › <a href="/learn/data-platform-architecture/">Data platform architecture</a> › <a href="/learn/data-platform-sim/">DataTwin Studio</a>{" › " + sc["nav"] if sc["slug"] else ""}</p>
<p class="note" style="margin:10px 0 0;display:flex;gap:12px;flex-wrap:wrap;align-items:center"><b>Scenes:</b> {nav} <span>· more coming: performance stories, streaming, Kafka, data quality, Unity Catalog, dimensional modelling, cost</span></p>
<p class="eyebrow" style="margin-top:16px">{sc["eyebrow"]}</p>
<h1>{sc["h1"]}</h1>
<p class="lede">{sc["lede"]}</p>
<p><span class="real">real</span> Recorded on {env['master']} Spark {env['spark']}{(' + Delta Lake ' + env['delta']) if env.get('delta') not in (None, 'n/a') else ''} on {env['recorded_at'][:10]}. {sc["real"]}</p>
<div class="scen">{scen_btns}</div>
<div class="ctl"><button id="prev">◀ Back</button><button id="play">▶ Play</button><button id="next">Next ▶</button><span class="pos" id="pos"></span><span class="note">Arrow keys work too. Click a step, a tab or a commit to look closer.</span></div>
<div class="studio"><nav class="steps" id="steps" aria-label="Steps"></nav><div><div class="insp" id="insp"></div><div class="grid8" id="grid"></div></div></div>
<section><p class="eyebrow">Read alongside</p><p><a href="/learn/data-platform-architecture/">Data platform architecture</a> · <a href="/learn/medallion-architecture/">Medallion architecture</a> · <a href="/concepts/table-formats/">Open table formats</a> · <a href="/concepts/small-files/">The small-files problem</a> · <a href="/concepts/idempotency/">Idempotency</a> · <a href="/concepts/cost-drivers/">Where data costs come from</a></p></section>
<script type="application/json" id="sim-data">{blob}</script>
<script>{JS}</script>"""
    html = wb.page(sc["title"], sc["desc"], url, body, CSS)
    out = ROOT / "learn" / "data-platform-sim" / sc["slug"]
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(html)
    print("studio ->", out / "index.html", f"{len(html) // 1024} KB")


def main():
    for sc in SCENES:
        page(sc)


if __name__ == "__main__":
    main()
