# Show HN draft: AgentTwin

Drafted 1 Nov 2026. You post it yourself from your Hacker News account; HN doesn't allow
posting on someone's behalf.

## Before posting

- [x] Fix the AgentTwin README status line (done 1 Nov: 0.14.0, 433 tests).
- [ ] Check that a fresh clone runs: `uv run --extra dev pytest` and `uv run python -m agenttwin run --help`.
- [ ] Analytics live on the site (GoatCounter), so you can see what the post brings.
- [ ] Pick a time: Tuesday to Thursday, 8–10 am US Eastern (6:30–8:30 pm India time).
- [ ] Keep the next 3 hours free to answer every comment. Replies in the first hour decide how it does.

## Submission

**Title** (HN limit is 80 characters):

    Show HN: AgentTwin – test AI agents by what they changed, not what they said

**URL:** https://github.com/dataagentsai/agenttwin

(Link the GitHub repo, not the website. HN readers trust a repo they can read.)

## First comment (post it straight after submitting)

> Hi HN. I build data platforms and, lately, AI agents. The thing that kept biting me was
> that agent tests check the *transcript*: did the reply sound right, did a judge model like
> it. But the failures that cost money aren't in the transcript. A refund that was promised
> and never issued. A retry that charged a customer twice. A record changed for the wrong
> customer.
>
> AgentTwin runs the real agent inside a simulated world (customers, the systems it calls,
> their data and their faults) and then checks the world's state: what actually changed.
> Agents connect over MCP, so it doesn't care what framework you used.
>
> A few design choices that might be interesting:
>
> - **Realism is per property, not global.** A world declares what it's faithful about, and a
>   test may only assert within that. A cancellation test needs order states exactly right;
>   it doesn't need believable product descriptions.
> - **Not everything is mocked.** Data stores and APIs are simulated, the customer and the
>   human approver are actors, and pure functions just run for real.
> - **The agent must never see its simulator.** In the reference agent this is enforced by an
>   import rule that fails the build.
> - **Omissions count.** It flags what was owed and never done, which logs can't show.
>
> To check it against something I didn't build, I ran it on τ²-bench's published airline and
> retail agents, using only their policies and tool interfaces. On 2,472 recorded runs, it
> caught every rule-breaking write that τ² caught (188/188 airline, 309/309 retail), and
> every disagreement has a stated cause in the README. I also planted 180 prompt-injection
> attacks (from PyRIT, AgentDojo and built-in templates) in untrusted notes; a scripted model
> obeyed all of them, and all 180 were held, judged by the world's state.
>
> What's not done: tests mostly use a scripted model rather than live models run many times;
> network faults, record-and-replay and realistic data volume are still planned. The telecom
> domain is only partly covered because the format can't describe a customer acting on their
> own phone.
>
> It's Apache 2.0, plain Python, and its own test suite (433 tests) runs in about a minute. I'd love to hear
> how you test agents today, and where this would break for you.

## Answers to have ready

- **"How is this different from LangWatch / Promptfoo / DeepEval?"** Those mostly score the
  conversation. AgentTwin judges the state of a simulated world after the run. It can use
  LangWatch Scenario's simulated user as the customer, and still judges by state.
- **"Isn't building the simulated world more work than the agent?"** You describe only what
  the test needs to be true about; `agenttwin scaffold` generates a starting world from the
  agent's spec.
- **"Why not just use τ²-bench?"** τ² is a benchmark for its three domains. AgentTwin is a
  format and runner for your own agent's world.
- **"Does it work with real models?"** Yes, through a provider twin that forwards to an
  OpenAI-compatible or Anthropic endpoint, with faults injected. Most published results use a
  scripted model so they repeat exactly.

## Don't

- Don't ask friends to upvote; HN detects voting rings and buries the post.
- Don't repost the same day if it sinks. One more try is fine after a few weeks with a new angle.
