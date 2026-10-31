---
title: Your Databricks cluster scales up and never comes back down
published: false
canonical_url: https://cleandataengineering.ai/writing/cluster-never-scales-down/
description: Autoscaling on Databricks grows a cluster quickly and shrinks it slowly, and sometimes not at all. The usual reasons are a minimum set too high, clusters that are never quite idle, workers holding data the autoscaler doesn't want to throw away, and streaming or shared workloads that keep everything busy. This note explains each one, the fixes, and how to see it in your own cluster events and billing tables.
---

*Originally published at [cleandataengineering.ai](https://cleandataengineering.ai/writing/cluster-never-scales-down/).*


Riya turns on autoscaling for the team's shared cluster: minimum 2 workers, maximum 10. The morning load arrives at 9 a.m., the cluster grows to 10, and the job finishes by 9:40. At 6 p.m. she looks again. The cluster still has 10 workers.

Nothing is broken. Autoscaling did exactly what it is built to do. It just turns out that growing and shrinking are not mirror images of each other.

Our [ten cost leaks post](/writing/databricks-cost-leaks/) gave this problem one paragraph. This note goes deep on it: why an autoscaling cluster grows easily but stays big, and how to make it come back down.

{{drawing: scale-balloon}}

## What autoscaling actually promises

Autoscaling means you give a cluster a **minimum** and a **maximum** number of workers, and Databricks adds or removes workers between those two numbers as the load changes. A worker is one of the machines that runs Spark tasks. You pay for every worker for every minute it is running, busy or not.

Two things matter for this post:

- **Scale-up is eager.** When tasks are queuing, adding workers is safe. The worst case is that you paid for a few extra minutes.
- **Scale-down is cautious.** Removing a worker is only safe if it has nothing useful on it. So the autoscaler waits until workers look idle, and removing them can take longer than adding them did.

Databricks has two flavours. **Optimized autoscaling**, on the Premium plan and above, scales down more aggressively than **standard autoscaling**. If your workspace is on the Standard plan, or a cluster was created in a way that uses standard autoscaling, expect slower shrinking.

## What it looks like over a day

Draw the number of workers across a working day and the problem is easy to see.

{{drawing: scale-day-line}}

The healthy cluster rises for the morning load and falls back to its minimum once the load is done. The sticky one rises at 9 a.m. and stays near the top until someone terminates it, or until auto-termination kicks in at night.

Here is what that shape costs. **This is an example, with made-up round numbers, not a real bill.** Say each worker costs ₹60 an hour, counting both the Databricks charge and the cloud machine. The cluster really needs 2 workers after 10 a.m., but sits at 8 until 8 p.m.

- Extra workers: 8 minus 2 is 6.
- Extra hours: 10 a.m. to 8 p.m. is 10.
- Extra cost per day: 6 workers times 10 hours times ₹60 is ₹3,600.
- Over 22 working days: about ₹79,200 a month, for one cluster doing nothing in the afternoon.

Use your own rates. The point is that the cost grows with idle hours, and idle hours are invisible unless you look.

## Six reasons the cluster stays big

{{drawing: scale-why-stay}}

### 1. The minimum is set too high

Autoscaling never goes below the minimum. A cluster with a minimum of 8 is a fixed cluster of 8 that can sometimes grow. Minimums often get raised once, after a slow morning, and are never lowered again.

### 2. Idle all-purpose clusters with long or no auto-termination

All-purpose clusters are the ones people attach notebooks to. Auto-termination stops a cluster after a set time with no activity. If it is switched off, or set to many hours, the cluster sits at its minimum (or worse, at whatever size it reached) all evening and all weekend.

### 3. Workers holding cached data or shuffle files are kept

A shuffle is when Spark moves rows between workers for a join or a group-by, writing intermediate files on the workers' local disks. A cache is data someone asked Spark to keep in memory or on local disk, for example with `df.cache()`. If a worker holding those files is removed, the work behind them may have to be redone. So the autoscaler can be reluctant to remove such workers, and a forgotten `cache()` in a notebook can keep machines alive long after anyone needs them.

### 4. Streaming jobs on autoscaling clusters

A streaming job processes small batches all day. The cluster is rarely fully idle, so classic autoscaling often sees just enough activity to keep workers, and streaming clusters can grow during a burst and then stay large. This is why Databricks recommends fixed-size clusters for Structured Streaming on classic compute, or enhanced autoscaling in declarative pipelines (Lakeflow Declarative Pipelines, formerly Delta Live Tables), which was built with streaming in mind. Our [streaming post](/writing/databricks-streaming/) covers how to run those jobs well.

### 5. One heavy job sharing a cluster with many small ones

The heavy job pushes the cluster to its maximum. Then a steady trickle of small notebook queries and short jobs keeps a few tasks running on most workers. No worker is ever idle enough to remove. The cluster stays sized for the heavy job, paid for by the small ones.

A skewed job does something similar. If one task does most of the work, the rest of the cluster waits for it. The rule we use flags skew when the slowest task takes more than 5 times the median.

### 6. Scale-down is slower and more cautious than scale-up

Even with none of the above, shrinking simply happens later than growing. Workers are removed only after they have been idle for a while, and often a few at a time. For a short, spiky load, the cluster may spend more time coming down than it spent working.

## What goes wrong when people fix it

- **Setting the maximum very low** to "control cost". Jobs run longer on fewer machines, and the total bill can go up instead of down.
- **Turning auto-termination down to 2 or 3 minutes** on a cluster people use all day. Every coffee break means a cold start, and people start running a loop to keep it awake.
- **Turning autoscaling off everywhere.** For batch jobs on their own cluster, autoscaling usually helps. The trouble is mostly shared, streaming and interactive clusters.
- **Fixing one cluster by hand.** Without a cluster policy, the next cluster someone creates has the same settings as the old one.

## The fixes

{{drawing: scale-fix-card}}

1. **Job compute per job.** A job cluster starts for one job and ends with it, so there is nothing left to shrink. It is also billed at a lower rate than all-purpose compute.
2. **Sensible minimums.** Start with a minimum of 1 or 2 for batch work and let autoscaling grow. Raise the minimum only if you can name the reason.
3. **Auto-termination on every all-purpose cluster.** Pick something that fits how people work, such as 20 to 30 minutes idle.
4. **Cluster policies.** A policy can limit the minimum and maximum workers and require auto-termination, so good settings are the default and bad ones are impossible.
5. **Serverless where it fits.** With serverless compute for notebooks, jobs or SQL warehouses, Databricks manages the size for you, and you stop tuning minimums at all. Check that your workloads and region are supported first.
6. **Separate clusters for streaming.** Give each long-running stream its own fixed-size cluster, or run it in a declarative pipeline with enhanced autoscaling.
7. **Unpersist what you cache.** Call `unpersist()` when a cached table is no longer needed, and don't leave `cache()` in scheduled code by habit.

## How to watch it

You can't fix what you don't see. Two places show this problem clearly.

**The cluster event log.** Every cluster has an event log in its page that records when it started, resized and terminated. Read a day of it. If you see a resize up in the morning and no resize down until termination, you have a sticky cluster.

**The billing system tables.** `system.billing.usage` records usage per cluster per day. A query like this shows which clusters used the most DBUs (Databricks Units, the unit the price list is written in) last week:

```
SELECT usage_metadata.cluster_id,
       usage_date,
       SUM(usage_quantity) AS dbus
FROM system.billing.usage
WHERE usage_date >= current_date() - 7
  AND usage_metadata.cluster_id IS NOT NULL
GROUP BY ALL
ORDER BY dbus DESC
LIMIT 20;
```

A shared cluster near the top every day, with no heavy job to explain it, is the first one to look at. Where your workspace has the compute system tables, they also show each cluster's settings over time, including its minimum, maximum and auto-termination.

## Six questions to check your own workspace

1. What is the minimum worker count on each of your autoscaling clusters, and who decided it?
2. Which all-purpose clusters have auto-termination off, or set to more than an hour?
3. In yesterday's event log for your busiest shared cluster, when did it last resize down?
4. Which streaming jobs run on autoscaling all-purpose clusters?
5. Which scheduled jobs share a cluster with people's notebooks?
6. Do you have a cluster policy that every new cluster must use?

A cluster that grows in the morning should be small again by lunch; if it isn't, the valve is stuck, not the pump.

