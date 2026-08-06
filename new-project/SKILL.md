---
name: new-project
description: >
  Scaffold a new neuroimaging research project as a YODA-structured DataLad dataset with a
  plain BIDS layout, a basic analysis container recipe, and a project.yaml activity log.
  Trigger on "start a new project", "new study", "scaffold a project", "initialize a dataset",
  "set up a research project". This is the Stage-1 (Initialize) entry point.
plane: workflow
stamped: [S, M, T, P, E]
delegates_to: [datalad]
---

# Skill: new-project

Stand up a reproducible project skeleton in one pass: a DataLad dataset (Tracking + Modularity),
a plain BIDS layout (Self-containment), and a pinned container recipe (Portability + Ephemerality).
You own the *what/why*; you delegate every DataLad operation to the **datalad doer** subagent.

## When to use
- The user is starting a new study / analysis project and has no dataset yet.
- Do NOT use to add an analysis to an existing project — that is `analyze/propose-comparison`.

## Steps
1. **Gather project info** (ask; keep it short):
   - `short_name` (kebab-case, used as the directory name)
   - one-line study description
   - primary language/stack (Python / R) — for the container recipe
   - *(optional)* expected preprocessing pipelines (fMRIPrep, MRIQC, …) — recorded as notes only
     in v1 (Nipoppy wiring is deferred).

2. **Create the YODA dataset** — delegate to the **datalad doer**:
   > "Create a YODA DataLad dataset at `./<short_name>` with the text-to-git procedure
   > (`datalad create -c text2git -c yoda --description '<description>'`)."
   YODA gives `code/`, `inputs/`, `outputs/`, `README.md`. The **`text2git`** procedure is
   important: under YODA's default `.gitattributes` everything except `code/**` and `*.md`/`*.txt`
   is annexed — which turns `project.yaml` and BIDS metadata (`dataset_description.json`,
   `*.tsv`, `*.json` sidecars) into **read-only annex symlinks the planner cannot append to**.
   `text2git` keeps text files in git (writable + diffable) while binary data (NIfTI, etc.) still
   annexes. Confirm `.datalad/` exists before continuing.

3. **Overlay a plain BIDS skeleton** at the dataset root (write these yourself; they are small
   text files that YODA stores in git):
   - `dataset_description.json` — `{"Name": "<description>", "BIDSVersion": "1.9.0",
     "DatasetType": "raw"}`
   - `participants.tsv` — header row `participant_id` (+ any known columns)
   - `README` — study summary + how the dataset is organized
   - `.bidsignore` — ignore non-BIDS helpers (`code/`, `outputs/`, `containers/`)
   - `derivatives/` — where BIDS-derivative outputs land (keep a `.gitkeep`)
   Raw BIDS data lives at the dataset root; `outputs/`/`derivatives/` hold results; `inputs/`
   holds linked source subdatasets (YODA P1). Do not copy raw data in by hand.

4. **Scaffold a basic analysis container recipe** in `containers/` (recipe only; building/
   registration happens on the first `analyze/run-comparison`):
   - Python → `environment.yml` (pin interpreter + core scientific stack) and a minimal
     `Dockerfile`/`Apptainer.def` built from it.
   - R → an `renv.lock` stub + equivalent container def.
   Note in the README that analyses run via `datalad container-run` (Portability + Ephemerality).

5. **Initialize the project ledger** — write `project.yaml` at the dataset root using the shape
   below, with one `new-project` log entry and empty `products:` / `obligations:` lists (later
   skills populate them). Follow the conventions in `docs/project-ledger.md`; the structure is
   validated by `schemas/project.schema.json`.

6. **Save everything** — delegate to the **datalad doer**:
   > "Save the new-project scaffold: `datalad save -m 'scaffold YODA+BIDS project <short_name>'`."

7. **Report** — dataset path, what was created, and the suggested next step
   (`analyze/propose-comparison`, or link input data with the datalad doer).

## `project.yaml` shape (the ledger)
Validated by `schemas/project.schema.json`; conventions in `docs/project-ledger.md`. `new-project`
writes the header + first log entry and seeds empty `products`/`obligations` (populated later by
`analyze/manage-product`, `disseminate/*`, and `govern/*`).
```yaml
project:
  name: <short_name>
  description: <one-line description>
  created: 2026-07-10T14:30:00Z
  dataset_root: .
  stack: python            # python | R | other
products: []               # named deliverables — grouped from kept comparisons later
obligations: []            # Manage & Comply commitments (pre-registrations, DMP/ethics/funder)
log:
  # append-only; never rewrite or reorder prior entries
  - { ts: 2026-07-10T14:30:00Z, op: new-project, stage: initialize,
      note: "scaffolded YODA+BIDS dataset + container recipe", branch: main }
```

## Constraints
- Never run DataLad commands yourself — delegate creation and save to the datalad doer.
- Keep `project.yaml` append-only and schema-valid (`schemas/project.schema.json`). The
  `new-project` entry is the first log line; `products`/`obligations` start empty.
- BIDS files are the only thing this skill writes directly; everything provenance-related goes
  through the doer so the very first commit is properly tracked.
- Container building is deferred to first run — scaffold the recipe, don't build it here.
