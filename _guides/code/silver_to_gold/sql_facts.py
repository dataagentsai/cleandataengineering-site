"""Fact examples in SQL for /learn/silver-to-gold/fact-examples/. Same shape as sql_dimensions.py.

One DuckDB connection runs the whole list in order, so later examples can read earlier gold tables
(the aggregate and consolidated examples read fact_order_line from the first example).
"""

EXAMPLES = [
    # ------------------------------------------------------------------------------------------ Transaction
    dict(
        id="f-transaction", short="Transaction", kind="Transaction fact",
        title="Transaction fact: one row per order line, with an on-time-in-full flag",
        question="Did each order line arrive on time and in full? And how many tyres did we promise by region?",
        grain="One row per order line.",
        plain="The workhorse. Something happened once (a line was ordered), so it gets one row, with the numbers that belong to it. "
              "Here the rule is: a line is OTIF when everything ordered was delivered, and the last delivery was on or before the promised date.",
        sources=[("silver_order_lines", """
CREATE TABLE silver_order_lines (line_id VARCHAR, order_id VARCHAR, dealer_id VARCHAR, product_id VARCHAR,
                                 qty_ordered INTEGER, unit_price INTEGER, promised_date DATE);
INSERT INTO silver_order_lines VALUES
  ('L1','O1','D1',    'P1',10,100,DATE '2026-11-10'),
  ('L2','O1','D1',    'P2', 5, 80,DATE '2026-11-10'),
  ('L3','O2','D7',    'P1', 8,100,DATE '2026-11-11'),
  ('L4','O2','D7',    'P3', 4,150,DATE '2026-11-13'),
  ('L5','O3','D9',    'P2', 6, 80,DATE '2026-11-13'),
  ('L6','O4','TEST01','P1', 1,100,DATE '2026-11-13');   -- a test dealer: never reaches gold
"""), ("silver_deliveries", """
CREATE TABLE silver_deliveries (delivery_id VARCHAR, line_id VARCHAR, warehouse VARCHAR, qty INTEGER, delivered_date DATE);
INSERT INTO silver_deliveries VALUES
  ('X1', 'L1','WH-A',10,DATE '2026-11-10'),
  ('X2', 'L2','WH-A', 5,DATE '2026-11-11'),   -- a day late
  ('X3', 'L3','WH-B', 6,DATE '2026-11-11'),   -- L3 comes in two deliveries
  ('X3b','L3','WH-B', 2,DATE '2026-11-12'),
  ('X4', 'L4','WH-A', 4,DATE '2026-11-13'),
  ('X5', 'L5','WH-A', 6,DATE '2026-11-13');
"""), ("dim_dealer", """
CREATE TABLE dim_dealer (dealer_key INTEGER, dealer_id VARCHAR, name VARCHAR, region VARCHAR, valid_from DATE, valid_to DATE);
INSERT INTO dim_dealer VALUES
  (-1,'?', 'Unknown',      'Unknown',DATE '1900-01-01',DATE '9999-12-31'),
  ( 1,'D1','Sharma Tyres', 'North',  DATE '2026-11-01',DATE '9999-12-31'),
  ( 2,'D7','Patel Motors', 'North',  DATE '2026-11-01',DATE '2026-11-12'),
  ( 3,'D7','Patel Motors', 'West',   DATE '2026-11-12',DATE '9999-12-31');
""")],
        steps=[
            dict(cap="The build. Add the child rows (deliveries) up to one row per line first, then join. Then look up the dealer version true on the promised date, with -1 for a dealer silver has not got yet.",
                 sql="""CREATE TABLE fact_order_line AS
WITH delivered AS (                       -- one row per line, BEFORE joining
  SELECT line_id, sum(qty) AS qty_delivered, max(delivered_date) AS last_delivered
  FROM silver_deliveries GROUP BY line_id)
SELECT o.line_id,
       o.order_id,                                            -- degenerate dimension
       COALESCE(d.dealer_key, -1)                AS dealer_key,
       CAST(strftime(o.promised_date, '%Y%m%d') AS INTEGER) AS promised_date_key,
       o.qty_ordered,
       COALESCE(x.qty_delivered, 0)              AS qty_delivered,
       o.qty_ordered * o.unit_price              AS line_amount,
       COALESCE(x.qty_delivered, 0) >= o.qty_ordered
         AND x.last_delivered <= o.promised_date AS is_otif
FROM silver_order_lines o
LEFT JOIN delivered x ON x.line_id = o.line_id
LEFT JOIN dim_dealer d
  ON d.dealer_id = o.dealer_id
 AND o.promised_date >= d.valid_from AND o.promised_date < d.valid_to
WHERE o.dealer_id NOT LIKE 'TEST%';""",
                 show="SELECT * FROM fact_order_line ORDER BY line_id"),
            dict(cap="Check the grain: one row per line. This must return no rows.",
                 sql="""SELECT line_id, count(*) AS n
FROM fact_order_line GROUP BY line_id HAVING count(*) > 1;""",
                 show="SELECT line_id, count(*) AS n FROM fact_order_line GROUP BY line_id HAVING count(*) > 1"),
            dict(cap="The trap, on purpose: join the deliveries straight in. L3 has two deliveries, so it appears twice and its 8 tyres are counted as 16.",
                 sql="""SELECT sum(o.qty_ordered) AS tyres_ordered_WRONG
FROM silver_order_lines o
LEFT JOIN silver_deliveries x ON x.line_id = o.line_id
WHERE o.dealer_id NOT LIKE 'TEST%';""",
                 show="""SELECT sum(o.qty_ordered) AS tyres_ordered_WRONG, (SELECT sum(qty_ordered) FROM fact_order_line) AS tyres_ordered_RIGHT
FROM silver_order_lines o LEFT JOIN silver_deliveries x ON x.line_id = o.line_id WHERE o.dealer_id NOT LIKE 'TEST%'"""),
        ],
        checks=[("five lines, the test dealer excluded", "SELECT count(*) FROM fact_order_line", 5),
                ("three lines were OTIF", "SELECT count(*) FROM fact_order_line WHERE is_otif", 3),
                ("L3 was in full but late", "SELECT qty_delivered = qty_ordered AND NOT is_otif FROM fact_order_line WHERE line_id='L3'", True),
                ("L3 joined to the North version of D7", "SELECT dealer_key FROM fact_order_line WHERE line_id='L3'", 2),
                ("L4 joined to the West version", "SELECT dealer_key FROM fact_order_line WHERE line_id='L4'", 3),
                ("L5 has the unknown dealer", "SELECT dealer_key FROM fact_order_line WHERE line_id='L5'", -1),
                ("the naive join double counts", "SELECT sum(o.qty_ordered) FROM silver_order_lines o LEFT JOIN silver_deliveries x ON x.line_id=o.line_id WHERE o.dealer_id NOT LIKE 'TEST%'", 41),
                ("the real total", "SELECT sum(qty_ordered) FROM fact_order_line", 33)],
        when="Almost always. If you are unsure which kind a fact is, start here.",
        trap="Joining child rows without adding them up first. And looking up the dealer's current row instead of the row true on the date.",
    ),
    # ------------------------------------------------------------------------------------------ Periodic snapshot
    dict(
        id="f-periodic", short="Periodic snapshot", kind="Periodic snapshot",
        title="Periodic snapshot: stock level per warehouse, per product, per day",
        question="How many tyres did each warehouse hold at the end of each day, including quiet days when nothing moved?",
        grain="One row per warehouse, per product, per day, from the first day it had stock.",
        plain="Stock is a level, not an event. Nothing 'happens' on a quiet day, but the question 'how much on Wednesday?' still has an answer. "
              "So we write a row for every day, carrying the level forward.",
        sources=[("silver_stock_movements", """
CREATE TABLE silver_stock_movements (warehouse VARCHAR, product_id VARCHAR, movement_date DATE, qty_change INTEGER);
INSERT INTO silver_stock_movements VALUES
  ('WH-A','P1',DATE '2026-11-10', 100),   -- received
  ('WH-A','P1',DATE '2026-11-12', -30),   -- dispatched
  ('WH-A','P2',DATE '2026-11-10',  50),
  ('WH-A','P2',DATE '2026-11-13', -20),
  ('WH-B','P1',DATE '2026-11-11',  60);
""")],
        steps=[
            dict(cap="Build a row for every day from each pair's first movement, then add up movements to date. Days with no movement get net 0 and keep the level. (In Spark or Databricks, replace the day generator with explode(sequence(...)).)",
                 sql="""CREATE TABLE fact_stock_daily AS
WITH pairs AS (
  SELECT warehouse, product_id, min(movement_date) AS first_day
  FROM silver_stock_movements GROUP BY warehouse, product_id),
days AS (
  SELECT CAST(unnest(generate_series(DATE '2026-11-10', DATE '2026-11-14', INTERVAL 1 DAY)) AS DATE) AS day),
spine AS (
  SELECT p.warehouse, p.product_id, d.day
  FROM pairs p JOIN days d ON d.day >= p.first_day),
moved AS (
  SELECT warehouse, product_id, movement_date AS day, sum(qty_change) AS net
  FROM silver_stock_movements GROUP BY warehouse, product_id, movement_date)
SELECT s.warehouse, s.product_id, s.day,
       COALESCE(m.net, 0) AS net_movement,
       sum(COALESCE(m.net, 0)) OVER (PARTITION BY s.warehouse, s.product_id
                                     ORDER BY s.day) AS closing_qty
FROM spine s
LEFT JOIN moved m USING (warehouse, product_id, day);""",
                 show="SELECT * FROM fact_stock_daily ORDER BY warehouse, product_id, day"),
            dict(cap="What you may add up. Across warehouses on one day: fine. Across days: never. Compare the three answers for product P1.",
                 sql="""SELECT
  (SELECT sum(closing_qty) FROM fact_stock_daily
    WHERE product_id = 'P1' AND day = DATE '2026-11-14')                AS right_latest_day_all_warehouses,
  (SELECT sum(closing_qty) FROM fact_stock_daily WHERE product_id = 'P1') AS wrong_added_over_days,
  (SELECT round(avg(t), 1) FROM (SELECT day, sum(closing_qty) AS t
     FROM fact_stock_daily WHERE product_id = 'P1' GROUP BY day))        AS right_average_stock;""",
                 show="""SELECT
  (SELECT sum(closing_qty) FROM fact_stock_daily WHERE product_id = 'P1' AND day = DATE '2026-11-14') AS right_latest_day_all_warehouses,
  (SELECT sum(closing_qty) FROM fact_stock_daily WHERE product_id = 'P1') AS wrong_added_over_days,
  (SELECT round(avg(t), 1) FROM (SELECT day, sum(closing_qty) AS t FROM fact_stock_daily WHERE product_id = 'P1' GROUP BY day)) AS right_average_stock"""),
        ],
        checks=[("every pair has a row for every day from its first movement", "SELECT count(*) FROM fact_stock_daily", 14),
                ("a quiet day keeps the level: WH-A P1 on 11 Nov", "SELECT closing_qty FROM fact_stock_daily WHERE warehouse='WH-A' AND product_id='P1' AND day=DATE '2026-11-11'", 100),
                ("end of 14 Nov, P1, both warehouses", "SELECT sum(closing_qty) FROM fact_stock_daily WHERE product_id='P1' AND day=DATE '2026-11-14'", 130),
                ("adding over days overstates stock", "SELECT sum(closing_qty) FROM fact_stock_daily WHERE product_id='P1'", 650)],
        when="Levels and balances: stock, bank balance, headcount, open orders at the end of each day.",
        trap="Never add a level across days: 100 on Monday plus 100 on Tuesday is not 200 tyres. Add across warehouses, then take the last day or the average over days. "
             "And a day before the first movement should show 0 or no row by design, not a surprise gap.",
    ),
    # ------------------------------------------------------------------------------------------ Accumulating
    dict(
        id="f-accumulating", short="Accumulating snapshot", kind="Accumulating snapshot",
        title="Accumulating snapshot: one row per order line, filled in as it moves",
        question="How many days does a line take from order to shipment, and which lines are still open?",
        grain="One row per order line, for its whole life.",
        plain="A line goes through steps: ordered, picked, shipped, delivered. Instead of four rows, there is one row with four date columns. "
              "Empty at first, filled in as each step happens. This is the one fact kind whose rows change after they are written.",
        sources=[("silver_line_events", """
CREATE TABLE silver_line_events (line_id VARCHAR, event VARCHAR, event_date DATE);
INSERT INTO silver_line_events VALUES
  ('L1','ordered',  DATE '2026-11-08'), ('L1','picked',   DATE '2026-11-09'),
  ('L1','shipped',  DATE '2026-11-09'), ('L1','delivered',DATE '2026-11-10'),
  ('L2','ordered',  DATE '2026-11-08'), ('L2','picked',   DATE '2026-11-09'), ('L2','shipped', DATE '2026-11-10'),
  ('L3','ordered',  DATE '2026-11-09'), ('L3','picked',   DATE '2026-11-10');
""")],
        steps=[
            dict(cap="The processor, as a view: turn milestone events into one row per line. It is pure: events in, rows out.",
                 sql="""CREATE VIEW v_line_pipeline AS
SELECT line_id,
       max(CASE WHEN event = 'ordered'   THEN event_date END) AS ordered_date,
       max(CASE WHEN event = 'picked'    THEN event_date END) AS picked_date,
       max(CASE WHEN event = 'shipped'   THEN event_date END) AS shipped_date,
       max(CASE WHEN event = 'delivered' THEN event_date END) AS delivered_date
FROM silver_line_events GROUP BY line_id;""", show=None),
            dict(cap="Night 1: build the table, with the measures worked out from the dates. Empty steps stay empty. An 'is_open' flag stops open lines hiding inside averages.",
                 sql="""CREATE TABLE fact_line_pipeline AS
SELECT line_id, ordered_date, picked_date, shipped_date, delivered_date,
       date_diff('day', ordered_date, shipped_date)  AS days_order_to_ship,
       delivered_date IS NULL                        AS is_open
FROM v_line_pipeline;""",
                 show="SELECT * FROM fact_line_pipeline ORDER BY line_id"),
            dict(cap="Night 2: new events arrive. L2 is delivered, L3 ships, and a new line L4 is ordered.",
                 sql="""INSERT INTO silver_line_events VALUES
  ('L2','delivered',DATE '2026-11-11'), ('L3','shipped',DATE '2026-11-11'), ('L4','ordered',DATE '2026-11-11');""",
                 show=None),
            dict(cap="Night 2, the writer: MERGE by line. Rows that exist are updated, new lines are inserted. Run it twice and nothing changes.",
                 sql="""MERGE INTO fact_line_pipeline t
USING (SELECT line_id, ordered_date, picked_date, shipped_date, delivered_date,
              date_diff('day', ordered_date, shipped_date) AS days_order_to_ship,
              delivered_date IS NULL                       AS is_open
       FROM v_line_pipeline) s
ON t.line_id = s.line_id
WHEN MATCHED THEN UPDATE SET
     ordered_date = s.ordered_date, picked_date = s.picked_date,
     shipped_date = s.shipped_date, delivered_date = s.delivered_date,
     days_order_to_ship = s.days_order_to_ship, is_open = s.is_open
WHEN NOT MATCHED THEN INSERT VALUES
     (s.line_id, s.ordered_date, s.picked_date, s.shipped_date, s.delivered_date,
      s.days_order_to_ship, s.is_open);""",
                 show="SELECT * FROM fact_line_pipeline ORDER BY line_id"),
            dict(cap="The question: average days to ship, and how many lines are still open. Open lines are counted, never averaged away.",
                 sql="""SELECT round(avg(days_order_to_ship), 2) AS avg_days_to_ship,
       count(*) FILTER (WHERE is_open)   AS open_lines,
       count(*)                          AS all_lines
FROM fact_line_pipeline;""",
                 show="""SELECT round(avg(days_order_to_ship), 2) AS avg_days_to_ship, count(*) FILTER (WHERE is_open) AS open_lines, count(*) AS all_lines
FROM fact_line_pipeline"""),
        ],
        checks=[("four lines after night 2", "SELECT count(*) FROM fact_line_pipeline", 4),
                ("L2 now delivered", "SELECT delivered_date FROM fact_line_pipeline WHERE line_id='L2'", "2026-11-11"),
                ("L1 was not blanked by the update", "SELECT delivered_date FROM fact_line_pipeline WHERE line_id='L1'", "2026-11-10"),
                ("two lines still open: L3 and the new L4", "SELECT count(*) FROM fact_line_pipeline WHERE is_open", 2),
                ("L3 shipped after two days", "SELECT days_order_to_ship FROM fact_line_pipeline WHERE line_id='L3'", 2)],
        when="Anything with a start, several steps and an end: orders, loan applications, claims, support tickets.",
        trap="Every update is effectively a restatement, so log changes you have already published. And a line that never reaches the last step needs the open flag, or an average hides it.",
    ),
    # ------------------------------------------------------------------------------------------ Factless event
    dict(
        id="f-factless", short="Factless", kind="Factless fact",
        title="Factless fact: visits (an event) and promo coverage (what could have happened)",
        question="How many times did our reps visit each dealer? And which dealers were offered the November promo but never ordered?",
        grain="Visits: one row per visit. Coverage: one row per promo per eligible dealer.",
        plain="Some facts have nothing to add up. A rep visited a dealer: that is the whole fact. You count rows. "
              "A second kind records what was possible (who was offered a promo) so you can later ask what did not happen.",
        sources=[("silver_rep_visits", """
CREATE TABLE silver_rep_visits (visit_id VARCHAR, dealer_id VARCHAR, rep VARCHAR, visit_date DATE);
INSERT INTO silver_rep_visits VALUES
  ('V1','D1','Asha',DATE '2026-11-03'), ('V2','D1','Asha',DATE '2026-11-10'),
  ('V3','D7','Ravi',DATE '2026-11-04');
"""), ("dim_dealer_names", """
CREATE TABLE dim_dealer_names (dealer_id VARCHAR, name VARCHAR);
INSERT INTO dim_dealer_names VALUES ('D1','Sharma Tyres'),('D7','Patel Motors'),('D11','Khan Auto'),('D12','Rao Wheels');
"""), ("silver_promo_offers", """
CREATE TABLE silver_promo_offers (promo_id VARCHAR, dealer_id VARCHAR, start_date DATE, end_date DATE);
INSERT INTO silver_promo_offers VALUES
  ('NOV-DEAL','D1', DATE '2026-11-10', DATE '2026-11-14'),
  ('NOV-DEAL','D7', DATE '2026-11-10', DATE '2026-11-14'),
  ('NOV-DEAL','D11',DATE '2026-11-10', DATE '2026-11-14'),
  ('NOV-DEAL','D12',DATE '2026-11-10', DATE '2026-11-14');
""")],
        steps=[
            dict(cap="The event fact has keys and no numbers. One row per visit.",
                 sql="""CREATE TABLE fact_dealer_visit AS
SELECT DISTINCT visit_id, dealer_id, rep, visit_date      -- DISTINCT: a re-sent visit is still one visit
FROM silver_rep_visits;""",
                 show="SELECT * FROM fact_dealer_visit ORDER BY visit_id"),
            dict(cap="Count the rows. Start from the dimension so dealers with no visits show 0 (a fact alone cannot show them).",
                 sql="""SELECT d.name, count(v.visit_id) AS visits
FROM dim_dealer_names d
LEFT JOIN fact_dealer_visit v USING (dealer_id)
GROUP BY d.name ORDER BY visits DESC, d.name;""",
                 show="""SELECT d.name, count(v.visit_id) AS visits
FROM dim_dealer_names d LEFT JOIN fact_dealer_visit v USING (dealer_id)
GROUP BY d.name ORDER BY visits DESC, d.name"""),
            dict(cap="The coverage fact is silver_promo_offers: who was offered the promo. The question 'who did not order?' is an anti-join between coverage and what happened (orders in the promo window, from the transaction fact).",
                 sql="""SELECT p.promo_id, p.dealer_id, n.name
FROM silver_promo_offers p
JOIN dim_dealer_names n USING (dealer_id)
WHERE NOT EXISTS (
  SELECT 1 FROM silver_order_lines o
  WHERE o.dealer_id = p.dealer_id
    AND o.promised_date BETWEEN p.start_date AND p.end_date)
ORDER BY p.dealer_id;""",
                 show="""SELECT p.promo_id, p.dealer_id, n.name
FROM silver_promo_offers p JOIN dim_dealer_names n USING (dealer_id)
WHERE NOT EXISTS (SELECT 1 FROM silver_order_lines o WHERE o.dealer_id = p.dealer_id AND o.promised_date BETWEEN p.start_date AND p.end_date)
ORDER BY p.dealer_id"""),
        ],
        checks=[("three visits", "SELECT count(*) FROM fact_dealer_visit", 3),
                ("a dealer with no visits still shows 0", "SELECT count(v.visit_id) FROM dim_dealer_names d LEFT JOIN fact_dealer_visit v USING (dealer_id) WHERE d.dealer_id='D11'", 0),
                ("two dealers were offered the promo but never ordered", """SELECT count(*) FROM silver_promo_offers p WHERE NOT EXISTS (
                   SELECT 1 FROM silver_order_lines o WHERE o.dealer_id=p.dealer_id AND o.promised_date BETWEEN p.start_date AND p.end_date)""", 2)],
        when="Attendance, visits, logins, eligibility, enrolment: events with nothing to measure, and 'who did not' questions.",
        trap="'What did NOT happen' cannot be read from the events alone. Keep a coverage fact (who was in scope) or compare with the full dimension.",
    ),
    # ------------------------------------------------------------------------------------------ Aggregate
    dict(
        id="f-aggregate", short="Aggregate", kind="Aggregate fact",
        title="Aggregate fact: OTIF by region and day, built from the fact above",
        question="Show OTIF by region on a dashboard that must open instantly.",
        grain="One row per region per promised date.",
        plain="A summary of another gold fact, kept because a busy dashboard asks the same question all day. "
              "Built from the transaction fact, never from silver, so the two always agree. Store the counts, not just the percent.",
        sources=[], note="Reads fact_order_line and dim_dealer, built in the first example.",
        steps=[
            dict(cap="Group the transaction fact. Keep lines and otif_lines as counts.",
                 sql="""CREATE TABLE fact_otif_region_day AS
SELECT d.region,
       CAST(strptime(CAST(f.promised_date_key AS VARCHAR), '%Y%m%d') AS DATE) AS promised_date,
       count(*)                                  AS lines,
       sum(CASE WHEN f.is_otif THEN 1 ELSE 0 END) AS otif_lines,
       sum(f.qty_ordered)                        AS qty_ordered
FROM fact_order_line f
JOIN dim_dealer d USING (dealer_key)
GROUP BY d.region, f.promised_date_key;""",
                 show="SELECT *, round(100.0 * otif_lines / lines, 1) AS otif_pct FROM fact_otif_region_day ORDER BY region, promised_date"),
            dict(cap="Roll up to region. The percent of percents is wrong; the sum of counts is right.",
                 sql="""SELECT region,
       round(avg(100.0 * otif_lines / lines), 1)       AS wrong_avg_of_percents,
       round(100.0 * sum(otif_lines) / sum(lines), 1)  AS right_percent_from_counts
FROM fact_otif_region_day
GROUP BY region ORDER BY region;""",
                 show="""SELECT region, round(avg(100.0 * otif_lines / lines), 1) AS wrong_avg_of_percents,
       round(100.0 * sum(otif_lines) / sum(lines), 1) AS right_percent_from_counts
FROM fact_otif_region_day GROUP BY region ORDER BY region"""),
        ],
        checks=[("the aggregate loses no lines", "SELECT sum(lines) FROM fact_otif_region_day", 5),
                ("North really did 1 in 3", "SELECT round(100.0 * sum(otif_lines) / sum(lines), 1) FROM fact_otif_region_day WHERE region='North'", 33.3),
                ("averaging the daily percents gives 25", "SELECT round(avg(100.0 * otif_lines / lines), 1) FROM fact_otif_region_day WHERE region='North'", 25.0)],
        when="A question that is slow and asked all the time, over a fact that is big.",
        trap="Percents cannot be added or averaged across days or regions: keep the counts. And a summary nobody reads is pure cost: drop it.",
    ),
    # ------------------------------------------------------------------------------------------ Consolidated
    dict(
        id="f-consolidated", short="Consolidated", kind="Consolidated fact",
        title="Consolidated fact: plan next to actual, at one shared grain",
        question="Per region and month: what did we plan, what did we deliver, and what is the gap?",
        grain="One row per region per month.",
        plain="Plan comes from finance, actuals from our own fact. They arrive at different grains. "
              "Bring both to region and month first, then put them side by side with a FULL OUTER JOIN, so a region with only a plan, or only actuals, still shows.",
        note="Reads fact_order_line and dim_dealer from the first example, and finance's plan below.",
        sources=[("silver_sales_plan", """
CREATE TABLE silver_sales_plan (region VARCHAR, month VARCHAR, planned_qty INTEGER);
INSERT INTO silver_sales_plan VALUES ('North','2026-11',100), ('West','2026-11',60), ('South','2026-11',40);
""")],
        steps=[
            dict(cap="Two inputs brought to the same grain, then combined. COALESCE turns a missing side into 0 and gap shows what is missing.",
                 sql="""CREATE TABLE fact_plan_vs_actual AS
WITH actual AS (
  SELECT d.region,
         strftime(CAST(strptime(CAST(f.promised_date_key AS VARCHAR), '%Y%m%d') AS DATE), '%Y-%m') AS month,
         sum(f.qty_ordered) AS actual_qty
  FROM fact_order_line f JOIN dim_dealer d USING (dealer_key)
  GROUP BY 1, 2)
SELECT COALESCE(p.region, a.region) AS region,
       COALESCE(p.month,  a.month)  AS month,
       COALESCE(p.planned_qty, 0)   AS planned_qty,
       COALESCE(a.actual_qty,  0)   AS actual_qty,
       COALESCE(a.actual_qty, 0) - COALESCE(p.planned_qty, 0) AS gap
FROM silver_sales_plan p
FULL OUTER JOIN actual a ON a.region = p.region AND a.month = p.month;""",
                 show="SELECT * FROM fact_plan_vs_actual ORDER BY region"),
        ],
        checks=[("South has a plan and no actuals", "SELECT actual_qty FROM fact_plan_vs_actual WHERE region='South'", 0),
                ("Unknown region has actuals and no plan", "SELECT planned_qty FROM fact_plan_vs_actual WHERE region='Unknown'", 0),
                ("actuals add up to the transaction fact", "SELECT sum(actual_qty) FROM fact_plan_vs_actual", 33),
                ("plan adds up to finance's total", "SELECT sum(planned_qty) FROM fact_plan_vs_actual", 200)],
        when="Plan against actual, budget against spend, forecast against outcome: any comparison of two sources.",
        trap="An INNER or LEFT join silently drops the region that exists on only one side, which is exactly the row someone must look at. Use FULL OUTER JOIN, and reconcile both totals to their sources.",
    ),
    # ------------------------------------------------------------------------------------------ Allocation
    dict(
        id="f-allocation", short="Allocated header amount", kind="Transaction fact with allocation",
        title="Spreading an order-level amount (freight) over its lines",
        question="Freight is charged per order, but profit is reported per product. How is it shared out without a cent going missing?",
        grain="One row per order line, with its share of the order's freight.",
        plain="The amount belongs to the order (the header), but the fact is at line level. Share it in proportion to line value. "
              "Naive rounding loses or invents cents, so the share is worked out on a running total and each line gets the difference.",
        sources=[("silver_alloc_lines", """
CREATE TABLE silver_alloc_lines (order_id VARCHAR, line_id VARCHAR, line_amount DECIMAL(12,2));
INSERT INTO silver_alloc_lines VALUES
  ('A1','A1-1',100.00), ('A1','A1-2',100.00), ('A1','A1-3',100.00),
  ('B1','B1-1',1000.00), ('B1','B1-2', 400.00);
"""), ("silver_order_freight", """
CREATE TABLE silver_order_freight (order_id VARCHAR, freight DECIMAL(12,2));
INSERT INTO silver_order_freight VALUES ('A1',100.00), ('B1',90.00);
""")],
        steps=[
            dict(cap="The wrong way: round each line's share. Three equal lines each get 33.33, and 100.00 becomes 99.99.",
                 sql="""SELECT order_id, freight, sum(share) AS allocated_naive
FROM (SELECT l.order_id, f.freight,
             round(f.freight * l.line_amount / sum(l.line_amount) OVER (PARTITION BY l.order_id), 2) AS share
      FROM silver_alloc_lines l JOIN silver_order_freight f USING (order_id))
GROUP BY order_id, freight ORDER BY order_id;""",
                 show="="),
            dict(cap="The right way: each line gets (rounded running share) minus (rounded running share of the line before it). The pieces add up to exactly the freight.",
                 sql="""CREATE TABLE fact_line_freight AS
WITH running AS (
  SELECT l.order_id, l.line_id, l.line_amount, f.freight,
         sum(l.line_amount) OVER (PARTITION BY l.order_id ORDER BY l.line_id) AS cum_amount,
         sum(l.line_amount) OVER (PARTITION BY l.order_id)                   AS total_amount
  FROM silver_alloc_lines l JOIN silver_order_freight f USING (order_id)),
shares AS (
  SELECT *, round(freight * cum_amount / total_amount, 2) AS cum_share FROM running)
SELECT order_id, line_id, line_amount,
       cum_share - COALESCE(lag(cum_share) OVER (PARTITION BY order_id ORDER BY line_id), 0) AS freight_share
FROM shares;""",
                 show="SELECT * FROM fact_line_freight ORDER BY order_id, line_id"),
            dict(cap="The check every allocation needs: the shares add back to the header, order by order. This returns no rows when it is right.",
                 sql="""SELECT f.order_id, f.freight, sum(a.freight_share) AS allocated
FROM silver_order_freight f JOIN fact_line_freight a USING (order_id)
GROUP BY f.order_id, f.freight
HAVING sum(a.freight_share) <> f.freight;""",
                 show="""SELECT f.order_id, f.freight, sum(a.freight_share) AS allocated
FROM silver_order_freight f JOIN fact_line_freight a USING (order_id)
GROUP BY f.order_id, f.freight HAVING sum(a.freight_share) <> f.freight"""),
        ],
        checks=[("A1 shares add up to exactly 100", "SELECT sum(freight_share) FROM fact_line_freight WHERE order_id='A1'", 100.00),
                ("B1 shares add up to exactly 90", "SELECT sum(freight_share) FROM fact_line_freight WHERE order_id='B1'", 90.00),
                ("the naive way lost a cent on A1", "SELECT sum(round(100.00 * line_amount / 300.00, 2)) FROM silver_alloc_lines WHERE order_id='A1'", 99.99)],
        when="Freight, discounts, taxes and fees recorded per order or invoice but analysed per line, product or customer.",
        trap="Choose the share rule (by value, by quantity, equally) once, with the business, and write it down. Changing the rule later restates history.",
    ),
    # ------------------------------------------------------------------------------------------ Adjustments
    dict(
        id="f-adjustment", short="Adjustment rows", kind="Fact with adjustment rows",
        title="Adjustment rows: corrections as new rows, never edits",
        question="What is line L1 worth now, and what did we report for it on 15 November?",
        grain="One row per amount entry (the original, then each correction).",
        plain="When a number is corrected, don't change the old row. Add a new row with the difference, dated by when it was recorded. "
              "Add them all up for today's truth; add up to a date for what was known then.",
        sources=[("silver_sales_entries", """
CREATE TABLE silver_sales_entries (entry_id VARCHAR, line_id VARCHAR, recorded_on DATE, amount INTEGER, reason VARCHAR);
INSERT INTO silver_sales_entries VALUES
  ('E1','L1',DATE '2026-11-10', 1000, 'original'),
  ('E2','L1',DATE '2026-11-20', -200, 'price corrected'),
  ('E3','L1',DATE '2026-11-22',   50, 'late surcharge'),
  ('E4','L2',DATE '2026-11-10',  400, 'original');
""")],
        steps=[
            dict(cap="The fact is the silver entries as they are: append-only, one row per entry.",
                 sql="""CREATE TABLE fact_sales_ledger AS
SELECT entry_id, line_id, recorded_on, amount, reason FROM silver_sales_entries;""",
                 show="SELECT * FROM fact_sales_ledger ORDER BY entry_id"),
            dict(cap="Today's truth, and what we knew on 15 November. Same table, one extra filter.",
                 sql="""SELECT line_id,
       sum(amount)                                                    AS amount_now,
       sum(amount) FILTER (WHERE recorded_on <= DATE '2026-11-15')   AS amount_reported_on_15_nov
FROM fact_sales_ledger GROUP BY line_id ORDER BY line_id;""",
                 show="""SELECT line_id, sum(amount) AS amount_now, sum(amount) FILTER (WHERE recorded_on <= DATE '2026-11-15') AS amount_reported_on_15_nov
FROM fact_sales_ledger GROUP BY line_id ORDER BY line_id"""),
        ],
        checks=[("L1 is worth 850 now", "SELECT sum(amount) FROM fact_sales_ledger WHERE line_id='L1'", 850),
                ("on 15 Nov we reported 1000", "SELECT sum(amount) FROM fact_sales_ledger WHERE line_id='L1' AND recorded_on <= DATE '2026-11-15'", 1000)],
        when="Finance-grade numbers where 'what did we say then?' is a real question and silently changed history is not acceptable.",
        trap="Counting entries is not counting sales: a correction row is not a new sale. Count lines from the line grain, and add up amounts from the ledger.",
    ),
]
