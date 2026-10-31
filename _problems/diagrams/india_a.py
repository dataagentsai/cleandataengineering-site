"""Problem diagrams, India group (part A). kit, figure, E and ROOT are injected."""


def _person(cx, top, arm="down"):
    """A small stick person; head centre at (cx, top + 13), feet at top + 80."""
    s = (f'<circle class="hz" cx="{cx}" cy="{top + 13}" r="13"/>'
         f'<line class="lnc" x1="{cx}" y1="{top + 26}" x2="{cx}" y2="{top + 58}"/>'
         f'<line class="lnc" x1="{cx}" y1="{top + 58}" x2="{cx - 11}" y2="{top + 80}"/>'
         f'<line class="lnc" x1="{cx}" y1="{top + 58}" x2="{cx + 11}" y2="{top + 80}"/>'
         f'<line class="lnc" x1="{cx}" y1="{top + 36}" x2="{cx - 16}" y2="{top + 50}"/>')
    if arm == "up":  # hand raised to the ear, holding a phone
        s += (f'<line class="lnc" x1="{cx}" y1="{top + 36}" x2="{cx + 16}" y2="{top + 22}"/>'
              f'<rect class="hk" x="{cx + 12}" y="{top + 4}" width="9" height="18" rx="2"/>')
    else:
        s += f'<line class="lnc" x1="{cx}" y1="{top + 36}" x2="{cx + 16}" y2="{top + 50}"/>'
    return s


def _cloud(cx, cy, s=1.0, cls="hz"):
    """A puffy cloud centred near (cx, cy)."""
    def p(dx, dy):
        return f"{cx + dx * s:.0f},{cy + dy * s:.0f}"
    return (f'<path class="{cls}" d="M{p(-80, 25)} Q{p(-105, 25)} {p(-95, 0)} Q{p(-100, -30)} {p(-60, -25)} '
            f'Q{p(-45, -60)} {p(-5, -45)} Q{p(30, -70)} {p(60, -35)} Q{p(100, -40)} {p(95, -5)} '
            f'Q{p(115, 25)} {p(80, 25)} Z"/>')


def _house(x, y, w=26):
    """A tiny house: walls w wide, roof on top; (x, y) is the bottom-left corner."""
    h = int(w * 0.75)
    return (f'<rect class="hz" x="{x}" y="{y - h}" width="{w}" height="{h}" rx="2"/>'
            f'<path class="hz" d="M{x - 4},{y - h} L{x + w / 2:.0f},{y - h - w * 0.6:.0f} L{x + w + 4},{y - h} Z"/>')


def _temple(x, y):
    """A small temple: base, spire and a flag; (x, y) is the bottom centre."""
    return (f'<rect class="hz" x="{x - 18}" y="{y - 22}" width="36" height="22" rx="2"/>'
            f'<path class="hz" d="M{x - 13},{y - 22} Q{x},{y - 62} {x + 13},{y - 22} Z"/>'
            f'<line class="ln" x1="{x}" y1="{y - 50}" x2="{x}" y2="{y - 70}"/>'
            f'<path class="hk" d="M{x},{y - 70} L{x + 12},{y - 66} L{x},{y - 62} Z"/>')


def _well(x, y):
    """A round well seen from the side; (x, y) is the bottom centre."""
    return (f'<rect class="hz" x="{x - 16}" y="{y - 16}" width="32" height="16" rx="3"/>'
            f'<ellipse class="hz" cx="{x}" cy="{y - 16}" rx="16" ry="5"/>'
            f'<line class="ln" x1="{x - 13}" y1="{y - 16}" x2="{x - 13}" y2="{y - 36}"/>'
            f'<line class="ln" x1="{x + 13}" y1="{y - 16}" x2="{x + 13}" y2="{y - 36}"/>'
            f'<line class="ln" x1="{x - 17}" y1="{y - 36}" x2="{x + 17}" y2="{y - 36}"/>')


# ---------------------------------------------------------------- 1. token tax

def d_token_tax():
    t = kit.text
    d = ""
    d += t(20, 30, "the same question, cut into pieces the model pays for", "sm")
    # English row
    d += t(20, 86, "English", "bd")
    d += t(140, 62, "\"How are you?\"", "sm")
    for i, w in enumerate(["How", "are", "you", "?"]):
        x = 140 + i * 66
        d += f'<rect class="pf pf-bx" x="{x + 3}" y="{72 + 3}" width="58" height="32" rx="7"/><rect class="hz" x="{x}" y="72" width="58" height="32" rx="7" style="fill:none"/>'
        d += t(x + 29, 94, w, "tx", "middle")
    d += t(410, 94, "say 4 pieces", "sm")
    # Hindi row
    d += t(20, 186, "Hindi", "bd")
    d += t(140, 162, "\"आप कैसे हैं?\"", "sm")
    frags = ["आ", "प", "क", "ै", "स", "े", "ह", "ै", "ं", "?"]
    for i, w in enumerate(frags):
        x = 140 + i * 44
        d += f'<rect class="pf pf-bxs" x="{x + 3}" y="{172 + 3}" width="38" height="32" rx="7"/><rect class="hz" x="{x}" y="172" width="38" height="32" rx="7" style="fill:none"/>'
        d += t(x + 19, 194, w, "tx", "middle")
    d += t(140, 228, "say 10 pieces, many of them broken bits of letters", "sm")
    # the bill: coin stacks
    d += '<line class="lnd" x1="700" y1="50" x2="700" y2="240"/>'
    d += t(850, 40, "what you pay", "bd", "middle")
    d += f'<ellipse class="pf pf-bxs" cx="790" cy="96" rx="26" ry="9"/><ellipse class="hz" cx="790" cy="96" rx="26" ry="9" style="fill:none"/>'
    d += t(840, 101, "1×", "bd")
    for j in range(6):
        d += f'<ellipse class="pf pf-bxs" cx="790" cy="{205 - j * 11}" rx="26" ry="9"/><ellipse class="hz" cx="790" cy="{205 - j * 11}" rx="26" ry="9" style="fill:none"/>'
    d += t(830, 180, ["about 3 to 8×,", "and worse answers"], "bd")
    # the data buckets
    d += '<line class="lnd" x1="20" y1="252" x2="980" y2="252"/>'
    d += t(20, 290, "and less to learn from:", "sm")
    for bx, lvl, lab in [(250, 8, "English text: plenty"), (600, 50, "clean Hinglish text: scarce")]:
        d += f'<path class="zg" d="M{bx + 4 + lvl * 0.1:.0f},{268 + lvl} L{bx + 46 - lvl * 0.1:.0f},{268 + lvl} L{bx + 42},{316} L{bx + 8},{316} Z" style="opacity:.8"/>' if lvl < 50 else \
             f'<path class="zg" d="M{bx + 8},{308} L{bx + 42},{308} L{bx + 42},{316} L{bx + 8},{316} Z"/>'
        d += f'<path class="ln" d="M{bx},{266} L{bx + 50},{266} L{bx + 44},{318} L{bx + 6},{318} Z" style="fill:none"/>'
        d += t(bx + 64, 298, lab, "tx")
    return figure(1000, 330, d,
                  "The English question How are you is cut into about 4 pieces; the same Hindi question is cut into about 10 broken pieces. "
                  "One coin pays for English; a stack of coins, about 3 to 8 times more, pays for Hindi. Below, a full bucket of English text and a nearly empty bucket of clean Hinglish text.",
                  "The tokenizer cuts Indian scripts into many more pieces than English, so the same sentence costs about 3 to 8 times more, and there is little clean data to make the answers good.")


# ---------------------------------------------------------------- 2. speech

def d_speech():
    b, a, t = kit.box, kit.arrow, kit.text
    d = ""
    # speaker and speech bubble
    d += '<path class="hz" d="M20,20 L330,20 Q340,20 340,30 L340,82 Q340,92 330,92 L110,92 L84,116 L90,92 L30,92 Q20,92 20,82 L20,30 Q20,20 30,20 Z"/>'
    d += t(180, 50, "\"Bhai, kal market chalein?", "tx", "middle")
    d += t(180, 76, "Traffic bahut hai yaar\"", "tx", "middle")
    d += _person(70, 130)
    d += t(70, 240, "Hinglish, with a", "sm", "middle")
    d += t(70, 260, "Bhojpuri accent", "sm", "middle")
    # noisy street + phone line
    d += t(140, 150, "honk!", "bd")
    d += t(150, 225, "street noise", "sm")
    d += kit.path("M100,190 L130,182 L140,198 L152,180 L164,198 L176,180 L188,198 L200,180 L212,198 L224,182 L240,190 L355,170", "ln")
    d += t(215, 168, "bad phone line", "sm", "middle")
    # model
    d += b(360, 115, 240, 110, "Speech model", ["trained on", "standard Hindi"], "solid")
    d += a(602, 170, 652, 170)
    # transcript
    d += '<rect class="hz" x="655" y="60" width="325" height="200" rx="6"/>'
    d += t(817, 48, "what it writes down", "sm", "middle")
    d += t(680, 108, "Bhai, kal", "tx")
    d += '<rect class="zr" x="760" y="90" width="110" height="26" rx="6"/>' + t(815, 108, "market ka len", "sm", "middle")
    d += '<rect class="zr" x="680" y="136" width="80" height="26" rx="6"/>' + t(720, 154, "trophy", "sm", "middle")
    d += t(770, 154, "bahut", "tx")
    d += '<rect class="zr" x="828" y="136" width="70" height="26" rx="6"/>' + t(863, 154, "haiya", "sm", "middle")
    d += t(680, 205, "the words that matter come out wrong", "sm")
    d += t(680, 230, "(the red ones, as an example)", "sm")
    return figure(1000, 280, d,
                  "A person says a Hinglish sentence, Bhai, kal market chalein, traffic bahut hai yaar, over a honking street and a crackly phone line. "
                  "A speech model trained on standard Hindi writes it down with several words wrong.",
                  "Speech models learn standard Hindi, but people talk in dialects, switch to English mid-sentence, and call from noisy streets.")


# ---------------------------------------------------------------- 3. documents

def d_documents():
    b, a, t = kit.box, kit.arrow, kit.text
    d = ""
    # the scanned record, slightly crooked
    d += '<g transform="rotate(-2 170 170)">'
    d += '<rect class="hz" x="30" y="30" width="270" height="270" rx="4"/>'
    d += t(165, 62, "खसरा / Khasra No.", "bd", "middle")
    for y in (84, 150, 200, 250):
        d += f'<line class="ln" x1="45" y1="{y}" x2="285" y2="{y}"/>'
    d += '<line class="ln" x1="140" y1="84" x2="140" y2="290"/>'
    d += t(50, 112, "मालिक", "sm") + t(50, 140, "Owner", "sm")
    d += t(50, 180, "रकबा / Area", "sm")
    d += t(50, 230, "सर्वे नं.", "sm")
    # handwriting scribbles
    d += '<path class="ln" d="M150,125 q10,-18 20,0 t20,0 t20,-4 q8,-14 16,2 t18,0 t16,-6" style="fill:none"/>'
    d += '<path class="ln" d="M150,180 q8,-16 16,0 t16,-2 t18,4 q10,-12 20,0" style="fill:none"/>'
    d += '<path class="ln" d="M150,232 q6,-14 14,0 t14,0 t14,-4" style="fill:none"/>'
    # the stamp, right over the text
    d += '<circle class="zr" cx="235" cy="215" r="38" style="opacity:.55"/><circle class="lnd" cx="235" cy="215" r="28" style="fill:none"/>'
    d += t(235, 220, "SEAL", "lbl", "middle")
    d += '</g>'
    # callouts on the left gutter of the arrow
    d += t(330, 60, ["two scripts", "on one page"], "sm")
    d += t(330, 256, ["stamp over the", "handwriting"], "sm")
    d += a(305, 165, 435, 165)
    d += b(440, 115, 210, 100, "Text recognition", ["built mostly", "for English"], "solid")
    d += a(652, 165, 700, 165)
    # extracted fields
    for i, f in enumerate(["Owner: ???", "Area: ???", "Survey no.: ???"]):
        d += b(705, 45 + i * 85, 270, 65, f, "", "bxm")
    return figure(1000, 320, d,
                  "A crooked scan of a land record with Hindi and English labels, handwritten entries and a round stamp over the writing. "
                  "It goes into a text recognition tool built mostly for English, and the fields it should pull out, owner, area and survey number, come back as question marks.",
                  "Land records and forms mix scripts, stamps and handwriting, and text recognition for Indian scripts is far behind English, so the key fields come out unreadable.")


# ---------------------------------------------------------------- 4. budget phone

def d_phone():
    t = kit.text
    d = ""
    # flagship phone, small, on the left
    d += '<rect class="hz" x="40" y="70" width="100" height="180" rx="16"/><rect class="pf pf-bx" x="50" y="88" width="80" height="140" rx="6"/>'
    d += t(90, 165, "demo ✓", "bd", "middle")
    d += t(90, 280, ["a flagship phone:", "where demos run"], "sm", "middle")
    # budget phone, centre, with a model too big for it
    d += '<rect class="hz" x="340" y="20" width="160" height="285" rx="20"/><rect class="hz" x="352" y="42" width="136" height="238" rx="6"/>'
    d += kit.box(300, 120, 240, 76, "AI model", "1–3B parameters", "solid")
    d += '<line class="ln" x1="488" y1="34" x2="512" y2="38"/><path class="hz" d="M512,38 L526,24 L600,24 L600,52 L526,52 Z"/>'
    d += t(563, 43, "₹10,000", "lbl", "middle")
    d += t(420, 240, "offline, in Hindi", "sm", "middle")
    d += t(240, 70, ["most Indian", "phones are", "this one"], "sm", "middle")
    d += kit.path("M270,90 Q300,90 334,70", "lnd")
    # three limits
    d += '<line class="lnd" x1="612" y1="70" x2="612" y2="300"/>'
    # memory chip
    d += '<rect class="hz" x="630" y="40" width="50" height="40" rx="4"/><rect class="zr" x="640" y="50" width="30" height="20" rx="2"/>'
    for i in range(4):
        d += f'<line class="ln" x1="{636 + i * 12}" y1="40" x2="{636 + i * 12}" y2="32"/><line class="ln" x1="{636 + i * 12}" y1="80" x2="{636 + i * 12}" y2="88"/>'
    d += t(710, 58, "Memory", "bd") + t(710, 80, "the model barely fits", "sm")
    # battery
    d += '<rect class="hz" x="630" y="132" width="50" height="26" rx="4"/><rect class="hk" x="680" y="139" width="5" height="12" rx="1"/><rect class="zr" x="634" y="136" width="9" height="18" rx="2"/>'
    d += t(710, 142, "Battery", "bd") + t(710, 164, "every answer drains it", "sm")
    # thermometer
    d += '<rect class="hz" x="649" y="200" width="12" height="50" rx="6"/><circle class="zr" cx="655" cy="256" r="11"/><rect class="zr" x="652" y="212" width="6" height="40"/>'
    d += t(625, 215, "~", "bd", "middle") + t(688, 215, "~", "bd", "middle")
    d += t(710, 226, "Heat", "bd") + t(710, 248, "it gets hot, then slows down", "sm")
    return figure(1000, 315, d,
                  "On the left, a flagship phone showing a working demo. In the centre, a ₹10,000 budget phone with an AI model of 1 to 3 billion parameters drawn too wide for it. "
                  "On the right, three limits: memory, battery and heat.",
                  "On-device AI demos run on flagship phones, but most Indian phones are budget models, where memory, battery and heat are the limit.")


# ---------------------------------------------------------------- 5. addresses

def d_address():
    b, a, t = kit.box, kit.arrow, kit.text
    d = ""
    # the address slip
    d += '<rect class="hz" x="20" y="40" width="260" height="120" rx="6"/>'
    d += t(30, 30, "the address, as people write it", "sm")
    d += t(36, 76, "Ground floor, behind", "tx") + t(36, 102, "the temple, near the", "tx") + t(36, 128, "old well, Ward 7", "tx")
    d += a(282, 100, 322, 100)
    d += b(325, 55, 170, 90, "Map software", ["turns text into", "one map point"], "bx")
    # the map
    d += '<rect class="hz" x="535" y="15" width="445" height="295" rx="10"/>'
    d += '<path class="ln" d="M535,170 Q700,150 980,180" style="fill:none"/><path class="ln" d="M720,15 Q700,160 740,310" style="fill:none"/>'
    # two temples, two wells: which one?
    d += _temple(600, 150) + _well(660, 150)
    d += _temple(800, 290) + _well(860, 290)
    d += t(630, 42, ["a temple", "and a well"], "sm", "middle")
    d += t(892, 238, ["another", "temple,", "another", "well"], "sm")
    # the real door, with a dashed 100 m circle
    d += _house(830, 140, 28)
    d += '<circle class="lnd" cx="844" cy="125" r="42" style="fill:none"/>'
    d += t(844, 62, "the real door", "bd", "middle")
    # the pin, landing at the wrong temple
    d += '<path class="pf pf-solid" d="M600,182 q-16,0 -16,16 q0,12 16,30 q16,-18 16,-30 q0,-16 -16,-16 Z"/><path class="ln" d="M600,182 q-16,0 -16,16 q0,12 16,30 q16,-18 16,-30 q0,-16 -16,-16 Z" style="fill:none"/>'
    d += '<circle class="hz" cx="600" cy="198" r="5"/>'
    d += t(630, 250, "the pin lands here", "bd")
    d += kit.path("M497,120 Q545,180 580,205", "ln")
    d += t(20, 210, "the rider, the ambulance and the bank's", "sm")
    d += t(20, 232, "address check all go to the pin", "sm")
    d += t(20, 276, "DIGIPIN, a national digital address", "sm")
    d += t(20, 298, "code, is new and not yet on most", "sm")
    return figure(1000, 320, d,
                  "An address written as behind the temple, near the old well, Ward 7 goes into map software. On the map there are two temples and two wells; "
                  "the pin lands by the wrong temple, far outside a dashed circle around the real door.",
                  "Indian addresses are directions in free text, not codes, so the map point lands at the wrong temple and deliveries, ambulances and KYC checks miss.")


# ---------------------------------------------------------------- 6. voice-clone scam

def d_scam():
    b, a, t = kit.box, kit.arrow, kit.text
    d = ""
    d += b(15, 110, 160, 100, "Scammer", ["a short clip of", "the son's voice"], "bxm")
    d += a(177, 160, 212, 160)
    d += b(215, 110, 160, 100, "Voice cloner", ["speaks Hindi in", "the son's voice"], "solid")
    d += a(377, 160, 412, 160)
    # the filter, a sieve with a big hole
    d += b(415, 100, 190, 120, "Scam filter", ["trained mostly", "on English"], "bxs")
    d += t(510, 250, "lets it through ✓", "sm", "middle")
    d += a(607, 160, 690, 160)
    # mother on the phone, with the call in a bubble
    d += _person(730, 120, arm="up")
    d += '<path class="hz" d="M620,15 L975,15 Q985,15 985,25 L985,80 Q985,90 975,90 L770,90 L748,112 L748,90 L630,90 Q620,90 620,80 L620,25 Q620,15 630,15 Z"/>'
    d += t(800, 44, "\"Maa, main hoon! Jaldi ₹20,000", "tx", "middle")
    d += t(800, 72, "UPI kar do, bahut urgent hai\"", "tx", "middle")
    d += t(800, 108, "(say)", "lbl", "middle")
    d += t(770, 160, "\"It's my son.\"", "bd")
    # the UPI payment
    d += a(745, 230, 820, 260)
    d += '<rect class="zr" x="825" y="240" width="150" height="44" rx="10"/>'
    d += t(900, 268, "UPI: money gone", "bd", "middle")
    return figure(1000, 300, d,
                  "A scammer feeds a short clip of a son's voice to a voice cloner. The cloned call, in Hindi, asks a mother to send ₹20,000 on UPI urgently. "
                  "It passes a scam filter trained mostly on English, and the mother pays.",
                  "Scam calls now use cloned voices in Indian languages, and the detectors meant to stop them were trained mostly on English.")


# ---------------------------------------------------------------- 7. monsoon

def d_monsoon():
    b, t = kit.box, kit.text
    d = ""
    # the coarse forecast grid
    gx, gy, cw, ch = 30, 120, 190, 95
    for r in range(2):
        for c in range(3):
            d += f'<rect class="hz" x="{gx + c * cw}" y="{gy + r * ch}" width="{cw}" height="{ch}"/>'
            if (r, c) != (0, 1):
                d += t(gx + c * cw + cw / 2, gy + r * ch + ch / 2 + 6, "\"light rain\"", "sm", "middle")
    d += t(30, 338, "a global model: one forecast for each big square", "sm")
    # the downpour on one district
    d += _cloud(355, 50, 0.75, "pf pf-solid")
    d += _cloud(355, 50, 0.75, "ln")
    for i in range(7):
        x = 318 + i * 13
        d += f'<line class="ln" x1="{x}" y1="72" x2="{x - 8}" y2="{140}"/>'
    d += t(gx + cw + 8, gy + ch - 8, "\"light rain\"", "sm")
    # the flooded village under it
    d += '<path class="zr" d="M298,192 Q350,178 406,192 L406,213 L298,213 Z" style="opacity:.7"/>'
    d += _house(310, 188, 22) + _house(342, 184, 22) + _house(374, 188, 22)
    d += t(462, 46, ["a downpour on", "one district"], "sm")
    # right side
    d += b(640, 35, 340, 105, "What a district needs", ["heavy rain, here,", "a few hours ahead"], "solid")
    d += b(640, 165, 340, 105, "What it gets", ["good big-picture forecasts;", "floods hit with little warning"], "bxs")
    d += t(810, 300, "as in Assam and Kerala", "sm", "middle")
    return figure(1000, 350, d,
                  "A grid of big forecast squares, each saying light rain. A dark cloud pours on one district inside one square, and its houses stand in floodwater. "
                  "Beside it: a district needs heavy-rain warnings a few hours ahead, but gets big-picture forecasts and floods with little warning.",
                  "Global AI weather models see the big picture, but the rain that floods one district a few hours from now falls inside a single square.")


# ---------------------------------------------------------------- 8. small farms

def d_farms():
    b, a, t = kit.box, kit.arrow, kit.text
    d = ""
    # strips of small plots
    fx, fy, fw, fh = 30, 50, 360, 240
    strips = [(0, 50, "zg"), (50, 35, "zy"), (85, 60, "pf pf-bx"), (145, 30, "zg"), (175, 55, "zy"),
              (230, 40, "pf pf-bxs"), (270, 45, "zg"), (315, 45, "pf pf-bx")]
    for x0, w, cls in strips:
        d += f'<rect class="{cls}" x="{fx + x0}" y="{fy}" width="{w}" height="{fh / 2:.0f}" style="opacity:.75"/>'
        d += f'<rect class="hz" x="{fx + x0}" y="{fy}" width="{w}" height="{fh / 2:.0f}" style="fill:none"/>'
    strips2 = [(0, 70, "pf pf-bxs"), (70, 40, "zg"), (110, 45, "zy"), (155, 65, "zg"), (220, 35, "pf pf-bx"),
               (255, 50, "zy"), (305, 55, "zg")]
    for x0, w, cls in strips2:
        d += f'<rect class="{cls}" x="{fx + x0}" y="{fy + fh / 2:.0f}" width="{w}" height="{fh / 2:.0f}" style="opacity:.75"/>'
        d += f'<rect class="hz" x="{fx + x0}" y="{fy + fh / 2:.0f}" width="{w}" height="{fh / 2:.0f}" style="fill:none"/>'
    # the satellite pixel grid on top
    for i in range(4):
        d += f'<line class="lnc" x1="{fx + i * 120}" y1="{fy}" x2="{fx + i * 120}" y2="{fy + fh}" style="stroke-dasharray:8 6"/>'
    for j in range(3):
        d += f'<line class="lnc" x1="{fx}" y1="{fy + j * 120}" x2="{fx + fw}" y2="{fy + j * 120}" style="stroke-dasharray:8 6"/>'
    d += f'<rect class="lnc" x="{fx + 240}" y="{fy}" width="120" height="120" style="fill:none;stroke-width:5"/>'
    d += t(30, 36, "small plots, with the satellite's 10-metre pixels drawn on top", "sm")
    d += t(210, 316, "one pixel covers several farmers' plots", "sm", "middle")
    # what one pixel says
    d += a(394, 110, 452, 110)
    d += b(455, 50, 230, 120, "One pixel, one colour", ["rice + wheat + bare soil", "blended together"], "bxs")
    d += t(570, 200, ["which plot is", "stressed? no idea"], "sm", "middle")
    # ground truth
    d += _person(780, 200)
    d += '<rect class="hz" x="800" y="232" width="26" height="32" rx="3"/><line class="ln" x1="805" y1="242" x2="821" y2="242"/><line class="ln" x1="805" y1="252" x2="821" y2="252"/>'
    d += b(720, 50, 260, 120, "Ground truth", ["how much did this plot", "really yield? few records"], "bxm")
    d += t(860, 225, ["the check on", "the answer", "is scarce"], "sm")
    return figure(1000, 330, d,
                  "A patchwork of narrow farm plots with a grid of 10-metre satellite pixels drawn over it; each pixel covers several plots. "
                  "One pixel gives one blended colour, so nobody can tell which plot is stressed, and a farmer with a notebook stands by: real yield records are few.",
                  "Satellite pixels are 10 metres across, bigger than many Indian plots, so one pixel blends several farms, and there is little ground truth to check against.")


DRAWINGS = {
    "ai-in-indian-languages-costs-more-and": d_token_tax,
    "speech-recognition-for-dialects-and-code-mixed": d_speech,
    "reading-indian-documents-land-records-forms-handwriting": d_documents,
    "useful-ai-on-a-10-000-phone": d_phone,
    "addresses-that-machines-can-t-read": d_address,
    "voice-clone-and-upi-scams-in-indian": d_scam,
    "hyperlocal-monsoon-and-flood-forecasts": d_monsoon,
    "crop-yield-and-stress-for-small-farms": d_farms,
}
