"""Every check in the data-project-review skill, by category, at /learn/technical-anchor/project-review/checks/.

    (cd ~/data-project-review && uv run scripts/export.py)   # refresh catalog.json from the YAML first
    python3 _guides/review_checks.py && python3 _site/nav.py && python3 _site/seo.py

Reads ~/data-project-review/catalog.json (the skill's own export), so the page always matches the skill.
Each check can be marked Keep / Change / Drop with a note; marks stay in the reader's browser and
"Copy my review" puts them on the clipboard as plain text. Added 2 Nov 2026 so the owner can review the catalog.
"""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path.home() / "data-project-review" / "catalog.json"
_ta = importlib.util.spec_from_file_location("technical_anchor", ROOT / "_guides" / "technical_anchor.py")
ta = importlib.util.module_from_spec(_ta)
_ta.loader.exec_module(ta)
wb, E, SITE = ta.wb, ta.E, ta.SITE
URL = f"{SITE}/learn/technical-anchor/project-review/checks/"
REPO = "https://github.com/dataagentsai/data-project-review"
LEVELS = ["plan", "designed", "evidenced", "proven"]

CSS = ta.CSS.replace("</style>", """
  .filters { position:sticky; top:0; z-index:5; background:#fff; border:var(--line); border-radius:var(--wob); padding:10px 14px; margin:18px 0; display:flex; flex-wrap:wrap; gap:8px 12px; align-items:center; font-size:14.5px; }
  .filters input, .filters select { font:inherit; font-size:14px; border:1.5px solid var(--ink); border-radius:10px; padding:4px 8px; background:#fff; color:var(--ink); }
  .filters input { flex:1; min-width:180px; }
  .filters .count { color:var(--muted); font-size:13.5px; margin-left:auto; }
  .jump { display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:6px 18px; font-size:15px; margin:10px 0 0; }
  .jump a { text-decoration:none; } .jump span { color:var(--muted); font-size:13px; }
  h2.grp { margin-top:38px; } h3.con { font-family:var(--hand); font-weight:400; font-size:25px; margin:26px 0 6px; }
  details.chk { border:var(--line); border-radius:12px; margin:8px 0; background:#fff; }
  details.chk[open] { background:#FDFCF8; }
  details.chk > summary { list-style:none; cursor:pointer; padding:9px 14px; display:flex; flex-wrap:wrap; gap:6px 10px; align-items:baseline; }
  details.chk > summary::-webkit-details-marker { display:none; }
  details.chk > summary::before { content:"›"; color:var(--faint); transition:transform .15s; display:inline-block; }
  details.chk[open] > summary::before { transform:rotate(90deg); }
  .cid { font-family:var(--mono, monospace); font-size:13px; font-weight:700; } .ctitle { font-weight:700; flex:1; min-width:200px; }
  .pill { font-size:12px; font-weight:700; border:1.5px solid var(--ink); border-radius:999px; padding:0 8px; background:#fff; white-space:nowrap; }
  .pill.high { background:var(--rose-wash); } .pill.medium { background:var(--butter-wash); } .pill.low { background:var(--mint-wash); }
  .pill.mark-keep { background:#DFF3E7; } .pill.mark-change { background:#FFF1C2; } .pill.mark-drop { background:#F7D9D9; }
  .who { font-size:13px; color:var(--muted); }
  .cbody { padding:2px 16px 14px 30px; font-size:15px; }
  .cbody dl { display:grid; grid-template-columns:150px 1fr; gap:6px 14px; margin:8px 0; }
  .cbody dt { font-size:12px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; color:var(--faint); padding-top:3px; }
  .cbody dd { margin:0; } .cbody ul { margin:0; padding-left:18px; }
  .due { border-collapse:collapse; font-size:13.5px; } .due td, .due th { border:1px solid var(--rule-firm); padding:3px 8px; text-align:left; }
  .bind { border:1.5px dashed var(--rule-firm); border-radius:10px; padding:8px 12px; margin:10px 0; background:var(--peri-wash); }
  .bind b { display:block; font-size:12px; letter-spacing:.06em; text-transform:uppercase; color:var(--faint); }
  .rev { display:flex; flex-wrap:wrap; gap:8px; align-items:center; border-top:1.5px dashed var(--rule-firm); padding-top:10px; margin-top:10px; }
  .rev button { font:inherit; font-size:13.5px; font-weight:700; border:1.5px solid var(--ink); border-radius:999px; padding:3px 12px; background:#fff; cursor:pointer; color:var(--ink); }
  .rev button.on[data-m=keep] { background:#DFF3E7; } .rev button.on[data-m=change] { background:#FFF1C2; } .rev button.on[data-m=drop] { background:#F7D9D9; }
  .rev textarea { flex:1 1 100%; font:inherit; font-size:14px; border:1.5px solid var(--rule-firm); border-radius:10px; padding:6px 8px; min-height:44px; }
  .revbar { position:sticky; bottom:0; z-index:5; background:var(--ink); color:#fff; border-radius:14px; padding:9px 14px; display:flex; flex-wrap:wrap; gap:8px 14px; align-items:center; font-size:14px; margin-top:24px; }
  .revbar button { font:inherit; font-size:13.5px; font-weight:700; border:0; border-radius:999px; padding:4px 12px; cursor:pointer; background:#fff; color:var(--ink); }
  .revbar .ghost { background:transparent; color:#fff; border:1.5px solid #fff; }
  @media (max-width:640px) { .cbody dl { grid-template-columns:1fr; } .cbody { padding-left:16px; } }
</style>""")

JS = """<script>
(function(){
  var KEY='cde-review-checks-v1', st={};
  try { st=JSON.parse(localStorage.getItem(KEY)||'{}')||{}; } catch(e) { st={}; }
  function save(){ try { localStorage.setItem(KEY, JSON.stringify(st)); } catch(e) {} }
  var all=[].slice.call(document.querySelectorAll('details.chk'));
  function paint(d){ var id=d.id, s=st[id]||{}, tag=d.querySelector('.mark');
    d.querySelectorAll('.rev button').forEach(function(b){ b.classList.toggle('on', b.dataset.m===s.m); });
    tag.className='pill mark'+(s.m?' mark-'+s.m:''); tag.textContent=s.m?s.m:''; tag.style.display=s.m?'':'none';
    var ta=d.querySelector('textarea'); if(ta && ta.value!==(s.n||'')) ta.value=s.n||''; }
  function tally(){ var c={keep:0,change:0,drop:0}; Object.keys(st).forEach(function(k){ if(st[k].m) c[st[k].m]++; });
    document.getElementById('rv-count').textContent='Reviewed '+(c.keep+c.change+c.drop)+' of '+all.length+' · keep '+c.keep+' · change '+c.change+' · drop '+c.drop; }
  all.forEach(function(d){
    d.querySelectorAll('.rev button').forEach(function(b){ b.addEventListener('click', function(){
      var s=st[d.id]||{}; s.m = s.m===b.dataset.m ? '' : b.dataset.m; st[d.id]=s; save(); paint(d); tally(); filter(); }); });
    var ta=d.querySelector('textarea'); ta.addEventListener('input', function(){ var s=st[d.id]||{}; s.n=ta.value; st[d.id]=s; save(); });
    paint(d); });
  var q=document.getElementById('f-q'), fs=[].slice.call(document.querySelectorAll('.filters select'));
  function filter(){ var text=(q.value||'').toLowerCase(), shown=0;
    var want={}; fs.forEach(function(s){ want[s.name]=s.value; });
    all.forEach(function(d){
      var ok = (!text || d.textContent.toLowerCase().indexOf(text)>=0);
      ['kind','owner','severity','component'].forEach(function(k){ if(want[k] && (' '+d.dataset[k]+' ').indexOf(' '+want[k]+' ')<0) ok=false; });
      if(want.mark){ var m=(st[d.id]||{}).m||''; if(want.mark==='none' ? m : m!==want.mark) ok=false; }
      d.style.display=ok?'':'none'; if(ok) shown++; });
    document.querySelectorAll('h3.con').forEach(function(h){ var any=false, n=h.nextElementSibling;
      while(n && n.tagName==='DETAILS'){ if(n.style.display!=='none') any=true; n=n.nextElementSibling; } h.style.display=any?'':'none'; });
    document.getElementById('f-count').textContent=shown+' of '+all.length+' checks'; }
  q.addEventListener('input', filter); fs.forEach(function(s){ s.addEventListener('change', filter); });
  document.getElementById('rv-open').addEventListener('click', function(){ var o=!all[0].open; all.forEach(function(d){ if(d.style.display!=='none') d.open=o; }); });
  document.getElementById('rv-copy').addEventListener('click', function(){
    var lines=['My review of the data-project-review checks:'];
    all.forEach(function(d){ var s=st[d.id]; if(s && (s.m || s.n)) lines.push(d.id+' '+(s.m||'note').toUpperCase()+' ('+d.dataset.title+')'+(s.n?': '+s.n.replace(/\\s+/g,' '):'')); });
    var t=lines.join('\\n'), b=this;
    function done(){ b.textContent='Copied'; setTimeout(function(){ b.textContent='Copy my review'; }, 1500); }
    if(navigator.clipboard) navigator.clipboard.writeText(t).then(done, function(){ prompt('Copy this:', t); });
    else prompt('Copy this:', t); });
  document.getElementById('rv-clear').addEventListener('click', function(){ if(confirm('Clear all your marks and notes on this device?')){ st={}; save(); all.forEach(paint); tally(); filter(); } });
  if(location.hash){ var t=document.getElementById(location.hash.slice(1)); if(t && t.tagName==='DETAILS') t.open=true; }
  tally(); filter();
})();
</script>"""


def main():
    cat = json.loads(SRC.read_text())
    v, roles, stages = cat["vocab"], cat["roles"], cat["stages"]
    concerns = {**v["concerns"]["technical"], **v["concerns"]["delivery"]}
    binds = cat["bindings"]
    how = {cid: (b["name"], h) for t, b in binds.items() for cid, h in b["how"].items()}
    rname = lambda r: roles.get(r, {}).get("name", r)

    def names(xs, table):
        xs = xs or ["any"]
        return "any" if "any" in xs else ", ".join(x.replace("-", " ") for x in xs)

    def card(c):
        a = c.get("applies") or {}
        comps = a.get("components") or ["any"]
        due = c.get("due") or {}
        due_rows = "".join(f"<tr><td>{lv}</td><td>stage {due[lv]}: {E(stages[str(due[lv])]['name'])}</td></tr>" for lv in LEVELS if lv in due)
        ev = c.get("evidence") or {}
        sig = "".join(f"<li>{E(s)}</li>" for s in c.get("signals") or [])
        rel = ", ".join(f'<a href="#{r}">{r}</a>' for r in c.get("related") or [])
        b = how.get(c["id"])
        bind = (f'<div class="bind"><b>On {E(b[0])}</b>{E(b[1].get("do", ""))}'
                + (f'<br><i>Check it:</i> {E(b[1]["verify"])}' if b[1].get("verify") else "")
                + (f'<br><i>Trap:</i> {E(b[1]["traps"])}' if b[1].get("traps") else "") + "</div>") if b else ""
        kind = c.get("binding") and "tech" or c["kind"]
        rows = [("Question", E(c["question"])), ("Why it matters", E(c["why"])),
                ("Applies to", f"{E(names(a.get('kind'), v['kinds']))} · components: {E(names(comps, v['components']))} · patterns: {E(names(a.get('patterns'), v['patterns']))}"),
                ("Owner", E(rname(c["owner"])) + (f" · also {E(', '.join(rname(r) for r in c.get('also') or []))}" if c.get("also") else "")),
                ("Evidence", f"in: {E(', '.join(ev.get('docs') or []))}<br>looks like: {E(ev.get('looks_like', ''))}")]
        if sig:
            rows.append(("How the gap shows", f"<ul>{sig}</ul>"))
        if c.get("contradiction"):
            rows.append(("Compare", E(c["contradiction"])))
        rows += [("Due by", f'<table class="due">{due_rows}</table>'), ("Fail fast", E(c["fail_fast"]))]
        if c.get("signal_id"):
            rows.append(("Script signal", f"<code>{E(c['signal_id'])}</code> (found without AI)"))
        if rel:
            rows.append(("Related", rel))
        dl = "".join(f"<dt>{k}</dt><dd>{val}</dd>" for k, val in rows)
        return (f'<details class="chk" id="{c["id"]}" data-kind="{kind}" data-owner="{c["owner"]}" data-severity="{c["severity"]}" '
                f'data-component="{" ".join(comps)}" data-title="{E(c["title"])}">'
                f'<summary><span class="cid">{c["id"]}</span><span class="ctitle">{E(c["title"])}</span>'
                f'<span class="pill {c["severity"]}">{c["severity"]}</span><span class="pill mark" style="display:none"></span>'
                f'<span class="who">{E(rname(c["owner"]))}</span></summary>'
                f'<div class="cbody"><dl>{dl}</dl>{bind}'
                f'<div class="rev"><button data-m="keep">Keep</button><button data-m="change">Change</button><button data-m="drop">Drop</button>'
                f'<textarea placeholder="Your note: what to change, or why to drop"></textarea></div></div></details>')

    def section(kind, title, lede):
        cs = [c for c in cat["checks"] if c["kind"] == kind]
        out = f'<h2 class="grp" id="{kind}">{title} ({len(cs)})</h2><p>{lede}</p>'
        for con in v["concerns"][kind]:
            group = [c for c in cs if c["concern"] == con]
            if group:
                out += f'<h3 class="con" id="c-{con}">{E(concerns[con])} ({len(group)})</h3>' + "".join(card(c) for c in group)
        return out

    tech_only = [c for b in binds.values() for c in b["checks"]]
    jump = "".join(f'<div><a href="#c-{con}">{E(concerns[con])}</a> <span>{sum(1 for c in cat["checks"] if c["concern"] == con)}</span></div>'
                   for kind in ("technical", "delivery") for con in v["concerns"][kind])
    sel = lambda name, label, opts: (f'<select name="{name}" aria-label="{label}"><option value="">{label}: all</option>'
                                     + "".join(f'<option value="{k}">{E(t)}</option>' for k, t in opts) + "</select>")
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › <a href="/learn/technical-anchor/">The technical anchor</a> › <a href="/learn/technical-anchor/project-review/">Project review</a> › The checks</p>
<p class="eyebrow" style="margin-top:22px">Project review · the catalog</p>
<h1>The checks: all {len(cat['checks']) + len(tech_only)}, by category</h1>
<p class="lede">These are the questions the <a href="/learn/technical-anchor/project-review/">project review skill</a> asks of a data project's documents: {sum(1 for c in cat['checks'] if c['kind'] == 'technical')} technical, {sum(1 for c in cat['checks'] if c['kind'] == 'delivery')} about delivery, and {len(tech_only)} that only apply on Databricks. Open a check to see why it matters, when it applies, what good evidence looks like, by which stage it is due, and the cheapest test that could prove a team wrong.</p>
<p><b>To review them:</b> mark each check <b>Keep</b>, <b>Change</b> or <b>Drop</b> and add a note. Your marks stay in this browser. When you're done, <b>Copy my review</b> puts them on your clipboard as plain text to send back. The checks come from <a href="{REPO}">the repository</a>, so this page always matches the skill.</p>
<div class="jump">{jump}<div><a href="#tech">Databricks only</a> <span>{len(tech_only)}</span></div></div>
<div class="filters"><input id="f-q" type="search" placeholder="Search checks: duplicates, estimate, history…" aria-label="Search checks">
{sel("kind", "Type", [("technical", "Technical"), ("delivery", "Delivery"), ("tech", "Databricks only")])}
{sel("owner", "Owner", [(k, r["name"]) for k, r in roles.items()])}
{sel("severity", "Severity", [("high", "High"), ("medium", "Medium"), ("low", "Low")])}
{sel("component", "Component", [(k, k) for k in v["components"]])}
{sel("mark", "My review", [("none", "not reviewed yet"), ("keep", "keep"), ("change", "change"), ("drop", "drop")])}
<span class="count" id="f-count"></span></div>
{section("technical", "Technical checks", "What has to be true of the data and the platform: the things that make numbers wrong, loads fail or go-lives slip.")}
{section("delivery", "Delivery checks", "Why projects fail for reasons that have nothing to do with code: estimates, requirements, scope, planning, stakeholders, communication and handover. Each one says how the gap shows up in documents.")}
<h2 class="grp" id="tech">Databricks only ({len(tech_only)})</h2><p>Checks that only make sense on Databricks. Every common check above that works differently on Databricks also has an "On Databricks" box. {E(binds.get('databricks', {}).get('version_note') or '')}</p>
{"".join(card(c) for c in tech_only)}
<div class="revbar"><span id="rv-count"></span><button id="rv-copy">Copy my review</button><button class="ghost" id="rv-open">Open or close all shown</button><button class="ghost" id="rv-clear">Clear</button></div>
{JS}"""
    desc = (f"All {len(cat['checks']) + len(tech_only)} checks in the data-project-review skill, by category: technical, delivery and Databricks. "
            "Each with why it matters, when it applies, the evidence to look for, when it is due and a fail-fast test.")
    out = ROOT / "learn" / "technical-anchor" / "project-review" / "checks"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(wb.page("The project review checks, by category", desc, URL, body, CSS))
    print("review checks ->", out)


if __name__ == "__main__":
    main()
