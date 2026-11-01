"""Two left-panel sections and their pages: AI for a cause, and Deep tech.

    python3 _site/sections.py && python3 _site/nav.py && python3 _site/seo.py

Added 1 Nov 2026 at the owner's request. Each section has a hub page with cards, and the
projects that had no public page yet get one here:

    /ai-for-cause/          hub: Babu, AI for road safety, Raah
    /ai-for-cause/raah/     Raah, a low-cost walking guide for blind people (from ~/raah-vision-assist/PLAN.html)
    /deep-tech/             hub: Hard problems, Hinglish pre-training data, robot data benchmark

Pages that already existed keep their URLs (/projects/babu-companion/, /road-safety/, /problems/,
/projects/hinglish-pretraining-data/, /projects/robotics-data-benchmark/),
so no links break. The cards reuse hubs.py's card() and CSS; pages use the site shell from
_writing/build.py.
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("hubs", ROOT / "_site" / "hubs.py")
hubs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hubs)
wb, SITE, card, group = hubs.wb, hubs.SITE, hubs.card, hubs.group
MAIL = "basant@cleandataengineering.ai"

PERI, MINT, ROSE, BUTTER = "var(--peri-wash)", "var(--mint-wash)", "var(--rose-wash)", "var(--butter-wash)"

CSS = hubs.CSS + """<style>
  .stat { display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:14px; margin:24px 0; }
  .stat div { border:var(--line); border-radius:var(--wob); padding:12px 16px; background:var(--peri-wash); font-size:15px; }
  .stat b { display:block; font-family:var(--hand); font-size:30px; font-weight:400; line-height:1.1; }
  .answer { background:var(--butter-wash); border:var(--line); border-radius:var(--wob); padding:14px 20px; margin:20px 0; }
  .answer p { margin:6px 0; }
  .tw { overflow-x:auto; margin:10px 0 0; }
  .tw table { border-collapse:collapse; width:100%; font-size:15px; }
  .tw th, .tw td { border-bottom:1px solid var(--rule-firm); padding:9px 10px; text-align:left; vertical-align:top; }
  .tw th { background:var(--surface-2); font-weight:700; }
  .fig { border:var(--line); border-radius:var(--wob); padding:16px; margin:18px 0; background:#fff; }
  .fig svg { width:100%; height:auto; display:block; }
  .fig figcaption { font-size:14px; color:var(--muted); margin-top:8px; }
  .status { display:inline-block; font-size:12.5px; font-weight:700; padding:1px 10px; border:1.5px solid var(--ink); border-radius:999px; background:var(--rose-wash); }
  .join { border:var(--line); border-radius:var(--wob); padding:14px 20px; background:var(--mint-wash); margin:26px 0; }
  section.s { margin:34px 0 0; }
  .src { font-size:13.5px; color:var(--muted); }
</style>"""


def crumbs(*parts):
    """crumbs(("AI for a cause", "/ai-for-cause/"), ("Raah", None))"""
    bits = ['<a href="/">Home</a>'] + [f'<a href="{h}">{n}</a>' if h else n for n, h in parts]
    return f'<p class="crumbs">{" › ".join(bits)}</p>'


def table(head, rows):
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tw"><table><tr>{th}</tr>{tr}</table></div>'


def join_box(what, subject):
    return (f'<div class="join"><b>Want to help?</b> {what} Write to '
            f'<a href="mailto:{MAIL}?subject={subject}">{MAIL}</a> and say what you would like to pick up.</div>')


# ---------------------------------------------------------------- hubs
def ai_for_cause():
    body = crumbs(("AI for a cause", None)) + """
<p class="eyebrow" style="margin-top:22px">AI for a cause · free, open, not for profit</p>
<h1>AI for a cause</h1>
<p class="lede">Projects that use AI to help people who are usually left out: older adults living alone, people on India's roads, and blind people walking on their own. Each one is built to cost the person almost nothing, runs on a phone or tablet they may already own, and is open for anyone to join.</p>""" + group(
        "projects", "The projects", "Each has its own page with the plan, what's built and the open work.", [
            card("Babu, a companion for older adults", "/projects/babu-companion/", "Hindi-speaking companion on a tablet",
                 "A warm, patient companion for an older person living alone: daily chats, medicine reminders, family news, and rules that keep it honest and kind.",
                 [("The project", "/projects/babu-companion/"), ("A day with Babuji", "/projects/babu-companion/simulation/")], PERI),
            card("AI for road safety", "/road-safety/", "nine ideas, built cheaper",
                 "About 1.7 lakh people die on Indian roads every year. Nine AI tools that help, rebuilt around the phone people already own instead of costly hardware.",
                 [("Read the ideas", "/road-safety/")], BUTTER),
            card("Raah, a walking guide for blind people", "/ai-for-cause/raah/", "phone in a chest pouch, speaks Hindi",
                 "Warns about what's ahead (an auto, an open drain, a pole) and reads signs when asked. Works offline, adds to the white cane, costs the user under ₹500.",
                 [("Read the plan", "/ai-for-cause/raah/")], MINT),
        ]) + f"""
<section class="group"><h2>How these projects are run</h2>
<p>Three rules hold for all of them. <b>Low cost to the person comes first</b>: use the phone they own, run models on the device, use free and open data. <b>Safety and honesty are rules, not hopes</b>: the parts that decide what to say are plain rules that can be tested line by line. <b>Nothing is sold</b>: the code and designs are open source, and any outside money only puts hardware in people's hands for free.</p>
{join_box("Every project needs builders, testers and people who know the community it serves.", "AI%20for%20a%20cause")}</section>"""
    desc = "AI for a cause: open, not-for-profit projects that use AI to help people usually left out. Babu, a companion for older adults; AI for road safety in India; Raah, a low-cost walking guide for blind people."
    return "ai-for-cause", wb.page("AI for a cause", desc, f"{SITE}/ai-for-cause/", body, CSS)


def deep_tech():
    body = crumbs(("Deep tech", None)) + """
<p class="eyebrow" style="margin-top:22px">Deep tech · hard problems, measured</p>
<h1>Deep tech</h1>
<p class="lede">Hard research problems where one small group can still produce a result that counts. The common thread: <b>the quality of the data decides the quality of the model</b>, and that can be measured instead of argued about.</p>""" + group(
        "projects", "The projects", "Start with the list of hard problems, then pick a project that tests one of them.", [
            card("The hardest unsolved problems", "/problems/", "79 problems in 10 groups",
                 "From fusion to forgetting: what each problem is, why it's hard, and which ones one person or a small team can actually test.",
                 [("Browse the problems", "/problems/")], PERI),
            card("Hinglish pre-training data", "/projects/hinglish-pretraining-data/", "an open corpus for how India types",
                 "Hundreds of millions of people type Hindi in English letters, yet the biggest open web corpus holds only about 0.2 GB of it, and a third is junk. Build a clean, open one and prove it helps.",
                 [("The project", "/projects/hinglish-pretraining-data/")], MINT),
            card("A data benchmark for robot learning", "/projects/robotics-data-benchmark/", "same robot, same training, different data",
                 "Many methods claim to pick the best robot demonstrations, but each is tested on its own setup. One fixed test bench shows which ones help once the robot acts.",
                 [("The project", "/projects/robotics-data-benchmark/")], BUTTER),
        ]) + f"""
<section class="group"><h2>How these projects are run</h2>
<p>Each one fixes its success test <b>before</b> the work starts, uses free and open tools wherever they exist, keeps cloud GPU spend small (hundreds of dollars, not millions), and publishes data, code and results in the open, including results that show no effect.</p>
{join_box("These need people who like careful experiments: data engineers, ML engineers, researchers and students.", "Deep%20tech")}</section>"""
    desc = "Deep tech: hard research problems one small group can test. The 79 hardest unsolved problems, an open Hinglish pre-training corpus, and a data-curation benchmark for robot learning."
    return "deep-tech", wb.page("Deep tech", desc, f"{SITE}/deep-tech/", body, CSS)


# ---------------------------------------------------------------- Raah
RAAH_FIG = """<figure class="fig">
<svg viewBox="0 0 900 330" role="img" aria-label="Fast path on the phone: camera, small models, rule table, then vibration and Hindi voice. Ask path: button, question, cloud describer, answer.">
  <g fill="none" stroke="#1F1F1F" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="70" cy="70" r="26" fill="#FFF8E8"/>
    <path d="M70 96 L70 200 M70 200 L46 268 M70 200 L94 268 M70 130 L36 176 M70 130 L118 168"/>
    <path d="M118 168 L150 268" stroke-width="2.4"/>
    <path d="M54 118 Q52 112 60 112 L82 112 Q88 113 88 120 L89 160 Q88 166 82 166 L60 166 Q53 165 53 159 Z" fill="#E8EEF9"/>
    <path d="M196 80 Q192 70 204 70 L326 69 Q338 70 337 82 L338 122 Q337 134 325 134 L206 135 Q195 134 195 122 Z" fill="#E8EEF9"/>
    <path d="M378 80 Q374 70 386 70 L516 69 Q528 70 527 82 L528 122 Q527 134 515 134 L388 135 Q377 134 377 122 Z" fill="#E8EEF9"/>
    <path d="M568 80 Q564 70 576 70 L686 69 Q698 70 697 82 L698 122 Q697 134 685 134 L578 135 Q567 134 567 122 Z" fill="#FCE9EF"/>
    <path d="M738 80 Q734 70 746 70 L866 69 Q878 70 877 82 L878 122 Q877 134 865 134 L748 135 Q737 134 737 122 Z" fill="#EAF6EF"/>
    <path d="M100 140 C 140 120, 160 102, 194 102"/><path d="M338 102 L376 102"/><path d="M528 102 L566 102"/><path d="M698 102 L736 102"/>
    <path d="M196 220 Q192 210 204 210 L326 209 Q338 210 337 222 L338 262 Q337 274 325 274 L206 275 Q195 274 195 262 Z" fill="#FFF8E8"/>
    <path d="M378 220 Q374 210 386 210 L516 209 Q528 210 527 222 L528 262 Q527 274 515 274 L388 275 Q377 274 377 262 Z" fill="#FFF8E8"/>
    <path d="M738 220 Q734 210 746 210 L866 209 Q878 210 877 222 L878 262 Q877 274 865 274 L748 275 Q737 274 737 262 Z" fill="#EAF6EF"/>
    <path d="M150 244 L194 242"/><path d="M338 242 L376 242"/><path d="M528 242 C 620 242, 650 242, 736 242" stroke-dasharray="6 6"/>
  </g>
  <g font-family="DM Sans, sans-serif" font-size="13.5" fill="#1F1F1F" text-anchor="middle">
    <text x="266" y="98">camera, 10–15</text><text x="266" y="116">pictures a second</text>
    <text x="452" y="98">small models see:</text><text x="452" y="116">what, where, how far</text>
    <text x="632" y="98">rule table decides</text><text x="632" y="116">speak or stay quiet</text>
    <text x="806" y="98">buzz + Hindi voice</text><text x="806" y="116">"Ruko! Naali"</text>
    <text x="266" y="238">button pressed:</text><text x="266" y="256">"ye kya hai?"</text>
    <text x="452" y="238">read the sign on the</text><text x="452" y="256">phone, or ask the cloud</text>
    <text x="806" y="238">short spoken answer</text><text x="806" y="256">in a few seconds</text>
    <text x="70" y="300">phone in a</text><text x="70" y="316">chest pouch</text>
  </g>
  <g font-family="Patrick Hand, cursive" font-size="20" fill="#1F1F1F">
    <text x="196" y="52">Fast path · always on, no internet, about 0.3 seconds</text>
    <text x="196" y="196">Ask path · only when asked</text>
  </g>
</svg>
<figcaption>Pink box: the part that decides what to say is plain rules, so it behaves the same way every time and each rule can be tested. The AI models only report what they see.</figcaption>
</figure>"""


def raah():
    body = crumbs(("AI for a cause", "/ai-for-cause/"), ("Raah", None)) + f"""
<div class="hero" style="padding-top:22px"><p class="eyebrow">AI for a cause · <span class="status">plan · first interviews next</span></p>
<h1>Raah: a low-cost walking guide for blind people</h1>
<p class="thesis">A phone app, worn in a chest pouch, that warns about what is ahead and says what it is, in Hindi. Warnings work with no internet. The cloud is used only when the person asks "what is this?". It costs the user almost nothing. Raah (राह) means "path".</p></div>

<div class="answer"><p><b>Like you're five:</b> imagine a friend walking just behind you who keeps quiet most of the time. When something is in your way, they say "auto ahead, close, on your left." When you ask "what's this shop?", they read the board for you. Raah is that friend, living in a phone that hangs on your chest.</p></div>

<div class="stat">
<div><b>Under ₹500</b>cost to the user at first: a pouch and one earbud, on a phone they own</div>
<div><b>0.3 seconds</b>target time from seeing a hazard to buzzing, about 40 cm of walking</div>
<div><b>Offline</b>every safety warning works with no internet</div>
</div>

<section class="s"><p class="eyebrow">Why</p><h2>The problem</h2>
<p>India has millions of blind and low-vision people. Most use a white cane, which finds things at foot level but can't warn about a vehicle reversing toward them, a branch at head height, or say which bus has arrived. Devices that help exist, but they cost ₹2–4 lakh or are built for Western streets and English. Indian streets are harder: often no footpath, mixed traffic, parked bikes, open drains, speed breakers and stray animals.</p>
<p><b>The gap in one line:</b> describing a picture is a solved problem. Guiding someone safely along an Indian street, in their language, at a price they can pay, is not.</p></section>

<section class="s"><p class="eyebrow">Reuse first</p><h2>What already exists</h2>
{table(["Tool", "What it does", "What it lacks for this job"], [
        ["Be My Eyes, Seeing AI, Google Lookout", "Free apps that read text and describe a photo", "The phone is held in the hand, and you have to ask. No warnings while walking. We recommend them alongside Raah."],
        ["RBI MANI app", "Identifies Indian currency notes", "Only money. Raah links to it rather than rebuilding it."],
        ["Smart glasses (Envision, OrCam, Ray-Ban Meta)", "Camera glasses that read or describe", "₹30k to ₹4 lakh, mostly English, often need internet"],
        ["IIT Delhi SmartCane", "Cane vibrates for obstacles at body height", "Doesn't say what the thing is. It proves Indian users take up low-cost aids."],
    ])}</section>

<section class="s"><p class="eyebrow">What's new</p><h2>The part nobody has built yet</h2>
<ul>
<li><b>Hands-free warnings that run all the time</b> and speak only when something matters.</li>
<li><b>Trained on Indian streets:</b> autos, e-rickshaws, cows, dogs, open drains, speed breakers, handcarts, not just "car" and "person".</li>
<li><b>Hindi first, offline first.</b> Other languages later.</li>
<li><b>Free and open source.</b> A clip-on camera comes later, given free where possible through the government's ADIP scheme and NGOs.</li>
</ul></section>

<section class="s"><p class="eyebrow">How it works</p><h2>Two paths</h2>
{RAAH_FIG}</section>

<section class="s"><p class="eyebrow">The core</p><h2>Knowing when to stay quiet</h2>
<p>The hardest problem is talking too much, not detecting things. A street has dozens of objects. If the app names them all, the person stops listening, and their ears are what they rely on to hear traffic. So every detection gets one of three levels.</p>
{table(["Level", "Meaning", "What the person hears"], [
        ["<b>Stop</b>", "Could hurt within about 2 seconds: a vehicle within 3 m and coming closer, an open drain or step down ahead, a bar at head height", "A strong double buzz and one or two words, \"Ruko! Naali\". It interrupts anything else."],
        ["<b>In path</b>", "In the walking line but not urgent: a parked bike, a pole, a cow", "A short phrase with side and distance, \"Pole, seedha, 4 kadam\", said once."],
        ["<b>Info</b>", "Useful but not in the way: a door, a bench, a bus stop sign", "Only in explore mode, or when asked."],
    ])}</section>

<section class="s"><p class="eyebrow">Non-negotiable</p><h2>Safety rules</h2>
<ol>
<li><b>Never say "the path is clear."</b> Silence doesn't mean safe, and users learn that on day one.</li>
<li><b>The cane stays.</b> Raah adds to the white cane and never replaces it.</li>
<li><b>Ears stay open:</b> one earbud or bone-conduction headphones only.</li>
<li><b>Fail loudly.</b> If the camera is blocked, the battery is low or the phone overheats, it says so.</li>
<li><b>A missed hazard counts far more than a false alarm.</b> Better to warn about a shadow than miss a drain.</li>
</ol></section>

<section class="s"><p class="eyebrow">The plan</p><h2>Five phases, each with a pass or fail test</h2>
{table(["Phase", "When", "What", "Passes if"], [
        ["0 · Listen", "Nov 2026", "Walk real routes with 8–10 blind people through blind-welfare groups. Ask what goes wrong and what would help.", "A ranked list of their top 3 needs. If walking hazards aren't in it, the plan changes."],
        ["1 · Phone app", "Dec 2026 – Jan 2027", "Camera, ready-made detector, rule table, Hindi voice, buzz, and \"ye kya hai?\"", "Warning under 0.4 s, 2 hours of battery, 3 blind users use it alone after 15 minutes."],
        ["2 · Indian streets", "Feb – Mar 2027", "Retrain the detector on Indian street images and our own walk videos; add step-down detection", "Catches 95% of stop-level hazards in test videos, at most 1 false alarm a minute."],
        ["3 · Pilot", "Apr – Jun 2027", "20 people, 4 weeks of daily use, a sighted helper nearby at first", "12 of 20 still use it in week 4, and no safety incident caused by the app."],
        ["4 · Clip-on camera", "Jul – Dec 2027", "A spectacle camera that follows the head; more languages; NGOs hand it out", "Camera under ₹3k to make, and at least one NGO giving it out."],
    ])}
<p>Accuracy is a number, not a feeling: 200 short walk videos filmed from chest height on Indian streets, by day, night and in rain, with every hazard marked by hand. Every new version is scored on them before any user sees it.</p></section>

{join_box("Raah needs Android developers, people to film and label street videos, and above all blind and low-vision people and the groups that work with them, to tell us what matters.", "Raah")}
<p class="src">Plan version 0.1, 1 November 2026. Every number here is an estimate until phase 1 measures it. "Raah" is a working name.</p>"""
    desc = "Raah: a free, open-source phone app worn in a chest pouch that warns blind people about hazards ahead and reads signs when asked, in Hindi, offline, for under ₹500."
    return "ai-for-cause/raah", wb.page("Raah: a low-cost walking guide for blind people", desc, f"{SITE}/ai-for-cause/raah/", body, CSS)


# ---------------------------------------------------------------- certifications by vendor
# The certifications hub (hand-written) lists exams by role. This adds a "By vendor" section,
# built from those same table rows, so the left panel can link straight to one vendor.
VENDORS = [("anthropic", "Claude (Anthropic)", ["Anthropic"]), ("databricks", "Databricks", ["Databricks"]),
           ("microsoft", "Microsoft", ["Microsoft"]), ("aws", "AWS", ["AWS"]), ("gcp", "Google Cloud", ["Google Cloud"])]


def cert_vendors():
    import re
    f = ROOT / "certifications" / "index.html"
    t = f.read_text()
    t = re.sub(r"\n  <!-- vendors:start -->.*?<!-- vendors:end -->", "", t, flags=re.S)
    table_area = t[t.index('<section id="ai"'):t.index('<section id="cca"')]
    rows = []
    for sec in ("ai", "data"):
        part = table_area[table_area.index(f'<section id="{sec}"'):]
        part = part[:part.index("</section>")]
        for r in re.findall(r'<tr><td class="vd">(.*?)</td>(.*?)</tr>', part, re.S):
            rows.append((r[0], "AI" if sec == "ai" else "Data", r[1]))
    blocks = []
    for vid, name, keys in VENDORS:
        mine = [(kind, cells) for v, kind, cells in rows if v in keys]
        trs = "".join(f'<tr><td class="vd">{kind}</td>{cells}</tr>' for kind, cells in mine)
        blocks.append(f'<div id="{vid}" style="scroll-margin-top:20px"><h3 class="sub">{name}</h3>'
                      f'<div class="tbl"><table class="certs"><tr><th>Field</th><th>Certification</th><th>Level</th>'
                      f'<th>What it proves</th><th>Learn for it here</th></tr>{trs}</table></div></div>')
    sec = ('\n  <!-- vendors:start --><section id="vendors">\n    <p class="eyebrow">By vendor</p>\n'
           '    <h2>Certifications by vendor</h2>\n    <p>The same exams as above, grouped by who runs them. '
           'Other vendors (NVIDIA, Snowflake, dbt Labs, Confluent) are in the tables above.</p>\n    '
           + "".join(blocks) + "\n  </section><!-- vendors:end -->\n")
    i = t.index('  <section id="cca">')
    t = t[:i] + sec.lstrip("\n") + "\n" + t[i:]
    jump = '<a href="#vendors">By vendor</a> '
    if jump not in t:
        t = t.replace('<a href="#cca">Free prep: Claude</a>', jump + '<a href="#cca">Free prep: Claude</a>', 1)
    f.write_text(t)
    print("certifications -> by vendor:", ", ".join(f"{n} {sum(1 for v, _, _ in rows if v in k)}" for _, n, k in VENDORS))


def main():
    for fn in (ai_for_cause, deep_tech, raah):
        slug, html = fn()
        out = ROOT / slug
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(html)
        print("page ->", slug)
    cert_vendors()


if __name__ == "__main__":
    main()
