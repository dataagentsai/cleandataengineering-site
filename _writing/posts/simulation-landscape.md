---
title: AgentTwin vs LangWatch, Veris and friends: the simulation landscape
date: 2026-10-31
subject: ai
audience: builders
kind: decision
draft: false
summary: Tools that test agents in a simulation each pretend to be a different part of the world. Conversation simulators such as LangWatch Scenario play the customer, red-team kits such as PyRIT play the attacker, Strands ToolSimulator plays the tools, sandboxes such as Veris play the whole environment, τ²-bench is one fixed published world, and AgentTwin builds the world from your agent's spec and judges what changed in it. Pick by the risk you fear most, and expect to combine more than one.
linkedin: Three agent-testing demos in one week, and every one looked great. That's the trap. Each simulation tool pretends to be a different part of your agent's world: the customer, the attacker, the tools, the whole environment. Here is what LangWatch, PyRIT, Strands ToolSimulator, Veris, τ²-bench and our own AgentTwin each simulate, what each leaves out, and how to pick.
deeper: /learn/agenttwin/#others
deeper_label: AgentTwin explained: who else builds this, and how it differs
---

Say Neha's team is about to ship a claims assistant for a motor insurer. It reads claims, asks for documents and pays out up to ₹50,000. Before real policyholders meet it, she wants it tested in a simulation. In one week she sees three demos. Each shows a lifelike customer, a neat dashboard and a green score.

All three demos were good, and each tested something different: one played the customer, one an attacker, one the systems behind the agent. None showed what was left out.

This post maps the tools that test agents in a simulation: what each one pretends to be, what it leaves out, and when to pick it. One thing to know before you read on: **AgentTwin is our own work.** We have described it as plainly as the others, weak spots included, but weigh what we say about it with that in mind.

## The map: five kinds of tool, plus ours

A simulation puts the real agent in a pretend world. The tools differ in *which part* of that world they pretend to be. The [AgentTwin guide](/learn/agenttwin/#others) sorts them into five kinds, and each is good at one part.

{{drawing: land-map}}

Everything below comes from each tool's public documentation as of October 2026. Products change quickly, so check a detail before you rely on it.

## Island by island

### LangWatch Scenario, and other conversation simulators

**What it simulates:** the user. In LangWatch Scenario, developers write scenarios in code. A model plays the customer with a persona, and a model judge scores the chat against criteria. An autopilot mode lets the simulated customer improvise towards a goal. LangWatch also describes generating multi-step scenarios from a list of business policies, including where two policies overlap. It is open source (Apache 2.0), works with any agent through an adapter, and sits on the LangWatch platform for dashboards.

**What it leaves out:** the systems behind the agent. The tools are your real tools or your own mocks. There are no approvers or human desks acting on a clock, and no injected faults such as a lost reply. A promise the agent never kept is caught only if the judge happens to notice. And LangWatch does not publish a count of what is missing from your scenarios.

**Pick it when** realistic customers matter most: varied wording, moods, voice. The same kind of tool includes the Azure AI Evaluation Simulator, Maxim and Coval (for voice). AgentTwin uses LangWatch's simulated customer for exactly this job.

### PyRIT, and other red-team kits

**What it simulates:** an attacker. PyRIT is Microsoft's open-source red-teaming kit, built from four parts: **seeds** (attack goals), **converters** (rewrite one attack many ways), **attacker models** (read the reply and try again, turn by turn) and **scorers**.

**What it leaves out:** your business. PyRIT knows nothing of your rules, so it can't tell whether a refund was owed. Its neighbours differ. The Azure AI Red Teaming Agent wraps PyRIT. promptfoo writes attacks aimed at your app from a short paragraph about its purpose. garak probes the model itself, not the agent around it.

**Pick it when** you need breadth of attacks: many wordings of the same trick, without writing each by hand.

### AWS Strands ToolSimulator

**What it simulates:** the tools. A model writes each tool's reply and keeps shared state between calls. Runs are judged by goal-success evaluators. It is open source and works with Strands agents.

**What it leaves out:** the real rules. A model playing your order system can be talked into allowing what the real system refuses. Faults are possible only by asking the model to act them out.

**Pick it when** you have a long tail of tools nobody has described, and they are read-only and low-stakes. Not for a system whose rules matter.

### Veris, and other simulation sandboxes

**What it simulates:** the whole environment, often for training agents with reinforcement learning (learning by trial and reward). Veris, Collinear and Patronus are commercial. Veris tests any agent without changes, by catching its network calls (DNS interception), with model-powered mocks of the tools. Runs are seed-pinned so they can be repeated. Judging uses rubrics, verifiers and model graders.

**What it leaves out:** as far as its public material says, the rules come from the vendor's mocks and the scenario, not from your spec. A judge for things owed but never done, and injected faults, are not stated. Absent from the documents is not the same as absent from the product, so ask.

**Pick it when** you need any agent tested unmodified, at scale, on a managed platform with dashboards, or you want a training environment.

### τ²-bench, and other research worlds

**What it simulates:** one fixed, hand-coded domain, such as an airline, a retail shop or a telecom line. Runs are judged by checks on the end state. τ²-bench also has "dual control", where the customer has tools too and must act on their side, for example on their own phone. Its pass^k measure (run the same scenario k times; it passes only if all k pass) separates "worked once" from "works reliably". AgentDojo and AppWorld are in the same family.

**What it leaves out:** your domain. The world is theirs, not yours. And when we compared, τ²-bench does not check whether the agent read another customer's record.

**Pick it when** you want a proven, published yardstick: to compare against others, or to test your own judges. AgentTwin judged 2,472 recorded τ²-bench runs from the published policy and tools alone. On airline and retail it flagged exactly the rule-breaking writes τ²-bench flags (188 and 309).

### AgentTwin (ours)

**What it simulates:** the whole world, built from the agent's own spec, the written list of its tools, rules and promises. The [flight-simulator post](/writing/agenttwin-flight-simulator/) explains the idea. Customers can be scripted, state machines or model-played (through LangWatch). Systems are deterministic stand-ins that refuse the way the real system would. Approvers and desks act on a clock. Faults include slow systems, lost replies, stale reads and the model provider going down. Four judges read the world's state: did a write break a rule, was something owed never done, did the agent say something false, did it touch someone else's data. Each world states what it is faithful about. It is Apache 2.0.

**What it leaves out:** a lot, today. It reaches only agents that call their tools over MCP (the Model Context Protocol). It has no UI or dashboards. It does not judge tone or helpfulness. Its customers are basic, which is why it borrows LangWatch's. No stand-in has yet been checked against a real system. Scenarios run once with a scripted model, and repeated live runs are only in the lab. The tests are only as complete as the spec. And it has one builder and has not yet been used by an outside team.

**Pick it when** your agent changes records under written rules (refunds, renewals, payouts), calls its tools over MCP, and you can write its spec.

## Who covers what

Here is the same landscape as a grid. It covers only what the sources state. A question mark means the source doesn't say, not that the tool can't.

{{drawing: land-grid}}

Judging by the world's state means looking at what changed in the systems, not at what the agent said. The [oracle problem post](/writing/oracle-problem/) explains why that order of checking matters.

## Which one for your agent

Start from the risk you fear most, not from the tool you saw first.

{{drawing: land-pick}}

1. **If the risk is how people talk**, such as Hinglish, anger, half-finished sentences or voice, start with a conversation simulator.
2. **If the risk is hidden attacks**, such as an instruction planted in a claim note, add a red-team kit.
3. **If the agent changes records by rules**, you need a world judged by state. AgentTwin fits if your agent uses MCP and its spec is written. A sandbox like Veris fits if you need any agent unmodified, at scale, as a paid service.

Most agents answer yes to more than one question. That is normal: AgentTwin itself uses LangWatch for customers and PyRIT for attacks, and keeps only the world and the judges for itself.

## Mistakes when choosing

1. **Picking by demo.** Every demo shows a lifelike customer and a green score. Ask what decided the score and what was never simulated.
2. **Assuming one tool covers everything.** Each kind is good at one part. A conversation simulator with your own mocks behind it has not tested your systems' rules.
3. **Judging only the transcript.** "Sure, I'll take care of that for you!" reads well, and nothing was done. In [our five-scenario run](/writing/agent-met-real-customer/), a faulty agent passed every reply check and failed every world check.
4. **Letting a model play a system whose rules matter.** It can be talked into a yes the real system would refuse. A canned mock that always says "OK" proves nothing either.
5. **Mistaking a benchmark for your domain.** τ²-bench's airline is not your insurer. Use it to test your judges, not to sign off your agent.

## Seven questions to ask a vendor (or us)

1. Where do the rules come from: my spec, your mocks, or a model's prompt?
2. When a tool is simulated, does it refuse the way my real system would?
3. Is a run judged by reading the chat, or by reading the state of the systems?
4. Can a run fail because something owed was never done, even though nothing changed?
5. Can you inject faults, such as a lost reply, and move the clock so an approver goes quiet?
6. Does each world say what it is faithful about, and has that been checked against a real system?
7. Which agents can it reach without changes, and does it tell me what my scenarios are missing?

The right tool is the one that pretends to be the part of the world your agent is most likely to get wrong.
