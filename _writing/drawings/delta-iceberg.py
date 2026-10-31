"""Drawings for 'Delta, Iceberg, or both? Open table formats are settled'. Globals kit, figure, E, ROOT are injected."""


def _page(x, y, rot=0, w=54, h=70, label="parquet"):
    """A loose page: a sheet with a folded corner and a few text lines."""
    cx, cy = x + w / 2, y + h / 2
    s = (f'<g transform="rotate({rot} {cx} {cy})">'
         f'<path class="hz" d="M{x},{y} L{x + w - 12},{y} L{x + w},{y + 12} L{x + w},{y + h} L{x},{y + h} Z"/>'
         f'<path class="ln" d="M{x + w - 12},{y} L{x + w - 12},{y + 12} L{x + w},{y + 12}"/>')
    for j in range(3):
        s += f'<line class="ln" x1="{x + 8}" y1="{y + 24 + j * 12}" x2="{x + w - 10}" y2="{y + 24 + j * 12}"/>'
    s += '</g>'
    return s


def _reader(cx, y, label):
    """A stick person reading."""
    return (f'<circle class="hz" cx="{cx}" cy="{y}" r="13"/>'
            f'<line class="lnc" x1="{cx}" y1="{y + 13}" x2="{cx}" y2="{y + 44}"/>'
            f'<line class="lnc" x1="{cx}" y1="{y + 44}" x2="{cx - 11}" y2="{y + 62}"/>'
            f'<line class="lnc" x1="{cx}" y1="{y + 44}" x2="{cx + 11}" y2="{y + 62}"/>'
            f'<line class="lnc" x1="{cx}" y1="{y + 24}" x2="{cx + 18}" y2="{y + 18}"/>'
            f'<line class="lnc" x1="{cx}" y1="{y + 24}" x2="{cx - 18}" y2="{y + 18}"/>'
            + kit.text(cx, y + 84, label, "sm", "middle"))


def drawing_otf_binder():
    t = kit.text
    d = t(250, 30, "A FOLDER OF PARQUET FILES", "lbl", "middle")
    d += t(750, 30, "AN OPEN TABLE FORMAT", "lbl", "middle")
    # left: a messy pile of loose pages, one half-torn
    for x, y, r in [(90, 90, -14), (150, 70, 8), (215, 100, -5), (280, 75, 16), (120, 170, 10), (200, 180, -18), (290, 165, 4), (350, 120, -9)]:
        d += _page(x, y, r)
    d += t(250, 290, ["which pages are today's table?", "which were half-written by a crash?"], "sm", "middle")
    # divider
    d += '<line class="lnd" x1="500" y1="50" x2="500" y2="320"/>'
    # right: a binder with rings, a table of contents and neat pages
    d += '<rect class="hz" x="560" y="60" width="380" height="210" rx="10"/>'
    for j in range(3):
        d += f'<circle class="hz" cx="580" cy="{105 + j * 60}" r="9"/>'
    d += kit.box(605, 75, 150, 180, "The log", ["table of contents:", "v1 = files a, b", "v2 = + c, d", "v3 = - b, + e"], "solid")
    for x in [775, 835]:
        d += _page(x, 90, 0, 50, 64) + _page(x + 4, 170, 0, 50, 64)
    d += t(750, 300, ["same Parquet files, plus a list of", "exactly which ones make each version"], "sm", "middle")
    return figure(1000, 335, d, "Left: a messy pile of loose pages labelled a folder of Parquet files, with the questions which pages are today's table and which were half-written by a crash. Right: the same pages neatly held in a ring binder whose first page is a table of contents, the log, listing which files make each version.",
                  "A table format doesn't change the pages. It adds the table of contents.")


def drawing_otf_badges():
    b, t = kit.box, kit.text
    d = t(500, 26, "what the log makes possible on plain Parquet files", "sm", "middle")
    badges = [("Transactions", ["a write fully happens", "or not at all"]),
              ("Time travel", ["read the table", "as it was at v1"]),
              ("Schema changes", ["add a column", "without rewriting"]),
              ("Safe writers", ["two jobs at once,", "no lost rows"])]
    for i, (title, sub) in enumerate(badges):
        x = 20 + i * 245
        cx = x + 107
        # badge ribbon tails
        d += f'<path class="hz" d="M{cx - 30},110 L{cx - 42},160 L{cx - 22},150 L{cx - 12},166 L{cx},115 Z"/>'
        d += f'<path class="hz" d="M{cx + 30},110 L{cx + 42},160 L{cx + 22},150 L{cx + 12},166 L{cx},115 Z"/>'
        d += f'<circle class="pf pf-bxs" cx="{cx}" cy="85" r="42"/><circle class="hz" cx="{cx}" cy="85" r="32"/>'
        d += t(cx, 93, str(i + 1), "bd", "middle")
        d += b(x, 180, 215, 90, title, sub, "bx")
    return figure(1000, 285, d, "Four rosette badges, numbered one to four, each above a box: transactions, a write fully happens or not at all; time travel, read the table as it was at version 1; schema changes, add a column without rewriting; safe writers, two jobs at once with no lost rows.",
                  "The four things a log adds. All four come from one idea: readers trust the list, not the folder.")


def drawing_otf_bookkeeping():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(250, 26, "DELTA LAKE", "lbl", "middle")
    d += t(750, 26, "APACHE ICEBERG", "lbl", "middle")
    # Delta: a row of numbered commits plus a checkpoint, pointing down to data files
    d += b(20, 45, 460, 120, "", "", "solid") + t(250, 76, "the _delta_log folder", "bd", "middle")
    for i, n in enumerate(["000.json", "001.json", "002.json", "010 checkpoint"]):
        w = 86 if i < 3 else 120
        x = 40 + i * 98
        d += f'<rect class="hz" x="{x}" y="95" width="{w}" height="44" rx="4"/>' + t(x + w / 2, 122, n, "sm", "middle")
    d += a(250, 167, 250, 210)
    d += b(100, 212, 300, 66, "Parquet data files", "", "bx")
    d += t(250, 305, ["commit = create the next", "numbered file, all or nothing"], "sm", "middle")
    d += '<line class="lnd" x1="500" y1="40" x2="500" y2="320"/>'
    # Iceberg: catalog pointer to metadata, manifests, data
    d += b(530, 45, 200, 60, "Catalog", "points to current", "bxs")
    d += b(780, 45, 200, 60, "Metadata file", "this version", "solid")
    d += a(732, 75, 778, 75)
    d += b(780, 128, 200, 52, "Manifests", "lists of files", "solid")
    d += a(880, 107, 880, 126)
    d += b(780, 212, 200, 66, "Parquet data files", "", "bx")
    d += a(880, 182, 880, 210)
    d += t(630, 205, ["commit = the catalog", "swaps its pointer", "to a new metadata file"], "sm", "middle")
    return figure(1000, 330, d, "Left, Delta Lake: a _delta_log folder of numbered JSON commits and a checkpoint every ten, pointing to Parquet data files; a commit means creating the next numbered file. Right, Apache Iceberg: a catalog points to the current metadata file, which points to manifests, which point to Parquet data files; a commit means the catalog swaps its pointer.",
                  "Same pages underneath. Delta keeps the table of contents in a folder; Iceberg keeps it in a tree, with a catalog holding the bookmark.")


def drawing_otf_read_both():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(500, 26, "one copy of the data, two kinds of readers", "sm", "middle")
    # the one writer
    d += b(20, 120, 160, 80, "One writer", "e.g. a Spark job", "bx")
    d += a(182, 160, 228, 160)
    # the data with two tables of contents
    d += b(230, 55, 360, 228, "", "", "bxm")
    d += t(410, 85, "the same Parquet files", "bd", "middle")
    for i in range(5):
        d += _page(260 + i * 62, 105, 0, 46, 58)
    d += b(250, 180, 150, 76, "Delta log", "", "solid")
    d += b(420, 180, 150, 76, ["Iceberg", "metadata"], "", "solid")
    # catalog
    d += b(625, 120, 150, 80, "Catalog", ["Iceberg REST", "interface"], "bxs")
    d += a(592, 215, 640, 202)
    # readers
    d += a(777, 140, 830, 105)
    d += a(777, 180, 830, 225)
    d += _reader(860, 60, "Iceberg engine")
    d += _reader(860, 190, "another engine")
    d += t(410, 306, ["UniForm: Delta writes the Iceberg metadata too", "no second copy, no nightly sync job"], "sm", "middle")
    return figure(1000, 340, d, "One writer writes a single set of Parquet files that carries both a Delta log and Iceberg metadata. A catalog with an Iceberg REST interface serves the table, and two stick-figure readers, different engines, read it through the catalog.",
                  "Read both: one set of files, two tables of contents, and a catalog that tells every engine where to look.")


DRAWINGS = {
    "otf-binder": drawing_otf_binder,
    "otf-badges": drawing_otf_badges,
    "otf-bookkeeping": drawing_otf_bookkeeping,
    "otf-read-both": drawing_otf_read_both,
}
