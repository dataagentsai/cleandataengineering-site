"""Drawings for 'The AI engineer roadmap'. Globals kit, figure, E, ROOT are injected."""


def _house(cx, base):
    """A small cartoon house whose floor sits at y=base."""
    return (f'<rect class="hz" x="{cx - 16}" y="{base - 22}" width="32" height="22" rx="2"/>'
            f'<path class="hz" d="M{cx - 21},{base - 21} L{cx},{base - 38} L{cx + 21},{base - 21} Z"/>'
            f'<rect class="hk" x="{cx - 4}" y="{base - 12}" width="8" height="12"/>')


def _person(cx, foot):
    """A stick person whose feet touch y=foot."""
    return (f'<circle class="bx" cx="{cx}" cy="{foot - 46}" r="12"/>'
            f'<line class="lnc" x1="{cx}" y1="{foot - 34}" x2="{cx}" y2="{foot - 15}"/>'
            f'<line class="lnc" x1="{cx}" y1="{foot - 15}" x2="{cx - 9}" y2="{foot}"/>'
            f'<line class="lnc" x1="{cx}" y1="{foot - 15}" x2="{cx + 10}" y2="{foot}"/>'
            f'<line class="lnc" x1="{cx}" y1="{foot - 27}" x2="{cx + 18}" y2="{foot - 35}"/>'
            f'<line class="lnc" x1="{cx}" y1="{foot - 27}" x2="{cx - 16}" y2="{foot - 21}"/>')


def drawing_road_map():
    b, t = kit.box, kit.text
    towns = [("Foundations", "phase 1"), ("Models", "phase 2"), ("Context", "phase 3"),
             ("Reliable", "phase 4"), ("Running", "phase 5"), ("Deeper", "optional")]
    d = t(500, 24, "six towns in order; each one uses what you learned in the town before", "sm", "middle")
    pos = []
    for i in range(6):
        x = 20 + i * 172
        y = 200 if i % 2 == 0 else 130
        pos.append((x, y))
    # the road, drawn first so the towns sit on top of it
    # a winding two-edged road with a dashed centre line, from the side of one town to the next
    for i in range(4):
        (x1, y1), (x2, y2) = pos[i], pos[i + 1]
        ax, bx2 = x1 + 110, x2
        for off, cls in ((-13, "ln"), (13, "ln"), (0, "lnd")):
            ay, by = y1 + 29 + off, y2 + 29 + off
            d += f'<path class="{cls}" fill="none" d="M{ax},{ay} C{ax + 12},{ay} {bx2 - 12},{by} {bx2},{by}"/>'
    # the side trip to the optional town is only a dashed track
    (x1, y1), (x2, y2) = pos[4], pos[5]
    d += f'<line class="lnd" x1="{x1 + 110}" y1="{y1 + 29}" x2="{x2}" y2="{y2 + 29}"/>'
    for i, ((name, sub), (x, y)) in enumerate(zip(towns, pos)):
        d += _house(x + 55, y - 4)
        d += b(x, y, 110, 58, name, sub, "bxm" if i == 5 else ("bxs" if i == 3 else "bx"))
    # the detour sign below the road, under town 4
    d += '<line class="lnc" x1="560" y1="285" x2="560" y2="360"/>'
    d += '<path class="hz" d="M500,285 L615,285 L635,305 L615,325 L500,325 Z"/>'
    d += t(562, 310, "SKIP FOR NOW", "lbl", "middle")
    d += '<path class="lnd" d="M640,310 Q700,345 780,335"/>'
    d += t(790, 315, ["training from scratch,", "every new framework,", "certificates alone"], "sm", "start")
    return figure(1000, 380, d, "A road zigzags through six towns: foundations, models, context, reliable, running, and an optional town called deeper at the end of a dashed road. Below the road a sign reading skip for now points down a dashed side road to training from scratch, every new framework, and certificates alone.",
                  "The roadmap as six towns. The last one is a side trip, and the detour sign marks what can wait.")


def drawing_road_stairs():
    t = kit.text
    steps = [("1 Foundations", ["Python, APIs,", "SQL, Git, cloud"], "bx"),
             ("2 Models", ["prompts, JSON,", "tools, the loop"], "bx"),
             ("3 Context", ["retrieval, RAG,", "the window"], "bx"),
             ("4 Reliable", ["evals, guardrails,", "traces, tests"], "bxs"),
             ("5 Running", ["cost, shipping,", "security, people"], "bx"),
             ("6 Deeper", ["fine-tune, serve,", "a tiny model"], "bxm")]
    d = t(500, 24, "climb one stair at a time; each stair ends with something that works", "sm", "middle")
    for i, (title, sub, k) in enumerate(steps):
        x = 10 + i * 165
        y = 290 - i * 42
        d += kit.box(x, y, 150, 370 - y, "", "", k)
        d += t(x + 75, y + 28, title, "bd", "middle")
        d += t(x + 75, y + 50, sub, "sm", "middle")
    d += t(910, 360, "optional", "lbl", "middle")
    d += _person(55, 288)
    return figure(1000, 385, d, "Six stairs rising left to right. 1 Foundations: Python, APIs, SQL, Git, cloud. 2 Models: prompts, JSON, tools, the loop. 3 Context: retrieval, RAG, the window. 4 Reliable: evals, guardrails, traces, tests. 5 Running: cost, shipping, security, people. 6 Deeper, dashed and marked optional: fine-tune, serve, a tiny model. A stick person stands on the first stair.",
                  "Six phases as a staircase. Stair 4 is the one people most want to skip, and the one that makes you trustworthy.")


def drawing_road_skip():
    b, t = kit.box, kit.text
    d = t(500, 24, "they look like the front door, but they are side rooms for later", "sm", "middle")
    items = [("Training from scratch", ["a lab's job;", "build with models first"]),
             ("Every new framework", ["learn the job,", "not the name"]),
             ("Certificates alone", ["a project with evals", "says more"])]
    for i, (title, sub) in enumerate(items):
        x = 20 + i * 330
        cx = x + 145
        if i == 0:  # a tall server rack
            d += f'<rect class="hz" x="{cx - 35}" y="50" width="70" height="110" rx="4"/>'
            d += "".join(f'<line class="ln" x1="{cx - 35}" y1="{72 + j * 22}" x2="{cx + 35}" y2="{72 + j * 22}"/>' for j in range(4))
            d += "".join(f'<circle class="hk" cx="{cx + 24}" cy="{61 + j * 22}" r="3"/>' for j in range(5))
        if i == 1:  # a messy pile of cards with new names
            for j, (dx, dy, rot) in enumerate([(-50, 110, -8), (-10, 95, 6), (-40, 70, 4), (0, 52, -6)]):
                d += f'<rect class="hz" x="{cx + dx}" y="{dy}" width="80" height="44" rx="4" transform="rotate({rot} {cx + dx + 40} {dy + 22})"/>'
            d += t(cx + 40, 80, "NEW!", "lbl", "middle")
        if i == 2:  # a certificate with a ribbon
            d += f'<rect class="hz" x="{cx - 60}" y="60" width="120" height="85" rx="4"/>'
            d += "".join(f'<line class="ln" x1="{cx - 40}" y1="{82 + j * 16}" x2="{cx + 40}" y2="{82 + j * 16}"/>' for j in range(3))
            d += f'<circle class="pf pf-bxs" cx="{cx + 40}" cy="140" r="14"/><circle class="hz" cx="{cx + 40}" cy="140" r="14"/>'
            d += f'<path class="ln" d="M{cx + 32},152 L{cx + 28},172 M{cx + 48},152 L{cx + 52},172"/>'
        # the cross over the picture
        d += f'<line class="lnc" x1="{cx - 70}" y1="45" x2="{cx + 70}" y2="170"/>'
        d += f'<line class="lnc" x1="{cx + 70}" y1="45" x2="{cx - 70}" y2="170"/>'
        d += b(x, 190, 290, 90, title, sub, "bxm")
    return figure(1000, 300, d, "Three crossed-out pictures. A server rack: training from scratch, a lab's job, build with models first. A messy pile of cards marked new: every new framework, learn the job, not the name. A certificate with a ribbon: certificates alone, a project with evals says more.",
                  "Three things to skip early. Each one is fine later; none of them is the place to start.")


def drawing_road_projects():
    b, t = kit.box, kit.text
    cards = [("Data service", ["rates API, SQL,", "tests, cloud"], "bx"),
             ("Expense helper", ["receipt to JSON,", "two tools, a loop"], "bx"),
             ("Handbook bot", ["answers from", "documents, cited"], "solid"),
             ("Prove it", ["golden questions,", "guardrails, traces"], "solid"),
             ("Go live", ["real users, cost,", "an approval step"], "solid"),
             ("Tiny model", ["a laptop model or", "a small fine-tune"], "bxm")]
    d = t(500, 24, "one small project closes each phase; finish it in a few weekends", "sm", "middle")
    for i, (title, sub, k) in enumerate(cards):
        x = 5 + i * 166
        d += kit.num(x + 75, 58, i + 1)
        d += b(x, 85, 150, 110, title, sub, k)
    # bracket under cards 3 to 5
    x1, x2 = 5 + 2 * 166 + 10, 5 + 4 * 166 + 140
    d += f'<path class="ln" d="M{x1},212 Q{x1},228 {x1 + 20},228 L{x2 - 20},228 Q{x2},228 {x2},212"/>'
    d += t((x1 + x2) / 2, 254, "the same assistant, growing up", "bd", "middle")
    d += t(910, 225, "optional", "lbl", "middle")
    return figure(1000, 275, d, "Six numbered project cards in a row: data service, expense helper, handbook bot, prove it, go live, and an optional tiny model. A bracket under cards 3, 4 and 5 says the same assistant, growing up.",
                  "One project per phase. Projects 3 to 5 are one assistant that you keep improving.")


DRAWINGS = {"road-map": drawing_road_map, "road-stairs": drawing_road_stairs,
            "road-skip": drawing_road_skip, "road-projects": drawing_road_projects}
