"""Drawings for 'Why your agent costs $4 per question: 9 cost mistakes'. Globals kit, figure, E, ROOT are injected."""


def drawing_cost_taxi():
    b, a, t, p = kit.box, kit.arrow, kit.text, kit.path
    d = b(20, 90, 170, 80, "The model", ["reads the whole", "context again"], "solid")
    d += a(192, 130, 218, 130)
    d += b(220, 90, 150, 80, "A tool", "runs", "bx")
    d += a(372, 130, 398, 130)
    d += b(400, 90, 150, 80, "The result", "goes back in", "bx")
    d += p("M475,172 Q290,265 105,172") + t(290, 258, "round again: trip 2, trip 3, up to trip 16", "sm", "middle")
    d += a(552, 130, 636, 160, "fare", lx=596, ly=128)
    # the taxi
    d += '<path class="hz" d="M700,150 L732,102 L868,102 L900,150 Z"/>'
    d += '<rect class="hz" x="640" y="150" width="320" height="70" rx="18"/>'
    d += '<path class="ln" d="M745,145 L760,112 L795,112 L795,145 Z"/><path class="ln" d="M810,145 L810,112 L845,112 L862,145 Z"/>'
    d += '<line class="ln" x1="802" y1="155" x2="802" y2="212"/>'
    for cx in (710, 890):
        d += f'<circle class="hz" cx="{cx}" cy="222" r="24"/><circle class="hk" cx="{cx}" cy="222" r="6"/>'
    d += '<rect class="bxs" x="745" y="52" width="110" height="44" rx="6"/>' + t(800, 81, "$3.99", "bd", "middle")
    d += '<line class="ln" x1="790" y1="96" x2="790" y2="102"/><line class="ln" x1="810" y1="96" x2="810" y2="102"/>'
    d += t(800, 30, "the meter", "sm", "middle")
    d += t(800, 280, "it ticks on every trip, not on every answer", "sm", "middle")
    return figure(1000, 295, d, "An agent loop of three boxes: the model reads the whole context again, a tool runs, the result goes back in, and round again up to trip 16. Each trip feeds a taxi meter that reads $3.99.",
                  "An agent is a taxi with the meter running. Every trip round the loop is another fare. (Made-up example.)")


def drawing_cost_where():
    t = kit.text
    scale = 900 / 3.99
    parts = [("solid", 3.36), ("bxs", 0.39), ("bx", 0.24)]
    d = t(500, 26, "one question, $3.99 in total (a made-up example)", "bd", "middle")
    x = 50
    xs = []
    for cls, usd in parts:
        w = usd * scale
        d += f'<rect class="{cls}" x="{x:.0f}" y="80" width="{w:.0f}" height="60" rx="4"/>'
        xs.append((x, w))
        x += w
    ix, iw = xs[0]
    d += t(ix + iw / 2, 172, "input: re-reading the context, $3.36", "tx", "middle")
    d += t(ix + iw / 2, 194, "16 steps, 1,120,000 tokens", "sm", "middle")
    rx, rw = xs[1]
    d += t(rx + rw / 2, 66, "one retry, $0.39", "sm", "middle")
    d += t(950, 172, "the answers, $0.24", "tx", "end")
    d += t(950, 194, "16,000 tokens", "sm", "end")
    return figure(1000, 215, d, "A stacked bar for one question costing $3.99: input tokens $3.36, one retry $0.39, output tokens $0.24.",
                  "Where the money went. Input tokens dominate; the model's actual answers are a sliver at the end. Example prices: $3 per million tokens in, $15 out.")


def drawing_cost_snowball():
    t = kit.text
    base, ph, rh = 340, 20, 16
    steps = [(1, 60), (2, 190), (3, 320), (4, 450), (5, 580), (16, 820)]
    d = t(500, 24, "each step sends everything again: the prompt plus every tool result so far", "sm", "middle")
    d += '<rect class="bx" x="40" y="50" width="22" height="14" rx="3"/>' + t(70, 62, "prompt and tools, 10,000 tokens", "sm")
    d += '<rect class="bxs" x="40" y="74" width="22" height="14" rx="3"/>' + t(70, 86, "one tool result, 8,000 tokens", "sm")
    for k, x in steps:
        y = base - ph
        d += f'<rect class="bx" x="{x}" y="{y}" width="90" height="{ph}" rx="3"/>'
        for _ in range(k - 1):
            y -= rh
            d += f'<rect class="bxs" x="{x}" y="{y}" width="90" height="{rh}" rx="3"/>'
        d += t(x + 45, base + 22, f"step {k}", "tx", "middle")
        d += t(x + 45, base + 42, f"{10 + 8 * (k - 1)},000 sent", "sm", "middle")
    d += t(720, base - 30, "and so on", "sm", "middle")
    d += '<line class="lnd" x1="680" y1="345" x2="760" y2="345"/>'
    return figure(1000, 395, d, "Columns for steps 1 to 5 and step 16. Each column is the prompt plus one more tool result than the last: 10,000 tokens sent at step 1, 42,000 at step 5, 130,000 at step 16.",
                  "The context snowball. Nothing is ever dropped, so the last step reads thirteen times what the first did.")


def drawing_cost_right_model():
    b, a, t = kit.box, kit.arrow, kit.text
    d = b(10, 120, 150, 80, "A question", "", "bxm")
    d += a(162, 160, 193, 160)
    d += b(195, 110, 190, 100, "The router", ["a rule, or a", "small model"], "bxs")
    outs = [(10, "Plain code", ["a status lookup", "104 ms, $0"], "bx", 0),
            (120, "Small model", ["the simple steps", "cheap per token"], "bx", 1),
            (230, "Big model", ["the one hard step", "only when needed"], "solid", 4)]
    for y, n, s, k, coins in outs:
        d += a(387, 160, 468, y + 40)
        d += b(470, y, 220, 80, n, s, k)
        for j in range(coins):
            d += f'<ellipse class="hz" cx="760" cy="{y + 58 - j * 9}" rx="22" ry="7"/>'
        if coins == 0:
            d += t(760, y + 46, "free", "sm", "middle")
    d += t(880, 40, ["what each", "step costs"], "sm", "middle")
    d += t(880, 170, ["most steps", "land here"], "sm", "middle")
    return figure(1000, 320, d, "A question goes to a router, which is a rule or a small model. It sends a status lookup to plain code for $0 in 104 ms, simple steps to a small model, and only the one hard step to the big model. Coin stacks grow from none to four.",
                  "The right worker for each step. Code first, a small model next, the big model only where it earns its price.")


def drawing_cost_budgets():
    t = kit.text
    layers = [(20, 20, 960, 320, "bx", "PER MONTH", "a budget with alerts, and a kill switch someone on call can flip", "tell a person, or switch off"),
              (60, 90, 880, 230, "bxs", "PER TASK", "steps, time and money: in our tutorial, 12 trips, 60 seconds or $0.50", "stop with a reason, hand over"),
              (100, 160, 800, 140, "bx", "PER STEP", "output tokens per call, and the size of each tool result", "cut and carry on")]
    d = ""
    for x, y, w, h, cls, name, what, then in layers:
        d += f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="16"/>'
        d += t(x + 16, y + 24, name, "lbl") + t(x + 16, y + 46, what, "sm")
        d += t(x + w - 16, y + 24, then, "bd", "end")
    # a small stop sign inside the inner box
    pts = " ".join(f"{500 + 30 * c},{250 + 30 * s}" for c, s in
                   [(-0.41, -1), (0.41, -1), (1, -0.41), (1, 0.41), (0.41, 1), (-0.41, 1), (-1, 0.41), (-1, -0.41)])
    d += f'<polygon class="hz" points="{pts}"/>' + t(500, 255, "STOP", "lbl", "middle")
    return figure(1000, 355, d, "Three nested budgets. Per month: a budget with alerts and a kill switch; tell a person or switch off. Per task: steps, time and money, 12 trips, 60 seconds or $0.50 in our tutorial; stop with a reason and hand over. Per step: output tokens and tool-result size; cut and carry on.",
                  "Budgets at three sizes. Each runaway is only visible at one of them, so you need all three.")


DRAWINGS = {"cost-taxi": drawing_cost_taxi, "cost-where": drawing_cost_where, "cost-snowball": drawing_cost_snowball,
            "cost-right-model": drawing_cost_right_model, "cost-budgets": drawing_cost_budgets}
