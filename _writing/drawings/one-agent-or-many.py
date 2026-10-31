"""Drawings for 'One agent or many?'. kit, figure, E and ROOT are injected."""


def _cook(cx, top, hat=True):
    """A small stick cook; head centre at (cx, top + 26)."""
    s = ""
    if hat:
        s += (f'<path class="hz" d="M{cx - 10},{top + 16} Q{cx - 16},{top} {cx - 4},{top + 4} '
              f'Q{cx},{top - 4} {cx + 4},{top + 4} Q{cx + 16},{top} {cx + 10},{top + 16} Z"/>')
    s += (f'<circle class="bx" cx="{cx}" cy="{top + 26}" r="10"/>'
          f'<line class="lnc" x1="{cx}" y1="{top + 36}" x2="{cx}" y2="{top + 66}"/>'
          f'<line class="lnc" x1="{cx}" y1="{top + 66}" x2="{cx - 10}" y2="{top + 86}"/>'
          f'<line class="lnc" x1="{cx}" y1="{top + 66}" x2="{cx + 10}" y2="{top + 86}"/>'
          f'<line class="lnc" x1="{cx}" y1="{top + 46}" x2="{cx - 16}" y2="{top + 56}"/>'
          f'<line class="lnc" x1="{cx}" y1="{top + 46}" x2="{cx + 16}" y2="{top + 56}"/>')
    return s


def _note(x, y, w=26, h=18):
    return (f'<rect class="bxs" x="{x}" y="{y}" width="{w}" height="{h}" rx="2"/>'
            f'<line class="ln" x1="{x + 5}" y1="{y + 7}" x2="{x + w - 5}" y2="{y + 7}"/>'
            f'<line class="ln" x1="{x + 5}" y1="{y + 12}" x2="{x + w - 9}" y2="{y + 12}"/>')


def drawing_cooks():
    t = kit.text
    d = '<rect class="bxm" x="10" y="10" width="560" height="300" rx="14"/>'
    d += '<rect class="bxm" x="590" y="10" width="400" height="300" rx="14"/>'
    d += t(290, 40, "Five cooks, passing notes", "bd", "middle")
    d += t(790, 40, "One cook, good tools", "bd", "middle")
    # five cooks in a row with notes passed between them
    xs = [60, 170, 280, 390, 500]
    for i, cx in enumerate(xs):
        d += _cook(cx, 100)
        if i < 4:
            d += kit.path(f"M{cx + 18},{150} Q{cx + 55},{108} {xs[i + 1] - 18},{150}", "lnd")
            d += _note(cx + 42, 96)
    # counter
    d += '<rect class="hz" x="30" y="196" width="520" height="16" rx="4"/>'
    d += t(290, 250, ["each note leaves something out,", "and the dish waits for everyone"], "sm", "middle")
    # one cook with knife, recipe card and timer
    cx = 700
    d += _cook(cx, 100)
    d += '<rect class="hz" x="620" y="196" width="350" height="16" rx="4"/>'
    # knife
    d += ('<path class="hz" d="M760,186 L812,170 L816,178 L766,192 Z"/>'
          '<rect class="hk" x="812" y="168" width="20" height="10" rx="3" transform="rotate(-17 822 173)"/>')
    # recipe card
    d += '<rect class="hz" x="850" y="120" width="56" height="70" rx="4"/>'
    d += "".join(f'<line class="ln" x1="860" y1="{136 + j * 14}" x2="896" y2="{136 + j * 14}"/>' for j in range(4))
    # timer
    d += ('<circle class="hz" cx="940" cy="170" r="18"/><line class="ln" x1="940" y1="170" x2="940" y2="158"/>'
          '<line class="ln" x1="940" y1="170" x2="949" y2="174"/><rect class="hk" x="935" y="146" width="10" height="6" rx="2"/>')
    d += t(790, 250, ["the whole dish in one head,", "a tool for each special job"], "sm", "middle")
    return figure(1000, 320, d,
                  "Left: five stick-figure cooks in a row, each passing a yellow note to the next along dashed curves. Right: one cook at a counter with a knife, a recipe card and a timer.",
                  "Five cooks spend their time writing and reading notes. One cook with good tools keeps the whole dish in mind.")


def drawing_handoff():
    b, a, t = kit.box, kit.arrow, kit.text
    notes = [(["Refund order 4417,", "not the gift wrap,", "needed by Friday:", "travels Saturday"], 210, 120),
             (["Refund order 4417,", "not the gift wrap,", "by Friday"], 190, 100),
             (["Refund order 4417,", "by Friday"], 170, 80),
             (["Refund order 4417"], 170, 60)]
    who = ["Priya", "Agent 1", "Agent 2", "Agent 3"]
    d = t(500, 24, "each hand-off is a summary, and each summary drops something", "sm", "middle")
    for i, ((lines, w, h), name) in enumerate(zip(notes, who)):
        cx = 120 + i * 253
        d += _cook(cx, 210, hat=False)
        d += t(cx, 330, name, "bd", "middle")
        x, y = cx - w // 2, 190 - h
        d += f'<rect class="{"bxs" if i == 0 else "hz"}" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/>'
        d += t(cx, y + 26, lines, "sm", "middle")
        if i < 3:
            d += a(cx + 40, 270, cx + 213, 270)
    d += t(500, 365, "the refund goes out wrong, and no error is logged anywhere", "sm", "middle")
    return figure(1000, 380, d,
                  "Four people in a line: Priya, then agents 1, 2 and 3. Above each is the note they hold. Priya's note says refund order 4417, not the gift wrap, needed by Friday because she travels Saturday. Each later note is shorter, until the last says only refund order 4417.",
                  "A hand-off losing context. Nothing errors; the last agent just does the wrong thing confidently.")


def drawing_middle():
    b, a, t = kit.box, kit.arrow, kit.text
    d = b(10, 150, 150, 70, "A request", "from a person", "bxm")
    d += a(162, 185, 218, 185)
    d += b(220, 130, 170, 110, "Router", ["plain rules,", "no model"], "bxs")
    paths = [("Human desk", "someone was hurt", "bx", 20),
             ("Fixed refusal", "written in advance", "bx", 110),
             ("Direct answer", "one read, no model", "bx", 200)]
    for name, sub, k, y in paths:
        d += b(470, y, 200, 70, name, sub, k)
        d += a(392, 185, 468, y + 35)
    d += b(470, 300, 200, 80, "One agent", "one loop, all context", "solid")
    d += a(392, 200, 468, 330)
    tools = [("Lookup tool", "claims system"), ("Sub-call", "summarise a file"), ("Payout tool", "checked first")]
    for i, (name, sub) in enumerate(tools):
        y = 140 + i * 85
        d += b(770, y, 210, 70, name, sub, "bx" if i != 1 else "bxm")
        d += a(672, 340, 768, y + 35)
    d += t(875, 125, "SPECIALISTS ARE TOOLS", "lbl", "middle")
    d += t(305, 290, ["four paths, asked", "in a fixed order"], "sm", "middle")
    return figure(1000, 400, d,
                  "A request goes to a router made of plain rules. The router sends it to one of four paths: a human desk, a fixed refusal, a direct answer with no model, or one agent. The one agent has three specialist tools: a lookup tool, a sub-call that summarises a file, and a payout tool that is checked first.",
                  "The middle path. The router sends the easy and the risky cases away; the one agent keeps all the context and calls specialists as tools.")


def drawing_decide():
    b, a, t = kit.box, kit.arrow, kit.text
    qs = [("Different permissions or teams?", "or truly different skills"),
          ("Independent pieces of work?", "none needs another's result"),
          ("Too big for one context window?", "more than the model can read")]
    picks = [("Split on that line only", "a typed ticket at the boundary", "bx"),
             ("Parallel workers", "each reports back to one place", "bx"),
             ("Sub-agents read slices", "each sends back a summary", "bx")]
    d = ""
    for i, ((q1, q2), (pn, ps, k)) in enumerate(zip(qs, picks)):
        y = 20 + i * 120
        d += b(20, y, 380, 80, f"{i + 1}. {q1}", q2, "bxs")
        d += a(402, y + 40, 600, y + 40, "yes", lx=500, ly=y + 30)
        d += b(605, y, 375, 80, pn, ps, k)
        if i < 2:
            d += a(210, y + 82, 210, y + 118, "no", lx=232, ly=y + 106, anchor="start")
    y = 380
    d += a(210, 342, 210, y - 2, "no", lx=232, ly=364, anchor="start")
    d += b(20, y, 960, 72, "One agent with a router and good tools", "split later, once a trace shows where the boundary belongs", "solid")
    return figure(1000, 465, d,
                  "Three questions down the left. One: different permissions, teams or skills? Yes means split on that line only. Two: independent pieces of work? Yes means parallel workers that report to one place. Three: too big for one context window? Yes means sub-agents that each read a slice. If all three are no: one agent with a router and good tools.",
                  "Three questions, asked in order. Most projects reach the bottom box.")


def drawing_card():
    b, t = kit.box, kit.text
    d = '<rect class="hz" x="150" y="10" width="700" height="370" rx="16"/>'
    d += t(500, 48, "IF YOU GO MULTI-AGENT", "lbl", "middle")
    items = [("Complete hand-offs", "a typed ticket, tested", "AAC-0062"),
             ("One budget for all", "tokens, steps and money", "AAC-0064"),
             ("Loop detection", "the harness counts hand-offs", "AAC-0063"),
             ("One trace, per agent", "cost and time on each part", "AAC-0067"),
             ("Contain failure", "worse, never corrupt or hung", "AAC-0065")]
    for i, (name, sub, ref) in enumerate(items):
        y = 70 + i * 60
        d += f'<rect class="bxs" x="190" y="{y + 8}" width="28" height="28" rx="5"/>'
        d += f'<path class="lnc" d="M196,{y + 22} L203,{y + 30} L214,{y + 12}"/>'
        d += t(240, y + 28, name, "bd", "start")
        d += t(480, y + 28, sub, "tx", "start")
        d += t(820, y + 28, ref, "sm", "end")
    # shield
    d += ('<path class="pf pf-solid" d="M915,150 L960,165 Q960,230 915,255 Q870,230 870,165 Z"/>'
          '<path class="hz" d="M915,160 L950,172 Q950,225 915,245 Q880,225 880,172 Z"/>'
          '<path class="lnc" d="M898,205 L911,218 L933,190"/>')
    return figure(1000, 390, d,
                  "A safety card with five ticked items: complete hand-offs with a typed ticket, one budget for all agents, loop detection by the harness, one trace with cost and time per agent, and containing one agent's failure. Each names its catalog obligation. A small shield sits beside the card.",
                  "Five rules if you split. Each one is an obligation in the AI Assurance Catalog, with a test behind it.")


DRAWINGS = {"multi-cooks": drawing_cooks, "multi-handoff": drawing_handoff, "multi-middle": drawing_middle,
            "multi-decide": drawing_decide, "multi-card": drawing_card}
