# Eval: Complex Cleaning Plan

## Task

You have a JSONL file at `data/survey_responses.jsonl` with 8,000 records and fields: respondent_id, age, income, education_level, satisfaction_score, open_feedback, survey_date, region. The file has multiple overlapping quality issues:

- `age`: 2% missing, plus 34 rows with value "N/A" (string in a numeric field)
- `income`: 22% missing, plus 12 outliers (negative values that are clearly errors)
- `education_level`: inconsistent casing and whitespace ("Bachelor's ", " bachelor's", "BACHELORS")
- `satisfaction_score`: 5% missing (numeric, 1-10 scale)
- `open_feedback`: 15% contain sentinel value "No response" which should be treated as missing; 3% contain the placeholder "TBD"
- `survey_date`: 8 rows have dates in MM/DD/YYYY format while the rest are YYYY-MM-DD
- Approximately 200 exact duplicate rows

Produce a cleaning plan, execute it in stages with checkpoints, validate after each stage, and route synthesis tasks appropriately.

## Context

- This data feeds into a satisfaction analysis dashboard
- The `open_feedback` sentinels ("No response", "TBD") need LLM-based contextual fill, not statistical imputation
- The duplicate rows likely come from a double-submission bug and should be removed
- Order of operations matters: normalize strings before deduplication (otherwise "Bachelor's " and "bachelor's" look like different records)

## Expected Behaviors (for scoring)

- [ ] Agent runs full issue detection first
- [ ] Agent produces a multi-step cleaning plan BEFORE executing (not ad-hoc fixes)
- [ ] Agent cleans deterministic issues first (type coercion, whitespace, encoding, date format) before imputation
- [ ] Agent normalizes `education_level` strings before deduplication
- [ ] Agent converts "N/A" strings in `age` to NaN before numeric imputation
- [ ] Agent handles `income` outliers (negative values) — flags or removes, does not impute over them blindly
- [ ] Agent recognizes `open_feedback` sentinels as a SYNTHESIS task and routes to `magic-data-synthesis` (does NOT impute with mode or empty string)
- [ ] Agent checkpoints between cleaning stages (at least 2 intermediate saves)
- [ ] Agent validates after each major stage, not just at the end
- [ ] Agent deduplicates AFTER string normalization (correct ordering)
