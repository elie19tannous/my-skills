# Eval: Basic Quality Score

## Task

You have a CSV file at `data/customer_records.csv` with 5,000 rows and these columns:
- `id` (integer, unique identifier)
- `name` (string, customer name)
- `email` (string, email address)
- `age` (integer, some missing values)
- `signup_date` (string, date format varies: "2024-01-15", "Jan 15, 2024", "15/01/2024")
- `status` (string, values: "active", "inactive", "Active", "ACTIVE")

The dataset has ~8% missing values concentrated in `age` and `email`, mixed date formats in `signup_date`, and inconsistent casing in `status`.

Profile this dataset and report the quality score.

## Expected Behaviors (for scoring)

- [ ] Agent detects column types before profiling (numeric vs text vs categorical)
- [ ] Agent computes a composite quality score (0-100) across completeness, consistency, uniqueness, validity
- [ ] Agent reports per-column breakdown alongside the aggregate score (not just the overall number)
- [ ] Agent identifies the inconsistent casing in `status` as a consistency issue
- [ ] Agent identifies the mixed date formats in `signup_date` as a consistency issue
- [ ] Agent reports the score with context: row count (5,000), column count (6), and what the score means for the use case
- [ ] Agent does NOT use LLM for computing statistics — uses code/scripts
