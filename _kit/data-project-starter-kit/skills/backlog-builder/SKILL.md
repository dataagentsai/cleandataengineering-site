---
name: backlog-builder
description: "Builds an Agile backlog for a data project in thin slices, from the corpus backlog. Use at the start of a project or when a new source or report is added."
---

# Backlog builder

For: PM, BA, product owner

Builds an Agile backlog for a data project in thin slices, from the corpus backlog. Use at the start of a project or when a new source or report is added.

## You give it
- The metrics wanted and the reports they appear in.
- The sources (`01-discovery/source-register.md`).
- The stage the project is at.
- The corpus backlog, downloaded as a sheet from the corpus backlog page.

## It also reads
- The template `templates/agile-backlog.md`.

## Steps
1. List the beliefs that could stop the project. Make each one a spike in slice 0, riskiest first.
2. Define slice 1: one source to one trusted number that a named person checks.
3. Define the later slices by widening: more sources, more metrics, more users.
4. For each slice, pull the corpus backlog items that apply. Common items once; per-source, per-dataset and per-product items once for each.
5. Write each item as a story, keep the corpus ID, the seat, the stage and the acceptance checks.
6. Mark each item Ready or not, using the five Ready rules. List what is missing.
7. Add the Run items: alerts, runbook, cost watch.

## You get
`03-backlog/agile-backlog.md` and `agile-backlog.csv`, and a short list of items that are not Ready and why.

## Check before you hand it over
- [ ] No slice is a layer. Every slice ends in something a person checks.
- [ ] Slice 0 holds the riskiest belief.
- [ ] Every item has acceptance checks written as checks on data.

## Rules for every skill
- Use only what is in the files you were given. Do not invent a fact, a name, a number or a date.
- Where something is missing, write `UNKNOWN` and who could answer.
- After each statement taken from a file, say which file it came from.
- Use the words in `00-project/glossary.md`. If a word is used two ways, say so.
- Write in plain words, for people who do not write code.
- The result is a draft. End with the line: `Draft by an AI assistant. To be checked by: ______`.
- Client data, personal data and secrets stay out of any tool the client has not approved.
