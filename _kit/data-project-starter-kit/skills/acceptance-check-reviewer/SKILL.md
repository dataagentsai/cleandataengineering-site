---
name: acceptance-check-reviewer
description: "Finds requirements that cannot be tested and suggests a rewrite. Use before a spec goes for agreement."
---

# Acceptance check reviewer

For: BA, tester

Finds requirements that cannot be tested and suggests a rewrite. Use before a spec goes for agreement.

## You give it
- A spec, or a list of requirements.

## Steps
1. Read each line. Mark it as a check on data, or a wish.
2. A wish has no number, no source of truth, or no way to test it. Words such as fast, accurate, user-friendly and complete are signs.
3. For each wish, suggest a rewrite with a value, a comparison and who accepts. Leave the value blank if it is not known.
4. List the checks that have no one to accept them.
5. List what the spec does not cover: late data, corrections, bad records, who can see it.

## You get
A table: line, check or wish, why, suggested rewrite. Then the gaps.

## Check before you hand it over
- [ ] Suggested values are marked as suggestions.
- [ ] Every line of the spec was looked at.

## Rules for every skill
- Use only what is in the files you were given. Do not invent a fact, a name, a number or a date.
- Where something is missing, write `UNKNOWN` and who could answer.
- After each statement taken from a file, say which file it came from.
- Use the words in `00-project/glossary.md`. If a word is used two ways, say so.
- Write in plain words, for people who do not write code.
- The result is a draft. End with the line: `Draft by an AI assistant. To be checked by: ______`.
- Client data, personal data and secrets stay out of any tool the client has not approved.
