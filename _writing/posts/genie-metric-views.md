---
title: Talk to your data the right way: Genie and metric views on Databricks
date: 2026-10-31
subject: analytics
audience: builders
kind: explainer
draft: false
summary: A chat window over your data is easy to build and easy to get wrong. The model should not write SQL against your tables; it should pick from numbers you have already defined. On Databricks that means metric views in Unity Catalog as the one definition, with AI/BI Genie and your dashboards both reading from them.
linkedin: Your dashboard says ₹4.2 crore. Your new chatbot says ₹5.1 crore. The chatbot is not broken; it just wrote its own meaning of "revenue". The fix is not a better model. It is one definition, shared by chat and dashboards, drawn simply.
deeper: /concepts/semantic-layer/
deeper_label: the semantic layer, explained simply
---

Someone in finance types "what was net revenue last quarter?" into the new chat window. A number comes back in four seconds. It looks right. It is not the number on the finance dashboard.

Nobody can say which one is wrong, so both stop being trusted. And it will not be the dashboard people stop using.

The chat interface was never the hard part. The hard part is that a language model writing SQL against real tables is wrong in ways the person asking cannot see. This post shows the architecture that fixes it on Databricks, and what to set up before anyone types a question.

## Why the numbers disagree

Picture a retailer with stores across India. Three tools answer "revenue last quarter".

{{drawing: genie-two-revenues}}

The finance dashboard subtracts refunds. The sales dashboard doesn't. The chatbot looked at the tables, saw a column called `amount`, and summed it, perhaps with a join that counted some orders twice.

Each tool wrote its own SQL, so each carries its own idea of what "revenue" means. Two dashboards that disagree is an old problem. A chatbot makes it worse, because it writes fresh SQL for every question, and it never says "I'm not sure".

This is not about model size. Public text-to-SQL tests built on real enterprise databases, with hundreds of columns, near-duplicate names and joins nobody wrote down, are exactly where models invent relationships. dbt reports roughly 40% accuracy for raw SQL against plain tables, against 83% when the model goes through a semantic layer. The scaffolding matters more than the model.

## The one idea: the model chooses, it does not construct

Here is the rule the rest of the post follows.

> The model does not write SQL against your tables. It picks a defined metric, a few dimensions and a filter from a menu you published. The formula and the joins are already fixed.

A **metric** is a number people quote, such as net revenue. A **dimension** is something you slice it by, such as state or month. A **semantic layer** is the place where each metric is defined once, with its formula, its joins and its filters, so every tool that asks gets the same answer.

If the model picks the right metric, the join and the arithmetic are right by construction. That is the difference between making wrong answers less likely and making a whole class of them impossible.

## The layers on Databricks

On Databricks, the semantic layer is a **metric view**: an object in Unity Catalog, Databricks' catalog for tables and permissions, that declares measures, dimensions and joins over your tables.

{{drawing: genie-layers}}

Read it from the bottom up.

1. **Gold tables** hold trusted data in a dimensional shape: fact tables such as orders, dimension tables such as store and date. Keep facts at the finest grain anyone will slice by, one row per order line, not monthly totals. A pre-summed table can only answer the questions someone thought of.
2. **Metric views** sit on gold. Each one names its measures, like *net revenue is the sum of amount minus the sum of refunds*, its dimensions, and how the tables join.
3. **Readers** sit on top. A Genie space, AI/BI dashboards, SQL editors and notebooks all query the same metric view.

A trimmed sketch of a metric view definition looks like this:

```
source: main.gold.fact_order_lines
dimensions:
  - name: state
    expr: store_state
measures:
  - name: net_revenue
    expr: SUM(amount) - SUM(refund_amount)
```

And anyone, person or model, asks for it like this:

```
SELECT state, MEASURE(net_revenue)
FROM main.semantic.sales_metrics
GROUP BY state
```

This matches our [medallion post](/writing/medallion-done-right/): readers start at gold or semantic. Genie is just another reader, and it should start at the semantic layer.

On Databricks, don't bring a second semantic tool alongside metric views. Genie and the dashboards read metric views directly. A metric defined somewhere else is a second definition that Genie cannot see.

## What happens to one question

Here is a single question on its way through.

{{drawing: genie-one-question}}

1. **The question.** Priya in finance asks for net revenue by state, last quarter.
2. **Genie picks.** It matches "net revenue" to the measure, "by state" to the dimension, and "last quarter" to a date filter. This is a choice from a short list, not free writing.
3. **A small query.** Genie still writes a query, but a tiny one over the metric view. It names the measure; it does not write the formula or the joins.
4. **The answer.** Priya sees the table and can open the SQL behind it. The measure's definition is there to check.

If the answer is wrong, that question becomes a test case. More on that below.

## Setting up a Genie space properly

A **Genie space** is where you choose which data Genie can use and how it should talk about it. The space is the product. Four things go into it.

- **The data.** Add your metric views, and only the gold tables you truly need. Fewer, cleaner assets give better answers than a whole schema.
- **Instructions.** Plain text that teaches your words and rules: "a quarter means the Indian financial year quarter, starting in April", "sales means net revenue unless someone says gross", "status 3 means cancelled".
- **Example SQL queries.** Questions you have answered correctly before, with the SQL that answers them. Genie learns from these, and some can be saved as trusted assets, so an answer built from one is marked as trusted.
- **Benchmarks.** A set of test questions, each with an answer you have checked by hand. Run them after every change to the space or the metric views and watch the score.

Ten questions you have actually checked beat a hundred you assume are fine.

## Mistakes we see

### 1. Pointing Genie at silver tables

It feels faster. But silver isn't shaped for questions, and business rules end up in the chat instead of in tested tables. **Genie reads metric views, plus gold when it must.**

### 2. Dumping the whole schema into one space

Two hundred tables "so it can answer anything". Every extra table is something the model might pick by mistake. **One space per team or topic, with a handful of assets.**

### 3. No example questions

Without examples, Genie has to guess what your people mean by "sales" or "this quarter". **Write the twenty questions people really ask, with the SQL that answers them.**

### 4. No benchmarks before launch

Then quality is opinion, and the first wrong number is found by a director. **Agree the accuracy you need, write the test questions, then launch.**

### 5. Chat and dashboards on different definitions

If the dashboard reads a gold table and Genie reads a metric view, they will drift. **Both read the same metric view.** Build the dashboard first; it proves the definitions with a more forgiving audience.

### 6. Permissions in the instructions

"Don't show salary data" in the instructions is a request, not a control. **Access is enforced in Unity Catalog by who is asking**, never by the prompt.

### 7. Metrics nobody owns

Definitions drift. **Every measure has a named owner**, and stale ones are removed rather than left lying around.

## Before you open the doors

{{drawing: genie-checklist}}

Write the metrics first: the twenty questions people will ask, as metric, slices and grain. Build gold to serve them. That order sounds backwards, but the finest slice any metric needs decides the grain of your fact tables, and finding that out later means rebuilding gold.

When the space can't answer something, a clear "I don't have a definition for churn" is better than a guess. Each of those becomes a backlog item: a metric to define, not a prompt to tweak.

## Five questions to check your own setup

1. If you ask Genie and your main dashboard for the same number, do they match to the rupee?
2. Does your Genie space read metric views, or raw tables?
3. How many questions with hand-checked answers do you test against, and when did they last run?
4. Who owns the definition of your most-quoted metric?
5. When Genie gets something wrong, where does that question go?

Get one definition right, and chat and dashboards agree for free.
