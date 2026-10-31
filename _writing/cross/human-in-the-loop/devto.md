---
title: Human in the loop without humans in the way
published: false
canonical_url: https://cleandataengineering.ai/writing/human-in-the-loop/
description: A person should approve the few actions that can't be undone, and nothing else. The approval should be a durable wait that holds no server, shows the approver enough to decide in seconds, and has a clear answer for "nobody replied". Autonomy widens only when people have agreed with the agent on that one decision, measured.
---

*Originally published at [cleandataengineering.ai](https://cleandataengineering.ai/writing/human-in-the-loop/).*


Our claims assistant can pay money. A signed-in policyholder, Rohan, can ask it to release the payment on an approved claim, and the money goes straight to his account.

That is the kind of action that needs "a human in the loop". But a human on *everything* means Rohan waits a day to learn his claim status, and the handler, Asha, spends her shift approving things that never needed her.

The goal is a person on the few decisions that matter, and nowhere else. This post shows how we arranged that, using three real runs of the assistant: a payout within the limit, one above the limit that Asha approved, and one she refused.

## Three lanes, not one gate

{{drawing: hitl-toll-gate}}

At a toll plaza most cars never stop, some stop for a quick look, and a few are pulled over every time. An agent's actions sort the same way. We call these **risk tiers**: groups of actions that get the same treatment.

{{drawing: hitl-lanes}}

- **Green: runs alone.** Reading a claim's status. Paying ₹25,000 or less on an approved claim, which a plain rule in code, `policy:automatic-limit`, allows in the same turn. In the real run (flow 7), Rohan's ₹25,000 payout was done in 3.2 seconds with no person involved.
- **Yellow: needs approval.** A payout above ₹25,000. In flows 8 and 9, Rohan asked for ₹25,001 and the agent paused until Asha decided.
- **Red: always goes to a person.** When someone was hurt, or when Rohan asks for a human, the agent doesn't try at all. It hands the conversation to a person straight away.

The lines between lanes live in code and configuration, not in the prompt. The model can only ask for an action; the harness, the ordinary code around the model that runs its tools and checks, puts the request in the right lane.

The rule that makes this a must is [AAC-0078](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0078.yaml) in the AI Assurance Catalog: a defined class of irreversible actions pauses for a person, and the approval path, the timeout and the case where the facts changed during the pause are all tested.

## Approval is a durable wait

Here is the hard part. Asha might take five minutes or five hours. What does the agent do meanwhile?

The wrong answer is to keep the web request open. That holds a server thread for hours, and if the server restarts, the request is lost.

The right answer is a **durable workflow**: a function whose progress is saved in a database after every step, so it can stop and pick up later exactly where it was. We use DBOS, a small Python library that keeps its state in the PostgreSQL we already run. Temporal does the same job well but needs its own servers.

{{drawing: hitl-durable-wait}}

Here is what happened in flow 8:

1. Rohan asked to release the payment on claim CLM-010004.
2. The agent's tool `request_payout` started a workflow. Its first step read the claim and saw ₹25,001, which is above ₹25,000.
3. The workflow saved the state WAITING and went to sleep. No thread is held, just a row in the database.
4. The turn ended at once. Rohan was told: "I have sent this payout to a claims handler to authorise. Nothing has been paid yet."
5. Later, Asha clicked Approve on her desk. That sent a message to the waiting workflow.
6. The workflow woke, read the claim again to check nothing had changed, and paid it, once.
7. When Rohan asked "has it been paid?", the answer came from the workflow's saved state in 208 milliseconds, without calling the model.

In flow 9 Asha refused instead. The workflow recorded REFUSED, nothing was paid, and Rohan was told that a handler reviewed the payout and couldn't authorise it.

Our server scales to zero when it's quiet, so a restart mid-wait is normal. On start-up, DBOS finds the waiting workflows and carries on from their last saved step. A finished step, such as the payment, returns its saved result and never runs twice.

And the claims system that moves the money doesn't trust the agent's word. Before paying above the limit, it reads the approval record itself: granted, not expired, same claim and amount, and decided by someone other than the customer.

## What the approver sees

An approval is only as good as the card the approver reads. If the card is vague, people click Approve to clear the queue, and the human in the loop becomes a rubber stamp.

{{drawing: hitl-card}}

A good card lets someone decide in seconds:

- **The action in one line,** in plain words: "Pay ₹25,001 to Rohan on claim CLM-010004."
- **Why it's here:** "above the automatic limit of ₹25,000."
- **The facts it turns on,** read fresh from the claims system: the claim status, the assessor's note, the account it will be paid into.
- **What the customer actually said,** quoted, not the model's summary of it.
- **Two clear buttons,** and a place to give a reason for a refusal.

If the facts change while the card is waiting, the old approval is no good. Our workflow marks it STALE and starts a fresh one, so Asha never approves something she didn't see.

## When nobody answers

Every wait needs an answer to "what if nobody replies?"

- **Approvals expire.** Ours are valid for 24 hours. After that the claims system won't accept them, and nothing is paid. Expired means no, never yes.
- **Hand-offs come back.** If nobody picks up a hand-off within 30 minutes, it expires, and the next time Rohan writes the agent says plainly that nobody has picked up his reference yet, and that it is back with him.

## Handing off mid-conversation

Ours hands off for injuries or when Rohan asks for a person, and also when a conversation is going badly: the claims system is down, he has asked for the same thing three times, or the chat has reached ten turns.

A hand-off is the same kind of durable wait. While it's queued, every new message from Rohan gets "a colleague has this" and the model isn't called at all. That stops the agent and a person both answering at once.

The person who picks it up needs the story so far, on the screen they work from. [AAC-0043](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0043.yaml) says to test the hand-off where the receiving person reads it, not just where the system wrote it, and to test it under load.

## Widening autonomy, carefully

If people approve almost every payout of a certain kind for weeks, perhaps that kind can move to green.

{{drawing: hitl-dial}}

But measure the right thing. [AAC-0118](https://github.com/dataagentsai/ai-assurance-catalog/blob/main/catalog/AAC-0118.yaml) says the agreement must be measured on that one decision, not on conversations in general. It must also be sampled where mistakes hide: amounts near the proposed new limit, and cases where the facts are unclear. Say you want to raise the limit from ₹25,000 to ₹40,000. Look at how often Asha agreed on payouts between ₹25,000 and ₹40,000, especially the ones with a messy assessor's note.

Write the sample size and the agreement next to the new limit. If a slice hasn't shown agreement, it stays with a person.

## Five mistakes we see

1. **Approval in a chat message.** "The manager says yes" typed into the conversation is text, and a model or an attacker can produce text. An approval is a record written by a separate desk, checked by the system that acts.
2. **Approvals that hold a server thread.** Waiting inside the web request ties up the server and loses the work on a restart. Use a durable workflow.
3. **No timeout.** A request with no expiry hangs forever, and nobody tells the customer. Decide what silence means, and make it the safe answer.
4. **A card nobody can read.** If approvers can't decide in seconds, they stop reading and start clicking. Measure how long they take and how often they refuse; a refusal rate near zero can mean a rubber stamp.
5. **A person on everything.** If every action needs approval, approvals stop meaning anything. Keep people for the yellow and red lanes.

## Six questions to check your own agent

1. Which of your agent's actions can't be undone, and is that list written in code rather than in the prompt?
2. Can the model, or text inside a tool result, produce something your system treats as an approval?
3. If your server restarts while an approval is waiting, does the approval survive, and is the action still done exactly once?
4. What happens after a day of silence, and is the default "no"?
5. Does the system that acts check the approval itself, including whether the facts changed since it was granted?
6. When you last widened what the agent may do alone, what agreement did you measure, on which decision, and how many cases?

A good human in the loop is someone who is asked rarely, sees everything they need, and is never waited on by a server.

