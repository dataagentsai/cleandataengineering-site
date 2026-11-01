"""AI for road safety, built cheaper: one page at /road-safety/.

    python3 _guides/road_safety.py && python3 _site/nav.py && python3 _site/seo.py

Copies the site's <head> styles, top bar and footer from mindset/index.html (nav.py then
rewrites the header with the current left panel), and writes road-safety/index.html.
Facts are from prior knowledge (1 Nov 2026); recheck before building.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = (ROOT / "mindset" / "index.html").read_text()
OUT = ROOT / "road-safety" / "index.html"

TITLE = "AI for road safety, built cheaper"
DESC = ("Nine AI tools that make Indian roads safer, rebuilt for a fraction of today's cost: "
        "phone instead of hardware, models on the phone, open data, no sales team.")
URL = "https://cleandataengineering.ai/road-safety/"

CSS = """
  .rs-stat { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:14px; margin:26px 0; }
  .rs-stat div { border:var(--line); border-radius:var(--wob); padding:14px 18px; background:var(--peri-wash); font-size:15px; }
  .rs-stat b { display:block; font-family:var(--hand); font-size:32px; font-weight:400; line-height:1.1; }
  .rs-answer { background:var(--butter-wash); border:var(--line); border-radius:var(--wob); padding:16px 22px; margin:22px 0; }
  .rs-answer p { margin:6px 0; }
  .rs-table { overflow-x:auto; margin:10px 0 0; }
  .rs-table table { border-collapse:collapse; width:100%; font-size:15px; }
  .rs-table th, .rs-table td { border-bottom:1px solid var(--rule-firm); padding:9px 10px; text-align:left; vertical-align:top; }
  .rs-table th { background:var(--surface-2); font-weight:700; }
  .rs-fig { border:var(--line); border-radius:var(--wob); padding:18px; margin:18px 0; background:#fff; }
  .rs-fig svg { width:100%; height:auto; display:block; }
  .rs-fig figcaption { font-size:14px; color:var(--muted); margin-top:8px; }
  .rs-cards { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:16px; margin-top:16px; }
  .rs-card { border:var(--line); border-radius:var(--wob); padding:16px 20px; background:var(--mint-wash); }
  .rs-card.later { background:var(--butter-wash); }
  .rs-card h3 { font-size:24px; margin:0 0 4px; line-height:1.15; }
  .rs-card p { margin:8px 0; font-size:15px; }
  .rs-card .lbl { display:block; font-size:11.5px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; color:var(--faint); }
  .rs-badge { display:inline-block; font-size:12.5px; font-weight:700; padding:1px 10px; border:1.5px solid var(--ink); border-radius:999px; background:#fff; }
"""

FIG = """<figure class="rs-fig">
<svg viewBox="0 0 900 370" role="img" aria-label="A phone with camera, motion sensors and GPS feeds one shared core, which serves six of the ideas">
  <g fill="none" stroke="#1F1F1F" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <path d="M44 84 Q40 80 48 78 L150 77 Q160 78 159 88 L161 284 Q160 294 150 295 L52 296 Q42 295 42 285 Z" fill="#F1F4FB"/>
    <rect x="58" y="104" width="86" height="150" rx="6" fill="#FFFFFF"/>
    <circle cx="101" cy="274" r="7"/>
    <path d="M166 186 C 200 180, 230 192, 262 186"/><path d="M252 178 L264 186 L252 194"/>
    <path d="M274 138 Q270 128 282 128 L462 126 Q474 128 474 140 L476 236 Q474 248 462 248 L284 250 Q272 248 272 236 Z" fill="#FFF8E8"/>
  </g>
  <g font-family="DM Sans, sans-serif" font-size="13" fill="#1F1F1F" text-anchor="middle">
    <text x="101" y="138">camera</text><text x="101" y="178">motion</text><text x="101" y="194">sensors</text><text x="101" y="232">GPS</text>
    <text x="101" y="326" font-family="Patrick Hand, cursive" font-size="20">The phone</text>
    <text x="374" y="168" font-family="Patrick Hand, cursive" font-size="22">Shared core</text>
    <text x="374" y="192">small models on the phone</text><text x="374" y="210">+ one data pipeline</text><text x="374" y="228">+ open maps</text>
  </g>
  <g fill="none" stroke="#1F1F1F" stroke-width="1.5">
    <path d="M476 188 C 545 188, 540 44, 600 44"/><path d="M476 188 C 545 188, 540 99, 600 99"/>
    <path d="M476 188 C 545 188, 540 154, 600 154"/><path d="M476 188 C 545 188, 540 209, 600 209"/>
    <path d="M476 188 C 545 188, 540 264, 600 264"/><path d="M476 188 C 545 188, 540 319, 600 319"/>
  </g>
  <g stroke="#1F1F1F" stroke-width="1.5">
    <rect x="600" y="26" width="282" height="36" rx="12" fill="#F0F8F3"/><rect x="600" y="81" width="282" height="36" rx="12" fill="#F0F8F3"/>
    <rect x="600" y="136" width="282" height="36" rx="12" fill="#F0F8F3"/><rect x="600" y="191" width="282" height="36" rx="12" fill="#F0F8F3"/>
    <rect x="600" y="246" width="282" height="36" rx="12" fill="#FFF8E8"/><rect x="600" y="301" width="282" height="36" rx="12" fill="#FFF8E8"/>
  </g>
  <g font-family="DM Sans, sans-serif" font-size="14" fill="#1F1F1F">
    <text x="614" y="49">2 · Driving coach in Hinglish</text><text x="614" y="104">3 · Crash SOS for budget phones</text>
    <text x="614" y="159">4 · Pothole map</text><text x="614" y="214">5 · Drowsy-driver alerts</text>
    <text x="614" y="269">8 · Danger-spot prediction</text><text x="614" y="324">9 · Pay-how-you-drive score</text>
  </g>
</svg>
<figcaption>Mint: start now. Butter: later. Idea 1, the crash database from news, runs on its own pipeline and feeds idea 8.</figcaption>
</figure>"""

# (number, title, now, today, cheaper, who)
IDEAS = [
    (1, "Crash database from news", True,
     "The government publishes totals once a year. Detailed crash records are not open.",
     "AI reads local-language news every day and pulls out the place, time, vehicles and cause, building an open, street-level map. Free models and news feeds keep the cost near zero.",
     "Grants, CSR funds, researchers, journalists."),
    (2, "Phone driving coach in Hinglish", True,
     "Telematics firms sell to insurers. Consumer apps are foreign and paid.",
     "The phone's motion sensors score each drive on the phone itself and give tips in Hinglish.",
     "The driver or a parent, through a small subscription."),
    (3, "Crash detection and SOS for budget phones", True,
     "Built into Pixel and iPhone only, which are expensive phones.",
     "An app for budget Android phones and two-wheeler riders that sends the location to family on WhatsApp or SMS.",
     "Bundled with the driving coach."),
    (4, "Pothole and road-damage map", True,
     "Survey vehicles and fees charged per kilometre.",
     "A phone on the dashboard runs a small detection model, and commuters and delivery riders build an open map.",
     "Grants first, cities later."),
    (5, "Drowsy and distracted driver alerts", True,
     "AI dashcam hardware plus a monthly fee per vehicle.",
     "An old phone faces the driver and checks for closed eyes and phone use on the device, with nothing sent to the cloud.",
     "Small fleets with 1–10 trucks."),
    (6, "Night voice companion for truck drivers", False,
     "Little exists.",
     "Voice chat in Hindi that checks the driver is still alert at night.",
     "The fleet or the driver's family."),
    (7, "Helmet and triple-riding detection", False,
     "Big city camera contracts.",
     "A cheap camera with a small edge box, or existing CCTV feeds.",
     "Factory gates, campuses and housing societies."),
    (8, "Danger-spot prediction", False,
     "The iRASTE pilot in Nagpur, plus manual road-safety audits.",
     "Built from idea 1's crash data, idea 4's pothole map and OpenStreetMap roads.",
     "Highway authorities and cities."),
    (9, "Pay-how-you-drive insurance score", False,
     "Insurer telematics programmes using a device or app contracts.",
     "Reuse idea 2's driving scores as a report the driver shares with their insurer.",
     "Insurers, once idea 2 has users."),
]


def card(n, title, now, today, cheaper, who):
    badge = "Start now" if now else "Later"
    return (f'<div class="rs-card{"" if now else " later"}"><h3>{n} · {title}</h3>'
            f'<span class="rs-badge">{badge}</span>'
            f'<p><span class="lbl">Today</span>{today}</p>'
            f'<p><span class="lbl">Low-cost version</span>{cheaper}</p>'
            f'<p><span class="lbl">Who could fund or pay</span>{who}</p></div>')


BODY = f"""<main class="wrap">
<div class="hero"><p class="eyebrow">Build with us · open idea, needs builders</p><h1>{TITLE}</h1>
<p class="thesis">The AI tools that make roads safer mostly exist already, but they are <em>expensive</em>. This page is about building the same nine jobs for a fraction of the cost, so ordinary people and small operators in India can afford them.</p></div>

<div class="rs-stat">
<div><b>~1.7 lakh</b>people die on Indian roads every year, the most of any country</div>
<div><b>9 ideas</b>5 to start now, 4 for later</div>
<div><b>1 shared core</b>one phone app and one data pipeline serve 6 of the 9</div>
</div>

<div class="rs-answer">
<p><b>Short answer: start with a crash database built from news (idea 1). Then build one phone app that holds the Hinglish driving coach and crash SOS (ideas 2 and 3).</b></p>
<p>"Someone already does it" is not a reason to skip an idea. The difference here is cost: the phone replaces special hardware, small models run on the phone instead of in the cloud, open data replaces paid data, and a self-serve app replaces a sales team.</p>
</div>

<section><p class="eyebrow">Where the money goes</p><h2>Why today's tools are expensive, and how to cut the cost</h2>
<div class="rs-table"><table>
<tr><th>What costs money today</th><th>Low-cost replacement</th></tr>
<tr><td>Dedicated AI dashcams and sensor boxes in every vehicle</td><td>The phone people already own, or an old Android phone mounted in the vehicle</td></tr>
<tr><td>Uploading video to the cloud and processing it there</td><td>Small models running on the phone. Only tiny results, like a pothole's location or a crash alert, leave it</td></tr>
<tr><td>Paid AI services</td><td>Free hosted open models for the few text steps</td></tr>
<tr><td>Paid maps and street imagery</td><td>OpenStreetMap, Mapillary open street imagery, public news</td></tr>
<tr><td>Survey vans and manual road audits</td><td>Crowd collection by volunteers, delivery riders and commuters using the app</td></tr>
<tr><td>Sales teams, pilots and contracts</td><td>A self-serve app on the Play Store</td></tr>
</table></div></section>

<section><p class="eyebrow">The trick</p><h2>One phone, many ideas</h2>
<p>The phone already has a camera, motion sensors and GPS. Build the app that reads them once, and most of the ideas become small add-ons.</p>
{FIG}</section>

<section><p class="eyebrow">The list</p><h2>The nine ideas</h2>
<div class="rs-cards">
{chr(10).join(card(*i) for i in IDEAS)}
</div></section>

<section><p class="eyebrow">Order</p><h2>Order of work</h2>
<ol>
<li><b>Idea 1, crash database.</b> It is the cheapest, a public good and grant-friendly, and it creates the data the other ideas need.</li>
<li><b>Ideas 2 and 3</b> as one phone app. This builds the shared phone core.</li>
<li><b>Ideas 4 and 5</b> as add-ons to the same app.</li>
<li><b>Ideas 6 to 9</b> once there are data and users.</li>
</ol>
<p><b>First small step for idea 1:</b> pick one state, list 20 Hindi and English local news feeds, extract one week of crash reports with a free model, and count how many give a usable place name.</p></section>

<section><p class="eyebrow">Join</p><h2>Want to build one of these?</h2>
<p>All nine are open. Each one needs a lead, and idea 1 is a good first project for a data engineer who wants to learn language models on real, messy data. Write to <a href="mailto:basant@cleandataengineering.ai?subject=Road%20safety%20idea">basant@cleandataengineering.ai</a> with the idea number you want to pick up.</p>
<p style="font-size:14px;color:var(--muted)">Sources, from prior knowledge and to be rechecked before building: Ministry of Road Transport and Highways, "Road Accidents in India" yearly reports; iRASTE Nagpur (Intel, IIIT Hyderabad); crash detection on Pixel and iPhone; IRDAI's 2022 approval of telematics add-ons.</p></section>
</main>
"""


def main():
    head_end = SRC.index("</style>")
    head = SRC[:head_end] + CSS + SRC[head_end:SRC.index("<main")]
    head = re.sub(r"<title>.*?</title>", f"<title>{TITLE} · Clean Data Engineering</title>", head, count=1)
    head = re.sub(r'(<meta name="description" content=")[^"]*', rf"\g<1>{DESC}", head, count=1)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', rf"\g<1>{TITLE}", head, count=1)
    head = re.sub(r'(<meta property="og:description" content=")[^"]*', rf"\g<1>{DESC}", head, count=1)
    head = head.replace("https://cleandataengineering.ai/mindset/", URL)
    foot = SRC[SRC.index("<footer>"):]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(head + BODY + foot)
    print("wrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
