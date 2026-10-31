"""Drawings for 'DBOS vs Temporal: durable agents without the drama'. kit, figure, E and ROOT are injected."""


def _person(cx, top):
    """A small walking stick person; head centre at (cx, top + 13)."""
    return (f'<circle class="bx" cx="{cx}" cy="{top + 13}" r="13"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 26}" x2="{cx}" y2="{top + 58}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 58}" x2="{cx - 13}" y2="{top + 80}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 58}" x2="{cx + 13}" y2="{top + 80}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 36}" x2="{cx - 16}" y2="{top + 50}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 36}" x2="{cx + 16}" y2="{top + 50}"/>')


def _flag(x, ground):
    """A save-point flag: pole from the ground up 100 px, a pennant at the top."""
    top = ground - 100
    return (f'<line class="lnc" x1="{x}" y1="{ground}" x2="{x}" y2="{top}"/>'
            f'<path class="hz" d="M{x},{top} L{x + 52},{top + 16} L{x},{top + 32} Z"/>'
            f'<circle class="hk" cx="{x}" cy="{top}" r="5"/>')


def _drum(x, y, w, h):
    """A database drum outline, top ellipse visible."""
    ry = 16
    return (f'<path class="bx" d="M{x},{y + ry} L{x},{y + h - ry} A{w / 2},{ry} 0 0 0 {x + w},{y + h - ry} '
            f'L{x + w},{y + ry} A{w / 2},{ry} 0 0 0 {x},{y + ry} A{w / 2},{ry} 0 0 0 {x + w},{y + ry}"/>')


def drawing_save_point():
    t = kit.text
    g = 250
    d = f'<path class="ln" d="M20,{g} Q260,{g - 6} 500,{g} T980,{g}"/>'
    for i, x in enumerate([120, 330, 540]):
        d += _flag(x, g)
        d += t(x, g + 26, f"step {i + 1} saved", "sm", "middle")
    # the player, walking on past the last save
    d += _person(680, g - 82)
    # the crash: a lightning bolt
    d += '<path class="hz" d="M842,110 L808,182 L834,182 L812,244 L872,160 L844,160 L866,110 Z"/>'
    d += t(890, 160, "crash!", "bd")
    d += t(890, 184, ["restart,", "deploy"], "sm")
    # reload: back to the last flag
    d += kit.path("M840,100 Q700,20 566,128", "lnd")
    d += t(705, 40, "reload from the last save, carry on", "sm", "middle")
    d += t(330, g + 50, "finished steps are never played again; they hand back their saved result", "sm", "middle")
    return figure(1000, 315, d,
                  "A video game path with three save-point flags marked step 1, 2 and 3 saved. A stick person walks on past the third flag and is hit by a lightning bolt labelled crash. A dashed arrow loops back from the crash to the third flag: reload from the last save and carry on.",
                  "Durable execution is a save point after every step. A crash costs you the step in progress, never the whole task.")


def drawing_two_shapes():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(250, 26, "DBOS: A LIBRARY IN YOUR APP", "lbl", "middle")
    d += t(750, 26, "TEMPORAL: A SEPARATE SERVICE", "lbl", "middle")
    d += '<line class="lnd" x1="500" y1="12" x2="500" y2="330"/>'
    # left: the app holds DBOS, writes to its own Postgres
    d += '<rect class="hz" x="20" y="45" width="270" height="235" rx="14"/>'
    d += t(155, 72, "your app", "bd", "middle")
    d += b(40, 88, 230, 64, "your agent code", kind="bx")
    d += b(40, 170, 230, 92, "DBOS library", ["@DBOS.workflow()", "@DBOS.step()"], "solid")
    d += a(292, 216, 340, 216)
    d += t(316, 200, "saves", "sm", "middle")
    d += _drum(345, 120, 140, 160)
    d += t(415, 196, "your", "bd", "middle") + t(415, 220, "Postgres", "bd", "middle")
    d += t(415, 246, "dbos tables", "sm", "middle")
    d += t(250, 318, "no new server: one process, one database you already run", "sm", "middle")
    # right: workers in the app poll a separate cluster
    d += '<rect class="hz" x="515" y="45" width="200" height="235" rx="14"/>'
    d += t(615, 72, "your app", "bd", "middle")
    d += b(530, 88, 170, 64, "agent code", kind="bx")
    d += b(530, 170, 170, 92, "workers", ["workflows and", "activities"], "bx")
    d += b(782, 60, 198, 74, "its own database", "and search index", "bxm")
    d += a(881, 168, 881, 138)
    d += b(782, 170, 198, 92, "Temporal cluster", ["keeps each run's", "event history"], "solid")
    d += a(717, 200, 779, 200)
    d += t(748, 191, "polls", "sm", "middle")
    d += a(779, 234, 717, 234)
    d += t(748, 256, "results", "sm", "middle")
    d += t(750, 318, "a cluster you run, or Temporal Cloud runs it for you", "sm", "middle")
    return figure(1000, 335, d,
                  "Left: DBOS. Your app holds your agent code and the DBOS library with its workflow and step decorators, and saves to your own Postgres. Right: Temporal. Your app holds agent code and workers, which poll a separate Temporal cluster that keeps each run's event history in its own database and search index.",
                  "Same promise, two shapes. DBOS lives inside your app and your database; Temporal is a service your workers talk to.")


def drawing_payout_wait():
    b, a, t, n = kit.box, kit.arrow, kit.text, kit.num
    d = ""
    rows = [(66, "DBOS", ("Step: check", ["₹30,000 > ₹25,000"]), ("Wait for a message", ["DBOS.recv(),", "no thread held"]),
             ("Approve arrives", ["Asha: DBOS.send()"]), ("Step: pay", ["once, by its key"]),
             "the wait is one row in your Postgres"),
            (240, "TEMPORAL", ("Activity: check", ["runs on a worker"]), ("Wait for a signal", ["workflow code,", "nothing running"]),
             ("Signal arrives", ["Asha: Approve"]), ("Activity: pay", ["once, by its key"]),
             "the wait is events in the cluster's history")]
    for y, name, s1, s2, s3, s4, foot in rows:
        d += t(20, y - 26, name, "lbl")
        d += b(20, y, 190, 84, s1[0], s1[1], "bx") + n(32, y, 1)
        d += a(212, y + 42, 252, y + 42)
        d += b(255, y, 200, 84, s2[0], s2[1], "solid") + n(267, y, 2)
        d += f'<line class="lnd" x1="458" y1="{y + 42}" x2="596" y2="{y + 42}"/>'
        d += t(527, y + 32, "two days", "sm", "middle")
        d += b(600, y, 180, 84, s3[0], s3[1], "bxm") + n(612, y, 3)
        d += a(782, y + 42, 812, y + 42)
        d += b(815, y, 165, 84, s4[0], s4[1], "bxs") + n(827, y, 4)
        d += t(527, y + 112, foot, "sm", "middle")
    return figure(1000, 370, d,
                  "Two rows for one ₹30,000 payout. DBOS: a step checks the amount against ₹25,000, the workflow waits for a message with DBOS.recv and holds no thread, two days later Asha's approval arrives with DBOS.send, and a step pays once. Temporal: an activity checks, workflow code waits for a signal, the signal arrives, an activity pays once.",
                  "The same payout in both. The story is identical; only where the wait is written down differs.")


def drawing_decide():
    b, a, t = kit.box, kit.arrow, kit.text
    d = ""
    d += b(20, 30, 280, 104, ["Does a task wait,", "or outlive a request?"], kind="bxs")
    d += a(302, 82, 357, 82, "yes")
    d += b(360, 30, 280, 104, ["Many languages, huge", "volume, long undos?"], kind="bxs")
    d += a(642, 82, 697, 82, "no")
    d += b(700, 30, 280, 104, ["Already run", "Postgres?"], kind="bxs")
    d += a(160, 136, 160, 210, "no", lx=172, ly=178, anchor="start")
    d += a(500, 136, 500, 210, "yes", lx=512, ly=178, anchor="start")
    d += a(840, 136, 840, 210, "yes", lx=852, ly=178, anchor="start")
    d += b(20, 213, 280, 96, "Neither", ["an idempotency key", "and a retry"], "bxm")
    d += b(360, 213, 280, 96, "Temporal", ["Cloud, unless a team", "will run the cluster"], "solid")
    d += b(700, 213, 280, 96, "DBOS", ["a library and a few", "tables in your Postgres"], "solid")
    d += t(980, 340, "no Postgres yet? a managed one is often smaller than a cluster", "sm", "end")
    return figure(1000, 355, d,
                  "Three questions in a row. Does a task wait or outlive a request? No leads to neither: an idempotency key and a retry. Yes leads to: many languages, huge volume, long undo chains? Yes leads to Temporal. No leads to: already run Postgres? Yes leads to DBOS.",
                  "Three questions, asked in order. Most agent teams stop at the first one.")


DRAWINGS = {
    "dur-save-point": drawing_save_point,
    "dur-two-shapes": drawing_two_shapes,
    "dur-payout-wait": drawing_payout_wait,
    "dur-decide": drawing_decide,
}
