"""Drawings for 'How to learn in the AI era'. Globals kit, figure, E, ROOT are injected."""


def _person(cx, top):
    return (f'<circle class="bx" cx="{cx}" cy="{top}" r="13"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 13}" x2="{cx}" y2="{top + 45}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 45}" x2="{cx - 11}" y2="{top + 68}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 45}" x2="{cx + 12}" y2="{top + 68}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 24}" x2="{cx + 18}" y2="{top + 36}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 24}" x2="{cx - 16}" y2="{top + 36}"/>')


def drawing_learn_two_engineers():
    b, t = kit.box, kit.text
    d = t(500, 22, "same tool, same AI, same six months", "sm", "middle")
    d += '<rect class="hz" x="20" y="40" width="465" height="300" rx="10"/>'
    d += '<rect class="hz" x="515" y="40" width="465" height="300" rx="10"/>'
    d += t(252, 66, "RAHUL", "lbl", "middle") + t(747, 66, "ANANYA", "lbl", "middle")
    d += _person(90, 95) + _person(585, 95)
    d += b(140, 90, 320, 70, "Asks AI to write it", "copies, it runs, moves on", "bxm")
    d += b(635, 90, 320, 70, "Asks AI to explain it", "builds it, then teaches it", "bx")
    d += b(45, 200, 415, 115, "Month six: it breaks", ["he can't tell why;", "he asks the AI again"], "bxs")
    d += b(540, 200, 415, 115, "Month six: it breaks", ["she knows where to look,", "and fixes it in an hour"], "solid")
    return figure(1000, 360, d,
                  "Two engineers with the same tool. Rahul asks AI to write it, copies it and moves on; at month six it breaks and he can't tell why. Ananya asks AI to explain it, builds it and teaches it; at month six she knows where to look and fixes it.",
                  "AI can save you the typing. It can't save you the understanding, and month six always comes.")


def drawing_learn_map():
    b, t = kit.box, kit.text
    d = t(500, 22, "draw the map first; then every new name has a place", "sm", "middle")
    centre = (390, 150, 220, 70)
    d += b(*centre, "Your role", "data engineer, say", "solid")
    spots = [(40, 50, "Data in", "sources, CDC, files"), (370, 40, "Store and shape", "tables, layers, formats"),
             (700, 50, "Serve", "BI, APIs, AI apps"), (40, 250, "Run it", "orchestrate, monitor, cost"),
             (370, 275, "Trust it", "quality, tests, lineage"), (700, 250, "Guard it", "access, privacy")]
    for x, y, title, sub in spots:
        d += b(x, y, 250 if x != 370 else 260, 64, title, sub, "bx")
    for x1, y1, x2, y2 in ((290, 95, 388, 165), (500, 104, 500, 148), (700, 95, 612, 165),
                           (290, 270, 388, 205), (500, 222, 500, 273), (700, 270, 612, 205)):
        d += f'<line class="ln" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>'
    d += b(800, 140, 180, 60, "New tool?", "pin it on a branch", "bxs")
    d += '<path class="lnd" d="M800,170 Q760,150 735,120"/>'
    return figure(1000, 355, d,
                  "A mind map with your role in the middle and six branches: data in, store and shape, serve, run it, trust it, guard it. A note says: new tool? Pin it on a branch.",
                  "Learn the branches once. A new product name then takes a minute to place, not a week to learn.")


def drawing_learn_t_depth():
    b, t = kit.box, kit.text
    d = t(500, 22, "wide and shallow across the map, deep in one place", "sm", "middle")
    d += b(40, 45, 920, 70, "Breadth: the whole map", "5 seconds (what is it?) and 10 minutes (when would I use it?)", "bx")
    d += b(330, 130, 340, 62, "50 minutes", "how it works inside", "bxs")
    d += b(330, 207, 340, 62, "5 hours", "built it, broke it, fixed it", "bxs")
    d += b(330, 284, 340, 62, "Your core", "you can teach it", "solid")
    d += t(170, 230, ["deep only where", "your job lives"], "sm", "middle")
    d += t(830, 230, ["everything else:", "know it exists"], "sm", "middle")
    return figure(1000, 365, d,
                  "A T-shape. The top bar is breadth across the whole map at two depths: 5 seconds (what is it) and 10 minutes (when would I use it). The stem goes down through 50 minutes (how it works inside), 5 hours (built it, broke it, fixed it) to your core, which you can teach.",
                  "Four depths. Most things only need the first two. Your core needs all four.")


def drawing_learn_tutor():
    b, t = kit.box, kit.text
    d = '<rect class="zg" x="20" y="40" width="470" height="285" rx="10"/>'
    d += '<rect class="zr" x="510" y="40" width="470" height="285" rx="10"/>'
    d += t(255, 68, "AI AS A TUTOR", "lbl", "middle") + t(745, 68, "AI AS A GHOSTWRITER", "lbl", "middle")
    tut = ["explain it, then quiz me", "what's wrong with my answer?", "give me a broken one to fix", "what goes wrong in production?"]
    gho = ["write the pipeline for me", "just fix this error", "paste, run, move on"]
    for i, s in enumerate(tut):
        d += b(45, 85 + i * 52, 420, 42, s, "", "bxm")
    for i, s in enumerate(gho):
        d += b(535, 85 + i * 52, 420, 42, s, "", "bxm")
    d += t(255, 312, "you end up able to do it", "bd", "middle")
    d += t(745, 312, "you end up with code you can't explain", "bd", "middle")
    return figure(1000, 340, d,
                  "Two columns. AI as a tutor: explain it then quiz me; what's wrong with my answer; give me a broken one to fix; what goes wrong in production. You end up able to do it. AI as a ghostwriter: write the pipeline for me; just fix this error; paste, run, move on. You end up with code you can't explain.",
                  "The same AI, two ways of asking. Only one of them is learning.")


def drawing_learn_loop():
    b, p = kit.box, kit.path
    d = b(60, 60, 200, 80, "1 See it", "a picture first", "bx")
    d += b(400, 60, 200, 80, "2 Run it", "a simulator; break it", "bx")
    d += b(740, 60, 200, 80, "3 Build it", "a small real project", "bxs")
    d += b(400, 220, 200, 80, "4 Teach it", "write it, explain it", "solid")
    d += kit.arrow(262, 100, 396, 100)
    d += kit.arrow(602, 100, 736, 100)
    d += p("M840,142 Q840,260 604,260")
    d += p("M396,260 Q160,260 160,144")
    d += kit.text(500, 200, "teaching shows the gaps; go round again", "sm", "middle")
    return figure(1000, 320, d,
                  "A loop: see it as a picture; run it in a simulator and break it; build a small real project; teach it by writing or explaining. Teaching shows the gaps, and you go round again.",
                  "See, run, build, teach. Each step tests the one before it.")


DRAWINGS = {"learn-two-engineers": drawing_learn_two_engineers, "learn-map": drawing_learn_map,
            "learn-t-depth": drawing_learn_t_depth, "learn-tutor": drawing_learn_tutor, "learn-loop": drawing_learn_loop}
