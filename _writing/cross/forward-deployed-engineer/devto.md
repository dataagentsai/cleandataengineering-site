---
title: What a forward-deployed engineer actually does
published: false
canonical_url: https://cleandataengineering.ai/writing/forward-deployed-engineer/
description: A forward-deployed engineer works inside a customer's team to make a product or AI system actually work in their world. The job runs in six steps: discovery, a scope that does as much as possible without a model, a prototype, deploying in the customer's own cloud, proving it with evals and cost numbers, and handing over. It needs engineering plus ten traits, from listening and judgement to ownership of the customer's result and the big picture.
---

*Originally published at [cleandataengineering.ai](https://cleandataengineering.ai/writing/forward-deployed-engineer/).*


A product works perfectly in the vendor's demo. Then it meets a real customer. Their data is in three systems that disagree. Their security team will not let anything leave their cloud. Their finance lead wants to know what it costs per month before anyone says yes.

Someone has to close that gap. Not a salesperson, and not a slide deck. An engineer who goes and sits with the customer's team, learns how their world works, and makes the product work in it.

That person is a **forward-deployed engineer**, or FDE. "Forward" is borrowed from the army: you work at the front, where the customer is, not back at headquarters.

## An engineer with a backpack

The simplest picture of the job is an engineer who packs a bag and moves into the customer's office for a few weeks or months.

{{drawing: fde-backpack}}

The bag holds the things that travel well: the product, a set of tools, and habits for building, testing and measuring. What is not in the bag is the customer's world. Their data, their rules, their people and their cloud are all already in that office. The FDE's job is to join the two.

This is why the role exists mostly around AI systems and data platforms today. A model or a platform is generic. The value only appears when it is wired into one company's messy, specific reality.

## The job in six steps

Every engagement is different, but the shape repeats. Here it is as a path.

{{drawing: fde-path}}

1. **Discovery.** Find out three things before writing any code: what problem, in the customer's own words; what data exists, where it lives and how good it is; and what rules apply, such as who may see what and what must never happen. A good week of discovery saves a bad month of building.
2. **A deterministic-first scope.** "Deterministic" means the same input always gives the same output, like ordinary code or a SQL query. Before reaching for a model, ask how much of the job plain code can do. Often a lookup, a rule and a template answer most cases, and the model is only needed for the part that truly needs language. This makes the system cheaper, easier to test and easier to trust.
3. **A prototype.** Build the smallest thing that works end to end on the customer's real data, even if only for one slice: one region, one product line, one kind of request. Show it early. The first reaction from real users is worth more than any requirement document.
4. **Deploy in their cloud.** The customer's data usually cannot leave their account, and their security team must be able to see and switch off everything. So the system runs inside their cloud, with their sign-in, their network rules and their logs. This step is often slower than building the prototype, so plan for it from day one.
5. **Prove it with evals and cost numbers.** An eval is a test set of real cases with known right answers that the system must pass before each release. Run it and show the score slice by slice. Then show what each answer or task costs, in rupees, including the people who review the output. "It looks good" is an opinion. "It got 92 of 100 refund cases right at about ₹3 a case" is a decision someone can make. (Those numbers are an example.)
6. **Hand over.** The customer's own team must be able to run, change and fix the system after you leave. That means a runbook, a short design note, the eval set they can re-run, and at least one person on their side who has made a change while you watched. If it only works while you are in the room, it doesn't work.

The posts on [offline evals](/writing/offline-evals/) and [measuring agent ROI](/writing/agent-roi/) cover step five in depth, and [one harness, five homes](/writing/harness-five-homes/) helps with step four when the customer's cloud is Azure, Google Cloud, AWS or Databricks. Together they make a decent toolkit.

## The skills mix

Engineering is the base. You need to build things that run, read unfamiliar systems quickly and debug in someone else's environment. But engineering alone is not enough, and it is the ten traits across the top that make the job.

{{drawing: fde-skills}}

- **Listening.** Customers describe solutions, not problems. "We need a chatbot" often means "our support team answers the same forty questions all day". Hearing the second sentence inside the first is most of discovery.
- **Writing.** You will write more than you expect: a one-page scope, a decision note, a weekly update, the runbook. Short, plain writing is how a busy customer team keeps up with you, and how the work survives after you leave.
- **Judgement.** Deciding what not to build. Saying "this part does not need a model". Telling the customer early that their data cannot support what they hoped. Choosing the boring, reliable option when the exciting one would make a better demo.
- **Ownership.** You are measured by whether the customer succeeds, not by whether your code is correct. If the data turns out to be scanned PDFs, that is your problem too, because it decides the result. Report bad news early with a next step, and measure the outcome ("claims cleared in 12 minutes instead of 40") rather than the activity ("six features shipped").
- **The big picture.** Every system sits in a chain. Know who feeds the data you depend on, who uses your output next, and which company goal the work serves. A change that works in your piece but breaks the payments team downstream is not a working change.
- **Earning trust.** Keep small promises, say "I don't know yet" when you don't, and never let the customer be surprised by bad news. Everything else rests on this.
- **Comfort with ambiguity.** There is rarely a full spec. Turn "make AI work for our claims team" into a concrete first step this week, and let the next step come from what you learn.
- **Learning speed.** New domain, new data, new cloud, every engagement. Pick up enough insurance, pharma or retail in days to ask good questions.
- **Pragmatism.** Ship the good-enough version that solves today's problem. Perfect is often just a later date.
- **Carrying lessons back.** The gap you closed by hand at one customer will appear at the next. Turn the fix into a reusable piece and take it back to the product team; this is what makes an FDE worth more than a contractor.

A useful test: could you explain what you built, why, and which company goal it moves, to the customer's finance lead in five minutes? If yes, the traits are working. The habit underneath all of them is in [fail fast, own the result](/writing/fail-fast-own-the-result/).

## How it differs from nearby roles

The FDE is often confused with three other jobs. They overlap, but the centre of each is different.

{{drawing: fde-roles}}

| Role | Main job | Writes production code? | Stays until it works? |
|---|---|---|---|
| Consultant | Advise on what to do | Sometimes | Often leaves with a report |
| Solutions engineer | Show the product can fit, before the sale | Demos and proofs of concept | Usually hands off after the sale |
| Product engineer | Build the product for all customers | Yes, in the product | Rarely meets a single customer |
| Forward-deployed engineer | Make it work for this customer | Yes, in their environment | Yes, then hands over |

These are generalisations; real jobs blur the lines. The short version: a consultant advises, a solutions engineer persuades, a product engineer builds for everyone, and an FDE builds for one customer until it works. A good FDE also carries lessons back to the product team, because the same gap they closed by hand at one customer will appear at the next.

## What goes wrong

- **Skipping discovery because the product "already does that".** It does, in the demo. The customer's data is where it breaks.
- **Starting with the model.** The prototype is impressive, but it is slow, costly and hard to test, and half of it could have been a SQL query.
- **Building in your own cloud first.** Moving it into theirs later turns into a second project, with a security review you didn't plan for.
- **No numbers at the end.** Without an eval score and a cost per task, the customer has nothing to decide with, and the pilot quietly stalls.
- **Becoming the system.** If every fix needs you, you have built a dependency, not a hand-over.
- **Fixing your piece, breaking theirs.** Changing a field, a schedule or a format without asking who reads it next.

## How to grow into it

You don't need the title to practise the job. Most FDEs started as data, software or platform engineers who kept ending up in rooms with the people who used their work.

1. **Sit with your users.** Ask to shadow the analysts or support staff who use what you build, for one afternoon. Write down every workaround you see.
2. **Practise deterministic-first.** On your next feature, write down which part plain code can do before you reach for a model or a new service.
3. **Deploy into an environment you don't control.** A different cloud account, a locked-down network, someone else's sign-in. It is uncomfortable, which is the point.
4. **Always end with a number.** Get used to closing every piece of work with a test score and a cost.
5. **Write the hand-over note even when nobody asks.** Then ask a colleague to make one change using only that note.
6. **Build one end-to-end project as if for a customer.** On this site, [projects](/projects/) carrying the "Forward-deployed ready" label are good ones to copy: take one, run it through the six steps above, and finish with an eval score, a cost and a hand-over note.

## Seven questions to check your own FDE readiness

1. Can you name the problem, the data and the rules for the last thing you built, in the user's words?
2. Which part of it could have been done without a model or a new service?
3. Could it run in someone else's cloud account by next week?
4. Do you know its pass rate and its cost per task?
5. Could someone else change it tomorrow without calling you?
6. What is the customer better off by, in their own numbers?
7. Who upstream and downstream would notice if your piece changed?

The product gets them interested; the forward-deployed engineer gets it working, proves it, and leaves it in good hands.

