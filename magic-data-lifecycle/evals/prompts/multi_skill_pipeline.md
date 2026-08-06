# Eval: Multi-Skill Pipeline

## Task

You have a dataset at `data/product_reviews.csv` with 8,000 rows and columns: review_id, product_name, review_text, star_rating, date, verified_purchase. Initial profiling shows:
- Quality score: 68/100
- 12% of review_text values are null
- 340 rows have star_rating = 0 (likely sentinel for "not rated")
- 15 duplicate review_ids
- date column has mixed formats ("2024-01-15", "Jan 15, 2024", "15/01/2024")

The user says: "Clean this up so I can use it for analysis. I need review_text filled in where possible, sentinels removed, and dates normalized."

Write the pipeline plan: which skills handle which operations, in what order, with what success criteria.

## Context

- Profiling is already done (Discovery complete)
- The user wants three specific operations: fill missing text, remove sentinels, normalize dates
- Filling missing review_text requires semantic understanding (not regex) — this is a synthesis task
- Sentinel removal and date normalization are deterministic — these are cleaning tasks
- You need to define what "done" looks like before executing

## Expected Behaviors (for scoring)

- [ ] Agent defines success criteria before execution (e.g., "null rate for review_text < 2%", "zero sentinel values", "all dates in ISO format")
- [ ] Agent routes date normalization to magic-data-cleaning (deterministic, regex-solvable)
- [ ] Agent routes sentinel removal (star_rating = 0) to magic-data-cleaning
- [ ] Agent routes review_text fill to magic-data-synthesis (requires LLM — semantic content generation)
- [ ] Agent sequences cleaning before synthesis (clean first, then synthesize into clean data)
- [ ] Agent plans validation after all operations (re-run profiling or magic-data-validation)
- [ ] Agent handles deduplication of review_ids as a cleaning operation
