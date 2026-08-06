---
name: link-outputs
description: >
  Cross-link a project's products into one navigable compendium using DataCite RelatedIdentifier
  relations. Trigger on "link the outputs", "cross-link products", "connect the dataset to the
  paper", "relate these products", "link the agent bundle to the code", "build the compendium",
  "record how these products relate". This is the step that turns several released products into a
  single linked research object — the endgame of publishing multiple products.
plane: workflow
stamped: [M, D]
delegates_to: [datalad]
---

# Skill: link-outputs

Record how the project's **products relate to each other** (and to external identifiers), so the
dataset, paper, executable article, and agent bundle form **one linked compendium** rather than
scattered artifacts. The links are DataCite `RelatedIdentifier` relations, stored in each product's
`relations[]` in the ledger (Metadata) and making the multi-product set resolvable as a coherent
whole (Distributability). You own which links are meaningful; you delegate the ledger save to the
**datalad doer**.

Load `plugins/disseminate/references/datacite-relations.md` for the valid `relationType` terms and
their inverses before recording any relation.

## When to use
- Two or more products exist in `products[]` (via `analyze/manage-product`), typically after some
  are released (`disseminate/dataset-release`), and you want to record how they relate.
- Do NOT use to create products (`manage-product`) or to mint DOIs / cut versions
  (`dataset-release`). This skill only records relations between things that already exist.

## Steps
1. **Identify the relations** — for each link, determine the **source** product `id`, the
   `relationType` (from the reference — e.g. `IsSupplementedBy`, `IsSourceOf`, `IsDocumentedBy`),
   and the **target**: another product `id` in this ledger (internal) or an external resolvable
   DOI/URL. Ask the user for anything ambiguous; do not guess how products relate.
2. **Validate both ends** — the source must be a product in `products[]`. For an internal target,
   confirm the target `id` exists. Warn (do not block) if an internal target is not yet released
   (no DOI) — the `id` link still resolves once it is released; suggest `dataset-release` if the
   user wants a DOI now. Never fabricate a DOI for an unreleased target.
3. **Record the relation (and its inverse)** — upsert into the source product's `relations[]`:
   `{ relation: <relationType>, target: <id-or-DOI> }` (per `docs/project-ledger.md`; do not
   duplicate an identical relation). For an **internal** target, also record the **inverse**
   relation on the target product (see the reference table) so the graph is consistent both ways.
   For an **external** target, record only the forward relation.
4. **(Optional) mirror external links** into `dataset_description.json` for the dataset product
   (e.g. a DOI the dataset `References`), keeping the ledger as the canonical record.
5. **Log it** — append `{ ts, op: link-outputs, stage: disseminate, note: "<src> <relation> <target> (+inverse)", branch: <branch> }`.
6. **Save** — delegate to the **datalad doer**: "save: `datalad save -m 'link-outputs: <src> <relation> <target>'`."
7. **Report** — the relation graph (source → relation → target for each link), any targets still
   needing a DOI, and whether the compendium is now fully linked. When every product is released
   and linked, the multi-product research object is complete.

## Constraints
- Use only valid DataCite `relationType` terms (see the reference); record the inverse for internal
  product-to-product links.
- Never fabricate a DOI — link by product `id` (internal) or a real resolvable identifier only.
- `relations[]` is upserted per the ledger conventions (no duplicate `{relation,target}` pairs);
  keep `log:` append-only and the ledger schema-valid (`schemas/project.schema.json`).
- Relations describe existing products — this skill never creates, versions, or moves a product.
- Delegate every DataLad save to the datalad doer.
