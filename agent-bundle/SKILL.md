---
name: agent-bundle
description: >
  Synthesize a Paper2Agent-style MCP server from the project's scripts + data dictionary, emitted in
  the harness's own SKILL.md + plugin.json + MCP config, with result-reproduction tests. Trigger on
  "agent bundle", "Paper2Agent", "make an MCP server", "expose the methods as tools", "agent-callable
  paper", "tool bundle". Produces an agent-bundle-kind living product that dogfoods the harness format.
plane: workflow
stamped: [A, E]
delegates_to: [datalad]
---

# Skill: agent-bundle

Turn the project's analysis code into an **agent-callable bundle**: the paper's methods become
parameterized, tested MCP tools an agent or person can invoke to reproduce or extend results
(Actionable), each backed by a reproduction test (Ephemerality — verifiably re-runnable). The bundle
is emitted in the harness's **own** `SKILL.md` + `plugin.json` + MCP format, so the project dogfoods
the structure it is built from. You delegate ledger/history reads and the save to the **datalad
doer**.

Load `plugins/disseminate/references/paper2agent-bundle.md` for the bundle layout and mapping before
generating.

## When to use
- A product's analyses are provenanced (`run-comparison` outputs exist) and the author wants them
  exposed as reusable, tested tools / an MCP server.
- Do NOT use to write the paper (`draft-manuscript`) or to build the reproducible article
  (`executable-article`) — this exposes the *methods as callable tools*.

## Steps
1. **Extract candidate tools** — from `code/` scripts and the `participants.json` data dictionary:
   each analysis becomes a parameterized tool (inputs = the script's real inputs, typed from the
   dictionary; outputs = the provenanced `derivatives/…`). List them and confirm scope with the user.
2. **Scaffold the bundle** (per the reference) at `agent-bundle/`: `.claude-plugin/plugin.json`,
   one `skills/<tool>/SKILL.md` per tool, `mcp/server.py` exposing the tools over MCP, `.mcp.json`
   registration, and `tests/reproduce.py`.
3. **Write reproduction tests** — each test asserts the tool reproduces the recorded result for its
   comparison (`derivatives/cmp-<slug>/`), so the bundle is verifiably re-executable.
4. **Register + log** — add the bundle path to the product's `outputs[]` (or create an
   `agent-bundle`-kind product); append
   `{ ts, op: agent-bundle, stage: disseminate, note: "Paper2Agent bundle for <id>", branch: <branch> }`.
5. **Save** — delegate to the datalad doer: "save: `datalad save -m 'agent-bundle: synthesize <id>'`."
6. **Report** — the bundle path, the tools exposed, how to run the MCP server + reproduction tests,
   and the next step: `link-outputs` to relate the bundle to the code (`IsDerivedFrom`) and paper
   (`IsSupplementTo`).

## Constraints
- Tools wrap *existing* provenanced analyses — do not invent new methods or change the science; a
  tool's output must match the recorded result (that is what the reproduction test asserts).
- Emit the harness's own `SKILL.md` + `plugin.json` + `.mcp.json` format (dogfooding) — do not
  invent a bespoke bundle format.
- Every tool ships a reproduction test; a bundle whose tools are not verifiably reproducible is not
  releasable.
- Record the bundle under the product's `outputs[]`; keep `log:` append-only and the ledger
  schema-valid. Delegate reads/saves to the datalad doer.
