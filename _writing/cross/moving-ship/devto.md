---
title: Building agents on a moving ship: what has settled, what is still open, and how not to get stuck
published: false
canonical_url: https://cleandataengineering.ai/writing/moving-ship/
description: Some parts of the agent stack have settled: OpenTelemetry for traces, Postgres for state, MCP for tools, JSON Schema for typed outputs, OAuth and OpenID Connect for identity, Git and CI for releases, and open table formats for data. Others are still moving, such as frameworks, agent-to-agent protocols, memory, evals, guardrail products, GenAI field names and the models themselves. Pick boring standards for the first group, put the second behind ports with contract tests, and keep the code that protects money in your own hands.
---

*Originally published at [cleandataengineering.ai](https://cleandataengineering.ai/writing/moving-ship/).*


Building an agent in 2026 feels like building on a ship at sea. New frameworks, new protocols and new models arrive every month. Whatever you pick, someone in the team will share a link next week saying a better one just launched.

So teams freeze. Some wait for things to settle. Others pick one big framework and hope it wins. Both end up stuck.

But the whole ship is not moving. Some planks are nailed down and will stay there. Some crates are still sliding about. The trick is to know which is which, and tie the crates down. This post is our judgement as of October 2026, from building the agent in our [Agent Harness tutorial](/learn/agent-harness/) and a reference agent beside it. Some of it will age, and we say where we are unsure.

## Planks and crates

Here is the picture to keep in your head.

{{drawing: ship-deck}}

A **plank** is a part of the stack that has settled. It is an open standard or a boring tool that many vendors already support, and you can build on it for years. A **crate** is a part that is still moving. The products change, the leaders change, and sometimes even the idea of what the part should do changes.

You stand on planks. You strap crates down.

## What has settled

These are the planks. For each one, more than one vendor supports it, the alternatives have faded, and we would bet a new agent on it today.

{{drawing: ship-columns}}

1. **OpenTelemetry for traces.** OpenTelemetry is the open standard for how code reports what it did: spans, metrics and logs. Every major trace store accepts it. Write your spans once and the backend becomes a line of config. We wrote a whole post on it: [OpenTelemetry is here to stay](/writing/opentelemetry-for-agents/).
2. **Postgres for state.** Conversations, checkpoints, approvals, the ledger of payouts, and even search vectors with pgvector can all live in one database you already know how to run. See [just use Postgres](/writing/just-use-postgres/).
3. **MCP for tools.** The Model Context Protocol is the agreed way an agent finds and calls tools. The big model vendors and most agent frameworks speak it. This one is honestly in between: the protocol itself has settled, but its sign-in and security pieces are still being worked out, so check the far end of every tool call yourself.
4. **JSON Schema and structured outputs.** JSON Schema is a standard way to describe the shape of data. Tool arguments and model replies are checked against it, and most model providers can now be told to reply in a given shape. In our harness, typed models generate the schemas and every tool argument is validated before any call.
5. **OAuth and OpenID Connect for identity.** These are the long-standing standards for signing in and passing permission. An agent acting for a person should carry that person's token, not invent its own login scheme.
6. **Git and CI for releases.** Prompts, model choices and policy are code. Version them together, test them in CI (continuous integration, the automatic checks on every change), and roll back the same way you roll back code.
7. **Open table formats for data.** Delta Lake and Apache Iceberg store tables as open files that many engines can read. Which of the two you pick is still a choice, but the move to open formats has settled.

## What is still moving

These are the crates. Each is useful today. None has a clear winner, and some may look very different in a year.

1. **Agent frameworks and loops.** LangGraph, the OpenAI Agents SDK, the Claude Agent SDK, Pydantic AI, Microsoft Agent Framework and plain code all take a different shape. We compared them in [choosing your agent loop](/writing/choosing-agent-loop/). Our own agent writes the loop by hand.
2. **Agent-to-agent protocols.** A2A is an open protocol for one agent to hand work to another. Our design uses it, but it is young, and how agents should hand off, limit and trace each other is still being argued.
3. **Memory products.** Long-term memory for agents is sold as its own product by several vendors. What to remember, and when to forget, is not agreed. Plain tables in Postgres do most of the job for us.
4. **Eval tooling.** pydantic-evals, DeepEval, promptfoo, Inspect, Ragas and the cloud evaluators overlap and keep changing. Your test cases are the lasting part; the runner is not.
5. **Guardrail products.** Content screens and prompt-attack detectors improve every few months. The checks that matter most are still rules in your own code, as we showed in [every guardrail, sorted](/writing/guardrails-sorted/).
6. **The GenAI telemetry field names.** OpenTelemetry has settled, but its standard names for model calls, such as `gen_ai.request.model`, are still changing. Keep them in one file so a rename is a one-line change.
7. **Model prices and the models themselves.** The best model for a job, and its price per token, change several times a year. Assume the model you launch with is not the one you will run next year.

For a map of every concern and the tools that fill it, see [the agent tech stack](/writing/agent-tech-stack/).

## Strap every crate behind a port

You cannot wait for the crates to stop. You can strap them down so that when one slides, nothing else breaks.

{{drawing: ship-straps}}

The strap has three parts.

1. **A port.** A port is a small interface in your own code that names the job, such as "call a model" or "write a span". Your agent talks only to the port, never to a product.
2. **Adapters.** An adapter is a short piece of code that makes one product fit the port. Swapping products means writing one adapter and changing one line of config.
3. **Contract tests.** These are the same tests, run against every adapter. A new adapter is only plugged in when it passes them.

Our reference agent enforces this mechanically. A rule in the build says that only the model module may import a provider's SDK, only the tools module may speak MCP, and only the state modules may touch the database. A new module gets those bans without anyone remembering to add them. Traces work the same way: the tutorial's agent sends them to Application Insights, the reference agent sends them to Langfuse, and switching between the two is one adapter and one line of YAML. For how to do it in code, see [swap anything, break nothing](/writing/harness-design-patterns/).

## Three rules for building on a moving ship

{{drawing: ship-rules}}

1. **Boring standards for the settled parts.** Don't wrap Postgres in a home-made database layer, and don't invent a tool protocol when MCP exists. Use the plank directly.
2. **Ports for the moving parts.** Every crate in the list above goes behind a port with adapters and contract tests.
3. **Your own code for anything that protects money.** The check before a ₹40,000 refund, the step budget on each turn, and the cost of each finished task belong in your code, at an exact step your tests can reach. In every comparison we made, these stayed in our own code. And if a product changes its behaviour, your money should not change with it.

## Mistakes we see often

1. **Betting the whole agent on one framework.** The framework owns the loop, the state, the traces and the retries. When it changes, or a better one arrives, the whole agent has to move.
2. **Building your own where a standard exists.** A home-made trace format, tool protocol or login scheme is a crate you nailed down yourself. It ages fast and nobody else can read it.
3. **Waiting for things to settle before shipping.** The crates may never stop. Teams that wait lose a year, and still have to choose.
4. **Putting a port in front of a plank.** Wrapping Postgres or OpenTelemetry in your own abstraction adds code without adding freedom. Ports are for crates.
5. **Product names in business logic.** If a vendor's name shows up in the code that decides a refund, swapping that vendor is a project, not an afternoon.

## Six questions to check your own agent

1. For each part of your stack, can you say whether it is a plank or a crate?
2. Do you use the standard directly for every settled part, or did you build your own?
3. Does every moving part sit behind a port that your agent talks to?
4. If your framework or model vendor vanished tomorrow, how many files would change?
5. Do your contract tests run against every adapter, including the one you might swap to?
6. Are the checks that protect money in your own code, at a step a test can reach?

Stand on the planks, strap the crates, and ship.

