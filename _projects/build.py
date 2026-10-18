"""Build /projects/ from the data files in _projects/ (data_a.py, data_b.py, data_c.py).

    python3 _projects/build.py

Each project becomes /projects/<id>/ with the same ten sections, so a group can start from the page alone:
purpose, business benefits, status and how to join, requirements, a very high-level architecture (no tool
names), the tech stack as bindings per platform, what needs to be done, roles, what you learn, links.
"""
import html
import importlib.util
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
E = html.escape
sys.path.insert(0, str(HERE))

spec = importlib.util.spec_from_file_location("writing_build", ROOT / "_writing" / "build.py")
wb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wb)
kit = wb.kit

PROJECTS = []
for name in ("data_a", "data_b", "data_c"):
    try:
        PROJECTS += __import__(name).PROJECTS
    except ImportError:
        pass

GROUPS = {"standards": "Open standards & builds", "learning": "Learning builds", "open": "Open to lead"}
STATUS = {"active": "Active · join me", "starting": "Starting · join early", "not-started": "Not started · lead it"}
SUBJECTS = wb.SUBJECTS
# Practice label (forward-deployed engineering): projects you could take into a real customer setting.
FDE_READY = {"claims-fnol-azure", "reference-agent", "eval-harness-framework", "data-eng-specs", "dataeng-training", "asksherlock"}
EMAIL = "basant@cleandataengineering.ai"

CSS = """<style>
  .cards { display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:16px; margin-top:18px; }
  .card { background:#fff; border:1.5px solid var(--ink); border-radius:var(--wob); padding:16px 20px; font-family:var(--sans); display:flex; flex-direction:column; text-decoration:none; color:inherit; transition:transform .15s; }
  .card:hover { transform:rotate(-.4deg) translateY(-2px); }
  .card[data-subject=ai] { background:var(--peri-wash); } .card[data-subject=llm] { background:var(--mint-wash); }
  .card[data-subject=data] { background:var(--rose-wash); } .card[data-subject=cost] { background:var(--butter-wash); }
  .card h3 { font-family:var(--hand); font-weight:400; font-size:24px; margin:0 0 4px; color:var(--ink); } .card p { font-size:14px; color:var(--muted); margin:0 0 10px; line-height:1.5; }
  .pills { display:flex; gap:6px; flex-wrap:wrap; margin-top:auto; }
  .pill { font:12px var(--sans); padding:1px 9px; border-radius:999px; border:1.5px solid var(--ink); color:var(--ink); background:#fff; }
  .pill.st-active { background:var(--accent); color:var(--paper); border-color:var(--accent); }
  .pill.st-starting { border-color:var(--accent); color:var(--accent); }
  .bar { height:9px; background:#fff; border:1.5px solid var(--ink); border-radius:999px; margin:8px 0 10px; overflow:hidden; } .bar i { display:block; height:100%; background:var(--butter); }
  .proj h2 { margin-top:38px; } .proj ul { padding-left:22px; } .proj li { margin:5px 0; }
  .benefits { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; font-family:var(--sans); }
  .benefits div { background:var(--mint-wash); border:1.5px solid var(--ink); border-radius:var(--wob); padding:12px 16px; } .benefits b { display:block; font-family:var(--hand); font-weight:400; font-size:21px; margin-bottom:2px; } .benefits span { font-size:14.5px; color:var(--ink-soft); }
  .join { background:var(--butter-wash); border:1.5px solid var(--ink); border-radius:var(--wob); padding:18px 22px; font-family:var(--sans); font-size:15px; }
  .join .btns { display:flex; gap:12px; flex-wrap:wrap; margin-top:10px; }
  .join .btns a { background:var(--peri); color:var(--ink); border:1.5px solid var(--ink); padding:7px 16px; border-radius:999px; text-decoration:none; font-weight:700; }
  .join .btns a.alt { background:#fff; color:var(--ink); }
  .tw { overflow-x:auto; } .proj table { border-collapse:collapse; width:100%; font-family:var(--sans); font-size:14px; margin:6px 0 16px; }
  .proj th, .proj td { text-align:left; padding:7px 10px; border-bottom:1px solid var(--rule); vertical-align:top; }
  .proj th { font-size:11.5px; letter-spacing:.08em; text-transform:uppercase; color:var(--faint); }
  .built { font-weight:650; color:var(--ink); } .st { font:11.5px var(--mono); padding:1px 6px; border-radius:3px; border:1px solid var(--rule-firm); }
  .st.done { background:var(--accent); color:var(--paper); border-color:var(--accent); } .st.doing { color:var(--accent); border-color:var(--accent); }
  .ms { font-family:var(--sans); font-size:15px; margin:18px 0 4px; } .ms span { color:var(--faint); font-size:13px; }
  .meta { font-family:var(--sans); font-size:13.5px; color:var(--faint); }
</style>"""


def progress(p):
    tasks = [t for _, ts in p.get("work", []) for t in ts]
    done = sum(1 for t in tasks if t[1] == "done")
    return done, len(tasks)


def pills(p):
    out = f'<span class="pill st-{p["status"]}">{E(STATUS[p["status"]])}</span><span class="pill">{E(SUBJECTS.get(p["subject"], p["subject"]))}</span>'
    if p["id"] in FDE_READY:
        out += '<span class="pill">Forward-deployed ready</span>'
    return out


def arch(p):
    """The very high-level architecture: components in flow order, no tool names."""
    if kit is None or not p.get("components"):
        return ""
    comps = p["components"]
    per, w, h, gx, gy = 4, 220, 84, 30, 50
    labels = {(a, b): l for a, b, l in p.get("flows", [])}
    d, pos = "", {}
    for i, (name, resp) in enumerate(comps):
        r, c = divmod(i, per)
        c = c if r % 2 == 0 else per - 1 - c          # snake, so the flow reads continuously
        x, y = 10 + c * (w + gx), 10 + r * (h + gy)
        pos[name] = (x, y)
        words, lines, cur = resp.split(), [], ""
        for wd in words:
            if len(cur) + len(wd) > 30:
                lines.append(cur)
                cur = wd
            else:
                cur = (cur + " " + wd).strip()
        lines.append(cur)
        d += kit.box(x, y, w, h, name if len(name) < 26 else name[:25] + "…", lines[:2], "solid" if i == 0 else "bx")
    for (a, _), (b, _) in zip(comps, comps[1:]):
        (x1, y1), (x2, y2) = pos[a], pos[b]
        if y1 == y2:
            xa, xb = (x1 + w, x2) if x2 > x1 else (x1, x2 + w)
            d += kit.arrow(xa + 2, y1 + h / 2, xb - 2, y2 + h / 2)
            if labels.get((a, b)):
                d += kit.text((xa + xb) / 2, y1 + h / 2 - 8, labels[(a, b)][:14], "sm lb", "middle")
        else:
            d += kit.arrow(x1 + w / 2, y1 + h + 2, x2 + w / 2, y2 - 2, labels.get((a, b), "")[:18] or None, lx=x1 + w / 2 + 8, anchor="start")
    rows = (len(comps) + per - 1) // per
    others = [f"{E(a)} → {E(b)}: {E(l)}" for a, b, l in p.get("flows", [])
              if not any(a == x and b == y for (x, _), (y, _) in zip(comps, comps[1:]))]
    extra = f'<p class="meta">Also: {" · ".join(others)}</p>' if others else ""
    return wb.figure(1000, 10 + rows * (h + gy) - gy + 20, d, "The components of " + p["title"] + " in flow order.",
                     "Components and what each is responsible for, with no tool names: the tools come in the next section.") + extra


def bindings(p):
    b = p.get("bindings") or {}
    if not b:
        return ""
    plats = list(b)
    names = [c for c, _ in p.get("components", [])]
    for plat in plats:
        for c in b[plat]:
            if c not in names:
                names.append(c)
    head = "<tr><th>Component</th>" + "".join(f"<th>{E(x)}</th>" for x in plats) + "</tr>"
    rows = ""
    for c in names:
        cells = ""
        for plat in plats:
            v = b[plat].get(c, "—")
            built = v.endswith("✓")
            cells += f'<td class="{"built" if built else ""}">{E(v)}</td>'
        if any(b[plat].get(c) for plat in plats):
            rows += f"<tr><td>{E(c)}</td>{cells}</tr>"
    return f'<div class="tw"><table>{head}{rows}</table></div><p class="meta">Bold with ✓ = built and running today. Everything else is the planned or possible binding: the components stay the same, only the tools change.</p>'


def work(p):
    out = ""
    for ms, tasks in p.get("work", []):
        done = sum(1 for t in tasks if t[1] == "done")
        out += f'<p class="ms"><strong>{E(ms)}</strong> <span>{done} of {len(tasks)} done</span></p>'
        out += '<div class="tw"><table><tr><th>Task</th><th>Status</th><th>Size</th><th>Skill</th></tr>'
        for task, st, size, skill in tasks:
            out += f'<tr><td>{E(task)}</td><td><span class="st {st}">{st}</span></td><td>{E(size)}</td><td>{E(skill)}</td></tr>'
        out += "</table></div>"
    return out + '<p class="meta">Size: S = an evening or two, M = about a week part-time, L = a few weeks.</p>'


def join_box(p):
    subj = quote(f"Join: {p['title']}")
    body = quote("Hi Basant,\n\nI'd like to join this project.\nSkills:\nHours a week:\nWhat I'd like to pick up:\n")
    btns = f'<a href="mailto:{EMAIL}?subject={subj}&body={body}">Join this project</a>'
    if p.get("repo") and p.get("repo_public"):
        btns += f'<a class="alt" href="{p["repo"]}/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22">Good first tasks on GitHub</a>'
        btns += f'<a class="alt" href="{p["repo"]}">The repository</a>'
    lead = p.get("lead", "")
    if p["status"] == "not-started":
        msg = "Nobody has started this yet. Lead it, or join the first group." if "Open" in lead else "Not started yet: join the first group and shape it from day one."
    elif p["status"] == "starting":
        msg = "Early days: the shape is still being decided, so joiners now have the most say."
    else:
        msg = "Under way: pick a task below, or tell me what you'd like to learn and I'll suggest one."
    first = "".join(f"<li>{E(g)}</li>" for g in p.get("good_first", []))
    first = f"<p style=\"margin:12px 0 4px\"><strong>Good first tasks this week:</strong></p><ul>{first}</ul>" if first else ""
    repo_note = "" if p.get("repo_public") else '<p class="meta" style="margin-top:8px">The code is not public yet; joiners get access.</p>'
    return f'<div class="join"><strong>{E(STATUS[p["status"]])}.</strong> {msg} <span class="meta">Lead: {E(lead)}.</span>{first}<div class="btns">{btns}</div>{repo_note}</div>'


def project_page(p):
    done, total = progress(p)
    benefits = "".join(f"<div><b>{E(t)}</b><span>{E(s)}</span></div>" for t, s in p.get("benefits", []))
    lst = lambda xs: "<ul>" + "".join(f"<li>{E(x)}</li>" for x in xs) + "</ul>"
    roles = "".join(f"<tr><td>{E(r)}</td><td>{E(str(n))}</td><td>{E(hw)}</td><td>{E(what)}</td></tr>" for r, n, hw, what in p.get("roles", []))
    links = "".join(f'<li><a href="{u}">{E(l)}</a></li>' for l, u in p.get("links", []))
    started = f" · started {E(p['started'])}" if p.get("started") else ""
    body = f"""<article class="proj">
<div class="hero" style="padding-top:48px">
  <p class="post-meta"><a href="/projects/">Projects</a> · {E(GROUPS.get(p['group'], ''))}{started}</p>
  <h1>{E(p['title'])}</h1>
  <p class="thesis">{E(p['one_liner'])}</p>
  <div class="pills">{pills(p)}</div>
  {f'<div class="bar" title="{done} of {total} tasks done"><i style="width:{100 * done / total if total else 0:.0f}%"></i></div><p class="meta">{done} of {total} tasks done</p>' if total else ''}
</div>
<h2>1 · Purpose</h2><p>{E(p['purpose'])}</p><p class="meta">For: {E(p.get('audience', ''))}</p>
<h2>2 · Business benefits</h2><div class="benefits">{benefits}</div>
<h2>3 · Status and how to join</h2>{join_box(p)}
<h2>4 · Requirements</h2><p><strong>What it must do</strong></p>{lst(p.get('functional', []))}<p><strong>How well it must do it</strong></p>{lst(p.get('nonfunctional', []))}
<h2>5 · Architecture, very high level</h2>{arch(p)}
<h2>6 · Tech stack, per platform</h2>{bindings(p)}
<h2>7 · What needs to be done</h2>{work(p)}
<h2>8 · Roles</h2><div class="tw"><table><tr><th>Role</th><th>How many</th><th>Hours / week</th><th>What they do</th></tr>{roles}</table></div>
<h2>9 · What you'll learn</h2>{lst(p.get('learn', []))}<p><strong>Level-up questions</strong></p>{lst(p.get('questions', []))}
<h2>10 · Links</h2><ul>{links or '<li>Links come once the work is public.</li>'}</ul>
</article>"""
    return wb.page(p["title"], p["one_liner"], f"{wb.SITE}/projects/{p['id']}/", body, wb.kit_css() + CSS)


def list_page():
    def chips(name, opts):
        return f'<div class="chips" data-f="{name}"><button class="on" data-v="">All</button>' + "".join(
            f'<button data-v="{k}">{E(v)}</button>' for k, v in opts.items()) + "</div>"
    order = {"active": 0, "starting": 1, "not-started": 2}
    cards = ""
    for p in sorted(PROJECTS, key=lambda p: (order[p["status"]], p["group"], p["title"])):
        done, total = progress(p)
        bar = f'<div class="bar"><i style="width:{100 * done / total if total else 0:.0f}%"></i></div>' if total else ""
        benefit = p["benefits"][0][1] if p.get("benefits") else ""
        cards += (f'<a class="card" href="/projects/{p["id"]}/" data-subject="{p["subject"]}" data-status="{p["status"]}" '
                  f'data-group="{p["group"]}" data-practice="{"fde" if p["id"] in FDE_READY else ""}">'
                  f'<h3>{E(p["title"])}</h3><p>{E(p["one_liner"])}</p><p><em>{E(benefit)}</em></p>{bar}<div class="pills">{pills(p)}</div></a>')
    body = f"""<div class="hero"><h1>Projects</h1>
<p class="thesis">Real things to build, each with a page that says why it matters, what it looks like, what it's built with on each cloud, and exactly what needs doing next. Some are under way and you can join; some haven't started and need a lead.</p>
<p style="font-family:var(--sans);font-size:14px">To join: open a project and use <strong>Join this project</strong>, or pick a good first task from its repository.</p></div>
{chips("status", {k: v.split(" · ")[0] for k, v in STATUS.items()})}{chips("subject", SUBJECTS)}{chips("group", GROUPS)}{chips("practice", {"fde": "Forward-deployed ready"})}
<div class="cards">{cards}</div>
<script>
(function(){{var f={{}};document.querySelectorAll('.chips').forEach(function(c){{c.addEventListener('click',function(e){{
var b=e.target.closest('button');if(!b)return;c.querySelectorAll('button').forEach(function(x){{x.classList.toggle('on',x===b)}});
f[c.dataset.f]=b.dataset.v;document.querySelectorAll('.card').forEach(function(el){{
var ok=Object.keys(f).every(function(k){{return!f[k]||el.dataset[k]===f[k]}});el.style.display=ok?'':'none'}})}})}})}})();
</script>"""
    return wb.page("Projects", "Real projects to build or join: purpose, benefits, architecture, tech stack per cloud, and what needs doing.",
                   f"{wb.SITE}/projects/", body, CSS)


def main():
    out = ROOT / "projects"
    out.mkdir(exist_ok=True)
    for p in PROJECTS:
        (out / p["id"]).mkdir(exist_ok=True)
        (out / p["id"] / "index.html").write_text(project_page(p))
    (out / "index.html").write_text(list_page())
    print(f"{len(PROJECTS)} projects -> {out}")


if __name__ == "__main__":
    main()
