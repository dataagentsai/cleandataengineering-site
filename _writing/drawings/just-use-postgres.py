"""Drawings for 'Just use Postgres: the one database your agent needs'. kit, figure, E and ROOT are injected."""
import math


def _drum(x, y, w, h):
    """A database drum outline, top ellipse visible."""
    ry = 16
    return (f'<path class="bx" d="M{x},{y + ry} L{x},{y + h - ry} A{w / 2},{ry} 0 0 0 {x + w},{y + h - ry} '
            f'L{x + w},{y + ry} A{w / 2},{ry} 0 0 0 {x},{y + ry} A{w / 2},{ry} 0 0 0 {x + w},{y + ry}"/>')


def drawing_toolbox():
    t = kit.text
    jobs = ["checkpoints", "memory (pgvector)", "workflows (DBOS)", "queues", "the ledger", "approvals", "audit log"]
    L, top = 160, 232
    d = ""
    for i, job in enumerate(jobs):
        ang = math.radians(165 - i * 25)
        ux, uy = math.cos(ang), -math.sin(ang)
        vx, vy = -uy * 9, ux * 9
        px, py = 380 + i * 40, top + 4
        pts = [(px + vx, py + vy), (px + ux * L + vx, py + uy * L + vy), (px + ux * (L + 22), py + uy * (L + 22)),
               (px + ux * L - vx, py + uy * L - vy), (px - vx, py - vy)]
        d += '<path class="hz" d="M' + " L".join(f"{a:.0f},{b:.0f}" for a, b in pts) + ' Z"/>'
        lx, ly = px + ux * (L + 36), py + uy * (L + 36)
        anchor = "end" if ux < -0.3 else ("start" if ux > 0.3 else "middle")
        d += t(round(lx), round(ly + 5), job, "bd", anchor)
    d += f'<rect class="hz" x="330" y="{top}" width="340" height="84" rx="12"/>'
    d += kit.box(330, top, 340, 84, "PostgreSQL", "one database, one backup, one bill", "solid")
    d += f'<circle class="hz" cx="640" cy="{top + 42}" r="9"/>'
    return figure(1000, 335, d,
                  "A Swiss army knife whose body is PostgreSQL. Seven blades fan out: checkpoints, memory with pgvector, workflows with DBOS, queues, the ledger, approvals and the audit log.",
                  "One Postgres, seven jobs. Each blade is just a table or two.")


def drawing_before_after():
    b, t = kit.box, kit.text
    d = t(240, 22, "BEFORE: SIX STORES", "lbl", "middle") + t(760, 22, "AFTER: ONE POSTGRES", "lbl", "middle")
    d += '<line class="lnd" x1="500" y1="10" x2="500" y2="330"/>'
    stores = [(5, 40, "Redis"), (5, 140, "Vector DB"), (5, 240, "Queue"),
              (345, 40, "Workflow DB"), (345, 140, "Log store"), (345, 240, "App DB")]
    for x, y, name in stores:
        d += b(x, y, 130, 56, name, kind="bxm")
        ex = x + 130 if x < 200 else x
        d += f'<line class="lnd" x1="{ex}" y1="{y + 28}" x2="{240 + (-62 if x < 200 else 62)}" y2="168"/>'
    d += b(178, 140, 124, 56, "Agent", kind="solid")
    d += t(240, 322, "6 logins · 6 backups · 6 bills", "sm", "middle")
    d += b(530, 140, 124, 56, "Agent", kind="solid")
    d += kit.arrow(656, 168, 716, 168)
    d += _drum(720, 40, 260, 260)
    rows = ["checkpoints", "requests (ledger)", "approvals", "escalations", "dbos.* (workflows)", "jobs, memory, audit"]
    d += t(850, 92, "PostgreSQL", "bd", "middle")
    for i, r in enumerate(rows):
        d += t(850, 124 + i * 26, r, "sm", "middle")
    d += t(760, 322, "1 login · 1 backup · 1 bill", "sm", "middle")
    return figure(1000, 340, d,
                  "Left: an agent wired to six separate stores: Redis, a vector database, a queue, a workflow database, a log store and an app database. Right: the same agent with one PostgreSQL holding checkpoints, the ledger, approvals, escalations, the DBOS tables, and jobs, memory and audit.",
                  "Every extra store is another login, backup schedule and bill. One Postgres holds the same jobs as tables.")


def drawing_turn_tables():
    b, t, n = kit.box, kit.text, kit.num
    steps = [("Front door", "read the newest checkpoint; add a delivery row", "checkpoints, requests", "bx"),
             ("Anything waiting?", "a payout or a hand-off still pending?", "approvals, dbos", "bx"),
             ("The model thinks", "writes nothing at all", "no table", "solid"),
             ("Each write tool", "claim a row with the call's key first", "requests", "bxs"),
             ("Save", "insert or update this turn's checkpoint", "checkpoints", "bx"),
             ("Settle", "mark the delivery row answered", "requests", "bx")]
    d = ""
    for i, (s, what, tbl, k) in enumerate(steps):
        y = 20 + i * 62
        d += b(40, y, 230, 48, s, kind=k) + n(30, y + 24, i + 1)
        d += kit.arrow(272, y + 24, 332, y + 24)
        d += t(342, y + 30, what, "tx")
        d += t(980, y + 30, tbl, "sm" if tbl == "no table" else "bd", "end")
    d += t(500, 408, "read once at the start, guard each write in the middle, save once at the end", "sm", "middle")
    return figure(1000, 420, d,
                  "Six steps of one turn and the tables each touches: front door reads checkpoints and adds a row to requests; anything waiting reads approvals and the dbos tables; the model writes nothing; each write tool claims a row in requests; save writes checkpoints; settle updates requests.",
                  "One turn of the claims assistant, by table. Every table is in the same database, claims_agent.")


def drawing_outgrow():
    b, t = kit.box, kit.text
    signs = [("Huge vector collection", "the index no longer fits in memory", "a search service"),
             ("Heavy analytics", "a year of rows, fighting the agent", "the lakehouse"),
             ("Very high write rates", "events faster than one server writes", "an event store")]
    d = ""
    for i, (title, sub, dest) in enumerate(signs):
        cx = 170 + i * 330
        d += f'<path class="zy" d="M{cx},20 L{cx + 48},68 L{cx},116 L{cx - 48},68 Z"/>'
        d += f'<path class="ln" d="M{cx},20 L{cx + 48},68 L{cx},116 L{cx - 48},68 Z"/>'
        d += (f'<line class="lnc" x1="{cx}" y1="44" x2="{cx}" y2="78"/>'
              f'<circle class="hk" cx="{cx}" cy="92" r="4"/>')
        d += f'<line class="lnc" x1="{cx}" y1="116" x2="{cx}" y2="148"/>'
        d += b(cx - 150, 150, 300, 72, title, sub, "bxs")
        d += kit.arrow(cx, 224, cx, 262)
        d += b(cx - 110, 265, 220, 50, "move to " + dest, kind="bxm")
    d += t(500, 345, "move only the job that shows the sign; everything else stays in Postgres", "sm", "middle")
    return figure(1000, 360, d,
                  "Three yellow warning signs. A huge vector collection whose index no longer fits in memory: move to a search service. Heavy analytics fighting the agent: move to the lakehouse. Very high write rates: move to an event store.",
                  "The three signs that a job has outgrown Postgres. No sign, no move.")


DRAWINGS = {"pg-toolbox": drawing_toolbox, "pg-before-after": drawing_before_after,
            "pg-turn-tables": drawing_turn_tables, "pg-outgrow": drawing_outgrow}
