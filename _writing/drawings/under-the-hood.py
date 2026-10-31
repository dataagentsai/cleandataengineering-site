"""Drawings for 'Under the hood'. Globals kit, figure, E, ROOT are injected."""


def drawing_uh_iceberg():
    b, t = kit.box, kit.text
    d = t(500, 22, "what you type is the tip; what you pay for is underneath", "sm", "middle")
    d += '<path class="hz" d="M400,120 L450,55 L550,55 L600,120 Z"/>'
    d += t(500, 100, "one line of code", "tx", "middle")
    d += '<path class="lnd" d="M30,122 Q250,112 500,122 T970,122"/>'
    d += t(950, 112, "waterline", "sm", "end")
    d += '<rect class="hz" x="130" y="132" width="740" height="180" rx="70"/>'
    items = [(285, 150, "files written", "and rewritten"), (500, 150, "a transaction", "log entry"),
             (715, 150, "data shuffled", "between machines"), (390, 230, "memory, spill", "to disk"),
             (610, 230, "the bill", "per second")]
    for x, y, a, s in items:
        d += b(x - 85, y, 170, 58, a, s, "bx")
    return figure(1000, 330, d,
                  "An iceberg. Above the waterline: one line of code. Below: files written and rewritten, a transaction log entry, data shuffled between machines, memory and spill to disk, and the bill per second.",
                  "Tools hide the bottom of the iceberg on purpose. That is fine until it breaks or the bill arrives.")


def drawing_uh_curves():
    t, p = kit.text, kit.path
    d = '<line class="ln" x1="80" y1="290" x2="940" y2="290"/><line class="ln" x1="80" y1="290" x2="80" y2="45"/>'
    d += t(90, 42, "what you can do on your own", "sm", "start")
    d += t(510, 318, "months on the job", "sm", "middle")
    d += p("M85,285 Q200,130 520,140 T930,135", "lnd")
    d += p("M85,285 Q450,270 600,160 T930,55", "lnc")
    d += t(330, 200, "shortcuts: fast start,", "sm", "middle") + t(330, 218, "then stuck when it breaks", "sm", "middle")
    d += t(640, 60, "fundamentals: slow start,", "sm", "end") + t(640, 78, "then it compounds", "sm", "end")
    d += '<circle class="hk" cx="585" cy="168" r="6"/>'
    d += kit.box(610, 190, 230, 58, "The first real incident", "where the lines cross", "bxs")
    return figure(1000, 335, d,
                  "Two curves over months on the job. Shortcuts start fast, then flatten and get stuck when something breaks. Fundamentals start slow, then compound and pass the shortcut line around the first real incident.",
                  "The slow road looks slower for a few months. After the first real incident, it is the only road that keeps going up.")


def drawing_uh_layers():
    b, t = kit.box, kit.text
    layers = [("Your code", "the query, the pipeline, the prompt", "bxm"),
              ("The tool", "the API or button you call", "bx"),
              ("The engine", "plans, stages, tasks; tokens and context", "bx"),
              ("Storage and network", "files, logs, bytes moved", "bx"),
              ("Time and money", "where every choice ends up", "bxs")]
    d = t(500, 22, "every tool is a stack; learn one layer below where you work", "sm", "middle")
    for i, (title, sub, k) in enumerate(layers):
        d += b(250, 40 + i * 62, 500, 52, title, sub, k)
    d += '<path class="lnc" d="M765,66 Q830,97 765,126"/>'
    d += t(785, 64, "you work here", "sm", "start")
    d += t(790, 134, "learn this one too", "bd", "start")
    return figure(1000, 360, d,
                  "Five stacked layers: your code; the tool; the engine (plans, stages, tasks; tokens and context); storage and network (files, logs, bytes moved); time and money. An arrow from 'you work here' at the code layer to 'learn this one too' at the tool layer below.",
                  "You don't need the whole stack. You need the layer under the one you touch every day.")


def drawing_uh_check_ai():
    b, a = kit.box, kit.arrow
    d = b(20, 110, 200, 80, "AI's answer", "fluent and confident", "bxm")
    d += a(222, 150, 288, 150)
    d += b(290, 95, 260, 110, "You, with fundamentals", ["does this match how", "the engine works?"], "solid")
    d += a(552, 130, 638, 80)
    d += a(552, 170, 638, 220)
    d += b(640, 40, 340, 80, "Check it", "run it, read the plan or the log", "bxs")
    d += b(640, 180, 340, 80, "Without them", "you can only ask the AI again", "bx")
    return figure(1000, 290, d,
                  "The AI's answer, fluent and confident, goes to you. With fundamentals you ask whether it matches how the engine works, and check it by running it and reading the plan or log. Without them, you can only ask the AI again.",
                  "Fundamentals are what let you check the machine instead of trusting it.")


DRAWINGS = {"uh-iceberg": drawing_uh_iceberg, "uh-curves": drawing_uh_curves,
            "uh-layers": drawing_uh_layers, "uh-check-ai": drawing_uh_check_ai}
