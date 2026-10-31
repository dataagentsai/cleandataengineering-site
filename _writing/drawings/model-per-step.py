"""Drawings for 'There is no best model, only the best model for this step'. Globals kit, figure, E, ROOT are injected."""


def drawing_mdl_toolbox():
    b, t = kit.box, kit.text
    d = t(500, 26, "nobody asks which tool is best; they ask which tool fits this job", "sm", "middle")
    # the hammer
    d += '<rect class="hz" x="145" y="70" width="16" height="120" rx="4"/>'
    d += '<path class="hz" d="M108,52 L198,52 L198,82 L108,82 Q96,67 108,52 Z"/>'
    # the screwdriver
    d += '<rect class="hz" x="484" y="58" width="32" height="70" rx="12"/>'
    d += '<line class="ln" x1="494" y1="68" x2="494" y2="118"/><line class="ln" x1="506" y1="68" x2="506" y2="118"/>'
    d += '<rect class="hz" x="495" y="128" width="10" height="50" rx="2"/>'
    d += '<path class="hz" d="M495,178 L505,178 L502,192 L498,192 Z"/>'
    # the tweezers
    d += '<path class="hz" d="M832,56 L846,56 L852,190 L846,190 Z"/>'
    d += '<path class="hz" d="M868,56 L854,56 L848,190 L854,190 Z"/>'
    d += '<rect class="hz" x="830" y="52" width="40" height="12" rx="4"/>'
    jobs = [(30, "The hammer", ["the strong model:", "the one hard step"], "solid"),
            (380, "The screwdriver", ["a small fast model:", "routing, extraction"], "bx"),
            (730, "The tweezers", ["plain code: exact", "lookups and checks"], "bxs")]
    for x, n, s, k in jobs:
        d += b(x, 215, 240, 90, n, s, k)
    return figure(1000, 320, d, "Three tools drawn side by side: a hammer labelled the strong model for the one hard step, a screwdriver labelled a small fast model for routing and extraction, and tweezers labelled plain code for exact lookups and checks.",
                  "A toolbox, not a trophy. Each tool is the best one for a different job.")


def drawing_mdl_turn():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(500, 24, "one turn of a claims agent, and who does the work at each step", "sm", "middle")
    steps = [("A message", ["\"Is my claim", "covered?\""], "bxm", ""),
             ("Route it", ["rules first,", "small model if unsure"], "bx", "no model, or small"),
             ("Pull out facts", ["claim number,", "date, amount"], "bx", "small model"),
             ("Decide", ["read the policy,", "weigh the case"], "solid", "strong model"),
             ("Check, reply", ["limits, grounding,", "the template"], "bxs", "plain code")]
    for i, (n, s, k, who) in enumerate(steps):
        x = 10 + i * 198
        d += b(x, 60, 180, 100, n, s, k)
        if i < 4:
            d += a(x + 182, 110, x + 196, 110)
        if who:
            d += t(x + 90, 190, who, "bd", "middle")
    # coins under each worker
    coins = [0, 0, 1, 4, 0]
    for i, c in enumerate(coins):
        cx = 100 + i * 198
        if i == 0:
            continue
        if c == 0:
            d += t(cx, 230, "about free", "sm", "middle")
        for j in range(c):
            d += f'<ellipse class="hz" cx="{cx}" cy="{238 - j * 9}" rx="22" ry="7"/>'
    d += t(500, 280, "a known claim number skips the model entirely: 104 ms, no model call", "sm", "middle")
    return figure(1000, 295, d, "Five steps in a row: a message, route it with rules or a small model, pull out facts with a small model, decide with a strong model, check and reply with plain code. Coin stacks under each step are empty except one coin for extraction and four for the decision.",
                  "One turn, several workers. Only the decide step pays for the strong model.")


def drawing_mdl_dials():
    t = kit.text
    import math
    dials = [("Accuracy", "passes your cases", 0.8), ("Cost", "per task, not per token", 0.35),
             ("Speed", "time to the answer", 0.55), ("Reliability", "valid output, calls let in", 0.7)]
    d = t(500, 26, "turn one dial up and another usually moves down", "sm", "middle")
    for i, (n, s, v) in enumerate(dials):
        cx, cy, r = 125 + i * 250, 170, 85
        d += f'<path class="hz" d="M{cx - r},{cy} A{r},{r} 0 0 1 {cx + r},{cy} Z"/>'
        for k in range(5):
            ang = math.pi - k * math.pi / 4
            x1, y1 = cx + (r - 12) * math.cos(ang), cy - (r - 12) * math.sin(ang)
            x2, y2 = cx + r * math.cos(ang), cy - r * math.sin(ang)
            d += f'<line class="ln" x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}"/>'
        ang = math.pi - v * math.pi
        nx, ny = cx + (r - 22) * math.cos(ang), cy - (r - 22) * math.sin(ang)
        d += f'<line class="lnc" x1="{cx}" y1="{cy}" x2="{nx:.0f}" y2="{ny:.0f}"/><circle class="hk" cx="{cx}" cy="{cy}" r="6"/>'
        d += t(cx, cy + 32, n, "bd", "middle") + t(cx, cy + 54, s, "sm", "middle")
    return figure(1000, 245, d, "Four dials in a row: accuracy (passes your cases), cost (per task, not per token), speed (time to the answer) and reliability (valid output, calls not refused), each with a needle at a different point.",
                  "The four dials. You set them per step, not once for the whole agent.")


def drawing_mdl_scorecard():
    t = kit.text
    cols = ["Small model", "Strong model", "Plain code"]
    rows = [("Route the message", ["✓", "✓", "✓"]), ("Pull out the claim number", ["✓", "✓", "✓"]),
            ("Decide if it is covered", ["✗", "✓", "—"]), ("Write the reply", ["✓", "✓", "—"])]
    x0, y0, cw, rh, lw = 60, 70, 210, 44, 250
    w = lw + cw * 3
    d = t(500, 30, "a made-up example card: your tasks down the side, candidate models across", "sm", "middle")
    d += f'<rect class="hz" x="{x0}" y="{y0}" width="{w}" height="{rh * 7}" rx="10"/>'
    for j, c in enumerate(cols):
        d += t(x0 + lw + cw * j + cw / 2, y0 + 28, c, "bd", "middle")
    d += t(x0 + 16, y0 + 28, "TASK", "lbl")
    for i, (task, marks) in enumerate(rows):
        y = y0 + rh * (i + 1)
        d += f'<line class="ln" x1="{x0}" y1="{y}" x2="{x0 + w}" y2="{y}"/>'
        d += t(x0 + 16, y + 28, task, "tx")
        for j, m in enumerate(marks):
            cx = x0 + lw + cw * j + cw / 2
            if m == "✓" and ((i in (0, 1) and j == 2) or (i == 3 and j == 0) or (i == 2 and j == 1)):
                d += f'<rect class="bxs" x="{cx - 70}" y="{y + 8}" width="140" height="28" rx="6"/>'
            d += t(cx, y + 28, m, "bd", "middle")
    y = y0 + rh * 5
    d += f'<line class="lnc" x1="{x0}" y1="{y}" x2="{x0 + w}" y2="{y}"/>'
    for i, (n, vals) in enumerate([("Cost per task", ["low", "high", "about $0"]), ("Time per task", ["fast", "slower", "ms"])]):
        yy = y + rh * i
        d += t(x0 + 16, yy + 28, n, "sm")
        for j, v in enumerate(vals):
            d += t(x0 + lw + cw * j + cw / 2, yy + 28, v, "sm", "middle")
    for j in range(1, 3 + 1):
        x = x0 + lw + cw * (j - 1)
        d += f'<line class="lnd" x1="{x}" y1="{y0}" x2="{x}" y2="{y0 + rh * 7}"/>'
    d += t(500, y0 + rh * 7 + 30, "pick the cheapest column that passes each row (highlighted)", "sm", "middle")
    return figure(1000, y0 + rh * 7 + 45, d, "A scorecard with four task rows (route the message, pull out the claim number, decide if it is covered, write the reply) and three columns (small model, strong model, plain code). Ticks and crosses mark which pass; the cheapest passing cell in each row is highlighted. Two bottom rows show cost and time per task.",
                  "The scorecard. Rows are your tasks, columns are candidates, and the winner is chosen row by row.")


DRAWINGS = {"mdl-toolbox": drawing_mdl_toolbox, "mdl-turn": drawing_mdl_turn,
            "mdl-dials": drawing_mdl_dials, "mdl-scorecard": drawing_mdl_scorecard}
