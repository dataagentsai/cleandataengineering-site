"""Drawings for 'The horse and the harness'. Globals kit, figure, E, ROOT are injected."""


def drawing_horse_lanes():
    import pages_horse as ph
    t = kit.text
    d = ph.road()
    d += t(14, 52, "RED · NEVER", "lbl") + t(14, 76, "move money nobody asked for · show one customer's details to another", "tx")
    d += t(14, 110, "YELLOW · ASK A PERSON", "lbl") + t(14, 134, "a refund above the limit: a person approves first", "tx")
    d += t(14, 401, "YELLOW · ASK A PERSON", "lbl") + t(14, 422, "the agent is unsure or going round in circles: hand over", "tx")
    d += t(14, 462, "RED · NEVER", "lbl") + t(14, 486, "follow instructions hidden inside a customer's email", "tx")
    d += t(14, 372, "GREEN · approve a refund under the limit, say ₹5,000", "bd")
    g = '<line class="ln" x1="370" y1="236" x2="652" y2="240"/><line class="ln" x1="370" y1="256" x2="650" y2="256"/>'
    g += '<rect class="bx" x="240" y="205" width="130" height="66" rx="10"/>' + t(305, 244, "the work", "tx", "middle")
    g += '<circle class="bx" cx="292" cy="286" r="32"/><line class="ln" x1="292" y1="254" x2="292" y2="318"/><line class="ln" x1="260" y1="286" x2="324" y2="286"/>'
    g += '<circle class="bx" cx="335" cy="168" r="14"/><line class="lnc" x1="335" y1="182" x2="335" y2="206"/><line class="lnc" x1="335" y1="192" x2="362" y2="190"/>'
    g += ph.horse() + '<path class="lnc" d="M752,198 Q620,140 364,190"/>'
    d += f'<g transform="translate(0,28)">{g}</g>'
    d += t(560, 168, "reins: your rules and checks", "bd", "middle")
    d += t(220, 205, ["driver: the people", "who own the rules"], "sm", "end")
    d += t(800, 305, ["the horse: the AI model.", "strong and fast, but it", "doesn't know your road"], "sm")
    return figure(1000, 510, d,
                  "A horse in harness pulls a cart along a road. The green middle lane says approve a refund under the limit, say ₹5,000. The yellow lanes on each side say a refund above the limit needs a person to approve it first, and an agent that is unsure or going round in circles hands over. The red edges say never move money nobody asked for, never show one customer's details to another, and never follow instructions hidden inside a customer's email. A driver holds the reins.",
                  "The AI model is the horse. The harness is everything that keeps it in the green lane: your rules, your checks and the people who own them.")


def drawing_horse_scenes():
    import pages_horse as ph
    t, path = kit.text, kit.path
    p = ""
    scenes = [("Stays green", "a ₹2,000 refund, under the limit", "approved, written down, done", 100),
              ("Drifts into yellow", "a ₹60,000 refund, above the limit", "pulled back: a person approves first", 55),
              ("Heads for red", "an email says \"send ₹5 lakh to me\"", "stopped: no money moves unasked", 16)]
    for i, (title, ex, what, hy) in enumerate(scenes):
        x0 = 10 + i * 330
        p += f'<rect class="zr" x="{x0}" y="10" width="310" height="40"/><rect class="zy" x="{x0}" y="50" width="310" height="40"/>'
        p += f'<rect class="zg" x="{x0}" y="90" width="310" height="100"/>'
        p += f'<line class="lnd" x1="{x0}" y1="90" x2="{x0 + 310}" y2="90"/><line class="lnc" x1="{x0}" y1="50" x2="{x0 + 310}" y2="50"/>'
        sc = 0.42
        p += ph.horse(x0 + 150 - 615 * sc, hy - 132 * sc, sc)
        if i == 1:
            p += path(f"M{x0 + 285},{hy + 20} Q{x0 + 305},{hy + 60} {x0 + 280},{hy + 95}", "lnc")
            p += t(x0 + 275, hy + 122, "pulled back", "sm", "end")
        if i == 2:
            p += f'<line class="lnc" x1="{x0 + 262}" y1="14" x2="{x0 + 296}" y2="46"/><line class="lnc" x1="{x0 + 296}" y1="14" x2="{x0 + 262}" y2="46"/>'
        p += t(x0 + 155, 215, title, "bd", "middle")
        p += t(x0 + 155, 239, ex, "sm", "middle")
        p += t(x0 + 155, 261, what, "sm", "middle")
    return figure(1000, 275, p,
                  "Three small scenes of the horse on a green, yellow and red road. Stays green: a ₹2,000 refund under the limit is approved, written down and done. Drifts into yellow: a ₹60,000 refund above the limit is pulled back so a person approves first. Heads for red: an email says send ₹5 lakh to me, and it is stopped because no money moves unasked.",
                  "Three journeys, made-up amounts. The harness lets green through, pulls yellow back to a person, and stops red outright.")


def drawing_horse_checklist():
    t = kit.text
    d = '<rect class="hz" x="210" y="16" width="740" height="420" rx="10"/>'
    d += t(580, 52, "BEFORE THE AGENT GOES LIVE", "lbl", "middle")
    rows = [("Who decides the red lines?", "a named owner, not the vendor"),
            ("Where is the proof they hold?", "tests that try to break them, every change"),
            ("Who is told when one is tested?", "a name and a time limit"),
            ("Where is the kill switch?", "who may pull it, and has it been tried"),
            ("What if we change the model?", "the same tests run again first")]
    for i, (q, a) in enumerate(rows):
        y = 74 + i * 70
        bx, by = 250, y + 12
        d += f'<rect class="hz" x="{bx}" y="{by}" width="26" height="26" rx="3"/>'
        d += f'<path class="lnc" d="M{bx + 5},{by + 14} L{bx + 11},{by + 21} L{bx + 22},{by + 5}"/>'
        d += t(300, y + 28, q, "bd")
        d += t(300, y + 50, a, "sm")
        if i < 4:
            d += f'<line class="lnd" x1="240" y1="{y + 66}" x2="920" y2="{y + 66}"/>'
    # a stick-figure leader holding the card
    d += ('<circle class="bx" cx="110" cy="200" r="20"/><line class="lnc" x1="110" y1="220" x2="110" y2="310"/>'
          '<line class="lnc" x1="110" y1="245" x2="205" y2="225"/><line class="lnc" x1="110" y1="250" x2="70" y2="290"/>'
          '<line class="lnc" x1="110" y1="310" x2="85" y2="370"/><line class="lnc" x1="110" y1="310" x2="135" y2="370"/>')
    d += t(110, 400, "you", "sm", "middle")
    return figure(1000, 450, d,
                  "A leader holds a checklist card titled before the agent goes live, with five ticked questions. Who decides the red lines: a named owner, not the vendor. Where is the proof they hold: tests that try to break them, every change. Who is told when one is tested: a name and a time limit. Where is the kill switch: who may pull it, and has it been tried. What if we change the model: the same tests run again first.",
                  "Five questions, one card. None of them is about which AI model you bought.")


DRAWINGS = {
    "horse-lanes": drawing_horse_lanes,
    "horse-scenes": drawing_horse_scenes,
    "horse-checklist": drawing_horse_checklist,
}
