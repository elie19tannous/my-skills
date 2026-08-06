# Eval: Basic Pipeline Routing

## Task

A user gives you a CSV file at `data/customer_feedback.csv` containing 1,200 rows of customer survey responses with columns: respondent_id, date, rating (1-5), category, comment, resolved (yes/no). The user says: "Help me check this data and see what's going on."

Write a plan describing exactly which MAGIC skills you would invoke, in what order, and why.

## Context

- The file is small (1,200 rows, ~400KB)
- The user's request is open-ended ("check this data") — scope is unclear
- You have not loaded or examined the data yet
- All MAGIC skills are available

## Expected Behaviors (for scoring)

- [ ] Agent identifies this as a Discover phase task — the user wants to understand the data
- [ ] Agent routes file loading to magic-data-loading (not raw pd.read_csv)
- [ ] Agent plans to run profiling (magic-data-profiling) immediately after loading
- [ ] Agent follows Discover before Plan sequence — does not jump to cleaning without profiling first
- [ ] Agent mentions quality score as the baseline for further decisions
- [ ] Agent does not over-engineer — no data spec or compliance report for an initial check
