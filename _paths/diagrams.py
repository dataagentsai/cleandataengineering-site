"""Simple hand-drawn-style diagrams for concept pages: pastel boxes, ink outlines, arrows.

Each diagram returns (svg, caption). Keep them small: one idea per drawing.
"""
from html import escape as E

FILL = {"rose": "#FCF2F7", "peri": "#F1F4FB", "butter": "#FFF8E8", "mint": "#F0F8F3", "lilac": "#F6F2FC",
        "sky": "#EFF8FB", "white": "#FFFFFF", "grey": "#F3F3F1", "bronze": "#F5E3D3", "silver": "#ECEEF1", "gold": "#FFF1C2"}
DEFS = ('<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M0,0 L10,5 L0,10 z" fill="#1F1F1F"/></marker></defs>')


def box(x, y, w, h, title, sub="", fill="white"):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{FILL[fill]}" stroke="#1F1F1F" stroke-width="1.6"/>'
    ty = y + h / 2 + (-4 if sub else 6)
    s += f'<text x="{x + w / 2}" y="{ty}" text-anchor="middle" font-size="19" fill="#1F1F1F">{E(title)}</text>'
    for i, line in enumerate(sub.split("\n") if sub else []):
        s += f'<text x="{x + w / 2}" y="{ty + 20 + i * 16}" text-anchor="middle" font-size="14" fill="#555">{E(line)}</text>'
    return s


def arrow(x1, y1, x2, y2, label=""):
    s = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#1F1F1F" stroke-width="1.6" marker-end="url(#ah)"/>'
    if label:
        s += f'<text x="{(x1 + x2) / 2}" y="{(y1 + y2) / 2 - 7}" text-anchor="middle" font-size="13" fill="#555">{E(label)}</text>'
    return s


def text(x, y, t, size=15, anchor="middle", fill="#555"):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{fill}">{E(t)}</text>'


def row(y, items, x0=10, w=150, gap=40, h=78):
    """items: (title, sub, fill). Returns svg for boxes joined by arrows."""
    s, x = "", x0
    for i, (t, sub, f) in enumerate(items):
        s += box(x, y, w, h, t, sub, f)
        if i < len(items) - 1:
            s += arrow(x + w + 2, y + h / 2, x + w + gap - 4, y + h / 2)
        x += w + gap
    return s


def svg(w, h, body, label):
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{E(label)}">{DEFS}{body}</svg>'


def medallion():
    b = row(20, [("Sources", "apps, files,\nAPIs", "grey"), ("Bronze", "raw, as it\narrived", "bronze"),
                 ("Silver", "clean, typed,\none row per thing", "silver"), ("Gold", "shaped for\na use", "gold"),
                 ("Uses", "dashboards,\nML, AI", "mint")], w=150, gap=36, h=92)
    b += text(470, 140, "each layer is built only from the one before, so you can always rebuild", 15)
    return (svg(940, 155, b, "Sources flow into bronze (raw), then silver (clean), then gold (business-ready), then to dashboards, ML and AI."),
            "Medallion architecture: raw, clean, ready. Fix a step and rebuild from the layer below.")


def etl_elt():
    b = text(10, 22, "ETL", 20, "start", "#1F1F1F")
    b += row(32, [("Extract", "from source", "grey"), ("Transform", "outside the\nwarehouse", "butter"), ("Load", "clean data\nonly", "peri")], x0=70, w=170, gap=50, h=72)
    b += text(10, 150, "ELT", 20, "start", "#1F1F1F")
    b += row(160, [("Extract", "from source", "grey"), ("Load", "raw data\nkept", "peri"), ("Transform", "with SQL inside\nthe warehouse", "mint")], x0=70, w=170, gap=50, h=72)
    return (svg(720, 245, b, "ETL: extract, transform, then load. ELT: extract, load raw, then transform inside the warehouse."),
            "Same three steps, different order. ELT keeps the raw copy, so you can re-run a fixed transformation.")


def batch_stream():
    b = text(10, 22, "Batch", 20, "start", "#1F1F1F")
    b += row(32, [("Events pile up", "all day", "grey"), ("Nightly job", "processes\nthe pile", "butter"), ("Report", "fresh by\n9 a.m.", "peri")], x0=90, w=170, gap=46, h=72)
    b += text(10, 150, "Stream", 20, "start", "#1F1F1F")
    b += row(160, [("Each event", "as it happens", "grey"), ("Stream job", "handles it in\nseconds", "mint"), ("Alert / table", "fresh within\nseconds", "peri")], x0=90, w=170, gap=46, h=72)
    return (svg(740, 245, b, "Batch collects events and processes them on a schedule; streaming handles each event within seconds."),
            "Batch is simpler and cheaper; streaming is fresher. Choose by how fresh the answer must be.")


def row_col():
    b = text(165, 22, "Row-based (CSV, JSON, Avro)", 17, "middle", "#1F1F1F")
    cols = ["date", "store", "item", "amount"]
    for r in range(3):
        for c in range(4):
            b += f'<rect x="{20 + c * 72}" y="{36 + r * 34}" width="68" height="28" rx="6" fill="{["#FCF2F7", "#F1F4FB", "#FFF8E8"][r]}" stroke="#1F1F1F" stroke-width="1.3"/>'
            b += text(54 + c * 72, 55 + r * 34, cols[c], 13, fill="#1F1F1F")
    b += text(165, 160, "a whole row is stored together", 14)
    b += text(555, 22, "Columnar (Parquet)", 17, "middle", "#1F1F1F")
    for c in range(4):
        for r in range(3):
            hot = c in (0, 3)
            fill, sw, op = ("#F0F8F3", 1.8, "") if hot else ("#FFFFFF", 1.1, ' opacity="0.55"')
            b += f'<rect x="{410 + c * 74}" y="{36 + r * 34}" width="68" height="28" rx="6" fill="{fill}" stroke="#1F1F1F" stroke-width="{sw}"{op}/>'
            b += text(444 + c * 74, 55 + r * 34, cols[c], 13, fill="#1F1F1F" if hot else "#999")
    b += text(555, 160, "'sales by date' reads only 2 of 4 columns", 14)
    return (svg(720, 175, b, "Row formats store whole rows together; columnar formats store each column together, so a query reads only the columns it needs."),
            "Analytics reads a few columns across many rows, which is why columnar files are faster and cheaper.")


def star():
    b = box(285, 95, 170, 80, "fact_sales", "date, product, store,\ncustomer, amount", "butter")
    for (x, y, t) in [(30, 15, "dim_date"), (540, 15, "dim_product"), (30, 185, "dim_store"), (540, 185, "dim_customer")]:
        b += box(x, y, 170, 62, t, "", "peri")
    b += arrow(283, 115, 202, 60) + arrow(457, 115, 538, 60) + arrow(283, 160, 202, 205) + arrow(457, 160, 538, 205)
    return (svg(740, 260, b, "A fact table of sales in the middle, linked to date, product, store and customer dimension tables."),
            "Star schema: numbers in the fact table, descriptions in the dimensions around it.")


def rag():
    b = row(20, [("Question", "from the user", "grey"), ("Search", "by meaning\nand keywords", "peri"), ("Top passages", "with sources", "butter"),
                 ("Model", "answers only\nfrom these", "lilac"), ("Answer", "with citations", "mint")], w=148, gap=36, h=84)
    b += text(462, 136, "if search misses the right passage, no model can save the answer: test retrieval on its own", 15)
    return (svg(930, 150, b, "A question is used to search documents; the top passages go to the model, which answers from them with citations."),
            "Retrieval-augmented generation: find first, then answer from what you found.")


def agent_loop():
    b = box(20, 90, 150, 80, "Context", "instructions,\nhistory, data", "grey")
    b += box(230, 90, 150, 80, "Model", "answer or\nask for a tool", "lilac")
    b += box(440, 20, 160, 80, "Check", "is this call\nallowed?", "butter")
    b += box(660, 20, 150, 80, "Tool runs", "your code", "peri")
    b += box(440, 170, 160, 70, "Answer", "checked, then sent", "mint")
    b += arrow(172, 130, 228, 130) + arrow(382, 115, 438, 65) + text(395, 78, "tool?", 13, "end") + arrow(602, 60, 658, 60)
    b += arrow(735, 102, 735, 268) + f'<line x1="735" y1="270" x2="95" y2="270" stroke="#1F1F1F" stroke-width="1.6"/>' + arrow(95, 270, 95, 172)
    b += text(415, 290, "the result goes back into the context; repeat until done or a budget runs out", 14)
    b += arrow(382, 150, 438, 200, "done")
    return (svg(830, 300, b, "The model reads the context and either answers or asks for a tool; a check approves the call, the tool runs, and the result goes back into the context."),
            "The agent loop. The check between the model's request and the tool is where safety lives.")


DIAGRAMS = {"medallion": medallion, "etl-elt": etl_elt, "batch-stream": batch_stream, "row-col": row_col, "star": star, "rag": rag, "agent-loop": agent_loop}
