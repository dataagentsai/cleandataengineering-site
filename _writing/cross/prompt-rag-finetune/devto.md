---
title: Prompt, RAG or fine-tune? Pick in that order
published: false
canonical_url: https://cleandataengineering.ai/writing/prompt-rag-finetune/
description: There are three ways to make a language model better at your job. Prompting changes the instructions, RAG hands it the right facts at question time, and fine-tuning trains the model itself. They fix different problems and cost very different amounts, so try them in that order and only climb when your eval set shows the step below can't do it.
---

*Originally published at [cleandataengineering.ai](https://cleandataengineering.ai/writing/prompt-rag-finetune/).*


A team builds an assistant for their HR policies. It gets the leave rules wrong, so someone says, "Let's fine-tune it on our documents." Six weeks later the model sounds more like the company, still gets the leave rules wrong, and the policy has changed twice since the training run.

Fine-tuning was the wrong tool. The model wasn't missing a habit, it was missing facts, and there is a cheaper tool built for exactly that.

There are three ways to make a model better at your job: prompting, retrieval and fine-tuning. Each fixes a different problem and costs a different amount. This post shows what each one is for, and why you should try them in that order.

## Three tools, rising cost

Think of a sticky note, an open book and a gym.

{{drawing: prf-tools}}

- **Prompting is the sticky note.** You write instructions and a few worked examples, and send them with every request. A first version takes minutes and costs almost nothing.
- **RAG is the open book.** RAG stands for *retrieval-augmented generation*. Before the model answers, your code searches your documents for the passages that fit the question and puts them in front of the model. It takes days to set up well: you need a search index and a way to check it finds the right passages.
- **Fine-tuning is the gym.** You train the model further on hundreds or thousands of examples of the answers you want, which changes its *weights* (the numbers inside the model that decide what it says). It takes weeks, and as the fine-tuning lessons in our LearnLLMStack repo found, most of that time goes on gathering good examples and building a fair test, not on the training run itself.

The key difference: the first two change what the model *sees*. Only the third changes the model.

## What each one fixes

They aren't three strengths of the same medicine. They treat different illnesses.

{{drawing: prf-fixes}}

**Prompting fixes behaviour and format.** "Answer in two sentences." "Always return these six fields as JSON." "If the question is about salary, hand it to a person." Most problems that look like "the model is dumb" are really "nobody told it clearly." A few good examples in the prompt often close most of the gap.

**RAG fixes missing or changing knowledge.** The model has never seen your leave policy, your product catalogue or yesterday's price list. No instruction can make it know them. Fetch the right passage at question time and it can answer, and quote where the answer came from. When the policy changes, you update the index, not the model.

**Fine-tuning fixes habits, and cost at volume.** It is the right tool for three jobs:

1. A style or language the model handles badly even with examples, such as natural Hinglish replies.
2. A narrow skill or exact format repeated at huge volume, such as sorting a million support tickets a month into twenty types.
3. Letting a small, cheap model do a big model's job on one task, so each request costs far less and runs faster, or fits on a laptop inside a hospital's own network.

**Fine-tuning does not reliably teach facts.** Training squeezes patterns from the examples into the weights. It doesn't file facts away where the model can look them up. In LearnLLMStack we trained a toy model of 22,080 weights on a single sentence. It learned that sentence perfectly, and given a new start like "the dog" it produced nonsense. Big models are far better than a toy, but the lesson carries over: training stores *patterns of what it saw*, not a reference book you can query. Facts learned that way can't be cited, go stale on the day the policy changes, and get mixed up with similar facts.

There is a famous public warning here. BloombergGPT was a 50-billion-weight model trained from scratch on finance text. Later tests found that GPT-4, with no finance training at all, matched or beat it on many finance tasks. Adding knowledge by training is the most expensive way to do it, and a general model with good retrieval often catches up anyway.

## Three questions, in order

Before anything else, write a clear prompt with a few examples, and build a small eval set: a few dozen real questions with known good answers. Then ask three questions.

{{drawing: prf-questions}}

1. **Is the model missing facts, or facts that change?** Then add RAG. Don't fine-tune.
2. **Is the behaviour still wrong despite clear instructions and good examples?** Check that the instructions really are clear first: give the prompt to a colleague and see if they would do the job right. If they would and the model still won't, fine-tuning the habit may be worth it.
3. **Is the cost or speed too high at your real volume?** Say your ticket sorter handles 10 lakh tickets a month on a large model. A small fine-tuned model that matches it on that one task could cost a fraction per ticket. At 50 requests a day, the bill is small and the weeks of setup will never pay back.

If every answer is no, ship the prompt. Our fine-tuning lessons put it simply: before any fine-tune, score the best prompt-only version on the same test set. That score is the baseline. A fine-tune that doesn't beat it, or doesn't beat it cheaply enough, is a "don't fine-tune" result, and that is a useful finding too.

Every one of these steps depends on the eval set. Without it, "the new prompt is better" is an opinion. Our post on [offline evals](/writing/offline-evals/) shows how to build one.

## Most systems combine them

These aren't three rival choices. They stack.

{{drawing: prf-stack}}

Most real systems are a prompt plus RAG on a general model. The prompt carries the rules and the format, and retrieval carries the facts. Deciding what goes into that bundle, and what stays out, is its own skill, covered in [context engineering](/writing/context-engineering/).

A few systems, usually at high volume, add a fine-tuned model underneath. The habits move into the weights, so the prompt gets shorter, but the facts still come from retrieval. Fine-tuning and RAG work together; it is rarely one or the other.

## Mistakes we see often

1. **Fine-tuning to teach facts.** The HR example above. The model gets more confident, not more correct, and the facts go stale with the next policy update. Use RAG.
2. **RAG over a messy corpus, with no evaluation.** Three versions of the same policy, scanned PDFs, and nobody checking whether the search returns the right passage. The model answers from the wrong page, fluently. Clean the documents, and test retrieval on its own: for each eval question, did the right passage come back?
3. **Giant prompts nobody maintains.** Every bug adds a new paragraph, until the prompt is three thousand words, contradicts itself, and nobody dares delete a line. Keep prompts in version control, give each rule a reason, and remove rules your eval set shows aren't needed.
4. **No eval set, so you can't tell if a change helped.** Teams change the prompt, try three questions by hand, and call it better. Then a different slice breaks. Fewer than about a hundred good examples and no test set means you are not ready to fine-tune, and not really ready to change the prompt either.
5. **Fine-tuning to make the model "smarter".** Fine-tuning narrows a model to a task; it rarely makes it broadly better at reasoning. If you need a smarter model, pick a bigger or newer one.

## Five questions to check before you choose

1. Have you written the prompt as clearly as you would brief a new colleague, with two or three examples?
2. Do you have an eval set, and a baseline score from the best prompt-only version?
3. Is the failure about missing facts, or about how the model behaves?
4. If it's facts: do they change, and can you show where each answer came from?
5. If you're thinking of fine-tuning: what volume makes the weeks of setup pay back, and how will you retrain when the task changes?

Start with the sticky note, open the book when facts are missing, and only go to the gym when your numbers send you there.

