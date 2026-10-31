"""Drawings for 'Answer without the model first: 104 ms vs 7 seconds'. Globals kit, figure, E, ROOT are injected."""


def _person(cx, top, cls="bx"):
    """A small stick person whose head centre sits at (cx, top)."""
    return (f'<circle class="{cls}" cx="{cx}" cy="{top}" r="14"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 14}" x2="{cx}" y2="{top + 52}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 52}" x2="{cx - 12}" y2="{top + 76}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 52}" x2="{cx + 12}" y2="{top + 76}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 26}" x2="{cx - 18}" y2="{top + 42}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 26}" x2="{cx + 18}" y2="{top + 42}"/>')


def drawing_direct_receptionist():
    b, t = kit.box, kit.text
    d = t(500, 24, "she answers what she can see on her own desk, and calls the manager for the rest", "sm", "middle")
    # the customer and the question
    d += _person(110, 110)
    d += '<path class="hz" d="M40,40 L250,40 Q262,40 262,52 L262,78 Q262,90 250,90 L150,90 L128,104 L134,90 L52,90 Q40,90 40,78 L40,52 Q40,40 52,40 Z"/>'
    d += t(151, 71, "What time do you close?", "tx", "middle")
    # the receptionist behind her desk
    d += _person(400, 110, "bxs")
    d += '<rect class="hz" x="320" y="160" width="160" height="40" rx="6"/>'
    d += '<rect class="hz" x="440" y="146" width="26" height="14" rx="3"/>'
    d += '<path class="hz" d="M300,40 L470,40 Q482,40 482,52 L482,78 Q482,90 470,90 L420,90 L404,104 L404,90 L312,90 Q300,90 300,78 L300,52 Q300,40 312,40 Z"/>'
    d += t(391, 71, "8 pm, every day.", "tx", "middle")
    # the manager's door, closed, phone untouched
    d += '<rect class="hz" x="780" y="50" width="110" height="150" rx="6"/>'
    d += '<circle class="hk" cx="870" cy="128" r="5"/>'
    d += t(835, 40, "MANAGER", "lbl", "middle")
    d += '<line class="lnd" x1="490" y1="130" x2="770" y2="130"/>'
    d += '<line class="lnc" x1="615" y1="112" x2="645" y2="148"/><line class="lnc" x1="645" y1="112" x2="615" y2="148"/>'
    d += t(630, 176, "no call needed", "sm", "middle")
    d += b(40, 230, 440, 80, "Answers herself", ["closing time, the address,", "a booking she can see on screen"], "bxs")
    d += b(520, 230, 440, 80, "Calls the manager", ["a refund, a complaint,", "anything she is not sure of"], "bxm")
    return figure(1000, 325, d, "Cartoon: a customer asks a receptionist what time they close, and she answers 8 pm herself. A dashed line to the manager's closed door is crossed out. Below, two boxes: she answers closing time, the address and bookings she can see; she calls the manager for a refund, a complaint or anything she is not sure of.",
                  "A good receptionist. The manager's time goes to the questions that need a manager.")


def drawing_direct_two_roads():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(500, 22, "two real messages from the same customer, sent to the claims assistant in October 2026", "sm", "middle")
    d += b(10, 130, 190, 90, "Rohan's message", ["names a claim,", "or doesn't"], "bxm")
    d += a(202, 175, 243, 175)
    d += b(245, 135, 140, 80, "Router", "plain rules", "solid")
    # upper road: direct
    d += a(387, 160, 468, 92, "names CLM-019002", lx=405, ly=108, anchor="end")
    d += b(470, 45, 270, 90, "Direct path", ["one read from the claims", "system, one template"], "bx")
    d += t(605, 160, "104 ms · 0 model calls · $0", "bd", "middle")
    # lower road: loop
    d += a(387, 190, 468, 258, "\"my claim\"", lx=405, ly=258, anchor="end")
    d += b(470, 215, 270, 90, "Model loop", ["2 trips: look up his", "claims, then write"], "bx")
    d += t(605, 330, "7,076 ms · 2 model calls · $0.00058", "bd", "middle")
    # both arrive
    d += a(742, 90, 818, 158)
    d += a(742, 260, 818, 192)
    d += b(820, 135, 170, 80, "Reply", "to Rohan", "bxm")
    return figure(1000, 350, d, "A message goes to the router at a fork. If it names claim CLM-019002 it takes the direct path, one read and one template, in 104 ms with no model call and $0. If it says my claim, it takes the model loop, two trips, in 7,076 ms with two model calls and $0.00058. Both roads end at the reply.",
                  "One fork, two roads. Flow 1a took the top road; flow 1b took the bottom one.")


def drawing_direct_same_checks():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(500, 22, "the cheap road skips the model, not the checks", "sm", "middle")
    d += b(10, 120, 150, 90, "Front door", ["token, kill", "switch, ledger"], "bxs")
    d += a(162, 165, 193, 165)
    d += b(195, 125, 120, 80, "Router", "", "solid")
    d += a(317, 150, 353, 95)
    d += a(317, 180, 353, 235)
    d += b(355, 50, 180, 80, "Direct path", "read + template", "bx")
    d += b(355, 200, 180, 80, "Model loop", "checks on every trip", "bx")
    d += a(537, 90, 578, 145)
    d += a(537, 240, 578, 185)
    d += b(580, 85, 240, 160, "Before the reply", ["no promise of cover", "no personal data echoed", "money in rupees", "same rules, both roads"], "bxs")
    d += a(822, 165, 853, 165)
    d += b(855, 125, 135, 80, "Save, reply", "", "bxm")
    d += t(500, 312, "the claims system also checks the read is Rohan's own, the same as for any tool call", "sm", "middle")
    return figure(1000, 325, d, "A front door check, then the router splits into the direct path and the model loop. Both join at the same before-reply check: no promise of cover, no personal data echoed, money in rupees. Then save and reply.",
                  "Both roads go through the same front door and the same last check. The direct path is not a side door.")


def drawing_direct_rule_card():
    t = kit.text
    x0, y0, w, h = 150, 50, 700, 330
    d = f'<rect class="hz" x="{x0}" y="{y0}" width="{w}" height="{h}" rx="10"/>'
    d += f'<circle class="hk" cx="{x0 + w / 2}" cy="{y0 + 4}" r="7"/>'
    d += t(x0 + 30, y0 + 40, "ROUTER RULES · VERSION v1", "lbl")
    d += t(x0 + w - 30, y0 + 40, "the first yes wins", "sm", "end")
    d += f'<line class="ln" x1="{x0 + 20}" y1="{y0 + 56}" x2="{x0 + w - 20}" y2="{y0 + 56}"/>'
    rows = [("Must a person handle this?", "Escalate"), ("Must we refuse?", "Refuse"),
            ("Which intents are in it?", "(just counts them)"), ("Exactly one read, one reference?", "Direct")]
    for i, (q, out) in enumerate(rows):
        y = y0 + 92 + i * 48
        d += kit.num(x0 + 44, y - 6, i + 1)
        d += t(x0 + 72, y, q, "tx")
        if out == "Direct":
            d += f'<rect class="bxs" x="{x0 + w - 190}" y="{y - 24}" width="160" height="34" rx="8"/>'
        d += t(x0 + w - 110, y, out, "bd" if not out.startswith("(") else "sm", "middle")
    yl = y0 + 92 + 4 * 48 - 22
    d += f'<line class="lnd" x1="{x0 + 20}" y1="{yl}" x2="{x0 + w - 20}" y2="{yl}"/>'
    d += t(x0 + 30, yl + 30, "all four say no: send it to the model loop", "bd")
    d += t(x0 + 30, yl + 56, "Direct needs all three: one intent, it only reads, one CLM- or POL- number", "sm")
    return figure(1000, 395, d, "An index card pinned at the top, titled router rules version v1, the first yes wins. Four numbered questions: must a person handle this (Escalate), must we refuse (Refuse), which intents are in it, exactly one read and one reference (Direct, highlighted). Below: if all four say no, send it to the model loop. Direct needs one intent, read-only, one claim or policy number.",
                  "The whole router fits on a card. Four questions, always in the same order.")


DRAWINGS = {"direct-receptionist": drawing_direct_receptionist, "direct-two-roads": drawing_direct_two_roads,
            "direct-same-checks": drawing_direct_same_checks, "direct-rule-card": drawing_direct_rule_card}
