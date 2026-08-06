---
name: publish
description: >
  Publish the dataset so it is independently retrievable by others — push committed state
  (git history + annexed content) to a sibling, and verify a fresh clone can `datalad get`
  the results. Trigger on "publish", "publish the dataset", "share the dataset", "push to a
  remote/sibling", "release the data", "make this distributable", "set up a remote and push".
  This is the Stage-6+ (Disseminate) entry point for baseline Distributability.
plane: workflow
stamped: [D]
delegates_to: [datalad]
---

# Skill: publish

Make the dataset **Distributable (STAMPED-D)**: transfer already-committed state to a sibling so
anyone with access can clone it and retrieve the exact annexed outputs. You never run DataLad
yourself — you delegate every sibling/push/verify operation to the **datalad doer**.

> STAMPED note: a datalad-managed dataset served over any git-annex sibling *already* satisfies
> baseline Distributability — a plain SSH/local sibling is enough. Richer archival targets
> (GitHub + a storage sibling via `--publish-depends`, OSF, a RIA store) are add-ons layered on
> the same push, not prerequisites. Pick the lightest target that meets the sharing need.

## When to use
- The user wants to share, back up, release, or hand off the dataset, or make it reproducible for
  a collaborator/reviewer.
- Do NOT use to record local work — that is `analyze/checkpoint` (a checkpoint should happen
  *before* publishing; publish only ever transfers committed state).
- Do NOT use to run or promote an analysis — that is the `analyze/*` skills.

## Steps
1. **Ensure a clean, committed tree** — delegate to the datalad doer:
   > "status: report modified/untracked files and the current branch."
   Push transfers only committed state. If the tree is dirty, tell the user and route to
   `analyze/checkpoint` first (or have them confirm publishing the current committed state).
2. **Choose the target sibling** — delegate to the doer:
   > "siblings: list configured siblings for this dataset."
   - **A suitable sibling already exists** → use it.
   - **None exists** → ask the user where to publish, then delegate creation to the doer. Keep it
     to the lightest option that fits (baseline D needs only one of these):
     - local path / SSH host — `create-sibling` (simplest, satisfies D)
     - GitHub/GitLab/GIN + a **storage sibling** wired with `--publish-depends` (so annexed
       content reaches storage before git history reaches the host)
     - OSF (`create-sibling-osf`, needs the `datalad-osf` extension) or a RIA store — richer
       archival add-ons.
   If a git host is paired with separate annex storage, the storage sibling MUST be set as a
   `--publish-depends` — otherwise the push sends git history without the file content and
   consumers cannot retrieve outputs.
3. **Guard against publishing secrets** — before pushing, confirm no credentials, tokens, or
   restricted/identifiable data are staged for transfer. De-identification is a separate concern
   (deferred), but never publish `.git-annex`-tracked PII or a `credentials`/`.env` file. If in
   doubt, ask the user.
4. **Push** — delegate to the doer:
   > "push: `datalad push --to <sibling>` including annexed content (`--data anything`, or
   > `auto-if-wanted` if the sibling has `annex-wanted` configured); push all comparison branches,
   > not just the current one."
   Wait for the doer's structured result (git refs pushed, annexed objects transferred).
5. **Verify Distributability** — delegate a fresh-clone check to the doer (the same proof the e2e
   smoke test asserts — see `tests/e2e-smoke.sh`, "distributability"):
   > "clone `<sibling>` to a scratch dir and `datalad get` one published output; confirm the
   > content is retrievable, then discard the clone."
   If retrieval fails, the annexed content did not reach storage — most often a missing
   `--publish-depends`; relay the doer's error and stop.
6. **Log it** — append to `project.yaml`:
   `{ ts, op: publish, stage: disseminate, note: "pushed <branches> to <sibling>; verified clone+get", branch: <branch> }`.
7. **Report** — the sibling, what was transferred (git + annex), that an independent clone can
   retrieve the outputs, and any richer target the user might add next (OSF/Zenodo DOI, RIA).

## Constraints
- Delegate every sibling/push/clone/get operation to the datalad doer — never call `datalad`
  (and never `git push`) directly; a raw `git push` bypasses annex content and publish-depends
  ordering.
- Publish only committed state — a dirty tree means checkpoint first; never `--force` a push over
  a sibling's history to "make it fit".
- Never skip the `--publish-depends` wiring when a git host and a separate storage sibling are
  both in play — this is the single most common cause of "cloned but can't `get` the data".
- Do not publish credentials or restricted/identifiable content; surface the risk instead.
- Keep `project.yaml` append-only.
