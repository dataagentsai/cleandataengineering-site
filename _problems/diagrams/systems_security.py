"""Problem diagrams for the groups 'Data and computer systems' and 'Security'.
kit, figure, E and ROOT are injected by _problems/build.py."""


def _person(cx, top):
    """A small stick person; head centre at (cx, top + 13), feet at top + 80."""
    return (f'<circle class="hz" cx="{cx}" cy="{top + 13}" r="13"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 26}" x2="{cx}" y2="{top + 58}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 58}" x2="{cx - 11}" y2="{top + 80}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 58}" x2="{cx + 11}" y2="{top + 80}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 36}" x2="{cx - 16}" y2="{top + 50}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 36}" x2="{cx + 16}" y2="{top + 50}"/>')


def _pink(x, y, w, h, rx=8):
    """A pink 'trouble' shape: pastel fill under an ink outline."""
    return (f'<rect class="pf pf-hatch" x="{x + 3}" y="{y + 3}" width="{w}" height="{h}" rx="{rx}"/>'
            f'<rect class="hz" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="none" style="fill:none"/>')


def _lock(cx, top, dashed=False, mark=""):
    """A small padlock: shackle plus body (40 x 32), body top at top + 18."""
    cls = "lnd" if dashed else "ln"
    s = f'<path class="{cls}" fill="none" d="M{cx - 12},{top + 18} L{cx - 12},{top + 8} Q{cx},{top - 8} {cx + 12},{top + 8} L{cx + 12},{top + 18}"/>'
    if dashed:
        s += f'<rect class="lnd" fill="none" x="{cx - 20}" y="{top + 18}" width="40" height="32" rx="5"/>'
    else:
        s += (f'<rect class="pf pf-bxs" x="{cx - 17}" y="{top + 21}" width="40" height="32" rx="5"/>'
              f'<rect class="hz" style="fill:none" x="{cx - 20}" y="{top + 18}" width="40" height="32" rx="5"/>')
    if mark:
        s += kit.text(cx, top + 41, mark, "bd", "middle")
    return s


def _magnifier(cx, cy, r=20):
    return (f'<circle class="hz" cx="{cx}" cy="{cy}" r="{r}"/>'
            f'<line class="lnc" x1="{cx + r * .7:.0f}" y1="{cy + r * .7:.0f}" x2="{cx + r * 1.6:.0f}" y2="{cy + r * 1.6:.0f}"/>')


def _cross(cx, cy, s=7):
    return (f'<line class="lnc" x1="{cx - s}" y1="{cy - s}" x2="{cx + s}" y2="{cy + s}"/>'
            f'<line class="lnc" x1="{cx + s}" y1="{cy - s}" x2="{cx - s}" y2="{cy + s}"/>')


def _tick(cx, cy):
    return f'<path class="lnc" fill="none" d="M{cx - 8},{cy} L{cx - 2},{cy + 7} L{cx + 10},{cy - 8}"/>'


# ---------------------------------------------------------------- systems

def d_query_sizes():
    b, a, t = kit.box, kit.arrow, kit.text
    d = b(10, 30, 170, 90, "A query", ["join three tables"], "bx")
    d += a(182, 75, 222, 75)
    d += b(225, 30, 230, 90, "The planner guesses", ["\"about 10 rows\"", "(say)"], "solid")
    d += a(457, 75, 497, 75)
    d += b(500, 30, 210, 90, "Picks a plan", ["built for 10 rows"], "bx")
    d += a(712, 75, 752, 75)
    d += b(755, 30, 235, 90, "Then it runs", ["10,000 rows arrive:", "1,000 times more"], "bxs")
    # the planner, guessing
    d += _person(340, 170) + t(372, 190, ["\"10, I think\""], "sm")
    # cartoon: a tap pouring a flood of rows into a small cup
    d += '<rect class="hz" x="800" y="148" width="90" height="20" rx="5"/><rect class="hz" x="866" y="168" width="24" height="18" rx="3"/>'
    for i in range(12):
        x = 852 + (i % 4) * 13 + (i // 4) * 3
        y = 192 + (i // 4) * 13
        d += f'<rect class="pf pf-bxs" x="{x}" y="{y}" width="11" height="8" rx="2"/><rect class="hz" style="fill:none" x="{x}" y="{y}" width="11" height="8" rx="2"/>'
    d += '<path class="hz" d="M846,236 L914,236 L906,280 L854,280 Z"/>'
    for x, y in ((830, 248), (822, 266), (924, 250), (934, 268), (840, 284), (920, 286)):
        d += f'<rect class="pf pf-bxs" x="{x}" y="{y}" width="11" height="8" rx="2"/><rect class="hz" style="fill:none" x="{x}" y="{y}" width="11" height="8" rx="2"/>'
    d += t(780, 214, ["a plan for", "a cupful"], "sm", "end")
    d += t(952, 250, "rows", "sm")
    d += t(570, 200, ["the slow plan was picked", "before anything ran"], "sm", "middle")
    return figure(1000, 295, d,
                  "A query goes to the planner, which guesses about 10 rows and picks a plan built for 10 rows. When it runs, 10,000 rows arrive, 1,000 times more. A cartoon tap pours a flood of rows into a small cup that overflows.",
                  "A query planner guesses row counts before it runs anything. When the guess is off by 1,000 times, it picks a plan built for the wrong size.")


def d_gpus_busy():
    b, t = kit.box, kit.text
    d = ""
    for i in range(8):
        x = 20 + i * 120
        bad = i == 4
        if bad:
            d += _pink(x, 50, 96, 56)
            d += t(x + 48, 84, "bad GPU", "sm", "middle")
            d += t(x + 48, 36, "stuck!", "bd", "middle")
        else:
            d += f'<rect class="hz" x="{x}" y="50" width="96" height="56" rx="6"/>'
            d += t(x + 48, 84, "GPU", "sm", "middle")
            d += t(x + 48, 36, "z z z", "sm", "middle")
        for k in range(4):
            px = x + 18 + k * 20
            d += f'<line class="ln" x1="{px}" y1="106" x2="{px}" y2="114"/>'
        d += f'<line class="ln" x1="{x + 48}" y1="114" x2="{x + 48}" y2="140"/>'
    d += '<line class="lnc" x1="20" y1="140" x2="980" y2="140"/>'
    d += t(20, 162, "the network: every step waits until all GPUs report back", "sm")
    d += b(20, 180, 300, 90, "A failure", ["one machine dies, and all go", "back to the last saved point"], "bxm")
    d += b(350, 180, 300, 90, "A slow machine", ["one straggler, and", "everyone waits for it"], "bxs")
    d += b(680, 180, 300, 90, "The network", ["GPUs sit idle waiting", "for each other's data"], "bx")
    return figure(1000, 285, d,
                  "Eight GPUs in a row joined by one network line. Seven are asleep, waiting. One in the middle is a bad GPU, stuck. Below: a failure sends everyone back to the last saved point, a slow machine makes everyone wait, and the network makes GPUs wait for each other's data.",
                  "A big training run moves at the pace of its slowest GPU. One failure, one slow machine or one slow link leaves thousands of others idle.")


def d_proving_code():
    b, a, t = kit.box, kit.arrow, kit.text
    d = b(10, 20, 220, 90, "AI writes code", ["hundreds of lines", "in seconds"], "bx")
    d += a(232, 65, 278, 65)
    d += b(280, 20, 210, 90, "Tests", ["catch some bugs,", "miss others"], "bxs")
    d += a(492, 65, 578, 65)
    # a bug slipping past the tests
    d += ('<ellipse class="hk" cx="535" cy="44" rx="9" ry="6"/>'
          '<line class="ln" x1="529" y1="38" x2="524" y2="31"/><line class="ln" x1="541" y1="38" x2="546" y2="31"/>'
          '<line class="ln" x1="529" y1="50" x2="524" y2="56"/><line class="ln" x1="541" y1="50" x2="546" y2="56"/>')
    d += b(580, 20, 200, 90, "Shipped", ["with the bugs", "nobody saw"], "bxm")
    # robot with a tall pile of pages
    d += ('<rect class="hz" x="60" y="160" width="60" height="44" rx="8"/>'
          '<circle class="hk" cx="78" cy="180" r="5"/><circle class="hk" cx="102" cy="180" r="5"/>'
          '<line class="ln" x1="90" y1="160" x2="90" y2="146"/><circle class="hz" cx="90" cy="142" r="5"/>'
          '<rect class="hz" x="54" y="210" width="72" height="60" rx="8"/>')
    for i in range(9):
        d += f'<rect class="hz" x="{150 + (i % 2) * 4}" y="{256 - i * 13}" width="70" height="12" rx="2"/>'
    d += t(190, 292, "faster than anyone can read", "sm", "middle")
    # a person reviewing a short pile
    d += _person(400, 190)
    for i in range(2):
        d += f'<rect class="hz" x="430" y="{256 - i * 13}" width="60" height="12" rx="2"/>'
    d += _magnifier(360, 226, 10)
    d += t(420, 292, "a person reads slowly", "sm", "middle")
    # the sure way
    d += b(600, 170, 390, 100, "A formal proof", ["Lean or Dafny can show the code is right,", "but they are hard to use"], "solid")
    d += t(795, 292, "the sure way, rarely taken", "sm", "middle")
    return figure(1000, 305, d,
                  "AI writes hundreds of lines in seconds, tests catch some bugs and miss others, and a bug slips through to shipped code. Below, a robot stands by a tall pile of pages while a person with a magnifier reviews a short pile. On the right, a formal proof in Lean or Dafny could show the code is right but is hard to use.",
                  "AI writes code faster than people can review it. Tests catch only some bugs, and the tools that can prove code right are hard to use.")


def d_same_input():
    b, a, t = kit.box, kit.arrow, kit.text
    d = b(10, 90, 180, 90, "Same prompt", ["temperature 0,", "sent 3 times"], "bx")
    d += a(192, 135, 255, 135)
    d += b(258, 80, 250, 110, "The server", ["batches it with other", "users' requests"], "solid")
    d += a(510, 120, 590, 50) + a(510, 135, 590, 135) + a(510, 150, 590, 220)
    d += b(593, 22, 210, 56, "Run 1", ["\"approve the refund\""], "bx")
    d += b(593, 107, 210, 56, "Run 2", ["\"approve the refund\""], "bx")
    d += b(593, 192, 210, 56, "Run 3", ["\"reject the refund\""], "bxs")
    d += t(383, 230, ["a different batch adds GPU sums", "in a different order: tiny rounding", "changes can flip a word"], "sm", "middle")
    d += _person(905, 110)
    d += t(905, 92, "which one do I audit?", "sm", "middle")
    return figure(1000, 290, d,
                  "The same prompt at temperature 0 is sent three times to a server that batches it with other users' requests. Runs 1 and 2 say approve the refund; run 3 says reject the refund. An auditor asks which one to audit.",
                  "Even at temperature 0, batching and GPU maths can change an LLM's answer between runs, which breaks audits and repeatable tests.")


def d_retrieval():
    b, a, t = kit.box, kit.arrow, kit.text
    d = b(10, 40, 200, 100, "A question", ["\"What was the Q3", "GST for plant B?\""], "bxm")
    d += a(212, 90, 236, 90)
    d += _magnifier(262, 84, 18)
    d += a(296, 90, 330, 90)
    # the fetched list
    d += '<rect class="hz" x="332" y="20" width="250" height="180" rx="10"/>'
    d += t(347, 46, "Top 5 fetched", "bd")
    rows = ["Q3 sales summary", "GST rules, general", "plant A budget", "Q2 GST letter", "B-team org chart"]
    for i, r in enumerate(rows):
        y = 74 + i * 26
        d += t(347, y, f"{i + 1}. {r}", "sm") + _cross(560, y - 5, 5)
    d += b(332, 225, 250, 62, "Say, rank 9: the right one", ["a table of numbers"], "bxm")
    d += a(584, 110, 628, 110)
    d += b(630, 60, 200, 100, "The model", ["answers from the", "wrong text"], "solid")
    d += a(832, 110, 858, 110)
    d += b(860, 60, 130, 100, "An answer", ["wrong, but", "sounds sure"], "bxs")
    # what trips search
    d += t(10, 176, "search slips on:", "sm")
    tags = ["tables", "numbers", "acronyms", "mixed languages"]
    for i, tg in enumerate(tags):
        x, y = 10 + (i % 2) * 150, 192 + (i // 2) * 44
        w = 140
        d += f'<rect class="hz" x="{x}" y="{y}" width="{w}" height="32" rx="14"/>' + t(x + w / 2, y + 21, tg, "sm", "middle")
    return figure(1000, 300, d,
                  "A question about Q3 GST for plant B goes to search. The top 5 fetched passages are all wrong; the right one, a table of numbers, sits at say rank 9. The model answers from the wrong text and sounds sure. Search slips on tables, numbers, acronyms and mixed languages.",
                  "Most wrong RAG answers start with fetching the wrong text. The right passage, often a table or a number, never reaches the model.")


def d_matching():
    b, a, t = kit.box, kit.arrow, kit.text
    cards = [("ACME Ltd., Pune", "sales system", "bx"), ("Acme Limited", "billing system", "bx"),
             ("A.C.M.E. Pvt Ltd", "support system", "bx"), ("Acme Foods, Pune", "a different company!", "bxs")]
    d = ""
    for i, (n, s, k) in enumerate(cards):
        y = 12 + i * 70
        d += b(10, y, 250, 58, n, s, k)
        d += f'<line class="lnd" x1="262" y1="{y + 29}" x2="378" y2="150"/>'
    d += '<circle class="hz" cx="425" cy="150" r="48"/>'
    d += t(425, 146, ["same", "thing?"], "bd", "middle")
    d += a(475, 150, 518, 150)
    d += b(520, 90, 230, 120, "At scale", ["millions of pairs, and", "people still check", "the hard ones"], "solid")
    d += a(752, 150, 800, 150)
    d += _person(835, 110)
    for i in range(10):
        d += f'<rect class="hz" x="{880 + (i % 2) * 5}" y="{190 - i * 12}" width="80" height="11" rx="2"/>'
    d += t(900, 230, "the review queue", "sm", "middle")
    return figure(1000, 300, d,
                  "Four records: ACME Ltd. Pune, Acme Limited and A.C.M.E. Pvt Ltd are the same company in three systems; Acme Foods Pune is a different company. Dashed lines meet at a circle asking: same thing? At scale there are millions of pairs, and a person beside a tall pile still checks the hard ones.",
                  "The same customer, drug or company is spelled differently in every system, and look-alikes are not always the same, so matching still needs people at scale.")


def _dice(cx, cy):
    s = f'<rect class="hz" x="{cx - 28}" y="{cy - 28}" width="56" height="56" rx="9"/>'
    for dx, dy in ((-13, -13), (13, 13), (0, 0), (13, -13), (-13, 13)):
        s += f'<circle class="hk" cx="{cx + dx}" cy="{cy + dy}" r="4"/>'
    return s


def d_privacy():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(125, 22, "THE TRUE COUNT", "lbl", "middle") + t(340, 22, "ADD NOISE", "lbl", "middle") + t(560, 22, "WHAT IS PUBLISHED", "lbl", "middle")
    rows = [(40, ("Say, 1,000,000", "people in a state"), ("About 1,000,030", "still useful"), "bx",
             ["the noise is tiny", "next to the count"]),
            (170, ("Say, 12", "people at one clinic"), ("Could be 0, could be 60", "useless for a decision"), "bxs",
             ["the same noise", "swamps the count"])]
    for y, true, pub, k, note in rows:
        d += b(10, y, 230, 90, true[0], true[1], "bx")
        d += a(242, y + 45, 300, y + 45)
        d += _dice(340, y + 45)
        d += a(380, y + 45, 428, y + 45)
        d += b(430, y, 260, 90, pub[0], pub[1], k)
        d += t(720, y + 40, note, "sm")
    d += t(340, 290, "say, plus or minus 50, so no one person can be picked out", "sm", "middle")
    d += _person(905, 150) + t(905, 140, "hidden, but", "sm", "middle") + t(905, 256, "the number", "sm", "middle") + t(905, 276, "is lost too", "sm", "middle")
    return figure(1000, 300, d,
                  "Two rows. A true count of say 1,000,000 people gets random noise added and is published as about 1,000,030, still useful. A true count of say 12 people at one clinic gets the same noise and could be published as anything from 0 to 60, useless. A person is hidden, but the number is lost too.",
                  "Differential privacy adds random noise so no person can be identified. The noise barely touches big groups but makes small groups' numbers useless.")


def d_data_meaning():
    b, a, t = kit.box, kit.arrow, kit.text
    d = b(10, 110, 150, 80, "Raw orders", "", "bx")
    defs = ["say: includes tax", "say: after refunds", "say: booked, not yet paid"]
    for i, s in enumerate(defs):
        y = 20 + i * 92
        d += a(162, 150, 238, y + 38)
        d += b(240, y, 240, 76, "revenue", s, "bx")
        d += _tick(500, y + 38)
        d += a(515, y + 38, 588, 150)
    d += t(200, 12, "every copy moves correctly", "sm", "middle")
    d += b(590, 95, 190, 110, "Dashboard", ["\"revenue\":", "three numbers"], "solid")
    d += b(590, 222, 190, 66, "Meaning check", "nobody has one", "bxm")
    d += _person(890, 110)
    d += t(890, 92, "which revenue is real?", "sm", "middle")
    return figure(1000, 300, d,
                  "Raw orders flow correctly into three tables, each called revenue: say one includes tax, one is after refunds, one is booked but not yet paid. Each copy gets a tick. All three feed one dashboard that shows three numbers for revenue. A dashed box says there is no meaning check, and a person asks which revenue is real.",
                  "Pipelines move data correctly, yet \"revenue\" can mean three things in three tables, and nothing checks the meaning.")


# ---------------------------------------------------------------- security

def d_memory_unsafe():
    t = kit.text
    d = t(196, 40, "a buffer with 8 slots", "sm", "middle")
    d += '<path class="ln" fill="none" d="M22,52 L22,46 L370,46 L370,52"/>'
    for i in range(8):
        x = 22 + i * 44
        d += f'<rect class="pf pf-bx" x="{x + 3}" y="{63}" width="40" height="50" rx="4"/><rect class="hz" style="fill:none" x="{x}" y="60" width="40" height="50" rx="4"/>'
    d += _pink(378, 60, 86, 50) + t(421, 90, "secret", "sm", "middle")
    d += _pink(470, 60, 96, 50) + t(518, 90, "next step", "sm", "middle")
    d += kit.arrow(22, 140, 560, 140)
    d += t(290, 165, "a write runs past the end, and C does not stop it", "sm", "middle")
    d += t(290, 215, ["most serious C and C++ security bugs", "are memory errors like this"], "tx", "middle")
    # the mountain of old code
    d += '<path class="hz" d="M630,282 L800,52 L990,282 Z"/>'
    d += t(805, 190, ["C and C++:", "billions", "of lines"], "sm", "middle")
    d += _person(575, 200)
    d += '<line class="lnc" x1="591" y1="250" x2="610" y2="280"/><path class="hz" d="M604,276 L618,272 L622,288 Z"/>'
    d += t(600, 28, ["rewrite it all in Rust by hand?", "unaffordable"], "sm")
    return figure(1000, 300, d,
                  "A row of 8 memory slots labelled a buffer, followed by a secret and the program's next step. An arrow shows a write running past the end into the secret and the next step. On the right, a small person with a shovel stands beside a mountain of billions of lines of C and C++, asking: rewrite it all in Rust by hand? Unaffordable.",
                  "C and C++ let a write run past the end of a buffer, which causes most serious security bugs, and there is far too much of that code to rewrite by hand.")


def d_malicious_packages():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(20, 30, "thousands of new packages arrive every day", "tx")
    # the reviewer
    d += _person(560, 40) + _magnifier(530, 70, 10)
    d += t(600, 66, ["one reviewer", "can't open them all"], "sm")
    # the belt
    d += '<rect class="hz" x="20" y="200" width="680" height="22" rx="11"/>'
    for i in range(8):
        d += f'<circle class="hz" cx="{40 + i * 92}" cy="211" r="6"/>'
    parcels = [("numpy", False), ("requests", False), ("reqeusts", True), ("pandas", False), ("popular-lib", True)]
    for i, (n, bad) in enumerate(parcels):
        x = 30 + i * 134
        if bad:
            d += _pink(x, 138, 116, 60)
            d += f'<path class="hk" d="M{x + 30},138 L{x + 36},120 L{x + 44},138 Z"/><path class="hk" d="M{x + 72},138 L{x + 80},120 L{x + 86},138 Z"/>'
        else:
            d += f'<rect class="hz" x="{x}" y="138" width="116" height="60" rx="6"/>'
            d += f'<line class="ln" x1="{x + 58}" y1="138" x2="{x + 58}" y2="150"/>'
        d += t(x + 58, 174, n, "sm", "middle")
    d += t(326, 248, "a look-alike name", "sm", "middle")
    d += t(594, 248, "a hijacked maintainer", "sm", "middle")
    d += a(702, 211, 758, 190)
    d += b(760, 135, 230, 110, "Your build", ["pip install reqeusts:", "one typo, and the", "bad one runs"], "solid")
    return figure(1000, 270, d,
                  "A conveyor belt of packages: numpy, requests, a look-alike called reqeusts with devil horns, pandas, and popular-lib whose maintainer was hijacked, also with horns. One reviewer with a magnifier can't open them all. The belt feeds your build, where one typo installs the bad package.",
                  "Attackers publish look-alike packages and hijack real maintainers, and thousands of new packages a day is far more than people can review.")


def d_ai_vulns():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(10, 18, "FUZZING", "lbl")
    d += b(10, 30, 190, 90, "A fuzzer", ["throws random inputs"], "bx")
    d += a(202, 75, 266, 75)
    d += b(268, 30, 200, 90, "The program", "", "bx")
    d += a(470, 60, 568, 38) + a(470, 90, 568, 110)
    d += b(570, 8, 210, 60, "A crash", "found", "bxs")
    d += b(570, 80, 210, 60, "A logic bug", "no crash, so missed", "bxm")
    d += t(800, 98, ["say, it skips the", "password check"], "sm")
    d += '<line class="lnd" x1="10" y1="162" x2="990" y2="162"/>'
    d += t(10, 188, "AI BUG-FINDING", "lbl")
    d += b(10, 200, 190, 90, "An AI bug-finder", ["reads the code"], "solid")
    d += a(202, 245, 262, 245)
    for i in range(6):
        x, y = 270 + i * 9, 270 - i * 12
        d += f'<rect class="hz" x="{x}" y="{y}" width="110" height="34" rx="4"/>'
    d += t(370, 234, "!", "bd", "middle")
    d += t(340, 316, "say, 50 alarms", "sm", "middle")
    d += a(432, 245, 520, 245)
    d += _person(555, 205)
    d += t(555, 316, "a defender checks each one", "sm", "middle")
    d += a(600, 245, 668, 245)
    d += b(670, 200, 320, 90, "Most are false", ["say, 45 waste a day each;", "the 5 real ones are buried"], "bxs")
    return figure(1000, 330, d,
                  "Top: a fuzzer throws random inputs at a program, finds a crash, but misses a logic bug such as skipping the password check, because it does not crash. Bottom: an AI bug-finder reads the code and raises say 50 alarms; a defender checks each one; most are false and the few real ones are buried.",
                  "Fuzzing finds crashes but not logic bugs. AI finds more, but false alarms eat the defenders' time.")


def d_post_quantum():
    t = kit.text
    d = '<rect class="hz" x="10" y="20" width="600" height="268" rx="16"/>'
    d += t(30, 48, "AN ORGANISATION'S SYSTEMS", "lbl")
    known = ["in code", "in configs", "in libraries", "in vendor tools"]
    for i, lab in enumerate(known):
        cx = 80 + i * 140
        d += _lock(cx, 70) + t(cx, 142, lab, "sm", "middle")
    for i in range(3):
        cx = 80 + i * 140
        d += _lock(cx, 172, dashed=True, mark="?") + t(cx, 244, "not found yet", "sm", "middle")
    d += _person(510, 180) + _magnifier(482, 222, 11)
    d += t(510, 172, "where is it all?", "sm", "middle")
    # the future quantum computer: a chandelier of discs
    cx = 830
    for i, (w, y) in enumerate(((150, 60), (120, 105), (90, 150), (60, 195))):
        d += f'<ellipse class="hz" cx="{cx}" cy="{y}" rx="{w / 2}" ry="13"/>'
        if i < 3:
            d += f'<line class="ln" x1="{cx - w / 2 + 18}" y1="{y + 12}" x2="{cx - w / 2 + 30}" y2="{y + 34}"/><line class="ln" x1="{cx + w / 2 - 18}" y1="{y + 12}" x2="{cx + w / 2 - 30}" y2="{y + 34}"/>'
    d += f'<line class="ln" x1="{cx}" y1="208" x2="{cx}" y2="226"/>'
    d += t(cx, 34, "a future quantum computer", "sm", "middle")
    d += t(cx, 252, ["will break today's", "encryption locks"], "sm", "middle")
    d += '<path class="lnc" fill="none" d="M744,130 L700,112 L712,140 L640,126" marker-end="url(#ar)"/>'
    return figure(1000, 300, d,
                  "A big box of an organisation's systems holds padlocks in code, configs, libraries and vendor tools, plus three dashed padlocks with question marks that have not been found yet. A person with a magnifier asks where it all is. On the right, a future quantum computer sends a lightning bolt: it will break today's encryption locks.",
                  "Future quantum computers will break today's encryption, and most organisations don't even know everywhere they use it.")


def d_identity():
    b, a, t = kit.box, kit.arrow, kit.text
    # laptop with a video call
    d = '<rect class="hz" x="30" y="30" width="240" height="160" rx="8"/><path class="hz" d="M12,190 L288,190 L300,210 L0,210 Z"/>'
    d += '<circle class="pf pf-bx" cx="153" cy="103" r="38"/><circle class="hz" style="fill:none" cx="150" cy="100" r="38"/>'
    d += '<circle class="hk" cx="137" cy="92" r="4"/><circle class="hk" cx="163" cy="92" r="4"/><path class="ln" fill="none" d="M136,114 Q150,124 164,114"/>'
    d += '<path class="lnd" fill="none" d="M104,66 Q150,40 196,66 L198,126 Q150,160 102,126 Z"/>'
    d += t(150, 172, "the boss, on video", "sm", "middle")
    d += t(40, 236, ["dashed: a cloned face", "and voice"], "sm")
    d += b(310, 20, 270, 72, "\"Pay the supplier now\"", ["it's urgent, I'm in a meeting"], "bxs")
    d += '<path class="ln" fill="none" d="M310,70 L272,90"/>'
    d += _person(650, 100)
    d += t(650, 84, "I know that face", "sm", "middle")
    d += a(680, 140, 728, 140)
    d += b(730, 100, 260, 84, "Payment sent", ["to the fraudster"], "solid")
    # phishing
    d += '<path class="ln" fill="none" d="M326,228 L326,252 Q326,270 340,270 Q352,270 352,258"/>'
    d += b(365, 222, 250, 70, "Passwords", ["still typed into fake pages"], "bxm")
    d += a(617, 257, 790, 188)
    return figure(1000, 300, d,
                  "A laptop shows the boss on a video call, but a dashed outline shows the face and voice are cloned. The boss says pay the supplier now, it's urgent. An employee thinks: I know that face. The payment goes to the fraudster. Below, a fishing hook by a box: passwords are still typed into fake pages, which also leads to the payment.",
                  "Seeing and hearing someone is no longer proof: cloned faces and voices pass the \"I recognise them\" check, and passwords still get phished.")


DRAWINGS = {
    "estimating-query-sizes-the-40-year-database": d_query_sizes,
    "keeping-thousands-of-gpus-busy": d_gpus_busy,
    "proving-ai-written-code-is-correct": d_proving_code,
    "same-input-different-llm-answer": d_same_input,
    "retrieval-that-finds-the-right-passage": d_retrieval,
    "matching-records-that-refer-to-the-same": d_matching,
    "useful-analytics-with-privacy-guarantees": d_privacy,
    "data-meaning-not-just-data-movement": d_data_meaning,
    "memory-unsafe-code-everywhere": d_memory_unsafe,
    "malicious-packages-in-software-supply-chains": d_malicious_packages,
    "ai-that-finds-vulnerabilities-before-attackers-do": d_ai_vulns,
    "post-quantum-migration": d_post_quantum,
    "identity-when-voices-and-faces-can-be": d_identity,
}
