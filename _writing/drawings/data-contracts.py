"""Drawings for 'Data contracts: stop breaking the team downstream'. kit, figure, E and ROOT are injected by build.py."""


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


def drawing_dc_parcel():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(500, 24, "the parcel is the data; the signed note is the contract", "sm", "middle")
    d += _person(120, 120, "right")
    d += t(120, 250, "Producer", "bd", "middle") + t(120, 270, "the app team", "sm", "middle")
    d += _person(880, 120, "left")
    d += t(880, 250, "Consumer", "bd", "middle") + t(880, 270, "the data team", "sm", "middle")
    # parcel
    d += '<rect class="hz" x="420" y="150" width="160" height="100" rx="4"/>'
    d += '<line class="ln" x1="500" y1="150" x2="500" y2="250"/><line class="ln" x1="420" y1="200" x2="580" y2="200"/>'
    # note on top
    d += '<path class="hz" d="M440,55 L560,55 L560,140 L440,140 Z"/>'
    d += t(500, 76, "orders v1.3", "bd", "middle")
    d += t(500, 96, ["what's inside", "when it arrives"], "sm", "middle")
    d += '<path class="ln" d="M465,132 Q475,122 485,132 Q495,142 505,130 Q515,120 530,132"/>'
    d += '<line class="lnd" x1="500" y1="140" x2="500" y2="150"/>'
    d += a(160, 175, 405, 195, "hands over", lx=280, ly=170)
    d += a(595, 195, 840, 175, "builds on it", lx=720, ly=170)
    d += b(320, 280, 360, 60, "Change coming?", "tell the consumer first", "bxs")
    return figure(1000, 355, d, "A producer stick figure hands a parcel to a consumer stick figure. A signed note on the parcel reads orders v1.3: what's inside, when it arrives. Below, a yellow box says: change coming? tell the consumer first.",
                  "A data contract is the signed note on the parcel. The consumer builds on the note, not on guesses.")


def drawing_dc_card():
    b, t = kit.box, kit.text
    d = t(500, 22, "one contract per dataset, kept next to the code", "sm", "middle")
    links = [(250, 135, 330, 150), (250, 220, 330, 205), (750, 135, 670, 180), (750, 220, 670, 240), (750, 305, 670, 270), (250, 305, 330, 235)]
    for x1, y1, x2, y2 in links:
        d += f'<line class="lnd" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>'
    d += '<rect class="hz" x="330" y="40" width="340" height="270" rx="8"/>'
    d += '<line class="ln" x1="330" y1="88" x2="670" y2="88"/>'
    d += t(500, 72, "orders.contract.yaml", "bd", "middle")
    rows = [("schema", "order_id, amount, ..."), ("meaning", "amount: ₹, incl. tax"), ("rules", "amount >= 0"),
            ("freshness", "in by 6 a.m."), ("owner", "app-orders team"), ("changes", "30 days' notice")]
    for i, (k, v) in enumerate(rows):
        y = 120 + i * 32
        d += t(355, y, k, "sm") + t(450, y, v, "tx")
    d += b(20, 100, 230, 70, "What it looks like", "columns and types", "bxm")
    d += b(20, 185, 230, 70, "What it means", "each column in words", "bxm")
    d += b(20, 270, 230, 70, "What must be true", "quality rules", "bxm")
    d += b(750, 100, 230, 70, "When it arrives", "freshness", "bxm")
    d += b(750, 185, 230, 70, "Who answers", "a team, not a person", "bxm")
    d += b(750, 270, 230, 70, "How it changes", "notice and versions", "bxm")
    return figure(1000, 355, d, "A drawn card titled orders.contract.yaml with six lines: schema, meaning, rules, freshness, owner, changes. Labels around it say what it looks like, what it means, what must be true, when it arrives, who answers, and how it changes.",
                  "What a contract holds. Every line answers a question a consumer would otherwise ask on chat.")


def drawing_dc_checkpoints():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(500, 22, "the same contract file, checked in three places", "sm", "middle")
    d += b(10, 60, 160, 80, "Producer", "changes the app", "bxm")
    d += a(172, 100, 208, 100)
    d += b(210, 50, 170, 100, "CI check", ["before the change", "ships"], "bxs")
    d += kit.num(225, 50, 1)
    d += a(382, 100, 418, 100)
    d += b(420, 60, 140, 80, "Bronze", "as it arrived", "bx")
    d += a(562, 100, 598, 100)
    d += b(600, 50, 170, 100, "Ingestion check", ["before rows", "reach silver"], "bxs")
    d += kit.num(615, 50, 2)
    d += a(772, 100, 808, 100)
    d += b(810, 60, 180, 80, "Silver", "only good rows", "bx")
    d += a(685, 152, 685, 208, "fails", lx=695, ly=185, anchor="start")
    d += b(600, 210, 170, 70, "Quarantine", "+ alert the owner", "bxm")
    d += b(810, 210, 180, 90, "Monitoring", ["on time?", "usual row count?"], "bxs")
    d += kit.num(825, 210, 3)
    d += '<line class="lnd" x1="900" y1="208" x2="900" y2="142"/>'
    d += b(210, 210, 170, 70, "Contract file", "one source of truth", "solid")
    d += '<line class="lnd" x1="295" y1="208" x2="295" y2="152"/>'
    d += '<path class="lnd" d="M382,240 Q560,235 625,152"/>'
    d += t(500, 268, "same file", "sm", "middle")
    return figure(1000, 320, d, "A row: producer, a CI check (1), bronze, an ingestion check (2), silver. Failing rows go from the ingestion check to quarantine with an alert to the owner. Monitoring (3) watches silver for freshness and row count. One contract file feeds the CI check and the ingestion check.",
                  "Three checkpoints. The earlier the check, the cheaper the break.")


def drawing_dc_sort():
    b, t = kit.box, kit.text
    d = t(500, 24, "would a consumer who did nothing wrong get a wrong answer?", "bd", "middle")
    d += '<rect class="zr" x="20" y="50" width="470" height="270" rx="10"/>'
    d += '<rect class="zg" x="510" y="50" width="470" height="270" rx="10"/>'
    d += t(255, 80, "BREAKING: major version, announce first", "lbl", "middle")
    d += t(745, 80, "SAFE: minor version, ship it", "lbl", "middle")
    breaking = [("Rename a column", "amount to order_amount"), ("Drop a column", ""),
                ("Change a type", "number to text"), ("Change the meaning", "amount now excludes tax")]
    for i, (n, s) in enumerate(breaking):
        x = 40 + (i % 2) * 220
        y = 100 + (i // 2) * 105
        d += b(x, y, 210, 90, n, s, "bx")
    d += b(530, 100, 430, 90, "Add an optional column", "coupon, null for old rows", "bx")
    d += b(530, 205, 430, 90, "Loosen an unused rule", "safe, but get a quick review", "bxm")
    return figure(1000, 335, d, "Two bins. The red bin, breaking, holds rename a column, drop a column, change a type, and change the meaning. The green bin, safe, holds add an optional column, and loosen an unused rule with a quick review.",
                  "Sort every change into one of two bins before it ships. The bin decides the version number.")


DRAWINGS = {"dc-parcel": drawing_dc_parcel, "dc-card": drawing_dc_card,
            "dc-checkpoints": drawing_dc_checkpoints, "dc-sort": drawing_dc_sort}
