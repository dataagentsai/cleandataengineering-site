"""Drawings for 'One harness, five homes'. Globals kit, figure, E, ROOT are injected."""


def _person(x, y):
    """A small stick person; (x, y) is the centre of the head."""
    return (f'<circle class="bx" cx="{x}" cy="{y}" r="13"/>'
            f'<line class="lnc" x1="{x}" y1="{y + 13}" x2="{x}" y2="{y + 50}"/>'
            f'<line class="lnc" x1="{x}" y1="{y + 50}" x2="{x - 12}" y2="{y + 72}"/>'
            f'<line class="lnc" x1="{x}" y1="{y + 50}" x2="{x + 12}" y2="{y + 72}"/>'
            f'<line class="lnc" x1="{x}" y1="{y + 24}" x2="{x + 22}" y2="{y + 10}"/>'
            f'<line class="lnc" x1="{x}" y1="{y + 24}" x2="{x - 16}" y2="{y + 38}"/>')


def drawing_home_floorplan():
    b, t = kit.box, kit.text
    d = t(175, 30, "THE HARNESS: ONE FLOOR PLAN", "lbl", "middle")
    d += '<rect class="pf pf-solid" x="20" y="45" width="310" height="235" rx="10"/>'
    rooms = ["Model door", "Loop", "Tools", "State", "Checks", "Traces"]
    for i, r in enumerate(rooms):
        d += b(35 + (i % 2) * 145, 60 + (i // 2) * 72, 130, 56, r, (), "solid")
    d += kit.path("M340,165 Q360,165 378,165")
    d += t(680, 30, "FIVE HOMES BUILT FROM IT", "lbl", "middle")
    names = ["Azure", "Google Cloud", "AWS", "Databricks", "Open source"]
    for i, n in enumerate(names):
        x = 395 + i * 120
        cx = x + 50
        d += f'<path class="hz" d="M{x - 8},150 L{cx},100 L{x + 108},150 Z"/>'
        cls = "lnd" if i == 4 else "hz"
        d += f'<rect class="{cls}" x="{x}" y="150" width="100" height="110"/>'
        if i == 0:  # bricks
            for j, yy in enumerate(range(168, 260, 16)):
                d += f'<line class="ln" x1="{x}" y1="{yy}" x2="{x + 100}" y2="{yy}"/>'
                off = 0 if j % 2 else 12
                for xx in range(x + 12 + off, x + 100, 25):
                    if not (cx - 14 < xx < cx + 14 and yy > 210):
                        d += f'<line class="ln" x1="{xx}" y1="{yy - 16}" x2="{xx}" y2="{yy}"/>'
        if i == 1:  # timber planks
            for xx in range(x + 14, x + 100, 14):
                if not (cx - 14 < xx < cx + 14):
                    d += f'<line class="ln" x1="{xx}" y1="150" x2="{xx}" y2="260"/>'
        if i == 2:  # glass windows
            for wx in (x + 10, x + 62):
                d += (f'<rect class="hz" x="{wx}" y="164" width="28" height="30"/>'
                      f'<line class="ln" x1="{wx + 14}" y1="164" x2="{wx + 14}" y2="194"/>'
                      f'<line class="ln" x1="{wx}" y1="179" x2="{wx + 28}" y2="179"/>')
        if i == 3:  # stone
            for (sx, sy) in [(14, 168), (40, 172), (70, 166), (88, 190), (16, 196), (22, 230), (80, 226), (86, 248), (14, 252)]:
                d += f'<ellipse class="hz" cx="{x + sx}" cy="{sy}" rx="9" ry="6"/>'
        if i == 4:  # a hammer leaning on the wall
            d += (f'<line class="lnc" x1="{x + 14}" y1="255" x2="{x + 30}" y2="200"/>'
                  f'<rect class="hk" x="{x + 20}" y="192" width="22" height="9" rx="2" transform="rotate(16 {x + 31} 196)"/>')
        d += f'<rect class="hz" x="{cx - 11}" y="225" width="22" height="35" rx="2"/>'
        d += t(cx, 284, n, "tx", "middle")
    d += t(680, 310, "same rooms and doors; only the material changes", "sm", "middle")
    return figure(1000, 325, d,
                  "A lavender floor plan labelled the harness, with six rooms: model door, loop, tools, state, checks and traces. An arrow leads to five small houses built from it: Azure in brick, Google Cloud in timber planks, AWS with glass windows, Databricks in stone, and open source with a dashed outline and a hammer leaning on the wall, because you build it yourself.",
                  "One floor plan, five houses. The harness design is the plan; each platform is a different material.")


def drawing_home_badges():
    b, t = kit.box, kit.text
    d = t(195, 40, "THE JOB (CONCEPT)", "lbl", "middle")
    d += b(30, 70, 330, 160, "Durable waits", ["wait days for a person,", "survive a restart,", "never pay twice"], "solid")
    d += t(645, 22, "THE PRODUCT ON EACH PLATFORM", "lbl", "middle")
    badges = [("Durable Task Scheduler", "Azure", "bx"), ("Workflows", "Google Cloud", "bx"),
              ("Step Functions", "AWS", "bx"), ("bring your own", "Databricks", "bxm"),
              ("DBOS or Temporal", "open source", "bxs")]
    for i, (name, where, kind) in enumerate(badges):
        y = 36 + i * 56
        d += b(520, y, 240, 46, name, (), kind)
        d += t(775, y + 28, where, "sm")
        d += f'<line class="lnd" x1="362" y1="150" x2="518" y2="{y + 23}"/>'
    d += t(195, 262, "the card never changes; the badge does", "sm", "middle")
    return figure(1000, 325, d,
                  "A lavender job card: durable waits, meaning wait days for a person, survive a restart and never pay twice. Dashed lines join it to five product badges: Durable Task Scheduler on Azure, Workflows on Google Cloud, Step Functions on AWS, bring your own on Databricks, and DBOS or Temporal in open source.",
                  "Concept versus product. One job card, five badges. On Databricks our sources name no product for this job, so you bring one.")


def drawing_home_umbrella():
    b, t = kit.box, kit.text
    # canopy with a scalloped edge
    d = '<path class="hz" d="M40,120 Q300,-20 560,120 Q527,100 495,120 Q462,100 430,120 Q397,100 365,120 Q332,100 300,120 Q267,100 235,120 Q202,100 170,120 Q137,100 105,120 Q72,100 40,120 Z"/>'
    d += '<line class="ln" x1="300" y1="50" x2="300" y2="36"/>'
    d += t(300, 84, "a managed agent service", "bd", "middle")
    # handle in the gap between the two pairs of boxes
    d += '<path class="lnc" d="M300,112 L300,215 Q300,232 286,232 Q274,232 274,220" fill="none"/>'
    for i, n in enumerate(["Loop", "Tools", "Memory", "Tracing"]):
        x = 45 + i * 120 + (50 if i >= 2 else 0)
        d += b(x, 145, 105, 60, n, (), "bx")
    d += t(300, 258, "Foundry Agent Service, Agent Engine, AgentCore, Mosaic AI Agent Framework", "sm", "middle")
    d += t(800, 30, "STILL YOURS, OUT IN THE RAIN", "lbl", "middle")
    for i, n in enumerate(["Checks that protect money", "Evals on your own cases", "Cost per business task"]):
        y = 50 + i * 70
        d += b(650, y, 300, 52, n, (), "bxs")
        for k in range(3):
            dx = 612 + k * 10
            d += f'<line class="ln" x1="{dx + 4}" y1="{y + 6 + k * 12}" x2="{dx}" y2="{y + 20 + k * 12}"/>'
    return figure(1000, 275, d,
                  "An umbrella labelled a managed agent service covers four blue boxes: loop, tools, memory and tracing. Underneath it are the names Foundry Agent Service, Agent Engine, AgentCore and Mosaic AI Agent Framework. To the right, out in the rain, three yellow boxes are still yours: checks that protect money, evals on your own cases, and cost per business task.",
                  "A managed agent service covers several rows at once. Some rows stay out in the rain, and they are yours.")


def drawing_home_pick():
    b, t, a = kit.box, kit.text, kit.arrow
    d = _person(45, 95)
    d += t(45, 192, ["you, before", "shopping"], "sm", "middle")
    qs = [("Where is your data?", ["the agent reads it every", "turn; live next to it"]),
          ("Where is your identity?", ["where staff and customers", "already sign in"]),
          ("What will your team run?", ["which managed pieces you", "trust, and which you patch"])]
    for i, (q, s) in enumerate(qs):
        x = 95 + i * 250
        d += b(x, 70, 235, 120, q, s, "bxs")
        d += kit.num(x + 18, 70, i + 1)
        if i < 2:
            d += a(x + 237, 130, x + 248, 130)
    d += a(832, 130, 868, 130)
    # the house the answers point to
    d += '<path class="hz" d="M872,120 L925,78 L978,120 Z"/>'
    d += '<rect class="hz" x="880" y="120" width="90" height="80"/>'
    d += '<rect class="hz" x="914" y="160" width="22" height="40" rx="2"/>'
    d += t(925, 225, "your home", "tx", "middle")
    d += t(465, 236, "answer all three before you name a product", "sm", "middle")
    return figure(1000, 260, d,
                  "A stick person on the left faces three numbered yellow question cards in a row: one, where is your data, since the agent reads it every turn; two, where is your identity, where staff and customers already sign in; three, what will your team run, which managed pieces you trust and which you patch. An arrow leads to a small house labelled your home.",
                  "How to pick a home: three questions, answered before anyone names a product.")


DRAWINGS = {
    "home-floorplan": drawing_home_floorplan,
    "home-badges": drawing_home_badges,
    "home-umbrella": drawing_home_umbrella,
    "home-pick": drawing_home_pick,
}
