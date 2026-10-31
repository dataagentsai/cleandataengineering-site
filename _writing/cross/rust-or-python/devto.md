---
title: Rust or Python for agents? Probably both
published: false
canonical_url: https://cleandataengineering.ai/writing/rust-or-python/
description: Python wins for the thinking parts of an agent: orchestration, prompts, evals and fast iteration, with the whole AI library ecosystem behind it. Rust wins for the heavy lifting: sandboxes, gateways on the hot path, and tools shipped as one small binary. The model call usually dominates latency, so Rust helps only where the model is not involved.
---

*Originally published at [cleandataengineering.ai](https://cleandataengineering.ai/writing/rust-or-python/).*


Every few weeks the same argument starts in an agent team. One engineer says Python is slow and the agent should be rewritten in Rust. Another says nobody on the team knows Rust and the agent works fine. Both are partly right, which is why the argument never ends.

The way out is to stop asking it about the whole agent. An agent is not one program. As we argued in [the model is 10%](/writing/model-is-ten-percent/), most of it is ordinary software: a loop, some tools, checks, traces, a sandbox, maybe a gateway. Each of those parts has its own answer.

For most teams, the answer comes out the same way: **Python for the thinking, Rust for the heavy lifting.**

## The brain and the arm

**Rust** is a systems programming language. It compiles to a fast native program, like C does, but the compiler refuses code that could misuse memory. **Python** is the language most AI work is already written in: slower to run, much faster to write and change.

{{drawing: rust-brain-arm}}

Think of the brain and the arm. The brain decides what to do next, changes its mind often, and talks to many other people. The arm lifts the same heavy thing thousands of times a day, and must never slip. You would not ask your arm to plan the week, and you would not lift the sofa with your head.

## Where Python wins

Python is the brain of the agent, for five plain reasons.

1. **The AI library ecosystem.** The model providers' official software development kits, the eval libraries, the data tools and the vector store clients all arrive in Python first, and often only there.
2. **Evals and notebooks.** An eval is a test of how well the agent does its job. Most eval work happens in a notebook: load a hundred conversations, score them, look at the bad ones, change the prompt, run again. That loop lives in Python.
3. **Fast iteration.** Prompts, tool descriptions and orchestration logic change every week. In Python a change is one edit and one run, with no compile step.
4. **Most agent frameworks.** The popular agent frameworks are Python first, with TypeScript next. Rust options exist but are young.
5. **The team you can hire.** In Bengaluru or Pune you can hire ten good Python engineers this month. Finding one who has shipped Rust in production takes longer.

## Where Rust wins

Rust is the arm. It earns its place in the parts that run all the time, touch untrusted input, or must be shipped to someone else's machine.

1. **Sandboxes and code-execution runtimes.** When an agent writes code and runs it, the runner must hold that code in a cage it cannot get out of. Firecracker, the small virtual machine behind AWS Lambda, is written in Rust, and so is Wasmtime, a popular WebAssembly runtime.
2. **Gateways and proxies on the hot path.** The **hot path** is code that every single request passes through. A gateway that checks keys, counts tokens and routes calls for every agent in the company runs on it.
3. **Tool runtimes and CLIs shipped as one small binary.** A Rust program compiles to one file. Your user downloads it and runs it, with no Python version to install and no virtual environment to break.
4. **Speed and low memory.** A Rust service often handles the same traffic with a fraction of the memory and far less waiting, which matters when you pay for every container.
5. **Memory safety without a garbage collector.** A **garbage collector** is the part of a language that cleans up unused memory while the program runs, and it can pause the program to do so. Rust has none, yet the compiler still prevents the classic memory bugs that make C code unsafe. For a sandbox, that is the whole point.

## One agent, two languages

Put a real agent on the page and colour each part by language.

{{drawing: rust-one-agent}}

The orchestration loop, the prompts and the evals stay in Python, because they change every week and need the AI libraries. The sandbox, the gateway and the parser for big files go to Rust, because they run on every request, touch untrusted input, or chew through a lot of bytes.

Notice the model sits outside both. It is somebody else's server, and it is almost always the slowest thing in the picture. Say a turn takes 3 seconds: around 2.9 of those are the model thinking. Rewriting the Python loop in Rust might save a few milliseconds out of the remaining hundred. The user will not notice. **Rust helps where the model is not involved.**

## You already use Rust from Python

If you write Python today, you are very likely already running Rust without knowing it.

{{drawing: rust-crate}}

- **uv**, the fast Python package installer, is written in Rust.
- **Ruff**, the linter and formatter, is written in Rust.
- **Pydantic** version 2 does its validation in `pydantic-core`, which is Rust.
- **Polars**, the DataFrame library, is Rust inside.
- **Hugging Face tokenizers**, which split text into tokens, is Rust inside.

Every one of them has a Python face and a Rust engine. That is the split this post recommends, already proven by tools millions of people install every day.

## How the two meet

There are three common ways to join a Python brain to a Rust arm.

1. **PyO3 bindings.** PyO3 is a Rust library that lets you write a Python module in Rust. You `import` it like any other package. This is how Polars and `pydantic-core` work. Use it for a fast function called many times inside one process, such as a parser.
2. **A separate service over HTTP or gRPC.** The Rust part runs as its own small server, and Python calls it over the network. **gRPC** is a way of calling functions on another server with a strict, typed contract. Use this for a gateway or a sandbox, which should live in their own process anyway.
3. **MCP.** The Model Context Protocol is a standard way for an agent to find and call tools. A tool server written in Rust looks exactly like one written in Python to the agent. We covered it in [MCP is here to stay](/writing/mcp-here-to-stay/).

All three are the same idea as a port and adapter: the Python side codes to an interface and does not care what language sits behind it. So you can start with a Python sandbox runner today and swap in a Rust one later, without touching the loop.

## Three questions for each part

When someone proposes Rust for a part of the agent, ask three questions in order.

{{drawing: rust-three-questions}}

1. **Is it on the hot path, away from the model?** If every request waits on it, and the model is not the slow part, speed matters. If it waits on the model anyway, it does not.
2. **Does it run untrusted code or input?** Code the model wrote, files a stranger uploaded, a page fetched from the web. Here memory safety is worth a lot.
3. **Does the team know Rust, or will it learn?** If the answer is no, use a ready-made Rust tool rather than writing your own.

A part that gets "no" to the first two stays in Python. A part that gets "yes" to either, and "yes" to the third, is a good candidate for Rust.

## What goes wrong

**Rewriting the whole agent in Rust for speed.** The model call is the slow part. Months later the agent is no faster, the prompts are harder to change, and the eval notebooks no longer talk to the agent code.

**Python in a latency-critical proxy.** The opposite mistake. A gateway every agent in the company goes through, written as a quick Python script, becomes the thing that falls over on the busiest day. This is a good place for a ready-made proxy, or Rust.

**Writing your own sandbox in either language.** A cage for untrusted code is hard to build safely. Adopt a proven one before you write one.

**Choosing by hype.** "Rust is fast" and "Python is what AI uses" are both slogans. Measure where the time actually goes, with a trace of one real turn, before you choose.

## Five questions to check your own agent

1. In a trace of one turn, how much time is the model, and how much is your code?
2. Which parts run on every request, and which run once a day?
3. Where does untrusted code or input enter, and what holds it?
4. Is each Rust or Python part behind an interface, so you could swap the language later?
5. Who on the team would fix the Rust part at 2 a.m.?

Let Python do the thinking, let Rust do the lifting, and let a trace, not a slogan, tell you which is which.

