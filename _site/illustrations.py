"""Spot illustrations for the site, all in one style: flat, friendly, soft pastels, thin dark outlines.

    python3 _site/illustrations.py      # writes assets/illustrations/<name>.svg

Every scene is built from the same parts (person, blob, board, blocks, book, badge, plant, bulb), so the
people and colours stay consistent from page to page.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "illustrations"
INK = "#1E1B3A"
PAL = dict(mint="#C9F2E3", peach="#FBE6DA", peri="#DDE5FB", butter="#FFF0C2", rose="#F8DDE9", lav="#E7DEF8",
           blue="#5B6BEF", yellow="#FFC75A", orange="#FF8A5B", green="#2FA58A", plum="#7A5AC8", navy="#2B2862",
           coral="#F07C7C", teal="#3BB4C1")
SKIN = ["#F2A07B", "#B9673F", "#E8B48E", "#8D5634"]
HAIR = ["#26224D", "#1E1B3A", "#5A3A2A", "#26224D"]
STYLE = f"""<style>.o{{stroke:{INK};stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}}
.t{{fill:none;stroke:{INK};stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}}</style>"""


def svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">'
            f'<title>{label}</title><defs>{STYLE}</defs>{body}</svg>')


def blob(cx, cy, rx, ry, color, wobble=0.12):
    """A soft organic blob."""
    k = wobble
    return (f'<path d="M{cx - rx},{cy} C{cx - rx},{cy - ry * (1 + k)} {cx - rx * .2},{cy - ry} {cx + rx * .1},{cy - ry * (1 - k)} '
            f'C{cx + rx * .7},{cy - ry * (1 + k)} {cx + rx},{cy - ry * .4} {cx + rx},{cy + ry * .1} '
            f'C{cx + rx},{cy + ry * (1 + k)} {cx + rx * .3},{cy + ry} {cx - rx * .2},{cy + ry * (1 - k)} '
            f'C{cx - rx * .8},{cy + ry} {cx - rx},{cy + ry * .5} {cx - rx},{cy} Z" fill="{color}"/>')


def person(x, y, shirt, pants, skin=0, reach=None, face=1, scale=1.0, sit=False):
    """A friendly standing (or sitting) person. (x, y) = feet centre. reach = (hx, hy) for one hand, or None."""
    s = scale
    S, H = SKIN[skin], HAIR[skin]
    g = []
    if not sit:
        g.append(f'<path d="M{x - 36 * s},{y} L{x - 30 * s},{y - 90 * s} C{x - 28 * s},{y - 100 * s} {x + 28 * s},{y - 100 * s} {x + 30 * s},{y - 90 * s} L{x + 36 * s},{y} Z" fill="{pants}" class="o"/>')
        top = y - 92 * s
    else:
        g.append(f'<path d="M{x - 30 * s},{y - 40 * s} L{x + 50 * s},{y - 40 * s} L{x + 54 * s},{y} L{x + 30 * s},{y} L{x + 28 * s},{y - 22 * s} L{x - 30 * s},{y - 22 * s} Z" fill="{pants}" class="o"/>')
        top = y - 40 * s
    # body
    g.append(f'<path d="M{x - 46 * s},{top} C{x - 50 * s},{top - 70 * s} {x - 30 * s},{top - 108 * s} {x},{top - 110 * s} '
             f'C{x + 32 * s},{top - 108 * s} {x + 50 * s},{top - 70 * s} {x + 46 * s},{top} Z" fill="{shirt}" class="o"/>')
    sh = (x + 34 * s * face, top - 84 * s)
    if reach:
        g.append(f'<path d="M{sh[0]},{sh[1]} Q{(sh[0] + reach[0]) / 2},{sh[1] + 6 * s} {reach[0]},{reach[1]}" fill="none" stroke="{shirt}" stroke-width="{18 * s}" stroke-linecap="round"/>')
        g.append(f'<circle cx="{reach[0]}" cy="{reach[1]}" r="{9 * s}" fill="{S}" class="o"/>')
    else:
        g.append(f'<path d="M{sh[0]},{sh[1]} Q{sh[0] + 14 * s * face},{sh[1] + 40 * s} {sh[0] + 4 * s * face},{sh[1] + 66 * s}" fill="none" stroke="{shirt}" stroke-width="{17 * s}" stroke-linecap="round"/>')
        g.append(f'<circle cx="{sh[0] + 4 * s * face}" cy="{sh[1] + 70 * s}" r="{8 * s}" fill="{S}" class="o"/>')
    # neck, head, hair, face
    hx, hy = x + 4 * s * face, top - 132 * s
    g.append(f'<rect x="{x - 7 * s}" y="{top - 114 * s}" width="{16 * s}" height="{14 * s}" rx="{5 * s}" fill="{S}"/>')
    g.append(f'<circle cx="{hx}" cy="{hy}" r="{25 * s}" fill="{S}" class="o"/>')
    g.append(f'<path d="M{hx - 26 * s},{hy - 2 * s} C{hx - 28 * s},{hy - 30 * s} {hx + 16 * s},{hy - 40 * s} {hx + 26 * s},{hy - 12 * s} '
             f'C{hx + 14 * s},{hy - 20 * s} {hx - 4 * s},{hy - 22 * s} {hx - 18 * s},{hy + 4 * s} Z" fill="{H}"/>')
    ex = hx + 8 * s * face
    g.append(f'<circle cx="{ex - 5 * s}" cy="{hy + 2 * s}" r="{2.3 * s}" fill="{INK}"/><circle cx="{ex + 7 * s}" cy="{hy + 1 * s}" r="{2.3 * s}" fill="{INK}"/>')
    g.append(f'<path d="M{ex - 6 * s},{hy + 12 * s} C{ex - 1 * s},{hy + 17 * s} {ex + 6 * s},{hy + 16 * s} {ex + 9 * s},{hy + 11 * s}" class="t" style="stroke-width:2"/>')
    return "".join(g)


def board(x, y, w, h, tilt=-3, content="flow"):
    c = f'<g transform="rotate({tilt} {x + w / 2} {y + h / 2})"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#fff" class="o"/>'
    c += f'<line x1="{x}" y1="{y + 22}" x2="{x + w}" y2="{y + 22}" class="t" style="stroke-width:1.6"/>'
    c += f'<circle cx="{x + w - 26}" cy="{y + 11}" r="4" fill="{PAL["blue"]}"/><circle cx="{x + w - 13}" cy="{y + 11}" r="4" fill="{PAL["yellow"]}"/>'
    if content == "flow":
        bx = [(x + 24, y + 52, PAL["peri"]), (x + w / 2 - 22, y + 52, PAL["butter"]), (x + w - 70, y + 52, PAL["lav"])]
        for i, (a, b, col) in enumerate(bx):
            c += f'<rect x="{a}" y="{b}" width="46" height="32" rx="8" fill="{col}" class="o" style="stroke-width:1.8"/>'
            if i < 2:
                c += f'<line x1="{a + 48}" y1="{b + 16}" x2="{bx[i + 1][0] - 2}" y2="{b + 16}" class="t" style="stroke-width:1.8"/>'
        c += f'<rect x="{x + w / 2 - 22}" y="{y + 108}" width="46" height="30" rx="8" fill="{PAL["mint"]}" class="o" style="stroke-width:1.8"/>'
        c += f'<line x1="{x + w / 2 + 1}" y1="{y + 86}" x2="{x + w / 2 + 1}" y2="{y + 106}" class="t" style="stroke-width:1.8"/>'
    elif content == "chart":
        for i, hh in enumerate([30, 52, 40, 70, 58]):
            c += f'<rect x="{x + 30 + i * 30}" y="{y + h - 20 - hh}" width="18" height="{hh}" rx="3" fill="{[PAL["blue"], PAL["green"], PAL["yellow"], PAL["plum"], PAL["teal"]][i]}"/>'
        c += f'<line x1="{x + 20}" y1="{y + h - 20}" x2="{x + w - 20}" y2="{y + h - 20}" class="t" style="stroke-width:1.6"/>'
    elif content == "checklist":
        for i in range(4):
            yy = y + 44 + i * 30
            c += f'<rect x="{x + 22}" y="{yy - 10}" width="18" height="18" rx="4" fill="{PAL["mint"] if i < 3 else "#fff"}" class="o" style="stroke-width:1.8"/>'
            if i < 3:
                c += f'<path d="M{x + 26},{yy} L{x + 30},{yy + 4} L{x + 37},{yy - 5}" class="t" style="stroke:{PAL["green"]};stroke-width:2.6"/>'
            c += f'<line x1="{x + 52}" y1="{yy}" x2="{x + w - 30 - (i % 2) * 40}" y2="{yy}" class="t" style="stroke-width:1.8;stroke:#B9B6CC"/>'
    elif content == "text":
        for i in range(6):
            c += f'<line x1="{x + 22}" y1="{y + 44 + i * 20}" x2="{x + w - 24 - (i % 3) * 30}" y2="{y + 44 + i * 20}" class="t" style="stroke-width:1.8;stroke:#B9B6CC"/>'
    return c + "</g>"


def bulb(x, y):
    r = "".join(f'<line x1="{x + a}" y1="{y + b}" x2="{x + c}" y2="{y + d}"/>' for a, b, c, d in
                [(0, -28, 0, -40), (-26, -14, -37, -22), (26, -14, 37, -22), (-30, 10, -43, 12), (30, 10, 43, 12)])
    return (f'<g class="t" style="stroke:#F2A93B;stroke-width:4">{r}</g><circle cx="{x}" cy="{y + 8}" r="22" fill="{PAL["yellow"]}" class="o"/>'
            f'<path d="M{x - 7},{y + 16} C{x - 12},{y + 5} {x - 3},{y} {x},{y + 7} C{x + 3},{y} {x + 12},{y + 5} {x + 7},{y + 16}" class="t"/>'
            f'<rect x="{x - 10}" y="{y + 29}" width="20" height="13" rx="4" fill="{PAL["navy"]}" class="o"/>')


def plant(x, y, s=1):
    return (f'<path d="M{x - 18 * s},{y - 36 * s} L{x + 18 * s},{y - 36 * s} L{x + 13 * s},{y} L{x - 13 * s},{y} Z" fill="{PAL["orange"]}" class="o"/>'
            f'<path d="M{x},{y - 36 * s} C{x - 26 * s},{y - 60 * s} {x - 30 * s},{y - 92 * s} {x - 8 * s},{y - 104 * s} C{x + 2 * s},{y - 80 * s} {x + 4 * s},{y - 58 * s} {x},{y - 36 * s} Z" fill="{PAL["green"]}" class="o"/>'
            f'<path d="M{x + 2 * s},{y - 36 * s} C{x + 14 * s},{y - 64 * s} {x + 36 * s},{y - 76 * s} {x + 46 * s},{y - 70 * s} C{x + 40 * s},{y - 50 * s} {x + 22 * s},{y - 38 * s} {x + 2 * s},{y - 36 * s} Z" fill="#7FD1B4" class="o"/>')


def blocks(x, y):
    cols = [PAL["blue"], PAL["yellow"], PAL["coral"], PAL["green"], PAL["plum"], PAL["teal"]]
    pos = [(0, 0), (56, 0), (112, 0), (28, -46), (84, -46), (56, -92)]
    return "".join(f'<rect x="{x + a}" y="{y + b - 44}" width="52" height="44" rx="6" fill="{cols[i]}" class="o"/>' for i, (a, b) in enumerate(pos))


def book(x, y):
    return (f'<path d="M{x},{y} C{x + 40},{y - 14} {x + 70},{y - 10} {x + 90},{y + 4} L{x + 90},{y + 84} C{x + 70},{y + 70} {x + 40},{y + 66} {x},{y + 80} Z" fill="#fff" class="o"/>'
            f'<path d="M{x + 180},{y} C{x + 140},{y - 14} {x + 110},{y - 10} {x + 90},{y + 4} L{x + 90},{y + 84} C{x + 110},{y + 70} {x + 140},{y + 66} {x + 180},{y + 80} Z" fill="{PAL["peri"]}" class="o"/>'
            + "".join(f'<line x1="{x + 14}" y1="{y + 14 + i * 14}" x2="{x + 76}" y2="{y + 10 + i * 14}" class="t" style="stroke-width:1.6;stroke:#B9B6CC"/>' for i in range(4)))


def badge(x, y):
    return (f'<path d="M{x - 16},{y + 22} L{x - 26},{y + 70} L{x - 6},{y + 60} L{x + 2},{y + 78} L{x + 8},{y + 26} Z" fill="{PAL["coral"]}" class="o"/>'
            f'<path d="M{x + 16},{y + 22} L{x + 26},{y + 70} L{x + 6},{y + 60} L{x - 2},{y + 78} L{x - 8},{y + 26} Z" fill="{PAL["blue"]}" class="o"/>'
            f'<circle cx="{x}" cy="{y}" r="34" fill="{PAL["yellow"]}" class="o"/><circle cx="{x}" cy="{y}" r="22" fill="#fff" class="o"/>'
            f'<path d="M{x - 9},{y} L{x - 2},{y + 7} L{x + 11},{y - 7}" class="t" style="stroke:{PAL["green"]};stroke-width:3.5"/>')


def laptop(x, y):
    return (f'<rect x="{x}" y="{y}" width="120" height="78" rx="6" fill="#fff" class="o"/>'
            f'<rect x="{x + 12}" y="{y + 12}" width="40" height="10" rx="3" fill="{PAL["peri"]}"/><rect x="{x + 12}" y="{y + 30}" width="80" height="8" rx="3" fill="{PAL["butter"]}"/><rect x="{x + 12}" y="{y + 46}" width="60" height="8" rx="3" fill="{PAL["mint"]}"/>'
            f'<path d="M{x - 14},{y + 78} L{x + 134},{y + 78} L{x + 124},{y + 90} L{x - 4},{y + 90} Z" fill="{PAL["navy"]}" class="o"/>')


SCENES = {
    # name: (w, h, body, label)
    "learn": (420, 300,
              blob(210, 170, 190, 120, PAL["mint"]) + board(130, 50, 230, 170, -2, "flow") +
              person(90, 300, PAL["yellow"], PAL["orange"], 0, reach=(160, 132)) + bulb(370, 50),
              "A learner points at a flow on a board, with a lightbulb above."),
    "projects": (420, 300,
                 blob(210, 175, 190, 115, PAL["peach"]) + blocks(140, 280) +
                 person(80, 300, PAL["green"], PAL["navy"], 1, reach=(146, 196)) +
                 person(352, 300, PAL["blue"], PAL["navy"], 2, reach=(300, 196), face=-1),
                 "Two people build a tower of colourful blocks together."),
    "standards": (420, 300,
                  blob(220, 170, 185, 118, PAL["peri"]) + board(150, 40, 200, 190, 2, "checklist") +
                  person(96, 300, PAL["plum"], PAL["navy"], 3, reach=(168, 150)) + plant(375, 290, 0.9),
                  "A person ticks items off a checklist on a board, next to a plant."),
    "research": (420, 300,
                 blob(210, 168, 192, 118, PAL["lav"]) + board(120, 52, 240, 170, -2, "chart") +
                 person(352, 300, PAL["teal"], PAL["navy"], 0, reach=(300, 160), face=-1) + bulb(90, 60),
                 "A researcher looks at a chart of results, with a lightbulb."),
    "writing": (420, 300,
                blob(210, 172, 190, 112, PAL["butter"]) + book(110, 150) +
                person(330, 300, PAL["coral"], PAL["navy"], 2, reach=(270, 200), face=-1) + plant(70, 292, 0.8),
                "A person writing in an open book, beside a plant."),
    "certifications": (420, 300,
                       blob(210, 170, 188, 116, PAL["rose"]) + badge(250, 110) +
                       person(120, 300, PAL["blue"], PAL["orange"], 1, reach=(205, 120)) + plant(360, 290, 0.85),
                       "A person holds up a badge with a tick on it."),
    "about": (420, 300,
              blob(210, 172, 190, 114, PAL["mint"]) + laptop(170, 150) +
              person(110, 300, PAL["green"], PAL["navy"], 1, reach=(184, 208)) + bulb(350, 60),
              "A person working at a laptop, with an idea lightbulb."),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (w, h, body, label) in SCENES.items():
        (OUT / f"{name}.svg").write_text(svg(w, h, body, label))
    print(f"{len(SCENES)} illustrations -> {OUT}")


if __name__ == "__main__":
    main()
