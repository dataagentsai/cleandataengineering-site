---
name: test-and-reconciliation-plan-writer
description: "Turns a spec's acceptance checks into tests on data and a reconciliation plan. Use when a spec is agreed."
---

# Test and reconciliation plan writer

For: Tester

Turns a spec's acceptance checks into tests on data and a reconciliation plan. Use when a spec is agreed.

## You give it
- The agreed spec.
- The metric definitions with the figures to match.

## It also reads
- The template `templates/test-and-reconciliation-plan.md`.

## Steps
1. One test per acceptance check: data used, expected result, where evidence is kept.
2. List the figures to match, with tolerance and signer. Flag any that are missing.
3. Add the count checks between layers.
4. Add tests for the cases where things go wrong.
5. List the users who must accept, and what each tests.

## You get
`05-test/test-plan-SPEC-NNN.md`.

## Check before you hand it over
- [ ] Every acceptance check has a test.
- [ ] No test uses made-up data where real data is required.

## Rules for every skill
- Use only what is in the files you were given. Do not invent a fact, a name, a number or a date.
- Where something is missing, write `UNKNOWN` and who could answer.
- After each statement taken from a file, say which file it came from.
- Use the words in `00-project/glossary.md`. If a word is used two ways, say so.
- Write in plain words, for people who do not write code.
- The result is a draft. End with the line: `Draft by an AI assistant. To be checked by: ______`.
- Client data, personal data and secrets stay out of any tool the client has not approved.
