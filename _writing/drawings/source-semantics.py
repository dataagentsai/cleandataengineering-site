"""Drawings for 'Source semantic understanding: a key to data program success'. kit, figure, E and ROOT are injected by build.py."""


def _person(cx, top, arm=""):
    d = (f'<circle class="bx" cx="{cx}" cy="{top + 13}" r="13"/>'
         f'<line class="lnc" x1="{cx}" y1="{top + 26}" x2="{cx}" y2="{top + 70}"/>'
         f'<line class="lnc" x1="{cx}" y1="{top + 70}" x2="{cx - 12}" y2="{top + 98}"/>'
         f'<line class="lnc" x1="{cx}" y1="{top + 70}" x2="{cx + 12}" y2="{top + 98}"/>')
    if arm == "right":
        d += f'<line class="lnc" x1="{cx}" y1="{top + 40}" x2="{cx + 30}" y2="{top + 48}"/>'
        d += f'<line class="lnc" x1="{cx}" y1="{top + 40}" x2="{cx - 16}" y2="{top + 60}"/>'
    else:
        d += f'<line class="lnc" x1="{cx}" y1="{top + 40}" x2="{cx - 30}" y2="{top + 48}"/>'
        d += f'<line class="lnc" x1="{cx}" y1="{top + 40}" x2="{cx + 16}" y2="{top + 60}"/>'
    return d


def drawing_sem_two_halves():
    b, t = kit.box, kit.text
    d = t(500, 24, "two kinds of understanding; tools only help with one", "sm", "middle")
    # plumbing
    d += '<rect class="hz" x="20" y="45" width="460" height="265" rx="10"/>'
    d += t(250, 75, "PLUMBING", "lbl", "middle")
    d += b(50, 95, 130, 70, "Source", "app, database", "bx")
    d += b(320, 95, 130, 70, "Lake", "tables land", "bx")
    d += '<line class="ln" x1="182" y1="120" x2="318" y2="120"/><line class="ln" x1="182" y1="140" x2="318" y2="140"/>'
    d += kit.arrow(200, 130, 300, 130)
    d += t(60, 190, ["where it lives", "how to connect", "how to pick up changes"], "tx")
    d += b(60, 246, 380, 56, "When broken, it shouts", "the load fails", "bxm")
    # meaning
    d += '<rect class="hz" x="520" y="45" width="460" height="265" rx="10"/>'
    d += t(750, 75, "MEANING", "lbl", "middle")
    d += '<rect class="hz" x="550" y="100" width="250" height="60" rx="4"/>'
    d += '<line class="ln" x1="635" y1="100" x2="635" y2="160"/><line class="ln" x1="710" y1="100" x2="710" y2="160"/>'
    d += t(592, 136, "₹10,000", "sm", "middle") + t(672, 136, "status 07", "sm", "middle") + t(755, 136, "9999-12-31", "sm", "middle")
    d += '<circle class="hz" cx="860" cy="125" r="34"/><line class="lnc" x1="884" y1="149" x2="920" y2="185"/>'
    d += t(860, 131, "?", "bd", "middle")
    d += t(560, 190, ["what one row is", "which records count", "which date matters"], "tx")
    d += b(560, 246, 380, 56, "When wrong, it whispers", "the load succeeds", "bxs")
    return figure(1000, 325, d, "Two panels. Plumbing: a source connected to a lake by a pipe, with where it lives, how to connect and how to pick up changes; when broken, it shouts. Meaning: a data row reading 10,000 rupees, status 07, 9999-12-31 under a magnifying glass, with what one row is, which records count and which date matters; when wrong, it whispers.",
                  "Plumbing failures stop the load. Meaning failures let it succeed with the wrong answer.")


def drawing_sem_six():
    b = kit.box
    d = kit.text(500, 24, "almost every meaning problem falls under one of these", "sm", "middle")
    d += b(390, 160, 220, 80, "One source", "six questions", "solid")
    items = [("What is one row?", "grain, key, master copy"), ("What life does it live?", "statuses, fixes, deletes"),
             ("What time is it?", "which date, zone, year"), ("What do values mean?", "codes, money, blanks"),
             ("How do records connect?", "header and lines, hierarchies"), ("What can we trust?", "test data, trusted report")]
    for i, (ti, su) in enumerate(items):
        left = i < 3
        x = 30 if left else 700
        y = 50 + (i % 3) * 110
        kind = "bxs" if i == 5 else "bx"
        d += b(x, y, 270, 80, ti, su, kind)
        d += kit.num(x + 14, y, i + 1)
        if left:
            d += f'<line class="lnd" x1="302" y1="{y + 40}" x2="388" y2="200"/>'
        else:
            d += f'<line class="lnd" x1="698" y1="{y + 40}" x2="612" y2="200"/>'
    return figure(1000, 360, d, "One source in the middle with six numbered questions around it: what is one row, what life does it live, what time is it, what do values mean, how do records connect, and what can we trust.",
                  "Six questions for every source. The sixth, which report the business trusts, is the one that proves the rest.")


def drawing_sem_order_life():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(500, 24, "the same correct data, two different totals", "sm", "middle")
    d += t(20, 82, "Order A", "bd")
    d += b(110, 55, 140, 60, "Draft", "", "bxm") + a(252, 85, 278, 85)
    d += b(280, 55, 140, 60, "Approved", "", "bxm") + a(422, 85, 448, 85)
    d += b(450, 50, 170, 70, "Posted", "₹10,000", "bx") + a(622, 85, 718, 85, "a week later", lx=670, ly=72)
    d += b(720, 50, 260, 70, "Return", "−₹2,000, a row of its own", "bx")
    d += t(20, 172, "Order B", "bd")
    d += b(110, 145, 140, 60, "Draft", "", "bxm") + a(252, 175, 278, 175)
    d += b(280, 140, 230, 70, "Cancelled", "amount still ₹10,000", "bxs")
    d += '<rect class="zr" x="90" y="245" width="380" height="110" rx="10"/>'
    d += '<rect class="zg" x="530" y="245" width="380" height="110" rx="10"/>'
    d += b(120, 265, 320, 70, "Naive sum: ₹18,000", "every row, every status", "bxm")
    d += b(560, 265, 320, 70, "Finance: ₹8,000", "posted, less returns", "solid")
    return figure(1000, 370, d, "Order A goes draft, approved, posted at 10,000 rupees, and a week later a return of minus 2,000 rupees is booked as its own row. Order B goes draft then cancelled, with its amount still 10,000 rupees. A red panel shows the naive sum, 18,000 rupees; a green panel shows finance's figure, 8,000 rupees.",
                  "Nothing is broken. The only difference is knowing which statuses count and how returns are booked.")


def drawing_sem_who():
    b, t = kit.box, kit.text
    d = t(500, 24, "three people, three kinds of answer", "sm", "middle")
    d += _person(170, 40, "right") + _person(500, 40, "left") + _person(830, 40, "left")
    # the engineer's profile sheet
    d += '<rect class="hz" x="770" y="62" width="34" height="44" rx="3"/>'
    d += '<line class="ln" x1="776" y1="74" x2="798" y2="74"/><line class="ln" x1="776" y1="84" x2="798" y2="84"/><line class="ln" x1="776" y1="94" x2="792" y2="94"/>'
    d += t(170, 162, "Architect", "bd", "middle") + t(500, 162, "Key user", "bd", "middle") + t(830, 162, "Data engineer", "bd", "middle")
    d += b(50, 180, 240, 70, "Where it lives", "and how to reach it", "bx")
    d += b(380, 180, 240, 70, "What it means", "which rows count, and why", "solid")
    d += b(710, 180, 240, 70, "What the data says", "a profile of real rows", "bxs")
    d += kit.arrow(708, 215, 622, 215, "shows", lx=665, ly=205)
    d += b(150, 290, 700, 60, "One short session per source", "people react to real data far better than they remember rules", "bxm")
    return figure(1000, 365, d, "Three stick figures. The architect knows where the data lives and how to reach it. The key user knows what it means and which rows count. The data engineer, holding a sheet, brings a profile of real rows and shows it to the key user. Below: one short session per source.",
                  "Ask the architect who knows. Then put a profile of real data in front of that person.")


def drawing_sem_one_record():
    b, t = kit.box, kit.text
    d = t(500, 22, "write the meaning down once, next to the loading settings", "sm", "middle")
    d += '<rect class="hz" x="40" y="40" width="390" height="270" rx="8"/>'
    d += '<line class="ln" x1="40" y1="86" x2="430" y2="86"/>'
    d += t(235, 70, "sales.orders", "bd", "middle")
    rows = [("grain", "one row per order line"), ("key", "order_id + line_no"), ("report date", "posting_date"),
            ("counts when", "POSTED, CLOSED"), ("amount", "INR, excl. tax"), ("trusted", "Finance sales pack")]
    for i, (k, v) in enumerate(rows):
        y = 118 + i * 32
        d += t(62, y, k, "sm") + t(185, y, v, "tx")
    d += b(560, 45, 400, 70, "Quality rules", "status known, key unique, run on every load", "bx")
    d += b(560, 140, 400, 70, "Catalog descriptions", "users read the meaning, not guess it", "bx")
    d += b(560, 235, 400, 70, "Reconciliation", "lake total matches the trusted report", "solid")
    d += kit.arrow(432, 120, 556, 80) + kit.arrow(432, 175, 556, 175) + kit.arrow(432, 230, 556, 268)
    return figure(1000, 325, d, "A drawn card for sales.orders lists grain, key, report date, counts when, amount and trusted report. Arrows lead to three uses: quality rules, catalog descriptions, and reconciliation against the trusted report.",
                  "One semantic record, three payoffs. The last one, reconciliation, is the definition of done.")


DRAWINGS = {"sem-two-halves": drawing_sem_two_halves, "sem-six": drawing_sem_six,
            "sem-order-life": drawing_sem_order_life, "sem-who": drawing_sem_who,
            "sem-one-record": drawing_sem_one_record}
