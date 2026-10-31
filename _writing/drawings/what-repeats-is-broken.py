# Drawings for the post "What repeats is broken".
# kit, figure, E and ROOT are injected by _writing/build.py.


def _person(cx, top):
    return (f'<circle class="bx" cx="{cx}" cy="{top}" r="13"/><line class="lnc" x1="{cx}" y1="{top + 13}" x2="{cx}" y2="{top + 42}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 42}" x2="{cx - 10}" y2="{top + 62}"/><line class="lnc" x1="{cx}" y1="{top + 42}" x2="{cx + 12}" y2="{top + 62}"/>'
            f'<line class="lnc" x1="{cx}" y1="{top + 24}" x2="{cx + 20}" y2="{top + 14}"/><line class="lnc" x1="{cx}" y1="{top + 24}" x2="{cx - 16}" y2="{top + 32}"/>')


def _invoice(x, y, tilt=0):
    lines = "".join(f'<line class="ln" x1="{x + 8}" y1="{y + 26 + j * 10}" x2="{x + (40 if j % 2 else 46)}" y2="{y + 26 + j * 10}"/>'
                    for j in range(3))
    return (f'<g transform="rotate({tilt} {x + 27} {y + 32})"><rect class="hz" x="{x}" y="{y}" width="54" height="64" rx="3"/>'
            f'<text class="sm" x="{x + 27}" y="{y + 17}" text-anchor="middle">₹40,000</text>{lines}</g>')


def _file(x, y, label):
    return (f'<path class="hz" d="M{x},{y} L{x + 40},{y} L{x + 54},{y + 14} L{x + 54},{y + 64} L{x},{y + 64} Z"/>'
            f'<path class="ln" d="M{x + 40},{y} L{x + 40},{y + 14} L{x + 54},{y + 14}"/>'
            f'<text class="sm" x="{x + 27}" y="{y + 42}" text-anchor="middle">{label}</text>')


def drawing_photocopier():
    b, a, t = kit.box, kit.arrow, kit.text
    # photocopier
    d = ('<rect class="hz" x="40" y="120" width="170" height="120" rx="8"/>'
         '<rect class="hz" x="55" y="98" width="140" height="24" rx="4"/>'
         '<rect class="pf pf-bx" x="65" y="140" width="60" height="30" rx="4"/>'
         '<circle class="hz" cx="160" cy="155" r="10"/><circle class="hz" cx="185" cy="155" r="6"/>'
         '<rect class="hz" x="210" y="190" width="40" height="10" rx="2"/>'
         '<line class="ln" x1="55" y1="215" x2="195" y2="215"/>')
    d += t(125, 270, "the same invoice, printed twice", "sm", "middle")
    d += _invoice(255, 105, -8) + _invoice(285, 150, 6)
    # rushed path
    d += a(350, 150, 470, 85)
    d += _person(500, 40)
    d += b(545, 35, 300, 90, "The rushed accountant", "pays ₹40,000, then pays again", "bxm")
    d += '<rect class="zr" x="860" y="55" width="120" height="50" rx="8"/>' + t(920, 86, "₹80,000 out", "bd", "middle")
    # careful path
    d += a(350, 195, 470, 245)
    d += _person(500, 190)
    d += b(545, 185, 300, 90, "The careful accountant", ["checks the invoice number,", "files the copy"], "bxs")
    d += '<rect class="zg" x="860" y="205" width="120" height="50" rx="8"/>' + t(920, 236, "₹40,000 out", "bd", "middle")
    return figure(1000, 290, d,
                  "A photocopier prints the same ₹40,000 invoice twice. One accountant pays both and ₹80,000 goes out. A careful accountant checks the invoice number, files the copy, and only ₹40,000 goes out.",
                  "Repeats are normal. What matters is whether the receiver checks before it acts.")


def drawing_naive_vs_safe():
    b, a, t = kit.box, kit.arrow, kit.text
    d = _file(12, 95, "b-0912") + _file(72, 135, "b-0912")
    d += t(80, 225, ["the same file,", "sent twice"], "sm", "middle")
    d += t(560, 22, "naive pipeline", "lbl", "middle")
    d += t(560, 192, "our pipeline", "lbl", "middle")
    # naive row
    d += a(118, 128, 150, 80)
    naive = [("Bronze", "appends 6 rows again", "bxm"), ("Silver", ["INSERT: order 1001", "now twice"], "bxm")]
    for i, (n, s, k) in enumerate(naive):
        x = 152 + i * 255
        d += b(x, 35, 225, 90, n, s, k)
        d += a(x + 227, 80, x + 253, 80)
    d += '<rect class="zr" x="662" y="35" width="320" height="90" rx="10"/>'
    d += t(822, 72, "dashboard: ₹2,500", "bd", "middle") + t(822, 98, "every job said success", "sm", "middle")
    # safe row
    d += a(130, 205, 150, 250)
    safe = [("Run log check", ["b-0912 already loaded:", "add nothing"], "bxs"), ("Silver", ["MERGE on order_id:", "0 rows changed"], "solid")]
    for i, (n, s, k) in enumerate(safe):
        x = 152 + i * 255
        d += b(x, 205, 225, 90, n, s, k)
        d += a(x + 227, 250, x + 253, 250)
    d += '<rect class="zg" x="662" y="205" width="320" height="90" rx="10"/>'
    d += t(822, 242, "dashboard: ₹1,250", "bd", "middle") + t(822, 268, "the same as the first run", "sm", "middle")
    return figure(1000, 310, d,
                  "Batch b-0912 is sent twice. In the naive pipeline bronze appends 6 rows again, silver inserts order 1001 a second time, and the dashboard says ₹2,500. In our pipeline the run log check sees the batch was already loaded, MERGE on order_id changes 0 rows, and the dashboard still says ₹1,250.",
                  "Recorded in the DataTwin Studio (Spark 3.5.1, Delta Lake 3.2.0): the same file twice doubles the naive pipeline's revenue and leaves ours unchanged.")


def drawing_toolbox():
    b, t = kit.box, kit.text
    d = ('<path class="hz" d="M420,62 L420,28 Q420,18 432,18 L568,18 Q580,18 580,28 L580,62"/>'
         '<rect class="hz" x="15" y="60" width="970" height="250" rx="14"/>'
         '<line class="ln" x1="15" y1="90" x2="985" y2="90"/>')
    tools = [("Batch ledger", ["was this batch loaded?", "then skip it"], "bxs"),
             ("MERGE on keys", ["one row per order,", "however often it runs"], "solid"),
             ("Partition overwrite", ["replace exactly", "the day you load"], "bx"),
             ("Dedupe in silver", ["one row per key,", "latest event wins"], "bx"),
             ("Watermark after commit", ["move the bookmark", "only once data is in"], "bxs"),
             ("Idempotency keys", ["the other system", "ignores a repeat"], "bx")]
    for i, (n, s, k) in enumerate(tools):
        x = 40 + (i % 3) * 315
        y = 105 + (i // 3) * 100
        d += b(x, y, 290, 85, n, s, k)
    return figure(1000, 320, d,
                  "A toolbox holding six tools: a batch ledger, MERGE on keys, partition overwrite, dedupe in silver, watermark moved after commit, and idempotency keys.",
                  "Six small tools, each guarding a different door. Most pipelines need three or four of them.")


def drawing_crash():
    b, a, t, p, n = kit.box, kit.arrow, kit.text, kit.path, kit.num
    d = b(10, 60, 200, 100, "Read the batch", ["from the watermark:", "after 26 Oct"], "bx") + n(16, 66, 1)
    d += a(212, 110, 248, 110)
    d += b(250, 60, 210, 100, "Write the data", ["MERGE, one", "atomic commit"], "solid") + n(256, 66, 2)
    # the crash: a lightning bolt
    d += ('<path class="zr" d="M505,40 L478,108 L500,108 L482,170 L530,92 L506,92 L526,40 Z"/>'
          '<path class="ln" d="M505,40 L478,108 L500,108 L482,170 L530,92 L506,92 L526,40 Z" fill="none"/>')
    d += t(504, 192, "crash", "bd", "middle")
    d += b(550, 60, 210, 100, "Move the watermark", ["only after step 2", "has committed"], "bxs") + n(556, 66, 3)
    d += a(762, 110, 788, 110)
    d += b(790, 60, 200, 100, "Mark done", ["in the batch", "ledger"], "bxs") + n(796, 66, 4)
    d += '<line class="lnd" x1="462" y1="110" x2="472" y2="110"/><line class="lnd" x1="536" y1="110" x2="548" y2="110"/>'
    d += p("M470,205 Q290,300 110,164", "lnd")
    d += t(330, 272, ["re-run: the bookmark never moved, so it reads the same batch;", "step 2 again is a MERGE on the same rows, so nothing doubles"], "sm", "middle")
    return figure(1000, 310, d,
                  "Four steps: read the batch from the watermark, write the data with MERGE in one atomic commit, move the watermark, mark done in the ledger. A lightning bolt marks a crash between writing and moving the watermark. A dashed arrow goes back to step 1: the re-run reads the same batch, and MERGE lands on the same rows.",
                  "Write first, move the bookmark second. A crash in between costs one repeat, and the repeat is harmless.")


DRAWINGS = {"rep-photocopier": drawing_photocopier, "rep-naive-vs-safe": drawing_naive_vs_safe,
            "rep-toolbox": drawing_toolbox, "rep-crash": drawing_crash}
