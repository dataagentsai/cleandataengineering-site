"""Drawings for 'Describe the world, not the test'.
kit, figure, E and ROOT are given as globals by build.py."""


def _person(cx, top, r=12):
    """A small stick person whose head centre is at (cx, top)."""
    return (f'<circle class="hz" cx="{cx}" cy="{top}" r="{r}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + r}" x2="{cx}" y2="{top + r + 30}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + r + 30}" x2="{cx - 10}" y2="{top + r + 50}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + r + 30}" x2="{cx + 10}" y2="{top + r + 50}"/>')


def _house(x, y, w=44, h=34):
    """A tiny house: a box with a roof, its bottom-left corner at (x, y)."""
    return (f'<rect class="hz" x="{x}" y="{y - h}" width="{w}" height="{h}" rx="2"/>'
            f'<path class="hz" d="M{x - 4},{y - h} L{x + w / 2},{y - h - 20} L{x + w + 4},{y - h} Z"/>')


def drawing_awd_map():
    b, t = kit.box, kit.text
    d = t(500, 26, "a map answers every route; a list of directions answers one", "sm", "middle")
    # --- left: the town map ---
    d += '<rect class="pf pf-solid" x="35" y="55" width="460" height="260" rx="18"/>'
    d += '<rect class="hz" x="30" y="50" width="460" height="260" rx="18" fill-opacity="0"/>'
    # roads
    d += '<path class="lnc" fill="none" d="M40,180 Q200,160 300,185 T480,175"/>'
    d += '<path class="lnc" fill="none" d="M250,60 Q240,150 265,300"/>'
    # buildings
    d += _house(70, 150) + t(92, 168, "Asha", "sm", "middle")
    d += _house(330, 150, 70, 40) + t(365, 168, "library", "sm", "middle")
    d += _house(90, 275, 60, 36) + t(120, 295, "bank", "sm", "middle")
    d += _house(370, 280, 50, 34) + t(395, 298, "approver", "sm", "middle")
    # a storm cloud (a fault) and a clock (time)
    d += '<path class="hz" d="M150,110 Q138,92 160,88 Q166,66 190,72 Q206,60 216,84 Q236,86 228,110 Z"/>'
    d += '<polyline class="lnc" fill="none" points="186,112 178,128 190,128 182,144"/>'
    d += '<circle class="hz" cx="440" cy="85" r="18"/><line class="ln" x1="440" y1="85" x2="440" y2="72"/><line class="ln" x1="440" y1="85" x2="450" y2="90"/>'
    d += t(260, 345, "THE WORLD, DRAWN ONCE", "lbl", "middle")
    # --- right: a list of directions ---
    d += '<path class="hz" d="M600,55 L930,55 L930,300 Q900,316 870,300 Q840,286 810,300 Q780,316 750,300 Q720,286 690,300 Q660,316 630,300 L600,300 Z"/>'
    lines = ["1. leave Asha's house", "2. turn left at the bank", "3. ask for The Hobbit", "4. expect: renewed",
             "", "(no storm, no closed road,", " no clerk on leave)"]
    for i, s in enumerate(lines):
        d += t(620, 92 + i * 30, s, "sm" if i >= 5 else "tx")
    d += t(765, 345, "A SCRIPT: ONE ROUTE", "lbl", "middle")
    d += t(545, 185, "vs", "bd", "middle")
    return figure(1000, 360, d, "Left: a cartoon map of a small town with Asha's house, a library, a bank, an approver's office, a storm cloud and a clock. Right: a paper list of directions for one trip: leave Asha's house, turn left at the bank, ask for The Hobbit, expect renewed, with a note that it assumes no storm, no closed road and no clerk on leave.",
                  "A world description is the map. A test script is one list of directions through it, written for a day when nothing goes wrong.")


def drawing_awd_six_parts():
    b, t = kit.box, kit.text
    d = t(500, 26, "write each part once; every scenario reads from the same description", "sm", "middle")
    left = [("Users", ["who they are, what", "they want, how they act"]),
            ("Systems + data", ["the tools, and the", "rows they hold at the start"]),
            ("Rules", ["what may change, and", "what is owed; cited"])]
    right = [("Faults", ["slow, lost reply,", "stale read, outage"]),
             ("Approvers", ["yes, no, never,", "or yes twice"]),
             ("Time", ["steps between turns;", "events at set hours"])]
    for i, (title, sub) in enumerate(left):
        y = 50 + i * 115
        d += b(20, y, 270, 90, title, sub, "bx")
        d += kit.arrow(292, y + 45, 388, 175 + (i - 1) * 30)
    for i, (title, sub) in enumerate(right):
        y = 50 + i * 115
        d += b(710, y, 270, 90, title, sub, "bxm")
        d += kit.arrow(708, y + 45, 612, 175 + (i - 1) * 30)
    d += b(390, 115, 220, 120, "World description", ["a few small files,", "read by everything"], "solid")
    d += t(500, 400, "rules live in the agent's own spec; the world cites it and never restates it", "sm", "middle")
    return figure(1000, 415, d, "A central box labelled world description, with six parts feeding it. On the left: users (who they are, what they want, how they act), systems and data (the tools and the rows at the start), and rules (what may change and what is owed, cited from the spec). On the right: faults (slow, lost reply, stale read, outage), approvers (yes, no, never, or yes twice) and time (steps between turns, events at set hours).",
                  "Six parts of a world. Write each one once, and every scenario draws on all of them.")


def drawing_awd_fan_out():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(500, 26, "the generator reads the world and asks what to vary", "sm", "middle")
    d += b(15, 135, 190, 100, "World", ["users, systems,", "rules, faults, time"], "solid")
    d += a(207, 185, 263, 185)
    # the generator: a little machine with a hopper and a crank
    d += '<path class="hz" d="M300,85 L400,85 L380,120 L320,120 Z"/>'
    d += b(265, 125, 170, 120, "Generator", ["edges of each rule,", "pairs of everything"], "bxs")
    d += '<circle class="hz" cx="350" cy="268" r="14"/><line class="lnc" x1="350" y1="268" x2="376" y2="282"/>'
    cards = [("Renew 7 days late", "the last allowed day", "bx"),
             ("Renew 8 days late", "one past the limit", "bx"),
             ("Someone else's loan", "must stay private", "bx"),
             ("Approver never answers", "request must expire", "bx"),
             ("Forgets the number", ["+ loan already returned", "+ the reply is lost"], "bxs")]
    for i, (title, sub, k) in enumerate(cards):
        y = 45 + i * 64 if i < 4 else 305
        h = 52 if i < 4 else 72
        d += b(555, y, 290, h, title, sub, k)
        d += a(437, 185, 551, y + h / 2)
    d += t(860, 345, ["nobody", "scripted this"], "bd")
    return figure(1000, 395, d, "On the left a world box feeds a generator drawn as a small machine with a hopper and a crank. The generator varies the edges of each rule and pairs of everything. Arrows fan out to five scenario cards: renew 7 days late, renew 8 days late, someone else's loan, approver never answers, and a highlighted one combining a customer who forgets the number, a loan already returned and a lost reply, labelled nobody scripted this.",
                  "One world, many scenarios. The edges come from the rules, and the odd combinations come from pairing every dimension with every other.")


def drawing_awd_change():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(30, 34, "WITH A WORLD DESCRIPTION", "lbl")
    d += b(20, 55, 230, 95, "Add one fault", ["a new kind joins", "the list of faults"], "bxs")
    d += a(252, 102, 318, 102)
    d += b(320, 55, 250, 95, "Coverage check", ["finds the pairs no", "scenario covers yet"], "bx")
    d += a(572, 102, 638, 102)
    d += b(640, 55, 230, 95, "New skeletons", ["one per missing pair;", "you fill in the words"], "solid")
    d += _person(925, 70)
    d += t(500, 185, "no existing scenario was edited", "bd", "middle")
    d += '<line class="lnd" x1="20" y1="215" x2="980" y2="215"/>'
    d += t(30, 255, "WITH SCRIPTS", "lbl")
    # a stack of script pages
    for k in range(4):
        d += f'<rect class="hz" x="{40 + k * 12}" y="{275 + k * 8}" width="110" height="80" rx="4"/>'
    d += t(130, 395, "200 scripts", "sm", "middle")
    d += a(200, 320, 288, 320)
    d += b(290, 275, 330, 95, "Someone must remember", ["which scripts could meet", "the new fault, and edit them"], "bxm")
    d += a(622, 322, 688, 322)
    d += b(690, 275, 220, 95, "Most never do", "the gap stays hidden", "bxm")
    return figure(1000, 410, d, "Top row, with a world description: add one new kind of fault to the list of faults; a coverage check finds the pairs no scenario covers yet; new scenario skeletons are written, one per missing pair, and a person fills in the words. No existing scenario was edited. Bottom row, with scripts: a stack of 200 scripts; someone must remember which scripts could meet the new fault and edit them; most never do, and the gap stays hidden.",
                  "Change the world, and the missing scenarios show up on their own. Change a pile of scripts, and you rely on someone's memory.")


DRAWINGS = {
    "awd-map": drawing_awd_map,
    "awd-six-parts": drawing_awd_six_parts,
    "awd-fan-out": drawing_awd_fan_out,
    "awd-change": drawing_awd_change,
}
