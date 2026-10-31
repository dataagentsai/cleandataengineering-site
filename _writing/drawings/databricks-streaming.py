"""Drawings for 'Streaming on Databricks without the pain'. kit, figure, E and ROOT are injected by build.py."""


def drawing_stream_need():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(500, 22, "ask in order; stop at the first answer that fits", "sm", "middle")
    d += kit.num(30, 75, 1) + b(50, 40, 260, 80, "Act within minutes?", "someone acts on it fast", "bx")
    d += kit.num(30, 185, 2) + b(50, 150, 260, 80, "Needed within the hour?", "most dashboards are", "bx")
    d += kit.num(30, 295, 3) + b(50, 260, 260, 80, "Hours old is fine?", "or it arrives in drops", "bx")
    d += a(180, 122, 180, 148, "no", lx=196, ly=140, anchor="start")
    d += a(180, 232, 180, 258, "no", lx=196, ly=250, anchor="start")
    d += a(312, 80, 618, 80, "yes")
    d += a(312, 190, 618, 190, "yes")
    d += a(312, 300, 618, 300, "yes")
    d += b(620, 40, 360, 80, "Streaming", "seconds fresh, always on", "solid")
    d += b(620, 150, 360, 80, "Frequent batch", "every 5 to 15 minutes", "bxs")
    d += b(620, 260, 360, 80, "Batch", "hourly or daily, simplest", "bx")
    d += t(465, 368, "cost and effort go up as you climb", "sm", "middle")
    d += '<line class="lnd" x1="600" y1="335" x2="600" y2="50"/>'
    return figure(1000, 385, d, "Three questions on the left: does someone act within minutes, is it needed within the hour, is hours old fine or does it arrive in drops. Answers lead right to streaming, frequent batch, or batch.",
                  "Do you really need streaming? Most answers land on the middle box.")


def drawing_stream_two_speeds():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(500, 22, "the same layers, the same rules; only the speed changes", "sm", "middle")
    names = [("Bronze", "bx"), ("Silver", "bx"), ("Gold", "bxs")]
    for i, (n, k) in enumerate(names):
        x = 250 + i * 250
        d += b(x, 105, 200, 130, n, "same contract, same checks", k)
    # slow lane above, fast lane below
    d += b(20, 40, 180, 60, "Daily files", "slow lane", "bxm")
    d += b(20, 240, 180, 60, "Event stream", "fast lane", "bxm")
    d += kit.path("M202,70 Q235,72 248,128", "lnd")
    d += kit.path("M202,270 Q235,268 248,212", "lnc")
    for i in range(2):
        x = 452 + i * 250
        d += a(x, 135, x + 46, 135, kind="lnd") + a(x, 205, x + 46, 205, kind="lnc")
    d += t(600, 75, "dashed: most tables, in batches, say once a day", "sm", "middle")
    d += t(600, 275, "thick: a few hot tables, flowing all the time", "sm", "middle")
    return figure(1000, 330, d, "Bronze, silver and gold boxes in a row. A dashed slow lane from daily files enters once a day. A thick fast lane from an event stream flows through continuously.",
                  "One medallion, two speeds. Hot tables use the fast lane through the very same layers.")


def drawing_stream_bookmark():
    b, a, t = kit.box, kit.arrow, kit.text
    # an open book with a bookmark
    d = ('<path class="hz" d="M60,90 Q160,70 250,95 L250,285 Q160,262 60,280 Z"/>'
         '<path class="hz" d="M250,95 Q340,70 440,90 L440,280 Q340,262 250,285 Z"/>')
    d += "".join(f'<line class="ln" x1="80" y1="{120 + j * 26}" x2="230" y2="{122 + j * 26}"/>' for j in range(6))
    d += "".join(f'<line class="ln" x1="270" y1="{122 + j * 26}" x2="420" y2="{120 + j * 26}"/>' for j in range(3))
    d += '<path class="pf pf-bxs" d="M330,60 L360,60 L360,175 L345,160 L330,175 Z"/><path class="ln" d="M330,60 L360,60 L360,175 L345,160 L330,175 Z"/>'
    d += t(250, 320, "read up to here; carry on from here", "sm", "middle")
    d += b(520, 40, 200, 80, "Checkpoint", ["what's done,", "running totals"], "solid")
    d += b(520, 160, 200, 80, "Restart", "opens at the bookmark", "bx")
    d += a(620, 122, 620, 158)
    d += b(760, 160, 220, 80, "Delta table", "each row once", "bxs")
    d += a(722, 200, 758, 200)
    d += b(520, 270, 460, 70, "Delete it", "start over (duplicates) or skip ahead (a silent gap)", "bxm")
    d += '<line class="lnc" x1="532" y1="282" x2="556" y2="306"/><line class="lnc" x1="556" y1="282" x2="532" y2="306"/>'
    return figure(1000, 350, d, "An open book with a bookmark. Beside it: the checkpoint records what is done; a restart opens at the bookmark and writes each row once to a Delta table. Deleting the checkpoint means starting over or skipping ahead.",
                  "A checkpoint is a bookmark. Lose it and the stream either rereads the book or skips chapters.")


def drawing_stream_train():
    b, a, t = kit.box, kit.arrow, kit.text
    # platform and train
    d = '<line class="lnc" x1="20" y1="250" x2="980" y2="250"/>'
    d += '<rect class="hz" x="40" y="130" width="420" height="110" rx="14"/>'
    d += "".join(f'<rect class="pf pf-bx" x="{62 + j * 95}" y="150" width="70" height="44" rx="4"/>'
                 f'<rect class="ln" x="{62 + j * 95}" y="150" width="70" height="44" rx="4" fill="none"/>' for j in range(4))
    d += "".join(f'<circle class="hz" cx="{90 + j * 110}" cy="246" r="12"/>' for j in range(4))
    d += t(250, 225, "the 10:05 window", "bd", "middle")
    # clock
    d += '<circle class="hz" cx="560" cy="90" r="34"/><line class="lnc" x1="560" y1="90" x2="560" y2="66"/><line class="lnc" x1="560" y1="90" x2="578" y2="98"/>'
    d += t(560, 150, ["doors held", "10 minutes"], "sm", "middle")

    def person(x, y):
        return (f'<circle class="hz" cx="{x}" cy="{y}" r="10"/><line class="lnc" x1="{x}" y1="{y + 10}" x2="{x}" y2="{y + 34}"/>'
                f'<line class="lnc" x1="{x}" y1="{y + 34}" x2="{x - 9}" y2="{y + 50}"/><line class="lnc" x1="{x}" y1="{y + 34}" x2="{x + 9}" y2="{y + 50}"/>'
                f'<line class="lnc" x1="{x}" y1="{y + 18}" x2="{x - 14}" y2="{y + 10}"/>')
    d += person(650, 188) + a(630, 205, 480, 205)
    d += t(650, 280, ["4 minutes late:", "counted"], "sm", "middle")
    d += person(880, 188)
    d += t(880, 280, ["25 minutes late:", "missed the train"], "sm", "middle")
    d += b(700, 30, 280, 90, "The watermark", ["how long to wait;", "then close and forget"], "bxs")
    return figure(1000, 315, d, "A train for the 10:05 window holds its doors for 10 minutes. A passenger four minutes late gets on and is counted. One twenty-five minutes late misses it.",
                  "A watermark is a train that waits a fixed time. Without one, the train waits for ever and the platform fills up.")


def drawing_stream_tap():
    b, t = kit.box, kit.text

    def tap(cx, drops, flow):
        s = (f'<rect class="hz" x="{cx - 60}" y="60" width="90" height="26" rx="6"/>'
             f'<path class="hz" d="M{cx + 30},66 L{cx + 60},66 Q{cx + 72},66 {cx + 72},80 L{cx + 72},100 L{cx + 52},100 L{cx + 52},86 L{cx + 30},86 Z"/>'
             f'<rect class="hz" x="{cx - 24}" y="44" width="20" height="16" rx="3"/>')
        if flow:
            s += f'<rect class="pf pf-bx" x="{cx + 54}" y="102" width="16" height="70"/><line class="ln" x1="{cx + 54}" y1="102" x2="{cx + 54}" y2="172"/><line class="ln" x1="{cx + 70}" y1="102" x2="{cx + 70}" y2="172"/>'
        for j in range(drops):
            s += f'<ellipse class="pf pf-bx" cx="{cx + 62}" cy="{118 + j * 22}" rx="6" ry="8"/><ellipse class="ln" cx="{cx + 62}" cy="{118 + j * 22}" rx="6" ry="8" fill="none"/>'
        s += f'<path class="hz" d="M{cx + 22},180 L{cx + 102},180 L{cx + 94},212 L{cx + 30},212 Z"/>'
        return s

    d = t(500, 22, "same code, same checkpoint; only the trigger changes", "sm", "middle")
    cols = [("Always on", ["new data in seconds;", "compute never stops"], "solid", 0, True),
            ("Every N minutes", ["say every 10 minutes;", "compute still on"], "bx", 2, False),
            ("Available now", ["process what's there,", "then stop; schedule it"], "bxs", 1, False)]
    for i, (n, s, k, drops, flow) in enumerate(cols):
        x = 20 + i * 330
        d += tap(x + 100, drops, flow)
        d += b(x, 235, 300, 90, n, s, k)
    return figure(1000, 340, d, "Three taps. Always on: a steady flow, compute never stops. Every N minutes: drips on a schedule while compute stays on. Available now: one drop, then the tap is off until the next scheduled run.",
                  "Triggers as a tap. Available-now is streaming code run as a batch, and usually the right place to start.")


DRAWINGS = {"stream-need": drawing_stream_need, "stream-two-speeds": drawing_stream_two_speeds,
            "stream-bookmark": drawing_stream_bookmark, "stream-train": drawing_stream_train,
            "stream-tap": drawing_stream_tap}
