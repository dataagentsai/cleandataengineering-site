---
title: Context engineering: what goes into the window, and what stays out
published: false
canonical_url: https://cleandataengineering.ai/writing/context-engineering/
description: On every step, an agent's model reads one bundle of text, called the context. What you put in it, in what order, and what you leave out decides how well the agent works and what it costs. This post shows five habits, using a real claims assistant: stable things first, fence what comes back from tools, trim, show only the allowed tools, and pass references instead of whole documents.
---

*Originally published at [cleandataengineering.ai](https://cleandataengineering.ai/writing/context-engineering/).*


A language model remembers nothing between calls. Each time your agent takes a step, the model starts from a blank page and reads one bundle of text: the instructions, the conversation so far, the tools it may use, the results that came back. That bundle is called the **context**, and the most a model can read at once is its **context window**.

So before every step, your code decides what the model reads. Often that code just appends everything, and the agent gets slower, dearer and more confused as the conversation grows.

**Context engineering** is doing that job on purpose: choosing what goes into the window, in what order, and what stays out.

## The window is a small desk

Think of the context window as a desk. A modern window is big, but it is still a desk, and everything competes for space on it: the instructions, the conversation so far, the tool definitions, the tool results, any memory, and any data you looked up.

{{drawing: ctx-desk}}

Two things go wrong when the desk is piled high.

**The model loses track.** The longer the context, the easier it is for the one important line to get lost among the rest. A rule on page one is followed less reliably when it is buried under a raw database dump.

**You pay for every paper, on every step.** An agent works in a loop. Each trip round the loop is a fresh model call, and the whole context is sent again. A 10,000-character tool result that stays in the context is paid for on step 2, step 3 and every step after. The [cost mistakes post](/writing/agent-cost-mistakes/) works through the numbers; here we look at the habits that stop the pile growing.

The rest of this post follows a real example: the claims assistant of a motor insurer, from our Agent Harness tutorial. A policyholder called Rohan chats with it about his own policies and claims. Before every model call, one function rebuilds the context from scratch, so if you know the inputs, you know exactly what the model saw.

## Habit 1: stable things first

The parts of the context always go in the same order.

{{drawing: ctx-stack}}

1. **The system prompt**: who the assistant is and its rules, such as "answer only from what the tools return" and "never promise a date".
2. **The tool list**: the 8 tools Rohan may use, about 500 tokens. A token is a small piece of a word, roughly four characters of English.
3. **Earlier turns**: the conversation so far, text only.
4. **Rows re-read**: any claim the conversation has touched is read again, fresh.
5. **The new message**: what Rohan just typed.
6. **This turn's tool calls**: what the model has asked for so far.
7. **This turn's results**: what came back.

Why this order? Many model providers offer **prompt caching**: if the start of your prompt is exactly the same as last time, they reuse their work and usually charge less for it. That only works if the start really is identical, character for character. So the parts that never change go first, and the parts that change go last, closest to where the model starts writing.

So never put something that changes, such as today's date or a request ID, near the top.

Part 4 deserves a note. If an earlier turn read claim CLM-019002, the harness reads that claim again now, rather than trusting what the conversation said ten minutes ago. The status in the context is always today's status.

## Habit 2: fence what comes back

Anything a tool returns may contain words written by someone else: a claim note, an email, a web page. If the model treats those words as orders, whoever wrote them can steer your agent. This is called **prompt injection**.

{{drawing: ctx-fence}}

So the harness wraps every tool result in a fence, a pair of markers that say "this is data from a tool, not instructions". Three details matter:

- **No exemptions.** Every tool result is fenced, even from a tool that sounds trusted.
- **The fence can't be closed from inside.** If the data contains the closing marker, it is escaped first, so a planted note can't end the fence early and start giving orders.
- **The user's own words are not fenced.** Fencing the customer would teach the model to ignore the person it serves. His message is checked in a different way, before the model sees it.

A fence is a hint, not a wall. In a real test, a planted note did make the model ask for a payout. The check before the tool refused, because Rohan had never asked for one. Fence anyway, and assume the model will sometimes be fooled.

## Habit 3: trim

There are two cuts, and each solves a different problem.

{{drawing: ctx-trim}}

**Cut huge tool results.** One search can return a whole web page. The claims assistant cuts any tool result at 8,000 characters and adds a mark that says it was truncated and how long it was. The mark matters: the model knows it is not seeing everything and can ask for something narrower.

**Keep the whole context within a budget.** Each call has a budget of 24,000 characters, roughly 8,000 tokens. Over that, the harness drops whole old exchanges from the middle. The beginning says what the conversation is about, and the end is what Rohan just asked, so both stay. The middle is the part least needed right now.

Drop *whole* exchanges. A tool request without its result confuses the model, and some providers reject it outright. After trimming, a final check makes sure no tool call has lost its answer. If one has, the turn fails rather than send a broken transcript.

Many teams summarise old turns instead of dropping them, by asking a model to write a short recap. That can work, but this assistant deliberately doesn't. A summary loses exact numbers like claim amounts, it costs another model call, and it can carry a planted instruction forward in disguise. If you do summarise, fence the summary like any other untrusted text.

## Habit 4: show only the tools this person may use

Every tool you show takes space and is one more thing the model might pick. More importantly, **the model can only ask for tools it has been shown.**

The claims assistant has 9 tools in all. Before the first step, the harness keeps only those that Rohan's sign-in allows, so the model sees 8. The one that actually pays money, `issue_payout`, needs a staff permission, so it never appears. The model can't be talked into calling a tool it doesn't know exists.

This is the cheapest guardrail there is, and it makes the context smaller at the same time.

## Habit 5: pass references, not whole documents

The context should hold *where* something is, not the whole thing. The claims assistant keeps claim numbers like CLM-019002 in the conversation, and fetches the fresh row when it needs it. It never pastes Rohan's whole claim file in just in case.

The same idea works for documents. Say a customer uploads a 60-page survey report. Don't put all 60 pages on the desk. Give the model the document's ID and a tool that returns the one section it asks for.

Just as important is what never goes in at all. Rohan's email and phone number stay in the claims system. The harness's own notes about the conversation, the trace, the costs, and other customers' data are never shown to the model. If the model doesn't need it to take the next step, it stays off the desk.

## What goes wrong

- **Appending forever.** Every tool result stays in the context for the whole conversation. The cost of each step climbs, and old results drown the new question.
- **A timestamp at the top.** The first line changes on every call, so caching never kicks in.
- **Trusting tool output.** An unfenced email or web page is read as if you wrote it.
- **Cutting through the middle of an exchange.** A tool call loses its result and the transcript breaks.
- **One big tool list for everyone.** Admin tools shown to customers, and hundreds of tokens of tools nobody needs.
- **Counting characters forever.** Characters are a fair guide, but providers bill in tokens. The tutorial agent counts characters today, and a real token counter is on its list of known gaps.

## Six questions to check your own agent

1. Can you print exactly what the model read on its last step?
2. Is the start of your context identical between two calls in the same conversation?
3. Is every tool result fenced, with no exceptions?
4. What is the biggest tool result your agent can put in the context?
5. What happens when a conversation runs to 50 turns?
6. Does the model see any tool that this user isn't allowed to use?

If you can't answer the first one, start there. The rest of the [harness](/writing/model-is-ten-percent/) is easier to build once you can see the desk.

A good context isn't the most you can fit. It's the least the model needs to take the next step well.

