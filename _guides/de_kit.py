"""The data project starter kit: templates and skills as files, a zip to download, and the page that shows them.

    python3 _guides/de_kit.py     (then python3 _guides/de_programme.py, python3 _site/nav.py, python3 _site/seo.py)

Writes:
  _kit/data-project-starter-kit/            the kit as plain files (source of the zip; not served, folder starts with _)
  assets/data-project-starter-kit.zip       the download
  /how-we-work/data-essentials/starter-kit/ the page: every template and skill, readable in the browser
Content is in de_kit_data.py.
"""
import shutil
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import de_essentials as DE  # noqa: E402
import de_kit_data as K  # noqa: E402

E, table, L, Lx, C = DE.E, DE.table, DE.L, DE.Lx, DE.C
BASE = DE.BASE
ROOT = DE.ROOT
NAME = "data-project-starter-kit"
KIT = ROOT / "_kit" / NAME
ZIP = f"/assets/{NAME}.zip"

CSS = """<style>
  .tf details.file { border:var(--line); border-radius:var(--wob); padding:6px 14px; margin:8px 0; background:#fff; }
  .tf details.file summary { cursor:pointer; } .tf details.file summary b { font-size:16.5px; } .tf details.file summary span { color:var(--muted); font-size:14px; }
  .tf details.file pre { white-space:pre-wrap; word-break:break-word; font-size:13.5px; line-height:1.5; border-top:1.5px dashed var(--ink); margin:8px 0 4px; padding-top:8px; }
  .tf a.dl { display:inline-block; border:var(--line); border-radius:var(--wob); padding:6px 16px; background:var(--butter-wash); text-decoration:none; font-weight:700; }
  .tf .path { font-size:13px; color:var(--muted); }
</style>"""


def skill_md(s):
    slug, name, who, desc, give, steps, out, tmpl, checks, _sess = s
    extra = "".join(f"- `{f}` in this folder.\n" for f, _ in K.EXTRA.get(slug, []))
    t = f"- The template `templates/{tmpl}`.\n" if tmpl else ""
    return (f'---\nname: {slug}\ndescription: "{desc}"\n---\n\n# {name}\n\nFor: {who}\n\n{desc}\n\n'
            "## You give it\n" + "".join(f"- {x}\n" for x in give) +
            ("\n## It also reads\n" + t + extra if (t or extra) else "") +
            "\n## Steps\n" + "".join(f"{i}. {x}\n" for i, x in enumerate(steps, 1)) +
            f"\n## You get\n{out}\n"
            "\n## Check before you hand it over\n" + "".join(f"- [ ] {x}\n" for x in checks) +
            "\n" + K.RULES)


def template_md(t):
    _f, title, folder, owner, body = t
    return f"# {title}\n\n{K.HEAD}\nCopy to: `{folder}/`  ·  Owner: {owner}\n{body}"


def readme():
    tl = "".join(f"| `templates/{f}` | {title} | `{folder}/` | {owner} |\n" for f, title, folder, owner, _ in K.TEMPLATES)
    sl = "".join(f"| `skills/{s[0]}/` | {s[1]} | {s[2]} |\n" for s in K.SKILLS)
    fl = "".join(f"| `{f}/` | {what} |\n" for f, what in K.FOLDERS)
    return f"""# Data project starter kit

Templates and skills for the non-technical roles on a data project: business analyst, project manager, PMO, delivery manager, product owner, tester.
From cleandataengineering.ai/how-we-work/data-essentials/programme/. Free to use and change.

No code. Every file is plain text, so it can be kept in git, reviewed, and read by a person or by an AI assistant.

## How to start a project from this kit
1. Copy this folder and rename it to your project's name.
2. Put it in git (your team's repository tool). From now on, every change has an author, a reason and a reviewer.
3. Fill `templates/project-one-pager.md` and save it as `00-project/one-pager.md`.
4. For each template you need, copy it from `templates/` to the folder named at its top, and fill it there. Keep `templates/` blank.
5. Work through the stages: {K.STAGES}.

## Folders
| Folder | What goes in it |
|---|---|
{fl}| `templates/` | The blank templates. Do not fill them here. |
| `skills/` | The skills an AI assistant can follow. |

## Templates
| File | Template | Copy to | Owner |
|---|---|---|---|
{tl}| `templates/agile-backlog.csv` | The same backlog as a sheet | `03-backlog/` | PM |

## Skills
A skill is a short written instruction, a template and a checklist that an AI assistant follows the same way every time.

| Folder | Skill | For |
|---|---|---|
{sl}
### How to use a skill
- With an AI assistant that supports skills (for example Claude): add the skill's folder as a skill. In Claude Code, copy `skills/` to `.claude/skills/` in the project. Then ask in plain words, for example "estimate this project" or "review this project for the discovery gate".
- With any other AI assistant: open the skill's `SKILL.md`, paste it as your first message, then give it the files it asks for.
- Without AI: the steps and the checklist in each `SKILL.md` work as a checklist for a person.

### Rules
The result of a skill is a draft. A named person checks it and owns it.
Client data, personal data and secrets stay out of any tool the client has not approved.

## Improving the kit
When a project finds a better question, check or step, propose the change here, as a change for review. That is how the kit learns.
"""


def build_files():
    if KIT.exists():
        shutil.rmtree(KIT)
    files = {"README.md": readme()}
    for f, what in K.FOLDERS:
        files[f"{f}/README.md"] = f"# {f}\n\n{what}\n\nCopy the templates you need from `templates/` into this folder and fill them here.\n"
    for t in K.TEMPLATES:
        files[f"templates/{t[0]}"] = template_md(t)
    files["templates/agile-backlog.csv"] = K.BACKLOG_CSV
    for s in K.SKILLS:
        files[f"skills/{s[0]}/SKILL.md"] = skill_md(s)
        for f, body in K.EXTRA.get(s[0], []):
            files[f"skills/{s[0]}/{f}"] = body
    for rel, text in files.items():
        p = KIT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")
    z = ROOT / ZIP.strip("/")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in sorted(files):
            zi = zipfile.ZipInfo(f"{NAME}/{rel}", date_time=(2026, 11, 23, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            zf.writestr(zi, files[rel].encode("utf-8"))
    print("wrote", len(files), "files to", KIT, "and", z)
    return files


def show(anchor, title, sub, path, text):
    return (f'<details class="file" id="{anchor}"><summary><b>{E(title)}</b> <span>· {E(sub)}</span></summary>'
            f'<p class="path"><code>{E(path)}</code></p><pre>{E(text)}</pre></details>')


def kit_page(files):
    url_path = f"{BASE}starter-kit/"
    nt, ns = len(K.TEMPLATES), len(K.SKILLS)
    trow = [[f'<a href="#t-{f[:-3]}"><b>{E(title)}</b></a>', f"<code>{E(folder)}</code>", E(owner)] for f, title, folder, owner, _ in K.TEMPLATES]
    ttab = table(["Template", "Folder", "Owner"], trow)
    srow = [[f'<a href="#sk-{s[0]}"><b>{E(s[1])}</b></a>', E(s[2]), E(s[3])] for s in K.SKILLS]
    stab = table(["Skill", "For", "What it does, and when to use it"], srow)
    tshow = "".join(show(f"t-{f[:-3]}", title, f"{folder} · owner: {owner}", f"templates/{f}", files[f"templates/{f}"]) for f, title, folder, owner, _ in K.TEMPLATES)
    tshow += show("t-agile-backlog-csv", "Agile backlog, as a sheet", "03-backlog · owner: PM", "templates/agile-backlog.csv", K.BACKLOG_CSV)
    sshow = ""
    for s in K.SKILLS:
        sshow += show(f"sk-{s[0]}", s[1], s[2], f"skills/{s[0]}/SKILL.md", files[f"skills/{s[0]}/SKILL.md"])
        for f, body in K.EXTRA.get(s[0], []):
            sshow += show(f"sk-{s[0]}-{f[:-3]}", f"{s[1]}: {f}", "read by the skill", f"skills/{s[0]}/{f}", body)
    tree = "\n".join([f"{NAME}/", "  README.md"] + [f"  {f}/".ljust(18) + what for f, what in K.FOLDERS] + ["  templates/".ljust(18) + f"{nt} blank templates and the backlog sheet", "  skills/".ljust(18) + f"{ns} skills, one folder each"])
    steps = ["Download the kit and unzip it.", "Rename the folder to your project's name and put it in git.", "Fill the project one-pager first.",
             "Copy each template you need from templates/ into the folder named at its top, and fill it there.", "Add the skills to your AI assistant, or paste a skill's SKILL.md as your first message."]
    qa = [("Do I need an AI assistant to use this?", "No. The templates are plain files. Each skill is also a checklist a person can follow."),
          ("Which AI assistant do the skills work with?", "Any. They are plain instructions. Assistants that support skills, for example Claude, can load each folder as a skill. With others, paste the SKILL.md as your first message."),
          ("Can I put client data into an AI tool?", "Only into a tool the client has approved. The skills say so, and a named person checks every result."),
          ("Where do the numbers in the estimator come from?", "From the worked example on the estimation page. They are starting values. Replace them with your own actuals."),
          ("Can I change the kit?", "Yes. It is free to use and change. Propose improvements as a change for review, so every project gets them.")]
    toc = "".join(f'<li><a href="#{a}">{b}</a></li>' for a, b in [("get", "Get the kit"), ("templates", f"{nt} templates"), ("skills", f"{ns} skills"), ("faq", "FAQ")])
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/how-we-work/">How we work</a> › <a href="{BASE}">Data essentials</a> › Starter kit</p>
<p class="eyebrow" style="margin-top:22px">Starter kit · templates and skills for a data project</p>
<h1>The data project starter kit</h1>
<p class="lede">{nt} templates and {ns} skills for the non-technical roles on a data project, as plain files you keep in git. No code. Open any of them below, or download the whole kit.</p>
<div class="tf">{CSS}
<nav class="toc"><b>On this page</b><ol>{toc}</ol></nav>
<section id="get"><p class="eyebrow">Start here</p><h2>Get the kit</h2>
<p><a class="dl" href="{ZIP}" download>Download the starter kit (zip)</a></p>
<pre class="tree" style="border:var(--line);border-radius:var(--wob);padding:10px 16px;background:#fff;font-size:14px;line-height:1.5;overflow-x:auto">{E(tree)}</pre>
<ol>{"".join(f"<li>{E(x)}</li>" for x in steps)}</ol>
<div class="box"><b>What a skill is:</b> a short written instruction, a template and a checklist that an AI assistant follows the same way every time. The result is a draft. A named person checks it and owns it.</div>
<p class="note">The kit belongs to {L(BASE + 'programme/', 'the 13-week programme')}, where each template is filled and each skill is built on a real project.</p></section>
<section id="templates"><p class="eyebrow">Templates</p><h2>{nt} templates for a data project</h2>{ttab}
<h3 style="margin-top:18px">Open a template</h3>{tshow}</section>
<section id="skills"><p class="eyebrow">Skills</p><h2>{ns} skills</h2>{stab}
<h3 style="margin-top:18px">Open a skill</h3>{sshow}
<p class="note">The estimator uses the figures on {Lx('/how-we-work/estimation/', 'estimation mistakes')}. The project review uses a short list of checks by stage; the full catalogue is {Lx('/learn/technical-anchor/project-review/checks/', 'the project review checks')}. The backlog builder pulls from {L(BASE + 'backlog/', 'the corpus backlog')}.</p></section>
<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(qa)}</section>
</div>"""
    title = "The data project starter kit: templates and skills"
    desc = (f"{nt} templates and {ns} skills for business analysts, project managers, PMO and delivery managers on a data project: Agile backlog, spec, estimate sheet, "
            "status report, project review, estimator. Plain files to keep in git. Free to download.")
    return url_path, DE.page_shell(title, desc, url_path, body, [("How we work", "/how-we-work/"), ("Data essentials", BASE), ("Starter kit", url_path)], qa)


def main():
    files = build_files()
    DE.write(*kit_page(files))


if __name__ == "__main__":
    main()
