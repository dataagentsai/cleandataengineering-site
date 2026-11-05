"""The hard problems of each data layer, and how to solve them: a hub, one page per layer or hop, and a filterable
list, under /learn/hard-problems/.

    uv run --no-project --with pyyaml python3 _guides/hard_problems_export.py ~/data-platform-catalog
    python3 _guides/hard_problems.py

The content comes from the data platform catalog's layers (one record per layer or hop), exported to
_guides/hard_problems.json. Teach first: the plain picture, then the tables.
"""
import json
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "_paths"))
import components as C  # noqa: E402  (page CSS, faq())
import realtime as R  # noqa: E402  (ld(), short_desc(), shared CSS)
from diagrams import FILL, arrow, svg, text  # noqa: E402

wb = C.wb
SITE = wb.SITE
BASE = "/learn/hard-problems/"
CHECKS_URL = "/learn/shift-left/all-checks/"
faq = C.faq
CSS = R.CSS

DATA = json.loads((Path(__file__).parent / "hard_problems.json").read_text())
LAYERS = sorted(DATA["layers"], key=lambda x: x["order"])
ALL = [dict(c, layer=L["id"], layer_title=L["title"].replace("Semantic to experiences", "Semantic to UI")) for L in LAYERS for c in L["challenges"]]
N = len(ALL)
SLUG = {L["id"]: L["id"].replace("_", "-") for L in LAYERS}
SHORT = {L["id"]: L["title"].replace("Semantic to experiences", "Semantic to UI") for L in LAYERS}
VERDICT = {"solve": "solved", "assist": "assisted", "people_decide": "people decide"}
VTIP = {"solve": "once the decision is declared, the engine does it and a test proves it",
        "assist": "the tool suggests, warns and tests; a person confirms",
        "people_decide": "a business decision; the tool records it, versions it and enforces it"}
STATUS = {"built": "built", "building": "building", "designed": "designed", "gap": "gap"}
COLOUR = {"source": "grey", "ingestion": "sky", "bronze": "bronze", "silver": "silver", "gold": "gold",
          "semantic": "lilac"}
HARDEST = {"silver_to_gold", "gold_to_semantic"}


def fill(lid):
    return FILL["butter"] if "_to_" in lid else FILL[COLOUR.get(lid, "peri")]


def counts(chs):
    return {v: sum(c["verdict"] == v for c in chs) for v in VERDICT}


def fig(s, cap):
    return f'<figure class="diagram">{s}<figcaption>{cap}</figcaption></figure>'


def wrap(t, n):
    out, line = [], ""
    for w in t.split():
        if len(line) + len(w) + 1 > n:
            out.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    return out + ([line] if line else [])


def badge(kind, v):
    label = VERDICT.get(v, v) if kind == "v" else STATUS.get(v, v)
    return f'<span class="hp-b hp-{kind}-{v}">{E(label)}</span>'


def htable(head, rows):
    h = "".join(f"<th>{E(x)}</th>" for x in head)
    r = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f'<div class="tw"><table class="t hp-t"><tr>{h}</tr>{r}</table></div>'


# ------------------------------------------------------------------ drawings
def flow_map():
    """Ten layers and hops as one snake: 1 to 5 left to right, 6 to 10 right to left."""
    w, h, gx, gy, x0, y0 = 196, 176, 22, 64, 12, 34
    pos = {}
    for i, L in enumerate(LAYERS):
        r, k = divmod(i, 5)
        col = k if r == 0 else 4 - k
        pos[L["id"]] = (x0 + col * (w + gx), y0 + r * (h + gy))
    b = text(545, 20, "the data flow, from the source system to the screen", 15)
    for i, L in enumerate(LAYERS):
        x, y = pos[L["id"]]
        hard = L["id"] in HARDEST
        b += (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill(L["id"])}" stroke="#1F1F1F" '
              f'stroke-width="{3 if hard else 1.6}"{"" if not L["hop"] else " stroke-dasharray=\"7 5\""}/>')
        b += text(x + 12, y + 24, f"{L['order']}", 15, anchor="start", fill="#888")
        b += text(x + w / 2, y + 30, SHORT[L["id"]], 20, fill="#1F1F1F")
        c = counts(L["challenges"])
        b += text(x + w / 2, y + 54, f"{c['solve']} solved · {c['assist']} assisted · {c['people_decide']} decide", 14)
        yy = y + 84
        for ch in L["challenges"][:2]:
            lines = wrap(ch["title"], 22)
            if len(lines) > 2:
                lines = [lines[0], lines[1] + "…"]
            for j, ln in enumerate(lines):
                b += text(x + 12, yy, ("· " if j == 0 else "  ") + ln, 15, anchor="start", fill="#1F1F1F")
                yy += 19
            yy += 6
        if hard:
            b += (f'<rect x="{x + w - 70}" y="{y - 12}" width="64" height="22" rx="11" fill="#FCE4EC" stroke="#1F1F1F" '
                  f'stroke-width="1.2"/>') + text(x + w - 38, y + 4, "hardest", 12, fill="#1F1F1F")
    for i in range(len(LAYERS) - 1):
        (x1, y1), (x2, y2) = pos[LAYERS[i]["id"]], pos[LAYERS[i + 1]["id"]]
        if y1 == y2 and x2 > x1:
            b += arrow(x1 + w + 2, y1 + h / 2, x2 - 2, y2 + h / 2)
        elif y1 == y2:
            b += arrow(x1 - 2, y1 + h / 2, x2 + w + 2, y2 + h / 2)
        else:
            b += arrow(x1 + w / 2, y1 + h + 2, x2 + w / 2, y2 - 14)
    return svg(1090, y0 + 2 * h + gy + 12, b, "Ten layers and hops from source to screen, each with its headline challenges and how many are solved, assisted or left to people. Silver to gold and gold to semantic are marked hardest.")


def two_kinds():
    b = '<rect x="10" y="10" width="420" height="190" rx="16" fill="#FBF4EC" stroke="#1F1F1F" stroke-width="1.6"/>'
    b += text(220, 40, "Bronze to silver: make one source faithful", 16, fill="#1F1F1F")
    b += (f'<rect x="40" y="62" width="110" height="44" rx="10" fill="#fff" stroke="#1F1F1F" stroke-width="1.4"/>'
          + text(95, 89, "one source", 14, fill="#1F1F1F") + arrow(152, 84, 200, 84)
          + f'<rect x="204" y="58" width="196" height="52" rx="10" fill="{FILL["peri"]}" stroke="#1F1F1F" stroke-width="1.4"/>'
          + text(302, 82, "the same steps", 14, fill="#1F1F1F") + text(302, 100, "for every source", 12.5))
    b += text(220, 140, "duplicates, bad files, schema changes,", 13.5) + text(220, 160, "deletes, out-of-order changes", 13.5)
    b += text(220, 188, "hard, but mechanical", 15, fill="#2E7D4F")
    b += '<rect x="460" y="10" width="420" height="190" rx="16" fill="#FFF8E8" stroke="#1F1F1F" stroke-width="3"/>'
    b += text(670, 40, "Silver to gold: make many sources agree", 16, fill="#1F1F1F")
    for i, t in enumerate(["orders", "deliveries", "dealers"]):
        y = 56 + i * 26
        b += (f'<rect x="484" y="{y}" width="96" height="22" rx="7" fill="#fff" stroke="#1F1F1F" stroke-width="1.2"/>'
              + text(532, y + 16, t, 12.5, fill="#1F1F1F") + arrow(582, y + 11, 640, 92))
    b += (f'<rect x="644" y="66" width="214" height="52" rx="10" fill="{FILL["gold"]}" stroke="#1F1F1F" stroke-width="1.4"/>'
          + text(751, 89, "one fact, one number", 14, fill="#1F1F1F") + text(751, 107, "keys, grain, time, meaning", 12.5))
    b += text(670, 150, "dropped rows, keys, grain, history,", 13.5) + text(670, 170, "completeness, late data, definitions", 13.5)
    b += text(670, 194, "needs judgment about meaning and timing", 15, fill="#9A5B00")
    return svg(890, 210, b, "Bronze to silver makes one source faithful with the same steps for every source. Silver to gold makes many sources agree and needs judgment about meaning and timing.")


def strip(cur):
    cw, gap = 104, 4
    b = ""
    for i, L in enumerate(LAYERS):
        x = 8 + i * (cw + gap)
        on = L["id"] == cur
        b += (f'<rect x="{x}" y="8" width="{cw}" height="58" rx="10" fill="{"#1F1F1F" if on else fill(L["id"])}" '
              f'stroke="#1F1F1F" stroke-width="{2.4 if on else 1.2}"/>')
        lines = wrap(SHORT[L["id"]], 12)
        for j, ln in enumerate(lines[:2]):
            yy = 42 + (j - (len(lines[:2]) - 1) / 2) * 18
            b += text(x + cw / 2, yy, ln, 15, fill="#FFFFFF" if on else "#1F1F1F")
    return svg(8 + len(LAYERS) * (cw + gap), 74, b, f"Where this page sits in the flow: {SHORT[cur]}, highlighted among the ten layers and hops.")


def verdict_bar(chs):
    c = counts(chs)
    tot = max(1, len(chs))
    cols = [("solve", "#CDEBD8"), ("assist", "#FFE7A3"), ("people_decide", "#F8C9D9")]
    b, x, W = "", 10, 760
    for v, col in cols:
        w = W * c[v] / tot
        if w:
            b += f'<rect x="{x}" y="14" width="{w}" height="40" fill="{col}" stroke="#1F1F1F" stroke-width="1.2"/>'
            if w > 80:
                b += text(x + w / 2, 40, f"{c[v]} {VERDICT[v]}", 14, fill="#1F1F1F")
            x += w
    st = {s: sum(ch["status"] == s for ch in chs) for s in STATUS}
    b += text(10, 80, "Status: " + ", ".join(f"{st[s]} {s}" for s in STATUS if st[s]), 14, anchor="start", fill="#1F1F1F")
    return svg(780, 92, b, f"{c['solve']} solved, {c['assist']} assisted, {c['people_decide']} left to people; " + ", ".join(f"{st[s]} {s}" for s in STATUS if st[s]) + ".")


# ------------------------------------------------------------------ pages
def nav(cur):
    items = "".join(f'<span>{E(SHORT[L["id"]])}</span>' if L["id"] == cur else f'<a href="{BASE}{SLUG[L["id"]]}/">{E(SHORT[L["id"]])}</a>' for L in LAYERS)
    other = '<span>All challenges</span>' if cur == "all" else f'<a href="{BASE}all-challenges/">All challenges</a>'
    return f'<div class="sib"><a href="{BASE}">↑ All layers</a>{items}{other}</div>'


def checks_links(c):
    if not c["checks"]:
        return ""
    links = ", ".join(f'<a href="{CHECKS_URL}#q={E(x)}">{E(x)}</a>' for x in c["checks"])
    more = f" and {c['n_checks'] - len(c['checks'])} more" if c["n_checks"] > len(c["checks"]) else ""
    return f'<p class="note">Shift-left checks that guard it: {links}{more}.</p>'


def refs(c):
    bits = []
    if c["dac"]:
        bits.append("assurance rules " + ", ".join(E(d) for d in c["dac"]))
    if c["adr"]:
        bits.append("decisions " + "; ".join(E(a["id"] + (" " + a["title"] if a["title"] else "")) for a in c["adr"]))
    return f'<p class="note">{"; ".join(bits)}.</p>' if bits else ""


def layer_page(L):
    i = LAYERS.index(L)
    chs, aps = L["challenges"], L["anti_patterns"]
    rows = []
    for c in chs:
        ex = E(c["example"]) + (f' <span class="note">(tested on day {c["world_day"]})</span>' if c.get("world_day") else "")
        rows.append((f'<b>{E(c["title"])}</b><br><span class="note">{E(c["id"])}</span>', E(c["goes_wrong"]), ex,
                     E(c["solution"]) + refs(c) + checks_links(c), badge("v", c["verdict"]), badge("s", c["status"])))
    ap_rows = [(f'<b>{E(a["title"])}</b>', E(a["why"]), E(a["instead"])) for a in aps]
    hop = "This is a hop: the step that moves data from one layer to the next. " if L["hop"] else ""
    hard = ('<p class="hp-hard"><b>One of the two hardest steps.</b> ' + ("This is the first place several sources meet, so keys, grain, time and meaning have to agree. " if L["id"] == "silver_to_gold" else "Numbers leave the data team here and reach people, tools and agents, so one definition has to hold everywhere. ") + "Most of the work is business decisions, which is why they are declared and tested rather than coded by hand.</p>") if L["id"] in HARDEST else ""
    nxt = LAYERS[i + 1] if i + 1 < len(LAYERS) else None
    body = f"""<section id="where"><p class="eyebrow">Where we are</p><h2>{E(SHORT[L["id"]])}</h2>
{fig(strip(L["id"]), "The ten layers and hops from source to screen. The dark box is this page.")}
<p><b>What this {"hop" if L["hop"] else "layer"} must achieve.</b> {E(L["purpose"])}</p>
<p>{hop}Handled by: {E(", ".join(L["components"]))}.</p>{hard}</section>

<section id="challenges"><p class="eyebrow">The hard part</p><h2>{len(chs)} challenges, and how they are solved</h2>
{fig(verdict_bar(chs), "Solved means the engine does it once the decision is declared, and a test proves it. Assisted means the tool suggests and checks, and a person confirms. People decide means a business decision the tool records and enforces.")}
<p>Every example comes from the tyre world, a synthetic tyre company whose fourteen simulated days carry planted problems with known right answers, so each fix is tested, not just described.</p>
{htable(["Challenge", "What goes wrong", "Tyre-world example", "How we solve it", "Verdict", "Status"], rows)}</section>

<section id="anti"><p class="eyebrow">What not to do</p><h2>Common anti-patterns</h2>
<p>An anti-pattern is a habit that looks reasonable and keeps causing the same damage. These are the ones seen most often at this {"hop" if L["hop"] else "layer"}.</p>
{htable(["Anti-pattern", "Why it hurts", "Do this instead"], ap_rows)}</section>"""
    qa = [(f"What are the hardest problems in the {SHORT[L['id']].lower()} {'step' if L['hop'] else 'layer'}?", "; ".join(c["title"] for c in chs[:5]) + "."),
          (f"What is the most common mistake at {SHORT[L['id']].lower()}?", (aps[0]["title"] + ". " + aps[0]["instead"]) if aps else "See the challenges above.")]
    desc = f"The hard challenges and common anti-patterns of {SHORT[L['id']].lower()} in a data platform, with how each is solved and tested. This {'hop' if L['hop'] else 'layer'} must {L['purpose'][0].lower() + L['purpose'][1:]}"
    return SLUG[L["id"]], SHORT[L["id"]], f"{SHORT[L['id']]}: hard problems and anti-patterns", desc, body, qa, (nxt and (SLUG[nxt["id"]], SHORT[nxt["id"]]))


def all_page():
    data = json.dumps(ALL, ensure_ascii=False).replace("</", "<\\/")
    body = f"""<section id="list"><p class="eyebrow">Every challenge</p><h2>All {N} challenges, filterable</h2>
<p>Every challenge across the ten layers and hops. Filter by layer, verdict and status, or search; the filters stay in the page address, so a filtered list can be shared. Open a row to see what goes wrong, the tyre-world example, how it is solved, and the rules and checks behind it.</p>
<div class="slf">
<input id="hpq" type="search" placeholder="Search title, problem, example or fix" aria-label="Search challenges">
<div id="hpsel"></div>
<p class="slcount"><b id="hpn"></b> <button type="button" id="hpclear">Clear filters</button></p>
</div>
<div class="tw"><table class="t slt"><thead><tr><th>Challenge</th><th>Layer</th><th>Verdict</th><th>Status</th></tr></thead><tbody id="hpbody"></tbody></table></div>
<script id="hpdata" type="application/json">{data}</script>
<script>{JS}</script></section>"""
    c = counts(ALL)
    qa = [("How many of these problems can a tool solve?", f"Of {N}, {c['solve']} are solved once the decision is declared, {c['assist']} are assisted (the tool suggests and checks, a person confirms) and {c['people_decide']} are business decisions people make, which the tool records and enforces."),
          ("Where are the hardest problems?", "Silver to gold and gold to semantic: the first place several sources meet, and the place where numbers reach people, tools and agents.")]
    return "all-challenges", "All challenges", "Every hard problem across the data layers, filterable", f"All {N} hard problems of a data platform from source to screen, filterable by layer, verdict and status, with how each is solved and tested.", body, qa, None


JS = r"""
(function(){
var D=JSON.parse(document.getElementById('hpdata').textContent);
var VL={solve:'solved',assist:'assisted',people_decide:'people decide'};
var F=[['layer','Layer',function(c){return [c.layer_title]}],['verdict','Verdict',function(c){return [c.verdict]}],['status','Status',function(c){return [c.status]}]];
var st={q:''};F.forEach(function(f){st[f[0]]=''});
function rd(){var h=location.hash.slice(1);if(!h)return;h.split('&').forEach(function(p){var kv=p.split('=');if(kv[0] in st)st[kv[0]]=decodeURIComponent(kv[1]||'')});}
function wr(){var p=[];for(var k in st){if(st[k])p.push(k+'='+encodeURIComponent(st[k]))}history.replaceState(null,'',p.length?'#'+p.join('&'):location.pathname);}
function lab(k,v){return k==='verdict'?(VL[v]||v):v}
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(m){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]})}
function ok(c,skip){if(st.q){var t=(c.id+' '+c.title+' '+c.goes_wrong+' '+c.example+' '+c.solution+' '+c.layer_title).toLowerCase();if(t.indexOf(st.q.toLowerCase())<0)return false;}
 for(var i=0;i<F.length;i++){var f=F[i];if(f[0]===skip||!st[f[0]])continue;if(f[2](c).indexOf(st[f[0]])<0)return false;}return true;}
var ORD={};D.forEach(function(c,i){if(!(c.layer_title in ORD))ORD[c.layer_title]=i});
function sel(){var h='';F.forEach(function(f){var cnt={};D.forEach(function(c){if(!ok(c,f[0]))return;f[2](c).forEach(function(v){cnt[v]=(cnt[v]||0)+1})});
 var all={};D.forEach(function(c){f[2](c).forEach(function(v){all[v]=1})});var keys=Object.keys(all);
 keys.sort(function(a,b){return f[0]==='layer'?ORD[a]-ORD[b]:(a<b?-1:1)});
 var o='<label>'+f[1]+'<select data-k="'+f[0]+'"><option value="">All</option>';
 keys.forEach(function(v){o+='<option value="'+esc(v)+'"'+(st[f[0]]===v?' selected':'')+'>'+esc(lab(f[0],v))+' ('+(cnt[v]||0)+')</option>'});
 h+=o+'</select></label>'});document.getElementById('hpsel').innerHTML=h;
 Array.prototype.forEach.call(document.querySelectorAll('#hpsel select'),function(s){s.onchange=function(){st[s.dataset.k]=s.value;go()}});}
function rows(){var r=D.filter(function(c){return ok(c,null)});document.getElementById('hpn').textContent=r.length+' of '+D.length+' challenges';
 var h='';r.forEach(function(c){
 var ch=c.checks.length?'<p class="note">Shift-left checks that guard it: '+c.checks.map(function(x){return '<a href="/learn/shift-left/all-checks/#q='+esc(x)+'">'+esc(x)+'</a>'}).join(', ')+(c.n_checks>c.checks.length?' and '+(c.n_checks-c.checks.length)+' more':'')+'.</p>':'';
 var rf=(c.dac.length?'assurance rules '+esc(c.dac.join(', ')):'')+(c.adr.length?(c.dac.length?'; ':'')+'decisions '+c.adr.map(function(a){return esc(a.id+' '+a.title)}).join('; '):'');
 h+='<tr class="slr" data-id="'+c.id+'"><td><b>'+esc(c.title)+'</b><br><span class="note">'+c.id+'</span></td><td>'+esc(c.layer_title)+'</td><td><span class="hp-b hp-v-'+c.verdict+'">'+esc(VL[c.verdict])+'</span></td><td><span class="hp-b hp-s-'+c.status+'">'+esc(c.status)+'</span></td></tr>'+
 '<tr class="sld" id="d-'+c.id+'" hidden><td colspan="4"><p><b>What goes wrong.</b> '+esc(c.goes_wrong)+'</p><p><b>Tyre-world example.</b> '+esc(c.example)+(c.world_day?' (tested on day '+c.world_day+')':'')+'</p><p><b>How we solve it.</b> '+esc(c.solution)+'</p>'+(rf?'<p class="note">'+rf+'.</p>':'')+ch+'</td></tr>'});
 document.getElementById('hpbody').innerHTML=h||'<tr><td colspan="4">No challenge matches these filters.</td></tr>';
 Array.prototype.forEach.call(document.querySelectorAll('tr.slr'),function(t){t.onclick=function(){var d=document.getElementById('d-'+t.dataset.id);d.hidden=!d.hidden}});}
function go(){wr();sel();rows();}
rd();var q=document.getElementById('hpq');q.value=st.q;q.oninput=function(){st.q=q.value;go()};
document.getElementById('hpclear').onclick=function(){for(var k in st)st[k]='';q.value='';go()};
go();})();
"""

HP_CSS = """<style>
.hp-b{display:inline-block;border-radius:999px;padding:1px 9px;font-size:12.5px;font-weight:600;border:1.3px solid #1F1F1F;white-space:nowrap}
.hp-v-solve{background:#CDEBD8}.hp-v-assist{background:#FFE7A3}.hp-v-people_decide{background:#F8C9D9}
.hp-s-built{background:#fff}.hp-s-building{background:#E4ECFA}.hp-s-designed{background:#F3F3F1}.hp-s-gap{background:#FCE4EC}
table.hp-t td{vertical-align:top}table.hp-t td p.note{margin:6px 0 0;font-size:13px}
.hp-hard{border-left:4px solid #C2185B;padding:6px 12px;background:#FFF5F8}
.slf input[type=search]{width:100%;max-width:520px;padding:9px 12px;font-size:16px;border:1.6px solid #1F1F1F;border-radius:10px;margin:6px 0 10px;box-sizing:border-box}
#hpsel{display:flex;flex-wrap:wrap;gap:8px 12px}#hpsel label{display:flex;flex-direction:column;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--faint)}
#hpsel select{font-size:14px;padding:5px 6px;border:1.4px solid #1F1F1F;border-radius:8px;background:#fff;max-width:240px;text-transform:none;letter-spacing:0;color:var(--ink)}
.slcount{margin:12px 0 4px}.slcount button{margin-left:10px;font-size:13px;border:1.4px solid #1F1F1F;border-radius:999px;background:#fff;padding:2px 12px;cursor:pointer}
tr.slr{cursor:pointer}tr.slr:hover td{background:var(--butter-wash)}tr.sld td{background:#FAFAF8}tr.sld p{margin:4px 0 8px}
</style>"""


def render(slug, short, title, desc, body, qa, nxt, cur, num):
    url = f"{SITE}{BASE}{slug}/"
    full = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › <a href="{BASE}">Hard problems by layer</a> › {E(short)}</p>
<p class="eyebrow" style="margin-top:22px">Hard problems by layer · {num}</p>
<h1>{E(title)}</h1>
<p class="lede">{E(desc)}</p>{nav(cur)}
{body}
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{faq(qa)}</section>
<section id="next"><p class="eyebrow">Next</p><h2>Where to go next</h2>
{f'<p><b>Next:</b> <a href="{BASE}{nxt[0]}/">{E(nxt[1])}</a></p>' if nxt else ''}
<p><a href="{BASE}">↑ All layers</a> · <a href="{BASE}all-challenges/">All {N} challenges, filterable</a> · <a href="/learn/shift-left/">Shift left: fail fast on data code</a> · <a href="/learn/medallion-architecture/">Medallion architecture</a></p>
{nav(cur)}</section>"""
    crumbs = [("Learn", f"{SITE}/learn/"), ("Hard problems by layer", f"{SITE}{BASE}"), (short, url)]
    return wb.page(title, R.short_desc(desc), url, full, CSS + HP_CSS + R.ld(title, desc, url, qa, crumbs))


def hub():
    url = f"{SITE}{BASE}"
    c = counts(ALL)
    cards = "".join(f'<a href="{BASE}{SLUG[L["id"]]}/"><span class="n">{L["order"]}{" · hop" if L["hop"] else ""}</span><b>{E(SHORT[L["id"]])}</b><span>{E(L["purpose"])}</span></a>' for L in LAYERS)
    rules = [("Keep event time; never trust arrival order", "Every record has two times: when it happened and when it reached us. Joins, windows and history use when it happened."),
             ("Never drop; mark it", "A row with no match gets an unknown member, a late row gets a flag, a partial window gets a provisional flag. Dropping hides the problem; marking makes it visible and fixable."),
             ("Make every output recomputable per window", "Writes replace a window instead of appending to it, so a late file or a correction simply means rerunning that window."),
             ("Write the business policy down, per dataset", "How long to wait for late data, whether to publish provisional numbers, when a period closes, what a metric means. These are decisions, so they are declared, versioned and tested.")]
    rule_rows = "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td></tr>" for a, b in rules)
    qa = [("What are the hardest problems in a data platform?", "Making several sources agree in gold (keys, grain, history, completeness, late data, corrections) and making one number hold everywhere in the semantic layer (definitions, additivity, versions, provisional numbers). Earlier layers are hard but mechanical."),
          ("Can a framework solve these problems?", f"Most of them, once the business decision is declared. Of the {N} listed here, {c['solve']} are solved by the engine once declared, {c['assist']} are assisted and {c['people_decide']} stay with people.")]
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › Hard problems by layer</p>
<p class="eyebrow" style="margin-top:22px">Data engineering · free guide · {len(LAYERS)} layers and hops · {N} challenges</p>
<h1>Hard problems by layer, and how to solve them</h1>
<p class="lede">Every layer of a data platform, from the source system to the screen, has its own hard problems and its own common mistakes. This guide lists them layer by layer, with a worked example from a synthetic tyre company and how each one is solved and tested.</p>

<section id="picture"><p class="eyebrow">The picture</p><h2>Ten steps from source to screen</h2>
<p>Data moves through <b>layers</b>, places where it rests (bronze keeps what arrived, silver cleans one source, gold combines sources into facts, the semantic layer defines the numbers people use), and <b>hops</b>, the steps that move it from one layer to the next (drawn dashed). Each box shows the first few challenges and how many are solved, assisted or left to people.</p>
{fig(flow_map(), "Read 1 to 5 left to right, then 6 to 10 right to left. The two boxes with a thick border are the hardest steps.")}</section>

<section id="hardest"><p class="eyebrow">Why there</p><h2>The hardest problems sit at silver to gold and gold to semantic</h2>
<p>Before silver, the work is making <b>one</b> source faithful: duplicates, resent files, schema changes, deletes, changes that arrive out of order. That is hard but mechanical, so one engine with the same steps for every source handles it. From silver to gold, <b>several</b> sources meet for the first time, and they have to agree on keys, grain, time and meaning. From gold to semantic, numbers reach people, dashboards, conversational tools and agents, and one definition has to hold everywhere. Those steps need business judgment, not only code.</p>
{fig(two_kinds(), "One source faithful is mechanical. Many sources agreeing needs judgment about meaning and timing.")}</section>

<section id="thesis"><p class="eyebrow">The approach</p><h2>Declare the business decisions; the engine builds them; the tests prove them</h2>
<p>Tools such as dbt or a semantic layer give you a place to write the answer, but they do not know the answer. The answer is a set of business decisions: what one row of a fact means, which history applies, how long to wait for a late file, what a metric counts. Write those decisions down once, as data. The engine then builds the joins, the windows and the metric definitions from them, and the tests check the results against known answers. Of the {N} challenges here, {c['solve']} are solved this way, {c['assist']} are assisted and {c['people_decide']} stay with people.</p>
<h3>Four rules behind most of it</h3>
<div class="tw"><table class="t"><tr><th>Rule</th><th>What it means</th></tr>{rule_rows}</table></div></section>

<section id="pages"><p class="eyebrow">The layers</p><h2>One page per layer and hop</h2><div class="map">{cards}<a href="{BASE}all-challenges/"><span class="n">All</span><b>All {N} challenges</b><span>Filter every challenge by layer, verdict and status.</span></a></div></section>

<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{faq(qa)}</section>
<section id="next"><p class="eyebrow">Related</p><h2>Where it connects</h2>
<p><a href="/learn/medallion-architecture/">Medallion architecture</a> explains the layers themselves; <a href="/learn/shift-left/">Shift left</a> shows the code checks that guard many of these fixes; <a href="/learn/datatwin/">DataTwin, explained</a> shows how the tyre world tests them.</p></section>"""
    crumbs = [("Learn", f"{SITE}/learn/"), ("Hard problems by layer", url)]
    title = "Hard problems by layer, and how to solve them"
    desc = f"The hard problems and anti-patterns of each data platform layer from source to screen ({N} challenges), why silver to gold and gold to semantic are hardest, and how each is solved and tested."
    return wb.page(title, desc, url, body, CSS + HP_CSS + R.ld(title, desc, url, qa, crumbs))


def main():
    out = ROOT / "learn" / "hard-problems"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(hub())
    pages = [(layer_page(L), L["id"], f"{L['order']} of {len(LAYERS)}") for L in LAYERS] + [(all_page(), "all", "all challenges")]
    for (slug, short, title, desc, body, qa, nxt), cur, num in pages:
        d = out / slug
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(render(slug, short, title, desc, body, qa, nxt, cur, num))
    print("hard problems ->", out, f"(hub + {len(pages)} pages, {N} challenges)")


if __name__ == "__main__":
    main()
