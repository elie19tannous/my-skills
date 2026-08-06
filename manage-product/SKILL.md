---
name: manage-product
description: >
  Group kept comparisons into a named product — a paper, dataset release, or report — recorded in
  the project ledger's products[] registry. Trigger on "make a product", "group these comparisons",
  "start a paper", "which comparisons go in the paper", "add this comparison to the product",
  "manage products", "define a deliverable". This is where a bag of comparison branches becomes one
  or more publishable products (the pivot toward multiple linked outputs).
plane: workflow
stamped: [M, A]
delegates_to: [datalad]
---

# Skill: manage-product

Turn kept comparisons into **products**. A comparison is a `cmp/<slug>` branch; a *product* is a
named deliverable that groups a chosen subset of them (plus their outputs) into something you will
release and cite. This is the first place the harness represents *multiple* distinct outputs from
one project — the ledger's `products[]` is the registry the later `disseminate/*` skills release and
cross-link. You own the grouping judgment; you delegate the ledger save to the **datalad doer**.

> Ledger note: `products[]` is an **upsert registry** (edited in place), unlike the append-only
> `log:`. Follow `docs/project-ledger.md`: find a product by `id` and update its fields, or add a
> new entry — never drop or rewrite another product, and move `status` only forward. Every write is
> `datalad save`-d so the grouping is provenanced.

## When to use
- The user wants to bundle comparisons into a paper / dataset release / report, add a comparison to
  an existing product, or see/adjust what products exist.
- Do NOT use to create or run a comparison (`analyze/propose-comparison` / `run-comparison`), to
  release a product with a DOI (`disseminate/dataset-release`), or to cross-link products
  (`disseminate/link-outputs`) — this skill only defines the grouping.

## Steps
1. **Identify the product** — get from the user:
   - `id` — a stable kebab-case slug, unique within `products[]` (e.g. `main-paper`)
   - `kind` — `paper` | `dataset` | `report` | `article` | `agent-bundle` | `other`
   - `title` — a human label
   - which comparisons belong to it (`cmp/<slug>` branches). One comparison may appear in more than
     one product (e.g. a shared figure) — that is allowed; call it out so it is intentional.
2. **Verify the comparisons exist and are complete** — delegate to the **datalad doer**:
   > "list branches matching `cmp/*` and the recent log; confirm each of `<the named branches>`
   > exists and has a `run-comparison` entry."
   If a named comparison has no recorded run, warn that the product references incomplete work and
   ask whether to include it anyway or run it first (`analyze/run-comparison`).
3. **Upsert the product** in `project.yaml` `products[]` (per `docs/project-ledger.md`): create the
   entry if `id` is new, else update it. Set `kind`, `title`, `status`
   (`planned` → `in-progress` → `released`), `comparisons` (the branch list), and `outputs` (the
   dataset-relative result paths, e.g. `derivatives/cmp-<slug>/`). Leave `dois: []` and
   `relations: []` — those are owned by `disseminate/dataset-release` and `link-outputs`.
4. **Log it** — append one entry to `project.yaml`:
   `{ ts, op: manage-product, stage: analyze, note: "grouped <branches> into product <id> (<kind>)", branch: <branch> }`.
5. **Save** — delegate to the **datalad doer**:
   > "save: `datalad save -m 'manage-product: <id> groups <branches>'`."
6. **Report** — the product `id`, its comparisons/outputs/status, any incomplete comparisons
   flagged, and the next step (add more comparisons, or `disseminate/dataset-release` to release it,
   then `disseminate/link-outputs` to link it to other products).

## Constraints
- Keep `products[]` ids unique; do not duplicate a comparison within a single product's list.
- Products group and describe comparisons — they never move, rename, or modify the branches or
  their data. This skill edits only the ledger.
- Do not set `dois` or `relations` here; releasing and cross-linking are separate skills.
- The `log:` stays append-only; `products[]` is upserted in place but never destructively (status
  moves forward, entries are not deleted). Keep the ledger schema-valid
  (`schemas/project.schema.json`).
- Delegate every DataLad operation (branch listing, save) to the datalad doer.
