---
name: run-pipeline
description: >
  Run a nipoppy processing pipeline (fMRIPrep, MRIQC, ...) on a dataset's BIDS data with full
  DataLad provenance, then record completion status. Trigger on "run fmriprep", "run mriqc",
  "process the dataset", "run the pipeline", "run a nipoppy pipeline", "process participants with
  provenance". This is the Stage-8 (Process) entry point — nipoppy commands invoked *with* datalad.
plane: workflow
stamped: [A, T, P, E]
delegates_to: [nipoppy, datalad]
---

# Skill: run-pipeline

Execute a nipoppy processing pipeline so the computation is **provenanced**: nipoppy provides the
containerized pipeline invocation (Boutiques + Apptainer → Portability/Ephemerality), and DataLad
wraps it (`datalad run`) so inputs, command, and outputs are recorded (Actionability + Tracking).
You never run tools yourself — you orchestrate two doers: the **nipoppy doer** constructs and
validates the command; the **datalad doer** runs it with provenance.

> Design note: nipoppy alone does not record provenance and datalad does not know pipeline
> mechanics — so this planner joins them. The nipoppy command is always executed *through*
> `datalad run`; a bare `nipoppy process` is never the final step. (The container image itself is
> pinned by nipoppy's `config.json` + Boutiques descriptor, so datalad's own `container-run`
> image-capture is not needed here — nipoppy owns that layer.)

## When to use
- A nipoppy dataset (`config.json` + `manifest.tsv`) exists with BIDS data ready, and the user
  wants to run a processing pipeline.
- Do NOT use to create/curate the dataset (that is nipoppy `init`/`bidsify` — a future `curate`
  planner) or to run a bespoke analysis script (that is `analyze/run-comparison`).

## Steps
1. **Confirm pipeline + context** — determine the `--pipeline`, `--pipeline-version`, and
   optional `--pipeline-step` / `--participant-id` / `--session-id` from the user. If the pipeline
   or version is unspecified, ask (never guess a version).
2. **Validate + construct (nipoppy doer)** — delegate:
   > "Validate this nipoppy dataset (config.json, manifest.tsv, Linux+Apptainer, pipeline version
   > matches a pulled image) and construct the `nipoppy process --pipeline <X> --pipeline-version
   > <V> [...]` command; run it once with `--simulate` to preview, and return the exact command
   > plus the inputs it reads and outputs it writes."
   Expect a structured result with `command`, `inputs`, `outputs`, `run_via: datalad-run`. If it
   returns `result: failed` (state/platform gap), relay the fix and stop.
3. **Ensure a clean tree (datalad doer)** — `datalad run` requires a clean tree:
   > "status: report modified/untracked files and the current branch."
   If dirty, route to `analyze/checkpoint` first (or have the user confirm), then continue.
4. **Run with provenance (datalad doer)** — delegate the execution:
   > "run: `datalad run -m '<pipeline> <version> on <scope>'` with inputs `<-i from step 2>` and
   > outputs `<-o from step 2, e.g. derivatives/<pipeline>, proc/logs/<pipeline>>`, command
   > `'<the nipoppy process command>'`."
   Wait for the doer's structured result (commit sha, recorded outputs, pass/fail). On failure,
   relay the doer's error and the nipoppy log path; nothing was committed. Stop.
5. **Record completion (nipoppy doer → datalad doer)** — after a successful run:
   > nipoppy doer: "track-processing for `<pipeline>` to update `tabular/bagel.tsv`."
   > then datalad doer: "save: `datalad save -m 'track-processing: <pipeline> <version>'`."
6. **Log it** — append to `project.yaml`:
   `{ ts, op: run-pipeline, stage: process, note: "datalad run nipoppy process <pipeline> <version>
   on <scope>; commit <sha>; outputs <paths>", branch: <branch> }`.
7. **Report** — the pipeline/version/scope, the provenance commit, output derivatives, updated
   bagel status, and that the run is replayable via the datalad doer (`datalad rerun`). Suggest the
   next step (`nipoppy extract` for IDPs, or `analyze/propose-comparison`).

## Constraints
- Always execute the nipoppy command through the datalad doer's `datalad run` — never let a
  dataset-mutating `nipoppy process`/`bidsify`/`extract` run bare. Provenance is the whole point.
- Require a meaningful `-m` message that names the pipeline, version, and scope; never a placeholder.
- Declare inputs/outputs from the nipoppy doer's report — do not invent paths. Prefer the pipeline's
  own `derivatives/<pipeline>` and `proc/logs/<pipeline>` as `-o`; leave `scratch/` untracked.
- Do not diagnose or "fix" the pipeline's science — if a container errors on its own logic, surface
  the nipoppy log to the user; the harness owns provenance, not the pipeline internals.
- Keep `project.yaml` append-only; log both successful and (as a note) failed runs if useful.
