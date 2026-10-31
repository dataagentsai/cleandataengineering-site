"""Drawings for 'Building agents on a moving ship'. Globals kit, figure, E, ROOT are injected."""


def _crate(x, y, w, h):
    """A small wooden crate: an outline with two slats."""
    return (f'<rect class="hz" x="{x}" y="{y}" width="{w}" height="{h}" rx="3"/>'
            f'<line class="ln" x1="{x}" y1="{y + h / 3}" x2="{x + w}" y2="{y + h / 3}"/>'
            f'<line class="ln" x1="{x}" y1="{y + 2 * h / 3}" x2="{x + w}" y2="{y + 2 * h / 3}"/>')


def _nails(x, y, w, h):
    return (f'<circle class="hk" cx="{x + 12}" cy="{y + h / 2}" r="3"/>'
            f'<circle class="hk" cx="{x + w - 12}" cy="{y + h / 2}" r="3"/>')


def drawing_ship_deck():
    b, t = kit.box, kit.text
    d = t(40, 34, "crates still slide about: strap them down", "sm")
    # crates on deck, tilted, with little motion marks
    crates = [("framework", 110, -7), ("memory", 330, 5), ("eval tool", 560, -4), ("model", 770, 8)]
    for name, x, rot in crates:
        cx, cy = x + 70, 122
        d += f'<g transform="rotate({rot} {cx} {cy})">' + b(x, 87, 140, 70, name, "", "bxm") + '</g>'
        d += (f'<line class="ln" x1="{x - 28}" y1="107" x2="{x - 10}" y2="107"/>'
              f'<line class="ln" x1="{x - 34}" y1="127" x2="{x - 12}" y2="127"/>')
    # the deck planks, nailed down
    planks = ["OpenTelemetry", "Postgres", "MCP", "JSON Schema", "OAuth"]
    for i, name in enumerate(planks):
        x = 84 + i * 168
        d += b(x, 188, 160, 44, name, "", "bx") + _nails(x, 188, 160, 44)
    # the hull
    d += '<path class="hz" d="M70,238 L930,238 L860,312 L140,312 Z"/>'
    d += '<circle class="hz" cx="250" cy="275" r="12"/><circle class="hz" cx="500" cy="275" r="12"/><circle class="hz" cx="750" cy="275" r="12"/>'
    # waves
    d += '<path class="ln" d="M20,326 Q60,312 100,326 T180,326 T260,326 T340,326 T420,326 T500,326 T580,326 T660,326 T740,326 T820,326 T900,326 T980,326"/>'
    d += t(500, 362, "the planks are nailed down: stand on them", "sm", "middle")
    return figure(1000, 380, d, "A cartoon ship on the waves. Its deck is five nailed planks: OpenTelemetry, Postgres, MCP, JSON Schema and OAuth. On top of the deck, four tilted dashed crates slide about: framework, memory, eval tool and model.",
                  "The agent stack as a ship. Stand on the planks that are nailed down; strap down the crates that still slide.")


def drawing_ship_columns():
    b, t = kit.box, kit.text
    d = t(250, 30, "NAILED DOWN (SETTLED)", "lbl", "middle")
    d += t(760, 30, "STILL SLIDING (MOVING)", "lbl", "middle")
    planks = [("OpenTelemetry", "how code reports traces", "bx"),
              ("Postgres", "state, checkpoints, vectors", "bx"),
              ("MCP", "tools; security parts still maturing", "bxs"),
              ("JSON Schema", "the shape of tool calls and replies", "bx"),
              ("OAuth and OpenID Connect", "who is asking, with whose rights", "bx"),
              ("Git and CI", "prompts and policy released as code", "bx"),
              ("Open table formats", "Delta or Iceberg: both open", "bxs")]
    for i, (name, sub, kind) in enumerate(planks):
        y = 50 + i * 66
        d += b(30, y, 440, 56, name, sub, kind) + _nails(30, y, 440, 56)
    crates = [("Frameworks and loops", "no clear winner"),
              ("Agent to agent (A2A)", "a young protocol"),
              ("Memory products", "what to keep is not agreed"),
              ("Eval tooling", "runners overlap and change"),
              ("Guardrail products", "screens improve every few months"),
              ("GenAI field names", "the trace names still get renamed"),
              ("Models and prices", "change several times a year")]
    for i, (name, sub) in enumerate(crates):
        y = 50 + i * 66
        x = 540 + (20 if i % 2 else 0)
        d += b(x, y, 410, 56, name, sub, "bxm")
    d += t(30, 528, "yellow: settled, with one edge still moving", "sm")
    return figure(1000, 545, d, "Two columns. On the left, seven nailed planks that have settled: OpenTelemetry, Postgres, MCP (its security parts still maturing), JSON Schema, OAuth and OpenID Connect, Git and CI, and open table formats (Delta or Iceberg). On the right, seven dashed crates still sliding: frameworks and loops, agent to agent, memory products, eval tooling, guardrail products, GenAI field names, and models and prices.",
                  "Our judgement as of October 2026. MCP and table formats are planks with one edge still moving.")


def drawing_ship_straps():
    b, t = kit.box, kit.text
    d = b(30, 115, 200, 100, "Your agent", ["talks only", "to the port"], "bx")
    d += kit.arrow(232, 165, 278, 165)
    d += b(280, 115, 180, 100, "Model port", ["one small", "interface"], "solid")
    adapters = ["Anthropic adapter", "OpenAI adapter", "Groq adapter"]
    for i, name in enumerate(adapters):
        y = 40 + i * 80
        d += b(560, y, 200, 50, name, "", "bxs" if i == 2 else "bx")
        d += f'<line class="{"lnc" if i == 2 else "lnd"}" x1="462" y1="165" x2="558" y2="{y + 25}"/>'
        # the product it straps down: a crate with a strap across it
        d += _crate(800, y + 2, 70, 46)
        d += f'<line class="lnc" x1="790" y1="{y + 25}" x2="880" y2="{y + 25}"/>'
        d += f'<line class="ln" x1="762" y1="{y + 25}" x2="788" y2="{y + 25}"/>'
    d += t(835, 25, "the products", "sm", "middle")
    d += b(560, 280, 320, 50, "Contract tests", "the same tests for every adapter", "bxs")
    d += t(370, 250, ["the thick strap is the", "one plugged in today"], "sm", "middle")
    return figure(1000, 345, d, "Your agent talks only to a lavender model port. Three straps run from the port to three adapters: Anthropic, OpenAI and Groq. Each adapter holds a strapped crate, the product. A thick strap marks the one plugged in today. Below the adapters, a yellow box: contract tests, the same tests for every adapter.",
                  "Ports and adapters as cargo straps. When a crate slides, you change one adapter and one line of config.")


def drawing_ship_rules():
    b, t = kit.box, kit.text
    d = ""
    # icons above each card: a nailed plank, a strapped crate, a rupee coin
    d += '<rect class="hz" x="130" y="30" width="100" height="22" rx="3"/><circle class="hk" cx="142" cy="41" r="3"/><circle class="hk" cx="218" cy="41" r="3"/>'
    d += _crate(465, 14, 70, 46) + '<line class="lnc" x1="455" y1="37" x2="545" y2="37"/>'
    d += '<circle class="hz" cx="820" cy="37" r="24"/>' + t(820, 45, "₹", "bd", "middle")
    cards = [("Boring standards", ["for the settled parts:", "use the plank directly,", "don't wrap it"]),
             ("Ports", ["for the moving parts:", "adapters and the same", "contract tests"]),
             ("Your own code", ["for anything that", "protects money: checks,", "budgets, cost per task"])]
    for i, (title, sub) in enumerate(cards):
        x = 30 + i * 320
        d += b(x, 80, 300, 170, title, sub, "solid" if i == 2 else "bx")
        d += kit.num(x + 22, 80, i + 1)
    return figure(1000, 265, d, "Three cards. One, with a nailed plank: boring standards for the settled parts; use the plank directly, don't wrap it. Two, with a strapped crate: ports for the moving parts, with adapters and the same contract tests. Three, with a rupee coin: your own code for anything that protects money: checks, budgets, cost per task.",
                  "Three rules for building on a moving ship.")


DRAWINGS = {
    "ship-deck": drawing_ship_deck,
    "ship-columns": drawing_ship_columns,
    "ship-straps": drawing_ship_straps,
    "ship-rules": drawing_ship_rules,
}
