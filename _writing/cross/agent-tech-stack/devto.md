---
title: The autonomous agent tech stack, one concern at a time
published: false
canonical_url: https://cleandataengineering.ai/writing/agent-tech-stack/
description: An autonomous agent has about fifteen jobs to do besides calling a model: the loop, the gateway, tools, context, memory, guardrails, identity, approvals, durability, tracing, evals, cost, release and more. Each job stays the same while the products doing it keep changing. This post gives one picture and one table, with two to four example tools per job across open source and the clouds.
---

*Originally published at [cleandataengineering.ai](https://cleandataengineering.ai/writing/agent-tech-stack/).*


A new agent product launches almost every week. Someone in your team shares the link and asks whether you need it. Is it a framework? A gateway? A memory store? An eval tool? Often the product page doesn't say, because it would like to be all of them.

There is an easier way to think about it. An autonomous agent, meaning a model that picks its own next step and calls tools until a job is done, has a fixed list of jobs to do around the model. We call each job a **concern**. The list hardly changes. The products that fill it change all the time.

So learn the jobs once. Then every new name becomes a short question: which job does it do, and do we already have something doing it?

## The whole stack, as a building

Start with the big picture. People meet the agent on the top floor. The models sit one floor down. Underneath everything is data and compute.

{{drawing: stack-building}}

The biggest floor is the **harness**: the plain software around the model that decides what it sees, what it may touch, and what happens when it gets something wrong. That floor holds the fifteen concerns in this post, in three rooms:

1. **One turn.** The loop, the context, the tools and the door to the model. These run every time someone sends a message.
2. **Around every turn.** Guardrails, identity, state and memory, knowledge, a person stepping in, and steps that survive a crash.
3. **Watch and change.** Tracing and cost tell you what happened. Evals and release config decide what is allowed to change next.

## Concept versus product

This is the one idea to take away. A **concept** is the job and its logic. A **product** is one thing doing that job somewhere: a library, a cloud service or a vendor's tool.

{{drawing: stack-swap}}

Take the model gateway. The job is "one governed door for every model call, which holds the keys, applies limits, logs the calls and screens what goes through". LiteLLM does that job in open source. Azure API Management does it on Azure. On AWS you can put API Gateway in front of Bedrock. Portkey sells it as a product. The card stays the same; the badge in the slot changes.

It also helps to know what *kind* of product a new name is. Our [AI Universe page](/learn/ai-universe/) sorts them into four kinds:

- **An implementation** does one concept's job. Langfuse does tracing; pgvector stores embeddings.
- **A bundle** packages many concepts under one name. Microsoft Foundry and AWS Bedrock AgentCore are bundles.
- **A protocol** is an agreed way for two parts to talk. MCP (Model Context Protocol) joins an agent to its tools; A2A joins an agent to another agent; OpenTelemetry joins any code to a tracing store.
- **A wrapper** is a convenience layer over something else. LiteLLM wraps many providers' APIs in one shape.

## The map: fifteen concerns, one row each

Here is the whole map. Each row gives the job in one sentence and a few example tools. Open-source tools come first, then cloud services with the cloud in brackets. These are examples, not a ranking, and the deeper page compares the options for each row.

| Concern | The job, in one sentence | Example tools |
|---|---|---|
| Control loop | Ask the model, run the tools it asks for, go round again, and stop within step, time and money limits. | plain Python, LangGraph, Microsoft Agent Framework (Azure), Agent Development Kit (Google Cloud) |
| Models | The trained weights that read the context and choose the next step. | Llama, gpt-oss, Gemini (Google), Claude (Anthropic) |
| Model access and gateway | One governed door for every model call: keys, limits, logs and screening. | LiteLLM, API Management AI gateway (Azure), Bedrock with API Gateway (AWS), Portkey |
| Tools and MCP | Let the model act only through typed tools that are checked before they run. | MCP Python SDK, FastMCP, AgentCore Gateway (AWS), A2A SDK for agent to agent |
| Context assembly | Build exactly what the model reads on each call, within a budget, with untrusted text fenced off. | your own code, Jinja templates for fixed replies, LlamaIndex, Bedrock prompt management (AWS) |
| [State and memory](/writing/just-use-postgres/) | Keep what each conversation and person needs, for as long as it should, and no longer. | PostgreSQL, Redis for short caches, Mem0, Cosmos DB (Azure) |
| Knowledge and retrieval | Find passages with their sources, filtered by what this person may see. | pgvector, Qdrant, Azure AI Search, Bedrock Knowledge Bases (AWS) |
| [Guardrails and policy](/writing/guardrails-sorted/) | Check what may go in, come out and run, before and after every step. | your own rules, Llama Prompt Guard 2, AI Content Safety (Azure), Bedrock Guardrails (AWS) |
| Identity and security | Know who is asking and whose authority the agent acts with, and attack it before someone else does. | PyJWT, Keycloak, Entra ID (Azure), PyRIT for red-teaming |
| [Human in the loop](/writing/human-in-the-loop/) | Approvals and hand-offs that the agent cannot grant itself. | Chatwoot as the staff desk, Teams cards through Logic Apps (Azure), Dynamics 365 Contact Center |
| Durability and workflows | Survive a restart, wait days for a person, and never run a payment twice. | DBOS, Temporal, Durable Task Scheduler (Azure), Step Functions (AWS) |
| [Tracing](/writing/tracing-agents/) | Record every step of every turn so you can see later what happened and why. | [OpenTelemetry](/writing/opentelemetry-for-agents/), Langfuse, Application Insights (Azure), Cloud Trace (Google) |
| [Evals](/writing/offline-evals/) | Prove the agent does the right thing on your own cases before each release. | pydantic-evals, DeepEval, promptfoo, Foundry evaluation (Azure) |
| [Cost](/writing/agent-cost-mistakes/) | Measure spend per unit of business work, and stop a turn that runs over budget. | your own meter, Langfuse cost tracking, API Management token metrics (Azure), Helicone |
| Release and config | Version the prompt, model and policy together, with a canary (a small share of traffic first) and a way back. | OpenFeature with flagd, Unleash, App Configuration (Azure), AWS AppConfig |

Two rows say "your own code" or "your own meter", and that is on purpose. When we compared products for the [Agent Harness tutorial](/learn/agent-harness/tech.html), we found none that builds the context the way an agent that handles money needs, and none that can tie spend to one finished piece of business work, such as one registered claim. Some jobs are still yours to write.

## Bundles fill several rows at once

A bundle is not bad. It just answers a different question. Instead of filling one row, it fills five or six.

{{drawing: stack-bundle}}

Bedrock AgentCore, for example, is AWS's set of harness parts: a runtime, memory, identity, a gateway and observability. Foundry Agent Service on Azure gives a hosted loop with tools, memory and tracing. Both are useful. But hold each one up against the table and mark which rows it fills. The rows that protect money, the evals that use your own cases and the cost of each business task usually stay with you.

## Which concerns to fill first

You do not need fifteen products on day one. You need the concerns that make one turn work, then the ones that make it safe, then the ones that let it change.

{{drawing: stack-stairs}}

1. **First, one turn works.** A loop, two or three tools, one door to the model, and a trace of every step from the very first run.
2. **Next, it is safe to use.** Guardrails, checking who is asking, state and memory, and a cost budget per turn.
3. **Then it can change and wait.** Evals before every release, a person approving risky actions, steps that survive a crash, and versioned release config.

Knowledge and retrieval join whenever the job needs documents. For many agents that is step two; for some it never comes.

## Six mistakes we see often

1. **Shopping before listing the jobs.** A team picks a platform, then finds out later which rows it left empty. Write the fifteen rows first, then shop.
2. **Treating a bundle as the whole stack.** One product name is not fifteen concerns. Mark the rows it fills, and own the rest.
3. **Letting a product own the loop when you need exact checks.** If a check must sit just before a payment tool runs, you need to see that step. Some frameworks and hosted agents keep the loop out of sight.
4. **Putting business rules in the gateway.** The gateway should hold keys, limits and screening. Rules such as "refunds over ₹40,000 need approval" belong in your code, or moving to another gateway becomes a rewrite.
5. **Hidden retries.** A retry buried inside a provider's SDK is invisible to your own retry budget and your trace. Keep retries and fallbacks in one place you control.
6. **Product names all over the code.** If "Langfuse" or "Entra" appears in your business logic, swapping it is a project. Put each product behind one small interface, so a swap is one adapter and one line of config.

## Five questions to check your own stack

1. Can you name the product, or your own code, that fills each of the fifteen rows today?
2. Which rows are empty, and is each one empty on purpose?
3. For each bundle you use, which rows does it fill, and which are still yours?
4. If one product disappeared tomorrow, how many files would you change to replace it?
5. Can you show the cost and the trace of one business task, from the first message to the final reply?

Learn the fifteen jobs once, and every new product name becomes a five-minute question instead of a week of worry.

