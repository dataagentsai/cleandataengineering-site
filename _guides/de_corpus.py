"""The corpus backlog page, organised by phase and hop, with common versus per-dataset versus per-data-product work.

Used by de_essentials.corpus_page(). Unit of delivery: a KPI group and its dashboard (a data product).
For every layer: what is common (done once) and what repeats per source, per dataset, per data product.
Includes a planner: enter sources, datasets and data products, and see how many items to plan, by layer.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import de_essentials as DE  # noqa: E402
import de_ess_data as D  # noqa: E402
import de_ess_groups as G  # noqa: E402

E, table, fig, L, C = DE.E, DE.table, DE.fig, DE.L, DE.C
BASE = DE.BASE
HOP_NAME = {h[0]: h[1] for h in G.HOPS}
SCOPE_NAME = {s[0]: s[1] for s in G.SCOPES}


def page():
    items = []
    for it in D.BACKLOG:
        hop, phase, scope, theme = G.classify(it)
        items.append((it, hop, phase, scope, theme))
    # matrix counts hop x scope
    mat = {h[0]: {s[0]: 0 for s in G.SCOPES} for h in G.HOPS}
    for it, hop, phase, scope, theme in items:
        mat[hop][scope] += 1
    heat = lambda n: "" if n == 0 else ('class="y"' if n >= 6 else 'class="p"')
    mrows = ""
    tot = {s[0]: 0 for s in G.SCOPES}
    for h in G.HOPS:
        cells = "".join(f'<td class="c" {heat(mat[h[0]][s[0]])}>{mat[h[0]][s[0]] or ""}</td>' for s in G.SCOPES)
        for s in G.SCOPES:
            tot[s[0]] += mat[h[0]][s[0]]
        mrows += f'<tr><td><a href="#hop-{h[0]}"><b>{E(h[1])}</b></a></td>{cells}<td class="c"><b>{sum(mat[h[0]].values())}</b></td></tr>'
    mhead = "<tr><th>Hop or phase</th>" + "".join(f"<th>{E(s[1])}</th>" for s in G.SCOPES) + "<th>All</th></tr>"
    mfoot = "<tr><td><b>All items</b></td>" + "".join(f'<td class="c"><b>{tot[s[0]]}</b></td>' for s in G.SCOPES) + f'<td class="c"><b>{sum(tot.values())}</b></td></tr>'
    scopes = table(["Scope", "What it means", "Examples"], [[f"<b>{E(n)}</b>", E(d), E(e)] for k, n, d, e in G.SCOPES])
    disc_map = table(["Discovery document section", "Backlog items that cover it"], [[f"<b>{E(a)}</b>", " ".join(f'<a href="#{i}">{i}</a>' for i in b.split())] for a, b in D.DISC_MAP])
    sections = ""
    for h in G.HOPS:
        hop_items = [x for x in items if x[1] == h[0]]
        body = ""
        if h[0] == "discovery":
            themes = []
            for it, hop, phase, scope, theme in hop_items:
                if theme not in themes:
                    themes.append(theme)
            for th in themes:
                body += f'<h3 class="theme">{E(th)}</h3>' + "".join(det(x) for x in hop_items if x[4] == th)
        else:
            for ph in G.PHASES:
                xs = [x for x in hop_items if x[2] == ph]
                if xs:
                    body += f'<h3 class="theme">{ph}</h3>' + "".join(det(x) for x in xs)
        extra = f'<h3 class="theme">How the discovery document maps to items</h3>{disc_map}' if h[0] == "discovery" else ""
        sections += (f'<section id="hop-{h[0]}" class="area"><h2>{E(h[1])} <span class="note">({len(hop_items)} items)</span></h2><p class="sub">{E(h[2])} <b>{E(h[3])}</b></p>{extra}{body}</section>')
    js_items = [dict(id=it[0], hop=HOP_NAME[hop], phase=phase, scope=SCOPE_NAME[scope], title=it[1], owner=DE.seat_text(it[2]), type=it[3], stage=it[5], size=it[7], applies=it[6],
                     acceptance="; ".join(it[8].split("|")), evidence=it[9], depends=it[10], prevents=", ".join(map(str, it[4]))) for it, hop, phase, scope, theme in items]
    opts = lambda xs: "".join(f'<option value="{v}">{E(t)}</option>' for v, t in xs)
    f_hop = opts([("", "All hops and phases")] + [(h[0], h[1]) for h in G.HOPS])
    f_scope = opts([("", "Any scope")] + [(s[0], s[1]) for s in G.SCOPES])
    f_phase = opts([("", "Any phase")] + [(p, p) for p in G.PHASES])
    f_seat = opts([("", "Any owner"), ("BA", "BA"), ("TA", "Tech Anchor"), ("PM", "PM")])
    f_type = opts([("", "Any type")] + [(t, t) for t in ("Document", "Decision", "Spike", "Slice", "Run")])
    f_app = opts([("", "Always and conditional"), ("always", "Always"), ("cond", "Only when it applies")])
    n_by = {s: sum(1 for i in D.BACKLOG if s in [x.strip() for x in i[2].split("+")]) for s in ("BA", "TA", "PM")}
    css = """<style>
  .tf .filters { position:sticky; top:0; z-index:5; background:#fff; border:var(--line); border-radius:var(--wob); padding:10px 14px; margin:18px 0; display:flex; flex-wrap:wrap; gap:8px 10px; align-items:center; font-size:14.5px; }
  .tf .filters select, .tf .filters input, .tf .plan input { font:inherit; font-size:14px; border:1.5px solid var(--ink); border-radius:10px; padding:4px 8px; background:#fff; color:var(--ink); }
  .tf .filters input { flex:1; min-width:150px; } .tf .filters button { font:inherit; font-size:14px; border:1.5px solid var(--ink); border-radius:10px; padding:4px 12px; background:var(--butter-wash); cursor:pointer; }
  .tf .filters .count { color:var(--muted); font-size:13.5px; margin-left:auto; }
  .tf details.itm { border:var(--line); border-radius:12px; margin:8px 0; background:#fff; } .tf details.itm[open] { background:#FDFCF8; }
  .tf details.itm > summary { list-style:none; cursor:pointer; padding:9px 14px; display:flex; flex-wrap:wrap; gap:6px 10px; align-items:baseline; }
  .tf details.itm > summary::-webkit-details-marker { display:none; } .tf details.itm > summary::before { content:"›"; color:var(--faint); display:inline-block; } .tf details.itm[open] > summary::before { transform:rotate(90deg); }
  .tf .cid { font-family:var(--mono, monospace); font-size:13px; font-weight:700; } .tf .ctitle { font-weight:700; flex:1; min-width:220px; }
  .tf .pill { font-size:12px; font-weight:700; border:1.5px solid var(--ink); border-radius:999px; padding:0 8px; background:#fff; white-space:nowrap; } .tf .pill.sc { background:var(--butter-wash); }
  .tf .ibody { padding:0 18px 10px; font-size:15px; } .tf .ibody ul { margin:4px 0 8px; } .tf section.area h2 .note { font-size:14px; font-family:inherit; } .tf h3.theme { margin:18px 0 4px; font-size:19px; }
  .tf section.area p.sub { color:#52514e; margin:0 0 6px; }
  .tf .plan { border:var(--line); border-radius:var(--wob); padding:10px 16px; background:#fff; margin:12px 0; } .tf .plan label { margin-right:14px; font-size:15px; } .tf .plan input { width:64px; }
</style>"""
    js = """<script>
const ITEMS = %s; const MAT = %s; const SC = ['project','platform','source','dataset','product']; const HOPS = %s;
function q(id){return document.getElementById(id)}
function apply(){
  const f={hop:q('f-hop').value,scope:q('f-scope').value,phase:q('f-phase').value,seat:q('f-seat').value,type:q('f-type').value,app:q('f-app').value,text:q('f-text').value.toLowerCase()};
  let shown=0;
  document.querySelectorAll('details.itm').forEach(d=>{const ok=(!f.hop||d.dataset.hop===f.hop)&&(!f.scope||d.dataset.scope===f.scope)&&(!f.phase||d.dataset.phase===f.phase)&&(!f.seat||d.dataset.seat.split(' ').includes(f.seat))&&(!f.type||d.dataset.type===f.type)&&(!f.app||d.dataset.app===f.app)&&(!f.text||d.textContent.toLowerCase().includes(f.text));d.style.display=ok?'':'none';if(ok)shown++;});
  document.querySelectorAll('section.area').forEach(s=>{s.style.display=[...s.querySelectorAll('details.itm')].some(d=>d.style.display!=='none')?'':'none';});
  q('count').textContent=shown+' of '+ITEMS.length+' items';
}
function plan(){
  const n={project:1,platform:1,source:+q('p-src').value||0,dataset:+q('p-ds').value||0,product:+q('p-prod').value||0};
  let rows='',tc=0,tp=0,ts=0,td=0,tpr=0;
  HOPS.forEach(h=>{const m=MAT[h[0]];const c=m.project+m.platform,s=m.source*n.source,d=m.dataset*n.dataset,p=m.product*n.product,t=c+s+d+p;
    rows+='<tr><td><b>'+h[1]+'</b></td><td class="c">'+c+'</td><td class="c">'+s+'</td><td class="c">'+d+'</td><td class="c">'+p+'</td><td class="c"><b>'+t+'</b></td></tr>';tc+=c;ts+=s;td+=d;tpr+=p;});
  const tot=tc+ts+td+tpr;
  rows+='<tr><td><b>Total item instances</b></td><td class="c"><b>'+tc+'</b></td><td class="c"><b>'+ts+'</b></td><td class="c"><b>'+td+'</b></td><td class="c"><b>'+tpr+'</b></td><td class="c"><b>'+tot+'</b></td></tr>';
  q('plan-rows').innerHTML=rows;
  q('plan-note').textContent='Common work (once): '+tc+' of '+tot+' item instances ('+Math.round(100*tc/Math.max(tot,1))+'%%). Each further data product that reuses the common work and the same datasets adds about '+Object.values(MAT).reduce((a,m)=>a+m.product,0)+' items.';
}
['f-hop','f-scope','f-phase','f-seat','f-type','f-app'].forEach(i=>q(i).addEventListener('change',apply));q('f-text').addEventListener('input',apply);
['p-src','p-ds','p-prod'].forEach(i=>q(i).addEventListener('input',plan));
q('f-csv').addEventListener('click',()=>{const cols=['id','hop','phase','scope','title','owner','type','stage','size','applies','acceptance','evidence','depends','prevents'];const e=v=>'"'+String(v).replace(/"/g,'""')+'"';
  const rows=[cols.join(',')].concat(ITEMS.map(i=>cols.map(c=>e(i[c])).join(',')));const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([rows.join('\\n')],{type:'text/csv'}));a.download='data-project-backlog.csv';a.click();});
if(location.hash&&q(location.hash.slice(1))&&q(location.hash.slice(1)).tagName==='DETAILS')q(location.hash.slice(1)).open=true;
apply();plan();
</script>""" % (json.dumps(js_items, ensure_ascii=False), json.dumps(mat), json.dumps([[h[0], h[1]] for h in G.HOPS]))
    qa = [("What is a data product here?", "A group of KPIs and the dashboard that shows them, with the datasets they need. It is the unit you deliver and accept. One project may deliver several."),
          ("How do I use the matrix?", "Read down the columns. The first two columns are done once. The last three repeat. To plan, enter how many sources, datasets and data products you have, and read off the number of items to plan."),
          ("Is this a Jira backlog?", "No. It is a reusable starting list at scope level, between an epic and a task. Download the CSV, keep what applies, and split items into tasks in your own tool.")]
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/how-we-work/">How we work</a> › <a href="{BASE}">Data essentials</a> › Corpus backlog</p>
<p class="eyebrow" style="margin-top:22px">Topic 13 · The reusable backlog</p>
<h1>The corpus backlog for a data project</h1>
<p class="lede">{len(D.BACKLOG)} backlog items for a data project, organised by phase and by hop: Discovery (the full list), then Source to Land, Land to Bronze, Bronze to Silver, Silver to Gold, Gold to Semantic and Semantic to Consumption. Each item says whether it is common work done once, or repeats per source, per dataset or per data product, where the unit of delivery is a group of KPIs and the dashboard for them.</p>
<div class="tf">{css}
<section id="idea"><p class="eyebrow">The idea</p><h2>One KPI group and its dashboard, traced through every layer</h2>
<p>Take a group of KPIs and the dashboard that shows them. To deliver it, work happens in every layer. Some of that work is <b>common</b>: environments, access model, standards, metadata store. You do it once. Some is <b>per source</b> or <b>per dataset</b>: profile it, agree its keys, load it, clean it. Some is <b>per data product</b>: define the KPIs, build the facts, reconcile, accept the dashboard. The matrix counts the items in each cell.</p>
{scopes}
<h3 style="margin-top:18px">The matrix: items by hop and by how often they repeat</h3><div class="tw"><table class="t">{mhead}{mrows}{mfoot}</table></div>
<div class="box"><b>Why it matters:</b> the first data product pays for the common work. Later products reuse it, and only repeat the per-dataset and per-product items. That is where estimates and plans usually go wrong.</div></section>
<section id="planner"><p class="eyebrow">Planner</p><h2>How many items for your project?</h2>
<div class="plan"><label>Source systems <input id="p-src" type="number" min="0" value="2"></label><label>Datasets (tables) <input id="p-ds" type="number" min="0" value="6"></label><label>Data products (KPI group + dashboard) <input id="p-prod" type="number" min="0" value="1"></label></div>
<div class="tw"><table class="t"><tr><th>Hop or phase</th><th>Common (once)</th><th>Per source</th><th>Per dataset</th><th>Per data product</th><th>Total</th></tr><tbody id="plan-rows"></tbody></table></div><p class="note" id="plan-note"></p>
<p class="note">Counts are item instances to plan, not days. Scope tags are guidance; trim with 'applies when'.</p></section>
<section id="how"><p class="eyebrow">How to use it</p><h2>Start with all, remove what does not apply</h2>
<p>Items owned by BA: {n_by['BA']}, Tech Anchor: {n_by['TA']}, PM: {n_by['PM']}. Types: <b>Document</b> (write it down), <b>Decision</b> (someone decides), <b>Spike</b> (learn something risky, timeboxed), <b>Slice</b> (a thin working piece), <b>Run</b> (a repeated activity). Phase follows the lifecycle stage: Discover (stages 1 to 3), Design (4), Build (5 to 6), Test (7), Run and close (8 to 10).</p>
<div class="box"><b>Do not skip Discovery.</b> It is cheap, and it prevents the causes that are most expensive later.</div></section>
<div class="filters"><select id="f-hop">{f_hop}</select><select id="f-scope">{f_scope}</select><select id="f-phase">{f_phase}</select><select id="f-seat">{f_seat}</select><select id="f-type">{f_type}</select><select id="f-app">{f_app}</select>
<input id="f-text" type="search" placeholder="Search"><button id="f-csv" type="button">Download CSV</button><span class="count" id="count"></span></div>
{sections}
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(qa)}</section>
<div class="pn">{L(BASE + 'layers/across/', '← Across everything')}{L(BASE, 'The roadmap')}{L(BASE + 'plan/', 'Next: plan and estimates →')}</div>
{js}
</div>"""
    title = "The corpus backlog for a data project"
    desc = (f"{len(D.BACKLOG)} reusable backlog items for a data project, organised by hop from Discovery to Semantic and Consumption, tagged common versus per source, per dataset or per data product, "
            "with a planner and CSV download.")
    return f"{BASE}backlog/", DE.page_shell(title, desc, f"{BASE}backlog/", body, [("How we work", "/how-we-work/"), ("Data essentials", BASE), ("Corpus backlog", BASE + "backlog/")], qa)


def det(x):
    it, hop, phase, scope, theme = x
    iid, title, seat, typ, prev, stage, applies, size, ac, evid, dep = it
    acl = "<ul>" + "".join(f"<li>{E(a)}</li>" for a in ac.split("|")) + "</ul>"
    seats = " ".join(s.strip() for s in seat.split("+"))
    return (f'<details class="itm" id="{iid}" data-hop="{hop}" data-scope="{scope}" data-phase="{phase}" data-seat="{seats}" data-type="{typ}" data-app="{"always" if applies == "Always" else "cond"}">'
            f'<summary><span class="cid">{iid}</span><span class="ctitle">{E(title)}</span><span class="pill">{E(DE.seat_text(seat))}</span><span class="pill">{typ}</span><span class="pill sc">{E(SCOPE_NAME[scope])}</span>'
            f'<span class="pill">stage {stage}</span><span class="pill">{size}</span></summary>'
            f'<div class="ibody"><p><b>Done when</b></p>{acl}<p><b>Evidence:</b> {E(evid)}</p><p><b>Depends on:</b> {E(dep)}</p>'
            f'<p><b>Where:</b> {E(HOP_NAME[hop])} · <b>Phase:</b> {phase} · <b>Scope:</b> {E(SCOPE_NAME[scope])} · <b>Stage:</b> {E(DE.stage_word(stage))} · <b>Applies when:</b> {E(applies)}</p>'
            f'<p><b>Prevents causes:</b> {DE.cause_links(prev)}</p></div></details>')
