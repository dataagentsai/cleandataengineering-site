# Checks for a project review, by stage

A short list for non-technical reviewers. Check this stage and every stage before it.
The full catalogue is at cleandataengineering.ai/learn/technical-anchor/project-review/checks/.

For each check: find the evidence in the project's files. No evidence means the check fails.

## Stage 1. Requirement received
- The need names the decision it supports, not only 'build a dashboard'.
- There are at least three business questions the data must answer.
- A sponsor and a business owner are named.
- Assumptions are listed.

## Stage 2. Rough estimate
- The estimate is a range, with its assumptions.
- It lists what was counted: sources, tables, reports, users.
- The cost of discovery is shown on its own.
- Waiting is shown apart from effort.

## Stage 3. Discovery
- Every source has an owner by name and a filled questionnaire.
- The team has seen a real sample of each source.
- Access to each source has been requested, with a date, and tested.
- Every metric has one definition and one business owner.
- At least one figure has been rebuilt by hand and matches a figure the business trusts.
- Requirements are written as checks on data.
- The fail-fast tests have results: sample, access, meaning, one number, volume and timing, change, user.
- A risk and dependency register exists, with owners and dates.

## Stage 4. Discovery sign-off (gate)
- A review of the discovery document was held by someone who did not write it.
- The decision is recorded: go, go with changes, or stop, by a named signer.
- Conditions have owners and dates.
- The estimate was redone after discovery, and scope and date changes are written down.

## Stage 5. MVP 1 starts
- The backlog is cut in slices, not layers. Slice 1 ends in a number a named person checks.
- Every item in the first sprint meets the Ready rules.
- Environments and access work on day one.
- Design, security and privacy reviews are booked or done.

## Stage 6. Build
- The weekly status report says what was proved, with a number someone checked.
- Effort is tracked against the estimate weekly, apart from calendar time.
- Scope changes have a decision log entry and say what was removed.
- Demos use real numbers.
- No dependency has been blocked for more than three days without escalation.

## Stage 7. Test
- Every acceptance check in the spec has a test with a result.
- Totals match the trusted figure within the agreed tolerance, and someone signed.
- Counts between layers are explained.
- Users accepted on real data, by name.
- There is a rule for bad records, and someone looks at them.

## Stage 8. Deploy
- The release is done by the pipeline, not by hand, and has been rehearsed.
- Quality checks run daily and alert a named person.
- The runbook exists, and a failure drill was run from it by someone who did not build it.
- Cost has an owner and an alert figure.
- Access rules are in place and were reviewed.

## Stage 9. Production sign-off (gate)
- The first production run was reconciled to the trusted figure.
- Operations accepted the runbook, by name.
- Open findings rated Blocker are closed; Majors are accepted in writing with a date.
- Every old report has a switch-off date.

## Stage 10. Project sign-off (gate)
- The old reports were switched off, or there is a dated decision to keep them.
- The handover pack was accepted by the people who will run it.
- Estimated against actual is recorded, effort and calendar apart.
- A retrospective produced at least one change to the starter kit.

## At every stage
- Every document is in the project repository, with history.
- Every number has a name, a formula and an owner.
- Every risk, action and dependency has one name and one date.
- No file contradicts another on scope, dates or definitions.
