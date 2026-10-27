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
  .steps button { display:flex; gap:8px; width:100%; text-align:left; font:inherit; font-size:14px; border:0; background:none; padding:7px 8px; border-radius:10px; cursor:pointer; color:var(--ink-soft); }
  .steps button b { font-family:var(--hand); font-size:19px; min-width:24px; color:var(--ink); }
  .steps button.on { background:var(--butter-wash); color:var(--ink); outline:1.5px solid var(--ink); }
  .steps button.done { color:var(--ink); }
  .insp { border:var(--line); border-radius:var(--wob); padding:14px 18px; background:var(--butter-wash); margin-bottom:14px; }
  .insp h2 { font-size:28px; margin:0 0 6px; } .insp p { margin:0 0 10px; font-size:16.5px; }
  .insp pre, .panel pre { font-family:var(--mono); font-size:12px; line-height:1.45; background:#fff; border:1px solid var(--rule); border-radius:8px; padding:10px 12px; overflow-x:auto; margin:6px 0; white-space:pre; }
  .grid8 { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
  .panel { border:1.5px solid #bbb; border-radius:14px; padding:10px 12px; background:#fff; min-width:0; transition:border-color .2s, box-shadow .2s; }
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
  @media (max-width:980px) { .studio { grid-template-columns:1fr; } .steps { position:static; max-height:none; } .grid8 { grid-template-columns:1fr; } .tiles { grid-template-columns:1fr 1fr; } }
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
    const env = D.env, gs = D.group_for_step[step.n] || [];
    let h = '<p class="kv">' + esc(env.master) + ' · driver ' + esc(env.executors.map(e => e.host + ', ' + e.cores + ' cores').join('; ')) + ' · Spark ' + esc(env.spark) + ' · Delta ' + esc(env.delta) + '</p>';
    if (!gs.length) return h + '<p class="empty">' + (step.n === 10 ? 'No Spark job ran: the batch check stopped it before any work.' : 'No Spark work in this step.') + '</p>';
    const jobs = gs.flatMap(g => D.jobs[g] || []);
    const stages = jobs.flatMap(j => j.stages), tasks = stages.reduce((a, s) => a + s.tasks, 0), ms = jobs.reduce((a, j) => a + j.ms, 0);
    const shuffle = stages.reduce((a, s) => a + s.shuffle_write, 0);
    h += '<div class="tiles" style="grid-template-columns:repeat(4,1fr);margin:6px 0"><div class="tile"><span>jobs</span><b>' + jobs.length + '</b></div><div class="tile"><span>stages</span><b>' + stages.length + '</b></div><div class="tile"><span>tasks</span><b>' + tasks + '</b></div><div class="tile"><span>time</span><b>' + (ms / 1000).toFixed(1) + 's</b></div></div>';
    const top = jobs.slice().sort((a, b) => b.ms - a.ms).slice(0, 8), mx = Math.max(...top.map(j => j.ms), 1);
    h += '<div class="bars">' + top.map(j => '<div class="bar"><i style="width:' + Math.round(160 * j.ms / mx) + 'px"></i>job ' + j.job + ' · ' + j.ms + ' ms · ' + j.stages.map(s => s.tasks).join('+') + ' tasks · ' + esc(j.desc.replace(/^(Delta: )+/, '')) + '</div>').join('') + '</div>';
    h += '<p class="note">Shuffle written: ' + shuffle + ' bytes. Many stages have 50 tasks: that is Delta rebuilding the table\'s state from its log (50 partitions by default), not your data. On three rows, the bookkeeping is most of the work.</p>';
    return h;
  },
  layers(p, ch) {
    if (!p) return '<p class="empty">No data yet.</p>';
    const names = ['landing', 'bronze', 'silver', 'quarantine', 'gold'].filter(n => p[n]);
    const hint = (D.tab_for_step[curStep] || [])[0]; const cur = (tabState.layers && names.includes(tabState.layers)) ? tabState.layers : (names.includes(hint) ? hint : names[names.length - 1]);
    return tabs('layers', names, cur, ch) + tbl(p[cur]);
  },
  storage(p, ch) {
    if (!p) return '<p class="empty">No files yet.</p>';
    const names = Object.keys(p).filter(k => k !== 'landing');
    let h = '<p class="kv">landing/ ' + esc((p.landing || []).join(', ')) + '</p>';
    if (!names.length) return h;
    const hint = (D.tab_for_step[curStep] || [])[1]; const cur = (tabState.storage && names.includes(tabState.storage)) ? tabState.storage : (names.includes(hint) ? hint : names[names.length - 1]);
    const t = p[cur];
    h += tabs('storage', names, cur, ch) + '<p class="kv">' + esc(t.table) + ': ' + t.data_files + ' Parquet file(s) on disk, ' + t.commits.length + ' commit(s) in _delta_log/</p>';
    h += t.commits.slice().reverse().map((c, i) => {
      const ci = (c.actions.find(a => a.commitInfo) || {}).commitInfo || {};
      const m = ci.operationMetrics || {};
      const keys = ['numOutputRows', 'numTargetRowsInserted', 'numTargetRowsUpdated', 'numTargetRowsCopied', 'numTargetFilesAdded', 'numTargetFilesRemoved', 'numFiles', 'numRemovedFiles'].filter(k => k in m);
      return '<details class="c"' + (i === 0 ? ' open' : '') + '><summary>_delta_log/' + c.file + ' · ' + esc(ci.operation) + ' · ' + keys.map(k => k.replace('numTarget', '').replace('num', '') + '=' + m[k]).join(' ') + '</summary><pre>' + esc(JSON.stringify(c.actions, null, 1)) + '</pre></details>';
    }).join('');
    return h;
  },
  engine(p) {
    if (!p) return '<p class="empty">' + (scen.id === 'naive' && curStep > 4 ? 'Plans were not recorded for the naive pipeline; see scenario 1 for the plans of each hop.' : 'No query yet.') + '</p>';
    return '<p class="note">The physical plan Spark chose for this step (EXPLAIN FORMATTED, recorded):</p><pre>' + esc(p.plan) + '</pre>';
  },
  logs(_, __, step, st) {
    const lines = (st.logs || []).slice(-9);
    let h = '<div class="log">' + lines.map(l => '<div class="' + l[1] + '">' + esc(l[0]) + ' ' + esc(l[1]) + ' ' + esc(l[2]) + '</div>').join('') + '</div>';
    if ((st.run_log || []).length) h += '<p class="note" style="margin-top:8px">run_log</p>' + tbl({cols: ['pipeline', 'layer', 'batch', 'status', 'config fingerprint', 'rows'], rows: st.run_log.slice(-6)});
    return h;
  },
  dashboard(p) {
    if (!p) return '<p class="empty">No data yet.</p>';
    return '<div class="tiles">' + p.tiles.map(t => '<div class="tile' + (/✗|2,500/.test(t[1]) ? ' bad' : '') + '"><span>' + esc(t[0]) + '</span><b>' + esc(t[1]) + '</b></div>').join('') + '</div>' + (p.note ? '<p class="note" style="margin-top:6px">' + esc(p.note) + '</p>' : '');
  },
};
const ORDER = [['inputs', '1 · Inputs'], ['config', '2 · Config & metadata'], ['cluster', '3 · Cluster'], ['layers', '4 · Layers'], ['storage', '5 · Storage (Delta log)'], ['engine', '6 · Engine (query plan)'], ['logs', '7 · Logs'], ['dashboard', '8 · Dashboard']];
function render() {
  const n = scen.steps[idx], step = BY[n], {st, changed} = state(idx);
  curStep = n; if (lastStep !== n) { for (const k in tabState) delete tabState[k]; lastStep = n; }
  document.querySelectorAll('.scen button').forEach(b => b.classList.toggle('on', b.dataset.s === scen.id));
  document.getElementById('steps').innerHTML = scen.steps.map((sn, i) => '<button data-i="' + i + '" class="' + (i === idx ? 'on' : i < idx ? 'done' : '') + '"><b>' + (i + 1) + '</b><span>' + esc(BY[sn].title) + '</span></button>').join('');
  document.getElementById('insp').innerHTML = '<p class="eyebrow">Step ' + (idx + 1) + ' of ' + scen.steps.length + ' · ' + esc(scen.label) + '</p><h2>' + esc(step.title) + '</h2><p>' + esc(step.plain) + '</p>' + (step.code ? '<details' + (idx > 0 ? ' open' : '') + '><summary style="cursor:pointer;font-size:14px">The code that ran</summary><pre>' + esc(step.code) + '</pre></details>' : '');
  document.getElementById('pos').textContent = (idx + 1) + ' / ' + scen.steps.length;
  document.getElementById('grid').innerHTML = ORDER.map(([k, t]) => '<div class="panel' + (step.focus.includes(k) || (k === 'cluster' && D.group_for_step[n]) ? ' focus' : '') + (k === 'storage' || k === 'engine' ? '' : '') + '" id="p-' + k + '"><h3>' + t + '<small>' + (step.focus.includes(k) ? 'changed' : '') + '</small></h3>' + R[k](st[k], changed[k] || [], step, st) + '</div>').join('');
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


def main():
    data = json.loads((ROOT / "_sim" / "data" / "batch.json").read_text())
    data["scenarios"] = SCENARIOS
    data["group_for_step"] = {str(k): v for k, v in GROUP_FOR_STEP.items()}
    data["tab_for_step"] = TAB_FOR_STEP
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    env = data["env"]
    scen_btns = "".join(f'<button data-s="{s["id"]}">{s["label"]}</button>' for s in SCENARIOS)
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › <a href="/learn/data-platform-architecture/">Data platform architecture</a> › DataTwin Studio</p>
<p class="eyebrow" style="margin-top:20px">DataTwin Studio · scene 1 · one batch, end to end</p>
<h1>Watch one batch go through a data platform</h1>
<p class="lede">A clothing shop's orders file travels from the moment a data engineer onboards the table to the dashboard tile. Every panel shows what that part of the platform holds at that step: the YAML and the metadata database, the Spark jobs and tasks, the rows in each layer, the Delta Lake commit files, the query plan, the logs and the dashboard. Then break it: send the same file again.</p>
<p><span class="real">real</span> Every value was recorded from a real run on {env['master']} Spark {env['spark']} + Delta Lake {env['delta']} on {env['recorded_at'][:10]}, with a real SQLite metadata store. Only the story (who merged the pull request, why the file was re-sent) is made up.</p>
<div class="scen">{scen_btns}</div>
<div class="ctl"><button id="prev">◀ Back</button><button id="play">▶ Play</button><button id="next">Next ▶</button><span class="pos" id="pos"></span><span class="note">Arrow keys work too. Click a step, a tab or a commit to look closer.</span></div>
<div class="studio"><nav class="steps" id="steps" aria-label="Steps"></nav><div><div class="insp" id="insp"></div><div class="grid8" id="grid"></div></div></div>
<section><p class="eyebrow">Read alongside</p><p><a href="/learn/data-platform-architecture/">Data platform architecture</a> · <a href="/learn/data-platform-architecture/metadata-store/">Metadata store</a> · <a href="/learn/data-platform-architecture/ingestion/">Ingestion</a> · <a href="/learn/data-platform-architecture/bronze-to-silver/">Bronze to silver</a> · <a href="/learn/data-platform-architecture/gold/">Gold</a> · <a href="/concepts/idempotency/">Idempotency</a></p>
<p class="note">More scenes are on the way: Delta Lake internals, Spark internals, streaming and Kafka, data quality and profiling, Unity Catalog, dimensional modelling, and cost.</p></section>
<script type="application/json" id="sim-data">{blob}</script>
<script>{JS}</script>"""
    desc = "Watch one batch move through a data platform: metadata, Spark jobs, bronze, silver, gold, Delta Lake commits, query plans, logs and the dashboard, recorded from a real run."
    html = wb.page("DataTwin Studio: one batch, end to end", desc, URL, body, CSS)
    out = ROOT / "learn" / "data-platform-sim"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(html)
    print("studio ->", out / "index.html", f"{len(html) // 1024} KB")


if __name__ == "__main__":
    main()
