---
title: Answer without the model first: 104 ms vs 7 seconds
published: false
canonical_url: https://cleandataengineering.ai/writing/answer-without-the-model/
description: Our claims assistant answers some questions without calling the model at all. When a customer names the claim, a few plain rules send the message down a direct path of one read and one approved template: 104 ms and $0, against about 7 seconds through the model loop. This build log shows how the router decides, which checks the direct path still passes, and when not to do it.
---

*Originally published at [cleandataengineering.ai](https://cleandataengineering.ai/writing/answer-without-the-model/).*


Rohan is a policyholder with a motor insurer. He opens the chat and types: "What's the status of claim CLM-019002?" The reply comes back in 104 milliseconds. No language model was called. It cost nothing.

Now he asks almost the same thing without the number: "what is the status of my claim". This time the reply takes 7,076 milliseconds, two model calls and $0.00058 in model tokens.

Both answers came from the same claims assistant, the reference agent in our [Agent Harness tutorial](/learn/agent-harness/). This is the build log of the part that made the first one fast: the **direct path**, where plain code answers before the model is ever asked.

## The receptionist who doesn't call the manager

Ask a good receptionist what time the shop closes and she tells you. She doesn't knock on the manager's door. Ask her for a refund and she does, because that needs someone with authority and judgement.

{{drawing: direct-receptionist}}

That is the whole idea, which we call **deterministic first**. Deterministic means the same input always gives the same output, so it can be tested completely. Build as much of the system as you can from parts like that, and hand control to a model only where you really need its flexibility.

A claim status, when the customer names the claim, is a closing-time question. The answer is one row in the claims system.

## Two roads from one fork

Every message passes a **router** first. The router is not a model. It is a short list of rules written as regular expressions, which are text patterns, and it runs in about 0 ms. It sends each message down the cheapest road that is still safe.

{{drawing: direct-two-roads}}

Here are the two real turns side by side, from the assistant running on Azure in October 2026.

| | Flow 1a: names the claim | Flow 1b: "my claim" |
|---|---|---|
| Road | Direct | Model loop |
| Model calls | 0 | 2 |
| Tool calls | 1 | 1 |
| Time | 104 ms | 7,076 ms |
| Model cost | $0 | $0.00058 |
| Trace spans | 14 | 38 |

On the direct road the harness made one read, `get_claim` for CLM-019002, and poured the result into wording a person approved in advance: "Claim CLM-019002 is registered. An assessor will look at it and tell you what they need next."

On the loop road the model first asked for `list_claims`, because Rohan never said which claim, then wrote the answer on a second trip. Look at where the 7 seconds went: the model provider, Groq, took only 0.6 and 1.0 seconds. Most of the rest was the gateway waking up and a content-safety check on each prompt and answer. The direct path skips all of that.

That is about 70 times faster. The money is small per turn, but [cost mistakes](/writing/agent-cost-mistakes/) compound with volume, and the time is what the customer feels.

## How the router decides

The router asks four questions, always in the same order. The first "yes" picks the road. If all four say no, the message goes to the model loop.

{{drawing: direct-rule-card}}

1. **Must a person handle this?** An injury, a request for a human, or a tow. Yes means hand it to a person. "Nobody was hurt" does not count as an injury.
2. **Must we refuse?** Six rules, such as promising cover or discussing someone else's policy. Yes means a polite, pre-written refusal.
3. **Which intents are in it?** An intent is what the person wants, such as `claim_status` or `report_claim`. There are seven. This step only counts them.
4. **Exactly one read, one reference?** Yes means the direct path.

Question 4 is strict on purpose. All three must hold: exactly one intent, that intent only reads (claim status, payout status or policy status), and exactly one reference of the right kind, a CLM- or POL- number. Two claim numbers, a typo like "pol 1", or anything that writes all go to the loop.

The order matters: hand-offs come first, so an injury in half a message is never ignored. The rules carry a version, `v1` today, written on every trace, and a test runs every example message from the spec.

The guiding rule is one line: **when in doubt, use the loop; never guess on the cheap road.** "My claim" could mean any of Rohan's nine claims, so the router doesn't pick one. Choosing a worker for every step is in [a model per step](/writing/model-per-step/); this is the step where the right worker is no model at all.

## The cheap road still passes the checks

The direct path is not a shortcut around the harness. It skips the model, and nothing else.

{{drawing: direct-same-checks}}

Before the router, every message goes through the same front door: the sign-in token is checked, the kill switch is checked, and a ledger row stops the same message being handled twice. The read itself is made with Rohan's identity, so the claims system checks that CLM-019002 is his, exactly as it would for a model's tool call.

After the template is filled, the reply goes through the same before-reply check as a model's answer. Three rules run there: no promise of cover, no personal data echoed back, and money shown in rupees. Approved wording gets checked anyway, because a template filled with the wrong value is still wrong. And if a value is missing, the template engine fails rather than printing a blank.

## How much traffic it can take

For the loop, the ceiling today is the model quota, not our servers. Groq's free tier allows 8,000 tokens a minute, and one loop turn uses 1,500 to 2,500, so the whole assistant manages only 3 to 5 loop turns a minute. The gateway in front of the model also allows 30 calls a minute.

The direct path uses none of that. No model tokens, no gateway calls, no content-safety checks. Its limits are our own servers, which hold no state and scale out on Azure Container Apps without code changes, and the claims system it reads from.

To be honest about what we know: no load test exists yet. The plan is Azure Load Testing at three times the expected peak. And 104 ms is the best real case, not a promise. Another direct answer, a policy status, took 643 ms, because 287 ms of it was fetching the token to read on Rohan's behalf. Every direct answer we recorded was still under a second.

## Why it is safer, not only cheaper

1. **It can't make anything up.** Every fact came from one read. No model fills a gap with a plausible guess.
2. **It can't be talked into anything.** A message full of clever instructions has no model to fool.
3. **A person approved the wording.** Nobody hopes the model phrased it carefully.
4. **It can be tested completely.** Same message, same road, same reply, every time.

## When not to do it

- **Anything that writes.** Releasing a payment or registering a claim never takes the direct path, even with a clean claim number.
- **Anything that needs judgement.** "Will my claim be approved?" is refused by a rule, and anything needing real reasoning goes to the loop.
- **When the rules would have to guess.** If you find yourself writing a rule to pick "the most likely claim", stop.
- **Rare questions.** A template has to be written, approved and kept up to date. Spend that on the questions people ask every day.

## What goes wrong

**A router that guesses.** Someone loosens question 4 so "my claim" picks the newest claim. It is right most of the time, and wrong for the customer with two open claims. A wrong confident answer is worse than a slow right one.

**A direct path that skips checks.** It is tempting to wire the template straight to the reply because "we wrote the wording ourselves". Then a template prints another customer's data, or a status nobody approved, with nothing in the way.

**Templates that go stale.** Example: the claims system adds a status called "on hold", and the template only knows the old ones. A strict engine fails loudly instead of printing a blank, but someone still has to own the templates and change them when the business does.

## 5 questions to check your own agent

1. Which of your most common questions could be answered from one read and a fixed sentence?
2. When your router isn't sure, does it send the message to the model, or guess?
3. Do template replies pass the same final check as model replies?
4. Is your router versioned, and is the version written on every trace?
5. Do you know where the seconds in a slow turn actually go?

The fastest, cheapest and safest model call is the one you never had to make.

