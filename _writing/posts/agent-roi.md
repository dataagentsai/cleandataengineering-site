---
title: Measuring agent ROI: what to count before you scale
date: 2026-10-31
subject: ai
audience: leaders
kind: leader-brief
draft: false
summary: An agent pays off only if the cost of each completed task, counting people as well as the model, falls without errors or complaints rising. Measure the same tasks before and after, include the hidden costs of review, upkeep and on-call, and prove it on a small pilot with a baseline before you scale. One page of numbers is enough to decide.
linkedin: "The agent handled 9,000 conversations last month" tells you nothing about whether it paid off. What counts is the cost of each completed task, before and after, with the review time, rework and upkeep included. Here is what to count, a worked example and a one-page scorecard.
deeper: /learn/agent-harness/cost.html
deeper_label: Cost, where the money goes, in the Agent Harness tutorial
cross: /writing/agent-cost-mistakes/
cross_label: Why your agent costs $4 per question: 9 cost mistakes
---

The pilot report looks wonderful. The agent handled 9,000 conversations last month, the model bill was ₹30,000, and the team is asking for budget to roll it out to every region.

Then someone asks a plain question: did it save us money? Nobody can say. The report counted conversations and tokens, not finished work, and it left out the people who quietly checked and fixed what the agent did.

An **agent** here means software that uses an AI model to take steps on its own, such as reading a claim, looking up the policy and approving a payout. This page covers what to count, the costs that hide below the waterline, and a one-page scorecard to decide whether to scale.

## Return on investment is a weighing scale

{{drawing: roi-scale}}

Return on investment, or **ROI**, is simply what you get back compared with what you put in. For an agent, both pans of the scale hold more than people expect.

The cost pan holds the model bill, the platform it runs on, and the people who review its work, fix its mistakes and keep it running. The value pan holds hours handed back to your team, fewer errors, faster answers and happier customers. If you weigh only the model bill against hours saved, the scale will always tip the right way, and it will be wrong.

## Count completed tasks, not conversations

The unit that matters is the **completed task**: a claim settled, a refund issued, a question answered so the customer didn't come back. Not a conversation, not a message, and not a token, which is the small piece of text a model is billed by.

A conversation that ends with "let me pass you to a colleague" is not a completed task for the agent. It is a task for a person, with a little extra cost on top. A payout that is reversed next week is not completed either. Count what finished, stayed finished and needed nobody to redo it.

## Before and after, on the same tasks

{{drawing: roi-before-after}}

Here is a worked example. **Every number in it is made up** to show the arithmetic; yours will differ.

A claims team handles 10,000 requests a month. Before the agent, a handler spends about 15 minutes on each, at an all-in cost of ₹600 an hour, so ₹150 a request. About 5% need redoing. That is ₹15 lakh for handling plus ₹75,000 of rework: ₹15.75 lakh a month, or about **₹158 per completed task**.

After the agent, on the same kinds of request:

| Cost line (example) | Per month |
|---|---|
| Model bill, about ₹3 a request | ₹30,000 |
| Platform: hosting, tracing, gateway | ₹70,000 |
| Handlers on the 4,000 requests handed back | ₹6,00,000 |
| Review: 2 minutes on each of the 6,000 the agent finished | ₹1,20,000 |
| Rework: 3% of all requests | ₹45,000 |
| Upkeep: tests, safety rules, on-call | ₹1,00,000 |
| **Total** | **₹9,65,000** |

That is about **₹97 per completed task**, down from ₹158. Handler hours fall from about 2,600 a month to about 1,300. Measure the rest the same way, before and after: time to resolution, and customer outcomes such as complaints and reversed decisions.

In a real pilot, not every line improves. Say complaints fall a little but reversed payouts rise from 40 to 55 a month. That doesn't sink the case, but it must be explained before you scale, because reversals cost money and trust.

About the model bill: ₹3 a request is a cautious example. Our own test agent, a claims assistant, costs well under a tenth of a US cent per turn by its own meter. A careless design can cost dollars per question instead, which is why the meter matters.

## The hidden costs below the water

{{drawing: roi-iceberg}}

Look at the table again. The model bill is ₹30,000 out of ₹9.65 lakh, about 3%. It is the part everyone sees, and the smallest. Below the water sit four costs that rarely appear in a pilot report:

1. **Review time.** People checking the agent's work, often more at the start than anyone planned.
2. **Upkeep of tests and safety rules.** Engineers call the tests **evals** and the safety rules **guardrails**. Both need someone to keep them current as products, policies and models change.
3. **On-call.** Someone must answer when the agent misbehaves at 2 a.m.
4. **Model price changes.** Prices move, and providers retire models. Ask what happens to cost per task if the price doubles. Here, the bill would go from ₹30,000 to ₹60,000, which is survivable. In a design where the model is half the cost, it is not.

Leave these out and the pilot will look better than the rollout ever will.

## Run a small pilot with a baseline

Don't measure "after" against a memory of "before". Pick one slice of work, such as one claim type in one region, and record its numbers for four weeks before the agent touches it. That record is your **baseline**. Then run the agent on the same slice for four weeks and compare.

Better still, run the agent on half the requests and leave the other half with people over the same weeks. Then a busy festival month or a policy change hits both halves equally, and the difference is the agent's doing.

Your engineers already have most of these numbers in the agent's own records. Ask them to read [why your agent costs $4 per question](/writing/agent-cost-mistakes/) and [online evals and monitoring](/writing/online-evals/), which covers joining complaints and reversals back to the run that caused them.

## The one-page scorecard

{{drawing: roi-scorecard}}

Everything above fits on one page: the same eight numbers, before and after, each marked better, worse, or a new cost to count. Cost per completed task, hours saved, error and rework rate, review time, time to resolution, complaints, reversals, and upkeep. If cost falls and nothing important gets worse, scale. If any customer line gets worse, find out why first.

## What goes wrong

1. **Counting conversations.** Volume rises while the work quietly flows back to people.
2. **Weighing only the model bill.** It is the tip of the iceberg.
3. **No baseline.** "It feels faster" is not a number.
4. **Different tasks before and after.** The agent gets the easy requests, people keep the hard ones, and the comparison flatters the agent.
5. **Review time assumed to be zero.** In the example it was larger than the model bill and the platform together.

## Five questions to ask before you scale

1. What does one completed task cost today, people included, and what did it cost before?
2. Were before and after measured on the same kinds of task, over the same weeks?
3. How much review, rework and upkeep time is in that number, and who is doing it?
4. Did complaints, reversals or time to resolution get worse anywhere?
5. If the model price doubled tomorrow, would the agent still pay off?

Scale the agent when the scorecard says so, not when the demo does.
