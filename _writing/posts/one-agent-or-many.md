---
title: One agent or many? When multi-agent is a mistake
date: 2026-10-31
subject: ai
audience: builders
kind: decision
draft: false
summary: Splitting work across several agents looks tidy on a whiteboard, but every hand-off loses context, every conversation between agents costs money, and every extra agent is one more thing to trace and test. Go multi-agent when permissions, skills, parallel work or sheer size truly demand it. Otherwise, one agent with a router and good tools does the job better.
linkedin: A "team" of five agents looks great in a demo. In production it means five hand-offs that drop details, a bill that multiplies, and agents politely passing the same task back and forth. Here is when multi-agent really helps, when one agent with good tools is better, and five safety rules if you do split.
deeper: /learn/agent-harness/tech-17.html
deeper_label: agent-to-agent hand-offs in the Agent Harness tutorial, with the full comparison
---

A new agent project often starts with an org chart. There's a planner agent, a research agent, a writer agent, a reviewer agent, and a manager agent to keep them in line.

Then real work arrives. The writer gets a summary of the research instead of the research, and fills the gaps with guesses. The reviewer sends the draft back, the writer sends it forward again, and they keep going. The bill for one question is several times what anyone expected, and when the answer is wrong, nobody can tell which agent got it wrong.

Splitting work across agents (often called *multi-agent*) is sometimes the right call. More often it's an org chart drawn too early. This post helps you tell the two apart.

## Too many cooks

Picture a kitchen. On one side, five cooks each make one part of the dish and pass notes about it. On the other, one cook has a good set of knives, a recipe card and a timer.

{{drawing: multi-cooks}}

The five cooks are not five times faster. They spend their time on notes and waiting. Each note leaves something out. And when the dish comes out too salty, every cook points at the next one.

The single cook with good tools does each step with the whole dish in mind. That cook is what most agents should look like: **one agent**, meaning one model running one loop, with tools for each specialist job.

## When many agents really help

There are four honest reasons to split.

1. **Separate permissions or separate teams.** The agent that reads medical records must not be the agent that can send emails. If two parts of the work need different access, or are owned by different teams with their own release cycles, a boundary between agents is a real boundary.
2. **Truly different skills.** Not "a research step and a writing step", which one agent handles fine with two tools, but genuinely different jobs, such as one part that writes and runs code and another that talks to customers, each needing its own instructions, tools and tests.
3. **Parallel, independent work.** Checking fifty supplier invoices that don't depend on each other can be split across workers and run at the same time. The key word is *independent*: if the workers need each other's results, you are back to passing notes.
4. **A context too big for one window.** The context window is how much text the model can read at once. If one task really needs more than fits, sub-agents can each read a slice and send back a short summary.

## When many agents hurt

Each extra agent brings costs that don't show up in the demo.

**Every hand-off loses context.** A hand-off is when one agent passes work to another. The sender writes a summary, and a summary always leaves something out.

{{drawing: multi-handoff}}

Say a customer, Priya, writes: "Refund order 4417, but not the gift wrap, and I need it by Friday because I travel on Saturday." By the third agent, the note may just say "refund order 4417". The [AI Assurance Catalog](https://github.com/dataagentsai/ai-assurance-catalog) puts the danger plainly: silent context loss at a hand-off "produces confidently wrong work with no error anywhere in the trace" ([AAC-0062](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0062.yaml)).

**Costs multiply.** Every message between agents is a model call, and each agent re-reads its own instructions and history on every step. Five agents talking means far more calls than one agent doing the same work. We covered the other ways this bill grows in [9 cost mistakes](/writing/agent-cost-mistakes/).

**Loops and ping-pong.** Agent A decides the task belongs to agent B. Agent B decides it belongs to A. Neither is wrong by its own rules, so it goes on until something runs out, usually your money.

**Harder tracing and testing.** With one agent, a bad answer has one place to look. With five, you have to rebuild who said what to whom. Testing is harder too, because each agent depends on what the others send.

**Failures spread.** If one agent times out or returns nonsense, the next agent may treat that nonsense as fact and build on it. One bad step becomes a bad answer.

## The middle path: one agent, a router and specialist tools

You can get most of the benefit of specialists without most of the cost.

{{drawing: multi-middle}}

A **router** is a small piece of code that reads the request first and picks a path. In the tutorial's claims agent, the router asks four questions in a fixed order, using plain rules and no model at all:

1. Does this need a person, for example someone was hurt? Hand it to the human desk.
2. Is this something we must refuse, for example "will my claim be approved"? Send a reply written in advance.
3. Is it one simple, read-only question about one claim? Answer it straight from the claims system, with no model call.
4. Anything else goes to the one agent and its loop.

Inside that loop, the "specialists" are tools. A tool can be a database lookup, or it can be a **sub-call**: a single model call with its own narrow prompt, such as "summarise this 40-page document". The difference from a sub-agent is control. A sub-call does one job and returns. It doesn't decide who works next, and it can't hand the task back.

The tutorial's verdict for the claims agent is the same. It runs as one agent, and handing work inside one service is listed as "fine within one agent". Agent-to-agent hand-offs over an open protocol are designed but not built yet, and only with limits attached ([17 · Agent-to-agent](/learn/agent-harness/tech-17.html)).

## Three questions to decide

Before you draw the org chart, ask these in order.

{{drawing: multi-decide}}

If the first "yes" comes from permissions, split along that line and nowhere else. If it comes from independent work, use workers that each do one piece and report back to one place, rather than agents that talk to each other. If every answer is no, start with one agent and a router. You can always split later, once a trace shows you exactly where the boundary belongs.

## If you do go multi-agent

Sometimes the answer really is many agents. Then five rules keep it safe.

{{drawing: multi-card}}

1. **Complete hand-off payloads.** Pass a typed ticket, not a chat summary: the goal, the facts, the limits and the deadline, each as a named field. A test should check that nothing the receiver needs is missing ([AAC-0062](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0062.yaml)).
2. **One budget for the whole system.** Token, step and money limits must cover all agents together. In the catalog's words, "ten agents each within budget is not a system within budget" ([AAC-0064](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0064.yaml)).
3. **Loop detection.** The harness, not the agents, counts how often the same task has been handed over and stops it, with a test proving the stop works "rather than discovered in a bill" ([AAC-0063](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0063.yaml)). A depth limit and a fan-out limit, meaning how many agents one agent may call, do the same job.
4. **Per-agent attribution in one trace.** One trace for the whole request, with each agent's cost, time and quality marked on its own part. Without it, you can see the system is slow and expensive but never which part ([AAC-0067](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0067.yaml)). [Tracing autonomous agents](/writing/tracing-agents/) shows how to set that up.
5. **Contain one agent's failure.** A sub-agent that errors, times out or returns garbage should make the answer predictably worse, not corrupt it or hang the system ([AAC-0065](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0065.yaml)).

Two more checks belong with these. Test the routing itself, including the cases where nothing should be delegated at all ([AAC-0061](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0061.yaml)). And when two agents can disagree, write down which one wins and test it, rather than letting whichever answer arrived last win ([AAC-0066](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0066.yaml)).

## Mistakes we see often

1. **Splitting by job title.** "Researcher, writer, reviewer" mirrors a human team, not a real boundary. Those are usually three tools or three steps.
2. **Letting agents chat freely.** Open conversation between agents is where loops and runaway costs come from. Hand-offs should be one-way tickets with limits.
3. **A budget per agent only.** Each agent stays under its limit while the whole system spends far more than anyone planned.
4. **A model as the manager.** A supervisor agent deciding every hand-off adds a model call to each step. A rule-based router is faster, cheaper and testable.
5. **Splitting before measuring.** Without a trace of the single-agent version, you don't know where the real boundary is.

## Six questions to check your own design

1. Which of the four reasons (permissions, skills, parallel work, size) justifies each boundary between your agents?
2. Could each "agent" be a tool or a single sub-call instead?
3. What exactly does a hand-off carry, and is there a test that it carries enough?
4. What is the most one request can cost across all agents together?
5. What stops two agents passing the same task back and forth?
6. When the answer is wrong, can one trace tell you which agent made it wrong?

If you can't answer the first question, you don't need many agents yet; you need one good one.
