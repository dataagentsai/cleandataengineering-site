---
title: Should you build or buy your agent? A one-page guide for leaders
date: 2026-10-31
subject: ai
audience: leaders
kind: leader-brief
draft: false
summary: Build or buy is rarely an either-or choice for an agent. Six questions decide it: how special the process is, where the data may go, what each task costs to run, what you can switch later, who owns it after launch, and what you must prove to auditors. Most teams end up in the middle: buy the plumbing, and build the rules that protect money and make you different.
linkedin: Every leader is being asked the same question this year: should we build our own AI agent or buy one? The honest answer is usually "both, in the right places". Six questions, one decision card, and five things to ask your team on Monday.
deeper: /learn/agent-harness/
deeper_label: the Agent Harness tutorial, for the engineers who will build it
cross: /writing/model-is-ten-percent/
cross_label: The model is 10%. The harness is the other 90%.
---

A vendor shows you an agent that answers customer emails. It is polished, it is ready next month, and the price is one line on a quote. Meanwhile your own team says they could build something better that fits your process exactly. Both sound reasonable, and both can go badly wrong.

An **agent** here means software that uses an AI model to take steps on its own: read a request, look things up, and act, such as raising a ticket or approving a refund. Because it acts, the decision is bigger than choosing a chatbot.

This page gives you the six questions that decide build or buy, and the middle path most teams end up on.

## Three roads, not two

{{drawing: buy-crossroads}}

**Buy** means a finished product that does the whole job. **Build** means your engineers write it, end to end. The third road is the one we see work most often: **buy the plumbing, build the rules**. The plumbing is the common machinery every agent needs. The rules are the parts that are yours alone.

## The six questions

{{drawing: buy-decision-card}}

### 1. How special is your process?

Some jobs are the same in every company: answering common support questions, writing up meeting notes, sorting invoices. A vendor has seen thousands of these, and you gain little by building your own. Buy.

Other jobs are the reason customers choose you: how you price a claim, how you judge a supplier, how you decide who gets a refund. If you buy that, your edge now lives in someone else's product, and your competitors can buy the same thing. Build the parts that carry the edge.

### 2. Who owns the data, and where may it go?

An agent reads your data to do its job. Ask where that data travels: to which country, which company, and whether it is kept or used for training. Customer records, health data and payment details often come with rules about where they may sit. If a product cannot keep the data where it must stay, it is out, however good the demo.

### 3. What will it cost per task?

The licence is the number on the quote. The bigger number is often what it costs to *run*: each time the agent handles one request, it pays for the AI model it calls, and sometimes for many calls. A badly built agent can cost dollars per question, while a well built one can cost a fraction of a cent. Ask for the cost per finished task, and ask how it is measured.

### 4. What can you switch later?

AI models get better and cheaper several times a year. If the product ties you to one model, you cannot take the better or cheaper one when it arrives. The same goes for your workflows and your data. Ask: can we change the model? Can we export our rules, our history and our test cases in a form we can use elsewhere?

### 5. Who will own it after launch?

An agent is not finished on launch day. Someone has to keep checking that it still gives the right answers (engineers call these checks **evals**), keep its safety limits (**guardrails**) up to date, and answer the phone when it misbehaves at 2 a.m. If you build, that is your team, for years. If you buy, find out exactly which of these the vendor does and which still land on you.

### 6. What must you prove to auditors and regulators?

If a regulator asks why the agent approved a ₹40,000 refund, can you show every step it took, what it read, and which rule allowed it? Some products show you that. Many show only the final answer. In a regulated business, "the vendor says it is safe" is not evidence.

## Where the money goes in a year

{{drawing: buy-year-money}}

The numbers in this picture are an example, not a benchmark. Say a product licence costs ₹10 lakh a year. The agent handles 20,000 requests a month at ₹2 each to run, which is about ₹4.8 lakh a year. And a quarter of an engineer's time goes on checks, fixes and being on call, which is about ₹8 lakh.

The quote showed ₹10 lakh. The year cost about ₹23 lakh. Your numbers will differ, but the shape is common: the licence is only one of three piles, and the other two exist whether you build or buy.

## The middle path: buy the plumbing, build the rules

{{drawing: buy-middle-path}}

Most of an agent is ordinary machinery: the AI model itself, a **gateway** that routes every model call through one place, **tracing** that writes down each step the agent takes, and the platform it runs on. These are common to every agent and improve fast. Buy them, or use good open-source versions. Building your own is effort spent on a part that gives you no edge.

A small part of the agent is yours alone, and it is where money and reputation are at stake:

- **Business rules:** who may get a refund, and up to what limit.
- **Checks:** small, plain rules that stop the agent before it does something wrong, such as paying out money nobody asked for.
- **Evals on your own cases:** a test set of your real requests, in your language, with your edge cases, run before every change.

Keep these in your own hands. They are what you will be asked to explain to an auditor, and what you would lose if you swapped vendors. Your engineers can read more in [why your agent costs $4 per question](/writing/agent-cost-mistakes/).

## What goes wrong

1. **Buying the whole thing for your core process.** It works, but now your edge is a setting in someone else's product.
2. **Building the plumbing.** Months go on a home-made gateway or tracing tool instead of the rules that matter.
3. **Comparing licence to salaries.** Running cost and the people needed after launch belong in both columns.
4. **No exit plan.** Nobody asked how to take the rules, history and test cases out, until the renewal price arrived.
5. **No owner after launch.** The agent was a project, and the project ended. Its answers slowly got worse, and nobody was checking.

## Five questions to ask your team on Monday

1. Which part of this process is common to every company, and which part makes us different?
2. Where will our data travel, and is that allowed?
3. What does one finished task cost to run, and how do we know?
4. If a better or cheaper AI model arrives next quarter, how long would it take us to switch?
5. Who owns this agent's evals, guardrails and on-call after launch, by name?

Buy what everyone has, build what only you have, and make sure someone owns it after launch.
