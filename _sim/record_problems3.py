"""Problem Lab, third set (problems 11-19), recorded from REAL runs on local Spark + Delta.

Called by record_problems.py. Each problem: what you see, the naive fix (run for real), the right fix.
  quality    bad data: rules from a contract, quarantine with a reason
  latedim    early facts, late dimensions: inferred members
  dark       source goes dark: freshness SLO, catch-up that absorbs the flood
  recon      reconciliation mismatch: count and sum at every hop
  tz         time zones and daylight saving
  writers    two writers at once
  skew       one hot key
  pii        personal data leak: tags, masking, audit
  heal       self-healing at 2 a.m.: deterministic runbook with gates
"""
import hashlib
import json
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from pyspark.sql import functions as F

from record_problems import chk, money, rows, short_err, version


def tbl(df, n=15):
    r = df.limit(n).collect()
    return {"cols": df.columns, "rows": [[None if x is None else str(x) for x in row] for row in r], "count": df.count()}


def more2(R, spark, wh):
    sql = R.sql
    for d in ("dq", "ld", "dark", "rc", "tz", "wr", "sk", "pii", "heal"):
        sql(f"CREATE DATABASE {d}")

    # =================================================================== 11. bad data
    data = [("6001", "C-1", 500.0, "IN"), ("6002", None, 300.0, "IN"), ("6003", "C-2", -200.0, "IN"), ("6004", "C-3", 150.0, "Ind"),
            ("6005", "C-4", 800.0, "US"), ("6006", "C-5", 250.0, "IN"), ("6007", "C-6", 90.0, "GB"), ("6008", "C-1", 410.0, "IN")]
    spark.createDataFrame(data, "order_id string, customer_id string, amount double, country string").write.format("delta").saveAsTable("dq.bronze")
    RULES = [("customer_id is present", "customer_id IS NOT NULL"), ("amount is not negative", "amount >= 0"),
             ("country is an ISO code", "country IN ('IN','US','GB','AE','SG')")]
    contract_yaml = "# orders.contract.yaml (owned by the source team and the data team together)\nrules:\n" + "".join(f"  - name: {n}\n    check: {c}\n" for n, c in RULES) + "on_fail: quarantine_and_alert"
    contract_hash = hashlib.sha256(contract_yaml.encode()).hexdigest()[:12]

    def rule_checks(t):
        return [chk(n, f"{R.val(f'SELECT count(*) FROM {t} WHERE NOT coalesce({c}, false)')} rows break it", R.val(f"SELECT count(*) FROM {t} WHERE NOT coalesce({c}, false)") == 0) for n, c in RULES]

    def by_country(t):
        return {"tiles": [[r.country or "(none)", money(r.rev)] for r in sql(f"SELECT country, sum(amount) rev FROM {t} GROUP BY country ORDER BY country").collect()][:4]}
    sql("CREATE TABLE dq.silver USING delta AS SELECT * FROM dq.bronze")
    R.log("INFO", "silver loaded: 8 rows")
    R.pstep("quality", "What you see: bad values flow straight into the dashboard",
            "Eight orders arrived. One has no customer, one has a negative amount (a refund sent as an order), and one says country 'Ind' instead of 'IN'. Nothing stops them: the dashboard shows −₹200 in India's revenue, a separate country called 'Ind', and an order nobody can be billed for. The source does not validate, and the agreed rules (the contract) exist only in a wiki.",
            "CREATE TABLE silver AS SELECT * FROM bronze   -- no rules applied\n\n" + contract_yaml,
            rule_checks("dq.silver"), {"silver": R.table("dq.silver")}, by_country("dq.silver"))

    loose = [("customer_id is present", "true"), ("amount is not negative", "amount >= -1000"), ("country is an ISO code", "length(country) <= 3")]
    loose_yaml = "rules:\n" + "".join(f"  - name: {n}\n    check: {c}\n" for n, c in loose) + "on_fail: quarantine_and_alert"
    sql("CREATE TABLE dq.silver_loose USING delta AS SELECT * FROM dq.bronze WHERE " + " AND ".join(f"({c})" for _, c in loose))
    loose_hash = hashlib.sha256(loose_yaml.encode()).hexdigest()[:12]
    R.log("INFO", "all rules passed: 8 rows")
    R.pstep("quality", "Naive fix: loosen the rules until the job passes",
            "The job kept failing at night, so someone edited the rules: customer_id no longer required, negative amounts allowed down to −1,000, and any country code of up to three letters accepted. Every rule passes now, and the log says so. But the data is exactly as bad as before: measured against the agreed contract, the same rows still break it. Only the alarm was switched off.",
            loose_yaml + "\n# the edited contract: every rule now passes",
            [chk(n + " (as agreed)", c[1], c[2]) for n, c in zip([r[0] for r in RULES], rule_checks("dq.silver_loose"))] +
            [chk("contract unchanged", f"{contract_hash} → {loose_hash}", False)],
            {"silver": R.table("dq.silver_loose")}, by_country("dq.silver_loose"))

    failed = F.filter(F.array(*[F.when(~F.coalesce(F.expr(c), F.lit(False)), F.lit(n)) for n, c in RULES]), lambda x: x.isNotNull())
    checked = spark.table("dq.bronze").withColumn("failed_rules", failed).cache()
    checked.filter(F.size("failed_rules") == 0).drop("failed_rules").write.format("delta").saveAsTable("dq.silver_ok")
    checked.filter(F.size("failed_rules") > 0).withColumn("failed_rules", F.concat_ws("; ", "failed_rules")) \
        .withColumn("_quarantined_at", F.lit("2026-10-27T23:00:00Z")).write.format("delta").saveAsTable("dq.quarantine")
    checked.unpersist()
    n_ok, n_q = R.val("SELECT count(*) FROM dq.silver_ok"), R.val("SELECT count(*) FROM dq.quarantine")
    for r in sql("SELECT failed_rules, count(*) n FROM dq.quarantine GROUP BY failed_rules ORDER BY failed_rules").collect():
        R.log("WARN", f"{r.n} row(s) quarantined: {r.failed_rules}; owner of 'orders' alerted")
    R.pstep("quality", "Right fix: rules from the contract, quarantine with the rule that failed",
            f"The rules live in the contract file and are never edited to make a run pass. The job evaluates every rule on every row and collects the names of the rules a row breaks. Rows that break none go to silver ({n_ok}); the others go to quarantine with the failed rule names ({n_q}), and the source owner gets one alert per rule. When the source fixes them, they are replayed from quarantine. The counts add up: 8 in, {n_ok} + {n_q} out.",
            "failed = filter(array(*[when(~coalesce(expr(check), lit(False)), lit(name)) for name, check in contract.rules]),\n                lambda x: x.isNotNull())\nchecked = bronze.withColumn('failed_rules', failed)\nchecked.filter(size('failed_rules') == 0) -> silver\nchecked.filter(size('failed_rules') > 0)  -> quarantine   # with failed_rules\nalert(owner, counts per rule)",
            rule_checks("dq.silver_ok") + [chk("rows in = silver + quarantine", f"8 = {n_ok} + {n_q}", n_ok + n_q == 8), chk("contract unchanged", contract_hash, True)],
            {"silver": R.table("dq.silver_ok"), "quarantine": R.table("dq.quarantine")}, by_country("dq.silver_ok"), "dq.quarantine")

    # =================================================================== 12. early facts, late dimensions
    sql("CREATE TABLE ld.dim_customer (customer_sk BIGINT, customer_id STRING, city STRING, is_inferred BOOLEAN) USING delta")
    sql("INSERT INTO ld.dim_customer VALUES (1,'C-1','Pune',false),(2,'C-2','Delhi',false)")
    spark.createDataFrame([("7001", "C-1", 500.0), ("7002", "C-2", 300.0), ("7003", "C-9", 900.0)], "order_id string, customer_id string, amount double") \
        .write.format("delta").saveAsTable("ld.orders")
    TRUTH = 1700.0
    sql("CREATE TABLE ld.fact_inner USING delta AS SELECT o.order_id, d.customer_sk, o.amount FROM ld.orders o JOIN ld.dim_customer d USING (customer_id)")

    def report(fact, dim="ld.dim_customer"):
        return sql(f"SELECT coalesce(d.city, 'Unknown') AS city, count(*) AS orders, sum(f.amount) AS revenue FROM {fact} f LEFT JOIN {dim} d USING (customer_sk) GROUP BY 1 ORDER BY 1")
    rev = R.val("SELECT sum(amount) FROM ld.fact_inner")
    n = R.val("SELECT count(*) FROM ld.fact_inner")
    R.log("INFO", f"fact loaded: {n} rows (3 orders in the batch)")
    R.pstep("latedim", "What you see: an order vanishes from the report",
            f"Three orders arrived. Order 7003 is from customer C-9, who signed up a minute ago, but the customer feed runs hourly and has not delivered C-9 yet. The fact load joins orders to the customer dimension with an inner join, so order 7003 simply drops out: {n} orders and {money(rev)} in gold, {money(TRUTH)} in the shop. No error, no log line, just less money.",
            "SELECT o.order_id, d.customer_sk, o.amount\nFROM orders o JOIN dim_customer d USING (customer_id)   -- inner join",
            [chk("every order reaches gold", f"{n} of 3", n == 3), chk("revenue = what the shop sold", f"{money(rev)} vs {money(TRUTH)}", rev == TRUTH)],
            {"report by city": tbl(report("ld.fact_inner")), "dim_customer": R.table("ld.dim_customer"), "orders": R.table("ld.orders")})

    sql("INSERT INTO ld.dim_customer VALUES (-1,'(unknown)','Unknown',false)")
    sql("""CREATE TABLE ld.fact_unknown USING delta AS SELECT o.order_id, coalesce(d.customer_sk, -1) AS customer_sk, o.amount
           FROM ld.orders o LEFT JOIN ld.dim_customer d USING (customer_id)""")
    sql("INSERT INTO ld.dim_customer VALUES (3,'C-9','Mumbai',false)")        # the customer feed arrives an hour later
    rep = report("ld.fact_unknown")
    mumbai = R.val("SELECT coalesce(sum(f.amount),0) FROM ld.fact_unknown f JOIN ld.dim_customer d USING (customer_sk) WHERE d.city = 'Mumbai'")
    unknown = R.val("SELECT coalesce(sum(amount),0) FROM ld.fact_unknown WHERE customer_sk = -1")
    R.log("INFO", "customer feed delivered C-9 (Mumbai)")
    R.pstep("latedim", "Naive fix: point unknown customers at one 'Unknown' row",
            f"A left join with a default key -1 ('Unknown') keeps every order: revenue is right again. An hour later the customer feed delivers C-9, who lives in Mumbai. But the fact row still points at -1, and nothing will ever repoint it. Mumbai shows {money(mumbai)}; 'Unknown' keeps {money(unknown)} forever, and it grows every day.",
            "SELECT o.order_id, coalesce(d.customer_sk, -1) AS customer_sk, o.amount\nFROM orders o LEFT JOIN dim_customer d USING (customer_id)\n\n-- an hour later the customer feed adds C-9 (Mumbai) as a new row",
            [chk("every order reaches gold", "3 of 3", True), chk("order 7003 counted in Mumbai once C-9 arrives", f"Mumbai {money(mumbai)}", mumbai == 900),
             chk("'Unknown' empties once customers arrive", money(unknown), unknown == 0)],
            {"report by city": tbl(rep), "dim_customer": R.table("ld.dim_customer")})

    sql("CREATE TABLE ld.dim2 (customer_sk BIGINT, customer_id STRING, city STRING, is_inferred BOOLEAN) USING delta")
    sql("INSERT INTO ld.dim2 VALUES (1,'C-1','Pune',false),(2,'C-2','Delhi',false)")
    inferred = """INSERT INTO dim2
SELECT (SELECT max(customer_sk) FROM dim2) + row_number() OVER (ORDER BY customer_id), customer_id, NULL, true
FROM (SELECT DISTINCT customer_id FROM orders) o
WHERE NOT EXISTS (SELECT 1 FROM dim2 d WHERE d.customer_id = o.customer_id)"""
    sql(inferred.replace("dim2", "ld.dim2").replace("FROM orders", "FROM ld.orders"))
    placeholders_at_load = R.val("SELECT count(*) FROM ld.dim2 WHERE is_inferred")
    sql("CREATE TABLE ld.fact_ok USING delta AS SELECT o.order_id, d.customer_sk, o.amount FROM ld.orders o JOIN ld.dim2 d USING (customer_id)")
    v_fact = version(spark, "ld.fact_ok")
    spark.createDataFrame([("C-9", "Mumbai")], "customer_id string, city string").createOrReplaceTempView("customer_feed")
    fill = """MERGE INTO dim2 d USING customer_feed s ON d.customer_id = s.customer_id
WHEN MATCHED AND d.is_inferred THEN UPDATE SET city = s.city, is_inferred = false   -- fill the placeholder in place, same key"""
    sql(fill.replace("dim2", "ld.dim2"))
    mumbai = R.val("SELECT coalesce(sum(f.amount),0) FROM ld.fact_ok f JOIN ld.dim2 d USING (customer_sk) WHERE d.city = 'Mumbai'")
    left = R.val("SELECT count(*) FROM ld.dim2 WHERE is_inferred")
    n = R.val("SELECT count(*) FROM ld.fact_ok")
    R.log("INFO", f"inferred member created for C-9 at fact load ({placeholders_at_load} placeholder)")
    R.log("INFO", "customer feed filled the placeholder for C-9; fact untouched")
    R.pstep("latedim", "Right fix: an inferred member, filled in when the customer arrives",
            f"Before loading facts, create a placeholder row in the customer dimension for every customer_id the dimension has not seen, flagged is_inferred, with its own key. The order joins to it and is counted. When the customer feed delivers C-9, the MERGE fills that same row in place (same key) and clears the flag. The fact table is never touched (still version {version(spark, 'ld.fact_ok')}, was {v_fact}), yet the report now shows Mumbai {money(mumbai)}. The count of placeholders is a check: it should drop to zero as dimensions catch up.",
            inferred + "\n\n-- load facts with a plain join: every customer now has a row\n\n-- when the customer feed arrives:\n" + fill,
            [chk("every order reaches gold", f"{n} of 3", n == 3), chk("order 7003 counted in Mumbai once C-9 arrives", f"Mumbai {money(mumbai)}", mumbai == 900),
             chk("placeholders left", f"{placeholders_at_load} at load → {left} now", left == 0), chk("fact rows rewritten", f"version {v_fact} → {version(spark, 'ld.fact_ok')}", version(spark, "ld.fact_ok") == v_fact)],
            {"report by city": tbl(report("ld.fact_ok", "ld.dim2")), "dim_customer": R.table("ld.dim2")}, None, "ld.dim2")

    # =================================================================== 13. source goes dark
    base = datetime(2026, 10, 27, tzinfo=timezone.utc)
    events = [(f"E-{h:02d}{i}", base + timedelta(hours=h, minutes=6 * i), float(50 + (h * 13 + i * 7) % 90)) for h in range(12) for i in range(9)]
    OUT_H = range(3, 9)                  # deliveries for these hours never came

    def delivery(h):
        if h in OUT_H:
            return []
        if h == 9:
            return [e for e in events if 3 <= e[1].hour <= 9]          # the flood
        return [e for e in events if e[1].hour == h]
    SCH = "event_id string, event_ts timestamp, amount double"
    truth_h = {}
    for e in events:
        truth_h[e[1].hour] = truth_h.get(e[1].hour, 0) + e[2]

    def hourly(t):
        got = {r.h: r.rev for r in sql(f"SELECT hour(event_ts) h, sum(amount) rev FROM {t} GROUP BY 1").collect()}
        return {"hourly revenue": {"cols": ["hour", "loaded", "source", "match"], "rows": [[f"{h:02d}:00", money(got.get(h, 0)), money(truth_h[h]), "✓" if got.get(h, 0) == truth_h[h] else "✗"] for h in range(12)], "count": 12}}, got

    def dupes(t):
        return R.val(f"SELECT count(*) - count(DISTINCT event_id) FROM {t}")
    sql("CREATE TABLE dark.naive (event_id STRING, event_ts TIMESTAMP, amount DOUBLE) USING delta")
    pages = []
    for h in range(0, 9):                # runs at h+1:05 for hour h, up to the moment before the flood
        rows_h = delivery(h)
        if rows_h:
            spark.createDataFrame(rows_h, SCH).write.format("delta").mode("append").saveAsTable("dark.naive")
        else:
            pages.append(f"{h + 1:02d}:05")
            R.log("ERROR", f"{h + 1:02d}:05 PAGE on-call: no new orders in the last hour")
    view, got = hourly("dark.naive")
    R.pstep("dark", "What you see: six hours of nothing, and a page every hour",
            f"The orders source went down at 03:00. The hourly job keeps running and finds nothing, and the monitor pages the on-call engineer every time: {len(pages)} pages between {pages[0]} and {pages[-1]}, mostly in the middle of the night, all saying the same thing. Hours 03–08 show zero revenue, and nobody can tell 'the shop was quiet' from 'we received nothing'.",
            "every hour:\n    rows = fetch(hour)\n    append(rows)\n    if not rows: page_oncall('no new orders in the last hour')",
            [chk("hours 03–08 have data", "all six empty", False), chk("one alert per incident", f"{len(pages)} pages", len(pages) <= 2)],
            view, {"tiles": [["Pages sent", str(len(pages))], ["Empty hours", "6"], ["Source", "down"], ["Correct", "✗ no"]]}, None, ["inputs", "checks", "layers", "logs"])
    spark.createDataFrame(delivery(9), SCH).write.format("delta").mode("append").saveAsTable("dark.naive")      # the flood
    for h in OUT_H:                      # on-call re-runs the 'missed' hours; the recovered source now serves them
        spark.createDataFrame([e for e in events if e[1].hour == h], SCH).write.format("delta").mode("append").saveAsTable("dark.naive")
    for h in (10, 11):
        spark.createDataFrame(delivery(h), SCH).write.format("delta").mode("append").saveAsTable("dark.naive")
    view, got = hourly("dark.naive")
    d = dupes("dark.naive")
    R.log("WARN", f"10:05 flood loaded: {len(delivery(9))} rows; on-call re-ran hours 03–08 by hand")
    R.pstep("dark", "Naive fix: load the flood, then re-run the missed hours by hand",
            f"At 10:05 the source comes back and sends everything it held: {len(delivery(9))} orders in one delivery. The job appends it. Meanwhile the on-call engineer, following the pages, re-runs the six 'missed' hours by hand, and the recovered source serves those hours again. Both land. {d} orders are now counted twice, and hours 03–08 show double revenue.",
            "append(flood)                      # 10:05, hours 03–09 in one go\nfor h in missed_hours: append(fetch(h))   # by hand, at the same time",
            [chk("no order counted twice", f"{d} duplicates", d == 0), chk("every hour = source", f"{sum(1 for h in range(12) if got.get(h, 0) == truth_h[h])} of 12 hours", all(got.get(h, 0) == truth_h[h] for h in range(12)))],
            view, {"tiles": [["Pages sent", str(len(pages))], ["Duplicates", str(d)], ["Source", "back"], ["Correct", "✗ no"]]}, None, ["inputs", "checks", "layers", "logs"])

    sql("CREATE TABLE dark.ok (event_id STRING, event_ts TIMESTAMP, amount DOUBLE) USING delta")
    sql("CREATE TABLE dark.slo_log (slo STRING, breached_at STRING, recovered_at STRING, minutes INT) USING delta")
    merge = "MERGE INTO dark.ok t USING batch s ON t.event_id = s.event_id WHEN NOT MATCHED THEN INSERT *"
    SLO = timedelta(hours=2)
    alerts, breach = [], None
    for h in range(12):
        clock = base + timedelta(hours=h + 1, minutes=5)
        batches = [delivery(h)] + ([[e for e in events if e[1].hour == x] for x in OUT_H] if h == 9 else [])   # the same hand re-runs happen
        for b in batches:
            if b:
                spark.createDataFrame(b, SCH).createOrReplaceTempView("batch")
                sql(merge)
        newest = R.val("SELECT max(event_ts) FROM dark.ok").replace(tzinfo=timezone.utc)
        lag = clock - newest
        if lag > SLO and breach is None:
            breach = clock
            alerts.append(f"{clock:%H:%M} freshness SLO breached: newest order is {int(lag.total_seconds() // 60)} min old (limit {int(SLO.total_seconds() // 60)})")
            R.log("ERROR", alerts[-1])
        elif lag <= SLO and breach is not None:
            mins = int((clock - breach).total_seconds() // 60)
            sql(f"INSERT INTO dark.slo_log VALUES ('orders fresh within 2 h', '{breach:%H:%M}', '{clock:%H:%M}', {mins})")
            alerts.append(f"{clock:%H:%M} freshness SLO recovered after {mins} min")
            R.log("INFO", alerts[-1])
            breach = None
    view, got = hourly("dark.ok")
    d = dupes("dark.ok")
    slo_rows = R.val("SELECT count(*) FROM dark.slo_log")
    R.pstep("dark", "Right fix: a freshness SLO that alerts once, and loads that absorb the flood",
            f"Alert on what matters: 'the newest order is more than 2 hours old' (a freshness service level objective, SLO). That fires once when it is breached and once when it recovers: {len(alerts)} alerts instead of {len(pages)} pages. Every load is a MERGE on event_id, so the flood and the hand re-runs can overlap safely: {d} duplicates. Every hour lands on its own hour by event time. The breach itself is recorded honestly in an SLO log, not hidden.",
            "every hour:\n    MERGE INTO orders USING batch ON event_id WHEN NOT MATCHED THEN INSERT *\n    lag = now - max(event_ts)\n    if lag > 2 h and not breached: alert('breached'); breached = now\n    if lag <= 2 h and breached:    alert('recovered'); slo_log(breached, now)",
            [chk("one alert per incident", f"{len(alerts)} alerts (breach + recovery)", len(alerts) <= 2), chk("no order counted twice", f"{d} duplicates", d == 0),
             chk("every hour = source", f"{sum(1 for h in range(12) if got.get(h, 0) == truth_h[h])} of 12 hours", all(got.get(h, 0) == truth_h[h] for h in range(12))),
             chk("SLO breach recorded", f"{slo_rows} row in slo_log", slo_rows == 1)],
            {**view, "slo_log": R.table("dark.slo_log")}, {"tiles": [["Alerts", str(len(alerts))], ["Duplicates", str(d)], ["SLO breach", f"{R.val('SELECT max(minutes) FROM dark.slo_log')} min"], ["Correct", "✓ yes"]]},
            None, ["inputs", "checks", "layers", "logs"])

    # =================================================================== 14. reconciliation mismatch
    N = 10404
    src = [(f"O-{i:05d}", f"C-{i % 3000:04d}", f"2026-10-{20 + i % 7:02d}", f"S-{i % 12 + 1:02d}", round(100 + i * 0.01, 2)) for i in range(N)]
    src += [(f"O-9{i:04d}", "C-0100", "2026-10-26", "S-13", 75.0 + i) for i in range(8)]                       # a store opened this week
    for k, i in enumerate(range(6)):                                                                            # same customer, day and amount, different orders
        o = src[100 + i * 37]
        src.append((f"O-8{k:04d}", o[1], o[2], o[3], o[4]))
    S = "order_id string, customer_id string, d string, store_id string, amount double"
    spark.createDataFrame(src, S).selectExpr("order_id", "customer_id", "to_date(d) AS order_date", "store_id", "amount").write.format("delta").saveAsTable("rc.bronze")
    spark.createDataFrame([(f"S-{i:02d}", ["North", "South", "East", "West"][i % 4]) for i in range(1, 13)], "store_id string, region string").write.format("delta").saveAsTable("rc.stores")
    n_src, s_src = len(src), round(sum(x[4] for x in src), 2)
    DEDUPE_BUG = "row_number() OVER (PARTITION BY customer_id, order_date, amount ORDER BY order_id)"
    DEDUPE_OK = "row_number() OVER (PARTITION BY order_id ORDER BY order_id)"
    sql(f"CREATE TABLE rc.silver USING delta AS SELECT order_id, customer_id, order_date, store_id, amount FROM (SELECT *, {DEDUPE_BUG} rn FROM rc.bronze) WHERE rn = 1")
    sql("CREATE TABLE rc.gold USING delta AS SELECT o.*, s.region FROM rc.silver o JOIN rc.stores s USING (store_id)")
    n_gold, s_gold = R.val("SELECT count(*) FROM rc.gold"), round(R.val("SELECT sum(amount) FROM rc.gold"), 2)
    R.log("WARN", f"source says {n_src:,} orders, gold has {n_gold:,}")
    R.pstep("recon", "What you see: the source says one number, gold says another",
            f"The order system's own report says {n_src:,} orders worth {money(s_src)} this week. Gold says {n_gold:,} orders worth {money(s_gold)}. {n_src - n_gold} orders are missing somewhere between the source and the dashboard, and every job reported success.",
            f"silver = dedupe(bronze)          -- keeps one row per {DEDUPE_BUG.split('BY ')[1].split(' ORDER')[0]}\ngold   = silver JOIN stores USING (store_id)   -- adds region",
            [chk("gold orders = source orders", f"{n_gold:,} vs {n_src:,}", n_gold == n_src), chk("gold revenue = source revenue", f"{money(s_gold)} vs {money(s_src)}", s_gold == s_src)],
            {"gold vs source": {"cols": ["", "orders", "revenue"], "rows": [["source", f"{n_src:,}", money(s_src)], ["gold", f"{n_gold:,}", money(s_gold)]], "count": 2}},
            {"tiles": [["Source", f"{n_src:,}"], ["Gold", f"{n_gold:,}"], ["Missing", str(n_src - n_gold)], ["Correct", "✗ no"]]})
    pct = 100 * (n_src - n_gold) / n_src
    R.log("INFO", f"reconciliation within 1% tolerance ({pct:.2f}%): PASS")
    R.pstep("recon", "Naive fix: 'close enough', a 1% tolerance",
            f"A reconciliation check with a 1% tolerance passes: the gap is {pct:.2f}%. It is green every day from now on. But those {n_src - n_gold} orders are real sales worth {money(s_src - s_gold)} this week, and the causes are still in the pipeline, losing orders every day. A tolerance is for known, explained differences (like orders still in flight at the cut-off), not for differences nobody has explained.",
            "assert abs(source_count - gold_count) / source_count < 0.01   # passes",
            [chk("gold within 1% of source", f"{pct:.2f}%", True), chk("every missing order explained", f"{n_src - n_gold} unexplained", False)],
            {"gold vs source": {"cols": ["", "orders", "revenue"], "rows": [["source", f"{n_src:,}", money(s_src)], ["gold", f"{n_gold:,}", money(s_gold)]], "count": 2}},
            {"tiles": [["Source", f"{n_src:,}"], ["Gold", f"{n_gold:,}"], ["Check", "✓ green"], ["Explained", "✗ no"]]})

    def hops(silver, gold):
        hs = [("source", n_src, s_src), ("bronze", R.val("SELECT count(*) FROM rc.bronze"), round(R.val("SELECT sum(amount) FROM rc.bronze"), 2)),
              ("silver", R.val(f"SELECT count(*) FROM {silver}"), round(R.val(f"SELECT sum(amount) FROM {silver}"), 2)),
              ("gold", R.val(f"SELECT count(*) FROM {gold}"), round(R.val(f"SELECT sum(amount) FROM {gold}"), 2))]
        out, prev = [], None
        for name, c, s in hs:
            out.append([name, f"{c:,}", money(s), "" if prev is None else (f"{c - prev:+d}" if c != prev else "0")])
            prev = c
        return hs, {"count and sum at every hop": {"cols": ["hop", "orders", "revenue", "change"], "rows": out, "count": len(out)}}
    hs_before, hop_view = hops("rc.silver", "rc.gold")
    lost_silver = sql("SELECT b.order_id, b.customer_id, b.order_date, b.amount FROM rc.bronze b LEFT ANTI JOIN rc.silver s USING (order_id) ORDER BY 1")
    lost_gold = sql("SELECT s.order_id, s.store_id, s.amount FROM rc.silver s LEFT ANTI JOIN rc.gold g USING (order_id) ORDER BY 1")
    n_ls, n_lg = lost_silver.count(), lost_gold.count()
    R.log("ERROR", f"bronze → silver lost {n_ls} orders (dedupe key); silver → gold lost {n_lg} orders (store_id S-13 not in stores)")
    sql(f"CREATE TABLE rc.silver2 USING delta AS SELECT order_id, customer_id, order_date, store_id, amount FROM (SELECT *, {DEDUPE_OK} rn FROM rc.bronze) WHERE rn = 1")
    sql("CREATE TABLE rc.gold2 USING delta AS SELECT o.*, coalesce(s.region, 'Unassigned') AS region FROM rc.silver2 o LEFT JOIN rc.stores s USING (store_id)")
    hs_after, hop_after = hops("rc.silver2", "rc.gold2")
    ok_all = all(c == n_src and s == s_src for _, c, s in hs_after)
    R.log("INFO", "after fixes: every hop " + ", ".join(f"{h} {c:,}" for h, c, _ in hs_after))
    R.pstep("recon", "Right fix: count and sum at every hop, then drill into the hop that lost rows",
            f"Count and sum the same orders at every hop: source, bronze, silver, gold. The table shows exactly where rows disappear: bronze to silver lost {n_ls} (the dedupe key was customer, day and amount, so different orders with the same values were merged), and silver to gold lost {n_lg} (an inner join to stores, and store S-13 opened this week). An anti-join lists the exact orders lost at each hop. Fix both (dedupe on order_id; left join with an 'Unassigned' region and an alert for the missing store), and every hop matches.",
            "for hop in [source, bronze, silver, gold]:\n    record(hop, count(*), sum(amount))\n\n-- which orders did a hop lose?\nSELECT * FROM bronze LEFT ANTI JOIN silver USING (order_id)\n\n-- fixes\n" + DEDUPE_OK + "\nsilver LEFT JOIN stores ... coalesce(region, 'Unassigned')",
            [chk("bronze → silver", f"lost {n_ls} before, 0 after", True), chk("silver → gold", f"lost {n_lg} before, 0 after", True),
             chk("every hop: same count and sum as the source", "all match" if ok_all else "differ", ok_all)],
            {"before the fix": hop_view["count and sum at every hop"], "after the fix": hop_after["count and sum at every hop"],
             "lost at silver": tbl(lost_silver, 6), "lost at gold": tbl(lost_gold, 8)},
            {"tiles": [["Source", f"{n_src:,}"], ["Gold", f"{hs_after[-1][1]:,}"], ["Missing", str(n_src - hs_after[-1][1])], ["Correct", "✓ yes"]]}, None, ["inputs", "checks", "layers", "logs"])

    # =================================================================== 15. time zones and daylight saving
    STORES = {"S-IN": "Asia/Kolkata", "S-LDN": "Europe/London"}
    local_sales = [("S-IN", "2026-10-26 11:00", 400.0, None), ("S-IN", "2026-10-26 23:30", 650.0, None), ("S-IN", "2026-10-27 03:00", 220.0, None),
                   ("S-IN", "2026-10-27 12:15", 900.0, None), ("S-LDN", "2026-10-24 00:30", 120.0, 0), ("S-LDN", "2026-10-24 18:00", 300.0, None),
                   ("S-LDN", "2026-10-25 01:30", 80.0, 0), ("S-LDN", "2026-10-25 01:30", 95.0, 1), ("S-LDN", "2026-10-26 23:40", 60.0, None)]
    sales = []
    for i, (st, lt, amt, fold) in enumerate(local_sales):
        dt = datetime.strptime(lt, "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo(STORES[st]), fold=fold or 0)
        sales.append((f"T-{i + 1}", st, dt.astimezone(timezone.utc).replace(tzinfo=None), amt, lt + (" (" + dt.tzname() + ")")))
    spark.createDataFrame([(a, b, c, d) for a, b, c, d, _ in sales], "sale_id string, store_id string, ts_utc timestamp, amount double").write.format("delta").saveAsTable("tz.sales")
    spark.createDataFrame(list(STORES.items()), "store_id string, tz string").write.format("delta").saveAsTable("tz.stores")
    till = {}
    for _, st, _, amt, lt in sales:
        k = (st, lt[:10])
        till[k] = till.get(k, 0) + amt

    def compare(q):
        got = {(r.store_id, str(r.day)): r.rev for r in sql(q).collect()}
        keys = sorted(set(got) | set(till))
        ok = sum(1 for k in till if got.get(k) == till[k])
        return {"daily totals vs the till report": {"cols": ["store", "day", "pipeline", "till", "match"],
                                                    "rows": [[k[0], k[1], money(got.get(k, 0)), money(till.get(k, 0)), "✓" if got.get(k) == till.get(k) else "✗"] for k in keys], "count": len(keys)}}, ok, len(till)
    sales_view = {"sales (as stored, UTC)": {"cols": ["sale_id", "store", "ts_utc", "local time at the till", "amount"],
                                            "rows": [[a, b, str(c), e, str(d)] for a, b, c, d, e in sales], "count": len(sales)}}
    Q1 = "SELECT store_id, to_date(ts_utc) AS day, sum(amount) AS rev FROM tz.sales GROUP BY 1, 2"
    view, ok, n = compare(Q1)
    R.log("WARN", f"daily totals by UTC date: {ok} of {n} store-days match the tills")
    R.pstep("tz", "What you see: late-night sales land on the wrong day",
            f"Two shops: Pune (India, UTC+5:30) and London (UTC+1 in summer, UTC+0 from 25 Oct 2026, when the clocks go back). Timestamps are stored in UTC, which is right. But the daily report groups by the UTC date, so a sale at 03:00 in Pune on 27 Oct (21:30 UTC on the 26th) is counted on the 26th, and a sale at 00:30 in London on 24 Oct is counted on the 23rd. Only {ok} of {n} store-days match the shops' own till reports.",
            Q1.replace("tz.sales", "sales"),
            [chk("every store-day matches its till", f"{ok} of {n}", ok == n)],
            {**view, **sales_view}, {"tiles": [["Store-days right", f"{ok} of {n}"], ["Pune", "UTC+5:30"], ["London", "BST → GMT 25 Oct"], ["Correct", "✗ no"]]})
    Q2 = "SELECT store_id, to_date(ts_utc + INTERVAL 5 HOURS 30 MINUTES) AS day, sum(amount) AS rev FROM tz.sales GROUP BY 1, 2"
    view, ok, n = compare(Q2)
    R.log("WARN", f"after adding +5:30 everywhere: {ok} of {n} store-days match")
    R.pstep("tz", "Naive fix: add +5:30 somewhere",
            f"'Our business is in India, add five and a half hours.' Pune's days are now right, and some of London's happen to come out right too. But the London sale at 23:40 on 26 Oct (23:40 UTC) is pushed to 27 Oct, a day the London till never traded on. +5:30 is London's offset on no day of the year. {ok} of {n} store-days match. Hard-coded offsets break the day a second time zone, or a daylight-saving change, appears.",
            Q2.replace("tz.sales", "sales"),
            [chk("every store-day matches its till", f"{ok} of {n}", ok == n)],
            view, {"tiles": [["Store-days right", f"{ok} of {n}"], ["Pune", "fixed"], ["London", "broken"], ["Correct", "✗ no"]]})
    Q3 = """SELECT s.store_id, to_date(from_utc_timestamp(s.ts_utc, st.tz)) AS day, sum(s.amount) AS rev
FROM tz.sales s JOIN tz.stores st USING (store_id) GROUP BY 1, 2"""
    view, ok, n = compare(Q3)
    ldn25 = R.val("SELECT count(*) FROM tz.sales s JOIN tz.stores st USING (store_id) WHERE st.store_id = 'S-LDN' AND to_date(from_utc_timestamp(s.ts_utc, st.tz)) = '2026-10-25'")
    R.log("INFO", f"business day from each store's own time zone: {ok} of {n} store-days match")
    R.pstep("tz", "Right fix: store UTC, convert at the edge with each store's own time zone",
            f"Keep UTC in storage. Give each store a named time zone (Asia/Kolkata, Europe/London, never a fixed offset) and define the business day explicitly: the calendar day at the store's till. Convert only when you compute that day. The time-zone database knows that London moved from BST to GMT on 25 Oct 2026, so that day had 25 hours and the two sales at 01:30 (one before the change, one after) both count on the 25th ({ldn25} sales). {ok} of {n} store-days match the tills.",
            Q3.replace("tz.sales", "sales").replace("tz.stores", "stores"),
            [chk("every store-day matches its till", f"{ok} of {n}", ok == n), chk("both 01:30 London sales on 25 Oct", f"{ldn25} sales", ldn25 == 2)],
            {**view, "stores": R.table("tz.stores")}, {"tiles": [["Store-days right", f"{ok} of {n}"], ["Pune", "✓"], ["London", "✓ incl. 25-hour day"], ["Correct", "✓ yes"]]})

    # =================================================================== 16. two writers at once
    pq = str(Path(wh) / "points_parquet")
    spark.createDataFrame([("A-1", 150)], "account string, points int").write.mode("overwrite").parquet(pq)
    START, ADD_A, ADD_B = 150, 100, 50
    want = START + ADD_A + ADD_B

    def read_points():
        return {r.account: r.points for r in spark.read.parquet(pq).collect()}

    def write_points(d):
        spark.createDataFrame(list(d.items()), "account string, points int").write.mode("overwrite").parquet(pq)
    bar = threading.Barrier(2)
    seen = {}

    def job(name, add):
        cur = read_points()            # read the current balance
        seen[name] = cur["A-1"]
        bar.wait()                     # both have read before either writes
        cur["A-1"] += add
        with lock_w:
            write_points(cur)
    lock_w = threading.Lock()          # only to stop two Spark writes to one folder colliding mid-file; the lost update happens anyway
    ts = [threading.Thread(target=job, args=("job A", ADD_A)), threading.Thread(target=job, args=("job B", ADD_B))]
    [t.start() for t in ts]
    [t.join() for t in ts]
    got = read_points()["A-1"]
    R.log("ERROR" if got != want else "INFO", f"both jobs succeeded; balance {got}, expected {want}")
    R.pstep("writers", "What you see: two jobs both succeed, and one change is lost",
            f"Account A-1 has {START} loyalty points, stored as plain Parquet files. Two jobs run at the same time: the order job adds {ADD_A}, the referral job adds {ADD_B}. Each reads the balance ({seen.get('job A')} and {seen.get('job B')}), adds its points, and overwrites the files. Both succeed. The balance is {got}, not {want}: whichever wrote last erased the other's change. Nothing failed, so nothing alerts. This is a lost update.",
            "def job(add):\n    points = spark.read.parquet(path)          # read\n    points = points + add                      # modify\n    points.write.mode('overwrite').parquet(path)   # write\n\n# job A (+100) and job B (+50) at the same time",
            [chk("balance = 150 + 100 + 50", f"{got}", got == want), chk("a failure was reported", "none: both succeeded", False)],
            {"points": tbl(spark.read.parquet(pq))}, {"tiles": [["Balance", str(got)], ["Expected", str(want)], ["Errors", "0"], ["Correct", "✗ no"]]})

    write_points({"A-1": START})
    flag = Path(wh) / "points.lock"
    bar2 = threading.Barrier(2)
    proceeded = []

    def job_lock(name, add):
        free = not flag.exists()       # check the flag ...
        bar2.wait()                    # ... both check before either creates it
        if not free:
            return
        flag.write_text(name)          # ... then take the 'lock'
        proceeded.append(name)
        cur = read_points()
        bar.wait()
        cur["A-1"] += add
        with lock_w:
            write_points(cur)
        flag.unlink(missing_ok=True)   # release the 'lock'
    bar = threading.Barrier(2)
    ts = [threading.Thread(target=job_lock, args=("job A", ADD_A)), threading.Thread(target=job_lock, args=("job B", ADD_B))]
    [t.start() for t in ts]
    [t.join() for t in ts]
    got = read_points()["A-1"]
    R.log("ERROR" if got != want else "INFO", f"flag-file lock: {len(proceeded)} job(s) passed the check; balance {got}, expected {want}")
    R.pstep("writers", "Naive fix: a lock file",
            f"'Write a lock file before you start; skip the run if it exists.' Checking for the file and creating it are two separate steps, so two jobs that start together both see no file, both create it, and both carry on: {len(proceeded)} jobs passed the check. The balance is {got} again. And if a job ever crashes before deleting its lock file, every later run is blocked until someone deletes it by hand.",
            "if not exists('points.lock'):     # check\n    create('points.lock')         # then act: another job can slip in between\n    job(add)\n    delete('points.lock')         # never reached if the job crashes",
            [chk("balance = 150 + 100 + 50", f"{got}", got == want), chk("only one job at a time", f"{len(proceeded)} passed the check", len(proceeded) == 1)],
            {"points": tbl(spark.read.parquet(pq))}, {"tiles": [["Balance", str(got)], ["Expected", str(want)], ["Jobs through", str(len(proceeded))], ["Correct", "✗ no"]]})

    conflicts, attempts_log, got = 0, [], None
    upd = "UPDATE wr.points SET points = points + {add} WHERE account = 'A-1'"
    for attempt in range(25):
        sql("DROP TABLE IF EXISTS wr.points")
        sql("CREATE TABLE wr.points (account STRING, points INT) USING delta")
        sql(f"INSERT INTO wr.points VALUES ('A-1', {START})")
        b3 = threading.Barrier(2)
        log = []

        def job_delta(name, add):
            b3.wait()
            for tries in range(1, 6):
                try:
                    spark.sql(upd.format(add=add))
                    log.append((name, tries, "committed"))
                    return
                except Exception as e:  # noqa: BLE001
                    log.append((name, tries, short_err(e, ["ConcurrentAppendException", "Concurrent", "conflict"])[:150]))
                    time.sleep(0.2 * tries)        # back off, then re-read and re-apply
        ts = [threading.Thread(target=job_delta, args=("job A", ADD_A)), threading.Thread(target=job_delta, args=("job B", ADD_B))]
        [t.start() for t in ts]
        [t.join() for t in ts]
        failed = [x for x in log if x[2] != "committed"]
        got = R.val("SELECT points FROM wr.points")
        if failed:
            conflicts, attempts_log = len(failed), log
            break
        attempts_log = log
    for name, tries, res in attempts_log:
        R.log("INFO" if res == "committed" else "WARN", f"{name}, try {tries}: {res}")
    R.pstep("writers", "Right fix: optimistic concurrency (Delta) and a retry",
            f"On Delta, each job writes its new files and then tries to create the next commit. If another job committed first and changed the files this job read, the commit is refused with a conflict error instead of silently overwriting. The job backs off, re-reads, re-applies its change, and commits. Recorded: {conflicts} conflict(s), then a successful retry; the balance is {got}. Better still, avoid the race: give each table one owner job, or have writers append events (+{ADD_A}, +{ADD_B}) and sum them, so they never update the same row.",
            "def job(add):\n    for attempt in range(5):\n        try:\n            spark.sql(f\"UPDATE points SET points = points + {add} WHERE account = 'A-1'\")\n            return\n        except ConcurrentModificationException:   # Delta refused the commit\n            sleep(backoff(attempt))                 # then re-read and re-apply",
            [chk("balance = 150 + 100 + 50", f"{got}", got == want), chk("conflict detected, not hidden", f"{conflicts} conflict(s) seen", conflicts > 0),
             chk("both changes landed", "yes" if got == want else "no", got == want)],
            {"points": R.table("wr.points"), "attempts": {"cols": ["job", "try", "result"], "rows": [[a, str(b), c] for a, b, c in attempts_log], "count": len(attempts_log)}},
            {"tiles": [["Balance", str(got)], ["Expected", str(want)], ["Conflicts", str(conflicts)], ["Correct", "✓ yes" if got == want else "✗ no"]]}, "wr.points", ["inputs", "checks", "layers", "logs"])

    # =================================================================== 17. skew
    spark.conf.set("spark.sql.adaptive.enabled", "false")
    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")      # customers is big in real life: no broadcast
    spark.range(0, 1_200_000).selectExpr("id AS order_id", "CASE WHEN id % 10 < 7 THEN 'C-MARKETPLACE' ELSE format_string('C-%06d', id % 200000) END AS customer_id",
                                          "cast(id % 97 AS DOUBLE) AS amount").write.format("delta").saveAsTable("sk.orders")
    spark.range(0, 200000).selectExpr("format_string('C-%06d', id) AS customer_id", "CASE WHEN id % 3 = 0 THEN 'Gold' ELSE 'Standard' END AS tier") \
        .union(spark.createDataFrame([("C-MARKETPLACE", "Partner")], "customer_id string, tier string")).write.format("delta").saveAsTable("sk.customers")

    def measure(df, parts):
        spark.conf.set("spark.sql.shuffle.partitions", str(parts))
        joined = df()
        a = time.perf_counter()
        res = joined.agg(F.count("*").alias("n"), F.sum("amount").alias("s")).first()
        ms = int((time.perf_counter() - a) * 1000)
        per = sorted([r["count"] for r in df().withColumn("p", F.spark_partition_id()).groupBy("p").count().collect()])
        med = per[len(per) // 2]
        return {"ms": ms, "max": per[-1], "med": med, "n": res["n"], "s": res["s"], "parts": parts, "per": per}

    plain = lambda: spark.table("sk.orders").join(spark.table("sk.customers"), "customer_id")  # noqa: E731
    m1 = measure(plain, 8)
    spark.conf.set("spark.sql.shuffle.partitions", "8")

    def skew_view(m):
        return {"rows per join task": {"cols": ["task", "rows"], "rows": [[str(i + 1), f"{v:,}"] for i, v in enumerate(sorted(m["per"], reverse=True)[:10])], "count": len(m["per"])}}
    R.log("WARN", f"join: {m1['parts']} tasks, biggest {m1['max']:,} rows, median {m1['med']:,}; {m1['ms']} ms")
    R.pstep("skew", "What you see: one task does most of the work",
            f"1.2 million orders joined to 200,000 customers. One account (a marketplace partner) places 70% of all orders. A join sends every row with the same key to the same task, so one of {m1['parts']} tasks gets {m1['max']:,} rows while the median task gets {m1['med']:,}. On a cluster with a core for every task, the job finishes only when the biggest task does, and that task holds {100 * m1['max'] // m1['n']}% of all rows: the 'one task runs for an hour while 199 finish in a minute' story. (This laptop has two cores, so tasks queue anyway and wall time, {m1['ms']} ms, barely shows the problem; the task sizes do.)",
            "orders.join(customers, 'customer_id')     # sort-merge join, 8 shuffle partitions, AQE off",
            [chk("biggest task within 3× the median", f"{m1['max']:,} vs {m1['med']:,} ({m1['max'] / max(m1['med'], 1):.0f}×)", m1["max"] <= 3 * m1["med"])],
            skew_view(m1), {"tiles": [["Biggest task", f"{m1['max']:,}"], ["Median task", f"{m1['med']:,}"], ["Biggest share", f"{100 * m1['max'] // m1['n']}%"], ["Even", "✗ no"]]})
    m2 = measure(plain, 64)
    R.log("WARN", f"64 partitions: biggest {m2['max']:,} rows, median {m2['med']:,}; {m2['ms']} ms")
    R.pstep("skew", "Naive fix: more partitions (or more machines)",
            f"Raising shuffle partitions from 8 to 64 spreads the other customers thinner, but every row for the marketplace account still hashes to one task: the biggest task still has {m2['max']:,} rows ({100 * m2['max'] // m2['n']}% of all rows), now against a median of {m2['med']:,}. More executors would only add idle workers waiting for that same task.",
            "spark.conf.set('spark.sql.shuffle.partitions', 64)\norders.join(customers, 'customer_id')",
            [chk("biggest task within 3× the median", f"{m2['max']:,} vs {m2['med']:,}", m2["max"] <= 3 * m2["med"])],
            skew_view(m2), {"tiles": [["Biggest task", f"{m2['max']:,}"], ["Median task", f"{m2['med']:,}"], ["Biggest share", f"{100 * m2['max'] // m2['n']}%"], ["Even", "✗ no"]]})
    SALT = 16
    hot = [r.customer_id for r in sql("SELECT customer_id FROM sk.orders GROUP BY 1 HAVING count(*) > 0.1 * (SELECT count(*) FROM sk.orders)").collect()]

    def salted():
        o = spark.table("sk.orders").withColumn("salt", F.when(F.col("customer_id").isin(hot), F.col("order_id") % SALT).otherwise(0))
        c = spark.table("sk.customers").withColumn("salts", F.when(F.col("customer_id").isin(hot), F.sequence(F.lit(0), F.lit(SALT - 1))).otherwise(F.array(F.lit(0)))) \
            .withColumn("salt", F.explode("salts")).drop("salts")
        return o.join(c, ["customer_id", "salt"])
    m3 = measure(salted, 8)
    same = m3["n"] == m1["n"] and m3["s"] == m1["s"]
    R.log("INFO", f"salted join (hot keys: {', '.join(hot)}): biggest {m3['max']:,} rows, median {m3['med']:,}; {m3['ms']} ms")
    R.pstep("skew", "Right fix: split the hot key (salting), or let AQE do it",
            f"Find the hot keys (here, any customer with more than 10% of orders: {', '.join(hot)}). Give each hot-key order a 'salt' from 0 to {SALT - 1}, copy the hot customer's row {SALT} times (one per salt), and join on customer plus salt. The hot key's rows now spread over many tasks: biggest {m3['max']:,} rows ({100 * m3['max'] // m3['n']}% of all rows), median {m3['med']:,}, and the result is identical ({m3['n']:,} rows). On Spark 3 and Databricks, adaptive query execution (AQE) skew-join handling does this split for you when it can; see the Spark internals scene. Broadcasting the small side, when it is small, avoids the shuffle altogether. Measured wall times on this two-core laptop (plain {m1['ms']} ms, 64 partitions {m2['ms']} ms, salted {m3['ms']} ms) do not show the gain, because two cores run tasks two at a time whatever their size; the even task sizes are what pay off on a cluster.",
            f"hot = keys with more than 10% of rows        # {', '.join(hot)}\norders    = orders.withColumn('salt', when(isin(hot), order_id % {SALT}).otherwise(0))\ncustomers = customers.withColumn('salt', explode(when(isin(hot), sequence(0, {SALT - 1})).otherwise(array(0))))\norders.join(customers, ['customer_id', 'salt'])",
            [chk("biggest task within 3× the median", f"{m3['max']:,} vs {m3['med']:,}", m3["max"] <= 3 * m3["med"]), chk("same result as the plain join", f"{m3['n']:,} rows", same)],
            skew_view(m3), {"tiles": [["Biggest task", f"{m3['max']:,}"], ["Median task", f"{m3['med']:,}"], ["Biggest share", f"{100 * m3['max'] // m3['n']}%"], ["Even", "✓ yes"]]})
    spark.conf.set("spark.sql.adaptive.enabled", "true")
    spark.conf.unset("spark.sql.autoBroadcastJoinThreshold")
    spark.conf.set("spark.sql.shuffle.partitions", "2")

    # =================================================================== 18. personal data leak
    spark.createDataFrame([("C-1", "Asha Rao", "+91 98200 11234", "+91 98200 55678", "Pune"), ("C-2", "Ravi Iyer", "+91 99300 22345", None, "Delhi"),
                           ("C-3", "Meera Shah", "+91 97400 33456", "+91 97400 99012", "Pune")],
                          "customer_id string, name string, phone string, alt_phone string, city string").write.format("delta").saveAsTable("pii.customers")
    tags = {"customer_id": "none", "name": "pii", "phone": "pii", "city": "none"}     # alt_phone was added last week, untagged
    ROLES = {"analyst": False, "support": True}                                          # can this role see personal data?
    audit = []

    def query_as(role, q, src="pii.customers"):
        audit.append([role, q.replace(src, "customers")])
        return sql(q.replace(src, src if role is None else f"pii.customers_for_{role}"))
    q = "SELECT customer_id, name, phone, alt_phone, city FROM pii.customers"
    leaked = sql(q)
    R.log("INFO", "analyst ran: " + q.replace("pii.", ""))
    R.pstep("pii", "What you see: an analyst can read every phone number",
            "The analyst needs customers per city. The table has names and phone numbers, and last week a developer added alt_phone. Analysts query the table directly, so they see everything. Nobody knows who has looked at what: there is no record of the query.",
            q.replace("pii.", "") + "    -- as an analyst",
            [chk("phones hidden from analysts", "visible", False), chk("every column has a sensitivity tag", "alt_phone has none", False), chk("audit shows who saw what", "nothing recorded", False)],
            {"what the analyst sees": tbl(leaked)})
    access = {"analyst": False}
    err = ""
    try:
        if not access["analyst"]:
            raise PermissionError("analyst has no access to customers")
    except PermissionError as e:
        err = str(e)
    R.log("ERROR", f"analyst query refused: {err}")
    R.pstep("pii", "Naive fix: take the analyst's access away",
            f"The leak is closed, and so is the analyst's work: '{err}'. Counting customers per city needed no personal data at all. The team will ask for the access back, someone will grant it in a hurry, and alt_phone is still untagged for the next person.",
            "REVOKE SELECT ON customers FROM analysts",
            [chk("phones hidden from analysts", "no access at all", True), chk("analyst can count customers per city", "refused", False),
             chk("every column has a sensitivity tag", "alt_phone has none", False), chk("audit shows who saw what", "nothing recorded", False)],
            {"what the analyst sees": {"cols": ["error"], "rows": [[err]], "count": 1}})
    cols = spark.table("pii.customers").columns
    untagged = [c for c in cols if c not in tags]
    R.log("ERROR", f"deploy blocked: column(s) without a sensitivity tag: {', '.join(untagged)}")
    tags["alt_phone"] = "pii"                                                                        # the PR that tags it
    R.log("INFO", "tag added by PR: alt_phone = pii; deploy check passed")

    def masked(c):
        return f"CASE WHEN length({c}) > 4 THEN concat('••••• ', right({c}, 4)) END AS {c}" if tags[c] == "pii" else c
    for role, sees in ROLES.items():
        sel = ", ".join(c if sees else masked(c) for c in cols)
        sql(f"CREATE OR REPLACE VIEW pii.customers_for_{role} AS SELECT {sel} FROM pii.customers")
    a_view = query_as("analyst", q)
    s_view = query_as("support", "SELECT customer_id, name, phone FROM pii.customers WHERE customer_id = 'C-1'")
    by_city = query_as("analyst", "SELECT city, count(*) AS customers FROM pii.customers GROUP BY city ORDER BY city")
    a_rows = a_view.collect()
    hidden = all((r.phone or "").startswith("•") for r in a_rows)
    full = s_view.first().phone.startswith("+91")
    for role, qq in audit:
        R.log("INFO", f"audit: {role} ran {qq}")
    R.pstep("pii", "Right fix: tag every column, mask by role, record every read",
            "Three rules. First, the contract tags every column (pii or none), and a deploy check blocks any column without a tag: alt_phone was blocked until a PR tagged it. Second, masking is generated from the tags and is on by default: roles without the right see '••••• 1234', the support team sees the full number. Third, every query is recorded: who, and what they ran. The analyst counts customers per city without ever seeing a phone number. On Databricks, Unity Catalog column masks and the audit log do this; here the same rule is a view per role generated from the tags.",
            "# customers.contract.yaml\ncolumns: {customer_id: none, name: pii, phone: pii, alt_phone: pii, city: none}\n\ndeploy check: every column has a tag, else block\nfor role in roles:\n    CREATE VIEW customers_for_<role> AS SELECT <pii columns masked unless the role may see them> ...\nquery_as(role, sql) -> runs on that role's view and writes an audit row",
            [chk("phones hidden from analysts", "masked" if hidden else "visible", hidden), chk("support sees the full number", "yes" if full else "no", full),
             chk("analyst can count customers per city", f"{by_city.count()} cities", by_city.count() == 2), chk("every column has a sensitivity tag", "all tagged", all(c in tags for c in cols)),
             chk("audit shows who saw what", f"{len(audit)} queries recorded", len(audit) >= 3)],
            {"what the analyst sees": tbl(a_view), "analyst: customers per city": tbl(by_city), "audit": {"cols": ["role", "query"], "rows": audit[-3:], "count": 3}})

    # =================================================================== 19. self-healing at 2 a.m.
    raw = [(f"H-{i:03d}", f"b-{i // 10}", float(100 + i * 3)) for i in range(60)]
    spark.createDataFrame(raw, "order_id string, batch_id string, amount double").write.format("delta").saveAsTable("heal.bronze")
    spark.createDataFrame([r for r in raw if r[1] == "b-5"], "order_id string, batch_id string, amount double").write.format("delta").mode("append").saveAsTable("heal.bronze")   # the source re-sent b-5
    TRUTH = sum(r[2] for r in raw)
    sql("CREATE TABLE heal.silver USING delta AS SELECT * FROM heal.bronze")        # the job appended the re-sent batch too
    CONTRACT = "rules:\n  - name: order_id is unique\n    check: count(*) = count(DISTINCT order_id)\n  - name: revenue = source total\n    check: sum(amount) = source_total"
    chash = hashlib.sha256(CONTRACT.encode()).hexdigest()[:12]

    def health(t):
        dup = R.val(f"SELECT count(*) - count(DISTINCT order_id) FROM {t}")
        rev = R.val(f"SELECT sum(amount) FROM {t}")
        return dup, rev
    dup, rev = health("heal.silver")
    R.log("ERROR", f"02:00 check failed: order_id is unique ({dup} duplicates); revenue {money(rev)} vs {money(TRUTH)}")
    R.log("ERROR", "02:00 PAGE on-call")
    R.pstep("heal", "What you see: a check goes red at 2 a.m.",
            f"At 02:00 the source re-sent batch b-5, and the job appended it again. The uniqueness check on silver fails ({dup} duplicate orders) and revenue reads {money(rev)} instead of {money(TRUTH)}. The on-call engineer is paged. This could be any problem in this lab; the question is what happens next, and who (or what) may change production.",
            CONTRACT,
            [chk("order_id is unique", f"{dup} duplicates", dup == 0), chk("revenue = source total", f"{money(rev)} vs {money(TRUTH)}", rev == TRUTH)],
            {"silver (b-5 rows)": tbl(sql("SELECT * FROM heal.silver WHERE batch_id = 'b-5' ORDER BY order_id"), 20)},
            {"tiles": [["Duplicates", str(dup)], ["Revenue", money(rev)], ["Truth", money(TRUTH)], ["Correct", "✗ no"]]})
    sql("CREATE TABLE heal.silver_auto USING delta AS SELECT * FROM heal.silver")
    bad_contract = CONTRACT.replace("  - name: order_id is unique\n    check: count(*) = count(DISTINCT order_id)\n", "")
    bhash = hashlib.sha256(bad_contract.encode()).hexdigest()[:12]
    dup2, rev2 = health("heal.silver_auto")
    R.log("WARN", "auto-fixer: removed rule 'order_id is unique' (it kept failing); set source_total from silver; checks pass")
    R.pstep("heal", "Naive fix: let an auto-fixer change production directly",
            f"An automated fixer (a script, or an AI agent with production rights) is told 'make the checks pass'. The quickest way is to edit the checks: it deletes the uniqueness rule and recomputes the expected total from silver itself. Every check is now green. The data is still wrong ({dup2} duplicates, {money(rev2)} instead of {money(TRUTH)}), the contract has changed without review, and nobody approved anything.",
            "# what the fixer changed\n" + bad_contract + "\nsource_total = SELECT sum(amount) FROM silver   -- the check now compares silver with itself",
            [chk("order_id is unique (as agreed)", f"{dup2} duplicates", dup2 == 0), chk("revenue = source total (as agreed)", f"{money(rev2)} vs {money(TRUTH)}", rev2 == TRUTH),
             chk("contract unchanged", f"{chash} → {bhash}", False), chk("fix reviewed by a person", "no", False)],
            {"contract after the fix": {"cols": ["line"], "rows": [[l] for l in bad_contract.splitlines()], "count": len(bad_contract.splitlines())}},
            {"tiles": [["Duplicates", str(dup2)], ["Revenue", money(rev2)], ["Checks", "✓ green"], ["Correct", "✗ no"]]})

    RUNBOOKS = {"order_id is unique": "rebuild silver from bronze, keeping one row per order_id"}
    stages = []

    def stage(name, detail, ok=True):
        stages.append([f"02:{len(stages) * 3 + 1:02d}", name, detail, "✓" if ok else "✗"])
        R.log("INFO" if ok else "ERROR", f"{name}: {detail}")
    rebuild = "SELECT order_id, batch_id, amount FROM (SELECT *, row_number() OVER (PARTITION BY order_id ORDER BY batch_id) rn FROM {src}) WHERE rn = 1"
    stage("detect", f"check 'order_id is unique' failed ({dup} duplicates)")
    rb = RUNBOOKS["order_id is unique"]
    stage("triage", f"failed check matched a known runbook: {rb}")
    sql("CREATE TABLE heal.dev_silver USING delta AS " + rebuild.format(src="heal.bronze"))
    stage("fix in dev", "runbook ran on a dev copy built from bronze")
    ddup, drev = health("heal.dev_silver")
    stage("test in dev", f"all contract checks pass in dev ({ddup} duplicates, revenue {money(drev)})", ddup == 0 and drev == TRUTH)
    same_contract = hashlib.sha256(CONTRACT.encode()).hexdigest()[:12] == chash
    stage("gate", f"contract file unchanged ({chash}); only data changes; on-call approval (simulated here)", same_contract)
    v_before = version(spark, "heal.silver")
    spark.sql(rebuild.format(src="heal.bronze")).write.format("delta").mode("overwrite").saveAsTable("heal.silver")
    stage("apply to prod", f"same runbook on prod: silver version {v_before} → {version(spark, 'heal.silver')}; rollback = RESTORE TO VERSION {v_before}")
    spark.createDataFrame([("H-060", "b-6", 280.0)], "order_id string, batch_id string, amount double").createOrReplaceTempView("next_batch")
    sql("INSERT INTO heal.bronze SELECT * FROM next_batch")
    sql("MERGE INTO heal.silver t USING next_batch s ON t.order_id = s.order_id WHEN NOT MATCHED THEN INSERT *")
    TRUTH2 = TRUTH + 280.0
    fdup, frev = health("heal.silver")
    stage("verify on the next run", f"03:00 batch loaded; checks still pass ({fdup} duplicates, revenue {money(frev)})", fdup == 0 and frev == TRUTH2)
    R.pstep("heal", "Right fix: a deterministic runbook with gates; agents propose, gates decide",
            "Self-healing is the normal change process, run fast and automatically. Detect (a check failed), triage (a table maps the failed check to a known runbook), fix in dev first, run the same contract checks there, pass a gate (the contract file must be unchanged, only data may change, and the on-call engineer approves), apply the same runbook to production with a recorded rollback version, and verify on the next run. An AI agent may help with triage or write the proposed fix, but it never edits production or the contract directly; unknown failures still page a person.",
            "detect   -> failed check: 'order_id is unique'\ntriage   -> RUNBOOKS[check]  # known fix, or page a human\nfix_dev  -> run runbook on a dev copy\ntest     -> same contract checks in dev\ngate     -> contract hash unchanged AND human approval\napply    -> same runbook in prod, rollback = RESTORE TO VERSION v\nverify   -> checks pass on the next scheduled run",
            [chk("order_id is unique", f"{fdup} duplicates", fdup == 0), chk("revenue = source total", f"{money(frev)} vs {money(TRUTH2)}", frev == TRUTH2),
             chk("contract unchanged", chash, same_contract), chk("fix tested in dev and approved", "yes", True), chk("verified on the next run", "03:00 run green", fdup == 0)],
            {"run log": {"cols": ["time", "stage", "detail", "ok"], "rows": stages, "count": len(stages)}, "silver": R.table("heal.silver", ["order_id"], 8)},
            {"tiles": [["Duplicates", str(fdup)], ["Revenue", money(frev)], ["Contract", "unchanged"], ["Correct", "✓ yes"]]}, "heal.silver", ["inputs", "checks", "layers", "logs"])
