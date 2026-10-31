"""Drawings for 'If you can't replay it, you can't fix it: tracing autonomous agents'.
kit, figure, E and ROOT are given as globals by build.py."""


def _person(cx, top):
    """A small stick person whose head centre is at (cx, top)."""
    return (f'<circle class="hz" cx="{cx}" cy="{top}" r="14"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 14}" x2="{cx}" y2="{top + 52}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 52}" x2="{cx - 12}" y2="{top + 76}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 52}" x2="{cx + 12}" y2="{top + 76}"/>')


def drawing_trace_detective():
    b, t = kit.box, kit.text
    d = b(10, 40, 230, 110, "The complaint", ["\"the assistant said my", "payout was on its way\""], "bxm")
    # the detective: stick person, hat, magnifying glass
    cx = 330
    d += _person(cx, 90)
    d += f'<path class="hk" d="M{cx - 22},80 L{cx + 22},80 L{cx + 14},68 L{cx - 14},68 Z"/>'
    d += f'<line class="lnc" x1="{cx}" y1="122" x2="{cx + 34}" y2="108"/>'
    d += f'<line class="lnc" x1="{cx + 34}" y1="108" x2="{cx + 48}" y2="98"/><circle class="hz" cx="{cx + 60}" cy="88" r="16"/>'
    d += t(cx, 200, "the on-call engineer", "sm", "middle")
    # evidence board 1: only the final answer
    d += b(440, 20, 250, 180, "Only the reply", ["one line of text,", "no steps, no times"], "bxm")
    d += t(565, 178, "? ? ?", "bd", "middle")
    # evidence board 2: a trace
    d += b(720, 20, 270, 180, "A trace", ["every model call,", "tool call and check,", "in order, with times"], "bx")
    d += t(855, 180, "clues", "bd", "middle")
    d += t(565, 228, "a guess", "sm", "middle") + t(855, 228, "a fix", "sm", "middle")
    return figure(1000, 240, d, "A complaint about a bad answer. A detective engineer looks at two evidence boards: one holds only the final reply and question marks; the other holds a trace of every model call, tool call and check, which gives clues.",
                  "With only the reply, you can guess. With a trace, you can find the step that went wrong.")


def drawing_trace_tree():
    b, t, p = kit.box, kit.text, kit.path
    rows = [(0, "agent.turn", "Rohan asks about CLM-019900; how it ended", "solid"),
            (1, "agent.run", "3 model calls, $0.00087, why it ended", "bx"),
            (2, "gen_ai.chat", "step 1: model asks for get_claim", "bx"),
            (2, "agent.tool", "get_claim: outcome ok, result size", "bx"),
            (2, "gen_ai.chat", "step 2: model asks for request_payout", "bx"),
            (2, "agent.policy", "before the tool: blocked, nobody asked", "bxs"),
            (2, "gen_ai.chat", "step 3: model writes the reply", "bx")]
    d = ""
    for i, (lvl, name, note, kind) in enumerate(rows):
        x, y = 20 + lvl * 70, 14 + i * 54
        d += b(x, y, 200, 40, name, "", kind)
        d += t(x + 216, y + 26, note, "sm")
        if lvl:
            d += p(f"M{x - 40},{y - 14} L{x - 40},{y + 20} L{x - 4},{y + 20}", "ln", end=False)
    d += t(980, 30, "one trace", "bd", "end") + t(980, 52, "per turn", "bd", "end")
    return figure(1000, 400, d, "A trace tree for one turn. agent.turn at the top, agent.run inside it, and inside that three gen_ai.chat model calls, one agent.tool call to get_claim, and one agent.policy check that blocked request_payout.",
                  "One turn of the claims assistant as a trace: the turn, the run, and a span for every model call, tool call and check.")


def drawing_trace_span_card():
    t = kit.text
    cards = [("gen_ai.chat", "a model call", ["model asked for, model that answered", "config fingerprint (prompt version)",
                                               "tokens in, tokens out", "cost of this call", "how long it took"]),
             ("agent.tool", "a tool call", ["tool name: get_claim", "changes something? yes or no",
                                            "idempotency key", "outcome: ok, refused, error", "result cut to size? how much"]),
             ("agent.policy", "a check", ["where it sits: before the tool", "which rule blocked it",
                                          "did the check itself fail?", "did it time out?", "how long it took"])]
    d = ""
    for i, (name, what, fields) in enumerate(cards):
        x = 10 + i * 330
        d += f'<rect class="pf pf-bxs" x="{x + 5}" y="25" width="310" height="250" rx="10"/>'
        d += f'<rect class="hz" x="{x}" y="20" width="310" height="250" rx="10"/>'
        d += f'<circle class="hz" cx="{x + 290}" cy="40" r="7"/>'
        d += t(x + 20, 52, name, "bd") + t(x + 20, 74, what, "sm")
        d += f'<line class="lnd" x1="{x + 16}" y1="88" x2="{x + 294}" y2="88"/>'
        for j, f in enumerate(fields):
            y = 118 + j * 34
            d += f'<line class="ln" x1="{x + 20}" y1="{y + 8}" x2="{x + 290}" y2="{y + 8}"/>'
            d += t(x + 20, y, f, "tx")
    return figure(1000, 285, d, "Three index cards. A model call span holds the model, a config fingerprint, tokens, cost and time. A tool call span holds the tool name, whether it changes something, an idempotency key, the outcome and whether the result was cut. A check span holds where it sits, which rule blocked, and whether it failed or timed out.",
                  "What one span holds, for the three kinds that matter most. None of these fields contains the customer's words.")


def drawing_trace_bins():
    t = kit.text
    bins = [("STORE", "on every turn", ["span names and times", "model, tokens, cost", "tool names, outcomes", "which check fired"], "zg"),
            ("REDACT", "only on chosen turns", ["the customer's words", "the reply", "tool arguments, results", "masked, then capped"], "zy"),
            ("DROP", "never kept", ["Aadhaar, PAN, card", "and phone numbers", "passwords and tokens", "whole documents"], "zr")]
    d = ""
    for i, (name, when, items, zone) in enumerate(bins):
        cx = 170 + i * 330
        for j, it in enumerate(items):
            d += t(cx, 30 + j * 24, it, "tx", "middle")
        d += f'<path class="{zone}" d="M{cx - 110},140 L{cx + 110},140 L{cx + 90},290 L{cx - 90},290 Z"/>'
        d += f'<path class="hz" d="M{cx - 110},140 L{cx + 110},140 L{cx + 90},290 L{cx - 90},290 Z" fill-opacity="0"/>'
        d += f'<rect class="hz" x="{cx - 122}" y="126" width="244" height="16" rx="4"/>'
        d += t(cx, 205, name, "bd", "middle") + t(cx, 230, when, "sm", "middle")
    return figure(1000, 305, d, "Three bins. Store, on every turn: span names, times, model, tokens, cost, tool names, outcomes and which check fired. Redact, only on chosen turns: the customer's words, the reply, tool arguments and results, masked then capped. Drop, never kept: identity numbers, card and phone numbers, passwords, tokens and whole documents.",
                  "Sort every field into one of three bins before you write the first span.")


def drawing_trace_replay():
    b, a, t, n = kit.box, kit.arrow, kit.text, kit.num
    frames = [("Rohan asks", ["what did the", "assessor write?"], "bxm"), ("Model", ["asks for", "get_claim"], "bx"),
              ("Tool", ["claim + a", "planted note"], "bx"), ("Model", ["asks for", "request_payout"], "solid"),
              ("Check", ["blocked:", "nobody asked"], "bxs"), ("Reply", ["the assessor's", "words, ₹0 paid"], "bx")]
    d = '<rect class="hz" x="4" y="40" width="992" height="150" rx="6"/>'
    d += "".join(f'<rect class="hk" x="{16 + k * 38}" y="45" width="14" height="7" rx="2"/>'
                 f'<rect class="hk" x="{16 + k * 38}" y="173" width="14" height="9" rx="2"/>' for k in range(26))
    for i, (title, sub, k) in enumerate(frames):
        x = 14 + i * 164
        d += b(x, 66, 148, 100, title, sub, k) + n(x + 10, 66, i + 1)
    # play / pause controls
    d += '<path class="hz" d="M330,212 L330,244 L356,228 Z"/>'
    d += '<rect class="hz" x="380" y="212" width="9" height="32" rx="2"/><rect class="hz" x="396" y="212" width="9" height="32" rx="2"/>'
    d += '<path class="hz" d="M430,212 L430,244 L450,228 Z"/><line class="lnc" x1="455" y1="212" x2="455" y2="244"/>'
    d += t(470, 234, "step", "sm")
    d += a(576, 262, 576, 172)
    d += t(600, 280, "pause here: this is the step to explain, and the test to write", "sm")
    d += t(500, 24, "a captured turn, stepped through with its recorded model answers: no live model, $0", "sm", "middle")
    return figure(1000, 295, d, "A film strip of six frames: Rohan asks, the model asks for get_claim, the tool returns the claim with a planted note, the model asks for request_payout, the check blocks it, the reply gives the assessor's words with nothing paid. Play, pause and step buttons sit below, with an arrow pointing at the fourth frame.",
                  "Replay is a film you can pause. The frame where it went wrong becomes the next test.")


DRAWINGS = {"trace-detective": drawing_trace_detective, "trace-tree": drawing_trace_tree,
            "trace-span-card": drawing_trace_span_card, "trace-bins": drawing_trace_bins,
            "trace-replay": drawing_trace_replay}
