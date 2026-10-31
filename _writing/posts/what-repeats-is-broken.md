---
title: What repeats is broken
date: 2026-10-31
subject: data
audience: builders
kind: explainer
draft: false
summary: Every pipeline sees the same data more than once: retries, queues that deliver twice, files sent again, backfills and tired re-runs. A pipeline is idempotent when processing the same input twice gives the same result as processing it once. This post shows, with numbers from real recorded runs, how a naive pipeline doubles revenue and the six patterns that make repeats safe.
linkedin: A network timeout sends the same orders file twice. Your pipeline loads it twice, and the revenue tile quietly doubles from ₹1,250 to ₹2,500. Nothing failed, so nothing alerted. Here is why every pipeline sees repeats, and six simple patterns that make a second run harmless.
deeper: /concepts/idempotency/
deeper_label: idempotency, the key concept, with where it lives on each platform
---

An accountant receives an invoice for ₹40,000 and pays it. Next morning the same invoice arrives again, photocopied by someone who wasn't sure the first one went through. A careful accountant checks the invoice number and files the copy. A rushed one pays twice.

Data pipelines get photocopied invoices every day. The question is never *whether* the same data will arrive twice. It is whether your pipeline is the careful accountant or the rushed one.

{{drawing: rep-photocopier}}

## What idempotent means

An operation is **idempotent** when doing it twice has the same effect as doing it once. Pressing a lift button five times still calls one lift. Setting a thermostat to 22 degrees twice still leaves it at 22. Adding ₹40,000 to a balance twice does not.

For a pipeline the rule is simple: **the same input, processed twice, must give the same tables as processing it once.**

## Everything repeats

A repeat is not a rare accident. It is built into how data moves.

1. **Retries after failure.** A job times out after it has actually finished, and the scheduler runs it again.
2. **At-least-once delivery.** Most queues and event streams promise that every message arrives *at least* once. The other half of that promise is that some arrive twice.
3. **The same file sent again.** The sender's network drops, so it sends the file again to be safe.
4. **Backfills.** A bug is fixed, and last week has to be rebuilt over data that is already there.
5. **A re-run by a tired engineer.** It's 2 a.m., the dashboard looks stale, and someone presses "run" one more time.

None of these is a bug in the sender. Each is normal. A pipeline that breaks on a repeat is broken; it just hasn't been found out yet.

## The same file, sent twice

Our DataTwin Studio records a real Spark and Delta Lake run of exactly this story. A clothing shop's orders file, batch `b-0912`, goes through landing, bronze, silver and gold. Then a network timeout makes the sender deliver the same batch a second time. The run is done twice: once with our pipeline, once with a naive one.

{{drawing: rep-naive-vs-safe}}

These are the recorded numbers.

- **First run, both pipelines:** the revenue tile says ₹1,250 for 27 October.
- **Same file again, naive pipeline:** bronze appends the batch again (6 more rows), silver inserts order 1001 a second time, and the dashboard says **₹2,500**. Every job reported success.
- **Same file again, our pipeline:** the loader looks in its run log, sees that batch `b-0912` already succeeded, and adds nothing. Even when silver is run again on purpose, a MERGE on the order id finds the same row and changes nothing. The dashboard still says **₹1,250**.

The naive pipeline didn't crash; it believed every row it was given. Watch both versions step by step in [the DataTwin Studio](/learn/data-platform-sim/).

## The toolbox

There is no single trick. There is a small toolbox, and each tool guards a different door.

{{drawing: rep-toolbox}}

1. **Batch ids and a ledger of what was loaded.** Every delivery gets an id, and a run log table records which ids have been loaded. Before loading, check the ledger. This is the cheapest guard: in the recorded run, no Spark job ran at all for the repeat. It is the heart of [one metadata-driven ingestion framework](/writing/metadata-driven-ingestion/).
2. **MERGE on business keys, not append.** A business key is the thing that makes a row one real thing, such as an order id. MERGE says "update the row with this key if it exists, insert it if not". Run it twice and you still have one row per order.
3. **Overwrite exactly the partition you load.** A daily job takes the date as a parameter and atomically replaces that one day. On Delta Lake this is `replaceWhere`. In the recorded Problem Lab, a re-run of an appending job turned 27 October from ₹849 into ₹1,698. Replacing just that day made it ₹849 again, however many times it ran, and the other 26 days were never touched.
4. **Deduplicate in silver.** Bronze keeps every row as it arrived, duplicates included. Silver keeps one row per business key, chosen by a clear rule, such as the latest event. That split is what [medallion done right](/writing/medallion-done-right/) is about.
5. **Move the watermark only after the write commits.** A watermark is the bookmark that says "I have loaded everything up to here". More on this in the next section.
6. **Idempotency keys on writes to other systems.** When a pipeline calls an API, sends an email or posts a payment, send a key with each request, such as the batch id plus the order id. The other side remembers keys it has seen and ignores a repeat.

## The crash in the middle

The hardest repeat is the one you cause yourself. A job writes its data and then dies before it records that it finished.

{{drawing: rep-crash}}

The order of the steps is the whole trick. Write the data first, in one atomic commit. Only then move the watermark and mark the batch done in the ledger. If the job dies between the two, the bookmark still points at the old place, so the re-run picks up the same batch. Because the write is a MERGE or a partition overwrite, doing it again lands on the same rows. Nothing is lost, and nothing doubles.

Move the watermark first instead, and a crash loses the batch for good.

The Problem Lab recorded a version of this. A job loaded silver, then the cluster was lost before gold. Re-running everything from the top inserted the batch into silver a second time, and gold showed **₹2,400 instead of ₹1,200**. With every step made safe to repeat and a run log, the re-run skipped silver, built gold, and revenue stayed at ₹1,200 even when it was run twice more.

## The same idea in agents

Agents repeat too. A user taps "send" twice. A chat channel delivers the same message twice. A tool call times out, and the agent loop retries it, though the first call may have worked. If that tool issues a refund, the customer is refunded twice.

The fix is the same toolbox in different clothes: give every message and every tool call an id, record it before the action runs, and return the first answer to a repeat. The ledger table in [just use Postgres](/writing/just-use-postgres/) is exactly this.

## Mistakes we see

- **Adding DISTINCT and calling it fixed.** In the recorded Problem Lab, an event stream delivered one event twice and an order had a second event when it was paid. True revenue was ₹2,790; the dashboard said ₹4,770. DISTINCT removes only rows identical in every column, and these weren't, so revenue stayed at ₹4,770. Deduplicate on the business key instead.
- **Reloading everything to make re-runs safe.** It works, but in the Problem Lab it rewrote all 81 rows of all 27 days to change 3, and that cost grows every day. Replace only the partition you load.
- **Reading "today" from the clock inside the job.** Then the job can only ever build today, and a backfill means editing code. Pass the date in as a parameter.
- **Thinking MERGE is free.** The recorded run shows a MERGE that changed nothing still rewrote a file. It is safe for the data, not free. Compare a row hash first and skip unchanged rows.
- **Fixing the past by hand.** In the Problem Lab, a bug dropped ₹5,390 of revenue over five days. Scaling gold by a factor in production got 23 of 27 days right. A backfill, which is just the same safe job run for each day in a loop, got all 27 right.

## The replay test

Here is one check that catches most of the above. In your test environment, or in CI on every change:

1. Load a small, fixed set of input files.
2. Snapshot every table: row counts, sums of the money columns, and a hash of the rows.
3. Load the **same** files again, then run each job once more on top.
4. Snapshot again and compare. Any difference fails the build.

For bonus points, kill the job halfway through one run and check that the re-run still matches.

## Five questions to check your own pipelines

1. If yesterday's file arrived again right now, what would your revenue tile say?
2. Which of your loads append, and what stops them appending the same rows twice?
3. Does each job take its date as a parameter, so a backfill is the same job in a loop?
4. Does your watermark move before or after the write commits?
5. When a job calls another system, does it send a key that system can use to spot a repeat?

The data will arrive twice. Make sure your numbers don't.
