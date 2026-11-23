"""Sample Ops dashboards for AI and agents: a hub plus seven sample pages at /learn/ai-ops-dashboard/.

    python3 _guides/ops_dashboard.py      (then python3 _site/nav.py and python3 _site/seo.py)

Every number is MADE UP and labelled so on each page. One story runs through all seven pages (so the pages agree):
  Nov 20  the claims policy documents stop refreshing (stale index)       -> Data and retrieval, Quality
  Nov 21  SQL assistant release v2.3 goes out; a source column was renamed -> Quality, Runs
  Nov 22  Support agent retry loop doubles Large-model spend               -> Cost
  Nov 23  a burst of prompt-injection attempts, all blocked                -> Safety
Colours: reference palette slots 1-4 (blue, orange, aqua, violet) for series; status colours are reserved and
always shown with an icon and a label. Every chart has a table view and hover text. Light only.
"""
import json
import sys
from html import escape as E
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import de_essentials as DE  # noqa: E402

C = DE.C
table = DE.table
URL = "/learn/ai-ops-dashboard/"
S1, S2, S3, S4 = "#2a78d6", "#eb6834", "#1baf7a", "#6250d6"
GOOD, WARN, SERIOUS, CRIT = "#0ca30c", "#fab219", "#ec835a", "#d03b3b"
STATUS = {"good": (GOOD, "✓", "Healthy"), "warn": (WARN, "!", "Watch"), "serious": (SERIOUS, "▲", "Serious"), "crit": (CRIT, "✕", "Critical")}
DAYS = [f"Nov {d}" for d in range(10, 24)]
INK, MUTED, GRID, BASE = "#0b0b0b", "#898781", "#e1e0d9", "#c3c2b7"

PAGES = [("overview", "Overview", "Is everything healthy right now, and what needs a person?"),
         ("runs", "Runs and traces", "What did one agent run actually do, step by step?"),
         ("quality", "Quality and evals", "Is it still giving good answers after the last release?"),
         ("cost", "Cost and tokens", "What are we spending, on what, and are we on budget?"),
         ("safety", "Safety and approvals", "What was blocked, and what is waiting for a human?"),
         ("data", "Data and retrieval", "Is the data the AI reads fresh, complete and unchanged?"),
         ("governance", "Governance", "Which AI systems exist, who owns them, and are reviews up to date?")]

CSS = """<style>
  .ops { margin:10px 0 30px; }
  .ops .banner { border:1.5px dashed var(--ink); border-radius:12px; padding:8px 14px; background:var(--butter-wash); font-size:14.5px; margin:0 0 14px; }
  .ops .tabs { display:flex; flex-wrap:wrap; gap:6px; margin:0 0 18px; }
  .ops .tabs a { border:1.5px solid var(--ink); border-radius:999px; padding:3px 13px; text-decoration:none; font-size:14px; background:#fff; }
  .ops .tabs a.on { background:#0b0b0b; color:#fff; }
  .ops .tiles { display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:10px; margin:0 0 16px; }
  .ops .tile { border:1.5px solid var(--ink); border-radius:12px; padding:10px 14px; background:#fcfcfb; }
  .ops .tile .l { font-size:13px; color:#52514e; } .ops .tile .v { font-size:30px; font-weight:700; line-height:1.15; }
  .ops .tile .d { font-size:13.5px; } .ops .tile .st { float:right; font-size:13px; font-weight:700; }
  .ops .grid2 { display:grid; grid-template-columns:repeat(auto-fit,minmax(480px,1fr)); gap:14px; }
  .ops .card { border:1.5px solid var(--ink); border-radius:12px; padding:10px 14px 8px; background:#fcfcfb; margin:0 0 14px; overflow-x:auto; }
  .ops .card h3 { margin:2px 0 2px; font-size:17px; } .ops .card .sub { font-size:13.5px; color:#52514e; margin:0 0 6px; }
  .ops svg { width:100%; height:auto; display:block; min-width:460px; } .ops svg text { font-family:inherit; fill:#0b0b0b; }
  .ops .legend { display:flex; flex-wrap:wrap; gap:4px 16px; font-size:13.5px; margin:0 0 4px; } .ops .legend i { display:inline-block; width:12px; height:12px; border-radius:3px; margin-right:6px; vertical-align:-1px; }
  .ops .pill { font-size:12.5px; font-weight:700; border:1.5px solid var(--ink); border-radius:999px; padding:0 9px; white-space:nowrap; background:#fff; }
  .ops .pill b { display:inline-block; margin-right:4px; }
  .ops table.t td, .ops table.t th { font-size:13.5px; } .ops details { margin:6px 0 2px; font-size:13.5px; } .ops summary { cursor:pointer; color:#52514e; }
  .ops .btn { font:inherit; font-size:13px; border:1.5px solid var(--ink); border-radius:8px; padding:1px 10px; background:#fff; margin-right:4px; }
  .ops .need { border-left:6px solid var(--ink); padding:6px 12px; margin:8px 0; background:#fff; border-radius:0 10px 10px 0; font-size:14.5px; }
</style>"""


# ------------------------------------------------------------------ small components
def pill(kind, text=None):
    col, icon, label = STATUS[kind]
    return f'<span class="pill"><b style="color:{col}">{icon}</b>{E(text or label)}</span>'


def tile(label, value, delta, kind):
    col, icon, lab = STATUS[kind]
    return (f'<div class="tile" style="border-left:8px solid {col}"><span class="st"><b style="color:{col}">{icon}</b> {lab}</span><div class="l">{E(label)}</div>'
            f'<div class="v">{E(value)}</div><div class="d">{E(delta)}</div></div>')


def tabs(cur):
    return '<div class="tabs">' + "".join(f'<a href="{URL}{k}/"{" class=on" if k == cur else ""}>{E(n)}</a>' for k, n, _ in PAGES) + "</div>"


def banner():
    return '<div class="banner"><b>Sample dashboard.</b> Every number here is made up to show the layout. The same story runs through all seven pages, so you can follow one problem from view to view.</div>'


def legend(items):
    return '<div class="legend">' + "".join(f'<span><i style="background:{c}"></i>{E(n)}</span>' for n, c in items) + "</div>"


def table_view(head, rows):
    h = "".join(f"<th>{E(x)}</th>" for x in head)
    b = "".join("<tr>" + "".join(f"<td>{E(str(c))}</td>" for c in r) + "</tr>" for r in rows)
    return f'<details><summary>Table view</summary><div class="tw"><table class="t"><tr>{h}</tr>{b}</table></div></details>'


def card(title, sub, inner):
    return f'<div class="card"><h3>{E(title)}</h3><p class="sub">{E(sub)}</p>{inner}</div>'


def line_chart(series, ymin, ymax, fmt="{:.0f}", target=None, labels=DAYS, unit="", h=250):
    """series: [(name, values, colour)]. One axis. Direct end labels plus legend; hover text per day."""
    w, l, r, t, b = 680, 46, 150, 12, 28
    pw, ph = w - l - r, h - t - b
    n = len(labels)
    X = lambda i: l + i * pw / (n - 1)
    Y = lambda v: t + ph - (v - ymin) / (ymax - ymin) * ph
    d = ""
    for k in range(5):
        v = ymin + (ymax - ymin) * k / 4
        d += f'<line x1="{l}" y1="{Y(v):.1f}" x2="{l + pw}" y2="{Y(v):.1f}" stroke="{GRID}" stroke-width="1"/><text x="{l - 6}" y="{Y(v) + 4:.1f}" text-anchor="end" font-size="11.5" fill="{MUTED}">{fmt.format(v)}{unit}</text>'
    d += f'<line x1="{l}" y1="{t + ph}" x2="{l + pw}" y2="{t + ph}" stroke="{BASE}" stroke-width="1.2"/>'
    for i in range(0, n, 3):
        d += f'<text x="{X(i):.1f}" y="{h - 8}" text-anchor="middle" font-size="11.5" fill="{MUTED}">{labels[i]}</text>'
    if target is not None:
        d += f'<line x1="{l}" y1="{Y(target):.1f}" x2="{l + pw}" y2="{Y(target):.1f}" stroke="{INK}" stroke-width="1.2" stroke-dasharray="5 4"/><text x="{l + pw + 6}" y="{Y(target) + 4:.1f}" font-size="11.5">target {fmt.format(target)}{unit}</text>'
    ends = []
    for name, vals, col in series:
        pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(vals))
        d += f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>'
        d += f'<circle cx="{X(n - 1):.1f}" cy="{Y(vals[-1]):.1f}" r="4" fill="{col}" stroke="#fcfcfb" stroke-width="2"/>'
        ends.append([Y(vals[-1]), name, vals[-1]])
    ends.sort()
    for k in range(1, len(ends)):
        if ends[k][0] - ends[k - 1][0] < 14:
            ends[k][0] = ends[k - 1][0] + 14
    for y, name, v in ends:
        d += f'<text x="{l + pw + 10}" y="{y + 4:.1f}" font-size="12">{E(name)} {fmt.format(v)}{unit}</text>'
    for i in range(n):
        tip = f"{labels[i]}: " + ", ".join(f"{nm} {fmt.format(vs[i])}{unit}" for nm, vs, _ in series)
        d += f'<rect x="{X(i) - pw / (n - 1) / 2:.1f}" y="{t}" width="{pw / (n - 1):.1f}" height="{ph}" fill="transparent"><title>{E(tip)}</title></rect>'
    svg = f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Line chart, {n} days, " >{d}</svg>'
    lg = legend([(nm, c) for nm, _, c in series]) if len(series) > 1 else ""
    tv = table_view(["Day"] + [nm for nm, *_ in series], [[labels[i]] + [fmt.format(vs[i]) + unit for _, vs, _ in series] for i in range(n)])
    return lg + svg + tv


def stacked(series, fmt="${:.0f}", labels=DAYS, h=260):
    w, l, r, t, b = 640, 46, 20, 12, 28
    pw, ph = w - l - r, h - t - b
    n = len(labels)
    tot = [sum(vs[i] for _, vs, _ in series) for i in range(n)]
    ymax = max(tot) * 1.1
    Y = lambda v: t + ph - v / ymax * ph
    d = ""
    for k in range(5):
        v = ymax * k / 4
        d += f'<line x1="{l}" y1="{Y(v):.1f}" x2="{l + pw}" y2="{Y(v):.1f}" stroke="{GRID}"/><text x="{l - 6}" y="{Y(v) + 4:.1f}" text-anchor="end" font-size="11.5" fill="{MUTED}">{fmt.format(v)}</text>'
    bw = pw / n * 0.62
    for i in range(n):
        x = l + i * pw / n + (pw / n - bw) / 2
        base = 0
        tip = f"{labels[i]}: " + ", ".join(f"{nm} {fmt.format(vs[i])}" for nm, vs, _ in series) + f", total {fmt.format(tot[i])}"
        for nm, vs, col in series:
            y0, y1 = Y(base), Y(base + vs[i])
            d += f'<rect x="{x:.1f}" y="{y1:.1f}" width="{bw:.1f}" height="{max(y0 - y1, 0):.1f}" fill="{col}" stroke="#fcfcfb" stroke-width="2"><title>{E(tip)}</title></rect>'
            base += vs[i]
        if i % 3 == 0:
            d += f'<text x="{x + bw / 2:.1f}" y="{h - 8}" text-anchor="middle" font-size="11.5" fill="{MUTED}">{labels[i]}</text>'
    d += f'<line x1="{l}" y1="{t + ph}" x2="{l + pw}" y2="{t + ph}" stroke="{BASE}" stroke-width="1.2"/>'
    svg = f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Stacked bars of daily spend by model class">{d}</svg>'
    tv = table_view(["Day"] + [nm for nm, *_ in series] + ["Total"], [[labels[i]] + [fmt.format(vs[i]) for _, vs, _ in series] + [fmt.format(tot[i])] for i in range(n)])
    return legend([(nm, c) for nm, _, c in series]) + svg + tv


def hbars(items, fmt="{:.0f}", color=S1, maxv=None, unit=""):
    """items: [(label, value, colour|None)]."""
    w, l, rh = 640, 190, 30
    maxv = maxv or max(v for _, v, _ in items) * 1.15
    d = ""
    for i, (lab, v, col) in enumerate(items):
        y = 8 + i * rh
        bw = (w - l - 90) * v / maxv
        d += f'<text x="{l - 8}" y="{y + 15}" text-anchor="end" font-size="13">{E(lab)}</text>'
        d += f'<rect x="{l}" y="{y + 4}" width="{bw:.1f}" height="14" rx="3" fill="{col or color}"><title>{E(lab)}: {fmt.format(v)}{unit}</title></rect>'
        d += f'<text x="{l + bw + 6:.1f}" y="{y + 16}" font-size="12.5">{fmt.format(v)}{unit}</text>'
    h = 12 + len(items) * rh
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Horizontal bar chart">{d}</svg>' + table_view(["Item", "Value"], [[a, fmt.format(b) + unit] for a, b, _ in items])


def shell(cur, title, body, desc):
    url_path = f"{URL}{cur}/" if cur else URL
    page_body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/learn/">Learn</a> › <a href="{URL}">AI ops dashboard</a>{' › ' + E(title) if cur else ''}</p>
<p class="eyebrow" style="margin-top:22px">{'Sample dashboard' if cur else 'Guide · with seven sample dashboards'}</p><h1>{E(title)}</h1>
<div class="tf ops">{CSS}{body}</div>"""
    crumbs = [("Learn", "/learn/"), ("AI ops dashboard", URL)] + ([(title, url_path)] if cur else [])
    return url_path, DE.page_shell(("AI ops dashboard: " + title) if cur else title, desc, url_path, page_body, crumbs)


# ------------------------------------------------------------------ made-up data (one story)
REQ = [9400, 9700, 9900, 10100, 9800, 6200, 5900, 9600, 9900, 10200, 10050, 9950, 10300, 9850]
SUCC = {"Support agent": [95.2, 95.0, 94.8, 95.4, 95.1, 94.9, 95.3, 95.0, 94.7, 95.2, 95.1, 94.9, 94.2, 94.4],
        "Claims intake": [92.1, 92.4, 91.8, 92.0, 92.3, 91.9, 92.2, 92.5, 92.0, 91.8, 91.6, 90.2, 87.5, 86.9],
        "SQL assistant": [91.0, 91.5, 91.2, 91.8, 92.0, 91.4, 91.7, 92.1, 91.9, 92.2, 92.0, 88.5, 83.1, 82.4],
        "Summariser": [96.5, 96.8, 96.2, 96.6, 96.9, 96.4, 96.7, 96.5, 96.8, 96.6, 96.3, 96.5, 96.7, 96.4]}
COST = {"Large model": [190, 195, 205, 210, 200, 120, 115, 198, 206, 214, 210, 208, 330, 236], "Small model": [60, 62, 64, 66, 63, 40, 38, 64, 66, 68, 67, 66, 70, 68],
        "Embeddings": [22, 23, 22, 24, 23, 15, 14, 23, 24, 25, 24, 24, 25, 24], "Search and tools": [44, 45, 46, 47, 45, 30, 29, 46, 47, 48, 47, 47, 50, 46]}
EVALS = {"Task completion": [91.0, 91.4, 91.1, 91.6, 91.8, 91.3, 91.5, 91.9, 91.7, 92.0, 91.9, 88.6, 84.2, 83.8],
         "Groundedness": [93.0, 93.4, 92.8, 93.1, 93.5, 93.0, 93.3, 93.2, 93.6, 93.1, 93.4, 92.2, 89.5, 89.1],
         "Safety": [99.1, 99.0, 99.2, 99.1, 99.0, 99.2, 99.1, 99.1, 99.0, 99.2, 99.1, 99.0, 99.1, 99.0],
         "Format validity": [98.5, 98.6, 98.4, 98.7, 98.6, 98.5, 98.7, 98.6, 98.5, 98.6, 98.7, 98.4, 98.5, 98.6]}
BLOCKS = [41, 38, 44, 47, 43, 22, 20, 45, 46, 49, 52, 58, 61, 119]
HIT = {"Support knowledge base": [91, 90, 91, 92, 91, 90, 91, 92, 91, 91, 92, 91, 90, 91], "Claims policy documents": [89, 90, 89, 90, 89, 90, 89, 90, 89, 88, 84, 78, 71, 66]}
NOSRC = [6.1, 6.0, 6.3, 6.1, 6.2, 6.0, 6.2, 6.1, 6.3, 6.2, 7.0, 9.4, 12.8, 15.9]


def overview():
    tiles = "".join([tile("Requests, 24h", "9,850", "▲ 4% vs last Monday", "good"), tile("Task success", "92.5%", "▼ 2.1 pts vs 7-day average", "warn"), tile("Slowest 5% of runs (p95)", "6.2 s", "target under 8 s", "good"),
                     tile("Spend, 24h", "$374", "month to date $7,980 of $9,000", "serious"), tile("Open incidents", "3", "1 critical, 2 serious", "serious"), tile("Waiting for a person", "7", "oldest 3 h 10 min", "warn")])
    chart1 = card("Task success rate by agent", "Share of runs that finished the task correctly, last 14 days. One axis, one measure.", line_chart([(n, v, c) for (n, v), c in zip(SUCC.items(), [S1, S2, S3, S4])], 78, 100, "{:.0f}", target=90, unit="%"))
    reqs = stacked([("Requests", REQ, S1)], fmt="{:,.0f}")
    chart2 = card("Requests per day", "All agents together. Weekends are quieter.", reqs.replace('<div class="legend"><span><i style="background:#2a78d6"></i>Requests</span></div>', ""))
    rows = [["Support agent", pill("good"), "4,100", "94.4%", "5.1 s", "$143", "Customer care", "v4.8"],
            ["Claims intake", pill("serious", "Stale data"), "1,820", "86.9%", "7.4 s", "$61", "Claims ops", "v3.1"],
            ["SQL assistant", pill("crit", "Regression"), "960", "82.4%", "6.2 s", "$38", "Analytics", "v2.3"],
            ["Summariser", pill("good"), "2,670", "96.4%", "3.8 s", "$92", "Operations", "v1.9"],
            ["Data-quality agent", pill("good"), "300", "97.0%", "4.4 s", "$40", "Data platform", "v1.2"]]
    health = card("Agent health", "One line per agent: status first, then the numbers behind it.", '<div class="tw"><table class="t"><tr><th>Agent</th><th>Status</th><th>Runs 24h</th><th>Success</th><th>p95</th><th>Cost</th><th>Owner</th><th>Release</th></tr>' + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</table></div>")
    need = (f'<div class="card"><h3>Needs a person now</h3><p class="sub">Sorted by seriousness. Each one opens the view that explains it.</p>'
            f'<div class="need" style="border-color:{CRIT}">{pill("crit", "Critical")} <b>SQL assistant regression after release v2.3.</b> Task success fell from 92% to 82%. Compare with v2.2 in <a href="{URL}quality/">Quality and evals</a>.</div>'
            f'<div class="need" style="border-color:{SERIOUS}">{pill("serious")} <b>Claims policy documents are 52 hours stale.</b> The source stopped refreshing on Nov 20. See <a href="{URL}data/">Data and retrieval</a>.</div>'
            f'<div class="need" style="border-color:{SERIOUS}">{pill("serious")} <b>Spend is on track to exceed the monthly budget by about 16%.</b> A retry loop doubled the Support agent bill on Nov 22. See <a href="{URL}cost/">Cost and tokens</a>.</div>'
            f'<div class="need" style="border-color:{WARN}">{pill("warn")} <b>Prompt-injection attempts doubled today.</b> All blocked, no data left. See <a href="{URL}safety/">Safety and approvals</a>.</div></div>')
    body = banner() + tabs("overview") + f'<div class="tiles">{tiles}</div>' + need + f'<div class="grid2">{chart1}{chart2}</div>' + health
    body += "<p>The first screen answers one question: is anything wrong, and who needs to act? Everything else is one click down.</p>"
    return shell("overview", "Overview", body, "Sample ops dashboard overview for AI agents: health tiles, task success by agent, requests, agent health table and the issues that need a person now. Made-up data.")


def runs():
    rows = [("run_8f21", "SQL assistant", "10:42", 9, 3, "8.5 s", "14,200", "$0.07", pill("crit", "Failed")), ("run_8f20", "Support agent", "10:41", 6, 2, "4.9 s", "6,100", "$0.03", pill("good", "Success")),
            ("run_8f1f", "Claims intake", "10:41", 8, 3, "9.1 s", "11,800", "$0.06", pill("serious", "No source found")), ("run_8f1e", "Summariser", "10:40", 4, 1, "3.2 s", "9,400", "$0.04", pill("good", "Success")),
            ("run_8f1d", "Support agent", "10:39", 5, 1, "4.1 s", "5,200", "$0.02", pill("warn", "Needs a person")), ("run_8f1c", "Support agent", "10:39", 3, 0, "1.1 s", "900", "$0.00", pill("serious", "Blocked: injection")),
            ("run_8f1b", "SQL assistant", "10:38", 9, 3, "7.9 s", "13,900", "$0.07", pill("crit", "Failed")), ("run_8f1a", "Summariser", "10:38", 4, 1, "3.6 s", "8,800", "$0.04", pill("good", "Success"))]
    t = ('<div class="tw"><table class="t"><tr><th>Run</th><th>Agent</th><th>Started</th><th>Steps</th><th>Tool calls</th><th>Duration</th><th>Tokens</th><th>Cost</th><th>Outcome</th></tr>'
         + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</table></div>")
    filt = '<p class="sub">Filters: agent · outcome · release · last hour. (Sample: filters are not active.)</p>'
    # waterfall
    steps = [("Receive request", 0.0, 0.1, "g"), ("Check the question (guardrail)", 0.1, 0.4, "v"), ("Plan the steps", 0.4, 1.6, "l"), ("Look up metric definitions", 1.6, 2.4, "r"),
             ("Run SQL query", 2.4, 4.1, "t"), ("Retry SQL (1)", 4.1, 5.0, "t"), ("Retry SQL (2)", 5.0, 5.8, "t"), ("Write the answer", 5.8, 8.2, "l"), ("Check the answer (guardrail)", 8.2, 8.5, "v")]
    col = {"g": "#898781", "v": S4, "l": S1, "r": S3, "t": S2}
    w, left, tt = 700, 230, 8.5
    sc = (w - left - 30) / tt
    d = ""
    for k in range(0, 10, 2):
        d += f'<line x1="{left + k * sc:.1f}" y1="20" x2="{left + k * sc:.1f}" y2="{40 + len(steps) * 30}" stroke="{GRID}"/><text x="{left + k * sc:.1f}" y="14" text-anchor="middle" font-size="11.5" fill="{MUTED}">{k} s</text>'
    for i, (nm, a, b, k) in enumerate(steps):
        y = 26 + i * 30
        d += f'<text x="{left - 8}" y="{y + 15}" text-anchor="end" font-size="12.5">{E(nm)}</text>'
        d += f'<rect x="{left + a * sc:.1f}" y="{y + 3}" width="{max((b - a) * sc, 3):.1f}" height="16" rx="3" fill="{col[k]}"><title>{E(nm)}: {a:.1f} s to {b:.1f} s</title></rect>'
        if nm.startswith("Retry"):
            d += f'<text x="{left + b * sc + 6:.1f}" y="{y + 16}" font-size="12" fill="{CRIT}">✕ column not found</text>'
    svg = f'<svg viewBox="0 0 {w} {60 + len(steps) * 30}" role="img" aria-label="Trace waterfall for run 8f21: nine steps over 8.5 seconds, with two failed retries of a SQL tool call">{d}</svg>'
    lg = legend([("Model call", S1), ("Tool call", S2), ("Search", S3), ("Guardrail", S4), ("Other", "#898781")])
    trace = card("Trace of run_8f21 (SQL assistant, failed)", "Each bar is one step. Time runs left to right. This is the picture that tells you where a run went wrong.", lg + svg + table_view(["Step", "From (s)", "To (s)"], [[a, f"{b:.1f}", f"{c:.1f}"] for a, b, c, _ in steps]))
    why = (f'<div class="card"><h3>What happened, in plain words</h3><p>The assistant wrote a query using a column called <code>region_cd</code>. The source team renamed it to <code>region_code</code> on Nov 21. '
           f'The query failed. The assistant retried twice with the same query, then gave the user a vague answer. Three things to fix: refresh the metric definitions, stop retrying an error that cannot succeed, and give a clear message to the user. '
           f'The data side is on the <a href="{URL}data/">Data and retrieval</a> page.</p></div>')
    body = banner() + tabs("runs") + card("Latest runs", "Newest first. The outcome column uses an icon and a word, never colour alone.", filt + t) + trace + why
    return shell("runs", "Runs and traces", body, "Sample ops dashboard for agent runs and traces: a table of recent runs and a step-by-step trace of one failed run. Made-up data.")


def quality():
    ch = card("Evaluation pass rate by suite", "Automatic checks run on a fixed set of test questions every night. Release v2.3 went out on Nov 21.", line_chart([(n, v, c) for (n, v), c in zip(EVALS.items(), [S1, S2, S3, S4])], 80, 100, "{:.0f}", unit="%"))
    rel = [("Task completion", "91.9%", "84.0%", "−7.9 pts", "crit"), ("Groundedness (answers backed by sources)", "93.3%", "89.3%", "−4.0 pts", "serious"), ("Safety checks", "99.1%", "99.0%", "−0.1 pts", "good"),
           ("Format validity", "98.6%", "98.5%", "−0.1 pts", "good"), ("p95 latency", "5.1 s", "6.2 s", "+1.1 s", "warn"), ("Cost per task", "$0.031", "$0.038", "+23%", "warn")]
    rt = ('<div class="tw"><table class="t"><tr><th>Measure</th><th>v2.2</th><th>v2.3</th><th>Change</th><th>Verdict</th></tr>' + "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td><td>{pill(k)}</td></tr>" for a, b, c, d, k in rel) + "</table></div>")
    cmp_ = card("SQL assistant: release v2.3 against v2.2", "The release gate: no ship if a core measure falls more than 2 points.", rt)
    fails = card("Three failing test cases", "Examples to read, not just counts.", "<ol><li><b>'Total claims paid by region last quarter.'</b> Used the old column name <code>region_cd</code>, so the query failed.</li><li><b>'What is the excess on flood cover?'</b> Answered from a policy document that is 52 hours stale.</li><li><b>'Compare this month with last year.'</b> Compared different date ranges and did not say so.</li></ol>")
    fb = [93, 92, 93, 94, 93, 92, 93, 93, 94, 93, 93, 91, 87, 86]
    users = card("User thumbs-up rate", "Real users, not test questions. It confirms what the evals suggest.", line_chart([("Thumbs up", fb, S1)], 80, 100, "{:.0f}", unit="%"))
    body = banner() + tabs("quality") + f'<div class="grid2">{ch}{users}</div>' + cmp_ + fails
    body += "<p>Two sources agree here: the nightly tests and real users both fell after Nov 21. When only one moves, suspect the test set or the feedback widget before the model.</p>"
    return shell("quality", "Quality and evals", body, "Sample ops dashboard for AI quality: evaluation pass rates by suite, a release comparison, failing cases and user feedback. Made-up data.")


def cost():
    lbl = DAYS
    st = card("Spend per day, by model class", "Dollars per day. Nov 22 shows a retry loop in the Support agent: the Large-model bar nearly doubled.", stacked([(k, v, c) for (k, v), c in zip(COST.items(), [S1, S2, S3, S4])]))
    per = hbars([("Summariser", 0.034, None), ("Support agent", 0.035, None), ("Data-quality agent", 0.133, None), ("Claims intake", 0.034, None), ("SQL assistant", 0.040, None)], fmt="${:.3f}")
    pc = card("Cost per successful task", "Dollars per task that actually succeeded. A cheap agent that fails is not cheap.", per)
    bud = (f'<div class="tw"><table class="t"><tr><th>Month to date</th><th>Budget</th><th>Used</th><th>Projected</th><th>Status</th></tr><tr><td>$7,980</td><td>$9,000</td><td>89%</td><td>$10,400</td><td>{pill("serious", "Over budget by ~16%")}</td></tr></table></div>')
    bd = card("Budget", "Month to date, with a projection from the daily average.", bud + hbars([("Used so far", 7980, S1), ("Budget", 9000, "#898781"), ("Projected", 10400, SERIOUS)], fmt="${:,.0f}", maxv=11500))
    top = [("run_7c90", "Support agent", "Nov 22 14:02", "184,000", "$2.10", "Loop: the same tool call 61 times"), ("run_7c8e", "Support agent", "Nov 22 14:01", "176,000", "$1.98", "Loop: the same tool call 58 times"), ("run_8a02", "Summariser", "Nov 23 09:15", "142,000", "$0.71", "Very long document")]
    tt = card("Most expensive runs, last 24 h", "The runs that explain a spike.", '<div class="tw"><table class="t"><tr><th>Run</th><th>Agent</th><th>When</th><th>Tokens</th><th>Cost</th><th>Why</th></tr>' + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in top) + "</table></div>")
    body = banner() + tabs("cost") + f'<div class="grid2">{st}{bd}</div><div class="grid2">{pc}{tt}</div>'
    body += "<p>The useful alert is not 'spend is high'. It is 'this agent's cost per task doubled', with the runs that caused it one click away.</p>"
    return shell("cost", "Cost and tokens", body, "Sample ops dashboard for AI cost: daily spend by model class, cost per successful task, budget projection and the most expensive runs. Made-up data.")


def safety():
    cats = hbars([("Prompt injection", 312, S4), ("Personal data in input", 188, S4), ("Off-topic", 140, S4), ("Unsafe content", 61, S4), ("Jailbreak attempt", 47, S4)], fmt="{:,.0f}")
    c1 = card("Blocked requests by reason, last 7 days", "What the guardrails stopped.", cats)
    c2 = card("Blocked requests per day", "Nov 23 is double the usual: a burst of injection attempts aimed at the Support agent.", line_chart([("Blocked", BLOCKS, S4)], 0, 140, "{:.0f}"))
    ap = [("Refund of ₹18,400", "Support agent", "3 h 10 min", "Over the ₹10,000 limit"), ("Close claim CL-90418", "Claims intake", "2 h 40 min", "Claim above threshold"), ("Delete customer record", "Support agent", "1 h 55 min", "Irreversible action"),
          ("Send email to 240 customers", "Support agent", "55 min", "Bulk message")]
    apr = ('<div class="tw"><table class="t"><tr><th>Action</th><th>Agent</th><th>Waiting</th><th>Why a person</th><th></th></tr>' + "".join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td><td><button class="btn">Approve</button><button class="btn">Reject</button></td></tr>' for a, b, c, d in ap) + "</table></div><p class='sub'>4 of 7 shown. Buttons are not active in this sample.</p>")
    c3 = card("Waiting for a person", "Actions the agent may not take alone. The oldest at the top.", apr)
    inc = [("INC-241", "Prompt-injection burst on Support agent", pill("serious"), "Open", "Support lead", "All blocked, no data left"), ("INC-240", "Claims policy documents stale", pill("serious"), "Open", "Data platform", "Answers may cite old terms"),
           ("INC-238", "SQL assistant regression after v2.3", pill("crit"), "Open", "Analytics", "Roll back or fix forward"), ("INC-239", "Support agent retry loop doubled cost", pill("warn"), "Resolved", "Customer care", "Loop limit added")]
    c4 = card("Incidents", "Every incident has an owner and a status.", '<div class="tw"><table class="t"><tr><th>ID</th><th>What</th><th>Severity</th><th>State</th><th>Owner</th><th>Note</th></tr>' + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in inc) + "</table></div>")
    body = banner() + tabs("safety") + f'<div class="grid2">{c1}{c2}</div>' + c3 + c4
    body += f'<p>This is where the principles on the <a href="/learn/responsible-ai/">Responsible AI</a> page become something an operator can watch: security (blocked attacks), accountability (who owns each incident) and human oversight (the waiting list).</p>'
    return shell("safety", "Safety and approvals", body, "Sample ops dashboard for AI safety: blocked requests by reason, actions waiting for human approval and an incident log. Made-up data.")


def data():
    src = [("Customer tickets", "Customer care", "every 4 h", "1 h", "good"), ("Knowledge-base articles", "Customer care", "daily", "6 h", "good"), ("Product catalogue", "Product", "daily", "9 h", "good"),
           ("Claims policy documents", "Claims ops", "daily", "52 h", "serious"), ("Finance metrics table", "Finance", "daily", "5 h", "warn")]
    notes = {"Claims policy documents": "Refresh job stopped on Nov 20.", "Finance metrics table": "Column renamed: region_cd to region_code (Nov 21)."}
    rows = "".join(f'<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td><td>{pill(k)}</td><td>{notes.get(a, "")}</td></tr>' for a, b, c, d, k in src)
    t = card("Source freshness", "How old is the data the AI reads, against how old it is allowed to be.", f'<div class="tw"><table class="t"><tr><th>Source</th><th>Owner</th><th>Expected</th><th>Age now</th><th>Status</th><th>Note</th></tr>{rows}</table></div>')
    ret = card("Retrieval hit rate", "Share of questions where the search found a useful source. Claims fell as its documents went stale.", line_chart([("Support KB", HIT["Support knowledge base"], S1), ("Claims policy docs", HIT["Claims policy documents"], S2)], 60, 100, "{:.0f}", unit="%"))
    ns = card("Answers with no source found", "A rising line here means the AI is answering from memory. One measure, one axis.", line_chart([("No source", NOSRC, S2)], 0, 20, "{:.0f}", unit="%"))
    chg = card("Changes detected upstream", "The data side of an AI incident. Each links to the owner of the source.", "<ul><li><b>Nov 21.</b> Finance metrics table: column <code>region_cd</code> renamed to <code>region_code</code>. The SQL assistant still uses the old name.</li><li><b>Nov 20.</b> Claims policy documents: refresh job stopped. No new documents indexed since.</li><li><b>Nov 18.</b> Product catalogue: 1,204 new items, all indexed.</li></ul>")
    body = banner() + tabs("data") + t + f'<div class="grid2">{ret}{ns}</div>' + chg
    body += '<p>Most AI failures that look like model problems start here. See the <a href="/learn/data-systems/">data systems</a> pages and the <a href="/concepts/data-quality/">data quality</a> and <a href="/concepts/lineage/">lineage</a> ideas.</p>'
    return shell("data", "Data and retrieval", body, "Sample ops dashboard for the data behind AI: source freshness, retrieval hit rate, answers with no source and upstream changes. Made-up data.")


def governance():
    tiles = "".join([tile("AI systems registered", "12", "9 built here, 3 bought in", "good"), tile("High-risk systems", "3", "each with a named owner", "good"), tile("Reviews overdue", "2", "oldest 41 days", "serious"), tile("Incidents, 30 days", "4", "1 critical", "warn")])
    reg = [("Support agent", "Customer care", "Medium", "Oct 14", "Jan 14", "n/a", "Approval over ₹10,000", "good"), ("Claims intake", "Claims ops", "High", "Sep 02", "Dec 02", "Passed Sep", "Person decides all claims", "good"),
           ("SQL assistant", "Analytics", "Medium", "Aug 20", "Nov 20", "n/a", "Read-only data", "serious"), ("Summariser", "Operations", "Low", "Oct 30", "Apr 30", "n/a", "Advice only", "good"),
           ("CV screening (bought in)", "HR", "High", "Jun 11", "Oct 11", "Overdue", "Person reviews rejections", "serious"), ("Pricing model", "Sales", "High", "Oct 01", "Jan 01", "Passed Oct", "Person approves changes", "good")]
    rows = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td><td>{e}</td><td>{f}</td><td>{g}</td><td>{pill(k, 'Review overdue' if k == 'serious' else 'Up to date')}</td></tr>" for a, b, c, d, e, f, g, k in reg)
    t = card("AI register", "Every AI system, tool and bought-in product: owner, risk tier, review dates, fairness testing, human oversight.", f'<div class="tw"><table class="t"><tr><th>System</th><th>Owner</th><th>Risk tier</th><th>Last review</th><th>Next due</th><th>Fairness test</th><th>Human oversight</th><th>Review</th></tr>{rows}</table></div>')
    tier = card("Systems by risk tier", "Match the care to the risk.", hbars([("Low", 4, S3), ("Medium", 5, S1), ("High", 3, S2)], fmt="{:.0f}"))
    body = banner() + tabs("governance") + f'<div class="tiles">{tiles}</div>' + t + tier
    body += '<p>This is the register and the review calendar from the <a href="/learn/responsible-ai/">Responsible AI</a> page, turned into something that raises its hand when a review is late. The wider system is in <a href="/learn/ai-governance/">AI governance</a>.</p>'
    return shell("governance", "Governance", body, "Sample ops dashboard for AI governance: the register of AI systems, risk tiers, review dates, fairness tests and human oversight. Made-up data.")


def hub():
    qs = table(["The operator's question", "Where it is answered", "Sample page"], [[E(q), E(n), f'<a href="{URL}{k}/">{E(n)}</a>'] for k, n, q in PAGES])
    feeds = table(["What the dashboard shows", "Where the data usually comes from"], [
        ["Runs, steps, tool calls, duration", "Traces from the agent framework or gateway. OpenTelemetry has conventions for model calls (check the current status)."],
        ["Tokens and cost", "The model gateway or the cloud bill, joined to the run by an ID."],
        ["Quality and evals", "Nightly test runs, plus user feedback and sampled human review."],
        ["Guardrail blocks and approvals", "The guardrail layer and the human-approval queue."],
        ["Data freshness and retrieval", "The data platform's pipeline logs, quality checks and the search index."],
        ["Register and reviews", "The AI system register, kept by governance."]])
    rules = ("<ol><li><b>Answer 'is anything wrong?' on one screen.</b> Status first, numbers second.</li><li><b>Alert on symptoms, then link to causes.</b> 'Task success fell' with a link to the release and the data change.</li>"
             "<li><b>Show a person's next action.</b> Every red item has an owner and a link.</li><li><b>One measure per chart, one axis.</b> Never two scales on one chart.</li>"
             "<li><b>Colour never carries meaning alone.</b> Status uses an icon and a word.</li><li><b>Keep a table view.</b> Anyone can read the exact numbers.</li><li><b>Join the story.</b> The same incident should be visible from quality, cost, safety and data.</li></ol>")
    body = f"""<p class="lede">A dashboard for running AI and agents day to day. It is different from an analytics dashboard: it is built for an operator who must decide in minutes whether something is wrong, why, and who should act. These are seven sample views, with made-up data and one story running through them.</p>
<section><p class="eyebrow">The idea</p><h2>Seven questions, seven views</h2>{qs}</section>
<section><p class="eyebrow">See them</p><h2>The sample dashboards</h2><div class="cards3">{"".join(f'<div><h3><a href="{URL}{k}/">{E(n)}</a></h3><p>{E(q)}</p></div>' for k, n, q in PAGES)}</div>
<div class="box"><b>The story in the samples:</b> on Nov 20 the claims policy documents stop refreshing; on Nov 21 a source column is renamed and a new release of the SQL assistant goes out; on Nov 22 a retry loop doubles spend; on Nov 23 a burst of injection attempts is blocked. Follow it from the Overview into each view.</div></section>
<section><p class="eyebrow">Design rules</p><h2>What makes these views usable</h2>{rules}</section>
<section><p class="eyebrow">Where the data comes from</p><h2>What feeds each view</h2>{feeds}</section>
<section><p class="eyebrow">Go further</p><h2>Related pages</h2><ul><li>{DE.Lx('/learn/responsible-ai/', 'Responsible AI, explained')}</li><li>{DE.Lx('/learn/ai-governance/', 'AI governance: running AI you can trust')}</li><li>{DE.Lx('/learn/agent-guardrails/', 'Agent guardrails')}</li><li>{DE.Lx('/learn/eval-harness/', 'Eval Harness')}</li></ul></section>"""
    return shell(None, "AI ops dashboard: what it looks like", body, "Seven sample ops dashboards for AI and agents: overview, runs and traces, quality, cost, safety and approvals, data and retrieval, governance. Made-up data, one story.")


def main():
    for rel, html in [hub(), overview(), runs(), quality(), cost(), safety(), data(), governance()]:
        DE.write(rel, html)


if __name__ == "__main__":
    main()
