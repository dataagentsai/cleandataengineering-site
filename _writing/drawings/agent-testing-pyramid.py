"""Drawings for 'The agent testing pyramid'.
kit, figure, E and ROOT are given as globals by build.py."""


def _person(cx, top):
    """A small stick person whose head centre is at (cx, top)."""
    return (f'<circle class="hz" cx="{cx}" cy="{top}" r="14"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 14}" x2="{cx}" y2="{top + 52}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 52}" x2="{cx - 12}" y2="{top + 76}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 52}" x2="{cx + 12}" y2="{top + 76}"/>')


def _cassette(x, y, w=120, h=76):
    """A cartoon cassette tape with its top-left corner at (x, y)."""
    cy = y + h * 0.45
    return (f'<rect class="hz" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/>'
            f'<rect class="pf pf-bxs" x="{x + 14}" y="{y + 10}" width="{w - 28}" height="{h * 0.6}" rx="5"/>'
            f'<rect class="hz" x="{x + 14}" y="{y + 10}" width="{w - 28}" height="{h * 0.6}" rx="5" fill-opacity="0"/>'
            f'<circle class="hz" cx="{x + w * 0.32}" cy="{cy}" r="10"/><circle class="hk" cx="{x + w * 0.32}" cy="{cy}" r="3"/>'
            f'<circle class="hz" cx="{x + w * 0.68}" cy="{cy}" r="10"/><circle class="hk" cx="{x + w * 0.68}" cy="{cy}" r="3"/>'
            f'<line class="ln" x1="{x + w * 0.32}" y1="{cy + 10}" x2="{x + w * 0.68}" y2="{cy + 10}"/>'
            f'<path class="hz" d="M{x + 24},{y + h} L{x + 32},{y + h - 10} L{x + w - 32},{y + h - 10} L{x + w - 24},{y + h} Z"/>')


def drawing_pyr_pyramid():
    t = kit.text
    layers = ["production monitoring", "load tests", "failure drills", "red teaming", "golden-set evals",
              "scenario simulation", "recorded model replies", "contract tests", "unit tests"]
    kinds = ["solid", "bxs", "bxs", "bxs", "bxs", "bxs", "bx", "bx", "bx"]
    cx, top, step, bh = 540, 46, 44, 36
    d = ""
    for i, (name, k) in enumerate(zip(layers, kinds)):
        w = 210 + i * 64
        d += kit.box(cx - w / 2, top + i * step, w, bh, name, "", k)
    # the line between "no live model" and "the real thing"
    ly = top + 6 * step - 3
    d += f'<line class="lnd" x1="{cx - 340}" y1="{ly}" x2="{cx + 330}" y2="{ly}"/>'
    d += t(990, ly - 44, ["above the line:", "a real model", "or real load"], "sm", "end")
    d += t(990, ly + 24, ["below it: no", "live model,", "$0, seconds"], "sm", "end")
    # the side arrow
    d += kit.arrow(70, top + 8 * step + 30, 70, top + 6)
    d += t(70, top - 14, "few, slow, costly", "bd", "middle")
    d += t(70, top + 9 * step + 22, "many, fast, free", "bd", "middle")
    return figure(1000, top + 9 * step + 40,
                  d, "A pyramid of nine layers. From the wide bottom to the narrow top: unit tests, contract tests, recorded model replies, scenario simulation, golden-set evals, red teaming, failure drills, load tests, production monitoring. A dashed line sits above recorded model replies: below it nothing calls a live model. An arrow on the left points up from many, fast, free to few, slow, costly.",
                  "The bottom three layers never call a live model. They are most of your tests, and they run on every save.")


def drawing_pyr_cassette():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(250, 24, "ONCE: RECORD", "lbl", "middle") + t(750, 24, "EVERY TEST AFTER: REPLAY", "lbl", "middle")
    d += f'<line class="lnd" x1="500" y1="10" x2="500" y2="290"/>'
    # record side
    d += b(10, 50, 180, 80, "Real model", ["costs money, and", "differs each time"], "bx")
    d += a(192, 90, 248, 90, "reply")
    d += _cassette(252, 52)
    d += t(312, 152, "saved to a file", "sm", "middle")
    d += t(312, 172, "with the question it answers", "sm", "middle")
    # a red record dot
    d += '<circle class="zr" cx="392" cy="60" r="9"/><circle class="hz" cx="392" cy="60" r="9" fill-opacity="0"/>'
    d += t(410, 65, "rec", "sm")
    # replay side
    d += _cassette(530, 52)
    d += '<path class="hz" d="M534,30 L534,46 L548,38 Z"/>'
    d += a(652, 100, 718, 100)
    d += b(722, 50, 270, 90, "Your agent's real loop", ["same reply every time,", "no network, $0"], "solid")
    d += b(530, 190, 200, 80, "The test fails", ["loudly: re-record", "on purpose"], "bxs")
    d += a(560, 132, 560, 186, "question changed?", lx=572, ly=166, anchor="start")
    d += b(760, 190, 230, 80, "No live fallback", ["it never quietly calls", "the real model"], "bxm")
    return figure(1000, 290, d, "Left: a real model's reply is recorded once onto a cassette tape, saved with the question it answers. Right: the cassette plays the same reply into the agent's real loop, with no network and no cost. If the question has changed, the test fails loudly; it never falls back to calling the real model.",
                  "A cassette is a recorded model reply. Record once, replay forever, and fail if the question no longer matches.")


def drawing_pyr_drill():
    b, a, t = kit.box, kit.arrow, kit.text
    d = b(10, 60, 180, 90, "The model", ["or a tool,", "or the server"], "bx")
    # cord from the model, ending in a plug, pulled out of a socket
    d += '<path class="ln" d="M190,105 Q220,105 236,118"/>'
    d += '<rect class="hz" x="234" y="112" width="26" height="18" rx="3"/>'
    d += '<line class="lnc" x1="260" y1="116" x2="272" y2="116"/><line class="lnc" x1="260" y1="126" x2="272" y2="126"/>'
    d += '<rect class="hz" x="300" y="104" width="24" height="34" rx="4"/>'
    d += '<path class="ln" d="M330,120 Q350,120 372,110"/>'
    d += t(286, 166, "pulled out", "sm", "middle") + t(286, 186, "on purpose", "sm", "middle")
    # spark lines between plug and socket
    d += '<path class="lnd" d="M278,100 L286,92 M290,104 L298,90"/>'
    d += b(376, 60, 190, 90, "Your agent", ["mid-conversation"], "solid")
    d += a(568, 105, 616, 105)
    # speech bubble with the reply
    d += '<path class="hz" d="M620,40 L990,40 L990,170 L700,170 L672,196 L680,170 L620,170 Z"/>'
    d += t(805, 80, ["\"I can't check your claim right", "now. Nothing has been changed.", "Shall I pass this to a person?\""], "tx", "middle")
    d += _person(470, 168)
    d += t(560, 238, "the drill checks three things:", "sm")
    d += kit.box(10, 260, 310, 50, "nothing paid twice", "", "bxs")
    d += kit.box(345, 260, 310, 50, "nothing lost", "", "bxs")
    d += kit.box(680, 260, 310, 50, "an honest reply", "", "bxs")
    return figure(1000, 320, d, "A failure drill. The model's plug has been pulled out of its socket on purpose while the agent is mid-conversation. The agent replies honestly that it can't check the claim right now, nothing has been changed, and offers to pass it to a person. A stick person watches. The drill checks three things: nothing paid twice, nothing lost, an honest reply.",
                  "Break one thing on purpose. Pass means the agent stays correct and tells the truth, not that it stays clever.")


def drawing_pyr_when():
    b, t = kit.box, kit.text
    cols = [("Every commit", "seconds to minutes", ["unit tests", "contract tests", "cassette replays", "scripted scenarios"], "bx"),
            ("Every night", "an hour, some cost", ["scenarios with a", "live model, repeated", "golden set on", "the live model"], "bxs"),
            ("Before a release", "the gate", ["red team suite", "failure drills", "load test", "all green, or no release"], "bxs"),
            ("Always, in production", "never stops", ["a fake customer asks", "known questions", "new release on a", "small slice first"], "solid")]
    d = ""
    for i, (title, sub, items, k) in enumerate(cols):
        x = 10 + i * 248
        d += b(x, 20, 232, 64, title, sub, k)
        d += f'<rect class="hz" x="{x}" y="100" width="232" height="140" rx="10"/>'
        for j, it in enumerate(items):
            d += t(x + 116, 130 + j * 28, it, "tx", "middle")
        if i < 3:
            d += kit.arrow(x + 234, 52, x + 246, 52)
    d += kit.path("M870,242 C870,300 130,300 130,246", "lnd")
    d += t(500, 312, "every miss in production comes back as a new test at the bottom", "sm", "middle")
    return figure(1000, 325, d, "Four columns, left to right. Every commit: unit tests, contract tests, cassette replays, scripted scenarios. Every night: scenarios with a live model, repeated, and the golden set on the live model. Before a release: red team suite, failure drills, load test, all green or no release. Always in production: a fake customer asks known questions, and a new release takes a small slice of traffic first. A dashed arrow loops from production back to every commit.",
                  "Cheap tests run all the time. Costly ones run less often. Production feeds new cases back to the bottom.")


DRAWINGS = {"pyr-pyramid": drawing_pyr_pyramid, "pyr-cassette": drawing_pyr_cassette,
            "pyr-drill": drawing_pyr_drill, "pyr-when": drawing_pyr_when}
