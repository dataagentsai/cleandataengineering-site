"""Drawings for 'A flight simulator for your agent: what AgentTwin is, and what it is not'.
kit, figure, E and ROOT are given as globals by build.py."""


def _person(cx, top):
    """A small stick person whose head centre is at (cx, top)."""
    return (f'<circle class="hz" cx="{cx}" cy="{top}" r="14"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 14}" x2="{cx}" y2="{top + 52}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 52}" x2="{cx - 12}" y2="{top + 76}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 52}" x2="{cx + 12}" y2="{top + 76}"/>')


def _check(x, y):
    return f'<path class="lnc" d="M{x},{y} L{x + 18},{y + 20} L{x + 52},{y - 22}"/>'


def _cross(x, y):
    return (f'<line class="lnc" x1="{x}" y1="{y - 20}" x2="{x + 40}" y2="{y + 20}"/>'
            f'<line class="lnc" x1="{x + 40}" y1="{y - 20}" x2="{x}" y2="{y + 20}"/>')


def drawing_twin_simulator():
    b, t, p = kit.box, kit.text, kit.path
    d = t(500, 24, "the cockpit and the pilot are real; everything outside the window is pretend", "sm", "middle")
    # pretend weather: a cloud with lightning
    d += '<path class="hz" d="M90,140 Q72,112 104,106 Q110,72 146,78 Q172,60 190,96 Q222,98 210,140 Z"/>'
    d += '<polyline class="lnc" fill="none" points="150,144 136,168 154,168 140,194"/>'
    d += b(30, 205, 240, 80, "Pretend weather", ["a storm, fog,", "a crosswind"], "bxm")
    d += p("M272,245 Q330,245 366,205", "lnd")
    # the cockpit
    d += '<rect class="pf pf-solid" x="375" y="65" width="260" height="200" rx="24"/>'
    d += '<rect class="hz" x="370" y="60" width="260" height="200" rx="24" fill-opacity="0"/>'
    d += '<path class="hz" d="M392,78 L608,78 L590,132 L410,132 Z"/>'
    d += t(500, 110, "screens, not glass", "sm", "middle")
    d += _person(500, 160)
    d += '<rect class="hz" x="530" y="205" width="60" height="30" rx="4"/>'
    d += '<line class="ln" x1="512" y1="206" x2="540" y2="214"/>'
    d += t(500, 290, "the pilot and controls are real", "bd", "middle")
    # the instructor with a switch panel
    d += _person(810, 60)
    d += '<rect class="hz" x="840" y="78" width="70" height="50" rx="4"/>'
    d += ''.join(f'<line class="lnc" x1="{852 + k * 16}" y1="{92 + (k % 2) * 8}" x2="{852 + k * 16}" y2="{112 + (k % 2) * 4}"/>' for k in range(4))
    d += b(730, 175, 240, 90, "The instructor", ["fails an engine,", "kills the radio"], "bxm")
    d += p("M728,215 Q680,200 634,180", "lnd")
    d += t(500, 325, "afterwards, nobody asks how it felt: they check where the plane ended up", "sm", "middle")
    return figure(1000, 340, d, "A cartoon flight simulator. In the middle, a real pilot sits in a real cockpit whose window is a screen. On the left, a cloud with lightning stands for pretend weather. On the right, an instructor at a switch panel can fail an engine or kill the radio. Afterwards, the check is where the plane ended up.",
                  "A flight simulator: the pilot is real, the weather is not. AgentTwin does the same for an agent.")


def drawing_twin_world():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(500, 40, "everything around the agent is pretend", "sm", "middle")
    left = [("Customer", ["scripted, or played", "by a model"]),
            ("Systems + data", ["stand-ins that keep", "the spec's rules"]),
            ("Approver", ["yes, no, or", "never answers"])]
    right = [("Faults", ["slow system,", "lost reply"]),
             ("Clock", ["days pass", "in seconds"]),
             ("Planted notes", ["attacks hidden", "in the data"])]
    for i, (title, sub) in enumerate(left):
        y = 20 + i * 120
        d += b(20, y, 240, 85, title, sub, "bx")
        d += a(262, y + 42, 398, 150 + i * 30)
    for i, (title, sub) in enumerate(right):
        y = 20 + i * 120
        d += b(740, y, 240, 85, title, sub, "bxm")
        d += a(738, y + 42, 602, 150 + i * 30)
    d += b(400, 120, 200, 110, "Real agent", ["code, prompts, model:", "unchanged"], "solid")
    # small clock face on the clock box
    d += '<circle class="hz" cx="950" cy="182" r="16"/><line class="ln" x1="950" y1="182" x2="950" y2="170"/><line class="ln" x1="950" y1="182" x2="959" y2="187"/>'
    d += a(500, 232, 500, 286)
    d += b(340, 288, 320, 75, "Judges read the world", "afterwards, not the chat", "bxs")
    return figure(1000, 375, d, "The real agent sits in the middle, unchanged. Around it, all pretend: on the left a customer, systems and data run by stand-ins that keep the spec's rules, and an approver; on the right faults, a clock where days pass in seconds, and attacks planted in the data. Below, judges read the world afterwards, not the chat.",
                  "Real agent, simulated world. Six kinds of pretend thing, and judges that read what changed.")


def drawing_twin_judge_world():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(155, 28, "WHAT THE AGENT SAID", "lbl", "middle") + t(470, 28, "LOAN BEFORE", "lbl", "middle")
    d += t(710, 28, "LOAN AFTER", "lbl", "middle") + t(910, 28, "JUDGE", "lbl", "middle")
    rows = [("well-built agent", ("L-1: renewed", "renew ran once", "bxs"), True),
            ("faulty agent", ("L-1: open", "renew never ran", "bxm"), False)]
    for i, (who, after, ok) in enumerate(rows):
        y = 70 + i * 125
        d += t(30, y - 10, who, "sm")
        d += f'<rect class="hz" x="20" y="{y}" width="270" height="60" rx="16"/>'
        d += f'<path class="hz" d="M60,{y + 58} L50,{y + 80} L84,{y + 58}"/>'
        d += t(155, y + 36, "\"Done, it's renewed!\"", "tx", "middle")
        d += b(370, y - 5, 200, 70, "L-1: open", "2 days late", "bx")
        d += a(572, y + 30, 608, y + 30)
        d += b(610, y - 5, 200, 70, after[0], after[1], after[2])
        if ok:
            d += _check(884, y + 32) + t(910, y + 75, "pass", "sm", "middle")
        else:
            d += _cross(890, y + 30) + t(910, y + 75, "fail: owed, not done", "sm", "middle")
    d += t(500, 320, "same words, different worlds: only a judge that reads the world can tell them apart", "bd", "middle")
    return figure(1000, 340, d, "Two runs. In both, the agent says 'Done, it's renewed!' and the loan L-1 starts open, 2 days late. In the well-built run the loan ends up renewed, renew ran once, and the judge passes it. In the faulty run the loan is still open because renew never ran, and the judge fails it: owed, not done.",
                  "Judge the world, not the words. The same reply can sit on top of two very different worlds.")


def drawing_twin_compare():
    b, a, t = kit.box, kit.arrow, kit.text
    d = ""
    panels = [("Digital twin", ["copies a real machine", "to predict it", "asks: what will it do?"]),
              ("Single-question eval", ["one question,", "one checked answer", "asks: was this right?"]),
              ("Load test", ["thousands of requests", "at once", "asks: is it fast?"]),
              ("AgentTwin", ["copies the world", "around a real agent", "asks: what changed?"])]
    for i, (title, lines) in enumerate(panels):
        x = 10 + i * 248
        cx = x + 115
        if i == 3:
            d += f'<rect class="pf pf-bxs" x="{x + 5}" y="15" width="230" height="290" rx="16"/>'
        d += f'<rect class="hz" x="{x}" y="10" width="230" height="290" rx="16" fill-opacity="0"/>'
        d += t(cx, 44, title, "bd", "middle")
        for j, s in enumerate(lines):
            d += t(cx, 222 + j * 24, s, "bd" if j == 2 else "sm", "middle")
        if i == 0:
            d += b(x + 12, 80, 90, 60, "Engine", "real", "bx")
            d += a(x + 104, 110, x + 126, 110)
            d += b(x + 128, 80, 90, 60, "Copy", "virtual", "bxm")
            d += t(cx, 170, "sensor data flows in", "sm", "middle")
        if i == 1:
            d += f'<rect class="hz" x="{x + 40}" y="72" width="150" height="100" rx="8"/>'
            d += t(x + 56, 104, "Q: refund my order?", "sm")
            d += f'<line class="lnd" x1="{x + 52}" y1="118" x2="{x + 178}" y2="118"/>'
            d += t(x + 56, 144, "A: yes, ₹3,499", "sm")
            d += _check(x + 150, 150)
        if i == 2:
            d += b(x + 120, 90, 95, 70, "Agent", "", "bx")
            for k in range(5):
                yy = 80 + k * 22
                d += a(x + 18, yy, x + 116, 125 + (k - 2) * 8)
        if i == 3:
            d += b(cx - 45, 95, 90, 60, "Agent", "real", "solid")
            for (ox, oy) in ((-80, -15), (80, -15), (-80, 45), (80, 45)):
                d += f'<circle class="hz" cx="{cx + ox}" cy="{110 + oy}" r="16"/>'
            d += t(cx, 186, "pretend world around it", "sm", "middle")
    return figure(1000, 315, d, "Four small panels. A digital twin copies a real engine from sensor data to predict it. A single-question eval checks one question and one answer. A load test fires thousands of requests at the agent to see if it is fast. AgentTwin, highlighted, keeps the agent real, puts a pretend world around it, and asks what changed.",
                  "Same family of words, four different jobs. AgentTwin is the only one that asks what changed in the world.")


DRAWINGS = {
    "twin-simulator": drawing_twin_simulator,
    "twin-world": drawing_twin_world,
    "twin-judge-world": drawing_twin_judge_world,
    "twin-compare": drawing_twin_compare,
}
