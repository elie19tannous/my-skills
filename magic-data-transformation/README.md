# Magic Data Transformation

Reshape, aggregate, merge, and derive columns — then deliver the result to a database or HuggingFace Hub.

## What This Skill Does

- Pivots, melts, and reshapes tables; groups and aggregates with custom functions
- Joins and merges multiple datasets with join-explosion detection
- Delivers processed data to SQLite/PostgreSQL/MySQL or pushes directly to HuggingFace Hub

## Files

- `SKILL.md` — Agent knowledge document and frontmatter
- `scripts/` — `reshape.py`, `aggregate.py`, `merge_datasets.py`, `derive_columns.py`, `validate_transform.py`, `deliver_to_db.py`, `deliver_to_hf.py`

## Related Skills

- `magic-data-cleaning` — clean before transforming to avoid propagating errors
- `magic-data-validation` — validate after transformations before delivery
- `magic-data-lifecycle` — transformation is a mid-pipeline phase between cleaning and validation
