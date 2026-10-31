# Drawings for the post "Stop writing pipelines: one metadata-driven ingestion framework for 500 tables".
# kit, figure, E and ROOT are injected by _writing/build.py.


def _page(x, y, tilt):
    """A small script page, drawn as a tilted sheet with code lines."""
    lines = "".join(f'<line class="ln" x1="{x + 8}" y1="{y + 14 + j * 10}" x2="{x + 8 + (30 if j % 2 else 38)}" y2="{y + 14 + j * 10}"/>'
                    for j in range(4))
    return (f'<g transform="rotate({tilt} {x + 27} {y + 30})"><rect class="hz" x="{x}" y="{y}" width="54" height="60" rx="3"/>'
            f'{lines}</g>')


def _person(cx, top):
    return (f'<circle class="bx" cx="{cx}" cy="{top}" r="13"/><line class="lnc" x1="{cx}" y1="{top + 13}" x2="{cx}" y2="{top + 42}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 42}" x2="{cx - 10}" y2="{top + 62}"/><line class="lnc" x1="{cx}" y1="{top + 42}" x2="{cx + 12}" y2="{top + 62}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 24}" x2="{cx + 20}" y2="{top + 14}"/><line class="lnc" x1="{cx}" y1="{top + 24}" x2="{cx - 16}" y2="{top + 32}"/>')


def drawing_many_vs_one():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(220, 28, "before: one pipeline per table", "lbl", "middle")
    d += t(745, 28, "after: one engine reads a table of settings", "lbl", "middle")
    tilts = [-6, 4, -3, 7, 3, -7, 5, -4, -5, 6, -2, 4]
    d += ('<path class="lnd" d="M75,90 Q160,250 260,110 T430,200"/>'
          '<path class="lnd" d="M120,240 Q230,40 330,230"/>')
    for i in range(12):
        col, row = i % 4, i // 4
        d += _page(40 + col * 95 + (row % 2) * 18, 55 + row * 72, tilts[i])
    d += t(220, 290, "500 small programs, 500 ways to break", "sm", "middle")
    d += '<line class="lnd" x1="480" y1="50" x2="480" y2="290"/>'
    # the config table, drawn as a little grid
    d += '<rect class="hz" x="515" y="80" width="160" height="140" rx="4"/>'
    d += '<rect class="pf pf-bxs" x="515" y="80" width="160" height="28" rx="4"/>'
    d += "".join(f'<line class="ln" x1="515" y1="{108 + j * 28}" x2="675" y2="{108 + j * 28}"/>' for j in range(4))
    d += '<line class="ln" x1="580" y1="80" x2="580" y2="220"/>'
    d += t(595, 240, "metadata store", "sm", "middle") + t(595, 258, "one row per table", "sm", "middle")
    d += a(677, 150, 703, 150)
    d += b(705, 95, 130, 110, "Engine", ["one pipeline,", "tested once"], "solid")
    d += a(837, 150, 863, 150)
    d += b(865, 105, 125, 90, "Bronze", "every table", "bx")
    return figure(1000, 305, d,
                  "On the left, twelve small script pages are scattered and tangled with dashed lines, labelled 500 small programs. On the right, a metadata store drawn as a grid with one row per table feeds a single engine, which writes to bronze.",
                  "Hundreds of hand-written pipelines, or one engine that reads what to do from a table.")


def drawing_config_row():
    b, t = kit.box, kit.text
    fields = [("Source", "shop_db, Postgres", "bx"), ("Format", "database table", "bx"),
              ("Load type", "incremental", "solid"), ("Keys", "order_id", "bx"),
              ("Schedule", "every hour", "bx"), ("Watermark column", "updated_at", "bx"),
              ("Schema", "columns and types", "bx"), ("Connection", "kv://shop-db-readonly", "bxs")]
    d = '<rect class="hz" x="5" y="45" width="990" height="245" rx="10"/>'
    d += '<rect class="hz" x="25" y="22" width="150" height="34" rx="6"/>' + t(100, 45, "table: orders", "bd", "middle")
    d += t(985, 38, "one row of settings, edited by pull request", "sm", "end")
    for i, (title, sub, k) in enumerate(fields):
        x = 25 + (i % 4) * 242
        y = 75 + (i // 4) * 105
        d += b(x, y, 222, 85, title, sub, k)
    return figure(1000, 300, d,
                  "One config row for the orders table, drawn as eight boxes: source shop_db Postgres, format database table, load type incremental, keys order_id, schedule every hour, watermark column updated_at, schema columns and types, and connection kv://shop-db-readonly, a secret reference.",
                  "What one row in the metadata store says about one table. The connection is a pointer to a secret, never the secret.")


def drawing_one_run():
    b, a, t = kit.box, kit.arrow, kit.text
    steps = [("Read config", ["merge the tiers,", "take a fingerprint"], "bx"),
             ("Check watermark", ["last good run:", "26 Oct, 09:00"], "bx"),
             ("Extract", ["only rows changed", "after the watermark"], "bx"),
             ("Land the files", ["untouched, in", "batch=b-0912/"], "bx"),
             ("Write to bronze", ["one commit,", "with the batch id"], "solid"),
             ("Update watermark", ["only after step 5", "has succeeded"], "bxs"),
             ("Log the run", ["status, rows,", "fingerprint"], "bx")]
    xs = [15, 260, 505, 750, 750, 505, 260]
    d = ""
    for i, (title, sub, k) in enumerate(steps):
        x = xs[i]
        y = 30 if i < 4 else 195
        d += b(x, y, 200, 100, title, sub, k) + kit.num(x + 6, y + 6, i + 1)
        if i < 3:
            d += a(x + 202, y + 50, x + 243, y + 50)
        elif i == 3:
            d += a(x + 100, y + 102, x + 100, 193)
        elif i < 6:
            d += a(x - 2, y + 50, x - 43, y + 50)
    d += t(120, 230, ["if the job dies", "before step 6,", "nothing is lost and", "nothing doubles"], "sm", "middle")
    return figure(1000, 310, d,
                  "Seven numbered steps in a snake. Top row: read config, check watermark, extract, land the files. Bottom row, right to left: write to bronze in one commit with the batch id, move the watermark only after step 5 succeeds, log the run.",
                  "One run of the engine. The watermark moves only after bronze has the data.")


def drawing_new_table():
    b, a, t, p = kit.box, kit.arrow, kit.text, kit.path
    d = _person(45, 95)
    d += t(500, 26, "adding table 501: no new pipeline, no new code", "sm", "middle")
    boxes = [("A few lines", "of YAML", "bx"), ("Pull request", ["a teammate", "reviews it"], "bx"),
             ("Validator", ["known keys, right", "types, no secrets"], "bxs"),
             ("Metadata store", "one more row", "solid"), ("Next run", "loads it", "bxm")]
    for i, (title, sub, k) in enumerate(boxes):
        x = 95 + i * 180
        d += b(x, 60, 150, 110, title, sub, k)
        if i < 4:
            d += a(x + 152, 115, x + 178, 115)
    d += p("M530,172 Q350,262 172,174", "lnd")
    d += t(350, 252, "fails: fix it and push again", "sm", "middle")
    return figure(1000, 270, d,
                  "A person adds a few lines of YAML, opens a pull request a teammate reviews, a validator checks known keys, right types and no secrets, the loader writes one more row into the metadata store, and the next run loads the table. A dashed arrow from the validator back to the YAML says: fails, fix it and push again.",
                  "Table 501 is a reviewed change to a config file, checked by a machine before it reaches the store.")


DRAWINGS = {"ingest-many-vs-one": drawing_many_vs_one, "ingest-config-row": drawing_config_row,
            "ingest-one-run": drawing_one_run, "ingest-new-table": drawing_new_table}
