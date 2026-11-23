---
name: risk-and-dependency-register
description: "Reads the project's files for early signs of the known failure causes and keeps the register current. Use weekly."
---

# Risk and dependency register

For: PM, PMO

Reads the project's files for early signs of the known failure causes and keeps the register current. Use weekly.

## You give it
- The project repository.
- This week's notes.
- The current register.

## It also reads
- The template `templates/risk-and-dependency-register.md`.

## Steps
1. Read for early signs: unanswered questions to a source owner, access not granted, a metric with no owner, two definitions, no figure to match, scope added with nothing removed, status in percent, no one named to run it.
2. For each sign, add or update a risk, with its theme (A to F) and where the sign was seen.
3. List every dependency on someone outside the team, with the date asked and the days blocked.
4. Flag blocks older than three days for escalation.
5. Leave owner and date blank for people to fill; never assign a person yourself.

## You get
An updated `04-run/risk-and-dependency-register.md`, and the three items that need action this week.

## Check before you hand it over
- [ ] Every risk names where its early sign was seen.
- [ ] No owner was invented.

## Rules for every skill
- Use only what is in the files you were given. Do not invent a fact, a name, a number or a date.
- Where something is missing, write `UNKNOWN` and who could answer.
- After each statement taken from a file, say which file it came from.
- Use the words in `00-project/glossary.md`. If a word is used two ways, say so.
- Write in plain words, for people who do not write code.
- The result is a draft. End with the line: `Draft by an AI assistant. To be checked by: ______`.
- Client data, personal data and secrets stay out of any tool the client has not approved.
