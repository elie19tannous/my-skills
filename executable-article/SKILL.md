---
name: executable-article
description: >
  Scaffold a NeuroLibre-style reproducible preprint for a product: a MyST/Jupyter Book that rebuilds
  its figures from the provenanced data and the project's container environment. Trigger on
  "executable article", "reproducible preprint", "NeuroLibre", "MyST article", "living paper",
  "make the figures reproducible". Produces an article-kind living product.
plane: workflow
stamped: [A, P, E]
delegates_to: [datalad]
---

# Skill: executable-article

Turn a product into a **re-executable article** — figures regenerate from the provenanced outputs in
the project's pinned container, rather than being pasted in. That makes the paper Actionable
(re-runs) and Portable/Ephemeral (rebuilt from spec). You delegate history/ledger reads and the save
to the **datalad doer**.

Load `plugins/disseminate/references/neurolibre-structure.md` for the scaffold and how each piece
maps to the harness before generating.

## When to use
- A product (usually a paper) is analyzed and (ideally) released, and the author wants a
  reproducible executable-article form.
- Do NOT use to write prose (`draft-manuscript`) or to release/DOI a version (`dataset-release`);
  this generates the executable build around the results.

## Steps
1. **Identify inputs** — the product `id`, its comparisons' outputs (`derivatives/cmp-<slug>/`), the
   `containers/` recipe (for the environment), and the dataset's published location (the
   `dataset-release` DOI or the DataLad sibling — from the ledger). If the dataset is unreleased,
   note that repo2data should point at the sibling and a DOI be wired at release.
2. **Scaffold the article** (per the reference) at `article/` (or the author's path): `myst.yml`,
   `paper.md`, `content/` figure notebooks, and `binder/` with an environment derived from
   `containers/` plus a `data_requirement.json` (repo2data) resolving the published dataset.
3. **Wire figures to provenance** — each `content/` notebook computes its figure from the
   provenanced `derivatives/…` outputs (not a static image), so the build reproduces them.
4. **Register + log** — add the article path to the product's `outputs[]`; append
   `{ ts, op: executable-article, stage: disseminate, note: "NeuroLibre article for <id>", branch: <branch> }`.
5. **Save** — delegate to the datalad doer: "save: `datalad save -m 'executable-article: scaffold <id>'`."
6. **Report** — the article path, how to build/preview (`myst build` / Jupyter Book), what still
   needs wiring (e.g. the dataset DOI once released), and the next step: `link-outputs` to relate the
   article to the dataset (`Documents`) and paper (`IsSupplementTo`).

## Constraints
- Figures must regenerate from provenanced outputs + the pinned environment — do not embed static
  images as the source of truth; the article's value is re-executability.
- The `binder/` environment derives from the project's container recipe/digest — keep it consistent
  with what analyses actually ran in; do not invent dependencies.
- repo2data points at the *published* dataset (DOI or sibling) — never a local absolute path.
- Record the article under the product's `outputs[]`; keep `log:` append-only and the ledger
  schema-valid. Delegate reads/saves to the datalad doer.
