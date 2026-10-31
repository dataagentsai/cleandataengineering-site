"""Drawings for 'Build only the gaps: AgentTwin assembled from open-source tools'.
kit, figure, E and ROOT are given as globals by build.py."""


def _brick(x, y, w, kind):
    """A Lego-style brick, 26 high, with studs on top. kind is 'bx' or 'solid'."""
    s = f'<rect class="pf pf-{kind}" x="{x + 3}" y="{y + 3}" width="{w}" height="26" rx="3"/>'
    for k in range(max(1, w // 24)):
        sx = x + 8 + k * 24
        s += f'<rect class="hz" x="{sx}" y="{y - 6}" width="12" height="7" rx="2"/>'
    s += f'<rect class="hz" x="{x}" y="{y}" width="{w}" height="26" rx="3" fill-opacity="0"/>'
    return s


def _person(cx, top):
    return (f'<circle class="hz" cx="{cx}" cy="{top}" r="14"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 14}" x2="{cx}" y2="{top + 52}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 52}" x2="{cx - 12}" y2="{top + 76}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 52}" x2="{cx + 12}" y2="{top + 76}"/>')


def drawing_asm_lego():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(500, 22, "buy every brick the shop sells; make only the shapes it doesn't", "sm", "middle")
    # the shop: awning, building, shelves of bricks
    d += '<rect class="hz" x="40" y="72" width="230" height="150" rx="6"/>'
    d += '<path class="hz" d="M30,72 L30,48 L280,48 L280,72 Q264,86 249,72 Q233,86 218,72 Q202,86 186,72 Q170,86 155,72 Q139,86 124,72 Q108,86 92,72 Q76,86 61,72 Q45,86 30,72 Z"/>'
    d += t(155, 66, "SHOP", "lbl", "middle")
    d += '<line class="ln" x1="52" y1="140" x2="258" y2="140"/><line class="ln" x1="52" y1="200" x2="258" y2="200"/>'
    for i in range(4):
        d += _brick(58 + i * 50, 108, 40, "bx")
        d += _brick(58 + i * 50, 168, 40, "bx")
    d += t(155, 250, "the shop: open-source tools", "bd", "middle")
    d += a(282, 150, 385, 150, "most", lx=333, ly=138)
    # the model in the middle: mostly shop bricks, four home-made ones
    rows = [(200, [(400, 96, "bx"), (500, 100, "bx")]),
            (172, [(420, 70, "bx"), (494, 60, "solid"), (558, 42, "bx")]),
            (144, [(410, 90, "bx"), (504, 80, "bx")]),
            (116, [(430, 50, "solid"), (484, 70, "bx")]),
            (88, [(450, 46, "solid"), (500, 50, "solid")])]
    for y, bricks in rows:
        for (x, w, k) in bricks:
            d += _brick(x, y, w, k)
    d += t(500, 250, "the model: AgentTwin", "bd", "middle")
    # home: four custom bricks on a workbench
    homes = [("World format", 710, 70), ("Stand-ins", 850, 70), ("Judges", 710, 135), ("Mode switch", 850, 135)]
    for name, x, y in homes:
        d += b(x, y, 130, 50, name, "", "solid")
    d += '<rect class="hz" x="700" y="200" width="290" height="14" rx="3"/>'
    d += '<line class="lnc" x1="715" y1="214" x2="715" y2="236"/><line class="lnc" x1="975" y1="214" x2="975" y2="236"/>'
    d += t(845, 260, "made at home: only 4", "bd", "middle")
    d += a(698, 150, 615, 150, "4", lx=656, ly=138)
    return figure(1000, 275, d, "A cartoon of a Lego build. On the left, a shop with shelves of blue bricks stands for open-source tools. In the middle, the AgentTwin model is built mostly from shop bricks, with four lavender bricks mixed in. On the right, a workbench at home holds the four custom bricks: world format, stand-ins, judges and mode switch.",
                  "Most bricks come from the shop. Four had to be made at home, because no shop sold them.")


def drawing_asm_assembly():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(500, 26, "the core never imports a tool: each one plugs into a port", "sm", "middle")
    # the core with its four built pieces
    d += '<rect class="pf pf-solid" x="355" y="65" width="300" height="270" rx="22"/>'
    d += '<rect class="hz" x="350" y="60" width="300" height="270" rx="22" fill-opacity="0"/>'
    d += t(500, 92, "AgentTwin core: built", "bd", "middle")
    inner = [("World format", 362, 110), ("Stand-ins", 513, 110), ("Four judges", 362, 200), ("Mode switch", 513, 200)]
    for name, x, y in inner:
        d += b(x, y, 125, 70, name, "", "bxs")
    d += t(500, 310, "the four gaps", "sm", "middle")
    left = [("pytest", "runs every scenario"), ("Hypothesis", "invents edge values"), ("allpairspy", "picks combinations")]
    right = [("LangWatch Scenario", "plays the customer"), ("PyRIT", "rewrites attacks"), ("time-machine", "moves the clock")]
    for i, (name, sub) in enumerate(left):
        y = 85 + i * 85
        d += b(20, y, 240, 65, name, sub, "bx")
        d += a(262, y + 32, 336, y + 32)
        d += f'<circle class="hz" cx="350" cy="{y + 32}" r="9"/>'
    for i, (name, sub) in enumerate(right):
        y = 85 + i * 85
        d += b(740, y, 240, 65, name, sub, "bx")
        d += a(738, y + 32, 664, y + 32)
        d += f'<circle class="hz" cx="650" cy="{y + 32}" r="9"/>'
    d += t(140, 345, "ADOPTED", "lbl", "middle") + t(860, 345, "ADOPTED", "lbl", "middle")
    d += t(500, 362, "small circles are ports: unplug one tool, plug in another", "sm", "middle")
    return figure(1000, 375, d, "AgentTwin's core in the middle, holding the four pieces it builds itself: the world format, the stand-ins, four judges and the mode switch. Around it, six adopted tools plug into small port circles on the core's edge: pytest, Hypothesis and allpairspy on the left; LangWatch Scenario, PyRIT and time-machine on the right.",
                  "Built in the middle, adopted around the edge. Every adopted tool reaches the core only through a port.")


def drawing_asm_rule():
    b, a, t = kit.box, kit.arrow, kit.text
    d = ""
    # a person with a magnifying glass: check first
    d += _person(90, 60)
    d += '<circle class="hz" cx="140" cy="88" r="16"/><line class="lnc" x1="129" y1="100" x2="104" y2="122"/>'
    d += t(110, 175, "check first,", "sm", "middle") + t(110, 195, "design second", "sm", "middle")
    qs = [("Does it exist?", "search before you design", "No: build it", "small, behind a port"),
          ("Good enough, behind a port?", "does the job, can be unplugged", "No: look again", "or extend it"),
          ("What exactly is the gap?", "one sentence: what it doesn't do", "Can't name it?", "then don't build")]
    for i, (q, qs_, no, nos) in enumerate(qs):
        y = 30 + i * 110
        d += kit.num(250, y + 35, i + 1)
        d += b(280, y, 340, 70, q, qs_, "bxs")
        d += a(622, y + 35, 718, y + 35, "no", lx=670, ly=y + 25)
        d += b(720, y, 250, 70, no, nos, "bxm")
        if i < 2:
            d += a(450, y + 72, 450, y + 108, "yes", lx=475, ly=y + 94)
    d += a(450, 322, 450, 358, "named", lx=490, ly=344)
    d += b(320, 360, 260, 62, "Build only that gap", "and write down why", "solid")
    return figure(1000, 435, d, "A three-question card, with a small person holding a magnifying glass. Question 1: does it exist? If no, build it, small and behind a port. Question 2: is it good enough behind a port? If no, look again or extend it. Question 3: what exactly is the gap? If you can't name it, don't build. If you can, build only that gap and write down why.",
                  "The decision rule. Each \"yes\" moves you down the card; you only build at the bottom, and only the named gap.")


def _basket(x, label):
    """A woven basket 290 wide whose top-left corner is at (x + 60, 300)."""
    s = f'<path class="hz" d="M{x + 50},300 L{x + 360},300 L{x + 330},385 L{x + 80},385 Z"/>'
    s += f'<line class="ln" x1="{x + 60}" y1="320" x2="{x + 353}" y2="320"/>'
    s += f'<line class="ln" x1="{x + 70}" y1="366" x2="{x + 337}" y2="366"/>'
    s += kit.text(x + 205, 348, label, "bd", "middle")
    return s


def drawing_asm_baskets():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(250, 26, "IN", "lbl", "middle") + t(760, 26, "OUT", "lbl", "middle")
    ins = [("pytest", "one runner, so one report"), ("Hypothesis", "finds odd inputs; already a dependency"),
           ("LangWatch Scenario", "only its customer: we judge by state")]
    outs = [("WireMock / Prism", "canned answers: a shipped order 'cancels'"), ("garak", "tests the model, not the agent"),
            ("DeepTeam", "overlaps promptfoo: one is enough")]
    for col, (x, items) in enumerate(((45, ins), (555, outs))):
        for i, (name, why) in enumerate(items):
            y = 45 + i * 77
            d += b(x, y, 410, 62, name, why, "bx" if col == 0 else "bxm")
        d += a(x + 205, 272, x + 205, 296)
    d += _basket(45, "in use: 12 of 38")
    d += _basket(555, "opted out: 6 of 38")
    d += t(500, 410, "the other 20 wait with a reason: next, evaluate, later, or the Azure version", "sm", "middle")
    return figure(1000, 425, d, "Two baskets. The In basket, holding 12 of 38 tools, with examples: pytest, one runner so one report; Hypothesis, finds odd inputs and is already a dependency; LangWatch Scenario, only its customer because AgentTwin judges by state. The Out basket, holding 6 of 38: WireMock and Prism, canned answers that would let a shipped order cancel; garak, tests the model not the agent; DeepTeam, overlaps promptfoo. The other 20 wait with a reason.",
                  "Sorted into two baskets, each with a one-line reason. The reasons matter more than the verdicts.")


DRAWINGS = {
    "asm-lego": drawing_asm_lego,
    "asm-assembly": drawing_asm_assembly,
    "asm-rule": drawing_asm_rule,
    "asm-baskets": drawing_asm_baskets,
}
