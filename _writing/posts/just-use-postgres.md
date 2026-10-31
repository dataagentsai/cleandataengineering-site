---
title: Just use Postgres: the one database your agent needs
date: 2026-10-31
subject: ai
audience: builders
kind: decision
draft: false
summary: An agent needs to remember a lot of different things: the conversation, what it already did, what is waiting for a person, and what it decided. One PostgreSQL database can hold all of it, which means one thing to secure, back up and pay for. Move a job out only when you see a clear sign that it has outgrown Postgres.
linkedin: Your agent probably doesn't need Redis, a vector database, a queue, a workflow engine and a log store. It needs one PostgreSQL database with a few well-named tables. Here is the claims assistant's whole memory, table by table, and the three signs that tell you when to move something out.
deeper: /learn/agent-harness/state-tables.html
deeper_label: the tables in the Agent Harness tutorial, one by one
---

Draw the architecture of a typical agent and count the databases. There is Redis for the conversation, a vector database for memory, a queue, a workflow engine with its own store, a log store for the audit trail, and the app's own database. Six things to secure, back up, monitor and pay for, before the agent has answered one question.

Now look at what each of them actually holds. A few thousand rows of conversation. Some approvals waiting for a person. A list of tool calls already made. That is not six databases' worth of work. It is a few tables.

As [The model is 10%](/writing/model-is-ten-percent/) argues, most of a working agent is the ordinary software around the model, and much of that software is remembering things carefully. Our claims assistant keeps everything that matters in one PostgreSQL server. This post shows what goes in it, and the honest signs that something has outgrown it.

## One database, many jobs

{{drawing: pg-toolbox}}

PostgreSQL (Postgres for short) is a relational database that has been around for more than thirty years. It is not exciting, and that is the point. It has transactions, which means several writes either all happen or none do, plus row locks, JSON columns, and extensions such as vector search.

An agent needs seven kinds of memory, and Postgres can hold every one:

1. **Conversation state and checkpoints.** A checkpoint is the conversation saved at the end of a turn, so the next turn can pick up where the last one stopped.
2. **Memory with search by meaning.** The pgvector extension stores *embeddings*, lists of numbers that capture what a piece of text means, and finds the nearest ones. So "my car was hit" can find a note about a "rear-end collision".
3. **Durable workflows.** A durable workflow is a function whose progress is saved after every step, so it can wait for days and survive a restart. DBOS, a small Python library, keeps all its workflow state in Postgres tables.
4. **Queues.** A table of jobs, plus `SELECT ... FOR UPDATE SKIP LOCKED`, lets many workers each take a different job without stepping on each other. A worker skips rows another worker has already locked.
5. **The idempotency and delivery ledger.** *Idempotent* means doing it twice has the same effect as doing it once. The ledger is a table that records each write before it runs, so a retry gets the first answer instead of a second payout.
6. **Approvals.** A row for each action waiting for a person, with who decided and when.
7. **The audit log.** An append-only table, one that is only ever added to, of who did what and why.

## Six stores, or one

{{drawing: pg-before-after}}

Each extra store looks free on the day you add it. The bill arrives later, in four ways.

- **Security.** Every store needs its own logins, network rules, encryption keys and access reviews. Every one is a place where customer data can leak.
- **Backups.** Six stores means six backup schedules that are never quite in step. Restore them after an incident and the conversation says a payout is waiting, while the workflow engine says it was paid.
- **Transactions.** With one database, "save the approval and record it in the audit log" is one transaction. With two stores, you need extra machinery to keep them agreeing, and you will get it wrong at least once.
- **Money and people.** Each store is a line on the bill and a thing someone must understand at 2 a.m.

With one Postgres, a join answers questions that would otherwise need a script across three systems: "show me every approval Asha decided this week, with the conversation that led to it."

## One turn, table by table

Here is what the claims assistant writes when Rohan, a policyholder, sends a message. Everything lives in one database, `claims_agent`, in a schema called `agent_state`, with DBOS's own tables in a schema called `dbos`.

{{drawing: pg-turn-tables}}

1. **Front door.** Read the newest row in `checkpoints` for Rohan's conversation. Insert a delivery row in `requests`, marked in flight, so the same message sent twice is answered once.
2. **Anything waiting?** Read `approvals` and DBOS's tables to see if a payout or a hand-off is still pending.
3. **The model thinks.** No table is touched at all. Model calls are the one part of the turn that writes nothing.
4. **Each write tool.** Before registering a claim or asking for a payout, insert a row in `requests` with the tool call's key. If the row is already there, the stored result comes back and the tool does not run again.
5. **Save.** Insert or update the `checkpoints` row for this turn. "Insert, or update if this run id is already there" means a retried save can't make a duplicate.
6. **Settle.** Mark the delivery row answered, with the reply. It is settled even when the turn failed, so a retry gets the same answer.

When Rohan asks to release ₹25,001 on claim CLM-010004, which is above the automatic limit of ₹25,000, step 4 starts a DBOS workflow. It writes a row in `approvals` and a row in `dbos.workflow_status`, and goes to sleep. No server is held while it waits, only rows. When Asha, the claims handler, clicks Approve, her decision lands in `dbos.notifications`, and the workflow wakes and pays once. The full story is in [Human in the loop without humans in the way](/writing/human-in-the-loop/).

Add `sessions`, for encrypted sign-in tokens, and `escalations`, for hand-offs, and that is the whole agent: five tables of ours and DBOS's own, in one small managed server.

To be honest about what is built: the conversation, the ledger, approvals, hand-offs and DBOS all run in Postgres today. Memory with pgvector is designed but not built yet. A simple audit table is easy to add, because the decision is already written in `approvals` with who decided it.

## Postgres is on every cloud

You don't have to run it yourself. Managed Postgres, where the cloud handles patches, backups and failover, is offered everywhere:

| Where you are | Managed Postgres |
|---|---|
| Databricks | Lakebase |
| Azure | Azure Database for PostgreSQL |
| Google Cloud | Cloud SQL, AlloyDB |
| AWS | Aurora, RDS |
| Anywhere | Neon, Supabase |

So choosing Postgres doesn't lock you to a cloud. The same tables and the same SQL move with you. Before you rely on pgvector, check that the extension is enabled on the service and version you picked.

## When to move something out

Postgres is the right default, not the answer to everything. Three signs tell you a job has outgrown it.

{{drawing: pg-outgrow}}

1. **The vector collection gets very large.** pgvector works well while its index fits comfortably in the server's memory. When your documents grow far past that and searches slow down, move search to a dedicated service. The tutorial names Azure AI Search as the fallback if the corpus outgrows pgvector.
2. **Heavy analytics.** "Cost per conversation, by week, for the last year" scans millions of rows and fights the agent for the same server. Copy the data to the lakehouse and run reports there. Postgres serves the agent; the lakehouse serves the analysts.
3. **Very high write rates.** If traces or events pour in faster than one server can write them, send them to a store built for that. Keep the ledger and approvals in Postgres, because those need transactions.

Move only the job that shows the sign. Everything else stays where it is.

## What goes wrong

- **Adding a store for each new feature.** "We need memory, so add a vector database." Ask first whether a table and an extension would do.
- **Treating Postgres as a dump.** One `events` table with a JSON blob for everything is not a design. Give each job its own table with real columns, as `requests`, `checkpoints` and `approvals` have.
- **Running reports on the agent's database.** One long query at month-end slows every customer's turn. Analytics go to the lakehouse.
- **Holding a connection while waiting.** An approval can take hours. Put the wait in a durable workflow, as rows, not in an open request.
- **No clean-up.** The tutorial deletes checkpoints older than 30 days and can erase one person's rows on request. Decide this on day one.
- **Moving out too early.** Leaving Postgres because "it won't scale" before any sign appears just buys you six stores and the problems above.

## Seven questions to check your own agent

1. How many separate stores does your agent write to, and could you name what each one holds?
2. If the server restarts in the middle of a turn, what is lost?
3. If the same message arrives twice, what stops a second payout?
4. Where does an approval wait, and does anything hold a thread while it does?
5. Can you restore everything to one consistent moment after an incident?
6. Do reports run on the same database that serves customers?
7. Which of the three signs have you actually seen, and which are you guessing at?

Start with one database, and make each new store earn its place with a sign you can point to.
