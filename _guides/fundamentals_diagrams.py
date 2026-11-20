"""Inline SVG pictures for the fundamentals pages. Each function returns (svg, caption).

FIGS maps page slug -> section id -> list of functions; fundamentals.py places them under the
section's intro, before the table. Illustrative drawings: shapes and proportions teach, numbers
are orders of magnitude, and captions say so where it matters.
"""
import sys
from html import escape as E
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_paths"))
from diagrams import FILL, arrow, box, text  # noqa: E402
from diagrams import svg as _svg  # noqa: E402


def svg(w, h, body, label):
    """diagrams.svg with bigger box text so it stays readable at page width."""
    return _svg(w, h, body.replace('font-size="19"', 'font-size="22"').replace('font-size="14"', 'font-size="16.5"'), label)

INK = "#1F1F1F"


def rect(x, y, w, h, fill="white", stroke=INK, sw=1.4, rx=6, op=1):
    f = FILL.get(fill, fill)
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{f}" stroke="{stroke}" stroke-width="{sw}" opacity="{op}"/>'


def t(x, y, s, size=15, anchor="middle", fill="#333", bold=False):
    w = ' font-weight="700"' if bold else ""
    size = round(size * 1.18, 1)
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{fill}"{w}>{E(s)}</text>'


# ------------------------------------------------------------------ performance
def perf_ladder():
    rows = [("CPU cache", 0.5, "nanoseconds", "mint"), ("Memory", 2, "~100 ns", "mint"), ("Local SSD / disk cache", 5, "~100 µs", "butter"),
            ("Object storage, same region", 7.3, "~10-50 ms to first byte", "butter"), ("Another service or API call", 8, "ms to seconds, per call", "rose"),
            ("Another region or cloud", 8.5, "100+ ms and egress fees", "rose"), ("A human approving something", 13, "hours to days", "rose")]
    b = t(10, 22, "Longer bar = slower to reach one piece of data (log scale: each tick is 10x)", 15, "start", "#555")
    y = 40
    for name, lg, lab, f in rows:
        w = max(8, lg * 44)
        b += t(250, y + 21, name, 15, "end", INK) + rect(262, y, w, 28, f) + t(262 + w + 8, y + 20, lab, 13.5, "start", "#555")
        y += 38
    return svg(940, y + 6, b, "Bars showing how much slower each place to keep data is, from memory to a human."), \
        "The data physics ladder. Moving down a row is roughly 10 to 1,000 times slower. Orders of magnitude to build intuition, not benchmarks."


def perf_buckets():
    segs = [("wait", 70, "grey"), ("read", 220, "peri"), ("shuffle", 190, "butter"), ("compute", 90, "mint"), ("write", 60, "rose")]
    after = [("wait", 70, "grey"), ("read", 40, "peri"), ("shuffle", 190, "butter"), ("compute", 90, "mint"), ("write", 60, "rose")]
    b = ""
    for label, row, y in (("A slow job", segs, 40), ("Same job after fixing the biggest bucket (read)", after, 130)):
        b += t(10, y - 10, label, 16, "start", INK, True)
        x = 10
        for n, w, f in row:
            b += rect(x, y, w, 44, f) + t(x + w / 2, y + 28, n if w > 45 else "", 14.5, "middle", INK)
            x += w
        b += t(x + 10, y + 28, f"{x - 10} units", 13.5, "start", "#555")
    b += t(10, 214, "Fix the dominant bucket first. Polishing a small one barely moves the total.", 15, "start", "#555")
    return svg(940, 226, b, "Two bars splitting a job into wait, read, shuffle, compute and write; the second has a much smaller read."), \
        "Where the time goes: find the biggest bucket before tuning anything. Illustrative proportions."


def perf_rowcol():
    b = ""
    cols = ["id", "date", "status", "amount"]
    for k, (title, x0) in enumerate((("Row storage: a row sits together", 10), ("Column storage: a column sits together", 480))):
        b += t(x0, 26, title, 15.5, "start", INK, True)
        for r in range(5):
            for c in range(4):
                hot = (c == 3)
                if k == 0:
                    fill = "rose" if hot else "white"
                    xx = x0 + c * 56
                    yy = 44 + r * 34
                else:
                    fill = "mint" if hot else "white"
                    xx = x0 + c * 56
                    yy = 44 + r * 34
                op = 1 if (k == 0 or hot) else 0.45
                b += rect(xx, yy, 52, 28, fill, op=op)
        for c, n in enumerate(cols):
            b += t(x0 + c * 56 + 26, 226, n, 12.5, "middle", "#555")
    b += t(10, 256, "Total of amount: reads every cell", 14.5, "start", "#555")
    b += t(480, 256, "Total of amount: reads one column", 14.5, "start", "#555")
    return svg(940, 270, b, "A grid read row by row versus column by column, highlighting the one column needed."), \
        "Why analytics uses column storage: a query about one column reads one column."


def perf_skip():
    b = ""
    labels = [("Random layout", 10, ["Jan-Dec", "Jan-Dec", "Jan-Dec", "Jan-Dec"], [True] * 4),
              ("Clustered by date", 480, ["Jan-Mar", "Apr-Jun", "Jul-Sep", "Oct-Dec"], [True, False, False, False])]
    for title, x0, rng, hit in labels:
        b += t(x0, 26, title, 15.5, "start", INK, True)
        for i, (r, h) in enumerate(zip(rng, hit)):
            x = x0 + i * 112
            b += rect(x, 44, 100, 74, "mint" if h else "grey", op=1 if h else 0.5)
            b += t(x + 50, 74, f"file {i + 1}", 14, "middle", INK) + t(x + 50, 100, r, 12, "middle", "#555")
        b += t(x0, 144, "Query: WHERE month = Feb", 14.5, "start", "#555")
    b += t(10, 168, "All 4 files could hold Feb: all opened.", 14.5, "start", INK)
    b += t(480, 168, "Only file 1 can hold Feb: 3 skipped.", 14.5, "start", INK)
    return svg(940, 184, b, "Four files each showing their value range; with random layout all are read, with clustering only one."), \
        "File skipping: each file records its min and max. Clustering makes those ranges tight so the engine can skip files. Partitioning, Z-order and liquid clustering are different ways to get this."


def perf_cluster():
    b = box(340, 12, 260, 60, "Driver", "plans and schedules", "butter")
    for i in range(3):
        x = 40 + i * 300
        b += arrow(470, 72, x + 110, 118)
        b += box(x, 120, 220, 56, f"Executor {i + 1}", "", "peri")
        for k in range(3):
            b += rect(x + 12 + k * 66, 156 + 0, 58, 0, "white")
        b += "".join(rect(x + 14 + k * 68, 190, 58, 26, "mint") + t(x + 43 + k * 68, 208, "task", 12.5, "middle", INK) for k in range(3))
    b += t(10, 244, "One task per partition. Too few leave cores idle; too many drown in start-up cost.", 15, "start", "#555")
    return svg(940, 258, b, "A driver coordinating three executors, each running several tasks."), \
        "Driver, executors and tasks. The driver coordinates; executors do the work in parallel, one task per partition per core."


def perf_shuffle():
    b = t(10, 24, "Narrow step: stays inside a partition", 15.5, "start", INK, True)
    for i in range(3):
        y = 40 + i * 36
        b += rect(10, y, 90, 26, "peri") + arrow(102, y + 13, 190, y + 13) + rect(192, y, 90, 26, "mint")
    b += t(490, 24, "Wide step (shuffle): all to all", 15.5, "start", INK, True)
    for i in range(3):
        y = 40 + i * 36
        b += rect(490, y, 90, 26, "peri") + rect(800, y, 90, 26, "butter")
    for i in range(3):
        for j in range(3):
            b += f'<line x1="582" y1="{53 + i * 36}" x2="798" y2="{53 + j * 36}" stroke="{INK}" stroke-width="1" opacity="0.45"/>'
    b += t(10, 166, "Filter, select, map", 14.5, "start", "#555") + t(490, 166, "Join, group-by, sort: data crosses the network", 14.5, "start", "#555")
    return svg(940, 180, b, "Narrow steps keep each partition separate; a shuffle connects every partition to every other."), \
        "Why a shuffle is the expensive step: all-to-all movement across the network. Filter before it, not after."


def perf_gold():
    b = t(10, 24, "Without a gold object", 15.5, "start", INK, True) + t(490, 24, "With a gold object", 15.5, "start", INK, True)
    b += rect(10, 44, 120, 60, "bronze") + t(70, 80, "raw tables", 14.5, "middle", INK)
    for i in range(4):
        b += arrow(132, 74, 230, 50 + i * 18) + rect(232, 38 + i * 18, 120, 14, "rose") + t(292, 49 + i * 18, "same heavy query", 11, "middle", INK)
    b += t(10, 134, "Every viewer pays the full scan and join cost.", 14.5, "start", "#555")
    b += rect(490, 44, 100, 60, "bronze") + t(540, 80, "raw tables", 14.5, "middle", INK)
    b += arrow(592, 74, 640, 74, "once") + rect(642, 44, 110, 60, "gold") + t(697, 80, "gold table", 14.5, "middle", INK)
    for i in range(4):
        b += arrow(754, 74, 820, 50 + i * 18) + rect(822, 44 + i * 18, 100, 12, "mint") + t(872, 54 + i * 18, "cheap read", 11, "middle", INK)
    b += t(490, 134, "Pay once at load time; every read is small and fast.", 14.5, "start", "#555")
    return svg(940, 148, b, "Many heavy queries on raw tables versus one precomputed gold table serving cheap reads."), \
        "Why gold has performance objects: spend write time once to save read time many times."


# ------------------------------------------------------------------ cost
def cost_idle():
    b = t(10, 22, "One day on a cluster that never switches off (each block = 1 hour)", 15, "start", INK, True)
    busy = {2, 3, 9, 10, 11, 14}
    for h in range(24):
        x = 10 + h * 38
        b += rect(x, 36, 34, 40, "mint" if h in busy else "rose")
        if h % 3 == 0:
            b += t(x + 17, 92, f"{h:02d}h", 12, "middle", "#555")
    b += rect(10, 110, 18, 14, "mint") + t(34, 122, "busy (6 h)", 14, "start") + rect(150, 110, 18, 14, "rose") + t(174, 122, "idle but billed (18 h)", 14, "start")
    b += t(10, 152, "Billed for 24 hours, working for 6. An idle timeout of a few minutes removes most of the pink.", 15, "start", "#555")
    return svg(940, 166, b, "A 24-hour strip where only 6 hours are busy and 18 are idle but billed."), \
        "Idle compute: the same bill for busy and idle hours. Illustrative example."


def cost_frequency():
    rows = [("Monthly", 24), ("Weekly", 104), ("Daily", 730), ("Hourly", 17520)]
    b = t(10, 22, "A job that costs $2 per run, per year (illustrative)", 15, "start", INK, True)
    mx = 17520
    for i, (n, v) in enumerate(rows):
        y = 40 + i * 44
        w = max(6, 620 * (v / mx) ** 0.5)
        b += t(110, y + 24, n, 15, "end", INK) + rect(122, y, w, 32, ["mint", "mint", "butter", "rose"][i]) + t(122 + w + 10, y + 22, f"${v:,}", 15, "start", INK)
    b += t(10, 224, "Bar length is a square-root scale so the small ones stay visible. Ask how often before asking how fast.", 14, "start", "#555")
    return svg(940, 238, b, "Bars showing that a $2 job costs $24 a year monthly and $17,520 a year hourly."), \
        "Frequency multiplies everything. Same job, same $2: monthly is $24 a year, hourly is $17,520."


def cost_lines():
    b = t(10, 22, "Where a typical data bill goes (illustrative shape, not a measurement)", 15, "start", INK, True)
    parts = [("Compute", 62, "rose"), ("Storage", 14, "butter"), ("Network", 6, "sky"), ("Platform services", 12, "lilac"), ("Other", 6, "grey")]
    x = 10
    for n, p, f in parts:
        w = p / 100 * 900
        b += rect(x, 40, w, 56, f) + t(x + w / 2, 66, n if w > 110 else "", 15, "middle", INK) + t(x + w / 2, 86, f"{p}%" if w > 40 else "", 13.5, "middle", "#555")
        x += w
    b += t(10, 120, "Network 6%, Platform services 12%, Other 6%.", 14, "start", "#555") + t(10, 148, "Start with idle and oversized compute, then wasteful queries.", 15, "start", "#555")
    return svg(940, 160, b, "A horizontal stacked bar showing compute as the largest share of a data bill."), \
        "The five lines of a bill. The split varies by team; use the shape, not the numbers."


# ------------------------------------------------------------------ processing
def proc_lazy():
    b = box(10, 20, 150, 70, "Your code", "filter, join, write", "butter") + arrow(162, 55, 220, 55)
    b += box(222, 20, 150, 70, "Plan", "nothing runs yet", "peri") + arrow(374, 55, 432, 55)
    b += box(434, 20, 150, 70, "Optimiser", "reorders, pushes\nfilters down", "lilac") + arrow(586, 55, 644, 55)
    b += box(646, 20, 150, 70, "Stages", "cut at each\nshuffle", "mint")
    b += t(10, 126, "Only an action (write, count, collect, show) makes the engine run the plan. Each action is a new job with planning cost.", 15, "start", "#555")
    return svg(940, 140, b, "Code becomes a plan, an optimiser rewrites it, then it is cut into stages."), \
        "Lazy evaluation: transformations describe; an action runs."


def proc_batch_stream():
    b = t(10, 22, "How much at a time", 15.5, "start", INK, True)
    labels = [("Full refresh", "everything, every run", "rose", 10), ("Incremental batch", "only new or changed", "mint", 245), ("Micro-batch", "small batches, often", "butter", 480), ("Continuous", "row by row", "lilac", 715)]
    for n, s, f, x in labels:
        b += box(x, 36, 215, 70, n, s, f)
    b += arrow(110, 130, 820, 130)
    b += t(10, 126, "simple, costly at scale", 13, "start", "#555") + t(930, 126, "fresh, complex", 13, "end", "#555")
    b += t(10, 160, "Choose by how fresh the answer must be. Most businesses need incremental batch.", 15, "start", "#555")
    return svg(940, 174, b, "A spectrum from full refresh through incremental and micro-batch to continuous processing."), \
        "Freshness is a business question first. Cost and complexity rise as you go right."


def proc_failure():
    b = box(10, 30, 170, 66, "Job fails", "midway", "rose") + arrow(182, 63, 262, 63) + box(264, 30, 170, 66, "Rerun", "", "butter")
    b += arrow(436, 63, 516, 63) + box(518, 30, 400, 66, "Same table as a clean run", "idempotent write", "mint")
    b += box(10, 124, 424, 60, "Blind append: duplicates", "", "rose") + t(676, 160, "Fix: overwrite a partition or merge on a key", 15, "middle", INK)
    return svg(940, 200, b, "A rerun after failure gives the same table when writes are idempotent, but duplicates with blind appends."), \
        "Safe reruns: overwrite or merge on a key, never blindly append."


# ------------------------------------------------------------------ security
def sec_gates():
    b = box(10, 30, 130, 66, "You", "person or job", "peri")
    names = [("Who are you?", "identity", "butter"), ("Allowed?", "permissions", "mint"), ("Which rows?", "filters, masks", "lilac")]
    x, prev = 190, 142
    for n, sub, f in names:
        b += arrow(prev, 63, x - 2, 63) + box(x, 30, 180, 66, n, sub, f)
        prev = x + 182
        x += 215
    b += arrow(prev, 63, 826, 63) + rect(828, 34, 100, 58, "gold") + t(878, 70, "Data", 19, "middle", INK, True)
    b += rect(190, 130, 738, 44, "grey") + t(559, 158, "Audit log: who read what, and when", 15, "middle", INK)
    b += t(10, 204, "Secrets stay in a secret store, never in code.", 14.5, "start", "#555")
    return svg(940, 218, b, "A request passes identity, permission and row and column checks before reaching data, with an audit log underneath."), \
        "Layers of access control. Each gate narrows what is visible; the audit log proves it."


# ------------------------------------------------------------------ storage
def stor_table():
    b = t(10, 22, "A table is files plus a ledger", 16, "start", INK, True)
    b += rect(10, 40, 250, 150, "butter") + t(135, 62, "Transaction log (the ledger)", 15, "middle", INK, True)
    for i, line in enumerate(["v1: add file A, file B", "v2: add file C", "v3: remove A, add A2", "current = B, C, A2"]):
        b += t(24, 92 + i * 28, line, 14.5, "start", INK)
    for i, (n, f, a) in enumerate([("file A", "grey", 0.4), ("file B", "mint", 1), ("file C", "mint", 1), ("file A2", "mint", 1)]):
        b += rect(380 + i * 135, 60, 120, 56, f, op=a) + t(440 + i * 135, 94, n, 15, "middle", INK)
    b += arrow(262, 100, 376, 88) + t(640, 146, "files are never edited, only added or replaced", 14.5, "middle", "#555")
    b += t(640, 172, "Readers follow the ledger: always a consistent snapshot", 14.5, "middle", "#555")
    return svg(940, 204, b, "A transaction log listing versions, pointing to immutable files in storage."), \
        "How lake tables work: update = write new files and record it in the log."


def stor_partition():
    b = t(10, 22, "Too many partitions", 15.5, "start", INK, True) + t(490, 22, "Right-sized partitions", 15.5, "start", INK, True)
    for i in range(12):
        b += rect(10 + (i % 6) * 72, 36 + (i // 6) * 46, 64, 36, "rose") + t(42 + (i % 6) * 72, 59 + (i // 6) * 46, "1 MB", 12, "middle", INK)
    b += t(10, 142, "Tiny files: slow to list, little skipping.", 14.5, "start", "#555")
    for i in range(3):
        b += rect(490 + i * 150, 36, 140, 82, "mint") + t(560 + i * 150, 70, f"month {i + 1}", 14.5, "middle", INK) + t(560 + i * 150, 94, "~500 MB", 13.5, "middle", "#555")
    b += t(490, 142, "Healthy sizes: cheap to list, easy to skip.", 14.5, "start", "#555")
    return svg(940, 158, b, "Many tiny partition folders versus a few well-sized ones."), \
        "Partition only on a column people filter on, and only so each partition stays large."


# ------------------------------------------------------------------ database families
def db_map():
    items = [("Relational", "correct small transactions", "peri", "rows, keys, SQL"), ("Key-value / NoSQL", "instant lookup by key", "butter", "key to value"),
             ("MPP warehouse", "big scans in parallel", "mint", "columns, many nodes"), ("Open table formats", "many engines, one copy", "sky", "files plus a log"),
             ("Object storage", "cheap, durable floor", "grey", "buckets of files"), ("Graph", "who connects to whom", "rose", "nodes and edges"),
             ("Vector", "find by meaning", "lilac", "embeddings"), ("Embedded engine", "small data, one machine", "gold", "no cluster")]
    b = ""
    for i, (n, s, f, k) in enumerate(items):
        x = 10 + (i % 4) * 232
        y = 14 + (i // 4) * 120
        b += box(x, y, 218, 102, n, s + "\n" + k, f)
    b += t(10, 262, "Pick by the main read and write pattern. Most platforms combine several.", 15, "start", "#555")
    return svg(940, 276, b, "Eight database families each with what they are built for."), \
        "The families at a glance, each a bet on one access pattern."


def db_flow():
    b = box(10, 40, 180, 70, "Source DB", "relational", "peri") + arrow(192, 75, 252, 75, "extract")
    b += box(254, 40, 180, 70, "Object storage", "files + log", "grey") + arrow(436, 75, 496, 75)
    b += box(498, 40, 190, 70, "Analytics", "warehouse or lakehouse", "mint") + arrow(690, 75, 730, 50) + arrow(690, 75, 730, 100)
    b += box(732, 14, 198, 56, "Vector index", "AI search", "lilac") + box(732, 84, 198, 56, "Serving store", "fast lookups", "butter")
    b += t(10, 170, "Each store does the one job it is shaped for.", 15, "start", "#555")
    return svg(940, 184, b, "Data flowing from an operational database to object storage, an analytics engine, a vector index and a serving store."), \
        "How the families work together in one platform."


FIGS = {
    "performance": {"ladder": [perf_ladder], "where": [perf_buckets], "storage": [perf_rowcol, perf_skip], "tasks": [perf_cluster],
                    "move": [perf_shuffle], "gold": [perf_gold]},
    "cost": {"where": [cost_lines], "idle": [cost_idle], "refresh": [cost_frequency]},
    "processing": {"model": [proc_lazy], "batch": [proc_batch_stream], "parallel": [perf_shuffle], "safe": [proc_failure]},
    "security": {"access": [sec_gates]},
    "storage": {"table": [stor_table], "layout": [perf_skip, stor_partition], "format": [perf_rowcol]},
    "database-families": {"choose": [db_map], "open": [db_flow]},
}
