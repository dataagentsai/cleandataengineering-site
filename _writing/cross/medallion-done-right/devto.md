---
title: Bronze, Silver, Gold, and where most teams get it wrong
published: false
canonical_url: https://cleandataengineering.ai/writing/medallion-done-right/
description: Almost every lakehouse says it uses the medallion architecture. Fewer use it well. The layers aren't folders; each one is a promise about the data inside it. This post draws the layers as a kitchen, then shows the seven mistakes we see most and the one test that prevents them.
---

*Originally published at [cleandataengineering.ai](https://cleandataengineering.ai/writing/medallion-done-right/).*


Ask ten data teams whether they use the medallion architecture and nine will say yes. They have a bronze schema, a silver schema and a gold schema. Then ask why two dashboards show two different revenue numbers, and the room goes quiet.

The layers were created. The promises behind them were not kept.

## The layers as a kitchen

The easiest way to see what each layer is for is to walk through a kitchen.

{{drawing: kitchen}}

- **Landing** is the delivery bag. Files exactly as they arrived: CSV, JSON, API pages. Nobody touches them.
- **Bronze** is the store room. Every row ever received, in the source's own shape, plus a note of when and where it came from. Nothing is cleaned or thrown away.
- **Silver** is the prep counter. One clean row per real thing: one per order, one per customer. Types fixed, duplicates removed, codes standardised.
- **Gold** is the dish. Tables cooked for one use: a sales star schema, a feature table for a model, a data product for another team.
- **Semantic** is the menu. One name and one definition for every number people quote, such as *net revenue*, so every dashboard and every chatbot gives the same answer.

You never cook straight from the delivery bag. And because the store room keeps everything, you can always go back and cook again.

## Data moves one way

The whole architecture rests on one rule.

{{drawing: spine-readers}}

Each layer is built **only from the layer before it**. Silver is built from bronze, gold from silver, never the other way around. Readers start at gold or semantic. Nobody reads bronze, not even an analyst in a hurry.

That one rule is what lets you rebuild any layer from the one below it when a bug is found.

## Seven mistakes we see most

### 1. Cleaning in bronze

Someone adds "just a small fix" to the bronze load: a date parse, a filter on test rows. Now bronze no longer holds what arrived. When the fix turns out to be wrong, there is nothing left to rebuild from. **Bronze keeps everything, as it came.**

### 2. Business rules in silver

Silver starts to say "active customers only" or "revenue excluding refunds". Those are choices for one use. The next team that needs all customers has to go back to bronze. **Silver cleans; it doesn't decide.**

### 3. Dashboards reading silver, or bronze

It's quicker, until the silver table changes shape and twelve reports break overnight. **Readers start at gold or semantic.** Those layers are the published contract; the layers below may change.

### 4. Dropping bad rows silently

A row fails a check, and a `WHERE` clause quietly removes it. Totals stop matching the source and nobody can say why.

{{drawing: quarantine}}

**Bad rows go to quarantine with the reason.** Someone fixes the rule or the source, and the rows are replayed. Nothing disappears.

### 5. One gold table per dashboard

Every new report gets its own gold table, each with its own copy of "revenue". After a year there are forty of them and six definitions. **Gold is shaped by use, not by chart.** The definition of a number lives once, in the semantic layer.

### 6. No semantic layer at all

Without it, every dashboard tool and every AI assistant writes its own SQL for the same number. That is where the "two revenues" meeting comes from. On Databricks this is a metric view. Elsewhere it might be dbt's semantic layer or Cube. Whichever you use, **one definition, used everywhere.**

### 7. Quality checks added at the end

Checks get bolted on after the first bad week, and only on gold. By then bad rows have travelled through every layer. **Checks belong on every hop**, declared once with the pipeline, switched on from day one.

## The one test that prevents them

Nearly every mistake above is a step sitting in the wrong layer. When you write a new transformation, ask four questions in order.

{{drawing: layer-test}}

1. Does it keep the data exactly as it came? It belongs in **bronze**.
2. Does it clean one real thing, in a way that's right for every use? **Silver**.
3. Does it shape data for one particular use? **Gold**.
4. Does it define a number that people quote? **Semantic**.

If a step doesn't fit cleanly, it's usually two steps. Split it.

## A few things the medallion doesn't do

- **It isn't a data model.** Gold still needs real modelling, such as facts and dimensions. The medallion tells you *where* that goes, not *how* to do it.
- **More layers don't help.** "Platinum" and "diamond" layers usually mean gold has lost its definition. Fix the definition instead.
- **The names don't matter.** Raw, cleaned, curated works just as well, as long as each layer keeps its promise.

## Check your own lakehouse

1. Could you rebuild silver from bronze tomorrow if you had to?
2. Does any dashboard read from silver or bronze?
3. Where do rows that fail a check go?
4. How many tables define "revenue"?
5. Are your quality checks on every layer, or only the last one?

If any answer surprises you, start there. The layers are cheap to create. The promises are what make them worth having.

