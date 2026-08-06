---
name: run-comparison
description: >
  Execute a proposed comparison's analysis script with full DataLad provenance, on its branch,
  inside the project container. Trigger on "run the comparison", "run this analysis with
  provenance", "execute the comparison", "container-run this script", or after the user has
  written the analysis script for a branch created by propose-comparison.
plane: workflow
stamped: [A, T, P, E]
delegates_to: [containers, datalad]
---

# Skill: run-comparison

Run the user's analysis script as a provenanced, containerized computation so inputs, command,
container image, and outputs are all recorded (Actionability + Tracking) in a disposable,
rebuilt-from-spec environment (Portability + Ephemerality). You never run the tool yourself —
you delegate to the **datalad doer**.

## When to use
- A comparison branch exists (`analyze/propose-comparison`) and the analysis script is written.
- Do NOT use for one-off exploratory commands that produce no output files — those need no run
  record. Do NOT use to create the branch (that is `propose-comparison`).

## Steps
1. **Confirm context** — verify you are on the comparison's branch (`cmp/<slug>`) and the script
   exists in `code/`. If not, ask the user which branch/script, or route to `propose-comparison`.
2. **Gather run parameters**:
   - `command` — how to invoke the script (e.g. `python code/stats.py`)
   - `-i` inputs — the data files/globs the script reads (e.g. `participants.tsv`, `sub-*/…`)
   - `-o` outputs — where results land (prefer `derivatives/cmp-<slug>/…`)
   - `-m` message — a meaningful description of the run
   - container — the project container recipe from `containers/` (build/register on first use)
3. **Ensure the container image exists (containers doer)** — if no `.sif` has been built yet for the
   project recipe, delegate to the **containers doer**:
   > "build a `.sif` from `containers/<recipe>` into `containers/<name>.sif`."
   It returns the image path and the `datalad containers-add …` command to register it. Skip if the
   image is already built and registered.
4. **Delegate execution to the datalad doer**:
   > "container-run `<command>` on branch `cmp/<slug>` using container `<name>` (register it with the
   > `containers-add` command from step 3 if not yet registered), inputs `<-i …>`, outputs `<-o …>`,
   > message `<-m …>`."
   Wait for its structured result (commit sha, recorded outputs, pass/fail).
5. **Handle the result**:
   - **ok** — note the commit and output paths.
   - **failed** — relay the doer's error + suggested fix; nothing was committed. Stop.
6. **Log it** — append to `project.yaml`:
   `{ ts, op: run-comparison, stage: analyze, note: "container-run <command>; commit <sha>;
   outputs <paths>", branch: cmp/<slug> }`.
7. **Report** — commit, outputs, and that the run is replayable via the doer (`datalad rerun`).

## Constraints
- Always run through the datalad doer's `container-run` path so the environment is captured — do
  not fall back to a bare `datalad run` or a raw shell command for an analysis with outputs.
- Require a meaningful `-m` message; never a placeholder.
- Do not write or "fix" the analysis script's science — if it errors on its own logic, surface it
  to the user; the harness owns provenance, not the model.
- Keep `project.yaml` append-only; log both successful and (as a note) failed runs if useful.
