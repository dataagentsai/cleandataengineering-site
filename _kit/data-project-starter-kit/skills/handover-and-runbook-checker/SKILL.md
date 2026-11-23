---
name: handover-and-runbook-checker
description: "Checks that someone who did not build it can run it. Use before the operational readiness sign-off."
---

# Handover and runbook checker

For: Delivery manager

Checks that someone who did not build it can run it. Use before the operational readiness sign-off.

## You give it
- The runbook and the handover notes.
- The consumer register.

## It also reads
- The template `templates/runbook-and-handover.md`.

## Steps
1. For each thing that can go wrong, check there is an alert, a named person, a first step and an escalation.
2. Check the rerun steps are complete and say what must not be done.
3. Check a failure drill was run, and what changed after it.
4. Check cost has an owner and an alert figure.
5. Check every old report has a switch-off date.

## You get
A findings list rated Blocker, Major, Minor, Note.

## Check before you hand it over
- [ ] A role without a name counts as missing.

## Rules for every skill
- Use only what is in the files you were given. Do not invent a fact, a name, a number or a date.
- Where something is missing, write `UNKNOWN` and who could answer.
- After each statement taken from a file, say which file it came from.
- Use the words in `00-project/glossary.md`. If a word is used two ways, say so.
- Write in plain words, for people who do not write code.
- The result is a draft. End with the line: `Draft by an AI assistant. To be checked by: ______`.
- Client data, personal data and secrets stay out of any tool the client has not approved.
