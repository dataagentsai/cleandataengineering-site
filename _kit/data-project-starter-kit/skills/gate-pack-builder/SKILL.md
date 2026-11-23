---
name: gate-pack-builder
description: "Gathers the evidence for a sign-off gate and says what is missing. Use two weeks before a gate."
---

# Gate pack builder

For: PM, delivery manager

Gathers the evidence for a sign-off gate and says what is missing. Use two weeks before a gate.

## You give it
- The gate (for example discovery sign-off, production sign-off).
- The project repository.

## It also reads
- The template `templates/sign-off-record.md`.

## Steps
1. List what this gate needs as evidence (see the sign-off record and `skills/project-review/checks.md`).
2. Find each piece in the repository. Link it.
3. List what is missing or out of date.
4. List open review findings rated Blocker or Major.
5. Draft the one-page summary for the signer: what they are signing, the evidence, the open points.

## You get
`06-reviews/gate-NAME-pack.md`, and a draft sign-off record.

## Check before you hand it over
- [ ] Every evidence link opens a real file.
- [ ] Missing evidence is on the first page, not the last.

## Rules for every skill
- Use only what is in the files you were given. Do not invent a fact, a name, a number or a date.
- Where something is missing, write `UNKNOWN` and who could answer.
- After each statement taken from a file, say which file it came from.
- Use the words in `00-project/glossary.md`. If a word is used two ways, say so.
- Write in plain words, for people who do not write code.
- The result is a draft. End with the line: `Draft by an AI assistant. To be checked by: ______`.
- Client data, personal data and secrets stay out of any tool the client has not approved.
