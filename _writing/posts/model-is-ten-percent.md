---
title: The model is 10%. The harness is the other 90%.
date: 2026-10-31
subject: ai
audience: builders
kind: explainer
draft: true
summary: Most of a working agent is not the model. It is the ordinary software around it, called the harness: what the model sees, what it may touch, what pulls it back, and what writes every step down. This post draws the whole harness on one page.
linkedin: Your agent demo worked. Then real people used it. The fix is almost never a better prompt or a bigger model. It's the 90% of the agent that isn't the model at all. One page, five drawings.
deeper: /learn/agent-harness/
deeper_label: the Agent Harness tutorial, drawn box by box
---

Every agent demo looks the same. You give a model a few tools, write a good prompt, and it books the meeting, finds the order, answers the question. It feels like magic.

Then real people use it. Someone asks two things at once. A tool times out. A document contains a sentence that sounds like an order. The model, trying to be helpful, promises something it can't deliver. Most teams react by rewriting the prompt, and then rewriting it again.

The teams whose agents survive do something else. They build a **harness**: the plain software around the model that decides what it sees, what it may touch, and what happens when it gets something wrong.

## The horse and the harness

A horse is strong and fast, and it will pull all day. But it doesn't know the road, it can be startled, and now and then it bolts. Nobody fixes that by shouting at the horse. We put it in a harness: blinkers, reins, a cart and a driver.

{{drawing: horse-road}}

A language model is the horse. Your code is the harness. Its one job is to **keep the horse on the green path**:

- **Green** is the job done properly: the answer says only what the tools returned.
- **Yellow** is allowed with care: ask the person first, wait for approval, or re-check.
- **Red** is never allowed, however the model was talked into it.

A better horse drifts less often. But nobody can promise it never drifts, so the reins stay.

## What the harness is made of

Put the model in the middle of a page and draw everything else a working agent needs. You get something like this.

{{drawing: ten-ninety}}

The numbers are a picture, not a measurement. But in every agent we have built, the call to the model is one small function, and everything else on this page is the rest of the code. In plain words, the nine jobs are:

1. **Context:** decides what the model sees on each step, and what is left out.
2. **Tools:** the short list of things the model may ask to do. If a tool isn't on the list, the model can't even ask for it.
3. **Checks:** small rules that pull the model back before something wrong happens.
4. **State and memory:** what was said and what was done, so nothing is lost between steps or between visits.
5. **Durable steps:** if the server restarts halfway through, the work carries on and nothing runs twice.
6. **Human approval:** for risky actions, the agent waits for a person to say yes.
7. **Traces:** every step written down, so you can see what happened and why.
8. **Evals:** a driving test the agent must pass before each release.
9. **Cost meter:** a budget for each task, so one bad conversation can't burn a week's money.

None of these needs a smarter model. All of them are ordinary software that engineers already know how to build and test.

## One turn, step by step

Here is what happens when a person asks the agent something.

{{drawing: agent-loop}}

1. A person asks a question.
2. The harness builds the context: the instructions, the conversation so far, and the tools allowed for this person.
3. The model picks the next step. Either it answers, or it asks for a tool.
4. The harness checks the request, and only then calls the tool.
5. The tool answers. The harness hands the result back to the model, clearly marked as *data, not instructions*.

This repeats until the model has an answer. The harness checks the answer too, then sends the reply.

Notice who does the touching. The model never calls a tool, reads a database or sends a message itself. It only **asks**. The harness decides.

## One rule, four places

The most useful part of the harness is the checks. A check is a small, plain function that answers one question with yes or no. There are four natural places to put one.

{{drawing: four-checks}}

- **Before the model:** is this message allowed in at all? Is the person signed in? Is the agent switched on?
- **After the model:** is what the model wants to do safe? Is the answer grounded in what the tools returned?
- **Before the tool:** did the person actually ask for this? Is the amount within the limit?
- **After the tool:** fence the result so it is treated as data, and cut it down if it's huge.

Take a refund. The model may be fooled by a sentence hidden in an email and ask for a ₹40,000 refund. That's fine, because asking is all it can do. The check before the tool looks at what the person actually wrote. They never asked for a refund, so the call never runs, and the model is told why.

The model was fooled. The harness made it not matter.

## Why the harness, not a better prompt

Three reasons.

**A prompt is a hint. A check is a rule.** "Never refund without approval" in a prompt works most of the time. The same sentence as code works every time.

**A harness can be tested.** You can write an ordinary unit test for "no refund without a request". You can't write one for a prompt.

**The harness outlives the model.** Models change every few months. When the harness owns the context, the tools and the checks, swapping to a new model means changing one function, not rebuilding the agent.

## What to build first

You don't need all nine parts on day one. Build them in this order.

{{drawing: build-order}}

- **Day 1:** the loop, three tools, and a trace of every step. You can't fix what you can't see.
- **Week 1:** checks on anything that changes data or moves money, state and memory, and a cost budget per task.
- **Month 1:** evals that run before every release, human approval for risky actions, and steps that survive a crash.

You can stop on any stair and still have something that works.

## Five questions for your own agent

1. Can the model reach a dangerous tool directly, or can it only ask?
2. If a document tells your agent to do something, what stops it?
3. Can you replay yesterday's bad conversation step by step?
4. Is there a test that must pass before a new prompt or model goes live?
5. What is the most one conversation can cost?

If any answer is "the prompt handles it", that is where your harness starts.

Assume the horse will sometimes bolt, and build the harness so it can't leave the road.
