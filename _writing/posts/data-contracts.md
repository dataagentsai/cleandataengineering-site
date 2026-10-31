---
title: Data contracts: stop breaking the team downstream
date: 2026-10-31
subject: data
audience: builders
kind: explainer
draft: false
summary: Most data breakages start with an upstream change nobody announced. A data contract is a written agreement between the team that produces a dataset and the teams that use it, checked by a machine in three places. This post draws what a contract holds, where it is checked, and which changes break it.
linkedin: The app team renamed one column on a Tuesday. By Wednesday, the revenue dashboard said ₹0 and both loads said "success". A data contract would have stopped that change before it shipped. What a contract holds, where it is checked, and which changes break it, drawn simply.
deeper: /concepts/data-contracts/
deeper_label: data contracts, the key idea on one page
---

On a Tuesday, the app team ships a new version. In their order file, the column `amount` is now called `order_amount`. It's a tidy rename, and nobody thinks to tell the data team.

On Wednesday morning, Ananya opens the sales dashboard. Tuesday's revenue says ₹0. The nightly load ran, and it reported success. So did the one after it.

Nothing was broken in the pipeline. What broke was a promise that was never written down.

## A promise, written down

A **data contract** is a written agreement between the team that produces a dataset and the teams that use it. The producer promises what the data will look like and how it will behave. The consumers can then build on that promise without guessing.

{{drawing: dc-parcel}}

Think of a courier delivery. The parcel is the data. The signed note on top says what's inside, how it's packed, when it will arrive, and who to call if something is wrong. If the sender wants to change any of that, they tell you first, before the parcel turns up different.

A contract written once in a wiki is not enough. The useful kind is a file in version control that a machine checks on every change.

## What a contract holds

A contract answers the questions a consumer would otherwise have to ask on chat.

{{drawing: dc-card}}

1. **Schema.** The columns, their types, and which ones are required.
2. **Meaning.** What each column means in words. `amount` is the order value in rupees, including tax, before refunds.
3. **Quality rules.** `order_id` is unique. `amount` is never negative. `country` is a two-letter code.
4. **Freshness.** How late the data may be. "Yesterday's orders are in by 6 a.m."
5. **Owner.** A team, not a person, and how to reach them.
6. **Change policy.** How changes are announced, and how much notice consumers get.

You don't have to invent a format for this. The **Open Data Contract Standard** (ODCS) is an open standard for writing data contracts in YAML, maintained under the Linux Foundation's Bitol project. Whether you use it or a simpler file of your own, the point is the same: one file per dataset, kept next to the code, read by people and by machines.

## Three places it is checked

A contract nobody checks is a wish. It earns its keep when it is checked in three places, each catching a different kind of problem.

{{drawing: dc-checkpoints}}

1. **In the producer's CI**, before the change ships. CI is the automatic test run on every pull request. The app team's pull request that renames `amount` runs a check against the contract, and fails. The producer finds out at their desk, not the consumer at 9 a.m. This is the cheapest place to catch a break, and the one teams skip most.
2. **At ingestion**, on the bronze-to-silver hop. Bronze keeps what arrived, in the source's own shape. Before rows move into silver, the job compares what arrived with the contract. A missing required column stops the load. A row that breaks a quality rule goes to quarantine with the reason. This is the safety net for producers who don't run the CI check, such as an outside vendor's file.
3. **In monitoring**, after the data lands. Freshness and volume are promises about time and size, and you can only check them by watching. Did today's file arrive by 6 a.m.? Is the row count close to the usual?

The ingestion check is the same idea as the [quality rules in config](/writing/data-quality-as-config/). The contract is where those rules come from, and who agreed to them.

## The rename, replayed

The DataTwin Studio [Problem Lab](/learn/data-platform-sim/problems/) recorded this exact story on a real Spark and Delta Lake run. The numbers below are from that recorded run.

The source file for 27 October arrived with `order_amount` instead of `amount`, plus a new `coupon` column. The job read it with the old schema, found no `amount`, and filled it with nulls. Three rows had no amount, and 27 October revenue showed ₹0 instead of ₹1,990.

The naive fix was to let the schema evolve automatically. The load succeeded, silver grew two extra columns, and revenue still showed ₹0, because every report reads `amount`, not `order_amount`.

The right fix was a contract check before the write. The check saw that a required column was missing, stopped the load, wrote nothing, and alerted the source owner. A one-line mapping from `order_amount` to `amount` was added to the ingestion settings by a reviewed pull request. On the re-run, the check passed, the new `coupon` column was accepted, and 27 October showed ₹1,990.

## Breaking or safe?

The rename and the new coupon column arrived in the same file. One was a break, and the other was fine. Learning to tell them apart is most of the skill.

{{drawing: dc-sort}}

A change is **breaking** if a consumer who did nothing wrong would get a wrong answer or an error. Renaming a column, dropping one, changing its type, making an optional column required, or changing what a column means are all breaking. The last one is the sneakiest: `amount` that quietly starts excluding tax still passes every schema check.

A change is **safe** if every existing consumer keeps working without touching their code. Adding an optional column is safe. So is loosening a rule in a way no consumer relies on, though that one deserves a quick review.

That sorting gives you versioning:

- A safe change is a minor version, from 1.2 to 1.3. Ship it.
- A breaking change is a major version, from 1.3 to 2.0. Announce it, and run old and new side by side for an agreed notice period, so consumers can move when they are ready.

## How it fits with the rest

A contract is not a separate system. It plugs into two things you may already have.

- **Metadata-driven ingestion.** If you bring tables in with [one generic pipeline and a row of settings per table](/writing/metadata-driven-ingestion/), the contract sits alongside that row. The settings say how to load. The contract says what the loaded data must look like. The rename mapping in the story above was a settings change, triggered by a contract failure.
- **Data quality.** The quality rules in the contract are run by the same engine as every other rule, with the same quarantine and the same alert.

And in the medallion layers, the contract is checked where bronze becomes silver. That's why [bronze keeps everything as it came](/writing/medallion-done-right/): when the check stops a load, you have the original file to replay once the fix is in.

## What goes wrong

- **The contract lives in a wiki.** It was right on the day it was written. No machine reads it, so nobody notices when it drifts.
- **Only the consumer checks it.** The break is caught, but at ingestion, after the producer has shipped. Put the check in the producer's CI too.
- **Turning on automatic schema evolution and calling it done.** It is right for a new column. For a rename, it hides the break, as the recorded run shows.
- **Loosening a rule to make the job pass.** A rule that keeps failing at night gets quietly relaxed. The data is just as bad; only the alarm is off. Changes to a contract need the same review as any breaking change.
- **No named owner.** A contract signed by nobody is not a contract. Every dataset needs a team that answers the alert.
- **Contracts for everything on day one.** Start with the five datasets that break most often, and add more as they earn it.

## Five questions to check your own setup

1. For your most important dataset, could you show someone the contract file in under a minute?
2. If the source team renamed a column today, where would it be caught first: their CI, your ingestion, or a user?
3. Does a missing required column stop the load, or fill it with nulls?
4. Who gets the alert when freshness slips, and is that a team or one person on leave?
5. When did a contract last change, and who reviewed it?

The rename will happen again. A contract decides whether it fails one pull request or one morning of your users' trust.
