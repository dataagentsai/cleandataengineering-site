---
title: What one conversation costs: under a tenth of a cent
date: 2026-10-31
subject: cost
audience: leaders
kind: leader-brief
draft: false
summary: A real conversation with our test claims assistant cost $0.00087 in model fees, and every turn we measured cost between nothing and $0.00093. It is that low because of four design choices, not luck. The model bill is the smallest line in your AI budget; people, review, upkeep and the platform are the real costs, so ask your team for the cost of each completed task.
linkedin: One real conversation with our test claims assistant cost $0.00087 in model fees. A thousand of them would cost 87 US cents. The model bill is almost never the problem; here is why it stays low, what makes it explode elsewhere, and what you should actually budget for.
deeper: /learn/agent-harness/cost.html
deeper_label: Cost, where the money goes, in the Agent Harness tutorial
cross: /writing/agent-cost-mistakes/
cross_label: the engineering version
---

A customer named Rohan asks our test claims assistant what the assessor wrote on his glass claim. Hidden in that claim's notes is a planted instruction telling the assistant to pay out the claim at once. The assistant reads the claim, is briefly fooled into asking for the payout, gets refused by a safety rule, and then answers Rohan's real question.

That whole conversation cost **$0.00087** in model fees. A thousand conversations like it would cost 87 US cents. At an assumed rate of ₹85 to the dollar, that is about 7 paise each.

This brief explains why the number is that small, what makes AI bills explode elsewhere, and what you should actually budget for. The assistant is a test system built for a public tutorial, not a live service, but its numbers are measured by the assistant itself, not guessed.

## A cent, cut into ten

{{drawing: conv-coin}}

Each time a customer sends a message and the assistant replies, that is one **turn**. Across fourteen real test flows, a turn cost between $0 and $0.00093. The dearest turn still fits inside one tenth of a US cent.

The cost comes from **tokens**, the small pieces of text a model is billed by, roughly three quarters of a word each. The assistant pays for every token it reads and every token it writes.

## Where the money in one conversation goes

{{drawing: conv-bar}}

Rohan's conversation took three trips to the model. The first read his claim. The second was the fooled attempt at a payout, which was blocked. The third wrote the answer.

Each trip costs more than the last, because the model rereads everything so far before adding a little more. That growth is small here, but it is the same mechanism that turns a cheap assistant into an expensive one when nobody limits it.

## Why it is that low

Four ordinary design choices keep the bill small.

1. **An open-weight model on a low-cost provider.** An open-weight model is one whose internals are published, so many companies can host it and compete on price. Ours, gpt-oss-120b on Groq, is priced at about $0.15 per million tokens read and $0.75 per million written.
2. **Answering without the model when possible.** A plain question such as "what is the status of my claim?" is answered by ordinary code that looks up the record. It costs $0 and replies in about a tenth of a second instead of seven seconds. Refused and blocked requests also never reach the model.
3. **Trimmed context.** **Context** is everything the model is shown before it answers. Ours has a fixed size limit, so old parts of the conversation are dropped instead of being resent on every trip.
4. **Budgets per task.** Every turn has hard limits: at most 12 trips, 60 seconds and $0.50. Twelve trips cost about $0.05 at today's prices, so the $0.50 ceiling has never been reached. It exists to stop a runaway, not to manage normal spend.

## What makes costs explode elsewhere

When teams report a few dollars per question, the model's price is rarely to blame. Usually the assistant resends its whole history on every step, loops with no limit, retries failures over and over, or uses a large expensive model for a small job. Each of these multiplies the bill, and together they can turn a fraction of a cent into dollars. Your engineers will find the detail in the engineering version linked at the end.

## What to actually budget for

{{drawing: conv-budget}}

Here is the uncomfortable part. Even our tiny test system's monthly running bill is mostly not the model: a database costs about $22 a month if left running, while the model tokens sit inside a provider's free allowance.

At real scale the pattern holds. The tutorial works through a deployment handling 2,000 conversations a day. It estimates model spend at $28.75 a day, or $10.67 with a smarter design, while one person spending a fifth of their time on it cost $54.79 a day. People were the biggest line either way.

So budget for the things that do not appear on the model invoice:

- **People** who own the assistant and handle what it passes on.
- **Review** of its work, often heavier in the first months than planned.
- **Upkeep** of its tests and safety rules as your products and policies change.
- **Platform**: hosting, databases, monitoring and the gateway that controls access to the model.

[Measuring agent ROI](/writing/agent-roi/) shows how to weigh all of these against the value the assistant brings.

## Ask for cost per completed task

The most useful number is the **cost per completed task**: a claim registered, a question answered so the customer did not come back. It divides everything above, people included, by the work that actually finished.

Ask your team for it directly. A good team can tell you the model cost of any single conversation, because the cost is recorded as it happens; ours writes it on every turn's record. If they can only show you a monthly invoice, they cannot yet tell you which conversations are expensive or why.

## What goes wrong

1. **Budgeting only for the model.** It is the smallest line, so the plan looks cheap and the rollout does not.
2. **No limits per task.** One stuck conversation can loop for minutes, paying on every trip.
3. **Judging by the invoice alone.** By the time the invoice arrives, the expensive pattern has run for a month.

## Four questions to ask about your AI bill

1. What does one completed task cost, with people, review, upkeep and platform included?
2. What share of requests are answered without calling the model at all?
3. What is the most a single conversation is allowed to spend, and what happens when it hits that limit?
4. Can you show me the cost of one specific conversation from yesterday?

The model is the cheap part; spend your attention on everything around it.
