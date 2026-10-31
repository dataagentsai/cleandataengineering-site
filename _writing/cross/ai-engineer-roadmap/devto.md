---
title: The AI engineer roadmap: what to learn, in what order, and what to skip
published: false
canonical_url: https://cleandataengineering.ai/writing/ai-engineer-roadmap/
description: AI engineering is a lot to take in, but the order makes it manageable. Learn it in six phases: foundations, building with models, context and knowledge, reliability, running it, and an optional deeper phase on the models themselves. Skip model training, framework-hopping and project-free certificates early on, and finish each phase with one small project.
---

*Originally published at [cleandataengineering.ai](https://cleandataengineering.ai/writing/ai-engineer-roadmap/).*


Open any feed and AI engineering looks like a hundred things to learn by Friday. New models, new frameworks, new words. It is easy to read about all of it and build none of it.

The honest truth is kinder than the feed. An AI engineer builds products where a model does part of the work, and most of that product is ordinary software around the model call. If you already write code or move data for a living, you are closer than you think.

This post is the map: six phases in order, three things to skip for now, and one project per phase. If you are a data engineer who wants a month-by-month plan, read [from data engineer to AI engineer: the 6-month switch](/writing/data-engineer-to-ai-engineer/). This is the wider map behind it.

## The map in one picture

{{drawing: road-map}}

Think of it as a road with six towns. Drive at your own speed, but keep the order: each town uses what you learned in the one before. The last town is a side trip, and plenty of good AI engineers never go there. The detour sign marks things that look important early but slow you down.

## The six phases

{{drawing: road-stairs}}

Each phase ends with a sentence you can truthfully say about yourself. That sentence matters more than the hours spent.

### Phase 1: foundations

**What to learn:** Python well enough to write and test small programs. APIs, which are how one program asks another for something over the web, usually sending and receiving JSON (a simple text format for data). SQL, because most useful answers live in a database. Git, so your work has history and others can review it. And cloud basics: how to run a small app somewhere that is not your laptop.

**You can say:** "I can build a small service, test it, put it in Git and run it in the cloud."

Software engineers move through this town quickly; data engineers often need a little more on APIs and testing. Don't skip it either way.

### Phase 2: building with models

**What to learn:** what a model call really is: messages go in, text comes out, and you pay for tokens (pieces of words) both ways. Prompting: clear instructions and examples. Structured output: asking for JSON in a fixed shape and checking it in code. Tool calling: the model asks your code to run a function, such as "look up this order", and your code decides whether to allow it. And the agent loop: the model picks a step, your code runs it, the result goes back, until the job is done or a step limit stops it.

**You can say:** "I can write an agent loop by hand, and a bad tool call is refused by code, not by hope."

Write the loop once in plain Python before you pick up a framework, so you know what the framework does for you.

### Phase 3: context and knowledge

**What to learn:** the context is everything the model reads on one call. Retrieval means finding the right passages from your own documents. RAG, short for retrieval-augmented generation, means putting those passages into the context so the model answers from your facts instead of its memory. Context engineering is the wider skill of choosing what goes into that window and what stays out.

**You can say:** "My assistant answers from our documents, shows where each answer came from, and I can measure how often it finds the right passage."

### Phase 4: making it reliable

**What to learn:** evals, which are a set of questions with known right answers that your system must pass before each release. Guardrails, which are small checks before and after the model and its tools that stop it doing something wrong. Tracing, which records every step of a run so you can replay a bad answer. And ordinary testing of the code around the model.

**You can say:** "A release is blocked when quality drops, and I can open one trace and explain a wrong answer."

This is the phase people most want to skip, and the one that makes you trustworthy. Anyone can build a demo; proving it works is the job.

### Phase 5: running it

**What to learn:** cost, meaning what one question costs and the budget that stops a runaway loop. Shipping: prompts, models and tools versioned and deployed together. Security, especially prompt injection, where text inside a document or email tries to give the model orders. And human in the loop: deciding which actions wait for a person to approve, such as a refund above ₹40,000.

**You can say:** "Real people use it, I know what it costs per question, and risky actions wait for a person."

### Phase 6: going deeper (optional)

**What to learn:** fine-tuning, which means training an existing model a little more on your own examples. Serving models yourself, which means hosting open models and making them fast and cheap. And building a tiny language model on your laptop, just to see how the insides work.

**You can say:** "I know when tuning beats prompting, and I can explain how a model predicts the next word."

This phase is for curiosity, or for moving toward shaping models rather than using them. Come here when phases 1 to 5 feel solid.

## Start here, phase by phase

If you want one thing to read per phase, start with these.

| Phase | Start here |
|---|---|
| 1. Foundations | [The model is 10%, the harness is the other 90%](/writing/model-is-ten-percent/) |
| 2. Building with models | [Choosing your agent loop](/writing/choosing-agent-loop/) |
| 3. Context and knowledge | [Context engineering](/writing/context-engineering/) |
| 4. Making it reliable | [Before it ships: offline evals](/writing/offline-evals/) |
| 5. Running it | [9 cost mistakes](/writing/agent-cost-mistakes/) |
| 6. Going deeper | [Prompt, RAG or fine-tune? Pick in that order](/writing/prompt-rag-finetune/) |

## What to skip for now

{{drawing: road-skip}}

1. **Training models from scratch.** Big models are trained by a few labs with enormous budgets. AI engineering is mostly building *with* models. A tiny model in phase 6 is a great lesson; a real one from scratch is a different job.
2. **Chasing every new framework.** A new framework appears almost every week. Learn the jobs instead of the names. Our [AI Universe](/learn/ai-universe/) sorts every name you will hear into seven families, so a new product becomes "another way of doing a job I already know".
3. **Certificates without projects.** A certificate says you studied; a project with evals says you can build. If you only have time for one, build.

## One project per phase

{{drawing: road-projects}}

Reading gets you to the edge of each town; a project gets you through it. Keep each one to a few weekends.

1. **Foundations: a tiny data service.** Pull daily exchange rates from a public API, store them in a SQL table, add tests, and run it in the cloud behind a small web endpoint.
2. **Building with models: an expense helper.** Paste in a receipt, get back checked JSON (vendor, date, amount in ₹), and give the model two tools: "look up the policy limit" and "file the claim". Write the loop yourself, with a step limit.
3. **Context and knowledge: ask the handbook.** An assistant over a set of policy documents that answers with citations. Keep twenty test questions and count how often it finds the right passage.
4. **Making it reliable: prove the handbook bot.** Add thirty golden questions that run on every change, two or three guardrails, and a trace for every run.
5. **Running it: put it in front of people.** Let a few friends or teammates use it. Show cost per question, set a budget, add one action that waits for approval, and try to break it with a planted instruction in a document.
6. **Going deeper: a tiny model.** Train a very small model on a public-domain book on your laptop, or fine-tune a small open model and compare it with plain prompting on your phase 4 eval set.

Projects 3, 4 and 5 are the same assistant growing up, on purpose. One project you can explain end to end beats six demos you can't.

## Mistakes that slow people down

- **Starting in the middle.** Jumping to agents without phase 1 means every bug feels like a model problem when it is really a code problem.
- **Reading without building.** Ten articles on RAG teach less than one evening of watching your own retrieval miss.
- **Staying in phase 2 forever.** Prompting is fun, so people polish prompts for months. Move on once your loop works.
- **Going alone.** Share each project, even a rough one. Feedback from one reviewer beats a month of guessing.

## Five questions to check your own progress

1. Can you build, test and deploy a small service without following a tutorial step by step?
2. Can you write an agent loop by hand, with a step limit, and explain each line?
3. Does your assistant show where its answers come from, and do you know how often it finds the right passage?
4. Would your current project block a release if quality dropped?
5. Do you know what one question costs, and which actions wait for a person?

Each "yes" is a town behind you. For topics, projects and readiness checks at each level, see the [AI Engineering path](/paths/ai-engineering/).

Pick the town you are in today, finish its one project, and drive on.

