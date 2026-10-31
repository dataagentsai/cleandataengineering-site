"""Diagrams for the 'Science and maths' problems.
kit, figure, E and ROOT are given as globals by build.py."""


def _person(cx, top):
    """A small stick person whose head centre is at (cx, top)."""
    return (f'<circle class="hz" cx="{cx}" cy="{top}" r="14"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 14}" x2="{cx}" y2="{top + 52}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 52}" x2="{cx - 12}" y2="{top + 76}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 52}" x2="{cx + 12}" y2="{top + 76}"/>')


def _tick(x, y, s=1.0):
    return f'<path class="lnc" fill="none" d="M{x},{y} L{x + 8 * s},{y + 9 * s} L{x + 24 * s},{y - 12 * s}"/>'


def _cross(x, y, r=11):
    return (f'<line class="lnc" x1="{x - r}" y1="{y - r}" x2="{x + r}" y2="{y + r}"/>'
            f'<line class="lnc" x1="{x + r}" y1="{y - r}" x2="{x - r}" y2="{y + r}"/>')


# ---------------------------------------------------------------- 1. maths into Lean

def d_lean():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(150, 28, "WRITTEN MATHS", "lbl", "middle")
    # a tall pile of proof papers
    for i in range(7):
        x, y = 60 + (i % 2) * 8, 200 - i * 20
        d += f'<rect class="hz" x="{x}" y="{y}" width="170" height="30" rx="3" transform="rotate({(-3, 2, -1, 3, -2, 1, -4)[i]} {x + 85} {y + 15})"/>'
    d += t(150, 101, "proof: let x be ...", "sm", "middle")
    d += t(150, 268, ["piles of proofs,", "easy for people to read"], "sm", "middle")
    # the slow translation pipe
    d += t(480, 28, "TRANSLATE INTO LEAN BY HAND", "lbl", "middle")
    d += '<path class="hz" d="M280,110 L400,140 L560,140 L680,110 L680,190 L560,160 L400,160 L280,190 Z"/>'
    # a snail in the narrow neck
    d += ('<g transform="translate(480 150) scale(1.6) translate(-480 -150)"><circle class="pf pf-bxs" cx="480" cy="142" r="13"/><circle class="hz" cx="480" cy="142" r="13" fill="none"/>'
          '<path class="ln" fill="none" d="M480,142 m-6,0 a6,6 0 1,1 6,6"/>'
          '<path class="ln" fill="none" d="M462,155 L502,155 Q508,155 506,147"/>'
          '<line class="ln" x1="503" y1="148" x2="508" y2="138"/><line class="ln" x1="506" y1="149" x2="514" y2="141"/></g>')
    d += t(480, 222, ["slow, careful work", "line by line"], "sm", "middle")
    d += a(250, 150, 276, 150)
    d += a(684, 150, 722, 150)
    # the checker
    d += b(725, 60, 250, 120, "Lean checker", ["a machine checks", "every step"], "solid")
    d += _tick(752, 214, 1.0) + t(790, 220, "checked: only a few", "sm")
    return figure(1000, 290, d,
                  "A tall pile of written proofs on the left feeds into a pipe that narrows to a thin neck, where a snail crawls: translating into Lean by hand is slow, careful work. On the right a Lean checker box checks every step, but only a few proofs come out checked.",
                  "Written maths is easy for people to read, but turning it into a proof language like Lean is slow, so few results are ever checked by a machine.")


# ---------------------------------------------------------------- 2. weather beyond two weeks

def _sun(cx, cy):
    rays = "".join(f'<line class="ln" x1="{cx + 17 * c}" y1="{cy + 17 * s}" x2="{cx + 25 * c}" y2="{cy + 25 * s}"/>'
                   for c, s in ((1, 0), (-1, 0), (0, 1), (0, -1), (.7, .7), (-.7, .7), (.7, -.7), (-.7, -.7)))
    return f'<circle class="pf pf-bxs" cx="{cx}" cy="{cy}" r="12"/><circle class="hz" cx="{cx}" cy="{cy}" r="12" fill="none"/>' + rays


def _cloud(cx, cy):
    return (f'<path class="hz" d="M{cx - 30},{cy + 10} Q{cx - 38},{cy - 6} {cx - 18},{cy - 8} Q{cx - 12},{cy - 26} {cx + 6},{cy - 16} '
            f'Q{cx + 26},{cy - 22} {cx + 28},{cy - 4} Q{cx + 40},{cy + 2} {cx + 30},{cy + 10} Z"/>')


def d_weather():
    t = kit.text
    x0, x2, x4, y = 80, 520, 960, 180   # today, 2 weeks, 4 weeks; the centre line
    d = f'<rect class="zg" x="{x0}" y="40" width="{x2 - 140 - x0}" height="240" rx="8"/>'
    d += f'<rect class="zy" x="{x2 - 140}" y="40" width="200" height="240" rx="8"/>'
    d += f'<rect class="zr" x="{x2 + 60}" y="40" width="{x4 - x2 - 60}" height="240" rx="8"/>'
    # a fan of forecast lines that spreads out
    for k in (-1, -0.6, -0.25, 0.1, 0.45, 0.8, 1.1):
        d += (f'<path class="ln" fill="none" d="M{x0},{y} C{x0 + 220},{y + 4 * k} {x2 - 120},{y + 25 * k} {x2 + 40},{y + 45 * k} '
              f'S{x4 - 120},{y + 60 * k} {x4 - 10},{y + 68 * k}"/>')
    d += _sun(150, 245) + _cloud(260, 248)
    d += t(230, 68, ["a few days: AI models", "beat physics models"], "sm", "middle")
    d += t(x2 - 40, 66, "skill fades", "bd", "middle")
    d += t(x2 + 340, 80, "?", "bd", "middle")
    d += t(x2 + 260, 68, ["seasonal forecasts:", "still weak"], "sm", "middle")
    # time axis
    d += f'<line class="lnc" x1="{x0}" y1="305" x2="{x4}" y2="305" marker-end="url(#ar)"/>'
    for x, lab in ((x0, "today"), (x2 - 40, "about 2 weeks"), (x4 - 40, "a month and more")):
        d += f'<line class="ln" x1="{x}" y1="298" x2="{x}" y2="312"/>' + t(x, 334, lab, "sm", "middle")
    return figure(1000, 350, d,
                  "Forecast lines start together today and spread out into a widening fan. In the first days, a green zone with a sun and a cloud: AI models beat physics models. Around two weeks, a yellow zone: skill fades. Beyond that, a red zone with a question mark: seasonal forecasts are still weak.",
                  "AI weather models win for days ahead, but every forecast spreads apart and its skill fades after about two weeks.")


# ---------------------------------------------------------------- 3. protein function and binding

def d_protein():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(120, 30, "SEQUENCE", "lbl", "middle")
    # a straight string of beads
    for i in range(9):
        cls = "pf pf-bx" if i % 3 else "pf pf-bxs"
        d += f'<circle class="{cls}" cx="{30 + i * 22}" cy="140" r="10"/><circle class="hz" cx="{30 + i * 22}" cy="140" r="10" fill="none"/>'
    d += t(120, 180, "a chain of amino acids", "sm", "middle")
    d += a(232, 140, 290, 140)
    d += t(261, 112, "fold", "sm", "middle")
    # the folded shape
    d += t(380, 30, "STRUCTURE", "lbl", "middle")
    d += ('<path class="hz" d="M310,140 C300,80 360,70 380,100 C400,60 460,90 440,130 C470,150 440,210 400,190 '
          'C380,220 320,210 330,175 C300,170 300,150 310,140 Z"/>'
          '<path class="ln" fill="none" d="M335,140 C350,110 370,150 390,120 C410,95 425,140 405,160 C385,180 360,160 345,180"/>')
    d += _tick(350, 232, 0.9) + t(380, 238, "largely solved", "sm")
    # what is still open
    d += t(760, 30, "STILL OPEN", "lbl", "middle")
    rows = [("What does it do?", "its job in the cell"), ("What does it bind to?", "which molecules fit"),
            ("Will a design work?", "in a real lab")]
    for i, (title, sub) in enumerate(rows):
        y = 48 + i * 82
        d += b(620, y, 280, 68, title, sub, "bxm")
        d += t(925, y + 46, "?", "bd", "middle")
        d += a(462, 140, 616, y + 34)
    return figure(1000, 300, d,
                  "A straight chain of beads, the sequence, folds into a 3D shape, the structure, with a tick: largely solved. From the shape, three arrows lead to dashed boxes with question marks: what does it do, what does it bind to, and will a design work in a real lab.",
                  "Predicting a protein's shape is largely solved; predicting what it does, what it binds to, and which designs work in a lab is not.")


# ---------------------------------------------------------------- 4. drug toxicity

def _pill(cx, cy):
    return (f'<g transform="rotate(-25 {cx} {cy})"><rect class="hz" x="{cx - 26}" y="{cy - 11}" width="52" height="22" rx="11"/>'
            f'<path class="pf pf-bxs" d="M{cx},{cy - 10} L{cx + 15},{cy - 10} A10,10 0 0,1 {cx + 15},{cy + 10} L{cx},{cy + 10} Z"/>'
            f'<line class="ln" x1="{cx}" y1="{cy - 11}" x2="{cx}" y2="{cy + 11}"/></g>')


def d_tox():
    b, a, t = kit.box, kit.arrow, kit.text
    d = _pill(70, 110) + t(70, 160, "a new drug", "sm", "middle")
    d += a(108, 110, 160, 110)
    d += b(162, 60, 220, 100, "Early tests", ["cells, quick screens:", "looks safe"], "bx")
    # magnifier that misses a hidden spot
    d += ('<circle class="hz" cx="250" cy="215" r="22"/><line class="lnc" x1="266" y1="231" x2="286" y2="251"/>'
          '<circle class="hk" cx="318" cy="222" r="5"/>')
    d += t(332, 252, "a hidden side effect it misses", "sm")
    d += _tick(392, 62, 0.8)
    d += a(384, 110, 450, 110)
    d += b(452, 60, 220, 100, "Years of trials", ["more tests,", "then people"], "bx")
    d += a(674, 110, 740, 110)
    d += b(742, 60, 240, 100, "The side effect shows", ["the drug fails late"], "bxs")
    d += _cross(950, 196)
    # cost grows along the way
    d += '<path class="pf pf-bxs" d="M170,300 L970,280 L970,320 L170,302 Z"/>'
    d += '<path class="ln" fill="none" d="M170,300 L970,280 L970,320 L170,302 Z"/>'
    d += t(560, 338, "money and time spent keep growing, so failing late is the most costly way to fail", "sm", "middle")
    return figure(1000, 350, d,
                  "A new drug passes early tests, which look safe, while a magnifying glass misses a small hidden side effect. After years of trials the side effect shows and the drug fails late. Underneath, a wedge shows money and time spent growing all the way along.",
                  "Most drug candidates fail late, after years of work, because early tests miss the side effects.")


# ---------------------------------------------------------------- 5. battery and material candidates

def d_materials():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(130, 28, "MILLIONS OF POSSIBLE MATERIALS", "lbl", "middle")
    for r in range(8):
        for c in range(11):
            x, y = 26 + c * 20 + (r % 2) * 8, 52 + r * 20
            d += f'<circle class="hz" cx="{x}" cy="{y}" r="5"/>'
    d += t(130, 230, "too many to test them all", "sm", "middle")
    d += a(252, 120, 300, 120)
    d += b(302, 70, 210, 100, "A model predicts", ["\"this one stores", "lots of charge\""], "solid")
    d += a(514, 100, 590, 70)
    d += b(592, 30, 200, 70, "The property", "predicted well", "bx")
    d += _tick(812, 66, 0.9)
    d += a(514, 140, 590, 170)
    d += b(592, 135, 200, 80, "Can it be made?", ["the model", "can't say"], "bxm")
    d += t(808, 182, "?", "bd", "middle")
    # the slow lab: a flask with a queue
    d += ('<path class="hz" d="M880,250 L880,272 L856,312 Q852,320 862,320 L918,320 Q928,320 924,312 L900,272 L900,250 Z"/>'
          '<path class="pf pf-bxs" d="M866,300 L914,300 L922,314 L858,314 Z"/>')
    for i in range(4):
        d += f'<circle class="hz" cx="{620 + i * 50}" cy="290" r="8"/>'
    d += a(812, 290, 848, 290)
    d += t(690, 330, "the lab tests them one at a time, slowly", "sm", "middle")
    d += kit.path("M692,217 Q680,250 650,276", "lnd")
    return figure(1000, 345, d,
                  "A field of tiny dots stands for millions of possible materials. A model picks one and predicts it stores lots of charge: the property is predicted well, with a tick. But a dashed box asks whether it can be made, and the model can't say. Candidates queue up for a flask: the lab tests them one at a time, slowly.",
                  "Models can predict how a new material would behave, but not whether it can be made, and the lab can only test a few.")


# ---------------------------------------------------------------- 6. deep theory

def _padlock(cx, cy, label):
    return (f'<path class="ln" fill="none" d="M{cx - 11},{cy} L{cx - 11},{cy - 12} A11,11 0 0,1 {cx + 11},{cy - 12} L{cx + 11},{cy}"/>'
            f'<rect class="pf pf-bxs" x="{cx - 18}" y="{cy}" width="36" height="28" rx="4"/>'
            f'<rect class="hz" x="{cx - 18}" y="{cy}" width="36" height="28" rx="4" fill="none"/>'
            + kit.text(cx + 30, cy + 20, label, "sm", "start"))


def d_theory():
    b, a, t = kit.box, kit.arrow, kit.text
    # the big locked door
    d = '<rect class="hz" x="400" y="30" width="240" height="270" rx="10"/>'
    d += t(520, 56, "OPEN FOR DECADES", "lbl", "middle")
    d += _padlock(440, 86, "P vs NP")
    d += _padlock(440, 150, "Riemann hypothesis")
    d += _padlock(440, 214, "unifying physics")
    # computers pushing, and bouncing off
    for i in range(3):
        x = 40 + i * 70
        d += f'<rect class="hz" x="{x}" y="150" width="56" height="120" rx="4"/>'
        d += "".join(f'<line class="ln" x1="{x + 10}" y1="{168 + j * 22}" x2="{x + 46}" y2="{168 + j * 22}"/>' for j in range(5))
    d += t(130, 296, "more and more computing", "sm", "middle")
    d += a(260, 200, 392, 200)
    d += kit.path("M392,214 Q330,250 268,236", "lnd")
    d += t(330, 180, "push", "sm", "middle")
    d += t(330, 268, "no luck", "sm", "middle")
    # the missing key
    d += _person(730, 120)
    d += ('<circle class="hz" cx="810" cy="130" r="24" stroke-dasharray="6 5"/>'
          '<path class="lnd" fill="none" d="M834,130 L950,130 M920,130 L920,152 M942,130 L942,148"/>')
    d += t(880, 100, "missing", "sm", "middle")
    d += b(700, 220, 280, 80, "The key: new mathematics", "nobody has found it yet", "bxm")
    return figure(1000, 320, d,
                  "A tall door with three padlocks: P vs NP, the Riemann hypothesis and unifying physics, open for decades. On the left, a row of computers pushes at the door and bounces off. On the right, a stick person looks at a dashed outline of a key: new mathematics, which nobody has found yet.",
                  "These problems are locked doors; more computing doesn't open them, only new mathematics will.")


# ---------------------------------------------------------------- 7. ageing and fusion

def d_ageing_fusion():
    b, a, t = kit.box, kit.arrow, kit.text
    # a person with a laptop, outside
    d = _person(70, 110)
    d += ('<rect class="hz" x="96" y="160" width="56" height="34" rx="3"/>'
          '<path class="hz" d="M90,194 L158,194 L164,204 L84,204 Z"/>')
    d += t(100, 240, ["one person,", "one laptop"], "sm", "middle")
    # a fence
    d += "".join(f'<line class="lnc" x1="{215 + i * 14}" y1="60" x2="{215 + i * 14}" y2="230"/>' for i in range(5))
    d += '<line class="lnc" x1="205" y1="100" x2="285" y2="100"/><line class="lnc" x1="205" y1="190" x2="285" y2="190"/>'
    d += kit.path("M160,140 Q180,120 198,132", "lnd")
    # ageing: a lab
    d += b(320, 40, 300, 90, "Ageing", ["needs labs, living cells", "and long studies"], "bx")
    d += ('<path class="hz" d="M462,150 L462,168 L442,200 Q440,206 448,206 L492,206 Q500,206 498,200 L478,168 L478,150 Z"/>'
          '<path class="pf pf-bxs" d="M450,190 L490,190 L496,202 L444,202 Z"/>')
    # fusion: a reactor
    d += b(655, 40, 320, 90, "Fusion", ["needs reactors,", "huge machines"], "solid")
    d += ('<ellipse class="hz" cx="815" cy="182" rx="60" ry="22"/><ellipse class="pf pf-bxs" cx="815" cy="182" rx="26" ry="8"/>'
          '<ellipse class="ln" fill="none" cx="815" cy="182" rx="26" ry="8"/>')
    # decades
    d += '<line class="lnc" x1="320" y1="262" x2="970" y2="262" marker-end="url(#ar)"/>'
    for i in range(6):
        d += f'<line class="ln" x1="{340 + i * 110}" y1="255" x2="{340 + i * 110}" y2="269"/>'
    d += t(645, 292, "decades of work, for both", "sm", "middle")
    return figure(1000, 305, d,
                  "A stick person with a laptop stands outside a fence. Behind it are two big boxes: ageing, which needs labs, living cells and long studies, drawn with a flask; and fusion, which needs reactors, huge machines, drawn with a ring-shaped reactor. A long timeline underneath reads decades of work, for both.",
                  "Ageing and fusion both need labs or reactors and decades of work, so a person with a laptop can only follow them.")


DRAWINGS = {
    "turning-maths-into-machine-checked-proofs": d_lean,
    "weather-beyond-two-weeks": d_weather,
    "predicting-what-a-protein-does-or-binds": d_protein,
    "predicting-drug-toxicity-early": d_tox,
    "finding-new-battery-and-material-candidates": d_materials,
    "deep-theory-p-vs-np-the-riemann": d_theory,
    "ageing-and-fusion": d_ageing_fusion,
}
