"""Drawings for 'Measuring agent ROI'. Globals kit, figure, E, ROOT are injected."""


def drawing_roi_scale():
    b, t = kit.box, kit.text
    d = ""
    # base and centre post
    d += '<path class="hz" d="M420,446 L580,446 L600,472 L400,472 Z"/>'
    d += '<rect class="hz" x="490" y="300" width="20" height="146" rx="3"/>'
    # the beam, level, with short posts up to two plates
    d += '<line class="lnc" x1="200" y1="300" x2="800" y2="300"/>'
    d += '<circle class="hz" cx="500" cy="300" r="12"/>'
    for cx in (200, 800):
        d += f'<rect class="hz" x="{cx - 8}" y="260" width="16" height="40" rx="3"/>'
        d += f'<rect class="hz" x="{cx - 150}" y="248" width="300" height="12" rx="5"/>'
    # cost pan
    d += t(200, 26, "COSTS", "lbl", "middle")
    costs = [("Model bill", "the part everyone sees", "bx"),
             ("Platform", "hosting, tracing, gateway", "bx"),
             ("People", "review, rework, upkeep", "solid")]
    for i, (name, sub, kind) in enumerate(costs):
        d += b(70, 40 + i * 70, 260, 62, name, sub, kind)
    # value pan
    d += t(800, 26, "VALUE", "lbl", "middle")
    value = [("Hours back", "for your team"),
             ("Fewer errors", "less rework, fewer reversals"),
             ("Happier customers", "faster answers, fewer complaints")]
    for i, (name, sub) in enumerate(value):
        d += b(670, 40 + i * 70, 260, 62, name, sub, "bxs")
    d += t(500, 150, ["weigh every", "item, on both", "sides"], "sm", "middle")
    return figure(1000, 486, d,
                  "A cartoon balance scale. On the left plate, costs: the model bill (the part everyone sees), the platform (hosting, tracing, gateway) and people (review, rework, upkeep). On the right plate, value: hours back for your team, fewer errors (less rework, fewer reversals) and happier customers (faster answers, fewer complaints).",
                  "ROI is a scale. Put every cost on one side and every kind of value on the other, not just the model bill against hours saved.")


def drawing_roi_before_after():
    b, t = kit.box, kit.text
    d = t(500, 26, "made-up example: the same 10,000 claims requests a month", "sm", "middle")
    base, top = 340, 80
    groups = [("Cost per completed task", "₹158", "₹97", 158, 97),
              ("Handler hours a month", "2,600", "1,300", 2600, 1300),
              ("Error and rework rate", "5%", "3%", 5, 3)]
    for i, (name, bv, av, bn, an) in enumerate(groups):
        c = 180 + i * 320
        full = base - top
        hb = full
        ha = full * an / bn
        d += b(c - 105, base - hb, 95, hb - 2, bv, "", "bx")
        d += b(c + 10, base - ha, 95, ha - 2, av, "", "solid")
        d += t(c - 57, base + 24, "before", "sm", "middle")
        d += t(c + 57, base + 24, "after", "sm", "middle")
        d += t(c, base + 54, name, "bd", "middle")
    d += '<line class="ln" x1="40" y1="340" x2="960" y2="340"/>'
    return figure(1000, 410, d,
                  "Three pairs of bars, before and after the agent, on a made-up example of the same 10,000 claims requests a month. Cost per completed task falls from ₹158 to ₹97. Handler hours a month fall from 2,600 to 1,300. The error and rework rate falls from 5% to 3%.",
                  "Before and after, on the same tasks. Example numbers only: measure your own baseline first.")


def drawing_roi_iceberg():
    b, t = kit.box, kit.text
    d = '<rect class="pf pf-bx" x="20" y="150" width="960" height="330" rx="8"/>'
    # the iceberg: a small tip above the water, a big body below
    d += ('<path class="hz" d="M425,150 L455,92 L492,62 L530,80 L552,112 L575,150 '
          'L880,212 L925,362 L780,470 L220,470 L75,362 L120,212 Z"/>')
    # the water line
    w = "M20,150"
    for x in range(60, 1000, 40):
        w += f" Q{x - 20},{142 if (x // 40) % 2 else 158} {x},150"
    d += f'<path class="ln" d="{w}"/>'
    d += t(600, 84, "Model bill: ₹30,000", "bd", "start")
    d += t(600, 108, "the part in the pilot report", "sm", "start")
    d += t(400, 96, "ABOVE THE WATER", "lbl", "end")
    hidden = [("Review and rework", "checking and fixing its work"),
              ("Upkeep", "tests and safety rules"),
              ("On-call", "someone awake at 2 a.m."),
              ("Price changes", "the model bill can double")]
    for i, (name, sub) in enumerate(hidden):
        x = 200 + (i % 2) * 320
        y = 225 + (i // 2) * 100
        d += b(x, y, 280, 80, name, sub, "bxm" if i == 3 else "bxs")
    d += t(500, 450, "BELOW THE WATER: RARELY IN THE PILOT REPORT", "lbl", "middle")
    return figure(1000, 490, d,
                  "An iceberg. Above the water is a small tip, the model bill of ₹30,000, the part in the pilot report. Below the water is a much bigger body holding review and rework, upkeep of tests and safety rules, on-call, and model price changes.",
                  "The model bill is the tip. In the example it was about 3% of the monthly cost.")


def drawing_roi_scorecard():
    t = kit.text
    d = '<rect class="hz" x="130" y="16" width="740" height="500" rx="10"/>'
    d += t(500, 50, "AGENT SCORECARD: ONE SLICE, FOUR WEEKS", "lbl", "middle")
    d += t(170, 86, "measure", "sm") + t(580, 86, "before", "sm", "middle")
    d += t(690, 86, "after", "sm", "middle") + t(800, 86, "better?", "sm", "middle")
    rows = [("Cost per completed task", "₹158", "₹97", "y"),
            ("Handler hours a month", "2,600", "1,300", "y"),
            ("Error and rework rate", "5%", "3%", "y"),
            ("Review time a month", "none", "200 hours", "c"),
            ("Time to resolution", "2 days", "1 day", "y"),
            ("Complaints a month", "120", "110", "y"),
            ("Reversed payouts a month", "40", "55", "n"),
            ("Upkeep a month", "none", "₹1 lakh", "c")]
    for i, (name, bv, av, mark) in enumerate(rows):
        y = 100 + i * 44
        d += t(170, y + 28, name, "tx")
        d += t(580, y + 28, bv, "tx", "middle") + t(690, y + 28, av, "tx", "middle")
        bx, by = 788, y + 10
        d += f'<rect class="hz" x="{bx}" y="{by}" width="24" height="24" rx="3"/>'
        if mark == "y":
            d += f'<path class="lnc" d="M{bx + 5},{by + 13} L{bx + 10},{by + 19} L{bx + 20},{by + 5}"/>'
        elif mark == "n":
            d += (f'<path class="lnc" d="M{bx + 6},{by + 6} L{bx + 18},{by + 18}"/>'
                  f'<path class="lnc" d="M{bx + 18},{by + 6} L{bx + 6},{by + 18}"/>')
        else:
            d += t(bx + 12, by + 18, "+", "bd", "middle")
        d += f'<line class="lnd" x1="160" y1="{y + 44}" x2="840" y2="{y + 44}"/>'
    d += t(500, 492, "Decision: scale once the extra reversals are explained.", "bd", "middle")
    return figure(1000, 530, d,
                  "A one-page scorecard for one slice of work over four weeks, with made-up example numbers, before and after. Cost per completed task ₹158 to ₹97, better. Handler hours 2,600 to 1,300, better. Error and rework rate 5% to 3%, better. Review time none to 200 hours, a new cost counted. Time to resolution 2 days to 1 day, better. Complaints 120 to 110, better. Reversed payouts 40 to 55, worse. Upkeep none to ₹1 lakh, a new cost counted. Decision: scale once the extra reversals are explained.",
                  "One page, eight numbers, before and after (example numbers). A tick is better, a cross is worse, a plus is a new cost you must count.")


DRAWINGS = {
    "roi-scale": drawing_roi_scale,
    "roi-before-after": drawing_roi_before_after,
    "roi-iceberg": drawing_roi_iceberg,
    "roi-scorecard": drawing_roi_scorecard,
}
