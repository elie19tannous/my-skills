# Magic Data Validation

Validate datasets against schemas, check cross-column constraints, detect sentinel values, and catch statistical pitfalls before delivery.

## What This Skill Does

- Infers or applies custom schemas and validates column types, ranges, and null constraints
- Checks cross-column business rules and catches statistical traps (Simpson's paradox, join explosion)
- Detects remaining sentinel/placeholder values that synthesis should have filled

## Files

- `SKILL.md` — Agent knowledge document and frontmatter
- `scripts/` — `infer_schema.py`, `validate_schema.py`, `check_constraints.py`, `content_validator.py`, `sanity_check.py`, `validate_statistics.py`

## Related Skills

- `magic-data-cleaning` — cleaning feeds into validation; re-validate after every cleaning step
- `magic-data-transformation` — validate after reshaping and merging
- `magic-data-lifecycle` — validation is the final gate before delivery
