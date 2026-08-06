---
name: log-decision
description: >
  Record a design or analysis decision — what was decided, why, and the alternatives considered — as
  a durable entry in the project log. Trigger on "log this decision", "record why we chose", "decision
  log", "note the rationale", "document this choice", "we decided to". Captures the reasoning behind
  choices so the project's history explains itself.
plane: workflow
stamped: [T]
delegates_to: [datalad]
---

# Skill: log-decision

Capture the *why* behind a choice so future-you (or a collaborator, or a reviewer) can reconstruct
the reasoning, not just the result. Decisions are recorded as tracked log entries in the ledger —
provenance for judgment, alongside the provenance for computation. You delegate the save to the
**datalad doer**.

## When to use
- A non-obvious methodological or design choice was made (a model, an exclusion criterion, a tool,
  dropping/keeping a comparison) and its rationale should be preserved.
- Do NOT use to record a computation (`analyze/run-comparison` already provenances that) or to make
  a formal commitment (`govern/preregister` / `govern/obligations`).

## Steps
1. **Capture the decision** — get: the `decision` (what was chosen), the `rationale` (why), the
   `alternatives` considered and why they were not chosen, and the `scope` (which branch/comparison/
   product it affects, if any).
2. **Append to the log** — one entry to `project.yaml` `log[]`:
   `{ ts, op: log-decision, stage: manage, note: "DECISION: <decision> — WHY: <rationale> — ALT: <alternatives>", branch: <branch> }`.
   Keep the note self-contained so the reasoning is legible from the log alone.
3. **Save** — delegate to the datalad doer: "save: `datalad save -m 'log-decision: <short decision>'`."
4. **Report** — confirm the decision was recorded and on which branch.

## Constraints
- Record the decision *and* its rationale and alternatives — a decision without its "why" is not
  worth logging; do not reduce it to a bare statement.
- Record honestly: capture the actual reasoning, including trade-offs, not a post-hoc justification.
- `log:` is append-only — a reversed decision is a *new* log-decision entry referencing the prior
  one, never an edit of it. Keep the ledger schema-valid; delegate the save to the datalad doer.
