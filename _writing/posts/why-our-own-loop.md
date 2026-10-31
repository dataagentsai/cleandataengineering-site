---
title: Why we wrote our own agent loop
date: 2026-10-31
subject: ai
audience: builders
kind: decision
draft: false
summary: Our reference agent, a support agent that can move real money, runs on a loop we wrote ourselves in one file of 416 lines. We did it so every budget and check sits at a place a test can reach. We kept the door open by putting the loop behind a port: a Pydantic AI version is written, LangGraph and Claude Agent SDK versions are planned, and all of them must pass the same frozen tests.
linkedin: Everyone told us to pick an agent framework. We wrote the loop ourselves instead: 416 lines, four of which actually go round. Here is what a framework would have given us, what it would have cost, and the exact conditions under which we would switch.
deeper: /learn/agent-harness/tech-l4.html
deeper_label: the control loop in the Agent Harness tutorial
---

When we started the [reference agent](https://github.com/dataagentsai/reference-agent), a customer-support agent for a clothing shop that can cancel orders and pay refunds, the first question people asked was which framework we would use. LangGraph? The Claude Agent SDK? Pydantic AI?

We used none of them for the loop. The agent's loop is plain Python that we wrote and own, in one file.

The general comparison of the options is in [choosing your agent loop](/writing/choosing-agent-loop/). This post is our own story: why plain code, how small it is, what we gave up, and what would change our minds.

## A bicycle in the shed

Picking a framework is like walking into a car showroom. Everything is included: the engine, the seats, the satnav, a warranty. Writing your own loop is building a bicycle in the shed. It has fewer parts, and you know every one of them, because you fitted them.

{{drawing: own-bike-showroom}}

A car is the right choice for many trips. But our agent moves money. Say Priya asks for a refund of ₹4,000 on a jacket. Before it runs, we want to point at the exact line that checked she owns the order, the line that checked the amount, and the line that would stop a run going round too often, each with an ordinary unit test.

The README puts it in one line: no agent framework, so that each layer of the harness is visible.

## The one place that sees the whole trip

A single model call can't tell whether it is the first call of a task or the fourteenth. Only the loop sees the whole trip. Only the loop knows that fourteen calls are one runaway task, not fourteen separate tasks. Our notes call this seeing the *trajectory*: the full path a run has taken so far.

Everything that needs that view lives in the loop:

- **A step budget.** The run stops after 12 trips round the loop, and always records why.
- **A clock.** A turn may take at most 60 seconds.
- **A cost ceiling.** The run stops once it has spent $0.50, checked between calls, because you can't un-spend a call.
- **A tool-call bound.** At most 8 tool calls in one step, and 24 in a turn.
- **A loop detector.** If the model asks for the same tool with the same arguments three times, it is going in circles, and the run stops. This is called *oscillation*.

When we wrote the decision down in September, the note said: handing the loop to a framework means handing over the only place that can see the trajectory, to save writing about 350 lines once. A bad trade for this agent.

## How small is it, really?

We counted, because "small" is easy to claim.

{{drawing: own-loop-lines}}

The loop is one file of **416 lines**. Take out the blank lines, comments and explanations, and **290 lines of code** remain. The part that actually goes round is four lines: for each step up to the budget, take a step; if that step ended the run, return how it ended; if no step did, stop because the budget ran out.

Each step does five things in the order drawn above. In the last one, the loop counts the tool calls, looks for circling and checks each call before running the ones allowed.

Six small helper files sit beside it: planning calls, screening them, running them, recording how a run ends, counting spend, and making sure the agent doesn't act on data that has gone stale. With those, the whole folder is 1,356 lines, 785 of them code.

It has grown since that September note. Each new rule, such as the clock and the tool-call bound, added a few lines in a place we chose.

## What a framework would have given us, and cost us

We are not pretending the trade is one-sided.

{{drawing: own-gain-cost}}

A framework hands you a lot on day one, and the left pan is real: resumable state, approval pauses, streaming, documentation and a community. The right pan is quieter. Our budgets and checks would sit wherever the framework's hooks happen to be, not where the rule belongs, and each upgrade could move those hooks.

Owning the loop doesn't mean owning everything. Waiting days for an approval and surviving a restart we got by adopting Temporal and DBOS, two tools built for that job. We own the one place that sees the trajectory, and adopt the rest. That pattern, a port for each part with an adapter plugged in, is the subject of [swap anything, break nothing](/writing/harness-design-patterns/).

We do use Pydantic AI today, just not as the loop. It calls the model for us, behind our own model interface, and one module is the only place allowed to import it.

## The loop is a plug, not a foundation

Choosing plain code would be a trap if it meant we could never change our minds. So the loop sits behind a *port*: a fixed shape the rest of the agent calls, without knowing what is plugged in behind it.

{{drawing: own-loop-port}}

Here is where each plug stands today:

- **Our own loop:** built, and the one the agent runs on.
- **Pydantic AI owning the loop:** written. Its agent runs the steps, and our checks run at its own hooks before each model request and around each tool. One line of configuration picks it. It is being measured now, and the results are not in.
- **LangGraph owning the loop:** planned, not built.
- **The Claude Agent SDK owning the loop:** planned, not built. So is a fourth run, with our loop calling Claude's own SDK for the model.

Every plug is judged by a bar we wrote down on 1 October, before any of them was built, so the bar couldn't bend to fit the result:

1. **The same test cases, unchanged.** Sixteen cases for three ports, the approval, cost and policy checks, frozen on 20 October. If someone edits a case file, the build fails.
2. **At most 150 lines of adapter per port**, not counting blank lines or comments.
3. **No change to our interfaces** made just so the framework can call them.
4. **No fighting the framework.** No private interfaces, no wrapping its loop, no second copy of state it already holds.

On a rough count, the Pydantic AI adapter's policy piece is 122 lines and its cost piece 38, even counting every line of each file. The official count and the test run are still to come.

## When we would switch

We would hand the loop to someone else if any of these became true:

- **The job changes shape.** Our September note says a research assistant with a complicated graph gets a different answer. Our tutorial picks LangGraph for workflow-shaped agents, full Pydantic AI for simple ones, and Microsoft Agent Framework for a .NET team.
- **The agent works on files and code.** Our plans already put a different agent, a Spark cost analyst with subagents, on the Claude Agent SDK.
- **An adapter clears all four bars.** Then switching is a line of configuration, not a rewrite, and the decision gets cheap.

## What went wrong when we owned the loop

Owning the loop means owning its bugs. Two real ones from our review log:

1. **Checks declared but never called.** Our checks could run in five places. Three of them were declared and accepted rules in configuration, but nothing ever called them. No test failed, because no test asked whether each place was reached. We found it by asking a plain question in review: are the checks really a list we can configure? Now all five are reached, and a test proves it.
2. **A failure that escaped.** A broken conversation history that no provider would accept slipped past the loop, and the customer got a plain server error with no reply. Now it ends the run like every other failure, with a reason and a message for the customer.

Owning the loop meant these were ours to find and ours to fix. It also meant each fix landed in a file we already understood, not in someone else's callback.

## Six questions to ask before you write your own

1. Can a wrong step move money or change someone's records?
2. Can you name the line where your step budget, cost ceiling and loop detection live?
3. Would your tests reach every step if a framework ran them?
4. Which parts can you adopt instead, such as durable waits, tracing and the model call itself?
5. Is the loop behind a port, so the choice can be undone?
6. Have you written down, before you start, what would make you switch?

The loop is a small part of the harness, as we argued in [the model is 10%](/writing/model-is-ten-percent/). It is also the part that holds the budgets, so if you can't answer the second question, start there.

Write the four lines that go round yourself, and adopt everything else.
