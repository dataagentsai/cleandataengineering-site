"""Drawings for 'Why we wrote our own agent loop'. kit, figure, E and ROOT are injected."""


def _wheel(cx, cy, r=12):
    return f'<circle class="hz" cx="{cx}" cy="{cy}" r="{r}"/><circle class="hk" cx="{cx}" cy="{cy}" r="3"/>'


def _car(x, y):
    """A small car; (x, y) is the top-left of its body."""
    return (f'<path class="hz" d="M{x},{y + 50} L{x},{y + 28} L{x + 30},{y + 26} L{x + 48},{y} L{x + 108},{y} '
            f'L{x + 128},{y + 26} L{x + 160},{y + 28} L{x + 160},{y + 50} Z"/>'
            f'<path class="bxs" d="M{x + 54},{y + 7} L{x + 102},{y + 7} L{x + 116},{y + 24} L{x + 42},{y + 24} Z"/>'
            + _wheel(x + 36, y + 52, 13) + _wheel(x + 124, y + 52, 13))


def drawing_bike_showroom():
    t = kit.text
    d = '<rect class="bxm" x="10" y="10" width="470" height="300" rx="14"/>'
    d += '<rect class="bxm" x="520" y="10" width="470" height="300" rx="14"/>'
    # left: a shed roof line and a bicycle with a person holding a spanner
    d += '<path class="ln" d="M40,60 L245,28 L450,60"/>'
    d += t(245, 84, "THE SHED", "lbl", "middle")
    bx = 150
    d += _wheel(bx + 20, 200, 32) + _wheel(bx + 150, 200, 32)
    d += (f'<path class="ln" d="M{bx + 20},200 L{bx + 65},150 L{bx + 125},150 L{bx + 150},200 '
          f'M{bx + 65},150 L{bx + 85},200 L{bx + 125},150 M{bx + 85},200 L{bx + 20},200"/>')
    d += (f'<line class="lnc" x1="{bx + 55}" y1="138" x2="{bx + 77}" y2="138"/>'
          f'<line class="lnc" x1="{bx + 125}" y1="150" x2="{bx + 133}" y2="130"/>')
    px = 395
    d += (f'<circle class="bx" cx="{px}" cy="132" r="13"/><line class="lnc" x1="{px}" y1="145" x2="{px}" y2="190"/>'
          f'<line class="lnc" x1="{px}" y1="190" x2="{px - 12}" y2="228"/><line class="lnc" x1="{px}" y1="190" x2="{px + 12}" y2="228"/>'
          f'<line class="lnc" x1="{px}" y1="160" x2="{px - 30}" y2="172"/><line class="lnc" x1="{px}" y1="160" x2="{px + 18}" y2="178"/>')
    d += (f'<path class="hz" d="M{px - 54},178 L{px - 28},164 L{px - 24},171 L{px - 50},185 Z"/>'
          f'<circle class="hz" cx="{px - 56}" cy="183" r="7"/>')
    d += t(245, 268, "Our own loop", "bd", "middle")
    d += t(245, 292, "few parts, and we fitted every one", "sm", "middle")
    # right: showroom with two cars on a floor and an "everything included" sign
    d += t(755, 50, "THE SHOWROOM", "lbl", "middle")
    d += '<rect class="hz" x="655" y="64" width="200" height="34" rx="6"/>'
    d += t(755, 87, "everything included", "sm", "middle")
    d += _car(560, 140) + _car(780, 140)
    d += '<line class="ln" x1="540" y1="208" x2="970" y2="208"/>'
    d += ('<path class="hz" d="M716,150 L752,150 L760,160 L752,170 L716,170 Z"/>'
          '<circle class="hk" cx="724" cy="160" r="3"/>')
    d += t(755, 268, "A framework", "bd", "middle")
    d += t(755, 292, "engine, seats and satnav fitted for you", "sm", "middle")
    return figure(1000, 320, d,
                  "Two panels. Left, a shed with a hand-built bicycle and a stick person holding a spanner, labelled our own loop: few parts, and we fitted every one. Right, a car showroom with two cars, a price tag and a sign saying everything included, labelled a framework.",
                  "Both get you there. For an agent that moves money, we wanted to know every part.")


def drawing_loop_lines():
    b, a, t, n, p = kit.box, kit.arrow, kit.text, kit.num, kit.path
    d = b(250, 10, 500, 76, "The part that goes round: 4 lines", "for each step, up to 12: take a step", "solid")
    steps = [("Check the clock", "and is the customer here?", "bx"),
             ("Ask the model", "after a check", "bx"),
             ("Count", "tokens and money", "bx"),
             ("Answer", "words pass a check", "bxs"),
             ("Plan and act", "check each tool call", "bxs")]
    for i, (title, sub, k) in enumerate(steps):
        x = 10 + i * 198
        d += b(x, 150, 182, 86, title, sub, k) + n(x + 14, 150, i + 1)
        if i < 4:
            d += a(x + 184, 193, x + 196, 193)
    d += a(500, 88, 500, 146)
    d += t(512, 124, "one step", "sm", "start")
    d += p("M900,238 Q500,330 100,238", "lnd") + t(500, 300, "tools ran: take another step", "sm", "middle")
    # a sheet of paper with the count
    d += '<path class="hz" d="M70,330 L190,330 L210,350 L210,410 L70,410 Z"/>'
    d += "".join(f'<line class="ln" x1="88" y1="{350 + j * 14}" x2="190" y2="{350 + j * 14}"/>' for j in range(4))
    d += t(230, 360, "416 lines in one file", "bd", "start")
    d += t(230, 388, "290 of them code, once blank lines, comments and explanations are taken out", "sm", "start")
    return figure(1000, 425, d,
                  "At the top, a box: the part that goes round, 4 lines, for each step up to 12 take a step. An arrow goes down to five numbered steps in a row: check the clock and whether the customer is still here; ask the model after a check; count tokens and money; answer, where words pass a check; plan and act, checking each tool call. A dashed arrow loops back: tools ran, take another step. Below, a sheet of paper: 416 lines in one file, 290 of them code.",
                  "Our whole loop, drawn. Every rule has a line you can point at and a test can reach.")


def drawing_gain_cost():
    b, t = kit.box, kit.text
    # a balance scale
    d = '<line class="lnc" x1="500" y1="70" x2="500" y2="270"/>'
    d += '<path class="hz" d="M450,270 L550,270 L530,250 L470,250 Z"/>'
    d += '<line class="lnc" x1="290" y1="62" x2="710" y2="78"/>'
    d += '<circle class="hk" cx="500" cy="70" r="6"/>'
    d += '<line class="ln" x1="290" y1="62" x2="250" y2="104"/><line class="ln" x1="290" y1="62" x2="330" y2="104"/>'
    d += '<line class="ln" x1="710" y1="78" x2="670" y2="120"/><line class="ln" x1="710" y1="78" x2="750" y2="120"/>'
    d += b(30, 108, 420, 160, "It would have given us",
           ["state saved after each step", "a pause for a person to approve", "streaming replies", "built-in tools",
            "docs and a community", "fewer lines that are ours"], "bx")
    d += b(550, 124, 420, 144, "It would have cost us",
           ["checks only where its hooks are", "some steps hidden from our tests", "prompt text we didn't write",
            "hooks that move on upgrade", "the one view of the whole trip"], "bxs")
    d += t(500, 300, "for this agent, the right side weighed more", "sm", "middle")
    return figure(1000, 315, d,
                  "A balance scale with two pans. Left pan, what a framework would have given us: state saved after each step, a pause for a person to approve, streaming replies, built-in tools, docs and a community, fewer lines that are ours. Right pan, what it would have cost us: checks only where its hooks are, some steps hidden from our tests, prompt text we didn't write, hooks that move on upgrade, and the one view of the whole trip.",
                  "A fair trade to weigh. For a support agent that moves money, the cost side won.")


def drawing_loop_port():
    b, a, t = kit.box, kit.arrow, kit.text
    plugs = [("Our own loop", "built: runs today", "solid"),
             ("Pydantic AI", "written: being measured", "bx"),
             ("LangGraph", "planned", "bxm"),
             ("Claude Agent SDK", "planned", "bxm")]
    d = t(140, 22, "WHO RUNS THE STEPS", "lbl", "middle")
    for i, (name, sub, k) in enumerate(plugs):
        y = 40 + i * 92
        d += b(10, y, 260, 72, name, sub, k)
        d += a(272, y + 36, 356, 200)
    d += b(360, 70, 290, 260, "The same bar for all",
           ["16 frozen test cases,", "unchanged", "at most 150 lines", "of adapter per port",
            "no interface changed", "for the framework", "no fighting its loop"], "bxs")
    d += a(652, 200, 716, 200)
    d += b(720, 150, 270, 100, "The loop port", "one call: run a turn", "solid")
    d += t(855, 290, ["router, state, checks", "and traces never know", "which plug ran"], "sm", "middle")
    return figure(1000, 420, d,
                  "Four plugs on the left: our own loop, built and running today; Pydantic AI, written and being measured; LangGraph, planned; the Claude Agent SDK, planned. Each arrow passes through one gate, the same bar for all: 16 frozen test cases unchanged, at most 150 lines of adapter per port, no interface changed for the framework, no fighting its loop. The gate leads to the loop port, one call to run a turn, which the router, state, checks and traces use without knowing which plug ran.",
                  "Plain code today, but not for ever. Any loop that clears the same bar can take its place.")


DRAWINGS = {"own-bike-showroom": drawing_bike_showroom, "own-loop-lines": drawing_loop_lines,
            "own-gain-cost": drawing_gain_cost, "own-loop-port": drawing_loop_port}
