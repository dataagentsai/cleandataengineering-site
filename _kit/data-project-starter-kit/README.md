# Data project starter kit

Templates and skills for the non-technical roles on a data project: business analyst, project manager, PMO, delivery manager, product owner, tester.
From cleandataengineering.ai/how-we-work/data-essentials/programme/. Free to use and change.

No code. Every file is plain text, so it can be kept in git, reviewed, and read by a person or by an AI assistant.

## How to start a project from this kit
1. Copy this folder and rename it to your project's name.
2. Put it in git (your team's repository tool). From now on, every change has an author, a reason and a reviewer.
3. Fill `templates/project-one-pager.md` and save it as `00-project/one-pager.md`.
4. For each template you need, copy it from `templates/` to the folder named at its top, and fill it there. Keep `templates/` blank.
5. Work through the stages: 1 Requirement received, 2 Rough estimate, 3 Discovery, 4 Discovery sign-off (gate), 5 MVP 1 starts, 6 Build, 7 Test, 8 Deploy, 9 Production sign-off (gate), 10 Project sign-off (gate).

## Folders
| Folder | What goes in it |
|---|---|
| `00-project/` | The one-pager, the cast and stakeholder map, the glossary. |
| `01-discovery/` | The source register, source questionnaires, interview notes. |
| `02-specs/` | Specs, metric definitions, source-to-target mapping. |
| `03-backlog/` | The Agile backlog and the estimate. |
| `04-run/` | Weekly status reports, the risk and dependency register, the decision log, meeting notes. |
| `05-test/` | The test and reconciliation plan, and the results. |
| `06-reviews/` | Review findings and sign-off records. |
| `07-handover/` | The consumer register, the runbook, the retrospective. |
| `templates/` | The blank templates. Do not fill them here. |
| `skills/` | The skills an AI assistant can follow. |

## Templates
| File | Template | Copy to | Owner |
|---|---|---|---|
| `templates/project-one-pager.md` | Project one-pager | `00-project/` | PM |
| `templates/cast-and-stakeholder-map.md` | Cast and stakeholder map | `00-project/` | PM |
| `templates/glossary.md` | Glossary | `00-project/` | BA |
| `templates/source-register.md` | Source register | `01-discovery/` | BA |
| `templates/source-questionnaire.md` | Source questionnaire | `01-discovery/` | BA |
| `templates/metric-definition.md` | Metric definition sheet | `02-specs/` | BA |
| `templates/spec.md` | Spec | `02-specs/` | BA |
| `templates/source-to-target-mapping.md` | Source-to-target mapping | `02-specs/` | BA |
| `templates/agile-backlog.md` | Agile backlog for a data project | `03-backlog/` | PM |
| `templates/estimate-sheet.md` | Estimate sheet | `03-backlog/` | Tech Anchor |
| `templates/risk-and-dependency-register.md` | Risk and dependency register | `04-run/` | PM |
| `templates/decision-log.md` | Decision log | `04-run/` | PM |
| `templates/weekly-status-report.md` | Weekly status report | `04-run/` | PM |
| `templates/meeting-notes.md` | Meeting notes | `04-run/` | Everyone |
| `templates/test-and-reconciliation-plan.md` | Test and reconciliation plan | `05-test/` | Tester |
| `templates/review-findings-log.md` | Review checklist and findings log | `06-reviews/` | PMO |
| `templates/sign-off-record.md` | Sign-off record | `06-reviews/` | PM |
| `templates/consumer-register.md` | Consumer register | `07-handover/` | BA |
| `templates/runbook-and-handover.md` | Runbook and handover | `07-handover/` | Tech Anchor |
| `templates/retrospective.md` | Retrospective | `07-handover/` | PM |
| `templates/agile-backlog.csv` | The same backlog as a sheet | `03-backlog/` | PM |

## Skills
A skill is a short written instruction, a template and a checklist that an AI assistant follows the same way every time.

| Folder | Skill | For |
|---|---|---|
| `skills/data-project-estimator/` | Data project estimator | Tech Anchor, PM, delivery manager |
| `skills/project-review/` | Project review | PMO, delivery manager, Tech Anchor |
| `skills/backlog-builder/` | Backlog builder | PM, BA, product owner |
| `skills/requirement-to-spec/` | Requirement to spec | BA |
| `skills/source-question-list/` | Source question list | BA, Tech Anchor |
| `skills/metric-definition-writer/` | Metric definition writer | BA, product owner |
| `skills/acceptance-check-reviewer/` | Acceptance check reviewer | BA, tester |
| `skills/source-to-target-mapping-draft/` | Source-to-target mapping draft | BA |
| `skills/glossary-keeper/` | Glossary keeper | BA |
| `skills/discovery-pack-summary/` | Discovery pack summary | BA, Tech Anchor |
| `skills/meeting-notes-to-actions/` | Meeting notes to actions and decisions | Everyone |
| `skills/weekly-status-report/` | Weekly status report | PM |
| `skills/risk-and-dependency-register/` | Risk and dependency register | PM, PMO |
| `skills/ready-checker/` | Ready checker | PM, BA |
| `skills/gate-pack-builder/` | Gate pack builder | PM, delivery manager |
| `skills/change-request-impact/` | Change request impact | PM, product owner |
| `skills/stakeholder-map/` | Stakeholder map and communication plan | PM, BA |
| `skills/test-and-reconciliation-plan-writer/` | Test and reconciliation plan writer | Tester |
| `skills/proposal-checker/` | Proposal and statement-of-work checker | Delivery manager, sponsor |
| `skills/handover-and-runbook-checker/` | Handover and runbook checker | Delivery manager |
| `skills/portfolio-health-roll-up/` | Portfolio health roll-up | PMO |
| `skills/template-and-skill-keeper/` | Template and skill keeper | PMO |
| `skills/lessons-learnt-collector/` | Lessons learnt collector | PMO, everyone |

### How to use a skill
- With an AI assistant that supports skills (for example Claude): add the skill's folder as a skill. In Claude Code, copy `skills/` to `.claude/skills/` in the project. Then ask in plain words, for example "estimate this project" or "review this project for the discovery gate".
- With any other AI assistant: open the skill's `SKILL.md`, paste it as your first message, then give it the files it asks for.
- Without AI: the steps and the checklist in each `SKILL.md` work as a checklist for a person.

### Rules
The result of a skill is a draft. A named person checks it and owns it.
Client data, personal data and secrets stay out of any tool the client has not approved.

## Improving the kit
When a project finds a better question, check or step, propose the change here, as a change for review. That is how the kit learns.
