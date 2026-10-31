"""Drawings for 'Agent-to-agent protocols (A2A): worth watching, not yet settled'.
kit, figure, E and ROOT are injected."""


def _embassy(x, y, flag="bxs"):
    """A small embassy building: roof, columns, door and a flag. x, y is the top-left of the walls."""
    w, h = 170, 130
    s = f'<line class="lnc" x1="{x + w / 2}" y1="{y - 50}" x2="{x + w / 2}" y2="{y - 95}"/>'
    s += f'<rect class="{flag}" x="{x + w / 2}" y="{y - 95}" width="34" height="20" rx="2"/>'
    s += f'<path class="hz" d="M{x - 12},{y} L{x + w / 2},{y - 50} L{x + w + 12},{y} Z"/>'
    s += f'<rect class="hz" x="{x}" y="{y}" width="{w}" height="{h}" rx="3"/>'
    for i in range(4):
        cx = x + 22 + i * 42
        if i in (1, 2):
            continue
        s += f'<line class="ln" x1="{cx}" y1="{y + 12}" x2="{cx}" y2="{y + h - 8}"/>'
    s += f'<rect class="hz" x="{x + w / 2 - 20}" y="{y + h - 52}" width="40" height="52" rx="18"/>'
    return s


def drawing_embassies():
    b, t, a, p = kit.box, kit.text, kit.arrow, kit.path
    d = _embassy(50, 110)
    d += _embassy(700, 110, "pf pf-solid")
    # notice board on a post beside the right embassy: the agent card
    d += '<line class="lnc" x1="935" y1="150" x2="935" y2="240"/>'
    d += '<rect class="hz" x="895" y="95" width="80" height="60" rx="4"/>'
    d += "".join(f'<line class="ln" x1="907" y1="{110 + j * 13}" x2="963" y2="{110 + j * 13}"/>' for j in range(3))
    d += t(935, 82, "agent card", "sm", "middle")
    # the sealed envelope in the middle
    d += '<rect class="hz" x="420" y="120" width="160" height="90" rx="4"/>'
    d += '<path class="ln" d="M420,120 L500,170 L580,120"/>'
    d += '<circle class="bxs" cx="500" cy="170" r="11"/>'
    d += t(500, 92, "the standard envelope", "bd", "middle")
    d += t(500, 236, "from, to, task ID, what is asked", "sm", "middle")
    d += a(232, 165, 412, 165)
    d += a(588, 165, 688, 165)
    d += p("M700,250 Q500,300 232,250", "lnd")
    d += t(500, 300, "replies and status updates, same task ID", "sm", "middle")
    d += b(25, 260, 220, 60, "Your agent", "Meera's shop", "bx")
    d += b(675, 260, 220, 60, "Their agent", "logistics partner", "solid")
    return figure(1000, 335, d,
                  "Two embassy buildings with flags. Your agent, at Meera's shop, on the left; their agent, at a logistics partner, on the right, with a notice board beside it labelled agent card. A sealed envelope travels between them, marked from, to, task ID and what is asked. A dashed arrow brings replies and status updates back with the same task ID.",
                  "An agent-to-agent protocol is a standard envelope. Neither embassy needs to know how the other works inside; the notice board says what it offers.")


def _toolbox(x, y, w=130, h=70):
    s = f'<path class="ln" d="M{x + w / 2 - 25},{y} L{x + w / 2 - 25},{y - 16} L{x + w / 2 + 25},{y - 16} L{x + w / 2 + 25},{y}"/>'
    s += f'<rect class="hz" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/>'
    s += f'<line class="ln" x1="{x}" y1="{y + 22}" x2="{x + w}" y2="{y + 22}"/>'
    s += f'<rect class="bxs" x="{x + w / 2 - 10}" y="{y + 15}" width="20" height="14" rx="2"/>'
    return s


def drawing_mcp_vs_a2a():
    b, t, a, p = kit.box, kit.text, kit.arrow, kit.path
    d = t(240, 30, "Agent to tool: MCP", "bd", "middle")
    d += t(240, 52, "it does exactly what it is told", "sm", "middle")
    d += b(20, 110, 150, 80, "Your agent", "in charge", "bx")
    d += a(172, 150, 290, 150)
    d += t(231, 132, "get order 4417", "sm", "middle")
    d += _toolbox(300, 118)
    d += t(365, 225, "Order tool", "tx", "middle")
    d += t(240, 280, ["one call, one answer,", "back in a moment"], "sm", "middle")
    d += '<line class="lnd" x1="495" y1="20" x2="495" y2="310"/>'
    d += t(755, 30, "Agent to agent: A2A", "bd", "middle")
    d += t(755, 52, "it decides how to do the work", "sm", "middle")
    d += b(520, 110, 150, 80, "Your agent", "hands over a goal", "bx")
    d += a(672, 140, 818, 140)
    d += t(745, 104, ["quote delivery", "by Friday"], "sm", "middle")
    d += p("M818,175 L672,175", "lnd")
    d += t(745, 200, "a question back?", "sm", "middle")
    d += b(825, 110, 160, 80, "Their agent", "plans its own steps", "solid")
    d += a(905, 192, 905, 218)
    d += _toolbox(860, 236, 90, 50)
    d += t(755, 280, ["may take minutes,", "uses its own tools"], "sm", "middle")
    return figure(1000, 320, d,
                  "Two halves. Left, agent to tool with MCP: your agent, in charge, sends get order 4417 to a toolbox labelled order tool; one call, one answer, back in a moment. Right, agent to agent with A2A: your agent hands a goal, quote delivery by Friday, to their agent, which plans its own steps and uses its own toolbox; a dashed arrow comes back with a possible question, and the work may take minutes.",
                  "MCP reaches a tool that does what it is told. A2A reaches another agent that decides how, and may use MCP for its own tools.")


def drawing_ticket():
    t = kit.text
    d = '<rect class="pf pf-bxs" x="128" y="26" width="760" height="356" rx="14"/>'
    d += '<rect class="hz" x="120" y="20" width="760" height="356" rx="14"/>'
    d += '<line class="lnd" x1="730" y1="34" x2="730" y2="362"/>'
    d += t(150, 58, "HAND-OFF TICKET", "lbl", "start")
    d += t(700, 58, "T-2291", "sm", "end")
    d += '<line class="ln" x1="140" y1="72" x2="710" y2="72"/>'
    rows = [("goal", "quote delivery for order 4417"),
            ("facts", "40 kg sofa, Pune to Nagpur"),
            ("limits", "customer pays up to ₹2,500"),
            ("deadline", "delivered by Friday"),
            ("depth", "hand-off 1 of at most 2"),
            ("fan-out", "may call at most 2 agents"),
            ("trace ID", "tr-8f31, same as the request"),
            ("on behalf of", "customer Ravi, quote only")]
    for i, (k, v) in enumerate(rows):
        y = 104 + i * 34
        d += t(150, y, k, "bd", "start")
        d += t(320, y, v, "tx", "start")
    # the stub: a tick box
    d += '<rect class="bxs" x="785" y="150" width="44" height="44" rx="6"/>'
    d += '<path class="lnc" d="M795,172 L805,184 L822,158"/>'
    d += t(807, 230, ["checked", "before it", "leaves"], "sm", "middle")
    return figure(1000, 395, d,
                  "A drawn hand-off ticket, number T-2291, with eight fields: goal, quote delivery for order 4417; facts, 40 kg sofa, Pune to Nagpur; limits, customer pays up to 2,500 rupees; deadline, delivered by Friday; depth, hand-off 1 of at most 2; fan-out, may call at most 2 agents; trace ID tr-8f31, same as the request; on behalf of customer Ravi, quote only. A torn-off stub has a ticked box: checked before it leaves.",
                  "A typed hand-off ticket. Every field is named and checked before it leaves, so nothing the receiver needs is lost in a summary.")


def drawing_port():
    b, t, a = kit.box, kit.text, kit.arrow
    d = b(25, 125, 190, 90, "Your agent", ["calls only", "the port"], "bx")
    d += a(217, 170, 273, 170)
    d += b(275, 125, 200, 90, "Hand-off port", ["hand this work", "to that agent"], "solid")
    d += b(580, 40, 230, 70, "In-process adapter", "today: a function call", "bx")
    d += b(580, 195, 230, 70, "A2A adapter", "later, when it settles", "bxm")
    d += '<line class="lnc" x1="477" y1="165" x2="578" y2="78"/>'
    d += '<line class="lnd" x1="477" y1="178" x2="578" y2="228"/>'
    d += a(812, 75, 843, 75)
    d += b(845, 40, 145, 70, "Same service", "our other agent", "bx")
    d += a(812, 230, 843, 230)
    d += b(845, 195, 145, 70, "Partner's agent", "another company", "bxm")
    d += t(500, 100, "plugged in", "sm", "end")
    d += b(200, 290, 600, 55, "The same for both adapters", "typed ticket, depth and fan-out limits, one trace, identity at each hop", "bxs")
    return figure(1000, 360, d,
                  "Your agent calls only a lavender hand-off port. A thick line plugs the port into an in-process adapter, today a function call, which reaches our other agent in the same service. A dashed line leads to an A2A adapter, for later when it settles, which would reach a partner's agent at another company. Below, a yellow strip: the same for both adapters, typed ticket, depth and fan-out limits, one trace, identity at each hop.",
                  "Stay ready without betting. Today the port uses a plain function call; when A2A settles, you add one adapter and change one line of config.")


DRAWINGS = {"a2a-embassies": drawing_embassies, "a2a-mcp-vs-a2a": drawing_mcp_vs_a2a,
            "a2a-ticket": drawing_ticket, "a2a-port": drawing_port}
