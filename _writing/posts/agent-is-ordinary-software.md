---
title: Most of an agent is ordinary software
date: 2026-10-31
subject: ai
audience: builders
kind: build-log
draft: false
summary: We counted every line of code in our reference agent and sorted it by job. The code that calls the model is 817 of 24,631 lines, about 3%, and the rest is tests, checks, durable workflows, state, tracing and plumbing. So most of building an agent is ordinary engineering, and the skills you already have apply.
linkedin: People say the model is 10% of an agent. It is a nice slogan. So we measured it. In our open reference agent, the code that calls the model is 3% of the lines. Tests alone are 18,415 lines. Here is the count, the method, and how to check your own.
deeper: /learn/agent-harness/
deeper_label: the Agent Harness tutorial, which walks the same agent layer by layer
---

We once drew a picture that said [the model is 10% of an agent](/writing/model-is-ten-percent/) and the harness is the rest. We said at the time that the number was a picture, not a measurement. People kept asking what the real number was.

So we counted. We took our open [reference agent](https://github.com/dataagentsai/reference-agent), a customer-support agent for a clothing web shop, and sorted every line of its Python by the job that line does.

The answer is not 10%. It is about 3%. The slogan was generous to the model.

## The iceberg, with real numbers

In a demo you see the model. It reads a message, picks a tool, writes a reply. That part is the tip. Everything that keeps it honest, safe and running sits under the water.

{{drawing: loc-iceberg}}

The reference agent has 24,631 lines of code, not counting tests. The code that calls a model is 817 of them. The other 23,814 lines are the loop, the checks, the waiting-for-a-person workflows, the database, the traces, the evals and the plumbing that joins them. Then there are 18,415 more lines of tests on top.

## How we counted

The method is deliberately boring, so anyone can repeat it.

1. **Which files.** Every `.py` file committed at one point in the repository's history, commit `d0a8b84`. That covers the agent itself, its harness package (`packages/agent-harness`), its evals, scripts and tests. Because we read from the commit, `.venv`, `node_modules`, scratch copies and uncommitted work can't sneak in. The repository holds no vendored code, meaning no copied-in third-party libraries.
2. **Which lines.** A line counts if it holds code. Blank lines, comment lines and docstrings (the explanation strings at the top of a Python function or file) are dropped. We used Python's own `tokenize` and `ast` modules to find them, rather than guessing with a pattern.
3. **Which job.** Each file goes to exactly one job, by a list of folder and file rules. The first rule that fits wins. For example, the `llm` folder and the model adapter go to "the code that calls a model". The approval and escalation workflows go to "durable workflows". Tests are counted on their own.

The counting script takes the repository and the commit as its two inputs, and prints the table below.

## The numbers

| Job | Files | Code lines | Share of agent code | Share of everything |
|---|---|---|---|---|
| The code that calls a model | 8 | 817 | 3.3% | 1.9% |
| The loop | 20 | 1,572 | 6.4% | 3.7% |
| Context building | 2 | 144 | 0.6% | 0.3% |
| Checks, policies and sign-in | 31 | 2,509 | 10.2% | 5.8% |
| Tools and tool adapters | 8 | 815 | 3.3% | 1.9% |
| State and persistence | 24 | 1,471 | 6.0% | 3.4% |
| Durable workflows and retries | 35 | 2,667 | 10.8% | 6.2% |
| Tracing, telemetry and cost | 24 | 1,677 | 6.8% | 3.9% |
| Evals | 53 | 5,379 | 21.8% | 12.5% |
| Config and wiring | 10 | 944 | 3.8% | 2.2% |
| Everything else | 52 | 6,636 | 26.9% | 15.4% |
| Tests | 110 | 18,415 | not counted | 42.8% |

"Share of agent code" leaves tests out, so it adds up to 24,631 lines. "Share of everything" puts them back, for a total of 43,046.

Here are the same numbers as bars.

{{drawing: loc-bars}}

Four things stand out.

- **The model call is small, and it isn't even simple.** Those 817 lines already speak to more than one provider, and read what a gateway in front of the model says about each call. The part that sends a request is a small piece of it. The rest is making every call, to any provider, go through one place.
- **Tests are the biggest single job.** 18,415 lines, more than any job in the agent itself. Add the 5,379 lines of evals, and checking the agent is more than half of all the code.
- **"Everything else" is big, and it's honest.** Inside it: 3,360 lines of report pages and scripts, 1,662 lines of the edge (the web server, the chat webhook, the customer's login and the reviewer's page), 925 lines of a stand-in shop that the tools talk to, and 689 lines of shared types. None of it is clever. All of it has to work.
- **Context building is tiny.** 144 lines. Deciding what the model sees is a hard *design* problem, but the code that does it is short. Lines measure what you maintain, not what you have to think hard about.

## What those lines ask of you

Look at the biggest rows again and ask what you need to know to write them. Mostly it isn't prompting.

{{drawing: loc-skills}}

- **Tests.** Fake tool servers, fixtures, and recorded model replies played back so a test gives the same answer every time.
- **Retries and idempotency.** Idempotency means doing something twice has the same effect as doing it once. A refund request that times out gets retried, and the shop must not pay the customer twice.
- **Auth.** The agent acts only with the customer's own session. The tool server checks that token on every call, and never trusts a customer id the model wrote.
- **Schemas.** Typed inputs and outputs at every seam, so a bad value fails loudly at the boundary instead of quietly three steps later.
- **SQL and Postgres.** Conversations, an idempotency ledger and queues of approvals waiting for a person all live in the database, and survive a restart.
- **Tracing.** Every step written down with its cost, so you can replay a bad conversation and see where it turned.

A good backend or data engineer has most of these skills already. Take a data engineer who has built a pipeline that retries without loading a file twice. That person already knows the core idea behind an agent's durable workflows. The new part, talking to the model well, is real, but it's the small part.

## What goes wrong when you measure

A line count is easy to get wrong, and easy to over-read.

- **Counting other people's code.** Leave out `.venv`, `node_modules`, vendored libraries and generated files, or a framework's thousands of lines will drown your own.
- **Mixing tests in.** With tests in, our model share falls from 3.3% to 1.9%. Both are true. Say which one you mean.
- **Treating the grouping as fact.** Sorting files into jobs is judgement. Move a few files between rows and the numbers shift by a few hundred lines. The shape doesn't change. We also tried keeping docstrings in, and the model's share stayed about the same, at 3.4%.
- **Reading lines as importance.** One wrong line in the model call can break every reply. Lines tell you where the maintenance goes, not where the risk is.
- **Generalising from one agent.** This one was built to teach, so it is heavy on tests and evals. A weekend demo would show a much bigger model share, because it has almost nothing under the water. That is the point, not a counter-example.

## How to check your own agent's split

{{drawing: loc-check-own}}

You don't need our script. A rough first pass is one line in the repository's folder. It keeps docstrings in, which barely moved our answer:

```
git ls-files '*.py' | xargs grep -cvE '^\s*(#|$)'
```

That prints a count per file. Paste it into a spreadsheet, add a column for the job, and write down the rule you used for each folder. Tag a file by what it mostly does. If a file does three jobs, that is a finding too.

## Five questions to check your own split

1. Can you point to the one place where every model call goes through, and say how many lines it is?
2. Is your test code bigger or smaller than your agent code? If much smaller, what isn't tested?
3. Which job is your biggest row, and did you plan for it to be?
4. How many lines make sure the same action never runs twice?
5. If you swapped models tomorrow, how many files would change?

Measure your own agent before you believe anyone's slogan, ours included.
