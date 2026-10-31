"""Drawings for 'Your Databricks cluster scales up and never comes back down'. Globals kit, figure, E, ROOT are injected."""


def drawing_scale_balloon():
    t = kit.text
    d = t(500, 24, "the pump works every time; the valve sticks", "sm", "middle")
    # pump on the left
    d += '<rect class="hz" x="110" y="150" width="60" height="150" rx="6"/>'
    d += '<line class="lnc" x1="140" y1="150" x2="140" y2="95"/><rect class="hz" x="100" y="82" width="80" height="16" rx="6"/>'
    d += '<rect class="hz" x="90" y="300" width="100" height="14" rx="4"/>'
    d += t(140, 345, ["scale-up:", "quick and eager"], "bd", "middle")
    # hose to balloon
    d += '<path class="ln" d="M170,280 Q330,320 476,286"/>'
    # balloon
    d += '<ellipse class="pf pf-solid" cx="500" cy="150" rx="120" ry="105"/>'
    d += '<ellipse class="hz" cx="500" cy="150" rx="120" ry="105" style="fill:none"/>'
    d += '<path class="ln" d="M455,90 Q470,70 495,66"/>'
    d += t(500, 145, "10 workers", "bd", "middle")
    d += t(500, 168, "at 6 p.m.", "sm", "middle")
    # neck and valve
    d += '<path class="hz" d="M488,253 L512,253 L506,272 L494,272 Z"/>'
    d += '<rect class="bxs" x="476" y="272" width="48" height="26" rx="4"/>'
    d += '<line class="lnc" x1="470" y1="275" x2="530" y2="295"/><line class="lnc" x1="470" y1="295" x2="530" y2="275"/>'
    d += t(500, 330, ["scale-down:", "slow and cautious"], "bd", "middle")
    # stuck note
    d += '<path class="lnd" d="M540,285 Q620,300 690,270"/>'
    d += t(700, 250, ["valve stuck by:", "a high minimum,", "data on the workers,", "work that never quite stops"], "sm", "start")
    return figure(1000, 380, d, "A cartoon of a hand pump inflating a balloon labelled 10 workers at 6 p.m. The pump is labelled scale-up, quick and eager. The balloon's valve is crossed out, labelled scale-down, slow and cautious, stuck by a high minimum, data on the workers and work that never quite stops.",
                  "Autoscaling grows a cluster easily. Shrinking it is where things get stuck.")


def drawing_scale_day_line():
    t = kit.text
    x0, x1 = 120, 940
    y_top, y_base = 70, 270  # 10 workers at top, 0 at base
    hrs0, hrs1 = 6, 22
    def X(h):
        return x0 + (h - hrs0) * (x1 - x0) / (hrs1 - hrs0)
    def Y(w):
        return y_base - w * (y_base - y_top) / 10
    d = t(500, 24, "workers on a shared cluster, minimum 2, maximum 10 (illustrative)", "sm", "middle")
    # axes
    d += f'<line class="ln" x1="{x0}" y1="{y_base}" x2="{x1}" y2="{y_base}"/>'
    d += f'<line class="ln" x1="{x0}" y1="{y_base}" x2="{x0}" y2="{y_top - 10}"/>'
    for w in (0, 2, 10):
        d += f'<line class="ln" x1="{x0 - 6}" y1="{Y(w):.0f}" x2="{x0}" y2="{Y(w):.0f}"/>' + t(x0 - 12, Y(w) + 5, str(w), "sm", "end")
    for h, lbl in ((6, "6 a.m."), (9, "9 a.m."), (12, "noon"), (15, "3 p.m."), (18, "6 p.m."), (21, "9 p.m.")):
        d += t(X(h), y_base + 50, lbl, "sm", "middle")
    # the paid-for gap between the lines
    gap = [(9.3, 10), (21, 10), (21, 2), (10.8, 2), (10, 10)]
    d += '<path class="zr" opacity="0.45" d="' + " ".join(f"{'M' if i == 0 else 'L'}{X(h):.0f},{Y(w):.0f}" for i, (h, w) in enumerate(gap)) + ' Z"/>'
    # sticky line
    pts = [(6, 2), (9, 2), (9.3, 10), (21, 10), (21, 0), (22, 0)]
    dd = " ".join(f"{'M' if i == 0 else 'L'}{X(h):.0f},{Y(w):.0f}" for i, (h, w) in enumerate(pts))
    d += f'<path class="lnc" d="{dd}" style="fill:none"/>'
    # healthy line
    pts2 = [(9.3, 10), (10, 10), (10.8, 2), (22, 2)]
    dd2 = " ".join(f"{'M' if i == 0 else 'L'}{X(h):.0f},{Y(w):.0f}" for i, (h, w) in enumerate(pts2))
    d += f'<path class="lnd" d="{dd2}" style="fill:none;stroke-width:3"/>'
    # labels
    d += t(X(15), Y(10) - 14, "sticky (thick line): stays at 10 until it is terminated at night", "bd", "middle")
    d += t(X(15), Y(2) + 26, "healthy (dashed line): back to 2 once the load is done", "tx", "middle")
    d += t(X(15), Y(6) + 5, "shaded: idle workers you pay for", "bd", "middle")
    return figure(1000, 335, d, "A line chart of workers from 6 a.m. to 10 p.m. Both lines rise from 2 to 10 at 9 a.m. for the morning load. The healthy dashed line falls back to 2 by about 11 a.m. The sticky thick line stays at 10 until 9 p.m.",
                  "Same morning load, two clusters. The area between the lines is the cost.")


def drawing_scale_why_stay():
    b, t = kit.box, kit.text
    d = t(500, 24, "three small reasons a worker is never removed", "sm", "middle")
    d += kit.num(160, 60, 1) + b(40, 80, 240, 90, "A high floor", ["the minimum is 8,", "so 8 is the smallest"], "bx")
    d += kit.num(500, 60, 2) + b(380, 80, 240, 90, "Data on board", ["cached tables and", "shuffle files"], "bxs")
    d += kit.num(840, 60, 3) + b(720, 80, 240, 90, "Never quite idle", ["a stream, or a trickle", "of small queries"], "bx")
    # 1: floor - workers standing on a raised floor
    d += '<rect class="hz" x="70" y="250" width="180" height="40" rx="4"/>'
    for i in range(6):
        d += f'<rect class="pf pf-solid" x="{80 + i * 28}" y="{222}" width="22" height="26" rx="3"/>'
    d += t(160, 276, "minimum workers", "sm", "middle")
    d += '<line class="lnd" x1="60" y1="310" x2="260" y2="310"/>'
    d += t(160, 330, "zero is down here", "sm", "middle")
    # 2: worker carrying boxes
    d += '<rect class="hz" x="460" y="225" width="80" height="80" rx="8"/>'
    d += t(500, 320, "a worker", "sm", "middle")
    for j, (x, y) in enumerate(((470, 240), (500, 240), (470, 270), (500, 270))):
        d += f'<rect class="bxs" x="{x}" y="{y}" width="24" height="22" rx="2"/>'
    d += t(560, 255, ["remove me and", "this work is redone"], "sm", "start")
    # 3: a tap dripping into a worker
    d += '<rect class="hz" x="800" y="200" width="60" height="16" rx="4"/><rect class="hz" x="822" y="216" width="16" height="14" rx="2"/>'
    for k, y in enumerate((242, 262, 282)):
        d += f'<path class="bxs" d="M826,{y} q4,-8 8,0 a4,4 0 1,1 -8,0 Z"/>'
    d += '<rect class="hz" x="790" y="295" width="80" height="22" rx="4"/>'
    d += t(880, 250, ["a little work,", "all day long"], "sm", "start")
    return figure(1000, 345, d, "Three numbered panels. One: a high floor, workers standing on a raised platform labelled minimum workers. Two: data on board, a worker carrying cached tables and shuffle files, labelled remove me and this work is redone. Three: never quite idle, a tap dripping a little work all day.",
                  "Most sticky clusters come down to one of these three: a floor set too high, data on the workers, or work that never fully stops.")


def drawing_scale_fix_card():
    t = kit.text
    d = t(500, 24, "pin it next to your cluster settings", "sm", "middle")
    d += '<rect class="hz" x="250" y="45" width="500" height="330" rx="10"/>'
    d += '<rect class="pf pf-bxs" x="258" y="53" width="484" height="44" rx="6"/>'
    d += t(500, 82, "Make it come back down", "bd", "middle")
    items = ["Job compute for each scheduled job", "A minimum of 1 or 2 for batch work", "Auto-termination on every all-purpose cluster",
             "A cluster policy that enforces all of this", "Serverless where it fits", "Streams on their own fixed-size cluster",
             "Watch the event log and billing tables"]
    for i, s in enumerate(items):
        y = 125 + i * 36
        d += f'<rect class="hz" x="285" y="{y - 14}" width="18" height="18" rx="3"/>'
        d += f'<path class="lnc" d="M288,{y - 5} L293,{y} L301,{y - 12}" style="fill:none"/>'
        d += t(320, y + 1, s, "tx", "start")
    # pin
    d += '<circle class="bxs" cx="500" cy="45" r="9"/>'
    return figure(1000, 390, d, "A pinned checklist card titled Make it come back down, with seven ticked items: job compute for each scheduled job, a minimum of 1 or 2 for batch work, auto-termination on every all-purpose cluster, a cluster policy that enforces all of this, serverless where it fits, streams on their own fixed-size cluster, watch the event log and billing tables.",
                  "The fix checklist. A cluster policy turns most of these from good habits into defaults.")


DRAWINGS = {
    "scale-balloon": drawing_scale_balloon,
    "scale-day-line": drawing_scale_day_line,
    "scale-why-stay": drawing_scale_why_stay,
    "scale-fix-card": drawing_scale_fix_card,
}
