---
name: liab-deploy
description: >
  Scaffold a Lab-in-a-Box deployment — a pyinfra config that stands up self-hosted Forgejo +
  git-annex data serving and publishes the DataLad dataset over git-annex remotes as a data-sovereign
  distribution channel. Trigger on "lab in a box", "self-host the data", "data sovereign", "Forgejo",
  "pyinfra deploy", "self-hosted git-annex", "own our infrastructure". Produces a deployment product
  alongside the cloud-hosted outputs.
plane: workflow
stamped: [D]
delegates_to: [datalad]
---

# Skill: liab-deploy

Give the project a **data-sovereign** distribution channel: self-hosted infrastructure that serves
the DataLad dataset over git-annex remotes, so the lab controls where its data lives while keeping
the same Distributability a cloud sibling provides. The infra is declarative (pyinfra), so the
deployment itself is reproducible. You delegate sibling registration and the save to the **datalad
doer**.

Load `plugins/disseminate/references/liab-deployments.md` for the deployment layout and mapping
before generating.

## When to use
- The project wants to self-host its dataset (data sovereignty, institutional policy), alongside or
  instead of a cloud archive.
- Do NOT use to push to an existing sibling (`disseminate/publish`) or to mint a DOI
  (`dataset-release`) — this scaffolds the *destination infrastructure*.

## Steps
1. **Gather targets** — the host(s) that will run the deployment and whether Forgejo (git host) +
   git-annex serving are both wanted. Confirm the operator has access to the target hosts.
2. **Scaffold the deployment** (per the reference) at `liab/`: `inventory.py` (hosts), `deploy.py`
   (pyinfra operations for Forgejo + git-annex special remote), and `config/`. Do not run the
   deployment for the user — scaffold it and show the `pyinfra inventory.py deploy.py` command.
3. **Register the sibling (datalad doer)** — once the store is up, delegate:
   > "siblings: register the self-hosted Forgejo/git-annex store as a sibling (`create-sibling` /
   > the annex special remote), with a storage `--publish-depends` so annexed content is served."
   Then the user pushes with `disseminate/publish`.
4. **Register + log** — record the deployment path (and, once live, the sibling name) under a product
   (kind `other`) `outputs[]`; append
   `{ ts, op: liab-deploy, stage: disseminate, note: "Lab-in-a-Box deploy scaffold; sibling <name>", branch: <branch> }`.
5. **Save** — delegate to the datalad doer: "save: `datalad save -m 'liab-deploy: scaffold self-hosted serving'`."
6. **Report** — the deployment path, how to run it, the registered sibling (once live), and the next
   step: `disseminate/publish` to push to the self-hosted store, then `link-outputs` to relate the
   mirror to the dataset (`IsVariantFormOf`).

## Constraints
- Scaffold, do not deploy: never run `pyinfra` or provision remote hosts on the user's behalf —
  present the command and let the operator run it against their own infrastructure.
- The self-hosted store is a *destination* — it reuses the standard sibling/publish/provenance flow
  (register via the datalad doer, push via `publish`), it does not bypass it.
- Ensure annexed content is actually served (a storage `--publish-depends`) so a clone can
  `datalad get` from the self-hosted store — otherwise it distributes history without data.
- Record under a product's `outputs[]`; keep `log:` append-only and the ledger schema-valid.
  Delegate sibling/save operations to the datalad doer.
