"""Drawings for 'AgentTwin vs LangWatch, Veris and friends: the simulation landscape'.
kit, figure, E and ROOT are given as globals by build.py."""


def _land_tick(x, y, s=1.0):
    return f'<path class="lnc" fill="none" d="M{x},{y} L{x + 9 * s},{y + 10 * s} L{x + 26 * s},{y - 11 * s}"/>'


def _land_wave(x, y):
    return f'<path class="ln" fill="none" d="M{x},{y} q8,-7 16,0 t16,0 t16,0"/>'


def _land_island(cx, cy, title, sub, names, star=False):
    rx, ry = 150, 62
    d = ""
    if star:
        d += f'<ellipse class="pf pf-solid" cx="{cx + 4}" cy="{cy + 4}" rx="{rx}" ry="{ry}"/>'
        d += f'<ellipse class="hz" cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill-opacity="0"/>'
    else:
        d += f'<ellipse class="pf pf-bxs" cx="{cx + 4}" cy="{cy + 4}" rx="{rx}" ry="{ry}"/>'
        d += f'<ellipse class="hz" cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill-opacity="0"/>'
    d += kit.text(cx, cy - 16, title, "bd", "middle")
    d += kit.text(cx, cy + 6, sub, "tx", "middle")
    d += kit.text(cx, cy + 28, names, "sm", "middle")
    return d


def drawing_land_map():
    t = kit.text
    d = t(500, 22, "each kind of tool lives on its own island; none of them covers the whole sea", "sm", "middle")
    for (x, y) in [(330, 60), (640, 210), (330, 215), (660, 62), (60, 200), (900, 205), (420, 395), (760, 410)]:
        d += _land_wave(x, y)
    d += _land_island(170, 110, "Conversation simulators", "plays: the customer", "LangWatch, Azure, Maxim, Coval")
    d += _land_island(500, 110, "Red-team kits", "plays: the attacker", "PyRIT, promptfoo, garak")
    d += _land_island(830, 110, "Tool simulators", "plays: the tools", "AWS Strands ToolSimulator")
    d += _land_island(170, 300, "Research worlds", "one fixed domain", "τ²-bench, AgentDojo, AppWorld")
    d += _land_island(500, 300, "AgentTwin (ours)", "the world, from your spec", "judges what changed", star=True)
    d += _land_island(830, 300, "Sandboxes (paid)", "the whole environment", "Veris, Collinear, Patronus")
    # a small boat with a stick person: the agent team choosing where to land
    d += '<path class="hz" d="M520,418 L640,418 L622,446 L538,446 Z"/>'
    d += '<line class="lnc" x1="580" y1="418" x2="580" y2="380"/>'
    d += '<path class="hz" d="M583,382 L612,410 L583,410 Z"/>'
    d += ('<circle class="hz" cx="552" cy="384" r="9"/><line class="lnc" x1="552" y1="393" x2="552" y2="414"/>'
          '<line class="lnc" x1="552" y1="400" x2="566" y2="392"/>')
    d += t(660, 440, "your team, choosing where to land", "sm", "start")
    return figure(1000, 460, d,
                  "A cartoon map of six islands in a sea. Conversation simulators play the customer (LangWatch, Azure, Maxim, Coval). Red-team kits play the attacker (PyRIT, promptfoo, garak). Tool simulators play the tools (AWS Strands ToolSimulator). Research worlds are one fixed domain (τ²-bench, AgentDojo, AppWorld). Sandboxes, which are paid, simulate the whole environment (Veris, Collinear, Patronus). AgentTwin, ours, builds the world from your spec and judges what changed. A small boat carries your team, choosing where to land.",
                  "The landscape as a map. Each kind of tool is good at one part of the world around an agent.")


def drawing_land_grid():
    t = kit.text
    cols = [("CUSTOMERS",), ("SYSTEMS",), ("FAULTS",), ("APPROVERS,", "CLOCK"), ("ATTACKERS",), ("JUDGES BY", "WORLD STATE")]
    xs = [300, 420, 540, 660, 780, 905]
    d = ""
    for x, c in zip(xs, cols):
        d += t(x, 30, list(c), "lbl", "middle")
    rows = [("AgentTwin (ours)", "pyyyyy"),
            ("LangWatch Scenario", "ynnn?p"),
            ("Strands ToolSimulator", "nypn??"),
            ("Veris", "yy?p??"),
            ("τ²-bench", "yy???y"),
            ("PyRIT", "nnnnyn")]
    for i, (name, marks) in enumerate(rows):
        y = 100 + i * 46
        if i == 0:
            d += '<rect class="pf pf-solid" x="14" y="80" width="972" height="40" rx="10"/>'
        d += t(30, y + 5, name, "bd" if i == 0 else "tx", "start")
        for x, m in zip(xs, marks):
            if m == "y":
                d += _land_tick(x - 13, y, 0.9)
            elif m == "p":
                d += t(x, y + 5, "partly", "sm", "middle")
            elif m == "n":
                d += f'<line class="ln" x1="{x - 10}" y1="{y}" x2="{x + 10}" y2="{y}"/>'
            else:
                d += t(x, y + 6, "?", "bd", "middle")
        d += f'<line class="lnd" x1="20" y1="{y + 23}" x2="980" y2="{y + 23}"/>'
    d += t(500, 392, "tick: the sources say yes   ·   partly: basic, or only through a model   ·   dash: no, or not its job   ·   ?: not stated", "sm", "middle")
    return figure(1000, 410, d,
                  "A grid. Rows: AgentTwin, LangWatch Scenario, Strands ToolSimulator, Veris, τ²-bench, PyRIT. Columns: customers, systems, faults, approvers and clock, attackers, judges by world state. AgentTwin: customers partly, everything else yes. LangWatch Scenario: customers yes, systems, faults and approvers no, attackers not stated, judging partly. Strands ToolSimulator: systems yes, faults partly, customers and approvers no, attackers and judging not stated. Veris: customers and systems yes, approvers partly, faults, attackers and judging not stated. τ²-bench: customers, systems and end-state checks yes, the rest not stated. PyRIT: attackers yes, everything else no.",
                  "Who covers what, from each tool's public documentation as of October 2026. A question mark means the source doesn't say, not that the tool can't.")


def drawing_land_pick():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(500, 22, "ask what you fear most; most agents answer yes more than once", "sm", "middle")
    qs = [("Is the worry how people talk?", "their own words, moods, voice"),
          ("Is the worry hidden attacks?", "planted notes, rewritten jailbreaks"),
          ("Does it change records by rules?", "refunds, renewals, payouts")]
    ans = [("A conversation simulator", ["LangWatch Scenario, Azure,", "Maxim, Coval"], "bx"),
           ("A red-team kit", ["PyRIT, promptfoo,", "Azure AI Red Teaming Agent"], "bx"),
           ("A world judged by state", ["AgentTwin: MCP agent, spec written", "Veris: any agent, managed, paid"], "solid")]
    for i, ((qt, qs_), (at, asub, kind)) in enumerate(zip(qs, ans)):
        y = 50 + i * 125
        d += kit.num(36, y + 45, i + 1)
        d += b(60, y, 360, 90, qt, qs_, "bxs")
        d += a(422, y + 45, 538, y + 45, "yes")
        d += b(540, y - 5, 430, 100, at, asub, kind)
        if i < 2:
            d += a(240, y + 92, 240, y + 123, "no", lx=262, ly=y + 112)
    d += t(500, 432, "yes to more than one? combine them: AgentTwin itself borrows LangWatch for customers and PyRIT for attacks", "sm", "middle")
    return figure(1000, 450, d,
                  "Three questions in a column, each with a yes arrow to a kind of tool. 1: is the worry how people talk, in their own words, moods or voice? Then a conversation simulator such as LangWatch Scenario, Azure, Maxim or Coval. 2: is the worry hidden attacks? Then a red-team kit such as PyRIT, promptfoo or the Azure AI Red Teaming Agent. 3: does the agent change records by rules, such as refunds, renewals and payouts? Then a world judged by state: AgentTwin for an MCP agent whose spec is written, or Veris for any agent, managed and paid. A note says to combine them if you answer yes more than once.",
                  "Which one for your agent. Start from the risk, not the demo.")


DRAWINGS = {
    "land-map": drawing_land_map,
    "land-grid": drawing_land_grid,
    "land-pick": drawing_land_pick,
}
