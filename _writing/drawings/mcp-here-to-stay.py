"""Drawings for 'MCP is here to stay: give your agent tools the standard way'.
kit, figure, E and ROOT are injected."""


def _plug(x, y, shape):
    """A small plug head at (x, y), pointing right; shape picks the tip."""
    s = f'<rect class="hz" x="{x}" y="{y - 14}" width="44" height="28" rx="5"/>'
    if shape == "pins":
        s += (f'<rect class="hk" x="{x + 44}" y="{y - 9}" width="12" height="5"/>'
              f'<rect class="hk" x="{x + 44}" y="{y + 4}" width="12" height="5"/>')
    elif shape == "round":
        s += f'<circle class="hz" cx="{x + 52}" cy="{y}" r="8"/>'
    elif shape == "wide":
        s += f'<rect class="hz" x="{x + 44}" y="{y - 11}" width="16" height="22" rx="2"/>'
    elif shape == "tri":
        s += f'<path class="hz" d="M{x + 44},{y - 10} L{x + 60},{y} L{x + 44},{y + 10} Z"/>'
    else:  # usb-c style
        s += f'<rect class="hz" x="{x + 44}" y="{y - 6}" width="16" height="12" rx="6"/>'
    return s


def drawing_mcp_usb():
    t, b = kit.text, kit.box
    d = ""
    # left half: tangle of cables
    d += t(250, 30, "Before: glue for every pair", "bd", "middle")
    d += t(250, 52, "each agent wired to each tool its own way", "sm", "middle")
    agents = [("Support agent", 90), ("Coding assistant", 175), ("Chat app", 260)]
    tools = [("Orders", 90, "pins"), ("Claims", 175, "round"), ("Files", 260, "tri")]
    for name, y in agents:
        d += b(20, y - 25, 150, 50, name, (), "bx")
    for name, y, _ in tools:
        d += b(370, y - 25, 110, 50, name, (), "bxm")
    # tangled wires
    for _, ya in agents:
        for _, yt, _ in tools:
            d += f'<path class="lnd" d="M172,{ya} C240,{ya + (yt - ya) * 0.2 - 30} 300,{yt + 30} 368,{yt}"/>'
    d += t(270, 312, "3 agents x 3 tools = 9 pieces of glue", "sm", "middle")
    # divider
    d += '<line class="lnd" x1="505" y1="20" x2="505" y2="320"/>'
    # right half: one port shape
    d += t(755, 30, "After: one plug shape", "bd", "middle")
    d += t(755, 52, "every agent and every tool speaks MCP", "sm", "middle")
    for name, y in agents:
        d += b(530, y - 25, 150, 50, name, (), "bx")
        d += _plug(683, y, "c")
    d += b(765, 65, 34, 220, "", (), "solid")
    d += t(782, 300, "MCP", "lbl", "middle")
    for name, y, _ in tools:
        d += f'<line class="lnc" x1="801" y1="{y}" x2="852" y2="{y}"/>'
        d += b(855, y - 25, 125, 50, name, (), "bxm")
    d += t(755, 330, "each side writes its plug once", "sm", "middle")
    return figure(1000, 345, d,
                  "Two halves. Left: three agents, a support agent, a coding assistant and a chat app, each wired by a different tangled cable to three tools, orders, claims and files: nine pieces of glue. Right: the same three agents each with the same small plug, all fitting one MCP strip, which connects once to each tool.",
                  "Like USB-C for agents. Before, every agent needed its own cable to every tool. With MCP, each agent has one client and each tool has one server.")


def drawing_mcp_handshake():
    b, t, n = kit.box, kit.text, kit.num
    d = ""
    d += b(30, 40, 200, 300, "The agent", ["MCP client,", "inside the harness"], "bx")
    d += b(770, 40, 200, 300, "Order server", ["MCP server,", "in front of the", "order system"], "solid")
    rows = [
        (1, "initialize", '"Hello, which version do you speak?"', '"This one. I have tools."', 85),
        (2, "tools/list", '"What can you do?"', '"get_order, cancel_order, ..."', 175),
        (3, "tools/call", '"Run get_order, id ORD-1042"', '"Status: shipped"', 265),
    ]
    for num, name, ask, reply, y in rows:
        d += n(268, y - 12, num)
        d += t(290, y - 6, name, "lbl")
        d += kit.arrow(240, y + 8, 760, y + 8)
        d += t(500, y, ask, "tx", "middle")
        d += kit.path(f"M760,{y + 30} L240,{y + 30}", "lnd")
        d += t(500, y + 50, reply, "sm", "middle")
    d += t(500, 372, "JSON-RPC notes, over stdio on one machine or Streamable HTTP across a network", "sm", "middle")
    return figure(1000, 390, d,
                  "The agent on the left and the order server on the right exchange three question and answer pairs. One, initialize: which version do you speak? This one, I have tools. Two, tools/list: what can you do? get_order, cancel_order and so on. Three, tools/call: run get_order for ORD-1042. Status: shipped.",
                  "The whole MCP conversation is three questions. Solid arrows are questions, dashed arrows are answers, and the labels are the real message names.")


def drawing_mcp_rules_server():
    b, t, a = kit.box, kit.text, kit.arrow
    d = ""
    # the model with a speech bubble
    d += b(20, 95, 170, 90, "The model", ["asks for", "cancel_order"], "bx")
    d += a(192, 140, 247, 140)
    d += b(250, 95, 170, 90, "The harness", ["makes the call,", "with Rohan's token"], "bx")
    d += a(422, 140, 477, 140)
    # the server, big, with its checks inside
    d += '<rect class="pf pf-solid" x="480" y="30" width="500" height="250" rx="16"/>'
    d += t(500, 58, "Order server: the rules live here", "bd")
    d += b(500, 75, 220, 75, "Token checked", ["is this Rohan?", "scope allows it?"], "bxs")
    d += b(740, 75, 220, 75, "His order?", ["owner comes from", "the token, not args"], "bxs")
    d += b(500, 170, 220, 75, "Rule in code", ["only before the", "order is picked"], "bxs")
    d += b(740, 170, 220, 75, "Then it acts", ["order cancelled,", "result returned"], "solid")
    d += a(722, 112, 738, 112)
    d += kit.path("M800,152 Q720,158 680,167", "ln")
    d += a(722, 207, 738, 207)
    # the prompt note, crossed
    d += '<path class="hz" d="M40,225 L250,225 L250,290 L40,290 Z"/>'
    d += t(145, 250, '"Only cancel before', "sm", "middle")
    d += t(145, 268, 'the order is picked"', "sm", "middle")
    d += '<rect class="zr" x="270" y="238" width="150" height="40" rx="8"/>'
    d += t(345, 263, "not a rule", "bd", "middle")
    d += t(145, 315, "in the prompt: a request, not a rule", "sm", "middle")
    return figure(1000, 330, d,
                  "The model asks for cancel_order; the harness makes the call with Rohan's token; inside the order server four checks run in turn: the token is checked, the order must be his, a rule in code allows cancelling only before the order is picked, and only then does it act. Below left, a prompt note saying the same rule is crossed out.",
                  "Where the business rules live. The server checks who is asking and applies the rule in its own code. The same sentence in a prompt is only a request.")


def drawing_mcp_shield():
    t = kit.text
    d = ""
    cx = 500
    d += (f'<path class="pf pf-bx" d="M{cx},28 L{cx + 150},68 L{cx + 140},210 '
          f'Q{cx + 110},285 {cx},320 Q{cx - 110},285 {cx - 140},210 L{cx - 150},68 Z"/>')
    d += f'<path class="ln" d="M{cx},28 L{cx + 150},68 L{cx + 140},210 Q{cx + 110},285 {cx},320 Q{cx - 110},285 {cx - 140},210 L{cx - 150},68 Z"/>'
    d += t(cx, 150, "Your MCP", "bd", "middle")
    d += t(cx, 174, "server", "bd", "middle")
    d += t(cx, 200, "a door into", "sm", "middle")
    d += t(cx, 218, "real data", "sm", "middle")
    items = [
        (1, 30, 45, "Sign-in", ["OAuth for remote servers,", "token checked every call"], "bx"),
        (2, 30, 160, "Least privilege", ["show only tools this", "user's token allows"], "bx"),
        (3, 680, 45, "Untrusted text", ["descriptions and results", "can carry injection"], "bxs"),
        (4, 680, 160, "Pinned versions", ["serve the exact", "version you tested"], "bxs"),
        (5, 355, 335, "Who sees what", ["no sensitive data to a", "server you don't trust"], "bxm"),
    ]
    for num, x, y, title, sub, kind in items:
        d += kit.box(x, y, 290, 90, title, sub, kind) + kit.num(x + 12, y, num)
    d += kit.path("M322,90 Q350,100 362,110", "lnd")
    d += kit.path("M322,205 Q345,200 360,195", "lnd")
    d += kit.path("M678,90 Q650,100 638,110", "lnd")
    d += kit.path("M678,205 Q655,200 640,195", "lnd")
    return figure(1000, 440, d,
                  "A shield labelled your MCP server, a door into real data, surrounded by five numbered boxes: one, sign-in with OAuth and a token checked every call; two, least privilege, showing only the tools the user's token allows; three, untrusted text, since descriptions and results can carry injection; four, pinned versions; five, no sensitive data to a server you don't trust.",
                  "Five things to secure before you plug a server in. Most of them are ordinary security; number three is the one that is new with agents.")


DRAWINGS = {
    "mcp-usb": drawing_mcp_usb,
    "mcp-handshake": drawing_mcp_handshake,
    "mcp-rules-server": drawing_mcp_rules_server,
    "mcp-shield": drawing_mcp_shield,
}
