---
name: project-review
description: "Reviews a data project's documents against the checks for its stage and rates each finding. Use before a gate, when taking over a project, or when a project feels off."
---

# Project review

For: PMO, delivery manager, Tech Anchor

Reviews a data project's documents against the checks for its stage and rates each finding. Use before a gate, when taking over a project, or when a project feels off.

## You give it
- The project repository, or the documents for one gate.
- The stage the project is at (1 to 10).

## It also reads
- The template `templates/review-findings-log.md`.
- `checks.md` in this folder.

## Steps
1. Confirm the stage. If the documents disagree about the stage, that is the first finding.
2. Read `checks.md`. Take the checks for this stage and every earlier stage.
3. For each check, look for the evidence in the files. Quote the file and section. If there is none, the check fails.
4. Rate each failed check as Blocker, Major, Minor or Note, using the meanings in the findings log.
5. Look for contradictions between files: two definitions of one number, a date in the plan that the status report no longer supports, a risk with no owner.
6. Match what you found to the six failure themes, and name the early signs that are showing.
7. Recommend go, go with conditions, or stop. Give the conditions with an owner and a date left blank for people to fill.

## You get
A filled findings log saved as `06-reviews/review-stage-N.md`, with the five most important findings on top.

## Check before you hand it over
- [ ] Every finding names the file it came from, or says no file exists.
- [ ] No finding is rated on opinion alone.
- [ ] The reviewer named on the log is a person who did not build it.

## Rules for every skill
- Use only what is in the files you were given. Do not invent a fact, a name, a number or a date.
- Where something is missing, write `UNKNOWN` and who could answer.
- After each statement taken from a file, say which file it came from.
- Use the words in `00-project/glossary.md`. If a word is used two ways, say so.
- Write in plain words, for people who do not write code.
- The result is a draft. End with the line: `Draft by an AI assistant. To be checked by: ______`.
- Client data, personal data and secrets stay out of any tool the client has not approved.
