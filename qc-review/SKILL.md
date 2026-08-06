---
name: qc-review
description: >
  Run the Stage-5 quality/review pass: validate the dataset against BIDS and produce a lightweight
  STAMPED self-assessment of the project's reproducibility posture. Trigger on "qc", "quality check",
  "review the dataset", "is this BIDS-valid", "validate the dataset", "reproducibility audit",
  "STAMPED assessment", "check the dataset before release". Read-only review — it reports gaps and
  recommends the skill that closes each; it does not change the dataset.
plane: workflow
stamped: [S]
delegates_to: [bids, datalad]
---

# Skill: qc-review

Assess whether the dataset is in good shape to build on and release: is it **BIDS-valid**
(Self-containment), and how does the project score across STAMPED? This is a read-only review that
turns the current state into a short report with concrete next actions. You delegate validation to
the **bids doer** and state inspection to the **datalad doer**; you do not modify anything.

## When to use
- Before grouping/releasing a product, at the end of curation, or whenever the user wants a quality
  or reproducibility check.
- Do NOT use to fix issues — this skill only diagnoses. It routes each gap to the skill that fixes
  it (`curate/annotate`, `curate/raw-to-bids`, `analyze/checkpoint`, `disseminate/publish`, …).

## Steps
1. **BIDS validation (bids doer)** — delegate:
   > "validate this dataset against BIDS and report result (valid/invalid/unverified), error and
   > warning counts, and any dataset_description/participants/sidecar gaps."
   Relay the summary. If the validator is absent, report `unverified` with the install hint — never
   claim validity that was not checked.
2. **State inspection (datalad doer)** — delegate a read-only check:
   > "status + log: is the working tree clean, what is the current branch, is a sibling configured?"
3. **STAMPED self-assessment** — from the bids result, the datalad state, and the ledger
   (`project.yaml`), score each letter and name the gap-closing skill:
   - **S** self-contained → BIDS valid + `dataset_description.json`/`README` present (`curate/*`)
   - **T** tracked → working tree clean, runs recorded (`analyze/checkpoint`, `run-comparison`)
   - **A** actionable → analyses are provenanced `datalad run`s, not ad-hoc shell
   - **M** metadata → data dictionary / sidecars / controlled terms present (`curate/annotate`)
   - **P/E** portable/ephemeral → a container recipe exists and analyses run in it
     (`process/run-pipeline`, `run-comparison`)
   - **D** distributable → a sibling exists / a product is released (`disseminate/publish`,
     `dataset-release`)
4. **Log it** — append `{ ts, op: qc-review, stage: qc, note: "bids <result>; STAMPED gaps: <letters>", branch: <branch> }`, then delegate the save to the datalad doer.
5. **Report** — a compact scorecard: BIDS result (errors/warnings), the STAMPED letters that are
   satisfied vs. the gaps, and for each gap the single skill that closes it. Recommend the highest
   priority next action.

## Constraints
- Read-only: never modify, rename, or "fix" dataset files here — diagnose and route to the fixing
  skill. Validation and state inspection go through the bids and datalad doers respectively.
- Never assert BIDS validity the bids doer did not verify (an absent validator is `unverified`, not
  a pass).
- The STAMPED assessment is a snapshot, not a gate — report it plainly with gaps; do not block other
  work. Keep `log:` append-only and the ledger schema-valid.
