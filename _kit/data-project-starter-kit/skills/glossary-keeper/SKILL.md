---
name: glossary-keeper
description: "Keeps one meaning per business word across the project's files. Use weekly, and before any spec is agreed."
---

# Glossary keeper

For: BA

Keeps one meaning per business word across the project's files. Use weekly, and before any spec is agreed.

## You give it
- The glossary.
- The specs, notes and status reports.

## It also reads
- The template `templates/glossary.md`.

## Steps
1. List the business words used in the files that are not in the glossary.
2. List the words used with two meanings, with the file for each.
3. List the words with no owner.
4. Propose an entry for each new word, taken from how the files use it.

## You get
Proposed changes to `00-project/glossary.md`, and the list of words needing a decision.

## Check before you hand it over
- [ ] No meaning was taken from outside the project's files.
- [ ] Conflicts are shown, not resolved.

## Rules for every skill
- Use only what is in the files you were given. Do not invent a fact, a name, a number or a date.
- Where something is missing, write `UNKNOWN` and who could answer.
- After each statement taken from a file, say which file it came from.
- Use the words in `00-project/glossary.md`. If a word is used two ways, say so.
- Write in plain words, for people who do not write code.
- The result is a draft. End with the line: `Draft by an AI assistant. To be checked by: ______`.
- Client data, personal data and secrets stay out of any tool the client has not approved.
