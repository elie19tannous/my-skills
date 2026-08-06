---
name: draft-manuscript
description: >
  Scaffold an IMRaD manuscript for a product and auto-fill the Methods, Data-availability, and
  provenance sections from the DataLad history and the project ledger. Trigger on "draft the
  manuscript", "start the paper", "write up the results", "IMRaD scaffold", "methods section",
  "data availability statement". Produces the paper product's write-up; the science/argument stays
  the author's.
plane: workflow
stamped: [M]
delegates_to: [datalad]
---

# Skill: draft-manuscript

Turn a grouped **paper** product into a manuscript skeleton whose *mechanical* sections are filled
from provenance — Methods from the recorded `datalad run`/`container-run` commands, a
Data-availability statement from the ledger's products/DOIs, and a provenance appendix from
`datalad log`. The scientific narrative (Intro, interpretation, Discussion) is the author's; the
harness fills only what it can derive faithfully. You delegate history/ledger reads and the save to
the **datalad doer**.

## When to use
- A paper product exists in `products[]` (via `analyze/manage-product`) and the author wants a
  manuscript scaffold to write into.
- Do NOT invent results or claims — this scaffolds structure and fills provenance-derived text only.

## Steps
1. **Identify the product** — the `paper`-kind product `id` and the comparisons it groups.
2. **Gather provenance (datalad doer)** — delegate:
   > "log: list the `datalad run`/`container-run` commits for branches `<the product's comparisons>`
   > with their commands, inputs, and outputs."
   Use this to write a faithful **Methods** paragraph (what was run, in which container, on which
   inputs) and a **provenance appendix**.
3. **Scaffold IMRaD** — write `manuscript/` (or the author's chosen path): `index.md` with
   Introduction / Methods / Results / Discussion headings. Pre-fill:
   - **Methods** — from step 2 (commands, container/version, parameters). Mark anything uncertain
     `[TODO: confirm]` rather than guessing.
   - **Results** — a stub per comparison pointing at its `derivatives/cmp-<slug>/` outputs/figures.
   - **Data & code availability** — from the ledger: the dataset/product DOIs (or "pending release"
     if unreleased), the DataLad dataset, and the container recipe.
   - Leave Introduction/Discussion as author prompts.
4. **Register + log** — record the manuscript path under the product's `outputs[]`; append
   `{ ts, op: draft-manuscript, stage: disseminate, note: "IMRaD scaffold for <id>", branch: <branch> }`.
5. **Save** — delegate to the datalad doer: "save: `datalad save -m 'draft-manuscript: scaffold <id>'`."
6. **Report** — the manuscript path, which sections were auto-filled vs. left to the author, and the
   next steps (`disseminate/reporting-checklist`, then `dataset-release`/`link-outputs`).

## Constraints
- Fill only provenance-derivable text (Methods, availability, provenance). Never fabricate results,
  statistics, citations, or claims; mark gaps `[TODO]`.
- Read history/ledger and save through the datalad doer; keep `log:` append-only and the ledger
  schema-valid. Record the manuscript under the product's `outputs[]` (upsert per the conventions).
- The manuscript is a product artifact — it does not modify the comparisons or their data.
