"""Drawings for 'What a forward-deployed engineer actually does'. Globals kit, figure, E, ROOT are injected."""


def _person(cx, top):
    """A stick person whose head centre is at (cx, top)."""
    return (f'<circle class="bx" cx="{cx}" cy="{top}" r="13"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 13}" x2="{cx}" y2="{top + 45}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 45}" x2="{cx - 11}" y2="{top + 68}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 45}" x2="{cx + 12}" y2="{top + 68}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 24}" x2="{cx + 18}" y2="{top + 36}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 24}" x2="{cx - 16}" y2="{top + 36}"/>')


def drawing_fde_backpack():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(500, 24, "the bag carries what travels well; the customer's world is already in the office", "sm", "middle")
    # the engineer with a backpack, walking right
    d += _person(150, 130)
    d += '<rect class="hz" x="104" y="146" width="32" height="44" rx="8"/>'
    d += '<line class="ln" x1="120" y1="146" x2="148" y2="150"/>'
    d += t(150, 232, "the FDE", "bd", "middle")
    d += b(30, 250, 250, 85, "In the bag", ["the product, tools,", "build-test-measure habits"], "bx")
    d += a(205, 175, 365, 175, "walks in", lx=285, ly=165)
    # the customer's office: a building outline
    d += '<path class="hz" d="M380,90 L970,90 L970,345 L380,345 Z"/>'
    d += '<path class="ln" d="M380,90 L675,38 L970,90"/>'
    d += t(675, 80, "THE CUSTOMER'S OFFICE", "lbl", "middle")
    d += b(400, 105, 270, 70, "Their data", "three systems that disagree", "bxs")
    d += b(685, 105, 265, 70, "Their rules", "who may see what", "bxs")
    d += b(400, 190, 270, 70, "Their people", "the real problem, in words", "bxs")
    d += b(685, 190, 265, 70, "Their cloud", "nothing leaves it", "bxs")
    d += b(510, 275, 330, 58, "The job", "join the bag to this world", "solid")
    return figure(1000, 360, d,
                  "A stick person with a backpack holding the product, tools and habits walks into a customer's office. Inside are their data, their rules, their people and their cloud. In the middle is the job: join the bag to this world.",
                  "An FDE brings the product and the habits. Everything that makes it hard is already in the customer's office.")


def drawing_fde_path():
    b, t, p = kit.box, kit.text, kit.path
    d = t(500, 22, "one path, six milestones; each stop answers a question before the next", "sm", "middle")
    d += p("M60,135 Q250,60 440,135 T820,135 Q930,170 880,260 Q760,330 500,300 Q260,280 120,300", "lnd")
    stops = [(25, 70, "1 Discovery", ["problem, data,", "rules"], "bx"),
             (355, 95, "2 Scope", ["what code can do", "without a model"], "bxs"),
             (690, 70, "3 Prototype", ["one slice, real", "data, end to end"], "bx"),
             (810, 200, "4 Deploy", ["in their cloud,", "their sign-in"], "bx"),
             (430, 240, "5 Prove", ["eval score and", "cost per task"], "bxs"),
             (40, 240, "6 Hand over", ["runbook, note,", "their own team"], "solid")]
    for x, y, title, sub, k in stops:
        d += b(x, y, 170, 80, title, sub, k)
    # a small flag at the finish
    d += '<line class="lnc" x1="60" y1="236" x2="60" y2="196"/><path class="hz" d="M60,196 L88,204 L60,214 Z"/>'
    return figure(1000, 340, d,
                  "A winding dashed path with six milestones: discovery of problem, data and rules; a scope of what code can do without a model; a prototype on one slice of real data; deploy in their cloud; prove with an eval score and cost per task; hand over with a runbook to their own team. A flag marks hand over.",
                  "The six-step journey. The finish line is not the demo; it is the customer running it without you.")


def drawing_fde_skills():
    b, t = kit.box, kit.text
    d = t(500, 22, "a T-shape: one deep skill, three wide ones across the top", "sm", "middle")
    # top bar of the T: three wide skills
    d += b(120, 45, 245, 90, "Listening", ["hear the problem", "inside the request"], "bxs")
    d += b(380, 45, 245, 90, "Writing", ["scope, notes,", "runbook, updates"], "bxs")
    d += b(640, 45, 245, 90, "Judgement", ["what not to build,", "what to say early"], "bxs")
    # the stem: engineering
    d += b(380, 150, 245, 170, "Engineering", ["build, debug and", "deploy in someone", "else's environment"], "solid")
    d += t(250, 220, ["the stem gets you", "in the door"], "sm", "middle")
    d += t(760, 220, ["the bar makes it", "work for them"], "sm", "middle")
    return figure(1000, 335, d,
                  "A T-shape. The stem is engineering: build, debug and deploy in someone else's environment. The top bar has three skills: listening, writing and judgement.",
                  "Engineering is the stem. Listening, writing and judgement are what turn it into the FDE job.")


def drawing_fde_roles():
    b, t = kit.box, kit.text
    d = t(500, 22, "same customer, three different centres of gravity", "sm", "middle")
    panels = [(20, "Consultant", "advises", ["leaves with", "a report"], "bxm"),
              (350, "Product engineer", "builds for everyone", ["rarely meets one", "customer"], "bx"),
              (680, "FDE", "builds for this one", ["stays until it", "works, hands over"], "solid")]
    for x, name, verb, sub, k in panels:
        d += f'<rect class="hz" x="{x}" y="45" width="300" height="270" rx="10"/>'
        d += t(x + 150, 72, name.upper(), "lbl", "middle")
        cx = x + 150
        if name == "Consultant":
            d += _person(cx - 60, 100)
            d += f'<rect class="hz" x="{cx}" y="105" width="44" height="56" rx="3"/>'
            d += "".join(f'<line class="ln" x1="{cx + 8}" y1="{117 + j * 12}" x2="{cx + 36}" y2="{117 + j * 12}"/>' for j in range(3))
        elif name == "Product engineer":
            d += _person(cx - 70, 100)
            d += f'<rect class="hz" x="{cx - 20}" y="105" width="90" height="60" rx="4"/>'
            d += f'<line class="ln" x1="{cx + 25}" y1="165" x2="{cx + 25}" y2="178"/>'
            d += f'<line class="ln" x1="{cx}" y1="178" x2="{cx + 50}" y2="178"/>'
        else:
            d += _person(cx - 50, 100)
            d += _person(cx + 50, 100)
            d += f'<rect class="hz" x="{cx - 20}" y="150" width="40" height="22" rx="3"/>'
        d += b(x + 20, 195, 260, 105, verb, sub, k)
    return figure(1000, 330, d,
                  "Three panels. A consultant beside a report: advises and leaves with a report. A product engineer at a screen: builds for everyone and rarely meets one customer. An FDE next to a customer person: builds for this one, stays until it works and hands over.",
                  "Consultant, product engineer, FDE. The solutions engineer sits between the first two, before the sale.")


DRAWINGS = {"fde-backpack": drawing_fde_backpack, "fde-path": drawing_fde_path,
            "fde-skills": drawing_fde_skills, "fde-roles": drawing_fde_roles}
