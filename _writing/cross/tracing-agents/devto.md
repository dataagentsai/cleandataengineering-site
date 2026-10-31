---
title: If you can't replay it, you can't fix it: tracing autonomous agents
published: false
canonical_url: https://cleandataengineering.ai/writing/tracing-agents/
description: When an agent gives a bad answer, the final reply tells you almost nothing. You need a trace: one per turn, with a span for every model call, tool call and check, carrying the model, a prompt version, tokens, cost, time and the decision, but not the customer's personal data. With that, yesterday's bad conversation becomes something you can step through and turn into a test.
---

*Originally published at [cleandataengineering.ai](https://cleandataengineering.ai/writing/tracing-agents/).*


A policyholder rings the call centre. *"Your assistant told me my payout was on its way. Where is it?"* Somebody opens the logs. They find the reply, word for word, and nothing else.

Was it the model? A tool that returned old data? A check that should have fired and didn't? A new prompt that went out on Tuesday? Nobody can say. So the team guesses, changes the prompt, and hopes.

An agent doesn't produce one answer. It takes several steps: it asks the model, calls tools, gets checked, and asks the model again. If you only keep the last step, you can't fix the first one. This post is about keeping all of them, in a way you can replay.

## No trace, no clues

{{drawing: trace-detective}}

A **trace** is the written record of one piece of work, broken into timed pieces called **spans**. Each span says what happened, when it started, how long it took, and a few facts about it. Spans sit inside each other, so the record reads like a tree.

The example here is the claims assistant from our [Agent Harness tutorial](/learn/agent-harness/): a motor insurer's chat assistant on Azure, where a signed-in policyholder like Rohan can ask about his claims, report a new one or ask for an approved claim to be paid.

## One trace per turn

A **turn** is one message from Rohan and everything the agent does before it replies. Make each turn one trace. That is the unit people complain about, and the unit you will want to replay.

{{drawing: trace-tree}}

This is a real turn, the one from [flow 13 of the tutorial](/learn/agent-harness/flow-13.html), where we planted a note in claim CLM-019900 telling the assistant to pay out. Read it top to bottom:

1. `agent.turn` is the whole turn. It carries who asked, which conversation, and how the turn ended.
2. `agent.run` is the loop inside it. It carries the total cost and why the loop stopped.
3. Each `gen_ai.chat` is one model call. There were three.
4. `agent.tool` is one tool call, here `get_claim`.
5. `agent.policy` is one check. This one sat before a tool, saw that Rohan never asked for a payout, and blocked `request_payout`.

Without the tree, all you know is that the reply was fine. With it, you can see the model *was* fooled at step 2, and the check is why nothing was paid. That is a different story, with a different fix.

Every span in a turn shares one trace id, and the conversation id rides along on every span too. On Azure that means one query in Application Insights pulls up the whole turn in order.

## What one span should hold

The fields are where most tracing goes wrong. Too few and you can't explain anything. Too many and you're storing personal data in a system that wasn't built for it.

{{drawing: trace-span-card}}

For a **model call**, keep:

- **The model you asked for, and the model that answered.** They can differ: a provider may serve a specific build behind a general name.
- **A prompt version.** Our harness records a *config fingerprint*: a short code that changes whenever the prompt, the model or the settings change. If quality drops on Wednesday, you can see that every bad turn carries the fingerprint that went live on Tuesday.
- **Tokens in and tokens out**, and the **cost** of the call in money.
- **How long it took.** The span's own start and end give you this for free.

For a **tool call**, keep the tool's name, whether it changes anything in the world, the **outcome** (ok, refused, error or replayed), and how big the result was, including whether it was cut down before reaching the model. Our harness cuts tool results at 8,000 characters, and the span says when it did.

For a **check**, keep where it sits, **which rule fired**, and whether the check itself failed or timed out. A check that errors quietly looks exactly like a check that passed, unless the span says so.

On the turn itself, keep **the decision**: did it complete, refuse, hand over to a person, or wait for approval? And if a rule caused that, which rule?

## OpenTelemetry, in plain words

You don't need to invent a format for any of this. **OpenTelemetry** is an open standard, run by the Cloud Native Computing Foundation, for writing traces, metrics and logs. Your code writes spans through its library. A small piece called an **exporter** sends them wherever you like: Application Insights, Grafana, Langfuse, Datadog or a file on disk. To change where traces go, you change the exporter, not your code.

OpenTelemetry also publishes **semantic conventions**: agreed names for common fields, so every tool knows where to look. The **GenAI conventions** cover model calls. They give names like `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens` and `gen_ai.tool.name`. Our `gen_ai.chat` span uses those names. Fields the standard doesn't cover yet, like cost, the config fingerprint or which check fired, go under our own `agent.` prefix.

The GenAI conventions are still young, and some names have already changed. Keep every name in one file, so a rename is a one-line change. We also keep a **span contract**: a list of every span and the fields it must carry. A test fails if the code writes a span that isn't on the list, or leaves out a required field.

## Store, redact or drop

Decide where every field goes before you write the first span.

{{drawing: trace-bins}}

- **Store** the structure on every turn: span names, times, models, tokens, cost, tool names, outcomes, checks and decisions. None of it is personal, and it answers most questions.
- **Redact** the words. The customer's message, the reply, tool arguments and results are kept only on turns chosen for capture, masked first, then cut to a fixed length. In our harness that is 4,000 characters. Each turn also carries a flag saying whether its words were kept, so a check that found nothing in an empty reply isn't counted as a pass.
- **Drop** what should never leave the process. Our redaction step masks Aadhaar numbers (it checks the last digit, so a random 12-digit reference isn't mistaken for one), PAN, card and phone numbers before anything is exported.

On the claims assistant in Azure today, no words are captured at all. The structure alone was enough to explain the planted-note turn.

## How long to keep it

Pick a number on purpose. Ours is **30 days** in the Log Analytics workspace, which is included in the price, with a daily cap so a runaway logger can't run up a bill. Anything you need for longer, such as a turn that became a test case, should be copied out into your test suite, not kept by making every trace live forever. If your industry has its own retention rules, those win.

## Replay: stepping through yesterday

A trace tells you *what* happened. **Replay** lets you watch it again, one step at a time, and try a fix.

{{drawing: trace-replay}}

Replay needs one more piece: the recorded model answers. Our harness can record each real model call once and play it back later, with no network and no cost. Each recording is keyed by a fingerprint of exactly what the model was sent. If you change the prompt, the model or the tool list, the replay refuses rather than quietly calling the live model, so you always know which run you're looking at.

A replay goes like this:

1. Find the turn by its conversation id.
2. Load the recorded model answers and run the turn again through the real harness.
3. Pause at each span and compare: what the model asked for, what the tool returned, what the check decided.
4. Change one thing, such as the prompt, the rule or the tool, and run it again.
5. Save the turn as a test, so the same mistake can't ship twice.

This works for a turn whose words and model answers were recorded, such as a test run or a turn chosen for capture. In our harness, turning any production turn into a test in one step is not built yet; it is on the list.

That last step is where tracing meets **evals**, the tests you run on an agent before and after release. A good trace is the raw material for a good eval. Evals get their own post.

## Four mistakes we see often

1. **Logging only the final answer.** You can see that it went wrong, never where.
2. **Logging full personal data.** Traces get copied, exported and shared with vendors. Anything personal in them is now in all those places.
3. **No prompt version.** Prompts change more often than code. Without a version on every model call, you can't tie a bad week to the change that caused it.
4. **Traces in a format you can't leave.** A vendor's own logging library is quick to start with. Then the price changes, or you need a second tool, and every span has to be rewritten. Write OpenTelemetry and swap the exporter instead.

## Six questions to check your own agent

1. Can you pull up every step of one turn from a conversation id alone?
2. Does every model call record the model that answered and the prompt version?
3. Can you tell which check fired, and whether a check failed quietly?
4. Do you know the cost of a single turn, not just the monthly bill?
5. Could you show a regulator your traces today without exposing personal data?
6. Could you replay last Tuesday's worst conversation without calling the live model?

If the answer to the last one is no, start there; the other five come along on the way.

