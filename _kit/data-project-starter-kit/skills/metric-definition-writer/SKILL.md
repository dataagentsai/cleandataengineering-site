---
name: metric-definition-writer
description: "Writes one definition for one number, with an owner and a figure to match. Use when a number is named in a requirement, or when two people mean different things by it."
---

# Metric definition writer

For: BA, product owner

Writes one definition for one number, with an owner and a figure to match. Use when a number is named in a requirement, or when two people mean different things by it.

## You give it
- The name of the number.
- How people describe it: notes, old reports, existing formulas.
- The glossary.

## It also reads
- The template `templates/metric-definition.md`.

## Steps
1. Collect every description of the number. If they differ, show them side by side and stop for a decision.
2. Write the formula in words, then exactly. State the grain, what is included and excluded, and the time rule.
3. Name the figure it must match, the tolerance and who signs. If unknown, write UNKNOWN.
4. Draft a worked example for one real period, if real values were given.
5. Add the word to the glossary, with 'also called' and 'not the same as'.

## You get
`02-specs/metric-NAME.md`, and a list of decisions the owner must make.

## Check before you hand it over
- [ ] There is one owner, by name.
- [ ] Included and excluded are both filled.
- [ ] Two different meanings were not merged quietly.

## Rules for every skill
- Use only what is in the files you were given. Do not invent a fact, a name, a number or a date.
- Where something is missing, write `UNKNOWN` and who could answer.
- After each statement taken from a file, say which file it came from.
- Use the words in `00-project/glossary.md`. If a word is used two ways, say so.
- Write in plain words, for people who do not write code.
- The result is a draft. End with the line: `Draft by an AI assistant. To be checked by: ______`.
- Client data, personal data and secrets stay out of any tool the client has not approved.
