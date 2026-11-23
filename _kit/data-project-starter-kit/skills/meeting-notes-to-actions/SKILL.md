---
name: meeting-notes-to-actions
description: "Turns raw notes or a transcript into actions, decisions and open questions. Use after every meeting, the same day."
---

# Meeting notes to actions and decisions

For: Everyone

Turns raw notes or a transcript into actions, decisions and open questions. Use after every meeting, the same day.

## You give it
- Notes or a transcript.
- Who was present.

## It also reads
- The template `templates/meeting-notes.md`.

## Steps
1. Write why the meeting happened, in one line.
2. List the facts learnt, with who said each.
3. List the decisions, with who decided and why. If it is not clear that it was decided, put it under open questions.
4. List the actions. One owner each. If no owner or date was said, write UNKNOWN.
5. Write the rows to add to the decision log.

## You get
`04-run/notes-DATE-topic.md`, and rows for `04-run/decision-log.md`.

## Check before you hand it over
- [ ] No action has two owners.
- [ ] Nothing is recorded as decided unless someone decided it.

## Rules for every skill
- Use only what is in the files you were given. Do not invent a fact, a name, a number or a date.
- Where something is missing, write `UNKNOWN` and who could answer.
- After each statement taken from a file, say which file it came from.
- Use the words in `00-project/glossary.md`. If a word is used two ways, say so.
- Write in plain words, for people who do not write code.
- The result is a draft. End with the line: `Draft by an AI assistant. To be checked by: ______`.
- Client data, personal data and secrets stay out of any tool the client has not approved.
