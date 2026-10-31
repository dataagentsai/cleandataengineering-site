"""Drawings for 'Swap anything, break nothing: software design patterns for agent harnesses'.
kit, figure, E and ROOT are given as globals by build.py."""


def _plug_left(x, y):
    """A two-pin plug whose body's top-left corner is at (x, y), pins pointing left."""
    return (f'<rect class="hz" x="{x}" y="{y}" width="50" height="40" rx="8"/>'
            f'<rect class="hk" x="{x - 16}" y="{y + 9}" width="16" height="6" rx="2"/>'
            f'<rect class="hk" x="{x - 16}" y="{y + 25}" width="16" height="6" rx="2"/>'
            f'<path class="ln" d="M{x + 50},{y + 20} Q{x + 62},{y + 20} {x + 64},{y + 32}"/>')


def _tick(x, y):
    return f'<path class="lnc" d="M{x},{y} l7,8 l14,-16"/>'


def drawing_pat_socket():
    b, t, p, a = kit.box, kit.text, kit.path, kit.arrow
    d = b(10, 110, 200, 100, "Your harness", ["only knows the", "socket's shape"], "bx")
    d += '<line class="lnc" x1="212" y1="160" x2="250" y2="160"/>'
    # the wall plate and its socket: the port
    d += '<rect class="hz" x="250" y="90" width="120" height="140" rx="14"/>'
    d += ('<circle class="hz" cx="310" cy="160" r="34"/>'
          '<rect class="hk" x="296" y="146" width="7" height="22" rx="3"/><rect class="hk" x="317" y="146" width="7" height="22" rx="3"/>')
    d += t(310, 256, "the port", "bd", "middle") + t(310, 278, "LLMClient", "sm", "middle")
    plugs = [("scripted", "canned answers, for tests"), ("litellm-proxy", "the open-source gateway"),
             ("groq-direct", "straight to Groq"), ("apim-ai-gateway", "Azure's gateway")]
    for i, (name, what) in enumerate(plugs):
        y = 20 + i * 80
        d += _plug_left(626, y)
        d += t(706, y + 16, name, "tx") + t(706, y + 37, what, "sm")
    # the chosen plug, plugged in
    d += p("M344,160 Q470,160 608,125", "lnc", end=False)
    d += b(400, 236, 190, 72, "The YAML", "model: litellm-proxy", "bxs")
    d += a(495, 234, 495, 158)
    return figure(1000, 325, d, "A cartoon. Your harness is wired to a wall socket labelled the port, LLMClient. Four plugs hang beside it: scripted, litellm-proxy, groq-direct and apim-ai-gateway. A cable joins the socket to the litellm-proxy plug, and a yellow note, the YAML, points at that cable and says model: litellm-proxy.",
                  "The port is the socket, each adapter is a plug, and one line of YAML picks which plug goes in.")


def drawing_pat_turn():
    b, a, t, n = kit.box, kit.arrow, kit.text, kit.num
    steps = [("Route", "is a model needed?", "bx"), ("Build context", "what it sees", "bx"),
             ("Ask the model", "one call, typed", "solid"), ("Check, then act", "the gates, the tool", "bxs"),
             ("Write it down", "trace and state", "bx")]
    d = t(500, 26, "the template: the same five steps, in the same order, every turn", "sm", "middle")
    for i, (title, sub, k) in enumerate(steps):
        x = 10 + i * 202
        d += b(x, 50, 170, 96, title, sub, k) + n(x + 12, 50, i + 1)
        if i < 4:
            d += a(x + 172, 98, x + 200, 98)
    d += '<line class="lnd" x1="95" y1="148" x2="95" y2="194"/>' + b(10, 196, 170, 104, "Which path?", ["answer directly,", "refuse, a person,", "or the loop"], "bxm")
    d += '<line class="lnd" x1="499" y1="148" x2="499" y2="194"/>' + b(414, 196, 170, 104, "Which model?", ["small or strong,", "named in config"], "bxm")
    d += t(230, 238, ["strategies: one slot,", "several ways to fill it"], "sm")
    d += t(800, 238, ["the slots change;", "the order never does"], "sm", "middle")
    return figure(1000, 312, d, "Five steps in a row, the same every turn: route, build context, ask the model, check then act, write it down. Under route, a dashed slot asks which path: answer directly, refuse, a person, or the loop. Under ask the model, a dashed slot asks which model, small or strong, named in config.",
                  "Template method fixes the steps of a turn. Strategy fills a slot inside a step with one of several interchangeable choices.")


def drawing_pat_gates():
    b, a, t = kit.box, kit.arrow, kit.text
    d = '<line class="ln" x1="10" y1="212" x2="990" y2="212"/>'
    # the suitcase: the tool call waiting to go through
    d += ('<rect class="hz" x="22" y="140" width="84" height="62" rx="8"/>'
          '<path class="ln" d="M50,140 L50,128 L78,128 L78,140"/>'
          '<line class="ln" x1="22" y1="162" x2="106" y2="162"/>')
    d += t(64, 120, "refund ₹40,000", "sm", "middle")
    gates = [(270, "Allowed tool?"), (460, "Did they ask?"), (650, "Under the limit?")]
    for c, sign in gates:
        d += b(c - 80, 36, 160, 56, sign, "", "bxs")
        d += (f'<line class="lnc" x1="{c - 60}" y1="92" x2="{c - 60}" y2="212"/>'
              f'<line class="lnc" x1="{c + 60}" y1="92" x2="{c + 60}" y2="212"/>')
    d += a(108, 172, 778, 172)
    d += b(780, 116, 200, 90, "The tool", "issue_refund", "bx")
    d += t(500, 246, "they run in order, and the first gate that says no stops the call: the tool never runs", "sm", "middle")
    d += t(500, 270, "a gate that crashes, or runs out of time, says no too", "sm", "middle")
    return figure(1000, 285, d, "A suitcase labelled refund of 40,000 rupees waits at a line of three airport security gates: allowed tool, did they ask, under the limit. Past the gates is the tool, issue_refund.",
                  "Chain of responsibility. Each check is a gate; any one can turn the call back, and a new check is one more gate in the line.")


def _doll(cx, base, s):
    """A small matryoshka doll standing on y=base, scaled by s."""
    hr = 13 * s
    return (f'<path class="hz" d="M{cx - 18 * s},{base} Q{cx - 26 * s},{base - 30 * s} {cx - 12 * s},{base - 44 * s} '
            f'L{cx + 12 * s},{base - 44 * s} Q{cx + 26 * s},{base - 30 * s} {cx + 18 * s},{base} Z"/>'
            f'<circle class="hz" cx="{cx}" cy="{base - 44 * s - hr + 4 * s}" r="{hr}"/>'
            f'<ellipse class="pf pf-bxs" cx="{cx}" cy="{base - 20 * s}" rx="{9 * s}" ry="{11 * s}"/>')


def drawing_pat_dolls():
    b, t = kit.box, kit.text
    layers = [(10, 10, 740, 300, "bx", "Trace", ["every try", "written down"]),
              (130, 30, 600, 260, "bxs", "Cache", ["seen it?", "answer at once"]),
              (250, 50, 460, 220, "bx", "Retry", ["failed? wait,", "try again"]),
              (370, 70, 320, 180, "bxs", "Timeout", ["too slow?", "give up"])]
    d = ""
    for x, y, w, h, k, name, sub in layers:
        d += f'<rect class="pf pf-{k}" x="{x + 4}" y="{y + 4}" width="{w - 2}" height="{h - 2}" rx="14"/>'
        d += f'<rect class="{k} ol" x="{x}" y="{y}" width="{w}" height="{h}" rx="14"/>'
        d += t(x + 60, 140, name, "bd", "middle") + t(x + 60, 166, sub, "sm", "middle")
    d += b(492, 110, 180, 100, "The tool call", "get_order", "solid")
    d += _doll(805, 150, 1.25) + _doll(880, 150, 1.0) + _doll(942, 150, 0.75)
    d += t(875, 200, ["each doll adds", "one job; the call", "inside never", "changes"], "sm", "middle")
    return figure(1000, 320, d, "Nested layers like Russian dolls around a tool call, get_order. From the outside in: trace, every try written down; cache, answer at once if seen before; retry, wait and try again; timeout, give up if too slow. Three small dolls stand beside it.",
                  "Decorators. Each wrapper has the same shape as the call inside, adds one job, and passes the call inward.")


def drawing_pat_exam():
    b, t = kit.box, kit.text
    d = ('<path class="hz" d="M20,20 L320,20 L360,60 L360,305 L20,305 Z"/>'
         '<path class="ln" d="M320,20 L320,60 L360,60"/>')
    d += t(40, 56, "THE MODEL PORT'S EXAM", "lbl")
    d += t(40, 104, ["Row 1: a text answer", "comes back typed, with", "its usage"], "tx")
    d += t(40, 192, ["Row 2: a tool call", "comes back with parsed", "arguments"], "tx")
    d += t(40, 286, "one sheet, every adapter", "sm")
    names = [("scripted", "bx"), ("litellm-proxy", "bx"), ("groq-direct", "bx"), ("apim-ai-gateway", "bx"),
             ("your new adapter", "bxm")]
    for i, (name, k) in enumerate(names):
        y = 20 + i * 60
        d += f'<line class="lnd" x1="362" y1="165" x2="468" y2="{y + 24}"/>'
        d += b(470, y, 260, 48, name, "", k)
        if k == "bxm":
            d += t(780, y + 31, "must pass both", "sm")
        else:
            d += _tick(752, y + 24) + _tick(792, y + 24)
    return figure(1000, 320, d, "An exam sheet for the model port with two rows: a text answer comes back typed with its usage, and a tool call comes back with parsed arguments. Dashed lines lead to five desks: scripted, litellm-proxy, groq-direct and apim-ai-gateway each have two ticks; your new adapter must pass both.",
                  "Contract tests. Every adapter for a port sits the same exam, row by row, before it may be bound in YAML.")


DRAWINGS = {"pat-socket": drawing_pat_socket, "pat-turn": drawing_pat_turn, "pat-gates": drawing_pat_gates,
            "pat-dolls": drawing_pat_dolls, "pat-exam": drawing_pat_exam}
