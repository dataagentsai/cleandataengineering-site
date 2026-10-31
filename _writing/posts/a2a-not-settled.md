---
title: Agent-to-agent protocols (A2A): worth watching, not yet settled
date: 2026-10-31
subject: ai
audience: builders
kind: decision
draft: false
summary: Agent-to-agent protocols promise that agents built by different teams or companies can find each other and hand over work in one standard way. A2A is the leading one, and it is worth learning, but in October 2026 it is still moving. Don't bet your agent on it yet. Put hand-offs behind a port, pass a typed ticket with depth and fan-out limits, keep one trace across agents, and check identity at every hop, so plugging A2A in later is one adapter.
linkedin: "Our agent will just talk to their agent" is the most hopeful sentence in AI right now. Agent-to-agent protocols like A2A are worth watching, but they are not settled yet. Here is what A2A actually defines, how it differs from MCP, and five things to build now so you can adopt it later without a rewrite.
deeper: /learn/agent-harness/tech-17.html
deeper_label: agent-to-agent hand-offs in the Agent Harness tutorial, with the full comparison
---

Meera runs the support agent for a furniture shop in Pune. A customer asks what delivery to Nagpur will cost. The answer lives with a logistics partner, who now runs an agent of their own, built by another company, on another cloud.

Today, someone on Meera's team writes custom glue for that one pair of agents. Next month a second partner arrives, and someone writes the glue again.

Agent-to-agent protocols promise to end that. The best known is A2A. It is a good idea, and it is worth learning. It is also still moving. This post explains what it does, how it differs from MCP, and how to be ready for it without betting your agent on it.

## Two embassies and a standard envelope

Think of two embassies. They don't share staff, language or rules. They still work together, because both agree on the envelope: who it is from, who it is for, what is being asked, and a reference number for the reply.

{{drawing: a2a-embassies}}

An agent-to-agent protocol is that envelope for agents. It is an agreed way for an agent from one team or company to find out what another agent can do, ask it to do something, and follow the work until it is done. Neither side has to know how the other is built.

**A2A** (short for Agent2Agent) is the leading attempt. Google started it in 2025 and later handed it to the Linux Foundation, so no single company owns it now. It is built from a few simple parts:

1. **An agent card.** This is the notice board outside the embassy. It is a small document, published at a known web address, that says what the agent is called, what skills it offers, where to send requests, and how callers must sign in.
2. **A task.** This is the case file. When one agent asks another for work, the work becomes a task with an ID and a status that moves through a lifecycle: submitted, working, waiting for more input, then completed, failed or cancelled. Long work can stream updates instead of making the caller wait in silence.
3. **Messages.** These are the letters. Each message carries parts, such as text, a file or structured data. A finished task hands back its results as well.

It all travels over ordinary web requests, which is part of its appeal.

## MCP is for tools, A2A is for agents

People often mix up A2A and MCP. They solve neighbouring problems.

{{drawing: a2a-mcp-vs-a2a}}

**MCP**, the Model Context Protocol, connects an agent to a **tool**. A tool does exactly what it's told: "get order 4417" returns order 4417. The agent stays in charge of every step. We covered it in [MCP is here to stay](/writing/mcp-here-to-stay/).

**A2A** connects an agent to **another agent**. You don't tell the other agent how to do the work. You hand over a goal, such as "quote delivery of a 40 kg sofa to Nagpur by Friday", and it decides the steps, perhaps calling its own tools over MCP. The work can take minutes, can come back with a question, and can fail in ways a function call can't.

So the two fit together. MCP is how an agent reaches its tools. A2A is how one agent reaches another agent that has tools of its own.

## Where it stands in October 2026

In [building on a moving ship](/writing/moving-ship/) we split the agent stack into settled planks and sliding crates. MCP is close to a plank. A2A is still a crate.

That is our judgement, not a criticism. Several things are still open:

1. **The spec itself has kept changing** between versions. That is normal for a young standard, and costly for anyone who wrote against the old shape.
2. **Finding agents is unsolved at scale.** An agent card says what one agent can do. Knowing which agents exist, which version is live and which ones you are allowed to call needs a registry, and there is no agreed one.
3. **Trust across companies is hard.** Signing in between two organisations, and proving which person a request is really for, is where most of the real work sits.
4. **Limits and tracing are left to you.** How deep a chain of hand-offs may go, who pays for it, and how one trace follows a request across companies are not settled by any protocol today.

Our own tutorial reached the same verdict. In the [17 · Agent-to-agent](/learn/agent-harness/tech-17.html) page, the claims agent's design picks A2A endpoints with a typed hand-off ticket, depth and fan-out limits and one trace. Its status is honest: designed, not built. Inside one service, a plain in-process hand-off is fine.

And before any protocol, ask whether you need a second agent at all. Most teams don't, as we argued in [one agent or many](/writing/one-agent-or-many/).

## Stay ready without betting on it

You don't have to choose between adopting A2A now and ignoring it. Build what any hand-off needs, and leave the wire format for later.

{{drawing: a2a-port}}

1. **Keep hand-offs behind a port.** A port is a small interface in your own code that names the job, here "hand this work to that agent". Your agent calls only the port. Today the adapter behind it can be a plain function call inside the same service. Later, an A2A adapter can sit beside it, and switching is one adapter and one line of config.
2. **Pass a typed hand-off ticket.** The receiver needs everything, not a chat summary. Make the ticket a typed object with named fields, checked before it leaves. More on it below.
3. **Set depth and fan-out limits.** *Depth* is how many hand-offs deep a chain may go. *Fan-out* is how many agents one agent may call for a single task. The harness enforces both, not the agents, so two agents can never pass a task back and forth until your money runs out.
4. **Keep one trace across agents.** Every hand-off carries the trace ID of the original request, so the whole journey shows up as one story with each agent's cost and time on its own part. [Tracing autonomous agents](/writing/tracing-agents/) shows the setup.
5. **Check identity at each hop.** Every receiving agent checks two things: which agent is calling, and which person the work is really for. Pass a narrowed permission for this one task, never the user's full sign-in, and let each agent check it again before it acts.

None of these five depend on A2A, and you would need all of them on top of A2A anyway.

### The typed hand-off ticket

Here is what Meera's agent sends to the logistics agent.

{{drawing: a2a-ticket}}

Each field has a job. The **goal** and **facts** stop the receiver guessing. The **limits** and **deadline** carry the customer's constraints, which a summary would drop. **Depth** and **fan-out** let the next agent know how much room is left. The **trace ID** keeps one story. **On behalf of** says whose permission this is.

The [AI Assurance Catalog](https://github.com/dataagentsai/ai-assurance-catalog) puts the reason plainly: silent context loss at a hand-off "produces confidently wrong work with no error anywhere in the trace" ([AAC-0062](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0062.yaml)). A typed ticket, with a test that checks nothing the receiver needs is missing, is the fix. Its neighbours, AAC-0061 to AAC-0067, cover loops, budgets, failures and tracing.

When A2A does settle, this ticket simply rides inside an A2A message as structured data. Nothing about it has to change.

## Mistakes we see often

1. **Writing the protocol into business logic.** If A2A field names appear in the code that decides a refund, every spec change becomes a project.
2. **Treating another agent like a tool.** An agent can take minutes, ask a question back, or fail halfway. Code that expects an instant answer will hang or guess.
3. **Trusting the agent card.** A card is a claim about what an agent can do, written by its owner. Test what the agent actually does before you route real work to it.
4. **Forwarding the user's full sign-in.** The third agent in a chain should hold a permission for one task, not the keys to the customer's account.
5. **No limit on depth.** Without it, a chain of polite agents can loop or fan out until the bill tells you.
6. **Waiting for the standard before building the basics.** Tickets, limits, traces and identity checks are needed whatever protocol wins. Build them now.

## Six questions to check your own design

1. Does your agent hand work to other agents through one port, or is hand-off code spread across the loop?
2. Is every hand-off a typed ticket, and is there a test that it carries everything the receiver needs?
3. What stops a chain of hand-offs from going too deep or calling too many agents?
4. Can one trace show the whole request across every agent, with each agent's cost on its own part?
5. At each hop, who checks which agent is calling and which person the work is for?
6. If you adopted A2A next quarter, how many files would change?

Watch A2A closely, build the hand-off basics today, and plug the protocol in when it stops moving.
