---
title: Shipping agents: versioning prompts, models and tools together
published: false
canonical_url: https://cleandataengineering.ai/writing/shipping-agents/
description: An agent's behaviour comes from its prompt, its model, its tools, its checks and its settings, so release them together as one sealed, fingerprinted unit. Pin the model, gate every release on quality, cost and every model it can reach, send a small share of traffic first, rehearse the rollback, keep a kill switch, serve exactly what was tested, and stamp the release id on every trace.
---

*Originally published at [cleandataengineering.ai](https://cleandataengineering.ai/writing/shipping-agents/).*


On Friday evening someone opens the prompt in the admin screen and tidies a sentence. No pull request, no test run. It's only words.

On Monday the refund numbers look odd. Was it the prompt edit? The model provider's update over the weekend? The new tool someone added on Thursday? Nobody can say, because nothing recorded which prompt, which model and which tools answered each customer.

What an agent does comes from five things that change on different days, through different doors. This post is about shipping them as one.

## One release is one sealed box

{{drawing: ship2-sealed-box}}

A **release** of an agent is everything that changes what it does, versioned together:

1. **the prompt**, the instructions the model reads
2. **the model**, down to its exact version
3. **the tool definitions**, their names and argument schemas
4. **the checks**, the rules and limits the code enforces around the model
5. **the config**, such as temperature, step budgets and routing rules

Seal them together and give the box a **fingerprint**: a short code computed from everything inside. Change any one thing and the fingerprint changes, so you know you have a new release that hasn't been tested yet.

In our reference agent, a table-driven test spells out what is in and what is out. A new model, prompt version, routing rule, temperature or step budget must change the fingerprint. Rotating an API key or pointing at a different tool server address must not, because neither changes what the agent decides.

One honest lesson: that fingerprint hashes the prompt's *label* ("v2"), not its text, so an edit that forgot to bump the label would run under the old fingerprint. It's logged as an open finding. A label is a promise someone has to keep; a hash of the text keeps itself.

## Pin the model version

"Latest" is not a version. Many providers offer a moving name that points at whatever model is current. Use it, and your agent changes on a day you didn't choose, and last week's tests describe a different system.

So name the exact version, and keep a short list of models the agent is allowed to use. The reference agent pins one model per run, from an approved list of three, and refuses to start if asked for anything else.

Pinned models still disappear. That agent's earlier list named two models the provider had retired, and every call came back "not found". Only a live check against the provider's model list catches that.

The [AI Assurance Catalog](https://github.com/dataagentsai/ai-assurance-catalog) asks for this in [AAC-0012](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0012.yaml): record the exact model and prompt behind each request, and test that you can go back to the previous pair.

## Prompts are code, so gate them like code

{{drawing: ship2-one-word}}

The picture is an illustrative example, but the shape is common. One word leaves the prompt and the agent becomes a little more willing. A person reading the change would approve it. A golden case at the edge of the 30-day rule would not.

A **release gate** is the list of things that must be true before a release goes out. It runs in your build pipeline on every change, and if any line fails, the release stops. Our post on [offline evals](/writing/offline-evals/) covers how to build the tests behind it. For shipping, four lines matter most.

1. **The golden set and the scenarios pass.** A **golden set** is a frozen list of cases with known right answers; a **scenario** is a whole conversation run against a simulated world. The new release is compared case by case with the one customers have today, not with perfection ([AAC-0013](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0013.yaml)).
2. **Cost does not regress.** Measure cost per successful task on the same frozen set, and block a big increase the way you block a quality drop ([AAC-0102](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0102.yaml)). Otherwise a small quality gain bought with double the spend ships quietly and turns up on the invoice. The reference agent keeps its cost per task in a committed baseline file that may only stay the same or get better.
3. **Every model it can reach is evaluated.** Not just the main one. If the agent can fall back to a cheaper model when the main one is busy, that fallback serves customers too, usually in the middle of an incident ([AAC-0098](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0098.yaml)).
4. **Routing changes count.** A change to which model handles which request is a behaviour change, even when it ships as a config edit ([AAC-0101](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0101.yaml)).

To be honest about our own state: the reference agent has three approved models but only measures the pinned one. The other two are checked for being configured and priced, not for being right. It's an open finding. Where these tests sit among the others is in the [agent testing pyramid](/writing/agent-testing-pyramid/).

## Canary, watch, then roll out

{{drawing: ship2-release-road}}

The gate covers the cases you thought of. Real customers will think of others, so don't send everyone at once.

A **canary** release sends a small share of real traffic, say 5%, to the new release while everyone else stays on the old one. You watch the two side by side: the same [online checks](/writing/online-evals/), the same error and hand-off rates, the same cost per turn, split by release. If the canary looks no worse after an agreed window, move it to 100%. If it looks worse, send that 5% back.

Our claims assistant on Azure is set up for this: two revisions side by side, and one command sets the split to 95 and 5. That exercise hasn't been run yet, so it's a step still to do, not a claim.

## Rollback is a drill, not a hope

A **rollback** means putting the previous release back. It only works if the previous box is still sealed and still runnable: the same prompt text, the same pinned model, the same tool versions, the same checks.

The catch is that the parts drift apart. The reference agent once kept its routing label and its routing rules in two places, both reading "v2". On the day they disagreed, a rollback would have restored the label and not the rules. Now the agent refuses to start if they differ.

So rehearse it: roll back on purpose, on a schedule, and check that what comes back is the box that was tested. AAC-0012 says reverting is tested rather than assumed.

## Feature flags and a kill switch

A **feature flag** is a setting you can change without a new deploy, such as turning a new tool on for some users. Flags are useful, but a flag that changes behaviour is part of the box. If flipping it changes what the agent does, it should change the fingerprint, and it should pass the gate first.

There is one flag that skips the queue: the **kill switch**. In our harness it's a single setting, `agent.enabled`, read at the start of every turn. Set it to false and the next turn gets a polite "paused" reply with no model call and no tool call, while work already waiting for a person goes on. When something is wrong and you don't yet know why, you need a stop that needs no deploy.

## Serve exactly what was tested

A gate proves something about one specific box. Swap anything in it afterwards and the proof no longer covers what customers use ([AAC-0107](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0107.yaml)). The swap is usually invisible: a container rebuilt from the same tag, a model alias that moved, a prompt edited in an admin screen.

So pin everything by an exact identifier: the container by its digest (a hash of its contents, not a name like "latest"), the model by its version, the prompt by its hash. Then, as the release starts, check that the fingerprint serving traffic is the fingerprint that passed.

## Stamp the release on every trace

{{drawing: ship2-trace-stamp}}

Every turn's trace in the reference agent carries the config fingerprint as `agent.config.fingerprint`, and a test checks it's there.

That turns Monday's mystery into a filter. Group the bad turns by release: either they all carry one release, such as the canary that started on Tuesday, or that release is cleared. Our post on [tracing agents](/writing/tracing-agents/) covers the rest of what a good trace holds.

## Mistakes we see often

1. **Editing prompts live in production.** A deploy with no test, no record and no way back.
2. **An unpinned "latest" model.** Your agent changes when the provider decides, and your evals describe a system that no longer exists.
3. **No rollback rehearsal.** The first try should not be during an incident, at night.
4. **Evaluating only the main model.** The fallback goes untested until the main model is overloaded, exactly when you can least afford surprises.

## Six questions to check your own release process

1. If I point at one customer's conversation from last week, can you tell me the exact prompt, model, tools and checks that answered it?
2. Does any change to the prompt text, even one word, produce a new fingerprint and run the gate?
3. Is every model your agent can reach, fallbacks included, scored on your golden set?
4. Does a cost increase block a release, or only show up on a chart?
5. When did you last roll back on purpose, and did the old release come back whole?
6. If the agent started misbehaving right now, how many minutes until it stops, and does stopping it need a deploy?

Ship the box you tested, the whole box, and nothing but the box.

