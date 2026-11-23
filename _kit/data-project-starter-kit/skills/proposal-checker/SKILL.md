---
name: proposal-checker
description: "Reads a proposal or statement of work for what is missing or not said. Use before it goes to the client."
---

# Proposal and statement-of-work checker

For: Delivery manager, sponsor

Reads a proposal or statement of work for what is missing or not said. Use before it goes to the client.

## You give it
- The draft proposal or statement of work.
- The estimate.

## Steps
1. Compare scope in the proposal with the counts in the estimate. List differences.
2. List assumptions in the estimate that are not in the proposal.
3. List what is excluded but not said.
4. List what the client must provide (access, people, approvals, figures to match) and whether each has a date.
5. Check that discovery is priced on its own or that the price is a range.
6. Check that support after go-live and the switch-off of the old report are covered.

## You get
A findings list rated Blocker, Major, Minor, Note.

## Check before you hand it over
- [ ] Each finding quotes the section it refers to.

## Rules for every skill
- Use only what is in the files you were given. Do not invent a fact, a name, a number or a date.
- Where something is missing, write `UNKNOWN` and who could answer.
- After each statement taken from a file, say which file it came from.
- Use the words in `00-project/glossary.md`. If a word is used two ways, say so.
- Write in plain words, for people who do not write code.
- The result is a draft. End with the line: `Draft by an AI assistant. To be checked by: ______`.
- Client data, personal data and secrets stay out of any tool the client has not approved.
