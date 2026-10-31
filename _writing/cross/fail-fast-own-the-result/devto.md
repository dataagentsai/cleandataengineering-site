---
title: Fail fast, own the result: critical thinking for forward-deployed engineers
published: false
canonical_url: https://cleandataengineering.ai/writing/fail-fast-own-the-result/
description: Failing fast does not mean failing more. It means finding out you are wrong on day two instead of week seven, by writing down the beliefs your plan stands on and testing the riskiest one in the cheapest way that could prove it wrong. A forward-deployed engineer does this because they own the customer's result, not just their own code.
---

*Originally published at [cleandataengineering.ai](https://cleandataengineering.ai/writing/fail-fast-own-the-result/).*


Priya is a forward-deployed engineer at an insurance company in Pune. For six weeks she builds a claims assistant: it reads a new claim, pulls the policy, and drafts a decision for a human to approve. The code is clean, the tests pass, and the demo goes well.

In week seven she connects it to the real claims system. Most older policies turn out to exist only as scanned PDFs, and the security team will not allow the model to run outside the company's cloud region. Nothing she built was wrong. The plan underneath it was standing on two beliefs nobody had checked.

That is the problem "fail fast" solves. Not by failing more often, but by finding out you are wrong as early and as cheaply as possible.

## Fail fast means find out cheap

The same mistake costs very different amounts depending on when you discover it.

{{drawing: ff-cost-curve}}

On day two, finding out that the policies are scanned PDFs costs one query on a hundred rows. In week two, it costs reworking one screen. In week seven, it costs a rebuild, a missed date and some of the customer's trust.

So failing fast is not about speed of typing. It is about moving the moment of discovery to the left, where it is cheap.

## Every plan stands on beliefs

Critical thinking on the job starts with one uncomfortable step: write down what has to be true for your plan to work.

{{drawing: ff-stilts}}

Take your plan and finish this sentence as many times as you can: "This only works if…". For Priya's assistant:

- This only works if the problem is real: claims handlers really spend their time on this step.
- This only works if the data exists: policies are readable text, not images.
- This only works if the model can do it: it drafts the right decision for most real claims.
- This only works if we can run it in their cloud, under their security rules.
- This only works if people will use it: handlers trust a draft enough to start from it.

None of these is a coding question, and each one can sink the whole project. They feel obvious, which is exactly why nobody checks them.

## The fail-fast loop

Once the beliefs are written down, test them with a small loop that runs in days, not weeks.

{{drawing: ff-loop}}

1. **Write the belief.** One sentence, specific enough to be wrong. "The data is good" can't be tested. "At least 90% of policies since 2020 are stored as text" can.
2. **Find the cheapest test that could prove it wrong.** Not a test that shows you are right. People naturally look for evidence that agrees with them; testers call this confirmation bias. So ask: "What would I see if I were wrong?" and go and look for that. For the data belief, pull 100 random policies, not the 10 the customer picked for the demo.
3. **Set the kill line before you look.** Decide in advance what result means stop or change course: "If fewer than 80 of 100 are text, we redesign around document reading." If you set the line after seeing the result, you will move it.
4. **Run it, then keep, change or stop.** Then write one line about what you learned, and pick the next belief.

Step three is the one people skip, and it is the one that keeps you honest.

## Which belief to test first

You can't test everything at once. Sort the beliefs by two questions: how much would it hurt if this were wrong, and how quickly can I check it?

{{drawing: ff-matrix}}

- **Costly if wrong, quick to test: test first.** Does the data exist? Pull 100 rows. Do users want it? Show three claims handlers a paper sketch of the screen and watch where they hesitate.
- **Costly if wrong, slow to test: plan a proper test, and start it on day one.** Getting access in the customer's cloud can take weeks of security review, so ask in the first meeting, not after the demo.
- **Cheap if wrong, quick to test: just try it.** Button wording, report layout.
- **Cheap if wrong, slow to test: leave it for later.** How it behaves at ten times today's load can wait until people are using it.

For "can the model do it?", the cheapest honest test is about twenty real past cases with known outcomes, run in an afternoon. That is the seed of an eval set; the post on [offline evals](/writing/offline-evals/) shows how to grow it. And often the answer is that part of the job needs no model at all, as in [answer without the model first](/writing/answer-without-the-model/).

## Six thinking tools for the job

These are small habits, each a few minutes long.

1. **The pre-mortem.** Before starting, imagine it is two months later and the project has failed. Write down why. The reasons you come up with are your riskiest beliefs.
2. **"What would change my mind?"** Ask it of yourself and of the customer. If the answer is "nothing", it is a preference, not a belief, and no test will help.
3. **"Compared to what?"** A system that is right 85% of the time sounds weak until you learn the current manual process is right 70% of the time. Always find today's number before judging the new one.
4. **Check the number at its source.** "We get 2,000 claims a day" came from a slide. Count a week of real records.
5. **A second pair of eyes.** Ask one colleague to argue against your plan for ten minutes. Thank them.
6. **Look one step up, one step down, and up to the goal.** Who feeds the data you depend on, and what happens to your output next? If the claims system upstream changes a field, or the payments team downstream relies on your draft, your "working" change can break theirs. And ask which company goal this serves; if you can't name it, check the plan before building more.

## Fail in the cheap places

Fail fast has limits. It is a way to fail safely, not an excuse to be careless.

{{drawing: ff-where}}

Fail as often as you like in a notebook, on a sample of rows, on paper, or in a test account. Never fail on customer data in production, with people's money, or with the customer's trust. The whole point of failing fast in the cheap places is that you never have to fail in the expensive one.

## Own the result, not just the code

There is a second trait that makes this habit stick: **ownership**. A forward-deployed engineer is measured by whether the customer succeeds, not by whether their own code is correct.

If Priya only owned her code, week seven would not be her problem. The code works; the data is the customer's issue. But an FDE owns the result: claims handled faster and right, in the customer's world, with their data. That is what customer success means for this role.

Ownership changes behaviour in four ways:

- **You chase the risky beliefs even when they are outside your code**, because they decide the result.
- **You report failures early and plainly.** "We tested whether policies are text. Only 55 of 100 are. So we are adding a document-reading step, which moves the pilot by one week." A failure found early, with a next step, is good news for a customer.
- **You measure the outcome, not the activity.** Not "we shipped six features" but "handlers now clear a claim in 12 minutes instead of 40". (Those numbers are an example.)
- **You stay until it works for them**, and then make sure their own team can keep it working without you.

The post on [what a forward-deployed engineer does](/writing/forward-deployed-engineer/) covers the rest of the job. This habit sits underneath all of it.

## What goes wrong

- **Failing slow.** Showing nothing until the big demo, so every wrong belief surfaces at once, late.
- **Tests that can't fail.** Trying the model on the ten easy cases the customer chose. It passes, and proves nothing.
- **Moving the kill line.** "80 out of 100 was the bar, but 62 is close enough." Decide before you look.
- **Confusing fast with careless.** Experimenting on live customer data because it was quicker.
- **Owning the code, not the result.** "My part works" while the customer's problem stays unsolved.

## Seven questions to check your own thinking

1. Can you list the beliefs your current plan stands on?
2. Which one would hurt most if it were wrong, and have you tested it yet?
3. What result would make you stop or change course, written down before you look?
4. Is your last test one that could have failed?
5. What is today's number, before your system?
6. Where are you failing: in a cheap place, or an expensive one? And who upstream or downstream would feel it?
7. If your code works perfectly and the customer still isn't better off, whose problem is that?

You will be wrong often; the job is to find out first, and cheaply, and to keep going until the customer is better off.

