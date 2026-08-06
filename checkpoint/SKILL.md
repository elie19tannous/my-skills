---
name: checkpoint
description: >
  Save the current dataset state with a structured DataLad commit so the Tracking chain is never
  left broken between work sessions. Trigger on "checkpoint", "save my work", "commit the current
  state", "wrap up this session", or at the end of a working session before switching context.
plane: workflow
stamped: [T]
delegates_to: [datalad]
---

# Skill: checkpoint

Take a clean, described snapshot of the dataset. This keeps the provenance chain continuous (a
dirty working tree produces misleading run records downstream). You delegate the save to the
**datalad doer**.

> v1 note: checkpoint is **on-demand** — invoked by the user or suggested by the coordinator. An
> automatic end-of-session `datalad save` (a `Stop`/session-end hook) is intentionally deferred:
> how often vs. how long to trigger it is a latency/tuning question that likely varies per study
> (plan gap B5), best decided after real use.

## When to use
- The user is pausing/ending a session, or wants intermediate state recorded.
- Do NOT use to record a provenanced *computation* — that is `analyze/run-comparison`
  (`container-run`), which already commits its own outputs. Checkpoint captures hand edits,
  notes, and other loose changes.

## Steps
1. **Inspect state** — delegate to the datalad doer:
   > "status: report modified/untracked files in this dataset and the current branch."
   If nothing is unsaved, tell the user there is nothing to checkpoint and stop.
2. **Compose a message** — summarize what changed since the last save into a meaningful `-m`
   (e.g. "checkpoint: draft stats.py + participant notes"). Ask the user if the change set is
   ambiguous.
3. **Save** — delegate to the datalad doer:
   > "save: `datalad save -m '<message>'` on the current branch."
4. **Log it** — append to `project.yaml`:
   `{ ts, op: checkpoint, stage: <current-stage>, note: "<message>", branch: <branch> }`.
5. **Report** — the commit sha and current branch.

## Constraints
- Delegate status and save to the datalad doer; never call datalad directly.
- Always use a meaningful message — never "wip"/"save"/placeholder.
- Keep `project.yaml` append-only.
- Do not force-save over a comparison mid-run; if a `container-run` is in progress, let it finish
  (it commits its own outputs).
