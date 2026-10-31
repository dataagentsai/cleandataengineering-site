"""Problem diagrams: Physical AI, robots and autonomy; Society and trust. kit, figure, E and ROOT are injected."""


def _x(cx, cy, s=10):
    """A hand-drawn cross."""
    return (f'<line class="lnc" x1="{cx - s}" y1="{cy - s}" x2="{cx + s}" y2="{cy + s}"/>'
            f'<line class="lnc" x1="{cx + s}" y1="{cy - s}" x2="{cx - s}" y2="{cy + s}"/>')


def _tick(cx, cy):
    return f'<path class="lnc" d="M{cx - 10},{cy} L{cx - 3},{cy + 8} L{cx + 11},{cy - 9}" fill="none"/>'


def _person(cx, top):
    """A small stick person; head centre at (cx, top + 12)."""
    return (f'<circle class="hz" cx="{cx}" cy="{top + 12}" r="12"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 24}" x2="{cx}" y2="{top + 54}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 54}" x2="{cx - 10}" y2="{top + 74}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 54}" x2="{cx + 10}" y2="{top + 74}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 34}" x2="{cx - 15}" y2="{top + 46}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 34}" x2="{cx + 15}" y2="{top + 46}"/>')


def _gripper(cx, top, open_=True):
    """A two-finger robot gripper hanging from an arm; fingertips near top + 90."""
    w = 26 if open_ else 14
    return (f'<rect class="hz" x="{cx - 6}" y="{top}" width="12" height="40" rx="3"/>'
            f'<rect class="hz" x="{cx - 30}" y="{top + 40}" width="60" height="16" rx="5"/>'
            f'<path class="hz" d="M{cx - w},{top + 56} L{cx - w - 6},{top + 90} L{cx - w + 4},{top + 90} L{cx - w + 8},{top + 56} Z"/>'
            f'<path class="hz" d="M{cx + w},{top + 56} L{cx + w + 6},{top + 90} L{cx + w - 4},{top + 90} L{cx + w - 8},{top + 56} Z"/>')


def _face(cx, cy, r=34, cls="hz"):
    return (f'<circle class="{cls}" cx="{cx}" cy="{cy}" r="{r}"/>'
            f'<circle class="hk" cx="{cx - r * 0.35:.0f}" cy="{cy - r * 0.15:.0f}" r="3"/>'
            f'<circle class="hk" cx="{cx + r * 0.35:.0f}" cy="{cy - r * 0.15:.0f}" r="3"/>'
            f'<path class="ln" d="M{cx - r * 0.4:.0f},{cy + r * 0.3:.0f} Q{cx},{cy + r * 0.6:.0f} {cx + r * 0.4:.0f},{cy + r * 0.3:.0f}" fill="none"/>')


def _phone(x, y, w=34, h=56):
    return (f'<rect class="hz" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/>'
            f'<rect class="pf pf-bxs" x="{x + 5}" y="{y + 7}" width="{w - 10}" height="{h - 18}" rx="2"/>')


# ---------------------------------------------------------------- physical

def d_robot_hands():
    t = kit.text
    d = ""
    # lab: a rigid block, held
    d += '<rect class="zg" x="10" y="20" width="280" height="270" rx="14"/>'
    d += t(150, 48, "In the lab", "bd", "middle")
    d += _gripper(150, 62, open_=False)
    d += '<rect class="pf pf-bx" x="128" y="150" width="44" height="44" rx="3"/><rect class="hz" x="126" y="148" width="44" height="44" rx="3" fill="none"/>'
    d += _tick(150, 225)
    d += t(150, 268, "hard, known block: held", "sm", "middle")
    # outside: towel slips, egg cracks, new shape missed
    d += '<rect class="zr" x="310" y="20" width="680" height="270" rx="14"/>'
    d += t(650, 48, "Outside the lab", "bd", "middle")
    items = [(420, "soft towel: slips"), (650, "egg: crushed"), (880, "new shape: missed")]
    for cx, lab in items:
        d += _gripper(cx, 62)
        d += t(cx, 268, lab, "sm", "middle")
    # towel: a floppy cloth sliding out
    d += '<path class="pf pf-bxs" d="M385,165 Q405,150 425,168 Q445,186 462,170 L466,205 Q440,222 420,205 Q400,190 380,205 Z"/>'
    d += '<path class="ln" d="M385,165 Q405,150 425,168 Q445,186 462,170 L466,205 Q440,222 420,205 Q400,190 380,205 Z" fill="none"/>'
    d += '<path class="lnd" d="M470,190 Q490,210 486,236" fill="none"/>'
    # egg with a crack
    d += '<ellipse class="hz" cx="650" cy="175" rx="22" ry="29"/>'
    d += '<path class="lnc" d="M636,165 L646,178 L654,166 L664,180" fill="none"/>'
    # odd shape
    d += '<path class="hz" d="M850,185 L868,150 L890,172 L912,148 L908,205 L862,210 Z"/>'
    d += t(880, 238, "?", "bd", "middle")
    # touch sense callout
    d += t(540, 112, ["the fingers feel", "almost nothing"], "sm", "middle")
    d += kit.path("M590,108 Q612,104 624,118", "lnd")
    return figure(1000, 305, d,
                  "Left, in the lab: a robot gripper holds a hard, known block. Right, outside the lab: the same gripper lets a soft towel slip, cracks an egg, and misses a new odd shape, because its fingers feel almost nothing.",
                  "A robot hand that works on lab blocks fails on soft, fragile or unfamiliar things, because touch sensing and fine control are weak.")


def d_robot_data():
    t = kit.text
    d = ""
    # web text: a tall stack of pages
    for i in range(12):
        y = 230 - i * 15
        d += f'<rect class="hz" x="{70 + (i % 3) * 4}" y="{y}" width="200" height="28" rx="3"/>'
        d += f'<line class="ln" x1="{84 + (i % 3) * 4}" y1="{y + 14}" x2="{250 + (i % 3) * 4}" y2="{y + 14}"/>'
    d += t(170, 290, "the web: trillions of words", "bd", "middle")
    # robot recordings: three small reels, each a different plug
    d += t(680, 46, "recorded robot actions: very few", "bd", "middle")
    reels = [(520, "lab A", "circle"), (680, "lab B", "square"), (840, "lab C", "tri")]
    for cx, lab, shape in reels:
        d += f'<circle class="hz" cx="{cx}" cy="150" r="40"/><circle class="hz" cx="{cx}" cy="150" r="10"/>'
        for dx, dy in ((0, -24), (21, 12), (-21, 12)):
            d += f'<circle class="pf pf-bx" cx="{cx + dx}" cy="{150 + dy}" r="7"/>'
        d += f'<line class="ln" x1="{cx}" y1="190" x2="{cx}" y2="214"/>'
        if shape == "circle":
            d += f'<circle class="bxs ol" cx="{cx}" cy="226" r="12"/>'
        elif shape == "square":
            d += f'<rect class="bxs ol" x="{cx - 12}" y="214" width="24" height="24" rx="2"/>'
        else:
            d += f'<path class="bxs ol" d="M{cx},212 L{cx + 14},238 L{cx - 14},238 Z"/>'
        d += t(cx, 262, lab, "sm", "middle")
    d += t(680, 290, "and every lab uses its own format", "sm", "middle")
    d += t(400, 160, "vs", "bd", "middle")
    return figure(1000, 305, d,
                  "Left: a tall stack of pages, the web's trillions of words. Right: just three small reels of recorded robot actions from labs A, B and C, each ending in a different-shaped plug, so they do not fit together.",
                  "Language models learned from trillions of words, but robots have only a few recorded actions to learn from, in formats that do not match.")


def d_sim_real():
    t = kit.text
    d = ""
    # simulation panel
    d += '<rect class="pf pf-bx" x="14" y="24" width="400" height="230" rx="14"/><rect class="bx ol" x="10" y="20" width="400" height="230" rx="14"/>'
    d += t(210, 50, "In simulation", "bd", "middle")
    for i in range(6):
        d += f'<line class="lnd" x1="{40 + i * 66}" y1="200" x2="{60 + i * 66}" y2="235"/>'
    d += '<line class="ln" x1="30" y1="200" x2="390" y2="200"/>'
    d += _gripper(210, 70, open_=False)
    d += '<rect class="hz" x="190" y="158" width="40" height="40" rx="2"/>'
    d += _tick(300, 140)
    d += t(320, 100, ["even light,", "exact friction"], "sm")
    # arrow
    d += kit.arrow(418, 135, 568, 135, "the same policy", ly=122)
    # reality panel
    d += '<rect class="zr" x="575" y="20" width="415" height="230" rx="14"/>'
    d += t(782, 50, "In the real world", "bd", "middle")
    d += '<line class="ln" x1="595" y1="200" x2="970" y2="200"/>'
    # sun glare
    d += '<circle class="pf pf-bxs" cx="930" cy="88" r="18"/><circle class="hz" cx="930" cy="88" r="18" fill="none"/>'
    for dx, dy in ((-30, 0), (30, 0), (0, -28), (-22, 20), (22, 20), (-22, -20)):
        d += f'<line class="ln" x1="{930 + dx * 0.8:.0f}" y1="{88 + dy * 0.8:.0f}" x2="{930 + dx * 1.2:.0f}" y2="{88 + dy * 1.2:.0f}"/>'
    d += _gripper(760, 70)
    # dropped cube, tilted on the floor, with a slip mark
    d += '<rect class="hz" x="800" y="162" width="36" height="36" rx="2" transform="rotate(18 818 180)"/>'
    d += '<path class="lnd" d="M770,170 Q790,150 800,165" fill="none"/>'
    d += _x(700, 140)
    d += t(782, 272, "slippery surface, glare, worn fingers", "sm", "middle")
    d += t(210, 272, "trained here", "sm", "middle")
    return figure(1000, 290, d,
                  "Left: in simulation, with even light and exact friction, a robot gripper holds a cube. The same policy is moved to the right, the real world, where glare, a slippery surface and worn fingers make it drop the cube.",
                  "A robot that learned in a perfect simulator meets real friction, light and wear, and fails.")


def d_av_safe():
    t = kit.text
    import random
    rnd = random.Random(7)
    d = ""
    # the space of all situations: a big cloud of dots
    d += '<ellipse class="pf pf-bx" cx="330" cy="160" rx="300" ry="125"/><ellipse class="ln" cx="330" cy="160" rx="300" ry="125" fill="none"/>'
    d += t(330, 22, "every situation the robot could meet", "bd", "middle")
    pts = []
    while len(pts) < 70:
        x, y = rnd.uniform(60, 600), rnd.uniform(55, 265)
        if ((x - 330) / 285) ** 2 + ((y - 160) / 112) ** 2 < 1:
            pts.append((x, y))
    for x, y in pts:
        d += f'<circle class="hk" cx="{x:.0f}" cy="{y:.0f}" r="3"/>'
    # tested area
    d += '<ellipse class="zg" cx="250" cy="165" rx="120" ry="70" style="opacity:.75"/>'
    d += t(250, 170, "the scenarios you tested", "sm", "middle")
    # rare failures, outside the tested patch
    for x, y in ((520, 100), (560, 210), (440, 250)):
        d += f'<circle class="zr" cx="{x}" cy="{y}" r="11"/><circle class="hk" cx="{x}" cy="{y}" r="3"/>'
    d += t(700, 160, ["red: rare failures", "nobody tested"], "sm")
    d += kit.path("M695,150 Q620,110 536,102", "lnd")
    # right side: miles needed vs driven
    d += kit.box(780, 40, 205, 95, "Drive it?", ["far too many miles", "to prove it safe"], "bxs")
    d += kit.box(780, 165, 205, 95, "Test scenarios?", ["nobody agrees which", "ones are enough"], "bxm")
    return figure(1000, 300, d,
                  "A large cloud of dots shows every situation a robot could meet. A green patch inside it marks the scenarios that were tested. Three red dots, rare failures, sit outside the patch. Beside it: driving enough miles to prove safety is impossible, and nobody agrees which scenarios are enough.",
                  "You cannot drive enough miles to prove a machine safe, and nobody agrees which test scenarios cover the rare failures that matter.")


def d_no_gps():
    t = kit.text
    d = ""
    # satellite crossed out
    d += '<rect class="hz" x="60" y="30" width="34" height="24" rx="3"/>'
    d += '<rect class="pf pf-bx" x="20" y="34" width="34" height="16"/><rect class="pf pf-bx" x="100" y="34" width="34" height="16"/>'
    d += '<rect class="ln" x="20" y="34" width="34" height="16" fill="none"/><rect class="ln" x="100" y="34" width="34" height="16" fill="none"/>'
    d += _x(77, 42, 22)
    d += t(150, 48, "GPS jammed or blocked", "sm")
    # tunnel roof and floor
    d += '<path class="lnc" d="M20,100 Q500,80 980,100" fill="none"/><path class="lnc" d="M20,290 Q500,305 980,290" fill="none"/>'
    d += t(330, 48, "indoors, underground", "sm")
    # true path (solid) vs believed path (dashed, drifting)
    d += '<path class="ln" d="M90,200 L900,200" fill="none"/>'
    d += kit.path("M90,200 Q400,196 600,174 Q760,156 900,142", "lnd")
    # drone at start
    d += ('<rect class="hz" x="60" y="190" width="40" height="18" rx="5"/>'
          '<line class="ln" x1="50" y1="186" x2="110" y2="186"/>'
          '<ellipse class="hz" cx="50" cy="184" rx="14" ry="4"/><ellipse class="hz" cx="110" cy="184" rx="14" ry="4"/>')
    # growing uncertainty circles at minute marks
    for x, yb, r, m in ((330, 192, 14, "minute 1"), (600, 172, 26, "minute 2"), (900, 142, 32, "minute 3")):
        d += f'<circle class="zy" cx="{x}" cy="{yb}" r="{r}" style="opacity:.6"/>'
        d += f'<circle class="hk" cx="{x}" cy="200" r="4"/>'
        d += t(x, 238, m, "sm", "middle")
    d += t(330, 272, "solid: where it really is", "sm", "middle")
    d += t(640, 272, "dashed: where it thinks it is", "sm", "middle")
    d += '<line class="ln" x1="950" y1="196" x2="950" y2="146" marker-end="url(#ar)"/>' + t(958, 128, "drift", "bd", "middle")
    return figure(1000, 310, d,
                  "A drone flies along a tunnel with GPS crossed out. Its true path is a straight solid line; the path it believes it is on, dashed, curves away, and the yellow circle of uncertainty grows at minute 1, 2 and 3.",
                  "Without GPS, a drone or robot guesses its position from its own motion, and the small errors add up to real drift within minutes.")


def d_batteries():
    t = kit.text
    d = ""
    # humanoid robot
    d += ('<rect class="hz" x="62" y="40" width="56" height="44" rx="10"/>'
          '<circle class="hk" cx="80" cy="60" r="4"/><circle class="hk" cx="100" cy="60" r="4"/>'
          '<rect class="hz" x="50" y="92" width="80" height="90" rx="10"/>'
          '<line class="lnc" x1="50" y1="105" x2="25" y2="160"/><line class="lnc" x1="130" y1="105" x2="155" y2="160"/>'
          '<line class="lnc" x1="72" y1="182" x2="68" y2="240"/><line class="lnc" x1="108" y1="182" x2="112" y2="240"/>')
    # battery on its chest, almost empty
    d += ('<rect class="hz" x="66" y="112" width="48" height="26" rx="4"/><rect class="hk" x="114" y="119" width="5" height="12"/>'
          '<rect class="zr" x="70" y="116" width="9" height="18"/>')
    d += t(90, 266, "a humanoid or drone", "sm", "middle")
    # timeline of a work shift
    x0, x1 = 230, 950
    hr = (x1 - x0) / 8
    d += t(590, 40, "a work shift, say 8 hours", "bd", "middle")
    d += f'<rect class="hz" x="{x0}" y="70" width="{x1 - x0}" height="50" rx="10"/>'
    d += f'<rect class="zg" x="{x0 + 4}" y="74" width="{2 * hr - 4:.0f}" height="42" rx="8"/>'
    d += t(x0 + hr, 100, "runs 1–2 hours", "sm", "middle")
    d += f'<rect class="hatch" x="{x0 + 2 * hr:.0f}" y="74" width="{6 * hr - 4:.0f}" height="42" rx="8"/>'
    d += t(x0 + 5 * hr, 100, "flat, on the charger", "bd", "middle")
    for h in range(9):
        d += f'<line class="ln" x1="{x0 + h * hr:.0f}" y1="124" x2="{x0 + h * hr:.0f}" y2="134"/>'
        d += t(x0 + h * hr, 152, f"{h}h", "sm", "middle")
    # slow improvement: a nearly flat line
    d += '<line class="ln" x1="300" y1="250" x2="900" y2="250"/><line class="ln" x1="300" y1="250" x2="300" y2="180"/>'
    d += kit.path("M300,236 Q600,230 890,220", "lnc")
    d += t(310, 194, "energy per kilogram", "sm")
    d += t(900, 272, "years", "sm", "end")
    d += t(640, 208, "only a few percent better a year", "sm", "middle")
    return figure(1000, 290, d,
                  "A humanoid robot with a nearly empty battery on its chest. Beside it, an 8-hour work shift, given as an example: the robot runs for the first 1 to 2 hours and is flat on the charger for the rest. Below, energy per kilogram rises only slowly, a few percent a year.",
                  "Humanoids and drones run for only 1–2 hours, and battery energy per kilogram improves only a few percent a year.")


# ---------------------------------------------------------------- society

def d_deepfakes():
    t = kit.text
    d = ""
    gens = [(110, "old generator 1", True), (330, "old generator 2", True), (790, "newest generator", False)]
    for cx, lab, caught in gens:
        cls = "pf pf-bx" if caught else "pf pf-solid"
        d += _face(cx, 90, 40, cls)
        d += f'<circle class="ln" cx="{cx}" cy="90" r="40" fill="none"/>'
        d += t(cx, 160, lab, "sm", "middle")
    # glitch marks on old fakes
    for cx in (110, 330):
        d += f'<path class="lnd" d="M{cx + 18},{62} L{cx + 32},{74} L{cx + 22},{82}" fill="none"/>'
    # detector magnifier
    d += '<circle class="hz" cx="560" cy="80" r="40"/><circle class="pf pf-bxs" cx="560" cy="80" r="32"/>'
    d += '<line class="lnc" x1="588" y1="108" x2="620" y2="142"/>'
    d += t(560, 86, "detector", "bd", "middle")
    d += t(560, 160, "trained on old fakes", "sm", "middle")
    # verdict row
    d += '<rect class="zg" x="20" y="190" width="420" height="70" rx="12"/>'
    d += t(230, 220, "caught: it learned their tell-tale marks", "sm", "middle")
    d += _tick(230, 240)
    d += '<rect class="zr" x="620" y="190" width="360" height="70" rx="12"/>'
    d += t(800, 220, "passes as real: new marks, unseen", "sm", "middle")
    d += _x(800, 242, 9)
    d += kit.arrow(745, 90, 610, 85)
    d += kit.arrow(375, 90, 512, 85)
    return figure(1000, 275, d,
                  "Faces from two old generators carry small tell-tale marks, and a detector trained on them catches them. A face from the newest generator has different marks, and the same detector passes it as real.",
                  "A deepfake detector learns the marks of the generators it has seen, so every new generator slips past it.")


def d_provenance():
    b, a, t = kit.box, kit.arrow, kit.text
    d = ""
    # original photo with mark and signature seal
    d += '<rect class="hz" x="20" y="60" width="150" height="110" rx="6"/>'
    d += '<path class="pf pf-bx" d="M28,160 L70,110 L100,140 L125,118 L162,160 Z"/>'
    d += '<circle class="pf pf-bxs" cx="135" cy="85" r="10"/>'
    d += '<circle class="solid ol" cx="160" cy="62" r="18"/>'
    d += t(160, 67, "✓", "bd", "middle")
    d += t(95, 200, ["the original:", "watermark + signature"], "sm", "middle")
    # three edits
    edits = [("crop", 260), ("re-encode", 470), ("screenshot", 680)]
    prev = 172
    for i, (name, x) in enumerate(edits):
        d += a(prev, 115, x - 4, 115)
        d += b(x, 75, 150, 80, name, "", "bxs")
        prev = x + 152
    d += a(prev, 115, 866, 115)
    # stripped copy
    d += '<rect class="hz" x="868" y="60" width="120" height="110" rx="6"/>'
    d += '<path class="pf pf-bx" d="M874,160 L905,118 L930,142 L950,124 L982,160 Z"/>'
    d += t(928, 100, "?", "bd", "middle")
    d += t(928, 200, ["a copy with", "no mark left"], "sm", "middle")
    # the mark fading along the way
    d += t(500, 40, "each edit can wipe the mark, and most apps drop the signature", "sm", "middle")
    for i, x in enumerate((335, 545, 755)):
        op = (0.7, 0.4, 0.15)[i]
        d += f'<circle class="solid ol" cx="{x + 75}" cy="58" r="11" style="opacity:{op}"/>'
    d += t(500, 250, "where did this picture come from?  nobody can tell", "bd", "middle")
    return figure(1000, 270, d,
                  "An original picture carries a watermark and a signature seal. It goes through a crop, a re-encode and a screenshot, the seal fading at each step, and comes out as a copy with no mark left, so nobody can tell where it came from.",
                  "Ordinary edits strip watermarks, and signed content is rarely carried end to end, so the origin of a picture is lost.")


def d_tutor():
    t = kit.text
    d = ""
    # student and tutor
    d += _person(70, 60)
    d += t(70, 160, "student", "sm", "middle")
    d += ('<rect class="hz" x="180" y="60" width="74" height="62" rx="10"/>'
          '<rect class="pf pf-solid" x="188" y="70" width="58" height="34" rx="4"/>'
          '<circle class="hk" cx="205" cy="86" r="3"/><circle class="hk" cx="229" cy="86" r="3"/>'
          '<rect class="hz" x="200" y="122" width="34" height="10" rx="3"/>')
    d += t(217, 160, "AI tutor", "sm", "middle")
    d += kit.arrow(92, 92, 176, 92)
    d += t(130, 50, "help?", "sm", "middle")
    # speech bubble: gives the answer
    d += '<path class="hz" d="M262,40 L430,40 Q440,40 440,50 L440,90 Q440,100 430,100 L290,100 L272,116 L276,100 L272,100 Q262,100 262,90 Z"/>'
    d += t(351, 76, "\"the answer is 42\"", "sm", "middle")
    # two gauges: feels helpful vs test score
    d += kit.box(500, 30, 220, 110, "Feels helpful", ["homework done,", "student happy"], "bx")
    d += kit.box(760, 30, 220, 110, "Test without it", ["gain: rarely", "shown in trials"], "bxm")
    d += kit.arrow(722, 85, 756, 85)
    # bars
    d += '<line class="ln" x1="530" y1="270" x2="950" y2="270"/>'
    d += '<rect class="zg" x="560" y="185" width="80" height="85" rx="4"/>'
    d += '<rect class="zy" x="820" y="250" width="80" height="20" rx="4"/>'
    d += t(600, 178, "how it feels", "sm", "middle")
    d += t(860, 240, "measured gain", "sm", "middle")
    d += t(250, 220, ["some students learn", "to lean on it instead"], "sm", "middle")
    d += kit.path("M250,190 Q245,180 238,170", "lnd")
    return figure(1000, 285, d,
                  "A student asks an AI tutor for help and it gives the answer. That feels helpful: homework done, student happy. But on a test without the tutor, a real gain is rarely shown in trials. A tall bar for how it feels stands beside a short bar for the measured gain.",
                  "Many AI tutors feel helpful, but few show test-score gains in controlled trials, and some teach students to lean on them.")


def d_fact_check():
    t = kit.text
    d = ""
    # time axis
    d += '<line class="lnc" x1="40" y1="250" x2="960" y2="250"/>'
    for x, lab in ((60, "0"), (250, "minutes"), (600, "hours"), (900, "days")):
        d += f'<line class="ln" x1="{x}" y1="244" x2="{x}" y2="258"/>' + t(x, 278, lab, "sm", "middle")
    # the rumour fans out fast
    d += _phone(42, 110)
    d += t(60, 96, "a false claim", "sm", "middle")
    fan = [(170, 40), (170, 130), (170, 190), (270, 20), (270, 80), (270, 140), (270, 190)]
    for x, y in fan:
        d += f'<line class="lnd" x1="78" y1="138" x2="{x}" y2="{y + 18}"/>' if x == 170 else ""
    for x, y in fan:
        if x == 270:
            src = min((p for p in fan if p[0] == 170), key=lambda p: abs(p[1] - y))
            d += f'<line class="lnd" x1="{src[0] + 26}" y1="{src[1] + 18}" x2="{x}" y2="{y + 18}"/>'
    for x, y in fan:
        d += _phone(x, y, 26, 40)
        d += f'<circle class="zr" cx="{x + 13}" cy="{y + 18}" r="5"/>'
    d += t(310, 226, "many have seen it", "sm")
    # gap
    d += '<rect class="zy" x="330" y="90" width="430" height="80" rx="12" style="opacity:.6"/>'
    d += t(545, 125, "the gap: the rumour spreads unchecked", "bd", "middle")
    d += t(545, 150, "spreads in minutes, checks take hours or days", "sm", "middle")
    # fact-checker arrives late
    d += _person(860, 70)
    d += '<rect class="hz" x="885" y="105" width="50" height="40" rx="4"/>'
    d += _tick(910, 122)
    d += t(880, 175, "the fact-check", "sm", "middle")
    d += t(880, 196, "arrives", "sm", "middle")
    d += kit.path("M880,205 Q890,228 900,244", "lnd")
    return figure(1000, 290, d,
                  "On a timeline, one phone with a false claim spreads it to many phones within minutes. A wide yellow gap follows. A fact-checker with a ticked report arrives only after hours or days.",
                  "False claims spread in minutes, and fact-checks take hours or days, so many people see the rumour long before the correction.")


DRAWINGS = {
    "robot-hands-that-cope-with-new-objects": d_robot_hands,
    "too-little-robot-training-data": d_robot_data,
    "the-gap-between-simulation-and-reality": d_sim_real,
    "proving-an-autonomous-system-is-safe": d_av_safe,
    "flying-and-moving-without-gps": d_no_gps,
    "batteries-limit-every-robot": d_batteries,
    "spotting-deepfakes": d_deepfakes,
    "proving-where-content-came-from": d_provenance,
    "an-ai-tutor-that-measurably-raises-learning": d_tutor,
    "fact-checking-at-the-speed-of-rumour": d_fact_check,
}
