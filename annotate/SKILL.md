---
name: annotate
description: >
  Enrich a dataset's metadata so it is self-describing and machine-queryable — complete
  dataset_description.json, generate a participants.json data dictionary, fill BIDS sidecars,
  and (optionally) annotate phenotypic variables / assessments with controlled terms
  (Neurobagel/SNOMED, ReproSchema, NIDM). Trigger on "annotate", "add metadata", "describe the
  dataset", "data dictionary", "annotate variables", "standardize variable names", "add sidecars",
  "make this dataset self-describing". This advances the Metadata (M) and Actionable (A) of STAMPED.
plane: workflow
stamped: [M, A]
delegates_to: [datalad]
---

# Skill: annotate

Make the dataset **Metadata-rich (M)** and **Actionable (A)**: fill in the descriptive and
controlled-vocabulary metadata that lets a human — or an agent — understand and query the data
without opening the raw files. Every metadata edit is a file in the dataset, so you keep it
**provenanced** by delegating the save to the **datalad doer**; you never annotate off to the side.

> Scope note: the v1-workable core is BIDS/dataset-level metadata — `dataset_description.json`, a
> `participants.json` data dictionary, and BIDS sidecars — which need no extra tools and are fully
> provenanced. Controlled-term annotation against external vocabularies (Neurobagel/`bagel-cli`,
> SNOMED, ReproSchema, NIDM/`pynidm`) is the richer add-on: those are capability-plane tools
> (a future `annotate` doer). Until those doers exist, construct the annotation, cite the source
> term explicitly, and still datalad-save the result — never fabricate a code.

## When to use
- Data is in (or near) BIDS form and needs describing: missing/thin `dataset_description.json`,
  `participants.tsv` columns with no data dictionary, imaging files without sidecar metadata, or
  phenotypic variables that should carry standard terms.
- Do NOT use to convert raw data to BIDS (that is a `curate` conversion step / nipoppy `bidsify`)
  or to run a pipeline (`process/run-pipeline`). Annotate describes; it does not compute.

## Steps
1. **Survey current metadata (datalad doer for state)** — inspect what exists: is
   `dataset_description.json` present and complete (Name, BIDSVersion, Authors, License,
   DatasetType)? Does every non-id column in `participants.tsv` have an entry in
   `participants.json`? Which imaging files lack sidecars? Report the gaps before editing.
2. **Dataset-level metadata** — complete `dataset_description.json` (authorship, license, funding,
   references) and any BIDS top-level files (`README`, `CHANGES`). Ask the user for anything you
   cannot derive (authors, license) — do not invent authorship.
3. **Data dictionary** — for each `participants.tsv` column (and other phenotypic `.tsv`s), add a
   `participants.json` entry with `Description`, `Units`, and `Levels` for categoricals. This is
   the highest-value, always-available annotation (M) and makes the columns queryable (A).
4. **BIDS sidecars** — fill/extend JSON sidecars for imaging data as needed (task, acquisition,
   units). Keep edits BIDS-valid; suggest running `bids-validator` after.
5. **Controlled-term annotation (optional, richer M/A)** — when the user wants standardized
   vocabularies, map variables/assessments to controlled terms:
   - phenotypic variables → Neurobagel (`bagel-cli`) / SNOMED codes
   - behavioral assessments/questionnaires → ReproSchema
   - neuroimaging annotation & provenance → NIDM (`pynidm`)
   Look up or confirm each term with the user; **never guess a code**. (These tool invocations
   will delegate to the `annotate` capability doer once it exists; for now, record the mapping and
   its source in the metadata.)
6. **Provenance the edits (datalad doer)** — delegate the save so the annotation is tracked:
   > "save: `datalad save -m 'annotate: <what was added, e.g. participants.json data dictionary +
   > dataset_description authors>'`."
7. **Log it** — append to `project.yaml`:
   `{ ts, op: annotate, stage: curate, note: "<metadata added>", branch: <branch> }`.
8. **Report** — what was annotated, what controlled-term coverage exists vs. remains, and suggest
   `bids-validator` and (when ready) pushing a Neurobagel graph.

## Constraints
- Delegate the save to the datalad doer so metadata is provenanced — never leave annotation edits
  uncommitted, and never call `datalad` directly.
- Never fabricate controlled-vocabulary codes (SNOMED/Neurobagel/NIDM/ReproSchema) or authorship —
  look them up or ask; cite the source of every term.
- Keep edits BIDS-valid; a data dictionary or sidecar that breaks the schema is worse than none.
  Recommend `bids-validator` rather than asserting validity.
- Do not restructure or rename data files here — annotation describes existing data; renaming is a
  curation/conversion concern.
- Keep `project.yaml` append-only.
