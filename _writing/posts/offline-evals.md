---
title: Before it ships: offline evals for autonomous agents
date: 2026-10-31
subject: ai
audience: builders
kind: explainer
draft: false
summary: An agent can be wrong without throwing a single error, so you need a test it must pass before every release. Build a golden set of cases with known right answers, play whole conversations against a simulated world, judge each case with code first and an LLM judge only where code can't see, compare with the last release slice by slice, and turn every production failure into a new case.
linkedin: Your agent's average score went up, so you shipped it. Then refunds broke, because one slice got worse and the average hid it. Here is how to build offline evals that block a bad release: golden sets, scenarios, code checks before judges, and a baseline that is the last release, not perfection.
deeper: /learn/eval-harness/
deeper_label: the Eval Harness tutorial, with every check and pattern
---

A customer asks the support agent for a refund. The agent replies, *"Done, ₹3,499 is on its way to your card."* The reply is polite, quick and well formatted. No tool threw an error. And no refund was ever issued.

Unit tests won't catch that. Latency is fine, nothing turns red, and the dashboard looks healthy. The agent was wrong without failing.

**Offline evaluation** is how you catch it before customers do. "Offline" means it runs before release, in your build pipeline, on cases you wrote down, not on live traffic. This post covers its five parts, and the loop that keeps it honest.

## A driving test, not a vibe check

{{drawing: eval-driving-test}}

Nobody hands over car keys because a learner "seemed fine around the block". There is a test, with set manoeuvres, an examiner with a checklist, and a clear pass or fail. Fail it, and you practise and come back.

Treat a new agent release the same way. A new prompt, model or tool is a new driver. Before it gets the keys, it drives a fixed route, and something other than its own confidence marks the sheet. Ten people trying it in a chat window for an afternoon is not that: it can't be repeated next week to see whether anything got worse.

## Golden sets: cards with known right answers

{{drawing: eval-golden-cards}}

A **golden set** is a list of single cases, each with an input and a known right answer. Think of each case as an index card:

- **the question:** what the customer says, plus the facts in the world before (the order, its date, its status)
- **the expected tool:** which tool the agent should call, or must not call
- **the expected outcome:** what should be true afterwards, such as "refund issued" or "handed to a person"
- **the slice:** a label for the kind of case, such as returns, cancellations, a Hindi message, or an order over the approval limit

Three rules make a golden set worth having.

1. **Generate the edges from the rules.** If the policy says returns within 30 days, write cases at day 29, day 30 and day 31. In the reference agent from our [Agent Harness tutorial](/learn/agent-harness/test-golden.html), the golden set is 35 cases, each naming the boundary it tests.
2. **Cover every slice.** A set that is 90% easy refunds will score well and prove little. Count the cards per slice and fill the thin ones.
3. **Freeze it.** The set lives in Git. You never edit a case to make a failing run pass. If a case is genuinely wrong, retire it in a reviewed change with the reason written down.

The [AI Assurance Catalog](https://github.com/dataagentsai/ai-assurance-catalog) puts the first rule plainly in [AAC-0001](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0001.yaml): a version-controlled set of representative inputs with expected outcomes, and every release candidate scored against it.

## Scenarios: whole conversations in a pretend world

A golden card tests one turn. Real trouble often takes several: the customer changes their mind, a tool fails twice, a person approves something late. For that you need a **scenario**: a short story with a customer, what they say in order, and what the world looks like before. It runs the real agent against simulated systems and a clock you can fast-forward, then checks what is true in that world afterwards. The claims assistant in our tutorial has 29 scenarios, with names like *a-large-payout-waits-for-a-handler* (a ₹25,001 payout is not made until a person approves) and *the-handler-approves-it-twice* (a double click still pays once). All 29 pass at the last run.

Building that pretend world is a job of its own; our tool for it, AgentTwin, gets its own posts later.

## How a case is judged: code first, judge last

{{drawing: eval-scoring}}

When a case finishes, ask questions in this order, and stop at the first one that fails.

1. **Did the right tool run?** Code can check this exactly from the trace. If the reply says "refunded" and `issue_refund` was never called, the case fails.
2. **With the right arguments?** The right order id, the right amount, not ₹34,990 when it should be ₹3,499. Check the arguments yourself: one evaluation library we tried compares tool names, not arguments.
3. **Did the world end up right?** Read the pretend systems afterwards. One refund, not two. Nothing written for another customer. Nothing paid that needed approval.
4. **Only then, an LLM judge.** An **LLM judge** is a second model asked to grade the reply. Use it for things code can't check, such as "is every sentence supported by what the tools returned?" or "is the tone right for an upset customer?"

The first three are cheap, exact, and give the same answer every time. The judge costs money on every case (about $0.0005 per call in our spike) and can be wrong in ways that look confident.

So a judge must earn the right to block a release. Score it against a set that people have labelled, and measure how often it agrees with them ([AAC-0084](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0084.yaml)). Probe its known biases, such as preferring longer answers or whichever answer comes first ([AAC-0085](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0085.yaml)). Run the same case several times and with the instructions reworded, and check the verdict holds ([AAC-0086](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0086.yaml)). Until it passes all three, the judge only reports. That is the rule in our harness: only exact rules and calibrated judges may block.

Code checks need checking too. Our first "promised but not done" rule raised 3 findings, all false alarms: the replies said "nothing has been paid yet". Once it skipped negations, it raised 0.

## Baselines: beat the last release, not perfection

{{drawing: eval-baseline}}

Perfection is not a useful target. The useful question is: **is this release worse than the one customers have today?**

So run the new release and the current one on the same frozen set, and compare them case by case. [AAC-0013](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0013.yaml) asks for wins, losses and ties per case, because an unchanged average often hides a release that fixed one thing and broke two.

Then break the score down by slice ([AAC-0017](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0017.yaml)). In the picture, the average barely moved, but Hindi messages got worse. An average alone would have shipped that.

The reference agent keeps its baseline in a committed file: the golden pass rate, the context size, and the cost per task ($0.000945). It works like a ratchet. Each number may stay the same or get better, but never worse.

## The release gate: what blocks

A **release gate** is a short file that lists what must be true before a release goes out. Your build pipeline runs it on every change. If any line fails, the release is blocked, with no "ship it anyway" button.

A sensible gate blocks a release when:

- any must-pass check fails; in our harness, picking the right tool and saying what the reply must say both need a pass rate of 1.0, so one miss blocks
- any slice is worse than the last release
- any attack case succeeds, judged by the world afterwards: something was paid, written or leaked
- a judge that hasn't been checked against people tries to block (it may only report)
- a result is uncertain; uncertain goes to a person and is never counted as a pass

## Every production failure becomes a new card

{{drawing: eval-loop}}

The golden set is never finished. Something will go wrong in production that no card covered. When it does, open the trace (our post on [tracing agents](/writing/tracing-agents/) covers how to keep one you can replay), find the step that went wrong, and write it down as a new card or scenario with the right answer. Fix the agent. The new card now runs before every release, so that mistake can't ship again.

To be honest about our own state: turning a production turn into a scenario in one step is not built yet in the claims assistant. Until it is, a person writes the card by hand. What matters is that the card gets written.

## Four mistakes we see often

1. **Only an average score.** One number for the whole set hides the slice that broke. Always look at slices and at per-case wins and losses.
2. **A judge that was never checked against people.** If nobody measured how often the judge agrees with a human, every score it gives is decoration. Let it report, not block.
3. **A golden set that never changes.** The set you wrote at launch tests last spring's agent. Add every production miss, and add a card for every new tool and every new rule.
4. **Testing only the final text.** "Your refund is on its way" can be word-perfect while nothing was refunded. Check the tools, the arguments and the world, then the words. The checks that run while the agent works are a different job, covered in [every guardrail your agent needs](/writing/guardrails-sorted/).

## Six questions to check your own agent

1. Do you have a frozen golden set in Git, and can you say how many cards each slice has?
2. Do your cases sit on the edges of your rules: one day, one rupee, one step either side of each limit?
3. When a case is judged, do you check which tool ran, with which arguments, and what changed in the world, before you look at the words?
4. If you use an LLM judge, do you know how often it agrees with people, and does it give the same verdict twice?
5. Is a release compared with the last release, case by case and slice by slice?
6. When something failed in production last month, is it a card in your set today?

An agent that hasn't passed a test you wrote down hasn't passed anything.
