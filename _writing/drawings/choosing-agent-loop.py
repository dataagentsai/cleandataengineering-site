"""Drawings for 'Choosing your agent loop'. kit, figure, E and ROOT are injected."""


def _wheel(cx, cy, r=12):
    return f'<circle class="hz" cx="{cx}" cy="{cy}" r="{r}"/><circle class="hk" cx="{cx}" cy="{cy}" r="3"/>'


def _runner(cx, top, baton=None):
    """A small running stick figure; head centre at (cx, top + 11)."""
    s = (f'<circle class="bx" cx="{cx}" cy="{top + 11}" r="11"/>'
         f'<line class="lnc" x1="{cx}" y1="{top + 22}" x2="{cx - 4}" y2="{top + 50}"/>'
         f'<line class="lnc" x1="{cx - 4}" y1="{top + 50}" x2="{cx - 18}" y2="{top + 70}"/>'
         f'<line class="lnc" x1="{cx - 4}" y1="{top + 50}" x2="{cx + 12}" y2="{top + 68}"/>'
         f'<line class="lnc" x1="{cx - 2}" y1="{top + 32}" x2="{cx - 18}" y2="{top + 42}"/>'
         f'<line class="lnc" x1="{cx - 2}" y1="{top + 32}" x2="{cx + 16}" y2="{top + 38}"/>')
    if baton == "out":
        s += f'<rect class="bxs" x="{cx + 14}" y="{top + 31}" width="16" height="7" rx="2"/>'
    return s


def drawing_vehicles():
    t = kit.text
    d = ""
    labels = [("A bus on a fixed route", "LangGraph: a graph", ["you draw the stops", "and the roads between"]),
              ("A relay race", "OpenAI Agents SDK: handoffs", ["one agent passes", "the baton to the next"]),
              ("A car with a driver", "Claude Agent SDK", ["the driver and the", "tools come included"]),
              ("A bicycle you build", "Plain code: your while-loop", ["every part is yours,", "and so is every repair"])]
    for i, (name, who, sub) in enumerate(labels):
        x = 10 + i * 248
        d += f'<rect class="bxm" x="{x}" y="10" width="232" height="290" rx="14"/>'
        d += t(x + 116, 202, name, "bd", "middle")
        d += t(x + 116, 228, who, "lbl", "middle")
        d += t(x + 116, 254, sub, "sm", "middle")
    # 1. bus with route dots
    x = 10
    d += '<path class="lnd" d="M30,160 L240,160"/>'
    d += "".join(f'<circle class="pf pf-bxs" cx="{cx}" cy="160" r="7"/><circle class="hz" cx="{cx}" cy="160" r="5"/>' for cx in (40, 125, 230))
    d += f'<rect class="hz" x="{x + 40}" y="70" width="150" height="66" rx="10"/>'
    d += "".join(f'<rect class="bxs" x="{x + 52 + j * 34}" y="82" width="24" height="22" rx="3"/>' for j in range(4))
    d += _wheel(x + 72, 140) + _wheel(x + 160, 140)
    d += t(x + 115, 125, "route 4", "sm", "middle")
    # 2. relay: two runners, baton between
    d += '<line class="ln" x1="270" y1="166" x2="480" y2="166"/>'
    d += _runner(320, 92, baton="out") + _runner(410, 92)
    d += kit.path("M352,84 Q372,62 396,84", "lnd")
    # 3. car with driver
    x = 506
    d += (f'<path class="hz" d="M{x + 20},140 L{x + 20},110 L{x + 60},110 L{x + 82},80 L{x + 150},80 L{x + 172},110 '
          f'L{x + 212},112 L{x + 212},140 Z"/>')
    d += f'<path class="bxs" d="M{x + 90},88 L{x + 140},88 L{x + 156},108 L{x + 78},108 Z"/>'
    d += f'<circle class="bx" cx="{x + 116}" cy="96" r="8"/>'
    d += _wheel(x + 60, 142, 14) + _wheel(x + 172, 142, 14)
    d += f'<rect class="hz" x="{x + 30}" y="116" width="26" height="12" rx="3"/>'
    d += t(x + 116, 172, "toolbox in the boot", "sm", "middle")
    # 4. bicycle with spanner
    x = 754
    d += _wheel(x + 60, 135, 28) + _wheel(x + 170, 135, 28)
    d += (f'<path class="ln" d="M{x + 60},135 L{x + 100},95 L{x + 150},95 L{x + 170},135 M{x + 100},95 L{x + 115},135 '
          f'L{x + 150},95 M{x + 115},135 L{x + 60},135"/>')
    d += f'<line class="lnc" x1="{x + 92}" y1="85" x2="{x + 110}" y2="85"/><line class="lnc" x1="{x + 150}" y1="95" x2="{x + 158}" y2="78"/>'
    d += (f'<path class="hz" d="M{x + 166},66 L{x + 196},48 L{x + 201},56 L{x + 171},74 Z"/>'
          f'<circle class="hz" cx="{x + 201}" cy="48" r="8"/>')
    return figure(1000, 310, d,
                  "Four vehicles. A bus on a fixed route with stops, for LangGraph's graph. Two relay runners passing a baton, for the OpenAI Agents SDK's handoffs. A car with a driver and a toolbox in the boot, for the Claude Agent SDK. A bicycle with a spanner beside it, for a plain-code loop.",
                  "Four shapes of loop. They all get you there; they differ in who drives and who fixes it.")


def drawing_five_steps():
    b, a, t, n, p = kit.box, kit.arrow, kit.text, kit.num, kit.path
    steps = [("Build the context", "what the model reads", "bx"), ("Ask the model", "one call", "solid"),
             ("Read the answer", "words or tool requests?", "bx"), ("Check, then run", "the tools it asked for", "bxs"),
             ("Stop or go round", "done, or out of budget?", "bx")]
    d = ""
    for i, (title, sub, k) in enumerate(steps):
        x = 10 + i * 198
        d += b(x, 70, 182, 96, title, sub, k) + n(x + 12, 70, i + 1)
        if i < 4:
            d += a(x + 184, 118, x + 196, 118)
    d += p("M900,168 Q500,290 100,168") + t(500, 258, "go round: the tool results go into the next context", "sm", "middle")
    d += t(500, 36, "the same five steps in LangGraph, either SDK, or your own while-loop", "sm", "middle")
    d += b(250, 280, 500, 60, "Stop rules, checked every trip", "say, 12 trips, 60 seconds, $0.50", "bxs")
    return figure(1000, 350, d,
                  "Five boxes in a row: build the context, ask the model, read the answer, check then run the tools, stop or go round. An arrow loops back from the last to the first. Below, a box for stop rules checked every trip.",
                  "What every agent loop does. The frameworks differ only in who writes these five boxes, and where you can reach in.")


def drawing_port():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(500, 24, "THE HARNESS: STAYS THE SAME", "lbl", "middle")
    parts = [("Router", "bx"), ("State", "bx"), ("Checks", "bxs"), ("Traces", "bx"), ("Cost meter", "bxs")]
    for i, (name, k) in enumerate(parts):
        d += b(30 + i * 192, 40, 170, 56, name, kind=k)
    d += b(310, 130, 380, 70, "The loop port", "run(turn) gives back a result", "solid")
    d += "".join(f'<line class="lnd" x1="{115 + i * 192}" y1="98" x2="{400 + i * 50}" y2="128"/>' for i in range(5))
    # socket pins under the port
    d += "".join(f'<rect class="hk" x="{470 + j * 36}" y="200" width="10" height="20" rx="2"/>' for j in range(3))
    plugs = [("Plain code", "about 400 lines: built", "solid"), ("Pydantic AI", "adapter: built", "bx"),
             ("LangGraph", "adapter: planned", "bxm"), ("Claude Agent SDK", "adapter: planned", "bxm")]
    for i, (name, sub, k) in enumerate(plugs):
        x = 30 + i * 240
        d += b(x, 280, 220, 70, name, sub, k)
        d += a(x + 110, 278, 480 + i * 12, 224)
    d += t(500, 384, "same tests for every plug; swapping is a line of configuration", "sm", "middle")
    return figure(1000, 400, d,
                  "Five harness parts across the top: router, state, checks, traces, cost meter. They all connect to one socket, the loop port. Below, four plugs point up to the socket: plain code and Pydantic AI, both built; LangGraph and the Claude Agent SDK, both planned.",
                  "The loop as a plug-in part. The reference agent runs its own loop, and can run Pydantic AI's instead without the rest noticing.")


def drawing_decide():
    b, a, t = kit.box, kit.arrow, kit.text
    qs = [("Can a wrong step move money", "or change someone's records?"),
          ("Is the work a known flow", "with pauses for a person?"),
          ("Does it work on files, code", "or the web, for your own team?")]
    picks = [("Plain code loop", "checks at exact places", "solid"),
             ("LangGraph", "a graph with checkpoints", "bx"),
             ("Claude Agent SDK", "tools and context included", "bx")]
    d = ""
    for i, ((q1, q2), (pn, ps, k)) in enumerate(zip(qs, picks)):
        y = 20 + i * 120
        d += b(20, y, 380, 80, f"{i + 1}. {q1}", q2, "bxs")
        d += a(402, y + 40, 600, y + 40, "yes", lx=500, ly=y + 30)
        d += b(605, y, 375, 80, pn, ps, k)
        if i < 2:
            d += a(210, y + 82, 210, y + 118, "no", lx=232, ly=y + 106, anchor="start")
    y = 380
    d += a(210, 322, 210, y - 2, "no", lx=232, ly=360, anchor="start")
    d += b(20, y, 960, 72, "Start with a plain loop", "add handoffs (the OpenAI Agents SDK's idea) only if you really have specialists passing work", "bxm")
    return figure(1000, 465, d,
                  "Three questions down the left. One: can a wrong step move money or change records? Yes leads to a plain code loop. Two: is the work a known flow with pauses for a person? Yes leads to LangGraph. Three: does it work on files, code or the web for your own team? Yes leads to the Claude Agent SDK. If all three are no, start with a plain loop and add handoffs only if you really have specialists.",
                  "Three questions, asked in order. Whatever you pick, put it behind the port.")


DRAWINGS = {"loop-vehicles": drawing_vehicles, "loop-five-steps": drawing_five_steps,
            "loop-port": drawing_port, "loop-decide": drawing_decide}
