"""Drawings for 'The autonomous agent tech stack, one concern at a time'. Globals kit, figure, E, ROOT are injected."""


def drawing_stack_building():
    b, t = kit.box, kit.text
    # chimney first, so the roof covers its bottom
    d = '<rect class="hz" x="690" y="28" width="32" height="50" rx="3"/>'
    d += '<path class="hz" d="M40,88 L450,22 L860,88 Z"/>'
    d += t(450, 74, "an autonomous agent", "sm", "middle")
    d += '<rect class="hz" x="60" y="88" width="780" height="352" rx="6"/>'
    d += b(80, 100, 740, 66, "Experience: where people meet it", "a chat window, a copilot in an app, a coding agent, a background job", "bx")
    d += '<rect class="pf pf-solid" x="76" y="180" width="748" height="176" rx="12"/>'
    d += t(92, 203, "THE HARNESS: FIFTEEN CONCERNS, MOSTLY ORDINARY SOFTWARE", "lbl")
    rooms = [("One turn", ["the loop, the context,", "tools, the model door"]),
             ("Around every turn", ["guardrails, identity,", "state, memory, knowledge,", "a person, durable steps"]),
             ("Watch and change", ["tracing and cost,", "evals and release"])]
    for i, (title, sub) in enumerate(rooms):
        d += b(92 + i * 245, 218, 230, 122, title, sub, "solid")
    d += b(80, 370, 740, 58, "Models", "Claude, GPT, Gemini, Llama, Qwen, gpt-oss", "bxs")
    d += b(30, 452, 820, 60, "Foundation: data and compute", "your data and retrieval stores, chips, clusters, serving engines", "bx")
    # a small person outside, pointing at the top floor
    d += ('<circle class="bx" cx="930" cy="400" r="13"/><line class="lnc" x1="930" y1="413" x2="930" y2="450"/>'
          '<line class="lnc" x1="930" y1="450" x2="918" y2="472"/><line class="lnc" x1="930" y1="450" x2="942" y2="472"/>'
          '<line class="lnc" x1="930" y1="424" x2="900" y2="404"/><line class="lnc" x1="930" y1="424" x2="948" y2="438"/>')
    d += kit.path("M900,385 Q890,250 850,150")
    d += t(935, 495, ["people only", "see the", "top floor"], "sm", "middle")
    return figure(1000, 535, d, "A cartoon building. The top floor is experience: a chat window, a copilot, a coding agent, a background job. The middle floor is the harness with three rooms: one turn (the loop, the context, tools, the model door), around every turn (guardrails, identity, state, memory, knowledge, a person, durable steps) and watch and change (tracing, cost, evals, release). Below it is a floor of models, and the foundation is data and compute. A small person outside points at the top floor.",
                  "The whole stack as a building. The harness floor is the biggest, and it is where this post lives.")


def drawing_stack_swap():
    b, t = kit.box, kit.text
    d = t(210, 40, "THE JOB (CONCEPT)", "lbl", "middle")
    d += b(30, 70, 360, 150, "Model gateway", ["one governed door for every", "model call: keys, limits,", "logs and screening"], "solid")
    d += t(635, 24, "PRODUCTS THAT DO IT", "lbl", "middle")
    badges = [("LiteLLM", "open source"), ("Azure API Management", "Azure"),
              ("Bedrock + API Gateway", "AWS"), ("Portkey", "a vendor")]
    for i, (name, where) in enumerate(badges):
        y = 40 + i * 60
        d += b(520, y, 230, 46, name, "", "bxs" if i == 1 else "bx")
        d += t(765, y + 29, where, "sm")
        d += f'<line class="{"lnc" if i == 1 else "lnd"}" x1="392" y1="145" x2="518" y2="{y + 23}"/>'
    d += kit.path("M880,60 Q950,150 880,240") + kit.path("M880,240 Q810,150 880,60", "lnd")
    d += t(935, 155, "swap", "sm", "middle")
    d += t(210, 258, "the thick line is the one plugged in today", "sm", "middle")
    return figure(1000, 280, d, "A lavender card for the job, a model gateway: one governed door for every model call. Four product badges sit to its right: LiteLLM (open source), Azure API Management (Azure), Bedrock with API Gateway (AWS) and Portkey (a vendor). A thick line joins the card to the one plugged in today; dashed lines join the others. A curved arrow says swap.",
                  "Concept versus product. The card stays the same; the badge in the slot can change.")


def drawing_stack_bundle():
    b, t = kit.box, kit.text
    d = b(20, 40, 620, 200, [], (), "bxm")
    d += t(40, 72, "ONE PRODUCT NAME, MANY CONCERNS INSIDE", "lbl")
    for i, name in enumerate(["Loop", "Memory", "Identity", "Gateway", "Tracing"]):
        d += b(37 + i * 120, 110, 105, 70, name, "", "bx")
    d += t(330, 216, "an agent platform, for example", "sm", "middle")
    # a price tag hanging off the bundle
    d += '<path class="hz" d="M560,6 L620,6 L632,20 L620,34 L560,34 Z"/><circle class="hk" cx="620" cy="20" r="3"/>'
    d += '<line class="ln" x1="590" y1="34" x2="590" y2="40"/>' + t(588, 25, "one name", "sm", "middle")
    d += t(830, 24, "STILL YOURS", "lbl", "middle")
    for i, name in enumerate(["Checks that protect money", "Evals on your own cases", "Cost per business task"]):
        d += b(680, 38 + i * 70, 300, 55, name, "", "bxs")
    return figure(1000, 255, d, "A dashed bundle labelled one name holds five concern boxes: loop, memory, identity, gateway, tracing. To the right, three yellow boxes are still yours: checks that protect money, evals on your own cases, cost per business task.",
                  "A bundle fills several rows of the map at once. Ask which rows, and which ones are still yours.")


def drawing_stack_stairs():
    b, t = kit.box, kit.text
    d = b(40, 210, 290, 80, "First: one turn works", ["the loop, two or three tools,", "the model door, a trace"], "bx")
    d += b(345, 140, 290, 150, "Next: safe to use", ["guardrails, identity,", "state and memory,", "a cost budget"], "bxs")
    d += b(650, 60, 320, 230, "Then: it can change and wait", ["evals before every release,", "a person approves,", "steps that survive a crash,", "versioned release config"], "bx")
    d += ('<circle class="bx" cx="130" cy="160" r="13"/><line class="lnc" x1="130" y1="173" x2="130" y2="192"/>'
          '<line class="lnc" x1="130" y1="192" x2="120" y2="208"/><line class="lnc" x1="130" y1="192" x2="142" y2="208"/>'
          '<line class="lnc" x1="130" y1="180" x2="150" y2="168"/><line class="lnc" x1="130" y1="180" x2="114" y2="186"/>')
    d += '<line class="ln" x1="940" y1="58" x2="940" y2="10"/><path class="hz" d="M940,10 L978,20 L940,30 Z"/>'
    d += t(40, 40, ["fill the concerns in this order;", "each stair works on its own"], "sm")
    return figure(1000, 300, d, "Three stairs going up. First, one turn works: the loop, two or three tools, the model door, a trace. Next, safe to use: guardrails, identity, state and memory, a cost budget. Then it can change and wait: evals before every release, a person approves, steps that survive a crash, versioned release config. A small person stands on the first stair and a flag sits on the top one.",
                  "Which concerns to fill first. Knowledge and retrieval join whenever the job needs documents.")


DRAWINGS = {
    "stack-building": drawing_stack_building,
    "stack-swap": drawing_stack_swap,
    "stack-bundle": drawing_stack_bundle,
    "stack-stairs": drawing_stack_stairs,
}
