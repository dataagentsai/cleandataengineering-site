---
title: DBOS vs Temporal: durable agents without the drama
date: 2026-10-31
subject: ai
audience: builders
kind: decision
draft: false
summary: Durable execution lets a long agent task survive crashes, restarts and waits of days, with each step done once. DBOS does it as a library that keeps state in the Postgres you already run; Temporal does it with a separate, mature cluster that workers poll. Pick by what you already run and what you need, and if no task waits longer than one request, you may need neither.
linkedin: Your agent asks a manager to approve a payout, and the manager replies two days later. Something has to remember where the agent was, through every restart in between. Here is how DBOS and Temporal each do that job, what each costs you to run, and when an idempotency key and a retry are all you need.
deeper: /learn/agent-harness/dbos.html
deeper_label: DBOS in the Agent Harness tutorial: what it does, the payout flow, the hand-off flow, and crash and restart
---

Most agent turns are over in a few seconds. A customer asks, the model thinks, a tool runs, and the answer goes back. If the server falls over halfway, you retry and nobody notices.

Then one day the agent has to wait. A payout above ₹25,000 needs a claims handler to approve it, and the handler might reply in five minutes or in two days. In those two days your server will restart, deploy, and maybe scale to zero. Something has to remember exactly where the agent was, and make sure the money is paid once, not twice.

That something is **durable execution**. DBOS and Temporal are two good ways to get it, built in very different shapes. This post compares them fairly, and ends with the case where you need neither.

## What durable execution is

{{drawing: dur-save-point}}

Think of a video game with save points. You play, you reach a flag, the game saves. If the power goes, you don't start the game again. You reload and carry on from the last flag.

Durable execution does the same for a piece of code. You write the long task as a **workflow**, a function split into **steps**. After each step finishes, its result is saved somewhere safe. If the process dies, the workflow is run again from the top, but every finished step hands back its saved result instead of running again. So the code catches up to where it was, and carries on.

That gives you three things:

1. **It survives crashes and restarts.** Progress lives in storage, not in memory.
2. **It can wait for days.** A waiting workflow is a saved record, not a running thread, so it costs almost nothing.
3. **Each step runs once,** as far as the outside world can tell, as long as the steps themselves are safe to retry. More on that in the mistakes.

## Two shapes for the same job

{{drawing: dur-two-shapes}}

**DBOS is a library inside your app.** You add it to your Python code and mark functions with decorators: `@DBOS.workflow()` on the workflow, `@DBOS.step()` on each step. DBOS writes each step's result into tables in your own Postgres. There is no separate server to run. When your app starts, DBOS looks for workflows that were still running and carries each one on from its last finished step.

**Temporal is a separate service.** A Temporal cluster, which you run yourself or rent as Temporal Cloud, keeps an **event history** for every workflow run: a list of everything that happened, in order. Your own processes run **workers**, which poll the cluster for work. Temporal splits your code in two. **Workflow** code decides what happens next and must be deterministic, which means it gives the same result every time it is replayed from the history. **Activity** code does the real work, such as calling an API or writing to a database. After a crash, a worker replays the workflow from its event history to rebuild where it was.

Temporal is mature, runs at very large scale, and has software kits for many languages. DBOS is younger and smaller. It started with Python and TypeScript; if your team writes in something else, check its current list before you choose.

Both get you the same promise. The difference is where the state lives and what you have to run.

## One payout, two ways

{{drawing: dur-payout-wait}}

Say Rohan asks the claims assistant to release ₹30,000. The automatic limit is ₹25,000, so a handler, Asha, must approve it. She replies two days later.

**In DBOS,** the payout is one workflow function:

1. A step reads the claim and sees ₹30,000 is above the limit.
2. The workflow calls `DBOS.recv()` to wait for a message. Nothing is running now; there is just a row in Postgres saying the workflow is waiting.
3. Rohan's turn ends at once. He is told nothing has been paid yet.
4. Two days later, Asha clicks Approve. Her desk calls `DBOS.send()` with the workflow's id.
5. The workflow wakes, re-reads the claim in a step to check nothing changed, and pays in another step.

**In Temporal,** the shape is nearly the same. An activity reads the claim. The workflow code waits for a **signal**, Temporal's word for a message sent to a running workflow. Asha's desk sends that signal through the cluster. A worker picks up the workflow again, and an activity makes the payment.

The real flow, step by step, is in the tutorial's [payout flow](/learn/agent-harness/dbos-approval.html). Why the approval belongs in a durable wait at all, and what Asha should see on her card, is in [Human in the loop without humans in the way](/writing/human-in-the-loop/).

## The trade-offs

| | DBOS | Temporal |
|---|---|---|
| What you run | your app and the Postgres you already have | a cluster with its own database, or Temporal Cloud |
| What you pay for | nothing new | the cluster's servers and the people to run them, or the Cloud bill |
| Time for each step | one write to your own database | a round trip through the cluster |
| Languages | check its current list | many, mature |
| Seeing what is running | query its tables in your Postgres | a web interface over every run's history |
| Scale | as far as your Postgres goes | very large, proven |
| Team skills | Postgres and your app | a new service and its replay rules |

A few of these need a word more.

- **Running it.** Our comparison in the tutorial put Temporal's ongoing work for the team as "low on Cloud; high self-hosted". DBOS adds no infrastructure at all, because it reuses the database the agent already writes its other state to, as [Just use Postgres](/writing/just-use-postgres/) argues.
- **Rules on your code.** Temporal's are strict: workflow code may not read the clock, make random numbers, or do input and output directly. That strictness is what makes its replay reliable. DBOS asks the same thing in a lighter way: put anything that changes between runs inside a step. In the tutorial even reading the clock is a step, so a replay sees the same time.
- **Changing code while runs are waiting.** Temporal has mature tools for running old and new versions of a workflow side by side. In the tutorial we handle it the plain way: before changing a workflow's steps, let the waiting ones finish.

Our verdict in the Agent Harness was DBOS, because its state lives in the Postgres we already run, so it adds nothing. We would move to Temporal for long chains of steps that must be undone one by one if something fails late, which people call sagas, or when we need mature versioning. A bank with many teams writing in many languages is a different place from a single agent team with one database, and Temporal fits it well.

## When you need neither

Plenty of agents never wait. Each turn reads, thinks, calls a tool or two, and answers in under ten seconds. Nothing has to survive a restart in the middle, because the client can simply try again.

For those, you need two things, both small:

- **An idempotency key.** *Idempotent* means doing it twice has the same effect as doing it once. Give each write a key, such as the tool call's id, and record it before the write runs. A second attempt with the same key gets the first answer back.
- **A retry.** If the turn fails, run it again. The key makes the retry safe.

That is all the tutorial's ordinary turns use. Only two functions in the whole harness are workflows: the payout approval and the hand-off to a person. Everything else is a turn with a key.

## Which one, in three questions

{{drawing: dur-decide}}

1. **Does any task wait for a person or a timer, or run longer than one request?** If not, use an idempotency key and a retry, and stop there.
2. **Do you have many services in many languages, or very large volume, or long undo chains?** Then Temporal, on Temporal Cloud unless you have a team to run the cluster.
3. **Do you already run Postgres?** Then DBOS. It is a library and a few tables, not a new system.

## Mistakes we see

1. **Non-deterministic code inside the workflow.** Reading the clock, a random number, or an API call made directly in workflow code gives a different answer on replay, and the workflow takes a different path. Put it in a step, or an activity in Temporal.
2. **Steps that are not idempotent.** A step can run, do its work, and crash before its result is saved. On restart it runs again. If that step sends money, the payment system must recognise the repeat by its key, or Rohan is paid twice.
3. **Holding a thread while waiting.** Waiting inside a web request or a `while` loop with a sleep ties up a server and is lost on a restart. Use the framework's durable wait, such as `DBOS.recv()` or a durable sleep, or a Temporal signal or timer.
4. **No answer for silence.** A wait with no timeout hangs forever. Decide what happens when nobody replies, and make it the safe answer.
5. **A cluster for a three-second task.** Adopting Temporal, with its servers, workers and replay rules, for turns that never wait is cost and complexity with nothing to show for it.

## Six questions to check your own setup

1. Which of your agent's tasks can wait longer than one request, and could you name them all?
2. If your server restarts while one of them is waiting, what brings it back, and from which step?
3. Can every step that touches the outside world be run twice without a second effect?
4. Does any workflow code read the clock, make a random number, or call an API outside a step?
5. Who runs your workflow engine, and what does it cost each month, in servers and in people?
6. If your tasks never wait, what would you lose by removing the engine and keeping just keys and retries?

Durable execution should be boring: a save point after every step, and nobody paid twice.
