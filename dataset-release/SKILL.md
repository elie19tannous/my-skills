---
name: dataset-release
description: >
  Cut a citable, versioned release of a product: bump the version, write a BIDS CHANGES entry, tag
  the exact state with datalad, and (optionally) mint a DOI. Trigger on "release the dataset",
  "cut a release", "tag a version", "make a citable version", "mint a DOI", "publish version 1.0",
  "release the paper's data". This turns a grouped product (from analyze/manage-product) into a
  fixed, referenceable version — the step before cross-linking multiple products.
plane: workflow
stamped: [D, M]
delegates_to: [datalad, archive]
---

# Skill: dataset-release

Freeze a **product** at a named version so it can be cited and cross-linked: a version bump, a BIDS
`CHANGES` entry, an immutable datalad **version tag**, and — when credentials exist — a minted
**DOI**. A release is a durable, resolvable pointer to one exact state (Distributability) with a
citable record (Metadata). You own the release judgment; you delegate tagging/saving to the
**datalad doer** and DOI minting to the **archive doer**.

> Scope note: the version + `CHANGES` + tag path is always available and fully provenanced. DOI
> minting is the gated add-on — the archive doer returns `result: unminted` (not a fake DOI) when no
> Zenodo/OSF/DataCite credential is configured, and the release still completes. Push the tagged
> state to a sibling/archive via `disseminate/publish`.

## When to use
- A product exists in the ledger `products[]` (via `analyze/manage-product`) and is ready to be
  fixed at a version — a dataset release, a paper's data/outputs snapshot, a report.
- Do NOT use to group comparisons (`analyze/manage-product`), to push working state to a sibling
  (`disseminate/publish`), or to cross-link products (`disseminate/link-outputs`).

## Steps
1. **Identify the product + version** — get the product `id` from `products[]` and the new version
   (semver, e.g. `1.0.0`; suggest the next bump and confirm). A version is immutable once tagged —
   never re-tag an existing version; cut a new one.
2. **Ensure a clean tree (datalad doer)** — a release must tag committed state:
   > "status: report modified/untracked files and the current branch."
   If dirty, route to `analyze/checkpoint` first.
3. **Write release metadata** — at the dataset root:
   - prepend a **BIDS `CHANGES`** entry: `<version> <YYYY-MM-DD>` followed by bulleted notes.
   - record the version where the dataset expects it; once a DOI is minted, set
     `dataset_description.json` `"DatasetDOI"`.
4. **Tag the release (datalad doer)** — delegate a tagged save:
   > "save with a version tag: `datalad save -m 'release <id> v<version>' --version-tag v<version>`."
   This creates the immutable, provenanced release point.
5. **Mint a DOI (archive doer, gated)** — delegate:
   > "mint a DOI for tag `v<version>` of product `<id>` (backend auto: OSF/Zenodo/DataCite)."
   - `result: ok` → capture the `doi`; set it in `dataset_description.json` and (step 6) the ledger.
   - `result: unminted` → proceed without a DOI; report how to enable minting. Never invent one.
6. **Update the ledger** — set the product's `status: released`; append any minted DOI to the
   product's `dois[]` (per `docs/project-ledger.md`); append a log entry
   `{ ts, op: dataset-release, stage: disseminate, note: "released <id> v<version>; doi <doi|none>", branch: <branch> }`.
   Delegate the save to the datalad doer (a plain `datalad save`, tree already tagged).
7. **Report** — the product, version, tag, `CHANGES` entry, DOI (or "unminted — set ZENODO_TOKEN /
   datalad-osf to mint"), and the next step: `disseminate/publish` to push the tag to a
   sibling/archive, then `disseminate/link-outputs` to link this release to other products.

## Constraints
- Tag committed state only (clean tree); a version tag is immutable — never move or reuse it.
- Never fabricate a DOI — a DOI enters the ledger/metadata only when the archive doer returns one.
- Every release is a datalad version tag so the exact state is reproducible via `datalad` from the
  tag; do not create releases as plain files without a tag.
- `products[]` is upserted (status → `released`) and `dois[]` appended per the ledger conventions;
  keep `log:` append-only and the ledger schema-valid (`schemas/project.schema.json`).
- Delegate every tag/save to the datalad doer and every deposit/mint to the archive doer — never
  call git/datalad or an archive API directly.
