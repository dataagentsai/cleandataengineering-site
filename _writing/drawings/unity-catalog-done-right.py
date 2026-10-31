"""Drawings for 'Unity Catalog done right: one governance model for data and AI'.
kit, figure, E and ROOT arrive as globals from build.py."""


def _person(cx, top):
    """A small stick person; top is the y of the head's centre."""
    return (f'<circle class="bx" cx="{cx}" cy="{top}" r="13"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 13}" x2="{cx}" y2="{top + 42}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 42}" x2="{cx - 11}" y2="{top + 62}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 42}" x2="{cx + 11}" y2="{top + 62}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 22}" x2="{cx - 18}" y2="{top + 10}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 22}" x2="{cx + 18}" y2="{top + 10}"/>')


def _bookcase(x, y, label):
    """A bookcase 150 wide, 170 tall, with three shelves of books."""
    d = f'<rect class="hz" x="{x}" y="{y}" width="150" height="170" rx="6"/>'
    for s in range(3):
        sy = y + 52 + s * 55
        d += f'<line class="ln" x1="{x}" y1="{sy}" x2="{x + 150}" y2="{sy}"/>'
        for j in range(6):
            h = 30 + (j * 7 + s * 5) % 12
            k = "pf pf-bxs" if (j + s) % 3 else "pf pf-bx"
            d += f'<rect class="{k}" x="{x + 12 + j * 21}" y="{sy - h}" width="14" height="{h}" rx="2"/>'
            d += f'<rect class="hz" x="{x + 12 + j * 21}" y="{sy - h}" width="14" height="{h}" rx="2" style="fill:none"/>'
    d += kit.text(x + 75, y + 195, label, "sm", "middle")
    return d


def drawing_uc_library():
    t = kit.text
    # the building: roof and walls
    d = '<path class="hz" d="M40,110 L330,40 L620,110 Z"/>'
    d += t(330, 95, "the building = a catalog", "bd", "middle")
    d += '<rect class="hz" x="55" y="110" width="550" height="270" rx="6"/>'
    d += _bookcase(85, 135, "schema: bronze")
    d += _bookcase(255, 135, "schema: silver")
    d += _bookcase(425, 135, "schema: gold")
    # the librarian at a desk, checking a card
    d += _person(790, 150)
    d += '<rect class="hz" x="700" y="205" width="180" height="22" rx="4"/>'
    d += '<line class="ln" x1="715" y1="227" x2="715" y2="295"/><line class="ln" x1="865" y1="227" x2="865" y2="295"/>'
    d += '<rect class="pf pf-bxs" x="820" y="152" width="74" height="46" rx="4"/>'
    d += '<rect class="hz" x="820" y="152" width="74" height="46" rx="4" style="fill:none"/>'
    d += t(857, 172, "card:", "sm", "middle") + t(857, 190, "finance", "sm", "middle")
    d += kit.box(665, 315, 320, 70, "The librarian", "checks your card: the grants", "solid")
    d += t(790, 40, ["a book = a table, view,", "volume, function or model"], "sm", "middle")
    return figure(1000, 400, d,
                  "A library building labelled 'the building is a catalog'. Inside are three bookcases labelled schema bronze, schema silver and schema gold, each full of books. A note says a book is a table, view, volume, function or model. On the right a librarian stands at a desk holding a card that says finance, labelled 'checks your card: the grants'.",
                  "Unity Catalog as a library. Every book has an address of three parts: building, bookcase, book.")


def drawing_uc_layout():
    b, t = kit.box, kit.text
    d = t(500, 24, "one catalog per environment, one schema per layer", "sm", "middle")
    envs = [("dev", "bxm"), ("test", "bx"), ("prod", "solid")]
    for i, (env, k) in enumerate(envs):
        x = 20 + i * 330
        d += f'<rect class="hz" x="{x}" y="45" width="300" height="290" rx="14" style="fill:none"/>'
        d += t(x + 150, 75, f"catalog: {env}", "bd", "middle")
        for j, (lay, lk) in enumerate([("bronze", "bx"), ("silver", "bx"), ("gold", "bxs")]):
            d += b(x + 40, 92 + j * 78, 220, 60, lay, "", lk if env != "dev" else "bxm")
    d += b(300, 355, 400, 60, "prod.gold.daily_sales", "catalog . schema . table", "bxs")
    d += t(150, 390, ["or one catalog", "per domain: sales,", "finance, hr"], "sm", "middle")
    d += t(860, 390, ["jobs read and write", "only their own", "environment"], "sm", "middle")
    return figure(1000, 455, d,
                  "Three catalogs side by side: dev, test and prod. Each holds three schemas: bronze, silver and gold. Below, a full name reads prod.gold.daily_sales, which is catalog, schema, table. Notes say you can instead use one catalog per domain such as sales, finance and HR, and that jobs read and write only their own environment.",
                  "A layout most teams can live with. The full name of a table tells you where it lives and how far it has travelled.")


def drawing_uc_grants_flow():
    b, a, t = kit.box, kit.arrow, kit.text
    # a group of three people
    d = ""
    for i, cx in enumerate([70, 120, 170]):
        d += _person(cx, 70 + (i % 2) * 6)
    d += t(120, 175, "group: finance_analysts", "bd", "middle")
    d += t(120, 197, "Priya, Arjun, Meera", "sm", "middle")
    d += a(235, 110, 375, 110, "one grant", ly=98)
    d += t(305, 135, "SELECT", "sm", "middle")
    d += b(380, 60, 300, 100, "Schema: prod.gold", "the grant sits here, once", "solid")
    tables = [(270, "daily_sales", "bx"), (480, "customers", "bx"), (690, "store_targets", "bxm")]
    for x, name, k in tables:
        d += a(530, 162, x + 95, 258)
        d += b(x, 260, 190, 70, name, "inherits it" if k == "bx" else "added next month", k)
        d += f'<path class="lnc" d="M{x + 162},{290} l7,8 l13,-16"/>'
    d += t(870, 110, ["a new person joins?", "add them to the group.", "a new table? it", "inherits the grant."], "sm", "middle")
    return figure(1000, 350, d,
                  "Three stick people form the group finance_analysts: Priya, Arjun and Meera. One SELECT grant goes from the group to the schema prod.gold. Arrows flow down to three tables, daily_sales, customers and store_targets, each ticked. The last one, added next month, also inherits the grant.",
                  "Grant once, high up, to a group. Everything below inherits it, including tables that do not exist yet.")


def _mini_table(x, y, rows, highlight=None):
    """A small grid of cells; rows is a list of 3-tuples. First row is the header."""
    widths = [120, 130, 110]
    d = ""
    for r, row in enumerate(rows):
        cx = x
        for c, cell in enumerate(row):
            k = "pf pf-bxs" if r == 0 else ("pf pf-solid" if highlight == c and r > 0 else "")
            if k:
                d += f'<rect class="{k}" x="{cx}" y="{y + r * 34}" width="{widths[c]}" height="34"/>'
            d += f'<rect class="hz" x="{cx}" y="{y + r * 34}" width="{widths[c]}" height="34" style="fill:none"/>'
            d += kit.text(cx + widths[c] / 2, y + r * 34 + 23, cell, "bd" if r == 0 else "tx", "middle")
            cx += widths[c]
    return d


def drawing_uc_masks():
    b, a, t = kit.box, kit.arrow, kit.text
    d = b(300, 15, 400, 90, "One table: prod.silver.customers",
          ["mask: phone shown only to support", "filter: analysts see their own state"], "solid")
    d += a(420, 107, 250, 150) + a(580, 107, 750, 150)
    # Priya, support
    d += _person(40, 175) + t(40, 265, ["Priya,", "support"], "sm", "middle")
    d += _mini_table(85, 150, [("name", "phone", "state"), ("Ravi K", "98450 12345", "KA"),
                               ("Asha M", "99000 54321", "TN"), ("Dev S", "98860 11111", "KA")])
    # Arjun, analyst in Karnataka
    d += _mini_table(530, 150, [("name", "phone", "state"), ("Ravi K", "*****", "KA"),
                                ("Dev S", "*****", "KA")], highlight=1)
    d += _person(950, 175) + t(950, 265, ["Arjun,", "analyst, KA"], "sm", "middle")
    d += t(705, 275, "Asha's row is filtered out; phones are masked", "sm", "middle")
    d += t(245, 305, "sees every row, phones in full", "sm", "middle")
    return figure(1000, 320, d,
                  "One table, prod.silver.customers, carries a mask on phone for support only and a row filter by state for analysts. Priya in support sees three rows with full phone numbers. Arjun, an analyst in Karnataka, sees only the two Karnataka rows, with the phone column shown as stars.",
                  "Same table, same query, two answers. The rule lives on the table, so every tool that reads it obeys.")


def drawing_uc_one_roof():
    b, a, t = kit.box, kit.arrow, kit.text
    d = '<path class="hz" d="M120,120 L500,40 L880,120 Z"/>'
    d += t(500, 103, "Unity Catalog", "bd", "middle")
    d += b(140, 135, 720, 55, "same grants, same lineage, same tags, same audit log", "", "bxs")
    things = [(140, "Tables, views", "the data"), (325, "Models", ["registered, with", "versions"]),
              (510, "Functions", ["tools an agent", "may call"]), (695, "Metric views", ["one meaning", "per number"])]
    for x, title, sub in things:
        d += b(x, 210, 165, 95, title, sub, "solid" if title == "Functions" else "bx")
    d += f'<rect class="hz" x="120" y="120" width="760" height="200" rx="6" style="fill:none"/>'
    # readers come in through the front
    readers = [(140, "An analyst"), (400, "A dashboard"), (660, "An agent")]
    for x, name in readers:
        d += b(x, 375, 200, 55, name, "", "bxm")
        d += a(x + 100, 373, x + 100, 324)
    # the bypass, crossed out
    d += kit.path("M902,402 Q985,360 884,250", "lnd")
    d += '<line class="lnc" x1="925" y1="328" x2="955" y2="358"/><line class="lnc" x1="955" y1="328" x2="925" y2="358"/>'
    d += t(950, 445, ["own key, around", "the catalog: no"], "sm", "middle")
    return figure(1000, 470, d,
                  "A house roof labelled Unity Catalog covers four boxes: tables and views, models, functions that an agent may call, and metric views. A strip under the roof says same grants, same lineage, same tags, same audit log. An analyst, a dashboard and an agent all enter from below. A dashed path from outside, an agent with its own key going straight to storage, is crossed out.",
                  "Data and AI under one roof. Whoever or whatever asks, the same rules answer.")


DRAWINGS = {"uc-library": drawing_uc_library, "uc-layout": drawing_uc_layout, "uc-grants-flow": drawing_uc_grants_flow,
            "uc-masks": drawing_uc_masks, "uc-one-roof": drawing_uc_one_roof}
