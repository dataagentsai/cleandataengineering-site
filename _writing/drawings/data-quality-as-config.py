"""Drawings for 'Data quality as config, not code'. kit, figure, E and ROOT are injected by build.py."""


def _notebook(x, y, lines):
    t = kit.text
    d = f'<rect class="hz" x="{x}" y="{y}" width="104" height="78" rx="4"/>'
    d += "".join(f'<circle class="hz" cx="{x + 16 + j * 18}" cy="{y}" r="4"/>' for j in range(5))
    d += t(x + 52, y + 34, lines, "sm", "middle")
    return d


def drawing_dq_scattered():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(225, 26, "before: a check in every notebook", "bd", "middle")
    books = [["is it null?", ""], ["dupes, v2", "(copied)"], ["amount > 0", ""],
             ["is it null?", "(again)"], ["country in", "a list"], ["???", "nobody knows"]]
    for i, lines in enumerate(books):
        d += _notebook(40 + (i % 3) * 130, 60 + (i // 3) * 112, lines)
    d += t(225, 290, "40 notebooks, 40 slightly different rules", "sm", "middle")
    d += '<line class="lnd" x1="465" y1="20" x2="465" y2="295"/>'
    d += t(735, 26, "after: one rules file, one engine", "bd", "middle")
    d += b(495, 80, 190, 110, "orders.dq.yaml", ["every rule for", "the dataset"], "bxs")
    d += a(687, 135, 763, 135, "read by")
    d += b(765, 80, 210, 110, "One engine", ["runs the rules", "at every hop"], "solid")
    d += t(735, 250, ["a new dataset is a new file;", "a new rule is a new line"], "sm", "middle")
    return figure(1000, 305, d, "Left: six notebooks, each with its own copy of a check, some copied, one that nobody understands. Right: one rules file read by one engine that runs the rules at every hop.",
                  "The same checks, written forty times or written once. Only one of these can be reviewed in a single pull request.")


def drawing_dq_rule_card():
    b, t = kit.box, kit.text
    d = t(500, 22, "one rule is a few lines of config: no Python, no SQL", "sm", "middle")
    for x1, y1, x2, y2 in [(250, 135, 330, 155), (250, 220, 330, 200), (750, 185, 670, 230), (750, 270, 670, 260)]:
        d += f'<line class="lnd" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>'
    d += '<rect class="hz" x="330" y="40" width="340" height="250" rx="8"/>'
    d += '<line class="ln" x1="330" y1="88" x2="670" y2="88"/>'
    d += t(500, 72, "DQ-01", "bd", "middle")
    rows = [("dataset", "orders"), ("rule", "is_complete"), ("column", "customer_id"),
            ("severity", "block"), ("action", "quarantine"), ("owner", "sales-data")]
    for i, (k, v) in enumerate(rows):
        y = 118 + i * 30
        d += t(355, y, k, "sm") + t(470, y, v, "tx")
    d += b(20, 100, 230, 70, "What to check", "a rule type and a column", "bxm")
    d += b(20, 185, 230, 70, "How serious", "warn or block", "bxm")
    d += b(750, 150, 230, 70, "What happens", "to the rows that fail", "bxm")
    d += b(750, 235, 230, 70, "Who owns it", "and gets the alert", "bxm")
    return figure(1000, 315, d, "A drawn index card for rule DQ-01: dataset orders, rule is_complete, column customer_id, severity block, action quarantine, owner sales-data. Labels around it say what to check, how serious, what happens to failing rows, and who owns it.",
                  "One rule as a card. Every rule in the file answers the same four questions.")


def drawing_dq_engine_hop():
    b, a, t = kit.box, kit.arrow, kit.text
    d = b(10, 115, 150, 90, "Bronze", "50,012 rows in", "bx")
    d += a(162, 160, 198, 160)
    d += b(225, 10, 180, 54, "Rules table", "", "bxm") + a(315, 66, 315, 92)
    d += b(200, 95, 230, 130, "The DQ engine", ["one interface,", "runs every rule"], "solid")
    d += b(200, 262, 108, 50, "Spark SQL", "", "bx") + b(322, 262, 108, 50, "Deequ", "", "bx")
    d += '<line class="lnd" x1="254" y1="260" x2="285" y2="227"/><line class="lnd" x1="376" y1="260" x2="345" y2="227"/>'
    d += t(315, 340, "adapters: swap one for the other with one line", "sm", "middle")
    d += a(432, 115, 528, 55, "passes", lx=470, ly=70, anchor="end")
    d += b(530, 15, 210, 80, "Silver", "49,780 good rows", "bx")
    d += a(432, 160, 528, 162, "fails", lx=480, ly=150)
    d += b(530, 118, 210, 90, "Quarantine", ["232 rows, each with", "the rule it broke"], "bxm")
    d += a(432, 205, 528, 268, "results", lx=470, ly=258, anchor="end")
    d += b(530, 230, 210, 90, "Results table", ["one row per rule", "per run"], "bxs")
    d += a(742, 255, 788, 220) + a(742, 295, 788, 312)
    d += b(790, 180, 200, 70, "Dashboard", "trends per dataset", "bx")
    d += b(790, 280, 150, 66, "Alert", "to the owner", "bxs")
    d += ('<path class="hz" d="M956,330 Q956,300 970,298 Q984,300 984,330 L988,336 L952,336 Z"/>'
          '<circle class="hk" cx="970" cy="341" r="3"/>')
    return figure(1000, 355, d, "Bronze rows go into the data quality engine, which reads the rules table and runs them through an adapter, Spark SQL or Deequ. Passing rows go to silver, failing rows go to quarantine with the rule they broke, and results go to a results table that feeds a dashboard and an alert to the owner.",
                  "One hop, one engine. The numbers are from a recorded run on 50,012 orders in DataTwin Studio.")


def drawing_dq_rule_types():
    b, t = kit.box, kit.text
    d = t(500, 26, "row rules: judge one row, so a bad row can go to quarantine", "bd", "middle")
    row = [("Completeness", "is it there?"), ("Uniqueness", "only once?"),
           ("Validity", "an allowed value?"), ("Referential", "does its parent exist?")]
    for i, (n, s) in enumerate(row):
        d += b(10 + i * 248, 45, 230, 90, n, s, "bx")
    d += t(500, 186, "table rules: judge the whole batch, so they warn or stop the load", "bd", "middle")
    tab = [("Freshness", "did it arrive on time?", "bxs"), ("Volume", "about the usual count?", "bxs"),
           ("Reconciliation", ["do the counts add up?", "bronze = silver + quarantine"], "solid")]
    for i, (n, s, k) in enumerate(tab):
        d += b(10 + i * 335, 205, 300, 100, n, s, k)
    return figure(1000, 320, d, "Seven rule types in two rows. Row rules: completeness, uniqueness, validity, referential. Table rules: freshness, volume, reconciliation.",
                  "Seven rule types, one question each. Which row a type sits in decides what blocking can mean for it.")


DRAWINGS = {"dq-scattered": drawing_dq_scattered, "dq-rule-card": drawing_dq_rule_card,
            "dq-engine-hop": drawing_dq_engine_hop, "dq-rule-types": drawing_dq_rule_types}
