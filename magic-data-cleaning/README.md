# Magic Data Cleaning

Clean data by detecting issues, handling missing values, normalizing strings, and executing structured cleaning plans with before/after validation.

## What This Skill Does

- Handles missing values with strategy selection by column type and missing rate (mean/median, KNN, mode, drop)
- Normalizes text columns: whitespace stripping, encoding fixes, casing standardization, deduplication
- Generates a cleaning plan JSON for complex multi-step operations and validates results after each step

## Files

- `SKILL.md` — Agent knowledge document and frontmatter
- `scripts/` — `detect_issues.py`, `handle_missing.py`, `normalize_strings.py`, `execute_cleaning_plan.py`, `validate_clean.py`

## Related Skills

- `magic-data-profiling` — profiling surfaces the issues that cleaning addresses
- `magic-data-synthesis` — LLM-based filling of sentinel/placeholder values (not cleaning)
- `magic-data-validation` — re-validate after cleaning to catch regressions
