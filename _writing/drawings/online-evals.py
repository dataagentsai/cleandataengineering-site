"""Drawings for 'It passed offline. Now watch it live: online evals and monitoring'.
kit, figure, E and ROOT are given as globals by build.py."""
import math


def _pt(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy - r * math.sin(a)


def _gauge(cx, cy, label, sub, needle_deg):
    t = kit.text
    r = 70
    d = f'<circle class="hz" cx="{cx}" cy="{cy}" r="{r}"/>'
    # the red zone, top right of the dial
    x0, y0 = _pt(cx, cy, 60, 0)
    x1, y1 = _pt(cx, cy, 60, 40)
    d += f'<path class="zr" d="M{cx},{cy} L{x0:.1f},{y0:.1f} A60,60 0 0 0 {x1:.1f},{y1:.1f} Z"/>'
    for deg in (180, 135, 90, 45, 0):
        a0, b0 = _pt(cx, cy, 58, deg)
        a1, b1 = _pt(cx, cy, 68, deg)
        d += f'<line class="ln" x1="{a0:.1f}" y1="{b0:.1f}" x2="{a1:.1f}" y2="{b1:.1f}"/>'
    nx, ny = _pt(cx, cy, 52, needle_deg)
    d += f'<line class="lnc" x1="{cx}" y1="{cy}" x2="{nx:.1f}" y2="{ny:.1f}"/>'
    d += f'<circle class="hk" cx="{cx}" cy="{cy}" r="6"/>'
    d += t(cx, cy + 98, label, "bd", "middle") + t(cx, cy + 118, sub, "sm", "middle")
    return d


def drawing_live_dashboard():
    t = kit.text
    d = t(500, 24, "you glance at four needles, and a bell rings when one leaves its normal range", "sm", "middle")
    d += '<rect class="hz" x="40" y="44" width="920" height="250" rx="60"/>'
    gauges = [("Cost", "per task", 120), ("Latency", "slowest turns", 100),
              ("Hand-offs", "to a person", 140), ("Guardrail hits", "refusals per rule", 22)]
    for i, (lab, sub, deg) in enumerate(gauges):
        d += _gauge(170 + i * 220, 160, lab, sub, deg)
    # a warning lamp over the last gauge
    d += '<path class="zr" d="M830,58 L846,84 L814,84 Z"/>'
    d += '<path class="hz" d="M830,58 L846,84 L814,84 Z" fill-opacity="0"/>'
    d += t(830, 81, "!", "bd", "middle")
    d += t(500, 322, "one rule refusing far more turns than usual: the needle is in the red", "sm", "middle")
    return figure(1000, 335, d, "A car dashboard with four round gauges: cost per task, latency of the slowest turns, hand-offs to a person, and guardrail hits per rule. Each dial has a red zone at the top right. The guardrail-hits needle sits in the red and a warning lamp is lit above it.",
                  "Monitoring is a dashboard you glance at, plus alarms that ring when a needle leaves its normal range.")


def drawing_live_two_speeds():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(20, 30, "INLINE: EVERY TURN", "lbl") + t(520, 30, "ONLINE: AFTER THE FACT", "lbl")
    # inline
    d += b(10, 60, 130, 80, "A turn", "one reply", "bx")
    d += a(142, 100, 178, 100)
    d += b(180, 50, 160, 100, "Quick checks", ["8 points, rules,", "under 50 ms each"], "bxs")
    d += a(342, 100, 378, 100)
    d += b(380, 60, 100, 80, "Reply", "or safe reply", "bx")
    # stopwatch
    d += ('<circle class="hz" cx="260" cy="212" r="28"/>'
          '<rect class="hz" x="253" y="176" width="14" height="8" rx="2"/>'
          '<line class="lnc" x1="260" y1="212" x2="272" y2="198"/>')
    d += t(245, 270, ["milliseconds: it can still", "change the reply"], "sm", "middle")
    d += '<line class="lnd" x1="500" y1="44" x2="500" y2="300"/>'
    # online
    for k in range(3):
        d += f'<rect class="hz" x="{536 + k * 8}" y="{190 - k * 8}" width="64" height="40" rx="5"/>'
    d += b(520, 60, 130, 80, "Finished turns", "stored traces", "bx")
    d += a(652, 100, 698, 100)
    d += t(675, 90, "sample", "sm", "middle")
    d += b(700, 50, 150, 100, "Slow scoring", ["rules every 60 s,", "judge: planned"], "solid")
    d += a(852, 100, 878, 100)
    d += b(880, 60, 110, 80, "Alert", "page, ticket", "bxm")
    # magnifying glass
    d += ('<circle class="hz" cx="775" cy="205" r="24"/>'
          '<line class="lnc" x1="792" y1="222" x2="812" y2="242"/>')
    d += t(755, 270, ["minutes: the reply has gone,", "so it can only alert"], "sm", "middle")
    return figure(1000, 310, d, "Left, inline: a turn passes through quick checks at 8 points, rules under 50 milliseconds each, before the reply or a safe reply; a stopwatch shows it works in milliseconds and can still change the reply. Right, online: finished turns are stored as traces, a sample is scored slowly by rules every 60 seconds, with a sampled judge planned, and the result is an alert; a magnifying glass shows it works minutes later and can only alert.",
                  "Inline checks every turn fast and can block. Online scores finished turns slowly and can only raise an alarm.")


def drawing_live_baseline():
    t = kit.text
    xs = list(range(60, 861, 80))
    upper = [128, 124, 134, 127, 121, 130, 125, 131, 127, 123, 128]
    d = t(60, 26, "SHARE OF TURNS ENDING ESCALATED, REFUSED OR FAILED", "lbl")
    top = " ".join(f"{x},{u}" for x, u in zip(xs, upper))
    bot = " ".join(f"{x},{u + 62}" for x, u in reversed(list(zip(xs, upper))))
    d += f'<polygon class="pf pf-bx" points="{top} {bot}"/>'
    d += f'<polyline class="lnd" fill="none" points="{top}"/>'
    d += f'<polyline class="lnd" fill="none" points="{bot}"/>'
    line = [(60, 160), (140, 152), (220, 166), (300, 158), (380, 150), (460, 162), (540, 155),
            (620, 162), (700, 158), (780, 148), (820, 118), (860, 84)]
    d += '<polyline class="lnc" fill="none" points="' + " ".join(f"{x},{y}" for x, y in line) + '"/>'
    d += '<circle class="zr" cx="860" cy="84" r="9"/><circle class="hz" cx="860" cy="84" r="9" fill-opacity="0"/>'
    d += '<line class="ln" x1="40" y1="240" x2="900" y2="240"/>'
    d += t(60, 262, "a week ago", "sm", "middle") + t(860, 262, "now", "sm", "middle")
    d += t(240, 218, "last week's normal range", "sm", "middle")
    # bell
    d += ('<path class="hz" d="M930,70 Q930,48 950,46 Q970,48 970,70 L974,96 L926,96 Z"/>'
          '<circle class="hk" cx="950" cy="103" r="5"/><circle class="hz" cx="950" cy="42" r="4"/>'
          '<line class="ln" x1="918" y1="56" x2="908" y2="50"/><line class="ln" x1="982" y1="56" x2="992" y2="50"/>')
    d += '<line class="lnd" x1="872" y1="82" x2="920" y2="76"/>'
    d += t(980, 300, "alert: over twice last week's share, over 15%, and at least 20 turns in the hour", "sm", "end")
    return figure(1000, 315, d, "A band across a week shows last week's normal range for the share of turns that ended escalated, refused or failed. Today's line stays inside the band, then climbs out of it at the right. A bell rings at the point where it leaves. The alert fires at over twice last week's share, over 15 percent, with at least 20 turns in the hour.",
                  "Compare today with the agent's own normal, not with a fixed number, and ask for enough traffic before you ring the bell.")


def drawing_live_canary():
    b, a, t = kit.box, kit.arrow, kit.text
    # cage
    d = '<path class="hz" d="M30,230 L30,110 Q100,40 170,110 L170,230 Z"/>'
    d += ''.join(f'<line class="ln" x1="{x}" y1="{100 if x in (65, 135) else 80}" x2="{x}" y2="230"/>' for x in (65, 100, 135))
    d += '<line class="lnc" x1="20" y1="230" x2="180" y2="230"/>'
    d += '<line class="ln" x1="50" y1="190" x2="150" y2="190"/>'
    # bird on the perch
    d += '<ellipse class="pf pf-bxs" cx="100" cy="168" rx="26" ry="18"/><ellipse class="hz" cx="100" cy="168" rx="26" ry="18" fill-opacity="0"/>'
    d += '<circle class="pf pf-bxs" cx="120" cy="146" r="13"/><circle class="hz" cx="120" cy="146" r="13" fill-opacity="0"/>'
    d += '<path class="hk" d="M132,144 L142,148 L132,151 Z"/><circle class="hk" cx="123" cy="143" r="2"/>'
    d += '<path class="hz" d="M76,170 L60,182 L78,180 Z"/>'
    d += t(100, 254, "a test customer", "sm", "middle")
    # clock
    d += ('<circle class="hz" cx="206" cy="222" r="16"/>'
          '<line class="ln" x1="206" y1="222" x2="206" y2="211"/><line class="ln" x1="206" y1="222" x2="214" y2="226"/>')
    d += t(228, 228, "every 10 minutes", "sm")
    d += a(172, 125, 228, 125)
    d += b(230, 80, 200, 90, "The real front door", ["sign-in, gateway,", "model, tools"], "bx")
    d += a(432, 125, 468, 125)
    d += b(470, 60, 240, 130, "Four known questions", ["order status, my orders,", "a late return,", "someone else's order"], "bxs")
    d += a(712, 105, 758, 72)
    d += a(712, 150, 758, 190)
    d += b(760, 30, 230, 80, "Right answers", ["counted, and kept", "out of every rate"], "bx")
    d += b(760, 145, 230, 95, "Fails twice running", ["or goes silent for", "25 minutes: page"], "bxm")
    return figure(1000, 270, d, "A canary in a cage stands for a test customer. Every 10 minutes it goes through the real front door (sign-in, gateway, model and tools) and asks four known questions: order status, my orders, a late return, and someone else's order. Right answers are counted and kept out of every rate. If a case fails twice running, or the canary goes silent for 25 minutes, a person is paged.",
                  "The synthetic canary. Real traffic reads a broken deployment as a quiet hour; the canary doesn't wait for a customer to notice.")


def drawing_live_loop():
    b, a, t, p = kit.box, kit.arrow, kit.text, kit.path
    steps = [("Customer comes back", ["next day, about", "the same thing"], "bxm"),
             ("Joined to the run", ["by the conversation", "id the run recorded"], "bx"),
             ("Replay the trace", ["find the step", "that went wrong"], "bx"),
             ("New golden case", ["question, tool,", "outcome, slice"], "bxs")]
    d = ""
    for i, (title, sub, k) in enumerate(steps):
        x = 10 + i * 250
        d += b(x, 40, 220, 90, title, sub, k) + kit.num(x + 12, 40, i + 1)
        if i < 3:
            d += a(x + 222, 85, x + 248, 85)
    d += b(380, 215, 240, 80, "The offline gate", "runs it before every release", "solid")
    d += p("M870,132 C 870,230 760,255 624,255", "lnc")
    d += a(378, 255, 262, 255)
    d += b(40, 215, 220, 80, "The next release", "safe from this one", "bx")
    # the growing stack of cards
    for k in range(3):
        d += f'<rect class="hz" x="{885 + k * 8}" y="{232 - k * 8}" width="56" height="38" rx="5"/>'
    d += '<rect class="pf pf-bxs" x="901" y="216" width="56" height="38" rx="5"/>'
    d += t(929, 240, "+1", "bd", "middle")
    d += t(915, 288, "the set grows", "sm", "middle")
    return figure(1000, 310, d, "Four numbered steps in a row: a customer comes back the next day about the same thing; that outcome is joined to the run by the conversation id the run recorded; the trace is replayed to find the step that went wrong; a new golden case is written with question, tool, outcome and slice. A curved arrow takes it down to the offline gate, which runs it before every release, and on to the next release. A small stack of cards gains one.",
                  "A live failure, joined back to the run that caused it, becomes a new golden case for the offline gate.")


DRAWINGS = {"live-dashboard": drawing_live_dashboard, "live-two-speeds": drawing_live_two_speeds,
            "live-baseline": drawing_live_baseline, "live-canary": drawing_live_canary,
            "live-loop": drawing_live_loop}
