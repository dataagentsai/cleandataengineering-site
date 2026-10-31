"""Drawings for 'Before it ships: offline evals for autonomous agents'.
kit, figure, E and ROOT are given as globals by build.py."""


def _person(cx, top):
    """A small stick person whose head centre is at (cx, top)."""
    return (f'<circle class="hz" cx="{cx}" cy="{top}" r="14"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 14}" x2="{cx}" y2="{top + 52}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 52}" x2="{cx - 12}" y2="{top + 76}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 52}" x2="{cx + 12}" y2="{top + 76}"/>')


def drawing_eval_driving_test():
    b, a, t, p = kit.box, kit.arrow, kit.text, kit.path
    d = t(500, 24, "a new prompt, model or tool is a new driver: it passes the test before it gets the keys", "sm", "middle")
    # the learner car with an L plate
    d += b(10, 70, 200, 110, "New release", ["new prompt, model", "or tool"], "solid")
    d += ('<rect class="hz" x="60" y="200" width="100" height="34" rx="10"/>'
          '<path class="hz" d="M78,200 L92,182 L130,182 L144,200 Z"/>'
          '<circle class="hz" cx="82" cy="238" r="9"/><circle class="hz" cx="138" cy="238" r="9"/>'
          '<rect class="hz" x="98" y="207" width="24" height="20" rx="2"/>')
    d += t(110, 223, "L", "bd", "middle")
    d += a(212, 125, 280, 125)
    # the test: route + examiner
    d += b(282, 60, 290, 130, "The driving test", ["golden cards, scenarios,", "checks on what it did"], "bxs")
    d += _person(640, 80)
    d += '<rect class="hz" x="656" y="104" width="30" height="38" rx="3"/>'
    d += ''.join(f'<line class="ln" x1="661" y1="{114 + k * 9}" x2="681" y2="{114 + k * 9}"/>' for k in range(3))
    d += t(640, 184, "the examiner:", "sm", "middle") + t(640, 202, "the release gate", "sm", "middle")
    d += a(700, 100, 780, 70, "pass")
    d += a(700, 150, 780, 205, "fail", ly=196)
    # keys
    d += b(782, 30, 210, 80, "The keys", "it ships", "bx")
    d += ('<circle class="hz" cx="840" cy="140" r="12"/>'
          '<line class="lnc" x1="852" y1="140" x2="900" y2="140"/>'
          '<line class="lnc" x1="890" y1="140" x2="890" y2="152"/><line class="lnc" x1="878" y1="140" x2="878" y2="150"/>')
    d += b(782, 170, 210, 80, "Back to practice", "fix it, test again", "bxm")
    d += p("M785,240 Q500,300 400,192", "lnd")
    return figure(1000, 285, d, "A new release, drawn as a learner car with an L plate, takes a driving test of golden cards, scenarios and checks on what it did. A stick-person examiner with a clipboard is the release gate. Pass leads to the keys and it ships; fail leads back to practice and round to the test again.",
                  "Offline evals are a driving test for every release. Something other than the agent marks the sheet.")


def drawing_eval_golden_cards():
    t, b = kit.text, kit.box
    d = ""
    # two cards behind, fanned up and to the right; their labels sit in the visible strip
    for k, day in ((2, "day 31"), (1, "day 29")):
        bx, by = 30 + k * 40, 56 - k * 20
        d += f'<rect class="hz" x="{bx}" y="{by}" width="440" height="240" rx="10"/>'
        d += t(bx + 430, by + 15, day, "sm", "end")
    # the front card
    x, y = 30, 56
    d += f'<rect class="pf pf-bxs" x="{x + 5}" y="{y + 5}" width="440" height="240" rx="10"/>'
    d += f'<rect class="hz" x="{x}" y="{y}" width="440" height="240" rx="10"/>'
    d += t(x + 20, y + 30, "golden case: returns-day-30", "bd") + t(x + 420, y + 30, "day 30", "sm", "end")
    d += f'<line class="lnd" x1="{x + 16}" y1="{y + 44}" x2="{x + 424}" y2="{y + 44}"/>'
    rows = [("QUESTION", "\"Refund my kurta, I returned it\""),
            ("WORLD BEFORE", "order returned 30 days ago, ₹3,499"),
            ("EXPECTED TOOL", "issue_refund, once"),
            ("EXPECTED OUTCOME", "one refund of ₹3,499"),
            ("SLICE", "returns, on the limit")]
    for j, (k, v) in enumerate(rows):
        yy = y + 76 + j * 34
        d += t(x + 20, yy, k, "lbl") + t(x + 180, yy, v, "tx")
    # the side notes
    d += b(600, 60, 380, 90, "One card per edge", ["the 30-day rule gets", "day 29, day 30 and day 31"], "bxs")
    d += b(600, 180, 380, 90, "Kept in Git, frozen", ["never edited to make", "a failing run pass"], "bx")
    return figure(1000, 310, d, "A stack of index cards. The front card is a golden case: the question 'refund my kurta, I returned it', the world before (returned 30 days ago, 3,499 rupees), the expected tool issue_refund once, the expected outcome one refund of 3,499 rupees, and the slice 'returns, on the limit'. Cards behind it test day 29 and day 31.",
                  "A golden set is a stack of cards with known right answers, and the edges of every rule get a card each.")


def drawing_eval_scoring():
    b, a, t = kit.box, kit.arrow, kit.text
    steps = [("Right tool?", ["did issue_refund", "actually run?"], "bx"),
             ("Right arguments?", ["this order,", "₹3,499 not ₹34,990"], "bx"),
             ("World right?", ["one refund, nothing", "else changed"], "bx"),
             ("LLM judge", ["grounded? tone?", "only what code can't"], "bxm")]
    d = t(500, 24, "ask in this order and stop at the first failure", "sm", "middle")
    for i, (title, sub, k) in enumerate(steps):
        x = 10 + i * 248
        d += b(x, 50, 222, 110, title, sub, k) + kit.num(x + 12, 50, i + 1)
        if i < 3:
            d += a(x + 224, 105, x + 246, 105)
    d += t(372, 200, "code: exact, free, same answer every time", "bd", "middle")
    d += '<path class="lnd" d="M20,180 L724,180"/>'
    d += '<path class="lnd" d="M758,180 L980,180"/>'
    d += t(869, 200, "a model: costs money, can be wrong", "sm", "middle")
    d += _person(830, 232)
    d += '<rect class="hz" x="852" y="250" width="28" height="34" rx="3"/>'
    d += t(890, 262, "checked against", "sm") + t(890, 282, "people's labels", "sm")
    return figure(1000, 320, d, "Four steps in a row, numbered. One, right tool: did issue_refund actually run? Two, right arguments: this order, 3,499 rupees not 34,990. Three, world right: one refund, nothing else changed. These three are code. Four, dashed, the LLM judge, for grounding and tone only, checked against labels from a person.",
                  "Code checks first, the judge last. The judge may only block once it agrees with people.")


def drawing_eval_baseline():
    t = kit.text
    slices = [("Refunds", 86, 88), ("Cancellations", 90, 91), ("Hindi messages", 84, 62), ("Over the limit", 80, 84)]
    base_y, scale = 230, 2.0
    d = t(500, 22, "same frozen set, run on both releases (illustrative heights)", "sm", "middle")
    for i, (name, old, new) in enumerate(slices):
        cx = 120 + i * 230
        ho, hn = old * scale, new * scale
        d += f'<rect class="pf pf-bx" x="{cx - 60}" y="{base_y - ho}" width="52" height="{ho}" rx="4"/>'
        d += f'<rect class="hz" x="{cx - 60}" y="{base_y - ho}" width="52" height="{ho}" rx="4" fill-opacity="0"/>'
        zone = "zr" if new < old - 5 else "pf pf-solid"
        d += f'<rect class="{zone}" x="{cx + 8}" y="{base_y - hn}" width="52" height="{hn}" rx="4"/>'
        d += f'<rect class="hz" x="{cx + 8}" y="{base_y - hn}" width="52" height="{hn}" rx="4" fill-opacity="0"/>'
        d += t(cx, base_y + 26, name, "tx", "middle")
        if new < old - 5:
            d += t(cx + 34, base_y - hn - 12, "worse", "bd", "middle")
    d += f'<line class="lnc" x1="20" y1="{base_y}" x2="980" y2="{base_y}"/>'
    d += f'<rect class="pf pf-bx" x="300" y="280" width="22" height="16" rx="3"/>' + t(330, 294, "last release", "sm")
    d += f'<rect class="pf pf-solid" x="470" y="280" width="22" height="16" rx="3"/>' + t(500, 294, "new release", "sm")
    d += t(640, 294, "the average barely moved", "sm")
    return figure(1000, 310, d, "Paired bars for four slices, last release against new release: refunds, cancellations and over-the-limit cases are about the same or better, but Hindi messages dropped sharply and are marked worse. The average barely moved.",
                  "Compare with the last release, slice by slice. The average hides the slice that broke.")


def drawing_eval_loop():
    b, t, p = kit.box, kit.text, kit.path
    steps = [("A miss in production", ["\"refunded\", but", "nothing was"], "bxm", (370, 15)),
             ("Replay the trace", ["find the step", "that went wrong"], "bx", (720, 140)),
             ("Write a new card", ["question, tool,", "outcome, slice"], "bxs", (370, 265)),
             ("The gate runs it", ["before every", "release, for ever"], "bx", (20, 140))]
    d = ""
    for title, sub, k, (x, y) in steps:
        d += b(x, y, 260, 95, title, sub, k)
    d += p("M632,60 C 720,60 850,85 850,136", "lnc")
    d += p("M850,237 C 850,300 740,312 634,312", "lnc")
    d += p("M368,312 C 260,312 150,300 150,237", "lnc")
    d += p("M150,138 C 150,85 270,60 366,60", "lnc")
    # a small stack of cards in the middle, growing
    for k in range(4):
        d += f'<rect class="hz" x="{455 + k * 8}" y="{160 - k * 8}" width="70" height="46" rx="5"/>'
    d += '<rect class="pf pf-bxs" x="479" y="136" width="70" height="46" rx="5"/>'
    d += t(514, 164, "+1", "bd", "middle")
    d += t(500, 232, "the golden set grows", "sm", "middle")
    return figure(1000, 375, d, "A loop of four: a miss in production (the agent said refunded but nothing was), replay the trace to find the wrong step, write a new card with question, tool, outcome and slice, and the gate runs it before every release. In the middle, a stack of cards gains one.",
                  "Every production failure becomes a new card, so the same mistake can't ship twice.")


DRAWINGS = {"eval-driving-test": drawing_eval_driving_test, "eval-golden-cards": drawing_eval_golden_cards,
            "eval-scoring": drawing_eval_scoring, "eval-baseline": drawing_eval_baseline,
            "eval-loop": drawing_eval_loop}
