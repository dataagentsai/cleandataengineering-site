---
title: Describe the world, not the test
date: 2026-10-31
subject: ai
audience: builders
kind: explainer
draft: false
summary: Writing hundreds of test scripts for an agent doesn't scale, because every new rule or fault means editing scripts by hand. Instead, write down the agent's world once: its users, systems and data, rules, faults, approvers and time. Scenarios are then generated from that description, including combinations nobody would have thought to script. This post shows what a good world description holds, with a small example, and says honestly what AgentTwin's format does today.
linkedin: Your agent has 200 test scripts. Then the rules change, or a new kind of failure shows up, and someone has to remember which scripts to edit. There's a better unit of work: describe the agent's world once, and generate the scenarios from it. Here is what that description holds.
deeper: /learn/agenttwin/
deeper_label: AgentTwin, explained, with a step-through simulator
---

A team builds a support agent for a lending library. They write a test for each thing that can happen: renew a book, renew a late book, ask about someone else's book, the system times out. Soon there are, say, 200 scripts.

Then the library changes the renewal limit from 7 days late to 14. Someone has to find every script that assumed 7. Next month the team learns that the system sometimes drops a reply after doing the work. Someone has to work out which of the 200 scripts could meet a dropped reply, and write new ones. Nobody remembers them all.

The fix is to change what you write. Don't write the tests. Write down the agent's **world** once, and let the tests come from it. This is how the world format in AgentTwin works, and this post explains it. If you're new to AgentTwin, start with [what it is](/writing/agenttwin-flight-simulator/).

## A map, not a list of directions

{{drawing: awd-map}}

A test script is a list of directions. "Leave Asha's house, turn left at the bank, ask for The Hobbit, expect it renewed." It works for one trip, on a day when nothing goes wrong.

A world description is the map. It shows the houses, the roads, the library, the bank, and also the storm that can roll in and the clerk who might be on leave. From a map you can plan any trip, including ones nobody planned before. When a new road opens, you change the map once and every route can use it.

## What a world description holds

{{drawing: awd-six-parts}}

A good world description has six parts.

1. **Users.** Who talks to the agent and what they want. Asha wants to renew a book. Just as important is *how* they behave, because agents fail on behaviour, not mood. AgentTwin keeps a small catalogue of these behaviours, called **personas**: `plain`, `forgets-the-identifier`, `impatient`, `two-things-at-once`, `second-language` and `does-not-believe-it`.
2. **Systems and their data.** The tools the agent can call, and the rows those systems hold at the start: two members and three loans. Each row is there to test a rule: one loan inside the renewal limit, one outside it, one that belongs to someone else.
3. **Rules.** What may change and when, and what is *owed*: if Asha asks and the rule allows it, a renewal must happen. The rules come from the agent's own spec, which is the written list of its tools and the rule behind each one. The world points to that spec and is not allowed to restate it.
4. **Faults.** Things that go wrong that are nobody's fault: a slow system, a lost reply, a stale read, the model provider being down.
5. **Approvers.** The people who must say yes to risky actions. They can say yes, say no, never answer, or say yes twice.
6. **Time.** How much time passes between turns, and events that happen at set hours whoever is talking, such as an overnight job that marks loans returned.

The rule in part 3 matters more than it looks. Before AgentTwin had it, the return window of its shop agent lived in the world file, and a second world was made by copying the first. The copies drifted apart. When each rule is written down once, there is nothing to drift from.

## A small example

Here is a trimmed world for the library agent. It is a sketch, cut down to show the shape, but the field names are the real ones from the format, which is called AWD (Agent World Description).

```yaml
# A sketch, trimmed. The renewal rule is NOT here: it lives in the agent's spec.
apiVersion: awd/v0
name: library
seed: 7
spec: {aoas: library-agent, version: 0.1.0, path: library.aoas.yaml}
fidelity:
  faithful_about:
    - loan.status, and how many days late each loan is
  not_faithful_about:
    - book descriptions, fines and opening hours
  verified_against: null      # not yet checked against a real system
systems:
  loans:
    projects: loan_system
    resolution: mock
    presents:
      renew:
        description: Renew a loan. Open loans only, at most 7 days late.
        refusal: a loan {late} days late cannot be renewed
records:
  member:
    - {id: M-1, name: Asha}
    - {id: M-2, name: Ravi}
  loan:
    - {id: L-1, member: M-1, book: The Hobbit, status: open, late: 2}
    - {id: L-2, member: M-1, book: Dune, status: open, late: 9}
    - {id: L-3, member: M-2, book: Emma, status: open, late: 0}
calendar:
  - id: overnight-sync-marks-emma-returned
    at: 10h
    by: loans
    entity: loan
    where: [{field: id, equals: [L-3]}]
    sets: {status: returned}
    record_only: true          # the record changes; the book did not come back
```

A few things are worth noticing.

- **`fidelity`** says what the world is accurate about and, more usefully, what it isn't. A test about renewals needs loan status exactly right. It doesn't need real book blurbs.
- **`resolution`** says how each system is played: `mock`, `replay`, `real` or `shadow`. Shadow means calling the real system and the stand-in side by side and comparing them.
- **`record_only`** is how you make a record lie. The system says Emma is back; she isn't. An agent that repeats the record as fact fails. One that says "the system shows it as returned" passes.

The faults, the approver's behaviour and the persona are chosen in each scenario from the fixed lists above, for example `perturbations: [{kind: lost_reply, tool: renew}]` and `approver: {decides: never}`.

## From one world to many scenarios

{{drawing: awd-fan-out}}

Once the world is written down, scenarios can be generated from it. AgentTwin does this in three ways today.

1. **The edges of each rule.** A rule like "at most 7 days late" carries its own boundaries. The `scaffold` command reads the spec and writes rows at every state, at each limit and one past it, so 7 and 8 days late, plus a starter scenario for each tool and each refusal. Run against the shop agent's own spec, it wrote 17 scenarios, and all 17 passed.
2. **Pairs of everything.** The `coverage` command treats four things as dimensions: what the customer wants, what state their record is in, which persona they are, and which fault happens. It checks that every value of one has met every value of the others in at least one scenario. `scaffold --pairwise` then writes skeletons for the pairs nobody has. This is where you find a customer who forgets their loan number, asking about a loan that is already returned, while the reply gets lost. Nobody writes that test by hand.
3. **Attacks.** A `generate` block in a scenario turns one planted-instruction test into many cases, drawn from open-source attack libraries, each judged by what changed in the world.

The skeletons are honest drafts. They name the right tools, records and edges, and leave the customer's exact words as `TODO` for a person to fill in. The world knows what to vary. It doesn't know how Asha talks.

## Change the world, not 200 scripts

{{drawing: awd-change}}

This is why a world scales better than a pile of scripts. Scripts grow by multiplication: every new fault times every existing situation is a new script someone has to imagine. A world grows by addition: you add the fault once, and the coverage check lists the pairs that are now missing.

The same goes for rules. Change the renewal limit in the spec from 7 to 14, and the generated edges move to 14 and 15 without anyone editing a test record. A second shop, with slightly different rules, is a small file that extends the first spec instead of a copy of everything. AgentTwin's electronics version of its shop agent is 70 lines; the earlier copy was 131.

The world also refuses nonsense. The loader rejects a row that breaks a stated rule, such as a returned book that is still overdue. When those checks arrived, the shop agent's set of fixed test cases went from 29 to 26: three of them described situations that could never happen.

## What is built, and what is not

**Built.** The world format and a loader that refuses impossible data. Rows, systems, fidelity and the calendar in the world file. Scaffold, coverage and pairwise skeletons. Generated attacks. Personas, faults (slow, lost reply, stale read, provider down and a few more), approvers that grant, refuse, never answer or grant twice, and time that moves between turns.

**Not built, or not yet in the world file.** Personas and fault kinds are fixed lists in AgentTwin's code, chosen per scenario; you can't yet declare a new one in a world file. Shadow mode is designed but not built, so every world today honestly says `verified_against: null`. And a world is small and clean: real data with volume, skew and odd old rows is out of reach. The `not_faithful_about` list is how a world admits that, not a fix for it.

## What goes wrong

1. **Restating the rules in the world.** Then you have two copies of the return window, and one day they disagree. Point to the spec instead.
2. **Rows in the middle of each rule.** A loan 3 days late tells you little. 7 and 8 tell you whether the limit is right.
3. **Pretending the world is perfect.** A world with an empty `not_faithful_about` list is claiming more than it can know.
4. **Trusting skeletons as tests.** A generated skeleton with `TODO` words proves nothing until someone writes how the customer speaks and runs it.
5. **Faults that land at random.** A fault on a different call each run gives failures nobody can reproduce. AgentTwin puts each fault on a named call, such as the first call to `renew`.

## Five questions to check your own testing

1. If a rule changed tomorrow, how many test files would you have to edit?
2. Is each rule written down in exactly one place your tests read from?
3. Do your test records sit exactly on each limit and one past it?
4. Can you list which pairs of situation and fault your tests have never tried?
5. Does your test setup say, in writing, what it is *not* accurate about?

For how these scenarios play out against a real agent, see [what happened when one met a real customer](/writing/agent-met-real-customer/).

Write the map once, and let the routes come from it.
