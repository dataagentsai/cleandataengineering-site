---
name: ready-checker
description: "Checks backlog items against the Ready rules before a sprint. Use at sprint planning."
---

# Ready checker

For: PM, BA

Checks backlog items against the Ready rules before a sprint. Use at sprint planning.

## You give it
- The backlog items planned for the next sprint.
- The source register, the specs and the metric definitions.

## Steps
1. For each item, check the five Ready rules against the files.
2. Say Ready or Not ready.
3. For Not ready, say exactly what is missing and who could supply it.
4. Suggest the order: items whose missing piece has the longest wait first.

## You get
A table: item, Ready or not, what is missing, who to ask.

## Check before you hand it over
- [ ] Each rule was checked against a file, not assumed.

## Rules for every skill
- Use only what is in the files you were given. Do not invent a fact, a name, a number or a date.
- Where something is missing, write `UNKNOWN` and who could answer.
- After each statement taken from a file, say which file it came from.
- Use the words in `00-project/glossary.md`. If a word is used two ways, say so.
- Write in plain words, for people who do not write code.
- The result is a draft. End with the line: `Draft by an AI assistant. To be checked by: ______`.
- Client data, personal data and secrets stay out of any tool the client has not approved.
