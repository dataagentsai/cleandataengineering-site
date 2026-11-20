"""Dimension examples in SQL for /learn/silver-to-gold/dimension-examples/.

Every example is data, not prose: small silver tables in, the SQL, the gold table out. run_sql.py executes them
in DuckDB (one connection for the page) and writes sql_results.json; the page generator only reads that file, so
every table on the page is a real result. test_sql_examples.py checks each example's `checks` (table-driven).

Dialect: DuckDB. The few places where Spark / Databricks SQL differs are listed on the page.
"""

DATE_DIM = """
CREATE TABLE dim_date AS
SELECT CAST(strftime(d, '%Y%m%d') AS INTEGER)                    AS date_key,
       d                                                          AS date,
       dayname(d)                                                 AS day_name,
       isodow(d) >= 6                                             AS is_weekend,
       strftime(d, '%Y-%m')                                       AS year_month,
       'FY' || (year(d) + CASE WHEN month(d) >= 4 THEN 0 ELSE -1 END)
            || '-' || right(CAST(year(d) + CASE WHEN month(d) >= 4 THEN 1 ELSE 0 END AS VARCHAR), 2) AS fiscal_year,
       'Q' || CAST(((month(d) + 8) % 12) // 3 + 1 AS INTEGER)       AS fiscal_quarter
FROM (SELECT CAST(unnest(generate_series(DATE '2026-04-01', DATE '2027-03-31', INTERVAL 1 DAY)) AS DATE) AS d);
"""

EXAMPLES = [
    # ------------------------------------------------------------------------------------------ Type 1
    dict(
        id="d-type1", short="Type 1: overwrite", kind="SCD Type 1",
        title="Type 1: overwrite the old value",
        question="What is this product called today? (Nobody needs to know what it was called last year.)",
        plain="The dimension keeps one row per product. When the source changes a name, the row is rewritten. "
              "The product keeps its key, so every old fact still points at it and now shows the new name.",
        sources=[("silver_products", """
CREATE TABLE silver_products (product_id VARCHAR, product_name VARCHAR, brand VARCHAR, size VARCHAR);
INSERT INTO silver_products VALUES
  ('P1','Highway Plus','Apex','205/55R16'),
  ('P2','City Grip','Apex','185/65R15'),
  ('P3','Trail King','Roadster','265/65R17');
"""), ("silver_products_day2", """
CREATE TABLE silver_products_day2 (product_id VARCHAR, product_name VARCHAR, brand VARCHAR, size VARCHAR);
INSERT INTO silver_products_day2 VALUES
  ('P1','Highway Plus','Apex','205/55R16'),
  ('P2','City Grip 2','Apex','185/65R15'),   -- renamed
  ('P3','Trail King','Roadster','265/65R17'),
  ('P4','Snow Master','Roadster','195/65R15'); -- new
""")],
        steps=[
            dict(cap="Night 1: build the dimension. The key is a number gold hands out; the source's own id stays as a column.",
                 sql="""CREATE TABLE dim_product AS
SELECT row_number() OVER (ORDER BY product_id) AS product_key,
       product_id, product_name, brand, size
FROM silver_products;""",
                 show="SELECT * FROM dim_product ORDER BY product_key"),
            dict(cap="Night 2, first half: rewrite rows whose attributes changed. The key does not move.",
                 sql="""UPDATE dim_product d
SET product_name = s.product_name, brand = s.brand, size = s.size
FROM silver_products_day2 s
WHERE d.product_id = s.product_id
  AND (d.product_name IS DISTINCT FROM s.product_name
    OR d.brand        IS DISTINCT FROM s.brand
    OR d.size         IS DISTINCT FROM s.size);""", show=None),
            dict(cap="Night 2, second half: add products gold has never seen, with the next free keys.",
                 sql="""INSERT INTO dim_product
SELECT (SELECT COALESCE(max(product_key), 0) FROM dim_product)
         + row_number() OVER (ORDER BY s.product_id),
       s.product_id, s.product_name, s.brand, s.size
FROM silver_products_day2 s
WHERE NOT EXISTS (SELECT 1 FROM dim_product d WHERE d.product_id = s.product_id);""",
                 show="SELECT * FROM dim_product ORDER BY product_key"),
        ],
        checks=[("P2 kept key 2 and got the new name", "SELECT product_name FROM dim_product WHERE product_key = 2", "City Grip 2"),
                ("P4 got the next key", "SELECT product_key FROM dim_product WHERE product_id = 'P4'", 4),
                ("one row per product", "SELECT count(*) - count(DISTINCT product_id) FROM dim_product", 0)],
        when="Names, descriptions and codes where a correction should show everywhere, and history has no business value.",
        trap="History is gone on purpose. If someone later asks 'what was it called when we sold it?', Type 1 cannot answer. "
             "Also never re-number: the key must stay the same on every run, or old facts point at the wrong product.",
    ),
    # ------------------------------------------------------------------------------------------ Type 2
    dict(
        id="d-type2", short="Type 2: keep history", kind="SCD Type 2",
        title="Type 2: keep history, one row per version",
        question="Which region was this dealer in on the day the order was promised?",
        plain="When a dealer moves region, the old row is closed (it gets an end date) and a new row opens. Both stay. "
              "Each version has its own key, and a fact picks the version that was true on the event date.",
        sources=[("silver_dealer_changes", """
CREATE TABLE silver_dealer_changes (dealer_id VARCHAR, name VARCHAR, region VARCHAR, tier VARCHAR, changed_on DATE);
INSERT INTO silver_dealer_changes VALUES
  ('D1','Sharma Tyres','North','Gold',     DATE '2026-11-01'),
  ('D1','Sharma Tyres','North','Gold',     DATE '2026-11-08'),  -- re-sent, nothing changed
  ('D1','Sharma Tyres','North','Platinum', DATE '2026-11-14'),
  ('D7','Patel Motors','North','Silver',   DATE '2026-11-01'),
  ('D7','Patel Motors','West', 'Silver',   DATE '2026-11-12');
"""), ("silver_order_lines", """
CREATE TABLE silver_order_lines (line_id VARCHAR, dealer_id VARCHAR, promised_date DATE);
INSERT INTO silver_order_lines VALUES
  ('L1','D1',DATE '2026-11-10'), ('L3','D7',DATE '2026-11-11'),
  ('L4','D7',DATE '2026-11-13'), ('L6','D1',DATE '2026-11-15');
""")],
        steps=[
            dict(cap="Drop rows where nothing changed (the re-sent 8 Nov row), by comparing each row with the one before it.",
                 sql="""CREATE TABLE dealer_changes_clean AS
SELECT *
FROM (SELECT *,
             concat_ws('|', name, region, tier) AS sig,
             lag(concat_ws('|', name, region, tier))
               OVER (PARTITION BY dealer_id ORDER BY changed_on) AS prev_sig
      FROM silver_dealer_changes)
WHERE prev_sig IS NULL OR sig <> prev_sig;""",
                 show="SELECT dealer_id, name, region, tier, changed_on FROM dealer_changes_clean ORDER BY dealer_id, changed_on"),
            dict(cap="Each version ends where the next one starts. The last version stays open (a far-future end date, so range joins need no NULL handling).",
                 sql="""CREATE TABLE dim_dealer AS
SELECT row_number() OVER (ORDER BY dealer_id, changed_on) AS dealer_key,
       dealer_id, name, region, tier,
       changed_on AS valid_from,
       COALESCE(lead(changed_on) OVER (PARTITION BY dealer_id ORDER BY changed_on),
                DATE '9999-12-31')                          AS valid_to,
       lead(changed_on) OVER (PARTITION BY dealer_id ORDER BY changed_on) IS NULL AS is_current
FROM dealer_changes_clean;""",
                 show="SELECT * FROM dim_dealer ORDER BY dealer_key"),
            dict(cap="A fact looks up the version true on its event date (valid_from inclusive, valid_to exclusive).",
                 sql="""SELECT o.line_id, o.dealer_id, o.promised_date,
       d.dealer_key, d.region, d.tier
FROM silver_order_lines o
LEFT JOIN dim_dealer d
  ON d.dealer_id = o.dealer_id
 AND o.promised_date >= d.valid_from
 AND o.promised_date <  d.valid_to
ORDER BY o.line_id;""",
                 show="""SELECT o.line_id, o.dealer_id, o.promised_date, d.dealer_key, d.region, d.tier
FROM silver_order_lines o
LEFT JOIN dim_dealer d ON d.dealer_id = o.dealer_id AND o.promised_date >= d.valid_from AND o.promised_date < d.valid_to
ORDER BY o.line_id"""),
        ],
        checks=[("D7 has two versions", "SELECT count(*) FROM dim_dealer WHERE dealer_id = 'D7'", 2),
                ("the re-sent row made no version", "SELECT count(*) FROM dim_dealer WHERE dealer_id = 'D1'", 2),
                ("L3 (11 Nov) was North", """SELECT d.region FROM silver_order_lines o JOIN dim_dealer d ON d.dealer_id=o.dealer_id
                   AND o.promised_date >= d.valid_from AND o.promised_date < d.valid_to WHERE o.line_id='L3'""", "North"),
                ("L4 (13 Nov) was West", """SELECT d.region FROM silver_order_lines o JOIN dim_dealer d ON d.dealer_id=o.dealer_id
                   AND o.promised_date >= d.valid_from AND o.promised_date < d.valid_to WHERE o.line_id='L4'""", "West"),
                ("versions never overlap", """SELECT count(*) FROM dim_dealer a JOIN dim_dealer b ON a.dealer_id=b.dealer_id
                   AND a.dealer_key < b.dealer_key AND a.valid_to > b.valid_from AND a.valid_from < b.valid_to""", 0)],
        when="Attributes people group by and where the past matters: a dealer's region, a customer's segment, an employee's department.",
        trap="Looking up the dealer's current row instead of the row true on the date silently moves old orders to the new region. "
             "Also check that versions of one dealer never overlap: an overlap makes a fact match two rows and doubles its numbers.",
    ),
    # ------------------------------------------------------------------------------------------ Type 3
    dict(
        id="d-type3", short="Type 3: previous value", kind="SCD Type 3",
        title="Type 3: current value plus the one before",
        question="Show each dealer's region now, and the region they were in before, side by side.",
        plain="One row per dealer, with two columns: region now and region before. Only one step back is kept. "
              "Useful for a 'moved from X to Y' report, and for a transition period when a reorganisation happens.",
        sources=[("silver_dealer_regions", """
CREATE TABLE silver_dealer_regions (dealer_id VARCHAR, name VARCHAR, region VARCHAR, from_date DATE);
INSERT INTO silver_dealer_regions VALUES
  ('D1','Sharma Tyres','North',DATE '2026-11-01'),
  ('D7','Patel Motors','North',DATE '2026-11-01'),
  ('D7','Patel Motors','West', DATE '2026-11-12');
""")],
        steps=[
            dict(cap="Take each dealer's newest row, and bring in the region from the row before it.",
                 sql="""CREATE TABLE dim_dealer_t3 AS
SELECT row_number() OVER (ORDER BY dealer_id) AS dealer_key,
       dealer_id, name,
       region          AS current_region,
       prev_region     AS previous_region,
       from_date       AS current_region_since
FROM (SELECT *,
             lag(region) OVER (PARTITION BY dealer_id ORDER BY from_date) AS prev_region,
             row_number() OVER (PARTITION BY dealer_id ORDER BY from_date DESC) AS rn
      FROM silver_dealer_regions)
WHERE rn = 1;""",
                 show="SELECT * FROM dim_dealer_t3 ORDER BY dealer_key"),
        ],
        checks=[("D7 moved from North", "SELECT previous_region FROM dim_dealer_t3 WHERE dealer_id='D7'", "North"),
                ("D1 has no previous region", "SELECT count(*) FROM dim_dealer_t3 WHERE dealer_id='D1' AND previous_region IS NULL", 1)],
        when="A reorganisation where you want old and new views at once, or a 'moved from' column on a report.",
        trap="Two moves in a row lose the first region. If that matters, you wanted Type 2.",
    ),
    # ------------------------------------------------------------------------------------------ Mini
    dict(
        id="d-mini", short="Mini-dimension", kind="Mini-dimension",
        title="Mini-dimension: fast-changing attributes in their own small table",
        question="Report orders by the dealer's volume band and risk band, as they were that month, without a new dealer row every month.",
        plain="Volume band and risk band change often. Making a Type 2 version of the dealer each time would explode the dealer table. "
              "Instead the few possible band combinations go in a tiny table of their own, and the fact carries both keys.",
        sources=[("silver_dealer_monthly_profile", """
CREATE TABLE silver_dealer_monthly_profile (dealer_id VARCHAR, month VARCHAR, volume_band VARCHAR, risk_band VARCHAR, qty INTEGER);
INSERT INTO silver_dealer_monthly_profile VALUES
  ('D1','2026-10','Medium','Low',    40), ('D1','2026-11','Medium','Low',    55),
  ('D7','2026-10','High',  'Low',   120), ('D7','2026-11','High',  'Medium',130),
  ('D9','2026-10','Low',   'Medium', 12), ('D9','2026-11','Medium','Medium', 30);
""")],
        steps=[
            dict(cap="The mini-dimension holds one row per band combination that exists, not one per dealer.",
                 sql="""CREATE TABLE dim_dealer_profile AS
SELECT row_number() OVER (ORDER BY volume_band, risk_band) AS profile_key,
       volume_band, risk_band
FROM (SELECT DISTINCT volume_band, risk_band FROM silver_dealer_monthly_profile);""",
                 show="SELECT * FROM dim_dealer_profile ORDER BY profile_key"),
            dict(cap="The monthly fact carries the profile key that was true that month.",
                 sql="""CREATE TABLE fact_dealer_month AS
SELECT p.dealer_id, p.month, m.profile_key, p.qty
FROM silver_dealer_monthly_profile p
JOIN dim_dealer_profile m USING (volume_band, risk_band);""",
                 show="SELECT * FROM fact_dealer_month ORDER BY dealer_id, month"),
            dict(cap="Ask the question: tyres by risk band, per month. D7's Medium risk in November shows up in November only.",
                 sql="""SELECT f.month, m.risk_band, sum(f.qty) AS qty
FROM fact_dealer_month f JOIN dim_dealer_profile m USING (profile_key)
GROUP BY f.month, m.risk_band ORDER BY f.month, m.risk_band;""",
                 show="""SELECT f.month, m.risk_band, sum(f.qty) AS qty
FROM fact_dealer_month f JOIN dim_dealer_profile m USING (profile_key)
GROUP BY f.month, m.risk_band ORDER BY f.month, m.risk_band"""),
        ],
        checks=[("six dealer-months, five band combinations", "SELECT count(*) FROM dim_dealer_profile", 5),
                ("no month lost in the join", "SELECT count(*) FROM fact_dealer_month", 6)],
        when="A big dimension (millions of customers) with a few attributes that change monthly: a credit band, an activity band, a loyalty level.",
        trap="Bands must be small, banded values (Low, Medium, High), never raw numbers like a credit score: raw numbers make the mini-dimension as big as the fact.",
    ),
    # ------------------------------------------------------------------------------------------ Date
    dict(
        id="d-date", short="Date dimension", kind="Type 0 (fixed), generated",
        title="Date dimension: generated, never changes",
        question="Group by fiscal quarter, weekday or weekend without writing date maths in every report.",
        plain="No source table at all. You generate one row per day for as many years as you need. "
              "Rows never change (Type 0), and every fact points at a date by a whole-number key like 20261113.",
        sources=[],
        steps=[
            dict(cap="One row per day for an Indian financial year (April to March). In Spark or Databricks, replace the generator with explode(sequence(DATE'2026-04-01', DATE'2027-03-31', INTERVAL 1 DAY)).",
                 sql=DATE_DIM.strip(),
                 show="SELECT * FROM dim_date WHERE date IN (DATE '2026-03-31', DATE '2026-11-13', DATE '2026-11-14', DATE '2026-11-15', DATE '2027-03-31') ORDER BY date"),
            dict(cap="Add the unknown date, so a fact whose date is missing still joins.",
                 sql="""INSERT INTO dim_date VALUES (-1, NULL, 'Unknown', FALSE, 'Unknown', 'Unknown', 'Unknown');""",
                 show="SELECT * FROM dim_date WHERE date_key IN (-1, 20261113) ORDER BY date_key"),
        ],
        checks=[("365 days plus the unknown row", "SELECT count(*) FROM dim_date", 366),
                ("13 Nov 2026 is in FY2026-27 quarter 3", "SELECT fiscal_year || ' ' || fiscal_quarter FROM dim_date WHERE date_key = 20261113", "FY2026-27 Q3"),
                ("31 March 2027 is the last day of quarter 4", "SELECT fiscal_year || ' ' || fiscal_quarter FROM dim_date WHERE date_key = 20270331", "FY2026-27 Q4")],
        when="Always. Every fact has at least one date.",
        trap="Fiscal year and quarter are the part people get wrong: check the first and last day of the year against finance's own calendar before anyone reports on it.",
    ),
    # ------------------------------------------------------------------------------------------ Role-playing
    dict(
        id="d-role", short="Role-playing date", kind="Role-playing",
        title="Role-playing: one date table, used as promised date and delivered date",
        question="Which weekday was the delivery made on, and how many days after the promised day?",
        plain="A fact often has several dates. You do not build a second date table. The same date dimension plays "
              "two roles, and gets a different name each time you join it. (This example uses the dim_date built in the previous one.)",
        sources=[("fact_order_line_dates", """
CREATE TABLE fact_order_line_dates (line_id VARCHAR, promised_date_key INTEGER, delivered_date_key INTEGER);
INSERT INTO fact_order_line_dates VALUES
  ('L1', 20261110, 20261110), ('L2', 20261110, 20261111), ('L3', 20261111, 20261112), ('L7', 20261113, NULL);
""")],
        steps=[
            dict(cap="Give each role its own view, so report tools show 'Promised date' and 'Delivered date' as separate pickers.",
                 sql="""CREATE VIEW dim_promised_date  AS SELECT date_key AS promised_date_key,  date AS promised_date,  day_name AS promised_day  FROM dim_date;
CREATE VIEW dim_delivered_date AS SELECT date_key AS delivered_date_key, date AS delivered_date, day_name AS delivered_day FROM dim_date;""",
                 show=None),
            dict(cap="Join both roles to the same fact. A LEFT JOIN on the second keeps L7, which has not been delivered yet.",
                 sql="""SELECT f.line_id, p.promised_day, d.delivered_day,
       date_diff('day', p.promised_date, d.delivered_date) AS days_after_promise
FROM fact_order_line_dates f
JOIN dim_promised_date p USING (promised_date_key)
LEFT JOIN dim_delivered_date d USING (delivered_date_key)
ORDER BY f.line_id;""",
                 show="""SELECT f.line_id, p.promised_day, d.delivered_day,
       date_diff('day', p.promised_date, d.delivered_date) AS days_after_promise
FROM fact_order_line_dates f
JOIN dim_promised_date p USING (promised_date_key)
LEFT JOIN dim_delivered_date d USING (delivered_date_key)
ORDER BY f.line_id"""),
        ],
        checks=[("L3 was a day late", """SELECT date_diff('day', p.promised_date, d.delivered_date) FROM fact_order_line_dates f
                  JOIN dim_promised_date p USING (promised_date_key) JOIN dim_delivered_date d USING (delivered_date_key) WHERE f.line_id='L3'""", 1),
                ("the undelivered line stays in", """SELECT count(*) FROM fact_order_line_dates f JOIN dim_promised_date p USING (promised_date_key)
                  LEFT JOIN dim_delivered_date d USING (delivered_date_key)""", 4)],
        when="Any fact with more than one date, or more than one dealer, warehouse or employee role (ship-from and ship-to).",
        trap="An INNER JOIN on the second role quietly drops every row that has no value yet, such as lines not yet delivered. Use LEFT JOIN, or point the key at the unknown row.",
    ),
    # ------------------------------------------------------------------------------------------ Junk
    dict(
        id="d-junk", short="Junk dimension", kind="Junk",
        title="Junk dimension: a handful of flags in one small table",
        question="Count orders by rush, payment mode and gift wrap, without three more columns of text on a huge fact.",
        plain="Small flags that do not belong anywhere else are put together in one little table with a row per combination that exists. "
              "The fact carries one key instead of three flags.",
        sources=[("silver_orders", """
CREATE TABLE silver_orders (order_id VARCHAR, is_rush VARCHAR, payment_mode VARCHAR, gift_wrap VARCHAR, amount INTEGER);
INSERT INTO silver_orders VALUES
  ('O1','Y','COD',    'N', 1400), ('O2','N','Prepaid','N', 800),
  ('O3','Y','COD',    'N',  300), ('O4','N','Prepaid','Y', 500);
""")],
        steps=[
            dict(cap="One row per combination that really occurs. (If the flags are few, you can instead cross join every possible value so the table is complete up front.)",
                 sql="""CREATE TABLE dim_order_flags AS
SELECT row_number() OVER (ORDER BY is_rush, payment_mode, gift_wrap) AS order_flags_key,
       is_rush, payment_mode, gift_wrap
FROM (SELECT DISTINCT is_rush, payment_mode, gift_wrap FROM silver_orders);""",
                 show="SELECT * FROM dim_order_flags ORDER BY order_flags_key"),
            dict(cap="The fact keeps order_id (see the next example) and one key for all three flags.",
                 sql="""CREATE TABLE fact_order AS
SELECT o.order_id, f.order_flags_key, o.amount
FROM silver_orders o
JOIN dim_order_flags f
  ON f.is_rush = o.is_rush AND f.payment_mode = o.payment_mode AND f.gift_wrap = o.gift_wrap;""",
                 show="SELECT * FROM fact_order ORDER BY order_id"),
        ],
        checks=[("O1 and O3 share a key", "SELECT count(DISTINCT order_flags_key) FROM fact_order WHERE order_id IN ('O1','O3')", 1),
                ("three combinations", "SELECT count(*) FROM dim_order_flags", 3)],
        when="Three to ten low-cardinality flags and codes sitting on a fact: rush, payment mode, channel, gift wrap.",
        trap="A new flag value (a new payment mode) needs a new row before the fact load, or the join drops the order. Add the new combination first, then load.",
    ),
    # ------------------------------------------------------------------------------------------ Degenerate
    dict(
        id="d-degenerate", short="Degenerate dimension", kind="Degenerate",
        title="Degenerate dimension: the order number stays in the fact",
        question="Show me everything on order O1.",
        plain="An order number is something you filter and group by, so it behaves like a dimension. "
              "But it has nothing to describe (no name, no region), so it gets no table. The number simply sits in the fact.",
        sources=[("fact_order_line", """
CREATE TABLE fact_order_line (order_id VARCHAR, line_no INTEGER, product_id VARCHAR, qty INTEGER);
INSERT INTO fact_order_line VALUES
  ('O1',1,'P1',10), ('O1',2,'P2',5), ('O2',1,'P1',8), ('O2',2,'P3',4);
""")],
        steps=[
            dict(cap="No join, no table. Group and filter on the order number directly.",
                 sql="""SELECT order_id, count(*) AS lines, sum(qty) AS tyres
FROM fact_order_line
GROUP BY order_id ORDER BY order_id;""",
                 show="SELECT order_id, count(*) AS lines, sum(qty) AS tyres FROM fact_order_line GROUP BY order_id ORDER BY order_id"),
        ],
        checks=[("two orders", "SELECT count(DISTINCT order_id) FROM fact_order_line", 2)],
        when="Order numbers, invoice numbers, ticket numbers: identifiers with no attributes of their own.",
        trap="If the order later gains attributes (customer note, approver), it stops being degenerate: give it a real dimension then.",
    ),
    # ------------------------------------------------------------------------------------------ Bridge
    dict(
        id="d-bridge", short="Bridge (many-to-many)", kind="Bridge table",
        title="Bridge table: a dealer offers several services",
        question="Revenue by service, when one dealer offers fitting, balancing and alignment, without counting the same money three times.",
        plain="One dealer, many services: a join would repeat the dealer's revenue once per service. "
              "A bridge table sits between them and gives each pair a weight. Weights for one dealer add up to 1, so the totals still add up.",
        sources=[("silver_dealer_services", """
CREATE TABLE silver_dealer_services (dealer_id VARCHAR, service VARCHAR);
INSERT INTO silver_dealer_services VALUES
  ('D1','Fitting'), ('D1','Balancing'),
  ('D7','Fitting'), ('D7','Alignment'), ('D7','Balancing');
"""), ("fact_dealer_revenue", """
CREATE TABLE fact_dealer_revenue (dealer_id VARCHAR, revenue INTEGER);
INSERT INTO fact_dealer_revenue VALUES ('D1',1000), ('D7',1500);
""")],
        steps=[
            dict(cap="The bridge: one row per dealer and service, weight = 1 divided by how many services the dealer offers.",
                 sql="""CREATE TABLE bridge_dealer_service AS
SELECT dealer_id, service,
       1.0 / count(*) OVER (PARTITION BY dealer_id) AS weight
FROM silver_dealer_services;""",
                 show="SELECT dealer_id, service, round(weight, 4) AS weight FROM bridge_dealer_service ORDER BY dealer_id, service"),
            dict(cap="The wrong way and the right way, side by side. Revenue is really 2,500.",
                 sql="""SELECT b.service,
       sum(f.revenue)                       AS revenue_naive,
       round(sum(f.revenue * b.weight), 2)  AS revenue_weighted
FROM fact_dealer_revenue f
JOIN bridge_dealer_service b USING (dealer_id)
GROUP BY b.service ORDER BY b.service;""",
                 show="""SELECT b.service, sum(f.revenue) AS revenue_naive, round(sum(f.revenue * b.weight), 2) AS revenue_weighted
FROM fact_dealer_revenue f JOIN bridge_dealer_service b USING (dealer_id)
GROUP BY b.service ORDER BY b.service"""),
        ],
        checks=[("weighted revenue adds up to the real 2,500", "SELECT round(sum(f.revenue * b.weight), 2) FROM fact_dealer_revenue f JOIN bridge_dealer_service b USING (dealer_id)", 2500.0),
                ("naive revenue is far too high", "SELECT sum(f.revenue) FROM fact_dealer_revenue f JOIN bridge_dealer_service b USING (dealer_id)", 6500),
                ("weights sum to 1 per dealer", "SELECT count(*) FROM (SELECT dealer_id FROM bridge_dealer_service GROUP BY dealer_id HAVING abs(sum(weight) - 1) > 0.001)", 0)],
        when="Genuine many-to-many: a patient with several diagnoses, a dealer with several services, a product in several categories.",
        trap="The naive join is the classic double count. Keep weights at full precision (0.3333 three times is 0.9999). Always test that weighted totals equal the fact's own total, and publish only the weighted view.",
    ),
    # ------------------------------------------------------------------------------------------ Hierarchy
    dict(
        id="d-hierarchy", short="Flattened hierarchy", kind="Hierarchy",
        title="Hierarchy: city, state and region in one row",
        question="Group orders by region, state or city, with no recursive queries in the report.",
        plain="The source stores places as a tree: each place points at its parent. For reporting, you flatten the tree "
              "so each city row also carries its state and region. Reports then just pick a column.",
        sources=[("silver_geography", """
CREATE TABLE silver_geography (geo_id VARCHAR, name VARCHAR, level VARCHAR, parent_id VARCHAR);
INSERT INTO silver_geography VALUES
  ('R1','North','region',NULL),       ('R2','West','region',NULL),
  ('S1','Delhi','state','R1'),        ('S2','Maharashtra','state','R2'),
  ('C1','New Delhi','city','S1'),     ('C2','Mumbai','city','S2'), ('C3','Pune','city','S2');
""")],
        steps=[
            dict(cap="A fixed three-level tree is just two self-joins. (A tree of unknown depth needs a recursive query; do it once here, never in reports.)",
                 sql="""CREATE TABLE dim_geography AS
SELECT row_number() OVER (ORDER BY c.geo_id) AS geography_key,
       c.name AS city, s.name AS state, r.name AS region
FROM silver_geography c
JOIN silver_geography s ON s.geo_id = c.parent_id AND s.level = 'state'
JOIN silver_geography r ON r.geo_id = s.parent_id AND r.level = 'region'
WHERE c.level = 'city';""",
                 show="SELECT * FROM dim_geography ORDER BY geography_key"),
        ],
        checks=[("every city has a region", "SELECT count(*) FROM dim_geography WHERE region IS NULL", 0),
                ("three cities", "SELECT count(*) FROM dim_geography", 3)],
        when="Product to category to department; city to state to country; employee to manager to director.",
        trap="An INNER JOIN drops a city whose state is missing in the source. Use LEFT JOINs plus a check that counts cities in silver against cities in gold.",
    ),
    # ------------------------------------------------------------------------------------------ Inferred
    dict(
        id="d-inferred", short="Unknown and inferred members", kind="Late-arriving member",
        title="Late dealer: the unknown row and the inferred row",
        question="An order arrives for dealer D9 before D9 is in the dealer list. What does the fact point at?",
        plain="Two safe answers. The unknown row (key -1) says 'we do not know yet' and the fact is re-keyed when D9 appears. "
              "The inferred row creates a placeholder for D9 now, with a real key, and fills it in when the real details arrive. The fact never changes.",
        sources=[("dim_dealer_i", """
CREATE TABLE dim_dealer_i (dealer_key INTEGER, dealer_id VARCHAR, name VARCHAR, region VARCHAR, is_inferred BOOLEAN);
INSERT INTO dim_dealer_i VALUES
  (-1,'?','Unknown','Unknown',FALSE),
  ( 1,'D1','Sharma Tyres','North',FALSE),
  ( 2,'D7','Patel Motors','West',FALSE);
"""), ("silver_late_order_lines", """
CREATE TABLE silver_late_order_lines (line_id VARCHAR, dealer_id VARCHAR, qty INTEGER);
INSERT INTO silver_late_order_lines VALUES ('L1','D1',10), ('L4','D7',4), ('L5','D9',6);
""")],
        steps=[
            dict(cap="Create a placeholder for every dealer id the facts mention but the dimension does not know.",
                 sql="""INSERT INTO dim_dealer_i
SELECT (SELECT max(dealer_key) FROM dim_dealer_i) + row_number() OVER (ORDER BY dealer_id),
       dealer_id, 'Unknown (inferred)', 'Unknown', TRUE
FROM (SELECT DISTINCT dealer_id FROM silver_late_order_lines o
      WHERE NOT EXISTS (SELECT 1 FROM dim_dealer_i d WHERE d.dealer_id = o.dealer_id));""",
                 show="SELECT * FROM dim_dealer_i ORDER BY dealer_key"),
            dict(cap="Build the fact. Every line now has a real key, even L5.",
                 sql="""CREATE TABLE fact_line AS
SELECT o.line_id, d.dealer_key, o.qty
FROM silver_late_order_lines o JOIN dim_dealer_i d USING (dealer_id);""",
                 show="SELECT * FROM fact_line ORDER BY line_id"),
            dict(cap="Days later the real D9 arrives from silver. Fill the placeholder in. Its key, and so the fact, does not change.",
                 sql="""UPDATE dim_dealer_i
SET name = 'Gupta Wheels', region = 'West', is_inferred = FALSE
WHERE dealer_id = 'D9';""",
                 show="""SELECT f.line_id, d.dealer_key, d.dealer_id, d.name, d.region, d.is_inferred
FROM fact_line f JOIN dim_dealer_i d USING (dealer_key) ORDER BY f.line_id"""),
        ],
        checks=[("L5 points at the D9 placeholder, not at -1", "SELECT dealer_key FROM fact_line WHERE line_id='L5'", 3),
                ("after the fill-in L5 shows the real region", "SELECT d.region FROM fact_line f JOIN dim_dealer_i d USING (dealer_key) WHERE f.line_id='L5'", "West"),
                ("no line points at unknown", "SELECT count(*) FROM fact_line WHERE dealer_key = -1", 0)],
        when="Any feed where facts can arrive before their dimension: new customers, new dealers, new products. This is normal.",
        trap="With a Type 2 dimension, the first real version of D9 should start from the placeholder's first-seen date, not from today, or earlier facts look up no version.",
    ),
]
