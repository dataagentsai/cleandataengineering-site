"""Learning paths: one page per discipline, and one per discipline x platform.

    python3 _paths/build.py      # writes paths/ (hub + 6 disciplines + one page per platform)

A visitor picks "who I am" and "where I work" and lands on one page made for that pair,
for example /paths/data-engineering/aws/. Data lives in _paths/data.py.
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
spec = importlib.util.spec_from_file_location("writing_build", ROOT / "_writing" / "build.py")
wb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wb)
from data import CERTS, CONCEPTS, DISCIPLINES, LEVELS, PLATFORM_NOTE, PLATFORMS, PROJECTS, READ, STATUS  # noqa: E402

E = wb.E
SITE = wb.SITE
OUT = ROOT / "paths"
BY_ID = {d["id"]: d for d in DISCIPLINES}

CSS = """<style>
  .crumbs { font-size:13.5px; color:var(--faint); margin:28px 0 0; } .crumbs a { color:var(--muted); }
  .phero { padding:26px 0 6px; } .phero h1 { margin-bottom:10px; } .phero .who { font-size:19px; color:var(--ink-soft); }
  .switch { display:flex; flex-wrap:wrap; gap:8px; margin:14px 0 0; font-size:14px; align-items:center; }
  .switch .lb { color:var(--faint); margin-right:4px; }
  .switch a, .switch span.on { border:1.5px solid var(--ink); border-radius:var(--wob); padding:3px 13px; text-decoration:none; color:var(--ink); background:#fff; }
  .switch span.on { background:var(--ink); color:#fff; }
  .lvlstrip { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin:24px 0 0; }
  .lvlstrip a { border:var(--line); border-radius:var(--wob); padding:12px 16px; text-decoration:none; color:var(--ink); background:var(--wash); }
  .lvlstrip b { font-family:var(--hand); font-weight:400; font-size:26px; display:block; }
  .lvlstrip span { font-size:13.5px; color:var(--muted); display:block; line-height:1.4; }
  .goal { background:var(--wash); border:var(--line); border-radius:var(--wob); padding:12px 18px; font-size:17px; margin:6px 0 18px; }
  .tw { overflow-x:auto; } table.learn { border-collapse:collapse; width:100%; font-size:15px; margin:4px 0 18px; }
  table.learn th, table.learn td { text-align:left; padding:8px 10px; border-bottom:1.5px dashed var(--rule-firm); vertical-align:top; }
  table.learn th { font-size:11.5px; letter-spacing:.08em; text-transform:uppercase; color:var(--faint); font-weight:700; }
  table.learn td.tool { font-weight:600; color:var(--ink); }
  table.learn td small { display:block; color:var(--faint); font-weight:400; font-size:13px; }
  h3.sub { font-size:24px; margin:22px 0 8px; }
  .projs { display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:12px; margin:6px 0 18px; }
  .proj { border:var(--line); border-radius:var(--wob); padding:14px 18px; background:#fff; display:flex; flex-direction:column; }
  .proj h4 { font-family:var(--hand); font-weight:400; font-size:22px; margin:0 0 4px; }
  .proj p { font-size:14.5px; color:var(--ink-soft); margin:0 0 10px; line-height:1.5; }
  .proj .st { font-size:11.5px; font-weight:700; letter-spacing:.05em; text-transform:uppercase; color:var(--ink); margin-bottom:6px; }
  .proj .st i { font-style:normal; background:var(--butter); border:1.5px solid var(--ink); border-radius:999px; padding:0 8px; }
  .proj .port { font-size:13px; color:var(--muted); margin:0 0 8px; }
  .proj .lk { margin-top:auto; font-size:14px; display:flex; gap:12px; flex-wrap:wrap; }
  ul.ready { list-style:none; padding:0; margin:0 0 8px; } ul.ready li { padding:4px 0 4px 28px; position:relative; }
  ul.ready li::before { content:""; position:absolute; left:2px; top:9px; width:14px; height:14px; border:1.5px solid var(--ink); border-radius:4px; }
  .note { font-size:14px; color:var(--faint); }
  .pgrid { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin:14px 0; }
  .pgrid a { border:var(--line); border-radius:var(--wob); padding:14px 16px; text-decoration:none; color:var(--ink); background:var(--wash); }
  .pgrid b { font-family:var(--hand); font-weight:400; font-size:24px; display:block; } .pgrid span { font-size:13px; color:var(--muted); }
  .matrix td a { white-space:nowrap; }
  @media (max-width:640px) { .lvlstrip { grid-template-columns:1fr; } }
</style>"""


def wash(d):
    return f'style="--wash:var({d["wash"]})"'


def crumbs(*parts):
    bits = ['<a href="/">Home</a>', '<a href="/paths/">Paths</a>'] + [f'<a href="{u}">{E(t)}</a>' if u else E(t) for t, u in parts]
    return '<p class="crumbs">' + " › ".join(bits) + "</p>"


def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>"


def breadcrumb_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(items)]}


def course_ld(name, desc, url, level_names, teaches):
    return {"@context": "https://schema.org", "@type": "Course", "name": name, "description": desc, "url": url,
            "inLanguage": "en", "isAccessibleForFree": True, "educationalLevel": "Beginner to advanced",
            "teaches": teaches,
            "provider": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE},
            "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "online", "courseWorkload": "Self-paced"},
            "syllabusSections": [{"@type": "Syllabus", "name": n} for n in level_names],
            "offers": {"@type": "Offer", "price": 0, "priceCurrency": "USD", "category": "Free"}}


def project_card(pid, plat=None):
    p = PROJECTS[pid]
    st = STATUS[p["status"]]
    port = ""
    if plat and p["on"] and plat not in p["on"]:
        port = f'<p class="port">Built on {", ".join(PLATFORMS[x] for x in p["on"])} today. Porting it to {PLATFORMS[plat]} is a good first contribution.</p>'
    elif plat and p["on"]:
        port = f'<p class="port">Built on {PLATFORMS[plat]} already.</p>'
    links = []
    if p.get("site"):
        links.append(f'<a href="{p["site"]}">Open the project</a>')
    subj = f"Project: {p['title']}" + (f" ({PLATFORMS[plat]})" if plat else "")
    verb = "I want to lead this" if p["status"] in ("proposed", "needs-lead") else "I want to join"
    links.append(f'<a href="mailto:basant@cleandataengineering.ai?subject={E(subj)}">{verb}</a>')
    return (f'<div class="proj"><div class="st"><i>{E(st)}</i></div><h4>{E(p["title"])}</h4>'
            f'<p>{E(p["what"])}</p>{port}<div class="lk">{"".join(links)}</div></div>')


def learn_table(topics, plat):
    rows = []
    for title, what, keys in topics:
        tools = "<br>".join(f'{E(CONCEPTS[k][2][plat])}<small>{E(CONCEPTS[k][0].lower())}</small>' for k in keys)
        rows.append(f"<tr><td><b>{E(title)}</b></td><td>{E(what)}</td><td class='tool'>{tools}</td></tr>")
    return (f'<div class="tw"><table class="learn"><tr><th>Learn</th><th>What it means</th><th>On {E(PLATFORMS[plat])} you use</th></tr>'
            + "".join(rows) + "</table></div>")


def concept_table(topics, plats):
    rows = []
    for title, what, keys in topics:
        cells = "".join("<td>" + "<br>".join(E(CONCEPTS[k][2][p]) for k in keys) + "</td>" for p in plats)
        rows.append(f"<tr><td><b>{E(title)}</b><small>{E(what)}</small></td>{cells}</tr>")
    head = "".join(f"<th>{E(PLATFORMS[p])}</th>" for p in plats)
    return f'<div class="tw"><table class="learn"><tr><th>Learn</th>{head}</tr>' + "".join(rows) + "</table></div>"


def level_strip(d, base=""):
    return '<div class="lvlstrip">' + "".join(
        f'<a href="{base}#{k}"><b>{LEVELS[k][0]}</b><span>{LEVELS[k][1]} · {d["levels"][k]["weeks"]}</span><span>{E(d["levels"][k]["goal"])}</span></a>'
        for k in ("crawl", "walk", "run")) + "</div>"


def reading(d):
    return " · ".join(f'<a href="{READ[r][1]}">{E(READ[r][0])}</a>' for r in d["read"])


def platform_switch(d, cur):
    out = ['<div class="switch"><span class="lb">Platform:</span>']
    for p in d["platforms"]:
        out.append(f'<span class="on">{PLATFORMS[p]}</span>' if p == cur else f'<a href="/paths/{d["id"]}/{p}/">{PLATFORMS[p]}</a>')
    out.append(f'<a href="/paths/{d["id"]}/">Compare all</a></div>')
    return "".join(out)


def role_switch(cur, plat=None):
    out = ['<div class="switch"><span class="lb">Role:</span>']
    for d in DISCIPLINES:
        if d["id"] == cur:
            out.append(f'<span class="on">{d["short"]}</span>')
        else:
            tgt = f"/paths/{d['id']}/{plat}/" if plat and plat in d["platforms"] else f"/paths/{d['id']}/"
            out.append(f'<a href="{tgt}">{d["short"]}</a>')
    return "".join(out) + "</div>"


def certs_box(d, plat):
    cs = CERTS.get(d["id"], {}).get(plat, [])
    if not cs:
        return ""
    items = "".join(f"<li>{E(c)}</li>" for c in cs)
    return (f'<section id="certs"><p class="eyebrow">Optional</p><h2>Certifications on {PLATFORMS[plat]}</h2>'
            f'<p>Projects prove more than certificates, but a certificate can open a door. These fit this path. Exam names and codes change, so check the current one before you book.</p>'
            f'<ul>{items}</ul><p class="note">Free prep we have written: <a href="/certifications/">Certifications</a>.</p></section>')


def platform_page(d, plat):
    name = f'{d["name"]} on {PLATFORMS[plat]}'
    desc = f'A free {d["name"].lower()} learning path on {PLATFORM_NOTE[plat]}: crawl, walk and run, with the {PLATFORMS[plat]} services to learn and GitHub projects to build at each level.'
    url = f"{SITE}/paths/{d['id']}/{plat}/"
    body = [crumbs((d["name"], f"/paths/{d['id']}/"), (PLATFORMS[plat], None)),
            f'<div class="phero" {wash(d)}><p class="eyebrow">Learning path · {PLATFORMS[plat]}</p><h1>{E(name)}</h1>',
            f'<p class="who">{E(d["who"])}</p><p class="note" style="margin:0">Free, like everything here: no sign-up, no paywall. Only the cloud you practise on may charge; the open-source path costs nothing.</p>{platform_switch(d, plat)}{role_switch(d["id"], plat)}{level_strip(d)}</div>',
            f'<section><p>{E(d["why"])}</p><p class="note">Every topic below is a <b>concept</b> (the job) with the <b>{PLATFORMS[plat]} product</b> that does it. '
            f'Learn the concept once; on another platform only the product name changes. Read alongside: {reading(d)}.</p></section>']
    teaches = []
    for k in ("crawl", "walk", "run"):
        lv = d["levels"][k]
        teaches += [t[0] for t in lv["topics"]]
        body.append(f'<section id="{k}" {wash(d)}><p class="eyebrow">{LEVELS[k][1]} · {lv["weeks"]}</p>'
                    f'<h2>{LEVELS[k][0]}: {E(LEVELS[k][2])}</h2><p class="goal">{E(lv["goal"])}</p>'
                    f'<h3 class="sub">Learn</h3>{learn_table(lv["topics"], plat)}'
                    f'<h3 class="sub">Build on GitHub</h3><div class="projs">{"".join(project_card(p, plat) for p in lv["projects"])}</div>'
                    f'<h3 class="sub">You are ready to move on when</h3><ul class="ready">{"".join(f"<li>{E(r)}</li>" for r in lv["ready"])}</ul></section>')
    body.append(certs_box(d, plat))
    body.append('<section><p class="eyebrow">Learn together</p><h2>Do it with others</h2>'
                '<p>Every project above has a page, a list of open work and a "good first issue" label on GitHub. Pick one at your level, say hello by email, and build it in the open. '
                'If a project says <i>needs a lead</i>, that can be you.</p>'
                f'<p><a href="/projects/">All projects →</a> &nbsp; <a href="/paths/">Another path →</a></p></section>')
    ld = jsonld(course_ld(name, desc, url, [f"{LEVELS[k][0]} ({LEVELS[k][1]})" for k in LEVELS], teaches)) + \
        jsonld(breadcrumb_ld([("Paths", "/paths/"), (d["name"], f"/paths/{d['id']}/"), (PLATFORMS[plat], f"/paths/{d['id']}/{plat}/")]))
    return wb.page(name + " · learning path", desc, url, "\n".join(body), CSS + ld)


def discipline_page(d):
    desc = f'A free {d["name"].lower()} learning path in three levels (crawl, walk, run) on {", ".join(PLATFORMS[p] for p in d["platforms"])}, with GitHub projects to build at each level.'
    url = f"{SITE}/paths/{d['id']}/"
    pg = "".join(f'<a href="/paths/{d["id"]}/{p}/" {wash(d)}><b>{PLATFORMS[p]}</b><span>{E(PLATFORM_NOTE[p])}</span></a>' for p in d["platforms"])
    body = [crumbs((d["name"], None)),
            f'<div class="phero" {wash(d)}><p class="eyebrow">Learning path</p><h1>{E(d["name"])}</h1><p class="who">{E(d["who"])}</p>{role_switch(d["id"])}</div>',
            f'<section id="platform"><p class="eyebrow">Step 1</p><h2>Where do you work?</h2><p>Pick your platform and you get one page with that platform\'s products in every step.</p><div class="pgrid">{pg}</div></section>',
            f'<section {wash(d)}><p class="eyebrow">Why this path</p><p>{E(d["why"])}</p>{level_strip(d)}<p class="note" style="margin-top:12px">Read alongside: {reading(d)}.</p></section>']
    for k in ("crawl", "walk", "run"):
        lv = d["levels"][k]
        links = " · ".join(f'<a href="/paths/{d["id"]}/{p}/#{k}">{PLATFORMS[p]}</a>' for p in d["platforms"])
        body.append(f'<section id="{k}" {wash(d)}><p class="eyebrow">{LEVELS[k][1]} · {lv["weeks"]}</p><h2>{LEVELS[k][0]}: {E(LEVELS[k][2])}</h2>'
                    f'<p class="goal">{E(lv["goal"])}</p><p class="note">Open this level on: {links}</p>'
                    f'<h3 class="sub">Learn: the concept, and the product on each platform</h3>{concept_table(lv["topics"], d["platforms"])}'
                    f'<h3 class="sub">Build on GitHub</h3><div class="projs">{"".join(project_card(p) for p in lv["projects"])}</div>'
                    f'<h3 class="sub">You are ready to move on when</h3><ul class="ready">{"".join(f"<li>{E(r)}</li>" for r in lv["ready"])}</ul></section>')
    ld = jsonld(course_ld(d["name"] + " learning path", desc, url, [f"{LEVELS[k][0]} ({LEVELS[k][1]})" for k in LEVELS],
                          [t[0] for k in LEVELS for t in d["levels"][k]["topics"]])) + \
        jsonld(breadcrumb_ld([("Paths", "/paths/"), (d["name"], f"/paths/{d['id']}/")]))
    return wb.page(d["name"] + " learning path: crawl, walk, run", desc, url, "\n".join(body), CSS + ld)


def picker(compact=False):
    roles = "".join(f'<option value="{d["id"]}">{E(d["name"])}</option>' for d in DISCIPLINES)
    plats = "".join(f'<option value="{k}">{E(v)}</option>' for k, v in PLATFORMS.items())
    supported = json.dumps({d["id"]: d["platforms"] for d in DISCIPLINES})
    return f"""<form class="picker" onsubmit="return goPath(this)">
  <label>I am learning <select name="r" aria-label="Role">{roles}</select></label>
  <label>on <select name="p" aria-label="Platform">{plats}</select></label>
  <button type="submit">Show my path →</button>
</form>
<script>
function goPath(f){{var s={supported};var r=f.r.value,p=f.p.value;location.href='/paths/'+r+'/'+(s[r].indexOf(p)>=0?p+'/':'');return false;}}
</script>"""


def hub_page():
    desc = "Free learning paths for data, AI, LLM, ML, software and forward-deployed engineers on AWS, Azure, Google Cloud, Databricks and open source: crawl, walk, run, with GitHub projects at every level."
    head = "".join(f"<th>{E(v)}</th>" for v in PLATFORMS.values())
    rows = "".join(
        f'<tr><td><a href="/paths/{d["id"]}/"><b>{E(d["name"])}</b></a></td>'
        + "".join(f'<td><a href="/paths/{d["id"]}/{p}/">{PLATFORMS[p]}</a></td>' if p in d["platforms"] else "<td>–</td>" for p in PLATFORMS)
        + "</tr>" for d in DISCIPLINES)
    cards = "".join(
        f'<a href="/paths/{d["id"]}/" {wash(d)}><b>{E(d["name"])}</b><span>{E(d["who"])}</span></a>' for d in DISCIPLINES)
    body = f"""{crumbs()}
<div class="phero" style="--wash:var(--peri-wash)"><p class="eyebrow">Learning paths</p><h1>Pick your path</h1>
<p class="who">Free, like everything here. Six roles, five platforms, three levels. Choose who you are and where you work, and you get one page with what to learn and what to build.</p>
{picker()}</div>
<section><p class="eyebrow">Or browse</p><h2>Six roles</h2><div class="pgrid">{cards}</div></section>
<section><p class="eyebrow">Every page, at a glance</p><h2>Role × platform</h2><div class="tw"><table class="learn matrix"><tr><th>Role</th>{head}</tr>{rows}</table></div></section>
<section><p class="eyebrow">How the levels work</p><h2>Crawl, walk, run</h2>
<ul class="ready">{"".join(f"<li><b>{v[0]}</b> ({v[1]}): {E(v[2])}</li>" for v in LEVELS.values())}</ul>
<p>Each level has topics to learn, GitHub projects to build, and a short checklist that tells you when you are ready to move on. Not sure where to start? <a href="/mindset/">Read the dragon story</a>, then <a href="/learn/ai-universe/">draw the map</a>.</p></section>"""
    ld = jsonld({"@context": "https://schema.org", "@type": "ItemList", "name": "Learning paths",
                 "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}/paths/{d['id']}/", "name": d["name"]} for i, d in enumerate(DISCIPLINES)]})
    return wb.page("Learning paths: data, AI, LLM, ML, software and FDE", desc, f"{SITE}/paths/", body, CSS + ld)


def home_roles():
    out = ['<div class="roles">']
    for d in DISCIPLINES:
        lv = "".join(f'<a href="/paths/{d["id"]}/#{k}">{LEVELS[k][0]}</a>' for k in ("crawl", "walk", "run"))
        pl = " · ".join(f'<a href="/paths/{d["id"]}/{p}/">{PLATFORMS[p]}</a>' for p in d["platforms"])
        out.append(f'<div class="role" {wash(d)}><h3><a href="/paths/{d["id"]}/">{E(d["name"])}</a></h3><p>{E(d["who"])}</p>'
                   f'<div class="lv">{lv}</div><div class="pl">{pl}</div></div>')
    return "".join(out) + "</div>"


def put(s, name, html_):
    a, b = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    return s[: s.index(a) + len(a)] + html_ + s[s.index(b):]


def main():
    home = ROOT / "index.html"
    s = put(put(home.read_text(), "picker", picker()), "paths", home_roles())
    home.write_text(s)
    OUT.mkdir(exist_ok=True)
    (OUT / "index.html").write_text(hub_page())
    n = 1
    for d in DISCIPLINES:
        (OUT / d["id"]).mkdir(exist_ok=True)
        (OUT / d["id"] / "index.html").write_text(discipline_page(d))
        n += 1
        for p in d["platforms"]:
            (OUT / d["id"] / p).mkdir(exist_ok=True)
            (OUT / d["id"] / p / "index.html").write_text(platform_page(d, p))
            n += 1
    for d in DISCIPLINES:  # every concept used must have every platform the discipline supports
        for k in LEVELS:
            for _, _, keys in d["levels"][k]["topics"]:
                for key in keys:
                    missing = [p for p in d["platforms"] if p not in CONCEPTS[key][2]]
                    assert not missing, (d["id"], key, missing)
            for pid in d["levels"][k]["projects"]:
                assert pid in PROJECTS, pid
    print(f"{n} pages -> {OUT}")


if __name__ == "__main__":
    main()
