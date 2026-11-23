# Rates and rules for the estimator

These are starting values, taken from the worked example on cleandataengineering.ai/how-we-work/estimation/.
Replace them with your own actuals as soon as you have any (`03-backlog/actuals.md`).

## Size each source
| Size | Signals | First build, person-weeks |
|---|---|---|
| Small | A few tables, clear keys, a reliable change column, documents exist, the owner answers within a day | 1 to 2 |
| Medium | Ten to thirty tables, some joins to learn, deletes need care, some documents, the owner is busy | 3 to 5 |
| Large | Many tables or a packaged application, codes that need a lookup, no change column, history in odd formats | 6 to 10 |
| Very large | Several systems feeding one model, conflicting definitions, no reachable owner | 10 to 20, split it |

Twenty sources are never twenty copies of an average source. Size each one.

## One medium source, estimated honestly
About twelve tables, a daily load, history kept, a few final tables and one dashboard that must match the finance report.

| Line | Low (days) | High (days) | Usually in the estimate? |
|---|---|---|---|
| Discovery: what the source data means | 12 | 18 | No |
| Access and environment set-up (effort only) | 2 | 3 | No |
| Getting the data in | 4 | 6 | Yes |
| Cleaning, with history | 8 | 12 | Yes |
| Final tables and metric definitions | 6 | 10 | Yes |
| Tests and checks | 6 | 9 | No |
| Reconciling with finance, and fixing | 8 | 14 | No |
| Loading history | 3 | 5 | No |
| Deploy, monitoring, runbook | 4 | 6 | No |
| Support after go-live, first four weeks | 5 | 8 | No |
| Total | 58 | 91 | |

A code-only estimate of this source says 18 to 28 days. The honest one is about three times that.
Use this table as the shape for other sizes. Scale it by the source size, then adjust each line with a stated reason.

## Rules
1. Give a range, with the assumptions behind it.
2. Show the usually forgotten lines on their own lines.
3. Show waits apart from effort. Waiting for access is not effort.
4. Do not add a flat percentage for contingency. Put the forgotten items in as real lines.
5. Say the date to re-estimate, usually after the first source runs end to end.
6. Before discovery, fix the price of discovery only.
7. Compare with what similar work really took, not with what it was estimated at.

## Five questions to ask of any estimate
1. Is there a line for understanding the source data, and is it bigger than the line for getting the data in?
2. Is it a range, and does it say what event will narrow it?
3. Are waits (access, answers, sign-off) shown apart from effort?
4. Is reconciliation in, with a tolerance and someone to sign it off?
5. Did the people who will build it make the estimate?
