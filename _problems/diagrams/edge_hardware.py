"""Problem diagrams: Edge AI and serving cost, and Chips, compute and energy. kit, figure, E and ROOT are injected."""
import math


# ---------- small cartoon helpers ----------

def _person(cx, top):
    """A small stick person; head centre at (cx, top + 13), feet at top + 80."""
    return (f'<circle class="bx" cx="{cx}" cy="{top + 13}" r="13"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 26}" x2="{cx}" y2="{top + 58}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 58}" x2="{cx - 11}" y2="{top + 80}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 58}" x2="{cx + 11}" y2="{top + 80}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 36}" x2="{cx - 16}" y2="{top + 50}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 36}" x2="{cx + 16}" y2="{top + 50}"/>')


def _bolt(x, y):
    """A lightning bolt about 20 x 40, top-left at (x, y)."""
    return (f'<path class="bxs" d="M{x + 12},{y} L{x},{y + 22} L{x + 9},{y + 22} L{x + 4},{y + 40} '
            f'L{x + 21},{y + 14} L{x + 12},{y + 14} L{x + 18},{y} Z"/>')


def _pylon(cx, top, h):
    """An electricity pylon drawn in lines; the top is at (cx, top)."""
    bot = top + h
    s = (f'<line class="ln" x1="{cx - 32}" y1="{bot}" x2="{cx - 6}" y2="{top}"/>'
         f'<line class="ln" x1="{cx + 32}" y1="{bot}" x2="{cx + 6}" y2="{top}"/>'
         f'<line class="ln" x1="{cx - 6}" y1="{top}" x2="{cx + 6}" y2="{top}"/>'
         f'<line class="lnc" x1="{cx - 34}" y1="{top + 22}" x2="{cx + 34}" y2="{top + 22}"/>')
    for i in range(1, 4):
        y0, y1 = top + h * (i - 1) / 4 + 22 * (i == 1), top + h * i / 4 + 22
        w0, w1 = 6 + 26 * (y0 - top) / h, 6 + 26 * (min(y1, bot) - top) / h
        s += f'<line class="ln" x1="{cx - w0:.0f}" y1="{y0:.0f}" x2="{cx + w1:.0f}" y2="{min(y1, bot):.0f}"/>'
        s += f'<line class="ln" x1="{cx + w0:.0f}" y1="{y0:.0f}" x2="{cx - w1:.0f}" y2="{min(y1, bot):.0f}"/>'
    return s


def _chip(x, y, w, h, fill="pf pf-bx"):
    """A chip: a square with little pins on every side."""
    s = f'<rect class="{fill}" x="{x + 3}" y="{y + 3}" width="{w}" height="{h}" rx="5"/>'
    s += f'<rect class="hz ol" x="{x}" y="{y}" width="{w}" height="{h}" rx="5" style="fill:transparent"/>'
    n = max(2, int(w // 16))
    for i in range(n):
        px = x + w * (i + 1) / (n + 1)
        py = y + h * (i + 1) / (n + 1)
        s += (f'<line class="ln" x1="{px:.0f}" y1="{y - 7}" x2="{px:.0f}" y2="{y}"/>'
              f'<line class="ln" x1="{px:.0f}" y1="{y + h}" x2="{px:.0f}" y2="{y + h + 7}"/>'
              f'<line class="ln" x1="{x - 7}" y1="{py:.0f}" x2="{x}" y2="{py:.0f}"/>'
              f'<line class="ln" x1="{x + w}" y1="{py:.0f}" x2="{x + w + 7}" y2="{py:.0f}"/>')
    return s


def _phone(x, y, w=64, h=100):
    return (f'<rect class="hz" x="{x}" y="{y}" width="{w}" height="{h}" rx="11"/>'
            f'<rect class="bxm" x="{x + 7}" y="{y + 12}" width="{w - 14}" height="{h - 28}" rx="4"/>'
            f'<circle class="hz" cx="{x + w / 2}" cy="{y + h - 8}" r="3"/>')


# ---------- edge: Edge AI and serving cost ----------

def d_low_bits():
    t = kit.text
    panels = [("16 bits", None, "smooth", "zg", "fine"),
              ("4 bits", 16, "16 steps", "zg", "nearly as good"),
              ("2 bits", 4, "4 steps", "zr", "drops sharply"),
              ("ternary", 3, "only −1, 0, +1", "zr", "drops sharply")]
    d = t(500, 24, "the same weights, stored with fewer and fewer steps", "sm", "middle")
    for i, (name, levels, steps, zone, verdict) in enumerate(panels):
        x0 = 12 + i * 247
        w, top, h = 228, 60, 140
        cy, amp = top + h / 2, 52
        d += f'<rect class="hz" x="{x0}" y="{top}" width="{w}" height="{h}" rx="12"/>'
        d += t(x0 + w / 2, top - 8, name, "bd", "middle")
        xs = [x0 + 14 + j * (w - 28) / 120 for j in range(121)]
        vs = [math.sin(j / 120 * 2 * math.pi * 1.5) for j in range(121)]
        # the true curve, dashed
        d += '<path class="lnd" d="M' + " L".join(f"{xx:.1f},{cy - amp * v:.1f}" for xx, v in zip(xs, vs)) + '"/>'
        if levels:
            q = [round((v + 1) / 2 * (levels - 1)) / (levels - 1) * 2 - 1 for v in vs]
            pts = f"M{xs[0]:.1f},{cy - amp * q[0]:.1f}"
            for j in range(1, 121):
                if q[j] != q[j - 1]:
                    pts += f" L{xs[j]:.1f},{cy - amp * q[j - 1]:.1f} L{xs[j]:.1f},{cy - amp * q[j]:.1f}"
            pts += f" L{xs[-1]:.1f},{cy - amp * q[-1]:.1f}"
            d += f'<path class="lnc" d="{pts}"/>'
        else:
            d += '<path class="lnc" d="M' + " L".join(f"{xx:.1f},{cy - amp * v:.1f}" for xx, v in zip(xs, vs)) + '"/>'
        d += t(x0 + w / 2, top + h + 24, steps, "sm", "middle")
        d += f'<rect class="{zone}" x="{x0 + 34}" y="{top + h + 36}" width="{w - 68}" height="32" rx="16"/>'
        d += t(x0 + w / 2, top + h + 58, verdict, "tx", "middle")
    d += t(500, 300, "reasoning and non-English text are the first to break", "sm", "middle")
    return figure(1000, 315, d,
                  "Four panels show the same wavy curve of model weights. At 16 bits it is smooth and quality is fine. At 4 bits it is 16 small steps and nearly as good. At 2 bits it is 4 coarse steps and at ternary only minus one, zero and plus one; quality drops sharply.",
                  "Shrinking a model works down to about 4 bits. Below that the weights become a few crude steps, and quality falls off a cliff.")


def d_kv_cache():
    b, a, t = kit.box, kit.arrow, kit.text
    d = ""
    # a growing chat
    for i, w in enumerate((90, 150, 200)):
        d += f'<rect class="hz" x="20" y="{50 + i * 52}" width="{w}" height="38" rx="16"/>'
        d += "".join(f'<line class="ln" x1="{34 + k * 22}" y1="{69 + i * 52}" x2="{48 + k * 22}" y2="{69 + i * 52}"/>'
                     for k in range(int((w - 24) / 22)))
    d += t(120, 230, ["a chat gets longer:", "every token is kept"], "sm", "middle")
    d += a(228, 140, 288, 140)
    # GPU memory
    d += '<rect class="hz" x="292" y="40" width="420" height="250" rx="14"/>'
    d += t(502, 30, "GPU memory", "bd", "middle")
    d += '<rect class="pf pf-solid" x="306" y="244" width="396" height="34" rx="6"/>'
    d += t(504, 267, "the model's weights", "tx", "middle")
    heights = [5, 8, 3, 10, 13]
    for c, n in enumerate(heights):
        x = 316 + c * 78
        for k in range(n):
            y = 226 - k * 17
            d += f'<rect class="{"bxs" if y < 52 else "pf pf-bx"}" x="{x}" y="{y}" width="58" height="14" rx="3"/>'
        d += t(x + 29, 304, f"user {c + 1}", "sm", "middle")
    # outcomes
    d += b(765, 30, 220, 95, "Compute", ["still has room", "to spare"], "bx")
    d += b(765, 160, 220, 95, "Out of memory", ["new chats must wait", "or be turned away"], "bxs")
    d += '<rect class="bxs" x="700" y="4" width="54" height="13" rx="3" transform="rotate(25 727 10)"/>'
    d += kit.path("M716,28 Q745,110 762,200", "ln")
    return figure(1000, 315, d,
                  "Chat bubbles get longer. Every token is kept in GPU memory, which holds the model's weights at the bottom and a growing stack of blocks for each user. User 5's stack spills over the top. Compute still has room to spare, but the GPU is out of memory and new chats must wait.",
                  "Every token of every conversation is kept in GPU memory while the model answers, so long chats and many users run out of memory before they run out of compute.")


def d_tinyml():
    b, a, t = kit.box, kit.arrow, kit.text
    d = b(15, 50, 220, 190, "A useful model", ["as it is usually", "trained"], "solid")
    d += a(240, 145, 340, 145)
    d += t(290, 108, ["thousands of", "times smaller"], "sm", "middle")
    # the little board
    d += '<rect class="hz" x="345" y="85" width="210" height="125" rx="10"/>'
    d += "".join(f'<circle class="hz" cx="{360 + k * 18}" cy="100" r="4"/>' for k in range(10))
    d += _chip(410, 125, 70, 55, "pf pf-bxs")
    d += t(445, 158, "KB", "bd", "middle")
    d += f'<circle class="hz" cx="530" cy="150" r="10"/><circle class="hk" cx="530" cy="150" r="3"/>'
    d += t(450, 236, "a ₹500 board: kilobytes of memory", "sm", "middle")
    # coin battery
    d += '<path class="ln" d="M557,190 Q590,195 598,228"/>'
    d += '<circle class="bx" cx="620" cy="250" r="26"/><circle class="hz" cx="620" cy="250" r="17"/>'
    d += t(620, 256, "+", "bd", "middle")
    d += t(655, 256, "a coin battery", "sm")
    # the machine making a sound
    d += '<rect class="hz" x="800" y="95" width="160" height="100" rx="10"/>'
    d += '<circle class="hz" cx="880" cy="145" r="32"/>'
    for k in range(3):
        ang = k * 120
        d += (f'<line class="lnc" x1="880" y1="145" x2="{880 + 26 * math.cos(math.radians(ang)):.0f}" '
              f'y2="{145 + 26 * math.sin(math.radians(ang)):.0f}"/>')
    d += '<rect class="hz" x="815" y="195" width="20" height="20" rx="3"/><rect class="hz" x="925" y="195" width="20" height="20" rx="3"/>'
    d += t(880, 240, "a machine humming", "sm", "middle")
    for k, r in enumerate((30, 55, 80)):
        d += f'<path class="ln" d="M{790 - r * 0.35:.0f},{145 - r} Q{780 - r:.0f},145 {790 - r * 0.35:.0f},{145 + r}"/>'
    d += t(700, 50, "listening all day for a fault", "sm", "middle")
    return figure(1000, 305, d,
                  "A big model on the left must become thousands of times smaller to fit on a ₹500 board with kilobytes of memory, powered by a coin battery, which listens all day to a humming machine for a fault.",
                  "Always-on sensing means running a useful model on a chip with kilobytes of memory and a coin battery, so the model must be thousands of times smaller.")


def d_federated():
    b, t = kit.box, kit.text
    d = b(380, 12, 240, 82, "The shared model", "on a server", "solid")
    d += t(20, 34, ["the data stays on each phone;", "only model updates travel"], "sm")
    phones = [(100, "lots of data", 6), (300, "very little data", 1), (500, "went offline", 0),
              (700, "an attacker", 3), (900, "different habits", 4)]
    for cx, label, bars in phones:
        x = cx - 32
        d += _phone(x, 190)
        for k in range(bars):
            d += f'<rect class="pf pf-bx" x="{x + 13}" y="{206 + k * 10}" width="38" height="7" rx="2"/>'
        d += t(cx, 315, label, "sm", "middle")
        tx = 420 + (cx - 100) / 800 * 160
        if label == "went offline":
            d += f'<line class="lnd" x1="{cx}" y1="186" x2="{tx:.0f}" y2="98"/>'
            d += (f'<line class="lnc" x1="{cx - 12}" y1="130" x2="{cx + 12}" y2="154"/>'
                  f'<line class="lnc" x1="{cx + 12}" y1="130" x2="{cx - 12}" y2="154"/>')
            d += (f'<line class="lnc" x1="{x + 14}" y1="215" x2="{x + 50}" y2="260"/>'
                  f'<line class="lnc" x1="{x + 50}" y1="215" x2="{x + 14}" y2="260"/>')
        elif label == "an attacker":
            d += kit.arrow(cx, 186, tx, 98, kind="lnc")
            d += (f'<path class="hk" d="M{x + 6},192 L{x + 2},172 L{x + 18},188 Z"/>'
                  f'<path class="hk" d="M{x + 58},192 L{x + 62},172 L{x + 46},188 Z"/>')
            d += t(cx - 62, 178, "a poisoned update", "sm", "end")
        else:
            d += kit.arrow(cx, 186, tx, 98)
    return figure(1000, 330, d,
                  "A shared model on a server receives updates from five phones; the data stays on the phones. One phone has lots of data, one very little, one went offline, one is an attacker sending a poisoned update, and one has different habits.",
                  "Training across many phones keeps the data private, but the phones are very different, they drop out, and some send poisoned updates.")


def d_energy():
    a, t = kit.arrow, kit.text
    d = _pylon(70, 40, 200)
    d += t(70, 268, "the grid", "sm", "middle")
    d += '<path class="ln" d="M104,62 Q160,90 222,135"/>'
    # meter
    d += '<circle class="hz" cx="270" cy="150" r="48"/>'
    d += '<path class="ln" d="M236,160 A36,36 0 0 1 304,160"/>'
    d += '<line class="lnc" x1="270" y1="165" x2="252" y2="130"/><circle class="hk" cx="270" cy="165" r="5"/>'
    d += t(270, 186, "? Wh", "bd", "middle")
    d += t(270, 225, ["watt-hours per answer:", "rarely measured"], "sm", "middle")
    d += '<line class="ln" x1="318" y1="150" x2="385" y2="150"/>'
    d += kit.box(388, 95, 200, 110, "The model", ["on a GPU", "or a laptop"], "solid")
    d += a(590, 150, 640, 150)
    d += '<path class="hz" d="M645,110 L805,110 Q815,110 815,120 L815,170 Q815,180 805,180 L690,180 L670,200 L674,180 L655,180 Q645,180 645,170 L645,120 Q645,110 655,110 Z"/>'
    d += t(730, 152, "an answer", "tx", "middle")
    # knobs that move the meter
    for k, name in enumerate(("batch size", "bits", "cache reuse")):
        cx = 420 + k * 70 if k < 2 else 568
        cx = (408, 488, 572)[k]
        d += f'<circle class="hz" cx="{cx}" cy="245" r="14"/><line class="lnc" x1="{cx}" y1="245" x2="{cx + 8}" y2="235"/>'
        d += t(cx, 282, name, "sm", "middle")
    d += t(660, 250, ["settings that", "move the meter"], "sm")
    # demand versus grid
    d += a(850, 270, 975, 60)
    d += t(905, 105, "AI demand", "sm", "end")
    d += a(850, 270, 980, 215)
    d += t(985, 250, "grid supply", "sm", "end")
    return figure(1000, 300, d,
                  "Power flows from a grid pylon through a meter showing an unknown number of watt-hours per answer, into a model on a GPU or laptop, which gives an answer. Three knobs, batch size, bits and cache reuse, move the meter. On the right, AI demand rises faster than grid supply.",
                  "AI's electricity demand is growing faster than grids, yet few people measure what one answer costs in energy, end to end.")


def d_trust():
    a, t = kit.arrow, kit.text
    d = kit.box(15, 95, 200, 110, "The approved model", ["checked and signed"], "solid")
    d += '<circle class="bxs" cx="200" cy="100" r="18"/><path class="lnc" d="M191,100 L198,107 L210,93"/>'
    d += a(218, 150, 300, 150, "installed", ly=140)
    # someone else's device
    d += '<rect class="hz" x="305" y="40" width="160" height="235" rx="22"/>'
    d += '<rect class="bxm" x="320" y="70" width="130" height="170" rx="6"/>'
    d += '<circle class="hz" cx="385" cy="258" r="6"/>'
    d += t(385, 28, "someone else's device", "sm", "middle")
    d += t(385, 140, "?", "tt", "middle").replace('class="tt"', 'class="tt" style="font-size:56px"')
    d += t(385, 180, ["swapped or", "tampered with?"], "sm", "middle")
    d += a(468, 158, 560, 158)
    # the answer, maybe edited on the way
    d += '<rect class="hz" x="565" y="112" width="180" height="92" rx="8"/>'
    d += t(655, 148, "The answer", "bd", "middle")
    d += t(655, 176, "looks fine", "sm", "middle")
    d += '<path class="bxs" d="M716,76 L770,128 L760,138 L706,86 Z"/><path class="hz" d="M770,128 L778,148 L760,138 Z"/>'
    d += t(690, 66, "changed on the way?", "sm", "end")
    d += a(748, 158, 840, 158)
    d += _person(890, 112)
    d += t(890, 98, "?", "bd", "middle")
    d += t(890, 222, ["you, far away:", "how can you tell?"], "sm", "middle")
    return figure(1000, 290, d,
                  "An approved, signed model is installed on someone else's device. Inside the device there is a big question mark: was it swapped or tampered with? The answer it sends may also be changed on the way. You, far away, cannot tell.",
                  "Once a model runs on someone else's device, it is hard to prove it is still the approved model, and that its answers were not changed.")


# ---------- hardware: Chips, compute and energy ----------

def d_memory_wall():
    b, t = kit.box, kit.text
    d = b(15, 60, 190, 130, "Memory", ["holds the model,", "feeds it slowly"], "bx")
    # conveyor belt
    d += '<line class="lnc" x1="210" y1="200" x2="660" y2="200"/><line class="lnc" x1="210" y1="226" x2="660" y2="226"/>'
    for k in range(7):
        d += f'<circle class="hz" cx="{222 + k * 72}" cy="213" r="10"/>'
    d += f'<rect class="bxs" x="290" y="176" width="44" height="24" rx="4"/>'
    d += f'<rect class="bxs" x="500" y="176" width="44" height="24" rx="4"/>'
    d += t(420, 258, "a slow conveyor brings the numbers", "sm", "middle")
    # the chip at the table
    d += _chip(700, 50, 120, 100, "pf pf-solid")
    d += '<circle class="hk" cx="737" cy="90" r="5"/><circle class="hk" cx="783" cy="90" r="5"/>'
    d += '<path class="ln" d="M745,120 Q760,110 775,120"/>'
    d += t(760, 140, "Chip", "sm", "middle")
    d += t(850, 52, "z z z", "bd")
    d += '<ellipse class="hz" cx="760" cy="215" rx="72" ry="17"/><ellipse class="hz" cx="760" cy="213" rx="48" ry="9"/>'
    d += '<line class="lnc" x1="852" y1="185" x2="852" y2="245"/><path class="ln" d="M846,185 L846,200 M858,185 L858,200"/>'
    d += '<path class="hz" d="M872,185 Q884,200 872,215 L872,245"/>'
    d += t(900, 150, ["fast, but its", "plate is empty", "most of the time"], "sm")
    return figure(1000, 275, d,
                  "On the left, memory holds the model. A slow conveyor belt carries a few boxes of numbers towards a fast chip with a face, sitting at an empty plate with a knife and fork, dozing while it waits.",
                  "Chips compute far faster than memory can feed them, so serving an LLM is mostly waiting for memory, not doing maths.")


def d_many_chips():
    t = kit.text
    d = t(500, 26, "one big model, spread over thousands of chips", "sm", "middle")

    def grid(x0, name):
        s = t(x0 + 100, 66, name, "bd", "middle")
        for r in range(3):
            for c in range(3):
                x, y = x0 + 10 + c * 68, 88 + r * 60
                s += _chip(x, y, 44, 38)
                if c < 2:
                    s += f'<line class="ln" x1="{x + 51}" y1="{y + 19}" x2="{x + 61}" y2="{y + 19}"/>'
                if r < 2:
                    s += f'<line class="ln" x1="{x + 22}" y1="{y + 45}" x2="{x + 22}" y2="{y + 53}"/>'
        return s
    d += grid(30, "rack A") + grid(760, "rack B: chips idle, waiting")
    d += '<line class="lnc" x1="260" y1="167" x2="752" y2="167"/>'
    for k in range(6):
        d += f'<rect class="bxs" x="{300 + k * 30}" y="152" width="24" height="30" rx="3"/>'
    d += t(380, 140, "data piles up between chips", "sm", "middle")
    d += '<circle class="hz" cx="590" cy="110" r="22"/><line class="ln" x1="590" y1="110" x2="590" y2="95"/><line class="ln" x1="590" y1="110" x2="602" y2="114"/>'
    d += t(590, 150, "time", "sm", "middle")
    d += _bolt(660, 88) + t(670, 150, "power", "sm", "middle")
    d += '<path class="lnd" d="M130,268 Q500,330 860,268" marker-end="url(#ar)"/>'
    d += t(500, 326, "optical links and new network designs: still being proven", "sm", "middle")
    return figure(1000, 340, d,
                  "Two racks of chips, A and B, joined by one thick link where boxes of data pile up, costing time and power. A dashed curve below is an optical link, still being proven. Chips in rack B sit idle, waiting.",
                  "Big models span many chips, and every move of data between them costs time and power.")


def d_power_cooling():
    t = kit.text
    d = _pylon(70, 50, 200)
    d += t(70, 278, "the grid", "sm", "middle")
    d += '<path class="ln" d="M104,72 Q150,95 192,120"/>'
    # calendar: waiting years
    d += '<rect class="hz" x="195" y="95" width="110" height="95" rx="8"/>'
    d += '<line class="ln" x1="195" y1="122" x2="305" y2="122"/>'
    d += '<line class="lnc" x1="222" y1="86" x2="222" y2="104"/><line class="lnc" x1="278" y1="86" x2="278" y2="104"/>'
    d += t(250, 165, "years", "bd", "middle")
    d += t(250, 220, ["a new site waits", "for power"], "sm", "middle")
    d += '<line class="lnd" x1="308" y1="142" x2="372" y2="142"/>'
    # the hot rack
    d += '<rect class="hz" x="375" y="55" width="120" height="215" rx="8"/>'
    for k in range(8):
        y = 72 + k * 24
        d += f'<rect class="pf pf-bx" x="387" y="{y}" width="96" height="16" rx="3"/><circle class="hk" cx="473" cy="{y + 8}" r="2.5"/>'
    for k in range(3):
        x = 400 + k * 35
        d += f'<path class="ln" d="M{x},48 Q{x - 8},38 {x},28 Q{x + 8},18 {x},8"/>'
    d += t(510, 84, ["one rack draws", "over 100 kW"], "tx")
    # thermometer
    d += '<rect class="hz" x="560" y="120" width="22" height="105" rx="11"/>'
    d += '<rect class="zr" x="565" y="140" width="12" height="95"/>'
    d += '<circle class="zr" cx="571" cy="240" r="17"/><circle class="ln" cx="571" cy="240" r="17"/>'
    # cooling unit with a fan
    d += '<rect class="hz" x="650" y="110" width="170" height="130" rx="10"/>'
    d += '<circle class="hz" cx="735" cy="175" r="46"/>'
    for k in range(3):
        ang = math.radians(k * 120 + 20)
        d += (f'<ellipse class="bx" cx="{735 + 22 * math.cos(ang):.0f}" cy="{175 + 22 * math.sin(ang):.0f}" rx="20" ry="9" '
              f'transform="rotate({k * 120 + 20} {735 + 22 * math.cos(ang):.0f} {175 + 22 * math.sin(ang):.0f})"/>')
    for k, (x, y) in enumerate(((860, 140), (900, 180), (870, 215))):
        d += f'<path class="bx" d="M{x},{y - 18} Q{x + 13},{y} {x},{y + 8} Q{x - 13},{y} {x},{y - 18} Z"/>'
    d += t(790, 278, "cooling and water can't keep up", "sm", "middle")
    return figure(1000, 295, d,
                  "Power from a grid pylon reaches a calendar marked years: a new site waits for power. Next to it a hot rack draws over 100 kW, with heat rising off it, a high thermometer, and a cooling unit with a fan and water drops that cannot keep up.",
                  "AI racks now draw over 100 kW each, grids and cooling cannot keep up, and new data centres wait years for power.")


def d_chip_design():
    t = kit.text
    # the expert and the calendar
    d = '<rect class="hz" x="35" y="30" width="110" height="80" rx="8"/><line class="ln" x1="35" y1="54" x2="145" y2="54"/>'
    d += t(90, 88, "months", "bd", "middle")
    d += _person(90, 140)
    d += t(90, 250, ["months of", "expert work"], "sm", "middle")
    # a pile of parts
    import random
    rnd = random.Random(7)
    for _ in range(26):
        x, y = rnd.randint(190, 320), rnd.randint(200, 270)
        d += f'<rect class="bxs" x="{x}" y="{y}" width="14" height="10" rx="2" transform="rotate({rnd.randint(-30, 30)} {x + 7} {y + 5})"/>'
    d += t(255, 186, "billions of parts", "sm", "middle")
    d += kit.path("M300,200 Q330,170 362,168", "ln")
    # the floor plan
    d += '<rect class="hz" x="370" y="30" width="260" height="260" rx="6"/>'
    cells = [(0, 0, 2, 1), (2, 0, 1, 2), (3, 0, 3, 1), (6, 0, 2, 2), (0, 1, 2, 2), (3, 1, 2, 2), (5, 1, 1, 1),
             (2, 2, 1, 1), (5, 2, 3, 1), (0, 3, 3, 2), (3, 3, 1, 3), (4, 3, 2, 1), (6, 3, 2, 2), (4, 4, 2, 2),
             (0, 5, 2, 3), (2, 5, 1, 1), (6, 5, 2, 1), (2, 6, 2, 2), (4, 6, 2, 2), (6, 6, 2, 2)]
    for k, (cx, cy, w, h) in enumerate(cells):
        cls = ("pf pf-bx", "pf pf-bxs", "pf pf-solid")[k % 3]
        d += f'<rect class="{cls}" x="{378 + cx * 31 + 2}" y="{38 + cy * 31 + 2}" width="{w * 31 - 6}" height="{h * 31 - 6}" rx="3"/>'
    d += '<path class="ln" d="M405,60 L405,130 L500,130 L500,215 L590,215"/>'
    d += '<path class="ln" d="M470,55 L560,55 L560,180 L440,180 L440,260"/>'
    d += '<path class="ln" d="M600,90 L600,150 L520,150"/>'
    d += t(500, 312, "place and wire every part", "sm", "middle")
    # the AI and its disputed claim
    d += '<rect class="bx" x="730" y="130" width="76" height="58" rx="10"/>'
    d += '<circle class="hk" cx="752" cy="155" r="6"/><circle class="hk" cx="784" cy="155" r="6"/>'
    d += '<line class="ln" x1="752" y1="174" x2="784" y2="174"/>'
    d += '<line class="ln" x1="768" y1="130" x2="768" y2="112"/><circle class="bxs" cx="768" cy="106" r="7"/>'
    d += '<rect class="bx" x="722" y="195" width="92" height="72" rx="10"/>'
    d += t(768, 238, "AI", "bd", "middle")
    d += '<path class="hz" d="M820,40 L980,40 Q990,40 990,50 L990,90 Q990,100 980,100 L850,100 L825,122 L835,100 L830,100 Q820,100 820,90 L820,50 Q820,40 830,40 Z"/>'
    d += t(905, 76, "\"we did it better!\"", "tx", "middle")
    d += t(840, 190, "?", "tt", "middle").replace('class="tt"', 'class="tt" style="font-size:44px"')
    d += t(870, 228, ["published results", "are disputed"], "sm")
    return figure(1000, 325, d,
                  "An expert with a calendar marked months. A pile of billions of parts goes into a chip floor plan where every part must be placed and wired. On the right a robot labelled AI says it did it better, next to a question mark: published results are disputed.",
                  "Placing and wiring billions of parts on a chip takes months of expert work, and the published claims that AI does it better are disputed.")


def d_light_analog():
    b, t = kit.box, kit.text
    d = ""
    rows = [(20, "Digital chip", ["exact 0s and 1s"], "bx", False, 4, "3.00", "bx", "a lot of energy"),
            (165, "Light or analog", ["numbers as brightness", "or voltage"], "solid", True, 1, "2.9? 3.1?", "bxs", "far less energy")]
    for y, name, sub, kind, noisy, bolts, result, rk, energy in rows:
        d += b(10, y, 220, 110, name, sub, kind)
        mid = y + 55
        if not noisy:
            pts = f"M260,{mid + 25}"
            for k in range(6):
                x = 260 + k * 60
                hi = k % 2 == 0
                pts += f" L{x},{mid + 25} L{x},{mid - 25} L{x + 30},{mid - 25} L{x + 30},{mid + 25}"
            pts += f" L620,{mid + 25}"
            d += f'<path class="lnc" d="{pts}"/>'
        else:
            pts = []
            for j in range(181):
                x = 260 + j * 2
                v = math.sin(j / 180 * 4 * math.pi) * 25 + 6 * math.sin(j * 0.9) + 4 * math.sin(j * 2.3 + 1)
                pts.append(f"{x},{mid - v:.1f}")
            d += '<path class="lnd" d="M' + " L".join(f"{260 + j * 2},{mid - math.sin(j / 180 * 4 * math.pi) * 25:.1f}" for j in range(181)) + '"/>'
            d += '<path class="lnc" d="M' + " L".join(pts) + '"/>'
        for k in range(bolts):
            d += _bolt(650 + k * 30, mid - 32)
        d += t(650, mid + 36, energy, "sm")
        d += b(800, y + 15, 190, 80, result, "the answer", rk)
    d += t(440, 300, "noise blurs every number", "sm", "middle")
    return figure(1000, 312, d,
                  "Two rows. A digital chip uses exact 0s and 1s, a clean square wave, four lightning bolts of energy, and the exact answer 3.00. A light or analog chip uses brightness or voltage, a noisy wave, one lightning bolt, and a blurred answer: 2.9 or 3.1.",
                  "Computing with light or analog circuits could use far less energy, but noise makes the numbers imprecise.")


def d_quantum():
    t = kit.text
    d = t(130, 34, ["many physical qubits,", "making errors all the time"], "sm", "middle")
    bad = {(0, 1), (1, 4), (2, 2), (3, 0), (3, 5), (4, 3)}
    for r in range(5):
        for c in range(6):
            x, y = 40 + c * 36, 90 + r * 36
            cls = "zr" if (r, c) in bad else "hz"
            d += f'<circle class="{cls}" cx="{x}" cy="{y}" r="12"/>'
            if (r, c) in bad:
                d += f'<circle class="ln" cx="{x}" cy="{y}" r="12"/>'
                d += f'<path class="ln" d="M{x + 9},{y - 18} L{x + 15},{y - 11} L{x + 11},{y - 9} L{x + 17},{y - 2}"/>'
    d += kit.arrow(250, 162, 335, 162, "checked", ly=150)
    d += t(292, 186, "together", "sm", "middle")
    d += '<circle class="pf pf-solid" cx="413" cy="166" r="56"/><circle class="solid ol" cx="410" cy="162" r="56"/>'
    d += t(410, 158, "1 logical", "tx", "middle") + t(410, 180, "qubit", "tx", "middle")
    d += t(410, 248, "error-corrected", "sm", "middle")
    d += '<line class="lnd" x1="500" y1="40" x2="500" y2="270"/>'
    d += t(530, 70, "Today: a handful", "bd")
    for k in range(3):
        d += f'<circle class="solid" cx="{555 + k * 50}" cy="112" r="18"/>'
    d += t(530, 180, "A useful machine: thousands", "bd")
    for k in range(12):
        d += f'<circle class="bxm" cx="{548 + k * 34}" cy="222" r="13"/>'
    d += t(965, 250, "…and more", "sm", "end")
    return figure(1000, 285, d,
                  "On the left a grid of physical qubits, several marked with errors, are checked together to make one logical, error-corrected qubit. On the right: today's machines have a handful of logical qubits; a useful machine needs thousands, drawn as a long dashed row.",
                  "Qubits make errors constantly, so many must work together as one reliable qubit. A useful machine needs thousands of those; today's have a handful.")


DRAWINGS = {
    "shrinking-models-below-4-bits-without-losing": d_low_bits,
    "the-memory-cost-of-long-conversations-the": d_kv_cache,
    "always-on-sensing-on-tiny-chips-tinyml": d_tinyml,
    "learning-on-the-device-while-keeping-data": d_federated,
    "energy-per-answer": d_energy,
    "trusting-a-model-running-on-someone-else": d_trust,
    "the-memory-wall": d_memory_wall,
    "connecting-thousands-of-chips": d_many_chips,
    "power-and-cooling-for-ai-data-centres": d_power_cooling,
    "ai-for-chip-design": d_chip_design,
    "computing-with-light-or-analog-circuits": d_light_analog,
    "quantum-error-correction": d_quantum,
}
