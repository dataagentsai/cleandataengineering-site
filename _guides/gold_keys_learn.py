"""Learn-from-zero sections for /learn/gold-data-modelling/ (imported by gold_modelling.py):
keys from zero (business, durable, surrogate, fact primary key, how keys are made, what changes when),
kinds of dimension with examples, and bridge tables.

Numbers come from _guides/code/gold_keys/results.json (e2e.py, run 14 Nov 2026 on Spark 3.5.1); code is read
from keys.py and bridge.py, which have 14 table-driven tests (test_keys.py).
"""
import ast
import json
import sys
from html import escape as E
from pathlib import Path

HERE = Path(__file__).parent
CODE = HERE / "code" / "gold_keys"
sys.path.insert(0, str(HERE))
import components as C  # noqa: E402
from bi_choice import ar, bx, svg, t, vtable  # noqa: E402
from gold_harness_spec import fig  # noqa: E402
from silver_to_gold_learn import EXTRA_CSS, htable  # noqa: E402,F401

R = json.loads((CODE / "results.json").read_text())


def src(file, *names):
    text = (CODE / file).read_text()
    return "\n\n\n".join(ast.get_source_segment(text, n) for n in ast.parse(text).body if getattr(n, "name", None) in names)


def nd(s):
    if s is None:
        return ""
    s = str(s)
    if s.startswith("9999"):
        return "open"
    if s.startswith("1900"):
        return "(from the start)"
    if len(s) == 10 and s[4] == "-":
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return f"{int(s[8:])} {months[int(s[5:7]) - 1]} {s[:4]}"
    return s


# ------------------------------------------------------------------ drawings
def d_person():
    i = bx(380, 20, 240, 80, ["Asha, the person", "(one durable key)"], "g", 16)
    i += bx(20, 20, 300, 80, ["passport P123, later P987", "(business keys: issued by others,", "can change)"], "w", 14) + ar(320, 60, 378, 60)
    i += bx(680, 10, 300, 46, ["address 1: Pune, 2019 to 2024"], "b", 14) + bx(680, 66, 300, 46, ["address 2: Delhi, 2024 to now"], "y", 14)
    i += ar(620, 50, 678, 33) + ar(620, 70, 678, 89)
    i += bx(560, 160, 200, 60, ["letter, 2023", "addressed to Pune"], "w", 14) + ar(600, 158, 678, 42)
    i += bx(780, 160, 200, 60, ["letter, 2025", "addressed to Delhi"], "w", 14) + ar(880, 158, 840, 114)
    i += t(500, 252, "When Asha moves, nobody rewrites the 2023 letter. It was sent to Pune, and that stays true.", 14, "middle")
    i += t(500, 274, "Letters are facts. Each address is one dimension version (one surrogate key). Asha is the durable key. Passports are business keys.", 14, "middle")
    return svg(1000, 286, "An everyday picture of keys. Asha is one person: one durable key. Her passport numbers, P123 and "
                          "later P987, are business keys issued by someone else that can change. Her addresses are versions: "
                          "Pune from 2019 to 2024, Delhi from 2024. A letter from 2023 was addressed to Pune and a letter from "
                          "2025 to Delhi. When she moves, nobody rewrites the old letter. Letters are facts, addresses are "
                          "dimension versions.", i)


def d_four():
    i = t(95, 18, "1. business keys", 13, "middle") + t(305, 18, "2. key map", 13, "middle") + t(520, 18, "3. durable key", 13, "middle")
    i += t(760, 18, "4. version (surrogate) keys", 13, "middle")
    i += bx(10, 40, 170, 50, ["ERP: D7"], "w", 14) + bx(10, 110, 170, 50, ["new ERP: DLR-0007"], "w", 14)
    i += ar(180, 65, 228, 90) + ar(180, 135, 228, 110)
    i += bx(230, 60, 150, 70, ["key map", "both -> 2"], "l", 14) + ar(380, 95, 448, 95)
    i += bx(450, 60, 140, 70, ["dealer_dk 2", "Patel Motors"], "g", 15) + ar(590, 85, 648, 60) + ar(590, 105, 648, 130)
    i += bx(650, 34, 220, 52, ["dealer_sk 102: North", "until 12 Nov"], "b", 14) + bx(650, 106, 220, 52, ["dealer_sk 103: West", "from 12 Nov"], "y", 14)
    i += bx(30, 200, 280, 56, ["fact L3, promised 11 Nov", "dealer_sk 102, dealer_dk 2"], "w", 13)
    i += bx(360, 200, 280, 56, ["fact L4, promised 13 Nov", "dealer_sk 103, dealer_dk 2"], "w", 13)
    i += bx(690, 200, 280, 56, ["fact L7, from new ERP, 14 Nov", "dealer_sk 103, dealer_dk 2"], "w", 13)
    i += ar(170, 198, 700, 88, dash=True) + ar(500, 198, 740, 160, dash=True) + ar(830, 198, 800, 160, dash=True)
    i += t(500, 284, "each fact row's own key (its primary key) is its grain: line_id. Not a dealer key at all.", 13, "middle")
    return svg(1000, 296, "One dealer through every kind of key. Business keys from two systems, D7 and DLR-0007, go through "
                          "the key map to one durable key, 2, Patel Motors. That dealer has two versions: surrogate key 102 "
                          "(North, until 12 November) and 103 (West, from 12 November). Fact L3, promised 11 November, stores "
                          "102 and 2. Fact L4, 13 November, stores 103 and 2. Fact L7 from the new system on 14 November "
                          "also stores 103 and 2. Each fact row's own primary key is its grain, line_id.", i)


def d_change():
    i = ""
    panels = [("1. Fix a typo (Type 1)", "w", "row 102 edited in place", "L3 -> 102: unchanged", "g"),
              ("2. Dealer moves (Type 2)", "w", "new row 103 added", "L3 -> 102: unchanged; L4 -> 103", "g"),
              ("3. Late dealer (inferred)", "w", "row 104 filled in later", "L5 -> 104: unchanged", "g"),
              ("4. Rebuild renumbers keys", "w", "102 now means Gupta Tyres", "L3 -> 102: now WRONG", "r")]
    for k, (title, f, dim, fact, ff) in enumerate(panels):
        x = 10 + k * 247
        i += bx(x, 10, 232, 220, [""], f) + t(x + 116, 36, title, 14, "middle")
        i += bx(x + 16, 56, 200, 56, ["dimension:", dim], "b", 13) + ar(x + 116, 146, x + 116, 114)
        i += bx(x + 16, 148, 200, 56, ["fact:", fact], ff, 13)
    i += t(500, 256, "Facts store keys once. A dimension change never needs a fact change, as long as keys are never renumbered.", 14, "middle")
    return svg(1000, 268, "What a change to a dimension does to facts. 1, fixing a typo edits row 102 in place; fact L3 still "
                          "points at 102, unchanged. 2, a dealer moving adds row 103; L3 keeps 102 and new fact L4 gets 103. "
                          "3, a late dealer's placeholder row 104 is filled in later; L5 keeps 104. 4, a rebuild that renumbers "
                          "keys makes 102 mean Gupta Tyres, so L3 is now wrong. Facts store keys once; a dimension change never "
                          "needs a fact change as long as keys are never renumbered.", i)


def d_dim_kinds():
    cards = [("Conformed", "one dealer list for every fact", "g"), ("Date", "a row per day, with months, holidays", "g"),
             ("Role-playing", "date used as order, promised, delivered", "g"), ("Changing (SCD)", "keeps history, or not", "b"),
             ("Degenerate", "order_id on the fact, no table", "w"), ("Junk", "a bag of small flags in one table", "w"),
             ("Mini-dimension", "fast-changing bands split off", "b"), ("Outrigger", "a dimension pointing to another", "y"),
             ("Shrunken", "month, region: a coarser copy", "w"), ("Hierarchy", "org chart, category tree", "y"),
             ("Multi-valued", "several members per fact row", "r"), ("Reference and audit", "units, currencies; run ids", "w")]
    i = ""
    for k, (n, s, f) in enumerate(cards):
        x, y = 10 + (k % 4) * 247, 10 + (k // 4) * 92
        i += bx(x, y, 232, 80, [n, s], f, 15)
    return svg(1000, 286, "Twelve kinds of dimension: conformed, date, role-playing, changing (SCD), degenerate, junk, "
                          "mini-dimension, outrigger, shrunken, hierarchy, multi-valued, and reference and audit.", i)


def d_role():
    i = bx(390, 70, 220, 90, ["fact_otif", "order_date_key", "promised_date_key", "delivered_date_key"], "y", 14)
    i += bx(20, 10, 230, 56, ["view: order_date"], "g", 14) + bx(20, 90, 230, 56, ["view: promised_date"], "g", 14)
    i += bx(20, 170, 230, 56, ["view: delivered_date"], "g", 14)
    for y in (38, 118, 198):
        i += ar(388, 115, 252, y)
    i += bx(700, 70, 280, 90, ["dim_date", "one table, one row per day,", "read by all three views"], "b", 14)
    i += t(500, 250, "one date table, three roles: each role is a view with its own column names", 13, "middle")
    return svg(1000, 262, "A role-playing dimension. fact_otif has three date keys: order, promised and delivered. Each points "
                          "at a view named for its role, and all three views read the same dim_date table.", i)


def d_junk():
    i = bx(10, 30, 330, 150, ["fact without a junk dimension", "is_rush  Y / N", "payment  cash / credit", "channel  dealer / online",
                              "4 flag columns on every row"], "w", 14)
    i += ar(340, 105, 398, 105)
    i += bx(400, 10, 260, 190, ["dim_order_profile (junk)", "1: N, cash, dealer", "2: N, cash, online", "3: N, credit, dealer",
                                "...", "8: Y, credit, online"], "b", 13)
    i += ar(660, 105, 718, 105) + bx(720, 50, 270, 110, ["fact keeps ONE column:", "order_profile_key = 3"], "y", 14)
    return svg(1000, 212, "A junk dimension. Instead of three small flag columns on every fact row (rush yes or no, payment cash "
                          "or credit, channel dealer or online), one small table lists all eight combinations, and the fact "
                          "keeps one key, for example 3 for not rush, credit, dealer.", i)


def d_bridge():
    i = bx(10, 10, 470, 230, [""], "w") + t(245, 34, "without a bridge: join reps straight on", 15, "middle")
    i += bx(30, 60, 150, 56, ["L3", "revenue 40,000"], "y", 14) + ar(180, 88, 228, 70) + ar(180, 88, 228, 128)
    i += bx(230, 48, 230, 44, ["Asha: 40,000"], "r", 13) + bx(230, 106, 230, 44, ["Vik: 40,000"], "r", 13)
    i += t(245, 190, "one sale of 40,000 now counts as 80,000", 14, "middle")
    i += bx(520, 10, 470, 230, [""], "w") + t(755, 34, "with a bridge and weights", 15, "middle")
    i += bx(540, 60, 130, 56, ["L3", "rep_group G2"], "y", 14) + ar(670, 88, 698, 88)
    i += bx(700, 50, 130, 76, ["bridge G2", "Asha 0.6", "Vik 0.4"], "b", 13) + ar(830, 88, 858, 88)
    i += bx(860, 50, 115, 76, ["Asha 24,000", "Vik 16,000", "= 40,000"], "g", 13)
    i += t(755, 190, "weights add to 1, so totals stay right", 14, "middle")
    return svg(1000, 252, "Why a bridge. Without it, order line L3 worth 40,000, sold by two reps, is joined to both and "
                          "counts as 80,000. With a bridge, the fact stores group G2; the bridge lists Asha 0.6 and Vik 0.4; "
                          "shared out, Asha gets 24,000 and Vik 16,000, still 40,000.", i)


def d_hier():
    i = bx(400, 10, 200, 50, ["Head of Sales"], "g", 14)
    i += bx(200, 100, 200, 50, ["North manager"], "b", 14) + bx(600, 100, 200, 50, ["West manager"], "b", 14)
    i += bx(200, 190, 200, 50, ["Asha"], "w", 14) + bx(600, 190, 200, 50, ["Vik"], "w", 14)
    i += ar(460, 60, 330, 98) + ar(540, 60, 670, 98) + ar(300, 150, 300, 188) + ar(700, 150, 700, 188)
    i += bx(830, 10, 160, 150, ["bridge rows for", "the Head:", "Head-Head 0", "Head-managers 1", "Head-Asha 2", "Head-Vik 2"], "y", 12)
    i += t(500, 270, "one row per (person above, person below): 'sum everything under X' becomes one join", 13, "middle")
    return svg(1000, 282, "A hierarchy bridge. Head of Sales manages a North manager, who manages Asha, and a West manager, "
                          "who manages Vik. The bridge holds one row per pair of a person and anyone below them, with the "
                          "depth, so the total under any person is one join.", i)


# ------------------------------------------------------------------ content
KEY_WORDS = [
    ("Business key", "The source's own code", "D7 in the ERP; DLR-0007 in the new ERP", "Comes from outside. Can change, be reused, or differ between systems. Kept as a column; never the link from facts."),
    ("Durable key", "One number per real thing", "dealer_dk 2 = Patel Motors", "Given once by the key map and never changes, whatever the source does. Use it for 'today's view' of history."),
    ("Surrogate key (version key)", "One number per dimension row", "dealer_sk 102 (North), 103 (West)", "With history (SCD Type 2), each version gets its own. Facts store it to remember the version true on their date."),
    ("Dimension primary key", "What makes a dimension row unique", "dealer_sk", "The surrogate key. Unique, never null, never reused, never renumbered."),
    ("Fact primary key", "What makes a fact row unique", "line_id on fact_otif", "The grain. Not a dealer key: many fact rows share one dealer."),
    ("Reserved keys", "Special rows in every dimension", "-1 unknown, -2 not applicable", "So a fact never has an empty key and joins never drop rows."),
]

FACT_PK = [
    ("fact_otif (transaction)", "one row per order line", "line_id", "The order line's own id (a degenerate dimension)"),
    ("fact_daily_stock (periodic snapshot)", "one row per warehouse, product and day", "warehouse_dk + product_dk + snapshot_date", "Several columns together"),
    ("fact_line_lifecycle (accumulating)", "one row per order line", "line_id", "Same as its process"),
    ("fact_rep_visit (factless)", "one row per rep, dealer and day", "rep_dk + dealer_dk + visit_date", "The row IS the event"),
    ("fact_otif_region_day (aggregate)", "one row per day and region", "promised_date + region", "The grain it was added up to"),
    ("fact_plan_vs_actual (consolidated)", "one row per dealer and month", "dealer_dk + month", "The shared grain"),
]

SK_WAYS = [
    ("Key map (assign once, store)", "The first time a version is seen, it gets the next number (102, 103...) and the pair is saved. Later runs look it up.", "Stable forever; small integers; survives rebuilds and source renames", "Needs a small table and one writer at a time", "Pursue: our default"),
    ("Hash of business key + version date", "dealer_sk = hash('D7', 12 Nov 2026). No table: compute it anywhere.", "No lookup table; same number on every rerun and every engine", "Changes if the business key changes (our run: different hash for D7 and DLR-0007); 64-bit numbers; rare collisions to check", "Pursue with care: when one stable source owns the code"),
    ("Identity or row number at build", "Number the rows each time the dimension is built.", "Simple", "A rebuild renumbers everything; old facts silently point at other dealers (our run below)", "Drop"),
    ("The source's code as the key", "Facts store D7 directly.", "No work", "Breaks with history (which version?), with two systems, and when codes are reused", "Drop"),
]

CHANGES = [
    ("A typo in a name is fixed (Type 1)", "Row 102 (and 103) edited in place; keys unchanged", "No", "All history now shows the right spelling, which is what you want"),
    ("Dealer moves region (Type 2)", "Row 102 closed (valid_to 12 Nov); new row 103 added", "No", "Old facts keep 102 (North, true then); new facts get 103"),
    ("A fact arrives before its dealer: inferred member", "Placeholder row 104 created at fact load; filled in when the dealer arrives", "No", "Our run: 0 fact rows rewritten"),
    ("A fact arrives before its dealer: unknown key (-1)", "Fact stores -1; when the dealer arrives, the fact is re-keyed", "Yes, those rows", "Our run: 1 fact row rewritten (L5: -1 to 104)"),
    ("Source system renames the code (D7 to DLR-0007)", "Key map adds DLR-0007 -> durable 2; keys unchanged", "No (key map). Yes (hash keys)", "With hash keys every new fact gets a different number than the old facts"),
    ("Two dealers found to be the same (merge)", "Key map points both codes at one durable key; old versions stay", "No", "'Today's view' joins on the durable key, so both show as one"),
    ("Someone rebuilds the dimension with new numbers", "Every key can change", "Yes, all of them", "Never do this: it is why keys are assigned once and stored"),
    ("The fact's own numbers change (late delivery)", "Not a dimension change", "Yes, that fact row", "Replaced in its window by the harness, logged as a restatement"),
]

DIM_KINDS = [
    ("Conformed", "One dimension, same keys and values, shared by every fact that needs it", "dim_dealer used by orders, deliveries and rep visits", "Bank: dim_customer used by transactions and support tickets", "Pursue: always for shared things"),
    ("Date (calendar)", "One row per day: week, month, fiscal period, holiday, working day", "Promised date with 'is_working_day' for OTIF", "Retail: festival weeks (Diwali) as a column", "Pursue: every mart has one"),
    ("Role-playing", "The same dimension used several times on one fact, under different names", "Date as order, promised and delivered date", "Airline: airport as origin and destination", "Pursue: one table, one view per role"),
    ("Changing (SCD types 0 to 6)", "How a dimension keeps or drops history", "Region Type 2, phone number Type 1", "Hospital: patient address Type 2", "Pursue per column; see the SCD table below"),
    ("Degenerate", "An id kept on the fact, with no table of its own", "order_id on fact_otif", "Invoice number, ticket number", "Pursue"),
    ("Junk", "A small table of every combination of low-value flags", "Rush yes/no, payment type, channel", "E-commerce: gift wrap, coupon used, express", "Pursue when a fact has several small flags"),
    ("Mini-dimension", "Fast-changing attributes split from a big dimension into their own", "Dealer credit band, changing monthly", "Bank: customer income band and age band", "Pursue when Type 2 would multiply rows"),
    ("Outrigger", "A dimension that points to another dimension", "Dealer to its city and state", "Product to its supplier", "Pursue with care: usually flatten the columns in"),
    ("Shrunken (rolled up)", "A smaller copy at a coarser level, for aggregate facts", "dim_month and dim_region for the monthly plan", "Retail: store group for weekly targets", "Pursue for aggregate and consolidated facts"),
    ("Hierarchy (parent-child)", "Members nested at uneven depths", "Sales org chart", "Chart of accounts; product category tree", "Flatten fixed levels into columns; bridge for uneven ones"),
    ("Multi-valued", "One fact row belongs to several members", "Two reps on one order line", "Hospital stay with several diagnoses; joint bank account", "Pursue via a bridge table"),
    ("Reference and audit", "Small fixed lists; and how a row got there", "Units, currencies; run id and source", "Country codes; ICD codes", "Pursue; audit is often just columns"),
]

BRIDGE_WHEN = [
    ("Several sales reps share an order line", "Multi-valued", "Commission and sales by rep", "Bridge with weights (shares)"),
    ("A hospital stay has several diagnoses", "Multi-valued", "Cost by diagnosis; stays per diagnosis", "Bridge; weights for cost, none for counts"),
    ("A joint bank account has two holders", "Multi-valued", "Balances by customer", "Bridge with ownership share"),
    ("A film has three genres", "Multi-valued", "Minutes watched by genre", "Bridge; equal weights or counts only"),
    ("An employee has several skills", "Multi-valued", "Headcount by skill", "Bridge, no weights: count people"),
    ("Org chart, chart of accounts, category tree of uneven depth", "Hierarchy", "Total under any manager or account", "Hierarchy bridge (ancestor, descendant, depth)"),
    ("A tyre is built from parts that are built from parts", "Hierarchy", "Cost of all parts under a product", "Hierarchy bridge (bill of materials)"),
]

BRIDGE_NOT = [
    ("Each fact row has exactly one member", "A normal key on the fact. This is most dimensions.", "No bridge"),
    ("Several members, but one is 'main'", "Keep the main one as a normal key (primary diagnosis, lead rep)", "No bridge, if only the main one is reported"),
    ("At most two or three, always the same roles", "Separate keys: rep_1_key, rep_2_key", "No bridge; simpler"),
    ("A hierarchy with fixed levels", "Flatten into columns: region, area, territory", "No bridge"),
]

BRIDGE_RULES = [
    ("Weights add up to 1 per group", "Checked every run; a group off by any amount stops the build (tested)"),
    ("Sums use the weight", "revenue x weight, then add up: totals stay right"),
    ("Counts may ignore the weight", "'How many lines did Vik work on?' counts distinct lines, never sums revenue"),
    ("Groups are reused", "The same set of reps with the same shares is one group, used by many fact rows"),
    ("A bridge can have history", "If shares change over time, give the bridge valid_from and valid_to, like an SCD2 dimension"),
    ("Hide it from report users", "Expose 'revenue by rep (shared)' in the metric view; most tools double count if users join the bridge themselves"),
]


def part_keys():
    s1, s2, s3, s4, s5 = R["step1"], R["step2"], R["step3"], R["step4"], R["step5"]
    km = htable(["source", "business_key", "dealer_dk"], [[k["source"], k["business_key"], k["dealer_dk"]] for k in s4["keymap"]], hl=[2, 3])
    dimcols = ["dealer_sk", "dealer_dk", "business_key", "name", "region", "valid_from", "valid_to", "is_current"]
    dim1 = htable(dimcols, [[d[c] if c not in ("valid_from", "valid_to") else nd(d[c]) for c in dimcols] for d in s1["dim"]])
    dim2 = htable(dimcols + ["inferred"], [[d[c] if c not in ("valid_from", "valid_to") else nd(d[c]) for c in dimcols + ["inferred"]] for d in s2["dim"]], hl=[1, 2, 3])
    f1 = htable(["line_id", "dealer_id (business key)", "promised", "dealer_sk", "dealer_dk"], [[f["line_id"], f["dealer_id"], nd(f["promised_date"]), f["dealer_sk"], f["dealer_dk"]] for f in s1["fact"]])
    f2 = htable(["line_id", "dealer_id", "promised", "dealer_sk", "dealer_dk", "dealer name", "region on that date"],
                [[f["line_id"], f["dealer_id"], nd(f["promised_date"]), f["dealer_sk"], f["dealer_dk"], f["dealer_name"], f["region_as_was"]] for f in s2["fact"]], hl=[2, 3], dim=[0, 1])
    d9 = htable(["when", "dealer_sk", "name", "region", "inferred"], [["13 Nov (placeholder)", s3["d9_before"][0]["dealer_sk"], s3["d9_before"][0]["name"], s3["d9_before"][0]["region"], s3["d9_before"][0]["inferred"]],
                                                                    ["15 Nov (real details)", s3["d9_after"][0]["dealer_sk"], s3["d9_after"][0]["name"], s3["d9_after"][0]["region"], s3["d9_after"][0]["inferred"]]], hl=[1])
    ren = htable(["fact", "stored dealer_sk", "was", "after a renumbering rebuild, the key now means"],
                 [[f["line_id"], f["dealer_sk"], {"L1": "Sharma Tyres", "L3": "Patel Motors, North", "L4": "Patel Motors, West", "L5": "Kumar Wheels"}[f["line_id"]],
                   next(f"{r['name']}, {r['region']}" for r in s5["renumbered"] if r["dealer_sk"] == f["dealer_sk"])] for f in s5["fact_now_reads"]], hl=[1, 2, 3])
    both = htable(["line_id", "dealer", "promised", "region as it was (join on dealer_sk)", "region today (join dealer_dk to current row)"],
                  [[x["line_id"], x["dealer_id"], nd(x["promised_date"]), x["region_as_was"], x["region_as_is"]] for x in R["step6"]], hl=[1])
    return f"""
<section id="keys-zero"><p class="eyebrow">2a. Keys from zero</p><h2>Keys from zero: one picture, one dealer, one story</h2>
<p>Keys feel abstract until you see them on real rows. Start with something everyone knows.</p>
{fig(d_person(), "A person, their passport numbers, their addresses, and letters sent to them.")}
<p>Keep that picture. Now the same thing for a dealer, Patel Motors, which our tyre company calls <b>D7</b>. Patel Motors moved from the North region to the West on 12 Nov, and later a new ERP system started calling it <b>DLR-0007</b>.</p>
{fig(d_four(), "Business keys come in from systems; the key map turns them into one durable key; each version gets a surrogate key; facts store keys.")}
{C.table(["Key", "In one line", "In the example", "Why it exists"], KEY_WORDS)}

<h3>The story, run for real</h3>
<p>Every table below came out of a run of the code on this page (Spark 3.5.1, 14 Nov 2026).</p>
<p><b>Step 1: first load.</b> Two dealers arrive. The key map gives each a durable key (1 and 2), and each version a surrogate key (101 and 102). Note the typo "Patel Motor": we fix it in step 2. Two order lines are loaded. The build looks up each line's business key <i>as of its promised date</i> and stores the keys it finds.</p>
{dim1}{f1}
<p><b>Step 2: three things happen on 12 to 13 Nov.</b> The typo is fixed (a Type 1 change). D7 moves to the West (a Type 2 change). A new line L5 arrives for dealer <b>D9</b>, who is not in the dealer list yet.</p>
{dim2}
<ul><li><b>Typo fixed:</b> rows 102 and 103 now say "Patel Motors". The keys did not change.</li>
<li><b>Move:</b> row 102 got an end date (12 Nov) and row 103 was added for the West.</li>
<li><b>D9:</b> a placeholder row, 104, was made with real keys and "unknown" values. This is called an <b>inferred member</b>.</li></ul>
{f2}
<p>The old fact rows L1 and L3 were <b>not touched</b>. Compared with step 1, they are identical: <b>{"yes" if s2["old_fact_rows_unchanged"] else "NO"}</b>. L3 still says North, because Patel Motors was in the North on 11 Nov. Like the letter sent to Pune.</p>
<p><b>Step 3: D9's real details arrive on 15 Nov.</b> Row 104 is filled in, in place. Its key stays 104, so L5 needs no change: {s3["fact_rows_rewritten"]} fact rows rewritten. With the other approach, the unknown key -1, L5 would have stored -1 and would now have to be rewritten to 104: {s3["unknown_member_alternative"]["fact_rows_rewritten"]} fact row rewritten.</p>
{d9}
<p><b>Step 4: a new ERP calls Patel Motors "DLR-0007".</b> The key map simply gets one more line pointing at the same durable key 2. A new fact L7 from the new system on 14 Nov gets dealer_sk {s4["L7"]["dealer_sk"]} and dealer_dk {s4["L7"]["dealer_dk"]}: exactly the same as L4 from the old system.</p>
{km}
<p>With <b>hash keys</b>, this would have broken. The hash of ("D7", 12 Nov) is {s4["hash_old_code"]}, and the hash of ("DLR-0007", 12 Nov) is {s4["hash_new_code"]}. Same dealer, same version, different key: {"they match" if s4["hash_match"] else "they do not match"}. Old and new facts would point at different keys for one dealer.</p>
<p><b>Step 5: what goes wrong if keys are numbered at build time.</b> Say someone rebuilds the dimension and numbers the rows 101, 102, 103... in order. A new dealer, D5 Gupta Tyres, has arrived in the meantime. It sorts before D7, so every number after it shifts by one. The facts still hold their old numbers:</p>
{ren}
<p>No error, no warning. L3's sale now reports under a different dealer, and L4 and L5 under the wrong versions. That is why a surrogate key is <b>assigned once, stored, and never renumbered</b>.</p>
{fig(d_change(), "Four kinds of change. Only renumbering hurts the facts.")}

<h3>So: if a surrogate key changes, does the fact change? Is the fact append-only?</h3>
<div class="box"><b>The short answer.</b> A surrogate key is a promise: once given to a version, it never changes. So when a dimension changes, <b>facts do not change</b>. A Type 1 fix edits the dimension row, a Type 2 change adds a new row, and an inferred member is filled in, all without touching a fact. The fact's keys are written once, when the fact row is loaded. Facts are rewritten only for their <i>own</i> reasons: late data or a correction to their own numbers (the window is replaced), or re-keying rows that were stored with the unknown key -1.</div>
{C.table(["What happens", "In the dimension", "Must facts change?", "Note"], CHANGES)}

<h3>As it was, or as it is today: why facts carry two keys</h3>
<p>L3 was sold when Patel Motors was in the North. Today Patel Motors is in the West. Which region should L3 count under? Both answers are useful, for different questions:</p>
{both}
<ul><li><b>"How did each region do at the time?"</b> Join on <code>dealer_sk</code>, the version key stored on the fact. L3 counts under North.</li>
<li><b>"How do today's regions' dealers compare over the years?"</b> Join the fact's <code>dealer_dk</code> to the dealer's <i>current</i> row. L3 counts under West.</li></ul>
<p>Two small integer columns on the fact give both views, and nothing ever needs rewriting.</p>

<h3>The fact's own primary key</h3>
<p>A fact's primary key is what makes one of its rows unique. That is its <b>grain</b>, not a dimension key. Many order lines share dealer 103, so dealer_sk cannot be a fact's primary key.</p>
{C.table(["Fact", "Grain", "Primary key", "Note"], FACT_PK)}
<p>Use durable keys (or the business id) in a fact's primary key, not version keys. A version can change while the row stays the same row. Check the primary key is unique on every run, before writing.</p>

<h3>How to make surrogate keys</h3>
{vtable(["Way", "How", "Good", "Bad", "Verdict"], SK_WAYS)}
<details class="code" open><summary>The key map and version keys, as tested (keys.py)</summary>{C.code(src("keys.py", "assign_durable_keys", "assign_version_keys"))}</details>
<details class="code"><summary>The lookup that stores keys on a fact, and the two other ways (keys.py)</summary>{C.code(src("keys.py", "lookup_via_keymap", "hash_key", "identity_key"))}</details>
<p>All code and the 14 table-driven tests: <code>_guides/code/gold_keys/</code>.</p>
</section>"""


def part_dims():
    return f"""
<section id="dim-kinds"><p class="eyebrow">5a. Kinds of dimension</p><h2>The kinds of dimension, with examples</h2>
<p>A dimension describes the who, what, where and when that numbers are sliced by. Most dimensions are plain lists (dealers, products). The other kinds solve one specific problem each. Learn the problem and the kind becomes obvious.</p>
{fig(d_dim_kinds(), "Twelve kinds. Green ones you will have in every mart; the others solve one problem each.")}
{vtable(["Kind", "What it is", "Tyre example", "Another business", "Verdict"], DIM_KINDS)}
<h3>Role-playing: one date table, many dates</h3>
<p>An order line has three dates. Do not build three date tables. Build one, and give the fact three keys into it, each read through a view named for its role.</p>
{fig(d_role(), "One dim_date, three roles.")}
<h3>Junk: a home for small flags</h3>
<p>Flags like "rush order" or "payment type" are too small for their own dimension, and too many to clutter every fact row. Put every combination in one small table and give the fact one key.</p>
{fig(d_junk(), "Three flags, eight combinations, one key on the fact.")}
<h3>Changing dimensions (SCD types)</h3>
<p>How each column keeps history is a choice per column. Type 1 (overwrite) and Type 2 (new version) are the two you will use most; the keys story above shows both. The full list of SCD types is in the table just above, under 5. Dimensions.</p>
</section>"""


def part_bridge():
    b, h = R["bridge"], R["hierarchy"]
    alloc = htable(["line_id", "rep", "weight", "revenue", "revenue shared"], [[a["line_id"], a["rep"], a["weight"], f"{a['revenue']:,.0f}", f"{a['revenue_allocated']:,.0f}"] for a in b["allocated"]], hl=[1, 2])
    compare = htable(["", "Asha", "Vik", "total", "true total"],
                     [["without a bridge", f"{b['naive_by_rep'][0]['revenue']:,.0f}", f"{b['naive_by_rep'][1]['revenue']:,.0f}", f"{b['naive_total']:,.0f}", f"{b['true_total']:,.0f}"],
                      ["with the bridge", f"{b['allocated_by_rep'][0]['revenue']:,.0f}", f"{b['allocated_by_rep'][1]['revenue']:,.0f}", f"{b['allocated_total']:,.0f}", f"{b['true_total']:,.0f}"]], hl=[1])
    roll = htable(["person", "revenue under them"], [[r["ancestor"], f"{r['revenue_under']:,.0f}"] for r in h["rollup"]])
    return f"""
<section id="bridge"><p class="eyebrow">5b. Bridge tables</p><h2>Bridge tables: why, and in which scenarios</h2>
<p>A fact row normally points at <b>one</b> member of each dimension: one dealer, one product, one date. A bridge is needed in exactly two situations:</p>
<ol><li><b>A fact row belongs to several members at once</b> (multi-valued). One order line sold jointly by two reps. One hospital stay with three diagnoses. One account with two holders.</li>
<li><b>Members sit in a tree of uneven depth</b> (hierarchy), and people ask "the total under X". An org chart, a chart of accounts, a bill of materials.</li></ol>
<h3>Scenario 1: one order line, two sales reps</h3>
<p>Order line L3 is worth 40,000 and was sold by Asha and Vik together, 60/40. Line L1 (50,000) was Asha's alone. The true total is 90,000.</p>
{fig(d_bridge(), "Joined straight on, a shared sale is counted once per rep. A bridge shares it out.")}
{compare}
<p>Without a bridge, the company "sold" {b['naive_total']:,.0f} instead of {b['true_total']:,.0f}, and Asha's commission is paid on money that was half Vik's. With the bridge, the fact stores one group key (G2), and the bridge lists the group's members with weights that add up to 1:</p>
{alloc}
<p>Not every question needs the weight. "How many lines did each rep work on?" counts lines, with no sharing: Asha {b['lines_touched_by_rep'][0]['lines']}, Vik {b['lines_touched_by_rep'][1]['lines']}. Counts may ignore weights; sums must use them.</p>
<h3>Scenario 2: the total under a manager</h3>
<p>The Head of Sales asks for revenue under each person, at every level. The tree has uneven depth in real companies, so fixed columns (region, area) do not work. A hierarchy bridge holds one row for each pair of a person and anyone below them (including themselves, at depth 0). "Total under X" is then one join and a sum:</p>
{fig(d_hier(), "One row per (above, below) pair.")}
{roll}
<h3>More scenarios, in other businesses</h3>{C.table(["Scenario", "Kind", "Question it answers", "Bridge"], BRIDGE_WHEN)}
<h3>When you do NOT need a bridge</h3>{vtable(["Situation", "Do this instead", "Verdict"], BRIDGE_NOT)}
<h3>Rules for bridges</h3>{C.table(["Rule", "Why"], BRIDGE_RULES)}
<details class="code"><summary>The bridge functions, as tested (bridge.py)</summary>{C.code(src("bridge.py", "naive_join", "weights_ok", "allocate", "rollup_hierarchy"))}</details>
</section>"""


TOC = [("keys-zero", "2a. Keys from zero: one dealer, one story"), ("dim-kinds", "5a. Kinds of dimension, with examples"), ("bridge", "5b. Bridge tables: why and when")]

QA_EXTRA = [
    ("If a surrogate key changes, do I have to update the fact table?", "A surrogate key should never change: it is assigned once per dimension version and stored. When a dimension changes, a Type 1 fix edits the row and a Type 2 change adds a new row with a new key; existing facts keep the key they stored, so no fact is rewritten. Facts are rewritten only for their own reasons: late data, corrections, or re-keying rows stored with the unknown key."),
    ("What is the difference between a business key, a durable key and a surrogate key?", "The business key is the source's own code (D7) and can change or differ between systems. The durable key is one number per real thing, given once by a key map, that never changes. The surrogate key is one number per dimension row, so with SCD Type 2 each version gets its own. Facts store the surrogate key for 'as it was' and can also store the durable key for 'as it is today'."),
    ("What is the primary key of a fact table?", "Its grain: the columns that make one row unique, such as the order line id, or warehouse plus product plus date for a daily stock snapshot. It is not a dimension's surrogate key, because many fact rows share one dimension member."),
    ("How do you generate surrogate keys in a data lakehouse?", "Keep a key map: the first time a version is seen it gets the next integer, the pair is stored, and later runs look it up. Hashing the business key with the version date needs no table but changes when the business key changes. Never number rows at build time: a rebuild renumbers them and old facts point at the wrong members."),
    ("What are the types of dimensions?", "Conformed, date, role-playing, changing (SCD types), degenerate, junk, mini-dimension, outrigger, shrunken, hierarchy, multi-valued, and reference or audit dimensions. Most marts use conformed, date and role-playing ones; the others each solve one specific problem."),
    ("When do you need a bridge table?", "When one fact row belongs to several members of a dimension, such as an order line sold by two reps or a hospital stay with several diagnoses, and when members sit in an uneven hierarchy such as an org chart. The bridge lists each group's members with weights that add up to 1, so totals stay right."),
]
