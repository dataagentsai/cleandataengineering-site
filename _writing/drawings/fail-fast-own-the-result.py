"""Drawings for 'Fail fast, own the result'. Globals kit, figure, E, ROOT are injected."""


def drawing_ff_cost_curve():
    b, t, p = kit.box, kit.text, kit.path
    d = t(500, 22, "the same mistake, found on three different days", "sm", "middle")
    d += '<line class="ln" x1="80" y1="290" x2="940" y2="290"/><line class="ln" x1="80" y1="290" x2="80" y2="50"/>'
    d += t(90, 48, "cost of finding out you were wrong", "sm", "start")
    d += t(510, 318, "time on the job", "sm", "middle")
    d += p("M90,275 Q600,265 920,80", "lnc")
    for cx, cy in ((140, 274), (333, 259), (887, 98)):
        d += f'<circle class="hk" cx="{cx}" cy="{cy}" r="6"/>'
    d += b(100, 150, 190, 64, "Day 2", "a query on 100 rows", "bxs")
    d += '<line class="lnd" x1="170" y1="214" x2="142" y2="268"/>'
    d += b(300, 135, 220, 64, "Week 2", "rework one screen", "bx")
    d += '<line class="lnd" x1="380" y1="199" x2="336" y2="253"/>'
    d += b(540, 40, 250, 70, "Week 7", ["rebuild everything,", "and the customer's trust"], "solid")
    d += '<line class="lnd" x1="790" y1="80" x2="880" y2="96"/>'
    return figure(1000, 330, d,
                  "A rising curve: the cost of finding out you were wrong grows with time. On day 2 it costs a query on 100 rows; in week 2 it costs reworking one screen; in week 7 it costs rebuilding everything and the customer's trust.",
                  "Failing fast is not failing more. It is moving the same discovery to the left, where it is cheap.")


def drawing_ff_stilts():
    t = kit.text
    d = t(500, 22, "a plan stands on beliefs; nobody looks at them until one gives way", "sm", "middle")
    d += '<path class="hz" d="M250,70 L750,70 L750,180 L250,180 Z"/>'
    d += '<path class="ln" d="M250,70 L500,38 L750,70"/>'
    d += t(500, 115, "YOUR PLAN", "lbl", "middle")
    d += t(500, 145, "six weeks of careful, correct work", "sm", "middle")
    d += '<line class="lnc" x1="180" y1="180" x2="820" y2="180"/>'
    d += '<line class="ln" x1="60" y1="300" x2="940" y2="300"/>'
    labels = ["the problem is real", "the data exists", "the model can do it", "we can run in their cloud"]
    for i, (x, lab) in enumerate(zip((230, 410, 590, 770), labels)):
        if i == 1:  # the cracked one
            d += f'<line class="lnc" x1="{x}" y1="180" x2="{x}" y2="228"/>'
            d += f'<path class="ln" d="M{x - 9},228 L{x + 7},236 L{x - 7},244 L{x + 9},252"/>'
            d += f'<line class="lnd" x1="{x}" y1="254" x2="{x}" y2="300"/>'
            d += t(x + 18, 245, "nobody checked", "sm", "start")
        else:
            d += f'<line class="lnc" x1="{x}" y1="180" x2="{x}" y2="300"/>'
        d += t(x, 324, lab, "tx", "middle")
    return figure(1000, 345, d,
                  "A house labelled 'your plan' stands on four stilts: the problem is real, the data exists, the model can do it, we can run in their cloud. The stilt 'the data exists' is cracked, with a note: nobody checked.",
                  "Every plan stands on a few beliefs. Find them, and check the weakest one first.")


def drawing_ff_loop():
    b, t, p = kit.box, kit.text, kit.path
    d = b(360, 25, 280, 80, "1 Write the belief", "“this only works if…”", "bx")
    d += b(690, 140, 290, 85, "2 Cheapest test", ["that could prove", "the belief wrong"], "bxs")
    d += b(360, 260, 280, 80, "3 Kill line", "decided before you look", "bxs")
    d += b(20, 140, 290, 85, "4 Run it, then", ["keep, change", "or stop"], "bx")
    d += b(405, 148, 190, 70, "Days,", "not weeks", "solid")
    d += p("M640,65 Q790,65 830,136")
    d += p("M830,228 Q830,300 644,300")
    d += p("M358,300 Q165,300 165,229")
    d += p("M165,138 Q165,65 356,65")
    return figure(1000, 355, d,
                  "A loop of four steps: write the belief; find the cheapest test that could prove it wrong; set the kill line before you look; run it, then keep, change or stop. In the middle: days, not weeks.",
                  "The fail-fast loop. Step 3 is the one people skip, and it is the one that keeps you honest.")


def drawing_ff_matrix():
    b, t = kit.box, kit.text
    d = t(550, 22, "which belief to test first", "sm", "middle")
    d += '<rect class="zg" x="180" y="40" width="360" height="135" rx="8"/>'
    d += '<rect class="zy" x="560" y="40" width="360" height="135" rx="8"/>'
    d += '<rect class="hz" x="180" y="190" width="360" height="135" rx="8"/>'
    d += '<rect class="hz" x="560" y="190" width="360" height="135" rx="8"/>'
    d += t(360, 66, "TEST FIRST", "lbl", "middle") + t(740, 66, "PLAN A PROPER TEST", "lbl", "middle")
    d += t(360, 216, "JUST TRY IT", "lbl", "middle") + t(740, 216, "LEAVE FOR LATER", "lbl", "middle")
    d += b(200, 82, 155, 60, "Data exists", "pull 100 rows", "bxm")
    d += b(370, 82, 155, 60, "Users want it", "show a sketch", "bxm")
    d += b(600, 82, 280, 60, "Runs in their cloud", "ask security on day 1", "bxm")
    d += b(240, 232, 240, 60, "Button wording", "change it later", "bxm")
    d += b(600, 232, 280, 60, "Load at 10 times", "once it is in use", "bxm")
    d += t(95, 100, ["costly", "if wrong"], "sm", "middle") + t(95, 250, ["cheap", "if wrong"], "sm", "middle")
    d += t(360, 350, "quick to test", "sm", "middle") + t(740, 350, "slow to test", "sm", "middle")
    return figure(1000, 365, d,
                  "A two-by-two grid. Costly if wrong and quick to test: test first, for example whether the data exists or users want it. Costly if wrong and slow to test: plan a proper test, such as running in their cloud. Cheap if wrong and quick: just try it. Cheap if wrong and slow: leave for later.",
                  "Test first what would hurt most if wrong and costs least to check.")


def drawing_ff_where():
    b, t = kit.box, kit.text
    d = '<rect class="zg" x="30" y="30" width="450" height="240" rx="10"/>'
    d += '<rect class="zr" x="520" y="30" width="450" height="240" rx="10"/>'
    d += t(255, 60, "FAIL HERE, OFTEN", "lbl", "middle") + t(745, 60, "NEVER FAIL HERE", "lbl", "middle")
    for i, s in enumerate(["a notebook", "100 sample rows", "a paper sketch", "a test account"]):
        x, y = 55 + (i % 2) * 210, 85 + (i // 2) * 85
        d += b(x, y, 190, 65, s, "", "bxm")
    for i, s in enumerate(["customer data in production", "people's money", "the customer's trust"]):
        d += b(560, 82 + i * 62, 370, 52, s, "", "bxm")
    return figure(1000, 300, d,
                  "Two zones. Fail here, often: a notebook, 100 sample rows, a paper sketch, a test account. Never fail here: customer data in production, people's money, the customer's trust.",
                  "Fail fast in the cheap places so you never fail in the expensive one.")


DRAWINGS = {"ff-cost-curve": drawing_ff_cost_curve, "ff-stilts": drawing_ff_stilts, "ff-loop": drawing_ff_loop,
            "ff-matrix": drawing_ff_matrix, "ff-where": drawing_ff_where}
