---
name: weekly-status-report
description: "Writes the weekly status report in five headings, starting with what was proved. Use every week."
---

# Weekly status report

For: PM

Writes the weekly status report in five headings, starting with what was proved. Use every week.

## You give it
- The backlog.
- The risk and dependency register.
- This week's notes and test results.
- Last week's report.

## It also reads
- The template `templates/weekly-status-report.md`.

## Steps
1. Proved this week: only what works end to end with a number someone checked. Name who checked. If nothing was proved, say so.
2. Next: what will be proved next week.
3. Risks with a date, from the register. Add any early sign seen this week.
4. Waiting on: names, and since when. Flag anything blocked more than three days.
5. Decisions needed: what, from whom, by when, what happens if late.
6. Compare with last week. Say what moved and what did not.

## You get
`04-run/status-DATE.md`.

## Check before you hand it over
- [ ] There is no 'percent complete'.
- [ ] Bad news is in the first half of the page.
- [ ] Every wait has a name and a date.

## Rules for every skill
- Use only what is in the files you were given. Do not invent a fact, a name, a number or a date.
- Where something is missing, write `UNKNOWN` and who could answer.
- After each statement taken from a file, say which file it came from.
- Use the words in `00-project/glossary.md`. If a word is used two ways, say so.
- Write in plain words, for people who do not write code.
- The result is a draft. End with the line: `Draft by an AI assistant. To be checked by: ______`.
- Client data, personal data and secrets stay out of any tool the client has not approved.
