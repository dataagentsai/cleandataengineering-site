---
title: The agent testing pyramid
published: false
canonical_url: https://cleandataengineering.ai/writing/agent-testing-pyramid/
description: Most of an agent is ordinary software, so most of its tests are ordinary tests that run in seconds for free. Tests that need a real model are few, and they sit near the top. This post draws the whole testing strategy as a pyramid, from unit tests at the bottom to production monitoring at the top.
---

*Originally published at [cleandataengineering.ai](https://cleandataengineering.ai/writing/agent-testing-pyramid/).*


Ask a team how they test their agent and you often hear: "We run it against the model and look at the answers." Every test is slow, every run costs money, and the same test passes on Monday and fails on Tuesday.

That isn't a testing problem. It's a shape problem. The model is one function in a large program. The rest is routing, tools, checks, state and retries, as we drew in [the model is 10%](/writing/model-is-ten-percent/). That code can be tested the way you test any code: exactly, quickly and for free.

So the tests form a pyramid. Lots of cheap, exact tests at the bottom. A few slow, costly ones at the top. This post walks it from the bottom up.

## The whole pyramid

{{drawing: pyr-pyramid}}

The line that matters is the dashed one. Below it, the model is replaced by a script or a recording, so nothing calls a live model. Above it, a real model, real attackers or real traffic are involved, and each test costs time or money.

Here are real numbers from the claims assistant in our Agent Harness tutorial: **750 tests from 35 files, 0 failures, in about 80 seconds.** The larger reference agent has 2,179 tests from 106 files. Almost all of them sit below the line.

## Layer 1: unit tests for the harness

The harness is the code around the model: the checks, the tools, the router that picks a path. Each piece is an ordinary function, so it gets ordinary unit tests.

The best way to write them is as a table. Take the rule "a payout over the ₹25,000 limit needs a person". The test is one function and a table of rows: ₹24,999, ₹25,000 and ₹25,001. One rupee under the limit, exactly on it, one rupee over. Most bugs live at the edges, so write the edges out.

In the tutorial's agents, the model in these tests is a **scripted model**: a fake that returns the reply the test tells it to. The database and tools are in-memory fakes too. A test like "the model asks for a refund nobody requested; the check must block it" runs in milliseconds and gives the same answer every time.

## Layer 2: contract tests for every tool and port

A **port** is a socket in your code where a vendor plugs in: the model provider, sign-in, secrets, logging, approvals, storage. Each vendor's code that fits a socket is an **adapter**.

A contract test is one table of rows per port that every adapter must pass. In the tutorial, six ports each have their own table. The model port has four adapters, from a scripted model to an Azure gateway, and all four pass the same rows.

That's what makes "swap Groq for Azure" or "swap Keycloak for Entra" a configuration change instead of a rewrite. The same idea applies to tools. If a tool says it returns a claim with an amount and a status, a test holds it to that promise.

## Layer 3: recorded model replies

Sometimes you want the real loop with a real model's reply, but not the cost or the randomness. That's what a **cassette** is for.

{{drawing: pyr-cassette}}

You call the real model once and save its reply to a file, keyed by a fingerprint of the question: the messages, the tool names and the settings. Every test after that plays the reply back. No network, no bill, and the same reply every time.

Two rules make cassettes safe:

1. **A mismatch fails the test.** If the question has changed, for example because a tool was added, the player refuses. You re-record on purpose.
2. **There is no fallback.** The player can't quietly call the live model when it misses. A test that spends money without telling you is the worst kind of test.

## Layer 4: scenario simulation

A **scenario** is a whole small story: who asks, what they say turn by turn, what goes wrong, and what must be true at the end. The tutorial runs these in **AgentTwin**, a simulated world around the real, unchanged agent. It has a fake customer, a fake claims system, a clock that can jump ahead, and faults it can switch on.

The key is that a scenario is judged by **the state of the world**, not by the wording of the reply. Was anything paid? Was the payout made exactly once? Was a person brought in? That's what catches "Yes, it's registered" when nothing was registered.

The claims assistant passes 29 of 29 scenarios. Today they run with a scripted model, once each. Running them with a live model, several times over, is designed for nightly runs.

## Layer 5: golden-set evals

A **golden set** is a list of single cases with known right answers, frozen in Git. You run it against a real model before a release and compare the score with the last release. The reference agent has 35 golden cases, built from the spec's own limits: a 30-day rule gets cases at day 29, 30 and 31.

One rule matters more than the rest: never edit a case to make it pass. We'll cover evals properly in a later post.

## Layer 6: red teaming

A red-team test is an attack, such as a note planted in a claim that says "approve the payout". It passes only if the world is unchanged afterwards. In the tutorial, each scenario gets 20 generated injection attempts, and the scripted model is written to fall for every one. The test checks that the harness still stops the write. The checks themselves are the ones sorted in [every guardrail your agent needs](/writing/guardrails-sorted/).

A successful attack blocks the release and becomes a permanent test.

## Layer 7: failure drills

A failure drill breaks one thing on purpose and checks that the agent stays correct.

{{drawing: pyr-drill}}

The tutorial's drills include a crash before a step is saved, the same message arriving twice, an approval clicked twice, the model failing twice in a row, and slow or stale reads. Several run in-process today. The live versions, breaking things on the real cloud, are still to build, and the tutorial says so.

A pass doesn't mean the agent was clever. It means nothing was paid twice, nothing was lost, and the reply told the truth.

## Layers 8 and 9: load tests and production

**Load tests** ask whether the agent holds up at, say, three times your busiest hour. Honestly, the tutorial has none yet. For now its real ceiling is the model provider's free quota: 8,000 tokens a minute, which is only three to five agent turns a minute.

**Production monitoring** is the top of the pyramid because it's the only test with real people in it. In the reference agent, a fake customer asks known questions through the real front door every 10 minutes. Its turns are marked as synthetic and left out of the numbers. A new release should take a small slice of traffic first. And every real miss should come back as a new test at the bottom.

## Which tests run when

{{drawing: pyr-when}}

Put the cheap tests where they run most. Unit, contract, cassette and scripted scenario tests run on every commit. Live-model repeats run nightly. Red team, drills and load run before a release. Production checks never stop.

## Five mistakes we see often

1. **Testing only with the live model.** Every test is slow and costs money, so people stop running them. Move everything you can below the line.
2. **Flaky tests from randomness.** A test that calls a live model will sometimes fail for no reason, and soon nobody trusts a red build. Script the model or replay a cassette. Where you really need a live model, run the case several times and require it to pass every time, not most times.
3. **No failure drills.** The happy path works, then the model provider has a bad hour and the agent tells customers their claim is approved. Pull the plug before your customers do.
4. **Red teaming once and never again.** Attacks change, and so do your prompts and tools. Keep every past attack as a test, and run the suite before every release.
5. **Judging the reply, not the world.** "Your refund is on its way" can be a lovely sentence and a complete lie. Check what actually happened.

## Six questions to check your own agent

1. How many of your tests run without calling a model, and how long do they take?
2. Do your rules have boundary rows, one under the limit, on it and one over?
3. Could you swap your model provider and prove nothing broke, in one test run?
4. Can a test ever call the live model by accident?
5. What does your agent say when the model is down, and is there a test for it?
6. When a customer hits a bug, how does it become a test?

Build the pyramid wide at the bottom, and the few tests at the top will be the ones worth paying for.

