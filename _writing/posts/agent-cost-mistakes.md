---
title: Why your agent costs $4 per question: 9 cost mistakes
date: 2026-10-31
subject: ai
audience: builders
kind: field-note
draft: false
summary: Teams often find out what their agent costs from the invoice, and the number per question is far higher than anyone guessed. It is rarely the model's price. It is the harness around the model resending everything, looping, retrying and never measuring. Here are the nine mistakes behind the bill, a worked example of how they add up, and the questions to check your own agent.
linkedin: An agent that answers one question for $4 usually isn't using an expensive model. It is resending its whole history on every step, looping with no limit, and nobody is metering it. Our own agent answers a turn for under a tenth of a cent. Here are the 9 mistakes that make the difference.
deeper: /learn/agent-harness/cost.html
deeper_label: Cost, where the money goes, in the Agent Harness tutorial
---

The demo was cheap. A few cents of testing, a happy pilot, a green light. Then the first full month of real traffic arrives, someone divides the invoice by the number of questions answered, and gets something like $4 per question.

That number is not a statistic. It is the kind of bill teams discover, and the pattern behind it is almost always the same. The model's price per token was fine. The harness around the model, meaning the ordinary code that builds the prompt, runs the loop and calls the tools, was quietly multiplying it.

This note walks through how a question gets to $4, the nine mistakes that do it, and what our own agent pays for the same kind of work.

## How a question turns into $4

An autonomous agent works in a loop. The model reads the context, picks a step, a tool runs, the result goes back in, and the model reads everything again. Every trip round the loop is a fresh model call, and you pay for every token it reads.

{{drawing: cost-taxi}}

Here is a made-up but typical example. The prices are example prices, not any vendor's list: $3 per million input tokens and $15 per million output tokens.

1. The system prompt, the tool descriptions and the question come to 10,000 tokens. A token is a piece of a word, roughly three quarters of one.
2. Each step calls a tool that returns a whole web page or a full database dump: about 8,000 tokens, kept in the context forever.
3. The agent takes 16 steps. Step 1 reads 10,000 tokens. Step 16 reads 130,000.
4. Added up, that is 1,120,000 input tokens: $3.36.
5. The model writes about 1,000 tokens per step: $0.24.
6. The last call times out and is retried, resending all 130,000 tokens: $0.39.

Total: **$3.99 for one question.**

{{drawing: cost-where}}

Look at where the money went. The model's answers, the part that feels like "the AI working", cost 24 cents. Almost everything else was the agent re-reading things it had already read.

## Mistakes 1, 2 and 5: paying for the same tokens again and again

{{drawing: cost-snowball}}

**1. Context bloat.** The context is everything sent to the model on one call. If every step sends the whole history plus every raw tool result, the context grows like a snowball and each step costs more than the last. The fix is a context budget: cut long tool results to a fixed size, and drop old exchanges from the middle once the context passes a limit. Our tutorial agent cuts any tool result at 8,000 characters and keeps each call's context near 24,000 characters.

**2. No prompt caching.** Many providers can reuse the unchanged beginning of a prompt and charge less for it. That only works if the beginning really is unchanged, byte for byte. Put the system prompt and tool list first and keep them identical between calls; put anything that changes, such as the time or the user's name, after them. In a scale estimate in our tutorial, the planners assumed 60% of input would hit the cache, and losing that was one of the biggest jumps in the total.

**5. Retries that resend everything.** A timeout on a 130,000-token call costs you the full call again. Cap the number of retries, and never retry an answer that came back unreadable, because the same input usually gives the same mess.

Fix only mistake 1 in the example, by cutting each tool result to about 2,000 tokens, and the same 16 steps cost about $1.56 instead of $3.99.

## Mistakes 3, 7 and 8: the wrong worker for the job

{{drawing: cost-right-model}}

**3. The biggest model for every step.** Deciding "is this a status question or a refund?" doesn't need the strongest model you can buy. Use a small, cheap model for routing and simple steps, and keep the big one for the step that really needs reasoning. Choose with a test set, not a hunch: the cheapest model that passes your tests is the right one.

Run the trimmed example on a model priced at $0.15 per million tokens in and $0.75 out, which is what our tutorial agent actually pays, and the question costs about 8 cents.

**7. Calling the model for things code can answer.** "What's the status of claim CLM-1042?" is a database lookup. Deterministic-first means: if plain code can answer for certain, answer without the model. In our tutorial agent, the direct path answers in 104 milliseconds for $0, against about 7 seconds through the loop.

**8. Multi-agent chatter.** Splitting one job across several agents that talk to each other means each agent reads the others' messages, and each message is another full model call. Every hand-off between agents is a context that gets sent again. Start with one agent and a few tools. Add a second agent only when you can name what it does that a tool can't.

## Mistakes 4 and 6: nothing stops the meter

{{drawing: cost-budgets}}

**4. Runaway loops with no step budget.** An agent that can't find what it wants will keep asking. Without a limit, it asks forever and pays every time. Give each task a maximum number of steps, and stop when the agent makes the same tool call with the same arguments a third time, because that is a loop, not progress.

**6. No per-task budget or kill switch.** A step limit counts trips. A money limit counts dollars. You want both, at more than one level:

- **Per step:** a cap on output tokens and on the size of each tool result. When it is hit, cut and carry on.
- **Per task:** a cap on steps, time and money. When it is hit, stop with a named reason and hand over to a person.
- **Per month:** a budget with alerts, and a kill switch an operator can flip without a deploy.

Our tutorial agent stops a turn at 12 trips, 60 seconds or $0.50, whichever comes first. The money check happens between calls, because you can't un-spend a call that has already been made. The monthly Azure budget only sends an email; it never switches anything off, which is why the per-task limits matter more. The full set is on the [budgets page](/learn/agent-harness/cost-budgets.html).

## Mistake 9: no cost meter

**9. Nobody knows the cost per task.** Cloud bills arrive by resource, hours late: so much for the model, so much for the database. They can't tell you that one claim cost a tenth of a cent and another cost $2. Only your own code can.

The fix is a small meter. When each model response arrives, read the token counts it reports, multiply by a price table in your code, and add it to the running total for the task. Write that total on the trace, the record of every step in the run. Now you can sort tasks by cost, find the expensive ones and see which mistake caused them. Make a model with no price fail at start-up rather than count as free.

The number to watch is cost per task, or better, cost per task actually resolved. A rising total bill with a flat cost per task is growth. A flat number of users with a rising cost per task is a problem.

## What our own agent pays

Our tutorial agent is a claims assistant for a motor insurer. Its real turns, priced by its own meter in October 2026, cost between $0.00014 and $0.00093 each when they go through the loop: well under a tenth of a cent. Turns answered by the direct path, refused or blocked before the model cost $0 in model tokens.

What makes a turn dearer is more trips round the loop. One turn sent 652 tokens on its first trip and 1,535 on its second, the snowball in miniature. The dearest turns took three trips. At those prices, twelve trips would cost about 5 cents, so the $0.50 ceiling has never been reached.

None of that comes from a clever model. It comes from the nine fixes above, and most of them are the same harness parts that keep the agent safe.

## 9 questions to check your own agent's cost

1. Can you name the cost of one task, from your own trace, not the cloud bill?
2. How many input tokens does the last step of a typical task send, compared with the first?
3. Are tool results cut to a fixed size before they go back to the model?
4. Is the start of every prompt identical between calls, so caching can work?
5. Which steps use your biggest model, and has a test shown a smaller one fails them?
6. What share of questions could plain code answer without the model?
7. What is the maximum number of steps a task can take, and what happens when it is hit?
8. Is there a money limit per task, and a kill switch someone can flip today?
9. If you run more than one agent, can you say what each one costs per task?

Find the cost of one task first; every other fix starts from that number.
