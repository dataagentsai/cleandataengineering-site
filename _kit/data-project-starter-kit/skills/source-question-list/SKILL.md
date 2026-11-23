---
name: source-question-list
description: "Prepares the questions for a meeting with a source system owner and records the answers. Use before and after every source meeting."
---

# Source question list

For: BA, Tech Anchor

Prepares the questions for a meeting with a source system owner and records the answers. Use before and after every source meeting.

## You give it
- What is known about the source so far.
- The spec or the metrics that need this source.

## It also reads
- The template `templates/source-questionnaire.md`.

## Steps
1. Read what is known. Pre-fill the questionnaire with it, and say where each answer came from.
2. List the questions still open, most important first: owner, key, changes and deletes, access, the figure to match.
3. Add questions specific to the metrics: which fields feed which number.
4. After the meeting, take the notes and fill the answers. Mark what is still UNKNOWN and who to ask.
5. Update the source register row: owner, access status, size, biggest unknown.

## You get
Before: a one-page question list. After: `01-discovery/questionnaire-SOURCE.md` filled, and the register updated.

## Check before you hand it over
- [ ] Every answer says who gave it.
- [ ] Nothing is filled from general knowledge of similar systems.
- [ ] The list of unknowns has names and dates.

## Rules for every skill
- Use only what is in the files you were given. Do not invent a fact, a name, a number or a date.
- Where something is missing, write `UNKNOWN` and who could answer.
- After each statement taken from a file, say which file it came from.
- Use the words in `00-project/glossary.md`. If a word is used two ways, say so.
- Write in plain words, for people who do not write code.
- The result is a draft. End with the line: `Draft by an AI assistant. To be checked by: ______`.
- Client data, personal data and secrets stay out of any tool the client has not approved.
