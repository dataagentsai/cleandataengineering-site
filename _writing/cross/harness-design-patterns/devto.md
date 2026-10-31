---
title: Swap anything, break nothing: software design patterns for agent harnesses
published: false
canonical_url: https://cleandataengineering.ai/writing/harness-design-patterns/
description: Everything around an agent changes every few months: the model, the gateway, the trace backend, the cloud. A handful of old software design patterns keep those changes small. Put each vendor behind a port, pick the adapter in one YAML file, line up the checks so any one can stop a call, wrap calls in retries and traces, and make every adapter pass the same contract tests.
---

*Originally published at [cleandataengineering.ai](https://cleandataengineering.ai/writing/harness-design-patterns/).*


Here is a week in the life of an agent team. On Monday the model you chose gets a cheaper sibling. On Wednesday the company says everything must run on Azure. On Friday someone wants traces in a different tool. None of these is a big idea. Each should take an afternoon.

In most agent code, each one takes a fortnight. The vendor's library is called in the loop, in the tools, in the checks and in the tests. An `if env == "azure"` sits in nine places. A swap becomes a hunt.

The fix is old. A **design pattern** is a named, well-tested shape for code, and a few of them solved "swap the part, keep the machine" decades ago. This post walks through six of them, using the open-source [reference agent](https://github.com/dataagentsai/reference-agent), a customer-support agent for a clothing shop, as the example.

## Sockets and plugs

The first pattern has two names that mean nearly the same thing: **code to an interface**, and **ports and adapters**.

A **port** is a socket in the wall. It says what shape a part must have, and nothing about who made it. An **adapter** is a plug: one vendor's product, shaped to fit that socket. Your harness only ever touches the socket.

{{drawing: pat-socket}}

In the reference agent, the model port is one small interface. Every model call in the agent goes through this one method:

```python
class LLMClient(Protocol):
    async def complete(self, request: ModelRequest) -> ModelResponse: ...
```

Four adapters fit it today: `scripted` (canned answers, no network, for tests), `litellm-proxy` (the open-source gateway), `groq-direct` (straight to Groq from a laptop) and `apim-ai-gateway` (Azure's gateway). The loop has no idea which one it holds.

The agent has ten ports like this, from `secrets` and `telemetry` to `state`, `identity` and `approval`. The telemetry port is a good one to study: the loop writes OpenTelemetry spans and never learns where they go. We wrote about that in [instrument your agent once, send traces anywhere](/writing/opentelemetry-for-agents/).

The rule that makes this real: **each vendor library is imported by exactly one adapter module**. The reference agent doesn't trust people to remember this. An import check runs with the tests, and it says, in effect, "nothing may import `openai`, `anthropic` or `groq` except the `llm` module". It fails closed, so a new module inherits the ban without anyone adding it.

## One file picks the plugs

The other half of the first pattern is **inversion of control**. Normally a piece of code chooses its own parts: the loop would create a Groq client itself. Inverted, the loop is *handed* a model client and never chooses. Something else does the choosing, in one place, called the **composition root**.

In the reference agent, the composition root reads YAML. Each port names an adapter:

```yaml
model:     { adapter: litellm-proxy }
state:     { adapter: postgres }
identity:  { adapter: keycloak }
telemetry: { adapter: otel-to-langfuse }
```

Moving to Azure is a different YAML file, not different code. Here is what the open-source stack and the Azure stack each bind:

| Port | Open-source stack | Azure stack |
|---|---|---|
| model | litellm-proxy | apim-ai-gateway |
| state | postgres | azure-postgresql-flexible |
| identity | keycloak | entra-id |
| telemetry | otel-to-langfuse | azure-monitor-otel |
| approval | temporal-updates | dbos-workflows |
| secrets | environment-settings | key-vault |

Notice the state row: both stacks run PostgreSQL, one on a laptop and one managed by Azure. That choice is argued in [just use Postgres](/writing/just-use-postgres/).

Startup refuses a YAML file that names an unknown adapter or writes a secret as a plain value. A wrong file stops the agent before the first customer, not during their conversation.

The same idea works for checks. The companion eval harness has an `evaluators.yaml` where each check names its adapter: groundedness from Azure AI Evaluation, faithfulness from Ragas, tool correctness from DeepEval, personal data from Presidio. Four vendors, one result format, one file.

## A fixed recipe with swappable slots

The second and third patterns work together inside a turn.

**Template method**, or pipeline, means the steps and their order are fixed, and only what happens inside a step can vary. Every turn of the agent runs the same recipe.

**Strategy** means one slot, several interchangeable ways to fill it, chosen while the program runs.

{{drawing: pat-turn}}

The reference agent's first step is a strategy. A small router reads each message and picks a path: answer directly without a model, refuse, hand to a person, or run the full loop. "Get me a human" never costs a model call. The same slot idea fits model choice: say, a small cheap model to sort the question and a stronger one to write the reply, each named in configuration.

The loop itself is the template. Its description is plain: open the tool surface, take steps until one ends the run, and stop on the step budget if none does. The reference agent even lets a framework own the loop, behind the same function signature, so the recipe stays put while the cook changes.

## Security gates for every call

The fourth pattern is **chain of responsibility**: a line of handlers, each looking at the same request, where any one can stop it.

{{drawing: pat-gates}}

Think of airport security. You pass the gates in order, and any gate can turn you back. In the harness, checks sit at four points of a turn: before the model, after the model, before a tool and after a tool. (Where they sit, and why, is the heart of [the model is 10%](/writing/model-is-ten-percent/).)

At each point the reference agent runs its rules in order, and the first block wins. Two details matter more than they look:

1. **A rule that crashes blocks.** If the check for "did the customer ask for this refund?" throws an error, the refund doesn't run. The other choice, log and let it through, gives you a guard everyone believes in and nobody has.
2. **A rule that runs out of time blocks too.** A point can have a time budget, and a rule still running when it is spent counts as a no.

## Russian dolls around a call

The fifth pattern is the **decorator**: wrap an object in another object with the same shape, which adds one job and then passes the call inward.

{{drawing: pat-dolls}}

The reference agent wraps every network model adapter in `ResilientLLM`. It has the same `complete` method as the client inside it, so the loop can't tell it's there. It waits out a rate limit for exactly as long as the provider asks, retries real failures a few times with growing pauses, and stops calling a provider that is clearly down. It never retries an answer it couldn't read, because the same prompt to the same model would mostly buy a second bill.

Order matters, and it is easy to get wrong:

- **Trace outermost**, so you see every try, including cache hits.
- **Cache next**, so a hit skips everything below it.
- **Retry outside the timeout**, so each try gets its own clock.

One warning: retrying a write is only safe if something underneath stops it happening twice. In the reference agent, a ledger of request keys at the tool boundary does that job. Without one, a retry is how a timeout becomes a double refund.

## The same exam for every adapter

The last pattern is the one that makes all the others safe: **contract tests per port**. Each port has one table of test rows, and every adapter for that port must pass every row.

{{drawing: pat-exam}}

The model port's table has rows like "a text answer comes back typed, with its usage" and "a tool call comes back with parsed arguments". All four model adapters run the same rows, with the vendor's web traffic answered inside the test, so there is no network and no cost. The identity, secrets, telemetry, approval and records ports each have their own table. A new adapter joins by being registered, and is then held to the rows the others pass. You can see the tables drawn in [contract tests: every plug fits its socket](/learn/agent-harness/test-contract.html).

## What goes wrong

- **Vendor calls sprinkled through the loop.** The vendor's library is imported in the loop, in a tool and in a check. Every swap becomes a search, and you'll miss one.
- **If-branches on environment.** `if env == "azure"` in nine places means nine places to get wrong, and the branch you don't run locally is the one that breaks. Pick adapters in one file instead.
- **Interfaces shaped like one vendor's API.** If your model port takes that vendor's message objects, it isn't a port, it's a copy. Write the port in your own words, such as `ModelRequest` and `ModelResponse`, and let each adapter translate.
- **No contract tests.** The swap passes review and the agent starts, but the new adapter drops the token count. Nothing crashes; the cost meter just reads zero until someone notices.

## Five questions to check your own harness

1. How many files import your model vendor's library? Is the answer one?
2. Can you switch cloud by changing a configuration file and nothing else?
3. If one check crashes, does the call it was checking stop or go through?
4. Where are retries, timeouts and traces added: in one wrapper, or in every caller?
5. If you add a new adapter tomorrow, which tests must it pass before it ships?

Vendors will keep changing; build the harness so a change is a new plug, not a new house.

