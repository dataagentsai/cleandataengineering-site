"""Drawings for 'Human in the loop without humans in the way'. kit, figure, E and ROOT are injected."""
import math


def _person(cx, top, wave=False):
    """A small stick person; head centre at (cx, top + 13)."""
    s = (f'<circle class="bx" cx="{cx}" cy="{top + 13}" r="13"/>'
         f'<line class="lnc" x1="{cx}" y1="{top + 26}" x2="{cx}" y2="{top + 58}"/>'
         f'<line class="lnc" x1="{cx}" y1="{top + 58}" x2="{cx - 11}" y2="{top + 80}"/>'
         f'<line class="lnc" x1="{cx}" y1="{top + 58}" x2="{cx + 11}" y2="{top + 80}"/>'
         f'<line class="lnc" x1="{cx}" y1="{top + 36}" x2="{cx - 16}" y2="{top + 50}"/>')
    if wave:
        s += f'<line class="lnc" x1="{cx}" y1="{top + 36}" x2="{cx + 22}" y2="{top + 18}"/>'
    else:
        s += f'<line class="lnc" x1="{cx}" y1="{top + 36}" x2="{cx + 16}" y2="{top + 50}"/>'
    return s


def _cart(x, y, label):
    """A little cart: body 110 x 46 at (x, y), two wheels."""
    return (f'<rect class="hz" x="{x}" y="{y}" width="110" height="46" rx="8"/>'
            f'<circle class="hz" cx="{x + 24}" cy="{y + 52}" r="10"/><circle class="hz" cx="{x + 86}" cy="{y + 52}" r="10"/>'
            + kit.text(x + 55, y + 28, label, "sm", "middle"))


def drawing_toll_gate():
    t = kit.text
    d = ""
    # the road: two lanes
    d += '<line class="ln" x1="20" y1="110" x2="980" y2="110"/><line class="ln" x1="20" y1="270" x2="980" y2="270"/>'
    d += '<line class="lnd" x1="20" y1="190" x2="980" y2="190"/>'
    # booth lane (top): cart waiting at a raised barrier
    d += _cart(270, 125, "₹25,001")
    d += t(185, 140, ["waits,", "holding nothing"], "sm", "middle")
    d += '<rect class="hz" x="420" y="100" width="14" height="90" rx="3"/>'
    d += '<path class="hz" d="M427,112 L570,62 L574,74 L431,124 Z"/>'
    # booth beside the road, and Asha waving
    d += '<path class="hz" d="M600,30 L660,8 L720,30 Z"/><rect class="hz" x="610" y="30" width="100" height="70" rx="4"/>'
    d += '<rect class="bxs" x="628" y="44" width="64" height="30" rx="4"/>'
    d += _person(775, 18, wave=True)
    d += t(810, 34, "Asha", "bd")
    d += t(810, 62, ["one look, then", "waves it through"], "sm")
    # fast lane (bottom): cart going straight through
    d += _cart(560, 205, "₹8,000")
    d += kit.arrow(690, 231, 780, 231)
    d += t(800, 236, "green lane: no stop", "sm")
    return figure(1000, 285, d,
                  "A toll plaza with two lanes. In the top lane a cart carrying a ₹25,001 payout waits at a raised barrier while Asha, beside her booth, waves it through. In the bottom lane a cart carrying ₹8,000 drives straight on without stopping.",
                  "Most requests drive straight through. A few stop for one quick look from a person, and the cart holds nothing while it waits.")


def drawing_lanes():
    t = kit.text
    lanes = [("zg", "Green: runs alone", "claim status · a payout of ₹25,000 or less", "a rule decides, same turn"),
             ("zy", "Yellow: needs approval", "a payout above ₹25,000", "the agent pauses until a person decides"),
             ("zr", "Red: always a person", "someone was hurt · \"a person, please\"", "the agent hands off at once")]
    d = ""
    for i, (z, name, ex, what) in enumerate(lanes):
        y = 20 + i * 92
        d += f'<rect class="{z}" x="20" y="{y}" width="960" height="76" rx="14"/>'
        d += t(44, y + 32, name, "bd")
        d += t(44, y + 58, what, "sm")
        d += t(500, y + 45, ex, "tx")
    return figure(1000, 300, d,
                  "Three coloured lanes. Green, runs alone: claim status, a payout of ₹25,000 or less. Yellow, needs approval: a payout above ₹25,000. Red, always a person: someone was hurt, or the customer asks for a person.",
                  "Sort actions into lanes in code. The model can ask for anything; the harness decides which lane it goes in.")


def drawing_durable_wait():
    b, a, t, n = kit.box, kit.arrow, kit.text, kit.num
    d = ""
    d += b(10, 40, 200, 90, "The agent asks", ["request_payout", "₹25,001"], "bx") + n(22, 40, 1)
    d += a(212, 85, 262, 85)
    d += b(265, 40, 220, 90, "The workflow sleeps", ["state WAITING,", "one row in PostgreSQL"], "solid") + n(277, 40, 2)
    d += a(487, 85, 537, 85)
    d += b(540, 40, 200, 90, "Asha clicks", ["Approve, minutes", "or hours later"], "bxm") + n(552, 40, 3)
    d += a(742, 85, 792, 85)
    d += b(795, 40, 195, 90, "It wakes", ["re-reads the claim,", "pays once"], "bxs") + n(807, 40, 4)
    # crash and restart loop under the sleeping workflow
    d += '<rect class="hatch" x="265" y="185" width="220" height="60" rx="12"/>'
    d += t(375, 220, "the server restarts", "bd", "middle")
    d += kit.path("M330,132 Q300,160 320,183", "lnd")
    d += kit.path("M430,183 Q450,160 420,132", "lnd")
    d += t(510, 205, "on start-up DBOS finds the waiting workflow", "sm")
    d += t(510, 228, "and carries on from its last saved step", "sm")
    d += t(500, 280, "the turn ended at step 1: Rohan was told \"nothing has been paid yet\"", "sm", "middle")
    return figure(1000, 295, d,
                  "Four steps: the agent asks for a ₹25,001 payout; the workflow sleeps as one row in PostgreSQL; Asha clicks Approve later; the workflow wakes, re-reads the claim and pays once. Below the sleeping step, a server restart loops back to it.",
                  "The real flow 8. Nothing waits in memory, so a restart in the middle changes nothing.")


def drawing_card():
    t = kit.text
    d = ""
    # the card
    d += '<rect class="hz" x="200" y="20" width="600" height="300" rx="14"/>'
    d += t(230, 56, "Pay ₹25,001 to Rohan on claim CLM-010004", "bd")
    d += '<line class="ln" x1="220" y1="72" x2="780" y2="72"/>'
    rows = [("Why here", "above the automatic limit of ₹25,000"),
            ("The facts", "claim approved · assessor's note · paid to the account on his policy"),
            ("He said", "\"Please release the payment for claim CLM-010004\""),
            ("Expires", "in 24 hours; if nobody decides, nothing is paid")]
    for i, (k, v) in enumerate(rows):
        y = 104 + i * 40
        d += t(230, y, k.upper(), "lbl") + t(340, y, v, "sm")
    # buttons
    d += '<rect class="pf pf-bxs" x="230" y="262" width="150" height="40" rx="10"/><rect class="bxs ol" x="230" y="262" width="150" height="40" rx="10"/>'
    d += t(305, 288, "Approve", "bd", "middle")
    d += '<rect class="hz" x="400" y="262" width="150" height="40" rx="10"/>'
    d += t(475, 288, "Refuse, why?", "bd", "middle")
    # notes on the side
    d += t(30, 110, ["one line,", "plain words"], "sm")
    d += kit.path("M110,104 Q160,70 222,56", "lnd")
    d += t(830, 150, ["read fresh,", "not from", "the model"], "sm")
    d += kit.path("M826,150 Q805,145 785,145", "lnd")
    d += t(830, 280, ["decide in", "seconds"], "sm")
    return figure(1000, 335, d,
                  "An approval card. Title: pay ₹25,001 to Rohan on claim CLM-010004. Rows: why here, the facts, what he said, when it expires. Two buttons: Approve, and Refuse with a reason.",
                  "What a good approval card shows. If it takes more than a few seconds to decide, the card is the problem.")


def drawing_dial():
    t = kit.text
    cx, cy, r = 300, 250, 190
    d = ""

    def arc(a0, a1, cls):
        x0, y0 = cx + r * math.cos(math.radians(a0)), cy - r * math.sin(math.radians(a0))
        x1, y1 = cx + r * math.cos(math.radians(a1)), cy - r * math.sin(math.radians(a1))
        xi1, yi1 = cx + (r - 50) * math.cos(math.radians(a1)), cy - (r - 50) * math.sin(math.radians(a1))
        xi0, yi0 = cx + (r - 50) * math.cos(math.radians(a0)), cy - (r - 50) * math.sin(math.radians(a0))
        return (f'<path class="{cls}" d="M{x0:.0f},{y0:.0f} A{r},{r} 0 0 1 {x1:.0f},{y1:.0f} '
                f'L{xi1:.0f},{yi1:.0f} A{r - 50},{r - 50} 0 0 0 {xi0:.0f},{yi0:.0f} Z"/>')
    d += arc(180, 120, "zr") + arc(120, 60, "zy") + arc(60, 0, "zg")
    d += f'<path class="ln" d="M{cx - r},{cy} A{r},{r} 0 0 1 {cx + r},{cy}"/>'
    d += t(cx - r + 10, cy + 26, "a person decides", "sm")
    d += t(cx + r - 10, cy + 26, "runs alone", "sm", "end")
    # needle pointing into yellow, a little toward green
    nx, ny = cx + 150 * math.cos(math.radians(75)), cy - 150 * math.sin(math.radians(75))
    d += f'<line class="lnc" x1="{cx}" y1="{cy}" x2="{nx:.0f}" y2="{ny:.0f}"/><circle class="hk" cx="{cx}" cy="{cy}" r="8"/>'
    d += kit.path(f"M{cx + 60},{cy - 175} Q{cx + 120},{cy - 200} {cx + 160},{cy - 165}", "ln")
    d += t(cx + 150, cy - 205, "turn only with evidence", "sm", "middle")
    # the evidence box
    d += kit.box(560, 40, 420, 190, "Before you turn it",
                 ["measure agreement on this one decision,", "not on all conversations;",
                  "sample amounts near the new limit", "and the unclear cases;",
                  "write the sample size beside the limit"], "bxs")
    return figure(1000, 285, d,
                  "A dial running from red, a person decides, through yellow, to green, runs alone. The needle sits in yellow. Beside it: before you turn it, measure agreement on this one decision, sample amounts near the new limit and unclear cases, and write the sample size beside the limit.",
                  "Autonomy is a dial, not a switch. Turn it one notch, for one decision, only when the agreement is measured there.")


DRAWINGS = {"hitl-toll-gate": drawing_toll_gate, "hitl-lanes": drawing_lanes, "hitl-durable-wait": drawing_durable_wait,
            "hitl-card": drawing_card, "hitl-dial": drawing_dial}
