"""Problem diagrams for group 'core' (Inside the model: the core of LLMs).
kit, figure, E and ROOT are injected as globals by _problems/build.py."""
import math


# ---------- small cartoon helpers ----------

def _person(cx, top, wave=False):
    """A stick person; head centre at (cx, top + 13), feet at top + 80."""
    s = (f'<circle class="bx" cx="{cx}" cy="{top + 13}" r="13"/>'
         f'<line class="lnc" x1="{cx}" y1="{top + 26}" x2="{cx}" y2="{top + 58}"/>'
         f'<line class="lnc" x1="{cx}" y1="{top + 58}" x2="{cx - 11}" y2="{top + 80}"/>'
         f'<line class="lnc" x1="{cx}" y1="{top + 58}" x2="{cx + 11}" y2="{top + 80}"/>'
         f'<line class="lnc" x1="{cx}" y1="{top + 36}" x2="{cx - 16}" y2="{top + 50}"/>')
    if wave:
        s += f'<line class="lnc" x1="{cx}" y1="{top + 36}" x2="{cx + 20}" y2="{top + 20}"/>'
    else:
        s += f'<line class="lnc" x1="{cx}" y1="{top + 36}" x2="{cx + 16}" y2="{top + 50}"/>'
    return s


def _robot(cx, top, mouth="smile"):
    """A little robot standing for the model; about 76 wide, 126 tall."""
    s = (f'<line class="ln" x1="{cx}" y1="{top}" x2="{cx}" y2="{top + 12}"/><circle class="bxs" cx="{cx}" cy="{top}" r="5"/>'
         f'<rect class="solid" x="{cx - 32}" y="{top + 12}" width="64" height="48" rx="10"/>'
         f'<circle class="hk" cx="{cx - 13}" cy="{top + 32}" r="4"/><circle class="hk" cx="{cx + 13}" cy="{top + 32}" r="4"/>')
    if mouth == "smile":
        s += f'<path class="ln" d="M{cx - 12},{top + 45} Q{cx},{top + 54} {cx + 12},{top + 45}"/>'
    elif mouth == "flat":
        s += f'<line class="ln" x1="{cx - 11}" y1="{top + 48}" x2="{cx + 11}" y2="{top + 48}"/>'
    else:  # puzzled
        s += f'<path class="ln" d="M{cx - 12},{top + 49} Q{cx - 6},{top + 44} {cx},{top + 49} Q{cx + 6},{top + 54} {cx + 12},{top + 49}"/>'
    s += (f'<rect class="hz" x="{cx - 38}" y="{top + 66}" width="76" height="60" rx="8"/>'
          f'<line class="lnc" x1="{cx - 38}" y1="{top + 78}" x2="{cx - 54}" y2="{top + 104}"/>'
          f'<line class="lnc" x1="{cx + 38}" y1="{top + 78}" x2="{cx + 54}" y2="{top + 104}"/>')
    return s


def _bubble(x, y, w, h, lines, tx, ty, cls="tx", kind="hz"):
    """A speech bubble with a tail pointing at (tx, ty)."""
    lines = [lines] if isinstance(lines, str) else lines
    bx = min(max(tx, x + 22), x + w - 22)
    by = y + h if ty > y + h else y
    s = (f'<path class="{kind}" d="M{bx - 12},{by} L{tx},{ty} L{bx + 12},{by} Z"/>'
         f'<rect class="{kind}" x="{x}" y="{y}" width="{w}" height="{h}" rx="16"/>'
         f'<line x1="{bx - 10}" y1="{by}" x2="{bx + 10}" y2="{by}" style="stroke:{"#fff" if kind == "hz" else "#FFF3C9"};stroke-width:3"/>')
    gap = 22
    y0 = y + h / 2 - (len(lines) - 1) * gap / 2 + 6
    s += kit.text(x + w / 2, y0, lines, cls, "middle")
    return s


def _cross(cx, cy, r=12):
    return (f'<line class="lnc" x1="{cx - r}" y1="{cy - r}" x2="{cx + r}" y2="{cy + r}"/>'
            f'<line class="lnc" x1="{cx + r}" y1="{cy - r}" x2="{cx - r}" y2="{cy + r}"/>')


def _tick(cx, cy):
    return f'<path class="lnc" d="M{cx - 10},{cy} L{cx - 3},{cy + 8} L{cx + 12},{cy - 10}"/>'


# ---------- 1. hallucination ----------

def d_hallucination():
    t = kit.text
    d = _person(80, 150)
    d += _bubble(20, 30, 250, 76, ["In which year did", "this tax rule change?"], 80, 148)
    d += kit.arrow(280, 110, 360, 110)
    d += _robot(430, 120)
    d += _bubble(490, 24, 230, 70, "\"In 2014. Definitely.\"", 450, 128, "bd", "bxs")
    d += _cross(745, 59) + t(770, 52, ["confidently", "wrong"], "sm")
    # the missing dashboard light
    d += '<rect class="hz" x="560" y="150" width="400" height="120" rx="14"/>'
    d += t(760, 176, "THE MODEL'S DASHBOARD", "lbl", "middle")
    d += '<circle class="bxs" cx="640" cy="218" r="20"/>'
    for k in range(8):
        a = k * math.pi / 4
        d += f'<line class="ln" x1="{640 + 26 * math.cos(a):.0f}" y1="{218 + 26 * math.sin(a):.0f}" x2="{640 + 34 * math.cos(a):.0f}" y2="{218 + 34 * math.sin(a):.0f}"/>'
    d += t(640, 262, "sounds sure", "sm", "middle")
    d += '<circle class="bxm" cx="850" cy="218" r="20"/>' + t(850, 224, "?", "bd", "middle")
    d += t(850, 262, "\"I'm guessing\": no such light", "sm", "middle")
    return figure(1000, 290, d,
                  "A person asks in which year a tax rule changed. A smiling robot answers 'In 2014. Definitely.', which is wrong. On the model's dashboard the 'sounds sure' light is lit, and the 'I'm guessing' light does not exist.",
                  "Training rewards a confident answer, and the model has no reliable inner light that says \"I am guessing\".")


# ---------- 2. multi-step reasoning ----------

def d_reasoning():
    t = kit.text
    d = ""
    # river
    d += '<rect class="zg" x="0" y="0" width="0" height="0"/>'
    d += '<path class="bx" style="stroke:none" d="M90,190 L910,190 L910,262 L90,262 Z"/>'
    for y in (204, 226, 248):
        d += f'<path class="ln" style="stroke:#7aa6cf" d="M110,{y} q20,-7 40,0 t40,0 t40,0"/><path class="ln" style="stroke:#7aa6cf" d="M560,{y} q20,-7 40,0 t40,0 t40,0"/>'
    d += _person(45, 140)
    d += t(45, 245, "start", "sm", "middle")
    # flag on the far bank
    d += '<line class="lnc" x1="955" y1="140" x2="955" y2="222"/><path class="bxs" d="M955,142 L992,154 L955,168 Z"/>'
    d += t(955, 245, "answer", "sm", "middle")
    for k in range(10):
        x = 130 + k * 78
        p = 0.95 ** (k + 1)
        d += f'<ellipse class="hz" cx="{x}" cy="226" rx="26" ry="11"/>'
        h = p * 110
        d += f'<rect class="pf pf-bxs" x="{x - 14}" y="{170 - h:.0f}" width="28" height="{h:.0f}" rx="3"/>'
        d += f'<rect class="ln" style="fill:none" x="{x - 14}" y="{170 - h:.0f}" width="28" height="{h:.0f}" rx="3"/>'
        d += t(x, 290, f"step {k + 1}", "sm", "middle")
    d += t(130, 46, "95%", "bd", "middle") + t(832, 94, "about 60%", "bd", "middle")
    d += t(480, 30, "each bar: the chance every step so far was right", "sm", "middle")
    return figure(1000, 305, d,
                  "Ten stepping stones cross a river from a person to the answer. Above each stone a bar shows the chance that every step so far was right: 95% after one step, shrinking to about 60% after ten.",
                  "Small errors compound: 95% right per step is about 60% right over 10 steps. And the written reasoning may not match how the model really got there.")


# ---------- 3. thinking cost ----------

def d_thinking():
    t = kit.text
    d = kit.box(10, 60, 170, 80, "\"What is 2 + 2?\"", "an easy question", "bxm")
    d += kit.arrow(182, 100, 222, 100)
    d += _robot(275, 40)
    # long scroll of hidden thinking
    d += '<rect class="hz" x="350" y="40" width="430" height="150" rx="6"/>'
    d += '<ellipse class="hz" cx="350" cy="115" rx="12" ry="75"/><ellipse class="hz" cx="780" cy="115" rx="12" ry="75"/>'
    for j in range(7):
        w = 350 - (j * 37) % 90
        d += f'<line class="ln" x1="378" y1="{60 + j * 18}" x2="{378 + w}" y2="{60 + j * 18}"/>'
    d += t(565, 212, "thousands of hidden thinking tokens, all paid for", "sm", "middle")
    d += kit.arrow(794, 100, 834, 100)
    d += kit.box(837, 60, 150, 80, "\"4\"", "needed about ten", "bxs")
    # the missing dial
    cx, cy = 150, 270
    d += f'<path class="hz" d="M{cx - 50},{cy} A50,50 0 0 1 {cx + 50},{cy} Z"/>'
    d += t(cx - 44, cy + 20, "a little", "sm", "middle") + t(cx + 44, cy + 20, "a lot", "sm", "middle")
    d += t(cx, cy - 14, "?", "bd", "middle")
    d += t(225, 252, "how much should it think?", "tx")
    d += t(225, 276, "nobody has a reliable dial for that", "sm")
    return figure(1000, 300, d,
                  "The easy question 'What is 2 + 2?' goes into the model, which unrolls a long scroll of thousands of hidden thinking tokens before answering '4', an answer that needed about ten. Below, a dial from 'a little' to 'a lot' has only a question mark: nobody has a reliable dial for how much to think.",
                  "Reasoning models spend thousands of hidden tokens on questions that need ten, and nobody can reliably tell in advance how much thinking a question needs.")


# ---------- 4. continual learning ----------

def d_continual():
    t = kit.text
    d = t(500, 28, "THE MODEL'S WEIGHTS: ONE FULL SHELF", "lbl", "middle")
    # shelf
    d += '<rect class="hz" x="300" y="44" width="400" height="190" rx="6"/>'
    d += '<line class="lnc" x1="300" y1="140" x2="700" y2="140"/><line class="lnc" x1="300" y1="234" x2="700" y2="234"/>'
    cols = ["bx", "hz", "bx", "bx", "hz", "bx", "hz", "bx", "bx", "hz", "bx", "hz", "bx"]
    for row, y0 in enumerate((52, 146)):
        for i in range(13):
            h = 80 if (i + row) % 3 else 72
            d += f'<rect class="{cols[(i + row * 5) % 13]}" x="{312 + i * 29}" y="{y0 + 88 - h - 6}" width="24" height="{h}" rx="3"/>'
    # new book being pushed in
    d += '<rect class="bxs" x="190" y="104" width="34" height="84" rx="3" transform="rotate(-8 207 146)"/>'
    d += kit.arrow(232, 146, 292, 146)
    d += t(120, 76, ["new facts,", "this week"], "tx", "middle")
    d += t(120, 210, ["update the", "weights"], "sm", "middle")
    # books falling out of the right side
    d += '<rect class="bx" x="728" y="120" width="24" height="76" rx="3" transform="rotate(28 740 158)"/>'
    d += '<rect class="hz" x="790" y="200" width="24" height="76" rx="3" transform="rotate(70 802 238)"/>'
    d += kit.path("M712,90 Q760,80 770,118", "lnd") + kit.path("M760,190 Q790,175 800,200", "lnd")
    d += t(870, 120, ["old skills", "fall off"], "bd", "middle")
    d += t(870, 175, "(\"catastrophic", "sm", "middle") + t(870, 195, "forgetting\")", "sm", "middle")
    d += '<line class="ln" x1="720" y1="290" x2="990" y2="290"/>'
    d += kit.box(300, 252, 400, 56, "Today's fix", "retrain from scratch, or bolt on retrieval", "bxm")
    return figure(1000, 320, d,
                  "A full bookshelf stands for the model's weights. A yellow book of new facts is pushed in from the left; on the right, old books, the model's old skills, fall off the shelf. Below, today's fix: retrain from scratch, or bolt on retrieval.",
                  "Updating the weights on new facts damages old skills, so today a model learns nothing after it ships without a full retrain.")


# ---------- 5. long context ----------

def d_long_context():
    t = kit.text
    d = t(500, 24, "A MILLION TOKENS FIT IN", "lbl", "middle")
    # attention curve
    d += t(40, 58, "how well it notices", "sm")
    d += '<path class="lnc" d="M60,74 Q120,170 300,176 L700,176 Q880,170 940,74"/>'
    # long document strip
    for i in range(23):
        x = 40 + i * 40
        d += f'<rect class="hz" x="{x}" y="196" width="36" height="46" rx="3"/>'
        d += f'<line class="ln" x1="{x + 7}" y1="{208}" x2="{x + 29}" y2="{208}"/><line class="ln" x1="{x + 7}" y1="{220}" x2="{x + 25}" y2="{220}"/>'
    facts = [(318, "A"), (498, "B"), (678, "C")]
    for x, lab in facts:
        d += f'<rect class="bxs" x="{x - 18}" y="196" width="36" height="46" rx="3"/>' + t(x, 226, lab, "bd", "middle")
    d += t(80, 270, "start: noticed", "sm", "middle") + t(920, 270, "end: noticed", "sm", "middle")
    d += t(170, 132, "the middle sags", "sm", "middle")
    # combining
    d += '<path class="lnd" d="M318,246 Q408,300 498,246"/><path class="lnd" d="M498,246 Q588,300 678,246"/>'
    d += t(498, 312, "the answer needs A + B + C together: missed", "tx", "middle")
    return figure(1000, 330, d,
                  "A long strip of pages stands for a million-token context. Above it, a curve of how well the model notices facts is high at the start and end and sags in the middle. Three facts, A, B and C, sit in the middle, and the answer needs all three together, which the model misses.",
                  "A long document fits in the window, but facts in the middle get missed, and facts spread far apart are not combined.")


# ---------- 6. personal memory ----------

def d_memory():
    t = kit.text
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    d = '<line class="ln" x1="40" y1="50" x2="960" y2="50"/>'
    for i, m in enumerate(months):
        x = 80 + i * 168
        d += f'<line class="ln" x1="{x}" y1="44" x2="{x}" y2="56"/>' + t(x, 32, m, "sm", "middle")
    events = [(80, "\"I live in Pune\""), (248, "\"I'm vegetarian\""), (584, "\"I moved to Delhi\"")]
    for x, s in events:
        d += f'<line class="lnd" x1="{x}" y1="56" x2="{x}" y2="76"/>'
        d += kit.box(x - 78, 76, 156, 40, s, "", "bx")
    # memory drawer
    d += '<rect class="hz" x="40" y="160" width="440" height="140" rx="10"/>'
    d += t(260, 186, "THE ASSISTANT'S MEMORY", "lbl", "middle")
    d += kit.box(58, 200, 130, 40, "lives in Pune", "", "bxs")
    d += kit.box(198, 200, 140, 40, "lives in Delhi", "", "bxs")
    d += t(268, 266, "both kept: which one is true now?", "sm", "middle")
    d += kit.box(350, 200, 112, 40, "health note", "", "bxm")
    d += t(406, 290, "may leak", "sm", "middle")
    d += kit.path("M190,121 Q160,140 126,196", "lnd") + kit.path("M584,121 Q500,160 300,196", "lnd")
    # June question
    d += _person(905, 170)
    d += _bubble(700, 140, 170, 60, "\"A gym near home?\"", 890, 178)
    d += _robot(560, 162, "smile")
    d += _bubble(620, 222, 230, 56, "\"Here are gyms in Pune!\"", 600, 250, "tx", "bxs")
    d += _cross(870, 250, 10)
    return figure(1000, 315, d,
                  "A six-month timeline: in January the user says 'I live in Pune', in February 'I'm vegetarian', in April 'I moved to Delhi'. The assistant's memory keeps both 'lives in Pune' and 'lives in Delhi', plus a health note that may leak. In June the user asks for a gym near home and the assistant suggests gyms in Pune.",
                  "Memories go stale, contradict each other and can leak private details, and nobody has settled what an assistant should remember, update or forget.")


# ---------- 7. long video ----------

def d_video():
    t = kit.text
    d = ""
    # film strip
    d += '<rect class="hk" x="20" y="30" width="960" height="96" rx="4"/>'
    for i in range(48):
        d += f'<rect x="{26 + i * 20}" y="36" width="10" height="8" rx="2" style="fill:#fff"/><rect x="{26 + i * 20}" y="112" width="10" height="8" rx="2" style="fill:#fff"/>'
    icons = {1: "door opens", 5: "phone call", 9: "car leaves"}
    for i in range(12):
        x = 30 + i * 79
        d += f'<rect class="hz" x="{x}" y="50" width="70" height="56" rx="3"/>'
        if i in icons:
            d += t(x + 35, 74, icons[i].split()[0], "sm", "middle") + t(x + 35, 94, icons[i].split()[1], "sm", "middle")
    d += t(30, 150, "0 min", "sm") + t(970, 150, "60 min", "sm", "end")
    # short clip: fine
    d += '<path class="ln" d="M30,160 L30,170 L178,170 L178,160"/>'
    d += kit.box(20, 190, 220, 70, "One short clip", "\"a man opens a door\"", "bx") + _tick(222, 206)
    # whole hour question
    d += _robot(390, 160, "puzzled")
    d += t(445, 168, "?", "bd")
    d += _bubble(480, 170, 320, 60, ["\"Which came first:", "the call or the car leaving?\""], 440, 210)
    d += t(640, 268, "across the hour, the order of events gets lost", "tx", "middle")
    d += kit.box(820, 170, 160, 60, "car, door, call?", "", "bxs") + _cross(960, 176, 9)
    return figure(1000, 285, d,
                  "A film strip runs from 0 to 60 minutes, with a door opening early, a phone call in the middle and a car leaving near the end. On one short clip the model correctly says 'a man opens a door'. Asked which came first across the hour, the puzzled model jumbles the order: car, door, call.",
                  "Models describe a short clip well, but lose track of who did what, and in which order, across an hour of video.")


# ---------- 8. synthetic data collapse ----------

def _bell(cx, base, width, height):
    pts = []
    for k in range(41):
        x = -2.6 + k * 5.2 / 40
        pts.append(f"{cx + x / 2.6 * width:.1f},{base - height * math.exp(-x * x / 2):.1f}")
    return f'<path class="pf pf-bx" d="M{pts[0]} L' + " L".join(pts[1:]) + ' Z"/><path class="ln" d="M' + " L".join(pts) + '"/>'


def d_synthetic():
    t = kit.text
    # the jar of human text, nearly empty
    d = '<path class="hz" d="M40,80 L40,240 Q40,256 56,256 L144,256 Q160,256 160,240 L160,80"/>'
    d += '<rect class="hz" x="32" y="66" width="136" height="16" rx="4"/>'
    d += '<path class="bxs" d="M42,226 L158,226 L158,240 Q158,254 144,254 L56,254 Q42,254 42,240 Z"/>'
    d += t(100, 40, "good public text", "tx", "middle") + t(100, 286, "nearly used up", "sm", "middle")
    d += kit.arrow(170, 180, 206, 180)
    gens = [("human text", 92, 60), ("generation 1", 66, 80), ("generation 2", 42, 100), ("generation 3", 22, 118)]
    for i, (lab, w, h) in enumerate(gens):
        cx = 300 + i * 200
        d += f'<rect class="hz" x="{cx - 90}" y="90" width="180" height="150" rx="10"/>'
        d += _bell(cx, 220, w, h)
        d += f'<line class="ln" x1="{cx - 80}" y1="220" x2="{cx + 80}" y2="220"/>'
        d += t(cx, 266, lab, "tx", "middle")
        if i < 3:
            d += kit.arrow(cx + 92, 165, cx + 108, 165)
    d += kit.path("M400,84 Q600,20 800,84", "lnd")
    d += kit.path("M600,84 Q700,40 800,84", "lnd", end=False)
    d += t(600, 36, "each model trains on the last one's writing", "sm", "middle")
    d += t(800, 290, "fewer kinds of answer: rare things vanish", "sm", "middle")
    return figure(1000, 305, d,
                  "A jar of good public text is nearly empty. Next to it, four frames show the spread of what a model writes: wide for human text, then narrower for generation 1, 2 and 3, as each model trains on the last one's writing, until rare things vanish.",
                  "Good public text is nearly used up, and training on model-written text can narrow the model each generation (\"model collapse\").")


# ---------- 9. evaluation is broken ----------

def d_evaluation():
    t = kit.text
    d = t(250, 24, "1. THE TEST LEAKS INTO TRAINING", "lbl", "middle")
    # exam sheet
    d += '<rect class="hz" x="20" y="60" width="120" height="150" rx="4"/>'
    d += t(80, 86, "TEST", "bd", "middle")
    for j in range(4):
        d += f'<line class="ln" x1="34" y1="{106 + j * 22}" x2="102" y2="{106 + j * 22}"/>' + _tick(120, 104 + j * 22)
    d += t(80, 236, "questions + answers", "sm", "middle")
    d += kit.arrow(146, 135, 196, 135, "posted online", lx=171, ly=120)
    # training pile
    for j in range(6):
        d += f'<rect class="{"bxs" if j == 2 else "hz"}" x="{205 + (j % 2) * 8}" y="{186 - j * 22}" width="120" height="20" rx="3"/>'
    d += t(270, 236, "training data", "sm", "middle")
    d += kit.arrow(338, 135, 368, 135)
    d += _robot(420, 70)
    d += _bubble(355, 214, 140, 40, "\"98%! (seen it)\"", 420, 198, "sm", "bxs")
    d += '<line class="lnd" x1="515" y1="30" x2="515" y2="270"/>'
    # saturated scoreboard
    d += t(760, 24, "2. EVERY MODEL HITS THE TOP WITHIN MONTHS", "lbl", "middle")
    d += '<line class="ln" x1="560" y1="80" x2="960" y2="80"/>' + t(965, 85, "max", "sm")
    d += '<line class="ln" x1="560" y1="200" x2="960" y2="200"/>'
    for i, h in enumerate((114, 116, 112, 117)):
        x = 585 + i * 95
        d += f'<rect class="{["bx", "solid", "bxs", "bx"][i]}" x="{x}" y="{200 - h}" width="60" height="{h}" rx="4"/>'
        d += t(x + 30, 222, f"model {'ABCD'[i]}", "sm", "middle")
    d += t(760, 256, "so which one is best for my task?", "tx", "middle")
    d += t(915, 256, "?", "bd")
    return figure(1000, 280, d,
                  "Left: a test sheet with its answers is posted online, lands in a pile of training data, and the model scores 98% because it has seen the answers. Right: a scoreboard where four models all sit at the maximum, leaving the question: which one is best for my task?",
                  "Benchmarks leak into training data and saturate within months, so scores stop telling you which model is better for your task.")


# ---------- 10. world models ----------

def _domino(x, base, angle=0, cls="hz"):
    return f'<rect class="{cls}" x="{x}" y="{base - 70}" width="16" height="70" rx="2" transform="rotate({angle} {x + 16} {base})"/>'


def d_world():
    t = kit.text
    d = t(240, 26, "SEEN IN TRAINING, A THOUSAND TIMES", "lbl", "middle")
    d += '<line class="ln" x1="20" y1="170" x2="460" y2="170"/>'
    d += t(46, 94, "push", "sm", "middle") + kit.arrow(40, 110, 78, 130)
    for i in range(6):
        d += _domino(90 + i * 60, 170, 62)
    d += t(240, 204, "push the first one: all fall", "tx", "middle")
    d += '<line class="lnd" x1="500" y1="30" x2="500" y2="290"/>'
    d += t(760, 26, "NEVER SEEN: TAKE ONE OUT FIRST", "lbl", "middle")
    d += '<line class="ln" x1="540" y1="170" x2="980" y2="170"/>'
    xs = [580, 640, None, 760, 820, 880]
    for i, x in enumerate(xs):
        if x is None:
            d += '<rect class="bxm" x="700" y="100" width="16" height="70" rx="2"/>'
            d += _cross(708, 135, 12)
        else:
            d += _domino(x, 170, 62 if i < 2 else 0)
    d += t(780, 204, "really: two fall, four stay up", "tx", "middle")
    d += _robot(570, 196, "smile")
    d += _bubble(640, 236, 200, 48, "\"All six fall!\"", 610, 250, "bd", "bxs")
    d += _cross(870, 260, 11)
    return figure(1000, 330, d,
                  "Left: a row of dominoes, pushed, all fall, a pattern seen in training a thousand times. Right: the same row with the third domino taken out, which was never seen. In reality two fall and four stay up, but the model predicts 'All six fall!'.",
                  "Models learn patterns, not how the world works, so they fail on \"what would happen if\" questions they never saw in training.")


# ---------- 11. new architectures ----------

def _grid(x, y, n, cell, hi=None):
    s = ""
    for r in range(n):
        for c in range(n):
            s += f'<rect class="{"bxs" if c <= r else "hz"}" x="{x + c * cell}" y="{y + r * cell}" width="{cell}" height="{cell}" style="stroke-width:1"/>'
    return s


def d_architectures():
    t = kit.text
    d = t(300, 24, "TRANSFORMER: EVERY WORD LOOKS AT EVERY OTHER", "lbl", "middle")
    d += _grid(30, 170, 4, 18) + t(66, 268, "4 words", "sm", "middle") + t(66, 288, "16 checks", "sm", "middle")
    d += kit.arrow(110, 200, 150, 200)
    d += _grid(160, 134, 8, 14) + t(216, 268, "8 words", "sm", "middle") + t(216, 288, "64 checks", "sm", "middle")
    d += kit.arrow(282, 190, 322, 190)
    d += _grid(330, 54, 16, 12) + t(426, 268, "16 words", "sm", "middle") + t(426, 288, "256 checks", "sm", "middle")
    d += t(180, 80, ["double the length,", "four times the work"], "tx", "middle")
    d += '<line class="lnd" x1="560" y1="30" x2="560" y2="290"/>'
    d += t(780, 24, "ALTERNATIVES (MAMBA, HYBRIDS)", "lbl", "middle")
    # conveyor of words passing a fixed notepad
    d += '<line class="ln" x1="590" y1="190" x2="970" y2="190"/>'
    for i in range(7):
        x = 598 + i * 54
        if 3 <= i <= 3:
            continue
        d += f'<rect class="bx" x="{x}" y="166" width="40" height="22" rx="4"/>'
    d += '<rect class="solid" x="745" y="70" width="80" height="80" rx="6"/>'
    for j in range(4):
        d += f'<line class="ln" x1="757" y1="{88 + j * 15}" x2="813" y2="{88 + j * 15}"/>'
    d += kit.arrow(785, 164, 785, 154)
    d += t(860, 96, ["one fixed-size", "running note"], "sm")
    d += t(780, 230, "cost grows in a straight line: cheaper", "tx", "middle")
    d += t(780, 258, "but not yet clearly as good", "tx", "middle")
    d += t(780, 284, "?", "bd", "middle")
    return figure(1000, 300, d,
                  "Left: grids of checks for a transformer: 4 words need 16 checks, 8 words 64, 16 words 256, so doubling the length quadruples the work. Right: an alternative model reads words past one fixed-size running note, so cost grows in a straight line; it is cheaper but not yet clearly as good.",
                  "Transformer cost grows with the square of the context length. Cheaper designs exist, but nobody has shown they are as good.")


# ---------- 12. learning from far less data ----------

def d_less_data():
    t = kit.text
    d = '<line class="ln" x1="20" y1="290" x2="980" y2="290"/>'
    # child with a small stack
    d += _person(90, 210)
    for j in range(4):
        d += f'<rect class="{"bx" if j % 2 else "bxs"}" x="{130 + (j % 2) * 4}" y="{272 - j * 18}" width="80" height="16" rx="3"/>'
    d += t(150, 170, ["a child:", "about 100 million words"], "tx", "middle")
    # model with a tower that runs off the top
    d += _robot(560, 164)
    for j in range(15):
        d += f'<rect class="{"bx" if j % 2 else "hz"}" x="{640 + (j % 3) * 4}" y="{272 - j * 17}" width="120" height="15" rx="3"/>'
    d += '<path class="lnd" d="M640,12 L640,26 M764,12 L764,26"/>'
    d += t(702, 8, "", "sm")
    d += t(800, 60, ["a model:", "over 10 trillion words"], "tx")
    d += t(800, 112, "(this tower would go", "sm") + t(800, 132, "far off the page)", "sm")
    d += kit.path("M240,240 Q400,150 520,200", "lnd")
    d += t(370, 140, "same language, about", "sm", "middle") + t(370, 160, "100,000 times the reading", "sm", "middle")
    d += kit.box(250, 222, 260, 52, "How does a child do it?", "", "bxm")
    return figure(1000, 300, d,
                  "A child stands by a small stack of books, about 100 million words. A robot stands by a tower of books, over 10 trillion words, that would go far off the page: about 100,000 times the reading for the same language. Nobody knows how a child does it.",
                  "A child learns language from about 100 million words; models need over 10 trillion, and nobody knows how to close most of that gap.")


DRAWINGS = {
    "hallucination-the-model-doesn-t-know-what": d_hallucination,
    "reliable-multi-step-reasoning": d_reasoning,
    "thinking-cost-models-overthink-easy-questions": d_thinking,
    "continual-learning-learn-after-deployment-without-forgetting": d_continual,
    "using-long-context-not-just-fitting-it": d_long_context,
    "personal-memory-across-months-of-conversations": d_memory,
    "understanding-long-video": d_video,
    "running-out-of-human-text-synthetic-data": d_synthetic,
    "evaluation-itself-is-broken": d_evaluation,
    "world-models-and-cause-and-effect": d_world,
    "new-architectures-beyond-the-transformer": d_architectures,
    "learning-from-far-less-data": d_less_data,
}
