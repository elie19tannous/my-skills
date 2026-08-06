# Linguistic Shared Utilities

Shared Python utilities used across multiple linguistic skills. **Not a skill** — has no SKILL.md.

## Contents

- `data/` — reference data
- `findings_presenter.py`
- `interaction_utils.py`
- `lang_codes.py`

## Source of truth — do not hand-edit the bundles

This directory is the **single source of truth**. Each `magic-linguistic-*` skill
that imports these utilities ships its own committed copy at
`skills/<skill>/_linguistic_shared/`, so the skill is self-contained on disk and
survives an isolated install (our CLI and `npx skills add`/skills.sh recursively
copy only the named skill dir — never this sibling).

Those per-skill copies are **generated** by `scripts/sync-linguistic-shared.py`
and committed. **Never hand-edit a per-skill `_linguistic_shared/`.** After
changing anything here, re-run the sync and commit the regenerated bundles:

```bash
python scripts/sync-linguistic-shared.py
```

CI job `check-shared-in-sync` fails if any committed bundle drifts from this source.
