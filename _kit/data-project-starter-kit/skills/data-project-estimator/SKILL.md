---
name: data-project-estimator
description: "Estimates a data project as an effort range with assumptions, with waiting time kept apart. Use when someone asks how long or how much a data project, a new source or a change will take."
---

# Data project estimator

For: Tech Anchor, PM, delivery manager

Estimates a data project as an effort range with assumptions, with waiting time kept apart. Use when someone asks how long or how much a data project, a new source or a change will take.

## You give it
- The scope: sources, tables or files, metrics, reports, environments, approvals, years of history.
- `01-discovery/source-register.md`, if it exists.
- `03-backlog/actuals.md` from past projects, if it exists.
- What is not known yet.

## It also reads
- The template `templates/estimate-sheet.md`.
- `rates.md` in this folder.

## Steps
1. Count what can be counted. Fill section 1 of the estimate sheet. If a count is missing, ask for it; do not guess.
2. Size each source as small, medium, large or very large, using the signals in `rates.md`. Say which signals you used.
3. Fill every effort line, including the lines marked as usually forgotten. Give a low and a high figure and the assumption behind each.
4. If past actuals exist, compare. Say where this estimate is lower than what similar work really took.
5. List the waits (access, approvals, answers, sign-offs) in section 4 as calendar time. Never add them to effort.
6. Give the calendar range from team size, effort and waits.
7. Number the assumptions. Mark the one that moves the estimate most. Say what is not included.
8. Say which event will narrow the range, and the date to re-estimate.
9. Ask the five questions in `rates.md` and report any that fail.

## You get
A filled estimate sheet saved as `03-backlog/estimate.md`, and three lines on top: the range, the biggest assumption, the re-estimate date.

## Check before you hand it over
- [ ] It is a range, never one number.
- [ ] The line for understanding the source data is bigger than the line for getting the data in.
- [ ] Waiting is shown apart from effort.
- [ ] Reconciliation is in, with a tolerance and a signer.
- [ ] The people who will build it have seen it.

## Rules for every skill
- Use only what is in the files you were given. Do not invent a fact, a name, a number or a date.
- Where something is missing, write `UNKNOWN` and who could answer.
- After each statement taken from a file, say which file it came from.
- Use the words in `00-project/glossary.md`. If a word is used two ways, say so.
- Write in plain words, for people who do not write code.
- The result is a draft. End with the line: `Draft by an AI assistant. To be checked by: ______`.
- Client data, personal data and secrets stay out of any tool the client has not approved.
