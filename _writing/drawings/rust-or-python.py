"""Drawings for 'Rust or Python for agents? Probably both'. Globals kit, figure, E, ROOT are injected."""


def drawing_rust_brain_arm():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(500, 24, "the brain decides and changes its mind; the arm lifts the same heavy thing all day", "sm", "middle")
    # the brain: a lumpy outline with a few folds
    d += ('<path class="hz" d="M150,150 Q130,100 180,85 Q200,55 245,70 Q280,50 310,80 Q355,80 350,125 '
          'Q375,160 335,180 Q320,210 275,200 Q245,220 215,200 Q170,210 160,180 Q130,175 150,150 Z"/>')
    d += ('<path class="ln" d="M190,110 Q215,95 235,115" fill="none"/>'
          '<path class="ln" d="M255,95 Q285,105 300,130" fill="none"/>'
          '<path class="ln" d="M185,160 Q215,140 245,165" fill="none"/>'
          '<path class="ln" d="M265,160 Q295,150 320,170" fill="none"/>')
    d += t(250, 240, "PYTHON", "lbl", "middle")
    d += b(110, 265, 280, 90, "The thinking", ["orchestration, prompts,", "evals, notebooks"], "bx")
    # the arm: upper arm lying flat, forearm raised, fist holding a dumbbell
    d += ('<path class="hz" d="M610,212 Q660,180 705,208 Q745,200 765,160 L778,112 Q797,88 816,104 '
          'L812,168 Q802,238 740,246 L610,246 Z"/>')
    d += '<path class="ln" d="M712,214 Q738,196 758,204" fill="none"/>'
    d += ('<line class="lnc" x1="745" y1="92" x2="855" y2="92"/>'
          '<rect class="pf pf-solid" x="734" y="66" width="22" height="52" rx="4"/><rect class="hz" x="730" y="64" width="22" height="52" rx="4"/>'
          '<rect class="pf pf-solid" x="852" y="66" width="22" height="52" rx="4"/><rect class="hz" x="848" y="64" width="22" height="52" rx="4"/>')
    d += t(750, 262, "RUST", "lbl", "middle")
    d += b(610, 275, 280, 80, "The heavy lifting", ["sandbox, gateway, parser"], "bxs")
    # the two talk to each other
    d += a(390, 115, 585, 115, "what to do next", ly=105)
    d += a(585, 165, 390, 165, "the result", ly=155)
    return figure(1000, 370, d, "A cartoon brain labelled Python, the thinking: orchestration, prompts, evals and notebooks. A strong arm lifting a dumbbell labelled Rust, the heavy lifting: sandbox, gateway and parser. Arrows between them: the brain sends what to do next, the arm sends back the result.",
                  "Python for the thinking, Rust for the heavy lifting. Most agents need both.")


def drawing_rust_one_agent():
    b, a, t = kit.box, kit.arrow, kit.text
    d = b(380, 30, 240, 90, "The model", ["someone else's server,", "the slow part"], "bxm")
    d += t(170, 140, "PYTHON: THE THINKING", "lbl", "middle")
    d += t(830, 140, "RUST: THE HEAVY LIFTING", "lbl", "middle")
    left = [("Orchestration loop", "picks the next step"), ("Prompts and tool list", "change every week"),
            ("Evals", "notebooks and scores")]
    right = [("Gateway", "every call passes through"), ("Code sandbox", "runs code the model wrote"),
             ("File parser", "chews through big files")]
    for i, (n, s) in enumerate(left):
        d += b(30, 155 + i * 95, 280, 80, n, s, "bx")
    for i, (n, s) in enumerate(right):
        d += b(690, 155 + i * 95, 280, 80, n, s, "bxs")
    d += a(312, 190, 686, 190, "every model call", ly=180)
    d += a(312, 215, 686, 280, "run this code", lx=470, ly=228)
    d += a(705, 153, 622, 105)
    d += t(500, 440, "say a turn takes 3 seconds: about 2.9 of them are the model", "sm", "middle")
    return figure(1000, 455, d, "One agent split by language. On the left in Python: the orchestration loop, the prompts and tool list, and the evals. On the right in Rust: the gateway every call passes through, the code sandbox that runs code the model wrote, and a parser for big files. The loop sends every model call through the gateway to the model, which sits outside both as someone else's server and is the slow part.",
                  "One agent, two languages. The parts that change often stay in Python; the parts every request passes through go to Rust.")


def drawing_rust_crate():
    b, t = kit.box, kit.text
    d = t(500, 24, "a Python face on the outside, a Rust engine on the inside", "sm", "middle")
    # the crate
    d += '<rect class="pf pf-bxs" x="305" y="85" width="390" height="250" rx="6"/><rect class="hz" x="300" y="80" width="390" height="250" rx="6"/>'
    d += ''.join(f'<line class="ln" x1="300" y1="{y}" x2="690" y2="{y}"/>' for y in (142, 205, 268))
    d += '<line class="lnc" x1="305" y1="325" x2="685" y2="85"/>'
    d += '<rect class="hz" x="390" y="180" width="210" height="50" rx="4"/>'
    d += t(495, 211, "RUST INSIDE", "lbl", "middle")
    # a little gear on the lid
    d += ('<circle class="hz" cx="495" cy="62" r="16"/><circle class="hk" cx="495" cy="62" r="5"/>'
          + ''.join(f'<rect class="hk" x="{495 + dx - 3}" y="{62 + dy - 3}" width="6" height="6"/>'
                    for dx, dy in ((0, -20), (0, 20), (-20, 0), (20, 0), (14, 14), (-14, -14), (14, -14), (-14, 14))))
    left = [("uv", "installs packages"), ("Ruff", "lints and formats"), ("Pydantic core", "validates data")]
    right = [("Polars", "DataFrames"), ("tokenizers", "Hugging Face")]
    for i, (n, s) in enumerate(left):
        y = 80 + i * 90
        d += b(30, y, 210, 64, n, s, "bx")
        d += f'<line class="ln" x1="242" y1="{y + 32}" x2="298" y2="{y + 32}"/><circle class="hz" cx="248" cy="{y + 32}" r="5"/>'
    for i, (n, s) in enumerate(right):
        y = 125 + i * 90
        d += b(760, y, 210, 64, n, s, "bx")
        d += f'<line class="ln" x1="692" y1="{y + 32}" x2="758" y2="{y + 32}"/><circle class="hz" cx="752" cy="{y + 32}" r="5"/>'
    return figure(1000, 350, d, "A wooden crate stamped Rust inside, with five labels tied to it: uv installs packages, Ruff lints and formats, Pydantic core validates data, Polars DataFrames, and Hugging Face tokenizers.",
                  "Python tools you already use that are Rust inside.")


def drawing_rust_three_questions():
    b, a, t, n = kit.box, kit.arrow, kit.text, kit.num
    d = t(500, 24, "ask for each part of the agent, not for the whole agent", "sm", "middle")
    d += b(20, 60, 270, 95, "Hot path?", ["every request waits on it,", "and it isn't the model"], "bxs") + n(26, 60, 1)
    d += b(360, 60, 270, 95, "Untrusted input?", ["code the model wrote,", "uploads, web pages"], "bxs") + n(366, 60, 2)
    d += b(700, 70, 280, 75, "Keep it in Python", "most parts land here", "bx")
    d += a(292, 107, 356, 107, "no", ly=98)
    d += a(632, 107, 696, 107, "no", ly=98)
    d += b(360, 255, 270, 95, "Team knows Rust?", ["or will learn it, and fix", "it at 2 in the morning"], "bxs") + n(366, 255, 3)
    d += a(155, 157, 356, 285, "yes", lx=240, ly=232)
    d += a(495, 157, 495, 251, "yes", lx=512, ly=208, anchor="start")
    d += b(700, 225, 280, 70, "Write it in Rust", "sandbox, gateway, parser", "solid")
    d += b(700, 315, 280, 70, "Adopt a Rust tool", "don't write your own", "bxm")
    d += a(632, 285, 696, 262, "yes", ly=262)
    d += a(632, 322, 696, 345, "no", ly=322)
    return figure(1000, 400, d, "A decision picture with three questions. One: is it on the hot path, where every request waits and it isn't the model? Two: does it take untrusted input such as code the model wrote, uploads or web pages? If both are no, keep it in Python. If either is yes, three: does the team know Rust? If yes, write it in Rust. If no, adopt a ready-made Rust tool.",
                  "Three questions per part. Most parts end up in Python; a few earn Rust.")


DRAWINGS = {"rust-brain-arm": drawing_rust_brain_arm, "rust-one-agent": drawing_rust_one_agent,
            "rust-crate": drawing_rust_crate, "rust-three-questions": drawing_rust_three_questions}
