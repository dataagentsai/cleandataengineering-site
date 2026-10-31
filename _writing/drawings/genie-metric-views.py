"""Drawings for 'Talk to your data the right way: Genie and metric views on Databricks'.
kit, figure, E and ROOT arrive as globals from build.py."""


def _person(cx, top):
    """A small stick person; top is the y of the head's centre."""
    return (f'<circle class="bx" cx="{cx}" cy="{top}" r="13"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 13}" x2="{cx}" y2="{top + 42}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 42}" x2="{cx - 11}" y2="{top + 62}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 42}" x2="{cx + 11}" y2="{top + 62}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 22}" x2="{cx - 18}" y2="{top + 10}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 22}" x2="{cx + 18}" y2="{top + 10}"/>')


def drawing_genie_two_revenues():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(500, 22, "same question, \"revenue last quarter?\", three answers", "sm", "middle")
    tools = [(20, "Finance dashboard", "₹4.2 crore", "bx"), (365, "Sales dashboard", "₹4.6 crore", "bx"),
             (710, "The chatbot", "₹5.1 crore", "bxm")]
    notes = ["its own SQL: after refunds", "its own SQL: before refunds", "SQL it guessed just now"]
    for i, (x, title, sub, k) in enumerate(tools):
        d += b(x, 45, 270, 90, title, sub, k)
        d += t(x + 135, 165, notes[i], "sm", "middle")
        d += a(x + 135, 178, 500 + (i - 1) * 120, 268)
    d += b(300, 270, 400, 80, "The same tables", "orders, refunds, stores", "bxs")
    # a confused manager on the left, with question marks
    d += _person(115, 255) + t(158, 262, "?", "bd", "start") + t(172, 248, "?", "bd", "start")
    d += t(115, 342, "which one is right?", "sm", "middle")
    d += t(850, 300, ["nobody is wrong;", "each wrote its own", "meaning of \"revenue\""], "sm", "middle")
    return figure(1000, 365, d,
                  "Two dashboards and a chatbot each write their own SQL against the same tables and report three different revenue numbers: 4.2, 4.6 and 5.1 crore rupees. A confused person asks which one is right.",
                  "The \"two revenues\" problem, now with a third voice. Every tool carries its own copy of the meaning.")


def drawing_genie_layers():
    b, a, t = kit.box, kit.arrow, kit.text
    d = ""
    tops = [(20, "Genie space", "people ask in English", "bxs"), (355, "AI/BI dashboards", "charts people check", "bx"),
            (690, "SQL, notebooks, apps", "anyone who queries", "bxm")]
    for x, title, sub, k in tops:
        d += b(x, 20, 290, 80, title, sub, k)
        d += a(x + 145, 102, 500 + (x - 355) * 0.45, 158)
    d += b(150, 160, 700, 100, "Metric views in Unity Catalog", ["one definition per number: net revenue, active customers,", "how tables join, which filters apply"], "solid")
    d += a(500, 262, 500, 298)
    d += b(250, 300, 500, 80, "Gold tables", "facts and dimensions, at the finest grain", "bx")
    d += a(500, 382, 500, 413)
    d += b(320, 415, 360, 70, "Silver and bronze", "readers never come down here", "bxm")
    d += t(60, 210, ["the meaning", "lives here,", "once"], "sm", "middle")
    return figure(1000, 500, d,
                  "Layers from the bottom up: silver and bronze, then gold tables, then metric views in Unity Catalog holding one definition per number. Three readers sit on top of the metric views: a Genie space, AI/BI dashboards, and SQL, notebooks and apps.",
                  "One definition in the middle. Chat, dashboards and code all read the same metric view, so they all give the same number.")


def drawing_genie_one_question():
    b, a, t, n, p = kit.box, kit.arrow, kit.text, kit.num, kit.path
    steps = [(10, "The question", ["\"net revenue by state,", "last quarter?\""], "bxm"),
             (265, "Genie picks", ["measure: net revenue", "by: state", "when: last quarter"], "solid"),
             (520, "A small query", ["over the metric view,", "MEASURE(net_revenue)", "no joins, no formula"], "bx"),
             (775, "The answer", ["the table, the SQL,", "and what net revenue", "means, shown"], "bxs")]
    d = ""
    for i, (x, title, sub, k) in enumerate(steps):
        d += b(x, 70, 215, 130, title, sub, k) + n(x + 14, 70, i + 1)
        if i < 3:
            d += a(x + 217, 135, x + 263, 135)
    d += t(500, 30, "the model chooses from a menu; the metric view does the maths", "sm", "middle")
    d += p("M882,202 Q640,300 372,202", "lnd")
    d += t(627, 292, "a wrong answer? the person marks it, and it joins your test questions", "sm", "middle")
    return figure(1000, 310, d,
                  "Four numbered steps: a person asks for net revenue by state last quarter; Genie picks the measure, the dimension and the time filter; a small query runs over the metric view using MEASURE(net_revenue) with no joins or formula; the answer shows the table, the SQL and the definition. A dashed line loops back from the answer: a wrong answer becomes a test question.",
                  "One question, start to finish. The hard parts, the formula and the joins, were decided long before anyone asked.")


def drawing_genie_checklist():
    t = kit.text
    # a clipboard
    d = ('<rect class="hz" x="250" y="40" width="500" height="350" rx="14"/>'
         '<rect class="pf pf-bxs" x="420" y="26" width="160" height="34" rx="8"/>'
         '<rect class="hz" x="420" y="26" width="160" height="34" rx="8" style="fill:none"/>')
    items = ["metric views over gold, each with an owner", "one space per team, a few views only",
             "instructions: your words, your rules", "example SQL for the questions you trust",
             "benchmark questions with checked answers", "a dashboard on the same metric views"]
    for i, item in enumerate(items):
        y = 100 + i * 55
        d += f'<rect class="hz" x="290" y="{y - 18}" width="24" height="24" rx="4"/>'
        d += (f'<path class="lnc" d="M294,{y - 6} L301,{y + 2} L312,{y - 16}"/>')
        d += t(332, y, item, "tx", "start")
    d += _person(860, 170) + t(860, 270, ["tick all six,", "then invite users"], "sm", "middle")
    d += t(120, 200, ["before day one,", "not after the", "first wrong number"], "sm", "middle")
    return figure(1000, 410, d,
                  "A clipboard with six ticked boxes: metric views over gold, each with an owner; one space per team with a few views; instructions in your words; example SQL for trusted questions; benchmark questions with checked answers; a dashboard on the same metric views. A stick person stands beside it.",
                  "What to set up before you open a Genie space to real users.")


DRAWINGS = {"genie-two-revenues": drawing_genie_two_revenues, "genie-layers": drawing_genie_layers,
            "genie-one-question": drawing_genie_one_question, "genie-checklist": drawing_genie_checklist}
