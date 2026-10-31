---
title: There is no best model, only the best model for this step
date: 2026-10-31
subject: llm
audience: builders
kind: decision
draft: false
summary: Picking one "best" model for a whole agent is the wrong question. Test candidates on a small golden set of your own tasks, weigh accuracy, cost, speed and reliability for each step, decide where your data is allowed to go, and give each step the cheapest worker that passes, which is often plain code. Then pin the versions and test again whenever a model changes.
linkedin: Which model should our agent use? Wrong question. An agent turn has four or five steps, and each one has a different best answer, sometimes "no model at all". Here is how we choose, with a scorecard you can fill in this week.
deeper: /learn/agent-harness/tech-l2.html
deeper_label: Model invocation, in the Agent Harness tutorial
---

Every agent project has the meeting. Someone opens a leaderboard, someone else has read that a new model came out last week, and the room spends an hour on one question: which model should we use?

It is the wrong question. An agent doesn't make one kind of decision. In a single turn it sorts the message, pulls out a few facts, thinks hard about one thing, and writes a reply. Those are different jobs, and each one has its own best worker.

This post is how we pick models for a vertical agent, meaning an agent built for one domain, such as insurance claims. Our example is the claims agent in the [Agent Harness tutorial](/learn/agent-harness/), which runs an open-weight model on Groq behind an Azure gateway.

## A toolbox, not a trophy

Nobody asks which tool in a toolbox is the best. A hammer is best for nails and hopeless for a watch strap. The question is always which tool fits this job.

{{drawing: mdl-toolbox}}

Models are the same. A strong model is the hammer: worth it for the one step that needs real reasoning. A small fast model is the screwdriver: good at sorting messages and pulling out a claim number. And plain code is the tweezers: exact, instant and free, for anything a rule can decide.

## Test on your own tasks, not the leaderboard

A public leaderboard tells you how a model did on someone else's questions. Your agent will face your questions, in your language, with your rules.

So the first thing to build is a **golden set**: a list of real tasks from your domain, each with a known right answer. Start small. Our reference agent's golden set has 35 cases for one job, deciding whether an action is allowed. Each case tests an edge of a rule, so a 30-day rule gets cases at 29, 30 and 31 days. The set lives in Git and is never edited to make a failing case pass.

Here is why it matters. When we tested a popular open-source tool for spotting personal data, its defaults missed the name "Priya Sharma", called a claim number a US driver's licence, and read an Indian phone number as a date. It wasn't a bad tool. It was trained for someone else's data. A leaderboard would never have shown us that. A handful of our own cases did.

How to build the set and run it before every release is in [offline evals](/writing/offline-evals/).

## Weigh four things, per step

Once you can score a model on your own cases, four things decide the choice.

{{drawing: mdl-dials}}

1. **Accuracy.** Does it pass your golden cases for this step? Not in general, for this step.
2. **Cost.** Count cost per task, not price per token. A cheap model that needs three tries costs more than a dearer one that gets it right once. Our model, `gpt-oss-120b` on Groq, is priced at $0.15 per million tokens in and $0.75 per million out. The smaller `gpt-oss-20b` is $0.10 and $0.50.
3. **Speed.** Measure the time the user waits, not the model alone. In one of our real turns, Groq answered in 0.6 and 1.0 seconds, but the turn took 7.1 seconds. Most of the wait was a gateway waking up and a content-safety check.
4. **Reliability.** Does it return valid output every time, and will the provider let you call it? Groq's free tier allows 8,000 tokens a minute. One loop turn uses 1,500 to 2,500, so in practice that is only 3 to 5 turns a minute. Rate limits are part of the model choice.

These dials pull against each other. The point is to set them for each step, not once for the whole agent.

## Open-weight or closed: where may the data go?

An **open-weight** model is one whose trained weights are published, so anyone can run it: you, on your own servers, or a hosting provider. A **closed** model can only be reached through its maker's service or a cloud that resells it.

That gives you three questions to answer before you compare scores:

- **Where is the data allowed to go?** Every prompt carries the user's words and whatever the tools returned. For a claims agent that means names, policy numbers and medical details. If a rule says that data must stay in India, or inside your own cloud account, that rule picks the shortlist for you.
- **Host it yourself, or use a provider?** Running an open-weight model yourself keeps the data at home, but you now own the GPUs, the scaling and the 2 a.m. outages. A provider is far less work, and the data leaves your walls.
- **Which region?** Data residency means the data is stored and processed in a named place. Our Azure design places the gateway in Central India with the region pinned, and the tutorial notes that model availability still has to be checked region by region.

Our choice shows the trade. We use `gpt-oss-120b`, an open-weight model, hosted by Groq: it has a free tier and an API in the common OpenAI style, so lock-in is low. Every call goes through Azure API Management, a gateway that lets through only that one model and checks every prompt and answer. The planned move is to Azure's own model catalogue, with GPT, Claude and small models, still behind the same gateway. Because the agent only ever talks to the gateway, that swap is configuration, not a rewrite.

## A model per step

Here is one turn of the claims agent, with the right worker at each step.

{{drawing: mdl-turn}}

1. **Route the message.** Rules first. A message naming a known claim number never reaches a model at all: it is answered from a template in 104 milliseconds for $0, against about 7 seconds for the same question through the model. Where rules are unsure, the plan is a small local classifier, then a small model only if that is unsure too.
2. **Pull out the facts.** Extraction, meaning turning "my car was hit on Tuesday" into a date and a claim type, is a small-model job.
3. **Decide.** Reading the policy and weighing the case is the one step that earns a strong model.
4. **Check and reply.** Limits, grounding and the reply template are plain code.

The tutorial plans a small job to do this choosing for you: run every candidate on the golden set before each release and pick the cheapest model that passes, per job. It is designed but not yet built, and the scorecard below is the hand-made version. We also rejected a model router that picks a model at run time, for one reason: the same input might not get the same model twice, so a result can't be reproduced.

The money side of this, and what happens when every step uses the biggest model, is in [9 cost mistakes](/writing/agent-cost-mistakes/).

## Re-test on every model change

A model name is not a version. Providers update models, retire them and change their defaults. Your golden set passed last month on last month's model.

So **pin the version**: write the exact model name and version in configuration, not "latest". Our gateway goes further and refuses any model not on its list, with an error that says so. Then treat a model change like a code change. It goes through the golden set, and it ships only if no slice gets worse. We call the request at temperature 0 for the same reason, so the same input gives an answer as close to the same as possible, which makes a before-and-after comparison fair.

## The scorecard

Here is the whole method on one card.

{{drawing: mdl-scorecard}}

1. Write your agent's steps down the side.
2. Put two or three candidate models across the top, plus a column for plain code.
3. For each cell, run the golden cases for that step and mark pass or fail.
4. Add cost per task and time per task, measured, not taken from a price page.
5. In each row, circle the cheapest column that passes.

The ticks in the drawing are an example. Yours will differ, and that is the point.

## Mistakes we see often

1. **Choosing by leaderboard.** A high public score says nothing about Indian names, your policy wording or your edge cases.
2. **The biggest model everywhere.** Routing a "where is my claim?" message through the strongest model is paying a surgeon to take your temperature.
3. **Never re-testing.** The provider updated the model, nobody re-ran the golden set, and a slice that worked quietly broke.
4. **Forgetting where the data goes.** The model was chosen on scores, and only later did someone ask which country the prompts were processed in.
5. **No rate-limit plan.** The model passed every test, then the first busy hour hit the provider's limit.

## Six questions to check your own choice

1. Do you have at least a few dozen golden cases from your own domain, and does every candidate run against them?
2. For each step, could plain code do it instead?
3. Do you know the cost per task, measured, for each step?
4. Do you know which country and which company processes every prompt?
5. Is every model version pinned in configuration, and does a change go through the golden set?
6. What happens when the provider says no: a rate limit, an outage, a retired model?

The best model is the cheapest worker that passes your own test, one step at a time.
