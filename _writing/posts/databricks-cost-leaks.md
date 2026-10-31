---
title: Your Databricks bill has a leak: 10 cost mistakes we keep seeing
date: 2026-10-31
subject: data
audience: builders
kind: field-note
draft: false
summary: A Databricks bill rarely jumps because of one big decision. It leaks through ten small holes: the wrong kind of compute, clusters left running, tiny files, one slow task, Python where Spark would do, and no tags to say who spent what. This note shows how to spot each one, the fix in plain words, and a ten-minute weekly check.
linkedin: Nobody decides to waste half the Databricks budget. It leaks out through ten small holes, like a cluster left on over the weekend or 3,000 tiny files. Here is how to spot each leak, what fixes it, and a ten-minute check you can run every Monday.
deeper: /learn/data-platform-sim/performance/
deeper_label: Performance stories, every fix measured
---

The finance team sends a message on the first of the month: the Databricks bill went up again, can someone explain? Nobody can. No single person made a big, expensive decision. The money left through a lot of small holes at once.

We see the same holes again and again. Most of them are not exotic tuning problems. They are a cluster nobody turned off, a job running on the wrong kind of compute, or a table made of thousands of tiny files.

This note goes through the ten we see most. For each one: how to spot it, and the fix.

{{drawing: dbx-leaky-bucket}}

## Where the money actually goes

On Databricks you pay mostly for compute: machines running, measured in DBUs (Databricks Units, the unit the price list is written in) plus the cloud provider's charge for the virtual machines. Storage is usually a small part of the bill. So the first question is always the same: **were the machines working, or just sitting there?**

{{drawing: dbx-weekend-bill}}

Our [performance stories](/learn/data-platform-sim/performance/) include one worked example, with example prices rather than a real bill. An all-purpose cluster of 4 nodes is started on Friday evening to debug a job and never stopped. By Monday morning it has run for 63 hours and cost about $139, for a weekend with no new data. The same three nights of real work on job clusters, with auto-termination on the interactive cluster, comes to about $5. Your rates will differ. The shape of the saving is the point.

## The compute leaks

### 1. Interactive compute running scheduled jobs

All-purpose compute is the cluster you attach a notebook to and explore with. Job compute is started by a job and stopped when the job ends, and it is billed at a lower rate. Scheduled jobs that point at an all-purpose cluster pay the higher rate, and they keep that cluster alive between runs.

- **Spot it:** list your scheduled jobs and check what each one runs on. Any job attached to an existing all-purpose cluster is a candidate.
- **Fix:** run scheduled work on job compute, or on serverless compute for jobs where your workspace has it. Keep all-purpose clusters for people.

### 2. Clusters too big, or autoscaling that never shrinks

A cluster sized for last year's biggest backfill now runs every small daily job. Or autoscaling has a minimum so high that the cluster can never get smaller, which is what happened in the weekend example: the minimum was 4, so it stayed at 4.

- **Spot it:** look at the cluster's metrics while a job runs. If the CPUs sit mostly idle, the cluster is bigger than the work.
- **Fix:** start small and let autoscaling grow, with a low minimum. Use cluster policies so nobody can create a 40-node cluster by accident.

### 3. No auto-termination

An interactive cluster with auto-termination off will run until someone remembers it.

- **Spot it:** any all-purpose cluster with auto-termination disabled, or set to many hours.
- **Fix:** set auto-termination to something short, such as 15 to 30 minutes idle, and enforce it with a cluster policy so it cannot be switched off.

### 4. SQL warehouses left on, or sized too big

SQL warehouses are the compute behind dashboards and SQL queries. A large warehouse that never stops, serving a dashboard opened twice a day, is a quiet leak.

- **Spot it:** check each warehouse's size, its auto-stop setting, and how many queries it actually ran last week.
- **Fix:** set a short auto-stop, start at a smaller size and grow only when queries queue. Serverless warehouses start quickly, which makes a short auto-stop painless.

## The data and code leaks

These don't show up as an idle cluster. They show up as a job that takes an hour when it should take five minutes, and you pay for every one of those minutes.

### 5. Small files

A streaming job or a frequent small batch writes thousands of tiny files. Every read must list them, open them and read each file's footer, which costs more than reading the data. The rule we use: flag any table whose **average file is under about 32 MB**.

{{drawing: dbx-small-files}}

- **Spot it:** `DESCRIBE DETAIL` on a Delta table shows the number of files and the total size. Divide one by the other.
- **Fix:** run `OPTIMIZE` to compact them. In our recorded run, 3,000 files of about 7 KB each became one file, and a store revenue query went from 1.4 seconds to 235 milliseconds. Then prevent it: write bigger batches, and turn on optimized writes or auto-compaction. Small files usually start in bronze, the raw landing layer, so the [medallion post](/writing/medallion-done-right/) is a good place to decide where compaction runs.

### 6. Skew: one task does most of the work

Spark splits work into tasks that run side by side. If 40% of orders belong to one customer, say a "guest checkout" account, every one of those rows lands in one task. The other tasks finish and wait. The cluster is paid for while it waits.

{{drawing: dbx-skew-bars}}

- **Spot it:** in the Spark UI, open the slowest stage and compare the longest task with the median. The rule we use: **skew when the slowest task takes more than 5 times the median**. In our recorded run the slowest join task took 246 milliseconds against a median of 45, about 5.5 times.
- **Fix:** turn on adaptive query execution (AQE), Spark's feature that re-plans a query using what it measured while running, with its skew-join setting. It splits the hot partition into several tasks. In that run the critical path, the time the job takes if every task has its own core, dropped from 460 to 179 milliseconds. If one key is still huge, handle it separately.

### 7. Too many or too few shuffle partitions

A shuffle is when Spark moves rows between machines, for a join or a group-by. The number of pieces it cuts the data into matters both ways. Too few, and each task gets more than fits in memory and writes to disk, called spill. Too many, and Spark spends its time scheduling thousands of tiny tasks.

- **Spot it:** spill in the stage details, or stages with thousands of tasks that each run for a few milliseconds.
- **Fix:** let AQE merge small partitions, and avoid a fixed number copied from a test job. In our recorded run, a sort with 1 shuffle partition spilled 128 MB to disk and took 7.5 seconds; 32 partitions took 6.2 seconds with no spill. That run also caught a trap: AQE's merging can glue small partitions back into big ones, so check spill after changing it.

### 8. Python UDFs where a built-in function would do

A Python UDF (user-defined function) sends every row out of Spark's engine to a Python process and back. Photon, Databricks' faster engine, cannot speed it up either.

- **Spot it:** `BatchEvalPython` in the query plan, or `@udf` in the code.
- **Fix:** rewrite with built-in functions such as `when`, `upper` and `trim`. In our recorded run, adding tax to 2 million rows went from 1.7 seconds to 141 milliseconds, about 12 times faster, with the same total. If Python really is needed, a pandas UDF moves data in batches and is much faster than one row at a time.

### 9. collect() and toPandas() on big data

Both pull every row onto the driver, the one machine that coordinates the cluster. On a big table the driver runs out of memory, the job fails, and someone "fixes" it with a bigger driver.

- **Spot it:** search notebooks and jobs for `collect()` and `toPandas()` on anything not already aggregated or limited.
- **Fix:** do the summary in Spark and bring back only the answer. In our recorded run, collecting 3 million rows hit the driver's result limit and failed; grouping in Spark and returning the top 10 stores took 123 milliseconds.

## The leak that hides all the others

### 10. No cost tags

Without tags, the bill is one number. Nobody can say which team, project or job spent it, so nobody feels responsible for it.

- **Spot it:** query the billing usage system table for last month and see how much has no team tag.
- **Fix:** put tags such as team, project and environment on every cluster, job and warehouse, and make a cluster policy require them. Tags flow into the billing system tables, so every row of usage can be grouped by team.

## A ten-minute weekly check

You don't need a cost tool to start. You need one query and one habit.

{{drawing: dbx-weekly-check}}

1. Query the billing system tables (`system.billing.usage`, joined to `system.billing.list_prices`) for the last 7 days, grouped by tag and by compute type.
2. Look for the top five jobs and clusters by spend, and anything untagged.
3. Put that query on a dashboard, add a budget alert, and look at it every Monday with a cup of chai.

## Ten questions to check your own workspace

1. Which scheduled jobs run on all-purpose compute?
2. What is the smallest size each cluster can autoscale down to?
3. Does any all-purpose cluster have auto-termination switched off?
4. How many queries did your biggest SQL warehouse run last week, and how long was it on?
5. Which of your largest tables have an average file size under 32 MB?
6. In your slowest job, how does the longest task compare with the median?
7. Is the shuffle partition count set by hand anywhere, and does any stage spill?
8. How many Python UDFs could be built-in functions?
9. Where does code call `collect()` or `toPandas()` on a whole table?
10. What share of last month's bill has no team tag?

Fix the holes in the bucket before you buy a bigger tap.
