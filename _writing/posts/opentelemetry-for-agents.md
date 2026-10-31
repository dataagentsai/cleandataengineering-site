---
title: OpenTelemetry is here to stay: instrument your agent once, send traces anywhere
date: 2026-10-31
subject: ai
audience: builders
kind: decision
draft: false
summary: Almost everything in an agent stack changes every few months, but how you send traces out of it has settled: OpenTelemetry. Write your spans once with its library and its standard GenAI field names, put a Collector in between, and the backend becomes one line of config. The standard is settled; some GenAI field names are still moving, so keep them in one file.
linkedin: Models, frameworks and eval tools for agents change every quarter. One choice has stopped changing: OpenTelemetry. Our claims assistant moved its traces from a laptop to Azure Application Insights by changing one line of config, and not one line of agent code.
deeper: /learn/agent-harness/tech-l11.html
deeper_label: the observability layer of the Agent Harness, with what we chose and why
---

Pick any part of an agent stack and ask what you'd choose today. The model? It'll change by spring. The framework? There's a new one every month. The eval tool, the gateway, the vector store? All moving.

Now ask how your traces should leave the agent. That question has an answer, and it isn't going to change: **OpenTelemetry**.

This post is about that one settled bet. It is not about *what* to put in a trace; [tracing autonomous agents](/writing/tracing-agents/) covers that. This one is about the plumbing: the standard, the pipe, and why choosing the backend becomes a line of config instead of a rewrite.

## One plug, many sockets

{{drawing: otel-plug}}

Think of a travel adapter. You don't buy a new charger for every country you visit. You keep one charger and carry an adapter that fits any socket.

Agent tracing used to work the other way. Each vendor shipped its own library. You called it in your agent's code, wrote spans in its format, and used its field names. Moving to another vendor meant finding every one of those calls and rewriting it.

OpenTelemetry is the one plug. Your agent writes spans in one standard way, and every serious backend now has a socket that accepts them.

## What OpenTelemetry is, in plain words

**OpenTelemetry**, often shortened to OTel, is an open standard for three kinds of signal: **traces** (what happened, step by step), **metrics** (numbers counted over time) and **logs** (lines of text). It is run by the Cloud Native Computing Foundation, the same open body that looks after Kubernetes, and no single vendor owns it.

It has four parts you need to know.

1. **The SDK.** A library in your code, available for Python, Java, .NET, JavaScript and more. You open and close spans with it, and attach fields to them.
2. **The exporter.** A small piece inside the SDK that decides where finished spans go.
3. **OTLP**, the OpenTelemetry Protocol. This is the wire format: the agreed shape of the data as it travels, over HTTP or gRPC. Any backend that speaks OTLP can read any agent that writes it.
4. **The Collector.** A separate program that sits between your agent and the backends. It receives OTLP, batches it, retries when a backend is down, and sends copies wherever you tell it.

{{drawing: otel-pipeline}}

The reference agent behind our [Agent Harness tutorial](/learn/agent-harness/) runs exactly this. The agent sends OTLP to a Collector on the same machine. The Collector sends traces on to Langfuse and metrics to Prometheus. The agent knows nothing about either.

## Why put a Collector in the middle?

It's tempting to skip it. The SDK can send straight to a backend, so why run another program?

Our reference agent did skip it at first. Traces went straight from the agent to Langfuse. Then, on the first live run of its overnight monitoring job, Langfuse timed out on three batches, and two of seven turns never reached the backend, so they were never evaluated. The SDK's batch exporter doesn't have the queue and retries a Collector has. Ours now queues what a slow backend can't take yet and keeps retrying for up to ten minutes. It also counts what it sent and what it failed to send, so a loss shows up as a number instead of a silent gap.

The Collector is also where you do the things your agent shouldn't have to know about: send to two backends at once while you compare them, drop a field before it leaves your network, or sample only some traces for an expensive backend.

## The GenAI semantic conventions

A standard pipe is half the story. The other half is agreeing on what the fields are called.

OpenTelemetry publishes **semantic conventions**: standard names for common facts, so every backend knows where to look. HTTP calls have had these for years. The **GenAI conventions** do the same for model calls. These are the names our harness uses, copied from its `names.py` file and checked against OpenTelemetry's own Python package:

| Field | What it holds |
|---|---|
| `gen_ai.provider.name` | who served the call, such as a model provider |
| `gen_ai.operation.name` | what kind of call, such as a chat |
| `gen_ai.request.model` | the model you asked for |
| `gen_ai.response.model` | the model that actually answered |
| `gen_ai.usage.input_tokens` | tokens sent in |
| `gen_ai.usage.output_tokens` | tokens that came back |
| `gen_ai.tool.name` | the tool the model asked to call |

Two general names matter just as much: `session.id` for the conversation, and `user.id` for who was talking. Our harness uses these standard names on purpose. A backend that groups traces by session will do it with no setup, while our own `agent.tenant` field is understood by nothing.

## What's settled and what's still moving

Here is the honest part.

{{drawing: otel-settled}}

**Settled:** the SDK, the OTLP wire format, the Collector, and the core conventions for things like HTTP and service names. These are marked stable, and every major backend accepts them.

**Still moving:** the GenAI conventions. In OpenTelemetry's own Python package they sit in the module for conventions that are not yet stable, and the project calls their status "development". Names have already changed. `gen_ai.usage.prompt_tokens` became `gen_ai.usage.input_tokens`. `gen_ai.system` became `gen_ai.provider.name` in version 1.37.0. And the whole `gen_ai` family has since moved into its own repository, separate from the main conventions.

That isn't a reason to wait. It's a reason to be tidy:

1. Keep every field name in one file. Our harness keeps them all in `names.py`, so a rename is one line, not a search across the codebase.
2. During a rename, send both names for one release. Ours sends `gen_ai.system` and `gen_ai.provider.name` side by side, because a dashboard grouping by the old name would go dark the day the libraries around it updated.
3. Put your own fields under your own prefix, such as `agent.`, so nobody mistakes them for the standard. Cost, the prompt version and which check fired have no standard name yet, so ours are `agent.cost.usd`, `agent.config.fingerprint` and `agent.policy.blocked_by`.

## Switching backends: one line

{{drawing: otel-switch}}

The claims assistant in our tutorial is a motor insurer's chat assistant on Azure. It has three config files, one for tests, one for a laptop and one for Azure. The telemetry part of each is a single choice of adapter:

```
# config/local.yaml
telemetry:
  adapter: console

# config/azure.yaml
telemetry:
  adapter: azure-monitor-otel
  connection_string: {key_vault: appinsights-connection-string}
```

On a laptop, spans stay in memory, where tests can read them. On Azure, Microsoft's Azure Monitor OpenTelemetry distro, which is the OpenTelemetry SDK packaged with an exporter for Application Insights, sends the same spans to Application Insights. The span code, the field names and the tests are the same in both. The reference agent has a third adapter that sends OTLP to a Collector with Langfuse behind it. Same spans again.

The list of backends that accept OTLP keeps growing. Langfuse, Arize Phoenix, Datadog, Grafana and Azure Monitor all take OpenTelemetry data, either directly or through their own agent or distro. The details differ, such as which endpoint, which headers and whether there's a free tier, so check each one's own docs before you commit. But the agent side stays the same.

So the vendor question gets smaller. Pick the backend your team can afford and will actually open. If it disappoints you in six months, you change a config file, not your agent.

## Four mistakes we see often

1. **Vendor libraries sprinkled through the agent.** A tracing call from one vendor's library in every tool and every model call. It's quick on day one. On the day you switch, every one of them has to go. Write OpenTelemetry spans through one helper, and keep any vendor code inside the exporter or the Collector.
2. **No Collector.** Sending straight from the agent to a SaaS backend works until that backend is slow. Then spans are lost, and nothing tells you. That is exactly how our reference agent lost two of seven turns.
3. **Sending personal data to a SaaS backend.** Once a customer's Aadhaar number or phone number is in a span, it is in the vendor's storage, their backups and every export. Redact in the agent before anything is exported, and use the Collector as a second net. Better still, keep the words out of spans entirely unless a turn is chosen for capture.
4. **Making up names when a standard one exists.** `model`, `tokens_in`, `conversation`: each needs a mapping in every backend you ever use. `gen_ai.request.model`, `gen_ai.usage.input_tokens` and `session.id` need none.

## Five questions to check your own agent

1. If you had to move to a different tracing backend next week, how many files would you change?
2. Do your model-call spans use `gen_ai.*` names, or names you invented?
3. Are all your field names in one file, so a rename in the standard is a one-line change?
4. Is there a Collector, or anything with a queue and retries, between your agent and your backend?
5. Could you send the same traces to two backends at once, to compare them, without a code change?

Everything else in the stack will keep moving. Make this the one part you only have to build once.
