---
title: Under the hood: why fundamentals are the slow road that wins
published: false
canonical_url: https://cleandataengineering.ai/writing/under-the-hood/
description: Tools and AI make it easy to get results without knowing what happens underneath, and many engineers now skip that part. It is slower to learn what's under the hood, but it is what lets you debug, control cost, design well and check an AI's answer. Learn one layer below where you work, and open the hood on the tools you use every week.
---

*Originally published at [cleandataengineering.ai](https://cleandataengineering.ai/writing/under-the-hood/).*


We ran a small experiment for the DataTwin Studio. Load a day of orders into a Delta table with a MERGE. Then load the exact same file again. The second MERGE matches every row and changes nothing.

Except it still wrote a new data file. The table's numbers were identical, the job was green, and underneath, the transaction log recorded a file written. Do that every hour on a big table and you pay for it in storage, small files and slower reads, and nobody can tell you why. You can see it for yourself in the [recorded run](/learn/data-platform-sim/).

You only see that if you look under the hood. And more and more engineers don't.

## The bottom of the iceberg

Modern tools are designed to hide the machinery. One line of code reads a table, joins it and writes it back. One call to a model returns a fluent answer. That is a good thing: nobody wants to hand-write a distributed join.

{{drawing: uh-iceberg}}

But the machinery is still there. Files are written and rewritten. A transaction log records every change. Data is shuffled between machines over the network. Memory fills up and spills to disk. A model counts tokens and forgets whatever falls outside its context window. And a meter runs for every second of it.

When everything works, you never need the bottom of the iceberg. When it breaks, or when the bill arrives, the bottom of the iceberg is the only place the answer lives.

## Why people are skipping it

It isn't laziness. Three things make skipping easy:

- **The tools are genuinely good.** You can build a working pipeline without ever knowing what a shuffle is.
- **AI answers the surface question instantly.** "Write me a MERGE" gets a correct-looking MERGE in seconds. It doesn't tell you the MERGE rewrites files.
- **Results are rewarded fast; understanding is rewarded late.** The ticket closes today. The incident that needs the understanding comes in month six.

So for a while, skipping looks like the smart choice.

## The slow road, and where it overtakes

Here is what the two approaches look like over time.

{{drawing: uh-curves}}

Learning shortcuts gets you moving fast: copy the pattern, ask the AI, ship it. Learning fundamentals starts slower, because you stop to ask how it works and you build small things to find out.

Then the first real incident arrives. A job that ran in ten minutes takes three hours. A re-run doubles a day of revenue. The [cluster never scales back down](/writing/cluster-never-scales-down/). The model gives a confident answer that is wrong. On the shortcut road, you're stuck: you can only try things and ask the AI again. On the fundamentals road, you know where to look.

The slow road isn't slower for long. It is slower for a few months, and then it is the only road that keeps going up.

## What fundamentals actually buy you

1. **Debugging.** You know which layer to look at. "It's slow" becomes "the join is shuffling the big table; let's broadcast the small one."
2. **Cost control.** You know what you are paying for: files rewritten, data moved, machines left running, tokens sent.
3. **Better design.** Choices like table layout, incremental loads, partitioning or how much context to send a model are only good if you know what they do underneath.
4. **Checking the AI.** This one is new, and it may matter most.

{{drawing: uh-check-ai}}

An AI answer is fluent and confident whether it is right or wrong. If you understand the engine, you can check it: run it, read the query plan, read the log, and see whether it does what the answer claims. If you don't, your only move is to ask the AI again, and hope. The post on [the oracle problem](/writing/oracle-problem/) explains why someone always has to know the right answer; fundamentals are how that someone is you.

## How to learn under the hood without drowning

You can't learn every layer of everything. You don't need to.

{{drawing: uh-layers}}

- **Learn one layer below where you work.** If you write SQL, learn how the engine plans and runs it. If you call a model, learn tokens, context windows and sampling. If you use a framework, learn what it calls underneath. One layer down is where most problems and most costs come from.
- **Open the hood on what you use every week.** Not on everything. The tools you touch daily deserve the 50-minute and 5-hour depths from [how to learn in the AI era](/writing/learn-in-the-ai-era/).
- **Read what the machine writes.** Query plans, the Spark UI, the Delta transaction log, the token count on a model call. The machine already tells you what it did; most people never look.
- **Ask "what happens when…?"** What happens when this job runs twice? When the source sends a file late? When the input is ten times bigger? Then run it and see.
- **Build a tiny version.** A tiny key-value store, a tiny scheduler, a tiny model. Building a small one teaches more than reading about a big one.
- **Use AI to explain the internals, then verify by running.** "Explain what a MERGE does to the files in a Delta table" is a great prompt. Then run it and read the log yourself.

The site's [Delta Lake internals](/learn/data-platform-sim/delta/) and [Spark internals](/learn/data-platform-sim/spark/) pages are recorded from real runs for exactly this: you see the files, the log, the stages and the tasks, not a description of them.

## What goes wrong

- **Skipping it because the AI knows.** The AI knows the words. You need to know the machine, because you are the one on call.
- **Going to the bottom of everything.** Reading the source code of every tool you touch. One layer down, on what you use most, is enough.
- **Theory without running.** Reading about shuffles without ever watching one. Fundamentals stick when you see them happen.
- **Learning internals of the wrong tool.** Go deep on what your job runs on, not on whatever is popular this month.
- **Treating it as a phase.** Under-the-hood learning isn't a course you finish. It is a habit: every time something surprises you, open the hood.

## Six questions to check your own fundamentals

1. For the tool you use most, can you describe what happens one layer below your code?
2. What does your most common job actually write to storage when it runs?
3. When did you last read a query plan, a transaction log or a token count?
4. What would happen if your main pipeline ran twice in a row?
5. Could you tell whether an AI's explanation of your system was wrong?
6. What surprised you this month, and did you open the hood to find out why?

It is the slower way to learn, and it is still the right one: the engineers who know what's underneath are the ones everyone calls when it breaks.

