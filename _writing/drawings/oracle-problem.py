"""Drawings for 'Who checks the checker? The oracle problem in agent simulation'.
kit, figure, E and ROOT are given as globals by build.py."""


def _orc_person(cx, top):
    """A small stick person whose head centre is at (cx, top)."""
    return (f'<circle class="hz" cx="{cx}" cy="{top}" r="14"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 14}" x2="{cx}" y2="{top + 52}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 52}" x2="{cx - 12}" y2="{top + 76}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 52}" x2="{cx + 12}" y2="{top + 76}"/>')


def _orc_tick(x, y, s=1.0):
    return f'<path class="lnc" fill="none" d="M{x},{y} L{x + 9 * s},{y + 10 * s} L{x + 26 * s},{y - 11 * s}"/>'


def _orc_cross(x, y, s=1.0):
    r = 10 * s
    return (f'<line class="lnc" x1="{x}" y1="{y - r}" x2="{x + 2 * r}" y2="{y + r}"/>'
            f'<line class="lnc" x1="{x + 2 * r}" y1="{y - r}" x2="{x}" y2="{y + r}"/>')


def drawing_orc_own_paper():
    b, t = kit.box, kit.text
    d = t(500, 22, "an answer sheet is only worth something if someone else holds the key", "sm", "middle")
    # left: the student marks their own paper
    d += _orc_person(150, 70)
    d += '<line class="lnc" x1="150" y1="100" x2="200" y2="118"/>'
    d += '<rect class="hz" x="110" y="146" width="300" height="14" rx="3"/>'
    d += '<rect class="hz" x="215" y="72" width="150" height="72" rx="4"/>'
    d += ''.join(f'<line class="ln" x1="228" y1="{88 + k * 14}" x2="290" y2="{88 + k * 14}"/>' for k in range(4))
    d += _orc_tick(305, 98, 1.3)
    d += t(332, 136, "10/10", "bd", "middle")
    d += '<path class="hz" d="M40,30 L160,30 L160,50 L118,50 L128,58 L104,50 L40,50 Z"/>'
    d += t(100, 45, "all correct!", "sm", "middle")
    d += b(60, 190, 360, 90, "Marks its own paper", ["the agent's own model reads", "the agent's chat and says 'fine'"], "bxm")
    d += t(500, 130, "vs", "bd", "middle")
    # right: a teacher with the answer key
    d += _orc_person(650, 70)
    d += '<line class="lnc" x1="650" y1="100" x2="700" y2="112"/>'
    d += '<rect class="pf pf-bxs" x="706" y="76" width="150" height="72" rx="4"/>'
    d += '<rect class="hz" x="702" y="72" width="150" height="72" rx="4" fill-opacity="0"/>'
    d += t(777, 100, "ANSWER KEY", "lbl", "middle")
    d += ''.join(f'<line class="ln" x1="722" y1="{114 + k * 12}" x2="832" y2="{114 + k * 12}"/>' for k in range(2))
    d += b(560, 190, 380, 90, "Marks against a key", ["the written rules and the world's", "state say what is right"], "bxs")
    d += t(500, 312, "the thing under test never grades itself", "bd", "middle")
    return figure(1000, 325, d,
                  "A cartoon exam. On the left a student marks their own paper with a big tick and 10 out of 10, saying 'all correct!': the agent's own model reads the agent's chat and says fine. On the right a teacher holds an answer key: the written rules and the world's state say what is right.",
                  "The calculator problem as an exam. A student who marks their own paper always passes.")


def drawing_orc_order():
    b, a, t = kit.box, kit.arrow, kit.text
    steps = [("World state", ["what changed in", "the systems?"], "bx"),
             ("Action rules", ["was every write", "asked for, allowed?"], "bx"),
             ("Owed vs done", ["required or promised,", "but never done?"], "bx"),
             ("LLM judge", ["only what code can't", "see; checked first"], "bxm")]
    d = t(500, 22, "ask the cheap, exact questions first; call a model only for what is left", "sm", "middle")
    for i, (title, sub, kind) in enumerate(steps):
        x = 10 + i * 250
        d += kit.num(x + 22, 62, i + 1)
        d += b(x, 80, 225, 110, title, sub, kind)
        if i < 3:
            d += a(x + 227, 135, x + 248, 135)
    d += '<line class="lnc" x1="40" y1="240" x2="950" y2="240"/>'
    d += '<path class="lnc" fill="none" d="M935,230 L952,240 L935,250"/>'
    d += t(40, 272, "free, instant, same answer every time", "sm", "start")
    d += t(950, 272, "costs per call, can be confidently wrong", "sm", "end")
    return figure(1000, 290, d,
                  "Four checkers in order, left to right. 1, world state: what changed in the systems? 2, action rules: was every write asked for and allowed? 3, owed versus done: required or promised, but never done? 4, an LLM judge, drawn dashed: only what code can't see, and checked first. An arrow underneath runs from free, instant and repeatable to costly and sometimes confidently wrong.",
                  "The order of checkers. Most failures are caught before a model is ever asked.")


def drawing_orc_mutants():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(500, 20, "break the agent on purpose, then see whether any test goes red", "sm", "middle")
    # a planted bug (a small beetle)
    d += '<ellipse class="hz" cx="105" cy="78" rx="24" ry="15"/><circle class="hz" cx="134" cy="78" r="8"/>'
    d += '<line class="ln" x1="105" y1="63" x2="105" y2="93"/>'
    d += ''.join(f'<line class="ln" x1="{92 + k * 13}" y1="64" x2="{88 + k * 13}" y2="52"/>'
                 f'<line class="ln" x1="{92 + k * 13}" y1="92" x2="{88 + k * 13}" y2="104"/>' for k in range(3))
    d += t(105, 125, "a planted bug", "sm", "middle")
    d += b(20, 140, 170, 90, "The agent", "as built, plus one bug", "solid")
    rows = [("Mutant 1", "the own-order check removed", True),
            ("Mutant 2", "7 days loosened to 8", True),
            ("Mutant 3", "the repeat guard dropped", False)]
    for i, (title, sub, caught) in enumerate(rows):
        y = 45 + i * 100
        d += a(192, 185, 258, y + 37)
        d += b(260, y, 290, 75, title, sub, "bx")
        d += a(552, y + 37, 628, y + 37)
        if caught:
            d += _orc_tick(645, y + 37, 1.1)
            d += t(690, y + 43, "caught: a test went red", "tx", "start")
        else:
            d += _orc_cross(645, y + 37, 1.1)
            d += t(690, y + 43, "missed: a test is missing", "bd", "start")
    d += t(500, 345, "a bug that no test notices becomes a named gap to fill", "sm", "middle")
    return figure(1000, 360, d,
                  "A small beetle stands for a planted bug. The agent, as built plus one bug, is copied into three mutants: one with the own-order check removed, one with 7 days loosened to 8, one with the guard against repeating a write dropped. Every test runs against each. The first two are caught because a test went red. The third is missed, which means a test is missing.",
                  "Mutation testing. Seed known faults, and a checker that misses one has a gap with a name.")


def drawing_orc_agreement():
    t = kit.text
    d = t(150, 28, "CASE", "lbl", "middle") + t(400, 28, "PEOPLE SAY", "lbl", "middle")
    d += t(600, 28, "JUDGE SAYS", "lbl", "middle") + t(800, 28, "AGREE?", "lbl", "middle")
    rows = [("tone with an upset buyer", "pass", "pass"),
            ("apology, no promise", "fail", "fail"),
            ("long but correct answer", "pass", "pass"),
            ("polite, but dodged it", "fail", "pass"),
            ("short and right", "pass", "pass"),
            ("asked one good question", "pass", "pass")]
    for i, (case, ppl, jdg) in enumerate(rows):
        y = 70 + i * 42
        d += t(150, y + 5, case, "tx", "middle")
        for cx, v in ((400, ppl), (600, jdg)):
            k = "pf pf-bxs" if v == "pass" else "pf pf-bx"
            d += f'<rect class="{k}" x="{cx - 38}" y="{y - 14}" width="76" height="28" rx="12"/>'
            d += f'<rect class="hz" x="{cx - 40}" y="{y - 16}" width="76" height="28" rx="12" fill-opacity="0"/>'
            d += t(cx - 2, y + 4, v, "tx", "middle")
        if ppl == jdg:
            d += _orc_tick(788, y, 0.8)
        else:
            d += _orc_cross(790, y, 0.8)
    d += t(500, 342, "5 of 6 agree, but a judge that always says 'pass' would get 4 of 6 for free", "bd", "middle")
    d += t(500, 368, "so score it with a statistic that removes lucky agreement, and look hard at every cross", "sm", "middle")
    return figure(1000, 385, d,
                  "Six cases in rows. Two columns of verdicts: what people said and what the LLM judge said, then whether they agree. They agree on five; on 'polite, but dodged it' people said fail and the judge said pass. A note says a judge that always says pass would agree on 4 of 6 for free, so use a statistic that removes lucky agreement.",
                  "A judge checked against people. Agreement is measured, and the disagreements are the lesson.")


DRAWINGS = {
    "orc-own-paper": drawing_orc_own_paper,
    "orc-order": drawing_orc_order,
    "orc-mutants": drawing_orc_mutants,
    "orc-agreement": drawing_orc_agreement,
}
