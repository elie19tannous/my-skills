---
name: preregister
description: >
  Freeze a comparison's specification before execution and register it externally (OSF
  Registrations / ClinicalTrials.gov / PROSPERO), recording a confirmatory obligation in the ledger.
  Trigger on "preregister", "pre-register this comparison", "freeze the analysis plan", "register
  the hypothesis", "confirmatory analysis", "lock the spec before running". This is the right end of
  the rigor spectrum for analyze/propose-comparison — the frozen spec becomes a tracked obligation.
plane: workflow
stamped: [S, T, A]
delegates_to: [datalad]
---

# Skill: preregister

Turn a comparison into a **confirmatory** one: freeze its specification *before* any data is
analyzed, register that spec with an external registry, and record it as an outstanding
**obligation** in the ledger. The frozen spec is the STAMPED spec-centric research object
(Self-contained, Tracked, Actionable) — the durable thing; the later run is Ephemeral and is checked
*against* this spec. You own the freeze/registration judgment; you delegate the save to the
**datalad doer**.

> This is the confirmatory path of `analyze/propose-comparison`. A "preregistration" recorded *after*
> looking at the outcome is not one — the freeze must precede execution. `analyze/run-comparison`
> then checks results against the registered spec and any deviation is reportable.

## When to use
- A comparison should be confirmatory: its hypothesis, inputs, and analysis plan are to be frozen
  and registered before running (often right after `propose-comparison` picks the confirmatory mode).
- Do NOT use for exploratory quick queries (just `propose-comparison`), or to execute the analysis
  (`run-comparison`), or to resolve/track existing obligations (`govern/obligations`).

## Steps
1. **Freeze the spec** — capture the immutable specification for the comparison's `cmp/<slug>`
   branch: `what` (hypothesis), `why`, `inputs`, `expected_outputs`, and the **analysis plan**
   (model, primary outcome, exclusions, corrections). Write it as a durable, versioned file
   (e.g. `code/prereg/<slug>.md`) so the frozen text is itself tracked. Confirm with the user that
   this is final — after registration it does not change.
2. **Register externally** — guide the user to submit the frozen spec to the appropriate registry
   (OSF Registrations, ClinicalTrials.gov, PROSPERO for systematic reviews) and obtain the
   registration **id/URL**. The harness records the reference the user provides; it does not
   fabricate or auto-submit one. If registration is pending, record the obligation as `pending`
   with no `ref` yet and note that the ref must be added once assigned.
3. **Record the obligation** — add to `project.yaml` `obligations[]` (per `docs/project-ledger.md`):
   `{ id: prereg-<slug>, kind: preregistration, description: "<what>; frozen for cmp/<slug>",
   due: <optional date>, status: pending, ref: <registration URL or omit> }`.
4. **Log it** — append `{ ts, op: preregister, stage: govern, note: "froze + registered cmp/<slug> (<ref>)", branch: cmp/<slug> }`.
5. **Save** — delegate to the **datalad doer**: "save: `datalad save -m 'preregister cmp/<slug>: freeze spec + register (<ref>)'`."
6. **Report** — the frozen spec path, the registration ref (or that it is pending), the new pending
   obligation, and that `run-comparison` must check outcomes against this spec — deviations are
   reportable. The obligation is discharged (via `govern/obligations`) once the confirmatory
   comparison is completed as specified.

## Constraints
- Freeze precedes execution — never "preregister" a comparison whose outcome has already been seen;
  if it has, record it honestly as exploratory (`propose-comparison`), not confirmatory.
- The frozen spec is immutable after registration — a change means a new comparison + a new
  registration, recorded as such.
- Never fabricate a registration id/URL — record only what the registry actually assigned.
- Add the obligation per the ledger conventions; keep `log:` append-only and the ledger
  schema-valid. Delegate the save to the datalad doer.
