---
title: Delta, Iceberg, or both? Open table formats are settled
date: 2026-10-31
subject: data
audience: builders
kind: decision
draft: false
summary: An open table format is Parquet files plus a log that turns a folder into a real table, with transactions, time travel, schema changes and safe concurrent writes. The move to open formats has settled. Delta Lake and Apache Iceberg do the same job with different bookkeeping, and today you can often keep one copy of the data and let readers of both kinds use it.
linkedin: Teams still lose weeks arguing Delta versus Iceberg. The bigger decision was made years ago: tables live in open files that any engine can read. Here is what a table format really does, recorded from a real Delta run, how the two compare, and how to stop choosing a side.
deeper: /learn/data-platform-sim/delta/
deeper_label: Delta Lake internals, recorded step by step from a real run
---

Every few months a data team holds the same meeting. Someone has read that Iceberg is winning. Someone else points out that the whole platform runs on Delta. A third person mentions Hudi. An hour later nothing is decided, and the tables stay exactly where they were.

The meeting is arguing about the smaller question. The big one was settled years ago: your tables should live as open files in your own storage, readable by more than one engine, and not locked inside one vendor's database.

This post is part of our series on what has settled, after [building agents on a moving ship](/writing/moving-ship/). It explains what a table format actually does, using numbers recorded from a real Delta Lake run, then compares Delta and Iceberg, and shows how to read both without picking a side.

## Loose pages and a binder

A data lake starts as a folder of Parquet files. Parquet is a column-based file format: compact, fast to scan, and readable by almost every engine. But a folder of Parquet files is a pile of loose pages. Nothing says which pages belong to today's table, which were half-written by a job that crashed, or which were replaced last week.

{{drawing: otf-binder}}

An **open table format** puts those pages in a binder with a table of contents. The pages are still ordinary Parquet files. The table of contents is a log, or a set of metadata files, sitting next to them. It lists exactly which files make up the table at each version. A reader opens the table of contents first and reads only the pages it names.

That is the whole trick. Delta Lake, Apache Iceberg and Apache Hudi are three ways of keeping that table of contents. Our concept page on [open table formats](/concepts/table-formats/) has the short version.

## What the log adds

Once there is a table of contents, four things become possible that a plain folder could never do safely.

{{drawing: otf-badges}}

1. **Transactions.** A write either fully happens or doesn't happen at all. In our recorded Delta run (Spark 3.5.1 with Delta Lake 3.2.0, on a laptop), an insert first wrote two Parquet files, one per Spark task, and only then wrote commit 1 naming them. Until that commit file existed, nobody could see the rows. A job that crashes halfway leaves files no commit names, and readers never see them.
2. **Time travel.** Old files are not deleted when rows change; the log simply stops listing them. In the recording, reading version 1 meant replaying only commits 0 and 1, and yesterday's table came back exactly, including a row that had since been deleted.
3. **Schema changes.** The log records the table's columns. Adding a column is a new entry in the log, not a rewrite of every file.
4. **Safe concurrent writers.** Two writers race to create the next commit file, and only one can win. In the recording, two writers that both appended rows both succeeded: the loser checked that the winner had only added rows and took the next version number. Two writers that updated the same row did not: the second failed with a `ConcurrentAppendException` instead of silently overwriting the first.

These four are why a cheap lake can be trusted like a warehouse, and why the [medallion layers](/writing/medallion-done-right/) can be rebuilt with confidence.

## Why this has settled

Three things make open table formats a plank, not a crate.

- **Every major platform ships one.** Databricks and Microsoft Fabric's OneLake store Delta. AWS offers Iceberg in S3 Tables, and Google Cloud offers Iceberg through BigLake. Snowflake reads and writes Iceberg tables.
- **Your data stays yours.** The files sit in your storage in an open format. If you change engines, you point the new engine at the same files instead of exporting everything.
- **Many engines, one table.** Spark, Trino, Flink, DuckDB and the cloud warehouses can all read at least one of these formats, and usually both.

No serious new platform today asks you to load your data into a closed format first. That is what "settled" means.

## Delta and Iceberg: same idea, different bookkeeping

Delta and Iceberg solve the same problem. The difference is where the table of contents lives and who keeps it.

{{drawing: otf-bookkeeping}}

**Delta Lake** keeps a folder called `_delta_log` next to the data. Each commit is a numbered JSON file listing the files added and removed. Replaying hundreds of JSON files would be slow, so every 10 commits Delta writes a checkpoint, one Parquet file holding the whole state, and readers start from there. A commit happens when a new numbered file is created, and creating it is all-or-nothing.

**Apache Iceberg** keeps a tree of metadata files: a table metadata file, which points to a list of manifests, which point to the data files. A **catalog**, a small service that knows where each table's current metadata file is, holds a pointer to the latest one. A commit happens when the catalog swaps that pointer.

| | Delta Lake | Apache Iceberg |
|---|---|---|
| Table of contents | numbered commits in `_delta_log` | metadata tree, pointer held by a catalog |
| Strongest with | Spark and Databricks, Microsoft Fabric | many engines at once: Trino, Flink, Snowflake, AWS, Google Cloud |
| Known for | deep Spark integration, change data feed, deletion vectors | hidden partitioning, changing the partition scheme without rewriting data |
| Clean-up jobs | `OPTIMIZE` and `VACUUM` | rewriting data files, expiring snapshots |

The honest summary: if most of your work runs on Databricks or Fabric, Delta is the natural home. If many engines from many vendors need to write the same tables, Iceberg's catalog-centred design was built for that. The two keep borrowing each other's best ideas, so the feature gap narrows every year.

## Reading both without picking a side

The newer answer to "Delta or Iceberg?" is often "write one, let both kinds of reader in". The goal is **one copy of the data, two kinds of readers**.

{{drawing: otf-read-both}}

- **Delta UniForm.** UniForm, short for Universal Format, is a Delta table setting. When it is on, Delta writes Iceberg metadata alongside its own log for the same Parquet files. Iceberg readers see an Iceberg table; nothing is copied.
- **Iceberg REST catalogs.** The Iceberg project defines a standard REST interface for catalogs. Any engine that speaks it can find and read tables from any catalog that serves it, without a custom connector per vendor.
- **Unity Catalog serving Iceberg clients.** Databricks' Unity Catalog can act as an Iceberg REST catalog, so engines outside Databricks can read Delta tables that have UniForm switched on, as Iceberg.

There are also tools that translate metadata between formats after the fact. Whatever you use, the test is simple: is there one set of Parquet files, with one owner who writes them? If yes, adding a reader is configuration, not a new pipeline.

## Hudi, briefly

Apache Hudi came out of Uber and is the third open format. It is strongest at heavy upserts and incremental pulls, meaning "give me only the rows that changed since my last read", and it offers both copy-on-write and merge-on-read tables. It has a loyal following on streaming-heavy platforms. For most new projects the choice is Delta or Iceberg, but a working Hudi platform is no reason to migrate.

## Mistakes we see often

1. **Choosing a format by hype.** The right format is the one your main engines write best. Follow your platform, not the conference talk.
2. **Never running OPTIMIZE or VACUUM.** Every small write adds small files, and old files stay on disk for time travel. In our recording, 300 small files made a one-customer query take 777 ms; after `OPTIMIZE` compacted them into one file, the same query took 278 ms. The 300 old files stayed on disk until `VACUUM` removed them. Our [Databricks cost leaks](/writing/databricks-cost-leaks/) post covers small files in more depth.
3. **Letting VACUUM break time travel.** `VACUUM` deletes files no current version needs, once they are older than the retention period, 7 days by default. In the recording, retention was forced to 0 hours, which Delta refuses until a safety check is switched off. Afterwards the log still listed version 4, but reading it failed with a "file does not exist" error. Retention is how far back you can travel. Set it on purpose.
4. **Two copies of the data to serve two engines.** A nightly job that copies Delta tables into Iceberg doubles storage, adds a lag, and creates two truths that drift apart. Use UniForm or a shared catalog instead.
5. **Hand-rolled Parquet folders.** Writing plain Parquet and building your own locking and clean-up recreates a table format, badly.

## Six questions to check your own setup

1. Which format do your main write engines handle best, and is that the one you use?
2. Is any table copied into a second format just so another engine can read it?
3. When did `OPTIMIZE` or compaction last run on your busiest table?
4. What is your `VACUUM` or snapshot retention, and does it match how far back people need to travel?
5. If two jobs write the same table at once, do you know what happens?
6. Could a new engine read your tables tomorrow through a catalog, without a new pipeline?

Pick the format your platform writes best, keep one copy, and let the readers come to it.
