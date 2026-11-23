---
name: requirement-to-spec
description: "Turns meeting notes, an old report or a request into a draft spec with acceptance checks. Use when a requirement has been discussed but not written."
---

# Requirement to spec

For: BA

Turns meeting notes, an old report or a request into a draft spec with acceptance checks. Use when a requirement has been discussed but not written.

## You give it
- Meeting notes, emails, the old report or the request.
- `00-project/glossary.md` and any metric definitions.

## It also reads
- The template `templates/spec.md`.

## Steps
1. Write the purpose: the question, who asks it, what they will do with the answer.
2. List what is in and what is out. If the notes do not say, put it under open questions.
3. Write what must be true as numbered acceptance checks. Each one must be testable on data and have an example with real values.
4. For each number, link the metric definition. If there is none, list it as missing.
5. Fill the cases where things go wrong: late source, corrected record, broken rule.
6. List every open question, with who could decide.

## You get
A draft saved as `02-specs/SPEC-NNN-short-name.md`, and a list of questions for the next meeting.

## Check before you hand it over
- [ ] Nothing in the spec says how to build it.
- [ ] Every acceptance check can be run by a tester.
- [ ] Open questions are listed, not answered by guessing.

## Rules for every skill
- Use only what is in the files you were given. Do not invent a fact, a name, a number or a date.
- Where something is missing, write `UNKNOWN` and who could answer.
- After each statement taken from a file, say which file it came from.
- Use the words in `00-project/glossary.md`. If a word is used two ways, say so.
- Write in plain words, for people who do not write code.
- The result is a draft. End with the line: `Draft by an AI assistant. To be checked by: ______`.
- Client data, personal data and secrets stay out of any tool the client has not approved.
