"""Drawings for 'What one conversation costs: under a tenth of a cent'. Globals kit, figure, E, ROOT are injected."""
import math


def _pt(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def _wedge(cx, cy, r, a1, a2, cls):
    x1, y1 = _pt(cx, cy, r, a1)
    x2, y2 = _pt(cx, cy, r, a2)
    return f'<path class="{cls}" d="M{cx:.1f},{cy:.1f} L{x1:.1f},{y1:.1f} A{r},{r} 0 0,1 {x2:.1f},{y2:.1f} Z"/>'


def drawing_conv_coin():
    b, t, p = kit.box, kit.text, kit.path
    cx, cy, r = 260, 215, 150
    d = ""
    # nine slices stay in the coin, one slice is pulled out
    for i in range(1, 10):
        d += _wedge(cx, cy, r, -90 + i * 36, -54 + i * 36, "hz")
    d += f'<circle class="ln" cx="{cx}" cy="{cy}" r="{r - 22}" style="fill:none;stroke-dasharray:4 6"/>'
    ox, oy = _pt(0, 0, 34, -72)
    sx, sy = cx + ox, cy + oy
    d += _wedge(sx, sy, r, -90, -54, "pf pf-bxs")
    d += _wedge(sx, sy, r, -90, -90 + 36 * 0.87, "pf pf-solid")
    d += _wedge(sx, sy, r, -90, -54, "ln")
    d += t(cx, cy + r + 34, "one US cent, cut into ten", "bd", "middle")
    # labels on the right
    px, py = _pt(sx, sy, r + 6, -76)
    d += b(560, 20, 400, 90, "Rohan's conversation", ["$0.00087, about 7 paise", "(at an assumed ₹85 to the dollar)"], "solid")
    d += p(f"M558,60 Q{px + 120:.0f},{py - 30:.0f} {px + 4:.0f},{py:.0f}", "ln")
    qx, qy = _pt(sx, sy, 105, -56)
    d += b(560, 140, 400, 76, "The whole slice: a tenth of a cent", "$0.001", "bxs")
    d += p(f"M558,180 Q450,150 {qx + 6:.0f},{qy:.0f}", "lnd")
    d += b(560, 260, 400, 76, "A thousand of them", "87 US cents", "bx")
    return figure(1000, 410, d,
                  "A cartoon coin, one US cent, cut into ten slices. One slice is pulled out: the whole slice is a tenth of a cent, $0.001, and most of it is shaded as Rohan's conversation, $0.00087, about 7 paise at an assumed ₹85 to the dollar. A box beside it says a thousand such conversations cost 87 US cents.",
                  "One real conversation fits inside a tenth of a cent, with room to spare.")


def drawing_conv_bar():
    t = kit.text
    # shares from each trip's token counts (672/50, 855/239, 956/270) at $0.15 and $0.75 per million
    trips = [("Trip 1", ["reads the", "claim"], 138.3, "bx"),
             ("Trip 2", ["tries the planted", "payout: refused"], 307.5, "bxs"),
             ("Trip 3", ["writes the", "answer"], 345.9, "solid")]
    total = sum(x[2] for x in trips)
    d = t(500, 28, "ROHAN'S CONVERSATION: $0.00087 ON THE METER", "lbl", "middle")
    x = 50
    for name, what, v, cls in trips:
        w = 900 * v / total
        d += f'<rect class="{cls}" x="{x:.0f}" y="60" width="{w - 4:.0f}" height="64" rx="6"/>'
        d += t(x + w / 2, 99, name, "bd", "middle")
        d += t(x + w / 2, 154, what, "tx", "middle")
        d += t(x + w / 2, 202, f"about {round(100 * v / total)}%", "sm", "middle")
        x += w
    d += t(500, 240, "each trip rereads everything before it, so each costs a little more", "sm", "middle")
    return figure(1000, 260, d,
                  "One bar split into three trips to the model. Trip 1 reads the claim, about 17% of the cost. Trip 2 tries the planted payout and is refused, about 39%. Trip 3 writes the answer, about 44%. The meter's total for the conversation was $0.00087.",
                  "Where the money in one conversation goes. Shares are worked out from each trip's token counts; the total is the assistant's own meter.")


def drawing_conv_budget():
    b, t, p = kit.box, kit.text, kit.path
    parts = [("Model bill", "", 4, "solid"),
             ("Platform", ["hosting,", "monitoring"], 16, "bx"),
             ("Upkeep", ["tests, safety", "rules"], 20, "bx"),
             ("Review", ["checking its", "work"], 25, "bxs"),
             ("People", ["owners, hand-offs", "from the assistant"], 35, "bxs")]
    d = t(500, 26, "EXAMPLE PROPORTIONS, NOT DATA: WHERE AN AI BUDGET GOES", "lbl", "middle")
    x = 40
    for name, sub, share, kind in parts:
        w = 920 * share / 100
        if share < 10:
            d += f'<rect class="{kind}" x="{x:.0f}" y="120" width="{w - 6:.0f}" height="110" rx="6"/>'
            d += p(f"M{x + 60:.0f},78 Q{x + 40:.0f},88 {x + w / 2:.0f},116", "ln")
            d += t(x + 68, 74, "the model bill: the part everyone asks about", "bd", "start")
        else:
            d += b(x, 120, w - 8, 110, name, sub, kind)
        x += w
    # a little stick person above the people box
    px, py = 905, 66
    d += f'<circle class="hz" cx="{px}" cy="{py}" r="9"/>'
    d += f'<path class="ln" d="M{px},{py + 9} L{px},{py + 30} M{px - 12},{py + 17} L{px + 12},{py + 17} M{px},{py + 30} L{px - 9},{py + 44} M{px},{py + 30} L{px + 9},{py + 44}"/>'
    d += t(885, 92, "the biggest slice", "sm", "end")
    return figure(1000, 250, d,
                  "A bar of example proportions, not data, showing where an AI budget goes: a thin sliver for the model bill, then larger blocks for platform (hosting, monitoring), upkeep (tests, safety rules), review (checking its work) and the biggest, people (owners, hand-offs from the assistant).",
                  "The real budget. The model bill is a sliver; people, review, upkeep and platform are most of it. Example proportions only.")


DRAWINGS = {
    "conv-coin": drawing_conv_coin,
    "conv-bar": drawing_conv_bar,
    "conv-budget": drawing_conv_budget,
}
