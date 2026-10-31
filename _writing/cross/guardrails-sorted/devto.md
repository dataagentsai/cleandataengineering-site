---
title: Every guardrail your agent needs, sorted: must-have, should-have, rule or judge
published: false
canonical_url: https://cleandataengineering.ai/writing/guardrails-sorted/
description: "Guardrails" sounds like one product you buy. In a working agent it is about fifty small checks, each with a job, a place and a price. We sorted 57 common ones. 39 are plain rules in code, and only 2 need an LLM judge. Here are the labels, the pictures, and the 15 to build first.
---

*Originally published at [cleandataengineering.ai](https://cleandataengineering.ai/writing/guardrails-sorted/).*


Ask a team how their agent is protected and you often hear one word: *guardrails*. Usually it means one product sitting in front of the model, screening what users type.

That's one guardrail out of about fifty. The others sit in different places, catch different things, and most of them are a few lines of ordinary code.

We collected the common ones, from our own agents and from the tests in the [AI Assurance Catalog](https://github.com/dataagentsai/ai-assurance-catalog). There are 57. This post sorts them so you can see which matter first.

## Six labels on every guardrail

Before a list of 57 can be useful, each one needs labels.

{{drawing: guard-card}}

- **Priority.** *Must* means every agent that can change something in the real world. *Should* means most agents. *Could* depends on the use.
- **Where it sits.** At the front door, before or after the model, before or inside a tool, after a tool, across the whole run, or in the logs.
- **How it decides.** A rule in code, a small classifier, an LLM judge, a person, or a platform setting.
- **If it fires.** Block, redact, refuse the call, stop the run, wait for a person, or just flag.
- **Concern.** Security, safety, privacy, truth, correctness, cost, reliability or human oversight.
- **Proven by.** The test that shows it really works. A guardrail without a test is a hope.

## Most guardrails are plain rules

Sort all 57 by how they decide and the picture is clear.

{{drawing: guard-how}}

**39 of 57 are rules in code.** "Did the user ask for this refund?" "Is the amount under the limit?" "Did a tool really return this order number?" Each is an `if` statement. It runs in microseconds, costs nothing, and gives the same answer every time, so you can test it like any other code.

**Small classifiers** handle meaning that a pattern can't catch: harmful content, personal data, reworded attacks. They are cheap and fast, but they give a score, not a certainty.

**Only 2 need an LLM judge:** "is every sentence supported by the documents?" and "is the tone right?" Those questions need nuance, so they're worth the cost and the second of waiting.

## Where they sit

Guardrails sit all along a turn, not just on the user's message.

{{drawing: guard-where}}

The two busiest spots are **after the model writes** and **before a tool acts**. That makes sense. The first is where the model can say something wrong. The second is where it can *do* something wrong.

## The 15 to build first

If your agent can change anything, such as data, money or messages, start with these must-haves.

| Guardrail | What it catches | How |
|---|---|---|
| Verify who is asking | a forged or expired sign-in | rule |
| Kill switch | an operator needs to stop the agent now | rule |
| Sensitive topics go to a person | injury, self-harm, legal threats | rule |
| Known injection phrases | "ignore your previous instructions" | rule |
| Harmful content, in and out | hate, violence, self-harm | classifier |
| Only the tools this user may use | admin tools offered to a normal user | rule |
| Output matches its schema | broken JSON, missing fields | rule |
| Claims an action that didn't happen | "I've booked it" when nothing was booked | rule |
| Names or numbers no tool returned | a made-up order number or price | rule |
| The user actually asked for this | a refund triggered by a planted note | rule |
| Arguments are valid and in range | ₹4,00,000 when the limit is ₹40,000 | rule |
| Approval for risky actions | a large payout, a mass email | person |
| The tool checks identity again | the agent's token used for someone else | rule |
| Fence the result as data | text in a document read as orders | rule |
| Step, time and money budget | a run that loops for 20 minutes | rule |

Thirteen of the fifteen are rules. You can build most of them in a week.

## Rule first, classifier next, judge last

When you add a guardrail, start on the bottom stair.

{{drawing: guard-ladder}}

Use a classifier only when a rule can't see the problem. Use an LLM judge only when a classifier can't either. Every step up adds cost and delay, and you can be less sure the check behaves the same way every time.

## Five mistakes we see often

1. **Screening only the user's message.** Attacks also arrive through tool results, emails and documents. Many setups never check those.
2. **Failing open.** The guardrail service times out and everything is let through. A guardrail that errors should block.
3. **An LLM judge where a rule would do.** "Is the amount under ₹40,000?" doesn't need a model. It needs an `if`.
4. **Writing the guardrail in the prompt.** "Never refund without approval" in a prompt is a request, not a rule. Put it in code, before the tool.
5. **Never measuring it.** A guardrail that blocks 30% of good requests is as broken as one that blocks nothing. Watch how often each one fires, and test both cases.

## The full list

All 57 are in the [guardrail catalog](/learn/agent-guardrails/). You can filter by priority, by how they decide, and by concern. Each one comes with example tools and the test that proves it works. It will keep growing; if you rely on one that's missing, tell us.

