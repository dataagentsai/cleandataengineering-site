---
title: Unity Catalog done right: one governance model for data and AI
published: false
canonical_url: https://cleandataengineering.ai/writing/unity-catalog-done-right/
description: Unity Catalog is the one place on Databricks that says where every table, model and agent tool lives, who may use it, and where it came from. Done right, that means a simple three-part layout, grants to groups set high up the tree, masks and filters on the table itself, and descriptions good enough for people and AI assistants to read. This post draws each part and lists the mistakes that undo it.
---

*Originally published at [cleandataengineering.ai](https://cleandataengineering.ai/writing/unity-catalog-done-right/).*


A new analyst joins on Monday. By Wednesday she still can't see the sales tables, because access was granted to eleven people by name and nobody remembers which ones. On Thursday someone finally gives her admin "for now". She can now see every customer's phone number.

Nobody did anything wicked. There was simply no model for who may see what, so every request became a favour.

Unity Catalog is Databricks' answer to that problem: one catalog for tables, files, models and agent tools, with one way of granting access, one record of lineage and one place for descriptions. This post explains it simply and shows the setup that keeps it clean.

## A library with a librarian

The easiest way to picture Unity Catalog is a library.

{{drawing: uc-library}}

Every object has an address in three parts, written `catalog.schema.object`:

1. **Catalog** is the building. It is the top-level container, usually one per environment or per business area.
2. **Schema** is a bookcase inside it. It groups related objects, such as everything in the gold layer.
3. **Object** is a book: a table, a view, a volume (a folder of files such as CSVs or PDFs), a function, or a machine learning model.

The librarian is the permission check. Before you take a book, the librarian looks at your card and asks whether your group has been allowed into that building, that bookcase and that book. Every tool on the platform, from a notebook to a dashboard to a chat window, goes through the same librarian.

## A layout you can live with

The three levels are only useful if you decide what each one means and stick to it.

{{drawing: uc-layout}}

The most common sensible layout is:

- **One catalog per environment:** `dev`, `test` and `prod`. A job running in test can only touch the test catalog, so a bad deployment can't overwrite production. Catalogs can also be bound to particular workspaces, so the dev workspace can't even see `prod`.
- **One schema per medallion layer:** `bronze`, `silver`, `gold`. The full name `prod.gold.daily_sales` then tells you both where a table lives and how far it has travelled. If the layers themselves are new to you, [Bronze, Silver, Gold, and where most teams get it wrong](/writing/medallion-done-right/) explains them.

Larger companies often swap this around: one catalog per domain (`sales`, `finance`, `hr`) and one schema per data product, with environments kept in separate workspaces or a prefix such as `sales_dev`. Either works. What matters is that the rule is written down and that nobody has to guess where a new table goes.

## Grant to groups, high up the tree

Permissions in Unity Catalog are granted on an object and flow down to everything inside it.

{{drawing: uc-grants-flow}}

Grant `SELECT` on the schema `prod.gold` to the group `finance_analysts`, and every table in that schema is readable by that group. That includes tables created next month. Two small extra grants, `USE CATALOG` and `USE SCHEMA`, let the group open the building and the bookcase.

Three habits keep grants sane:

1. **Grant to groups, never to people.** When Priya joins finance, she is added to the group in your identity provider, and she sees what finance sees. When she moves team, she is removed, and her access goes with her. Nobody edits a grant.
2. **Grant as high up as makes sense.** One grant on a schema beats forty grants on forty tables. Drop to table level only for the odd exception.
3. **Give every object an owning group, not an owning person.** The owner can change grants. If that owner is a person who has left, nobody can.

The same applies to programs. A pipeline should run as a service principal (an identity for a program rather than a person) that may read bronze and write silver, and nothing else.

## Masks and filters for sensitive data

Some columns, such as phone numbers, PAN numbers or salaries, should be visible to a few people and hidden from everyone else. Some rows should be visible only to the team they belong to. Unity Catalog handles both on the table itself.

{{drawing: uc-masks}}

- A **column mask** is a small SQL function attached to a column. It decides, for each reader, whether to return the real value or a hidden one such as `*****`.
- A **row filter** is a SQL function attached to the table. It decides which rows each reader may see, for example only the rows for their own state.

Both functions usually check group membership, so the rule reads like "show the phone if the reader is in `support`". Because the rule sits on the table, it applies everywhere: SQL, notebooks, dashboards and Genie all get the same masked answer. You don't need a separate "safe" copy of the table for each audience, which is the copy that always goes stale.

## Lineage you don't have to draw

When a job reads one table and writes another, Unity Catalog records it. You get lineage at table and column level without writing anything extra, and you can see it in the catalog explorer or query it from system tables.

That turns two painful questions into a click. Where did this number come from? Follow the lineage upstream to the source. What breaks if I drop this column? Follow it downstream and see the two gold tables and the dashboard that use it. No slide of boxes that goes out of date the week after.

## Descriptions and tags: written for people and for AI

A table called `cust_v2_final` with no description is useless to the next person. It is worse than useless to an AI assistant, which will guess what it means and answer confidently.

Every table and every important column should have a plain-language description, such as "one row per customer, refreshed daily at 6 am, owned by the CRM team". Databricks can draft these for you with AI, but a person should read and correct them.

Tags add labels you can search and act on, such as `pii = phone`, `domain = sales` or `tier = gold`. Search finds tables by tag, reviewers can list every column tagged as personal data, and Databricks' assistants and Genie read the descriptions to pick the right table. Good descriptions are now part of how your AI answers questions correctly.

## Govern AI assets too

The part most teams miss is that Unity Catalog is not only for tables.

{{drawing: uc-one-roof}}

- **Models** are registered in the catalog, such as `prod.ml.churn_model`, with versions and aliases. The same grants decide who may deploy or call them, and lineage links a model to the tables it was trained on.
- **Functions** stored in the catalog can be handed to an agent as tools. The agent can only call the functions it has been granted, and each call runs under the catalog's permissions, masks included.
- **Metric views** hold the one agreed definition of numbers like net revenue, so dashboards and chat give the same answer. [Talk to your data the right way](/writing/genie-metric-views/) shows how they work with Genie.

The point is one roof. An analyst, a dashboard and an agent all come in through the same door and meet the same rules. An agent that holds its own storage key and reads files directly has stepped around every grant, mask and audit record you built.

## Five mistakes we see most

### 1. Grants to individual users

It starts as one quick favour and ends as hundreds of grants nobody can review. Access never leaves when people do. **Grant to groups.**

### 2. One giant catalog for everything

Dev tables, test copies and production all sit in `main`. A test job overwrites a production table, and nobody can grant "all of production" in one line. **Split catalogs by environment or by domain.**

### 3. No descriptions or tags

People ask in chat which table is the real one, and AI assistants pick the wrong one. **Describe every table and key column, and tag personal data.**

### 4. Sensitive columns left unmasked

The phone column is "only in silver" and "only analysts use silver". Then someone builds a dashboard on it. **Put the mask on the column, not on a promise.**

### 5. AI tools that bypass the catalog

An agent gets a storage key or an admin token because setting up grants felt slow. It now sees everything, and nothing it reads appears in lineage. **Give agents a service principal, catalog functions as tools, and the same grants as everyone else.**

## Seven questions to check your own setup

1. Can you say, in one sentence, what a catalog and a schema mean in your platform?
2. How many grants go to named people rather than groups?
3. Who owns each production schema: a group or a person who might leave?
4. Could a job running in dev write to a production table?
5. Which columns hold personal data, and are they tagged and masked?
6. Does every gold table have a description a new joiner would understand?
7. Does any agent, notebook or tool read data without going through the catalog?

If any answer makes you pause, start there. A catalog doesn't govern anything by existing; the layout, the groups and the descriptions do.

