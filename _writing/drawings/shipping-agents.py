"""Drawings for 'Shipping agents: versioning prompts, models and tools together'.
kit, figure, E and ROOT are given as globals by build.py."""


def _person(cx, top):
    """A small stick person whose head centre is at (cx, top)."""
    return (f'<circle class="hz" cx="{cx}" cy="{top}" r="14"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 14}" x2="{cx}" y2="{top + 52}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 52}" x2="{cx - 12}" y2="{top + 76}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 52}" x2="{cx + 12}" y2="{top + 76}"/>')


def drawing_ship2_sealed_box():
    b, t = kit.box, kit.text
    d = t(500, 24, "everything that changes what the agent does goes in one box, with one name", "sm", "middle")
    # a cardboard box, drawn front, top and side, with tape across the lid
    d += ('<path class="hz" d="M50,130 L90,90 L330,90 L290,130 Z"/>'
          '<path class="hz" d="M290,130 L330,90 L330,270 L290,310 Z"/>'
          '<rect class="hz" x="50" y="130" width="240" height="180" rx="4"/>'
          '<rect class="pf pf-bxs" x="150" y="130" width="40" height="70"/>'
          '<path class="pf pf-bxs" d="M150,130 L190,90 L230,90 L190,130 Z"/>'
          '<line class="ln" x1="150" y1="130" x2="150" y2="200"/><line class="ln" x1="190" y1="130" x2="190" y2="200"/>')
    d += t(170, 250, "release r42", "bd", "middle")
    d += t(170, 276, "sealed", "sm", "middle")
    # the string from the box to the tag
    d += '<path class="ln" d="M290,150 Q340,150 372,128"/>'
    # the luggage tag
    d += '<path class="hz" d="M380,60 L700,60 L700,310 L380,310 L380,140 L362,124 L380,108 Z"/>'
    d += '<circle class="hz" cx="396" cy="124" r="7"/>'
    rows = [("PROMPT", "v7 (hash of the text)"),
            ("MODEL", "gpt-oss-120b, pinned"),
            ("TOOLS", "v3: names and schemas"),
            ("CHECKS", "v12: rules and limits"),
            ("CONFIG", "temperature, budgets")]
    for j, (k, v) in enumerate(rows):
        yy = 96 + j * 34
        d += t(420, yy, k, "lbl") + t(520, yy, v, "tx")
    d += '<line class="lnd" x1="412" y1="270" x2="688" y2="270"/>'
    d += t(420, 296, "FINGERPRINT", "lbl") + t(560, 296, "9f3a…c21", "bd")
    # the rule
    d += b(740, 70, 250, 100, "Change any one", ["new fingerprint,", "new release"], "bxs")
    d += b(740, 200, 250, 100, "Not in the box", ["API keys, tool URLs:", "they don't change behaviour"], "bxm")
    return figure(1000, 330, d, "A taped cardboard box labelled release r42, sealed. A luggage tag tied to it lists prompt v7 (a hash of the text), model gpt-oss-120b pinned, tools v3 with names and schemas, checks v12 with rules and limits, config with temperature and budgets, and a fingerprint 9f3a…c21. Beside it: change any one and you get a new fingerprint and a new release; API keys and tool URLs are not in the box because they don't change behaviour.",
                  "One release is one sealed box. The fingerprint is a short code made from everything inside.")


def drawing_ship2_release_road():
    b, a, t, p = kit.box, kit.arrow, kit.text, kit.path
    steps = [("Build", ["seal the box,", "get a fingerprint"], "bx"),
             ("Gate", ["golden set, scenarios,", "cost, every model"], "bxs"),
             ("Canary 5%", ["a small share", "of real traffic"], "solid"),
             ("Watch", ["compare it with", "the old release"], "bx"),
             ("Full rollout", ["100% on", "the new release"], "bx")]
    d = t(500, 24, "a release travels this road in order; it can turn back at any point", "sm", "middle")
    for i, (title, sub, k) in enumerate(steps):
        x = 12 + i * 196
        d += b(x, 50, 178, 105, title, sub, k) + kit.num(x + 12, 50, i + 1)
        if i < 4:
            d += a(x + 180, 102, x + 194, 102)
    # the road under the boxes
    d += '<line class="lnd" x1="12" y1="180" x2="974" y2="180"/>'
    # the rollback path from Watch back to the previous release
    d += b(330, 245, 300, 85, "Previous release", "still sealed, still ready", "bxm")
    d += p("M689,157 Q689,287 634,287", "lnc")
    d += t(700, 262, "rollback: one command,", "bd") + t(700, 284, "rehearsed, not assumed", "sm")
    # the gate's own no
    d += p("M297,157 Q297,230 326,268", "lnd")
    d += t(130, 238, "gate fails:", "sm") + t(130, 258, "the old one stays live", "sm")
    return figure(1000, 345, d, "Five numbered steps on a road: build (seal the box, get a fingerprint), gate (golden set, scenarios, cost, every model), canary at 5% of real traffic, watch (compare with the old release), full rollout at 100%. A thick arrow runs from watch back to a dashed box, the previous release, still sealed and ready: rollback is one command, rehearsed. A dashed arrow from the gate shows that if the gate fails, the old release stays live.",
                  "The release road. The way back matters as much as the way forward.")


def drawing_ship2_one_word():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(500, 24, "an illustrative change: someone tidies one word out of the prompt", "sm", "middle")
    # two prompt cards
    d += '<rect class="hz" x="20" y="50" width="330" height="96" rx="8"/>'
    d += t(36, 76, "PROMPT V7", "lbl")
    d += t(36, 104, "Always check the return date", "tx") + t(36, 128, "before you issue a refund.", "tx")
    d += '<rect class="pf pf-bxs" x="25" y="175" width="330" height="96" rx="8"/>'
    d += '<rect class="hz" x="20" y="170" width="330" height="96" rx="8" fill-opacity="0"/>'
    d += t(36, 196, "PROMPT V8", "lbl")
    d += t(36, 224, "Always check the return date", "tx") + t(36, 248, "before you issue a refund.", "tx")
    d += '<line class="lnc" x1="32" y1="218" x2="92" y2="218"/>'
    d += t(340, 196, "one word gone", "sm", "end")
    d += a(352, 218, 410, 218)
    # the gate with a golden card
    d += b(412, 150, 250, 136, "The gate", ["golden case: returned", "31 days ago, ₹3,499,", "must refuse"], "bxs")
    d += _person(720, 156)
    d += a(762, 218, 800, 218)
    d += b(802, 150, 188, 136, "Blocked", ["v8 refunded it;", "v7 stays live"], "solid")
    d += t(705, 76, "nobody would spot this", "sm", "middle") + t(705, 96, "reading the diff", "sm", "middle")
    return figure(1000, 300, d, "Two prompt cards. Version 7 says 'Always check the return date before you issue a refund.' Version 8 is the same with the word 'Always' struck out. Version 8 goes into the gate, which holds a golden case: an order returned 31 days ago for 3,499 rupees, which must be refused. A stick-person examiner stands by. Result: blocked, because version 8 refunded it, so version 7 stays live.",
                  "A prompt is code. A one-word edit is a behaviour change, and the gate is what notices.")


def drawing_ship2_trace_stamp():
    b, t = kit.box, kit.text
    d = t(500, 24, "every turn's trace carries the release it ran under", "sm", "middle")
    turns = [("turn 1041", "refund, ok", "r41"), ("turn 1042", "order status, ok", "r42"),
             ("turn 1043", "refund, wrong", "r42"), ("turn 1044", "refund, wrong", "r42")]
    for j, (name, what, rel) in enumerate(turns):
        y = 52 + j * 62
        d += f'<rect class="hz" x="20" y="{y}" width="420" height="48" rx="6"/>'
        d += t(36, y + 30, name, "bd") + t(150, y + 30, what, "tx")
        kind = "pf pf-solid" if rel == "r42" else "pf pf-bx"
        d += f'<ellipse class="{kind}" cx="388" cy="{y + 24}" rx="40" ry="17"/>'
        d += f'<ellipse class="hz" cx="388" cy="{y + 24}" rx="40" ry="17" fill-opacity="0"/>'
        d += t(388, y + 30, rel, "bd", "middle")
    # the rubber stamp cartoon
    d += ('<rect class="hz" x="490" y="128" width="70" height="22" rx="3"/>'
          '<rect class="hz" x="512" y="96" width="26" height="32" rx="4"/>'
          '<circle class="hz" cx="525" cy="84" r="16"/>')
    d += t(525, 180, "stamped on", "sm", "middle") + t(525, 200, "at the start", "sm", "middle")
    d += b(610, 60, 380, 110, "Filter by release", ["both wrong refunds ran on r42,", "the 5% canary since Tuesday"], "bxs")
    d += b(610, 200, 380, 100, "So you know what to roll back", ["and which box to open", "to find the change"], "bx")
    return figure(1000, 315, d, "Four trace cards, each with an oval stamp naming its release: turn 1041 refund ok on r41, turn 1042 order status ok on r42, turns 1043 and 1044 refund wrong on r42. A cartoon rubber stamp sits beside them. Filtering by release shows both wrong refunds ran on r42, the 5% canary since Tuesday, so you know what to roll back and which box to open to find the change.",
                  "Stamp the release id on every trace. Without it, a bad Monday has no suspect.")


DRAWINGS = {"ship2-sealed-box": drawing_ship2_sealed_box, "ship2-release-road": drawing_ship2_release_road,
            "ship2-one-word": drawing_ship2_one_word, "ship2-trace-stamp": drawing_ship2_trace_stamp}
