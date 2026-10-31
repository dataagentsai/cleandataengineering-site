---
title: The LLM gateway: the switch between your agent and every model
date: 2026-10-31
subject: llm
audience: builders
kind: explainer
draft: false
summary: An LLM gateway is one service that sits between all your apps and every model provider. It holds the keys, the list of approved models, the limits and budgets per team, the cache, the screening and the cost log, and it switches to another provider when one fails. It is not the provider, and it is not the place for business rules about money or consent; those belong in the agent's harness.
linkedin: If three teams each hold their own model API key, you don't have an AI platform, you have three bills and no switch. An LLM gateway is that switch. Here is what belongs in it, what doesn't, and the five mistakes we see most.
deeper: /learn/agent-harness/model-gateway.html
deeper_label: The APIM gateway, with its live policies, in the Agent Harness tutorial
---

Say a company has three things calling models. Priya's support agent uses one provider. Arjun's claims agent uses another. An analyst's notebook uses a third, with a key pasted into a cell. Each has its own key, its own retry code and its own idea of what a call costs.

Then finance asks a simple question: which team spent what on AI last month? Nobody can answer without opening three dashboards. A provider has an outage, and one of the three apps goes down while the others carry on. Someone leaves, and their key is still in an environment file.

The fix is one small service that every app talks to instead of the providers. It is called an **LLM gateway**. This post explains what it does, what it is not, and what you should keep out of it.

## A switchboard for model calls

Picture an old telephone exchange. Callers never wired themselves to each other. They plugged into a board, and an operator connected each call to the right line.

{{drawing: gw-switchboard}}

An LLM gateway is that board. Your apps and agents send every model call to it. The gateway decides which provider gets the call, adds the right key, applies the company's rules, and writes down what happened.

The trick that makes this painless is **one API for many models**. Most gateways speak the same request format as OpenAI's chat completions, so to an app the gateway looks exactly like a provider. Moving an app behind the gateway is usually a change of one setting, the `base_url`, plus a new key that the gateway issued. Swapping the model behind it later needs no change to the app at all.

## A provider is not a gateway

These two get mixed up all the time, because some features appear in both. They belong to different companies and protect different things.

| | Provider | Gateway |
|---|---|---|
| Who runs it | the business that hosts the model | the company that *uses* models |
| What it protects | its GPUs and its revenue | your data, your money, your uptime |
| Its rate limit stops | any one customer using up the hardware | any one of your teams using up your quota |
| Examples | Groq, OpenAI, Anthropic, Amazon Bedrock, Google Vertex AI | LiteLLM proxy, Portkey, Kong, Cloudflare AI Gateway, Azure API Management |

Bedrock and Vertex can serve many models from one endpoint, which makes them look like gateways. They are still providers: they run models and bill you for them. Your gateway sits in front of them, the same as in front of anyone else.

The products in the right-hand column differ in which jobs they do well, and they change quickly. Check each job below against the product before you pick one.

## One call through the gateway

Here is what happens to a single call. The order varies by product; this is one sensible version.

{{drawing: gw-one-call}}

1. **Key check.** The app shows a key the gateway issued. An unknown key is refused. The real provider keys stay inside the gateway, ideally in a secrets store. In our tutorial, the gateway is Azure API Management (APIM), and it fetches the Groq key from Azure Key Vault itself, so the key never appears in our code.
2. **Allow-list.** Only approved models may be called. Our APIM policy allows exactly one model, `gpt-oss-120b`. When a test script asked it for a different model, it answered 403 "model not allowed" in 250 milliseconds.
3. **Rate limits, quotas and budgets.** Our APIM allows 30 calls a minute; the 31st gets a 429 ("too many requests"), and the harness waits as told and retries. The next level up is a **budget per team**: each team gets its own gateway key, and the gateway counts spend against it, say ₹20,000 a month, before each call. A related limit, tokens per agent at APIM, is not available on the cheapest Consumption tier we use, so we haven't switched it on yet.
4. **Cache.** If exactly the same request came in a moment ago, return the stored answer and pay nothing. Exact-match caching is simple and safe. "Similar enough" caching is cleverer and riskier, so start without it.
5. **Content screening.** A classifier checks the prompt and the answer. Ours is Azure AI Content Safety: Prompt Shields looks for jailbreak attempts, and a harm check scores hate, sexual content, violence and self-harm from 0 to 6, blocking at 4 or more.
6. **Route.** The gateway picks the provider for this model and forwards the call with the provider's key.
7. **Log cost.** One row per call: which app, which team, which model, tokens in and out, and the price. Our APIM also sends its own token count to Application Insights, so we have a second count to check our own meter against.

Steps 1 to 3 can stop a call before a single token is paid for. That is a big part of why the gateway exists.

## When a provider goes down

Providers have bad hours. A good gateway treats that as routine.

{{drawing: gw-fallback}}

**Fallback** means a list: try provider A, and if it fails or is too slow, send the same call to provider B. The agent sees one normal answer. The log records where it switched. The check for this is easy to state: stop provider A in the middle of a load test, and no request should fail.

To be honest about our own setup: our tutorial agent has no second model today. Inside the harness, a failed call is retried up to 3 times, and after 3 failures in a row a circuit breaker stops calls for 10 seconds, so we don't hammer a provider that is already down. That limits the damage, but it doesn't keep the agent running. A fallback route is the next thing to add.

Two details matter when you build it. The backup model must also be on the allow-list, and it must behave well enough on your evaluations, because a backup that gives wrong answers is worse than a clear error. And retries need a ceiling. In our harness, all retries in one turn share one allowance of 4. If the gateway retries as well, count both, or one slow provider turns each call into many.

## What should not live in the gateway

The gateway is good at rules that are the same for every app. It is the wrong place for rules that need to know the business.

{{drawing: gw-two-boxes}}

The reason is simple: **the gateway sees the model ask for a tool, but never what the tool does.** It doesn't know that `request_payout` moves money, that the customer only asked a question, or that ₹40,000 is the limit for this policy. The agent's **harness**, meaning the ordinary code around the model that runs the loop and the tools, does know.

Our tutorial has a clear example. A claim note carried hidden text telling the assistant to request a payout. The model obeyed and asked for `request_payout`. Content Safety at the gateway didn't stop it, because APIM screens prompts and answers, not tool results. What stopped the payout was a rule in the harness: the customer never asked for one.

The gateway also fails open in places. If Content Safety is down, or its free quota of 5,000 checks a month is used up, our APIM lets the call through and records the verdict as "unavailable". That is acceptable for a company-wide screen. It would not be acceptable for a rule about money.

So: keys, models, limits, cache, screening, routing and cost go in the gateway. Consent, amounts, approvals, tool permissions and checks on tool results go in the harness. Our post [Every guardrail your agent needs, sorted](/writing/guardrails-sorted/) shows where each kind of check sits.

## Five mistakes we see often

1. **Keys in every app.** Each team holds a provider key. Nobody can rotate them all, revoke one person's access, or say who spent what. Put the provider keys in the gateway and give each app its own gateway key.
2. **No budget per team.** One looping agent uses the whole company's quota, and everyone else gets 429s. A spend limit per team key stops one runaway at the door. [Why your agent costs $4 per question](/writing/agent-cost-mistakes/) shows how fast a loop runs up a bill.
3. **Business rules in gateway policies.** "Block payouts over ₹40,000" written as a regular expression in a gateway policy. It can't see the tool call happen, it can't see the policy limit, and the next app inherits a rule that was never meant for it.
4. **A gateway with no fallback.** All the setup, and it still points every call at one provider. When that provider goes down, so does everything.
5. **A gateway that is a single point of failure.** Every app now depends on it. Run more than one copy, watch its health like any production service, and decide what happens when it is unreachable, because "every agent stops" should be a choice, not a surprise.

## Six questions to check your own setup

1. Can you list every place a provider key lives today?
2. If one team's agent loops all night, what stops it, and who finds out?
3. Which models are approved, and what happens when someone calls one that isn't?
4. If your main provider fails right now, which call goes to the backup, and has the backup passed your evaluations?
5. Can you show last month's model spend per team from one log?
6. Which of your gateway policies would make sense only for one app? Those belong in that app's harness.

Put the switch in front of every model, and keep the business rules behind it, in the agent that understands them.
