"""Drawings for 'From data engineer to AI engineer: the 6-month switch'. Globals kit, figure, E, ROOT are injected."""


def drawing_switch_backpack():
    b, t = kit.box, kit.text
    d = t(500, 26, "you are not starting from zero: most of an agent is software and data plumbing", "sm", "middle")
    # the backpack
    d += '<rect class="hz" x="400" y="80" width="200" height="230" rx="40"/>'
    d += '<path class="ln" d="M445,80 Q445,45 500,45 Q555,45 555,80"/>'
    d += '<rect class="hz" x="430" y="200" width="140" height="80" rx="14"/>'
    d += '<line class="ln" x1="430" y1="225" x2="570" y2="225"/>'
    d += t(500, 150, "what you", "bd", "middle") + t(500, 172, "already carry", "bd", "middle")
    tags = [(20, 60, "Pipelines", "steps in order", "bx"), (20, 155, "Idempotency", "re-run, no duplicates", "bx"),
            (20, 250, "Data quality", "checks that block bad data", "bxs"),
            (660, 60, "Contracts", "agreed shape of data", "bx"), (660, 155, "SQL and cloud", "query it, host it", "bx"),
            (660, 250, "Cost and tests", "know the bill, prove it works", "bxs")]
    for x, y, title, sub, k in tags:
        d += b(x, y, 320 if x > 400 else 320, 76, title, sub, k)
    for y in (98, 193, 288):
        d += f'<line class="lnd" x1="342" y1="{y}" x2="400" y2="{min(max(y, 120), 280)}"/>'
        d += f'<line class="lnd" x1="658" y1="{y}" x2="600" y2="{min(max(y, 120), 280)}"/>'
    return figure(1000, 345, d, "A backpack in the middle labelled what you already carry, with six tags around it: pipelines, idempotency, data quality, contracts, SQL and cloud, cost and tests.",
                  "The backpack a data engineer brings. Every tag here is a job inside a working agent.")


def drawing_switch_map():
    b, a, t = kit.box, kit.arrow, kit.text
    rows = [("Orchestration", "The agent loop", "steps, retries, budgets"),
            ("Idempotency", "Safe tools", "a retry never pays twice"),
            ("Data contracts", "Structured output", "ask for JSON, validate it"),
            ("Data quality tests", "Evals", "a test set before release"),
            ("Cost dashboards", "A token meter", "cost per question")]
    d = t(180, 26, "YOU KNOW THIS", "lbl", "middle") + t(720, 26, "IT BECOMES THIS IN AN AGENT", "lbl", "middle")
    for i, (left, right, sub) in enumerate(rows):
        y = 45 + i * 78
        d += b(40, y, 280, 62, left, "", "bx")
        d += a(322, y + 31, 478, y + 31)
        d += b(480, y, 480, 62, right, sub, "solid" if i == 3 else "bxs")
    return figure(1000, 440, d, "Five rows. Orchestration becomes the agent loop. Idempotency becomes safe tools. Data contracts become structured output. Data quality tests become evals. Cost dashboards become a token meter.",
                  "Same idea, new name. The new words hide old skills.")


def drawing_switch_bridge():
    t = kit.text
    d = t(500, 24, "one plank a month; you can stand on each plank before laying the next", "sm", "middle")
    # two banks
    d += '<path class="pf pf-bx" d="M0,150 L150,150 Q170,230 160,300 L0,300 Z"/>'
    d += '<path class="pf pf-solid" d="M1000,150 L850,150 Q830,230 840,300 L1000,300 Z"/>'
    d += t(75, 185, ["Data", "engineer"], "bd", "middle") + t(925, 185, ["AI", "engineer"], "bd", "middle")
    # water
    for y in (268, 292):
        d += f'<path class="ln" d="M180,{y} Q230,{y - 10} 280,{y} T380,{y} T480,{y} T580,{y} T680,{y} T780,{y} T820,{y}"/>'
    # handrail rope
    d += '<path class="ln" d="M150,95 Q500,155 850,95"/>'
    planks = ["LLM basics", "Tools, loop", "Context, RAG", "Evals", "Guardrails", "Trace, ship"]
    for i, name in enumerate(planks):
        x = 160 + i * 115
        cx = x + 52
        f = 1 - ((cx - 500) / 350) ** 2
        y = 150 + 25 * f
        rope = 95 + 30 * (1 - ((cx - 500) / 350) ** 2) * 1.0
        d += f'<line class="lnd" x1="{cx}" y1="{rope:.0f}" x2="{cx}" y2="{y:.0f}"/>'
        d += kit.box(x, y, 105, 62, f"Month {i + 1}", name, "bxs" if i == 3 else "bx")
    # stick person on the left bank
    d += ('<circle class="bx" cx="120" cy="104" r="12"/><line class="lnc" x1="120" y1="116" x2="120" y2="134"/>'
          '<line class="lnc" x1="120" y1="134" x2="111" y2="149"/><line class="lnc" x1="120" y1="134" x2="130" y2="149"/>'
          '<line class="lnc" x1="120" y1="122" x2="138" y2="114"/><line class="lnc" x1="120" y1="122" x2="104" y2="128"/>')
    return figure(1000, 310, d, "A rope bridge from the data engineer bank to the AI engineer bank, with six planks: month 1 LLM basics, month 2 tools and the loop, month 3 context and RAG, month 4 evals, month 5 guardrails, month 6 tracing and shipping. A small person stands on the left bank.",
                  "Six planks, one a month. Month 4, evals, is the plank people most often skip.")


def drawing_switch_project():
    b, a, t, p = kit.box, kit.arrow, kit.text, kit.path
    d = b(10, 120, 150, 80, "A question", "\"sales in Pune?\"", "bxm")
    d += a(162, 160, 193, 160)
    d += b(195, 105, 190, 110, "The agent", ["model plus", "harness"], "solid")
    d += a(387, 160, 438, 160, "asks", lx=412, ly=150)
    d += b(440, 105, 200, 110, "Semantic layer", ["defined metrics,", "no raw SQL"], "bxs")
    d += a(642, 160, 693, 160)
    d += b(695, 105, 170, 110, "Lakehouse", ["gold tables", "you built"], "bx")
    d += b(110, 255, 230, 70, "Evals", "golden questions", "bxs")
    d += b(400, 255, 230, 70, "Cost meter", "₹ per question", "bxs")
    d += b(690, 255, 230, 70, "Traces", "every step written", "bxs")
    d += '<line class="ln" x1="290" y1="217" x2="290" y2="236"/><line class="ln" x1="225" y1="236" x2="805" y2="236"/>'
    d += a(225, 236, 225, 253) + a(515, 236, 515, 253) + a(805, 236, 805, 253)
    d += p("M290,103 Q290,30 100,118") + t(205, 36, "answer with the number and where it came from", "sm", "middle")
    return figure(1000, 340, d, "A question goes to the agent, which asks a semantic layer of defined metrics, which reads lakehouse gold tables. Under the agent sit three proof boxes: evals with golden questions, a cost meter in rupees per question, and traces of every step.",
                  "One portfolio project. Your data skills build the right half; the left half and the three proof boxes are what you learn.")


DRAWINGS = {"switch-backpack": drawing_switch_backpack, "switch-map": drawing_switch_map,
            "switch-bridge": drawing_switch_bridge, "switch-project": drawing_switch_project}
