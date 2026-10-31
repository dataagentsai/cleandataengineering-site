"""Drawings for 'Should you build or buy your agent?'. Globals kit, figure, E, ROOT are injected."""


def _person(x, y):
    """A stick person whose feet are at (x, y)."""
    return (f'<circle class="bx" cx="{x}" cy="{y - 62}" r="12"/>'
            f'<line class="lnc" x1="{x}" y1="{y - 50}" x2="{x}" y2="{y - 20}"/>'
            f'<line class="lnc" x1="{x}" y1="{y - 20}" x2="{x - 10}" y2="{y}"/>'
            f'<line class="lnc" x1="{x}" y1="{y - 20}" x2="{x + 10}" y2="{y}"/>'
            f'<line class="lnc" x1="{x}" y1="{y - 42}" x2="{x - 14}" y2="{y - 28}"/>'
            f'<line class="lnc" x1="{x}" y1="{y - 42}" x2="{x + 6}" y2="{y - 62}"/>')


def drawing_buy_crossroads():
    b, t = kit.box, kit.text
    d = ""
    # three roads from the foot of the post
    d += '<path class="ln" d="M470,400 Q300,370 40,370"/><path class="ln" d="M440,432 Q300,410 40,410"/>'
    d += '<path class="ln" d="M530,400 Q700,370 960,370"/><path class="ln" d="M560,432 Q700,410 960,410"/>'
    d += '<path class="lnd" d="M470,400 L488,330"/><path class="lnd" d="M530,400 L512,330"/>'
    # the post
    d += '<rect class="hz" x="490" y="110" width="20" height="300" rx="3"/>'
    # top board: the middle road, with an arrow pointing straight on
    d += kit.arrow(500, 62, 500, 22)
    d += b(300, 64, 400, 76, "Buy the plumbing, build the rules", "the middle road, the one most teams take", "solid")
    # left arm: buy
    d += '<path class="hz" d="M210,170 L180,200 L210,230 Z"/>'
    d += b(208, 170, 270, 60, "Buy", "a finished product", "bx")
    # right arm: build
    d += '<path class="hz" d="M790,170 L820,200 L790,230 Z"/>'
    d += b(522, 170, 270, 60, "Build", "your team writes all of it", "bx")
    # the leader, wondering
    d += _person(300, 404)
    d += t(325, 330, "?", "bd")
    d += t(130, 300, "fast, but your edge lives in someone else's product", "sm", "start")
    d += t(870, 300, ["fits exactly, but you own", "every part, for years"], "sm", "middle")
    return figure(1000, 450, d,
                  "A cartoon signpost at a fork in the road, with a person looking up at it. The left arm says Buy: a finished product. The right arm says Build: your team writes all of it. The top board, pointing straight on, says Buy the plumbing, build the rules: the middle road, the one most teams take.",
                  "Build or buy is really three roads. The middle one is the most common.")


def drawing_buy_decision_card():
    b, t = kit.box, kit.text
    d = '<rect class="hz" x="150" y="20" width="700" height="470" rx="10"/>'
    d += t(500, 56, "BUILD OR BUY: ONE PAGE", "lbl", "middle")
    d += t(640, 92, "leans buy", "sm", "middle") + t(760, 92, "leans build", "sm", "middle")
    rows = [("Is the process special to us?", "common job", "our edge"),
            ("Where may the data go?", "anywhere allowed", "must stay put"),
            ("What does one task cost?", "known, metered", "unknown"),
            ("Can we switch later?", "yes, export all", "locked in"),
            ("Who owns it after launch?", "vendor does most", "our team"),
            ("What must we prove?", "little", "every step")]
    for i, (q, buy, build) in enumerate(rows):
        y = 110 + i * 62
        d += kit.num(190, y + 25, i + 1)
        d += t(215, y + 31, q, "tx")
        d += f'<rect class="hz" x="628" y="{y + 12}" width="24" height="24" rx="3"/>'
        d += f'<rect class="hz" x="748" y="{y + 12}" width="24" height="24" rx="3"/>'
        d += t(640, y + 54, buy, "sm", "middle") + t(760, y + 54, build, "sm", "middle")
        if i < 5:
            d += f'<line class="lnd" x1="180" y1="{y + 60}" x2="820" y2="{y + 60}"/>'
    return figure(1000, 505, d,
                  "A one-page card titled Build or buy. Six numbered questions, each with two tick boxes, leans buy and leans build. One: is the process special to us? Common job or our edge. Two: where may the data go? Anywhere allowed or must stay put. Three: what does one task cost? Known and metered, or unknown. Four: can we switch later? Yes, export all, or locked in. Five: who owns it after launch? Vendor does most, or our team. Six: what must we prove? Little, or every step.",
                  "Tick one box per question. Mostly left means buy; mostly right means build that part yourself.")


def drawing_buy_year_money():
    b, t = kit.box, kit.text
    d = t(500, 26, "example numbers for one agent, not a benchmark", "sm", "middle")
    base = 320
    scale = 12  # px per lakh
    # bar 1: what the quote shows
    h = 10 * scale
    d += b(150, base - h, 200, h, "Licence", "₹10 lakh", "bx")
    d += t(250, base + 30, "what the quote shows", "bd", "middle")
    # bar 2: the full year, stacked
    piles = [("Licence", "₹10 lakh", 10, "bx"),
             ("Running", "₹4.8 lakh", 4.8, "bxs"),
             ("People", "₹8 lakh", 8, "solid")]
    y = base
    for name, amount, lakh, kind in piles:
        h = lakh * scale
        y -= h
        d += b(600, y, 200, h - 4, name, amount, kind)
    d += t(700, base + 30, "what the year costs: about ₹23 lakh", "bd", "middle")
    d += t(820, base - 10 * scale - 4.8 * scale / 2 + 5, ["20,000 tasks a month", "at ₹2 a task"], "sm", "start")
    d += t(820, base - 14.8 * scale - 8 * scale / 2 + 5, ["a quarter of an engineer:", "checks, fixes, on-call"], "sm", "start")
    d += f'<line class="ln" x1="100" y1="{base}" x2="900" y2="{base}"/>'
    # a coin
    d += '<circle class="hz" cx="440" cy="230" r="26"/>' + t(440, 239, "₹", "bd", "middle")
    return figure(1000, 370, d,
                  "Two bars on an example. The left bar, what the quote shows, is the licence alone: ₹10 lakh. The right bar, what the year costs, stacks the licence (₹10 lakh), running cost (₹4.8 lakh, for 20,000 tasks a month at ₹2 a task) and people (₹8 lakh, a quarter of an engineer for checks, fixes and on-call), about ₹23 lakh in all.",
                  "An example year. The licence is one of three piles, and the other two exist whether you build or buy.")


def drawing_buy_middle_path():
    b, t = kit.box, kit.text
    d = t(40, 34, "BUILD: SMALL, AND YOURS ALONE", "lbl")
    top = [("Business rules", ["who gets a refund,", "up to what limit"]),
           ("Checks", ["stop a wrong action", "before it happens"]),
           ("Evals on your cases", ["your real requests,", "before every change"])]
    for i, (name, sub) in enumerate(top):
        d += b(40 + i * 315, 50, 290, 100, name, sub, "solid")
    # a rupee coin above the build row
    d += '<circle class="hz" cx="930" cy="26" r="18"/>' + t(930, 33, "₹", "bd", "middle")
    d += t(40, 200, "BUY: COMMON TO EVERY AGENT", "lbl")
    bottom = [("AI model", "rented by the call"),
              ("Gateway", "one door for model calls"),
              ("Tracing", "every step written down"),
              ("Platform", "where it runs")]
    for i, (name, sub) in enumerate(bottom):
        d += b(40 + i * 237, 216, 217, 80, name, sub, "bx")
    # the pipes under the floor
    d += '<path class="lnc" d="M40,330 L960,330"/>'
    for x in (150, 387, 624, 861):
        d += f'<line class="ln" x1="{x}" y1="298" x2="{x}" y2="328"/>'
        d += f'<circle class="hz" cx="{x}" cy="330" r="7"/>'
    d += t(500, 362, "the plumbing: improves fast, gives no edge, so buy it or use good open source", "sm", "middle")
    return figure(1000, 380, d,
                  "Two rows. The bottom row, in blue, is what to buy because every agent needs it: the AI model, a gateway, tracing and the platform, sitting on pipes. The top row, in lavender, is what to build because it is yours alone: business rules, checks, and evals on your own cases.",
                  "The middle path. Buy the plumbing; build the parts that protect money and make you different.")


DRAWINGS = {
    "buy-crossroads": drawing_buy_crossroads,
    "buy-decision-card": drawing_buy_decision_card,
    "buy-year-money": drawing_buy_year_money,
    "buy-middle-path": drawing_buy_middle_path,
}
