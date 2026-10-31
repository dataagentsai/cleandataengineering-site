---
title: Who checks the checker? The oracle problem in agent simulation
date: 2026-10-31
subject: ai
audience: builders
kind: explainer
draft: false
summary: In testing, the "oracle" is whatever decides pass or fail, and for an agent in an open conversation there is no free one. A simulation should decide with code that reads what changed in the world first, then rules on actions, then what was owed but never done, and only last an LLM judge that has been checked against people. Then test the checkers themselves by planting known bugs and seeing which ones they miss.
linkedin: Your agent passed every test. Who decided it passed? If the answer is "another model read the chat and said it looked fine", you have a student marking their own paper. Here is the oracle problem in plain words, the order of checkers that solves most of it, and how to prove your checker would catch a bug.
deeper: /learn/agenttwin/
deeper_label: AgentTwin explained, including how it helps the tester not miss
---

Priya sends back a kurta and asks the shop's support agent for her ₹2,400. The agent replies, *"Your refund is on its way."* Your test suite runs that conversation and prints a green tick.

Here is the uncomfortable question: what decided the tick was green? Somebody, or something, had to know what the right outcome was. If that something is wrong, every green tick after it is wrong too, and nothing will tell you.

Testers have a name for that something. They call it the **oracle**. This post is about the oracle for agent tests: why it is hard, the order of checks that makes it mostly easy, and how to check the checker.

## The oracle problem in plain words

Every test has two halves. One does something, such as playing a conversation. The other decides whether what happened was right. That second half is the oracle.

For a lot of software, the oracle is cheap. If you test a calculator, maths tells you the answer. You can compare with a trusted library, or check rules that must always hold, such as *a + b equals b + a*. The [AgentTwin guide](/learn/agenttwin/) calls this "maths gives an oracle for free".

An agent has no free oracle. Whether "refund this order" was right depends on the shop's rules, the order's state, who is asking and what was promised. A model can write ten thousand conversations in a minute. It can't tell you which outcome is correct unless the rules are written down.

That is the oracle problem: generating tests is easy, knowing the right answer is hard.

## The calculator problem: don't let it mark its own paper

{{drawing: orc-own-paper}}

There is a tempting shortcut. Generate tests by running the code and recording what it does today. Every test passes, and coverage looks perfect. But those tests have recorded the bugs as the right answers. You used the calculator to check the calculator.

Agents have their own version of this. The agent's model writes a reply, and then the same model, or a close cousin, reads the chat and decides whether it went well. The reply sounds confident and polite, so the grade comes back high. Models are known to prefer their own writing, which is why the [AI Assurance Catalog](https://github.com/dataagentsai/ai-assurance-catalog) lists self-preference among the judge biases you must probe ([AAC-0085](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0085.yaml)).

The rule is simple: **the thing under test never grades itself.** The answer key has to come from outside it. For an agent, the answer key is the written spec (its rules and promises) applied to the state of the systems it touched.

## How a simulation decides pass or fail

In a simulation, as described in [the flight-simulator post](/writing/agenttwin-flight-simulator/), the agent is real and the world around it is pretend: the customer, the order system, the payment system. Because you own that pretend world, you can look inside it after every run. That changes the oracle problem a lot.

{{drawing: orc-order}}

Ask four questions, in this order:

1. **What changed in the world?** Read the systems, not the chat. Is Priya's order now marked refunded? Did exactly one payment of ₹2,400 go out? This is a plain comparison of rows before and after.
2. **Was every action allowed and asked for?** Each write to a system is checked against a rule. Did Priya ask for this refund? Is it her order? Is the return within the window? An action nobody asked for fails, however polite the reply.
3. **Was anything owed but never done?** This is the sneaky one. The spec says "a refund is owed once the return is received". If the return was received and no refund exists, the run fails, even though nothing bad *happened*.
4. **Only then, an LLM judge.** An **LLM judge** is a second model asked to grade something. Use it for what code can't check, such as "was the tone right for an upset customer?", and only after it has been checked against people (more below).

Why does question 3 need its own checker? As the AgentTwin code puts it, a missed action "leaves no evidence". The world didn't change, so the first check sees nothing wrong. No rule was broken, so the second sees nothing wrong. Only a checker that knows what the run *owed* can see the hole. And it must work out what was owed from the opening state, because a refund that was done removes itself from the "still owed" list.

The same thinking covers the agent's words. If the agent says "your refund is on its way" and the world shows no refund, that is a false claim about its own actions. The catalog makes this an obligation of its own: a claimed action must be supported by that action's result, and a refusal or error is not a success ([AAC-0110](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0110.yaml)). Code can check this by comparing the claim with the row.

## When you do need a judge, check it against people

Some questions really do need judgement. "Did it answer what she actually asked?" "Was it kind without promising anything?" For those, an LLM judge is fine, but it has to earn its place.

{{drawing: orc-agreement}}

Take a set of cases, have people label each one pass or fail, and run the judge on the same set. Then compare. The catalog asks for three things before a judge may block a release:

1. **Agreement with human labels, measured properly** ([AAC-0084](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0084.yaml)). Not raw accuracy. In the picture, a judge that always says "pass" would agree four times out of six by luck. Use a statistic that removes lucky agreement, such as Cohen's kappa, which compares the agreement you got with what chance alone would give.
2. **Known biases probed** ([AAC-0085](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0085.yaml)). Swap the order of two answers, pad one with extra words, change the formatting, and see if the verdict moves. It shouldn't.
3. **Stable verdicts** ([AAC-0086](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0086.yaml)). Score the same case several times, and again with the instructions reworded but meaning the same. An unstable judge can't gate anything.

Until a judge passes all three, let it report, not block. The [offline evals post](/writing/offline-evals/) shows where this fits in a release gate.

Look hardest at the crosses. The one row where people said fail and the judge said pass tells you more than the five ticks.

## How to know your checker is right: plant a bug

You now have checkers you trust. How would you know if one of them was blind? The old software answer is **mutation testing**: break the code on purpose, in a small known way, and see whether any test notices. Each broken copy is called a **mutant**.

{{drawing: orc-mutants}}

The AgentTwin guide lists the kind of mutants worth planting in an agent:

- remove a check, such as "is this the customer's own order?"
- loosen a limit, such as a 7-day return window that now allows 8
- drop the repeat guard (often called an idempotency key), so the same message sent twice pays twice

Run the whole suite against each mutant. If a test goes red, the mutant is "caught" and that checker works. If every test stays green, you have found a missing test, and it has a name: "nobody checks the 8th day". Python has tools such as mutmut for this.

To be honest about where this stands: in AgentTwin, mutation testing is listed as "to build, first". What exists today is a different cross-check. AgentTwin's verdicts were compared with τ²-bench's own verdicts (τ²-bench is a published agent benchmark) on 2,472 recorded runs, and every disagreement has a stated cause. Comparing two independent oracles is another way to catch a blind one.

## Mistakes that make checkers lie

1. **Checking words instead of the world.** AgentTwin hit this itself. A test that the reply "never says *has been refunded*" failed on *"Nothing has been refunded yet"*, which was exactly the right sentence. Its own notes now say to compare the claim with the row instead.
2. **Passing questions for free.** If a customer only asks "where is my order?", nothing changes in the world, so a check that only looks for wrong changes always passes. The AgentTwin notes call this a "false pass": the suite reports success because it can't see. Questions need a truth check that compares the answer with the record.
3. **Asking the final state what was owed.** Once a refund is done, it is no longer owed. Work out obligations from the starting state, then check what was done.
4. **The agent's team owns the yardstick.** If the agent's team can edit its own tests, it can make them easy. Keep the answer key somewhere the team under test can't change.
5. **A judge where an `if` would do.** "Is the refund ₹2,400 or less?" is not a question for a model.
6. **Never planting a bug.** A suite that has never caught a known fault hasn't proved it can catch any.

## Six questions to check your own checkers

1. For each test, can you say in one sentence what decides pass or fail, and where its right answer comes from?
2. Does anything grade the agent using the agent's own model?
3. Do your checks read what changed in the systems before they read the reply?
4. Can a run fail because something owed was never done, even when nothing changed?
5. Has every LLM judge been scored against human labels, probed for bias and rerun for stability before it is allowed to block?
6. When did you last break the agent on purpose, and which tests noticed?

A green tick is only as honest as whatever decided it was green, so test that too.
