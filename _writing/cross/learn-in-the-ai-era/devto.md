---
title: How to learn in the AI era: draw the map, grow a T, and teach it back
published: false
canonical_url: https://cleandataengineering.ai/writing/learn-in-the-ai-era/
description: When AI can answer any question, facts are cheap; what's scarce is knowing what to learn, how deep to go, and proving you understand it. Draw a map of your field, learn wide at two shallow depths and deep in your core, use AI as a tutor rather than a ghostwriter, and go round the loop of see it, run it, build it, teach it.
---

*Originally published at [cleandataengineering.ai](https://cleandataengineering.ai/writing/learn-in-the-ai-era/).*


Rahul and Ananya join the same data team in the same month. Both are handed the same new tool, and both have the same AI assistant.

Rahul asks the assistant to write the pipeline. It runs. He moves on to the next ticket, and the next. Ananya asks the assistant to explain how the tool works, builds a small version herself, breaks it on purpose, and then explains it to a colleague over lunch.

{{drawing: learn-two-engineers}}

Six months later the pipeline fails at night. Rahul pastes the error into the assistant and gets three confident answers that don't work. Ananya knows where to look, and has it fixed in an hour.

AI didn't make learning unnecessary. It made the *wrong kind* of learning very easy. This post is about the right kind.

## What changed, and what didn't

What changed: facts are free. Any syntax, any error message, any definition is one question away. Memorising them is worth less than it was.

What didn't change: someone still has to decide what the system should do, notice when an answer is wrong, and fix it at night. That needs understanding, and understanding still has to be built in your own head.

So the scarce skills are now three: knowing **what** to learn, knowing **how deep** to go, and **proving** to yourself that you understand it.

## Start with fundamentals that don't expire

Tools change every year. The ideas underneath them change every decade or so. Learn the ideas first, and each new tool becomes a new name for something you already know.

For data and AI engineering, the long-lasting ones include:

- how data is modelled: tables, keys, the grain of a table, history over time
- SQL, and how an engine actually runs a query across many machines
- state and failure: retries, and why running a job twice must not double a number (idempotency)
- testing: checking data, not just code
- cost: what you pay for, per run and per month
- access and privacy: who may see what
- how a language model works: tokens, context, why it can be confidently wrong
- evaluation: how you know an AI answer is right

The site's [key concepts](/concepts/) are exactly this list, each explained once, the same on every cloud.

Learning what happens under the hood is slower than learning the buttons, and it is still the right way. The companion post, [under the hood: why fundamentals are the slow road that wins](/writing/under-the-hood/), shows why, with a real example of a job that changed nothing and still rewrote a file.

## Draw the map before the trek

The fastest learners don't learn more tools. They have a map, and they place each new tool on it.

{{drawing: learn-map}}

Put your role in the middle. Around it, the few big jobs every system in your field does: getting data in, storing and shaping it, serving it, running it, trusting it, guarding it. When a new product appears, ask one question: which branch does it sit on, and what does it replace there? That takes a minute. Without the map, every new name feels like starting again.

Draw yours on paper this week. For AI engineering, the [AI Universe](/learn/ai-universe/) is a ready-made map, with a page for [placing a new name](/learn/ai-universe/place-it/) on it.

## Grow a T: what goes wide, what goes deep

You can't go deep on everything, and you shouldn't stay shallow on everything. The answer is a T-shape, with four depths.

{{drawing: learn-t-depth}}

1. **5 seconds: what is it?** One sentence. "Kafka moves events between systems." Know this for everything on your map.
2. **10 minutes: when would I use it, and not?** Its job, its alternative, its one big trade-off. Know this for most of your map too.
3. **50 minutes: how does it work inside?** The moving parts, why it fails, what it costs. Do this for the things you touch every week.
4. **5 hours: built it, broke it, fixed it.** Only for your core: the few things your job really depends on.

If you can teach it, it's deep. If you can place it on the map and say when to use it, that's wide enough. The common mistake is going 5 hours deep on whatever came up first, and staying at 5 seconds on the thing your job depends on.

## Use AI as a tutor, not a ghostwriter

The same AI can make you sharper or make you dependent. It depends on how you ask.

{{drawing: learn-tutor}}

Prompts that teach you:

- "Explain incremental loads like I'm new, with an everyday example. Then ask me three questions."
- "Here is my explanation of idempotency. What's wrong or missing?"
- "Give me a small broken pipeline that double-counts a day, and let me find the bug."
- "What are the three most common ways this goes wrong in production?"
- "Compare Delta Lake and Iceberg: when would you pick each?"

Prompts that skip the learning: "write it for me", "just fix this error", and pasting the answer in without reading it.

One rule covers it: **never ship what you can't explain.** If the AI wrote it, explain each part back, out loud or in writing, before it goes in. If you can't, that's the bit to learn next.

## The loop: see it, run it, build it, teach it

Reading feels like learning. It is the first step of four.

{{drawing: learn-loop}}

1. **See it.** Start with a picture of how the thing works, not a wall of text. Every course on this site starts this way.
2. **Run it.** Watch it work step by step, then break it on purpose and watch what happens. The [simulators](/simulators/) exist for this: a real Spark batch, a real agent turn, nineteen data problems.
3. **Build it.** A small project with real data, end to end. Small is fine; finished is the point. [Community projects](/projects/) each list good first tasks.
4. **Teach it.** Explain it to a friend, write a short post, or answer someone's question. Teaching finds your gaps faster than any test, and then you go round again.

## Learn with others

Learning alone is slower, and easier to quit. Find one study partner and meet weekly to explain one thing each. Join a project where someone reviews your work. When you've learned something, [write or teach it here](/about/#join); we help shape it. The people who teach end up knowing it best.

## What goes wrong

- **Collecting courses.** Ten started, none finished. Pick one path and finish it; see [find your path](/paths/).
- **The tutorial loop.** Following along feels productive, but you only learn when you build something nobody gave you the steps for.
- **Letting AI skip the struggle.** The struggle is where the learning happens. Ask for a hint, not the answer.
- **Deep in the wrong place.** Five hours on a tool you'll never use, five seconds on the one you use daily.
- **Learning tools, not ideas.** Next year's tool will have a new name. The idea underneath will be the same.

## A 30-day start

1. **Week 1:** draw your map, and circle your core: the three or four things your job depends on most.
2. **Week 2:** get the whole map to the 10-minute depth, and two core items to 50 minutes. Use AI as a tutor, with the prompts above.
3. **Week 3:** build one small project on your core, end to end, with real data.
4. **Week 4:** teach it. Write a page, record a short video, or explain it to a colleague. Then update your map with what you found.

## Seven questions to check your own learning

1. Can you draw your field's map from memory, with your core circled?
2. Pick a tool you use every week: can you explain how it works inside, in two minutes, without notes?
3. Name a new product from this month: which branch does it sit on?
4. In your last piece of AI-assisted work, could you explain every part of it?
5. When did you last break something on purpose to see what happens?
6. What have you built that nobody gave you the steps for?
7. What did you last teach someone, and what gap did it show you?

Answers are free now; understanding is still earned, one map, one build and one explanation at a time.

