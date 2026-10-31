---
title: It passed offline. Now watch it live: online evals and monitoring
date: 2026-10-31
subject: ai
audience: builders
kind: explainer
draft: false
summary: Passing the release gate proves an agent handles the cases you wrote down, not the ones customers bring. After release, quick checks keep running inside every turn, slower scoring re-reads finished turns, and a handful of rates are compared with the agent's own normal from last week. Add a test customer that asks known questions on a schedule, join complaints and returns back to the run that caused them, and turn every live failure into a new offline case.
linkedin: Your agent passed every offline test, so you shipped it. Three weeks later the provider quietly updated the model and one guardrail started refusing a tenth of all turns. Nothing threw an error. Here is what to watch after release, the alert rules we actually use, and the loop that turns each live failure into a test.
deeper: /learn/agent-harness/eval-online.html
deeper_label: online eval, alert rules and dashboards in the Agent Harness tutorial
---

The support agent passed its release gate on Friday. Every golden case was green, no slice got worse, and it shipped.

On Tuesday, Priya on the support desk notices something odd. More customers than usual are being handed to a person. Nothing has crashed and every request returns a reply. When someone finally looks, one guardrail has been refusing perfectly ordinary refund questions since Sunday night.

Offline evals, covered in [before it ships](/writing/offline-evals/), prove the agent handles the cases you wrote down. They can't see the cases customers bring, a provider changing the model under you, or a tool that slows down at month end. This post is about the other half: watching the agent once it is live.

## A dashboard, and a bell

{{drawing: live-dashboard}}

A driver doesn't read engine logs while driving. They glance at a few gauges, and a lamp comes on when something leaves its normal range. Running an agent is the same: a small dashboard, and alert rules that call a person when a needle goes into the red.

Both read the same record. Every turn writes a **trace**, a tree of timed steps covering each model call, tool call and check. Our posts on [tracing agents](/writing/tracing-agents/) and on [OpenTelemetry](/writing/opentelemetry-for-agents/) cover how to record one. Here we only read it.

## Two speeds: inline and online

{{drawing: live-two-speeds}}

**Inline checks** run inside every turn, before the customer sees the reply. In the reference agent from our [Agent Harness tutorial](/learn/agent-harness/eval-inline.html) there are 8 check points, and each check must finish in under 50 milliseconds or the app refuses to start. So they are all plain rules today, and if one fails the customer gets a safe reply instead.

**Online evals** run after the turn, on stored traces. A watch job reads finished turns every 60 seconds and runs 24 rules, such as "the reply claims an action that didn't happen" or "the same failing tool was called again". The reply has already gone, so an online eval can't fix it. It can only raise a finding: page someone now, open a ticket for this week, or add a point to a trend.

Cheap rules can score every finished turn, and ours do. An **LLM judge**, a second model asked to grade a reply, costs money each time, so it scores only a sample. The [AI Assurance Catalog](https://github.com/dataagentsai/ai-assurance-catalog) asks for exactly this in [AAC-0014](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0014.yaml): score a sample of live traffic on the same rubrics you use offline, and alert when a score crosses its threshold. It is the only stage that sees what real customers actually type.

To be honest about our own state: the sampled judge is designed, not built. The plan is a small self-hosted model rather than a big paid one.

## What to watch

Every request can succeed while the agent stops doing its job, so the useful numbers are rates, not single errors. Here is what we watch, with each one's alert rule in the reference agent.

| Watch | Alert rule |
|---|---|
| Guardrail hits | one rule refuses more than 10% of turns in an hour |
| Hand-offs | a hand-off rule's cases are mostly closed by the desk as "the agent could have done it": over 30% in a week |
| Cost per task | the cost of the 95th-percentile run is twice last week's |
| Latency | the slowest 5% of turns take over 20 seconds, for 10 minutes |
| Errors | more than 5% of turns fail in 10 minutes |
| Judge scores on samples | designed: the sampled score falls below its offline threshold |

Two habits make these rules trustworthy. Every rate needs a minimum amount of traffic, so a quiet hour with one bad turn isn't "100% failed". The turn-failure rule needs at least 10 turns, for example. And every alert has a **severity** that says what happens next: *page* means a person looks now, *ticket* means this week. A slow trend goes on the dashboard, not into someone's phone. A trend that pages is a trend nobody reads the second time.

The dashboard itself has four rows, each answering one question for one audience: is it working, is it doing its job, is it right, and what does it cost.

## Compare with its own normal

{{drawing: live-baseline}}

A fixed limit like "alert at 10% hand-offs" is wrong for most agents. A returns agent in the week after Diwali hands off more than in a quiet week in March. The better question is: **is today different from this agent's own normal?**

That normal is the **baseline**. Our main behaviour rule compares the share of turns that ended escalated, refused or failed in the last hour with the same share a week ago. It fires when today is over twice last week's share, is over 15% in absolute terms, and there were at least 20 turns in the hour. [AAC-0114](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0114.yaml) asks for this: watch the rates that say whether the system is doing its job against a declared baseline, and alert a person before a user reports it.

A second rule watches releases. Every run carries a fingerprint of its configuration: the model it asked for, the prompt version, budgets and flags. When a fingerprint less than a day old pushes the bad-ending share to twice yesterday's, the new release is the first suspect.

## Drift: when the provider changes the model

That release rule has a blind spot. When a provider updates a model behind the same name, *your* configuration doesn't change, so nothing looks like a release.

Two things catch it anyway. First, the week-on-week rules don't care why behaviour moved. Some tend to move after a model change: unreadable model replies above 2%, the model asking for tools that aren't offered, or model calls per turn up by half on last week. Second, run the same inputs again and again, so any change in the answers is a change in the system, not in the customers. [AAC-0082](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0082.yaml) calls this watching behaviour on unchanged inputs over time. That is the canary's job.

## A test customer on a schedule

{{drawing: live-canary}}

Monitoring built on real traffic has one big weakness: a broken deployment looks like a quiet hour. If sign-in fails, no turns arrive, and every rate looks perfect.

So the reference agent has a **synthetic canary**: a test customer with orders nobody else has. Every 10 minutes it signs in through the real front door and asks four known questions, chosen to cross every part of the system and change nothing:

1. the status of a delivered order, which must be reported as delivered
2. its list of orders, which must be named
3. a return outside the window, where the reply must not claim a return was opened
4. someone else's order, where nothing about it may come back

A person is paged if a case fails twice running, or if the canary reports nothing for 25 minutes. Its turns are marked as synthetic and left out of every rate. This is [AAC-0116](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0116.yaml). The canary runs in the reference agent; on our Azure deployment it is planned, not built.

## Join what happened later

A rule reads what the agent said. Only what happens afterwards says whether it was right. [AAC-0115](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0115.yaml) asks for later signals to be attached to the run that produced them, through an id the run recorded.

The reference agent joins three today. A customer who opens a new conversation within a day of one marked complete has *returned*: the answer didn't hold. A next message asking for a person means the answer didn't satisfy. A thumbs up or down is stated outright. The first two are guesses, so they are labelled as inferred and versioned like a rule. The first version counted a customer asking four questions in one minute as four failed answers; now a new conversation within 30 minutes is a follow-up. A reversed refund belongs here too, but the test shop has no reversals, so it has no source yet.

## Every live failure becomes a golden case

{{drawing: live-loop}}

Watching only pays if it changes the next release. Our design targets about 15 minutes to detect a problem through an online rule, an hour to find the cause in the trace, and 30 minutes to recover by rolling back or flipping the kill switch, against about two days when a customer has to complain first.

Then the last step: the failure becomes a new golden case, and the offline gate runs it before every release. Turning a production turn into a case in one step is not built yet. For now, a person writes the case by hand.

## Five mistakes we see often

1. **Watching only errors.** An agent that refuses everything throws no errors. Watch how turns end, by the rule that decided.
2. **Fixed limits with no baseline.** Alert on "twice its own normal", not a number someone guessed at launch.
3. **No minimum traffic.** One bad turn at 3 a.m. becomes "100% failing" and pages someone for nothing.
4. **Counting the canary as a customer.** Its turns must be left out of the rates, or a healthy canary hides a sick agent.
5. **Alerts that never become tests.** If the same alert fires twice for the same cause, the golden set is missing a case.

## Six questions to check your own agent

1. If sign-in broke at midnight, what would tell you before the first customer complained?
2. Do you know last week's share of turns that ended handed off, refused or failed, and would you hear if it doubled today?
3. Can you see refusals by the rule that made them?
4. Does every alert say whether it needs a person now or this week?
5. When a customer comes back the next day, can you find the run that answered them the first time?
6. Is last month's worst live failure a golden case today?

Passing offline is the driving test; watching it live is checking the mirrors every few seconds, for as long as it drives.
