---
title: Stop writing pipelines: one metadata-driven ingestion framework for 500 tables
published: false
canonical_url: https://cleandataengineering.ai/writing/metadata-driven-ingestion/
description: Most teams bring data in with one hand-written pipeline per source table, and by table 500 nobody can keep them all working. A metadata-driven framework keeps one row of settings per table in a config store and runs one generic pipeline that reads it. Adding table 501 becomes a reviewed row, not new code.
---

*Originally published at [cleandataengineering.ai](https://cleandataengineering.ai/writing/metadata-driven-ingestion/).*


Priya joins a data team and is asked to bring in one more table from the shop database. She opens the repository and finds 212 pipelines, one per table. Most are copies of each other with small changes. Some load everything every night, some only new rows. Three of them handle a renamed column in three different ways, and one has a database password pasted into it.

She copies the closest one, changes the table name, and adds pipeline 213. It works. It is also one more thing someone has to fix when the source changes.

There is a better way, and it is not a new tool. It is a habit: **describe each table, don't code it.**

## 500 pipelines, or one engine and a table

{{drawing: ingest-many-vs-one}}

On the left is the usual path. Every table gets its own pipeline. Each one is small, but together they are hundreds of slightly different programs, each with its own bugs.

On the right is the metadata-driven path. The settings for every table live in a **metadata store**: a small database whose only job is to describe the platform. One generic pipeline, the **engine**, reads a table's settings and loads it. The engine is written once, tested once, and fixed once.

"Metadata" here just means data about data: where a table lives and how to load it, rather than the rows themselves.

The engine only does ingestion. It copies data from the source into **bronze**, the layer that keeps every row exactly as it arrived plus a note of when and where it came from. Cleaning is silver's job, later.

## What one config row holds

{{drawing: ingest-config-row}}

For each table, the metadata store answers eight questions.

1. **Source.** Which system it comes from, such as the shop's Postgres database, an SFTP folder or a REST API.
2. **Format.** How the data arrives: a database table, CSV, JSON, Parquet.
3. **Load type.** One of three. A *full load* copies the whole table every run, which is fine for small reference tables. An *incremental* load copies only rows changed since last time, using a column such as `updated_at`. *Change data capture*, or CDC, reads the database's own change log, so it sees every insert, update and delete in order.
4. **Keys.** The column or columns that identify a row, such as `order_id`. Silver will need these to remove duplicates.
5. **Schedule.** How often it runs: every hour, every night at 2 a.m.
6. **Watermark column.** For incremental loads, the column that says how far we got.
7. **Schema.** The columns and types we expect, so a surprise can be spotted.
8. **Connection.** A *reference* to a secret, such as `kv://shop-db-readonly`, never the password itself.

Two details make this work at scale.

First, settings come in three tiers: platform defaults, then source settings, then table settings. A table setting beats a source setting, which beats a platform default. So you set "incremental" once for the whole shop database and override it only for the one table that needs CDC.

Second, the **watermark value** itself, the actual "we loaded up to 9 a.m. yesterday", does not live in the config. Config says what *should* happen. A separate state table records what *did* happen. Mixing them means a settings change can quietly rewrite history.

People don't type these rows into the database by hand. They write a short YAML file per source and change it through a pull request. A loader then writes it into the store.

```
source: shop_db
type: postgres
config:
  ingestion.connection_ref: kv://shop-db-readonly
  ingestion.mode: incremental
datasets:
  - name: orders
    config:
      ingestion.watermark_column: updated_at
      silver.key: order_id
  - name: customers
    config:
      ingestion.mode: cdc
      silver.key: customer_id
```

## One run, step by step

Here is what the engine does when the scheduler says "load orders now".

{{drawing: ingest-one-run}}

1. **Read the config.** Merge platform, source and table settings into one set, and take a short fingerprint of it, so you can later prove which settings this run used.
2. **Check the watermark.** Read from the state table how far the last good run reached, say `2026-10-26 09:00`.
3. **Extract.** Ask the source for rows where `updated_at` is later than that.
4. **Land the files.** Write them, untouched, to a landing folder for this batch, such as `landing/shop_db/orders/batch=b-0912/`. Write a completion marker last, so nobody reads half a batch.
5. **Write to bronze.** Append the files to the bronze table in one commit, adding columns for when the row arrived, which source it came from and its **batch id**. Before appending, check whether this batch id already succeeded. If it did, stop: a retried job adds nothing.
6. **Update the watermark.** Only now move it forward, to the latest `updated_at` in the batch.
7. **Log the run.** Record the status, row counts, batch id and the settings fingerprint in the run log.

The order matters. If the job dies after step 5, the watermark hasn't moved, the batch check stops a double append, and the next run picks up cleanly.

The same engine handles all three load types. A full load simply skips the watermark steps. A CDC load reads change events instead of querying by date. The load type is a setting, not a different pipeline.

## Adding table 501

{{drawing: ingest-new-table}}

When someone needs a new table, they:

1. add a few lines of YAML for it,
2. open a pull request, where a teammate reviews it,
3. let the validator check it: every key must be a known key, every value the right type, the connection a secret reference, the load type one of the allowed three,
4. merge, and the loader writes it into the metadata store.

The next scheduled run picks it up. No new pipeline, no new deployment of code. Git keeps the history of every change, and the store is what the engine reads at run time.

## What goes wrong

### Config with no validation

A typo like `ingestion.mod: incremental` is accepted silently, so the engine falls back to the default and starts full-loading a table with a billion rows. **Check every key against a registry of known keys, types and allowed values before anything reaches the store.** Reject what you don't recognise.

### Secrets in the config

Someone puts the password in the YAML "just for now". Now it is in git history forever and readable by everyone with access to the repository. **Config holds a reference to a secret store**, such as Key Vault, Secrets Manager or Databricks secrets. The validator should refuse anything that looks like a password.

### No run log

A number changed last month and someone asks why. The settings have been edited three times since. Without a run log you can only guess. **Every run writes one row**: status, counts, batch id, and the fingerprint and full copy of the settings it used.

### Watermark updated before the write succeeds

The engine moves the watermark forward, then the bronze write fails. The next run starts from the new watermark, and those rows are gone for good. Nobody notices until a monthly total doesn't match. **The watermark moves last**, only after bronze has committed and the run is logged as successful.

### One giant generic notebook nobody can test

"Generic" turns into one 3,000-line notebook full of `if source_type == ...` branches. Nobody dares change it, so people start copying it, and you are back to 500 pipelines. **Keep the engine small and split into parts**: a mover that gets data into landing (this part can be a tool such as Data Factory, Lakeflow Connect or dlt), and your own lander that writes bronze the same way every time. Give each part tests that run without a real source.

## Six questions to check your own setup

1. How many lines of code does it take to add a new table today?
2. If someone mistypes a setting, what stops it?
3. Can you find a password anywhere in your config or its git history?
4. For last Tuesday's load of your biggest table, can you say which settings it ran with and how many rows it brought in?
5. If a job dies halfway through, does the next run lose rows, double them, or neither?
6. Could a new joiner read your engine and its tests in an afternoon?

Write the engine once, then let each new table be a row someone can review.

