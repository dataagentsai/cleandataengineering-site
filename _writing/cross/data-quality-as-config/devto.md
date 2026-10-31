---
title: Data quality as config, not code
published: false
canonical_url: https://cleandataengineering.ai/writing/data-quality-as-config/
description: Most teams have data quality checks, but they are scattered across notebooks, each written a little differently. A metadata-driven framework moves every rule into a YAML file or a rules table, and one engine runs them at each hop. Bad rows go to quarantine with a reason, results land in a table, and a new dataset is a new file, not new code.
---

*Originally published at [cleandataengineering.ai](https://cleandataengineering.ai/writing/data-quality-as-config/).*


Ask a data team whether they check data quality and they will say yes. Ask where the checks are, and someone opens a notebook. Then another. The null check on `customer_id` is in the orders notebook, copied into the returns notebook, and changed slightly in the payments one.

Nobody can say which rules were in force last Tuesday. Nobody can list every check on one table. When a check fails, it either stops the whole job or quietly removes the rows.

The fix is not more checks. It is moving the checks out of code and into configuration.

## From forty notebooks to one file

Here is the change in one picture.

{{drawing: dq-scattered}}

In a **metadata-driven** framework, the rules are data about your data. They live in one YAML file per dataset, or in a rules table, and nowhere else. A pipeline never writes a check itself. It calls one engine, and the engine reads the rules for that dataset and runs them.

That gives you three things at once:

- **One place to look.** Every rule for `orders` is in `orders.dq.yaml`.
- **One review.** A new rule is a line in a pull request, read by a person, like any other change.
- **One way of running.** Every check behaves the same, logs the same and fails the same, because the same engine runs all of them.

## One rule, written as config

A rule is a few lines. It says what to check, how serious a failure is, what to do with the rows that fail, and who owns it.

{{drawing: dq-rule-card}}

A real file has a handful of them. This is a cut-down version of the file used in the DataTwin Studio data quality run:

```
# datasets/orders.dq.yaml  (owned by the data team; reviewed by pull request)
dataset: orders
owner: sales-data
dq_engine: spark_sql
checks:
  - id: DQ-01
    rule: is_complete
    column: customer_id
    severity: block
    action: quarantine
  - id: DQ-04
    rule: is_contained_in
    column: country
    params: {values: [IN, US, GB, AE, SG]}
    severity: warn
    action: alert
  - id: DQ-06
    rule: row_count_between
    params: {min: 40000, max: 60000}
    severity: block
    action: stop
```

(The recorded run spells *block* as `error`; the idea is the same.)

A loader checks the file and writes it into a small metadata database: one row per rule, plus a **fingerprint** of the whole rule set. A fingerprint is a short hash, so if any rule changes, the fingerprint changes. Every run records the fingerprint it used, so "which rules were in force on 27 October?" has an exact answer.

## The engine at each hop

A **hop** is one step where data moves from one layer to the next, such as bronze to silver. The engine runs at every hop, and it does the same five things each time.

{{drawing: dq-engine-hop}}

1. **Read the rules** for this dataset from the rules table.
2. **Run them** through the bound adapter.
3. **Pass** the good rows on to the next layer.
4. **Quarantine** the rows that break a blocking rule, with the IDs of the rules they broke.
5. **Write the results**: one row per rule per run, with the measured value, pass or fail, and the fingerprint. The dashboard reads that table, and failures send an alert to the owner.

In the recorded run, 50,012 orders arrived in bronze. Five of seven rules failed. 232 rows went to quarantine: 200 with no customer, 12 duplicate orders delivered twice, and 20 negative amounts. Two warnings, a country written as `Ind` and some customers missing from the customer table, raised alerts but kept their rows. 49,780 rows went to silver.

The [medallion post](/writing/medallion-done-right/) covers why quarantine beats a quiet `WHERE` clause. The short version: nothing disappears, and every parked row says why it was parked.

### One interface, many engines

The engine is one **interface**: a fixed set of calls the pipeline makes, such as "run these rules on this table". Behind it sit **adapters**, one per tool that does the real work. The recorded run has two: plain Spark SQL, and Deequ, an open-source library for data checks on Spark. Great Expectations could be a third.

The YAML line `dq_engine` picks the adapter. Change `spark_sql` to `deequ` and the same rules run on Deequ, with no pipeline code changed. In the recording every verdict agreed.

Two lessons came out of building it:

- **An adapter says what it can't do.** Deequ has no check for "this customer exists in the customer table", so the engine sends that one rule to Spark SQL instead of failing.
- **Every adapter must mean the same thing.** Deequ counts *uniqueness* as the share of rows whose value appears exactly once. The Spark SQL adapter had to compute exactly that. Running both side by side is now a test.

## Seven kinds of rule

Almost every check you will write is one of seven types.

{{drawing: dq-rule-types}}

- **Completeness**: is the value there? `customer_id` is never empty.
- **Uniqueness**: does it appear only once? One row per `order_id`.
- **Validity**: is it an allowed value or in range? `amount` is not negative; `country` is a real country code.
- **Referential**: does the parent exist? Every order's customer is in the customer table.
- **Freshness**: did the data arrive on time? Say, the newest order is less than two hours old.
- **Volume**: is the row count about usual? Between 40,000 and 60,000 orders a day.
- **Reconciliation**: do the numbers add up across a hop? Rows in bronze equal rows in silver plus rows in quarantine. In the run above, 50,012 equals 49,780 plus 232.

## Warn or block

Every rule has a severity, and the two rows of the picture decide what it means.

| Severity | On a row rule | On a table rule |
|---|---|---|
| warn | keep the row, raise an alert | publish, raise an alert |
| block | send the row to quarantine | stop the load; the next layer keeps yesterday's data |

On 27 October in the recording, only 19,812 orders arrived instead of about 50,000. The volume rule blocked, so silver kept yesterday's data instead of publishing a third of today's. An anomaly check, which compares today's count with past runs, failed too. A fixed range catches the obvious drop; the history catches a drop that is still inside the range.

## What goes wrong

1. **Rules stay in notebooks "for now".** The framework exists, but half the checks never move. Now there are two places to look, which is worse than one.
2. **Everything blocks.** Every rule is set to block, the load stops twice a week, and someone switches the checks off. Block what would mislead a reader; warn on the rest.
3. **Everything warns.** The opposite failure. Alerts arrive daily and nobody reads them. A warning that never leads to action should be deleted or promoted.
4. **Suggested rules accepted blindly.** Deequ can profile a table and suggest rules. In the recording it suggested that `country` may be `Ind`. Suggestions describe today's data, bugs included, so they go to a draft pull request and a person decides.
5. **A rule loosened to make the job pass.** The rule was right; the data was wrong. Fix the source, then replay the quarantined rows.
6. **Zero rows checked counted as a pass.** An empty table can pass a uniqueness or validity rule, because no row is there to fail it. A check that looked at nothing is an error, not a pass.
7. **No owner per dataset.** An alert with no named owner goes to a shared channel and dies there.

## Six questions to check your own setup

1. Can you list every rule on your most important table without opening a notebook?
2. Could you say which rules were in force on a date last month?
3. Where does a row that fails a check go, and does it carry the reason?
4. Do rows in equal rows out plus rows quarantined, at every hop?
5. Which of your rules would stop a load today, and who is told when one does?
6. How much code does it take to add checks to a new dataset?

If the last answer is more than one new file, start there.

