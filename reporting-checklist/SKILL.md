---
name: reporting-checklist
description: >
  Apply the right reporting guideline to a manuscript product — an EQUATOR checklist (CONSORT,
  STROBE, PRISMA, ARRIVE) or, for neuroimaging, COBIDAS — and record item-by-item compliance.
  Trigger on "reporting checklist", "CONSORT", "STROBE", "PRISMA", "ARRIVE", "COBIDAS", "reporting
  guideline", "is the paper compliant", "checklist for submission". Produces a completed checklist
  artifact for the product.
plane: workflow
stamped: [M]
delegates_to: [datalad]
---

# Skill: reporting-checklist

Attach the correct reporting guideline to a manuscript and work through it item by item, so the
paper meets the standard its study type requires and the checklist ships with submission. This is
completeness **Metadata** — a machine-and-reviewer-checkable record of what the paper reports. You
delegate the save to the **datalad doer**.

Load `plugins/disseminate/references/equator-guidelines.md` to pick the right guideline before
starting.

## When to use
- A manuscript product exists (`disseminate/draft-manuscript`) and needs a reporting-guideline pass,
  typically before submission.
- Do NOT use to write the manuscript (`draft-manuscript`) or to release/cite it (`dataset-release`).

## Steps
1. **Pick the guideline** — from the study design (see the reference): RCT → **CONSORT**;
   observational → **STROBE**; systematic review/meta-analysis → **PRISMA**; animal research →
   **ARRIVE**; neuroimaging methods reporting → **COBIDAS**. Confirm with the author if ambiguous.
2. **Instantiate the checklist** — write `manuscript/checklists/<guideline>.md` with each item and a
   status (`reported: <section/page>` | `not-applicable: <why>` | `TODO`). Pre-fill items the harness
   can evidence from the manuscript + ledger (e.g. data-availability, provenance, registration/
   pre-registration from `obligations[]`); leave the rest `TODO` for the author.
3. **Register + log** — add the checklist path to the product's `outputs[]`; append
   `{ ts, op: reporting-checklist, stage: disseminate, note: "<guideline> checklist for <id>", branch: <branch> }`.
4. **Save** — delegate to the datalad doer: "save: `datalad save -m 'reporting-checklist: <guideline> for <id>'`."
5. **Report** — the guideline chosen, how many items are satisfied vs. `TODO`, and the gaps the
   author must close before submission (e.g. a missing pre-registration → `govern/preregister`).

## Constraints
- Choose the guideline by study design, not convenience; when in doubt, ask.
- Mark an item `reported` only with a real section/page pointer — never claim compliance you cannot
  evidence; unknowns stay `TODO`.
- Record the checklist under the product's `outputs[]`; keep `log:` append-only and the ledger
  schema-valid. Delegate the save to the datalad doer.
