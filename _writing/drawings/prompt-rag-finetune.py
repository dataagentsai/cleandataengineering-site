"""Drawings for 'Prompt, RAG or fine-tune? Pick in that order'.
kit, figure, E and ROOT are given as globals by build.py."""


def _sticky(cx, cy):
    """A sticky note with a folded corner and a few scribbled lines."""
    x, y = cx - 45, cy - 45
    return (f'<path class="pf pf-bxs" d="M{x},{y} L{x + 90},{y} L{x + 90},{y + 70} L{x + 70},{y + 90} L{x},{y + 90} Z"/>'
            f'<path class="hz" d="M{x},{y} L{x + 90},{y} L{x + 90},{y + 70} L{x + 70},{y + 90} L{x},{y + 90} Z" fill="none"/>'
            f'<path class="ln" d="M{x + 90},{y + 70} L{x + 70},{y + 70} L{x + 70},{y + 90}"/>'
            + "".join(f'<line class="ln" x1="{x + 14}" y1="{y + 20 + k * 16}" x2="{x + 72 - (k % 2) * 16}" y2="{y + 20 + k * 16}"/>' for k in range(4)))


def _book(cx, cy):
    """An open book seen from above."""
    return (f'<path class="hz" d="M{cx},{cy - 30} Q{cx - 40},{cy - 46} {cx - 80},{cy - 34} L{cx - 80},{cy + 34} Q{cx - 40},{cy + 22} {cx},{cy + 38} Z"/>'
            f'<path class="hz" d="M{cx},{cy - 30} Q{cx + 40},{cy - 46} {cx + 80},{cy - 34} L{cx + 80},{cy + 34} Q{cx + 40},{cy + 22} {cx},{cy + 38} Z"/>'
            + "".join(f'<line class="ln" x1="{cx - 66}" y1="{cy - 22 + k * 14}" x2="{cx - 14}" y2="{cy - 18 + k * 14}"/>' for k in range(4))
            + "".join(f'<line class="ln" x1="{cx + 14}" y1="{cy - 18 + k * 14}" x2="{cx + 66}" y2="{cy - 22 + k * 14}"/>' for k in range(4))
            + f'<rect class="pf pf-bxs" x="{cx + 20}" y="{cy - 6}" width="40" height="10" rx="2"/>')


def _dumbbell(cx, cy):
    """A dumbbell on a gym bench."""
    return (f'<rect class="hz" x="{cx - 80}" y="{cy + 20}" width="160" height="16" rx="5"/>'
            f'<line class="lnc" x1="{cx - 60}" y1="{cy + 36}" x2="{cx - 60}" y2="{cy + 56}"/>'
            f'<line class="lnc" x1="{cx + 60}" y1="{cy + 36}" x2="{cx + 60}" y2="{cy + 56}"/>'
            f'<line class="lnc" x1="{cx - 50}" y1="{cy - 10}" x2="{cx + 50}" y2="{cy - 10}"/>'
            f'<rect class="hk" x="{cx - 66}" y="{cy - 34}" width="18" height="48" rx="4"/>'
            f'<rect class="hk" x="{cx - 84}" y="{cy - 26}" width="16" height="32" rx="4"/>'
            f'<rect class="hk" x="{cx + 48}" y="{cy - 34}" width="18" height="48" rx="4"/>'
            f'<rect class="hk" x="{cx + 68}" y="{cy - 26}" width="16" height="32" rx="4"/>')


def drawing_prf_tools():
    t, b = kit.text, kit.box
    d = t(30, 24, "each tool costs more than the one before: climb only when the step below can't do the job", "sm", "start")
    # rising steps
    steps = [(30, 250, "Prompt", "minutes, almost free"), (360, 190, "RAG", "days, a search index"),
             (690, 130, "Fine-tune", "weeks, data and tests")]
    for i, (x, top, name, cost) in enumerate(steps):
        d += f'<rect class="pf pf-bx" x="{x}" y="{top}" width="280" height="{370 - top}" rx="6"/>'
        d += f'<rect class="hz" x="{x}" y="{top}" width="280" height="{370 - top}" rx="6" fill="none"/>'
        d += t(x + 140, top + 30, name, "bd", "middle") + t(x + 140, top + 54, cost, "sm", "middle")
    d += _sticky(170, 185)
    d += _book(500, 130)
    d += _dumbbell(830, 60)
    d += t(170, 395, "a sticky note of instructions", "sm", "middle")
    d += t(500, 395, "an open book of facts", "sm", "middle")
    d += t(830, 395, "a gym that changes the model", "sm", "middle")
    return figure(1000, 410, d, "Three rising steps. The lowest is Prompt, minutes and almost free, with a sticky note. The middle is RAG, days and a search index, with an open book. The highest is Fine-tune, weeks of data and tests, with a dumbbell on a gym bench.",
                  "A sticky note, an open book and a gym. The first two change what the model sees; only the gym changes the model.")


def drawing_prf_fixes():
    b, t = kit.box, kit.text
    cols = [("Prompt", "solid", ["instructions", "and examples"], ["behaviour", "and format"], ["a few lines", "to maintain"]),
            ("RAG", "bx", ["the facts it reads", "for this question"], ["missing or", "changing facts"], ["an index, chunks", "and a retrieval test"]),
            ("Fine-tune", "bxs", ["its own weights", "by training"], ["style, a narrow skill,", "format at volume"], ["examples, GPUs,", "a retrain per update"])]
    rows = ["IT CHANGES", "IT FIXES", "IT COSTS"]
    d = ""
    for j, r in enumerate(rows):
        d += t(10, 128 + j * 100, r, "lbl")
    for i, (name, kind, ch, fx, co) in enumerate(cols):
        x = 140 + i * 285
        d += b(x, 20, 265, 60, name, "", kind)
        for j, lines in enumerate((ch, fx, co)):
            d += b(x, 95 + j * 100, 265, 80, lines[0], lines[1], "bxm")
    d += t(570, 410, "fine-tuning is not in the facts column: it does not reliably teach the model new facts", "sm", "middle")
    return figure(1000, 425, d, "Three columns: Prompt, RAG and Fine-tune. Prompt changes instructions and examples, fixes behaviour and format, and costs a few lines to maintain. RAG changes the facts the model reads for this question, fixes missing or changing facts, and costs an index, chunks and a retrieval test. Fine-tune changes the model's own weights, fixes style, a narrow skill or format at volume, and costs examples, GPUs and a retrain per update.",
                  "What each tool changes, what it fixes, and what it costs to keep.")


def drawing_prf_questions():
    b, a, t, n = kit.box, kit.arrow, kit.text, kit.num
    d = b(60, 20, 340, 80, "Start: a clear prompt", ["a few examples, and an eval set"], "solid")
    d += t(640, 52, "measure on the eval set", "sm", "middle") + t(640, 72, "after every change", "sm", "middle")
    qs = [("Is it missing facts?", ["or facts that change"], "Add RAG", ["fetch them at question time"], "bx"),
          ("Still wrong behaviour?", ["despite clear instructions"], "Fine-tune the habit", ["format, tone, one skill"], "bxs"),
          ("Too slow or dear?", ["at your real volume"], "Fine-tune a small one", ["to do the big one's job"], "bxs")]
    d += a(230, 102, 230, 128)
    for i, (q, qs_, ans, asub, kind) in enumerate(qs):
        y = 130 + i * 120
        d += n(30, y + 45, i + 1)
        d += b(60, y, 340, 90, q, qs_, "bxm")
        d += a(402, y + 45, 600, y + 45, "yes")
        d += b(602, y, 300, 90, ans, asub, kind)
        if i < 2:
            d += a(230, y + 92, 230, y + 118, "no", lx=246, ly=y + 110, anchor="start")
    d += a(230, 462, 230, 488, "no", lx=246, ly=480, anchor="start")
    d += t(230, 512, "ship the prompt", "bd", "middle")
    return figure(1000, 530, d, "Start with a clear prompt, a few examples and an eval set. Then three numbered questions in order. One: is it missing facts? Yes leads to add RAG. No leads to two: is the behaviour still wrong despite clear instructions? Yes leads to fine-tune the habit: format, tone, one skill. No leads to three: too slow or expensive at your real volume? Yes leads to fine-tune a small model to do the big one's job. No leads to ship the prompt.",
                  "Start with the prompt, then ask three questions top to bottom. Most teams stop at the first.")


def drawing_prf_stack():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(250, 24, "WHAT MOST SYSTEMS RUN", "lbl", "middle") + t(750, 24, "A FEW, AT HIGH VOLUME", "lbl", "middle")
    left = [("The prompt", ["rules, format, 3 examples"], "solid"), ("Retrieved facts", ["top 5 passages, fenced"], "bx"),
            ("A general model", ["as it comes"], "bxm")]
    right = [("The prompt", ["shorter: habits moved"], "solid"), ("Retrieved facts", ["still fetched fresh"], "bx"),
             ("A tuned small model", ["format and tone baked in"], "bxs")]
    for col, items in ((0, left), (1, right)):
        x = 60 + col * 500
        for j, (title, sub, kind) in enumerate(items):
            d += b(x, 50 + j * 100, 380, 80, title, sub, kind)
    d += t(250, 362, "change a fact: update the index", "sm", "middle")
    d += t(750, 362, "facts still come from RAG, never the weights", "sm", "middle")
    d += a(442, 280, 556, 280) + t(499, 308, ["only if the", "numbers say so"], "sm", "middle")
    return figure(1000, 380, d, "Two stacks. On the left, what most systems run: the prompt on top, retrieved facts in the middle, a general model at the bottom. On the right, a few high-volume systems: a shorter prompt, retrieved facts still fetched fresh, and a tuned small model with format and tone baked in. An arrow between the bottom boxes says only if the numbers say so.",
                  "Most real systems are a prompt plus RAG. Fine-tuning sits underneath, rarely, and the facts still come from retrieval.")


DRAWINGS = {"prf-tools": drawing_prf_tools, "prf-fixes": drawing_prf_fixes,
            "prf-questions": drawing_prf_questions, "prf-stack": drawing_prf_stack}
