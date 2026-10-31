---
title: Build only the gaps: AgentTwin assembled from open-source tools
date: 2026-10-31
subject: ai
audience: builders
kind: decision
draft: false
summary: AgentTwin is an assembler. Where a proven open-source tool already does a job, it plugs that tool in behind a port and builds nothing. It builds only four things no tool did: the world description format, the stand-ins that project that world into the agent's systems, the judges that read the world's state, and the switch between pretend and real. Of 38 tools we looked at, 12 are in use, 6 were turned down, and every decision has a written reason.
linkedin: We looked at 38 open-source tools for testing AI agents. 12 are in use today, 6 were turned down, and the rest wait for a reason. What we built ourselves fits in four boxes. Here is the rule we used: check if it exists, put it behind a port, and name the gap or don't build it.
deeper: /learn/agenttwin/open-source/
deeper_label: all 38 tools, one card each, with the reason for every decision
---

When you start building a tool, the tempting first step is a blank folder and a big plan. You will write your own test runner, your own fake customers, your own attack library, your own clock. It feels like progress for about a month.

Then you notice that every one of those already exists, written by people who spent years on it, and yours is the worst version.

**AgentTwin** puts a real AI agent in a pretend world and checks what changed in that world (the [first post](/writing/agenttwin-flight-simulator/) explains it). This post is about how it was put together. It is an **assembler**: it uses open-source tools for every job they already do well, and builds only the pieces nobody had built.

## Buy most bricks, make a few

{{drawing: asm-lego}}

Think of a Lego model. You buy almost every brick from the shop: they are cheap, they fit, and they never wobble. For the one odd shape your model needs and no set sells, you make a custom brick at home.

A good build is mostly shop bricks. A bad build is a home-made brick for every part, each one a little lopsided.

For AgentTwin, the shop is open source. We looked at 38 tools that do some part of testing an agent: running tests, inventing edge values, playing a customer, writing attacks, faking data, moving the clock, injecting faults. Then we asked of each one: does it do a job we need, and does it do it well enough?

## The four pieces nothing else did

Four jobs had no tool. These are AgentTwin's own.

1. **The world format.** A file that describes the agent's world: its users, systems and data, rules, faults and time. The loader refuses a world that could not exist, such as an order that shipped before it was placed. [Describe the world, not the test](/writing/describe-the-world/) covers it.
2. **The stand-ins.** We call this the *projection*: turning the world file into pretend systems the agent can call. A stand-in holds state and refuses what the real system would refuse. A canned mock that says "OK" to everything can't do this.
3. **The four judges.** They read the world's state after a run, not the chat. Only a judge that reads state can say *a refund was owed and never issued*. Nothing changed, nothing false was said, and a judge reading the transcript would pass it.
4. **The mode switch.** The same scenario runs in one of four modes: against the stand-in (mock), against recorded real answers (replay), against a real system (real), or against both at once to see where they differ (shadow).

Everything else is adopted.

## The core in the middle, tools on ports

{{drawing: asm-assembly}}

A **port** is a socket in the code: a small, fixed interface that says what a job needs, such as "give me the customer's next message". An **adapter** is the plug that connects one tool to that socket. The pattern is explained in [Swap anything, break nothing](/writing/harness-design-patterns/).

AgentTwin has one hard constraint: **the format and the engine never import an adopted tool.** The reason, written in its code, is that a simulator that imported one tool would only ever simulate one stack. So each tool sits behind a port, with its adapter outside the core.

That is what lets a team on Azure swap the open-source customer simulator for Microsoft's managed one. Two of the 38 tools are exactly this: Azure versions of a job an open-source tool already fills, behind the same port.

The ports also keep weight out. LangWatch Scenario, the library that plays the customer, pulls in about 380 MB of dependencies and pins older versions of some shared libraries. Because it sits behind a port in its own optional install, nobody who doesn't use it carries any of that.

## The decision rule: three questions

{{drawing: asm-rule}}

Before building anything, we ask three questions in order.

1. **Does it exist?** Check first, before designing. A search costs minutes. A build costs weeks.
2. **Is it good enough, behind a port?** It doesn't have to be perfect. It has to do the job, and you have to be able to unplug it later.
3. **What exactly is the gap?** Name what the existing tool doesn't do, and why it can't be extended to do it. If you can't name the gap in one sentence, don't build.

The third question usually shrinks the build a lot. Take choosing scenarios. A small library called allpairspy picks a short list of test combinations that still covers every pair of values, for example every customer type meeting every fault. It works, but for the clothing-shop agent it left 187 of 468 possible pairs uncovered. The gap was not "write a scenario picker". It was "fill in the missing pairs". So allpairspy stays, and a small piece of our own code tops it up.

## In or out, and why

{{drawing: asm-baskets}}

Of the 38 tools, here is where each one landed as of 30 October 2026:

| Decision | Tools | Means |
|---|---|---|
| In use | 12 | plugged in and working today |
| Opt in next | 7 | chosen, not plugged in yet |
| Evaluate | 6 | must prove itself first |
| Later | 5 | right tool, not needed yet |
| Cloud binding | 2 | the Azure version, behind the same port |
| Opt out | 6 | turned down, for the reason given |

A few of the reasons, because the reasons are the useful part.

**In.** *pytest* runs every scenario, because a second test runner would split the evidence across two reports. *Hypothesis* invents hundreds of odd inputs to break a rule, and was already a dependency. *PyRIT*, Microsoft's red-teaming toolkit, rewrites one attack many ways; 180 generated attack cases held on both reference agents. *time-machine* moves the clock forward so "30 days later" takes a second.

**In, but only part of it.** From LangWatch Scenario we use only the simulated customer, not its judge, because AgentTwin judges by state, not by words. From PyRIT we use only the fixed, free rewrites; its model-driven parts need a paid model. *AgentDojo*, a research set of prompt-injection attacks, is copied in as data, because installing the package would pull in five model vendors' libraries.

**Out.** *WireMock* and *Prism* return canned answers; a canned mock would cancel a shipped order and the test would pass while proving nothing. *garak* probes the model, not the agent around it, and AgentTwin's question is whether harm reached the world. *DeepTeam* overlaps *promptfoo*, and one red-team generator is enough. *GraphWalker* walks every path through a state diagram; we use its idea, but a Java tool for one algorithm was too heavy.

Turned down is not the same as wrong. Each one is a good tool for a different question.

## Mistakes we made, or nearly made

1. **Planning a whole framework.** Early plans listed parts to build: a clock, a population of customers, a fault injector. Each one already existed. Starting from "what do we build?" instead of "what exists?" nearly cost weeks.
2. **Adopting a tool without a port.** Import a tool straight into your core and it decides your dependency versions, your cloud and your upgrade schedule. The day you need to swap it, the swap is a rewrite.
3. **Taking the whole tool when you need one part.** LangWatch Scenario's judge reads the conversation. Had we taken it along with the customer, we would have two judges that disagree, and the wrong one would be easier to read.
4. **No record of why a tool was turned down.** Six months later someone suggests WireMock again, and the team argues it from scratch. AgentTwin keeps an adoption file, ADOPTION.md, where every row has a verdict and a reason, including the rejections.
5. **Calling a tool adopted before it is plugged in.** At one design check, most of the tools listed as "adopted" were still only planned. Keep "in use" and "chosen" as separate labels, and be honest about which is which.

## Six questions to check your own build-vs-adopt choices

1. For the last thing you built, did you search for an existing tool before you designed it?
2. Can you name, in one sentence, the gap each home-made piece fills?
3. Could you swap any adopted tool in an afternoon, or is it imported all through your code?
4. When you adopt a tool, do you take only the part you need?
5. Is there a written reason for every tool you turned down, where the next person will find it?
6. Do your labels tell apart a tool that is working today from one you merely chose?

Buy the bricks the shop sells, and save your hands for the shapes it doesn't.
