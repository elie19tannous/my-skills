# Magic Data Profiling

Profile datasets by running quality scoring, distribution analysis, outlier detection, and issue detection before any cleaning or transformation.

## What This Skill Does

- Computes per-column quality scores (completeness, validity, uniqueness) and an aggregate dataset quality score
- Runs distribution analysis, normality tests, and correlation matrices with method selection based on data shape
- Detects outliers, categorical groupings, and classifies answer types across columns

## Files

- `SKILL.md` — Agent knowledge document and frontmatter
- `scripts/` — `quality_score.py`, `distribution_analysis.py`, `correlation_matrix.py`, `outlier_detection.py`, `detect_all_issues.py`, `deep_quality_analysis.py`, `detect_categories.py`, `classify_answers.py`
- `references/` — profiling guide

## Related Skills

- `magic-data-loading` — load data before profiling
- `magic-data-cleaning` — profiling reveals issues that cleaning then fixes
- `magic-statistical-analysis` — for hypothesis testing beyond descriptive profiling
