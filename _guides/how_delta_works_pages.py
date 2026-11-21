"""Page bodies for the 'How reads and writes work' section. Every number comes from R (measured results), never typed by hand."""
import json
from html import escape as E

import how_delta_works as H
from how_delta_works import R, bx, ar, svg, fig, t, n, sz, sec, pct, hbars, strip, code_box, section, real, FILLS

RD, SP, JN, WR, BD = R["read"], R["spark"], R["joins"], R["write"], R["build"]
Q = RD["queries"]
LASTCP = json.loads(RD["last_checkpoint"])
FOOT = RD["footer"]
CH = {c["column"]: c for c in FOOT["chunks"]}
OPS = {o["label"]: o for o in WR["ops"]}
LAB = ("measured on a laptop with Apache Spark 3.5.1 and open-source Delta Lake 3.2.0, local mode, 2 cores. "
       "Not Databricks: Photon, predictive I/O and liquid clustering were not available locally.")


def p(s):
    return f"<p>{s}</p>"


def ul(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def table(head, rows, cls="t"):
    th = "".join(f"<th>{h}</th>" for h in head)
    body = "".join("<tr>" + "".join(f"<td{(' class=\"v ' + c[1] + '\"') if isinstance(c, tuple) else ''}>{c[0] if isinstance(c, tuple) else c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tw"><table class="{cls}"><tr>{th}</tr>{body}</table></div>'


PURSUE, DROP = ("Pursue", "pursue"), ("Drop", "drop")


# =================================================================== hub
def d_big():
    i = bx(10, 20, 170, 90, ["Your query", "SQL or DataFrame", "(Python, SQL, Scala)"], "b", 15)
    i += bx(230, 20, 200, 90, ["Driver", "plans the query", "reads the delta log", "picks files to read"], "y", 15)
    i += bx(480, 20, 200, 90, ["Executors", "tasks read files,", "filter, join, aggregate"], "g", 15)
    i += bx(730, 20, 260, 90, ["Parquet files in storage", "columns, compressed,", "with min and max in the footer"], "r", 15)
    i += ar(182, 65, 228, 65) + ar(432, 65, 478, 65) + ar(682, 65, 728, 65)
    i += bx(230, 170, 200, 70, ["_delta_log", "which files, and their stats"], "l", 14) + ar(330, 112, 330, 168, label="reads", lx=360, ly=145)
    i += t(500, 275, "Reads: the log narrows the file list before any data is touched.", 15, "middle")
    i += t(500, 298, "Writes: executors write new Parquet files, then the driver adds a commit to the log.", 15, "middle")
    return svg(1000, 312, "The read path in one picture. A query goes to the driver, which plans it and reads the delta log to choose which files to read. Executors run tasks that read those Parquet files from storage. For writes, executors write new Parquet files and the driver then adds one commit to the log.", i)


def page_start():
    cards = "".join(f'<li><a href="{H.BASE}{s}"><b>{E(lab)}: {E(title.split(":")[0])}</b></a><br>{E(desc.split(".")[0])}.</li>' for s, lab, title, desc in H.PAGES[1:])
    body = (
        p("When someone says a query is slow, or a write is expensive, the cause is nearly always one of a few mechanisms: which files were opened, how many bytes came off disk, whether data had to move between machines, or how much was rewritten. This section shows each mechanism with a drawing and then with a measurement, in the order a beginner needs them.")
        + fig(d_big(), "The whole story on one page. Each later page zooms into one box.")
        + '<div class="box"><b>The short version.</b> A Delta table is Parquet files plus a log. A read asks the log which files could match, opens only those, and reads only the columns it needs. A write adds new files and then one line to the log. Everything else here explains how, why that sometimes goes wrong, and how to tell.</div>'
        + section("path", "The path", "Ten pages, in this order", '<ol class="steps">' + cards + "</ol>")
        + section("measured", "How this was measured", "Real runs, not invented numbers",
                  p(f"Every number on these pages was produced by a script in the site repository and is {LAB} Absolute times are tiny because the table is small. Use the <b>ratios and counts</b> (files read, bytes read, rows copied), which behave the same way on a terabyte.")
                  + ul([f"<b>The table:</b> {n(BD['rows'])} rows, {BD['columns']} columns, {n(BD['T']['files'])} files of {n(BD['rows_per_file'])} rows, {sz(BD['T']['bytes'])} on disk. A 1 TB table is the same picture with more files.",
                        "<b>Marked clearly:</b> anything that only exists on Databricks (Photon, predictive I/O, liquid clustering, the query profile) comes from the Databricks documentation and was <i>not</i> measured.",
                        "<b>Honest gaps:</b> the Delta protocol document could not be fetched during writing, so the log mechanics are shown from real log files, and the rules are labelled as general knowledge where they go beyond what was observed."]))
        + section("words", "Words used", "A small glossary", "<dl class='gloss'>" + "".join(f"<dt>{a}</dt><dd>{b}</dd>" for a, b in [
            ("Driver", "The one process that plans the query and talks to the log."),
            ("Executor", "A worker process that runs tasks on slices of the data."),
            ("Task", "One unit of work on one slice, usually one file or part of a file."),
            ("Stage", "A group of tasks that can run without moving data between machines."),
            ("Shuffle", "Moving rows between executors so that matching keys end up together."),
            ("Parquet", "A column-oriented file format with min and max values in its footer."),
            ("Delta log", "The folder of JSON commit files (plus checkpoints) that says which Parquet files make up the table."),
            ("Data skipping", "Using min and max values to skip files that cannot match a filter."),
            ("Predicate pushdown", "Handing a filter to the file reader so it can skip data early."),
        ]) + "</dl>")
        + section("next", "Related", "Where it connects",
                  p('<a href="/learn/data-platform-sim/delta/">Delta Lake internals simulator</a> · <a href="/learn/row-vs-column-storage/">Row vs column storage</a> · <a href="/learn/table-maintenance/">Who maintains your tables</a> · <a href="/learn/databricks-compute/photon-and-caches/">Photon and caches (compute guide)</a> · <a href="/learn/delta-vs-iceberg/">Delta vs Iceberg</a>'))
    )
    qa = [("What is a Delta table, physically?", "A folder of Parquet data files plus a _delta_log folder of JSON commit files and occasional checkpoints. The log says which files are currently part of the table and carries per-file statistics."),
          ("Why do reads touch the log first?", "Because the log lists every live file with its minimum and maximum values. The driver uses that list to skip files before any data is read."),
          ("Are the numbers in this section from Databricks?", "No. They come from open-source Delta Lake 3.2.0 on Spark 3.5.1 on a laptop. Databricks-only features are described from its documentation and marked as not measured.")]
    return body, qa


# =================================================================== 1. files on disk
def d_folder():
    i = bx(10, 10, 300, 44, ["events/   (the table)"], "w", 15)
    i += bx(40, 90, 330, 44, ["_delta_log/   (the transaction log)"], "l", 14) + ar(160, 56, 160, 88)
    i += bx(430, 90, 330, 44, ["data files   part-0000….snappy.parquet"], "r", 14) + ar(240, 32, 428, 100)
    cp = RD["checkpoint_listing"]
    names = [x for x in cp if x.endswith(".json") or "checkpoint" in x][:10]
    show = ["000…000.json", "000…001.json", "000…004.json", "000…005.checkpoint.parquet", "000…005.json", "000…009.json", "_last_checkpoint"]
    for k, nm in enumerate(show):
        f = "y" if "checkpoint" in nm else "w"
        i += bx(60, 150 + k * 34, 310, 30, [nm], f, 12.5)
    i += t(215, 150 + 7 * 34 + 14, "a real log with 10 commits (table L)", 13, "middle")
    for k in range(5):
        i += bx(430, 150 + k * 34, 330, 30, [f"part-{k:05d}-….parquet  (10,000 rows)"], "g", 12.5)
    i += t(595, 150 + 5 * 34 + 14, "20 files in the main table T", 13, "middle")
    i += bx(790, 90, 200, 120, ["The log is small", "and says which", "files are live"], "y", 14)
    return svg(1000, 470, "A Delta table is a folder. Inside it a _delta_log folder holds numbered JSON commit files, a checkpoint parquet file after every few commits, and a _last_checkpoint pointer. Next to it are the Parquet data files.", i)


def d_parquet():
    i = bx(10, 20, 60, 130, ["PAR1"], "w", 13) + bx(76, 20, 640, 130, [""], "r", 13)
    i += t(396, 44, f"Row group 1   ({n(FOOT['rows'])} rows, {len(FOOT['chunks']) and 40} column chunks)", 15, "middle")
    cols = [("event_id", 90), ("user_id", 90), ("country", 70), ("amount", 90), ("payload", 120), ("f01 … f33", 60), ("late_code", 70)]
    x = 88
    for k, (nm, w) in enumerate(cols):
        i += bx(x, 58, w - 4, 80, [nm], "y" if nm != "payload" else "b", 13)
        x += w
    i += bx(722, 20, 190, 130, ["Footer", "schema,", "where each column", "chunk starts,", "min and max"], "l", 13)
    i += bx(918, 20, 72, 130, ["PAR1"], "w", 13)
    i += t(500, 190, "Readers start at the end: read the footer, then jump straight to the column chunks they need.", 15, "middle")
    i += t(500, 215, f"This real file: {n(FOOT['file_bytes'])} bytes, 1 row group, codec {CH['event_id']['codec']}, written by {FOOT['created_by'].split(' (')[0]}.", 14, "middle")
    return svg(1000, 235, "Anatomy of a Parquet file: a PAR1 marker, one or more row groups each holding one chunk per column, then a footer with the schema, the locations of every column chunk and their minimum and maximum values, then PAR1 again. Readers begin at the footer.", i)


def d_add():
    st = RD["log_add_first_stats"]
    a = RD["log_add_first"]
    lines = ['{"add": {',
             f'  "path": "{a["path"][:30]}…parquet",',
             f'  "partitionValues": {{}},   "size": {a["size"]},   "dataChange": true,',
             '  "stats": {',
             f'    "numRecords": {st["numRecords"]},',
             f'    "minValues": {{"event_id": {st["minValues"]["event_id"]}, "user_id": {st["minValues"]["user_id"]}, "event_date": "{st["minValues"]["event_date"]}", …}},',
             f'    "maxValues": {{"event_id": {st["maxValues"]["event_id"]}, "user_id": {st["maxValues"]["user_id"]}, "event_date": "{st["maxValues"]["event_date"]}", …}},',
             f'    "nullCount": {{"event_id": 0, "user_id": 0, …}}']
    lines += ["  }", "}}"]
    box, h = code_box(10, 14, 660, lines, 12.5)
    i = box
    i += bx(700, 30, 290, 40, ["path: which file"], "w", 13) + bx(700, 76, 290, 40, ["size: used to plan tasks"], "w", 13)
    i += bx(700, 122, 290, 50, ["numRecords: lets count(*) be", "answered without opening files"], "g", 13)
    i += bx(700, 178, 290, 50, ["min and max: skip files that", "cannot hold the value you want"], "y", 13)
    i += bx(700, 234, 290, 40, ["nullCount: IS NULL filters"], "w", 13)
    return svg(1000, max(h + 30, 290), "One real add action from the delta log. It holds the file path, size, partition values, whether it changes data, and statistics: number of records, per-column minimum and maximum values and null counts. The driver uses the statistics to skip files.", i)


def d_state():
    u1 = OPS["update_one_file"]
    i = bx(10, 20, 220, 80, ["version 0", f"+{WR['create']['actions']['add']} add", "(a table of 10 files)"], "g", 14)
    i += bx(270, 20, 220, 80, ["version 1", "−1 remove, +1 add", "(an UPDATE rewrote one file)"], "y", 14)
    i += bx(530, 20, 200, 80, ["version 2 …", "more commits"], "w", 15)
    i += bx(770, 20, 220, 80, ["a checkpoint, for example", f"v{LASTCP['version']}: all live files saved"], "l", 14)
    i += ar(232, 60, 268, 60) + ar(492, 60, 528, 60)
    i += bx(10, 150, 480, 70, ["Live files = every add, minus every file that was later removed"], "b", 15)
    i += bx(520, 150, 470, 70, ["A reader loads the latest checkpoint, then replays only the JSON commits after it"], "y", 14)
    i += t(500, 262, "Old Parquet files stay on disk after a remove. That is what makes time travel possible, until VACUUM deletes them.", 14, "middle")
    return svg(1000, 280, "The log is a list of commits. Version 0 adds the data files, version 1 removes one file and adds its rewritten replacement, and so on. A checkpoint saves the live set so a reader replays only the commits after it. Removed files stay on disk until VACUUM.", i)


def page_files_on_disk():
    cp = LASTCP
    body = (
        section("folder", "From zero", "A Delta table is a folder of files", p("There is no database server holding a Delta table. Open the folder and you see two kinds of things: <b>Parquet data files</b>, and a <b>_delta_log</b> folder that says which of those files currently make up the table.") + fig(d_folder(), "The folder, drawn from a real table. The log is numbered; the checkpoint is a shortcut.")
                + real(f"The main table has {BD['T']['files']} Parquet files and one commit. A second small table made with ten commits shows the checkpoint: Delta wrote <code>00000000000000000005.checkpoint.parquet</code> and a <code>_last_checkpoint</code> file that says <i>version {cp['version']}, {cp['numOfAddFiles']} live files, {n(cp['sizeInBytes'])} bytes</i>."))
        + section("parquet", "Inside a data file", "Parquet: columns stored in chunks, with a footer of statistics", p("Each data file is Parquet. Inside it, data is cut into <b>row groups</b>, and inside each row group every column is its own <b>chunk</b>. At the very end sits a <b>footer</b> with the schema, where each chunk starts, and the minimum and maximum of each column chunk.") + fig(d_parquet(), "Reading starts at the footer, not the top of the file.")
                + real(f"One real file from the main table: {n(FOOT['file_bytes'])} bytes holding {n(FOOT['rows'])} rows in {FOOT['row_groups']} row group with 40 column chunks. Its footer says <code>event_id</code> runs from {CH['event_id']['min']} to {CH['event_id']['max']}. That one line is what lets a reader skip this whole file when you ask for <code>event_id = 50</code>."))
        + section("add", "Inside the log", "The add action: where the statistics live", p("Each commit file is plain JSON, one action per line. The important action is <b>add</b>: it names a data file and carries that file's statistics, so the <b>driver</b> can decide which files matter <i>without opening any of them</i>.") + fig(d_add(), "A real add action, lightly shortened. This is the line the driver reads.")
                + p(f"The same commit also holds a <code>protocol</code> action (this table needs reader version {RD['log_protocol']['minReaderVersion']}, writer version {RD['log_protocol']['minWriterVersion']}), a <code>metaData</code> action (schema, partition columns, table settings), and a <code>commitInfo</code> action recording who did what: operation <code>{RD['log_commitInfo']['operation']}</code>, mode <code>{RD['log_commitInfo']['operationParameters']['mode']}</code>, isolation level <code>{RD['log_commitInfo']['isolationLevel']}</code>, written by <code>{RD['log_commitInfo']['engineInfo']}</code>."))
        + section("state", "Putting commits together", "How a reader works out which files are live", fig(d_state(), "Add and remove, replayed in order, give the table's current state.")
                + ul(["Every <b>add</b> makes a file live. Every <b>remove</b> makes it not live. The current table is what is left after replaying the commits in order.",
                      "To avoid replaying thousands of small files, Delta writes a <b>checkpoint</b> every few commits: one Parquet file holding the whole live set. A reader loads the latest checkpoint and then only the JSON commits after it.",
                      "<b>Remove does not delete.</b> The old Parquet file stays in the folder. That is why <code>VERSION AS OF 0</code> still works after an overwrite, and why storage grows until <code>VACUUM</code> runs (see the write path).",
                      "The log is read by Spark itself. During the experiments the Spark UI showed queries named <code>Scan ExistingRDD Delta Table State</code>: Delta uses a small Spark job to load and filter the log."])
                + '<div class="box"><b>Note.</b> The commit-replay and checkpoint rules above are general Delta behaviour confirmed here by the real files; the formal protocol document could not be fetched while writing, so details such as multi-part and V2 checkpoints are not described.</div>')
    )
    qa = [("What does the _delta_log folder contain?", "Numbered JSON commit files that record add, remove, metaData, protocol and commitInfo actions, plus periodic checkpoint Parquet files and a _last_checkpoint pointer."),
          ("Where are the min and max values kept?", "Twice: per file inside the add action in the delta log, and per column chunk inside each Parquet file's footer. Delta uses the first to skip files, and the Parquet reader uses the second to skip row groups."),
          ("Does removing a file delete it?", "No. A remove action only marks the file as no longer part of the table. The file stays until VACUUM deletes files older than the retention period.")]
    return body, qa


# =================================================================== 2. read path
def d_cluster():
    i = bx(10, 20, 200, 120, ["Driver", "1. resolve the table", "2. read the log", "3. skip files", "4. plan tasks"], "y", 14)
    i += bx(290, 20, 250, 56, ["Executor 1", "2 task slots"], "g", 14) + bx(290, 84, 250, 56, ["Executor 2 …", "more slots, more files at once"], "g", 14)
    i += bx(620, 20, 180, 120, ["Parquet files", "in storage", "(20 here,", "thousands at 1 TB)"], "r", 14)
    i += bx(830, 20, 160, 120, ["Result", "to the driver,", "or written", "to a table"], "b", 14)
    i += ar(212, 80, 288, 48, label="tasks", lx=250, ly=58) + ar(212, 90, 288, 112)
    i += ar(542, 48, 618, 70, label="read", lx=580, ly=52) + ar(542, 112, 618, 100)
    i += ar(802, 80, 828, 80)
    i += bx(10, 170, 200, 54, ["_delta_log", "files and statistics"], "l", 13) + ar(110, 142, 110, 168)
    i += t(500, 262, "One task reads one file (or one slice of a big file). More executor slots means more files read at the same time.", 14, "middle")
    return svg(1000, 280, "The cluster picture. The driver resolves the table, reads the delta log, skips files and plans tasks. Executors, each with several task slots, run the tasks that read Parquet files from storage. Results go to the driver or are written to a table.", i)


def d_steps():
    steps = [("1", "Resolve", "find the table folder"), ("2", "Read the log", "latest checkpoint + later commits"), ("3", "Prune partitions", "skip folders that cannot match"),
             ("4", "Skip files", "min/max of each file vs the filter"), ("5", "Plan tasks", "one task per file or slice"),
             ("6", "Read footers", "skip row groups by min/max"), ("7", "Read chunks", "only the columns the query needs")]
    fills = ["w", "l", "g", "g", "y", "r", "r"]
    i = ""
    for k, (num, h, sub) in enumerate(steps):
        x = 10 + (k % 4) * 248 if k < 4 else 10 + (k - 4) * 330
        y = 20 if k < 4 else 140
        wdt = 232 if k < 4 else 310
        i += bx(x, y, wdt, 80, [f"{num}. {h}", sub], fills[k], 15)
    for k in range(3):
        i += ar(10 + k * 248 + 233, 60, 10 + (k + 1) * 248 - 2, 60)
    i += ar(850, 102, 800, 138)
    i += ar(10 + 310 + 2, 180, 10 + 330 - 2, 180) + ar(340 + 312, 180, 660 - 2, 180)
    i += t(500, 255, "Steps 1 to 5 happen on the driver and read only metadata. Steps 6 and 7 happen on executors and read data.", 15, "middle")
    return svg(1000, 275, "The seven steps of a Delta read. On the driver: resolve the table, read the log, prune partitions, skip files using min and max, and plan tasks. On executors: read Parquet footers and skip row groups, then read only the needed column chunks.", i)


def d_queries():
    names = [("SELECT * (all 40 columns)", "q1_select_star"), ("2 columns only", "q2_two_columns"), ("event_date = one day (sorted)", "q3_event_date"),
             ("user_id = one value (random)", "q4_user_id"), ("late_code, column 40 (no stats)", "q5_late_code_default_stats"), ("late_code, stats on all 40", "q5b_late_code_stats_on_all"),
             ("user_id after Z-ORDER", "q4z_user_id_zorder")]
    rows1 = [(lab, Q[k]["files"], f"{Q[k]['files']} of {RD['zorder']['files'] if 'zorder' in k else BD['T']['files']}", "r" if Q[k]["files"] > 5 else "g") for lab, k in names]
    rows2 = [(lab, Q[k]["input_bytes"], sz(Q[k]["input_bytes"]), "r" if Q[k]["input_bytes"] > 5e6 else ("y" if Q[k]["input_bytes"] > 1e6 else "g")) for lab, k in names]
    a, y1 = hbars(rows1, 10, 34, 270, 330, 30)
    b, y2 = hbars(rows2, 10, y1 + 52, 270, 330, 30)
    i = t(10, 22, "Files opened", 16) + a + t(10, y1 + 40, "Bytes read from disk", 16) + b
    return svg(1000, y2 + 10, "Two bar charts for seven queries. Files opened: select star 20, two columns 20, one day 1, random user_id 20, column 40 without statistics 20, column 40 with statistics 1, user_id after Z-order 1 of 28. Bytes read: select star 11.6 MB, two columns 2.9 MB, one day 0.7 MB, random user_id 12.0 MB, column 40 without statistics 0.9 MB, with statistics 0.6 MB, after Z-order 0.6 MB.", i)


def d_ranges():
    rg = RD["ranges"]
    i = t(10, 22, "event_date range per file (the data arrived in date order)", 15)
    for k, r in enumerate(rg):
        i += f'<rect x="{10 + k * 48}" y="34" width="42" height="26" rx="4" fill="{FILLS["g"]}" stroke="#111" stroke-width="1.2"/>' + t(31 + k * 48, 52, str(k + 1), 12, "middle")
    i += t(10, 92, "Each file holds exactly one day. A filter on one day matches one file.", 14)
    i += t(10, 130, "user_id range per file (values were random)", 15)
    for k, r in enumerate(rg):
        x0 = 10 + (r["user_id_min"] / 50000) * 940
        w = max(4, (r["user_id_max"] - r["user_id_min"]) / 50000 * 940)
        i += f'<rect x="{x0:.0f}" y="{142 + k * 12}" width="{w:.0f}" height="9" rx="3" fill="{FILLS["r"]}" stroke="#111" stroke-width="1"/>'
    i += f'<line x1="{10 + 12345 / 50000 * 940:.0f}" y1="136" x2="{10 + 12345 / 50000 * 940:.0f}" y2="{142 + 20 * 12}" stroke="#111" stroke-width="1.8" stroke-dasharray="5 4"/>'
    i += t(10 + 12345 / 50000 * 940 + 8, 142 + 20 * 12 + 14, "user_id = 12,345 falls inside every file's range", 14)
    i += t(10, 142 + 20 * 12 + 14, "0", 13) + t(950, 142 + 20 * 12 + 14, "50,000", 13, "end")
    return svg(1000, 142 + 20 * 12 + 36, "Two views of the 20 files. Top: the event_date range of each file is a single distinct day, so a one-day filter matches one file. Bottom: the user_id range of each file spans almost 0 to 50,000, so every file's range contains the value 12,345 and no file can be skipped.", i)


def d_stat32():
    i = t(10, 22, "40 columns, in table order. Delta collects min and max only for the first 32 by default.", 15)
    for k in range(40):
        has = k < 32
        i += f'<rect x="{10 + k * 24}" y="34" width="21" height="40" rx="3" fill="{FILLS["g"] if has else FILLS["r"]}" stroke="#111" stroke-width="1.1"/>'
    i += t(10, 98, "columns 1 to 32: have statistics", 14) + t(10 + 32 * 24 + 6, 98, "33 to 40: none", 14)
    i += t(10 + 39 * 24 + 10, 126, "late_code (column 40)", 14, "end")
    i += bx(10, 150, 450, 60, ["Filter on late_code, default table", f"{Q['q5_late_code_default_stats']['files']} files opened, {sz(Q['q5_late_code_default_stats']['input_bytes'])} read"], "r", 14)
    i += bx(500, 150, 480, 60, ["Same filter, statistics on all 40 columns", f"{Q['q5b_late_code_stats_on_all']['files']} file opened, {sz(Q['q5b_late_code_stats_on_all']['input_bytes'])} read"], "g", 14)
    return svg(1000, 230, "Forty columns drawn as boxes. The first 32 are shaded as having statistics, the last 8 as having none. A filter on column 40 opens 20 files and reads 0.9 MB on the default table, but opens only 1 file and reads 0.6 MB when statistics are collected on all 40 columns.", i)


def page_read_path():
    q = Q
    cnt = R["count"]
    body = (
        section("who", "Who does what", "The driver plans, the executors read", p("Before any data moves, one process, the <b>driver</b>, works out <i>which files</i> are needed. Only then do the <b>executors</b>, the worker processes, read them in parallel. This split is why metadata work (the log) and data work (the files) behave so differently.") + fig(d_cluster(), "Metadata work on the driver, data work on executors."))
        + section("steps", "The steps", "Seven steps from SQL to bytes", fig(d_steps(), "Steps 1 to 5 never touch a data file.")
                  + ul(["<b>Steps 2 to 4 are Delta's contribution.</b> The driver loads the live file list and the statistics for each file from the log, then drops every file whose min and max prove it cannot match. This is called <b>data skipping</b>.",
                        "<b>Step 3, partition pruning,</b> only applies when the table is partitioned: whole folders are dropped by name.",
                        "<b>Steps 6 and 7 are Parquet's contribution.</b> Inside each chosen file the reader checks the footer's per-chunk min and max (skipping row groups) and then reads only the column chunks the query names."]))
        + section("queries", "Six kinds of query", "One table, six queries, measured", p(f"The table has {BD['T']['files']} files of {n(BD['rows_per_file'])} rows: <code>event_id</code> and <code>event_date</code> increase with the load order, <code>user_id</code> is random, and 40 columns in all. Each query was run to a no-op sink so nothing was printed, and repeated three times after a warm-up.")
                  + fig(d_queries(), "Files opened and bytes read for each query. Red is bad, green is good.")
                  + table(["Query", "Files opened", "Bytes read", "Rows decoded", "Why"], [
                      ["<code>SELECT *</code>", f"{q['q1_select_star']['files']} of {BD['T']['files']}", sz(q['q1_select_star']['input_bytes']), n(q['q1_select_star']['rows']), "No filter, every column: the full cost."],
                      ["<code>SELECT event_id, amount</code>", f"{q['q2_two_columns']['files']} of {BD['T']['files']}", f"{sz(q['q2_two_columns']['input_bytes'])} ({pct(q['q2_two_columns']['input_bytes'], q['q1_select_star']['input_bytes'])} of select *)", n(q['q2_two_columns']['rows']), "Every file opened, but only 2 of 40 column chunks read."],
                      ["<code>WHERE event_date = one day</code>", f"{q['q3_event_date']['files']} of {BD['T']['files']}", f"{sz(q['q3_event_date']['input_bytes'])} ({pct(q['q3_event_date']['input_bytes'], q['q1_select_star']['input_bytes'])})", n(q['q3_event_date']['rows']), "Sorted column: each file holds one day, so 19 files are skipped by the log alone."],
                      ["<code>WHERE user_id = 12345</code>", f"{q['q4_user_id']['files']} of {BD['T']['files']}", sz(q['q4_user_id']['input_bytes']), n(q['q4_user_id']['rows']), "Random column: every file's range contains 12,345, so nothing can be skipped."],
                      ["<code>WHERE late_code = 7</code> (column 40)", f"{q['q5_late_code_default_stats']['files']} of {BD['T']['files']}", f"{sz(q['q5_late_code_default_stats']['input_bytes'])}", n(q['q5_late_code_default_stats']['rows']), "No log statistics, so all files opened. The Parquet footer then skipped most data."],
                      ["same, statistics on all 40 columns", f"{q['q5b_late_code_stats_on_all']['files']} of {BD['T']['files']}", sz(q['q5b_late_code_stats_on_all']['input_bytes']), n(q['q5b_late_code_stats_on_all']['rows']), "The log can now skip 19 files without opening them."],
                      ["<code>WHERE user_id = 12345</code> after Z-ORDER", f"{q['q4z_user_id_zorder']['files']} of {RD['zorder']['files']}", sz(q['q4z_user_id_zorder']['input_bytes']), n(q['q4z_user_id_zorder']['rows']), "Z-ordering clustered similar user_ids together, so one file matches."]])
                  + real(f"Plan lines from the engine confirm each reading. For the two-column query: <code>ReadSchema: struct&lt;event_id:bigint,amount:double&gt;</code>. For the one-day query: <code>PushedFilters: [IsNotNull(event_date), EqualTo(event_date,2026-01-10)]</code>. Timings were all between {sec(min(v['seconds'] for v in q.values()))} and {sec(max(v['seconds'] for v in q.values()))} here, so judge by files and bytes, not seconds."))
        + section("minmax", "Why min and max work", "A filter helps only when the data's order cooperates", p("Data skipping is a yes-or-no test on each file: <i>can this value possibly be inside [min, max]?</i> If the answer is no, the file is skipped. That works well on a column whose values arrive in order, and not at all on one that is scrambled.") + fig(d_ranges(), "Real min and max of all 20 files. Sorted column on top, random column below.")
                  + ul(["<b>event_date</b> arrived in order, so every file has min = max = one day. A one-day filter excludes 19 of 20 files for free.", "<b>user_id</b> is random, so every file spans almost the whole range. No file can be excluded, however selective the filter looks.", "The lesson: a column is only useful for skipping if the layout of the files makes ranges narrow. Section 3 shows how to make that happen on purpose."]))
        + section("stats32", "The 32-column limit", "Statistics are not collected for every column", fig(d_stat32(), "Where statistics stop, skipping stops.")
                  + p(f"By default Delta collects min, max and null counts only for the <b>first 32 columns</b> (the Databricks docs say the same). The real add action for the main table lists {RD['log_add_first_stats']['stat_columns']} statistics columns and does not list <code>late_code</code>. A second copy of the table with <code>delta.dataSkippingNumIndexedCols = 40</code> had {RD['log_stats_cols_T2']} and could skip files on it.")
                  + ul(["<b>Settings (from the Databricks docs):</b> <code>delta.dataSkippingNumIndexedCols</code> changes how many leading columns get statistics; <code>delta.dataSkippingStatsColumns</code> (Databricks Runtime 13.3 LTS and later) names the columns and takes precedence. Neither recomputes statistics for files already written.",
                        "<b>To recompute</b> on existing data: <code>ANALYZE TABLE t COMPUTE DELTA STATISTICS</code> (Databricks Runtime 14.3 LTS and later).",
                        "<b>Put columns you filter or join on early in the schema,</b> or list them explicitly. Long strings are truncated in statistics; the docs do not say at how many characters.",
                        "<b>A second chance:</b> even with no log statistics the Parquet footer has its own min and max per column chunk. That rescued part of the read above (0.9 MB instead of 11.6 MB), but only after opening all 20 files. With thousands of files, that opening can become the expensive part."]))
        + section("nodata", "Reading nothing", "Some queries never open a data file", p("The log holds <code>numRecords</code>, and min and max, for every file. For a few query shapes the engine answers from those numbers alone.")
                  + table(["Query", "Plan starts with", "Parquet read?"], [[f"<code>SELECT count(*)</code>", f"<code>{E(cnt['count_star']['first_plan_line'])}</code>", ("No", "pursue")],
                                                                                [f"<code>SELECT min(event_id), max(event_id)</code>", f"<code>{E(cnt['min_max']['first_plan_line'][:44])}</code>", ("No", "pursue")],
                                                                                ["<code>count(*)</code> with a filter", "<code>HashAggregate</code> over <code>FileScan parquet</code>", ("Yes", "drop")],
                                                                                ["<code>SUM(amount)</code>", "<code>HashAggregate</code> over <code>FileScan parquet</code>", ("Yes", "drop")]])
                  + real("A plain <code>count(*)</code> on the whole table became a <code>LocalTableScan</code>: the answer came from the log with no Parquet file opened. This was seen on open-source Delta Lake 3.2.0; I did not check how Databricks behaves, so confirm it before relying on it there."))
        + section("scale", "Scaling up", "The same picture at 1 TB", p("These are arithmetic, not measurements, but they follow from the ratios above and from one Databricks docs figure: a 1 TB table is tuned to about 256 MB files, which is about 4,096 files.")
                  + table(["Query on 1 TB", "Reads about", "How"], [["<code>SELECT *</code>", "1,000 GB", "Everything"], ["two of 40 columns", f"{1000 * q['q2_two_columns']['input_bytes'] / q['q1_select_star']['input_bytes']:.0f} GB", f"Same {pct(q['q2_two_columns']['input_bytes'], q['q1_select_star']['input_bytes'])} ratio as measured"],
                                                                   ["one day of 365, sorted by date", f"{1000 / 365:.1f} GB (about {4096 // 365} of 4,096 files)", "Skipped by the log"], ["a random column", "1,000 GB", "Nothing can be skipped, 4,096 files opened"]])
                  + p("Spark normally splits large files so one task handles at most about 128 MB (a general default, not re-checked here). So 256 MB files give roughly 8,000 tasks, which a cluster with 64 task slots works through in about 130 waves.") + "")
        + section("tips", "What to do", "Rules that follow from this", table(["Do", "Because", "Verdict"], [
            ["Select only the columns you need", "Column chunks you do not name are never read", PURSUE], ["Filter on columns that are sorted or clustered", "Narrow min/max ranges let the log skip files", PURSUE],
            ["Put filter and join columns in the first 32, or list them", "Statistics exist only for those", PURSUE], ["Use <code>SELECT *</code> on wide tables", "Pays for every column", DROP],
            ["Expect a filter on a random column to help", "Every file's range contains the value", DROP], ["Count rows with <code>count(*)</code> on the whole table", "Can be answered from the log (confirmed locally)", PURSUE]]))
    )
    qa = [("Does Delta read every file for every query?", "No. The driver uses the min and max values in the log to skip files that cannot match the filter, and only then are data files read. If the layout is random, though, nothing can be skipped."),
          ("Why is select * so expensive on a wide table?", "A Parquet file stores each column as its own chunk. A query that names two of forty columns reads two chunks; select * reads all forty."),
          ("Why did a filter on the 40th column still read fewer bytes?", "Delta had no statistics for it, so it opened every file, but each Parquet footer has its own min and max per column chunk, so most row groups could still be skipped. Collecting statistics on that column avoids opening the files at all."),
          ("Can a query be answered without reading data files?", "Yes in some cases: an unfiltered count(*) or min/max on a Delta table was answered from the log's statistics in the local experiments.")]
    return body, qa


# =================================================================== 3. layout
def d_small_files():
    i = t(10, 22, f"{BD['T']['files']} files of {n(BD['rows_per_file'])} rows", 15)
    for k in range(20):
        i += f'<rect x="{10 + k * 24}" y="34" width="21" height="52" rx="3" fill="{FILLS["g"]}" stroke="#111" stroke-width="1.1"/>'
    i += t(10, 118, f"{BD['S']['files']} files of 500 rows (same data)", 15)
    for r in range(4):
        for k in range(100):
            i += f'<rect x="{10 + k * 9.6:.1f}" y="{130 + r * 14}" width="7.6" height="11" fill="{FILLS["r"]}" stroke="#111" stroke-width="0.6"/>'
    S, T = RD["small_files"]["s_all"], RD["small_files"]["t_all"]
    i += table_svg(10, 205, [["", f"{BD['T']['files']} files", f"{BD['S']['files']} files"],
                             ["Bytes on disk", sz(BD['T']['bytes']), sz(BD['S']['bytes'])],
                             ["Tasks for SELECT *", str(T["tasks"]), str(S["tasks"])],
                             ["Bytes read, SELECT *", sz(T["input_bytes"]), sz(S["input_bytes"])],
                             ["Files for a one-day filter", str(RD['small_files']['t_date']['files']), str(RD['small_files']['s_date']['files'])],
                             ["Time, SELECT *", sec(T["seconds"]), sec(S["seconds"])]])
    return svg(1000, 205 + 6 * 30 + 12, "The same 200,000 rows stored in 20 files and in 400 files. The 400-file layout takes more bytes on disk, needs more tasks, opens 20 files instead of 1 for a one-day filter and is slower for select star.", i)


def table_svg(x, y, rows, col_w=(300, 220, 220), row_h=30):
    out = ""
    for r, row in enumerate(rows):
        xx = x
        for c, cell in enumerate(row):
            f = "w" if r else "y"
            out += bx(xx, y + r * row_h, col_w[c] - 4, row_h - 4, [cell], f, 13.5)
            xx += col_w[c]
    return out


def d_arrange():
    i = ""
    panels = [("As loaded", "each file = one date,\nall user_ids"), ("After Z-ORDER by user_id", "each file = a slice\nof user_ids"), ("Partitioned by country", "one folder per country")]
    for pn, (title, sub) in enumerate(panels):
        x0 = 20 + pn * 330
        i += t(x0 + 140, 22, title, 15, "middle")
        i += f'<rect x="{x0}" y="34" width="280" height="150" fill="#fff" stroke="#111" stroke-width="1.2"/>'
        if pn == 0:
            for k in range(20):
                i += f'<rect x="{x0 + 2 + k * 13.9:.1f}" y="36" width="12.5" height="146" fill="{FILLS["r"]}" stroke="#111" stroke-width="0.8"/>'
            i += f'<line x1="{x0}" y1="110" x2="{x0 + 280}" y2="110" stroke="#111" stroke-width="2" stroke-dasharray="6 4"/>'
            i += t(x0 + 140, 205, "user_id = 12345 crosses all 20 files", 13, "middle")
        elif pn == 1:
            for k in range(28):
                f = "g" if k == 12 else "w"
                i += f'<rect x="{x0 + 2}" y="{36 + k * 5.2:.1f}" width="276" height="5" fill="{FILLS[f]}" stroke="#111" stroke-width="0.5"/>'
            i += f'<line x1="{x0}" y1="{36 + 12 * 5.2 + 2.6:.1f}" x2="{x0 + 280}" y2="{36 + 12 * 5.2 + 2.6:.1f}" stroke="#111" stroke-width="2" stroke-dasharray="6 4"/>'
            i += t(x0 + 140, 205, f"crosses {Q['q4z_user_id_zorder']['files']} of {RD['zorder']['files']} files (measured)", 13, "middle")
        else:
            for k in range(10):
                f = "g" if k == 0 else "w"
                i += f'<rect x="{x0 + 2 + (k % 5) * 55:.0f}" y="{40 + (k // 5) * 72}" width="52" height="66" rx="4" fill="{FILLS[f]}" stroke="#111" stroke-width="1"/>'
            i += t(x0 + 140, 205, "country = 'IN' opens one folder", 13, "middle")
    i += t(500, 240, "Horizontal axis: event_date.  Vertical axis: user_id.  The dashed line is the filter. Every box it crosses has to be read.", 14, "middle")
    return svg(1000, 258, "Three ways to arrange the same data and what a filter on user_id or country crosses. As loaded, the filter line crosses all 20 date-ordered files. After Z-order by user_id, files are slices of user_ids and the line crosses one of 28 files. Partitioned by country, a filter on one country opens one folder.", i)


def d_chunks():
    cols = [("event_id", "event_id"), ("user_id", "user_id"), ("amount", "amount"), ("payload (random text)", "payload"), ("country (10 values)", "country"), ("f01 (few values)", "f01"), ("late_code (20 values)", "late_code")]
    i = t(10, 22, "Per column chunk, one 10,000-row file:   raw size (outline)  vs  on disk after compression (solid)", 14)
    mx = max(CH[c]["uncompressed"] for _, c in cols)
    y = 40
    for lab, c in cols:
        u, z = CH[c]["uncompressed"], CH[c]["compressed"]
        i += t(210, y + 22, lab, 14, "end")
        i += f'<rect x="220" y="{y + 4}" width="{max(2, 560 * u / mx):.0f}" height="24" rx="4" fill="#fff" stroke="#111" stroke-width="1.3"/>'
        i += f'<rect x="220" y="{y + 4}" width="{max(2, 560 * z / mx):.0f}" height="24" rx="4" fill="{FILLS["g"] if u / z > 3 else FILLS["y"]}" stroke="#111" stroke-width="1.3"/>'
        i += t(790, y + 22, f"{n(u)} → {n(z)} B  ({u / z:.1f}×)", 13)
        y += 38
    i += t(500, y + 18, f"Whole file: {n(FOOT['uncompressed_bytes'])} bytes raw → {n(FOOT['file_bytes'])} bytes on disk ({FOOT['uncompressed_bytes'] / FOOT['file_bytes']:.1f}×).", 15, "middle")
    return svg(1000, y + 34, "Seven column chunks from one real Parquet file, each shown as an outlined bar for its raw size and a solid bar for its compressed size. Columns with few distinct values (country, f01, late_code) shrink by more than ten times. Random numbers shrink about two times, and random text barely shrinks.", i)


def page_layout():
    S, T = RD["small_files"]["s_all"], RD["small_files"]["t_all"]
    body = (
        section("small", "The small file problem", "The same rows in 400 files instead of 20", p("Nothing about the data changed: same rows, same columns. Only the number of files did. Every file has its own footer to read and its own task to schedule, so many tiny files cost more than a few right-sized ones.") + fig(d_small_files(), "Measured on both layouts of the same 200,000 rows.")
                 + real(f"The 400-file layout used {sz(BD['S']['bytes'])} on disk against {sz(BD['T']['bytes'])} for 20 files ({BD['S']['bytes'] / BD['T']['bytes']:.1f}× more, because per-file overhead and weaker compression add up), needed {S['tasks']} tasks instead of {T['tasks']}, and a one-day filter opened {RD['small_files']['s_date']['files']} files instead of {RD['small_files']['t_date']['files']}. On a laptop disk the time difference is small ({sec(S['seconds'])} vs {sec(T['seconds'])}); on cloud storage each file is a separate request, which is likely to make it worse. That last point is general knowledge, not measured here.")
                 + ul(["<b>Where small files come from:</b> frequent small appends, streaming micro-batches, too many shuffle partitions at write time, and partitioning by a column with too many values.", "<b>The fix is compaction:</b> <code>OPTIMIZE</code> rewrites many small files into fewer big ones (the write-path page shows a real one: 20 files removed, 1 added)."]))
        + section("cols", "Columns and compression", "Why columnar files shrink, with real chunk sizes", p("Each column chunk is compressed on its own, and a chunk holds values of one type with many repeats. That is why column files shrink so well. The sizes below come from the footer of one real file.") + fig(d_chunks(), "Raw vs compressed size per column chunk. Few distinct values means big savings.")
                 + ul([f"<b>country</b> has 10 values: {n(CH['country']['uncompressed'])} → {n(CH['country']['compressed'])} bytes ({CH['country']['uncompressed'] / CH['country']['compressed']:.0f}×). The footer lists the encoding <code>{'PLAIN_DICTIONARY' if 'PLAIN_DICTIONARY' in CH['country']['encodings'] else CH['country']['encodings'][0]}</code>: store each distinct value once, then small numbers that point to it.",
                       f"<b>payload</b> is random text, so it barely shrinks ({CH['payload']['uncompressed'] / CH['payload']['compressed']:.2f}×) and is the biggest chunk on disk ({sz(CH['payload']['compressed'])}). That is why selecting only two columns read just {pct(Q['q2_two_columns']['input_bytes'], Q['q1_select_star']['input_bytes'])} of the bytes.",
                       "<b>Compression and skipping are one idea:</b> a column with few or ordered values is both smaller and easier to skip."]))
        + section("arrange", "Organising files", "Arrange the files so filters cross fewer of them", fig(d_arrange(), "Three arrangements of the same data. Only the first is free; the others need a write or OPTIMIZE.")
                 + table(["Technique", "What it does", "Good for", "Watch out"], [
                     ["<b>Partitioning</b>", "One folder per value of a column", "Low-cardinality columns you always filter on (country, date)", "Too many values makes many tiny files"],
                     ["<b>Z-order</b>", "Sorts data along several columns so similar values share files", "High-cardinality columns in filters", "Not combinable with liquid clustering; skip columns without statistics"],
                     ["<b>Liquid clustering</b> (Databricks)", "Clusters by up to four keys, adjusts without rewriting everything", "Replaces partitioning and Z-order for new tables (Databricks Runtime 15.4 LTS and later)", "Keys must have statistics, so be within the first 32 columns"],
                     ["<b>OPTIMIZE</b>", "Compacts small files, and applies Z-order or clustering", "Fixing small files", "Costs compute; predictive optimization can run it for managed tables"]])
                 + real(f"Z-ordering the main table by <code>user_id</code> (with a small target file size, so it produced {RD['zorder']['files']} files) turned the random-column query from {Q['q4_user_id']['files']} of {BD['T']['files']} files into {Q['q4z_user_id_zorder']['files']} of {RD['zorder']['files']}, and from {sz(Q['q4_user_id']['input_bytes'])} read to {sz(Q['q4z_user_id_zorder']['input_bytes'])}.")
                 + '<div class="box"><b>Not measured:</b> I could not run liquid clustering locally. Creating a <code>CLUSTER BY</code> table and running <code>OPTIMIZE</code> on open-source Delta 3.2.0 raised an error, so the liquid clustering rows are from the Databricks docs only. Z-order, which does the same job in the same family, was measured.</div>')
        + section("size", "File size", "How big should a file be", p("The Databricks docs say tables under 2.56 TB get a 256 MB target, growing linearly to 1 GB between 2.56 TB and 10 TB, and 1 GB above that. Unity Catalog managed tables tune this automatically. For others you can set <code>delta.targetFileSize</code>.")
                 + table(["Table size", "Target file", "Files (from the docs)"], [["1 TB", "256 MB", "about 4,096"], ["10 TB", "1 GB", "about 24,437"], ["100 TB", "1 GB", "about 114,437"]])
                 + ul(["<b>Auto compaction</b> (<code>delta.autoOptimize.autoCompact</code>) compacts small files after a write; <b>optimized write</b> (<code>delta.autoOptimize.optimizeWrite</code>) shuffles before writing so files come out a good size.", "<b>Predictive optimization</b> runs OPTIMIZE, VACUUM and ANALYZE for Unity Catalog managed tables, and is on by default, per the docs."]))
        + section("tips", "What to do", "Layout checklist", table(["Do", "Verdict"], [["Keep files near the target size; compact small ones", PURSUE], ["Cluster or Z-order by the columns you filter and join on", PURSUE], ["Partition only on low-cardinality columns", PURSUE], ["Partition by a high-cardinality column such as user_id", DROP], ["Leave thousands of tiny files and rely on a bigger cluster", DROP]]))
    )
    qa = [("What is the small file problem?", "Many tiny files mean many footers to read, many tasks to schedule and, on cloud storage, many requests. The same rows in 400 files instead of 20 took about 1.6 times the bytes on disk and opened 20 files instead of 1 for a one-day filter in the local test."),
          ("Why do columns compress better than rows?", "A column chunk holds values of one type with many repeats, so dictionary and run-length encoding work well. In the real file a 10-value column shrank about 14 times, while random text barely shrank."),
          ("Z-order or liquid clustering?", "On Databricks the docs recommend liquid clustering for new tables and say it replaces partitioning and Z-order. Z-order is still the older option and cannot be combined with liquid clustering. Only Z-order was measured here.")]
    return body, qa


# =================================================================== 4. joins
J = JN["joins"]
SH = JN["shuffles"]


def d_bhj():
    i = bx(10, 20, 220, 70, ["Small table", f"({sz(R['spark']['table_bytes']['dim_country'])} on disk)"], "g", 14)
    i += bx(10, 110, 220, 50, ["Driver collects it,", "then sends a copy"], "y", 13) + ar(120, 92, 120, 108)
    for k in range(3):
        y = 14 + k * 70
        i += bx(330, y, 330, 56, [f"Executor {k + 1}: its slice of the big table", "+ a full copy of the small table"], "b", 13)
        i += ar(232, 135, 328, y + 28)
    i += bx(720, 40, 270, 120, ["Each slice joins locally", f"shuffle written: {J['j1_big_small_broadcast']['shuffle_write_bytes']} bytes", "the big table never moves"], "g", 14)
    i += ar(662, 100, 718, 100)
    return svg(1000, 230, "Broadcast hash join. The small table is collected on the driver and a copy is sent to every executor. Each executor joins its own slice of the big table with that copy locally, so the big table is never shuffled and zero shuffle bytes are written.", i)


def d_smj():
    i = bx(10, 20, 200, 60, ["Big table A", "slices on many executors"], "b", 13) + bx(10, 110, 200, 60, ["Table B", "slices on many executors"], "b", 13)
    i += bx(270, 20, 200, 150, ["Shuffle by the", "join key", "same key lands on", "the same executor", f"{sz(J['j4_big_big_sortmerge']['shuffle_write_bytes'])} moved"], "r", 14)
    i += ar(212, 50, 268, 70) + ar(212, 140, 268, 120)
    i += bx(530, 20, 200, 150, ["Sort each side", "by the key", "then walk both", "lists together", "(merge)"], "y", 14) + ar(472, 95, 528, 95)
    i += bx(790, 20, 200, 150, ["Joined rows", "tasks: " + str(J['j4_big_big_sortmerge']['tasks']), f"time: {sec(J['j4_big_big_sortmerge']['seconds'])}"], "g", 14) + ar(732, 95, 788, 95)
    i += t(500, 205, "Both sides cross the network. This is the expensive path, and the one used when neither table is small.", 14, "middle")
    return svg(1000, 225, "Sort-merge join. Both tables are shuffled by the join key so equal keys land on the same executor, each side is sorted, and the two sorted lists are merged. About 35.8 MB was moved in this test.", i)


def d_aqe():
    i = bx(10, 20, 230, 80, ["Planned before running", "SortMergeJoin", "(sizes unknown)"], "r", 14)
    i += bx(290, 20, 230, 80, ["Both sides are shuffled", f"{sz(J['j4b_big_big_aqe_on']['shuffle_write_bytes'])} written", "now real sizes are known"], "y", 14) + ar(242, 60, 288, 60)
    i += bx(570, 20, 200, 80, ["One side is small", "enough to broadcast"], "w", 14) + ar(522, 60, 568, 60)
    i += bx(810, 20, 180, 80, ["Final plan:", J['j4b_big_big_aqe_on']['join_kind']], "g", 14) + ar(772, 60, 808, 60)
    i += t(500, 140, "AQE changes the plan using real sizes after the shuffle stage finishes. The shuffle itself was already paid for.", 15, "middle")
    i += t(500, 165, "So if you know a table is small, hint the broadcast up front instead of waiting for AQE.", 15, "middle")
    return svg(1000, 185, "Adaptive query execution at work. The plan starts as a sort-merge join. After both sides are shuffled the real sizes are known and one side is small enough to broadcast, so the final plan is a broadcast hash join. The shuffle has already happened by then.", i)


def d_dpp():
    off, on = J["j5_partitioned_dpp_off"], J["j5b_partitioned_dpp_on"]
    i = bx(10, 20, 230, 80, ["Small table filtered:", "region = 'AMER'", "→ US, BR"], "g", 14)
    i += bx(300, 20, 270, 80, ["Spark passes that list", "into the big table's scan", "before it reads"], "y", 14) + ar(242, 60, 298, 60)
    for k, c in enumerate(["IN", "US", "UK", "DE", "FR", "AU", "AE", "SG", "JP", "BR"]):
        hit = c in ("US", "BR")
        i += bx(10 + k * 70, 150, 64, 44, [c], "g" if hit else "w", 14, dash=not hit)
    i += t(10, 215, "partitions of the big table, one folder per country; dashed = never read", 13)
    i += bx(640, 20, 350, 80, ["Without it: " + f"{off['files']} files, {n(off['rows'])} rows", "With it:      " + f"{on['files']} files, {n(on['rows'])} rows"], "w", 14) + ar(572, 60, 638, 60)
    return svg(1000, 235, "Dynamic partition pruning. A small table is filtered to two countries. Spark hands that list of values to the scan of the big table, which is partitioned by country, so only the folders for those two countries are read: 6 files and 40,010 rows instead of 22 files and 200,010 rows.", i)


def d_skew():
    i = t(10, 22, "Rows per shuffle partition (illustration, not measured)", 14)
    sizes = [30, 36, 28, 34, 260, 31, 29, 33]
    for k, v in enumerate(sizes):
        w = v * 2.4
        i += f'<rect x="10" y="{34 + k * 24}" width="{w:.0f}" height="18" rx="4" fill="{FILLS["r"] if v > 100 else FILLS["g"]}" stroke="#111" stroke-width="1.2"/>'
    i += t(660, 34 + 4 * 24 + 14, "← one huge partition: one slow task", 14)
    i += bx(10, 240, 480, 56, ["Skew handling splits the huge partition into pieces", "so several tasks share the work"], "y", 14)
    i += bx(520, 240, 470, 56, ["Databricks defaults: a partition counts as skewed if it is", "5× the median and above 256 MB"], "w", 14)
    return svg(1000, 310, "An illustration of skew: eight shuffle partitions where seven are about the same size and one is many times larger, so one task runs far longer than the rest. Adaptive query execution splits the oversized partition. By Databricks defaults a partition counts as skewed when it is more than five times the median and above 256 MB.", i)


def page_joins():
    jt = lambda k: J[k]
    rows = [["big × small (10 rows), default", "BroadcastHashJoin", jt('j1_big_small_broadcast')['shuffle_write_bytes'], jt('j1_big_small_broadcast')['tasks'], sec(jt('j1_big_small_broadcast')['seconds'])],
            ["same, broadcast switched off", "SortMergeJoin", jt('j2_big_small_forced_sortmerge')['shuffle_write_bytes'], jt('j2_big_small_forced_sortmerge')['tasks'], sec(jt('j2_big_small_forced_sortmerge')['seconds'])],
            ["big × medium (50,000 rows)", "BroadcastHashJoin", jt('j3_big_medium_broadcast')['shuffle_write_bytes'], jt('j3_big_medium_broadcast')['tasks'], sec(jt('j3_big_medium_broadcast')['seconds'])],
            ["big × big (threshold lowered)", "SortMergeJoin", jt('j4_big_big_sortmerge')['shuffle_write_bytes'], jt('j4_big_big_sortmerge')['tasks'], sec(jt('j4_big_big_sortmerge')['seconds'])],
            ["big × big, AQE on", jt('j4b_big_big_aqe_on')['join_kind'] + " (AQE changed it)", jt('j4b_big_big_aqe_on')['shuffle_write_bytes'], jt('j4b_big_big_aqe_on')['tasks'], sec(jt('j4b_big_big_aqe_on')['seconds'])]]
    rows = [[a, b, f"{sz(c) if c else '0 B'}", d, e] for a, b, c, d, e in rows]
    body = (
        section("why", "The problem", "Why joins are the expensive part", p("A join has to bring matching rows together. If they already sit on the same machine that is cheap. If not, rows must <b>shuffle</b> across the network, and that is where most join time goes. Spark chooses between a few strategies to avoid or minimise the movement.") + "")
        + section("bhj", "Strategy 1: broadcast", "Big table with a small table: send the small one everywhere", fig(d_bhj(), "No shuffle of the big table at all.") + real(f"Joining the 200,000-row table to a 10-row table produced a <code>BroadcastHashJoin</code> with <b>{J['j1_big_small_broadcast']['shuffle_write_bytes']} bytes</b> shuffled. A 50,000-row table ({sz(R['spark']['table_bytes']['dim_user'])} on disk) was broadcast too.")
                  + ul(["<b>The limit:</b> a table is broadcast if it is below a size threshold. The Databricks AQE page lists <code>spark.databricks.adaptive.autoBroadcastJoinThreshold</code> at 30 MB for the run-time switch. The planning-time threshold default (10 MB in open-source Spark) was not re-checked because the Spark docs page was not reachable.", "<b>A broadcast table has to fit</b> in the driver and in every executor's memory. Broadcasting something too big is a classic cause of out-of-memory errors."]))
        + section("smj", "Strategy 2: sort-merge", "Big table with big table: shuffle both by the key", fig(d_smj(), "Both sides move. Nothing is small enough to copy.") + real(f"Switching broadcast off for the same join forced a <code>SortMergeJoin</code>: <b>{sz(J['j2_big_small_forced_sortmerge']['shuffle_write_bytes'])}</b> shuffled and {J['j2_big_small_forced_sortmerge']['tasks']} tasks instead of {J['j1_big_small_broadcast']['tasks']}. Two big tables joined on <code>event_id</code> shuffled {sz(J['j4_big_big_sortmerge']['shuffle_write_bytes'])}.")
                  + table(["Join (measured)", "Strategy", "Shuffle written", "Tasks", "Time"], rows)
                  + p("Times are small because the data is small. The shuffle bytes and task counts are what grow with the data. The Databricks docs say Photon replaces sort-merge joins with hash joins (see the Photon page)."))
        + section("aqe", "Adaptive query execution", "AQE: fixing the plan with real sizes", fig(d_aqe(), "AQE can only switch after it has measured the shuffle.") + real(f"With AQE on and the planning threshold lowered, the join that would have been a sort-merge ended as a <code>{J['j4b_big_big_aqe_on']['join_kind']}</code>, yet it still wrote {sz(J['j4b_big_big_aqe_on']['shuffle_write_bytes'])} of shuffle. This matches the Databricks docs, which say AQE only switches after both sides are shuffled and that a broadcast hint is still worth using when you know the sizes.")
                  + table(["AQE feature (Databricks docs)", "What it does", "Default"], [["Sort-merge to broadcast", "Switches when a side is small after the shuffle", "30 MB (<code>spark.databricks.adaptive.autoBroadcastJoinThreshold</code>)"], ["Coalesce partitions", "Merges many small shuffle partitions", "target 64 MB (<code>advisoryPartitionSizeInBytes</code>)"], ["Skew join", "Splits oversized partitions", "factor 5, 256 MB"], ["Empty relation propagation", "Drops work on empty inputs", "on"]]))
        + section("skew", "Skew", "When one key has most of the rows", fig(d_skew(), "One slow task holds up the whole stage.") + ul(["AQE splits skewed partitions for most join types, but never in a broadcast join, and not on the outer side of some outer joins (the docs list left-side handling for INNER, LEFT OUTER, LEFT SEMI, LEFT ANTI and right-side for INNER, RIGHT OUTER).", "The old <code>SKEW</code> hints are marked retired in the docs: AQE handles it by default.", "Skew was not measured here."]))
        + section("dpp", "Pruning through the join", "Dynamic partition pruning: let the small side shrink the big side", fig(d_dpp(), "The filter on the small table travels into the big table's scan.")
                  + real(f"Joining the table partitioned by country to the country table filtered to <code>region = 'AMER'</code>: without dynamic partition pruning {J['j5_partitioned_dpp_off']['files']} files and {n(J['j5_partitioned_dpp_off']['rows'])} rows were scanned; with it {J['j5b_partitioned_dpp_on']['files']} files and {n(J['j5b_partitioned_dpp_on']['rows'])} rows, and the plan contained <code>dynamicpruning</code>. It needs a broadcast of the filtered side to work, so turning broadcast off in the first attempt switched it off too.")
                  + ul(["<b>Databricks adds dynamic file pruning</b> (not measured): for joins on Delta tables it pushes the small side's values into the big Delta table's scan to skip <i>files</i>, not only partitions. Per the docs it is on by default (<code>spark.databricks.optimizer.dynamicFilePruning</code>), applies when the big table is above 10 GB and 10 files, works best on non-partitioned tables, and needs Photon for MERGE, UPDATE and DELETE."]))
        + section("layout", "Layout helps joins", "How organising files speeds up joins", table(["Arrangement", "Helps because", "Source"], [["Partition by a low-cardinality join column", "Partition pruning, and dynamic partition pruning from the other side", "Measured above"], ["Cluster or Z-order by the join key", "Narrow min/max per file, so pushed-down key values skip files", "Z-order measured on filters; join effect from the Databricks docs"], ["Keep the small side small and broadcast-able", "No shuffle of the big table", "Measured above"], ["Compact small files", "Fewer, bigger tasks on both sides", "Measured on layout page"]])
                  + p("The Databricks dynamic file pruning page recommends liquid clustering on frequently joined columns and Photon-enabled compute."))
        + section("choose", "Choosing", "Which join, when", table(["Situation", "Expect", "Verdict"], [["One side is small", "Broadcast hash join, no shuffle", PURSUE], ["Both sides large, same key", "Sort-merge join, plan for the shuffle", PURSUE], ["You know a side is small but stats are missing", "Add a broadcast hint instead of waiting for AQE", PURSUE], ["Broadcasting a big table", "Out-of-memory risk", DROP], ["Joining on a column with a few huge keys", "Skew: check the plan and the task times", DROP]]))
    )
    qa = [("What is the difference between a broadcast join and a sort-merge join?", "A broadcast join copies the small table to every executor, so the big table is never moved. A sort-merge join shuffles both tables by the join key, sorts them and merges them. In the local test the broadcast join wrote 0 bytes of shuffle and the sort-merge wrote 32.6 MB for the same data."),
          ("Does AQE avoid the shuffle?", "No. It uses the real sizes after the shuffle stage to change the plan, for example to a broadcast join, so the shuffle that produced those sizes has already happened."),
          ("What is dynamic partition pruning?", "When a join's other side is filtered to a few values, Spark passes those values to the big table's scan so only matching partitions are read. Here it cut 22 files and 200,010 rows to 6 files and 40,010 rows.")]
    return body, qa


# =================================================================== 5. inside spark
def d_narrow_wide():
    i = t(10, 22, "Narrow: each output partition depends on one input partition", 15)
    for k in range(3):
        i += bx(10, 36 + k * 44, 120, 36, [f"partition {k + 1}"], "b", 13) + ar(132, 54 + k * 44, 198, 54 + k * 44) + bx(200, 36 + k * 44, 190, 36, ["filter + select"], "g", 13) + ar(392, 54 + k * 44, 458, 54 + k * 44) + bx(460, 36 + k * 44, 120, 36, [f"partition {k + 1}"], "b", 13)
    i += t(620, 22, "Wide: output partitions need data from many inputs", 15)
    for k in range(3):
        i += bx(620, 36 + k * 44, 100, 36, [f"input {k + 1}"], "b", 13)
        i += bx(880, 36 + k * 44, 100, 36, [f"output {k + 1}"], "r", 13)
        for m in range(3):
            i += f'<line x1="722" y1="{54 + k * 44}" x2="878" y2="{54 + m * 44}" stroke="#111" stroke-width="1"/>'
    i += t(300, 190, "No data moves between machines.", 14, "middle") + t(800, 190, "Rows are sent across the network: a shuffle.", 14, "middle")
    i += t(500, 225, "Narrow steps are chained into one stage. Every wide step starts a new stage.", 15, "middle")
    return svg(1000, 240, "Narrow and wide transformations. Narrow: filter and select work on each partition independently and keep partitions one to one. Wide: output partitions need rows from many input partitions, drawn as crossing lines, which is a shuffle. Narrow steps chain into one stage; each wide step starts a new stage.", i)


def d_exchanges():
    kinds = [("hash", "hashpartitioning", "groupBy, join, window,", "distinct", "same key goes to the same partition"),
             ("range", "rangepartitioning", "orderBy", "", "sorted ranges per partition"),
             ("round robin", "RoundRobinPartitioning", "repartition(n)", "", "rows dealt out evenly"),
             ("single", "SinglePartition", "global aggregate,", "limit", "everything to one partition"),
             ("broadcast", "BroadcastExchange", "broadcast join", "", "a copy to every executor")]
    i = ""
    for k, (name, plan, who1, who2, what) in enumerate(kinds):
        x = 10 + k * 198
        i += bx(x, 20, 186, 34, [name], ["b", "y", "g", "r", "l"][k], 15)
        i += bx(x, 64, 186, 56, [l for l in (who1, who2) if l], "w", 13)
        i += bx(x, 130, 186, 50, [what], "w", 12.5)
        i += bx(x, 190, 186, 34, [plan], "w", 12)
    return svg(1000, 240, "The five kinds of exchange in a Spark plan: hash partitioning for group by, join, window and distinct; range partitioning for order by; round robin for repartition; single partition for global aggregates and limits; and broadcast, a copy to every executor for broadcast joins.", i)


def d_driver():
    d = SP["driver"]
    rows = [("count()", d["count"]["result_bytes"], "r_"), ("take(5)", d["take5"]["result_bytes"], ""), ("show(20)", d["show20"]["result_bytes"], ""), ("groupBy.agg().collect()", d["agg_then_collect"]["result_bytes"], ""),
            ("write to a table (noop sink)", d["write_noop"]["result_bytes"], ""), ("collect() of 2 columns", d["collect_2_cols"]["result_bytes"], ""), ("collect() of all 40 columns", d["collect_all_cols"]["result_bytes"], "")]
    bars = []
    for lab, v, _ in rows:
        f = "g" if v < 1e5 else ("y" if v < 5e6 else "r")
        bars.append((lab, v, sz(v), f))
    a, y = hbars(bars, 10, 30, 300, 520, 32)
    i = t(10, 22, "Bytes the tasks sent back to the driver", 15) + a
    i += t(500, y + 22, "Almost everything stays on the executors. Only collect-style actions ship the data itself.", 14, "middle")
    return svg(1000, y + 40, "Bytes returned to the driver by seven actions. count, take, show, an aggregate then collect, and a write return only kilobytes. collect of two columns returns 2.2 MB and collect of all 40 columns returns 33.1 MB.", i)


def d_cache():
    c = SP["cache"]
    i = bx(10, 20, 170, 60, ["Parquet files", f"{sz(BD['T']['bytes'])} on disk"], "r", 14)
    i += bx(260, 20, 220, 60, ["cache() / persist()", "first action fills it"], "y", 14) + ar(182, 50, 258, 50, label="read once", lx=220, ly=40)
    i += bx(560, 20, 200, 60, ["Executor memory", f"{sz(max(x['memSize'] for x in c['storage']))} held"], "g", 14) + ar(482, 50, 558, 50)
    i += bx(820, 20, 170, 60, ["Later actions", "read memory"], "b", 14) + ar(762, 50, 818, 50)
    i += t(500, 120, f"Before the cache: {c['before']['files']} files read. After: {c['after']['files']} files read. Time {sec(c['before']['seconds'])} → {sec(c['after']['seconds'])} (tiny table).", 15, "middle")
    i += t(500, 146, f"The cache holds every column it was given, decoded: {sz(max(x['memSize'] for x in c['storage']))} in memory against {sz(BD['T']['bytes'])} of compressed Parquet.", 15, "middle")
    return svg(1000, 165, "How caching changes a select. The first action reads the Parquet files and stores the data in executor memory. Later actions read memory instead of files. The cache stores the data decoded, so it is larger than the compressed files.", i)


def page_inside_spark():
    d, c = SP["driver"], SP["cache"]
    srows = [["<code>filter + select</code>", "narrow", "none", "0 B", SH["narrow_filter_select"]["tasks"]],
             ["<code>groupBy('country').sum()</code>", "wide", "hash", sz(SH["wide_groupby"]["shuffle_write_bytes"]), SH["wide_groupby"]["tasks"]],
             ["<code>distinct()</code>", "wide", "hash", sz(SH["wide_distinct"]["shuffle_write_bytes"]), SH["wide_distinct"]["tasks"]],
             ["<code>orderBy('amount')</code>", "wide", "range", sz(SH["wide_orderby"]["shuffle_write_bytes"]), SH["wide_orderby"]["tasks"]],
             ["<code>repartition(8)</code>", "wide", "round robin", sz(SH["wide_repartition"]["shuffle_write_bytes"]), SH["wide_repartition"]["tasks"]],
             ["window <code>partitionBy('country')</code>", "wide", "hash", sz(SH["wide_window"]["shuffle_write_bytes"]), SH["wide_window"]["tasks"]]]
    body = (
        section("nw", "Narrow and wide", "The one idea that explains most Spark performance", p("Some steps work on each slice of data on its own (<b>narrow</b>). Others need rows from many slices to meet (<b>wide</b>) and so move data across the network. Narrow steps are cheap and chain together. Wide steps cost a shuffle and cut the job into <b>stages</b>.") + fig(d_narrow_wide(), "Lines that cross are the cost.")
                  + table(["Operation", "Kind", "Exchange", "Shuffle written (measured)", "Tasks"], srows)
                  + real(f"The surprise is in the bytes. <code>groupBy</code> and <code>distinct</code> shuffled only {sz(SH['wide_groupby']['shuffle_write_bytes'])} and {sz(SH['wide_distinct']['shuffle_write_bytes'])}, because Spark first aggregates inside each partition and shuffles only the partial results. <code>orderBy</code>, <code>repartition</code> and a window moved the whole dataset: about {sz(SH['wide_orderby']['shuffle_write_bytes'])}, {sz(SH['wide_repartition']['shuffle_write_bytes'])} and {sz(SH['wide_window']['shuffle_write_bytes'])}, which is bigger than the {sz(BD['T']['bytes'])} of compressed Parquet because shuffle data is not column-compressed that way."))
        + section("kinds", "Kinds of shuffle", "Five kinds of exchange, one for each job", fig(d_exchanges(), "Each exchange line in a plan names how rows are redistributed.")
                  + ul(["<b>Hash</b>: rows with the same key go to the same partition. Used by group by, join and window.", "<b>Range</b>: rows are split into sorted ranges. Used by order by. Spark first samples the data to pick the boundaries (general knowledge; the order by query ran an extra stage in the local test).", "<b>Round robin</b>: rows are dealt out evenly, ignoring content. Used by repartition(n).", "<b>Single partition</b>: everything goes to one place, so avoid it for big data.", "<b>Broadcast</b>: a small table is copied to every executor."]))
        + section("when", "When work actually happens", "Nothing runs until an action", p("DataFrame steps like <code>filter</code> and <code>select</code> are <b>transformations</b>: they only extend a plan. Work starts when an <b>action</b> is called: <code>count</code>, <code>collect</code>, <code>show</code>, <code>write</code>. Then the driver turns the plan into stages at each exchange, and tasks run on executors.")
                  + table(["Call", "Kind", "What happens"], [["<code>spark.read…</code>, <code>.filter()</code>, <code>.select()</code>, <code>.join()</code>", "transformation", "The plan grows. No files are read. (A Delta read does load the log to know the schema.)"], ["<code>.explain()</code>", "plan only", "Prints the plan without running it."], ["<code>.count()</code>, <code>.collect()</code>, <code>.show()</code>, <code>.write…</code>", "action", "The plan is optimised, split into stages and run."], ["<code>.cache()</code>", "marker", "Nothing is stored until the first action runs."]]))
        + section("driver", "What travels to the driver", "Most actions send almost nothing back", fig(d_driver(), "Measured bytes returned to the driver by each action.")
                  + ul([f"<b>count()</b>: each task sends one number. {sz(d['count']['result_bytes'])} in total, including the small log-reading tasks.", f"<b>take(5) and show()</b>: only as many partitions as needed are scanned ({d['take5']['tasks']} tasks), and a few rows come back.", f"<b>write</b>: the data stays on the executors and goes straight to storage; the driver only sees {sz(d['write_noop']['result_bytes'])} of task results.", f"<b>collect()</b>: every row is sent to the driver. 200,000 rows of 2 columns was {sz(d['collect_2_cols']['result_bytes'])} ({sec(d['collect_2_cols']['seconds'])}); all 40 columns was {sz(d['collect_all_cols']['result_bytes'])} ({sec(d['collect_all_cols']['seconds'])}). At billions of rows this is the classic way to crash a driver.", "<b>A broadcast join</b> also routes the small table through the driver before copying it out (general Spark behaviour, not measured). <code>toPandas()</code> is a collect and has the same limit; it was not measured because pandas is not installed in the test environment."])
                  + '<div class="box"><b>The safety limit.</b> Spark caps the total result size with <code>spark.driver.maxResultSize</code>. I believe its default is 1 GB, but I did not re-check that against the docs.</div>')
        + section("cache", "Caching", "What cache() does to a select", fig(d_cache(), "Cache moves reads from files to memory, at a memory cost.")
                  + real(f"On the {sz(BD['T']['bytes'])} table, a cached query read {c['after']['files']} files instead of {c['before']['files']} and ran in {sec(c['after']['seconds'])} against {sec(c['before']['seconds'])}. The table is tiny, so the win is small here; at scale the saving is the I/O. The cached data took {sz(max(x['memSize'] for x in c['storage']))} of memory for the whole table, more than the {sz(BD['T']['bytes'])} of files, because it keeps every column decoded.")
                  + ul(["<b>Select first, cache second.</b> Cache only the columns and rows you will reuse; caching a 40-column DataFrame stores all 40.", "<b>Cache only what you reuse.</b> If it is read once it is pure cost.", "Delta also caches its own log state in small cached datasets, which showed up as extra entries in the storage list.", "Databricks adds a separate <b>disk cache</b> for remote files on local SSD on supported compute. It is covered in the <a href=\"/learn/databricks-compute/photon-and-caches/\">compute guide</a> and was not measured here."]))
        + section("tips", "What to do", "Rules that follow", table(["Do", "Verdict"], [["Chain narrow steps; count the exchanges in the plan", PURSUE], ["Reduce data before a wide step (filter, select, aggregate)", PURSUE], ["Use take, show or write instead of collect on big data", PURSUE], ["Collect a large table to the driver", DROP], ["Cache a DataFrame you read once", DROP]]))
    )
    qa = [("What is the difference between narrow and wide transformations?", "Narrow transformations such as filter and select work on one partition at a time and need no data movement. Wide transformations such as group by, join and order by need rows from many partitions and cause a shuffle, which starts a new stage."),
          ("Why did group by shuffle so little data?", "Spark first aggregates within each partition and shuffles only the partial results. In the local test a group by moved 838 bytes while an order by of the same table moved 32.6 MB."),
          ("What gets sent to the driver?", "Only what the action returns. count, take, show and write send kilobytes. collect sends every row, 33.1 MB for all 40 columns of 200,000 rows in the test, which is how drivers run out of memory on large tables.")]
    return body, qa


# =================================================================== 6. python and the JVM
PJ = SP["pyjvm"]


def d_proc():
    i = bx(10, 20, 220, 110, ["Your Python process", "the driver program", f"process id {PJ['driver_python_pid']}", "df = spark.read…"], "b", 14)
    i += bx(330, 20, 230, 110, ["The JVM (Spark driver)", f"process id {PJ['jvm_pid']}", "builds the plan, runs the", "scheduler, holds the log state"], "y", 14)
    i += ar(232, 75, 328, 75, label="Py4J", lx=280, ly=62) + ar(328, 90, 232, 90)
    i += bx(660, 20, 160, 50, ["Executor JVM tasks"], "g", 14) + bx(660, 80, 160, 50, ["…do the real work"], "g", 14)
    i += ar(562, 75, 658, 50)
    i += bx(850, 20, 140, 110, ["Python workers", "only for UDFs", f"ids {PJ['worker_pids'][0]}, {PJ['worker_pids'][1]}"], "r", 13)
    i += ar(822, 100, 848, 100) + ar(848, 112, 822, 112)
    i += t(500, 170, "Your Python code never touches the data. It sends instructions to the JVM over a socket (Py4J).", 15, "middle")
    i += t(500, 196, f"The DataFrame object in Python is a thin handle to a JVM object of type {PJ['df_jvm_type']}.", 14, "middle")
    return svg(1000, 215, "The PySpark process picture. Your Python program (one process id) talks over the Py4J bridge to the Spark JVM (a different process id). The JVM runs the plan and the executor tasks. Separate Python worker processes exist only when Python code such as a UDF has to run on the data.", i)


def d_udf():
    i = bx(10, 20, 200, 90, ["JVM executor", "rows in columnar", "or row form"], "g", 14)
    i += bx(300, 20, 200, 90, ["Serialise rows", "(pickle, in batches)"], "y", 14) + ar(212, 55, 298, 55, label="rows out", lx=255, ly=44)
    i += bx(590, 20, 200, 90, ["Python worker", "runs your lambda", "row by row"], "r", 14) + ar(502, 55, 588, 55)
    i += bx(10, 150, 200, 60, ["JVM continues", "with the result"], "g", 14)
    i += bx(300, 150, 200, 60, ["Deserialise", "results back"], "y", 14) + ar(590, 95, 502, 160)
    i += ar(298, 180, 212, 180)
    i += bx(830, 20, 160, 190, ["The cost", "every value is", "copied out of the", "JVM and back,", "and the optimizer", "cannot see inside", "your lambda"], "w", 13)
    return svg(1000, 230, "What a Python UDF does. Rows leave the JVM executor, are serialised in batches, sent to a separate Python worker that runs the function row by row, and the results are serialised back and returned to the JVM. Every value is copied out and back, and the optimizer cannot see inside the function.", i)


def page_python_and_jvm():
    r = PJ["runs"]
    sp, bi = r["python_udf"], r["builtin_expr"]
    d = SP["driver"]
    body = (
        section("proc", "Two processes", "Python is the remote control, the JVM is the engine", p("PySpark is not Spark rewritten in Python. Spark runs on the JVM. Your Python program starts that JVM and sends it instructions through a bridge called <b>Py4J</b>. When you write <code>df.filter(...)</code> you are not filtering anything: you are asking the JVM to add a step to its plan.") + fig(d_proc(), "Two separate processes, and extra Python workers only when Python code must run on the data.")
                  + real(f"Real process ids from the run: the Python driver program was process <b>{PJ['driver_python_pid']}</b>, the Spark JVM was <b>{PJ['jvm_pid']}</b> (Java {PJ['jvm_java_version']}), and the Python workers that ran a UDF were <b>{PJ['worker_pids'][0]}</b> and <b>{PJ['worker_pids'][1]}</b>. The Python <code>DataFrame</code> object wrapped a JVM <code>{PJ['df_jvm_type']}</code>."))
        + section("api", "What stays in the JVM", "Built-in functions never leave the JVM", p("<code>filter</code>, <code>select</code>, <code>join</code>, <code>groupBy</code> and the functions in <code>pyspark.sql.functions</code> are all instructions that the JVM executes itself. No data is sent to Python. Their speed is the same as Scala or SQL, because the work is the same.")
                  + table(["You write", "Runs in", "Python sees data?"], [["<code>df.filter(F.col('amount') &gt; 800)</code>", "JVM", "No"], ["<code>F.col('amount') * 1.1</code>", "JVM", "No"], ["<code>df.groupBy(...).agg(F.sum(...))</code>", "JVM", "No"], ["<code>udf(lambda x: x * 1.1)</code>", "Python workers", "Yes, every value"], ["<code>df.rdd.map(lambda r: ...)</code>", "Python workers", "Yes, every row"], ["<code>df.collect()</code> / <code>df.toPandas()</code>", "JVM, then driver Python", "Yes, all rows"]]))
        + section("udf", "The cost of a Python UDF", "Same arithmetic, written two ways", fig(d_udf(), "Every row makes a round trip to a Python process.")
                  + real(f"Multiplying a column by 1.1 on 200,000 rows: the built-in expression took <b>{sec(bi['seconds'])}</b> and its plan had no Python step; the Python UDF took <b>{sec(sp['seconds'])}</b> ({sp['seconds'] / bi['seconds']:.1f}× slower) and its plan contained a <code>BatchEvalPython</code> node. An equivalent <code>rdd.map(lambda …)</code> took {sec(PJ['rdd_lambda_seconds'])}. Treat the ratio as indicative: on other data and hardware it will differ.")
                  + ul(["<b>Why slower:</b> each value is copied out of the JVM, run through Python, and copied back. The optimizer also cannot push a filter through the lambda or fuse it with neighbouring steps.", "<b>Arrow and pandas UDFs</b> move data in column batches instead of row by row and are the usual faster option, but they need PyArrow, which was not installed in the test environment, so they were not measured.", "<b>The fix is usually built-in functions.</b> Check <code>pyspark.sql.functions</code> before writing a UDF."]))
        + section("collect", "Conversion at the edge", "What collect() converts, and why it is slow", p("The JVM holds rows in its own format. <code>collect()</code> must serialise every row, send it to the driver process, and build a Python object for each one. That is conversion work on top of the network transfer.")
                  + table(["Action", "Result size", "Time", "Why"], [["<code>groupBy.agg().collect()</code>", sz(d["agg_then_collect"]["result_bytes"]), sec(d["agg_then_collect"]["seconds"]), "A few summary rows"], ["<code>collect()</code>, 2 columns", sz(d["collect_2_cols"]["result_bytes"]), sec(d["collect_2_cols"]["seconds"]), "200,000 small rows to Python"], ["<code>collect()</code>, 40 columns", sz(d["collect_all_cols"]["result_bytes"]), sec(d["collect_all_cols"]["seconds"]), "Same rows, 15× the bytes"]])
                  + p("The rule: aggregate or filter in Spark, and collect only the small result."))
        + section("tips", "What to do", "Python and JVM rules", table(["Do", "Verdict"], [["Use built-in functions and SQL expressions", PURSUE], ["Use Arrow or pandas UDFs when you must run Python", PURSUE], ["Collect only small, aggregated results", PURSUE], ["Write a row-by-row Python UDF for something a built-in can do", DROP], ["Loop over a collected DataFrame in Python", DROP]]))
    )
    qa = [("Does PySpark process data in Python?", "No. Your Python program sends instructions to the Spark JVM over Py4J, and the JVM runs the plan. Python only touches data if you use a UDF, an RDD lambda, or collect results."),
          ("How much slower is a Python UDF?", "About 2 times slower than the equivalent built-in expression in the local test, 0.25 seconds against 0.13 seconds for 200,000 rows, and the plan shows a BatchEvalPython step. The gap grows with more data."),
          ("What is the difference between a Python UDF and a pandas UDF?", "A Python UDF handles one row at a time. A pandas UDF (Arrow-based) handles column batches, which reduces conversion cost. Pandas UDFs need PyArrow, which was not available in the local test, so only the plain UDF was measured.")]
    return body, qa


# =================================================================== 7. photon
def d_rowbatch():
    i = t(250, 22, "One row at a time through each step", 15, "middle") + t(750, 22, "A batch of values through each step", 15, "middle")
    for k in range(4):
        i += bx(10 + k * 120, 40, 110, 40, [["scan", "filter", "project", "aggregate"][k]], "b", 13)
        if k < 3: i += ar(122 + k * 120, 60, 128 + k * 120, 60)
    for k in range(6):
        i += f'<rect x="{10 + k * 78}" y="100" width="70" height="26" rx="4" fill="{FILLS["r"]}" stroke="#111" stroke-width="1.1"/>' + t(45 + k * 78, 118, f"row {k + 1}", 12, "middle")
    i += t(250, 150, "each row pays the call overhead of every step", 13, "middle")
    for k in range(4):
        i += bx(520 + k * 120, 40, 110, 40, [["scan", "filter", "project", "aggregate"][k]], "g", 13)
        if k < 3: i += ar(632 + k * 120, 60, 638 + k * 120, 60)
    i += f'<rect x="520" y="100" width="470" height="26" rx="4" fill="{FILLS["g"]}" stroke="#111" stroke-width="1.1"/>' + t(755, 118, "a whole column of values, processed in a tight loop", 13, "middle")
    i += t(755, 150, "the call overhead is paid once per batch", 13, "middle")
    return svg(1000, 170, "Row-at-a-time versus vectorised execution. Left: each row passes through scan, filter, project and aggregate one at a time, paying the overhead of each step for every row. Right: a batch of values for a column passes through each step in a tight loop, paying the overhead once per batch.", i)


def d_photon_where():
    i = bx(10, 20, 200, 70, ["Your query", "SQL / DataFrame"], "b", 14) + ar(212, 55, 268, 55)
    i += bx(270, 20, 230, 70, ["Spark's planner (Catalyst)", "still plans the query, in the JVM"], "y", 14) + ar(502, 55, 558, 55)
    i += bx(560, 20, 200, 70, ["Photon", "native C++ engine runs", "the supported operators"], "g", 14)
    i += bx(790, 20, 200, 70, ["Plain Spark", "runs anything Photon", "cannot (falls back)"], "w", 14) + ar(762, 70, 788, 70)
    i += t(500, 125, "Per the Databricks docs: Photon replaces the JVM execution layer for supported operations. Unsupported operations fall back to Spark.", 14, "middle")
    return svg(1000, 145, "Where Photon sits. The query is still planned by Spark's Catalyst optimizer in the JVM. Photon, a native C++ engine, then runs the supported operators, and anything it cannot run falls back to regular Spark execution.", i)


def page_photon():
    body = (
        '<div class="box"><b>Read this first.</b> Photon only exists on Databricks, so nothing on this page was measured on the laptop. It is written from the Databricks documentation, and the one local observation (the open-source plan) is marked. Where the reason is general knowledge rather than from the docs, it says so.</div>'
        + section("problem", "The problem", "Spark on the JVM spends a lot of time not computing", p("Open-source Spark runs its operators on the JVM. For a long time the main cost was <i>doing the arithmetic on one row at a time</i>, with objects allocated for rows, garbage to collect, and a function call per row for every step. As disks and networks got faster, the CPU became the bottleneck, and that overhead stood out.") + fig(d_rowbatch(), "The idea behind vectorised engines: pay the overhead once per batch, not once per row."))
        + section("solve", "How it solves it", "A native, vectorised engine in place of the JVM execution layer", fig(d_photon_where(), "Photon replaces the execution, not the planning.")
                  + table(["What changes (Databricks docs)", "Effect"], [["Native C++ vectorised engine replaces the JVM execution layer", "No per-row JVM overhead for supported operators"], ["Replaces sort-merge joins with hash joins", "Cheaper joins (see the joins page)"], ["Columnar shuffle", "Data stays column-shaped when it moves between executors"], ["Scan: filter pushdown, dictionary pruning, row-group skipping", "Less data decoded at the file reader"], ["Predictive I/O requires Photon", "Faster selective reads on supported tables"], ["Dynamic file pruning in MERGE, UPDATE, DELETE requires Photon", "Fewer files rewritten (see the write page)"]])
                  + ul(["<b>Why native code is faster</b> (general knowledge, not in the docs I read): no garbage collector, no object per row, and tight loops over arrays that CPUs handle well. The docs say it is <i>vectorised</i>; I did not read a figure for any speed-up.", "<b>Local observation, open-source Spark:</b> the real plans show <code>FileScan parquet … Batched: true</code> followed by <code>ColumnarToRow</code>. Open-source Spark reads Parquet in column batches but then converts to rows for most later steps. Photon's pitch is to avoid that conversion for supported operators; I could not verify that locally."]))
        + section("covers", "What it covers", "Operators, and what it cannot do", table(["Covered (docs)", "Not covered (docs)"], [["Scans (Parquet, Delta, CSV, JSON), filter, project, hash aggregate, hash join, hash shuffle, nested-loop join, union, sort, top-k, limit, window, Delta and Parquet write", "UDFs, RDD APIs, Dataset APIs"], ["Null-aware anti join, spatial join, expand, scalar subquery", "Stateful streaming"], ["", "Queries shorter than about 2 seconds see no meaningful benefit"]])
                  + ul(["<b>Where it is on:</b> by default for serverless, SQL warehouses and serverless pipelines. On classic compute, jobs and classic pipelines it is on by default with a Use Photon Acceleration switch; the APIs use <code>runtime_engine = PHOTON</code>."]))
        + section("see", "Seeing it", "How to tell Photon ran", ul(["<b>Spark UI:</b> Photon operators show in orange in the DAG.", "<b>Query profile:</b> Photon operators show in purple, and the profile gives the percentage of task time spent in Photon.", "<b>If a step is not Photon,</b> it ran in regular Spark. A Python UDF in the middle is the usual reason."]) + p("A query that is mostly Photon operators with one UDF in the middle will fall back for that step and pay the conversion in and out."))
        + section("tips", "When it helps", "A short guide", table(["Workload", "Expect", "Verdict"], [["Big scans, joins, aggregations, MERGE on Delta", "Biggest gains (per the docs' operator list)", PURSUE], ["Short queries under about 2 seconds", "No meaningful benefit", DROP], ["Heavy use of Python UDFs or RDD code", "Falls back to Spark", DROP], ["Anything waiting on slow storage rather than CPU", "Little to gain (general reasoning, not from the docs)", DROP]]) + p('See also the cost side in the <a href="/learn/databricks-compute/photon-and-caches/">Photon and caches</a> compute page.'))
    )
    qa = [("What does Photon replace?", "The JVM execution layer for supported operators. Spark's Catalyst optimizer still plans the query; Photon then runs the supported operators in a native C++ vectorised engine, and unsupported operations fall back to regular Spark."),
          ("When does Photon not help?", "Per the Databricks docs it does not run UDFs, RDD or Dataset APIs, or stateful streaming, and queries under about two seconds see no meaningful benefit."),
          ("How can I see whether a query used Photon?", "In the Spark UI Photon operators appear in orange, and in the query profile they appear in purple with the share of task time spent in Photon.")]
    return body, qa


# =================================================================== 8. plan and UI
SUM = R["count"]["sum_amount"]["full_plan"]


def d_plan():
    plan = ["HashAggregate(sum(amount))", "  Exchange SinglePartition", "    HashAggregate(partial_sum(amount))", "      ColumnarToRow", "        FileScan parquet [amount]  Batched: true"]
    i = ""
    fills = ["g", "r", "g", "w", "y"]
    labs = ["4  final sum of the partial sums", "3  shuffle: send partials to one place", "2  partial sum inside each partition", "1b convert column batches to rows", "1a read only the amount column"]
    for k, (ln, f, lab) in enumerate(zip(plan, fills, labs)):
        y = 14 + k * 50
        i += bx(10, y, 470, 40, [ln.strip()], f, 13.5)
        i += t(500, y + 25, lab, 14)
    i += t(10, 275, "Read plans from the bottom up: data flows from the scan at the bottom to the result at the top.", 15)
    return svg(1000, 295, "A real query plan for SELECT SUM(amount), read from the bottom: the scan reads only the amount column in batches, a conversion to rows, a partial sum inside each partition, a shuffle to a single partition, and a final sum at the top.", i)


def d_tools():
    tools = [("EXPLAIN", "before running", "scan filters, join kind, exchanges", "b"), ("Spark UI: SQL / Stages", "after running", "time, bytes, shuffle, spill, skew", "y"), ("Query profile (Databricks)", "after running", "pruning %, operator time, memory", "g"),
             ("DESCRIBE DETAIL", "table now", "numFiles, sizeInBytes", "l"), ("DESCRIBE HISTORY", "table past", "what each write changed", "l"), ("_delta_log", "raw truth", "actions, stats, DVs", "r")]
    i = ""
    for k, (name, when, what, f) in enumerate(tools):
        x = 10 + (k % 3) * 330
        y = 14 + (k // 3) * 110
        i += bx(x, y, 316, 96, [name, when, what], f, 14)
    return svg(1000, 240, "Six places to look: EXPLAIN shows the plan before the query runs; the Spark UI shows time, bytes, shuffle and skew after it runs; the Databricks query profile shows pruning percent, operator time and memory; DESCRIBE DETAIL shows the table's current file count and size; DESCRIBE HISTORY shows what each write changed; and the delta log is the raw record.", i)


def page_plan_and_ui():
    q1, q3 = Q["q1_select_star"], Q["q3_event_date"]
    body = (
        section("plan", "Reading a plan", "The plan is a recipe: read it from the bottom", fig(d_plan(), "A real plan from the run, annotated.")
                + '<pre class="code">' + E("\n".join(SUM[:5]).replace("plan_id=", "id=")[:600]) + "</pre>"
                + ul(["<b>The bottom node is the scan.</b> <code>FileScan parquet [amount]</code> lists only the columns it will read, and the plan lists the filters it handed to the reader as <code>PushedFilters</code>. For the one-day query the plan showed <code>PushedFilters: [IsNotNull(event_date), EqualTo(event_date,2026-01-10)]</code>.", "<b>An <code>Exchange</code> is a shuffle.</b> Count them: each one is a stage boundary and a network cost.", "<b>The join node tells you the strategy:</b> <code>BroadcastHashJoin</code>, <code>SortMergeJoin</code> and so on.", "<b>Stars like <code>*(1)</code></b> mark steps fused into one generated-code stage."]))
        + section("map", "When to look at what", "Six places to look", fig(d_tools(), "Each tool answers a different question.")
                  + table(["Symptom", "Look at", "What you will see"], [
                      ["A query is slow and you want to know why before running it", "<code>EXPLAIN FORMATTED</code>", "Scan filters, columns read, join kind, number of exchanges"],
                      ["A query is slow after running", "Spark UI, Stages and SQL tabs; Databricks query profile", "Which stage or operator took the time; skewed tasks; spills"],
                      ["A filter should have skipped files but did not", "Scan node metrics: files read, bytes read; the plan's PushedFilters", "How many files the scan actually opened"],
                      ["Reads got slower over weeks", "<code>DESCRIBE DETAIL</code>", "numFiles up and file size down means small files"],
                      ["A table got big or an update was expensive", "<code>DESCRIBE HISTORY</code>", "Per commit: files added and removed, rows copied (see the write page)"],
                      ["You need to know exactly what a write did", "<code>_delta_log/*.json</code>", "The add, remove and deletion vector actions"],
                      ["Memory errors on the driver", "Executors tab, plan for <code>collect</code> or a broadcast", "Result size, broadcast size"]]))
        + section("ui", "The Spark UI", "What each tab is for", table(["Tab", "Use it to"], [["Jobs", "See the actions that ran and how long each took"], ["Stages", "See one stage's tasks: duration spread shows skew, shuffle read and write, spill"], ["SQL / DataFrame", "See the plan as a graph with row counts and time per node"], ["Storage", "See what is cached and how big it is"], ["Executors", "See memory, task counts and garbage collection per executor"], ["Environment", "See the settings that were in force"]])
                  + real(f"The same numbers are available programmatically. In the local runs the scan node reported <code>number of files read</code> ({q1['files']} for select *, {q3['files']} for the one-day filter), <code>size of files read</code>, <code>number of output rows</code>, <code>scan time</code> and <code>metadata time</code>. The metadata time was {q1['metadata_ms']:.0f} ms for select * and {q3['metadata_ms']:.0f} ms for the filtered query, which is the driver-side cost of listing and pruning files: small here, but it grows with file count."))
        + section("profile", "On Databricks", "The query profile", p("The Databricks query profile (from the docs) shows a query summary with filter icons that indicate the percent of data pruned during scanning, aggregated task time, I/O, and a breakdown of scheduling, optimisation, file pruning and execution time. The graph shows operator nodes with <b>time spent</b>, <b>memory peak</b> and <b>rows</b>, a top-operators panel, performance insights, a link to the Spark UI, and JSON export.")
                  + '<div class="box"><b>Not confirmed:</b> the docs page I read does not list the exact scan metric names (files read, files pruned, bytes read), the join type labels in the graph, or the spill metrics. Open a real profile in your workspace to see them.</div>')
        + section("delta", "Delta's own views", "DESCRIBE DETAIL, HISTORY and the log", p("These answer questions about the table rather than one query. The names below are the real counters recorded by the write experiments:")
                  + table(["Where", "Counters seen", "Tells you"], [["<code>DESCRIBE DETAIL</code>", "numFiles, sizeInBytes", "Is the table made of many small files?"], ["<code>DESCRIBE HISTORY</code> (operationMetrics)", "numAddedFiles, numRemovedFiles, numCopiedRows, numUpdatedRows, numDeletedRows, numDeletionVectorsAdded", "How much a write rewrote"], ["<code>commitInfo</code> in the log", "operation, isolationLevel, isBlindAppend, readVersion, engineInfo", "What kind of write and under what isolation"]])
                  + p('Next page: <a href="/learn/how-delta-works/write-path/">how writes work under the hood</a>, where these counters are used.'))
    )
    qa = [("How do I read a Spark query plan?", "From the bottom up. The scan at the bottom shows the columns read and the filters pushed down; each Exchange above it is a shuffle and a stage boundary; join nodes show the strategy. Data flows upward to the final result."),
          ("Where do I see how many files a query read?", "In the scan node's metrics in the Spark UI SQL tab (number of files read, size of files read), and on Databricks in the query profile, which shows the percent of data pruned during scanning."),
          ("How do I know if my Delta table has small files?", "Run DESCRIBE DETAIL and compare numFiles with sizeInBytes. Many files with a small average size is the small file problem.")]
    return body, qa


# =================================================================== 9. write path
def m(op, key, default=0):
    return int(OPS[op]["operationMetrics"].get(key, default))


def d_write_flow():
    steps = [("1  Plan", ["read the log", "at version N"], "y"), ("2  Write files", ["executors write", "new Parquet files;", "nobody can see", "them yet"], "g"), ("3  Gather", ["driver collects", "each new file's", "path, size, stats"], "w"),
             ("4  Commit", ["driver creates", "N+1.json in the log,", "atomically"], "r"), ("5  Visible", ["readers now see", "version N+1"], "b")]
    i = ""
    for k, (h, lines, f) in enumerate(steps):
        x = 10 + k * 198
        i += bx(x, 20, 186, 100, [h] + lines, f, 13.5)
        if k < 4:
            i += ar(x + 188, 70, x + 196, 70)
    i += bx(500, 150, 480, 56, ["If another writer committed N+1 first: check whether the two", "changes conflict, then retry on top of it or fail"], "w", 13)
    i += ar(700, 122, 700, 148)
    i += t(10, 175, "The commit is the only step that matters:", 14) + t(10, 197, "before it, a failed write leaves only unused files.", 14)
    return svg(1000, 225, "The universal write sequence. Plan by reading the log at version N, write new Parquet files on executors, gather their paths and statistics on the driver, commit by atomically creating the next numbered JSON file, and only then do readers see the new version. If another writer committed first, Delta checks for a conflict and retries or fails.", i)


def files_row(x, y, kept, removed, added, dv=0, size=17, gap=4):
    out, k = "", 0
    for cnt, f, dash in ((kept, "w", False), (dv, "y", False), (removed, "r", False), (added, "g", False)):
        for _ in range(cnt):
            out += f'<rect x="{x + k * (size + gap)}" y="{y}" width="{size}" height="{size + 8}" rx="3" fill="{FILLS[f]}" stroke="#111" stroke-width="1.2"/>'
            k += 1
    return out


def d_ops():
    rows = [("INSERT / append", 10, 0, 2, 0, "append"), ("UPDATE, rows in one file", 9, 1, 1, 0, "update_one_file"), ("UPDATE, rows in every file", 0, 10, 2, 0, "update_every_file"),
            ("DELETE (rewrite)", 9, 1, 1, 0, "delete_rewrite"), ("DELETE (deletion vector)", 9, 0, 0, 1, "delete_with_deletion_vector"), ("MERGE, keys in one file", 9, 1, 1, 0, "merge_keys_in_one_file"),
            ("MERGE, keys in every file", 0, 10, 2, 0, "merge_keys_in_every_file"), ("OPTIMIZE (20 small files)", 0, 20, 1, 0, "optimize_after_small_appends"), ("OVERWRITE", 0, 10, 2, 0, "overwrite")]
    i = t(10, 18, "each square is a data file:   white = kept   red = removed   green = added   yellow = same file plus a deletion vector", 13)
    y = 30
    for lab, kept, rem, add, dv, key in rows:
        if key != "append":
            o = OPS[key]
            rem = int(o["actions"].get("remove", 0)) if key not in ("delete_with_deletion_vector",) else 0
            add = int(o["actions"].get("add", 0)) if key not in ("delete_with_deletion_vector",) else 0
            dv = o["dv_adds"]
            kept = max(0, o["files_before"] - rem - dv) if key != "optimize_after_small_appends" else 0
        else:
            o = OPS["insert_append"]; kept, rem, add, dv = o["files_before"], 0, o["actions"].get("add", 0), 0
        i += t(280, y + 20, lab, 14, "end") + files_row(296, y + 2, min(kept, 20), min(rem, 20), min(add, 20), dv, 14, 3)
        i += t(296 + (min(kept, 20) + min(rem, 20) + min(add, 20) + dv) * 17 + 14, y + 20, f"{o['actions'].get('remove', 0)} removed, {o['actions'].get('add', 0)} added" if key != "delete_with_deletion_vector" else "0 rewritten, 1 deletion vector", 13)
        y += 34
    return svg(1000, y + 10, "What each write did to the files of a 10-file table, drawn as squares. Append adds files and removes none. An update or delete touching one file replaces just that file. An update or merge touching rows in every file replaces all ten. A delete with deletion vectors changes no data file at all. Optimize replaces 20 small files with one. Overwrite removes all ten and adds new ones.", i)


def d_amp():
    ro = [("UPDATE, 11 rows in one file", 11, m("update_one_file", "numUpdatedRows") + m("update_one_file", "numCopiedRows")),
          ("UPDATE, 1,042 rows in every file", 1042, m("update_every_file", "numUpdatedRows") + m("update_every_file", "numCopiedRows")),
          ("DELETE, 50 rows (rewrite)", 50, m("delete_rewrite", "numDeletedRows") + m("delete_rewrite", "numCopiedRows")),
          ("DELETE, 50 rows (deletion vector)", 50, m("delete_with_deletion_vector", "numCopiedRows")),
          ("MERGE, 1,000 updates in one file", 1000, m("merge_keys_in_one_file", "numTargetRowsUpdated") + m("merge_keys_in_one_file", "numTargetRowsCopied")),
          ("MERGE, 100 updates, one per file", 100, m("merge_keys_in_every_file", "numTargetRowsUpdated") + m("merge_keys_in_every_file", "numTargetRowsCopied"))]
    rows = [(lab, rw, f"{n(rw)} rows rewritten to change {n(ch)}", "g" if rw < 1000 else ("y" if rw <= 10000 else "r")) for lab, ch, rw in ro]
    a, y = hbars(rows, 10, 14, 290, 330, 32)
    return svg(1000, y + 10, "Rows rewritten versus rows changed for six writes. Updating 11 rows in one file rewrote 10,000. Updating 1,042 rows spread over every file rewrote 100,000. Deleting 50 rows by rewrite copied 9,950 rows, but with a deletion vector no rows were copied. A merge changing 100 rows, one in each file, rewrote 100,000.", a)


def d_dv():
    i = bx(10, 20, 330, 90, ["Data file (Parquet)", "10,000 rows, untouched", "still the same bytes on disk"], "w", 14)
    i += bx(420, 20, 270, 90, ["Deletion vector", "tiny: 31 bytes here", "marks 50 row positions"], "y", 14) + ar(342, 65, 418, 65, label="pointed to by the add action", lx=380, ly=52)
    i += bx(760, 20, 230, 90, ["A reader opens the file", "and skips the marked rows"], "g", 14) + ar(692, 65, 758, 65)
    i += t(500, 145, "Delete becomes a metadata change. The cost moves to later: reads must apply the vector until OPTIMIZE or a rewrite purges it.", 14, "middle")
    return svg(1000, 165, "Deletion vectors. The data file is not rewritten. A tiny deletion vector file marks which row positions are deleted, and the add action in the log points to it. Readers open the data file and skip the marked rows.", i)


def page_write_path():
    o = OPS
    ins = o["insert_append"]
    tt = WR["time_travel"]
    upd1, updall, delr, deldv = o["update_one_file"], o["update_every_file"], o["delete_rewrite"], o["delete_with_deletion_vector"]
    mg1, mgall, opt, ovr = o["merge_keys_in_one_file"], o["merge_keys_in_every_file"], o["optimize_after_small_appends"], o["overwrite"]
    rows = []
    for lab, op in [("INSERT (append)", ins), ("UPDATE, one file", upd1), ("UPDATE, every file", updall), ("DELETE, rewrite", delr), ("DELETE, deletion vector", deldv), ("MERGE, one file", mg1), ("MERGE, every file", mgall), ("OPTIMIZE", opt), ("OVERWRITE", ovr)]:
        a = op["actions"]
        rows.append([lab, f"<code>{op['operation']}</code>", a.get("add", 0), a.get("remove", 0), "yes" if op["isBlindAppend"] else "no", op["isolationLevel"]])
    body = (
        section("flow", "The sequence", "Every write is: write new files, then commit", fig(d_write_flow(), "Files first, then one atomic commit.")
                + ul(["<b>Data files are never edited.</b> A Parquet file, once written, does not change. A write adds new files, and the log says which files are live.", "<b>The commit is atomic.</b> The log entry for version N+1 either exists or does not, so a reader never sees half a write. If a job dies before step 4, it leaves unused files and no change to the table.", f"<b>The log records how it was done.</b> Every commit in the experiments logged <code>readVersion</code> (the version the writer started from), <code>isolationLevel</code> ({upd1['isolationLevel']}) and <code>isBlindAppend</code> (true only if the write read nothing first).", "<b>Concurrency (general knowledge, not measured here):</b> two writers can run at once. When a second tries to commit a version someone has already taken, Delta checks whether the changes touch the same files and either retries on top of the winner or fails with a conflict. The Delta protocol document could not be fetched to confirm the details."]))
        + section("ops", "All the write paths", "What each one does to the files", fig(d_ops(), "From real commits. Counts of files added and removed are exact.")
                  + table(["Write", "Operation in the log", "add actions", "remove actions", "Blind append", "Isolation"], rows)
                  + p("<b>Method.</b> Each operation ran on its own fresh 10-file table of 100,000 rows, so the counts are not muddied by earlier writes."))
        + section("append", "Append and insert", "The cheap one", p(f"An <code>INSERT</code> of 5,000 rows added {ins['actions']['add']} new files and removed none; the commit has <b>only</b> add actions ({ins['seconds']:.2f} s). No existing file is read or touched, which is why appends are the cheapest write, and why concurrent appends usually do not conflict (general knowledge, not measured here). The downside is the small file problem: many small appends make many small files, which <code>OPTIMIZE</code> later fixes."))
        + section("update", "Update", "Changing 11 rows rewrote 10,000", p("Parquet files cannot be edited in place, so an <code>UPDATE</code> finds the files that contain matching rows, reads them whole, writes new copies with the changes applied, and removes the old ones from the log. This is called <b>copy on write</b>.") + fig(d_amp(), "Rows rewritten to change a few rows. Spread-out changes are the worst case.")
                  + real(f"Updating 11 rows that lived in one file removed 1 file and added 1, with <b>{n(m('update_one_file', 'numUpdatedRows'))} rows updated and {n(m('update_one_file', 'numCopiedRows'))} copied unchanged</b>. Updating about 1,000 rows spread through every file removed {updall['actions']['remove']} files and added {updall['actions']['add']}, copying {n(m('update_every_file', 'numCopiedRows'))} rows. Where the changed rows live matters far more than how many there are.")
                  + ul(["<b>Layout decides the cost.</b> If rows that change together sit in the same files, an update rewrites few files. Clustering by the update key helps.", "<b>A rewrite also reshapes the table:</b> the second update above turned 10 files into 2, because the rewrite produced new files sized by the write, not the original layout."]))
        + section("delete", "Delete", "Rewrite, or mark with a deletion vector", p("Without deletion vectors, a delete is an update that drops rows: the whole file is rewritten without them. With them, nothing is rewritten.") + fig(d_dv(), "A deletion vector turns a delete into a metadata change.")
                  + real(f"Deleting 50 rows: by rewrite it removed 1 file, added 1 and copied {n(m('delete_rewrite', 'numCopiedRows'))} rows. With <code>delta.enableDeletionVectors = true</code> it added <b>{m('delete_with_deletion_vector', 'numDeletionVectorsAdded')} deletion vector</b>, rewrote 0 files and copied {m('delete_with_deletion_vector', 'numCopiedRows')} rows. The log entry shows a <code>deletionVector</code> with storageType <code>{deldv['sample_dv']['storageType']}</code>, size {deldv['sample_dv']['sizeInBytes']} bytes and cardinality {deldv['sample_dv']['cardinality']}. Reading the table afterwards returned {n(WR['dv_rows_after'])} of the original 100,000 rows.")
                  + ul(["<b>The trade:</b> deletes become cheap, and later reads do a little extra work until OPTIMIZE or a rewrite removes the marked rows (the usual reason for running OPTIMIZE after many deletes; general knowledge).", "In the log the file shows as a remove and an add of the <i>same</i> file, the add now carrying the vector. No data file was written."]))
        + section("merge", "Merge", "Two phases: find the touched files, then rewrite them", p("<code>MERGE</code> joins a source to the target, then applies updates, deletes and inserts. Internally it first finds which target files contain matches, then rewrites only those files and writes any inserted rows as new files.")
                  + real(f"Merging 1,000 matching keys that sat in one file (plus 1,000 new keys) removed {m('merge_keys_in_one_file', 'numTargetFilesRemoved')} file and added {m('merge_keys_in_one_file', 'numTargetFilesAdded')}: {n(m('merge_keys_in_one_file', 'numTargetRowsUpdated'))} updated, {n(m('merge_keys_in_one_file', 'numTargetRowsInserted'))} inserted, {n(m('merge_keys_in_one_file', 'numTargetRowsCopied'))} copied. Merging only 100 keys, but one in each of the 10 files, removed {m('merge_keys_in_every_file', 'numTargetFilesRemoved')} files and rewrote {n(m('merge_keys_in_every_file', 'numTargetRowsCopied') + m('merge_keys_in_every_file', 'numTargetRowsUpdated'))} rows to change {m('merge_keys_in_every_file', 'numTargetRowsUpdated')}.")
                  + ul(["<b>The cost of a merge is the files it touches, not the rows it changes.</b> Put a filter on the merge condition (for example a date) so the search covers fewer files.", "<b>Not measured:</b> how the source and target are joined inside MERGE, and Databricks features that speed it up (the docs say dynamic file pruning in MERGE needs Photon)."]))
        + section("optimize", "Compaction", "OPTIMIZE rewrites many files as one", p(f"After five tiny appends the table had {opt['files_before']} files. <code>OPTIMIZE</code> removed {opt['actions']['remove']} and added {opt['actions']['add']}. The commit marks these as not changing data, so streams and readers can ignore it."))
        + section("overwrite", "Overwrite and time travel", "Old files stay until VACUUM", p(f"An overwrite removed all {ovr['actions']['remove']} files from the live set and added {ovr['actions']['add']} new ones. The 100,000-row version is still there: <code>VERSION AS OF 0</code> returned {n(tt['rows_version0'])} rows while the current table had {n(tt['rows_now'])}. The folder held {tt['parquet_files_on_disk']} Parquet files but only {tt['files_in_current_version']} were live.")
                  + ul(["<b>Time travel is just reading an older log version.</b> No data was copied for it.", "<b>Storage keeps growing</b> with every rewrite until <code>VACUUM</code> deletes files older than the retention period (the Databricks docs name <code>delta.deletedFileRetentionDuration</code>, default 7 days). VACUUM was not run in these tests."]))
        + section("tips", "What to do", "Write rules that follow", table(["Do", "Because", "Verdict"], [["Batch appends and compact", "Many tiny commits make small files", PURSUE], ["Cluster data by the keys you update or merge on", "Fewer files are touched", PURSUE], ["Turn on deletion vectors for delete-heavy tables", "A delete stops rewriting files", PURSUE], ["Filter the MERGE condition", "Fewer target files to search", PURSUE], ["Update scattered rows one at a time", "Each update rewrites whole files", DROP], ["Assume an overwrite frees disk", "Old files remain until VACUUM", DROP]]))
    )
    qa = [("What does Delta do when you update a row?", "It finds the files holding matching rows, reads them whole, writes new copies with the change applied, and records a remove for the old file and an add for the new one. In the local test, updating 11 rows rewrote 10,000."),
          ("What are deletion vectors?", "A small side file that marks deleted row positions, so a delete does not rewrite the data file. In the test, deleting 50 rows with deletion vectors rewrote 0 files and copied 0 rows, against 1 file and 9,950 rows copied without them."),
          ("Why does storage not shrink after an overwrite?", "Delta only marks the old files as removed in the log. They stay on disk so older versions can be read, until VACUUM deletes files past the retention period.")]
    return body, qa


# =================================================================== 10. clickhouse
def d_ch_layout():
    i = bx(10, 20, 220, 50, ["A table = many data parts"], "w", 14)
    i += bx(10, 90, 330, 190, ["One part (a folder on disk)", "", "primary.idx      the sparse index", "<column>.bin    one file per column", "<column>.mrk    where each granule starts", "(skip index files, if any)"], "y", 13.5)
    i += ar(120, 72, 120, 88)
    i += bx(400, 20, 280, 110, ["Rows are sorted by the", "ORDER BY key before", "being written to the part", "so equal values sit together"], "g", 14)
    i += bx(400, 160, 280, 120, ["Every insert makes a new part;", "background merges combine", "parts into bigger sorted ones"], "r", 14)
    i += bx(720, 20, 270, 260, ["Why this is fast to read", "", "only the needed columns", "are opened (one file each)", "", "sorted data compresses well", "and can be located by a", "tiny index"], "b", 14)
    return svg(1000, 300, "ClickHouse storage. A table is a set of immutable data parts. Each part is a folder holding a sparse primary index file, one data file and one marks file per column, and optional skipping index files. Rows are sorted by the ORDER BY key before being written, and every insert creates a new part which background merges later combine.", i)


def d_ch_granule():
    i = t(10, 22, "One sorted column, cut into granules of 8,192 rows. The index keeps one entry (mark) per granule.", 14)
    for k in range(60):
        hit = k == 25
        i += f'<rect x="{10 + k * 16}" y="34" width="14" height="46" fill="{FILLS["g"] if hit else FILLS["w"]}" stroke="#111" stroke-width="{1.6 if hit else 0.8}"/>'
    i += t(10 + 25 * 16 + 7, 100, "binary search lands here", 13, "middle")
    i += bx(10, 125, 470, 90, ["With the primary index (the docs' example)", "1 of 1,083 granules read", "8.19 thousand rows, 740 KB"], "g", 14)
    i += bx(520, 125, 470, 90, ["Without a useful index", "all granules read", "8.87 million rows, 70.45 MB"], "r", 14)
    i += t(500, 245, "The primary index held 96.93 KiB for 8.87 million rows, small enough to keep in memory.", 14, "middle")
    return svg(1000, 262, "The sparse primary index. A sorted column is cut into granules of 8,192 rows and the index stores one mark per granule. A filter on the sorted key finds the matching granule by binary search. In the ClickHouse docs' example one granule of 1,083 was read, 8.19 thousand rows and 740 KB, against 8.87 million rows and 70.45 MB without the index.", i)


def page_clickhouse():
    body = (
        '<div class="box"><b>Source.</b> This page is written from the ClickHouse documentation, read on 21 November 2026. ClickHouse was not run in these experiments, so the numbers are the docs\' own examples, labelled as such.</div>'
        + section("idea", "The idea", "Read less, and read it faster", p("ClickHouse is a column database built for analytical reads. Its speed comes from stacking several ideas: store columns separately, keep rows sorted so that a tiny index can find them, skip whole blocks, compress well, and process data in batches on all cores. Most of these have a counterpart in the Delta and Parquet world you have just seen."))
        + section("layout", "On disk", "Sorted parts, one file per column", fig(d_ch_layout(), "Each part is a folder; each column is its own file.")
                  + ul(["<b>Parts.</b> A table is a set of immutable data parts. Each insert creates one, sorted by the <code>ORDER BY</code> key, with its own sparse primary index.", "<b>One file per column</b> in the usual (wide) format, plus a marks file saying where each granule starts. A query opens only the columns it names.", "<b>Compact parts</b> keep all columns in one file for small, frequent inserts; the docs say a part is stored compact or wide by size thresholds (<code>min_bytes_for_wide_part</code>, <code>min_rows_for_wide_part</code>), but I could not confirm their defaults.", "<b>Background merges</b> combine parts within a partition into larger sorted ones; the docs give a target of about 150 GB compressed."]))
        + section("index", "The sparse primary index", "A tiny index that points at blocks of 8,192 rows", fig(d_ch_granule(), "Index entries are per granule, not per row, so the index stays small.")
                  + ul(["<b>Granule:</b> the smallest unit ClickHouse reads. <code>index_granularity</code> defaults to <b>8192</b> rows (and <code>index_granularity_bytes</code> to 10 MB).", "<b>Sparse:</b> the index stores the first value of each granule, not every row, so it fits in memory. Finding rows is a binary search over those marks, then a read of just the matching granules.", "<b>Order matters:</b> the index only helps filters on the leading sort-key columns. The docs show a filter on the second key column reading 1,076 of 1,083 marks, while the same query on a table sorted the other way read 39.", "<b>A filter on a non-leading column</b> uses a weaker 'generic exclusion search' that works well only if the columns before it have few distinct values."])
                  + p("From the docs' worked example: <code>WHERE UserID = 749927693</code> read 1 mark of 1,083 and processed 8.19 thousand rows (740 KB); the same query on a table without that key processed 8.87 million rows (70.45 MB)."))
        + section("skip", "Skipping and pre-aggregation", "Three more ways not to read", table(["Mechanism", "What it does", "From the docs"], [["Skipping indexes", "Per block of granules, store min/max, a set of values or a bloom filter; skip blocks that cannot match", "Example: a set index dropped 6,102 of 6,104 granules; 100 million rows scanned became 32.77 thousand"], ["Projections", "A hidden second copy of the data inside each part, sorted or pre-aggregated differently; the engine picks the cheapest", "Example read the same 39 marks as a table sorted by that key"], ["Materialised views", "Pre-aggregate at insert time", "Example read 41 of 1,083 marks"]])
                  + p("The docs warn that adding a skipping index to a key column is often the wrong fix: indexes only help when the indexed column correlates with the primary key. Try the sort key, a projection or a materialised view first."))
        + section("compress", "Compression and execution", "Small on disk, wide in parallel", ul(["<b>Codecs.</b> The default is LZ4 for self-managed ClickHouse and ZSTD in ClickHouse Cloud. Per column you can chain specialised codecs: <code>Delta</code> and <code>DoubleDelta</code> for timestamps and counters, <code>Gorilla</code> for slowly changing floats, <code>T64</code> for integers, and <code>LowCardinality(String)</code> for dictionary encoding.", "<b>Vectorised processing.</b> Operators pass batches of rows, not single rows, which suits CPU caches and SIMD instructions.", "<b>Parallelism.</b> The plan is unfolded into lanes, typically one per core, each handling a separate range of the data.", "<b>Less I/O is also faster compute:</b> the docs note compression often speeds queries up, because disks and networks are the bottleneck."]))
        + section("compare", "Side by side", "ClickHouse and Delta, level by level", table(["Level", "Delta Lake + Parquet", "ClickHouse"], [["Choose files or parts", "Partition pruning, then min/max in the delta log", "Partition pruning, then the sparse primary index"], ["Inside a file or part", "Parquet footer min/max per row group", "Granule marks, plus skipping indexes"], ["Which columns", "Column chunks named in the query", "One file per column, only named ones opened"], ["How data is ordered", "Whatever the writer produced, unless clustered or Z-ordered", "Always sorted by ORDER BY inside every part"], ["Pre-aggregation", "Materialized views, metric view materialisation", "Projections, materialised views"], ["Updates", "Copy on write, deletion vectors", "Parts and merges; point updates are not its strength"]])
                  + p("The biggest difference is the sort. ClickHouse sorts every part by the key as it writes, so a narrow index always works. Delta leaves ordering to you, so the layout steps on the layout page (clustering, Z-order) are how you get the same effect."))
        + section("write", "The write side", "Why inserts want batches", ul(["Every synchronous insert creates a part, so the docs recommend batches of at least 1,000 rows, ideally 10,000 to 100,000, and about one insert per second. Too many small parts means too many merges ('too many parts' errors).", "<b>Async inserts</b> (<code>async_insert</code>) buffer small inserts on the server: the docs list a 100 MiB size limit, a 200 ms busy timeout and up to 450 queries per flush as defaults, and recommend <code>wait_for_async_insert = 1</code>.", "<b>Where it is weaker (docs):</b> point lookups and point updates (the sparse index finds ranges, not single rows), and single-row high-frequency inserts. I found no statement about join performance in the pages I read."]))
        + section("see", "Checking", "How to see what a query read", p("<code>EXPLAIN indexes = 1 SELECT …</code> shows how many parts and granules the index selected, for example <code>Granules: 1/1083</code>. The <code>system.query_log</code> table records <code>read_rows</code> and <code>read_bytes</code> per query."))
        + '<div class="box"><b>Not confirmed:</b> defaults for the mark and uncompressed caches, how much the operating system page cache helps, the default block size, and join behaviour. The docs pages I could read did not state them. Also, the mark counts quoted for the second key column, projections and materialised views (1,076 of 1,083, 39, 41) came from a summarised part of the long sparse-index guide in the docs rather than its verbatim text, so check them there.</div>'
    )
    qa = [("Why are ClickHouse reads so fast?", "It reads fewer bytes (one file per column, a sparse primary index that finds 8,192-row granules, skipping indexes), compresses well, and processes batches of data in parallel on all cores. In the docs' example an index lookup read 8.19 thousand rows instead of 8.87 million."),
          ("What is a granule?", "The smallest block ClickHouse reads, by default 8,192 rows. The primary index stores one entry per granule, not per row, so it is small enough to sit in memory."),
          ("Why does ClickHouse want batched inserts?", "Each insert creates a new data part, and background merges must combine them. The docs recommend batches of at least 1,000 rows, ideally 10,000 to 100,000, at about one insert per second, or async inserts.")]
    return body, qa
