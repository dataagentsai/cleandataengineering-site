"""Problem diagrams, India group (part b). kit, figure, E and ROOT are injected."""


def _person(cx, top, arms="down"):
    """A small stick person; head centre at (cx, top + 12). About 74 px tall."""
    s = (f'<circle class="hz" cx="{cx}" cy="{top + 12}" r="12"/>'
         f'<line class="lnc" x1="{cx}" y1="{top + 24}" x2="{cx}" y2="{top + 52}"/>'
         f'<line class="lnc" x1="{cx}" y1="{top + 52}" x2="{cx - 10}" y2="{top + 74}"/>'
         f'<line class="lnc" x1="{cx}" y1="{top + 52}" x2="{cx + 10}" y2="{top + 74}"/>')
    if arms == "up":
        s += (f'<line class="lnc" x1="{cx}" y1="{top + 32}" x2="{cx - 16}" y2="{top + 16}"/>'
              f'<line class="lnc" x1="{cx}" y1="{top + 32}" x2="{cx + 16}" y2="{top + 16}"/>')
    elif arms == "talk":
        s += (f'<line class="lnc" x1="{cx}" y1="{top + 32}" x2="{cx - 14}" y2="{top + 46}"/>'
              f'<line class="lnc" x1="{cx}" y1="{top + 32}" x2="{cx + 18}" y2="{top + 26}"/>')
    else:
        s += (f'<line class="lnc" x1="{cx}" y1="{top + 32}" x2="{cx - 14}" y2="{top + 46}"/>'
              f'<line class="lnc" x1="{cx}" y1="{top + 32}" x2="{cx + 14}" y2="{top + 46}"/>')
    return s


def _bubble(x, y, w, h, tail_x, tail_y):
    """A speech bubble with a little tail pointing to (tail_x, tail_y)."""
    mx = x + w / 2
    return (f'<rect class="hz" x="{x}" y="{y}" width="{w}" height="{h}" rx="14"/>'
            f'<path class="hz" d="M{mx - 10},{y + h - 1} L{tail_x},{tail_y} L{mx + 10},{y + h - 1}"/>')


# ------------------------------------------------------------------ groundwater

def d_groundwater():
    t, a = kit.text, kit.arrow
    d = ""
    # sky and ground line
    d += '<line class="ln" x1="20" y1="110" x2="980" y2="110"/>'
    # a few small rain drops on the left: a little goes in
    for i, (x, y) in enumerate([(70, 30), (100, 52), (130, 28), (160, 50)]):
        d += f'<path class="pf pf-bx" d="M{x},{y} Q{x - 6},{y + 12} {x},{y + 16} Q{x + 6},{y + 12} {x},{y} Z"/>'
        d += f'<path class="ln" d="M{x},{y} Q{x - 6},{y + 12} {x},{y + 16} Q{x + 6},{y + 12} {x},{y} Z"/>'
    d += t(115, 92, "rain", "sm", "middle")
    d += a(115, 120, 115, 168)
    d += t(130, 150, "a little in", "bd")
    # the aquifer: water body, old level dashed, new lower level
    d += '<rect class="pf pf-bx" x="20" y="232" width="960" height="78"/>'
    d += '<line class="lnd" x1="20" y1="180" x2="980" y2="180"/>'
    d += t(975, 172, "water table, years ago", "sm", "end")
    d += '<line class="ln" x1="20" y1="232" x2="980" y2="232"/>'
    d += t(975, 252, "water table now", "sm", "end")
    d += a(330, 186, 330, 226)
    d += t(345, 212, "keeps dropping", "sm")
    # tube well + pump on the right of centre, pipe deep into the water
    px = 560
    d += f'<rect class="hz" x="{px - 6}" y="70" width="12" height="225"/>'
    d += f'<rect class="hz" x="{px - 34}" y="62" width="68" height="48" rx="6"/>'
    d += t(px, 92, "pump", "sm", "middle")
    d += f'<path class="hz" d="M{px + 34},78 L{px + 80},78 L{px + 80},92 L{px + 34},92"/>'
    # water gushing out to a field
    d += f'<path class="lnc" d="M{px + 82},86 Q{px + 112},90 {px + 120},104"/>'
    d += t(px + 130, 54, "a lot out", "bd")
    d += t(px + 130, 74, "fields, towns", "sm")
    d += a(px, 250, px, 210)
    # crops
    for i in range(4):
        x = 720 + i * 26
        d += f'<path class="ln" d="M{x},110 L{x},88 M{x},98 Q{x - 10},90 {x - 12},84 M{x},94 Q{x + 10},86 {x + 12},80"/>'
    # measuring: a clipboard with only a few ticks
    d += '<rect class="hz" x="830" y="16" width="140" height="80" rx="8"/>'
    d += t(900, 40, "well readings", "sm", "middle")
    d += "".join(f'<line class="ln" x1="{846 + j * 9}" y1="56" x2="{846 + j * 9}" y2="80"/>' for j in range(12))
    d += "".join(f'<circle class="hk" cx="{846 + j * 9}" cy="68" r="4"/>' for j in (1, 6, 10))
    return figure(1000, 320, d,
                  "A cross-section of the ground. A little rain soaks in on the left. A pump on a tube well pulls a lot of water up from deep below for fields and towns. The water table has dropped from a dashed line years ago to a lower line now. A clipboard shows well readings taken only a few times a year.",
                  "More water is pumped out than rain puts back, so the water table keeps falling, and wells are measured only a few times a year.")


# ------------------------------------------------------------------ delhi air

def d_delhi_air():
    t, a = kit.text, kit.arrow
    d = ""
    # the city skyline with India Gate in the middle
    d += '<line class="ln" x1="330" y1="290" x2="670" y2="290"/>'
    for x, w, h in [(340, 50, 70), (395, 40, 100), (560, 45, 90), (610, 50, 60)]:
        d += f'<rect class="hz" x="{x}" y="{290 - h}" width="{w}" height="{h}" rx="3"/>'
    d += '<path class="hz" d="M465,290 L465,200 L535,200 L535,290 L518,290 L518,236 Q500,214 482,236 L482,290 Z"/>'
    d += '<rect class="hz" x="458" y="188" width="84" height="14" rx="2"/>'
    # the smog cloud over it
    d += '<path class="hatch" d="M330,170 Q320,120 370,118 Q390,78 450,92 Q490,60 545,88 Q610,74 630,118 Q680,124 668,170 Z"/>'
    d += t(500, 140, "smog", "bd", "middle")
    # five sources around, each a box with an arrow into the cloud
    srcs = [(20, 30, "Crop fires", "stubble burning", (330, 135)),
            (20, 140, "Traffic", "cars, trucks, autos", (325, 160)),
            (20, 240, "Dust", "roads, building sites", (360, 172)),
            (780, 30, "Industry", "factories, power", (668, 130)),
            (780, 140, "Weather", "wind, still air", (672, 160))]
    for x, y, title, sub, (tx, ty) in srcs:
        d += kit.box(x, y, 200, 70, title, sub, "bx")
        ex = x + 202 if x < 500 else x - 2
        d += a(ex, y + 35, tx, ty)
    # the open question
    d += kit.box(760, 232, 230, 76, "How much from each?", "a different mix every day", "bxs")
    return figure(1000, 320, d,
                  "Delhi's skyline with India Gate under a hatched smog cloud. Arrows feed into the cloud from five boxes: crop fires, traffic, dust, industry and weather. A yellow note asks how much comes from each, since the mix is different every day.",
                  "Five sources feed the same smog, the mix changes every day, and nobody can say for sure how much comes from each.")


# ------------------------------------------------------------------ solar grid

def d_solar_grid():
    t, a = kit.text, kit.arrow
    d = ""
    # sun with a cloud partly over it
    d += '<circle class="pf pf-bxs" cx="90" cy="70" r="34"/><circle class="ln" cx="90" cy="70" r="34"/>'
    for i in range(8):
        import math
        ang = math.radians(i * 45)
        d += (f'<line class="ln" x1="{90 + 42 * math.cos(ang):.0f}" y1="{70 + 42 * math.sin(ang):.0f}" '
              f'x2="{90 + 56 * math.cos(ang):.0f}" y2="{70 + 56 * math.sin(ang):.0f}"/>')
    d += '<path class="hz" d="M100,118 Q96,92 124,94 Q136,70 164,84 Q192,80 192,106 Q210,112 200,128 L104,128 Q92,126 100,118 Z"/>'
    # solar panels
    for i in range(3):
        x = 40 + i * 62
        d += f'<path class="hz" d="M{x},250 L{x + 54},250 L{x + 44},200 L{x + 10},200 Z"/>'
        d += f'<line class="ln" x1="{x + 27}" y1="200" x2="{x + 27}" y2="250"/><line class="ln" x1="{x + 5}" y1="225" x2="{x + 49}" y2="225"/>'
        d += f'<line class="ln" x1="{x + 27}" y1="250" x2="{x + 27}" y2="268"/>'
    d += t(130, 295, "solar farm", "sm", "middle")
    d += a(232, 225, 290, 200)
    # the day's chart: forecast vs what actually came
    d += '<line class="ln" x1="300" y1="290" x2="740" y2="290"/><line class="ln" x1="300" y1="290" x2="300" y2="40"/>'
    d += t(520, 312, "one day: morning to evening", "sm", "middle")
    d += t(310, 40, "power", "sm")
    d += '<path class="lnd" d="M320,285 Q520,20 720,285"/>'
    d += t(612, 92, "forecast", "sm")
    d += ('<path class="lnc" d="M320,285 Q380,180 420,150 L440,215 L465,120 L490,230 L515,140 L540,240 '
          'L565,130 L590,205 Q650,200 720,285"/>')
    d += t(470, 270, "what came:", "sm", "middle")
    d += t(470, 288, "clouds pass", "sm", "middle")
    # the distributor pays for the gap
    d += _person(830, 40, "up")
    d += t(830, 140, "the distributor", "bd", "middle")
    d += kit.box(760, 170, 230, 110, "Fills every gap", ["buys or sells power", "at short notice,", "and loses money"], "bxs")
    return figure(1000, 320, d,
                  "A sun with a cloud passing over a small solar farm. A chart of one day shows a smooth dashed forecast curve and a jagged real output line that dips each time a cloud passes. On the right the electricity distributor, arms up, has to fill every gap at short notice and loses money.",
                  "Solar output swings with every passing cloud, and the electricity distributor pays to fill each gap between the forecast and what actually came.")


# ------------------------------------------------------------------ rural doctors

def d_rural_doctor():
    t, a = kit.text, kit.arrow
    d = ""
    # the primary health centre
    d += '<path class="hz" d="M20,110 L150,50 L280,110 Z"/>'
    d += '<rect class="hz" x="35" y="110" width="230" height="170" rx="4"/>'
    d += '<rect class="pf pf-bxs" x="60" y="122" width="180" height="26" rx="4"/>'
    d += t(150, 141, "Primary Health Centre", "sm", "middle")
    d += '<line class="lnc" x1="150" y1="66" x2="150" y2="96"/><line class="lnc" x1="135" y1="81" x2="165" y2="81"/>'
    # one doctor inside, at a desk
    d += _person(110, 170)
    d += '<rect class="hz" x="130" y="212" width="100" height="14" rx="3"/>'
    d += t(180, 268, "one doctor, or none", "sm", "middle")
    # the long queue outside
    for i in range(6):
        d += _person(310 + i * 42, 190)
    d += t(410, 186, "a long queue", "bd", "middle")
    d += a(300, 230, 272, 230)
    # what a triage helper would have to cope with
    d += kit.box(600, 20, 380, 70, "A triage helper must...", "", "solid")
    d += kit.box(600, 105, 380, 55, "work with little data", "no tests, no records", "bx")
    d += kit.box(600, 172, 380, 55, "speak the local language", "Hindi and more", "bx")
    d += kit.box(600, 239, 380, 60, "be safe", "when unsure, send to a hospital", "bxs")
    return figure(1000, 320, d,
                  "A primary health centre with one doctor at a desk and a long queue of six people outside. On the right, what a triage helper must do: work with little data, speak the local language, and be safe by sending people to a hospital when unsure.",
                  "One doctor, or none, faces a long queue, and any helper tool has to work with little data, in local languages, and safely.")


# ------------------------------------------------------------------ court backlog

def d_court_backlog():
    t, a = kit.text, kit.arrow
    d = ""
    # the judge's bench
    d += '<rect class="hz" x="60" y="160" width="260" height="120" rx="6"/>'
    d += '<rect class="pf pf-solid" x="64" y="164" width="252" height="20"/>'
    d += _person(190, 86)
    d += t(190, 236, "the court", "bd", "middle")
    # tower of files on the bench and beside it
    for i in range(9):
        y = 270 - i * 24
        off = (i % 3 - 1) * 5
        d += f'<rect class="hz" x="{350 + off}" y="{y}" width="120" height="20" rx="3"/>'
        d += f'<line class="ln" x1="{362 + off}" y1="{y + 10}" x2="{400 + off}" y2="{y + 10}"/>'
    d += t(410, 56, "pending", "bd", "middle")
    d += t(410, 76, "about 50 million cases", "sm", "middle")
    # the adjournment loop: a file comes up, gets a new date, goes back
    d += kit.box(560, 40, 200, 74, "Case called", "today's list", "bx")
    d += a(762, 77, 800, 77)
    d += kit.box(802, 40, 188, 74, "\"Next date\"", "adjourned", "bxs")
    d += kit.path("M896,116 Q896,200 760,205 Q620,205 620,118", "ln")
    d += t(760, 196, "back in the pile", "sm", "middle")
    # why it gets adjourned
    d += t(560, 250, "why it slips:", "lbl")
    d += t(560, 276, "scheduling clashes · missing papers · adjournments", "sm")
    d += a(552, 200, 478, 200)
    return figure(1000, 300, d,
                  "A judge at a bench beside a tall stack of files labelled about 50 million pending cases. A loop: a case is called on today's list, is given a next date and adjourned, and goes back in the pile. Below: it slips because of scheduling clashes, missing papers and adjournments.",
                  "A case comes up, gets a new date, and goes back on the pile, so about 50 million cases wait.")


# ------------------------------------------------------------------ thin-file credit

def d_thin_file_credit():
    t, a = kit.text, kit.arrow
    d = ""
    # the applicant with an empty file
    d += _person(70, 90)
    d += t(70, 190, "Sunita runs a", "sm", "middle")
    d += t(70, 208, "small stall", "sm", "middle")
    d += '<rect class="hz" x="110" y="110" width="70" height="56" rx="4"/>'
    d += t(145, 135, "credit", "sm", "middle")
    d += t(145, 155, "record", "sm", "middle")
    d += '<line class="lnc" x1="114" y1="164" x2="176" y2="112"/>'
    d += t(145, 96, "empty", "bd", "middle")
    # other data she does have
    d += kit.box(20, 230, 230, 74, "Other data, say,", ["phone bills, UPI payments"], "bxm")
    d += a(252, 267, 318, 180)
    d += a(184, 138, 318, 138)
    # the model
    d += kit.box(320, 90, 220, 110, "A lending model", ["guesses if she", "will repay"], "solid")
    d += a(542, 145, 596, 145)
    d += '<rect class="hz" x="600" y="118" width="96" height="54" rx="10"/>'
    d += t(648, 152, "No", "tt", "middle")
    # two problems
    d += kit.box(740, 30, 245, 100, "Unfair?", ["may turn down whole", "groups more often"], "bxs")
    d += a(698, 132, 738, 90)
    d += kit.box(740, 165, 245, 100, "\"Why me?\"", ["hard to explain to her", "or to the regulator"], "bxs")
    d += a(698, 158, 738, 210)
    return figure(1000, 315, d,
                  "Sunita, who runs a small stall, holds an empty credit record. A lending model uses other data instead, such as phone bills and UPI payments, and says no. Two yellow boxes: is it unfair to whole groups, and can anyone explain why to her or to a regulator?",
                  "With no credit record, a model has to judge from other data, and its answers can be unfair and hard to explain.")


# ------------------------------------------------------------------ informal jobs

def d_informal_jobs():
    t, a = kit.text, kit.arrow
    d = ""
    # Ramesh the mason, with a trowel and no CV
    d += _person(90, 120, "talk")
    d += '<path class="hz" d="M108,146 L130,134 L136,144 L114,156 Z"/>'
    d += t(90, 222, "Ramesh, mason", "bd", "middle")
    d += t(90, 242, "skilled, no CV", "sm", "middle")
    d += _bubble(30, 30, 200, 60, 96, 118)
    d += t(130, 56, "\"Any work", "sm", "middle")
    d += t(130, 76, "this week?\"", "sm", "middle")
    # word-of-mouth chain at the bottom: friend, contractor, one nearby job
    d += kit.path("M120,250 Q170,290 230,286", "lnd")
    d += kit.box(235, 255, 140, 56, "a friend", "", "bx")
    d += a(377, 283, 413, 283)
    d += kit.box(415, 255, 150, 56, "a contractor", "", "bx")
    d += a(567, 283, 603, 283)
    d += kit.box(605, 255, 150, 56, "one job", "if lucky", "bxs")
    d += t(780, 288, "word of mouth", "sm")
    # the job board he cannot reach
    d += '<rect class="hz" x="440" y="20" width="540" height="200" rx="10"/>'
    d += t(710, 48, "job posts", "bd", "middle")
    for i in range(3):
        x = 462 + i * 172
        d += f'<rect class="pf pf-bx" x="{x}" y="66" width="152" height="72" rx="6"/><rect class="bx ol" x="{x}" y="66" width="152" height="72" rx="6"/>'
        d += f'<line class="ln" x1="{x + 14}" y1="88" x2="{x + 120}" y2="88"/><line class="ln" x1="{x + 14}" y1="106" x2="{x + 100}" y2="106"/>'
        d += t(x + 76, 128, "upload CV", "sm", "middle")
    d += t(710, 172, "typed forms, in English,", "sm", "middle")
    d += t(710, 192, "asking for a CV", "sm", "middle")
    d += '<line class="lnd" x1="236" y1="160" x2="430" y2="120"/>'
    d += '<line class="lnc" x1="320" y1="126" x2="344" y2="154"/><line class="lnc" x1="344" y1="126" x2="320" y2="154"/>'
    return figure(1000, 320, d,
                  "Ramesh, a skilled mason with no CV, asks for work this week. A dashed line from him to a board of job posts that ask for a typed CV is crossed out. Instead he goes by word of mouth: a friend, then a contractor, then one job if he is lucky.",
                  "Most workers have skills but no CV, so the jobs posted online never reach them, and work still comes by word of mouth.")


# ------------------------------------------------------------------ indian traffic

def d_indian_traffic():
    t = kit.text
    d = ""
    # a road with no lane markings, edges only
    d += '<path class="ln" d="M20,120 Q500,110 980,120"/><path class="ln" d="M20,300 Q500,310 980,300"/>'
    # self-driving car on the left with a camera
    d += '<path class="hz" d="M40,250 L40,218 Q50,196 80,194 L150,194 Q176,196 190,218 L196,250 Z"/>'
    d += '<circle class="hz" cx="72" cy="254" r="12"/><circle class="hz" cx="166" cy="254" r="12"/>'
    d += '<rect class="hk" x="106" y="182" width="22" height="12" rx="3"/>'
    d += '<path class="lnd" d="M128,188 L300,150 M128,188 L300,240" />'
    # thought bubble: what it learned
    d += '<rect class="bxs" x="30" y="16" width="250" height="78" rx="18"/>'
    d += '<circle class="bxs" cx="100" cy="112" r="9"/><circle class="bxs" cx="112" cy="134" r="6"/>'
    d += t(155, 44, "learned on US roads:", "sm", "middle")
    d += t(155, 66, "neat lanes, cars,", "sm", "middle")
    d += t(155, 86, "rules followed", "sm", "middle")
    # auto-rickshaw
    ax, ay = 340, 170
    d += f'<path class="hz" d="M{ax},{ay + 60} L{ax},{ay + 20} Q{ax + 4},{ay} {ax + 40},{ay} L{ax + 90},{ay} L{ax + 96},{ay + 60} Z"/>'
    d += f'<path class="pf pf-bxs" d="M{ax + 4},{ay + 20} Q{ax + 8},{ay + 4} {ax + 40},{ay + 4} L{ax + 88},{ay + 4} L{ax + 90},{ay + 20} Z"/>'
    d += f'<circle class="hz" cx="{ax + 20}" cy="{ay + 64}" r="10"/><circle class="hz" cx="{ax + 80}" cy="{ay + 64}" r="10"/>'
    d += t(ax + 48, ay + 46, "auto", "sm", "middle")
    # a cow, standing in the road
    cx, cy = 520, 200
    d += f'<ellipse class="hz" cx="{cx}" cy="{cy}" rx="44" ry="22"/>'
    d += f'<ellipse class="hz" cx="{cx + 56}" cy="{cy - 14}" rx="16" ry="11"/>'
    d += f'<path class="ln" d="M{cx + 50},{cy - 24} L{cx + 46},{cy - 34} M{cx + 62},{cy - 24} L{cx + 66},{cy - 34}"/>'
    d += "".join(f'<line class="lnc" x1="{cx + dx}" y1="{cy + 18}" x2="{cx + dx}" y2="{cy + 46}"/>' for dx in (-30, -14, 16, 30))
    d += f'<path class="ln" d="M{cx - 44},{cy - 4} Q{cx - 60},{cy + 6} {cx - 56},{cy + 22}"/>'
    # a hand cart with a person pushing
    d += '<rect class="hz" x="660" y="220" width="90" height="30" rx="4"/>'
    d += '<circle class="hz" cx="680" cy="262" r="12"/><circle class="hz" cx="730" cy="262" r="12"/>'
    d += '<line class="lnc" x1="750" y1="226" x2="776" y2="212"/>'
    d += _person(790, 178)
    d += t(706, 212, "cart", "sm", "middle")
    # a motorbike weaving the wrong way
    d += '<circle class="hz" cx="880" cy="182" r="11"/><circle class="hz" cx="940" cy="182" r="11"/>'
    d += '<path class="hz" d="M880,182 L900,160 L930,160 L940,182"/>'
    d += _person(912, 100)
    d += kit.path("M960,150 Q920,140 880,146", "lnd")
    # question marks over what the car sees
    for x, y in [(386, 150), (520, 150), (706, 196), (912, 92)]:
        d += t(x, y - 8, "?", "tt", "middle")
    d += t(640, 140, "no lanes, mixed traffic, loose rules", "bd", "middle")
    return figure(1000, 320, d,
                  "A road with no lane markings. On the left a self-driving car whose thought bubble says it learned on US roads with neat lanes, cars and rules followed. Ahead of it, each with a question mark: an auto-rickshaw, a cow standing in the road, a hand cart pushed by a person, and a motorbike weaving the wrong way.",
                  "A self-driving model trained on neat Western roads meets no lanes, autos, cows and carts, and stops recognising what it sees.")


DRAWINGS = {
    "groundwater-running-out": d_groundwater,
    "where-delhi-s-air-pollution-comes-from": d_delhi_air,
    "grid-forecasting-with-lots-of-solar": d_solar_grid,
    "too-few-doctors-in-rural-clinics": d_rural_doctor,
    "court-case-backlog": d_court_backlog,
    "credit-for-people-with-no-credit-history": d_thin_file_credit,
    "matching-informal-workers-to-jobs": d_informal_jobs,
    "driving-in-indian-traffic": d_indian_traffic,
}
