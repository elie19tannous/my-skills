---
name: people
description: >
  Record who contributed and how, using CRediT roles and persistent identifiers (ORCID, ROR), in the
  ledger's contributors[] — and reflect them into dataset_description.json Authors. Trigger on "add a
  contributor", "credit", "CRediT roles", "authors", "who worked on this", "add ORCID", "record
  contributions", "author list". Keeps authorship a provenanced, standard-coded record.
plane: workflow
stamped: [M]
delegates_to: [datalad]
---

# Skill: people

Maintain the project's people as structured **Metadata**: each contributor with their CRediT roles
and persistent identifiers, so credit is explicit, standard-coded, and machine-readable — and so it
flows into the dataset's `Authors` and, at release, DataCite creators. The canonical record is the
ledger `contributors[]`; you delegate the save to the **datalad doer**.

CRediT roles (use these exact terms): Conceptualization, Data curation, Formal analysis, Funding
acquisition, Investigation, Methodology, Project administration, Resources, Software, Supervision,
Validation, Visualization, Writing – original draft, Writing – review & editing.

## When to use
- The user wants to add/update a contributor, assign CRediT roles, or record ORCIDs/affiliations.
- Do NOT use to write a report (`project/status-report`) or to mint DOIs (`disseminate/dataset-release`).

## Steps
1. **Capture the contributor** — `name`, `orcid` (as an ORCID URL, if known), `affiliation_ror`
   (ROR URL, if known), and their `roles` from the CRediT list above. Ask; do not guess an ORCID or
   invent roles.
2. **Upsert into `contributors[]`** (per `docs/project-ledger.md`) — match by `name` (or ORCID) and
   update, or add a new entry. Keep roles to valid CRediT terms; do not duplicate a person.
3. **Reflect into `dataset_description.json`** — update the `Authors` list to match (order is the
   author order the team agrees on). Keep it consistent with the ledger.
4. **Log it** — append `{ ts, op: people, stage: manage, note: "credited <name> (<roles>)", branch: <branch> }`.
5. **Save** — delegate to the datalad doer: "save: `datalad save -m 'people: credit <name>'`."
6. **Report** — the updated contributor list with roles, and any missing ORCIDs/affiliations to fill.

## Constraints
- Use only valid CRediT role terms (listed above); never invent a role or an ORCID/ROR — record only
  identifiers the user provides.
- Keep `contributors[]` de-duplicated (one entry per person) and consistent with
  `dataset_description.json` Authors.
- Upsert per the ledger conventions; keep `log:` append-only and the ledger schema-valid. Delegate
  the save to the datalad doer.
