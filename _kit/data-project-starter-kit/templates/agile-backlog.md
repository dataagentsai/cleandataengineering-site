# Agile backlog for a data project

Project: ______  ·  Owner of this file: ______  ·  Last updated: ____-__-__

Copy to: `03-backlog/`  ·  Owner: PM

A data backlog is cut in thin slices. A slice runs from one source to one trusted number that a person checks. Do not plan layer by layer.

The same backlog is in `agile-backlog.csv`, to open as a sheet or load into your tracking tool.

## Kinds of item
| Kind | What it is | Example |
|---|---|---|
| Spike | Learn something risky in a fixed time. The output is an answer. | Can we reach the billing system from our environment? |
| Slice | A thin piece through every layer, for one source, ending in a number a person checks. | Daily sales by store, from the orders system, to one report. |
| Run | What keeps it alive. | Alert the on-call person if the nightly load is late. |
| Fix or debt | Works today, will hurt later. Small, visible and sized. | Replace a manual file upload with the automatic load. |

## Ready: an item can start when
- [ ] The source and its owner are named.
- [ ] We have seen a real sample of the data.
- [ ] Access to the source works from our environment.
- [ ] The business owner of each metric is named.
- [ ] Acceptance criteria are written as checks on data, not wishes.

## Done: an item is finished when
- [ ] Tested against the source: counts and totals match.
- [ ] Reconciled to a figure the business already trusts.
- [ ] Quality checks run daily and alert a named person.
- [ ] Deployed to the test environment by the pipeline, not by hand.
- [ ] Documented: where it came from and what it means.
- [ ] Shown to the business owner, who accepts it.

## The slices
Order by risk. Slice 0 is the spikes: test the most dangerous belief first.

| Slice | What it proves | Sources | The number a person checks | Who checks | Target date |
|---|---|---|---|---|---|
| 0 Spikes | The beliefs that could stop the project hold | | | | |
| 1 | One source to one trusted number, end to end | | | | |
| 2 | Widen: | | | | |
| 3 | Widen: | | | | |

## The items
Pull items from the corpus backlog (cleandataengineering.ai/how-we-work/data-essentials/backlog/). Keep its ID so the acceptance checks come with it.

| ID | Slice | Kind | Story | Corpus item | Seat | Stage | Size | Ready? | Acceptance checks | Evidence | Owner | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B-001 | 0 | Spike | Get one real extract and compare it with the description we were given | | BA | 3 | S | Yes | We can open it; it matches the description | Sample file and notes | | To do |
| B-002 | 0 | Spike | Reach the source from the build environment with the right permissions | | PM | 3 | S | No | A test read works from our environment | Screenshot or log | | To do |
| B-003 | 0 | Spike | Rebuild one figure finance already knows | | BA | 3 | M | No | Within the agreed tolerance | Worked example | | To do |
| B-004 | 1 | Slice | Daily sales by store, from the orders system, to one report | | Tech Anchor | 6 | L | No | Matches the finance report within tolerance | Reconciliation result | | To do |
| B-005 | 1 | Run | Alert a named person if the nightly load is late | | Tech Anchor | 6 | S | No | A test failure reaches the named person | Alert received | | To do |

Sizes: S, M, L. Give days as a range in the estimate sheet, not here.

## Each sprint
| Sprint | Goal: what will be proved | Items | Demo to whom, with which real numbers |
|---|---|---|---|
| 1 | | | |

Done when: slice 1 ends in a number a named person will check, and every item in the next sprint is Ready.
