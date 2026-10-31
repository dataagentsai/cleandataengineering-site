"""Drawings for 'Most of an agent is ordinary software'. Globals kit, figure, E, ROOT are injected.

All numbers are code lines at reference-agent commit d0a8b84 (blank lines, comments and docstrings dropped).
"""

ROWS = [  # (job, lines) — tests are drawn last and dashed
    ("The code that calls a model", 817),
    ("The loop", 1572),
    ("Context building", 144),
    ("Checks, policies, sign-in", 2509),
    ("Tools and tool adapters", 815),
    ("State and persistence", 1471),
    ("Durable workflows, retries", 2667),
    ("Tracing, telemetry, cost", 1677),
    ("Evals", 5379),
    ("Config and wiring", 944),
    ("Everything else", 6636),
    ("Tests", 18415),
]


def _person(cx, top, cls="bx"):
    return (f'<circle class="{cls}" cx="{cx}" cy="{top}" r="13"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 13}" x2="{cx}" y2="{top + 48}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 48}" x2="{cx - 11}" y2="{top + 70}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 48}" x2="{cx + 11}" y2="{top + 70}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 24}" x2="{cx - 17}" y2="{top + 38}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 24}" x2="{cx + 20}" y2="{top + 34}"/>')


def drawing_loc_iceberg():
    t = kit.text
    d = t(500, 22, "what you see in a demo is the tip; the code you maintain is under the water", "sm", "middle")
    # the tip, above the water
    d += '<path class="solid" d="M440,128 L468,72 L492,58 L512,66 L534,52 L560,128 Z"/>'
    d += t(600, 72, ["the model call", "817 lines, 3%"], "bd", "start")
    d += '<line class="ln" x1="596" y1="80" x2="540" y2="88"/>'
    # the sea
    d += ('<path class="ln" d="M20,130 Q60,120 100,130 T180,130 T260,130 T340,130 T420,130 '
          'T580,130 T660,130 T740,130 T820,130 T900,130 T980,130"/>')
    # the body, below the water
    d += '<path class="pf pf-bx" d="M440,132 L560,132 L700,170 L840,250 L780,350 L520,372 L250,345 L150,250 L300,165 Z"/>'
    d += '<path class="ln" d="M440,132 L300,165 L150,250 L250,345 L520,372 L780,350 L840,250 L700,170 L560,132"/>'
    d += t(500, 172, "23,814 lines, 97%", "bd", "middle")
    labels = [(300, 215, "the loop"), (500, 215, "checks and sign-in"), (700, 215, "durable workflows"),
              (270, 262, "state"), (420, 262, "tools"), (580, 262, "traces and cost"), (740, 262, "config"),
              (390, 309, "evals"), (620, 309, "the edge, pages, reports")]
    for x, y, s in labels:
        d += t(x, y, s, "tx", "middle")
    # a small boat for scale
    d += '<path class="hz" d="M120,112 L190,112 L178,126 L132,126 Z"/><line class="ln" x1="155" y1="112" x2="155" y2="82"/>'
    d += '<path class="hz" d="M157,84 L180,106 L157,106 Z"/>'
    d += t(910, 330, ["plus 18,415 lines", "of tests"], "sm", "middle")
    return figure(1000, 390, d,
                  "An iceberg. Above the water, a small tip labelled the model call, 817 lines, 3 percent. Below the water, a large body labelled 23,814 lines, 97 percent, containing the loop, checks and sign-in, durable workflows, state, tools, traces and cost, config, evals, and the edge, pages and reports. A note says plus 18,415 lines of tests.",
                  "The reference agent, measured. Leaving tests out, the model call is 3% of the code.")


def drawing_loc_bars():
    t = kit.text
    d = t(500, 22, "code lines by job, reference agent at commit d0a8b84", "sm", "middle")
    scale = 560 / 18415
    for i, (job, n) in enumerate(ROWS):
        y = 50 + i * 36
        if job == "Tests":
            y += 14
            d += '<line class="lnd" x1="40" y1="{0}" x2="960" y2="{0}"/>'.format(y - 9)
        cls = "solid" if i == 0 else ("bxm" if job == "Tests" else "bx")
        d += t(320, y + 18, job, "bd" if i == 0 else "tx", "end")
        w = max(4, round(n * scale))
        d += f'<rect class="{cls}" x="335" y="{y + 2}" width="{w}" height="24" rx="4"/>'
        d += t(335 + w + 10, y + 19, f"{n:,}", "tx", "start")
    return figure(1000, 510, d,
                  "Horizontal bars of code lines by job. The code that calls a model 817. The loop 1,572. Context building 144. Checks, policies and sign-in 2,509. Tools and tool adapters 815. State and persistence 1,471. Durable workflows and retries 2,667. Tracing, telemetry and cost 1,677. Evals 5,379. Config and wiring 944. Everything else 6,636. Below a dashed line, tests 18,415.",
                  "The model call is the first bar, and one of the shortest. Tests, below the line, are bigger than any job above it.")


def drawing_loc_skills():
    b, t = kit.box, kit.text
    d = t(500, 22, "what the other 97% asks of you: skills you may already have", "sm", "middle")
    boxes = [("Tests", ["fakes, fixtures,", "recorded replies"], "bxs"),
             ("Retries, idempotency", ["the same refund", "never runs twice"], "bx"),
             ("Auth", ["the token is checked", "at the tool, every call"], "bx"),
             ("Schemas", ["typed inputs and", "outputs at every seam"], "bx"),
             ("SQL and Postgres", ["state, ledgers,", "queues that survive"], "bx"),
             ("Tracing", ["every step written", "down, with its cost"], "bxs")]
    for i, (title, sub, k) in enumerate(boxes):
        x = 40 + (i % 3) * 320
        y = 45 + (i // 3) * 110
        d += b(x, y, 280, 92, title, sub, k)
    d += b(360, 280, 280, 70, "Talking to the model", "3% of the lines", "solid")
    return figure(1000, 365, d,
                  "Six boxes for the skills most of the code needs: tests with fakes, fixtures and recorded replies; retries and idempotency so the same refund never runs twice; auth with the token checked at the tool on every call; schemas with typed inputs and outputs; SQL and Postgres for state, ledgers and queues; tracing with every step and its cost. Below, one smaller lavender box: talking to the model, 3 percent of the lines.",
                  "Most of an agent asks for skills a good backend or data engineer already has.")


def drawing_loc_check_own():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(500, 22, "an hour with a spreadsheet, or twenty lines of Python", "sm", "middle")
    steps = [("List the files", ["your own code only,", "no .venv or vendored"]),
             ("Tag each file", ["one job per file,", "first rule that fits"]),
             ("Count code lines", ["skip blanks, comments,", "docstrings"]),
             ("Divide", ["each job by the total,", "tests on their own"])]
    for i, (title, sub) in enumerate(steps):
        x = 10 + i * 248
        d += b(x, 50, 220, 92, title, sub, "solid" if i == 3 else "bx")
        d += kit.num(x + 22, 72, i + 1)
        if i < 3:
            d += a(x + 222, 96, x + 246, 96)
    # a person holding a tally sheet
    d += _person(90, 180, "bxs")
    d += '<rect class="hz" x="112" y="196" width="46" height="58" rx="4"/>'
    for j in range(3):
        d += f'<line class="ln" x1="120" y1="{210 + j * 14}" x2="150" y2="{210 + j * 14}"/>'
    d += t(190, 226, "the model call: is it near 10%, or smaller?", "tx", "start")
    return figure(1000, 270, d,
                  "Four steps left to right: list the files, your own code only; tag each file with one job; count code lines, skipping blanks, comments and docstrings; divide each job by the total, with tests on their own. Below, a small person holds a tally sheet and asks whether the model call is near 10 percent or smaller.",
                  "How to measure your own agent's split. The rules you tag with matter more than the tool you count with.")


DRAWINGS = {
    "loc-iceberg": drawing_loc_iceberg,
    "loc-bars": drawing_loc_bars,
    "loc-skills": drawing_loc_skills,
    "loc-check-own": drawing_loc_check_own,
}
