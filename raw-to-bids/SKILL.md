---
name: raw-to-bids
description: >
  Convert raw imaging data (DICOMs) into a BIDS-valid layout with full DataLad provenance, via
  nipoppy's containerized converter. Trigger on "convert to BIDS", "bidsify", "dcm2bids",
  "heudiconv", "raw DICOMs to BIDS", "organize raw data", "curate the raw imaging". This is the
  Stage-2 (Curate) ingest step — getting raw data *into* the dataset before annotate/process.
plane: workflow
stamped: [S, A, T, P, E]
delegates_to: [nipoppy, datalad]
---

# Skill: raw-to-bids

Get raw imaging data into a standardized, **self-contained BIDS** layout so everything downstream
(annotate, process, analyze) has a canonical structure to work from — and do it **provenanced**:
nipoppy runs the containerized converter (dcm2bids / HeuDiConv / BIDScoin → Portability/Ephemerality)
and DataLad wraps it (`datalad run`) so inputs, command, and outputs are recorded. You orchestrate
two doers: the **nipoppy doer** constructs/validates the `bidsify` command; the **datalad doer**
runs it with provenance. You never run tools yourself.

> Design note: like `process/run-pipeline`, the nipoppy command is executed *through* `datalad run`
> — a bare `nipoppy bidsify` is never the final step. The converter container is pinned by nipoppy's
> `config.json` + Boutiques, so datalad's own `container-run` image-capture is not needed here.

## When to use
- A nipoppy dataset (`config.json` + `manifest.tsv`) has raw DICOMs staged (post-reorg) and needs
  BIDS conversion.
- Do NOT use to run a processing pipeline (`process/run-pipeline`), to add descriptive metadata to
  an already-BIDS dataset (`curate/annotate`), or to initialize a project (`project/new-project`).

## Steps
1. **Confirm readiness** — determine the converter (`--pipeline` name/version as configured) and
   any `--participant-id` / `--session-id` scope from the user. Raw data must be staged where
   nipoppy expects it (post-reorg); if it is not, direct the user to nipoppy `reorg` first.
2. **Validate + construct (nipoppy doer)** — delegate:
   > "Validate this nipoppy dataset (config.json, manifest.tsv, Linux+Apptainer, converter version
   > matches a pulled image) and construct the `nipoppy bidsify [--pipeline ... scope ...]` command;
   > run it once with `--simulate` to preview, and return the exact command plus the inputs it reads
   > (sourcedata/post-reorg) and outputs it writes (`bids/`)."
   If it returns `result: failed` (state/platform gap), relay the fix and stop.
3. **Ensure a clean tree (datalad doer)** — `datalad run` requires a clean tree:
   > "status: report modified/untracked files and the current branch."
   If dirty, route to `analyze/checkpoint` first.
4. **Run with provenance (datalad doer)** — delegate:
   > "run: `datalad run -m 'bidsify <converter> on <scope>'` with inputs `<-i from step 2>` and
   > outputs `<-o from step 2, e.g. bids/>`, command `'<the nipoppy bidsify command>'`."
   Wait for the structured result (commit sha, recorded outputs, pass/fail). On failure, relay the
   doer's error + the nipoppy log path; nothing was committed. Stop.
5. **Update curation status (nipoppy doer → datalad doer)** — after success:
   > nipoppy doer: "track-curation to update `tabular/curation_status.tsv` after bidsify."
   > then datalad doer: "save: `datalad save -m 'track-curation: post-bidsify'`."
6. **Log it** — append to `project.yaml`:
   `{ ts, op: raw-to-bids, stage: curate, note: "datalad run nipoppy bidsify <converter> on <scope>; commit <sha>; outputs bids/", branch: <branch> }`.
7. **Report** — the converter/scope, the provenance commit, the `bids/` output, and the next step:
   `curate/annotate` to enrich metadata, or `process/run-pipeline` to process the BIDS data.
   Suggest `govern/qc-review` (bids-validator) to confirm BIDS validity.

## Constraints
- Always execute the converter through the datalad doer's `datalad run` — never let a
  dataset-mutating `nipoppy bidsify` run bare. Provenance is the point.
- Require a meaningful `-m` message naming the converter and scope; never a placeholder.
- Declare inputs/outputs from the nipoppy doer's report — do not invent paths.
- Do not hand-edit `manifest.tsv` or restructure the raw data yourself — nipoppy owns the layout.
- Keep `project.yaml` append-only and schema-valid; delegate every tool operation to a doer.
