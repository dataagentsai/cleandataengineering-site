---
name: source-to-target-mapping-draft
description: "Drafts which source field feeds which target field, and lists the gaps. Use after the spec and the source questionnaire exist."
---

# Source-to-target mapping draft

For: BA

Drafts which source field feeds which target field, and lists the gaps. Use after the spec and the source questionnaire exist.

## You give it
- The source field lists, with meanings.
- The spec and the metric definitions.

## It also reads
- The template `templates/source-to-target-mapping.md`.

## Steps
1. List the target fields the spec needs.
2. For each, propose the source field and the rule in words. Say how sure you are and why.
3. List target fields with no source.
4. List rules where more than one option exists, with the options.
5. Add an example in and out where real values were given.

## You get
`02-specs/mapping-SPEC-NNN.md`.

## Check before you hand it over
- [ ] No mapping rests on a field name alone: the meaning was checked in the questionnaire.
- [ ] Gaps are listed, not filled.

## Rules for every skill
- Use only what is in the files you were given. Do not invent a fact, a name, a number or a date.
- Where something is missing, write `UNKNOWN` and who could answer.
- After each statement taken from a file, say which file it came from.
- Use the words in `00-project/glossary.md`. If a word is used two ways, say so.
- Write in plain words, for people who do not write code.
- The result is a draft. End with the line: `Draft by an AI assistant. To be checked by: ______`.
- Client data, personal data and secrets stay out of any tool the client has not approved.
