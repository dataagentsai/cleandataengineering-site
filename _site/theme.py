"""The site's one look: white, soothing pastels, hand-drawn. Light only.

    python3 _site/theme.py

Puts THEME (below) into the first <style> block of the hand-made pages (home, /learn/, the certifications hub),
and draws the home page's cartoon (the horse in harness, keeping to the green path) between the hero markers.
/writing/ and /projects/ copy the home page's style when they build, so rebuild them after this.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ["index.html", "learn/index.html", "certifications/index.html"]
HUBS = {"learn/index.html": "learn", "certifications/index.html": "certifications"}

THEME = """<style>
  /* Clean Data Engineering: white, soothing, hand-drawn. Light only, on purpose. */
  :root {
    color-scheme: light;
    --paper:#FFFFFF; --surface:#FFFFFF; --surface-2:#F7F6F2;
    --ink:#1F1F1F; --ink-soft:#3D3D3D; --muted:#555555; --faint:#8A8A8A;
    --rule:#ECE9E2; --rule-firm:#CFCAC0;
    --accent:#3B4F8F; --accent-wash:#F1F4FB;
    --peri:#A3B5DF; --peri-wash:#F1F4FB; --butter:#FFD98A; --butter-wash:#FFF8E8;
    --rose:#E6BFD2; --rose-wash:#FCF2F7; --mint:#B9DFC8; --mint-wash:#F0F8F3;
    --lilac:#CDBFE6; --lilac-wash:#F6F2FC; --sky:#AED9E8; --sky-wash:#EFF8FB;
    --hand:"Patrick Hand","Comic Sans MS",cursive;
    --sans:"DM Sans",ui-sans-serif,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
    --serif:var(--sans);
    --mono:"JetBrains Mono",ui-monospace,"SF Mono",Menlo,Consolas,monospace;
    --line:1.5px solid var(--ink);
    --wob:255px 18px 225px 18px/18px 225px 18px 255px;
  }
  * { box-sizing:border-box; }
  html { color-scheme:light; background:#FFFFFF; }
  body { margin:0; background:#FFFFFF; color:var(--ink); font-family:var(--sans); font-size:17px; line-height:1.65; -webkit-font-smoothing:antialiased; }
  .wrap { max-width:860px; margin:0 auto; padding:0 20px; }
  a { color:var(--accent); text-underline-offset:3px; }

  header { padding:26px 0 0; }
  nav { display:flex; align-items:baseline; gap:6px 18px; flex-wrap:wrap; }
  .brand { font-family:var(--hand); font-size:25px; color:var(--ink); text-decoration:none; margin-right:auto; }
  nav a.n { font-size:14.5px; color:var(--muted); text-decoration:none; }
  nav a.n:hover { color:var(--ink); text-decoration:underline; text-decoration-style:wavy; }

  h1, h2, h3 { font-family:var(--hand); font-weight:400; letter-spacing:0; }
  .hero { padding:52px 0 8px; }
  .hero.art-hero { display:grid; grid-template-columns:1fr 1fr; gap:36px; align-items:center; }
  h1 { font-size:clamp(40px,6vw,58px); line-height:1.05; margin:0 0 18px; }
  .thesis { font-size:19px; line-height:1.6; color:var(--ink-soft); }
  .thesis em { font-style:normal; background:linear-gradient(transparent 62%, var(--butter) 62%); }
  .art svg { width:100%; height:auto; display:block; }

  section { padding:48px 0 0; margin-top:48px; border-top:1.5px dashed var(--rule-firm); }
  h2 { font-size:34px; line-height:1.15; margin:0 0 10px; }
  .eyebrow { font-family:var(--sans); font-size:12px; font-weight:700; letter-spacing:.14em; text-transform:uppercase; color:var(--faint); margin:0 0 6px; }
  p { margin:0 0 16px; }

  .questions { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:12px; margin:22px 0 0; }
  .q { background:var(--peri-wash); border:var(--line); border-radius:var(--wob); padding:14px 18px; }
  .q b { display:block; font-family:var(--hand); font-size:22px; font-weight:400; color:var(--ink); margin-bottom:2px; }
  .q span { font-size:14.5px; color:var(--muted); line-height:1.5; }
  a.q { text-decoration:none; color:inherit; }

  .standards { display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:18px; margin-top:22px; }
  .std { background:var(--peri-wash); border:var(--line); border-radius:var(--wob); padding:18px 22px; display:flex; flex-direction:column; }
  #learn .std { background:var(--mint-wash); }
  .std h3 { font-size:25px; margin:0 0 2px; color:var(--ink); }
  .std .v { font-family:var(--mono); font-size:11.5px; color:var(--faint); margin-bottom:8px; }
  .std p { font-size:15px; color:var(--ink-soft); margin:0 0 12px; line-height:1.55; }
  .std .links { font-size:14.5px; margin-top:auto; display:flex; gap:14px; flex-wrap:wrap; }
  .std .doi { font-family:var(--mono); font-size:11.5px; color:var(--faint); }

  .research { background:var(--butter-wash); border:var(--line); border-radius:var(--wob); padding:22px 26px; margin-top:22px; }
  .research h3 { font-size:25px; margin:0 0 8px; }
  .research p, .research li { font-size:15.5px; color:var(--ink-soft); line-height:1.6; }
  .research ol { margin:0 0 14px; padding-left:20px; } .research li { margin:4px 0; }
  .status { display:inline-block; font-family:var(--sans); font-size:11.5px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; color:var(--ink); background:var(--butter); border:1.5px solid var(--ink); padding:1px 10px; border-radius:999px; vertical-align:middle; }

  ul.posts { list-style:none; margin:20px 0 0; padding:0; }
  ul.posts li { padding:14px 0; border-bottom:1.5px dashed var(--rule); }
  ul.posts li:first-child { border-top:1.5px dashed var(--rule); }
  ul.posts .t { font-size:18px; font-weight:600; color:var(--ink); display:block; text-decoration:none; }
  ul.posts a.t:hover { text-decoration:underline; text-decoration-style:wavy; }
  ul.posts .d { font-family:var(--sans); font-size:13px; color:var(--faint); display:block; margin-top:3px; }

  .picker { display:flex; flex-wrap:wrap; gap:10px 12px; align-items:center; margin:18px 0 0; font-size:16px; background:var(--butter-wash); border:var(--line); border-radius:var(--wob); padding:14px 18px; }
  .picker label { display:flex; gap:8px; align-items:center; }
  .picker select { font:inherit; font-size:15.5px; border:1.5px solid var(--ink); border-radius:10px; padding:5px 8px; background:#fff; color:var(--ink); max-width:100%; }
  .picker button { font:inherit; font-weight:700; font-size:15.5px; border:1.5px solid var(--ink); border-radius:var(--wob); padding:6px 16px; background:var(--ink); color:#fff; cursor:pointer; }
  .roles { display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:14px; margin-top:22px; }
  .role { border:var(--line); border-radius:var(--wob); padding:16px 20px; background:var(--wash); display:flex; flex-direction:column; }
  .role h3 { font-size:25px; margin:0 0 4px; } .role h3 a { color:var(--ink); text-decoration:none; }
  .role p { font-size:15px; color:var(--ink-soft); margin:0 0 10px; line-height:1.5; }
  .role .lv { display:flex; gap:8px; flex-wrap:wrap; margin-top:auto; }
  .role .lv a { font-size:14px; font-weight:700; border:1.5px solid var(--ink); border-radius:999px; padding:1px 12px; background:#fff; color:var(--ink); text-decoration:none; }
  .role .pl { font-size:13px; color:var(--faint); margin-top:10px; } .role .pl a { color:var(--muted); }

  footer { border-top:1.5px dashed var(--rule-firm); margin-top:64px; padding:26px 0 56px; font-size:14px; color:var(--faint); }
  footer a { color:var(--muted); }
  .art img { width:100%; height:auto; display:block; }
  .spot { float:right; width:min(270px,40%); height:auto; margin:-18px 0 12px 26px; }
  .hub-hero { display:grid; grid-template-columns:1.2fr .8fr; gap:30px; align-items:center; }
  .hub-hero img { width:100%; height:auto; }
  section::after { content:""; display:block; clear:both; }
  @media (max-width:760px) { .hero.art-hero, .hub-hero { grid-template-columns:1fr; } .art { max-width:440px; } .spot { width:42%; } }
</style>"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,600;9..40,700&family=Patrick+Hand&family=JetBrains+Mono:wght@500&display=swap">')


def hero_art():
    return ('<div class="art"><img src="/assets/illustrations/hero-team.svg" alt="Two people at a whiteboard sketching a flow, with a lightbulb above them." width="600" height="440">'
            '<p class="eyebrow" style="text-align:center;margin-top:4px"><a href="/learn/agent-harness/arch-horse.html">Why our mascot is a horse →</a></p></div>')


def hero_art_horse():
    """The horse in harness on a soft green road: the site's mascot drawing."""
    sys.path.insert(0, str(Path.home() / "agent-harness-tutorial"))
    import kit
    import pages_horse as ph
    d = ('<rect x="0" y="40" width="560" height="44" fill="#FCF2F7"/><rect x="0" y="84" width="560" height="40" fill="#FFF8E8"/>'
         '<rect x="0" y="124" width="560" height="190" fill="#F0F8F3"/><rect x="0" y="314" width="560" height="40" fill="#FFF8E8"/>'
         '<rect x="0" y="354" width="560" height="44" fill="#FCF2F7"/>'
         '<line class="lnd" x1="0" y1="124" x2="560" y2="124"/><line class="lnd" x1="0" y1="314" x2="560" y2="314"/>')
    g = ('<line class="ln" x1="370" y1="236" x2="652" y2="240"/><line class="ln" x1="370" y1="256" x2="650" y2="256"/>'
         '<rect class="bx" x="240" y="205" width="130" height="66" rx="10"/>'
         '<circle class="bx" cx="292" cy="286" r="32"/><line class="ln" x1="292" y1="254" x2="292" y2="318"/><line class="ln" x1="260" y1="286" x2="324" y2="286"/>'
         '<circle class="bx" cx="335" cy="168" r="14"/><line class="lnc" x1="335" y1="182" x2="335" y2="206"/><line class="lnc" x1="335" y1="192" x2="362" y2="190"/>'
         + ph.horse() + '<path class="lnc" d="M752,198 Q620,140 364,190"/>')
    d += f'<g transform="translate(-205,10) scale(0.92)">{g}</g>'
    d += kit.text(280, 30, "the model is the horse · the harness keeps it on the green path", "sm", "middle")
    css = ("<style>.art{--ink:#222;--paper:#fff;--soft:#F3F3F1;--fill:#ECECEA;--muted:#5E5E5E;--hand:\"Patrick Hand\",cursive}"
           ".art svg rect,.art svg line,.art svg path,.art svg circle,.art svg ellipse{filter:url(#rough)}"
           ".art text{font-family:var(--hand)} .art .bx{fill:#fff;stroke:#222;stroke-width:2} .art .hz{fill:#fff;stroke:#222;stroke-width:2.2;stroke-linejoin:round}"
           ".art .hk{fill:#222;stroke:#222} .art .bxs{fill:#F3F3F1;stroke:#222;stroke-width:2} .art .ln{stroke:#222;stroke-width:1.8;fill:none}"
           ".art .lnd{stroke:#222;stroke-width:1.5;fill:none;stroke-dasharray:6 5;opacity:.55} .art .lnc{stroke:#222;stroke-width:3;fill:none;stroke-linecap:round}"
           ".art .sm{fill:#5E5E5E;font-size:15px}</style>")
    return (f'<div class="art">{css}{kit.DEFS}<svg viewBox="0 0 560 400" role="img" aria-label="A horse in harness pulling a cart along the green middle of a road, with soft yellow and pink edges.">{d}</svg>'
            f'<p class="eyebrow" style="text-align:center;margin-top:6px"><a href="/learn/agent-harness/arch-horse.html">Why a horse? →</a></p></div>')


def main():
    for rel in PAGES:
        p = ROOT / rel
        if not p.exists():
            continue
        s = p.read_text()
        s = re.sub(r"<style>.*?</style>", lambda m: THEME, s, count=1, flags=re.S)
        s = re.sub(r'<meta name="color-scheme"[^>]*>', "", s)
        s = s.replace("<head>", '<head>\n<meta name="color-scheme" content="light">', 1)
        if "family=Patrick+Hand" not in s:
            s = s.replace("<style>", FONTS + "\n<style>", 1)
        if rel == "index.html":
            a, b = "<!-- hero-art:start -->", "<!-- hero-art:end -->"
            if a not in s:
                s = s.replace('<div class="hero">', '<div class="hero art-hero"><div>', 1)
                s = s.replace("</p>\n  </div>", f"</p>\n  </div>\n  {a}{b}\n  </div>", 1)
            s = s[: s.index(a) + len(a)] + hero_art() + s[s.index(b):]
        if rel == "index.html":
            for sec, art in (("learn", "learn"), ("projects", "projects"), ("standards", "standards"),
                             ("research", "research"), ("writing", "writing"), ("about", "about")):
                tag = f'<section id="{sec}">'
                img = f'<img class="spot" src="/assets/illustrations/{art}.svg" alt="" width="420" height="300">'
                if tag in s and img not in s:
                    s = s.replace(tag, tag + "\n    " + img, 1)
        if rel in HUBS and 'class="hub-hero"' not in s:
            art = HUBS[rel]
            s = re.sub(r'<div class="hero">(.*?)</div>',
                       lambda m: f'<div class="hero hub-hero"><div>{m.group(1)}</div><img src="/assets/illustrations/{art}.svg" alt="" width="420" height="300"></div>',
                       s, count=1, flags=re.S)
        p.write_text(s)
        print("themed", rel)


if __name__ == "__main__":
    main()
