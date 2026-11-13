"""The tiny tyre company used on /learn/silver-to-gold/. Silver as it stands before each nightly run."""
from datetime import date

D = date
OPEN = D(9999, 12, 31)

LINES_S = "line_id string, order_id string, dealer_id string, product string, qty_ordered int, promised_date date, _seq long"
DELS_S = "delivery_id string, line_id string, warehouse string, qty int, delivered_date date, _seq long"
DEALERS_S = "dealer_id string, name string, region string, valid_from date, valid_to date, _seq long"
FILES_S = "warehouse string, file_date date"

# run r0 (night of 5 Nov): one old line, already built before our story starts
LINES_R0 = [("L0", "O0", "D1", "R15", 3, D(2026, 11, 5), 1001)]
DELS_R0 = [("X0", "L0", "WH-A", 3, D(2026, 11, 5), 2101)]

# run r1 (night of 13 Nov): six new order lines and five deliveries arrived in silver
LINES_R1 = LINES_R0 + [
    ("L1", "O1", "D1", "R15", 10, D(2026, 11, 10), 1041),
    ("L2", "O1", "D1", "R16", 5, D(2026, 11, 10), 1042),
    ("L3", "O2", "D7", "R15", 8, D(2026, 11, 11), 1043),
    ("L4", "O3", "D7", "R17", 4, D(2026, 11, 13), 1044),
    ("L5", "O4", "D9", "R15", 6, D(2026, 11, 13), 1045),
    ("L6", "O5", "TEST01", "R15", 1, D(2026, 11, 13), 1046),
]
DELS_R1 = DELS_R0 + [
    ("X1", "L1", "WH-A", 10, D(2026, 11, 10), 2201),
    ("X2", "L2", "WH-A", 5, D(2026, 11, 11), 2202),
    ("X3", "L3", "WH-B", 6, D(2026, 11, 11), 2203),
    ("X4", "L4", "WH-A", 4, D(2026, 11, 13), 2204),
    ("X5", "L5", "WH-A", 6, D(2026, 11, 13), 2205),
]
# run r2 (night of 15 Nov): the last 2 tyres of L3 arrive on 14 Nov
LINES_R2 = LINES_R1
DELS_R2 = DELS_R1 + [("X6", "L3", "WH-B", 2, D(2026, 11, 14), 2206)]

DEALERS_R1 = [
    ("D1", "Sharma Tyres", "North", D(2024, 1, 1), OPEN, 501),
    ("D7", "Patel Motors", "North", D(2024, 3, 1), D(2026, 11, 12), 502),   # moved region on 12 Nov
    ("D7", "Patel Motors", "West", D(2026, 11, 12), OPEN, 503),
]
DEALERS_R2 = DEALERS_R1 + [("D9", "Kumar Wheels", "South", D(2026, 11, 1), OPEN, 504)]   # arrives late

# daily delivery files: both warehouses owe one per day
FILES_R0 = [("WH-A", D(2026, 11, 5)), ("WH-B", D(2026, 11, 5))]
FILES_R1 = FILES_R0 + [(w, D(2026, 11, d)) for d in (10, 11) for w in ("WH-A", "WH-B")] + [("WH-A", D(2026, 11, 13))]
FILES_R2 = FILES_R1 + [("WH-B", D(2026, 11, 13))] + [(w, D(2026, 11, 14)) for w in ("WH-A", "WH-B")]

# for the other fact kinds
MOVES_S = "warehouse string, product string, move_date date, qty int"
MOVES = [("WH-A", "R15", D(2026, 11, 10), 100), ("WH-A", "R15", D(2026, 11, 10), -10),
         ("WH-A", "R15", D(2026, 11, 12), -6), ("WH-A", "R15", D(2026, 11, 13), 50)]
EVENTS_S = "line_id string, milestone string, at date"
EVENTS_DAY1 = [("L3", "ordered", D(2026, 11, 8)), ("L3", "shipped", D(2026, 11, 10))]
EVENTS_DAY2 = [("L3", "delivered", D(2026, 11, 14))]
EVENTS_DAY3 = [("L3", "invoiced", D(2026, 11, 16))]
VISITS_S = "rep_id string, dealer_id string, visit_date date"
VISITS = [("R-Asha", "D1", D(2026, 11, 10)), ("R-Asha", "D1", D(2026, 11, 10)), ("R-Vik", "D7", D(2026, 11, 11))]
PLAN_S = "dealer_id string, month string, plan_qty int"
PLAN = [("D1", "2026-11", 20), ("D7", "2026-11", 10), ("D9", "2026-11", 5)]
