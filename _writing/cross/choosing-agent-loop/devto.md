---
title: Choosing your agent loop: LangGraph vs OpenAI Agents SDK vs Claude Agent SDK vs plain code
published: false
canonical_url: https://cleandataengineering.ai/writing/choosing-agent-loop/
description: Every agent runs the same small loop: build the context, ask the model, run the tools it asked for, and go round again. LangGraph, the OpenAI Agents SDK, the Claude Agent SDK and a plain while-loop are four ways to own that loop, each with real gifts and real costs. Pick by the job, then put the loop behind a port so you can change your mind.
---

*Originally published at [cleandataengineering.ai](https://cleandataengineering.ai/writing/choosing-agent-loop/).*


A new agent project often starts with a long argument about frameworks. LangGraph or the OpenAI Agents SDK? The Claude Agent SDK, or just write it ourselves? People pick a side early and defend it for months.

The argument matters less than it feels. Under all of them sits the same small loop, and in a working agent that loop is a small part of the code. The checks, the state, the traces and the cost meter are the rest, as we argued in [the model is 10%](/writing/model-is-ten-percent/).

Still, the loop is a real choice, and each option has real gifts and real costs. This post compares them fairly, as of October 2026. These products change fast, so check the details below against their current documentation before you rely on them.

## Four ways to make the trip

Think of the loop as getting from a question to an answer. There are four ways to make the trip.

{{drawing: loop-vehicles}}

- **LangGraph is a bus on a fixed route.** You draw the agent as a graph: boxes (called nodes) for steps, and lines (called edges) for which step can follow which. The framework runs your graph and carries one shared state object between the nodes.
- **The OpenAI Agents SDK is a relay race.** You define agents, each with instructions and tools. One agent can hand the conversation to another, which is called a *handoff*. The model sees a handoff as just another tool it can call.
- **The Claude Agent SDK is a car with a driver.** It packages the same loop that runs Claude Code as a library. The loop, a set of built-in tools for files, the shell and the web, and the handling of long conversations all come included.
- **Plain code is a bicycle you build yourself.** It is a `while` loop: call the model, run any tools it asked for, repeat. The tutorial's claims agent does this in about 400 lines of Python.

Our tutorial compares a few more. **Pydantic AI** is a typed Python framework whose agent you can step through one step at a time. The **Anthropic tool runner** is a thin helper: the loop with hooks, still yours. **Microsoft Agent Framework** suits .NET or Azure-first teams.

## The same five steps, whoever drives

Whichever you choose, the loop does the same job.

{{drawing: loop-five-steps}}

1. **Build the context:** the instructions, the conversation so far, and the tools this person may use.
2. **Ask the model** for its next step.
3. **Read the answer.** Is it words, or a request to call tools?
4. **Check, then run** the tools it asked for, and add the results to the context.
5. **Stop or go round.** Stop if the model answered in words, or if a budget ran out.

The budgets are the part teams forget. The tutorial's agent stops after 12 trips, 60 seconds, $0.50 or 24 tool calls, whichever comes first. The question to ask of any framework is simple: where would my checks and budgets sit, and can my tests reach them?

## What each one gives you

**LangGraph** gives you the most structure for long, stateful work. A *checkpointer* saves the state after each step, so a run can stop, wait and resume, and Postgres is one of the stores it can use (see [just use Postgres](/writing/just-use-postgres/)). An *interrupt* pauses the graph for a person to approve. It streams results as they happen and works with any model. Our tutorial's verdict is that tests can check it node by node, but full tracing comes mainly with LangSmith, the tracing service from the same company.

**The OpenAI Agents SDK** gives you a small set of ideas: agents, handoffs, guardrails that check input and output, and sessions that remember the conversation. Tracing is switched on by default and goes to OpenAI's dashboard, and you can add your own exporters. It streams, and it can call other providers' models. Our own builds don't use it, so we have not measured it the way we measured the others.

**The Claude Agent SDK** gives you the most out of the box: built-in tools, subagents, hooks that run before and after each tool, permission checks, and support for MCP servers. MCP, the Model Context Protocol, is a standard way to plug tools into an agent. It is the quickest way to an agent that works on files and code. Our tutorial rates it best for coding, operations and research agents.

**A plain loop** gives you nothing for free, and complete control. Every check sits at an exact line that a unit test can reach, and it works with any model. You write state, checkpoints and streaming yourself.

## What each one costs you

There are three costs, and they are easy to miss in a demo.

**Lock-in.** Our tutorial rates the Claude Agent SDK's lock-in as high, because it is Claude-only. LangGraph's is medium, because your agent is shaped like its graph and its best tracing is LangSmith. A plain loop has none.

**Learning.** A graph framework is a new way of thinking about code. An SDK is a new set of rules about what runs when. Everyone on your team already knows how a `while` loop works.

**Hidden prompts.** Every framework sends the model text you didn't write: descriptions of built-in tools, handoff tools, output-format reminders. That text uses tokens, and it changes when you upgrade. Log the exact request your agent sends and read it at least once.

There is a fourth cost for agents that touch money. In the tutorial's comparison, tests can reach every step of a plain loop, but only partly reach the Claude Agent SDK's, because the loop is hidden inside it.

## Pick this when

| Pick | When | Watch for |
|---|---|---|
| Plain code loop | a wrong step moves money or changes records, and every step must be tested | you build state, streaming and checkpoints |
| LangGraph | the work is a known flow with branches and pauses for approval | the graph model to learn; best tracing is LangSmith |
| OpenAI Agents SDK | a few specialist agents pass one conversation between them | handoff prompts you didn't write; tracing goes to OpenAI unless you change it |
| Claude Agent SDK | internal agents that work on files, code, a shell or the web | Claude only; tests can't reach every step |
| Pydantic AI | small typed agents, or as the model layer under your own loop | for bigger agents, step the loop yourself |

If you'd rather not read a table, ask three questions in order.

{{drawing: loop-decide}}

The tutorial's own decision follows the first question. It writes the loop itself and uses Pydantic AI only to call the model, so the budgets and checks sit at exact places a test can reach. It says it would pick LangGraph for workflow-shaped agents and Agent Framework for a .NET team.

## The loop is the small part. Put it behind a port.

A *port* is a fixed shape that a part must fit, like a socket on the wall. The rest of the agent calls the port and never knows which part is plugged in.

{{drawing: loop-port}}

The [reference agent](https://github.com/dataagentsai/reference-agent) writes its own loop, with no framework, so that each layer of the harness is visible. Its harness has one call for a turn. A second module answers the same call with Pydantic AI owning the steps, chosen by one line of configuration. The router, the waits and the state don't know which loop ran.

Adapters for LangGraph and the Claude Agent SDK are planned, not built. Each must pass the same test cases unchanged, in at most 150 lines of adapter per port, without changing the harness to suit the framework.

The reference agent's notes put it plainly: if you can't say where your step budget, loop detection and cost ceiling live after adopting a framework, the framework has adopted you.

## What goes wrong

1. **Choosing by demo.** The framework that builds the quickest demo is not always the one you can test and run for a year.
2. **Checks inside the framework's callbacks only.** When the framework changes how its callbacks work, your rules move with it. Keep the rules in your own code and call them from the hooks.
3. **No budgets.** Some frameworks have a step limit, but none knows your money limit. A loop with no stop rule will find a way to loop.
4. **Never reading the real request.** The hidden prompt grows with each upgrade, and nobody notices until the bill does.
5. **The whole agent written in the framework's shapes.** Then swapping the loop means rewriting the agent.

## Seven questions to ask before you choose

1. If a wrong step happens, does it cost money or change someone's data?
2. Where exactly would my step, time and money budgets sit?
3. Can a unit test reach the check that runs before each tool call?
4. Does it work with the models I may need next year, not just this one?
5. Where do my traces go by default, and can I send them to my own store?
6. Can a run pause for hours waiting for a person, and survive a restart?
7. What text does it send to the model that I didn't write?

Choose the loop that fits the job, keep it behind a port, and spend the time you saved on the other 90%.

