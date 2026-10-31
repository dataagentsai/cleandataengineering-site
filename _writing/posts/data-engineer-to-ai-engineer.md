---
title: From data engineer to AI engineer: the 6-month switch
date: 2026-10-31
subject: career
audience: builders
kind: explainer
draft: false
summary: A data engineer already knows most of what an AI engineer does, because most of an agent is ordinary software and data plumbing. What is left is six gaps, one a month: model basics, tools and the agent loop, context and retrieval, evals, guardrails, and tracing and cost. Prove it with one project, not a pile of certificates.
linkedin: You build pipelines that re-run without duplicates, block bad data and show what they cost. Congratulations, you already know half of AI engineering. Here is the other half, one month at a time, plus the one project that proves it.
deeper: /paths/ai-engineering/
deeper_label: the AI Engineering path, Crawl to Run
---

Many data engineers look at AI engineering and feel they are standing on the wrong side of a river. The job posts talk about agents, retrieval and evals. Your days are full of pipelines, tables and late-night reruns.

Here is the good news, and it is honest: the river is narrower than it looks. A working agent is a small call to a model wrapped in a lot of ordinary software. Steps that run in order, data that must be checked, a bill that must be watched. That is your job already.

This post shows what you already carry, the six gaps to close in about six months, one project that proves you closed them, and how to talk about it.

## What you already carry

{{drawing: switch-backpack}}

Look at what a data engineer does every week:

- **Pipelines and orchestration:** steps in order, on a schedule, with retries when something fails.
- **Idempotency:** a big word for a simple promise. Running the same job twice gives the same result, with no duplicate rows.
- **Data quality:** checks that stop bad data before anyone sees it.
- **Contracts:** an agreed shape for the data passed between teams, so nothing breaks silently.
- **SQL and cloud:** you can query anything and run it somewhere real.
- **Cost and testing:** you know what a job costs, and you can prove it does what it should.

Every one of these is a job inside a working agent. In our post [the model is 10%, the harness is the other 90%](/writing/model-is-ten-percent/), the harness is the plain software around the model. Read it in month 1, and you will notice how much of that 90% you have built before under other names.

## Same idea, new name

A lot of AI vocabulary is old ideas wearing new clothes.

{{drawing: switch-map}}

- **The agent loop** is orchestration. The model picks a step, your code runs it, and the result goes back in. It needs limits and retries, just like a pipeline.
- **Safe tools** are idempotency. A tool is a function the model may ask your code to run. If a network blip makes it run twice, it must not refund twice.
- **Structured output** is a contract. You ask the model for JSON (a simple text format for data) in a fixed shape, check it, and retry if it doesn't match.
- **Evals** are data quality tests for behaviour. An eval is a set of questions with known right answers that the agent must pass before each release.
- **A token meter** is your cost dashboard. A token is a piece of a word, and you pay for every one the model reads and writes.

So the switch is not learning a new world. It is learning a few new parts and reusing a lot of old habits.

## The six-month plan

{{drawing: switch-bridge}}

Lay one plank a month. Each month ends with something small that works. If you have evenings and weekends rather than full days, stretch it; the order matters more than the speed.

### Month 1: model basics and prompting

Learn what a model call really is: messages in, text out, tokens counted, a price per call. Learn temperature, which controls how random the answer is. Practise asking for structured output and validating it with code. By the end, you can say what each call cost and a broken answer is caught by code.

### Month 2: tool calling and the agent loop

Give the model three tools, such as "look up an order" or "run a saved query". Write the loop yourself in plain Python before you try a framework, so you understand what frameworks hide. Add a step limit. Make every tool check its inputs before it acts.

### Month 3: context, retrieval and RAG

The context is everything the model reads on one call. Retrieval-augmented generation, or RAG, means searching your own documents and putting the best passages into the context, so the model answers from your facts. Here your skills shine: chunking documents is a data pipeline, and keeping an index fresh is an incremental load.

### Month 4: evals

This is the plank people skip, and it is the one that makes you trustworthy. Write a golden set of questions with known answers. Check with code first, such as "did it call the right tool?" or "is the number exact?", and use another model as a judge only where code can't see. Read [before it ships: offline evals](/writing/offline-evals/) this month. If you have written data quality tests, you will feel at home.

### Month 5: guardrails and security

A guardrail is a small check that stops the agent doing something wrong. Learn prompt injection, which is when a document or message contains text that tries to give the model orders. The answer is code, not a stronger prompt: the model may only ask, and a check before each tool decides. Treat everything that comes back from a tool as data, never as instructions.

### Month 6: tracing, cost and shipping

A trace writes down every step: what the model saw, which tool ran, how long it took, and what it cost. Add a budget per question. Put the agent behind a simple app, run your evals in CI (the automatic checks that run on every change), and deploy it. Read [9 cost mistakes](/writing/agent-cost-mistakes/) this month; most of them are mistakes a cost-minded data engineer already knows how to spot.

## One project to prove it

Six months of learning needs one thing people can look at: one project that uses all six planks, not ten small demos.

{{drawing: switch-project}}

A good fit for a data engineer is **an agent that answers business questions over a lakehouse**:

1. **The lakehouse:** a few clean gold tables you build yourself from an open dataset, say sales by city and month. This is your home ground.
2. **A semantic layer:** a place where each metric, such as revenue, is defined once. The model picks a defined metric instead of writing its own SQL, so the chat and the dashboard agree. Our post on [Genie and metric views](/writing/genie-metric-views/) shows the idea on Databricks; the same idea works with open-source tools.
3. **The agent:** the loop, two or three tools, and checks on every tool call.
4. **Evals:** thirty golden questions, such as "sales in Pune last March", with the right numbers, run on every change.
5. **A cost meter:** cost per question, shown on the page.
6. **Traces:** for any answer, you can show every step that produced it.

Put it on GitHub with a README that a stranger can follow, a short video, and one page of results: what passed, what failed, what it costs per question.

## Mistakes that slow the switch

- **Starting with model training.** Most AI engineering work is building *with* models, not training them. Start by calling one.
- **Collecting certificates without a project.** A certificate says you studied. A project with evals says you can build. If you only have time for one, build.
- **Skipping evals.** Without them, every change is a guess, and you can't answer "how do you know it works?" in an interview.
- **Framework first.** Starting with a big agent framework hides the loop. Write it once by hand; then use the framework knowingly.
- **Hiding your data background.** Your pipelines, quality checks and cost work are strengths for this role. Lead with them.

## How to talk about it in interviews

Tell the story of the project, not a list of tools. A simple shape works:

1. **The problem:** "Business users get different numbers from chat and from dashboards."
2. **The design:** "The model never writes SQL. It picks from metrics defined once in a semantic layer."
3. **The proof:** "Thirty golden questions run on every change. Here is what passes, and here is the one case that still fails and why."
4. **The cost:** "Here is what one question costs, and the budget that stops a runaway."
5. **The bridge:** "This is the same discipline as my pipeline work: contracts, idempotency and tests, applied to a model."

Be honest about what you haven't done. "I have built one agent end to end and evaluated it" is a strong, true sentence.

## Five questions to check your readiness

1. Can you say what one call to a model costs, and why?
2. Can you write an agent loop by hand, with a step limit, without a framework?
3. If a tool runs twice by accident, what stops it doing harm twice?
4. Do you have a test set that blocks a release when quality drops?
5. Can you open one trace and explain every step of a wrong answer?

If you can answer all five with your own project, you have made the switch. For the topics, projects and readiness checks at each level, see the [AI Engineering path](/paths/ai-engineering/).

You already know how to build things that run reliably; now you are adding a model to the list.
