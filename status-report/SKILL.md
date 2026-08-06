---
name: status-report
description: >
  Generate a human-readable status/progress report for the project from the ledger — study header,
  products and their release/DOI state, outstanding obligations, contributors, and recent activity.
  Trigger on "status report", "progress report", "where is the project", "generate PROJECT.md",
  "funder report", "project summary", "catch me up in writing". Produces a report from project.yaml;
  it never hand-edits the ledger.
plane: workflow
stamped: [M]
delegates_to: [datalad]
---

# Skill: status-report

Turn the ledger into a readable report. `project.yaml` is the machine-actionable source of truth;
this skill renders a `PROJECT.md` (or a funder/progress report) *from* it so people can read the
project's state without parsing YAML. The report is generated, never hand-edited — edits go to the
ledger via the owning skills. You delegate the ledger read and the save to the **datalad doer**.

> Distinct from the `coordinator` agent: the coordinator gives a fast interactive "where am I / what's
> next" on load; status-report produces a durable, shareable written artifact (PROJECT.md / a funder
> report) committed to the dataset.

## When to use
- The user wants a written summary, a `PROJECT.md`, or a progress/funder report.
- Do NOT use to change project state — this only reads the ledger and renders it. To record a
  decision use `project/log-decision`; to credit people use `project/people`.

## Steps
1. **Read the ledger (datalad doer)** — delegate: "read `project.yaml` and report its `project`,
   `products`, `obligations`, `contributors`, and recent `log` entries." Optionally include
   `datalad log` highlights for the provenance section.
2. **Render the report** — write `PROJECT.md` (or the requested report path) with:
   - **Overview** — study name/description, current stage (from the last log op), branch.
   - **Products** — each product: kind, status, comparisons, outputs, DOIs, relations.
   - **Obligations** — pending (highlight due/overdue), met, waived.
   - **People** — contributors with CRediT roles + ORCIDs.
   - **Recent activity** — the last several log entries.
   Fill only from the ledger; mark anything absent (e.g. "no DOI — unreleased"), do not invent.
3. **Register + log** — append `{ ts, op: status-report, stage: manage, note: "rendered <path>", branch: <branch> }`.
4. **Save** — delegate to the datalad doer: "save: `datalad save -m 'status-report: render <path>'`."
5. **Report** — the report path and a one-line summary of project state.

## Constraints
- Generated, not authored: `PROJECT.md` is rendered from the ledger and should not be hand-edited;
  never write project state *into* the report that is not in the ledger.
- Render only what the ledger contains; mark gaps rather than filling them.
- Keep `log:` append-only and the ledger schema-valid; delegate reads/saves to the datalad doer.
