---
title: Streaming on Databricks without the pain
date: 2026-10-31
subject: data
audience: builders
kind: decision
draft: false
summary: Most teams that ask for streaming need fresh data, not a stream. Start by asking how fresh the data must be; often a batch every 5 to 15 minutes is enough and far simpler. When you do stream, run the same medallion at two speeds, keep your checkpoints, set a watermark, and pick a trigger that matches how often the data actually arrives.
linkedin: "We need real-time" is the most expensive sentence in data engineering. Usually a batch every 10 minutes would do, at a fraction of the cost and the pager calls. When you really do need streaming on Databricks, here is the simple version: one medallion at two speeds, checkpoints you never delete, and a stream that only runs when there is data.
deeper: /learn/data-platform-architecture/#streaming
deeper_label: the streaming lane in the full data platform architecture
---

Priya's product manager says the sales dashboard must be "real-time". Two weeks later Priya has a cluster running day and night, a Kafka topic, a folder of checkpoints she is scared to touch, and a dashboard that people look at twice a day.

Nobody did anything wrong. They just answered the second question first. The first question is whether you need streaming at all.

This post gives a simple way to decide, and then the handful of ideas that keep a stream boring once you have one.

## First question: do you need streaming at all?

Streaming means the pipeline keeps running and picks up new data within seconds or a few minutes of it arriving. That is powerful, and it costs money and attention every hour of the day. Ask three questions before you build one.

{{drawing: stream-need}}

1. **Does someone act on this data within minutes?** A fraud check that blocks a payment, stock levels in a quick-commerce store, a live operations screen. If nobody acts that fast, you don't need it that fast.
2. **Is it needed within the hour, but not within seconds?** For most dashboards and reports, data that is 5 to 15 minutes old is fine. That is a frequent batch, not a stream.
3. **Is hours old fine, or does the data arrive in drops anyway?** If a partner sends a file every hour, an always-on stream will spend most of each hour waiting. Run a batch on the same schedule as the drops.

Here is the trade-off in one table.

| Choice | How fresh | What it costs | How hard to run |
|---|---|---|---|
| Batch (hourly or daily) | hours | only while it runs | easiest |
| Frequent batch (every 5 to 15 minutes) | minutes | only while it runs, plus start-up time | easy |
| Streaming (always on) | seconds | all day, every day | hardest |

The middle row is the one most teams should pick first. And as you'll see below, you can write it as streaming code from day one, so moving to a real stream later is a setting, not a rewrite.

## One medallion, two speeds

If you do need streaming, you don't need a second architecture. The same bronze, silver and gold layers from the [medallion post](/writing/medallion-done-right/) work at two speeds.

{{drawing: stream-two-speeds}}

Most tables move on the slow lane, in batches. A few hot tables move on the fast lane: events land in a bronze stream, flow into silver streaming tables, and feed gold tables that update incrementally, which means only the new rows are processed each time. The contracts, quality checks and one-way rule are the same on both lanes. Only the speed changes.

This matters because the alternative, a separate streaming system beside the batch one, means every rule is written twice and the two copies drift apart.

## Your two ways to build it on Databricks

- **Structured Streaming in your own code.** This is Spark's streaming engine. You write the read, the transformation and the write in Python or SQL, and you choose the checkpoint location, the trigger and the write logic yourself. Full control, and full responsibility.
- **Lakeflow Declarative Pipelines** (formerly Delta Live Tables). You declare the tables you want, such as a streaming table for silver and a materialized view for gold, and the pipeline works out the order, runs Structured Streaming underneath and manages the checkpoints for you. You also declare quality expectations next to each table.

For sources, two names come up again and again. **Auto Loader** watches a cloud storage folder and picks up each new file once, which is the usual way to stream files into bronze. **Kafka** and **Azure Event Hubs** are the usual sources when the data is a stream of events to begin with.

A fair rule of thumb: if your team wants the plumbing handled, start with declarative pipelines. If you need unusual write logic or fine control, write Structured Streaming yourself. Either way, the ideas below are the same.

## Checkpoints, and why you never delete them

A checkpoint is a small folder where the stream writes down how far it has got: which files or which Kafka messages it has already processed, plus any running totals it is keeping.

{{drawing: stream-bookmark}}

Think of it as a bookmark. When the stream stops, for a deploy, a crash or a cluster restart, it opens the book at the bookmark and carries on. Nothing is read twice and nothing is skipped.

Delete the checkpoint and you've thrown away the bookmark. Depending on how the stream is set up, it either starts from the very beginning and writes everything again, or starts from "now" and silently skips whatever arrived in between. Both are bad, and neither shows up as an error.

So: one checkpoint per stream, never shared, never deleted to "fix" something. If you change a stream so much that the old checkpoint no longer fits, treat it as a new stream with a new checkpoint and a planned backfill.

### Exactly-once into Delta

Exactly-once means each record ends up in the target table one time, even if the stream crashes and restarts halfway. When a stream writes to a Delta table, the checkpoint and Delta's transaction log work together so that a batch is either fully committed or not at all, and a restarted batch is not written twice. That is the main reason to keep the bookmark safe.

### MERGE in foreachBatch for upserts

A plain stream only appends rows. But silver usually needs one row per order, updated when the order changes. That is an upsert: update the row if it exists, insert it if it doesn't.

The common pattern is `foreachBatch`, which hands you each small batch of new rows as an ordinary table. Inside it you run a Delta `MERGE` on the business key, such as the order ID. Write the MERGE so that running it twice on the same batch gives the same result, because after a crash a batch can be replayed. A MERGE by key that keeps the latest version of each row is naturally safe in this way.

## Late data and watermarks

Events don't always arrive in order. A delivery app on a phone in a lift might send its "order delivered" event ten minutes late.

{{drawing: stream-train}}

A watermark is how long the stream waits for late events, like a train that holds the doors for a fixed time. You might say "wait up to 10 minutes past the event time". Events within that window are counted. Events later than that miss the train.

The watermark matters most when the stream keeps a running state, for example counting orders per 5-minute window, removing duplicates, or joining two streams. Without a watermark, the stream must keep every window open for ever in case a late event turns up. That state grows every day until the stream slows down and eventually falls over. With a watermark, old windows are closed and their state is dropped.

Pick the wait from how late your data really arrives, not from a guess. Too short and you drop real events. Too long and you keep more state than you need.

## Triggers: how often the tap runs

A trigger decides when the stream processes new data. Think of a tap.

{{drawing: stream-tap}}

- **Always on.** The stream keeps running and processes new data in small batches as soon as it arrives. Freshest, and the cluster never stops.
- **Every N minutes.** The stream stays running but processes on a fixed schedule, such as every 10 minutes. Smoother, but the cluster is still on.
- **Available now.** The stream starts, processes everything that has arrived since the last checkpoint, and stops. You schedule it as a job, say every 15 minutes or every hour.

Available-now is the quiet hero. It is streaming code, with its checkpoint, exactly-once writes and watermarks, run as a batch. That is the frequent batch from the first section. When the business later needs seconds instead of minutes, you change the trigger, not the pipeline.

## A stream that runs all day costs all day

This is the part that surprises people. An always-on stream keeps its compute running whether ten events arrive or ten million. Take an example cluster at ₹200 an hour. Always on, that's ₹4,800 a day. Run the same code with available-now once an hour, taking about five minutes each time, and it is roughly two hours of compute a day, plus start-up time.

Before you leave a stream always on, look at when the data actually arrives.

## Mistakes we see most

1. **Streaming everything.** Every table gets a stream because one table needed it. Stream the few hot tables; batch the rest.
2. **Deleting checkpoints.** Done to "reset" a stuck stream. The result is duplicates or a silent gap.
3. **No watermark.** State grows for ever, the stream gets slower each week, and one day it runs out of memory.
4. **Always-on compute for data that arrives hourly.** Paying for 24 hours to process a few minutes of work. Use available-now on a schedule.
5. **Schema changes breaking the stream.** The source adds a column and the stream stops at 2 a.m. Decide in advance what happens: Auto Loader can track the schema and keep unexpected fields in a rescued column instead of losing them, and your pipeline should alert someone and restart cleanly rather than fail in silence.

## Questions to check your own setup

1. Who acts on this data, and how quickly do they really need it?
2. Could this stream run with available-now on a schedule instead?
3. Does every stream have its own checkpoint, and does anyone on the team know never to delete it?
4. Does every stream that counts, deduplicates or joins have a watermark?
5. Is your MERGE safe to run twice on the same batch?
6. What happens, and who hears about it, when the source adds a column?

Streaming is a speed, not a separate world. Choose the slowest speed the business can live with, and the rest gets much easier.
